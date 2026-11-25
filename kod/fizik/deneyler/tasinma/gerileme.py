"""Gerileme denetimi: koridor_karisiklik deneyinin tam kayıtları (`../koridor_karisiklik/akis/`, fizik koşulmaz)
konumlayıcıya v3 taraması (kör maske) ile yeniden beslenir; "algi" sürümünün konumlayıcı düzeyindeki kısmı uygulanır:

  - kurma: bilinen başlangıçta (D) baştan; küresel konumlamada (B, C) KayipBeyni'nin karar kuralı sağlanınca (en olası
    harita aynı, `kararsiz` ve `konum_kararsiz` False, p >= 0,9, art arda 10 işlenen tarama)
  - kurulu iken her taramada `algi.TasinmaAlgisi` (aynı eşikler); "kayboldum" -> `mcl.baslat()` (küresel yeniden
    başlatma), kurma yeniden beklenir.
Sürüş yok (kayıt açık çevrim): beynin durma / yavaşlama / keşif davranışı burada sınanmaz, yalnız yanlış alarm ve
yeniden başlatmanın yanlış koridora kesin karar üretip üretmediği.

Algı konumlayıcının durumuna ve RNG'sine dokunmaz: hiç "kayboldum" olmayan koşuda adımlar v3 ile birebir aynıdır
(kanıt: her koşuda `en` / `kararsiz` dizisi deneyin `ham_v3` kaydıyla karşılaştırılır). "kayboldum" olan koşu ayrıca
algısız (v3) yeniden beslenir.

Alt küme (küçültülmüş): B tohum 1 (6 koridor x 3 başlangıç = 18), C (insanlı, 18), D (bilinen başlangıç, 18) = 54
kayıt; B'nin tohum 2-5'i (72 kayıt) koşulmadı.

    py -3 gerileme.py [--isci 3]          # -> sonuc/gerileme.json, sonuc/gerileme.csv
"""

import argparse
import csv
import json
import math
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
KK = os.path.join(os.path.dirname(BURASI), "koridor_karisiklik")


def _yukle():
    if KK not in sys.path:
        sys.path.insert(1, KK)
    sys.path.insert(1, BURASI)
    import kos as K          # koridor_karisiklik/kos.py
    return K


def gorevler():
    K = _yukle()
    return [g for g in K.gorevler(["B", "C", "D"]) if g["bolum"] != "B" or g["tohum"] == 1]


def _bir(g, algi_acik=True):
    import numpy as np  # noqa: F401
    K = _yukle()
    O = K.O
    import algi as AL
    from gezinme.beyinler import bilesik, govdeden_noktaya, noktadan_govdeye
    from konumlama import CokHaritaliMCL
    from konumlama.benzet import goreli
    kor = g["kor"]
    ki, si = O.KORIDORLAR.index(kor), K.BASLANGICLAR.index(g["baslangic"])
    lidar_tohum = 1000 * g["tohum"] + 10 * ki + si
    mcl_tohum = 500000 + lidar_tohum
    akis, ek = K.akis_oku(g)
    akis = [(O.maskele(t), o, gg, y) for t, o, gg, y in akis]
    harita_ad = {h.ad: h for h in O.haritalar()}
    mcl = CokHaritaliMCL(O.haritalar(), ozellik=O.ozellik(True), tohum=mcl_tohum)
    bilinen = akis[0][2] if g.get("bilinen") else None
    if bilinen is not None:
        mcl.baslat_poz(kor, *bilinen, diger_haritalar=True)
    algi = AL.TasinmaAlgisi()
    kurulu = bilinen is not None
    ardisik, aday = 0, None
    onceki_o, onceki_p = None, None
    adimlar, olaylar = [], []
    for i, (tar, o, gg, yol) in enumerate(akis):
        artim = goreli(onceki_o, o) if onceki_o is not None else (0.0, 0.0, 0.0)
        tah = mcl.guncelle(tar, artim=(artim if onceki_o is not None else None))
        onceki_o = o
        p = (tah.x, tah.y, tah.theta)
        p1 = tah.olasiliklar[tah.en_olasi]
        kararli = (not tah.kararsiz) and (not tah.konum_kararsiz) and p1 >= 0.9
        if algi_acik and not kurulu and tah.olcum_islendi:
            ardisik = ardisik + 1 if (kararli and tah.en_olasi == aday) else (1 if kararli else 0)
            aday = tah.en_olasi if kararli else None
            if ardisik >= 10:
                kurulu = True
                algi.sifirla()
                onceki_p = None
        if algi_acik and kurulu:
            sic = 0.0
            if onceki_p is not None:
                ong = noktadan_govdeye(bilesik(govdeden_noktaya(onceki_p), artim))
                sic = math.hypot(p[0] - ong[0], p[1] - ong[1])
            d = algi.guncelle(harita_ad[tah.en_olasi], p, tar, kararsiz=tah.konum_kararsiz, sicrama_m=sic)
            onceki_p = p
            if d == "kayip":
                olaylar.append(dict(i=i, t=round(tar["t"], 2), yol=round(yol, 2), harita=tah.en_olasi,
                                    hata=round(math.hypot(p[0] - gg[0], p[1] - gg[1]), 2), sicrama=round(sic, 2),
                                    uyum=algi.son))
                mcl.baslat()
                kurulu, ardisik, aday, onceki_p = False, 0, None, None
        adimlar.append((tah.en_olasi, bool(tah.kararsiz), bool(tah.konum_kararsiz),
                        round(math.hypot(p[0] - gg[0], p[1] - gg[1]), 3)))
    yk = sum(1 for a in adimlar if not a[1] and a[0] != kor)
    kk = sum(1 for a in adimlar if a[0] == kor and not a[1] and not a[2] and a[3] > 0.5)
    son = adimlar[-1]
    return dict(id=g["id"], bolum=g["bolum"], kor=kor, algi=algi_acik, adim=len(adimlar), kayboldum=len(olaylar),
                olaylar=olaylar, yanlis_koridor_kesin_adim=yk, konum_kesin_yanlis_adim=kk,
                son_dogru=bool(son[0] == kor and not son[1]), seri=[(a[0], a[1]) for a in adimlar])


