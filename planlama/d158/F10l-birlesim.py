# P10.7b2d-A birleşim sınaması (F10l-gunluk.md § 3; düzeltme turu 1: § 9). Depoya yazmaz. FreeCAD istemez.
#   py -3 -B -X utf8 planlama/d158/F10l-birlesim.py [ROBOT] [commit]
# Düzeltme turu 1'den sonra K1 / K2 metni önceki commit'le (1c4e882) birebir aynı değil: çapalar silindi, "madde N" göndermeleri kart
# numarasına çevrildi (F10l-kontrol D2), bara uçları tek karta taşındı ve saplama yer tutucuları eklendi (D1), K2'de bir paragraf
# bölündü (N4), K2'ye bir cümle eklendi (N3). Düzeltme turu 2 (F10l-kontrol-2; § 10): 17.1'e G05 akü ucu cümlesi (D1), 17.4'e
# Kablo yolu 3 cümlesi (D2), dört "N." saplama biçimi "N numaralı" (N2). Sınama üç parça:
#   A  yapı: ana metin + alt adımlar (sırayla) = ALT_TAM_HAM; ALT_TAM_HAM = kaynaktaki çapalı metnin (ALT_KAYNAK_HAM) çapası silinmiş,
#      göndermesi çevrilmiş hâli (paragraf paragraf).
#   B  cümle çokluğu (bütün kaynak metinleri, yer bağımsız, yer tutucular çözülmüş): çapa ve gönderme biçimi eşitlenir (çapa silinir;
#      "madde N", "K2 madde N", "alt adım S.M", "bu alt adımda aşağıda / yukarıda" → §G). Kalan eklenen / silinen cümleler BEKLENEN
#      listesiyle TAM eşit olmalı; listede olmayan fark da, listede olup gerçekleşmeyen fark da hatadır.
#   C  gönderme biçimi eşitlenmeden: çevrilen her gönderme sayılır (rehber_metin.GONDERME_KAYIT), çözülemeyen 0.
import os, sys, re, subprocess, types, collections
ROBOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEAD = sys.argv[2] if len(sys.argv) > 2 else "1c4e882"
RH = os.path.join(ROBOT, "tasarim", "freecad", "rehber")
sys.path.insert(0, RH)
b = subprocess.run(["git", "show", HEAD + ":tasarim/freecad/rehber/rehber_metin.py"], cwd=ROBOT, capture_output=True, check=True).stdout
ESKI = types.ModuleType("rehber_metin_head")                       # dosyaya yazmadan, bellekte
ESKI.__file__ = os.path.join(RH, "rehber_metin.py")
exec(compile(b.decode("utf-8"), HEAD + ":rehber_metin.py", "exec"), ESKI.__dict__)
import rehber_metin as YENI
import rehber_denetim as RD

# Beklenen farklar (norm biçiminde, § 9'da cümle cümle "eski → yeni + gerekçe"). (sınıf, cümle)
_G06 = ("Şarj kolu (G06, 16 AWG): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı "
        "saplama, mavi M5 halka pabuç, ana anahtarın saplama ölçüsü kablajda teyit; F1'de takılır); 7,5 A mini hat sigortasının kapaklı "
        "yuvası ana anahtar girişindeki ucun dibinde (kaynak ucu), kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); "
        "− ucu yıldız barası")
_G07 = "Akü ölçüm bölücüsü (G07, 22 AWG): ana anahtar çıkışı (bölücünün üst direnci bu uçta) → güç paneli üstü → kat üstü → arayüz kartı, bölücü orta noktası"
_ALT = "Alt kat kartlarının (iki BTS7960B, XL4016 A / B / çevre) klemens uçları B3'te, kat ve güç paneli gelmeden bağlandı"
_BUR = "Burada B3'te etiketli bırakılan öbür uçları yerlerine bağla: "
_SON = ("G19'u arayüz kartının çevre 5 V / GND klemensine; SV1'i dağıtım kartı A'nın, SV2'yi dağıtım kartı B'nin V+ / GND giriş "
        "klemensine (OUT+ → V+, OUT− → GND).")
_F1 = ("F1 20 A → röle K1 kontağı (30 → 87 (87a boş); soketin kuyruk numaraları kablajda teyit: G08 sigorta kutusundan girişe, G09 "
       "çıkıştan anahtarlı bara%s; 12 AWG); F1 → ön şarj kartı → anahtarlı bara (G10, G11; 12 AWG).")
