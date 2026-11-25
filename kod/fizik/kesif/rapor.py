"""sonuc/*.csv -> sonuc/SONUC.md (özet tablolar + başarısızlık listesi). Sayılar CSV'den, elle düzeltme yok."""

import csv
import glob
import os
import statistics as st
from collections import defaultdict

from ._yol import KESIF

SONUC = os.path.join(KESIF, "sonuc")


def _oku():
    S = []
    for yol in sorted(glob.glob(os.path.join(SONUC, "*.csv"))):
        if os.path.basename(yol).startswith("mujoco"):
            continue
        with open(yol, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                r["_dosya"] = os.path.basename(yol)
                S.append(r)
    return S


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _ort(xs, fmt="%.1f"):
    xs = [x for x in xs if x is not None]
    return fmt % st.mean(xs) if xs else "-"


def _boy(ad):
    try:
        return ad.split("_")[1]
    except IndexError:
        return ad


def ozet_tablo(S, anahtar):
    G = defaultdict(list)
    for r in S:
        G[anahtar(r)].append(r)
    satirlar = ["| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | "
                "poz hata maks ort (m) | doğru duvar ort |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in sorted(G, key=str):
        R = G[k]
        b = [r for r in R if r.get("durum") == "basari"]
        sb = [_f(r["sure_s"]) for r in b]
        satirlar.append("| %s | %d | %d/%d | %s | %s | %s | %s | %s | %s | %s |" % (
            " ".join(map(str, k)) if isinstance(k, tuple) else k, len(R), len(b), len(R), _ort(sb),
            "%.0f" % max(sb) if sb else "-", _ort([_f(r.get("yol_m")) for r in R]),
            _ort([_f(r.get("carpma_sayisi")) for r in R], "%.2f"), _ort([_f(r.get("puan")) for r in R], "%.0f"),
            _ort([_f(r.get("poz_hata_maks_m")) for r in R], "%.2f"),
            _ort([_f(r.get("dogru_duvar_orani")) for r in R], "%.2f")))
    return "\n".join(satirlar)


def rapor_yaz():
    S = _oku()
    if not S:
        return "CSV yok"
    md = ["# Keşif beyni: ölçüm sonuçları", "",
          "Bu dosya `py -3 -m kesif.kos rapor` ile CSV'lerden üretilir; elle düzeltilmez. Benzetici: `benzet2b.py` "
          "(2B, dönen tarama çarpıklığı açık, %14 dönüş fazlası + gürültü varsayılan). Hakem: `labirent.hakem`.", ""]
    ilk = [r for r in S if r.get("deney") == "ilk"]
    if ilk:
        md += ["## İlk tur: strateji x labirent boyu (5 tohum, %14 dönüş hatası)", "",
               ozet_tablo(ilk, lambda r: (r["strateji"], _boy(r["sahne"]))), "",
               "### Labirent bazında (kesif)", "",
               ozet_tablo([r for r in ilk if r["strateji"] == "kesif"], lambda r: r["sahne"]), ""]
        k = [r for r in ilk if r["strateji"] == "kesif"]
        tm = [_f(r.get("tarama_ms_ort")) for r in k]
        tp = [_f(r.get("tarama_ms_p95")) for r in k]
        tx = [_f(r.get("tarama_ms_maks")) for r in k]
        pm = [_f(r.get("plan_ms_ort")) for r in k]
        px = [_f(r.get("plan_ms_maks")) for r in k]
        md += ["### Adım süresi (kesif, bu makinede, tek iş parçacığı, düşük öncelik)", "",
               "- tarama işleme (SLAM + gerekiyorsa plan) ort %s ms, p95 ort %s ms, en kötü %s ms" %
               (_ort(tm, "%.1f"), _ort(tp, "%.1f"), "%.0f" % max(x for x in tx if x is not None) if any(tx) else "-"),
               "- planlama ort %s ms, en kötü %s ms" % (_ort(pm, "%.1f"),
                                                         "%.0f" % max(x for x in px if x is not None) if any(px) else "-"),
               ""]
    # başvuru: labirent alanındaki çözüm uzunluğu ve ideal duvar izleme (yalnız rapor için; beyin bunları görmez)
    import json
    from ._yol import SAHNELER
    md += ["### Başvuru (sahne JSON'undan; beyin görmez): alt sınırlar, 0,25 m/s, dönüşsüz", "",
           "| sahne | çözüm (m) | çözüm süresi (s) | sağ el hücre | ideal sağ el (s) | sol el hücre |",
           "| --- | --- | --- | --- | --- | --- |"]
    for ad in sorted({r["sahne"] for r in ilk}, key=lambda a: (int(_boy(a).split("x")[0]), a)):
        try:
            with open(os.path.join(SAHNELER, ad + ".json"), encoding="utf-8") as f:
                L = json.load(f)["labirent"]
            dt = L.get("duvar_takip", {})
            h = L.get("hucre_m", 1.3)
            md.append("| %s | %.1f | %.0f | %s | %.0f | %s |" % (ad, L["cozum_uzunlugu_m"], L["cozum_uzunlugu_m"] / 0.25,
                                                             dt.get("sag_el_hucre"), dt.get("sag_el_hucre", 0) * h / 0.25,
                                                             dt.get("sol_el_hucre")))
        except (OSError, KeyError, ValueError):
            pass
    md.append("")
    od = [r for r in S if r.get("strateji") == "kesif" and r.get("deney") in ("ilk", "odometri")]
    if any(r.get("deney") == "odometri" for r in od):
        md += ["## Odometri duyarlılığı (kesif; dönüş fazlası 0 / %14 / %25)", "",
               ozet_tablo(od, lambda r: ("%.2f" % _f(r["donus_hata"]), _boy(r["sahne"]))), ""]
    hz = [r for r in S if r.get("deney") == "hafiza"]
    if hz:
        md += ["## Hafızalı koşu (aynı labirent, ilk koşunun haritası ve çıkış pozu)", "",
               "| sahne | n (ilk başarılı) | ilk süre ort | hafızalı süre ort | hafızalı başarı | kazanç |",
               "| --- | --- | --- | --- | --- | --- |"]
        G = defaultdict(list)
        for r in hz:
            G[r["sahne"]].append(r)
        for s in sorted(G):
            R = [r for r in G[s] if r.get("durum") == "basari"]
            a = [_f(r["sure_s"]) for r in R]
            b = [_f(r.get("hafiza_sure_s")) for r in R if r.get("hafiza_durum") == "basari"]
            kaz = "%.0f%%" % (100 * (1 - st.mean(b) / st.mean(a))) if a and b else "-"
            md.append("| %s | %d/%d | %s | %s | %d/%d | %s |" % (s, len(R), len(G[s]), _ort(a), _ort(b), len(b),
                                                                len(R), kaz))
        md.append("")
    ay = [r for r in S if r.get("deney", "").startswith("ayar")]
    if ay:
        once = [r for r in ilk if r["strateji"] == "kesif"]
        po = [_f(r.get("puan")) or 0.0 for r in once]
        ps = [_f(r.get("puan")) or 0.0 for r in ay]
        md += ["## Ayar: sınama kümesinde sonra (önce = ilk turun kesif satırları; arama eğitim labirentlerinde)", "",
               "- önce: başarı %d/%d, puan ort %.1f; sonra: başarı %d/%d, puan ort %.1f" % (
                   sum(r["durum"] == "basari" for r in once), len(once), st.mean(po) if po else 0,
                   sum(r["durum"] == "basari" for r in ay), len(ay), st.mean(ps) if ps else 0), "",
               ozet_tablo(ay, lambda r: (r.get("ayar") or "-", _boy(r["sahne"]))), ""]
    mj_yol = os.path.join(SONUC, "mujoco.csv")
    if os.path.exists(mj_yol):
        with open(mj_yol, encoding="utf-8") as f:
            M = list(csv.DictReader(f))
        for r in M:
            if not r.get("durum") and (_f(r.get("sure_s")) or 0) >= 899.8:
                r["durum"] = "fail_sure"
        iki = {(r["sahne"], r["tohum"]): r for r in ilk if r["strateji"] == "kesif"}
        md += ["## MuJoCo (gezinme.duzenek) ile 2B benzetici: aynı labirent ve tohum (kesif)", "",
               "MuJoCo'da tohum LiDAR gürültüsünü değiştirir; odometri hatası düzeneğin fiziğinden gelir (beynin "
               "öğrendiği dönüş ölçeği k_don ort %s). Beyin ön bilgisiz kurulur (`KesifBeyni()`)." % _ort(
                   [_f(r.get("k_don")) for r in M], "%.3f"), "",
               "| sahne | tohum | MuJoCo durum | süre | çarpma | poz hata maks | doğru duvar | 2B durum | 2B süre | "
               "2B poz hata maks | 2B doğru duvar |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in sorted(M, key=lambda r: (r["sahne"], r["tohum"])):
            b2 = iki.get((r["sahne"], r["tohum"]), {})
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["sahne"], r["tohum"], r.get("durum"), r.get("sure_s"), r.get("carpma_sayisi"),
                r.get("poz_hata_maks_m"), r.get("dogru_duvar_orani"), b2.get("durum", "-"), b2.get("sure_s", "-"),
                b2.get("poz_hata_maks_m", "-"), b2.get("dogru_duvar_orani", "-")))
        md += ["", ozet_tablo(M, lambda r: ("mujoco", _boy(r["sahne"]))), ""]
        tm = [_f(r.get("tarama_ms_ort")) for r in M]
        md += ["MuJoCo tarama işleme ort %s ms; gerçek zaman oranı ort %s (aynı anda %s)." % (
            _ort(tm), _ort([_f(r.get("rtf")) for r in M], "%.1f"), "3 MuJoCo + 2 benzetici süreci"), ""]
    fail = [r for r in S if r.get("durum") != "basari"]
    md += ["## Başarısızlıklar (%d)" % len(fail), "",
           "| dosya | strateji | sahne | tohum | odo | durum | süre | sebep / son mod | son olaylar |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in fail:
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s | %s |" % (
            r["_dosya"], r.get("strateji"), r.get("sahne"), r.get("tohum"), r.get("donus_hata"), r.get("durum"),
            r.get("sure_s"), r.get("sikisma_sebebi") or "-", r.get("son_mod") or "-",
            (r.get("olaylar") or "").replace("|", "/")[:160]))
    yol = os.path.join(SONUC, "SONUC.md")
    with open(yol, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    return yol


if __name__ == "__main__":
    print(rapor_yaz())
