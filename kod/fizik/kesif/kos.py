"""Deney matrisi: strateji x labirent x tohum (x odometri hatası) -> sonuc/<ad>.csv (+ hata görselleri sonuc/ham/).

    py -3 -m kesif.kos ilk            # ilk tur: 3 strateji x 11 labirent x 5 tohum, %14 dönüş hatası
    py -3 -m kesif.kos odometri       # kesif x labirentler x 5 tohum x dönüş hatası {0, 0,14, 0,25}
    py -3 -m kesif.kos hafiza         # hafızalı ikinci koşu (aynı labirent, ilk koşunun haritası)
    py -3 -m kesif.kos rapor          # sonuc/*.csv -> sonuc/SONUC.md

`kod/fizik` dizininden çalıştırılır. İşlemci kuralı: en çok 2 süreç (`--is`), her biri tek iş parçacıklı ve düşük
öncelikli (`_yol.dusuk_oncelik`). Hiçbir koşu sonucu ayarla gizlenmez: başarısızlıklar sebebiyle CSV'de kalır.
"""

import argparse
import csv
import math
import os
import sys
import time

from . import _yol
from ._yol import KESIF, durum_yaz, dusuk_oncelik

SONUC = os.path.join(KESIF, "sonuc")
HAM = os.path.join(SONUC, "ham")

LABIRENTLER = ["labirent_5x5_t1", "labirent_7x7_t1", "labirent_9x9_t1", "labirent_9x9_t2", "labirent_9x9_t3",
               "labirent_13x13_t1", "labirent_13x13_t2", "labirent_13x13_t3",
               "labirent_17x17_t1", "labirent_17x17_t2", "labirent_17x17_t3"]
STRATEJILER = ["kesif", "sag_duvar", "rastgele"]
TOHUMLAR = [0, 1, 2, 3, 4]

ALANLAR = ["deney", "strateji", "sahne", "tohum", "donus_hata", "durum", "sure_s", "yol_m", "carpma_sayisi",
           "carpma_suresi_s", "puan", "p_en", "kesfedilen_hucre", "toplam_hucre", "sikisma_sebebi",
           "poz_hata_maks_m", "poz_hata_son_m", "yon_hata_maks_der", "duvar_hata_ort_m", "dogru_duvar_orani",
           "tarama_ms_ort", "tarama_ms_p95", "tarama_ms_maks", "plan_ms_ort", "plan_ms_maks", "gercek_sure_s",
           "k_don", "kurtarma", "kara_liste", "son_mod", "olaylar", "hafiza_sure_s", "hafiza_durum", "hafiza_puan",
           "ayar"]


def beyin_kur(strateji, sahne, tohum, ayar=None, hafiza=None):
    if strateji == "kesif":
        from .beyin import KesifBeyni
        from .sahne import beyin_start_cizgisi
        return KesifBeyni(ayar=ayar, start_cizgisi=beyin_start_cizgisi(sahne), hafiza=hafiza)
    if strateji == "sag_duvar":
        from .taban import SagDuvarBeyni
        return SagDuvarBeyni()
    if strateji == "rastgele":
        from .taban import RastgeleBeyni
        return RastgeleBeyni(tohum=tohum)
    raise ValueError(strateji)


def sahne_al(ad):
    """Ad ya da ("uret", satir, sutun, tohum, algoritma) -> Sahne (eğitim labirentleri bellekte üretilir)."""
    from .sahne import sahne_yukle
    if isinstance(ad, (tuple, list)) and ad and ad[0] == "uret":
        from labirent.uretici import sahne_kur
        _, R, C, t, alg = ad
        isim = "egitim_%dx%d_%s_%d" % (R, C, alg.replace(":", ""), t)
        harita, s3, _ = sahne_kur(isim, R, C, t, algoritma=alg)
        return sahne_yukle((harita, s3))
    return sahne_yukle(ad)


