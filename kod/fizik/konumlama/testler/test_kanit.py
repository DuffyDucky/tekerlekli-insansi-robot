"""Harita kanıtı: olasılık ölçümden gelmeli, parçacık filtresinin rastgeleliğinden değil.

Bulgu (MuJoCo deneyi, `kod/fizik/deneyler/koridor_karisiklik`): eski tahmincide (artım = log sum_i w_i L_i) iki
birebir aynı haritanın olasılığı 0,95'e kaydı; 6 koridorda yanlış koridora kesin karar verildi. Bu dosya:
  - ikiz haritalar, çok tohum (sentetik 20 tohum; MuJoCo kaydı --uzun ile 20 tohum)
  - benzer çift koridor_5 / koridor_6 (gerçek haritalar varsa): fark görünmeden kararsız, sonra doğru karar
  - baslat_poz çok haritada, işlenmeyen taramada poz ileri taşıma, kör sektör payı
Tohum sayısı: varsayılan hızlı kip 5, `kos.py --uzun` (LALE_KONUM_UZUN=1) 20.
"""

import math
import os
import pickle
import sys
import tempfile
import unittest

import numpy as np

from . import FIZIK  # noqa: F401
from .ortak import kaydet
from konumlama import CokHaritaliMCL, LidarOzellik, harita_yukle
from konumlama.benzet import goreli, konum_hatasi, yol_boyunca, yol_uret
from konumlama.harita2b import HARITA_KLASORU
from konumlama.tarama import OZELLIK_DOSYASI

UZUN = os.environ.get("LALE_KONUM_UZUN") == "1"
N_TOHUM = 20 if UZUN else 5
OZ = LidarOzellik.gecici()
DENEY = os.path.join(FIZIK, "deneyler", "koridor_karisiklik")
CIFT = ("koridor_5", "koridor_6")
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
KORIDOR_VAR = all(os.path.exists(os.path.join(HARITA_KLASORU, k + ".json")) for k in KORIDORLAR)


def ozet(v):
    v = np.asarray(v, dtype=float)
    return "ort %.3f, medyan %.3f, en çok %.3f (n=%d)" % (v.mean(), np.median(v), v.max(), v.size)


def ikiz(veri, a="ikiz_a", b="ikiz_b"):
    return [dict(veri, ad=a), dict(veri, ad=b)]


class IkizHaritalar(unittest.TestCase):
    def test_ikiz_20_tohum_sentetik(self):
        """Dayanak: iki birebir aynı harita (oda_bos), uzun yol (iki tur, ≈ 26 m, 345 tarama), 20 tohum: hiçbir tohumda hiçbir
        adımda kesin karar yok; en büyük p1 - p2 dağılımı raporlanır."""
        veri = harita_yukle("oda_bos").veri
        tur = [(3.0, 2.5), (4.6, 2.5), (4.6, 3.9), (1.4, 3.9), (1.4, 1.1), (4.6, 1.1), (4.6, 2.5)]
        yol = yol_uret(tur + tur[1:], 0.0)
        farklar, kesin = [], 0
        for t in range(20):
            mcl = CokHaritaliMCL(ikiz(veri), ozellik=OZ, tohum=100 + t)
            s = yol_boyunca(mcl, mcl.haritalar[0], yol, OZ, np.random.default_rng(200 + t))
            farklar.append(max(tah.fark for _, tah in s))
            kesin += sum(1 for _, tah in s if not tah.kararsiz)
        kaydet("ikiz sentetik 20 tohum", "en büyük p1-p2 (tohum başına)", ozet(farklar))
        kaydet("ikiz sentetik 20 tohum", "kesin adım (toplam) / adım", "%d / %d" % (kesin, 20 * len(s)))
        self.assertEqual(kesin, 0)
        self.assertLess(max(farklar), 0.2)

    def test_eski_tahminci_kayar(self):
        """Dayanak: kök neden kanıtı — aynı ikiz kurulumda eski tahminci ("ortalama") yeni tahminciden ("uyum")
        belirgin biçimde fazla kayar (tohum başına en büyük |log p_a/p_b|)."""
        veri = harita_yukle("oda_bos").veri
        tur = [(3.0, 2.5), (4.6, 2.5), (4.6, 3.9), (1.4, 3.9), (1.4, 1.1), (4.6, 1.1), (4.6, 2.5)]
        yol = yol_uret(tur + tur[1:], 0.0)
        sonuc = {}
        for kanit in ("ortalama", "uyum"):
            lr = []
            for t in range(N_TOHUM):
                mcl = CokHaritaliMCL(ikiz(veri), ozellik=OZ, tohum=300 + t, harita_kaniti=kanit)
                s = yol_boyunca(mcl, mcl.haritalar[0], yol, OZ, np.random.default_rng(400 + t))
                lr.append(max(abs(math.log(tah.olasiliklar["ikiz_a"] / tah.olasiliklar["ikiz_b"])) for _, tah in s))
            sonuc[kanit] = lr
            kaydet("ikiz sentetik, %s" % kanit, "en büyük |log pa/pb|", ozet(lr))
        self.assertLess(np.mean(sonuc["uyum"]) * 3, np.mean(sonuc["ortalama"]))


