"""Deneme zinciri sınamaları (kesif.deneme): harita taşıma, START'a sıfırlama, yeniden hizalama.

    cd kod/fizik && py -3 -m unittest kesif.testler.test_deneme -v
"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kesif import _yol  # noqa: E402,F401
from kesif.benzet2b import Dunya2B  # noqa: E402
from kesif.testler.test_kesif import KUTU, _oda  # noqa: E402


def _tarama(dunya, poz, rng, n=500):
    """Gövde merkezi pozunda (LiDAR x +0,19) anlık tarama; SLAM'in beklediği sözlük."""
    ac = -math.pi + np.arange(n) * 2 * math.pi / n
    x, y, th = poz
    ox, oy = x + 0.19 * math.cos(th), y + 0.19 * math.sin(th)
    m = dunya.isinlar(np.full(n, ox), np.full(n, oy), th + ac) + rng.normal(0, 0.005, n)
    m[~np.isfinite(m) | (m > 12)] = np.nan
    return {"t": 0.0, "acilar": ac, "mesafeler": m}


def _hizalama_hatasi(hizala, gercek):
    from kesif.deneme import HizalaliSLAM
    from kesif.robot import VARSAYILAN
    d = Dunya2B(_oda(KUTU))
    rng = np.random.default_rng(3)
    s = HizalaliSLAM(robot=VARSAYILAN)
    for _ in range(6):                         # 1. deneme: START'ta harita
        s.tarama_isle(_tarama(d, (0.0, 0.0, 0.0), rng), 0.0)
    # yeni deneme: beyin kural gereği (0, 0, 0) sanar, robot biraz şaşık konmuş
    s.poz = s.odo_poz = s._son_poz_tarama = (0.0, 0.0, 0.0)
    s.alan = None
    s.hizala_kalan = 2 if hizala else 0
    for _ in range(2):
        s.tarama_isle(_tarama(d, gercek, rng), 0.0)
    return math.hypot(s.poz[0] - gercek[0], s.poz[1] - gercek[1]), abs(s.poz[2] - gercek[2])


class HizalamaSinama(unittest.TestCase):
    def test_hizalama_yerlestirme_hatasini_giderir(self):
        for gercek in [(0.05, -0.04, math.radians(4.0)), (-0.06, 0.05, math.radians(-3.5))]:
            e, eth = _hizalama_hatasi(True, gercek)
            self.assertLess(e, 0.02, gercek)
            self.assertLess(eth, math.radians(0.5), gercek)

    def test_kapaliyken_hafif_slam_ile_ayni(self):
        from kesif.deneme import HizalaliSLAM
        from kesif.robot import VARSAYILAN
        from kesif.slam import HafifSLAM
        d = Dunya2B(_oda(KUTU))
        sonuc = []
        for sinif in (HafifSLAM, HizalaliSLAM):
            rng = np.random.default_rng(5)
            s = sinif(robot=VARSAYILAN)
            for k in range(5):
                s.odometri((0.02, 0.0, 0.01), 0.1 * k)
                s.tarama_isle(_tarama(d, (0.02 * k, 0.0, 0.01 * k), rng), 0.1 * k)
            sonuc.append((s.poz, s.izgara.L.copy()))
        self.assertEqual(sonuc[0][0], sonuc[1][0])
        self.assertTrue(np.array_equal(sonuc[0][1], sonuc[1][1]))

    def test_yerlestirme_hatasi_belirli_ve_kirpik(self):
        from kesif.deneme import yerlestirme_hatasi
        self.assertEqual(yerlestirme_hatasi("labirent_5x5_t1", 0, 1), (0.0, 0.0, 0.0))
        a = yerlestirme_hatasi("labirent_5x5_t1", 0, 2)
        self.assertEqual(a, yerlestirme_hatasi("labirent_5x5_t1", 0, 2))
        self.assertNotEqual(a, yerlestirme_hatasi("labirent_5x5_t1", 0, 3))
        for k in range(2, 40):
            dx, dy, dth = yerlestirme_hatasi("labirent_9x9_t1", k, k)
            self.assertLessEqual(max(abs(dx), abs(dy)), 0.06)
            self.assertLessEqual(abs(dth), math.radians(4.0) + 1e-12)


class ZincirSinama(unittest.TestCase):
    def test_5x5_basarisiz_deneme_haritasi_tasinir_ve_cozer(self):
        """1. deneme 35 s'de (kısa sınır) biter; 2. deneme haritayla START'tan başlar, START'tan çıkmaz, çözer."""
        from kesif.benzet2b import Benzetici, BenzetimAyari
        from kesif.beyin import olustur
        from kesif.deneme import bilinen_alan_m2, yeni_deneme, zincir_hazirla
        from kesif.sahne import sahne_yukle
        s = sahne_yukle("labirent_5x5_t1")
        b = olustur("labirent_5x5_t1")
        z = zincir_hazirla(b)
        sinir0 = b.ayar.sinir
        r1 = Benzetici(s, b, BenzetimAyari(sure_siniri_s=35.0, tohum=0)).kos()
        self.assertEqual(r1["durum"], "fail_sure", r1)
        L1 = b.slam.izgara.L.copy()
        alan1 = bilinen_alan_m2(b)
        k_don = b.slam.k_don
        b.kara_liste.append((1.0, 1.0, 30.0))
        yeni_deneme(b, z)
        self.assertEqual(b.slam.poz, (0.0, 0.0, 0.0))
        self.assertEqual((b.t, b.mod, b.yol, b.kara_liste), (0.0, "baslangic", [], []))
        self.assertTrue(np.array_equal(L1, b.slam.izgara.L), "harita korunmalı")
        self.assertEqual(b.slam.k_don, k_don)
        self.assertEqual(b.ayar.sinir, sinir0)
        self.assertEqual(b.slam.hizala_kalan, 2)
        self.assertGreater(alan1, 10.0)
        r2 = Benzetici(s, b, BenzetimAyari(sure_siniri_s=200.0, tohum=1)).kos()
        self.assertEqual(r2["durum"], "basari", r2)
        self.assertEqual(int(r2.get("carpma_sayisi") or 0), 0, r2)
        self.assertGreaterEqual(bilinen_alan_m2(b), alan1)
        self.assertIn((0.0, "deneme", 2), b.olaylar)


if __name__ == "__main__":
    unittest.main()