def tek_kos(g):
    """g: {"deney", "strateji", "sahne", "tohum", "donus_hata", "sure", "hafiza": bool, "ayar": BeyinAyari | None,
    "png": bool} -> satır sözlüğü."""
    import numpy as np
    from .benzet2b import Benzetici, BenzetimAyari, harita_dogrulugu
    sahne = sahne_al(g["sahne"])
    b = beyin_kur(g["strateji"], sahne, g["tohum"], g.get("ayar"))
    A = BenzetimAyari(sure_siniri_s=g.get("sure", 900.0), tohum=g["tohum"], donus_hata=g.get("donus_hata", 0.14))
    bz = Benzetici(sahne, b, A)
    r = bz.kos()
    satir = {k: r.get(k) for k in ALANLAR if k in r}
    if isinstance(satir.get("olaylar"), list):     # hakem olayları: türlerin özeti
        from collections import Counter
        satir["olaylar"] = " ".join("%s:%d" % kv for kv in Counter(o.get("tur") for o in satir["olaylar"]).items())
    satir.update({"deney": g["deney"], "strateji": g["strateji"], "sahne": sahne.ad, "tohum": g["tohum"],
                  "donus_hata": A.donus_hata, "ayar": g.get("ayar_ad", "")})
    d = b.durum()
    if g["strateji"] == "kesif":
        satir.update(harita_dogrulugu(sahne, d))
        pm = b.zaman["plan_ms"] or [0.0]
        satir.update({"plan_ms_ort": round(float(np.mean(pm)), 2), "plan_ms_maks": round(float(np.max(pm)), 1),
                      "k_don": round(b.slam.k_don, 3), "kurtarma": b.sayac["kurtarma"],
                      "kara_liste": b.sayac["kara_liste"],
                      "olaylar": "; ".join("%s:%s" % (o[0], o[1] if len(o) < 3 or not isinstance(o[2], str)
                                                    else o[1] + "/" + o[2]) for o in b.olaylar[-8:])})
    satir["son_mod"] = d.get("mod")
    satir.pop("duvar_hucre", None)
    if g.get("hafiza") and g["strateji"] == "kesif" and r["durum"] == "basari":
        hz = b.hafiza_ver()
        b2 = beyin_kur("kesif", sahne, g["tohum"], g.get("ayar"), hafiza=hz)
        A2 = BenzetimAyari(sure_siniri_s=g.get("sure", 900.0), tohum=g["tohum"] + 1000, donus_hata=A.donus_hata)
        r2 = Benzetici(sahne, b2, A2).kos()
        satir.update({"hafiza_sure_s": r2["sure_s"], "hafiza_durum": r2["durum"], "hafiza_puan": r2["puan"]})
    if g.get("png") or r["durum"] != "basari":
        try:
            from .ciz import ciz
            os.makedirs(HAM, exist_ok=True)
            yol = os.path.join(HAM, "%s_%s_%s_t%d_o%02d.png" % (g["deney"], g["strateji"], sahne.ad, g["tohum"],
                                                               int(round(A.donus_hata * 100))))
            gp = getattr(bz, "son_poz_dingil", None)
            if gp is not None:
                from .robot import VARSAYILAN as R
                gp = (gp[0] - R.dingil_x_m * math.cos(gp[2]), gp[1] - R.dingil_x_m * math.sin(gp[2]), gp[2])
            ciz(sahne, b, yol, gercek_poz=gp, baslik="%s %s t%d %s %.0fs" % (g["strateji"], sahne.ad, g["tohum"],
                                                                         r["durum"], r["sure_s"]))
        except Exception as e:   # görsel yan ürün; koşuyu düşürmesin
            satir["olaylar"] = (satir.get("olaylar") or "") + " [ciz hata: %s]" % e
    return satir


def _baslat():
    dusuk_oncelik()


def _guvenli(g):
    try:
        return tek_kos(g)
    except Exception as e:  # beyin çökmesi de bir sonuçtur
        import traceback
        return {"deney": g["deney"], "strateji": g["strateji"], "sahne": str(g["sahne"]), "tohum": g["tohum"],
                "donus_hata": g.get("donus_hata", 0.14), "durum": "hata",
                "olaylar": "%s: %s" % (type(e).__name__, traceback.format_exc()[-400:].replace("\n", " | "))}


