"""v4 hız zarfı sınamaları (unittest).

    cd kod/fizik && py -3 -m unittest kesif.testler.test_hiz4 -v
"""

import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kesif import _yol  # noqa: E402,F401


def _sur(iz, poz, adim=4000, dt=0.05):
    """Arka dingil tek tekerlekli kinematiği; komutlar doğrudan uygulanır. -> (süre, son poz, en büyük v)."""
    x, y, th = poz
    q = iz.ayar.donme_merkezi_x
    vm = 0.0
    for k in range(adim):
        km = iz.komut((x, y, th))
        if km.bitti:
            return k * dt, (x, y, th), vm
        vm = max(vm, km.v)
        ax, ay = x + q * math.cos(th), y + q * math.sin(th)
        ax += km.v * dt * math.cos(th + 0.5 * km.w * dt)
        ay += km.v * dt * math.sin(th + 0.5 * km.w * dt)
        th += km.w * dt
        x, y = ax - q * math.cos(th), ay - q * math.sin(th)
    return None, (x, y, th), vm


class FrenZarfi(unittest.TestCase):
    def test_fren_hizi_tanimi(self):
        from kesif.surus4 import fren_hizi
        self.assertEqual(fren_hizi(0.0), 0.0)
        self.assertEqual(fren_hizi(-1.0), 0.0)
        for d in (0.05, 0.2, 0.8):
            v = fren_hizi(d, a=0.5, tepki_s=0.15)
            self.assertAlmostEqual(v * 0.15 + v * v / (2 * 0.5), d, places=9)
        self.assertGreater(fren_hizi(0.3), fren_hizi(0.1))

    def test_zarf_izleyici_kuyrugu_kisaltir_ve_yol_sonunda_durur(self):
        from gezinme.izleyici import IzleyiciAyar, YolIzleyici
        from kesif.surus4 import ZarfIzleyici
        yol = [(0.0, 0.0), (1.3, 0.0)]
        sonuc = {}
        for ad, cls in (("v3", YolIzleyici), ("v4", ZarfIzleyici)):
            iz = cls(IzleyiciAyar(v_max=0.25, dur_mesafe_m=0.12, kalk_mesafe_m=0.18, yavas_mesafe_m=0.50))
            iz.yol_ver(yol)
            sonuc[ad] = _sur(iz, (0.0, 0.0, 0.0))
        t3, p3, _ = sonuc["v3"]
        t4, p4, v4m = sonuc["v4"]
        self.assertIsNotNone(t3)
        self.assertIsNotNone(t4)
        self.assertLess(t4, t3 - 0.5)                 # doğrusal yumuşak varışın kuyruğu kısalır
        self.assertLess(abs(p4[0] - 1.3), 0.06)       # gövde merkezi yol sonunda (varış payı)
        self.assertLessEqual(v4m, 0.25 + 1e-9)        # v_max'ı aşmaz

    def test_engel_zarfi_dur_esigini_korur(self):
        from gezinme.izleyici import IzleyiciAyar
        from kesif.surus4 import ZarfIzleyici
        iz = ZarfIzleyici(IzleyiciAyar(v_max=0.39, dur_mesafe_m=0.12, kalk_mesafe_m=0.18))
        iz.yol_ver([(0.0, 0.0), (5.0, 0.0)])
        k = iz.komut((0.0, 0.0, 0.0), on_mesafe=0.10)
        self.assertTrue(k.durdu)
        iz2 = ZarfIzleyici(IzleyiciAyar(v_max=0.39, a_max=100.0, dur_mesafe_m=0.12))
        iz2.yol_ver([(0.0, 0.0), (5.0, 0.0)])
        k2 = iz2.komut((0.0, 0.0, 0.0), on_mesafe=0.20)
        from kesif.surus4 import fren_hizi
        self.assertLessEqual(k2.v, fren_hizi(0.08) + 1e-9)


