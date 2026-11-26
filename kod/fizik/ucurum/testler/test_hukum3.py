"""Bağımsız hüküm 3: yeni sahneler (yalnız ekleme), eğik yarık hakemi, görev listesi (ön kayıt sayıları, eşli düzenler)."""
import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucurum import sahne as S  # noqa: E402


class TestHukum3Sahne(unittest.TestCase):
    def test_egik_phi0_dik_ile_ayni(self):
        u, d = S.egik_yarik(0.12, 1.0, 0.0), S.acik(0.12, L=1.0)
        rng = random.Random(3)
        for _ in range(3000):
            x, y = rng.uniform(15.5, 17.5), rng.uniform(14.6, 15.4)
            self.assertAlmostEqual(S.pay(u["kenarlar"], x, y), S.pay(d["kenarlar"], x, y), places=12)

    def test_egik_dondurulmus_pay(self):
        u = S.al("h3_egik_125_35")
        _, cx, cy, phi, hx, hy = u["kenarlar"][0]
        self.assertAlmostEqual(S.pay(u["kenarlar"], cx, cy), -hy, places=12)
        ux, uy = math.cos(phi), math.sin(phi)
        # eksen ucunun 1 cm ötesi dışarıda, 1 cm berisi içeride
        self.assertAlmostEqual(S.pay(u["kenarlar"], cx + ux * (hx + 0.01), cy + uy * (hx + 0.01)), 0.01, places=9)
        self.assertLess(S.pay(u["kenarlar"], cx + ux * (hx - 0.01), cy + uy * (hx - 0.01)), 0.0)
        # deliğin en yakın köşesi x = E'de
        xs = [cx + a * hx * ux - b * hy * uy for a in (-1, 1) for b in (-1, 1)]
        self.assertAlmostEqual(min(xs), S.E, places=9)

    def test_yeni_sahneler_eski_adlarla_cakismaz(self):
        yeni = [a for a in S.SAHNELER if a.startswith("h3_")]
        self.assertEqual(len(yeni), 53)
        for a in yeni:
            u = S.al(a)
            self.assertEqual(u["ad"], a)
            self.assertTrue(u["kutular"])

    def test_gorev_listesi(self):
        from ucurum import hukum3
        G = hukum3.gorevler()
        self.assertEqual(len(G), 16635)
        self.assertEqual(len({g["kimlik"] for g in G}), len(G))
        self.assertTrue(all(211 <= g["tohum"] <= 220 for g in G))
        self.assertTrue(all(g["sahne"].startswith("h3_") for g in G))
        tab = {}
        for g in G:
            tab.setdefault(g["taban"], set()).add(json_key(g))
        self.assertTrue(all(len(v) == 1 for v in tab.values()))     # beş düzende aynı sahne / senaryo / tohum


def json_key(g):
    import json
    return json.dumps([g["alt"], g["sahne"], g["senaryo"], g["tohum"], g.get("yok")], sort_keys=True)


if __name__ == "__main__":
    unittest.main()
