"""Sentetik uçtan uca: 2B ışın izlemeyle gürültülü tarama, bozuk odometriyle yol, filtre doğru haritaya ve konuma
yakınsıyor mu. Odometri bozukluğu her koşuda: ileri ölçek +%3, dönüş -%1,4 (SIMULASYON.md (e) iz farkı), ileri std
%2, dönüş std %5. Tarama: 12 m, 0,72°, 3 cm gürültü (geçici değerler)."""

import math
import time
import unittest

import numpy as np

from . import FIZIK  # noqa: F401
from .ortak import kaydet, koridor
from konumlama import (CokHaritaliMCL, LidarOzellik, OlcumParametreleri, harita_yukle, karar_ani,
                       sentetik_tarama, tek_taramadan_sinifla)
from konumlama.benzet import konum_hatasi, yol_boyunca, yol_uret

OZ = LidarOzellik.gecici()
UC_HARITA = ["oda_engelli", "oda_bos", "acik_alan"]
YOL_ENGELLI = [(1.5, 1.5), (2.5, 2.8), (4.2, 2.8), (6.0, 2.8), (7.2, 2.8), (7.2, 3.8)]
YOL_BOS = [(3.0, 2.5), (4.5, 2.5), (4.5, 3.8), (1.5, 3.8)]
KORIDOR_A = koridor("koridor_A", kapilar=[(4, "alt", 0.9), (10, "ust", 0.9), (17, "alt", 0.9)])
KORIDOR_B = koridor("koridor_B", kapilar=[(4, "alt", 0.9), (10, "ust", 0.9), (17, "ust", 0.9)])


def kos(haritalar, dogru, noktalar, aci0, tohum, **kw):
    ayar = kw.pop("ayar", {})
    mcl = CokHaritaliMCL(haritalar, ozellik=OZ, tohum=tohum, **ayar)
    h = mcl.haritalar[mcl.adlar.index(dogru)]
    s = yol_boyunca(mcl, h, yol_uret(noktalar, aci0), OZ, np.random.default_rng(1000 + tohum), **kw)
    return mcl, s


def mod_yakinda(tah, poz, harita, xy=0.25, aci=math.radians(10), en_az_pay=0.05):
    for m in tah.modlar:
        if (m["harita"] == harita and m["pay"] >= en_az_pay and math.hypot(m["x"] - poz[0], m["y"] - poz[1]) < xy
                and abs((m["theta"] - poz[2] + math.pi) % (2 * math.pi) - math.pi) < aci):
            return True
    return False


