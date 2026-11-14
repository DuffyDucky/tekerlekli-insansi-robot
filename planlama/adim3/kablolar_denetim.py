"""Kablo tablosunun kalıcı denetimi (planlama/adim3/kablolar.json).

FreeCAD gerekmez, yalnız standart kütüphane (+ `git show` ile main'deki kanallar.yaml okunur).

    py -3 planlama/adim3/kablolar_denetim.py                    # bütün sınamalar
    py -3 planlama/adim3/kablolar_denetim.py --bozma-denemesi   # + her sınama için bilerek bozulmuş kopya: yakalıyor mu
    py -3 planlama/adim3/kablolar_denetim.py --kanallar DOSYA   # main yerine yerel kanallar.yaml

Elektrik güvenliği sınamaları kablonun kendi beyanına (devre türü, dal, koruma sayısı) değil devrenin yapısına dayanır:
her damar ucu `dugumler` listesindeki bir düğümdür, her düğüm bir ağa (`aglar`) bağlıdır, ağları koruyucular (sigorta, BMS,
dönüştürücü sınırı, direnç) ve anahtarlar (ana anahtar, K1 / K2 kontağı, mantar NC, bobinler) birbirine bağlar. Denetim her
kablonun besleme zincirini, koruyanını, dalını ve acil stop durumunu buradan yeniden kurar ve kayıtla karşılaştırır.

Düzeltme turu 2 (P107a-kontrol-2.md D1′): tablonun kendi değerleri (koruyucu akımı, istisna kapsamı, klemens sınırı, kesit
tablosu, ortam katsayısı, dal ↔ sigorta, §12 listeleri, donanım adetleri) bağımsız kaynaktan ayrıştırılan sayıyla / öğeyle
karşılaştırılır: elektrik.md "Sigorta listesi" tablosu ve blok şeması, kablolama-on-kararlar.md karar satırları ve §12,
maliyet.json model / adet alanları, bu dosyadaki sabit kaynak tabloları (kesit, katsayı, klemens sınırı, istisna kararları).

Sınamalar:
    alanlar      zorunlu alanlar; tanımsız alan yok (kablo ve damar); durum eksik / teyit ile tutarlı; devre türü, dal, koruma
                 izinli değer kümesinden; kayıt düzeyi uç parçası damar uçlarının parçasıyla tutarlı
    iki_uc       her kablonun ve damarın iki ucu dolu
    yer_tutucu   'kesin' kayıtta uçlarda, damarlarda, sonlandırmada; her kayıtta uç alanlarında '?', '…', 'öneri', 'belirlenecek',
                 'bilinmiyor', 'sonra bakılacak', 'TBD' ya da boş yok (eksik bilgi eksik / teyit alanına yazılır)
    koruyucu     her koruyucunun akımı ve biçimi (standart / mini) elektrik.md sigorta listesinden, blok şemasından ve varsa
                 kablolama-on-kararlar.md karar satırından ayrıştırılan sayıyla; sipariş satırının (maliyet.json) modelindeki
                 amperle; koruyucunun adındaki sayıyla aynı. Belgede sayı bulunamazsa hata
    ag           her uç düğümler listesinde; düğümün ağı tanımlı; adından güç ucu olduğu belli düğümün ağı var; bir telin iki
                 ucu aynı ağda (ya da arada kayıtlı hat sigortası / direnç); 5 V Pi ve 5 V çevre ağları hiçbir telde / elemanda /
                 kart içi bağda birleşmiyor; her güç ağının aküye kadar beslemesi var
    ayni_nokta   aynı klemens / pin iki ayrı işe verilmemiş (ortak_noktalar dışında bir uç yalnız bir kez)
    esp32_pin    ESP32 uçları pin-haritasi.md §9 JSON'uyla birebir; GPIO numarası düğümün sayı alanından (metin ayıklanmaz)
    pca_kanal    PCA9685 kanalları main kod/jestler/kanallar.yaml ve pin-haritasi.md §9 ile aynı (düğümün sayı alanından)
    kesit        kural tablosu ve ortam katsayıları bu dosyadaki sabit kaynak tablolarıyla aynı; bölge sıcaklığı kaynak
                 satırından; akım taşıyan her + / − damar (devre türü ne yazılırsa yazılsın) koruyanının akımına göre kesit alır:
                 koruyan, damarın ağından aküye doğru ilk akım sınırlayan eleman (koruyucular tablosu); sınır = tablo × bölgenin
                 ortam katsayısı. Kayıttaki koruma kimliği türetilenle aynı olmalı. Geçmeyen kablo yalnız kayıtlı istisna ya da
                 'karara bağlı'. İstisna kabloyu sınamadan çıkarmaz: üye listesi sabit karar listesiyle (ISTISNA_KARARI) aynı;
                 türetilen koruyan istisnanın koruyucusu; akım ≤ istisnanın üst sınırı (belgesiz koruyucuda üst sınır ≤ en ince
                 izinli kesitin sınırı); kesit ≥ en ince izinli kesit; üst sınırın sayısı kaynak satırında. Bara köprüleri de
                 kesit sınamasına girer
    donus        her + damarlı kablonun aynı kabloda − damarı ya da kayıtlı ortak dönüşü var, dönüş kesiti + damarından ince
                 değil; motor çıkışları çift; her dönüş düğümü tel / kart içi bağlarla yıldız noktasına varıyor
    tahmin       boy (ölçüm / CAD) ile boy_tahmin ayrı; tahmin montaj-analiz uçlarından yeniden hesaplanınca aynı
    klemens      her damar ucunun türü (uc_turu, sabit sözlük) var; klemense / baraya giren iletkenin kesiti türün sınırını
                 aşmıyor (sınırlar UC_TURU_SINIRI sabit tablosundan; tablodaki klemens_turleri bununla aynı olmalı); sınırı
                 bilinmeyen uca 12 AWG yalnız 'klemens:' teyit maddesiyle; 12 AWG kabloda sonlandırma metni 5,08 / WAGO / BTS
                 klemensi diyorsa o tür bir uçta yazılı; saplamalı düğümde saplama başına pabuç sınırı ve köprü adedi
    malzeme      malzeme türü başına ihtiyaç × (1 + pay) ≤ liste ≤ ⌈ihtiyaç × (1 + pay) ÷ birim⌉ + 1 birim (iki yönlü)
    donanim      tablodan sayılan adetler maliyet.json'la: hat sigortası yuvası (mini sigorta sayısı), her sigorta satırı, saplama
                 takımı, halka pabuç paketleri (uç türünden), röle başına bir 1N4007 + yedek (yapısal alan)
    acil_stop    besleme zinciri ağlardan yeniden kurulur; kayıttaki zincir, dal ve acil stop bayrağı bununla aynı; her dalın
                 §12 ifadesi kablolama-on-kararlar.md §12'nin doğru listesinde tam öğe olarak (alt dize değil), öbür listede
                 değil; dal ↔ sigorta ve sigorta ↔ ilk eleman elektrik.md blok şemasındaki sigorta bloklarıyla aynı
    kaynak       her kablonun kaynağı var; belge:satır satırı var ve o satırlarda kablonun ayırt edici terimlerinden biri geçiyor
                 (genel sözcükler ve çıplak sayılar ayırt edici değil); json#anahtar yolu çözülüyor; koruyucu / anahtar / bölge
    sayi_metin   kablo adı ve kesit notundaki "N A" / "N AWG" sayıları kaydın koruyucusu / kesitiyle tutarlı; her metin
                 alanındaki "F<n> N A" ve "ana sigorta N A" koruyucular tablosuyla aynı
    denetim_62   10.11 dökümünün 62 satırının her biri bir kayda ya da 'çıkan / birleşen' notuna bağlı
    gorunum      kablolar.md ve elektrik.md'nin sonundaki dal başına kesit bloğu tablodan üretilenle aynı (kablolar_uret.py)

Çıkış kodları: 0 hepsi geçti (ve --bozma-denemesi'nde her bozma yakalandı); 1 en az bir sınama ya da bozma denemesi
geçmedi; 2 kaynak okunamadı (tablo, pin haritası, main'deki kanallar.yaml).
"""
import argparse
import copy
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

BURASI = Path(__file__).resolve().parent
KOK = BURASI.parents[1]
sys.path.insert(0, str(BURASI))
import kablolar_uret  # noqa: E402

TABLO = BURASI / "kablolar.json"
GORUNUM = BURASI / "kablolar.md"
PIN = BURASI / "pin-haritasi.md"
KOK_BELGE = BURASI / "kablolama-on-kararlar.md"
MALIYET = KOK / "planlama" / "maliyet.json"
MONTAJ = "tasarim/freecad/montaj/montaj-analiz.json"
KANALLAR_MAIN = "origin/main:kod/jestler/kanallar.yaml"
DURUMLAR = ("kesin", "kablajda teyit edilecek", "karara bağlı")
ZORUNLU = ("kimlik", "ad", "devre", "demet", "dal", "uc_a", "uc_b", "damarlar", "kesit", "renk", "sonlandirma", "koruma",
           "acil_stopta_enerjili", "besleme_zinciri", "boy", "rehber", "eksik", "teyit", "durum", "kaynak", "denetim_62")
KART_USTU = {"UART0_TX", "UART0_RX", "DURUM_LED"}
ESP32_GPIO_DISI = {"3V3", "GND", "VIN", "micro USB"}
GUC_KUTUP = ("+", "−", "±")
BES_V = {"5V-pi", "5V-cevre"}
YER_TUTUCU = re.compile(r"(^\s*$|\?|…|\.\.\.|öneri|belirlenecek|bilinmiyor|bilinmeyen|sonra bakılacak|bakılacak|\bTBD\b|^\s*-+\s*$)",
                        re.I)
ALAN_KABLO = set(ZORUNLU) | {"bolge", "boy_not", "boy_tahmin", "gerilim_dusumu_kontrol", "hazir_kablo", "kesit_istisna", "kesit_not",
                             "malzeme", "not", "ortak_donus", "tarihce"}
ALAN_DAMAR = {"a", "b", "ad", "ara", "ara_koruyucu", "ara_uc", "gpio", "not", "pca_ad", "pca_kanal", "pin", "kesit", "uc_turu", "uc_kuyrugu"}
SAYI = r"(\d+(?:,\d+)?)"


def tr_sayi(s):
    return float(s.replace(",", "."))


# ---- sabit kaynak tabloları (tablodaki değer bunlarla karşılaştırılır; değiştirmek bir karar ve bu dosyada iz ister)
# kesit_kurali.tablo dayanakları: 33 CFR 183.425 Table 5 (80 °C sütunu) ve NFPA 79 (2018) Table 12.5.1 (75 °C sütunu, Lutze baskısı)
KESIT_KAYNAGI = {12: {"cfr": 35, "nfpa79": 25}, 16: {"cfr": 20, "nfpa79": 10}, 18: {"cfr": 15, "nfpa79": 7},
                 20: {"cfr": None, "nfpa79": 5}, 22: {"cfr": None, "nfpa79": 3}, 24: {"cfr": None, "nfpa79": 2}}
# ortam düzeltmesi: NEC 2020 Table 310.15(B)(1), 75 °C sütunu (ikincil kaynak; kesit_kurali.ortam.kaynak)
KATSAYI_KAYNAGI = [(30, 1.0), (45, 0.82), (50, 0.75)]
# bölge sıcaklığı: kaynak satırında bu kalıpla yazılı sayı
BOLGE_KALIBI = {"etek": r"etek havası ≤ (\d+) °C", "kafa": r"normal karşılamada \*\*~(\d+) °C"}
# uç türü → en kalın kesit (mm²); None: bilinmiyor; "klemens değil": lehim / fiş. Kaynak: maliyet.json satırları
UC_TURU_SINIRI = {
    "bara-pabuc": 6.0,       # kalem 154 sarı RV 5.5-5 '4.0-6.0 mm' (saplamada pabuç yığını)
    "pabuc": 6.0,            # kalem 154 (cihaz saplamasına halka pabuç)
    "wago-2273": 2.5,        # kalem 62 WAGO 2273-203: 0,5–2,5 mm²
    "klemens-508": None,     # kalem 80 2 pin 5,08 mm vidalı klemens: satıcı sayfasında kesit yok
    "bts-guc": None,         # kalem 45 BTS7960 modülü: güç klemensinin kesiti yazmıyor
    "modul-vidali": None,    # XL4016 / SY8205 / regülatör / PC817 modülü / mantar kontak vidası: kesit yazmıyor
    "sigorta-kutusu": None,  # kalem 51 6 yollu bıçak sigorta kutusu: uç tipi ve kesit yazmıyor
    "lehim": "klemens değil",
    "konnektor": "klemens değil",
}
# uç türü → (aldığı iletken, en ince kesit mm²); None: bilinmiyor. Kaynak: kalem 62 WAGO 2273 yalnız tek telli 0,5–2,5 mm²
# (üçüncü bağımsız bakış, dağıtıcı veri sayfaları); kalem 162 kırmızı pabuç 0,50–1,50 mm² (en ince pabuç); vidalı klemens sıkıştırma
UC_TURU_ILETKEN = {"bara-pabuc": ("tek telli / ince telli", 0.5), "pabuc": ("tek telli / ince telli", 0.5),
                   "wago-2273": ("tek telli", 0.5), "klemens-508": ("tek telli / ince telli", None), "bts-guc": (None, None),
                   "modul-vidali": (None, None), "sigorta-kutusu": (None, None), "lehim": (None, None), "konnektor": (None, None)}
# alt sınırı belgesiz olup ince teli (< 0,5 mm², 22 AWG ve incesi) almayan kart klemensi (ek tur kararı: lehim + makaron)
ALT_SINIRI_BELGESIZ = {"klemens-508"}
KUCUK_KESIT_MM2 = 0.5
# malzeme → iletken (maliyet.json satırları: silikon kablo çok ince telli, sinyal teli çok telli); None: hazır / kendi ucu
MALZEME_ILETKEN = {"silikon-12": "ince telli", "silikon-16": "ince telli", "silikon-18": "ince telli", "sinyal-22": "ince telli",
                   "servo-uzatma": "ince telli", "hazir": None, "motor-kablosu": None}
# AWG → mm² (AWG tanımı, iki basamak): kesit.mm2 bu tablodan, kesit_kurali.tablo da
AWG_MM2 = {12: 3.31, 16: 1.31, 18: 0.82, 20: 0.52, 22: 0.33, 24: 0.2}
HAT_YUVASI_KUYRUK_AWG = 16   # kalem 85 'Su Geçirmez Mini/Micro Bıçak Sigorta Yuvası - 16AWG': ara_uc tarafında iletken yuva kuyruğu
# istisna adı → (karar kodu, sabit üye listesi). Üye eklemek / çıkarmak yeni karar ister (kablolama-on-kararlar.md, günlük)
ISTISNA_KARARI = {
    "servo-uzatmasi": ("O-2", {f"S{i:02d}" for i in range(1, 11)}),
    "ana-hat-12awg": ("O-15", {"G01", "G02", "G03", "G04", "G05"}),
    "motor-fabrika-kablosu": ("O-16", {"M01", "M02", "M03", "M04"}),
    "kafa-5v-donusturucu-arkasi": ("O-21", {"K03", "K04", "K05"}),
    "servo-ana-hat-16awg": ("O-20", {"SV1", "SV2", "SV3"}),
}
# istisna adı → {koruyucu: en ince izinli AWG} (kararın metni: O-2 22 AWG hobi servo kablosu; O-15 12 AWG; O-16 18 AWG'den
# inceyse orkestratöre; düzeltme turu 1 madde 5 18 AWG, O-21 hazır micro USB 24 AWG'den ince olamaz; O-20 c 16 AWG)
ISTISNA_KESITI = {
    "servo-uzatmasi": {"XL4016-A": 22, "XL4016-B": 22, "XL4016-C": 22},
    "ana-hat-12awg": {"aku-bms": 12, "ana-sigorta": 12},
    "motor-fabrika-kablosu": {"BTS7960-sol": 18, "BTS7960-sag": 18},
    "kafa-5v-donusturucu-arkasi": {"D24V50F5": 18, "SY8205": 24},
    "servo-ana-hat-16awg": {"XL4016-A": 16, "XL4016-B": 16, "XL4016-C": 16},
}
# parça → güç ucunun türü (uç türü serbestçe 'lehim' yazılıp sınırı bilinmeyen uç teyidinden kaçılmasın)
PARCA_UC_TURU = {"Sigorta kutusu": "sigorta-kutusu", "Akü": "pabuc", "Ana anahtar": "pabuc", "BTS7960 sol": "bts-guc",
                 "BTS7960 sağ": "bts-guc", "XL4016 A": "modul-vidali", "XL4016 B": "modul-vidali", "XL4016 C": "modul-vidali",
                 "XL4016 çevre": "modul-vidali"}
# koruyucu → elektrik.md "Sigorta listesi" satırı (Yer, alt anahtar); yükü olmayan satır
SIGORTA_LISTESI = {"ana-sigorta": ("Ana", None), "F1": ("F1", None), "F3": ("F3", None), "F4": ("F4", None), "F5": ("F5", None),
                   "F6": ("F6", None), "hat-A": ("Hat", "A"), "hat-B": ("Hat", "B"), "hat-C": ("Hat", "C"),
                   "hat-G22": ("Hat", "G22"), "hat-cevre": ("Hat", "çevre"), "hat-sarj": ("Şarj", None)}
SIGORTA_LISTESI_YUKSUZ = {"F2"}
# sigorta olmayan koruyucuların belge sayısı: (dosya, satır kalıbı, sayı kalıbı)
BELGE_SAYISI = {
    "aku-bms": ("elektrik", r"^Akü Victron SuperPack", r"BMS (\d+) A sürekli"),
    **{k: ("elektrik", r"XL4016'nın kendi akım sınırına", r"çipin anahtar akımı sınırı \*\*" + SAYI + r" A tipik")
       for k in ("XL4016-A", "XL4016-B", "XL4016-C", "XL4016-cevre")},
}
BELGESIZ = {"D24V50F5", "SY8205", "BTS7960-sol", "BTS7960-sag"}   # akım sınırı belgede sayı değil: tabloda None olmalı
# kablolama-on-kararlar.md karar satırları: koruyucu → (satır kalıbı, sayı kalıbı)
KARAR_SATIRI = {
    "F6": (r"^\| K11 \|", r"F6 " + SAYI + " A"),
    "F5": (r"^\| KT3 \|", r"F5 yuvasında " + SAYI + " A standart"),
    "hat-G22": (r"^\| Hat sigortası yuvası / 2 A mini \|", r"O-18 b: G22'nin bara ucunda " + SAYI + " A"),
    "hat-cevre": (r"^\| Hat sigortası yuvası / 2 A mini \|", r"O-19 a: XL4016 çevre çıkışında " + SAYI + " A"),
    "hat-sarj": (r"^\s+şarj kolu:", r"düzeltme turu 1'de \*\*" + SAYI + r" A mini"),
}
# blok şemasındaki öğe → eleman: (öğe kalıbı, ardındaki öğenin kalıbı ya da None). Her eleman şemada tam bir öğeyle eşleşir;
# girişi, şemada kendisinden önce gelen ilk eşlenmiş öğenin çıkışıdır (ek tur, üçüncü bakış D-C)
SAYI_A = r"^\d+(?:,\d+)? A"
DIYAGRAM = {
    "aku-bms": (r"^Akü Victron", None), "ana-sigorta": (r"^Ana sigorta \d", None), "ana-anahtar": (r"ana anahtar$", None),
    **{f"F{i}": (rf"^F{i} \d", None) for i in (1, 3, 4, 5, 6)},
    "K1-kontak": (r"röle K1 kontağı", None), "K2-kontak": (r"K2 ön şarj kolu", None), "mantar": (r"^mantar NC", None),
    "K1-bobin": (r"röle K1 bobini", None), "K2-bobin": (r"K2 bobini", None),
    "hat-A": (SAYI_A + "$", r"^XL4016 A\b"), "hat-B": (SAYI_A + "$", r"^XL4016 B\b"), "hat-C": (SAYI_A + "$", r"^XL4016 C\b"),
    "hat-G22": (SAYI_A + " mini", r"^PC817 #2"), "hat-cevre": (SAYI_A + " mini", r"^ESP32 VIN"), "hat-sarj": (SAYI_A + " mini", r"^XT60E-M"),
    "XL4016-A": (r"^XL4016 A\b", None), "XL4016-B": (r"^XL4016 B\b", None), "XL4016-C": (r"^XL4016 C\b", None),
    "XL4016-cevre": (r"^XL4016 çevre", None), "D24V50F5": (r"^D24V50F5", None), "SY8205": (r"^SY8205", None),
    "gogus-regulatoru": (r"^LM2577 \+ LM2596", None), "BTS7960-sol": (r"^BTS7960 sol", None), "BTS7960-sag": (r"^BTS7960 sağ", None),
    "R-aku-olcum": (r"akü ADC bölücü", None),
}
DIYAGRAM_DISI = {"esp32-3v3": "ESP32 kartının kendi 3V3 regülatörü (şemada 'enkoder (3V3 ESP32'den)', ayrı öğe değil)"}
YON = ("tablo ↔ elektrik.md blok şeması uyuşmuyor; şema doğruysa tabloyu, tablo doğruysa önce şemayı ve karar kaydını düzelt "
       "(denetimin 'devreden' dediği, tablonun kendi koruyucular / anahtarlar / düğümler alanlarıdır)")
