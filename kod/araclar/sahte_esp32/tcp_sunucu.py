"""Sahte ESP32'yi gerçek zamanda koşturan ve yerel bir TCP portunda "sanal seri hat" olarak sunan katman.

Windows'ta sürücü kurmadan çalışır: Pi istemcisi `TcpTasima(port=...)` ile bağlanır, satır sonlu JSON konuşur.
Seri hat noktadan noktaya olduğu için aynı anda tek istemci: yeni bağlantı eskisini kapatır. İstemci yokken kartın
yazdıkları kaybolur (karşıda dinleyen yok); bağlantı açılınca kart resetlenmez (DTR/RTS kapalı açılış, E3).

Çekirdek saf kalır: zamanı bu katman verir (10 ms dilim, gecikirse yakalar). Çekirdeğe dokunan her şey
`kilit` altında (fiziksel ortam işlemleri ve görünüm de bu kilidi alır).
"""

import socket
import threading
import time

from .cekirdek import DILIM_MS


class TcpSunucu:
    def __init__(self, cekirdek, host="127.0.0.1", port=5760):
        self.cekirdek = cekirdek
        self.kilit = threading.RLock()
        self._dinleyici = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._dinleyici.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._dinleyici.bind((host, port))
        self._dinleyici.listen(1)
        self._dinleyici.setblocking(False)
        self.host, self.port = self._dinleyici.getsockname()
        self._istemci = None
        self._dur = threading.Event()
        self._is = None
        self.gecikme_sayisi = 0          # gerçek zamana yetişemeyen dilim sayısı (bilgi)

    def baslat(self):
        self._is = threading.Thread(target=self._dongu, name="sahte-esp32", daemon=True)
        self._is.start()
        return self

    def durdur(self):
        self._dur.set()
        if self._is is not None:
            self._is.join(timeout=2)
        for s in (self._istemci, self._dinleyici):
            if s is not None:
                try:
                    s.close()
                except OSError:
                    pass
        self._istemci = None

    def istemci_kopar(self):
        """Sunucu tarafından bağlantıyı kes (kablo çekildi)."""
        with self.kilit:
            if self._istemci is not None:
                try:
                    self._istemci.close()
                except OSError:
                    pass
                self._istemci = None

    def _kabul(self):
        try:
            s, _ = self._dinleyici.accept()
        except (BlockingIOError, InterruptedError, OSError):
            return
        s.setblocking(False)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        with self.kilit:
            if self._istemci is not None:
                try:
                    self._istemci.close()
                except OSError:
                    pass
            self._istemci = s

    def _oku(self):
        s = self._istemci
        if s is None:
            return
        while True:
            try:
                veri = s.recv(4096)
            except (BlockingIOError, InterruptedError):
                return
            except OSError:
                veri = b""
            if not veri:
                with self.kilit:
                    if self._istemci is s:
                        self._istemci = None
                try:
                    s.close()
                except OSError:
                    pass
                return
            with self.kilit:
                self.cekirdek.bayt_al(veri)

    def _yaz(self, satirlar):
        s = self._istemci
        if s is None or not satirlar:
            return
        veri = ("\n".join(satirlar) + "\n").encode("utf-8")
        try:
            s.setblocking(True)
            s.settimeout(0.5)
            s.sendall(veri)
            s.setblocking(False)
        except OSError:
            with self.kilit:
                if self._istemci is s:
                    self._istemci = None

    def _dongu(self):
        dilim = DILIM_MS / 1000.0
        sonraki = time.monotonic()
        while not self._dur.is_set():
            self._kabul()
            self._oku()
            simdi = time.monotonic()
            if simdi >= sonraki:
                n = 0
                while simdi >= sonraki and n < 20:
                    with self.kilit:
                        self.cekirdek.adim(DILIM_MS)
                        cikan = self.cekirdek.cikis_al()
                    self._yaz(cikan)
                    sonraki += dilim
                    n += 1
                if simdi >= sonraki:          # 200 ms'den fazla geride: yakalamayı bırak
                    self.gecikme_sayisi += 1
                    sonraki = simdi + dilim
            time.sleep(0.001)