_G10 = ("Sonra G10'u K2 kontağının girişine lehimle, ön şarj direnci (5,6 Ω) çıkış ucunda, G11 direncin öbür bacağından %s; K2'nin "
        "uçları COM → NO (NC boş) (röle pimlerinin yeri kablajda teyit: röle gövdesindeki şema).")
_G16 = "XL4016 C'yi de mini hat sigortasıyla (5 A) baradan güç panelindeki IN+ / IN− klemensine bağla (G16, 16 AWG)"
_G22 = "PC817 #2 algı teli (G22, 22 AWG): anahtarlı bara ucunda (kaynak ucu) 2 A mini hat sigortası"
_KAFA = "Kafa 12 V (G17), göğüs 12 V (G20) ve ESP32 USB'nin (U06) taban uçlarını bağla."
_TOP = "Toprak (G05, 12 AWG): akü − → yıldız barasının ortadaki %s saplaması."
_G22K = ("G22'nin kutbu + → IN2 +, IN2 − → GND: + damarını (hat sigortasından gelen) arayüz kartındaki PC817 modülünün IN2 + klemensine, "
         "− damarını modülün IN2 − klemensinden yıldız barasına bağla; − damarının yıldız ucu 5 cm 18 AWG siyah ara parçaya lehimli, ara "
         "parça kırmızı pabuçla yıldız barasının %s saplamasına.")
_F1K = ("Kırmızı ucu arayüz kartındaki PC817 #1 giriş klemensinin + ucuna (mantar sonrası düğüm, E3), siyah ucunu güç panelindeki yıldız "
        "barasının (GND, M5 saplama) akü dönüşü saplamasına %s bağla.")
_TES = ("Teslimde bakılacaklar (`planlama/d158/kablo-tablosu-gunluk.md` §16.7, §17.7): alçak profil mini sigortalar (çevre 2 A, şarj "
        "7,5 A) \"Mini/Micro\" yuvaya oturuyor; K1 soketinin kuyruk kesiti okundu, G08 / G09'un 12 AWG teline eklendi; 5,08 mm klemensin "
        "kesit aralığı okundu (A06 / G07 lehimli uçlarına yeniden bakılır); G22'nin yıldız ucu 5 cm 18 AWG ara parça + kırmızı pabuç; akü "
        "dönüşü (G05) yıldızın %s saplamasında; T8 E ve E2 tezgâh kısa devre denemeleri yapıldı "
        "(`planlama/d158/testler/T8-servo-hatlari.md` E: bir servo uzatmasının ucunda ve SV1–SV3'te, servolar sökülü, en çok 2 s, yanmaz "
        "zemin): XL4016 akımı kesiyor ya da düşürüyor, kablo 80 °C'nin altında (kalırsa istisna düşer, tasarıma); K04'ün (kafa ekranı "
        "Power USB) üstündeki kesit yazısı okundu: 24 AWG'den inceyse ya da yazı yoksa 18 AWG + micro B fişle yeniden yapılır.")
