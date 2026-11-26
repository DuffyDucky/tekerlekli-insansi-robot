"""Tamamlama turu birim testleri (dar delik sahneleri, yeni yerleşimler, montaj toleransı, sensör zamanlaması, tutma freni).

    py -3 -m unittest discover -s ucurum/testler -t .      (kod/fizik içinde; MuJoCo testleri sanal ortamla)
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucurum import _yol  # noqa: E402,F401
from ucurum import sahne as S  # noqa: E402
from ucurum import sensor as SN  # noqa: E402

try:
    import mujoco  # noqa: F401
    import numpy  # noqa: F401
    MJ = True
except ImportError:
    MJ = False


class TestYeniYerlesim(unittest.TestCase):
    def test_govdeye_sigar_ve_sayilar(self):
        for ad, n in (("4OD+4AD", 8), ("4TD+2AD", 6), ("6OD+2AD", 8), ("4OD+2AD", 6)):
            L = SN.yerlesim(ad, 0.12, 30)
            self.assertEqual(len(L), n, ad)
            for a in L:
                self.assertLessEqual(abs(a.x), 0.255 + 1e-9)
                self.assertLessEqual(abs(a.y), 0.250 + 1e-9)
        arka_ic = [a for a in SN.yerlesim("4OD+4AD", 0.12, 30) if a.ad.startswith("arka_ic")]
        self.assertEqual([a.yon_derece for a in arka_ic], [180.0, 180.0])

    def test_montaj_kotu_izi_yaklastirir(self):
        L = SN.yerlesim("4OD+2AD", 0.12, 30)
        K = SN.montaj_bozu(L, None, kotu=True)

        def iz(a):                      # zemin izinin robot merkezine yatay uzaklığı (eksen ışını)
            e = a.eksen()
            t = a.z / -e[2]
            return math.hypot(a.x + e[0] * t, a.y + e[1] * t)
        for a, b in zip(L, K):
            self.assertLess(iz(b), iz(a), a.ad)
            self.assertAlmostEqual(b.egim_derece, a.egim_derece - 3.0)
        self.assertEqual(L[0].z, 0.12)          # kaynak değişmez


class TestYeniSahne(unittest.TestCase):
    def test_kare_yarik(self):
        k = S.al("kare_15")
        self.assertEqual(k["kenarlar"][0][:3], ["dik", S.E, S.E + 0.15])
        self.assertAlmostEqual(k["kenarlar"][0][4] - k["kenarlar"][0][3], 0.15)
        y = S.al("yarik_10")
        self.assertAlmostEqual(y["kenarlar"][0][2] - y["kenarlar"][0][1], 1.0)

    def test_iskele_pay(self):
        u = S.al("iskele_90")
        self.assertAlmostEqual(S.pay(u["kenarlar"], S.E - 1.0, S.Y0), 0.45)
        self.assertLess(S.pay(u["kenarlar"], S.E - 1.0, S.Y0 + 0.5), 0.0)

    def test_burun_ve_rampa_ucurum(self):
        self.assertAlmostEqual(S.al("merdiven_burun_18x28")["kenarlar"][0][2], S.E + 0.03)
        r = S.al("rampa_10_ucurum")
        self.assertTrue(r["z_dusus_yok"])
        self.assertAlmostEqual(r["kenarlar"][0][2], S.E + 2.0)


class _SahteDunya:
    pass


@unittest.skipUnless(MJ, "mujoco yok (sanal ortam)")
class TestZamanlama(unittest.TestCase):
    def _dizi(self, **k):
        import numpy as np
        d = SN.SensorDizisi.__new__(SN.SensorDizisi)
        d.ayarlar = [None, None]
        d.rng = np.random.default_rng(3)
        d.periyot = float(k.get("periyot_ms") or 20)
        d.butce = float(k.get("butce_ms") or d.periyot)
        d.faz = [0, 10]
        d._sonraki = [0.0, 10.0]
        d._kuyruk = []
        d.olc = lambda i: 0.1
        return d

    def test_33ms_periyot_ve_butce(self):
        d = self._dizi(periyot_ms=33, butce_ms=33)
        for t in range(0, 1000, 10):
            d.ornekle(t)
        ornek0 = [h for (h, i, _) in d._kuyruk if i == 0]
        self.assertTrue(29 <= len(ornek0) <= 31)                    # 1 s'de ≈ 30 örnek
        self.assertEqual(ornek0[0], 40)                             # 0 ms'de alınan, 33 ms -> 40 ms dilimde hazır

    def test_varsayilan_ilk_surumle_ayni(self):
        d = self._dizi()
        for t in range(0, 100, 10):
            d.ornekle(t)
        self.assertEqual([(h, i) for (h, i, _) in d._kuyruk],
                         [(20, 0), (30, 1), (40, 0), (50, 1), (60, 0), (70, 1), (80, 0), (90, 1), (100, 0), (110, 1)])


@unittest.skipUnless(MJ, "mujoco yok (sanal ortam)")
class TestTutma(unittest.TestCase):
    def _kos(self, tutma):
        from ucurum import kosu
        from ucurum.denetci import DenetciAyar
        yer = SN.yerlesim("2K", 0.06, 15)
        r = kosu.kos("rampa_10_uzun", yer, DenetciAyar(esik_m=50.0, fren="rampa", fren_ivme=1.0), dict(tur="ileri", aci=0, v=0.25),
                     tohum=1, baslangic=(S.E - 0.6, S.Y0, 0.0), zorla_tetik=lambda c: c.dunya.poz()[0] >= S.E + 0.85,
                     t_max=12.0, tutma=tutma, durdu_bekle_s=3.0)
        return r

    def test_konum_tutma_kaymayi_durdurur(self):
        r0 = self._kos(None)
        r1 = self._kos(("konum", 40.0, 100.0))
        self.assertTrue(r1["tetik"])
        self.assertEqual(r1["bitis"], "durdu")                      # hız 0,005 m/s altında 3 s kaldı
        self.assertNotEqual(r0["bitis"], "durdu")                   # tutmasız: kısa devre freni sıfır hızda tutmaz, kayar
        self.assertGreater(r0["x_son"] - r1["x_son"], 0.2)


class TestTamamlama2(unittest.TestCase):
    """Tamamlama 2: yarık düzeltmesi (iz sensörü y ±0,216 / ROI), yan sensörler, yeni yarık sahneleri, SECIM_3 dondurması."""

    def test_yeni_yerlesimler_sigar(self):
        for ad, n in (("6WD+4AD", 10), ("6WRD+4AD", 10), ("6WD+4AD+2Y30", 12), ("6WD+4AD+2Y35", 12), ("6WRD+4AD+2Y35", 12)):
            L = SN.yerlesim(ad, 0.12, 30)
            self.assertEqual(len(L), n, ad)
            for a in L:
                self.assertLessEqual(abs(a.x), 0.255 + 1e-9)
                self.assertLessEqual(abs(a.y), 0.250 + 1e-9)
            iz = [a for a in L if a.ad.startswith("on_iz")]
            self.assertEqual(sorted(a.y for a in iz), [-0.216, 0.216])
            self.assertEqual({a.koni_derece for a in iz}, {15.0 if "6WR" in ad else 27.0})
        yan = [a for a in SN.yerlesim("6WD+4AD+2Y35", 0.12, 30) if a.ad.startswith("yan")]
        self.assertEqual([(a.yon_derece, a.egim_derece) for a in yan], [(90.0, 35.0), (-90.0, 35.0)])

    def test_cift_iz_ve_roi_yan(self):
        L = SN.yerlesim("8WRD+4AD+2YR37", 0.12, 30)
        self.assertEqual(len(L), 14)
        for a in L:
            self.assertLessEqual(abs(a.x), 0.255 + 1e-9)
            self.assertLessEqual(abs(a.y), 0.250 + 1e-9)
        iz = [a for a in L if a.ad.startswith("on_iz")]
        self.assertEqual(sorted(round(a.y, 3) for a in iz), [-0.236, -0.196, 0.196, 0.236])
        self.assertEqual({a.koni_derece for a in iz}, {15.0})
        yan = [a for a in L if a.ad.startswith("yan")]
        self.assertEqual([(a.x, a.yon_derece, a.egim_derece, a.koni_derece) for a in yan],
                         [(0.10, 90.0, 37.0, 15.0), (0.10, -90.0, 37.0, 15.0)])
        self.assertEqual([a.ad for a in L[:8]], ["on_sol", "on_iz_dis_sol", "on_iz_ic_sol", "on_ic_sol", "on_ic_sag", "on_iz_ic_sag",
                                                 "on_iz_dis_sag", "on_sag"])

    def test_eski_yerlesim_degismedi(self):
        L = SN.yerlesim("6OD+4AD", 0.12, 30)
        self.assertEqual([(a.ad, a.y, a.koni_derece) for a in L if a.ad.startswith("on_iz")],
                         [("on_iz_sol", 0.19, 27.0), ("on_iz_sag", -0.19, 27.0)])

    def test_yeni_yarik_sahneleri(self):
        for c in (9, 11, 13):
            u = S.al("yarik_%d" % c)
            k = u["kenarlar"][0]
            self.assertAlmostEqual(k[4] - k[3], c / 100.0)
            self.assertAlmostEqual(k[2] - k[1], 1.0)
            self.assertNotIn(c, S.KARE_GEL)

    def test_secim3_donduruldu(self):
        from ucurum import deney as D
        G = D.gorevler("t_hukum")
        self.assertEqual(len(G), 3412)
        self.assertEqual(max(g["tohum"] for g in G), 205)
        self.assertEqual({g["ys"]["ad"] for g in G}, {"6OD+4AD"})

    def test_t2_hukum_tohum_ve_kapsam(self):
        from ucurum import deney as D
        G = D.gorevler("t2_hukum")
        self.assertEqual({g["tohum"] for g in G}, set(range(206, 211)))
        dn = {g["senaryo"]["d"] for g in G if g["alt"] == "yeni_donus_dar"}
        self.assertIn(0.35, dn)
        self.assertTrue({"yarik_9", "yarik_11", "yarik_13"} <= {g["sahne"] for g in G})
        gel = {g["sahne"] for a in ("t2_yarik_gel", "t2_yarik_gel2", "t2_donus_gel", "t2_donus_gel2",
                                                     "t2_kusur", "t2_duyar") for g in D.gorevler(a)}
        self.assertFalse({206, 207, 208, 209, 210} & {g["tohum"] for a in ("t2_yarik_gel", "t2_donus_gel2", "t2_kusur", "t2_duyar")
                                                     for g in D.gorevler(a)})
        self.assertFalse({"yarik_9", "yarik_11", "yarik_13"} & gel)


@unittest.skipUnless(MJ, "mujoco yok (sanal ortam)")
class TestTamamlama2Mj(unittest.TestCase):
    def test_isinlar_tekere_carpmaz(self):
        from ucurum import kosu
        for ad in ("6WRD+4AD+2Y35", "6WD+4AD+2Y30", "8WRD+4AD+2YR37", "8WRD+4AD+2YR40"):
            _, _, _, sd, _ = kosu.dunya_kur("duz", SN.yerlesim(ad, 0.12, 30), 1)
            self.assertEqual(sd.teker_ortusmesi(), [0] * len(sd.ayarlar), ad)


if __name__ == "__main__":
    unittest.main()
