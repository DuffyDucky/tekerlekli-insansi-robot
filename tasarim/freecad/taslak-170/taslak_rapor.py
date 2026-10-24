# Lale 1,70 m taslak raporu (sistem Python'u; FreeCAD gerekmez): kutle.json + taslak-analiz.json + gorsel/*.png -> rapor.html
#   python taslak_rapor.py
# Devrilme, motor, servo ve tam carpisma bolumleri BOS baslik: ayri analiz ajani doldurur.
import os, sys, json, base64, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import taslak_ayar as TA
import arayuz as A
import taslak_rapor_analiz as RA      # analiz ajani bolumleri (analiz/*.json)

K = json.load(open(os.path.join(HERE, "kutle.json"), encoding="utf-8"))
AN = json.load(open(os.path.join(HERE, "taslak-analiz.json"), encoding="utf-8"))


def sayi(x, n=1):
    s = ("{:,.%df}" % n).format(x)
    return s.replace(",", " ").replace(".", ",").replace(" ", ".").replace("-", "−")


def esc(s):
    return html.escape(str(s))


def img64(ad):
    p = os.path.join(HERE, "gorsel", ad)
    if not os.path.exists(p):
        return None
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def tablo(basliklar, satirlar, sinif=""):
    h = "<div class='tw'><table class='%s'><tr>%s</tr>" % (sinif, "".join("<th>%s</th>" % b for b in basliklar))
    for s in satirlar:
        h += "<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in s)
    return h + "</table></div>"


def am(v, n=0):
    return "(%s; %s; %s)" % (sayi(v[0], n), sayi(v[1], n), sayi(v[2], n))


def aralik(a):
    return "%s … %s" % (sayi(a[0], 0), sayi(a[1], 0)) if a else "sınırsız"


DURUM = {"ayni": "aynı", "tasindi": "taşındı", "degisti": "değişti", "yeni": "yeni"}
T, E = K["toplam"], K["eski_125"]
KF, KL = K["kafa"], K["kol"]
BO = AN["baski_ozet"]
dur = AN["durum"]
yer = AN["yerlesim"]
taslak_cak = [c for c in yer["ev_pozu_cakisma"] if c.get("kaynak") == "taslak"]
mevcut_cak = [c for c in yer["ev_pozu_cakisma"] if c.get("kaynak") != "taslak"]
sup_cak = sum(1 for s in yer["kafa_suprulme"] if s["cakisma"])
o = KL["oran"]
mo = o["S1_statik_moment_kol_yatay"]
uzatma_g = sum(p["kutle_g"] for p in K["parcalar"] if p["ad"].startswith("Govde uzatma bandi"))
BB = KL["sag"].get("bolum_boylari_mm", {})
SERVO = TA.OMUZ_SERVO["ad"]
KOL_ANALIZ_LINK = ("<p class='karar'>Ayrıntılı kol analizi (DS3235 karşılaştırması, akım bütçesi, parça yükleri ve emniyet katsayıları, dirsek geri sürme, "
                   "önceki doğrusal modelle fark): <a href='kol-analiz/rapor.html'>kol-analiz/rapor.html</a>. İlk analiz ×1,25'i doğrusal (tüp : yaka) "
                   "varsaymıştı; kontrol ajanı (24 Ekim 2026) taslağın gerçek ×1,25 geometrisiyle (ek ön kolda) yeniden koştu.</p>")


def analiz_durumu():
    """Analiz dosyalari (analiz/*.json) guncel geometriye mi ait? (eski, neden) dondurur. Kontrol ajani yeniden kosunca not kalkar."""
    neden = []
    try:
        g = json.load(open(os.path.join(HERE, "analiz", "girdi-yeni-444.json"), encoding="utf-8"))
        y_an = g["eksen"]["dirsek_sag|bilek"]["n"][1]
        y_su = KL["sag"]["bilek_ekseni"]["nokta"][1]
        if abs(y_an - y_su) > 0.05:
            neden.append("bilek ekseni analizde y %s, güncel geometride y %s" % (sayi(y_an, 1), sayi(y_su, 1)))
    except Exception:
        neden.append("analiz/girdi-yeni-444.json okunamadı")
    try:
        hs = json.load(open(os.path.join(HERE, "analiz", "hesap.json"), encoding="utf-8"))
        sv = hs["servo"]["yeni-444"]["kol"][0].get("servo")
        if sv != SERVO:
            neden.append("omuz servosu hesapta %s, kararda %s" % (sv, SERVO))
        if TA.ON_KOL_UZAMA > 0 and hs.get("kol_orani", {}).get("dagilim") != "on_kol":
            neden.append("kol oranı hesabı ek boyu tüp : yaka dağıtıyor (ön kol değil)")
    except Exception:
        neden.append("analiz/hesap.json okunamadı")
    return bool(neden), neden


ANALIZ_ESKI, ANALIZ_NEDEN = analiz_durumu()


def yeniden_notu(bolum):
    if not ANALIZ_ESKI:
        return ""
    return ("<div class='karar'><b class='uy'>×%s + %s için yeniden hesaplanacak.</b> Bu %s bölümündeki değerler önceki geometriye aittir "
            "(kol ×1,15, omuz DS3218MG; %s). Kontrol ajanı <code>taslak_analiz.py</code> + <code>taslak_hesap.py</code> ile yeniden koşunca bu not "
            "kendiliğinden kalkar.</div>" % (sayi(o["hedef"], 2), esc(SERVO), bolum, esc("; ".join(ANALIZ_NEDEN))))

