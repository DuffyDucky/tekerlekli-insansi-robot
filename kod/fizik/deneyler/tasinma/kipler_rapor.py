"""Kip karşılaştırması tabloları (kipler.py ham sonuçlarından) + "emin değilim" ölçütünün sınamada etkisi.

    py -3 kipler_rapor.py     # -> sonuc/kipler_2b.csv, sonuc/kipler_ozet.json, sonuc/kipler_tablolar.md

Önce `emin.py` (geliştirme kümesinde kural seçimi, sonuc/emin_secim.json)."""

import csv
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emin  # noqa: E402
import kipler as KP  # noqa: E402

SONUC = os.path.join(KP.KC.SONUC)
ALANLAR = ["id", "kume", "kip", "kosul", "dunya", "tur", "koridor", "tohum", "hedef", "sonuc", "beyin_bitti",
           "varis_m", "sure_s", "bitis", "rota_m", "t_tasima", "alarm", "alarm_tasima_oncesi", "tepki_s", "kurtarma",
           "yardim", "temas_olay", "temas_hareketli", "temas_duran", "yanlis_surus_s", "konum_maks_m",
           "konum_kesin_yanlis", "bekleme_s", "nan_orani", "v_sic_maks", "v_u_med", "v_g_med", "v_std_xy", "v_pay",
           "v_kk", "v_rast", "emin_sonuc", "duvar_s"]
GRUPLAR = [
    ("temiz harita", ["taban"]),
    ("okul günü hafif", ["okul_hafif"]),
    ("okul günü orta", ["okul_orta"]),
    ("okul günü ağır", ["okul_agir"]),
    ("tek etken 2. kademe: kapı %25, cam %50", ["kapi_2", "cam_2", "esya_2"]),
    ("tek etken 3. kademe: kapı %50, dönüşsüz %50", ["kapi_3", "donussuz_3", "cam_3", "donussuz_4"]),
    ("taşınma, temiz harita (4 tür)", ["taban+ayni_uzak", "taban+ters180", "taban+kucuk", "taban+baska_koridor"]),
    ("taşınma (küçük) + eskime (kapı / cam / dönüşsüz)", ["kapi_2+ayni_uzak", "kapi_2+kucuk", "cam_2+ayni_uzak", "cam_2+kucuk",
                                                  "donussuz_3+ayni_uzak", "donussuz_3+kucuk"]),
]


def oku(kume):
    """Yalnız kümenin (daraltılmış) koşul listesindeki koşular: kesilen koşulun yarım kalan koşuları gruba girmesin."""
    K = set(KP.KUMELER[kume]["kosullar"])
    return [s for s in emin.oku(kume) if s["kosul"] in K]


def basarili(s):
    """Doğru davranış: hedefe doğru varış; tek haritalı beyni başka koridora taşımada güvenli durma."""
    if s.get("tur") == "baska_koridor":
        return s["sonuc"] == "guvenli_durma"
    return s["sonuc"] == "dogru_varis"


def yanlis_alarm(s):
    """Taşıma YOKKEN (ya da taşımadan önce) "kayboldum"."""
    return (s.get("alarm_tasima_oncesi") or 0) > 0


def satir_duz(s, kural):
    v = s.get("vardim") or {}
    d = {k: s.get(k) for k in ALANLAR}
    d.update(v_sic_maks=v.get("sic_maks"), v_u_med=v.get("u_med"), v_g_med=v.get("g_med"), v_std_xy=v.get("std_xy"),
             v_pay=v.get("pay"), v_kk=v.get("kk"), v_rast=(round(emin.deger(v, "rast"), 3) if v else None),
             emin_sonuc=(emin.uygula(s, kural) if kural else None))
    return d


