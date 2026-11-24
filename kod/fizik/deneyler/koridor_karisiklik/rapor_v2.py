"""rapor.html'nin v2 bölümü (düzeltme sonrası durum, v1 / v2 / v2-360 karşılaştırması, 360° görüş).

rapor.py çağırır. Bütün sayılar sonuc_v2/karsilastirma.json'dan (karsilastir.py) okunur; metinlerdeki sayılar da
buradan biçimlenir, elle yazılmaz.
"""

import json
import os

BURASI = os.path.dirname(os.path.abspath(__file__))
K = ["koridor_%d" % i for i in range(1, 7)]
KS = {k: "K%d" % (i + 1) for i, k in enumerate(K)}
SV = ["v1", "v2", "v2_360"]
SAD = {"v1": "v1", "v2": "v2", "v2_360": "v2-360"}
BAS_AD = {"bas": "başlangıç ucu", "son": "öbür uç", "orta": "ortadan"}


def yukle():
    yol = os.path.join(BURASI, "sonuc_v2", "karsilastirma.json")
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
    """Kendinden emin yanlış gibi sayaçlar: 0 yeşil, değilse kırmızı."""
    return '<span class="ok">0</span>' if v == iyi else '<span class="no">%s</span>' % v


def tablo(baslik, satirlar, sinif="say", min_w=0):
    h = "".join("<th>%s</th>" % b for b in baslik)
    g = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in s) for s in satirlar)
    st = ' style="min-width:%dpx"' % min_w if min_w else ""
    return '<div class="tw"><table class="%s"%s><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (sinif, st, h, g)


def toplam_yanlis(S, s, bol):
    E = S[s][bol]
    return sum(v["yanlis_adim"] for v in E["koridor"].values()), sum(v["yanlis_kosu"] for v in E["koridor"].values())


def son_say(S, s, bol):
    E = S[s][bol]["koridor"]
    return (sum(v["son_dogru"] for v in E.values()), sum(v["son_kararsiz"] for v in E.values()),
            sum(v["son_yanlis"] for v in E.values()), sum(v["n"] for v in E.values()))


def yanlis_satirlari(S, s, bol):
    return [[x["id"], KS[x["kor"]], BAS_AD[x["baslangic"]], x["tohum"], KS[x["harita"]], x["adim"], t(x["sure_s"]),
             "%s–%s" % (t(x["ilk_yol"]), t(x["son_yol"])), t(x["en_buyuk_p"], 2)] for x in S[s][bol]["yanlislar"]]


# ------------------------------------------------------------------ tablolar
def tablo_surumler():
    sat = [
        ["<b>v1</b>", "düzeltme öncesi konumlayıcı (commit c34618b); bu raporun ilk sürümü",
         "kör sektör var (konumlayıcıda pay 0°)",
         "<code>ham/</code>, <code>sonuc/</code>, <code>gorsel/</code> (tarihçe, yeniden üretilmez)"],
        ["<b>v2</b>", "düzeltilmiş konumlayıcı (harita olasılığı ölçüm kanıtından, çok haritada <code>baslat_poz</code>, "
         "kör sektör maskesi sensörle aynı, işlenmeyen taramada poz odometriyle ilerletiliyor); varsayılan ayarlar",
         "kör sektör var (134,2°–225,8°, sensör ile konumlayıcı aynı)",
         "<code>ham_v2/</code>, <code>sonuc_v2/</code>, <code>gorsel_v2/</code>"],
        ["<b>v2-360</b>", "v2 ile aynı konumlayıcı",
         "kör sektör yok: LiDAR her yöne görüyor, robot gövdesi ışını kesmiyor (VARSAYIM; taban ile gövde arasında açık "
         "bir LiDAR boşluğunun üst sınırı)",
         "<code>ham_v2_360/</code>, <code>sonuc_v2_360/</code>, <code>gorsel_v2_360/</code>"],
    ]
    return tablo(["Sürüm", "Konumlayıcı", "LiDAR görüşü", "Dosyalar"], sat, sinif="", min_w=820)


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
    r = ["doğru haritadaki en iyi poz 0,5 m'den uzak: K1 / bütün koridorlar"]
    for s in SV:
        h = S[s]["A"]["konum_hata_05"]
        r.append("%d / %d" % (h["koridor_1"], sum(h.values())))
    sat.append(r)
    return tablo(["Koridor (36 poz)", "v1: D / K / Y", "v2: D / K / Y", "v2-360: D / K / Y"], sat, min_w=640)