kart = [
    ("%s mm" % sayi(K["olcu"]["boy"], 0), "boy, yerden kafa tepesine (125 cm tasarım: %s mm) · %s × %s mm genişlik × derinlik" % (
        sayi(E["boy"], 0), sayi(K["olcu"]["genislik_x"], 0), sayi(K["olcu"]["derinlik_z"], 0))),
    ("%s kg" % sayi(T["kutle_payli_g"] / 1000, 2), "toplam kütle, kablo payı dahil (parçalar %s kg) · 125 cm: %s kg" % (
        sayi(T["kutle_g"] / 1000, 2), sayi(E["kutle_payli_g"] / 1000, 2))),
    ("y %s mm" % sayi(T["am_payli"][1], 0), "ağırlık merkezi yerden (paylı), AM %s mm · 125 cm: y %s" % (am(T["am_payli"], 1), sayi(E["am_payli"][1], 0))),
    ("%d" % T["parca_sayisi"], "parça (%d aynı, %d taşındı, %d değişti, %d yeni) · 125 cm: %d" % (
        dur["ayni"], dur["tasindi"], dur["degisti"], dur["yeni"], E["parca_sayisi"])),
    ("%d" % BO["sayi"], "baskı parçası (%d yeni, %d değişti) · 25 × 25 × 25 cm tablaya sığmayan %d, 230 mm hedefini aşan %d" % (
        BO["yeni"], BO["degisti"], len(BO["sigmayan_250"]), len(BO["hedef_230_asan"]))),
    ("%s mm" % sayi(KF["tilt_grubu"]["am_eksene_dik_uzaklik_mm"], 2), "kafanın (tilt grubu %s g) AM'si ile tilt ekseni arası · tilt %s°" % (
        sayi(KF["tilt_grubu"]["kutle_g"], 0), aralik(TA.TILT_ARALIK))),
    ("×%s" % sayi(o["secilen"], 2), "kol boyu %s → %s mm (karar; tüp +%s, ön kol +%s, yaka +%s) · omuz S1 statik momenti ×%s · omuz servoları %s" % (
        sayi(o["boy_eski_mm"], 1), sayi(o["boy_yeni_mm"], 1), sayi(o["ust_kol_uzama_mm"], 0), sayi(o.get("on_kol_uzama_mm", 0), 1),
        sayi(o["el_uzama_mm"], 0), sayi(mo["oran"], 2), SERVO)),
    ("+%s mm" % sayi(TA.DY, 0), "uzama gövdede: 2 sabit kesitli kabuk bandı (%s g) + direk %s mm (sigma 40×40)" % (sayi(uzatma_g, 0), sayi(TA.DIREK_L_YENI, 1))),
]

# dirsek catali karsilastirma gorseli: 8 mm kararinda (25 Ekim) 5 / 7 / 8, 7 mm'de 5 / 7
CATAL_GORSEL = "catal-5-7-8.png" if TA.CATAL_DIS_KOL > 7.0 else "catal-5-7.png"
gorsel = [("taslak-on.png", "Önden (ev pozu)"), ("taslak-yan.png", "Sağdan"), ("taslak-izometrik.png", "İzometrik"),
          ("taslak-kol.png", "Sağ kol yakın: ×%s, ön kol uzatıldı (dirsek → bilek %s mm), omuz %s" % (
              sayi(o["hedef"], 2), sayi(BB.get("on_kol", 0), 1), SERVO)),
          (CATAL_GORSEL, ("Dirsek çatalı dış kolu 5 / 7 / 8 mm (sağ kol; çatal kırmızı, horn cıvataları + pul gri, çevre yarı saydam): sütunlar 5 mm M3x8, "
                          "7 mm M3x10, 8 mm M3x12 + 2 pul; üstte önden, altta izometrik") if CATAL_GORSEL == "catal-5-7-8.png" else
           ("Dirsek çatalı dış kolu %s → %s mm (sağ kol; çatal kırmızı, horn cıvataları gri, çevre yarı saydam): üstte önce, altta sonra; "
            "solda önden, sağda izometrik" % (sayi(TA.CATAL_DIS_KOL_ESKI, 0), sayi(TA.CATAL_DIS_KOL, 0)))),
          ("karsilastirma-125-170-on.png", "125 cm (solda, mevcut tasarım) ve 170 cm taslak (sağda), önden, aynı ölçek"),
          ("karsilastirma-125-170-izo.png", "125 cm ve 170 cm, izometrik"), ("taslak-kafa.png", "Yeni kafa: 10,1\" ekran, kamera üstte"),
          ("taslak-kafa-arka.png", "Kafa arkadan: alt boyun açıklığı + arka çentik, havalandırma yarıkları"),
          ("taslak-govde-uzatma.png", "Gövde uzatma bantları (y 476,5 … 911,5): dikişler ve bindirme cıvataları"),
          ("taslak-govde-kesit.png", "Kesit (gövde kabuğunun ön yarısı kaldırıldı): 1235,5 mm direk, uzatma braketleri, kafa boynu ve adaptör")]

h = ["""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lale 170 Taslak</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
.sub{color:var(--mut);margin-bottom:18px}
.rozet{display:inline-block;background:var(--uy);color:#fff;border-radius:6px;padding:2px 9px;font-size:13px;font-weight:600;vertical-align:middle}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
table.sayi td:not(:first-child):not(:nth-child(2)){text-align:right;white-space:nowrap}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:21px}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:5px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.wide{grid-column:1/-1}
.not{color:var(--mut);font-size:13px}.bos{border:2px dashed var(--line);border-radius:10px;padding:14px;color:var(--mut)}
.t{color:var(--uy);font-weight:600}.uy{color:var(--uy);font-weight:600}
h3{font-size:16px;margin:20px 0 8px}
.sonuc{background:var(--card);border:2px solid var(--acc2);border-radius:12px;padding:14px 18px;margin:18px 0}.sonuc h2{margin-top:0;border:0}
.sonuc .cevap{font-size:19px;font-weight:700;margin:4px 0 8px}
.karar{background:rgba(47,134,212,.08);border-left:4px solid var(--acc2);border-radius:6px;padding:10px 14px;margin:12px 0}
</style></head><body><main>"""]
h.append("<h1>Lale 1,70 m taslak montajı <span class='rozet'>TASLAK</span></h1>")
h.append("<div class='sub'>21 Ekim 2026 kararları (hoca + ekip): boy 1700 mm (yerden kafa tepesine), yüz kafada 10\" sınıfı HDMI ekran (model belli değil), "
         "otonomi yok (lidar / lidar direği / haritalama kapsam dışı), kumanda telefondan. Mevcut modüller ve ana montaj değiştirilmedi; varyant "
         "<code>tasarim/freecad/taslak-170/</code> klasöründe. <span class='t'>Tahmini</span> işaretli değerler ölçülmedi.</div>")
h.append("<div class='karar'><b>Karar (Duffy, 24 Ekim 2026):</b> kol ×%s (%s), omuz servoları (S1, S2; iki kol) <b>%s</b> (eski %s; gövde aynı kabul, "
         "geometri değişmedi). Uzatma: üst kol tüpü +%s mm (×1,15'ten), ön kol +%s mm (yeni), el yakası +%s mm (×1,15'ten). Eski ×1,15 taslak "
         "<code>TASLAK_KOL=115</code> ile yeniden üretilir.</div>" % (
             sayi(o["hedef"], 2), esc(o.get("karar", "")), esc(SERVO), esc(TA.OMUZ_SERVO_ESKI["ad"]), sayi(o["ust_kol_uzama_mm"], 0),
             sayi(o.get("on_kol_uzama_mm", 0), 1), sayi(o["el_uzama_mm"], 0)))
h.append(yeniden_notu("sonuç kutusu ve analiz kartlarındaki (devrilme, servo, çarpışma)"))
h.append(RA.sonuc_kutusu())
h.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (esc(a), esc(b)) for a, b in kart + RA.kartlar()) + "</div>")

