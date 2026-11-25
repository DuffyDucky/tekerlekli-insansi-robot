"""Taşınma deneyinin birim testleri (sistem Python'u, numpy; MuJoCo gerekmez; ≈ 10 s).

    py -3 -m unittest discover -s kod/fizik/deneyler/tasinma/testler -v"""

import math
import os
import random
import sys
import unittest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
import kacirma as KC  # noqa: E402
import algi as AL  # noqa: E402

import numpy as np  # noqa: E402


def _tarama(kor, poz, tohum=0):
    from gezinme.beyinler import haritalar
    from konumlama import LidarOzellik
    from konumlama.tarama import sentetik_tarama
    h = haritalar([kor])[0]
    return sentetik_tarama(h, poz, LidarOzellik.varsa_dosyadan(), rng=np.random.default_rng(tohum))


class TestAlgi(unittest.TestCase):
    def test_dogru_pozda_iyi_yanlista_kotu(self):
        from gezinme.beyinler import haritalar
        h5, h2 = haritalar(["koridor_5"])[0], haritalar(["koridor_2"])[0]
        a = AL.TasinmaAlgisi()
        poz = (8.0, 6.2, 0.0)
        u, g, n = a.olc(h5, poz, _tarama("koridor_5", poz))
        self.assertGreater(u, 0.9)
        self.assertLess(g, 0.05)
        self.assertGreater(n, 50)
        # koridor_2'deki gerçek tarama, koridor_5 haritasında okunursa uyum düşer
        u2, g2, _ = a.olc(h5, poz, _tarama("koridor_2", (5.0, 6.75, 0.0)))
        self.assertLess(u2, a.uyum_esik)
        del h2

    def test_pencere_ve_sicrama(self):
        from gezinme.beyinler import haritalar
        h5 = haritalar(["koridor_5"])[0]
        a = AL.TasinmaAlgisi()
        poz = (8.0, 6.2, 0.0)
        iyi = _tarama("koridor_5", poz)
        kotu = _tarama("koridor_2", (5.0, 6.75, 0.0))
        for _ in range(12):
            self.assertEqual(a.guncelle(h5, poz, iyi), "iyi")
        durumlar = [a.guncelle(h5, poz, kotu) for _ in range(8)]
        self.assertEqual(durumlar[2], "suphe")            # 3 kötü
        self.assertEqual(durumlar[-1], "kayip")           # 10'da 8 kötü
        a.sifirla()
        self.assertEqual(a.guncelle(h5, poz, iyi, sicrama_m=1.5), "kayip")
        a.sifirla()
        self.assertEqual(a.guncelle(h5, poz, iyi, sicrama_m=0.4), "iyi")
        # konum_kararsiz kötü sayılır
        a.sifirla()
        d = [a.guncelle(h5, poz, iyi, kararsiz=True) for _ in range(10)]
        self.assertEqual(d[-1], "kayip")


class TestTasimaPozu(unittest.TestCase):
    def test_turler(self):
        from gezinme.beyinler import haritalar
        simdi = (8.0, 6.2, 0.0)
        veri = KC.HO.harita_oku("koridor_5")
        for tur in KC.TURLER:
            k1, p1 = KC.tasima_pozu(tur, "koridor_5", simdi, random.Random(5), dunya_veri=veri)
            k2, p2 = KC.tasima_pozu(tur, "koridor_5", simdi, random.Random(5), dunya_veri=veri)
            self.assertEqual((k1, p1), (k2, p2))           # belirlenimci
            h = haritalar([k1])[0]
            self.assertTrue(KC._gecerli(h, None, *p1) or tur == "ters180")
            d = math.hypot(p1[0] - simdi[0], p1[1] - simdi[1])
            if tur == "ayni_uzak":
                self.assertEqual(k1, "koridor_5")
                self.assertGreaterEqual(d, 5.0 - 1e-9)
            elif tur == "kucuk":
                self.assertTrue(0.9 <= d <= 3.3, d)
                self.assertLessEqual(abs(KC.HO_sar(p1[2] - simdi[2])), math.radians(15.0) + 1e-9)
            elif tur == "ters180":
                self.assertAlmostEqual(abs(KC.HO_sar(p1[2] - simdi[2])), math.pi, places=6)
                self.assertLess(d, 1e-9)
            else:
                self.assertNotEqual(k1, "koridor_5")


class _Kaydeden:
    """Yalnız sabit komut veren, artımları biriktiren beyin (yer gerçeğini görmez)."""

    def __init__(self):
        self.top = 0.0
        self.poz = (0.0, 0.0, 0.0)
        self.tah = None
        self.k = None

    def adim(self, t, tarama, artim):
        self.top += artim[0]
        return 0.20, 0.0

    def durum(self):
        return {"mod": "izle"}


class TestKacirici(unittest.TestCase):
    def test_tasima_odometriye_yansimaz(self):
        from benzet2b import Benzet2B
        import kos_tasinma as KT
        dn = KC.HO.dunya_kur("koridor_5", {}, np.random.default_rng(0))
        b = _Kaydeden()
        hakem = KT.TasinmaHakemi((100.0, 100.0), son_t=8.0)
        kc = KT.Kacirici(b, "ab", "koridor_5", "kucuk", random.Random(3), 0.5, hakem, 10.0, dn["veri"])
        kc.hedef_tam = "k5_kapi_3"
        b.koridor = "koridor_5"
        bz = Benzet2B(dn, kc, (4.0, 6.2, 0.0), 1, {})
        kc.bz = bz
        bz.kos(8.0, hakem=hakem)
        self.assertIsNotNone(kc.tasima)
        sicrama = kc.tasima["uzaklik"]
        self.assertGreater(sicrama, 0.9)
        # odometri artımlarının toplamı sürülen yola eşit (taşıma sıçraması yok): yer gerçeği yolu sıçramasız sayılır
        self.assertLess(abs(b.top - kc.yol), 0.15)
        self.assertLess(b.top, 0.20 * 8.0 + 0.05)


class TestSarmalayici(unittest.TestCase):
    def test_iyi_taramada_komut_aynen(self):
        class Ic:
            koridor = "koridor_5"
            poz = (8.0, 6.2, 0.0)

            class _T:
                konum_kararsiz = False
                kararsiz = False
            tah = _T()
            k = None

            class izleyici:
                class ayar:
                    dt_s = 0.05

            def adim(self, t, tarama, artim):
                return 0.25, 0.1

            def durum(self):
                return {"mod": "izle"}
        tb = AL.TasinmaBeyni(Ic(), ["koridor_5"], "k5_kapi_3", 1)
        tar = _tarama("koridor_5", (8.0, 6.2, 0.0))
        for i in range(15):
            self.assertEqual(tb.adim(0.1 * i, tar, (0.0, 0.0, 0.0)), (0.25, 0.1))
        self.assertEqual(tb.kurtarma, 0)


if __name__ == "__main__":
    unittest.main()