def ozet(S, kural=None):
    n = len(S)
    o = dict(n=n, basari=sum(1 for s in S if basarili(s)),
             dogru=sum(1 for s in S if s["sonuc"] == "dogru_varis"),
             sessiz=sum(1 for s in S if s["sonuc"] == "sessiz_hata"),
             guvenli=sum(1 for s in S if s["sonuc"] == "guvenli_durma"),
             sure=sum(1 for s in S if s["sonuc"] == "sure_doldu"),
             istisna=sum(1 for s in S if s["sonuc"] == "istisna"),
             alarm=sum(1 for s in S if yanlis_alarm(s)),
             temas=sum(1 for s in S if (s.get("temas_olay") or 0) > 0),
             temas_olay=sum(s.get("temas_olay") or 0 for s in S))
    T = [s for s in S if s.get("t_tasima") is not None]
    o["tasima"] = len(T)
    o["fark"] = sum(1 for s in T if s.get("tepki_s") is not None)
    tp = [s["tepki_s"] for s in T if s.get("tepki_s") is not None]
    o["fark_med"] = round(statistics.median(tp), 1) if tp else None
    o["fark_maks"] = round(max(tp), 1) if tp else None
    if kural:
        U = [emin.uygula(s, kural) for s in S]
        o["e_onlenen"] = U.count("onlenen")
        o["e_gereksiz"] = U.count("gereksiz_durma")
    return o


def hucre(o):
    return "%d / %d / %d / %d" % (o["dogru"], o["sessiz"], o["guvenli"], o["sure"])


def tablo_kosul(S, kipler):
    gr = {}
    for s in S:
        gr.setdefault((s["kosul"], s["kip"]), []).append(s)
    satir = ["| Koşul | " + " | ".join(kipler) + " | yanlış alarm (algi / izleme_algi) | fark etme (algi / izleme_algi) | temaslı koşu (" + " / ".join(kipler) + ") |",
             "| --- |" + " --- |" * len(kipler) + " --- | --- | --- |"]
    for kosul in KP.KUMELER[S[0]["kume"]]["kosullar"]:
        if not any((kosul, k) in gr for k in kipler):
            continue
        O = {k: ozet(gr.get((kosul, k), [])) for k in kipler}
        al = " / ".join("%d" % O[k]["alarm"] if k in O and O[k]["n"] else "-" for k in ("algi", "izleme_algi")
                        if k in kipler) or "-"
        fk = " / ".join(("%d/%d (%s s)" % (O[k]["fark"], O[k]["tasima"], O[k]["fark_med"]) if O[k]["tasima"] else "-")
                        for k in ("algi", "izleme_algi") if k in kipler) or "-"
        satir.append("| %s | %s | %s | %s | %s |" % (kosul, " | ".join(hucre(O[k]) if O[k]["n"] else "-" for k in kipler),
                                                    al, fk, " / ".join(str(O[k]["temas"]) for k in kipler)))
    return "\n".join(satir)


