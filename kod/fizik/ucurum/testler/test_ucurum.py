"""ucurum birim testleri. Saf testler bağımlılıksız (py -3); MuJoCo testleri sanal ortam yoksa atlanır.

    py -3 -m unittest discover -s kod/fizik/ucurum/testler -t kod/fizik
    %V% -m unittest discover -s kod/fizik/ucurum/testler -t kod/fizik
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucurum import _yol  # noqa: E402,F401
from ucurum import sahne as S  # noqa: E402
from ucurum import sensor as SN  # noqa: E402
from ucurum.denetci import DenetciAyar, UcurumDenetci  # noqa: E402

try:
    import mujoco  # noqa: F401
    MJ = True
except ImportError:
    MJ = False


def _kalibre(d, deger=0.063, n=25):
    for i in range(d.n):
        for _ in range(n):
            d.kalibrasyon_ornegi(i, deger)
    d.kalibre()


class TestDenetci(unittest.TestCase):
    def test_kalibrasyon_ortanca(self):
        d = UcurumDenetci(1)
        for v in (0.060, 0.065, 0.062, 0.200, 0.061):
            d.kalibrasyon_ornegi(0, v)
        self.assertAlmostEqual(d.kalibre()[0], 0.062)

    def test_onay_art_arda(self):
        d = UcurumDenetci(2, DenetciAyar(esik_m=0.04, onay=2))
        _kalibre(d)
        self.assertFalse(d.isle(0.00, 0, 0.30))       # 1. kanıt
        self.assertFalse(d.isle(0.02, 0, 0.064))      # zemin: sayaç sıfırlanır
        self.assertFalse(d.isle(0.04, 0, 0.30))
        self.assertFalse(d.isle(0.04, 1, 0.30))       # başka sensörün kanıtı ayrı sayılır
        self.assertTrue(d.isle(0.06, 0, 0.30))
        self.assertEqual((d.tetik_sensor, d.neden), (0, "sapma"))
        self.assertAlmostEqual(d.tetik_t, 0.06)

    def test_esik_alti_ve_yakin_tetiklemez(self):
        d = UcurumDenetci(1, DenetciAyar(esik_m=0.04, onay=1))
        _kalibre(d)
        for k in range(10):
            d.isle(k * 0.02, 0, 0.063 + 0.039)          # eşiğin hemen altı
            d.isle(k * 0.02, 0, 0.040)                  # yakın (eşik, halı): uçurum değil
        self.assertFalse(d.tetik)

    def test_none_politikalari(self):
        for pol, beklenen in (("ucurum", True), ("yok_say", False)):
            d = UcurumDenetci(1, DenetciAyar(onay=2, politika=pol))
            _kalibre(d)
            d.isle(0.0, 0, None)
            d.isle(0.02, 0, None)
            self.assertEqual(d.tetik, beklenen, pol)
        d = UcurumDenetci(1, DenetciAyar(onay=2, politika="yavasla", yavas_yok_n=5, yavas_hiz=0.1))
        _kalibre(d)
        for k in range(4):
            d.isle(k * 0.02, 0, None)
        self.assertFalse(d.tetik)
        self.assertEqual(d.hiz_siniri(0.1), 0.1)
        self.assertIsNone(d.hiz_siniri(0.7))
        d.isle(0.1, 0, None)
        self.assertTrue(d.tetik)

    def test_donuk_sensor_arizali(self):
        d = UcurumDenetci(1, DenetciAyar(onay=2, politika="ucurum", donuk_n=25))
        _kalibre(d)
        for k in range(30):
            d.isle(k * 0.02, 0, 0.063)                  # gürültüsüz sabit değer: donmuş çıktı
        self.assertTrue(d.arizali[0])
        self.assertTrue(d.tetik)                         # arızalı = veri yok = (bu politikada) dur
        d2 = UcurumDenetci(1, DenetciAyar(onay=2, politika="yok_say", donuk_n=25))
        _kalibre(d2)
        for k in range(30):
            d2.isle(k * 0.02, 0, 0.063)
        self.assertTrue(d2.arizali[0])
        self.assertFalse(d2.tetik)                       # yok_say: ölü sensör sessizce yok sayılır (zayıflık)

    def test_kalibrasyonsuz_sensor_arizali(self):
        d = UcurumDenetci(2)
        for _ in range(5):
            d.kalibrasyon_ornegi(0, 0.06)
        d.kalibre()
        self.assertEqual(d.arizali, [False, True])


class TestSensorSaf(unittest.TestCase):
    def test_obek_en_yakin_yeterli(self):
        # 13 ağırlık: 4 yakın (>= %25) -> yakın öbek
        h = [(0.06, 1.0)] * 4 + [(0.23, 1.0)] * 9
        self.assertAlmostEqual(SN.obek_degeri(h, 13.0), 0.06)
        h = [(0.06, 1.0)] * 3 + [(0.23, 1.0)] * 10      # 3 / 13 < %25 -> uzak öbek
        self.assertAlmostEqual(SN.obek_degeri(h, 13.0), 0.23)
        self.assertIsNone(SN.obek_degeri([(0.06, 1.0)] * 3, 13.0))   # sinyal yetersiz -> dönüş yok
        self.assertIsNone(SN.obek_degeri([], 13.0))

    def test_isin_sayisi_ve_koni(self):
        a = SN.SensorAyar("s", 0.25, 0, 0.06, egim_derece=15, yon_derece=0, koni_derece=27)
        L = a.isinlar()
        self.assertEqual(len(L), 17)
        d = a.eksen()
        for yon, _ in L:
            c = sum(x * y for x, y in zip(yon, d))
            self.assertLessEqual(math.degrees(math.acos(min(1.0, c))), 13.5 + 1e-6)
        self.assertGreater(d[0], 0.0)                     # öne yatık
        self.assertLess(d[2], 0.0)                        # aşağı bakar

    def test_yerlesimler_govdeye_sigar(self):
        # etek kutusu x +-0,2625 y +-0,26 z 0,035-0,265; teker kutusu (ön / arka) x |0,1225-0,2475| y |0,187-0,245| z 0-0,125
        for ad in ("2K", "2I", "3KO", "4O", "2K+2A", "3KO+2A", "2KD+2AD", "3KOD+2AD", "4OD+2AD"):
            for z in (0.06, 0.12):
                for s in SN.yerlesim(ad, z, 15):
                    self.assertLessEqual(abs(s.x), 0.2625 - 0.0075, (ad, s.ad))
                    self.assertLessEqual(abs(s.y), 0.26 - 0.01 + 1e-9, (ad, s.ad))
                    self.assertTrue(0.035 < s.z < 0.265)
                    icinde = (0.1225 - 0.005 <= abs(s.x) <= 0.2475 + 0.005) and (0.187 - 0.005 <= abs(s.y) <= 0.245 + 0.005 - 1e-9)
                    self.assertFalse(icinde, (ad, s.ad))

    def test_capraz_yerlesim_yonleri(self):
        L = {s.ad: s for s in SN.yerlesim("2KD+2AD", 0.06, 30)}
        self.assertEqual(len(L), 4)
        for ad, s in L.items():
            d = s.eksen()
            self.assertGreater(d[0] * (1 if s.x > 0 else -1), 0.0, ad)   # önde öne, arkada arkaya
            self.assertGreater(d[1] * (1 if s.y > 0 else -1), 0.0, ad)   # köşeden dışa
            self.assertLess(d[2], 0.0, ad)

    def test_orta_sensorlu_capraz_yerlesim(self):
        L = SN.yerlesim("3KOD+2AD", 0.12, 30)
        self.assertEqual([s.ad for s in L], ["on_sol", "on_orta", "on_sag", "arka_sol", "arka_sag"])
        yon = {s.ad: s.yon_derece for s in L}
        self.assertEqual((yon["on_sol"], yon["on_orta"], yon["on_sag"]), (45.0, 0.0, -45.0))   # orta düz öne
        self.assertEqual(len(SN.yerlesim("4OD+2AD", 0.12, 30)), 6)


class TestSahne(unittest.TestCase):
    def test_pay(self):
        self.assertAlmostEqual(S.pay([[1.0, 0.0, 16.0]], 15.9, 3.0), 0.1)
        self.assertAlmostEqual(S.pay([[1.0, 0.0, 16.0], [0.0, 1.0, 15.0]], 15.5, 14.8), 0.2)
        self.assertEqual(S.pay([], 1, 2), math.inf)

    def test_pay_dikdortgen_delik(self):
        k = [["dik", 16.0, 18.0, 14.75, 15.25]]
        self.assertAlmostEqual(S.pay(k, 15.9, 15.0), 0.1)            # önünde
        self.assertAlmostEqual(S.pay(k, 16.5, 15.35), 0.1)           # yanında (yan zeminde)
        self.assertAlmostEqual(S.pay(k, 16.05, 15.2), -0.05)         # içinde: en yakın kenara uzaklığın eksisi
        self.assertAlmostEqual(S.pay(k, 15.7, 15.65), 0.5)           # köşeden çapraz
        self.assertAlmostEqual(S.pay(k + [[1.0, 0.0, 15.95]], 15.9, 15.0), 0.05)

    def test_acik_sahnesi(self):
        u = S.al("acik_55")
        self.assertEqual(u["kenarlar"], [["dik", S.E, S.E + S.ACIK_L, S.Y0 - 0.275, S.Y0 + 0.275]])
        self.assertEqual(u["yaklasma"], [1.0, 0.0, S.E])
        yan = [k for k in u["kutular"] if k["ad"].startswith("zemin_yan")]
        for k in yan:                                                 # yan zemin üstü z = 0, açıklığın dibine dek iner
            self.assertAlmostEqual(k["pos"][2] + k["size"][2], 0.0)
            self.assertLess(k["pos"][2] - k["size"][2], -3.0)
        m = S.al("dar_merdiven_60")
        b = [k for k in m["kutular"] if k["ad"].startswith("zemin_basamak")]
        self.assertAlmostEqual(b[0]["pos"][2] + b[0]["size"][2], -0.18)
        self.assertAlmostEqual(2 * b[0]["size"][1], 0.60)
        for ad in S.DENETIM_SINAMA_YENI:
            self.assertEqual(S.al(ad)["tur"], "denetim")

    def test_merdiven_basamaklari(self):
        u = S.al("merdiven_17x30")
        b = [k for k in u["kutular"] if k["ad"].startswith("zemin_basamak")]
        self.assertEqual(len(b), 6)
        ust = [k["pos"][2] + k["size"][2] for k in b]
        for i, z in enumerate(ust):
            self.assertAlmostEqual(z, -(i + 1) * 0.17)
        self.assertAlmostEqual(b[0]["pos"][0] - b[0]["size"][0], S.E)

    def test_sarmalama_ucurumsuz_sahneyi_degistirmez(self):
        import dunya as D
        S.kur()
        sahne = D.sahne_oku("oda_rampa")
        s1 = D.sahne_xml(None, sahne)
        s2 = D.sahne_xml.asil(None, sahne)
        self.assertEqual(s1, s2)
        s3 = D.sahne_xml(None, S.sahne_sozlugu("merdiven_17x30"))
        self.assertNotIn('type="plane"', s3)
        self.assertIn("zemin_basamak_5", s3)


@unittest.skipUnless(MJ, "mujoco yok (sanal ortam)")
class TestFizik(unittest.TestCase):
    def test_kafa_kafaya_durur_kesmede_duser(self):
        from ucurum import kosu
        yer = SN.yerlesim("3KO", 0.06, 15)
        r = kosu.kos("merdiven_17x30", yer, DenetciAyar(fren="rampa", fren_ivme=2.0), dict(tur="ileri", aci=0, v=0.25), tohum=1)
        self.assertTrue(r["tetik"])
        self.assertFalse(r["dustu"])
        self.assertGreater(r["pay_min_cm"], 0.0)
        r = kosu.kos("merdiven_17x30", yer, DenetciAyar(fren="kes"), dict(tur="ileri", aci=0, v=0.39), tohum=1)
        self.assertTrue(r["tetik"])
        self.assertTrue(r["dustu"])                       # motor kesme (boşta kayma) 0,39 m/s'de yetmez

    def test_dar_aciklik_orta_sensor(self):
        """Robottan dar (0,5 m) açıklık, orta hattan kafa kafaya: dört köşe düzeni tetiklemez, ön ortalı düzen durur."""
        from ucurum import kosu
        ay = DenetciAyar(esik_m=0.10, onay=3, politika="yavasla", fren="rampa", fren_ivme=2.0)
        sen = dict(tur="ileri", aci=0, v=0.39, yanal=[0.0, 0.0])
        r = kosu.kos("acik_50", SN.yerlesim("2KD+2AD", 0.12, 30), ay, sen, tohum=1)
        self.assertTrue(r["dustu"])
        r = kosu.kos("acik_50", SN.yerlesim("3KOD+2AD", 0.12, 30), ay, sen, tohum=1)
        self.assertTrue(r["tetik"])
        self.assertFalse(r["dustu"])
        self.assertGreater(r["pay_min_cm"], 0.0)

    def test_denetcisiz_davranis_ayni(self):
        """Denetçi bağlı değilken UcurumEsp32 FizikEsp32 ile aynı yolu sürer (bit düzeyinde)."""
        from ucurum import kosu
        import varyantlar as VR
        from fizik_esp32 import FizikEsp32
        from sahte_esp32.harita import Harita
        from sahte_esp32.tasima import BellekTasima
        from lale_pi.istemci import Esp32Istemci
        S.kur()
        sz = S.sahne_sozlugu("duz", (12.0, 15.0, 0.0))
        out = []
        for C in (FizikEsp32, kosu.esp32_sinifi()):
            c = C(Harita.dosyadan(S.HARITA), konum=(12.0, 15.0, 0.0), sahne=sz, varyant=VR.al("ONERI"), sonar_acik=False)
            e = Esp32Istemci(BellekTasima(c))
            e.baglan()
            e.devreye_al_ve_bekle()
            e.sur_tut(0.3, 0.2, 1500)
            out.append(c.dunya.poz())
        self.assertEqual(out[0], out[1])


if __name__ == "__main__":
    unittest.main()
