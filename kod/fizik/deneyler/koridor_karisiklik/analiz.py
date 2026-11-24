"""Koridor karışıklık deneyi: ham sonuçlardan tablolar (CSV), özet (ozet.json) ve görseller (gorsel/*.png).

    py -3 kod\\fizik\\deneyler\\koridor_karisiklik\\analiz.py      # matplotlib gerekir (sanal ortamda yok; sistem py -3)

Fizik / MuJoCo gerekmez; benzer çift için 2B ışın izleme konumlama modülünden (yalnız numpy).
"""

import glob
import json
import math
import os
import sys

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(os.path.dirname(BURASI))
KOD = os.path.dirname(FIZIK)
sys.path.insert(0, FIZIK)
HAM = os.path.join(BURASI, "ham")
GORSEL = os.path.join(BURASI, "gorsel")
SONUC = os.path.join(BURASI, "sonuc")
# v1: c34618b konumlayıcısı (ham/, sonuc/, gorsel/; yeniden koşulmaz, `--etiket v1` bugünkü modülle 60 ışını farklı seçer)
ETIKET = "v1"
ETIKET_AD = {"v1": "v1 (düzeltme öncesi)", "v2": "v2 (düzeltilmiş konumlayıcı)", "v2_360": "v2-360 (kör sektör yok)"}
K = ["koridor_%d" % i for i in range(1, 7)]
KS = {k: "K%d" % (i + 1) for i, k in enumerate(K)}
BICIM = {"koridor_1": "düz 2,0×30", "koridor_2": "düz 3,5×12", "koridor_3": "L 2,4", "koridor_4": "T 2,6",
         "koridor_5": "düz 2,4×24 (A)", "koridor_6": "düz 2,4×24 (B)"}
BAS_AD = {"bas": "başlangıç ucu", "son": "öbür uç (ters)", "orta": "ortadan"}
FARK_S = (15.7, 17.25)
X0 = 1.8                          # benzer çiftte orta hat başlangıcı (s = x - 1,8)

# renkler (dataviz varsayılan paleti, açık yüzey)
SERI = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DOGRU, KARARSIZ, YANLIS = "#1f8a4c", "#9a9890", "#c62f2f"
MUREKKEP, IKINCIL, CIZGI = "#1d1f22", "#52514e", "#d9d6cf"