# adından güç ucu olduğu belli düğümler (nokta kısmı); bunların ağı yazılı olmalı
GUC_ADI = re.compile(r"^(V\+|VIN|VCC.*|.*VBUS|\+|−|GND.*|3V3|\+12 V|(.* )?5 V|OUT[+−].*|IN[+−]|B[+−]|M[+−]|.* V\+|"
                     r".* GND( \(.*\))?|.*VCC|IN\d [+−]|.*jak [+−]|motor [+−]|L[+−]|[+−] kutup.*|K2 bobini [+−]|8[5-7]|30)$")
DUR_SOZ = {"kartı", "kart", "giriş", "girişi", "çıkış", "çıkışı", "kablo", "kablosu", "için", "ile", "güç", "hat", "hattı",
           "dal", "dalı", "tarafı", "modülü", "the", "and", "uç", "ucu", "sol", "sağ", "orta", "arka", "ön", "servosu",
           # genel sözcükler (düzeltme turu 2): her satırda geçebilir, ayırt edici sayılmaz
           "sigorta", "sigortası", "sigortaları", "kutusu", "kutu", "kablolar", "gnd", "toprak", "bara", "barası", "baraları",
           "yıldız", "akü", "ana", "anahtar", "anahtarı", "anahtarlı", "mini", "standart", "awg", "klemens", "klemensi", "vidalı",
           "noktası", "nokta", "düğüm", "düğümü", "besleme", "dönüş", "dönüşü", "yolu", "yollu", "sinyal", "başlık", "başlığı",
           "kesit", "kesiti", "json", "kablolar.json", "elektrik", "planlama", "adim3"}


class KaynakYok(Exception):
    pass


# ---------------------------------------------------------------- kaynaklar
def pin_json(metin):
    m = re.search(r"## 9\..*?```json\s*\n(.*?)\n```", metin, re.S)
    if not m:
        raise KaynakYok("pin-haritasi.md §9 JSON bloğu bulunamadı")
    try:
        return json.loads(m.group(1))
    except ValueError as h:
        raise KaynakYok(f"pin-haritasi.md §9 JSON okunamadı: {h}")


def kanallar_yaml(metin):
    k = {}
    for ad, kanal in re.findall(r"^\s+(\w+):\s*\{\s*kanal:\s*(\d+)", metin, re.M):
        k[ad] = int(kanal)
    if not k:
        raise KaynakYok("kanallar.yaml'da kanal satırı bulunamadı")
    return k


def kaynaklari_oku(a):
    try:
        veri = json.loads(Path(a.tablo).read_text(encoding="utf-8"))
        pin = pin_json(PIN.read_text(encoding="utf-8"))
        p12 = KOK_BELGE.read_text(encoding="utf-8")
        if a.kanallar:
            yaml = Path(a.kanallar).read_text(encoding="utf-8")
        else:
            c = subprocess.run(["git", "-C", str(KOK), "show", KANALLAR_MAIN], capture_output=True)
            if c.returncode != 0:
                raise KaynakYok(f"git show {KANALLAR_MAIN} başarısız: {c.stderr.decode('utf-8', 'replace').strip()}")
            yaml = c.stdout.decode("utf-8")
        gor = Path(a.gorunum).read_text(encoding="utf-8") if Path(a.gorunum).exists() else None
        maliyet = json.loads(MALIYET.read_text(encoding="utf-8"))
        elektrik = (BURASI / "elektrik.md").read_text(encoding="utf-8")
        parcalar = json.loads((KOK / MONTAJ).read_text(encoding="utf-8"))["parcalar"]
    except OSError as h:
        raise KaynakYok(str(h))
    except ValueError as h:
        raise KaynakYok(f"kablolar.json okunamadı: {h}")
    return {"veri": veri, "pin": pin, "kanallar": kanallar_yaml(yaml), "p12": p12, "gorunum": gor, "maliyet": maliyet,
            "parcalar": parcalar, "elektrik": elektrik}


# ---------------------------------------------------------------- devre modeli (ağlar, elemanlar, zincir)
def elemanlar(v):
    e = dict(v.get("koruyucular", {}))
    e.update(v.get("anahtarlar", {}))
    return e


def dugum_agi(v, u):
    d = v["dugumler"].get(u)
    return d.get("ag") if d else None


def tel_agi(v, d):
    """Telin ağı: arada kayıtlı eleman varsa onun çıkışı (ara ucun karşısındaki düğümün ağı), yoksa a ucunun ağı."""
    if d.get("ara_koruyucu"):
        e = v["koruyucular"].get(d["ara_koruyucu"])
        if not e:
            return None
        ote = d["b"] if d.get("ara_uc") == "a" else d["a"]
        n = dugum_agi(v, ote)
        return n if n in e["cikis"] else e["cikis"][0]
    return dugum_agi(v, d["a"])


def kutup(v, net):
    return v["aglar"].get(net, {}).get("kutup") if net else None


def besleyenler(v, net):
    return sorted(k for k, e in elemanlar(v).items() if net in e["cikis"])


def zincir(v, net, gorulen=()):
    """Aküden ağa eleman listesi (paralel besleyenler liste içinde liste). Kurulamazsa ValueError."""
    if net in gorulen:
        raise ValueError(f"döngü: {net}")
    f = besleyenler(v, net)
    if not f:
        raise ValueError(f"ağın beslemesi yok: {net}")
    E = elemanlar(v)
    girisler = {E[k]["giris"] for k in f}
    if len(girisler) != 1:
        raise ValueError(f"ağ {net}: paralel besleyenlerin girişleri farklı {sorted(map(str, girisler))}")
    g = girisler.pop()
    ust = [] if g is None else zincir(v, g, gorulen + (net,))
    return ust + [f[0] if len(f) == 1 else f]


def duz(z):
    for x in z:
        yield from (x if isinstance(x, list) else [x])


def sinirlayan(v, net):
    """Ağdan aküye doğru ilk akım sınırlayan eleman (koruyucular tablosu); anahtar / geçiş elemanları atlanır."""
    for x in reversed(zincir(v, net)):
        ids = x if isinstance(x, list) else [x]
        k = [i for i in ids if i in v["koruyucular"]]
        if k:
            return max(k, key=lambda i: math.inf if v["koruyucular"][i]["akim_a"] is None else v["koruyucular"][i]["akim_a"])
    return None


def akim(v, kid):
    a = v["koruyucular"][kid]["akim_a"]
    return math.inf if a is None else a


def guc_damarlari(v, r):
    """[(damar, tel ağı, koruyan kimliği)]: akım taşıyan + / − / ± damarlar ve koruyanları (yapıdan)."""
    yildiz = v["yildiz_noktasi"]
    kok = [k for k, e in v["koruyucular"].items() if e["giris"] is None]
    l, gnd = [], []
    for d in r["damarlar"]:
        n = tel_agi(v, d)
        if kutup(v, n) not in GUC_KUTUP:
            continue
        if n == "GND":
            gnd.append(d)
            continue
        k = d["ara_koruyucu"] if d.get("ara_koruyucu") else sinirlayan(v, n)
        l.append((d, n, k))
    if gnd:
        if l:
            k = max((x[2] for x in l), key=lambda i: akim(v, i))
            l += [(d, "GND", k) for d in gnd]
        elif any(u in (yildiz, "Akü · − kutup (M5)") for d in gnd for u in (d["a"], d["b"])) and kok:
            l += [(d, "GND", kok[0]) for d in gnd]      # ana dönüş: aküye kadar her şeyin akımı
    return l


def kablo_zinciri(v, r):
    g = guc_damarlari(v, r)
    ng = [n for _, n, _ in g if n != "GND"]
    if ng:
        zz = [zincir(v, n) for n in ng]
        p = []
        for xs in zip(*zz):
            if all(x == xs[0] for x in xs):
                p.append(xs[0])
            else:
                break
        return p
    if g:
        return [g[0][2]]
    for d in r["damarlar"]:
        for u in (d["a"], d["b"]):
            pb = v["parca_beslemesi"].get(v["dugumler"].get(u, {}).get("parca"))
            if pb:
                return zincir(v, pb)
    raise ValueError("güç damarı yok ve uçlardaki parçaların beslemesi parca_beslemesi'nde yok")


def zincir_enerjili(v, z):
    E, kes = elemanlar(v), set(v["zinciri_kesen_turler"])
    for x in z:
        ids = x if isinstance(x, list) else [x]
        if all(E[i]["tur"] in kes for i in ids):
            return False
    return True


def zincir_dali(v, z):
    tanim = {d["eleman"]: ad for ad, d in v["dallar"].items()}
    dal = None
    for x in z:
        for i in (x if isinstance(x, list) else [x]):
            if i in tanim:
                dal = tanim[i]
    return dal


# ---------------------------------------------------------------- sınamalar
def s_alanlar(v, b):
    h = []
    kim = Counter(r.get("kimlik") for r in v["kablolar"])
    h += [f"kimlik iki kez: {k}" for k, n in kim.items() if n > 1]
    for r in v["kablolar"]:
        eks = [z for z in ZORUNLU if z not in r]
        if eks:
            h.append(f"{r.get('kimlik')}: eksik alan {eks}")
            continue
        if r["durum"] not in DURUMLAR:
            h.append(f"{r['kimlik']}: durum '{r['durum']}' tanımsız")
        bekl = "karara bağlı" if r["eksik"] else ("kablajda teyit edilecek" if r["teyit"] else "kesin")
        if r["durum"] != bekl:
            h.append(f"{r['kimlik']}: durum '{r['durum']}', eksik / teyit listesine göre '{bekl}' olmalı")
        if r["demet"] not in v["demet_sirasi"]:
            h.append(f"{r['kimlik']}: demet '{r['demet']}' demet_sirasi'nda yok")
        if r["devre"] not in v["devre_turleri"]:
            h.append(f"{r['kimlik']}: devre türü '{r['devre']}' izinli listede (devre_turleri) yok")
        if r["dal"] not in v["dallar"]:
            h.append(f"{r['kimlik']}: dal '{r['dal']}' dallar tablosunda yok")
        if r["koruma"] is not None and r["koruma"] not in v["koruyucular"]:
            h.append(f"{r['kimlik']}: koruma '{r['koruma']}' koruyucular tablosunda yok")
        if r.get("bolge") and r["bolge"] not in v["kesit_kurali"]["ortam"]["bolgeler"]:
            h.append(f"{r['kimlik']}: bölge '{r['bolge']}' tanımsız")
        if r["boy"] is None and not r.get("boy_not"):
            h.append(f"{r['kimlik']}: boy yok ve boy_not yok")
        fazla = sorted(set(r) - ALAN_KABLO)
        if fazla:
            h.append(f"{r['kimlik']}: tanımsız alan {fazla} (denetim okumaz; eski alan adı mı?)")
        for d in r["damarlar"]:
            fazla = sorted(set(d) - ALAN_DAMAR)
            if fazla:
                h.append(f"{r['kimlik']}/{d.get('ad')}: damarda tanımsız alan {fazla}")
        # kayıt düzeyi uç parçası, o yandaki damar uçlarından birinin parçasıyla tutarlı (B5c)
        for u, yan in (("uc_a", "a"), ("uc_b", "b")):
            p = str(r[u].get("parca", "")).casefold()
            parcalar = {str(v["dugumler"].get(d[yan], {}).get("parca", "")).casefold() for d in r["damarlar"]}
            nokta = str(r[u].get("nokta", "")).casefold()
            if p and not any(x and (x in p or p in x or x.split()[0][:5] == p.split()[0][:5] or x.split()[0] in nokta)
                             for x in parcalar):
                h.append(f"{r['kimlik']}: {u}.parca '{r[u].get('parca')}' damar uçlarının parçalarından hiçbiriyle tutmuyor")
        # kesit: mm² AWG'den (sabit tablo)
        kesitler = [("kesit", r.get("kesit"))] + [(f"{d['ad']} kesit", d.get("kesit")) for d in r["damarlar"]] + [
            (f"{d['ad']} uç kuyruğu {y}", x) for d in r["damarlar"] for y, x in (d.get("uc_kuyrugu") or {}).items()]
        for ne, k in kesitler:
            if isinstance(k, dict) and k.get("awg") is not None:
                if k["awg"] not in AWG_MM2 or abs((k.get("mm2") or 0) - AWG_MM2[k["awg"]]) > 0.005:
                    h.append(f"{r['kimlik']}: {ne} {k['awg']} AWG ↔ {k.get('mm2')} mm²; AWG tablosunda {AWG_MM2.get(k['awg'])} mm²")
    for t in v["kesit_kurali"]["tablo"]:
        if abs(t["mm2"] - AWG_MM2.get(t["awg"], -1)) > 0.005:
            h.append(f"kesit_kurali.tablo {t['awg']} AWG ↔ {t['mm2']} mm²; AWG tablosunda {AWG_MM2.get(t['awg'])}")
    return h


def s_iki_uc(v, b):
    h = []
    for r in v["kablolar"]:
        for u in ("uc_a", "uc_b"):
            x = r.get(u) or {}
            if not str(x.get("parca", "")).strip() or not str(x.get("nokta", "")).strip():
                h.append(f"{r['kimlik']}: {u} boş")
        if not r.get("damarlar"):
            h.append(f"{r['kimlik']}: damar yok")
        for d in r.get("damarlar", []):
            if not str(d.get("a", "")).strip() or not str(d.get("b", "")).strip():
                h.append(f"{r['kimlik']}: damar '{d.get('ad')}' ucu boş")
    return h


def s_yer_tutucu(v, b):
    """Her kayıtta uç alanları (uc_a / uc_b, damar uçları, damar adı) yer tutucusuz; kesin kayıtta sonlandırma ve damar notları da."""
    h = []
    for r in v["kablolar"]:
        alanlar = [("uc_a", r["uc_a"].get("parca", "")), ("uc_a", r["uc_a"].get("nokta", "")),
                   ("uc_b", r["uc_b"].get("parca", "")), ("uc_b", r["uc_b"].get("nokta", ""))]
        for d in r["damarlar"]:
            alanlar += [(f"damar '{d['ad']}'", d["a"]), (f"damar '{d['ad']}'", d["b"]), (f"damar '{d['ad']}' ad", d["ad"])]
        if r["durum"] == "kesin":
            alanlar.append(("sonlandirma", r["sonlandirma"]))
            for d in r["damarlar"]:
                alanlar += [(f"damar '{d['ad']}' {k}", x) for k, x in d.items() if k in ("ara", "not") and isinstance(x, str)]
        for ad, x in alanlar:
            m = YER_TUTUCU.search(str(x))
            if m:
                h.append(f"{r['kimlik']} ({r['durum']}): {ad} yer tutucu içeriyor '{m.group(0).strip() or 'boş'}': {str(x)[:70]} "
                         "(eksik bilgi eksik / teyit alanına)")
    return h


def bolum(metin, baslik):
    m = re.search(r"^## " + re.escape(baslik) + r"\s*\n(.*?)(?=^## |\Z)", metin, re.S | re.M)
    return m.group(1) if m else None


def sigorta_listesi(el):
    """elektrik.md 'Sigorta listesi': {(Yer, alt anahtar): (akım, biçim)}, hatalar. Tek tablo; Değer hücresi 'N A standart|mini'
    (parantez içi tarihçe atılır), Hat satırı 'mini: A 7,5 A · B …'."""
    s = bolum(el, "Sigorta listesi")
    if s is None:
        return {}, ["elektrik.md'de '## Sigorta listesi' bölümü yok"]
    satir = s.splitlines()
    tablolar, simdi = [], None
    for x in satir:
        if x.startswith("|"):
            if simdi is None:
                simdi = []
                tablolar.append(simdi)
            simdi.append(x)
        else:
            simdi = None
    if len(tablolar) != 1:
        return {}, [f"Sigorta listesi bölümünde {len(tablolar)} tablo var; ayrıştırılabilir tek tablo olmalı"]
    t, h = {}, []
    for x in tablolar[0][2:]:
        c = [y.strip() for y in x.strip().strip("|").split("|")]
        yer, deger = c[0], c[1].replace("**", "")
        while re.search(r"\([^()]*\)", deger):
            deger = re.sub(r"\([^()]*\)", "", deger)
        deger = " ".join(deger.split())
        if yer == "Hat":
            m = re.match(r"^mini:\s*(.*)$", deger)
            if not m:
                h.append(f"Sigorta listesi Hat satırı 'mini: A … · B …' biçiminde değil: '{c[1][:60]}'")
                continue
            for parca in m.group(1).split("·"):
                mm = re.match(r"^\s*(\w+) (.*)$", parca)
                sayilar = re.findall(SAYI + " A", mm.group(2)) if mm else []
                if len(sayilar) != 1:
                    h.append(f"Sigorta listesi Hat satırında '{parca.strip()}' {len(sayilar)} akım değeri (bir olmalı)")
                    continue
                t[(yer, mm.group(1))] = (tr_sayi(sayilar[0]), "mini")
            continue
        if len(re.findall(SAYI + " A", deger)) != 1:
            h.append(f"Sigorta listesi '{yer}' satırının Değer hücresinde {len(re.findall(SAYI + ' A', deger))} akım değeri: "
                     f"'{c[1][:60]}' (bir olmalı; tarihçe parantez içinde)")
            continue
        m = re.match(r"^" + SAYI + r" A (standart|mini)\b", deger)
        if not m:
            h.append(f"Sigorta listesi '{yer}' satırının Değer hücresi 'N A standart|mini' değil: '{c[1][:60]}' (sayı okunamadı)")
            continue
        t[(yer, None)] = (tr_sayi(m.group(1)), m.group(2))
    return t, h


def satir_sayisi(metin, satir_kalibi, sayi_kalibi):
    """Kalıba uyan tek satırdaki tek sayı -> (sayı, None) ya da (None, hata)."""
    sat = [x for x in metin.splitlines() if re.search(satir_kalibi, x)]
    if len(sat) != 1:
        return None, f"'{satir_kalibi}' kalıbına uyan {len(sat)} satır (bir olmalı)"
    m = re.findall(sayi_kalibi, sat[0])
    if len(m) != 1:
        return None, f"'{sayi_kalibi}' satırda {len(m)} kez (bir olmalı): {sat[0][:80]}"
    return tr_sayi(m[0] if isinstance(m[0], str) else m[0][0]), None


def blok_sema(el):
    """Blok şemasının sigorta blokları: {F<n>: (akım, blok metni)}, kutu girişi metni, hatalar."""
    s = bolum(el, "Blok şema (metin)")
    m = re.search(r"```\n(.*?)```", s or "", re.S)
    if not m:
        return {}, "", ["elektrik.md blok şeması (```) bulunamadı"]
    sat = m.group(1).splitlines()
    idx = [(i, mm) for i, x in enumerate(sat) for mm in [re.search(r"[├└]─ (F\d) " + SAYI + r" A ──", x)] if mm]
    son = next((i for i, x in enumerate(sat) if re.match(r"^(Veri|Toprak):", x)), len(sat))
    bloklar = {}
    for j, (i, mm) in enumerate(idx):
        bit = idx[j + 1][0] if j + 1 < len(idx) else son
        bloklar[mm.group(1)] = (tr_sayi(mm.group(2)), "\n".join(sat[i:bit]))
    return bloklar, sat[0] if sat else "", ([] if bloklar else ["blok şemasında sigorta satırı yok"])