class UctanUca(unittest.TestCase):
    def test_oda_engelli_yakinsama(self):
        """Dayanak: görev "sentetik uçtan uca" — gerçek oda_engelli, 3 harita, 3 tohum: doğru harita, son konum hatası
        < 0,15 m / 3°, karar kalıcı."""
        for tohum in (1, 2, 3):
            mcl, s = kos(UC_HARITA, "oda_engelli", YOL_ENGELLI, 0.0, tohum)
            poz, son = s[-1]
            e, a = konum_hatasi(son, poz)
            k = karar_ani(mcl.gecmis, "oda_engelli")
            kk = karar_ani(mcl.gecmis, "oda_engelli", konum_da=True)
            ort = np.mean([konum_hatasi(t, p)[0] for p, t in s[len(s) // 2:]])
            kaydet("oda_engelli t%d" % tohum, "harita kararı yol m / konum kararı yol m",
                   "%.2f / %.2f" % (k["gidilen_yol_m"] if k else float("nan"), kk["gidilen_yol_m"] if kk else float("nan")))
            kaydet("oda_engelli t%d" % tohum, "son hata m / derece; ikinci yarı ort. m",
                   "%.3f / %.2f; %.3f" % (e, math.degrees(a), ort))
            self.assertEqual(son.en_olasi, "oda_engelli")
            self.assertFalse(son.kararsiz)
            self.assertIsNotNone(k)
            self.assertLess(e, 0.15)
            self.assertLess(math.degrees(a), 3.0)

    def test_oda_bos_ayrimi(self):
        """Dayanak: oda_engelli / oda_bos ayrımı — gerçek oda_bos: doğru harita; oda 180° simetrik olduğu için konum
        kararsız raporlanır ve gerçek poz modlardan birinde."""
        for tohum in (1, 2, 3):
            mcl, s = kos(UC_HARITA, "oda_bos", YOL_BOS, 0.0, tohum)
            poz, son = s[-1]
            k = karar_ani(mcl.gecmis, "oda_bos")
            kaydet("oda_bos t%d" % tohum, "harita kararı yol m; son p(oda_bos); mod sayısı",
                   "%.2f; %.4f; %d" % (k["gidilen_yol_m"] if k else float("nan"), son.olasiliklar["oda_bos"],
                                       len(son.modlar)))
            self.assertEqual(son.en_olasi, "oda_bos")
            self.assertFalse(son.kararsiz)
            self.assertTrue(son.konum_kararsiz)
            self.assertTrue(mod_yakinda(son, poz, "oda_bos"))

    def test_benzer_koridorlar_karar_ani(self):
        """Dayanak: iki benzer koridor (yalnız x = 17'deki kapının yanı farklı). Fark 12 m menzile girene dek
        (ilk 3 m yol) filtre kararsız kalmalı; sonra doğru koridora karar vermeli, koridor boyunca konum < 0,2 m."""
        mcl, s = kos([KORIDOR_A, KORIDOR_B, "oda_engelli"], "koridor_A", [(1.5, 2.0), (16.0, 2.0)], 0.0, 1)
        erken = [t for _, t in s if t.gidilen_yol_m <= 3.0]
        self.assertTrue(erken)
        self.assertTrue(all(t.kararsiz for t in erken), [round(t.fark, 3) for t in erken])
        poz, son = s[-1]
        e, _ = konum_hatasi(son, poz)
        k = karar_ani(mcl.gecmis, "koridor_A")
        kaydet("benzer koridor", "ilk 3 m'de en büyük p1-p2", "%.3f" % max(t.fark for t in erken))
        kaydet("benzer koridor", "karar: yol m (x) / adım", "%.2f (x=%.1f) / %d" % (
            k["gidilen_yol_m"], 1.5 + k["gidilen_yol_m"], k["adim"]))
        kaydet("benzer koridor", "son hata m; p(A)", "%.3f; %.4f" % (e, son.olasiliklar["koridor_A"]))
        self.assertEqual(son.en_olasi, "koridor_A")
        self.assertFalse(son.kararsiz)
        self.assertLess(e, 0.2)

    def test_beklenmeyen_engel_ve_kayip(self):
        """Dayanak: karışım modeli — haritada olmayan iki insan (r 0,25 m) yol kenarında ve %5 ışın kaybı varken
        doğru harita, son hata < 0,25 m."""
        insanlar = [{"tur": "daire", "x": 3.0, "y": 3.4, "r": 0.25}, {"tur": "daire", "x": 6.6, "y": 2.2, "r": 0.25}]
        mcl, s = kos(UC_HARITA, "oda_engelli", YOL_ENGELLI, 0.0, 4, ek_engeller=insanlar, kayip_orani=0.05)
        poz, son = s[-1]
        e, a = konum_hatasi(son, poz)
        kaydet("insan + %5 kayıp", "son hata m / derece; p(oda_engelli)",
               "%.3f / %.2f; %.4f" % (e, math.degrees(a), son.olasiliklar["oda_engelli"]))
        self.assertEqual(son.en_olasi, "oda_engelli")
        self.assertLess(e, 0.25)

    def test_isin_modeli(self):
        """Dayanak: ölçüm modeli seçeneği "isin" (beam model) de yakınsar."""
        p = OlcumParametreleri(model="isin")
        mcl = CokHaritaliMCL(UC_HARITA, ozellik=OZ, olcum=p, tohum=5)
        h = mcl.haritalar[0]
        bas = time.perf_counter()
        s = yol_boyunca(mcl, h, yol_uret(YOL_ENGELLI[:4], 0.0), OZ, np.random.default_rng(5))
        sure = (time.perf_counter() - bas) / len(s)
        poz, son = s[-1]
        e, _ = konum_hatasi(son, poz)
        kaydet("isin modeli", "son hata m; adım başına ms (ilk dahil)", "%.3f; %.1f" % (e, sure * 1e3))
        self.assertEqual(son.en_olasi, "oda_engelli")
        self.assertLess(e, 0.2)

    def test_tohum_ayni_sonuc(self):
        """Dayanak: aynı tohum = aynı sonuç (filtre + tarama üreteci)."""
        def bir():
            mcl, s = kos(UC_HARITA, "oda_engelli", YOL_ENGELLI[:3], 0.0, 7)
            return [(g["olasiliklar"], g["x"], g["y"], g["theta"]) for g in mcl.gecmis], mcl.parcaciklar()
        g1, p1 = bir()
        g2, p2 = bir()
        self.assertEqual(g1, g2)
        for a, b in zip(p1, p2):
            np.testing.assert_array_equal(a, b)
        mcl3, _ = kos(UC_HARITA, "oda_engelli", YOL_ENGELLI[:3], 0.0, 8)
        self.assertFalse(np.array_equal(mcl3.parcaciklar()[1][:50], p1[1][:50]))


class TekTarama(unittest.TestCase):
    def test_tek_tarama_sinifla(self):
        """Dayanak: hareketsiz tek tarama sınıflaması — farklı odalar ayrılır, benzer koridorlar ve ikiz harita
        kararsız çıkar."""
        rng = np.random.default_rng(11)
        dort = UC_HARITA + [KORIDOR_A]
        for dogru, poz in (("oda_engelli", (1.5, 1.5, 0.0)), ("oda_engelli", (6.0, 2.8, 2.0)),
                           ("oda_bos", (3.0, 2.5, 0.0)), ("koridor_A", (6.0, 2.0, 0.0))):
            h = harita_yukle(KORIDOR_A if dogru == "koridor_A" else dogru)
            tar = sentetik_tarama(h, poz, OZ, rng)
            bas = time.perf_counter()
            r = tek_taramadan_sinifla(dort, tar, ozellik=OZ)
            sure = time.perf_counter() - bas
            px, py, pt, _ = r["pozlar"][dogru]
            e = math.hypot(px - poz[0], py - poz[1])
            kaydet("tek tarama %s" % dogru, "p(dogru); poz hatası m; süre ms",
                   "%.4f; %.3f; %.0f" % (r["olasiliklar"][dogru], e, sure * 1e3))
            self.assertEqual(r["en_olasi"], dogru)
            self.assertFalse(r["kararsiz"])
            if dogru != "oda_bos":           # oda_bos 180° simetrik: en iyi poz iki moddan biri
                self.assertLess(e, 0.3)
        # benzer koridorlar, fark menzil dışında
        tar = sentetik_tarama(harita_yukle(KORIDOR_A), (1.5, 2.0, 0.0), OZ, rng)
        r = tek_taramadan_sinifla([KORIDOR_A, KORIDOR_B], tar, ozellik=OZ)
        kaydet("tek tarama A/B (x=1.5)", "p(A), p(B)", "%.3f, %.3f" % (r["olasiliklar"]["koridor_A"],
                                                                       r["olasiliklar"]["koridor_B"]))
        self.assertTrue(r["kararsiz"])


if __name__ == "__main__":
    unittest.main()