BEKLENEN_SILINEN = [
    ("D1 G06 − ucu: saplama numarası, G05'ten sonra", _G06 + "na (mavi pabuç)."),
    ("P10.7b2d-A SEMA G07: cümle ikiye bölündü (eklenen iki cümle)", _G07),
    ("D1 alt kat: bara uçları başka kartta bağlandı göstergesi", _ALT + "."),
    ("D1 alt kat: G12–G15 ve G18 bağlaması bara çıkışları / sigorta kutusu kartına taşındı",
     _BUR + "G12 ve G13'ün + uçlarını anahtarlı baraya, − uçlarını yıldız barasına; G14 ve G15'in + uçlarını hat sigortası yuvasıyla "
     "anahtarlı baraya (§G), − uçlarını yıldız barasına; G18'in + ucunu sigorta kutusunun F4 çıkışına (§G), − ucunu yıldız barasına; " + _SON),
    ("D1 G09 saplama", _F1 % "ya"),
    ("D1 G11 saplama", _G10 % "baraya"),
    ("D1 G16 saplama", _G16 + "."),
    ("D1 G22 + ucu saplama", _G22 + "."),
    ("D1 direk: G17 / G20 taban ucu sigorta kutusu kartında bağlandı", _KAFA),
    # düzeltme turu 2 (F10l-kontrol-2 N2): "N." saplama biçimi → "N numaralı" (değer aynı; F10l-gunluk § 10)
    ("T2 N2 17.1 G05 saplama biçimi", _TOP % "(3.)"),
    ("T2 N2 17.6 G22 saplama biçimi", _G22K % "5."),
    ("T2 N2 F1 kontrol saplama biçimi", _F1K % "(3.)"),
    ("T2 N2 K1 kontrol saplama biçimi", _TES % "3."),
]
BEKLENEN_EKLENEN = [
    ("D1 G06 − ucu: saplama numarası, G05'ten sonra", _G06 + "nın 3 numaralı saplamasına, §G takılan G05'in üstüne (mavi pabuç)."),
    ("P10.7b2d-A SEMA G07", _G07 + "."),
    ("P10.7b2d-A SEMA G07", "Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır), karede yok"),
    ("D1 alt kat: bara uçları başka kartta bağlandı göstergesi",
     _ALT + "; G12–G15'in bara uçları §G, G18'in kutu ve yıldız uçları §G bağlandı."),
    ("D1 alt kat: kalan uçlar", _BUR + _SON),
    ("D1 G09 saplama", _F1 % "nın 3 numaralı saplamasına"),
    ("D1 G11 saplama", _G10 % "anahtarlı baranın 3 numaralı saplamasına"),
    ("D1 G16 saplama, G13'ten sonra", _G16 + "; G16'nın + ucu anahtarlı baranın 2 numaralı, − ucu yıldız barasının 2 numaralı saplamasına, "
     "G13'ün üstüne."),
    ("D1 G22 + ucu saplama", _G22 + "; G22'nin yuvasının bara kuyruğu anahtarlı baranın 4 numaralı saplamasına."),
    ("D1 G12–G15 bara uçları (alt kattan taşındı), kalın pabuç altta",
     "G12–G15'in alt kat ucu B3'te bağlandı; burada B3'te etiketli bırakılan bara uçlarını bağla, kalın pabuç altta: önce G12'nin + ucunu "
     "anahtarlı baranın 1 numaralı, G13'ünkünü 2 numaralı saplamasına, − uçlarını yıldız barasının 1 ve 2 numaralı saplamasına; sonra G14 "
     "ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baranın 1 numaralı saplamasına, − uçlarını yıldız barasının 1 numaralı "
     "saplamasına (her biri G12'nin üstüne)."),
    ("D1 G17 / G18 / G20 kutu ve yıldız uçları (alt kat ve direk kartından taşındı)",
     "G17, G18, G20 ve A01'in kutu ucunu kendi yuvasının çıkışına bağla (G17 F3, G18 F4, A01 F5, G20 F6); G17, G18 ve G20'nin − ucunu "
     "yıldız barasına: G17 ve G18 4 numaralı, G20 5 numaralı saplamaya (G18'in öbür ucu B3'te XL4016 çevreye bağlandı)."),
    ("D1 direk: G17 / G20 taban ucu sigorta kutusu kartında bağlandı",
     "Kafa 12 V'un (G17) ve göğüs 12 V'un (G20) taban uçları §G bağlandı; ESP32 USB'nin (U06) taban ucunu bağla."),
    ("N3 K2 kol servo uzatmaları: karedeki Kablo yolu 5 / 7'nin K1 kısmı",
     "Karede Kablo yolu 5 ve 7'nin baradan dağıtım kartlarına giden kısmı K1'de bağlandı; burada yalnız uzatmaları tak."),
    # düzeltme turu 2 (F10l-kontrol-2 D1, D2, N2; F10l-gunluk § 10)
    ("T2 D1 17.1 G05'in akü ucu XT60 (kablolar.json G05 uc_a, G01)",
     "G05'in akü ucu XT60'ın robot tarafındaki − ucudur (lehim): akünün kutbuna doğrudan bağlama, akü kutupları bantlı kalır (akü ile "
     "XT60'ın akü tarafı arası G01, §G)."),
    ("T2 D2 17.4 Kablo yolu 3'ün G12 kısmı karede, ucu 17.5'te",
     "Karede Kablo yolu 3'ün baradan sol BTS7960B'ye giden kısmı (G12) da görünür; o uç §G bağlanır."),
    ("T2 N2 17.1 G05 saplama biçimi", _TOP % "(3 numaralı)"),
    ("T2 N2 17.6 G22 saplama biçimi", _G22K % "5 numaralı"),
    ("T2 N2 F1 kontrol saplama biçimi", _F1K % "(3 numaralı)"),
    ("T2 N2 K1 kontrol saplama biçimi", _TES % "3 numaralı"),
]


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


_G = re.compile(r"(?:\b(?:K[12]) )?\bmadde \d+[a-z]?\b(?:'(?:de|da|te|ta)(?:ki)?)?|\balt adım \d+\.\d+\b(?:'(?:de|da|te|ta)(?:ki)?)?|"
                r"\bbu alt adımda (?:aşağıda|yukarıda)")