def oku(bolum):
    out = []
    for f in sorted(glob.glob(os.path.join(HAM, bolum, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            out.append(json.load(fh))
    return out


def plt_kur():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": CIZGI,
                         "axes.labelcolor": MUREKKEP, "xtick.color": IKINCIL, "ytick.color": IKINCIL,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                         "grid.color": "#ecebe6", "grid.linewidth": 0.8, "figure.facecolor": "white",
                         "axes.facecolor": "white", "savefig.dpi": 130, "axes.titleweight": "bold",
                         "axes.titlesize": 11, "legend.frameon": False})
    return plt


def csv_yaz(ad, basliklar, satirlar):
    os.makedirs(SONUC, exist_ok=True)
    with open(os.path.join(SONUC, ad), "w", encoding="utf-8-sig") as f:
        f.write(";".join(basliklar) + "\n")
        for s in satirlar:
            f.write(";".join("" if v is None else str(v) for v in s) + "\n")


# ------------------------------------------------------------------ yardımcı geometri
def ozellik_yakin(kor, x, y, r=3.0):
    """Sahne özelliklerinden (kapı, kolon, dolap, köşe ...) (x, y)'ye r içindekiler: kısa metin listesi."""
    with open(os.path.join(FIZIK, "sahneler", kor + ".json"), encoding="utf-8") as f:
        s = json.load(f)
    out = []
    for o in s["ozellikler"]:
        m = o.get("merkez")
        if not m:
            continue
        d = math.hypot(m[0] - x, m[1] - y)
        if d <= r:
            out.append((d, "%s (%.1f m)" % (o["id"], d)))
    return [t for _, t in sorted(out)][:4]


def harita2b(ad):
    from konumlama.harita2b import Harita2B
    return Harita2B.dosyadan(os.path.join(KOD, "araclar", "haritalar", ad + ".json"))


def harita_ciz(ax, h, renk="#3d4148"):
    for (x1, y1, x2, y2) in h.parcalar:
        ax.plot([x1, x2], [y1, y2], color=renk, lw=1.2, solid_capstyle="round")
    for (cx, cy, r) in h.daireler:
        ax.add_patch(__import__("matplotlib").patches.Circle((cx, cy), r, fill=False, color=renk, lw=1.2))


def tarama_noktalari(poz, mesafeler, montaj=(0.19, 0.0)):
    x, y, th = poz
    n = len(mesafeler)
    a = -math.pi + np.arange(n) * (2 * math.pi / n)
    m = np.array([np.nan if v is None else v for v in mesafeler], dtype=float)
    ok = np.isfinite(m)
    ox = x + math.cos(th) * montaj[0] - math.sin(th) * montaj[1]
    oy = y + math.sin(th) * montaj[0] + math.cos(th) * montaj[1]
    return ox + m[ok] * np.cos(th + a[ok]), oy + m[ok] * np.sin(th + a[ok]), (ox, oy)


# ------------------------------------------------------------------ A
def analiz_a(plt, oz):
    A = oku("A")
    pozlar = [dict(p, kor=r["gorev"]["kor"], tur=r["gorev"]["tur"]) for r in A if "pozlar" in r for p in r["pozlar"]]
    hatalar = [r for r in A if "hata" in r]
    ras = [p for p in pozlar if p["tur"] == "rastgele"]
    yog = [p for p in pozlar if p["tur"] == "yogun"]

    def tablo(liste):
        T = {k: {c: 0 for c in K + ["kararsiz"]} for k in K}
        for p in liste:
            T[p["kor"]]["kararsiz" if p["kararsiz"] else p["en_olasi"]] += 1
        return T
    T = tablo(ras)
    oranlar = {}
    for k in K:
        n = sum(T[k].values())
        d = T[k][k]
        ky = T[k]["kararsiz"]
        oranlar[k] = dict(n=n, dogru=d, kararsiz=ky, yanlis=n - d - ky)
    top = {a: sum(oranlar[k][a] for k in K) for a in ("n", "dogru", "kararsiz", "yanlis")}
    # kararsızken hangi haritalar arasında kalıyor (ilk iki)
    ikili = {}
    for p in ras:
        if p["kararsiz"]:
            s = sorted(p["olasiliklar"].items(), key=lambda kv: -kv[1])
            key = "%s-%s" % tuple(sorted((KS[s[0][0]], KS[s[1][0]])))
            ikili.setdefault(p["kor"], {}).setdefault(key, 0)
            ikili[p["kor"]][key] += 1
    # kararsızken doğru harita ilk ikide mi
    ilk_ikide = sum(1 for p in ras if p["kararsiz"] and p["kor"] in
                    [kv[0] for kv in sorted(p["olasiliklar"].items(), key=lambda kv: -kv[1])[:2]])
    # yanlış (kesin) pozlar
    yanlislar = []
    for p in pozlar:
        if not p["kararsiz"] and p["en_olasi"] != p["kor"]:
            g = p["gercek"]
            e = p["en_poz"]
            yanlislar.append(dict(tur=p["tur"], kor=p["kor"], j=p["j"], s=p["s"], ters=p["ters"], yan=p["yan"],
                                  gercek=g, tahmin=p["en_olasi"], tahmin_poz=e, p=p["olasiliklar"][p["en_olasi"]],
                                  p_dogru=p["olasiliklar"][p["kor"]], fark=p["fark"],
                                  gercek_yakin=ozellik_yakin(p["kor"], g[0], g[1]),
                                  tahmin_yakin=ozellik_yakin(p["en_olasi"], e[0], e[1]), mesafeler=p["mesafeler"]))
    # doğru haritadaki en iyi poz hatası (konum)
    konum = [p["dogru_poz_hata_m"] for p in ras if not p["kararsiz"] and p["en_olasi"] == p["kor"]]
    konum_hepsi = [p["dogru_poz_hata_m"] for p in ras]
    csv_yaz("A_pozlar.csv", ["tur", "koridor", "j", "s_m", "ters", "yan_m", "x", "y", "yaw", "en_olasi", "kararsiz", "fark"]
            + ["p_" + KS[k] for k in K] + ["dogru_harita_poz_hata_m", "sure_s"],
            [[p["tur"], p["kor"], p["j"], p["s"], p["ters"], p["yan"], *p["gercek"], p["en_olasi"], p["kararsiz"], p["fark"]]
             + [p["olasiliklar"][k] for k in K] + [p["dogru_poz_hata_m"], p["sure_s"]] for p in pozlar])
    csv_yaz("A_karisiklik.csv", ["gercek \\ tahmin"] + [KS[k] for k in K] + ["kararsiz"],
            [[KS[k]] + [T[k][c] for c in K + ["kararsiz"]] for k in K])

    # --- görsel: karışıklık tablosu
    karisiklik_ciz(plt, T, "A. Durağan tek tarama: 6 × 7 karışıklık (koridor başına %d poz)" % (top["n"] // 6),
                   "poz sayısı", os.path.join(GORSEL, "A_karisiklik.png"))
    # --- görsel: benzer çift s'ye göre (yoğun + rastgele)
    fig, ax = plt.subplots(figsize=(10, 3.9))
    for ci, kor in enumerate(("koridor_5", "koridor_6")):
        es = "koridor_6" if kor == "koridor_5" else "koridor_5"
        for ters, mk in ((False, "o"), (True, "s")):
            ps = sorted([p for p in yog if p["kor"] == kor and p["ters"] == ters], key=lambda p: p["s"])
            ax.plot([p["s"] for p in ps], [p["olasiliklar"][kor] - p["olasiliklar"][es] for p in ps], marker=mk, ms=4,
                    lw=1.5, color=SERI[ci], ls="-" if not ters else "--",
                    label="gerçek %s, %s" % (KS[kor], "+x yönüne bakıyor" if not ters else "−x yönüne bakıyor"))
    ax.axvspan(*FARK_S, color="#f3c9b4", alpha=0.6, lw=0)
    ax.text(sum(FARK_S) / 2, 0.56, "fark bölgesi", ha="center", va="bottom", fontsize=8, color=IKINCIL)
    ax.axhline(0.5, color=YANLIS, lw=1, ls=":")
    ax.text(0.2, 0.51, "karar eşiği: p1 − p2 ≥ 0,5", fontsize=8, color=YANLIS, va="bottom")
    ax.axhline(0, color=IKINCIL, lw=0.8)
    ax.set_ylim(-0.25, 0.65)
    ax.set_xlabel("orta hat boyunca konum s (m)")
    ax.set_ylabel("p(gerçek) − p(eşi)")
    ax.legend(loc="lower left", fontsize=8, ncol=2)
    ax.set_title("A. Benzer çift, durağan tek tarama: doğru koridor lehine fark (yan sapma 0, yön sapması 0, her 1 m)",
                 loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(GORSEL, "A_benzer_cift_s.png"))
    plt.close(fig)
    # benzer çift yoğun: kaç poz kesin
    yog_ozet = {}
    for kor in ("koridor_5", "koridor_6"):
        ps = [p for p in yog if p["kor"] == kor]
        yog_ozet[kor] = dict(n=len(ps), dogru=sum(1 for p in ps if not p["kararsiz"] and p["en_olasi"] == kor),
                             kararsiz=sum(1 for p in ps if p["kararsiz"]),
                             yanlis=sum(1 for p in ps if not p["kararsiz"] and p["en_olasi"] != kor),
                             kesin_s=[(p["s"], p["ters"]) for p in ps if not p["kararsiz"]])
    # benzer çift rastgele: s'ye göre
    ras_cift = [dict(kor=p["kor"], s=p["s"], ters=p["ters"], p5=p["olasiliklar"]["koridor_5"],
                     p6=p["olasiliklar"]["koridor_6"], durum=("kararsiz" if p["kararsiz"] else
                                                              ("dogru" if p["en_olasi"] == p["kor"] else "yanlis")))
                for p in ras if p["kor"] in ("koridor_5", "koridor_6")]
    return dict(tablo=T, oranlar=oranlar, toplam=top, ikili=ikili, kararsiz_ilk_ikide=ilk_ikide,
                yanlislar=[{k: v for k, v in y.items() if k != "mesafeler"} for y in yanlislar], hatalar=len(hatalar),
                konum_dogru_med=float(np.median(konum)) if konum else None,
                konum_dogru_buyuk=sum(1 for v in konum if v > 0.5), konum_dogru_n=len(konum),
                konum_hepsi_buyuk=sum(1 for v in konum_hepsi if v > 0.5), yogun=yog_ozet, rastgele_cift=ras_cift,
                sure_ort=float(np.mean([p["sure_s"] for p in pozlar])) if pozlar else None), yanlislar


def karisiklik_ciz(plt, T, baslik, birim, yol, yuzde=False):
    sut = K + ["kararsiz"]
    M = np.array([[T[k][c] for c in sut] for k in K], dtype=float)
    satir_top = M.sum(1, keepdims=True)
    P = M / np.maximum(satir_top, 1)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list("mavi", ["#ffffff", "#cde2fb", "#6da7ec", "#2a78d6", "#104281"])
    gri = LinearSegmentedColormap.from_list("gri", ["#ffffff", "#e4e2dc", "#b9b6ad", "#8a877e", "#5e5c55"])
    P6 = P.copy()
    P6[:, 6] = np.nan
    ax.imshow(P6, cmap=cm, vmin=0, vmax=1, aspect="auto")
    Pk = np.full_like(P, np.nan)
    Pk[:, 6] = P[:, 6]
    ax.imshow(Pk, cmap=gri, vmin=0, vmax=1, aspect="auto")
    ax.axvline(5.5, color="white", lw=3)
    ax.grid(False)
    for i in range(len(K)):
        for j in range(len(sut)):
            v = M[i, j]
            if v == 0:
                continue
            metin = ("%.1f%%" % (100 * P[i, j])) if yuzde else ("%d" % v)
            ax.text(j, i, metin, ha="center", va="center", fontsize=9,
                    color="white" if P[i, j] > 0.55 else MUREKKEP,
                    fontweight="bold" if (j == i or (j < 6 and j != i)) else "normal")
            if j < 6 and j != i:
                ax.add_patch(__import__("matplotlib").patches.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                                                       ec=YANLIS, lw=2))
    ax.set_xticks(range(len(sut)), [KS[k] for k in K] + ["kararsız"])
    ax.set_yticks(range(len(K)), ["%s  %s" % (KS[k], BICIM[k]) for k in K])
    ax.set_xlabel("tahmin")
    ax.set_ylabel("gerçek koridor")
    ax.set_title(baslik, loc="left")
    ax.text(1.0, -0.16, "Hücre: %s. Kırmızı çerçeve = kendinden emin yanlış." % birim, transform=ax.transAxes,
            ha="right", fontsize=8, color=IKINCIL)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)


