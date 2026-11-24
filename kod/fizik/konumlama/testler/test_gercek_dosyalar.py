"""Deneyin gerçek dosyalarıyla duman testi: `kod/fizik/lidar_ozellik.json` + `kod/araclar/haritalar/koridor_1..6`.
Dosyalar yoksa (başka ajan henüz yazmadıysa) atlanır. Bu dosyalar değişebilir: iddialar bilerek gevşek, yalnız
"kendinden emin yanlış karar yok" özelliğini sınar."""

import math
import os
import unittest

import numpy as np

from . import FIZIK  # noqa: F401
from .ortak import kaydet
from konumlama import CokHaritaliMCL, LidarOzellik, harita_yukle, karar_ani
from konumlama.benzet import konum_hatasi, yol_boyunca, yol_uret
from konumlama.harita2b import HARITA_KLASORU
from konumlama.tarama import OZELLIK_DOSYASI

KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
VAR = os.path.exists(OZELLIK_DOSYASI) and all(
    os.path.exists(os.path.join(HARITA_KLASORU, k + ".json")) for k in KORIDORLAR)


@unittest.skipUnless(VAR, "lidar_ozellik.json ya da koridor_1..6 yok")
class GercekDosyalar(unittest.TestCase):
    def test_ozellik_okunur(self):
        """Dayanak: sensör ajanının lidar_ozellik.json'u ayrıştırılır (montaj, kör sektör, gürültü)."""
        oz = LidarOzellik.dosyadan()
        kaydet("lidar_ozellik.json", "menzil / çözünürlük / montaj x / kör sektör / gürültü std",
               "%.2f-%.1f m / %.2f° / %.3f m / %s / %.3f m" % (oz.menzil_min_m, oz.menzil_maks_m,
                                                              oz.acisal_cozunurluk_derece, oz.montaj_x_m,
                                                              oz.kor_sektorler_derece, oz.mesafe_gurultu_std_m))
        self.assertGreater(oz.menzil_maks_m, oz.menzil_min_m)
        self.assertGreater(oz.isin_acilari().size, 100)

    def test_benzer_cift_kendinden_emin_yanlis_yok(self):
        """Dayanak: koridor_5'te (benzer çiftin biri) başlangıçtan +x yönünde 12 m: hiçbir adımda yanlış haritaya
        kesin karar ya da 0,5 m'den büyük hatayla kesin konum yok."""
        oz = LidarOzellik.dosyadan()
        dogru = "koridor_5"
        mcl = CokHaritaliMCL(KORIDORLAR, ozellik=oz, tohum=1)
        h = mcl.haritalar[mcl.adlar.index(dogru)]
        x0, y0, t0 = h.baslangic
        yol = yol_uret([(x0, y0), (x0 + 12.0 * math.cos(t0), y0 + 12.0 * math.sin(t0))], t0)
        xs = np.array([p[0] for p in yol])
        ys = np.array([p[1] for p in yol])
        if not h.serbest_mi(xs, ys).all():
            self.skipTest("koridor_5 değişmiş: başlangıçtan 12 m düz yol serbest değil")
        s = yol_boyunca(mcl, h, yol, oz, np.random.default_rng(3))
        yanlis_harita = sum(1 for _, t in s if not t.kararsiz and t.en_olasi != dogru)
        yanlis_konum = sum(1 for p, t in s if t.en_olasi == dogru and not t.konum_kararsiz
                           and konum_hatasi(t, p)[0] > 0.5)
        k = karar_ani(mcl.gecmis, dogru)
        kaydet("koridor_5 (gerçek)", "karar yolu m; kendinden emin yanlış harita / konum adımı",
               "%s; %d / %d (%d adım)" % ("%.2f" % k["gidilen_yol_m"] if k else "karar yok", yanlis_harita,
                                          yanlis_konum, len(s)))
        self.assertEqual(yanlis_harita, 0)
        self.assertEqual(yanlis_konum, 0)


if __name__ == "__main__":
    unittest.main()
