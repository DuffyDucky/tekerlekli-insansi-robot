"""Ham koşu kayıtlarından CSV ve tablolar; görünürlük ısı haritası (PNG).

    %V% kod\\fizik\\sanalray\\rapor.py            # sonuc/ab_*.csv, sonuc/kayip_*.csv, sonuc/tablolar.md
    py -3 kod\\fizik\\sanalray\\rapor.py --ciz    # gorsel/gorunurluk.png (matplotlib)"""

import csv
import glob
import json
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sanalray import _yol  # noqa: E402

AB_ALAN = ["id", "kume", "koridor", "hedef", "tohum", "aralik", "donus_fazlasi", "kafa", "mercek", "cozunurluk", "boy_m",
           "yukseklik", "etiket_sayisi", "basari", "neden", "sure_s", "yol_m", "rota_m", "varis_hatasi_m",
           "en_yanal_sapma_m", "temas_olay", "konum_hata_en_m", "konum_hata_ort_m", "konum_std_en_m", "etiket_olcum",
           "etiket_ret", "pan_komut", "kare", "kare_ms_ort", "bitis", "rtf", "duvar_s"]
KAYIP_ALAN = ["id", "kume", "koridor", "birak", "kafa", "aralik", "donus_fazlasi", "mercek", "cozunurluk", "boy_m",
              "basari", "neden", "sure_s", "yol_m", "ilk_etiket_s", "lokalize_s", "lokalize_yol_m", "karar_koridor",
              "varis_hatasi_m", "en_yanal_sapma_m", "temas_olay", "konum_hata_en_m", "etiket_olcum", "etiket_ret",
              "bas_x", "bas_y", "bas_yon_derece", "bitis", "rtf", "duvar_s"]


def ham():
    out = []
    for y in sorted(glob.glob(os.path.join(_yol.HAM, "kosu", "*.json"))):
        with open(y, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def _csv(yol, satir, alan):
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alan, extrasaction="ignore")
        w.writeheader()
        for s in satir:
            w.writerow(s)


def csv_uret():
    H = ham()
    ab = [s for s in H if s["id"].startswith("ab_")]
    ky = [s for s in H if s["id"].startswith("kayip_")]
    for kume in ("gelistirme", "sinama"):
        _csv(os.path.join(_yol.SONUC, "ab_%s.csv" % kume), [s for s in ab if s.get("kume") == kume], AB_ALAN)
        _csv(os.path.join(_yol.SONUC, "kayip_%s.csv" % kume), [s for s in ky if s.get("kume") == kume], KAYIP_ALAN)
    return ab, ky


def _ort(a):
    a = [x for x in a if x is not None]
    return sum(a) / len(a) if a else float("nan")


def _en(a):
    a = [x for x in a if x is not None]
    return max(a) if a else float("nan")


def _f(x, n=2):
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else ("%.*f" % (n, x)).replace(".", ",")


