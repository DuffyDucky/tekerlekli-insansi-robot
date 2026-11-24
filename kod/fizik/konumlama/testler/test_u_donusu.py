"""Yerinde U dönüşünde poz koridorun uçtan uca (nokta simetrik) eşine çevrilmemeli.

Bulgu (deney v2, 24.11.2026): U dönüşlü 36 koşunun 6'sında poz dönüş sırasında ya da hemen sonra 180° ters döndü.
Mekanizma (BENIOKU "U dönüşünde ters poz"): yerinde dönüşte gövde merkezi dönme noktasının (çeker dingil) çevresinde
öteleşir, odometri saf dönüş bildirir; doğru mod geride kalır. Eski "çapraz enjeksiyon" öteki haritaların en iyi
pozundan yerel aramayla iyileştirilmiş ayna poza parçacık koyup en iyi parçacığın önselini veriyordu; ayna mod tek
adımda ağırlığı alıyordu. Ölçüt (deneyinkiyle aynı): doğru haritada konum "kesin" iken hata > 0,5 m olan adım yok.
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
from konumlama import CokHaritaliMCL, LidarOzellik, sentetik_tarama
from konumlama.benzet import goreli
from konumlama.harita2b import HARITA_KLASORU
from konumlama.tarama import OZELLIK_DOSYASI

UZUN = os.environ.get("LALE_KONUM_UZUN") == "1"
DENEY = os.path.join(FIZIK, "deneyler", "koridor_karisiklik")
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
HAZIR = (all(os.path.exists(os.path.join(HARITA_KLASORU, k + ".json")) for k in KORIDORLAR)
         and os.path.exists(OZELLIK_DOSYASI))


def _sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def sentetik_u_akisi(merkez_geri=0.185, donus_olcek=1.14, y=6.2):
    """koridor_5 ortasından (x 13) sona (x 24,2), yerinde U dönüşü, 7,5 m geri. Dönüşte gövde merkezi 0,185 m arkadaki
    noktanın çevresinde döner (ONERI çeker dingili), odometri saf dönüş ve %14 fazla bildirir (MuJoCo B_koridor_5_orta_t1
    kaydında ölçülen: 136° dönüşte gerçek 0,33 m öteleme, odometri 0 m ve 155°). -> [(gerçek poz, odometri artımı)]"""
    poz = [(x, y, 0.0) for x in np.arange(13.0, 24.2, 0.025)]
    art = [(0.025, 0.0, 0.0)] * (len(poz) - 1)
    x, yy, th = poz[-1]
    cx, cy = x - merkez_geri, yy
    n = int(math.ceil(math.pi / 0.08))                  # 0,8 rad/s, 10 Hz
    for i in range(n):
        t2 = th + math.pi * (i + 1) / n
        poz.append((cx + merkez_geri * math.cos(t2), cy + merkez_geri * math.sin(t2), _sar(t2)))
        art.append((0.0, 0.0, donus_olcek * math.pi / n))
    x, yy, th = poz[-1]
    for i in range(1, 300):
        poz.append((x - 0.025 * i, yy, th))
        art.append((0.025, 0.0, 0.0))
    return poz, art


def kos_ve_say(mcl, kor, adimlar):
    """adimlar: [(tarama, artım | None, gerçek poz)] -> (konum kesin-yanlış adım, ilk yolu, son hata m, son harita)."""
    kotu, ilk = 0, None
    for i, (tar, art, g) in enumerate(adimlar):
        tah = mcl.guncelle(tar, artim=art)
        e = math.hypot(tah.x - g[0], tah.y - g[1])
        if tah.en_olasi == kor and not tah.kararsiz and not tah.konum_kararsiz and e > 0.5:
            kotu += 1
            ilk = tah.gidilen_yol_m if ilk is None else ilk
    return kotu, ilk, e, tah.en_olasi


def _u_kaydi():
    """Deneyin `tani_donus.kayit("koridor_5", "orta", 1)` akışı (B_koridor_5_orta_t1 sürüşü; v2 maskesi). Geçici
    klasörde önbelleklenir; önbellek yoksa MuJoCo + deney klasörüyle üretilir, ikisi de yoksa None."""
    onbellek = os.path.join(tempfile.gettempdir(), "lale_konumlama_akis", "koridor_5_orta_t1.pkl")
    if os.path.exists(onbellek):
        with open(onbellek, "rb") as f:
            return pickle.load(f)
    try:
        import mujoco  # noqa: F401
    except ImportError:
        return None
    if not os.path.exists(os.path.join(DENEY, "tani_donus.py")):
        return None
    if DENEY not in sys.path:
        sys.path.insert(0, DENEY)
    import tani_donus
    akis = tani_donus.kayit("koridor_5", "orta", 1)
    os.makedirs(os.path.dirname(onbellek), exist_ok=True)
    with open(onbellek, "wb") as f:
        pickle.dump(akis, f)
    return akis


@unittest.skipUnless(HAZIR, "koridor_1..6 / lidar_ozellik.json yok")
class UDonusu(unittest.TestCase):
    def test_sentetik_u_donusu(self):
        """Dayanak: kayda bağlı olmayan U dönüşü (dönme merkezi gövdenin 0,185 m arkasında, odometri %14 fazla dönüş),
        6 koridor, küresel başlangıç: konum kesin-yanlış adım 0, sonda doğru koridor ve hata < 0,3 m. Tohum 0-3 (--uzun
        0-11). Çapraz enjeksiyonlu sürüm (362cd4d) aynı kurulumda (dönme noktası 0,18 m) 12 tohumun 5'inde 12-319
        konum kesin-yanlış adım verdi (0-3 içinde tohum 2: 66 adım)."""
        oz = LidarOzellik.dosyadan()
        poz, art = sentetik_u_akisi()
        sonuc = []
        for t in range(12 if UZUN else 4):
            rng = np.random.default_rng(800 + t)
            mcl = CokHaritaliMCL(KORIDORLAR, ozellik=oz, tohum=900 + t)
            h = mcl.haritalar[mcl.adlar.index("koridor_5")]
            adimlar = []
            for i, p in enumerate(poz):
                a = None
                if i > 0:
                    dx, dy, dth = art[i - 1]
                    k = 1.0 + rng.normal(0, 0.02)
                    a = (dx * k, dy * k, dth + rng.normal(0, 0.002))
                adimlar.append((sentetik_tarama(h, p, oz, rng), a, p))
            sonuc.append(kos_ve_say(mcl, "koridor_5", adimlar))
        kaydet("U dönüşü sentetik (%d tohum)" % len(sonuc), "kesin-yanlış adım (tohum başına); son hata en çok m",
               "%s; %.3f" % (", ".join(str(s[0]) for s in sonuc), max(s[2] for s in sonuc)))
        self.assertEqual(sum(s[0] for s in sonuc), 0, sonuc)
        self.assertTrue(all(s[3] == "koridor_5" and s[2] < 0.3 for s in sonuc), sonuc)

    def test_mujoco_u_donusu(self):
        """Dayanak: deney v2'de çevrilen B_koridor_5_orta_t1 kaydı (1399 tarama, ≈ 24 m, U dönüşü 11,2 m'de), deneyin
        tani_donus tohumları 501042 + 7k: k = 0-2 (--uzun 0-4). Çapraz enjeksiyonlu sürüm: 5 tohumun 3'ünde çevrilme."""
        akis = _u_kaydi()
        if akis is None:
            self.skipTest("U dönüşü kaydı yok (MuJoCo / deney klasörü yok, önbellek yok)")
        oz = LidarOzellik.dosyadan()
        sonuc = []
        for k in range(5 if UZUN else 3):
            mcl = CokHaritaliMCL(KORIDORLAR, ozellik=oz, tohum=501042 + 7 * k)
            adimlar, onceki = [], None
            for tar, o, g, _ in akis:
                adimlar.append((tar, goreli(onceki, o) if onceki is not None else None, g))
                onceki = o
            sonuc.append(kos_ve_say(mcl, "koridor_5", adimlar))
        kaydet("U dönüşü MuJoCo K5 orta t1 (%d tohum)" % len(sonuc), "kesin-yanlış adım (tohum başına); son hata en çok m",
               "%s; %.3f" % (", ".join(str(s[0]) for s in sonuc), max(s[2] for s in sonuc)))
        self.assertEqual(sum(s[0] for s in sonuc), 0, sonuc)
        self.assertTrue(all(s[3] == "koridor_5" for s in sonuc), sonuc)


if __name__ == "__main__":
    unittest.main()