# ------------------------------------------------------------------ B / C / D
def sutunlardan(r):
    a = r["adimlar"]
    n = len(a["i"])
    return [{k: a[k][i] for k in a} for i in range(n)]


def analiz_hareket(plt, bolum):
    R = oku(bolum)
    ok = [r for r in R if "hata" not in r]
    hatali = [r for r in R if "hata" in r]
    satirlar = []
    for r in ok:
        g, o = r["gorev"], r["olcutler"]
        satirlar.append([r["gorev"]["id"], g["kor"], g["baslangic"], g["tohum"], r["lidar_tohum"], r["mcl_tohum"],
                         o["karar_yol_m"], o["karar_t_s"], o["ilk_dogru_yol_m"], o["yanlis_adim"], o["yanlis_sure_s"],
                         ",".join(KS[x] for x in o["yanlis_haritalar"])] + [o["yol_durum"][d] for d in ("2", "5", "10", "15")]
                        + [(o["konum_ileri"] or {}).get("ort_mutlak"), (o["konum_ileri"] or {}).get("p95"),
                           (o["konum_yan"] or {}).get("ort_mutlak"), (o["konum_yan"] or {}).get("p95"),
                           (o["konum_xy"] or {}).get("en_cok"), o["konum_yanlis_adim"], o["son_dogru"], o["son_durum"],
                           o["son_p_dogru"], o["toplam_yol_m"], r["surus"]["bitti"], r["surus"]["temas"],
                           r["surus"]["sonar_yavaslama_s"], len(r.get("insanlar", [])), r["sure_duvar_s"]]
                        + _kk_sutun(r))
    csv_yaz("%s_kosular.csv" % bolum,
            ["id", "koridor", "baslangic", "tohum", "lidar_tohum", "mcl_tohum", "karar_yol_m", "karar_t_s", "ilk_dogru_yol_m",
             "kesin_yanlis_adim", "kesin_yanlis_s", "yanlis_haritalar", "durum_2m", "durum_5m", "durum_10m", "durum_15m",
             "ileri_hata_ort_m", "ileri_hata_p95_m", "yan_hata_ort_m", "yan_hata_p95_m", "xy_hata_en_cok_m",
             "konum_kesin_yanlis_adim", "son_dogru", "son_durum", "son_p_dogru", "toplam_yol_m", "surus_bitti", "temas",
             "sonar_yavaslama_s", "insan", "sure_duvar_s", "konum_karar_yol_m", "kk_ileri_ort_m", "kk_ileri_en_cok_m",
             "kk_yan_ort_m", "kk_yan_en_cok_m"], satirlar)
    return ok, hatali


def _kk_sutun(r):
    i, il, yn = konum_karari(r)
    if i is None:
        return [None] * 5
    return [r["adimlar"]["yol"][i], round(float(np.abs(il).mean()), 3), round(float(np.abs(il).max()), 3),
            round(float(np.abs(yn).mean()), 3), round(float(np.abs(yn).max()), 3)]


