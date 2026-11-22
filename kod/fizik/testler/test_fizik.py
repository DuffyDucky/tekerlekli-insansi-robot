"""Y0f fizik testleri: modelin CAD ile tutarlılığı, el hesabıyla karşılaştırma, protokol üstünden fizik, belirlenimcilik.

`kod/fizik/kos_fizik.py` koşturur (2B koşucusu `kod/testler/kos.py` bu klasörü görmez). mujoco yoksa hepsi "atlandı".
Sınırlar el hesabına göre konmuştur; tutmazsa ya model ya el hesabı değişmiştir: ikisine de bak.
"""

import json
import math
import os
import sys
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(BURASI)
KOD = os.path.dirname(FIZIK)
KOK = os.path.dirname(KOD)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import dunya as D  # noqa: E402

FIZIK_YOK = "fizik bağımlılığı (mujoco) yok: atlandı (%s)" % (D.FIZIK_HATA,)
fizik_gerekli = unittest.skipUnless(D.FIZIK_VAR, FIZIK_YOK)


def oku(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


@fizik_gerekli
class Model(unittest.TestCase):
    def test_kutle_ve_am_cad_ile_ayni(self):
        """Dayanak: tasarim/freecad/montaj/montaj-analiz.json toplam + taban-analiz.json kablo_payi (400 g, TAHMİN)."""
        w = D.FizikDunya(None, None, (0, 0, 0))
        k = oku(os.path.join(FIZIK, "model", "kutle_karsilastirma.json"))
        ta = oku(os.path.join(KOK, "tasarim", "freecad", "taban", "taban-analiz.json"))
        self.assertAlmostEqual(float(sum(w.m.body_mass)), k["model"]["kutle_kg"], places=4)
        ev = next(p for p in ta["robot"]["pozlar"] if p["kod"] == "ev")
        am = w.am()
        cad = [ev["am"][2] / 1000.0, ev["am"][0] / 1000.0, ev["am"][1] / 1000.0]   # CAD (X, Y, Z) -> robot (x=Z, y=X, z=Y)
        for i in range(3):
            self.assertAlmostEqual(am[i], cad[i], delta=0.0005)

    def test_statik_aks_yukleri_el_hesabi(self):
        """Dayanak: taban-analiz.json aks (ön 121,6 N, arka 136,2 N)."""
        w = D.FizikDunya(None, None, (0, 0, 0))
        w.adim(0.5)
        N = w.teker_yukleri()
        ta = oku(os.path.join(KOK, "tasarim", "freecad", "taban", "taban-analiz.json"))["aks"]
        self.assertAlmostEqual(N[0] + N[2], ta["on_N"], delta=1.0)
        self.assertAlmostEqual(N[1] + N[3], ta["arka_N"], delta=1.0)

    def test_statik_devrilme_egimi_ileri_el_hesabi(self):
        """El hesabı atan(d_on / h) = atan(195,5 / 520,5) = 20,6 derece; fizik (tekerler kilitli, yerçekimi eğik) ±0,5."""
        G = 9.81
        w = D.FizikDunya(None, None, (0, 0, 0), degis={"teker_zemin_surtunme": 1.5})
        for dof in w.teker_dof:
            w.m.dof_damping[dof] = 1e5
        for aci, devrik in ((20.0, False), (21.2, True)):
            th = math.radians(aci)
            w.m.opt.gravity[:] = (G * math.sin(th), 0.0, -G * math.cos(th))
            w.adim(1.0)
            self.assertEqual(w.egim() > math.radians(0.5), devrik, "eğim %.1f" % aci)


@fizik_gerekli
class ProtokolUstunden(unittest.TestCase):
    def _deney(self, **k):
        import olcumler
        return olcumler.Deney(**k)

    def test_enkoder_fizikteki_teker_acisindan(self):
        """Protokol odo'su (tik) fizikteki ön teker dönüşünü izler; düz sürüşte kaymasız: tik yolu = taban yolu ±%1."""
        dn = self._deney()
        dn.devreye_al()
        x0 = dn.c.x
        dn.e.sur_tut(0.5, 0.0, 2000)
        dn.e.istek({"k": "dur"})
        dn.e.bekle(800)
        yol = dn.c.x - x0
        tik = sum(dn.c.tik) / 2.0
        yol_tik = tik / dn.c.tik_tur * math.pi * dn.c.teker_capi
        self.assertGreater(yol, 0.3)
        self.assertAlmostEqual(yol_tik / yol, 1.0, delta=0.01)

    def test_acil_stop_bosta_kayarak_durur(self):
        """Acil stop EN LOW (boşta): fren yok, robot dişli sürtünmesi + yuvarlanma direnciyle durur (0,05-0,6 m)."""
        dn = self._deney()
        dn.devreye_al()
        dn.e.sur_tut(1.0, 0.0, 2500)
        x0 = dn.c.x
        dn.c.mantar = True
        dn.e.bekle(4000)
        yol = dn.c.x - x0
        self.assertEqual(dn.c.hakem()["guc"], "ariza")            # mantar: arızaya geçer, neden acil_stop
        self.assertTrue(0.05 < yol < 0.6, yol)
        self.assertLess(abs(dn.w.hiz()[0]), 0.002)

    def test_belirlenimci(self):
        """Aynı girdi iki kez: aynı son konum (bit düzeyinde)."""
        sonuc = []
        for _ in range(2):
            dn = self._deney()
            dn.devreye_al()
            dn.e.sur_tut(0.4, 0.3, 1500)
            dn.e.istek({"k": "dur"})
            dn.e.bekle(500)
            sonuc.append(tuple(dn.w.d.qpos))
        self.assertEqual(sonuc[0], sonuc[1])


if __name__ == "__main__":
    unittest.main()