class Hizalanma(unittest.TestCase):
    def test_hizala_iste_yay_yerine_yerinde_doner(self):
        from gezinme.izleyici import IzleyiciAyar
        from kesif.surus4 import ZarfIzleyici
        yol = [(0.0, 0.0), (2.0, 0.6)]                # başlangıçta ~0,3 rad yön hatası (donus_gir 0,9 altında)
        for iste, mod in ((False, "izle"), (True, "yerinde")):
            iz = ZarfIzleyici(IzleyiciAyar(v_max=0.25))
            iz.yol_ver(yol)
            iz.hizala_iste = iste
            k = iz.komut((0.0, 0.0, 0.0))
            self.assertEqual(k.mod, mod)
            self.assertFalse(iz.hizala_iste)          # bir adımlık istek


class SupurmeDenetimi(unittest.TestCase):
    def test_yay_yaninda_duvar_ucu_yakalanir(self):
        from kesif.robot import VARSAYILAN as R
        from kesif.surus4 import supurme_carpar, yay_pozlari
        P = yay_pozlari(0.39, 0.0, 0.8, R.dingil_x_m, 0.6)      # sola yay (r = 1,25 m)
        self.assertGreater(len(P), 5)
        self.assertGreater(P[-1][2], 0.1)
        bos = (np.array([3.0, -3.0]), np.array([3.0, 3.0]))
        self.assertFalse(supurme_carpar(P, R, 0.05, tarama_xy=bos))
        # gövdenin sol ön köşesinin yay boyunca geçeceği yerde bir duvar ucu (düz sürüşte gövde dışında kalır)
        uc = (np.array([0.55]), np.array([0.40]))
        self.assertTrue(supurme_carpar(P, R, 0.05, tarama_xy=uc))
        duz = yay_pozlari(0.39, 0.0, 0.0, R.dingil_x_m, 0.6)
        self.assertFalse(supurme_carpar(duz, R, 0.05, tarama_xy=uc))

    def test_harita_sorgusu(self):
        from kesif.robot import VARSAYILAN as R
        from kesif.surus4 import supurme_carpar, yay_pozlari
        P = yay_pozlari(0.39, 0.0, 0.0, R.dingil_x_m, 0.6)
        hep_dolu = lambda wx, wy: bool(((wx > 0.6) & (wx < 0.7)).any())      # gövde merkezinden 0,6-0,7 m önde
        self.assertTrue(supurme_carpar(P, R, 0.05, dolu_mu=hep_dolu, govde_poz=(0.0, 0.0, 0.0)))
        self.assertFalse(supurme_carpar(P, R, 0.05, dolu_mu=hep_dolu, govde_poz=(-2.0, 0.0, 0.0)))


