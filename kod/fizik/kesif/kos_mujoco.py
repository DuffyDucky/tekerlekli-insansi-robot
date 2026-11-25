"""MuJoCo düzeneğinde (gezinme.duzenek) keşif beyni: labirent ailesi x tohum -> sonuc/mujoco.csv + kayıtlar.

    py -3 -m kesif.kos_mujoco --is 4                 # 11 labirent x tohum {0, 1, 2}
    py -3 -m kesif.kos_mujoco --sahne 5x5 --tohum 0  # tek koşu

Beyin labirentte ön bilgisiz kurulur (`KesifBeyni()`: START çizgisi kurala göre 0,45 m geride; sahneden hiçbir şey
okunmaz). Hakem: `labirent.hakem.Hakem(sahne)`. Kayıt (`gezinme.duzenek.Kayit`, .npz, taramalarla) sonuc/ham/mujoco/
altına; tekrar oynatmalı rapor bunları okur. Aynı labirent + tohum 2B benzeticide de koşulup (`kos.tek_kos`)
karşılaştırma sonuc/mujoco_2b.csv'ye yazılır (`--karsilastir`).
"""

import argparse
import csv
import math
import os
import time

from ._yol import durum_yaz, dusuk_oncelik
from .kos import ALANLAR, HAM, LABIRENTLER, SONUC

KAYIT_DIZIN = os.path.join(HAM, "mujoco")
M_ALANLAR = ["sahne", "tohum", "durum", "sure_s", "yol_m", "carpma_sayisi", "carpma_suresi_s", "puan", "p_en",
             "kesfedilen_hucre", "sikisma_sebebi", "poz_hata_maks_m", "poz_hata_son_m", "yon_hata_maks_der",
             "duvar_hata_ort_m", "dogru_duvar_orani", "tarama_ms_ort", "tarama_ms_p95", "tarama_ms_maks", "duvar_s",
             "rtf", "k_don", "kurtarma", "son_mod", "olaylar", "kayit"]


def tek_mujoco(g):
    dusuk_oncelik()
    import numpy as np
    from gezinme.duzenek import Duzenek, Kayit
    from labirent.hakem import Hakem
    from .beyin import KesifBeyni
    from .benzet2b import harita_dogrulugu
    from .sahne import dunyadan_beyne, sahne_yukle
    ad, tohum = g["sahne"], g["tohum"]
    s2 = sahne_yukle(ad)
    b = KesifBeyni()
    dz = Duzenek(ad, tohum=tohum)
    os.makedirs(KAYIT_DIZIN, exist_ok=True)
    kyol = os.path.join(KAYIT_DIZIN, "%s_t%d.npz" % (ad, tohum))
    kayit = Kayit(kyol, taramalar=True)
    # tarama işleme süresi
    orj = b.slam.tarama_isle
    ms = []

    def olcen(tarama, t):
        t0 = time.perf_counter()
        r = orj(tarama, t)
        ms.append((time.perf_counter() - t0) * 1000.0)
        return r
    b.slam.tarama_isle = olcen
    h = Hakem(ad, sure_siniri_s=g.get("sure", 900.0))
    r = dz.kos(b, g.get("sure", 900.0), hakem=h, kayit=kayit)
    hs = dict(r.get("hakem") or {})
    satir = {k: hs.get(k) for k in M_ALANLAR if k in hs}
    satir.update({"sahne": ad, "tohum": tohum, "duvar_s": r.get("duvar_s"), "rtf": r.get("rtf"), "kayit": kyol,
                  "son_mod": r.get("son_mod")})
    if not satir.get("durum") and float(r.get("sure_s") or 0) >= g.get("sure", 900.0) - 0.2:
        satir["durum"] = "fail_sure"     # düzenek döngüsü süre sınırında hakemden önce biter
    # poz hatası (beyin çerçevesinde): kayıt satırları gerçek (dünya, gövde) ve tahmin (beyin) içerir
    S = np.array(kayit.satir, dtype=float).reshape(-1, 18)
    if S.shape[0]:
        gx, gy = dunyadan_beyne(s2, S[:, 1], S[:, 2])
        gth = S[:, 3] - s2.start_poz[2]
        e = np.hypot(gx - S[:, 7], gy - S[:, 8])
        eth = np.abs((gth - S[:, 9] + np.pi) % (2 * np.pi) - np.pi)
        ok = np.isfinite(e)
        if ok.any():
            satir.update({"poz_hata_maks_m": round(float(np.nanmax(e)), 3), "poz_hata_son_m": round(float(e[ok][-1]), 3),
                          "yon_hata_maks_der": round(float(np.degrees(np.nanmax(eth))), 2)})
    satir.update(harita_dogrulugu(s2, b.durum()))
    satir.pop("duvar_hucre", None)
    satir.pop("duvar_hata_p95_m", None)
    if ms:
        m = np.array(ms)
        satir.update({"tarama_ms_ort": round(float(m.mean()), 2), "tarama_ms_p95": round(float(np.percentile(m, 95)), 2),
                      "tarama_ms_maks": round(float(m.max()), 1)})
    satir.update({"k_don": round(b.slam.k_don, 3), "kurtarma": b.sayac["kurtarma"],
                  "olaylar": "; ".join("%s:%s" % (o[0], o[1]) for o in b.olaylar[-8:])})
    try:
        from .ciz import ciz
        x, y, th = dz.gercek_poz()
        ciz(s2, b, os.path.join(KAYIT_DIZIN, "%s_t%d.png" % (ad, tohum)), gercek_poz=(x, y, th),
            baslik="MuJoCo %s t%d %s %.0fs" % (ad, tohum, satir.get("durum"), float(satir.get("sure_s") or 0)))
    except Exception:
        pass
    return satir


