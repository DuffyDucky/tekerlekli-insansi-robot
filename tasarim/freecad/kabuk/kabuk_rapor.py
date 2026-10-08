# Kabuk modulu raporu (rapor.html, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: kabuk-analiz.json (kabuk_montaj.py), ../carpisma-sonuc.json (carpisma.py), ../montaj/montaj-analiz.json
# (ana_montaj.py), onceki/*.json (kabuk oncesi montaj ve carpisma), ../omuz/regresyon/fark.json,
# ../iskelet/regresyon/fark.json, ../omuz/omuz-analiz.json, ../arayuz.py, gorsel/*.png (kabuk_gorsel.py)
import os, sys, json, base64, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path.insert(0, UST)
import arayuz as A

G = os.path.join(HERE, "gorsel")


def js(*p):
    return json.load(open(os.path.join(*p), encoding="utf-8"))


d = js(HERE, "kabuk-analiz.json")
c = js(UST, "carpisma-sonuc.json")
m = js(UST, "montaj", "montaj-analiz.json")
m0 = js(HERE, "onceki", "montaj-analiz-once.json")
c0 = js(HERE, "onceki", "carpisma-once.json")
ro = js(UST, "omuz", "regresyon", "fark.json")
ri = js(UST, "iskelet", "regresyon", "fark.json")
omz = js(UST, "omuz", "omuz-analiz.json")


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


TR = [(r"\bGovde\b", "Gövde"), (r"\bGogus\b", "Göğüs"), (r"\bbandi\b", "bandı"), (r"\bsag\b", "sağ"), (r"\bkapagi\b", "kapağı"),
      (r"\bEtek on\b", "Etek ön"), (r"\bbraketi\b", "braketi"), (r"\bcivatasi\b", "cıvatası"), (r"\bIsil gomme somun\b", "Isıl gömme somun"),
      (r"\bcekic\b", "çekiç"), (r"\bdayali\b", "dayalı"), (r"\bucu\b", "ucu"), (r"\biceride\b", "içeride"), (r"\bkanal tabani\b", "kanal tabanı"),
      (r"\bsomun alti\b", "somun altı"), (r"\bdeligi\b", "deliği"), (r"\bekseninde\b", "ekseninde"), (r"\bkavramasi\b", "kavraması"),
      (r"\bucundan\b", "ucundan"), (r"\bdis yuzune\b", "dış yüzüne"), (r"\bayni\b", "aynı"), (r"\boturuyor\b", "oturuyor"),
      (r"\bbrakete\b", "brakete"), (r"\bboss'una\b", "boss'una"), (r"\bdudak altina\b", "dudak altına"), (r"\bkati\b", "katı"),
      (r"\bplakasi\b", "plakası"), (r"\bustu\b", "üstü"), (r"\balti\b", "altı"), (r"\bgovdesi\b", "gövdesi"), (r"\bmantari\b", "mantarı"),
      (r"\bboslugu\b", "boşluğu"), (r"\bkonnektor\b", "konnektör"), (r"\baku\b", "akü"), (r"\byatik\b", "yatık"), (r"\bburc\b", "burç"),
      (r"\bkati\b", "katı"), (r"\bpan servosu\b", "pan servosu"), (r"\bkontrplak\b", "kontrplak"), (r"\btasiyici\b", "taşıyıcı"),
      (r"\bduz\b", "düz"), (r"\bbaski\b", "baskı"), (r"\byan yuzu\b", "yan yüzü"), (r"\btablada\b", "tablada"),
      (r"\bdik\b", "dik"), (r"\bters\b", "ters"), (r"\bdis yuzu\b", "dış yüzü"), (r"\bust plakasi\b", "üst plakası"),
      (r"\balt kenari\b", "alt kenarı"), (r"\bomuz duvari\b", "omuz duvarı"), (r"\bcatali\b", "çatalı"), (r"\btupu\b", "tüpü"),
      (r"\bUst kol\b", "Üst kol"), (r"\bRulman kapagi\b", "Rulman kapağı"), (r"\bgobegi\b", "göbeği"), (r"\bkulak\b", "kulak"),
      (r"\bOmuz yuvasi\b", "Omuz yuvası"), (r"\bdiregi\b", "direği"), (r"\brayi\b", "rayı"), (r"\bSase\b", "Şase"),
      (r"\bparca\b", "parça"), (r"\bsayisi\b", "sayısı"), (r"\badlari\b", "adları"), (r"\bsirasi\b", "sırası"), (r"\bbuyuk\b", "büyük"),
      (r"\bsinir kutusu\b", "sınır kutusu"), (r"\bkutlesi\b", "kütlesi"), (r"\bagirlik\b", "ağırlık"), (r"\bgecerli\b", "geçerli"),
      (r"\bcakisma\b", "çakışma"), (r"\bbosluk\b", "boşluk"), (r"\bcakisan\b", "çakışan"), (r"\bGobek\b", "Göbek"), (r"\bdeger\b", "değer"),
      (r"\bkol_gobek\b", "kol × göbek"), (r"\bgobek_govde\b", "göbek × gövde"), (r"\bkol_govde\b", "kol × gövde"),
      (r"\bgruplari\b", "grupları"), (r"\bici\b", "içi"), (r"\bbaglantilar\b", "bağlantılar"), (r"\belemanlar\b", "elemanlar"),
      (r"\bihlali\b", "ihlali"), (r"\bayrilmis\b", "ayrılmış"), (r"\bbolge\b", "bölge"), (r"\btoplam\b", "toplam"),
      (r"\bkabuk\b", "kabuk"), (r"\bkol\b", "kol"), (r"^Baglanti$", "Bağlantı eleman"), (r"^Satin$", "Satın alınan"), (r"^Baski$", "Baskı")]


