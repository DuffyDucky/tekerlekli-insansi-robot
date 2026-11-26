"""Kip karşılaştırması ve "emin değilim" ölçütünün birim testleri (sistem Python'u, numpy; ≈ 3 s).

    py -3 -m unittest discover -s kod/fizik/deneyler/tasinma/testler -v"""

import os
import sys
import unittest

BURASI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BURASI)
import emin  # noqa: E402
import kipler as KP  # noqa: E402


def _tarama(kor, poz, tohum=0):
    import numpy as np
    from gezinme.beyinler import haritalar
    from konumlama import LidarOzellik
    from konumlama.tarama import sentetik_tarama
    h = haritalar([kor])[0]
    return sentetik_tarama(h, poz, LidarOzellik.varsa_dosyadan(), rng=np.random.default_rng(tohum))


class _Ic:
    """Sabit komut veren, 10. adımda "bitti" diyen sahte beyin (yer gerçeği görmez)."""
    koridor = "koridor_5"

    def __init__(self):
        self.poz = (8.0, 6.2, 0.0)
        self.tah = None
        self.k = None
        self.n = 0

    def adim(self, t, tarama, artim):
        self.n += 1
        if self.n == 5:
            self.poz = (10.0, 6.2, 0.0)        # konumlayıcı kendi kendine 2 m atladı
        return 0.25, 0.1

    def durum(self):
        return {"mod": "bitti" if self.n >= 10 else "izle"}


class TestGozlemci(unittest.TestCase):
    def test_komut_aynen_ve_vardim_kaydi(self):
        ic = _Ic()
        g = KP.Gozlemci(ic, "koridor_5")
        tar = _tarama("koridor_5", (8.0, 6.2, 0.0))
        for i in range(12):
            self.assertEqual(g.adim(0.1 * i, tar, (0.0, 0.0, 0.0)), (0.25, 0.1))
        self.assertEqual(g.vardim_sayisi, 1)
        v = g.vardim
        self.assertAlmostEqual(v["sic_maks"], 2.0, places=6)
        self.assertEqual(v["sic_03"], 1)
        self.assertIsNotNone(v["u_med"])
        self.assertEqual(g.koridor, "koridor_5")          # bilinmeyen alanlar beyne geçer


class TestEmin(unittest.TestCase):
    def test_kural_ve_uygula(self):
        v = dict(sic_maks=3.0, u_med=0.9, g_med=0.01, std_xy=0.02, pay=0.95, kk=False, rast_n=0, tarama_n=100)
        self.assertTrue(emin.emin_degil(v, [("sic", 1.0)]))
        self.assertFalse(emin.emin_degil(v, [("sic", 5.0), ("uyum", 0.8)]))
        self.assertTrue(emin.emin_degil(v, [("sic", 5.0), ("uyum", 0.95)]))
        self.assertFalse(emin.emin_degil(None, [("sic", 0.0)]))
        s_hata = dict(sonuc="sessiz_hata", beyin_bitti=True, vardim=v)
        s_dogru = dict(sonuc="dogru_varis", beyin_bitti=True, vardim=v)
        s_sure = dict(sonuc="sure_doldu", beyin_bitti=False, vardim=v)
        self.assertEqual(emin.uygula(s_hata, [("sic", 1.0)]), "onlenen")
        self.assertEqual(emin.uygula(s_dogru, [("sic", 1.0)]), "gereksiz_durma")
        self.assertEqual(emin.uygula(s_sure, [("sic", 1.0)]), "sure_doldu")
        self.assertEqual(emin.uygula(s_dogru, [("sic", 5.0)]), "dogru_varis")

    def test_secim_sinir(self):
        iyi = dict(sic_maks=0.1, u_med=0.95, g_med=0.0, std_xy=0.02, pay=0.95, kk=False, rast_n=0, tarama_n=100)
        kotu = dict(iyi, sic_maks=12.0)
        S = [dict(sonuc="dogru_varis", beyin_bitti=True, vardim=iyi) for _ in range(50)]
        S += [dict(sonuc="sessiz_hata", beyin_bitti=True, vardim=kotu) for _ in range(5)]
        r = emin.sec(S)
        self.assertEqual(r["gelistirme"]["onlenen"], 5)
        self.assertEqual(r["gelistirme"]["gereksiz"], 0)


class TestKosul(unittest.TestCase):
    def test_kosul_coz_ve_gorevler(self):
        self.assertEqual(KP.kosul_coz("kapi_2+kucuk"), ("kapi_2", "kucuk"))
        self.assertEqual(KP.kosul_coz("okul_orta"), ("okul_orta", None))
        G = KP.gorevler("sinama")
        self.assertEqual(len(G), len(KP.KUMELER["sinama"]["kosullar"]) * 4 * 6 * 2)
        self.assertEqual(len({g["id"] for g in G}), len(G))
        # tohumlar önceki aşamalarla ve geliştirmeyle çakışmaz
        self.assertFalse(set(KP.KUMELER["sinama"]["tohumlar"]) & set(KP.KUMELER["gelistirme"]["tohumlar"]))
        self.assertFalse(set(KP.KUMELER["sinama"]["tohumlar"]) & {1, 2, 3, 4, 901, 902, 903})


if __name__ == "__main__":
    unittest.main()
