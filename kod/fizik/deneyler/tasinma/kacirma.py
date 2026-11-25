"""Taşınma ("kaçırılmış robot") deneyi: ortak parçalar (yollar, tohumlar, kümeler, taşıma pozları, hakem tarafı).

Önceki aşamanın bozulma altyapısı (`../harita_eskimesi`: `ortak.dunya_kur`, `benzet2b.Benzet2B`, `kos2b`, `insan`)
DEĞİŞTİRİLMEDEN içe aktarılır. Taşıma yalnız benzetici / hakem tarafında olur: robotun gerçek pozu bir anda başka
yere konur, odometri bunu görmez (teker dönmez), beyin yalnız taramayı ve odometri artımını görür.

Taşıma türleri (TURLER):
  ayni_uzak      aynı koridorda başka yer: orta hat çizgesinde rastgele poz (yan ±0,45 m, yön rastgele), şimdiki
                 yerden en az min(5 m, koridor boyunun %40'ı) uzakta
  ters180        aynı yerde gövde merkezi çevresinde 180° çevrilmiş
  kucuk          orta hat boyunca 1-3 m ileri ya da geri kaydırılmış, yan ±0,2 m, yön ±15°
  baska_koridor  başka bir koridorun (öbür 5'ten biri) orta hattında rastgele poz
Bütün yerleştirmeler `senaryo_kayip.rastgele_birak` ile aynı geçerlilik kuralına uyar: dönme merkezi (arka dingil)
her yüzeyden >= 0,60 m, gövde çevresi >= 0,05 m, serbest alanda.
"""

import json
import math
import os
import sys
import time
import zlib

BURASI = os.path.dirname(os.path.abspath(__file__))
DENEYLER = os.path.dirname(BURASI)
HE = os.path.join(DENEYLER, "harita_eskimesi")
if HE not in sys.path:
    sys.path.insert(0, HE)
# önceki aşamanın ortak.py'si (yollar, dunya_kur, dusuk_oncelik) ayrı adla: koridor_karisiklik'in ortak.py'siyle
# aynı süreçte (gerileme.py) çakışmasın
if "he_ortak" in sys.modules:
    HO = sys.modules["he_ortak"]
else:
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location("he_ortak", os.path.join(HE, "ortak.py"))
    HO = _iu.module_from_spec(_sp)
    sys.modules["he_ortak"] = HO
    _sp.loader.exec_module(HO)

FIZIK = HO.FIZIK
SONUC = os.path.join(BURASI, "sonuc")
HAM = os.path.join(SONUC, "ham")
GORSEL = os.path.join(BURASI, "gorsel")
DURUM = os.path.join(BURASI, ".durum")
KORIDORLAR = HO.KORIDORLAR
VARIS_PAYI = HO.VARIS_PAYI
HATA_ESIK = 0.5                       # m: bunun üstü "yanlış poz"
YON_ESIK = math.radians(30.0)         # yön hatası bunun üstündeyse de "yanlış poz" (hata 9,99 yazılır)

TURLER = ["ayni_uzak", "ters180", "kucuk", "baska_koridor"]
# Yanlış alarm koşulları (taşıma yok): önceki aşamanın 2. kademesi (insan 1 / 10 m, eşya 1 / 10 m) ve ikisi birden
# + karma_3 (insan 2 / 10 m + eşya 2 / 10 m, 3. kademe; geliştirmede koşulmadı, yalnız sınamada)
YA_KOSULLARI = {"taban": {}, "insan_2": {"insan": 1.0}, "esya_2": {"esya": 1.0}, "karma_2": {"insan": 1.0, "esya": 1.0},
                "karma_3": {"insan": 2.0, "esya": 2.0}}
SENARYOLAR = ["ab", "cok"]           # ab: AbBeyni (tek harita); cok: 6 harita, bilinen başlangıç (KayipBeyni izleme evresi)
SURUMLER = ["v3", "algi"]

# Kümeler: geliştirme (eşikler bunda ayarlandı) ve sınama (hüküm bunda). Tohumlar ve koridorlar ayrı yazılır.
GELISTIRME = dict(koridorlar=("koridor_2", "koridor_3", "koridor_5"), tohumlar=(901, 902, 903))
SINAMA = dict(koridorlar=tuple(KORIDORLAR), tohumlar=(1, 2))
SINAMA_DISI_HARITA = ("koridor_1", "koridor_4", "koridor_6")   # geliştirmede hiç kullanılmamış haritalar


def tohum(*parca):
    return zlib.crc32("|".join(map(str, parca)).encode()) & 0x7FFFFFFF


def durum_yaz(satir):
    with open(DURUM, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), satir))


def dusuk_oncelik():
    HO.dusuk_oncelik()


