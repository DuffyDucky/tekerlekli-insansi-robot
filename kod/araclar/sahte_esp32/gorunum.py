"""Tarayıcıda üstten bakış: oda, robot, sonar ışınları, durum; klavyeyle sürüş ve acil stop.

Çekirdekten ayrı ve isteğe bağlı. Yalnız standart kitaplık (http.server); dış JS kitaplığı / CDN yok.

Komut yolu protokolden geçer: sayfa → HTTP → "pilot" iş parçacığındaki Pi istemcisi (`lale_pi.istemci`, TCP taşıma)
→ sahte ESP32'nin TCP portu. Sayfanın gösterdiği iki ayrı şey var: "Pi'nin gördüğü" (protokolden gelen mesajlar) ve
"hakem" (haritadaki gerçek konum; çekirdekten salt okunur). Mantar (acil stop) fiziksel bir düğmedir, protokol
komutu değil: sayfadaki mantar tuşu fiziksel ortamı değiştirir (gerçek robotta eldeki mantar).
"""

import json
import math
import os
import queue
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_KOD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _y in (os.path.join(_KOD, "pi"), os.path.join(_KOD, "ortak")):
    if _y not in sys.path:
        sys.path.insert(0, _y)

from lale_pi.istemci import Esp32Istemci, ProtokolHatasi  # noqa: E402
from lale_pi.tasima import TcpTasima  # noqa: E402

SAYFA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gorunum.html")
IZ_BOYU = 600
YEREL_ADLAR = ("127.0.0.1", "localhost")


def surus_dogrula(v, w):
    """Görünümden gelen sürüş isteğini doğrular: sonlu sayı (bool değil), ±1'e kırpılmış (v, w) döner ya da ValueError."""
    sonuc = []
    for ad, x in (("v", v), ("w", w)):
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise ValueError("%s sayı olmalı: %r" % (ad, x))
        x = float(x)
        if not math.isfinite(x):
            raise ValueError("%s sonlu olmalı: %r" % (ad, x))
        sonuc.append(max(-1.0, min(1.0, x)))
    return tuple(sonuc)


class Pilot(threading.Thread):
    """Pi tarafı: istemciyi tek iş parçacığında sürer. Sürüş isteği varken 100 ms'de bir `sur`, 1 s'de bir `ping`."""

    def __init__(self, port):
        super().__init__(name="pilot", daemon=True)
        self.esp = Esp32Istemci(TcpTasima(port=port))
        self.kuyruk = queue.Queue()
        self.kilit = threading.Lock()
        self.istek = (0.0, 0.0)
        self._son_istek_ms = 0
        self.surus_acik = False
        self.anlik = {}
        self.son_cevap = None
        self.hatalar = []
        self._dur = threading.Event()

    def durdur(self):
        self._dur.set()

    def surus(self, v, w):
        """Sürüş isteği. v, w sonlu sayı olmalı (bool değil); ±1'e kırpılır. Geçersizse ValueError (istek değişmez)."""
        v, w = surus_dogrula(v, w)
        with self.kilit:
            self.istek = (v, w)
            self._son_istek_ms = time.monotonic()

    def canli_mi(self):
        return self.is_alive()

    def run(self):
        self.esp.baglan()
        self._son = [0.0, 0.0]                              # son sur, son ping
        while not self._dur.is_set():
            try:
                self._tur()
            except Exception as h:                          # tek kötü tur iş parçacığını öldürmesin
                self.hatalar.append("%s: %s" % (type(h).__name__, h))
                del self.hatalar[:-50]
                with self.kilit:
                    self.istek = (0.0, 0.0)                 # şüphede dur
                time.sleep(0.05)

    def _tur(self):
        """Pilot döngüsünün bir turu: kuyruktaki komutlar, sürüş, kalp atışı, anlık durum."""
        simdi = time.monotonic()
        while True:
            try:
                komut = self.kuyruk.get_nowait()
            except queue.Empty:
                break
            try:
                self.son_cevap = self.esp.istek(komut, zaman_asimi_ms=500)
            except (ProtokolHatasi, Exception) as h:    # görünüm çökmesin; hata sayfada
                self.son_cevap = {"istemci_hatasi": str(h), "komut": komut}
        with self.kilit:
            v, w = self.istek
            bayat = simdi - self._son_istek_ms > 0.6     # sayfa sustuysa (sekme kapandı) sürme
        if bayat:
            v = w = 0.0
        istek_var = abs(v) > 1e-6 or abs(w) > 1e-6
        try:
            if istek_var and simdi - self._son[0] >= 0.1:
                self.esp.gonder({"k": "sur", "v": v, "w": w})
                self._son[0] = simdi
                self.surus_acik = True
            elif not istek_var and self.surus_acik:
                self.esp.gonder({"k": "dur"})
                self.surus_acik = False
            if simdi - self._son[1] >= 1.0:
                self.esp.gonder({"k": "ping"})
                self._son[1] = simdi
            self.esp.bekle(20)
        except OSError as h:
            self.hatalar.append(str(h))
            time.sleep(0.2)
        self._anlik_guncelle(v, w)

    def _anlik_guncelle(self, v, w):
        son = self.esp.son
        a = {
            "guc": (son.get("guc") or {}).get("guc") or (son.get("ping") or {}).get("guc"),
            "ping": son.get("ping"), "odo": son.get("odo"), "sonar": son.get("sonar"), "engel": son.get("engel"),
            "guc_olayi": son.get("guc"), "istek": [v, w], "son_cevap": self.son_cevap,
            "kayit": self.esp.kayit[-14:], "sema_hatalari": len(self.esp.sema_hatalari),
        }
        with self.kilit:
            self.anlik = a
        if len(self.esp.gelen) > 5000:                      # uzun oturumda bellek büyümesin
            del self.esp.gelen[:-1000]


