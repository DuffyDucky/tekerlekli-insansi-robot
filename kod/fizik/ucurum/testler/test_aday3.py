"""Aday 3 (dondurma 3) birim testleri: iz çifti değişen düzenler, denetçi davranış kuralları, ayar aşamalarının tohumları.

    py -3 -m unittest discover -s ucurum/testler -t .      (kod/fizik içinde; MuJoCo testleri sanal ortamla)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucurum import _yol  # noqa: E402,F401
from ucurum import sensor as SN  # noqa: E402
from ucurum.denetci import DenetciAyar, UcurumDenetci  # noqa: E402

try:
    import mujoco  # noqa: F401
    import numpy  # noqa: F401
    MJ = True
except ImportError:
    MJ = False


class TestIzDuzen(unittest.TestCase):
    def test_sigar_ve_yalniz_iz_degisir(self):
        temel = SN.yerlesim("8WRD+4AD+2YR40", 0.12, 30)
        for b, (ara, z, e) in SN.IZ_DUZEN.items():
            L = SN.yerlesim(b + "D+4AD+2YR40", 0.12, 30)
            self.assertEqual(len(L), 14, b)
            self.assertEqual([a.ad for a in L], [a.ad for a in temel])
            for a, t in zip(L, temel):
                self.assertLessEqual(abs(a.x), 0.255 + 1e-9)
                self.assertLessEqual(abs(a.y), 0.250 + 1e-9)
                if a.ad.startswith("on_iz"):
                    self.assertAlmostEqual(abs(a.y), 0.216 + (ara if "dis" in a.ad else -ara))
                    self.assertEqual((a.z, a.egim_derece, a.koni_derece), (z or 0.12, e or 30.0, 15.0))
                else:
                    self.assertEqual((a.x, a.y, a.z, a.egim_derece, a.yon_derece, a.koni_derece),
                                     (t.x, t.y, t.z, t.egim_derece, t.yon_derece, t.koni_derece))

    def test_eski_cift_iz_degismedi(self):
        iz = [a for a in SN.yerlesim("8WRD+4AD+2YR40", 0.12, 30) if a.ad.startswith("on_iz")]
        self.assertEqual(sorted(round(a.y, 3) for a in iz), [-0.236, -0.196, 0.196, 0.236])
        self.assertEqual({(a.z, a.egim_derece) for a in iz}, {(0.12, 30.0)})


class TestKural(unittest.TestCase):
    def test_kuralsiz_komut_ayni(self):
        d = UcurumDenetci(2, DenetciAyar(esik_m=0.1, onay=3, politika="yavasla"))
        self.assertIsNone(d.ayar.kural)
        self.assertEqual(d.komut(0.0, -1.0), (0.0, -1.0))
        self.assertEqual(d.komut(-0.25, 0.0), (-0.25, 0.0))
        self.assertIsNone(d.hiz_siniri(0.0))

    def test_yerinde_donus_yaya_cevrilir(self):
        d = UcurumDenetci(2, DenetciAyar(kural=dict(donus_yay_r=0.5, donus_w_tavan=0.5)))
        v, w = d.komut(0.0, -1.0)
        self.assertAlmostEqual(w, -0.5)
        self.assertAlmostEqual(v, 0.25)
        self.assertEqual(d.komut(0.25, 0.3), (0.25, 0.3))          # yerinde dönüş değil: dokunulmaz

    def test_geri_tavan(self):
        d = UcurumDenetci(2, DenetciAyar(kural=dict(geri_tavan=0.15)))
        v, w = d.komut(-0.25, 0.2)
        self.assertAlmostEqual(v, -0.15)
        self.assertAlmostEqual(w, 0.12)
        self.assertEqual(d.komut(-0.10, 0.0), (-0.10, 0.0))

    def test_supheli_okuma_surundurur_durdurmaz(self):
        d = UcurumDenetci(1, DenetciAyar(esik_m=0.1, onay=3, politika="yavasla",
                                         kural=dict(supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0)))
        for _ in range(26):
            d.kalibrasyon_ornegi(0, 0.140)
        d.kalibre()
        self.assertFalse(d.isle(1.0, 0, 0.170))                    # +30 mm: şüpheli, tetik değil
        self.assertEqual(d.hiz_siniri(1.5), 0.05)
        self.assertIsNone(d.hiz_siniri(2.1))
        self.assertFalse(d.tetik)
        self.assertEqual(d.supheli_say, 1)

    def test_bilinmeyen_kural_reddedilir(self):
        with self.assertRaises(AssertionError):
            DenetciAyar(kural=dict(hakem=1))


class TestDondurma3(unittest.TestCase):
    def test_adaylar_donmus(self):
        from ucurum import deney as D
        self.assertEqual(D.SECIM_3A["yerlesim"]["ad"], SN.ADAY_3A)
        self.assertEqual(D.SECIM_3B["yerlesim"]["ad"], SN.ADAY_3B)
        self.assertEqual(len(SN.yerlesim(SN.ADAY_3A, 0.12, 30)), D.SECIM_3A["sensor_n"])
        self.assertEqual(len(SN.yerlesim(SN.ADAY_3B, 0.12, 30)), D.SECIM_3B["sensor_n"])
        self.assertEqual(D.SECIM_3B["kural"], D.T3_B_KURAL["geri100"])
        a = D._ana(D.SECIM_3B)
        self.assertEqual(a["kural"], D.SECIM_3B["kural"])
        DenetciAyar(**a)                                            # kural alanları geçerli
        for s in (D.SECIM_1, D.SECIM_2, D.SECIM_3, D.SECIM_3A):    # eski seçimlerde kural yok: görevler değişmez
            self.assertNotIn("kural", D._ana(s))
        # kural dışında 3B, SECIM_3 ile aynı; 3A, secim.json ile yalnız yerleşim adında ayrılır
        self.assertEqual({k: v for k, v in D.SECIM_3B.items() if k != "kural"}, D.SECIM_3)
        s = D.secim()
        self.assertEqual({k: D.SECIM_3A[k] for k in ("esik_m", "onay", "politika", "fren", "fren_ivme", "hukum_kosul")},
                         {k: s[k] for k in ("esik_m", "onay", "politika", "fren", "fren_ivme", "hukum_kosul")})
        # dondurma anında secim.json değişmemişti (8WRD). Bağımsız hüküm 3'ün karar kuralı onu 3A'ya çevirdi (hükümden SONRA,
        # yalnız bu satır güncellendi): 3A yalnız durum alanı o hükmü gösteriyorsa kabul edilir.
        if s["yerlesim"]["ad"] == D.SECIM_3A["yerlesim"]["ad"]:
            self.assertTrue(s["durum"].startswith("ONAYLI SECIM: bagimsiz hukum 3"))
            self.assertEqual({k: s[k] for k in D.SECIM_3A}, D.SECIM_3A)
        else:
            self.assertEqual(s["yerlesim"]["ad"], "8WRD+4AD+2YR40")


class TestAsamalar(unittest.TestCase):
    def test_ayar_tohumlari_gelistirme(self):
        from ucurum import deney as D
        for a in ("t3_a_gel", "t3_b_gel"):
            G = D.gorevler(a)
            self.assertTrue({g["tohum"] for g in G} <= {1, 2, 3}, a)


@unittest.skipUnless(MJ, "mujoco yok (sanal ortam)")
class TestAday3Mj(unittest.TestCase):
    def test_isinlar_tekere_carpmaz(self):
        from ucurum import kosu
        for b in SN.IZ_DUZEN:
            _, _, _, sd, _ = kosu.dunya_kur("duz", SN.yerlesim(b + "D+4AD+2YR40", 0.12, 30), 1)
            self.assertEqual(sd.teker_ortusmesi(), [0] * len(sd.ayarlar), b)


if __name__ == "__main__":
    unittest.main()