def tablo_b(S, bol="B"):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            v = S[s][bol]["koridor"][k]
            r.append(("%d koşu / %d adım" % (v["yanlis_kosu"], v["yanlis_adim"])) if v["yanlis_adim"] else renk(0))
        for s in SV:
            v = S[s][bol]["koridor"][k]
            r.append("%s (%s–%s)%s" % (t(v["karar_med"], 2), t(v["karar_min"], 2), t(v["karar_max"], 2),
                                       " · %d koşuda yok" % v["karar_yok"] if v["karar_yok"] else ""))
        sat.append(r)
    return tablo(["Koridor"] + ["kendinden emin yanlış, %s" % SAD[s] for s in SV] +
                 ["doğru karara kadar yol m, %s: ortanca (en az–en çok)" % SAD[s] for s in SV], sat, min_w=1150)


def tablo_konum(S, bol="B"):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            v = S[s][bol]["koridor"][k]
            r.append("%s / %s%s" % (t(v["konum_karar_med"], 2), t(v["konum_karar_max"], 2),
                                    " · %d koşuda yok" % v["konum_karar_yok"] if v["konum_karar_yok"] else ""))
        for s in SV:
            v = S[s][bol]["koridor"][k]
            r.append(yz(v["kararsiz_adim"], v["adim"], 1))
        for s in SV:
            v = S[s][bol]["koridor"][k]
            r.append("%d / %d" % (v["son_dogru"], v["n"])
                     + (' <span class="uy">(%d kararsız)</span>' % v["son_kararsiz"] if v["son_kararsiz"] else "")
                     + (' <span class="no">(%d yanlış)</span>' % v["son_yanlis"] if v["son_yanlis"] else ""))
        sat.append(r)
    return tablo(["Koridor"] + ["koridorun neresi kesinleşene kadar yol m, %s: ortanca / en çok" % SAD[s] for s in SV] +
                 ["kararsız adım, %s" % SAD[s] for s in SV] + ["sonda doğru, %s" % SAD[s] for s in SV], sat, min_w=1250)


def tablo_cift(S):
    sat = []
    for kor in ("koridor_5", "koridor_6"):
        for b in ("bas", "son", "orta"):
            key = "%s_%s" % (kor, b)
            r = ["<b>%s</b> · %s" % (KS[kor], BAS_AD[b])]
            for s in ("v2", "v2_360"):
                x1 = S[s]["B"]["benzer_cift"].get(key)
                r.append(t(x1["fark_60"]["med"], 1) if x1 and x1["fark_60"] else "–")
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                if not x or not x["karar"]:
                    r.append("–")
                    continue
                r.append("%s (%s–%s)%s" % (t(x["karar"]["med"], 1), t(x["karar"]["min"], 1), t(x["karar"]["max"], 1),
                                           " · %d yok" % x["karar_yok"] if x["karar_yok"] else ""))
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append("%d / %d" % (x["once_karar"], x["n"]) if x else "–")
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append(("%d koşu / %d adım" % (x["yanlis_kosu"], x["yanlis_adim"]) if x["yanlis_adim"] else renk(0))
                         if x else "–")
            for s in SV:
                x = S[s]["B"]["benzer_cift"].get(key)
                r.append(t(x["p_es_max"], 2) if x else "–")
            sat.append(r)
    return tablo(["gerçek · başlangıç", "fark konumlayıcının ışınlarında görünür, yol m: v2 (ortanca)", "v2-360"] +
                 ["karar yolu m, %s: ortanca (aralık)" % SAD[s] for s in SV] +
                 ["farkı görmeden karar veren koşu, %s" % SAD[s] for s in SV] +
                 ["eşi kesin sanılan, %s" % SAD[s] for s in SV] + ["eşin en büyük p, %s" % SAD[s] for s in SV],
                 sat, min_w=1600)


def tablo_c(S):
    sat = []
    for k in K:
        r = ["<b>%s</b>" % KS[k]]
        for s in SV:
            v = S[s]["C"]["koridor"][k]
            r.append(("%d koşu / %d adım" % (v["yanlis_kosu"], v["yanlis_adim"])) if v["yanlis_adim"] else renk(0))
        for s in SV:
            v = S[s]["C"]["koridor"][k]
            r.append("%d / %d / %d" % (v["son_dogru"], v["son_kararsiz"], v["son_yanlis"]))
        for s in SV:
            v = S[s]["C"]["koridor"][k]
            r.append("%s (%s–%s)" % (t(v["karar_med"], 2), t(v["karar_min"], 2), t(v["karar_max"], 2)))
        sat.append(r)
    return tablo(["Koridor (3 koşu)"] + ["kendinden emin yanlış, %s" % SAD[s] for s in SV] +
                 ["sonda D / K / Y, %s" % SAD[s] for s in SV] + ["karar yolu m, %s" % SAD[s] for s in SV], sat, min_w=1150)


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
        for s in SV:
            v = S[s]["D"]["koridor"][k]
            r.append(t(100 * v["kk_xy_max"], 1) if v["kk_xy_max"] is not None else "–")
        sat.append(r)
    r = ["yanlış koridor adımı / kararsız konum adımı (18 koşu)"]
    for s in SV:
        D = S[s]["D"]
        r.append("%s / %s" % (renk(D["yanlis_koridor_adim"]), renk(D["konum_kararsiz_adim"])))
    sat.append(r + [""] * 6)
    return tablo(["Koridor (3 koşu)"] + ["ileri-geri cm, %s: ort / en çok" % SAD[s] for s in SV] +
                 ["yan cm, %s: ort / en çok" % SAD[s] for s in SV] + ["toplam en çok cm, %s" % SAD[s] for s in SV],
                 sat, min_w=1150)