def esit_bicim(c):
    return _G.sub("§G", re.sub(r"^\d+[a-z]?\. ", "", norm(c)))


hata = []
# A
for kod in YENI.DEMET_ALT:
    a = YENI.ADIM_HAM[kod]
    birlesim = "\n".join([a["is_"]] + [g["is_"] for g in a["sira"]])
    if birlesim != YENI.ALT_TAM_HAM[kod]:
        hata.append("A %s: ana + alt adımlar ALT_TAM_HAM değil" % kod)
    h, p = YENI.capa_haritasi({kod: YENI.ALT_KAYNAK_HAM[kod]})
    kaynak_par = YENI.ALT_KAYNAK_HAM[kod].split("\n")
    tam_par = YENI.ALT_TAM_HAM[kod].split("\n")
    if len(kaynak_par) != len(tam_par):
        hata.append("A %s: paragraf sayısı %d → %d" % (kod, len(kaynak_par), len(tam_par)))
    for j, (k, t) in enumerate(zip(kaynak_par, tam_par)):
        if esit_bicim(k) != esit_bicim(t):
            hata.append("A %s paragraf %d: çapa / gönderme dışında fark" % (kod, j))
    print("A %s: ana + %d alt adım = ALT_TAM_HAM %s; %d paragraf, çapalı kaynakla gönderme dışında aynı %s" % (
        kod, len(a["sira"]), birlesim == YENI.ALT_TAM_HAM[kod], len(tam_par),
        all(esit_bicim(k) == esit_bicim(t) for k, t in zip(kaynak_par, tam_par))))


# B
def cumleler(R):
    out = collections.Counter()
    for y, t in RD.kaynak_metinler(R):
        if re.match(r"kaynak K[12] alt adım \d+ ad$", y):
            continue                                                   # kart adları ayrı sayılır (aşağıda)
        for c in re.split(RD._CUMLE_GENIS, t or ""):
            if c.strip():
                out[esit_bicim(c)] += 1
    return out


ce, cy = cumleler(ESKI), cumleler(YENI)
ekl, sil = cy - ce, ce - cy
bek_e = collections.Counter(c for s, c in BEKLENEN_EKLENEN)
bek_s = collections.Counter(c for s, c in BEKLENEN_SILINEN)
print("\nB cümle (bütün kaynak metinleri, yer bağımsız, çapa / gönderme eşit): eski %d, yeni %d; eklenen %d (beklenen %d), silinen %d "
      "(beklenen %d)" % (sum(ce.values()), sum(cy.values()), sum(ekl.values()), sum(bek_e.values()), sum(sil.values()), sum(bek_s.values())))
for c, n in sorted((ekl - bek_e).items()):
    hata.append("B beklenmeyen ekleme x%d: %s" % (n, c))
for c, n in sorted((bek_e - ekl).items()):
    hata.append("B beklenen ekleme yok x%d: %s" % (n, c))
for c, n in sorted((sil - bek_s).items()):
    hata.append("B beklenmeyen silme x%d: %s" % (n, c))
for c, n in sorted((bek_s - sil).items()):
    hata.append("B beklenen silme yok x%d: %s" % (n, c))
for s, c in BEKLENEN_SILINEN:
    print("  SİLİNDİ [%s] %s" % (s, c[:150]))
for s, c in BEKLENEN_EKLENEN:
    print("  EKLENDİ [%s] %s" % (s, c[:150]))
for kod in YENI.DEMET_ALT:
    e = [g.get("ad") for g in ESKI.ADIM_HAM[kod].get("sira") or []]
    y = [g.get("ad") for g in YENI.ADIM_HAM[kod]["sira"]]
    print("  kart adları %s: %d → %d; yeni: %s; kalkan: %s" % (kod, len(e), len(y), [x for x in y if x not in e] or "-",
                                                             [x for x in e if x not in y] or "-"))
# C
print("\nC gönderme: çevrilen %d, çözülemeyen %d" % (len(YENI.GONDERME_KAYIT), len(YENI.GONDERME_HATA)))
for e in YENI.GONDERME_KAYIT:
    print("  %s: %s madde %s → alt adım %d.%d" % (e["yer"], e["kod"], e["capa"], YENI.ALT_ADIM_NO[e["kod"]], e["hedef"]))
if YENI.GONDERME_HATA:
    hata += ["C " + x for x in YENI.GONDERME_HATA]
for x in hata:
    print("HATA", x)
print("\nbirlesim sinamasi: %s" % ("GECER" if not hata else "KALIR (%d)" % len(hata)))
sys.exit(0 if not hata else 1)