# ---------------------------------------------------------------------- gorseller
h.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap in gorsel:
    s = img64(ad)
    cls = " class='wide'" if ad in ("karsilastirma-125-170-on.png", "catal-5-7.png", "catal-5-7-8.png") else ""
    icerik = "<img src='%s' alt='%s'>" % (s, esc(cap)) if s else "<div class='bos'>görsel yok: taslak_gorsel.py çalıştırılmadı</div>"
    h.append("<figure%s>%s<figcaption>%s</figcaption></figure>" % (cls, icerik, esc(cap)))
h.append("</div>")

# ---------------------------------------------------------------------- degisenler
h.append("<h2>Değişenler (125 cm → 170 cm)</h2>")
karar_sat = [["<b>Kol + omuz (karar, Duffy 24 Ekim 2026)</b>", "kol oranı, omuz S1/S2 servoları",
              "kol ×1,15 → ×%s (el ucu omuz ekseninden %s mm); ek ön kola (+%s mm), tüp ve yaka ×1,15'teki gibi; omuz servoları %s → %s "
              "(4 adet, iki kol; gövde aynı kabul, geometri değişmedi)" % (sayi(o["hedef"], 2), sayi(o["boy_yeni_mm"], 1), sayi(o.get("on_kol_uzama_mm", 0), 1),
                                                                          esc(TA.OMUZ_SERVO_ESKI["ad"]), esc(SERVO))]]
h.append(tablo(["Modül", "Parça / konu", "Değişiklik"], karar_sat + [[esc(a), esc(b), esc(c)] for a, b, c in AN["degisen"]]))
h.append("<p class='not'>Boy zinciri: omuz ekseni (travers merkezi) %s → %s mm; kafa yereli = traversin üst yüzü (y %s); kafa kabuğu altı yerel %s, "
         "üstü %s (eski 275). Uzama 476,5 dikişinin üstünde: taban, etek, gövde alt bandı ve alt gövde braketleri yerinde.</p>" % (
             sayi(A.S3, 0), sayi(TA.S3_YENI, 0), sayi(TA.S3_YENI + 20, 0), sayi(TA.KAFA_ALT_YEREL, 0), sayi(TA.KAFA_UST_YEREL, 0)))

# ---------------------------------------------------------------------- kafa
h.append("<h2>Kafa: 10,1\" ekran, tilt ekseni ağırlık merkezinde</h2>")
tg, pg = KF["tilt_grubu"], KF["pan_grubu"]
h.append(tablo(["Grup", "Kütle (g)", "AM (mm)", "Not"], [
    ["Tilt grubu (Kafa_Bas)", sayi(tg["kutle_g"], 1), am(tg["am"], 1), "AM'nin tilt eksenine dik uzaklığı %s mm (eksenden y %s, z %s); x yönü tilt torkunu etkilemez" % (
        sayi(tg["am_eksene_dik_uzaklik_mm"], 3), sayi(tg["am_eksene_gore"]["y"], 2), sayi(tg["am_eksene_gore"]["z"], 2))],
    ["Pan grubu (Kafa_Boyun + Kafa_Bas)", sayi(pg["kutle_g"], 1), am(pg["am"], 1), "AM'nin pan eksenine dik uzaklığı %s mm" % sayi(pg["am_pan_eksenine_dik_uzaklik_mm"], 1)],
    ["Kafa gövdesi (traverse sabit)", sayi(KF["govde"]["kutle_g"], 1), am(KF["govde"]["am"], 1), "değişmedi, %s mm yukarı" % sayi(TA.DY, 0)],
    ["Kafa toplam", sayi(KF["kafa_toplam"]["kutle_g"], 1), am(KF["kafa_toplam"]["am"], 1), "125 cm kafa ~1,4 kg (7\" LCD 230 g)"],
], "sayi"))
h.append(tablo(["Eksen", "Nokta (mm)", "Yön", "Aralık (°)"], [
    ["Tilt (Kafa_Bas)", am(KF["tilt_ekseni"]["nokta"], 2), esc(KF["tilt_ekseni"]["yon"]), aralik(KF["tilt_ekseni"]["aralik"])],
    ["Pan (Kafa_Boyun)", am(KF["pan_ekseni"]["nokta"], 2), esc(KF["pan_ekseni"]["yon"]), aralik(KF["pan_ekseni"]["aralik"])],
]))
h.append("<ul><li>Ekran: <b>%s</b>; cam %s × %s, kalınlık ~%s mm, <span class='t'>%s g tahmini</span> (robot_cad m_l10). Kasanın ön plakası kullanılmaz: "
         "cam ön kabuğun 2 mm çerçevesine dayanır, 4 PETG tırnak arkadan bastırır (M3×8 ISO 7380 + ısıl gömme somun).</li>" % (
             esc(TA.EKRAN10["model"]), sayi(TA.EKRAN10["cam"][0], 2), sayi(TA.EKRAN10["cam"][1], 2), sayi(TA.EKRAN10["kalinlik"], 0),
             sayi(TA.EKRAN10["kutle_g"], 0)))
h.append("<li>Denge: ekranın eksene göre yüksekliği dy = %s mm ve arka dış yüz zb = %s mm sekant yöntemiyle çözüldü (%d adım). Kafa 270 × 215 × %s mm "
         "(genişlik × yükseklik × derinlik). Ekran önde (cam önü eksenin 44 mm önünde: çatalın ön ağı tilt süpürmesinde ekran arkasına değmesin); "
         "karşı ağırlık Pi 5 + 5 V çevirici + tabla + derin arka kabuk.</li>" % (
             sayi(KF["denge"]["dy"], 2), sayi(KF["denge"]["zb"], 2), len(KF["denge"]["gecmis"]), sayi(47 - KF["denge"]["zb"], 0)))
h.append("<li>Tilt ekseni eski çatalda; çatal + tilt servosu + 625ZZ pimi <b>boyun yükseltme adaptörü</b> (PETG, h = %s mm) ile yukarı alındı: tilt ekseni "
         "kafa yerelinde y %s → %s. Pan düzeni (iki 6808-2RS, pan MG996R) değişmedi.</li>" % (
             sayi(KF["adaptor_h_mm"], 2), sayi(KF["tilt_eski_kafa_yereli_y"], 0), sayi(KF["tilt_ekseni_kafa_yereli_y"], 2)))
h.append("<li>Kafa alt duvarında boyun açıklığı x ±38 (R30 boyun × tilt ±15° süpürmesi); arka duvarın altında 12 mm çentik: tilt −15°'te arka-alt köşe "
         "rulman yuvasına iniyordu (kısa kontrolde bulundu, düzeltildi).</li>"
         "<li>Kafa kabuğu 4 baskı parçası (ön/arka × sağ/sol): x = 0 dikişinde 16 mm bindirme dili, tepe dikiş cıvataları havşalı (boy 1700'ü geçmesin).</li></ul>")

