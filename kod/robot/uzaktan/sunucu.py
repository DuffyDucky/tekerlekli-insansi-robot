# Ne yapıyor: telefondan kumanda için küçük web sunucusu (yalnız standart kütüphane: http.server).
# Pi'de robotla aynı süreçte, ayrı iş parçacığında çalışır. Telefon tarayıcıda http://lale.local:8080 açar.
#   GET  /                 kumanda sayfası (sayfa.html)      GET /manifest.json, /ikon.svg, /ikon-192.png
#   POST /giris {pin}      doğru PIN -> oturum çerezi; yanlış PIN 1 s bekletilir
#   GET  /durum            robotun durumu (çerez gerekir)    GET /bolgeler   bölge listesi
#   POST /sur {v,w}  /dur  /jest {ad,yon}  /soyle {metin}  /bolge {ad}  /bakim {ac}
# Güvenlik: yalnız yerel ağ için; POST yalnız JSON (application/json), gövde en çok 4 KB, başka siteden
# gelen istek (Origin farklı) reddedilir. İnternete açmayın (port yönlendirme yok).

import hmac
import json
import os
import secrets
import socket
import struct
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from robot.uzaktan.kopru import KopruHatasi

KLASOR = os.path.dirname(os.path.abspath(__file__))
SAYFA_DOSYASI = os.path.join(KLASOR, "sayfa.html")
MANIFEST_DOSYASI = os.path.join(KLASOR, "manifest.json")
CEREZ_ADI = "lale_oturum"
CEREZ_OMRU = 30 * 24 * 3600          # saniye; çerez 30 gün geçerli (sunucu yeniden başlarsa PIN yeniden sorulur)
EN_BUYUK_GOVDE = 4096
EN_FAZLA_OTURUM = 50
YANLIS_PIN_BEKLEME = 1.0

IKON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">'
            '<rect width="96" height="96" rx="20" fill="#0f172a"/>'
            '<path d="M40 16h16v24h24v16H56v24H40V56H16V40h24z" fill="#e5e7eb"/></svg>')


def png_ikon(boyut):
    """Koyu zemin üstünde açık renk artı (D-pad) PNG'si; harici dosya ve kütüphane gerekmez."""
    zemin, isaret = b"\x0f\x17\x2a", b"\xe5\xe7\xeb"
    orta, kol, kalinlik = boyut / 2, boyut * 0.33, boyut * 0.083
    satirlar = []
    for y in range(boyut):
        satir = bytearray(b"\x00")                     # PNG satır filtresi: yok
        for x in range(boyut):
            dx, dy = abs(x + 0.5 - orta), abs(y + 0.5 - orta)
            arti = (dx <= kalinlik and dy <= kol) or (dy <= kalinlik and dx <= kol)
            satir += isaret if arti else zemin
        satirlar.append(bytes(satir))

    def parca(tur, veri):
        return struct.pack(">I", len(veri)) + tur + veri + struct.pack(">I", zlib.crc32(tur + veri) & 0xFFFFFFFF)

    baslik = struct.pack(">IIBBBBB", boyut, boyut, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + parca(b"IHDR", baslik) + parca(b"IDAT", zlib.compress(b"".join(satirlar), 9))
            + parca(b"IEND", b""))


def yerel_adresler():
    """Bu makinenin yerel ağ IP'leri (127.x hariç). İnternete paket gitmez (UDP connect yalnız yol seçer)."""
    adresler = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            adresler.append(s.getsockname()[0])
    except OSError:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip not in adresler:
                adresler.append(ip)
    except OSError:
        pass
    return [ip for ip in adresler if not ip.startswith("127.")]


