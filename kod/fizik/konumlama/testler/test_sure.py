"""Süre: 6 harita, bir güncellemenin (hareket + tarama + gerekirse yeniden örnekleme + tahmin) bu makinede kaç ms
sürdüğü. Harita seti: `kod/araclar/haritalar/koridor_1..6` varsa onlar (deneyin seti), yoksa 3 mevcut oda + 3
sentetik koridor. Tarama üretimi süreye dahil değil."""

import os
import platform
import time
import unittest

import numpy as np

from . import FIZIK  # noqa: F401
from .ortak import kaydet, koridor
from konumlama import CokHaritaliMCL, LidarOzellik, OlcumParametreleri, harita_yukle, sentetik_tarama
from konumlama.benzet import goreli, yol_uret
from konumlama.harita2b import HARITA_KLASORU

OZ = LidarOzellik.gecici()
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
YEDEK = ["oda_engelli", "oda_bos", "acik_alan",
         koridor("koridor_A", kapilar=[(4, "alt", 0.9), (10, "ust", 0.9), (17, "alt", 0.9)]),
         koridor("koridor_B", kapilar=[(4, "alt", 0.9), (10, "ust", 0.9), (17, "ust", 0.9)]),
         koridor("koridor_C", uzunluk=30.0, genislik=3.0, kapilar=[(5, "alt", 1.2), (12, "ust", 0.9), (25, "alt", 0.9)],
                 engeller=[{"tur": "kutu", "x": 8, "y": 0.9, "g": 0.6, "d": 0.4},
                           {"tur": "daire", "x": 20, "y": 3.4, "r": 0.2}])]


def harita_seti():
    if all(os.path.exists(os.path.join(HARITA_KLASORU, k + ".json")) for k in KORIDORLAR):
        return "koridor_1..6", KORIDORLAR
    return "3 oda + 3 sentetik koridor", YEDEK


def olc(haritalar, N, model="alan", adim=30):
    p = OlcumParametreleri(model=model)
    mcl = CokHaritaliMCL(haritalar, ozellik=OZ, olcum=p, tohum=1, parcacik_sayisi=N)
    h = mcl.haritalar[-2]
    x0, y0, t0 = h.baslangic
    yol = yol_uret([(x0, y0), (x0 + 8.0, y0)], t0)
    rng = np.random.default_rng(2)
    taramalar = [sentetik_tarama(h, poz, OZ, rng) for poz in yol[:adim + 6]]
    t0 = time.perf_counter()
    mcl.guncelle(taramalar[0])
    ilk = time.perf_counter() - t0
    sureler = []
    for i in range(1, adim + 6):
        a = goreli(yol[i - 1], yol[i])
        t0 = time.perf_counter()
        mcl.guncelle(taramalar[i], artim=a)
        if i > 5:
            sureler.append(time.perf_counter() - t0)
    return ilk * 1e3, float(np.mean(sureler)) * 1e3, float(np.percentile(sureler, 95)) * 1e3, mcl, h.ad


class Sure(unittest.TestCase):
    def test_alti_harita_sure(self):
        """Dayanak: görev "süre" — 6 harita, 1500 / 3000 / 6000 parçacık ("alan"), 3000 ("isin")."""
        ad, haritalar = harita_seti()
        alan = sum(harita_yukle(h).hazirla().get("serbest_hucreler").size * 0.0025 for h in haritalar)
        kaydet("süre", "makine", "%s, %s, Python %s, numpy %s" % (platform.processor() or platform.machine(),
                                                                 platform.system(), platform.python_version(),
                                                                 np.__version__))
        kaydet("süre", "harita seti; toplam serbest alan", "%s; %.0f m2" % (ad, alan))
        for N, model in ((1500, "alan"), (3000, "alan"), (6000, "alan"), (3000, "isin")):
            ilk, ort, p95, mcl, dogru = olc(haritalar, N, model)
            kaydet("süre", "N=%d %s: ilk (kafes) / adım ort / adım p95 ms" % (N, model),
                   "%.0f / %.1f / %.1f" % (ilk, ort, p95))
            if N == 3000 and model == "alan":
                self.assertLess(ort, 100.0)       # 10 Hz taramaya yetişmeli (bu makinede)


if __name__ == "__main__":
    unittest.main()