# ---------------------------------------------------------------------- kol
h.append("<h2>Kol: ×%s (karar) ve omuz %s</h2>" % (sayi(o["secilen"], 3), esc(SERVO)))
h.append(KOL_ANALIZ_LINK)
h.append("<p>Boyla orantılı uzatma ×1,36 olurdu (el ucu %s mm). Karar ×%s (%s): el ucu omuz ekseninden %s → %s mm. Uzatma dağılımı: üst kol tüpü +%s mm, "
         "<b>ön kol +%s mm</b>, el yakası +%s mm.</p>" % (
             sayi(o["boy_eski_mm"] * 1.36, 0), sayi(o["hedef"], 2), esc(o.get("karar", "")), sayi(o["boy_eski_mm"], 1), sayi(o["boy_yeni_mm"], 1),
             sayi(o["ust_kol_uzama_mm"], 0), sayi(o.get("on_kol_uzama_mm", 0), 1), sayi(o["el_uzama_mm"], 0)))
if BB:
    h.append(tablo(["Bölüm (ev pozu, dikey)", "125 cm (mm)", "Taslak (mm)", "Not"], [
        ["Üst kol: S1 ekseni → dirsek ekseni", sayi(-A.DIRSEK["eksen_y"], 1), sayi(BB["ust_kol"], 1), "tüp 100 → %s mm" % sayi(100 + o["ust_kol_uzama_mm"], 0)],
        ["Ön kol: dirsek ekseni → bilek ekseni (horn)", sayi(A.DIRSEK["eksen_y"] - A.DIRSEK["bilek_nokta"][1], 1), sayi(BB["on_kol"], 1),
         "ön kol gövdesi dirsek ve bilek servosu arasında uzatıldı"],
        ["El: bilek ekseni → el ucu", sayi(A.DIRSEK["bilek_nokta"][1] - A.DIRSEK["el_ucu"][1], 1), sayi(BB["el"], 1), "yaka 13,6 → 32,6 mm (×1,15'teki gibi)"],
        ["<b>Toplam</b>", sayi(o["boy_eski_mm"], 1), sayi(BB["toplam"], 1), "×%s" % sayi(o["secilen"], 4)],
    ], "sayi"))
h.append("<ul><li><b>Neden ön kol:</b> kol analizi uzatmayı el yakasına değil tüpe ve/veya ön kola vermeyi önerdi (yakadaki 2× M3 ve bilek MG996R mili konsolu "
         "zayıf halka; yaka 32,6 mm'de kaldı). Tüp ile ön kol arasında ön kol seçildi: sınırlayıcı eklem omuz S1 (DS3235 ×1,25 ivmeli pay ~1,6, kol analizi). "
         "Ek tüpe verilseydi tüm dirsek grubu (dirsek çatalı + ön kol + iki servo + el, ~380 g) uzaklaşırdı; ön kola verilince yalnız bilek servosu + el "
         "(~160 g) ve ön kol uzatması uzaklaşıyor, S1 momenti daha az artıyor. Tüp +Y basılıyor (eğilme katmanlar arası), bu yüzden uzatılmadı. Dirsek MG996R "
         "payı geniş (statik ~2 / durma 9,4 kg·cm, kol analizi). Oran da insan koluna yaklaşır (üst kol / ön kol ×1,15'te %s, şimdi %s; insanda ~1,3).</li>" % (
             sayi(203.0 / 83.1, 2), sayi(BB["ust_kol"] / BB["on_kol"], 2) if BB else "?"))
_HS = RA.H["servo"]["yeni-444"]["kol"] if RA.H else None
h.append("<li>Omuz torku: kol öne yatayken S1 statik momenti ×%s (125 cm %s, taslak %s g·mm). %s</li>" % (
    sayi(mo["oran"], 2), sayi(mo["eski_gmm"], 0), sayi(mo["yeni_gmm"], 0),
    ("Kontrol ajanı hesabı (Servo bölümü): %s ile S1 statik pay %s×, ivmeli %s×, S2 %s×, elde ~%s g (2×); ilk kol analizi doğrusal modelle statik ~2,7×, "
     "ivmeli ~1,6× öngörmüştü." % (esc(_HS[0]["servo"]), sayi(_HS[0]["yuksuz_pay"], 2), sayi(_HS[0]["toplam_pay"], 2), sayi(_HS[1]["yuksuz_pay"], 2),
                                  sayi(_HS[0]["izinli_yuk_2x_g"], 0))) if _HS else "Servo payları analiz/hesap.json'da."))
h.append("<li>Omuz servoları <b>%s</b> (eski %s): gövde DS3218 ile aynı kabul edildi (40 × 20 × 40, kulak delikleri 49,5 × 10, 25T çıkış, 60 g); omuz yuvası "
         "ve geometri değişmedi, yalnız ad / kod / not. Gövde yüksekliği kaynaklarda 38,5 / 40 / 40,5 mm: <span class='uy'>servo gelince kumpasla "
         "doğrulanacak</span> (yuva derinliği ve horn düzlemi buna bağlı).</li>" % (esc(SERVO), esc(TA.OMUZ_SERVO_ESKI["ad"])))
h.append("<li>Üst kütle: kol kütlesi %s → %s g (her kol); uzun ve ağır kol, %s mm omuz yüksekliğinde devrilme momentini büyütür.</li>" % (
    sayi(o["kol_kutle_g"]["eski"], 0), sayi(o["kol_kutle_g"]["yeni"], 0), sayi(TA.S3_YENI, 0)))
