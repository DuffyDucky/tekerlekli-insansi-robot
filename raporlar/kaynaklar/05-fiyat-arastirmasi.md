---
title: "Kanıt: Parça fiyat araştırması ve doğrulama"
created: 2026-09-27
---

> Dört Claude Opus alt ajanının raporu (27 Eylül 2026) ve orkestratörün (Echo) doğrulama kaydı. Temiz liste
> `planlama/maliyet.json` dosyasında; sayfa `tasarim/Robot-Tasarim-Demosu.html` içindeki "Proje maliyeti" bölümü.
> Ajan raporları aşağıda kısaltılmadan (yalnız biçim düzeltilerek) duruyor; rakamlar ajanların beyanıdır, doğrulama
> sonucu ilk bölümde.

## 1. Kapsam

Malzeme listesi CAD montajındaki parçalardan (`tasarim/cad/parca-listesi.csv`, 4 motorlu önerilen yapı) ve
CAD'de çizilmeyen zorunlu kalemlerden (hafıza kartı, mikrofon, şarj cihazı, sigorta, kablo, klemens, filament,
vida) oluşuyor. Dört ajan paralel çalıştı: tahrik ve şase, işlemci ve sensörler, servo ve güç, üretim ve sarf
malzemesi ile kur. Üç ajan kullanım sınırı yüzünden bir kez kesildi ve kaldığı yerden sürdürüldü.

Kur: **1 USD = 48,8780 TL**, TCMB 25.09.2026 döviz satış (bülten 2026/181). Orkestratör XML'den ayrıca okudu:
https://www.tcmb.gov.tr/kurlar/202609/25092026.xml (27.09 Pazar olduğundan son iş günü). Serbest piyasa Cuma
kapanışı 48,9496 (fark ≈ %0,15).

## 2. Doğrulama (orkestratör, 27.09.2026)

**Yöntem.** Seçilen ve ikinci satıcı olarak gösterilen 75 ürün sayfası bir betikle yeniden açıldı. Fiyat ve stok,
sayfanın kendi yapısal verisinden (schema.org JSON-LD `offers.price` / `availability`, meta etiketleri) ve
görünür metinden okundu. Direnc, Motorobit, Robotsepeti, Robiz ve UserPil JSON-LD'de KDV hariç fiyat veriyor;
bunlar ×1,20 ile karşılaştırıldı. Ajanların beyanı değil, sayfanın o anki verisi esas alındı.

| Sonuç | Sayfa | Ayrıntı |
|---|---|---|
| Fiyat birebir tuttu | 71 / 75 | Kuruşu kuruşuna (Adafruit 29,25 USD ve Limacell 4.713,43 TL meta etiketinden) |
| Fiyat farklı | 1 | Hepsiburada ana sigorta yuvası: liste 550,00 TL; ajanın 495 TL'si sepete özel indirim. Listeye 550 TL yazıldı |
| Fiyat bulunamadı | 1 | Motorobit 30 A bıçak sigorta: arama sayfasında ad var, fiyat okunamadı → "tahmini" (4,20 TL, ajan beyanı) |
| Erişim engellendi | 2 | Trendyol WAGO sayfaları 403 → "tahmini" (ajanın tarayıcıdan okuduğu fiyat) |

**Yakalanan stok hataları.** Ajan 3 üç Direnc.net ürününe "stokta" demişti; sayfa verisi `OutOfStock` ve ürün
yorumlarında "stok ne zaman gelir?" soruları var:

| Kalem | Ajanın seçimi | Durum | Yerine (doğrulandı, stokta) |
|---|---|---|---|
| BTS7960B motor sürücü | Direnc.net 232,47 TL | Tükendi | Makermarketim 277,85 TL |
| XT60 konnektör çifti | Direnc.net 21,50 TL | Tükendi | Robotsepeti erkek 21,01 + dişi 21,61 = 42,62 TL |
| Makaron seti 750 parça | Direnc.net 232,47 TL | Tükendi | Robolink 328 parça kutulu 229,50 TL |

Beklendiği gibi tükenmiş olanlar: Camera Module 3 (Robotistan ve 5 satıcı daha), Orbus 20 Ah akü. Robotistan'da Pi 5
8 GB ve 7" LCD (C) sayfa verisine göre stokta (WebFetch özetinin "Tükendi" demesi şablondaki gizli bloktan).