class Gorunum:
    def __init__(self, sunucu, http_port=8765):
        self.sunucu = sunucu
        self.pilot = Pilot(sunucu.port)
        self.iz = []
        gorunum = self

        class Isleyici(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _json(self, veri, kod=200):
                b = json.dumps(veri, ensure_ascii=False).encode("utf-8")
                self.send_response(kod)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

            def _kaynak_uygun(self):
                """Yalnız aynı köken: Host 127.0.0.1 / localhost + kendi portu (DNS yeniden bağlama), Origin varsa aynısı
                (başka sitenin tarayıcıdan POST atması, CSRF). Origin'siz istek (curl, test) Host'la sınanır."""
                port = gorunum.http_port
                izinli_host = {"%s:%d" % (a, port) for a in YEREL_ADLAR}
                if (self.headers.get("Host") or "").lower() not in izinli_host:
                    return False
                origin = self.headers.get("Origin")
                if origin is not None and origin.lower() not in {"http://" + h for h in izinli_host}:
                    return False
                # Sec-Fetch-Site yalnız durum değiştiren isteklerde (POST): sayfanın kendisine başka yerden (bağlantı,
                # uzantı) gitmek zararsızdır; başka sitenin okuması zaten CORS başlığı olmadığı için engellenir.
                site = self.headers.get("Sec-Fetch-Site")
                if self.command == "POST" and site is not None and site not in ("same-origin", "none"):
                    return False
                return True

            def do_GET(self):
                if not self._kaynak_uygun():
                    return self._json({"hata": "köken"}, 403)
                if self.path in ("/", "/index.html"):
                    with open(SAYFA, "rb") as f:
                        b = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(b)))
                    self.end_headers()
                    self.wfile.write(b)
                elif self.path == "/harita":
                    self._json(gorunum.sunucu.cekirdek.harita.sozluk())
                elif self.path == "/durum":
                    self._json(gorunum.durum())
                elif self.path == "/favicon.ico":
                    self.send_response(204)
                    self.end_headers()
                else:
                    self._json({"hata": "yok"}, 404)

            def do_POST(self):
                if not self._kaynak_uygun():
                    return self._json({"hata": "köken"}, 403)
                try:
                    n = int(self.headers.get("Content-Length") or 0)
                except ValueError:
                    return self._json({"hata": "uzunluk"}, 400)
                if not 0 <= n <= 4096:
                    return self._json({"hata": "uzunluk"}, 413)
                try:
                    veri = json.loads(self.rfile.read(n) or b"{}")
                except ValueError:
                    return self._json({"hata": "json"}, 400)
                if not isinstance(veri, dict):
                    return self._json({"hata": "nesne bekleniyor"}, 400)
                if self.path == "/surus":
                    if "v" not in veri or "w" not in veri:
                        return self._json({"hata": "v ve w gerekli"}, 400)
                    try:
                        gorunum.pilot.surus(veri["v"], veri["w"])
                    except ValueError as h:
                        return self._json({"hata": str(h)}, 400)
                    return self._json({"ok": True})
                if self.path == "/komut":
                    gorunum.pilot.kuyruk.put(veri)
                    return self._json({"ok": True})
                if self.path == "/ortam":
                    return self._json(gorunum.ortam(veri.get("islem")))
                self._json({"hata": "yok"}, 404)

        self.http = ThreadingHTTPServer(("127.0.0.1", http_port), Isleyici)
        self.http_port = self.http.server_address[1]

    def ortam(self, islem):
        c = self.sunucu.cekirdek
        with self.sunucu.kilit:
            if islem == "mantar_bas":
                c.mantar = True
            elif islem == "mantar_birak":
                c.mantar = False
            elif islem == "mantar_degistir":
                c.mantar = not c.mantar
            elif islem == "basa_don":
                c.konum_ayarla(*c.harita.baslangic)
                self.iz = []
            else:
                return {"hata": "bilinmeyen işlem: %r" % (islem,)}
            return {"ok": True, "mantar": c.mantar}

    def durum(self):
        c = self.sunucu.cekirdek
        with self.sunucu.kilit:
            h = c.hakem()
            isinlar = {ad: [list(i) for i in v] for ad, v in c.son_isinlar.items()}
            kose = c._koseler(c.x, c.y, c.aci)
        if not self.iz or abs(self.iz[-1][0] - h["x"]) + abs(self.iz[-1][1] - h["y"]) > 0.02:
            self.iz.append((round(h["x"], 3), round(h["y"], 3)))
            del self.iz[:-IZ_BOYU]
        with self.pilot.kilit:
            pi = dict(self.pilot.anlik)
        return {"hakem": h, "isinlar": isinlar, "kose": kose, "iz": self.iz, "pi": pi,
                "gecikme": self.sunucu.gecikme_sayisi,
                "pilot": {"canli": self.pilot.canli_mi(), "hatalar": self.pilot.hatalar[-3:]}}

    def baslat(self):
        self.pilot.start()
        threading.Thread(target=self.http.serve_forever, name="http", daemon=True).start()
        return self

    def durdur(self):
        self.pilot.durdur()
        self.http.shutdown()
        self.http.server_close()