_b = yer["bosluk"].get("el <-> govde kabugu (ev pozu, sag)")
_CK = yer.get("catal")
if _CK and TA.CATAL_DIS_KOL > TA.CATAL_DIS_KOL_ESKI:
    _ci = _CK["bilgi"]["sag"]
    _KA = RA._kol_analiz()
    _cd = None
    try:
        _cd = [x for x in _KA["varyant"] if abs(x["oran"] - 1.25) < 1e-9][0]["servo"][SERVO]["catal_dis_kol"]
    except Exception:
        pass
    if _cd:
        _ts = [(k, _cd[k]) for k in sorted(_cd, key=float)]          # 5 / 7 / 8 (kontrol ajani, 24 Ekim gece)
        _z = lambda L_: " → ".join(("<b>%s</b>" if abs(float(k) - TA.CATAL_DIS_KOL) < 1e-9 else "%s") % sayi(r["dis_kol"][L_]["sf"], 2) for k, r in _ts)
        _sf = ("Kol analizi yeniden koşuldu (kontrol ajanı): dış kol SF (%s mm) L3 stall %s, L4 darbe %s (×1,25 + %s; ölçüt ≥ 2 güvenli, "
               "1,2–2 sınırda). Dayanım ve çarpışma ayrıntısı: <a href='#catal'>Dirsek çatalı kontrolü</a>." % (
                   " / ".join(k for k, _ in _ts), _z("L3"), _z("L4"), esc(SERVO)))
    else:
        _sf = ("Kesit ∝ kalınlık: dış kol gerilmesi ×%s, SF yaklaşık L3 %s / L4 %s (<span class='t'>tahmini</span>; kol analizi yeniden koşulmadı)." % (
            sayi(TA.CATAL_DIS_KOL_ESKI / TA.CATAL_DIS_KOL, 2), sayi(1.86 * TA.CATAL_DIS_KOL / TA.CATAL_DIS_KOL_ESKI, 2), sayi(0.77 * TA.CATAL_DIS_KOL / TA.CATAL_DIS_KOL_ESKI, 2)))
    h.append("<li><b>Dirsek çatalı dış kolu %s → %s mm</b> (horn tarafı, gövdeden uzak kol; 5 mm'de kol analizi L3 servo stall SF 1,86, L4 darbe 0,77). "
             "İç yüzü horn'a oturduğu için kalınlaştırma dışa (+X, dış yüz x %s → %s, omuz yereli); köprü aynı düzleme uzadı%s. Horn cıvataları M3x8 → %s "
             "(baş %s mm dışarıda, uç horn'da aynı yerde: horn'da 3,0 mm diş, servo kasasına 3,3 mm). Delikler, 625ZZ, pim, eksenler değişmedi. "
             "Kütle %s → %s g (kol başına, cıvatalar hariç). %s %s</li>" % (
                 sayi(TA.CATAL_DIS_KOL_ESKI, 0), sayi(TA.CATAL_DIS_KOL, 0), sayi(_CK["dis_yuz_x_yerel"][0], 1), sayi(_CK["dis_yuz_x_yerel"][1], 1),
                 ", 45° köprü desteği dış yüze kadar uzadı" if TA.CATAL_DESTEK_DIS else "",
                 ("M3x%s + %d × DIN 125-A M3 pul (%s mm; M3x11 standart değil)" % (sayi(TA.HORN_CIVATA_L, 0), TA.HORN_PUL_N, sayi(TA.HORN_PUL_T, 1)))
                 if TA.HORN_PUL_N else "M3x%s" % sayi(TA.HORN_CIVATA_L, 0),
                 sayi(TA.HORN_CIVATA_L - 8.0, 0), sayi(_ci["eski_g"], 1), sayi(_ci["yeni_g"], 1), _sf,
                 "<b>Karar: Duffy, 25 Ekim 2026 (8 mm).</b>" if TA.CATAL_DIS_KOL == 8.0 else "<span class='uy'>Duffy onayı bekliyor</span> (görünüm + çarpışma şartı)."))
h.append("<li>Değişen PETG parçalar: üst kol tüpü, ön kol gövdesi (tek parça kaldı), el%s; servolar, flanş aynen. Dirsek çatalı / ön kol / el ↔ gövde "
         "kabuğu ev pozunda %s mm (125 cm ~3,8).</li></ul>" % (
             ", dirsek çatalı (dış kol)" if TA.CATAL_DIS_KOL > TA.CATAL_DIS_KOL_ESKI else "; dirsek çatalı", sayi(_b["mm"], 1) if _b else "−"))
satir = []
for t in ("sag", "sol"):
    k = KL[t]
    for ad, v in k["bilesenler"].items():
        satir.append(["sağ" if t == "sag" else "sol", esc(ad), sayi(v["kutle_g"], 1), am(v["am"], 1)])
    for ad, et in (("S1_ile_donen", "S1 ile dönen"), ("S2_ile_donen", "S2 ile dönen"), ("dirsek_ile_donen", "dirsek ile dönen"),
                   ("bilek_ile_donen", "bilek ile dönen")):
        satir.append(["sağ" if t == "sag" else "sol", "<b>%s</b>" % et, sayi(k[ad]["kutle_g"], 1), am(k[ad]["am"], 1)])
h.append(tablo(["Kol", "Bileşen", "Kütle (g)", "AM (mm)"], satir, "sayi"))
h.append(tablo(["Eksen (sağ kol)", "Nokta (mm)", "Yön", "Aralık (°)"], [
    [n, am(KL["sag"][a]["nokta"], 2), esc(KL["sag"][a]["yon"]), aralik(KL["sag"][a]["aralik"])] for n, a in (
        ("Omuz öne-arka (S1)", "omuz_ekseni_S1"), ("Omuz yana açma (S2)", "S2_ekseni"), ("Dirsek", "dirsek_ekseni"), ("Bilek", "bilek_ekseni"))]))
h.append("<p class='not'>El ucu (sağ): %s mm. Sol kol X aynası.</p>" % am(KL["sag"]["el_ucu"], 1))

# ---------------------------------------------------------------------- kutle tablosu
h.append("<h2>Kütle ve ağırlık merkezi (modül bazında)</h2>")
sat = []
for m in K["moduller"]:
    sat.append([esc(m["ad"]), sayi(m["eski"]["kutle_g"], 0), sayi(m["yeni"]["kutle_g"], 0), sayi(m["yeni"]["kutle_g"] - m["eski"]["kutle_g"], 0),
                am(m["eski"]["am"], 0), am(m["yeni"]["am"], 0)])
sat.append(["<b>toplam (parçalar)</b>", sayi(E["kutle_g"], 0), sayi(T["kutle_g"], 0), sayi(T["kutle_g"] - E["kutle_g"], 0), am(E["am"], 1), am(T["am"], 1)])
sat.append(["<b>+ kablo payları</b>", sayi(E["kutle_payli_g"], 0), sayi(T["kutle_payli_g"], 0), sayi(T["kutle_payli_g"] - E["kutle_payli_g"], 0),
            am(E["am_payli"], 1), am(T["am_payli"], 1)])
h.append(tablo(["Modül", "125 cm (g)", "170 cm (g)", "Fark", "AM 125 (mm)", "AM 170 (mm)"], sat, "sayi"))
h.append("<p class='not'>Paylar (<span class='t'>tahmini</span>): %s. Parça bazında kütle/AM, gruplar ve eklemler: <code>kutle.json</code>. Destek poligonu "
         "(teker merkezleri, x; z): %s.</p>" % ("; ".join("%s %s g, %s" % (esc(p["ad"]), sayi(p["kutle_g"], 0), am(p["merkez"], 0)) for p in T["paylar"]),
                                                ", ".join("(%s; %s)" % (sayi(d["x"], 0), sayi(d["z"], 0)) for d in K["taban"]["destek_poligonu_teker_merkezleri"])))

# ---------------------------------------------------------------------- baglantilar
h.append("<h2>Bağlantı tablosu (yeni ve değişen bağlantılar)</h2>")
h.append(tablo(["Bağlantı", "Eleman", "Adet", "Parçalar", "Not", "Durum"],
               [[esc(b["ad"]), esc(b["tip"]), str(b["adet"]), esc(" / ".join(b["parcalar"])), esc(b.get("aciklama", "")), DURUM.get(b["durum"], b["durum"])]
                for b in AN["baglar"]]))
