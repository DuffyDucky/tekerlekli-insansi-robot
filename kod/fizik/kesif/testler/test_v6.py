"""v6 tüm gövde süpürme öngörüsü sınamaları (unittest).

    cd kod/fizik && py -3 -m unittest kesif.testler.test_v6 -v
"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kesif import _yol  # noqa: E402,F401


def _yay_beyni(surum, noktalar):
    """Sola yaydaki beyin: tanıdaki geometri (v5 17x17_t1 t1 yeniden koşusu: alfa 0,18, kappa 0,47, v_seyir)."""
    from gezinme.izleyici import Komut
    from kesif.beyin import KesifBeyni, surum_ayari
    b = KesifBeyni(ayar=surum_ayari(surum))
    b.mod = "kesif"
    b.t = 100.0
    iz = b.izleyici
    iz.son = Komut(0.25, 0.12, mod="izle")
    iz.son_alfa, iz.son_kappa, iz.son_kalan = 0.18, 0.47, 2.0
    iz._w = 0.12
    iz.ayar.v_max = 0.25
    b.on_mesafe = 1.4
    b.slam.son_noktalar = noktalar
    return b


class V6Surum(unittest.TestCase):
    def test_v1_v5_degismedi_v6_v5_ustune(self):
        from kesif.beyin import KesifBeyni, surum_ayari
        for s in ("v1", "v2", "v3", "v4", "v5"):
            self.assertFalse(surum_ayari(s).yay_v6)
        a5, a6 = surum_ayari("v5"), surum_ayari("v6")
        self.assertTrue(a6.yay_v6)
        a6.yay_v6 = False
        self.assertEqual(a5, a6)                       # v6 = v5 + tek alan
        self.assertEqual(KesifBeyni(ayar=surum_ayari("v6")).durum()["ek"]["surum"], "v6")
        self.assertEqual(KesifBeyni(ayar=surum_ayari("v5")).durum()["ek"]["surum"], "v5")


class Aciklik(unittest.TestCase):
    def test_kutu_acikligi(self):
        from kesif.robot import VARSAYILAN, gezinmeden_oku
        from kesif.surus4 import aciklik
        r = gezinmeden_oku(VARSAYILAN)
        hx = r.derinlik_m / 2
        self.assertAlmostEqual(aciklik([(0.0, 0.0, 0.0)], r, np.array([hx + 0.05]), np.array([0.0])), 0.05, places=6)
        self.assertLess(aciklik([(0.0, 0.0, 0.0)], r, np.array([hx - 0.02]), np.array([0.0])), 0.0)
        self.assertEqual(aciklik([(0.0, 0.0, 0.0)], r, np.zeros(0), np.zeros(0)), math.inf)
        # köşe: (hx + 0,03, hy + 0,04) -> 0,05
        self.assertAlmostEqual(aciklik([(0.0, 0.0, 0.0)], r, np.array([hx + 0.03]), np.array([r.genislik_m / 2 + 0.04])),
                               0.05, places=6)


class YayV6(unittest.TestCase):
    # sol yanın yanında, 2 cm'de duvar ucu (gövde x +0,20): tanıdaki dört temasın geometrisi
    UC = (np.array([0.20, 0.20, 0.20]), np.array([0.282, 0.30, 0.34]))

    def test_v5_her_adayi_carpar_sayar_v6_uzaklasan_secer(self):
        b5 = _yay_beyni("v5", self.UC)
        b5._hiz_ayarla_v4()
        self.assertIsNone(b5.izleyici.kappa_iste)                  # v5: duvar ucu zaten 3 cm payın içinde
        self.assertGreater(b5.sayac.get("yay_kacin_yok", 0), 0)    # -> aday yok, çarpan yay sürülür (kök neden)
        b6 = _yay_beyni("v6", self.UC)
        b6._hiz_ayarla_v4()
        k6 = b6.izleyici.kappa_iste
        self.assertIsNotNone(k6)
        self.assertLess(k6, 0.47)                                  # sola yay bırakıldı (duvar ucundan uzağa)
        self.assertGreater(b6.sayac.get("yay_kacin", 0), 0)
        self.assertIsNone(b6._kurtarma)

    def test_v6_aday_yoksa_geri_cekilir_sonra_en_genis(self):
        # her yanı kapalı: önde ve iki yanda 1 cm duvar
        xs = np.concatenate([np.full(30, 0.275), np.linspace(-0.25, 0.25, 30), np.linspace(-0.25, 0.25, 30)])
        ys = np.concatenate([np.linspace(-0.25, 0.25, 30), np.full(30, 0.272), np.full(30, -0.272)])
        b = _yay_beyni("v6", (xs, ys))
        b.on_mesafe = 1.4                                          # (ön şerit öyle görmüyor say: denetim yine kapatır)
        b._hiz_ayarla_v4()
        self.assertIsNotNone(b._kurtarma)
        self.assertEqual(b._kurtarma["neden"], "yay_sigmaz")
        b._kurtarma = None
        b.mod = "kesif"
        b.t = 105.0
        b._engel_onbellek = None
        b._hiz_ayarla_v4()
        self.assertIsNone(b._kurtarma)                             # aynı yer, 20 s içinde: en geniş açıklıklı aday
        self.assertEqual(b.sayac.get("yay_en_genis", 0), 1)

    def test_v6_gecmis_tarama_ve_harita_govde_yanini_kapsar(self):
        from kesif.beyin import KesifBeyni, surum_ayari
        b = KesifBeyni(ayar=surum_ayari("v6"))
        b.t = 1.0
        b.slam.son_noktalar = (np.array([0.20]), np.array([0.30]))
        b._gecmis_tarama_ekle(1.0)
        b.slam.son_noktalar = (np.zeros(0), np.zeros(0))             # son tarama artık görmüyor (LiDAR gerisi)
        b.t = 1.5
        x, y = b._engel_govde(b.slam.poz)
        self.assertTrue(np.any(np.hypot(x - 0.20, y - 0.30) < 0.02))
        b.t = 4.0
        b._gecmis_tarama_ekle(4.0)                                   # yay_gecmis_s (2 s) dışında: düşer
        x, y = b._engel_govde(b.slam.poz)
        self.assertFalse(np.any(np.hypot(x - 0.20, y - 0.30) < 0.02))
        # haritadaki dolu hücre (isabet ortalamasıyla) da gelir
        g = b.slam.izgara
        i, j = g.hucre(np.array([-0.10]), np.array([0.33]))
        g.L[int(i[0]), int(j[0])] = 3.0
        b._engel_onbellek = None
        x, y = b._engel_govde(b.slam.poz)
        self.assertTrue(np.any(np.hypot(x + 0.10, y - 0.33) < 0.04))

    def test_v6_yerinde_donus_tarama_noktasini_da_gorur(self):
        from kesif.beyin import KesifBeyni, surum_ayari
        sonuc = {}
        for surum in ("v5", "v6"):
            b = KesifBeyni(ayar=surum_ayari(surum))
            b.t = 1.0
            b.slam.poz = (3.0, 0.0, 0.0)                      # START sanal duvarından uzakta
            # yalnız taramada (haritada yok): sol arka köşenin 10 cm dışında, yerinde sola dönüşte süpürülür
            b.slam.son_noktalar = (np.array([-0.30]), np.array([0.32]))
            sonuc[surum] = b._supurme_carpar(b.slam.poz, 1.2)
        self.assertFalse(sonuc["v5"])
        self.assertTrue(sonuc["v6"])


class UctanUcaV6(unittest.TestCase):
    def test_5x5_2b_v6(self):
        from kesif.beyin import surum_ayari
        from kesif.kos import tek_kos
        r = tek_kos({"deney": "test", "strateji": "kesif", "sahne": "labirent_5x5_t1", "tohum": 0, "donus_hata": 0.14,
                     "ayar": surum_ayari("v6"), "ayar_ad": "v6"})
        self.assertEqual(r["durum"], "basari")
        self.assertEqual(int(r["carpma_sayisi"] or 0), 0)


if __name__ == "__main__":
    unittest.main()