class UzaktanSunucu:
    def __init__(self, robot_koprusu, port=8080, pin="1234", adres="0.0.0.0", yanlis_pin_bekleme=YANLIS_PIN_BEKLEME):
        self.kopru = robot_koprusu
        self.istenen_port = int(port)
        self.pin = str(pin)
        self.adres = adres
        self.yanlis_pin_bekleme = yanlis_pin_bekleme
        self.oturumlar = []                  # geçerli çerez değerleri (eskiden yeniye)
        self.oturum_kilidi = threading.Lock()
        self.pin_kilidi = threading.Lock()
        self.httpd = None
        self._is_parcacigi = None
        self._ikonlar = {}

    @property
    def port(self):
        return self.httpd.server_address[1] if self.httpd else self.istenen_port

    def adresler(self):
        """Telefonda açılacak adresler: IP'ler + ad.local (Pi'de lale.local)."""
        liste = [f"http://{ip}:{self.port}" for ip in yerel_adresler()]
        ad = socket.gethostname().split(".")[0].lower()
        liste.append(f"http://{ad}.local:{self.port}")
        if ad != "lale":
            liste.append(f"http://lale.local:{self.port}  (Pi'de)")
        return liste

    def baslat(self):
        self.httpd = ThreadingHTTPServer((self.adres, self.istenen_port), istek_isleyici_kur(self))
        self.httpd.daemon_threads = True
        self._is_parcacigi = threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.1},
                                              name="uzaktan-sunucu", daemon=True)
        self._is_parcacigi.start()
        self.kopru.baslat()
        if self.pin == "1234":
            print("[uzaktan] UYARI: PIN varsayılan (1234); ayarlar.yaml -> uzaktan.pin ile değiştirin.")
        return self

    def kapat(self):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        self.kopru.kapat()

    # ---------- oturum ----------

    def pin_dogru_mu(self, pin):
        return hmac.compare_digest(str(pin).encode("utf-8"), self.pin.encode("utf-8"))

    def oturum_ac(self):
        anahtar = secrets.token_urlsafe(24)
        with self.oturum_kilidi:
            self.oturumlar.append(anahtar)
            del self.oturumlar[:-EN_FAZLA_OTURUM]
        return anahtar

    def oturum_gecerli_mi(self, anahtar):
        if not anahtar:
            return False
        with self.oturum_kilidi:
            return any(hmac.compare_digest(anahtar, o) for o in self.oturumlar)

    def ikon(self, boyut):
        if boyut not in self._ikonlar:
            self._ikonlar[boyut] = png_ikon(boyut)
        return self._ikonlar[boyut]


def cerezden_oku(baslik, ad):
    for parca in (baslik or "").split(";"):
        anahtar, _, deger = parca.strip().partition("=")
        if anahtar == ad:
            return deger
    return None


