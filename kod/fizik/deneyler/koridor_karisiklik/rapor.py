"""rapor.html: sonuc/ozet.json + gorsel/*.png -> tek dosya (görseller base64 gömülü).

    py -3 kod\\fizik\\deneyler\\koridor_karisiklik\\rapor.py      (önce analiz.py)
"""

import base64
import html
import json
import os

BURASI = os.path.dirname(os.path.abspath(__file__))
K = ["koridor_%d" % i for i in range(1, 7)]
KS = {k: "K%d" % (i + 1) for i, k in enumerate(K)}
BICIM = {"koridor_1": "düz, 2,0 × 30 m, 16 kapı düzenli ritimde", "koridor_2": "düz, 3,5 × 12 m, kolon + dolap",
         "koridor_3": "L, 2,4 m, 16 + 10 m kol", "koridor_4": "T, 2,6 m, ana hat 22 m + 8 m yan kol",
         "koridor_5": "düz, 2,4 × 24 m (benzer çift A)", "koridor_6": "düz, 2,4 × 24 m (benzer çift B, 2 yerel fark)"}
BAS_AD = {"bas": "başlangıç ucu", "son": "öbür uç (ters)", "orta": "ortadan"}
DURUM_AD = {"dogru": "doğru", "kararsiz": "kararsız", "yanlis": "yanlış"}

# proje raporlarının stili (raporlar/aku-secimi/rapor.html) + bulgu / yorum kutuları ve şekiller
STIL = """
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f;--fig:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b;--ok:#4cb87c;--no:#e5675a;--uy:#d9a441;--acc2:#6aaef0;--fig:#f4f3ef}}
:root[data-theme="dark"]{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b;--ok:#4cb87c;--no:#e5675a;--uy:#d9a441;--acc2:#6aaef0;--fig:#f4f3ef}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:27px;margin:0 0 4px;line-height:1.25}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:20px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.tw{overflow-x:auto;margin:8px 0 6px;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
table.say td:not(:first-child),table.say th:not(:first-child){text-align:right}table.say td:not(:first-child){white-space:nowrap}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:20px;line-height:1.25}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:6px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px;font-size:13px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.uy{color:var(--uy);font-weight:600}.mut{color:var(--mut)}
.not{color:var(--mut);font-size:13px;margin:6px 0 14px}a{color:var(--acc2);word-break:break-word}
.env{border-left:4px solid var(--acc2);background:var(--card);padding:10px 14px;border-radius:6px;margin:12px 0}
.bulgu{border-left:4px solid var(--ok);background:var(--card);padding:10px 14px;border-radius:6px;margin:12px 0}
.yorum{border-left:4px solid var(--uy);background:var(--card);padding:10px 14px;border-radius:6px;margin:12px 0}
figure{margin:14px 0;background:var(--fig);border:1px solid var(--line);border-radius:10px;padding:8px}
figure img{width:100%;height:auto;display:block}figcaption{color:#555;font-size:12.5px;padding:4px 4px 0}
@media (max-width:640px){h1{font-size:22px}table{font-size:13px}main{padding:18px 16px 50px}}
"""

with open(os.path.join(BURASI, "sonuc", "ozet.json"), encoding="utf-8") as f:
    OZ = json.load(f)
with open(os.path.join(BURASI, "metin.json"), encoding="utf-8") as f:
    METIN = json.load(f)                      # elle yazılan yorum / sonuç maddeleri (bulgudan ayrı)


def e(s):
    return html.escape(str(s))


def sayi(v, b=1, bos="–"):
    if v is None:
        return bos
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return str(v)
    return ("%." + str(b) + "f") % v if b else "%d" % round(v)


def tr(v, b=1, bos="–"):
    return sayi(v, b, bos).replace(".", ",")


def yuzde(a, n):
    return "–" if not n else "%%%s" % tr(100.0 * a / n, 0)


def img(ad, alt):
    yol = os.path.join(BURASI, "gorsel", ad)
    if not os.path.exists(yol):
        return ""
    with open(yol, "rb") as f:
        b = base64.b64encode(f.read()).decode()
    return '<figure><img src="data:image/png;base64,%s" alt="%s"><figcaption>%s</figcaption></figure>' % (b, e(alt), e(alt))


def tablo(baslik, satirlar, sinif="say", min_w=0):
    h = "".join("<th>%s</th>" % b for b in baslik)
    g = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in s) for s in satirlar)
    st = ' style="min-width:%dpx"' % min_w if min_w else ""
    return '<div class="tw"><table class="%s"%s><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (sinif, st, h, g)


