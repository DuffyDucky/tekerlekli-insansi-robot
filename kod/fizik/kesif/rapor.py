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
        # deneme* / kahin*: hafızalı deneme zinciri ve kural dışı tavan; ilk giriş tablolarına karışmaz
        if os.path.basename(yol).startswith(("mujoco", "tani", "deneme", "kahin", "hiz_tani")):
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


def _csv(ad):
    yol = os.path.join(SONUC, ad)
    if not os.path.exists(yol):
        return []
    with open(yol, encoding="utf-8") as f:
        M = list(csv.DictReader(f))
    for r in M:
        if not r.get("durum") and (_f(r.get("sure_s")) or 0) >= 899.8:
            r["durum"] = "fail_sure"
    return M


def surum_tablo(gruplar):
    """gruplar: [(etiket, satırlar)] -> boyuta göre v1 / v2 tablosu."""
    md = ["| sürüm | küme | boy | n | başarı | ortanca süre (s, başarılı) | çarpma (toplam) | puan ort | "
          "en büyük poz hatası (m) | poz hatası maks ort (m) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for (surum, kume), R in gruplar:
        G = defaultdict(list)
        for r in R:
            G[_boy(r["sahne"])].append(r)
        for b in sorted(G, key=lambda x: int(x.split("x")[0])) + ["toplam"]:
            X = R if b == "toplam" else G[b]
            ok = [_f(r["sure_s"]) for r in X if r.get("durum") == "basari"]
            pz = [_f(r.get("poz_hata_maks_m")) for r in X if _f(r.get("poz_hata_maks_m")) is not None]
            md.append("| %s | %s | %s | %d | %d/%d | %s | %d | %s | %s | %s |" % (
                surum, kume, b, len(X), len(ok), len(X), "%.0f" % st.median(ok) if ok else "-",
                sum(int(_f(r.get("carpma_sayisi")) or 0) for r in X), _ort([_f(r.get("puan")) for r in X], "%.0f"),
                "%.2f" % max(pz) if pz else "-", _ort(pz, "%.2f")))
    return "\n".join(md)


def surum_bolumu(ilk2b, v2_2b):
    """v1 / v2 karşılaştırması: MuJoCo geliştirme (11 labirent x 3 tohum) ve sınama (10 yeni labirent x 2 tohum)."""
    d1 = [r for r in _csv("mujoco.csv")]
    d2 = [r for r in _csv("mujoco_v2.csv") if r.get("kos", "ilk") == "ilk"]
    s1 = [r for r in _csv("mujoco_sinama_v1.csv") if r.get("kos", "ilk") == "ilk"]
    s2a = _csv("mujoco_sinama_v2.csv")
    s2 = [r for r in s2a if r.get("kos", "ilk") == "ilk"]
    if not (d2 or s1 or s2):
        return []
    md = ["## v1 / v2 (MuJoCo)", "",
          "v1 = ilk teslim (commit 461216f davranışı, `surum_ayari(\"v1\")`), v2 = `surum_ayari(\"v2\")`. Geliştirme "
          "kümesi: 11 labirent x tohum {0, 1, 2}; sınama kümesi: `labirent_13x13_t4..t8`, `labirent_17x17_t4..t8` x "
          "tohum {0, 1} (geliştirme boyunca bakılmadı). Karar kuralı: v2 sınama başarısı v1'den az değilse ve çarpma "
          "artmadıysa varsayılan olur.", "",
          surum_tablo([(("v1", "gelistirme"), d1), (("v2", "gelistirme"), d2), (("v1", "sinama"), s1),
                       (("v2", "sinama"), s2)]), ""]
    if s1 and s2:
        b1 = sum(r.get("durum") == "basari" for r in s1)
        b2 = sum(r.get("durum") == "basari" for r in s2)
        c1 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in s1)
        c2 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in s2)
        md += ["Sınama kararı: v1 başarı %d/%d, çarpma %d; v2 başarı %d/%d, çarpma %d -> varsayılan **%s**." % (
            b1, len(s1), c1, b2, len(s2), c2, "v2" if (b2 >= b1 and c2 <= c1) else "v1"), ""]
        es = {(r["sahne"], r["tohum"]): r for r in s1}
        md += ["| sınama sahnesi | tohum | v1 durum | v1 süre | v2 durum | v2 süre |", "| --- | --- | --- | --- | --- | --- |"]
        for r in sorted(s2, key=lambda r: (r["sahne"], r["tohum"])):
            a = es.get((r["sahne"], r["tohum"]), {})
            md.append("| %s | %s | %s | %s | %s | %s |" % (r["sahne"], r["tohum"], a.get("durum", "-"),
                                                          a.get("sure_s", "-"), r.get("durum"), r.get("sure_s")))
        md.append("")
    hz = [r for r in s2a if r.get("kos") == "hafiza"]
    if hz:
        ilk = {(r["sahne"], r["tohum"]): r for r in s2}
        md += ["### Hafızalı ek tur (v2, sınama kümesi, ilk koşu başarılıysa aynı tohum)", "",
               "| sahne | tohum | ilk süre | hafızalı durum | hafızalı süre | kazanç | çarpma |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
        for r in sorted(hz, key=lambda r: (r["sahne"], r["tohum"])):
            a = _f(ilk.get((r["sahne"], r["tohum"]), {}).get("sure_s"))
            b = _f(r.get("sure_s"))
            md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["sahne"], r["tohum"], a, r.get("durum"), b,
                "%.0f%%" % (100 * (1 - b / a)) if a and b and r.get("durum") == "basari" else "-", r.get("carpma_sayisi")))
        md.append("")
    if v2_2b:
        ciftler = {(r["sahne"], str(r["tohum"])) for r in v2_2b}
        k1 = [r for r in ilk2b if r.get("strateji") == "kesif" and (r["sahne"], str(r["tohum"])) in ciftler]
        md += ["### 2B benzetici: v1 (ilk.csv) / v2 (v2_2b.csv), aynı labirent ve tohumlar", "",
               ozet_tablo(k1, lambda r: ("v1", _boy(r["sahne"]))), "", ozet_tablo(v2_2b, lambda r: ("v2", _boy(r["sahne"]))),
               ""]
    T = []
    for ad, et in (("tani_v1.csv", "v1"), ("tani_v2.csv", "v2")):
        T += [dict(r, surum=et) for r in _csv(ad)]
    if T:
        md += ["### Zaman dökümü (`kesif.tani`, MuJoCo geliştirme kayıtları; kesişen kalemler: tekrar, çıkmaz)", "",
               "| sürüm | sahne | tohum | durum | süre | düz | dönüş | bekle | kurtarma | tekrar | çözüm dışı | "
               "yol / çözüm | çıkmaz kol girilen / uzaktan görülmüş | düz hız ort | poz hata %50 / son |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in sorted(T, key=lambda r: (r["surum"], r["sahne"], r["tohum"])):
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s / %s |" % (
                r["surum"], r["sahne"], r["tohum"], r.get("durum"), r["sure_s"], r["duz_s"], r["donus_s"],
                r["bekle_s"], r["kurtarma_s"], r["tekrar_s"], r["cikmaz_s"], r["yol_orani"], r["cikmaz_gir"],
                r["cikmaz_gorulmus"], r["v_duz_ort"], r["poz_h_50"], r["poz_h_son"]))
        for et in ("v1", "v2"):
            X = [r for r in T if r["surum"] == et]
            if X:
                top = sum(_f(r["sure_s"]) for r in X)
                md.append("\n%s toplam süre payı: düz %.0f%%, dönüş %.0f%%, bekle %.0f%%, kurtarma %.0f%%; tekrar %.0f%%, "
                          "çözüm dışı %.0f%%; düz hız ort %.3f m/s." % (
                              et, *(100 * sum(_f(r[k]) for r in X) / top for k in
                                    ("duz_s", "donus_s", "bekle_s", "kurtarma_s", "tekrar_s", "cikmaz_s")),
                              st.mean(_f(r["v_duz_ort"]) for r in X)))
        md.append("")
    return md


