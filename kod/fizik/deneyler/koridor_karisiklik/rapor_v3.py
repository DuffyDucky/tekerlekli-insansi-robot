"""rapor.html'nin en baştaki bölümü: güncel durum (v3), v1 → v2 → v3 tarihçesi, dört sürümün karşılaştırması, 360° görüş.

rapor.py çağırır. Bütün sayılar sonuc_v3/karsilastirma.json'dan (karsilastir.py) okunur; metinlerdeki sayılar da buradan
biçimlenir, elle yazılmaz. İki hata türü hep ayrı verilir: "yanlış koridora kesin" (konumlayıcı kararsız değil, seçtiği
koridor yanlış) ve "doğru koridorda yanlış yer" (koridor doğru, konum da kesin, ama poz 0,5 m'den fazla yanlış).
"""

import json
import os

BURASI = os.path.dirname(os.path.abspath(__file__))
K = ["koridor_%d" % i for i in range(1, 7)]
KS = {k: "K%d" % (i + 1) for i, k in enumerate(K)}
SV = ["v1", "v2", "v3", "v3_360"]                 # ana karşılaştırma
SAD = {"v1": "v1", "v2": "v2", "v2_360": "v2-360", "v3": "v3", "v3_360": "v3-360"}
BAS_AD = {"bas": "başlangıç ucu", "son": "öbür uç", "orta": "ortadan"}


def yukle():
    yol = os.path.join(BURASI, "sonuc_v3", "karsilastirma.json")
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def tr(v, b=1, bos="–"):
    if v is None:
        return bos
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v)
    return ("%." + str(b) + "f") % v if b else "%d" % round(v)


def t(v, b=1, bos="–"):
    return tr(v, b, bos).replace(".", ",")


def yz(a, n, b=0):
    return "–" if not n else "%%%s" % t(100.0 * a / n, b)


def renk(v, iyi=0):
    return '<span class="ok">%s</span>' % v if v == iyi else '<span class="no">%s</span>' % v


def tablo(baslik, satirlar, sinif="say", min_w=0):
    h = "".join("<th>%s</th>" % b for b in baslik)
    g = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in s) for s in satirlar)
    st = ' style="min-width:%dpx"' % min_w if min_w else ""
    return '<div class="tw"><table class="%s"%s><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (sinif, st, h, g)


def u_atlama(o):
    """U dönüşü sırasında ya da en çok 3 m sonra pozun 180° ters dönmesi (karsilastir.u_atlama ile aynı)."""
    return (o["u_donusu"] == "sirasinda" or (o["u_donusu"] == "sonra" and o["u_sonrasi_yol_m"] <= 3.0)) \
        and (o["ilk_yon_farki_derece"] or 0) > 150


def kosu_adim(kosu, adim):
    return renk(0) if not adim else '<span class="no">%d koşu / %d adım</span>' % (kosu, adim)


# ------------------------------------------------------------------ özet sayılar
def sayilar(S):
    Z = {}
    for s in ("v1", "v2", "v2_360", "v3", "v3_360"):
        ol = S[s]["olaylar"]
        D = S[s]["D"]["koridor"]
        bc = S[s]["B"]["benzer_cift"]
        Z[s] = dict(
            a=S[s]["A"]["toplam"], n=S[s]["B"]["n"] + S[s]["C"]["n"],
            kor_kosu=sum(1 for o in ol if o["koridor_adim"]), kor_adim=sum(o["koridor_adim"] for o in ol),
            yer_kosu=sum(1 for o in ol if o["konum_adim"]), yer_adim=sum(o["konum_adim"] for o in ol),
            iki=sum(1 for o in ol if o["koridor_adim"] and o["konum_adim"]), toplam=len(ol),
            kor_b=sum(1 for o in ol if o["koridor_adim"] and o["bolum"] == "B"),
            kor_c=sum(1 for o in ol if o["koridor_adim"] and o["bolum"] == "C"),
            yer_b=sum(1 for o in ol if o["konum_adim"] and o["bolum"] == "B"),
            yer_c=sum(1 for o in ol if o["konum_adim"] and o["bolum"] == "C"),
            u_at=sum(1 for o in ol if u_atlama(o)), u_n=sum(S[s]["u_donuslu_kosu"].values()),
            cift_once=sum(x["once_karar"] for x in bc.values()), cift_n=sum(x["n"] for x in bc.values()),
            cift_yanlis=sum(1 for o in ol if o["bolum"] == "B" and o["neden"].startswith("benzer çift")),
            d_il=100 * max(v["kk_ileri_max"] for v in D.values()), d_yan=100 * max(v["kk_yan_max"] for v in D.values()),
            d_il_ort=100 * sum(v["kk_ileri_ort"] for v in D.values()) / len(D),
            son_dogru=sum(v["son_dogru"] for b in "BC" for v in S[s][b]["koridor"].values()),
            k1_max=S[s]["B"]["koridor"]["koridor_1"]["konum_karar_max"],
            k1_med=S[s]["B"]["koridor"]["koridor_1"]["konum_karar_med"])
    return Z


def tani_ozet(T):
    if not T:
        return None
    return dict(yanlis=T["koridor_5"]["yanlis_tohum"] + T["koridor_6"]["yanlis_tohum"],
                n=T["koridor_5"]["n"] + T["koridor_6"]["n"], ikiz=T["ikiz"]["kesin_tohum"], ikiz_n=T["ikiz"]["n"],
                ikiz_p=T["ikiz"]["p_max"])


# ------------------------------------------------------------------ tablolar
def tablo_surumler():
    sat = [
        ["<b>v1</b>", "düzeltme öncesi konumlayıcı (commit c34618b); raporun ilk sürümü", "kör sektör var",
         "<code>ham/</code>, <code>sonuc/</code>, <code>gorsel/</code> (tarihçe)"],
        ["<b>v2</b>", "harita olasılığı ölçüm kanıtından (uyum araması + çapraz tohum + %5 çapraz enjeksiyon), çok haritada "
         "<code>baslat_poz</code>, kör sektör maskesi sensörle aynı, işlenmeyen taramada poz odometriyle ilerletiliyor",
         "kör sektör var", "<code>ham_v2/</code>, <code>sonuc_v2/</code>, <code>gorsel_v2/</code> (commit 46a8314)"],
        ["<b>v3</b>", "v2 + çapraz enjeksiyon kaldırıldı (çapraz tohum yalnız harita kanıtında) + odometri artımı arka "
         "çeker dingilden gövde merkezine çevriliyor (<code>odometri_noktasi_x</code> = −0,185 m); varsayılan ayarlar",
         "kör sektör var", "<code>ham_v3/</code>, <code>sonuc_v3/</code>, <code>gorsel_v3/</code>; tam kayıt "
         "<code>akis/</code>"],
        ["<b>v3-360</b> (ve v2-360)", "v3 (v2) ile aynı konumlayıcı",
         "kör sektör yok: LiDAR her yöne görüyor, gövde ışını kesmiyor (VARSAYIM; üst sınır)",
         "<code>ham_v3_360/</code>, <code>sonuc_v3_360/</code>, <code>gorsel_v3_360/</code>"],
    ]
    return tablo(["Sürüm", "Konumlayıcı", "LiDAR görüşü", "Dosyalar"], sat, sinif="", min_w=860)


