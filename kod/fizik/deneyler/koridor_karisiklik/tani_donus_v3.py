"""Tanı (v3): U dönüşü yapan 36 kayıt × 3 konumlayıcı tohumu; poz koridorun uçtan uca eşine çevriliyor mu?

Kayıtlar deneyin tam kayıtlarıdır (akis/B ve akis/C, "orta" başlangıçlı koşular; fizik koşulmaz). Konumlayıcı varsayılan
ayarlarla, v3 taraması (sanal LiDAR'ın kör maskesi uygulanmış) ile beslenir. Tohumlar: deneydeki MCL tohumu ve
+1, +2. Çevrilme ölçütü deneyinkiyle aynı (karsilastir.olaylar): doğru koridor, kararlı, konum kesin, poz hatası > 0,5 m
ve yön farkı > 150°.

    OMP_NUM_THREADS=1 %V% kod\\fizik\\deneyler\\koridor_karisiklik\\tani_donus_v3.py   -> sonuc_v3/tani_donus_v3.json
"""

import json
import math
import multiprocessing as mp
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)


def _bir(arg):
    g, tohum = arg
    import kos as K
    import ortak as O
    akis, ek = K.akis_oku(g)
    akis = [(O.maskele(t), o, gg, y) for t, o, gg, y in akis]
    adimlar, _, _ = O.mcl_kos(akis, g["kor"], tohum, kor=True)
    kor = g["kor"]
    cev = [a for a in adimlar if a["en"] == kor and not a["kararsiz"] and not a["konum_kararsiz"]
           and math.hypot(a["ileri"], a["yan"]) > O.ESIK_KONUM_YANLIS
           and abs((a["th"] - a["gth"] + math.pi) % (2 * math.pi) - math.pi) > math.radians(150)]
    yk = [a for a in adimlar if not a["kararsiz"] and a["en"] != kor]
    return dict(id=g["id"], tohum=tohum, cevrilme_adim=len(cev), ilk_yol=(round(cev[0]["yol"], 2) if cev else None),
                yanlis_koridor_adim=len(yk), son_dogru=(adimlar[-1]["en"] == kor and not adimlar[-1]["kararsiz"]))


def main():
    import kos as K
    gl = [g for g in K.gorevler(["B", "C"]) if g["baslangic"] == "orta"]
    isler = []
    for g in gl:
        ki, si = K.O.KORIDORLAR.index(g["kor"]), K.BASLANGICLAR.index(g["baslangic"])
        t0 = 500000 + 1000 * g["tohum"] + 10 * ki + si
        isler += [(g, t0 + d) for d in (0, 1, 2)]
    with mp.Pool(7) as p:
        sonuc = p.map(_bir, isler, chunksize=1)
    out = dict(kayit_sayisi=len(gl), kosu=len(sonuc), cevrilen=sum(1 for x in sonuc if x["cevrilme_adim"]),
               yanlis_koridor_kosu=sum(1 for x in sonuc if x["yanlis_koridor_adim"]),
               son_dogru=sum(1 for x in sonuc if x["son_dogru"]), kosular=sonuc)
    with open(os.path.join(BURASI, "sonuc_v3", "tani_donus_v3.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print({k: v for k, v in out.items() if k != "kosular"})


if __name__ == "__main__":
    os.environ.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    main()
