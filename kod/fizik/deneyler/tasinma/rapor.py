"""Ham sonuçlardan CSV, tablolar ve görseller.

    py -3 rapor.py      # -> sonuc/tasinma_2b.csv, sonuc/mujoco.csv, sonuc/tablolar.md, sonuc/ozet.json, gorsel/*.png
"""

import csv
import glob
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kacirma as KC  # noqa: E402

ALANLAR = ["id", "kume", "senaryo", "surum", "kosul", "koridor", "tohum", "basari", "vardi", "bitis", "sure_s",
           "rota_m", "tasima_t_s", "tasima_uzaklik_m", "kalan_rota_m", "tepki_s", "suphe_s", "bulma_s",
           "yanlis_emin_s", "yanlis_emin_yol_m", "yanlis_surus_s", "temas_sonra", "temas_olay", "kayboldum",
           "kurtarma", "yardim", "son10_yol_m", "son_hata_m", "son_koridor_gercek", "son_harita_inanilan", "neden",
           "duvar_s"]
TUR_AD = {"ayni_uzak": "aynı koridor, uzak", "ters180": "180° çevrilmiş", "kucuk": "küçük kaydırma (1-3 m)",
          "baska_koridor": "başka koridor"}


def oku(alt, kume=None):
    out = []
    for y in sorted(glob.glob(os.path.join(KC.HAM, alt, kume or "*", "*.json"))):
        with open(y, encoding="utf-8") as f:
            d = json.load(f)
        ts = d.get("tasima") or {}
        d["tasima_t_s"] = ts.get("t")
        d["tasima_uzaklik_m"] = ts.get("uzaklik")
        d["kalan_rota_m"] = ts.get("kalan_rota_m")
        out.append(d)
    return out


def csv_yaz(yol, R):
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
        w.writeheader()
        for r in R:
            w.writerow(r)


def _med(v):
    v = [x for x in v if x is not None]
    return round(st.median(v), 1) if v else None


def _mx(v):
    v = [x for x in v if x is not None]
    return round(max(v), 1) if v else None


def _ykk(r):
    """Yanlış koridora kesin sürüş (s): seri (0,5 s) örneklerinde inanılan harita gerçek değil (hata yok), emin, beyin
    yardım beklemiyor ve hareket komutu var."""
    n = sum(1 for s in r.get("seri") or [] if s[2] and s[1] is None and (len(s) < 12 or s[11] != "yardim")
            and (abs(s[4]) > 0.02 or abs(s[5]) > 0.05))
    return 0.5 * n


def ozet_tasima(R):
    n = len(R)
    tep = [r["tepki_s"] for r in R if r.get("tepki_s") is not None]
    bul = [r["bulma_s"] for r in R if r.get("bulma_s") is not None]
    return dict(n=n, basari=sum(1 for r in R if r.get("basari")),
                tepki=len(tep), tepki_med=_med(tep), tepki_maks=_mx(tep),
                suphe=sum(1 for r in R if r.get("suphe_s") is not None),
                suphe_med=_med([r.get("suphe_s") for r in R]),
                bulma=len(bul), bulma_med=_med(bul), bulma_maks=_mx(bul),
                yanlis_emin_med=_med([r.get("yanlis_emin_s") for r in R]),
                yanlis_emin_maks=_mx([r.get("yanlis_emin_s") for r in R]),
                yanlis_surus_med=_med([r.get("yanlis_surus_s") for r in R]),
                yanlis_surus_maks=_mx([r.get("yanlis_surus_s") for r in R]),
                temas=sum(r.get("temas_sonra") or 0 for r in R),
                temas_kosu=sum(1 for r in R if r.get("temas_sonra")),
                beyin_bitti_yanlis=sum(1 for r in R if r.get("bitis") == "beyin bitti" and not r.get("vardi")),
                ykk_kosu=sum(1 for r in R if _ykk(r) > 0), ykk_s=round(sum(_ykk(r) for r in R), 1),
                istisna=sum(1 for r in R if "istisna" in str(r.get("neden", ""))))


