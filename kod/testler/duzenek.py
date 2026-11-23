"""Test düzeneği: hedef karta (sahte ya da ileride gerçek) bağlı istemci + fiziksel ortam + hakem.

Testler kartla YALNIZ protokol üzerinden konuşur (`self.esp`, `lale_pi.istemci.Esp32Istemci`). Protokolün
taşıyamadığı fiziksel şeyler ayrı bir arayüzden yapılır (`self.ortam`): mantara basmak, kabloyu çekmek, robotu bir
yere koymak. Haritadaki gerçek konum ve hız "hakem"dir (`self.hakem()`): kartın söylediğini dışarıdan doğrulamak
için okunur, kartın iç durumuna (çekirdek değişkenleri) testten erişilmez.

Hedef `LALE_HEDEF` ortam değişkeniyle seçilir:
- `bellek` (varsayılan): sahte kart, bellek içi taşıma, sanal saat (deterministik, hızlı).
- `tcp`: sahte kart gerçek zamanda, yerel TCP portundan (sanal seri hat). Zaman toleransı geniş.
- `fizik`: aynı sahte kart (firmware modeli aynen), dünya 2B yerine MuJoCo fiziği (Y0f, `kod/fizik/`); bellek içi, sanal
  saat. `mujoco` kurulu değilse testler "atlandı" olur (2B dünya etkilenmez). Koşucu: `kod/fizik/kos_fizik.py`.
- `seri:COM3` gibi: gerçek ESP32. `SeriTasima` henüz yazılmadı: bütün testler "atlandı" olur. Gerçek kartta
  ortam işlemleri (mantar, kablo) operatör eliyle yapılacak; hakem yok (hakem isteyen kontroller atlanır).
"""

import math
import os
import sys
import unittest

import lale_protokol as P
from sahte_esp32.cekirdek import SahteEsp32
from sahte_esp32.harita import Harita
from sahte_esp32.tasima import BellekTasima
from lale_pi.istemci import Esp32Istemci
from lale_pi.tasima import SeriTasima, TcpTasima


TIK_M = math.pi * P.parametre("teker_capi_m") / P.parametre("enkoder_tik_tur")   # bir enkoder tikinin teker yolu (TAHMİN)

# Fizik hedefinde (LALE_HEDEF=fizik) DOĞRULAMA düzeyindeki farklar. 2B dünya ideal (anında durma, kaymasız teker, tam hız);
# fizikte yalnız aşağıdaki doğrulamalar fiziksel karşılığıyla değişir, testin geri kalanı (bekçi tetiklenmesi, kilit,
# reset, olay iletileri, hata cevapları) iki dünyada aynen koşar. 2B'de bu sözlük hiç okunmaz.
# Duruş payları: 0,3 m/s'den protokol üstünden ölçülen (Y0f-gunluk düzeltme turu; ana parametreler) x ≈ 1,5.
FIZIK_DURUS = {
    # PWM 0 + EN HIGH (kısa devre freni): bekçi, ping / bozuk satır, kablo kopması (bekçi). Ölçülen 270 ms, 15,6 mm.
    "fren": dict(ms=400, m=0.025),
    # EN LOW (motor boşta): acil stop, reset. Ölçülen 870 ms, 0,128 m.
    "bosta": dict(ms=1300, m=0.20),
}
FIZIK_FARKLARI = {
    "durus": "anında durma yerine: sürücü komutu kesik (hedef 0; fren = EN HIGH + PWM 0, boşta = EN LOW) ve robot "
             "FIZIK_DURUS payı içinde durur (enkoder sabit, yol sınırlı)",
    "reset_odo": "reset sonrası ilk odo (0, 0) yerine: sayaç sıfırlandı (reset öncesinden küçük) ve boşta kayma payından az tik",
    "dur_fren_yolu": "dur fren yolu üst sınırına +5 mm (açık çevrim: teker komut rampasının arkasından gelir; ölçülen fazlalık 0,1 mm)",
    "kablo_yolu": "kopukken yol üst sınırına fren payı (bekçi durmasından sonra kısa devre freni kayması)",
    "hiz_esitligi": "hakem teker / gövde hızı 6 basamak eşitlik yerine ±0,01 m/s (açık çevrim KP = 0: akü 13,1 V, yük)",
    "w_kirpma": "yay dönüşünde enkoder oranı yerine firmware'in sürücüye verdiği teker hedefleri oranı (kırpma firmware'in "
                "işi); kızak yönlendirmeli robotun yayı gerçekten çizip çizmediği fiziğin bulgusudur (SIMULASYON.md dönüş)",
}