def blok_agaci(el):
    """elektrik.md blok şeması → (öğeler [(metin, üst öğe sırası ya da None)], hatalar). Her satırdaki '├─' / '└─' bir kol başlatır;
    kol '──' ile öğelere bölünür ('─┬─' kolun içinde dallanma: alttaki aynı sütunlu kol ┬'den önceki öğeden çıkar). Kolun üstü:
    yukarı doğru ilk kardeş kolun (aynı sütun ±1) üstü ya da sütunu küçük ilk kolun son öğesi (┬ sütunundaysa ┬ öncesi); ilk satır
    kök. '(X sonrası)' ile başlayan kol kökteki X öğesinden çıkar."""
    s = bolum(el, "Blok şema (metin)")
    m = re.search(r"```\n(.*?)```", s or "", re.S)
    if not m:
        return [], ["elektrik.md blok şeması (```) bulunamadı"]
    sat = m.group(1).splitlines()
    son = next((i for i, x in enumerate(sat) if re.match(r"^(Veri|Toprak):", x)), len(sat))
    sat = sat[:son]
    if not sat:
        return [], ["blok şeması boş"]
    ogeler, kollar, hatalar = [], [], []   # kollar: (satır, sütun, öğe sıraları, {┬ sütunu: ┬ öncesi öğe sırası}, açık üst)
    AYRAC = re.compile(r"\s*─┬─\s*|\s*─{2,}\s*")

    def bol(metin, bas):
        idx, capa, pos = [], {}, 0
        for mm in list(AYRAC.finditer(metin)) + [None]:
            parca = metin[pos:mm.start() if mm else len(metin)].strip(" │")
            if parca:
                ogeler.append([parca, None])
                idx.append(len(ogeler) - 1)
            if mm is None:
                break
            if "┬" in mm.group(0) and idx:
                capa[bas + mm.start() + mm.group(0).index("┬")] = idx[-1]
            pos = mm.end()
        for a_, b_ in zip(idx, idx[1:]):
            ogeler[b_][1] = a_
        return idx, capa

    kok_idx, kok_capa = bol(sat[0], 0)
    kollar.append((0, -1, kok_idx, kok_capa, False))
    for i, x in enumerate(sat[1:], 1):
        isaret = [mm.start() for mm in re.finditer(r"[├└]─", x)]
        for j, c in enumerate(isaret):
            metin = x[c + 2:isaret[j + 1] if j + 1 < len(isaret) else len(x)]
            idx, capa = bol(metin, c + 2)
            if not idx:
                hatalar.append(f"blok şeması satır {i + 1}, sütun {c}: kolda öğe yok")
                continue
            ust, acik = None, False
            ma = re.match(r"^\((.+?) sonrası\)\s*", ogeler[idx[0]][0])
            if ma:
                acik = True
                ogeler[idx[0]][0] = ogeler[idx[0]][0][ma.end():]
                aday = [k for k in kok_idx if ma.group(1).casefold() in ogeler[k][0].casefold()]
                if len(aday) != 1:
                    hatalar.append(f"blok şeması: '({ma.group(1)} sonrası)' kökte {len(aday)} öğeyle eşleşti (bir olmalı)")
                else:
                    ust = aday[0]
            else:
                bulundu = False
                for (si, sc, sidx, scapa, sacik) in reversed(kollar):
                    if si >= i:
                        continue
                    if abs(sc - c) <= 1 and si > 0:
                        ust, bulundu = ogeler[sidx[0]][1], True
                        break
                    if sc < c - 1 and not sacik:
                        yak = [k for col, k in scapa.items() if abs(col - c) <= 1]
                        ust, bulundu = (yak[0] if yak else sidx[-1]), True
                        break
                if not bulundu:
                    hatalar.append(f"blok şeması satır {i + 1}, sütun {c}: kolun üstü bulunamadı")
            ogeler[idx[0]][1] = ust
            kollar.append((i, c, idx, capa, acik))
    return [(o[0], o[1]) for o in ogeler], hatalar


def blok_karsilastir(v, el):
    """Tablodaki her koruyucu / anahtar blok şemasında tek öğeyle eşleşir; girişi, şemada önündeki ilk eşlenmiş öğenin çıkışı."""
    h = []
    og, hb = blok_agaci(el)
    if hb or not og:
        return (hb or ["blok şeması ayrıştırılamadı"]) + [YON]
    E = elemanlar(v)
    esle = {}
    for kid in E:
        if kid in DIYAGRAM_DISI:
            continue
        if kid not in DIYAGRAM:
            h.append(f"eleman {kid}: elektrik.md blok şemasında karşılığı tanımlı değil (DIYAGRAM); her eleman şemadan sınanır")
            continue
        kal, sonraki = DIYAGRAM[kid]
        aday = [i for i, (t, _) in enumerate(og) if re.search(kal, t)
                and (sonraki is None or any(u == i and re.search(sonraki, tt) for tt, u in og))]
        if len(aday) != 1:
            h.append(f"eleman {kid}: blok şemasında '{kal}'" + (f" (ardında '{sonraki}')" if sonraki else "")
                     + f" kalıbına uyan {len(aday)} öğe (bir olmalı). {YON}")
            continue
        esle[kid] = aday[0]
    ters = {}
    for kid, i in esle.items():
        ters.setdefault(i, []).append(kid)
    for kid, i in sorted(esle.items()):
        e = E[kid]
        t = og[i][0]
        mm = re.match(SAYI_A, t)
        if mm and kid in v["koruyucular"] and v["koruyucular"][kid]["akim_a"] != tr_sayi(mm.group(0)[:-2]):
            h.append(f"eleman {kid}: tabloda {v['koruyucular'][kid]['akim_a']} A, blok şemasında '{t}'. {YON}")
        u = og[i][1]
        while u is not None and u not in ters:
            u = og[u][1]
        if u is None:
            bek, ne = {None}, "kök"
        else:
            bek = {(E[k]["cikis"] or [None])[0] for k in ters[u]}
            ne = f"'{og[u][0][:40]}' ({', '.join(ters[u])})"
        if e.get("giris") not in bek:
            h.append(f"eleman {kid}: tabloda girişi '{e.get('giris')}', elektrik.md blok şemasında {ne} arkasında "
                     f"(beklenen giriş {sorted(map(str, bek))}). {YON}")
    for i, (t, _) in enumerate(og):
        if re.match(SAYI_A + r"(?: mini)?\b", t) and i not in ters:
            h.append(f"blok şemasındaki sigorta öğesi '{t[:40]}' tablodaki hiçbir koruyucuya eşlenmedi")
    return h


def amper(model):
    return [tr_sayi(x.replace(".", ",")) for x in re.findall(r"(\d+(?:[.,]\d+)?) ?A(?:mper)?\b", model)]


def set_coklu(el):
    m = re.search(r"kutudaki set ([0-9 ,×]+?) \(standart", el)
    if not m:
        return None
    c = Counter()
    for p in m.group(1).split(","):
        p = p.strip()
        mm = re.match(r"^(?:(\d+) × )?(\d+)$", p)
        if mm:
            c[float(mm.group(2))] += int(mm.group(1) or 1)
    return c


def s_koruyucu(v, b):
    h = []
    el, kok, kal = b["elektrik"], b["p12"], b["maliyet"]["kalemler"]
    liste, hl = sigorta_listesi(el)
    h += hl
    bloklar, ilk, hb = blok_sema(el)
    h += hb
    kullanilan = set()
    setten = Counter()
    eslesen = set(SIGORTA_LISTESI.values())
    for kid, e in v["koruyucular"].items():
        a = e["akim_a"]
        # adındaki sayılar
        for n in re.findall(r"(?<![\w,.])" + SAYI + r" A\b", e.get("ad", "")):
            if a is None or abs(tr_sayi(n) - a) > 1e-9:
                h.append(f"koruyucu {kid}: adı '{e['ad']}' {n} A diyor, akim_a {a}")
        if e["tur"] == "sigorta":
            if kid not in SIGORTA_LISTESI:
                h.append(f"koruyucu {kid}: elektrik.md sigorta listesinde karşılığı tanımlı değil (SIGORTA_LISTESI)")
                continue
            anahtar = SIGORTA_LISTESI[kid]
            kullanilan.add(anahtar[0])
            if anahtar not in liste:
                h.append(f"koruyucu {kid}: sigorta listesinde '{anahtar[0]}{' ' + anahtar[1] if anahtar[1] else ''}' sayısı okunamadı")
            else:
                la, lb = liste[anahtar]
                if a != la:
                    h.append(f"koruyucu {kid}: tabloda {a} A, elektrik.md sigorta listesinde {la:g} A")
                if e.get("bicak") != lb:
                    h.append(f"koruyucu {kid}: biçim '{e.get('bicak')}', sigorta listesinde '{lb}'")
            if kid in bloklar or re.match(r"F\d$", kid):
                if kid not in bloklar:
                    h.append(f"koruyucu {kid}: elektrik.md blok şemasında '├─ {kid} N A ──' satırı yok")
                elif bloklar[kid][0] != a:
                    h.append(f"koruyucu {kid}: tabloda {a} A, blok şemasında {bloklar[kid][0]:g} A")
            if kid == "ana-sigorta":
                m = re.findall(r"Ana sigorta " + SAYI + " A", ilk)
                if len(m) != 1 or tr_sayi(m[0]) != a:
                    h.append(f"koruyucu {kid}: tabloda {a} A, blok şemasının ilk satırında {m}")
            if kid in KARAR_SATIRI:
                n, x = satir_sayisi(kok, *KARAR_SATIRI[kid])
                if x:
                    h.append(f"koruyucu {kid}: kablolama-on-kararlar.md karar satırı: {x}")
                elif n != a:
                    h.append(f"koruyucu {kid}: tabloda {a} A, kablolama-on-kararlar.md karar satırında {n:g} A")
            # sipariş satırı
            s = e.get("siparis")
            if s == "set":
                if e.get("bicak") != "standart":
                    h.append(f"koruyucu {kid}: setten (standart) ama biçim '{e.get('bicak')}'")
                setten[a] += 1
            elif isinstance(s, int) and 0 <= s < len(kal):
                k = kal[s]
                am = amper(k["model"])
                if am != [a]:
                    h.append(f"koruyucu {kid}: maliyet.json kalem {s} ({k['model']}) amper {am}, tabloda {a} A")
                if ("mini" in k["model"].casefold()) != (e.get("bicak") == "mini"):
                    h.append(f"koruyucu {kid}: maliyet.json kalem {s} modeli '{k['model']}', biçim '{e.get('bicak')}'")
                if k.get("ver") and "v3" not in k["ver"].split(","):
                    h.append(f"koruyucu {kid}: sipariş satırı kalem {s} V3 listesinde değil")
            else:
                h.append(f"koruyucu {kid}: siparis alanı (maliyet.json kalemi ya da 'set') yok / geçersiz: {s!r}")
        elif kid in BELGE_SAYISI:
            dosya, sk, nk = BELGE_SAYISI[kid]
            n, x = satir_sayisi(el, sk, nk)
            if x:
                h.append(f"koruyucu {kid}: elektrik.md: {x}")
            elif n != a:
                h.append(f"koruyucu {kid}: tabloda {a} A, elektrik.md'de {n:g} A")
            s = e.get("siparis")
            if not isinstance(s, int) or not 0 <= s < len(kal):
                h.append(f"koruyucu {kid}: siparis kalemi yok / geçersiz: {s!r}")
            else:
                mod = kal[s]["model"]
                if e["tur"] == "bms":
                    m = re.findall(r"BMS (\d+) A", mod)
                    if not m or float(m[0]) != a:
                        h.append(f"koruyucu {kid}: maliyet.json kalem {s} ({mod[:60]}) BMS {m}, tabloda {a} A")
                else:
                    an = re.findall(SAYI + " A", e.get("anma", ""))
                    if amper(mod) != [tr_sayi(an[0])] if an else True:
                        h.append(f"koruyucu {kid}: maliyet.json kalem {s} ({mod[:60]}) amper {amper(mod)}, anma '{e.get('anma')}'")
        elif kid in BELGESIZ:
            if a is not None:
                h.append(f"koruyucu {kid}: akım sınırı belgelerde sayı olarak yok ama tabloda {a} A (kaynağı olmayan sayı)")
            if not e.get("sinir_kaynagi"):
                h.append(f"koruyucu {kid}: sinir_kaynagi yok")
        elif e["tur"] == "direnc":
            sat = [x for x in el.splitlines() if x.startswith("| Akü gerilimi |")]
            mm = re.search(r"(\d+) kΩ", sat[0]) if len(sat) == 1 else None
            vv = re.search(SAYI + r" V →", sat[0]) if len(sat) == 1 else None
            if not (mm and vv):
                h.append(f"koruyucu {kid}: elektrik.md 'Akü gerilimi' satırından direnç / gerilim okunamadı")
            else:
                i = tr_sayi(vv.group(1)) / (int(mm.group(1)) * 1000)
                if a is None or abs(a - i) > 0.05 * i:
                    h.append(f"koruyucu {kid}: tabloda {a} A, elektrik.md'den {vv.group(1)} V / {mm.group(1)} kΩ = {i:.6f} A")
        else:
            h.append(f"koruyucu {kid}: bağımsız kaynağı tanımlı değil (SIGORTA_LISTESI / BELGE_SAYISI / BELGESIZ)")
    tablodaki = {SIGORTA_LISTESI[k] for k, e in v["koruyucular"].items() if k in SIGORTA_LISTESI}
    for (yer, alt) in liste:
        if (yer, alt) not in tablodaki and yer not in SIGORTA_LISTESI_YUKSUZ:
            h.append(f"elektrik.md sigorta listesinde '{yer}{' ' + alt if alt else ''}' değerinin tabloda koruyucusu yok")
    ks = set_coklu(el)
    if ks is None:
        h.append("elektrik.md 'kutudaki set …' satırı okunamadı")
    else:
        for a, n in setten.items():
            if n > ks.get(a, 0):
                h.append(f"setten {n} × {a:g} A isteniyor, kutudaki sette {ks.get(a, 0)} tane")
    return h


def s_ag(v, b):
    h = []
    D, A, E = v["dugumler"], v["aglar"], elemanlar(v)
    for u, d in D.items():
        if d.get("ag") is not None and d["ag"] not in A:
            h.append(f"düğüm '{u}': ağ '{d['ag']}' aglar'da yok")
        if " · " not in u or u.split(" · ")[0] != d.get("parca"):
            h.append(f"düğüm '{u}': parça adı kimlikle tutmuyor")
            continue
        nokta = u.split(" · ", 1)[1]
        if d.get("ag") is None and GUC_ADI.match(nokta) and "→ GND" not in nokta:
            h.append(f"düğüm '{u}': adı güç ucu ama ağı yazılı değil")
    for kid, e in E.items():
        for n in ([e["giris"]] if e["giris"] else []) + e["cikis"]:
            if n not in A:
                h.append(f"eleman {kid}: ağ '{n}' aglar'da yok")
        sg = A.get(e["giris"], {}).get("sinif")
        for n in e["cikis"]:
            sc = A.get(n, {}).get("sinif")
            if sg in BES_V and sc in BES_V and sg != sc:
                h.append(f"eleman {kid}: {sg} ile {sc} ağlarını birleştiriyor (5 V Pi / çevre ayrı kalmalı)")
    for ib in v.get("ic_baglar", []):
        if ib.get("a") not in D or ib.get("b") not in D:
            h.append(f"kart içi bağ {ib.get('a')} ↔ {ib.get('b')}: uç düğümler listesinde yok")
            continue
        na, nb = D[ib["a"]].get("ag"), D[ib["b"]].get("ag")
        sa, sb = A.get(na, {}).get("sinif"), A.get(nb, {}).get("sinif")
        if sa in BES_V and sb in BES_V and sa != sb:
            h.append(f"kart içi bağ {ib['a']} ↔ {ib['b']}: 5 V Pi ve 5 V çevre ağlarını birleştiriyor ({na} ↔ {nb})")
        elif (kutup(v, na) in GUC_KUTUP or kutup(v, nb) in GUC_KUTUP) and na != nb and not ib.get("eleman"):
            # güç ağını başka ağa bağlayan kart içi bağ yalnız bir eleman üstünden (transistör, opto: 'eleman' yazılı)
            if not re.search(r"(BC337|PC817|transistör|kollektör|opto)", ib.get("ne", ""), re.I):
                h.append(f"kart içi bağ {ib['a']} ↔ {ib['b']}: farklı ağlar ({na} ↔ {nb}), arada eleman yazılı değil")
    for n, a in A.items():
        if a["kutup"] in ("+", "±") or (a["kutup"] == "−" and n != "GND"):
            try:
                zincir(v, n)
            except ValueError as x:
                h.append(f"ağ {n}: {x}")
    for r in v["kablolar"]:
        for d in r["damarlar"]:
            for u in (d["a"], d["b"]):
                if u not in D:
                    h.append(f"{r['kimlik']}/{d['ad']}: uç '{u}' düğümler listesinde yok")
            if d["a"] not in D or d["b"] not in D:
                continue
            na, nb = D[d["a"]].get("ag"), D[d["b"]].get("ag")
            sa, sb = A.get(na, {}).get("sinif"), A.get(nb, {}).get("sinif")
            if sa in BES_V and sb in BES_V and sa != sb:
                h.append(f"{r['kimlik']}/{d['ad']}: 5 V Pi ve 5 V çevre ağları bu telde birleşiyor ({na} ↔ {nb})")
                continue
            if d.get("ara_koruyucu"):
                e = v["koruyucular"].get(d["ara_koruyucu"])
                if not e or d.get("ara_uc") not in ("a", "b"):
                    h.append(f"{r['kimlik']}/{d['ad']}: ara_koruyucu '{d.get('ara_koruyucu')}' / ara_uc '{d.get('ara_uc')}' geçersiz")
                    continue
                gir, ote = (na, nb) if d["ara_uc"] == "a" else (nb, na)
                if gir != e["giris"] or ote not in e["cikis"]:
                    h.append(f"{r['kimlik']}/{d['ad']}: arada {d['ara_koruyucu']} ({e['giris']} → {e['cikis']}) ama uçlar {gir} → {ote}")
            elif d.get("ara"):
                h.append(f"{r['kimlik']}/{d['ad']}: 'ara' metni var ama ara_koruyucu yok")
            elif na != nb:
                h.append(f"{r['kimlik']}/{d['ad']}: telin iki ucu farklı ağlarda ({na} ↔ {nb})")
    return h


def s_ayni_nokta(v, b):
    ortak = set(v["ortak_noktalar"])
    yer = {}
    for r in v["kablolar"]:
        for d in r["damarlar"]:
            for u in (d["a"], d["b"]):
                yer.setdefault(u, []).append(f"{r['kimlik']}/{d['ad']}")
    return [f"'{u}' iki ayrı işte: {', '.join(k)}" for u, k in sorted(yer.items()) if len(k) > 1 and u not in ortak]


def s_esp32_pin(v, b):
    h = []
    pin = b["pin"]
    pinler, bos = pin["pinler"], pin["bos"]
    if len(pinler) + len(bos) != 25:
        h.append(f"pin haritası {len(pinler)} + {len(bos)} boş = {len(pinler) + len(bos)}; 25 bekleniyor")
    if set(bos) != {"12"}:
        h.append(f"boş pinler {sorted(bos)}; yalnız 12 bekleniyor")
    led = pinler.get("DURUM_LED", {})
    if led.get("gpio") != 2 or "baglanmaz" not in led.get("not", ""):
        h.append("GPIO2 yalnız kart LED'i olarak yazılı değil")
    for u, d in v["dugumler"].items():
        if d.get("parca") != "ESP32":
            continue
        nokta = u.split(" · ", 1)[1]
        if "gpio" in d:
            if not isinstance(d["gpio"], int) or u != f"ESP32 · GPIO{d['gpio']}":
                h.append(f"düğüm '{u}': gpio alanı {d.get('gpio')!r}, kimlik 'ESP32 · GPIO{d.get('gpio')}' olmalı")
        elif nokta not in ESP32_GPIO_DISI:
            h.append(f"düğüm '{u}': ESP32 ucu ama gpio sayı alanı yok (tek biçim: 'ESP32 · GPIO<n>' + gpio)")
    beklenen = {ad: p["gpio"] for ad, p in pinler.items() if ad not in KART_USTU}
    gorulen = {}
    for r in v["kablolar"]:
        for d in r["damarlar"]:
            gu = [v["dugumler"].get(u, {}).get("gpio") for u in (d["a"], d["b"])]
            gu = [g for g in gu if g is not None]
            esp_ucu = any(v["dugumler"].get(u, {}).get("parca") == "ESP32" and u.split(" · ", 1)[1] not in ESP32_GPIO_DISI
                          for u in (d["a"], d["b"]))
            if "gpio" not in d:
                if gu or esp_ucu:
                    h.append(f"{r['kimlik']}/{d['ad']}: ESP32 GPIO ucu var ama damarda gpio / pin yok")
                continue
            g, ad = d["gpio"], d.get("pin")
            if gu != [g]:
                h.append(f"{r['kimlik']}/{d['ad']}: damar gpio {g}, uç düğümünün gpio alanı {gu}")
            if g in (12, 2) or g in {pinler[k]["gpio"] for k in KART_USTU if k in pinler}:
                h.append(f"{r['kimlik']}/{d['ad']}: GPIO{g} dışarıya bağlanmaz (boş / LED / kart üstü)")
            if ad not in beklenen:
                h.append(f"{r['kimlik']}/{d['ad']}: pin adı '{ad}' pin haritasında yok")
            elif beklenen[ad] != g:
                h.append(f"{r['kimlik']}/{d['ad']}: {ad} haritada GPIO{beklenen[ad]}, tabloda GPIO{g}")
            gorulen.setdefault(ad, []).append(g)
    for ad, gl in gorulen.items():
        if len(gl) > 1:
            h.append(f"{ad} tabloda {len(gl)} kez")
    eksik = sorted(set(beklenen) - set(gorulen))
    if eksik:
        h.append(f"haritadaki pinler tabloda yok: {eksik}")
    return h


