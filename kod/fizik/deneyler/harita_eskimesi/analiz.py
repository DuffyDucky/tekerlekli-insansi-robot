"""Ham sonuçlardan CSV, özet tablolar (Markdown), kırılma noktaları, sıralama ve görseller.

    py -3 analiz.py          # -> sonuc/ab_2b.csv, sonuc/kayip_2b.csv, sonuc/mujoco.csv, sonuc/ozet.json,
                             #    sonuc/tablolar.md, gorsel/basari_*.png, gorsel/mujoco_2b.png"""

import csv
import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ortak  # noqa: E402
from kos2b import ALANLAR_AB, ALANLAR_KAYIP  # noqa: E402

ETIKET = {
    "taban": "taban (bozulmasız)", "kapi": "a. kapı durumu değişen oran", "esya": "b. eşya (adet / 10 m)",
    "insan": "c. insan (kişi / 10 m)", "grup": "c. grup (duvardan içeri m)", "olcek": "d. ölçek hatası",
    "genislik": "d. genişlik sapması (m)", "egrilme": "d. eğrilme (° / 20 m)", "gurultu": "e. menzil gürültüsü σ (m)",
    "donussuz": "e. dönüşsüz yüzey oranı", "cam": "e. cam kapı oranı", "menzil": "e. en uzun menzil (m)",
    "odo_olcek": "f. odometri ölçek (+)", "odo_donus": "f. dönüş hatası (+, %14 tabana ek)",
    "odo_kayma": "f. ani kayma (olay / dk)", "okul": "g. okul günü (hafif / orta / ağır)"}


def oku(desen):
    out = []
    for y in sorted(glob.glob(desen)):
        with open(y, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def csv_yaz(yol, satir, alanlar):
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        w.writeheader()
        for s in satir:
            w.writerow(s)


def _sayi(v):
    return v is not None and isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v))


