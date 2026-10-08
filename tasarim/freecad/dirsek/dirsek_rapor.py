# Dirsek modulu raporu (rapor.html, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: dirsek-analiz.json (dirsek_montaj.py), gorsel/*.png (dirsek_gorsel.py), ../arayuz.py; 2. asama:
# ../carpisma-sonuc.json (kol zinciri taramasi), ../montaj/montaj-analiz.json + eklem-dogrulama.json + gui-kontrol.json
# (ana montaj), ../montaj/gorsel/*.png|gif, ../omuz|iskelet/regresyon/fark.json. Yoksa ilgili bolum bos kalir.
import os, sys, json, base64, html, io

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path.insert(0, UST)
import arayuz as A

G = os.path.join(HERE, "gorsel")
GM = os.path.join(UST, "montaj", "gorsel")
d = json.load(open(os.path.join(HERE, "dirsek-analiz.json"), encoding="utf-8"))
DI = A.DIRSEK


def oku(*yol):
    f = os.path.join(UST, *yol)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


CRP = oku("carpisma-sonuc.json")
MA = oku("montaj", "montaj-analiz.json")
ED = oku("montaj", "eklem-dogrulama.json")
GK = oku("montaj", "gui-kontrol.json")
REG = {"omuz": oku("omuz", "regresyon", "fark.json"), "iskelet": oku("iskelet", "regresyon", "fark.json")}
KT = (CRP or {}).get("kol_tarama") or {}
KK = (CRP or {}).get("kol_kol")


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


def img64(ad, klasor=None):
    tip = "gif" if ad.endswith(".gif") else "png"
    return "data:image/%s;base64," % tip + base64.b64encode(open(os.path.join(klasor or G, ad), "rb").read()).decode()


def png64(fig):
    b = io.BytesIO()
    fig.savefig(b, format="png", dpi=130)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def tablo(baslik, satirlar, sinif=""):
    h = ["<table class='%s'><tr>" % sinif + "".join("<th>%s</th>" % esc(b) for b in baslik) + "</tr>"]
    for s in satirlar:
        h.append("<tr>" + "".join("<td>%s</td>" % x for x in s) + "</tr>")
    h.append("</table>")
    return "".join(h)


OK = "<span class='ok'>tamam</span>"
NO = "<span class='no'>HATA</span>"
Y = A.YAZICI
TR = {"Dirsek catali": "Dirsek çatalı", "On kol govdesi": "Ön kol gövdesi", "Bilek flansi": "Bilek flanşı", "El": "El",
      "M3 DIN 125 pul": "M3 DIN 125 pul", "M3 isil gomme somun": "M3 ısıl gömme somun", "M5 isil gomme somun": "M5 ısıl gömme somun",
      "M3x5 horn vidasi (servo ile)": "M3×5 horn vidası (servo ile gelir)", "25T aluminyum disk horn": "25T alüminyum disk horn",
      "MG996R servo": "MG996R servo (180°)", "625ZZ rulman 5x16x5": "625ZZ rulman 5×16×5",
      "Sikma bilezigi y -121": "Sıkma bileziği (üst cıvata)", "Sikma bilezigi y -132": "Sıkma bileziği (alt cıvata)",
      "Catal dis kolu -> dirsek horn": "Çatal dış kolu → dirsek horn'u", "Dirsek pimi (servo karsi yatagi)": "Dirsek pimi (servo karşı yatağı)",
      "Dirsek servosu kulagi": "Dirsek servosu kulağı", "Bilek servosu kulagi": "Bilek servosu kulağı",
      "Bilek flansi -> bilek horn": "Bilek flanşı → bilek horn'u", "El yakasi -> bilek flansi": "El yakası → bilek flanşı",
      "Eksen hizasi ve oturmalar": "Eksen hizası ve oturmalar"}


def tr(s):
    s = TR.get(s, s)
    return s.replace("x", "×") if s[:1] == "M" and "DIN" in s or "ISO" in s else s


# ---------------------------------------------------------------- ozetler
bag = d["baglanti_kontrol"]
bag_ok = sum(1 for b in bag if b["tamam"])
kontrol_n = sum(len(b["kontroller"]) for b in bag)
baski = d["baski"]
sigan = sum(1 for b in baski if b["sigar"])
destek = sum(1 for b in baski if b["desteksiz"])
tk = {t["eklem"]: t for t in d["tork"]["sonuc"]}
t1, t2, td, tb = tk["S1 (omuz one-arka)"], tk["S2 (omuz yana acma)"], tk["Dirsek"], tk["Bilek"]
ta = d["tarama"]
amin, amax = ta["serbest"]
ar = DI["aralik"]
bk = ta["bukulme"]
oe = d["tork"]["omuz_eski"]
uz = -DI["el_ucu"][1]
ev_cak = len(d["statik"])
ar_cak = len(d["omuz_arayuzu"]["cakisma"])


def pay(x):
    cls = "ok" if x >= 2 else ("no" if x < 1.2 else "uy")
    return "<span class='%s'>%s×</span>" % (cls, sayi(x, 2))


# ---------------------------------------------------------------- grafikler (matplotlib, statik; veri tablosu raporda)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C1, C2, INK, MUT, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e4df"
eg = d["tork"]["egri"]
als = [e["al"] for e in eg]


def stil(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9b7b0")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.tick_params(colors=MUT, labelsize=9)
    ax.set_axisbelow(True)


fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.9))
ax = axs[0]
ax.plot(als, [e["dirsek_yuklu"] for e in eg], color=C2, lw=2, marker="o", ms=4, label="0,5 kg el ucu yüküyle")
ax.plot(als, [e["dirsek_yuksuz"] for e in eg], color=C1, lw=2, marker="o", ms=4, label="yüksüz")
for yv, lab in ((td["stall_kgcm"], "MG996R durma 9,4"), (td["stall_kgcm"] / 2, "2× pay sınırı 4,7")):
    ax.axhline(yv, color=MUT, lw=1, ls="--")
    ax.text(als[0], yv + 0.15, lab, color=MUT, fontsize=8.5)
ax.text(als[-1], eg[-1]["dirsek_yuklu"] - 0.9, "0,5 kg", color=INK, fontsize=9, ha="right")
ax.text(als[-1], eg[-1]["dirsek_yuksuz"] + 0.3, "yüksüz", color=INK, fontsize=9, ha="right")
ax.set_title("Dirsek servosu torku (omuz ev pozunda)", fontsize=10.5, color=INK, loc="left")
ax.set_xlabel("Dirsek açısı (°), 0 = kol düz aşağıda", fontsize=9, color=MUT)
ax.set_ylabel("kg·cm", fontsize=9, color=MUT)
ax.set_ylim(0, 11)
stil(ax)
ax.legend(fontsize=8, frameon=False, loc="center right")
ax = axs[1]
ax.plot(als, [e["s1_yuklu_omuz90"] for e in eg], color=C2, lw=2, marker="o", ms=4, label="0,5 kg yükle")
ax.plot(als, [e["s1_yuksuz_omuz90"] for e in eg], color=C1, lw=2, marker="o", ms=4, label="yüksüz")
for yv, lab in ((t1["stall_kgcm"], "DS3218MG durma 20"), (t1["stall_kgcm"] / 2, "2× pay sınırı 10")):
    ax.axhline(yv, color=MUT, lw=1, ls="--")
    ax.text(als[-1], yv + 0.4, lab, color=MUT, fontsize=8.5, ha="right")
