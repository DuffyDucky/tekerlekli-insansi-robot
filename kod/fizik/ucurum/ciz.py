"""Uçurum deneyi görselleri (py -3, matplotlib): sonuc/*.csv -> gorsel/*.png.

    py -3 kod\\fizik\\ucurum\\ciz.py
"""

import collections
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import analiz as A  # noqa: E402

GORSEL = os.path.join(A.BURASI, "gorsel")
RENK = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]   # sabit sıra (dataviz varsayılan paleti)
YUZEY, MUREKKEP, IKINCIL = "#fcfcfb", "#0b0b0b", "#52514e"


def _eksen(ax):
    ax.set_facecolor(YUZEY)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(IKINCIL)
    ax.tick_params(colors=IKINCIL)
    ax.grid(True, color="#e4e3df", linewidth=0.6)
    ax.set_axisbelow(True)


def durma():
    R = [r for r in A.oku("durma") if r["sahne"] == "duz" and r["tohum"] == "1"]
    kipler = [("kes", None, "motor kesme (boşta)"), ("fren", None, "kısa devre freni"), ("rampa", "1.0", "rampa 1,0 m/s²"),
              ("rampa", "2.0", "rampa 2,0 m/s²")]
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=120, facecolor=YUZEY)
    _eksen(ax)
    for i, (k, a, ad) in enumerate(kipler):
        L = sorted((float(r["v"]), float(r["durma_yolu_m"]) * 100) for r in R if r["fren"] == k and (a is None or r["fren_ivme"] == a))
        ax.plot([x for x, _ in L], [y for _, y in L], color=RENK[i], linewidth=2, marker="o", markersize=7, label=ad)
        ax.annotate(ad, (L[-1][0], L[-1][1]), xytext=(6, 0), textcoords="offset points", va="center", color=MUREKKEP, fontsize=8)
    ax.set_xlabel("hız m/s", color=MUREKKEP)
    ax.set_ylabel("tetikten durmaya yol cm", color=MUREKKEP)
    ax.set_xlim(0.05, 0.52)
    ax.set_title("Düz zeminde durma yolu (ONERI, model)", color=MUREKKEP, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(GORSEL, "durma_yolu.png"), facecolor=YUZEY)
    plt.close(fig)


def yerlesim():
    R = [r for r in A.oku("gelistirme") if r["tur"] == "ileri" and r["fren"] == "rampa"]
    g = collections.defaultdict(list)
    for r in R:
        g[r["yerlesim"]].append(r)
    adlar = sorted(g, key=lambda y: A._ozet(g[y])[3] or -99)
    fig, ax = plt.subplots(figsize=(7.5, 6), dpi=120, facecolor=YUZEY)
    _eksen(ax)
    en_az = [A._ozet(g[y])[3] for y in adlar]
    p05 = [A._ozet(g[y])[4] for y in adlar]
    yy = range(len(adlar))
    ax.barh([y + 0.2 for y in yy], en_az, height=0.38, color=RENK[0], label="en küçük pay")
    ax.barh([y - 0.2 for y in yy], p05, height=0.38, color=RENK[1], label="%5 pay")
    ax.axvline(0, color=MUREKKEP, linewidth=1)
    ax.set_yticks(list(yy))
    ax.set_yticklabels(["%s (%d düştü)" % (y, A._ozet(g[y])[1]) for y in adlar], fontsize=7, color=MUREKKEP)
    ax.set_xlabel("teker temas noktasının kenara payı cm (negatif = kenarı geçti)", color=MUREKKEP)
    ax.set_title("Geliştirme ızgarası, ileri yaklaşma, fren rampa 2,0 m/s²", color=MUREKKEP, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(GORSEL, "yerlesim_pay.png"), facecolor=YUZEY)
    plt.close(fig)


def sinama():
    R = [r for r in A.oku("sinama") if r["alt"] == "ileri"]
    if not R:
        return
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=120, facecolor=YUZEY)
    _eksen(ax)
    for j, v in enumerate(("0.1", "0.25", "0.39")):
        M = [r for r in R if r["v"] == v and A.fl(r["pay_min_cm"]) is not None]
        ax.scatter([float(r["aci"]) + (j - 1) * 1.5 for r in M], [A.fl(r["pay_min_cm"]) for r in M], s=14, color=RENK[j],
                   label="%s m/s" % v.replace(".", ","), alpha=0.8)
    ax.axhline(0, color=MUREKKEP, linewidth=1)
    ax.set_ylim(bottom=-1)
    ax.set_xlabel("yaklaşma açısı ° (kenar normaline göre)", color=MUREKKEP)
    ax.set_ylabel("en küçük teker payı cm (0 altı = düştü)", color=MUREKKEP)
    ax.set_title("Sınama: 2KD+2AD z120 e30, 4 yeni geometri, tohum 101-110, %d koşu, %d düşme" % (len(R), sum(A.boolv(r["dustu"]) for r in R)),
                 color=MUREKKEP, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(GORSEL, "sinama_pay.png"), facecolor=YUZEY)
    plt.close(fig)


def _gen(s):
    return int(s.split("_")[1]) if s.startswith("acik_") and not s.endswith("_sig") else None


def dar():
    """Dar açıklık: genişliğe göre en küçük pay, yerleşim başına; solda geliştirme, sağda sınama."""
    parca = [("Geliştirme (tohum 1-2)", A.oku("dar_gelistirme")), ("Sınama (tohum 101-105)", A.oku("sinama2") + A.oku("sinama2_karsi"))]
    fig, eks = plt.subplots(1, 2, figsize=(10, 4.4), dpi=120, facecolor=YUZEY, sharey=True)
    for ax, (bas, R) in zip(eks, parca):
        _eksen(ax)
        R = [r for r in R if r.get("alt") == "dar" and _gen(r["sahne"])]
        for j, y in enumerate(sorted({r["yerlesim"] for r in R})):
            g = collections.defaultdict(list)
            for r in R:
                if r["yerlesim"] == y:
                    g[_gen(r["sahne"])].append(r)
            xs = sorted(g)
            en_az = [A._ozet(g[x])[3] for x in xs]
            dus = sum(A._ozet(g[x])[1] for x in xs)
            ax.plot(xs, en_az, color=RENK[j], linewidth=2, marker="o", markersize=6,
                    label="%s (%d / %d düştü)" % (y.split("_")[0], dus, sum(len(g[x]) for x in xs)))
        ax.axhline(0, color=MUREKKEP, linewidth=1)
        ax.set_xlabel("açıklık genişliği cm (3 m derin)", color=MUREKKEP)
        ax.set_title(bas, color=MUREKKEP, fontsize=10, loc="left")
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    eks[0].set_ylabel("en küçük teker payı cm (0 altı = düştü)", color=MUREKKEP)
    fig.suptitle("Robottan dar açıklık: z120 e30, 100 mm / 3, yavasla; 3 hız x 3 açı x 5 yanal kayma", color=MUREKKEP, fontsize=10, x=0.01,
                 ha="left")
    fig.tight_layout()
    fig.savefig(os.path.join(GORSEL, "dar_aciklik.png"), facecolor=YUZEY)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(GORSEL, exist_ok=True)
    for f in (durma, yerlesim, sinama, dar):
        try:
            f()
            print("tamam", f.__name__)
        except Exception as h:
            print("atlandi", f.__name__, h)