def konum_karari(r):
    """Harita doğru + kararlı + konum kararlı olup sonuna dek öyle kalan ilk adım (karar_ani(konum_da=True) ile aynı
    kural). -> (sıra ya da None, ileri dizisi, yan dizisi) karar sonrası (doğru harita en olası iken)."""
    a = r["adimlar"]
    kor = r["gorev"]["kor"]
    n = len(a["i"])
    ok = [a["en"][i] == kor and not a["kararsiz"][i] and not a["konum_kararsiz"][i] for i in range(n)]
    if not ok[-1]:
        return None, np.zeros(0), np.zeros(0)
    i = n - 1
    while i > 0 and ok[i - 1]:
        i -= 1
    return i, np.array(a["ileri"][i:]), np.array(a["yan"][i:])


def adim_karisiklik(runs):
    T = {k: {c: 0 for c in K + ["kararsiz"]} for k in K}
    for r in runs:
        kor = r["gorev"]["kor"]
        a = r["adimlar"]
        for en, ky in zip(a["en"], a["kararsiz"]):
            T[kor]["kararsiz" if ky else en] += 1
    return T


def son_karisiklik(runs):
    T = {k: {c: 0 for c in K + ["kararsiz"]} for k in K}
    for r in runs:
        a = r["adimlar"]
        T[r["gorev"]["kor"]]["kararsiz" if a["kararsiz"][-1] else a["en"][-1]] += 1
    return T


def ozet_kosular(runs):
    """Koridor başına: karar yolu dağılımı, yol noktası durum oranları, yanlış adım, konum hatası, son doğru."""
    oz = {}
    for k in K:
        rs = [r for r in runs if r["gorev"]["kor"] == k]
        if not rs:
            continue
        ky = [r["olcutler"]["karar_yol_m"] for r in rs]
        kv = [v for v in ky if v is not None]
        yd = {}
        for d in ("2", "5", "10", "15"):
            v = [r["olcutler"]["yol_durum"][d] for r in rs]
            yd[d] = {s: sum(1 for x in v if x == s) for s in ("dogru", "kararsiz", "yanlis")}
            yd[d]["yok"] = sum(1 for x in v if x is None)
        ileri = [r["olcutler"]["konum_ileri"] for r in rs if r["olcutler"]["konum_ileri"]]
        yan = [r["olcutler"]["konum_yan"] for r in rs if r["olcutler"]["konum_yan"]]
        kk = [konum_karari(r) for r in rs]
        kk_yol = [r["adimlar"]["yol"][i] for r, (i, _, _) in zip(rs, kk) if i is not None]
        ki = np.concatenate([np.abs(x[1]) for x in kk]) if kk else np.zeros(0)
        kyn = np.concatenate([np.abs(x[2]) for x in kk]) if kk else np.zeros(0)
        kk_oran = float(np.mean([np.mean(r["adimlar"]["konum_kararsiz"]) for r in rs]))
        oz[k] = dict(n=len(rs), karar_yok=sum(1 for v in ky if v is None),
                     konum_karar_med=float(np.median(kk_yol)) if kk_yol else None,
                     konum_karar_max=max(kk_yol) if kk_yol else None, konum_karar_yok=sum(1 for x in kk if x[0] is None),
                     kk_ileri_ort=float(ki.mean()) if ki.size else None,
                     kk_ileri_p95=float(np.percentile(ki, 95)) if ki.size else None,
                     kk_ileri_max=float(ki.max()) if ki.size else None,
                     kk_yan_ort=float(kyn.mean()) if kyn.size else None,
                     kk_yan_p95=float(np.percentile(kyn, 95)) if kyn.size else None,
                     kk_yan_max=float(kyn.max()) if kyn.size else None, konum_kararsiz_oran=kk_oran,
                     karar_med=float(np.median(kv)) if kv else None, karar_min=min(kv) if kv else None,
                     karar_max=max(kv) if kv else None, yol_durum=yd,
                     yanlis_kosu=sum(1 for r in rs if r["olcutler"]["yanlis_adim"] > 0),
                     yanlis_adim=sum(r["olcutler"]["yanlis_adim"] for r in rs),
                     yanlis_sure=round(sum(r["olcutler"]["yanlis_sure_s"] for r in rs), 1),
                     ileri_ort=float(np.mean([x["ort_mutlak"] for x in ileri])) if ileri else None,
                     ileri_p95=float(np.max([x["p95"] for x in ileri])) if ileri else None,
                     ileri_max=float(np.max([x["en_cok"] for x in ileri])) if ileri else None,
                     yan_ort=float(np.mean([x["ort_mutlak"] for x in yan])) if yan else None,
                     yan_p95=float(np.max([x["p95"] for x in yan])) if yan else None,
                     yan_max=float(np.max([x["en_cok"] for x in yan])) if yan else None,
                     konum_yanlis_kosu=sum(1 for r in rs if r["olcutler"]["konum_yanlis_adim"] > 0),
                     konum_yanlis_adim=sum(r["olcutler"]["konum_yanlis_adim"] for r in rs),
                     # doğru = son adımda doğru harita VE kararlı (ham olcutler.son_dogru kararsızı da sayar)
                     son_dogru=sum(1 for r in rs if r["olcutler"]["son_durum"] == "dogru"),
                     son_yanlis=sum(1 for r in rs if r["olcutler"]["son_durum"] == "yanlis"),
                     son_kararsiz=sum(1 for r in rs if r["olcutler"]["son_durum"] == "kararsiz"),
                     temas=sum(1 for r in rs if r["surus"]["temas"]), bitmedi=sum(1 for r in rs if not r["surus"]["bitti"]),
                     yol_ort=float(np.mean([r["olcutler"]["toplam_yol_m"] for r in rs])))
    return oz


def yanlis_listesi(runs):
    out = []
    for r in runs:
        o = r["olcutler"]
        for d in o["yanlis_dilimler"]:
            out.append(dict(id=r["gorev"]["id"], kor=r["gorev"]["kor"], baslangic=r["gorev"]["baslangic"],
                            tohum=r["gorev"]["tohum"], harita=d["harita"], adim=d["adim"], sure_s=round(d["adim"] * 0.1, 1),
                            ilk_yol=d["ilk_yol"], son_yol=d["son_yol"], en_buyuk_p=round(d["en_buyuk_p"], 3)))
    return out