def tablo_ozet(S, Z):
    """Dört sürümün tek bakışta karşılaştırması (iki hata türü ayrı)."""
    T = {s: tani_ozet(S[s]["tani"]) for s in SV}
    sat = [
        ["A: durağan tek taramada doğru / kararsız / yanlış (216 poz)"] +
        ["%d / %d / %s" % (Z[s]["a"]["dogru"], Z[s]["a"]["kararsiz"], renk(Z[s]["a"]["yanlis"])) for s in SV],
        ["B + C (%d koşu): <b>yanlış koridora kesin karar</b>, koşu / adım" % Z["v3"]["n"]] +
        [kosu_adim(Z[s]["kor_kosu"], Z[s]["kor_adim"]) for s in SV],
        ["B + C: <b>doğru koridorda kesin ama > 0,5 m yanlış yer</b>, koşu / adım"] +
        [kosu_adim(Z[s]["yer_kosu"], Z[s]["yer_adim"]) for s in SV],
        ["iki hatadan en az biri olan koşu (ikisi birden)"] +
        ["%s (%d)" % (renk(Z[s]["toplam"]), Z[s]["iki"]) for s in SV],
        ["U dönüşünde poz çevrilmesi (U dönüşlü koşu)"] +
        ["%s / %d" % (renk(Z[s]["u_at"]), Z[s]["u_n"]) for s in SV],
        ["benzer çift (B): farkı ışınlarında görmeden karar veren koşu"] +
        ["%s / %d" % (renk(Z[s]["cift_once"]), Z[s]["cift_n"]) for s in SV],
        ["B + C: sonda doğru koridor ve kararlı"] + ["%d / %d" % (Z[s]["son_dogru"], Z[s]["n"]) for s in SV],
        ["K1: koridorun neresinde olduğu kesinleşene kadar yol, ortanca / en çok m"] +
        ["%s / %s" % (t(Z[s]["k1_med"], 2), t(Z[s]["k1_max"], 1)) for s in SV],
        ["D: ileri-geri hata, koridor ortalaması / en çok cm"] +
        ["%s / %s" % (t(Z[s]["d_il_ort"]), t(Z[s]["d_il"])) for s in SV],
        ["D: yan hata en çok cm"] + [t(Z[s]["d_yan"]) for s in SV],
        ["tanı: aynı kayıtta yanlışa kesin tohum; ikiz haritada 'kesin' diyen tohum"] +
        [("%s / %d; %s / %d" % (renk(T[s]["yanlis"]), T[s]["n"], renk(T[s]["ikiz"]), T[s]["ikiz_n"])) if T[s] else "–"
         for s in SV],
    ]
    return tablo(["Ölçü"] + [SAD[s] for s in SV], sat, min_w=900)


def tablo_a(S):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            o = S[s]["A"]["oranlar"][k]
            r.append("%d / %d / %s" % (o["dogru"], o["kararsiz"], renk(o["yanlis"])))
        sat.append(r)
    r = ["<b>toplam</b>"]
    for s in SV:
        o = S[s]["A"]["toplam"]
        r.append("<b>%d / %d / %s</b>" % (o["dogru"], o["kararsiz"], renk(o["yanlis"])))
    sat.append(r)
    r = ["benzer çift yoğun set (K5 + K6, 92 poz)"]
    for s in SV:
        y = S[s]["A"]["yogun"]
        r.append("%d / %d / %s" % (sum(y[k]["dogru"] for k in y), sum(y[k]["kararsiz"] for k in y),
                                   renk(sum(y[k]["yanlis"] for k in y))))
    sat.append(r)
    return tablo(["Koridor (36 poz)"] + ["%s: D / K / Y" % SAD[s] for s in SV], sat, min_w=720)


def tablo_b_hata(S, bol="B"):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            v = S[s][bol]["koridor"][k]
            r.append(kosu_adim(v["yanlis_kosu"], v["yanlis_adim"]))
        for s in SV:
            ol = [o for o in S[s]["olaylar"] if o["bolum"] == bol and o["kor"] == k and o["konum_adim"]]
            r.append(kosu_adim(len(ol), sum(o["konum_adim"] for o in ol)))
        sat.append(r)
    return tablo(["Koridor"] + ["yanlış koridora kesin, %s" % SAD[s] for s in SV] +
                 ["doğru koridorda yanlış yer, %s" % SAD[s] for s in SV], sat, min_w=1350)


def tablo_karar(S):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            v = S[s]["B"]["koridor"][k]
            r.append("%s (%s–%s)%s" % (t(v["karar_med"], 2), t(v["karar_min"], 2), t(v["karar_max"], 2),
                                       " · %d koşuda yok" % v["karar_yok"] if v["karar_yok"] else ""))
        for s in SV:
            v = S[s]["B"]["koridor"][k]
            r.append("%s / %s%s" % (t(v["konum_karar_med"], 2), t(v["konum_karar_max"], 2),
                                    " · %d koşuda yok" % v["konum_karar_yok"] if v["konum_karar_yok"] else ""))
        for s in SV:
            v = S[s]["B"]["koridor"][k]
            r.append(yz(v["kararsiz_adim"], v["adim"], 1))
        sat.append(r)
    return tablo(["Koridor"] + ["doğru karara kadar yol m, %s: ortanca (en az–en çok)" % SAD[s] for s in SV] +
                 ["koridorun neresi kesinleşene kadar yol m, %s: ortanca / en çok" % SAD[s] for s in SV] +
                 ["kararsız adım, %s" % SAD[s] for s in SV], sat, min_w=1700)


