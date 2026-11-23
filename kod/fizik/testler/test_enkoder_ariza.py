"""Öneri firmware (dal oneri/donus-omni, VARSAYIM ONERI) enkoder arızası koruması: çalışırken takılan / ters bağlı enkoder.

Dayanak: Y0f-kontrol.md § 12.1 F1 (B: korumasız öneride v 0,10 komutu 0,39 m/s'ye, tek yan takılıyken robot kendiliğinden
döner). Koruma: motorlar.cpp DUZELTME_ORANI / DUZELTME_TABANI (PI düzeltme payı) + KUSKU_HIZ_M_S / KUSKU_SURE_MS (makullük;
o teker açık çevrime düşer). Her durum korumasız (kaçıyor) ve korumalı (kaçmıyor) koşulur. Sağlam enkoderli robot 1 s
v 0,10 ile gider, sonra arıza başlar, 3 s daha aynı komut. V0 (bugünkü firmware) bu testlerde yok.
"""

import math
import os
import sys
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(BURASI)
KOD = os.path.dirname(FIZIK)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import dunya as D  # noqa: E402

V_KOMUT = 0.10


def kos(var, bozuk):
    import olcumler as O
    dn = O.Deney(varyant=var)
    dn.devreye_al()
    dn.e.sur_tut(V_KOMUT, 0.0, 1000)
    t_ariza = dn.c.ms
    dn.c.enkoder_bozuk = list(bozuk)
    x0, y0, _, a0, _, _ = dn.w.poz()
    dn.e.sur_tut(V_KOMUT, 0.0, 2000)
    x1, y1, _, a1, _, _ = dn.w.poz()
    dn.e.sur_tut(V_KOMUT, 0.0, 1000)
    x2, y2, _, a2, _, _ = dn.w.poz()
    o = dn.c._oneri
    return dict(yol_m=math.hypot(x2 - x0, y2 - y0), v_son=math.hypot(x2 - x1, y2 - y1), aci_derece=math.degrees(a2 - a0),
                arizali=list(o["arizali"]),
                tespit_ms=[None if m is None else m - t_ariza for m in o["ariza_ms"]])


class EnkoderArizasi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not D.FIZIK_VAR:
            raise unittest.SkipTest("fizik bağımlılığı (mujoco) yok: atlandı (%s)" % (D.FIZIK_HATA,))
        import varyantlar as VR
        ad = os.environ.get("LALE_VARYANT") or "ONERI"     # öbür öneri varyantları için (ör. ONERI-MAKARA); fw_oneri şart
        cls.korumali = VR.al(ad)
        if not (cls.korumali and cls.korumali.get("fw_oneri")):
            raise unittest.SkipTest("%s öneri firmware'li değil" % ad)
        cls.korumasiz = dict(cls.korumali, fw_oneri=dict(cls.korumali["fw_oneri"], duzeltme_orani=None))

    def _ikisi(self, bozuk):
        once, sonra = kos(self.korumasiz, bozuk), kos(self.korumali, bozuk)
        print("\n  %s korumasız: 3 s yol %.2f m, son 1 s %.3f m, açı %+.1f° | korumalı: son 1 s %.3f m, açı %+.1f°, yol %.2f m, tespit %s ms"
              % (bozuk, once["yol_m"], once["v_son"], once["aci_derece"], sonra["v_son"], sonra["aci_derece"], sonra["yol_m"],
                 sonra["tespit_ms"]), end="")
        return once, sonra

    def test_saglam_enkoderde_alarm_yok(self):
        r = kos(self.korumali, (None, None))
        self.assertEqual(r["arizali"], [False, False])
        self.assertAlmostEqual(r["v_son"], V_KOMUT, delta=0.02)

    def test_iki_yan_takili(self):
        once, sonra = self._ikisi(("takili", "takili"))
        self.assertGreater(once["v_son"], 0.3, "korumasız öneri kaçmalıydı (B: 0,396 m/s)")
        self.assertEqual(sonra["arizali"], [True, True])
        self.assertLess(max(sonra["tespit_ms"]), 1000)
        self.assertLess(sonra["v_son"], 0.15)

    def test_iki_yan_ters_bagli(self):
        once, sonra = self._ikisi(("ters", "ters"))
        self.assertGreater(once["v_son"], 0.3, "korumasız öneri kaçmalıydı (B: 0,394 m/s)")
        self.assertEqual(sonra["arizali"], [True, True])
        self.assertLess(max(sonra["tespit_ms"]), 1000)
        self.assertLess(sonra["v_son"], 0.15)

    def test_tek_yan_takili(self):
        once, sonra = self._ikisi(("takili", None))
        self.assertGreater(abs(once["aci_derece"]), 30.0, "korumasız öneri kendiliğinden dönmeliydi (B: w −0,50)")
        self.assertEqual(sonra["arizali"], [True, False])
        self.assertLess(sonra["tespit_ms"][0], 1000)
        self.assertLess(abs(sonra["aci_derece"]), 10.0)
        self.assertLess(sonra["v_son"], 0.15)


if __name__ == "__main__":
    unittest.main()
