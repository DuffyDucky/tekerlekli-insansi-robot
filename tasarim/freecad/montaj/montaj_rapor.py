# Ana montaj raporu (rapor.html, gorseller gomulu) + hareket GIF'i. Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: montaj-analiz.json (ana_montaj.py), eklem-dogrulama.json (eklem_dogrulama.py), gui-kontrol.json
# (montaj_gui_kontrol.py), ../carpisma-sonuc.json (carpisma.py), gorsel/*.png (montaj_gorsel.py, montaj_gui_kontrol.py),
# hareket kareleri %TEMP%/robot-montaj-kare/ (montaj_gorsel.py; yoksa mevcut GIF kullanilir)
import os, sys, json, base64, re, html, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
G = os.path.join(HERE, "gorsel")
KARE = os.path.join(tempfile.gettempdir(), "robot-montaj-kare")
sys.path.insert(0, UST)
import arayuz as A

d = json.load(open(os.path.join(HERE, "montaj-analiz.json"), encoding="utf-8"))
e = json.load(open(os.path.join(HERE, "eklem-dogrulama.json"), encoding="utf-8"))
gk = json.load(open(os.path.join(HERE, "gui-kontrol.json"), encoding="utf-8"))
c = json.load(open(os.path.join(UST, "carpisma-sonuc.json"), encoding="utf-8"))