def istek_isleyici_kur(sunucu):
    kopru = sunucu.kopru

    class IstekIsleyici(BaseHTTPRequestHandler):
        server_version = "LaleKumanda/1"
        protocol_version = "HTTP/1.1"

        def log_message(self, bicim, *args):       # her isteği yazmasın (10 Hz sur); hatalar yine yazılır
            pass

        # ---------- cevap ----------

        def gonder(self, kod, govde, tur, ek_basliklar=None):
            self.send_response(kod)
            self.send_header("Content-Type", tur)
            self.send_header("Content-Length", str(len(govde)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            for ad, deger in (ek_basliklar or {}).items():
                self.send_header(ad, deger)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(govde)

        def json_gonder(self, kod, veri, ek=None):
            basliklar = {"Cache-Control": "no-store", **(ek or {})}
            self.gonder(kod, json.dumps(veri, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8", basliklar)

        def hata(self, kod, mesaj):
            self.close_connection = True            # okunmamış gövde bağlantıda kalmasın
            self.json_gonder(kod, {"ok": False, "hata": mesaj})

        # ---------- denetimler ----------

        def oturum_var(self):
            return sunucu.oturum_gecerli_mi(cerezden_oku(self.headers.get("Cookie"), CEREZ_ADI))

        def ayni_kaynak(self):
            """Origin başlığı varsa Host ile aynı olmalı (başka bir site telefondan robotu süremesin)."""
            kaynak = self.headers.get("Origin")
            return not kaynak or urlparse(kaynak).netloc == self.headers.get("Host", "")

        def govde_oku(self):
            """Gövde her durumda önce okunur: okunmadan kapatılan bağlantı Windows'ta istemciye RST gönderir."""
            try:
                uzunluk = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                raise KopruHatasi("Content-Length geçersiz.")
            if uzunluk > EN_BUYUK_GOVDE:
                raise KopruHatasi("İstek çok büyük.", 413)
            return self.rfile.read(uzunluk) if uzunluk else b"{}"

        def json_coz(self, ham):
            if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
                raise KopruHatasi("Yalnız JSON kabul edilir (Content-Type: application/json).", 415)
            try:
                veri = json.loads(ham.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise KopruHatasi("JSON okunamadı.")
            if not isinstance(veri, dict):
                raise KopruHatasi("JSON bir nesne olmalı: {...}.")
            return veri

        # ---------- GET ----------

        def do_GET(self):
            yol = urlparse(self.path).path
            if yol in ("/", "/index.html"):
                with open(SAYFA_DOSYASI, "rb") as f:
                    govde = f.read()
                self.gonder(200, govde, "text/html; charset=utf-8", {
                    "Cache-Control": "no-cache",
                    "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; "
                    "style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; "
                    "manifest-src 'self'; frame-ancestors 'none'"})
            elif yol == "/manifest.json":
                with open(MANIFEST_DOSYASI, "rb") as f:
                    self.gonder(200, f.read(), "application/manifest+json; charset=utf-8")
            elif yol == "/ikon.svg":
                self.gonder(200, IKON_SVG.encode("utf-8"), "image/svg+xml")
            elif yol in ("/ikon-192.png", "/ikon-512.png"):
                self.gonder(200, sunucu.ikon(192 if "192" in yol else 512), "image/png",
                            {"Cache-Control": "max-age=86400"})
            elif yol in ("/durum", "/bolgeler"):
                if not self.oturum_var():
                    return self.hata(401, "PIN gerekli.")
                if yol == "/durum":
                    self.json_gonder(200, {"ok": True, **kopru.durum()})
                else:
                    self.json_gonder(200, {"ok": True, "bolgeler": kopru.bolge_listesi()})
            else:
                self.hata(404, "Bulunamadı.")

        do_HEAD = do_GET

        # ---------- POST ----------

        def do_POST(self):
            yol = urlparse(self.path).path
            try:
                ham = self.govde_oku()
                if not self.ayni_kaynak():
                    raise KopruHatasi("Başka bir siteden gelen istek reddedildi.", 403)
                veri = self.json_coz(ham)
                if yol == "/giris":
                    return self.giris(veri)
                if not self.oturum_var():
                    raise KopruHatasi("PIN gerekli.", 401)
                if yol == "/sur":
                    v, w = kopru.sur(veri.get("v", 0), veri.get("w", 0))
                    return self.json_gonder(200, {"ok": True, "v": v, "w": w})
                if yol == "/dur":
                    kopru.dur()
                    return self.json_gonder(200, {"ok": True})
                if yol == "/jest":
                    return self.json_gonder(200, {"ok": True, **kopru.jest(veri.get("ad"), veri.get("yon"))})
                if yol == "/soyle":
                    return self.json_gonder(200, {"ok": True, **kopru.soyle(veri.get("metin"))})
                if yol == "/bolge":
                    return self.json_gonder(200, {"ok": True, **kopru.bolge_sec(veri.get("ad"))})
                if yol == "/bakim":
                    if not isinstance(veri.get("ac"), bool):
                        raise KopruHatasi("'ac' true ya da false olmalı.")
                    return self.json_gonder(200, {"ok": True, **kopru.bakim(veri["ac"])})
                raise KopruHatasi("Bulunamadı.", 404)
            except KopruHatasi as h:
                self.hata(h.kod, str(h))
            except Exception as h:                  # beklenmeyen hata sunucuyu düşürmesin
                print(f"[uzaktan] {yol} hatası: {h}")
                self.hata(500, "Robotta beklenmeyen hata; terminale bakın.")

        def giris(self, veri):
            with sunucu.pin_kilidi:          # denemeler sırayla: paralel isteklerle de saniyede en çok 1 yanlış PIN
                if not sunucu.pin_dogru_mu(veri.get("pin", "")):
                    time.sleep(sunucu.yanlis_pin_bekleme)    # tahmin denemesini yavaşlatır
                    raise KopruHatasi("PIN yanlış.", 401)
            cerez = (f"{CEREZ_ADI}={sunucu.oturum_ac()}; Path=/; Max-Age={CEREZ_OMRU}; "
                     "HttpOnly; SameSite=Strict")
            self.json_gonder(200, {"ok": True}, {"Set-Cookie": cerez})

    return IstekIsleyici