def _guvenli(g):
    try:
        return tek_mujoco(g)
    except Exception as e:
        import traceback
        return {"sahne": g["sahne"], "tohum": g["tohum"], "durum": "hata",
                "olaylar": "%s: %s" % (type(e).__name__, traceback.format_exc()[-500:].replace("\n", " | "))}


def main(argv=None):
    import multiprocessing as mp
    p = argparse.ArgumentParser()
    p.add_argument("--is", dest="is_sayisi", type=int, default=4)
    p.add_argument("--sahne", default=None)
    p.add_argument("--tohum", default="0,1,2")
    p.add_argument("--sure", type=float, default=900.0)
    a = p.parse_args(argv)
    dusuk_oncelik()
    labs = [l for l in LABIRENTLER if not a.sahne or any(s in l for s in a.sahne.split(","))]
    G = [{"sahne": l, "tohum": int(t), "sure": a.sure} for l in labs for t in a.tohum.split(",")]
    G.sort(key=lambda g: -int(g["sahne"].split("_")[1].split("x")[0]))
    yol = os.path.join(SONUC, "mujoco.csv")
    yeni = not os.path.exists(yol)
    durum_yaz("mujoco basladi: %d kosu, %d surec" % (len(G), a.is_sayisi))
    t0 = time.time()
    with open(yol, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=M_ALANLAR, extrasaction="ignore")
        if yeni:
            w.writeheader()
        with mp.get_context("spawn").Pool(max(1, min(5, a.is_sayisi)), maxtasksperchild=1) as hv:
            for k, s in enumerate(hv.imap_unordered(_guvenli, G)):
                w.writerow(s)
                f.flush()
                print("[%d/%d %.0fs] %s t%s -> %s %s (rtf %s)" % (k + 1, len(G), time.time() - t0, s.get("sahne"),
                                                                 s.get("tohum"), s.get("durum"), s.get("sure_s"),
                                                                 s.get("rtf")), flush=True)
    durum_yaz("mujoco bitti")


if __name__ == "__main__":
    main()