h.append("<p class='not'>Değişmeyen bağlantılar (travers-direk köşe bağlantıları, omuz yuvası 4× M6, kabuk bindirmeleri, Nextion, etek, taban) modül "
         "raporlarındaki gibi; yalnız konumları taşındı. Uzatma bandı dikişleri kabuk modülünün bindirme kuralını kullanır (12 mm dil, 0,25 mm boşluk, damla boss).</p>")

# ---------------------------------------------------------------------- baski
h.append("<h2>Baskı tablosu (okul yazıcısı 250 × 250 × 250 mm, parça hedefi ≤ 230)</h2>")
sat = []
for b in sorted(AN["baski"], key=lambda x: ({"yeni": 0, "degisti": 1, "tasindi": 2, "ayni": 3}[x["durum"]], x["modul"], x["ad"])):
    ok = "<span class='ok'>evet</span>" if b["hedef_230"] else ("<span class='t'>250'ye sığar</span>" if b["sigar_250"] else "<span class='no'>hayır</span>")
    sat.append([esc(b["ad"]), esc(b["modul"]), DURUM[b["durum"]], "%s × %s × %s" % (sayi(b["olcu"][0], 0), sayi(b["olcu"][1], 0), sayi(b["olcu"][2], 0)),
                ok, sayi(b["kutle_g"], 1), sayi(b["sure_saat"], 1), esc(b["yon"])])
h.append(tablo(["Parça", "Modül", "Durum", "Ölçü (mm, baskı yönünde)", "≤ 230", "Kütle (g)", "Süre (sa)", "Baskı yönü"], sat))
yb = [b for b in AN["baski"] if b["durum"] in ("yeni", "degisti")]
h.append("<p class='not'>Yeni + değişen baskı parçası %d adet, %s g PETG, ~%s saat (<span class='t'>tahmini</span>: 10 mm³/s ortalama). Tüm robot %d baskı parçası, %s g. "
         "Ölçü: baskı yönünde en küçük tabla dikdörtgeni (tablada döndürme dahil); yönü bilinmeyen mevcut parçada en küçük sığan yön.</p>" % (
             len(yb), sayi(sum(b["kutle_g"] for b in yb), 0), sayi(sum(b["sure_saat"] for b in yb), 0), len(AN["baski"]),
             sayi(sum(b["kutle_g"] for b in AN["baski"]), 0)))

# ---------------------------------------------------------------------- kisa yerlesim kontrolu
h.append("<h2>Kısa yerleşim kontrolü (CAD ajanı)</h2>")
h.append("<p>Ev pozunda yeni/değişen parçalar × tüm parçalar ve farklı ötelenen parça çiftleri (%d aday çift, eşik %s mm³); kafa pan {−90, −45, 0, 45, 90}° × "
         "tilt {−15, −7,5, 0, 7,5, 15}° süpürmesinde kafa ve boyun ↔ kafa gövdesi, kabuk, omuzlar, iskelet. Tam çarpışma taraması değildir.</p>" % (
             yer["aday_cift"], sayi(yer["esik_mm3"], 1)))
h.append("<ul><li>Taslaktan gelen çakışma: <b class='%s'>%d</b>%s</li>" % (
    "ok" if not taslak_cak else "no", len(taslak_cak),
    (": " + "; ".join("%s × %s (%s mm³)" % (esc(c["a"]), esc(c["b"]), sayi(c["hacim_mm3"], 1)) for c in taslak_cak)) if taslak_cak else ""))
h.append("<li>Mevcut tasarımdan gelen (125 cm'de de aynı hacim): %s</li>" % ("; ".join("%s (%s) × %s (%s mm³)" % (
    esc(c["a"]), esc(c["a_modul"]), esc(c["b"]), sayi(c["hacim_mm3"], 1)) for c in mevcut_cak) or "yok"))
h.append("<li>Kafa süpürmesi: çakışan poz <b class='%s'>%d / %d</b></li>" % ("ok" if not sup_cak else "no", sup_cak, len(yer["kafa_suprulme"])))
KT = yer.get("kol_kisa")
if KT:
    _ck = {}
    for c in KT["cakisma"]:
        _ck.setdefault((c["a"], c["b"]), []).append(c)
    h.append("<li>Kol kaba ızgarası (sağ kol, ön kol + el; S1 %s × S2 %s × dirsek %s × bilek %s = %d poz; gövde kabuğu, iskelet, kafa ev pozunda, omuz ve "
             "kendi üst kolu): çakışan poz <b class='%s'>%d / %d</b>%s. El en alt y %s mm (poz %s). İnce tarama ve kafa × kol (pan/tilt) kontrol ajanında.</li>" % (
                 "/".join(sayi(x, 0) for x in KT["izgara"]["S1"]), "/".join(sayi(x, 0) for x in KT["izgara"]["S2"]),
                 "/".join(sayi(x, 0) for x in KT["izgara"]["dirsek"]), "/".join(sayi(x, 0) for x in KT["izgara"]["bilek"]), KT["poz"],
                 "ok" if not KT["cakisan_poz"] else "no", KT["cakisan_poz"], KT["poz"],
                 (": " + "; ".join("%s × %s (%d poz, en çok %s mm³, ör. %s)" % (esc(a), esc(b), len(v), sayi(max(x["hacim_mm3"] for x in v), 1), v[0]["poz"])
                                   for (a, b), v in _ck.items())) if _ck else "",
                 sayi(KT["en_dusuk_el_y"]["y"], 0), KT["en_dusuk_el_y"]["poz"]))
CK = yer.get("catal")
if CK and CK["kalinlik_mm"] > CK["eski_mm"]:
    def _mn(ls, k):
        v = [r[k] for r in ls if r[k] is not None]
        return min(v) if v else None
    _om5 = [r["eski"][0] for r in CK["omuz"] if r["eski"]]
    _om7 = [r["yeni"][0] for r in CK["omuz"] if r["yeni"]]
    _om7r = min((r for r in CK["omuz"] if r["yeni"]), key=lambda r: r["yeni"][0], default=None)
    _yak = CK["ev_pozu_yaklasan"]
    h.append("<li>Dirsek çatalı %s → %s mm (sağ kol; aynı komşulara eski ve yeni çatal): ev pozunda 15 mm içindeki parçalar %d, yaklaşan %s; "
             "dirsek 0…105° (5°) ön kol + servolara (eş eksenli mil, rulman, pim hariç) en az %s → %s mm; S1 × S2 kaba ızgarada (%d poz) gövde kabuğu / iskelet / kafa / omuz gövdesi + göbeğe en az %s → %s mm%s.</li>" % (
                 sayi(CK["eski_mm"], 0), sayi(CK["kalinlik_mm"], 0), len(CK["ev_pozu"]),
                 ("<b class='ok'>yok</b>" if not _yak else "; ".join("%s %s → %s mm" % (esc(r["parca"]), sayi(r["eski_mm"], 2) if r["eski_mm"] is not None else "&gt; 15",
                                                                                         sayi(r["yeni_mm"], 2)) for r in _yak)),
                 sayi(_mn(CK["dirsek"], "eski_mm"), 1), sayi(_mn(CK["dirsek"], "yeni_mm"), 1), len(CK["omuz"]),
                 sayi(min(_om5), 1) if _om5 else "&gt; 40", sayi(min(_om7), 1) if _om7 else "&gt; 40",
                 (" (%s, poz S1/S2 %s)" % (esc(_om7r["yeni"][1]), _om7r["poz"])) if _om7r else ""))
