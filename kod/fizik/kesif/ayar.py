"""Parametre ayarı: eğitim labirentlerinde (bellekte üretilir; 13x13 / 17x17 sınama labirentleri KULLANILMAZ) rastgele
arama, amaç hakem puanı.

    py -3 -m kesif.ayar ara --n 16          # aday sayısı; sonuç sonuc/ham/ayar_arama.csv + en iyi sonuc/ayar_en_iyi.json
    py -3 -m kesif.ayar sina               # en iyi ayarla sınama kümesi (kos.LABIRENTLER x 5 tohum) -> sonuc/ayar_sonra.csv

Amaç (araştırma notu §5): J = ortalama(puan) + 0,5 * ortalama(en kötü %20 puan). Kuyruğu ödüllendirir: tek tük
başarısızlığı olan ama ortalaması yüksek aday yerine sağlam aday seçilir. Taban aday (varsayılan ayar) da aynı
tohumlarla ölçülür; en iyi aday tabanı geçmezse "kazanç yok" yazılır.
"""

import argparse
import copy
import csv
import json
import os
import random

from ._yol import durum_yaz, dusuk_oncelik
from .kos import HAM, LABIRENTLER, SONUC, TOHUMLAR, calistir

EGITIM = [("uret", 7, 7, 101, "geri_izleme"), ("uret", 7, 7, 102, "wilson"), ("uret", 9, 9, 103, "geri_izleme"),
          ("uret", 9, 9, 104, "wilson"), ("uret", 9, 9, 105, "agac:0.75"), ("uret", 11, 11, 106, "geri_izleme"),
          ("uret", 11, 11, 107, "wilson"), ("uret", 11, 11, 108, "agac:0.75")]

# (yol, alt, üst, tür)
UZAY = [("v_seyir", 0.22, 0.39, float),
        ("plan_aralik_s", 0.5, 2.0, float),
        ("sinir.w_don", 0.0, 1.0, float),
        ("sinir.w_dis", 0.0, 6.0, float),
        ("sinir.w_uzak", 0.0, 2.0, float),
        ("sinir.hister_m", 0.5, 3.0, float),
        ("sinir.bakis_m", 0.7, 1.3, float),
        ("bakis_sure_s", 2.0, 6.0, float),
        ("slam.yaz_w_maks", 0.4, 1.2, float)]


def ayar_uygula(ayar, degis):
    a = copy.deepcopy(ayar)
    for yol, v in degis.items():
        hedef = a
        parca = yol.split(".")
        for p in parca[:-1]:
            hedef = getattr(hedef, p)
        setattr(hedef, parca[-1], v)
    return a


def aday_uret(rng):
    return {yol: round(t(rng.uniform(lo, hi)), 3) for yol, lo, hi, t in UZAY}


def J(puanlar):
    p = sorted(puanlar)
    k = max(1, len(p) // 5)
    return sum(p) / len(p) + 0.5 * sum(p[:k]) / k


def degerlendir(degis, ad, tohumlar=(0,), csv_yolu=None, is_sayisi=2):
    from .beyin import BeyinAyari
    a = ayar_uygula(BeyinAyari(), degis)
    G = [{"deney": "ayar_ara", "strateji": "kesif", "sahne": s, "tohum": t, "donus_hata": 0.14, "ayar": a,
          "ayar_ad": ad} for s in EGITIM for t in tohumlar]
    S = calistir(G, csv_yolu or os.path.join(HAM, "ayar_arama.csv"), is_sayisi)
    puan = [float(s.get("puan") or -300.0) for s in S]
    return J(puan), puan


def ara(n, tohum=7, is_sayisi=2):
    rng = random.Random(tohum)
    os.makedirs(HAM, exist_ok=True)
    ozet = os.path.join(HAM, "ayar_ozet.csv")
    sonuc = []
    adaylar = [("taban", {})] + [("aday%02d" % k, aday_uret(rng)) for k in range(n)]
    for ad, d in adaylar:
        j, puan = degerlendir(d, ad, is_sayisi=is_sayisi)
        sonuc.append((j, ad, d))
        with open(ozet, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([ad, round(j, 1), round(sum(puan) / len(puan), 1), json.dumps(d)])
        durum_yaz("ayar %s J=%.1f" % (ad, j))
        print("AYAR", ad, round(j, 1), d, flush=True)
    sonuc.sort(key=lambda x: -x[0])
    taban = next(x for x in sonuc if x[1] == "taban")
    en = sonuc[0]
    kayit = {"en_iyi": en[1], "J": en[0], "degis": en[2], "taban_J": taban[0],
             "kazanc": en[1] != "taban", "egitim": [list(e) for e in EGITIM], "tohumlar": [0],
             "siralama": [(round(j, 1), a, d) for j, a, d in sonuc]}
    with open(os.path.join(SONUC, "ayar_en_iyi.json"), "w", encoding="utf-8") as f:
        json.dump(kayit, f, ensure_ascii=False, indent=1)
    return kayit


def sina(is_sayisi=2):
    from .beyin import BeyinAyari
    with open(os.path.join(SONUC, "ayar_en_iyi.json"), encoding="utf-8") as f:
        k = json.load(f)
    if not k.get("kazanc"):
        print("kazanç yok: taban en iyi")
        return
    a = ayar_uygula(BeyinAyari(), k["degis"])
    G = [{"deney": "ayar_sonra", "strateji": "kesif", "sahne": s, "tohum": t, "donus_hata": 0.14, "ayar": a,
          "ayar_ad": k["en_iyi"]} for s in LABIRENTLER for t in TOHUMLAR]
    G.sort(key=lambda g: -int(g["sahne"].split("_")[1].split("x")[0]))
    calistir(G, os.path.join(SONUC, "ayar_sonra.csv"), is_sayisi)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("is_", choices=["ara", "sina"])
    p.add_argument("--n", type=int, default=16)
    p.add_argument("--is", dest="is_sayisi", type=int, default=2)
    a = p.parse_args(argv)
    dusuk_oncelik()
    if a.is_ == "ara":
        print(ara(a.n, is_sayisi=a.is_sayisi))
    else:
        sina(a.is_sayisi)


if __name__ == "__main__":
    main()
