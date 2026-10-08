# Taban modulu raporu (rapor.html, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: taban-analiz.json (taban_montaj.py), gorsel/*.png (taban_gorsel.py), ../arayuz.py.
# 2. asama girdileri: ../carpisma-sonuc.json (taban_tarama, bolumler), ../montaj/montaj-analiz.json, eklem-dogrulama.json,
# gui-kontrol.json, ../montaj/gorsel/montaj-taban*.png, regresyon (../omuz|iskelet/regresyon/fark.json, regresyon/moduller.json).
import os, sys, json, base64, html

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path.insert(0, UST)
import arayuz as A

G = os.path.join(HERE, "gorsel")
d = json.load(open(os.path.join(HERE, "taban-analiz.json"), encoding="utf-8"))
T = A.TABAN
Y = A.YAZICI


def esc(s):
    return html.escape(str(s))


def sayi(x, n=1):
    s = ("%." + str(n) + "f") % x
    tam, _, ond = s.partition(".")
    neg = tam.startswith("-")
    tam = tam.lstrip("-")
    gr = []
    while len(tam) > 3:
        gr.insert(0, tam[-3:])
        tam = tam[:-3]
    gr.insert(0, tam)
    return ("−" if neg and s.strip("-0.,") else "") + ".".join(gr) + ("," + ond if ond else "")


def img64(ad):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(G, ad), "rb").read()).decode()


def tablo(baslik, satirlar, sinif=""):
    h = ["<table class='%s'><tr>" % sinif + "".join("<th>%s</th>" % esc(b) for b in baslik) + "</tr>"]
    for s in satirlar:
        h.append("<tr>" + "".join("<td>%s</td>" % x for x in s) + "</tr>")
    h.append("</table>")
    return "".join(h)


def md(s):
    s = esc(s)
    out, b, c, i = [], False, False, 0
    while i < len(s):
        if s.startswith("**", i):
            out.append("</b>" if b else "<b>")
            b = not b
            i += 2
        elif s[i] == "`":
            out.append("</code>" if c else "<code>")
            c = not c
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def durum(ok):
    return "<span class='ok'>tamam</span>" if ok else "<span class='no'>sorun</span>"


def pay_sinif(x):
    return "ok" if x >= 2.0 else ("uy" if x >= 1.2 else "no")


R = d["robot"]["pozlar"]
POZ_AD = {"ev": "Ev pozu (kollar aşağıda)", "one": "İki kol öne uzanmış (S1 90°, düz)", "one_yuk": "İki kol öne + elde 0,5 kg (bilgi)",
          "one_yukari": "İki kol öne-yukarı (S1 135°)", "geri": "İki kol geride (S1 −45°)", "yan_tek": "Sağ kol yana açık (S2 90°), sol aşağıda"}
EV = R[0]
MOT = d["motor"]
AKU = d["aku"]
bag = d["baglanti_kontrol"]
bag_ok = sum(1 for b in bag if b["tamam"])
te = d["teker_etek"]
te_min = min(t["bosluk_mm"] for t in te)
baski = d["baski"]
min_pay = min(min(p["duz"]["pay_ileri"], p["duz"]["pay_geri"], p["duz"]["pay_yan"]) for p in R if not p["yuk"])