def tablo_cift(S):
    sat = []
    for kor in ("koridor_5", "koridor_6"):
        for b in ("bas", "son", "orta"):
            key = "%s_%s" % (kor, b)
            r = ["<b>%s</b> · %s" % (KS[kor], BAS_AD[b])]
            for s in ("v3", "v3_360"):
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append(t(x["fark_60"]["med"], 1) if x and x["fark_60"] else "–")
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append("–" if not x or not x["karar"] else "%s (%s–%s)%s" % (
                    t(x["karar"]["med"], 1), t(x["karar"]["min"], 1), t(x["karar"]["max"], 1),
                    " · %d yok" % x["karar_yok"] if x["karar_yok"] else ""))
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append("%s / %d" % (renk(x["once_karar"]), x["n"]) if x else "–")
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append(t(x["p_es_max"], 2) if x else "–")
            sat.append(r)
    return tablo(["gerçek · başlangıç", "fark konumlayıcının ışınlarında görünür, yol m: v3 (ortanca)", "v3-360"] +
                 ["karar yolu m, %s: ortanca (aralık)" % SAD[s] for s in SV] +
                 ["farkı görmeden karar veren koşu, %s" % SAD[s] for s in SV] +
                 ["eşin en büyük p, %s" % SAD[s] for s in SV], sat, min_w=1800)


def tablo_u(S, Z):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            n = sum(1 for o in S[s]["olaylar"] if o["kor"] == k and u_atlama(o))
            r.append("%s / 6" % renk(n))
        sat.append(r)
    sat.append(["<b>toplam</b>"] + ["<b>%s / %d</b>" % (renk(Z[s]["u_at"]), Z[s]["u_n"]) for s in SV])
    return tablo(["Koridor (5 B + 1 C koşusu ortadan başlar, U dönüşü yapar)"] + [SAD[s] for s in SV], sat, min_w=640)


def tablo_tani_u(S):
    T = S.get("tani_donus_v3")
    if not T:
        return ""
    ks = T["kosular"]
    cev = [x for x in ks if x["cevrilme_adim"]]
    return tablo(["v3, U dönüşlü %d kayıt × 3 konumlayıcı tohumu (yeniden besleme)" % T["kayit_sayisi"], "değer"], [
        ["poz çevrilen koşu", "%s / %d" % (renk(T["cevrilen"]), T["kosu"])],
        ["çevrilme adımı (toplam)", str(sum(x["cevrilme_adim"] for x in ks))],
        ["çevrilen koşular", ", ".join("%s (tohum %d, %s m)" % (x["id"], x["tohum"], t(x["ilk_yol"], 1)) for x in cev) or "–"],
        ["yanlış koridora kesin karar olan koşu", "%s / %d" % (renk(T["yanlis_koridor_kosu"]), T["kosu"])],
        ["sonda doğru ve kararlı", "%d / %d" % (T["son_dogru"], T["kosu"])],
    ], sinif="", min_w=620)


def _c_hucre(x):
    if x is None:
        return "–"
    son = {"dogru": "", "kararsiz": ' <span class="uy">kararsız bitti</span>',
           "yanlis": ' <span class="no">yanlış bitti</span>'}.get(x["son_durum"], " " + x["son_durum"])
    k = renk(x["koridor_adim"])
    y = renk(x["yer_adim"])
    return "%s / %s%s" % (k, y, son)


def tablo_c(S):
    ids = [x["id"] for x in S["v3"]["C_kosular"]]
    by = {s: {x["id"]: x for x in S[s]["C_kosular"]} for s in SV}
    sat = []
    for i in ids:
        x3 = by["v3"][i]
        sat.append(["%s" % i, KS[x3["kor"]], BAS_AD[x3["baslangic"]]] + [_c_hucre(by[s].get(i)) for s in SV] +
                   [t(by[s][i]["karar_yol"], 1) if i in by[s] else "–" for s in SV])
    return tablo(["koşu", "gerçek", "başlangıç"] +
                 ["%s: yanlış koridor / yanlış yer (adım)" % SAD[s] for s in SV] +
                 ["karar yolu m, %s" % SAD[s] for s in SV], sat, min_w=1500)


def tablo_d(S):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            v = S[s]["D"]["koridor"][k]
            r.append("%s / %s" % (t(100 * v["kk_ileri_ort"], 1), t(100 * v["kk_ileri_max"], 1)))
        for s in SV:
            v = S[s]["D"]["koridor"][k]
            r.append("%s / %s" % (t(100 * v["kk_yan_ort"], 1), t(100 * v["kk_yan_max"], 1)))
        sat.append(r)
    r = ["yanlış koridor adımı / kararsız konum adımı (18 koşu)"]
    for s in SV:
        D = S[s]["D"]
        r.append("%s / %s" % (renk(D["yanlis_koridor_adim"]), renk(D["konum_kararsiz_adim"])))
    sat.append(r + [""] * len(SV))
    return tablo(["Koridor (3 koşu)"] + ["ileri-geri cm, %s: ort / en çok" % SAD[s] for s in SV] +
                 ["yan cm, %s: ort / en çok" % SAD[s] for s in SV], sat, min_w=1250)


def tablo_tani(S):
    sv = [s for s in ("v1", "v2", "v3") if S[s]["tani"]]
    sat = []
    for kor, ad in (("koridor_6", "K6 kaydı, 6 harita"), ("koridor_5", "K5 kaydı, 6 harita")):
        r = [ad]
        for s in sv:
            x = S[s]["tani"][kor]
            r.append("%s / %d tohum yanlışa kesin (%d adım); eşin en büyük p %s"
                     % (renk(x["yanlis_tohum"]), x["n"], x["yanlis_adim"], t(x["es_max"], 2)))
        sat.append(r)
    r = ["birebir aynı iki harita"]
    for s in sv:
        x = S[s]["tani"]["ikiz"]
        r.append("%s / %d tohum 'kesin' dedi (%d / %d adım); en büyük p %s"
                 % (renk(x["kesin_tohum"]), x["n"], x["kesin_adim"], x["adim"], t(x["p_max"], 2)))
    sat.append(r)
    return tablo(["Tanı (aynı kayıt, 10 konumlayıcı tohumu)"] + [SAD[s] for s in sv], sat, sinif="", min_w=980)