def uzatilmis_bolumu():
    """Kural DIŞI 1800 s koşular (sonuc/mujoco_uzatilmis_v2.csv): süre olsaydı çözer miydi. 15 dk tablolarına girmez."""
    M = _csv("mujoco_uzatilmis_v2.csv")
    if not M:
        return []
    import json
    from ._yol import SAHNELER
    T = {(r["sahne"], r["tohum"]): r for r in _csv("tani_uzatilmis_v2.csv")}
    md = ["## Uzatılmış süre (KURAL DIŞI: hakem süre sınırı 1800 s; v2, MuJoCo, tohum 0)", "",
          "Soru: 15 dk sınırı olmasaydı çözer miydi, ne kadar sürerdi. Bu satırlar yukarıdaki 15 dakikalık tabloların "
          "hiçbirinde yok. Gereken hız = yürünen yol / 900 s (aynı yolu 900 s'de bitirmek için ortalama hız).", "",
          "| sahne | durum | süre (s) | çözüm (m) | yürünen (m) | yol / çözüm | çarpma | poz hatası maks (m) | "
          "poz hatası %25 / %50 / son (m) | düz hız ort (m/s) | gereken hız (m/s) | gereken / 0,39 |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(M, key=lambda r: (int(_boy(r["sahne"]).split("x")[0]), r["sahne"])):
        try:
            with open(os.path.join(SAHNELER, r["sahne"] + ".json"), encoding="utf-8") as f:
                coz = float(json.load(f)["labirent"]["cozum_uzunlugu_m"])
        except (OSError, KeyError, ValueError):
            coz = None
        y = _f(r.get("yol_m"))
        t = T.get((r["sahne"], r["tohum"]), {})
        g = y / 900.0 if y else None
        md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s / %s | %s | %s | %s |" % (
            r["sahne"], r.get("durum"), r.get("sure_s"), "%.1f" % coz if coz else "-", "%.1f" % y if y else "-",
            "%.2f" % (y / coz) if y and coz else "-", r.get("carpma_sayisi"), r.get("poz_hata_maks_m"),
            t.get("poz_h_25", "-"), t.get("poz_h_50", "-"), t.get("poz_h_son", "-"), t.get("v_duz_ort", "-"),
            "%.3f" % g if g else "-", "%.2f" % (g / 0.39) if g else "-"))
    # hüküm: sınıflar verilerden (yol / çözüm < 1,3 = keşif verimli, > 1,5 = keşif dolaşıyor)
    k17 = [r for r in M if _boy(r["sahne"]) == "17x17"]
    cozulen = [r for r in k17 if r.get("durum") == "basari"]
    dk15 = [r for r in cozulen if (_f(r["sure_s"]) or 0) <= 900]
    coz = {}
    for r in M:
        try:
            with open(os.path.join(SAHNELER, r["sahne"] + ".json"), encoding="utf-8") as f:
                coz[r["sahne"]] = float(json.load(f)["labirent"]["cozum_uzunlugu_m"])
        except (OSError, KeyError, ValueError):
            pass
    oran = lambda r: (_f(r.get("yol_m")) or 0) / coz.get(r["sahne"], 1e9)
    hiz = [r["sahne"][9:] for r in k17 if r not in dk15 and oran(r) < 1.3]
    kesif = [r["sahne"][9:] for r in k17 if r not in dk15 and oran(r) >= 1.5]
    pz = [_f(r.get("poz_hata_maks_m")) for r in k17 if _f(r.get("poz_hata_maks_m")) is not None]
    md += ["**Hüküm** (17x17, tohum 0): 30 dakikada %d/%d çözülüyor (15 dakikada %d). 900 s'yi aşanların %s yürünen "
           "yol / çözüm < 1,3 ile yalnız hızdan aşıyor; %s yol / çözüm >= 1,5 ile keşif dolaşıyor (hakemin 300 s yeni "
           "hücresiz kuralına takılan ya da geç biten). Harita kayması süreyle büyüyor ama kaçmıyor: en büyük poz "
           "hatası %.2f–%.2f m, çarpma toplam %d." % (
               len(cozulen), len(k17), len(dk15), ", ".join(hiz) or "hiçbiri", ", ".join(kesif) or "hiçbiri",
               min(pz) if pz else 0, max(pz) if pz else 0, sum(int(_f(r.get("carpma_sayisi")) or 0) for r in M)), ""]
    return md