def tablo_tani(S):
    sat = []
    for kor, ad in (("koridor_6", "K6 kaydı, 6 harita"), ("koridor_5", "K5 kaydı, 6 harita")):
        r = [ad]
        for s in ("v1", "v2"):
            x = S[s]["tani"][kor]
            r.append("%s / %d tohum yanlışa kesin (%d adım); eşin en büyük p %s"
                     % (renk(x["yanlis_tohum"]), x["n"], x["yanlis_adim"], t(x["es_max"], 2)))
        sat.append(r)
    r = ["birebir aynı iki harita"]
    for s in ("v1", "v2"):
        x = S[s]["tani"]["ikiz"]
        r.append("%s / %d tohum 'kesin' dedi (%d / %d adım); en büyük p %s"
                 % (renk(x["kesin_tohum"]), x["n"], x["kesin_adim"], x["adim"], t(x["p_max"], 2)))
    sat.append(r)
    return tablo(["Tanı (aynı kayıt, 10 konumlayıcı tohumu)", "v1", "v2"], sat, sinif="", min_w=760)


def tablo_360(S):
    """v2 ile v2-360 farkı, koridor başına (B ve D)."""
    sat = []
    for k in K:
        b2, b3 = S["v2"]["B"]["koridor"][k], S["v2_360"]["B"]["koridor"][k]
        d2, d3 = S["v2"]["D"]["koridor"][k], S["v2_360"]["D"]["koridor"][k]
        sat.append(["<b>%s</b>" % KS[k],
                    "%s → %s" % (t(b2["karar_med"], 2), t(b3["karar_med"], 2)),
                    "%s → %s" % (t(b2["karar_max"], 2), t(b3["karar_max"], 2)),
                    "%s → %s" % (t(b2["konum_karar_med"], 2), t(b3["konum_karar_med"], 2)),
                    "%s → %s" % (t(b2["konum_karar_max"], 2), t(b3["konum_karar_max"], 2)),
                    "%s → %s" % (yz(b2["kararsiz_adim"], b2["adim"], 1), yz(b3["kararsiz_adim"], b3["adim"], 1)),
                    "%s → %s" % (t(100 * d2["kk_ileri_max"], 1), t(100 * d3["kk_ileri_max"], 1)),
                    "%s → %s" % (t(100 * d2["kk_yan_max"], 1), t(100 * d3["kk_yan_max"], 1))])
    return tablo(["Koridor (v2 → v2-360)", "B doğru karar yolu ortanca m", "B karar yolu en çok m",
                  "B neresi kesinleşir: ortanca m", "B neresi kesinleşir: en çok m", "B kararsız adım",
                  "D ileri-geri en çok cm", "D yan en çok cm"], sat, min_w=1150)


def u_atlama(o):
    """U dönüşü sırasında ya da en çok 3 m sonra pozun 180° ters dönmesi."""
    return (o["u_donusu"] == "sirasinda" or (o["u_donusu"] == "sonra" and o["u_sonrasi_yol_m"] <= 3.0)) \
        and o["ilk_yon_farki_derece"] > 150


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
        sat.append(["%s" % o["id"], KS[o["kor"]], o["insan"] or "–", kk, kp, t(o["ilk_hata_m"], 1),
                    t(o["ilk_yon_farki_derece"], 0), u, son, o["neden"]])
    if not sat:
        return '<p class="ok">Kendinden emin yanlış koşu yok.</p>'
    return tablo(["koşu", "gerçek", "insan", "yanlış koridor: adım, yol → sanılan", "doğru koridorda > 0,5 m yanlış yer: adım, yol",
                  "ilk kötü adımda hata m", "yön farkı °", "U dönüşü", "sonda", "gözlenen neden"], sat, min_w=1500)


def tablo_tani_donus(S):
    T = S.get("tani_donus")
    if not T:
        return ""
    ad = {"varsayilan": "varsayılan (deneydeki ayar)", "capraz_tohum=False": "<code>capraz_tohum=False</code>",
          "harita_kaniti=ortalama": "<code>harita_kaniti=\"ortalama\"</code> (v1'in harita kanıtı)"}
    sat = []
    for k, xs in T["denemeler"].items():
        at = [x for x in xs if x["kotu_adim"]]
        sat.append([ad.get(k, k), "%s / %d" % (renk(len(at)), len(xs)), sum(x["kotu_adim"] for x in xs),
                    ", ".join(t(x["ilk_kotu_yol"], 2) for x in at) or "–", renk(sum(x["yanlis_harita_adim"] for x in xs))])
    return tablo(["%s kaydı, 5 konumlayıcı tohumu" % T["kayit"], "atlayan tohum", "konum kesin ama > 2 m yanlış adım",
                  "ilk atlama yolu m", "yanlış koridor adımı"], sat, min_w=820)