def karisiklik(T, yuzdeli=False):
    sut = K + ["kararsiz"]
    sat = []
    for k in K:
        n = sum(T[k].values())
        hucre = ["<b>%s</b>" % KS[k]]
        for c in sut:
            v = T[k][c]
            metin = ("%s" % yuzde(v, n)) if yuzdeli else str(v)
            if v == 0:
                hucre.append('<span class="mut">0</span>')
            elif c == k:
                hucre.append('<span class="ok">%s</span>' % metin)
            elif c == "kararsiz":
                hucre.append('<span class="uy">%s</span>' % metin)
            else:
                hucre.append('<span class="no">%s</span>' % metin)
        hucre.append(str(n))
        sat.append(hucre)
    return tablo(["gerçek \\ tahmin"] + [KS[k] for k in K] + ["kararsız", "toplam"], sat)


def p(*parcalar):
    return "".join(parcalar)


def son_hucre(v):
    """Sonda doğru = son adımda doğru koridor VE kararlı; kararsız / yanlış biten ayrı yazılır."""
    s = "%d / %d" % (v["son_dogru"], v["n"])
    if v.get("son_kararsiz"):
        s += ' <span class="uy">(%d kararsız)</span>' % v["son_kararsiz"]
    if v.get("son_yanlis"):
        s += ' <span class="no">(%d yanlış)</span>' % v["son_yanlis"]
    return s


NOT_YOL = ('<p class="not">"D / K / Y" = o yol noktasındaki doğru / kararsız / yanlış koşu sayısı. Bir koşu o yola '
           'ulaşmadan bittiyse o noktada sayılmaz: payda yalnız o mesafeye ulaşan koşulardır. <b>*</b> = bazı koşular bu '
           'mesafeye ulaşmadı (ör. K2 12 m\'lik koridor: baştan ve sondan başlayan koşular 15 m\'ye ulaşmaz); hiçbiri '
           'ulaşmadıysa "–". "Sonda doğru" = son adımda doğru koridor ve kararlı; kararsız ya da yanlış biten ayrıca yazılır.</p>')


def bolum_hareket(b):
    """B / C için koridor tablosu."""
    E = OZ[b]
    sat = []
    for k in K:
        v = E["koridor"].get(k)
        if not v:
            continue
        yd = v["yol_durum"]

        def ydh(d):
            x = yd[d]
            n = v["n"] - x["yok"]
            if n == 0:
                return "–"
            s = "%d / %d / %d" % (x["dogru"], x["kararsiz"], x["yanlis"])
            return s if n == v["n"] else s + " *"

        sat.append(["<b>%s</b> %s" % (KS[k], e(BICIM[k])), v["n"],
                    "%s (%s–%s)" % (tr(v["karar_med"]), tr(v["karar_min"]), tr(v["karar_max"])) + (
                        " · %d koşuda yok" % v["karar_yok"] if v["karar_yok"] else ""),
                    ydh("2"), ydh("5"), ydh("10"), ydh("15"),
                    "%d koşu / %d adım" % (v["yanlis_kosu"], v["yanlis_adim"]) if v["yanlis_adim"] else '<span class="ok">0</span>',
                    son_hucre(v)])
    return tablo(["Koridor", "koşu", "doğru karara kadar yol, m: ortanca (en az–en çok)", "2 m: D / K / Y",
                  "5 m", "10 m", "15 m", "kendinden emin yanlış", "sonda doğru"], sat, min_w=980)


def bolum_konum(b):
    E = OZ[b]
    sat = []
    for k in K:
        v = E["koridor"].get(k)
        if not v:
            continue
        sat.append(["<b>%s</b>" % KS[k], tr(v["konum_karar_med"]) + " (en çok %s)" % tr(v["konum_karar_max"]),
                    yuzde(v["konum_kararsiz_oran"], 1).replace("%", "%") if False else "%%%s" % tr(100 * v["konum_kararsiz_oran"], 1),
                    "%s / %s / %s" % (tr(v["kk_ileri_ort"], 3), tr(v["kk_ileri_p95"], 3), tr(v["kk_ileri_max"], 2)),
                    "%s / %s / %s" % (tr(v["kk_yan_ort"], 3), tr(v["kk_yan_p95"], 3), tr(v["kk_yan_max"], 2)),
                    "%s / %s" % (tr(v["ileri_max"], 2), tr(v["yan_max"], 2)),
                    ('<span class="no">%d koşu / %d adım</span>' % (v["konum_yanlis_kosu"], v["konum_yanlis_adim"])
                     if v["konum_yanlis_adim"] else '<span class="ok">0</span>')])
    return tablo(["Koridor", "konum kararına kadar yol, m: ortanca", "konum kararsız adım",
                  "konum kararı sonrası ileri-geri hata, m: ort / p95 / en çok",
                  "yan hata, m: ort / p95 / en çok", "harita kararı sonrası en büyük hata (konum kararsız adımlar dahil), m: ileri / yan",
                  "konum kesin ama > 0,5 m yanlış"], sat, min_w=1100)


