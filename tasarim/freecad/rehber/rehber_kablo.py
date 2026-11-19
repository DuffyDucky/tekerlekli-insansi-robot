# 3B montaj rehberi: çizilen kablolar ↔ tek kablo kaynağı (P10.7b1). FreeCAD İSTEMEZ (standart kütüphane); kaynağı yalnız okur.
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_kablo.py                    # eşleme denetimi (kaynak) + çizilen / çizilmeyen tablosu
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_kablo.py --veri <json>      # ayrıca üretilmiş rehber-veri.json'u denetle
#   py -3 -X utf8 tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi   # her bozma en az bir hata vermeli
# Çıkış 0 = temiz.
#
# Tek kaynak: planlama/adim3/kablolar.json (74 kablo). Rehberde çizilen her kablo nesnesi (taban CAD'indeki 12 "Kablo yolu N" parçası,
# rehber_metin.SEMA gösterim şemaları, rehber_kol_kablo.py kol içi yol bölümleri) bir ya da birkaç tablo kimliğine bağlanır; ilk kimlik
# "ana" kablodur. Çizimin rengi ana kablonun devre sınıfının rengi (kablolar.json renk_kurali.siniflar[sinif].cizim; anahtar kelimeyle
# renk verme kaldırıldı), şema tüp yarıçapı ana kablonun kesitinden (YARICAP kuralı). Tıklanınca / listede tablo bilgisi görünür (kimlik,
# iki uç, kesit, sigorta, acil stopta enerjili mi). Eşlemesi olmayan çizim ve çizilmeyen tablo kablosu ayrı listelenir.
#
# Tüp yarıçapı kuralı (P10.7b1 düzeltme turu 1, F10h-kontrol §2-11; okunur ölçek, gerçek çap değil): kesit kademesi tablosu
# KESIT_YARICAP: 22 AWG 2,5 · 18 AWG 3,1 · 16 AWG 3,6 · 12 AWG 4,6 mm. Kural: en ince sinyal teli bugünkü en ince çizimden (2,5)
# ince değil (kol telleri 2,1'e inmez, eski 2,5'e döner); komşu kademeler arasında en az %15 fark (gözle seçilir); 22 → 12 AWG dört
# kademe (üç adım). Tabloda olmayan AWG: 2,5 + 1,8 × (√mm² − √0,33), en az 2,5. Hazır kablo (USB / HDMI / CSI): dış çap şartı
# varsa onun yarısı, en az 2,5; yoksa 2,5. Kesiti tabloda olmayan (motorun kendi kablosu, hazır ses kablosu, hoparlör kordonu) 2,5.
# Taban CAD parçalarının tüp çapı CAD geometrisidir (2,5 sabit): değiştirilmez (yalnız renk ve bilgi tablodan); kural şema ve kol
# tüplerine uygulanır.
#
# Tema tonları (TEMA_TON; F10h-kontrol §2-12, §2-13): sınıf rengi (kablolar.json cizim) her temada zemine karşı okunur olsun diye
# tema başına tonlanır. Ölçüt: her ton kendi temasının sahne zeminine ve lejant zeminine (rehber/stil.css --sahne, --card) karşı WCAG
# karşıtlığı ≥ 3,0 (karsitlik_denetle; kaynak denetiminde hata). Koyu temada "siyah" (toprak) açık gri tüp, lejant karesi koyu
# çekirdekli; açık temada sarı ve beyaz koyu / doygun ton. Hazır kablolar tür başına (HAZIR_TUR: USB, HDMI, CSI) ayrı ton ve lejant satırı.
import os, sys, re, json, math, copy, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TABLO_YOL = os.path.join(ROBOT, "planlama", "adim3", "kablolar.json")
sys.path.insert(0, HERE)

R_VARSAYILAN = 2.5
KESIT_YARICAP = {22: 2.5, 18: 3.1, 16: 3.6, 12: 4.6}
TEMA_TON = {
    "kirmizi": {"light": "#c0392b", "dark": "#ef5a4c"}, "turuncu": {"light": "#b35a00", "dark": "#f0903a"},
    "sari": {"light": "#8a6d00", "dark": "#e8c020"}, "mavi": {"light": "#1f6fb8", "dark": "#4a9fe8"},
    "yesil": {"light": "#1e7a3c", "dark": "#3dbb64"}, "mor": {"light": "#7d3c98", "dark": "#b07fd0"},
    "siyah": {"light": "#222222", "dark": "#b3b3b3", "cekirdek_dark": "#222222"}, "beyaz": {"light": "#4c7078", "dark": "#f2f6f7"},
    "hazir-usb": {"light": "#828282", "dark": "#818181"}, "hazir-hdmi": {"light": "#193cff", "dark": "#5ba7b8"},
    "hazir-csi": {"light": "#6f3312", "dark": "#b2916b"},
}
# P10.7b1 açık işler turu (kontrol-2 madde 17): en yakın çiftler ΔE00 < RENK_FARK_ESIK olduğu için yeniden tonlandı (eski → yeni):
# açık beyaz #4e6d7d → #4c7078, USB #7c7c7c → #828282, HDMI #2f3f4f → #1d3854, CSI #8a5a3c → #6f3312; koyu siyah #b9bec5 → #b3b3b3,
# USB #7d7d7d → #818181, HDMI #7f9bb5 → #5ba7b8, CSI #c0916c → #b2916b. Ana sınıfların (kırmızı … mor) tonları değişmedi.
# P10.7b2a (F10h-kontrol-4): açık HDMI #1d3854 → #193cff: lacivert ince çizgide siyaha yakın okunuyordu (ΔE00 15,3, L* farkı ≈ 10);
# yeni ton aynı mavi ailesinde, doygun ve açık (L* ≈ 39). Kural: açık temada siyah dışındaki her ton siyahtan ≥ SIYAH_L_FARK açık.
SIYAH_L_FARK = 15.0
# Seçim vurgusu (rehber/app.js VURGU_TON, tema başına "ana"): kablo tonlarıyla aynı sınamaya girer (zemine karşıtlık ≥ 3,0; her kablo
# tonuna ve sahnenin öbür işaret renklerine, EV_RENK ile KONUM_RENK'e, ΔE00 ≥ 15). Tablo app.js'ten okunur (tek kaynak).
# Düzeltme turu 1 (F10i-kontrol A9): "kopya" tonu da ΔE00 sınamasına girer ve ikisi app.js SINIF tablosunun parça sınıfı renklerine
# karşı da sınanır (eski açık ton #a35ef2 "lazer" #8e44ad'a 13,4'tü; yeni açık ton #e014ff). Karşıtlık ölçütü yalnız "ana" için.
APP_JS = os.path.join(ROBOT, "rehber", "app.js")
VURGU_ELLE = {}                                                      # bozma denemesi: {"light": ton, "dark": ton} app.js yerine


def vurgu_tonlari(yol=None):
    """app.js'in seçim vurgusu ve sahne işaret renkleri: ({tema: ana ton, tema + "_kopya": kopya tonu}, {ad: ton}). Okunamazsa
    KeyError. Düzeltme turu 1 (F10i-kontrol A9): kopya tonu da okunur (eşik sınamasına girer)."""
    s = open(yol or APP_JS, encoding="utf-8").read()
    m = re.search(r"const VURGU_TON = \{(.*?)\n  \};", s, re.S)
    if not m:
        raise KeyError("app.js'te VURGU_TON yok")
    v = {}
    for tm in ("light", "dark"):
        t = re.search(tm + r": \{[^}]*?\bana: \"(#[0-9a-fA-F]{6})\"", m.group(1))
        k = re.search(tm + r": \{[^}]*?\bkopya: \"(#[0-9a-fA-F]{6})\"", m.group(1))
        if not t or not k:
            raise KeyError("app.js VURGU_TON.%s.%s yok" % (tm, "ana" if not t else "kopya"))
        v[tm], v[tm + "_kopya"] = t.group(1).lower(), k.group(1).lower()
    v.update(VURGU_ELLE)
    sabit = {}
    for ad in ("EV_RENK", "KONUM_RENK"):
        t = re.search(ad + r" = \"(#[0-9a-fA-F]{6})\"", s)
        if not t:
            raise KeyError("app.js'te %s yok" % ad)
        sabit[ad] = t.group(1).lower()
    return v, sabit


SINIF_ELLE = {}                                                      # bozma denemesi: {sınıf: ton} app.js yerine


def sinif_renkleri(tm, yol=None):
    """app.js SINIF tablosunun parça sınıfı renkleri (seçim vurgusunun kendisi olan "secili" hariç); "onceki" tema başına
    (sahneRengi: koyu temada ayrı ton). Düzeltme turu 1 (F10i-kontrol A9): vurgu bu renklere karşı da ΔE00 eşiğine girer."""
    s = open(yol or APP_JS, encoding="utf-8").read()
    m = re.search(r"const SINIF = \{(.*?)\n  \};", s, re.S)
    if not m:
        raise KeyError("app.js'te SINIF yok")
    out = {a: b.lower() for a, b in re.findall(r"(\w+): \[\"(#[0-9a-fA-F]{6})\"", m.group(1))}
    out.pop("secili", None)
    if tm == "dark":
        t = re.search(r"SINIF\.onceki\[0\] = tema\(\) === \"dark\" \? \"(#[0-9a-fA-F]{6})\"", s)
        if not t:
            raise KeyError("app.js'te koyu tema SINIF.onceki tonu yok")
        out["onceki"] = t.group(1).lower()
    out.update(SINIF_ELLE)
    return out
HAZIR_TUR = {"U": ("hazir-usb", "Hazır kablo: USB"), "H": ("hazir-hdmi", "Hazır kablo: HDMI"), "C": ("hazir-csi", "Hazır kablo: kamera (CSI)")}
KARSITLIK_ESIK = 3.0
STIL_CSS = os.path.join(ROBOT, "rehber", "stil.css")

# Taban CAD'indeki "Kablo yolu N" parçaları (taban_parcalar.py etiketleri; görünen adlar rehber_metin.KABLO_AD) → tablo kimlikleri.
# İlk kimlik ana kablo (renk). Bir CAD yolu birkaç devre sınıfını taşıyorsa (karisik) ana kablonun rengini alır ve KARISIK listesine girer.
# Elle yazılmış tablo: geometri_denetle() her kimliği CAD yolunun noktalarıyla sınar (P10.7b1 düzeltme turu 1, kontrol Ü3). Yolun
# geometrisinin ulaşmadığı uçlu kablo burada yazılmaz (çizilmeyen sayılır, P10.7b2 girdisi).
CAD_ESLEME = {
    1: ("G02", "G01", "G03", "G04"),                                    # 12 V ana hat
    2: ("G05",),                                                         # toprak (akü − → yıldız barası)
    3: ("G12", "G09", "G11", "G08", "G10", "M01"),                       # F1 → röle / ön şarj → bara → BTS sol → ön sol motor
    4: ("M03", "M04", "G13"),                                            # bara → BTS sağ → ön sağ + arka sağ motor (arka sol yok)
    5: ("SV1", "G14", "S01", "S02", "S03", "S04"),                       # servo 6 V A → dağıtım A → direk → sağ omuz (uzatma demeti)
    6: ("S09", "S10"),                                                   # kafa servo uzatmaları (hat C)
    7: ("SV2", "G15", "S05", "S06", "S07", "S08"),                       # servo 6 V B → dağıtım B → direk → sol omuz
    8: ("G17",),                                                         # kafa 12 V
    9: ("G18",),                                                         # F4 → XL4016 çevre (yolun eski XL4016 → ESP32 devamı rehberde kırpılır: CAD_KIRP)
    10: ("A02", "A01", "A03", "A04", "A05", "A06"),                      # acil stop
    11: ("Q03", "X01"),                                                  # sol sonar → arayüz kartı → ESP32 (orta / sağ sonara gitmez)
    12: ("B01",),                                                        # BTS sol sinyali → ESP32 (eski üst kısım rehberde kırpılır: CAD_KIRP; U06 "ESP32 USB" şemasında)
}

# ------------------------------------------------------------------ geometrik eşleme sınaması (CAD yolu noktaları ↔ kablonun uçları)
# Kaynak: tasarim/freecad/taban/taban-analiz.json (taban_parcalar.py'nin FreeCAD çıktısı, geometriyle aynı commit'te): kablo_yolu[n-1].
# noktalar ve parcalar[].bb (xmin, xmax, ymin, ymax, zmin, zmax; mm). FreeCAD istemez.
# Kural: (1) eşlenen her kablonun iki yanı (damarların a uçları / b uçları) için en az bir uç parçası şunlardan birini sağlar:
#   modelli taban parçası → yol kırık çizgisi parçanın kutusuna ≤ GEO_ESIK mm; taban dışı parça (kafa, kol, gövde) → yolun taban
#   dışındaki bir uç noktası o parçanın bölgesinde (TABAN_DISI_BOLGE / TABAN_DISI_PARCA); modelsiz parça → MODELSIZ_KONUM'daki nominal
#   noktaya ≤ GEO_ESIK mm ya da vekil parçanın kutusuna; ne nokta ne vekil varsa sınanmaz ("elle bakıldı", bilgi).
# (2) Yolun iki uç noktası: y ≥ GEO_TABAN_DISI ise düştüğü bölge eşlenen bir kablonun taban dışı ucunun bölgesi olmalı; değilse uç
#   noktaya ≤ GEO_ESIK mm'deki modelli parça varsa eşlenen kablolardan birinin uç parçası (ya da vekili) olmalı; yakında parça yoksa
#   eşlenen bir kablonun nominal noktası ≤ GEO_ESIK mm'de olmalı ya da elle bakılan bir yanı bulunmalı. Uymayan uç ancak
#   GEO_ISTISNA'daki gerekçeyle geçer.
# Sınır: uç parçaları (ve kutupları) aynı olan iki kablo geometriyle ayırt edilmez (ayirt_edilemeyen()); onları CAD_ESLEME'nin onay
# kaydı korur (kritik_tablolar(), rehber_kritik_onay.json).
# Haritada olmayan uç parçası hata (sessiz geçiş yok).
GEO_ESIK = 10.0
GEO_TABAN_DISI = 400.0
GEO_ANALIZ = os.path.join(ROBOT, "tasarim", "freecad", "taban", "taban-analiz.json")
TABAN_DISI = "taban-disi"
MODELSIZ = "modelsiz"
NOMINAL = "nominal"                                                     # modelsiz, MODELSIZ_KONUM'da nominal konumu / vekili var
# Anahtar: kablolar.json kablo uçlarının (uc_a / uc_b) parça adı; en uzun önek eşleşir ("Röle K1 (MAH-112-C-4, soket)" → "Röle K1").
PARCA_CAD = {                                                           # tablo uç parçası → CAD parça adı deseni / sınıf
    "Akü": r"^Aku LiFePO4",
    "Ana sigorta yuvası": r"^Ana sigorta yuvasi", "Ana anahtar": r"^Ana anahtar ASW", "Sigorta kutusu": r"^Sigorta kutusu",
    "Röle K1": r"^Role 12 V", "Ön şarj kartı": r"^On sarj karti",
    "BTS7960 sol": r"^BTS7960 motor surucu sol$", "BTS7960 sağ": r"^BTS7960 motor surucu sag$",
    "JGB37-520 ön sol": r"^Motor JGB37-520 \(on sol\)", "JGB37-520 arka sol": r"^Motor JGB37-520 \(arka sol\)",
    "JGB37-520 ön sağ": r"^Motor JGB37-520 \(on sag\)", "JGB37-520 arka sağ": r"^Motor JGB37-520 \(arka sag\)",
    "XL4016 A": r"^XL4016 servo 6 V A", "XL4016 B": r"^XL4016 servo 6 V B", "XL4016 çevre": r"^XL4016 cevre",
    "XL4016 C": r"^XL4016 servo 6 V C",                                  # P10.7b2b (R8): G16 / SV3'ün ucu; CAD parçası güç panelinde
    "XT60E-F": MODELSIZ,                                                 # P10.7b2b (R8): G06'nın ucu; modeli yok (K50, MODELSIZ_KONUM)
    "Dağıtım kartı A": r"^Servo dagitim karti A", "Dağıtım kartı B": r"^Servo dagitim karti B",
    "Arayüz kartı": r"^Arayuz karti", "ESP32 DevKit": r"^ESP32 (DevKit|tasiyici)", "ESP32 / arayüz kartı": r"^(ESP32 |Arayuz karti)",
    "Elektronik katı": r"^(Arayuz karti|PCA9685|ESP32 )", "PC817 modülü (arayüz kartı)": r"^Arayuz karti",
    "HC-SR04 sağ": r"^Sonar HC-SR04 \(sag\)", "HC-SR04 orta": r"^Sonar HC-SR04 \(orta\)", "HC-SR04 sol": r"^Sonar HC-SR04 \(sol\)",
    "Acil stop mantarı": r"^Acil stop kontak govdesi",
    "XT60 (akü tarafı)": NOMINAL, "XT60 (robot tarafı)": NOMINAL, "Anahtarlı bara": NOMINAL,
    "Yıldız barası": NOMINAL, "Acil stop düğümü": MODELSIZ,
    # P10.7b2b (R8): dağıtım kartı C taban dışı (kafa) değil, güç panelinde (kablolar.json karar P7b2a-6); kart modelde yok (R23)
    "Dağıtım kartı C": MODELSIZ, "Kafa giriş klemensi": TABAN_DISI, "USB hub": TABAN_DISI,
}
# Modelsiz uç parçası → nominal konum / yerine geçen parça (P10.7b1 açık işler turu, F10h-kontrol-2 madde 11). Anahtar (parça, kutup);
# kutup ucun "nokta" alanıdır ("+" ya da "−"), "+ / −" gibi iki damarlı uçta kablonun ilk damarı; "*" her kutup. Değer (nokta, vekil,
# gerekçe): nokta varsa kablonun o yanı yolun bu noktaya ≤ GEO_ESIK mm geçmesiyle sağlanır; vekil (CAD parça adı deseni) yol ucundaki
# komşu parçanın bu uç sayılmasını sağlar, nokta yoksa yan vekil parçanın kutusuyla sınanır. İkisi de yoksa uç sınanmaz: "elle bakıldı"
# kaydı (bilgi) yazılır. Noktaların kaynağı taban_parcalar.py'deki kablo yolu tanımlarıdır (YOL listesi, yol etiketiyle birlikte).
_AKU_ARTI, _AKU_EKSI = (-65.5, 133.0, -29.0), (65.5, 133.0, -29.0)
MODELSIZ_KONUM = {
    ("XT60 (akü tarafı)", "+"): (_AKU_ARTI, r"^Aku LiFePO4",
                                 "XT60'ın modeli yok, akü kablosunun ucunda akü kutusunun üstünde durur; + kutup: yol 1 baş noktası ('aku + -> XT60')"),
    ("XT60 (akü tarafı)", "−"): (_AKU_EKSI, r"^Aku LiFePO4", "− kutup: yol 2 baş noktası ('aku - -> yildiz barasi 3. saplama')"),
    ("XT60 (robot tarafı)", "+"): (_AKU_ARTI, r"^Aku LiFePO4", "akü tarafıyla aynı yerde (geçme çift); + kutup yol 1 başı"),
    ("XT60 (robot tarafı)", "−"): (_AKU_EKSI, r"^Aku LiFePO4", "akü tarafıyla aynı yerde (geçme çift); − kutup yol 2 başı"),
    # P10.7b2k düzeltme turu 1 (F10u-kontrol 1): bara tutucuları P10.7b2j'de modelde; CAD yolları (taban_parcalar YOL 1, 2, 3, 5, 7,
    # 8, 9) CAD dalında tutuculara taşınıyor (ayrı tasarım ajanı; hedef listesi F10u-gunluk "CAD tasarım ajanına"). Eski vekiller
    # (yıldız: WAGO noktası (−20; 186; −90), anahtarlı: Röle K1 kutusu) kalktı: yan tutucunun kutusuyla sınanır, hangi saplamada
    # bittiği bara_yol_denetle'de (kablolar.json yerleşimi). Yollar taşınana dek bu ikisi HATA verir (beklenen).
    ("Yıldız barası", "*"): (None, r"^Bara tutucusu yildiz barasi",
                             "bara tutucusu modelde (P10.7b2j, arayuz TABAN['bara_tutucu']); saplaması bara_yol_denetle'de"),
    ("Anahtarlı bara", "*"): (None, r"^Bara tutucusu anahtarli bara",
                              "bara tutucusu modelde (P10.7b2j); saplaması bara_yol_denetle'de"),
    ("Acil stop düğümü", "*"): (None, None,
                                "güç panelinde küçük pertinaks kart; CAD'de ne modeli ne yol noktası var (yerleşim P10.7b2): sınanmaz, elle bakıldı"),
    # P10.7b2b (R8)
    ("Dağıtım kartı C", "*"): (None, None,
                               "güç panelinde, XL4016 C'nin yanında (kablolar.json P7b2a-6); kart modelde yok (R23) ve yol 6 yalnız boyun → "
                               "kafa bölümünü çiziyor: kart yanı sınanmaz, elle bakıldı"),
    ("XT60E-F", "*"): (None, None,
                       "panel şarj girişi: konnektör K50 b (dişi; alımı açık), etek deliği açık iş; modeli ve yol noktası yok: sınanmaz"),
}
# P10.7b2b (F10h-kontrol-3 §3.3-2; R8): onay kaydı olmadan da yakalanacak eşleme bozmaları.
# (a) Dal (GEO_DAL): dalda eşlenen her kablonun en az bir yanı dalın KENDİ noktalarıyla sağlanmalı; ana yolun ayrılma noktasına kadarki
#     bölümü yalnız öbür yan için (G19: yol 4'e G08, G20: yol 4'e G10 yalnız ana yol bölümüyle uyuyordu).
# (b) Sınıf: bir CAD yolu tek devre sınıfı taşır; bugün bilinen karışık yollar KARISIK_BILINEN'de (ayrılmaları R18 açık işi). Başka bir
#     karışım ya da bilinen yolun sınıf kümesinin değişmesi hata (G24: yol 10'da A03 yerine G22, yeşil ↔ turuncu).
# (c) Eksik eşleme: yolun sınıflarından birinde olup iki yanı da bu yolun noktalarıyla geometrik olarak sağlanan (elle bakılan yan
#     sayılmaz) ama eşlenmemiş kablo hata; bilinçli dışarıda bırakılan GEO_EKSIK_MUAF'ta gerekçesiyle (G26: yol 1'den G02 çıkarıldı).
#     Kısmi eşleme (G18 / yol 9: yol eski tasarım, G19 bu yolda çizili sayılmaz) G19'un yanı yola ulaşmadığı için zaten aday değil.
#     Yalnız vekil parçayla sağlanan yan (anahtarlı bara → Röle K1 kutusu) kanıt sayılmaz: her taban yolu röleden çıkar.
KARISIK_BILINEN = {3: ("kirmizi", "turuncu"), 5: ("sari", "turuncu"), 7: ("sari", "turuncu")}
_G10_YAKIN = ("ön şarj kartı sigorta kutusunun yanında: yol sigorta kutusunda biter ve kartın kutusuna 10 mm'den yakın geçer; "
              "G10 (F1 → ön şarj kartı) yol 3'te çizili")
GEO_EKSIK_MUAF = {1: {"G10": _G10_YAKIN}, 8: {"G10": _G10_YAKIN}}
TABAN_DISI_DESEN = r"servosu( \(|$)"                                    # kol / kafa servoları
# Taban dışı bölgeler (P10.7b1 açık işler turu, kontrol-2 madde 11): yolun taban dışındaki (y ≥ GEO_TABAN_DISI) uç noktası sırayla ilk
# tutan bölgeye düşer; kablonun taban dışı ucu ancak kendi bölgesinde biten yolla sağlanır. Aralıklar montaj/montaj-analiz.json parça
# merkezlerinden (ev pozu, global mm; +X sağ, +Y yukarı): kafa modülü x −134…134, y 1283…1578 (Govde grubu x −40…40, y 1283…1368) ve
# boyun geçişi (kabuğun üst ağzı y ≤ 1268 ile kafa gövdesi arası, eksen üstü: yol 6'nın başı (0; 1215)); omuz_sag x 86…191, y 1165…1305;
# dirsek_sag x 162…228, y 899…1119; sol kol x aynası; kabuk x −259…259, y 60…1268. Kutu (xmin, xmax, ymin, ymax); z sınanmaz.
TABAN_DISI_BOLGE = (("kafa", (-60.0, 60.0, 1200.0, 1600.0)), ("sağ kol", (60.0, 260.0, 880.0, 1320.0)),
                    ("sol kol", (-260.0, -60.0, 880.0, 1320.0)), ("gövde", (-260.0, 260.0, GEO_TABAN_DISI, 1280.0)))