def _operator(is_):
    raise unittest.SkipTest("operatör adımı gerekli (gerçek kart Ortam'ı henüz yok): %s" % is_)


class Ortam:
    """Fiziksel dünya arayüzü (protokol dışı). Gerçek kartta operatör / test donanımı uygular; uygulanmamış adım
    testi "atlandı" yapar."""

    tolerans_ms = 10
    hakem_var = False
    fizik = False          # True: MuJoCo dünyası (FIZIK_FARKLARI doğrulamaları)

    def mantar_bas(self):
        _operator("mantara bas")

    def mantar_birak(self):
        _operator("mantarı bırak")

    def kablo_kopar(self):
        _operator("USB kablosunu çek")

    def kablo_bagla(self):
        _operator("USB kablosunu tak")

    def ana_anahtar(self, acik):
        _operator("ana anahtar %s" % ("aç" if acik else "kapat"))

    def i2c(self, saglam):
        _operator("PCA9685 I2C hattını %s" % ("bağla" if saglam else "kopar"))

    def konum_ayarla(self, x, y, aci_derece):
        _operator("robotu (%.2f, %.2f, %.0f°) konumuna koy" % (x, y, aci_derece))

    def hakem(self):
        raise unittest.SkipTest("hakem yok (gerçek kart)")

    def kapat(self):
        pass


class SahteOrtam(Ortam):
    hakem_var = True

    def __init__(self, cekirdek, tasima, kilit=None, sunucu=None):
        self._c = cekirdek
        self._t = tasima
        self._kilit = kilit
        self._sunucu = sunucu

    def _yap(self, is_):
        if self._kilit is None:
            return is_()
        with self._kilit:
            return is_()

    def mantar_bas(self):
        self._yap(lambda: setattr(self._c, "mantar", True))

    def mantar_birak(self):
        self._yap(lambda: setattr(self._c, "mantar", False))

    def ana_anahtar(self, acik):
        self._yap(lambda: setattr(self._c, "ana_anahtar", bool(acik)))

    def i2c(self, saglam):
        self._yap(lambda: setattr(self._c, "i2c_saglam", bool(saglam)))

    def konum_ayarla(self, x, y, aci_derece):
        self._yap(lambda: self._c.konum_ayarla(x, y, math.radians(aci_derece)))

    def hakem(self):
        return self._yap(self._c.hakem)

    def kablo_kopar(self):
        if self._sunucu is None:
            self._t.kopar()
        else:
            self._t.kapat()
            self._sunucu.istemci_kopar()

    def kablo_bagla(self):
        if self._sunucu is None:
            self._t.bagla()
        else:
            self._t.ac()

    def kapat(self):
        if self._sunucu is not None:
            self._t.kapat()
            self._sunucu.durdur()


def duzenek_kur(harita="oda_bos", konum=None):
    """(istemci, ortam) döner. konum: (x, y, aci_derece) ya da None (haritanın başlangıcı)."""
    hedef = os.environ.get("LALE_HEDEF", "bellek")
    if hedef.startswith("seri:"):
        raise unittest.SkipTest("gerçek kart taşıması (SeriTasima) henüz yazılmadı: %s" % hedef)
    h = Harita.dosyadan(harita)
    k = None if konum is None else (konum[0], konum[1], math.radians(konum[2]))
    fizik = hedef == "fizik"
    if fizik:
        c = _fizik_karti(h, k)
        hedef = "bellek"
    else:
        c = SahteEsp32(h, konum=k)
    hakemsiz = os.environ.get("LALE_HAKEM") == "yok"     # gerçek kart provası: hakem okunamaz, yalnız protokol
    if hedef == "bellek":
        t = BellekTasima(c)
        esp = Esp32Istemci(t)
        esp.baglan()
        o = SahteOrtam(c, t)
        o.hakem_var = not hakemsiz
        o.fizik = fizik
        return esp, o
    if hedef == "tcp":
        from sahte_esp32.tcp_sunucu import TcpSunucu
        s = TcpSunucu(c, port=0).baslat()
        t = TcpTasima(port=s.port)
        esp = Esp32Istemci(t)
        esp.baglan()
        esp.bekle(50)
        o = SahteOrtam(c, t, kilit=s.kilit, sunucu=s)
        o.hakem_var = not hakemsiz
        o.tolerans_ms = 80
        return esp, o
    raise ValueError("bilinmeyen LALE_HEDEF: %r" % hedef)