def tablo_grup(S, kipler, kural):
    satir = ["| Koşul grubu (koşu / kip) | Kip | Doğru davranış | Sessiz hata | Güvenli durma | Süre doldu | Yanlış alarm | Temaslı koşu | Ölçütle önlenen sessiz hata | Ölçütle gereksiz durma |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    out = {}
    for ad, kosullar in GRUPLAR:
        for k in kipler:
            L = [s for s in S if s["kosul"] in kosullar and s["kip"] == k]
            if not L:
                continue
            o = ozet(L, kural)
            out[(ad, k)] = o
            satir.append("| %s | %s | %d / %d | %d | %d | %d | %s | %d | %s | %s |" % (
                "%s (%d)" % (ad, o["n"]) if k == kipler[0] else "", k, o["basari"], o["n"], o["sessiz"], o["guvenli"],
                o["sure"], ("%d" % o["alarm"]) if "algi" in k else "-", o["temas"],
                ("%d / %d" % (o["e_onlenen"], o["sessiz"])) if kural else "-",
                ("%d / %d" % (o["e_gereksiz"], o["dogru"])) if kural else "-"))
    return "\n".join(satir), out


def alarm_neden(o):
    n = (o[2] or {}).get("neden", "") if isinstance(o[2], dict) else str(o[2])
    if n.startswith("sicrama"):
        return "poz sıçraması"
    if n.startswith("bitti"):
        return "bitti ama şüpheli"
    return "uyum"


def tablo_alarm(S):
    """Taşıma yokken (ya da taşımadan önce) ilk "kayboldum"un nedeni, algi kiplerinde."""
    satir = ["| Koşul | Kip | yanlış alarmlı koşu | ilk alarm nedeni: poz sıçraması / uyum (10 taramanın 8'i kötü) / bitti ama şüpheli | alarm taramasında geçiş > 0,10 / uyum < 0,60 | yanlış alarmlı koşuların sonucu (doğru / sessiz / güvenli / süre) |",
             "| --- | --- | --- | --- | --- | --- |"]
    for kosul in KP.KUMELER[S[0]["kume"]]["kosullar"]:
        for k in ("algi", "izleme_algi"):
            L = [s for s in S if s["kosul"] == kosul and s["kip"] == k and yanlis_alarm(s)]
            if not L:
                continue
            ned = {"poz sıçraması": 0, "uyum": 0, "bitti ama şüpheli": 0}
            gc = du = 0
            for s in L:
                ilk = next(o for o in s["olaylar"] if o[1] == "kayboldum")
                ned[alarm_neden(ilk)] += 1
                ug = (ilk[2] or {}).get("uyum") if isinstance(ilk[2], dict) else None
                if ug and ug[0] is not None:
                    gc += ug[1] > 0.10
                    du += ug[0] < 0.60
            o = ozet(L)
            satir.append("| %s | %s | %d | %d / %d / %d | %d / %d | %s |" % (
                kosul, k, len(L), ned["poz sıçraması"], ned["uyum"], ned["bitti ama şüpheli"], gc, du, hucre(o)))
    return "\n".join(satir)


def main():
    secim = None
    if os.path.exists(emin.SECIM):
        with open(emin.SECIM, encoding="utf-8") as f:
            secim = json.load(f)
    kural = [tuple(x) for x in secim["kural"]] if secim else None
    md = ["# Kip karşılaştırması: tablolar (kipler_rapor.py üretir)", ""]
    ozetler = {}
    tum = []
    for kume in ("sinama", "gelistirme"):
        S = oku(kume)
        if not S:
            continue
        tum += S
        kipler = [k for k in KP.KUMELER[kume]["kipler"] if any(s["kip"] == k for s in S)]
        md += ["## %s (%d koşu; tohum %s)" % (kume, len(S), ", ".join(map(str, KP.KUMELER[kume]["tohumlar"]))), "",
               "Hücre: doğru varış / sessiz hata (yanlış yerde \"vardım\") / güvenli durma (\"yardım\") / süre doldu; "
               "koşul başına 12 koşu (6 koridor x 2 tohum).", "", tablo_kosul(S, kipler), "",
               "### Gruplar (ölçüt: %s)" % (kural if kural else "yok"), ""]
        t, o = tablo_grup(S, kipler, kural)
        md += [t, ""]
        if "algi" in kipler:
            md += ["### Yanlış alarmlar (taşıma yokken / taşımadan önce)", "", tablo_alarm(S), ""]
        ozetler[kume] = {"%s|%s" % k: v for k, v in o.items()}
        if kural:
            tk = {k: ozet([s for s in S if s["kip"] == k], kural) for k in kipler}
            ozetler[kume + "_kip"] = tk
            md += ["Ölçütün kip başına etkisi (%s): " % kume + "; ".join(
                "%s önlenen %d / %d sessiz hata, gereksiz durma %d / %d doğru varış" % (
                    k, v["e_onlenen"], v["sessiz"], v["e_gereksiz"], v["dogru"]) for k, v in tk.items()), ""]
            k2 = [tuple(x) for x in secim["en_iyi_tek"][0][0]]
            t2 = {k: ozet([s for s in S if s["kip"] == k], k2) for k in kipler}
            ozetler[kume + "_kip_tek"] = dict(kural=k2, ozet=t2)
            md += ["İkincil (seçilmedi; geliştirmenin en iyi tek adaylı kuralı %s): " % k2 + "; ".join(
                "%s önlenen %d / %d, gereksiz %d / %d" % (k, v["e_onlenen"], v["sessiz"], v["e_gereksiz"], v["dogru"])
                for k, v in t2.items()), ""]
    with open(os.path.join(SONUC, "kipler_2b.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, extrasaction="ignore")
        w.writeheader()
        for s in tum:
            w.writerow(satir_duz(s, kural))
    with open(os.path.join(SONUC, "kipler_ozet.json"), "w", encoding="utf-8") as f:
        json.dump(dict(kural=kural, secim=secim, ozet=ozetler), f, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(SONUC, "kipler_tablolar.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