# ------------------------------------------------------------------ taşıma pozları (hakem tarafı)
def _gecerli(h, dw, x, y, th):
    """Bırakma kuralı (senaryo_kayip.rastgele_birak ile aynı) + dünyada çarpışma yok."""
    import numpy as np
    from benzet2b import ROBOT
    from gezinme import senaryo_ortak as SO
    rx, ry = x + SO.DONME_X * math.cos(th), y + SO.DONME_X * math.sin(th)
    if float(h.geometri_uzakligi(np.array([rx]), np.array([ry]))[0]) < 0.60:
        return False
    P = np.array(SO._govde_noktalari(x, y, th))
    if float(h.geometri_uzakligi(P[:, 0], P[:, 1]).min()) < 0.05:
        return False
    if not bool(h.serbest_mi(np.array([x]), np.array([y]))[0]):
        return False
    if dw is not None and dw.temas((x, y, th), ROBOT, pay=0.05):
        return False
    return True


def _hat_boyu(kor):
    from gezinme import rota as R
    cz = R.Cizge(R.sahne(kor))
    return sum(math.hypot(cz.dugum[j][0] - cz.dugum[i][0], cz.dugum[j][1] - cz.dugum[i][1]) for i, j in cz.parcalar)


def tasima_pozu(tur, kor, simdi, rng, dunya_veri=None):
    """-> (yeni koridor, (x, y, th) gövde merkezi, harita = dünya çerçevesi). rng: random.Random."""
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.beyinler import haritalar
    from kesif.benzet2b import Dunya2B
    x0, y0, th0 = simdi
    if tur == "baska_koridor":
        diger = [k for k in KORIDORLAR if k != kor]
        yeni = diger[rng.randrange(len(diger))]
        h = haritalar([yeni])[0]
        for _ in range(200):
            p = SO.rastgele_birak(yeni, rng)
            if _gecerli(h, None, *p):
                return yeni, p
        raise RuntimeError("baska koridorda yer yok")
    h = haritalar([kor])[0]
    dw = Dunya2B(dunya_veri) if dunya_veri is not None else None
    if tur == "ters180":
        p = (x0, y0, HO_sar(th0 + math.pi))
        if _gecerli(h, dw, *p):
            return kor, p
        # duvara çok yakınsa: orta hatta en yakın noktada çevir
        q, _, _ = R.Cizge(R.sahne(kor)).izdusum(x0, y0)
        return kor, (q[0], q[1], HO_sar(th0 + math.pi))
    if tur == "ayni_uzak":
        en_az = min(5.0, 0.4 * _hat_boyu(kor))
        for _ in range(500):
            p = SO.rastgele_birak(kor, rng)
            if math.hypot(p[0] - x0, p[1] - y0) >= en_az and _gecerli(h, dw, *p):
                return kor, p
        raise RuntimeError("ayni koridorda uzak yer yok")
    if tur == "kucuk":
        cz = R.Cizge(R.sahne(kor))
        q, (i, j), _ = cz.izdusum(x0, y0)
        a, b = cz.dugum[i], cz.dugum[j]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for _ in range(500):
            d = rng.uniform(1.0, 3.0) * (1 if rng.random() < 0.5 else -1)
            yan = rng.uniform(-0.2, 0.2)
            cx, cy = q[0] + ux * d - uy * yan, q[1] + uy * d + ux * yan
            # kırılmayı geçen kaydırma: yeni noktayı çizgeye izdüşür (orta hat üstünde kalsın)
            q2, _, dd = cz.izdusum(cx, cy)
            if dd > 0.3:
                cx, cy = q2[0] - uy * yan, q2[1] + ux * yan
            if math.hypot(cx - x0, cy - y0) < 0.9:
                continue
            th = HO_sar(th0 + math.radians(rng.uniform(-15.0, 15.0)))
            if _gecerli(h, dw, cx, cy, th):
                return kor, (cx, cy, th)
        raise RuntimeError("kucuk kaydirma yeri yok")
    raise KeyError(tur)


def HO_sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


# ------------------------------------------------------------------ görevler
def gorevler(kume, senaryolar=SENARYOLAR, surumler=SURUMLER, turler=TURLER, ya=tuple(YA_KOSULLARI)):
    """kume: "gelistirme" | "sinama". Her görev: senaryo x sürüm x (taşıma türü | yanlış alarm koşulu) x koridor x tohum."""
    K = GELISTIRME if kume == "gelistirme" else SINAMA
    out = []
    for sn in senaryolar:
        for sr in surumler:
            for kosul in list(turler) + ["ya_" + y for y in ya]:
                for kor in K["koridorlar"]:
                    for t in K["tohumlar"]:
                        out.append(dict(id="%s_%s_%s_%s_%d" % (sn, sr, kosul, kor, t), kume=kume, senaryo=sn,
                                        surum=sr, kosul=kosul, koridor=kor, tohum=t))
    return out


def ham_yol(g, alt="2b"):
    return os.path.join(HAM, alt, g["kume"], g["id"] + ".json")


def json_yaz(yol, veri):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol + ".tmp", "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, default=str)
    os.replace(yol + ".tmp", yol)
