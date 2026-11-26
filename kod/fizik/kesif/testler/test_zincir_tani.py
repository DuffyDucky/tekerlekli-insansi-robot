"""Deneme zinciri tanısı (kesif.zincir_tani) ve neden kuralı (kesif.rapor_deneme.neden) sınamaları. Yalnız ölçüm kodu.

    cd kod/fizik && py -3 -m unittest kesif.testler.test_zincir_tani -v
"""

import json
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kesif import _yol  # noqa: E402,F401

AD = "labirent_17x17_t19"


def _sahte_kayit(yol, s2):
    """FINISH yanında bir sınır (F), uzakta iki sınır (A, B). İlk ek kaydı (t 0,1) önceki denemenin son planı gibi
    FINISH sınırını ucuz ve seçili gösterir: tanı onu atlamalı."""
    from kesif.sahne import dunyadan_beyne
    fx, fy = (float(v) for v in dunyadan_beyne(s2, 24.45, 2.6))     # FINISH çizgisinin 0,4 m içi (dünya)
    A, B = [5.0, 5.0], [9.0, 2.0]

    def ek(sec, d_yol, sinirlar):
        return {"sinirlar": sinirlar, "secilen_sinir": sec, "plan": {"d_yol": d_yol, "hedef_maliyet": d_yol}}
    F = [fx, fy, 1.2, fx, fy, 150.0]
    ekler = [{"t": 0.1, "ek": ek([fx, fy], 2.0, [[fx, fy, 1.2, fx, fy, 2.0]])},
             {"t": 2.1, "ek": ek(A, 100.0, [A + [1.2] + A + [100.0], F])},
             {"t": 4.1, "ek": ek([5.2, 5.1], 98.0, [A + [1.2] + A + [98.0], F])},     # aynı hedef (< 1 m)
             {"t": 6.1, "ek": ek(B, 30.0, [B + [1.2] + B + [30.0], F])}]
    T = np.arange(0.0, 8.0, 0.05)
    g = np.zeros((T.size, 3))
    g[:, 0] = np.linspace(4.0, 6.0, T.size)
    g[:, 1] = 4.0
    np.savez_compressed(yol, meta=np.array(json.dumps({"ekler": ekler, "haritalar": []})), t=T, gercek=g)


class ZincirTani(unittest.TestCase):
    def test_bayat_ek_atlanir_ve_secim_dizisi(self):
        from kesif.sahne import sahne_yukle
        from kesif.tani import labirent_grafi
        from kesif.zincir_tani import deneme_tani
        from kesif._yol import SAHNELER
        s2 = sahne_yukle(AD)
        with open(os.path.join(SAHNELER, AD + ".json"), encoding="utf-8") as f:
            sj = json.load(f)
        with tempfile.TemporaryDirectory() as d:
            yol = os.path.join(d, "k.npz")
            _sahte_kayit(yol, s2)
            r = deneme_tani(yol, s2, sj, labirent_grafi(sj), set())
        self.assertEqual(r["hedef_dyol_dizi"], "100 30")
        self.assertEqual(r["hedef_dyol_ilk"], 100.0)
        self.assertEqual(r["finish_sinir_ilk_t"], 2.1)
        self.assertEqual(r["finish_sinir_bas_maliyet"], 150.0)
        self.assertEqual(r["finish_sinir_secildi"], 0)          # bayat t 0,1 kaydındaki seçim sayılmaz
        self.assertGreater(r["finish_en_yakin_m"], 10.0)

    def test_neden_kurali(self):
        from kesif.rapor_deneme import neden
        tempo = (3.86, 4.23, 4.75)
        r1 = {"poz_hata_maks_m": "0.3", "finish_sinir_ilk_t": "", "finish_sinir_bas_maliyet": "",
              "finish_sinir_secildi": "0"}
        bilinen = dict(r1, finish_sinir_ilk_t="2.1", finish_sinir_bas_maliyet="150")
        self.assertTrue(neden([r1, r1], 220.0, tempo).startswith("hız"))
        self.assertEqual(neden([r1, bilinen], 150.0, tempo), "keşif / sınır sırası")
        self.assertEqual(neden([r1, r1], 150.0, tempo), "keşif / FINISH bölgesi görülmedi")
        self.assertIn("sınırda hız", neden([r1, r1], 200.0, tempo))
        kay = dict(r1, poz_hata_maks_m="0.6")
        self.assertIn("harita kayması işareti", neden([kay, kay, r1], 150.0, tempo))
        kop = [dict(r1, deneme_no="1", start_bagli_025="0", hedef_sayisi="80"),
               dict(r1, deneme_no="2", start_bagli_025="1", hedef_sayisi="0")]
        self.assertTrue(neden(kop, 100.0, tempo).startswith("harita kayması / START kopuk: 1."))

    def test_start_bagli(self):
        from kesif.zincir_tani import start_bagli
        iz = np.zeros((60, 100), dtype=np.int16)        # 5 cm: x -1..4 m, y -1,5..1,5 m, boş koridor
        h = {"izgara": iz, "cozunurluk_m": 0.05, "orijin": (-1.0, -1.5)}
        self.assertEqual(start_bagli(h, (3.0, 0.0)), 1)
        iz[:, 40] = 100                                  # x = 1,0 m'de duvar: kopuk
        self.assertEqual(start_bagli(h, (3.0, 0.0)), 0)
        iz[:, 40] = 0
        iz[:27, 40] = 100
        iz[33:, 40] = 100                                # 0,30 m'lik aralık: 0,25 m şişirmeyle kapanır
        self.assertEqual(start_bagli(h, (3.0, 0.0)), 0)
        self.assertEqual(start_bagli(h, (3.0, 0.0), r_m=0.10), 1)


if __name__ == "__main__":
    unittest.main()