def s_pca_kanal(v, b):
    h = []
    yaml, pj = b["kanallar"], {int(k): a for k, a in b["pin"]["pca9685_kanallar"].items()}
    for ad, k in yaml.items():
        if pj.get(k) != ad:
            h.append(f"main kanallar.yaml {ad} = K{k}, pin haritası K{k} = {pj.get(k)}")
    for u, d in v["dugumler"].items():
        if d.get("parca") == "PCA9685" and "pca_kanal" in d and u != f"PCA9685 · K{d['pca_kanal']}":
            h.append(f"düğüm '{u}': pca_kanal {d['pca_kanal']} kimlikle tutmuyor")
        if d.get("parca") == "PCA9685" and re.match(r"PCA9685 · K", u) and "pca_kanal" not in d:
            h.append(f"düğüm '{u}': PCA kanal ucu ama pca_kanal sayı alanı yok")
    tablo = {}
    for r in v["kablolar"]:
        for d in r["damarlar"]:
            for u in (d["a"], d["b"]):
                k = v["dugumler"].get(u, {}).get("pca_kanal")
                if k is not None and d.get("pca_kanal") != k:
                    h.append(f"{r['kimlik']}/{d['ad']}: uç '{u}' (K{k}), damarda pca_kanal {d.get('pca_kanal')}")
            if "pca_kanal" in d:
                tablo.setdefault(d["pca_kanal"], set()).add(d.get("pca_ad"))
    for k, adlar in sorted(tablo.items()):
        if len(adlar) > 1:
            h.append(f"K{k} tabloda iki ayrı adla: {sorted(adlar)}")
        ad = next(iter(adlar))
        if pj.get(k) != ad:
            h.append(f"K{k} tabloda '{ad}', pin haritasında '{pj.get(k)}'")
        yk = yaml.get(ad)
        if ad in yaml and yk != k:
            h.append(f"'{ad}' tabloda K{k}, main kanallar.yaml'da K{yk}")
    kullanilan = {k for k, a in pj.items() if a != "yedek"}
    if set(tablo) != kullanilan:
        h.append(f"tablodaki kanallar {sorted(tablo)}; pin haritasında kullanılanlar {sorted(kullanilan)}")
    for ad, k in yaml.items():
        if k not in tablo:
            h.append(f"main kanallar.yaml {ad} (K{k}) tabloda yok")
    return h


def kesit_degerlendir(v, r):
    """[(damar adı, koruyan, akım, sınır, geçti mi, awg)] ya da hata metni."""
    g = guc_damarlari(v, r)
    if not g:
        return []
    out = []
    for d, n, k in g:
        kes = d.get("kesit") or r.get("kesit")
        if kes is None:
            out.append((d["ad"], k, akim(v, k), None, False, None))
            continue
        rr = dict(r, kesit=kes)
        _, _, _, sinir = kablolar_uret.kablo_siniri(v, rr)
        a = akim(v, k)
        out.append((d["ad"], k, a, sinir, sinir is not None and a <= sinir + 1e-9, kes["awg"]))
    return out


def kesit_ozet(v):
    ist, karar = [], []
    for r in v["kablolar"]:
        if r.get("kesit_istisna"):
            ist.append(r["kimlik"])
        elif any(x.startswith("kesit-koruma:") for x in r["eksik"]):
            karar.append(r["kimlik"])
    return ist, karar


def sayi_gecer(metin, x):
    """Metinde x sayısı 'N A' / 'NA' / 'N Amper' olarak geçiyor mu (Türkçe ondalık virgül ya da nokta)."""
    for n in re.findall(r"(?<![\d,.])(\d+(?:[.,]\d+)?) ?A(?:mper|'[a-zçğıöşü]+)?\b", metin):
        if abs(tr_sayi(n.replace(".", ",")) - x) < 1e-9:
            return True
    return False