def yanlis_tablo(liste, bos):
    if not liste:
        return '<p class="ok">%s</p>' % e(bos)
    sat = [[e(y["id"]), KS[y["kor"]], BAS_AD[y["baslangic"]], y["tohum"], KS[y["harita"]], y["adim"], tr(y["sure_s"]),
            "%s–%s" % (tr(y["ilk_yol"]), tr(y["son_yol"])), tr(y["en_buyuk_p"], 2)] for y in liste]
    return tablo(["koşu", "gerçek", "başlangıç", "tohum", "sanılan", "adım", "süre s", "yol aralığı m", "en büyük p"], sat)


def main():
    A, B = OZ["A"], OZ["B"]
    C, D = OZ.get("C"), OZ.get("D")
    M = METIN
    css = STIL
    h = []
    h.append('<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
             'initial-scale=1"><title>Koridor Karışıklık Deneyi</title><style>%s</style></head><body><main>' % css)
    h.append("<h1>Koridor karışıklık deneyi: LiDAR hangi koridorda olduğunu ne ölçüde karıştırıyor?</h1>")
    h.append('<div class="sub">%s · Lale, MuJoCo simülasyonu · sanal RPLIDAR C1 + çok haritalı konumlayıcı (MCL) · '
             'betikler ve ham veri: <code>kod/fizik/deneyler/koridor_karisiklik/</code></div>' % e(M["tarih"]))
    # KPI
    h.append('<div class="k">')
    for kp in M["kpi"]:
        h.append('<div class="kpi"><span>%s</span><b>%s</b><span>%s</span></div>' % (e(kp[0]), e(kp[1]), e(kp[2])))
    h.append("</div>")
    h.append("<h2>Kısa sonuç</h2><ul>%s</ul>" % "".join("<li>%s</li>" % x for x in M["sonuc"]))
    h.append('<div class="env"><b>Okurken:</b> %s</div>' % M["okuma"])
    # kurulum
    h.append("<h2>1. Deney nasıl kuruldu</h2>")
    h.append(M["kurulum"])
    h.append(tablo(["Koridor", "Biçim", "Ne ile ayırt edilebilir"], [["<b>%s</b>" % KS[k], e(BICIM[k]), M["ayirt"][k]] for k in K],
                   sinif="", min_w=700))
    h.append(tablo(["Bölüm", "Soru", "Koşu"], M["bolumler"], sinif="", min_w=760))
    h.append(M["terimler"])
    # A
    h.append("<h2>2. A: durağan tek tarama</h2>")
    t = A["toplam"]
    h.append('<div class="bulgu"><b>Bulgu.</b> %d pozun %d\'i doğru (%s), %d\'i kararsız (%s), <b>%d\'i kendinden emin yanlış</b>.'
             ' %s</div>' % (t["n"], t["dogru"], yuzde(t["dogru"], t["n"]), t["kararsiz"], yuzde(t["kararsiz"], t["n"]),
                            t["yanlis"], M["A_bulgu"]))
    h.append(karisiklik(A["tablo"]))
    h.append('<p class="not">Satır gerçek koridor, sütun konumlayıcının tek taramadan seçtiği koridor. "Kararsız" = en olası iki '
             'koridorun olasılık farkı 0,5\'ten küçük. Koridor başına 36 poz: orta hat boyunca yayılmış, yan sapma ±0,3 m, '
             'yön sapması ±10°, yarısı ters yöne bakıyor.</p>')
    h.append(img("A_karisiklik.png", "A: 6 × 7 karışıklık tablosu (poz sayısı)"))
    ik = A["ikili"]
    h.append(tablo(["Gerçek", "kararsız kaldığı ikili (poz)"], [["<b>%s</b>" % KS[k], ", ".join("%s: %d" % kv for kv in
                    sorted(ik[k].items(), key=lambda kv: -kv[1]))] for k in K if k in ik], sinif=""))
    h.append('<div class="yorum"><b>Yorum.</b> %s</div>' % M["A_yorum"])
    # B
    h.append("<h2>3. B: hareket hâlinde, konum bilinmeden (küresel konumlama)</h2>")
    h.append('<div class="bulgu"><b>Bulgu.</b> %s</div>' % M["B_bulgu"])
    h.append("<h3>Karışıklık: bütün adımların dağılımı</h3>")
    h.append(karisiklik(B["adim_tablo"], yuzdeli=True))
    h.append('<p class="not">Her LiDAR turu (10 Hz) bir adım. Satırdaki yüzde, o koridordaki bütün koşuların bütün adımları '
             'içinde. Koşu sonundaki karar: %s.</p>' % M["B_son"])
    h.append(img("B_karisiklik.png", "B: adımların karışıklık tablosu (yüzde)"))
    h.append("<h3>Koridor başına: karar yolu, 2 / 5 / 10 / 15 m'de durum</h3>")
    h.append(bolum_hareket("B"))
    h.append(NOT_YOL)
    h.append('<p class="not">"Doğru karara kadar yol": doğru koridorun kararsız olmadan seçildiği ve koşu sonuna dek bozulmadığı '
             'ilk an (<code>karar_ani</code>).</p>')
    h.append(img("B_karar_yolu.png", "B: doğru karara kadar gidilen yol, koridor ve başlangıç başına"))
    h.append("<h3>Konum hatası (doğru koridorda)</h3>")
    h.append(bolum_konum("B"))
    h.append('<p class="not">Hata robotun kendi çerçevesinde: ileri-geri (gidiş yönü boyunca) ve yan. "Konum kararı" = harita '
             'doğru ve kararlı, ayrıca konumlayıcının kendi konum ölçütü (ana mod payı ≥ 0,8, std ≤ 0,5 m) sağlanıyor ve koşu '
             'sonuna dek öyle kalıyor.</p>')
    h.append('<div class="yorum"><b>Yorum.</b> %s</div>' % M["B_yorum"])
    h.append("<h3>Kendinden emin yanlışlar</h3>")
    h.append(yanlis_tablo(B["yanlislar"], "B'de hiçbir koşuda, hiçbir adımda yanlış koridor kesin seçilmedi."))
    for g in OZ.get("ornek_gorseller", []):
        if g.startswith("ornek_B"):
            h.append(img(g, "B: üstten görünüm örneği (%s)" % g))
    # benzer çift
    h.append("<h2>4. Benzer çift: K5 ve K6</h2>")
    h.append(M["cift_giris"])
    bc = B.get("benzer_cift", [])
    sat = [[e(x["id"]), KS[x["kor"]], BAS_AD[x["baslangic"]], tr(x["fark_menzil_yol"]), tr(x["fark_60_yol"]), tr(x["karar_yol"]),
            tr(x["karar_s"]), tr(x["fark_yaninda_yol"]), tr(x["p_es_en_cok"], 2), x["yanlis_cift"]] for x in bc]
    h.append(tablo(["koşu", "gerçek", "başlangıç", "fark 500 ışında görünür, yol m", "fark 60 ışında görünür, yol m",
                    "karar, yol m", "karar anında s, m", "robot fark bölgesinin yanında, yol m", "eşin en büyük p",
                    "eşi kesin sanılan adım"], sat, min_w=1100))
    h.append('<div class="bulgu"><b>Bulgu.</b> %s</div>' % M["cift_bulgu"])
    tani_yol = os.path.join(BURASI, "sonuc", "tani_ikiz.json")
    if os.path.exists(tani_yol):
        with open(tani_yol, encoding="utf-8") as f:
            TN = json.load(f)
        h.append("<h3>Tanı: aynı kayıt, farklı konumlayıcı tohumu; birebir aynı iki harita</h3>")
        h.append(M["tani_giris"])
        sat = []
        for kor in ("koridor_5", "koridor_6"):
            for x in TN[kor]:
                sat.append([KS[kor] + " kaydı", x["tohum"], tr(x["es_max_6m_once"], 2),
                            ('<span class="no">%d</span>' % x["yanlis_kesin_adim"]) if x["yanlis_kesin_adim"] else "0",
                            tr(x["ilk_kesin_dogru_yol"], 2)])
        h.append(tablo(["kayıt (başlangıç ucu, LiDAR tohumu 2)", "MCL tohumu", "eşin en büyük p (yol < 6 m)",
                        "kendinden emin yanlış adım", "ilk kesin doğru karar, yol m"], sat, min_w=760))
        sat = [[x["tohum"], tr(x["en_buyuk_p"], 2), "%d / %d" % (x["kesin_adim"], x["adim"]), tr(x["son_p_ikiz"], 2)]
               for x in TN["ikiz"]]
        h.append(tablo(["MCL tohumu", "en büyük p (doğrusu 0,50)", "'kesin' adım", "koşu sonunda p(ikiz)"], sat, min_w=560))
    h.append(img("B_benzer_cift.png", "B: benzer çift, p(K5) ve p(K6) – gidilen yol"))
    h.append(img("A_benzer_cift_s.png", "A: benzer çift, durağan tek taramada doğru koridor lehine fark"))
    h.append('<div class="yorum"><b>Yorum.</b> %s</div>' % M["cift_yorum"])
    # C
    if C:
        h.append("<h2>5. C: haritada olmayan 3 duran insan</h2>")
        h.append(M["C_giris"])
        h.append(bolum_hareket("C"))
        h.append(NOT_YOL)
        h.append(bolum_konum("C"))
        h.append(img("C_karisiklik.png", "C: adımların karışıklık tablosu (yüzde)"))
        h.append(img("C_benzer_cift.png", "C: benzer çift, insanlı, p(K5) ve p(K6) – gidilen yol"))
        h.append(yanlis_tablo(C["yanlislar"], "C'de hiçbir koşuda yanlış koridor kesin seçilmedi."))
        for g in OZ.get("ornek_gorseller", []):
            if g.startswith("ornek_C"):
                h.append(img(g, "C: üstten görünüm örneği (%s)" % g))
        h.append('<div class="bulgu"><b>Bulgu.</b> %s</div>' % M["C_bulgu"])
    # D
    if D:
        h.append("<h2>6. D: başlangıç biliniyor (park noktası)</h2>")
        h.append(M["D_giris"])
        sat = []
        for k in K:
            v = D["koridor"].get(k)
            if not v:
                continue
            sat.append(["<b>%s</b>" % KS[k], v["n"], tr(v["yol_ort"]),
                        "%s / %s / %s" % (tr(v["kk_ileri_ort"], 3), tr(v["kk_ileri_p95"], 3), tr(v["kk_ileri_max"], 2)),
                        "%s / %s / %s" % (tr(v["kk_yan_ort"], 3), tr(v["kk_yan_p95"], 3), tr(v["kk_yan_max"], 2)),
                        "%%%s" % tr(100 * v["konum_kararsiz_oran"], 1),
                        '<span class="ok">0</span>' if not v["yanlis_adim"] else '<span class="no">%d</span>' % v["yanlis_adim"],
                        son_hucre(v)])
        h.append(tablo(["Koridor", "koşu", "yol, m", "ileri-geri hata, m: ort / p95 / en çok", "yan hata, m: ort / p95 / en çok",
                        "konum kararsız adım", "yanlış koridor kesin (adım)", "sonda doğru"], sat, min_w=900))
        h.append('<div class="bulgu"><b>Bulgu.</b> %s</div>' % M["D_bulgu"])
        h.append(img("D_hata_yol.png", "D: yol boyunca konum hatası (ileri-geri ve yan)"))
    # nedenler, sınırlar, çıkarımlar
    h.append("<h2>7. Yanılgının nedenleri</h2>")
    h.append(M["nedenler"])
    h.append("<h2>8. Sınırlar: simülasyon neleri modellemiyor</h2>")
    h.append(M["sinirlar"])
    h.append("<h2>9. Gerçek robot için çıkarımlar</h2>")
    h.append(M["cikarimlar"])
    h.append("<h2>10. Garip / başarısız koşular ve tutarsızlıklar</h2>")
    h.append(M["garip"])
    h.append("<h2>11. Koşu sayıları, süre, yeniden üretme</h2>")
    h.append(M["kosu"])
    h.append("<h2>Açık işler</h2>")
    h.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in M["acik"]))
    h.append("<h2>Dosyalar</h2>")
    h.append(tablo(["Dosya", "İçerik"], M["dosyalar"], sinif=""))
    h.append("</main></body></html>")
    with open(os.path.join(BURASI, "rapor.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(h))
    print("rapor.html", os.path.getsize(os.path.join(BURASI, "rapor.html")) // 1024, "KB")


if __name__ == "__main__":
    main()
