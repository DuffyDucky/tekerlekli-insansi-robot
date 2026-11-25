"""sanalray birim testleri.

    %V% -m unittest sanalray.testler.test_sanalray -v        (cd kod\\fizik)

Saf testler numpy ister; görüntü / fizik testleri mujoco + cv2 yoksa atlanır."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sanalray import _yol  # noqa: E402,F401

try:
    import numpy as np  # noqa: F401
    NUMPY = True
except ImportError:
    NUMPY = False
try:
    import cv2  # noqa: F401
    import mujoco  # noqa: F401
    GORUNTU = True
except ImportError:
    GORUNTU = False


@unittest.skipUnless(NUMPY, "numpy yok")
class TestKonum(unittest.TestCase):
    def setUp(self):
        from sanalray.konum import EtiketEKF
        self.E = {1: dict(x=5.0, y=1.0, yaw=math.pi, boy_m=0.15), 2: dict(x=3.0, y=-1.0, yaw=math.pi / 2, boy_m=0.15)}
        self.f = EtiketEKF(self.E)

    def _olcum(self, poz, k, phi=0.0):
        from sanalray.konum import KAMERA_X, sar
        x, y, th = poz
        cx, cy = x + KAMERA_X * math.cos(th + phi), y + KAMERA_X * math.sin(th + phi)
        e = self.E[k]
        r = math.hypot(e["x"] - cx, e["y"] - cy)
        b = sar(math.atan2(e["y"] - cy, e["x"] - cx) - th - phi)
        psi = sar(e["yaw"] - th - phi)
        return r, b, psi

    def test_tahmin_belirsizligi_buyutur_olcum_kucultur(self):
        self.f.baslat((0.0, 0.0, 0.0), std=(0.05, 0.05, 0.02))
        s0 = self.f.std()[0]
        for _ in range(100):
            self.f.tahmin((0.05, 0.0, 0.0))
        s1 = self.f.std()[0]
        self.assertGreater(s1, s0)
        gercek = (5.0 - 0.0, 0.0, 0.0)
        del gercek
        self.f.olcum(1, *self._olcum(self.f.govde(), 1))
        self.assertLess(self.f.std()[0], s1)

    def test_tek_etiketten_poz_tersi(self):
        for poz in ((1.0, 0.5, 0.2), (2.0, -0.3, -0.4)):
            for phi in (0.0, 0.6):
                p = self.f.tek_etiketten(1, *self._olcum(poz, 1, phi), phi=phi)
                self.assertAlmostEqual(p[0], poz[0], places=6)
                self.assertAlmostEqual(p[1], poz[1], places=6)
                self.assertAlmostEqual(p[2], poz[2], places=6)

    def test_yanlis_poz_olcumle_duzelir_ve_donus_olcegi_ogrenilir(self):
        # gerçek dönüş = 0,8 x odometri (odometri %25 fazla); süzgeç ölçekten haberdar değil, etiketle öğrenir
        from sanalray.konum import XR
        th = 0.0                                   # arka dingil (0, 0)'da yerinde döner; gövde merkezi 0,185 m önünde
        self.f.baslat((-XR, 0.0, 0.0), std=(0.05, 0.05, 0.02))
        for i in range(200):
            dth_o = 0.02 if i % 40 < 20 else -0.02
            th += 0.8 * dth_o
            self.f.tahmin((0.0, 0.0, dth_o))
            gx, gy = -XR * math.cos(th), -XR * math.sin(th)
            gercek = [gx, gy, th]
            for k in (1, 2):
                self.f.olcum(k, *self._olcum(tuple(gercek), k))
        self.assertAlmostEqual(self.f.olcek(), 0.8, delta=0.05)

    def test_kapi_uzak_olcumu_reddeder(self):
        self.f.baslat((0.0, 0.0, 0.0), std=(0.02, 0.02, 0.01))
        # etiket 2 ≈ 3,1 m: ölçülen 4,1 m'de menzil std 0,22 m, 1 m sapma d2 ≈ 20 > 13,8
        r2, b2, psi2 = self._olcum((0.0, 0.0, 0.0), 2)
        self.assertEqual(self.f.olcum(2, r2 + 1.0, b2, psi2), "ret")
        r, b, psi = self._olcum((0.0, 0.0, 0.0), 1)
        self.assertEqual(self.f.olcum(1, r, b + math.radians(5), psi), "ret")
        self.assertEqual(self.f.olcum(99, r, b, psi), "bilinmeyen")


@unittest.skipUnless(NUMPY, "numpy yok")
class TestPlan(unittest.TestCase):
    def test_planlar_tekil_kimlik_ve_duvarda(self):
        from sanalray import etiket as E
        from sanalray.etiket import _harita
        tum = set()
        for kor in ("koridor_%d" % i for i in range(1, 7)):
            for ar in ("kavsak", 5):
                p = E.plan_uret(kor, ar, 0.15, "goz")
                h = _harita(kor)
                for e in p["etiketler"]:
                    # yüz normalinin tersine 2 cm içinde duvar var
                    r = h.isin(e["x"] + 0.05 * math.cos(e["yaw"]), e["y"] + 0.05 * math.sin(e["yaw"]), e["yaw"] + math.pi, 0.2)
                    self.assertIsNotNone(r, (kor, e))
                    self.assertLess(r[0], 0.06)
                ids = [e["id"] for e in p["etiketler"]]
                self.assertEqual(len(ids), len(set(ids)))
                if ar == 5:
                    self.assertFalse(tum & set(ids))
                    tum |= set(ids)
            self.assertGreaterEqual(E.plan_uret(kor, "kavsak")["sayi"], 2)


@unittest.skipUnless(GORUNTU, "mujoco / cv2 yok")
class TestGoruntu(unittest.TestCase):
    def test_etiket_karsidan_2m_algilanir(self):
        import mujoco
        from sanalray import gorunurluk as G, kamera as KM
        xml, e = G.sahne_xml(0.15, 1.55)
        m = mujoco.MjModel.from_xml_string(xml)
        d = mujoco.MjData(m)
        kam = KM.Kamera(m, d, "std", 1152, 648, kamera="c")
        G.kamera_koy(m, d, kam.cam, 2.0, 0.0, math.pi)
        g = kam.gri()
        kam.kapat()
        b = KM.Bulucu()
        s = b.bul(g)
        self.assertEqual([k for k, _ in s], [1])
        r, br, psi = KM.olcum_2b(*b.poz(s[0][1], 0.15, kam.K))
        self.assertLess(abs(r - 2.0), 0.03)
        self.assertLess(abs(br), math.radians(0.5))

    def test_etiketler_fizigi_degistirmez(self):
        from gezinme.duzenek import Duzenek
        from sanalray import etiket as E

        class Sur:
            def adim(self, t, tarama, artim):
                return 0.25, 0.3

            def durum(self):
                return {}
        son = []
        for etiketli in (False, True):
            if etiketli:
                s = E.etiketli_sahne("koridor_2", E.plan_uret("koridor_2", 5))
            else:
                E.kur()
                E.varlik_ayarla(None)
                s = "koridor_2"
            dz = Duzenek(s, tohum=0)
            dz.lidar.ayir()
            dz.kos(Sur(), 3.0)
            son.append(dz.gercek_poz())
        self.assertEqual(son[0], son[1])


class TestRapor(unittest.TestCase):
    def test_kayip_tablosu_ilk_etiket_ve_konumlanma_ayri(self):
        """İlk etiket görülmesi (ilk_etiket_s) ile konumlanma (lokalize_s) ayrı sütunlarda, doğru başlıkla."""
        from sanalray import rapor
        satir = [dict(kume="sinama", kafa="sabit", koridor="koridor_2", basari=True, ilk_etiket_s=0.5, lokalize_s=4.0,
                      lokalize_yol_m=0.2, sure_s=50.0, varis_hatasi_m=0.1, karar_koridor="koridor_2", temas_olay=0)]
        bas, _, veri = rapor.kayip_tablo(satir).splitlines()
        sut = [x.strip() for x in bas.strip("|").split("|")]
        hucre = [x.strip() for x in veri.strip("|").split("|")]
        self.assertEqual(len(sut), len(hucre))
        self.assertEqual(hucre[sut.index("ilk etiket görülme ort / en (s)")], "0,5 / 0,5")
        self.assertEqual(hucre[sut.index("konumlanma süresi ort / en (s)")], "4,0 / 4,0")
        self.assertFalse(any("ilk etikete" in s for s in sut))


if __name__ == "__main__":
    unittest.main()
