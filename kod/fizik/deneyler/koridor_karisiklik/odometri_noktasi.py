"""Denetim: deney kaydındaki odometri artımı robotun hangi noktasının artımı?

Konumlayıcı (v3) `MCLAyarlari.odometri_noktasi_x` ile artımın hangi noktada verildiğini varsayar (varsayılan -0,185 m: arka
çeker dingilin ortası; 0 = gövde merkezi). Deney odometrisi `lidar.DeneyKaydi`'nin tik toplamından (diferansiyel sürüş,
ds = (dl + dr) / 2): bu çeker dingil ortasının hareketidir; yer gerçeği ise taban gövdesinin (MuJoCo `taban`) pozudur.
Burada bir U dönüşlü kayıtta (B_koridor_5_orta_t1 sürüşü) her ardışık tarama çifti için odometri artımı, aday noktalar
p = (px, 0) için yer gerçeğinden hesaplanan nokta artımıyla karşılaştırılır; en iyi uyan px odometrinin noktasıdır.

    %V% kod\\fizik\\deneyler\\koridor_karisiklik\\odometri_noktasi.py   -> sonuc_v3/odometri_noktasi.json
"""

import json
import math
import os
import sys

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import ortak as O  # noqa: E402
import tani_donus as TD  # noqa: E402


def goreli(a, b):
    c, s = math.cos(a[2]), math.sin(a[2])
    dx, dy = b[0] - a[0], b[1] - a[1]
    return np.array([c * dx + s * dy, -s * dx + c * dy, O.sar(b[2] - a[2])])


def nokta(p, px):
    return (p[0] + px * math.cos(p[2]), p[1] + px * math.sin(p[2]), p[2])


def main():
    akis = TD.kayit("koridor_5", "orta", 1)
    odo = [a[1] for a in akis]
    ger = [a[2] for a in akis]
    adaylar = [round(x, 3) for x in np.arange(-0.30, 0.101, 0.005)]
    sonuc = {}
    # yalnız dönüş adımları (yer gerçeğinde |dθ| > 0,05 rad / tarama): nokta seçimi burada belirleyici
    don = [i for i in range(1, len(akis)) if abs(O.sar(ger[i][2] - ger[i - 1][2])) > 0.05]
    for px in adaylar:
        h = [goreli(nokta(ger[i - 1], px), nokta(ger[i], px))[:2] - goreli(odo[i - 1], odo[i])[:2] for i in don]
        sonuc[px] = float(np.sqrt(np.mean(np.sum(np.square(h), axis=1))))
    en_iyi = min(sonuc, key=sonuc.get)
    out = dict(kayit="B_koridor_5_orta_t1", donus_adimi=len(don), en_iyi_px_m=en_iyi,
               kok_ortalama_kare_hata_m={"%.3f" % k: round(v, 5) for k, v in sonuc.items()},
               px_0=round(sonuc[0.0], 5), px_eksi_0185=round(sonuc[-0.185], 5))
    hedef = os.path.join(BURASI, "sonuc_v3")
    os.makedirs(hedef, exist_ok=True)
    with open(os.path.join(hedef, "odometri_noktasi.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("dönüş adımı", len(don), "en iyi px", en_iyi, "hata(px=0)", out["px_0"], "hata(px=-0,185)", out["px_eksi_0185"])


if __name__ == "__main__":
    main()