def tr(s):
    s = str(s)
    for a, b in TR:
        s = re.sub(a, b, s)
    return s


def esc(s):
    s = html.escape(tr(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def img64(ad):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(G, ad), "rb").read()).decode()


def tablo(baslik, satirlar, sinif=""):
    h = ["<table class='%s'><tr>" % sinif + "".join("<th>%s</th>" % esc(b) for b in baslik) + "</tr>"]
    for s in satirlar:
        h.append("<tr>" + "".join("<td>%s</td>" % x for x in s) + "</tr>")
    h.append("</table>")
    return "".join(h)


OK = "<span class='ok'>tamam</span>"
NO = "<span class='no'>HATA</span>"
Y = A.YAZICI
UX, UY, UZ = Y["kullanilabilir"]

# ---------------------------------------------------------------- tarama ozeti (kol - kabuk)
tar = c["tarama"]
poz_say = sum(t["poz_sayisi"] for t in tar.values())
kol_kabuk = {}
for ad, t in tar.items():
    b = t.get("modul_bosluk_eklem_araliginda", {}).get("kabuk")
    kol_kabuk[ad] = b
omuz_ic = set()
for k in ("kol_govde",):
    for pz, hits in omz[k].items():
        if any("referans" not in h[1] for h in hits):
            omuz_ic.add(tuple(int(x) for x in pz.split(",")))
for k in ("kol_gobek",):
    for th, hits in omz[k].items():
        if hits:
            for phi in omz["phis"]:
                omuz_ic.add((phi, int(th)))
for k in ("gobek_govde",):
    for phi, hits in omz[k].items():
        if hits:
            for th in omz["ths"]:
                omuz_ic.add((int(phi), th))
kabuk_poz = {ad: set(tuple(p) for p in t.get("modul_cakisan_poz", {}).get("kabuk", [])) for ad, t in tar.items()}
kabuk_ek = {ad: sorted(v - omuz_ic) for ad, v in kabuk_poz.items()}
eklem_ici = lambda pz: -45 <= pz[0] <= 135 and 0 <= pz[1] <= 120
kabuk_eklem = {ad: [p for p in v if eklem_ici(p)] for ad, v in kabuk_poz.items()}
min_bosluk = min((b[0] for b in kol_kabuk.values() if b), default=None)
min_yer = next((b for b in kol_kabuk.values() if b and b[0] == min_bosluk), None)

baski = d["baski"]
desteksiz_degil = [b for b in baski if not b["desteksiz"]]
sigmayan = [b for b in baski if not b["sigar"]]
bag_ok = sum(1 for b in d["baglanti_kontrol"] if b["tamam"])
vida_ok = sum(1 for v in d["vida_kontrol"] if v["tamam"])
ekr_ok = sum(1 for v in d["ekran_kontrol"] if v["tamam"])
CG = d["agirlik_merkezi"]
kut_baski = sum(b["kutle_g"] for b in baski)
fil = sum(b["filament_g"] for b in baski)
sure = sum(b["sure_saat"] for b in baski)