def _med(L):
    L = sorted(x for x in L if _sayi(x))
    if not L:
        return None
    n = len(L)
    return L[n // 2] if n % 2 else 0.5 * (L[n // 2 - 1] + L[n // 2])


def _ort(L):
    L = [x for x in L if _sayi(x)]
    return sum(L) / len(L) if L else None


def ozetle(satir, kayip=False):
    gr = {}
    for s in satir:
        gr.setdefault(s["kosul"], []).append(s)
    out = {}
    for k in ortak.kosullar():
        S = gr.get(k["id"])
        if not S:
            continue
        n = len(S)
        b = sum(1 for s in S if s.get("basari"))
        o = dict(kosul=k["id"], etken=k["etken"], kademe=k["kademe"], deger=k["deger"], n=n, basari=b,
                 oran=b / n, istisna=sum(1 for s in S if "istisna" in str(s.get("neden", ""))),
                 varis_med=_med([s.get("varis_hatasi_m") for s in S if s.get("basari")]),
                 konum_ort=_ort([s.get("konum_ort_m") for s in S]),
                 konum_p95=_ort([s.get("konum_p95_m") for s in S]),
                 konum_maks=max([s.get("konum_maks_m") for s in S if _sayi(s.get("konum_maks_m"))] or [None],
                                key=lambda x: -1 if x is None else x),
                 kesin_yanlis_kosu=sum(1 for s in S if (s.get("konum_kesin_yanlis") or 0) > 0),
                 temas_hareketli=sum(s.get("temas_hareketli") or 0 for s in S),
                 temas_duran=sum(s.get("temas_duran") or 0 for s in S),
                 temas_kosu=sum(1 for s in S if (s.get("temas_olay") or 0) > 0),
                 sure_med=_med([s.get("sure_s") for s in S if s.get("basari")]),
                 bekleme_ort=_ort([s.get("bekleme_s") for s in S]),
                 nan_orani=_ort([s.get("nan_orani") for s in S]))
        if kayip:
            o.update(yanlis_karar=sum(1 for s in S if s.get("karar_koridor") and s.get("karar_dogru") is False),
                     yanlis_son=sum(1 for s in S if s.get("son_koridor") and s.get("son_koridor") != s["koridor"]),
                     karar_yok=sum(1 for s in S if s.get("karar_t_s") is None),
                     karar_t_med=_med([s.get("karar_t_s") for s in S]),
                     karar_yol_med=_med([s.get("karar_yol_m") for s in S]),
                     yanlis_kesin_adim_kosu=sum(1 for s in S if (s.get("yanlis_kesin") or 0) > 0))
        out[k["id"]] = o
    return out


def kirilma(oz, esik=0.9):
    """Etken başına: başarının ilk kez < esik olduğu kademe (yoksa None) + kademe başına oran."""
    out = {}
    for et in list(ortak.KADEMELER) + ["okul"]:
        L = sorted([o for o in oz.values() if o["etken"] == et], key=lambda o: o["kademe"])
        if not L:
            continue
        ilk = next((o for o in L if o["oran"] < esik), None)
        out[et] = dict(kirilma_kademe=(ilk["kademe"] if ilk else None), kirilma_deger=(ilk["deger"] if ilk else None),
                       oranlar=[(o["kademe"], o["deger"], o["basari"], o["n"]) for o in L],
                       ort_oran=sum(o["oran"] for o in L) / len(L), en_kotu=min(o["oran"] for o in L))
    return out


def _f(v, b=2, yuzde=False):
    if v is None:
        return "-"
    if yuzde:
        return "%d %%" % round(100 * v)
    return ("%." + str(b) + "f") % v


def _deger(o):
    et, d = o["etken"], o["deger"]
    if et == "okul":
        return ["hafif", "orta", "ağır"][int(d) - 1]
    if et in ("kapi", "donussuz", "cam", "olcek", "odo_olcek", "odo_donus"):
        return "%g %%" % round(100 * d, 1)
    if et == "genislik":
        return "± %g cm" % round(100 * d, 1)
    return "%g" % d


def tablo_ab(oz, taban_n=None):
    s = ["| Koşul | Kademe | Başarı | Varış hatası medyan (m) | Konum hatası ort / p95 / en büyük (m) | Kesin-yanlış konum (koşu) | Temas hareketli / duran | Bekleme ort (s) | NaN ışın |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    onceki = None
    for o in oz.values():
        et = ETIKET.get(o["etken"], o["etken"]) if o["etken"] != onceki else ""
        onceki = o["etken"]
        s.append("| %s | %s | %d / %d | %s | %s / %s / %s | %d | %d / %d | %s | %s |" % (
            et, _deger(o) if o["kademe"] else "-",
            o["basari"], o["n"], _f(o["varis_med"], 3), _f(o["konum_ort"], 3), _f(o["konum_p95"], 3),
            _f(o["konum_maks"], 2), o["kesin_yanlis_kosu"], o["temas_hareketli"], o["temas_duran"],
            _f(o["bekleme_ort"], 1), _f(o["nan_orani"], 2)))
    return "\n".join(s)


def tablo_kayip(oz):
    s = ["| Koşul | Kademe | Başarı | Yanlış koridora kesin karar (ilk / son) | Karar yok | Karar süresi medyan (s) | Karar yolu medyan (m) | Konum hatası ort / p95 (m, karardan sonra) | Temas hareketli / duran |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    onceki = None
    for o in oz.values():
        et = ETIKET.get(o["etken"], o["etken"]) if o["etken"] != onceki else ""
        onceki = o["etken"]
        s.append("| %s | %s | %d / %d | %d / %d | %d | %s | %s | %s / %s | %d / %d |" % (
            et, _deger(o) if o["kademe"] else "-", o["basari"], o["n"], o["yanlis_karar"], o["yanlis_son"],
            o["karar_yok"], _f(o["karar_t_med"], 0), _f(o["karar_yol_med"], 1), _f(o["konum_ort"], 3),
            _f(o["konum_p95"], 3), o["temas_hareketli"], o["temas_duran"]))
    return "\n".join(s)


def tablo_kirilma(kab, kky):
    s = ["| Etken | A'dan B'ye kırılma (başarı < %90) | A'dan B'ye kademe başarıları | Kayıp kırılma | Kayıp kademe başarıları |",
         "| --- | --- | --- | --- | --- |"]
    for et in kab:
        a = kab[et]
        b = kky.get(et, {})
        f = lambda r: ", ".join("%d/%d" % (x[2], x[3]) for x in r) if r else "-"

        def kd(r, et_=et):
            if not r or r.get("kirilma_kademe") is None:
                return "yok" if r else "-"
            return _deger(dict(etken=et_, deger=r["kirilma_deger"])) + " (k%d)" % r["kirilma_kademe"]
        s.append("| %s | %s | %s | %s | %s |" % (ETIKET.get(et, et), kd(a), f(a["oranlar"]), kd(b), f(b.get("oranlar"))))
    return "\n".join(s)


def siralama(kab, kky):
    """Zarar sırası: A'dan B'ye ve kayıpta ortalama başarı (kademeler üzerinden), sonra en kötü kademe."""
    L = []
    for et in kab:
        if et == "okul":
            continue
        a, b = kab[et], kky.get(et)
        L.append((et, a["ort_oran"], a["en_kotu"], b["ort_oran"] if b else None, b["en_kotu"] if b else None))
    L.sort(key=lambda r: (r[1] + (r[3] if r[3] is not None else r[1])) / 2)
    return L


def mujoco_karsilastir(mj, ab):
    idx = {(s["kosul"], s["koridor"], s["tohum"]): s for s in ab}
    out = []
    for m in mj:
        b = idx.get((m["kosul"], m["koridor"], m["tohum"]))
        out.append(dict(kosul=m["kosul"], koridor=m["koridor"], tohum=m["tohum"], mj_basari=m.get("basari"),
                        b2_basari=(b or {}).get("basari"), mj_varis=m.get("varis_hatasi_m"),
                        b2_varis=(b or {}).get("varis_hatasi_m"), mj_konum=m.get("konum_ort_m"),
                        b2_konum=(b or {}).get("konum_ort_m"), mj_konum_maks=m.get("konum_maks_m"),
                        b2_konum_maks=(b or {}).get("konum_maks_m"), mj_temas=m.get("temas_olay"),
                        b2_temas=(b or {}).get("temas_olay"), mj_neden=m.get("neden"), b2_neden=(b or {}).get("neden"),
                        mj_nan=m.get("nan_orani"), b2_nan=(b or {}).get("nan_orani")))
    return out


def tablo_mujoco(K):
    gr = {}
    for r in K:
        gr.setdefault(r["kosul"], []).append(r)
    s = ["| Koşul | MuJoCo başarı | 2B başarı (aynı tohum) | Uyuşmayan koşu | MuJoCo / 2B konum hatası ort (m) | MuJoCo / 2B varış hatası medyan (m) | Temas MuJoCo / 2B |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for k in ortak.kosullar():
        L = gr.get(k["id"])
        if not L:
            continue
        mjb = sum(1 for r in L if r["mj_basari"])
        b2 = sum(1 for r in L if r["b2_basari"])
        uy = [r["koridor"] + ":" + str(r["tohum"]) for r in L if bool(r["mj_basari"]) != bool(r["b2_basari"])]
        s.append("| %s | %d / %d | %d / %d | %s | %s / %s | %s / %s | %d / %d |" % (
            k["id"], mjb, len(L), b2, len(L), ", ".join(uy) or "-", _f(_ort([r["mj_konum"] for r in L]), 3),
            _f(_ort([r["b2_konum"] for r in L]), 3), _f(_med([r["mj_varis"] for r in L]), 3),
            _f(_med([r["b2_varis"] for r in L]), 3), sum(r["mj_temas"] or 0 for r in L),
            sum(r["b2_temas"] or 0 for r in L)))
    return "\n".join(s)


def tablo_varyant(V):
    gr = {}
    for s in V:
        gr.setdefault((s["kosul"], s["varyant"]), []).append(s)
    s_ = ["| Koşul | Varsayılan başarı | izleme başarı | Varsayılan / izleme konum hatası ort (m) | en büyük (m) | Temas varsayılan / izleme |",
          "| --- | --- | --- | --- | --- | --- |"]
    for k in ortak.kosullar():
        a, b = gr.get((k["id"], "varsayilan")), gr.get((k["id"], "izleme"))
        if not a or not b:
            continue
        s_.append("| %s | %d / %d | %d / %d | %s / %s | %s / %s | %d / %d |" % (
            k["id"], sum(1 for x in a if x.get("basari")), len(a), sum(1 for x in b if x.get("basari")), len(b),
            _f(_ort([x.get("konum_ort_m") for x in a]), 3), _f(_ort([x.get("konum_ort_m") for x in b]), 3),
            _f(max([x.get("konum_maks_m") or 0 for x in a]), 2), _f(max([x.get("konum_maks_m") or 0 for x in b]), 2),
            sum(x.get("temas_olay") or 0 for x in a), sum(x.get("temas_olay") or 0 for x in b)))
    return "\n".join(s_)


def gorseller(oz_ab, oz_ky, K):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(ortak.GORSEL, exist_ok=True)
    etkenler = list(ortak.KADEMELER) + ["okul"]
    fig, eksen = plt.subplots(3, 5, figsize=(15, 8.5), sharey=True)
    for ax, et in zip(eksen.ravel(), etkenler):
        for oz, renk, ad in ((oz_ab, "#2c6fbb", "A'dan B'ye"), (oz_ky, "#c0392b", "kayıp")):
            L = sorted([o for o in oz.values() if o["etken"] == et], key=lambda o: o["kademe"])
            t = oz.get("taban")
            if not L:
                continue
            xs = [0] + [o["kademe"] for o in L] if t else [o["kademe"] for o in L]
            ys = ([t["oran"]] if t else []) + [o["oran"] for o in L]
            ax.plot(xs, [100 * y for y in ys], "o-", color=renk, label=ad, lw=1.5, ms=4)
        ax.axhline(90, color="0.5", lw=0.8, ls="--")
        ax.set_title(ETIKET.get(et, et), fontsize=8.5)
        L = sorted([o for o in oz_ab.values() if o["etken"] == et], key=lambda o: o["kademe"])
        ax.set_xticks([0] + [o["kademe"] for o in L])
        ax.set_xticklabels(["0"] + [_deger(o) for o in L], fontsize=7)
        ax.set_ylim(-5, 105)
        ax.grid(alpha=0.25)
    eksen.ravel()[0].legend(fontsize=7, loc="lower left")
    for ax in eksen.ravel()[len(etkenler):]:
        ax.axis("off")
    fig.suptitle("Başarı (%) etken kademesine göre; 2B benzetici, koşul başına 12 koşu (6 koridor x 2 tohum); "
                 "kesikli çizgi %90", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(ortak.GORSEL, "basari_kademe.png"), dpi=90)
    plt.close(fig)
    if K:
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
        x = [r["b2_konum"] for r in K if _sayi(r["b2_konum"]) and _sayi(r["mj_konum"])]
        y = [r["mj_konum"] for r in K if _sayi(r["b2_konum"]) and _sayi(r["mj_konum"])]
        ax[0].loglog([max(v, 1e-3) for v in x], [max(v, 1e-3) for v in y], "o", ms=4, alpha=0.7)
        ax[0].plot([1e-3, 30], [1e-3, 30], "k--", lw=0.8)
        ax[0].set_xlabel("2B konum hatası ort (m)")
        ax[0].set_ylabel("MuJoCo konum hatası ort (m)")
        ax[0].set_title("Aynı koşul / koridor / tohum", fontsize=9)
        x = [r["b2_varis"] for r in K if _sayi(r["b2_varis"]) and _sayi(r["mj_varis"])]
        y = [r["mj_varis"] for r in K if _sayi(r["b2_varis"]) and _sayi(r["mj_varis"])]
        ax[1].loglog([max(v, 1e-3) for v in x], [max(v, 1e-3) for v in y], "o", ms=4, alpha=0.7, color="#c0392b")
        ax[1].plot([1e-3, 30], [1e-3, 30], "k--", lw=0.8)
        ax[1].axhline(0.3, color="0.5", lw=0.7, ls=":")
        ax[1].axvline(0.3, color="0.5", lw=0.7, ls=":")
        ax[1].set_xlabel("2B varış hatası (m)")
        ax[1].set_ylabel("MuJoCo varış hatası (m)")
        ax[1].set_title("Varış hatası (noktalı: başarı payı 0,3 m)", fontsize=9)
        fig.tight_layout()
        fig.savefig(os.path.join(ortak.GORSEL, "mujoco_2b.png"), dpi=90)
        plt.close(fig)


def main():
    ab = oku(os.path.join(ortak.HAM, "2b", "ab", "*.json"))
    ky = oku(os.path.join(ortak.HAM, "2b", "kayip", "*.json"))
    mj = oku(os.path.join(ortak.HAM, "mujoco", "*.json"))
    V = oku(os.path.join(ortak.HAM, "varyant", "*.json"))
    os.makedirs(ortak.SONUC, exist_ok=True)
    csv_yaz(os.path.join(ortak.SONUC, "ab_2b.csv"), ab, ALANLAR_AB)
    csv_yaz(os.path.join(ortak.SONUC, "kayip_2b.csv"), ky, ALANLAR_KAYIP)
    mj_alan = ["id", "kosul", "etken", "kademe", "deger", "koridor", "tohum", "hedef", "basari", "neden", "sure_s",
               "yol_m", "rota_m", "varis_hatasi_m", "konum_ort_m", "konum_p95_m", "konum_maks_m",
               "konum_kesin_yanlis", "temas_olay", "temas_hareketli", "temas_duran", "bekleme_s", "bitis", "nan_orani",
               "kayma_olay", "rtf", "duvar_s"]
    csv_yaz(os.path.join(ortak.SONUC, "mujoco.csv"), mj, mj_alan)
    oz_ab, oz_ky = ozetle(ab), ozetle(ky, kayip=True)
    kab, kky = kirilma(oz_ab), kirilma(oz_ky)
    K = mujoco_karsilastir(mj, ab)
    sira = siralama(kab, kky)
    ozet = dict(ab=oz_ab, kayip=oz_ky, kirilma_ab=kab, kirilma_kayip=kky, siralama=sira, mujoco_2b=K,
                sayilar=dict(ab=len(ab), kayip=len(ky), mujoco=len(mj)))
    with open(os.path.join(ortak.SONUC, "ozet.json"), "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=1, default=str)
    md = ["# Tablolar (analiz.py üretir)", "",
          "Koşu sayısı: A'dan B'ye 2B %d, kayıp 2B %d, MuJoCo %d." % (len(ab), len(ky), len(mj)), "",
          "## A'dan B'ye (2B)", "", tablo_ab(oz_ab), "", "## Kayıp robot (2B)", "", tablo_kayip(oz_ky), "",
          "## Kırılma noktaları", "", tablo_kirilma(kab, kky), "", "## Zarar sırası", "",
          "| Sıra | Etken | A'dan B'ye ort başarı | en kötü kademe | Kayıp ort başarı | en kötü kademe |",
          "| --- | --- | --- | --- | --- | --- |"]
    for i, r in enumerate(sira, 1):
        md.append("| %d | %s | %s | %s | %s | %s |" % (i, ETIKET.get(r[0], r[0]), _f(r[1], yuzde=True),
                                                    _f(r[2], yuzde=True), _f(r[3], yuzde=True), _f(r[4], yuzde=True)))
    md += ["", "## MuJoCo doğrulaması ile 2B (aynı koşul / koridor / tohum)", "", tablo_mujoco(K), ""]
    if V:
        csv_yaz(os.path.join(ortak.SONUC, "varyant_2b.csv"), V, ["varyant"] + ALANLAR_AB)
        md += ["## İsteğe bağlı varyant (AYRI tohumlar 3, 4; A'dan B'ye, 2B)", "", tablo_varyant(V), ""]
    with open(os.path.join(ortak.SONUC, "tablolar.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    try:
        gorseller(oz_ab, oz_ky, K)
    except ImportError:
        print("matplotlib yok: görsel atlandı")
    print("ab %d, kayip %d, mujoco %d" % (len(ab), len(ky), len(mj)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