@unittest.skipUnless(KORIDOR_VAR, "koridor_1..6 yok")
class BenzerCift(unittest.TestCase):
    def kos(self, dogru, tohum, yol_m=16.0):
        mcl = CokHaritaliMCL(KORIDORLAR, ozellik=OZ, tohum=tohum)
        h = mcl.haritalar[mcl.adlar.index(dogru)]
        x0, y0, t0 = h.baslangic
        yol = yol_uret([(x0, y0), (x0 + yol_m, y0)], t0)
        return yol_boyunca(mcl, h, yol, OZ, np.random.default_rng(5000 + tohum))

    def test_benzer_cift_karar(self):
        """Dayanak: koridor_5 / koridor_6 (fark yalnız koridor_6'da, x ≈ 17,5-19 m; 12 m menzille en erken ≈ 4 m
        yolda görünebilir), başlangıç ucundan 16 m, iki yönde N tohum: ilk 3,5 m'de kararsız, kendinden emin yanlış
        adım 0, sonda doğru karar; karar yolu raporlanır."""
        for dogru in CIFT:
            erken_fark, yanlis, karar = [], 0, []
            for t in range(N_TOHUM):
                s = self.kos(dogru, 700 + t)
                erken = [tah for _, tah in s if tah.gidilen_yol_m <= 3.5]
                erken_fark.append(max(tah.fark for tah in erken))
                yanlis += sum(1 for _, tah in s if not tah.kararsiz and tah.en_olasi != dogru)
                k = next((tah.gidilen_yol_m for _, tah in s if not tah.kararsiz and tah.en_olasi == dogru), None)
                karar.append(k if k is not None else float("nan"))
                self.assertEqual(s[-1][1].en_olasi, dogru)
                self.assertFalse(s[-1][1].kararsiz)
            kaydet("benzer çift %s (%d tohum)" % (dogru, N_TOHUM), "ilk 3,5 m en büyük p1-p2", ozet(erken_fark))
            kaydet("benzer çift %s (%d tohum)" % (dogru, N_TOHUM), "kendinden emin yanlış adım; karar yolu m",
                   "%d; medyan %.2f [%.2f, %.2f]" % (yanlis, np.nanmedian(karar), np.nanmin(karar), np.nanmax(karar)))
            self.assertEqual(yanlis, 0)
            self.assertLess(max(erken_fark), 0.5)

    def test_alti_koridor_hiz(self):
        """Dayanak: hız kaybı yok — her koridorun başlangıcından 12 m (1 tohum): doğru harita, kendinden emin yanlış
        adım yok; karar yolu raporlanır (benzer çift dışında ilk metrelerde)."""
        for dogru in KORIDORLAR:
            s = self.kos(dogru, 1, yol_m=12.0)
            k = next((tah.gidilen_yol_m for _, tah in s if not tah.kararsiz and tah.en_olasi == dogru), None)
            yanlis = sum(1 for _, tah in s if not tah.kararsiz and tah.en_olasi != dogru)
            kaydet("6 koridor hız", "%s karar yolu m; yanlış kesin adım" % dogru,
                   "%s; %d" % ("%.2f" % k if k is not None else "karar yok", yanlis))
            self.assertEqual(yanlis, 0)
            if dogru not in CIFT:
                self.assertIsNotNone(k)
                self.assertLess(k, 3.0)


