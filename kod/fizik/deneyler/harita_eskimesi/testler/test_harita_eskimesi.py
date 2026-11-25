"""Bozucuların ve 2B benzeticinin birim testleri (sistem Python'u, numpy; MuJoCo gerekmez).

    py -3 -m unittest discover -s kod/fizik/deneyler/harita_eskimesi/testler -v"""

import math
import os
import sys
import unittest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
import ortak  # noqa: E402

import numpy as np  # noqa: E402


class TestDonusum(unittest.TestCase):
    def test_kimlik_ve_ters(self):
        for olcek, eg in ((0.0, 0.0), (0.03, 0.0), (0.0, 4.0), (0.02, 2.0)):
            T = ortak.Donusum((1.8, 6.2, 0.3), olcek=olcek, egrilme_der_20m=eg)
            for x, y in ((1.8, 6.2), (10.0, 7.0), (20.0, 5.0), (3.0, 9.0)):
                wx, wy = T.nokta(x, y)
                bx, by = T.ters_nokta(wx, wy)
                self.assertAlmostEqual(bx, x, places=9)
                self.assertAlmostEqual(by, y, places=9)
            # başlangıç sabit nokta
            self.assertAlmostEqual(T.nokta(1.8, 6.2)[0], 1.8, places=12)
            p = T.ters_poz(T.poz((12.0, 6.0, 0.5)))
            self.assertAlmostEqual(p[2], 0.5, places=9)

    def test_olcek_ve_egrilme_buyuklugu(self):
        T = ortak.Donusum((0.0, 0.0, 0.0), olcek=0.02)
        self.assertAlmostEqual(T.nokta(20.0, 0.0)[0], 20.4, places=9)
        T = ortak.Donusum((0.0, 0.0, 0.0), egrilme_der_20m=2.0)
        self.assertAlmostEqual(math.degrees(T.aci(20.0, 0.0)), 2.0, places=9)
        # yay boyu korunur, yan sapma ≈ L^2 kappa / 2
        x, y = T.nokta(20.0, 0.0)
        self.assertAlmostEqual(y, 20.0 ** 2 * math.radians(2.0) / 20.0 / 2, delta=0.003)


class TestDunya(unittest.TestCase):
    def test_taban_haritayla_ayni(self):
        for kor in ortak.KORIDORLAR:
            dn = ortak.dunya_kur(kor, {}, np.random.default_rng(0))
            h = ortak.harita_oku(kor)
            self.assertEqual(sorted(map(tuple, dn["veri"]["duvarlar"])), sorted(map(tuple, h["duvarlar"])))
            self.assertTrue(dn["T"].kimlik)
            self.assertEqual(dn["siyah"], [])

    def test_kapi_ac_kapat(self):
        s = ortak.sahne_oku("koridor_5")
        h = ortak.harita_oku("koridor_5")
        kapali = [o for o in s["ozellikler"] if o["tur"] == "kapi_kapali"][0]
        acik = [o for o in s["ozellikler"] if o["tur"] == "kapi_acik"][0]
        d0 = [list(map(float, d)) for d in h["duvarlar"]]
        d1 = ortak.kapi_ac(d0, s, kapali, ortak.mevcut_odalar(s))
        self.assertEqual(len(d1), len(d0) - 3 + 7)           # girinti (3 parça) gider, oda (7 parça) gelir
        d2 = ortak.kapi_kapat(d0, s, acik)
        self.assertEqual(len(d2), len(d0) + 1)
        # yeni kapı kanadı koridor içinde değil: orta hatta uzaklığı > 1 m
        x1, y1, x2, y2 = d2[-1]
        self.assertGreater(ortak.en_yakin_hat(s, (x1 + x2) / 2, (y1 + y2) / 2)[0], 1.0)

    def test_kapi_orani_ic_ice(self):
        a = ortak.dunya_kur("koridor_1", {"kapi": 0.25}, np.random.default_rng(5))["kayit"]
        b = ortak.dunya_kur("koridor_1", {"kapi": 0.50}, np.random.default_rng(5))["kayit"]
        self.assertLessEqual(a["kapi_acilan"] + a["kapi_kapanan"], b["kapi_acilan"] + b["kapi_kapanan"])
        self.assertEqual(b["kapi_acilan"] + b["kapi_kapanan"], round(0.5 * b["kapi_toplam"]))

    def test_genislik(self):
        h0 = ortak.harita_oku("koridor_5")
        h1 = ortak.genislik_kaydir("koridor_5", 0.05)
        y0 = max(max(d[1], d[3]) for d in h0["duvarlar"] if min(d[0], d[2]) < 3.0 and max(d[0], d[2]) > 2.0
                 and 6.0 < min(d[1], d[3]) < 8.0)
        y1 = max(max(d[1], d[3]) for d in h1["duvarlar"] if min(d[0], d[2]) < 3.0 and max(d[0], d[2]) > 2.0
                 and 6.0 < min(d[1], d[3]) < 8.0)
        self.assertAlmostEqual(y1 - y0, 0.05, places=6)
        self.assertEqual(h1["baslangic"], h0["baslangic"])

    def test_esya_koridoru_kapatmaz(self):
        from konumlama.harita2b import Harita2B
        for kor in ortak.KORIDORLAR:
            dn = ortak.dunya_kur(kor, {"esya": 4.0}, np.random.default_rng(3))
            h = Harita2B(dn["veri"])
            s = dn["sahne"]
            for hat in ortak.hatlar(s):
                for (ax, ay), (bx, by) in zip(hat, hat[1:]):
                    n = int(math.hypot(bx - ax, by - ay) / 0.2)
                    P = np.array([(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)])
                    # orta hattan eşyaya / duvara en az robot yarı genişliği + 4 cm
                    self.assertGreater(float(h.geometri_uzakligi(P[:, 0], P[:, 1]).min()), 0.30, kor)

    def test_siyah_alt_kume(self):
        dn = ortak.dunya_kur("koridor_2", {"donussuz": 0.5}, np.random.default_rng(1))
        self.assertGreater(len(dn["siyah"]), 0)
        self.assertLess(len(dn["siyah"]), dn["kayit"]["parca"])


