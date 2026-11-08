# Kafa modulu raporu (rapor.html, gorseller gomulu). Sistem Python'u ile calisir (FreeCAD gerekmez).
# Girdiler: kafa-analiz.json (kafa_montaj.py), gorsel/*.png (kafa_gorsel.py), ../arayuz.py.
# F1a P1.6 (08.11.2026): 1,58 m kafasina (10,1 in QLED, Pi 5, ReSpeaker, USB ses karti + PAM8403) gore yenilendi; 125 cm
# metinleri ve kafa-analiz.json'da artik olmayan anahtarlar (olcu.ACIKLIK / Y_CAM, pi.konum_T / cevirici / amfi, isi.hava.giris_y ...)
# kaldirildi. Ozet: kafa grubu (tork kutlesi, kablo payi dahil), tilt payi tilt +-15 (pay_tilt15), pan payi pay_iki_hane.
# 2. asama: ../carpisma-sonuc.json (kafa_tarama), ../montaj/montaj-analiz.json, eklem-dogrulama.json, gui-kontrol.json ve
# ../montaj/gorsel/montaj-kafa*.png varsa "Moduller arasi carpisma ve ana montaj" bolumu doldurulur.
import os, sys, json, base64, html

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path.insert(0, UST)
import arayuz as A

G = os.path.join(HERE, "gorsel")
d = json.load(open(os.path.join(HERE, "kafa-analiz.json"), encoding="utf-8"))
K = A.KAFA
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


OK = "<span class='ok'>tamam</span>"
NO = "<span class='no'>HATA</span>"
TR = {"Servo yuvasi": "Servo yuvası", "Rulman yuvasi": "Rulman yuvası", "Boyun mili": "Boyun mili", "Egme catali": "Eğme çatalı",
      "Kafa iskeleti": "Kafa iskeleti", "Yuz kabugu (on) sag": "Yüz kabuğu (ön) sağ", "Yuz kabugu (on) sol": "Yüz kabuğu (ön) sol",
      "Arka kafa kabugu sag": "Arka kafa kabuğu sağ", "Arka kafa kabugu sol": "Arka kafa kabuğu sol",
      "Boyun yukseltme adaptoru": "Boyun yükseltme adaptörü", "Ekran tirnagi alt sag": "Ekran tırnağı alt sağ",
      "Ekran tirnagi alt sol": "Ekran tırnağı alt sol", "Ekran tirnagi ust sag": "Ekran tırnağı üst sağ", "Ekran tirnagi ust sol": "Ekran tırnağı üst sol",
      "MG996R servo": "MG996R servo (180°)", "25T aluminyum disk horn": "25T alüminyum disk horn",
      "M3x5 horn vidasi (servo ile)": "M3×5 horn vidası (servo ile gelir)", "625ZZ rulman 5x16x5": "625ZZ rulman 5×16×5",
      "6808-2RS rulman 40x52x7": "6808-2RS rulman 40×52×7", "M3 isil gomme somun": "M3 ısıl gömme somun",
      "M5 isil gomme somun": "M5 ısıl gömme somun", "M6 cekic somun (kanal 10)": "M6 çekiç somun (kanal 10)",
      "Boyun plakasi 3 mm Al (lazer/su jeti)": "Boyun plakası, 3 mm Al (lazer / su jeti)",
      "Vizor 3 mm siyah akrilik 190x115 (lazer)": "Vizör, 3 mm parlak siyah akrilik 190 × 115 (lazer)",
      "WaveShare 10.1HP-CAPQLED 10,1 in QLED 1280x720 HDMI kapasitif (kod 20789)": "WaveShare 10,1\" QLED 1280 × 720 HDMI (yüz ekranı, kod 20789)",
      "Raspberry Pi Camera Module 3": "Raspberry Pi Camera Module 3", "M2x8 PT vida (plastik icin)": "M2×8 PT vida (plastik için)",
      "M4 DIN 985 kontra somun": "M4 DIN 985 kontra somun",
      "Pan servosu kulagi": "Pan servosu kulağı → servo yuvası", "Boyun plakasi -> traverse": "Boyun plakası + servo yuvası → traverse",
      "Rulman yuvasi -> servo yuvasi": "Rulman yuvası → servo yuvası", "Boyun mili -> pan horn": "Boyun mili → pan horn'u",
      "Egme catali -> boyun mili": "Eğme çatalı → boyun mili flanşı", "Tilt servosu kulagi": "Tilt servosu kulağı → çatal",
      "Kafa iskeleti sag yanak -> tilt horn": "Kafa iskeleti sağ yanağı → tilt horn'u",
      "Tilt pimi (servo karsi yatagi)": "Tilt pimi (servo karşı yatağı, 625ZZ)", "Kafa kabugu -> kafa tablasi": "Kafa kabuğu → kafa tablası",
      "Ekran tirnagi -> yuz kabugu boss'u": "Ekran tırnağı → yüz kabuğu boss'u", "Ekran tirnagi -> cam seridi": "Ekran tırnağı → cam şeridi", "Kamera -> on kabuk boss'u": "Kamera → ön kabuk boss'u",
      "Eksen hizasi ve oturmalar": "Eksen hizası ve oturmalar"}


def tr(s):
    s = TR.get(s, s)
    return s.replace("x", "×") if (s[:1] == "M" and ("DIN" in s or "ISO" in s)) else s


def pay(x):
    cls = "ok" if x >= 2 else ("no" if x < 1.2 else "uy")
    return "<span class='%s'>%s×</span>" % (cls, sayi(x, 2))


# ---------------------------------------------------------------- ozetler
bag = d["baglanti_kontrol"]
bag_ok = sum(1 for b in bag if b["tamam"])
kontrol_n = sum(len(b["kontroller"]) for b in bag)
baski = d["baski"]
sigan = sum(1 for b in baski if b["sigar"])
destek = sum(1 for b in baski if b["desteksiz"])
ta = d["tarama"]
tmin, tmax = ta["serbest_tilt"]
pmin, pmax = ta["serbest_pan"]
TAR, PAR = K["tilt_aralik"], K["pan_aralik"]
tt, tp = d["tork"]["tilt"], d["tork"]["pan"]
r62 = d["r62"]
gr = d["grup"]
ev_cak = len(d["statik"])
bos_kp = min(v[0] for v in ta["bosluk_kafa_pan"].values())
bos_kp_a = min(ta["bosluk_kafa_pan"].items(), key=lambda kv: kv[1][0])
bos_kg = min(v[0] for v in ta["bosluk_kafa_govde"].values())
bag_min = d["bagil_bosluk"]["en_kucuk"][0] if d["bagil_bosluk"]["en_kucuk"] else [0, "-", "-"]
ms = tt["mesnet"]
OL = d["olcu"]

KARAR_TORK = ("**Tork (1,58 m):** tilt MG996R, tilt ±15° en kötü durumda %s kg·cm (yerçekimi %s + ivme %s; kafa grubu %s g, kablo payı dahil; "
              "kütle merkezi tilt ekseninden %s mm) → pay **%s×**; pan MG996R %s kg·cm (atalet + rulman + kablo, tahmini profil) → pay **%s×**. "
              "İki eksende de mevcut MG996R yeterli (ölçüt tilt ≥ 3,0, pan ≥ 2,0); kafa ağırlığı ve devirme momenti pan'da iki 6808-2RS'de, "
              "tilt'te 625ZZ pim ile horn arasında paylaşılıyor."
              % (sayi(tt["toplam_tilt15_kgcm"], 2), sayi(tt["statik_tilt15_kgcm"], 2), sayi(tt["ivme_kgcm"], 2), sayi(tt["kutle_g"], 1),
                 sayi(tt["am_eksen_mm"], 1), sayi(tt["pay_tilt15"], 2), sayi(tp["toplam_kgcm"], 2), sayi(tp["pay_iki_hane"], 2)))