**Orkestratörün diğer kararları.**
- WAGO 221-415 çıkarıldı (Trendyol'da tek adet stok); 221-413 10'lu paket yeterli. Star Akım 50'li paketle
  satıyor (1.003,50 TL), bu proje için fazla.
- Aküde Limacell 24 Ah seçildi: stoklu ve ölçüsü tutan 20 Ah bulunamadı; ölçü satıcıya sorulacak.
- Kargo: sepeti ücretsiz kargo eşiğini geçmeyen 7 sipariş × 120 TL (tahmini). Robolink'e makaron eklenince
  sepet 1.660,50 TL'ye çıkıp eşiği geçiyor.
- Beklenmeyen gider payı %15 (önceki fizibilitede %25'ti). Gerekçe: fiyatların çoğu artık doğrulandı, kargo ve
  yedek parça ayrı satırda. Sayfadan %0–25 arası seçilebiliyor.
- İkinci satıcı olarak yalnız betikle doğrulanan sayfalar gösterildi.

## 3. Sonuç (planlama/maliyet.json)

| Grup | TL | USD |
|---|---:|---:|
| İşlemci ve elektronik | 16.000,64 | 327,36 |
| Güç ve güvenlik | 10.717,89 | 219,28 |
| Ses ve görüntü | 8.229,97 | 168,38 |
| Tahrik ve şase | 7.900,94 | 161,65 |
| Üretim ve sarf (bölümün yazıcısıyla) | 5.487,53 | 112,27 |
| Servolar ve kol | 5.288,88 | 108,21 |
| Yedek parçalar | 1.632,81 | 33,41 |
| Kargo (tahmini) | 840,00 | 17,19 |
| **Parçalar ve kargo** | **56.098,66** | **1.147,73** |
| %15 beklenmeyen pay | 8.414,80 | 172,16 |
| **Genel toplam** | **64.513,46** | **1.319,89** |

Seçenekler: baskı hizmetiyle 68.831,71 TL; yedek parçasız 62.635,73 TL. 54 kalemin 48'i satıcı sayfasından
doğrulandı; 6'sı tahmini (lazer kesim ×2, M5 × 40 burç, 30 A sigorta, WAGO, kargo).

Önceki fizibilite tahmini (26.09, Orta/Pi 5): ≈ 61.700 TL (%25 pay dahil). Fark küçük; ama liste artık CAD
tasarımının gerçek parçalarına ve doğrulanmış satıcı sayfalarına dayanıyor.

---

# Ek: ajan raporları

## Ajan 1: tahrik ve şase

Fiyatlar ürün sayfalarından okundu. Stok bilgisi sayfadaki yapısal veriden (JSON-LD `availability`, Robotistan/Robolink'te `available/quantity`); Robotistan ve Robolink'te "Sepete Ekle" ve "Tükendi" düğmeleri şablonda birlikte durduğu için WebFetch özeti stoktaki ürüne yanlışlıkla "Tükendi" diyebiliyor. Motorobit, Robotsepeti ve Robiz'de JSON-LD fiyatı KDV hariç; KDV dahil fiyat sayfa metninden okundu. Trendyol, Hepsiburada, n11, Akakçe, Çiçeksepeti 403 verdi (Trendyol ve Hepsiburada'ya tarayıcıdan kısa bakıldı; M5×40 distans ve JGB37 enkoderli motor için uygun ürün çıkmadı).

### 1. Ham bulgular

| # | Kalem | Satıcı | Sayfadaki ürün adı | Birim TL (KDV dahil) | Stok | URL | Not |
|---|---|---|---|---|---|---|---|
| 1 | Motor | Direnc.net | JGB37-520 - 12V 60RPM Enkoderli Motor | 639,29 | Stokta | https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor | 12V, 60 rpm, enkoderli, 21 kg. Mil/D, Hall ve oran sayfada yazmıyor. Önceki fiyatla aynı |
| 1 | Motor | Robotistan | JGB37 520 12V 1000RPM Encoderli DC Motor | 622,12 | Tükendi | https://www.robotistan.com/jgb37-520-12v-1000rpm-encoderli-dc-motor | Yanlış RPM, elendi |
| 1 | Motor | Robotistan | 12V 37mm 66 RPM Redüktörlü DC Motor (JGB37-520) | 401,26 | Tükendi | https://www.robotistan.com/12v-35mm-66-rpm-dc-gear-motor | Enkodersiz, elendi |
| 1 | Motor | Robotsepeti | 12V 60Rpm 37mm Redüktörlü DC Motor | 940,53 | Stokta yok | https://www.robotsepeti.com/12v-60rpm-37mm-reduktorlu-dc-motor | Enkodersiz, elendi |
| 1 | Motor | Amazon.com (t) | JGB37-520 Hall Encoder 12V 60Rpm | — | Currently unavailable | https://www.amazon.com/dp/B08KXQ2PZH | İthal seçenek de yok |
| 2 | Braket | Robotistan | Aluminyum L tipi 37D Motor Tutucu (İkili) PL-1084 | 746,55 / çift | Stokta (17) | https://www.robotistan.com/aluminyum-l-tipi-37d-motor-tutucu | Pololu 37D (kaçık mil) için; JGB37 uyumu yazmıyor |
| 2 | Braket | Robotzade | 37 mm Motor Tutucu Aparat Metal | 111,72 | Stokta | https://www.robotzade.com/urun/37-mm-motor-tutucu-aparat-metal | Tekli, 6 M3 vida dahil. L tipi mi, kaçık mile uyar mı belirtilmemiş |
| 2 | Braket | Robotus (Jsumo) | 37 mm Motor Bağlantı Aparatı (2 Adet) | 262,76 / çift | Stokta | https://www.robotus.net/37-mm-motor-baglanti-aparati-2-adet | 2 mm paslanmaz, 6 delik 60° |
| 2 | Braket | Motorobit | 37 mm Motor Tutucu | 105,00 | Tükendi | https://www.motorobit.com/37-mm-motor-tutucu | |
| 3 | Kaplin | Motorobit | 6mm Motor Şaftı ile Uyumlu Hex Tekerlek Kaplini | 120,00 | Stokta (100+) | https://www.motorobit.com/6mm-motor-safti-ile-uyumlu-hex-tekerlek-kaplini | Pirinç, 6 mm delik, ≈12 mm hex, 30 mm. Spec tam uyuyor |
| 3 | Kaplin | Robotsepeti | Hex Tekerlek Kaplini (6mm Motor Mili için) | 151,89 | Stokta | https://www.robotsepeti.com/hex-tekerlek-kaplini-6mm-motor-mili-icin | Aynı spec |
| 3 | Kaplin | Robotistan | Robot Araba Tekerlek Altıgen Kaplin 6mm 30mm | 77,99 | Tükendi | https://www.robotistan.com/robot-araba-tekerlek-altigen-kaplin-6mm-30mm | |
| 3 | Kaplin | Robotistan | Büyük Arazi Tekerleği İçin Metal Kaplin | 63,70 | Tükendi | https://www.robotistan.com/buyuk-arazi-tekerlegi-icin-metal-kaplin | 4 mm mil, elendi |
| 4 | Tekerlek | Robotistan | Büyük Arazi Tekerleği 125 mm x 58 mm - Mavi | 353,63 | Stokta (83) | https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi | Kaplinsiz; göbek tipi yazmıyor |
| 4 | Tekerlek | Motorobit | Büyük Arazi Tekerleği 125mm x 58mm - Mavi | 600,00 | Stokta (10+) | https://www.motorobit.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi | "6mm şafta uyumlu kapliniyle gönderilir" |
| 4 | Tekerlek | Robotsepeti | Jsumo Büyük Boy Arazi Tekerleği - 125mm | 588,33 | Stokta | https://www.robotsepeti.com/jsumo-buyuk-boy-arazi-tekerlegi-125mm-1-adet | Genişlik/göbek bilgisi yok |
| 5 | Sigma | CNC Marketi | 40X40 Sigma Profil 10 Kanal Ağır Tip | 908,32 / m | Stokta | https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip | 1,65 kg/m; en az 1 m, ara ölçü alınabiliyor, ölçüye kesim ücretsiz |
| 5 | Sigma | Otomasyoncu.net | Sigma Profil AĞIR 40x40 - Kanal 10 | 1.071,25 / m | Belirsiz | https://www.otomasyoncu.net/urun/sigma-profil-40x40-agir-kanal-10 | Kesim ücretsiz |
| 5 | Sigma | Robolink | 40x40 Ağır Sigma Profil-Kanal 10 - 1 Metre | 957,00 | Tükendi | https://www.robolinkmarket.com/40x40-agir-sigma-profil-kanal-10-1-metre | 834 TL referansı artık geçersiz |
| 5 | Sigma | Robolink | … - 500mm | 579,00 / parça | Stokta (5) | https://www.robolinkmarket.com/40x40-agir-sigma-profil-kanal-10-500mm | |
| 6 | Köşe | CNC Marketi | Geniş Köşe Bağlantı 40X40 K10 | 24,68 | Stokta | https://www.cnc-marketi.com/urun/genis-kose-baglanti-40x40-k10 | |
| 6 | Köşe | Robolink | 40x40 Geniş Köşe Bağlantı (Doğuş) | 39,00 | Stokta (10) | https://www.robolinkmarket.com/40x40-genis-kose-baglanti | |
| 6 | Köşe | Otomasyoncu.net | 40x40 Köşe Bağlantı GENİŞ | 30,61 | Belirsiz | https://www.otomasyoncu.net/urun/40x40-kose-baglanti-genis | |
| 7 | T-somun | CNC Marketi | 10 Kanal Profil Tırtıllı Somunu M6 | 3,78 | Stokta | https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu-m6 | |
| 7 | T-somun | CNC Marketi | T Kanal Somunu M6 / M5 45X45 K10 | 7,54 / 7,56 | Stokta | https://www.cnc-marketi.com/urun/t-kanal-somunu-m6-45x45-k10 | "45x45 K10" etiketli |
| 7 | T-somun | Otomasyoncu.net | Tırtıllı Somun Kanal 10 (M6 / M5) | 4,70 / 5,29 | Belirsiz | https://www.otomasyoncu.net/urun/tirtilli-somun-kanal-10 | |
| 7 | T-somun | Robolink | M5/40 Tırtıllı Kanal Somun | 10,50 | Stokta (2) | https://www.robolinkmarket.com/m5-40-tirtilli-kanal-somun | Kanal 8, elendi |
| 7 | Civata | CNC Marketi | M6X16 Fosfat Allen İmbus Civata | 3,50 | Stokta | https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata | |
| 8 | Distans | — | M5×40 dişi-dişi | bulunamadı | — | — | Robotistan, Motorobit, Robotsepeti, Direnc, Robolink, Hatfon, Trendyol'da yok |
| 8 | (referans) | Motorobit | M3 40mm Metal Dişi-Dişi Aralayıcı | 14,40 | Stokta | https://www.motorobit.com/m3-40mm-metal-female-female-spacer-standoff-metal-distance | Yalnız tahmin dayanağı |
| 9 | Servo braket | Robiz | Servo Bracket Montaj Parçası (MG995/MG996R) | 88,20 | Stok Var | https://robiz.net/servobracket | 2,2 mm Al |
| 9 | Servo braket | Robotistan | Çok Fonksiyonlu Servo Motor Tutucu | 63,70 | Tükendi | https://www.robotistan.com/cok-fonksiyonlu-servo-motor-tutucu | |
| 9 | Servo braket | Pazarama (Alkatronik) | Servo Motor Metal Montaj Parçası Braket | 180,83 | Stokta | https://www.pazarama.com/servo-motor-metal-montaj-parcasi-braket-mg995-mg996r-s3003-td-8120mg-aluminyum-tutucu-p-ALK01001329 | |
| 10 | Uzun U | Robiz | Uzun U Servo Bracket | 88,20 | Stok Var | https://robiz.net/longubracket | 2 mm Al |
| 10 | Uzun U | Pazarama (Alkatronik) | Uzun U Servo Motor Metal Montaj Parçası Braket | 149,09 | Stokta | https://www.pazarama.com/uzun-u-servo-motor-metal-montaj-parcasi-braket-mg995-mg996r-s3003-td-8120mg-aluminyum-tutucu-p-ALK01001596?magaza=alkatronik | |

### 2. Önerilen seçim (ajanın)

| # | Kalem | Satıcı | Birim TL | Adet | Toplam TL | Durum |
|---|---|---|---|---|---|---|
| 1 | JGB37-520 60rpm enkoderli | Direnc.net | 639,29 | 4 | 2.557,16 | doğrulandı |
| 2 | 37 mm motor braketi | Robotzade | 111,72 | 4 | 446,88 | fiyat doğrulandı; JGB37 uyumu teyitsiz |
| 3 | Hex kaplin 6→12 mm | Motorobit | 120,00 | 4 | 480,00 | doğrulandı |
| 4 | Arazi tekerleği 125×58 | Robotistan (mavi) | 353,63 | 4 | 1.414,52 | doğrulandı |
| 5 | 40×40 ağır sigma K10 | CNC Marketi | 908,32/m | 2,70 m | 2.452,46 | doğrulandı (kesim ücretsiz) |
| 6 | Geniş köşe bağlantı K10 | CNC Marketi | 24,68 | 4 | 98,72 | doğrulandı |
| 7 | T-somun M6 K10 + M6x16 civata | CNC Marketi | 3,78 + 3,50 | 40 + 40 | 291,20 | doğrulandı |
| 8 | M5×40 dişi-dişi distans | — | ~40 | 4 | ~160 | tahmini |
| 9 | Çok amaçlı servo braketi | Robiz | 88,20 | 2 | 176,40 | doğrulandı |
| 10 | Uzun U servo braketi | Robiz | 88,20 | 1 | 88,20 | doğrulandı |
| | **Toplam** | | | | **≈8.165** | kargo hariç |

Gerekçeler: Motor için stokta ve spec'e uyan tek TR satıcı Direnc. Kaçık mile resmi uyan Pololu PL-1084 (1.493,10 TL, 3,3 kat pahalı). Robotistan tekerlek + Motorobit kaplin = 1.894,52 TL; Motorobit kaplinli tekerlek 4 adet 2.400 TL. Sigma kesim listesi 2×500, 3×260, 1×700, 1×200; 2,70 m (≈20 mm testere payı). Tam 3 m = 2.724,96 TL.

### 3. Kargo
Direnc 1.500 TL (2.557 → ücretsiz). Robotistan 1.500 TL (1.414,52 → ücretli; 5. yedek tekerlekle ücretsiz). Motorobit 2.500 TL (480 → ücretli). CNC Marketi 132 TL, 2.400 TL üzeri ücretsiz (2.842,38 → ücretsiz). Robiz 1.100 TL Sürat / 1.500 TL Yurtiçi (264,60 → ücretli). Robotzade eşik görülmedi.

### 4. Açık kalanlar
- M5×40 dişi-dişi distans TR'de bulunamadı (~40 TL/adet tahmin). Alternatifler: M5 uzatma somunu, M5 saplama + 40 mm boru, baskılı burç + uzun M5 civata.
- JGB37: Direnc sayfası 6 mm D mil, Hall enkoder ve 1:90 oranını yazmıyor; datasheet'ten teyit. TR'de ikinci stoklu satıcı yok.
- Tekerlek göbeği: Robotistan 12 mm hex'i açıkça yazmıyor; Motorobit 6 mm kaplin dahil gönderiyor.
- Motor braketi kaçık mil uyumu doğrulanmadı.
- T-somun tipi montaj sırasına göre kontrol edilmeli.
- Robolink sigma 834 → 957 TL, 1 m ürün tükendi.

## Ajan 2: işlemci, sensörler, ses ve görüntü

**Yöntem:** Fiyat ve stok ürün sayfalarının HTML'inden okundu: JSON-LD ve T-Soft `PRODUCT_DATA` alanları (`total_sale_price` KDV dahil, `available`, `quantity`); SAMM Market'te JSON-LD ve `stockCount`.

**Dikkat:** WebFetch özetleri Robotistan'da gizli duran "Tükendi" bloğunu okuyup yanlış sonuç veriyor. Pi 5 8GB ve LCD (C) sayfalarında sayfa verisi "stokta" (116 ve 99 adet), WebFetch "Tükendi" dedi. Robotistan, Direnc, Robotsepeti ve Motorobit'te fiyatların temel para birimi USD, sayfada TL gösteriliyor; fiyatlar günlük değişebilir.

### 1. Ham bulgular

| # | Kalem | Satıcı | Sayfadaki ürün adı | Birim TL (KDV dahil) | Stok | URL | Not |
|---|---|---|---|---|---|---|---|
| 1 | Pi 5 8GB | Robotistan | Raspberry Pi 5 8GB | 11.966,22 | Stokta (116) | https://www.robotistan.com/raspberry-pi-5-8-gb | 26.09'da tükenmişti. Satış 1 adetle sınırlı |
| 1 | Pi 5 8GB | SAMM | Raspberry Pi 5 - 8 GB | 12.057,68 | Stokta (122) | https://market.samm.com/raspberry-pi-5 | Resmi TR distribütörü |
| 1 | Pi 5 8GB | Direnc | Raspberry Pi 5 - 8GB | 12.204,69 | Stokta (3) | https://www.direnc.net/raspberry-pi-5-8gb | |
| 1 | Pi 5 8GB | Motorobit | Raspberry Pi 5 - 8GB | 13.320,00 | Tükendi | https://www.motorobit.com/raspberry-pi-5-8gb | |
| 1 | Pi 5 8GB | Robotsepeti | Raspberry Pi 5 - 8Gb | 16.329,24 | Stokta | https://www.robotsepeti.com/raspberry-pi-5-8gb | |
| 1 | Pi 5 8GB | Robolink | Raspberry Pi 5 - 8GB | 6.745,50 | Tükendi | https://www.robolinkmarket.com/raspberry-pi-5-8gb | Eski fiyat olabilir |
| 2 | Soğutucu | SAMM | Raspberry Pi 5 Aktif Soğutucu | 308,19 | Stokta (497) | https://market.samm.com/raspberry-pi-5-aktif-sogutucu | Resmi |
| 2 | Soğutucu | Robotistan | Raspberry Pi Active Cooler | 314,34 | Stokta (280) | https://www.robotistan.com/raspberry-pi-active-cooler-en | Resmi |
| 2 | Soğutucu | Robolink | Raspberry Pi 5 Aktif Soğutucu | 399,00 | Stokta (16) | https://www.robolinkmarket.com/raspberry-pi-5-aktif-sogutucu | |
| 2 | Soğutucu | Direnc | Raspberry Pi 5 Aktif Fanlı Soğutucu | 395,20 | Tükendi | https://www.direnc.net/raspberry-pi-5-aktif-fanli-sogutucu | Arama listesinden |
| 2 | Soğutucu | Robotsepeti | Raspberry Pi 5 Aktif Soğutucu Heatsink - 5V | 412,88 | Stokta (9) | https://www.robotsepeti.com/raspberry-pi-5-aktif-sogutucu-heatsink | Resmi olup olmadığı belirsiz |
| 3 | microSD | SAMM | Raspberry Pi 64GB A2 Class Hafıza Kartı | 2.166,16 | Stokta (313) | https://market.samm.com/raspberry-pi-64gb-a2-class-hafiza-karti | Resmi, A2 |
| 3 | microSD | Vatan | Sandisk Extreme Pro 64 GB (200MB/s) | 2.249,00 | Stokta | https://www.vatanbilgisayar.com/sandisk-extreme-pro-64-gb-hafiza-karti-200mb-s.html | microSDXC SDSQXCU-064G, A2 |
| 3 | microSD | SAMM | SanDisk Extreme Pro 64GB | 1.350,18 | Tükendi | https://market.samm.com/sdsqxcu-064g-gn6ma-sandisk-extreme-pro-64gb-200-90mb-s-microsdxc-uhs-i-a2-v30-hafiza-karti | |
| 3 | microSD | Direnc | Samsung EVO Plus 64GB 95 MB/s | 900,82 | Tükendi | https://www.direnc.net/samsung-evo-plus-64gb-95-mb/s-microsdhc-kart | A1, A2 değil |
| 4 | Kamera M3 | Robotistan | Raspberry Pi Camera Module 3 | 1.791,36 | Tükendi | https://www.robotistan.com/raspberrypi-camera-module | Standart |
| 4 | Kamera M3 | SAMM | Raspberry Pi Kamera Modül 3 | 2.246,77 | Tükendi (0) | https://market.samm.com/raspberry-pi-kamera-3 | |
| 4 | Kamera M3 | Robotizmo | Raspberry Pi Kamera Modül 3 | 2.255,49 | Tükendi | https://www.robotizmo.net/raspberry-pi-kamera-modul-3 | |
| 4 | Kamera M3 | Robolink | Raspberry Pi Kamera Modül 3 - Standart Lens | 2.817,00 | Tükendi | https://www.robolinkmarket.com/raspberry-pi-kamera-modul-3 | |
| 4 | Kamera M3 | Robotsepeti | Kamera Modülü 3 Standart SC1223 | 2.941,66 | Tükendi (0) | https://www.robotsepeti.com/raspberry-pi-kamera-kamera-modulu-3-imx708-12mp-autofocus-75-fov | Arama listesinden |
| 4 | Kamera M3 | Özdisan | RASPBERRY Pİ KAMERA V3 ORİJİNAL | fiyat yok | 0 | https://www.ozdisan.com/p/tek-kart-bilgisayar-modulleri-867/raspberry-raspberry-p-kamera-v3-1199863 | |
| 4 | Kamera M3 | Adafruit | Camera Module 3 Standard | 29,25 USD | InStock | https://www.adafruit.com/product/5657 | (t) ithal |
| 4 | (spec dışı) | Robotsepeti | Kamera Modülü 3 NOIR / Wide | 2.521,43 / 3.887,80 | Stokta | https://www.robotsepeti.com/raspberry-pi-kamera-modulu-3-noir | NoIR ve Wide istenmiyordu |
| 5 | FPC kablo | SAMM | Raspberry Pi 5 Kamera FPC Kablosu (200mm) | 70,44 | Stokta (147) | https://market.samm.com/raspberry-pi-5-kamera-fpc-kablosu | Resmi SC1128; 300 mm 140,89 |
| 5 | FPC kablo | Robolink | Raspberry Pi 5 Kamera FPC Kablosu - 200mm | 84,00 | Stokta (23) | https://www.robolinkmarket.com/raspberry-pi-5-kamera-fpc-kablosu-200mm | |
| 5 | FPC kablo | Robotsepeti | Raspberry Pi 5 Kamera için FPC Kablosu - 200mm | 91,25 | Stokta (43) | https://www.robotsepeti.com/raspberry-pi-5-kamera-icin-fpc-kablosu-200mm | |
| 6 | 7" LCD | Robotistan | WaveShare 7 Inch HDMI Kapasitif Dokunmatik LCD - 1024x600 (C) | 2.758,18 | Stokta (99) | https://www.robotistan.com/7-hdmi-kapasitif-dokunmatik-lcd-ekran-1024x600 | Paket: HDMI kablosu var, micro HDMI yazmıyor |
| 6 | 7" LCD | Robotistan | WaveShare 7 inch HDMI Rezistif Dokunmatik LCD | 2.903,45 | Stokta (49) | https://www.robotistan.com/7-inch-hdmi-rezistif-dokunmatik-lcd-1024x600 | 26.09 referansı; (C) değil |
| 6 | 7" LCD | Direnc | Raspberry 7 Inch HDMI Lcd C Ekran 1024×600 IPS | 2.931,97 | Stokta (8) | https://www.direnc.net/raspberry-7inch-hdmi-lcd-c-1024600-ips-supports-various-systems-waveshare | |
| 6 | 7" LCD | SAMM | Raspberry Pi 7 inç 1024x600 HDMI Kapasitif IPS LCD (C) | 3.052,58 | Stokta (51) | https://market.samm.com/raspberry-pi-7-hdmi-dokunmatik-ips-lcd-c-ekran | Paket: HDMI + HDMI→micro HDMI kablo |
| 6 | 7" LCD | Amazon.com.tr | WaveShare 7 Inch HDMI Kapasitif LCD (C) | 3.551,88 | Stokta | https://www.amazon.com.tr/dp/B09RMQSPPX | |
| 6 | 7" LCD | Robotsepeti | Waveshare 7inch HDMI LCD (C) | 4.082,31 | Stokta (10) | https://www.robotsepeti.com/waveshare-7inch-hdmi-lcd-c-ic-test-board | |
| 6 | 7" LCD | Motorobit | WaveShare 7 Inch (C) 1024x600 | 5.100,00 | Stokta (13) | https://www.motorobit.com/waveshare-7-inch-c-1024x600-dokunmatik-hdmi-ekra | |
| 7 | µHDMI kablo | Robotistan | HDMI Erkek Mikro HDMI Erkek Altın Uçlu Kablo - 1.5 M | 114,30 | Stokta (322) | https://www.robotistan.com/hdmi-erkek-mikro-hdmi-erkek-altin-uclu-kablo-1 | 1,5 m |
| 7 | µHDMI kablo | Robolink | HDMI - Micro HDMI Kablo 1.5M | 126,00 | Stokta (11) | https://www.robolinkmarket.com/hdmi-micro-hdmi-kablo-15m-al-4281 | |
| 7 | µHDMI kablo | SAMM | Orijinal Raspberry Pi Mikro Hdmi - Hdmi Kablo (SC0224) | 234,81 | Stokta (21) | https://market.samm.com/orijinal-raspberry-pi-mikro-hdmi-hdmi-kablo | ~235 mm, HDMI ucu dişi |
| 8 | ESP32 | Robolink | ESP32-WROOM-32D Wifi Bluetooth Geliştirme Modülü | 355,50 | Stokta (8) | https://www.robolinkmarket.com/esp32-wroom-32d-wifi-bluetooth-gelistirme-modulu | Pin sayısı sayfada yok |
| 8 | ESP32 | Direnc | ESP32-WROOM-32D Wifi Bluetooth Geliştirme Board | 377,76 | Stokta (1929) | https://www.direnc.net/esp32-wroom-32d-wifi-bluetooth-gelistirme-board | 26.09'da 275,22 TL |
| 8 | ESP32 | Robotistan | ESP32 ESP-32S WiFi+BT Geliştirme Kartı (30 Pin) | 416,14 | Stokta (1161) | https://www.robotistan.com/esp32-esp-32s-wifi-bluetooth-dual-mode-gelistirme-karti | 30 pin; ESP-WROOM-32 (32D değil) |
| 9 | PCA9685 | SAMM | PCA9685 16 Kanal I2C PWM/Servo Sürücü Kartı (Klon) | 197,15 | Stokta (7) | https://market.samm.com/pca9685-16-kanal-i2c-pwm-servo-surucu-karti-klon | |
| 9 | PCA9685 | Robotistan | PCA9685 16 Kanal I2C PWM/Servo Sürücü Kartı (Klon) | 241,71 | Stokta (52) | https://www.robotistan.com/pca9685-16-kanal-i2c-pwmservo-surucu-karti-klon | |
| 9 | PCA9685 | Robolink | PCA9685 16 Kanal 12-bit PWM Sürücü | 345,00 | Tükendi | https://www.robolinkmarket.com/pca9685-16-kanal-12-bit-pwm-surucu | 26.09 referansı |
| 9 | PCA9685 | Motorobit | 16 Kanal I2C PWM/Servo Sürücü Kartı PCA9685 | 390,00 | Stokta (16) | https://www.motorobit.com/16-kanal-i2c-pwmservo-surucu-karti-pca9685 | |
| 10 | BNO055 | Robotistan | BNO055 9DOF Sensör Modül | 753,10 | Stokta (5) | https://www.robotistan.com/bno055-9dof-sensor-modul | Muadil, 3,3/5 V regülatörlü |
| 10 | BNO055 | Robotistan | Boardoza BNO055 IMU Sensör Modülü | 1.146,02 | Stokta (6) | https://www.robotistan.com/boardoza-bno055-imu-sensor-modulu | |
| 10 | BNO055 | Robotsepeti | Adafruit BNO055 STEMMA QT | 2.974,68 | Stokta (8) | https://www.robotsepeti.com/adafruit-bno055-9-dof-mutlak-oryantasyon-imu-breakout-sensor | Orijinal Adafruit |
| 11 | HC-SR04 | Robolink | HC-SR04 Arduino Ultrasonic Mesafe Sensörü | 54,00 | Stokta (131) | https://www.robolinkmarket.com/hc-sr04-arduino-ultrasonic-mesafe-sensoru | |
| 11 | HC-SR04 | Direnc | HC-SR04 Arduino Ultrasonik Mesafe Sensörü | 58,12 | Stokta (1735) | https://www.direnc.net/arduino-ultrasonic-sensor-hc-sr04 | |
| 11 | HC-SR04 | Robotistan | HC-SR04 Ultrasonik Mesafe Sensörü | 62,51 | Stokta (26) | https://www.robotistan.com/hc-sr04-ultrasonik-mesafe-sensoru | |
| 12 | Mik. (bütçe) | Amazon.com.tr | Audio-Technica ATR4750 USB Tüm Yönlü Kuğu Boynu | 1.962,11 | Son 1 adet | https://www.amazon.com.tr/dp/B086CV7FWS | Omni; Linux UAC doğrulanmadı |
| 12 | Mik. (bütçe) | Amazon.com.tr | Boya BY-M100UA Kompakt USB Mikrofon | 1.199,90 | Stokta | https://www.amazon.com.tr/dp/B097HRS4TP | Yönlülük yazmıyor |
| 12 | Mik. (iyi) | Robotsepeti | ReSpeaker Lite 2 Mikrofon Uzak Alan AI Ses Kartı | 2.587,46 | Stokta (37) | https://www.robotsepeti.com/respeaker-lite-2-mikrofon-uzak-alan-ai-ses-tanima-ve-isleme-karti | XMOS XU316, USB/I2S, çıplak kart |
| 12 | Mik. (iyi) | Robotistan | ReSpeaker Mic Array v2.0 | 6.520,70 | Stokta (7) | https://www.robotistan.com/respeaker-mic-array-v20-eng | 4 mikrofon, XVF-3000 |
| 13 | MAX98357A | Amazon.com.tr | SANEC MAX98357 I2S 5V 3W Class-D | 227,23 | Stokta | https://www.amazon.com.tr/dp/B0HHTWJWYG | Muadil |
| 13 | MAX98357A | Robotsepeti | Adafruit MAX98357 3W Class D I2S | 728,81 | Stokta (50) | https://www.robotsepeti.com/adafruit-3w-class-d-amplifikator-breakout-karti-i2s | Orijinal Adafruit |
| 14 | Hoparlör | Motorobit | Speaker 4 ohm 3W 40mm | 105,00 | Stokta (1762) | https://www.motorobit.com/speaker-4-ohm-3w-40mm | |
| 14 | Hoparlör | Aletler.com.tr | 4 Ohm 3W Hoparlör 4cm | 68,99 | Belirsiz | https://www.aletler.com.tr/urun/4-ohm-3w-hoparlor-4cm | |
| 15 | Buton | Robotistan | 43mm LED Arcade Basmalı Buton Kırmızı | 74,42 | Stokta (80) | https://www.robotistan.com/43mm-led-arcade-basmali-buton-kirmizi | 43 mm, anlık |
| 15 | Buton | Direnc | 22mm Kırmızı Işıklı Yaylı Buton 1NO/1NC | 269,48 | Stokta (10) | https://www.direnc.net/22mm-kirmizi-yayli-buton-1no1nc | 22 mm panel tipi |

### 2. Önerilen seçim (ajanın)

| # | Kalem | Satıcı | Birim TL | Adet | Toplam TL | Stok | Durum |
|---|---|---|---|---|---|---|---|
| 1 | Pi 5 8GB | Robotistan | 11.966,22 | 1 | 11.966,22 | Stokta* | doğrulandı |
| 2 | Active Cooler | Robotistan | 314,34 | 1 | 314,34 | Stokta | doğrulandı |
| 3 | microSD 64GB A2 | SAMM | 2.166,16 | 1 | 2.166,16 | Stokta | doğrulandı |
| 4 | Camera Module 3 | Robotistan | 1.791,36 | 1 | 1.791,36 | **Tükendi** | fiyat doğrulandı, stok yok; yedek Adafruit 29,25 USD ithal |
| 5 | FPC kablo 200mm | SAMM | 70,44 | 1 | 70,44 | Stokta | doğrulandı |
| 6 | 7" HDMI LCD (C) | Robotistan | 2.758,18 | 1 | 2.758,18 | Stokta* | doğrulandı |
| 7 | µHDMI→HDMI | Robotistan | 114,30 | 1 | 114,30 | Stokta | doğrulandı (1,5 m) |
| 8 | ESP32 30 pin | Robotistan | 416,14 | 1 | 416,14 | Stokta | doğrulandı (WROOM-32) |
| 9 | PCA9685 | SAMM | 197,15 | 1 | 197,15 | Stokta (7) | doğrulandı |
| 10 | BNO055 | Robotistan | 753,10 | 1 | 753,10 | Stokta (5) | doğrulandı (muadil) |
| 11 | HC-SR04 | Robotistan | 62,51 | 3 | 187,53 | Stokta | doğrulandı |
| 12b | Mikrofon (öneri) | Robotsepeti ReSpeaker Lite | 2.587,46 | 1 | 2.587,46 | Stokta (37) | doğrulandı |
| 13 | MAX98357A | Robotsepeti (Adafruit) | 728,81 | 1 | 728,81 | Stokta | doğrulandı |
| 14 | Hoparlör | Motorobit | 105,00 | 1 | 105,00 | Stokta | doğrulandı |
| 15 | Bas-konuş butonu | Robotistan | 74,42 | 1 | 74,42 | Stokta | doğrulandı (43 mm) |
| | **Toplam** | | | | **24.230,61** | | kamera hariç 22.439,25 |

\* Robotistan stok bilgisi WebFetch özetiyle çelişiyor.

Gerekçeler: Robotistan tek sepette en ucuz/ucuza yakın; Pi 5 yedeği SAMM (12.057,68, resmi distribütör, 122 stok). Mikrofonda ReSpeaker Lite öneriliyor (XMOS DSP gürültü bastırma, UAC, bütçe mikrofondan ~625 TL pahalı); ATR4750'de DSP yok.

### 3. Kargo
Robotistan / Direnc / Robolink / SAMM / Vatan: 1.500 TL. Motorobit: 2.500 TL. Robotsepeti: 1.250 TL? (yalnız arama özetinden). Eşik altı ücret hiçbir sayfadan okunamadı.

### 4. Açık kalanlar
1. Camera Module 3 (standart) hiçbir TR satıcıda stokta değil (Robotistan, SAMM, Robolink, Robotsepeti, Robotizmo, Özdisan). Stok alarmı ya da Adafruit ithal.
2. Robotistan stok çelişkisi (Pi 5, LCD): sipariş öncesi tarayıcıdan bakılmalı.
3. ESP32: 30 pini açıkça yazan Robotistan kartı ESP-WROOM-32; kod ve pin düzeni aynı.
4. 1 m'den kısa µHDMI erkek-erkek kablo bulunamadı. SAMM LCD (C) paketinde HDMI→micro HDMI kablo var diyor; kutu içeriği doğrulanırsa 7. kalem gereksiz.
5. 30 mm arcade buton bulunamadı; 43 mm seçildi, uymazsa Direnc 22 mm (269,48).
6. BNO055 seçilen muadil; orijinal Adafruit 2.974,68 TL.
7. ReSpeaker Lite'ın USB (UAC) firmware'iyle gelip gelmediği Seeed wiki'den kontrol edilmeli.
8. Açılamayan siteler: Akakçe, Hepsiburada, Trendyol, n11, Teknosa, incehesap, Farnell TR, PiShop (403); Komponentci, Havyatech (DNS).
9. 26.09 referanslarındaki değişimler: Direnc ESP32 275,22 → 377,76; Robolink PCA9685 345 (tükendi); Robotistan 7" referansı (C) değil rezistif, 2.903,45 TL.

## Ajan 3: servolar, motor sürücüleri, güç ve güvenlik

Fiyatların hepsi ürün sayfasından okundu, KDV dahil; sayfada "+KDV" yazanlara %20 eklendi. Oturum sonunda WebSearch/WebFetch kullanım sınırına takıldı, kalan kontroller tarayıcıyla yapıldı.

### 1. Ham bulgular

| # | Kalem | Satıcı | Sayfadaki ürün adı | Birim TL | Stok | URL | Not |
|---|---|---|---|---|---|---|---|
| 1 | DS3218MG | Robocombo | DSSERVO DS3218 20kg Servo Motor - 180 Derece - Su | 959,40 | Stokta (225) | https://www.robocombo.com/dsservo-ds3218-20kg-servo-motor-180-derece-su--4151 | Teknik tabloda "Model: DS3218MG"; dişli malzemesi yazmıyor |
| 1 | DS3218MG | Motorobit | DS3218MG 20KG Waterproof Digital Servo Motor | 1.290,00 | Stokta (10+) | https://www.motorobit.com/ds3218mg-20kg-waterproof-digital-servo-motor | 180° |
| 1 | DS3218MG | Görsu | DS3218MG 20KG Su Geçirmez Dijital Servo Motor | 1.291,26 (1.076,05+KDV) | Stokta | https://gorsuelektronik.com/tr-urun-ds3218mg-20kg-su-gecirmez-dijital-servo-motor | Metal dişli |
| 1 | DS3218MG | Robotsepeti | DSServo DS3218MG 20kg … 180°, IP66 | 1.560,88 | Stokta | https://www.robotsepeti.com/dsservo-ds3218mg-20kg-su-gecirmez-dijital-servo-motor-180 | |
| 1 | DS3218MG | Robolink (ref.) | DS3218MG 20Kg Dijital Servo Motor | 1.594,50 | Tükendi | https://www.robolinkmarket.com/ds3218mg-20kg-dijital-servo-motor | |
| 2 | MG996R | Robocombo | Tower Pro MG996R Metal Dişli Dijital Servo Motor 180 Derece | 197,78 | Stokta (64, kritik) | https://www.robocombo.com/tower-pro-mg996r-metal-disli-dijital-servo-motor-180-derece | |
| 2 | MG996R | Motorobit | MG996R Servo Motor 180 Derece (Tower Pro) | 282,00 | Stokta (100+) | https://www.motorobit.com/mg996r-metal-disli-servo-motor | İçte plastik dişli var |
| 2 | MG996R | Robotsepeti | Tower Pro MG996R Servo Motor 180 Derece | 256,35 | Stokta | https://www.robotsepeti.com/tower-pro-mg996-r-servo-motor-180 | |
| 2 | MG996R muadil | Kartal Otomasyon | KO MG996R Servo Motor | 233,44 | Belirsiz | https://www.kartalotomasyon.com.tr/urun/mg996r-servo-motor | |
| 2 | MG996R | Robotistan (ref.) | MG996R Yüksek Torklu Servo Motor - 180 Derece | 230,99 | Tükendi | https://www.robotistan.com/mg996-13-kg-servo-motor | |
| 2 | MG996R | Robolink | MG996R Servo Motor | 291,00 | Tükendi | https://www.robolinkmarket.com/tower-pro-mg996r-servo-motor | "Klon" |
| 3 | BTS7960 | Direnc.net | BTS7960B 40 Amper Motor Sürücü Modülü | 232,47 | Stokta | https://www.direnc.net/bts7960b-40-amper-motor-surucu-modulu-1 | IBT-2 tipi; eski referans URL ana sayfaya gidiyor |
| 3 | BTS7960 | Makermarketim | BTS7960B 40 Amper Motor Sürücü Modülü | 277,85 | Stokta | https://www.makermarketim.net/bts7960b-40-amper-motor-surucu-modulu | |
| 3 | BTS7960 | Robotistan / Robolink / Robotsepeti / Motorobit | BTS7960B | 258,97 / 390,00 / 360,20 / 450,00 | Hepsi Tükendi | https://www.robotistan.com/bts7960b-40-amper-motor-driver-board | |
| 4 | XL4016 | Motorobit | XL4016 8A DC-DC Step Down (XH-M401) | 240,00 | Stokta (10+) | https://www.motorobit.com/xl4016-8a-dc-dc-step-down-voltage-regulator | Sürekli 5 A, 8 A'de fan şart |
| 4 | XL4016 | Robotronik | XL4016 8A DC-DC Step Down Potanslı | 170,10 | Stokta (22) | https://www.robotronik.com.tr/xl4016-8a-dc-dc-step-down-voltaj-regulatoru-potansli-a0188 | |
| 4 | XL4016 | Ulutaş | XL4016 LED 8A Dijital Voltaj Düşürücü | 275,68 | Stokta (90) | https://www.ulutaselektronik.com/urun/xl4016-led-8a-dc-dc-ayarlanabilir-dijital-voltaj-dusurucu-regulator-modulu | |
| 5 | Akü | Limacell (gecersunenerji) | Limacell Enerji 12 Volt 24 Ah Lifepo4 batarya | 4.713,43 | Sipariş üzerine üretim | https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya | 12,8 V, 30 A sürekli / 45 A anlık, 307 Wh; ölçü yok |
| 5 | Akü | Limacell (gecersunenerji) | Limacell Enerji 12 Volt 18 Ah Lifepo4 batarya | 4.271,55 | Sipariş üzerine | https://www.gecersunenerji.com/12-volt-18-ah-lifepo4-batarya | 230 Wh |
| 5 | Akü | Merter Elektronik | Orbus 12.8 Volt 20 Amper LifePO4 Akü LIT-12-20 | 6.038,46 | Tükendi | https://www.merterelektronik.com/orbus-12.8-volt-20-amper-lityum-lifepo4-aku-lit-12-20 | 181×77×175 mm, 3 kg, BMS |
| 5 | Akü | Enerjimar | Orbus 12 Volt 20 Amper Lityum İyon Akü | 4.704,00 | Stokta yok | https://enerjimar.com/orbus-12-volt-20-amperlityum-iyon-aku | "Li-ion" yazıyor |
| 5 | Akü | Trendyol (Pil Servisi) | 12V 18Ah LiFePO4 Batarya | 3.950,00 | Son 2 ürün | https://www.trendyol.com/pil-servisi/12v-18ah-lifepo4-batarya-p-1151302447 | BMS/ölçü yok |
| 5 | Akü (t) | ExpertPower | 12V 20Ah LiFePO4 EP1220 | 129,99 USD | Stokta yok | https://www.expertpower.us/products/ep1220-20ah | BMS 20 A |
| 6 | Şarj | UserPil | 14.4 Volt 6 Amper Lifepo4 Şarj Cihazı (4s) | 1.642,30 (1.368,58+KDV) | Stokta | https://userpilbatarya.com/urun/14-4-volt-6-amper-lifepo4-sarj-cihazi-4s/ | CC-CV |
| 6 | Şarj | Pil Yurdu | 14.6V(4S) 6A CcCv LiFePO4 Şarj Cihazı | 1.947,60 | Stokta yok | https://pilyurdu.com/14-6v4s-6a-cccv-lifepo4-sarj-cihazi-12v-6a/ | |
| 7 | Acil stop | Elektrix | EMAS Acil Stop Mantar 40mm Emergency Etiketli B200E-E | 231,66 + kargo | Stokta | https://www.elektrix.com/acil-stop-mantar-40mm-emergency-etiketli | 1NK, çevirmeli, 22 mm montaj |
| 7 | Acil stop | Kartal Otomasyon | B200E60 60mm Mantar Acil Stop Butonu NO | 267,70 | Belirsiz | https://www.kartalotomasyon.com.tr/B200E60-60mm-Mantar-Acil-Stop-Butonu-NO,PR-55175.html | Sayfa "NO" diyor |
| 7 | Acil stop | Akakçe (ref.) | 22mm mantar stop | — | — | https://www.akakce.com/kumanda-butonu/en-ucuz-22mm-mantar-stop-butonu-fiyati,817168446.html | Ürün artık yok |
| 8 | Sigorta kutusu | Motorobit | 6 Channel Auto Blade Fuse Box | 309,00 | Stokta (100+) | https://www.motorobit.com/6-channel-auto-blade-fuse-box | 5A, 10A, 2×15A, 2×20A sigorta dahil |
| 8 | 30A sigorta | Motorobit | 30 Amp Car Fuse - Blade Fuse | 4,20 | Belirsiz | https://www.motorobit.com/arama?q=b%C4%B1%C3%A7ak+sigorta | Yalnız arama listesi |
| 8 | Ana sigorta yuvası | Hepsiburada (allestock) | Allestock Kablolu Kapaklı Bıçak Sigorta Yuvası - Tekli | 495,00 | Stokta | https://www.hepsiburada.com/allestock-kablolu-kapakli-bicak-sigorta-yuvasi-tekli-pm-HBC00002M7LNF | 12 AWG, 30 A |
| 8 | Sigorta yuvası | Direnc.net | Sigorta Yuvası - Kablolu 30cm | 37,78 | Belirsiz | https://www.direnc.net/sigota-yuvasi-kablolu-30cm | 18 AWG, 30 A için ince |
| 9 | XT60 | Direnc.net | XT60 Plug 60A Li-Po Konnektör Takım | 21,50 / çift | Stokta | https://www.direnc.net/xt60-plug-60a-li-po-konnektor | |
| 9 | XT60 | Robotsepeti | XT60 Konnektör - Erkek / - Dişi | 21,01 + 21,61 | Stokta | https://www.robotsepeti.com/xt60-konnektor-erkek | |
| 10 | Ana anahtar | Motorobit | ASW-A01 100A ON-OFF Battery Disconnect Switch | 276,00 | Stokta (10+) | https://www.motorobit.com/asw-a01-100a-on-off-battery-disconnect-switch | |
| 10 | Ana anahtar | Motorobit | 56-00026 125A Battery Disconnect Switch | 156,00 | Stokta (10+) | https://www.motorobit.com/56-00026-125a-battery-disconnect-switch | |
| 11 | 12 AWG | Motorobit | 12 AWG Silicone Cable Red / Black - 1 Meter | 126,00 / m | Stokta | https://www.motorobit.com/12-awg-silicone-cable-red-1-meter | |
| 11 | 12 AWG | F1Depo | 12 AWG Silikon Kablo 1 Metre | 84,00 / m | Belirsiz | https://www.f1depo.com/urun/12-awg-silikon-kablo-1-metre-kirmizi-renk | |
| 11 | 18 AWG | Motorobit | 18 AWG Silicone Cable Red / Black - 1 Meter | 42,00 / m | Stokta | https://www.motorobit.com/18-awg-silicone-cable-red-1-meter | |
| 12 | 2200µF 16V | Motorobit | 2200uF 16V Electrolytic Capacitor 10x20mm | 4,20 | Stokta | https://www.motorobit.com/2200uf-16v-electrolytic-capacitor-10x20mm | |
| 12 | 2200µF 16V | Direnc.net | 2200uF 16V Kondansatör 10x20mm | 4,94 | Stokta | https://www.direnc.net/2200uf-16v | |
| 13 | Wago 221-413 | Trendyol (WAGO) | WAGO 221-413 3'lü (10 ADET) | 328,00 / 10'lu | Tükeniyor | https://www.trendyol.com/wago/221-413-3-lu-yayli-tirnakli-klemens-10-adet-p-1041174151 | |
| 13 | Wago 221-415 | Trendyol (WAGO) | WAGO 221-415 5'li Adet Fiyatı | 83,00 / adet | Son 1 ürün | https://www.trendyol.com/wago/221-415-5-li-yayli-tirnakli-klemens-adet-fiyati-p-43493710 | |
| 13 | Wago | Star Akım | Wago 221-413 / 221-415 | 20,07 / 31,80 adet | Stokta | https://www.starakim.com/buat-klemens-tirnakli-3-lu-122946 | 50'li / 25'li paket |
| 13 | Makaron | Direnc.net | 750 Parça Isı ile Daralan Makaron Paketi | 232,47 | Stokta | https://www.direnc.net/750-parca-isi-ile-daralan-makaron-paketi | |

### 2. Önerilen seçim (ajanın)

| # | Kalem | Satıcı | Birim TL | Adet | Toplam TL | Durum |
|---|---|---|---|---|---|---|
| 1 | DS3218MG | Robocombo | 959,40 | 4 (+1 yedek) | 3.837,60 (+959,40) | doğrulandı |
| 2 | MG996R (Tower Pro) | Robocombo | 197,78 | 6 (+2 yedek) | 1.186,68 (+395,56) | doğrulandı |
| 3 | BTS7960 | Direnc.net | 232,47 | 2 (+1 yedek) | 464,94 (+232,47) | doğrulandı |
| 4 | XL4016 8A | Motorobit | 240,00 | 3 | 720,00 | doğrulandı |
| 5 | LiFePO4 12,8V 24Ah | Limacell | 4.713,43 | 1 | 4.713,43 | doğrulandı (ölçü teyitsiz) |
| 6 | LiFePO4 şarj 6A | UserPil | 1.642,30 | 1 | 1.642,30 | doğrulandı |
| 7 | Emas B200E-E acil stop | Elektrix | 231,66 | 1 | 231,66 | doğrulandı |
| 8 | Sigorta kutusu + 2×30A + ana yuva | Motorobit / Hepsiburada | 309 + 4,20 + 495 | | 812,40 | doğrulandı |
| 9 | XT60 çift | Direnc.net | 21,50 | 5 | 107,50 | doğrulandı |
| 10 | Akü ayırıcı anahtar ASW-A01 | Motorobit | 276,00 | 1 | 276,00 | doğrulandı |
| 11 | 12 AWG 2+2 m, 18 AWG 5+5 m | Motorobit | 126 / 42 | | 924,00 | doğrulandı |
| 12 | 2200µF 16V | Motorobit | 4,20 | 4 | 16,80 | doğrulandı |
| 13 | WAGO 221-413 (10'lu) + 221-415 ×5 + makaron | Trendyol / Direnc | | | 975,47 | 221-415 stok yetersiz |
| | **Toplam** | | | | **17.496,21** (yedekler 1.587,43 dahil) | kargo hariç |

### 3. Kargo
Robocombo 2.000 TL (altında 150 TL). Motorobit 2.500 TL. Direnc 1.500 TL. Limacell "Kargo bedava". Elektrix 10.000 TL (ücretli).

### 4. Açık kalanlar
1. Akü: Limacell 24 Ah'ın ölçü, ağırlık, kasa tipi sayfada yok; sipariş üzerine üretim. 181×77×167 mm yuvaya sığdığı satıcıya sorulmalı. Ölçüsü tutan Orbus LIT-12-20 stokta yok.
2. UserPil şarj cihazı adında "14,4 V"; kesme gerilimi teyit edilmeli.
3. MG996R: orijinal Tower Pro'da bile iç dişliler plastik (Motorobit/Robotistan açıklaması).
4. DS3218MG: Robocombo dişli malzemesini belirtmiyor; 270° versiyonu TR'de yok.
5. XL4016: uzun süreli kullanımda 5 A öneriliyor; Pi 5 V/5 A hattı sınırda.
6. Ana sigorta yuvası pahalı (495 TL); ucuz alternatifler stokta yok.
7. Emas B200E60: Kartal sayfası "NO" diyor, üreticiye göre 1NC.
8. WAGO 221-415 Trendyol'da 1 adet; alternatif Star Akım 25'li paket.
9. XT60 Direnc 21,50 TL/çift diğerlerinin yarısı; Amass mı muadil mi teyit edilmeli.
10. Açılamayan: n11, Çiçeksepeti, Cimri, Akakçe, Trendyol'un bazı ürün sayfaları (403); Doğuş Elektrik, Komponentci, Saykil, Atakale (DNS).

## Ajan 4: 3D baskı, lazer kesim, hırdavat, kur, kargo

Hiçbir şey satın alınmadı, sepete eklenmedi, form gönderilmedi. Fiyatlar sayfadan veya sayfa kaynağındaki ürün verisinden (T-Soft `PRODUCT_DATA`, Shopify JSON, schema.org) okundu. Akakçe, Cimri, Trendyol, n11 ve Hepsiburada hem WebFetch hem curl ile **403** verdi.

### 1. Ham bulgular

| # | Kalem | Satıcı/kaynak | Ürün/hizmet | Fiyat TL (KDV dahil) | Stok | URL | Not |
|---|---|---|---|---|---|---|---|
| 1 | PETG | Microzey (resmi site) | PETG Siyah 1,75 mm 1 kg (HS PETG kategorisi) | **359,00** (liste 489, %27 indirim) | Var (quantity 145) | https://microzey.com/petg-siyah | KDV %20 dahil (sale_price 299,17 + KDV). Beyaz ve gri sayfaları 404. |
| 1 | PETG | Akakçe | Microzey PETG Siyah 1 kg | Açılmadı | – | https://www.akakce.com/filament/en-ucuz-microzey-petg-siyah-1-75mm-1-kg-fiyati,1676232605.html | 403. 565,28 TL'lik referans yeniden doğrulanamadı. |
| 1 | PETG | FilamentMarketim | Elas PETG 1,75 mm 1 kg siyah | **549,00** (havale 534,73) | InStock | https://www.filamentmarketim.com/elas-1.75-mm-siyah-petg-filament-1kg | Sayfada KDV ibaresi yok. 2.500 TL üzeri Elas alımında sepette ek %10 indirim var. |
| 1 | PETG | Ventatek | Filamix Hyper PETG Siyah 1 kg | **564,25** | "Kritik stok" | https://ventatek.com/filamix-hyper-petg-siyah-filament-1.75mm-1-kg | Schema fiyatı 470,21 KDV hariç, ×1,2 = 564,25 |
| 1 | PETG | FilamentMarketim | Filamix Hyper PETG (siyah/beyaz/gri) | **587,42** | Var | https://www.filamentmarketim.com/filamix-hyper-petg-filament | |
| 1 | PETG | Porima (resmi site) | Porima PETG Siyah RAL9005 1 kg / 3 kg | **673,44** / **2.014,56** | Var | https://porima3d.com/products/porima-petg-filament | "KDV dahildir" yazıyor |
| 1 | PETG | Robocombo | Porima PETG Beyaz 1 kg | 797,04 | **Yok** | https://www.robocombo.com/porima-petg-filament-1.75mm-beyaz-1kg-3587 | |
| 1 | PETG | Robolink | eSUN PETG Siyah 1 kg | 820,50 | **Yok** | https://www.robolinkmarket.com/esun-petg-filament-siyah-175mm-1000gr | |
| 1 | PETG | Robotsepeti | eSUN PETG Düz Siyah 1 kg | 873,49 | **Yok** | https://www.robotsepeti.com/esun-1-75mm-petg-duz-filament-siyah-1kg | |
| 2 | Baskı hizmeti | 3dprinterdestek | Rehber: "Türkiye'de… 0.50-2 TL/gram" | 0,50–2 TL/g | – | https://3dprinterdestek.com/3d-baski-maliyet-hesaplama | Kılavuz aralığı, firma teklifi değil |
| 2 | Baskı hizmeti | Yazdır Gelsin | STL yükleyip anında fiyat alınıyor | Sayfada TL/g yok. Kaynak koddaki malzeme tablosunda PETG `birim_fiyat` 0,85 (birimi yazmıyor) | – | https://yazdirgelsin.com/3d-baski-fiyati-hesapla | 2.000 TL üzeri kargo ücretsiz |
| 2 | Baskı hizmeti | Armut | 3D baskı ortalama fiyat | 500–4.000 / sipariş (200+ adet: 1.000–5.000) | – | https://armut.com/fiyatlari/3d-baski_12669 | Eylül 2026 |
| 3 | Al levha | Metal Reyonu | Alüminyum Levha 3 mm, alaşım 5754 | **395,00 TL/kg** | InStock | https://metalreyonu.com.tr/urun/aluminyum-levha-3-mm | KDV belirtilmemiş. Yalnız tam boy satılıyor, "özel boy kesimi yapılmamaktadır". |
| 3 | Al levha | Alüminyumburada | 5754-H111 3 mm | Fiyat görünmüyor ("₺ -,-") | Tam boy stok yok | https://aluminyumburada.com/aluminyum-levha/5754-H111-3mm | |
| 3 | Al kesim | Armut | Alüminyum lazer kesim | 1.000–5.000. Örnekler: 1.500 (300×300×4 mm, 17.09.2026), 500 (500×500×4 mm, 510 delik, 11.04.2026) | – | https://armut.com/fiyatlari/aluminyum-lazer-kesim_5918 | |
| 3 | Al kesim | lazermakine.com | Dakika fiyatı rehberi | Alüminyum ~40–50 TL/dk, ahşap ~20–35 TL/dk | – | https://lazermakine.com/lazer-kesim-dakikasi-kac-tl/ | 19.12.2025 tarihli |
| 3–4 | Online kesim | Cutmatik / KesiMAX / Robotistan / AKS / Lazerkesimci | DXF yükle, anında fiyat | Yayınlanmış birim fiyat yok | – | https://cutmatik.com/ · https://www.kesimax.com.tr/ · https://www.robotistan.com/lazer-kesim-servisi | Cutmatik fiyatları KDV hariç. Teklif için DXF gerekiyor, yüklenmedi. |
| 4 | Kontrplak | Lazerci | Huş 6 mm 76×76 cm | 7 EUR + KDV (≈467,8 TL, TCMB EUR 55,6880 ile) | Var | https://www.lazerci.com/kontrplak-urunleri?pg=1 | 5 mm yok |
| 4 | Kontrplak | iAhşap | Marin huş 4 mm 50×50 cm | 372,70 | Belirtilmemiş | https://www.iahsap.com/product-page/50x50-cm-kal%C4%B1nl%C4%B1k-18-mm-marin-hu%C5%9F-kontraplak-su-kontras%C4%B1-suya-dayan%C4%B1kl%C4%B1 | |
| 4 | Kontrplak | Kontrplaklar.com | Huş 4 mm 125×250 cm | 937,50 | Listelenmiş | https://kontrplaklar.com/hus | KDV belirsiz, 5 mm yok |
| 4 | Ahşap kesim | Armut | Ahşap lazer kesim | 250–1.800. Örnek: 40×40 cm kontrplak şablon 500 TL | – | https://armut.com/fiyatlari/ahsap-lazer-kesim_46788 | |
| 5 | Civata seti | Robolink | M3 YSB vida-somun-pul 220 parça | **411** | Var (7) | https://www.robolinkmarket.com/m3-ysb-vida-somun-ve-pul-seti-220-parca | Malzeme belirtilmemiş |
| 5 | Civata seti | Robolink | M4 YSB 395 parça | **657** | Var (8) | https://www.robolinkmarket.com/m4-ysb-vida-somun-ve-pul-seti-395-parca | Malzeme belirtilmemiş |
| 5 | Civata seti | Robolink | M5 YSB 188 parça | **363** | Var (4) | https://www.robolinkmarket.com/m5-ysb-vida-somun-ve-pul-seti-188-parca | Malzeme belirtilmemiş |
| 5 | Civata seti | Amazon.com.tr (Ayaz Bağlantı) | YSB Vida Seti M3 M4 M5, 1533 parça (3 kutu) | 1.885,15 | Var | https://www.amazon.com.tr/dp/B0HC453JDQ | "Alaşım çelik", teslimat ücretsiz |
| 5 | Civata seti | Amazon.com.tr (NetzerHırdavat) | Netzerkoz 855 adet M3–M6 YHB vida-somun-pul | 999,00 | 10 adet kaldı | https://www.amazon.com.tr/dp/B0GYXRZBRB | Malzeme "Demir". Havşa baş. |
| 5 | Civata seti | Amazon.com.tr (Ayaz) | M3 imbus paslanmaz 500 p / M4 imbus paslanmaz 335 p (DIN 912 A2-70) | 948,53 / 954,67 | Var | https://www.amazon.com.tr/dp/B0HBQ57BNF · https://www.amazon.com.tr/dp/B0HBPV3B4P | |
| 5 | Civata seti | Amazon.com.tr (Site Hırdavat) | M5 imbus civata-somun-rondela 284 p | 1.067,06 | 2–3 günde kargo | https://www.amazon.com.tr/dp/B08DFZPC98 | Malzeme belirtilmemiş |
| 5 | M3 burç | Direnc.net | Siyah M3 distans seti 200 parça (plastik) | **261,53** | Var (16) | https://www.direnc.net/siyah-m3-distans-vida-seti-200-parca | |
| 5 | M3 burç | Motorobit | 100 parça M3 siyah plastik aralayıcı | **360,00** | Var (24) | https://www.motorobit.com/100-piece-m3-black-plastic-spacer-set-standoff | Schema'daki 300,00 KDV hariç |
| 5 | M3 burç | Voltaj | M3 metal stand-off seti | 301,93 | 20+ | https://www.voltaj.net/araliyici-distans-m3-stand-off-seti-pmu35985 | KDV durumu belirsiz |
| 5 | M3 burç | Robotistan | 200 adet M3 plastik siyah | 322,67 | **Tükendi** | https://www.robotistan.com/200-adet-m3-plastik-siyah-mesafe-burcu-seti | |
| 5 | M3 burç | Robo90 | 120 adet M3 pirinç distans kutulu | 347,76 | **Yok** | https://www.robo90.com/120-adet-m3-distans-standoff-seti-kutulu | |

### 2. Önerilen tablo

| # | Kalem | Seçim | Birim | Miktar | Toplam TL | URL | Durum |
|---|---|---|---|---|---|---|---|
| 1 | PETG | Microzey PETG Siyah 1 kg | 359,00 | 5 | **1.795,00** | https://microzey.com/petg-siyah | doğrulandı (kargo belirsiz) |
| 3 | Al kesim | Lazer atölyesi: 3 mm 5754 plaka + küçük parçalar + 2 büküm | set | 1 | **1.500** (aralık 1.000–2.000) | Armut ve lazermakine referansları | tahmini |
| 4 | Kontrplak kesim | 5 mm huş (yoksa 4 veya 6 mm), 340×500 delikli | adet | 1 | **500** (aralık 400–700) | Armut ahşap örneği | tahmini |
| 5 | Civata | Robolink M3 + M4 + M5 YSB setleri | 411 + 657 + 363 | 1'er | **1.431,00** | Yukarıdaki Robolink URL'leri | doğrulandı |
| 5 | M3 burç | Direnc.net siyah M3 200 parça | 261,53 | 1 | **261,53** | https://www.direnc.net/siyah-m3-distans-vida-seti-200-parca | doğrulandı |
| | **Toplam (yazıcı varsa)** | | | | **≈5.487,53 TL ≈ 112,3 USD** (48,8780 ile), kargo hariç | | |
| 2 | *Alternatif: bölümde yazıcı yoksa* | PETG baskı hizmeti, 1,5 TL/g | 1,5 TL/g | 3.700 g | **≈5.550** (aralık 3.700–7.400) | https://3dprinterdestek.com/3d-baski-maliyet-hesaplama | tahmini, 1. satırın yerine geçer (toplam ≈9.242,53 TL) |

**Gerekçe ve hesaplar**
- **Filament:** Stoktaki en ucuz seçenek Microzey. %27'lik indirim kampanya fiyatı, bitebilir. Yedek plan Elas: 5 × 549 = 2.745 TL, 2.500 TL üzeri %10 indirimle 2.470,50 TL, kargo ücretsiz. Porima 3 kg + 2 × 1 kg = 3.361,44 TL.
- **Alüminyum:** 340×500×3 mm = 510 cm³ × 2,67 g/cm³ ≈ **1,36 kg**. Küçük parçalar 26,9 cm³ ≈ 0,07 kg. Toplam **≈1,43 kg**. Malzeme: 1,43 × 395 ≈ 566 TL; %30 fire ile ≈735 TL; fiyat KDV hariçse ≈880 TL. Kesim yolu ≈3,3 m, ≈27 delgi; makine süresi birkaç dakika × 40–50 TL/dk ≈ 150–250 TL. Hazırlık ücreti, asgari iş bedeli ve büküm eklenince Armut örnekleriyle (500–1.500 TL) birlikte 1.000–2.000 TL.
- **Kontrplak:** Malzeme 4 mm tam levhadan orantılanırsa ≈51 TL; 6 mm 76×76 levha ≈468 TL. Kesim ≈2,4 m, CO₂ lazerle 3–5 dk × 20–35 TL/dk. Asgari iş bedeli baskın; Armut'taki 40×40 cm şablon örneği 500 TL.
- **Baskı hizmeti:** 3,7 kg × 1–2 TL/g. Yazdır Gelsin'in PETG parametresi (0,85, büyük olasılıkla TL/g) yalnız malzeme payı gibi duruyor; süre ücreti ayrıca ekleniyor.
- **Civata:** Robolink setleri en ucuz, stokta ve KDV dahil, ama malzeme belirtilmemiş. Paslanmaz imbus yolu: Amazon'da M3 + M4 + M5 toplamı 2.970,26 TL. Tek kutu: Ayaz YSB M3/M4/M5, 1.885,15 TL.

### 3. Kur (USD/TRY)

| Kaynak | Tarih | Değer | URL |
|---|---|---|---|
| **TCMB döviz satış** | 25.09.2026, bülten 2026/181 | **48,8780** (döviz alış 48,7901, efektif satış 48,9514) | https://www.tcmb.gov.tr/kurlar/202609/25092026.xml |
| TCMB today.xml | Hâlâ 25.09.2026'yı gösteriyor | 48,8780 | https://www.tcmb.gov.tr/kurlar/today.xml |
| Investing (TR) Cuma kapanışı | 25 Eyl 2026 | **48,9496** (açılış 48,8780 / yüksek 49,1377 / düşük 48,6030) | https://tr.investing.com/currencies/usd-try-historical-data |
| Yahoo Finance (çapraz kontrol) | 25.09 günlük kapanış | 48,9494 | https://query1.finance.yahoo.com/v8/finance/chart/TRY=X?interval=1d&range=1mo |

EUR döviz satış 55,6880 (TCMB, 25.09). Öneri: TCMB döviz satış 48,8780. Serbest piyasayla fark yaklaşık %0,15.

### 4. Kargo

| Satıcı | Ücretsiz kargo eşiği | Eşik altı ücret | Kaynak |
|---|---|---|---|
| Robotistan | 1.500 TL (Yurtiçi/Aras) | Sayfada yok, sepette görünüyor | https://www.robotistan.com/kargo-ve-teslimat |
| Direnc.net | 1.500 TL ("Kargo Bedava" bandı) | Sayfada yok | https://www.direnc.net/ |
| Robolink Market | 1.500 TL, KDV dahil (SSS: "DHL için") | DHL 89,90 / HepsiJet 119 / Aras 139 | https://www.robolinkmarket.com/teslimat-kosullari |
| Robotsepeti | Sitede bulunamadı | Bulunamadı | https://www.robotsepeti.com/teslimat-kosullari.shtm |
| Motorobit | 2.500 TL (MNG-DHL) | Sayfada yok | https://www.motorobit.com/ |
| Microzey | Bant 2.000 TL, teslimat sayfası 1.500 TL (çelişkili) | "Alıcıya aittir", tutar yok | https://microzey.com/teslimat-kosullari |
| FilamentMarketim | 1.500 TL | "109 TL'den başlar" | Elas ürün sayfası |
| Porima / Ventatek / Yazdır Gelsin | 1.500 / 3.000 / 2.000 TL | – | İlgili sayfalar |

### 5. Açık kalanlar
- Microzey kargosu: 1.795 TL'lik sipariş 1.500 ile 2.000 TL arasında; hangi eşik geçerli belli değil. 6. makara eklenirse (2.154 TL) iki kurala göre de ücretsiz.
- Akakçe referansı (565,28 TL) 403 yüzünden yeniden doğrulanamadı. Trendyol, Hepsiburada ve Cimri de açılmadı.
- Alüminyum ve kontrplak kesimi tamamen tahmini. Net fiyat için DXF'i KesiMAX, Cutmatik veya Robotistan lazer servisine yükleyip anında teklif almak gerekiyor (Cutmatik KDV hariç veriyor). Delik çapı ve kesik ölçüleri varsayım.
- 5 mm huş bulunamadı; piyasada 4 veya 6 mm yaygın, kalınlık kararı verilmeli.
- Metal Reyonu 395 TL/kg'nin KDV durumu yazmıyor ve yalnız tam levha satılıyor; yalnız referans.
- Civata malzemesi Robolink ve Ayaz YSB setlerinde belirtilmemiş. Paslanmaz şartsa imbus setler (≈2.970 TL).
- Baskı hizmeti: gerçek fiyat için STL'leri Yazdır Gelsin'e yükleyip teklif almak gerekiyor; baskı hacmi ayrıca kontrol edilmeli.
- Eşik altı kargo ücretleri Robotistan, Direnc ve Motorobit'te sepete eklemeden görülemiyor.


## 4. V2 eklemeleri (2 Ekim 2026)

Hocanın geri bildirimiyle 7" yüz ekranı kalktı; göğüse 10,1" ekran, kafaya iki yuvarlak göz ekranı girdi. Araştırmayı bir
Claude Opus alt ajanı yaptı; orkestratör seçilen iki ürünün fiyatını ve stoğunu sayfanın JSON-LD verisinden yeniden okudu.

| Kalem | Satıcı | Sayfa verisi | KDV dahil | Stok |
|---|---|---|---|---|
| Waveshare 10.1" HDMI LCD (B) kasalı, 1280 × 800 | Robotsepeti | `price` 10272.51 (KDV hariç) | 12.327,01 TL | InStock |
| Waveshare 1.28" yuvarlak LCD (GC9A01), ×2 | Robotistan | `price` 863.43 (KDV dahil) | 863,43 TL | InStock |
| Alternatif: Waveshare 10.1" (E), 1024 × 600 | Robotistan | `price` 6607.48 | 6.607,48 TL | InStock (alt ajan) |
| Alternatif: GC9A01 muadil, çizimi yok | Motorobit | `price` 450.00 (KDV hariç) | 540,00 TL | InStock (alt ajan) |

- Direnc.net'teki 10,1" 1280 × 800 muhafazalı ekran `OutOfStock` (7.807,92 TL KDV dahil).
- 10,1" ekran ayrı 5 V besleme ister: arka ışık açıkken ≈ 750 mA (Waveshare wiki SSS). Dokunmatik için USB kablosu gerekir.
  Paketten HDMI ve USB kablosu çıkıp çıkmadığı doğrulanmadı.
- Filament: V2 baskı parçaları CAD'den ≈ 4,4 kg (V1 ≈ 3,7 kg) → V2'de 6 × 1 kg.
- Daha büyük SPI yuvarlak ekran bulunamadı (Robotistan 3,4" yuvarlak HDMI arabirimli, 5.408,83 TL).