def tablo_olaylar(S, s):
    sat = []
    for o in S[s]["olaylar"]:
        kk = ("%d adım, %s–%s m → %s" % (o["koridor_adim"], t(o["koridor_yol"][0]), t(o["koridor_yol"][1]),
                                         ", ".join(KS[h] for h in o["haritalar"]))) if o["koridor_adim"] else renk(0)
        kp = ("%d adım, %s–%s m" % (o["konum_adim"], t(o["konum_yol"][0]), t(o["konum_yol"][1]))) if o["konum_adim"] else renk(0)
        if o["son_harita"] != o["kor"]:
            son = '<span class="no">%s sanarak bitti</span>' % KS[o["son_harita"]]
        elif o["son_hata_m"] is not None and o["son_hata_m"] > 0.5:
            son = '<span class="no">doğru koridor, %s m hatayla bitti</span>' % t(o["son_hata_m"])
        else:
            son = '<span class="ok">düzeldi</span>'
        u = {"sirasinda": "sırasında", "sonra": "%s m sonra" % t(o["u_sonrasi_yol_m"]), "yok": "–"}[o["u_donusu"]]
        ins = "–" if not o["insan"] else "%s m, %s" % (t(o.get("insan_uzaklik_m"), 1),
                                                          "önde" if o.get("insan_onde") else "arkada")
        fb = o.get("insan_fark_bolgesinde")
        if fb:
            ins += "; %s m ötedeki insan sanılan haritada fark bölgesine düşüyor (x %s)" % (t(fb["menzil_m"], 1), t(fb["x"], 1))
        sat.append([o["id"], KS[o["kor"]], kk, kp, t(o["ilk_hata_m"], 1), t(o["ilk_yon_farki_derece"], 0), u, ins, son,
                    o["neden"]])
    if not sat:
        return '<p class="ok">Kesin yanlış koşu yok.</p>'
    return tablo(["koşu", "gerçek", "yanlış koridora kesin: adım, yol → sanılan",
                  "doğru koridorda yanlış yer: adım, yol", "ilk kötü adımda hata m", "yön farkı °", "U dönüşü",
                  "ilk kötü adımda en yakın insan", "sonda", "gözlenen neden"], sat, min_w=1650)


def tablo_360(S, a="v3", b="v3_360"):
    sat = []
    for k in K:
        b2, b3 = S[a]["B"]["koridor"][k], S[b]["B"]["koridor"][k]
        d2, d3 = S[a]["D"]["koridor"][k], S[b]["D"]["koridor"][k]
        a2, a3 = S[a]["A"]["oranlar"][k], S[b]["A"]["oranlar"][k]
        sat.append(["<b>%s</b>" % KS[k],
                    "%d → %d" % (a2["dogru"], a3["dogru"]),
                    "%s → %s" % (t(b2["karar_med"], 2), t(b3["karar_med"], 2)),
                    "%s → %s" % (t(b2["karar_max"], 2), t(b3["karar_max"], 2)),
                    "%s → %s" % (t(b2["konum_karar_med"], 2), t(b3["konum_karar_med"], 2)),
                    "%s → %s" % (t(b2["konum_karar_max"], 2), t(b3["konum_karar_max"], 2)),
                    "%s → %s" % (yz(b2["kararsiz_adim"], b2["adim"], 1), yz(b3["kararsiz_adim"], b3["adim"], 1)),
                    "%s → %s" % (t(100 * d2["kk_ileri_max"], 1), t(100 * d3["kk_ileri_max"], 1)),
                    "%s → %s" % (t(100 * d2["kk_yan_max"], 1), t(100 * d3["kk_yan_max"], 1))])
    return tablo(["Koridor (%s → %s)" % (SAD[a], SAD[b]), "A doğru (36 poz)", "B doğru karar yolu ortanca m",
                  "B karar yolu en çok m", "B neresi kesinleşir: ortanca m", "B neresi kesinleşir: en çok m",
                  "B kararsız adım", "D ileri-geri en çok cm", "D yan en çok cm"], sat, min_w=1250)


# ------------------------------------------------------------------ metin
TARIHCE_NOTU = ('<div class="env"><b>Bu bölüm tarihçedir.</b> Aşağıdaki 1–11. bölümler raporun ilk sürümüdür (v1, düzeltme '
                "öncesi konumlayıcı). Konumlayıcıdaki hatalar bu deneyle bulundu (4. bölüm tanı, 10. bölüm); v2 ve v3'te "
                "düzeltildiler, güncel sayılar yukarıdadır. v1 sayıları <code>sonuc/</code> ve <code>gorsel/</code> "
                "dosyalarındandır, değiştirilmedi.</div>")


def _kotulesen(S, Z, a, b):
    """a -> b geçişinde kötüleşen ölçüler (veriden)."""
    out = []
    if Z[b]["kor_kosu"] > Z[a]["kor_kosu"]:
        out.append("yanlış koridora kesin %d → %d koşu" % (Z[a]["kor_kosu"], Z[b]["kor_kosu"]))
    if Z[b]["yer_kosu"] > Z[a]["yer_kosu"]:
        out.append("doğru koridorda yanlış yer %d → %d koşu" % (Z[a]["yer_kosu"], Z[b]["yer_kosu"]))
    if Z[b]["u_at"] > Z[a]["u_at"]:
        out.append("U dönüşünde poz çevrilmesi %d → %d / %d koşu" % (Z[a]["u_at"], Z[b]["u_at"], Z[b]["u_n"]))
    if Z[b]["a"]["dogru"] < Z[a]["a"]["dogru"]:
        out.append("A doğru %d → %d poz" % (Z[a]["a"]["dogru"], Z[b]["a"]["dogru"]))
    if Z[b]["d_il"] > Z[a]["d_il"] + 0.5:
        out.append("D ileri-geri en çok %s → %s cm" % (t(Z[a]["d_il"]), t(Z[b]["d_il"])))
    for k in K:
        x, y = S[a]["B"]["koridor"][k]["karar_med"], S[b]["B"]["koridor"][k]["karar_med"]
        if x is not None and y is not None and y > x + 0.5:
            out.append("%s B karar yolu ortancası %s → %s m" % (KS[k], t(x, 2), t(y, 2)))
    return out


def _iyilesen(S, Z, a, b):
    out = []
    for ad, anah in (("yanlış koridora kesin", "kor_kosu"), ("doğru koridorda yanlış yer", "yer_kosu")):
        if Z[b][anah] < Z[a][anah]:
            out.append("%s %d → %d koşu" % (ad, Z[a][anah], Z[b][anah]))
    if Z[b]["u_at"] < Z[a]["u_at"]:
        out.append("U dönüşünde poz çevrilmesi %d → %d / %d koşu" % (Z[a]["u_at"], Z[b]["u_at"], Z[b]["u_n"]))
    if Z[b]["cift_once"] < Z[a]["cift_once"]:
        out.append("benzer çiftte farkı görmeden karar %d → %d / %d koşu" % (Z[a]["cift_once"], Z[b]["cift_once"],
                                                                           Z[b]["cift_n"]))
    Ta, Tb = tani_ozet(S[a]["tani"]), tani_ozet(S[b]["tani"])
    if Ta and Tb and (Tb["yanlis"] < Ta["yanlis"] or Tb["ikiz"] < Ta["ikiz"]):
        out.append("tanıda yanlışa kesin tohum %d → %d / %d, ikiz haritada 'kesin' %d → %d / %d"
                   % (Ta["yanlis"], Tb["yanlis"], Tb["n"], Ta["ikiz"], Tb["ikiz"], Tb["ikiz_n"]))
    if Z[b]["d_il_ort"] < Z[a]["d_il_ort"] - 0.1:
        out.append("D ileri-geri ortalama %s → %s cm" % (t(Z[a]["d_il_ort"]), t(Z[b]["d_il_ort"])))
    return out


