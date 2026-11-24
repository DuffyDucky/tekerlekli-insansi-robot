"""Sanal LiDAR (kod/fizik/lidar.py) testleri: sözleşme, analitik mesafe, gürültü, tohum, kör sektör, menzil, dönen tarama,
fiziğe dokunmama, kayıt, robotun kendi gövdesi, 3B penceredeki aç / kapa.

`kod/fizik/kos_fizik.py` koşturur; mujoco yoksa hepsi "atlandı". Sayılar `lidar_ozellik.json`'dan okunur; testteki sabitler
koridor_1 geometrisidir (duvar çizgileri y 5,0 / 7,0, iç duvar levhası 2 mm, uç duvarlar x 1,0 / 31,0).
"""

import math
import os
import sys
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(BURASI)
KOD = os.path.dirname(FIZIK)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import dunya as D  # noqa: E402

fizik_gerekli = unittest.skipUnless(D.FIZIK_VAR, "fizik bağımlılığı (mujoco) yok: atlandı (%s)" % (D.FIZIK_HATA,))


def _np():
    import numpy as np
    return np


@fizik_gerekli
class Sozlesme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import lidar as L
        cls.L = L
        cls.oz = L.ozellik_oku()
        cls.w, _, _ = L._dunya("koridor_1")
        cls.w.adim(0.3)

    def test_sozlesme_bicimi_ve_aci_izgarasi(self):
        """{"t", "acilar", "mesafeler"}; 500 ışın; gövde açısı -pi'den artan, konumlama ızgarasıyla aynı; NaN ölçüm yok."""
        np = _np()
        lid = self.L.SanalLidar(self.w)
        t = lid.anlik_tarama()
        self.assertEqual(set(t), {"t", "acilar", "mesafeler"})
        n = int(round(self.oz["gorus_acisi_derece"] / self.oz["acisal_cozunurluk_derece"]))
        self.assertEqual(len(t["acilar"]), n)
        self.assertEqual(len(t["mesafeler"]), n)
        self.assertIsInstance(t["mesafeler"][0], float)
        beklenen = -math.pi + np.arange(n) * (2 * math.pi / n)
        self.assertTrue(np.array_equal(np.array(t["acilar"]), beklenen))
        self.assertIn(0.0, t["acilar"])
        self.assertTrue(any(math.isnan(m) for m in t["mesafeler"]))
        self.assertEqual(lid.montaj[:3], (self.oz["montaj"]["x_m"], self.oz["montaj"]["y_m"], self.oz["montaj"]["z_m"]))

    def test_analitik_yan_duvarlar(self):
        """Orta hatta (y 6,0) sol / sağ duvar yüzüne LiDAR merkezinden 1,0 - 0,001 m; gürültü ve yuvarlama kapalı: < 0,5 mm."""
        np = _np()
        lid = self.L.SanalLidar(self.w, gurultu_sigma_m=0.0, cozunurluk_m=0.0)
        koken, _ = lid.koken_ve_eksen()
        m = np.array(lid.anlik_tarama()["mesafeler"])
        kal = self.w.p["ic_duvar_kalinligi_m"]
        sol = m[np.argmin(np.abs(lid.acilar - math.pi / 2))]
        sag = m[np.argmin(np.abs(lid.acilar + math.pi / 2))]
        self.assertAlmostEqual(sol, (7.0 - kal / 2) - koken[1], delta=0.0005)
        self.assertAlmostEqual(sag, koken[1] - (5.0 + kal / 2), delta=0.0005)
        # montaj ofseti: LiDAR merkezi tabanın 0,19 m önünde, 0,295 m yukarıda
        x, y, z, yaw, _, _ = self.w.poz()
        self.assertAlmostEqual(koken[0] - x, self.oz["montaj"]["x_m"], delta=1e-4)
        self.assertAlmostEqual(koken[2] - z, self.oz["montaj"]["z_m"], delta=1e-4)

    def test_cozunurluk_yuvarlamasi(self):
        np = _np()
        lid = self.L.SanalLidar(self.w, gurultu_sigma_m=0.0)
        m = np.array(lid.anlik_tarama()["mesafeler"])
        g = lid.son_ek.gercek
        ok = np.isfinite(m)
        q = lid.ayar.cozunurluk_m
        self.assertTrue(np.all(np.abs(m[ok] - g[ok]) <= q / 2 + 1e-9))
        self.assertTrue(np.allclose(m[ok] / q, np.round(m[ok] / q), atol=1e-6))

    def test_gurultu_istatistigi_parametreyle_uyumlu(self):
        """sigma 10 mm (VARSAYIM), 2000 tekrar: ortalama hata < 1 mm, std 10 ± 0,7 mm. sigma 0,02 ile std ölçeklenir."""
        np = _np()
        lid0 = self.L.SanalLidar(self.w, gurultu_sigma_m=0.0, cozunurluk_m=0.0)
        g = np.array(lid0.anlik_tarama()["mesafeler"])
        i = int(np.argmin(np.abs(lid0.acilar - math.pi / 2)))
        for sigma in (0.010, 0.020):
            lid = self.L.SanalLidar(self.w, gurultu_sigma_m=sigma, cozunurluk_m=0.0, tohum=5)
            olc = np.array([lid.anlik_tarama()["mesafeler"][i] for _ in range(2000)])
            self.assertLess(abs(olc.mean() - g[i]), 0.001)
            self.assertAlmostEqual(olc.std(), sigma, delta=0.07 * sigma)

    def test_tohum_belirlenimci(self):
        np = _np()
        a = np.array(self.L.SanalLidar(self.w, tohum=3).anlik_tarama()["mesafeler"])
        b = np.array(self.L.SanalLidar(self.w, tohum=3).anlik_tarama()["mesafeler"])
        c = np.array(self.L.SanalLidar(self.w, tohum=4).anlik_tarama()["mesafeler"])
        self.assertTrue(np.array_equal(a, b, equal_nan=True))
        self.assertFalse(np.array_equal(a, c, equal_nan=True))

    def test_kor_sektor_nan(self):
        """Maske: dosyadaki [139,2, 220,8] + her yana öneri payı 5 der; maskeli bütün ışınlar NaN, dışarıda yakın duvar ölçülür."""
        np = _np()
        lid = self.L.SanalLidar(self.w, gurultu_sigma_m=0.0)
        m = np.array(lid.anlik_tarama()["mesafeler"])
        d = np.degrees(lid.acilar) % 360
        b, e = self.oz["kor_sektorler_derece"][0]
        icerde = (d >= b - 5 - 1e-9) & (d <= e + 5 + 1e-9)
        self.assertTrue(np.array_equal(lid.kor, icerde))
        self.assertTrue(np.all(np.isnan(m[icerde])))
        # maskesizken arka uç duvar (x 1,0) bu ışınlarda görünür: maske sonucu değiştiriyor
        acik = self.L.SanalLidar(self.w, gurultu_sigma_m=0.0, kor_maske=False)
        self.assertTrue(np.all(np.isfinite(np.array(acik.anlik_tarama()["mesafeler"])[icerde])))
        self.assertEqual(int(self.L.SanalLidar(self.w, kor_pay_derece=0.0).kor.sum()),
                         int(((d >= b) & (d <= e)).sum()))

    def test_menzil_siniri(self):
        """Ön uç duvar 29 m -> NaN (12 m üstü); 12 m'yi aşan bütün ışınlar NaN; duvar 4 cm önde -> NaN, 6 cm -> ölçüm."""
        np = _np()
        lid = self.L.SanalLidar(self.w, gurultu_sigma_m=0.0, kor_maske=False)
        m = np.array(lid.anlik_tarama()["mesafeler"])
        g = lid.son_ek.gercek
        self.assertTrue(math.isnan(m[int(np.argmin(np.abs(lid.acilar)))]))
        uzak = np.isfinite(g) & (g > self.oz["menzil_maks_m"])
        self.assertGreater(int(uzak.sum()), 0)
        self.assertTrue(np.all(np.isnan(m[uzak])))
        self.assertLessEqual(np.nanmax(m), self.oz["menzil_maks_m"] + 0.01)
        kal = self.w.p["ic_duvar_kalinligi_m"]
        for bosluk, olcer in ((0.04, False), (0.06, True)):
            w2, _, _ = self.L._dunya("koridor_1", konum=(2.0, 5.0 + kal / 2 + bosluk + self.oz["montaj"]["x_m"], -math.pi / 2))
            l2 = self.L.SanalLidar(w2, gurultu_sigma_m=0.0, cozunurluk_m=0.0)
            v = l2.anlik_tarama()["mesafeler"][int(np.argmin(np.abs(l2.acilar)))]
            self.assertAlmostEqual(l2.son_ek.gercek[int(np.argmin(np.abs(l2.acilar)))], bosluk, delta=1e-4)
            self.assertEqual(not math.isnan(v), olcer, (bosluk, v))

    def test_gecersiz_oran(self):
        np = _np()
        lid = self.L.SanalLidar(self.w, gecersiz_oran=0.3, kor_maske=False, tohum=2)
        lid0 = self.L.SanalLidar(self.w, kor_maske=False)
        n0 = np.isfinite(np.array(lid0.anlik_tarama()["mesafeler"])).sum()
        n = np.mean([np.isfinite(np.array(lid.anlik_tarama()["mesafeler"])).sum() for _ in range(20)])
        self.assertAlmostEqual(n / n0, 0.7, delta=0.03)

    def test_govde_kendi_isinlari_kor_sektorun_icinde(self):
        """Robotun kendi CAD ağı (ev pozu) LiDAR düzleminde tek aralık örter, özellik dosyasının kör sektörünün içinde."""
        w = D.FizikDunya(None, None, (0, 0, 0))
        w.adim(0.3)
        ar = self.L.govde_carpma_analizi(w)[0.0]
        self.assertEqual(len(ar), 1, ar)
        b, e = self.oz["kor_sektorler_derece"][0]
        self.assertGreaterEqual(ar[0]["bas"], b)
        self.assertLessEqual(ar[0]["bit"], e)
        self.assertLess(abs(ar[0]["bas"] - b), 2.0)
        self.assertLess(abs(e - ar[0]["bit"]), 2.0)
        self.assertGreater(ar[0]["en_yakin_m"], self.oz["menzil_min_m"])     # maskesiz gerçek sensör gövdeyi görürdü


