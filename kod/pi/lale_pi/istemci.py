"""İnce Pi istemcisi: bağlan, komut gönder, cevap / telemetri al, kalp atışı.

Davranış durum makinesi, ses, yüz, jest oynatıcı YOK (sonraki paketler). İstemci yalnız protokolü
(`kod/ortak/protokol.json`) konuşur ve taşımayı (`tasima.py`) bilir; karşıda gerçek ESP32 mi sahte kart mı
olduğunu bilmez.

Gelen her satır protokole göre denetlenir; uymayan mesajlar `sema_hatalari` listesine düşer (testler bunu boş
bekler: sahte kart sözleşme dışı bir şey söylerse yakalanır).
"""

import os
import sys

_ORTAK = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ortak")
if _ORTAK not in sys.path:
    sys.path.insert(0, _ORTAK)

import lale_protokol as P  # noqa: E402


class ProtokolHatasi(Exception):
    pass


class ZamanAsimi(Exception):
    pass


class Esp32Istemci:
    def __init__(self, tasima, adim_ms=10, kayit_boyu=200):
        self.tasima = tasima
        self.adim_ms = adim_ms             # bekleme döngüsünün adımı (bellek içinde sanal ms)
        self.gelen = []                    # (zaman_ms, mesaj) sırayla; tüketmeyen okur
        self.son = {}                      # tür -> son mesaj ("odo", "sonar", "guc", "hazir", "engel", "ping", ...)
        self.sema_hatalari = []            # (satır, sorunlar)
        self.json_olmayan = []             # ROM açılış yazısı vb. (yok sayılır, kaydedilir)
        self.kayit = []                    # son satırlar (görünüm): ("<", satır) / (">", satır)
        self.kayit_boyu = kayit_boyu
        self.zaman_ms = 0                  # istemcinin kendi saati (bekledikçe artar)
        self._son_ping_ms = None

    # ------------------------------------------------------------ bağlantı

    def baglan(self):
        self.tasima.ac()

    def kapat(self):
        self.tasima.kapat()

    # ------------------------------------------------------------ gönderme

    def gonder(self, komut, denetle=True):
        """Komutu gönderir. denetle=True ise protokol dışı komut göndermeden önce ProtokolHatasi."""
        if denetle:
            sorun = P.komut_denetle(komut)
            if sorun:
                raise ProtokolHatasi("; ".join(sorun))
        bayt = P.kodla(komut)
        self._kaydet(">", bayt.decode("utf-8")[:-1])
        self.tasima.yaz(bayt)

    def ham_gonder(self, bayt):
        """Denetimsiz ham bayt (bozuk / eksik mesaj sınaması)."""
        self._kaydet(">", bayt.decode("utf-8", errors="replace").rstrip("\n"))
        self.tasima.yaz(bayt)

    # ------------------------------------------------------------ alma

    def _kaydet(self, yon, satir):
        self.kayit.append((yon, satir))
        if len(self.kayit) > self.kayit_boyu:
            del self.kayit[: len(self.kayit) - self.kayit_boyu]

    def _isle(self):
        for satir in self.tasima.oku():
            self._kaydet("<", satir)
            try:
                m = P.coz(satir)
            except P.BozukSatir:
                self.json_olmayan.append(satir)       # pin-haritasi.md Y10: açılış yazısı yok sayılır
                continue
            sorun = P.mesaj_denetle(m)
            if sorun:
                self.sema_hatalari.append((satir, sorun))
            tur = P.mesaj_turu(m)
            if tur == "cevap" and m.get("k") == "ping" and m.get("ok"):
                self.son["ping"] = m
            elif tur is not None and tur != "cevap":
                self.son[tur] = m
            self.gelen.append((self.zaman_ms, m))

    def bekle(self, ms):
        """Zamanı ilerletir (taşımaya göre sanal ya da gerçek) ve gelenleri işler."""
        kalan = ms
        while kalan > 0:
            d = min(self.adim_ms, kalan)
            self.tasima.bekle(d)
            self.zaman_ms += d
            kalan -= d
            self._isle()
        self._isle()

    def bekle_kosul(self, kosul, zaman_asimi_ms=2000, adim_ms=None, bas=None):
        """kosul(mesaj) doğru olan İLK mesajı bekler (gelen[bas:]; bas yoksa yalnız yeni gelenler); gelmezse ZamanAsimi."""
        if bas is None:
            bas = len(self.gelen)
        self._isle()
        gecen = 0
        adim = adim_ms or self.adim_ms
        while True:
            for _, m in self.gelen[bas:]:
                if kosul(m):
                    return m
            bas = len(self.gelen)
            if gecen >= zaman_asimi_ms:
                raise ZamanAsimi("koşul %d ms içinde sağlanmadı" % zaman_asimi_ms)
            self.bekle(adim)
            gecen += adim

    def istek(self, komut, zaman_asimi_ms=1000, denetle=True):
        """Komut gönder, cevabını (ok alanlı, aynı k ya da k'siz genel hata) bekle ve döndür."""
        bas = len(self.gelen)
        self.gonder(komut, denetle=denetle)
        k = komut.get("k") if isinstance(komut, dict) else None
        return self._cevap_bekle(bas, k, zaman_asimi_ms)

    def ham_istek(self, bayt, k=None, zaman_asimi_ms=1000):
        bas = len(self.gelen)
        self.ham_gonder(bayt)
        return self._cevap_bekle(bas, k, zaman_asimi_ms)

    def _cevap_bekle(self, bas, k, zaman_asimi_ms):
        gecen = 0
        while True:
            self._isle()
            for _, m in self.gelen[bas:]:
                if P.mesaj_turu(m) == "cevap" and (m.get("k") == k or "k" not in m):
                    return m
            if gecen >= zaman_asimi_ms:
                raise ZamanAsimi("%r için %d ms içinde cevap yok" % (k, zaman_asimi_ms))
            self.bekle(self.adim_ms)
            gecen += self.adim_ms

    # ------------------------------------------------------------ kısa yollar

    def ping(self):
        return self.istek({"k": "ping"})

    def arm(self):
        """Gücü devreye al. YALNIZ operatör isteğiyle (yazilim-plani.md E3); istemci kendiliğinden göndermez."""
        return self.istek({"k": "arm"})

    def devreye_al_ve_bekle(self, zaman_asimi_ms=1500):
        c = self.arm()
        if not c.get("ok"):
            return c
        return self.bekle_kosul(lambda m: m.get("k") == "guc" and "ok" not in m and m.get("guc") in ("devrede", "ariza"),
                                zaman_asimi_ms)

    def sur(self, v, w, rampa=None):
        komut = {"k": "sur", "v": v, "w": w}
        if rampa is not None:
            komut["rampa"] = rampa
        return self.istek(komut)

    def sur_tut(self, v, w, sure_ms, aralik_ms=200, ping_ms=1000, dur_kosul=None):
        """sure_ms boyunca `sur`u aralik_ms'de bir tekrarlar (bekçi 500 ms), ping_ms'de bir kalp atışı.

        dur_kosul(istemci) doğru olursa erken biter. Son cevabı döndürür.
        """
        gecen = 0
        son = None
        son_ping = -ping_ms
        while gecen < sure_ms:
            son = self.sur(v, w)
            if gecen - son_ping >= ping_ms:
                self.ping()
                son_ping = gecen
            adim = min(aralik_ms, sure_ms - gecen)
            self.bekle(adim)
            gecen += adim
            if dur_kosul is not None and dur_kosul(self):
                break
        return son

    def kalp_atisi(self, aralik_ms=None):
        """Son ping'den bu yana aralık dolduysa ping gönder (devredeyken 5 s sessizlik kuralı)."""
        aralik_ms = aralik_ms or P.ZAMAN["ping_onerilen"]
        if self._son_ping_ms is None or self.zaman_ms - self._son_ping_ms >= aralik_ms:
            self._son_ping_ms = self.zaman_ms
            self.gonder({"k": "ping"})

    def mesajlar(self, tur, bas=0):
        """gelen[bas:] içindeki belli türden mesajlar ("cevap", "guc", "odo", ...)."""
        return [m for _, m in self.gelen[bas:] if P.mesaj_turu(m) == tur]
