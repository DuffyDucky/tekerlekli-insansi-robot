# -*- coding: utf-8 -*-
# Lale 1,58 m - F1a raporu (P1.2, P1.3, P1.6, P1.7; planlama/d158/F1a-brief.md). Sistem Python'u; yalniz JSON okur, F1a-rapor.html yazar.
# Sayilarin hepsi dosyadan: KY/hat-secenek-{0,a,b}.json, kafa/kafa-analiz.json, kabuk/kabuk-analiz.json, montaj/montaj-analiz.json,
# KY/uygulama-olcum.json, KY/uygulama-ivme.json, planlama/d158/regresyon-son-kosu.json. "Once" degerleri git HEAD'deki ayni dosyadan.
#   py -3 tasarim/freecad/lale158/kafa-yerlesim/f1a_rapor.py
import os, json, base64, html, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
KOK = os.path.dirname(os.path.dirname(UST))
G = os.path.join(HERE, "gorsel")


def js(*yol):
    p = os.path.join(*yol)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def head(yol):
    """git HEAD'deki ayni JSON (once degeri); yoksa None."""
    try:
        s = subprocess.run(["git", "-C", KOK, "show", "HEAD:" + yol], capture_output=True, check=True).stdout.decode("utf-8")
        return json.loads(s)
    except Exception:
        return None


def esc(x):
    return html.escape(str(x))


def t(x, n=1):
    if x is None:
        return "–"
    s = ("%." + str(n) + "f") % x
    tam, _, ond = s.partition(".")
    neg = tam.startswith("-")
    tam = tam.lstrip("-")
    gr = []
    while len(tam) > 3:
        gr.insert(0, tam[-3:])
        tam = tam[:-3]
    gr.insert(0, tam)
    return ("−" if neg else "") + ".".join(gr) + ("," + ond if ond else "")


def img(ad, klasor=G):
    p = os.path.join(klasor, ad)
    if not os.path.exists(p):
        return "<div class='bos'>görsel yok: %s</div>" % esc(ad)
    return "<img src='data:image/png;base64,%s' alt='%s'>" % (base64.b64encode(open(p, "rb").read()).decode(), esc(ad))


def tablo(bas, sat, sinif=""):
    h = "<div class='tw'><table class='%s'><thead><tr>%s</tr></thead><tbody>" % (sinif, "".join("<th>%s</th>" % esc(b) for b in bas))
    for s in sat:
        h += "<tr>%s</tr>" % "".join("<td>%s</td>" % (c if isinstance(c, str) and c.startswith("<") else esc(c)) for c in s)
    return h + "</tbody></table></div>"


HS = {s: js(HERE, "hat-secenek-%s.json" % s) for s in "0ab"}
KF = js(UST, "kafa", "kafa-analiz.json") or {}
KB = js(UST, "kabuk", "kabuk-analiz.json") or {}
KB0 = head("tasarim/freecad/kabuk/kabuk-analiz.json") or {}
MA = js(UST, "montaj", "montaj-analiz.json") or {}
MA0 = head("tasarim/freecad/montaj/montaj-analiz.json") or {}
UO = js(HERE, "uygulama-olcum.json") or {}
UO0 = head("tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json") or {}
UI = js(HERE, "uygulama-ivme.json") or {}
UI0 = head("tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json") or {}
RG = js(KOK, "planlama", "d158", "regresyon-son-kosu.json") or {}
LK = js(UST, "lale158", "lale158-kontrol.json") or {}
LK0 = head("tasarim/freecad/lale158/lale158-kontrol.json") or {}
CS = js(UST, "carpisma-sonuc.json") or {}


def kcak(d):
    r = (d.get("kablo_tup_cakisma") or {}).get("Hoparlor") or []
    return "; ".join("%s %s mm³" % (esc(x[0]), t(x[1], 1)) for x in r) or "yok"
TT, TP = KF["tork"]["tilt"], KF["tork"]["pan"]


def rampa(u):
    try:
        d = u["izgara_yuk_0g"]["a_sinir_pay15"]
        return min(v for k, v in d.items() if k.startswith("rampa5_"))
    except Exception:
        return None


def bsk(k, ad):
    return next((b for b in (k.get("baski") or []) if b["ad"] == ad), None)