@fizik_gerekli
class Hareket(unittest.TestCase):
    def test_donen_tarama_kaymasi(self):
        """Düz giderken dönen tarama: yan duvar mesafesi anlık ile aynı, arka uç duvarda fark v x tau / |cos|."""
        import lidar as L
        # sınır 1 mm: hızlanma bitmeden (t < 3 s) robotun küçük yanal / yaw salınımı yan duvar mesafesini < 1 mm oynatır
        s = L.donen_karsilastir(say=lambda *_: None, t_tur=3.0)
        self.assertTrue(s["poz_bas_ayni"])
        self.assertGreater(s["v_gercek"], 0.3)
        self.assertAlmostEqual(s["tur_yolu_mm"], s["v_gercek"] * 99.0, delta=1.0)
        self.assertGreater(s["yan_ayni_yuzey"], 250)
        self.assertLess(s["yan_ayni_fark_en_cok_mm"], 1.0)
        self.assertLess(s["yan_kayma_sapma_en_cok_mm"], 1.0)
        self.assertGreater(s["arka_isin"], 40)
        self.assertGreater(s["arka_fark_en_cok_mm"], 15.0)
        self.assertLess(s["arka_sapma_en_cok_mm"], 1.0)

    def test_lidar_fizigi_degistirmez_ve_tur_hizi(self):
        """LiDAR bağlıyken robotun yolu bit düzeyinde aynı; 1 s'de 10 tur, t'ler 0,1 s arayla."""
        import lidar as L
        np = _np()
        son = []
        turlar = []
        for bagli in (False, True):
            dn = L.LidarDeneyi("koridor_1", kayit=False, tohum=1)
            if not bagli:
                dn.lidar.ayir()
            dn.lidar.dinleyiciler.append(lambda t, ek: turlar.append(t["t"]))
            dn.devreye_al()
            dn.e.sur_tut(0.3, 0.2, 1000)
            son.append(tuple(dn.w.d.qpos))
        self.assertEqual(son[0], son[1])
        dt = np.diff(turlar)
        self.assertGreaterEqual(len(turlar), 10)
        self.assertTrue(np.allclose(dt, 0.1, atol=1e-9), dt)

    def test_kayit_dosyasi(self):
        """npz: yer gerçeği, odometri, tik, taramalar; düz sürüşte odometri yer gerçeğine yakın; NaN korunur."""
        import lidar as L
        np = _np()
        dn = L.LidarDeneyi("koridor_5", tohum=9)
        dn.devreye_al()
        dn.e.sur_tut(0.25, 0.0, 1500)
        yol = os.path.join(tempfile.mkdtemp(), "deney.npz")
        dn.kayit.kaydet(yol)
        meta, dz = L.kayit_oku(yol)
        self.assertEqual(meta["sahne"], "koridor_5")
        self.assertEqual(meta["lidar"]["tohum"], 9)
        S, N = dz["mesafeler"].shape
        self.assertEqual(N, dn.lidar.N)
        self.assertGreaterEqual(S, 14)
        self.assertEqual(len(dz["tarama_t"]), S)
        self.assertTrue(np.isnan(dz["mesafeler"]).any())
        self.assertEqual(dz["gercek"].shape, dz["odo"].shape)
        self.assertGreater(dz["gercek"][-1, 0] - dz["gercek"][0, 0], 0.2)
        self.assertLess(float(np.max(np.abs(dz["odo"][:, :2] - dz["gercek"][:, :2]))), 0.02)
        ilk = next(L.taramalar(dz))
        self.assertEqual(set(ilk), {"t", "acilar", "mesafeler"})
        self.assertEqual(len(ilk["mesafeler"]), N)


@fizik_gerekli
class Pencere3B(unittest.TestCase):
    def test_f8_ac_kapa_kancayi_geri_birakir(self):
        """F8 (varsayılan kapalı): aç -> fizik adımına bağlanır, nokta çizilir; kapa -> adim_kaydi eski hâline döner."""
        import mujoco
        import gorunum3b as G
        p = G.Pencere("koridor_1")
        self.assertIsNone(p.lidar)
        self.assertIsNone(p.w.adim_kaydi)
        self.assertEqual(G.ISLER[(G.T_F8, False)], "lidar")
        p.is_yap("lidar")
        self.assertIsNotNone(p.w.adim_kaydi)
        p.adim(250)
        scn = mujoco.MjvScene(p.w.m, maxgeom=2000)
        scn.ngeom = 0
        self.assertGreater(p.lidar_ciz(scn), 100)
        p.is_yap("lidar")
        self.assertIsNone(p.lidar)
        self.assertIsNone(p.w.adim_kaydi)
        self.assertEqual(p.lidar_ciz(scn), 0)
        self.assertEqual(scn.ngeom, 0)
        G.LIDAR_DURUM["acik"] = False


if __name__ == "__main__":
    unittest.main()