def sayilar(S):
    Z = {}
    for s in SV:
        ol = S[s]["olaylar"]
        D = S[s]["D"]["koridor"]
        Z[s] = dict(
            a=S[s]["A"]["toplam"], kosu=len(ol), kosu_b=sum(1 for o in ol if o["bolum"] == "B"),
            kosu_c=sum(1 for o in ol if o["bolum"] == "C"),
            kor_kosu=sum(1 for o in ol if o["koridor_adim"]), kor_adim=sum(o["koridor_adim"] for o in ol),
            yer_kosu=sum(1 for o in ol if o["konum_adim"]), yer_adim=sum(o["konum_adim"] for o in ol),
            u_at=sum(1 for o in ol if u_atlama(o)), u_n=sum(S[s]["u_donuslu_kosu"].values()),
            u_kor=sum(1 for o in ol if u_atlama(o) and o["koridor_adim"]),
            u_kalici=sum(1 for o in ol if u_atlama(o) and (o["son_harita"] != o["kor"] or (o["son_hata_m"] or 0) > 0.5)),
            cift=sum(1 for o in ol if o["bolum"] == "B" and o["neden"].startswith("benzer çift")),
            cift_sonra=sum(x["yanlis_kosu"] for x in S[s]["B"]["benzer_cift"].values()),
            isl=S[s]["D"]["islenen"],
            d_il=100 * max(v["kk_ileri_max"] for v in D.values()), d_yan=100 * max(v["kk_yan_max"] for v in D.values()),
            d_il_ort=100 * sum(v["kk_ileri_ort"] for v in D.values()) / len(D),
            hareket_n=S[s]["B"]["n"] + S[s]["C"]["n"],
            kalan_c=sum(1 for o in ol if not u_atlama(o) and o["bolum"] == "C"),
            once_karar=sum(x["once_karar"] for x in S[s]["B"]["benzer_cift"].values()),
            cift_n=sum(x["n"] for x in S[s]["B"]["benzer_cift"].values()))
    return Z


TARIHCE_NOTU = ('<div class="env"><b>Bu bölüm tarihçedir.</b> Aşağıdaki 1–11. bölümler raporun ilk sürümüdür (v1, düzeltme '
                "öncesi konumlayıcı). Konumlayıcıdaki hatalar bu deneyle bulundu (4. bölüm tanı, 10. bölüm); v2'de "
                "düzeltildiler, güncel sayılar yukarıdaki karşılaştırmadadır. v1 sayıları <code>sonuc/</code> ve "
                "<code>gorsel/</code> dosyalarındandır, değiştirilmedi.</div>")