def konum_yanlis_listesi(runs):
    out = []
    for r in runs:
        if r["olcutler"]["konum_yanlis_adim"] > 0:
            ad = sutunlardan(r)
            kor = r["gorev"]["kor"]
            ky = [a for a in ad if a["en"] == kor and not a["kararsiz"] and not a["konum_kararsiz"]
                  and math.hypot(a["ileri"], a["yan"]) > 0.5]
            e = max(ky, key=lambda a: math.hypot(a["ileri"], a["yan"]))
            out.append(dict(id=r["gorev"]["id"], kor=kor, adim=len(ky), ilk_yol=ky[0]["yol"], son_yol=ky[-1]["yol"],
                            en_cok_m=round(math.hypot(e["ileri"], e["yan"]), 2), ileri=e["ileri"], yan=e["yan"],
                            gx=e["gx"], gy=e["gy"], x=e["x"], y=e["y"]))
    return out


def karar_dagilim_ciz(plt, runs, baslik, yol):
    fig, ax = plt.subplots(figsize=(9, 3.9))
    rng = np.random.default_rng(0)
    isaret = {"bas": "o", "son": "s", "orta": "^"}
    tavan = 0
    for i, k in enumerate(K):
        rs = [r for r in runs if r["gorev"]["kor"] == k]
        for r in rs:
            v = r["olcutler"]["karar_yol_m"]
            yanlis = r["olcutler"]["yanlis_adim"] > 0
            if v is None:
                v = r["olcutler"]["toplam_yol_m"]
                ax.scatter(i + rng.uniform(-0.18, 0.18), v, marker="x", s=46, color=YANLIS, zorder=3)
            else:
                ax.scatter(i + rng.uniform(-0.18, 0.18), v, marker=isaret[r["gorev"]["baslangic"]], s=40,
                           facecolor=(YANLIS if yanlis else SERI[0]), edgecolor="white", linewidth=1.2, zorder=3)
            tavan = max(tavan, v)
        kv = [r["olcutler"]["karar_yol_m"] for r in rs if r["olcutler"]["karar_yol_m"] is not None]
        if kv:
            ax.plot([i - 0.3, i + 0.3], [np.median(kv)] * 2, color=MUREKKEP, lw=2)
    ax.set_xticks(range(6), ["%s\n%s" % (KS[k], BICIM[k]) for k in K], fontsize=8.5)
    ax.set_ylabel("doğru karara kadar gidilen yol (m)")
    ax.set_title(baslik, loc="left")
    from matplotlib.lines import Line2D
    el = [Line2D([], [], marker=isaret[s], ls="", color=SERI[0], label=BAS_AD[s]) for s in ("bas", "son", "orta")]
    el += [Line2D([], [], marker="o", ls="", color=YANLIS, label="arada kendinden emin yanlış olan koşu"),
           Line2D([], [], marker="x", ls="", color=YANLIS, label="sonuna dek karar yok (koşu boyu)"),
           Line2D([], [], color=MUREKKEP, lw=2, label="ortanca")]
    ax.legend(handles=el, loc="upper left", fontsize=8, ncol=2)
    ax.set_ylim(-0.5, max(5, tavan * 1.35))
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)


# ------------------------------------------------------------------ benzer çift: farkın menzile girdiği nokta
def fark_gorunur(adimlar, oz, H5, H6):
    """Her adımda gerçek pozdan iki haritanın 2B taraması: kaç ışın > 5 cm farklı (500'ün kör olmayanları / MCL'nin 60'ı)."""
    from konumlama.tarama import tarama_hazirla
    n = int(round(360.0 / oz.acisal_cozunurluk_derece))
    acilar = -math.pi + np.arange(n) * (2 * math.pi / n)
    # sanal LiDAR kör maskesi (pay 5°) ve konumlayıcının 60 ışını
    d = np.degrees(acilar)
    kor_lidar = ((d - 134.2) % 360.0) <= ((225.8 - 134.2) % 360.0)
    if ETIKET != "v1":                     # v2: konumlayıcının maskesi = sanal LiDAR'ınki; v2_360: maske yok
        kor_lidar = oz.kor_mu(acilar)
    hz = tarama_hazirla({"t": 0, "acilar": acilar.tolist(), "mesafeler": [1.0] * n}, oz, 60)
    sec = np.searchsorted(acilar, hz.acilar - 1e-9)
    gx = np.array(adimlar["gx"]); gy = np.array(adimlar["gy"]); gth = np.array(adimlar["gth"])
    ox = gx + np.cos(gth) * oz.montaj_x_m
    oy = gy + np.sin(gth) * oz.montaj_x_m
    A = gth[:, None] + acilar[None, :]
    d5 = np.minimum(H5.isin_izle(ox, oy, A), 99.0)
    d6 = np.minimum(H6.isin_izle(ox, oy, A), 99.0)
    menzil = np.minimum(d5, d6) <= oz.menzil_maks_m
    fark = (np.abs(d5 - d6) > 0.05) & menzil & ~kor_lidar[None, :]
    return fark.sum(1), fark[:, sec].sum(1)