def tablo_tarihce(S, Z):
    sat = [
        ["<b>v1 → v2</b>", "harita olasılığı ölçüm kanıtından; çok haritada <code>baslat_poz</code>; kör sektör maskesi "
         "sensörle aynı; işlenmeyen taramada poz odometriyle ilerletiliyor",
         "; ".join(_iyilesen(S, Z, "v1", "v2")) or "–",
         '<span class="no">%s</span>' % ("; ".join(_kotulesen(S, Z, "v1", "v2")) or "ölçülen ölçütlerde kötüleşme yok")],
        ["<b>v2 → v3</b>", "çapraz enjeksiyon kaldırıldı (simetrik taramada ayna poza önsel desteği olmadan parçacık "
         "taşınıyordu); odometri artımı arka çeker dingilden gövde merkezine çevriliyor",
         "; ".join(_iyilesen(S, Z, "v2", "v3")) or "–",
         ('<span class="no">%s</span>' % "; ".join(_kotulesen(S, Z, "v2", "v3"))) if _kotulesen(S, Z, "v2", "v3")
         else '<span class="ok">ölçülen ölçütlerde kötüleşme yok</span>'],
    ]
    return tablo(["Geçiş", "Konumlayıcıda ne değişti", "Neyi çözdü (aynı veri)", "Neyi bozdu"], sat, sinif="", min_w=980)