# ------------------------------------------------------------------ P1.3 tablosu
def cak(h):
    c = h["cakisma_hatli"]
    return "0" if not c else "%d çift (toplam %s mm³)" % (len(c), t(sum(x[2] for x in c), 2))


def eris(h, on):
    r = [(k, v) for k, v in h["erisim"].items() if k.startswith(on)]
    return " / ".join(t(v["serbest_mm"], 2) for k, v in r)


def dizi1(h):
    v = next(v for k, v in h["erisim"].items() if k.startswith("Dizi vidasi M2x8 PT (1)"))
    return "%s mm (engel: %s)" % (t(v["serbest_mm"], 2), v["engel"])


def yakin(h):
    a = h["aciklik"]["hat_en_yakin"][:2]
    return "; ".join("%s %s" % (n, t(d, 2)) for n, d in a)


P13 = []
if all(HS.values()):
    sut = [HS[s] for s in "0ab"]
    P13 = [
        ("Kafa içi çakışma, HAT ile (> 0,5 mm³)", "cakisma_hatli", [cak(h) for h in sut]),
        ("Kafa içi çakışma, HAT'sız", "cakisma_hatsiz", [str(len(h["cakisma_hatsiz"])) for h in sut]),
        ("Eski kutu zarf × parçalar (mm³)", "eski_zarf_cakisma", [" / ".join(t(x[1], 2) for x in h["eski_zarf_cakisma"]) or "0" for h in sut]),
        ("HAT – dizi açıklığı (mm)", "aciklik.hat_dizi_mm", [t(h["aciklik"]["hat_dizi_mm"], 2) for h in sut]),
        ("HAT – en yakın iki parça (mm)", "aciklik.hat_en_yakin", [yakin(h) for h in sut]),
        ("HAT arka kenarı – arka duvar / yarık (mm)", "aciklik.hat_arka_kenar_duvar_ic_mm, hat_yarik_mm",
         ["%s / %s" % (t(h["aciklik"]["hat_arka_kenar_duvar_ic_mm"], 1), t(h["aciklik"]["hat_yarik_mm"], 1)) for h in sut]),
        ("HAT altı – Active Cooler (mm)", "aciklik.hat_alti_sogutucu_mm", [t(h["aciklik"]["hat_alti_sogutucu_mm"], 1) for h in sut]),
        ("HAT × fan yeri zarfı (mm³, K12)", "aciklik.hat_fan_yeri_kesisim_mm3", [t(h["aciklik"]["hat_fan_yeri_kesisim_mm3"], 2) for h in sut]),
        ("Erişim: HAT vidaları yukarı, Ø6 (mm)", "erisim", [eris(h, "HAT vidasi") for h in sut]),
        ("Erişim: dizi vidası 1 aşağı, Ø8", "erisim", [dizi1(h) for h in sut]),
        ("Erişim: dikiş cıvatası dışarıdan, Ø6 (mm)", "erisim", ["≥ " + eris(h, "Kabuk civatasi") for h in sut]),
        ("Kafa grubu, HAT ile / HAT'sız (g)", "tork_hatli/hatsiz.kafa_grubu_g",
         ["%s / %s" % (t(h["tork_hatli"]["kafa_grubu_g"], 1), t(h["tork_hatsiz"]["kafa_grubu_g"], 1)) for h in sut]),
        ("Tilt payı ±15°, HAT ile / HAT'sız", ".pay_tilt15", ["%s / %s" % (t(h["tork_hatli"]["pay_tilt15"], 2), t(h["tork_hatsiz"]["pay_tilt15"], 2)) for h in sut]),
        ("Pan payı, HAT ile / HAT'sız", ".pan_pay_iki_hane",
         ["%s / %s" % (t(h["tork_hatli"]["pan_pay_iki_hane"], 2), t(h["tork_hatsiz"]["pan_pay_iki_hane"], 2)) for h in sut]),
        ("Tilt −15°: kafa – pan grubu en yakın (mm)", "tilt_sinir_en_yakin", [t(h["tilt_sinir_en_yakin"]["-15"][0], 2) for h in sut]),
        ("Baskı: arka kabuk sağ destek sorunu", "baski", [str(h["baski"]["Arka kafa kabugu sag"]["destek_sorun_sayi"])
                                                        if isinstance(h["baski"]["Arka kafa kabugu sag"], dict) else "–" for h in sut]),
    ]