TABAN_DISI_PARCA = ((r"^Sağ kol ", "sağ kol"), (r"^Sol kol ", "sol kol"), (r"^Kafa |\(kafa\)$", "kafa"), (r"^USB hub", "gövde"))
# Dallanan yol: baş noktası ana yolun noktası (≤ 1 mm, sınanır). Dalda eşlenen kablo dalın kendi noktalarıyla ve ana yolun yalnız
# ayrılma noktasına kadarki bölümüyle sınanır (kablo o gövdeden gelir); ana yolun ayrılmadan sonraki kolu dala sayılmaz (kontrol-2 G1,
# G3). Dalın başı uç sayılmaz.
GEO_DAL = {4: 3}                                                        # yol 4, yol 3'ün (-50; 145; 60) noktasından ayrılır
GEO_ISTISNA = {
    # P10.7b2f: 12 kalktı; yolun eski üst bölümü rehberde kırpılır (CAD_KIRP), kırpılmış yolun iki ucu da B01'in uçlarında
    # P10.7b2i: 9 kalktı; yolun XL4016 çevre → ESP32 bölümü (eski tasarım) rehberde kırpılır (CAD_KIRP), kırpılmış yolun iki ucu G18'in uçlarında
}
# P10.7b2f: rehberde kırpılan CAD yolları. Model (taban_parcalar.py YOL) değişmez; rehber_veri.py parçanın gövdesini kesim düzleminin
# (yon · p ≤ kesim) yanında bırakır, sınamalar (geometri_denetle, demet_yol_adimlari, veri GLB sınaması) aynı kırpılmış noktalarla yürür.
# Kesim = korunan noktaların yon üstündeki en büyük izdüşümü + tüp yarıçapı (taban_parcalar.tup r = 2.5; tüp her noktada küre, aralarda
# silindir: korunan bölümün tamamı düzlemin bu yanında kalır). yon yoksa (0, 1, 0): kesim düzlemi y = sabit (yol 12, b2f'deki gibi).
# Yol 12: noktalar[0..2] B01'in gerçek yolu (BTS7960 sol → ESP32 taşıyıcısının merkezi (80; 75), kablo_yolu_taban.py ESP konumu);
# noktalar[3..] 05.11 öncesi "ESP32 → kafa USB" hattı (direk boyunca y 1325'e çıkar), ESP32 USB artık "ESP32 USB" şemasında çizilir.
# P10.7b2i (F10r-gunluk § 1), P10.7b2k düzeltme turu 2-3 (CAD turu 2, F10v: yol 9 16 nokta, yıldız 4'ten geçer): Yol 9:
# noktalar[0..12] G18'in yolu (sigorta kutusu F4 (0; 215,5; −203) → yıldız 4 (25; 194; −65) noktalar[5] → XL4016 çevre (49,2; 125; 75)
# noktalar[12], XL4016 çevrenin kutusunun içinde); noktalar[13..15] eski tasarımın çevre 5 V → ESP32 hattı (bugün G19 arayüz kartına
# gider, kendi şeması K1'de). İki bölümün y aralıkları çakışıyor (korunan 125…219, atılan 150…200): y düzlemi ayıramaz. Düzlem normali
# (0, 1, 1) / √2 (y + z izdüşümü): korunan en büyük 200 / √2 = 141,42 (noktalar[12]), atılan en küçük 275 / √2 = 194,45 (noktalar[15],
# ESP32 ucu); kesim 143,92, ESP32 ucuyla arada 50 mm (kalıntı yok; z ≤ 77,5 kesimi ESP32 ucunda kısa bir parça bırakıyordu, F10q § 3).
CAD_TUP_R = 2.5
CAD_KIRP = {
    # düzeltme turu 2 (F10u-kontrol T1, F10v § 5): CAD turu 2'de yol 9 yıldız 4'ten başlıyor (16 nokta), G18'in XL4016 ucu noktalar[12]
    9: dict(son=12, yon=(0.0, 1.0, 1.0),
            gerekce="yolun noktalar[13..] bölümü eski tasarımın XL4016 çevre → ESP32 hattı (çevre 5 V doğrudan ESP32'ye); G18'in XL4016 ucu "
                    "taban-analiz.json kablo_yolu[8].noktalar[12] (XL4016 çevrenin kutusunda); y aralıkları çakıştığı için kesim y + z "
                    "yönünde; rehber yalnız noktalar[0..12]'yi çizer"),
    12: dict(son=2, gerekce="yolun noktalar[3..] bölümü 05.11 öncesi ESP32 → kafa USB hattı (direk boyunca kafaya çıkar); B01'in ESP32 ucu "
                            "taban-analiz.json kablo_yolu[11].noktalar[2] = ESP32 taşıyıcısının merkezi; rehber yalnız noktalar[0..2]'yi çizer"),
}


def cad_noktalar(n, analiz=None, kirp=True):
    """Yol n'in noktaları (taban-analiz.json); kirp ise CAD_KIRP'e göre rehberin çizdiği bölüm."""
    A = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    pts = A["kablo_yolu"][n - 1]["noktalar"]
    k = CAD_KIRP.get(n) if kirp else None
    return pts[:k["son"] + 1] if k else pts


def cad_kirp_yon(n):
    """Yol n'in kesim düzlemi normali (birim vektör; CAD_KIRP[n]["yon"], yoksa +y). Kırpılmıyorsa None."""
    if n not in CAD_KIRP:
        return None
    y = CAD_KIRP[n].get("yon", (0.0, 1.0, 0.0))
    u = math.sqrt(sum(c * c for c in y))
    if u <= 0:
        raise ValueError("CAD_KIRP %d: yon sıfır vektör" % n)
    return tuple(c / u for c in y)


def izdusum(p, yon):
    return sum(a * b for a, b in zip(p, yon))


# P10.7b2f (F10m-kare-inceleme § 6, "ana kaldıraç"): uç etiketleri. Kablolar.json damar uçlarının kısa adı (damar a / b metninin " · "
# öncesi) → modeldeki parça (CAD etiketi deseni, gerekirse modül). Etiketin metni bu kısa addır, yeri parçanın robot.glb'deki kutusunun
# merkezi (rehber_gorunum.uc_isle); elle koordinat yok. Modelde parçası olmayan uç (bara, düğüm, klemens, konnektör) UC_MODELSIZ'de
# gerekçesiyle: karede etiketlenmez, basılı sayfada "karede görünmez" diye yazılır. uc_etiket_denetle: her kısa ad iki tablodan
# birinde, desen modelde tam bir parçaya (modül süzgeciyle) uyuyor.
UC_ETIKET = {
    "Akü": (r"^Aku LiFePO4", None), "Ana anahtar": (r"^Ana anahtar ASW", None), "Ana sigorta yuvası": (r"^Ana sigorta yuvasi", None),
    "Sigorta kutusu": (r"^Sigorta kutusu", None), "Röle K1": (r"^Role 12 V", None), "Ön şarj kartı": (r"^On sarj karti", None),
    "BTS7960 sol": (r"^BTS7960 motor surucu sol$", None), "BTS7960 sağ": (r"^BTS7960 motor surucu sag$", None),
    "JGB37 ön sol": (r"^Motor JGB37-520 \(on sol\)", None), "JGB37 ön sağ": (r"^Motor JGB37-520 \(on sag\)", None),
    "JGB37 arka sol": (r"^Motor JGB37-520 \(arka sol\)", None), "JGB37 arka sağ": (r"^Motor JGB37-520 \(arka sag\)", None),
    "XL4016 A": (r"^XL4016 servo 6 V A", None), "XL4016 B": (r"^XL4016 servo 6 V B", None), "XL4016 C": (r"^XL4016 servo 6 V C", None),
    "XL4016 çevre": (r"^XL4016 cevre 5 V", None),
    "Dağıtım kartı A": (r"^Servo dagitim karti A", None), "Dağıtım kartı B": (r"^Servo dagitim karti B", None),
    "Arayüz kartı": (r"^Arayuz karti", None), "PC817 modülü": (r"^Arayuz karti", None),       # PC817 arayüz kartının üstünde (modeli yok)
    "ESP32": (r"^ESP32 DevKit", None), "PCA9685": (r"^PCA9685", None), "BNO055": (r"^BNO055 IMU", None),
    "HC-SR04 sağ": (r"^Sonar HC-SR04 \(sag\)", None), "HC-SR04 orta": (r"^Sonar HC-SR04 \(orta\)", None),
    "HC-SR04 sol": (r"^Sonar HC-SR04 \(sol\)", None),
    "Acil stop mantarı": (r"^Acil stop kontak govdesi", None),
    "Raspberry Pi 5": (r"^Raspberry Pi 5", None), "Kamera": (r"^Kamera Raspberry Pi Camera", None), "QLED": (r"^Yuz ekrani WaveShare", None),
    "SY8205": (r"^SY8205 kafa", None), "D24V50F5": (r"^5 V cevirici Pololu", None), "PAM8403": (r"^PAM8403", None),
    "ReSpeaker": (r"^ReSpeaker", None), "Hoparlör": (r"^Hoparlor 40 x 20", None), "USB hub": (r"^USB Hub 4", None),
    "Göğüs ekranı": (r"^Gogus ekrani 11,6", None),
    # P10.7b2k (K64 a, P10.7b2j): baralar tutucularıyla modelde; etiket tutucunun kutusunda (bara modelde ayrı parça değil)
    "Anahtarlı bara": (r"^Bara tutucusu anahtarli bara", None), "Yıldız barası": (r"^Bara tutucusu yildiz barasi", None),
    "kafa pan servosu": (r"^Pan servosu MG996R", None), "kafa tilt servosu": (r"^Tilt servosu MG996R", None),
    "sağ S1 (omuz öne-arka) servosu": (r"^S1 servo DS3235", "omuz_sag"), "sağ S2 (omuz yana) servosu": (r"^S2 servo DS3235", "omuz_sag"),
    "sol S1 (omuz öne-arka) servosu": (r"^S1 servo DS3235", "omuz_sol"), "sol S2 (omuz yana) servosu": (r"^S2 servo DS3235", "omuz_sol"),
    "sağ dirsek servosu": (r"^Dirsek servosu MG996R", "dirsek_sag"), "sağ bilek servosu": (r"^Bilek servosu MG996R", "dirsek_sag"),
    "sol dirsek servosu": (r"^Dirsek servosu MG996R", "dirsek_sol"), "sol bilek servosu": (r"^Bilek servosu MG996R", "dirsek_sol"),
}
UC_MODELSIZ = {
    "Acil stop düğümü (mantar NC çıkışı)": "düğüm kartı modelde yok", "XT60 (akü tarafı)": "konnektör modelde yok",
    "XT60 (robot tarafı)": "konnektör modelde yok", "XT60E-F şarj girişi": "konnektör modelde yok (K50)",
    "Dağıtım kartı C (kafa)": "kafa dağıtım kartı modelde yok", "Kafa giriş klemensi": "klemens modelde yok",
    "Göğüs regülatörü": "regülatör modelde yok (K52 a: güç panelinde)", "Ses bölücüsü": "bölücü modelde yok",
}


def uc_kisa(d):
    """Damar ucu metni ("ESP32 · GPIO25") → kısa ad ("ESP32")."""
    return (d or "").split(" · ")[0].strip()


def uc_etiket_denetle(TB=None, cad=None):
    """Her damar ucunun kısa adı UC_ETIKET ya da UC_MODELSIZ'de (ikisinde birden değil); cad (rehber_gorunum.cad_parcalar()) verilirse
    UC_ETIKET deseni modelde (modül süzgeciyle) tam bir parçaya uyar. Döner hata listesi."""
    TB = TB or Tablo()
    hata = []
    adlar = set()
    for k, r in TB.K.items():
        for d in r.get("damarlar") or []:
            for y in "ab":
                if d.get(y):
                    adlar.add(uc_kisa(d[y]))
    for a in sorted(adlar):
        if a in UC_ETIKET and a in UC_MODELSIZ:
            hata.append("uç etiketi: %s hem UC_ETIKET hem UC_MODELSIZ'de" % a)
        elif a not in UC_ETIKET and a not in UC_MODELSIZ:
            hata.append("uç etiketi: %s sınıflanmamış (UC_ETIKET'e desen ya da UC_MODELSIZ'e gerekçe)" % a)
    for a in sorted(set(UC_ETIKET) | set(UC_MODELSIZ)):
        if a not in adlar:
            hata.append("uç etiketi: %s kablolar.json damar uçlarında yok (eski kayıt)" % a)
    if cad is not None:
        for a, (desen, mod) in sorted(UC_ETIKET.items()):
            n = sum(1 for c in cad if re.search(desen, c["etiket"]) and (mod is None or c["modul"] == mod))
            if n != 1:
                hata.append("uç etiketi: %s deseni %r%s modelde %d parçaya uyuyor (1 beklenir)" % (a, desen, " (%s)" % mod if mod else "", n))
    return hata


def cad_kirp_kesim(n, analiz=None):
    """Yol n kırpılıyorsa rehberdeki kesim (yon, d): rehber yon · p ≤ d yanını çizer (global, mm); kırpılmıyorsa None."""
    yon = cad_kirp_yon(n)
    if yon is None:
        return None
    return yon, max(izdusum(p, yon) for p in cad_noktalar(n, analiz)) + CAD_TUP_R


def cad_kirp_metin(n, analiz=None):
    """Kesimin kısa yazımı (log, onay kaydı): y yönünde b2f biçimi "y ≤ 192.5", başka yönde "(0, 0.707, 0.707) · p ≤ 143.92"."""
    yon, d = cad_kirp_kesim(n, analiz)
    if yon == (0.0, 1.0, 0.0):
        return "y ≤ %.1f" % d
    return "(%s) · p ≤ %.2f" % (", ".join("%.4g" % c for c in yon), d)


def cad_kirp_denetle(analiz=None):
    """P10.7b2i: kesim korunan bölümü eski bölümden ayırıyor mu (FreeCAD istemez). Atılan noktaların (noktalar[son+1..]) küreleri
    düzlemin öbür yanında olmalı: yon · p − r > d (aradaki silindirler de dışarıda kalır, dışbükey). Korunan bölüm kurulumdan dolayı
    içeride. Ayırmayan kesim rehber_veri.py'de "eski kısım kaldı" olurdu; burada kaynakta yakalanır. Döner hata listesi."""
    A = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    hata = []
    for n in sorted(CAD_KIRP):
        try:
            yon, d = cad_kirp_kesim(n, A)
        except (ValueError, IndexError, KeyError) as e:
            hata.append("CAD_KIRP yol %d: kesim kurulamadı (%s)" % (n, e))
            continue
        tum = cad_noktalar(n, A, kirp=False)
        son = CAD_KIRP[n]["son"]
        if not 0 < son < len(tum) - 1:
            hata.append("CAD_KIRP yol %d: son %d, yolun %d noktası var (kesecek bölüm yok ya da baş kesiliyor)" % (n, son, len(tum)))
            continue
        kalan = [(i, round(izdusum(p, yon) - CAD_TUP_R, 2)) for i, p in enumerate(tum) if i > son and izdusum(p, yon) - CAD_TUP_R <= d]
        if kalan:
            hata.append("CAD_KIRP yol %d: kesim (%s) eski bölümü ayırmıyor; düzlemin korunan yanında kalan atılan noktalar %s" % (
                n, cad_kirp_metin(n, A), kalan))
    return hata

# Kol içi yol bölümleri (rehber_kol_kablo.py bölüm anahtarı, sağ kol) → kimlikler. Sol kol aynı bölümler: SAG_SOL ile çevrilir.
# Bölüm "isaret" ise (ek yeri, ek noktası, kablo bağı) kablo değil, kendi işaret rengini korur; kimliği bilgi içindir.
# "servo_*": servonun kendi kablosu (tabloda ayrı kayıt yok): bağlandığı uzatmanın devresinde, ana kimlik o uzatma.
KOL_ESLEME = {
    "servo_bilek": ("S04",), "servo_dirsek": ("S03",), "lop_dirsek": ("S03", "S04"), "tup_ici": ("S03", "S04"),
    "tup_ara": ("S04", "S03"), "uzatma_tup": ("S03", "S04"), "uzatma_kol": ("S03", "S04"), "lop_s2": ("S03", "S04"),
    "gecis_s1": ("S02", "S03", "S04"), "s1_lop": ("S02", "S03", "S04"), "s1_cikis": ("S02", "S03", "S04"), "govde": ("S02", "S03", "S04"),
    "s1_-45": ("S02", "S03", "S04"), "s1_+135": ("S02", "S03", "S04"),
    "ek_jr": ("S03",), "ek_bilek": ("S04",), "nokta_lehim": ("S04",), "nokta_jr": ("S03",), "bag_k": ("S03", "S04"),
    "bag_tambur": ("S02", "S03", "S04"),
}
KOL_ISARET_TUR = ("ek", "ek_b", "bag", "ek_nokta")                    # rehber_kol_kablo RENK türleri: işaret (rengini korur)
SAG_SOL = {"S01": "S05", "S02": "S06", "S03": "S07", "S04": "S08"}


# P10.7b2c düzeltme turu 1 (F10k-kontrol D3): kayıttaki adı yanlış yer çağrıştıran uç parçası. Kayıttaki ad değişmez (kablolar.json);
# rehberde bu ad geçen her metinde (adım metinleri, şema adları, CAD yolu adları, tıklama kartı / kablo listesindeki kb satırları) kartın
# gerçek yeri de yazılı olmalı (uc_yer_eki_denetle; ek kb satırına bilgi_satiri'nde girer). Yer: kablolar.json karar P7b2a-6.
UC_YER_EK = {"Dağıtım kartı C (kafa)": "kart güç panelinde, XL4016 C'nin yanında; adındaki \"kafa\" beslediği pan / tilt servolarıdır"}


def uc_yer_eki(uc):
    """'Dağıtım kartı C (kafa) · V+' → 'Dağıtım kartı C (kafa) (kart güç panelinde, …) · V+' (UC_YER_EK; yalnız görünen metin)."""
    for ad, ek in UC_YER_EK.items():
        if uc == ad or uc.startswith(ad + " "):
            return ad + " (" + ek + ")" + uc[len(ad):]
    return uc


def tablo_yukle(yol=TABLO_YOL):
    return json.load(open(yol, encoding="utf-8"))


class Tablo:
    """kablolar.json üstünde türetme işlevleri."""

    def __init__(self, T=None):
        self.T = T if T is not None else tablo_yukle()
        self.K = {r["kimlik"]: r for r in self.T["kablolar"]}
        self.S = self.T["renk_kurali"]["siniflar"]
        self.KOR = self.T.get("koruyucular", {})

    # -- tek kablo
    def sinif(self, kimlik):
        return self.K[kimlik]["renk"]["sinif"]

    def renk(self, kimlik):
        c = self.S.get(self.sinif(kimlik))                           # sınıf renk kuralında yoksa siyah yer tutucu (kaynak_denetle hata yazar)
        return c["cizim"] if c else "#000000"

    def yaricap(self, kimlik):
        r = self.K[kimlik]
        k = r.get("kesit") or {}
        if k.get("awg") in KESIT_YARICAP:
            return KESIT_YARICAP[k["awg"]]
        if k.get("mm2"):
            return max(R_VARSAYILAN, round(2.5 + 1.8 * (math.sqrt(k["mm2"]) - math.sqrt(0.33)), 1))
        hk = r.get("hazir_kablo") or {}
        cap = (hk.get("sart") or {}).get("dis_cap_mm_en_cok")
        if r["renk"]["sinif"] == "hazir" and cap:
            return max(R_VARSAYILAN, round(cap / 2.0, 1))
        return R_VARSAYILAN

    def alt_sinif(self, kimlik):
        """Hazır kablonun türü (kimliğin harfi: U USB, H HDMI, C CSI) ya da sınıfın kendisi."""
        s = self.sinif(kimlik)
        if s == "hazir" and kimlik[0] in HAZIR_TUR:
            return HAZIR_TUR[kimlik[0]][0]
        return s

    def ton(self, kimlik):
        """Tema tonları {light, dark[, cekirdek_dark]}; tanımsızsa sınıf rengi iki temada."""
        return dict(TEMA_TON.get(self.alt_sinif(kimlik)) or {"light": self.renk(kimlik), "dark": self.renk(kimlik)})

    def koruma_metni(self, kimlik):
        k = self.K[kimlik].get("koruma")
        if not k:
            return "sigorta yok (hazır kablo / sinyal, besleyen hattın koruması)"
        c = self.KOR.get(k)
        if not c:
            return k
        if c.get("tur") == "sigorta":
            return "sigorta: %s" % c["ad"]
        return "koruma: %s" % c["ad"]

    def kesit_metni(self, kimlik):
        r = self.K[kimlik]
        k = r.get("kesit") or {}
        if k.get("awg"):
            return "%d AWG (%s mm²)" % (k["awg"], ("%g" % k["mm2"]).replace(".", ","))
        return r.get("kesit_not") or "kesit tabloda yok"

    def bilgi(self, kimlik):
        r = self.K[kimlik]
        d = r["damarlar"][0]
        return dict(kimlik=kimlik, ad=r["ad"], a=d["a"], b=d["b"], kesit=self.kesit_metni(kimlik), koruma=self.koruma_metni(kimlik),
                    acil=bool(r["acil_stopta_enerjili"]), sinif=r["renk"]["sinif"], durum=r.get("durum"))

    def bilgi_satiri(self, kimlik):
        b = self.bilgi(kimlik)
        return "%s: %s → %s · %s · %s · acil stopta %s" % (b["kimlik"], uc_yer_eki(b["a"]), uc_yer_eki(b["b"]), b["kesit"], b["koruma"],
                                                         "enerjili" if b["acil"] else "enerjisiz")

    # -- çizim kaydı (bir çizim nesnesi için)
    def cizim(self, kimlikler, isaret=False):
        ana = kimlikler[0]
        sinif = {self.sinif(k) for k in kimlikler}
        d = dict(kablo=list(kimlikler), ks=self.sinif(ana), kb=[self.bilgi_satiri(k) for k in kimlikler])
        if not isaret:
            d["renk"] = self.renk(ana)
            d["r"] = self.yaricap(ana)
            d["rt"] = self.ton(ana)                                   # düzeltme turu 1: tema tonu (app.js temaya göre seçer)
            if self.alt_sinif(ana) != self.sinif(ana):
                d["kt"] = self.alt_sinif(ana)                          # hazır kablo türü (lejant satırı)
        if len(sinif) > 1:
            d["karisik"] = sorted(sinif)
        return d

    def lejant(self):
        """app.js lejantı: sınıf → [renk, okunur ad, tema tonları]. Hazır kablo türleri ayrı satır (hazir-usb, hazir-hdmi, hazir-csi).
        P10.7b2e kısım 2 (F10l-kare-inceleme 32.5): beyaz kablo açık temada koyu camgöbeği (#4c7078) çizilir; lejant adı bunu söyler."""
        ad = dict(kirmizi="12 V doğrudan (kırmızı)", turuncu="Anahtarlı bara, motor (turuncu)", sari="Servo gücü 6 V (sarı)",
                  mavi="5 V (mavi)", yesil="Acil stop (yeşil)", mor="Sinyal (mor)", siyah="Toprak (siyah)", beyaz="Analog ses (beyaz; açık temada koyu çizilir)",
                  hazir="Hazır kablo: USB, HDMI, CSI (gri)")
        out = {k: [v["cizim"], ad.get(k, k), dict(TEMA_TON.get(k) or {"light": v["cizim"], "dark": v["cizim"]})] for k, v in self.S.items()}
        if "hazir" in self.S:
            for _h, (k, a) in HAZIR_TUR.items():
                out[k] = [self.S["hazir"]["cizim"], a, dict(TEMA_TON[k])]
        return out


def stil_zeminleri(yol=STIL_CSS):
    """rehber/stil.css'ten iki temanın sahne ve lejant (kart) zemini: {tema: {sahne, lejant}}."""
    s = open(yol, encoding="utf-8").read()
    acik = re.search(r":root\{([^}]*)\}", s).group(1)
    koyu = re.search(r":root\[data-theme=\"dark\"\]\{([^}]*)\}", s).group(1)
    def al(blok, ad):
        h = re.search(r"--%s:#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b" % ad, blok).group(1)
        return "#" + (h if len(h) == 6 else "".join(c * 2 for c in h)).lower()
    return {"light": {"sahne": al(acik, "sahne"), "lejant": al(acik, "card")}, "dark": {"sahne": al(koyu, "sahne"), "lejant": al(koyu, "card")}}


