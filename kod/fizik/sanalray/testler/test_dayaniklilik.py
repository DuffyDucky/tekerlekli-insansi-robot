"""Dayanıklılık turu testleri (kusur modeli, doğrulamalı başlatma, yanal sapma ölçütü).

    %V% -m unittest sanalray.testler.test_dayaniklilik -v        (cd kod\\fizik)

Saf testler numpy (başlatma testi ayrıca cv2) ister; yoksa atlanır. MuJoCo gerekmez."""

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
    CV2 = True
except ImportError:
    CV2 = False


def _plan():
    return dict(koridor="koridor_2", sayi=3, etiketler=[
        dict(id=50, x=1.0, y=0.0, z=1.55, yaw=math.pi / 2, boy_m=0.15),
        dict(id=51, x=3.0, y=2.0, z=1.55, yaw=-math.pi / 2, boy_m=0.15),
        dict(id=52, x=5.0, y=0.0, z=1.55, yaw=math.pi / 2, boy_m=0.15)])


@unittest.skipUnless(NUMPY, "numpy yok")
class TestKusurPlan(unittest.TestCase):
    def test_sifir_kusur_plan_ayni(self):
        from sanalray import kusur as KU
        p = _plan()
        pg, bilgi = KU.gercek_plan(p, KU.kusur_tam({}), KU.Cekilis(1, [50, 51, 52]))
        self.assertEqual(pg["etiketler"], p["etiketler"])
        self.assertEqual(bilgi, dict(kayip=[], yanlis=[], yirtik={}))

    def test_konum_hatasi_duvar_boyunca_ve_duzeyle_olceklenir(self):
        from sanalray import kusur as KU
        p = _plan()
        cek = KU.Cekilis(3, [50, 51, 52])
        g1, _ = KU.gercek_plan(p, KU.kusur_tam(dict(harita_konum_m=0.01)), cek)
        g5, _ = KU.gercek_plan(p, KU.kusur_tam(dict(harita_konum_m=0.05)), cek)
        for e, a, b in zip(p["etiketler"], g1["etiketler"], g5["etiketler"]):
            n = (math.cos(e["yaw"]), math.sin(e["yaw"]))
            d1 = (a["x"] - e["x"], a["y"] - e["y"])
            d5 = (b["x"] - e["x"], b["y"] - e["y"])
            self.assertAlmostEqual(d1[0] * n[0] + d1[1] * n[1], 0.0, places=9)     # duvara dik hata yok
            self.assertLessEqual(math.hypot(*d5), 0.05 + 1e-9)
            self.assertAlmostEqual(math.hypot(*d5), 5 * math.hypot(*d1), places=9)  # aynı yön, 5 kat
            self.assertLessEqual(abs(b["z"] - e["z"]), 0.05 + 1e-9)

    def test_aci_hatasi_sinirli_ve_kayip_etiket_cikar(self):
        from sanalray import kusur as KU
        p = _plan()
        g, bilgi = KU.gercek_plan(p, KU.kusur_tam(dict(harita_aci_derece=5.0, kayip_etiket=1)), KU.Cekilis(2, [50, 51, 52]))
        self.assertEqual(len(g["etiketler"]), 2)
        self.assertEqual(len(bilgi["kayip"]), 1)
        self.assertNotIn(bilgi["kayip"][0], [e["id"] for e in g["etiketler"]])
        for e in g["etiketler"]:
            e0 = next(x for x in p["etiketler"] if x["id"] == e["id"])
            self.assertLessEqual(abs(e["yaw"] - e0["yaw"]), math.radians(5.0) + 1e-9)

    def test_bilinmeyen_kusur_reddedilir(self):
        from sanalray import kusur as KU
        with self.assertRaises(ValueError):
            KU.kusur_tam(dict(yok_boyle=1))

    def test_aday_butun_plan_ise_ilk_tur_secimiyle_ayni(self):
        # tamamlama turu: aday süzgeci, aday = bütün plan iken ilk turun seçimini değiştirmemeli
        from sanalray import kusur as KU
        p = _plan()
        ku = KU.kusur_tam(dict(kayip_etiket=1, yirtik_oran=0.34))
        for tohum in range(1, 15):
            cek = KU.Cekilis(tohum, [50, 51, 52])
            a = KU.gercek_plan(p, ku, cek)
            b = KU.gercek_plan(p, ku, cek, aday=[52, 50, 51])
            self.assertEqual(a, b)

    def test_eksik_etiket_yalniz_adaydan_secilir(self):
        from sanalray import kusur as KU
        p = _plan()
        ku = KU.kusur_tam(dict(kayip_etiket=1, yirtik_oran=0.34))
        for tohum in range(1, 15):
            cek = KU.Cekilis(tohum, [50, 51, 52])
            g, bilgi = KU.gercek_plan(p, ku, cek, aday=[51])
            self.assertEqual(bilgi["kayip"], [51])
            self.assertNotIn(51, bilgi["yirtik"])                                 # eksik etiket yırtık sayılmaz
            ky = KU.kusur_tam(dict(yirtik_oran=0.34))
            self.assertEqual(KU.gercek_plan(p, ky, cek, aday=[51])[1], KU.gercek_plan(p, ky, cek)[1])  # yalnız yırtık: aday etkisiz
        _, bilgi = KU.gercek_plan(p, ku, KU.Cekilis(1, [50, 51, 52]), aday=[52, 50], aday_sirali=True)
        self.assertEqual(bilgi["kayip"], [52])                                     # "kritik": listenin ilki