class TestInsan(unittest.TestCase):
    def test_bacak_cifti_ve_yol_verme(self):
        from insan import Kalabalik
        s = ortak.sahne_oku("koridor_5")
        k = Kalabalik(s, "koridor_5", yogunluk=4.0, rng=np.random.default_rng(2))
        n = len(k.kisiler)
        self.assertEqual(k.bacaklar().shape, (2 * n, 3))
        robot = (12.0, 6.2, 0.0)                            # orta hatta duran robot
        en_az = 9.0
        for i in range(1200):                               # 60 s
            k.adim(i * 0.05, 0.05, robot)
            B = k.bacaklar()
            for x, y, r in B:
                c, s_ = math.cos(robot[2]), math.sin(robot[2])
                lx, ly = c * (x - robot[0]) + s_ * (y - robot[1]), -s_ * (x - robot[0]) + c * (y - robot[1])
                d = math.hypot(lx - max(-0.264, min(0.264, lx)), ly - max(-0.2615, min(0.2615, ly)))
                en_az = min(en_az, d - r)
        self.assertGreater(en_az, 0.0)                      # yürüyen insan duran robota girmez

    def test_grup_dagilir(self):
        from insan import Kalabalik
        s = ortak.sahne_oku("koridor_5")
        k = Kalabalik(s, "koridor_5", grup_girinti=1.2, rng=np.random.default_rng(2))
        self.assertEqual(k.sayi()["grup"], 4)
        m = k.grup_merkez
        for i in range(800):
            k.adim(i * 0.05, 0.05, (m[0] - 2.0, 6.2, 0.0))
        self.assertEqual(k.bacaklar().shape[0], 0)


class TestBenzet(unittest.TestCase):
    def _bz(self, p):
        from benzet2b import Benzet2B
        dn = ortak.dunya_kur("koridor_5", p, np.random.default_rng(0))

        class Bos:
            poz = None

            def adim(self, t, tarama, artim):
                self.son = tarama
                return 0.0, 0.0

            def durum(self):
                return {}
        b = Bos()
        bz = Benzet2B(dn, b, (6.0, 6.2, 0.0), 0, p)
        return bz

    def test_menzil_ve_siyah(self):
        bz = self._bz({"menzil": 2.0})
        LT = np.array([0.0, 0.2])
        LP = np.array([[bz.px, bz.py, bz.pth]] * 2)
        tar = bz._tarama(0.0, LT, LP)
        m = tar["mesafeler"]
        self.assertTrue(np.all(m[np.isfinite(m)] <= 2.0 + 1e-9))
        bz = self._bz({"donussuz": 1.0})
        tar = bz._tarama(0.0, LT, LP)
        self.assertTrue(np.all(np.isnan(tar["mesafeler"])))

    def test_belirlenimci(self):
        import kos2b
        g = [x for x in kos2b.gorevler("ab", ["esya_2"]) if x["koridor"] == "koridor_2" and x["tohum"] == 1][0]
        a, b = kos2b.kos_ab(g), kos2b.kos_ab(g)
        for k in ("basari", "varis_hatasi_m", "konum_ort_m", "sure_s"):
            self.assertEqual(a[k], b[k])


if __name__ == "__main__":
    unittest.main()