def kaynak_metni(s):
    """kaynak_coz ile aynı biçim; çözülen metni döndürür (yoksa None)."""
    if "#" in s:
        yol, anahtar = s.split("#", 1)
        try:
            d = json.loads((KOK / yol).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        for p in anahtar.split("."):
            if isinstance(d, list) and p.isdigit() and int(p) < len(d):
                d = d[int(p)]
            elif isinstance(d, dict) and p in d:
                d = d[p]
            else:
                return None
        return json.dumps(d, ensure_ascii=False)
    m = re.match(r"(.+?):(\d+)(?:-(\d+))?$", s)
    if not m or not (KOK / m.group(1)).is_file():
        return None
    sat = (KOK / m.group(1)).read_text(encoding="utf-8").splitlines()
    a, z = int(m.group(2)), int(m.group(3) or m.group(2))
    return "\n".join(sat[a - 1:z]) if 1 <= a <= z <= len(sat) else None


def istisna_sina(v, h, istisna):
    """Düzeltme turu 2: istisna kayıtlarının kendisi (üye listesi, karar, alanlar, koruyucu / üst sınır / en ince kesit)."""
    adlar = set(istisna)
    for ad in sorted(adlar - set(ISTISNA_KARARI)):
        h.append(f"istisna '{ad}': kayıtlı kararlarda yok (ISTISNA_KARARI); yeni istisna yeni karar ister")
    for ad in sorted(set(ISTISNA_KARARI) - adlar):
        h.append(f"istisna '{ad}': kayıtlı karar var ama tabloda yok")
    kodlar = {k.get("kod") for k in v.get("kararlar", [])}
    for ad, i in istisna.items():
        if ad not in ISTISNA_KARARI:
            continue
        kod, uyeler = ISTISNA_KARARI[ad]
        kap = i.get("kapsam", [])
        if len(kap) != len(uyeler) or set(kap) != uyeler:
            h.append(f"istisna '{ad}': kapsam {sorted(kap)} ({len(kap)}), kayıtlı karar {kod}: {sorted(uyeler)} ({len(uyeler)})")
        if kod not in str(i.get("karar", "")) or kod not in kodlar:
            h.append(f"istisna '{ad}': karar alanı / kararlar listesi {kod}'yu taşımıyor")
        for z in ("gerekce", "sart", "kontrol", "karar"):
            x = str(i.get(z, ""))
            m = YER_TUTUCU.search(x)
            if len(x.strip()) < 20 or m:
                h.append(f"istisna '{ad}': {z} boş / yer tutucu / çok kısa ('{x[:40]}')")
        kor = i.get("koruyucular")
        if not isinstance(kor, dict) or not kor:
            h.append(f"istisna '{ad}': koruyucular (kimlik → üst sınır, kaynak, en ince kesit) yok")
            continue
        bek = ISTISNA_KESITI.get(ad, {})
        gor = {k: x.get("en_ince_awg") for k, x in kor.items()}
        if gor != bek:
            h.append(f"istisna '{ad}': koruyucu → en ince kesit {gor}, kayıtlı kararda {bek}")
        for kid, x in kor.items():
            if kid not in v["koruyucular"]:
                h.append(f"istisna '{ad}': koruyucu {kid} koruyucular tablosunda yok")
                continue
            ust, ince = x.get("ust_sinir_a"), x.get("en_ince_awg")
            if not isinstance(ust, (int, float)) or not isinstance(ince, int):
                h.append(f"istisna '{ad}' / {kid}: ust_sinir_a / en_ince_awg sayı değil")
                continue
            km = kaynak_metni(str(x.get("kaynak", "")))
            if km is None:
                h.append(f"istisna '{ad}' / {kid}: üst sınırın kaynağı çözülmüyor: {x.get('kaynak')}")
            elif not sayi_gecer(km, ust):
                h.append(f"istisna '{ad}' / {kid}: üst sınır {ust:g} A kaynak satırında yok ({x.get('kaynak')})")
            a = v["koruyucular"][kid]["akim_a"]
            if a is not None and a > ust + 1e-9:
                h.append(f"istisna '{ad}': koruyucu {kid} {a:g} A, istisnanın üst sınırı {ust:g} A (istisna bu akımı savunmaz)")
            if a is None and not str(x.get("belgesiz_koruyucu", "")).strip():
                h.append(f"istisna '{ad}' / {kid}: koruyucunun akımı belgesiz; belgesiz_koruyucu gerekçesi yok")


def istisnali_kablo(v, h, r, i):
    """İstisnalı kablo sınamadan çıkmaz: koruyan istisnanın koruyucusu, akım ≤ üst sınır, kesit ≥ en ince izinli kesit."""
    ad = i["ad"]
    if r["kimlik"] not in ISTISNA_KARARI.get(ad, ("", set()))[1]:
        h.append(f"{r['kimlik']}: istisna '{ad}' kayıtlı kararın üye listesinde değil (sessiz muafiyet)")
    kor = i.get("koruyucular") or {}
    for d, n, k in guc_damarlari(v, r):
        x = kor.get(k)
        if x is None:
            h.append(f"{r['kimlik']}/{d['ad']}: devreden türetilen koruyan {k}, istisna '{ad}' yalnız {sorted(kor)} için. {YON}")
            continue
        kes = d.get("kesit") or r.get("kesit")
        ust, ince = x.get("ust_sinir_a"), x.get("en_ince_awg")
        if not isinstance(ust, (int, float)) or not isinstance(ince, int):
            continue
        if kes is None:
            if i.get("kesit_bilinmiyorsa") != "teyit" or not any("kesit" in t for t in r["teyit"]):
                h.append(f"{r['kimlik']}/{d['ad']}: kesit yok; istisna '{ad}' kesitsiz kabloyu yalnız 'kesit' teyidiyle alır")
        elif kes["awg"] > ince:
            h.append(f"{r['kimlik']}/{d['ad']}: {kes['awg']} AWG, istisna '{ad}' en ince {ince} AWG'ye izin veriyor")
        a = v["koruyucular"][k]["akim_a"]
        if a is not None:
            if a > ust + 1e-9:
                h.append(f"{r['kimlik']}/{d['ad']}: koruyan {k} {a:g} A > istisna '{ad}' üst sınırı {ust:g} A")
        else:
            _, _, _, s = kablolar_uret.kablo_siniri(v, dict(r, kesit={"awg": ince}))
            if s is None or ust > s + 1e-9:
                h.append(f"{r['kimlik']}/{d['ad']}: koruyan {k} belgesiz; istisnanın üst sınırı {ust:g} A, en ince izinli "
                         f"{ince} AWG'nin bu bölgedeki sınırı {s} A")


def s_kesit(v, b):
    h = []
    kk = v["kesit_kurali"]
    for t in kk["tablo"]:
        d = [x for x in t.get("dayanak", {}).values() if x is not None]
        if t["awg"] not in KESIT_KAYNAGI:
            h.append(f"kesit_kurali {t['awg']} AWG: sabit kaynak tablosunda (KESIT_KAYNAGI) yok")
        elif t.get("dayanak") != KESIT_KAYNAGI[t["awg"]]:
            h.append(f"kesit_kurali {t['awg']} AWG: dayanak {t.get('dayanak')}, kaynaklar (CFR Table 5 / NFPA 79 Table 12.5.1) "
                     f"{KESIT_KAYNAGI[t['awg']]}")
        if not d:
            h.append(f"kesit_kurali {t['awg']} AWG: dayanak (kaynak değerleri) yok")
        elif t["en_cok_koruma_a"] != min(d):
            h.append(f"kesit_kurali {t['awg']} AWG: en çok {t['en_cok_koruma_a']} A, kaynakların küçüğü {min(d)} A "
                     f"(temkinli olan alınır)")
        for ad in t.get("dayanak", {}):
            if ad not in kk.get("kaynaklar", {}) or not kk["kaynaklar"][ad].get("url"):
                h.append(f"kesit_kurali {t['awg']} AWG: '{ad}' kaynağının adı / bağlantısı yok")
    o = kk.get("ortam", {})
    if not o.get("kaynak", {}).get("url"):
        h.append("kesit_kurali.ortam: katsayıların kaynağı yok")
    if [(k["en_cok_c"], k["k"]) for k in o.get("katsayilar", [])] != KATSAYI_KAYNAGI:
        h.append(f"kesit_kurali.ortam.katsayilar {o.get('katsayilar')}, kaynak (NEC 310.15(B)(1), 75 °C) {KATSAYI_KAYNAGI}")
    for bad, x in o.get("bolgeler", {}).items():
        if kablolar_uret.katsayi(v, x["sicaklik_c"]) is None:
            h.append(f"bölge {bad}: {x['sicaklik_c']} °C için katsayı yok")
        km = kaynak_metni(x.get("kaynak", "")) or ""
        m = re.findall(BOLGE_KALIBI.get(bad, r"$^"), km)
        if len(m) != 1 or int(m[0]) != x["sicaklik_c"]:
            h.append(f"bölge {bad}: {x['sicaklik_c']} °C, kaynak satırında ({x.get('kaynak')}) kalıpla okunan {m}")
    for kid, e in v["koruyucular"].items():
        if e["akim_a"] is None and not e.get("sinir_kaynagi"):
            h.append(f"koruyucu {kid}: akım sınırı boş ve neden boş olduğu (sinir_kaynagi) yazılı değil")
        b_ = e.get("yuk_butcesi")
        if b_:
            for alan, ak in (("toplam_tipik_a", "tipik_a"), ("toplam_tepe_a", "tepe_a")):
                t = sum(x[ak] for x in b_["kalemler"])
                if abs(t - b_[alan]) > 0.005:
                    h.append(f"koruyucu {kid}: yük bütçesi {alan} {b_[alan]} A, kalemlerin toplamı {t:.3f} A")
            if e["akim_a"] is not None and b_["toplam_tepe_a"] >= e["akim_a"]:
                h.append(f"koruyucu {kid}: yük bütçesinin tepesi {b_['toplam_tepe_a']} A sigortanın {e['akim_a']} A'ine ulaşıyor (atar)")
    istisna = {i["ad"]: i for i in kk.get("istisnalar", [])}
    istisna_sina(v, h, istisna)
    for r in v["kablolar"]:
        g = guc_damarlari(v, r)
        tur = max((x[2] for x in g), key=lambda i: akim(v, i)) if g else None
        if r["koruma"] != tur:
            h.append(f"{r['kimlik']}: koruma '{r['koruma']}', devrenin yapısından '{tur}' (koruyucular tablosu). {YON}")
        ia = r.get("kesit_istisna")
        if ia:
            i = istisna.get(ia)
            if not i:
                h.append(f"{r['kimlik']}: kesit_istisna '{ia}' kesit_kurali.istisnalar'da yok")
            elif r["kimlik"] not in i.get("kapsam", []):
                h.append(f"{r['kimlik']}: istisna '{ia}' kapsamında değil (sessiz muafiyet)")
            else:
                istisnali_kablo(v, h, r, i)
            continue
        kararli = r["durum"] == "karara bağlı" and any(e.startswith("kesit-koruma:") for e in r["eksik"])
        sonuc = kesit_degerlendir(v, r)
        kotu = [x for x in sonuc if not x[4]]
        for ad, k, a, s, _, aw in kotu:
            if kararli:
                continue
            if s is None:
                h.append(f"{r['kimlik']}/{ad}: kesit yok; koruyan {k}")
            elif a == math.inf:
                h.append(f"{r['kimlik']}/{ad}: koruyan {k}'nin akım sınırı belgelenmemiş; {aw} AWG sınanamıyor")
            else:
                h.append(f"{r['kimlik']}/{ad}: {aw} AWG ortam düzeltmeli en çok {s:g} A, koruyan {k} {a:g} A")
        if kararli and sonuc and not kotu:
            h.append(f"{r['kimlik']}: 'kesit-koruma' kararı bekliyor ama kural geçiyor (eksik maddesi kalkmalı)")
    for ad, i in istisna.items():
        # beklenen akım bütçesi yazılı istisnada: her hattın sürekli ve tepe akımı kablonun düzeltilmiş sınırının altında
        for hat in (i.get("beklenen_akim_a") or {}).get("hatlar", []):
            r = next((x for x in v["kablolar"] if x["kimlik"] == hat.get("kablo")), None)
            if r is None:
                h.append(f"istisna '{ad}': beklenen akımdaki {hat.get('kablo')} tabloda yok")
                continue
            _, _, _, sinir = kablolar_uret.kablo_siniri(v, r)
            if sinir is None or abs(sinir - hat.get("duzeltilmis_sinir_a", -1)) > 0.05:
                h.append(f"istisna '{ad}': {r['kimlik']} düzeltilmiş sınırı kayıtta {hat.get('duzeltilmis_sinir_a')} A, "
                         f"kesit / bölgeden {sinir} A")
            elif max(hat.get("surekli_yogun_a", math.inf), hat.get("tepe_a", math.inf)) > sinir + 1e-9:
                h.append(f"istisna '{ad}': {r['kimlik']} beklenen akım (sürekli {hat.get('surekli_yogun_a')} / tepe "
                         f"{hat.get('tepe_a')} A) düzeltilmiş sınırın ({sinir:g} A) üstünde: istisna yapılamaz")
        for k in i.get("kapsam", []):
            if not any(r["kimlik"] == k and r.get("kesit_istisna") == ad for r in v["kablolar"]):
                h.append(f"istisna '{ad}' kapsamındaki {k} kayıtta istisnayı taşımıyor")
    # bara köprüleri (12 AWG zincir köprü): koruyan düğümün ağını besleyen zincirden; besleme ortadaysa akım yarıya
    bp = v.get("klemens_turleri", {}).get("bara-pabuc", {})
    for dugum, k in (bp.get("kopruler") or {}).items():
        if not isinstance(k, dict) or "awg" not in k:
            continue
        net = v["dugumler"].get(dugum, {}).get("ag")
        n = bp.get("dugumler", {}).get(dugum)
        if net == "GND":
            kor = [x for x, e in v["koruyucular"].items() if e["giris"] is None]
            kid = kor[0] if kor else None
        else:
            try:
                kid = sinirlayan(v, net)
            except ValueError:
                kid = None
        if kid is None:
            h.append(f"köprü {dugum}: koruyanı türetilemedi (ağ {net})")
            continue
        a = akim(v, kid)
        bs = k.get("besleme_saplamasi")
        _, _, _, s = kablolar_uret.kablo_siniri(v, {"kesit": {"awg": k["awg"]}, "bolge": "etek", "damarlar": [], "demet": ""})
        if bs is None:
            if s is None or a > s + 1e-9:
                h.append(f"köprü {dugum}: {k['awg']} AWG etekte en çok {s} A, koruyan {kid} {a:g} A (besleme saplaması yok: tam akım)")
            continue
        for x in kopru_akimlari(v, h, dugum, k, n, kid):
            i_, yan_, akim_ = x
            if s is None or akim_ > s + 1e-9:
                h.append(f"köprü {dugum} {i_}–{i_ + 1}: {k['awg']} AWG etekte en çok {s} A, en kötü akım {akim_:g} A ({yan_})")
    return h


def kok_sigorta(v, r):
    z = [x for x in duz(r["besleme_zinciri"]) if isinstance(x, str)]
    f = [x for x in z if re.match(r"^F\d$", x)]
    return f[0] if f else (r["koruma"] or (z[0] if z else None))


def kopru_akimlari(v, h, dugum, k, n, kid):
    """Zincir köprüde i–(i+1) köprüsünün en kötü akımı: besleme saplamasından uzak yandaki saplamalara bağlı dönüşlerin koruyucu
    akımları toplamı; aynı kök sigortadan beslenenler o sigortayla, hepsi kökteki koruyucuyla (ana dönüş) sınırlı."""
    yer = k.get("yerlesim")
    K = {r["kimlik"]: r for r in v["kablolar"]}
    iletken = sorted(f"{r['kimlik']}/{d['ad']}" for r in v["kablolar"] for d in r["damarlar"] for u in (d["a"], d["b"]) if u == dugum)
    if not isinstance(yer, dict):
        h.append(f"köprü {dugum}: besleme saplaması {k.get('besleme_saplamasi')} ama yerleşim (saplama → iletkenler) kayıtlı değil")
        return []
    yazili = sorted(x for xs in yer.values() for x in xs)
    if yazili != iletken:
        h.append(f"köprü {dugum}: yerleşimdeki iletkenler {yazili}, düğüme giden iletkenler {iletken}")
    bs = k["besleme_saplamasi"]
    m = v["klemens_turleri"]["bara-pabuc"].get("saplama_basina_en_cok_pabuc", 4)
    for i in range(1, n + 1):
        uc = (1 if i in (1, n) else 2) if n > 1 else 0
        if len(yer.get(str(i), [])) + uc > m:
            h.append(f"köprü {dugum}: saplama {i}'de {len(yer.get(str(i), []))} iletken + {uc} köprü ucu > {m} pabuç")
    aku = [x for x in yer.get(str(bs), []) if K.get(x.split("/")[0], {}).get("dal") == "aku-ana"]
    if not aku:
        h.append(f"köprü {dugum}: besleme saplaması {bs}'de akü dönüşü yok (yerleşim)")
    kok_a = akim(v, kid)

    def toplam(saplamalar):
        grup = {}
        for i in saplamalar:
            for x in yer.get(str(i), []):
                r = K.get(x.split("/")[0])
                if r is None:
                    continue
                f = kok_sigorta(v, r)
                a_ = akim(v, r["koruma"]) if r["koruma"] else None
                fa = akim(v, f) if f else None
                g = grup.setdefault(f, [fa, 0.0])
                g[1] += a_ if a_ is not None else (fa or 0)
        return min(kok_a, sum(min(fa, t) if fa is not None else t for fa, t in grup.values()))

    out = []
    for i in range(1, n):
        uzak = range(1, i + 1) if i < bs else range(i + 1, n + 1)
        out.append((i, f"saplama {', '.join(map(str, uzak))} dönüşleri", toplam(uzak)))
    return out


def awg(r, d):
    k = d.get("kesit") or r.get("kesit")
    return k["awg"] if k else None


def s_donus(v, b):
    h = []
    K = {r["kimlik"]: r for r in v["kablolar"]}
    for r in v["kablolar"]:
        art, eks, pm = [], [], []
        for d in r["damarlar"]:
            n = tel_agi(v, d)
            kp = kutup(v, n)
            (art if kp == "+" else eks if kp == "−" else pm if kp == "±" else []).append((d, n))
        if art and not eks:
            od = r.get("ortak_donus") or []
            if not od:
                h.append(f"{r['kimlik']}: + damarı var, aynı kabloda − damarı yok ve ortak_donus yazılı değil")
            for k in od:
                x = K.get(k)
                if not x:
                    h.append(f"{r['kimlik']}: ortak_donus '{k}' tabloda yok")
                    continue
                xd = [d for d in x["damarlar"] if kutup(v, tel_agi(v, d)) == "−"]
                if not xd:
                    h.append(f"{r['kimlik']}: ortak_donus {k}'de − damarı yok")
                elif r.get("kesit") and x.get("kesit") and x["kesit"]["awg"] > r["kesit"]["awg"]:
                    h.append(f"{r['kimlik']}: ortak dönüş {k} ({x['kesit']['awg']} AWG) + damarından ({r['kesit']['awg']} AWG) ince")
        for d, n in eks:
            for p, _ in art:
                if awg(r, d) and awg(r, p) and awg(r, d) > awg(r, p):
                    h.append(f"{r['kimlik']}: dönüş '{d['ad']}' ({awg(r, d)} AWG) + damarı '{p['ad']}'dan ({awg(r, p)} AWG) ince")
        if pm and len({n for _, n in pm}) < 2:
            h.append(f"{r['kimlik']}: motor çıkışı tek damarlı (M+ / M− çifti yok)")
    # yıldıza ulaşma
    yildiz = v["yildiz_noktasi"]
    if v["dugumler"].get(yildiz, {}).get("ag") != "GND":
        h.append(f"yıldız noktası '{yildiz}' GND ağında değil")
    don = {u for u, d in v["dugumler"].items() if kutup(v, d.get("ag")) == "−"}
    kom = {u: set() for u in don}

    def bag(x, y):
        if x in kom and y in kom:
            kom[x].add(y)
            kom[y].add(x)
    for r in v["kablolar"]:
        for d in r["damarlar"]:
            bag(d["a"], d["b"])
    for ib in v.get("ic_baglar", []):
        bag(ib["a"], ib["b"])
    parca = {}
    for u in don:
        p = v["dugumler"][u]["parca"]
        if v["dugumler"][u]["ag"] == "GND" and p not in v.get("ayri_topraklar", []):
            parca.setdefault(p, []).append(u)
    for l in parca.values():
        for x in l[1:]:
            bag(l[0], x)
    gor, yig = {yildiz}, [yildiz]
    while yig:
        for y in kom.get(yig.pop(), ()):
            if y not in gor:
                gor.add(y)
                yig.append(y)
    kull = {u for r in v["kablolar"] for d in r["damarlar"] for u in (d["a"], d["b"])}
    kopuk = sorted((don & kull) - gor)
    if kopuk:
        h.append(f"yıldız noktasına varmayan dönüş düğümleri: {', '.join(kopuk)}")
    return h


def montaj_merkez(parcalar, ad):
    taraf = None
    if " #" in ad:
        ad, taraf = ad.split(" #")
    m = [x["merkez"] for x in parcalar if x["ad"] == ad]
    if taraf:
        m = [c for c in m if (c[0] > 0) == (taraf == "sag")]
    return m[0] if len(m) == 1 else None


def tahmin_hesap(parcalar, uclar, kural):
    """montaj-analiz ev pozu merkezleri: en uzak çiftin Manhattan uzaklığı × çarpan + pay, yuvarlama adımına yukarı (boy_tahmin_kurali)."""
    d = 0
    for a, c in uclar:
        ma, mc = montaj_merkez(parcalar, a), montaj_merkez(parcalar, c)
        if ma is None or mc is None:
            return None, f"parça bulunamadı ya da tek değil: {a if ma is None else c}"
        d = max(d, sum(abs(x - y) for x, y in zip(ma, mc)))
    adim = kural["yuvarlama_mm"]
    return int(-(-(d * kural["carpan"] + kural["pay_mm"]) // adim) * adim), None


def s_tahmin(v, b):
    h = []
    for r in v["kablolar"]:
        t = r.get("boy_tahmin")
        if r["boy"] and t:
            h.append(f"{r['kimlik']}: hem boy (ölçüm / CAD) hem boy_tahmin var; tahmin ölçümün yerine geçmez")
            continue
        if r["boy"]:
            continue
        if not t:
            h.append(f"{r['kimlik']}: boy yok ve boy_tahmin yok")
            continue
        if "tahmin" not in t.get("etiket", "") or "P10.7b" not in t.get("etiket", ""):
            h.append(f"{r['kimlik']}: boy_tahmin etiketi 'tahmin, P10.7b'de ölçülecek' değil")
        if not isinstance(t.get("mm"), int) or t["mm"] <= 0:
            h.append(f"{r['kimlik']}: boy_tahmin.mm geçersiz")
            continue
        if t.get("uclar"):
            mm, e = tahmin_hesap(b["parcalar"], t["uclar"], v["boy_tahmin_kurali"])
            if e:
                h.append(f"{r['kimlik']}: boy_tahmin {e}")
            elif mm != t["mm"]:
                h.append(f"{r['kimlik']}: boy_tahmin {t['mm']} mm, uçlardan yeniden hesap {mm} mm")
        else:
            e = kaynak_coz(t.get("kaynak", ""))
            if e:
                h.append(f"{r['kimlik']}: sabit tahminin kaynağı: {e}")
    return h


def uc_iletkenleri(v, r):
    """[(damar, yan, tür, kesit {awg, mm2} ya da None)]: her damarın iki ucu; ara_uc yanında iletken hat yuvasının kuyruğu."""
    out = []
    mm2 = {t["awg"]: t["mm2"] for t in v["kesit_kurali"]["tablo"]}
    for d in r["damarlar"]:
        for yan in ("a", "b"):
            tur = (d.get("uc_turu") or {}).get(yan)
            kes = d.get("kesit") or r.get("kesit")
            if d.get("ara_koruyucu") and d.get("ara_uc") == yan and v["koruyucular"].get(d["ara_koruyucu"], {}).get("tur") == "sigorta":
                kes = {"awg": HAT_YUVASI_KUYRUK_AWG, "mm2": mm2.get(HAT_YUVASI_KUYRUK_AWG)}
            ku = (d.get("uc_kuyrugu") or {}).get(yan)
            if isinstance(ku, dict) and "awg" in ku:
                kes = {"awg": ku["awg"], "mm2": ku.get("mm2")}
            out.append((d, yan, tur, kes))
    return out


def s_klemens(v, b):
    h = []
    tur = v.get("klemens_turleri", {})
    if set(tur) != set(UC_TURU_SINIRI):
        h.append(f"klemens_turleri {sorted(tur)}; sabit uç türü sözlüğü (UC_TURU_SINIRI) {sorted(UC_TURU_SINIRI)}")
    for ad, t in tur.items():
        sab = UC_TURU_SINIRI.get(ad)
        if sab == "klemens değil":
            if not t.get("klemens_degil"):
                h.append(f"uç türü {ad}: klemens değil (lehim / fiş) ama klemens_degil işareti yok")
            continue
        if t.get("en_cok_mm2") != sab:
            h.append(f"klemens türü {ad}: sınır {t.get('en_cok_mm2')} mm², kaynak tablosunda (UC_TURU_SINIRI) {sab}")
        il = UC_TURU_ILETKEN.get(ad, ("?", "?"))
        if (t.get("iletken"), t.get("en_az_mm2")) != il:
            h.append(f"uç türü {ad}: iletken '{t.get('iletken')}', en ince {t.get('en_az_mm2')} mm²; sabit tabloda (UC_TURU_ILETKEN) {il}")
        e = kaynak_coz(t.get("kaynak") or "")
        if e:
            h.append(f"klemens türü {ad}: {e}")
    for r in v["kablolar"]:
        on_iki = False
        turler = set()
        for d, yan, t, kes in uc_iletkenleri(v, r):
            if t not in UC_TURU_SINIRI:
                h.append(f"{r['kimlik']}/{d['ad']}: {yan} ucunun türü '{t}' tanımsız (uc_turu, sabit sözlük)")
                continue
            turler.add(t)
            p_ = v["dugumler"].get(d[yan], {}).get("parca")
            nokta_ = d[yan].split(" · ", 1)[-1]
            direnc_ucu = d.get("ara_uc") == yan and v["koruyucular"].get(d.get("ara_koruyucu"), {}).get("tur") == "direnc"
            bts_sinyal = p_ in ("BTS7960 sol", "BTS7960 sağ") and nokta_ not in ("B+", "B−", "M+", "M−")
            if p_ in PARCA_UC_TURU and kutup(v, v["dugumler"].get(d[yan], {}).get("ag")) in GUC_KUTUP \
                    and not direnc_ucu and not bts_sinyal and t != PARCA_UC_TURU[p_]:
                h.append(f"{r['kimlik']}/{d['ad']}: {d[yan]} ucunun türü '{t}', {p_} güç ucu {PARCA_UC_TURU[p_]}")
            sinir = UC_TURU_SINIRI[t]
            if sinir == "klemens değil":
                continue
            if kes is None:
                if not any("kesit" in x for x in r["teyit"]):
                    h.append(f"{r['kimlik']}/{d['ad']}: {t} ucuna giriyor ama kesiti yok ve 'kesit' teyidi yok")
                continue
            on_iki |= kes["awg"] <= 12
            ku = (d.get("uc_kuyrugu") or {}).get(yan)
            malz = ku.get("malzeme") if isinstance(ku, dict) else r.get("malzeme")
            iletken = "ince telli" if kes.get("awg") == HAT_YUVASI_KUYRUK_AWG and d.get("ara_uc") == yan else MALZEME_ILETKEN.get(malz)
            il, az = UC_TURU_ILETKEN.get(t, (None, None))
            if il == "tek telli" and iletken == "ince telli":
                h.append(f"{r['kimlik']}/{d['ad']}: {yan} ucu {t} yalnız tek telli iletken alır, kablo {malz} ince telli")
            mm2_ = AWG_MM2.get(kes["awg"], kes.get("mm2") or 0)
            if az is not None and mm2_ < az - 1e-9:
                h.append(f"{r['kimlik']}/{d['ad']}: {kes['awg']} AWG ({mm2_} mm²) {yan} ucu {t} alt sınırının ({az} mm²) altında")
            elif az is None and t in ALT_SINIRI_BELGESIZ and mm2_ < KUCUK_KESIT_MM2 - 1e-9:
                h.append(f"{r['kimlik']}/{d['ad']}: {kes['awg']} AWG ({mm2_} mm²) {yan} ucu {t}: alt sınırı belgesiz klemens ince "
                         f"teli almaz (lehim + makaron ya da kuyruk)")
            if sinir is not None and (kes.get("mm2") or 0) > sinir:
                h.append(f"{r['kimlik']}/{d['ad']}: {kes['awg']} AWG ({kes.get('mm2')} mm²) {yan} ucu {t} sınırını ({sinir} mm²) aşıyor")
            elif sinir is None and kes["awg"] <= 12 and not any(x.startswith("klemens:") for x in r["teyit"]):
                h.append(f"{r['kimlik']}/{d['ad']}: {kes['awg']} AWG, sınırı bilinmeyen {t} ucuna (yalnız 'klemens:' teyit "
                         "maddesiyle, kesin olamaz)")
        if any((x.get("kesit") or r.get("kesit") or {}).get("awg", 99) <= 12 for x in r["damarlar"]):
            # 12 AWG kabloda sonlandırma metni bir klemens türü söylüyorsa o tür bir uçta yazılı olmalı (metin tür alanını geçemez)
            m = r["sonlandirma"].casefold()
            for kalip, t in (("5,08", "klemens-508"), ("wago", "wago-2273"), ("bts vidalı", "bts-guc")):
                if kalip in m and t not in turler:
                    h.append(f"{r['kimlik']}: sonlandırma metni '{kalip}' diyor, uç türlerinde {t} yok (12 AWG kablo)")
    for ad, t in tur.items():
        m = t.get("saplama_basina_en_cok_pabuc")
        if m is None:
            continue
        if m > 4:
            h.append(f"{ad}: saplama başına {m} pabuç; sınır 4 (ABYC E-11)")
        for dugum, n in t.get("dugumler", {}).items():
            iletken = sum(1 for r in v["kablolar"] for d in r["damarlar"] for u in (d["a"], d["b"]) if u == dugum)
            sigar = n * m - 2 * (n - 1)
            if iletken > sigar:
                h.append(f"{dugum}: {iletken} iletken, {n} saplama en çok {sigar} pabuç alır (saplama başına {m}, köprü uçları dahil)")
            for r in v["kablolar"]:
                for d, yan, tt, _ in uc_iletkenleri(v, r):
                    if d[yan] == dugum and tt != ad:
                        h.append(f"{r['kimlik']}/{d['ad']}: {dugum} saplamalı düğüm ama uç türü '{tt}' ({ad} olmalı)")
            k = (t.get("kopruler") or {}).get(dugum)
            if not isinstance(k, dict) or k.get("adet") != n - 1:
                h.append(f"{dugum}: {n} saplama zincir köprüyle {n - 1} köprü ister, kopruler kaydında "
                         f"{k.get('adet') if isinstance(k, dict) else 'yok'} (malzeme sayımı eksik kalır)")
            elif k.get("besleme_saplamasi") is not None and not (isinstance(k["besleme_saplamasi"], int) and 1 <= k["besleme_saplamasi"] <= n):
                h.append(f"{dugum}: besleme_saplamasi {k['besleme_saplamasi']!r}, 1..{n} olmalı")
    return h


def pabuc_sayimi(v):
    """{sınıf: uç sayısı}: saplamaya / cihaz saplamasına giden halka pabuçlu iletken uçları (akü kutbu hariç: kendi kalemi) +
    köprü uçları. Sınıf: 12 AWG ve kalını sarı, 14–16 mavi, 18–22 kırmızı."""
    c = Counter()
    for r in v["kablolar"]:
        for d, yan, t, kes in uc_iletkenleri(v, r):
            if t not in ("bara-pabuc", "pabuc") or kes is None:
                continue
            if v["dugumler"].get(d[yan], {}).get("parca") == "Akü":
                continue
            c["sarı" if kes["awg"] <= 12 else "mavi" if kes["awg"] <= 16 else "kırmızı"] += 1
    for dugum, k in (v.get("klemens_turleri", {}).get("bara-pabuc", {}).get("kopruler") or {}).items():
        if isinstance(k, dict) and "adet" in k:
            c["sarı" if k["awg"] <= 12 else "mavi" if k["awg"] <= 16 else "kırmızı"] += 2 * k["adet"]
    return c


def tek_kalem(kal, kosul, ne):
    i = [j for j, x in enumerate(kal) if kosul(x) and (not x.get("ver") or "v3" in x["ver"].split(","))]
    return (i[0], None) if len(i) == 1 else (None, f"maliyet.json'da {ne} için V3'te {len(i)} kalem (bir olmalı)")


def s_donanim(v, b):
    h = []
    kal = b["maliyet"]["kalemler"]
    pay = v["malzeme_payi"]
    # sigorta satırları: kalem başına tablodaki sigorta sayısı ≤ adet ≤ sayı + 1 yedek
    say = Counter(e["siparis"] for e in v["koruyucular"].values() if e["tur"] == "sigorta" and isinstance(e.get("siparis"), int))
    for i, n in sorted(say.items()):
        if i >= len(kal):
            continue
        if not n <= kal[i]["adet"] <= n + 1:
            h.append(f"maliyet.json kalem {i} ({kal[i]['model'][:40]}): {kal[i]['adet']} adet, tabloda bu sigortadan {n} "
                     f"(n ≤ adet ≤ n + 1 yedek)")
    # hat sigortası yuvası: her mini sigorta bir kapaklı yuvada, bir damarın ara_koruyucusu
    mini = sorted(k for k, e in v["koruyucular"].items() if e["tur"] == "sigorta" and e.get("bicak") == "mini")
    ara = {d.get("ara_koruyucu") for r in v["kablolar"] for d in r["damarlar"]}
    for k in mini:
        if k not in ara:
            h.append(f"mini sigorta {k} hiçbir damarın ara_koruyucusu değil (yuvası nerede?)")
    i, x = tek_kalem(kal, lambda x: x["ad"].startswith("Hat sigortası yuvası"), "hat sigortası yuvası")
    if x:
        h.append(x)
    elif not len(mini) <= kal[i]["adet"] <= len(mini) + 1:
        h.append(f"maliyet.json kalem {i} (Hat sigortası yuvası): {kal[i]['adet']} adet, tabloda {len(mini)} mini sigorta "
                 f"({', '.join(mini)})")
    # saplama takımı: düğüm saplamaları toplamı (+ en çok 1 yedek)
    bp = v.get("klemens_turleri", {}).get("bara-pabuc", {})
    ns = sum(bp.get("dugumler", {}).values())
    i, x = tek_kalem(kal, lambda x: x["ad"].startswith("Bara saplaması"), "bara saplaması")
    if x:
        h.append(x)
    elif not ns <= kal[i]["adet"] <= ns + 1:
        h.append(f"maliyet.json kalem {i} (Bara saplaması): {kal[i]['adet']} takım, tabloda {ns} saplama (n ≤ adet ≤ n + 1)")
    # halka pabuç paketleri (10'lu)
    ps = pabuc_sayimi(v)
    for sinif, kalip in (("sarı", "Halka pabuç 12 AWG"), ("mavi", "Halka pabuç 16 AWG"), ("kırmızı", "Halka pabuç 18–22 AWG")):
        i, x = tek_kalem(kal, lambda x: x["ad"].startswith(kalip), kalip)
        if x:
            h.append(x)
            continue
        birim = int(re.search(r"(\d+)'lu", kal[i]["model"]).group(1)) if re.search(r"(\d+)'lu", kal[i]["model"]) else 1
        gerek = ps[sinif] * (1 + pay)
        var = kal[i]["adet"] * birim
        ust = (math.ceil(gerek / birim - 1e-9) + 1) * birim
        if not gerek <= var <= ust:
            h.append(f"{kalip} (kalem {i}): tablodan {ps[sinif]} uç × {1 + pay:g} = {gerek:.1f}, listede {kal[i]['adet']} × {birim} = "
                     f"{var} (en çok {ust})")
    # geri tepme diyotu: röle bobini başına bir 1N4007 (yapısal alan) + 1 yedek
    bob = {k: e for k, e in v["anahtarlar"].items() if e["tur"] == "bobin"}
    K = {r["kimlik"]: r for r in v["kablolar"]}
    for k, e in bob.items():
        dd = e.get("geri_tepme_diyodu")
        if not isinstance(dd, dict) or dd.get("parca") != "1N4007" or not str(dd.get("yon", "")).strip():
            h.append(f"{k}: geri_tepme_diyodu (parca 1N4007, yer, yon, kablo) yok / eksik")
            continue
        if dd.get("kablo") not in K or "1N4007" not in K[dd["kablo"]]["sonlandirma"]:
            h.append(f"{k}: diyotun kablosu {dd.get('kablo')} yok ya da sonlandırmasında 1N4007 yazmıyor")
        # yön: katot bobinin besleme (+) ucunda, anot sürücü (−) ucunda; düğümlerin ağından
        ka = v["dugumler"].get(dd.get("katot_dugumu"), {}).get("ag")
        an = v["dugumler"].get(dd.get("anot_dugumu"), {}).get("ag")
        yon = str(dd.get("yon", ""))
        kc = next((x for x in yon.split(",") if "katot" in x), "")
        ac = next((x for x in yon.split(",") if "anot" in x and "katot" not in x), "")
        if not ("+" in kc and "−" not in kc and "−" in ac and "+" not in ac):
            h.append(f"{k}: 1N4007 yon metni '{yon}': katot bobin + ucunda, anot − ucunda olmalı (katot_dugumu / anot_dugumu ile aynı)")
        if ka != e["giris"] or an != (e["cikis"] or [None])[0]:
            h.append(f"{k}: 1N4007 katot düğümü {dd.get('katot_dugumu')!r} (ağ {ka}), anot {dd.get('anot_dugumu')!r} (ağ {an}); ters "
                     f"paralel söndürme için katot bobinin + ucunda ({e['giris']}), anot − ucunda ({(e['cikis'] or [None])[0]})")
    i, x = tek_kalem(kal, lambda x: "1N4007" in x["model"], "1N4007")
    if x:
        h.append(x)
    elif not len(bob) + 1 <= kal[i]["adet"] <= len(bob) + 2:
        h.append(f"maliyet.json kalem {i} (1N4007): {kal[i]['adet']} adet, röle bobini {len(bob)} + 1 yedek = {len(bob) + 1}")
    # röle sürücüsü: bobin başına bir BC337-40 + 1 yedek
    i, x = tek_kalem(kal, lambda x: "BC337-40" in x["model"], "BC337-40")
    if x:
        h.append(x)
    elif not len(bob) + 1 <= kal[i]["adet"] <= len(bob) + 2:
        h.append(f"maliyet.json kalem {i} (BC337-40): {kal[i]['adet']} adet, röle bobini {len(bob)} + 1 yedek = {len(bob) + 1}")
    # 2200 µF: kart başına (kondansatorler) = maliyet adedi (+ en çok 1) = elektrik.md'deki 'N × 2200 µF'
    ko = v.get("kondansatorler") or {}
    n2 = sum(y.get("adet", 0) for y in ko.get("yerler", []))
    parcalar = {d.get("parca") for d in v["dugumler"].values()}
    for y in ko.get("yerler", []):
        if y.get("kart") not in parcalar:
            h.append(f"kondansatorler: kart '{y.get('kart')}' düğümlerde yok")
    i, x = tek_kalem(kal, lambda x: "2200uF" in x["model"].replace(" ", ""), "2200 µF")
    if x:
        h.append(x)
    elif not n2 or not n2 <= kal[i]["adet"] <= n2 + 1:
        h.append(f"maliyet.json kalem {i} (2200 µF): {kal[i]['adet']} adet, tabloda kartlarda {n2} (n ≤ adet ≤ n + 1)")
    for sat in b["elektrik"].splitlines():
        if "11 mF" in sat or "servo kondansatörü" in sat:
            m = re.findall(r"(\d+) × 2200 µF", sat)
            if m and int(m[-1]) != n2:
                h.append(f"elektrik.md '{m[-1]} × 2200 µF' diyor (güncel kapasite satırı), tabloda kartlarda {n2}")
    # 5,08 mm klemens: tablodaki klemens-508 uçları kart yerlerinde; toplam × pay
    ky = v.get("klemens_yerleri") or {}
    yerler = ky.get("yerler", [])
    uc = Counter()
    for r in v["kablolar"]:
        for d, yan, t, _ in uc_iletkenleri(v, r):
            if t == "klemens-508":
                uc[v["dugumler"].get(d[yan], {}).get("parca")] += 1
    for p_, n_ in uc.items():
        ys = [y for y in yerler if y.get("parca") == p_]
        if not ys:
            h.append(f"klemens-508 uçları '{p_}' parçasında ({n_} uç), klemens_yerleri'nde yeri yok")
        elif n_ > 2 * sum(y.get("adet", 0) for y in ys):
            h.append(f"klemens yeri '{p_}': {n_} uç, {sum(y.get('adet', 0) for y in ys)} klemens en çok {2 * sum(y.get('adet', 0) for y in ys)} uç alır")
    nk = sum(y.get("adet", 0) for y in yerler)
    i, x = tek_kalem(kal, lambda x: "5.08mm Klemens" in x["model"], "5,08 mm klemens")
    if x:
        h.append(x)
    elif not math.ceil(nk * (1 + pay) - 1e-9) <= kal[i]["adet"] <= math.ceil(nk * 1.5 - 1e-9):
        h.append(f"maliyet.json kalem {i} (5,08 mm klemens): {kal[i]['adet']} adet, tabloda {nk} klemens × {1 + pay:g} = "
                 f"{nk * (1 + pay):.1f} (en çok {math.ceil(nk * 1.5 - 1e-9)})")
    # WAGO 2273: tabloda kullanılmıyorsa V3 listesinde olmaz
    nw = sum(1 for r in v["kablolar"] for d, yan, t, _ in uc_iletkenleri(v, r) if t == "wago-2273")
    wi = [j for j, x in enumerate(kal) if "2273" in x["model"] and (not x.get("ver") or "v3" in x["ver"].split(",")) and x.get("adet")]
    if nw == 0 and wi:
        h.append(f"maliyet.json kalem {wi[0]} (WAGO 2273): {kal[wi[0]]['adet']} adet V3'te, tabloda wago-2273 ucu yok")
    elif nw and not wi:
        h.append(f"tabloda {nw} wago-2273 ucu, maliyet.json'da V3 satırı yok")
    # pertinaks: parça listesi = plaket adedi (+ en çok 1)
    pp = v.get("pertinaks_parcalari") or {}
    npk = sum(x.get("plaket", 0) for x in pp.get("parcalar", []))
    i, x = tek_kalem(kal, lambda x: "Delikli Plaket" in x["model"], "delikli pertinaks")
    if x:
        h.append(x)
    elif not npk or not npk <= kal[i]["adet"] <= npk + 1:
        h.append(f"maliyet.json kalem {i} (delikli pertinaks): {kal[i]['adet']} adet, tabloda {npk} plaket (n ≤ adet ≤ n + 1)")
    return h


kablo_boy = kablolar_uret.kablo_boy
malzeme_ihtiyac = kablolar_uret.malzeme_ihtiyac


def s_malzeme(v, b):
    h = []
    mt, kal, pay = v["malzeme_turleri"], b["maliyet"]["kalemler"], v["malzeme_payi"]
    for r in v["kablolar"]:
        if r.get("malzeme") not in mt:
            h.append(f"{r['kimlik']}: malzeme '{r.get('malzeme')}' malzeme_turleri'nde yok")
    for (m, renk), mm in sorted(malzeme_ihtiyac(v).items()):
        i = mt[m]["maliyet"].get(renk, mt[m]["maliyet"].get("hepsi"))
        if i is None or i >= len(kal):
            h.append(f"{m} {renk}: maliyet.json kalemi yok")
            continue
        birim = mt[m].get("birim_m", 1)
        gerek = mm / 1000 * (1 + pay)
        ust = (math.ceil(gerek / birim - 1e-9) + 1) * birim
        var = kal[i]["adet"] * birim
        if var < gerek:
            h.append(f"{m} {renk}: ihtiyaç {mm / 1000:.2f} m × {1 + pay:g} = {gerek:.1f} m, maliyet.json kalem {i} "
                     f"({kal[i]['ad']}) {kal[i]['adet']} × {birim} m (eksik)")
        elif var > ust:
            h.append(f"{m} {renk}: maliyet.json kalem {i} ({kal[i]['ad']}) {kal[i]['adet']} × {birim} m = {var:g} m, üst eşik "
                     f"{ust:g} m (ihtiyaç {gerek:.1f} m, paket yuvarlaması + 1 birim; fazla)")
        if kal[i].get("ver") and "v3" not in kal[i]["ver"].split(","):
            h.append(f"{m} {renk}: maliyet.json kalem {i} V3 listesinde değil (ver {kal[i]['ver']})")
    for m, t in mt.items():
        if t.get("hesap_disi"):
            continue
        if not any(r.get("malzeme") == m for r in v["kablolar"]):
            h.append(f"malzeme türü {m} hiçbir kabloda yok ama tanımlı (listede kalemi fazla)")
    return h


def p12_listeleri(metin):
    m = re.search(r"## 12\..*?(?=\n## 13\.)", metin, re.S)
    if not m:
        return None, None
    s = m.group(0)
    en = re.search(r"\*\*Enerjili:\*\*(.*?)(?=\n- \*\*)", s, re.S)
    es = re.search(r"\*\*Enerjisiz:\*\*(.*?)(?=\n- \*\*|\Z)", s, re.S)
    return (en.group(1) if en else None), (es.group(1) if es else None)


def p12_ogeleri(liste):
    """§12 listesinin öğeleri (tam eşleşme için): kalın işaret ve parantez içi atılır; ';' ve cümle sonuyla bölünür; 'baş: üyeler'
    öğesinde baş alınır; 'a → b → c' zincirinde yalnız son öğe (zincirin vardığı yer; 'akü' gibi ara halkalar dal öğesi değil)."""
    s = " ".join(liste.replace("**", "").split())
    while re.search(r"\([^()]*\)", s):
        s = re.sub(r"\([^()]*\)", "", s)
    oge = set()
    for p in re.split(r";|\.\s+|\.$", s):
        p = p.split(":", 1)[0].strip(" .,")
        q = " ".join(p.split("→")[-1].split()).strip(" .,")
        if q:
            oge.add(q)
    return oge


def s_acil_stop(v, b):
    h = []
    en, es = p12_listeleri(b["p12"])
    if en is None or es is None:
        return ["kablolama-on-kararlar.md §12'de 'Enerjili:' / 'Enerjisiz:' listeleri bulunamadı"]
    en, es = p12_ogeleri(en), p12_ogeleri(es)
    for x in sorted(en & es):
        h.append(f"§12: '{x}' hem Enerjili hem Enerjisiz listesinde")
    E = elemanlar(v)
    gorulen = Counter(d["p12"] for d in v["dallar"].values())
    for x, n in gorulen.items():
        if n > 1:
            h.append(f"§12 ifadesi '{x}' {n} dalda (her dal kendi öğesi)")
    for ad, d in v["dallar"].items():
        if d["eleman"] not in E:
            h.append(f"dal {ad}: eleman '{d['eleman']}' koruyucular / anahtarlar'da yok")
            continue
        try:
            z = zincir(v, E[d["eleman"]]["cikis"][0])
        except ValueError as x:
            h.append(f"dal {ad}: {x}")
            continue
        enerjili = zincir_enerjili(v, z)
        dogru, yanlis = (en, es) if enerjili else (es, en)
        if d["p12"] not in dogru:
            h.append(f"dal {ad}: devrenin yapısına göre {'enerjili' if enerjili else 'enerjisiz'}; §12'nin "
                     f"{'Enerjili' if enerjili else 'Enerjisiz'} listesinde '{d['p12']}' öğesi yok (tam eşleşme)")
        if d["p12"] in yanlis:
            h.append(f"dal {ad}: '{d['p12']}' §12'nin {'Enerjisiz' if enerjili else 'Enerjili'} listesinde (yapıyla çelişiyor)")
        m = re.match(r"^(F\d)\b", d["p12"])
        if m and d["eleman"] != m.group(1):
            h.append(f"dal {ad}: §12 öğesi '{d['p12']}' {m.group(1)}'den, dalın elemanı {d['eleman']}")
        if re.match(r"^F\d$", d["eleman"]) and not m:
            h.append(f"dal {ad}: elemanı sigorta {d['eleman']}, §12 öğesi '{d['p12']}' o sigortayı adıyla anmıyor "
                     f"(öğe '{d['eleman']} …' ile başlamalı)")
    # blok şeması: sigorta kutusu ana anahtardan sonra; her F sigortası kutunun girişinden; şemada bir sigortanın bloğunda geçen
    # eleman o sigortanın çıkışından beslenir
    bloklar, ilk, hb = blok_sema(b["elektrik"])
    h += hb
    if "ana anahtar ── sigorta kutusu" not in ilk:
        h.append("blok şemasının ilk satırında 'ana anahtar ── sigorta kutusu' yok (kutu girişi okunamadı)")
    kutu = v["anahtarlar"].get("ana-anahtar", {}).get("cikis", [None])[0]
    for f in bloklar:
        e = v["koruyucular"].get(f)
        if e is None:
            if f not in SIGORTA_LISTESI_YUKSUZ:
                h.append(f"blok şemasındaki {f} koruyucular tablosunda yok")
        elif e["giris"] != kutu:
            h.append(f"{f}: girişi '{e['giris']}', blok şemasında sigorta kutusunda (ana anahtar sonrası, '{kutu}')")
    for x in blok_karsilastir(v, b["elektrik"]):
        h.append(x)
    for r in v["kablolar"]:
        try:
            z = kablo_zinciri(v, r)
        except ValueError as x:
            h.append(f"{r['kimlik']}: besleme zinciri kurulamadı: {x}")
            continue
        if r["besleme_zinciri"] != z:
            h.append(f"{r['kimlik']}: besleme_zinciri kayıtta {r['besleme_zinciri']}, devreden {z}. {YON}")
        dal = zincir_dali(v, z)
        if r["dal"] != dal:
            h.append(f"{r['kimlik']}: dal '{r['dal']}', besleme zincirinden '{dal}'")
        enj = zincir_enerjili(v, z)
        if r["acil_stopta_enerjili"] is not enj:
            h.append(f"{r['kimlik']}: acil_stopta_enerjili {r['acil_stopta_enerjili']}, besleme zincirine göre "
                     f"{'enerjili' if enj else 'enerjisiz'} ({' → '.join(map(str, z))})")
    return h


def kaynak_coz(s, terimler=None):
    """'yol:satır', 'yol:a-b' ya da 'yol#anahtar.yolu' -> hata metni ya da None. terimler verilirse hedef metinde biri aranır."""
    if "#" in s:
        yol, anahtar = s.split("#", 1)
        p = KOK / yol
        if not p.is_file():
            return f"dosya yok: {yol}"
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return f"json okunamadı: {yol}"
        for parca in anahtar.split("."):
            if isinstance(d, list) and parca.isdigit() and int(parca) < len(d):
                d = d[int(parca)]
            elif isinstance(d, dict) and parca in d:
                d = d[parca]
            else:
                return f"anahtar yok: {s}"
        metin = json.dumps(d, ensure_ascii=False)
    else:
        m = re.match(r"(.+?):(\d+)(?:-(\d+))?$", s)
        if not m:
            return f"biçim 'belge:satır' değil: {s}"
        p = KOK / m.group(1)
        if not p.is_file():
            return f"dosya yok: {m.group(1)}"
        satir = p.read_text(encoding="utf-8").splitlines()
        son = int(m.group(3) or m.group(2))
        if not 1 <= int(m.group(2)) <= son <= len(satir):
            return f"satır dışı: {s} (dosya {len(satir)} satır)"
        metin = "\n".join(satir[int(m.group(2)) - 1:son])
    if terimler:
        km = " ".join(re.findall(r"[0-9a-zçğıöşüµω]+", kucuk(metin)))
        tok = set(km.split())

        def es(t, x):   # sözcük eşleşmesi; ortak kök (kısa olan ≥ 5 harf) Türkçe eki tolere eder
            return t == x or (min(len(t), len(x)) >= 5 and (x.startswith(t) or t.startswith(x)))
        if not any((" " in t and f" {t} " in f" {km} ") or (" " not in t and any(es(t, x) for x in tok)) for t in terimler):
            return f"ilgisiz satır: {s} (kablonun ayırt edici terimlerinden hiçbiri yok: {', '.join(sorted(terimler)[:8])} …)"
    return None


def kucuk(x):
    return x.replace("İ", "i").replace("I", "ı").lower()


def terim(x):
    """Ayırt edici terimler: genel sözcükler (DUR_SOZ) ve çıplak sayılar dışarıda; kimlik / parça adı / sigorta kimliği kalır."""
    return {t for t in re.findall(r"[0-9a-zçğıöşü]+", kucuk(x))
            if t not in DUR_SOZ and not t.isdigit() and (len(t) >= 3 or (any(c.isdigit() for c in t) and len(t) >= 2))}


GENEL_IFADE = {"sigorta kutusu"}


def ifade(x):
    """Parça adı ifadesi (çok sözcüklü bileşen adı: 'ana anahtar', 'yıldız barası'): parantez içi atılır."""
    x = re.sub(r"\([^()]*\)", " ", x)
    f = " ".join(re.findall(r"[0-9a-zçğıöşüµω]+", kucuk(x)))
    return {f} if " " in f and f not in GENEL_IFADE else set()


def kablo_terimleri(v, r):
    t = terim(r["kimlik"]) | terim(r["ad"]) | terim(r["devre"])
    for d in r["damarlar"]:
        t |= terim(d["a"]) | terim(d["b"]) | terim(d["ad"])
        for u in (d["a"], d["b"]):
            t |= ifade(v["dugumler"].get(u, {}).get("parca", ""))
    t |= ifade(r["uc_a"].get("parca", "")) | ifade(r["uc_b"].get("parca", ""))
    if any(v["yildiz_noktasi"] in (d["a"], d["b"]) for d in r["damarlar"]):
        t.add("yıldız noktası")          # belgelerdeki adı (elektrik.md blok şeması 'Toprak:' satırı)
    if r.get("koruma"):
        t |= terim(r["koruma"]) | terim(v["koruyucular"].get(r["koruma"], {}).get("ad", ""))
    return t


def s_kaynak(v, b):
    h = []
    for r in v["kablolar"]:
        if not r.get("kaynak"):
            h.append(f"{r['kimlik']}: kaynak yok")
        te = kablo_terimleri(v, r)
        for s in r.get("kaynak", []):
            e = kaynak_coz(s, te)
            if e:
                h.append(f"{r['kimlik']}: {e}")
        if r.get("boy"):
            e = kaynak_coz(r["boy"]["kaynak"])
            if e:
                h.append(f"{r['kimlik']}: boy kaynağı: {e}")
    for t in v["kesit_kurali"]["tablo"]:
        e = kaynak_coz(t["kaynak"])
        if e:
            h.append(f"kesit_kurali {t['awg']} AWG: {e}")
    for kid, e in elemanlar(v).items():
        x = kaynak_coz(e["kaynak"], terim(kid) | terim(e["ad"]) | ifade(e["ad"].split("(")[0]) |
                       set(re.findall(r"\d+ (?:kω|ω|µf|mf)", kucuk(e["ad"]))))
        if x:
            h.append(f"eleman {kid}: {x}")
    for bad, x in v["kesit_kurali"]["ortam"]["bolgeler"].items():
        e = kaynak_coz(x["kaynak"])     # sıcaklığın kendisi kesit sınamasında kaynak satırından okunur (BOLGE_KALIBI)
        if e:
            h.append(f"bölge {bad}: {e}")
    return h


def s_denetim_62(v, b):
    gorulen = set(v["denetim_62_disarida"])
    for r in v["kablolar"]:
        if not r["denetim_62"]:
            return [f"{r['kimlik']}: denetim_62 boş (döküm karşılığı ya da 'yeni')"]
        for n in r["denetim_62"]:
            m = re.match(r"#(\d+)", n)
            if m:
                gorulen.add(f"#{m.group(1)}")
    eksik = [f"#{i}" for i in range(1, 63) if f"#{i}" not in gorulen]
    return [f"dökümün şu satırları eşlenmedi: {', '.join(eksik)}"] if eksik else []


def s_gorunum(v, b):
    if b["gorunum"] is None:
        return ["kablolar.md yok"]
    h = [] if kablolar_uret.uret(v, b["maliyet"]) == b["gorunum"] else [
        "kablolar.md tabloyla güncel değil: py -3 planlama/adim3/kablolar_uret.py"]
    el = b["elektrik"]
    if kablolar_uret.elektrik_yaz(el, v) != el:
        h.append("elektrik.md'deki dal başına kesit bloğu tabloyla güncel değil: py -3 planlama/adim3/kablolar_uret.py")
    return h


def s_sayi_metin(v, b):
    """Kablo metinlerindeki sayılar (D3 kalıcı çaresi; ek tur D-B). Sınanan alanlar: ad, kesit_not, not, sonlandırma, damar ara / not.
    'N A' yalnız kablonun kendi koruyucularının (besleme zinciri + koruma + ara koruyucu) akımı olabilir; kesit_not / not'ta ayrıca
    kablonun kendi kesit sınırları ve istisnasının üst sınırı. Metinde adıyla anılan koruyucunun sayısı ('F4 5 A', 'ana sigorta
    30 A', 'XL4016 çevre 10 A', 'BMS 30 A') o koruyucuyla aynı olmalı (komşu koruyucu yalnız adıyla anılabilir). 'N AWG' kablonun
    kesiti ya da uç kuyruğu. Tarihçe sayıları sınanmayan 'tarihce' alanında."""
    h = []
    KR = v["koruyucular"]
    istisna = {i["ad"]: i for i in v["kesit_kurali"].get("istisnalar", [])}
    AD = re.compile(r"(?P<ad>\bF[1-6]|[Aa]na sigorta(?: yuvası)?|\bBMS|XL4016 (?:A|B|C|çevre)|hat-[\wçğıöşü]+)\s+(?P<n>\d+(?:,\d+)?) A\b")

    def ad_kid(x):
        if re.match(r"^F[1-6]$", x):
            return x
        if x.casefold().startswith("ana sigorta"):
            return "ana-sigorta"
        if x == "BMS":
            return "aku-bms"
        if x.startswith("XL4016 "):
            return "XL4016-" + x.split()[1].replace("çevre", "cevre")
        return x

    for r in v["kablolar"]:
        izin = set()
        for x in list(duz(r["besleme_zinciri"])) + [r["koruma"]] + [d.get("ara_koruyucu") for d in r["damarlar"]]:
            if x in KR and KR[x]["akim_a"] is not None:
                izin.add(KR[x]["akim_a"])
        awgs = {(d.get("kesit") or r.get("kesit") or {}).get("awg") for d in r["damarlar"]} - {None}
        kuyruk = {x.get("awg") for d in r["damarlar"] for x in (d.get("uc_kuyrugu") or {}).values()}
        if any(d.get("ara_koruyucu") and KR.get(d["ara_koruyucu"], {}).get("tur") == "sigorta" for d in r["damarlar"]):
            kuyruk.add(HAT_YUVASI_KUYRUK_AWG)
        sinir = set()
        for aw in awgs:
            _, _, _, s_ = kablolar_uret.kablo_siniri(v, dict(r, kesit={"awg": aw}))
            if s_ is not None:
                sinir.add(s_)
            sinir |= {t["en_cok_koruma_a"] for t in v["kesit_kurali"]["tablo"] if t["awg"] == aw}
        if r.get("kesit_istisna") in istisna:
            sinir |= {x.get("ust_sinir_a") for x in (istisna[r["kesit_istisna"]].get("koruyucular") or {}).values()}
        alanlar = [("ad", r.get("ad"), izin), ("kesit_not", r.get("kesit_not"), izin | sinir), ("not", r.get("not"), izin | sinir),
                   ("sonlandirma", r.get("sonlandirma"), izin)]
        for d in r["damarlar"]:
            alanlar += [(f"{d['ad']} ara", d.get("ara"), izin), (f"{d['ad']} not", d.get("not"), izin | sinir)]
        for alan, x, iz in alanlar:
            x = x or ""
            if not isinstance(x, str):
                continue
            adli = []
            for mm in AD.finditer(x):
                kid = ad_kid(mm.group("ad"))
                adli.append(mm.span("n"))
                if kid not in KR:
                    h.append(f"{r['kimlik']}: {alan} '{x[:60]}' adıyla andığı '{mm.group('ad')}' koruyucular tablosunda yok")
                elif KR[kid]["akim_a"] != tr_sayi(mm.group("n")):
                    h.append(f"{r['kimlik']}: {alan} '{x[:60]}' {mm.group('ad')} {mm.group('n')} A diyor, koruyucular.{kid} "
                             f"{KR[kid]['akim_a']} A")
            for mm in re.finditer(r"(?<![\w,.])" + SAYI + r" A(?:'[a-zçğıöşü]+)?\b", x):
                if any(a_ <= mm.start(1) < b_ for a_, b_ in adli):
                    continue
                n = tr_sayi(mm.group(1))
                if not any(abs(n - y) < 1e-9 for y in iz if y is not None):
                    h.append(f"{r['kimlik']}: {alan} '{x[:60]}' {mm.group(1)} A diyor; kablonun kendi koruyucuları"
                             f"{' / sınırları' if iz is not izin else ''} {sorted(y for y in iz if y is not None)} (komşu koruyucu "
                             f"yalnız adıyla anılır; tarihçe 'tarihce' alanına)")
            for n in re.findall(r"(\d+) AWG", x):
                if int(n) not in awgs | kuyruk:
                    h.append(f"{r['kimlik']}: {alan} '{x[:60]}' {n} AWG diyor; kaydın kesiti {sorted(awgs)}, uç kuyruğu {sorted(kuyruk)}")
        metinler = [r["uc_a"].get("parca", ""), r["uc_a"].get("nokta", ""), r["uc_b"].get("parca", ""), r["uc_b"].get("nokta", "")] + [
            x for d in r["damarlar"] for x in (d["a"], d["b"])]
        for x in metinler:
            for mm in AD.finditer(x):
                kid = ad_kid(mm.group("ad"))
                if kid in KR and KR[kid]["akim_a"] != tr_sayi(mm.group("n")):
                    h.append(f"{r['kimlik']}: metin '{x[:50]}' {mm.group('ad')} {mm.group('n')} A diyor, koruyucular.{kid} {KR[kid]['akim_a']} A")
    return h


SINAMALAR = [("alanlar", s_alanlar), ("iki_uc", s_iki_uc), ("yer_tutucu", s_yer_tutucu), ("ag", s_ag),
             ("koruyucu", s_koruyucu), ("ayni_nokta", s_ayni_nokta), ("esp32_pin", s_esp32_pin),
             ("pca_kanal", s_pca_kanal), ("kesit", s_kesit), ("donus", s_donus), ("tahmin", s_tahmin), ("klemens", s_klemens),
             ("malzeme", s_malzeme), ("donanim", s_donanim), ("acil_stop", s_acil_stop), ("kaynak", s_kaynak),
             ("sayi_metin", s_sayi_metin), ("denetim_62", s_denetim_62), ("gorunum", s_gorunum)]


def kos(v, b):
    out = {}
    for ad, f in SINAMALAR:
        try:
            out[ad] = f(v, b)
        except (KeyError, TypeError, ValueError, AttributeError, StopIteration) as x:
            out[ad] = [f"sınama çalışamadı ({type(x).__name__}: {x})"]
    return out


# ---------------------------------------------------------------- bilerek bozma
def bul(v, kimlik):
    return next(r for r in v["kablolar"] if r["kimlik"] == kimlik)


def damar(r, ad):
    return next(d for d in r["damarlar"] if d["ad"] == ad)


def b_iki_uc(v, b):
    bul(v, "G02")["uc_b"]["nokta"] = ""
    damar(bul(v, "U01"), "USB")["b"] = " "


def b_ayni_nokta(v, b):
    damar(bul(v, "B02"), "IN1 (ileri PWM)")["b"] = "BTS7960 sol · IN1"     # sağ kartın IN1 teli sol kartın IN1 klemensine


def b_esp32_pin(v, b):
    d = damar(bul(v, "X01"), "röle K1 sürüşü")
    d["gpio"], d["b"] = 12, "ESP32 · GPIO12"                              # röle eski strapping pinine
    v["dugumler"]["ESP32 · GPIO12"] = {"parca": "ESP32", "ag": None, "gpio": 12}


def b_esp32_pin_2(v, b):
    d = damar(bul(v, "N02"), "A")
    d["gpio"], d["b"] = 15, "ESP32 · GPIO15"                              # iki enkoder kanalı aynı pine


def b_pca_kanal(v, b):
    for r in ("P01", "S02"):
        d = next(d for d in bul(v, r)["damarlar"] if d.get("pca_kanal") == 1)
        d["pca_ad"] = "sag_dirsek"                                          # K1'e yanlış eklem adı


def b_pca_kanal_2(v, b):
    b["kanallar"] = dict(b["kanallar"], sol_bilek=9, kafa_tilt=8)          # main'de kanal değişti, tablo eski


def b_kesit(v, b):
    v["koruyucular"]["F3"]["akim_a"] = 10                                 # 18 AWG kafa çiftine 10 A sigorta (tek kaynaktan)


def b_kesit_2(v, b):
    del bul(v, "G03")["kesit_istisna"]                                    # 12 AWG 30 A ile, istisna kaydı olmadan


def b_kesit_3(v, b):
    v["kesit_kurali"]["istisnalar"][0]["gerekce"] = ""                    # istisna gerekçesiz


def b_kesit_4(v, b):
    bul(v, "G18")["kesit_istisna"] = "servo-uzatmasi"                     # başka kablo sessizce istisnaya


def b_kesit_5(v, b):
    next(t for t in v["kesit_kurali"]["tablo"] if t["awg"] == 16)["en_cok_koruma_a"] = 15   # temkinli olmayan değer


def b_kesit_6(v, b):
    next(i for i in v["kesit_kurali"]["istisnalar"] if i["ad"] == "ana-hat-12awg")["sart"] = ""   # şartsız istisna


def b_kesit_7(v, b):
    bul(v, "G08")["kesit_istisna"] = "ana-hat-12awg"                      # kapsam dışı kabloya istisna


def b_kesit_8(v, b):
    v["koruyucular"]["hat-sarj"]["akim_a"] = 10                           # şarj sigortası eski 10 A: 16 AWG 45 °C'de 8,2 A


def b_kesit_9(v, b):
    r = bul(v, "G18")
    r["bolge"] = "kafa"                                                   # kafada 18 AWG + F4 5 A: 5,25 A geçer; …
    v["koruyucular"]["F4"]["akim_a"] = 5.5                                # … 5,5 A'lik sigortayı ortam düzeltmesi yakalar


def b_kesit_10(v, b):
    v["koruyucular"]["hat-cevre"]["akim_a"] = 3                           # çevre hat sigortası 3 A: 22 AWG 45 °C'de 2,46 A


def b_kesit_11(v, b):
    d = damar(bul(v, "G19"), "+5 V")                                      # çevre hat sigortası kaldırıldı: koruma yine
    d.pop("ara_koruyucu")                                                 # 'hat-cevre' yazılı, devreden XL4016-cevre
    d.pop("ara_uc")


def b_kesit_12(v, b):
    i = next(i for i in v["kesit_kurali"]["istisnalar"] if i["ad"] == "servo-ana-hat-16awg")
    i["beklenen_akim_a"]["hatlar"][0]["tepe_a"] = 9.0                     # SV1 tepe akımı 16 AWG'nin 8,2 A'inin üstünde


def b_kesit_13(v, b):
    i = next(i for i in v["kesit_kurali"]["istisnalar"] if i["ad"] == "servo-ana-hat-16awg")
    i["beklenen_akim_a"]["hatlar"][2]["duzeltilmis_sinir_a"] = 8.2        # SV3 kafada (7,5 A), etek sınırı yazıldı


def b_kesit_15(v, b):
    b_ = v["koruyucular"]["hat-cevre"]["yuk_butcesi"]
    b_["kalemler"][0]["tepe_a"] = 1.9                                     # ESP32 tepesi büyüdü, toplam güncellenmedi
    b_["kalemler"][0]["tipik_a"] = 1.9


def b_kesit_16(v, b):
    b_ = v["koruyucular"]["hat-cevre"]["yuk_butcesi"]
    b_["kalemler"][0]["tepe_a"] += 1.5                                    # tepe 2,1 A: 2 A sigorta atar (toplam tutarlı)
    b_["toplam_tepe_a"] += 1.5


def b_kesit_14(v, b):
    del bul(v, "SV2")["kesit_istisna"]                                    # istisna kapsamındaki kablo istisnayı taşımıyor


def b_tahmin(v, b):
    bul(v, "G03")["boy_tahmin"]["mm"] = 300                               # uçlarla tutmayan tahmin


def b_tahmin_2(v, b):
    bul(v, "G04")["boy"] = {"yol_mm": 300, "kaynak": "planlama/adim3/elektrik.md:70"}   # ölçüm geldi, tahmin silinmedi


def b_tahmin_3(v, b):
    bul(v, "G08")["boy_tahmin"]["etiket"] = "ölçüldü"                    # tahmin ölçüm gibi etiketlendi


def b_tahmin_4(v, b):
    del bul(v, "G09")["boy_tahmin"]                                       # boy da tahmin de yok


def b_tahmin_5(v, b):
    v["boy_tahmin_kurali"]["pay_mm"] = 150                                # kural değişti, tahminler eski


def b_klemens(v, b):
    damar(bul(v, "G05"), "−")["uc_turu"]["b"] = "wago-2273"                # 12 AWG, 2,5 mm²'lik klemense


def b_klemens_2(v, b):
    damar(bul(v, "G11"), "+")["uc_turu"]["a"] = "klemens-508"              # 12 AWG, sınırı bilinmeyen 5,08 klemense


def b_klemens_3(v, b):
    v["klemens_turleri"]["bara-pabuc"]["dugumler"]["Yıldız barası · GND"] = 3   # 11 iletkene üç saplama (4'er pabuç)


def b_klemens_4(v, b):
    v["klemens_turleri"]["bara-pabuc"]["saplama_basina_en_cok_pabuc"] = 5      # ABYC sınırı aşıldı


def b_klemens_5(v, b):
    r = bul(v, "G12")
    r["teyit"] = [t for t in r["teyit"] if not t.startswith("klemens:")]       # BTS klemensi teyitsiz 12 AWG


def b_malzeme(v, b):
    i = v["malzeme_turleri"]["silikon-18"]["maliyet"]["kırmızı"]
    b["maliyet"]["kalemler"][i]["adet"] = 7                               # sipariş eski adette kaldı


def b_malzeme_3(v, b):
    v["klemens_turleri"]["bara-pabuc"]["kopruler"]["Yıldız barası · GND"]["boy_mm"] = 400   # köprü metresi listeyi aşar


def b_klemens_6(v, b):
    v["klemens_turleri"]["bara-pabuc"]["kopruler"]["Yıldız barası · GND"]["adet"] = 3       # 5 saplama 4 köprü ister


def b_malzeme_2(v, b):
    bul(v, "G21")["malzeme"] = "silikon-14"                              # tanımsız tür


def b_acil_stop(v, b):
    bul(v, "G21")["acil_stopta_enerjili"] = False                         # göğüs ekranı (F6) acil stopta kapalı yazıldı


def b_acil_stop_2(v, b):
    b["p12"] = b["p12"].replace("F6 göğüs ekranı dalı", "göğüs ekranı")  # §12 değişti


def b_acil_stop_3(v, b):
    v["anahtarlar"]["K1-kontak"]["tur"] = "anahtar"                       # K1 kontağı acil stopta açılmaz diye yazıldı
    v["anahtarlar"]["K2-kontak"]["tur"] = "anahtar"


def b_acil_stop_4(v, b):
    bul(v, "G17")["besleme_zinciri"] = ["aku-bms", "ana-sigorta", "ana-anahtar", "F4"]   # zincir elle değişti


def b_acil_stop_5(v, b):
    b["p12"] = b["p12"].replace("K1 / K2 kontağından sonraki anahtarlı bara", "K1 / K2 kontağından sonraki bara")
    b["p12"] = b["p12"].replace("**Enerjili:** akü", "**Enerjili:** anahtarlı bara; akü")    # bara enerjili listeye taşındı


def b_kaynak(v, b):
    bul(v, "H02")["kaynak"] = []


def b_kaynak_2(v, b):
    bul(v, "G17")["kaynak"][0] = "planlama/adim3/elektrik.md:9999"


def b_kaynak_3(v, b):
    v["koruyucular"]["F3"]["kaynak"] = "planlama/adim3/elektrik.md:1"    # koruyucunun kaynağı ilgisiz satır


def b_alanlar(v, b):
    bul(v, "U04")["eksik"] = ["deneme"]                                   # eksik var ama durum değişmedi


def b_alanlar_2(v, b):
    bul(v, "G16")["devre"] = "sinyal (zayıf)"                             # izinli listede olmayan devre türü


def b_denetim_62(v, b):
    bul(v, "S01")["denetim_62"] = ["yeni"]                                # #22 karşılıksız kaldı


def b_gorunum(v, b):
    bul(v, "C01")["ad"] += " (değişti)"                                   # tablo değişti, görünüm üretilmedi


def b_gorunum_2(v, b):
    b["elektrik"] = b["elektrik"].replace("| G08 |", "| G08 (elle) |")      # elektrik.md bloğu elle değiştirildi


def b_ag(v, b):
    v["anahtarlar"]["kopru"] = {"ad": "deneme köprüsü", "tur": "gecis", "giris": "5v-pi", "cikis": ["5v-cevre"], "kaynak": "x:1"}


def b_ag_2(v, b):
    damar(bul(v, "G17"), "+")["b"] = "D24V50F5 · VOUT (P6KE6V8A)"          # 12 V tel 5 V Pi düğümüne


def b_ag_3(v, b):
    v["dugumler"]["XL4016 A · OUT+"]["ag"] = None                         # güç düğümünün ağı silindi


def b_ag_4(v, b):
    damar(bul(v, "G14"), "+")["ara_koruyucu"] = "hat-B"                   # yanlış hat sigortası (çıkışı XL4016 B)


def b_donus(v, b):
    bul(v, "G03")["ortak_donus"] = ["G22"]                                # 12 AWG'nin dönüşü 22 AWG kabloya yazıldı


def b_donus_2(v, b):
    v["ic_baglar"] = [x for x in v["ic_baglar"] if "#1" not in x["a"]]    # K1 bobininin dönüş yolu kayboldu


def b_donus_3(v, b):
    del bul(v, "M01")["damarlar"][1]                                      # motor kablosunun M− damarı silindi


def b_yer_tutucu(v, b):
    bul(v, "P01")["sonlandirma"] = "3 pinli köprü (öneri)"                 # kesin kayıtta öneri


# düzeltme turu 2: yeni sınamaların bozmaları ve ikinci kontrolün (P107a-kontrol-2.md) kaçan bozmalarından seçilenler
def kalem(b, kosul):
    return next(i for i, x in enumerate(b["maliyet"]["kalemler"]) if kosul(x))


def b_koruyucu(v, b):
    b["elektrik"] = b["elektrik"].replace("| F4 | 5 A standart |", "| F4 | 10 A standart |")     # belge değişti, tablo eski


def b_koruyucu_2(v, b):
    e = v["koruyucular"]["hat-C"]                                          # 5 → 7,5 A, sipariş de 7,5 A satırına
    e["akim_a"], e["siparis"], e["ad"] = 7.5, 88, "Hat sigortası C 7,5 A mini (XL4016 C girişi)"


def b_koruyucu_3(v, b):
    e = v["koruyucular"]["ana-sigorta"]                                    # N8c, adı da tutarlı 40 A
    e["akim_a"], e["ad"] = 40, e["ad"].replace("30 A", "40 A")


def b_koruyucu_4(v, b):
    v["koruyucular"]["D24V50F5"]["akim_a"] = 5                             # belgesiz sınıra sayı


def b_koruyucu_5(v, b):
    b["maliyet"]["kalemler"][v["koruyucular"]["ana-sigorta"]["siparis"]]["model"] = "40 Amper Oto Sigorta - Bıçak Sigorta"


def b_koruyucu_6(v, b):
    v["koruyucular"]["F5"]["bicak"] = "mini"                               # kutu standart bıçak alır


def b_kesit_17(v, b):
    r = bul(v, "G18")                                                      # N9d: F4 arkası 22 AWG kafa 5 V istisnasına
    r["kesit"], r["kesit_istisna"] = {"awg": 22, "mm2": 0.33}, "kafa-5v-donusturucu-arkasi"
    next(i for i in v["kesit_kurali"]["istisnalar"] if i["ad"] == "kafa-5v-donusturucu-arkasi")["kapsam"].append("G18")


def b_kesit_18(v, b):
    next(i for i in v["kesit_kurali"]["istisnalar"] if i["ad"] == "ana-hat-12awg")["kapsam"].append("G08")   # N9c
    bul(v, "G08")["kesit_istisna"] = "ana-hat-12awg"


def b_kesit_19(v, b):
    t = next(t for t in v["kesit_kurali"]["tablo"] if t["awg"] == 16)     # dayanak tutarlı biçimde değişti (kaynaktan farklı)
    t["dayanak"]["nfpa79"], t["en_cok_koruma_a"] = 15, 15


def b_kesit_20(v, b):
    v["kesit_kurali"]["ortam"]["katsayilar"][1]["k"] = 0.95                # ortam katsayısı kaynaktan farklı


def b_kesit_21(v, b):
    v["klemens_turleri"]["bara-pabuc"]["kopruler"]["Yıldız barası · GND"]["besleme_saplamasi"] = 1   # akü dönüşü uçta


def b_kesit_22(v, b):
    for x in v["kesit_kurali"]["istisnalar"][0]["koruyucular"].values():  # istisnanın en ince kesiti kararla tutmuyor
        x["en_ince_awg"] = 24
    bul(v, "S01")["kesit"] = {"awg": 24, "mm2": 0.2}


def b_acil_stop_6(v, b):
    r = bul(v, "G18")                                                      # N1b: çevre dalı tutarlı biçimde F3'e
    damar(r, "+")["a"] = "Sigorta kutusu · F3 çıkışı"
    v["ortak_noktalar"].append("Sigorta kutusu · F3 çıkışı")
    v["dugumler"]["XL4016 çevre · IN+"]["ag"] = "f3-cikis"
    v["koruyucular"]["XL4016-cevre"]["giris"] = "f3-cikis"
    for x in v["kablolar"]:
        x["besleme_zinciri"] = ["F3" if e == "F4" else e for e in x["besleme_zinciri"]]
        x["dal"] = "F3" if x["dal"] == "F4" else x["dal"]
        x["koruma"] = "F3" if x["koruma"] == "F4" else x["koruma"]


def b_acil_stop_7(v, b):
    v["koruyucular"]["F6"]["giris"] = "anahtarli-bara"                     # N2c: F6 röle arkasına, p12 öbür listenin ifadesi
    for k in ("G20", "G21"):
        r = bul(v, k)
        r["acil_stopta_enerjili"] = False
        r["besleme_zinciri"] = ["aku-bms", "ana-sigorta", "ana-anahtar", "F1", ["K1-kontak", "K2-kontak"], "F6"] + (
            ["gogus-regulatoru"] if k == "G21" else [])
    v["dallar"]["F6"]["p12"] = "anahtarlı bara"


def b_acil_stop_8(v, b):
    v["dallar"]["F4"]["p12"] = "akü"                                       # N16: Enerjili listesinin kısa ifadesi


def b_ag_5(v, b):
    v["ic_baglar"].append({"a": "D24V50F5 · VOUT (P6KE6V8A)", "b": "Arayüz kartı · çevre 5 V", "ne": "deneme"})   # N4b


def b_yer_tutucu_2(v, b):
    bul(v, "G17")["uc_b"]["nokta"] = "?"                                   # B5c: teyit kaydında uç '?'


def b_yer_tutucu_3(v, b):
    bul(v, "G18")["sonlandirma"] = "sonra bakılacak"                       # N5c


def b_klemens_7(v, b):
    bul(v, "G10")["sonlandirma"] = "F1 ucu sigorta kutusu çıkış klemensi; ön şarj kartı ucu: 2 pin 5,08 mm vidalı klemens"   # N7c


def b_klemens_8(v, b):
    v["klemens_turleri"]["klemens-508"]["en_cok_mm2"] = 4.0               # N7b: sınır kaynaksız büyütüldü
    damar(bul(v, "G11"), "+")["uc_turu"]["a"] = "klemens-508"


def b_klemens_9(v, b):
    r = bul(v, "G08")                                                      # sigorta kutusu ucu 'lehim', teyit silindi
    damar(r, "+")["uc_turu"]["a"] = "lehim"
    r["teyit"] = [t for t in r["teyit"] if not t.startswith("klemens:")]


def b_donanim(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: x["ad"].startswith("Hat sigortası yuvası"))]["adet"] = 3   # N11c


def b_donanim_2(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: x["ad"].startswith("Bara saplaması"))]["adet"] = 2        # N11d


def b_donanim_3(v, b):
    del v["anahtarlar"]["K1-bobin"]["geri_tepme_diyodu"]                  # N14 (yapısal alan)


def b_donanim_4(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: "1N4007" in x["model"])]["adet"] = 2   # yedek yok