def benzer_cift(plt, runs, oz, bolum, yol_png):
    H5, H6 = harita2b("koridor_5"), harita2b("koridor_6")
    cift = [r for r in runs if r["gorev"]["kor"] in ("koridor_5", "koridor_6")]
    ozet = []
    fig, axs = plt.subplots(2, 3, figsize=(13, 6.4), sharey=True)
    for r in sorted(cift, key=lambda r: (r["gorev"]["kor"], r["gorev"]["baslangic"], r["gorev"]["tohum"])):
        a = r["adimlar"]
        kor = r["gorev"]["kor"]
        f500, f60 = fark_gorunur(a, oz, H5, H6)
        yol = np.array(a["yol"])
        i500 = int(np.argmax(f500 > 0)) if (f500 > 0).any() else None
        i60 = int(np.argmax(f60 > 0)) if (f60 > 0).any() else None
        s = np.array(a["gx"]) - X0
        yan_bolge = (s >= FARK_S[0]) & (s <= FARK_S[1])
        i_yan = int(np.argmax(yan_bolge)) if yan_bolge.any() else None
        p5 = np.array([p[4] for p in a["p"]]); p6 = np.array([p[5] for p in a["p"]])
        o = r["olcutler"]
        ozet.append(dict(id=r["gorev"]["id"], kor=kor, baslangic=r["gorev"]["baslangic"], tohum=r["gorev"]["tohum"],
                         fark_menzil_yol=(float(yol[i500]) if i500 is not None else None),
                         fark_60_yol=(float(yol[i60]) if i60 is not None else None),
                         fark_yaninda_yol=(float(yol[i_yan]) if i_yan is not None else None),
                         karar_yol=o["karar_yol_m"], yanlis_adim=o["yanlis_adim"],
                         yanlis_cift=sum(1 for e, ky in zip(a["en"], a["kararsiz"]) if not ky and e in ("koridor_5", "koridor_6") and e != kor),
                         p_es_en_cok=float((p6 if kor == "koridor_5" else p5).max()),
                         karar_s=(float(s[next(i for i, y in enumerate(yol) if y >= o["karar_yol_m"])])
                                  if o["karar_yol_m"] is not None else None),
                         son_p=float(p5[-1] if kor == "koridor_5" else p6[-1])))
        ax = axs[0 if kor == "koridor_5" else 1, ["bas", "son", "orta"].index(r["gorev"]["baslangic"])]
        ax.plot(yol, p5, color=SERI[0], lw=1.3, alpha=0.85)
        ax.plot(yol, p6, color=SERI[1], lw=1.3, alpha=0.85)
        if i500 is not None:
            ax.axvline(yol[i500], color=IKINCIL, lw=0.8, ls=":")
        if i60 is not None:
            ax.axvline(yol[i60], color=SERI[6], lw=0.8, ls="--")
        if yan_bolge.any():
            ys = yol[yan_bolge]
            # ardışık parçalar
            idx = np.flatnonzero(yan_bolge)
            parca = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
            for pc in parca:
                ax.axvspan(yol[pc[0]], yol[pc[-1]], color="#f3c9b4", alpha=0.35, lw=0)
    for i, kor in enumerate(("koridor_5", "koridor_6")):
        for j, b in enumerate(("bas", "son", "orta")):
            ax = axs[i, j]
            ax.set_title("Gerçek %s · %s" % (KS[kor], BAS_AD[b]), fontsize=10)
            ax.axhline(0.5, color=CIZGI, lw=0.8)
            if i == 1:
                ax.set_xlabel("gidilen yol (m)")
        axs[i, 0].set_ylabel("olasılık")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig.legend(handles=[Line2D([], [], color=SERI[0], lw=2, label="p(K5)"), Line2D([], [], color=SERI[1], lw=2, label="p(K6)"),
                        Line2D([], [], color=IKINCIL, ls=":", label="fark 500 ışında görünür (12 m, 2B ışın izleme)"),
                        Line2D([], [], color=SERI[6], ls="--", label="fark konumlayıcının 60 ışınında görünür"),
                        Patch(color="#f3c9b4", alpha=0.6, label="robot fark bölgesinin yanında (s 15,70–17,25 m)")],
               loc="lower center", ncol=3, fontsize=8.5)
    fig.suptitle("%s. Benzer çift: olasılık – gidilen yol (her çizgi bir tohum)" % bolum, fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.09, 1, 0.97))
    fig.savefig(yol_png)
    plt.close(fig)
    return ozet


# ------------------------------------------------------------------ üstten görünüm örneği
def ustten_ciz(plt, baslik, gercek_kor, gercek_poz, tahmin_kor, tahmin_poz, mesafeler, yol, alt_not=""):
    import matplotlib.patches as mp
    iki = tahmin_kor != gercek_kor
    fig, axs = plt.subplots(2 if iki else 1, 1, figsize=(11, 6.6 if iki else 3.8))
    axs = np.atleast_1d(axs)
    cizimler = [(axs[0], gercek_kor, gercek_poz, "Gerçek: %s, gerçek poz ve tarama" % KS[gercek_kor], DOGRU)]
    if iki:
        cizimler.append((axs[1], tahmin_kor, tahmin_poz, "Konumlayıcının kesin sandığı: %s, tahmin pozu ve aynı tarama"
                         % KS[tahmin_kor], YANLIS))
    else:
        cizimler.append((axs[0], tahmin_kor, tahmin_poz, None, YANLIS))
    for ax, kor, poz, bas, renk in cizimler:
        if bas is not None:
            harita_ciz(ax, harita2b(kor))
            ax.set_title(bas, loc="left", fontsize=10)
        tx, ty, (ox, oy) = tarama_noktalari(poz, mesafeler)
        if bas is not None and kor in ("koridor_5", "koridor_6"):
            ax.axvspan(17.5, 19.05, color="#f3c9b4", alpha=0.7, lw=0, zorder=0)
            ax.text(18.3, 7.75, "fark bölgesi\n(K6: kapı +0,6 m, yangın dolabı)", ha="center", va="bottom", fontsize=7.5,
                    color=IKINCIL)
        if bas is not None:
            ax.add_patch(mp.Circle((ox, oy), 12.0, fill=False, ls=":", color=IKINCIL, lw=0.9, zorder=1))
            ax.text(ox + 12.05, oy, "12 m", fontsize=7.5, color=IKINCIL, va="center", clip_on=True)
        ax.scatter(tx, ty, s=5, color=renk, alpha=0.8, lw=0, zorder=3)
        x, y, th = poz
        ax.add_patch(mp.FancyArrow(x, y, 0.6 * math.cos(th), 0.6 * math.sin(th), width=0.07, color=renk, zorder=4))
        ax.add_patch(mp.Circle((x, y), 0.26, fill=False, color=renk, lw=1.5, zorder=4))
        ax.set_aspect("equal")
        ax.grid(False)
        h = harita2b(kor)
        ax.set_xlim(-0.5, h.genislik + 0.5)
        ax.set_ylim(-0.5, h.yukseklik + 0.8)
    if not iki:
        axs[0].set_title("%s: gerçek poz (yeşil) ve kesin sanılan poz (kırmızı), aynı tarama ikisine konmuş"
                         % KS[gercek_kor], loc="left", fontsize=10)
    fig.suptitle(baslik, fontsize=11, fontweight="bold", x=0.01, ha="left")
    if alt_not:
        fig.text(0.01, 0.005, alt_not, fontsize=8, color=IKINCIL, va="bottom")
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(yol)
    plt.close(fig)