# ---------------------------------------------------------------- GIF (iki kol birlikte, cozucu simulasyon kareleri)
GIF = os.path.join(G, "montaj-hareket.gif")
if os.path.exists(os.path.join(KARE, "pozlar.txt")):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    pozlar = [list(map(float, l.split())) for l in open(os.path.join(KARE, "pozlar.txt")) if l.strip()]
    frames = []
    for k, satir in enumerate(pozlar):
        if len(satir) == 5:                       # eski bicim: yalniz omuz
            satir = satir[:3] + [0.0, 0.0] + satir[3:] + [0.0, 0.0]
        t, sp, sy, sd, sb, lp, ly, ld, lb = satir
        im = Image.open(os.path.join(KARE, "k%03d.png" % k)).convert("RGB").resize((630, 448), Image.LANCZOS)
        dr = ImageDraw.Draw(im)
        dr.rectangle((6, 5, 478, 50), fill=(255, 255, 255))
        dr.text((12, 8), "Sağ: öne %+4.0f°  yana %3.0f°  dirsek %3.0f°  bilek %+3.0f°" % (sp, sy, sd, sb), fill=(30, 30, 30), font=font)
        dr.text((12, 29), "Sol: öne %+4.0f°  yana %3.0f°  dirsek %3.0f°  bilek %+3.0f°" % (lp, ly, ld, lb), fill=(30, 30, 30), font=font)
        dr.text((540, 425), "t = %.1f s" % t, fill=(110, 110, 110), font=font)
        frames.append(im.quantize(colors=48, method=Image.Quantize.MEDIANCUT))
    frames[0].save(GIF, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)
    print("GIF", len(frames), "kare", os.path.getsize(GIF) // 1024, "kB")


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
    return ("-" if neg and s.strip("-0.,") else "") + ".".join(gr) + ("," + ond if ond else "")


def bilimsel(x):
    if x == 0:
        return "0"
    m, ex = ("%.1e" % x).split("e")
    return "%s·10<sup>%d</sup>" % (m.replace(".", ","), int(ex))


def esc(s):
    s = html.escape(str(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def img64(ad):
    yol = os.path.join(G, ad)
    tip = "gif" if ad.endswith(".gif") else "png"
    return "data:image/%s;base64,%s" % (tip, base64.b64encode(open(yol, "rb").read()).decode())


def tablo(baslik, satirlar, sinif=""):
    h = ["<table class='%s'><tr>" % sinif + "".join("<th>%s</th>" % b for b in baslik) + "</tr>"]
    for s in satirlar:
        h.append("<tr>" + "".join("<td>%s</td>" % x for x in s) + "</tr>")
    h.append("</table>")
    return "".join(h)


MODAD = {"iskelet": "İskelet", "omuz_sag": "Sağ omuz", "omuz_sol": "Sol omuz", "kabuk": "Kabuk", "dirsek_sag": "Sağ dirsek",
         "dirsek_sol": "Sol dirsek"}
GRUPAD = {"Iskelet": "iskelet", "Kabuk": "kabuk", "OmuzSag_Govde": "sağ omuz gövde", "OmuzSag_Gobek": "sağ omuz göbeği",
          "OmuzSag_Kol": "sağ üst kol", "OmuzSol_Govde": "sol omuz gövde", "OmuzSol_Gobek": "sol omuz göbeği",
          "OmuzSol_Kol": "sol üst kol", "DirsekSag_UstKol": "sağ dirsek çatalı", "DirsekSag_OnKol": "sağ ön kol",
          "DirsekSag_El": "sağ el", "DirsekSol_UstKol": "sol dirsek çatalı", "DirsekSol_OnKol": "sol ön kol", "DirsekSol_El": "sol el"}
EKAD = {"one_arka": "öne-arka (S1)", "yana": "yana açma (S2)", "dirsek": "dirsek", "bilek": "bilek"}
EKKISA = {"one_arka": "öne", "yana": "yana", "dirsek": "dirsek", "bilek": "bilek"}


def komut_yaz(komut):
    """{modul: {eklem: derece}} -> 'sağ öne 90° yana 0° dirsek 60°; sol ...' (omuz ve dirsek ayni kolda birlesir)."""
    kol = {}
    for m, a in komut.items():
        t = "sağ" if m.endswith("_sag") else "sol"
        kol.setdefault(t, []).extend("%s %s°" % (EKKISA[k], sayi(v, 0)) for k, v in a.items())
    return "; ".join("%s %s" % (t, " ".join(v)) for t, v in sorted(kol.items(), key=lambda x: x[0] != "sağ"))


n_revolute = sum(1 for j in d["eklemler"] if j["tip"] == "Revolute")
n_eksen_kol = n_revolute // 2
K = d["karsilastirma"]
CG = d["agirlik_merkezi"]
oz = e["ozet"]
mx_mm = max(v["max_mm"] for v in e["vakalar"] if v["sinir_ici"])
mx_dg = max(v["max_derece"] for v in e["vakalar"] if v["sinir_ici"])
n_vaka = sum(1 for v in e["vakalar"] if v["sinir_ici"])
n_kare = sum(v["kare"] for v in e["vakalar"] if v["sinir_ici"])
tarama = c["tarama"]
n_poz = sum(t["poz_sayisi"] for t in tarama.values())
gui_ok = (gk["acilis"]["parca_gorunur"] == gk["acilis"]["parca"] and all(x["gorunur"] for x in gk["eklemler"].values())
          and all(gk["secim"].values()) and all(p["nesne"] == j for j, p in gk["pick"].items()) and not gk["hatalar"])
sur = gk["surukleme"]


def sur_aralik(kol, eklem):
    vs = [s["yol_boyunca"][eklem] for s in sur if s["kol"] == kol and s["kol_hareket_etti"] and eklem in s["yol_boyunca"]]
    vs = [v for v in vs if v[0] != v[1]]
    return (min(v[0] for v in vs), max(v[1] for v in vs)) if vs else None


# ---------------------------------------------------------------- tablolar
mod_satir = []
for m in d["moduller"]:
    mod_satir.append(["<b>%s</b>" % MODAD.get(m["ad"], m["ad"]), "%d" % m["parca"] + (" <span class='not'>(modülde %d)</span>" % m["parca_modulde"] if m["haric"] else ""),
                      sayi(m["kutle_g"], 1) + " g", "(%s; %s; %s)" % tuple(sayi(x, 1) for x in m["agirlik_merkezi"]),
                      "(%s; %s; %s)" % tuple(sayi(x, 0) for x in m["konum"]), "X aynası (gerçek aynalı geometri)" if m["ayna"] else "–",
                      esc(", ".join(m["haric"]) or "–"), esc(", ".join(GRUPAD.get(g, g) for g in m["gruplar"]))])
mod_satir.append(["<b>Toplam</b>", "<b>%d</b>" % d["parca_sayisi"], "<b>%s g</b>" % sayi(d["kutle_g"], 1),
                  "<b>(%s; %s; %s)</b>" % tuple(sayi(x, 1) for x in CG), "", "", "", "%d grup" % d["grup_sayisi"]])

ek_satir = []
for j in d["eklemler"]:
    if j["tip"] == "Grounded":
        ek_satir.append([esc(j["etiket"]), "Zemine sabit", esc(GRUPAD.get(j["alt"], j["alt"])), "–", "–", "–", "–"])
        continue
    if j["tip"] == "Fixed":
        ek_satir.append([esc(j["etiket"]), "Sabit (Fixed)", esc("%s → %s" % (GRUPAD.get(j["ust"]), GRUPAD.get(j["alt"]))),
                         "(%s; %s; %s)" % tuple(sayi(x, 1) for x in j["nokta"]), "–", "–", esc(j["aciklama"])])
        continue
    o = oz[j["isim"]]
    kol = "sag" if "Sag" in j["isim"] else "sol"
    sr = sur_aralik(kol, j["anahtar"])
    ek_satir.append([
        "<b>%s %s</b>" % ("Sağ" if kol == "sag" else "Sol", EKAD[j["anahtar"]]), "Döner (Revolute)",
        esc("%s → %s" % (GRUPAD.get(j["ust"]), GRUPAD.get(j["alt"]))),
        "(%s; %s; %s) · yön (%s; %s; %s)" % (tuple(sayi(x, 1) for x in j["nokta"]) + tuple(sayi(x + 0.0, 0) for x in j["eksen"])),
        "%s° … %s°" % (sayi(j["sinir"][0], 0), sayi(j["sinir"][1], 0)),
        "%s mm · %s° <span class='not'>(%d poz)</span>" % (bilimsel(o["max_mm"]), bilimsel(o["max_derece"]), o["vaka"]),
        ("%s° … %s° arası sürüklendi" % (sayi(sr[0], 0), sayi(sr[1], 0))) if sr else "–"])

vaka_satir = []
for v in e["vakalar"]:
    kom = komut_yaz(v["komut"])
    vaka_satir.append([esc(kom), "%d" % v["kare"], bilimsel(v["max_mm"]), bilimsel(v["max_derece"]), bilimsel(v["max_aci_hatasi"])])
sd_satir = []
for v in e["sinir_disi"]:
    k, a = list(v["komut"].items())[0]
    son = list(v["son_aci"].values())
    olc = "; ".join(sayi(abs(x[1]) if abs(abs(x[1]) - 180) < 1e-6 else x[1], 1) + "°" for x in son if abs(x[1]) > 1e-6) or "0°"
    sd_satir.append([esc(komut_yaz(v["komut"])),
                     olc, bilimsel(v["max_mm"]), "sınır uygulanmadı, komut aynen izlendi"])
sv_satir = []
for s in e["solve_testi"]:
    sv_satir.append([esc(komut_yaz({s["kol"]: s["poz"]})),
                     "evet" if s["sinir_ici"] else "<b>hayır</b>", " · ".join("%s %s°" % (EKKISA[k], sayi(x, 0)) for k, x in s["olculen"].items()),
                     bilimsel(s["max_mm"])])
sr_satir = []


def yol(s, k):
    v = s["yol_boyunca"].get(k)
    return "%s° … %s°" % (sayi(v[0], 1), sayi(v[1], 1)) if v else "–"


for s in sur:
    sr_satir.append(["%d" % s["deneme"], "sağ" if s["kol"] == "sag" else "sol", esc(s["aciklama"].replace("gobekten", "göbekten").replace("tupundan", "tüpünden")
                                                                                .replace("acma", "açma").replace("disari", "dışarı").replace("iceri", "içeri")
                                                                                .replace("one kaldirma", "öne kaldırma").replace("gorunum", "görünüm")
                                                                                .replace("sinir", "sınır").replace("cok", "çok").replace("basin ustune", "başın üstüne")),
                     esc(s["tiklanan"]), yol(s, "one_arka"), yol(s, "yana"), yol(s, "dirsek"),
                     "öne %s° · yana %s°" % (sayi(s["sonra"]["one_arka"][0], 1), sayi(s["sonra"]["yana"][0], 1)) +
                     (" · dirsek %s°" % sayi(s["sonra"]["dirsek"][0], 1) if "dirsek" in s["sonra"] else "")])
kt = c.get("kol_tarama") or {}
kk = c.get("kol_kol")
n_poz += sum(k["kaba_izgara"]["tam_poz"] + k["aralik_disi_halka"]["tam_poz"] for k in kt.values())
kol_satir = []
for taraf, k in kt.items():
    for m, b in sorted(k["en_kucuk_bosluk_aralikta"].items(), key=lambda x: x[1]["bosluk_mm"]):
        kol_satir.append(["%s kol" % ("Sağ" if taraf == "sag" else "Sol"), esc(m), sayi(b["bosluk_mm"], 1) + " mm",
                          esc("%s ↔ %s" % (b["parca"], b["hedef"])),
                          esc("öne %s° yana %s°" % (sayi(b["poz"][0], 0), sayi(b["poz"][1], 0)) +
                              ("" if len(b["poz"]) < 3 else " dirsek %s°" % sayi(b["poz"][2], 0)) +
                              ("" if len(b["poz"]) < 4 else " bilek %s°" % sayi(b["poz"][3], 0)))])
tar_satir = []
for ad, t in tarama.items():
    yk = t["en_yakin"]
    tar_satir.append([MODAD.get(ad, ad), "%d" % t["poz_sayisi"], "%d" % t["cakisan_poz"], "%d" % t["eklem_araliginda_cakisan"],
                      sayi(t["en_kucuk_bosluk_mm"]) + " mm",
                      esc("%s ↔ %s / %s, öne %s° yana %s°" % (yk[1], yk[2], yk[3], yk[0][0], yk[0][1])) if yk else "–"])

ADIM = [
    "FreeCAD 1.1'de **Dosya → Aç** ile `tasarim/freecad/montaj/robot-montaj.FCStd` dosyasını aç. Model ağacında **Robot** montajı, "
    "altında **Eklemler** (%d eklem) ve %d parça grubu görünür." % (len(d["eklemler"]), d["grup_sayisi"]),
    "Ağaçta **Robot**'a çift tıkla: montaj etkinleşir (Assembly tezgâhı açılır, eklem işaretleri görünür).",
    "Kolu fareyle tut ve sürükle: **yana açma** için mavi üst kol tüpünden, **öne kaldırma** için omuz göbeğinden (mavi kutu) tut. "
    "Eklem sınırlarında kol durur. Göbek eksene yakın olduğu için küçük fare hareketi büyük dönüş verir; yavaş sürükle. "
    "**Dirsek** için ön kolu (mavi, servolu gövde) tutup öne-yukarı sürükle; bilek fareyle zor tutulur (el küçük), simülasyonla oynat.",
    "Hazır hareket için ağaçta **Simulations → Kollari_oynat**'a çift tıkla, açılan panelde **Run Kinematics** (kinematiği çalıştır) düğmesine, "
    "sonra ▶ (ileri oynat) düğmesine bas. Paneli **OK** ile kapat. Kollar son karede kalır; sıfır pozuna dönmek için dosyayı "
    "kaydetmeden kapatıp yeniden aç.",
]

KARAR = [
    "**Sol omuz gerçek aynalı geometri:** Placement aynalama yapamaz; sağ omuzun her parçasının şekli `mirror` ile X'te aynalanıp "
    "konumuna kopyalanarak taşındı (`transformShape(m, True)`). Hacim farkı %s mm³, aynalı parçaların kendi kütle merkezi ile aynalanmış "
    "yerel merkez farkı %s mm. Sol parçaların adı \"(sol)\" ile bitiyor, `Aynali` özelliği doğru." % (bilimsel(d["hacim_fark_mm3"]), bilimsel(d["ayna_merkez_fark_mm"])),
    "**Yerleşim yalnız `arayuz.MODULLER`'den:** Ana montajda tek bir yerleşim sayısı yazılmadı. Omuz yuvası sabit eklem noktası "
    "`arayuz.OMUZ_YUVA_X` ortası (x = ±%s). Eklem eksenleri ve sınırları `omuz/omuz-montaj.FCStd`'deki eklemlerden okunuyor, solda "
    "eksen eksenel vektör olarak aynalanıyor (a′ = −M·a): öne-arka ekseni her iki kolda −X, yana açma ekseni sağda +Z, solda −Z. "
    "Böylece pozitif açı iki kolda da aynı hareketi veriyor." % sayi(sum(A.OMUZ_YUVA_X) / 2, 1),
    "**Öne-arka sınırı neden −45…135°, serbest aralık −60…180° iken:** −60…180° omuz taramasında *çarpışmanın olmadığı* aralık "
    "(geometri sınırı). Eklem sınırı ise servonun dönebildiği aralık: DS3218MG'nin 180° sürümü, horn kol aşağıdayken servo 45° "
    "konumunda takılıyor (omuz montaj sırası, 5. adım). Servo 0…180° → eklem −45…135°. Yana açmada sınır 0…120° (omuz_montaj); 0°'nin altında kol "
    "gövdeye çarpıyor (omuz taraması yana −20…−5°). 270° servo alınırsa sınırlar −60…180°'e kadar açılabilir "
    "(geometri izin veriyor); o zaman `omuz_montaj.py` güncellenip ana montaj yeniden kurulur.",
    "**Dirsek modülü omuz zincirine bağlı:** her dirsek çatalı omuzun Kol grubuna sabit eklemle (üst kol tüpünün ucu, pim + sıkma bileziği) "
    "bağlı; her kolda üst kol → ön kol (dirsek, 0…105°) ve ön kol → el (bilek, −90…90°) döner eklemleri. Eksen ve sınırlar "
    "`dirsek/dirsek-montaj.FCStd`'den okunuyor ve `arayuz.DIRSEK` ile karşılaştırılıyor; solda eksen aynalanıyor. Pozitif dirsek açısı iki kolda "
    "ön kolu öne büker, pozitif bilek açısı avucu öne çevirir. Sol dirsek sağın gerçek aynalı geometrisi.",
    "**Travers bir kez sayılıyor:** Omuz modülünün içindeki 200 mm traversi iskeletin parçası; ana montajda yalnız iskeletinki var. "
    "Omuzdaki kabuk duvarı (referans, 0 g) ana montajda yok; yerini gerçek kabuk modülü aldı (`kabuk/`). Parça sayısı %d = %s." % (d["karsilastirma"]["parca"]["montaj"], d["karsilastirma"]["parca"]["formul"]),
    "**Eklem yapısı:** İskelet zemine sabit (grounded); her omuz gövdesi ve kabuk iskelete sabit eklemle bağlı; her omuzda gövde → göbek "
    "(öne-arka) ve göbek → kol (yana açma), her dirsekte üst kol → ön kol (dirsek) ve ön kol → el (bilek) döner eklemleri. "
    "Serbestlik: %d (her kolda %d)." % (n_revolute, n_eksen_kol),
]

ACIK = [
    "**Eklem sınırları çözücüde zorlanmıyor:** FreeCAD 1.1'de sınırlar yalnız fareyle sürüklemede uygulanıyor (yana 0…120°, öne "
    "−45…135° aşılmadı). Simülasyon (Motion) ve `solve()` sınır dışı açıyı aynen kabul ediyor (öne 160°, 180°, −60°; yana 140°, −15°). "
    "Simülasyon formülü yazarken sınırları elle gözet; robot yazılımında servo açısı ayrıca sınırlanmalı.",
    "**Öne kaldırma kol tüpünden sürüklenmiyor:** Kol aşağıdayken üst kol tüpünü tutup sürüklemek öne-arka eksenini döndürmedi "
    "(yalnız yana açma döndü). Göbekten tutunca dönüyor ama göbek eksene yakın (≈ 40 mm) olduğu için hareket sıçramalı, serbest kol da "
    "salınıyor. Kesin açı için simülasyon veya eklem açısını betikle ver.",
    "**Sol kolda servo dönüş yönü ters:** Sol S1 ve S2 servoları aynalı yerleşimde; aynı eklem açısı (ör. öne +30°) için sol servo "
    "kendi mil yönüne göre ters döner. Yazılımda sol servoların komut işareti çevrilmeli, horn takma açısı da aynalı (sol S1 135° "
    "konumunda takılır) (tahmini; servo montajında doğrulanmalı).",
    "**Sol baskı parçaları aynalı basılmalı:** Omuz yuvası, rulman kapağı, omuz göbeği, kol çatalı ve tüp sağın aynası. Dilimleyicide "
    "STL'ler X'te aynalanarak basılır (`omuz/stl/` yalnız sağ). Servo, horn, rulman ve cıvatalar simetrik kabul edildi: DS3218MG gövdesi "
    "genişlik yönünde simetrik, aynası 180° çevrilmiş servo ile aynı (tahmini; kablo çıkışı tarafı farklı olabilir).",
    "**Kafa ve taban henüz yok:** `moduller.py`'de `SIRA` listesine eklenip birer yükleyici yazılınca ana montaja girer. Kafa pan/tilt "
    "eklemleri dirsekteki gibi `eklemler` + `beklenen` ile tanımlanır.",
    "**Bilek fareyle zor sürükleniyor:** el küçük ve ön kol ekseninde döndüğü için 3B görünümde tutup çevirmek pratik değil; bilek açısını "
    "simülasyonla (Kollari_oynat) ya da betikle ver.",
    "**Montaj dosyası iki adımda üretiliyor:** `ana_montaj.py` (arayüzsüz) dosyayı kurar, `montaj_gorsel.py` (GUI) eklem görünüm "
    "nesnelerini ve simülasyonu ekleyip yeniden kaydeder. Yalnız `ana_montaj.py` çalıştırılırsa dosya açıldığında eklem işaretleri görünmez.",
    "**Kütle ve ağırlık merkezi tabansız:** %s kg, AM yerden %s mm (iskelet + iki omuz + kabuk + iki dirsek). Akü, motorlar ve tekerler gelince AM "
    "belirgin şekilde aşağı iner." % (sayi(d["kutle_g"] / 1000, 2), sayi(CG[1], 0)),
]

# ---------------------------------------------------------------- HTML
H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Robot Ana Montajı</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:18px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
figure img{width:100%;display:block;background:#fff}figcaption{padding:8px 12px;color:var(--mut);font-size:13px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;background:var(--card);border-radius:10px;overflow:hidden;font-size:14px}
td,th{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}th{background:rgba(47,134,212,.12)}
table.sayi td:not(:first-child){text-align:right;white-space:nowrap}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:21px}.kpi span{color:var(--mut);font-size:13px}
ol li,ul li{margin:5px 0}code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px}
.ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}.wide{grid-column:1/-1}
.not{color:var(--mut);font-size:13px}
</style></head><body><main>""")
H.append("<h1>Robot ana montajı: iskelet + omuzlar + kabuk + dirsekler</h1>")
H.append("<div class='sub'>FreeCAD 1.1 Assembly · <code>ana_montaj.py</code> · %d parça, %d grup, %d eklem · yerleşim <code>arayuz.MODULLER</code>'den · "
         "sol omuz ve sol dirsek gerçek aynalı geometri</div>" % (d["parca_sayisi"], d["grup_sayisi"], len(d["eklemler"])))
kpi = [
    ("%d" % d["parca_sayisi"], "parça (%s) · tümü geçerli, STEP geri okuma %d katı" % (d["karsilastirma"]["parca"]["formul"], d["step_kati"])),
    ("%s kg" % sayi(d["kutle_g"] / 1000, 2), "kütle · AM (%s; %s; %s) mm · modül toplamından fark %s g" % (sayi(CG[0], 1), sayi(CG[1], 0), sayi(CG[2], 1), sayi(K["kutle"]["fark_analiz"], 2))),
    ("%d" % c["toplam"]["eklem_araliginda"], "eklem aralığında modüller arası çakışma (ev pozu + %d poz tarama; aralık dışı %d)" % (
        n_poz, c["toplam"]["cakisma"] - c["toplam"]["eklem_araliginda"])),
    ("%d eksen" % n_revolute, "2 kol × (öne-arka, yana açma, dirsek, bilek) · iskelet zemine sabit, omuzlar ve kabuk iskelete, dirsekler "
                              "omuz koluna sabit"),
    ("%s mm" % bilimsel(mx_mm).replace("<sup>", "<sup>"), "eklem doğrulama en büyük sapma (%d poz, %d çözücü karesi) · açı %s°" % (n_vaka, n_kare, re.sub("<.*?>", "", bilimsel(mx_dg)).replace("·10", "e"))),
    ("doğrulandı" if gui_ok else "SORUN", "GUI'de açılış: eklemler görünür, ağaçta ve 3B'de seçilebilir, sürükleme çalışıyor"),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")

H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (("montaj-izometrik.png", "İzometrik: iskelet, iki omuz, kabuk ve iki dirsek", ""),
                   ("montaj-on.png", "Önden (+Z'den bakış; robotun sağı görüntünün solunda)", ""),
                   ("montaj-yan.png", "Yandan (+X'ten bakış)", ""),
                   ("montaj-omuzlar.png", "Omuzlar yakından: sol omuz sağın aynası", "wide"),
                   ("montaj-dirsek.png", "Sağ dirsek ev pozunda: kol aşağıda, çatal kabuğun yanında", ""),
                   ("montaj-poz-selam.png", "Poz: sağ kol yana 100°, öne 20°, dirsek 95°, bilek −60°; sol kol yana 10°, dirsek 30°", ""),
                   ("montaj-poz-one.png", "Poz: iki kol öne 90°, dirsek 60°, bilek 45°", ""),
                   ("montaj-hareket.gif", "İki kol birlikte (Kollari_oynat simülasyonu, FreeCAD çözücüsünün kareleri): omuzlar zıt fazda öne-arka sallanır, "
                    "birlikte öne kalkıp yana açılır; sağ dirsek iki kez, sol dirsek bir kez bükülür, bilekler zıt yönde döner", "wide")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div>")

H.append("<h2>Modüller</h2><div class='tw'>")
H.append(tablo(["Modül", "Parça", "Kütle", "Ağırlık merkezi (mm)", "Yerel orijin (global)", "Dönüş", "Ana montajda yok", "Gruplar"], mod_satir))
H.append("</div><p class='not'>Kütle ve AM dosyadan geri okunarak hesaplandı (her parçanın <code>Kutle_g</code> özelliği ve katı kütle merkezi). "
         "Modül analizlerinin toplamı (iskelet + 2 × omuz, travers hariç + kabuk + 2 × dirsek) = %s g, <code>carpisma.py</code> = %s g; fark %s g (analiz JSON'ları 0,1 g'a yuvarlı). "
         "AM, <code>carpisma.py</code> sonucundan %s mm farklı (yuvarlama). Parça sayısı %d = %s.</p>" % (
             sayi(K["kutle"]["beklenen_analizlerden"], 1), sayi(K["kutle"]["carpisma"], 1), sayi(K["kutle"]["fark_analiz"], 3),
             sayi(K["am"]["fark_carpisma_mm"], 3), K["parca"]["montaj"], esc(K["parca"]["formul"])))

H.append("<h2>Eklemler</h2><div class='tw'>")
H.append(tablo(["Eklem", "Tip", "Bağladığı", "Konum ve eksen (global, mm)", "Sınır", "Doğrulama sapması (kolun tüm pozlarında en büyük)", "Sürükleme (GUI, yol boyunca)"], ek_satir))
H.append("</div><p class='not'>Pozitif açı: öne-arka = kol öne (+Z) kalkar, yana açma = kol dışarı açılır (sağda +X, solda −X). Çözücü sonrası "
         "kol ucu kontrolü: öne +90° → (±185; 955; 140), yana +90° → (±325; 955; 0); iki kolda %s.</p>" % (
             "doğru" if all(y["dogru"] for y in e["yon"]) else "<b>YANLIŞ</b>"))

H.append("<h2>Eklem doğrulaması</h2>")
H.append("<p><b>Yöntem:</b> FreeCAD 1.1'de Revolute açısı doğrudan sürülemiyor (<code>Angle</code> yalnız Angle ekleminde). Eklemler Create "
         "Simulation'ın kullandığı yolla sürüldü: her döner ekleme bir hareket (Motion, Angular, formül = açı × time), 0…1 s, 0,02 s adım. "
         "Her karede çözücünün verdiği grup yerleşimi, omuz modülünün kendi kinematiğiyle (<code>omuz_parcalar.Pp/Pr</code>, solda X aynasıyla "
         "<code>T·R·P·R·T⁻¹</code>) karşılaştırıldı. Sapma: grubun sınır kutusu köşelerindeki en büyük konum farkı ve dönüş farkı. "
         "Birim testi: formül 1 rad → %s° (formül radyan).</p>" % sayi(e["birim"]["olculen_derece"], 3))
H.append("<p>Sonuç: sınır içindeki %d pozun (omuz sağ/sol 10'ar, omuz + dirsek + bilek sağ/sol 10'ar, iki kol birlikte %d) tüm karelerinde en büyük "
         "sapma <b>%s mm</b> ve <b>%s°</b>; sürülmeyen gruplar (iskelet, omuz gövdeleri, kabuk, diğer kol) yerinde kaldı, dirsek grupları omuzla "
         "birlikte doğru taşındı. Eksenler ve sol aynalama doğru.</p>" % (
             n_vaka, sum(1 for v in e["vakalar"] if v["ad"].startswith("iki kol")), bilimsel(mx_mm), bilimsel(mx_dg)))
H.append("<div class='tw'>" + tablo(["Sürülen poz", "Kare", "Konum sapması mm", "Dönüş sapması °", "Açı hatası °"], vaka_satir, "sayi") + "</div>")
H.append("<h3>Sınır dışına sürülünce</h3><p>Simülasyon sınırları uygulamıyor: komut edilen açı aynen izleniyor. <code>solve()</code> da (GUI'de "
         "<i>Solve</i>, <code>doc.recompute()</code>) elle verilen sınır dışı pozu geri çekmiyor. Sınırlar yalnız fareyle sürüklemede durduruyor "
         "(aşağıdaki GUI tablosu).</p><div class='tw'>")
H.append(tablo(["Simülasyonla sürülen", "Ölçülen açı", "Konum sapması mm", "Davranış"], sd_satir))
H.append("</div><div class='tw' style='margin-top:10px'>")
H.append(tablo(["Elle verilen poz + solve()", "Sınır içinde", "Solve sonrası açı", "Konum sapması mm"], sv_satir))
H.append("</div>")

H.append("<h2>GUI'de açılış ve sürükleme</h2>")
a = gk["acilis"]
H.append("<p><code>montaj_gui_kontrol.py</code> dosyayı FreeCAD arayüzünde hiçbir düzeltme yapmadan açtı: %d/%d parça ve %d grup görünür, "
         "%d eklemin hepsinin görünüm nesnesi var ve görünür (%s), hepsi ağaçta seçilebiliyor, %d döner eklemin (dirsek ve bilek dahil) işareti "
         "3B görünümde tıklanınca eklemin kendisi seçiliyor. Robot montajı etkinleştirildi (çift tık karşılığı) ve kol, Qt fare olaylarıyla 3B "
         "görünümde sürüklendi. Simülasyon <code>Kollari_oynat</code> (%d hareket) görünüm nesnesiyle açılıyor.</p>" % (
             a["parca_gorunur"], a["parca"], a["grup_gorunur"], len(gk["eklemler"]), ", ".join(sorted(set(x["vp"] for x in gk["eklemler"].values()))),
             sum(1 for x in gk["eklemler"].values() if x["tip"] == "Revolute"), len(a["hareket"])))
H.append("<div class='grid'>")
sur_d = [x for x in sur if x["aciklama"].startswith("dirsek") and "dirsek" in x["sonra"]]
for ad, cap in (("montaj-gui-eklemler.png", "Montaj etkin, eklem işaretleri görünür; sağ dirsek eklemi seçili (bağladığı üst kol ve ön kol vurgulu)"),
                ("montaj-gui-surukleme.png", "Fareyle sürükleme: sağ kol yana %s° açıldı" % sayi(sur[0]["sonra"]["yana"][0], 0)),
                ("montaj-gui-dirsek.png", "Fareyle sürükleme: sağ dirsek %s° büküldü" % (sayi(sur_d[0]["sonra"]["dirsek"][0], 0) if sur_d else "?")),
                ("montaj-gui-agac.png", "Model ağacı: Robot montajı, Eklemler, %d grup, Kollari_oynat simülasyonu" % d["grup_sayisi"])):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (img64(ad), esc(cap), esc(cap)))
H.append("</div><h3>Sürükleme denemeleri</h3><div class='tw'>")
H.append(tablo(["#", "Kol", "Deneme", "Tutulan parça", "Öne-arka (yol boyunca)", "Yana (yol boyunca)", "Dirsek (yol boyunca)", "Bırakınca"], sr_satir))
H.append("</div><p class='not'>Yana açma: sürüklemede 120°'de ve 0°'da duruyor. Öne-arka: göbekten sürüklemede −45° ile 135° arasında kaldı; "
         "kol tüpünden sürüklemede dönmedi (açık işler). Dirsek: ön koldan sürüklemede döndü ve 0…105° içinde kaldı. Kol uzadığı için yana açmayı "
         "sınıra zorlayan sürüklemede çözücü serbest zinciri (öne-arka, dirsek) de sallayabiliyor; bırakınca açılar yine sınırlar içinde.</p>")

H.append("<h2>Çakışma (carpisma.py, yeniden koşuldu)</h2><h3>Omuz taraması (yalnız omuz parçaları)</h3><div class='tw'>")
H.append(tablo(["Hareketli modül", "Poz", "Çakışan poz", "Eklem aralığında", "En küçük boşluk", "En yakın çift"], tar_satir))
H.append("</div><p class='not'>Omuz tarama aralığı: %s. Aralık dışındaki çakışmalar eklem sınırlarıyla engelleniyor.</p>" % esc(list(tarama.values())[0]["aciklama"]))
if kt:
    k0 = list(kt.values())[0]
    H.append("<h3>Kol zinciri taraması (omuz × dirsek × bilek, dirsek parçaları)</h3>")
    H.append("<p>Kaba ızgara: öne-arka %s…%s° (15° adım), yana %s…%s° (15°), dirsek %s, bilek %s = kol başına <b>%d poz</b>; aralık dışı halka %d poz; "
             "5 mm'nin altında boşluk kalan alt pozların çevresi 5° adımla yeniden tarandı (%d alt poz). Eklem aralığında çakışma: sağ <b>%d</b>, sol <b>%d</b>; "
             "aralık dışı halkada sağ %d, sol %d poz (yana −10°: el kabuğa değiyor; omuz yana sınırı 0° bunu engelliyor). Kol ↔ kol (iki kol aynı anda, "
             "%d poz çifti: simetrik, zıt, birlikte öne): çakışma %d, en küçük boşluk %s mm.</p>" % (
                 k0["kaba_izgara"]["one_arka"][0], k0["kaba_izgara"]["one_arka"][-1], k0["kaba_izgara"]["yana"][0], k0["kaba_izgara"]["yana"][-1],
                 k0["kaba_izgara"]["dirsek"], k0["kaba_izgara"]["bilek"], k0["kaba_izgara"]["tam_poz"], k0["aralik_disi_halka"]["tam_poz"],
                 k0["alt_poz"]["ince"], kt["sag"]["cakisan_tam_poz_aralikta"], kt["sol"]["cakisan_tam_poz_aralikta"],
                 kt["sag"]["cakisan_tam_poz_aralik_disi"], kt["sol"]["cakisan_tam_poz_aralik_disi"],
                 kk["poz_cifti"] if kk else 0, kk["cakisan"] if kk else 0, sayi(kk["en_kucuk"]["bosluk_mm"], 0) if kk else "–"))
    H.append("<div class='tw'>" + tablo(["Kol", "Hedef", "En küçük boşluk (eklem aralığında)", "Parça çifti", "Poz"], kol_satir) + "</div>")
H.append("<p>Ev pozunda %d çakışma (%d sınır kutusu kesişen çift gerçek kesişimle sınandı). Eklem aralığında toplam <b>%d</b>, aralık dışı dahil %d. "
         "Ayrılmış bölgeler (%s) de tarandı.</p>" % (len(c["ev_pozu_cakisma"]), c["ev_pozu_kesisen_cift"], c["toplam"]["eklem_araliginda"],
                                                    c["toplam"]["cakisma"], ", ".join(c["ayrilmis_bolge"]["sahipler"])))

H.append("<h2>FreeCAD'de kolları oynatmak</h2><ol>" + "".join("<li>%s</li>" % esc(s) for s in ADIM) + "</ol>")
H.append("<h2>Kararlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in KARAR) + "</ul>")
H.append("<h2>Açık işler</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar ve çalıştırma sırası</h2><ul>"
         "<li><code>robot-montaj.FCStd</code> (Assembly, %d grup, %d eklem, Kollari_oynat simülasyonu) · <code>robot-montaj.step</code> "
         "(gruplar adlarıyla, %d katı) · <code>montaj-analiz.json</code> · <code>eklem-dogrulama.json</code> · <code>gui-kontrol.json</code> · <code>gorsel/</code></li>"
         "<li><code>moduller.py</code> (modül listesi + yükleyiciler + aynalama) → <code>ana_montaj.py</code> (freecadcmd) → <code>montaj_gorsel.py</code> "
         "(freecad.exe; dosyayı GUI'den yeniden kaydeder) → <code>montaj_gui_kontrol.py</code> (freecad.exe) → <code>eklem_dogrulama.py</code> (freecadcmd) → "
         "<code>../carpisma.py</code> → <code>montaj_rapor.py</code> (sistem Python'u)</li></ul>" % (d["grup_sayisi"], len(d["eklemler"]), d["step_kati"]))
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html yazildi", os.path.getsize(os.path.join(HERE, "rapor.html")) // 1024, "kB")