def ab_tablo(satir, anahtar):
    g = defaultdict(list)
    for s in satir:
        g[anahtar(s)].append(s)
    out = ["| koşul | başarı | varış hatası ort / en (m) | raydan en büyük yanal sapma ort / en (m) | konum hatası en (m) | "
           "duvar teması | etiket / koridor |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for k in sorted(g, key=str):
        r = g[k]
        b = sum(1 for s in r if s.get("basari"))
        out.append("| %s | %d/%d | %s / %s | %s / %s | %s | %d | %s |" % (
            k, b, len(r), _f(_ort([s.get("varis_hatasi_m") for s in r]), 3), _f(_en([s.get("varis_hatasi_m") for s in r]), 3),
            _f(_ort([s.get("en_yanal_sapma_m") for s in r]), 3), _f(_en([s.get("en_yanal_sapma_m") for s in r]), 3),
            _f(_en([s.get("konum_hata_en_m") for s in r]), 3), sum(s.get("temas_olay") or 0 for s in r),
            _f(_ort([s.get("etiket_sayisi") for s in r]), 1)))
    return "\n".join(out)


def kayip_tablo(satir):
    g = defaultdict(list)
    for s in satir:
        g[(s["kume"], s["kafa"])].append(s)
    # ilk_etiket_s: herhangi bir etiketin ilk kabul edilen algılaması; lokalize_s: süzgecin baslat_en_cok_menzil
    # (3,5 m) içindeki bir etiketten başlatıldığı an. İkisi ayrı sütun; karıştırılmasın.
    out = ["| küme, kafa | başarı | ilk etiket görülme ort / en (s) | konumlanma süresi ort / en (s) | "
           "konumlanana dek yol ort / en (m) | toplam süre ort (s) | varış hatası ort (m) | yanlış koridor | duvar teması |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in sorted(g):
        r = g[k]
        out.append("| %s, %s | %d/%d | %s / %s | %s / %s | %s / %s | %s | %s | %d | %d |" % (
            k[0], k[1], sum(1 for s in r if s.get("basari")), len(r),
            _f(_ort([s.get("ilk_etiket_s") for s in r]), 1), _f(_en([s.get("ilk_etiket_s") for s in r]), 1),
            _f(_ort([s.get("lokalize_s") for s in r]), 1),
            _f(_en([s.get("lokalize_s") for s in r]), 1), _f(_ort([s.get("lokalize_yol_m") for s in r]), 2),
            _f(_en([s.get("lokalize_yol_m") for s in r]), 2), _f(_ort([s.get("sure_s") for s in r]), 1),
            _f(_ort([s.get("varis_hatasi_m") for s in r]), 3),
            sum(1 for s in r if s.get("karar_koridor") and s.get("karar_koridor") != s["koridor"]),
            sum(s.get("temas_olay") or 0 for s in r)))
    return "\n".join(out)


def lidar_tablo(korlar):
    """LiDAR'lı gezinme deneyi (gezinme/sonuc/*.csv) aynı koridorlarda."""
    out = []
    for ad in ("senaryo_ab", "senaryo_kayip"):
        y = os.path.join(_yol.FIZIK, "gezinme", "sonuc", ad + ".csv")
        if not os.path.exists(y):
            continue
        with open(y, encoding="utf-8") as f:
            R = list(csv.DictReader(f))
        for etiket, alt in (("hepsi", R), ("sınama koridorları", [r for r in R if r["koridor"] in korlar])):
            b = sum(1 for r in alt if r["basari"] in ("True", "1", "true"))
            out.append(dict(deney=ad, kapsam=etiket, n=len(alt), basari=b,
                            varis=_ort([float(r["varis_hatasi_m"]) for r in alt if r.get("varis_hatasi_m")]),
                            temas=sum(int(float(r.get("temas_olay") or 0)) for r in alt),
                            karar_yol=_ort([float(r["karar_yol_m"]) for r in alt if r.get("karar_yol_m")]) if ad == "senaryo_kayip" else None,
                            karar_t=_ort([float(r["karar_t_s"]) for r in alt if r.get("karar_t_s")]) if ad == "senaryo_kayip" else None))
    return out


def gorunurluk_tablo():
    y = os.path.join(_yol.SONUC, "gorunurluk.csv")
    with open(y, encoding="utf-8") as f:
        R = list(csv.DictReader(f))
    # en uzak güvenilir algılama (oran >= 0,75 ve o mesafeye kadar her mesafede >= 0,75): mercek x çözünürlük x boy, açı 0 / 50 / 65
    idx = defaultdict(dict)
    for r in R:
        idx[(r["mercek"], r["cozunurluk"], r["boy_cm"], r["yukseklik"], r["aci_derece"], r["bozulma"])][float(r["mesafe_m"])] = float(r["algilama_orani"])

    def menzil(k):
        d = idx.get(k, {})
        en = 0.0
        for m in sorted(d):
            if d[m] >= 0.75:
                en = m
            else:
                break
        return en
    out = ["| mercek | çözünürlük | boy (cm) | 0° | 30° | 50° | 65° | 75° |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for mer in ("std", "genis"):
        for coz in ("768x432", "1152x648", "1536x864"):
            for boy in ("10", "15", "20"):
                out.append("| %s | %s | %s | %s |" % (mer, coz, boy, " | ".join(_f(menzil((mer, coz, boy, "goz", a, "temiz")), 2)
                                                                           for a in ("0", "30", "50", "65", "75"))))
    out2 = ["| bozulma (std, 1152 x 648, 15 cm, göz hizası) | 0° | 30° | 50° | 65° |", "| --- | --- | --- | --- | --- |"]
    for b in ("temiz", "gurultu", "los", "parlama", "kapanma25", "kapanma50", "donus_0.4", "donus_0.89"):
        out2.append("| %s | %s |" % (b, " | ".join(_f(menzil(("std", "1152x648", "15", "goz", a, b)), 2) for a in ("0", "30", "50", "65"))))
    out3 = ["| yükseklik (std, 1152, 15 cm, temiz) | 0° | 30° | 50° | 65° |", "| --- | --- | --- | --- | --- |"]
    for yk in ("goz", "kapi_ustu"):
        d0 = []
        for a in ("0", "30", "50", "65"):
            d = idx.get(("std", "1152x648", "15", yk, a, "temiz"), {})
            ok = [m for m in sorted(d) if d[m] >= 0.75]
            d0.append("%s-%s" % (_f(min(ok), 2), _f(max(ok), 2)) if ok else "-")
        out3.append("| %s | %s |" % (yk, " | ".join(d0)))
    # hata (temiz, std 1152 15 cm, göz): mesafeye göre ortanca
    hata = defaultdict(lambda: defaultdict(list))
    for r in R:
        if (r["mercek"], r["cozunurluk"], r["boy_cm"], r["yukseklik"], r["bozulma"]) == ("std", "1152x648", "15", "goz", "temiz") and r["menzil_hata_med_m"]:
            hata[float(r["mesafe_m"])]["m"].append(float(r["menzil_hata_med_m"]))
            hata[float(r["mesafe_m"])]["k"].append(float(r["kerteriz_hata_med_derece"]))
            hata[float(r["mesafe_m"])]["p"].append(float(r["psi_hata_med_derece"]))
            if r["tek_etiket_konum_hata_med_m"]:
                hata[float(r["mesafe_m"])]["t"].append(float(r["tek_etiket_konum_hata_med_m"]))
    out4 = ["| mesafe (m) | menzil hatası (m) | kerteriz hatası (°) | psi hatası (°) | tek etiketten konum hatası (m) |",
            "| --- | --- | --- | --- | --- |"]
    for m in sorted(hata):
        h = hata[m]
        med = lambda a: sorted(a)[len(a) // 2] if a else None
        out4.append("| %s | %s | %s | %s | %s |" % (_f(m, 2), _f(med(h["m"]), 3), _f(med(h["k"]), 3), _f(med(h["p"]), 1), _f(med(h["t"]), 3)))
    return "\n".join(out), "\n".join(out2), "\n".join(out3), "\n".join(out4)


def tablolar():
    ab, ky = csv_uret()
    s = []
    try:
        a, b, c, d = gorunurluk_tablo()
        s += ["## Görünürlük: en uzak güvenilir algılama (m; oran ≥ 0,75 kesintisiz), göz hizası, temiz", a, "",
              "## Bozulmalar", b, "", "## Yükseklik (algılanan mesafe aralığı)", c, "", "## Poz hatası (koşulların ortancası)", d, ""]
    except OSError:
        pass
    gel = [x for x in ab if x.get("kume") == "gelistirme"]
    sin = [x for x in ab if x.get("kume") == "sinama"]
    s += ["## A'dan B'ye, geliştirme (koridor_1, koridor_3)",
          ab_tablo(gel, lambda x: "aralık %s, dönüş fazlası %%%d" % (x["aralik"], round(x["donus_fazlasi"] * 100))), "",
          "## A'dan B'ye, sınama (koridor_2, 4, 5, 6)",
          ab_tablo(sin, lambda x: "aralık %s, %%%d, kafa %s" % (x["aralik"], round(x["donus_fazlasi"] * 100), x["kafa"])), "",
          "## Rastgele bırakılma", kayip_tablo(ky), ""]
    L = lidar_tablo(["koridor_2", "koridor_4", "koridor_5", "koridor_6"])
    s += ["## LiDAR'lı taban (gezinme/sonuc)", "| deney | kapsam | başarı | varış hatası ort (m) | temas | karar yolu ort (m) | karar süresi ort (s) |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in L:
        s.append("| %s | %s | %d/%d | %s | %d | %s | %s |" % (r["deney"], r["kapsam"], r["basari"], r["n"], _f(r["varis"], 3),
                                                            r["temas"], _f(r["karar_yol"], 2), _f(r["karar_t"], 1)))
    metin = "\n".join(s) + "\n"
    with open(os.path.join(_yol.SONUC, "tablolar.md"), "w", encoding="utf-8") as f:
        f.write(metin)
    try:
        print(metin)
    except UnicodeEncodeError:                      # cp1254 konsolu "≥" basamıyor; dosya zaten yazıldı
        print(metin.encode("ascii", "replace").decode("ascii"))
    return metin


def ciz():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    with open(os.path.join(_yol.SONUC, "gorunurluk.csv"), encoding="utf-8") as f:
        R = list(csv.DictReader(f))
    M = sorted({float(r["mesafe_m"]) for r in R})
    A = sorted({int(r["aci_derece"]) for r in R})
    fig, ax = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    for i, mer in enumerate(("std", "genis")):
        for j, boy in enumerate(("10", "15", "20")):
            Z = np.full((len(A), len(M)), np.nan)
            for r in R:
                if (r["mercek"], r["cozunurluk"], r["boy_cm"], r["yukseklik"], r["bozulma"]) == (mer, "1152x648", boy, "goz", "temiz"):
                    Z[A.index(int(r["aci_derece"])), M.index(float(r["mesafe_m"]))] = float(r["algilama_orani"])
            a = ax[i, j]
            im = a.imshow(Z, origin="lower", aspect="auto", cmap="viridis", vmin=0, vmax=1)
            a.set_xticks(range(len(M)), [("%g" % m) for m in M])
            a.set_yticks(range(len(A)), [str(x) for x in A])
            a.set_title("%s, %s cm, 1152x648" % ("Camera Module 3" if mer == "std" else "Camera Module 3 Wide", boy), fontsize=10)
            if i == 1:
                a.set_xlabel("mesafe (m)")
            if j == 0:
                a.set_ylabel("bakış açısı (°)")
    fig.colorbar(im, ax=ax, shrink=0.8, label="algılama oranı")
    fig.suptitle("AprilTag 36h11 algılama oranı (göz hizası, temiz görüntü; simülasyon: kusursuz baskı)")
    os.makedirs(_yol.GORSEL, exist_ok=True)
    fig.savefig(os.path.join(_yol.GORSEL, "gorunurluk.png"), dpi=90)
    print("gorsel/gorunurluk.png")


if __name__ == "__main__":
    if "--ciz" in sys.argv:
        ciz()
    else:
        tablolar()
