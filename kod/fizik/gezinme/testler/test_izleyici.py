"""YolIzleyici ve on_mesafe_hesapla birim testleri (MuJoCo'suz; yalnız standart kitaplık).

Benzetim: dönme merkezi arka dingilde (gövde merkezinin 0,185 m gerisi) tek tekerlekli robot; komut birinci dereceden
gecikmeyle izlenir (τ 0,15 s), dönüş komutun %89'u (ONERI ölçümü), ileri hız tam."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from gezinme.izleyici import IzleyiciAyar, Komut, YolIzleyici, on_mesafe_hesapla, sar  # noqa: E402

XR = -0.185


class Robot:
    def __init__(self, x, y, th, w_olcek=0.89, tau=0.15):
        self.x, self.y, self.th = x, y, th
        self.v = self.w = 0.0
        self.w_olcek, self.tau = w_olcek, tau

    def adim(self, v, w, dt):
        k = min(1.0, dt / self.tau)
        self.v += (v - self.v) * k
        self.w += (w * self.w_olcek - self.w) * k
        rx, ry = self.x + XR * math.cos(self.th), self.y + XR * math.sin(self.th)
        rx += self.v * math.cos(self.th) * dt
        ry += self.v * math.sin(self.th) * dt
        self.th = sar(self.th + self.w * dt)
        self.x, self.y = rx - XR * math.cos(self.th), ry - XR * math.sin(self.th)

    @property
    def poz(self):
        return (self.x, self.y, self.th)


def kos(iz, r, sure=120.0, dt=0.05, on=None, alt=5):
    """İzleyiciyi benzetimde koştur. on(t, robot) -> on_mesafe. Döner: (komutlar, izler)."""
    komutlar, izler = [], []
    t = 0.0
    while t < sure:
        k = iz.komut(r.poz, on(t, r) if on else None)
        komutlar.append((t, k))
        for _ in range(alt):
            r.adim(k.v, k.w, dt / alt)
        izler.append((t, r.x, r.y, r.th))
        t += dt
        if k.bitti:
            break
    return komutlar, izler


def yola_uzaklik(P, x, y):
    en = 1e9
    for a, b in zip(P, P[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
        en = min(en, math.hypot(a[0] + t * dx - x, a[1] + t * dy - y))
    return en


class Izleyici(unittest.TestCase):
    def test_duz_yol_varir_asmadan(self):
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver([(0.0, 0.0), (5.0, 0.0)])
        k, izler = kos(iz, r)
        self.assertTrue(k[-1][1].bitti)
        self.assertLess(math.hypot(r.x - 5.0, r.y), 0.12)
        self.assertLess(max(x for _, x, _, _ in izler), 5.0 + 0.05)          # aşma yok
        self.assertLess(max(abs(y) for _, _, y, _ in izler), 0.01)
        self.assertGreater(max(c.v for _, c in k), 0.24)                      # seyir hızına çıktı

    def test_ivme_ve_hiz_siniri(self):
        a = IzleyiciAyar(v_max=0.3, a_max=0.5, dt_s=0.05)
        iz = YolIzleyici(a)
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver([(0.0, 0.0), (4.0, 0.0)])
        k, _ = kos(iz, r)
        vs = [c.v for _, c in k]
        self.assertLessEqual(max(vs), 0.3 + 1e-9)
        artis = max(b - a_ for a_, b in zip(vs, vs[1:]))
        self.assertLessEqual(artis, 0.5 * 0.05 + 1e-9)
        self.assertLessEqual(max(abs(c.w) for _, c in k), 1.0 + 1e-9)

    def test_l_kose_yerinde_doner_ve_yolda_kalir(self):
        P = [(0.0, 0.0), (4.0, 0.0), (4.0, 3.0)]
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver(P)
        k, izler = kos(iz, r)
        self.assertTrue(k[-1][1].bitti)
        self.assertLess(math.hypot(r.x - 4.0, r.y - 3.0), 0.12)
        self.assertIn("yerinde", {c.mod for _, c in k})
        # dönme merkezi yol üstünde kalır (gövde merkezi yerinde dönüşte 0,185 m yarıçapla oynar)
        sapma = max(yola_uzaklik([(-1.0, 0.0)] + P, x + XR * math.cos(th), y + XR * math.sin(th)) for _, x, y, th in izler)
        self.assertLess(sapma, 0.10)

    def test_u_donusu(self):
        P = [(0.0, 0.0), (3.0, 0.0), (0.5, 0.0)]
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver(P)
        k, izler = kos(iz, r)
        self.assertTrue(k[-1][1].bitti)
        self.assertLess(math.hypot(r.x - 0.5, r.y), 0.12)
        self.assertLess(max(abs(y) for _, _, y, _ in izler), 0.25)

    def test_ters_yonde_baslarsa_once_yerinde_doner(self):
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, math.pi)
        iz.yol_ver([(0.0, 0.0), (3.0, 0.0)])
        k, _ = kos(iz, r)
        self.assertEqual(k[0][1].mod, "yerinde")
        self.assertEqual(k[0][1].v, 0.0)
        self.assertTrue(k[-1][1].bitti)
        self.assertLess(math.hypot(r.x - 3.0, r.y), 0.15)

    def test_engelde_durur_bekler_kalkar(self):
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver([(0.0, 0.0), (6.0, 0.0)])
        # 2-6 s arası önde 0,2 m engel (dur mesafesi 0,30)
        k, izler = kos(iz, r, on=lambda t, rb: 0.2 if 2.0 <= t < 6.0 else None)
        bekleyen = [c for t, c in k if 2.0 <= t < 6.0]
        self.assertTrue(all(c.durdu and c.v == 0.0 and c.w == 0.0 for c in bekleyen))
        self.assertTrue(k[-1][1].bitti)
        self.assertFalse(k[-1][1].durdu)

    def test_engel_yaklasinca_yavaslar(self):
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver([(0.0, 0.0), (10.0, 0.0)])
        k, _ = kos(iz, r, sure=6.0, on=lambda t, rb: 0.5 if t > 3.0 else None)
        son = [c for t, c in k if t > 4.0]
        self.assertTrue(all(c.v <= 0.25 * (0.5 - 0.3) / 0.5 + 1e-6 for c in son))
        self.assertTrue(all(not c.durdu for c in son))

    def test_yeni_yol_eskiyi_degistirir(self):
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        iz.yol_ver([(0.0, 0.0), (10.0, 0.0)])
        kos(iz, r, sure=4.0)
        iz.yol_ver([(r.x, r.y), (r.x, r.y + 2.0)])
        k, _ = kos(iz, r)
        self.assertTrue(k[-1][1].bitti)
        self.assertLess(math.hypot(r.y - 2.0, 0.0), 0.15)

    def test_bos_ve_tek_nokta(self):
        iz = YolIzleyici()
        k = iz.komut((0.0, 0.0, 0.0))
        self.assertIsInstance(k, Komut)
        self.assertTrue(k.bitti)
        self.assertEqual((k.v, k.w), (0.0, 0.0))
        iz.yol_ver([(2.0, 1.0)])
        r = Robot(0.0, 0.0, 0.0)
        k, _ = kos(iz, r)
        self.assertTrue(k[-1][1].bitti)
        self.assertLess(math.hypot(r.x - 2.0, r.y - 1.0), 0.15)

    def test_kucuk_poz_gurultusunde_kararli(self):
        import random
        rng = random.Random(3)
        iz = YolIzleyici()
        r = Robot(0.0, 0.0, 0.0)
        P = [(0.0, 0.0), (6.0, 0.0), (6.0, 4.0)]
        iz.yol_ver(P)
        t = 0.0
        while t < 120:
            p = (r.x + rng.gauss(0, 0.02), r.y + rng.gauss(0, 0.02), r.th + rng.gauss(0, 0.01))
            k = iz.komut(p)
            for _ in range(5):
                r.adim(k.v, k.w, 0.01)
            t += 0.05
            if k.bitti:
                break
        self.assertTrue(k.bitti)
        self.assertLess(math.hypot(r.x - 6.0, r.y - 4.0), 0.2)


class OnMesafe(unittest.TestCase):
    def _tarama(self, fn, n=500):
        acilar = [-math.pi + i * 2 * math.pi / n for i in range(n)]
        return {"t": 0.0, "acilar": acilar, "mesafeler": [fn(a) for a in acilar]}

    def test_ondeki_duvar(self):
        # LiDAR x 0,19'da; gövde çerçevesinde x = 1,5'te dik duvar
        def f(a):
            c = math.cos(a)
            return (1.5 - 0.19) / c if c > 0.05 else float("nan")
        d = on_mesafe_hesapla(self._tarama(f), 0.6, montaj=(0.19, 0.0))
        self.assertAlmostEqual(d, 1.5 - 0.2642, places=6)

    def test_serit_disi_sayilmaz_nan_ve_none(self):
        # yalnız sağda 0,5 m yanda duvar (y = -0,5): genişlik 0,6 şeridinde değil
        def f(a):
            s = math.sin(a)
            return 0.5 / -s if s < -0.05 else None
        self.assertEqual(on_mesafe_hesapla(self._tarama(f), 0.6, montaj=(0.19, 0.0)), math.inf)
        self.assertIsNone(on_mesafe_hesapla(None, 0.6))
        self.assertEqual(on_mesafe_hesapla(self._tarama(lambda a: float("nan")), 0.6), math.inf)

    def test_genis_seritte_yan_duvar_gorunur(self):
        def f(a):
            s = math.sin(a)
            return 0.5 / -s if s < -0.05 else None
        d = on_mesafe_hesapla(self._tarama(f), 1.2, montaj=(0.19, 0.0))
        self.assertLess(d, 4.0)


if __name__ == "__main__":
    unittest.main()