BAGLANTI = [
    ("Boyun plakası + servo yuvası → traverse", "Plaka traversin üst yüzünde (y = 0), servo yuvasının kulak flanşı plakada; ikisi birlikte "
     "traversin üst kanalına sıkılır (kanal z = 0'da)", "2× M6×20 DIN 912 + DIN 125 pul + M6 çekiç somun (x = ±40)"),
    ("Pan servosu → servo yuvası", "Servo üstten girer, kulakları 7 mm kalın tablaya oturur", "4× M3×8 DIN 912 + pul + M3 ısıl gömme somun"),
    ("Rulman yuvası → servo yuvası", "Dört kulak servo yuvasının üst yüzüne oturur; iki 6808-2RS içinde", "4× M3×10 DIN 912 + M3 ısıl gömme somun"),
    ("6808-2RS × 2 → rulman yuvası / boyun mili", "Üst rulman dış bileziği yuva tablasına, iç bileziği mil omzunun altına (eksenel yük); alt rulman "
     "Ø52 yuvada pres (radyal); iç bilezikler Ø40 milde", "pres geçme (tolerans montajda ayarlanır)"),
    ("Boyun mili → pan horn'u", "Milin alt diski horn'a dayalı, cıvatalar milin içinden takılır", "4× M3×8 DIN 912 (horn dişli delik, kavrama 3,0 mm)"),
    ("Eğme çatalı → boyun mili", "Çatal tabanı mil flanşına dayalı", "4× M3×8 DIN 912 + M3 ısıl gömme somun (flanşta)"),
    ("Tilt servosu → eğme çatalı", "Servo +X'ten U kulak plakasına girer, kulakları plakaya dayalı", "4× M4×16 DIN 912 + M4 DIN 985 kontra somun"),
    ("Kafa iskeleti → tilt horn'u (sağ)", "Sağ yanak horn'a dayalı", "4× M3×8 DIN 912 (horn dişli delik)"),
    ("Kafa iskeleti ↔ eğme çatalı (sol, karşı yatak)", "625ZZ dış bileziği sol yanakta, iç bileziği M5 pimle çatal dayamasına sıkılı; "
     "yanak ile çatal arası 1 mm", "M5×12 DIN 912 + DIN 125 pul + M5 ısıl gömme somun"),
    ("Boyun yükseltme adaptörü → eğme çatalı / kafa iskeleti", "1,58 m'de baş 10,1\" kafaya göre yükseltildi (adaptör %s mm); dört saplama "
     "adaptörü boydan boya geçer" % sayi(OL["adaptor_h"], 1), "4× M3×73 DIN 976 saplama + M3 pul + M3 DIN 985 somun"),
    ("Kafa kabuğu (ön sağ/sol + arka sağ/sol) → kafa iskeleti tablası", "Dört kabuk yarısı (dikey dikiş + ön/arka dikiş); tabla rafı "
     "sağ/sol yanaklarda", "4× M3×10 tabla cıvatası + 9× kabuk cıvatası (M3×6 / M3×5 ISO 7380) + M3 ısıl gömme somun"),
    ("Yüz ekranı (10,1\" QLED) → ön kabuk", "Cam ön duvar iç yüzüne dayalı; vida deliği yok, 4 tırnak arkadan cam şeridine basar",
     "4× M3×6 ISO 7380 + M3 ısıl gömme somun + 1 mm köpük bant"),
    ("Kamera → ön kabuk", "PCB boss'lara dayalı, lens ekranın üstünde ortada", "4× M2×8 PT vida (plastik için, tahmini)"),
    ("Raspberry Pi 5 + Active Cooler → kafa tablası", "4× M2,5×8 pirinç burç", "alttan 4× M2,5×8, üstten 4× M2,5×5"),
    ("ReSpeaker Mic Array v2.0 → kafa tepesi", "Dizi kartı tepe duvarına dayalı (mikrofonlar yukarı)", "3× M2×8 PT vida"),
    ("USB ses kartı, PAM8403, SY8205, TVS, 5 V çevirici", "Kafa içinde (PAM8403 sol duvarda), köpük bantla", "1 mm çift taraflı köpük bant (VHB)"),
]

KARAR = [
    "**Yapı (1,58 m):** boyun plakası → pan MG996R → pan karşı yatağı → eğme çatalı + tilt MG996R → boyun yükseltme adaptörü → kafa iskeleti → "
    "yüz ve arka kabuk (sağ/sol yarılar) + 10,1\" QLED yüz ekranı + kamera + Pi 5 + ReSpeaker + ses (USB ses kartı + PAM8403). "
    "Boyun ve pan grubu 125 cm kafasıyla aynı geometri (`kafa7_parcalar`), baş `kafa10_lib`'den. Kafa kutusu %s × %s × %s mm (`arayuz.KAFA`)."
    % tuple(sayi(x, 0) for x in K["kafa_kutu"]),
    "**Boyun plakası:** 70 × 70 × 3 Al + iki yan kulak; 2× M6 traversin üst kanalına (x = ±40). Plaka kabuk üst kapağının altında "
    "(yerel y 0…3, kapak %s…%s)." % (sayi(r62["kapak_y_yerel"][0], 0), sayi(r62["kapak_y_yerel"][1], 0)),
    "**Pan karşı yatağı:** iki 6808-2RS (omuzdaki ile aynı rulman), merkezleri arası %s mm. Kafa ağırlığı mil omzundan üst rulmanın iç bileziğine, "
    "oradan yuva tablasına iner; devirme momenti iki rulmanda kuvvet çifti olur (her birinde ≈ %s N). Pan servosu yalnız döndürür; mil içi boş (Ø32), "
    "kablolar eksenden iner." % (sayi(tp["rulman"]["rulman_arasi_mm"], 0), sayi(tp["rulman"]["radyal_N"], 0)),
    "**Tilt karşı yatağı:** dirsekteki çözümün aynısı: sağda horn, solda 625ZZ + M5 pim. Kafa ağırlığı iki mesnet arasında bölünür: servo miline "
    "≈ %%%d (%s N) radyal yük kalır, pime %s N; eksenel yük ve devirme momenti yok (dirsekte de aynı durum). Mili tamamen boşaltmak istenirse "
    "seçenek: sağ yanağa ikinci rulman + horn'a esnek kaplin (karar Ahmet'in)." % (round(100 * ms["horn_payi"]), sayi(ms["horn_N"], 1), sayi(ms["pim_N"], 1)),
    "**Tilt ekseni kafanın içinde** (y = %s, z = %s; kafa altından %s mm yukarıda): kafa grubunun kütle merkezi eksenden %s mm uzakta, bu yüzden "
    "yerçekimi momenti küçük (tilt ±15°'de statik %s kg·cm); torkun çoğu ivmeden (%s kg·cm)."
    % (sayi(OL["tilt_y"], 1), sayi(OL["tilt_z"], 0), sayi(OL["tilt_y"] - K["kafa_alt_y"], 0), sayi(tt["am_eksen_mm"], 1),
       sayi(tt["statik_tilt15_kgcm"], 2), sayi(tt["ivme_kgcm"], 2)),
    "**Boyun gövdesi iki parça:** pan servosu kulaklarıyla (53,6 mm) Ø52 rulman yuvasından geçemediği için servo yuvası ve rulman yuvası ayrı basılır, "
    "4× M3 ile birleşir. Servo kulakları tablanın üstüne oturur (destek gerektiren tavan yok).",
    "**Kafa kabuğu:** 2,5 mm duvar, dört parça: ön ve arka, her biri sağ/sol yarı (X2D tablasına sığması için dikey dikiş); yarılar dikiş dili ve "
    "M3 ISO 7380 kabuk cıvatalarıyla birleşir. Yüz kabukları yüz üstü, arka kabuklar sırt üstü basılır.",
    "**Yüz ekranı yuvası:** QLED camı ön duvarın iç yüzüne dayanır; pencere %s × %s mm, görünen alanın her yanında %s mm kabuk payı; tırnaklar cam "
    "şeridine %s mm basar." % (sayi(d["qled"]["pencere"][0], 1), sayi(d["qled"]["pencere"][1], 1), sayi(d["qled"]["gorunen_kabuk_pay_mm"], 1),
                                sayi(d["qled"]["tirnak"]["dil_cam_seridi_mm"], 1)),
    "**Kamera:** ekranın üstünde, kafa ortasında; ekrana boşluk %s mm (`kafa-analiz.json` qled.bosluk)." % sayi(d["qled"]["bosluk"]["ekran_kamera"], 1),
    "**Kütleler:** MG996R 55 g (datasheet), QLED 600 g (**varsayım**; üretici net kütle vermiyor, satıcı brüt 0,81–0,862 kg), kamera 4 g, PETG küçük parçalarda "
    "%%%d, kabuklarda %%%d etkin doluluk (**tahmini**). Tork kütlesine kablo payı %s g ve kafa içi kablo/fiş kalemleri eklenir (tahmini)."
    % (round(100 * d["doluluk"]), round(100 * d["doluluk_kabuk"]), sayi(tt["kablo_payi"]["kutle_g"], 0)),
    "**Tork varsayımları (tahmini):** %s; MG996R 9,4 kg·cm @4,8 V; rulman sürtünme katsayısı 0,0015; kablo halkası direnci ≈ 0,3 kg·cm." % d["tork"]["profil"],
    "**Tahmini ölçüler:** Camera Module 3 delik dizisinin dikey yeri, QLED toplam kalınlık 15,03 (STEP 14,38), fiş zarfları, USB ses kartı ve PAM8403 "
    "ölçüleri, M2 PT vida ve PETG'ye vida kavraması, 25T horn yüksekliği (dirsekle aynı).",
]