class BaslatPoz(unittest.TestCase):
    def test_cok_haritada_baslat_poz(self):
        """Dayanak: deney bulgusu 1 — baslat_poz çok haritada çökmemeli (eski: IndexError) ve doğru haritada kalmalı;
        öbür haritalar en az kotayla ve olasılık tabanında yaşar."""
        haritalar = ["oda_engelli", "oda_bos", "acik_alan"]
        mcl = CokHaritaliMCL(haritalar, ozellik=OZ, tohum=3)
        mcl.baslat_poz("oda_engelli", 1.5, 1.5, 0.0)
        p0 = mcl.harita_olasiliklari()
        self.assertGreater(p0["oda_engelli"], 0.999)
        sayi = mcl.tahmin().parcacik_sayilari
        self.assertTrue(all(sayi[h] > 0 for h in haritalar), sayi)
        yol = yol_uret([(1.5, 1.5), (2.5, 2.8), (4.2, 2.8), (6.0, 2.8)], 0.0)
        s = yol_boyunca(mcl, mcl.haritalar[0], yol, OZ, np.random.default_rng(9))
        self.assertTrue(all(tah.en_olasi == "oda_engelli" and not tah.kararsiz for _, tah in s))
        e, _ = konum_hatasi(s[-1][1], s[-1][0])
        kaydet("baslat_poz çok harita", "son hata m; p(oda_engelli)", "%.3f; %.6f" % (e, s[-1][1].olasiliklar["oda_engelli"]))
        self.assertLess(e, 0.15)
        # tek harita kipi de çökmez
        mcl2 = CokHaritaliMCL(haritalar, ozellik=OZ, tohum=4)
        mcl2.baslat_poz("oda_engelli", 1.5, 1.5, 0.0, diger_haritalar=False)
        s2 = yol_boyunca(mcl2, mcl2.haritalar[0], yol[:30], OZ, np.random.default_rng(9))
        # her adımda (yalnız sonda değil): parçacıksız haritalar ölçülmeden olasılık kazanmamalı
        self.assertTrue(all(tah.en_olasi == "oda_engelli" and not tah.kararsiz for _, tah in s2),
                        [(tah.en_olasi, round(tah.fark, 3)) for _, tah in s2[:5]])


