"""Ek koşular (tamamlama turu): ana ızgarada koşulmamış kayıp robot koşulları, ana ızgarayla AYNI tohumlarla.

    py -3 kos_ek.py --isci 2 [--kosul genislik_1,genislik_2,genislik_3,genislik_4]   # -> sonuc/ham/2b/kayip_ek/<id>.json

Koşu tanımı `kos2b.kos_kayip` (değiştirilmedi; tohumlar bırakma 20000 + 100 k + i, MCL 600000 + 10 k + i, i ∈ {0, 1},
dünya bozucusu crc32("kayip", etken, koridor, i)). Ham sonuçlar ana ızgaranın klasörüne DEĞİL `kayip_ek/`'e yazılır,
`analiz.py` bunları `kayip_ek_2b.csv`'ye ayrı yazar (ana `kayip_2b.csv` değişmez), kırılma tablosunda birleştirir."""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ortak  # noqa: E402
import kos2b  # noqa: E402

VARSAYILAN = ["genislik_1", "genislik_2", "genislik_3", "genislik_4"]


def yol(g):
    return os.path.join(ortak.HAM, "2b", "kayip_ek", g["id"] + ".json")


def kos_gorev(g):
    y = yol(g)
    if os.path.exists(y):
        return g["id"], "var"
    t0 = time.time()
    try:
        s = kos2b.kos_kayip(dict(g))
    except Exception as hata:
        import traceback
        s = dict(g, basari=False, neden="istisna: %r" % hata, iz=traceback.format_exc())
    s["duvar_toplam_s"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(y), exist_ok=True)
    with open(y + ".tmp", "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, default=str)
    os.replace(y + ".tmp", y)
    return g["id"], "basari=%s neden=%s" % (s.get("basari"), s.get("neden"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--isci", type=int, default=2)
    ap.add_argument("--kosul", default=",".join(VARSAYILAN))
    a = ap.parse_args()
    ortak.dusuk_oncelik()
    G = [g for g in kos2b.gorevler("kayip", a.kosul.split(",")) if not os.path.exists(yol(g))]
    ortak.durum_yaz("kos_ek kayip basladi: %d gorev" % len(G))
    import multiprocessing as mp
    with mp.Pool(a.isci, initializer=ortak.dusuk_oncelik, maxtasksperchild=20) as havuz:
        n = 0
        for gid, msj in havuz.imap_unordered(kos_gorev, G):
            n += 1
            ortak.durum_yaz("kayip_ek %d/%d %s %s" % (n, len(G), gid, msj))
    ortak.durum_yaz("kos_ek kayip bitti (%d)" % len(G))
    return 0


if __name__ == "__main__":
    sys.exit(main())
