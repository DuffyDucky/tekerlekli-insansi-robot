"""Beyin durumunu (harita, yol, hedef, poz) gerçek haritanın üstünde çiz (matplotlib; ayıklama ve rapor görseli)."""

import math

import numpy as np


def ciz(sahne, beyin, yol_png, gercek_poz=None, baslik="", iz=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .benzet2b import Dunya2B
    from .sahne import beyinden_dunyaya
    d = beyin.durum()
    h = d.get("harita")
    fig, ax = plt.subplots(figsize=(8, 8))
    if h:
        iz_ = np.asarray(h["izgara"])
        coz = h["cozunurluk_m"]
        x0, y0 = h["orijin"]
        # beynin haritası dünya çerçevesine: hücre merkezlerini çevirip noktalarla çiz
        for deger, renk, boy in ((0, "#cfe8cf", 2), (100, "#d62728", 3)):
            jj, ii = np.nonzero(iz_ == deger)
            if ii.size:
                wx, wy = beyinden_dunyaya(sahne, x0 + (ii + 0.5) * coz, y0 + (jj + 0.5) * coz)
                ax.scatter(wx, wy, s=boy, c=renk, marker="s", linewidths=0)
    P = Dunya2B(sahne.veri).parcalar
    for x1, y1, x2, y2 in P:
        ax.plot([x1, x2], [y1, y2], "k-", lw=0.8)
    for c, renk in ((sahne.start_cizgi, "g"), (sahne.finish_cizgi, "m")):
        if c:
            ax.plot([c[0][0], c[1][0]], [c[0][1], c[1][1]], renk + "-", lw=3)
    if d.get("yol"):
        Y = np.asarray(d["yol"])
        wx, wy = beyinden_dunyaya(sahne, Y[:, 0], Y[:, 1])
        ax.plot(wx, wy, "b.-", lw=1.2)
    if d.get("hedef") is not None:
        hx, hy = beyinden_dunyaya(sahne, *d["hedef"])
        ax.plot(hx, hy, "b*", ms=14)
    if iz is not None and len(iz):
        I = np.asarray(iz)
        ax.plot(I[:, 0], I[:, 1], "-", color="#ff7f0e", lw=0.8)
    p = d.get("poz")
    if p is not None:
        wx, wy = beyinden_dunyaya(sahne, p[0], p[1])
        th = p[2] + sahne.start_poz[2]
        ax.arrow(float(wx), float(wy), 0.4 * math.cos(th), 0.4 * math.sin(th), color="b", width=0.03)
    if gercek_poz is not None:
        x, y, th = gercek_poz
        c, s = math.cos(th), math.sin(th)
        k = np.array([(0.264, 0.262), (-0.264, 0.262), (-0.264, -0.262), (0.264, -0.262), (0.264, 0.262)])
        ax.plot(x + c * k[:, 0] - s * k[:, 1], y + s * k[:, 0] + c * k[:, 1], "k-", lw=1.5)
    ax.set_aspect("equal")
    ax.set_title(baslik + "  mod=%s" % d.get("mod"), fontsize=9)
    fig.tight_layout()
    fig.savefig(yol_png, dpi=90)
    plt.close(fig)