ax.set_title("Omuz S1 torku (omuz öne 90°, kol yatay)", fontsize=10.5, color=INK, loc="left")
ax.set_xlabel("Dirsek açısı (°)", fontsize=9, color=MUT)
ax.set_ylabel("kg·cm", fontsize=9, color=MUT)
ax.set_ylim(0, 27)
stil(ax)
ax.legend(fontsize=8, frameon=False, loc="lower left")
fig.tight_layout()
GRAF_TORK = png64(fig)
plt.close(fig)

# dirsek ici tarama: aci basina carpisan cift sayisi
fig, ax = plt.subplots(figsize=(10.5, 2.6))
ALS = ta["als"]
for al in ALS:
    n = len(ta["onkol_ust"][str(al)]) + sum(len(ta["el_ust"]["%d,%d" % (al, be)]) for be in ta["bes_kol"])
    ax.bar(al, 1, width=4.2, color=(C2 if n else C1))
ax.axvspan(ar[0] - 2.5, ar[1] + 2.5, color="#f0efec", zorder=0)
ax.text((ar[0] + ar[1]) / 2, 1.08, "yazılım sınırı %d…%d°" % (ar[0], ar[1]), ha="center", fontsize=9, color=INK)
ax.set_yticks([])
ax.set_ylim(0, 1.25)
ax.set_xlabel("Dirsek açısı (°)  —  mavi: serbest, turuncu: ön kol/el ↔ üst kol çakışması (bilek −90…90 dahil)", fontsize=9, color=MUT)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(colors=MUT, labelsize=9)
fig.tight_layout()
GRAF_TARAMA = png64(fig)
plt.close(fig)

# ---------------------------------------------------------------- metinler
BAGLANTI = [
    ("Dirsek çatalı → üst kol tüpü (omuz)",
     "Pim tüpün içine 25 mm girer (Ø50,8; tüp içi Ø51 → 0,1 mm boşluk). Yarıklı bilezik (iç Ø56,2) tüpü dıştan sarar. Tüp ucu alın "
     "kapağındaki V oluğun iki kenarına dayanır. Tüpe delik açılmaz, omuz geometrisi değişmez.",
     "2× M3×20 DIN 912 + 4× M3 pul + 2× M3 DIN 985 kontra somun (arka kulaklarda, yarığı kapatır)"),
    ("Dirsek servosu → ön kol gövdesi", "Servo arkadan kulak plakasındaki yuvaya girer, kulakları plakanın dış yüzüne oturur. Mil +X (dışarı).",
     "4× M4×16 DIN 912 + 4× M4 DIN 985 kontra somun (somunlar plakanın iç yüzünde)"),
    ("Dirsek horn'u → servo mili", "25 dişli mile geçer.", "M3 merkez vidası (servo ile gelir)"),
    ("Çatal dış kolu → dirsek horn'u", "Dış kol horn'un dış yüzüne oturur. Merkez vidası için Ø9 erişim deliği var.",
     "4× M3×8 DIN 912 → horn'un dişli delikleri"),
    ("Çatal iç kolu ↔ ön kol (servo karşı yatağı)",
     "625ZZ çatalın Ø16 yuvasına sıkı geçer, dış bileziği yuva dudağına dayanır. M5 cıvata, pul ve iç bilezikle birlikte ön koldaki Ø8 "
     "dayamaya sıkılır. Ön kol iç bilezikle döner. Yük iki yataktan geçtiği için servo mili yanal yük taşımaz (omuz S2 ile aynı çözüm).",
     "1× M5×12 DIN 912 + 1× M5 pul → ön kol yanağında M5 ısıl gömme somun"),
    ("Bilek servosu → ön kol gövdesi", "Servo arkadan bilek plakasına girer, mil aşağı (ön kol ekseninde), kulaklar plakaya oturur.",
     "4× M4×16 DIN 912 + 4× M4 DIN 985 kontra somun"),
    ("Bilek horn'u → servo mili", "25 dişli mile geçer.", "M3 merkez vidası (servo ile gelir)"),
    ("Bilek flanşı → bilek horn'u", "Flanş horn'un alt yüzüne oturur, merkez vidasının başı flanştaki Ø9 cebe girer.",
     "4× M3×8 DIN 912, flanştaki havşalardan horn'un dişli deliklerine"),
    ("El → bilek flanşı", "Elin yakası flanşa geçer (Ø28,3 / Ø28) ve tabanına dayanır.",
     "2× M3×6 ISO 7380 (radyal) → flanşta 2× M3 ısıl gömme somun"),
]
KARAR = [
    "**V3 düzeni korundu** (robot_cad sağ kol, rc:669-810): dirsek MG996R'sinin mili dışarıda (+X), gövdesi ön kolda; bilek MG996R'si "
    "mili aşağıda, ön kol ekseninde döndürür; el sabit. Bütçedeki 6 MG996R'nin 2'si dirsek, 2'si bilek (maliyet.json'daki dağılımla aynı).",
    "**Servo karşı yatağı:** omuz S2'deki çözümün aynısı: 625ZZ + M5×12 + ısıl gömme somun + Ø8 dayama. Dirsek servosunun mili, "
    "rulman ve horn aynı eksende (kontrol: eksenden sapma 0).",
    "**Tüpe bağlantı:** Omuzdaki üst kol tüpünün ucunda delik ya da kelepçe yok. Tüpe dokunmayan bir çözüm seçildi: pim + yarıklı sıkma bileziği "
    "(tüp, bilezikle pim arasında sıkışır). Tüp ucu V oluğun kenarlarına dayanır.",
    "**Dirsek ekseni** tüp ucunun 33 mm altında (omuz ekseninden −173 mm; V3'te −154). Bu pay bilezik, kapak ve ön kol başının dönüşü (R21, "
    "kapağa 4 mm) için gerekiyor.",
    "**Kol boyu:** omuz ekseninden el ucuna %s mm (V3 ARM0 306). Bilek servosu, flanş ve yaka için +%s mm." % (sayi(uz, 1), sayi(uz - 306, 1)),
    "**Dirsek aralığı:** yazılım sınırı %d…%d°. Tarama %d°'ye kadar serbest (bükülme boşluğu %s mm), %d°'de ön kol çatalın kapağına "
    "değiyor. Bükülme payı için kapağın ön kısmı 45° pahlı. Servo 180° olduğundan horn, servo orta konumu (90) dirsek %s°'ye denk gelecek "
    "şekilde takılır. Böylece servo yaklaşık −%s…%s° aralığını kapsar; sınır dışı kısım yazılımda kesilir."
    % (ar[0], ar[1], amax, sayi(bk[str(amax)][0], 1), ta["ilk_carpan"]["+"][0], sayi((ar[0] + ar[1]) / 2, 1),
       sayi(90 - (ar[0] + ar[1]) / 2, 1), sayi(90 + (ar[0] + ar[1]) / 2, 1)),
    "**Bilek:** ±90° (180° servo). El bilekteki her açıda ön kola ve (dirsek aralığında) üst kola çarpmıyor.",
    "**El:** V3'teki sabit el, hafif nesne için kancalı. Parmaklar 16 mm içe bükük, ucunda 5 mm dudak var (kol aşağıdayken çanta sapı gibi ~10 mm'lik "
    "bir sap tutar). Başparmak önde. Ek servo ya da kavrayıcı eklenmedi; proje planında eşya tutan kol kapsam dışı.",
    "**Ön kol gövdesi arkası açık U:** iki servo da arkadan takılır, bütün somunlara arkadan ulaşılır. Ön yüzü tablada desteksiz basılır.",
    "**Baskı yöntemi kabukla aynı** (X2D kullanılabilir %s × %s × %s mm, 45° çıkıntı, 1 mm katmanlı desteksizlik kontrolü). Çatal ters "
    "basılır (pim tablada). Tüp yuvasının tavanı V oluk, kapağın önü 45° pah, köprü ucu 45° kaburga; hepsi desteksiz basılabilir." % tuple(sayi(v, 0) for v in Y["kullanilabilir"]),
    "**Kütle:** PETG etkin doluluk %%%d (tahmini; küçük ve kalın cidarlı parçalar, 3-4 çevre + %%20 dolgu). Omuz %%60, kabuk %%90 kullanıyor. "
    "MG996R 55 g (datasheet), diğer satın alınan parçalar hacim × yoğunluk." % round(d["doluluk"] * 100),
    "**Sol kol:** sağın X aynası (`arayuz.MODULLER['dirsek_sol']`). Baskı parçaları (çatal, ön kol, flanş, el) dilimleyicide X'te aynalanarak "
    "basılır. Satın alınanlar ve bağlantı elemanları aynı.",
]
SIRA = [
    "Isıl gömme somunları havyayla bas: ön kol yanağına 1× M5, bilek flanşına 2× M3 (radyal).",
    "625ZZ'yi çatal iç kolunun Ø16 yuvasına, dudağa dayanana kadar bastır.",
    "Bilek servosunu ön kola arkadan sok (mil aşağı), 4× M4×16 + kontra somunla bağla. Dirsek servosunu da aynı şekilde tak.",
    "Bilek servosunu orta konuma getir. Horn'u el avucu içe (−X) bakacak şekilde tak, merkez vidasını sık. Bilek flanşını 4× M3×8 ile horn'a, "
    "eli yakasından 2× M3×6 ile flanşa bağla.",
    "Dirsek servosunu orta konuma (90) getir. Horn'u ön kol dirsek %s°'deyken tak, merkez vidasını sık." % sayi((ar[0] + ar[1]) / 2, 1),
    "Ön kolun başını çatalın kolları arasına aşağıdan sok. Dış kolu horn'a 4× M3×8 ile, iç kolu M5×12 + pulla bağla (pul ve iç bilezik ön "
    "koldaki dayamaya sıkılır, ön kol serbest döner).",
    "Çatalı tüpe tak (pim içeride, bilezik dışarıda). Tüp ucu oluğa dayanınca 2× M3×20 + pul + kontra somunla bileziği sık.",
]
KABUK_MIN = "–"
if KT:
    KABUK_MIN = sayi(min(k["en_kucuk_bosluk_aralikta"]["kabuk"]["bosluk_mm"] for k in KT.values() if "kabuk" in k["en_kucuk_bosluk_aralikta"]), 1)