def b_donanim_5(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: x["ad"].startswith("Halka pabuç 12 AWG"))]["adet"] = 1


def b_kaynak_4(v, b):
    bul(v, "G18")["kaynak"] = ["planlama/adim3/elektrik.md:5"]             # N10a: genel giriş paragrafı


def b_sayi_metin(v, b):
    bul(v, "G06")["ad"] = "Şarj kolu: akü + → 10 A hat sigortası → XT60E-M şarj girişi (+ / −)"   # D3'teki eski ad


def b_sayi_metin_2(v, b):
    bul(v, "K03")["kesit_not"] = "20 AWG (EL:279): D24V50F5 5 A ≤ 20 AWG'nin 5 A'i, sınırda"     # D3'teki eski not


def b_alanlar_3(v, b):
    bul(v, "G05")["klemensler"] = [{"uc": "b", "tur": "wago-2273"}]       # eski alan adı (denetim okumaz)


# ek tur (üçüncü bakış P107a-kontrol-3.md): kaçan bozmalarından seçilenler ve her yeni sınama için bozma
def zincir_yenile(v):
    """Yalnız tabloyu düzenleyen dikkatli kişi: zincir / dal / acil stop bayrağı / koruma denetimin kendi işlevleriyle yeniden."""
    for r in v["kablolar"]:
        z = kablo_zinciri(v, r)
        r["besleme_zinciri"], r["dal"], r["acil_stopta_enerjili"] = z, zincir_dali(v, z), zincir_enerjili(v, z)
        g = guc_damarlari(v, r)
        r["koruma"] = max((x[2] for x in g), key=lambda i: akim(v, i)) if g else None