class V4Surum(unittest.TestCase):
    def test_v1_v3_degismedi_v4_v3_ustune(self):
        from kesif.beyin import BeyinAyari, KesifBeyni, surum_ayari
        from gezinme.izleyici import YolIzleyici
        from kesif.surus4 import ZarfIzleyici
        for s in ("v1", "v2", "v3"):
            self.assertFalse(surum_ayari(s).hiz_zarfi)
            self.assertIs(type(KesifBeyni(ayar=surum_ayari(s)).izleyici), YolIzleyici)
        a3, a4 = surum_ayari("v3"), surum_ayari("v4")
        self.assertTrue(a4.hiz_zarfi)
        a4.hiz_zarfi = False
        self.assertEqual(a3, a4)                      # v4 = v3 + hız zarfı, başka fark yok
        self.assertEqual(surum_ayari("v1"), BeyinAyari())
        b = KesifBeyni(ayar=surum_ayari("v4"))
        self.assertIsInstance(b.izleyici, ZarfIzleyici)
        self.assertEqual(b.durum()["ek"]["surum"], "v4")

    def _beyin(self, nokta):
        from gezinme.izleyici import Komut
        from kesif.beyin import KesifBeyni, surum_ayari
        b = KesifBeyni(ayar=surum_ayari("v4"))
        b.mod = "kesif"
        b.izleyici.son = Komut(0.25, 0.0, mod="izle")
        b.izleyici.son_alfa, b.izleyici.son_kappa = 0.0, 0.0
        b.izleyici.ayar.v_max = 0.25
        b.slam.son_noktalar = nokta
        return b

    def test_hizlanma_izni_olcuye_dayali(self):
        bos = (np.array([6.0]), np.array([6.0]))
        b = self._beyin(bos)
        b._hiz_ayarla_v4()
        self.assertAlmostEqual(b.izleyici.ayar.v_max, 0.39, places=6)      # yön oturmuş, şerit boş
        # yön hatası büyük: v_seyir'de kalır
        b = self._beyin(bos)
        b.izleyici.son_alfa = 0.6
        b._hiz_ayarla_v4()
        self.assertAlmostEqual(b.izleyici.ayar.v_max, 0.25, places=6)
        # yön hatası arada: arada bir hız
        b = self._beyin(bos)
        b.izleyici.son_alfa = 0.375
        b._hiz_ayarla_v4()
        self.assertTrue(0.25 < b.izleyici.ayar.v_max < 0.39)
        # önde süpürme alanında tarama noktası: hızlanma reddedilir
        b = self._beyin((np.array([0.78]), np.array([0.0])))
        b._hiz_ayarla_v4()
        self.assertAlmostEqual(b.izleyici.ayar.v_max, 0.25, places=6)
        self.assertGreater(b.sayac.get("zarf_red", 0), 0)
        # süpürme v_seyir'de de çarpıyor: yerinde hizalanma iste (v4 varsayılanı yavaşlamaz: zarf_v_yavas 0)
        b = self._beyin((np.array([0.50]), np.array([0.0])))
        b._hiz_ayarla_v4()
        self.assertAlmostEqual(b.izleyici.ayar.v_max, 0.25, places=6)
        self.assertTrue(b.izleyici.hizala_iste)
        b = self._beyin((np.array([0.50]), np.array([0.0])))
        b.ayar.zarf_v_yavas = 0.12                    # deneysel yavaşlama seçeneği
        b._hiz_ayarla_v4()
        self.assertAlmostEqual(b.izleyici.ayar.v_max, 0.12, places=6)
        # kurtarma kipinde izin yok
        b = self._beyin(bos)
        b.mod = "kurtarma"
        b._hiz_ayarla_v4()
        self.assertAlmostEqual(b.izleyici.ayar.v_max, 0.25, places=6)

    def test_v4_5x5_basari_carpmasiz(self):
        from kesif.benzet2b import Benzetici, BenzetimAyari
        from kesif.beyin import olustur, surum_ayari
        from kesif.sahne import sahne_yukle
        s = sahne_yukle("labirent_5x5_t1")
        b = olustur("labirent_5x5_t1", ayar=surum_ayari("v4"))
        r = Benzetici(s, b, BenzetimAyari(sure_siniri_s=300.0, tohum=0)).kos()
        self.assertEqual(r["durum"], "basari", r)
        self.assertEqual(int(r.get("carpma_sayisi") or 0), 0, r)
        self.assertGreater(b.sayac.get("hizli", 0), 0)
        self.assertEqual(b.sayac["start_kesme"], 0)

    def test_deneme_zinciri_v4_izleyicisini_korur(self):
        from kesif.beyin import KesifBeyni, surum_ayari
        from gezinme.izleyici import YolIzleyici
        from kesif.deneme import yeni_deneme, zincir_hazirla
        from kesif.surus4 import ZarfIzleyici
        b = KesifBeyni(ayar=surum_ayari("v4"))
        b2 = yeni_deneme(b, zincir_hazirla(b))
        self.assertIsInstance(b2.izleyici, ZarfIzleyici)
        b3 = KesifBeyni(ayar=surum_ayari("v3"))
        b3 = yeni_deneme(b3, zincir_hazirla(b3))
        self.assertIs(type(b3.izleyici), YolIzleyici)


if __name__ == "__main__":
    unittest.main()
