"""Harita, ışın izleme, çarpışma ve belirlenimcilik (aynı girdi → aynı çıktı)."""

import math
import unittest

from sahte_esp32.cekirdek import SahteEsp32
from sahte_esp32.harita import Harita, harita_listesi
from sahte_esp32.tasima import BellekTasima
from lale_pi.istemci import Esp32Istemci


class HaritaTesti(unittest.TestCase):

    def test_en_az_iki_oda_haritasi_yuklenir(self):
        """Dayanak: brief "en az iki örnek harita" (düz veri dosyası)."""
        adlar = harita_listesi()
        self.assertGreaterEqual(len([a for a in adlar if a.startswith("oda_")]), 2, adlar)
        for ad in adlar:
            with self.subTest(harita=ad):
                h = Harita.dosyadan(ad)
                self.assertGreater(len(h.parcalar), 0)
                c = SahteEsp32(h)                                # başlangıç konumu engelin içinde değil
                self.assertFalse(c.hakem()["carpiyor"] or c._carpar(*h.baslangic))

    def test_isin_uzakligi_ve_gelis_acisi(self):
        """Dayanak: TASLAK sonar modeli (robot_parametreleri.json: koni, menzil, geliş sınırı)."""
        h = Harita.dosyadan("oda_bos")
        t, gelis = h.isin(3.0, 2.5, 0.0, 10.0)
        self.assertAlmostEqual(t, 3.0)
        self.assertAlmostEqual(gelis, 0.0)
        t, gelis = h.isin(3.0, 2.5, math.radians(60), 10.0)
        self.assertAlmostEqual(t, 2.5 / math.sin(math.radians(60)))   # üst duvar y = 5 (yan duvar 6 m'de)
        self.assertAlmostEqual(math.degrees(gelis), 30.0)
        t, gelis = h.isin(3.0, 2.5, math.radians(30), 10.0)
        self.assertAlmostEqual(t, 3.0 / math.cos(math.radians(30)))   # yan duvar x = 6
        self.assertAlmostEqual(math.degrees(gelis), 30.0)
        self.assertIsNone(h.isin(3.0, 2.5, 0.0, 2.0))                 # menzil içinde yüzey yok
        e = Harita.dosyadan("oda_engelli")
        t, _ = e.isin(2.0, 1.4, 0.0, 10.0)                            # kolon (3,2; 1,4) r 0,25
        self.assertAlmostEqual(t, 1.2 - 0.25)

    def test_cokgen_carpisma(self):
        """Dayanak: hakem (çarpışma sayısı) doğru olmalı; taban 520 × 525 mm (arayuz.py ETEK_A / ETEK_B)."""
        h = Harita.dosyadan("oda_bos")
        c = SahteEsp32(h)
        self.assertFalse(c._carpar(3.0, 2.5, 0.0))
        self.assertTrue(c._carpar(5.8, 2.5, 0.0))                     # ön yüz x = 6,06 > 6
        self.assertFalse(c._carpar(5.7, 2.5, 0.0))
        self.assertTrue(c._carpar(5.65, 2.5, math.radians(45)))       # köşe dönünce değer
        e = Harita.dosyadan("oda_engelli")
        ce = SahteEsp32(e)
        self.assertTrue(ce._carpar(3.2, 1.4 - 0.5, 0.0))              # kolon tabanın içinde kalır

    def test_esdogrusal_ve_degen_kenar_carpisma_sayilir(self):
        """Dayanak: Y0s-kontrol.md § 3 madde 5 (katı işaret karşılaştırması eşdoğrusal / değen parçayı kaçırıyordu)."""
        from sahte_esp32.harita import _parca_kesisir
        self.assertTrue(_parca_kesisir((0, 0, 2, 0), (1, 0, 3, 0)))      # eşdoğrusal üst üste
        self.assertTrue(_parca_kesisir((0, 0, 2, 0), (1, 0, 1, -1)))     # T değmesi (eski kod: işarete göre kaçırıyordu)
        self.assertTrue(_parca_kesisir((0, 0, 2, 0), (2, 0, 3, 1)))      # uç uca değme
        self.assertFalse(_parca_kesisir((0, 0, 2, 0), (3, 0, 4, 0)))     # eşdoğrusal ayrık
        self.assertFalse(_parca_kesisir((0, 0, 2, 0), (0, 1, 2, 1)))     # paralel
        kare = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for duvar in ([-1.0, 1.0, 2.0, 1.0], [2.0, 1.0, -1.0, 1.0]):     # kenarla eşdoğrusal, iki ucu da dışarıda
            with self.subTest(duvar=duvar):
                h = Harita({"boyut_m": [5, 5], "cevre_duvari": False, "duvarlar": [duvar]})
                self.assertTrue(h.cokgen_carpar(kare))
        h = Harita({"boyut_m": [5, 5], "cevre_duvari": False, "duvarlar": [[-1.0, 1.001, 2.0, 1.001]]})
        self.assertFalse(h.cokgen_carpar(kare))


class Belirlenimcilik(unittest.TestCase):

    def _kos(self):
        h = Harita.dosyadan("oda_engelli")
        c = SahteEsp32(h)
        t = BellekTasima(c)
        e = Esp32Istemci(t, kayit_boyu=10 ** 6)
        e.baglan()
        e.devreye_al_ve_bekle()
        e.sur_tut(0.3, 0.4, 4000)
        e.sur_tut(0.39, -0.2, 6000)
        e.ham_gonder(b"{bozuk\n")
        e.bekle(700)
        return [satir for yon, satir in e.kayit], c.hakem()

    def test_ayni_girdi_ayni_cikti(self):
        """Dayanak: brief mimari kararı "çekirdek saf ve deterministik; her koşuda aynı sonuç"."""
        a, ha = self._kos()
        b, hb = self._kos()
        self.assertEqual(a, b)
        self.assertEqual(ha, hb)
        self.assertGreater(len(a), 100)


if __name__ == "__main__":
    unittest.main()