def _ham_v3(g):
    yol = os.path.join(KK, "ham_v3", g["bolum"], g["id"] + ".json")
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        d = json.load(f)
    a = d["adimlar"]
    return list(zip(a["en"], a["kararsiz"]))


def isci(g):
    os.environ.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    t0 = time.time()
    r = _bir(g, True)
    v3 = _ham_v3(g)
    r["ham_v3_ayni"] = (None if v3 is None else
                        [tuple(x) for x in r["seri"]] == [(e, bool(k)) for e, k in v3])
    if r["kayboldum"]:
        b = _bir(g, False)
        r["v3"] = {k: b[k] for k in ("yanlis_koridor_kesin_adim", "konum_kesin_yanlis_adim", "son_dogru")}
        r["v3"]["ham_v3_ayni"] = (None if v3 is None else
                                  [tuple(x) for x in b["seri"]] == [(e, bool(k)) for e, k in v3])
    else:
        r["v3"] = {k: r[k] for k in ("yanlis_koridor_kesin_adim", "konum_kesin_yanlis_adim", "son_dogru")}
        r["v3"]["ham_v3_ayni"] = r["ham_v3_ayni"]
    r.pop("seri")
    r["duvar_s"] = round(time.time() - t0, 1)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--isci", type=int, default=3)
    a = ap.parse_args()
    sys.path.insert(0, BURASI)
    import kacirma as KC
    KC.dusuk_oncelik()
    G = gorevler()
    KC.durum_yaz("gerileme basladi: %d kayit" % len(G))
    import multiprocessing as mp
    out = []
    with mp.Pool(a.isci, initializer=KC.dusuk_oncelik) as p:
        for r in p.imap_unordered(isci, G):
            out.append(r)
            KC.durum_yaz("gerileme %d/%d %s kayboldum=%d yk=%d/%d son=%s ayni=%s" % (
                len(out), len(G), r["id"], r["kayboldum"], r["yanlis_koridor_kesin_adim"],
                r["v3"]["yanlis_koridor_kesin_adim"], r["son_dogru"], r["ham_v3_ayni"]))
    out.sort(key=lambda r: r["id"])
    oz = {}
    for b in ("B", "C", "D", "hepsi"):
        R = [r for r in out if b == "hepsi" or r["bolum"] == b]
        oz[b] = dict(kayit=len(R), kayboldum_kosu=sum(1 for r in R if r["kayboldum"]),
                     kayboldum_toplam=sum(r["kayboldum"] for r in R),
                     yanlis_koridor_kesin_kosu_algi=sum(1 for r in R if r["yanlis_koridor_kesin_adim"]),
                     yanlis_koridor_kesin_kosu_v3=sum(1 for r in R if r["v3"]["yanlis_koridor_kesin_adim"]),
                     yanlis_koridor_kesin_adim_algi=sum(r["yanlis_koridor_kesin_adim"] for r in R),
                     yanlis_koridor_kesin_adim_v3=sum(r["v3"]["yanlis_koridor_kesin_adim"] for r in R),
                     konum_kesin_yanlis_adim_algi=sum(r["konum_kesin_yanlis_adim"] for r in R),
                     konum_kesin_yanlis_adim_v3=sum(r["v3"]["konum_kesin_yanlis_adim"] for r in R),
                     son_dogru_algi=sum(1 for r in R if r["son_dogru"]),
                     son_dogru_v3=sum(1 for r in R if r["v3"]["son_dogru"]),
                     ham_v3_ile_ayni=sum(1 for r in R if r["v3"]["ham_v3_ayni"]))
    with open(os.path.join(KC.SONUC, "gerileme.json"), "w", encoding="utf-8") as f:
        json.dump(dict(ozet=oz, kosular=out), f, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(KC.SONUC, "gerileme.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "bolum", "koridor", "kayboldum", "yanlis_koridor_kesin_adim_algi",
                    "yanlis_koridor_kesin_adim_v3", "konum_kesin_yanlis_adim_algi", "konum_kesin_yanlis_adim_v3",
                    "son_dogru_algi", "son_dogru_v3", "ham_v3_ile_ayni"])
        for r in out:
            w.writerow([r["id"], r["bolum"], r["kor"], r["kayboldum"], r["yanlis_koridor_kesin_adim"],
                        r["v3"]["yanlis_koridor_kesin_adim"], r["konum_kesin_yanlis_adim"],
                        r["v3"]["konum_kesin_yanlis_adim"], r["son_dogru"], r["v3"]["son_dogru"],
                        r["v3"]["ham_v3_ayni"]])
    print(json.dumps(oz, indent=1))
    KC.durum_yaz("gerileme bitti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