class IleriTasima(unittest.TestCase):
    def test_islenmeyen_taramada_poz_ilerler(self):
        """Dayanak: deney bulgusu — işlenmeyen taramada eski poz dönüyordu (0,25 m/s'de 3,7-4,4 cm geride). Artık
        biriken odometriyle ileri taşınır; işlenen adımla süreklilik bozulmaz."""
        from konumlama import sentetik_tarama
        h = harita_yukle("oda_engelli")
        mcl = CokHaritaliMCL([h], ozellik=OZ, tohum=1, odometri_noktasi_x=0.0)   # artım = gövde merkezi
        mcl.baslat_poz("oda_engelli", 2.0, 2.8, 0.0, std_xy=0.01, std_theta=0.005)
        t0 = mcl.guncelle(sentetik_tarama(h, (2.0, 2.8, 0.0), OZ))          # ilk tarama işlenir
        self.assertTrue(t0.olcum_islendi)
        bos = {"t": 0.1, "acilar": [0.0], "mesafeler": [None]}
        dx = 0.02                                                           # eşik 0,05 m / 0,1 rad altında
        t1 = mcl.guncelle(bos, artim=(dx, 0.0, 0.0))
        self.assertFalse(t1.olcum_islendi)
        self.assertAlmostEqual(math.hypot(t1.x - t0.x, t1.y - t0.y), dx, delta=1e-9)
        t2 = mcl.guncelle(bos, artim=(dx, 0.0, 0.05))
        self.assertFalse(t2.olcum_islendi)
        self.assertAlmostEqual(math.hypot(t2.x - t0.x, t2.y - t0.y), 2 * dx, delta=1e-9)
        self.assertAlmostEqual(t2.theta - t0.theta, 0.05, delta=1e-9)

    def test_odometri_noktasi_govdeye_cevrilir(self):
        """Dayanak: U dönüşü bulgusu — odometri çeker dingilin ortasını izler (varsayılan 0,185 m geride); yerinde
        dönüşte gövde merkezi o noktanın çevresinde döner. Saf dönüş artımı dθ gövdeyi 2 r sin(dθ/2) taşımalı."""
        from konumlama import sentetik_tarama
        h = harita_yukle("oda_engelli")
        mcl = CokHaritaliMCL([h], ozellik=OZ, tohum=1)
        r = -mcl.ayar.odometri_noktasi_x
        self.assertAlmostEqual(r, 0.185)
        mcl.baslat_poz("oda_engelli", 2.0, 2.8, 0.0, std_xy=0.01, std_theta=0.005)
        t0 = mcl.guncelle(sentetik_tarama(h, (2.0, 2.8, 0.0), OZ))
        bos = {"t": 0.1, "acilar": [0.0], "mesafeler": [None]}
        t1 = mcl.guncelle(bos, artim=(0.0, 0.0, 0.08))                      # 0,1 rad eşiğinin altında: ileri taşıma
        self.assertFalse(t1.olcum_islendi)
        self.assertAlmostEqual(math.hypot(t1.x - t0.x, t1.y - t0.y), 2 * r * math.sin(0.04), delta=1e-9)
        self.assertAlmostEqual(t1.theta - t0.theta, 0.08, delta=1e-9)


class KorSektor(unittest.TestCase):
    def test_kor_pay_sensorle_ayni(self):
        """Dayanak: deney bulgusu 3 — sanal LiDAR kör sektörü her yana +5° ile maskeliyor ([134, 226]); konumlayıcı
        aynı payı kullanmalı, yoksa kenardaki ışınlar sahte "dönüş yok" sayılır."""
        oz = LidarOzellik.sozlukten({"kor_sektorler_derece": [[139.2, 220.8]]})
        self.assertEqual(oz.kor_pay_derece, 5.0)
        d = np.radians(np.array([133.5, 134.5, 139.0, 180.0, 221.0, 225.5, 226.5]))
        np.testing.assert_array_equal(oz.kor_mu(d), [False, True, True, True, True, True, False])
        if os.path.exists(OZELLIK_DOSYASI):
            gercek = LidarOzellik.dosyadan()
            self.assertTrue(gercek.kor_mu(np.radians([135.0]))[0])


# ------------------------------------------------------------ MuJoCo kaydı (--uzun)

def _mujoco_akis(kor):
    """Deneyin `tani_ikiz.kayit(kor)` akışı (aynı sürüş, aynı LiDAR tohumu). Deney dosyaları yalnız içe aktarılır;
    akış geçici klasörde önbelleklenir. MuJoCo / deney yoksa None."""
    onbellek = os.path.join(tempfile.gettempdir(), "lale_konumlama_akis", "%s_bas_t2.pkl" % kor)
    if os.path.exists(onbellek):
        with open(onbellek, "rb") as f:
            return pickle.load(f)
    try:
        import mujoco  # noqa: F401
    except ImportError:
        return None
    if not os.path.exists(os.path.join(DENEY, "tani_ikiz.py")):
        return None
    if DENEY not in sys.path:
        sys.path.insert(0, DENEY)
    import tani_ikiz
    akis = tani_ikiz.kayit(kor)
    os.makedirs(os.path.dirname(onbellek), exist_ok=True)
    with open(onbellek, "wb") as f:
        pickle.dump(akis, f)
    return akis