def html(S, img):
    Z = sayilar(S)
    E = S["v1_esitlik"]
    KR = S["kor"]
    v1, v2, v3 = Z["v1"], Z["v2"], Z["v2_360"]
    T1, T2 = S["v1"]["tani"], S["v2"]["tani"]
    h = []
    h.append('<h2 id="v2">Düzeltme sonrası durum (v2) ve 360° görüş (v2-360)</h2>')
    h.append('<div class="env"><b>Okurken:</b> <b>v1</b> = düzeltme öncesi konumlayıcı (raporun ilk sürümü), <b>v2</b> = '
             "düzeltilmiş konumlayıcı, <b>v2-360</b> = v2 + LiDAR'da kör sektör yok. Üçü de aynı sürüşleri, aynı tohumları ve "
             "aynı taramaları kullanır; değişen yalnız konumlayıcı (v1 → v2) ve görüş açısıdır (v2 → v2-360). Konumlayıcı "
             'her sürümde varsayılan ayarlarla koştu. "Kendinden emin yanlış" = konumlayıcı kararsız değilken yanlış koridor '
             'dedi; "yanlış yer" = doğru koridor, konum da kesin dedi ama poz 0,5 m\'den fazla yanlış.</div>')
    kp = [
        ("Kendinden emin yanlış koşu, B + C (%d koşu)" % v2["hareket_n"],
         "%d → %d → %d" % (v1["kosu"], v2["kosu"], v3["kosu"]),
         "v1 → v2 → v2-360; v2'de U dönüşünde poz atlaması: %d koşu" % v2["u_at"]),
        ("Benzer çift: fark görünmeden eşine kesin (B)", "%d → %d → %d" % (v1["cift"], v2["cift"], v3["cift"]),
         "koşu, v1 → v2 → v2-360 (v1'in ana bulgusu)"),
        ("Tanı: aynı kayıtta yanlışa kesin tohum",
         "%d / %d → %d / %d" % (T1["koridor_5"]["yanlis_tohum"] + T1["koridor_6"]["yanlis_tohum"],
                                T1["koridor_5"]["n"] + T1["koridor_6"]["n"],
                                T2["koridor_5"]["yanlis_tohum"] + T2["koridor_6"]["yanlis_tohum"],
                                T2["koridor_5"]["n"] + T2["koridor_6"]["n"]),
         "v1 → v2; ikiz haritada 'kesin' diyen tohum %d / %d → %d / %d" % (T1["ikiz"]["kesin_tohum"], T1["ikiz"]["n"],
                                                                          T2["ikiz"]["kesin_tohum"], T2["ikiz"]["n"])),
        ("D: konum kararı sonrası ileri-geri hata, en çok", "%s → %s → %s cm" % (t(v1["d_il"]), t(v2["d_il"]), t(v3["d_il"])),
         "koridor ortalamalarının ortalaması %s → %s → %s cm" % (t(v1["d_il_ort"]), t(v2["d_il_ort"]), t(v3["d_il_ort"]))),
        ("A: durağan tek taramada doğru (216 poz)", "%d → %d → %d" % (v1["a"]["dogru"], v2["a"]["dogru"], v3["a"]["dogru"]),
         "kendinden emin yanlış %d / %d / %d" % (v1["a"]["yanlis"], v2["a"]["yanlis"], v3["a"]["yanlis"])),
    ]
    h.append('<div class="k">')
    for a, b, c in kp:
        h.append('<div class="kpi"><span>%s</span><b>%s</b><span>%s</span></div>' % (a, b, c))
    h.append("</div>")
    b6 = lambda s, k: S[s]["B"]["benzer_cift"][k]  # noqa: E731
    madde = [
        "<b>Aynı veri.</b> v2 ve v2-360 fiziği v1'in tohumlarıyla yeniden koşuldu (v1'in ham kayıtları bütün taramaları "
        "saklamadığı için yeniden besleme yapılamadı). Adım sayısı v1 ile aynı olan hareket koşusu: %d / %d; yer gerçeği "
        "yolu en çok %s m farklı; v1'in sakladığı %d taramada ve A'nın %d pozunda farklı ışın sayısı %d."
        % (E["adim_sayisi_esit"], E["hareket_kosu"], t(E["en_buyuk_yol_farki_m"], 1), E["saklanan_tarama"], E["a_poz"],
           E["farkli_isin"] + E["a_farkli_isin"]),
        "<b>v1'in ana sorunu düzeldi.</b> Benzer çiftte fark görülmeden eşine kesin karar (B): %d koşu → %d koşu. "
        "Tanıda (aynı kayıt, 10 konumlayıcı tohumu × 2 koridor) yanlışa kesin tohum %d → %d; birebir aynı iki haritada "
        "'kesin' diyen tohum %d / %d → %d / %d, en büyük olasılık %s → %s (ayırt edemediğini doğru söylüyor). Benzer çiftte "
        "farkı ışınlarında görmeden karar veren koşu %d / %d → %d / %d; başlangıç ucundan K6'da fark %s m'de görünür, v2 "
        "%s m'de karar verir. (v2'de eşini kesin sanan tek B koşusu U dönüşü atlamasından sonradır; aşağıda.)"
        % (v1["cift"], v2["cift"], T1["koridor_5"]["yanlis_tohum"] + T1["koridor_6"]["yanlis_tohum"],
           T2["koridor_5"]["yanlis_tohum"] + T2["koridor_6"]["yanlis_tohum"], T1["ikiz"]["kesin_tohum"], T1["ikiz"]["n"],
           T2["ikiz"]["kesin_tohum"], T2["ikiz"]["n"], t(T1["ikiz"]["p_max"], 2), t(T2["ikiz"]["p_max"], 2),
           v1["once_karar"], v1["cift_n"], v2["once_karar"], v2["cift_n"],
           t(b6("v2", "koridor_6_bas")["fark_60"]["med"]), t(b6("v2", "koridor_6_bas")["karar"]["med"])),
        "<b>Konum doğruluğu arttı.</b> Başlangıç bilinen sürüşte (D) konum kararı sonrası ileri-geri hata koridor ortalaması "
        "%s → %s cm, en çok %s → %s cm, "
        "yan hata en çok %s → %s cm. v1'de bildirilen poz işlenmeyen taramalarda ilerletilmiyordu: işlenmeyen adımlarda "
        "ortalama mutlak ileri-geri hata v1 %s cm (işlenenlerde %s cm), v2 %s cm (%s cm)."
        % (t(v1["d_il_ort"]), t(v2["d_il_ort"]), t(v1["d_il"]), t(v2["d_il"]), t(v1["d_yan"]), t(v2["d_yan"]),
           t(100 * v1["isl"]["yok_mutlak"]), t(100 * v1["isl"]["isl_mutlak"]), t(100 * v2["isl"]["yok_mutlak"]),
           t(100 * v2["isl"]["isl_mutlak"])),
        '<b class="no">v2\'de hâlâ kendinden emin yanlış var: %d koşu (B %d, C %d).</b> %d koşuda yeni bir hata var: U dönüşü '
        "sırasında ya da hemen sonrasında poz koridorun uçtan uca eşine atlıyor (yön 180° ters, poz koridorun öbür "
        "yarısında). U dönüşlü koşularda sıklık: v2 %d / %d, v1 %d / %d. Atlayan koşulardan sonra yanlış koridora da geçen: "
        "%d; yanlış koridor ya da yanlış yerde biten: %d. Öbür %d koşu (C'de, insanlar varken: %d) aşağıda tek tek "
        "listelendi. Aynı kayıtta 5 tohumla yapılan tanıda atlama "
        "varsayılan ayarla %s, <code>capraz_tohum</code> kapalıyken %s, v1'in harita kanıtıyla %s tohumda görüldü: atlama "
        "v2'de gelen uyum aramalı harita kanıtı ve çapraz tohumlamayla ilişkili. Bu deneyde modüle dokunulmadı, ayar yapılmadı."
        % (v2["kosu"], v2["kosu_b"], v2["kosu_c"], v2["u_at"], v2["u_at"], v2["u_n"], v1["u_at"], v1["u_n"], v2["u_kor"],
           v2["u_kalici"],
           v2["kosu"] - v2["u_at"], v2["kalan_c"], *_donus_ozet(S)),
        "<b>360° görüş (v2-360) karışıklığı çözmüyor.</b> Durağan tek taramada doğru %d → %d poz; D'de ileri-geri en çok "
        "%s → %s cm. Ama hareket hâlinde doğru karar hızlanmadı (B ortanca, K5 %s → %s m, K6 %s → %s m) ve U dönüşü atlaması "
        "%d → %d koşu oldu. Konumlayıcı aynı %d ışını %s° yerine 360°'ye yayıyor; benzer çiftin farkı seyrek ışınlarda daha "
        "geç görünüyor (başlangıç ucundan K6: %s → %s m)."
        % (v2["a"]["dogru"], v3["a"]["dogru"], t(v2["d_il"]), t(v3["d_il"]),
           t(S["v2"]["B"]["koridor"]["koridor_5"]["karar_med"], 2), t(S["v2_360"]["B"]["koridor"]["koridor_5"]["karar_med"], 2),
           t(S["v2"]["B"]["koridor"]["koridor_6"]["karar_med"], 2), t(S["v2_360"]["B"]["koridor"]["koridor_6"]["karar_med"], 2),
           v2["u_at"], v3["u_at"], KR["isin_mcl"], t(360 - KR["genislik"] - 2 * KR["pay"], 1),
           t(b6("v2", "koridor_6_bas")["fark_60"]["med"]), t(b6("v2_360", "koridor_6_bas")["fark_60"]["med"])),
    ]
    h.append("<h3>Kısa sonuç</h3><ul>%s</ul>" % "".join("<li>%s</li>" % m for m in madde))

    h.append("<h3>Sürümler ve yöntem</h3>")
    h.append(tablo_surumler())
    h.append('<p class="not">v2 ve v2-360 aynı fizik koşusundan çıkar: LiDAR 360° kaydedilir, v2 taraması sanal LiDAR\'ın kendi '
             "kör sektör maskesi sonradan uygulanarak elde edilir. Gürültü üreteci maske ne olursa olsun aynı sayıda çekildiği "
             "için bu, maskeli taramayla birebir aynıdır. v2-360'ta robot gövdesi ışınları kesmiyor (VARSAYIM): sonuçlar taban "
             "ile gövde arasında açık bir LiDAR boşluğunun üst sınırıdır.</p>")

    h.append("<h3>A: durağan tek tarama (D / K / Y = doğru / kararsız / kendinden emin yanlış)</h3>")
    h.append(tablo_a(S))
    h.append("<h3>B: hangi koridor (90 koşu)</h3>")
    h.append(tablo_b(S))
    h.append(img("gorsel_v2/karsilastirma_ozet.png", "v1 / v2 / v2-360: B karar yolu, B konum kararı, B + C kendinden emin "
                 "yanlış adım, D ileri-geri hata"))
    h.append("<h3>B: koridorun neresinde</h3>")
    k1 = [S[s]["B"]["koridor"]["koridor_1"] for s in SV]
    h.append(tablo_konum(S))
    h.append('<p class="not">"Neresi kesinleşir" = konum kararsızlığı son kez bittiği yol. K1\'de en çok değer v1 %s m, v2 %s m, '
             "v2-360 %s m; ortanca %s / %s / %s m. v2 ve v2-360'taki büyük en çok değerler U dönüşü atlamasından sonra "
             "konumun yeniden kurulmasını bekleyen koşulardır (aşağıdaki liste).</p>"
             % (t(k1[0]["konum_karar_max"], 1), t(k1[1]["konum_karar_max"], 1), t(k1[2]["konum_karar_max"], 1),
                t(k1[0]["konum_karar_med"], 2), t(k1[1]["konum_karar_med"], 2), t(k1[2]["konum_karar_med"], 2)))

    h.append("<h3>Benzer çift (K5 / K6)</h3>")
    h.append(tablo_cift(S))
    h.append(img("gorsel_v2/karsilastirma_benzer_cift.png", "Benzer çift, başlangıç ucundan: doğru koridorun olasılığı, "
                 "üç sürüm (kesikli mor çizgi: fark konumlayıcının ışınlarında görünür, ortanca)"))

    h.append("<h3>Kendinden emin yanlış koşuların tamamı</h3>")
    for s in ("v2", "v2_360", "v1"):
        h.append("<p><b>%s</b> (%d koşu)</p>" % (SAD[s], len(S[s]["olaylar"])))
        h.append(tablo_olaylar(S, s))
    h.append('<p class="not">"Gözlenen neden" ham adımlardan çıkarılan etikettir: ilk kötü adımda tahmin ile gerçek yön farkı '
             "150°'den büyükse poz ters; U dönüşü yer gerçeğinden (yol başına 2 rad/m'den hızlı, toplam 2,5 rad'dan fazla "
             "dönüş). U dönüşünü yalnız ortadan başlayan koşular yapar.</p>")
    h.append("<p><b>Tanı: U dönüşü atlaması hangi değişiklikten?</b> Aynı kayıt (sürüş ve tarama), 5 konumlayıcı tohumu. "
             "Bu bir ayar denemesi değil; yalnız nedeni ayırmak için (<code>tani_donus.py</code>).</p>")
    h.append(tablo_tani_donus(S))
    h.append(img("gorsel_v2/ornek_B_konum.png", "v2: doğru koridor, konum kesin ama yanlış: poz koridorun öbür yarısında, yön ters"))

    h.append("<h3>C: haritada olmayan insanlar (18 koşu)</h3>")
    h.append(tablo_c(S))
    h.append("<h3>D: başlangıç biliniyor (18 koşu)</h3>")
    h.append(tablo_d(S))
    h.append("<h3>Tanı: aynı kayıt, 10 konumlayıcı tohumu (v1 → v2)</h3>")
    h.append(tablo_tani(S))

    h.append("<h2 id=\"g360\">360° görüş ne kazandırır</h2>")
    h.append(_g360(S, Z))
    h.append(tablo_360(S))
    return h