SIRA = [
    "Isıl gömme somunları bas: servo yuvası (4 tabla + 4 üst), boyun mili flanşı (4), eğme çatalı (M5), tabla rafları (4), kabuk dikişleri, "
    "ön kabuk tırnak boss'ları (4).",
    "Pan servosunun horn'unu servo orta konumunda (90) tak; servoyu servo yuvasına üstten indir, 4× M3×8 + pul.",
    "Alt 6808'i rulman yuvasına alttan, üst 6808'i üstten tablaya kadar pres et; rulman yuvasını 4× M3×10 ile servo yuvasına bağla.",
    "Boyun milini üstten iki rulmandan geçir; diski horn'a oturunca 4× M3×8'i milin içinden sık (gerekirse servo kulaklarının altına ince pul: "
    "mil omzu rulmanda otururken servo milini eksenel itmemeli).",
    "Eğme çatalını flanşa 4× M3×8 ile bağla; tilt servosunu +X'ten U plakaya 4× M4×16 + kontra somun (horn servo ortasında).",
    "625ZZ'yi kafa iskeletinin sol yanağına pres et; iskeleti indir, sağ yanağı horn'a 4× M3×8, sol pimi M5×12 + pul ile sık; boyun yükseltme "
    "adaptörünü 4× M3×73 saplamayla bağla.",
    "Boyun grubunu traverse oturt: 2× M6×20 + pul + çekiç somun (somunlar traversin üst kanalında, uzun kenarı kanala dik).",
    "Pi 5'i burçlara, ReSpeaker'ı tepeye, ses kartı / PAM8403 / SY8205 / TVS'yi köpük bantla yerleştir; QLED'i ön kabuğa oturt, 4 tırnakla "
    "(4× M3×6 + köpük bant) arkadan tut, kamerayı (4× M2×8) tak; kabloları zarflarda gösterilen yollardan geçir (pan ±90 ve tilt için gevşek halka).",
    "Arka kabuk yarılarını, sonra ön kabuk yarılarını yerleştir; tabla cıvataları (4× M3×10) ve kabuk cıvataları (M3 ISO 7380).",
]

ACIK = [
    "**K4 (14-15 Ekim 2026): Pi 5 kafada.** Kamera FPC 300 mm ve micro HDMI → HDMI 25–30 cm kafa içinde kalır; boyundan HDMI ve CSI geçmez. "
    "Isı testi (kafa kapalı, stres): SoC ≤ 75 °C, tilt servosu gövdesi ≤ 50 °C. Active Cooler debisi üreticiden yok (varsayım 1,0–1,55 L/s); yarıklı tahmin bir aralık (doğal çekiş ile fanın tam katkısı arası), test şart. Aşılırsa üst bant arkasına 25–30 mm egzoz fanı.",
    "**Ses:** mikrofon dizisi (ReSpeaker) kafa tepesinde, USB ses kartı + PAM8403 kafada (PAM8403 sol duvarda); hoparlör gövdede (kabuk, "
    "göğüs bandı arkası). Mikrofon–hoparlör uzaklığı `lale158/kafa-yerlesim/uygulama-olcum.json` (ölçüt ≥ 400 mm).",
    "**AI HAT+ (K2, karar Ahmet'te):** ana modelde yok. Pi 5 üstüne yığın arka üst dikiş boss'uyla çakışıyor; iki seçenek "
    "`lale158/kafa-yerlesim/hat_secenek.py` ile ölçüldü (`hat-secenek-a/b.json`, F1a raporu).",
    "Pi 5 için 4× M2,5 burç deliği tablada: alt vida burca girer (kupon testinde sıkma kontrolü).",
    "6808-2RS ve 625ZZ yük değerleri üretici kataloğundan doğrulanmalı (burada yalnız kuvvetler hesaplandı; değerler çok küçük).",
    "QLED kütlesi, cam şeridi kalınlığı (STEP 0,9 mm), fiş boyları, kamera delik yerleri parça gelince kumpas / tartı ile doğrulanmalı.",
    "Pan servosunun eksenel konumu: montajda ince pulla ayar; servo milinin eksenel yük almadığı elle kontrol edilmeli.",
    "Tilt'te servo miline kalan radyal pay (≈ %s N) kabul edilecek mi, yoksa sağ yanağa ikinci rulman + esnek kaplin mi (seçenek)." % sayi(ms["horn_N"], 1),
    "Yazılım sınırları: pan %s…%s°, tilt %s…%s° (`arayuz.KAFA`); servo horn'ları orta konumda = ev pozu." % (sayi(PAR[0], 0), sayi(PAR[1], 0),
                                                                                                    sayi(TAR[0], 0), sayi(TAR[1], 0)),
    "@@YASAK@@",
    "Pan fareyle zor sürükleniyor (boyun mili kafanın altında, eksene ≈ 20 mm): FreeCAD'de pan için simülasyon ya da betik kullan.",
]

# ---------------------------------------------------------------- 2. asama (moduller arasi tarama + ana montaj)
def _js(*yol):
    f = os.path.join(UST, *yol)
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


CRP = _js("carpisma-sonuc.json")
KT = (CRP or {}).get("kafa_tarama")
MA = _js("montaj", "montaj-analiz.json")
ED = _js("montaj", "eklem-dogrulama.json")
GK = _js("montaj", "gui-kontrol.json")
KOLAD = {"sag": "Sağ kol", "sol": "Sol kol"}
KATAD = {"omuz": "omuz (göbek + üst kol)", "dirsek catali": "dirsek çatalı", "on kol": "ön kol", "el": "el"}


def yasak_metni():
    """Acik isler maddesi: yasak bolge carpisma-sonuc.json'dan (sinir turlariyla 5 derece kesinlikte)."""
    ks = (KT or {}).get("kol") or {}
    oz = [(t, g, o) for t, k in ks.items() for g, o in (k.get("yasak_ozet") or {}).items()]
    if not oz:
        return "**Kafa-kol yasak pozu:** tarama yasak bölge bulmadı (ya da kafa taraması yok)."
    t, g, o = oz[0]
    yak = all(k.get("sinir_yakinsadi") for k in ks.values())
    return ("**Kafa-kol yasak pozu yazılımda:** kol öne %s…%s°, yana %s…%s°, dirsek %s…%s° (el yüzün önünde) iken kafa o kola doğru pan %s…%s° "
            "(sol kolda işaret ters) ve tilt %s…%s° birlikte verilmemeli (%s). Sınır, çakışan her çiftin eksen komşuları 5° (bilek 15°) adımla "
            "taranarak %s; satır satır sınırlar aşağıdaki yasak bölge tablosunda. Yazılımda bir adım (5°) pay bırak." % (
                sayi(o["kol_min"][0], 0), sayi(o["kol_max"][0], 0), sayi(o["kol_min"][1], 0), sayi(o["kol_max"][1], 0),
                sayi(o["kol_min"][2], 0), sayi(o["kol_max"][2], 0), sayi(min(abs(x) for x in o["pan"]), 0), sayi(max(abs(x) for x in o["pan"]), 0),
                sayi(o["tilt"][0], 0), sayi(o["tilt"][1], 0), ", ".join(o["parcalar"][:2]),
                "kesinleşti (yakınsadı: sağ %s, sol %s tur)" % (ks["sag"].get("sinir_tur"), ks["sol"].get("sinir_tur")) if yak
                else "YAKINSAMADI (tur sınırı); sınır belirsiz"))


ACIK = [yasak_metni() if x == "@@YASAK@@" else x for x in ACIK]


def kpoz(p):
    if not p:
        return "her pozda (sabit boyun)"
    return "pan %s°" % sayi(p[0], 0) + (", tilt %s°" % sayi(p[1], 0) if len(p) > 1 else "")


def kolpoz(p):
    ad = ("öne", "yana", "dirsek", "bilek")
    return " ".join("%s %s°" % (ad[i], sayi(v, 0)) for i, v in enumerate(p))


def img64m(ad):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(UST, "montaj", "gorsel", ad), "rb").read()).decode()


def araliklar(vs, adim=5):
    """[-90,-85,...,-60, 30, 35] -> '-90...-60°, 30...35°'"""
    vs = sorted(set(vs))
    if not vs:
        return "–"
    out, a, b = [], vs[0], vs[0]
    for v in vs[1:]:
        if v - b <= adim + 1e-6:
            b = v
        else:
            out.append((a, b))
            a = b = v
    out.append((a, b))
    return ", ".join(("%s°" % sayi(x, 0)) if x == y else "%s…%s°" % (sayi(x, 0), sayi(y, 0)) for x, y in out)


