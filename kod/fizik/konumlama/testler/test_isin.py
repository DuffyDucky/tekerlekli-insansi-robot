"""Işın izleme, uzaklık alanı ve tarama sözleşmesi: analitik sonuçlarla karşılaştırma."""

import importlib.util
import math
import os
import unittest

import numpy as np

from . import FIZIK  # noqa: F401  (yol)
from konumlama import Harita2B, LidarOzellik, harita_yukle, sentetik_tarama, tarama_hazirla

KOD = os.path.dirname(FIZIK)


def _eski_harita_modulu():
    """`kod/araclar/sahte_esp32/harita.py` (salt okunur; paketin __init__'ini çalıştırmadan)."""
    yol = os.path.join(KOD, "araclar", "sahte_esp32", "harita.py")
    spec = importlib.util.spec_from_file_location("_eski_harita", yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class IsinIzleme(unittest.TestCase):
    def test_kare_oda_analitik(self):
        """Dayanak: 4 x 4 m oda, (1, 1)'den her yöne ışın: en yakın duvara düz geometri."""
        h = Harita2B({"boyut_m": [4, 4]}, ad="kare")
        acilar = np.linspace(-math.pi, math.pi, 721, endpoint=False)
        d = h.isin_izle(np.array([1.0]), np.array([1.0]), acilar[None, :])[0]
        beklenen = []
        for a in acilar:
            c, s = math.cos(a), math.sin(a)
            ts = []
            if c > 1e-12: ts.append((4 - 1) / c)
            if c < -1e-12: ts.append((0 - 1) / c)
            if s > 1e-12: ts.append((4 - 1) / s)
            if s < -1e-12: ts.append((0 - 1) / s)
            beklenen.append(min(ts))
        np.testing.assert_allclose(d, beklenen, rtol=0, atol=1e-9)
        self.assertAlmostEqual(float(h.isin_izle([1.0], [1.0], [[math.pi / 4]])[0, 0]), 3 * math.sqrt(2), places=9)

    def test_daire_analitik(self):
        """Dayanak: r = 1 daire (5, 0)'da; (0, 0)'dan alfa açılı ışın t = 5 cos a - sqrt(1 - 25 sin^2 a)."""
        h = Harita2B({"boyut_m": [20, 20], "cevre_duvari": False,
                      "engeller": [{"tur": "daire", "x": 5, "y": 0, "r": 1}]})
        sinir = math.asin(1 / 5)
        acilar = np.linspace(-sinir * 0.999, sinir * 0.999, 101)
        d = h.isin_izle(np.array([0.0]), np.array([0.0]), acilar[None, :])[0]
        beklenen = 5 * np.cos(acilar) - np.sqrt(1 - 25 * np.sin(acilar) ** 2)
        np.testing.assert_allclose(d, beklenen, atol=1e-9)
        # teğetin dışı ve arkaya bakan ışın: yüzey yok
        disari = h.isin_izle([0.0], [0.0], [[sinir * 1.01, math.pi]])[0]
        self.assertTrue(np.all(np.isinf(disari)))

    def test_kutu_ve_menzil(self):
        """Dayanak: kutu kenarına dik ışın; menzil dışı = inf."""
        h = Harita2B({"boyut_m": [30, 30], "cevre_duvari": False,
                      "engeller": [{"tur": "kutu", "x": 3, "y": -1, "g": 1, "d": 2}]})
        self.assertAlmostEqual(float(h.isin_izle([0.0], [0.0], [[0.0]])[0, 0]), 3.0, places=12)
        self.assertTrue(np.isinf(h.isin_izle([0.0], [0.0], [[0.0]], menzil=2.5)[0, 0]))
        self.assertTrue(np.isinf(h.isin_izle([0.0], [0.0], [[math.pi]])[0, 0]))

    def test_eski_harita_ile_ayni(self):
        """Dayanak: sahte ESP32'nin skaler ışın izlemesiyle (kod/araclar/sahte_esp32/harita.py) mevcut 3 haritada,
        rastgele 2000 ışında fark < 1e-9 m."""
        eski = _eski_harita_modulu()
        rng = np.random.default_rng(3)
        for ad in ("oda_engelli", "oda_bos", "acik_alan"):
            yeni = harita_yukle(ad)
            e = eski.Harita.dosyadan(ad)
            x, y, _ = yeni.rastgele_serbest(200, rng)
            a = rng.uniform(-math.pi, math.pi, (200, 10))
            d = yeni.isin_izle(x, y, a, menzil=25.0)
            for i in range(200):
                for j in range(10):
                    r = e.isin(float(x[i]), float(y[i]), float(a[i, j]), 25.0)
                    if r is None:
                        self.assertTrue(np.isinf(d[i, j]), (ad, i, j))
                    else:
                        self.assertAlmostEqual(float(d[i, j]), r[0], delta=1e-9, msg=(ad, i, j))


class UzaklikAlani(unittest.TestCase):
    def test_uzaklik_ve_serbest(self):
        """Dayanak: boş 6 x 5 oda: hücre uzaklığı = en yakın duvar; serbest alan = pay dışı iç bölge."""
        h = harita_yukle("oda_bos")
        g = h.hazirla(0.05, 0.20)
        xs = g["x0"] + (np.arange(g["nx"]) + 0.5) * 0.05
        ys = g["y0"] + (np.arange(g["ny"]) + 0.5) * 0.05
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        ic = (X > 0) & (X < 6) & (Y > 0) & (Y < 5)
        beklenen = np.minimum.reduce([X, 6 - X, Y, 5 - Y])
        np.testing.assert_allclose(g["uzaklik"][ic], beklenen[ic], atol=1e-5)
        alan = h.serbest_alan_m2()
        self.assertAlmostEqual(alan, (6 - 0.4) * (5 - 0.4), delta=0.3)

    def test_engel_ici_dolu(self):
        """Dayanak: kutu ve daire içi serbest değil, erişilebilir bölge başlangıçtan."""
        h = harita_yukle("oda_engelli")
        h.hazirla()
        self.assertFalse(h.serbest_mi(np.array([2.0]), np.array([4.6]))[0])    # masa içi
        self.assertFalse(h.serbest_mi(np.array([3.2]), np.array([1.4]))[0])    # kolon içi
        self.assertTrue(h.serbest_mi(np.array([1.5]), np.array([1.5]))[0])     # başlangıç
        self.assertTrue(h.serbest_mi(np.array([6.0]), np.array([2.8]))[0])     # kapının ötesi


class TaramaSozlesmesi(unittest.TestCase):
    def test_none_kor_sektor_montaj(self):
        """Dayanak: sözleşme {t, acilar, mesafeler}; None = dönüş yok; kör sektör atılır; montaj ofseti uygulanır."""
        oz = LidarOzellik.gecici(montaj_x_m=0.10, kor_sektorler_derece=[[150, -150]])
        h = harita_yukle("oda_bos")
        tar = sentetik_tarama(h, (3.0, 2.5, 0.0), oz)        # gürültüsüz
        self.assertEqual(len(tar["acilar"]), 500)
        ileri = int(np.argmin(np.abs(np.array(tar["acilar"]))))
        self.assertAlmostEqual(tar["mesafeler"][ileri], 6.0 - 3.0 - 0.10, places=6)
        geri = int(np.argmin(np.abs(np.abs(np.array(tar["acilar"])) - math.pi)))
        self.assertIsNone(tar["mesafeler"][geri])            # kör sektör
        hz = tarama_hazirla(tar, oz)
        self.assertEqual(hz.acilar.size, 500 - sum(oz.kor_mu(np.array(tar["acilar"]))))
        self.assertFalse(np.any(np.abs(np.abs(hz.acilar) - math.pi) < math.radians(29)))
        # menzil dışı -> None
        acik = harita_yukle("acik_alan")
        t2 = sentetik_tarama(acik, (15.0, 15.0, 0.0), oz)
        n_none = sum(v is None for v in t2["mesafeler"])
        self.assertGreater(n_none, 300)

    def test_nan_ve_alt_ornekleme(self):
        """Dayanak: NaN da None gibi; menzil_min altı geçersiz; isin_sayisi eşit aralıklı seçer."""
        oz = LidarOzellik.gecici()
        tar = {"t": 1.0, "acilar": [0.0, 0.5, 1.0, 1.5], "mesafeler": [float("nan"), 0.05, 2.0, None]}
        hz = tarama_hazirla(tar, oz)
        self.assertEqual(int(hz.isabet.sum()), 1)
        tam = sentetik_tarama(harita_yukle("oda_bos"), (3, 2.5, 0), oz)
        self.assertEqual(tarama_hazirla(tam, oz, isin_sayisi=60).acilar.size, 60)

    def test_ozellik_sozlukten(self):
        """Dayanak: lidar_ozellik.json alanları (montaj sözlük, gürültü sayı ya da sözlük)."""
        oz = LidarOzellik.sozlukten({"menzil_min_m": 0.1, "menzil_maks_m": 8, "acisal_cozunurluk_derece": 1.0,
                                     "tarama_hz": 5, "mesafe_gurultu": {"std_m": 0.02},
                                     "montaj": {"x_m": 0.1, "y_m": 0.0, "yaw": 0.0},
                                     "kor_sektorler_derece": [[170, 190]]})
        self.assertEqual(oz.menzil_maks_m, 8.0)
        self.assertEqual(oz.mesafe_gurultu_std_m, 0.02)
        self.assertEqual(oz.isin_acilari().size, 360)
        self.assertTrue(oz.kor_mu(np.array([math.pi]))[0])
        self.assertFalse(oz.kor_mu(np.array([0.0]))[0])


if __name__ == "__main__":
    unittest.main()