def _donus_ozet(S):
    T = S.get("tani_donus")
    if not T:
        return ("–", "–", "–")
    out = []
    for k in ("varsayilan", "capraz_tohum=False", "harita_kaniti=ortalama"):
        xs = T["denemeler"].get(k, [])
        out.append("%d / %d" % (sum(1 for x in xs if x["kotu_adim"]), len(xs)))
    return tuple(out)


def _g360(S, Z):
    KR = S["kor"]
    A2, A3 = S["v2"]["A"]["oranlar"], S["v2_360"]["A"]["oranlar"]
    B2, B3 = S["v2"]["B"]["koridor"], S["v2_360"]["B"]["koridor"]
    D2, D3 = S["v2"]["D"]["koridor"], S["v2_360"]["D"]["koridor"]
    a_fark = [(k, A3[k]["dogru"] - A2[k]["dogru"]) for k in K]
    a_txt = ", ".join("%s: %+d" % (KS[k], d) for k, d in a_fark if d) or "hiçbir koridorda değişmiyor"
    med_fark = [(k, (B3[k]["karar_med"] or 0) - (B2[k]["karar_med"] or 0)) for k in K]
    kotu = max(med_fark, key=lambda x: x[1])
    iyi = min(med_fark, key=lambda x: x[1])
    bc = lambda s, k, f: S[s]["B"]["benzer_cift"][k][f]["med"]  # noqa: E731
    kk2 = sum(v["kararsiz_adim"] for v in B2.values()) / sum(v["adim"] for v in B2.values())
    kk3 = sum(v["kararsiz_adim"] for v in B3.values()) / sum(v["adim"] for v in B3.values())
    s = []
    s.append('<div class="env">Soru: sensörün %s° kör bölgesi (%s; yazılım maskesi her yana %s° pay ekler) işletmede neye mal '
             "oluyor? Aynı sürüşler v2 (kör bölge var) ve v2-360 (yok) ile karşılaştırıldı. Konumlayıcı ikisinde de "
             "taramadan %d ışın kullanır.</div>"
             % (t(KR["genislik"], 1), ", ".join("%s°–%s°" % (t(a, 1), t(b, 1)) for a, b in KR["sektorler"]),
                t(KR["pay"], 0), KR["isin_mcl"]))
    s.append('<div class="bulgu"><b>Bulgu.</b><ul>'
             "<li><b>Durağan tek tarama:</b> kör bölge kalkınca doğru poz sayısındaki değişim (36 pozdan) %s; K5 ve K6'da iki "
             "sürümde de bütün pozlar kararsız. Kendinden emin yanlış iki sürümde de %d.</li>"
             "<li><b>Hareket (B):</b> doğru karar yolunun ortancasının en çok kısaldığı koridor %s (%s → %s m), en çok uzadığı "
             "koridor %s (%s → %s m). Kararsız adım payı %s → %s.</li>"
             "<li><b>Benzer çift:</b> fark konumlayıcının ışınlarında başlangıç ucundan K6'da %s → %s m'de görünür (sık "
             "taramada, 500 ışın: %s → %s m). Aynı %d ışın daha geniş açıya yayıldığı için aralık açılıyor ve küçük fark "
             "bölgesi daha geç yakalanıyor; karar da %s → %s m.</li>"
             "<li><b>Konum doğruluğu (D):</b> ileri-geri hata en çok %s → %s cm, yan en çok %s → %s cm.</li>"
             "<li><b>U dönüşü atlaması</b> kör bölgeden gelmiyor: v2'de %d, v2-360'ta %d koşu.</li></ul></div>"
             % (a_txt, Z["v2_360"]["a"]["yanlis"],
                KS[iyi[0]], t(B2[iyi[0]]["karar_med"], 2), t(B3[iyi[0]]["karar_med"], 2),
                KS[kotu[0]], t(B2[kotu[0]]["karar_med"], 2), t(B3[kotu[0]]["karar_med"], 2),
                yz(kk2, 1, 1), yz(kk3, 1, 1),
                t(bc("v2", "koridor_6_bas", "fark_60")), t(bc("v2_360", "koridor_6_bas", "fark_60")),
                t(bc("v2", "koridor_6_bas", "fark_500")), t(bc("v2_360", "koridor_6_bas", "fark_500")),
                KR["isin_mcl"], t(bc("v2", "koridor_6_bas", "karar")), t(bc("v2_360", "koridor_6_bas", "karar")),
                t(Z["v2"]["d_il"]), t(Z["v2_360"]["d_il"]), t(Z["v2"]["d_yan"]), t(Z["v2_360"]["d_yan"]),
                Z["v2"]["u_at"], Z["v2_360"]["u_at"]))
    s.append('<div class="yorum"><b>Yorum.</b> Bu koridorlarda kör bölgenin hareket hâlindeki maliyeti koridor karışıklığı '
             "olarak görünmüyor; maliyet durağan tek taramada (%s) ve birkaç santimetrelik konum doğruluğunda. 360° görüşün "
             "kazancı ancak konumlayıcının ışın sayısı açıyla birlikte artırılırsa benzer çiftte de görülebilir; bu ayrı bir koşu "
             "kümesiyle denenmeli (bu deneyde ayar yapılmadı). Gövdenin ışını kesmediği varsayımıyla bu bir üst sınırdır.</div>"
             % (", ".join(KS[k] for k, d in a_fark if d > 0) or "yok"))
    return "".join(s)