# ---------------------------------------------------------------- tablolar
yz_satir = [
    ["Model", esc(Y["model"]) + " · " + esc(Y["nozul"])],
    ["Baskı hacmi (ana nozül)", "%s × %s × %s mm" % tuple(sayi(v, 0) for v in Y["hacim_ana"])],
    ["Yardımcı nozül / çift nozül", "%s × %s × %s mm" % tuple(sayi(v, 1).replace(",0", "") for v in Y["hacim_cift"])],
    ["Kullanılabilir (her eksende %s mm pay, tahmini)" % sayi(Y["pay"], 0),
     "<b>%s × %s × %s mm</b> (tek malzeme PETG, ana nozül) · çift nozülde %s × %s × %s" % (
         tuple(sayi(v, 0) for v in Y["kullanilabilir"]) + tuple(sayi(v, 1).replace(",0", "") for v in Y["kullanilabilir_cift"]))],
    ["Hazne / sıcaklık", "aktif ısıtmalı hazne en çok 65 °C · nozül 300 °C · tabla 120 °C"],
    ["Malzeme", "PLA, PETG, ABS, ASA, TPU, PA, PC, PET, PVA ve PLA/PETG destek malzemesi (her iki hotend)"],
    ["Kaynak", "<a href='%s'>%s</a> · %s" % (Y["kaynak"], Y["kaynak"], esc(Y["durum"]))],
]
bs_satir = []
for b in baski:
    o = b["olcu"]
    bs_satir.append([
        "<b>%s</b>" % esc(b["ad"]),
        "%s × %s × %s" % (sayi(o[0], 0), sayi(o[1], 0), sayi(o[2], 0)),
        (OK.replace("tamam", "sığıyor") if b["sigar"] else NO.replace("HATA", "SIĞMIYOR")) +
        ("<br><span class='not'>tabla açısı %d°%s</span>" % (b["tabla_aci"], "" if b["sigar_cift"] else " · çift nozülde sığmaz")),
        esc(b["yon"]),
        ("hayır" if b["desteksiz"] else "<b>evet</b> (%d katman)" % b["destek_sorun_sayi"]) +
        "<br><span class='not'>45° üstü çıkıntı %s %% (%s cm²)</span>" % (sayi(100 * b["cikinti_orani"], 1), sayi(b["cikinti_alan_cm2"], 1)),
        "%s g<br><span class='not'>filament %s g</span>" % (sayi(b["kutle_g"], 0), sayi(b["filament_g"], 0)),
        "%s sa" % sayi(b["sure_saat"], 1),
    ])
bs_satir.append(["<b>Toplam (%d parça)</b>" % len(baski), "", "%d / %d" % (len(baski) - len(sigmayan), len(baski)), "",
                 "%d parça destekli" % len(desteksiz_degil), "<b>%s g</b><br><span class='not'>filament %s g</span>" % (sayi(kut_baski, 0), sayi(fil, 0)),
                 "<b>%s sa</b>" % sayi(sure, 0)])

GB, EB = A.KABUK_GOVDE_BRAKET, A.KABUK_ETEK_BRAKET
bag_satir = [
    ["<b>Gövde kabuğu → gövde direği</b>",
     esc("4 adet 3 mm Al U braket (y = 400 ve 780, sağ ve sol). A ayağı direğin ±X yüzüne dayanır, 2× M6 kanalda çekiç somuna; "
         "C ayağı gövde yan duvarındaki Ø14 damla boss'a (M5 ısıl gömme somun) dayanır."),
     esc("8× M6×16 DIN 912 + 8× M6 pul + 8× M6 çekiç somun · 4× M5×10 DIN 912 + 4× M5 pul + 4× M5 ısıl gömme somun"), "4"],
    ["<b>Taban eteği → şase uzun rayları</b>",
     esc("6 adet 2 mm Al L braket (V3 cover_bracket3): yatay ayak uzun rayın üst yüzünde (z = −175, 0, 175), aşağı bükülü uç eteğin "
         "dik duvarındaki Ø9 boss'a (M3 ısıl gömme somun) dayanır. Etek braketlerinin bölgeleri tabandan kabuğa geçti."),
     esc("6× M6×14 DIN 912 + 6× M6 pul + 6× M6 çekiç somun · 6× M3×8 DIN 912 + 6× M3 ısıl gömme somun"), "6"],
    ["<b>Baskı parçaları arası (bindirme)</b>",
     esc("Bir parçanın iç yarısı (1,5 mm) komşusunun dış yarısının arkasına 12 mm dil olarak uzanır. Dilde Ø8 damla boss + M3 ısıl gömme "
         "somun, komşunun dudağından M3 bombe başlı cıvata. Ust kapak ve etek ust plakasında alın birleşim (plakada dil havada kalırdı)."),
     esc("%d× M3×6 ISO 7380 + %d× M3 ısıl gömme somun" % (len(d["vida_kontrol"]), len(d["vida_kontrol"]))), "%d" % len(d["vida_kontrol"])],
    ["<b>Nextion → göğüs ön duvarı</b>",
     esc("Cam ön yüzü duvar iç yüzüne 0,1 mm; PCB ön yüzü 4 adet Ø8 boss'a dayanır (boss boyu cam + LCD = %s mm). Pencere = aktif alan + "
         "%s mm her kenarda." % (sayi(A.NEXTION["kalinlik"] - A.NEXTION["pcb"][2], 1), sayi(A.NEXTION["pencere_pay"], 1))),
     esc("4× M3×6 DIN 912 + 4× M3 ısıl gömme somun (PCB delikleri Ø3,2, 251,6 × 145,6)"), "4"],
]
kont_satir = []
for b in d["baglanti_kontrol"]:
    det = []
    for ad, deger, ok in b["kontroller"]:
        if "civata ucu yuzden" in ad or "kavramasi" in ad or "kalan et" in ad:
            det.append(ad)
    kont_satir.append([esc(b["ad"]), esc(b["parca"]), "%d / %d" % (sum(1 for k in b["kontroller"] if k[2]), len(b["kontroller"])),
                       esc("; ".join(sorted(set(det)))), OK if b["tamam"] else NO])