def _parlaklik(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def karsitlik(a, b):
    x, y = _parlaklik(a), _parlaklik(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def karsitlik_tablosu(TB=None, zemin=None):
    """[(sınıf, tema, ton, sahne karşıtlığı, lejant karşıtlığı)] — lejantın her satırı için."""
    TB = TB or Tablo()
    zemin = zemin or stil_zeminleri()
    out = []
    for k, (_r, _a, ton) in TB.lejant().items():
        if k == "hazir" and any(x in TB.lejant() for x, _ in HAZIR_TUR.values()):
            continue                                                   # hazır kablolar tür satırlarıyla çizilir
        for tm in ("light", "dark"):
            out.append((k, tm, ton[tm], round(karsitlik(ton[tm], zemin[tm]["sahne"]), 2), round(karsitlik(ton[tm], zemin[tm]["lejant"]), 2)))
    v, _s = vurgu_tonlari()                                            # P10.7b2a: seçim vurgusu da (app.js VURGU_TON)
    for tm in ("light", "dark"):
        out.append(("vurgu", tm, v[tm], round(karsitlik(v[tm], zemin[tm]["sahne"]), 2), round(karsitlik(v[tm], zemin[tm]["lejant"]), 2)))
    return out


def karsitlik_denetle(TB=None, zemin=None):
    return ["kablo tonu %s (%s, %s): zemine karşı %.2f / lejant %.2f < %.1f" % (k, tm, t, a, b, KARSITLIK_ESIK)
            for k, tm, t, a, b in karsitlik_tablosu(TB, zemin) if min(a, b) < KARSITLIK_ESIK]


# ------------------------------------------------------------------ tonlar arası renk farkı (P10.7b1 açık işler turu, kontrol-2 madde 17)
# CIEDE2000 (ΔE00; sRGB → CIE XYZ (D65) → CIELAB, kL = kC = kH = 1). Lejantın her satırı aynı temadaki her satırla karşılaştırılır.
def _lab(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    X = (0.4124564 * c[0] + 0.3575761 * c[1] + 0.1804375 * c[2]) / 0.95047
    Y = 0.2126729 * c[0] + 0.7151522 * c[1] + 0.0721750 * c[2]
    Z = (0.0193339 * c[0] + 0.1191920 * c[1] + 0.9503041 * c[2]) / 1.08883
    f = [t ** (1 / 3.0) if t > 216 / 24389.0 else (24389 / 27.0 * t + 16) / 116.0 for t in (X, Y, Z)]
    return 116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])


def de2000(a, b):
    L1, a1, b1 = _lab(a)
    L2, a2, b2 = _lab(b)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cm = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if C1p else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if C2p else 0.0
    dL, dC = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dh = 0.0
    else:
        dh = h2p - h1p
        dh = dh - 360 if dh > 180 else (dh + 360 if dh < -180 else dh)
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lm, Cmp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hm = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hm = (h1p + h2p) / 2
    else:
        hm = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm))
         + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63)))
    dth = 30 * math.exp(-(((hm - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cmp ** 7 / (Cmp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cmp, 1 + 0.015 * Cmp * T
    Rt = -math.sin(math.radians(2 * dth)) * Rc
    return math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


# Eşik: ΔE00 ≥ 15. Gerekçe: ΔE00 ≈ 1 ancak yan yana görülen fark, 2–10 "dikkatle bakınca", 10'un üstü "bir bakışta ayrı renk" sayılır;
# burada tel 3B sahnede ince bir şerit (r 2,5–4,6 mm), gölgeli ve yan yana değil, üstelik renk körlüğü payı yok. Bugünkü en yakın çiftler
# 15'in altındaydı (açık: beyaz ↔ USB gri, koyu: siyah ↔ beyaz); yeniden tonlandıktan sonra eşik bütün çiftleri ayırır. Gözle bakış
# üretimde yapılır (F10h-gunluk § 9).
RENK_FARK_ESIK = 15.0


def renk_farki_tablosu(TB=None):
    """[(tema, sınıf 1, sınıf 2, ton 1, ton 2, ΔE00)] küçükten büyüğe; hazır kablo yalnız tür satırlarıyla."""
    TB = TB or Tablo()
    L = TB.lejant()
    ad = [k for k in L if not (k == "hazir" and any(x in L for x, _ in HAZIR_TUR.values()))]
    out = []
    v, sabit = vurgu_tonlari()
    for tm in ("light", "dark"):
        for i, a in enumerate(ad):
            for b in ad[i + 1:]:
                out.append((tm, a, b, L[a][2][tm], L[b][2][tm], round(de2000(L[a][2][tm], L[b][2][tm]), 1)))
        # P10.7b2a: seçim vurgusu her kablo tonuna ve sahnenin işaret renklerine karşı; düzeltme turu 1 (F10i-kontrol A9): ana ve
        # kopya tonu, app.js'in bütün parça sınıfı renklerine karşı da (açık temada eski ana ton "lazer" sınıfına 13,4 idi)
        sn = sinif_renkleri(tm)
        for va, vt in (("vurgu", v[tm]), ("vurgu kopya", v[tm + "_kopya"])):
            for b in ad:
                out.append((tm, va, b, vt, L[b][2][tm], round(de2000(vt, L[b][2][tm]), 1)))
            for b, t in sorted(sabit.items()):
                out.append((tm, va, b, vt, t, round(de2000(vt, t), 1)))
            for b, t in sorted(sn.items()):
                out.append((tm, va, "sınıf " + b, vt, t, round(de2000(vt, t), 1)))
    return sorted(out, key=lambda x: x[5])


def siyah_l_denetle(TB=None):
    """P10.7b2a: açık temada siyah dışındaki ton siyahtan en az SIYAH_L_FARK (CIELAB L*) açık olmalı (ince çizgide siyaha karışmasın)."""
    TB = TB or Tablo()
    L = TB.lejant()
    if "siyah" not in L:
        return []
    ls = _lab(L["siyah"][2]["light"])[0]
    return ["kablo tonu %s (light, %s): L* %.1f, siyahtan (%.1f) farkı %.1f < %g (ince çizgide siyaha karışır)" % (
                k, v[2]["light"], _lab(v[2]["light"])[0], ls, _lab(v[2]["light"])[0] - ls, SIYAH_L_FARK)
            for k, v in L.items() if k not in ("siyah", "hazir") and _lab(v[2]["light"])[0] - ls < SIYAH_L_FARK]


def renk_farki_denetle(TB=None):
    return ["kablo tonları %s ↔ %s (%s: %s / %s) ΔE00 %.1f < %g" % (a, b, tm, x, y, d, RENK_FARK_ESIK)
            for tm, a, b, x, y, d in renk_farki_tablosu(TB) if d < RENK_FARK_ESIK] + siyah_l_denetle(TB)


def cad_no(ad):
    m = re.match(r"Kablo yolu (\d+)\b", ad or "")
    return int(m.group(1)) if m else None


def kol_kimlik(anahtar):
    """'sag:tup_ici' / 'sol:tup_ici' → kimlikler (sol kol S05–S08)."""
    yan, k = anahtar.split(":", 1)
    ids = KOL_ESLEME.get(k)
    if ids is None:
        return None
    return tuple(SAG_SOL.get(i, i) if yan == "sol" else i for i in ids)


# ------------------------------------------------------------------ kaynak denetimi
def kaynak_denetle(TB=None, RM=None, kol_bolumler=None):
    """Eşlemenin kendisi: kimlik var mı, her şema / CAD numarası / kol bölümü eşlenmiş mi, renk sınıfı tanımlı mı. Doner (hata, bilgi)."""
    TB = TB or Tablo()
    if RM is None:
        import rehber_metin as RM
    hata = []

    def var(yer, ids):
        if not ids:
            hata.append("%s: kablo kimliği yok" % yer)
            return
        for i in ids:
            if i not in TB.K:
                hata.append("%s: bilinmeyen kablo kimliği %s (kablolar.json'da yok)" % (yer, i))
            elif TB.K[i]["renk"]["sinif"] not in TB.S:
                hata.append("%s: %s devre sınıfı renk kuralında yok: %s" % (yer, i, TB.K[i]["renk"]["sinif"]))
    for n, ids in CAD_ESLEME.items():
        var("CAD Kablo yolu %d" % n, ids)
    for n in RM.KABLO_AD:
        if n not in CAD_ESLEME:
            hata.append("KABLO_AD %d: CAD eşlemesi yok (rehber_kablo.CAD_ESLEME)" % n)
    for n in CAD_ESLEME:
        if n not in RM.KABLO_AD:
            hata.append("CAD_ESLEME %d: KABLO_AD'da yok" % n)
    for s in RM.SEMA:
        if len(s) != 5 or not isinstance(s[4], (tuple, list)):
            hata.append("SEMA %s: son alan kablo kimlikleri olmalı (renk değil)" % (s[1],))
            continue
        var("SEMA %s" % s[1], s[4])
        # şemanın adımı ana kablonun rehber adımlarından biri olmalı (tablo ↔ rehber adımı)
        if s[4] and s[4][0] in TB.K:
            kodlar = {x["kod"] for x in TB.K[s[4][0]].get("rehber", [])}
            if kodlar and s[2] not in kodlar:
                hata.append("SEMA %s: adım %s, ana kablo %s tabloda %s adımlarında" % (s[1], s[2], s[4][0], sorted(kodlar)))
    for k, ids in KOL_ESLEME.items():
        var("KOL %s" % k, ids)
        var("KOL sol:%s" % k, kol_kimlik("sol:" + k))
    if kol_bolumler is not None:
        for k in kol_bolumler:
            if k not in KOL_ESLEME:
                hata.append("kol bölümü %s eşlenmemiş (rehber_kablo.KOL_ESLEME)" % k)
        for k in KOL_ESLEME:
            if k not in kol_bolumler:
                hata.append("KOL_ESLEME %s: rehber_kol_kablo'da böyle bölüm yok" % k)
    # düzeltme turu 1: yarıçap kademeleri (en ince ≥ R_VARSAYILAN, komşu kademe ≥ %15, en az dört kademe)
    yk = [KESIT_YARICAP[a] for a in sorted(KESIT_YARICAP, reverse=True)]
    if len(yk) < 4 or yk[0] < R_VARSAYILAN:
        hata.append("KESIT_YARICAP: en az dört kademe ve en ince ≥ %g olmalı (%s)" % (R_VARSAYILAN, yk))
    for a, b in zip(yk[:-1], yk[1:]):
        if b < a * 1.15:
            hata.append("KESIT_YARICAP: komşu kademeler %g → %g, fark %%15'ten az" % (a, b))
    # düzeltme turu 1: her sınıfın tema tonu var ve iki temanın zeminine karşı ≥ KARSITLIK_ESIK
    for k in TB.S:
        if k not in TEMA_TON and k != "hazir":
            hata.append("renk sınıfı %s: TEMA_TON'da tonu yok" % k)
    hata += karsitlik_denetle(TB)
    hata += renk_farki_denetle(TB)                                   # açık işler turu: tonlar birbirinden ayrılmalı (ΔE00)
    return hata


def _kutu_mesafe(p, bb):
    d = 0.0
    for k in range(3):
        lo, hi = bb[2 * k], bb[2 * k + 1]
        e = lo - p[k] if p[k] < lo else (p[k] - hi if p[k] > hi else 0.0)
        d += e * e
    return math.sqrt(d)


def _yol_kutu(pts, bb, adim=2.0):
    """Kırık çizginin kutuya en kısa uzaklığı (≈ adim mm örnekleme)."""
    best = _kutu_mesafe(pts[0], bb)
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.dist(a, b)
        n = max(1, int(L / adim))
        for i in range(n + 1):
            t = i / n
            best = min(best, _kutu_mesafe([a[k] + (b[k] - a[k]) * t for k in range(3)], bb))
    return best


def uc_parcalari(TB, kimlik):
    """(a ucu parçaları, b ucu parçaları): kablonun kendi uçları (uc_a / uc_b; dönüş damarının yıldız ucu yan sayılmaz)."""
    r = TB.K[kimlik]
    return [r["uc_a"]["parca"]], [r["uc_b"]["parca"]]


def _onek(p, tablo):
    k = [x for x in tablo if p == x or p.startswith(x + " ")]
    return max(k, key=len) if k else None


def parca_sinifi(p):
    if re.search(TABAN_DISI_DESEN, p):
        return TABAN_DISI
    k = _onek(p, PARCA_CAD)
    return PARCA_CAD[k] if k else None


def uc_kutbu(TB, kimlik, yan):
    """Ucun kutbu: uc_a / uc_b 'nokta' alanı tek başına "+" ya da "−" ise o; değilse kablonun ilk damarı."""
    r = TB.K[kimlik]
    n = (r["uc_" + yan].get("nokta") or "").strip()
    return n if n in ("+", "−") else r["damarlar"][0]["ad"]


def modelsiz_konum(p, kutup):
    """MODELSIZ_KONUM girdisi (nokta, vekil, gerekçe) ya da None (tabloda yok → hata)."""
    k = _onek(p, {a for a, _b in MODELSIZ_KONUM})
    if k is None:
        return None
    return MODELSIZ_KONUM.get((k, kutup)) or MODELSIZ_KONUM.get((k, "*"))


def bolge(nokta):
    """Taban dışı uç noktasının bölgesi (TABAN_DISI_BOLGE'de ilk tutan) ya da None."""
    for ad, (x0, x1, y0, y1) in TABAN_DISI_BOLGE:
        if x0 <= nokta[0] <= x1 and y0 <= nokta[1] <= y1:
            return ad
    return None


def parca_bolgesi(p):
    for d, ad in TABAN_DISI_PARCA:
        if re.search(d, p):
            return ad
    return None


def uc_imzasi(TB, kimlik):
    """Geometrinin bir kablo için görebildiği her şey: iki yanın (sınıf / desen, kutup noktası, bölge) kümesi."""
    out = []
    for y, parcalar in zip("ab", uc_parcalari(TB, kimlik)):
        p = parcalar[0]
        s = parca_sinifi(p)
        if s == TABAN_DISI:
            out.append(("bölge", parca_bolgesi(p)))
        elif s in (NOMINAL, MODELSIZ):
            m = modelsiz_konum(p, uc_kutbu(TB, kimlik, y)) or (None, None, "")
            if m[0] is None and m[1]:
                out.append(("parça", m[1]))                          # vekil parça: geometri için o parçanın kendisi
            else:
                out.append(("nominal", m[0]) if m[0] else ("elle", p))
        else:
            out.append(("parça", s))
    out.append(("sınıf", TB.sinif(kimlik)))                           # P10.7b2b (R8 b): sınıf kuralı devre sınıfını da ayırır
    return frozenset(out)


def ayirt_edilemeyen(TB=None, esleme=None):
    """Geometrinin ayırt edemediği çiftler: eşlenen bir kablo ile aynı uç imzalı başka bir kablo (aynı yolda eşli olmayan).
    Doner [(yol, eşlenen, öbürü, öbürünün eşlendiği yollar)]."""
    TB = TB or Tablo()
    esleme = CAD_ESLEME if esleme is None else esleme
    imza = {k: uc_imzasi(TB, k) for k in TB.K if all(parca_sinifi(p[0]) for p in uc_parcalari(TB, k))}
    nerede = {}
    for n, ids in esleme.items():
        for i in ids:
            nerede.setdefault(i, []).append(n)
    out = []
    for n, ids in sorted(esleme.items()):
        for m in ids:
            if m not in imza:
                continue
            for k in sorted(imza):
                if k != m and imza[k] == imza[m] and n not in nerede.get(k, []):
                    out.append((n, m, k, nerede.get(k, [])))
    return out


ELLE = "elle"                                                          # sınanmayan (elle bakılan) yan: doğru sayılır ama geometri değil


def _yan_sina(TB, k, y, parcalar, cizgiler, dis_bolge, cad, sinif_f=None, bolge_f=None, konum_f=None):
    """Kablonun bir yanı (a / b) ↔ yolun çizgileri. Doner dict(sonuc=[True / False / ELLE], uc, nominal, disi, elle, hata, bilgi);
    iletiler yol numarasız ("<kimlik>: …"). sinif_f / bolge_f / konum_f: P10.7b2c şema sınaması kendi parça haritasını geçirir
    (varsayılan CAD yollarınınki: parca_sinifi, parca_bolgesi, modelsiz_konum)."""
    parca_sinifi_, parca_bolgesi_ = sinif_f or parca_sinifi, bolge_f or parca_bolgesi
    modelsiz_konum_ = konum_f or modelsiz_konum
    r = dict(sonuc=[], uc=set(), nominal=[], disi=set(), elle=False, hata=[], bilgi=[])
    for p in parcalar:
        s = parca_sinifi_(p)
        if s is None:
            r["hata"].append("%s: uç parçası '%s' PARCA_CAD haritasında yok" % (k, p))
            r["sonuc"].append(False)
        elif s == TABAN_DISI:
            b = parca_bolgesi_(p)
            if b is None:
                r["hata"].append("%s: taban dışı uç '%s' TABAN_DISI_PARCA'da bölgesiz" % (k, p))
                r["sonuc"].append(False)
                continue
            r["disi"].add(b)
            r["sonuc"].append(b in dis_bolge)
        elif s in (NOMINAL, MODELSIZ):
            m = modelsiz_konum_(p, uc_kutbu(TB, k, y))
            if m is None:
                r["hata"].append("%s: modelsiz uç '%s' MODELSIZ_KONUM'da yok" % (k, p))
                r["sonuc"].append(False)
                continue
            nokta, vekil, _g = m
            if nokta is None and vekil is None:
                r["elle"] = True
                r["bilgi"].append("%s %s: '%s' modelsiz, nominal konumu yok: elle bakıldı" % (k, y, p))
                r["sonuc"].append(ELLE)
                continue
            vp = cad(vekil) if vekil else []
            r["uc"].update(c["ad"] for c in vp)
            if nokta is not None:
                r["nominal"].append(nokta)
                d = min(_yol_kutu(c_, (nokta[0], nokta[0], nokta[1], nokta[1], nokta[2], nokta[2])) for c_ in cizgiler)
            elif vp:
                d = min(_yol_kutu(c_, c["bb"]) for c in vp for c_ in cizgiler)
                r["vekil"] = True                                     # yalnız vekil parçayla: eksik eşleme kanıtı sayılmaz
            else:
                r["hata"].append("%s: '%s' vekili için CAD parçası bulunamadı (%s)" % (k, p, vekil))
                r["sonuc"].append(False)
                continue
            r["sonuc"].append(d <= GEO_ESIK)
        else:
            cp = cad(s)
            if not cp:
                r["hata"].append("%s: '%s' için CAD parçası bulunamadı (%s)" % (k, p, s))
                r["sonuc"].append(False)
                continue
            d = min(_yol_kutu(c_, c["bb"]) for c in cp for c_ in cizgiler)
            r["uc"].update(c["ad"] for c in cp)
            r["sonuc"].append(d <= GEO_ESIK)
    return r


def geometri_denetle(TB=None, analiz=None, esleme=None, istisna=None):
    """CAD yolu noktaları ↔ eşlenen kabloların uç parçaları (kural yukarıda). Doner (hata, bilgi)."""
    TB = TB or Tablo()
    A = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    esleme = CAD_ESLEME if esleme is None else esleme
    istisna = GEO_ISTISNA if istisna is None else istisna
    modelli = [p for p in A["parcalar"] if (p.get("tur") not in ("Baski", "Lazer", "Baglanti") or p["ad"].startswith("Bara tutucusu "))
               and not p["ad"].startswith(("Burc", "Kablo yolu"))]           # düzeltme turu 1: bara tutucuları (Baski) uç parçası
    hata, bilgi = [], []
    kullanilan_ist = set()

    def cad(desen):
        return [p for p in modelli if re.search(desen, p["ad"])]
    for n, ids in sorted(esleme.items()):
        if n > len(A["kablo_yolu"]):
            hata.append("yol %d: taban-analiz.json'da yok" % n)
            continue
        pts = cad_noktalar(n, A)                                      # P10.7b2f: rehberin çizdiği (kırpılmış) bölüm
        cizgiler = [pts]
        ana = GEO_DAL.get(n)
        if ana:
            ap = cad_noktalar(ana, A)
            j = min(range(len(ap)), key=lambda i: math.dist(pts[0], ap[i]))
            if math.dist(pts[0], ap[j]) > 1.0:
                hata.append("yol %d: GEO_DAL'a göre yol %d'den ayrılmalı, baş noktası o yolda değil" % (n, ana))
            else:
                cizgiler.append(ap[:j + 1])                           # ana yolun yalnız ayrılma noktasına kadarki bölümü
        # taban dışı uç noktaları ve bölgeleri (yalnız bu yolun kendi uçları; dalın başı ana yolun üstünde, uç sayılmaz)
        dis_uclar = [u for u in ((pts[-1],) if ana else (pts[0], pts[-1])) if u[1] >= GEO_TABAN_DISI]
        dis_bolge = {bolge(u) for u in dis_uclar}
        yan_sinif = {"disi": set(), "elle": False}
        uc_parca, nominal = set(), []
        for k in ids:
            if k not in TB.K:
                continue                                              # kaynak_denetle bilinmeyen kimliği zaten yazar
            kendi = []                                                # P10.7b2b (a): dalın kendi noktalarıyla sağlanan yan
            for y, parcalar in zip("ab", uc_parcalari(TB, k)):
                r = _yan_sina(TB, k, y, parcalar, cizgiler, dis_bolge, cad)
                hata += ["yol %d %s" % (n, x) for x in r["hata"]]
                bilgi += ["yol %d %s" % (n, x) for x in r["bilgi"]]
                yan_sinif["disi"] |= r["disi"]
                yan_sinif["elle"] = yan_sinif["elle"] or r["elle"]
                uc_parca |= r["uc"]
                nominal += r["nominal"]
                if not any(r["sonuc"]):
                    hata.append("yol %d: %s %s yanı (%s) yola ulaşmıyor (eşik %g mm / taban dışı bölge %s)" % (
                        n, k, y, ", ".join(parcalar), GEO_ESIK, "/".join(sorted(x for x in dis_bolge if x)) or "yok"))
                if ana:
                    kendi.append(any(_yan_sina(TB, k, y, parcalar, [pts], dis_bolge, cad)["sonuc"]))
            if ana and kendi and not any(kendi):
                hata.append("yol %d: %s iki yanı da yalnız ana yolun (yol %d) bölümüyle sağlanıyor, dalın kendi noktalarına ulaşmıyor "
                            "(dal kablosu değil)" % (n, k, ana))
        # P10.7b2b (b): sınıf karışımı
        sinif = sorted({TB.sinif(k) for k in ids if k in TB.K})
        if len(sinif) > 1 and tuple(sinif) != tuple(sorted(KARISIK_BILINEN.get(n, ()))):
            hata.append("yol %d: devre sınıfları karışık (%s); bilinen karışım %s" % (
                n, "/".join(sinif), "/".join(sorted(KARISIK_BILINEN[n])) if n in KARISIK_BILINEN else "yok"))
        elif n in KARISIK_BILINEN and tuple(sinif) != tuple(sorted(KARISIK_BILINEN[n])):
            hata.append("yol %d: KARISIK_BILINEN %s ama yolun sınıfları %s (tabloyu güncelle)" % (
                n, "/".join(sorted(KARISIK_BILINEN[n])), "/".join(sinif)))
        # P10.7b2b (c): eksik eşleme (yolun sınıfında, iki yanı da bu yolla sağlanan, eşlenmemiş kablo)
        for k in sorted(TB.K):
            if k in ids or TB.sinif(k) not in sinif or k in GEO_EKSIK_MUAF.get(n, {}):
                continue
            yanlar = [_yan_sina(TB, k, y, parcalar, cizgiler, dis_bolge, cad) for y, parcalar in zip("ab", uc_parcalari(TB, k))]
            if all(not r["hata"] and not r.get("vekil") and any(x is True for x in r["sonuc"]) for r in yanlar):
                hata.append("yol %d: %s kablosunun iki yanı da bu yola ulaşıyor, sınıfı yolda (%s) ama eşlenmemiş (eksik eşleme; bilinçliyse "
                            "GEO_EKSIK_MUAF'a gerekçesiyle)" % (n, k, TB.sinif(k)))
        for ad_, uc in ((("baş", pts[0]),) if not (ana and len(cizgiler) > 1) else ()) + (("son", pts[-1]),):
            neden = None
            if uc[1] >= GEO_TABAN_DISI:
                b = bolge(uc)
                if b not in yan_sinif["disi"]:
                    neden = "taban dışında %s bölgesinde bitiyor, eşlenen kabloların o bölgede ucu yok" % (b or "tanımsız")
            else:
                yakin = sorted((_kutu_mesafe(uc, c["bb"]), c["ad"]) for c in modelli)
                yakin = [a for d, a in yakin if d <= GEO_ESIK]
                if yakin:
                    if not (set(yakin) & uc_parca):
                        neden = "uç noktasının yanındaki parça (%s) eşlenen kabloların ucu değil" % yakin[0]
                elif not (yan_sinif["elle"] or any(math.dist(uc, q) <= GEO_ESIK for q in nominal)):
                    neden = "uç noktasında parça yok; eşlenen kabloların nominal noktası da elle bakılan ucu da yok"
            if neden:
                if n in istisna:
                    kullanilan_ist.add(n)
                    bilgi.append("yol %d %s ucu: %s (istisna: %s)" % (n, ad_, neden, istisna[n][:60]))
                else:
                    hata.append("yol %d %s ucu %s: %s" % (n, ad_, [round(x, 1) for x in uc], neden))
    # P10.7b2k (F10r-kontrol D4): SEMA_GEO_ISTISNA gibi, kullanılmayan GEO_ISTISNA da hata (yol düzeldiyse istisna sessizce kalmaz)
    for n in sorted(set(istisna) - kullanilan_ist):
        hata.append("GEO_ISTISNA %s: kullanılmıyor (yol düzeldiyse ya da kırpıldıysa istisnayı kaldır)" % (n,))
    return hata, bilgi


# ------------------------------------------------------------------ P10.7b2c: gösterim şemalarının geometrik uç sınaması
# Şemalar (rehber_metin.SEMA) parça değildir; CAD yolları gibi uçlarının doğru parçaya ulaştığı sınanır (FreeCAD istemez). Kaynak
# noktaları sema_noktalari() çözer (rehber_veri.py de aynısını kullanır: tek çözücü). Parça kutuları: taban-analiz.json (global) +
# kafa-analiz.json (kafa yereli + yerlesim.konum; montaj-analiz.json merkezleriyle doğrulandı, P10.7b2c günlüğü). Kural geometri_denetle
# ile aynı (GEO_ESIK, taban dışı bölge, modelsiz / nominal), şemaya özgü iki fark:
#   (1) uç noktasının ≤ GEO_ESIK mm yanında modelli parça (taban ya da kafa) varsa eşlenen kabloların uç parçası olmalı; yoksa y ≥
#       GEO_TABAN_DISI için bölge, değilse nominal / elle bakılan uç (geometri_denetle ile aynı). Kafa parçaları taban dışında da modelli.
#   (2) Şemanın tek devre sınıfı olur (bilinen karışım yok); taban altındaki şemalar (y < GEO_TABAN_DISI noktası olan) kat ve alt
#       plakayı yalnız bilinen geçişlerden geçer (kablo_yolu_taban.gecis_denetle: Ø16 delik, ön kat kesiği, akü yarıkları).
# Eksik eşleme (şemanın yanından geçtiği başka kablo) yalnız bilgi: şema bir kablonun yolunu gösterir, demet değildir.
# İstisna (SEMA_GEO_ISTISNA) anahtarı (kaynak ad, "baş" / "son" / "<kimlik> <yan>"): uç ya da yan hatasını gerekçesiyle bilgiye çevirir;
# CAD'deki GEO_ISTISNA'dan farkı yanı da bağışlayabilmesidir (anahtar yanı açıkça adlandırır; onay kaydında).
# İkinci şema kaynağı (elektronik katı kısa telleri, kafa içi, ses): kaynak işlevini SEMA_KAYNAK'a ve sema_noktalari()'na ekle; yeni
# uç parçaları PARCA_CAD'de yoksa SEMA_PARCA'ya (desen / TABAN_DISI + SEMA_PARCA_BOLGE / MODELSIZ + SEMA_MODELSIZ) yazılır.
FC_DIZIN = os.path.join(ROBOT, "tasarim", "freecad")
KAFA_ANALIZ = os.path.join(FC_DIZIN, "kafa", "kafa-analiz.json")
SEMA_KAYNAK = ("yollar", "kafa_ici_qled", "taban", "kafa_ici")              # P10.7b2c B: kafa_ici = lale158/kablo_yolu_kafa.py
SEMA_PARCA = {                                                          # şema uç parçası → kafa / taban CAD deseni ya da sınıf
    "Raspberry Pi 5": r"^Raspberry Pi 5", "Kafa ekranı 10,1\" QLED": r"QLED", "Pololu D24V50F5": r"Pololu D24V50F5",
    "SY8205": r"^SY8205 kafa", "PAM8403": r"^PAM8403", "ReSpeaker Mic Array v2.0": r"^ReSpeaker",
    "Göğüs ekranı 11,6\"": TABAN_DISI, "Hoparlör 4 Ω 3 W": TABAN_DISI,   # kabuk parçaları, kutuları analizde yok: bölge
    "Göğüs ekranı regülatörü": MODELSIZ,
    # P10.7b2c ikinci yarı (ajan B): kafa içi ve ses şemalarının uçları
    "Kamera (Camera Module 3)": r"^Kamera Raspberry Pi Camera", "Kafa giriş klemensi": NOMINAL, "Ses bölücüsü": NOMINAL,
}
# Şemada nominal konumu / vekili olan modelsiz uçlar (P10.7b2c B; MODELSIZ_KONUM biçiminde: (parça, kutup) → (nokta, vekil, gerekçe)).
# Kafa giriş kartının noktası lale158/kablo_yolu_kafa.GIRIS_KARTI'nın globali (şema sınaması ikisinin aynı olduğunu da sınar).
SEMA_KONUM = {
    ("Kafa giriş klemensi", "*"): ((-58.0, 1514.0, 30.0), None,
                                   "kafa giriş kartı (P6KE18A + 3 klemens) modelde yok, E3a yerini yazmaz: yeri yaklaşık, boyun geçişinin "
                                   "solunda tabla üstü (kablo_yolu_kafa.GIRIS_KARTI)"),
    ("Ses bölücüsü", "*"): (None, r"^PAM8403",
                            "bölücü kablo üstünde, PAM giriş pedlerinin dibinde (kablolar.json O-9): yerine PAM8403 kutusu; varlığı ve yeri "
                            "masa denemesine (KT2) bağlı"),
    # P10.7b2c düzeltme turu 1 (F10k-kontrol kaçan bozma 1): SV3'ün kart ucu artık serbest değil. CAD yolu 6'nın kart yanı
    # MODELSIZ_KONUM'da "elle" kalır (o yol kartı çizmiyor); şema sınaması bu noktayı kullanır.
    # P10.7b2k (F10u-gunluk § A4; K64 a, P10.7b2j): şemalarda baralar modelli tutucularıyla sınanır. Düzeltme turu 1-2: CAD yolları da
    # (F10v: yollar saplamalara taşındı, CAD uçları (x; 194; z ± 10), şema uçları (x; 191,9; z + 5)); saplama bara_yol_denetle'de.
    ("Anahtarlı bara", "*"): (None, r"^Bara tutucusu anahtarli bara",
                              "bara tutucusu modelde (P10.7b2j, arayuz TABAN['bara_tutucu']); şema ucu saplamasının pabuç yüksekliğinde "
                              "(kablo_yolu_taban.bara_saplama): yerine tutucunun kutusu"),
    ("Yıldız barası", "*"): (None, r"^Bara tutucusu yildiz barasi",
                             "bara tutucusu modelde (P10.7b2j): yerine tutucunun kutusu"),
    ("Dağıtım kartı C", "*"): ((100.0, 192.0, -60.0), None,
                               "kart modelde yok (R23); kayıtta güç panelinde, XL4016 C'nin yanında (kablolar.json karar P7b2a-6, SV3 "
                               "boy_tahmin 'XL4016 C klemensinin yanında'): nominal nokta XL4016 C'nin −z yanında, kutusundan 36,5 mm "
                               "(kablo_yolu_taban.DAGITIM_C); yeri yaklaşık"),
}
# Eşlemesiz şema (P10.7b2c B, brief madde 5): her şema kaynağının her yolu SEMA'da olmalı; bilinçli dışarıda bırakılan yol burada
# gerekçesiyle. SEMA'da olan ya da kaynakta artık olmayan muaf HATA (liste sessizce eskimez).
# P10.7b2k: iki eski ses yolu ("Ses karti uzatmasi", "3,5 mm -> PAM") kablo_yolu_ekran.py'den kalktı (kart modelden çıktı): muaf boş
SEMA_ESLEMESIZ_MUAF = {
}
# Göğüs ekranı ucu port girintisinde olmalı (kablo_yolu_ekran.uc_bolgesi: göğüs yerel çerçevesinde kutu, lale158_kontrol ile aynı tanım);
# TABAN_DISI_BOLGE'nin "sol kol" kutusu (x ≤ −60, y ≥ 880) göğsün sol yarısını da kapsadığı için ekran portu ayrı bölgedir.
GOGUS_PORT = "göğüs ekranı portu"
SEMA_PARCA_BOLGE = ((r"^Göğüs ekranı 11,6", GOGUS_PORT), (r"^Hoparlör ", "gövde"))
SEMA_MODELSIZ = {"Göğüs ekranı regülatörü": "regülatör güç panelinde (K52 a, B5a) ama modeli ve nominal noktası yok (model sonraki tam "
                                             "taramalı CAD paketinde): sınanmaz, elle bakıldı"}
# Mevcut 11 şemada tutmayan uçlar (P10.7b2c; geometri düzeltilmedi, F10k-gunluk.md "mevcut şemalar"). Anahtar (SEMA kaynak adı, yer).
_FIS = "fiş gövdesi kart kutusunun dışında kalır; kablo_yolu_ekran fişin arka ucunu çizer (fiş boyu TAHMİN)"
# P10.7b2i: U06 ("ESP32 USB") istisnası kalktı: şema yeniden çizildi, son nokta ESP32'nin micro USB portunun 2,5 mm önünde
# (kablo_yolu_ekran.ESP_USB_TABAN; F10r-gunluk § 2)
SEMA_GEO_ISTISNA = {
    ("HDMI", "H02 a"): "baş Pi micro HDMI 1 fişinin arka ucu (pi_hdmi, Pi kutusuna 13 mm): " + _FIS,
    ("HDMI", "baş"): "Pi micro HDMI 1 fişinin arka ucu (H02 a ile aynı): " + _FIS,
    ("HDMI (serit, 2 lehimsiz fis)", "H01 a"): "son Pi micro HDMI 0 fişinin arka ucu (hdmi0, Pi kutusuna 26 mm): " + _FIS,
    ("HDMI (serit, 2 lehimsiz fis)", "son"): "Pi micro HDMI 0 fişinin arka ucu (H01 a ile aynı): " + _FIS,
    ("Dizi USB", "U01 b"): "baş ReSpeaker micro USB fişinin arka ucu (d_uc, kart kenarı + 35 + fiş boyu 20; kutuya 19 mm): " + _FIS,
    ("Dizi USB", "baş"): "ReSpeaker micro USB fişinin arka ucu (U01 b ile aynı; kafa bölgesinin x ±60 sınırı dışında): " + _FIS,
    ("12 V", "G20 a"): "baş güç panelinde sigorta kutusunun yanında (F6 çıkışı, kutuya 13 mm); göğüs ekranı regülatörü güç panelinde "
                       "(K52 a, B5a) ama panel üstündeki yeri modelde yok: şema regülatörü çizmez, baş noktası regülatör modele girince "
                       "(sonraki tam taramalı CAD paketi) yeniden bakılır",
}


def _gogus_port(nokta, r=3.0):
    """Nokta göğüs ekranının port girintisinde mi (kablo_yolu_ekran.uc_bolgesi, gp() çerçevesinin tersi)."""
    import arayuz as A_
    import kablo_yolu_ekran as KYE
    a = math.radians(A_.GOGUS_EGIM)
    c, s = math.cos(a), math.sin(a)
    yc = A_.GOGUS_EKRAN_Y
    dy, dz = nokta[1] - yc, nokta[2] - A_.gogus_z(yc)
    q = (nokta[0], c * dy - s * dz, s * dy + c * dz)
    b = KYE.uc_bolgesi(r)
    return all(b[k][0] - 1e-6 <= q[i] <= b[k][1] + 1e-6 for i, k in enumerate("xyz"))


def sema_bolge(nokta):
    """Şema ucunun taban dışı bölgesi: önce göğüs ekranı portu, sonra TABAN_DISI_BOLGE."""
    return GOGUS_PORT if _gogus_port(nokta) else bolge(nokta)


SEMA_NOKTA_ELLE = {}                                                    # bozma denemesi: {(kaynak, ad): noktalar} kaynak yerine


def sema_noktalari(kaynak, ad_k):
    """rehber_metin.SEMA girdisinin global noktaları (ev pozu, mm) ya da None (rehber_veri.py de bunu kullanır: tek çözücü).
    yollar → lale158/kablo_yolu_ekran.yollar(); kafa_ici_qled → aynı dosyanın tilt ekseni çerçevesi + (S3 + SG / 2 + tilt_nokta);
    taban → lale158/kablo_yolu_taban.yollar() (P10.7b2c)."""
    if (kaynak, ad_k) in SEMA_NOKTA_ELLE:
        return SEMA_NOKTA_ELLE[(kaynak, ad_k)]
    for p in (FC_DIZIN, os.path.join(FC_DIZIN, "lale158")):
        if p not in sys.path:
            sys.path.insert(0, p)
    if kaynak == "yollar":
        import kablo_yolu_ekran as KYE
        return KYE.yollar().get(ad_k)
    if kaynak == "kafa_ici_qled":
        import arayuz as A_
        import kablo_yolu_ekran as KYE
        qi = KYE.kafa_ici_qled()
        if ad_k not in qi:
            return None
        y0, zt = A_.S3 + A_.SG / 2 + A_.KAFA["tilt_nokta"][1], A_.KAFA["tilt_nokta"][2]
        return [(q[0], y0 + q[1], zt + q[2]) for q in qi[ad_k][0]]
    if kaynak == "taban":
        import kablo_yolu_taban as KYT
        return KYT.yollar().get(ad_k)
    if kaynak == "kafa_ici":                                           # P10.7b2c B: kafa içi ve ses (lale158/kablo_yolu_kafa.py)
        import kablo_yolu_kafa as KYK
        return KYK.yollar().get(ad_k)
    return None


def kaynak_yollari():
    """Her şema kaynağının yol adları {kaynak: [ad]} (eşlemesiz şema sınaması; P10.7b2c B)."""
    for p in (FC_DIZIN, os.path.join(FC_DIZIN, "lale158")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import kablo_yolu_ekran as KYE
    import kablo_yolu_taban as KYT
    import kablo_yolu_kafa as KYK
    return {"yollar": list(KYE.yollar()), "kafa_ici_qled": list(KYE.kafa_ici_qled()), "taban": list(KYT.yollar()),
            "kafa_ici": list(KYK.yollar())}


def sema_sinifi(p):
    k = _onek(p, SEMA_PARCA)
    return SEMA_PARCA[k] if k else parca_sinifi(p)


def sema_bolgesi(p):
    for d, ad in SEMA_PARCA_BOLGE:
        if re.search(d, p):
            return ad
    return parca_bolgesi(p)


def sema_konum(p, kutup):
    k = _onek(p, SEMA_MODELSIZ)
    if k:
        return (None, None, SEMA_MODELSIZ[k])
    k = _onek(p, {a for a, _b in SEMA_KONUM})                         # P10.7b2c B: şemaya özgü nominal / vekil
    if k:
        return SEMA_KONUM.get((k, kutup)) or SEMA_KONUM.get((k, "*"))
    return modelsiz_konum(p, kutup)


def sema_parcalari(analiz=None, kafa=None):
    """Şema sınamasının modelli parçaları: taban (global) + kafa (yerel + yerlesim.konum); filtre geometri_denetle ile aynı."""
    A_ = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    K = kafa if kafa is not None else json.load(open(KAFA_ANALIZ, encoding="utf-8"))
    ko = K.get("yerlesim", {}).get("konum") or [0.0, 0.0, 0.0]

    def m(p):
        # P10.7b2k: bara tutucuları basılır (Baski) ama şemada bara ucunun parçasıdır (SEMA_KONUM vekili)
        if p.get("bb") and p["ad"].startswith("Bara tutucusu "):
            return True
        return p.get("bb") and p.get("tur") not in ("Baski", "Lazer", "Baglanti") and not p["ad"].startswith(("Burc", "Kablo yolu"))
    out = [dict(ad=p["ad"], bb=list(p["bb"])) for p in A_["parcalar"] if m(p)]
    out += [dict(ad=p["ad"], bb=[p["bb"][i] + ko[i // 2] for i in range(6)]) for p in K["parcalar"] if m(p)]
    return out


_BOZMA_GERI = []                                                       # P10.7b2k: bozma denemesinin modül sabiti geri almaları
# P10.7b2k düzeltme turu 1 (F10u-kontrol 1): CAD kablo yolu × bara tutucusu / saplama takımı girişimi. Yolun merkez çizgisi 1 mm
# adımla örneklenir; her örnek tüp yarıçapı (CAD_TUP_R) kadar büyütülmüş tutucu ya da saplama takımı (civata, pul, yaylı pul, somun)
# kutusunun içindeyse HATA. İzin: yolun eşlenen kablolarının bara ucu olan saplamanın ekseni çevresinde (yatay ≤ BARA_IZIN_R, y ≥ BARA_IZIN_Y) yol
# saplamaya ve tutucuya değebilir (orada biter ya da oradan geçer). Ayrıca her bara ucu kendi saplamasının izin bölgesine ulaşmalı.
# Hedef saplamalar kablolar.json bara-pabuc yerleşiminden (rehber metnindeki {saplama.X} / {bsaplama.X} ile aynı kayıt).
BARA_IZIN_R = 12.0
BARA_IZIN_Y = 189.5                                                    # tutucu üst yüzü (gövde y 179,5…189,5)
BARA_ADIM = 1.0
_BARA_TAKIM = re.compile(r"^(?:Bara civatasi|Pul M5|Yayli pul M5|Somun M5) .*\((yildiz|anahtarli) (\d)\)$")
_BARA_AD = {"yildiz": "yıldız barasının", "anahtarli": "anahtarlı baranın"}
_BARA_UC = (("Yıldız barası", "yildiz", "Yıldız barası · GND"), ("Anahtarlı bara", "anahtarli", "Anahtarlı bara · +"))


def bara_yol_hedefleri(TB=None, tablo=None):
    """[(yol, kablo, kutup, bara, saplama no)]: CAD_ESLEME'deki her kablonun kablolar.json bara-pabuc yerleşimindeki her damarı
    (ör. G17/− yıldız 4: + damarı sigorta kutusundan gelir, − damarı aynı kılıfta yıldız saplamasından ayrılır). Rehber metnindeki
    {saplama.X} / {bsaplama.X} numaraları da bu kayıttan (rehber_deger). TB kullanılmaz (imza geri uyum)."""
    T = tablo if tablo is not None else json.load(open(TABLO_YOL, encoding="utf-8"))
    kop = T["klemens_turleri"]["bara-pabuc"]["kopruler"]
    out = []
    for n in sorted(CAD_ESLEME):
        for k in CAD_ESLEME[n]:
            for onek, bara, kk in _BARA_UC:
                for no, il in sorted(kop[kk]["yerlesim"].items(), key=lambda x: int(x[0])):
                    for x in il:
                        if x.split("/")[0] == k:
                            out.append((n, k, x.split("/")[1] if "/" in x else "", bara, int(no)))
    return out


def _kutu_icinde(q, bb, pay):
    return all(bb[2 * i] - pay <= q[i] <= bb[2 * i + 1] + pay for i in range(3))


def bara_yol_denetle(TB=None, analiz=None, hedef=None):
    """Doner hata listesi. Tutucu analizde yoksa (P10.7b2j birleşmemiş) tek HATA."""
    A = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    tut = [p for p in A["parcalar"] if p["ad"].startswith("Bara tutucusu ")]
    if not tut:
        return ["bara yolu: taban-analiz.json'da bara tutucusu yok (P10.7b2j CAD dalı birleşmemiş; girişim sınanamadı)"]
    takim = {}
    for p in A["parcalar"]:
        m = _BARA_TAKIM.match(p["ad"])
        if m:
            takim.setdefault((m.group(1), int(m.group(2))), []).append(p)
    eksen = {k: ((v[0]["bb"][0] + v[0]["bb"][1]) / 2, (v[0]["bb"][4] + v[0]["bb"][5]) / 2) for k, v in takim.items()}
    kutular = [(p["ad"], p["bb"], None) for p in tut] + [(p["ad"], p["bb"], k) for k, v in takim.items() for p in v]
    hedef = bara_yol_hedefleri(TB) if hedef is None else hedef
    izin = {}
    hata = []
    for n, k, y, bara, no in hedef:
        if no is None or (bara, no) not in eksen:
            hata.append("bara yolu: yol %d %s %s ucu (%s): kablolar.json yerleşiminde saplaması yok ya da modelde yok (%s)" % (n, k, y, bara, no))
            continue
        izin.setdefault(n, set()).add((bara, no))
    for n in sorted(CAD_ESLEME):
        pts = cad_noktalar(n, A)
        iz = izin.get(n, set())
        ulasti = set()
        ilk = {}
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            L = math.dist(a, b)
            m = max(1, int(L / BARA_ADIM))
            for j in range(m + 1):
                q = tuple(a[c] + (b[c] - a[c]) * j / m for c in range(3))
                yakin = [s_ for s_ in iz if math.hypot(q[0] - eksen[s_][0], q[2] - eksen[s_][1]) <= BARA_IZIN_R]
                # düzeltme turu 2 (F10u-kontrol T2): izin yalnız tutucu üstünde (pabuç yığını); gövdeye / panelin altından giriş HATA
                if yakin and q[1] >= BARA_IZIN_Y:
                    ulasti.update(yakin)
                    continue
                for ad, bb, tk in kutular:
                    ad_ = ("%s %d. saplamasının civata / pul / somun takımı" % (_BARA_AD[tk[0]], tk[1])) if tk else ad
                    if _kutu_icinde(q, bb, CAD_TUP_R) and ad_ not in ilk:
                        ilk[ad_] = (i, [round(c, 1) for c in q], tk)
        for ad, (i, q, tk) in sorted(ilk.items()):
            hata.append("bara yolu: yol %d noktalar[%d→%d] %s içinden geçiyor (%s; örnek %s)" % (
                n, i, i + 1, ad, "yabancı saplama" if tk else "tutucu gövdesi", q))
        for s_ in sorted(iz - ulasti):
            hata.append("bara yolu: yol %d %s %d. saplamasına ulaşmıyor (eksen ±%g mm)" % (n, _BARA_AD[s_[0]], s_[1], BARA_IZIN_R))
    return hata
BARA_SEMA = {"G16": "anahtarli", "G22": "anahtarli"}                   # P10.7b2k: bara saplamasından başlayan taban şemaları
_BARA_KOPRU = {"anahtarli": "Anahtarlı bara · +", "yildiz": "Yıldız barası · GND"}


def bara_tutarlilik(KYT, arayuz_taban=None, tablo=None):
    """P10.7b2k (F10u-gunluk § A4): kablo_yolu_taban.BARA (şema ölçüleri) ↔ arayuz TABAN["bara_tutucu"] (model) ve G16 / G22 şemasının
    başı ↔ kablolar.json bara yerleşimindeki saplama numarası. Model birleşmeden (P10.7b2j) önce arayuz'da tutucu yok: HATA."""
    hata = []
    if arayuz_taban is None:
        if FC_DIZIN not in sys.path:
            sys.path.insert(0, FC_DIZIN)
        import arayuz as _AR
        arayuz_taban = _AR.TABAN
    bt = arayuz_taban.get("bara_tutucu")
    if not bt:
        return ["bara: arayuz TABAN['bara_tutucu'] yok (P10.7b2j CAD dalı birleşmemiş; kablo_yolu_taban.BARA modelle sınanamıyor)"]
    if abs(bt.get("h", -1) - KYT.BARA_H) > 0.05:
        hata.append("bara: tutucu yüksekliği arayuz %r ≠ kablo_yolu_taban.BARA_H %r" % (bt.get("h"), KYT.BARA_H))
    for k, b in KYT.BARA.items():
        m = bt.get("baralar", {}).get(k)
        if not m:
            hata.append("bara %s: arayuz TABAN['bara_tutucu']['baralar']'da yok" % k)
            continue
        if abs(m["z"] - b["z"]) > 0.05 or len(m["saplama_x"]) != len(b["saplama_x"]) or any(
                abs(x - y) > 0.05 for x, y in zip(m["saplama_x"], b["saplama_x"])):
            hata.append("bara %s: kablo_yolu_taban.BARA (z %r, saplama_x %r) ≠ arayuz (z %r, saplama_x %r)" % (
                k, b["z"], b["saplama_x"], m["z"], m["saplama_x"]))
        if list(m["saplama_x"]) != sorted(m["saplama_x"]):
            hata.append("bara %s: arayuz saplama_x artan değil (numara yönü rehber B5a: önden bakınca soldan sağa = x artan)" % k)
    T = tablo if tablo is not None else json.load(open(TABLO_YOL, encoding="utf-8"))
    kopruler = T["klemens_turleri"]["bara-pabuc"]["kopruler"]
    yollar_ = KYT.yollar()
    for kab, bara in sorted(BARA_SEMA.items()):
        yer = kopruler[_BARA_KOPRU[bara]]["yerlesim"]
        no = [int(n) for n, ilt in yer.items() if any(i.split("/")[0] == kab for i in ilt)]
        if len(no) != 1:
            hata.append("bara şeması %s: kablolar.json %s yerleşiminde %d saplamada" % (kab, _BARA_KOPRU[bara], len(no)))
            continue
        bas = yollar_.get(kab, [None])[0]
        if bas is None or math.dist(bas, KYT.bara_saplama(bara, no[0])) > 0.05:
            hata.append("bara şeması %s: başı %r, kablolar.json'daki %d. saplama %r değil" % (
                kab, bas, no[0], [round(c, 1) for c in KYT.bara_saplama(bara, no[0])]))
    return hata


U06_PORT_PAY = 2.5


def u06_port_denetle(analiz=None):
    """P10.7b2k (F10r-kontrol D5): U06 ("ESP32 USB") şemasının taban ucu ESP32 DevKit'in micro USB portuna kilitli. kablo_yolu_ekran
    ESP_PORT ESP32 DevKit kutusunun +x yüzünde (taban-analiz.json), y ve z kutunun içinde; şemanın son noktası port ağzının
    U06_PORT_PAY mm önünde (+x). Kart taşınırsa ve şema kalırsa HATA. Sınır (F10u-kontrol 7): DevKit CAD'de 180° dönerse kutu aynı
    kalır, sınama geçer; yön yalnız taban_lib.esp_local'da (FreeCAD ister), açık iş karar kuyruğunda."""
    for p in (FC_DIZIN, os.path.join(FC_DIZIN, "lale158")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import kablo_yolu_ekran as KYE
    A_ = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    dk = [p for p in A_["parcalar"] if p["ad"].startswith("ESP32 DevKit")]
    if len(dk) != 1:
        return ["U06: taban-analiz.json'da %d ESP32 DevKit parçası (1 beklenir)" % len(dk)]
    bb, ep = dk[0]["bb"], KYE.ESP_PORT
    hata = []
    if abs(ep[0] - bb[1]) > 0.5 or not (bb[2] <= ep[1] <= bb[3]) or not (bb[4] <= ep[2] <= bb[5]):
        hata.append("U06: kablo_yolu_ekran.ESP_PORT %r ESP32 DevKit kutusunun +x yüzünde değil (kutu %r)" % (ep, bb))
    son = (KYE.yollar().get("ESP32 USB") or [None])[-1]
    hedef = (ep[0] + U06_PORT_PAY, ep[1], ep[2])
    if son is None or math.dist(son, hedef) > 0.05:
        hata.append("U06: 'ESP32 USB' şemasının son noktası %r, port ağzının %.1f mm önü %r değil" % (son, U06_PORT_PAY, hedef))
    return hata


def sema_geometri_denetle(TB=None, RM=None, analiz=None, kafa=None, istisna=None, nokta_f=None, kaynak_yol=None):
    """Gösterim şemalarının uçları ↔ eşlenen kabloların uç parçaları (kural yukarıda). Doner (hata, bilgi, tablo); tablo şema başına
    dict(sema, kod, kimlik, yanlar, uclar, gecis, istisna). kaynak_yol: {kaynak: [yol adı]} (varsayılan kaynak_yollari())."""
    TB = TB or Tablo()
    if RM is None:
        import rehber_metin as RM
    istisna = SEMA_GEO_ISTISNA if istisna is None else istisna
    nokta_f = nokta_f or sema_noktalari
    modelli = sema_parcalari(analiz, kafa)
    for p in (FC_DIZIN, os.path.join(FC_DIZIN, "lale158")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import kablo_yolu_taban as KYT
    import kablo_yolu_kafa as KYK
    kaynak_yol = kaynak_yollari() if kaynak_yol is None else kaynak_yol
    hata, bilgi, tablo = [], [], []
    # P10.7b2c B: rehber_kablo'daki nominal nokta ile şema kaynağının noktası aynı olmalı (biri taşınırsa öbürü eskimesin)
    gk = SEMA_KONUM.get(("Kafa giriş klemensi", "*"), (None,))[0]
    if gk is None or math.dist(gk, KYK.giris_karti_global()) > 0.05:
        hata.append("SEMA_KONUM Kafa giriş klemensi %s ≠ kablo_yolu_kafa.GIRIS_KARTI %s" % (
            gk, [round(c, 1) for c in KYK.giris_karti_global()]))
    dk = SEMA_KONUM.get(("Dağıtım kartı C", "*"), (None,))[0]                  # düzeltme turu 1: SV3'ün kart ucu
    if dk is None or math.dist(dk, KYT.DAGITIM_C) > 0.05:
        hata.append("SEMA_KONUM Dağıtım kartı C %s ≠ kablo_yolu_taban.DAGITIM_C %s" % (dk, [round(c, 1) for c in KYT.DAGITIM_C]))

    hata += bara_tutarlilik(KYT)                                                # P10.7b2k (A4)
    hata += u06_port_denetle(analiz)                                            # P10.7b2k (F10r-kontrol D5)

    def cad(desen):
        return [p for p in modelli if re.search(desen, p["ad"])]
    gorulen = set()
    kullanilan_ist = set()
    for s in RM.SEMA:
        if len(s) != 5 or not isinstance(s[4], (tuple, list)):
            continue                                                  # kaynak_denetle yazar
        kaynak, ad_k, kod, _ad, ids = s
        yer = "şema %s" % ad_k
        if kaynak == "kol_kablo":
            continue                                                  # kol bölümleri rehber_kol_kablo.py'de sınanır
        if kaynak not in SEMA_KAYNAK:
            hata.append("%s: bilinmeyen şema kaynağı %s (SEMA_KAYNAK)" % (yer, kaynak))
            continue
        gorulen.add((kaynak, ad_k))
        pts = nokta_f(kaynak, ad_k)
        if not pts or len(pts) < 2:
            hata.append("%s: kaynakta yolu yok (%s)" % (yer, kaynak))
            continue
        pts = [tuple(float(c) for c in q) for q in pts]
        satir = dict(sema=ad_k, kaynak=kaynak, kod=kod, kimlik=list(ids), yanlar=[], uclar=[], gecis=[], istisna=[])
        dis_bolge = {sema_bolge(u) for u in (pts[0], pts[-1]) if u[1] >= GEO_TABAN_DISI}
        yan_disi, elle, uc_parca, nominal = set(), False, set(), []
        for k in ids:
            if k not in TB.K:
                continue                                              # kaynak_denetle bilinmeyen kimliği yazar
            for y, parcalar in zip("ab", uc_parcalari(TB, k)):
                r = _yan_sina(TB, k, y, parcalar, [pts], dis_bolge, cad, sema_sinifi, sema_bolgesi, sema_konum)
                hata += ["%s %s" % (yer, x) for x in r["hata"]]
                bilgi += ["%s %s" % (yer, x) for x in r["bilgi"]]
                yan_disi |= r["disi"]
                elle = elle or r["elle"]
                uc_parca |= r["uc"]
                nominal += r["nominal"]
                sinif = sema_sinifi(parcalar[0])
                sinif_ad = ("bölge " + (sema_bolgesi(parcalar[0]) or "?")) if sinif == TABAN_DISI else (
                    "elle" if ELLE in r["sonuc"] else ("nominal / vekil" if sinif in (NOMINAL, MODELSIZ) else "modelli"))
                ok = any(r["sonuc"])
                if not ok:
                    g = istisna.get((ad_k, "%s %s" % (k, y)))
                    d = min((_yol_kutu(pts, c["bb"]) for c in cad(sinif)), default=None) if sinif and sinif not in (
                        TABAN_DISI, NOMINAL, MODELSIZ) else None
                    msg = "%s %s yanı (%s) şemaya ulaşmıyor (%s; eşik %g mm)" % (k, y, parcalar[0], "en yakın %.1f mm" % d if d is not None
                                                                              else "bölge / nominal", GEO_ESIK)
                    if g:
                        kullanilan_ist.add((ad_k, "%s %s" % (k, y)))
                        bilgi.append("%s %s (istisna: %s)" % (yer, msg, g[:70]))
                        satir["istisna"].append("%s %s" % (k, y))
                    else:
                        hata.append("%s: %s" % (yer, msg))
                satir["yanlar"].append((k, y, parcalar[0], sinif_ad, "tamam" if ok else ("istisna" if (ad_k, "%s %s" % (k, y)) in kullanilan_ist
                                                                                         else "HATA")))
        sinif = sorted({TB.sinif(k) for k in ids if k in TB.K})
        if len(sinif) > 1:
            hata.append("%s: devre sınıfları karışık (%s); şema tek sınıf taşır" % (yer, "/".join(sinif)))
        for ad_, uc in (("baş", pts[0]), ("son", pts[-1])):
            neden = None
            yakin = sorted((_kutu_mesafe(uc, c["bb"]), c["ad"]) for c in modelli)
            yakin = [a for d, a in yakin if d <= GEO_ESIK]
            if yakin:
                if not (set(yakin) & uc_parca):
                    neden = "uç noktasının yanındaki parça (%s) eşlenen kabloların ucu değil" % yakin[0]
            elif any(math.dist(uc, q) <= GEO_ESIK for q in nominal):
                pass                                                  # P10.7b2c B: modelsiz ucun nominal noktası (kafa giriş kartı)
            elif uc[1] >= GEO_TABAN_DISI:
                b = sema_bolge(uc)
                if b not in yan_disi:
                    neden = "taban dışında %s bölgesinde bitiyor, eşlenen kabloların o bölgede ucu yok" % (b or "tanımsız")
            elif not (elle or any(math.dist(uc, q) <= GEO_ESIK for q in nominal)):
                neden = "uç noktasında parça yok; eşlenen kabloların nominal noktası da elle bakılan ucu da yok"
            if neden:
                g = istisna.get((ad_k, ad_))
                if g:
                    kullanilan_ist.add((ad_k, ad_))
                    bilgi.append("%s %s ucu: %s (istisna: %s)" % (yer, ad_, neden, g[:70]))
                    satir["istisna"].append(ad_)
                else:
                    hata.append("%s %s ucu %s: %s" % (yer, ad_, [round(x, 1) for x in uc], neden))
            satir["uclar"].append((ad_, [round(x, 1) for x in uc], yakin[:2], "tamam" if not neden else (
                "istisna" if (ad_k, ad_) in kullanilan_ist else "HATA")))
        if any(q[1] < GEO_TABAN_DISI for q in pts):
            r_ = TB.yaricap(ids[0]) if ids and ids[0] in TB.K else R_VARSAYILAN
            for lv, n_, s_ in KYT.gecis_denetle(pts, r_):
                satir["gecis"].append((lv, [round(c, 1) for c in n_], s_ or "tamam"))
                if s_:
                    hata.append("%s: %s geçişi %s: %s" % (yer, lv, [round(c, 1) for c in n_], s_))
        # eksik eşleme yalnız bilgi
        for k in sorted(TB.K):
            if k in ids or TB.sinif(k) not in sinif:
                continue
            yanlar = [_yan_sina(TB, k, y, p_, [pts], dis_bolge, cad, sema_sinifi, sema_bolgesi, sema_konum)
                      for y, p_ in zip("ab", uc_parcalari(TB, k))]
            if all(not r["hata"] and not r.get("vekil") and any(x is True for x in r["sonuc"]) for r in yanlar):
                bilgi.append("%s: %s kablosunun iki yanı da şemaya ulaşıyor (aynı sınıf), şemada değil (yalnız bilgi)" % (yer, k))
        tablo.append(satir)
    # eşlemesiz şema: kaynakta çizili, SEMA'da yok (P10.7b2c B: bütün kaynaklar; bilinçli dışarıda bırakılan SEMA_ESLEMESIZ_MUAF'ta)
    for kaynak in SEMA_KAYNAK:
        for k in kaynak_yol.get(kaynak, []):
            if (kaynak, k) in gorulen:
                if (kaynak, k) in SEMA_ESLEMESIZ_MUAF:
                    hata.append("SEMA_ESLEMESIZ_MUAF %s:%s: SEMA'da girdisi var (muaftan çıkar)" % (kaynak, k))
            elif (kaynak, k) not in SEMA_ESLEMESIZ_MUAF:
                hata.append("%s şema kaynağının yolu %s: SEMA'da girdisi yok (eşlemesiz şema)" % (kaynak, k))
    for kaynak, k in sorted(SEMA_ESLEMESIZ_MUAF):
        if k not in kaynak_yol.get(kaynak, []):
            hata.append("SEMA_ESLEMESIZ_MUAF %s:%s: kaynakta böyle yol yok (muaftan çıkar)" % (kaynak, k))
    for k in sorted(set(istisna) - kullanilan_ist):
        hata.append("SEMA_GEO_ISTISNA %s: kullanılmıyor (şema düzeldiyse istisnayı kaldır)" % (k,))
    return hata, bilgi, tablo


def kritik_tablolar(esleme=None):
    """Onay kaydının 'kablo' bölümü (rehber_kritik): elle yazılmış eşleme ve eşik tabloları. Bunlardan biri değişirse
    rehber_denetim.py --kaynak (ve bu dosyanın ana koşusu) eski / yeni hâliyle HATA verir; geometrinin ayırt edemediği eşleme
    değişikliklerini (ayirt_edilemeyen()) yakalayan budur."""
    import rehber_kritik as _RK
    esleme = CAD_ESLEME if esleme is None else esleme
    g = []
    for n in sorted(esleme):
        g.append(_RK.girdi("CAD_ESLEME %d" % n, " ".join(esleme[n]), "CAD yolu ↔ kablo kimlikleri"))
    g.append(_RK.girdi("GEO_DAL", repr(sorted(GEO_DAL.items())), "dallanan yollar"))
    # P10.7b2b (R8): bilinen karışık yollar ve eksik eşleme muafları
    g.append(_RK.girdi("KARISIK_BILINEN", repr(sorted(KARISIK_BILINEN.items())), "bilinen karışık sınıflı yollar"))
    g.append(_RK.girdi("GEO_EKSIK_MUAF", repr(sorted((n, sorted(v.items())) for n, v in GEO_EKSIK_MUAF.items())), "eksik eşleme muafları"))
    for n in sorted(GEO_ISTISNA):
        g.append(_RK.girdi("GEO_ISTISNA %d" % n, GEO_ISTISNA[n], "geometri istisnası"))
    for n in sorted(CAD_KIRP):                                         # P10.7b2f
        _yon, _d = cad_kirp_kesim(n)                                   # P10.7b2i: y yönünde b2f'deki yazım ("kesim y 192.5") korunur
        g.append(_RK.girdi("CAD_KIRP %d" % n, ("son %d kesim y %r · %s" % (CAD_KIRP[n]["son"], _d, CAD_KIRP[n]["gerekce"])) if _yon == (0.0, 1.0, 0.0)
                           # P10.7b2k (F10r-kontrol D7): yön birim vektör olarak (cad_kirp_metin): (0, 1, 1) ile (0, 2, 2) aynı kesim, aynı kayıt
                           else ("son %d kesim %s · %s" % (CAD_KIRP[n]["son"], cad_kirp_metin(n), CAD_KIRP[n]["gerekce"])),
                           "rehberde kırpılan CAD yolu"))
    for k in sorted(UC_ETIKET):                                        # P10.7b2f: uç etiketi metni ve yeri bu eşlemeden
        g.append(_RK.girdi("UC_ETIKET", "%s = %r %r" % (k, UC_ETIKET[k][0], UC_ETIKET[k][1]), "uç etiketi → CAD parçası"))
    for k in sorted(UC_MODELSIZ):
        g.append(_RK.girdi("UC_MODELSIZ", "%s = %s" % (k, UC_MODELSIZ[k]), "uç etiketi: modelde parçası yok"))
    for k in sorted(PARCA_CAD):
        g.append(_RK.girdi("PARCA_CAD", "%s = %s" % (k, PARCA_CAD[k]), "uç parçası → CAD"))
    for (k, kt) in sorted(MODELSIZ_KONUM):
        nokta, vekil, _g = MODELSIZ_KONUM[(k, kt)]
        g.append(_RK.girdi("MODELSIZ_KONUM", "%s %s = %r %r" % (k, kt, nokta, vekil), "modelsiz uç → nominal konum / vekil"))
    g.append(_RK.girdi("TABAN_DISI", "%r %r %r" % (TABAN_DISI_DESEN, TABAN_DISI_BOLGE, TABAN_DISI_PARCA), "taban dışı bölgeler"))
    for k in sorted(KOL_ESLEME):
        g.append(_RK.girdi("KOL_ESLEME", "%s = %s" % (k, " ".join(KOL_ESLEME[k])), "kol bölümü ↔ kimlik"))
    g.append(_RK.girdi("KESIT_YARICAP", repr(sorted(KESIT_YARICAP.items())), "çizim yarıçapı kademeleri"))
    for k in sorted(TEMA_TON):
        g.append(_RK.girdi("TEMA_TON", "%s = %r" % (k, sorted(TEMA_TON[k].items())), "tema tonu"))
    g.append(_RK.girdi("ESIK", "GEO_ESIK %r GEO_TABAN_DISI %r KARSITLIK_ESIK %r RENK_FARK_ESIK %r" % (
        GEO_ESIK, GEO_TABAN_DISI, KARSITLIK_ESIK, RENK_FARK_ESIK), "eşikler"))
    v, sabit = vurgu_tonlari()                                         # P10.7b2a: seçim vurgusu (app.js) ve siyah L* kuralı
    g.append(_RK.girdi("VURGU_TON", "%r %r" % (sorted(v.items()), sorted(sabit.items())), "seçim vurgusu tonu"))
    for tm in ("light", "dark"):                                       # düzeltme turu 1 (A9): vurgunun sınandığı sınıf renkleri
        g.append(_RK.girdi("SINIF", "%s = %r" % (tm, sorted(sinif_renkleri(tm).items())), "parça sınıfı renkleri"))
    g.append(_RK.girdi("ESIK", "SIYAH_L_FARK %r" % SIYAH_L_FARK, "eşikler"))
    # P10.7b2c: gösterim şemalarının eşlemesi ve şema sınamasının tabloları (geometrinin ayırt edemediği şema eşlemesini de kilitler)
    import rehber_metin as _RM
    for s in _RM.SEMA:
        if len(s) == 5 and isinstance(s[4], (tuple, list)):
            g.append(_RK.girdi("SEMA_ESLEME", "%s:%s %s = %s" % (s[0], s[1], s[2], " ".join(s[4])), "şema ↔ adım ↔ kablo kimlikleri"))
    g.append(_RK.girdi("SEMA_KAYNAK", repr(SEMA_KAYNAK), "şema kaynak işlevleri"))
    for k in sorted(SEMA_PARCA):
        g.append(_RK.girdi("SEMA_PARCA", "%s = %s" % (k, SEMA_PARCA[k]), "şema uç parçası → CAD"))
    g.append(_RK.girdi("SEMA_PARCA_BOLGE", repr(SEMA_PARCA_BOLGE), "şema taban dışı bölgeleri"))
    for k in sorted(SEMA_MODELSIZ):
        g.append(_RK.girdi("SEMA_MODELSIZ", k, "şema modelsiz ucu (elle)"))
    for k in sorted(SEMA_GEO_ISTISNA):
        g.append(_RK.girdi("SEMA_GEO_ISTISNA", "%s / %s = %s" % (k[0], k[1], SEMA_GEO_ISTISNA[k]), "şema geometri istisnası"))
    # P10.7b2c ikinci yarı (ajan B): şema nominal uçları, eşlemesiz şema muafları, bağlantı tablosu eşlemesi
    for (k, kt) in sorted(SEMA_KONUM):
        nokta, vekil, _g = SEMA_KONUM[(k, kt)]
        g.append(_RK.girdi("SEMA_KONUM", "%s %s = %r %r" % (k, kt, nokta, vekil), "şema modelsiz ucu → nominal konum / vekil"))
    for k in sorted(SEMA_ESLEMESIZ_MUAF):
        g.append(_RK.girdi("SEMA_ESLEMESIZ_MUAF", "%s:%s = %s" % (k[0], k[1], SEMA_ESLEMESIZ_MUAF[k]), "SEMA'ya bilerek alınmayan şema yolu"))
    for k in sorted(BAGLANTI_TABLOSU):
        g.append(_RK.girdi("BAGLANTI_TABLOSU", "%s = %s" % (k, BAGLANTI_TABLOSU[k]), "bağlantı tablosuyla gösterilen kablo → adım"))
    g.append(_RK.girdi("SEMA_BOY_ETIKET", SEMA_BOY_ETIKET, "şema boyu etiketi"))
    # P10.7b2c düzeltme turu 1: tıklama kartının boy etiketi, gösterim şeması notu kuralı, yer eki
    g.append(_RK.girdi("SEMA_BOY_APP", SEMA_BOY_APP, "tıklama kartında şema boyu etiketi (app.js)"))
    g.append(_RK.girdi("SEMA_NOT", "%r %r %r" % (sorted(SEMA_NOT_KAYNAK.items()), SEMA_NOT_SOZ, SEMA_YAKLASIK), "gösterim şeması notu kuralı"))
    for k in sorted(UC_YER_EK):
        g.append(_RK.girdi("UC_YER_EK", "%s = %s" % (k, UC_YER_EK[k]), "yanlış yer çağrıştıran ada yer eki"))
    return g


def onay_denetle(esleme=None):
    """Kaydın yalnız 'kablo' bölümünü bugünkü tablolarla karşılaştırır. Doner [hata satırı]."""
    import rehber_kritik as _RK
    try:
        eski = _RK.oku()
    except _RK.KayitHatasi as e:                                    # düzeltme turu 2: bozuk / boş kayıt traceback değil HATA satırı
        return [str(e)]
    if eski is None:
        return ["onay kaydı yok (%s): rehber_denetim.py --kritik-onay-yenile" % os.path.basename(_RK.ONAY_DOSYASI)]
    E = {"bolumler": {"kablo": eski.get("bolumler", {}).get("kablo", [])}}
    return ["onaylı kablo tablosu %s: %s · eski: %s · yeni: %s" % (f["tur"], f["yer"], f["eski"] or "-", f["yeni"] or "-")
            for f in _RK.karsilastir(E, {"kablo": kritik_tablolar(esleme)})]


def cizilen_kimlikler(RM=None):
    if RM is None:
        import rehber_metin as RM
    c = {}
    for n, ids in CAD_ESLEME.items():
        for i in ids:
            c.setdefault(i, []).append("CAD Kablo yolu %d" % n)
    for s in RM.SEMA:
        for i in s[4]:
            c.setdefault(i, []).append("şema %s" % s[1])
    for k, ids in KOL_ESLEME.items():
        for yan in ("sag", "sol"):
            for i in kol_kimlik("%s:%s" % (yan, k)):
                c.setdefault(i, []).append("kol %s:%s" % (yan, k))
    return c


def cizim_tablosu(TB=None, RM=None):
    """P10.7b2c B (brief madde 4): üç sınıf. yol çizimi = CAD kablo yolu, gösterim şeması ya da kol bölümü; bağlantı tablosu =
    BAGLANTI_TABLOSU'ndaki kablo (adımın kablo listesinde {bag.<kimlik>} satırı; 3B çizilen sayılmaz); hiçbiri = ikisi de yok.
    cizilen / cizilmeyen eski anlamıyla (yol çizimi / değil) kalır."""
    TB = TB or Tablo()
    c = cizilen_kimlikler(RM)
    cizilen = [k for k in TB.K if k in c]
    cizilmeyen = [k for k in TB.K if k not in c]
    bag = [k for k in cizilmeyen if k in BAGLANTI_TABLOSU]
    hic = [k for k in cizilmeyen if k not in BAGLANTI_TABLOSU]
    kay = {}
    for k in cizilen:
        for t in {x.split()[0] for x in c[k]}:
            kay[t] = kay.get(t, 0) + 1
    return dict(toplam=len(TB.K), cizilen=len(cizilen), cizilmeyen=cizilmeyen, nerede={k: c[k] for k in cizilen},
                yol_cizimi=len(cizilen), yol_kaynak=dict(sorted(kay.items())), baglanti_tablosu=bag, hicbiri=hic)


# ------------------------------------------------------------------ bağlantı tablosu (P10.7b2c ikinci yarı, ajan B; brief madde 1)
# Elektronik katı kısa telleri 3B tüp değil, adımın kablo listesinde (ekranda ve basılıda aynı alan: app.js kablo listesi, yazdir.html
# "Kablo kancası") bağlantı tablosu satırıyla gösterilir. Satır elle yazılmaz: ham metinde tek bir {bag.<kimlik>} yer tutucusu, değeri
# rehber_deger'in kayıttan (kablolar.json damarları; ESP32 GPIO'su ve PCA9685 kanal adı pin-haritasi.md § 9 JSON'uyla karşılaştırılarak)
# kurduğu metin. Sınama: (1) kablo kayıtta, adım kablonun rehber adımlarından; (2) adımın ham kablo listesinde {bag.<kimlik>} tam bir
# kez ve başka adımda yok; (3) rehberdeki çözülmüş satır bugünkü kayıttan yeniden kurulanla aynı (eski kayıttan kalan tablo HATA);
# (4) tablo kurulamıyorsa (yanlış pin, kanal ↔ kanal adı uyuşmazlığı) HATA; (5) BAGLANTI_TABLOSU dışında {bag.…} HATA.
BAGLANTI_TABLOSU = {"I01": "B6a", "I02": "B6a", "P01": "B6a", "P02": "B6a", "P03": "K1"}
_BAG = re.compile(r"\{bag\.([^{}\s]+)\}")


def baglanti_tablosu_denetle(TB=None, RM=None, D=None):
    TB = TB or Tablo()
    if RM is None:
        import rehber_metin as RM
    import rehber_deger as _RDG
    D = D or _RDG.Degerler(TB.T)
    hata = []
    nerede = {}
    for kod, a in RM.ADIM_HAM.items():
        for i, t in enumerate(a.get("kablo") or []):
            for m in _BAG.finditer(t if isinstance(t, str) else ""):
                nerede.setdefault(m.group(1), []).append((kod, i))
    for k in sorted(set(nerede) - set(BAGLANTI_TABLOSU)):
        hata.append("{bag.%s}: BAGLANTI_TABLOSU'nda yok (%s)" % (k, ", ".join(x for x, _i in nerede[k])))
    for k, kod in sorted(BAGLANTI_TABLOSU.items()):
        yer = "bağlantı tablosu %s (%s)" % (k, kod)
        if k not in TB.K:
            hata.append("%s: kablo kayıtta yok" % yer)
            continue
        kodlar = {x["kod"] for x in TB.K[k].get("rehber", [])}
        if kod not in kodlar:
            hata.append("%s: adım kablonun rehber adımlarından değil (%s)" % (yer, sorted(kodlar)))
        n = nerede.get(k, [])
        if len(n) != 1 or n[0][0] != kod:
            hata.append("%s: adımın kablo listesinde {bag.%s} satırı %s (tam bir kez olmalı)" % (yer, k, n or "yok"))
            continue
        try:
            beklenen = D.deger("bag", k)
        except KeyError as e:
            hata.append("%s: tablo kayıttan kurulamadı (%s)" % (yer, e))
            continue
        ham = RM.ADIM_HAM[kod]["kablo"][n[0][1]]
        coz = (RM.ADIM.get(kod, {}).get("kablo") or [None] * (n[0][1] + 1))[n[0][1]]
        if coz != D.coz(ham) or beklenen not in (coz or ""):
            hata.append("%s: rehberdeki satır kayıttan kurulanla aynı değil (eski / elle) · rehber: %s · kayıt: %s" % (
                yer, (coz or "-")[:90], beklenen[:90]))
    return hata


# ------------------------------------------------------------------ şema yolundan boy (P10.7b2c B, brief madde 6)
# Her gösterim şemasının (kol bölümleri hariç) yol uzunluğu, şemanın ana kablosunun (SEMA girdisinin ilk kimliği) kablolar.json kaydında
# ayrı alan "sema_boy" = {mm, sema, kaynak, etiket[, ortak]}. boy / boy_tahmin'in yerine geçmez, üzerine yazılmaz; sipariş hesabı
# (kablolar_uret.kablo_boy, maliyet.json) okumaz. Yazma yalnız --sema-boy-yaz ile; ana koşu ve bozma denemesi tazeliği sınar.
SEMA_BOY_ETIKET = "gösterim şeması yolu; ölçüm değil"
SEMA_BOY_DOSYA = {"yollar": "tasarim/freecad/lale158/kablo_yolu_ekran.py#yollar",
                  "kafa_ici_qled": "tasarim/freecad/lale158/kablo_yolu_ekran.py#kafa_ici_qled",
                  "taban": "tasarim/freecad/lale158/kablo_yolu_taban.py#yollar",
                  "kafa_ici": "tasarim/freecad/lale158/kablo_yolu_kafa.py#yollar"}


def sema_boylari(RM=None, nokta_f=None):
    """{ana kimlik: sema_boy kaydı} ve hata listesi (aynı kablo iki şemanın ana kablosuysa)."""
    if RM is None:
        import rehber_metin as RM
    nokta_f = nokta_f or sema_noktalari
    out, hata = {}, []
    for s in RM.SEMA:
        if len(s) != 5 or s[0] not in SEMA_KAYNAK or not s[4]:
            continue
        pts = nokta_f(s[0], s[1])
        if not pts or len(pts) < 2:
            continue                                                  # sema_geometri_denetle yazar
        L = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))
        k = s[4][0]
        if k in out:
            hata.append("sema_boy %s: iki şemanın ana kablosu (%s, %s:%s)" % (k, out[k]["sema"], s[0], s[1]))
            continue
        e = dict(mm=int(round(L)), sema="%s:%s" % (s[0], s[1]), kaynak=SEMA_BOY_DOSYA[s[0]], etiket=SEMA_BOY_ETIKET)
        if len(s[4]) > 1:
            e["ortak"] = list(s[4][1:])
        out[k] = e
    return out, hata


def sema_boy_denetle(TB=None, RM=None, nokta_f=None):
    TB = TB or Tablo()
    bek, hata = sema_boylari(RM, nokta_f)
    for k in sorted(TB.K):
        v = TB.K[k].get("sema_boy")
        if k in bek and v != bek[k]:
            if (v or {}).get("mm") != bek[k]["mm"]:
                hata.append("sema_boy %s: kayıtta %s mm, şemadan %s mm (rehber_kablo.py --sema-boy-yaz)" % (
                    k, (v or {}).get("mm"), bek[k]["mm"]))
            else:
                hata.append("sema_boy %s: kayıt alanları şemadan farklı (%s ≠ %s)" % (k, v, bek[k]))
        elif k not in bek and v is not None:
            hata.append("sema_boy %s: kayıtta var, şeması yok (ana kablo değil)" % k)
    return hata


# ------------------------------------------------------------------ P10.7b2c düzeltme turu 1 (F10k-kontrol D1, D3, kaçan bozmalar 4 ve 5)
# (1) Tıklama kartındaki şema boyu (app.js semaSec): gösterim şemasının yol uzunluğu "çizim yolu ~N mm (kesim boyu değil)" etiketiyle
#     gösterilir; kol içi bölümün (veride "kol" alanı olan) sayısı bölüm uzunluğudur: "bölüm uzunluğu ~N mm (kesim boyu değil)" (orkestratör
#     ek kararı). Etiket ifadesi app.js'ten okunur ve sınanır; boy_mm başka yerde gösterilirse de HATA (sınanmayan ikinci gösterim olmasın).
SEMA_BOY_APP = (r'SEMA\[i\]\.boy_mm \? \(SEMA\[i\]\.kol \? " · bölüm uzunluğu ~" \+ Math\.round\(SEMA\[i\]\.boy_mm\) \+ " mm \(kesim boyu değil\)"\s*'
                r': " · çizim yolu ~" \+ Math\.round\(SEMA\[i\]\.boy_mm\) \+ " mm \(kesim boyu değil\)"\) : ""')
APP_JS_ELLE = {}                                                       # bozma denemesi: {"metin": app.js metni} dosya yerine


def sema_boy_etiketi_denetle(metin=None):
    s = metin if metin is not None else (APP_JS_ELLE.get("metin") or open(APP_JS, encoding="utf-8").read())
    m = re.search(r"\n    function semaSec\(i\) \{\n(.*?)\n    \}\n", s, re.S)
    if not m:
        return ["app.js: semaSec işlevi yok (şema boyu etiketi sınanamadı)"]
    g, hata = m.group(1), []
    if not re.search(r"const boy = " + SEMA_BOY_APP + ";", g) or not re.search(r'\)" \+\s*boy \+ "</span>"', g):
        hata.append("app.js semaSec: şema boyu \"çizim yolu ~N mm (kesim boyu değil)\" / kol bölümünde \"bölüm uzunluğu ~N mm (kesim boyu değil)\" "
                    "etiketiyle gösterilmiyor (F10k-kontrol D1)")
    if "boy_mm" in s[:m.start()] + s[m.end():]:
        hata.append("app.js: boy_mm semaSec dışında da gösteriliyor (etiketi sınanmıyor)")
    return hata


# (2) Gösterim şeması notu (kaçan bozma 4): çarpışma taramasından geçmeyen şema kaynaklarının (SEMA_NOT_KAYNAK) her şeması için adımın
#     kablo listesinde not bulunmalı: "gösterim şemasıdır", kaynak dosyası, "çarpışma taramasından geçmedi", "boy ölçümü değildir"; notun
#     "gösterim şemasıdır"dan önceki kısmı şemanın bütün kablo kimliklerini anmalı (şema notsuz ya da başka kabloların notu olan adıma
#     taşınırsa HATA: kaçan bozma 5, G19 → B3). Modelsiz / nominal uçlu şemanın görünen adında "yeri yaklaşık" (ya da ses bölücüsünün
#     "yeri ve varlığı kesin değil") geçmeli. Onay kaydından bağımsız. Eski kaynaklar (yollar, kafa_ici_qled) bu kurala girmez: notları
#     başka biçimde ya da yok (F10k-gunluk.md düzeltme turu 1; kuyrukta).
SEMA_NOT_KAYNAK = {"taban": "lale158/kablo_yolu_taban.py", "kafa_ici": "lale158/kablo_yolu_kafa.py"}
SEMA_NOT_SOZ = ("gösterim şemasıdır", "çarpışma taramasından geçmedi", "boy ölçümü değildir")
SEMA_YAKLASIK = ("yeri yaklaşık", "yeri ve varlığı kesin değil")


# P10.7b2k: tabloda (PARCA_CAD) modelsiz sayılan ama şemada modelli vekiliyle (SEMA_KONUM, bara tutucusu) sınanan uçlar: şemanın yeri
# yaklaşık değil, "yeri yaklaşık" istenmez. Vekil modelde yoksa sema_geometri_denetle zaten HATA verir.
SEMA_MODELLI_VEKIL = {"Anahtarlı bara", "Yıldız barası"}


def sema_not_denetle(TB=None, RM=None):
    TB = TB or Tablo()
    if RM is None:
        import rehber_metin as RM
    hata = []
    for s in RM.SEMA:
        if len(s) != 5 or s[0] not in SEMA_NOT_KAYNAK or not isinstance(s[4], (tuple, list)):
            continue
        kaynak, ad_k, kod, ad, ids = s
        dosya = "`%s`" % SEMA_NOT_KAYNAK[kaynak]
        notlar = [t for t in (RM.ADIM.get(kod) or {}).get("kablo") or []
                  if isinstance(t, str) and dosya in t and all(x in t for x in SEMA_NOT_SOZ)]
        if not notlar:
            hata.append("şema %s (%s): adımın kablo listesinde gösterim şeması notu yok (%s, %s)" % (ad_k, kod, dosya, " / ".join(SEMA_NOT_SOZ)))
        else:
            on = [t.split(SEMA_NOT_SOZ[0])[0] for t in notlar]
            eksik = [k for k in ids if not any(re.search(r"(?<!\w)%s(?!\w)" % re.escape(k), o) for o in on)]
            if eksik:
                hata.append("şema %s (%s): adımın gösterim şeması notu %s kablosunu anmıyor (şema yanlış adımda ya da not eksik)" % (
                    ad_k, kod, "/".join(eksik)))
        modelsiz = [p[0] for k in ids if k in TB.K for p in uc_parcalari(TB, k) if sema_sinifi(p[0]) in (NOMINAL, MODELSIZ)
                    and not _onek(p[0], SEMA_MODELLI_VEKIL)]
        if modelsiz and not any(x in ad for x in SEMA_YAKLASIK):
            hata.append("şema %s: modelsiz uç (%s) var, görünen adında \"%s\" yok" % (ad_k, modelsiz[0], SEMA_YAKLASIK[0]))
    return hata


# (3) Yer eki (D3): UC_YER_EK'teki ad geçen her görünen metinde ek de geçmeli (adım metinleri, şema adları, CAD yolu adları, kb satırları).
def uc_yer_eki_denetle(TB=None, RM=None):
    TB = TB or Tablo()
    if RM is None:
        import rehber_metin as RM
    metin = []

    def gez(o, yer):
        if isinstance(o, str):
            metin.append((yer, o))
        elif isinstance(o, dict):
            for k, v in o.items():
                gez(v, "%s.%s" % (yer, k))
        elif isinstance(o, (list, tuple)):
            for i, v in enumerate(o):
                gez(v, "%s[%d]" % (yer, i))
    gez(RM.ADIM, "adım")
    gez([s[3] for s in RM.SEMA if len(s) == 5], "şema adı")
    gez({n: v[1] for n, v in RM.KABLO_AD.items()}, "KABLO_AD")
    metin += [("kb %s" % k, TB.bilgi_satiri(k)) for k in sorted(TB.K)]
    hata = []
    for ad, ek in UC_YER_EK.items():
        n = 0
        for yer, t in metin:
            if ad in t:
                n += 1
                if ek not in t:
                    hata.append("%s: \"%s\" geçiyor, kartın yeri yazılı değil (\"%s\"; F10k-kontrol D3)" % (yer, ad, ek[:50]))
        if not n:
            hata.append("UC_YER_EK %s: hiçbir görünen metinde geçmiyor (kayıttaki ad değiştiyse eki güncelle)" % ad)
    return hata


def kayit_boyu(r):
    """Kayıttaki boy: CAD / liste boyu (önce önerilen, sonra liste, gereken, yol) ya da tahmin. Doner (mm, ad) ya da (None, '')."""
    b = r.get("boy") or {}
    for a, ad in (("onerilen_mm", "önerilen"), ("liste_mm", "liste"), ("gereken_mm", "gereken"), ("yol_mm", "CAD yolu")):
        if b.get(a):
            return b[a], ad
    t = r.get("boy_tahmin") or {}
    return (t["mm"], "tahmin") if t.get("mm") else (None, "")


def sema_boy_tablosu(TB=None, RM=None):
    """[(kimlik, kesit, kayıttaki mm, kayıt türü, şemadan mm, fark, ortak)] bütün şema ana kabloları; risk = fark > 0."""
    TB = TB or Tablo()
    bek, _h = sema_boylari(RM)
    out = []
    for k in sorted(bek):
        if k not in TB.K:
            continue
        mm, ad = kayit_boyu(TB.K[k])
        out.append((k, TB.kesit_metni(k), mm, ad, bek[k]["mm"], (bek[k]["mm"] - mm) if mm else None, bek[k].get("ortak", [])))
    return out


def sema_boy_yaz(yol=TABLO_YOL):
    """kablolar.json'a sema_boy alanlarını yazar (yalnız bu alan; şema sürümü 5). Biçim dosyanınki: indent 1, ensure_ascii False."""
    ham = open(yol, encoding="utf-8").read()
    T = json.loads(ham)
    if json.dumps(T, indent=1, ensure_ascii=False) + "\n" != ham:
        raise SystemExit("kablolar.json biçimi beklenenden farklı (indent 1); yazılmadı")
    bek, h = sema_boylari()
    if h:
        raise SystemExit("; ".join(h))
    yeni = []
    for r in T["kablolar"]:
        d = {}
        son = "boy_tahmin" if "boy_tahmin" in r else "boy"              # alan boy_tahmin'in (yoksa boy'un) hemen ardına
        for a, v in r.items():
            if a == "sema_boy":
                continue
            d[a] = v
            if a == son and r["kimlik"] in bek:
                d["sema_boy"] = bek[r["kimlik"]]
        yeni.append(d)
    T["kablolar"] = yeni
    T["surum"] = 5
    if "sema_boy" not in T["kaynak"]:
        T["kaynak"] += "; P10.7b2c (şema 5: sema_boy, gösterim şeması yolunun uzunluğu; planlama/d158/F10k-gunluk.md)"
    T["alanlar"]["sema_boy"] = ("gösterim şemasının yol uzunluğu (rehber_metin.SEMA; şemanın ana kablosunda, ortak: aynı şemadaki öbür "
                                "kablolar): mm, sema (kaynak:ad), kaynak, etiket '" + SEMA_BOY_ETIKET + "'. boy / boy_tahmin'in yerine "
                                "geçmez, sipariş hesabına girmez; yalnız rehber_kablo.py --sema-boy-yaz yazar")
    open(yol, "w", encoding="utf-8", newline="\n").write(json.dumps(T, indent=1, ensure_ascii=False) + "\n")
    return len(bek)


# ------------------------------------------------------------------ veri (rehber-veri.json) denetimi
def veri_denetle(V, TB=None):
    """Üretilmiş veride: her kablo parçası / şema tablo kimliği taşıyor mu; renk ve yarıçap türetilmişle aynı mı; lejant tablosu var mı."""
    TB = TB or Tablo()
    hata, eslesmeyen = [], []
    for p in V["parcalar"]:
        if not p.get("renk"):
            continue
        ids = p.get("kablo")
        if not ids:
            eslesmeyen.append("parça %s %s" % (p["id"], p["ad"]))
            continue
        bil = [i for i in ids if i not in TB.K]
        if bil:
            hata.append("parça %s: bilinmeyen kimlik %s" % (p["id"], bil))
            continue
        n = cad_no(p.get("ad_cad") or p["ad"])
        if n is not None and tuple(ids) != tuple(CAD_ESLEME.get(n, ())):
            hata.append("parça %s (Kablo yolu %d): kimlikler %s, CAD_ESLEME %s" % (p["id"], n, list(ids), list(CAD_ESLEME.get(n, ()))))
        if p["renk"].lower() != TB.renk(ids[0]).lower():
            hata.append("parça %s: renk %s, tablodan %s (%s)" % (p["id"], p["renk"], TB.renk(ids[0]), ids[0]))
        if p.get("rt") != TB.ton(ids[0]):                            # F10h kontrol-5 S3-1: sahnenin çizdiği tema tonu (eksik rt dahil)
            hata.append("parça %s: tema tonu %s, tablodan %s (%s)" % (p["id"], p.get("rt"), TB.ton(ids[0]), ids[0]))
    for i, s in enumerate(V.get("semalar", [])):
        if s.get("kol") and not str(s.get("kaynak", "")).startswith("kol_kablo:"):   # düzeltme turu 1 (D1): app.js etiketi "kol"a bakar
            hata.append("şema %d %s: kol bölümü değil ama 'kol' alanı var (kartta çizim yolu yerine bölüm uzunluğu diye gösterilir)" % (i, s["ad"][:40]))
        ids = s.get("kablo")
        if not ids:
            eslesmeyen.append("şema %d %s" % (i, s["ad"][:60]))
            continue
        bil = [k for k in ids if k not in TB.K]
        if bil:
            hata.append("şema %d: bilinmeyen kimlik %s" % (i, bil))
            continue
        if s.get("tur") in KOL_ISARET_TUR:
            continue                                                 # işaret: kendi rengi
        if s["renk"].lower() != TB.renk(ids[0]).lower():
            hata.append("şema %d: renk %s, tablodan %s (%s)" % (i, s["renk"], TB.renk(ids[0]), ids[0]))
        if abs(float(s.get("r") or R_VARSAYILAN) - TB.yaricap(ids[0])) > 1e-6:
            hata.append("şema %d: yarıçap %s, tablodan %s (%s)" % (i, s.get("r"), TB.yaricap(ids[0]), ids[0]))
        if s.get("rt") != TB.ton(ids[0]):
            hata.append("şema %d: tema tonu %s, tablodan %s (%s)" % (i, s.get("rt"), TB.ton(ids[0]), ids[0]))
    if not V.get("kablo_sinif"):
        hata.append("veride kablo_sinif (lejant: renk → devre sınıfı) yok")
    else:
        for k, v in TB.lejant().items():
            if V["kablo_sinif"].get(k, [None])[0] != v[0]:
                hata.append("kablo_sinif %s: %s, tablodan %s" % (k, V["kablo_sinif"].get(k), v[0]))
    return hata, eslesmeyen


# ------------------------------------------------------------------ P10.7b2f: kırpılan yolların üretilmiş mesh'i
def glb_kutulari(glb):
    """robot.glb düğüm adı (parça kimliği) → (bmin, bmax, izd) dünya koordinatında (mm); izd: CAD_KIRP'teki her kesim yönü (birim) →
    mesh köşelerinin o yöndeki (en küçük, en büyük) izdüşümü (P10.7b2i; +y yönünde bmin / bmax'ın y'si). Dosya yoksa None."""
    if not glb or not os.path.exists(glb):
        return None
    import rehber_sira as _RS
    meshes, nodes = _RS.glb_oku(glb)
    yonler = sorted({cad_kirp_yon(n) for n in CAD_KIRP})
    out = {}
    for name, mi, M in nodes:
        w = meshes[mi][0] @ M[:3, :3].T + M[:3, 3]
        izd = {}
        for yo in yonler:
            q = w @ yo
            izd[yo] = (float(q.min()), float(q.max()))
        out[name] = (tuple(float(x) for x in w.min(0)), tuple(float(x) for x in w.max(0)), izd)
    return out


def kirp_veri_denetle(V, kutular):
    """CAD_KIRP'teki her yol veride tek parça; mesh'i (robot.glb) kesim yönündeki izdüşümüyle kesim düzleminin (+0,5 mm pay) öbür yanına
    geçmiyor ve yolun başına (korunan noktaların en küçük izdüşümü − tüp yarıçapı, + 0,5 mm) iniyor. kutular None ise (GLB yok) yalnız
    parça varlığı sınanır. P10.7b2i: y düzlemi yerine kesim yönü (yol 12'de +y: b2f'deki y sınaması aynen)."""
    hata = []
    A = json.load(open(GEO_ANALIZ, encoding="utf-8"))
    for n in sorted(CAD_KIRP):
        yon, ky = cad_kirp_kesim(n, A)
        ps = [p for p in V["parcalar"] if cad_no(p.get("ad_cad") or p["ad"]) == n]
        if len(ps) != 1:
            hata.append("CAD_KIRP yol %d: veride %d parça (1 beklenir)" % (n, len(ps)))
            continue
        if kutular is None:
            continue
        k = kutular.get(ps[0]["id"])
        if k is None:
            hata.append("CAD_KIRP yol %d: %s robot.glb'de yok" % (n, ps[0]["id"]))
            continue
        iz = (k[2] if len(k) > 2 else {}).get(yon)
        if iz is None:
            hata.append("CAD_KIRP yol %d (%s): robot.glb'de %r yönünde izdüşüm yok (kesim yönü değişti, GLB eski)" % (n, ps[0]["id"], yon))
            continue
        if iz[1] > ky + 0.5:
            hata.append("CAD_KIRP yol %d (%s): mesh izdüşümü en büyük %.1f, kesim %.1f (%s): eski kısım rehberde çiziliyor" % (
                n, ps[0]["id"], iz[1], ky, cad_kirp_metin(n, A)))
        y0 = min(izdusum(p, yon) for p in cad_noktalar(n, A))
        if iz[0] > y0 - CAD_TUP_R + 0.5:
            hata.append("CAD_KIRP yol %d (%s): mesh izdüşümü en küçük %.1f, yolun başı %.1f: kesim yolun korunan kısmını da kesmiş" % (
                n, ps[0]["id"], iz[0], y0 - CAD_TUP_R))
    return hata


def uc_veri_denetle(V):
    """P10.7b2f: veride uç etiketleri (rehber_gorunum.uc_isle). Her etiket adı UC_ETIKET'te (birleşik ad " / " ile), numaralar 1..n
    sıralı, parça veride var; karede görünmez uçların adı UC_ETIKET ya da UC_MODELSIZ'de. uc_kaynak yoksa hata (eski veri)."""
    hata = []
    if "uc_kaynak" not in V:
        return ["veride uc_kaynak yok: uç etiketleri işlenmemiş (rehber_gorunum.uc_isle)"]
    PID = {p["id"] for p in V["parcalar"]}
    for a in V["adimlar"]:
        for j, g in [(0, a)] + list(enumerate(a.get("sira_grup") or [], 1)):
            yer = "%s.%d" % (a["i"], j)
            uc = g.get("uc") or []
            if [u["n"] for u in uc] != list(range(1, len(uc) + 1)):
                hata.append("uç etiketi %s: numaralar sıralı değil %s" % (yer, [u["n"] for u in uc]))
            for u in uc:
                bil = [x for x in u["ad"].split(" / ") if x not in UC_ETIKET]
                if bil or u["id"] not in PID:
                    hata.append("uç etiketi %s: %s (%s) UC_ETIKET'te yok ya da parça veride yok" % (yer, u["ad"], u["id"]))
            for u in g.get("uc_yok") or []:
                if u["ad"] not in UC_ETIKET and u["ad"] not in UC_MODELSIZ:
                    hata.append("uç etiketi %s: görünmez uç %s sınıflanmamış" % (yer, u["ad"]))
    return hata


# ------------------------------------------------------------------ bozma denemesi
def bozma_denemesi(V=None, kutular=None):
    import importlib
    import rehber_metin as RM0
    sonuc = []
    ANZ = json.load(open(GEO_ANALIZ, encoding="utf-8"))
    KAF = json.load(open(KAFA_ANALIZ, encoding="utf-8"))

    KU = {"k": None}
    import rehber_gorunum as _RG
    CAD = _RG.cad_parcalar()                                             # P10.7b2f: uç etiketi desenleri modelde sınanır

    def dene(ad, f):
        RM = copy.deepcopy(_modul_kopya(RM0))
        TB = Tablo()
        eski_cad, eski_kol = copy.deepcopy(CAD_ESLEME), copy.deepcopy(KOL_ESLEME)
        eski_ton, eski_yc = copy.deepcopy(TEMA_TON), copy.deepcopy(KESIT_YARICAP)
        eski_mk = copy.deepcopy(MODELSIZ_KONUM)
        eski_kb, eski_em, eski_pc = copy.deepcopy(KARISIK_BILINEN), copy.deepcopy(GEO_EKSIK_MUAF), copy.deepcopy(PARCA_CAD)
        eski_sp, eski_si = copy.deepcopy(SEMA_PARCA), copy.deepcopy(SEMA_GEO_ISTISNA)
        eski_sk, eski_sm, eski_bt = copy.deepcopy(SEMA_KONUM), copy.deepcopy(SEMA_ESLEMESIZ_MUAF), copy.deepcopy(BAGLANTI_TABLOSU)
        eski_kr, eski_gi = copy.deepcopy(CAD_KIRP), copy.deepcopy(GEO_ISTISNA)
        eski_ue, eski_um = copy.deepcopy(UC_ETIKET), copy.deepcopy(UC_MODELSIZ)
        try:
            V2 = copy.deepcopy(V) if V is not None else None
            KU["k"] = copy.deepcopy(kutular)
            f(RM, TB, V2)
            h = kaynak_denetle(TB, RM)
            h += geometri_denetle(TB, ANZ, CAD_ESLEME, GEO_ISTISNA)[0]
            h += bara_yol_denetle(TB, ANZ)                                     # P10.7b2k düzeltme turu 1
            h += cad_kirp_denetle(ANZ)                                         # P10.7b2i
            h += sema_geometri_denetle(TB, RM, ANZ, KAF)[0]                  # P10.7b2c
            h += baglanti_tablosu_denetle(TB, RM)                            # P10.7b2c B
            h += sema_boy_denetle(TB, RM)
            h += sema_boy_etiketi_denetle() + sema_not_denetle(TB, RM) + uc_yer_eki_denetle(TB, RM)   # düzeltme turu 1
            h += uc_etiket_denetle(TB, CAD)                                   # P10.7b2f
            if V2 is not None:
                h += veri_denetle(V2, TB)[0]
                h += kirp_veri_denetle(V2, KU["k"])                     # P10.7b2f
                h += uc_veri_denetle(V2)
            ho = onay_denetle()                                       # açık işler turu: onay kaydı ayrı mekanizma olarak sayılır
        finally:
            APP_JS_ELLE.clear()
            SEMA_KONUM.clear(); SEMA_KONUM.update(eski_sk)
            CAD_KIRP.clear(); CAD_KIRP.update(eski_kr)
            GEO_ISTISNA.clear(); GEO_ISTISNA.update(eski_gi)                 # P10.7b2k
            while _BOZMA_GERI:                                               # P10.7b2k: modül sabitini bozan denemelerin geri alması
                _BOZMA_GERI.pop()()
            UC_ETIKET.clear(); UC_ETIKET.update(eski_ue)
            UC_MODELSIZ.clear(); UC_MODELSIZ.update(eski_um)
            SEMA_ESLEMESIZ_MUAF.clear(); SEMA_ESLEMESIZ_MUAF.update(eski_sm)
            BAGLANTI_TABLOSU.clear(); BAGLANTI_TABLOSU.update(eski_bt)
            CAD_ESLEME.clear(); CAD_ESLEME.update(eski_cad)
            KOL_ESLEME.clear(); KOL_ESLEME.update(eski_kol)
            TEMA_TON.clear(); TEMA_TON.update(eski_ton)
            KESIT_YARICAP.clear(); KESIT_YARICAP.update(eski_yc)
            MODELSIZ_KONUM.clear(); MODELSIZ_KONUM.update(eski_mk)
            KARISIK_BILINEN.clear(); KARISIK_BILINEN.update(eski_kb)
            GEO_EKSIK_MUAF.clear(); GEO_EKSIK_MUAF.update(eski_em)
            PARCA_CAD.clear(); PARCA_CAD.update(eski_pc)
            SEMA_PARCA.clear(); SEMA_PARCA.update(eski_sp)
            SEMA_GEO_ISTISNA.clear(); SEMA_GEO_ISTISNA.update(eski_si)
            SEMA_NOKTA_ELLE.clear()
            VURGU_ELLE.clear()
            SINIF_ELLE.clear()
        mek = "+".join(x for x, v in (("denetim", h), ("onay", ho)) if v)
        sonuc.append((ad, len(h) + len(ho), (h + ho)[:2], mek))

    def b1(RM, TB, V): CAD_ESLEME[3] = ("G99",) + CAD_ESLEME[3][1:]
    def b2(RM, TB, V): RM.SEMA[0] = RM.SEMA[0][:4] + (("H09",),)
    def b3(RM, TB, V): RM.SEMA[1] = RM.SEMA[1][:4] + ((),)
    def b4(RM, TB, V): RM.SEMA[2] = RM.SEMA[2][:4] + ("#00a3a3",)
    def b5(RM, TB, V): KOL_ESLEME["uzatma_kol"] = ("S33",)
    def b6(RM, TB, V): RM.KABLO_AD[13] = ("Yeni", "Yeni kablo yolu")
    def b7(RM, TB, V): TB.K["G17"]["renk"]["sinif"] = "pembe"
    def b8(RM, TB, V): RM.SEMA[6] = RM.SEMA[6][:2] + ("K2",) + RM.SEMA[6][3:]      # ReSpeaker USB yanlış adımda
    def b9(RM, TB, V): del CAD_ESLEME[8]
    def b10(RM, TB, V): CAD_ESLEME[4] = CAD_ESLEME[4] + ("M02",)                    # kontrol Ü3: sol motor sağdaki yolda
    def b11(RM, TB, V): CAD_ESLEME[12] = CAD_ESLEME[12] + ("N01", "N02")            # kontrol Ü3: enkoderler ulaşmayan yolda
    def b12(RM, TB, V): CAD_ESLEME[11] = ("Q01", "Q02", "Q03", "X01")               # orta / sağ sonar sol sonar yolunda
    def b13(RM, TB, V): CAD_ESLEME[8] = ("G18",)                                     # kafa 12 V yoluna çevre 5 V kablosu
    def b14(RM, TB, V): TEMA_TON["siyah"]["dark"] = "#222222"                         # kontrol §2-12: toprak koyu temada görünmez
    def b15(RM, TB, V): TEMA_TON["sari"]["light"] = "#e2b714"                         # kontrol §2-12: sarı açık temada 1,58
    def b16(RM, TB, V): KESIT_YARICAP[22] = 2.1                                       # kontrol §2-11: kol teli inceldi
    def b17(RM, TB, V): KESIT_YARICAP[16] = 3.2                                       # 18 / 16 AWG kademesi gözle seçilmez
    # P10.7b1 açık işler turu (kontrol-2 madde 11 ve 17): kontrolün kaçan G bozmaları ve renk farkı
    def b18(RM, TB, V): CAD_ESLEME[4] = CAD_ESLEME[4] + ("M01",)                    # G1: dal ana yolun öbür kolunu miras alıyordu
    def b19(RM, TB, V): CAD_ESLEME[4] = CAD_ESLEME[4] + ("G12",)                    # G3
    def b20(RM, TB, V): CAD_ESLEME[5] = CAD_ESLEME[5] + ("S09",)                    # G4: kafa servosu sağ kol yolunda (bölge)
    def b21(RM, TB, V): CAD_ESLEME[1] = CAD_ESLEME[1] + ("G05",)                    # G7: XT60 − kutbu ana hat yolunda
    def b22(RM, TB, V): CAD_ESLEME[2] = CAD_ESLEME[2] + ("G01",)                    # G8
    def b23(RM, TB, V): CAD_ESLEME[10] = CAD_ESLEME[10] + ("G22",)                  # G6: ayırt edilemeyen çift (yalnız onay kaydı)
    def b24(RM, TB, V): TEMA_TON["hazir-usb"]["light"] = "#7c7c7c"; TEMA_TON["beyaz"]["light"] = "#4e6d7d"   # eski ΔE00 14,1
    def b25(RM, TB, V): TEMA_TON["siyah"]["dark"] = "#b9bec5"                         # eski: siyah ↔ beyaz koyu ΔE00 13,2
    def b26(RM, TB, V): MODELSIZ_KONUM[("Yıldız barası", "*")] = ((20.0, 186.0, -60.0),) + MODELSIZ_KONUM[("Yıldız barası", "*")][1:]
    def b27(RM, TB, V): TEMA_TON["hazir-hdmi"]["dark"] = "#7f9bb5"                    # eski: mavi ↔ HDMI koyu ΔE00 9,8
    # P10.7b2a (F10h-kontrol-4): seçim vurgusu ve açık HDMI
    def b28(RM, TB, V): VURGU_ELLE["light"] = "#7cfc00"                               # eski vurgu: açık zemine karşıtlık 1,1
    def b29(RM, TB, V): VURGU_ELLE["light"] = "#2a8a4a"                               # acil stop yeşiline yakın vurgu
    def b30(RM, TB, V): VURGU_ELLE["dark"] = "#e8c020"                                # servo sarısıyla aynı vurgu
    def b31(RM, TB, V): VURGU_ELLE["dark"] = "#ff3fa4"                                # EV_RENK ile aynı vurgu
    def b32(RM, TB, V): TEMA_TON["hazir-hdmi"]["light"] = "#1d3854"                   # eski açık HDMI: siyaha yakın (L*)
    # düzeltme turu 1 (F10i-kontrol A9): vurgu ↔ parça sınıfı renkleri, kopya tonu da
    def b33(RM, TB, V): VURGU_ELLE["light"] = "#a35ef2"                               # eski açık vurgu: "lazer" sınıfına ΔE00 13,4
    def b34(RM, TB, V): VURGU_ELLE["light_kopya"] = "#9b50b8"                         # kopya tonu "lazer" sınıfına yakın
    def b35(RM, TB, V): SINIF_ELLE["profil"] = "#00e5d6"                              # sınıf rengi koyu vurguya yakın
    def b36(RM, TB, V): VURGU_ELLE["dark_kopya"] = "#5d6168"                          # koyu kopya tonu önceki adımların grisi
    # P10.7b2b (F10h-kontrol-3 §3.3-2; R8): onay kaydı olmadan geometri / eşleme kuralıyla yakalanmalı (mek "denetim" içermeli)
    def b37(RM, TB, V): CAD_ESLEME[4] = CAD_ESLEME[4] + ("G08",)                    # G19: dal, yalnız ana yol bölümüyle uyar
    def b38(RM, TB, V): CAD_ESLEME[4] = CAD_ESLEME[4] + ("G10",)                    # G20
    def b39(RM, TB, V): CAD_ESLEME[10] = tuple("G22" if x == "A03" else x for x in CAD_ESLEME[10])   # G24: yeşil ↔ turuncu
    def b40(RM, TB, V): CAD_ESLEME[1] = tuple(x for x in CAD_ESLEME[1] if x != "G02")              # G26: eksik eşleme
    def b41(RM, TB, V): KARISIK_BILINEN.pop(3)                                       # bilinen karışım silindi
    def b42(RM, TB, V): CAD_ESLEME[5] = CAD_ESLEME[5] + ("G19",)                    # mavi kablo sarı / turuncu yolda
    def b43(RM, TB, V): GEO_EKSIK_MUAF.pop(1)                                        # G10 / yol 1 muafı silindi (eksik eşleme)
    def b44(RM, TB, V): PARCA_CAD["Dağıtım kartı C"] = r"^XL4016 servo 6 V C"        # kart XL4016 C'nin kutusu sayıldı: yol 6'ya ulaşmaz
    # P10.7b2c: gösterim şemalarının geometrik sınaması (mek "denetim" içermeli)
    def _si(RM, ad_k):
        return next(i for i, s in enumerate(RM.SEMA) if s[1] == ad_k)

    def _kt(ad_k):
        return [list(q) for q in sema_noktalari("taban", ad_k)]

    def b45(RM, TB, V):                                                               # yanlış uca bağlı yol: N01 şemasına N02
        i = _si(RM, "N01"); RM.SEMA[i] = RM.SEMA[i][:4] + (("N02",),)

    def b46(RM, TB, V):                                                               # eşik dışı uç: G19 sonu 30 mm kartın dışına
        p = _kt("G19"); p[-1][0] += 30.0; SEMA_NOKTA_ELLE[("taban", "G19")] = p

    def b47(RM, TB, V): del RM.SEMA[_si(RM, "N01")]                                    # eşlemesiz şema: kaynakta var, SEMA'da yok

    def b48(RM, TB, V):                                                               # yanlış adım: Q01 şeması B5a'da
        i = _si(RM, "Q01"); RM.SEMA[i] = RM.SEMA[i][:2] + ("B5a",) + RM.SEMA[i][3:]

    def b49(RM, TB, V):                                                               # kat kesiği dışından geçiş (N02, x 90)
        p = _kt("N02"); p[5][0] = p[6][0] = 90.0; SEMA_NOKTA_ELLE[("taban", "N02")] = p

    def b50(RM, TB, V):                                                               # alt plakayı deliksiz geçiş (M02, z +60)
        p = _kt("M02"); p[3][2] += 60.0; p[4][2] += 60.0; SEMA_NOKTA_ELLE[("taban", "M02")] = p

    def b51(RM, TB, V): SEMA_GEO_ISTISNA.pop(("HDMI", "baş"))                          # mevcut şemanın istisnası silindi (P10.7b2i: U06'nınki kalktı, HDMI'nınki)

    def b52(RM, TB, V):                                                               # iki sınıflı şema (SV3 + G16)
        i = _si(RM, "SV3"); RM.SEMA[i] = RM.SEMA[i][:4] + (("SV3", "G16"),)

    def b53(RM, TB, V): SEMA_PARCA.pop("PAM8403")                                      # şema uç parçası haritadan çıktı

    def b54(RM, TB, V):                                                               # mevcut şema yanlış uca: Dizi USB'ye U03
        i = _si(RM, "Dizi USB"); RM.SEMA[i] = RM.SEMA[i][:4] + (("U03",),)
    # P10.7b2c ikinci yarı (ajan B): bağlantı tablosu, kafa içi / ses şemaları, bütün kaynaklarda eşlemesiz şema, şema boyu

    def _dm(TB, k, ad):
        return next(d for d in TB.K[k]["damarlar"] if d["ad"] == ad)

    def _bag_sil(RM, kod, k):
        i = next(i for i, t in enumerate(RM.ADIM_HAM[kod]["kablo"]) if "{bag.%s}" % k in t)
        del RM.ADIM_HAM[kod]["kablo"][i]; del RM.ADIM[kod]["kablo"][i]

    def b55(RM, TB, V):                                                               # tablo: yanlış pin (SDA GPIO25)
        d = _dm(TB, "I01", "SDA"); d["gpio"] = 25; d["a"] = "ESP32 · GPIO25"

    def b56(RM, TB, V): _bag_sil(RM, "B6a", "I02")                                    # tablo: eksik satır

    def b57(RM, TB, V): _dm(TB, "P01", "K0 sag_omuz")["pca_kanal"] = 4                 # tablo: kayıtla uyuşmayan kanal

    def b58(RM, TB, V): _dm(TB, "P02", "K5 sol_omuz")["pca_ad"] = "sol_bilek"          # tablo: kanal adı pin haritasıyla tutmuyor

    def b59(RM, TB, V):                                                               # tablo: kayıt değişti, rehber eski (damar silindi)
        TB.K["I02"]["damarlar"] = [d for d in TB.K["I02"]["damarlar"] if d["ad"] != "GND"]

    def b60(RM, TB, V):                                                               # tablo: satır elle yazıldı (yer tutucusuz)
        i = next(i for i, t in enumerate(RM.ADIM_HAM["K1"]["kablo"]) if "{bag.P03}" in t)
        RM.ADIM_HAM["K1"]["kablo"][i] = RM.ADIM["K1"]["kablo"][i]

    def b61(RM, TB, V): BAGLANTI_TABLOSU["P03"] = "B6a"                               # tablo: yanlış adım

    def b62(RM, TB, V):                                                               # kafa içi: K02 şemasına K03 (yanlış uç)
        i = _si(RM, "K02"); RM.SEMA[i] = RM.SEMA[i][:4] + (("K03",),)

    def b63(RM, TB, V):                                                               # kafa giriş kartının nominal noktası taşındı
        n, v_, g_ = SEMA_KONUM[("Kafa giriş klemensi", "*")]; SEMA_KONUM[("Kafa giriş klemensi", "*")] = ((n[0] - 30.0,) + n[1:], v_, g_)

    def b64(RM, TB, V): SEMA_PARCA.pop("Ses bölücüsü")                                 # ses: bölücü uç haritasından çıktı

    def b65(RM, TB, V): del RM.SEMA[_si(RM, "Hoparlor")]                               # eşlemesiz şema (yollar kaynağı)

    # P10.7b2k: muaf boş (iki eski ses yolu kaynaktan da kalktı); deneme kaynakta olmayan yolun muafı oldu
    def b66(RM, TB, V): SEMA_ESLEMESIZ_MUAF[("yollar", "Ses karti uzatmasi")] = "eski"  # kaynakta olmayan yolun muafı eklendi

    def b67(RM, TB, V):                                                               # şema boyu eskidi (K03 ara noktası taşındı)
        p = [list(q) for q in sema_noktalari("kafa_ici", "K03")]; p[1][2] += 40.0; SEMA_NOKTA_ELLE[("kafa_ici", "K03")] = p

    def b68(RM, TB, V): TB.K["AU1"].pop("sema_boy", None)                             # şema boyu kaydı silindi

    def b69(RM, TB, V):                                                               # C01 sonu kameradan uzak
        p = [list(q) for q in sema_noktalari("kafa_ici", "C01")]; p[-1][2] -= 30.0; SEMA_NOKTA_ELLE[("kafa_ici", "C01")] = p

    def b70(RM, TB, V):                                                               # ses şeması ReSpeaker'dan değil Pi'den başlıyor
        p = [list(q) for q in sema_noktalari("kafa_ici", "AU1")]; p[0] = [0.0, 1290.0 + 236.0, 1.0]
        SEMA_NOKTA_ELLE[("kafa_ici", "AU1")] = p
    # P10.7b2c düzeltme turu 1 (F10k-kontrol D1, D3 ve kaçan bozmalar 1, 4, 5)
    _app = open(APP_JS, encoding="utf-8").read()
    _eti = re.search(r"const boy = " + SEMA_BOY_APP + ";", _app)

    def b71(RM, TB, V):                                                               # D1: kartta eski "~N mm" (etiketsiz)
        APP_JS_ELLE["metin"] = _app.replace(_eti.group(0), 'const boy = SEMA[i].boy_mm ? " · ~" + Math.round(SEMA[i].boy_mm) + " mm" : "";')

    def b72(RM, TB, V):                                                               # D1: gösterim şemasında "(kesim boyu değil)" silindi
        APP_JS_ELLE["metin"] = _app.replace('" · çizim yolu ~" + Math.round(SEMA[i].boy_mm) + " mm (kesim boyu değil)"',
                                            '" · çizim yolu ~" + Math.round(SEMA[i].boy_mm) + " mm"')

    def b73(RM, TB, V): APP_JS_ELLE["metin"] = _app.replace("(SEMA[i].kol ?", "(!SEMA[i].kol ?")    # D1: iki etiket yer değiştirdi

    def b85(RM, TB, V):                                                               # ek: kol bölümünde eski "~N mm" (etiketsiz)
        APP_JS_ELLE["metin"] = _app.replace('" · bölüm uzunluğu ~" + Math.round(SEMA[i].boy_mm) + " mm (kesim boyu değil)"',
                                            '" · ~" + Math.round(SEMA[i].boy_mm) + " mm"')

    def b86(RM, TB, V):                                                               # ek: kol bölümünde "(kesim boyu değil)" silindi
        APP_JS_ELLE["metin"] = _app.replace('" · bölüm uzunluğu ~" + Math.round(SEMA[i].boy_mm) + " mm (kesim boyu değil)"',
                                            '" · bölüm uzunluğu ~" + Math.round(SEMA[i].boy_mm) + " mm"')

    def b74(RM, TB, V):                                                               # D1: boy kartın başka yerinde etiketsiz
        APP_JS_ELLE["metin"] = _app.replace("    function kabloBilgi(x, en) {\n",
                                            "    function kabloBilgi(x, en) {\n      if (x.boy_mm) return \" · ~\" + x.boy_mm + \" mm\";\n", 1)

    def b75(RM, TB, V):                                                               # kaçan 1: SV3 kart ucu panelin öbür köşesine
        p = _kt("SV3"); p[-1] = [-100.0, p[-1][1], -60.0]; SEMA_NOKTA_ELLE[("taban", "SV3")] = p

    def b76(RM, TB, V):                                                               # kaçan 1: SV3 kart ucu 30 mm öteye (boşlukta)
        p = _kt("SV3"); p[-1][2] -= 30.0; SEMA_NOKTA_ELLE[("taban", "SV3")] = p

    def b77(RM, TB, V):                                                               # kaçan 1: nominal nokta kaynaktan ayrıldı
        n, v_, g_ = SEMA_KONUM[("Dağıtım kartı C", "*")]; SEMA_KONUM[("Dağıtım kartı C", "*")] = ((n[0], n[1], n[2] - 30.0), v_, g_)

    def _not_sil(RM, kod, soz):
        for A_ in (RM.ADIM, RM.ADIM_HAM):
            A_[kod]["kablo"] = [t for t in A_[kod]["kablo"] if soz not in t]

    def b78(RM, TB, V): _not_sil(RM, "B5a", "SV3'ün çizimi gösterim şemasıdır")       # kaçan 4: B5a notu silindi

    def b79(RM, TB, V):                                                               # kaçan 4: adından "yeri yaklaşık" silindi
        i = _si(RM, "SV3"); RM.SEMA[i] = RM.SEMA[i][:3] + (RM.SEMA[i][3].replace("yeri yaklaşık: ", ""),) + RM.SEMA[i][4:]

    def b80(RM, TB, V):                                                               # kaçan 5: G19 B3'e taşındı
        i = _si(RM, "G19"); RM.SEMA[i] = RM.SEMA[i][:2] + ("B3",) + RM.SEMA[i][3:]

    def b81(RM, TB, V):                                                               # kaçan 4: E3a notunda K02 anılmıyor
        for A_ in (RM.ADIM, RM.ADIM_HAM):
            A_["E3a"]["kablo"] = [t.replace("(K01, K02, K03)", "(K01, K03)") for t in A_["E3a"]["kablo"]]

    def b82(RM, TB, V):                                                               # D3: K1 P03 satırından kartın yeri silindi
        for A_ in (RM.ADIM, RM.ADIM_HAM):
            A_["K1"]["kablo"] = [t.replace(" Dağıtım kartı C (kafa): " + UC_YER_EK["Dağıtım kartı C (kafa)"] + ".", "")
                                 for t in A_["K1"]["kablo"]]

    def b83(RM, TB, V):                                                               # D3: kb satırında ek yok (SV3, S09, S10 kartı)
        o = TB.bilgi_satiri
        TB.bilgi_satiri = lambda k: o(k).replace(" (" + UC_YER_EK["Dağıtım kartı C (kafa)"] + ")", "")

    def b84(RM, TB, V):                                                               # D3: yeni metinde ad eksiz geçiyor
        i = _si(RM, "SV3"); RM.SEMA[i] = RM.SEMA[i][:3] + (RM.SEMA[i][3] + " → Dağıtım kartı C (kafa)",) + RM.SEMA[i][4:]
    deneme = [("CAD eşlemesinde bilinmeyen kimlik", b1), ("şemada bilinmeyen kimlik", b2), ("şemada kimlik yok", b3),
              ("şema son alanı yine renk (anahtar kelime / elle renk)", b4), ("kol bölümünde bilinmeyen kimlik", b5),
              ("KABLO_AD'da eşlemesiz CAD numarası", b6), ("devre sınıfı renk kuralında yok", b7),
              ("şema tablodaki adımla tutmuyor", b8), ("CAD numarasının eşlemesi silindi", b9),
              ("geometri: yol 4'e M02 (sol arka motor)", b10), ("geometri: yol 12'ye N01 / N02", b11),
              ("geometri: yol 11'e Q01 / Q02", b12), ("geometri: yol 8'e G18 (kafa yoluna çevre 5 V)", b13),
              ("karşıtlık: siyah koyu temada #222", b14), ("karşıtlık: sarı açık temada eski ton", b15),
              ("yarıçap: 22 AWG 2,1 (incelme)", b16), ("yarıçap: 16 AWG kademesi 18'e çok yakın", b17),
              ("geometri G1: yol 4'e M01 (dal mirası)", b18), ("geometri G3: yol 4'e G12 (dal mirası)", b19),
              ("geometri G4: yol 5'e S09 (bölge)", b20), ("geometri G7: yol 1'e G05 (XT60 − kutbu)", b21),
              ("geometri G8: yol 2'ye G01 (akü + kutbu)", b22), ("eşleme G6: yol 10'a G22 (ayırt edilemeyen)", b23),
              ("renk: açık beyaz / USB eski tonlar", b24), ("renk: koyu siyah eski ton", b25),
              ("nominal: yıldız noktası taşındı", b26), ("renk: koyu HDMI eski ton", b27),
              ("vurgu: eski açık yeşil (karşıtlık)", b28), ("vurgu: açık temada acil stop yeşiline yakın", b29),
              ("vurgu: koyu temada servo sarısı", b30), ("vurgu: EV_RENK ile aynı", b31), ("renk: açık HDMI eski ton (siyaha yakın)", b32),
              ("vurgu: eski açık ton (lazer sınıfına 13,4)", b33), ("vurgu kopya: açık temada lazer sınıfına yakın", b34),
              ("vurgu: profil sınıfı koyu vurguya yakın", b35), ("vurgu kopya: koyu temada önceki adımlar grisi", b36),
              ("eşleme G19: yol 4'e G08 (dal, ana yol bölümü)", b37), ("eşleme G20: yol 4'e G10 (dal, ana yol bölümü)", b38),
              ("eşleme G24: yol 10'da A03 yerine G22 (sınıf)", b39), ("eşleme G26: yol 1'den G02 çıktı (eksik)", b40),
              ("sınıf: yol 3'ün bilinen karışımı silindi", b41), ("sınıf: yol 5'e G19 (mavi)", b42),
              ("eksik eşleme: G10 / yol 1 muafı silindi", b43), ("dağıtım kartı C: XL4016 C kutusu sayıldı", b44),
              ("şema: N01 şemasına N02 (yanlış uç)", b45), ("şema: G19 sonu eşik dışında", b46),
              ("şema: N01 SEMA'dan silindi (eşlemesiz)", b47), ("şema: Q01 yanlış adımda (B5a)", b48),
              ("şema: N02 kat kesiği dışından", b49), ("şema: M02 alt plakayı deliksiz geçiyor", b50),
              ("şema: HDMI baş istisnası silindi", b51), ("şema: SV3 + G16 iki sınıf", b52),
              ("şema: PAM8403 SEMA_PARCA'dan çıktı", b53), ("şema: Dizi USB'ye U03 (mevcut şema)", b54),
              ("tablo: I01 SDA yanlış pin (GPIO25)", b55), ("tablo: I02 satırı eksik", b56),
              ("tablo: P01 kanal kayıtla uyuşmuyor", b57), ("tablo: P02 kanal adı pin haritasıyla tutmuyor", b58),
              ("tablo: I02 kaydı değişti, rehber eski", b59), ("tablo: P03 satırı elle yazıldı", b60),
              ("tablo: P03 yanlış adımda", b61), ("kafa içi: K02 şemasına K03", b62),
              ("kafa içi: giriş kartı nominali taşındı", b63), ("ses: bölücü SEMA_PARCA'dan çıktı", b64),
              ("eşlemesiz: Hoparlor (yollar) SEMA'dan silindi", b65), ("eşlemesiz: kaynakta olmayan yolun muafı", b66),
              ("şema boyu: K03 yolu değişti, kayıt eski", b67), ("şema boyu: AU1 kaydı silindi", b68),
              ("kafa içi: C01 sonu kameradan uzak", b69), ("ses: şema Pi'den başlıyor", b70),
              ("D1: kartta etiketsiz '~N mm'", b71), ("D1: '(kesim boyu değil)' silindi", b72), ("D1: iki etiket yer değiştirdi", b73),
              ("D1: boy kartın başka yerinde etiketsiz", b74), ("SV3 kart ucu panelin öbür köşesinde", b75),
              ("SV3 kart ucu 30 mm öteye", b76), ("dağıtım kartı C nominali kaynaktan ayrıldı", b77), ("B5a SV3 gösterim notu silindi", b78),
              ("SV3 adından 'yeri yaklaşık' silindi", b79), ("G19 şeması B3'e taşındı", b80), ("E3a notunda K02 anılmıyor", b81),
              ("D3: K1 P03 kartın yeri silindi", b82), ("D3: kb satırında yer eki yok", b83), ("D3: şema adında ad eksiz", b84),
              ("ek: kol bölümünde etiketsiz '~N mm'", b85), ("ek: kol bölümünde '(kesim boyu değil)' silindi", b86)]
    # P10.7b2f: Kablo yolu 12'nin kırpılması (CAD_KIRP)
    def b87(RM, TB, V): CAD_KIRP.pop(12)                                 # eski üst kısım yeniden çizilir, istisnası yok
    def b88(RM, TB, V): CAD_KIRP[12] = dict(CAD_KIRP[12], son=1)          # kesim B01'in ESP32 ucunu da kesti
    deneme += [("kırpma: yol 12 CAD_KIRP'ten silindi", b87), ("kırpma: yol 12 ESP32 ucundan önce kesildi", b88)]
    # P10.7b2i: Kablo yolu 9'un kırpılması (y + z yönünde kesim; F10r-gunluk § 1)
    def b94(RM, TB, V): CAD_KIRP.pop(9)                                  # eski XL4016 → ESP32 bölümü yeniden çizilir, istisnası yok
    def b95(RM, TB, V): CAD_KIRP[9] = dict(CAD_KIRP[9], son=2)            # kesim G18'in XL4016 ucunu da kesti
    def b96(RM, TB, V): CAD_KIRP[9] = {k: v for k, v in CAD_KIRP[9].items() if k != "yon"}   # y düzlemi: eski bölüm ayrılmıyor
    def b97(RM, TB, V): CAD_KIRP[9] = dict(CAD_KIRP[9], yon=(0.0, 0.0, 1.0))   # z düzlemi: ESP32 ucunda kalıntı (F10q § 3)
    deneme += [("kırpma: yol 9 CAD_KIRP'ten silindi", b94), ("kırpma: yol 9 XL4016 ucundan önce kesildi", b95),
               ("kırpma: yol 9 kesimi y düzlemi (ayırmıyor)", b96), ("kırpma: yol 9 kesimi z düzlemi (ESP32 kalıntısı)", b97)]
    # P10.7b2i: U06 şemasının eski istisnası geri eklendi (şema düzeldiği için "kullanılmıyor" yakalanmalı)
    def b98(RM, TB, V): SEMA_GEO_ISTISNA[("ESP32 USB", "son")] = "eski: taban ucu güç panelinin üstünde"
    deneme += [("şema: U06 eski istisnası geri eklendi", b98)]
    # P10.7b2k (A4, D5): bara şeması ve U06 port kilidi
    def _modul_boz(mod, ad, deger):
        eski = getattr(mod, ad)
        setattr(mod, ad, deger)
        _BOZMA_GERI.append(lambda: setattr(mod, ad, eski))
    def _kyt():
        for p_ in (FC_DIZIN, os.path.join(FC_DIZIN, "lale158")):
            if p_ not in sys.path:
                sys.path.insert(0, p_)
        import kablo_yolu_taban as KYT, kablo_yolu_ekran as KYE
        return KYT, KYE
    def b100(RM, TB, V): SEMA_KONUM.pop(("Anahtarlı bara", "*"))           # şema eski röle vekiline düştü (G16 / G22 başı röleden uzak)
    def b101(RM, TB, V):                                                  # şema ölçüsü modelden ayrıldı (saplama 10 mm kaydı)
        KYT, _ = _kyt()
        _modul_boz(KYT, "BARA", dict(KYT.BARA, anahtarli=dict(KYT.BARA["anahtarli"], saplama_x=(-27.5, -2.5, 22.5, 47.5))))
    def b102(RM, TB, V):                                                  # G22 yanlış saplamadan (3.) başlıyor
        KYT, _ = _kyt()
        eski = KYT.yollar
        _modul_boz(KYT, "yollar", lambda: dict(eski(), G22=[KYT.bara_saplama("anahtarli", 3)] + eski()["G22"][1:]))
    def b103(RM, TB, V):                                                  # U06 port ağzı ESP32 DevKit'in +x yüzünden 10 mm içeride
        _, KYE = _kyt()
        _modul_boz(KYE, "ESP_PORT", (97.0,) + tuple(KYE.ESP_PORT[1:]))
    deneme += [("şema: anahtarlı bara tutucu vekili silindi", b100), ("şema: bara saplama ölçüsü modelden ayrı", b101),
               ("şema: G22 yanlış saplamadan", b102), ("şema: U06 port ağzı DevKit yüzünde değil", b103)]
    # P10.7b2k (F10r-kontrol D4): yol 9 kırpılmışken eski GEO_ISTISNA'sı geri eklendi ("kullanılmıyor" yakalanmalı)
    def b99(RM, TB, V): GEO_ISTISNA[9] = "eski: yol 9'un ESP32 ucu eski tasarımda"
    deneme += [("geometri: yol 9 eski istisnası geri eklendi (kırpılmışken)", b99)]
    # P10.7b2f: uç etiketleri (UC_ETIKET / UC_MODELSIZ)
    def b89(RM, TB, V): UC_ETIKET.pop("ESP32")                           # uç sınıflanmamış
    def b90(RM, TB, V): UC_ETIKET["HC-SR04 sol"] = (r"^Sonar HC-SR04", None)   # desen üç sonara uyar
    def b91(RM, TB, V): UC_ETIKET["sağ dirsek servosu"] = (r"^Dirsek servosu MG996R", "dirsek_sol")   # yanlış yan: kayıt değişti (onay)
    def b92(RM, TB, V): UC_MODELSIZ["ESP32"] = "elle"                    # iki tabloda birden
    def b93(RM, TB, V): UC_ETIKET["Eski kart"] = (r"^ESP32 DevKit", None)  # kayıtta olmayan uç
    deneme += [("uç etiketi: ESP32 sınıflanmamış", b89), ("uç etiketi: sonar deseni üç parçaya uyuyor", b90),
               ("uç etiketi: sağ dirsek sol modülde", b91), ("uç etiketi: ESP32 iki tabloda", b92), ("uç etiketi: kayıtta olmayan uç", b93)]
    if V is not None:
        def v1(RM, TB, V):
            i = next(k for k, s in enumerate(V["semalar"]) if s.get("kablo") and s.get("tur") not in KOL_ISARET_TUR)
            V["semalar"][i]["renk"] = "#123456"
        def v2(RM, TB, V):
            i = next(k for k, s in enumerate(V["semalar"]) if s.get("kablo") and s.get("tur") not in KOL_ISARET_TUR)
            V["semalar"][i]["r"] = 9.9
        def v3(RM, TB, V):
            p = next(p for p in V["parcalar"] if p.get("renk"))
            p["renk"] = "#c0392b"                                     # eski tek "Kablo yolu" rengi
        def v4(RM, TB, V):
            p = next(p for p in V["parcalar"] if p.get("renk"))
            p["kablo"] = ["X99"]
        def v5(RM, TB, V): V.pop("kablo_sinif", None)
        # F10h kontrol-5 S3-1: CAD kablo parçasının tema tonu (F10e renk_sahne beklenenini veriden okur; tablo güvencesi burada)
        def v6(RM, TB, V):
            p = next(p for p in V["parcalar"] if p.get("renk") and p.get("rt") and p["rt"].get("light") != "#b35a00")
            p["rt"] = dict(p["rt"], light="#b35a00")                  # turuncu sınıfın açık tonu (başka sınıfın parçasında)
        def v7(RM, TB, V):
            p = next(p for p in V["parcalar"] if p.get("renk") and p.get("rt"))
            del p["rt"]                                               # sahne taban renge düşer
        def v8(RM, TB, V): TEMA_TON["yesil"]["light"] = "#2e8b57"     # kaynak ton değişti, veri yeniden üretilmedi
        def v9(RM, TB, V):                                            # düzeltme turu 1 (D1): gösterim şemasına "kol" (etiketsiz boy)
            next(s for s in V["semalar"] if not str(s.get("kaynak", "")).startswith("kol_kablo:"))["kol"] = "sag"
        def _izd_boz(n, en_kucuk=None, en_buyuk=None):              # P10.7b2i: kutu (bmin, bmax, izd); izd kesim yönündeki izdüşüm
            pid = next(p["id"] for p in V["parcalar"] if cad_no(p.get("ad_cad") or p["ad"]) == n)
            b0, b1, izd = KU["k"][pid]
            yo = cad_kirp_yon(n)
            a0, a1 = izd[yo]
            izd = dict(izd)
            izd[yo] = (a0 if en_kucuk is None else en_kucuk, a1 if en_buyuk is None else en_buyuk)
            KU["k"][pid] = (b0, b1, izd)
        def v10(RM, TB, V): _izd_boz(12, en_buyuk=1327.4)            # P10.7b2f: veri eski üretimden (mesh kırpılmamış)
        def v11(RM, TB, V): _izd_boz(12, en_kucuk=180.0)              # yolun B01 kısmı da kesilmiş
        def v16(RM, TB, V): _izd_boz(9, en_buyuk=196.9)               # P10.7b2i: yol 9 kırpılmamış (ESP32 ucu küresi 194,45 + 2,5)
        def v17(RM, TB, V): _izd_boz(9, en_kucuk=20.0)                # yol 9'un sigorta kutusu (F4) başı kesilmiş
        def v18(RM, TB, V):                                           # kesim yönü değişti, GLB eski (o yönde izdüşüm yok)
            pid = next(p["id"] for p in V["parcalar"] if cad_no(p.get("ad_cad") or p["ad"]) == 9)
            KU["k"][pid] = KU["k"][pid][:2] + ({k: v for k, v in KU["k"][pid][2].items() if k != cad_kirp_yon(9)},)
        def v13(RM, TB, V):                                           # uç etiketi adı tabloda yok
            g = next(g for a in V["adimlar"] for g in [a] + (a.get("sira_grup") or []) if g.get("uc"))
            g["uc"][0]["ad"] = "Eski kart"
        def v14(RM, TB, V):                                           # numara atlıyor
            g = next(g for a in V["adimlar"] for g in [a] + (a.get("sira_grup") or []) if len(g.get("uc") or []) > 1)
            g["uc"][1]["n"] = 7
        def v15(RM, TB, V): V.pop("uc_kaynak", None)                 # eski veri
        def v12(RM, TB, V):
            V["parcalar"] = [p for p in V["parcalar"] if cad_no(p.get("ad_cad") or p["ad"]) != 12]
        if kutular is not None:
            deneme += [("veri: yol 12 mesh'i kırpılmamış (eski GLB)", v10), ("veri: yol 12 mesh'i baştan kesilmiş", v11),
                       ("veri: yol 9 mesh'i kırpılmamış (eski GLB)", v16), ("veri: yol 9 mesh'i baştan kesilmiş", v17),
                       ("veri: yol 9 kesim yönünde izdüşüm yok", v18)]
        deneme += [("veri: yol 12 parçası yok", v12)]
        if V.get("uc_kaynak") is not None:
            deneme += [("veri: uç etiketi adı tabloda yok", v13), ("veri: uç etiketi numarası atlıyor", v14), ("veri: uç etiketi işlenmemiş", v15)]
        deneme += [("veri: şema rengi elle değişti", v1), ("veri: şema yarıçapı elle değişti", v2), ("veri: CAD kablo rengi eski",
                   v3), ("veri: CAD kablosunda bilinmeyen kimlik", v4), ("veri: lejant tablosu yok", v5),
                   ("veri: CAD kablo tema tonu yanlış", v6), ("veri: CAD kablosunda tema tonu yok", v7),
                   ("veri: kaynak tonu değişti, veri eski", v8), ("veri: gösterim şemasında 'kol' alanı (D1)", v9)]
    for ad, f in deneme:
        dene(ad, f)
    sonuc += bara_yol_bozma(ANZ)                                      # P10.7b2k düzeltme turu 1 (F10u-kontrol 1)
    return sonuc


def bara_yol_bozma(analiz):
    """bara_yol_denetle'nin farklı (diferansiyel) bozması. Yollar taşınana dek temel denetim zaten HATA verdiği için dene()'nin "hata
    var" ölçütü burada dişsizdir: yol 2 elle doğru çizilir (akü yarığından yıldız 3'e, y 195'te tutucu önünden) ve yalnız yol 2'nin
    hataları sayılır. Önkoşul (doğru yol 2 temiz) tutmazsa her satır YAKALANMADI. Tutucu analizde yoksa (birleşme öncesi) atlanır."""
    if not any(p["ad"].startswith("Bara tutucusu ") for p in analiz["parcalar"]):
        print("bara yolu bozması: taban-analiz.json'da tutucu yok, atlandı (P10.7b2j birleşince koşar)")
        return []
    dogru = [[65.5, 133, -29], [62, 160, -29], [60, 195, -30], [0, 195, -30], [0, 191.9, -50]]

    def say(noktalar, hedef=None, izin=None):
        A = copy.deepcopy(analiz)
        A["kablo_yolu"][1]["noktalar"] = noktalar
        global BARA_IZIN_R
        eski = BARA_IZIN_R
        try:
            if izin is not None:
                BARA_IZIN_R = izin
            return [h for h in bara_yol_denetle(None, A, hedef) if h.startswith("bara yolu: yol 2 ")]
        finally:
            BARA_IZIN_R = eski

    temel = say(dogru)
    hedef_k = [(n, k, y, b, (1 if k == "G05" else no)) for n, k, y, b, no in bara_yol_hedefleri()]
    out = []
    for ad, h in (("bara yolu: izin bölgesi sıfır (kendi saplaması da takım sayılır)", say(dogru, izin=0.0)),
                  ("bara yolu: G05 yıldızın 1. saplamasında bekleniyor", say(dogru, hedef_k)),
                  ("bara yolu: yol 2 yıldız 4'ün takımından geçip 3'te bitiyor", say(dogru[:3] + [[25, 191.9, -55], [0, 191.9, -50]])),
                  ("bara yolu: yol 2 tutucu gövdesinden (y 185) geçiyor", say(dogru[:2] + [[0, 185, -30], [0, 191.9, -50]])),
                  ("bara yolu: yol 2 saplamaya ulaşmadan bitiyor", say(dogru[:4])),
                  # düzeltme turu 2 (F10u-kontrol T2): izin bölgesi aşağı açıktı
                  ("bara yolu: dikey, kendi saplamasında gövdeye (y 182)", say(dogru + [[0, 182, -50]])),
                  ("bara yolu: gövde içinde kendi saplama ekseni boyunca (y 185)", say(dogru + [[0, 185, -50], [0, 185, -60]])),
                  ("bara yolu: panelin altından kendi saplamasına (y 176)", say(dogru[:2] + [[0, 176, -30], [0, 176, -55], [0, 191.9, -50]]))):
        n = 0 if temel else len(h)
        out.append((ad, n, (temel or h)[:2], "denetim" if n else ""))
    return out


def _modul_kopya(M):
    """rehber_metin'in yalnız KABLO_AD ve SEMA'sını taşıyan kopyası (bozma denemesi asıl modülü değiştirmez)."""
    import types
    k = types.SimpleNamespace()
    k.KABLO_AD = copy.deepcopy(M.KABLO_AD)
    k.SEMA = list(copy.deepcopy(M.SEMA))
    k.ADIM = copy.deepcopy(M.ADIM)                                    # P10.7b2c B: bağlantı tablosu satırları (kablo listesi)
    k.ADIM_HAM = copy.deepcopy(M.ADIM_HAM)
    return k


def ozet(TB=None):
    TB = TB or Tablo()
    t = cizim_tablosu(TB)
    print("kablo eşleme: tablo %d kablo, çizilen %d, çizilmeyen %d" % (t["toplam"], t["cizilen"], len(t["cizilmeyen"])))
    print("  çizilmeyen:", ", ".join(t["cizilmeyen"]))
    print("  üç sınıf (P10.7b2c): yol çizimi %d (%s) · bağlantı tablosu %d (%s) · hiçbiri %d (%s)" % (
        t["yol_cizimi"], ", ".join("%s %d" % kv for kv in t["yol_kaynak"].items()), len(t["baglanti_tablosu"]),
        ", ".join(t["baglanti_tablosu"]) or "-", len(t["hicbiri"]), ", ".join(t["hicbiri"]) or "-"))
    kar = []
    for n, ids in CAD_ESLEME.items():
        c = TB.cizim(ids)
        if c.get("karisik"):
            kar.append("Kablo yolu %d (%s)" % (n, "/".join(c["karisik"])))
    print("  karışık sınıflı CAD yolu (ana kablonun rengini alır):", "; ".join(kar) or "yok")
    return t


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri", default="")
    ap.add_argument("--bozma-denemesi", action="store_true")
    ap.add_argument("--sema-boy-yaz", action="store_true", help="kablolar.json sema_boy alanlarını şemalardan yaz (yalnız bu alan)")
    a = ap.parse_args()
    if a.sema_boy_yaz:
        print("sema_boy yazıldı: %d kablo (%s)" % (sema_boy_yaz(), os.path.relpath(TABLO_YOL, ROBOT)))
        sys.exit(0)
    TB = Tablo()
    V = json.load(open(a.veri, encoding="utf-8")) if a.veri else None
    KUTU = glb_kutulari(os.path.join(os.path.dirname(os.path.abspath(a.veri)), "robot.glb")) if a.veri else None   # P10.7b2f
    if a.bozma_denemesi:
        s = bozma_denemesi(V, KUTU)
        kac = [x for x in s if x[1] == 0]
        for ad, n, h, mek in s:
            print("  %-55s %s %s" % (ad, "YAKALANDI (%d; %s)" % (n, mek) if n else "KAÇTI", [x[:160] for x in h[:1]]))
        print("bozma denemesi: %d / %d yakalandı" % (len(s) - len(kac), len(s)))
        sys.exit(1 if kac else 0)
    import rehber_metin as RM
    try:                                                             # kol bölüm anahtarları (FreeCAD'siz türetme)
        import rehber_kol_kablo as KK
        kb = [b["k"] for b in KK.turet()[0]]
        kb_hata = []
    except Exception as e:                                           # noqa: BLE001
        kb = None                                                    # kontrol §2-4: türetilemezse eşleme sınaması dişsiz kalır → HATA
        kb_hata = ["kol bölümleri türetilemedi (%s: %s): kol eşlemesi sınanamadı" % (type(e).__name__, e)]
    h = kb_hata + kaynak_denetle(TB, RM, kb)
    gh, gb = geometri_denetle(TB)
    h += gh
    bh = bara_yol_denetle(TB)                                        # P10.7b2k düzeltme turu 1: CAD yolu × bara tutucusu / saplama
    h += bh
    print("bara yolu (CAD yolu × tutucu / saplama, izin ±%g mm): hedef %s; hata %d" % (
        BARA_IZIN_R, ", ".join("yol %d %s%s %s %d" % (n, k, y, b, no or 0) for n, k, y, b, no in bara_yol_hedefleri(TB)), len(bh)))
    kd = cad_kirp_denetle()                                          # P10.7b2i: kesim korunan bölümü eskisinden ayırıyor mu
    h += kd
    print("kırpma kesimi: %s; hata %d" % (", ".join("yol %d %s" % (n, cad_kirp_metin(n)) for n in sorted(CAD_KIRP)), len(kd)))
    ozet(TB)
    print("geometri: yol %d, eşik %g mm, taban dışı y >= %g; hata %d, bilgi %d" % (len(CAD_ESLEME), GEO_ESIK, GEO_TABAN_DISI, len(gh), len(gb)))
    for x in gb:
        if "istisna" in x or "elle bakıldı" in x:
            print("  BILGI", x)
    sh, sb, st = sema_geometri_denetle(TB, RM)                       # P10.7b2c: gösterim şemaları
    h += sh
    print("şema geometrisi: %d şema (%s), eşik %g mm; hata %d, bilgi %d, istisnalı %d" % (
        len(st), ", ".join("%s %d" % (k, sum(1 for s in st if s["kaynak"] == k)) for k in SEMA_KAYNAK), GEO_ESIK, len(sh), len(sb),
        sum(1 for s in st if s["istisna"])))
    for s in st:
        print("  ŞEMA %-34s %-4s %-9s yan %s · uç %s%s%s" % (
            s["sema"][:34], s["kod"], "/".join(s["kimlik"]), " ".join("%s%s:%s" % (k, y, d) for k, y, _p, _c, d in s["yanlar"]),
            " ".join("%s:%s" % (a, d) for a, _u, _y, d in s["uclar"]),
            (" · geçiş " + " ".join("%s:%s" % (lv, "tamam" if d == "tamam" else "HATA") for lv, _n, d in s["gecis"])) if s["gecis"] else "",
            (" · istisna " + ", ".join(s["istisna"])) if s["istisna"] else ""))
    for x in sb:
        if "istisna" in x or "elle bakıldı" in x:
            print("  BILGI", x)
    bh = baglanti_tablosu_denetle(TB, RM)                            # P10.7b2c B
    h += bh
    print("bağlantı tablosu: %d kablo (%s); hata %d" % (len(BAGLANTI_TABLOSU), ", ".join(
        "%s %s" % kv for kv in sorted(BAGLANTI_TABLOSU.items())), len(bh)))
    yh = sema_boy_denetle(TB, RM)
    h += yh
    sbt = sema_boy_tablosu(TB, RM)
    print("şema boyu (%s): %d şema, kayıt tazeliği hata %d; şema > kayıttaki: %d" % (
        SEMA_BOY_ETIKET, len(sbt), len(yh), sum(1 for x in sbt if x[5] is not None and x[5] > 0)))
    for k, kes, mm, ad, sm, fark, ortak in sbt:
        print("  BOY %-4s %-24s kayıt %5s mm (%s) · şema %5d mm · fark %s%s" % (
            k, kes[:24], mm, ad, sm, ("%+d" % fark) if fark is not None else "-", (" · ortak " + "/".join(ortak)) if ortak else ""))
    eh, nh, uh = sema_boy_etiketi_denetle(), sema_not_denetle(TB, RM), uc_yer_eki_denetle(TB, RM)   # düzeltme turu 1
    h += eh + nh + uh
    print("düzeltme turu 1: kart boy etiketi hata %d; gösterim şeması notu (%s) %d şema, hata %d; yer eki (%s) hata %d" % (
        len(eh), "/".join(sorted(SEMA_NOT_KAYNAK)), sum(1 for s in RM.SEMA if s[0] in SEMA_NOT_KAYNAK), len(nh),
        ", ".join(UC_YER_EK), len(uh)))
    try:                                                             # P10.7b2f: uç etiketleri
        import rehber_gorunum as _RG
        ueh = uc_etiket_denetle(TB, _RG.cad_parcalar())
    except Exception as e:                                           # noqa: BLE001
        ueh = ["uç etiketi: CAD etiketleri okunamadı (%s: %s)" % (type(e).__name__, e)]
    h += ueh
    print("uç etiketi: %d kısa ad modelde, %d modelsiz; hata %d" % (len(UC_ETIKET), len(UC_MODELSIZ), len(ueh)))
    ae = ayirt_edilemeyen(TB)
    print("geometrinin ayırt edemediği çiftler (onay kaydı korur): %d" % len(ae))
    for n, m, k, yer in ae:
        print("  yol %d: %s ↔ %s (%s)" % (n, m, k, "yol " + ", ".join(map(str, yer)) if yer else "çizilmeyen"))
    rf = renk_farki_tablosu(TB)
    for tm in ("light", "dark"):
        print("renk farkı (ΔE00, %s) en yakın: %s" % (tm, "; ".join(["%s ↔ %s %.1f" % (a, b, d) for t, a, b, _x, _y, d in rf if t == tm][:5])))
    ho = onay_denetle()
    print("onay kaydı (kablo bölümü): %s" % ("tutuyor" if not ho else "%d fark" % len(ho)))
    h += ho
    if V is not None:
        hv, es = veri_denetle(V, TB)
        h += hv
        kh = kirp_veri_denetle(V, KUTU)                                  # P10.7b2f
        h += kh
        uh2 = uc_veri_denetle(V)
        h += uh2
        print("veri uç etiketi: %d konum, hata %d" % (sum(1 for a in V["adimlar"] for g in [a] + (a.get("sira_grup") or [])
                                                        if g.get("uc") or g.get("uc_yok")), len(uh2)))
        print("kırpılan CAD yolları (%s): robot.glb %s; hata %d" % (
            ", ".join("yol %d %s" % (n, cad_kirp_metin(n)) for n in sorted(CAD_KIRP)), "okundu" if KUTU is not None else "YOK", len(kh)))
        print("veri: eşlemesiz çizim %d%s" % (len(es), (": " + "; ".join(es[:6])) if es else ""))
        h += ["eşlemesiz çizim: %s" % x for x in es]
    for x in h[:40]:
        print("  HATA", x)
    print("SONUÇ", "GEÇER" if not h else "KALDI (%d hata)" % len(h))
    sys.exit(0 if not h else 1)