def ozet_ya(R, V3):
    """R: bir sürümün yanlış alarm koşuları; V3: aynı görevlerin v3 sonuçları (eşli süre farkı)."""
    v3 = {(r["senaryo"], r["kosul"], r["koridor"], r["tohum"]): r for r in V3}
    fark = []
    for r in R:
        b = v3.get((r["senaryo"], r["kosul"], r["koridor"], r["tohum"]))
        if b and r.get("vardi") and b.get("vardi"):
            fark.append(r["sure_s"] - b["sure_s"])
    return dict(n=len(R), basari=sum(1 for r in R if r.get("basari")),
                kayboldum_kosu=sum(1 for r in R if r.get("kayboldum")),
                kayboldum=sum(r.get("kayboldum") or 0 for r in R),
                tepki_kosu=sum(1 for r in R if r.get("tepki_s") is not None),
                suphe_kosu=sum(1 for r in R if r.get("suphe_s") is not None),
                temas=sum(r.get("temas_sonra") or 0 for r in R),
                ykk_kosu=sum(1 for r in R if _ykk(r) > 0), ykk_s=round(sum(_ykk(r) for r in R), 1),
                sure_farki_med=(round(st.median(fark), 1) if fark else None),
                sure_farki_maks=(round(max(fark), 1) if fark else None), eslesen=len(fark))


def tablolar(R, baslik):
    satir = ["## " + baslik, ""]
    satir.append("Taşıma (koşul başına n koşu). tepki = beynin davranış değiştirdiği ilk an (algi: \"kayboldum\"; v3 cok: "
                 "yeniden plan / keşfe dönüş; v3 ab: tepki düzeneği yok); şüphe = konumlayıcının ilk `konum_kararsiz`'ı; "
                 "bulma = taşımadan sonra poz hatası < 0,5 m ve yön < 30° olup sonuna dek öyle kalan dilimin başı. "
                 "Süreler taşımadan sonra s (medyan / en çok).")
    satir.append("")
    satir.append("| senaryo | tür | sürüm | başarı | tepki (med / maks s) | şüphe | bulma (med / maks s) | "
                 "yanlış poza emin s (med / maks) | yanlış poza göre sürüş s (med / maks) | temas (koşu) | "
                 "yanlış yerde \"vardım\" | yanlış koridora kesin sürüş: koşu (toplam s) |")
    satir.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    oz = {}
    for sn in KC.SENARYOLAR:
        for tur in KC.TURLER:
            for sr in KC.SURUMLER:
                S = [r for r in R if r["senaryo"] == sn and r["kosul"] == tur and r["surum"] == sr]
                if not S:
                    continue
                o = ozet_tasima(S)
                oz["%s|%s|%s" % (sn, tur, sr)] = o
                bas = "%d/%d" % (o["basari"], o["n"])
                if sn == "ab" and tur == "baska_koridor":
                    bas += " (güvenli durdu)"
                satir.append("| %s | %s | %s | %s | %d/%d (%s / %s) | %d/%d (%s) | %d/%d (%s / %s) | %s / %s | %s / %s | "
                             "%d (%d) | %d | %d (%s) |" % (
                                 sn, TUR_AD[tur], sr, bas, o["tepki"], o["n"], o["tepki_med"], o["tepki_maks"],
                                 o["suphe"], o["n"], o["suphe_med"], o["bulma"], o["n"], o["bulma_med"],
                                 o["bulma_maks"], o["yanlis_emin_med"], o["yanlis_emin_maks"],
                                 o["yanlis_surus_med"], o["yanlis_surus_maks"], o["temas"], o["temas_kosu"],
                                 o["beyin_bitti_yanlis"], o["ykk_kosu"], o["ykk_s"]))
    satir += ["", "Yanlış alarm (taşıma yok). kayboldum = algi'nin boşuna \"kayboldum\" demesi; tepki (v3 cok) = "
              "boşuna yeniden plan / keşfe dönüş; süre farkı = algi - v3 (ikisi de vardıysa, eşli, s).", "",
              "| senaryo | koşul | sürüm | başarı | kayboldum koşu (toplam) | tepki koşu | şüphe koşu | temas | "
              "yanlış koridora kesin sürüş: koşu (s) | süre farkı med / maks s |", "|---|---|---|---|---|---|---|---|---|---|"]
    for sn in KC.SENARYOLAR:
        for y in KC.YA_KOSULLARI:
            k = "ya_" + y
            V3 = [r for r in R if r["senaryo"] == sn and r["kosul"] == k and r["surum"] == "v3"]
            for sr in KC.SURUMLER:
                S = [r for r in R if r["senaryo"] == sn and r["kosul"] == k and r["surum"] == sr]
                if not S:
                    continue
                o = ozet_ya(S, V3)
                oz["%s|%s|%s" % (sn, k, sr)] = o
                satir.append("| %s | %s | %s | %d/%d | %d (%d) | %d | %d | %d | %d (%s) | %s / %s |" % (
                    sn, y, sr, o["basari"], o["n"], o["kayboldum_kosu"], o["kayboldum"], o["tepki_kosu"],
                    o["suphe_kosu"], o["temas"], o["ykk_kosu"], o["ykk_s"], o["sure_farki_med"] if sr != "v3" else "-",
                    o["sure_farki_maks"] if sr != "v3" else "-"))
    return satir, oz


