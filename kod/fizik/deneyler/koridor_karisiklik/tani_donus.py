"""Tanı (v2): yerinde U dönüşünde poz koridorun nokta simetrik eşine atlıyor mu, hangi v2 değişikliği etkili?

Aynı MuJoCo kaydı (B_koridor_5_orta_t1 sürüşü, LiDAR tohumu aynı; v2 taraması = 360° + sanal LiDAR maskesi) konumlayıcıdan
5 MCL tohumuyla, üç ayarla geçirilir. Bu bir AYAR DENEMESİ DEĞİLDİR: deney sonuçları varsayılan ayarlarla alındı; burada
yalnız hangi bileşenin atlamaya yol açtığı ayrıştırılır.
  varsayilan            v2 varsayılan
  capraz_tohum=False    öteki haritaların en iyi pozlarından arama + %5 enjeksiyon kapalı
  harita_kaniti=ortalama  eski harita kanıtı tahmincisi (v1'deki gibi)
Ölçüt: U dönüşünden sonra konum "kesin" (harita doğru, kararlı, konum_kararsiz değil) iken poz hatası > 2 m olan adım.

    %V% kod\\fizik\\deneyler\\koridor_karisiklik\\tani_donus.py   -> sonuc_v2/tani_donus.json  (≈ 5 dk)
"""

import json
import math
import os
import sys

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import ortak as O  # noqa: E402
import kos as KO  # noqa: E402

DENEMELER = [("varsayilan", {}), ("capraz_tohum=False", {"capraz_tohum": False}),
             ("harita_kaniti=ortalama", {"harita_kaniti": "ortalama"})]
TOHUMLAR = [1, 2, 3, 4, 5]


def kayit(kor, bas_ad, tohum):
    ki, si = O.KORIDORLAR.index(kor), KO.BASLANGICLAR.index(bas_ad)
    yol = O.yollar(kor)[bas_ad]
    rng = np.random.default_rng(10000 + 31 * tohum + 7 * ki + si)
    p0, p1 = yol[0], yol[1]
    tg = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    yan = float(rng.uniform(-0.10, 0.10))
    sap = math.radians(float(rng.uniform(-3, 3)))
    bas = (p0[0] - math.sin(tg) * yan, p0[1] + math.cos(tg) * yan, O.sar(tg + sap))
    dz = O.Duzenek(kor, bas, lidar_tohum=1000 * tohum + 10 * ki + si, kor_maske=False)
    O.sur(dz, yol)
    return [(O.maskele(tar), o, g, y) for tar, o, g, y in O.kayittan_akis(dz)]


def kos(akis, kor, tohum, degisen):
    from konumlama import CokHaritaliMCL
    from konumlama.benzet import goreli
    mcl = CokHaritaliMCL(O.haritalar(), ozellik=O.ozellik(True), tohum=tohum, **degisen)
    onceki = None
    kotu = []
    yanlis = 0
    for tar, o, g, yol in akis:
        tah = mcl.guncelle(tar, artim=goreli(onceki, o) if onceki is not None else None)
        onceki = o
        if not tah.kararsiz and tah.en_olasi != kor:
            yanlis += 1
        if tah.en_olasi == kor and not tah.kararsiz and not tah.konum_kararsiz:
            e = math.hypot(tah.x - g[0], tah.y - g[1])
            if e > 2.0:
                kotu.append(yol)
    return dict(tohum=tohum, kotu_adim=len(kotu), ilk_kotu_yol=(round(kotu[0], 2) if kotu else None),
                yanlis_harita_adim=yanlis, son_harita=tah.en_olasi, son_kararsiz=tah.kararsiz,
                son_hata_m=round(math.hypot(tah.x - g[0], tah.y - g[1]), 2))


def main():
    kor, bas_ad, surus_tohum = "koridor_5", "orta", 1
    akis = kayit(kor, bas_ad, surus_tohum)
    sonuc = dict(kayit="B_%s_%s_t%d" % (kor, bas_ad, surus_tohum), denemeler={})
    for ad, degisen in DENEMELER:
        sonuc["denemeler"][ad] = [kos(akis, kor, 500000 + 1000 * surus_tohum + 10 * 4 + 2 + 7 * (t - 1), degisen)
                                  for t in TOHUMLAR]
        print(ad, sonuc["denemeler"][ad], flush=True)
    hedef = os.path.join(BURASI, "sonuc_v2")
    os.makedirs(hedef, exist_ok=True)
    with open(os.path.join(hedef, "tani_donus.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
