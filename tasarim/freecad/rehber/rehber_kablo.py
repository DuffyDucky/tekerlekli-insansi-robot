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
    "hazir-usb": {"light": "#828282", "dark": "#818181"}, "hazir-hdmi": {"light": "#1d3854", "dark": "#5ba7b8"},
    "hazir-csi": {"light": "#6f3312", "dark": "#b2916b"},
}
# P10.7b1 açık işler turu (kontrol-2 madde 17): en yakın çiftler ΔE00 < RENK_FARK_ESIK olduğu için yeniden tonlandı (eski → yeni):
# açık beyaz #4e6d7d → #4c7078, USB #7c7c7c → #828282, HDMI #2f3f4f → #1d3854, CSI #8a5a3c → #6f3312; koyu siyah #b9bec5 → #b3b3b3,
# USB #7d7d7d → #818181, HDMI #7f9bb5 → #5ba7b8, CSI #c0916c → #b2916b. Ana sınıfların (kırmızı … mor) tonları değişmedi.
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
    9: ("G18",),                                                         # F4 → XL4016 çevre (yolun devamı eski tasarım: GEO_ISTISNA)
    10: ("A02", "A01", "A03", "A04", "A05", "A06"),                      # acil stop
    11: ("Q03", "X01"),                                                  # sol sonar → arayüz kartı → ESP32 (orta / sağ sonara gitmez)
    12: ("B01",),                                                        # BTS sol sinyali → ESP32 (üst kısım eski yol: GEO_ISTISNA; U06 "ESP32 USB" şemasında)
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
    "Dağıtım kartı A": r"^Servo dagitim karti A", "Dağıtım kartı B": r"^Servo dagitim karti B",
    "Arayüz kartı": r"^Arayuz karti", "ESP32 DevKit": r"^ESP32 (DevKit|tasiyici)", "ESP32 / arayüz kartı": r"^(ESP32 |Arayuz karti)",
    "Elektronik katı": r"^(Arayuz karti|PCA9685|ESP32 )", "PC817 modülü (arayüz kartı)": r"^Arayuz karti",
    "HC-SR04 sağ": r"^Sonar HC-SR04 \(sag\)", "HC-SR04 orta": r"^Sonar HC-SR04 \(orta\)", "HC-SR04 sol": r"^Sonar HC-SR04 \(sol\)",
    "Acil stop mantarı": r"^Acil stop kontak govdesi",
    "XT60 (akü tarafı)": NOMINAL, "XT60 (robot tarafı)": NOMINAL, "Anahtarlı bara": NOMINAL,
    "Yıldız barası": NOMINAL, "Acil stop düğümü": MODELSIZ,
    "Dağıtım kartı C": TABAN_DISI, "Kafa giriş klemensi": TABAN_DISI, "USB hub": TABAN_DISI,
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
    ("XT60 (akü tarafı)", "−"): (_AKU_EKSI, r"^Aku LiFePO4", "− kutup: yol 2 baş noktası ('aku - -> WAGO yildiz noktasi')"),
    ("XT60 (robot tarafı)", "+"): (_AKU_ARTI, r"^Aku LiFePO4", "akü tarafıyla aynı yerde (geçme çift); + kutup yol 1 başı"),
    ("XT60 (robot tarafı)", "−"): (_AKU_EKSI, r"^Aku LiFePO4", "akü tarafıyla aynı yerde (geçme çift); − kutup yol 2 başı"),
    ("Yıldız barası", "*"): ((-20.0, 186.0, -90.0), None,
                             "güç panelindeki yıldız noktası: yol 2 son noktası ('aku - -> WAGO yildiz noktasi (guc paneli)'); yanında modelli parça yok"),
    ("Anahtarlı bara", "*"): (None, r"^Role 12 V",
                              "modeli yok; CAD yolları bara yerine röleden çıkar ('role -> WAGO'): yerine Röle K1 kutusu. Röle K1 ↔ bara ayırt edilmez"),
    ("Acil stop düğümü", "*"): (None, None,
                                "güç panelinde küçük pertinaks kart; CAD'de ne modeli ne yol noktası var (yerleşim P10.7b2): sınanmaz, elle bakıldı"),
}
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
    9: "yolun ucu ESP32'de: CAD yolu eski tasarımı çiziyor (çevre 5 V doğrudan ESP32'ye); tabloda G19 arayüz kartının 5 V klemensine "
       "gider ve bu yolda çizili sayılmaz (P10.7b2: yol yeniden çizilir)",
    12: "yolun üst ucu kafada: CAD yolu 05.11 öncesi ESP32 → kafa USB hattını çiziyor; ESP32 USB (U06) artık hub'a direk arka yüzünden "
        "gider ve \"ESP32 USB\" şemasında çizilir, bu yolda sayılmaz (P10.7b2: yol yeniden çizilir)",
}

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
        return "%s: %s → %s · %s · %s · acil stopta %s" % (b["kimlik"], b["a"], b["b"], b["kesit"], b["koruma"],
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
        """app.js lejantı: sınıf → [renk, okunur ad, tema tonları]. Hazır kablo türleri ayrı satır (hazir-usb, hazir-hdmi, hazir-csi)."""
        ad = dict(kirmizi="12 V doğrudan (kırmızı)", turuncu="Anahtarlı bara, motor (turuncu)", sari="Servo gücü 6 V (sarı)",
                  mavi="5 V (mavi)", yesil="Acil stop (yeşil)", mor="Sinyal (mor)", siyah="Toprak (siyah)", beyaz="Analog ses (beyaz)",
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
    for tm in ("light", "dark"):
        for i, a in enumerate(ad):
            for b in ad[i + 1:]:
                out.append((tm, a, b, L[a][2][tm], L[b][2][tm], round(de2000(L[a][2][tm], L[b][2][tm]), 1)))
    return sorted(out, key=lambda x: x[5])


def renk_farki_denetle(TB=None):
    return ["kablo tonları %s ↔ %s (%s: %s / %s) ΔE00 %.1f < %g" % (a, b, tm, x, y, d, RENK_FARK_ESIK)
            for tm, a, b, x, y, d in renk_farki_tablosu(TB) if d < RENK_FARK_ESIK]


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


def geometri_denetle(TB=None, analiz=None, esleme=None, istisna=None):
    """CAD yolu noktaları ↔ eşlenen kabloların uç parçaları (kural yukarıda). Doner (hata, bilgi)."""
    TB = TB or Tablo()
    A = analiz if analiz is not None else json.load(open(GEO_ANALIZ, encoding="utf-8"))
    esleme = CAD_ESLEME if esleme is None else esleme
    istisna = GEO_ISTISNA if istisna is None else istisna
    modelli = [p for p in A["parcalar"] if p.get("tur") not in ("Baski", "Lazer", "Baglanti") and not p["ad"].startswith(("Burc", "Kablo yolu"))]
    hata, bilgi = [], []

    def cad(desen):
        return [p for p in modelli if re.search(desen, p["ad"])]
    for n, ids in sorted(esleme.items()):
        if n > len(A["kablo_yolu"]):
            hata.append("yol %d: taban-analiz.json'da yok" % n)
            continue
        pts = A["kablo_yolu"][n - 1]["noktalar"]
        cizgiler = [pts]
        ana = GEO_DAL.get(n)
        if ana:
            ap = A["kablo_yolu"][ana - 1]["noktalar"]
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
            for y, parcalar in zip("ab", uc_parcalari(TB, k)):
                sonuc = []
                for p in parcalar:
                    s = parca_sinifi(p)
                    if s is None:
                        hata.append("yol %d %s: uç parçası '%s' PARCA_CAD haritasında yok" % (n, k, p))
                        sonuc.append(False)
                    elif s == TABAN_DISI:
                        b = parca_bolgesi(p)
                        if b is None:
                            hata.append("yol %d %s: taban dışı uç '%s' TABAN_DISI_PARCA'da bölgesiz" % (n, k, p))
                            sonuc.append(False)
                            continue
                        yan_sinif["disi"].add(b)
                        sonuc.append(b in dis_bolge)
                    elif s in (NOMINAL, MODELSIZ):
                        m = modelsiz_konum(p, uc_kutbu(TB, k, y))
                        if m is None:
                            hata.append("yol %d %s: modelsiz uç '%s' MODELSIZ_KONUM'da yok" % (n, k, p))
                            sonuc.append(False)
                            continue
                        nokta, vekil, _g = m
                        if nokta is None and vekil is None:
                            yan_sinif["elle"] = True
                            bilgi.append("yol %d %s %s: '%s' modelsiz, nominal konumu yok: elle bakıldı" % (n, k, y, p))
                            sonuc.append(True)
                            continue
                        vp = cad(vekil) if vekil else []
                        uc_parca.update(c["ad"] for c in vp)
                        if nokta is not None:
                            nominal.append(nokta)
                            d = min(_yol_kutu(c_, (nokta[0], nokta[0], nokta[1], nokta[1], nokta[2], nokta[2])) for c_ in cizgiler)
                        elif vp:
                            d = min(_yol_kutu(c_, c["bb"]) for c in vp for c_ in cizgiler)
                        else:
                            hata.append("yol %d %s: '%s' vekili için CAD parçası bulunamadı (%s)" % (n, k, p, vekil))
                            sonuc.append(False)
                            continue
                        sonuc.append(d <= GEO_ESIK)
                    else:
                        cp = cad(s)
                        if not cp:
                            hata.append("yol %d %s: '%s' için CAD parçası bulunamadı (%s)" % (n, k, p, s))
                            sonuc.append(False)
                            continue
                        d = min(_yol_kutu(c_, c["bb"]) for c in cp for c_ in cizgiler)
                        uc_parca.update(c["ad"] for c in cp)
                        sonuc.append(d <= GEO_ESIK)
                if not any(sonuc):
                    hata.append("yol %d: %s %s yanı (%s) yola ulaşmıyor (eşik %g mm / taban dışı bölge %s)" % (
                        n, k, y, ", ".join(parcalar), GEO_ESIK, "/".join(sorted(x for x in dis_bolge if x)) or "yok"))
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
                    bilgi.append("yol %d %s ucu: %s (istisna: %s)" % (n, ad_, neden, istisna[n][:60]))
                else:
                    hata.append("yol %d %s ucu %s: %s" % (n, ad_, [round(x, 1) for x in uc], neden))
    return hata, bilgi


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
    for n in sorted(GEO_ISTISNA):
        g.append(_RK.girdi("GEO_ISTISNA %d" % n, GEO_ISTISNA[n], "geometri istisnası"))
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
    TB = TB or Tablo()
    c = cizilen_kimlikler(RM)
    cizilen = [k for k in TB.K if k in c]
    cizilmeyen = [k for k in TB.K if k not in c]
    return dict(toplam=len(TB.K), cizilen=len(cizilen), cizilmeyen=cizilmeyen, nerede={k: c[k] for k in cizilen})


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


# ------------------------------------------------------------------ bozma denemesi
def bozma_denemesi(V=None):
    import importlib
    import rehber_metin as RM0
    sonuc = []
    ANZ = json.load(open(GEO_ANALIZ, encoding="utf-8"))

    def dene(ad, f):
        RM = copy.deepcopy(_modul_kopya(RM0))
        TB = Tablo()
        eski_cad, eski_kol = copy.deepcopy(CAD_ESLEME), copy.deepcopy(KOL_ESLEME)
        eski_ton, eski_yc = copy.deepcopy(TEMA_TON), copy.deepcopy(KESIT_YARICAP)
        eski_mk = copy.deepcopy(MODELSIZ_KONUM)
        try:
            V2 = copy.deepcopy(V) if V is not None else None
            f(RM, TB, V2)
            h = kaynak_denetle(TB, RM)
            h += geometri_denetle(TB, ANZ, CAD_ESLEME, GEO_ISTISNA)[0]
            if V2 is not None:
                h += veri_denetle(V2, TB)[0]
            ho = onay_denetle()                                       # açık işler turu: onay kaydı ayrı mekanizma olarak sayılır
        finally:
            CAD_ESLEME.clear(); CAD_ESLEME.update(eski_cad)
            KOL_ESLEME.clear(); KOL_ESLEME.update(eski_kol)
            TEMA_TON.clear(); TEMA_TON.update(eski_ton)
            KESIT_YARICAP.clear(); KESIT_YARICAP.update(eski_yc)
            MODELSIZ_KONUM.clear(); MODELSIZ_KONUM.update(eski_mk)
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
              ("nominal: yıldız noktası taşındı", b26), ("renk: koyu HDMI eski ton", b27)]
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
        deneme += [("veri: şema rengi elle değişti", v1), ("veri: şema yarıçapı elle değişti", v2), ("veri: CAD kablo rengi eski",
                   v3), ("veri: CAD kablosunda bilinmeyen kimlik", v4), ("veri: lejant tablosu yok", v5),
                   ("veri: CAD kablo tema tonu yanlış", v6), ("veri: CAD kablosunda tema tonu yok", v7),
                   ("veri: kaynak tonu değişti, veri eski", v8)]
    for ad, f in deneme:
        dene(ad, f)
    return sonuc


def _modul_kopya(M):
    """rehber_metin'in yalnız KABLO_AD ve SEMA'sını taşıyan kopyası (bozma denemesi asıl modülü değiştirmez)."""
    import types
    k = types.SimpleNamespace()
    k.KABLO_AD = copy.deepcopy(M.KABLO_AD)
    k.SEMA = list(copy.deepcopy(M.SEMA))
    return k


def ozet(TB=None):
    TB = TB or Tablo()
    t = cizim_tablosu(TB)
    print("kablo eşleme: tablo %d kablo, çizilen %d, çizilmeyen %d" % (t["toplam"], t["cizilen"], len(t["cizilmeyen"])))
    print("  çizilmeyen:", ", ".join(t["cizilmeyen"]))
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
    a = ap.parse_args()
    TB = Tablo()
    V = json.load(open(a.veri, encoding="utf-8")) if a.veri else None
    if a.bozma_denemesi:
        s = bozma_denemesi(V)
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
    ozet(TB)
    print("geometri: yol %d, eşik %g mm, taban dışı y >= %g; hata %d, bilgi %d" % (len(CAD_ESLEME), GEO_ESIK, GEO_TABAN_DISI, len(gh), len(gb)))
    for x in gb:
        if "istisna" in x or "elle bakıldı" in x:
            print("  BILGI", x)
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
        print("veri: eşlemesiz çizim %d%s" % (len(es), (": " + "; ".join(es[:6])) if es else ""))
        h += ["eşlemesiz çizim: %s" % x for x in es]
    for x in h[:40]:
        print("  HATA", x)
    print("SONUÇ", "GEÇER" if not h else "KALDI (%d hata)" % len(h))
    sys.exit(0 if not h else 1)