def _satir(kor, tohum, varis, olcum=10):
    return dict(koridor=kor, tohum=tohum, varis_hatasi_m=varis, etiket_olcum=olcum, etiket_ret=0, sure_s=50.0,
                en_yanal_sapma_m=0.1)


class TestEtkisiz(unittest.TestCase):
    def test_temizle_ayni_kosu_etkisiz_sayilir(self):
        from sanalray import dayaniklilik as DA
        temiz = [_satir("koridor_2", 1, 0.1), _satir("koridor_4", 1, 0.2)]
        r = [_satir("koridor_2", 1, 0.1), _satir("koridor_4", 1, 0.2, olcum=9)]
        etkili, etkisiz = DA.etkisiz_say(r, temiz)
        self.assertEqual([s["koridor"] for s in etkisiz], ["koridor_2"])
        self.assertEqual([s["koridor"] for s in etkili], ["koridor_4"])


class _SahteHarita:
    """x = 10 m'de dikey tek duvar (normal -x)."""

    def isin(self, x, y, aci, en_cok):
        c = math.cos(aci)
        if c <= 1e-9:
            return None
        d = (10.0 - x) / c
        if d <= 0 or d > en_cok:
            return None
        return d, abs(aci)


@unittest.skipUnless(NUMPY and CV2, "numpy / cv2 yok")
class TestDogrulamaliBaslatma(unittest.TestCase):
    def _beyin(self):
        from sanalray.beyin import SanalRayBeyni
        from sanalray.kamera import ic_parametre
        E = {50: dict(x=10.0, y=0.0, z=1.55, yaw=math.pi, boy_m=0.15, koridor="koridor_2")}
        return SanalRayBeyni(E, ic_parametre("std", 1152, 648), gorev="kayip", hedef="kapi_1", baslatma="dogrulamali",
                             harita_fn=lambda k: _SahteHarita(), durak_fn=lambda k, a: (a, (0.0, 0.0)),
                             rota_fn=lambda k, a, b: [a, b])

    def _olcum(self, poz):
        from sanalray.konum import KAMERA_X, sar
        x, y, th = poz
        cx, cy = x + KAMERA_X * math.cos(th), y + KAMERA_X * math.sin(th)
        r = math.hypot(10.0 - cx, 0.0 - cy)
        b = sar(math.atan2(0.0 - cy, 10.0 - cx) - th)
        return r, b, sar(math.pi - th)

    def test_tutarli_adaylar_ve_sonar_uyumu_baslatir(self):
        br = self._beyin()
        poz = (7.5, 0.2, 0.05)
        br.son_sonar = br.sonar_beklenen("koridor_2", poz)
        for i in range(6):
            br._aday_ekle(0.1 * i, 50, *self._olcum(poz))
        br._dogrula(1.0)
        self.assertTrue(br.ekf.hazir)
        p = br.ekf.govde()
        self.assertLess(math.hypot(p[0] - poz[0], p[1] - poz[1]), 1e-6)
        self.assertEqual(br.koridor, "koridor_2")

    def test_sonar_celiskisi_reddeder(self):
        br = self._beyin()
        poz = (7.5, 0.2, 0.05)
        br.son_sonar = br.sonar_beklenen("koridor_2", poz) + 0.8        # sonar başka bir şey görüyor
        for i in range(6):
            br._aday_ekle(0.1 * i, 50, *self._olcum(poz))
        br._dogrula(1.0)
        self.assertFalse(br.ekf.hazir)
        self.assertEqual(br.dogrulama_ret, 1)
        br._aday_ekle(1.2, 50, *self._olcum(poz))                        # bekleme süresinde aday alınmaz
        self.assertIsNone(br._dog)

    def test_tutarsiz_adaylar_reddeder(self):
        br = self._beyin()
        br.son_sonar = math.inf
        for i, poz in enumerate([(7.5, 0.2, 0.05), (7.0, -0.4, -0.2), (7.9, 0.6, 0.3), (7.2, 0.0, 0.15)]):
            br._aday_ekle(0.1 * i, 50, *self._olcum(poz))
        br._dogrula(1.0)
        self.assertFalse(br.ekf.hazir)

    def test_takilma_enkoderden_sezilir_ve_geri_cekilir(self):
        """Arama ilerle evresinde ileri komut var, enkoder ilerlemiyor (eğik duvara dayanmış, sonar yankısız)."""
        br = self._beyin()
        v = w = 0.0
        geri = False
        t = 0.0
        for _ in range(1200):
            t += 0.05
            artim = (0.0, 0.0, w * 0.05)          # dönüş işler, öteleme hiç işlemez (takılı)
            v, w = br.adim(t, artim, None, math.inf)
            if br.takilma_sayisi and v < 0:
                geri = True
                break
        self.assertTrue(geri, br.olaylar[-5:])
        self.assertGreaterEqual(br.takilma_sayisi, 1)

    def test_varsayilan_tek_dogrulamali_yola_girmez(self):
        """Regresyon: varsayılan baslatma 'tek'; aynı takılı girdide takılma denetimi, geri çekilme ve aday toplama hiç
        çalışmaz, komutlar _adim_ic ile birebir aynı (ilk sürüm davranışı)."""
        from sanalray.beyin import SanalRayBeyni
        from sanalray.kamera import ic_parametre
        E = {50: dict(x=10.0, y=0.0, z=1.55, yaw=math.pi, boy_m=0.15, koridor="koridor_2")}
        kw = dict(gorev="kayip", hedef="kapi_1", harita_fn=lambda k: _SahteHarita(),
                  durak_fn=lambda k, a: (a, (0.0, 0.0)), rota_fn=lambda k, a, b: [a, b])
        br = SanalRayBeyni(E, ic_parametre("std", 1152, 648), **kw)
        ic = SanalRayBeyni(E, ic_parametre("std", 1152, 648), **kw)
        self.assertEqual(br.baslatma, "tek")
        t, w1, w2 = 0.0, 0.0, 0.0
        for _ in range(1200):
            t += 0.05
            v1, w1 = br.adim(t, (0.0, 0.0, w1 * 0.05), None, math.inf)
            v2, w2 = ic._adim_ic(t, (0.0, 0.0, w2 * 0.05), None, math.inf)
            self.assertEqual((v1, w1), (v2, w2))
            self.assertGreaterEqual(v1, 0.0)                                  # hiç geri çekilme yok
        self.assertEqual(br.takilma_sayisi, 0)
        self.assertEqual(br._takilma, [])
        self.assertIsNone(br._dog)

    def test_egik_bakis_aday_olmaz(self):
        br = self._beyin()
        r, b, psi = self._olcum((7.5, 0.2, 0.05))
        br._aday_ekle(0.0, 50, r, b, psi + math.radians(70))
        self.assertIsNone(br._dog)


class TestYanalOlcut(unittest.TestCase):
    def test_baslangic_sapmasindan_arindirilmis(self):
        try:
            from sanalray import dayaniklilik as DY
            hk = DY._yanal_hakem((20.0, 0.0), [(0.0, 0.0), (20.0, 0.0)], type("B", (), {"ekf": type("F", (), {
                "govde": lambda self: None, "std": lambda self: None})()})())
        except ImportError as h:
            self.skipTest("gezinme yüklenemedi: %r" % h)
        x = 0.0
        t = 0.0
        while x < 10.0:
            y = 0.10 * math.exp(-x / 0.4)                  # 0,10 m başlangıç sapması, hızla söner
            hk.guncelle(t, (x, y, 0.0), False)
            x += 0.05
            t += 0.2
        self.assertAlmostEqual(hk.en_sapma, 0.10, places=6)
        self.assertAlmostEqual(hk.d0, 0.10, places=6)
        self.assertLess(hk.en_arin, 0.001)


if __name__ == "__main__":
    unittest.main()