def html(S, img):
    Z = sayilar(S)
    E3 = S["v1_esitlik_v3"]
    OD = S.get("odometri_noktasi")
    TU = S.get("tani_donus_v3")
    v1, v2, v3, v4 = Z["v1"], Z["v2"], Z["v3"], Z["v3_360"]
    T1, T2, T3 = tani_ozet(S["v1"]["tani"]), tani_ozet(S["v2"]["tani"]), tani_ozet(S["v3"]["tani"])
    ol3 = S["v3"]["olaylar"]
    h = []
    h.append('<h2 id="v3">Güncel durum (v3)</h2>')
    h.append('<div class="env"><b>Okurken:</b> <b>v1</b> = düzeltme öncesi konumlayıcı, <b>v2</b> = ilk düzeltme, '
             "<b>v3</b> = v2 + U dönüşü düzeltmesi, <b>-360</b> = aynı konumlayıcı, LiDAR'da kör sektör yok. Hepsi aynı "
             "sürüşleri, aynı tohumları ve aynı taramaları kullanır; konumlayıcı her sürümde varsayılan ayarlarla. İki hata "
             'türü ayrı sayılır: <b>yanlış koridora kesin</b> = konumlayıcı kararsız değil ama seçtiği koridor yanlış; '
             "<b>doğru koridorda yanlış yer</b> = koridor doğru, konum da kesin, ama poz 0,5 m'den fazla yanlış.</div>")
    kp = [
        ("Yanlış koridora kesin karar, B + C (%d koşu)" % v3["n"],
         "%d → %d → %d" % (v1["kor_kosu"], v2["kor_kosu"], v3["kor_kosu"]),
         "koşu, v1 → v2 → v3; adım %d → %d → %d" % (v1["kor_adim"], v2["kor_adim"], v3["kor_adim"])),
        ("Doğru koridorda kesin ama yanlış yer", "%d → %d → %d" % (v1["yer_kosu"], v2["yer_kosu"], v3["yer_kosu"]),
         "koşu; adım %d → %d → %d" % (v1["yer_adim"], v2["yer_adim"], v3["yer_adim"])),
        ("U dönüşünde poz çevrilmesi", "%d → %d → %d" % (v1["u_at"], v2["u_at"], v3["u_at"]),
         "/ %d U dönüşlü koşu%s" % (v3["u_n"], ("; tanı (3 tohum): %d / %d" % (TU["cevrilen"], TU["kosu"])) if TU else "")),
        ("Benzer çift: farkı görmeden karar (B)", "%d → %d → %d" % (v1["cift_once"], v2["cift_once"], v3["cift_once"]),
         "/ %d koşu; tanıda yanlışa kesin tohum %d → %d → %s / %d" % (
             v3["cift_n"], T1["yanlis"], T2["yanlis"], T3["yanlis"] if T3 else "–", T1["n"])),
        ("D: ileri-geri hata, ortalama / en çok", "%s / %s cm" % (t(v3["d_il_ort"]), t(v3["d_il"])),
         "v3; v1 %s / %s, v2 %s / %s" % (t(v1["d_il_ort"]), t(v1["d_il"]), t(v2["d_il_ort"]), t(v2["d_il"]))),
    ]
    h.append('<div class="k">')
    for a, b, c in kp:
        h.append('<div class="kpi"><span>%s</span><b>%s</b><span>%s</span></div>' % (a, b, c))
    h.append("</div>")

    # kalan v3 yanılgıları
    kalan = []
    for o in ol3:
        tur = []
        if o["koridor_adim"]:
            tur.append("%d adım %s sanıldı" % (o["koridor_adim"], ", ".join(KS[x] for x in o["haritalar"])))
        if o["konum_adim"]:
            tur.append("%d adım doğru koridorda yanlış yer" % o["konum_adim"])
        ins = (", en yakın insan %s m %s" % (t(o["insan_uzaklik_m"], 1), "önde" if o["insan_onde"] else "arkada")) \
            if o["insan"] else ""
        tk = [x for x in (TU or {}).get("kosular", []) if x["id"] == o["id"]]
        fb = o.get("insan_fark_bolgesinde")
        if fb:
            ins += ("; %s m ötedeki insan sanılan pozdan bakınca K6'nın fark bölgesine (yangın dolabı, x %s) düşüyor: "
                    "insan haritadaki farkı taklit ediyor" % (t(fb["menzil_m"], 1), t(fb["x"], 1)))
        elif o["insan"]:
            ins += "; hiçbir insan sanılan haritada benzer çiftin fark bölgesine düşmüyor, neden bu kayıtta belirlenmedi"
        tohum = ("; aynı kayıt 3 konumlayıcı tohumuyla: %d / %d tohumda yanlış koridora kesin"
                 % (sum(1 for x in tk if x["yanlis_koridor_adim"]), len(tk))) if tk else ""
        kalan.append("<code>%s</code> (%s; %s%s%s)" % (o["id"], "; ".join(tur), o["neden"], ins, tohum))
    madde = [
        "<b>U dönüşü hatası çözüldü.</b> U dönüşlü %d koşuda poz çevrilmesi v2'de %d, v3'te %d%s. Doğru koridorda "
        "kesin ama yanlış yer: v2 %d koşu / %d adım → v3 %d koşu / %d adım."
        % (v3["u_n"], v2["u_at"], v3["u_at"],
           ("; aynı 36 kayıt 3 konumlayıcı tohumuyla yeniden beslenince %d / %d" % (TU["cevrilen"], TU["kosu"])) if TU else "",
           v2["yer_kosu"], v2["yer_adim"], v3["yer_kosu"], v3["yer_adim"]),
        "<b>v2'nin kazançları korunuyor.</b> Benzer çiftte farkı ışınlarında görmeden karar veren koşu %d / %d (v1 %d); "
        "tanıda yanlışa kesin tohum %s / %d (v1 %d), ikiz haritada 'kesin' diyen tohum %s / %d (en büyük p %s). D'de "
        "ileri-geri hata ortalama %s cm, en çok %s cm; yan en çok %s cm."
        % (v3["cift_once"], v3["cift_n"], v1["cift_once"], T3["yanlis"] if T3 else "–", T1["n"], T1["yanlis"],
           T3["ikiz"] if T3 else "–", T1["ikiz_n"], t(T3["ikiz_p"], 2) if T3 else "–",
           t(v3["d_il_ort"]), t(v3["d_il"]), t(v3["d_yan"])),
        '<b class="%s">v3\'te kalan kesin yanılgı: %d koşu</b> (yanlış koridora kesin %d koşu / %d adım; doğru '
        "koridorda yanlış yer %d koşu / %d adım). %s"
        % ("no" if v3["toplam"] else "ok", v3["toplam"], v3["kor_kosu"], v3["kor_adim"], v3["yer_kosu"], v3["yer_adim"],
           ("Tek tek: " + "; ".join(kalan) + ".") if kalan else ""),
        "<b>A (durağan tek tarama)</b> konumlayıcı değişikliğinden etkilenmiyor: doğru %d, kararsız %d, kendinden emin "
        "yanlış %d (v2: %d / %d / %d)." % (v3["a"]["dogru"], v3["a"]["kararsiz"], v3["a"]["yanlis"], v2["a"]["dogru"],
                                           v2["a"]["kararsiz"], v2["a"]["yanlis"]),
        "<b>360° görüş (v3-360)</b>: yanlış koridora kesin %d koşu, yanlış yer %d koşu, U dönüşü çevrilmesi %d / %d; "
        "durağan tek taramada doğru %d → %d poz. Ayrıntı aşağıda."
        % (v4["kor_kosu"], v4["yer_kosu"], v4["u_at"], v4["u_n"], v3["a"]["dogru"], v4["a"]["dogru"]),
    ]
    h.append("<h3>Kısa sonuç</h3><ul>%s</ul>" % "".join("<li>%s</li>" % m for m in madde))

    h.append("<h3>Dört sürüm tek bakışta</h3>")
    h.append(tablo_ozet(S, Z))
    h.append('<p class="not">Her hücre aynı 108 B + C koşusundan (D: 18, A: 216 poz) sayıldı. v1 ve v2 sayıları yeniden '
             "koşulmadan, sonuç dosyalarından aynı iki tanımla yeniden sayıldı. U dönüşünü yalnız ortadan başlayan koşular "
             "yapar.</p>")
    h.append("<h3>Tarihçe: hangi düzeltme neyi çözdü, neyi bozdu</h3>")
    h.append(tablo_tarihce(S, Z))

    h.append("<h3>Sürümler ve yöntem</h3>")
    h.append(tablo_surumler())
    kay = E3.get("veri_kaynagi", {})
    h.append('<p class="not">v3: v2\'nin ham kayıtları taramaları saklamadığı için fizik v1 tohumlarıyla yeniden koşuldu ve '
             "bu kez tam kayıt (360° taramalar, enkoder odometrisi, yer gerçeği) <code>akis/</code>'a yazıldı (depoya girmez): "
             "sonraki konumlayıcı sürümleri fizik koşmadan aynı veriyle sınanabilir. Mesafeler 15 mm çözünürlüğün tam katı "
             "olduğundan tamsayı saklanır; her görevde diskten geri okunan kayıt bellektekiyle birebir karşılaştırıldı ve "
             "konumlayıcıya geri okunan verildi. Aynı veri: adım sayısı v1 ile aynı olan hareket koşusu %d / %d, yer gerçeği "
             "yolu en çok %s m farklı, v1'in sakladığı %d taramada ve A'nın %d pozunda farklı ışın %d. Veri kaynağı: %s.</p>"
             % (E3["adim_sayisi_esit"], E3["hareket_kosu"], t(E3["en_buyuk_yol_farki_m"], 1), E3["saklanan_tarama"],
                E3["a_poz"], E3["farkli_isin"] + E3["a_farkli_isin"],
                ", ".join("%s %d koşu" % ({"fizik": "fizik", "yeniden_besleme": "yeniden besleme"}.get(k, k), v)
                          for k, v in sorted(kay.items()))))
    if OD:
        h.append('<div class="bulgu"><b>Odometri noktası denetimi.</b> v3 konumlayıcısı odometri artımını arka çeker '
                 "dingilin ortasında (<code>odometri_noktasi_x</code> = −0,185 m) varsayıp gövde merkezine çevirir. Deneyin "
                 "odometrisi <code>lidar.DeneyKaydi</code>'nde tik toplamından, diferansiyel sürüş formülüyle (ds = (sol + "
                 "sağ) / 2) üretilir: bu çeker dingilin ortasının hareketidir; yer gerçeği taban gövdesinin pozudur. "
                 "<code>odometri_noktasi.py</code> bir U dönüşlü kayıtta (%s, %d dönüş adımı) odometri artımını aday "
                 "noktaların yer gerçeğinden hesaplanan artımıyla karşılaştırdı: en iyi uyan nokta x = %s m; hata "
                 "x = −0,185'te %s mm, gövde merkezinde (x = 0) %s mm. Varsayılan deneyle tutarlı; değiştirilmedi.</div>"
                 % (OD["kayit"], OD["donus_adimi"], t(OD["en_iyi_px_m"], 3), t(1000 * OD["px_eksi_0185"], 1),
                    t(1000 * OD["px_0"], 1)))

    h.append("<h3>A: durağan tek tarama (D / K / Y = doğru / kararsız / kendinden emin yanlış)</h3>")
    h.append(tablo_a(S))
    h.append("<h3>B: iki hata türü, koridor başına (90 koşu)</h3>")
    h.append(tablo_b_hata(S))
    h.append(img("gorsel_v3/karsilastirma_ozet.png", "v1 / v2 / v3 / v3-360: B karar yolu, B konum kararı, iki hata "
                 "türü (adım), D ileri-geri hata, U dönüşünde çevrilme"))
    h.append("<h3>B: karar yolu ve koridorun neresinde</h3>")
    h.append(tablo_karar(S))
    h.append('<p class="not">"Neresi kesinleşir" = konum kararsızlığının son kez bittiği yol. K1\'de en çok değer v1 %s m, '
             "v2 %s m, v3 %s m, v3-360 %s m. v2'deki büyük değer U dönüşü çevrilmesinden sonra konumun yeniden kurulmasını "
             "bekleyen koşudur.</p>" % (t(v1["k1_max"], 1), t(v2["k1_max"], 1), t(v3["k1_max"], 1), t(v4["k1_max"], 1)))
    h.append("<h3>U dönüşü yapan 36 koşuda poz çevrilmesi</h3>")
    h.append(tablo_u(S, Z))
    h.append(tablo_tani_u(S))
    h.append("<h3>Benzer çift (K5 / K6)</h3>")
    h.append(tablo_cift(S))
    h.append(img("gorsel_v3/karsilastirma_benzer_cift.png", "Benzer çift, başlangıç ucundan: doğru koridorun olasılığı, "
                 "dört sürüm (kesikli mor çizgi: fark konumlayıcının ışınlarında görünür, ortanca)"))
    h.append("<h3>C: haritada olmayan 3 insan, koşu koşu (18 koşu)</h3>")
    h.append(tablo_c(S))
    h.append('<p class="not">Hücre: yanlış koridora kesin adım / doğru koridorda yanlış yer adımı; sonda doğru ve kararlı '
             "değilse yazılır.</p>")
    h.append("<h3>D: başlangıç biliniyor (18 koşu)</h3>")
    h.append(tablo_d(S))
    h.append("<h3>Tanı: aynı kayıt, 10 konumlayıcı tohumu</h3>")
    h.append(tablo_tani(S))

    h.append("<h3>v3'te kalan kesin yanılgılar, tek tek</h3>")
    h.append(tablo_olaylar(S, "v3"))
    h.append('<p class="not">"Gözlenen neden" ham adımlardan çıkarılan etikettir: ilk kötü adımda tahmin ile gerçek yön farkı '
             "150°'den büyükse poz ters; U dönüşü yer gerçeğinden; en yakın insan = ilk kötü adımda robot merkezinden insan "
             "silindirinin yüzeyine uzaklık.</p>")
    h.append("<p><b>v3-360</b> (%d koşu)</p>" % len(S["v3_360"]["olaylar"]))
    h.append(tablo_olaylar(S, "v3_360"))
    h.append("<p><b>v2</b> (%d koşu, karşılaştırma için)</p>" % len(S["v2"]["olaylar"]))
    h.append(tablo_olaylar(S, "v2"))
    h.append(img("gorsel_v3/ornek_C_yanlis.png", "v3: insanlı koşuda yanlış koridora kesin kararın ilk adımı"))

    h.append('<h2 id="g360">360° görüş ne kazandırır (v3 → v3-360)</h2>')
    h.append(_g360(S, Z))
    h.append(tablo_360(S, "v3", "v3_360"))
    h.append('<p class="not">Ek: aynı karşılaştırma v2 → v2-360 (önceki konumlayıcı).</p>')
    h.append(tablo_360(S, "v2", "v2_360"))
    return h


