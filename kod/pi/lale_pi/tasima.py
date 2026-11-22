"""Pi tarafı taşıma katmanı: istemci, karşısında gerçek kart mı sahtesi mi olduğunu bilmez.

Bir taşıma dört şey yapar: `ac()`, `kapat()`, `yaz(bayt)`, `oku()` (o ana dek gelen tam satırlar, bekletmez) ve
`bekle(ms)` (zamanı ilerletir: gerçek hatta uyur, bellek içi sahte kartta sanal saati ilerletir). Testlerin
zaman tabanı budur; böylece aynı senaryo sanal saatle saniyeler içinde, gerçek kartla gerçek zamanda koşar.

Uygulamalar: `TcpTasima` (sahte ESP32'nin TCP "sanal seri hattı"), `SeriTasima` (gerçek kart; YAZILMADI, yer tutucu).
Bellek içi taşıma sahte karta bağlı olduğu için `kod/araclar/sahte_esp32/tasima.py` içinde.
"""

import socket
import time


class Tasima:
    """Arayüz. Satırlar metin olarak döner (UTF-8 çözülmüş, satır sonu atılmış)."""

    def ac(self):
        raise NotImplementedError

    def kapat(self):
        raise NotImplementedError

    def yaz(self, bayt):
        raise NotImplementedError

    def oku(self):
        raise NotImplementedError

    def bekle(self, ms):
        raise NotImplementedError

    def acik_mi(self):
        raise NotImplementedError


class SatirTamponu:
    """Gelen baytları satırlara böler; `\\r` atılır; UTF-8 olmayan satır '\\ufffd'li metin olur."""

    def __init__(self):
        self._b = bytearray()

    def ekle(self, veri):
        self._b += veri
        satirlar = []
        while True:
            i = self._b.find(b"\n")
            if i < 0:
                return satirlar
            ham = bytes(self._b[:i]).replace(b"\r", b"")
            del self._b[:i + 1]
            satirlar.append(ham.decode("utf-8", errors="replace"))


class TcpTasima(Tasima):
    """Sahte ESP32'nin yerel TCP portu (sürücüsüz sanal seri hat). Gerçek zaman."""

    def __init__(self, host="127.0.0.1", port=5760, baglanti_suresi_s=3.0):
        self.host, self.port = host, port
        self.baglanti_suresi_s = baglanti_suresi_s
        self._s = None
        self._tampon = SatirTamponu()
        self._satirlar = []

    def ac(self):
        self._s = socket.create_connection((self.host, self.port), timeout=self.baglanti_suresi_s)
        self._s.setblocking(False)
        self._tampon = SatirTamponu()

    def kapat(self):
        if self._s is not None:
            try:
                self._s.close()
            finally:
                self._s = None

    def acik_mi(self):
        return self._s is not None

    def yaz(self, bayt):
        if self._s is None:
            raise ConnectionError("TCP taşıma kapalı")
        self._s.setblocking(True)
        try:
            self._s.sendall(bayt)
        finally:
            self._s.setblocking(False)

    def _cek(self):
        if self._s is None:
            return
        while True:
            try:
                veri = self._s.recv(4096)
            except (BlockingIOError, InterruptedError):
                return
            except OSError:
                self.kapat()
                return
            if not veri:
                self.kapat()
                return
            self._satirlar += self._tampon.ekle(veri)

    def oku(self):
        self._cek()
        s, self._satirlar = self._satirlar, []
        return s

    def bekle(self, ms):
        bitis = time.monotonic() + ms / 1000.0
        while True:
            self._cek()
            kalan = bitis - time.monotonic()
            if kalan <= 0:
                return
            time.sleep(min(0.005, kalan))


class SeriTasima(Tasima):
    """Gerçek ESP32 (USB-UART, 115200). YAZILMADI: robot / masa düzeneği gelince doldurulacak.

    Yapılacaklar (kaynak: yazilim-plani.md "Donanımdan gelen kurallar" E3, `main` kod/robot/seri.py port_ac):
    - pyserial ile aç; DTR etkin + RTS bırakık açıp sonra DTR'yi bırakmak (EN hiç LOW olmasın, reset yok);
      Linux'ta `stty -F /dev/ttyUSB0 -hupcl`.
    - `bekle(ms)` gerçek zaman (TcpTasima gibi), `oku()` bekletmeden tam satırlar.
    - Açılışta JSON olmayan satırlar (ROM açılış yazısı, pin-haritasi.md Y10) istemcide yok sayılır.
    """

    def __init__(self, port, baud=115200):
        self.port, self.baud = port, baud

    def ac(self):
        raise NotImplementedError("SeriTasima henüz yazılmadı (gerçek kart gelince; docstring'e bak)")