def _akista_kos(mcl, akis):
    onceki = None
    for tar, o, g, yol in akis:
        tah = mcl.guncelle(tar, artim=goreli(onceki, o) if onceki is not None else None)
        onceki = o
        yield tah, g, yol


@unittest.skipUnless(UZUN and KORIDOR_VAR and os.path.exists(OZELLIK_DOSYASI), "yalnız --uzun ve deney dosyalarıyla")
class MujocoKayit(unittest.TestCase):
    def test_mujoco_ikiz_20_tohum(self):
        """Dayanak: deneyin tani_ikiz kaydı (koridor_5, 912 tarama, ≈ 22 m), [koridor_5, birebir kopya], 20 MCL
        tohumu: hiçbir adımda kesin karar yok (eski: 10 tohumun 5'inde, en büyük p 0,95)."""
        akis = _mujoco_akis("koridor_5")
        if akis is None:
            self.skipTest("MuJoCo / deney yok")
        oz = LidarOzellik.dosyadan()
        veri = harita_yukle("koridor_5").veri
        pmax, kesin = [], 0
        for t in range(901, 921):
            mcl = CokHaritaliMCL(ikiz(veri, "koridor_5", "ikiz"), ozellik=oz, tohum=t)
            en = 0.0
            for tah, _, _ in _akista_kos(mcl, akis):
                en = max(en, max(tah.olasiliklar.values()))
                kesin += 0 if tah.kararsiz else 1
            pmax.append(en)
        kaydet("MuJoCo ikiz 20 tohum", "en büyük p (tohum başına)", ozet(pmax))
        kaydet("MuJoCo ikiz 20 tohum", "kesin adım toplamı", "%d / %d" % (kesin, 20 * len(akis)))
        self.assertEqual(kesin, 0)

    def test_mujoco_benzer_cift_20_tohum(self):
        """Dayanak: deneyin B_koridor_5/6_bas_t2 kayıtları, 6 koridor, 20 MCL tohumu: kendinden emin yanlış adım 0
        (eski: koridor_6'da 20'nin 8'i), 6 m'den önce eşin en büyük olasılığı ve karar yolu raporlanır."""
        oz = LidarOzellik.dosyadan()
        haritalar = [harita_yukle(k) for k in KORIDORLAR]
        for dogru, es in (("koridor_6", "koridor_5"), ("koridor_5", "koridor_6")):
            akis = _mujoco_akis(dogru)
            if akis is None:
                self.skipTest("MuJoCo / deney yok")
            es_max, yanlis_kosu, yanlis, karar, son = [], 0, 0, [], 0
            for t in range(901, 921):
                mcl = CokHaritaliMCL(haritalar, ozellik=oz, tohum=t)
                e, y, k = 0.0, 0, None
                for tah, _, yol in _akista_kos(mcl, akis):
                    if yol < 6.0:
                        e = max(e, tah.olasiliklar[es])
                    if not tah.kararsiz and tah.en_olasi != dogru:
                        y += 1
                    if k is None and not tah.kararsiz and tah.en_olasi == dogru:
                        k = yol
                es_max.append(e)
                yanlis += y
                yanlis_kosu += 1 if y else 0
                karar.append(k if k is not None else float("nan"))
                son += 1 if tah.en_olasi == dogru else 0
            kaydet("MuJoCo %s (20 tohum)" % dogru, "6 m önce eşin en büyük p", ozet(es_max))
            kaydet("MuJoCo %s (20 tohum)" % dogru, "yanlış kesinli koşu / adım; karar yolu m; sonda doğru",
                   "%d / %d; medyan %.2f [%.2f, %.2f]; %d / 20" % (yanlis_kosu, yanlis, np.nanmedian(karar),
                                                                 np.nanmin(karar), np.nanmax(karar), son))
            self.assertEqual(yanlis, 0)
            self.assertEqual(son, 20)


if __name__ == "__main__":
    unittest.main()