vida_ozet = {}
for v in d["vida_kontrol"]:
    key = v["etiket"]
    vida_ozet.setdefault(key, []).append(v)
vk_satir = []
for k, vs in vida_ozet.items():
    vk_satir.append([esc(k), "%d" % len(vs), esc(", ".join(sorted(set(v["ic"] for v in vs)))), esc(", ".join(sorted(set(v["dis"] for v in vs)))),
                     sayi(min(v["kavrama"] for v in vs), 1) + " mm", sayi(min(v["dudak"] for v in vs), 2) + " mm",
                     OK if all(v["tamam"] for v in vs) else NO])

car_satir = []
for ad, t in tar.items():
    b = kol_kabuk[ad]
    car_satir.append([esc(ad), "%d" % t["poz_sayisi"], "%d" % len(kabuk_poz[ad]), "<b>%d</b>" % len(kabuk_eklem[ad]),
                      "%d" % len(kabuk_ek[ad]),
                      ("<b>%s mm</b><br><span class='not'>%s ↔ %s, öne %s° / yana %s°</span>" % (
                          sayi(b[0], 1), esc(b[1][1]), esc(b[1][2]), b[1][0][0], b[1][0][1])) if b else "–"])

bol_satir = [[esc(s), esc(a), sayi(dd, 1) + " mm", esc(p)] for s, a, dd, p in d["bolge"]["en_yakin"]]

# kutle ve AM degisimi
mm_once, mm_sonra = m0["kutle_g"], m["kutle_g"]
am0, am1 = m0["agirlik_merkezi"], m["agirlik_merkezi"]
km_satir = [
    ["Ana montaj (FreeCAD dosyasından)", "%d parça · %s g" % (m0["parca_sayisi"], sayi(mm_once, 1)),
     "%d parça · %s g" % (m["parca_sayisi"], sayi(mm_sonra, 1)), "+%s g" % sayi(mm_sonra - mm_once, 1)],
    ["Ağırlık merkezi (x; y; z) mm", "(%s; %s; %s)" % tuple(sayi(v, 1) for v in am0), "(%s; %s; %s)" % tuple(sayi(v, 1) for v in am1),
     "y %s mm" % sayi(am1[1] - am0[1], 1)],
    ["Kabuk modülü", "–", "%s g · AM (%s; %s; %s)" % ((sayi(d["kutle_g"], 1),) + tuple(sayi(v, 1) for v in CG)), ""],
    ["carpisma.py toplamı", "%s g" % sayi(c0["kutle_toplam_g"], 1), "%s g" % sayi(c["kutle_toplam_g"], 1),
     "AM y %s → %s" % (sayi(c0["agirlik_merkezi"][1], 1), sayi(c["agirlik_merkezi"][1], 1))],
]
kg_satir = [[esc(k), sayi(v, 0) + " g"] for k, v in sorted(d["kutle_grup"].items(), key=lambda x: -x[1])]


def reg_tablo(r):
    out = []
    for s in r["satirlar"]:
        f = "–" if s["fark"] is None else ("0" if s["fark"] == 0 else "%.2e" % s["fark"])
        out.append([esc(s["olcut"]), esc(s["once"]), esc(s["sonra"]), f, "<span class='ok'>aynı</span>" if s["ayni"] else NO.replace("HATA", "farklı")])
    return out