def v3_bolumu(S):
    """v2 / v3: geliştirme (eski 33 + 17x17_t4, t5 x tohum {0, 1}), sınama2 (13x13_t9..t13, 17x17_t9..t13 x 2),
    uzatılmış (kural dışı 1800 s)."""
    d3 = [r for r in _csv("mujoco_v3.csv") if r.get("kos", "ilk") == "ilk"]
    if not d3:
        return []
    ek = {(r["sahne"], r["tohum"]) for r in d3}
    d2 = [r for r in _csv("mujoco_v2.csv") if r.get("kos", "ilk") == "ilk"]
    d2 += [r for r in _csv("mujoco_sinama_v2.csv") if r.get("kos", "ilk") == "ilk" and (r["sahne"], r["tohum"]) in ek]
    s2 = [r for r in _csv("mujoco_sinama2_v2.csv") if r.get("kos", "ilk") == "ilk"]
    s3 = [r for r in _csv("mujoco_sinama2_v3.csv") if r.get("kos", "ilk") == "ilk"]
    md = ["## v2 / v3 (MuJoCo): dışa açık sınır önceliği", "",
          "Tanı: `sonuc/tani_dolanma.md`. v3 = v2 + dışa açık sınırın (dönüşsüz ışın oranı >= 0,3) maliyeti 25 m "
          "düşük, yeri hatırlanır. Geliştirme: eski 11 labirent x 3 tohum + görülmüş 17x17_t4, t5 x 2 tohum. "
          "Sınama2: `labirent_13x13_t9..t13`, `labirent_17x17_t9..t13` x tohum {0, 1}.", "",
          surum_tablo([(("v2", "gelistirme"), d2), (("v3", "gelistirme"), d3), (("v2", "sinama2"), s2),
                       (("v3", "sinama2"), s3)]), ""]
    if s2 and s3:
        b2 = sum(r.get("durum") == "basari" for r in s2)
        b3 = sum(r.get("durum") == "basari" for r in s3)
        c2 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in s2)
        c3 = sum(int(_f(r.get("carpma_sayisi")) or 0) for r in s3)
        md += ["Sınama2 kararı: v2 başarı %d/%d, çarpma %d; v3 başarı %d/%d, çarpma %d -> varsayılan **%s**." % (
            b2, len(s2), c2, b3, len(s3), c3, "v3" if (b3 >= b2 and c3 <= c2) else "v2"), ""]
        # SONUC.md'ye elle eklenmiş olan not (rapor yeniden üretilince kaybolmasın)
        md += ["Not: v3 sınama2'de kazanç getirmedi (15/20 = 15/20). Geliştirmedeki kazanç (27 → 30 / 37) düzeltmenin "
               "üzerinde tasarlandığı labirentten, 17x17_t3'ten geliyor; genel iyileşme kanıtı sayılmaz.", ""]
        es = {(r["sahne"], r["tohum"]): r for r in s2}
        md += ["| sınama2 sahnesi | tohum | v2 durum | v2 süre | v3 durum | v3 süre |",
               "| --- | --- | --- | --- | --- | --- |"]
        for r in sorted(s3, key=lambda r: (r["sahne"], r["tohum"])):
            a = es.get((r["sahne"], r["tohum"]), {})
            md.append("| %s | %s | %s | %s | %s | %s |" % (r["sahne"], r["tohum"], a.get("durum", "-"),
                                                          a.get("sure_s", "-"), r.get("durum"), r.get("sure_s")))
        md.append("")
    es = {(r["sahne"], r["tohum"]): r for r in d2}
    md += ["| geliştirme sahnesi | tohum | v2 durum | v2 süre | v3 durum | v3 süre |", "| --- | --- | --- | --- | --- | --- |"]
    for r in sorted(d3, key=lambda r: (r["sahne"], r["tohum"])):
        a = es.get((r["sahne"], r["tohum"]), {})
        if a.get("durum") != r.get("durum") or abs((_f(a.get("sure_s")) or 0) - (_f(r.get("sure_s")) or 0)) > 1:
            md.append("| %s | %s | %s | %s | %s | %s |" % (r["sahne"], r["tohum"], a.get("durum", "-"),
                                                          a.get("sure_s", "-"), r.get("durum"), r.get("sure_s")))
    md += ["", "(yalnız farklı sonuçlanan geliştirme koşuları)", ""]
    import json
    from ._yol import SAHNELER
    U = [("v2", _csv("mujoco_uzatilmis_v2.csv")), ("v3", _csv("mujoco_uzatilmis_v3.csv"))]
    if U[1][1]:
        md += ["### Uzatılmış (KURAL DIŞI 1800 s, tohum 0): dolanma kayboldu mu", "",
               "| sürüm | başarı | fail_sikisma | ort yol / çözüm | süre (başarılı, s) |", "| --- | --- | --- | --- | --- |"]
        for et, M in U:
            oranlar, sure = [], []
            for r in M:
                with open(os.path.join(SAHNELER, r["sahne"] + ".json"), encoding="utf-8") as f:
                    coz = float(json.load(f)["labirent"]["cozum_uzunlugu_m"])
                oranlar.append((_f(r.get("yol_m")) or 0) / coz)
                if r.get("durum") == "basari":
                    sure.append("%s %.0f" % (r["sahne"][9:], _f(r["sure_s"])))
            md.append("| %s | %d/%d | %d | %.2f | %s |" % (et, sum(r.get("durum") == "basari" for r in M), len(M),
                                                         sum(r.get("durum") == "fail_sikisma" for r in M),
                                                         st.mean(oranlar) if oranlar else 0, ", ".join(sure)))
        md.append("")
    v3_2b = [r for r in S if r.get("_dosya") == "v3_2b.csv"]
    if v3_2b:
        md += ["### 2B v2 / v3 (21 geliştirme labirenti x tohum {0, 1}, `sonuc/v3_2b.csv`)", "",
               ozet_tablo(v3_2b, lambda r: (r.get("ayar"), _boy(r["sahne"]))), ""]
    return md


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
    md += surum_bolumu(ilk, [r for r in S if r.get("_dosya") == "v2_2b.csv"])
    md += uzatilmis_bolumu()
    md += v3_bolumu(S)
    from .rapor_deneme import deneme_bolumu
    md += deneme_bolumu()
    from .rapor_hiz4 import v4_bolumu
    md += v4_bolumu()
    from .rapor_v5 import v5_bolumu
    md += v5_bolumu()
    from .rapor_v6 import v6_bolumu
    md += v6_bolumu()
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