# ------------------------------------------------------------------ D
def d_ciz(plt, runs, yol, geride_cm):
    v1 = ETIKET == "v1"
    fig, axs = plt.subplots(2, 3, figsize=(13, 6.2), sharey=True)
    for i, k in enumerate(K):
        ax = axs.flat[i]
        for j, r in enumerate(sorted([r for r in runs if r["gorev"]["kor"] == k], key=lambda r: r["gorev"]["tohum"])):
            a = r["adimlar"]
            yl = np.array(a["yol"])
            sec = np.array([e == k for e in a["en"]]) & (np.array(a["isl"], dtype=bool) if v1 else True)
            ax.plot(yl[sec], np.abs(np.array(a["ileri"]))[sec], color=SERI[0], lw=1.2, alpha=0.9,
                    label="|ileri-geri hata|" if j == 0 else None)
            ax.plot(yl[sec], np.abs(np.array(a["yan"]))[sec], color=SERI[1], lw=1.2, alpha=0.9,
                    label="|yan hata|" if j == 0 else None)
            kk = np.array(a["konum_kararsiz"])
            if kk.any():
                ax.scatter(yl[kk], np.full(kk.sum(), -0.02), marker="|", color=IKINCIL, s=20)
        ax.set_title("%s %s" % (KS[k], BICIM[k]), fontsize=10)
        if i >= 3:
            ax.set_xlabel("gidilen yol (m)")
    axs[0, 0].set_ylabel("konum hatası (m)")
    axs[1, 0].set_ylabel("konum hatası (m)")
    axs[0, 2].legend(loc="upper right", fontsize=8)
    fig.suptitle(("D. Bilinen başlangıç (park noktası): yol boyunca konum hatası, robot çerçevesinde (her çizgi bir tohum;\n"
                  "yalnız taramanın işlendiği adımlar: arada konumlayıcı eski pozu bildirir, hareket hâlinde ort. %s cm geride)"
                  if v1 else
                  "D. Bilinen başlangıç (park noktası), " + ETIKET_AD[ETIKET] + ": yol boyunca konum hatası, robot çerçevesinde\n"
                  "(her çizgi bir tohum; bütün adımlar; işlenmeyen taramada poz odometriyle ilerletiliyor; o adımlarda ileri-geri ort. %s cm)")
                 % ("%.1f" % geride_cm).replace(".", ","), fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)