KARAR = [
    "**Yazıcı Bambu Lab X2D (doğrulandı):** üretici teknik sayfasında ana nozül 256 × 256 × 260 mm, yardımcı ve çift nozül 235,5 × 256 × 256 mm, "
    "aktif ısıtmalı hazne 65 °C. Parçalar tek malzeme PETG ile ana nozülde basılacak; her eksende 10 mm pay (tahmini) → 246 × 246 × 250. "
    "Eski 250³ / PRINT_MAX 230 varsayımı kullanılmadı. Hiçbir parça destek istemediği için ikinci nozül (destek malzemesi) gerekmedi.",
    "**Duvar 3,0 mm (V3 2,5):** bindirmede her yarı 1,5 mm = 0,42 mm çizgiyle 3–4 çevre; 2,5 mm'de 1,25 mm'lik dudak cıvata başı altında ezilir. "
    "Eğilme rijitliği t³ ile %73 artar, kütle %20 artar. Eğik yüzlerde yatay ofset kullanıldı: normal kalınlık göğüs çıkıntısında (36°) 2,4 mm'ye iner.",
    "**Kesit V3 elips → yuvarlatılmış dikdörtgen (V3 ölçüleriyle):** omuz arayüzü x = 147…152 düz duvar ve Ø84 delik ister; elips kesitte "
    "bu yalnız tek çizgide düz. Köşe yarıçapı altta 40, göğüs ve omuzda 16 mm. Omuz bölgesinde yan duvar 5 mm (x 147…152, R58 ped), omuz "
    "modülündeki referans duvarla birebir.",
    "**Eğik göğüs, çıkıntılı çerçeve kutusu yerine:** V3'teki ekran kutusunun alt ve üst duvarları hangi yönde basılsa biri tavan kalıyordu. "
    "Burada göğüs ön duvarı ekran düzleminde 15° eğik (cam düzlemi V3 ile aynı: merkez y 820, z 95); ekranın altında 36° eğimli bir çıkıntı "
    "gövdeye iner. Desteksiz basılıyor, ekran duvarın arkasına oturuyor.",
    "**Nextion NX1060P101_011 yuvası datasheet'ten:** PCB 258 × 152 × 1,6, cam 236,8 × 144,8, kalınlık 9,8, aktif alan 222,72 × 125,28, "
    "delikler Ø3,2 / 251,6 × 145,6, 535 g. Pencere = aktif alan + 1,5 mm (tahmini). Konnektör (4 pin XH2.54) çizimdeki alt kenar ölçüsünden "
    "−X ucunda kabul edildi; arkasında 30 mm kablo boşluğu ayrılmış bölge (`Nextion konnektor ve kablo boslugu`).",
    "**Bölme ve dikiş yerleri:** gövde 4 yatay bant × sağ/sol + arka kapak (9), etek 3 bant × sağ/sol (6) = 15 baskı parçası. Yatay dikişler "
    "y = 476,5 (alt gövde), 690 (göğüs çıkıntısının kırılma çizgisi), 883 (ekran penceresinin üst kenarı: pencere üstte köprü kalmasın diye). "
    "Dikey dikiş x = 0 simetri çizgisi; etekte z = ±87,5 yan yüzlerde. Hepsi düz yüzlerde.",
    "**Baskı yönleri:** gövde bantları dik (alt kenar tablada), omuz bandı yan yüzü (omuz duvarı) tablada, arka kapak dış yüzü tablada, "
    "etek ters (üst plaka tablada). Boss'lar baskı yönünde 45° damla şekilli; kontrol katman katman (1 mm, 45° kuralı, 2 mm'den dar ve "
    "15 mm'den kısa açıklık köprü sayıldı).",
    "**İskelete bağlantı:** gövde 4 U braket ile direğe (direk yan kanalları y 400–450 ve 780–830 boş), etek 6 L braket ile uzun raylara "
    "(V3'teki 4 yerine 6: her etek parçası bir brakete oturuyor). Gövde etek plakasından 1 mm yukarıda (y 263): yük etekten değil direkten.",
    "**Etek köşe yarıçapı 15 (V3 25) ve derinlik 525 (V3 520):** V3 ölçüsünde teker köşesinde 7 mm, önde-arkada 10 mm kalıyordu. Şimdi "
    "tekerin her yönünde 12 mm.",
    "**Üst kapakta omuz yuvası erişim delikleri (Ø14, x = ±86):** ilk taramada omuz yuvasının üst M6 cıvatasının başı (y 981,6…987,6) "
    "üst kapağa giriyordu (ev pozunda 214 mm³). Kapakta delik açıldı; cıvataya anahtar da buradan girer.",
    "**Arka servis kapağı (160 × 190, 7 cıvata):** üst kenarı y = 690 dikişine alın dayanır, üç kenarında gövdenin iç yarısı 12 mm'lik "
    "kenet (ledge) bırakır. Açık bırakıldığında direk, alt braketler ve kablolar görülür.",
]
ACIK = [
    "**Kol yana 0°'nin altına inerse kabuğa çarpar:** eklem aralığında (öne −45…135°, yana 0…120°) kabuk çakışması 0. Tarama aralığının dışındaki "
    "yana −5…−20° pozlarında kol kabuğa çarpıyor (sağ %d, sol %d poz). Bunların %d'i yana −5°'de ve omuzun kendi parçalarına çarpmadığı pozlar "
    "(kabuk kaynaklı); −10° ve altında omuz kendi rulman kapağına da çarpıyor. Servo sınırı yazılımda 0°'de tutulmalı." % (
        len(kabuk_poz.get("omuz_sag", [])), len(kabuk_poz.get("omuz_sol", [])), len(kabuk_ek.get("omuz_sag", []))),
    "**Nextion ölçüleri sahada doğrulanmalı:** konnektör konumu ve arka bileşen yüksekliği (6 mm) çizimden yorum; ekran gelince kumpasla "
    "ölçülüp `arayuz.NEXTION` güncellenmeli. Dokunmatik tipi (C/R) kutudan doğrulanacak.",
    "**Kütle, filament ve süre tahmini:** PETG 1,27 g/cm³ × %90 doluluk (3 mm duvar = 2 × 3 çevre + %15 dolgu), filament +%5 atık, süre 10 mm³/s "
    "ortalama debiyle. Gerçek değerler Bambu Studio dilimlemesinden alınmalı.",
    "**Isıl gömme somun ölçüleri tahmini** (`arayuz.INSERT`: M3 Ø4,6 × 5,7, M5 Ø7 × 7). Alınacak ürünün ölçüsüyle boss ve delik güncellenmeli.",
    "**Bindirme cıvataları dışarıdan görünür** (bombe baş, 1,65 mm çıkıntı). Ekran üstündeki 883 dikişinde önde cıvata yok (yer Nextion "
    "boss'larında); o dikiş arkadan 4 cıvata ve iki yandaki dille tutuluyor.",
    "**Braket ayrıntıları tahmini:** Al sac kalınlığı (3 ve 2 mm), büküm yarıçapı modelde yok, M5 ve M3 kavrama boyları ısıl gömme somun boyuna göre.",
    "**V3'teki hoparlör ızgarası** (göğüs altında, CHEST3_SPK) bu modülde yok; hoparlör yeri seçilince ön duvara eklenir.",
    "**Kafa modülü** boyun açıklığına (üst kapakta R62) ve `Kafa pan servosu ve boyun` bölgesine uymalı (kabuk o bölgeye 5 mm). "
    "**Taban modülü** sonar (3 adet) ve acil stop için yeni ayrılmış bölgelere uymalı; etek braketleri artık kabuk bölgesi.",
    "**Montaj sırası (öneri):** etek parçaları birbirine cıvatalanır, raylardaki braketlere oturtulur; gövde braketleri direğe takılır; gövde "
    "sağ yarısı (bantlar birbirine bağlı) braketlere, sonra sol yarı; Nextion göğüs boss'larına önceden takılır; son olarak arka kapak. "
    "Sol yarının M5 cıvatalarına arka kapak açıklığından ulaşılır (tahmini, denenmeli).",
]