def _g360(S, Z, a="v3", b="v3_360", a0="v2", b0="v2_360"):
    KR = S["kor"]
    A2, A3 = S[a]["A"]["oranlar"], S[b]["A"]["oranlar"]
    B2, B3 = S[a]["B"]["koridor"], S[b]["B"]["koridor"]
    a_fark = [(k, A3[k]["dogru"] - A2[k]["dogru"]) for k in K]
    a_fark0 = [(k, S[b0]["A"]["oranlar"][k]["dogru"] - S[a0]["A"]["oranlar"][k]["dogru"]) for k in K]
    a_txt = ", ".join("%s: %+d" % (KS[k], d) for k, d in a_fark if d) or "hiçbir koridorda değişmiyor"
    a_txt0 = ", ".join("%s: %+d" % (KS[k], d) for k, d in a_fark0 if d) or "değişim yok"
    med = [(k, (B3[k]["karar_med"] or 0) - (B2[k]["karar_med"] or 0)) for k in K]
    kotu = max(med, key=lambda x: x[1])
    iyi = min(med, key=lambda x: x[1])
    bc = lambda s, k, f: S[s]["B"]["benzer_cift"][k][f]["med"]  # noqa: E731
    kk = {s: sum(v["kararsiz_adim"] for v in S[s]["B"]["koridor"].values()) /
          sum(v["adim"] for v in S[s]["B"]["koridor"].values()) for s in (a, b, a0, b0)}
    yon0 = (bc(b0, "koridor_6_bas", "karar") - bc(a0, "koridor_6_bas", "karar"))
    yon = (bc(b, "koridor_6_bas", "karar") - bc(a, "koridor_6_bas", "karar"))
    tutarli = (yon > 0) == (yon0 > 0)
    s = []
    s.append('<div class="env">Soru: sensörün %s° kör bölgesi (%s; yazılım maskesi her yana %s° pay ekler) işletmede neye mal '
             "oluyor? Aynı sürüşler %s (kör bölge var) ve %s (yok) ile karşılaştırıldı. Konumlayıcı ikisinde de taramadan "
             "%d ışın kullanır.</div>"
             % (t(KR["genislik"], 1), ", ".join("%s°–%s°" % (t(x, 1), t(y, 1)) for x, y in KR["sektorler"]),
                t(KR["pay"], 0), SAD[a], SAD[b], KR["isin_mcl"]))
    s.append('<div class="bulgu"><b>Bulgu.</b><ul>'
             "<li><b>Durağan tek tarama:</b> kör bölge kalkınca doğru poz sayısındaki değişim (36 pozdan) %s; K5 ve K6'da "
             "iki sürümde de bütün pozlar kararsız (v2'de: %s).</li>"
             "<li><b>Hareket (B):</b> doğru karar yolu ortancasının en çok kısaldığı koridor %s (%s → %s m), en çok uzadığı "
             "koridor %s (%s → %s m). Kararsız adım payı %s → %s (v2 → v2-360: %s → %s).</li>"
             "<li><b>Benzer çift:</b> fark konumlayıcının ışınlarında başlangıç ucundan K6'da %s → %s m'de görünür (500 "
             "ışınlık sık taramada %s → %s m); karar %s → %s m (v2 → v2-360: %s → %s m). Aynı %d ışın daha geniş açıya "
             "yayıldığı için küçük fark bölgesi seyrek ışınlarda daha geç yakalanıyor.</li>"
             "<li><b>İki hata türü:</b> yanlış koridora kesin %d → %d koşu, doğru koridorda yanlış yer %d → %d koşu; U dönüşü "
             "çevrilmesi %d → %d.</li>"
             "<li><b>Konum doğruluğu (D):</b> ileri-geri en çok %s → %s cm, yan en çok %s → %s cm.</li></ul></div>"
             % (a_txt, a_txt0,
                KS[iyi[0]], t(B2[iyi[0]]["karar_med"], 2), t(B3[iyi[0]]["karar_med"], 2),
                KS[kotu[0]], t(B2[kotu[0]]["karar_med"], 2), t(B3[kotu[0]]["karar_med"], 2),
                yz(kk[a], 1, 1), yz(kk[b], 1, 1), yz(kk[a0], 1, 1), yz(kk[b0], 1, 1),
                t(bc(a, "koridor_6_bas", "fark_60")), t(bc(b, "koridor_6_bas", "fark_60")),
                t(bc(a, "koridor_6_bas", "fark_500")), t(bc(b, "koridor_6_bas", "fark_500")),
                t(bc(a, "koridor_6_bas", "karar")), t(bc(b, "koridor_6_bas", "karar")),
                t(bc(a0, "koridor_6_bas", "karar")), t(bc(b0, "koridor_6_bas", "karar")), KR["isin_mcl"],
                Z[a]["kor_kosu"], Z[b]["kor_kosu"], Z[a]["yer_kosu"], Z[b]["yer_kosu"], Z[a]["u_at"], Z[b]["u_at"],
                t(Z[a]["d_il"]), t(Z[b]["d_il"]), t(Z[a]["d_yan"]), t(Z[b]["d_yan"])))
    s.append('<div class="yorum"><b>Yorum.</b> v2\'deki sonuçla %s: kör bölgenin maliyeti durağan tek taramada (%s) ve '
             "birkaç santimetrelik konum doğruluğunda; hareket hâlinde koridor karışıklığı olarak tutarlı bir maliyet "
             "görünmüyor, benzer çiftte 360° görüş aynı ışın bütçesiyle kararı geciktiriyor. 360°'nin kazancı ancak ışın sayısı "
             "açıyla birlikte artırılırsa benzer çiftte görülebilir; ayrı bir koşu kümesiyle denenmeli (burada ayar "
             "yapılmadı). Gövdenin ışını kesmediği varsayımıyla bu bir üst sınırdır.</div>"
             % ("tutarlı" if tutarli else "benzer çift kararının yönü bakımından TUTARSIZ",
                ", ".join(KS[k] for k, d in a_fark if d > 0) or "yok"))
    return "".join(s)