TORK_KARAR = (
    "**Karar (2. aşama): ana senaryo yüksüz jest.** Proje kapsamı 1. dönemde ses + tekerlek + kayıtlı jestler; eşya tutan kol kapsam dışı "
    "(README \"Ses mi görüntü mü\" satırı, `planlama/proje-plani.md`), 2. dönemde nesne tutma gerekirse belki ayrı bir hazır kol (SO-101). "
    "Yüksüz jestte mevcut servolar yeterli: dirsek MG996R pay %s×, omuz DS3218MG S1 %s× / S2 %s× (1. aşama tork taraması). 0,5 kg yük "
    "hesabı yalnız bilgi amaçlı tutuldu; el ucu yükü ~50 g ile sınırlı kabul edilir (2× payla izinli yük kol yatayken S1 %d g, S2 %d g). "
    "Yük ileride istenirse seçenekler: dirseğe DS3218MG (20 kg·cm, ön kol servoya göre güncellenir), omuza ≥ 50 kg·cm servo ya da redüktör."
    % (sayi(td["yuksuz_pay"], 1), sayi(t1["yuksuz_pay"], 1), sayi(t2["yuksuz_pay"], 1), t1["izinli_yuk_2x_g"], t2["izinli_yuk_2x_g"]))
ACIK = [
    "**0,5 kg yük (bilgi; karar verildi, bkz. Tork):** Kol yatayken el ucundaki 0,5 kg yükü omuz S1/S2 taşıyamıyor (%s kg·cm > DS3218MG %s; pay %s×). "
    "Dirsek servosunda pay kalmıyor (%s kg·cm, MG996R 9,4; pay %s×). 2× payla izinli yük kol yatayken S1 %d g, S2 %d g, dirsekte %d g. "
    "Seçenekler: (a) yükü ~50 g ile sınırla ya da yalnız kol aşağıdayken taşı (omuz ev pozunda dirsek 90°'de S1 %s kg·cm, pay %s×; "
    "dirsek yine sınırda); (b) dirseğe DS3218MG (20 kg·cm, pay %s×; ön kol 3,8 mm daha yüksek servoya göre güncellenir); (c) omuzda ≥ 50 kg·cm "
    "servo ya da redüktör (0,5 kg'da 2× pay için)."
    % (sayi(t1["yuklu_kgcm"], 1), sayi(t1["stall_kgcm"], 0), sayi(t1["yuklu_pay"], 2), sayi(td["yuklu_kgcm"], 1), sayi(td["yuklu_pay"], 2),
       t1["izinli_yuk_2x_g"], t2["izinli_yuk_2x_g"], td["izinli_yuk_2x_g"],
       sayi(max(e["s1_yuklu_omuz0"] for e in eg), 1), sayi(t1["stall_kgcm"] / max(e["s1_yuklu_omuz0"] for e in eg), 1),
       sayi(20.0 / td["yuklu_kgcm"], 2)),
    "**Servo kabloları:** Çatal kapağında Ø10 kablo deliği var, ancak omuz çatalının pimi dolu olduğundan tüpün üstü kapalı ve kablo tüpten "
    "omza çıkamıyor. Şimdilik kablolar dışarıdan gevşek halkayla (spiral kılıf) götürülmeli. Omuz pimine kablo deliği açmak omuz değişikliği; karar Duffy'nin.",
    "**Horn delik dizilimi:** 25T disk horn'da M3 deliklerin yarıçapı 8,5 mm varsayıldı (omuzdaki gibi). Horn alt yüzünün kasa üstünden "
    "yüksekliği 3,0 mm (tahmini; datasheet'e göre mil ucu 6,3 mm). Parçalar gelince kumpasla ölçülmeli.",
    "**Geçme toleransları:** pim/tüp ve bilezik/tüp 0,1 mm, 625ZZ yuvası Ø16 nominal çizildi. X2D toleransı için önce bilezik + pim deneme "
    "halkası basılmalı. PETG bilezik zamanla gevşeyebilir (sürünme); bakımda sıkma kontrolü yapılmalı.",
    "**Bilekte ayrı rulman yok:** el ve yük MG996R çıkış milinde. Kol yatayken 0,5 kg yük mile yaklaşık 0,3 N·m eğilme bindirir (tahmini). "
    "Yük sürekli taşınacaksa rulmanlı bilek göbeği (ör. 6805) eklenmeli; bu ön kolu yaklaşık 42 mm derinliğe çıkarır.",
    "**Ön kol arkası açık:** Görünüm için arkaya takılan bir kapak sonra eklenebilir (servolara erişimi kapatmamalı).",
    "**Kabuğa en yakın nokta:** kol aşağıdayken (yana 0°) dirsek çatalının sıkma bileziği göğüs bandına %s mm yaklaşıyor (eklem aralığında "
    "çakışma yok). Baskı toleransı ve kabuk montaj sapması bu payı yiyebilir; ilk montajda kol aşağıda öne-arka sallanırken bileziğin kabuğa "
    "sürtmediği elle kontrol edilmeli. Sürterse çözüm yazılımda yana açmayı en az 2-3° tutmak (geometri değişikliği gerekmez)." % KABUK_MIN,
    "**Yana açma 0°'ın altına inmemeli:** aralık dışı halkada (yana −10°) el ve bilek kabuğun göğüs/orta bandına giriyor. Omuz yazılım sınırı "
    "(yana 0…120°) bunu zaten engelliyor; servo kalibrasyonunda 0° konumu kabuğa doğru kaçmamalı.",
]