H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Taban Modülü V3</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:18px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
table.sayi td:not(:first-child){text-align:right;white-space:nowrap}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:21px}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:5px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.uy{color:var(--uy);font-weight:600}.wide{grid-column:1/-1}
.not{color:var(--mut);font-size:13px}a{color:var(--acc2)}
.bos{border:2px dashed var(--line);border-radius:10px;padding:18px;color:var(--mut);background:var(--card)}
.uyari{border-left:4px solid var(--uy);background:var(--card);padding:10px 14px;border-radius:6px}
.karar{border-left:4px solid var(--ok);background:var(--card);padding:10px 14px;border-radius:6px}
</style></head><body><main>""")
H.append("<h1>Taban modülü: şase plakaları, tahrik, akü, güç ve elektronik katı</h1>")
H.append("<div class='sub'>1. aşama (tasarım) · FreeCAD 1.1 · <code>taban_montaj.py</code> · %d parça (%d lazer kesim, %d baskı) + %d kablo yolu şeması · "
         "ölçüler <code>arayuz.TABAN</code>'dan, V3 yerleşimi (robot_cad satır 715–757) · yazıcı %s · 2. aşama: modüller arası tarama ve ana montaj aşağıda</div>"
         % (d["parca_sayisi"], d["lazer_sayisi"], d["baski_sayisi"], d["referans_sayisi"], esc(Y["model"])))
mot5 = MOT["rampa5"]
kpi = [
    ("%d / %d / %d" % (d["parca_sayisi"], d["lazer_sayisi"], d["baski_sayisi"]),
     "parça / lazer / baskı · hepsi geçerli, tek katı" if not d["gecersiz"] and not d["coklu_kati"] else "GEÇERSİZ PARÇA VAR"),
    ("%d" % len(d["ic_cakisma"]), "taban içi çakışma (%d çift sınandı, > 0,5 mm³)" % d["cift_sayisi"]),
    ("%d / %d" % (len(d["iskelet"]["cakisma"]), len(d["kabuk"]["cakisma"])),
     "taban ↔ iskelet / taban ↔ kabuk çakışma (ev pozu; %d + %d çift, %d temas)" % (d["iskelet"]["cift"], d["kabuk"]["cift"],
                                                                                    d["iskelet"]["temas"] + d["kabuk"]["temas"])),
    ("%d / %d" % (bag_ok, len(bag)), "bağlantı kontrolü: dayanma, eksen hizası, cıvata ucu payı / kavrama"),
    ("%s mm" % sayi(te_min, 1), "teker ↔ etek en küçük boşluk (hedef %s mm), dört teker" % sayi(d["teker_etek_hedef_mm"], 0)),
    ("%s kg" % sayi(EV["kutle_g"] / 1000, 2), "tam robot (taban %s kg, kablo payı dahil) · AM y %s mm, z %s mm"
     % (sayi(d["kutle_payli_g"] / 1000, 2), sayi(EV["am"][1], 0), sayi(EV["am"][2], 0))),
    ("%s / %s / %s" % (sayi(EV["duz"]["ileri"], 1), sayi(EV["duz"]["geri"], 1), sayi(EV["duz"]["yan"], 1)),
     "devrilme eşiği ileri / geri / yana m/s² (ev pozu) · tüm kol pozlarında en küçük pay %s×" % sayi(min_pay, 1)),
    ("%s kg·cm" % sayi(mot5["T_kgcm"], 2), "motor başına, 5° rampa + 0,5 m/s² · sürekli hedefe (6,3) oran %%%d (V3: 4,9 kg·cm, %%77)" % round(mot5["oran"] * 100)),
    ("%s sa" % sayi(AKU["senaryo"]["orta"]["saat"], 1), "akü süresi, orta kullanım %s W (tahmini; düşük %s sa, yüksek %s sa)"
     % (sayi(AKU["senaryo"]["orta"]["W"], 0), sayi(AKU["senaryo"]["dusuk"]["saat"], 0), sayi(AKU["senaryo"]["yuksek"]["saat"], 1))),
    ("%d / %d" % (sum(1 for b in baski if b["sigar"]), len(baski)), "X2D'ye sığan baskı · desteksiz %d / %d · toplam %s g filament"
     % (sum(1 for b in baski if b["desteksiz"]), len(baski), sayi(sum(b["filament_g"] for b in baski), 0))),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")
H.append("<p class='uyari'>%s</p>" % md(
    "**Motor torku sınırda:** robot V3'ten ağır çıktı (%s kg; V3 18,6 kg: kabuk 4,9 kg PETG, iskelet 5,8 kg). 5° rampada 0,5 m/s² ile "
    "motor başına %s kg·cm; JGB37'nin sürekli hedefine (6,3 kg·cm) oranı %%%d. Rampada yazılım ivmeyi 0,25 m/s²'ye düşürürse %s kg·cm (%%%d), "
    "sabit hızda %s kg·cm (%%%d). Düz zeminde %s kg·cm (%%%d). Devrilme payları rahat (en az %s×)." % (
        sayi(EV["kutle_g"] / 1000, 1), sayi(mot5["T_kgcm"], 2), round(mot5["oran"] * 100), sayi(MOT["rampa5_yavas"]["T_kgcm"], 2),
        round(MOT["rampa5_yavas"]["oran"] * 100), sayi(MOT["rampa5_durus"]["T_kgcm"], 2), round(MOT["rampa5_durus"]["oran"] * 100),
        sayi(MOT["duz"]["T_kgcm"], 2), round(MOT["duz"]["oran"] * 100), sayi(min_pay, 1))))

# ---------------------------------------------------------------- gorseller
H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (
        ("taban-izometrik.png", "İzometrik: taban + iskelet şasesi + kabuk eteği (yarı saydam)", ""),
        ("taban-izometrik-eteksiz.png", "Etek gizli: ön elektronik katı, arka güç paneli, acil stop ve ana anahtar (etek plakasının altında)", ""),
        ("taban-ust.png", "Üstten (kabuk ve katlar gizli; önü aşağıda): akü + kayışlar, takoz, BTS7960 ×2, XL4016 ×3, kat kartları", ""),
        ("taban-yan.png", "Yandan (+X), etek yarı saydam: aks 62,5, plaka 91,5, ray 94,5–134,5, kat 174,5, etek üstü 262", ""),
        ("taban-on.png", "Önden: sonarlar etek deliklerinde, teker–etek 12 mm", ""),
        ("taban-alt.png", "Alttan: plaka cıvataları (14× M6), motor braketleri (8× M4), kayış dönüşü, kablo delikleri", ""),
        ("taban-elektronik-kati.png", "Elektronik katı (ön): Pi 5 + Active Cooler, ESP32 taşıyıcı, PCA9685, BNO055, MAX98357A", ""),
        ("taban-guc-paneli.png", "Güç paneli (arka): sigorta kutusu, röle, ana sigorta; üstte acil stop ve ana anahtar gövdesi", ""),
        ("taban-aku-yakin.png", "Akü yakın plan (katlar gizli): iki cırt kayış plaka yarıklarından döner, ön takoz", ""),
        ("taban-teker-yakin.png", "Teker grubu: teker, kaplin, L braket, JGB37", ""),
        ("taban-motor-braket-yakin.png", "Teker gizli: braket flanşı plakanın altında, 2× M4 uzun rayın alt kanalına; motor 4× M3", ""),
        ("taban-sonar-yakin.png", "Sonar tutucular ön ara rayın ön kanalında; transdüserler etek deliklerinden 5,5 mm taşar", ""),
        ("taban-patlatilmis.png", "Patlatılmış", "wide")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div><h3>Tam robot önizleme (tüm modüller, ev pozu)</h3><div class='grid3'>")
for ad, cap in (("robot-tam-izometrik.png", "Önden izometrik"), ("robot-tam-yan.png", "Yandan"), ("robot-tam-arka.png", "Arkadan")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (img64(ad), esc(cap), esc(cap)))
H.append("</div>")

# ---------------------------------------------------------------- yapi
H.append("<h2>Yapı ve yerleşim</h2>")
H.append("<p>Koordinat global (taban yereli = global): +X sağ, +Y yukarı, +Z ileri, mm. Üç kat var:</p><ul>")
H.append("<li><b>Alt plaka</b> (3 mm Al 5754, y 91,5–94,5): şase raylarının altına 14× M6 + çekiç somun (uzun raylar z ±90 / ±235, ara raylar x ±50). "
         "Altında 4 motor braketi, üstünde (raylar arasında) akü, 2× BTS7960, 3× XL4016.</li>")
H.append("<li><b>Elektronik katı (ön)</b> (5 mm huş kontrplak, z 24,25–250, y 174,5–179,5): Pi 5, ESP32 taşıyıcı, PCA9685, BNO055, MAX98357A. "
         "4× M5×40 burç (z 40 / 230).</li>")
H.append("<li><b>Güç paneli (arka)</b> (5 mm kontrplak, z −250–23,75, direk cebi önden açık): sigorta kutusu, röle, ana sigorta yuvası. "
         "Akünün üstünde; akü değişiminde elektroniğe dokunmadan sökülür. 4× M5×40 burç (z −40 / −230).</li></ul>")
rows = []
for ad, yer, dayanak in (
        ("Tekerler (4)", "merkez x ±178, z ±185, aks y 62,5", "rc:96–97, rc:729 (V3)"),
        ("JGB37 + L braket (4)", "redüktör ön yüzü x ±133; flanş plakanın altında (y 90–91,5)", "rc:721–727"),
        ("Akü LiFePO4 (yatık)", "x ±90,5, y 94,5–171,5, z −205…−38; kutuplar +Z (z −29'a kadar)", "rc:733, rc:46"),
        ("BTS7960 ×2", "x ±67,5, z 165; 8 mm naylon burç üstünde (üst 143,5)", "rc:734 (+8 mm)"),
        ("XL4016 ×3", "(−49,2; 75) Pi · (49,2; 75) çevre 5 V · (0; 170) servo 6 V", "rc:736 (+8 mm)"),
        ("Raspberry Pi 5", "ön kat (−90,5; 80), SD yuvası x −135,5", "V3 (−59,6; −120) → taşındı"),
        ("ESP32 + taşıyıcı", "ön kat (80; 75)", "V3 (51,6; −135) → taşındı"),
        ("PCA9685", "ön kat (83; 125)", "V3 (51,6; −65) → taşındı"),
        ("BNO055 · MAX98357A", "(0; 60) · (−51,6; 40)", "rc:742–743 (aynı)"),
        ("Sigorta kutusu · röle · ana sigorta", "güç paneli (0; −203) · (−112; −130) · (112; −130)", "yeni (tahmini zarflar)"),
        ("Sonar HC-SR04 ×3", "x 0, ±79,4; y 110; PCB ön yüzü z 256", "rc:752 + kabuk delikleri"),
        ("Acil stop · ana anahtar", "etek üst plakası (79,4; −200) · aynası (−79,4; −200)", "rc:757 · yeni öneri")):
    rows.append((esc(ad), esc(yer), esc(dayanak)))
H.append("<div class='tw'>" + tablo(["Parça", "Konum (mm)", "Dayanak"], rows) + "</div>")

# ---------------------------------------------------------------- parca listesi
H.append("<h2>Parça listesi</h2><div class='tw'>")
rows = [(esc(t), esc(k), "%d" % a, sayi(m, 1)) for (t, k, a, m) in d["bom"]]
rows.append(("Pay", "Kablo payı (tahmini, geometri yok)", "1", sayi(d["kablo_payi"]["kutle_g"], 1)))
H.append(tablo(["Tür", "Kalem", "Adet", "Toplam kütle (g)"], rows, "sayi") + "</div>")
H.append("<p class='not'>CSV: <code>taban-bom.csv</code>. Kütleler: satın alınanlar satıcı / V3 değeri, tahmini zarflar tahmini; plaka ve bağlantı "
         "elemanları hacim × yoğunluk (Al 2,66, kontrplak 0,68, çelik 7,85 g/cm³); baskı %%80 etkin doluluk. Grup kütleleri: %s.</p>"
         % esc(", ".join("%s %s g" % (k, sayi(v, 0)) for k, v in d["kutle_grup"].items())))

# ---------------------------------------------------------------- baglantilar
BAGLANTI = [
    ("Alt plaka ↔ şase sigma rayları", "plaka rayların alt yüzüne dayanır; uzun ray alt kanalı x ±115 (z ±90, ±235), ara ray alt kanalları x ±50",
     "14× M6×14 DIN 912 + DIN 125 pul (alttan) + M6 çekiç somun; uç kanal tabanına 2,4 mm"),
    ("Motor braketi ↔ plaka ↔ uzun ray", "L braket flanşı plakanın altında; delikler uzun rayın alt kanal hizasında (x ±115, z ±185 ±16)",
     "8× M4×16 DIN 912 + pul + M4 çekiç somun (tahmini ölçü); braket motor takılmadan önce bağlanır"),
    ("JGB37 ↔ L braket", "redüktör ön yüzü braketin dikey plakasına; Ø31 dairedeki 6 delikten 4'ü", "4× M3×6 DIN 912 (4,5 mm kavrama)"),
    ("Kaplin ↔ mil ↔ teker", "Ø6 D mil kaplina 11,5 mm; altıgen kaplin teker yuvasına 17,5 mm", "kaplin set vidaları + M4×16 + pul eksenel vida"),
    ("Burç ↔ uzun ray üst kanalı", "M5×40 burç ray üstüne dayalı (x ±115, z ±40, ±230)", "M5 çekiç somun + M5×16 DIN 913 saplama (burca 6,7 mm)"),
    ("Kat / güç paneli ↔ burç", "kontrplak burç üstüne dayalı", "8× M5×12 DIN 912 + pul (burca 6 mm)"),
    ("BTS7960, XL4016 ↔ alt plaka", "kart 8 mm naylon burç üstünde (Al plakaya kısa devre yok)", "M3×6 üstten + M3×6 alttan (vidalar arası 0,6 mm)"),
    ("Pi 5, PCA9685, BNO055 ↔ ön kat", "datasheet delikleri: Pi 58 × 49 Ø2,7; PCA 55,9 × 19,05; BNO 20 × 12", "M2,5×8 pirinç burç + M2,5×5 üst + M2,5×8 alt"),
    ("ESP32 ↔ taşıyıcı ↔ ön kat", "ESP32 pinleri 2× 15'li dişi header'a 6 mm; taşıyıcı 8 mm naylon burçta", "M3×6 üst + M3×8 alt"),
    ("MAX98357A ↔ ön kat", "montaj deliği yok", "1 mm çift taraflı köpük bant"),
    ("Akü ↔ alt plaka", "akü raylar arasında (yanlarda 4,5 mm), arka ara raya 5 mm, önde takoz", "2× 25 mm cırt kayış (plaka yarıklarından döner) + baskı ön takoz (2× M3×8 + ısıl gömme somun)"),
    ("Sigorta kutusu, röle ↔ güç paneli", "kulaklardan; somunlar akünün dışında (z −213, x −112)", "3× M4×16 + pul + M4 DIN 985"),
    ("Sonar ↔ tutucu ↔ ön ara ray", "PCB üst/alt kenarı tutucu raylarında; tutucu ön ara rayın ön yüzüne (z 250)", "4× M6×14 ISO 7380 + M6 çekiç somun (etek duvarına 3,2 mm)"),
    ("Acil stop ↔ etek üst plakası", "Ø22,4 delik, bilezik plakanın üstünde", "butonun kendi somunu"),
]
H.append("<h2>Hangi parça neye, nasıl bağlanıyor</h2><div class='tw'>")
H.append(tablo(["Bağlantı", "Nasıl oturuyor", "Bağlantı elemanı"], [(esc(a), esc(b), esc(c)) for a, b, c in BAGLANTI]) + "</div>")
H.append("<h3>Bağlantı kontrolleri (<code>taban_montaj.py</code>)</h3>")
tip_ad = {"kanal": "Kanal (çekiç somun)", "saplama": "Burç saplaması", "burc": "Kat → burç", "dis": "Dişli delik (motor, kaplin)",
          "insert": "Isıl gömme somun", "burc_kart": "Kart burcu", "somun": "Somunlu (panel)", "mil": "Mil ↔ kaplin", "ray": "Sonar PCB ↔ ray",
          "gecme": "Header geçme"}
rows = []
for tp in tip_ad:
    bs = [b for b in bag if b["tip"] == tp]
    if not bs:
        continue
    ok = sum(1 for b in bs if b["tamam"])
    ornek = bs[0]["olcu"]
    ek = ""
    if tp in ("kanal", "saplama"):
        ek = "uç–kanal tabanı payı en az %s mm" % sayi(min(b["uc_taban_pay"] for b in bs), 1)
    elif tp == "ray":
        ek = "PCB–ray en büyük %s mm" % sayi(max(b["kart_tutucu_mm"] for b in bs), 2)
    elif "kavrama" in ornek:
        ek = "kavrama %s mm" % sayi(min(b["olcu"]["kavrama"] for b in bs), 1)
    rows.append((esc(tip_ad[tp]), "%d / %d" % (ok, len(bs)), esc(ek)))
H.append("<div class='tw'>" + tablo(["Tür", "Tamam", "Ölçüt örneği"], rows) + "</div>")
H.append("<p class='not'>Ölçütler: baş, pul, somun, burç ve kart yüzeye dayalı (≤ 0,01 mm); bağlantı elemanı ve delik/somun aynı eksende (≤ 10⁻⁴ mm); "
         "çekiç somun dudak altında, cıvata somunu tam geçer, uç kanal tabanına ≥ 0,5 mm; dişli delik ve burçta kavrama ≥ d; bir burçtaki iki vida "
         "arasında ≥ 0,5 mm.</p>")

# ---------------------------------------------------------------- uretim: lazer + baski
H.append("<h2>Üretim: lazer kesim ve baskı</h2><h3>Lazer kesim (DXF, ölçek 1:1, mm)</h3><div class='tw'>")
rows = [(esc(l["ad"]), "<code>%s</code>" % esc(l["dosya"]), esc(l["malzeme"]), "%s × %s" % (sayi(l["olcu"][0], 0), sayi(l["olcu"][1], 1)),
         "%d" % l["ic_kontur"], sayi(l["kesim_m"], 2), sayi(l["kutle_g"], 0)) for l in d["lazer"]]
H.append(tablo(["Parça", "Dosya", "Malzeme", "Ölçü (mm)", "İç kontur", "Kesim boyu (m)", "Kütle (g)"], rows) + "</div>")
H.append("<p class='not'>DXF: alt yüzün kenarları (LINE, CIRCLE, ARC), DXF X = robot x, DXF Y = −robot z (üstten bakış, robotun önü çizimin altında). "
         "Alt plakada M6 Ø6,6, M4 Ø4,5, M3 Ø3,4 delikler, Ø16 kablo delikleri ve 3,5 × 30 kayış yarıkları var; kılavuz / havşa yok. "
         "Katlarda M5 Ø5,5, M2,5 Ø2,9, M3 Ø3,4, M4 Ø4,5 delikler ve kablo kesikleri.</p>")
H.append("<h3>Baskı parçaları (%s, PETG, kullanılabilir %s mm)</h3><div class='tw'>" % (esc(Y["model"]), " × ".join(sayi(v, 0) for v in Y["kullanilabilir"])))
rows = [(esc(b["ad"]), " × ".join(sayi(v, 1) for v in b["olcu"]), durum(b["sigar"]), esc(b["yon"]), "%s %%" % sayi(b["cikinti_orani"] * 100, 1),
         "yok" if b["desteksiz"] else "<span class='uy'>gerekir</span>", sayi(b["filament_g"], 1), sayi(b["sure_saat"], 2)) for b in baski]
H.append(tablo(["Parça", "Ölçü (tabla, mm)", "Sığar", "Yön", "45° üstü çıkıntı", "Destek", "Filament (g)", "Süre (sa, tahmini)"], rows) + "</div>")
H.append("<p class='not'>Yöntem kabuk/kafa ile aynı: tabla düzleminde en küçük döndürülmüş kutu, 45° çıkıntı oranı, 1 mm katmanlarla desteksiz basılabilirlik "
         "(2 mm'den dar şerit ve 15 mm'den kısa açıklık serbest). Sağ ve sol sonar tutucu birbirinin aynası.</p>")

# ---------------------------------------------------------------- hesaplar
H.append("<h2>Mühendislik hesapları</h2><h3>Kütle ve ağırlık merkezi</h3>")
rows = [("Tabansız robot (ana montaj, 601 parça)", sayi(d["robot"]["tabansiz_kutle_g"] / 1000, 2), "(%s)" % "; ".join(sayi(v, 1) for v in d["robot"]["tabansiz_am"])),
        ("Taban parçaları (%d)" % d["parca_sayisi"], sayi(d["kutle_g"] / 1000, 2), "(%s)" % "; ".join(sayi(v, 1) for v in d["agirlik_merkezi"])),
        ("Kablo payı (tahmini)", sayi(d["kablo_payi"]["kutle_g"] / 1000, 2), "(%s)" % "; ".join(sayi(v, 0) for v in d["kablo_payi"]["merkez"])),
        ("<b>Tam robot (ev pozu)</b>", "<b>%s</b>" % sayi(EV["kutle_g"] / 1000, 2), "<b>(%s)</b>" % "; ".join(sayi(v, 1) for v in EV["am"]))]
H.append("<div class='tw'>" + tablo(["", "Kütle (kg)", "AM x; y; z (mm)"], rows, "sayi") + "</div>")
H.append("<p class='not'>En ağırlar: %s. Kol pozlarında omuz göbeği, üst kol, dirsek çatalı, ön kol ve el grupları (kol başına %s g) omuz kinematiğiyle "
         "döndürüldü (<code>omuz_parcalar.Pp/Pr</code>, <code>dirsek_parcalar.grup_yer</code>).</p>"
         % (esc(", ".join("%s %s g" % (a, sayi(m, 0)) for a, m in d["en_agir"][:6])),
            sayi(sum(v["kutle_g"] for v in d["robot"]["hareketli_gruplar"].values()), 0)))
H.append("<h3>Devrilme (eşik ivmesi m/s², pay = eşik ÷ 1,5 m/s² acil stop freni)</h3><div class='tw'>")
rows = []
for p in R:
    dz, r5 = p["duz"], p["rampa5"]
    rows.append((esc(POZ_AD.get(p["kod"], p["ad"])), sayi(p["kutle_g"] / 1000, 2), "%s / %s" % (sayi(p["am"][1], 0), sayi(p["am"][2], 0)),
                 "<span class='%s'>%s (%s×)</span>" % (pay_sinif(dz["pay_ileri"]), sayi(dz["ileri"], 2), sayi(dz["pay_ileri"], 1)),
                 "<span class='%s'>%s (%s×)</span>" % (pay_sinif(dz["pay_geri"]), sayi(dz["geri"], 2), sayi(dz["pay_geri"], 1)),
                 "<span class='%s'>%s (%s×)</span>" % (pay_sinif(dz["pay_yan"]), sayi(dz["yan"], 2), sayi(dz["pay_yan"], 1)),
                 "%s / %s / %s" % (sayi(r5["ileri"], 2), sayi(r5["geri"], 2), sayi(r5["yan"], 2)),
                 "%s° / %s° / %s°" % (sayi(dz["statik_egim_ileri"], 0), sayi(dz["statik_egim_geri"], 0), sayi(dz["statik_egim_yan"], 0))))
H.append(tablo(["Poz", "Kütle (kg)", "AM y / z", "İleri (frende)", "Geri", "Yana", "5° rampada ileri / geri / yana", "Statik devrilme eğimi"], rows) + "</div>")
H.append("<p class='not'>Eşik = g · (d · cos θ − h · sin θ) / h; d = ağırlık merkezinden teker temas hattına yatay uzaklık (teker merkez düzlemleri x ±178, "
         "z ±185; V3 hesabıyla aynı), h = AM yüksekliği. Rampada ileri: robot yokuş aşağı bakarken frenleme; geri: yokuş yukarı hızlanma; yana: "
         "rampaya yan dururken. V3 (README): ileri 5,8, geri 5,0, yana 5,2 m/s²; ağırlık merkezi 337 → %s mm yükseldi (kabuk ve gövde ağır), yine de "
         "en kötü pozda pay ≥ %s×. Elde 0,5 kg yük satırı bilgi amaçlı (dirsek raporu kolları yüksüz jest için onayladı).</p>"
         % (sayi(EV["am"][1], 0), sayi(min(min(p["duz"]["pay_ileri"], p["duz"]["pay_geri"], p["duz"]["pay_yan"]) for p in R), 1)))
H.append("<h3>Motor torku (V3 varsayımları)</h3><div class='tw'>")
rows = []
for k, ad in (("duz", "Düz zemin, 0,5 m/s²"), ("rampa5", "5° rampa, 0,5 m/s²"), ("rampa5_yavas", "5° rampa, 0,25 m/s² (yazılım sınırı önerisi)"),
              ("rampa5_durus", "5° rampa, sabit hız"), ("rampa5_yuk2", "5° rampa, 0,5 m/s², +2 kg yük (bilgi)")):
    m = MOT[k]
    sn = "ok" if m["oran"] <= 0.8 else ("uy" if m["oran"] <= 1.0 else "no")
    rows.append((esc(ad), sayi(m["F_N"], 1), sayi(m["T_kgcm"], 2), "<span class='%s'>%%%d</span>" % (sn, round(m["oran"] * 100))))
rows.append(("V3 (README, 18,6 kg, 5° rampa)", "–", "4,90", "%77"))
H.append(tablo(["Durum", "Çekiş kuvveti (N)", "Motor başına (kg·cm)", "Sürekli hedefin (6,3 kg·cm) yüzdesi"], rows) + "</div>")
H.append("<p class='not'>F = m · (a + g · sin θ + 0,03 · g · cos θ), T = F · 62,5 mm / 4 motor; JGB37 durma torku 21 kg·cm, sürekli çalışmada %%30'u "
         "(6,3 kg·cm) hedef (01-donanim-maliyet, V3 demosu). Hız 60 dev/dk × Ø125 = %s m/s. Aks yükü (düz, sabit hız): ön çift %s N, arka çift %s N "
         "(akü arkada); 5° rampa + 0,5 m/s² için gereken sürtünme katsayısı %s (kauçuk teker için düşük, tahmini).</p>"
         % (sayi(MOT["hiz_m_s"], 2), sayi(d["aks"]["on_N"], 0), sayi(d["aks"]["arka_N"], 0), sayi(d["aks"]["mu_gereken_rampa5"], 2)))
H.append("<h3>Akü süresi (tahmini)</h3><div class='tw'>")
rows = [(esc(t[0]), esc(t[1]), sayi(t[2], 1), sayi(t[3], 1), sayi(t[4], 1), esc(t[5])) for t in AKU["kalemler"]]
rows.append(("<b>Aküden çekilen (dönüştürücü kaybı + röle bobini dahil)</b>", "12,8 V", "<b>%s</b>" % sayi(AKU["senaryo"]["dusuk"]["W"], 1),
             "<b>%s</b>" % sayi(AKU["senaryo"]["orta"]["W"], 1), "<b>%s</b>" % sayi(AKU["senaryo"]["yuksek"]["W"], 1), ""))
rows.append(("<b>Süre, 24 Ah (307 Wh × %%%d)</b>" % round(AKU["kullanilabilir"] * 100), "", "<b>%s sa</b>" % sayi(AKU["senaryo"]["dusuk"]["saat"], 1),
             "<b>%s sa</b>" % sayi(AKU["senaryo"]["orta"]["saat"], 1), "<b>%s sa</b>" % sayi(AKU["senaryo"]["yuksek"]["saat"], 1), "tahmini"))
rows.append(("Süre, 20 Ah olursa (256 Wh)", "", "%s sa" % sayi(AKU["senaryo"]["dusuk"]["saat_20ah"], 1), "%s sa" % sayi(AKU["senaryo"]["orta"]["saat_20ah"], 1),
             "%s sa" % sayi(AKU["senaryo"]["yuksek"]["saat_20ah"], 1), ""))
H.append(tablo(["Kalem", "Hat", "Düşük (W)", "Orta (W)", "Yüksek (W)", "Dayanak"], rows) + "</div>")
H.append("<p class='not'>Tüm tüketim kalemleri tahmini (yalnız Nextion akımı datasheet'ten). XL4016 verimi 0,88, BTS7960 0,95, kullanılabilir kapasite %%80 "
         "(01-donanim-maliyet ile aynı) varsayıldı. Orta = ekranlar açık, kollar jest yapıyor, zamanın ~%%30'unda sürüş. Akü 24 Ah Limacell "
         "(307 Wh, 05-fiyat-arastirmasi); ölçüsü ve kütlesi henüz yok, model 20 Ah Landport yuvasıyla çizildi.</p>")

# ---------------------------------------------------------------- kablo yolu
H.append("<h2>Güç dağıtımı ve kablo yolu</h2>")
H.append("<div class='grid'>")
for ad, cap in (("taban-kablo-yolu.png", "Taban içi kablo yolu şeması (katlar yarı saydam): kırmızı 12 V ana hat, turuncu motor, sarı servo 6 V, mavi 5 V, yeşil acil stop, mor sinyal"),
                ("taban-kablo-yolu-direk.png", "Gövde direği boyunca: servo, 5 V ve Pi kabloları etek üst açıklığından çıkar, direğin arka/ön yüzü boyunca traverse")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (img64(ad), esc(cap), esc(cap)))
H.append("</div>")
H.append("<h3>Sigorta planı (sigorta kutusu ile gelen 5, 10, 2×15, 2×20 A)</h3><div class='tw'>")
SIG = [("Ana sigorta 30 A", "akü + → XT60 → kablolu yuva (güç panelinde)", "ana anahtar ASW-A01 → sigorta kutusu girişi"),
       ("F1 20 A", "röle (40 A) kontağı → WAGO", "BTS7960 sol + sağ (her biri iki motoru paralel sürer) ve XL4016 servo 6 V"),
       ("F2 15 A", "yedek", "ileride kol başına ayrı servo dönüştürücü (01'deki öneri)"),
       ("F3 10 A", "XL4016 Pi (5,1 V)", "Raspberry Pi 5 (USB-C)"),
       ("F4 5 A", "XL4016 çevre (5 V)", "Nextion, 7\" LCD, ESP32, PCA mantık, BNO055, sonarlar, amfi"),
       ("F5 5 A", "acil stop (NC) → röle bobini", "basınca röle bırakır: motor + servo gücü düşer, Pi ve ekranlar açık kalır (03-referans)"),
       ("F6", "boş", "")]
H.append(tablo(["Sigorta", "Hat", "Besledikleri"], [(esc(a), esc(b), esc(c)) for a, b, c in SIG]) + "</div>")
H.append("<h3>Kablo yolları (şema, <code>Referans</code> grubu; taramaya ve kütleye girmez)</h3><ol>")
for k in d["kablo_yolu"]:
    H.append("<li>%s</li>" % esc(k["devre"]))
H.append("</ol><ul>")
for s in ("**Akü → güç paneli:** kutuplar önde (z −29); kablolar akü ile orta ara ray arasındaki 18 mm boşluktan yukarı, güç panelinin akü kablo yarıklarından (x ±40…80, z −37…−23) çıkar.",
          "**Panel → alt kat:** aynı yarıklardan aşağı, orta ara rayın üstünden (y 140–170) ön bölmeye: BTS7960 ve XL4016'lar.",
          "**Motorlar:** ön motor kabloları Ø16 delikten (x ±80, z 200), arka motor kabloları plakanın altından öne gelip Ø16 delikten (x ±80, z 36) çıkar.",
          "**Alt kat → ön kat:** ön katın kablo kesiği (x ±60, z 150–175); Pi beslemesi ve ESP32 sinyalleri buradan.",
          "**Gövdeye çıkış:** etek üst plakasının 200 × 140 açıklığından direğin yanından. Servo demeti direğin **arka yüzü** boyunca (gövde braketleri ±X yüzünde, arka yüz boş), "
          "traverse çıkınca omuz servolarına ve R62 boyun açıklığından kafaya. 5 V çevre ve Pi → kafa (HDMI, kamera, USB) direğin **ön yüzünde**, Nextion konnektörüne y ~800'de ayrılır. "
          "Demet gövde arka servis kapağından (y 500–690) erişilebilir.",
          "**Sinyal:** sonarlar ön ara rayın üstünden ESP32'ye; enkoder ve BTS PWM/EN ESP32'ye; Pi ↔ ESP32 USB."):
    H.append("<li>%s</li>" % md(s))
H.append("</ul>")

# ---------------------------------------------------------------- servis
H.append("<h2>Servis erişimi</h2><ul>")
for s in ("**Akü değişimi:** (1) acil stop + ana anahtar kapalı, akü XT60'ı ayrılır. (2) Etek arka sağ ve sol (2 baskı parçası, M3 bindirme + etek braketi vidaları) "
          "sökülür; acil stop ve ana anahtar etekle gelir (kabloları fişli olmalı). (3) Güç paneli 4× M5 sökülüp ~50 mm geri çekilir (direk cebi önden açık) ve "
          "kaldırılır; sigorta kutusu ve röle panelde kalır (servis halkası). (4) İki cırt kayış açılır; akü 40 mm kaldırılıp arka ara rayın üstünden geriye alınır "
          "(üstte etek orta plakası y 259'da, akü üstü 211,5: 47 mm boşluk). Elektronik katına dokunulmaz.",
          "**Şarj:** akü yerinde, ayrı XT60 şarj girişinden (konum önerisi: etek üst plakası arka; kabukta delik gerekir, açık iş).",
          "**SD kart:** Pi 5 ön katın sol kenarında, SD yuvası −X'e bakar (x −135,5, z 80) ve etek orta sol bandının hizasında. Etek orta sol (1 parça) sökülünce yandan "
          "doğrudan erişilir. Günlük güncelleme SSH/ağ üzerinden; SD çıkarmak yalnız imaj değişiminde.",
          "**Sigortalar:** güç panelinin üstünde; etek arka bandı sökülünce erişilir.",
          "**Elektronik katı:** etek ön + orta bantları sökülünce yandan; kat 4× M5 ile söküp kaldırılabilir (kablolar kesikten).",
          "**Motor / teker:** teker M4 eksenel vidası dışarıdan (etek sökülmeden alttan erişim zor: etek yerden 35 mm). Motor braketi plakaya önce takılır (M4 anahtarı redüktörden geçmez)."):
    H.append("<li>%s</li>" % md(s))
H.append("</ul>")

# ---------------------------------------------------------------- 2. asama
H.append("<h2>Modüller arası çakışma ve ana montaj (2. aşama)</h2>")


def _js(*yol):
    f = os.path.join(UST, *yol)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


CRP, MA, ED, GK = _js("carpisma-sonuc.json"), _js("montaj", "montaj-analiz.json"), _js("montaj", "eklem-dogrulama.json"), _js("montaj", "gui-kontrol.json")
REG = {m: _js(m, "regresyon", "fark.json") for m in ("omuz", "iskelet")}
REGM = _js("taban", "regresyon", "moduller.json")
TT = (CRP or {}).get("taban_tarama")
MODTR = {"iskelet": "iskelet", "omuz_sag": "sağ omuz", "omuz_sol": "sol omuz", "kabuk": "kabuk", "dirsek_sag": "sağ dirsek", "dirsek_sol": "sol dirsek",
         "kafa": "kafa"}
if not TT:
    H.append("<div class='bos'>carpisma.py taban bölümü henüz koşmadı.</div>")
else:
    H.append("<p><b>Kapsam (<code>carpisma.py</code> bölüm 4c, %s):</b> taban 306 parça (kablo yolu şemaları hariç) KONTROL listesinde; tüm bölümler "
             "(omuz, kol zinciri, kol ↔ kol, kafa, taban) bölümlü tek koşuda yeniden koştu. %s</p>" % (
                 esc((CRP.get("bolumler") or {}).get("taban", {}).get("baslangic", "")), esc(CRP.get("birlestirme_notu", ""))))
    st = TT["statik"]
    H.append("<h3>Ev pozu: taban ↔ diğer modüller</h3><div class='tw'>" + tablo(
        ["Modül", "Kutu kesişen çift", "Çakışma", "Temas", "En küçük boşluk", "En yakın çift"],
        [[esc(MODTR.get(m, m)), "%d" % v["kutu_kesisen"], "<b>%d</b>" % len(v["cakisma"]), "%d" % v["temas"],
          (sayi(v["en_kucuk_bosluk_mm"], 1) + " mm") if v["en_kucuk_bosluk_mm"] is not None else "–", esc(" ↔ ".join(v["en_yakin"] or []))]
         for m, v in st.items()], "sayi") + "</div>")
    H.append("<p class='not'>Temaslar beklenen: plaka ↔ raylar, çekiç somunlar ↔ kanal dudakları, burçlar ↔ ray üstü (iskelet), acil stop bileziği ↔ "
             "etek üst plakası (kabuk). Kafa, omuzlar ve dirsekler ev pozunda tabandan çok uzak.</p>")
    sat = []
    for t, k in TT["kol"].items():
        for kat, b in sorted(k["en_kucuk_aralikta"].items(), key=lambda x: x[1]["bosluk_mm"]):
            sat.append(["%s kol" % ("Sağ" if t == "sag" else "Sol"), esc(kat), sayi(b["bosluk_mm"], 1) + " mm", esc("%s ↔ %s" % (b["parca"], b["hedef"])),
                        esc(" / ".join("%s°" % sayi(x, 0) for x in b["kol_poz"]))])
    k0 = TT["kol"]["sag"]
    n_cak = sum(k["cakisan_alt_poz_aralikta"] for k in TT["kol"].values())
    n_cd = sum(k["cakisan_alt_poz_aralik_disi"] for k in TT["kol"].values())
    H.append("<h3>Kollar × taban (tüm pozlar)</h3>")
    H.append("<p>Her kol: kol zinciri ızgarası (öne −45…135°, yana 0…120° 15° adımla, dirsek 0/30/60/90/105°, bilek −90/0/90° = %d poz) + aralık dışı "
             "halka (%d poz) + %d jest pozu; her alt poz (omuz göbeği + üst kol, dirsek çatalı, ön kol, el) taban parçalarına, ana anahtar düğmesi "
             "gösterimine (etek üstüne ~22 mm taşar) ve kabuğun etek parçalarına karşı. Sıkı sınır kutusu (tessellation dış kabuğu) ile alt sınır, kategori "
             "başına en küçük boşluk dal-sınırla tam ölçüldü; en küçüklerin çevresi 5° adımla (bilek 15°) yeniden tarandı. Sağ %d, sol %d tam ölçüm.</p>" % (
                 k0["poz"]["kaba"], k0["poz"]["aralik_disi"], k0["poz"]["jest"], TT["kol"]["sag"]["tam_olcum"], TT["kol"]["sol"]["tam_olcum"]))
    H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in [
        ("%d" % n_cak, "kol × taban çakışma, eklem aralığında (aralık dışı %d)" % n_cd),
        ("%s mm" % sayi(min(b["bosluk_mm"] for k in TT["kol"].values() for b in k["en_kucuk_aralikta"].values()), 0),
         "kol ↔ taban/etek en küçük boşluk (eklem aralığında)"),
        ("y %s mm" % sayi(min(k["kol_en_alt"]["y_mm"] for k in TT["kol"].values()), 0),
         "kolun en alt noktası (kol aşağıda, el ucu); tabanın en üstü y %s mm (acil stop mantarı)" % sayi(k0["taban_en_ust_y_mm"], 0)),
        (("%s mm" % sayi(TT["kafa"]["kutu_bosluk_mm"], 0)) if TT.get("kafa") else "–",
         "kafa (tüm pan × tilt) en alt noktası ↔ taban en üstü: ölçüm gerekmedi"),
    ]) + "</div>")
    H.append("<div class='tw'>" + tablo(["Kol", "Hedef", "En küçük boşluk", "Parça çifti", "Kol pozu (öne / yana / dirsek / bilek)"], sat) + "</div>")
    if n_cak == 0:
        H.append("<p class='karar'><b>Sonuç:</b> kollar hiçbir pozda tabana (acil stop mantarı, sonarlar, ana anahtar, etek üstü) yaklaşmıyor: el en "
                 "aşağıdayken bile etek üstünden ~%s mm yukarıda. Taban için yazılım sınırı ya da geometri değişikliği gerekmedi.</p>" % sayi(
                     min(k["en_kucuk_aralikta"].get("etek (kabuk)", {"bosluk_mm": 0})["bosluk_mm"] for k in TT["kol"].values()), 0))
if MA:
    tb = next((m for m in MA["moduller"] if m["ad"] == "taban"), None)
    H.append("<h3>Ana montaj</h3>")
    if tb:
        kp = d["kablo_payi"]
        m_t = MA["kutle_g"] + kp["kutle_g"]
        am_t = [(MA["kutle_g"] * MA["agirlik_merkezi"][i] + kp["kutle_g"] * kp["merkez"][i]) / m_t for i in range(3)]
        fark_am = max(abs(a - b) for a, b in zip(am_t, EV["am"]))
        ok_t = abs(m_t - EV["kutle_g"]) < 0.5 and fark_am < 0.2
        H.append("<p><code>montaj/moduller.py</code>'de <code>taban</code>: gövde grubu uzun raya sabit eklemle, 4 teker grubu (teker + kaplin + "
                 "M4 eksenel vida + pul) gövdeye <b>sınırsız döner eklemle</b> (eksen motor mili, +X; pozitif = ileri yuvarlanma). Taban %d parça, "
                 "%s g. Ana montaj %d parça, %d grup, %d eklem; kütle <b>%s g</b>, AM (%s; %s; %s) mm. Kablo payı (%s g, tahmini; parça listesine "
                 "girmiyor) eklenince %s g ve AM (%s; %s; %s): bu raporun devrilme hesabındaki %s g / (%s; %s; %s) ile fark %s g, AM %s mm "
                 "(<span class='%s'>%s</span>).</p>" % (
                     tb["parca"], sayi(tb["kutle_g"], 1), MA["parca_sayisi"], MA["grup_sayisi"], len(MA["eklemler"]),
                     sayi(MA["kutle_g"], 1), sayi(MA["agirlik_merkezi"][0], 1), sayi(MA["agirlik_merkezi"][1], 1), sayi(MA["agirlik_merkezi"][2], 1),
                     sayi(kp["kutle_g"], 0), sayi(m_t, 1), sayi(am_t[0], 1), sayi(am_t[1], 1), sayi(am_t[2], 1), sayi(EV["kutle_g"], 1),
                     sayi(EV["am"][0], 1), sayi(EV["am"][1], 1), sayi(EV["am"][2], 1), sayi(m_t - EV["kutle_g"], 2), sayi(fark_am, 2),
                     "ok" if ok_t else "no", "tutarlı" if ok_t else "TUTARSIZ"))
    if ED:
        tv = [v for v in ED["vakalar"] if v["ad"].startswith("taban")]
        ty = [y for y in ED["yon"] if y["kol"] == "taban"]
        if tv:
            H.append("<p><b>Eklem doğrulaması:</b> %d teker vakası (tek tek, birlikte, tam turdan büyük: 400°, −720°; kollar + kafa ile birlikte) "
                     "simülasyonla sürüldü; çözücünün teker yerleşimi, teker merkezinden +X etrafında beklenen dönüşten en çok %s mm / %s° farklı. Yön: "
                     "teker +90° → alt nokta geri (−Z), aks yüksekliğine: %s. <code>solve()</code> elle verilen teker açılarını korudu.</p>" % (
                         len(tv), "%.1e" % max(v["max_mm"] for v in tv), "%.1e" % max(v["max_derece"] for v in tv),
                         "dört teker doğru" if ty and all(y["dogru"] for y in ty) else "YANLIŞ"))
    if GK:
        tek = {k: v for k, v in GK["eklemler"].items() if k.startswith("Taban_")}
        H.append("<p><b>GUI açılışı:</b> %d/%d parça görünür; taban eklemleri (%d) görünür ve ağaçta seçilebilir: %s.</p>" % (
            GK["acilis"]["parca_gorunur"], GK["acilis"]["parca"], len(tek),
            "evet" if tek and all(v["gorunur"] for v in tek.values()) and all(GK["secim"].get(k) for k in tek) else "HAYIR"))
    H.append("<div class='grid'>")
    for ad, cap in (("montaj-taban.png", "Ana montajda taban, arkadan: etek, acil stop, tekerler"),
                    ("montaj-taban-ic.png", "Ana montajda taban, etek gizli: akü, güç paneli, elektronik katı, motorlar")):
        p = os.path.join(UST, "montaj", "gorsel", ad)
        if os.path.exists(p):
            H.append("<figure><img src='data:image/png;base64,%s' alt='%s'><figcaption>%s</figcaption></figure>" % (
                base64.b64encode(open(p, "rb").read()).decode(), esc(cap), esc(cap)))
    H.append("</div>")
H.append("<h3>Regresyon</h3><ul>")
for m, r in REG.items():
    if r:
        H.append("<li>%s regresyonu (<code>arayuz.py</code>'ye taban eklendikten sonra): <span class='%s'>%s</span></li>" % (
            m, "ok" if r["hepsi_ayni"] else "no", "birebir aynı (fark 0)" if r["hepsi_ayni"] else "FARK VAR"))
if REGM:
    H.append("<li>Kabuk, dirsek, kafa modül çıktıları (git HEAD arayüzü ile güncel arayüz): %s · <span class='%s'>%s</span></li>" % (
        esc(", ".join("%s %d parça" % (m, v["parca_sonra"]) for m, v in REGM["moduller"].items())), "ok" if REGM["hepsi_ayni"] else "no",
        "parça adları, hacim, sınır kutusu, kütle birebir aynı" if REGM["hepsi_ayni"] else "FARK VAR"))
H.append("</ul>")

# ---------------------------------------------------------------- kararlar
KARAR = [
    "**Kat iki parça:** ön elektronik katı + arka güç paneli. Akü yalnız yukarıdan çıkabiliyor (dört yanında ray); arka panel sökülünce akü elektroniğe dokunmadan değişir.",
    "**Pi 5, ESP32, PCA9685 ön kata taşındı** (V3'te akünün üstündeydi, z −135…−65): kat altı ile akü arasında 3 mm var, kart vidaları/somunları akünün üstüne inerdi; ayrıca akü servisi. Bölge değişikliği, gerekçe bu.",
    "**BTS7960 ve XL4016 8 mm naylon burç üstünde** (V3'te doğrudan plakadaydı: Al plaka PCB'yi kısa devre eder). Bölgeleri 8 mm yükseldi; üstte 31 mm boşluk kalıyor.",
    "**Motor braketi flanşı uzun rayın alt kanalına:** V3'te flanş delikleri (x 109 / 123) rayın dolu dudağına denk geliyordu (kanal 110–120); delikler kanal hizasına (x 115) alındı, M4 çekiç somun (tahmini ölçü). Braket elde yok; delik düzeni braket gelince doğrulanacak, gerekirse flanşa delik açılır.",
    "**Plaka → ray bağlantısı:** V3'te yoktu; 14× M6 alttan. M6×14 + pul ile uç somunu 0,1 mm geçer, kanal tabanına 2,4 mm kalır.",
    "**Burç:** V3'teki 4 burca kat ayrımı için z ±40'ta 4 burç eklendi (etek braketleri z 0 / ±105 arasında). Burç M5 çekiç somun + M5×16 saplama ile oturur.",
    "**Sonar tutucu:** kabuğa dokunmadan ön ara rayın ön kanalına; PCB yandan raylara sürülür, transdüserler etek deliklerinde (radyal 0,5 mm) ve 5,5 mm dışarı taşar.",
    "**Acil stop:** Emas B200E60 ölçüsüyle çizildi (04). Elde olan B200E-E 40 mm mantar: Ø60 zarfın içinde, delik aynı Ø22,4. NC kontağı röle bobinini keser; röle BOM'da yok (açık iş).",
    "**Ana anahtar (öneri):** etek üst plakasının altında, acil stobun aynası. Kabukta delik yok; düğme şeması Referans'ta (statik taramaya girmez, kol × taban taramasında hedef).",
    "**Tahmini zarflar:** sigorta kutusu (105 × 60 × 35), röle (30 × 30 × 45), ana sigorta yuvası (30 × 60 × 20), ana anahtar gövdesi (50 × 50 × 40), ESP32 taşıyıcı pertinaks (70 × 50). Ölçüler uydurulmadı: zarf, kumpasla ölçülünce güncellenecek.",
    "**Tahmini ölçüler:** BTS7960 delik aralığı ±21, M4/M5 çekiç somun gövdesi M6 ile aynı (16 × 10 × 5), teker iç geometrisi (altıgen yuva 17,5 mm, M4 eksenel vida), kaplin M4 dişi 12 mm, JGB37 M3 delik derinliği 6 mm, HC-SR04 pin bloğu.",
    "**Hesap varsayımları:** fren ivmesi 1,5 m/s², temas hattı teker merkez düzlemi (V3 ile aynı; gerçek temas lastik genişliği, yana biraz daha güvenli), kablo payı 400 g (tahmini), akü 2,8 kg (20 Ah Landport; 24 Ah'ın kütlesi bilinmiyor).",
]
H.append("<h2>Kararlar ve varsayımlar</h2><ul>" + "".join("<li>%s</li>" % md(s) for s in KARAR) + "</ul>")
H.append("<h3>Ayrılmış bölge değişiklikleri (<code>arayuz.py</code>, yalnız ekleme)</h3><div class='tw'>")
BOL = [("Pi 5, ESP32, PCA9685", "akü üstü (z −149…−53)", "ön kat (z 47…138); yeni bölge 'Elektronik katı ön yerleşimi'", "akü servisi, kat altı vida ↔ akü"),
       ("BTS7960 ×2, XL4016 ×3", "plaka üstü 43 / 23,5 mm", "+8 mm (naylon burç)", "kısa devre"),
       ("M5×40 burç", "z ±230", "+ z ±40 (4 adet)", "iki parçalı kat"),
       ("Güç paneli, ana anahtar gövdesi, Pi fan payı, sonar tutucular, akü takozu + kayışlar", "–", "yeni bölgeler", "yeni parçalar"),
       ("Akü kutupları", "bölge z −38'e kadar", "z −29'a kadar (V3 ile aynı)", "çizim gereği; takozun üstünde serbest")]
H.append(tablo(["Ne", "V3 / önceki", "Şimdi", "Neden"], [tuple(esc(x) for x in r) for r in BOL]) + "</div>")
H.append("<p class='not'>Eski taban bölgeleri <code>arayuz.BOLGELER</code>'de duruyor (yalnız ekleme kuralı); taban 2. aşamada <code>carpisma.py</code> KONTROL listesine "
         "girince bölgeleri yerine gerçek geometri taranır. Yeni ve eski %d taban bölgesi iskelet ve kabuğa karşı tarandı: %d ihlal.</p>"
         % (d["bolge"]["taban_bolge"], len(d["bolge"]["ihlal"])))

SIRA = ["Çekiç somunlar (M6 plaka, M4 braket, M5 burç, M6 sonar) kanallara düşürülüp 90° çevrilir.",
        "Motor braketleri flanşları plakanın altına, plaka raylara: önce M4 (braket + plaka), sonra 14× M6.",
        "Alt plaka üstü: BTS/XL burçları (alttan M3), akü takozu (M3 + ısıl gömme somun), kayışlar yarıklardan geçirilir.",
        "Motorlar braketlere (4× M3×6), kaplin (set vidaları mil düzlüğüne), teker (M4×16 eksenel).",
        "BTS7960, XL4016 kartları; akü + kayışlar.",
        "Saplama + burçlar; güç paneli (sigorta kutusu, röle, ana sigorta önceden takılı) ve elektronik katı (kartlar önceden takılı) 8× M5.",
        "Sonar tutucular ön ara raya, sonarlar raylara sürülür; kablolama (servis halkaları), etek ve acil stop / ana anahtar."]
H.append("<h2>Montaj sırası (öneri)</h2><ol>" + "".join("<li>%s</li>" % md(s) for s in SIRA) + "</ol>")
ACIK = ["**Akü:** Limacell 24 Ah'ın ölçüsü ve kütlesi satıcıdan (yuva 181 × 77 × 167; kutup yönü ve yeri). Farklıysa kayış ve takoz yeniden.",
        "**Motor braketi:** elde yok; JGB37 kaçık mili için delik düzeni (4 delik, Ø31 daire) ve flanş deliklerinin x 115 hizası. M4 çekiç somun (kanal 10) satın alınmalı.",
        "**Motor torku rampada %%%d:** yazılımda rampada ivme ≤ 0,25 m/s² (→ %%%d) ya da daha yüksek torklu motor; robot kütlesi V3'ten %s kg fazla." % (
            round(mot5["oran"] * 100), round(MOT["rampa5_yavas"]["oran"] * 100), sayi(EV["kutle_g"] / 1000 - 18.6, 1)),
        "**BOM'a eklenecekler:** 12 V 40 A röle + soket, ESP32 taşıyıcı (pertinaks + 2× 15'li dişi header), M2,5 pirinç burç + vida (Pi/PCA/BNO; settekiler M3), M4 ve M5 çekiç somun, M5×16 set vida, 25 mm cırt kayış (2), köpük bant, XT60 şarj girişi.",
        "**Kumpasla ölçülecek:** sigorta kutusu, röle, ana anahtar ASW-A01, ana sigorta yuvası, BTS7960 delik aralığı, eldeki BNO055 muadil kartı, HC-SR04 pin bloğu.",
        "**Kabuk (2. aşama / kabuk sahibi):** etek üst plakasına ana anahtar deliği ve XT60 şarj girişi; acil stop B200E-E ile delik aynı.",
        "**Isı:** Pi 5 + 3× XL4016 + 2× BTS7960 kapalı etekte; etek altı açık (yerden 35 mm), sıcak hava etek üst açıklığından gövdeye çıkar. Sıcaklık ölçülmeli; gerekirse etek arka bandına havalandırma.",
        "**Kamera kablosu:** Pi tabanda, kamera kafada (~900 mm): elimizdeki 200 mm FPC yetmez (kafa raporuyla birlikte karar).",
        "**Alt plaka 1,06 kg:** lazer kesimde hafifletme cepleri (akü ve kart bölgeleri dışında) ~%25 kazandırır; devrilme payı düşük kütleye duyarlı değil (akü belirleyici).",
        "**Robot yazılımı:** tekerler montajda serbest döner eklem; hız/ivme sınırı (rampada ≤ 0,25 m/s²) ve acil stop davranışı yazılımda."]
H.append("<h2>Açık işler</h2><ul>" + "".join("<li>%s</li>" % md(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>taban_lib.py</code>: JGB37, L braket, kaplin, teker, akü, kartlar (Pi 5, PCA9685, BNO055, MAX98357A, ESP32, BTS7960, XL4016, HC-SR04), acil stop, "
         "zarflar, burç, plaka yardımcıları, DXF yazıcı; baskı analizi dirsek_lib'den</li>"
         "<li><code>taban_parcalar.py</code>: parçalar, bağlantılar, baskı/lazer listesi, kablo yolu şeması (import edilebilir)</li>"
         "<li><code>taban_montaj.py</code>: kontroller, iskelet/kabuk taraması, hesaplar → <code>taban-montaj.FCStd</code>, <code>.step</code>, <code>taban-bom.csv</code>, "
         "<code>taban-analiz.json</code>, <code>dxf/*.dxf</code></li>"
         "<li><code>taban_gorsel.py</code> (FreeCAD GUI) → <code>gorsel/</code>; <code>taban_rapor.py</code> → bu sayfa</li>"
         "<li><code>../arayuz.py</code>: <code>TABAN</code>, <code>MODULLER['taban']</code> ve yeni taban bölgeleri</li></ul>")
H.append("<p class='not'>Üretildi: taban_rapor.py · analiz süresi %s s · STEP %d katı · gruplar %s</p>"
         % (sayi(d["sure_s"], 1), d["step_kati"], esc(", ".join(k for k in d["gruplar"]))))
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html", round(os.path.getsize(os.path.join(HERE, "rapor.html")) / 1024), "KB")