def f1_oncesi(v, kid, kab):
    v["koruyucular"][kid]["giris"] = "f1-cikis"
    r = bul(v, kab)
    damar(r, "+")["a"] = "Sigorta kutusu · F1 çıkışı"
    damar(r, "+")["uc_turu"]["a"] = "sigorta-kutusu"
    r["uc_a"] = {"parca": "Sigorta kutusu", "nokta": "F1 çıkışı"}
    if (r.get("kesit") or {}).get("awg", 99) <= 12:
        r["teyit"] = list(r["teyit"]) + ["klemens: sigorta kutusu F1 çıkış ucunun 12 AWG alıp almadığı teslimde"]
        r["durum"] = "kablajda teyit edilecek"
    zincir_yenile(v)


def b_blok(v, b):
    f1_oncesi(v, "hat-A", "G14")                                           # T40b: XL4016 A röle öncesine, tutarlı


def b_blok_2(v, b):
    v["dugumler"]["BTS7960 sol · B+"]["ag"] = "f1-cikis"                   # T42c: BTS sol röle öncesine, tam tutarlı
    f1_oncesi(v, "BTS7960-sol", "G12")


def b_blok_3(v, b):
    f1_oncesi(v, "hat-G22", "G22")                                         # T41b: bara algısı röle öncesine