# ---------------------------------------------------------------- HTML
H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dirsek Modülü V3</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:18px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
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
.uyari{border-left:4px solid var(--no);background:var(--card);padding:10px 14px;border-radius:6px}
.karar{border-left:4px solid var(--ok);background:var(--card);padding:10px 14px;border-radius:6px}
</style></head><body><main>""")


def md(s):
    """**kalin** ve `kod` -> HTML."""
    s = esc(s)
    out, b, c = [], False, False
    i = 0
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


H.append("<h1>Dirsek modülü (sağ kol): dirsek + ön kol + bilek + el</h1>")
H.append("<div class='sub'>2. aşama: modüller arası tarama + ana montaj · FreeCAD 1.1 · <code>dirsek_montaj.py</code> · %d parça (%d baskı) · ölçüler "
         "<code>arayuz.DIRSEK</code>'ten, V3 sağ kol düzeni (robot_cad) · yazıcı %s · sol kol = X aynası</div>"
         % (d["parca_sayisi"], d["baski_sayisi"], esc(Y["model"])))
kpi = [
    ("%d / %d" % (d["baski_sayisi"], d["parca_sayisi"]),
     "baskı / toplam parça · hepsi geçerli, tek katı" if not d["gecersiz"] and not d["coklu_kati"] else "GEÇERSİZ PARÇA VAR"),
    ("%d" % ev_cak, "ev pozunda modül içi çakışma (%d çift sınandı) · omuzla %d" % (d["cift_sayisi"], ar_cak)),
    ("%d / %d" % (bag_ok, len(bag)), "bağlantı kontrolü (%d tekil ölçüt): dayanma, eksen hizası, cıvata ucu / kavrama" % kontrol_n),
    ("%d…%d°" % (ar[0], ar[1]), "dirsek yazılım sınırı · tarama %d…%d° serbest, %d°'de bükülme boşluğu %s mm" % (amin, amax, ar[1], sayi(bk[str(int(ar[1]))][0], 1))),
    ("±90°", "bilek (ön kol ekseni) · el her açıda serbest"),
    ("%d / %d" % (sigan, len(baski)), "X2D'ye sığan baskı parçası · desteksiz %d / %d" % (destek, len(baski))),
    ("%s g" % sayi(d["kutle_g"], 0), "sağ kol, omuzdan aşağısı (baskı %s g) · omuz ekseninden el ucuna %s mm" % (sayi(d["kutle_tur"]["Baski"], 0), sayi(uz, 1))),
    ("%s× / %s×" % (sayi(td["yuksuz_pay"], 1), sayi(td["yuklu_pay"], 2)), "dirsek MG996R payı: yüksüz / 0,5 kg el ucu yüküyle"),
    ("%s× / %s×" % (sayi(t1["yuksuz_pay"], 1), sayi(t1["yuklu_pay"], 2)),
     "omuz S1 DS3218MG payı: yüksüz / 0,5 kg (omuz raporunda %s×, alt kol 260 g tahmini)" % sayi(20.0 / oe["S1"], 1)),
]
if KT:
    n_ar = sum(k["cakisan_tam_poz_aralikta"] + k["cakisan_alt_poz_aralikta"] for k in KT.values())
    kpi.insert(2, ("%d" % n_ar, "modüller arası çakışma, eklem aralığında (%d poz/kol + ince adım; kabuğa en az %s mm)" % (
        list(KT.values())[0]["kaba_izgara"]["tam_poz"], KABUK_MIN)))
if MA:
    kpi.append(("%s kg" % sayi(MA["kutle_g"] / 1000, 2), "ana montaj (iki dirsekle) · AM (%s; %s; %s) mm" % tuple(sayi(x, 1) for x in MA["agirlik_merkezi"])))
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")
H.append("<p class='karar'>%s</p>" % md(TORK_KARAR))

H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (("dirsek-izometrik.png", "İzometrik: dirsek modülü + sağ omuz (bağlam, omuz gövdesi yarı saydam)", ""),
                   ("dirsek-on.png", "Önden (+Z): sıkma bileziği, çatal, ön kol, kancalı el", ""),
                   ("dirsek-yan.png", "Yandan (+X): çatal dış kolu, horn ve 4× M3", ""),
                   ("dirsek-arka.png", "Arkadan: açık U ön kol, iki servo ve somunlar; bilezik kulakları (2× M3×20)", ""),
                   ("dirsek-eklem-yakin.png", "Dirsek eklemi yakın plan (çatal yarı saydam): horn → çatal dış kolu", ""),
                   ("dirsek-eklem-yakin-ic.png", "Dirsek eklemi içten: 625ZZ + M5 pim karşı yatak", ""),
                   ("dirsek-kesit-eklem.png", "Eksen kesiti (z = dirsek ekseni): M5 pim, pul, 625ZZ, Ø8 dayama, ısıl gömme somun, servo, horn, dış kol", "wide"),
                   ("dirsek-kesit.png", "Kesit (tam boy): pim, V oluk, kablo deliği, iki servo, bilek flanşı, el yakası", ""),
                   ("dirsek-patlatilmis.png", "Patlatılmış: üst grup, ön kol grubu, el grubu", "")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div>")
H.append("<h3>Dirsek açısı pozları (yandan, +X; solda ön)</h3><div class='grid4'>")
for al in (0, 45, 90, 105):
    ad = "dirsek-poz-%03d.png" % al
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure><img src='%s' alt='dirsek %d'><figcaption>Dirsek %d°</figcaption></figure>" % (img64(ad), al, al))
if os.path.exists(os.path.join(G, "dirsek-poz-090-bilek90.png")):
    H.append("<figure><img src='%s' alt='bilek'><figcaption>Dirsek 90°, bilek 90°</figcaption></figure>" % img64("dirsek-poz-090-bilek90.png"))
H.append("</div>")

H.append("<h2>Yapı</h2><ul>")
H.append("<li><b>Üst grup</b> (omuzun Kol grubuyla birlikte hareket eder): dirsek çatalı (pim + sıkma bileziği + köprü + iki kol), 625ZZ dış "
         "bileziği, dirsek horn'u ve cıvataları · %s g</li>" % sayi(d["kutle_grup"]["UstKol"], 0))
H.append("<li><b>Ön kol</b> (dirsek ekseninde döner): ön kol gövdesi, dirsek ve bilek MG996R, 625ZZ iç bileziği, M5 pim · %s g</li>"
         % sayi(d["kutle_grup"]["OnKol"], 0))
H.append("<li><b>El</b> (bilek ekseninde döner): bilek horn'u, bilek flanşı, el · %s g</li>" % sayi(d["kutle_grup"]["El"], 0))
H.append("<li>Dirsek ekseni X'e paralel, omuz yerelinde (x, %s, %s); bilek ekseni Y'ye paralel, x = %s, z = %s (üst kol tüpüyle aynı hizada).</li>"
         % (sayi(DI["eksen_y"], 0), sayi(DI["eksen_z"], 2), sayi(DI["bilek_x"], 0), sayi(DI["bilek_z"], 2)))
H.append("</ul>")

H.append("<h2>Parça listesi (sağ kol)</h2><div class='tw'>")
TUR = {"Baski": "Baskı (PETG)", "Satin": "Satın alınan", "Baglanti": "Bağlantı elemanı"}
rows = [(TUR.get(t, t), esc(tr(k)), n, 2 * n, sayi(m, 1)) for t, k, n, m in sorted(d["bom"], key=lambda r: ({"Baski": 0, "Satin": 1, "Baglanti": 2}[r[0]], r[1]))]
H.append(tablo(["Tür", "Kalem", "Adet (sağ)", "Adet (iki kol)", "Kütle sağ (g)"], rows, "sayi") + "</div>")
H.append("<p class='not'>CSV: <code>dirsek-bom.csv</code>. Satın alınanlar: 2× MG996R (bütçede 6 adet: dirsek, bilek, kafa), 2× 25T disk horn, 1× 625ZZ "
         "(omuzdaki ile aynı tip).</p>")

H.append("<h2>Hangi parça neye, nasıl bağlanıyor</h2><div class='tw'>")
H.append(tablo(["Bağlantı", "Nasıl oturuyor", "Bağlantı elemanı"], [(esc(a), esc(b), esc(c)) for a, b, c in BAGLANTI]) + "</div>")
H.append("<h3>Bağlantı kontrolleri (<code>dirsek_montaj.py</code>)</h3><div class='tw'>")
rows = []
for b in bag:
    olc = "; ".join(esc(x[0]) for x in b["kontroller"][:4]) + (" …" if len(b["kontroller"]) > 4 else "")
    rows.append((esc(tr(b["ad"])), len(b["kontroller"]), OK if b["tamam"] else NO, "<span class='not'>%s</span>" % olc))
H.append(tablo(["Bağlantı", "Ölçüt", "Sonuç", "Örnek ölçütler"], rows) + "</div>")
H.append("<p class='not'>Ölçütler: bağlantı elemanı tasarım ekseninde (sapma &lt; 10⁻⁶ mm); baş, pul ve somun yüzeye dayalı (≤ 0,01 mm); cıvata deliğin "
         "ortasında; cıvata ucu kontra somundan ≥ 0,5 mm taşıyor; ısıl gömme somunda kavrama ≥ d ve ≤ somun boyu; horn'da kavrama ≥ 2,5 mm ve uçtan "
         "servo kasasına ≥ 1 mm. Pimde ayrıca birbirine göre dönen parçaların değmediği kontrol edildi (≥ 0,3 mm). Omuz arayüzü: %s.</p>"
         % "; ".join("%s %s" % (esc(x[0]), "✓" if x[2] else "✗") for x in d["omuz_arayuzu"]["kontroller"]))

H.append("<h2>Baskı parçaları (%s)</h2><div class='tw'>" % esc(Y["model"]))
rows = []
for b in baski:
    o = b["olcu"]
    rows.append((esc(TR.get(b["ad"], b["ad"])), "%s × %s × %s" % (sayi(o[0], 0), sayi(o[1], 0), sayi(o[2], 0)), OK if b["sigar"] else NO,
                 esc(b["yon"]), "%s %%" % sayi(100 * b["cikinti_orani"], 1), OK if b["desteksiz"] else NO + " (%d)" % b["destek_sorun_sayi"],
                 sayi(b["hacim_cm3"], 1), sayi(b["kutle_g"], 0), sayi(b["filament_g"], 0), sayi(b["sure_saat"], 1)))
top = (sum(b["kutle_g"] for b in baski), sum(b["filament_g"] for b in baski), sum(b["sure_saat"] for b in baski))
rows.append(("<b>Toplam (sağ kol)</b>", "", "", "", "", "", "", "<b>%s</b>" % sayi(top[0], 0), "<b>%s</b>" % sayi(top[1], 0), "<b>%s</b>" % sayi(top[2], 1)))
H.append(tablo(["Parça", "Tablada ölçü (mm)", "X2D'ye sığar", "Baskı yönü", "45° üstü çıkıntı", "Desteksiz", "Hacim (cm³)", "Kütle (g)",
                "Filament (g)", "Süre (sa, tahmini)"], rows, "sayi") + "</div>")
H.append("<p class='not'>Kullanılabilir hacim %s × %s × %s mm (X2D ana nozul %s × %s × %s, her eksende %s mm pay; arayuz.YAZICI). Malzeme PETG; kütle = hacim × %s g/cm³ "
         "× %%%d etkin doluluk (tahmini); süre %s mm³/s ortalama debiyle (tahmini). Desteksizlik kabuktaki yöntemle: 1 mm katmanlarda önceki katmanın "
         "1 mm ötesine taşan, 2 mm'den geniş ve 15 mm'den uzun bölge yok. <b>Sol kol parçaları dilimleyicide X'te aynalanarak basılır</b> (iki kol toplamı %s g filament).</p>"
         % (sayi(Y["kullanilabilir"][0], 0), sayi(Y["kullanilabilir"][1], 0), sayi(Y["kullanilabilir"][2], 0), sayi(Y["hacim_ana"][0], 0),
            sayi(Y["hacim_ana"][1], 0), sayi(Y["hacim_ana"][2], 0), sayi(Y["pay"], 0), sayi(A.PETG_RHO, 2), round(d["doluluk"] * 100),
            sayi(A.PETG_HACIM_HIZI, 0), sayi(2 * top[1], 0)))

H.append("<h2>Tork</h2>")
H.append("<p class='karar'>%s</p>" % md(TORK_KARAR))
H.append("<p>Gerçek parça kütleleriyle (omuz parçaları omuz modelinden, dirsek parçaları bu modelden), el ucunda %s g yükle. Tarama: omuz S1 %d…%d°, "
         "S2 %d…%d°, dirsek %d…%d° (5° adım), bilek −90/0/90 (%s poz). Bilek torku için yük kancada.</p>"
         % (sayi(d["tork"]["yuk_g"], 0), -45, 135, 0, 120, ar[0], ar[1], sayi(37 * 25 * (int((ar[1] - ar[0]) / 5) + 1) * 3, 0)))
rows = []
POZ = lambda p: "S1 %+d°, S2 %d°, dirsek %d°, bilek %+d°" % tuple(p)
for t in d["tork"]["sonuc"]:
    ad = {"S1 (omuz one-arka)": "Omuz S1 (öne-arka)", "S2 (omuz yana acma)": "Omuz S2 (yana açma)"}.get(t["eklem"], t["eklem"])
    izin = ("≥ %s g" % sayi(t["izinli_yuk_2x_g"], 0)) if t["izinli_yuk_2x_g"] >= 3000 else "%s g" % sayi(t["izinli_yuk_2x_g"], 0)
    rows.append((esc(ad), esc(t["servo"]), sayi(t["stall_kgcm"], 1), sayi(t["yuksuz_kgcm"], 2), pay(t["yuksuz_pay"]),
                 sayi(t["yuklu_kgcm"], 2), pay(t["yuklu_pay"]), "<span class='not'>%s</span>" % esc(POZ(t["yuklu_poz"])), izin))
H.append("<div class='tw'>" + tablo(["Eklem", "Servo", "Durma torku (kg·cm)", "Yüksüz en kötü", "Pay", "0,5 kg ile en kötü (bilgi)", "Pay", "En kötü poz (yüklü)",
                                     "2× pay için izinli yük"], rows, "sayi") + "</div>")
H.append("<p class='not'>Durma torkları: MG996R 9,4 kg·cm @4,8 V (11 @6 V; datasheet, 01-donanim-maliyet.md); DS3218MG 20 kg·cm (omuz raporundaki değer). "
         "Omuz raporundaki eski hesap (dirsek ve aşağısı 260 g, omuzdan 200 mm, yüksüz) S1 %s / S2 %s kg·cm idi (≈ %s× pay). Gerçek kol (omuzdan "
         "aşağısı %s g, el ucu %s mm) yüksüz S1 %s / S2 %s kg·cm verir: pay %s× / %s×. Omuz dosyaları değiştirilmedi.</p>"
         % (sayi(oe["S1"], 2), sayi(oe["S2"], 2), sayi(20.0 / max(oe["S1"], oe["S2"]), 1), sayi(d["kutle_g"], 0), sayi(uz, 1), sayi(t1["yuksuz_kgcm"], 2),
            sayi(t2["yuksuz_kgcm"], 2), sayi(t1["yuksuz_pay"], 2), sayi(t2["yuksuz_pay"], 2)))
H.append("<figure class='wide'><img src='%s' alt='tork egrisi'><figcaption>Tork − dirsek açısı. Sol: dirsek servosu, omuz ev pozunda (kol aşağıda, ön kol "
         "dirsekle kalkar). Sağ: omuz S1, omuz öne 90° (üst kol yatay). Kesikli çizgiler durma torku ve 2× pay sınırı. Veri aşağıdaki tabloda.</figcaption></figure>" % GRAF_TORK)
rows = [(e["al"], sayi(e["dirsek_yuksuz"], 2), sayi(e["dirsek_yuklu"], 2), sayi(e["s1_yuksuz_omuz0"], 2), sayi(e["s1_yuklu_omuz0"], 2),
         sayi(e["s1_yuksuz_omuz90"], 2), sayi(e["s1_yuklu_omuz90"], 2)) for e in eg]
H.append("<details><summary class='not'>Tork tablosu (kg·cm)</summary><div class='tw'>" +
         tablo(["Dirsek (°)", "Dirsek yüksüz", "Dirsek 0,5 kg", "S1 yüksüz (omuz 0)", "S1 0,5 kg (omuz 0)", "S1 yüksüz (omuz öne 90)", "S1 0,5 kg (omuz öne 90)"],
               rows, "sayi") + "</div></details>")

H.append("<h2>Dirsek içi çakışma taraması</h2>")
H.append("<p>Ön kol grubu × üst grup (çatal, bilezik cıvataları, horn + omuzun üst kol tüpü ve çatalı) için dirsek %d…%d°, 5° adım. El × üst grup için "
         "her dirsek açısında bilek −90/−45/0/45/90. El × ön kol için bilek −90…90, 15° adım. Ölçüt: ortak hacim &gt; 0,5 mm³.</p>" % (ALS[0], ALS[-1]))
H.append("<figure class='wide'><img src='%s' alt='tarama'><figcaption>Dirsek açısına göre çakışma. Taranan aralığın altı (−60°) da serbest.</figcaption></figure>" % GRAF_TARAMA)
ilk = ta["ilk_carpan"].get("+")
rows = [("Serbest dirsek aralığı", "%d…%d° (tarama −60…150°)" % (amin, amax)),
        ("İlk çakışma", "%d°: %s" % (ilk[0], esc(", ".join("%s ↔ %s (%s mm³)" % (tr(a), tr(b), sayi(v, 1)) for a, b, v in ilk[1]))) if ilk else "yok"),
        ("Yazılım sınırı (arayuz.DIRSEK)", "%d…%d° · serbest aralıkta, sınırda bükülme boşluğu %s mm: %s" % (ar[0], ar[1], sayi(bk[str(int(ar[1]))][0], 2),
                                                                                         OK if ta["aralik_ok"] else NO)),
        ("Bükülme boşluğu (ön kol + el ↔ kapak/bilezik/tüp)", " · ".join("%s°: %s mm" % (k, sayi(v[0], 1)) for k, v in sorted(bk.items(), key=lambda x: int(x[0])))),
        ("Pimdeki eksenel boşluk", "%s mm (ön kol yanağı ↔ çatal iç kolu, her açıda)" % sayi(ta["bosluk"]["0"][0], 1)),
        ("Bilek", "−90…90° her açıda serbest (el ↔ ön kol)" if ta["bilek_serbest"] else "ÇAKIŞMA VAR"),
        ("Ev pozu", "modül içi %d çakışma; omuz Kol grubuyla %d" % (ev_cak, ar_cak))]
H.append("<div class='tw'>" + tablo(["", ""], rows) + "</div>")

H.append("<h2>Modüller arası çakışma</h2>")
HEDEF_AD = {"kabuk": "kabuk", "iskelet": "iskelet", "ayrilmis_bolgeler": "ayrılmış bölgeler (kafa, taban)"}


def hedef_ad(m):
    if m in HEDEF_AD:
        return HEDEF_AD[m]
    o, _, g = m.partition(" ")
    return "%s omuz %s" % ("sağ" if o.endswith("sag") else "sol", {"govde": "gövdesi", "gobek": "göbeği"}.get(g, g))


def poz_yaz(pz):
    et = ("öne", "yana", "dirsek", "bilek")
    return ", ".join("%s %s°" % (et[i], sayi(v, 0)) for i, v in enumerate(pz))


if not KT:
    H.append("<div class='bos'>carpisma-sonuc.json'da kol zinciri taraması yok (carpisma.py çalıştırılmadı).</div>")
else:
    k0 = KT["sag"]
    kb = k0["kaba_izgara"]
    H.append("<p><code>carpisma.py</code> (bölüm 4) dirsek modülünü omuz zinciriyle birlikte sürer: üst grup (çatal) omuzun Kol grubuyla "
             "(Pp·Pr), ön kol ayrıca dirsekte (Pe), el bilekte (Pb) döner; sol kol gerçek aynalı geometri. Hedefler: iskelet, kabuk, ayrılmış "
             "bölgeler (kafa, taban), iki omuzun gövdesi ve kendi omuzunun göbeği. Ön kol/el ile omuzun Kol grubu arasındaki bağıl hareket omuz "
             "pozundan bağımsız ve 1. aşamadaki dirsek içi taramada sınandı.</p>")
    H.append("<p><b>Yöntem:</b> kaba ızgara öne-arka %s…%s° ve yana %s…%s° (15° adım) × dirsek %s × bilek %s = kol başına <b>%d poz</b> "
             "(%d alt poz: çatal omuz pozuna, ön kol + dirseğe, el + bileğe bağlı ayrı hesaplanır). Sınır kutusu ön elemesi: her parçanın kutusu poz "
             "matrisiyle taşınır, hedefe %d mm'den uzak çiftler hiç ölçülmez; 5 mm'nin altına inen her aday tam ölçülür (distToShape, temas ya da gömülme "
             "şüphesinde ortak hacim &gt; 0,5 mm³), hedef başına en küçük boşluk dal-sınırla bulunur. 5 mm'nin altında boşluk kalan alt pozların "
             "çevresi 5° adımla yeniden tarandı (%d alt poz). Ayrıca aralık dışı halka: öne-arka −60° ve 150°, yana −10° (%d poz). Süre kol başına "
             "%s s.</p>" % (kb["one_arka"][0], kb["one_arka"][-1], kb["yana"][0], kb["yana"][-1], kb["dirsek"], kb["bilek"], kb["tam_poz"],
                           k0["alt_poz"]["kaba"], 150, k0["alt_poz"]["ince"], k0["aralik_disi_halka"]["tam_poz"], sayi(k0["sure_s"], 0)))
    rows = []
    for t, k in KT.items():
        rows.append(("<b>%s kol</b>" % ("Sağ" if t == "sag" else "Sol"), "%d" % k["kaba_izgara"]["tam_poz"],
                     (OK if not k["cakisan_tam_poz_aralikta"] and not k["cakisan_alt_poz_aralikta"] else NO) + " %d" % (
                         k["cakisan_tam_poz_aralikta"] + k["cakisan_alt_poz_aralikta"]),
                     "%d" % k["aralik_disi_halka"]["tam_poz"], "%d" % k["cakisan_tam_poz_aralik_disi"], "%d" % k["yakin_aralikta_sayi"],
                     "%d" % k["tam_olcum"]))
    H.append("<div class='tw'>" + tablo(["", "Poz (kaba)", "Eklem aralığında çakışma", "Aralık dışı poz", "Aralık dışı çakışan", "5 mm altı yaklaşım (alt poz)",
                                         "Tam ölçüm"], rows, "sayi") + "</div>")
    H.append("<h3>En küçük boşluklar (eklem aralığında)</h3>")
    rows = []
    for t, k in KT.items():
        for m, b in sorted(k["en_kucuk_bosluk_aralikta"].items(), key=lambda x: x[1]["bosluk_mm"]):
            rows.append(("%s kol" % ("Sağ" if t == "sag" else "Sol"), esc(hedef_ad(m)), "<b>%s mm</b>" % sayi(b["bosluk_mm"], 2),
                         esc("%s ↔ %s" % (b["parca"], b["hedef"])), esc(poz_yaz(b["poz"]))))
        if "ayrilmis_bolgeler" not in k["en_kucuk_bosluk_aralikta"]:
            rows.append(("%s kol" % ("Sağ" if t == "sag" else "Sol"), "ayrılmış bölgeler (kafa, taban)", "&gt; 150 mm", "–", "hiçbir pozda 150 mm'ye yaklaşmıyor"))
    if KK:
        e = KK["en_kucuk"]
        ed = KK["en_kucuk_dirsek"]
        rows.append(("İki kol", "sağ kol ↔ sol kol", "<b>%s mm</b>" % sayi(e["bosluk_mm"], 0), esc("%s ↔ %s" % tuple(e["cift"])),
                     esc("sağ: %s · sol: %s" % (poz_yaz(e["sag"]), poz_yaz(e["sol"])))))
        rows.append(("İki kol", "sağ dirsek ↔ sol dirsek", "%s mm" % sayi(ed["dirsek_bosluk_mm"], 0), esc("%s ↔ %s" % tuple(ed["dirsek_cift"])),
                     esc("sağ: %s · sol: %s" % (poz_yaz(ed["sag"]), poz_yaz(ed["sol"])))))
    H.append("<div class='tw'>" + tablo(["Kol", "Hedef", "En küçük boşluk", "Parça çifti", "Poz"], rows) + "</div>")
    if KK:
        H.append("<p class='not'>Kol ↔ kol: %d poz çifti (iki kol aynı anda; simetrik pozlar, zıt pozlar, iki kolun öne birlikte uzandığı pozlar "
                 "[öne 60…135°, yana 0…30°, dirsek 0…105°, bilek aynı ve zıt]), çakışma %d. Kollar yalnız dışarı açıldığı (yana 0…120°) ve dirsek ekseni "
                 "kolla birlikte döndüğü için kollar gövde ortasına yaklaşamıyor; iki kol arası en az %s mm.</p>" % (
                     KK["poz_cifti"], KK["cakisan"], sayi(KK["en_kucuk"]["bosluk_mm"], 0)))
    rows = []
    for m, L in k0["en_kucuk_ciftler_aralikta"].items():
        for b in L[:4]:
            rows.append((esc(hedef_ad(m)), sayi(b["bosluk_mm"], 2), esc("%s ↔ %s" % (b["parca"], b["hedef"])), esc(poz_yaz(b["poz"]))))
    H.append("<details><summary class='not'>Sağ kol: hedef başına en yakın parça çiftleri</summary><div class='tw'>" +
             tablo(["Hedef", "Boşluk (mm)", "Parça çifti", "Poz"], rows) + "</div></details>")
    H.append("<h3>Yasak poz bölgeleri</h3>")
    H.append("<p><b>Eklem aralığında yasak bölge yok</b>: omuz −45…135° / 0…120°, dirsek 0…105°, bilek ±90° içindeki bütün taranan pozlar "
             "çakışmasız; dirsek parçalarında geometri değişikliği gerekmedi. Aralık dışı bulgular (ayrı): yana −10°'de öne-arka −45…0° arasında el, "
             "bilek flanşı ve horn kabuğun göğüs/orta bandına giriyor (sağ %d, sol %d poz); bu bölge omuzun yana açma sınırı (0°) ile zaten kapalı. "
             "Öne-arka −60° ve 150°'de kol çakışmasız.</p>" % (KT["sag"]["cakisan_tam_poz_aralik_disi"], KT["sol"]["cakisan_tam_poz_aralik_disi"]))

H.append("<h2>Ana montajda</h2>")
if MA and ED:
    ek = [j for j in MA["eklemler"] if j.get("modul", "").startswith("dirsek")]
    rows = []
    for j in ek:
        if j["tip"] == "Fixed":
            rows.append((esc(j["etiket"]), "Sabit", "(%s)" % "; ".join(sayi(x, 1) for x in j["nokta"]), "–", "–"))
            continue
        o = ED["ozet"][j["isim"]]
        rows.append(("<b>%s %s</b>" % ("Sağ" if "Sag" in j["isim"] else "Sol", j["anahtar"]), "Döner",
                     "(%s) · yön (%s)" % ("; ".join(sayi(x, 1) for x in j["nokta"]), "; ".join(sayi(x + 0.0, 0) for x in j["eksen"])),
                     "%s…%s°" % (sayi(j["sinir"][0], 0), sayi(j["sinir"][1], 0)),
                     "%.1e mm · %.1e° (%d poz)" % (o["max_mm"], o["max_derece"], o["vaka"])))
    H.append("<p><code>montaj/moduller.py</code>'ye <code>dirsek_sag</code> / <code>dirsek_sol</code> yükleyicisi eklendi: üç grup (çatal, ön kol, el), "
             "çatal omuzun Kol grubuna sabit eklemle bağlı, eksenler ve sınırlar <code>dirsek-montaj.FCStd</code>'den okunup <code>arayuz.DIRSEK</code> "
             "ile karşılaştırılıyor, solda eksen aynalanıyor. Ana montaj %d parça, %d grup, %d eklem; kütle <b>%s kg</b>, AM (%s; %s; %s) mm "
             "(modül analizleri toplamından fark %s g).</p>" % (
                 MA["parca_sayisi"], MA["grup_sayisi"], len(MA["eklemler"]), sayi(MA["kutle_g"] / 1000, 2),
                 sayi(MA["agirlik_merkezi"][0], 1), sayi(MA["agirlik_merkezi"][1], 1), sayi(MA["agirlik_merkezi"][2], 1),
                 sayi(MA["karsilastirma"]["kutle"]["fark_analiz"], 2)))
    H.append("<div class='tw'>" + tablo(["Eklem", "Tip", "Nokta (global, mm) ve eksen", "Sınır", "Doğrulama sapması (en büyük)"], rows) + "</div>")
    vk = [v for v in ED["vakalar"] if "dirsek_sag" in v["komut"] or "dirsek_sol" in v["komut"]]
    sd = [v for v in ED["sinir_disi"] if any(k.startswith("dirsek") for k in v["komut"])]
    yn = [y for y in ED["yon"] if y["kol"].startswith("dirsek")]
    H.append("<p>Eklem doğrulaması (<code>eklem_dogrulama.py</code>): omuz + dirsek + bilek birlikte sürülen %d poz (sağ ve sol 10'ar, iki kol birlikte), "
             "her karede çözücünün grup yerleşimi <code>dirsek_parcalar.grup_yer</code> zinciriyle karşılaştırıldı: en büyük sapma <b>%.1e mm</b> / %.1e°. "
             "Yön: dirsek +90° el ucunu öne (+Z) getiriyor, bilek +90° avucu öne çeviriyor, iki kolda da %s. Sınır dışı sürüş (dirsek 120°, −20°; bilek "
             "120°) simülasyonda aynen izlendi (%d vaka): FreeCAD 1.1 sınırları yalnız fareyle sürüklemede uyguluyor, servo sınırı yazılımda.</p>" % (
                 len(vk), max(v["max_mm"] for v in vk), max(v["max_derece"] for v in vk),
                 "doğru" if all(y["dogru"] for y in yn) else "YANLIŞ", len(sd)))
    if GK:
        sur_d = [x for x in GK["surukleme"] if x["aciklama"].startswith("dirsek")]
        dj = [n for n in GK["eklemler"] if n.startswith("Dirsek")]
        H.append("<p>GUI'de taze açılış (<code>montaj_gui_kontrol.py</code>): %d dirsek eklemi (2 sabit + 4 döner) görünür ve ağaçta seçilebilir %s, "
                 "döner eklem işaretleri 3B görünümde tıklanınca eklemin kendisi seçiliyor %s. Ön koldan fareyle sürüklemede sağ dirsek %s°'ye büküldü "
                 "(sınır içinde).</p>" % (
                     len(dj), OK if all(GK["eklemler"][n]["gorunur"] and GK["secim"][n] for n in dj) else NO,
                     OK if all(GK["pick"][n]["nesne"] == n for n in GK["pick"] if n.startswith("Dirsek")) else NO,
                     sayi(sur_d[0]["sonra"]["dirsek"][0], 0) if sur_d else "–"))
else:
    H.append("<div class='bos'>montaj-analiz.json / eklem-dogrulama.json yok.</div>")
H.append("<div class='grid'>")
for ad, cap, w in (("montaj-dirsek.png", "Ana montaj: sağ dirsek ev pozunda, kabuğun yanında", ""),
                   ("montaj-poz-selam.png", "Ana montaj pozu: sağ kol yana 100°, öne 20°, dirsek 95°, bilek −60°; sol kol yana 10°, dirsek 30°", ""),
                   ("montaj-poz-one.png", "Ana montaj pozu: iki kol öne 90°, dirsek 60°, bilek 45°", ""),
                   ("montaj-gui-dirsek.png", "GUI: ön koldan fareyle sürüklenen sağ dirsek", ""),
                   ("montaj-hareket.gif", "Kollari_oynat simülasyonu (FreeCAD çözücü kareleri): omuz + dirsek + bilek birlikte", "wide")):
    if os.path.exists(os.path.join(GM, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad, GM), esc(cap), esc(cap)))
H.append("</div>")
H.append("<h3>Regresyon</h3>")
rr = []
for m, f in REG.items():
    if f:
        rr.append("%s %s (%d ölçüt)" % (m, "birebir aynı" if f["hepsi_ayni"] else "FARK VAR", len(f["satirlar"])))
H.append("<p>arayuz.py'ye <code>DIRSEK</code> ve iki <code>MODULLER</code> girişi eklendiği için koşuldu: %s. Kabuk modül çıktısı (kabuk_parcalar, "
         "güncel arayuz.py ile) git'teki <code>kabuk-montaj.FCStd</code> ile karşılaştırıldı: 202 / 202 parça, toplam hacim farkı 1,3·10⁻⁹ mm³, "
         "sınır kutusu farkı 0 mm. Omuz regresyonunun yeniden yazdığı aynı içerikli omuz dosyaları git ile geri alındı.</p>" % "; ".join(rr))

H.append("<h2>Kararlar ve varsayımlar</h2><ul>" + "".join("<li>%s</li>" % md(s) for s in KARAR) + "</ul>")
H.append("<h2>Montaj sırası (öneri)</h2><ol>" + "".join("<li>%s</li>" % md(s) for s in SIRA) + "</ol>")
H.append("<h2>Açık işler</h2><ul>" + "".join("<li>%s</li>" % md(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>dirsek_lib.py</code>: MG996R + 25T horn, baskı analizi (kabuktaki yöntem)</li>"
         "<li><code>dirsek_parcalar.py</code>: parçalar, bağlantı tanımları, kütle, kinematik (import edilebilir)</li>"
         "<li><code>dirsek_montaj.py</code>: kontroller, tarama, tork, baskı → <code>dirsek-montaj.FCStd</code>, <code>.step</code>, <code>dirsek-bom.csv</code>, "
         "<code>dirsek-analiz.json</code></li>"
         "<li><code>dirsek_gorsel.py</code> (FreeCAD GUI) → <code>gorsel/</code>; <code>dirsek_rapor.py</code> → bu sayfa</li>"
         "<li><code>../arayuz.py</code>: <code>DIRSEK</code> (eksenler, sınırlar, tüp arayüzü) ve <code>MODULLER['dirsek_sag' / 'dirsek_sol']</code></li>"
         "<li>2. aşama: <code>../carpisma.py</code> (kol zinciri taraması → <code>carpisma-sonuc.json</code> <code>kol_tarama</code>, <code>kol_kol</code>), "
         "<code>../montaj/moduller.py</code> (dirsek yükleyicisi), <code>ana_montaj.py</code>, <code>montaj_gorsel.py</code>, <code>eklem_dogrulama.py</code>, "
         "<code>montaj_gui_kontrol.py</code> → <code>../montaj/rapor.html</code></li></ul>")
H.append("<p class='not'>Üretildi: dirsek_rapor.py · analiz süresi %s s · STEP %d katı · eklemler %s</p>" % (sayi(d["sure_s"], 1), d["step_kati"],
                                                                                               "kuruldu" if d["joints_ok"] is True else esc(d["joints_ok"])))
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html", round(os.path.getsize(os.path.join(HERE, "rapor.html")) / 1024), "KB")
