"""Labirent: üretici, hakem, puan birim testleri (bağımlılıksız; mujoco gerekmez).

    py -3 -m unittest discover -s kod\\fizik\\labirent\\testler -v
"""

import json
import math
import os
import sys
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(BURASI)
sys.path.insert(0, LAB)

import hakem as H  # noqa: E402

U = H.U
P = H.P
SAHNE = "labirent_5x5_t1"


def _hat_uzerinde(hat, v, dt):
    """Kırık çizgi boyunca v hızla (x, y, th) örnekleri; th parça yönü."""
    out = []
    t = 0.0
    for (ax, ay), (bx, by) in zip(hat, hat[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L < 1e-9:
            continue
        th = math.atan2(by - ay, bx - ax)
        n = max(1, int(L / (v * dt)))
        for k in range(n):
            f = k / n
            out.append((ax + (bx - ax) * f, ay + (by - ay) * f, th))
    out.append((hat[-1][0], hat[-1][1], out[-1][2]))
    return out


def _kos(hk, pozlar, dt, temas=None, t0=0.0):
    t = t0
    for i, p in enumerate(pozlar):
        hk.guncelle(t, p, bool(temas and temas(t)))
        if hk.bitti:
            break
        t += dt
    return t


class TestUretici(unittest.TestCase):
    def test_belirlenimci_ve_dosyayla_ayni(self):
        for ad, kw in U.SAHNE_AILESI.items():
            h1, s1, _ = U.sahne_kur(ad, **kw)
            h2, s2, _ = U.sahne_kur(ad, **kw)
            self.assertEqual(json.dumps(h1), json.dumps(h2))
            hd, sd = U.oku(ad)
            self.assertEqual(sd["labirent"]["hucreler"], s1["labirent"]["hucreler"], ad)
            self.assertEqual(hd["duvarlar"], h1["duvarlar"], ad)

    def test_mukemmel_cesitli(self):
        for alg in ("geri_izleme", "wilson", "agac:0.5"):
            for (r, c) in ((3, 4), (8, 5), (17, 17), (2, 9)):
                for t in (1, 2, 11):
                    lab = U.labirent_uret(r, c, t, algoritma=alg)
                    bag, muk, E = lab.mukemmel_mi()
                    self.assertTrue(bag and muk, (alg, r, c, t))
                    self.assertEqual(E, r * c - 1)
                    self.assertEqual(lab.cozum()[0], lab.start[1])
                    self.assertEqual(lab.cozum()[-1], lab.finish[1])

    def test_kenar_secimi(self):
        lab = U.labirent_uret(6, 7, 3, start=("sol", 2), finish=("sag", -1))
        self.assertEqual(lab.start[1], (2, 0))
        self.assertEqual(lab.finish[1], (5, 6))
        self.assertTrue(lab.acik[2][0] & U.B)
        self.assertTrue(lab.acik[5][6] & U.D)

    def test_duvar_birlesimi_toplam_uzunluk(self):
        """Birleştirilmiş duvar boyu = kapalı kenar sayısı x hücre."""
        _, s = U.oku("labirent_9x9_t1")
        h, _ = U.oku("labirent_9x9_t1")
        lab, yer = U.labirent_sahneden(s)
        R, C = lab.satir, lab.sutun
        kenar = 2 * (R + C) - 2 + (R - 1) * C + R * (C - 1) - lab.kenar_sayisi()
        boy = sum(math.hypot(p[2] - p[0], p[3] - p[1]) for p in h["duvarlar"])
        self.assertAlmostEqual(boy, kenar * yer.h, places=6)

    def test_start_pozu(self):
        _, s = U.oku(SAHNE)
        L = s["labirent"]
        x, y, th = L["start"]["poz"]
        (ax, ay), (bx, by) = L["start"]["cizgi"]
        n = L["start"]["ic_normal"]
        self.assertAlmostEqual((x - (ax + bx) / 2) * n[0] + (y - (ay + by) / 2) * n[1], U.START_IC_M, places=6)
        self.assertAlmostEqual(math.cos(th), n[0], places=4)
        self.assertAlmostEqual(math.sin(th), n[1], places=4)
        self.assertEqual(s["baslangic"]["x"], x)

    def test_geometrik_kontrol(self):
        for ad in ("labirent_5x5_t1", "labirent_9x9_t2"):
            g = U.geometrik_kontrol(ad)
            self.assertTrue(g["ok"], (ad, g))


class TestHakem(unittest.TestCase):
    def setUp(self):
        _, self.s = U.oku(SAHNE)
        self.L = self.s["labirent"]

    def _cozum_hatti(self, dis_m=0.5):
        L = self.L
        fc, fn = L["finish"]["cizgi"], L["finish"]["ic_normal"]
        fm = [(fc[0][0] + fc[1][0]) / 2, (fc[0][1] + fc[1][1]) / 2]
        return [L["start"]["poz"][:2]] + L["cozum_yolu"] + [fm, [fm[0] - fn[0] * dis_m, fm[1] - fn[1] * dis_m]]

    def test_basari(self):
        hk = H.Hakem(SAHNE)
        _kos(hk, _hat_uzerinde(self._cozum_hatti(), 0.3, 0.1), 0.1)
        r = hk.sonuc
        self.assertTrue(hk.bitti)
        self.assertEqual(r["durum"], "basari")
        self.assertGreater(r["puan"], 1000)
        self.assertEqual(r["carpma_sayisi"], 0)
        self.assertAlmostEqual(r["p_en"], 1.0, places=6)
        self.assertGreater(r["yol_verimi"], 0.9)
        self.assertEqual(r["kesfedilen_hucre"], self.L["cozum_hucre_sayisi"])
        self.assertAlmostEqual(r["puan"], 1000 + 500 * (1 - r["sure_s"] / 900), places=1)

    def test_fail_start(self):
        hk = H.Hakem(SAHNE)
        x, y, th = self.L["start"]["poz"]
        n = self.L["start"]["ic_normal"]
        pozlar = [(x - n[0] * 0.01 * k, y - n[1] * 0.01 * k, th) for k in range(80)]   # geri geri 0,8 m
        _kos(hk, pozlar, 0.1)
        r = hk.sonuc
        self.assertEqual(r["durum"], "fail_start")
        self.assertEqual(r["puan"], -200)
        # onay anı: çizginin histerezis kadar dışı
        self.assertAlmostEqual(r["sure_s"], 0.1 * 50, delta=0.11)

    def test_fail_sure(self):
        hk = H.Hakem(SAHNE)
        hat = _hat_uzerinde(self._cozum_hatti(), 0.012, 0.5)            # çok yavaş: 900 s'de bitiremez
        _kos(hk, hat, 0.5)
        r = hk.sonuc
        self.assertEqual(r["durum"], "fail_sure", r["olaylar"][-1])
        self.assertAlmostEqual(r["sure_s"], 900.0, places=6)
        self.assertGreater(r["p_en"], 0.5)
        self.assertLess(r["p_en"], 1.0)
        self.assertAlmostEqual(r["puan"], 400 * r["p_en"], places=1)

    def test_fail_sikisma_hareketsiz_yerinde_donme(self):
        """START'ta arka dingil etrafında durmadan dönmek: hareketsiz sayılır (60 s), START'ı tetiklemez."""
        hk = H.Hakem(SAHNE)
        x, y, th0 = self.L["start"]["poz"]
        gx, gy = x - U.ARKA_DINGIL_M * math.cos(th0), y - U.ARKA_DINGIL_M * math.sin(th0)
        pozlar = []
        for k in range(1000):
            th = th0 + 0.05 * k
            pozlar.append((gx + U.ARKA_DINGIL_M * math.cos(th), gy + U.ARKA_DINGIL_M * math.sin(th), th))
        _kos(hk, pozlar, 0.1)
        r = hk.sonuc
        self.assertEqual(r["durum"], "fail_sikisma")
        self.assertEqual(r["sikisma_sebebi"], "hareketsiz")
        self.assertAlmostEqual(r["sure_s"], 60.0, delta=0.3)
        self.assertAlmostEqual(r["puan"], 400 * r["p_en"] - 100, places=1)     # dönerken merkez 0,185 m ileri gider
        self.assertLess(r["puan"], -80)

    def test_fail_sikisma_ilerlemesiz(self):
        """İki hücre arasında gidip gelmek: hareket var, yeni hücre yok -> 300 s'de ilerlemesiz."""
        hk = H.Hakem(SAHNE)
        a, b = self.L["cozum_yolu"][0], self.L["cozum_yolu"][1]
        tur = _hat_uzerinde([a, b, a], 0.3, 0.1)
        bas = _hat_uzerinde([self.L["start"]["poz"][:2], a], 0.3, 0.1)
        _kos(hk, bas + tur * 400, 0.1)
        r = hk.sonuc
        self.assertEqual(r["durum"], "fail_sikisma")
        self.assertEqual(r["sikisma_sebebi"], "ilerlemesiz")
        self.assertAlmostEqual(r["sure_s"], 300.0 + 1.5, delta=3.0)

    def test_baslangicta_yanlis_tetik_yok(self):
        """START pozunda titreşim, 0,35 m geri kayma ve arka dingil etrafında tam tur: hiçbir sonuç tetiklenmez."""
        hk = H.Hakem(SAHNE)
        x, y, th0 = self.L["start"]["poz"]
        n = self.L["start"]["ic_normal"]
        pozlar = [(x + 0.03 * math.sin(k), y + 0.03 * math.cos(1.3 * k), th0 + 0.05 * math.sin(k)) for k in range(100)]
        pozlar += [(x - n[0] * 0.01 * k, y - n[1] * 0.01 * k, th0) for k in range(36)]       # 0,35 m geri (merkez 0,10 içeride)
        x2, y2 = x - n[0] * 0.25, y - n[1] * 0.25
        x, y = x2 + n[0] * 0.25, y2 + n[1] * 0.25
        gx, gy = x - U.ARKA_DINGIL_M * math.cos(th0), y - U.ARKA_DINGIL_M * math.sin(th0)
        for k in range(73):
            th = th0 + math.radians(5 * k)
            pozlar.append((gx + U.ARKA_DINGIL_M * math.cos(th), gy + U.ARKA_DINGIL_M * math.sin(th), th))
        _kos(hk, pozlar, 0.1)
        self.assertFalse(hk.bitti, hk.olaylar)
        self.assertIsNone(hk.sonuc["durum"])

    def test_ilk_cagri_zamani_t0(self):
        hk = H.Hakem(SAHNE, sure_siniri_s=10.0)
        x, y, th = self.L["start"]["poz"]
        hk.guncelle(100.0, (x, y, th), False)
        hk.guncelle(109.9, (x, y + 0.001, th), False)
        self.assertFalse(hk.bitti)
        hk.guncelle(110.0, (x, y, th), False)
        self.assertEqual(hk.sonuc["durum"], "fail_sure")

    def test_carpma_olaylari(self):
        hk = H.Hakem(SAHNE)
        x, y, th = self.L["start"]["poz"]
        # temas: 0-0,5 s, 1,0-1,5 s (0,5 s ara: aynı olay), 3,0-4,0 s (yeni olay)
        temas = lambda t: (0.0 <= t < 0.5) or (1.0 <= t < 1.5) or (3.0 <= t < 4.0)
        pozlar = [(x + 0.002 * k, y, th) for k in range(60)]
        _kos(hk, pozlar, 0.1, temas=lambda t: temas(round(t, 6)))
        r = hk.sonuc
        self.assertEqual(r["carpma_sayisi"], 2)
        self.assertAlmostEqual(r["carpma_suresi_s"], 2.0, delta=0.11)
        self.assertEqual(len([o for o in r["olaylar"] if o["tur"] == "carpma"]), 2)

    def test_jeodezik_surekli_ve_monoton(self):
        hk = H.Hakem(SAHNE)
        hat = self._cozum_hatti(dis_m=0.0)
        onceki = None
        for x, y, _ in _hat_uzerinde(hat, 0.05, 1.0):
            g = hk.jeodezik(x, y)
            if onceki is not None:
                self.assertLessEqual(g, onceki + 1e-9)
                self.assertLess(onceki - g, 0.06)
            onceki = g
        self.assertAlmostEqual(onceki, 0.0, places=6)
        self.assertAlmostEqual(hk.g0, self.L["cozum_uzunlugu_m"] - U.START_IC_M, places=6)

    def test_cikmaz_kus_ucusu_yaniltmaz(self):
        """FINISH'e kuş uçuşu yakın ama labirentte uzak bir hücrede p_en küçük kalır."""
        _, s = U.oku("labirent_9x9_t1")
        hk = H.Hakem(s)
        lab, yer = U.labirent_sahneden(s)
        fx, fy = yer.merkez(lab.finish[1])
        en = None
        for hc, d in hk.d_hucre.items():
            cx, cy = yer.merkez(hc)
            k = math.hypot(cx - fx, cy - fy)
            if d >= 10 and (en is None or k < en[0]):
                en = (k, hc, d)
        self.assertIsNotNone(en)
        cx, cy = yer.merkez(en[1])
        self.assertGreaterEqual(hk.jeodezik(cx, cy), 9.5 * yer.h)


class TestPuan(unittest.TestCase):
    def test_formul(self):
        self.assertEqual(P.puan("basari", 0, 1, 0, 0)[0], 1500)
        self.assertEqual(P.puan("basari", 900, 1, 0, 0)[0], 1000)
        self.assertEqual(P.puan("basari", 450, 1, 2, 1.5)[0], 1250 - 100 - 15)
        self.assertEqual(P.puan("fail_sure", 900, 0.5, 0, 0)[0], 200)
        self.assertEqual(P.puan("fail_sikisma", 300, 0.5, 1, 0)[0], 200 - 100 - 50)
        self.assertEqual(P.puan("fail_start", 3, 0.9, 0, 0)[0], -200)
        toplam, d = P.puan("basari", 123.4, 1, 3, 2.2)
        self.assertAlmostEqual(sum(d.values()), toplam)

    def test_oyunlanamazlik(self):
        # kımıldamamak (sıkışma, ilerleme 0) her zaman aşımından ve küçük ilerlemeden kötü
        self.assertLess(P.puan("fail_sikisma", 60, 0, 0, 0)[0], P.puan("fail_sure", 900, 0, 0, 0)[0])
        # en yavaş temiz başarı > en iyi başarısızlık
        self.assertGreater(P.puan("basari", 900, 1, 0, 0)[0], P.puan("fail_sure", 900, 1, 0, 0)[0])
        # START'tan çıkmak, ilerlemeden bağımsız olarak her zaman aşımından kötü
        self.assertLess(P.puan("fail_start", 1, 1, 0, 0)[0], P.puan("fail_sure", 900, 0, 0, 0)[0])
        # duvara sürtünerek 10 s kazanmak: süre primi +5,6, ceza en az -50 - 10 x temas süresi
        kazanc = P.puan("basari", 590, 1, 1, 1.0)[0] - P.puan("basari", 600, 1, 0, 0)[0]
        self.assertLess(kazanc, 0)

    def test_ek_tur(self):
        s2, _ = P.ek_tur_puani(True, 100.0, 0, 39.0, v_maks=0.39)
        self.assertAlmostEqual(s2, 300.0)
        s2, _ = P.ek_tur_puani(True, 200.0, 1, 39.0, v_maks=0.39)
        self.assertAlmostEqual(s2, 150.0 - 50.0)
        self.assertEqual(P.ek_tur_puani(False, 50.0, 0, 39.0)[0], 0.0)


if __name__ == "__main__":
    unittest.main()
