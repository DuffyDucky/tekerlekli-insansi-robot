"""Harita (gri) ile bozulmuş dünyanın (kırmızı; cam kapının LiDAR'a görünen hâli mavi kesikli, dönüşsüz yüzey siyah,
insan bacakları yeşil) üstten görünümü. -> gorsel/dunya_<koridor>.png

    py -3 ciz_dunya.py [koridor_4]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ortak  # noqa: E402


def ciz(kor="koridor_4", kosul_idler=("kapi_4", "esya_4", "insan_4", "grup_3", "egrilme_4", "cam_4", "donussuz_2",
                                       "okul_agir")):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from kos2b import _dunya_ve_kalabalik
    harita = ortak.harita_oku(kor)
    fig, eksen = plt.subplots(len(kosul_idler), 1, figsize=(11, 2.6 * len(kosul_idler)))
    for ax, kid in zip(eksen, kosul_idler):
        k = ortak.kosul(kid)
        dn, kal = _dunya_ve_kalabalik(dict(senaryo="ab", koridor=kor, tohum=1, kosul=kid), k)
        for x1, y1, x2, y2 in harita["duvarlar"]:
            ax.plot([x1, x2], [y1, y2], color="0.6", lw=2.5, zorder=1)
        for x1, y1, x2, y2 in dn["veri"]["duvarlar"]:
            ax.plot([x1, x2], [y1, y2], color="#c0392b", lw=0.9, zorder=2)
        if dn["lidar_veri"] is not dn["veri"]:
            for x1, y1, x2, y2 in dn["lidar_veri"]["duvarlar"]:
                ax.plot([x1, x2], [y1, y2], color="#2c6fbb", lw=0.8, ls="--", zorder=3)
        for x1, y1, x2, y2 in dn["siyah"]:
            ax.plot([x1, x2], [y1, y2], color="k", lw=2.0, zorder=4)
        for e in dn["veri"]["engeller"]:
            if e["tur"] == "kutu":
                ax.add_patch(plt.Rectangle((e["x"], e["y"]), e["g"], e["d"], color="#c0392b", alpha=0.5, zorder=2))
            else:
                ax.add_patch(plt.Circle((e["x"], e["y"]), e["r"], color="#c0392b", alpha=0.5, zorder=2))
        if kal is not None:
            B = kal.bacaklar()
            for x, y, r in B:
                wx, wy = dn["T"].nokta(x, y)
                ax.add_patch(plt.Circle((wx, wy), r, color="#27ae60", zorder=5))
        ax.set_aspect("equal")
        ax.set_title("%s / %s  %s" % (kor, kid, dn["kayit"]), fontsize=8)
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    os.makedirs(ortak.GORSEL, exist_ok=True)
    yol = os.path.join(ortak.GORSEL, "dunya_%s.png" % kor)
    fig.savefig(yol, dpi=90)
    print(yol)


if __name__ == "__main__":
    ciz(*(sys.argv[1:2] or ["koridor_4"]))
