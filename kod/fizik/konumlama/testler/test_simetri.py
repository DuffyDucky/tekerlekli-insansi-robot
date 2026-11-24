"""Simetri / benzerlik farkındalığı: tam simetrik ortamda ve özdeş haritalarda filtre yanlış bir kesinliğe varmamalı."""

import math
import unittest

import numpy as np

from . import FIZIK  # noqa: F401
from .ortak import kaydet, kare_oda
from konumlama import CokHaritaliMCL, LidarOzellik, harita_yukle
from konumlama.benzet import yol_boyunca, yol_uret

OZ = LidarOzellik.gecici()


class Simetri(unittest.TestCase):
    def test_kare_oda_dort_mod(self):
        """Dayanak: boş 5 x 5 kare oda 90° dönme simetrik: hiçbir adımda konum kesin sayılmamalı; sonda en az iki
        mod (pay >= 0,1) yaşamalı ve gerçek poz modlardan birinde olmalı."""
        mcl = CokHaritaliMCL([kare_oda()], ozellik=OZ, tohum=1)
        h = mcl.haritalar[0]
        yol = yol_uret([(2.5, 2.5), (3.5, 2.5), (3.5, 3.5), (1.5, 3.5), (1.5, 1.5), (3.0, 1.5)], 0.3)
        s = yol_boyunca(mcl, h, yol, OZ, np.random.default_rng(2))
        self.assertTrue(all(t.konum_kararsiz for _, t in s))
        poz, son = s[-1]
        guclu = [m for m in son.modlar if m["pay"] >= 0.1]
        yakin = [m for m in son.modlar if m["pay"] >= 0.05 and math.hypot(m["x"] - poz[0], m["y"] - poz[1]) < 0.25
                 and abs((m["theta"] - poz[2] + math.pi) % (2 * math.pi) - math.pi) < math.radians(10)]
        kaydet("kare oda", "son mod payları", ", ".join("%.2f" % m["pay"] for m in son.modlar))
        kaydet("kare oda", "en büyük konum_payi (tüm adımlar)", "%.2f" % max(t.konum_payi for _, t in s))
        self.assertGreaterEqual(len(guclu), 2)
        self.assertTrue(yakin)

    def test_ikiz_haritalar_kararsiz(self):
        """Dayanak: iki özdeş harita (oda_bos'un iki kopyası): hiçbir adımda harita kararı verilmemeli."""
        a = dict(harita_yukle("oda_bos").veri)
        a["ad"] = "oda_a"
        b = dict(a)
        b["ad"] = "oda_b"
        mcl = CokHaritaliMCL([a, b], ozellik=OZ, tohum=3)
        h = mcl.haritalar[0]
        yol = yol_uret([(3.0, 2.5), (4.5, 2.5), (4.5, 3.8), (1.5, 3.8), (1.5, 1.2)], 0.0)
        s = yol_boyunca(mcl, h, yol, OZ, np.random.default_rng(4))
        farklar = [t.fark for _, t in s]
        kaydet("ikiz harita", "en büyük p1-p2 (tüm adımlar) / son", "%.3f / %.3f" % (max(farklar), farklar[-1]))
        self.assertTrue(all(t.kararsiz for _, t in s))
        self.assertLess(max(farklar), 0.5)


if __name__ == "__main__":
    unittest.main()
