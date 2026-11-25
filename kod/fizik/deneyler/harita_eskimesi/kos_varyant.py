"""İsteğe bağlı dayanıklılık varyantı (VARSAYILANLAR DEĞİŞMEDİ; yalnız bu deneyde, beyin kurulduktan sonra).

Varyant "izleme": A'dan B'ye beyninde (başlangıç biliniyor, tek harita) artırılmış MCL'nin rastgele saçması kapalı
(`mcl.ayar.rastgele_en_cok = 0`). Gerekçe (geliştirme tohumlarında, ana ızgaranın t = 1, 2 koşularında gözlendi): dünya
haritadan saptığında (kapı, eşya) ölçüm uyumu düşer, artırılmış MCL parçacıkların %10'una dek serbest alana saçar;
periyodik koridorda saçılan parçacık "takma" (alias) bir yerde taramayı daha iyi açıklar ve konum oraya atlar.

Sınama: ana ızgaradan AYRI tohumlar t ∈ {3, 4} (başlangıç sapması, MCL, dünya bozucusu ve benzetici gürültüsü bu
tohumlardan), aynı tohumlarda varsayılan beyin ile birlikte koşulur:

    py -3 kos_varyant.py [--isci 3] [--kosul taban,kapi_2,...]     # -> sonuc/ham/varyant/<varyant>_<id>.json
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ortak  # noqa: E402
import kos2b  # noqa: E402

TOHUMLAR = (3, 4)
VARSAYILAN_KOSULLAR = ["taban", "kapi_1", "kapi_2", "kapi_3", "kapi_4", "esya_2", "esya_4", "insan_2", "insan_4",
                       "cam_2", "cam_4", "donussuz_2", "donussuz_4", "okul_hafif", "okul_orta", "okul_agir"]


def izleme(beyin):
    beyin.mcl.ayar.rastgele_en_cok = 0.0


VARYANTLAR = {"varsayilan": None, "izleme": izleme}


def gorevler(kosul_sec):
    out = []
    for k in ortak.kosullar():
        if k["id"] not in kosul_sec:
            continue
        for kor in ortak.KORIDORLAR:
            for t in TOHUMLAR:
                for v in VARYANTLAR:
                    out.append(dict(id="%s_ab_%s_%s_%d" % (v, k["id"], kor, t), varyant=v, senaryo="ab", kosul=k["id"],
                                    etken=k["etken"], alt=k["alt"], kademe=k["kademe"], deger=k["deger"], koridor=kor,
                                    tohum=t))
    return out


def yol(g):
    return os.path.join(ortak.HAM, "varyant", g["id"] + ".json")


def kos_gorev(g):
    y = yol(g)
    if os.path.exists(y):
        return g["id"], "var"
    t0 = time.time()
    try:
        s = kos2b.kos_ab(dict(g), beyin_ayar=VARYANTLAR[g["varyant"]])
    except Exception as hata:
        import traceback
        s = dict(g, basari=False, neden="istisna: %r" % hata, iz=traceback.format_exc())
    s["id"] = g["id"]
    s["varyant"] = g["varyant"]
    s["duvar_toplam_s"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(y), exist_ok=True)
    with open(y, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, default=str)
    return g["id"], "basari=%s" % s.get("basari")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--isci", type=int, default=3)
    ap.add_argument("--kosul", default=",".join(VARSAYILAN_KOSULLAR))
    a = ap.parse_args()
    ortak.dusuk_oncelik()
    G = [g for g in gorevler(a.kosul.split(",")) if not os.path.exists(yol(g))]
    ortak.durum_yaz("varyant basladi: %d gorev" % len(G))
    import multiprocessing as mp
    with mp.Pool(a.isci, initializer=ortak.dusuk_oncelik, maxtasksperchild=40) as havuz:
        n = 0
        for gid, msj in havuz.imap_unordered(kos_gorev, G):
            n += 1
            if n % 20 == 0:
                ortak.durum_yaz("varyant %d/%d %s %s" % (n, len(G), gid, msj))
    ortak.durum_yaz("varyant bitti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