def _fizik_karti(harita, konum):
    """Y0f fizik arka ucu (kod/fizik/fizik_esp32.py); bağımlılık yoksa test atlanır."""
    fizik = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fizik")
    if fizik not in sys.path:
        sys.path.insert(0, fizik)
    import dunya
    if not dunya.FIZIK_VAR:
        raise unittest.SkipTest("fizik bağımlılığı (mujoco) yok: %s" % dunya.FIZIK_HATA)
    from fizik_esp32 import FizikEsp32
    v = os.environ.get("LALE_VARYANT")                   # yalnız VARSAYIM denemesi (kod/fizik/varyantlar.py); yoksa bugünkü robot
    if v:
        import varyantlar
        return FizikEsp32(harita, konum=konum, varyant=varyantlar.al(v))
    return FizikEsp32(harita, konum=konum)


class LaleTesti(unittest.TestCase):
    """Ortak kurulum. Alt sınıf `HARITA` ve `KONUM` verebilir."""

    HARITA = "oda_bos"
    KONUM = None

    def setUp(self):
        self.esp, self.ortam = duzenek_kur(self.HARITA, self.KONUM)
        self.addCleanup(self.ortam.kapat)
        self.tol = self.ortam.tolerans_ms

    def tearDown(self):
        # Kartın söylediği her şey sözleşmeye uymalı (protokol.json); uymayan mesaj testi bozar.
        self.assertEqual(self.esp.sema_hatalari, [], "protokol dışı mesaj")

    # ------------------------------------------------------------ yardımcılar

    def hakem(self):
        """Hakem zorunlu: yoksa test atlanır. Asıl iddiası protokolden doğrulanabilen testler `hakem_varsa` kullanır."""
        if not self.ortam.hakem_var:
            self.skipTest("hakem yok (gerçek kart)")
        return self.ortam.hakem()

    def hakem_varsa(self):
        """Ek doğrulama için hakem ya da None (gerçek kartta None; test protokol yarısıyla sürer)."""
        return self.ortam.hakem() if self.ortam.hakem_var else None

    # ------------------------------------------------------------ yalnız protokolden ölçüm (odo)

    def odo_hizlari(self, bas=0):
        """gelen[bas:] içindeki ardışık odo çiftlerinden [(ms, v_sol, v_sag)] (m/s; ms pencerenin sonu)."""
        odo = self.esp.mesajlar("odo", bas)
        hiz = []
        for a, b in zip(odo, odo[1:]):
            dt = (b["ms"] - a["ms"]) / 1000.0
            if dt > 0:
                hiz.append((b["ms"], (b["sol"] - a["sol"]) * TIK_M / dt, (b["sag"] - a["sag"]) * TIK_M / dt))
        return hiz

    def sur_olc(self, v, w, sure_ms):
        """sure_ms boyunca sür; bu sürede kartın odo'sundan ölçülen son pencerenin hızı (v_ort, v_sol, v_sag)."""
        bas = len(self.esp.gelen)
        self.esp.sur_tut(v, w, sure_ms)
        h = self.odo_hizlari(bas)
        self.assertTrue(h, "odo gelmedi")
        _, sol, sag = h[-1]
        return (sol + sag) / 2.0, sol, sag

    def enkoder_duruyor(self, bas=0, sonra_ms=None, en_az=2, durus=None):
        """gelen[bas:] içinde (ms > sonra_ms olan) odo mesajları en az `en_az` tane ve hepsi aynı tik mi?

        durus ("fren" / "bosta"): durma komutunun türü. 2B'de etkisiz (anında durur). Fizikte `durus_dogrula` koşar
        (sürücü komutu kesik, robot FIZIK_DURUS payı içinde durur) ve sabitlik pay süresinden sonrası için aranır."""
        if durus is not None and self.ortam.fizik:
            sonra_ms = self.durus_dogrula(durus, sonra_ms, bas, en_az)
        odo = [m for m in self.esp.mesajlar("odo", bas) if sonra_ms is None or m["ms"] > sonra_ms]
        self.assertGreaterEqual(len(odo), en_az, "yeterli odo yok")
        return len({(m["sol"], m["sag"]) for m in odo}) == 1

    # ------------------------------------------------------------ fizik hedefi: doğrulama düzeyindeki farklar

    def surucu_kesik_dogrula(self, durus):
        """Fizik: motor sürücüsünün girişi kesik mi (firmware hedefi 0; fren: EN HIGH + PWM 0, boşta: EN LOW)?"""
        if not (self.ortam.fizik and self.ortam.hakem_var):
            return
        s = self.ortam.hakem()["surucu"]
        self.assertEqual(s["hedef_m_s"], [0.0, 0.0], "durma komutunda firmware teker hedefi sıfırlanmadı: %r" % (s,))
        if durus == "fren":
            self.assertEqual((s["suruluyor"], s["pwm"]), (True, [0.0, 0.0]), "kısa devre freni yok: %r" % (s,))
        else:
            self.assertFalse(s["suruluyor"], "boşta beklenirken sürücü EN HIGH: %r" % (s,))

    def hakem_durdu(self, durus, mesaj):
        """2B: hakem gövde hızı tam 0 (anında durma). Fizik: o anda sürücü komutu kesik (FIZIK_FARKLARI "durus"); robotun
        pay içinde durduğu ayrıca `enkoder_duruyor(..., durus=)` ya da testin yol sınırıyla doğrulanır."""
        if self.ortam.fizik:
            self.surucu_kesik_dogrula(durus)
            return
        h = self.hakem_varsa()
        if h:
            self.assertEqual(h["v"], 0.0, mesaj)

    def hiz_esit(self, gercek, beklenen, mesaj=None):
        """2B: 6 basamak eşit. Fizik: ±0,01 m/s (FIZIK_FARKLARI "hiz_esitligi")."""
        if self.ortam.fizik:
            self.assertAlmostEqual(gercek, beklenen, delta=0.01, msg=mesaj)
        else:
            self.assertAlmostEqual(gercek, beklenen, places=6, msg=mesaj)

    def durus_dogrula(self, durus, sonra_ms, bas, en_az=2):
        """Fizik: "anında durma"nın fiziksel karşılığı. Sürücü komutu kesik; sonra_ms'den en çok FIZIK_DURUS[durus]
        süresi içinde enkoder durur ve bu arada en çok FIZIK_DURUS yolu alınır. Sabitliğin aranacağı yeni sonra_ms'i döner."""
        pay = FIZIK_DURUS[durus]
        self.surucu_kesik_dogrula(durus)
        sinir = sonra_ms + pay["ms"]
        for _ in range(200):                    # pay süresinden sonra en az en_az odo gelene dek bekle
            if len([m for m in self.esp.mesajlar("odo", bas) if m["ms"] > sinir]) >= en_az:
                break
            self.esp.bekle(50)
        odo = [m for m in self.esp.mesajlar("odo") if m["ms"] > 0]
        once = [m for m in odo if m["ms"] <= sonra_ms]
        if once:
            yol = (odo[-1]["sol"] - once[-1]["sol"] + odo[-1]["sag"] - once[-1]["sag"]) / 2.0 * TIK_M
            hiz = self.odo_hizlari(bas)
            v0 = max([abs(a + b) / 2.0 for ms, a, b in hiz if ms <= sonra_ms + 100] or [0.0])
            # durma komutuna kadar süren tam hız kısmı (en çok bir odo aralığı) yoldan düşülür
            yol -= v0 * (sonra_ms - once[-1]["ms"]) / 1000.0
            self.assertLessEqual(abs(yol), pay["m"], "durma komutundan sonra %.3f m gitti (pay %.3f m)" % (yol, pay["m"]))
        if self.ortam.hakem_var:
            self.assertEqual(self.ortam.hakem()["v"], 0.0, "pay süresi (%d ms) sonunda gövde duruyor değil" % pay["ms"])
        return sinir

    def yetenek_gerek(self, ad):
        y = self.esp.ping().get("yetenekler", [])
        if ad not in y:
            self.skipTest("kartta '%s' yeteneği yok (firmware 0.5.0'da TASLAK eklenti)" % ad)

    def devreye_al(self):
        olay = self.esp.devreye_al_ve_bekle()
        self.assertEqual(olay.get("guc"), "devrede", "devreye alınamadı: %r" % (olay,))
        return olay

    def guc_olayi_bekle(self, guc, zaman_asimi_ms=2000, bas=None):
        return self.esp.bekle_kosul(lambda m: m.get("k") == "guc" and "ok" not in m and m.get("guc") == guc,
                                    zaman_asimi_ms, bas=bas)

    def hata_bekle(self, cevap, hata, k="__ayni__"):
        self.assertIs(cevap.get("ok"), False, cevap)
        self.assertEqual(cevap.get("hata"), hata, cevap)
        if k != "__ayni__":
            self.assertEqual(cevap.get("k"), k, cevap)

    def odo_son(self):
        self.esp.bekle(110)
        return self.esp.son["odo"]