def ciz(R, yol):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    fig, eks = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for ax, sn in zip(eks, KC.SENARYOLAR):
        x = list(range(len(KC.TURLER)))
        for j, (sr, renk) in enumerate((("v3", "#9aa0a6"), ("algi", "#1a73e8"))):
            y = []
            for tur in KC.TURLER:
                S = [r for r in R if r["senaryo"] == sn and r["kosul"] == tur and r["surum"] == sr]
                y.append(100.0 * sum(1 for r in S if r.get("basari")) / max(len(S), 1))
            ax.bar([v + (j - 0.5) * 0.38 for v in x], y, 0.36, color=renk, label=sr)
        ax.set_xticks(x)
        ax.set_xticklabels(["aynı/uzak", "180°", "küçük", "başka kor."], fontsize=9)
        ax.set_title({"ab": "A'dan B'ye (tek harita)", "cok": "6 harita, bilinen başlangıç"}[sn], fontsize=10)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=0.3)
    eks[0].set_ylabel("başarı % (sınama, 12 koşu)")
    eks[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Taşınma: hedefe varış (ab / başka koridor: güvenli durma)", fontsize=10)
    fig.tight_layout()
    fig.savefig(yol, dpi=110)
    plt.close(fig)
    return True


def ciz_ornek(R, yol, anahtar=("ab", "kucuk", "koridor_5", 2)):
    """Bir görevde v3 ve algi: taşımadan sonra poz hatası ve hız komutu (zaman çizgisi)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    sn, tur, kor, t = anahtar
    S = {r["surum"]: r for r in R if (r["senaryo"], r["kosul"], r["koridor"], r["tohum"]) == anahtar}
    if len(S) < 2:
        return False
    fig, eks = plt.subplots(2, 1, figsize=(9, 4.6), sharex=True)
    for sr, renk in (("v3", "#9aa0a6"), ("algi", "#1a73e8")):
        r = S[sr]
        tk = (r.get("tasima") or {}).get("t", 0.0)
        x = [s[0] - tk for s in r["seri"]]
        e = [min(s[1], 10.0) if s[1] is not None else 10.0 for s in r["seri"]]
        v = [s[4] for s in r["seri"]]
        eks[0].plot(x, e, color=renk, label=sr, lw=1.6)
        eks[1].plot(x, v, color=renk, label=sr, lw=1.6)
        for o in r.get("olaylar") or []:
            if o[1] == "kayboldum":
                eks[0].axvline(o[0] - tk, color=renk, ls="--", lw=0.8)
    eks[0].axhline(KC.HATA_ESIK, color="#d93025", lw=0.6)
    eks[0].set_ylabel("poz hatası m\n(yön > 30°: 9,99)")
    eks[1].set_ylabel("v komutu m/s")
    eks[1].set_xlabel("taşımadan sonra s")
    eks[0].legend(frameon=False, fontsize=9)
    eks[0].set_title("%s, %s, %s tohum %d (kesik çizgi: \"kayboldum\")" % (sn, TUR_AD[tur], kor, t), fontsize=10)
    for ax in eks:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(yol, dpi=110)
    plt.close(fig)
    return True


def main():
    R = oku("2b")
    for r in R:
        r.setdefault("neden", "")
    csv_yaz(os.path.join(KC.SONUC, "tasinma_2b.csv"), R)
    M = oku("mujoco")
    csv_yaz(os.path.join(KC.SONUC, "mujoco.csv"), M)
    md = ["# Taşınma deneyi: tablolar (rapor.py üretir)", ""]
    oz = {}
    for kume in ("sinama", "gelistirme"):
        S = [r for r in R if r["kume"] == kume]
        if S:
            s, o = tablolar(S, {"sinama": "Sınama kümesi (hüküm): tohum 1, 2 x 6 koridor",
                                "gelistirme": "Geliştirme kümesi (eşik ayarı): tohum 901-903 x koridor_2, 3, 5"}[kume])
            md += s + [""]
            oz[kume] = o
    S = [r for r in R if r["kume"] == "sinama" and r["koridor"] in KC.SINAMA_DISI_HARITA]
    if S:
        s, o = tablolar(S, "Sınama, yalnız geliştirmede hiç kullanılmamış haritalar (koridor_1, 4, 6; 6 koşu / koşul)")
        md += s + [""]
        oz["sinama_yeni_harita"] = o
    if M:
        s, o = tablolar(M, "MuJoCo doğrulaması (A'dan B'ye, taban dünya)")
        md += s + [""]
        oz["mujoco"] = o
        # 2B ile aynı görev
        es = []
        R2 = {(r["senaryo"], r["surum"], r["kosul"], r["koridor"], r["tohum"]): r for r in R if r["kume"] == "sinama"}
        for m in M:
            b = R2.get((m["senaryo"], m["surum"], m["kosul"], m["koridor"], m["tohum"]))
            if b is not None:
                es.append((m["id"], bool(m.get("basari")), bool(b.get("basari"))))
        md += ["MuJoCo ile 2B aynı görev (aynı tohum, koridor, taşıma tohumu): %d / %d aynı sonuç." % (
            sum(1 for _, a, b in es if a == b), len(es)), ""]
        md += ["| görev | MuJoCo | 2B |", "|---|---|---|"] + ["| %s | %s | %s |" % e for e in es] + [""]
        oz["mujoco_2b_ayni"] = [sum(1 for _, a, b in es if a == b), len(es)]
    g = os.path.join(KC.SONUC, "gerileme.json")
    if os.path.exists(g):
        with open(g, encoding="utf-8") as f:
            oz["gerileme"] = json.load(f)["ozet"]
    with open(os.path.join(KC.SONUC, "tablolar.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(KC.SONUC, "ozet.json"), "w", encoding="utf-8") as f:
        json.dump(oz, f, ensure_ascii=False, indent=1)
    os.makedirs(KC.GORSEL, exist_ok=True)
    S = [r for r in R if r["kume"] == "sinama"]
    if S:
        ciz(S, os.path.join(KC.GORSEL, "basari_tur.png"))
        ciz_ornek(S, os.path.join(KC.GORSEL, "ornek_kucuk_koridor_5.png"))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