def acik(S):
    Z = sayilar(S)
    m = [
        "U dönüşünde pozun koridorun uçtan uca eşine atlaması (v2'de %d / %d U dönüşlü koşu, v2-360'ta %d / %d): konumlama "
        "modülünde düzeltilmeli. Tanı: <code>sonuc_v2/tani_donus.json</code>. Bu deneyde modüle dokunulmadı."
        % (Z["v2"]["u_at"], Z["v2"]["u_n"], Z["v2_360"]["u_at"], Z["v2_360"]["u_n"]),
        "İnsanlar varken başlangıçta (C) eşine ya da ters poza kesin karar: listede U dönüşüne bağlı olmayan C koşuları.",
        "360° görüşte ışın sayısı açıyla artırılırsa (ör. aynı aralık için daha çok ışın) benzer çiftte ne kazanılır: ayrı "
        "koşu kümesiyle, ayar ve değerlendirme tohumları ayrı denenmeli.",
        "v2-360 gövdenin ışını kesmediği varsayımına dayanıyor; gerçek bir LiDAR boşluğu tasarımıyla doğrulanmalı.",
        "Hareketli insanlar, cam, koyu yüzey ve eğik zemin denenmedi.",
        "Gerçek RPLIDAR C1 ile gerçek koridor kaydı alınmalı (harita ile bina farkı).",
        "Robot modeli ÖNERİ (dönebilen, öneri firmware + ön omni; VARSAYIM). Bugünkü robot (V0) modelde dönemiyor.",
    ]
    return "<h2>Açık işler</h2><ul>%s</ul>" % "".join("<li>%s</li>" % x for x in m)