# ------------------------------------------------------------------ ana
def main():
    global ETIKET, HAM, GORSEL, SONUC
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiket", default="v1", choices=["v1", "v2", "v2_360"])
    ETIKET = ap.parse_args().etiket
    if ETIKET != "v1":
        HAM, GORSEL, SONUC = (os.path.join(BURASI, d + "_" + ETIKET) for d in ("ham", "gorsel", "sonuc"))
    os.makedirs(GORSEL, exist_ok=True)
    os.makedirs(SONUC, exist_ok=True)
    plt = plt_kur()
    if ETIKET != "v1":                     # her görselin sağ üst köşesine sürüm etiketi
        from matplotlib.figure import Figure
        _kaydet = Figure.savefig

        def _etiketli(self, *a, **k):
            self.text(0.995, 0.995, ETIKET_AD[ETIKET], ha="right", va="top", fontsize=9, color="#555555")
            return _kaydet(self, *a, **k)
        Figure.savefig = _etiketli
    import dataclasses
    from konumlama import LidarOzellik
    oz = LidarOzellik.varsa_dosyadan()
    if ETIKET == "v2_360":
        oz = dataclasses.replace(oz, kor_sektorler_derece=[])
    ozet = {}
    a, a_yanlis = analiz_a(plt, oz)
    ozet["A"] = a
    ornekler = []
    if a_yanlis:
        y = max(a_yanlis, key=lambda v: v["p"])
        ustten_ciz(plt, "A. Kendinden emin yanlış örneği (durağan tek tarama, p = %.2f)" % y["p"], y["kor"], y["gercek"],
                   y["tahmin"], y["tahmin_poz"][:3], y["mesafeler"], os.path.join(GORSEL, "ornek_A_yanlis.png"),
                   "Gerçek s = %.1f m, %s yön, yan %.2f m. Tahmin edilen poz %s'te (%.1f, %.1f)." %
                   (y["s"], "ters" if y["ters"] else "ileri", y["yan"], KS[y["tahmin"]], y["tahmin_poz"][0], y["tahmin_poz"][1]))
        ornekler.append("ornek_A_yanlis.png")
    for bol in ("B", "C", "D"):
        ok, hatali = analiz_hareket(plt, bol)
        if not ok:
            continue
        e = dict(n=len(ok), hatali=[r["gorev"]["id"] for r in hatali], hata_metni=[r["hata"][-400:] for r in hatali])
        e["adim_tablo"] = adim_karisiklik(ok)
        e["son_tablo"] = son_karisiklik(ok)
        e["koridor"] = ozet_kosular(ok)
        e["yanlislar"] = yanlis_listesi(ok)
        e["konum_yanlislar"] = konum_yanlis_listesi(ok)
        # işlenen / işlenmeyen tarama adımlarında ileri-geri hata (konum kararı sonrası, hareket hâlinde)
        isl_il, isl_yok = [], []
        for r in ok:
            i0, _, _ = konum_karari(r)
            if i0 is None:
                continue
            a = r["adimlar"]
            yl, t = np.array(a["yol"]), np.array(a["t"])
            v = np.gradient(yl, t) if len(t) > 2 else np.zeros(len(t))
            for i in range(i0, len(t)):
                if v[i] > 0.2 and a["en"][i] == r["gorev"]["kor"]:
                    (isl_il if a["isl"][i] else isl_yok).append(a["ileri"][i])
        e["islenen"] = dict(n_isl=len(isl_il), n_yok=len(isl_yok),
                            isl_ort=float(np.mean(isl_il)) if isl_il else None,
                            isl_mutlak=float(np.mean(np.abs(isl_il))) if isl_il else None,
                            yok_ort=float(np.mean(isl_yok)) if isl_yok else None,
                            yok_mutlak=float(np.mean(np.abs(isl_yok))) if isl_yok else None)
        e["sure_ort_s"] = float(np.mean([r["sure_duvar_s"] for r in ok]))
        e["sure_top_s"] = float(np.sum([r["sure_duvar_s"] for r in ok]))
        e["yol_top_m"] = float(np.sum([r["olcutler"]["toplam_yol_m"] for r in ok]))
        e["surus"] = dict(temas=[r["gorev"]["id"] for r in ok if r["surus"]["temas"]],
                          bitmedi=[r["gorev"]["id"] for r in ok if not r["surus"]["bitti"]],
                          sonar_yavas=[(r["gorev"]["id"], r["surus"]["sonar_yavaslama_s"]) for r in ok
                                       if r["surus"]["sonar_yavaslama_s"] > 1.0])
        if bol in ("B", "C"):
            karisiklik_ciz(plt, e["adim_tablo"], "%s. Hareket hâlinde, küresel: adımların dağılımı (%d koşu)" % (bol, len(ok)),
                           "satırdaki adımların yüzdesi (10 Hz tarama başına bir adım)",
                           os.path.join(GORSEL, "%s_karisiklik.png" % bol), yuzde=True)
            karar_dagilim_ciz(plt, ok, "%s. Doğru karara kadar gidilen yol (karar sonuna dek bozulmadı)" % bol,
                              os.path.join(GORSEL, "%s_karar_yolu.png" % bol))
            e["benzer_cift"] = benzer_cift(plt, ok, oz, bol, os.path.join(GORSEL, "%s_benzer_cift.png" % bol))
            # kendinden emin yanlış örneği (harita)
            adaylar = [(r, o) for r in ok for o in r.get("ornekler", []) if not o.get("konum")]
            if adaylar:
                def _dilim_p(ro):
                    rr, oo = ro
                    return max(d["en_buyuk_p"] for d in rr["olcutler"]["yanlis_dilimler"] if d["ilk_i"] == oo["adim"]["i"])
                r, o = max(adaylar, key=_dilim_p)
                ad = o["adim"]
                d = next(d for d in r["olcutler"]["yanlis_dilimler"] if d["ilk_i"] == ad["i"])
                ustten_ciz(plt, "%s. Kendinden emin yanlış koridor: %s, yanlışın başladığı an (yol %s m, p(%s) = %s)" %
                           (bol, r["gorev"]["id"], ("%.1f" % ad["yol"]).replace(".", ","), KS[ad["en"]],
                            ("%.2f" % ad["p"][K.index(ad["en"])]).replace(".", ",")),
                           r["gorev"]["kor"], (ad["gx"], ad["gy"], ad["gth"]), ad["en"], (ad["x"], ad["y"], ad["th"]),
                           o["mesafeler"], os.path.join(GORSEL, "ornek_%s_yanlis.png" % bol),
                           "Yanlış %d adım (%s s) sürdü, yol %s–%s m, en büyük p %s." %
                           (d["adim"], ("%.1f" % (d["adim"] * 0.1)).replace(".", ","), ("%.1f" % d["ilk_yol"]).replace(".", ","),
                            ("%.1f" % d["son_yol"]).replace(".", ","), ("%.2f" % d["en_buyuk_p"]).replace(".", ",")))
                ornekler.append("ornek_%s_yanlis.png" % bol)
        konum_ad = [(r, o) for r in ok for o in r.get("ornekler", []) if o.get("konum")]
        if konum_ad:
            r, o = max(konum_ad, key=lambda ro: math.hypot(ro[1]["adim"]["ileri"], ro[1]["adim"]["yan"]))
            ad = o["adim"]
            ustten_ciz(plt, "%s. Doğru koridor, konum kesin ama yanlış: %s (yol %.1f m, hata %.2f m)" %
                       (bol, r["gorev"]["id"], ad["yol"], math.hypot(ad["ileri"], ad["yan"])),
                       r["gorev"]["kor"], (ad["gx"], ad["gy"], ad["gth"]), r["gorev"]["kor"], (ad["x"], ad["y"], ad["th"]),
                       o["mesafeler"], os.path.join(GORSEL, "ornek_%s_konum.png" % bol))
            ornekler.append("ornek_%s_konum.png" % bol)
        if bol == "D":
            d_ciz(plt, ok, os.path.join(GORSEL, "D_hata_yol.png"), -100 * e["islenen"]["yok_ort"])
            e["yanlis_koridor_adim"] = sum(1 for r in ok for en, ky in zip(r["adimlar"]["en"], r["adimlar"]["kararsiz"])
                                           if en != r["gorev"]["kor"])
            e["konum_kararsiz_adim"] = sum(sum(r["adimlar"]["konum_kararsiz"]) for r in ok)
            e["adim_top"] = sum(len(r["adimlar"]["i"]) for r in ok)
            e["en_kucuk_p_dogru"] = min(min(p[K.index(r["gorev"]["kor"])] for p in r["adimlar"]["p"]) for r in ok)
        ozet[bol] = e
    ozet["ornek_gorseller"] = ornekler
    with open(os.path.join(SONUC, "ozet.json"), "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=1)
    print("tamam:", ", ".join("%s %s" % (b, ozet[b]["n"] if b != "A" else ozet[b]["toplam"]["n"]) for b in ozet if b in "ABCD"))


if __name__ == "__main__":
    main()