def b_blok_4(v, b):
    b["elektrik"] = b["elektrik"].replace("├─ 7,5 A ── XL4016 A 6 V", "├─ 10 A ── XL4016 A 6 V")   # belge değişti, tablo eski


def b_blok_5(v, b):
    b["elektrik"] = b["elektrik"].replace("└─ 2 A mini (O-18 b) ── PC817 #2", "└─ PC817 #2")    # şemada yuvası yok


def b_sayi_metin_3(v, b):
    bul(v, "G22")["ad"] = "Anahtarlı bara → 7,5 A hat sigortası → PC817 #2 girişi (bara durumu)"   # T44: komşunun değeri


def b_sayi_metin_4(v, b):
    bul(v, "G19")["not"] = "Koruyan XL4016 çevre 8 A sınırı; 16 AWG yeter."                       # T28: not alanı


def b_sayi_metin_5(v, b):
    damar(bul(v, "G06"), "+")["ara"] = "10 A mini hat sigortası yuvası (16 AWG kuyruklu)"         # T30: damar ara


def b_sayi_metin_6(v, b):
    damar(bul(v, "G22"), "−")["not"] = "dönüş F4 10 A ile aynı saplamada"                          # damar notu, adıyla komşu


def b_klemens_10(v, b):
    for d in bul(v, "G17")["damarlar"]:                                    # ince telli kablo tek telli WAGO'ya
        d["uc_turu"]["b"] = "wago-2273"


def b_klemens_11(v, b):
    del damar(bul(v, "G22"), "−")["uc_kuyrugu"]                            # 22 AWG kırmızı pabucun alt sınırının altında


def b_klemens_12(v, b):
    damar(bul(v, "A06"), "+")["uc_turu"]["a"] = "klemens-508"              # 22 AWG alt sınırı belgesiz klemense


def b_klemens_13(v, b):
    v["klemens_turleri"]["wago-2273"]["iletken"] = "tek telli / ince telli"   # sözlük kaynaktan farklı


def b_kesit_23(v, b):
    y = v["klemens_turleri"]["bara-pabuc"]["kopruler"]["Yıldız barası · GND"]["yerlesim"]   # BTS sağ dönüşü öbür yana
    y["2"], y["5"] = ["G20/−", "G16/−"], ["G13/−", "G22/−"]


def b_kesit_24(v, b):
    y = v["klemens_turleri"]["bara-pabuc"]["kopruler"]["Yıldız barası · GND"]["yerlesim"]   # akü dönüşü uçta
    y["1"], y["3"] = ["G05/−", "G14/−", "G15/−"], ["G12/−", "G06/−"]


def b_alanlar_4(v, b):
    bul(v, "K01")["kesit"] = {"awg": 12, "mm2": 2.0}                       # T24: mm² AWG ile tutmuyor


def b_koruyucu_7(v, b):
    b["elektrik"] = b["elektrik"].replace("| F4 | 5 A standart |", "| F4 | 5 A standart, sonra 10 A |")   # P06


def b_donanim_6(v, b):
    v["anahtarlar"]["K1-bobin"]["geri_tepme_diyodu"]["yon"] = "katot (bantlı uç) 85'e (bobin −), anot 86'ya (bobin +)"   # T22


def b_donanim_7(v, b):
    dd = v["anahtarlar"]["K2-bobin"]["geri_tepme_diyodu"]                   # yapısal alan ters
    dd["katot_dugumu"], dd["anot_dugumu"] = dd["anot_dugumu"], dd["katot_dugumu"]


def b_donanim_8(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: "BC337-40" in x["model"])]["adet"] = 1            # T34


def b_donanim_9(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: "2200uF" in x["model"])]["adet"] = 4             # T35


def b_donanim_10(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: "5.08mm Klemens" in x["model"])]["adet"] = 2     # T39


def b_donanim_11(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: "2273" in x["model"])].pop("ver")                # WAGO V3'e geri


def b_donanim_12(v, b):
    b["maliyet"]["kalemler"][kalem(b, lambda x: "Delikli Plaket" in x["model"])]["adet"] = 5


# kontrolün (P107a-kontrol.md §1 D1) yakalanmayan on bozması, aynı biçimde
def k_B3(v, b):
    d = damar(bul(v, "X01"), "röle K1 sürüşü")
    d["b"] = "ESP32 · GPIO 12"
    d.pop("gpio")
    d.pop("pin")


def k_B4(v, b):
    r = bul(v, "G18")
    r["damarlar"] = [d for d in r["damarlar"] if d["ad"] != "−"]


def k_B5(v, b):
    damar(bul(v, "S03"), "V+")["b"] = "?"


def k_B6(v, b):
    r = bul(v, "G16")
    r["devre"] = "sinyal"
    r["kesit"] = {"awg": 22, "mm2": 0.33}


def k_B8(v, b):
    r = bul(v, "G12")
    r["dal"], r["acil_stopta_enerjili"] = "F4", True


def k_B9(v, b):
    bul(v, "G17")["koruma"] = "F4"


def k_B10(v, b):
    damar(bul(v, "X01"), "5 V")["a"] = "D24V50F5 · VOUT (P6KE6V8A)"


def k_B11(v, b):
    bul(v, "G08")["kaynak"][0] = "planlama/adim3/elektrik.md:1"


def k_B14(v, b):
    r = bul(v, "SV1")
    r["koruma"] = "hat-G22"
    r["kesit"] = {"awg": 22, "mm2": 0.33}


def k_B15(v, b):
    i = v["malzeme_turleri"]["servo-uzatma"]["maliyet"]["hepsi"]
    b["maliyet"]["kalemler"][i]["adet"] = 230


KONTROL_BOZMALARI = [("B3", k_B3, ("ag", "esp32_pin")), ("B4", k_B4, ("donus",)), ("B5", k_B5, ("ag", "yer_tutucu")),
                     ("B6", k_B6, ("kesit",)), ("B8", k_B8, ("acil_stop",)), ("B9", k_B9, ("kesit",)),
                     ("B10", k_B10, ("ag",)), ("B11", k_B11, ("kaynak",)), ("B14", k_B14, ("kesit",)), ("B15", k_B15, ("malzeme",))]

BOZMALAR = [("iki_uc", b_iki_uc), ("ayni_nokta", b_ayni_nokta), ("esp32_pin", b_esp32_pin), ("esp32_pin", b_esp32_pin_2),
            ("pca_kanal", b_pca_kanal), ("pca_kanal", b_pca_kanal_2), ("kesit", b_kesit), ("kesit", b_kesit_2),
            ("kesit", b_kesit_3), ("kesit", b_kesit_4), ("kesit", b_kesit_5), ("kesit", b_kesit_6), ("kesit", b_kesit_7),
            ("kesit", b_kesit_8), ("kesit", b_kesit_9), ("kesit", b_kesit_10), ("kesit", b_kesit_11),
            ("kesit", b_kesit_12), ("kesit", b_kesit_13), ("kesit", b_kesit_14), ("kesit", b_kesit_15), ("kesit", b_kesit_16),
            ("tahmin", b_tahmin), ("tahmin", b_tahmin_2), ("tahmin", b_tahmin_3), ("tahmin", b_tahmin_4), ("tahmin", b_tahmin_5),
            ("klemens", b_klemens), ("klemens", b_klemens_2), ("klemens", b_klemens_3), ("klemens", b_klemens_4),
            ("klemens", b_klemens_5), ("klemens", b_klemens_6), ("malzeme", b_malzeme), ("malzeme", b_malzeme_2),
            ("malzeme", b_malzeme_3),
            ("acil_stop", b_acil_stop), ("acil_stop", b_acil_stop_2), ("acil_stop", b_acil_stop_3), ("acil_stop", b_acil_stop_4),
            ("acil_stop", b_acil_stop_5), ("kaynak", b_kaynak), ("kaynak", b_kaynak_2), ("kaynak", b_kaynak_3),
            ("alanlar", b_alanlar), ("alanlar", b_alanlar_2), ("denetim_62", b_denetim_62), ("gorunum", b_gorunum),
            ("gorunum", b_gorunum_2), ("ag", b_ag), ("ag", b_ag_2), ("ag", b_ag_3), ("ag", b_ag_4),
            ("donus", b_donus), ("donus", b_donus_2), ("donus", b_donus_3), ("yer_tutucu", b_yer_tutucu),
            # düzeltme turu 2
            ("koruyucu", b_koruyucu), ("koruyucu", b_koruyucu_2), ("koruyucu", b_koruyucu_3), ("koruyucu", b_koruyucu_4),
            ("koruyucu", b_koruyucu_5), ("koruyucu", b_koruyucu_6), ("kesit", b_kesit_17), ("kesit", b_kesit_18),
            ("kesit", b_kesit_19), ("kesit", b_kesit_20), ("kesit", b_kesit_21), ("kesit", b_kesit_22),
            ("acil_stop", b_acil_stop_6), ("acil_stop", b_acil_stop_7), ("acil_stop", b_acil_stop_8), ("ag", b_ag_5),
            ("yer_tutucu", b_yer_tutucu_2), ("yer_tutucu", b_yer_tutucu_3), ("klemens", b_klemens_7), ("klemens", b_klemens_8),
            ("klemens", b_klemens_9), ("donanim", b_donanim), ("donanim", b_donanim_2), ("donanim", b_donanim_3),
            ("donanim", b_donanim_4), ("donanim", b_donanim_5), ("kaynak", b_kaynak_4), ("sayi_metin", b_sayi_metin),
            ("sayi_metin", b_sayi_metin_2), ("alanlar", b_alanlar_3),
            # ek tur
            ("acil_stop", b_blok), ("acil_stop", b_blok_2), ("acil_stop", b_blok_3), ("acil_stop", b_blok_4),
            ("acil_stop", b_blok_5), ("sayi_metin", b_sayi_metin_3), ("sayi_metin", b_sayi_metin_4),
            ("sayi_metin", b_sayi_metin_5), ("sayi_metin", b_sayi_metin_6), ("klemens", b_klemens_10), ("klemens", b_klemens_11),
            ("klemens", b_klemens_12), ("klemens", b_klemens_13), ("kesit", b_kesit_23), ("kesit", b_kesit_24),
            ("alanlar", b_alanlar_4), ("koruyucu", b_koruyucu_7), ("donanim", b_donanim_6), ("donanim", b_donanim_7),
            ("donanim", b_donanim_8), ("donanim", b_donanim_9), ("donanim", b_donanim_10), ("donanim", b_donanim_11),
            ("donanim", b_donanim_12)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="\n".join(__doc__.splitlines()[1:]))
    ap.add_argument("--bozma-denemesi", action="store_true", help="her sınama için bilerek bozulmuş kopyanın yakalandığını da sına")
    ap.add_argument("--kanallar", help="main yerine yerel kanallar.yaml")
    ap.add_argument("--tablo", default=str(TABLO))
    ap.add_argument("--gorunum", default=str(GORUNUM))
    a = ap.parse_args()
    try:
        b = kaynaklari_oku(a)
    except KaynakYok as h:
        print(f"KAYNAK OKUNAMADI: {h}")
        return 2
    v = b["veri"]
    sonuc = kos(v, b)
    kotu = 0
    sayi = Counter(r["durum"] for r in v["kablolar"])
    print(f"kablolar.json: {len(v['kablolar'])} kablo (" + ", ".join(f"{d} {sayi[d]}" for d in DURUMLAR) + ")")
    ist, karar = kesit_ozet(v)
    print(f"  kesit istisnası: {len(ist)} kablo; kesit-koruma kararı bekleyen: {len(karar)} ({', '.join(karar) or '-'})")
    for i in v["kesit_kurali"]["istisnalar"]:
        kk = [r["kimlik"] for r in v["kablolar"] if r.get("kesit_istisna") == i["ad"]]
        print(f"    istisna {i['ad']}: {len(kk)} kablo ({', '.join(kk)}); gerekçe / şart / kontrol / karar dolu: "
              f"{'evet' if all(str(i.get(z, '')).strip() for z in ('gerekce', 'sart', 'kontrol', 'karar')) else 'HAYIR'}")
    tah = sum(1 for r in v["kablolar"] if not r["boy"])
    print(f"  boy: {len(v['kablolar']) - tah} ölçüm / CAD, {tah} tahmin (P10.7b'de ölçülecek)")
    for ad, h in sonuc.items():
        print(f"  {'GEÇER ' if not h else 'GEÇMEZ'} {ad}" + (f" ({len(h)})" if h else ""))
        for x in h[:25]:
            print(f"      - {x}")
        kotu += bool(h)
    if a.bozma_denemesi:
        print("bilerek bozma (bozulmuş kopya; dosyalara yazılmaz):")
        S = dict(SINAMALAR)
        n = 0
        for ad, f in BOZMALAR:
            v2, b2 = copy.deepcopy(v), copy.deepcopy(b)
            f(v2, b2)
            h = kos(v2, b2)[ad]
            print(f"  {'YAKALADI ' if h else 'KAÇIRDI  '} {ad:<11} {f.__name__}: {h[0] if h else '-'}")
            kotu += not h
            n += 1
        print("bağımsız kontrolün kaçan on bozması (P107a-kontrol.md §1 D1):")
        for kod, f, adlar in KONTROL_BOZMALARI:
            v2, b2 = copy.deepcopy(v), copy.deepcopy(b)
            f(v2, b2)
            s2 = kos(v2, b2)
            tutan = [x for x in S if s2[x] and not sonuc[x]]
            beklenen = [x for x in adlar if s2[x]]
            ok = bool(beklenen)
            print(f"  {'YAKALADI ' if ok else 'KAÇIRDI  '} {kod:<4} {', '.join(tutan) or '-'}: "
                  f"{s2[beklenen[0]][0] if beklenen else '-'}")
            kotu += not ok
            n += 1
        print(f"  toplam bozma: {n}")
    print("SONUÇ: " + ("GEÇER" if not kotu else f"GEÇMEZ ({kotu})"))
    return 0 if not kotu else 1


if __name__ == "__main__":
    sys.exit(main())
