"""Keşif beyni birim + uçtan uca sınamaları (unittest; pytest gerekmez).

    cd kod/fizik && py -3 -m unittest kesif.testler.test_kesif -v
"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kesif import _yol  # noqa: E402,F401
from kesif.benzet2b import Dunya2B  # noqa: E402
from kesif.eslestir import eslestir  # noqa: E402
from kesif.izgara import Izgara, UzaklikAlani  # noqa: E402
from kesif.planla import KabaHarita, PlanAyari, iki_katmanli_bfs, yol_cikar2  # noqa: E402
from kesif.sinir import SinirAyari, sinirlari_bul  # noqa: E402


def _oda(duvarlar):
    """duvarlar: [(x1, y1, x2, y2)] -> Dunya2B için harita sözlüğü."""
    return {"ad": "sinama", "boyut_m": [20, 20], "cevre_duvari": False, "engeller": [],
            "duvarlar": [list(d) for d in duvarlar]}


KUTU = [(-2, -1.5, 3, -1.5), (3, -1.5, 3, 1.5), (3, 1.5, -2, 1.5), (-2, 1.5, -2, -1.5), (0.5, -1.5, 0.5, -0.4),
        (1.5, 1.5, 1.5, 0.6)]


def _tara(dunya, poz, n=500, gurultu=0.005, rng=None):
    rng = rng or np.random.default_rng(0)
    ac = -math.pi + np.arange(n) * 2 * math.pi / n
    x, y, th = poz
    ox, oy = x + 0.19 * math.cos(th), y + 0.19 * math.sin(th)
    m = dunya.isinlar(np.full(n, ox), np.full(n, oy), th + ac)
    m = m + rng.normal(0, gurultu, n)
    m[~np.isfinite(m) | (m > 12)] = np.nan
    return ac, m


def _yaz(g, poz, ac, m):
    ok = np.isfinite(m)
    x, y, th = poz
    ox, oy = x + 0.19 * math.cos(th), y + 0.19 * math.sin(th)
    g.isin_yaz(ox, oy, ox + m[ok] * np.cos(th + ac[ok]), oy + m[ok] * np.sin(th + ac[ok]), np.ones(ok.sum(), bool))


class IzgaraSinama(unittest.TestCase):
    def test_isin_dolu_bos_bilinmeyen(self):
        g = Izgara()
        for _ in range(3):
            g.isin_yaz(0.0, 0.0, np.array([2.0]), np.array([0.0]), np.array([True]))
        i, j = g.hucre(np.array([2.0, 1.0, 3.0]), np.array([0.0, 0.0, 0.0]))
        self.assertTrue(g.dolu()[i[0], j[0]])
        self.assertTrue(g.bos()[i[1], j[1]])
        self.assertTrue(g.bilinmeyen()[i[2], j[2]])

    def test_buyume(self):
        g = Izgara(boyut_m=4.0)
        g.isin_yaz(0.0, 0.0, np.array([6.0]), np.array([0.0]), np.array([True]))
        i, j = g.hucre(np.array([6.0]), np.array([0.0]))
        self.assertTrue(g.dolu()[i[0], j[0]])


class EslestirmeSinama(unittest.TestCase):
    def test_bilinen_kaydirmayi_bulur(self):
        d = Dunya2B(_oda(KUTU))
        g = Izgara()
        poz = (0.0, 0.0, 0.0)
        rng = np.random.default_rng(1)
        for _ in range(5):
            _yaz(g, poz, *_tara(d, poz, rng=rng))
        alan = UzaklikAlani(g, 0.0, 0.0, 8.0, 0.3)
        ac, m = _tara(d, poz, rng=rng)
        ok = np.isfinite(m)
        bx, by = 0.19 + m[ok] * np.cos(ac[ok]), m[ok] * np.sin(ac[ok])
        om = np.diag([1 / 0.2 ** 2, 1 / 0.2 ** 2, 1 / 0.2 ** 2])
        for off in [(0.08, -0.05, 0.04), (-0.10, 0.06, -0.05)]:
            r = eslestir(alan, bx, by, off, om)
            self.assertLess(math.hypot(r.poz[0], r.poz[1]), 0.02, (off, r.poz))
            self.assertLess(abs(r.poz[2]), math.radians(0.6), (off, r.poz))
            self.assertGreater(r.kalite, 0.8)


def _koridor_izgara(genislik):
    """x boyunca 4 m koridor, uçta (x > 3) bilinmeyen."""
    g = Izgara()
    xs = np.arange(-0.5, 3.0, 0.025)
    for y in np.arange(-genislik / 2 + 0.05, genislik / 2 - 0.04, 0.025):
        g.bos_yaz(xs, np.full(xs.size, y))
    for _ in range(4):
        for yw in (-genislik / 2, genislik / 2):
            g.isin_yaz(0.0, 0.0, xs, np.full(xs.size, yw), np.ones(xs.size, bool))
    g.isin_yaz(0.0, 0.0, np.full(30, -0.55), np.linspace(-genislik / 2, genislik / 2, 30), np.ones(30, bool))
    return g


class PlanSinirSinama(unittest.TestCase):
    def test_genis_koridor_sinir_ve_yol(self):
        g = _koridor_izgara(1.3)
        kh = KabaHarita(g, PlanAyari())
        dist, d_iyi, d_min = iki_katmanli_bfs(kh, 0.0, 0.0)
        sn = sinirlari_bul(kh, dist, (0.0, 0.0, 0.0), SinirAyari())
        self.assertTrue(sn, "koridor ucunda sınır bulunmalı")
        s = min(sn, key=lambda s: s.maliyet)
        self.assertGreater(s.merkez[0], 2.5)
        yol = yol_cikar2(kh, d_iyi, d_min, s.bakis)
        self.assertTrue(yol)
        for p in yol:
            self.assertLess(abs(p[1]), 0.2, "yol koridor ortasında kalmalı")

    def test_dar_koridor_gecilmez(self):
        g = _koridor_izgara(0.60)       # robot 0,52 m + pay: geçilmez
        kh = KabaHarita(g, PlanAyari())
        dist, d_iyi, d_min = iki_katmanli_bfs(kh, 0.0, 0.0)
        i, j = kh.hucre(2.5, 0.0)
        self.assertLess(dist[int(i), int(j)], 0, "0,60 m koridor C-uzayında kapalı olmalı")


class StartKorumaSinama(unittest.TestCase):
    def test_start_yasak_ve_filtre(self):
        from kesif.beyin import KesifBeyni
        b = KesifBeyni()
        g = b.slam.izgara
        i, j = g.hucre(np.array([-1.0]), np.array([0.0]))
        self.assertTrue(g.yasak[i[0], j[0]], "START gerisi yasak olmalı")
        # çizgiye 0,33 m'de (gövde merkezi) geri komut kesilir (0,3 s öngörü 0,30 m eşiğini aşar), ileri geçer
        self.assertEqual(b._start_filtre((-0.12, 0.0, 0.0), -0.2, 0.0), (0.0, 0.0))
        self.assertEqual(b._start_filtre((-0.12, 0.0, 0.0), 0.2, 0.0), (0.2, 0.0))
        # yerinde dönüş (dingil çevresinde gövde merkezi en çok ~0,08 m yaklaşır) kesilmez
        self.assertEqual(b._start_filtre((0.0, 0.0, 0.0), 0.0, 0.8), (0.0, 0.8))


class UctanUcaSinama(unittest.TestCase):
    def test_5x5_basari(self):
        from kesif.benzet2b import Benzetici, BenzetimAyari
        from kesif.beyin import olustur
        from kesif.sahne import sahne_yukle
        s = sahne_yukle("labirent_5x5_t1")
        b = olustur("labirent_5x5_t1")
        r = Benzetici(s, b, BenzetimAyari(sure_siniri_s=300.0, tohum=0)).kos()
        self.assertEqual(r["durum"], "basari", r)
        self.assertLess(r["sure_s"], 200.0)
        self.assertLess(r["tarama_ms_ort"], 50.0)


class SurumSinama(unittest.TestCase):
    def test_v1_varsayilan_v2_hiz_profili(self):
        from kesif.beyin import BeyinAyari, surum_ayari
        self.assertEqual(surum_ayari("v1"), BeyinAyari())
        self.assertTrue(surum_ayari("v2").hiz_profili)
        with self.assertRaises(ValueError):
            surum_ayari("v9")

    def test_v2_5x5_basari_carpmasiz(self):
        from kesif.benzet2b import Benzetici, BenzetimAyari
        from kesif.beyin import olustur, surum_ayari
        from kesif.sahne import sahne_yukle
        s = sahne_yukle("labirent_5x5_t1")
        b = olustur("labirent_5x5_t1", ayar=surum_ayari("v2"))
        r = Benzetici(s, b, BenzetimAyari(sure_siniri_s=300.0, tohum=0)).kos()
        self.assertEqual(r["durum"], "basari", r)
        self.assertEqual(int(r.get("carpma_sayisi") or 0), 0, r)
        self.assertGreater(b.sayac.get("hizli", 0), 0)

    def test_v3_disa_acik_sinir_oncelikli_ve_hatirlanir(self):
        from kesif.beyin import KesifBeyni, surum_ayari
        from kesif.sinir import Sinir
        self.assertEqual(surum_ayari("v2").disa_acik_bonus_m, 0.0)

        def sn(x, y, dis, m):
            return Sinir(hucreler=np.zeros((1, 2), int), merkez=(x, y), boy_m=1.0, dis=dis, bakis=(0, 0),
                         bakis_xy=(x, y), d_yol_m=m, maliyet=m)
        b = KesifBeyni(ayar=surum_ayari("v3"))
        yakin, acik = sn(1.0, 0.0, 0.0, 0.3), sn(5.0, 5.0, 1.0, 3.1)
        b._disa_acik_uygula([yakin, acik], {})
        self.assertLess(acik.maliyet, yakin.maliyet)       # 17x17_t3 durumu: açık sınır yakın sınırı geçer
        self.assertEqual(yakin.maliyet, 0.3)
        # dis titrese de (0) hatırlanan yerdeki sınır önceliğini korur
        tekrar = sn(5.5, 5.2, 0.0, 10.0)
        b._disa_acik_uygula([tekrar], {})
        self.assertAlmostEqual(tekrar.maliyet, 10.0 - b.ayar.disa_acik_bonus_m)


if __name__ == "__main__":
    unittest.main()