def asama2():
    h = []
    if not KT:
        h.append("<div class='bos'>carpisma.py kafa taraması henüz çalıştırılmadı.</div>")
        return h
    sb = KT["sabit"]
    ksum = KT["kol"]
    top_ar = sb["cakisan_alt_poz_aralikta"] + sum(k["cakisan_cift_aralikta"] for k in ksum.values())
    top_di = sb["cakisan_alt_poz_aralik_disi"] + sum(k["cakisan_cift_aralik_disi"] for k in ksum.values())
    n_kol = list(ksum.values())[0]["kol_pozu"]
    n_yak = sum(k["kafaya_yakin_tam_kol_pozu"] for k in ksum.values())
    n_tam = sb["tam_olcum"] + sum(k["tam_olcum"] for k in ksum.values())
    h.append("<p><b>Kapsam (<code>carpisma.py</code> bölüm 4b):</b> kafa pan %s…%s° × tilt %s (kaba, 15°; eklem aralığı pan %s…%s°, tilt %s…%s°; "
             "pan ±90° ötesi ve tilt 40° aralık dışı olarak ayrıca sayıldı) = <b>%d kafa pozu</b>. Her kolda kol zinciri kaba ızgarası (öne −45…135°, "
             "yana 0…120° 15° adımla, dirsek 0/30/60/90/105°, bilek −90/0/90°) + %d jest pozu (ev, selam, kafa kaşıma, el yüze/ağıza, kol tepede) = "
             "<b>%d kol pozu</b>, hepsi kafa pozlarıyla birlikte; sıkı sınır kutusu ön elemesinde dirseği kafaya %s mm'den yakın gelen kol pozu "
             "sağ + sol %d. Eklem aralığında çakışan ya da 5 mm altında kalan çiftlerin çevresi 5° adımla yeniden tarandı (kafa pan/tilt ±5/10°, "
             "kol ±5/10°, bilek ±15°); ardından yasak bölgenin sınırı: çakışan her çiftin eksen komşuları (5°, bilek 15°) yeni çakışma kalmayana dek "
             "ölçüldü (sağ %s, sol %s tur). Toplam %d tam ölçüm, %s s. Hedefler: iskelet, kabuk (üst kapak R62 halkası dahil), iki omuzun gövdesi, "
             "göbeği ve üst kolu, iki kolun dirsek çatalı, ön kolu ve eli; kafanın sabit boynu (gövde) da her kol pozunda sınandı. "
             "Kablo demeti gösterimi hariç.</p>" % (
                 sayi(KT["kaba"]["pan"][0], 0), sayi(KT["kaba"]["pan"][-1], 0), esc(KT["kaba"]["tilt"]), sayi(KT["aralik"]["pan"][0], 0),
                 sayi(KT["aralik"]["pan"][1], 0), sayi(KT["aralik"]["tilt"][0], 0), sayi(KT["aralik"]["tilt"][1], 0),
                 sb["kaba"]["poz"], len(KT["jest"]), n_kol, sayi(KT["lim_mm"], 0), n_yak, ksum.get("sag", {}).get("sinir_tur", "–"),
                 ksum.get("sol", {}).get("sinir_tur", "–"), n_tam, sayi(KT["sure_s"], 0)))
    h.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in [
        ("%d" % top_ar, "eklem aralığında çakışma (kafa × sabit modüller %d alt poz + kafa × kollar %d poz çifti)" % (
            sb["cakisan_alt_poz_aralikta"], sum(k["cakisan_cift_aralikta"] for k in ksum.values()))),
        ("%d" % top_di, "eklem aralığı dışında (bilgi; eklem sınırları engelliyor)"),
        ("%d" % sum(k["yasak_sayi"] for k in ksum.values()), "yasak kol alt pozu (kafa belirli açılara dönmemeli)"),
    ]) + "</div>")
    sat = []
    for m, b in sorted(sb["en_kucuk_aralikta"].items(), key=lambda kv: kv[1]["bosluk_mm"]):
        ad = m.replace("omuz_sag govde", "sağ omuz gövdesi").replace("omuz_sol govde", "sol omuz gövdesi").replace("(kafa govdesi)", "(kafanın sabit boynu)")
        sat.append([esc(ad), sayi(b["bosluk_mm"], 1) + " mm", esc("%s ↔ %s" % (b["parca"], b["hedef"])), esc(kpoz(b["kafa_poz"])), "–"])
    for t, k in ksum.items():
        for c, b in sorted(k["en_kucuk_aralikta"].items(), key=lambda kv: kv[1]["bosluk_mm"]):
            cak = b["hacim_mm3"] > 0.5 or b["hacim_mm3"] < 0
            sat.append([esc("%s: %s" % (KOLAD[t], KATAD.get(c, c))),
                        ("<span class='no'>çakışma %s mm³</span>" % sayi(b["hacim_mm3"], 0)) if cak else sayi(b["bosluk_mm"], 1) + " mm",
                        esc("%s ↔ %s" % (b["parca"], b["kafa_parca"])), esc(kpoz(b["kafa_poz"])), esc(kolpoz(b["kol_poz"]))])
    h.append("<h3>En küçük boşluklar (eklem aralığında)</h3><div class='tw'>" +
             tablo(["Hedef", "En küçük boşluk", "Parça çifti", "Kafa pozu", "Kol pozu"], sat) + "</div>")
    h.append("<p class='not'>Kafanın sabit boynu traverse oturuyor: boyun plakası ve çekiç somunlar traversle temaslı (0 mm, tasarım gereği; ev pozunda "
             "çakışma yok). Ölçülmeyen çiftlerin boşluğu ≥ %s mm (sıkı sınır kutusu: parçanın tessellation noktaları poz matrisiyle taşınıyor).</p>"
             % sayi(KT["lim_mm"], 0))
    ys = [(t, y) for t, k in ksum.items() for y in k["yasak"]]
    if ys:
        oz = []
        for t, k in ksum.items():
            for g, o in sorted((k.get("yasak_ozet") or {}).items()):
                oz.append([KOLAD[t], esc(g), "%d" % o["kol_alt_poz"],
                           esc(" · ".join("%s %s…%s°" % (n, sayi(a_, 0), sayi(b_, 0)) for n, a_, b_ in
                                          zip(("öne", "yana", "dirsek", "bilek"), o["kol_min"], o["kol_max"]))),
                           "her kafa pozu" if o["kafa_tum_pozlar"] else esc(("pan %s…%s°" % (sayi(o["pan"][0], 0), sayi(o["pan"][1], 0)) if o["pan"] else "")
                                                                            + (", tilt %s…%s°" % (sayi(o["tilt"][0], 0), sayi(o["tilt"][1], 0)) if o["tilt"] else "")),
                           esc(", ".join(o["parcalar"][:3]))])
        h.append("<h3>Kafa-kol yasak poz bölgeleri</h3>")
        if oz:
            h.append("<div class='tw'>" + tablo(["Kol", "Grup", "Çakışan alt poz", "Kol açıları (zarf)", "Kafa açıları (zarf)", "Çakışan çift"], oz) + "</div>")
        kural = [(t, r) for t, k in ksum.items() for r in (k.get("yasak_kural") or [])]
        if kural:
            ks_ = []
            for t, r in kural:
                ks_.append([KOLAD[t], "%s°" % sayi(r["one_arka"], 0), "%s°" % sayi(r["yana"], 0), "%s°" % sayi(r["dirsek"], 0),
                            esc(araliklar(r["bilek"], 15)), "her kafa pozu" if r["kafa_tum_pozlar"] else
                            esc("pan %s…%s°" % (sayi(r["pan"][0], 0), sayi(r["pan"][1], 0)) if r["pan"] else "–"),
                            esc("%s…%s°" % (sayi(r["tilt"][0], 0), sayi(r["tilt"][1], 0)) if r["tilt"] else "–")])
            h.append("<details open><summary>Yasak bölge tablosu (kol öne / yana / dirsek başına; 5° kesinlikte, %d satır)</summary><div class='tw'>" % len(ks_) +
                     tablo(["Kol", "Öne", "Yana", "Dirsek", "Bilek (çakışan)", "Kafa pan", "Kafa tilt"], ks_) + "</div></details>")

        def kafa_yaz(y):
            if y["kafa_tum_pozlar"]:
                return "her kafa pozunda"
            pt = {}
            for x in y["yasak_kafa_poz"]:
                pt.setdefault(x[0], []).append(x[1] if len(x) > 1 else None)
            return "; ".join("pan %s°%s" % (sayi(pn, 0), (" (tilt %s)" % araliklar([v for v in tl if v is not None]))
                                            if any(v is not None for v in tl) else "") for pn, tl in sorted(pt.items()))
        sat = []
        for t, y in ys[:24]:
            sat.append([KOLAD[t], esc(kolpoz(y["kol_poz"])) + " <span class='not'>(%s)</span>" % esc(y["kol_grup"]),
                        esc(kafa_yaz(y)), esc(", ".join(y["parcalar"][:3]))])
        h.append("<details><summary>Çakışan alt pozlar (ilk %d / %d)</summary><div class='tw'>" % (len(sat), len(ys)) +
                 tablo(["Kol", "Kol alt pozu", "Kafa bu açılara dönmemeli", "Çakışan çift"], sat) + "</div></details>" +
                 "<p class='not'>Kol alt pozu: öne/yana (üst kol), + dirsek (ön kol), + bilek (el); listedeki alt poz bütün devamlarıyla geçerli. "
                 "Robot yazılımı bu kol pozlarında kafa açısını sınırlamalı (ya da kafayı önce ev pozuna alıp sonra kolu kaldırmalı).</p>")
    else:
        h.append("<p class='karar'><b>Yasak poz bölgesi yok:</b> eklem aralığındaki hiçbir kol pozu × kafa pozu birleşiminde kafa kollarla, omuzlarla, "
                 "kabukla ya da iskeletle çakışmıyor. Yazılımda kafa için ek, kola bağlı sınır gerekmiyor.</p>")
    sat = []
    for t, k in ksum.items():
        for j in k["jest"]:
            b = j["en_kucuk"]
            sat.append([KOLAD[t], esc(j["ad"]), esc(kolpoz(j["poz"])), (sayi(b["bosluk_mm"], 1) + " mm") if b else "> %s mm" % sayi(KT["lim_mm"], 0),
                        esc("%s ↔ %s, %s" % (b["parca"], b["kafa_parca"], kpoz(b["kafa_poz"]))) if b else "–",
                        esc("; ".join(kpoz(x) for x in j["cakisan_kafa_poz"][:6])) or "yok"])
    h.append("<h3>Jest pozları</h3><div class='tw'>" + tablo(["Kol", "Jest", "Kol pozu", "Kafaya en küçük boşluk (kafa aralıkta)", "Çift, kafa pozu",
                                                            "Çakışan kafa pozu"], sat) + "</div>")
    if top_di:
        h.append("<p class='not'>Aralık dışı çakışmalar (pan ±90° ötesi, tilt 40° ya da kol komşuluğu): sabit hedeflerle %d alt poz, kollarla %d poz "
                 "çifti; eklem sınırları bunları engelliyor.</p>" % (sb["cakisan_alt_poz_aralik_disi"],
                                                                      sum(k["cakisan_cift_aralik_disi"] for k in ksum.values())))
    if MA:
        km = next((m for m in MA["moduller"] if m["ad"] == "kafa"), None)
        ej = [j for j in MA["eklemler"] if j.get("modul") == "kafa"]
        ek = "; ".join(("%s (döner, %s…%s°)" % (j["etiket"], sayi(j["sinir"][0], 0), sayi(j["sinir"][1], 0))) if j["tip"] == "Revolute"
                       else "%s (sabit)" % j["etiket"] for j in ej)
        kam = km["agirlik_merkezi"] if km else (0, 0, 0)
        h.append("<h3>Ana montaj</h3>")
        h.append("<p><code>montaj/robot-montaj.FCStd</code>: kafa üç grup (sabit boyun traverse sabit, pan grubu, kafa) ve %d eklem: %s. Kafa %d parça, "
                 "%s g, AM (%s; %s; %s) mm (global). Robot toplamı %d parça, <b>%s kg</b>, AM (%s; %s; %s) mm (tam robot, taban dahil; kablo payı hariç).</p>" % (
                     len(ej), esc(ek), km["parca"] if km else 0, sayi(km["kutle_g"], 1) if km else "–", sayi(kam[0], 1), sayi(kam[1], 1),
                     sayi(kam[2], 1), MA["parca_sayisi"], sayi(MA["kutle_g"] / 1000, 2), sayi(MA["agirlik_merkezi"][0], 1),
                     sayi(MA["agirlik_merkezi"][1], 1), sayi(MA["agirlik_merkezi"][2], 1)))
    if ED:
        kv = [v for v in ED["vakalar"] if "kafa" in v["komut"]]
        if kv:
            yk = [y for y in ED["yon"] if y["kol"] == "kafa"]
            h.append("<p><b>Eklem doğrulaması:</b> pan ve tilt Assembly simülasyonuyla %d pozda sürüldü (%d'i iki kolla birlikte); çözücünün kafa "
                     "gruplarının yerleşimi <code>kafa_parcalar.grup_yer</code> ile en çok <b>%.1e mm / %.1e°</b> sapıyor. Yön: %s.</p>" % (
                         len(kv), sum(1 for v in kv if len(v["komut"]) > 1), max(v["max_mm"] for v in kv), max(v["max_derece"] for v in kv),
                         esc("; ".join("%s +%s° %s" % (y["eklem"], sayi(y["aci"], 0), "doğru" if y["dogru"] else "YANLIŞ") for y in yk))))
    if GK and GK.get("kafa_surukleme"):
        ks = GK["kafa_surukleme"]
        h.append("<p><b>GUI:</b> pan ve tilt eklemleri görünür ve seçilebilir; fareyle sürükleme (montaj_gui_kontrol.py): %s.</p>" % esc("; ".join(
            "%s → pan %s°, tilt %s°" % (x["aciklama"], sayi(x["sonra"]["pan"][0], 0), sayi(x["sonra"]["tilt"][0], 0)) for x in ks)))
    fig = [(a, c) for a, c in (("montaj-kafa.png", "Ana montajda kafa (ev pozu)"),
                              ("montaj-poz-kafa.png", "Ana montaj: kafa pan −60°, tilt 20°; sağ kol öne 45°, yana 20°, dirsek 60°"),
                              ("montaj-gui-kafa.png", "GUI: kafa fareyle sürüklendi (pan)"))
           if os.path.exists(os.path.join(UST, "montaj", "gorsel", a))]
    if fig:
        h.append("<div class='grid'>" + "".join("<figure><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (img64m(a), esc(c), esc(c))
                                                for a, c in fig) + "</div>")
    return h


