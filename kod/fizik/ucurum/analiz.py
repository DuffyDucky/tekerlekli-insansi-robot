"""Uçurum deney tabloları (yalnız standart kütüphane; py -3 ya da %V%).

    py -3 kod\\fizik\\ucurum\\analiz.py [durma denetim gelistirme kusur sinama]   -> sonuc/tablolar.md (+ ekrana)

SONUC.md'deki tablolar buradan alındı; hüküm metni SONUC.md'de elle yazıldı."""

import csv
import collections
import json
import math
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
SONUC = os.path.join(BURASI, "sonuc")


def oku(ad):
    yol = os.path.join(SONUC, ad + ".csv")
    if not os.path.exists(yol):
        return []
    with open(yol, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def tr(x, n=2):
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    return ("%%.%df" % n % x).replace(".", ",")


def tablo(bas, satirlar):
    s = ["| " + " | ".join(bas) + " |", "| " + " | ".join("---" for _ in bas) + " |"]
    for r in satirlar:
        s.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(s)


def yuzde(a, b):
    return "-" if b == 0 else "%d / %d" % (a, b)


def boolv(x):
    return str(x) == "True"


# ------------------------------------------------------------------ durma / devrilme
def durma():
    R = oku("durma")
    out = []
    for sahne in ("duz", "rampa_10_inis"):
        S = []
        g = collections.OrderedDict()
        for r in R:
            if r["sahne"] != sahne:
                continue
            k = (r["fren"] if r["fren"] != "rampa" else "rampa %s" % tr(fl(r["fren_ivme"]), 1), r["v"])
            g.setdefault(k, []).append(r)
        for (kip, v), L in g.items():
            r = L[0]
            if sahne == "duz":
                S.append((kip, v, tr(fl(r["durma_yolu_m"]) and fl(r["durma_yolu_m"]) * 100, 1), tr(fl(r["durma_sure_s"])),
                          tr(fl(r["tepe_yavaslama"])), tr(fl(r["arka_yuk_once_N"]), 0), tr(fl(r["arka_yuk_min_N"]), 0),
                          tr(fl(r["arka_sifir_s"]) * 1000, 0), tr(fl(r["arka_kalkma_mm"])), tr(fl(r["pitch_tepe_der"]), 3)))
            else:
                S.append((kip, v, tr(fl(r["durma_yolu_06_m"]) * 100, 1), tr(fl(r["v_min_06"]), 3), tr(fl(r["kayma_hiz_1_2s"]), 3),
                          tr(fl(r["tepe_yavaslama"])), tr(fl(r["arka_yuk_once_N"]), 0), tr(fl(r["arka_yuk_once_min_N"]), 0),
                          tr(fl(r["arka_yuk_min_N"]), 0), tr(fl(r["arka_sifir_s"]) * 1000, 0), tr(fl(r["arka_kalkma_mm"])),
                          tr(fl(r["pitch_tepe_der"]), 3)))
        if sahne == "duz":
            out.append("### Düz zemin\n\n" + tablo(("fren", "v m/s", "durma yolu cm", "süre s", "tepe yavaşlama m/s²", "arka aks önce N",
                                                     "arka aks en az N", "arka aks 0 N ms", "arka teker kalkma mm", "öne yatma tepe °"), S))
        else:
            out.append("### 10° iniş rampası (gövde rampanın ortasında)\n\n" +
                       tablo(("fren", "v m/s", "0,6 s'de yol cm", "0,6 s'de en düşük v", "1-2 s kayma v m/s", "tepe yavaşlama",
                              "arka aks önce ort. N", "arka aks önce en az N", "arka aks en az N", "arka aks 0 N ms",
                              "arka teker kalkma mm", "öne yatma tepe °"), S))
    return "\n\n".join(out)


# ------------------------------------------------------------------ denetim (yanlış alarm, gölge)
def denetim():
    G = oku("denetim_golge")
    R = {r["kimlik"]: r for r in oku("denetim")}
    if not G:
        return "(denetim yok)"
    sahneler = []
    anahtarlar = []
    for g in G:
        if g["sahne"] not in sahneler:
            sahneler.append(g["sahne"])
        if g["anahtar"] not in anahtarlar:
            anahtarlar.append(g["anahtar"])
    say = collections.Counter()
    top = collections.Counter()
    for g in G:
        top[(g["anahtar"], g["sahne"])] += 1
        if boolv(g["tetik"]):
            say[(g["anahtar"], g["sahne"])] += 1
    S = []
    for a in anahtarlar:
        S.append([a.replace("_ucurum", "")] + [yuzde(say[(a, s)], top[(a, s)]) for s in sahneler])
    t1 = tablo(["eşik / onay"] + sahneler, S)
    # yerleşim yüksekliği x eğim, eşik 30 / 40 mm onay 2
    out = [t1]
    for anahtar in ("e30_o2_ucurum", "e40_o2_ucurum", "e60_o2_ucurum"):
        say2 = collections.Counter()
        top2 = collections.Counter()
        for g in G:
            if g["anahtar"] != anahtar:
                continue
            y = g["yerlesim"].split("_", 1)[1]
            top2[(y, g["sahne"])] += 1
            if boolv(g["tetik"]):
                say2[(y, g["sahne"])] += 1
        ys = sorted({k[0] for k in top2})
        out.append("Eşik %s: yükseklik / eğim başına yanlış durma\n\n" % anahtar + tablo(["z / eğim"] + sahneler,
                   [[y] + [yuzde(say2[(y, s)], top2[(y, s)]) for s in sahneler] for y in ys]))
    hata = sum(1 for r in R.values() if r.get("hata"))
    dus = sum(1 for r in R.values() if boolv(r.get("dustu")))
    out.append("Koşu: %d, hata %d, devrilme / düşme %d." % (len(R), hata, dus))
    return "\n\n".join(out)


# ------------------------------------------------------------------ geliştirme (ana ızgara)
def _ozet(L):
    n = len(L)
    d = sum(1 for r in L if boolv(r["dustu"]))
    tet = sum(1 for r in L if boolv(r["tetik"]))
    p = sorted(fl(r["pay_min_cm"]) for r in L if fl(r["pay_min_cm"]) is not None)
    en_az = p[0] if p else None
    p05 = p[max(0, int(math.floor(0.05 * (len(p) - 1))))] if p else None
    return n, d, tet, en_az, p05


def gelistirme(R=None, baslik="Geliştirme"):
    R = R if R is not None else oku("gelistirme")
    out = []
    ileri = [r for r in R if r["tur"] == "ileri"]
    g = collections.defaultdict(list)
    for r in ileri:
        g[(r["fren"], r["yerlesim"])].append(r)
    S = []
    for (fren, y), L in sorted(g.items(), key=lambda kv: (kv[0][0], _ozet(kv[1])[1], -(_ozet(kv[1])[3] or -99))):
        n, d, tet, en_az, p05 = _ozet(L)
        S.append((fren, y, n, d, tet, tr(en_az, 1), tr(p05, 1)))
    out.append("### İleri yaklaşma, yerleşim başına (bütün açı x hız x geometri x tohum)\n\n" +
               tablo(("fren", "yerleşim", "koşu", "düştü", "tetik", "en küçük pay cm", "%5 pay cm"), S))
    # hız x açı (rampa 2,0) en iyi 4 yerleşim
    sirali = [k for k in sorted(g, key=lambda k: (_ozet(g[k])[1], -(_ozet(g[k])[3] or -99))) if k[0] == "rampa"][:4]
    for k in sirali:
        L = g[k]
        T = []
        for v in ("0.1", "0.25", "0.39"):
            sat = [v]
            for a in ("0", "15", "30", "45", "60", "80"):
                M = [r for r in L if r["v"] == v and r["aci"] == a]
                n, d, tet, en_az, _ = _ozet(M)
                sat.append("%s%s" % (tr(en_az, 1), (" (%d düştü)" % d) if d else ""))
            T.append(sat)
        out.append("%s, fren rampa: en küçük pay cm (hız x açı)\n\n" % k[1] + tablo(("v m/s", "0°", "15°", "30°", "45°", "60°", "80°"), T))
    for tur in ("geri", "donus", "yay"):
        M = [r for r in R if r["tur"] == tur]
        if not M:
            continue
        g2 = collections.defaultdict(list)
        for r in M:
            g2[r["yerlesim"]].append(r)
        T = []
        for y, L in sorted(g2.items(), key=lambda kv: (_ozet(kv[1])[1], -(_ozet(kv[1])[3] or -99))):
            n, d, tet, en_az, p05 = _ozet(L)
            T.append((y, n, d, tet, tr(en_az, 1), tr(p05, 1)))
        out.append("### %s\n\n" % {"geri": "Geri giderken kenar", "donus": "Kenar yanında yerinde dönüş",
                                     "yay": "Kenara eğik gelen dönüşlü yörünge"}[tur] +
                   tablo(("yerleşim", "koşu", "düştü", "tetik", "en küçük pay cm", "%5 pay cm"), T))
    hata = sum(1 for r in R if r.get("hata"))
    out.append("Koşu: %d, hata %d." % (len(R), hata))
    return "\n\n".join(out)


def _golge_genel(asama):
    G = oku(asama + "_golge")
    if not G:
        return "(%s yok)" % asama
    sahneler = sorted({g["sahne"] for g in G})
    say, top = collections.Counter(), collections.Counter()
    for g in G:
        k = (g["anahtar"].replace("_ucurum", ""), g["yerlesim"].split("_", 1)[1])
        top[(k, g["sahne"])] += 1
        say[(k, g["sahne"])] += boolv(g["tetik"])
    ks = sorted({k for k, _ in top}, key=lambda k: (float(k[0].split("_")[0][1:]), k[0], k[1]))
    return tablo(["eşik / onay", "z / eğim"] + sahneler, [[k[0], k[1]] + [yuzde(say[(k, s)], top[(k, s)]) if top[(k, s)] else "-"
                                                                       for s in sahneler] for k in ks])


def rampa_ayrinti():
    G = oku("rampa_ayrinti_golge")
    say, top = collections.Counter(), collections.Counter()
    for g in G:
        k = g["anahtar"].replace("_ucurum", "")
        top[(k, g["aci"])] += 1
        say[(k, g["aci"])] += boolv(g["tetik"])
    ks = sorted({k for k, _ in top}, key=lambda k: (float(k.split("_")[0][1:]), k))
    return ("10° iniş rampasına giriş açısına göre yanlış durma (2K ve 3KO, z 60 / 120 mm, eğim 0 / 15 / 30°, v 0,25 / 0,39, tohum 1)\n\n" +
            tablo(["eşik / onay", "0°", "15°", "30°", "45°", "60°"],
                  [[k] + [yuzde(say[(k, a)], top[(k, a)]) for a in ("0", "15", "30", "45", "60")] for k in ks]))


def denetim2():
    return "Çapraz köşe yerleşimi (2KD) yanlış durma, tohum 1\n\n" + _golge_genel("denetim2")


def gelistirme2():
    R = oku("gelistirme2")
    out = []
    for alt in ("ileri", "geri", "donus", "yay"):
        g = collections.defaultdict(list)
        for r in R:
            if r["alt"] == alt:
                g[(r["yerlesim"], "e%d_o%s" % (round(float(r["esik_m"]) * 1000), r["onay"]))].append(r)
        T = []
        for (y, k), L in sorted(g.items(), key=lambda kv: (_ozet(kv[1])[1], -(_ozet(kv[1])[3] or -99))):
            n, d, tet, en_az, p05 = _ozet(L)
            T.append((y, k, n, d, tet, tr(en_az, 1), tr(p05, 1)))
        out.append("### %s\n\n" % {"ileri": "İleri yaklaşma (2 geometri x 6 açı x 3 hız)", "geri": "Geri giderken kenar",
                                     "donus": "Kenar yanında yerinde dönüş", "yay": "Kenara eğik gelen dönüşlü yörünge"}[alt] +
                   tablo(("yerleşim", "eşik mm / onay", "koşu", "düştü", "tetik", "en küçük pay cm", "%5 pay cm"), T))
    out.append("Koşu: %d, hata %d." % (len(R), sum(1 for r in R if r.get("hata"))))
    return "\n\n".join(out)


def kusur():
    R = oku("kusur")
    out = []
    olu = [r for r in R if r["alt"] == "olu"]
    g = collections.defaultdict(list)
    for r in olu:
        a = json.loads(r["ariza"]) if r["ariza"] else {}
        k = "arızasız" if not a else "%s s%s" % ({"sabit": "donmuş değer", "yok": "hep menzil dışı"}[list(a.values())[0]],
                                                 list(a.keys())[0])
        g[(r["politika"], k)].append(r)
    T = []
    for (pol, k), L in sorted(g.items()):
        n, d, tet, en_az, _ = _ozet(L)
        T.append((pol, k, n, d, tr(en_az, 1)))
    out.append("### Ölü sensör (uçurum koşuları: düştü = kaçırma)\n\n" + tablo(("politika", "arıza", "koşu", "düştü", "en küçük pay cm"), T))
    par = [r for r in R if r["alt"] == "parlak"]
    g = collections.defaultdict(list)
    for r in par:
        g[(r["politika"], r["yok_orani_ayar"], "duz" if r["sahne"] == "duz" else "ucurum")].append(r)
    T = []
    for pol in ("ucurum", "yok_say", "yavasla"):
        for yok in ("0.0", "0.05", "0.2", "0.5"):
            U = g.get((pol, yok, "ucurum"), [])
            D = g.get((pol, yok, "duz"), [])
            if not U and not D:
                continue
            nU, dU, _, en_az, _ = _ozet(U) if U else (0, 0, 0, None, None)
            yanlis = sum(1 for r in D if boolv(r["tetik"]))
            T.append((pol, yok, yuzde(dU, nU), tr(en_az, 1), yuzde(yanlis, len(D))))
    out.append("### Zemini parlak yüzey: dönüşsüz örnek oranı\n\n" + tablo(("politika", "dönüşsüz oran", "uçurumda düştü (kaçırma)",
                                                                     "en küçük pay cm", "düz zeminde yanlış durma"), T))
    return "\n\n".join(out)


def sinama_y():
    return "Politika `yavasla` (öbür her şey sinama ile aynı), tohum 101-105\n\n" + sinama("sinama_y")


def sinama(asama="sinama"):
    R = oku(asama)
    out = []
    il = [r for r in R if r["alt"] == "ileri"]
    g = collections.defaultdict(list)
    for r in il:
        g[(r["sahne"], r["v"])].append(r)
    T = []
    for (s, v), L in sorted(g.items()):
        n, d, tet, en_az, p05 = _ozet(L)
        kotu = min(L, key=lambda r: fl(r["pay_min_cm"]) if fl(r["pay_min_cm"]) is not None else 1e9)
        T.append((s, v, n, d, tet, tr(en_az, 1), tr(p05, 1), kotu["aci"]))
    out.append("### İleri yaklaşma (sınama)\n\n" + tablo(("geometri", "v m/s", "koşu", "düştü", "tetik", "en küçük pay cm",
                                                       "%5 pay cm", "en kötü açı"), T))
    for alt in ("geri", "donus", "yay"):
        L = [r for r in R if r["alt"] == alt]
        if L:
            n, d, tet, en_az, p05 = _ozet(L)
            out.append("%s: %d koşu, düştü %d, tetik %d, en küçük pay %s cm, %%5 %s cm" % (alt, n, d, tet, tr(en_az, 1), tr(p05, 1)))
    ya = [r for r in R if r["alt"] == "yanlis_alarm"]
    g = collections.defaultdict(list)
    for r in ya:
        g[r["sahne"]].append(r)
    out.append("### Yanlış alarm (sınama)\n\n" + tablo(("sahne", "koşu", "yanlış durma"),
                                                     [(s, len(L), sum(1 for r in L if boolv(r["tetik"]))) for s, L in g.items()]))
    out.append("Koşu: %d, hata %d." % (len(R), sum(1 for r in R if r.get("hata"))))
    return "\n\n".join(out)


def _dar_tablo(R, baslik):
    """Dar açıklık: yerleşim x genişlik (düşme / koşu, en küçük pay), sonra yerleşim x yanal kayma."""
    dar = [r for r in R if r.get("alt") == "dar"]
    if not dar:
        return "(%s: dar açıklık koşusu yok)" % baslik
    yer = sorted({r["yerlesim"] for r in dar})
    geo = sorted({r["sahne"] for r in dar}, key=lambda s: (s.startswith("dar_merdiven"), s.endswith("_sig"),
                                                           int("".join(ch for ch in s.split("_")[1] if ch.isdigit()) or 0)))
    out = []
    T = []
    for y in yer:
        sat = [y]
        for s in geo:
            L = [r for r in dar if r["yerlesim"] == y and r["sahne"] == s]
            n, d, tet, en_az, _ = _ozet(L)
            sat.append("%d / %d (%s)" % (d, n, tr(en_az, 1)))
        n, d, tet, en_az, _ = _ozet([r for r in dar if r["yerlesim"] == y])
        sat.append("**%d / %d** (%s)" % (d, n, tr(en_az, 1)))
        T.append(sat)
    out.append("### %s: dar açıklık, düştü / koşu (en küçük pay cm)\n\n" % baslik + tablo(["yerleşim"] + geo + ["toplam"], T))
    yan = sorted({fl(r["yanal"]) for r in dar if fl(r.get("yanal")) is not None})
    T = []
    for y in yer:
        for v in ("0.1", "0.25", "0.39"):
            sat = [y, v]
            for o in yan:
                L = [r for r in dar if r["yerlesim"] == y and r["v"] == v and fl(r["yanal"]) == o]
                n, d, tet, en_az, _ = _ozet(L)
                sat.append("%d / %d (%s)" % (d, n, tr(en_az, 1)))
            T.append(sat)
    out.append("Yanal kaymaya göre (açıklığın orta hattından, m; bütün genişlik ve açılar)\n\n" +
               tablo(["yerleşim", "v m/s"] + [tr(o, 2) for o in yan], T))
    ulasmadi = sum(1 for r in dar if not boolv(r["tetik"]) and not boolv(r["dustu"]))
    out.append("Tetiklemeyen ve düşmeyen (açıklığa varmadan ya da yanından geçen) koşu: %d / %d." % (ulasmadi, len(dar)))
    return "\n\n".join(out)


def _alt_ozet(R, altlar=("ileri", "geri", "donus", "yay")):
    T = []
    for y in sorted({r["yerlesim"] for r in R}):
        sat = [y]
        for alt in altlar:
            L = [r for r in R if r["yerlesim"] == y and r.get("alt") == alt]
            if not L:
                sat.append("-")
                continue
            n, d, tet, en_az, _ = _ozet(L)
            sat.append("%d / %d (%s)" % (d, n, tr(en_az, 1)))
        for alt in ("yanlis_alarm", "yanlis_alarm_yeni"):
            L = [r for r in R if r["yerlesim"] == y and r.get("alt") == alt]
            sat.append(yuzde(sum(1 for r in L if boolv(r["tetik"])), len(L)) if L else "-")
        T.append(sat)
    return tablo(["yerleşim"] + ["%s düştü (pay)" % a for a in altlar] + ["yanlış durma", "yanlış durma (yeni sahne)"], T)


def dar_gelistirme():
    R = oku("dar_gelistirme")
    out = [_dar_tablo(R, "Geliştirme (tohum 1-2)")]
    out.append("### Geniş kenar ve yanlış alarm (geliştirme sahneleri, politika yavasla)\n\n" + _alt_ozet(R))
    K = [r for r in R if r.get("alt") == "kusur"]
    g = collections.defaultdict(list)
    for r in K:
        a = json.loads(r["ariza"])
        g[(r["yerlesim"], "s%s %s" % (list(a)[0], list(a.values())[0]), r["sahne"])].append(r)
    T = [(k[0], k[1], k[2], len(L), sum(boolv(r["dustu"]) for r in L), sum(boolv(r["tetik"]) for r in L),
          ",".join(sorted({r["neden"] or "-" for r in L}))) for k, L in sorted(g.items())]
    out.append("### Ek ön sensör ölü (kafa kafaya, orta hattan)\n\n" + tablo(("yerleşim", "arıza", "sahne", "koşu", "düştü", "tetik", "neden"), T))
    out.append("Koşu: %d, hata %d." % (len(R), sum(1 for r in R if r.get("hata"))))
    return "\n\n".join(out)


def sinama2():
    R = oku("sinama2")
    out = [sinama("sinama2"), _dar_tablo(R, "Sınama (tohum 101-105)")]
    ya = [r for r in R if r["alt"] == "yanlis_alarm_yeni"]
    g = collections.defaultdict(list)
    for r in ya:
        g[r["sahne"]].append(r)
    out.append("### Yanlış alarm, yeni sahneler (sınama)\n\n" + tablo(("sahne", "koşu", "yanlış durma"),
                                                                    [(s, len(L), sum(1 for r in L if boolv(r["tetik"]))) for s, L in g.items()]))
    return "\n\n".join(out)


def main():
    istek = sys.argv[1:] or ["durma", "denetim", "rampa_ayrinti", "denetim2", "gelistirme", "gelistirme2", "kusur", "sinama", "sinama_y",
                             "dar_gelistirme", "sinama2"]
    parca = []
    for a in istek:
        f = globals()[a]
        try:
            parca.append("## %s\n\n%s" % (a, f()))
        except Exception as h:
            parca.append("## %s\n\n(hata: %s)" % (a, h))
    metin = "\n\n".join(parca) + "\n"
    with open(os.path.join(SONUC, "tablolar.md"), "w", encoding="utf-8") as f:
        f.write("# Uçurum deneyi: üretilen tablolar (analiz.py)\n\n" + metin)
    sys.stdout.reconfigure(encoding="utf-8")
    print(metin)


if __name__ == "__main__":
    main()