# ---------------------------------------------------------------- HTML
H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kabuk Modülü V3</title><style>
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
.not{color:var(--mut);font-size:13px}a{color:var(--acc2)}
</style></head><body><main>""")
H.append("<h1>Kabuk modülü (V3): gövde kabuğu + taban eteği</h1>")
H.append("<div class='sub'>FreeCAD 1.1 · <code>kabuk_montaj.py</code> · %d parça (%d baskı) · PETG %s mm duvar · göğüste Nextion NX1060P101_011 · "
         "ölçüler <code>arayuz.py</code>'den (robot_cad V3 torso_shell3 / base_cover3) · yazıcı %s</div>" % (
             d["parca_sayisi"], d["baski_sayisi"], sayi(A.KABUK_T, 1), esc(Y["model"])))
kpi = [
    ("%d / %d" % (d["baski_sayisi"], d["parca_sayisi"]), "baskı parçası / toplam parça · hepsi geçerli, tek katı" if not d["gecersiz"] and not d["coklu_kati"] else "GEÇERSİZ PARÇA VAR"),
    ("%d" % len(d["cakisma"]), "kabuk içi çakışma (%d çift sınandı)" % d["cakisma_cift_sayisi"]),
    ("%d" % len(d["iskelet_cakisma"]), "kabuk ↔ iskelet çakışma · ayrılmış bölge ihlali %d" % len(d["bolge"]["ihlal"])),
    ("%d" % sum(len(v) for v in kabuk_eklem.values()), "kol ↔ kabuk çakışma, eklem aralığında (iki omuz, %d poz)" % poz_say),
    ("%s mm" % (sayi(min_bosluk, 1) if min_bosluk is not None else "–"), "en küçük kol-kabuk boşluğu (eklem aralığında)"),
    ("%d / %d" % (len(baski) - len(sigmayan), len(baski)), "X2D'ye sığan parça (246 × 246 × 250) · desteksiz basılamayan %d" % len(desteksiz_degil)),
    ("%d / %d" % (bag_ok, len(d["baglanti_kontrol"])), "iskelete bağlantı kontrolü · bindirme %d/%d, ekran %d/%d" % (vida_ok, len(d["vida_kontrol"]), ekr_ok, len(d["ekran_kontrol"]))),
    ("%s kg" % sayi(d["kutle_g"] / 1000, 2), "kabuk kütlesi (baskı %s kg, Nextion 0,54) · AM yerden %s mm" % (sayi(kut_baski / 1000, 2), sayi(CG[1], 0))),
    ("aynı" if ro["hepsi_ayni"] and ri["hepsi_ayni"] else "FARK", "omuz ve iskelet regresyonu (geometri değişmedi)"),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")

H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (("kabuk-izometrik.png", "İzometrik: kabuk, iskelet, iki omuz", ""), ("kabuk-on.png", "Önden", ""),
                   ("kabuk-yan.png", "Yandan (+X)", ""),
                   ("kabuk-arka-kapak-acik.png", "Arkadan: servis kapağı açık (dışarı çekilmiş); direk ve alt braketler görünür", ""),
                   ("kabuk-kesit.png", "Kesit x = 0: gövde, eğik göğüs, Nextion, direk, etek", ""),
                   ("kabuk-kesit-gogus.png", "Kesit yakın: göğüs duvarı, cam, PCB, boss, dikişler", ""),
                   ("kabuk-patlatilmis.png", "Patlatılmış: her baskı parçası ayrı renk", "wide"),
                   ("kabuk-patlatilmis-on.png", "Patlatılmış, önden", ""),
                   ("kabuk-nextion-on.png", "Nextion yuvası önden: pencere = aktif alan + 1,5 mm", ""),
                   ("kabuk-nextion-ic.png", "Nextion yuvası içten (göğüs parçalarının ön yarısı, arkadan bakış): 4 boss, M3 cıvata, konnektör", ""),
                   ("kabuk-omuz-duvari.png", "Omuz bölgesi: 5 mm düz yan duvar, Ø84 delik (kabuk yarı saydam)", ""),
                   ("kabuk-baglanti-govde.png", "Gövde braketi (y 780): direğe 2× M6 + çekiç somun, gövde boss'una M5 (kabuk yarı saydam)", ""),
                   ("kabuk-baglanti-etek.png", "Etek braketi: uzun ray üst kanalına M6, etek boss'una M3 (kabuk yarı saydam)", "")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div>")

H.append("<h2>3D yazıcı</h2><div class='tw'>" + tablo(["", ""], yz_satir) + "</div>")
H.append("<h2>Baskı parçaları</h2><div class='tw'>")
H.append(tablo(["Parça", "Ölçü (baskı yönünde, mm)", "Tablaya sığıyor mu", "Baskı yönü", "Destek gerekir mi / çıkıntı", "Kütle (tahmini)", "Süre (tahmini)"], bs_satir))
H.append("</div><p class='not'>Ölçü: tabla düzleminde en iyi açıyla (0…90°) yerleşimin genişlik × derinliği ve baskı yüksekliği. Destek kontrolü: parça "
         "baskı yönüne çevrilip 1 mm katmanlara kesildi; her katmanın, bir alttaki katmanın 1 mm (45°) büyütülmüş izinin dışında kalan kısmı "
         "desteksiz sayıldı. 2 mm'den dar şeritler (bindirme basamakları) ve 15 mm'den kısa açıklıklar (Ø17 sonar delikleri) köprülenebilir "
         "kabul edildi (tahmini). Çıkıntı oranı: tabla yüzeyi dışında, normali aşağıya 45°'den dik bakan yüzey alanı / toplam yüzey.</p>")

H.append("<h2>Bağlantılar</h2><div class='tw'>")
H.append(tablo(["Bağlantı", "Nasıl oturuyor", "Bağlantı elemanı (toplam)", "Adet"], bag_satir))
H.append("</div><h3>İskelete bağlantı kontrolleri (her braket ayrı)</h3><div class='tw'>")
H.append(tablo(["Braket", "Kabuk parçası", "Kontrol", "Ölçü", "Sonuç"], kont_satir))
H.append("</div><p class='not'>Her braket: braket profile ve kabuk boss'una dayalı (0,00 mm), çekiç somun dudak altına dayalı, M6 cıvata ucu "
         "somunu geçip kanal tabanına değmiyor (%s ≤ uç < %s mm), cıvata ve somun aynı eksende, pul brakete dayalı; kabuk tarafında cıvata "
         "kavraması ≥ cıvata çapı ve ≤ ısıl gömme somun deliği, cıvata ucundan dış yüzeye ≥ 1 mm et, ısıl gömme somun boss'ta.</p>" % (
             sayi(A.LIP + A.CEKIC_SOMUN["T"], 1), sayi(A.KANAL_TABAN, 1)))
H.append("<h3>Bindirme cıvataları</h3><div class='tw'>")
H.append(tablo(["Dikiş", "Adet", "Isıl gömme somun (dil)", "Cıvata (dudak)", "En kısa kavrama", "Dudak", "Sonuç"], vk_satir))
H.append("</div><p class='not'>Cıvata başı dudağa dayalı, ısıl gömme somun boss'ta oturuyor, kavrama 3…5,7 mm, dudak ≥ 1,2 mm. Ekran: 4 cıvata, PCB "
         "boss'lara dayalı (%d/%d), kavrama %s mm.</p>" % (ekr_ok, len(d["ekran_kontrol"]), sayi(d["ekran_kontrol"][0]["kavrama"], 1) if d["ekran_kontrol"] else "–"))

H.append("<h2>Çakışma sonuçları</h2><ul>")
H.append("<li>Kabuk içi: <b>%d çakışma</b> (%d parça, %d sınır kutusu kesişen çift gerçek kesişimle sınandı, eşik %s mm³).</li>" % (
    len(d["cakisma"]), d["parca_sayisi"], d["cakisma_cift_sayisi"], sayi(d["tolerans_mm3"], 1)))
H.append("<li>Kabuk ↔ iskelet: <b>%d çakışma</b> (%d çift). Gövde iç yüzü ile direk arasında en az %s mm.</li>" % (
    len(d["iskelet_cakisma"]), d["iskelet_cift_sayisi"], sayi(d["bosluk"]["direk_govde_mm"], 1)))
H.append("<li>Ayrılmış bölgeler: %d bölge, <b>%d ihlal</b>. Teker ↔ etek en az %s mm.</li>" % (
    d["bolge"]["kontrol_edilen"], len(d["bolge"]["ihlal"]), sayi(d["bosluk"]["teker_etek_mm"], 1)))
H.append("<li>Modüller arası (<code>carpisma.py</code>, ev pozu): <b>%d çakışma</b> (%d sınır kutusu kesişen çift).</li></ul>" % (
    len(c["ev_pozu_cakisma"]), c["ev_pozu_kesisen_cift"]))
H.append("<div class='tw'>" + tablo(["Omuz", "Taranan poz", "Kabuğa çarpan poz (tümü)", "Eklem aralığında", "Kabuk kaynaklı (omuz kendine çarpmıyor)",
                                     "En küçük kol-kabuk boşluğu (eklem aralığında)"], car_satir) + "</div>")
H.append("<p class='not'>Tarama: öne-arka −60…180° (10°), yana −20…150° (5°), her omuz %d poz. Eklem aralığı öne −45…135°, yana 0…120°. "
         "Kabuğa çarpan pozların hepsi yana 0°'nin altında: %s. Kabuk kaynaklı olanlar (omuzun kendi parçaları serbest) yalnız yana −5°: "
         "orada kolun iç kenarı x = 152 düz duvarına giriyor (omuz modülündeki referans duvarla aynı sonuç). −10° ve altında omuz kendi rulman kapağına da çarpıyor.</p>" % (
             list(tar.values())[0]["poz_sayisi"],
             ", ".join(sorted(set("yana %d°" % p[1] for v in kabuk_poz.values() for p in v)))))
H.append("<h3>Kabuğun ayrılmış bölgelere en yakın noktası</h3><div class='tw'>" + tablo(["Sahip", "Bölge", "En küçük boşluk", "Kabuk parçası"], bol_satir) + "</div>")

H.append("<h2>Kütle ve ağırlık merkezi</h2><div class='grid'><div>")
H.append(tablo(["", "Kabuktan önce", "Güncel ana montaj (%s)" % ", ".join(x["ad"] for x in m["moduller"]), "Değişim"], km_satir))
H.append("</div><div>" + tablo(["Grup", "Kütle"], kg_satir, "sayi") + "</div></div>")
H.append("<p class='not'>Ana montaj: %s. Kütle karşılaştırması %s g fark (analiz JSON'ları 0,1 g yuvarlı).</p>" % (
    esc(m["karsilastirma"]["parca"]["formul"]), sayi(m["karsilastirma"]["kutle"]["fark_analiz"], 2)))

H.append("<h2>Regresyon: omuz ve iskelet değişmedi</h2><h3>Omuz (<code>omuz/omuz_regresyon.py</code>)</h3><div class='tw'>")
H.append(tablo(["Ölçüt", "Önce", "Sonra", "En büyük fark", "Sonuç"], reg_tablo(ro)) + "</div>")
H.append("<h3>İskelet (<code>iskelet/iskelet_regresyon.py</code>, yeni)</h3><div class='tw'>")
H.append(tablo(["Ölçüt", "Önce", "Sonra", "En büyük fark", "Sonuç"], reg_tablo(ri)) + "</div>")
H.append("<p class='not'>“Önce”: kabuk çalışmasından önce, değişmemiş <code>arayuz.py</code> ile alınan özet. “Sonra”: kabuk bölümleri eklendikten "
         "sonra. Omuz taramasındaki çakışan pozlar (yana −20…−5°) omuzun kendi referans duvarına ve parçalarınadır, öncekiyle aynı.</p>")

H.append("<h2>Kararlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in KARAR) + "</ul>")
H.append("<h2>Açık işler ve varsayımlar</h2><ul>" + "".join("<li>%s</li>" % esc(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>kabuk-montaj.FCStd</code> · <code>kabuk-montaj.step</code> (geri okuma %d katı) · <code>kabuk-bom.csv</code> · "
         "<code>kabuk-analiz.json</code> · <code>gorsel/</code></li>"
         "<li><code>kabuk_lib.py</code> (kesit, zarf, damla boss, ISO 7380) · <code>kabuk_parcalar.py</code> · <code>kabuk_montaj.py</code> "
         "(kontroller, baskı analizi, kayıt) · <code>kabuk_gorsel.py</code> · <code>kabuk_rapor.py</code></li>"
         "<li>Ortak: <code>../arayuz.py</code> (YAZICI, KABUK_*, GOVDE_KESIT, ETEK_KESIT, NEXTION, yeni bölgeler) · <code>../carpisma.py</code> · "
         "<code>../montaj/moduller.py</code></li></ul>" % d["step_kati"])
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html yazildi", os.path.getsize(os.path.join(HERE, "rapor.html")) // 1024, "kB")
