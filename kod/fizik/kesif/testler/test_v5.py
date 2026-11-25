"""v5 dönüş / yay güvenliği sınamaları (unittest).

    cd kod/fizik && py -3 -m unittest kesif.testler.test_v5 -v
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kesif import _yol  # noqa: E402,F401


class V5Surum(unittest.TestCase):
    def test_v1_v4_degismedi_v5_v4_ustune(self):
        from kesif.beyin import KesifBeyni, surum_ayari
        for s in ("v1", "v2", "v3", "v4"):
            a = surum_ayari(s)
            self.assertFalse(a.donus_durunca or a.donus_sigmaz_geri or a.yay_kacin)
            self.assertEqual(a.donus_kay_m, 0.60)
        a4, a5 = surum_ayari("v4"), surum_ayari("v5")
        a5.donus_durunca = a5.donus_sigmaz_geri = a5.yay_kacin = False
        a5.donus_kay_m = 0.60
        self.assertEqual(a4, a5)                       # v5 = v4 + dört alan, başka fark yok
        self.assertEqual(KesifBeyni(ayar=surum_ayari("v5")).durum()["ek"]["surum"], "v5")
        self.assertEqual(KesifBeyni(ayar=surum_ayari("v4")).durum()["ek"]["surum"], "v4")


class KappaIste(unittest.TestCase):
    def test_bir_adimlik_egrilik_istegi(self):
        from gezinme.izleyici import IzleyiciAyar
        from kesif.surus4 import ZarfIzleyici
        iz = ZarfIzleyici(IzleyiciAyar(v_max=0.25, a_max=100.0, a_w=100.0))
        iz.yol_ver([(0.0, 0.0), (5.0, 0.0)])
        iz.komut((0.0, 0.0, 0.0))
        iz.kappa_iste = 0.5
        k = iz.komut((0.0, 0.0, 0.0))
        self.assertAlmostEqual(k.w, k.v * 0.5, places=6)
        self.assertIsNone(iz.kappa_iste)
        self.assertAlmostEqual(iz.son_kappa, 0.0, places=6)      # saf takibin kendi eğriliği saklanır
        k2 = iz.komut((0.0, 0.0, 0.0))
        self.assertAlmostEqual(k2.w, 0.0, places=6)              # istek tek adımlık


class DonusSigmaz(unittest.TestCase):
    def _beyin(self, surum):
        from kesif.beyin import KesifBeyni, surum_ayari
        b = KesifBeyni(ayar=surum_ayari(surum))
        b.mod = "kesif"
        b.t = 100.0
        b._supurme_carpar = lambda p, d, pay=0.03: True      # hiçbir dönüş sığmıyor
        b._duz_carpar = lambda p, s, pay=0.02: True          # hiçbir kayma sığmıyor
        return b

    def test_v5_once_geri_cekilir_sonra_eski_davranis(self):
        from gezinme.izleyici import Komut
        k = Komut(0.0, 0.8, mod="yerinde", hedef=(5.0, 3.0))
        b = self._beyin("v5")
        poz = (5.0, 0.0, 0.0)
        self.assertEqual(b._donus_karar(poz, k), "geri")
        self.assertIsNotNone(b._kurtarma)
        self.assertFalse(b._donus_onay)
        b._kurtarma = None
        b.t = 105.0
        self.assertIsNone(b._donus_karar(poz, k))               # aynı yer, 20 s içinde: izleyiciye bırak
        self.assertTrue(b._donus_onay)
        self.assertEqual(b.sayac["donus_kor"], 1)
        b4 = self._beyin("v4")
        self.assertIsNone(b4._donus_karar(poz, k))              # v4: doğrudan izleyiciye bırakır
        self.assertIsNone(b4._kurtarma)

    def test_v5_durunca_denetler(self):
        from gezinme.izleyici import Komut
        from kesif.beyin import KesifBeyni, surum_ayari
        cagri = []
        for surum, beklenen in (("v4", 1), ("v5", 0)):
            b = KesifBeyni(ayar=surum_ayari(surum))
            b.slam.tur_sayisi = 5
            b.mod = "kesif"
            b.yol = [(0.0, 0.0), (0.0, 2.0)]
            b.t_plan = 1e9
            b._planla = lambda t, poz: None
            b._hiz_ayarla_v4 = lambda: None
            n = []
            b._donus_karar = lambda poz, k, n=n: n.append(1)
            b.izleyici.komut = lambda poz, on_mesafe=None: Komut(0.15, 0.0, mod="yerinde", hedef=(0.0, 2.0))
            b.izleyici._v = 0.15                              # hâlâ frenliyor
            b.adim(10.0, None, None)
            cagri.append(len(n))
            self.assertEqual(len(n), beklenen, surum)


class YayKacin(unittest.TestCase):
    def test_saga_yay_duvar_ucundan_uzaga_itilir(self):
        from gezinme.izleyici import Komut
        from kesif.beyin import KesifBeyni, surum_ayari
        sonuc = {}
        for surum in ("v4", "v5"):
            b = KesifBeyni(ayar=surum_ayari(surum))
            b.mod = "kesif"
            iz = b.izleyici
            iz.son = Komut(0.25, -0.1, mod="izle")
            iz.son_alfa, iz.son_kappa = -0.1, -0.4         # küçük yön hatası: hizalanma yok
            iz._w = -0.1
            iz.ayar.v_max = 0.25
            b.slam.son_noktalar = (np.array([0.42, 0.46, 0.50]), np.array([-0.33, -0.33, -0.33]))   # sağ önde duvar ucu
            b._hiz_ayarla_v4()
            sonuc[surum] = (iz.kappa_iste, iz.hizala_iste, dict(b.sayac))
        self.assertIsNone(sonuc["v4"][0])
        self.assertGreater(sonuc["v4"][2].get("zarf_yavas", 0), 0)     # v4 de çarpmayı öngörür, önlem yok (|alfa| küçük)
        k5 = sonuc["v5"][0]
        self.assertIsNotNone(k5)
        self.assertGreater(k5, -0.4)                     # sola (duvar ucundan uzağa) itildi
        self.assertGreater(sonuc["v5"][2].get("yay_kacin", 0), 0)


if __name__ == "__main__":
    unittest.main()