def acik(S):
    Z = sayilar(S)
    ol = S["v3"]["olaylar"]
    insanli = [o for o in ol if o["insan"]]
    m = []
    if Z["v3"]["u_at"]:
        m.append("U dönüşünde poz çevrilmesi v3'te hâlâ var (%d / %d koşu); konumlama modülünde incelenmeli."
                 % (Z["v3"]["u_at"], Z["v3"]["u_n"]))
    if insanli:
        taklit = [o for o in insanli if o.get("insan_fark_bolgesinde")]
        diger = [o for o in insanli if not o.get("insan_fark_bolgesinde")]
        m.append("İnsan haritadaki farkı taklit ediyor: v3'te kalan kesin yanılgıların hepsi insanlı C koşusu (%d koşu). %s%s"
                 "Dinamik engel ayıklama ya da 'fark birden çok taramada, farklı açılardan sürmeli' gibi bir kural ayrı koşu "
                 "kümesiyle denenmeli."
                 % (len(insanli),
                    ("%s: ilk yanlış adımda robotun önündeki insan, sanılan K6 pozundan bakınca K6'nın fark bölgesine "
                     "(yangın dolabı) düşüyor; konumlayıcı insanı dolap sanıyor. " % ", ".join("<code>%s</code>" % o["id"] for o in taklit))
                    if taklit else "",
                    ("%s: hiçbir insan sanılan haritada fark bölgesine düşmüyor; neden belirlenmedi (en yakın insan %s m). "
                     % (", ".join("<code>%s</code>" % o["id"] for o in diger),
                        ", ".join(t(o["insan_uzaklik_m"], 1) for o in diger))) if diger else ""))
    m += [
        "Odometri noktası robota bağlı: <code>odometri_noktasi_x</code> = −0,185 m arka çeker + ön omni (23.11.2026 "
        "kararı) içindir. Çekiş düzeni ya da enkoderin yeri değişirse bu değer güncellenmeli; yanlış eşleşme sonuçları "
        "sessizce bozar (deney için denetim: <code>sonuc_v3/odometri_noktasi.json</code>).",
        "360° görüşte ışın sayısı açıyla artırılırsa benzer çiftte ne kazanılır: ayrı koşu kümesiyle, ayar ve değerlendirme "
        "tohumları ayrı denenmeli. Tam kayıt (<code>akis/</code>) bunu fizik koşmadan mümkün kılıyor.",
        "v3-360 gövdenin ışını kesmediği varsayımına dayanıyor; gerçek bir LiDAR boşluğu tasarımıyla doğrulanmalı.",
        "Hareketli insanlar, cam, koyu yüzey ve eğik zemin denenmedi.",
        "Gerçek RPLIDAR C1 ile gerçek koridor kaydı alınmalı (harita ile bina farkı).",
        "Robot modeli ÖNERİ (dönebilen, öneri firmware + ön omni; VARSAYIM). Bugünkü robot (V0) modelde dönemiyor.",
    ]
    return "<h2>Açık işler</h2><ul>%s</ul>" % "".join("<li>%s</li>" % x for x in m)