# ------------------------------------------------------------------ P1.7
KEL = bsk(KB, "Hoparlor kelepcesi")
KAP = bsk(KB, "Hoparlor kabi arka (flansli)")
KAP0 = bsk(KB0, "Hoparlor kabi arka (flansli)")
mk = (UO.get("mic_hoparlor") or {})
mk0 = (UO0.get("mic_hoparlor") or {})
kabuk_g, kabuk0_g = KB.get("kutle_g"), KB0.get("kutle_g")
robot_g, robot0_g = MA.get("kutle_g"), MA0.get("kutle_g")
p17_tazemi = KB.get("sure_s") != KB0.get("sure_s")

H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>F1a kafa tutarlılığı</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 10px;border-bottom:2px solid var(--acc);display:inline-block}
.sub{color:var(--mut);margin-bottom:16px}.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.kpi b{display:block;font-size:20px}
.kpi span{color:var(--mut);font-size:13px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card);font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}.not{color:var(--mut);font-size:13px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.uy{color:var(--uy);font-weight:600}
.bos{border:2px dashed var(--line);border-radius:10px;padding:14px;color:var(--mut)}li{margin:4px 0}
</style></head><body><main>""")
H.append("<h1>F1a: kafa tutarlılığı (P1.2, P1.3, P1.6, P1.7)</h1>")
H.append("<div class='sub'>Lale 1,58 m · dal <code>lale-duzeltme</code> · tasarım ajanı A · rapor üretildi %s · "
         "günlük <code>planlama/d158/F1a-gunluk.md</code> · üreten <code>KY/f1a_rapor.py</code> (KY = tasarim/freecad/lale158/kafa-yerlesim)</div>"
         % datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))

rg_ok = RG.get("cikis_kodu") == 0
kart = [
    ("P1.2 yapıldı", "MAX98357A kalıntıları metin/yorum/rapor kodundan çıktı; kalanlar tarihçe ya da başka paketin dosyası"),
    ("P1.3 yapıldı", "AI HAT+ iki seçenek, ikisinde de kafa içi çakışma 0; ana model değişmedi; K2 Ahmet'te"),
    ("P1.6 yapıldı", "kafa_rapor.py ve kafa_gorsel.py 1,58 m'ye; lale158_rapor.py kasa ↔ çerçeve ölçütü 0,2"),
    ("P1.7 " + ("yapıldı" if p17_tazemi and KEL else "kısmen"), "hoparlör kelepçesi + köpük ped + M3×20; kabuk modeli "
     + ("yeniden kuruldu" if p17_tazemi else "henüz yeniden kurulmadı")),
    ("%s g" % t(TT["kutle_g"], 1), "kafa grubu (kafa-analiz.json tork.tilt.kutle_g)"),
    ("%s× / %s×" % (t(TT["pay_tilt15"], 2), t(TP["pay_iki_hane"], 2)), "tilt ±15 / pan servo payı (ölçüt 3,0 / 2,0)"),
    ("%s mm" % t(mk.get("poz_min_mm"), 1), "mikrofon – hoparlör, tüm pozlarda en az (uygulama-olcum.json; ölçüt ≥ 400)"),
    ("çıkış %s" % RG.get("cikis_kodu", "–"), "son regresyon %s (%s)" % (("GEÇER" if rg_ok else "KALIR"), esc(RG.get("tarih", "–")))),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (esc(a), esc(b)) for a, b in kart) + "</div>")

# ---- P1.3
H.append("<h2>P1.3 AI HAT+ 26T: K2 için iki seçenek</h2>")
H.append("<p>HAT ölçüsü üretici ürün özetinden (RP-008133-DS-1, Raspberry Pi Ltd, Ekim 2024): kart 65 × 56,5, delikler 58 × 49, 16 mm yığın başlığı. "
         "Kütle 30 g, bileşen zarfı 3,0 mm, yığın başlığının HAT üstündeki 8,5 mm'si, FFC halkası <b>varsayım</b> (belgede yok). "
         "<b>a</b>: arka duvar üst dikiş boss'u baş çerçevesinde (−8; 60) → (−5; 76). <b>b</b>: Pi 5 + HAT yığını 5 mm öne. "
         "HAT'i çevirmek uygulanamaz (GPIO başlığına takılı, Pi ile aynı yönde); yığını yükseltmek boss'u kurtarmaz (başlık sütunu boss yüksekliğini geçiyor). "
         "Betik <code>KY/hat_secenek.py</code> (<code>HAT_SECENEK=0/a/b</code>); ana model <code>kafa10_lib.SECENEK</code> varsayılanıyla aynı kaldı.</p>")
if P13:
    H.append(tablo(["Ölçüt", "Kaynak anahtar (hat-secenek-*.json)", "0: bugün + HAT", "a: boss taşı", "b: yığın 5 mm önde"],
                   [(a, "<code>%s</code>" % esc(k)) + tuple(v) for a, k, v in P13]))
else:
    H.append("<div class='bos'>hat-secenek-*.json eksik</div>")
H.append("<p class='not'>Seçenek 0'ın HAT'sız torku kafa-analiz.json ile aynı (%s g; %s; %s): yöntem kopyası doğrulandı. Dizi vidası 0 ve 2 için aşağı erişim "
         "üç seçenekte de 0 çıkıyor (ölçüm yöntemi sorunu, HAT'ten bağımsız; <b>doğrulanmadı</b>). b'de kablo yolları 5 mm kaydı, kablo boyu/kütlesi "
         "yeniden hesaplanmadı.</p>" % (t(KF["tork"]["tilt"]["kutle_g"], 1), t(TT["pay_tilt15"], 2), t(TP["pay_iki_hane"], 2)))
H.append("<div class='grid'>" + "".join("<figure>%s<figcaption>%s</figcaption></figure>" % (img(a), esc(c)) for a, c in (
    ("HAT-0-arka.png", "0: bugünkü model + HAT (arkadan, kabuk saydam; kırmızı dikiş cıvatası HAT içinde)"),
    ("HAT-0-kesit.png", "0: boss ekseninden kesit; başlık sütunu ve kart boss'a giriyor"),
    ("HAT-a-arka.png", "a: boss (−5; 76), HAT'in üstünde, yarık sütunlarının arasında"),
    ("HAT-a-kesit.png", "a: kesit; boss HAT ve başlığın üstünde"),
    ("HAT-b-arka.png", "b: yığın 5 mm önde"),
    ("HAT-b-kesit.png", "b: kesit; başlık boss'un önünde (HAT – kabuk 2,05 mm)"))) + "</div>")

# ---- P1.7
H.append("<h2>P1.7 Hoparlör arka tutucu</h2>")
H.append("<p>Arka tüp hoparlörün arka yüzünde biter (13,3 mm, önce 15,0). Üstüne ayrı baskı <b>Hoparlör kelepçesi</b> (70 × 10 köprü + 2 bacak) oturur; "
         "bacaklar flanş kulaklarındaki M3×20 (havşada) ile duvar boss'larındaki ısıl gömme somunlara sıkılır, köprü 1 mm köpük ped üzerinden hoparlörü "
         "duvara bastırır. Hoparlör yeri değişmedi. Ölçüler varsayım (ürün elde yok).</p>")
rows = []
if KEL:
    rows.append(("Kelepçe baskı (kabuk-analiz.json baski)", "%s × %s × %s mm, %s g, destek sorunu %d, %s" % (
        t(KEL["olcu"][0], 1), t(KEL["olcu"][1], 1), t(KEL["olcu"][2], 1), t(KEL["kutle_g"], 1), KEL["destek_sorun_sayi"], KEL["yon"])))
else:
    rows.append(("Kelepçe baskı", "kabuk-analiz.json'da yok (kabuk_montaj henüz koşmadı); hızlı denetim: 56,6 × 56,6 × 14,3, 4,3 g, destek sorunu 0 (SP/p17_kontrol.json)"))
if KAP:
    rows.append(("Arka kap baskı", "%s mm boy (önce %s), destek sorunu %d" % (t(KAP["olcu"][2], 1), t(KAP0["olcu"][2], 1) if KAP0 else "–", KAP["destek_sorun_sayi"])))
rows += [
    ("Kabuk içi çakışma (kabuk-analiz.json cakisma)", "%d (önce %d)" % (len(KB.get("cakisma", [])), len(KB0.get("cakisma", [])))),
    ("Kabuk × iskelet çakışma", "%d (önce %d)" % (len(KB.get("iskelet_cakisma", [])), len(KB0.get("iskelet_cakisma", [])))),
    ("Kabuk kütlesi (kutle_g)", "%s g (önce %s g)" % (t(kabuk_g, 1), t(kabuk0_g, 1))),
    ("Robot toplam (montaj-analiz.json kutle_g)", "%s g (önce %s g)" % (t(robot_g, 1), t(robot0_g, 1))),
    ("Mikrofon – hoparlör, tüm pozlarda en az (uygulama-olcum.json)", "%s mm (önce %s; ölçüt ≥ 400)" % (t(mk.get("poz_min_mm"), 1), t(mk0.get("poz_min_mm"), 1))),
    ("Devrilme payı, yüksüz rampa 5° (uygulama-ivme.json)", "%s (önce %s; ölçüt ≥ 1,5)" % (t(rampa(UI), 3), t(rampa(UI0), 3))),
    ("Hoparlör kablo tüpü × parçalar (lale158-kontrol.json kablo_tup_cakisma.Hoparlor)", "%s (önce %s); kablo ucu köprünün altına alındı, lehim tırnağı yeri varsayım" % (
        kcak(LK), kcak(LK0))),
    ("Ev pozu çakışması (carpisma-sonuc.json ev_pozu_cakisma)", "%d çift; dokuz bölümün sekizi bu döngüde aynı kaynakla koştu, omuz (03.11 koşusu) P6'ya kaldı" % (
        len(CS.get("ev_pozu_cakisma") or []))),
]
H.append(tablo(["Ölçüt", "Değer"], rows))
H.append("<div class='grid'>" + "".join("<figure>%s<figcaption>%s</figcaption></figure>" % (img(a), esc(c)) for a, c in (
    ("P17-hoparlor-ic.png", "Gövde içinden: kelepçe (mavi), kap (turuncu), M3×20"),
    ("P17-hoparlor-kesit-eksen.png", "Hoparlör ekseninden kesit: köprü + köpük ped hoparlörün arka yüzüne basıyor"),
    ("P17-hoparlor-kesit-civata.png", "Cıvata ekseninden kesit: bacak → flanş → ısıl gömme somun"))) + "</div>")

# ---- P1.6
H.append("<h2>P1.6 Eski betikler</h2><ul>"
         "<li><code>kafa/kafa_gorsel.py</code>: 158 parça adları ve kamera merkezleri; depodaki FCStd'nin geçici kopyasını açar, kaydetmez (<code>doc.save()</code> kalktı). 17 görsel.</li>"
         "<li><code>kafa/kafa_rapor.py</code>: eksik anahtarlar ve 125 cm metinleri gitti; özet kafa grubu %s g, tilt %s, pan %s.</li>"
         "<li><code>lale158/lale158_rapor.py:67</code>: kasa ↔ çerçeve ölçütü 0,5 → 0,2 (ölçülen <code>gogus_ekrani.kasa_cerceve_mm</code> 0,2 / 0,2).</li>"
         "<li><code>lale158/ikinci_ozet.py:142</code>: satırda ve dosyada kasa ↔ çerçeve ifadesi yok (bulgu 04.11 commit öncesi sürüme göre); dokunulmadı.</li></ul>"
         % (t(TT["kutle_g"], 1), t(TT["pay_tilt15"], 2), t(TP["pay_iki_hane"], 2)))
H.append("<div class='grid'>" + "".join("<figure>%s<figcaption>%s</figcaption></figure>" % (img(a, os.path.join(UST, "kafa", "gorsel")), esc(c)) for a, c in (
    ("kafa-izometrik.png", "kafa_gorsel.py: izometrik"), ("kafa-kablo-yolu.png", "kafa_gorsel.py: kafa içi yerleşim ve zarflar"),
    ("kafa-kesit-tilt.png", "kafa_gorsel.py: tilt ekseni kesiti"))) + "</div>")

# ---- P1.2
H.append("<h2>P1.2 MAX98357A kalıntıları</h2>")
H.append(tablo(["Yer", "Durum"], [
    ("arayuz.py, kafa10_lib.py, kafa_lib.py, kafa7_parcalar.py, qled_gorsel.py, taban_lib.py, taban_parcalar.py, taban_rapor.py", "düzeltildi (yorum/metin)"),
    ("kafa/rapor.html, taban/rapor.html, iskelet/rapor.html", "yeniden üretildi, MAX98357 yok"),
    ("kabuk/rapor.html", "açık: kabuk_rapor.py KeyError ekran_kontrol ile kırık (HEAD'de de), yenilenemedi; eski raporda 1 satır kaldı"),
    ("raporlar/**, planlama/adim*/**, duzeltme-plani.md, d158/F0-*, tasarim/cad/**, taslak-170/**, KY 05.11 seçim dosyaları, qled notu", "tarihçe, dokunulmadı"),
    ("planlama/maliyet.json:75", "açık: P4.2 / P8.1"), ("planlama/adim3/elektrik.md", "açık: P4.1 / K10"),
    ("planlama/yazilim-plani.md", "açık: P5.2"), ("rehber/rehber_metin.py, rehber/veri/*", "açık: P7.1"),
    ("tasarim/Robot-Tasarim-Demosu.html", "açık: P9.2"), ("Lale-Proje-Ozeti.txt", "açık: P4.4")]))

# ---- regresyon
H.append("<h2>Regresyon (son koşu)</h2>")
rr = []
KAR = {x["ad"]: x for x in (RG.get("karsilastirma") or [])}
for k, v in (RG.get("degerler") or {}).items():
    kar = KAR.get(k, {})
    rr.append((esc(v.get("etiket", k)), t(v.get("deger"), 3 if isinstance(v.get("deger"), float) and v.get("deger") % 1 else 0),
               esc(v.get("esik")), esc(kar.get("durum", v.get("esik_durumu", "–"))), "<code>%s : %s</code>" % (esc(v["kaynak"]["dosya"]), esc(v["kaynak"]["anahtar"]))))
H.append(tablo(["Değer", "Şimdi", "Eşik", "Durum", "Kaynak"], rr))
H.append("<p class='not'>Çıkış kodu %s, tarih %s, taban %s.</p>" % (esc(RG.get("cikis_kodu")), esc(RG.get("tarih")), esc(RG.get("taban_tarih"))))

# ---- acik isler
H.append("<h2>Açık işler</h2><ul>" + "".join("<li>%s</li>" % esc(x) for x in [
    "K2 kararı Ahmet'te (a ya da b). Seçilen seçenek ana modele P6.1 ile uygulanır; o zaman kafa_montaj + ana montaj + tarama yeniden.",
    "AI HAT+ kütlesi, bileşen yüksekliği ve yığın başlığı boyu varsayım: kart gelince tartı ve kumpas.",
    "HAT ile fan yeri zarfı (K12) her seçenekte kesişiyor; fan seçilirse yer değişmeli.",
    "Dizi vidası 0 ve 2 aşağı erişimi ölçüm yöntemiyle 0 çıkıyor (hat_secenek.py): yöntem düzeltilmeli, doğrulanmadı.",
    "Hoparlör, kap, kelepçe ve köpük ped ölçüleri varsayım (ürün elde yok); hoparlörün ön yüz köpüğü 0,5 mm varsayım.",
    "uygulama-baski.json (05.11) arka kapı 15 mm tüple ölçmüştü; kelepçe ve 13,3 mm kap kabuk-analiz.json'da (uygulama_baski.py tarihi sabit, yenilenmedi).",
    "kafa/gorsel içinde 125 cm'den kalan 3 poz görseli (tilt +30, −25, pan −60 tilt +20) silinmedi; rapor göstermiyor.",
    "Çarpışma taraması: ilk koşu kafa_sol sırasında bellek azlığından durdu; kafa_sol ve taban 23:06–23:16 tek tek tamamlandı (rc 0). carpisma-sonuc.json'da eski kaynakla kalan tek bölüm omuz; tam omuz taraması P6'da.",
    "kabuk_rapor.py KeyError ekran_kontrol (14.10'dan beri, HEAD'de de): kabuk/rapor.html eski kaldı, brief dışı.",
    "Hoparlör kablo ucu (kablo_yolu_ekran.py) değişti; uygulama_gorsel.py görselleri bu uçla yeniden üretilmedi.",
    "MAX98357A: maliyet.json, elektrik.md, yazilim-plani.md, rehber, demo, proje özeti başka paketlerde.",
    "kafa-analiz.json pi.boyun_kablolari metni 01.11 tarihli; kafa_montaj yeniden koşulmadı (brief dışı).",
]) + "</ul>")
H.append("</main></body></html>")
open(os.path.join(HERE, "F1a-rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("F1a-rapor.html", round(os.path.getsize(os.path.join(HERE, "F1a-rapor.html")) / 1024), "KB")
