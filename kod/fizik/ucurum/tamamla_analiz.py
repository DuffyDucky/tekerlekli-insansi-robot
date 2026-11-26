"""Tamamlama turu tabloları: sonuc/t_*.csv -> sonuc/tamamlama_tablolar.md (yalnız standart kütüphane; py -3).

    py -3 kod\\fizik\\ucurum\\tamamla_analiz.py
"""

import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402

E = 16.0


def oku(asama):
    yol = os.path.join(_yol.SONUC, asama + ".csv")
    if not os.path.exists(yol):
        return []
    with open(yol, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def b(x):
    return str(x) == "True"


def yer(r):
    return (r.get("yerlesim") or "").split("_z")[0]


def ozet(R):
    """düşme / koşu, en küçük pay (cm), hata."""
    n = len(R)
    d = sum(1 for r in R if b(r.get("dustu")))
    p = [f(r.get("pay_min_cm")) for r in R if f(r.get("pay_min_cm")) is not None]
    h = sum(1 for r in R if r.get("hata"))
    s = "%d / %d" % (d, n)
    if p:
        s += " (%s)" % ("%.1f" % min(p)).replace(".", ",")
    if h:
        s += " [%d hata]" % h
    return s


def fiziksel(R):
    """Hakemden bağımsız fiziksel sonuç: bir teker 20 mm'den çok indi ya da gövde 5°'den çok eğildi."""
    n = sum(1 for r in R if (f(r.get("teker_dz_min_mm")) or 0) < -20 or (f(r.get("egim_max_der")) or 0) > 5)
    return "%d / %d" % (n, len(R))


def kume(R, *anahtar):
    G = defaultdict(list)
    for r in R:
        G[tuple(a(r) if callable(a) else r.get(a) for a in anahtar)].append(r)
    return G


def tablo(baslik, sutun, satirlar):
    out = ["", "### " + baslik, "", "| " + " | ".join(sutun) + " |", "| " + " | ".join("---" for _ in sutun) + " |"]
    out += ["| " + " | ".join(str(c) for c in s) + " |" for s in satirlar]
    return out


def v_(x):
    return ("%.2f" % float(x)).replace(".", ",") if x not in (None, "") else "-"


def main():
    M = ["# Tamamlama turu tabloları (otomatik; `tamamla_analiz.py`)", "",
         "Düşme / koşu (en küçük pay cm). Pay = dört teker merkezinin kenara (deliğe) en küçük yatay payı; < 0 = düştü.",
         "Hata sütunu yalnız istisna varsa görünür. Ayar: t_delik_gel, t_yaklasma_gel, t_kusur6, t_rampa_*, t_duyar (tohum 1-3);",
         "hüküm: t_hukum (tohum 201-205 kullanıldı; 206-210 ayrıldı, tamamlama 2 hükmünde kullanıldı)."]
    # 1a tehlike
    R = oku("t_delik_tehlike")
    if R:
        S = []
        for r in sorted(R, key=lambda r: (r["alt"], int(r["sahne"].split("_")[1]), f(r["yanal"]), f(r["v"]))):
            L = int(r["sahne"].split("_")[1]) / 100.0 if r["alt"] == "kare" else 1.0
            gecti = f(r["x_son"]) is not None and f(r["x_son"]) > E + L + 0.2
            S.append((r["sahne"], v_(r["yanal"]), v_(r["v"]), "evet" if b(r["dustu"]) else "hayır", r["teker_dz_min_mm"],
                      r["egim_max_der"], r["dz_min_mm"], "evet" if b(r["govde_temas"]) else "hayır", "evet" if gecti else "HAYIR",
                      r.get("dustu_neden") or ""))
        M += tablo("1a. Delik tehlikesi (denetçi kapalı, robot deliğin üstünden geçer; tohum 1)",
                   ["sahne", "delik y (robota göre)", "v", "teker merkezi delik üstünde", "teker en çok iniş mm", "eğim en çok °",
                    "gövde z en az mm", "gövde zemine değdi", "geçti", "hakem nedeni"], S)
    R = oku("t_delik_boy")
    if R:
        S = []
        for (sh,), x in sorted(kume(R, "sahne").items(), key=lambda k: [int(c) for c in k[0][0].split("_")[1].split("x")]):
            S.append([sh, fiziksel(x), "%.1f" % min(f(r["teker_dz_min_mm"]) for r in x), "%.1f" % max(f(r["egim_max_der"]) for r in x),
                      sum(1 for r in x if b(r["govde_temas"]))])
        M += tablo("1a. Yarık boyu (denetçi kapalı; sol iz yarığın ortasında; 2 hız x tohum 1-3, açı 0 (±2°))",
                   ["yarık (genişlik x boy cm)", "fiziksel düşme", "teker en çok iniş mm", "eğim en çok °", "gövde değdi"], S)
    # 1b geliştirme
    R = oku("t_delik_gel")
    if R:
        D = [r for r in R if r["alt"] == "delik"]
        sh = sorted({r["sahne"] for r in D}, key=lambda s: (s.split("_")[0], int(s.split("_")[1])))
        S = []
        for ad in sorted({yer(r) for r in D}):
            g = kume([r for r in D if yer(r) == ad], "sahne")
            S.append([ad] + [ozet(g.get((s,), [])) for s in sh] + [ozet([r for r in D if yer(r) == ad]),
                                                                     fiziksel([r for r in D if yer(r) == ad])])
        M += tablo("1b. Dar delik, geliştirme (2 hız x 2 açı x 7 yanal x tohum 1-2 = sahne başına 56; hakem: teker merkezi delik "
                   "üstüne geçti = düştü, kötümser; fiziksel: teker > 20 mm indi ya da eğim > 5°)",
                   ["aday"] + sh + ["toplam", "fiziksel"], S)
        yr = sorted({f(r["yanal"]) for r in D})
        S = []
        for ad in sorted({yer(r) for r in D}):
            g = kume([r for r in D if yer(r) == ad], lambda r: f(r["yanal"]))
            S.append([ad] + [ozet(g.get((y,), [])) for y in yr])
        M += tablo("1b. Dar delik, deliğin robota göre y'si (m)", ["aday"] + [v_(y) for y in yr], S)
        g = kume(D, yer, "v")
        S = [[k[0], v_(k[1]), ozet(x)] for k, x in sorted(g.items())]
        M += tablo("1b. Dar delik, hıza göre", ["aday", "v", "düşme"], S)
        S = []
        for alt in ("dar", "ileri"):
            g = kume([r for r in R if r["alt"] == alt], yer)
            S += [[alt, k[0], ozet(x)] for k, x in sorted(g.items())]
        M += tablo("1b. Aynı adaylar: robottan dar açıklık (0,40 / 0,50) ve geniş kenar", ["alt", "aday", "düşme"], S)
    # 2
    R = oku("t_yaklasma_gel")
    if R:
        geos = ["acik_40", "acik_50", "acik_60", "acik_80", "acik_100", "merdiven_17x30", "bosluk_3m"]
        S = []
        for (alt, ad), x in sorted(kume(R, "alt", yer).items()):
            g = kume(x, "sahne")
            S.append([alt, ad] + [ozet(g.get((s,), [])) for s in geos] + [ozet(x)])
        M += tablo("2. Geri giderek ve yerinde dönerek yaklaşma (geliştirme, tohum 1-2)", ["senaryo", "aday"] + geos + ["toplam"], S)
        S = []
        for (alt, ad, v), x in sorted(kume([r for r in R if r["alt"] == "geri"], "alt", yer, "v").items()):
            S.append([alt, ad, v_(v), ozet(x), sum(1 for r in x if not b(r["tetik"]))])
        M += tablo("2. Geri, hıza göre (tetiksiz = hiç durmadı)", ["senaryo", "aday", "v", "düşme", "tetiksiz"], S)
    # 3
    R = oku("t_kusur6")
    if R:
        S = []
        for alt in ("olu_on", "olu_arka"):
            for (ar,), x in sorted(kume([r for r in R if r["alt"] == alt], "ariza").items()):
                ned = defaultdict(int)
                for r in x:
                    ned[r.get("neden") or "tetik yok"] += 1
                S.append([alt, ar or "arızasız", ozet(x), ", ".join("%s %d" % kv for kv in sorted(ned.items()))])
        M += tablo("3. Tek sensör ölü (4OD+2AD; sıra 0 ön sol köşe, 1 ön iç sol, 2 ön iç sağ, 3 ön sağ köşe, 4 arka sol, 5 arka sağ)",
                   ["senaryo", "arıza", "düşme", "tetik nedeni"], S)
        S = []
        for (yok,), x in sorted(kume([r for r in R if r["alt"] == "parlak"], lambda r: f(r["yok_orani_ayar"])).items()):
            uc = [r for r in x if r["sahne"] != "duz"]
            dz = [r for r in x if r["sahne"] == "duz"]
            S.append(["%d" % round(yok * 100), ozet(uc), "%d / %d" % (sum(1 for r in dz if b(r["tetik"])), len(dz))])
        M += tablo("3. Dönüşsüz örnek oranı (bütün sensörler), politika yavasla", ["dönüşsüz %", "uçurumda düşme (kaçırma)",
                                                                                    "düz zeminde durma (yanlış durma)"], S)
    R = oku("t_delik_fiz")
    if R:
        S = []
        for (ad, sh), x in sorted(kume(R, yer, "sahne").items()):
            dur = sum(1 for r in x if r["bitis"] == "durdu")
            S.append([ad, sh, ozet(x), fiziksel(x), "%d / %d" % (dur, len(x)), sum(1 for r in x if b(r["govde_temas"]))])
        M += tablo("1b. Yarıkta fiziksel sonuç (t_delik_gel yarık görevleri, koşu hakem 'düştü' dedikten sonra da sürer)",
                   ["aday", "sahne", "hakem (teker merkezi yarık üstünde)", "fiziksel düşme", "durdu", "gövde değdi"], S)
    R = oku("t_donus_w")
    if R:
        S = []
        for (w, d), x in sorted(kume(R, lambda r: abs(f(r["w"])), lambda r: f(r["d"])).items()):
            S.append([v_(w), v_(d), ozet(x)])
        M += tablo("2. Dar açıklık yanında yerinde dönüş, dönüş hızı tavanı (4OD+4AD, acik_40-100, tohum 1-2)",
                   ["|w| rad/s", "dönme merkezinin kenara uzaklığı m", "düşme"], S)
    R = oku("t_hukum_fiz")
    if R:
        S = []
        for (alt, sh, d), x in sorted(kume(R, "alt", "sahne", "d").items()):
            S.append([alt, sh, d or "-", ozet(x), fiziksel(x), sum(1 for r in x if b(r["govde_temas"]))])
        M += tablo("7. Hükümden sonra, yalnız rapor: hakemin düşme saydığı sahne türlerinde fiziksel sonuç (t_hukum_fiz, aynı görevler, "
                   "koşu sürer)", ["senaryo", "sahne", "d", "hakem", "fiziksel düşme", "gövde değdi"], S)
    R = oku("t_aday_son")
    if R:
        S = []
        for (alt, k), x in sorted(kume(R, "alt", lambda r: r["d"] if r["alt"] == "donus" else r["v"]).items()):
            ek = ""
            if alt == "yanlis_alarm":
                ek = "durdu %d / %d" % (sum(1 for r in x if b(r["tetik"])), len(x))
            elif alt == "kusur":
                ek = "arıza fark edilip durdu %d / %d" % (sum(1 for r in x if r.get("neden") == "yok"), len(x))
            elif alt == "delik":
                ek = "koşu hakemden 0,3 s sonra biter: fiziksel sonuç ölçülmedi"
            S.append([alt, ("d " if alt == "donus" else "v ") + v_(k), ozet(x), ek])
        M += tablo("Seçim öncesi son denetim: 6OD+4AD, kısa kip K20, konum tutma (geliştirme sahneleri, tohum 1-2)",
                   ["senaryo", "d / v", "düşme", "ek"], S)
    # 4
    R = oku("t_rampa_fren")
    if R:
        S = []
        for r in sorted(R, key=lambda r: (r["sahne"], r["kosul"], f(r["fren_ivme"]), f(r["v"]), r["tohum"])):
            if r["tohum"] != "1":
                continue
            k = json.loads(r["kosul"] or "{}").get("tutma")
            S.append((r["sahne"], k[0] if k else "yok", v_(r["fren_ivme"]), v_(r["v"]), r.get("arka_yuk_once_N"), r.get("arka_yuk_min_N"),
                      r.get("arka_sifir_s"), r.get("pitch_tepe_der"), r.get("tepe_yavaslama"), r.get("durma_yolu_06_m"),
                      r.get("kayma_2s_son_mm"), r.get("v_son1s_mm_s")))
        M += tablo("4a. Fren ivmesi taraması, zorla tetik (tohum 1)",
                   ["sahne", "tutma", "a m/s²", "v", "arka aks önce N", "arka aks en az N", "arka 0 N s", "öne yatma tepe °",
                    "tepe yavaşlama", "durma yolu 0,6 s m", "kayma (tetik+2 s -> son) mm", "son 1 s hız mm/s"], S)
    R = oku("t_rampa_ucurum")
    if R:
        S = []
        for (a, k, v), x in sorted(kume(R, lambda r: f(r["fren_ivme"]), "kosul", lambda r: f(r["v"])).items()):
            t = json.loads(k or "{}").get("tutma")
            S.append([v_(a), t[0] if t else "yok", v_(v), ozet(x)])
        M += tablo("4b. 10° iniş rampasının ucunda 3 m düşüş (seçilen sensörler, gerçek tetik; tohum 1, açı 0 / 20)",
                   ["fren a", "tutma", "v", "düşme"], S)
    # 5-6
    R = oku("t_duyar")
    if R:
        kads = list(dict.fromkeys(r["kad"] for r in R))
        S = []
        for kad in kads:
            x = [r for r in R if r["kad"] == kad]
            uc = [r for r in x if r["alt"] != "yanlis_alarm"]
            row = [kad]
            for v in ("0.25", "0.3", "0.39"):
                row.append(ozet([r for r in uc if r["v"] in (v,) and r["alt"] in ("ileri", "dar")]))
            row.append(ozet([r for r in uc if r["alt"] in ("geri", "donus")]))
            ya = [r for r in x if r["alt"] == "yanlis_alarm"]
            row.append("%d / %d" % (sum(1 for r in ya if b(r["tetik"])), len(ya)))
            S.append(row)
        M += tablo("5-6. Zamanlama ve duyarlılık (4OD+2AD; geliştirme sahneleri, tohum 1): ileri + dar açıklık, hıza göre",
                   ["koşul", "0,25 m/s", "0,30 m/s", "0,39 m/s", "geri + dönüş (≤ 0,25)", "yanlış durma"], S)
    # 7
    for asama in ("t_hukum", "t_hukum_karsi"):
        R = oku(asama)
        if not R:
            continue
        S = []
        for (alt, sahne), x in sorted(kume([r for r in R if not r["alt"].startswith("yanlis")], "alt", "sahne").items()):
            g = kume(x, "v")
            S.append([alt, sahne] + [ozet(g.get((v,), [])) for v in ("0.1", "0.2", "0.25", "0.3", "0.39", "")] + [ozet(x)])
        M += tablo("7. Hüküm (%s; tohum 201-205)" % asama, ["senaryo", "sahne", "0,10", "0,20", "0,25", "0,30", "0,39", "hızsız (dönüş)",
                                                            "toplam"], S)
        ya = [r for r in R if r["alt"].startswith("yanlis")]
        g = kume(ya, "sahne")
        S = [[k[0], "%d / %d" % (sum(1 for r in x if b(r["tetik"])), len(x))] for k, x in sorted(g.items())]
        M += tablo("7. Hüküm, yanlış durma (%s)" % asama, ["sahne", "durdu / koşu"], S)
    with open(os.path.join(_yol.SONUC, "tamamlama_tablolar.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(M) + "\n")
    print("tamamlama_tablolar.md: %d satir" % len(M))
    main2()


def _durdu(x):
    return "%d / %d" % (sum(1 for r in x if b(r["tetik"])), len(x))


def main2():
    """Tamamlama 2 (bağımsız incelemenin engelleyicileri): sonuc/t2_*.csv -> sonuc/tamamlama2_tablolar.md."""
    M = ["# Tamamlama 2 tabloları (otomatik; `tamamla_analiz.py`)", "",
         "Düşme / koşu (en küçük pay cm); hakem: teker merkezi kenarı geçti, eğim > 15° ya da z 3 cm düştü. Ayar: t2_yarik_gel,",
         "t2_donus_gel, t2_kusur, t2_duyar (tohum 1-2, geliştirme sahneleri). Hüküm: t2_hukum (tohum 206-210)."]
    R = oku("t2_yarik_gel") + oku("t2_yarik_gel2")
    if R:
        D = [r for r in R if r["alt"] == "delik"]
        sh = sorted({r["sahne"] for r in D}, key=lambda s: int(s.split("_")[1]))
        S = []
        for ad in sorted({yer(r) for r in D}):
            x = [r for r in D if yer(r) == ad]
            g = kume(x, "sahne")
            S.append([ad] + [ozet(g.get((s,), [])) for s in sh] + [ozet(x)] +
                     [ozet([r for r in R if yer(r) == ad and r["alt"] == a]) for a in ("dar", "ileri")])
        M += tablo("Y1. Yarık düzeltmesi, ayar (t2_yarik_gel + sonradan eklenen 8WRD t2_yarik_gel2; 2 hız x 2 açı x 10 y x tohum 1-2 = sahne başına 80)",
                   ["aday"] + sh + ["yarık toplam", "dar açıklık 0,40 / 0,50", "geniş kenar"], S)
        yr = sorted({f(r["yanal"]) for r in D})
        S = []
        for ad in sorted({yer(r) for r in D}):
            g = kume([r for r in D if yer(r) == ad], lambda r: f(r["yanal"]))
            S.append([ad] + [ozet(g.get((y,), [])) for y in yr])
        M += tablo("Y1. Yarık, deliğin robota göre y'si (m)", ["aday"] + [v_(y) for y in yr], S)
    R = oku("t2_donus_gel") + oku("t2_donus_gel2")
    if R:
        S = []
        for ad in sorted({yer(r) for r in R}):
            x = [r for r in R if yer(r) == ad]
            g = kume([r for r in x if r["alt"] == "donus"], lambda r: f(r["d"]))
            ya = [r for r in x if r["alt"] == "yanlis_alarm"]
            S.append([ad] + [ozet(g.get((d,), [])) for d in (0.35, 0.40, 0.45, 0.50)] +
                     [ozet([r for r in x if r["alt"] == "donus_genis"]), ozet([r for r in x if r["alt"] == "ileri"]),
                      _durdu(ya) if ya else "-"])
        M += tablo("Y2. Dar açıklık yanında yerinde dönüş, yan sensör adayları (t2_donus_gel + t2_donus_gel2; acik_40-100, ±1 rad/s, 3 kayma, tohum 1-2; "
                   "d = dönme merkezinin kenara uzaklığı)",
                   ["aday", "d 0,35", "d 0,40", "d 0,45", "d 0,50", "geniş kenar dönüş d 0,30-0,45", "geniş kenar ileri",
                    "yanlış durma"], S)
    R = oku("t2_kusur")
    if R:
        from ucurum import sensor as SN
        ad = yer(R[0])
        L = [a.ad for a in SN.yerlesim(ad, 0.12, 30)]
        S = []
        for alt in ("olu_on", "olu_on_yarik", "olu_arka", "olu_yan"):
            for (ar,), x in sorted(kume([r for r in R if r["alt"] == alt], "ariza").items()):
                ned = defaultdict(int)
                for r in x:
                    ned[r.get("neden") or "tetik yok"] += 1
                if ar:
                    k, v = list(json.loads(ar).items())[0]
                    ar = "%s %s" % (L[int(k)], v)
                S.append([alt, ar or "arızasız", ozet(x), ", ".join("%s %d" % kv for kv in sorted(ned.items()))])
        M += tablo("K. Tek sensör ölü (%s; tohum 1)" % ad, ["senaryo", "arıza", "düşme", "tetik nedeni"], S)
        S = []
        for (yok,), x in sorted(kume([r for r in R if r["alt"] == "parlak"], lambda r: f(r["yok_orani_ayar"])).items()):
            uc = [r for r in x if r["sahne"] != "duz"]
            dz = [r for r in x if r["sahne"] == "duz"]
            S.append(["%d" % round(yok * 100), ozet(uc), _durdu(dz)])
        M += tablo("K. Dönüşsüz örnek oranı (bütün sensörler), politika yavasla", ["dönüşsüz %", "uçurumda düşme (kaçırma)",
                                                                                    "düz zeminde durma (yanlış durma)"], S)
    R = oku("t2_duyar")
    if R:
        S = []
        for kad in list(dict.fromkeys(r["kad"] for r in R)):
            x = [r for r in R if r["kad"] == kad]
            uc = [r for r in x if r["alt"] != "yanlis_alarm"]
            row = [kad] + [ozet([r for r in uc if r["v"] == v and r["alt"] in ("ileri", "dar", "delik")]) for v in ("0.25", "0.3", "0.39")]
            row += [ozet([r for r in uc if r["alt"] in ("geri", "donus")]), ozet([r for r in uc if r["alt"] == "donus_dar"]),
                    _durdu([r for r in x if r["alt"] == "yanlis_alarm"])]
            S.append(row)
        M += tablo("D. Zamanlama ve duyarlılık, seçilen düzen (her koşul secim.json hukum_kosul üstüne; tohum 1): ileri + dar "
                   "açıklık + yarık, hıza göre", ["koşul", "0,25 m/s", "0,30 m/s", "0,39 m/s", "geri + geniş kenar dönüş (≤ 0,25)",
                                                   "dar açıklık dönüş d 0,35 / 0,40", "yanlış durma"], S)
    R = oku("t2_hukum")
    if R:
        S = []
        for (alt, sahne), x in sorted(kume([r for r in R if not r["alt"].startswith("yanlis")], "alt", "sahne").items()):
            g = kume(x, "v")
            S.append([alt, sahne] + [ozet(g.get((v,), [])) for v in ("0.1", "0.2", "0.25", "0.3", "0.39", "")] + [ozet(x), fiziksel(x)])
        M += tablo("H. Hüküm (t2_hukum; tohum 206-210)", ["senaryo", "sahne", "0,10", "0,20", "0,25", "0,30", "0,39",
                                                          "hızsız (dönüş)", "toplam", "teker > 20 mm / eğim > 5°"], S)
        D = [r for r in R if r["alt"] == "yeni_donus_dar"]
        if D:
            S = [[v_(k[0]), ozet(x)] for k, x in sorted(kume(D, lambda r: f(r["d"])).items())]
            M += tablo("H. Hüküm, dar açıklık yanında yerinde dönüş, d'ye göre", ["d m", "düşme"], S)
        D = [r for r in R if r["alt"] == "yeni_delik"]
        if D:
            S = [[k[0], ozet(x)] for k, x in sorted(kume(D, "sahne").items(), key=lambda k: int(k[0][0].split("_")[1]))]
            M += tablo("H. Hüküm, yarık genişliğine göre", ["sahne", "düşme"], S)
        ya = [r for r in R if r["alt"].startswith("yanlis")]
        S = [[k[0], _durdu(x)] for k, x in sorted(kume(ya, "sahne").items())]
        M += tablo("H. Hüküm, yanlış durma", ["sahne", "durdu / koşu"], S)
    with open(os.path.join(_yol.SONUC, "tamamlama2_tablolar.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(M) + "\n")
    print("tamamlama2_tablolar.md: %d satir" % len(M))


if __name__ == "__main__":
    main()