def calistir(gorevler, csv_yolu, is_sayisi=2):
    import multiprocessing as mp
    os.makedirs(os.path.dirname(csv_yolu), exist_ok=True)
    yeni = not os.path.exists(csv_yolu)
    if not yeni:
        # yarıda kalan matrisi sürdür: başarıyla (hata olmadan) koşulmuş görevleri atla, hatalı satırları ayıkla
        with open(csv_yolu, encoding="utf-8") as f:
            eski = list(csv.DictReader(f))
        tamam = {(r["strateji"], r["sahne"], str(r["tohum"]), "%.2f" % float(r["donus_hata"] or 0), r.get("ayar") or "")
                 for r in eski if r.get("durum") not in (None, "", "hata")}
        if any(r.get("durum") in (None, "", "hata") for r in eski):
            with open(csv_yolu, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
                w.writeheader()
                for r in eski:
                    if r.get("durum") not in (None, "", "hata"):
                        w.writerow(r)
        gorevler = [g for g in gorevler if (g["strateji"], g["sahne"] if isinstance(g["sahne"], str) else None,
                                            str(g["tohum"]), "%.2f" % g.get("donus_hata", 0.14), g.get("ayar_ad", ""))
                    not in tamam]
    t0 = time.time()
    n = len(gorevler)
    satirlar = []
    with open(csv_yolu, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
        if yeni:
            w.writeheader()
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=max(1, min(4, is_sayisi)), initializer=_baslat, maxtasksperchild=4) as havuz:
            for k, s in enumerate(havuz.imap_unordered(_guvenli, gorevler)):
                w.writerow(s)
                f.flush()
                satirlar.append(s)
                print("[%d/%d %.0fs] %s %s t%s o%s -> %s %s" % (k + 1, n, time.time() - t0, s.get("strateji"),
                                                              s.get("sahne"), s.get("tohum"), s.get("donus_hata"),
                                                              s.get("durum"), s.get("sure_s")), flush=True)
    return satirlar


def gorev_listesi(deney):
    G = []
    if deney == "ilk":
        for st in STRATEJILER:
            for lab in LABIRENTLER:
                for t in TOHUMLAR:
                    G.append({"deney": "ilk", "strateji": st, "sahne": lab, "tohum": t, "donus_hata": 0.14,
                              "png": st == "kesif" and t == 0})
    elif deney == "odometri":
        for oh in (0.0, 0.25):            # 0,14 ilk turdan
            for lab in LABIRENTLER:
                for t in TOHUMLAR:
                    G.append({"deney": "odometri", "strateji": "kesif", "sahne": lab, "tohum": t, "donus_hata": oh})
    elif deney == "hafiza":
        for lab in LABIRENTLER:
            for t in TOHUMLAR[:3]:
                G.append({"deney": "hafiza", "strateji": "kesif", "sahne": lab, "tohum": t, "donus_hata": 0.14,
                          "hafiza": True})
    elif deney == "v2_2b":
        # v2 (beyin.surum_ayari) geliştirme kümesinde; v1 karşılığı ilk.csv (aynı tohumlar)
        from .beyin import surum_ayari
        for lab in LABIRENTLER:
            for t in TOHUMLAR:
                G.append({"deney": "v2_2b", "strateji": "kesif", "sahne": lab, "tohum": t, "donus_hata": 0.14,
                          "ayar": surum_ayari("v2"), "ayar_ad": "v2", "hafiza": True})
    elif deney == "v3_2b":
        # v2 / v3 2B: 21 geliştirme labirenti (eski 11 + görülmüş 13x13_t4..t8, 17x17_t4..t8) x tohum {0, 1}
        from .beyin import surum_ayari
        labs = LABIRENTLER + ["labirent_%dx%d_t%d" % (n, n, t) for n in (13, 17) for t in range(4, 9)]
        for sur in ("v2", "v3"):
            for lab in labs:
                for t in (0, 1):
                    G.append({"deney": "v3_2b", "strateji": "kesif", "sahne": lab, "tohum": t, "donus_hata": 0.14,
                              "ayar": surum_ayari(sur), "ayar_ad": sur})
    elif deney == "kose_2b":
        # v2 kısa 2B denemesi: 4 geliştirme labirenti x tohum {0, 1} (sonuç sonuc/v2_2b.csv'ye taşındı; v2k = akıcı
        # köşe ilk denemede 8 koşuda 9 çarpma verdi, sonuc/ham/kose_2b_v2_ilk_v2k.csv)
        from .beyin import surum_ayari
        for sur in ("v2",):
            for lab in ("labirent_9x9_t1", "labirent_13x13_t1", "labirent_13x13_t3", "labirent_17x17_t1"):
                for t in (0, 1):
                    G.append({"deney": "kose_2b", "strateji": "kesif", "sahne": lab, "tohum": t, "donus_hata": 0.14,
                              "ayar": surum_ayari(sur), "ayar_ad": sur})
    else:
        raise ValueError(deney)
    # uzun koşular önce (havuz dengesi)
    G.sort(key=lambda g: -int(str(g["sahne"]).split("_")[1].split("x")[0]) if "x" in str(g["sahne"]) else 0)
    return G


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("deney", choices=["ilk", "odometri", "hafiza", "v2_2b", "kose_2b", "v3_2b", "rapor"])
    p.add_argument("--is", dest="is_sayisi", type=int, default=2)
    p.add_argument("--sahne", default=None, help="virgüllü süzgeç (alt dize)")
    p.add_argument("--strateji", default=None)
    a = p.parse_args(argv)
    if a.deney == "rapor":
        from .rapor import rapor_yaz
        print(rapor_yaz())
        return
    dusuk_oncelik()
    G = gorev_listesi(a.deney)
    if a.sahne:
        sz = a.sahne.split(",")
        G = [g for g in G if any(s in str(g["sahne"]) for s in sz)]
    if a.strateji:
        G = [g for g in G if g["strateji"] in a.strateji.split(",")]
    durum_yaz("kos %s basladi: %d gorev" % (a.deney, len(G)))
    calistir(G, os.path.join(SONUC, a.deney + ".csv"), a.is_sayisi)
    durum_yaz("kos %s bitti" % a.deney)


if __name__ == "__main__":
    main()