# ---------------------------------------------------------------- HTML
H = []
H.append("""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kafa Modülü 1,58 m</title><style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1f22;--mut:#666;--line:#e3e0d8;--acc:#7b8794;--acc2:#2f86d4;--ok:#2e8b57;--no:#c0392b;--uy:#b7791f}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#202226;--ink:#ececec;--mut:#9a9a9a;--line:#33363b}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:2px solid var(--acc2);display:inline-block}
h3{font-size:16px;margin:18px 0 8px}.sub{color:var(--mut);margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
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
H.append("<h1>Kafa modülü (1,58 m): boyun + pan + tilt + 10,1\" yüz ekranı</h1>")
H.append(__import__("carpisma_kos").eskime_html())   # C6: carpisma-sonuc.json eskidiyse uyari kutusu (bos dize = guncel)
H.append("<div class='sub'>1. aşama (tasarım) + 2. aşama (modüller arası, ana montaj) · FreeCAD 1.1 · <code>kafa_montaj.py</code> · %d parça (%d baskı) · ölçüler <code>arayuz.KAFA</code>'dan, "
         "boyun/pan 125 cm ile aynı, baş 10,1\" QLED (<code>kafa10_lib</code>) · yazıcı %s · 2. aşama: modüller arası tarama (<code>carpisma.py</code>) ve ana montaj (<code>montaj/</code>) aşağıda</div>"
         % (d["parca_sayisi"], d["baski_sayisi"], esc(Y["model"])))
kpi = [
    ("%d / %d" % (d["baski_sayisi"], d["parca_sayisi"]),
     "baskı / toplam parça · hepsi geçerli, tek katı" if not d["gecersiz"] and not d["coklu_kati"] else "GEÇERSİZ PARÇA VAR"),
    ("%d" % ev_cak, "ev pozunda modül içi çakışma (%d çift sınandı, > 0,5 mm³)" % d["cift_sayisi"]),
    ("%d / %d" % (bag_ok, len(bag)), "bağlantı kontrolü (%d tekil ölçüt): dayanma, eksen hizası, cıvata ucu / kavrama" % kontrol_n),
    ("%s…%s°" % (sayi(PAR[0], 0), sayi(PAR[1], 0)), "pan (MG996R 180°) · tarama ±180°'de serbest: %s…%s°" % (sayi(pmin, 0), sayi(pmax, 0))),
    ("%s…%s°" % (sayi(TAR[0], 0), sayi(TAR[1], 0)), "tilt yazılım sınırı (+ öne eğme) · tarama %s…%s° serbest, sınırda en az %s mm"
     % (sayi(tmin, 0), sayi(tmax, 0), sayi(bos_kp, 1))),
    ("%d / %d" % (sigan, len(baski)), "X2D'ye sığan baskı parçası · desteksiz %d / %d" % (destek, len(baski))),
    ("%s g" % sayi(tt["kutle_g"], 1), "kafa grubu (tilt ekseninde döner; parçalar %s g + kablo payı ve kafa içi kablolar, tork kütlesi)"
     % sayi(tt["kutle_parca_g"], 1)),
    ("%s g" % sayi(d["kutle_g"], 1), "modül toplamı (parçalar) · kafa %s g, pan grubu %s g, boyun %s g" % (sayi(gr["Kafa"]["m"], 1), sayi(gr["Pan"]["m"], 1),
                                                                                                       sayi(gr["Govde"]["m"], 1))),
    ("%s×" % sayi(tt["pay_tilt15"], 2), "tilt MG996R payı, tilt ±15° (%s kg·cm, yerçekimi + ivme; ölçüt ≥ 3,0)" % sayi(tt["toplam_tilt15_kgcm"], 2)),
    ("%s×" % sayi(tp["pay_iki_hane"], 2), "pan MG996R payı (%s kg·cm, atalet + sürtünme, tahmini; ölçüt ≥ 2,0)" % sayi(tp["toplam_kgcm"], 2)),
    ("r %s / %s" % (sayi(r62["kapak_seviyesi_r_max"], 1), sayi(r62["aciklik_r"], 0)),
     "kabuk kapağı seviyesinde boyunun en büyük yarıçapı / R62 açıklık · halkaya en az %s mm" % sayi(r62["sabit_en_kucuk"][0][0], 1)),
]
H.append("<div class='k'>" + "".join("<div class='kpi'><b>%s</b><span>%s</span></div>" % (a, esc(b)) for a, b in kpi) + "</div>")
H.append("<p class='karar'>%s</p>" % md(KARAR_TORK))

H.append("<h2>Görünümler</h2><div class='grid'>")
for ad, cap, w in (("kafa-izometrik.png", "İzometrik: kafa modülü + bağlam (traversin orta bölümü, kabuk üst kapağı R62 halkası yarı saydam)", ""),
                   ("kafa-on.png", "Önden (yüz): 10,1\" QLED penceresi, kamera", ""),
                   ("kafa-yan.png", "Yandan (+X): boyun, rulman yuvası, kafa", ""),
                   ("kafa-arka.png", "Arkadan: arka kabuk yarıları, havalandırma yarıkları", ""),
                   ("kafa-boyun-yakin.png", "Boyun mekanizması (kafa grubundan yalnız iskelet yarı saydam, tilt horn'u, 625ZZ): pan, çatal, tilt servosu, adaptör", ""),
                   ("kafa-boyun-yakin-arka.png", "Boyun mekanizması arkadan: 625ZZ karşı yatağı (sol yanak), M5 pim", ""),
                   ("kafa-kesit-pan.png", "Pan ekseni kesiti (x = 0): servo yuvası, pan servosu, iki 6808, boyun mili, çatal, tilt servosu, kafa", ""),
                   ("kafa-kesit-pan-yakin.png", "Pan yatağı yakın: mil omzu → üst 6808 iç bileziği → yuva tablası; alt 6808", ""),
                   ("kafa-kesit-tilt.png", "Tilt ekseni kesiti (z = %s): sağda horn + yanak, solda 625ZZ + M5 pim; üstte tabla, Pi 5, ReSpeaker" % sayi(OL["tilt_z"], 0), ""),
                   ("kafa-kablo-yolu.png", "Kafa içi yerleşim (kabuk saydam, ekran gizli); kırmızı: yer ayırma zarfları (fiş, kablo yolu, fan yeri)", ""),
                   ("kafa-yerlesim-ust.png", "Üstten: tabla üstü yerleşim ve zarflar", ""),
                   ("kafa-patlatilmis.png", "Patlatılmış: boyun (gövde), pan grubu, kafa grubu (baş tek blok kaldırılmış)", "")):
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure class='%s'><img src='%s' alt='%s'><figcaption>%s</figcaption></figure>" % (w, img64(ad), esc(cap), esc(cap)))
H.append("</div>")
H.append("<h3>Pan / tilt pozları</h3><div class='grid4'>")
for psi, th in ((45, 0), (-60, 10), (0, 13), (0, -13), (90, 0)):   # kafa_gorsel.POZ ile ayni
    ad = "kafa-poz-pan%+03d-tilt%+03d.png" % (psi, th)
    if os.path.exists(os.path.join(G, ad)):
        H.append("<figure><img src='%s' alt='poz'><figcaption>Pan %+d°, tilt %+d°</figcaption></figure>" % (img64(ad), psi, th))
H.append("</div>")

H.append("<h2>Yapı</h2><ul>")
H.append("<li><b>Boyun (gövdeye sabit)</b>: boyun plakası, servo yuvası, rulman yuvası, pan MG996R gövdesi, iki 6808 dış bileziği · %s g</li>" % sayi(gr["Govde"]["m"], 0))
H.append("<li><b>Pan grubu</b> (dikey eksende döner): pan horn'u, boyun mili, 6808 iç bilezikleri, eğme çatalı, tilt MG996R, 625ZZ iç bileziği + M5 pim · %s g</li>"
         % sayi(gr["Pan"]["m"], 0))
H.append("<li><b>Kafa grubu</b> (tilt ekseninde döner): tilt horn'u, kafa iskeleti, 625ZZ dış bileziği, yüz ve arka kabuk (sağ/sol), 10,1\" QLED, tırnaklar, kamera, "
         "Pi 5 + Active Cooler, ReSpeaker, USB ses kartı, PAM8403, SY8205, TVS, 5 V çevirici · %s g, "
         "kütle merkezi (%s; %s; %s)</li>" % (sayi(gr["Kafa"]["m"], 0), *[sayi(x, 1) for x in gr["Kafa"]["am"]]))
H.append("<li>Pan ekseni yerel Y ekseni (x = z = 0; kabuk R62 açıklığının merkezi), pan horn'u y = %s. Tilt ekseni X'e paralel, (y, z) = (%s, %s). "
         "Yerel orijin = traversin üst yüzünün ortası (global 0, %s, 0).</li>" % (sayi(K["pan_nokta"][1], 1), sayi(K["tilt_nokta"][1], 0),
                                                                                  sayi(K["tilt_nokta"][2], 0), sayi(K["taban_y"], 0)))
H.append("</ul>")

H.append("<h2>Parça listesi</h2><div class='tw'>")
TUR = {"Baski": "Baskı (PETG)", "Satin": "Satın alınan", "Baglanti": "Bağlantı elemanı", "Imalat": "İmalat (Al / akrilik)"}
SIRA_T = {"Baski": 0, "Imalat": 1, "Satin": 2, "Baglanti": 3}
rows = [(TUR.get(t, t), esc(tr(k)), n, sayi(m, 1)) for t, k, n, m in sorted(d["bom"], key=lambda r: (SIRA_T.get(r[0], 9), r[1]))]
H.append(tablo(["Tür", "Kalem", "Adet", "Kütle (g)"], rows, "sayi") + "</div>")
H.append("<p class='not'>CSV: <code>kafa-bom.csv</code>. Bütçe karşılaştırması bu raporda yapılmadı (maliyet: <code>planlama/maliyet.json</code>).</p>")

H.append("<h2>Hangi parça neye, nasıl bağlanıyor</h2><div class='tw'>")
H.append(tablo(["Bağlantı", "Nasıl oturuyor", "Bağlantı elemanı"], [(esc(a), esc(b), esc(c)) for a, b, c in BAGLANTI]) + "</div>")
H.append("<h3>Bağlantı kontrolleri (<code>kafa_montaj.py</code>)</h3><div class='tw'>")
rows = []
for b in bag:
    olc = "; ".join(esc(x[0]) for x in b["kontroller"][:4]) + (" …" if len(b["kontroller"]) > 4 else "")
    hata = [x[0] for x in b["kontroller"] if not x[2]]
    rows.append((esc(tr(b["ad"])), len(b["kontroller"]), OK if b["tamam"] else NO + " " + esc("; ".join(hata)), "<span class='not'>%s</span>" % olc))
H.append(tablo(["Bağlantı", "Ölçüt", "Sonuç", "Örnek ölçütler"], rows) + "</div>")
H.append("<p class='not'>Ölçütler: bağlantı elemanı tasarım ekseninde (sapma &lt; 10⁻⁶ mm); baş, pul, somun ve ısıl gömme somun yüzeye dayalı (≤ 0,01 mm); "
         "cıvata deliğin ortasında; kontra somundan ≥ 0,5 mm taşıyor; ısıl gömme somunda kavrama ≥ d ve ≤ somun boyu; horn'da kavrama ≥ 2,5 mm, uçtan servo "
         "kasasına ≥ 1 mm; çekiç somun dudak altında, cıvata ucu somunu ≥ 0,5 mm geçip kanal tabanına ≥ 1 mm kalıyor. Eksenler: servo milleri, horn'lar ve "
         "rulmanlar arayüz eksenlerinde (&lt; 0,05 mm). Birbirine göre dönen gruplar arasında en küçük boşluk %s mm (%s ↔ %s; eş eksenli rulman / horn "
         "çiftleri hariç; ölçüt ≥ 0,3 mm, %d ihlal).</p>" % (sayi(bag_min[0], 2), esc(bag_min[1]), esc(bag_min[2]), len(d["bagil_bosluk"]["hata"])))

H.append("<h2>Baskı parçaları (%s)</h2><div class='tw'>" % esc(Y["model"]))
rows = []
for b in baski:
    o = b["olcu"]
    rows.append((esc(TR.get(b["ad"], b["ad"])), "%s × %s × %s" % (sayi(o[0], 0), sayi(o[1], 0), sayi(o[2], 0)), OK if b["sigar"] else NO,
                 esc(b["yon"]), "%s %%" % sayi(100 * b["cikinti_orani"], 1), OK if b["desteksiz"] else NO + " (%d)" % b["destek_sorun_sayi"],
                 sayi(b["hacim_cm3"], 1), sayi(b["kutle_g"], 0), sayi(b["filament_g"], 0), sayi(b["sure_saat"], 1)))
top = (sum(b["kutle_g"] for b in baski), sum(b["filament_g"] for b in baski), sum(b["sure_saat"] for b in baski))
rows.append(("<b>Toplam</b>", "", "", "", "", "", "", "<b>%s</b>" % sayi(top[0], 0), "<b>%s</b>" % sayi(top[1], 0), "<b>%s</b>" % sayi(top[2], 1)))
H.append(tablo(["Parça", "Tablada ölçü (mm)", "X2D'ye sığar", "Baskı yönü", "45° üstü çıkıntı", "Desteksiz", "Hacim (cm³)", "Kütle (g)",
                "Filament (g)", "Süre (sa, tahmini)"], rows, "sayi") + "</div>")
sorunlu = [b for b in baski if not b["desteksiz"]]
if sorunlu:
    H.append("<p class='uyari'>%s</p>" % "<br>".join("%s: %d bölge, ilki katman %s mm (%s)" % (esc(TR.get(b["ad"], b["ad"])), b["destek_sorun_sayi"],
             sayi(b["destek_sorun"][0].get("z", 0), 1), esc(b["destek_sorun"][0])) for b in sorunlu))
H.append("<p class='not'>Kullanılabilir hacim %s × %s × %s mm (X2D ana nozul %s × %s × %s, her eksende %s mm pay; arayuz.YAZICI). Malzeme PETG; kütle = hacim × "
         "%s g/cm³ × etkin doluluk (küçük parçalar %%%d, kabuklar %%%d; tahmini); süre %s mm³/s ortalama debiyle (tahmini). Desteksizlik kabuktaki yöntemle: "
         "1 mm katmanlarda önceki katmanın 1 mm ötesine taşan, 2 mm'den geniş ve 15 mm'den uzun bölge yok.</p>"
         % (sayi(Y["kullanilabilir"][0], 0), sayi(Y["kullanilabilir"][1], 0), sayi(Y["kullanilabilir"][2], 0), sayi(Y["hacim_ana"][0], 0),
            sayi(Y["hacim_ana"][1], 0), sayi(Y["hacim_ana"][2], 0), sayi(Y["pay"], 0), sayi(A.PETG_RHO, 2), round(d["doluluk"] * 100),
            round(d["doluluk_kabuk"] * 100), sayi(A.PETG_HACIM_HIZI, 0)))

H.append("<h2>Tork</h2><div class='tw'>")
rows = [("Tilt (başı öne / arkaya), tilt ±15°", "MG996R", sayi(tt["kutle_g"], 1) + " g (kafa grubu)",
         "yerçekimi %s + ivme %s" % (sayi(tt["statik_tilt15_kgcm"], 3), sayi(tt["ivme_kgcm"], 3)),
         sayi(tt["toplam_tilt15_kgcm"], 2), "9,4", pay(tt["pay_tilt15"])),
        ("Tilt, yazılım aralığı (en kötü %+d°)" % tt["yercekimi_max_th"], "MG996R", sayi(tt["kutle_g"], 1) + " g (kafa grubu)",
         "yerçekimi %s + ivme %s" % (sayi(tt["yercekimi_max_kgcm"], 2), sayi(tt["ivme_kgcm"], 3)),
         sayi(tt["toplam_kgcm"], 2), "9,4", pay(tt["pay"])),
        ("Pan (sağa / sola)", "MG996R", sayi(tp["kutle_g"], 0) + " g (pan + kafa)",
         "atalet %s + rulman %s + kablo %s" % (sayi(tp["ivme_kgcm"], 3), sayi(tp["rulman_kgcm"], 4), sayi(tp["kablo_kgcm"], 2)),
         sayi(tp["toplam_kgcm"], 2), "9,4", pay(tp["pay_iki_hane"]))]
H.append(tablo(["Eklem", "Servo", "Taşınan kütle", "Bileşenler (kg·cm)", "Gereken (kg·cm)", "Stall (kg·cm)", "Pay"], rows, "sayi") + "</div>")
egri = tt["egri"]
H.append("<h3>Tilt yerçekimi momenti - açı</h3><div class='tw'>" + tablo(["Tilt (°)"] + ["%+d" % e["th"] for e in egri],
         [["kg·cm"] + [sayi(e["yercekimi_kgcm"], 2) for e in egri]], "sayi") + "</div>")
rul = tp["rulman"]
H.append("<p class='not'>Kafa grubunun kütle merkezi (%s; %s; %s), tilt ekseni (y, z) = (%s, %s): eksene uzaklık %s mm; kafa tam dönseydi en çok %s kg·cm. "
         "Tilt ataleti %s kg·m², pan ataleti (tilt 0) %s kg·m²; ivme %s rad/s² (%s). Pan rulmanları: eksenel %s N (üst 6808), devirme momenti %s N·m → "
         "rulman başına ≈ %s N radyal (merkezler arası %s mm). Tilt mesnetleri: horn (servo mili) %s N, 625ZZ pim %s N. Yetmezse seçenekler (gerekmedi): "
         "6 V besleme (MG996R 11 kg·cm), daha yavaş hareket profili, DS3218MG (omuzdaki 20 kg·cm).</p>"
         % (*[sayi(x, 1) for x in tt["am"]], sayi(tt["eksen"][0], 0), sayi(tt["eksen"][1], 0), sayi(tt["am_eksen_mm"], 1), sayi(tt["tam_tur_max_kgcm"], 2),
            sayi(tt["I_kgm2"], 5), sayi(tp["I_kgm2"]["0"], 5), sayi(tt["alfa_rad_s2"], 1), esc(d["tork"]["profil"]), sayi(rul["eksenel_N"], 1),
            sayi(rul["devirme_Nm"], 3), sayi(rul["radyal_N"], 0), sayi(rul["rulman_arasi_mm"], 0), sayi(ms["horn_N"], 1), sayi(ms["pim_N"], 1)))

H.append("<h2>Modül içi çakışma taraması (pan × tilt)</h2>")
H.append("<p>Pan %d…%d° (15° adım) × tilt %d…%d° (5° adım). Kafa grubu ↔ pan grubu yalnız tilt açısına, pan grubu ↔ boyun yalnız pan açısına bağlı; kafa ↔ boyun "
         "pan × tilt ızgarasında (%d poz). Ölçüt: ortak hacim &gt; 0,5 mm³ (eş eksenli horn / rulman çiftleri hariç).</p>"
         % (ta["psi"][0], ta["psi"][-1], ta["th"][0], ta["th"][-1], len(ta["kafa_govde"])))
ic = ta["ilk_carpan"]
rows = [("Tilt serbest aralık", "%s…%s°" % (sayi(tmin, 0), sayi(tmax, 0)), "yazılım sınırı %s…%s° %s" % (sayi(TAR[0], 0), sayi(TAR[1], 0),
                                                                                                   OK if ta["aralik_ok"] else NO)),
        ("Tilt: ilk çarpan (öne)", "%s°" % ic["+"][0] if "+" in ic else "tarama içinde yok", esc("; ".join("%s ↔ %s (%s mm³)" % tuple(x) for x in ic["+"][1])) if "+" in ic else ""),
        ("Tilt: ilk çarpan (arkaya)", "%s°" % ic["-"][0] if "-" in ic else "tarama içinde yok", esc("; ".join("%s ↔ %s (%s mm³)" % tuple(x) for x in ic["-"][1])) if "-" in ic else ""),
        ("Pan ↔ boyun", "%s…%s° serbest" % (sayi(pmin, 0), sayi(pmax, 0)), "±180° tarandı; sınır servo (180°) ve kablo halkası"),
        ("Tilt sınırında en küçük boşluk (kafa ↔ pan)", "%s mm" % sayi(bos_kp, 1), "tilt %s°: %s ↔ %s" % (bos_kp_a[0], esc(bos_kp_a[1][1]), esc(bos_kp_a[1][2]))),
        ("Kafa ↔ boyun en küçük boşluk", "%s mm" % sayi(bos_kg, 1), "pan −90 / 0 / 90 × tilt sınırları ve 0")]
H.append("<div class='tw'>" + tablo(["Sonuç", "Değer", "Ayrıntı"], rows) + "</div>")
H.append("<details><summary class='not'>Tilt açısına göre kafa ↔ pan grubu en küçük boşluk</summary><div class='tw'>" +
         tablo(["Tilt (°)", "Boşluk (mm)", "Parça çifti"], [("%+d" % int(k), sayi(v[0], 2), esc("%s ↔ %s" % (v[1], v[2])))
                                                           for k, v in sorted(ta["bosluk_kafa_pan"].items(), key=lambda kv: int(kv[0]))], "sayi") + "</div></details>")

H.append("<h2>Kabuk R62 boyun açıklığına uyum</h2>")
H.append("<p>Kabuk üst kapağı kafa yerelinde y %s…%s (global y = yerel + %s), boyun deliği R%s (kabuk_parcalar). Kapak seviyesinde yalnız sabit boyun var: servo yuvası "
         "bloğu (60 × 74 mm) ve kulak flanşı; en büyük yarıçap <b>%s mm</b> → deliğe en az %s mm. Pan grubunun en alt noktası y = %s (kapağın %s mm üstünde), "
         "kafa grubunun tüm pozlardaki en alt noktası y = %s (%s). Boyun plakası kapağın altında (y 0…3), kulakları x ±48'e uzanır.</p>"
         % (sayi(r62["kapak_y_yerel"][0], 0), sayi(r62["kapak_y_yerel"][1], 0), sayi(K["taban_y"], 0), sayi(r62["aciklik_r"], 0), sayi(r62["kapak_seviyesi_r_max"], 1),
            sayi(r62["sabit_en_kucuk"][0][0], 1), sayi(r62["pan_en_alt_y"], 1), sayi(r62["pan_en_alt_y"] - r62["kapak_y_yerel"][1], 0),
            sayi(r62["kafa_en_alt_y"], 1), esc("pan %s, tilt %s: %s" % tuple(r62["kafa_en_alt_poz"]))))

H.append("<h2>Kablo yolu</h2>")
H.append("<p><b>Kafa içi:</b> kablolar modelde yer ayırma zarfı olarak duruyor (kütle ve çakışmaya girmez; <code>kafa_montaj</code> her zarfın parçalarla "
         "kesişimini ve pan grubuna boşluğunu ölçer). Boyundan inenler: %s.</p>" % esc(d["pi"]["boyun_kablolari"]))
_z = d["qled"].get("zarf") or []
if _z:
    H.append("<div class='tw'>" + tablo(["Zarf", "Kesişen parça", "Pan grubuna boşluk (mm)", "Not"],
             [(esc(z_["ad"]), esc(", ".join(str(x) for x in z_.get("kesisim") or [])) or "yok",
               sayi(z_["pan_mm"], 1) if z_.get("pan_mm") is not None else "–", "<span class='not'>%s</span>" % esc(z_.get("not_", ""))) for z_ in _z]) + "</div>")
H.append("<p class='not'>Boyun bölümü (çatal tabanı → boyun mili içi → kablo odası → servo yuvası arka kanalı → R62) 125 cm kafasıyla aynı "
         "geometri (<code>kafa7_parcalar</code> Govde/Pan); 1,58 m'de ayrı kablo şeması yok (Referans grubu boş).</p>")

# ---------------------------------------------------------------- K4: Pi 5 kafada (15 Ekim 2026)
PI_ = d.get("pi")
ISI_ = d.get("isi")
if PI_ and ISI_:
    H.append("<h2>Raspberry Pi 5 kafada (K4, düzeltme planı 3. adım)</h2>")
    H.append("<ul><li>Pi 5 + Active Cooler kafa tablasının üstünde: kart köşesi baş çerçevesinde (x %s, y %s, z %s; baş çerçevesi = tilt ekseni), "
             "4× M2,5×8 pirinç burç (alttan M2,5×8, üstten M2,5×5).</li>"
             % (sayi(PI_["konum_T_bas_cercevesi"][0], 1), sayi(PI_["konum_T_bas_cercevesi"][1], 1), sayi(PI_["konum_T_bas_cercevesi"][2], 1)))
    H.append("<li>5 V çevirici Pololu D24V50F5 tablada (x %s, z %s; baş çerçevesi); ses yükseltici PAM8403, USB ses kartının analog çıkışından, "
             "sol duvarda (y %s, z %s); kafa ekranı için ayrı SY8205 + P6KE6V8A TVS. Boyundan: %s.</li>"
             % (sayi(PI_["cevirici_xz"][0], 0), sayi(PI_["cevirici_xz"][1], 0), sayi(PI_["amfi_sol_duvar_yz"][0], 0),
                sayi(PI_["amfi_sol_duvar_yz"][1], 1), esc(PI_["boyun_kablolari"])))
    hv = ISI_["hava"]
    H.append("<li>Havalandırma: arka kabuk yarıkları (yarık 35 × 3), giriş %s mm², çıkış %s mm², giriş–çıkış yükseklik farkı %s mm; "
             "1,55 L/s'de yarık hızı %s / %s m/s. (125 cm kafasında giriş %s, çıkış %s mm².)</li></ul>"
             % (sayi(hv["giris_mm2"], 0), sayi(hv["cikis_mm2"], 0), sayi(hv["H_mm"], 1), sayi(hv["giris_mm2_hiz_m_s_1.55L"], 2),
                sayi(hv["cikis_mm2_hiz_m_s_1.55L"], 2), sayi(hv["once"]["giris_mm2"], 0), sayi(hv["once"]["cikis_mm2"], 0)))
    rows = []
    for k_, ad_ in (("bosta", "Boşta (Pi 3,2 W)"), ("tipik", "Tipik (Pi 7 W)"), ("en_kotu", "En kötü (Pi 9,8 W)")):
        v_ = ISI_["senaryo"][k_]
        rows.append((esc(ad_), sayi(v_["W"], 1), sayi(v_["kapali_ic_C"], 1), sayi(v_["cekis_once_ic_C"], 1), sayi(v_["cekis_ic_C"], 1),
                     " / ".join(sayi(x, 1) for x in v_["yarikli_ic_C"]), "%s–%s" % (sayi(v_["aralik_C"][0], 0), sayi(v_["aralik_C"][1], 0)),
                     sayi(v_["servo_payi_kapali_K"], 1)))
    H.append("<div class='tw'>" + tablo(["Senaryo", "Kafa gücü (W)", "Kapalı kafa (°C)", "Yarıklı, yalnız doğal çekiş: önceki yarıklar (°C)",
                                         "Yarıklı, yalnız doğal çekiş: şimdiki (°C)", "İyimser: fan debisinin tamamı yarıklardan, 1,0 / 1,55 L/s (°C)",
                                         "Dürüst aralık (°C)", "Servo sınırına pay, kapalı (K)"], rows) + "</div>")
    H.append("<p class='not'>El hesabı, %s °C ortam, kafa içi ortalama hava (tahmini; kaynak: %s). Kapalı kabuk R ≈ %s K/W. Doğal çekiş: "
             "V̇ = C<sub>d</sub> A<sub>ef</sub> √(2 g H ΔT / T), C<sub>d</sub> %s, duvar kaybı paralel. Kafa küçük olduğu için baca etkisi zayıf "
             "(birkaç 0,1 L/s); asıl kazanç Active Cooler'ın perde altından taze hava emmesi, o da fan hızına ve sızıntıya bağlı. Active Cooler "
             "SoC ~50 °C altında durur, boşta doğal çekiş sınırı geçerli. "
             "Karar ölçümle: kafa kapalı, stres testinde SoC ≤ 75 °C, tilt servosu gövdesi ≤ 50 °C. Aşılırsa 25–30 mm egzoz fanı (üst bant arkasına).</p>"
             % (sayi(ISI_["varsayim"]["ortam_C"], 0), esc(ISI_["varsayim"]["kaynak"]), sayi(ISI_["varsayim"]["R_kapali_K_W"], 1),
                sayi(ISI_["varsayim"].get("Cd", 0.6), 1)))

H.append("<h2>Modüller arası çakışma ve ana montaj (2. aşama)</h2>")
H.extend(asama2())

H.append("<h2>Kararlar ve varsayımlar</h2><ul>" + "".join("<li>%s</li>" % md(s) for s in KARAR) + "</ul>")
H.append("<h2>Montaj sırası (öneri)</h2><ol>" + "".join("<li>%s</li>" % md(s) for s in SIRA) + "</ol>")
H.append("<h2>Açık işler</h2><ul>" + "".join("<li>%s</li>" % md(s) for s in ACIK) + "</ul>")
H.append("<h2>Dosyalar</h2><ul>"
         "<li><code>kafa_lib.py</code>: 6808-2RS, 10,1\" QLED, Camera Module 3, M2 vida, yuvarlatılmış kafa kutusu; MG996R / horn / baskı analizi dirsek_lib'den</li>"
         "<li><code>kafa7_parcalar.py</code>: boyun + pan grubu (125 cm ile ortak); <code>kafa10_lib.py</code>: 1,58 m başı (10,1\" QLED, Pi 5, ReSpeaker, ses)</li>"
         "<li><code>kafa_parcalar.py</code>: parçalar (kafa7 Govde/Pan + adaptör + kafa10 Bas), bağlantı tanımları, kütle, kinematik, yer ayırma zarfları</li>"
         "<li><code>kafa_montaj.py</code>: kontroller, tarama, R62, tork, baskı → <code>kafa-montaj.FCStd</code>, <code>.step</code>, <code>kafa-bom.csv</code>, "
         "<code>kafa-analiz.json</code></li>"
         "<li><code>kafa_gorsel.py</code> (FreeCAD GUI) → <code>gorsel/</code>; <code>kafa_rapor.py</code> → bu sayfa</li>"
         "<li><code>../arayuz.py</code>: <code>KAFA</code> (eksenler, sınırlar, plaka) ve <code>MODULLER['kafa']</code></li></ul>")
H.append("<p class='not'>Üretildi: kafa_rapor.py · analiz süresi %s s · STEP %d katı · eklemler %s</p>" % (sayi(d["sure_s"], 1), d["step_kati"],
                                                                                            "kuruldu" if d["joints_ok"] is True else esc(d["joints_ok"])))
H.append("</main></body></html>")
open(os.path.join(HERE, "rapor.html"), "w", encoding="utf-8").write("\n".join(H))
print("rapor.html", round(os.path.getsize(os.path.join(HERE, "rapor.html")) / 1024), "KB")