BOS_AD = {"kafa kabugu <-> omuz (ev pozu)": "kafa kabuğu ↔ omuz (ev pozu)", "kafa kabugu <-> govde kabugu ust kapagi": "kafa kabuğu ↔ gövde kabuğu üst kapağı",
          "kafa (Bas) <-> egme catali / tilt servosu / adaptor": "kafa ↔ eğme çatalı / tilt servosu / adaptör (eski kafada da 1,0)",
          "ekran <-> catal / adaptor": "ekran ↔ çatal / adaptör (ev pozu)", "el <-> govde kabugu (ev pozu, sag)": "kol ↔ gövde kabuğu (ev pozu, sağ)"}
for ad, v in yer["bosluk"].items():
    h.append("<li>En küçük boşluk, %s: %s</li>" % (esc(BOS_AD.get(ad, ad)), ("%s mm (%s / %s)" % (sayi(v["mm"], 1), esc(v["a"]), esc(v["b"]))) if v else "&gt; 60 mm"))
h.append("</ul>")

# ---------------------------------------------------------------------- analiz bolumleri (analiz ajani, taslak_rapor_analiz.py)
h.append("<h2>Bağımsız doğrulama: kütle ve AM</h2>")
h.append(yeniden_notu("doğrulama"))
h.append(RA.dogrulama())
h.append("<h2>Devrilme</h2>")
h.append(yeniden_notu("devrilme"))
h.append(RA.devrilme())
h.append("<h2>Motor (taban tahriki)</h2>")
h.append(yeniden_notu("motor"))
h.append(RA.motor())
h.append("<h2>Servo torkları (omuz, dirsek, kafa pan/tilt)</h2>")
h.append(yeniden_notu("servo (omuz %s ile)" % esc(SERVO)))
h.append(RA.servo())
h.append("<h2>Kol oranı: ×1,15 / ×1,25 / ×1,36 (hesap; karar ×%s)</h2>" % sayi(o["hedef"], 2))
h.append(KOL_ANALIZ_LINK)
h.append(yeniden_notu("kol oranı"))
h.append(RA.kol_orani())
h.append("<h2>Çarpışma taraması (tüm eklem aralıkları)</h2>")
h.append(yeniden_notu("çarpışma (kol zinciri, iki kol, kafa × kol; uzun ön kol yasak bölgeyi değiştirebilir)"))
h.append(RA.carpisma())
if TA.CATAL_DIS_KOL > TA.CATAL_DIS_KOL_ESKI:
    h.append("<h2 id='catal'>Dirsek çatalı dış kolu %s → %s mm: kontrol (geometri, çarpışma, dayanım)</h2>" % (
        sayi(TA.CATAL_DIS_KOL_ESKI, 0), sayi(TA.CATAL_DIS_KOL, 0)))
    h.append(RA.catal())

