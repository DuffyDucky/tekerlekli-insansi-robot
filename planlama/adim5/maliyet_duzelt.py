# -*- coding: utf-8 -*-
"""5. adim (B1, B2, E9, M6 kosullu): planlama/maliyet.json duzeltmesi. Bir kez kosulur (zaten uygulandiysa durur).
Kanit: raporlar/kaynaklar/05-fiyat-arastirmasi.md bolum 6. Adetler: planlama/adim5/bom_toplam.json (bom_say.py).
  py -3 planlama/adim5/maliyet_duzelt.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
YOL = os.path.join(HERE, "..", "maliyet.json")
d = json.load(open(YOL, encoding="utf-8"))
if any(it.get("adim") == "5" for it in d["kalemler"]):
    sys.exit("zaten uygulanmis (adim 5 kalemi var)")
K = d["kalemler"]


def bul(ad, model_bas=None):
    r = [it for it in K if it["ad"] == ad and (model_bas is None or it["model"].startswith(model_bas))]
    assert len(r) == 1, (ad, model_bas, len(r))
    return r[0]


def ek(it, sonra=None):
    it.setdefault("adim", "5")
    if sonra is None:
        K.append(it)
    else:
        K.insert(K.index(sonra) + 1, it)
    return it


PCV = "paslanmazcivata.ist"
U = "https://www.paslanmazcivata.ist/urun/"

# ---------------- B2: adet ve sürüm ----------------
it = bul("Sigma profil")
it.update(adet=3.0, adim="5",
          model="40 × 40 ağır, kanal 10; 3 × 1 m çubuk, ölçüye kesim: 800,5 · 500 + 200 + 190 · 500 + 190 + 190 mm")
it["not"] = "B2: CAD kesim planı (iskelet-analiz.json kesim, 2.570,5 mm; artık 194,5 / 99 / 109). Eski liste 2 × 500, 3 × 260, 700, 200 (V1)"
it = bul("T-somun")
it.update(adet=50, tl=3.79, adim="5", model="Kanal 10 tırtıllı somun, M6 (üstten yerleştirilir; CAD'de 'çekiç somun')")
it["not"] = "B2: CAD 50 = iskelet 8 + taban 18 + kabuk 14 + omuz 2 × 4 + kafa 2 (plandaki '40 → 18' eskiydi). Fiyat 15 Ekim 2026 (3,79 TL, stok 37.430)"
it = bul("İmbus civata")
it.update(adet=18, adim="5")
it["not"] = "B2: CAD M6×16 = 16 (iskelet 8, omuz 2 × 4) + 2 yedek. M6×14 ve M6×20 ayrı satırda"
it = bul("Mesafe burcu")
it.update(adet=8, adim="5")
it["not"] = "B2: CAD 8 (taban; M5 × 40 dişi-dişi AA 8). Türkiye'de bulunamadı: M5 uzatma somunu ya da uzun civata + baskılı burç"
for m in ("Alüminyum, MG996R", "Alüminyum, kafa"):
    x = [i for i in K if i["model"].startswith(m)]
    assert len(x) == 1
    x[0].update(ver="v1,v2", adim="5")
    x[0]["not"] = "B2: V3 CAD'de servo braketi yok (kafa ve kol baskı parçası)"
gw = bul("Göğüs ekranı")
gw.update(ver="v2", adim="5")
gw["not"] = gw["not"] + ". B2/K2: V3'te Nextion (alttaki satır)"
ek({"g": "ses", "ad": "Göğüs ekranı", "model": "Nextion NX1060P101-011C-I, 10,1\" 1024 × 600, kapasitif, USART (ESP32 UART2)",
    "adet": 1, "tl": 9154.91, "satici": "Robotistan", "url": "https://www.robotistan.com/nextion-nx1060p101-101touch-display",
    "durum": "dogrulandi", "stok": "yok", "ver": "v3",
    "alt": {"satici": "Robotistan (011R-I rezistif, aynı ölçü)", "tl": 9827.28,
            "url": "https://www.robotistan.com/nx1060p101-011r-i-101inc-akilli-seri-usart-hmi-rezistif-dokunmatik-ekran"},
    "not": "K2 (14 Ekim 2026). CAD ve datasheet bu model (R ve C aynı ölçü). Fiyat 15 Ekim 2026 (7.629,09 + KDV); sayfada Tükendi, rezistif sürümün sayfası da Tükendi diyor (arama listesi 'stokta'). RobotShop AB 101,64 € (sipariş üzerine). HDMI gerekmez"}, gw)
ak = bul("Akü")
ak.update(ver="v1,v2", adim="5")
ek({"g": "guc", "ad": "Akü", "model": "Victron Lithium SuperPack 12,8 V 20 Ah (BAT512020705), 256 Wh, BMS 30 A / 80 A 10 sn, M5 kutup, 167 × 181 × 77 mm, 3,0 kg",
    "adet": 1, "tl": 12680.70, "satici": "Atakale", "url": "https://atakale.com/index.php?product_id=438&route=product%2Fproduct",
    "durum": "dogrulandi", "stok": "var", "ver": "v3",
    "alt": {"satici": "Hepsiburada (KampKaravanMarket)", "tl": 16472.21,
            "url": "https://www.hepsiburada.com/victron-lithium-superpack-12-8v-20ah-256wh-m5-dahili-bms-li-lifepo4-lityum-aku-pm-HBC0000M2DPYC"},
    "not": "K3 (14 Ekim 2026), akü raporunun 1. tercihi; CAD yuvasıyla birebir. Fiyat 15 Ekim 2026 (10.567,25 + KDV), sayfada stok 1, USD'ye bağlı. Yüksek kapasitif yükte BMS keser: ön şarj E9 (elektrik.md)"}, ak)
hz = bul("3D baskı hizmeti", "PETG, ≈ 4,4")
hz["ver"] = "v2"
ek({"g": "uretim", "ad": "3D baskı hizmeti", "model": "PETG + PETG-CF, ≈ 6,0 kg parça (1,5 TL/g)", "adet": 6.0, "birim": "kg", "tl": 1500.0,
    "satici": "Online baskı hizmeti", "url": "https://yazdirgelsin.com/3d-baski-fiyati-hesapla", "durum": "tahmini", "stok": "belirsiz",
    "secenek": "hizmet", "ver": "v3",
    "not": "B2: V3 baskı listesi 50 parça, 5,96–6,02 kg (adim5/baski_toplam.py; M4 omuz, S1 kaset ve tambur dahil). Türkiye'de 0,5–2 TL/g"}, hz)
al = bul("Alüminyum lazer kesim")
al.update(model="3 mm alt plaka 270 × 500 + boyun plakası", adim="5")
al["not"] = "B2: V3 CAD (taban alt plaka, kafa boyun plakası). Aralık 1.000–2.000 TL; DXF ile teklif al"
kp = bul("Kontrplak lazer kesim")
kp.update(model="5 mm huş, 2 parça: elektronik katı 270 × 226 + güç paneli 270 × 274", adim="5")
kp["not"] = "B2: V3 CAD (taban). Aralık 400–700 TL"
for v in ("Vida seti M3", "Vida seti M4", "Vida seti M5"):
    x = bul(v)
    x.update(ver="v1,v2", adim="5")
    x["not"] = "B2: yıldız başlı set V3 CAD'e uymuyor (CAD DIN 912 / ISO 7380 / DIN 913 / DIN 985 + ısıl gömme); V3 satırları aşağıda"
cf = bul("PETG-CF filament (eklem parçaları)")
cf.update(adet=3, adim="5")
cf["not"] = ("B1/M4: CF parçalar 0,96–1,02 kg (omuz destekli, doluluk 0,8–0,9) + CF kuponlar (A, B, C, D1, D2) ≈ 0,2–0,3 kg → 3 × 0,5 kg = 1,5 kg. "
             "Fiyat 11 Ekim 2026 (havale 1.077,11); stok sorulmalı. Türkiye'de siyah 1 kg PETG-CF bulunamadı")
bs = bul("Bıçak sigorta (ek)")
bs.update(adet=5, adim="5",
          model="Standart bıçak (ATO) 5 A + 2 A (sigorta kutusu F4, F5); mini bıçak 7,5 A × 2 (XL4016 hat yuvaları) + 10 A (şarj girişi)")
bs["not"] = "E9/B2: kutudaki sette 5 A tek, F3 ve F4 iki 5 A ister → +1 standart 5 A (ikinci 5 A). F5 2 A standart. Mini/standart ayrımı yuvaya göre. Fiyat doğrulanmadı"
hy = bul("Hat sigortası yuvası")
hy.update(adet=3, adim="5")
hy["not"] = "E1 + E9: XL4016 A ve B girişleri (7,5 A) + XT60 şarj girişi (10 A, akü raporu önerisi). Fiyat doğrulanmadı"
pt = bul("Delikli pertinaks")
pt.update(adet=4, adim="5", model="70 × 50 mm (arayüz kartı + servo dağıtım A/B + ESP32 taşıyıcı)")
pt["not"] = "B1: CAD taban 4 kart (ESP32 taşıyıcı dahil). Fiyat doğrulanmadı"
kh = bul("Klemens ve pin header")
kh.update(tl=80.0, adim="5", model="2'li klemens 5,08 mm ×4 + 40'lı erkek header ×2 + 15'li dişi header ×2 (ESP32 taşıyıcı)")
ms = bul("Röle sürücü MOSFET")
ms.update(adet=2, adim="5")
ms["not"] = "E3 + E9: ikinci IRLZ44N ön şarj rölesi K2 için (GPIO2). Fiyat kategori sayfası önbelleğinden (25,64–26,99 TL), doğrulanmadı"
dy = bul("Diyot")
dy.update(adet=3, adim="5", model="1N4007 × 2 (röle K1 ve K2 bobini) + 1N5819 (ESP32 USB VBUS)")
ac = bul("Acil stop butonu")
ac["not"] = "B2: CAD (taban, M6 ölçümü) Emas B200E60 60 mm + ayrı kontak bloğu; bu satır 40 mm. Etek deliği ve kontak (1 NC, E3) CAD'e göre teyit edilecek; 2. satıcı B200E60"
kg = bul("Eşik altı siparişlerin kargosu")
kg.update(adet=12, adim="5",
          model="Robotzade, Robiz, Makermarketim, UserPil, Elektrix, Hepsiburada, Trendyol, Rulmanal, paslanmazcivata.ist, Rhino3DPrinter, Elo, Atakale")
kg["not"] = "B1 ile 5 yeni satıcı (Rulmanal eşiği 2.500 TL; diğerlerinin eşiği sayfada yok). Diğer mağazalarda sepet ücretsiz kargo eşiğini geçiyor"
eh = bul("Ekran kablosu")
eh["not"] = eh["not"] + ". B2/K2: Nextion UART olduğu için HDMI adedi 1 (yalnız 7\" yüz ekranı)"

for n in d["notlar"]:
    if n["b"].startswith("V2 göğüs ekranı"):
        n["b"] = "Göğüs ekranı Nextion (K2)."
        n["t"] = "V3'te göğüs ekranı Nextion NX1060P101 (CAD ve datasheet), 9.155 TL; 15 Ekim 2026'da Robotistan'da tükenmiş, stok alarmı kur. Waveshare 10,1\" yalnız V2 listesinde."
    if n["b"].startswith("Akü sipariş"):
        n["b"] = "Akü Victron SuperPack 12,8/20 (K3)."
        n["t"] = "Atakale'de tek adet stok (15 Ekim 2026). Ölçü CAD yuvasıyla birebir; kutuplar M5 halka pabuçla. Ön şarj devresi (E9) olmadan röle her çektiğinde BMS kesebilir."
d["notlar"].append({"b": "Vidalar CAD'e göre.", "t": "V3 CAD imbus (DIN 912), bombe başlı (ISO 7380), set vida, fiberli somun ve ısıl gömme somun kullanıyor; yıldız başlı setler V3 listesinden çıktı. Vida fiyatları tek satıcının kategori taban fiyatı (boya göre değişebilir)."})
d["notlar"].append({"b": "M6 CAD değişiklikleri koşullu.", "t": "Perçin somun, dışarıdan ISO 7380, servis kapağı bağlantıları ve M4 ısıl gömme, M6 CAD işi yapılırsa alınır; toplama girmez."})

# ---------------- B1: CAD'de olup maliyette olmayanlar ----------------
r = bul("Sigma profil")
r = ek({"g": "tahrik", "ad": "İç köşe bağlantı (gizli)", "model": "Kanal 10, 40 × 40, set vidalı (CAD: 8 adet, 16 × M6×10 set vida)", "adet": 8, "tl": 38.51,
        "satici": "CNC Marketi (45 × 45 K10 sayfası)", "url": "https://www.cnc-marketi.com/urun/45x45-gizli-kose-baglanti-90-k10",
        "durum": "tahmini", "stok": "belirsiz", "not": "B1. 40 × 40 kanal 10 gizli köşe sayfası bulunamadı, 45 × 45 K10 fiyatı yazıldı (fiyat doğrulanmadı). Set vida ayrı satırda"}, r)
r = ek({"g": "tahrik", "ad": "Tırtıllı somun M4", "model": "Kanal 10, M4 (motor braketleri, CAD 'çekiç somun')", "adet": 8, "tl": 3.91,
        "satici": "CNC Marketi", "url": "https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somun-m4", "durum": "dogrulandi", "stok": "var",
        "not": "B1. Fiyat 15 Ekim 2026"}, r)
r = ek({"g": "tahrik", "ad": "Tırtıllı somun M5", "model": "Kanal 10, M5 (kat burcu saplamaları)", "adet": 8, "tl": 3.85,
        "satici": "CNC Marketi", "url": "https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu10-kanal-profil-tirtilli-somunu",
        "durum": "dogrulandi", "stok": "var", "not": "B1. Fiyat 15 Ekim 2026"}, r)
r = ek({"g": "tahrik", "ad": "Alüminyum bükme braket", "model": "Gövde U braketi 3 mm × 4 + etek taşıyıcı L braketi 2 mm × 6 (lazer + abkant)", "adet": 10, "tl": 60.0,
        "satici": "Lazer kesim atölyesi", "url": "", "durum": "tahmini", "stok": "belirsiz",
        "not": "B1: CAD kabuk (6 + 4). DXF + büküm çizimiyle teklif; fiyat doğrulanmadı"}, r)
r = bul("Dirsek, bilek ve kafa servosu")
r = ek({"g": "servo", "ad": "Rulman 6808-2RS", "model": "40 × 52 × 7, KWC (omuz 2 + boyun 2)", "adet": 4, "tl": 106.75,
        "satici": "Rulmanal", "url": "https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman", "durum": "dogrulandi", "stok": "var",
        "alt": {"satici": "Rulmanal (NSK)", "tl": 1050.59, "url": "https://www.rulmanal.com.tr/urun/6808-2rs-nsk-40x52x7-rulman"},
        "not": "B1. Fiyat 15 Ekim 2026 (88,96 + KDV), stok 67. Kupon A ile yuva ölçüsü seçilir"}, r)
r = ek({"g": "servo", "ad": "Rulman 625ZZ", "model": "5 × 16 × 5 (omuz S2 2, dirsek 2, tilt 1)", "adet": 5, "tl": 29.65,
        "satici": "Rulmanal", "url": "https://www.rulmanal.com.tr/urun/625-zz-kwc-5-16-5-rulman", "durum": "dogrulandi", "stok": "var",
        "not": "B1. BGR 625 ZZ, fiyat 15 Ekim 2026 (24,71 + KDV), stok 8.548"}, r)
r = ek({"g": "servo", "ad": "Servo horn 25T alüminyum", "model": "25T disk horn, M3 delikli (10 servo)", "adet": 10, "tl": 82.32,
        "satici": "Robiz (kol tipi sayfası)", "url": "https://robiz.net/servoarm25t", "durum": "tahmini", "stok": "var",
        "alt": {"satici": "AZ-Delivery (5'li 9,99 €, ithal)", "url": "https://www.az-delivery.de/en/products/aluminium-25t-servoarm"},
        "not": "B1. CAD disk tipi; Türkiye'de disk tipi bulunamadı, Robiz kelepçeli tek kol fiyatı yazıldı (fiyat doğrulanmadı). Horn delik dizilimi Parti 2'den önce ölçülür"}, r)
r = ek({"g": "servo", "ad": "Servo uzatma kablosu", "model": "22 AWG, 3 damar, JR, 100 cm (10 hat: kollar ≈ 8,4 m + S1 × 2, pan, tilt ≈ 4,3 m)", "adet": 14, "tl": 43.94,
        "satici": "Robotistan", "url": "https://www.robotistan.com/60-cekirdek-22awg-servo-kablosu", "durum": "tahmini", "stok": "yok",
        "not": "B1/S1: boy S1-kaset.md (dirsek/bilek 1.541, S2 1.105 mm) + E1 (~1,0–1,3 m). Kesilip JR sıkılır. S1 kasetinden geçen kablo ≤ 1,4 mm kalınlık şartı ölçülecek. Sayfada iki uç erkek ve Tükendi; fiyat doğrulanmadı"}, r)
r = ek({"g": "servo", "ad": "JR konnektör seti", "model": "JR erkek + dişi gövde × 12'şer + krimp pin", "adet": 1, "tl": 150.0,
        "satici": "Tahmin", "url": "", "durum": "tahmini", "stok": "belirsiz",
        "not": "B1: uzatma uçları (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir). Fiyat doğrulanmadı"}, r)
r = bul("Röle sürücü MOSFET")
r = ek({"g": "guc", "ad": "Röle K1", "model": "Mini oto röle 12 V 40 A, 5 fişli, diyotlu (Elo)", "adet": 1, "tl": 166.32,
        "satici": "Elo", "url": "https://eticaret.elo.com.tr/urun/mini-role-12-v-40-a-5-fisli-diyotlu-toz-korumali", "durum": "dogrulandi", "stok": "belirsiz",
        "alt": {"satici": "Kartal Otomasyon (mikro 12 V 40 A)", "tl": 56.70, "url": "https://www.kartalotomasyon.com.tr/urun/12v-40a-mikro-role-5-fisli"},
        "not": "B1: CAD taban 'ISO mini röle 12 V 40 A + soket (BOM'da yok)'. Fiyat 15 Ekim 2026 (138,60 + KDV). Bobin ~0,15 A (ölçülecek)"}, r)
r = ek({"g": "guc", "ad": "Röle soketi", "model": "ISO mini, 5 fişli, kablolu", "adet": 1, "tl": 120.0, "satici": "Tahmin (n11 ilanı 119,90 TL)", "url": "",
        "durum": "tahmini", "stok": "belirsiz", "not": "B1. Fiyat doğrulanmadı"}, r)
r = ek({"g": "guc", "ad": "Ön şarj rölesi K2 (E9)", "model": "12 V röle 7 A, 5 pin, JQC-3F(T73)-12VDC", "adet": 1, "tl": 18.23,
        "satici": "Direnc.net", "url": "https://www.direnc.net/12v-7a-tek-kontak-5-pinli-jqc-3ft73-12vdc-role", "durum": "dogrulandi", "stok": "var",
        "not": "E9: bobini mantar NC sonrasından (F5), ikinci IRLZ44N ile GPIO2. Fiyat 15 Ekim 2026"}, r)
r = ek({"g": "guc", "ad": "Ön şarj direnci (E9)", "model": "5,6 Ω 11 W taş (çimento) direnç", "adet": 1, "tl": 13.95,
        "satici": "Direnc.net", "url": "https://www.direnc.net/022r-11w-tas-direnc-11664", "durum": "dogrulandi", "stok": "var",
        "not": "E9: K2 kontağıyla seri, K1 kontağına paralel. Fiyat 15 Ekim 2026"}, r)
r = ek({"g": "guc", "ad": "XT60 şarj girişi tutucusu", "model": "XT60 panel tutucu (etek), mevcut XT60 dişi ile", "adet": 1, "tl": 60.0,
        "satici": "Tahmin", "url": "", "durum": "tahmini", "stok": "belirsiz",
        "not": "B1: şarj girişi (akü raporu: 10 A hat sigortasıyla). Etek deliği açık iş (baskı listesi Parti 4). Fiyat doğrulanmadı"}, r)
r = ek({"g": "guc", "ad": "Akü kutup pabucu", "model": "M5 halka pabuç 12 AWG × 2 + M5 yaylı pul", "adet": 1, "tl": 40.0,
        "satici": "Tahmin", "url": "", "durum": "tahmini", "stok": "belirsiz", "not": "Victron M5 kutup (akü raporu). Fiyat doğrulanmadı"}, r)
r = bul("Kart burcu seti")
r = ek({"g": "uretim", "ad": "M2,5 pirinç distans seti", "model": "M2,5 distans (dişi-dişi / erkek-dişi) + vida + somun, ≈ 240 parça",
        "adet": 1, "tl": 300.0, "satici": "Amazon TR (Tenlacum 240 parça; sayfa açılmadı)", "url": "https://www.amazon.com.tr/dp/B07G5HM9ZT",
        "durum": "tahmini", "stok": "belirsiz",
        "not": "B1: CAD M2,5 × 8 pirinç burç 8 (taban) + kafa Pi burcu 4 (AA 5) + M2,5 DIN 912 24 (5 × 12, 8 × 12). Fiyat doğrulanmadı"}, r)


def vida(ad, model, adet, tl, url, notx):
    return {"g": "uretim", "ad": ad, "model": model, "adet": adet, "tl": tl, "satici": PCV, "url": url, "durum": "tahmini", "stok": "var", "ver": "v3",
            "not": notx + ". Kategori taban fiyatı 15 Ekim 2026 (boya göre değişebilir)"}


r = ek(vida("İmbus civata M3", "DIN 912 A2: M3×6 × 85, ×8 × 85, ×10 × 5, ×12 × 18, ×20 × 5", 198, 1.30, U + "m3-paslanmaz-imbus-civata-cesitleri-din912",
            "B1: CAD 178 (6 × 76, 8 × 78, 10 × 4, 12 × 16, 20 × 4) + pay"), r)
r = ek(vida("Bombe başlı imbus M3", "ISO 7380 A2: M3×6 × 65, M3×8 × 5", 70, 1.15, U + "m3-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380",
            "B1: CAD 63 (6 × 59, 8 × 4)"), r)
r = ek(vida("İmbus civata M4", "DIN 912 A2: M4×16", 56, 2.02, U + "m4-paslanmaz-imbus-civata-cesitleri-din912", "B1: CAD 51"), r)
r = ek(vida("İmbus civata M5", "DIN 912 A2: M5×10 × 5, M5×12 × 15", 20, 2.66, U + "m5-paslanmaz-imbus-civata-cesitleri-din912", "B1: CAD 17 (10 × 4, 12 × 13)"), r)
r = ek(vida("İmbus civata M6 (14 / 20)", "DIN 912 A2: M6×14 × 30, M6×20 × 2", 32, 3.89, U + "m6-paslanmaz-imbus-civata-cesitleri-din912",
            "B1: CAD M6×14 28 + M6×20 2 (M6×16 ayrı satırda, CNC Marketi)"), r)
r = ek(vida("Bombe başlı imbus M6", "ISO 7380 A2: M6×14 (sonar tutucu)", 4, 3.89, U + "m6-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380", "B1: CAD 4"), r)
r = ek(vida("Set vida M6×10", "DIN 916 A2 (CAD DIN 913; iç köşe bağlantı)", 16, 1.02, U + "6mm-paslanmaz-setskur-cesitleri-kafasiz-alyan-din916",
            "B1: CAD 16. DIN 913 sayfada yok, DIN 916 (çukur uç) yazıldı"), r)
r = ek(vida("Set vida M5×16 (saplama)", "DIN 916 A2 (CAD DIN 913; kat burcu saplaması)", 8, 0.84, U + "5mm-paslanmaz-setskur-cesitleri-kafasiz-alyan-din916",
            "B1: CAD 8 (plandaki 'M5×16 set vida × 8')"), r)
r = ek(vida("Fiberli somun M3 / M4", "DIN 985 A2: M3 × 5 + M4 × 43", 48, 1.02, U + "paslanmaz-fiberli-somun-cesitleri-din985",
            "B1: CAD M3 4 + M4 39 (36 kontra + 3 güç paneli)"), r)
r = ek(vida("Pul", "DIN 125 A2: M3 × 12, M4 × 16, M5 × 18, M6 × 24", 70, 0.40, U + "paslanmaz-pul-dar-pul-cesitleri-din125",
            "B1: CAD M3 12, M4 15, M5 17, M6 16 (+ pay)"), r)
r = ek({"g": "uretim", "ad": "Isıl gömme somun M3", "model": "Pirinç insert M3 (CAD deliği ruthex M3 × 5,7 için Ø4,0)", "adet": 125, "tl": 5.22,
        "satici": "Rhino3DPrinter", "url": "https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3", "durum": "dogrulandi", "stok": "belirsiz", "ver": "v3",
        "not": "B1: CAD 109 (kabuk 65, kafa 20, omuz 2 × 9, dirsek 4, taban 2) + pay. Fiyat 15 Ekim 2026 (adet; KDV ibaresi yok). Varyant dış çapı (4 / 5 mm) CAD deliğiyle uyumsuz olabilir: kupon C ile seç"}, r)
r = ek({"g": "uretim", "ad": "Isıl gömme somun M5", "model": "Pirinç insert M5", "adet": 12, "tl": 6.27,
        "satici": "Rhino3DPrinter", "url": "https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5", "durum": "tahmini", "stok": "belirsiz", "ver": "v3",
        "not": "B1: CAD 9 (kabuk 4, omuz 2, dirsek 2, kafa 1) + pay. Fiyat M3 sayfasındaki bağlantıdan (6,27), ölçü doğrulanmadı"}, r)
r = ek({"g": "uretim", "ad": "Cırt kayış", "model": "25 mm, akü bağı (2 × ~0,6 m)", "adet": 2, "tl": 30.0, "satici": "Tahmin", "url": "",
        "durum": "tahmini", "stok": "belirsiz", "not": "B1: CAD taban 2. Fiyat doğrulanmadı"}, r)
r = ek({"g": "uretim", "ad": "Kablo bağı ve yapışkanlı taban", "model": "Kablo bağı 2,5 × 100 (100'lü) + yapışkanlı/vidalı bağ tabanı 20 × 20 (100'lü)", "adet": 1, "tl": 180.0,
        "satici": "Tahmin", "url": "", "durum": "tahmini", "stok": "belirsiz",
        "not": "B1: S1 kaseti 2/kol + K1/K2 kablolama kapıları (M6 rehberi). Fiyat doğrulanmadı"}, r)
pe = bul("PETG filament", "Microzey HS PETG beyaz")
ek({"g": "uretim", "ad": "PETG filament (kupon + pay)", "model": "Microzey HS PETG beyaz, 1,75 mm, 1 kg", "adet": 1, "tl": 389.0,
    "satici": "Microzey", "url": "https://microzey.com/hs-petg-beyaz", "durum": "dogrulandi", "stok": "var", "secenek": "yazici", "ver": "v3",
    "not": "B1: düz PETG parçalar 5,01 kg (S1 kaset + tambur dahil) + PETG kuponlar (B, C, E) ≈ 0,1 kg; 6 makara %17 pay bırakıyordu, 7 makarayla %37. Fiyat 11 Ekim 2026"}, pe)
usb = bul("ESP32 – Pi USB kablosu")
ek({"g": "elektronik", "ad": "Bluetooth gamepad", "model": "PS4 / Xbox uyumlu kablosuz kol (Bluepad32)", "adet": 1, "tl": 750.0,
    "satici": "Tahmin", "url": "", "durum": "tahmini", "stok": "belirsiz",
    "not": "Yazılım planı Y4 (teleop). Ekipte varsa düşer. Fiyat doğrulanmadı"}, usb)


# ---------------- M6 CAD (koşullu, toplama girmez) ----------------
def m6(ad, model, adet, tl, satici, url, notx):
    ek({"g": "uretim", "ad": ad, "model": model, "adet": adet, "tl": tl, "satici": satici, "url": url, "durum": "tahmini", "stok": "belirsiz",
        "secenek": "kosullu", "kosullu": "M6 CAD", "not": "Koşullu (M6 CAD " + notx + "). Toplama girmez"})


m6("Bombe başlı imbus M5×16 (M6 K1)", "ISO 7380 A2, gövde braketi dışarıdan", 4, 2.95, PCV, U + "m5-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380",
   "K1; M5 ısıl gömme × 4 ve M5×10 × 4 düşer; kategori taban fiyatı")
m6("Perçin somun M5 + M3 (M6 K1/K2)", "Çelik perçin somun M5 × 6 (braket, 3 mm Al) + M3 × 8 (etek braketi, 2 mm Al)", 14, 5.0, "Tahmin", "",
   "K1 4 + K2 6 + pay; fiyat doğrulanmadı")
m6("Perçin somun aleti (M6 K1/K2)", "Elle perçin somun pensesi M3–M6", 1, 400.0, "Tahmin", "", "K1/K2; bölümde varsa düşer; fiyat doğrulanmadı")
m6("Bombe başlı imbus M3×8 (M6 K2)", "ISO 7380 A2, etek braketi dışarıdan", 6, 1.15, PCV, U + "m3-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380",
   "K2; etek M3 ısıl gömme × 6 düşer")
m6("Servis kapakları bağlantısı (M6 K4/K5)", "M3×6 ISO 7380 × 10 + M3 ısıl gömme × 10 (üst arka kapak 6 + etek sigorta kapağı 4)", 1, 63.70,
   PCV + " + Rhino3DPrinter", "", "K4 + K5; 10 × 1,15 + 10 × 5,22")
m6("Isıl gömme somun M4 (M6 C3)", "Pirinç insert M4 (S2 kol başına 2 + tilt 1)", 6, 6.0, "Tahmin", "",
   "C3, altıgen cep seçilmezse; DIN 985 × 5 düşer; fiyat doğrulanmadı")


# yaz (her kalem tek satır, gruplar arasında boş satır)
def s(x):
    return json.dumps(x, ensure_ascii=False)


out = ["{"]
for k in d:
    if k in ("gruplar", "notlar", "kalemler"):
        continue
    out.append("  %s: %s," % (json.dumps(k), s(d[k])))
for k in ("gruplar", "notlar"):
    out.append('  "%s": [' % k)
    out.append(",\n".join("    " + s(x) for x in d[k]))
    out.append("  ],")
out.append('  "kalemler": [')
rows, prev = [], None
for x in K:
    if prev is not None and x["g"] != prev:
        rows.append("")
    rows.append("    " + s(x) + ",")
    prev = x["g"]
rows[-1] = rows[-1].rstrip(",")
out.extend(rows)
out.append("  ]")
out.append("}")
with open(YOL, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
json.load(open(YOL, encoding="utf-8"))
print("yazildi:", len(K), "kalem")
