"""Test düzeneği: hedef karta (sahte ya da ileride gerçek) bağlı istemci + fiziksel ortam + hakem.

Testler kartla YALNIZ protokol üzerinden konuşur (`self.esp`, `lale_pi.istemci.Esp32Istemci`). Protokolün
taşıyamadığı fiziksel şeyler ayrı bir arayüzden yapılır (`self.ortam`): mantara basmak, kabloyu çekmek, robotu bir
yere koymak. Haritadaki gerçek konum ve hız "hakem"dir (`self.hakem()`): kartın söylediğini dışarıdan doğrulamak
için okunur, kartın iç durumuna (çekirdek değişkenleri) testten erişilmez.

Hedef `LALE_HEDEF` ortam değişkeniyle seçilir:
- `bellek` (varsayılan): sahte kart, bellek içi taşıma, sanal saat (deterministik, hızlı).
- `tcp`: sahte kart gerçek zamanda, yerel TCP portundan (sanal seri hat). Zaman toleransı geniş.
- `seri:COM3` gibi: gerçek ESP32. `SeriTasima` henüz yazılmadı: bütün testler "atlandı" olur. Gerçek kartta
  ortam işlemleri (mantar, kablo) operatör eliyle yapılacak; hakem yok (hakem isteyen kontroller atlanır).
"""

import math
import os
import unittest

import lale_protokol as P
from sahte_esp32.cekirdek import SahteEsp32
from sahte_esp32.harita import Harita
from sahte_esp32.tasima import BellekTasima
from lale_pi.istemci import Esp32Istemci
from lale_pi.tasima import SeriTasima, TcpTasima


TIK_M = math.pi * P.parametre("teker_capi_m") / P.parametre("enkoder_tik_tur")   # bir enkoder tikinin teker yolu (TAHMİN)


def _operator(is_):
    raise unittest.SkipTest("operatör adımı gerekli (gerçek kart Ortam'ı henüz yok): %s" % is_)


class Ortam:
    """Fiziksel dünya arayüzü (protokol dışı). Gerçek kartta operatör / test donanımı uygular; uygulanmamış adım
    testi "atlandı" yapar."""

    tolerans_ms = 10
    hakem_var = False

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
    c = SahteEsp32(h, konum=k)
    hakemsiz = os.environ.get("LALE_HAKEM") == "yok"     # gerçek kart provası: hakem okunamaz, yalnız protokol
    if hedef == "bellek":
        t = BellekTasima(c)
        esp = Esp32Istemci(t)
        esp.baglan()
        o = SahteOrtam(c, t)
        o.hakem_var = not hakemsiz
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

    def enkoder_duruyor(self, bas=0, sonra_ms=None, en_az=2):
        """gelen[bas:] içinde (ms > sonra_ms olan) odo mesajları en az `en_az` tane ve hepsi aynı tik mi?"""
        odo = [m for m in self.esp.mesajlar("odo", bas) if sonra_ms is None or m["ms"] > sonra_ms]
        self.assertGreaterEqual(len(odo), en_az, "yeterli odo yok")
        return len({(m["sol"], m["sag"]) for m in odo}) == 1

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