# ---------------------------------------------------------------------- acik isler, varsayimlar
acik_ek = [
    ["Göğüs Nextion ekranı", "taslakta yerinde (merkez y %s mm), karar açık" % sayi(A.GOGUS_Y + TA.DY, 0),
     "kaldırılırsa göğüs bandı penceresi kapanır, 535 g düşer (AM y ~15 mm iner; devrilmeye etkisi küçük, Önlemler tablosu)", "Duffy"],
    ["Uzatma bandı dikiş basamağı", "kesit dikişin 12 mm üstündeki kesit: alt (476,5) ve üst (911,5) dikişte ~0,7 mm dışa basamak", "görünür, zararsız", "kabuk"],
    ["Kafanın altı açık", "boyun açıklığı + arka çentik", "toz / parmak için esnek boyun körüğü düşünülebilir", "tasarım"],
    ["Kafa içi kablolar", "micro HDMI Pi → ekran (sağda), CSI FPC Pi → kamera (~200 mm)", "kablo boyları ve kafa içi kablo payı (25 g, tahmini) doğrulanacak", "elektrik"],
] + ([
    ["×%s + %s yeniden analiz" % (sayi(o["hedef"], 2), esc(SERVO)), "devrilme, servo payları, kol oranı, tam çarpışma taraması ve sonuç kutusu ×1,15 + DS3218MG geometrisine ait",
     "kontrol ajanı: <code>taslak_analiz.py</code> (tüm bölümler) + <code>taslak_hesap.py</code>", "kontrol ajanı"]] if ANALIZ_ESKI else []) + [
    ["%s gövde yüksekliği" % esc(SERVO), "kaynaklarda 38,5 / 40 / 40,5 mm (DS3218 ile aynı kabul edildi)", "servo gelince kumpasla ölç; farklıysa omuz yuvası / horn düzlemi "
     "kontrolü. Robocombo ilanı açıklamada 'RDS3235 ... U braket dahil' diyor: satıcıya sorulacak (kol-analiz NOTLAR)", "Duffy + satın alma"],
    ["Ön kol uzaması: kablo ve baskı", "bilek servosu kablosu +%s mm (MG996R 30 cm kablo); ön kol gövdesi tek parça (baskı tablosunda)" % sayi(o.get("on_kol_uzama_mm", 0), 1),
     "kablo yolu (<code>dirsek/kablo_yolu.py</code>, arayuz.KOL_KABLO) ön kol boyuna göre güncellenmeli; servo uzatma boyu", "elektrik + tasarım"],
] + ([
    (["Dirsek çatalı dış kolu 8 mm (karar: Duffy, 25 Ekim 2026)",
      "tasarım ajanı: 8 mm + M3x12 + 2 × DIN 125-A M3 pul, 45° destek dış yüze (gorsel/catal-5-7-8.png). Kontrol ajanı (24 Ekim gece): geometri, tam "
      "çarpışma taraması ve kol analizi 8 mm ile yeniden koşuldu (<a href='#catal'>Dirsek çatalı kontrolü</a>)",
      "BOM'a M3x12 (8) + DIN 125-A M3 pul (16) maliyet.json'da eklenmedi; horn cıvatası sıkma torku PETG'de ~0,5 N·m'yi geçmemeli (pul ile; "
      "<span class='t'>tahmini</span>)", "Duffy"] if TA.CATAL_DIS_KOL == 8.0 else
     ["Dirsek çatalı dış kolu %s mm (Duffy onayı)" % sayi(TA.CATAL_DIS_KOL, 0),
      "kontrol: geometri tuttu, çarpışma taramalarında 5 mm ile fark yok; stall SF güvenli, darbe (L4) hâlâ 1,2 altında (Dirsek çatalı kontrolü bölümü)",
      "onay Duffy'de (görünüm: gorsel/catal-5-7.png). L4 için seçenekler (onaylanmadı, uygulanmadı): 8 mm (yalnız hesapla L4 ~1,2), PETG-CF, jest hız sınırı; "
      "BOM'a M3x10 (8 adet) maliyet.json'da eklenmedi; 45° destek x 224,9'da bitiyor (dış 2 mm şerit köprü üstünde düz)", "Duffy"])]
    if TA.CATAL_DIS_KOL > TA.CATAL_DIS_KOL_ESKI else []) + [
    ["Onaylanmamış öneriler (kol analizi, UYGULANMADI)", "kol-analiz/rapor.html Düzeltmeler: S2 horn tarafı destek rulmanı (6806-2RS), göbekte ikinci 6808, kelepçeli "
     "horn (25T Al horn kanalı DS3235 durmada SF ~1,3), S1/S2 uzatmalarında 20 AWG, XL4016 çıkışı 6,4 V, yazılım hız / temas sınırları",
     "Duffy onaylarsa ayrı iş olarak modellenir (omuz yuvası, göbek, elektrik); bu taslakta geometri değişmedi", "Duffy"],
]
h.append("<h2>Açık işler</h2>" + RA.acik_isler(TA, KF, uzatma_g, acik_ek))
vars_ = [
    "Yüz ekranı ölçüleri Waveshare 10.1inch HDMI LCD (B) (04-parca-olculeri.md); <span class='t'>tahmini model</span>, kütle 600 g <span class='t'>tahmini</span>.",
    "Kafa kabukları 2,5 mm PETG, etkin doluluk 0,90; küçük PETG parçalar 0,80 (eski kafa / dirsek ile aynı, <span class='t'>tahmini</span>).",
    "Kablo payları: taban 400 g (mevcut tahmin), gövde uzaması 45 g, kafa içi 25 g (kafa AM'sine katılmadı); hepsi <span class='t'>tahmini</span>.",
    "Baskı süresi 10 mm³/s ortalama debiyle <span class='t'>tahmini</span>; okul yazıcısı 25 × 25 × 25 cm (hocanın söylediği, model doğrulanmadı).",
    "Kol ×%s Duffy'nin kararı (24 Ekim 2026, kol analizi önerisi); ek boyun ön kola verilmesi tasarım ajanının kaba moment karşılaştırmasıyla (S1 momenti ön kolda ~8.000, tüpte ~15.000 g·mm artış, <span class='t'>tahmini</span>). Eski ×1,15: <code>TASLAK_KOL=115</code>." % sayi(o["hedef"], 2),
    "Omuz servosu %s: gövde DS3218 ile aynı (40 × 20 × 40, kulak delikleri 49,5 × 10, 25T), 60 g; yükseklik <span class='t'>doğrulanmadı</span> (38,5 / 40 / 40,5)." % esc(SERVO),
    "Devrilmede fren 1,5 m/s² (acil stop, <span class='t'>tahmini</span>); motor durma torku 21 kg·cm satıcı etiketi (ölçülmedi); servo ivme profili 60°/0,4 s (<span class='t'>tahmini</span>).",
    "M3 saplama DIN 976 ve DIN 985 somun stokta varsayıldı; saplama %s mm'ye kesilir." % sayi(KF["adaptor_h_mm"] + 13.0, 0),
    "125 cm değerleri güncel modül betiklerinden (aynı yükleyiciler) hesaplandı; kayıtlı ana montaj çıktısı (montaj-analiz.json) daha eski.",
    "Mevcut FreeCAD tasarımında lidar yok; taslağa da eklenmedi.",
]
h.append("<h2>Varsayımlar</h2><ul>" + "".join("<li>%s</li>" % a for a in vars_) + "</ul>")
h.append("<h2>Dosyalar ve çalıştırma</h2><ul>"
         "<li><code>taslak_ayar.py</code> parametreler (boy, uzama, kol <code>TASLAK_KOL=115|125</code>, omuz servosu <code>TASLAK_OMUZ_SERVO</code>, ekran, taban genişliği, tabla) · <code>kafa10.py</code> yeni kafa + adaptör + denge · "
         "<code>taslak_parcalar.py</code> modülleri yükleyip varyantı kurar · <code>taslak_montaj.py</code> FCStd / STEP / kutle.json / taslak-analiz.json · "
         "<code>taslak_gorsel.py</code> (GUI) görseller · <code>taslak_rapor.py</code> bu rapor</li>"
         "<li>Analiz (analiz ajanı): <code>taslak_analiz.py</code> (FreeCAD; <code>TA_BOLUM=kutle|dogrula|statik|kol_sag|kol_sol|kolkol|kafa|kafakol_sag|kafakol_sol|kafakol_ince_sag|kafakol_ince_sol|catal|catal_geo</code>, "
         "<code>TA_ROBOT=eski</code> aynı taramayı 125 cm robotta koşar, <code>TASLAK_TABAN_W</code>) → <code>analiz/*.json</code>; <code>python taslak_hesap.py</code> "
         "(devrilme, motor, servo, kol oranı) → <code>analiz/hesap.json</code>; rapor bölümleri <code>taslak_rapor_analiz.py</code></li>"
         "<li><code>FC_SCRIPT=.../taslak-170/taslak_montaj.py freecadcmd.exe C:/Users/Victus/.robot-cad/run_fc.py</code> (~7 dk), sonra aynı yolla "
         "<code>taslak_gorsel.py</code> (<code>freecad.exe</code>), sonra <code>python taslak_rapor.py</code>. Taban genişliği denemesi: <code>TASLAK_TABAN_W=520</code>.</li>"
         "<li>Çıktılar: <code>taslak-170.FCStd</code> (%d parça, %d grup, %d eklem), <code>taslak-170.step</code> (%d katı), <code>kutle.json</code>, "
         "<code>taslak-analiz.json</code>, <code>gorsel/</code></li></ul>" % (AN["parca_sayisi"], AN["grup_sayisi"], AN["eklem_sayisi"], AN["step_kati"]))
h.append("<p class='not'>Üretildi: %s · montaj süresi %s s</p></main></body></html>" % (datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), sayi(AN["sure_s"], 0)))
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(h))
print("rapor.html yazildi")
