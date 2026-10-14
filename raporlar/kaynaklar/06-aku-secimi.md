# 06 — Akü seçimi (tekerlekli insansı robot V3)

Tarih: 11 Ekim 2026. Tüm fiyat ve stok değerleri satıcı sayfalarından 11.10.2026'da okundu. Hiçbir satıcıyla iletişime geçilmedi, sipariş verilmedi. "Sayfada yok" = sayfada yazmıyor, tahmin edilmedi. "Tahmini" = kaynaksız ya da türetilmiş. Görsel özet: `raporlar/aku-secimi/rapor.html`.

## Karar

**Net 1. tercih: Victron SuperPack 12,8/20 (BAT512020705), Atakale, 12.680,70 TL.** Üreticinin datasheet'inde ölçü 167 × 181 × 77 mm, yani CAD'deki yuva zarfıyla birebir aynı; 30 A sürekli / 80 A (10 sn) BMS teorik tepe akımı (17,6 A) rahat karşılıyor, M5 cıvatalı kutup ve entegre koruma anahtarı var, kütle yalnız +0,2 kg. Bedeli: Limacell 24 Ah'ın 2,7 katı fiyat, %17 az enerji (256 Wh) ve satıcıda tek adet stok. **Anahtar kural:** Limacell, 24 Ah ürünün ≤ 186 × 79 × 172 mm (tercihen 181 × 77 × 167) olduğunu ve M5/M6 cıvata kutup verdiğini yazılı teyit ederse 2. tercih 1. tercih olur (aynı güvenlik sınıfı, 1/2,7 fiyat, +%20 enerji, 8 saat için sınırda yeterli).

## 1. Güç bütçesi

### Yük kataloğu

| Yük | Hat | Tipik akım / güç | Tepe akım / güç | Kaynak |
|---|---|---|---|---|
| JGB37-520 12 V 60 dev/dk enkoderli ×4 (2× BTS7960 sürer) | 12 V (aküden) | Yüksüz 0,08–0,15 A/motor (Direnc sayfası), 0,06 A (Aslong tablosu). Motor başına: düz zeminde sabit hız ≈ 0,24 A, 0,5 m/s² ivmelenme ≈ 0,47 A, 5° rampada 0,5 m/s² ≈ 0,86 A (taban-analiz.json torklarından türetildi, tahmini) | Durma akımı 2,4–2,8 A/motor, 4 motor 9,6–11,2 A. 2,4 A: 76 dev/dk satıcı listesi; 2,8 A: 21 kg·cm ÷ 9 kg·cm × 1,2 A ölçeklemesi (tahmini; 60 dev/dk için akım yayımlanmamış) | Direnc.net JGB37-520 sayfası (yüksüz 0,08–0,15 A, 21 kg); Aslong JGB37-520 tablosu (oran 90: 66 dev/dk, yüksüz 60 mA, nominal 3 kg·cm / 240 mA, durma 9 kg·cm / 1,2 A); makerselectronics 76 dev/dk listesi (arama özeti) |
| BTS7960 sürücü ×2 | 12 V | Boşta ≈ 7 µA (ihmal); verim varsayımı %95 | Akım sınırı tipik 43 A; kart başı 2 motor paralel, 5,6 A'ya kadar | Infineon BTS7960 datasheet (components101 kopyası) |
| Röle bobini (12 V, 40 A, ISO mini) | 12 V | ≈ 0,12 A (1,5 W), robot açıkken sürekli (tahmini) | aynı | Genel röle değeri; kaynak yok, ölçülecek |
| XL4016 ×3 (Pi 5,1 V · çevre 5 V · servo 6 V) | 12 V → 5 / 6 V | Boşta toplam ≈ 0,4 W (tahmini); verim varsayımı %88 (%85–90) | Modül 8 A (uzun sürede 5 A önerilir). Servo hattı 8 A × 6 V = 48 W ile kendiliğinden sınırlı | XL4016 datasheet: tepe verim %96 (12 V çıkış); 12,8 V → 5 V düşüşte %85–90 beklenir (tahmini) |
| Raspberry Pi 5 8GB + Active Cooler + USB mikrofon | 5,1 V | Boşta ≈ 3,2 W, kamera + USB + fan ile ≈ 4 W; tam CPU yükü ≈ 9,8 W | ≈ 12 W (2,4 A); resmî besleme 5 V / 5 A | Jeff Geerling Pi 5 ölçümleri (boşta 2,4–3,2 W, stres 9,8 W); raspberry.tips (≈ 12 W, fan ≈ 0,5 W) |
| Nextion NX1060P101_011 10,1" göğüs ekranı | 5 V | %100 parlaklıkta 800 mA (4,0 W); uyku 170 mA; %60 parlaklık ≈ 2,5 W (tahmini) | 4,0 W (0,8 A) | donanim/datasheet/README.md (Nextion sayfası) |
| 7" yüz ekranı (Waveshare HDMI LCD (C)) | 5 V | Arka ışık açık ≈ 490 mA (2,45 W); kapalı ≈ 90 mA | 500 mA (2,5 W); Waveshare ≥ 500 mA besleme ister | Waveshare wiki, 7inch HDMI LCD (C) |
| ESP32 + PCA9685 + BNO055 + 3× HC-SR04 + MAX98357A + Camera Module 3 | 5 V | ESP32 Wi-Fi alım 95–100 mA; sonar ≈ 15 mA × 3; BNO055 ≈ 12 mA; PCA9685 ≈ 10 mA; amfi konuşmada ≈ 0,5 W; kamera ≈ 0,7 W (tahmini) | ESP32 Wi-Fi gönderim 240 mA; amfi 3 W (4 Ω, %10 THD); toplam ≈ 6 W | Deneyap Kart ESP32 güç tablosu (Espressif datasheet); Adafruit MAX98357A rehberi; HC-SR04, BNO055, PCA9685, kamera değerleri genel bilgi (doğrulanmadı) |
| Servolar: 4× DS3218MG (omuz) + 6× MG996R (dirsek, bilek, kafa) | 6 V | MG996R çalışırken 0,5–0,9 A; DS3218MG yükte ≈ 0,5–1,0 A (tahmini); tutarken 5–30 mA | DS3218MG durma 2,6 A (6,8 V); MG996R durma 2,5 A (6 V). Hepsi birden dursa 25,4 A (152 W) olurdu, ama XL4016 8 A × 6 V = 48 W'ta keser | aifitlab.com DS3218-MG tablosu (1,8 A @5 V, 2,6 A @6,8 V); MG996R Tower Pro datasheet kopyaları (2,5 A @6 V, çalışma 500–900 mA); 01-donanim-maliyet.md |


### Senaryolar (yük tarafı W; aküden çekilen toplam ve akım dahil)

| Kalem (yük tarafı, W) | Boşta / sunum bekleme | Normal etkileşim | Yoğun | Tepe (teorik) |
|---|---|---|---|---|
| Raspberry Pi 5 (5,1 V) | 4,0 | 6,5 | 10,0 | 12,0 |
| Nextion 10,1" (5 V) | 2,5 | 3,5 | 4,0 | 4,0 |
| 7" yüz ekranı (5 V) | 1,7 | 2,45 | 2,5 | 2,5 |
| ESP32 + sensör + amfi + kamera (5 V) | 1,2 | 2,5 | 3,5 | 6,0 |
| Servolar ×10 (6 V) | 1,5 | 6,0 | 24,0 | 48,0 |
| Tahrik ×4 motor (12 V) | 0,3 | 5,0 | 20,0 | 134,4 |
| **Aküden çekilen toplam** (DC-DC %88, BTS %95, röle 1,5 W, XL4016 boşta 0,4 W dahil) | **14,6 W** | **31,0 W** | **73,0 W** | **≈ 226 W** |
| Akü akımı (12,8 V) | 1,1 A | 2,4 A | 5,7 A | 17,6 A |


Boşta = yüz ve göğüs ekranı açık (%60 parlaklık), kollar ev pozunda, robot duruyor. Normal = konuşma + ara sıra jest (servo ortalaması 6 W), zamanın ~%15'inde sürüş (ort. 5 W), ekranlar parlak. Yoğun = sürekli sürüş (ort. 20 W; rampa ve ivmelenme dahil) + kollar / kafa sürekli hareketli (ort. 24 W) + Pi tam yük. Tepe = 4 motor aynı anda durma (11,2 A) + servo hattı XL4016 sınırında (8 A) + Pi 12 W + 5 V hattı 12,5 W; fiilen olmaz, BMS şartının üst sınırıdır. Yük tarafı değerleri tahmindir (yalnız Nextion akımı datasheet'ten); dayanaklar yukarıdaki tabloda.

**Hesap:** aküden çekilen = (Pi + 5 V hattı + servo) ÷ 0,88 + tahrik ÷ 0,95 + röle 1,5 W + XL4016 boşta 0,4 W. Örnek normal: (6,5 + 3,5 + 2,45 + 2,5 + 6,0) ÷ 0,88 + 5,0 ÷ 0,95 + 1,9 = 31,0 W. Tepe: 134,4 ÷ 0,95 + 48 ÷ 0,88 + 12 ÷ 0,88 + 12,5 ÷ 0,88 + 1,9 = 225,8 W → 17,6 A (12,8 V). Gerçekçi tepe: 4 × 1,5 A × 12 V ÷ 0,95 + 19 ÷ 0,88 + 12 ÷ 0,88 + 12,5 ÷ 0,88 + 1,9 = 127 W → 9,9 A.

### OZET.md ile karşılaştırma

|  | Boşta | Normal | Yoğun |
|---|---|---|---|
| tasarim/freecad/OZET.md (taban-analiz.json) | 11,1 W (22,2 sa) | 32,8 W (7,5 sa) | 81,2 W (3,0 sa) |
| Bu rapor | 14,6 W | 31,0 W | 73,0 W |
| Fark | +3,5 W (+%32) | −1,8 W (−%5) | −8,2 W (−%10) |

Normal senaryo OZET.md ile %5 içinde uyuşuyor. Boşta fark üç yerden: röle bobini (1,5 W) ve XL4016 boşta akımı (0,4 W) OZET'te yoktu; iki ekran toplam 3,0 W yerine 4,2 W (7" ekran için Waveshare 490 mA ölçümü, %60 parlaklıkla). Yoğunda fark Pi'nin 12 W yerine 10 W, tahrik ve servonun 25 W yerine 20 / 24 W alınmasından. OZET'in süreleri 307 Wh × %80 ile hesaplanmış; bu raporda %81 (= %90 DoD × %90 yaşlanma payı). GC9A01 göz ekranları V3'te yok (kafada yalnız 7" yüz ekranı, kafa-analiz.json); planlama/maliyet.json hâlâ 2× GC9A01 listeliyor (V2 kalıntısı). maliyet.json göğüs ekranı olarak Waveshare 10,1" HDMI (B) yazıyor, CAD ve datasheet klasörü Nextion; güç farkı küçük (Waveshare wiki 750 mA, Nextion 800 mA).

### Tepe akım

| Durum | Güç (akü tarafı) | Akım (12,8 V) | Anlamı |
|---|---|---|---|
| Yoğun, sürekli | 73 W | 5,7 A | Sürekli çalışma noktası |
| Gerçekçi tepe: 4 motor kalkış (başına ~1,5 A) + 4 servo jesti (19 W) + Pi / ekranlar | ≈ 127 W | ≈ 9,9 A (12 V'ta 10,6 A) | Pratikte görülebilecek en yüksek akım; BMS sürekli şartı bunun üstünde olmalı |
| Teorik tepe: 4 motor durma (11,2 A) + servo hattı sınırda (48 W) + Pi 12 W + 5 V hattı 12,5 W | ≈ 226 W | ≈ 17,6 A (12 V'ta 18,8 A) | Fiilen olmaz; BMS bunu kesmeden geçirmeli ya da yazılım motor akımını sınırlamalı |
| Açılışta kapasitif şarj (4× 2200 µF servo hattı, XL4016 / BTS giriş kondansatörleri) | – | kısa darbe, onlarca-yüzlerce A (tahmini) | Victron datasheet dipnot 1: yüksek giriş kapasiteli yükte akü kesebilir, ~10 sn sonra yeniden dener. Ön şarj / NTC önerilir |

**BMS şartı:** sürekli ≥ 20 A (tercihen 30 A = ana sigorta değeri), anlık ≥ 30 A (en az 1–10 sn), şarj akımı ≥ 6 A (UserPil şarj cihazı), 4S LiFePO4 için aşırı şarj / deşarj / kısa devre / sıcaklık korumalı. 20 A BMS'li aküler (Reyvolt, Atakale paketi, ZipPil) teorik tepeyi (17,6 A) dar farkla karşılar; kalkış ivmesini yazılımda sınırlamak (rampa) gerekir.

## 2. Hedef çalışma süresi

|  | Senaryo 1: ders / sunum | Senaryo 2: tam gün fuar / tanıtım |
|---|---|---|
| Süre | 3 saat | 8 saat (6 saat alt hedef) |
| Kullanım profili | %40 bekleme, %50 normal, %10 yoğun | %35 bekleme, %50 normal, %15 yoğun |
| Ortalama güç | 28,6 W | 31,5 W |
| Gereken enerji (kullanılan) | 86 Wh | 252 Wh (6 saatte 189 Wh) |
| Gereken nominal kapasite (÷ 0,81) | **106 Wh ≈ 8,3 Ah** → 10–12 Ah yeter | **311 Wh ≈ 24,3 Ah** (6 saatte 234 Wh ≈ 18,3 Ah) → 24 Ah sınırda, 30 Ah rahat |

Kullanılabilir kapasite = nominal × 0,90 (DoD) × 0,90 (yaşlanma, soğuk, BMS payı) = × 0,81. Yeni akü ve ılık ortamda gerçek süre yaklaşık %11 daha uzundur. Peukert etkisi LiFePO4'te ihmal edildi.

**Karışım ortalaması:** ders 0,40 × 14,6 + 0,50 × 31,0 + 0,10 × 73,0 = 28,6 W; fuar 0,35 × 14,6 + 0,50 × 31,0 + 0,15 × 73,0 = 31,5 W. Nominal Wh = W × saat ÷ 0,81 (3 saat: 86 ÷ 0,81 = 106 Wh; 8 saat: 252 ÷ 0,81 = 311 Wh; Ah = Wh ÷ 12,8).

### Aküye göre süre ve şarj

| Akü (nominal) | Bekleme 14,6 W | Normal 31 W | Yoğun 73 W | Ders karışımı 28,6 W | Fuar karışımı 31,5 W | 6 A şarj süresi |
|---|---|---|---|---|---|---|
| 12 Ah · 153,6 Wh | 8,5 sa | 4,0 sa | 1,7 sa | 4,3 sa | 3,9 sa | ≈ 2,3 sa |
| 18 Ah · 230 Wh | 12,8 sa | 6,0 sa | 2,6 sa | 6,5 sa | 5,9 sa | ≈ 3,2 sa |
| 20 Ah · 256 Wh | 14,2 sa | 6,7 sa | 2,8 sa | 7,2 sa | 6,6 sa | ≈ 3,5 sa |
| 24 Ah · 307 Wh | 17,0 sa | 8,0 sa | 3,4 sa | 8,7 sa | 7,9 sa | ≈ 4,1 sa |
| 30 Ah · 384 Wh | 21,3 sa | 10,0 sa | 4,3 sa | 10,9 sa | 9,9 sa | ≈ 5,0 sa |

Süreler Wh × 0,81 ÷ güç. Şarj süresi = Ah × 0,9 ÷ 6 A + CV kuyruğu 0,5 sa (tahmini; BMS şarj akımını sınırlıyorsa uzar). UserPil 14,4 V / 6 A şarj cihazı (CC-CV): Victron'un 14,2–14,4 V absorpsiyon aralığıyla uyumlu; Limacell sayfası 14,6 V yazıyor, 14,4 V ile %95–99 doluma ulaşır (genel bilgi, doğrulanmadı). Pil Yurdu'nun 14,6 V'luk şarj cihazı Victron için fazla yüksek. Şarj yalnız 0–45 °C arasında yapılmalı (Victron datasheet).

## 3. Yuva zarfı, kütle, devrilme

| Eksen | Boş zarf | Neye göre (dosya) | Mevcut akü 181 × 77 × 167 | Pay |
|---|---|---|---|---|
| X (genişlik) | 190 mm: uzun rayların iç yüzleri x ±95 | arayuz.py UZUN_RAY_X = 115, sigma 40 mm; taban-analiz.json | 181 | 4,5 mm / yan (kayış yarıkları x 90,75–94,25 bu payda) |
| Y (yükseklik) | 80 mm: alt plaka üstü y 94,5 → elektronik katı alt yüzü y 174,5 | arayuz.py Y_RAIL0, Y_DECK0 (M5×40 burç) | 77 (y 94,5–171,5) | 3 mm; üstten geçen kayış 1,5 mm |
| Z (derinlik) | 190 mm: arka ara ray ön yüzü z −210 → orta ara ray arka yüzü z −20 | arayuz.py ARA_RAY_Z = (−230, 0, 230), sigma 40 mm; taban_rapor.py (arka 5 mm, kablo boşluğu 18 mm) | 167 (z −205…−38); kutuplar z −29'a kadar | arkada 5 mm; önde 17–18 mm (takoz z −37,5…−20,5 + kutup + kablo) |

Yuva ileri doğru uzatılamaz: orta ara ray (y 94,5–134,5) tam genişlikte engel. Yukarı alan yalnız elektronik katını yükselten daha uzun burçla açılır (M5×50 ile ≈ +10 mm; kat üstü ≈ y 236, etek orta plakası y 259: pay var gibi görünüyor, ama CAD'de çakışma taraması yeniden koşulmalı; doğrulanmadı). Kutupları üst yüze bakan standart (UPS tipi) gövde yatırılıp kutuplar öne (+Z) bakacak şekilde konmalı; üstte yalnız 3 mm var.

**En büyük sığabilecek zarf (mevcut burç, kutuplar öne bakarken): 186 (X) × 79 (Y) × 172 (Z) mm** — payların 2 mm / 1 mm / 3 mm (kutup ve kablo için ön tarafta en az 15 mm) olduğu varsayımıyla (tahmini). Yuva 181 × 77 × 167'den yalnız birkaç mm büyük. 24 Ah ve üzeri hazır kasalı akünün çoğu (örn. 166 × 175 × 125 SLA ölçüsü) bu zarfa girmez, çünkü hiçbir kenarı 79 mm'nin altında değil. Y 89 mm'ye (M5×50 burç) çıkarsa 80–89 mm kalınlıkta paketler girer.

### Kütle farkı

| Akü kütlesi | Δ | İleri / geri / yana devrilme ivmesi (m/s²) | Pay (fren 1,5 m/s²) | Rampada motor yükü (5°, 0,5 m/s²) |
|---|---|---|---|---|
| 1,5 kg (Pil Yurdu 12 Ah) | −1,3 kg | 4,90 / 4,51 / 4,52 | 3,3× / 3,0× / 3,0× | %84,9 (ivme ≤ 0,25: %72,0) |
| 2,8 kg (CAD) | 0 | 5,28 / 4,52 / 4,70 | 3,5× / 3,0× / 3,1× | %90,3 (ivme ≤ 0,25: %76,6) |
| 3,0 kg (Victron) | +0,2 kg | 5,34 / 4,52 / 4,73 | 3,6× / 3,0× / 3,2× | %91,1 (%77,3) |
| 3,5 kg | +0,7 kg | 5,48 / 4,52 / 4,80 | 3,7× / 3,0× / 3,2× | %93,2 (%79,1) |
| 4,0 kg | +1,2 kg | 5,62 / 4,52 / 4,87 | 3,7× / 3,0× / 3,2× | %95,3 (%80,8) |

Hesap: ev pozu, kablo paylı ağırlık merkezi (−0,4; 370,5; −14,4) mm, 21,66 kg; ek kütle akü merkezinde (0; 133; −121,5). Temas hattı teker merkez düzlemleri (x ±178, z ±185), devrilme ivmesi a = g·d/h. Akü, geri devrilmenin kritik doğrusunun üzerinde durduğu için geri pay değişmiyor (3,0×); ileri ve yana pay ağırlıkla artıyor, hafifleyince azalıyor. Asıl bedel motor yükü: tork kütleyle doğru orantılı, her +1 kg ≈ +%4,6 (rampada ivme sınırı 0,25 m/s² önerisi geçerli kalır). Kollar uzanık pozlardaki en küçük pay (~2,9×) bu hesapta yeniden koşulmadı; akü arkada olduğu için ileri yönde düzelmesi, geri yönde değişmemesi beklenir (tarama ile doğrulanmadı).

## 4. Aday tablosu (Türkiye)

| # | Ürün (marka / model) | Satıcı · bağlantı | Fiyat (11.10.2026) | Stok | Ölçü (mm) · kütle | BMS sürekli / anlık | Kutup | Garanti | Wh · TL/Wh | Yuvaya (186×79×172) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Victron Lithium SuperPack 12,8/20 (BAT512020705) | [Atakale](https://atakale.com/index.php?product_id=438&route=product%2Fproduct) | 12.680,70 TL (KDV dahil; hariç 10.567,25) | 1 adet (sayfada) | 167 × 181 × 77 · 3 kg (üretici datasheet; satıcı sayfasında yok) | 30 A / 80 A (10 sn); şarj 15 A (datasheet) | M5 dişli yuva (datasheet) | sayfada yok | 256 · 49,5 | Sığar: CAD zarfıyla birebir aynı |
| 2 | Victron SuperPack 12,8/20 (aynı ürün) | [Hepsiburada / KampKaravanMarket](https://www.hepsiburada.com/victron-lithium-superpack-12-8v-20ah-256wh-m5-dahili-bms-li-lifepo4-lityum-aku-pm-HBC0000M2DPYC) | 16.472,21 TL | 5 adetten az | sayfada ölçü yok (ürün adı: 256 Wh, M5, dahili BMS) | sayfada yok (datasheet: 30 / 80 A) | M5 (ürün adı) | sayfada yok | 256 · 64,3 | Sığar (aynı ürün) |
| 3 | Limacell 12 V 24 Ah (GCRSN12-24) | [gecersunenerji.com](https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya) | 4.746,02 TL (havale %4: 4.556,18, "KDV dahil"; liste fiyatında KDV notu yok) | Özel üretim, ort. 3 iş günü; "en geç 15 Ekim kargoda" | sayfada yok · sayfada yok | 30 A / 45 A (sayfa) | sayfada yok | 6 ay; özel üretim, iade yok | 307 · 15,4 | Doğrulanamadı: ölçü yok. Siparişten önce ≤ 186×79×172 yazılı teyit |
| 4 | Limacell 12 V 30 Ah (GCRSN12-30) | [gecersunenerji.com](https://www.gecersunenerji.com/12-volt-30-ah-lifepo4-batarya) | 5.932,52 TL (havale %4: 5.695,22) | Özel üretim, 3 iş günü | sayfada yok · sayfada yok | 60 A / 100 A (sayfa) | sayfada yok | 6 ay, iade yok | 384 · 15,4 | Doğrulanamadı: 384 Wh bu hacimde zor (≈ 150 Wh/L gerekir) |
| 5 | Limacell 12 V 18 Ah (GCRSN12-18) | [gecersunenerji.com](https://www.gecersunenerji.com/12-volt-18-ah-lifepo4-batarya) | 4.301,08 TL (havale %4: 4.129,03) | Özel üretim, 3 iş günü | sayfada yok · sayfada yok | 30 A / 45 A | sayfada yok | 6 ay, iade yok | 230 · 18,7 | Doğrulanamadı |
| 6 | Reyvolt 12 V 24 Ah LiFePO4 | [Hepsiburada / Reyvolt Enerji](https://www.hepsiburada.com/reyvolt-12-volt-24-ah-lifepo4-aku-pm-HBC00008ZSR31) | 5.433,67 TL | "100 adetten az"; tahmini teslim 13 Ekim | sayfada yok · sayfada yok | maks. deşarj 20 A, maks. şarj 10 A (anlık değer yok) | sayfada yok | 12 ay | 307 (sayfa 12 V yazıyor) · 17,7 | Doğrulanamadı: ölçü yok |
| 7 | Atakale LFP paketi 12,8 V 24 Ah (4S, shrink, kasasız) | [Atakale](https://www.atakale.com/index.php?route=product/product&product_id=1196) | 4.069,62 TL (KDV dahil; hariç 3.391,35) | 2 adet (sayfa) | 155 × 155 × 80 (özellik tablosu; seçenek listesinde 155×120×80 ve 80×110×170 de geçiyor) · 2,74 kg | 10 A şarj / 20 A deşarj (haberleşmesiz) | sayfada yok | 5 yıl veya %80 DC 2000 çevrim (sayfa metni) | 307 · 13,2 | 80 mm > 79: ancak M5×50 burçla (+10 mm); kasasız paket, kutu gerekir |
| 8 | Vigor 12 V 20 Ah LiFePO4 | [Atakale (.com.tr)](https://www.atakale.com.tr/index.php?route=product%2Fproduct&product_id=346) | 3.843,12 TL (KDV dahil; hariç 3.202,60) | "Stok durumu: 7 gün" | sayfada yok · sayfada yok | 30 A sürekli (sayfa); anlık yok | kutup başı seçeneği: A tip (+114,72 TL), 50² kablo (+286,80 TL) | sayfada yok | 256 · 15,0 | Doğrulanamadı: ölçü yok |
| 9 | Eko-Mobil 12,8 V 30 Ah "özel üretim" | [ekomobilsolar.com](https://www.ekomobilsolar.com/urun/12-8v-lifepo4-aku-30-ah-lifepo4-lityum-aku) | 6.004,35 TL (havale 5.704,13; sayfa 101,67 USD + KDV de yazıyor, TL'nin KDV'si belirsiz) | 30 Ah var, "3 günde kargoda"; 18 / 24 / 45 / 60 Ah tükendi | sayfada yok · sayfada yok (silindirik hücre) | 40 A BMS (sürekli / anlık ayrımı yok) | sayfada yok | 24 ay | 384 · 15,6 | Doğrulanamadı |
| 10 | Pil Yurdu 12,8 V 12 Ah LiFePO4 (çocuk arabası pil paketi, PY-10847) | [pilyurdu.com](https://pilyurdu.com/12-8v-12-ah-lifepo4-aku-cocuk-arabasi-pilpaketi/) | 5.090 TL (KDV dahil) | Stokta | 150 × 95 × 65 (sıra belirtilmemiş) · 1,5 kg | 30 A (4S balanslı BMS); anlık yok | sayfada yok | sayfada yok (14 gün iade) | 154 · 33,1 | Sığar (65 mm dikey konursa) |
| 11 | Pil Yurdu 12 V 12 Ah LiFePO4 kutulu (PY-11593) | [pilyurdu.com](https://pilyurdu.com/12-volt-12-ah-lifepo4-batarya-kutulu/) | 5.090 TL (KDV dahil) | Stokta | 15 × 10 × 10 cm · 1,48 kg | sürekli 20 A (1,6C), anlık 6 A (sayfadaki değer tutarsız) | sayfada yok | sayfada yok (14 gün iade) | 154 · 33,1 | Sığmaz: en küçük kenar 100 mm |
| 12 | Orbus LIT-12-20 (12,8 V 20 Ah) | [Merter Elektronik](https://www.merterelektronik.com/orbus-12.8-volt-20-amper-lityum-lifepo4-aku-lit-12-20) | 6.038,46 TL (KDV dahil) | Stok 0 | 181 × 77 × 175 (başka satırda 81×77×175) · 3 kg | sayfada yok | sayfada yok | sayfada yok | 256 · 23,6 | z'de 175 > 172: kablo payı kalmaz. Stokta da yok |
| 13 | Orbus 12 V 20 A (ORB-L20), "Lityum İyon" yazıyor | [Enerjimar](https://enerjimar.com/orbus-12-volt-20-amperlityum-iyon-aku) | 4.761,60 TL (eski 5.297,28) | Stokta yok | sayfada yok · sayfada yok | sayfada yok | sayfada yok | sayfada yok | – | Doğrulanamadı; kimya ve model net değil |
| 14 | Powermaster 12,8 V 20 A LiFePO4 | [Merter Elektronik](https://www.merterelektronik.com/powermaster-12.8-volt-20-amper-lityum-lifepo4-aku) | 0,00 TL (yer tutucu) | Stok 0 | sayfada yok · sayfada yok | sayfada yok | sayfada yok | sayfada yok | – | Doğrulanamadı |
| 15 | UserPil 12,8 V 12 Ah LiFePO4 (akülü araba / UPS) | [userpilbatarya.com](https://userpilbatarya.com/urun/12-8v-12ah-lifepo4-akulu-araba-ups-akusu/) | 2.305,28 TL + KDV (≈ 2.766 TL, %20 varsayımıyla) | sayfada yok | sayfada yok · sayfada yok | sayfada yok | üstte (+/−), tip yok | sayfada yok | 154 · 18,0 | Doğrulanamadı |
| 16 | Pil Servisi 12 V 18 Ah LiFePO4 | [Trendyol](https://www.trendyol.com/pil-servisi/12v-18ah-lifepo4-batarya-p-1151302447) | 3.950 TL | "Son 2 ürün" | paket yüksekliği 8 cm yazıyor (ürün ölçüsü yok) | sayfada yok | sayfada yok | 1 yıl | 230 · 17,2 | Doğrulanamadı |
| 17 | Orion 12,8 V 18 Ah 32650 4S4P 20 A BMS pil grubu | [Trendyol / Propil](https://www.trendyol.com/orion/12-8v-18ah-32650-lifepo4-4s4-20a-bms-li-batarya-grubu-p-638455577) | 6.434,01 TL | Satışta (yarın kargoda) | sayfada yok · sayfada yok (hücre grubu) | 20 A BMS (başlıkta) | sayfada yok | sayfada yok | 230 · 28,0 | Doğrulanamadı (kasasız hücre grubu) |
| 18 | Tekvolt 12,8 V 12 Ah 4S2P LiFePO4 | [Trendyol / Tekpil](https://www.trendyol.com/tekvolt-enerji/tekvolt-12-8v-12ah-4s-2p-lifepo4-lfp-bms-devreli-batarya-p-1104555183) | 2.899 TL | Satışta | sayfada yok · sayfada yok | "BMS devreli", değer yok | sayfada yok | sayfada yok | 154 · 18,9 | Doğrulanamadı |
| 19 | ZipPil 12 V 24 Ah LiFePO4 pil paketi (LP3270012v24ah) | [zippilbatarya.com](https://zippilbatarya.com/12v-24ah-lifepo4-batarya-aku) | 4.161,28 TL + KDV (≈ 4.994 TL) | Stokta yok | "özel, ölçü teyit edilecek" · ≈ 4 kg | 20 A deşarj / 10 A şarj | uçlar kablolu, kasasız | 6 ay | 288 (sayfada "288wsa") · 17,3 | Doğrulanamadı; stokta da yok |
| 20 | Electroll 12,8 V 20 Ah (BMS'li) | [Hepsiburada / n11 (arama özeti)](https://www.hepsiburada.com/12-8v-20ah-lifepo4-enerji-akusu-gelismis-bms-li-uzun-omurlu-yuksek-guvenlikli-guc-deposu-pm-HBC00008OSPFM) | arama özetinde 3.999 TL (HB), 5.999 TL (n11) | Doğrulanamadı | 2,25 kg (arama özeti) · ölçü yok | arama özetinde yok | yok | yok | 256 | Doğrulanamadı: ürün sayfaları açılmadı (HB 403 ve kategoriye yönlendirme; n11 kategoriye yönlendirme) |
| 21 | Leoch LFP1218 (12,8 V 18 Ah): yalnız ölçü referansı | [leoch.com datasheet (arama özeti)](https://www.leoch.com/uploads/ueditor/file/20231127/6383670337137618236054615.pdf) | TR'de satıcı bulunamadı (Bulgaristan'da Comet ≈ 155 € + KDV) | – | 181,5 × 77 × 167,5 · ≈ 2,6 kg | datasheet açılmadı | – | – | 230 | Yuva ölçüsünün 18 Ah sınıfına karşılık geldiğini gösterir |

Tarama: 21 ilan / ürün. Direnc.net, Robotistan, Robotsepeti ve Motorobit'te 12,8 V LiFePO4 paket bulunamadı (Direnc ve Robotistan yalnız 3,2 V hücre listeledi; Motorobit ve Robotsepeti arama sayfaları ürün listesi yüklemedi). Trendyol / Hepsiburada / n11 arama sonuçları 3–6 ilan döndürdü; Hepsiburada'daki Bataryasan 24 Ah ve AHB Batteries 24 Ah sayfaları açılınca kategoriye yönlendi (arama özetinde ≈ 6.500 TL), Electroll 20 Ah da öyle; bu yüzden doğrulanamadı ve tabloya yalnız Electroll arama özetiyle girdi. Fiyatlar KDV dahil kabul edildi (satıcı belirtmediyse not düşüldü). TL/Wh = fiyat ÷ nominal Wh. "Sayfada yok" alanları tahmin edilmedi.

## 5. Öneri

|  | 1. tercih: yuvaya birebir | 2. tercih: uzun çalışma / ucuz | 3. tercih: yedek / stokta hazır |
|---|---|---|---|
| Ürün | Victron Lithium SuperPack 12,8/20 (BAT512020705) | Limacell 12 V 24 Ah (GCRSN12-24); tam gün için 30 Ah (GCRSN12-30) | Pil Yurdu 12,8 V 12 Ah pil paketi (PY-10847) |
| Satıcı · fiyat | Atakale · 12.680,70 TL (stok 1); Hepsiburada 16.472,21 TL | gecersunenerji.com · 4.746,02 TL (30 Ah: 5.932,52 TL) | pilyurdu.com · 5.090 TL, stokta |
| Ölçü · kütle | 167 × 181 × 77 mm · 3,0 kg (üretici datasheet) | sayfada yok (özel üretim, sorulacak) · kütle yok | 150 × 95 × 65 mm · 1,5 kg |
| BMS | 30 A sürekli / 80 A 10 sn; entegre koruma anahtarı | 30 A / 45 A (30 Ah: 60 A / 100 A) | 30 A sürekli, anlık yok |
| Yuvaya sığma | Sığar, CAD ile aynı zarf; kayış ve takoz aynı kalır | Ölçü teyit edilmeden bilinmiyor | Sığar; kayış ve takoz yeniden ölçülmeli (150 × 95 mm taban) |
| Kütle farkı · devrilme | +0,2 kg · ileri 3,6×, geri 3,0×, yana 3,2× | kütle yok (benzer 24 Ah paketler 2,7–4 kg → 0…+1,2 kg); geri pay 3,0× sabit | −1,3 kg · ileri 3,3×, geri 3,0×, yana 3,0×; rampada motor %85 |
| Kapasite · süre (normal 31 W) | 256 Wh · 6,7 sa (ders karışımı 7,2 sa; fuar karışımı 6,6 sa) | 307 Wh · 8,0 sa (fuar karışımı 7,9 sa); 30 Ah 384 Wh · 10,0 sa | 154 Wh · 4,0 sa (ders karışımı 4,3 sa); tam gün yetmez |
| Tepe akımı karşılar mı | Evet (30 A sürekli, 80 A / 10 sn > 17,6 A) | Evet (30 A / 45 A); 30 Ah: 60 A / 100 A | Evet sürekli (30 A); anlık değeri bilinmiyor |
| Senaryo 1 (3 sa) · Senaryo 2 (8 sa) | Evet · hayır (öğle şarjı ya da 2. akü gerekir) | Evet · 24 Ah sınırda, 30 Ah evet | Evet · hayır |
| Fiyat farkı (1. tercihe göre) | – | −7.935 TL (24 Ah), −6.748 TL (30 Ah) | −7.591 TL |


### Akü ile birlikte alınacak / yapılacak

- **Ana sigorta 30 A** (BOM'da var): aküye ≤ 15 cm kabloyla bağla. Victron ve Limacell BMS'i 30 A sürekli olduğu için sigorta ile eşit; F1 20 A (BTS + servo) ve diğer kollar mevcut sigorta planında kalır (teorik tepe 17,6 A < 30 A).
- **Kablo:** 12 AWG silikon (BOM'da var) 30 A için yeterli (genel bilgi); akü → sigorta → ana anahtar toplam ≤ 1,5 m.
- **Terminal:** Victron için 2× M5 halka pabuç (12 AWG, Ø5,3) + yaylı pul; Limacell / Eko-Mobil siparişine "M5 veya M6 cıvata kutup" notu düş. F2 faston (6,3 mm) 30 A sürekli için uygun değil (genel bilgi, yaklaşık 15 A sınıfı). Akü ucu → XT60 (60 A) geçişi BOM'daki XT60 ile.
- **Ön şarj / inrush:** NTC inrush sınırlayıcı (≥ 30 A) ya da 10 Ω / 5 W ön şarj direnci + bypass. Victron kapasitif yükte keser (datasheet dipnot 1); acil stop sonrası röle yeniden çekilince 4× 2200 µF + XL4016 / BTS kondansatörleri bu darbeyi üretir. Değer hesabı için toplam giriş kapasitesi ölçülmeli.
- **Şarj:** mevcut UserPil 14,4 V / 6 A CC-CV cihazı olur (Victron absorpsiyon 14,2–14,4 V, şarj akımı üst sınırı 15 A). XT60 şarj girişine 10 A hat içi sigorta önerilir (öneri). 14,6 V'luk cihaz (Pil Yurdu) Victron'a verilmemeli.
- **Sabitleme:** Victron'da mevcut 2× 25 mm cırt kayış + ön takoz aynı kalır. Kasasız shrink paketlerde (Atakale, Eko-Mobil, ZipPil) ABS / PETG kutu + köpük şart; yuvadaki kayışlar silindirik hücreye doğrudan bastırmamalı.
- **CAD:** yeni akü seçilince `arayuz.py` içindeki `aku=dict(olcu=…, kutle_g=…)` ve kayış / takoz parçaları güncellenir; ağırlık merkezi ve devrilme yeniden koşulur.

## Açık işler / doğrulanacaklar

- **Limacell ölçü ve kutup tipi:** satıcıya sor (sayfada ölçü, kütle, kutup yok; özel üretim, iade yok). İstenecek: dış ölçü, kütle, kutup tipi (M5/M6), BMS sürekli / anlık akım, şarj kesme gerilimi, hücre tipi. Yazılı teyit gelmeden sipariş verme.
- **Victron:** Atakale'de stok 1 adet, Hepsiburada'da "5 adetten az". Garanti süresi iki sayfada da yok; Victron'un resmî garantisi bu raporda doğrulanmadı. Atakale fiyatı USD'ye bağlı görünüyor (sayfa başlığı "217 USD"), kur değişirse oynar.
- **Motor akımı:** JGB37-520 60 dev/dk için yayımlanmış durma / nominal akım yok. Bir motoru laboratuvar güç kaynağında tutup 12 V'ta durma akımını ölç (tahmin 2,4–2,8 A); tepe akım hesabının en belirsiz girdisi bu.
- **Servo akımı:** DS3218MG 2,6 A satıcı değeri, MG996R 2,5 A datasheet kopyası. Gerçek jest akımını ölç (güç ölçerli bench testi).
- **Pi 5 + ekranlar:** Pi'nin kamera + USB ile gerçek çekimini ve iki ekranın seçilen parlaklıktaki akımını ölç; ekran parlaklığı (4 + 2,5 W) bütçedeki en büyük ayar noktası.
- **Röle bobini ve XL4016 boşta akımı** ölçülmedi (1,9 W toplam, tahmini); boşta senaryonun %13'ü.
- **Hedef süre:** kullanım senaryosunu Duffy / hocayla netleştir (3 saat ders mi, 8 saat fuar mı). 8 saat gerekiyorsa tek akü 30 Ah sınıfı ya da öğle şarjı / ikinci akü gerekir.
- **Burç uzatma seçeneği:** M5×50 burçla yükseklik 89 mm'ye çıkar, ama çakışma taraması koşulmadı (doğrulanmadı).
- **Ürün sayfaları:** Hepsiburada ve n11 ürün sayfaları doğrudan açılmadı (403); Bataryasan 24 Ah, AHB 24 Ah, Electroll 20 Ah doğrulanamadı. Fiyat ve stok 11.10.2026'da değişebilir.
- **UserPil şarj cihazı** kesme gerilimi (adında 14,4 V) hâlâ teyitsiz (05-fiyat-arastirmasi.md açık iş 2).
- **maliyet.json:** V3'te olmayan 2× GC9A01 göz ekranı ve CAD'deki Nextion yerine yazılı Waveshare 10,1" HDMI (B) kalemleri güncellenecek (bu raporda dokunulmadı).
- **Soğuk:** LiFePO4 0 °C altında şarj edilemez (Victron BMS engeller); dış mekân kullanımı için not.

## Kaynaklar

- Proje: tasarim/freecad/OZET.md, arayuz.py, taban/taban-analiz.json, taban/taban_rapor.py, kafa/kafa-analiz.json, donanim/datasheet/README.md, planlama/maliyet.json, raporlar/kaynaklar/01 ve 05
- [Victron 12,8 V & 25,6 V Lithium SuperPack datasheet (ölçü, kütle, akım, M5, dipnotlar)](https://www.victronenergy.com/upload/documents/Datasheet-12,8V-&-25,6-Lithium-SuperPack-EN.pdf)
- [Victron SuperPack: Atakale ürün sayfası](https://atakale.com/index.php?product_id=438&route=product%2Fproduct)
- [Victron SuperPack: Hepsiburada / KampKaravanMarket](https://www.hepsiburada.com/victron-lithium-superpack-12-8v-20ah-256wh-m5-dahili-bms-li-lifepo4-lityum-aku-pm-HBC0000M2DPYC)
- [Limacell 24 Ah](https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya)
- [Limacell 30 Ah](https://www.gecersunenerji.com/12-volt-30-ah-lifepo4-batarya)
- [Limacell 18 Ah](https://www.gecersunenerji.com/12-volt-18-ah-lifepo4-batarya)
- [Reyvolt 24 Ah (Hepsiburada)](https://www.hepsiburada.com/reyvolt-12-volt-24-ah-lifepo4-aku-pm-HBC00008ZSR31)
- [Atakale 24 Ah LFP paketi](https://www.atakale.com/index.php?route=product/product&product_id=1196)
- [Vigor 20 Ah (Atakale .com.tr)](https://www.atakale.com.tr/index.php?route=product%2Fproduct&product_id=346)
- [Eko-Mobil 12,8 V özel üretim LiFePO4](https://www.ekomobilsolar.com/urun/12-8v-lifepo4-aku-30-ah-lifepo4-lityum-aku)
- [Pil Yurdu 12 Ah çocuk arabası paketi](https://pilyurdu.com/12-8v-12-ah-lifepo4-aku-cocuk-arabasi-pilpaketi/)
- [Pil Yurdu 12 Ah kutulu](https://pilyurdu.com/12-volt-12-ah-lifepo4-batarya-kutulu/)
- [Orbus LIT-12-20 (Merter)](https://www.merterelektronik.com/orbus-12.8-volt-20-amper-lityum-lifepo4-aku-lit-12-20)
- [Orbus ORB-L20 (Enerjimar)](https://enerjimar.com/orbus-12-volt-20-amperlityum-iyon-aku)
- [Powermaster 20 A (Merter)](https://www.merterelektronik.com/powermaster-12.8-volt-20-amper-lityum-lifepo4-aku)
- [UserPil 12 Ah](https://userpilbatarya.com/urun/12-8v-12ah-lifepo4-akulu-araba-ups-akusu/)
- [Pil Servisi 18 Ah (Trendyol)](https://www.trendyol.com/pil-servisi/12v-18ah-lifepo4-batarya-p-1151302447)
- [Orion 18 Ah 4S4P (Trendyol)](https://www.trendyol.com/orion/12-8v-18ah-32650-lifepo4-4s4-20a-bms-li-batarya-grubu-p-638455577)
- [Tekvolt 12 Ah (Trendyol)](https://www.trendyol.com/tekvolt-enerji/tekvolt-12-8v-12ah-4s-2p-lifepo4-lfp-bms-devreli-batarya-p-1104555183)
- [ZipPil 24 Ah](https://zippilbatarya.com/12v-24ah-lifepo4-batarya-aku)
- [Electroll 20 Ah (Hepsiburada, doğrulanamadı)](https://www.hepsiburada.com/12-8v-20ah-lifepo4-enerji-akusu-gelismis-bms-li-uzun-omurlu-yuksek-guvenlikli-guc-deposu-pm-HBC00008OSPFM)
- [Leoch LFP1218 datasheet (arama özeti)](https://www.leoch.com/uploads/ueditor/file/20231127/6383670337137618236054615.pdf)
- [UserPil 14,4 V 6 A LiFePO4 şarj cihazı](https://userpilbatarya.com/urun/14-4-volt-6-amper-lifepo4-sarj-cihazi-4s/)
- [Aslong JGB37-520 tablosu](https://www.aslongdcmotor.com/sale-14447502-12v-24v-high-torque-micro-dc-motor-low-rpm-jgb37-520-oem-odm.html)
- [Direnc.net JGB37-520 60 dev/dk](https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor)
- [DS3218-MG tablosu (aifitlab)](https://aifitlab.com/products/dsservo-ds3218-mg-servo-motor)
- [MG996R Tower Pro datasheet kopyası](https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/f2017/kmv48_rp625/kmv48_rp625/kmv48_rp625/MG996RTowerPro.pdf)
- [Pi 5 güç ölçümleri (Jeff Geerling)](https://www.jeffgeerling.com/blog/2024/new-2gb-pi-5-has-33-smaller-die-30-idle-power-savings/)
- [Pi 5 güç tüketimi derlemesi (raspberry.tips)](https://raspberry.tips/en/faq/raspberry-pi-power-consumption-update-2026-all-models-compared)
- [Waveshare 7inch HDMI LCD (C) wiki](https://www.waveshare.com/wiki/7inch_HDMI_LCD_(C))
- [Waveshare 10.1inch HDMI LCD (B) wiki](https://www.waveshare.com/wiki/10.1inch_HDMI_LCD_(B))
- [Nextion NX1060P101-011C-I](https://nextion.tech/datasheets/nx1060p101-011c-i/)
- [ESP32 güç tüketimi (Deneyap Kart, Espressif tablosu)](https://deneyapkart.org/en/docs/guc-tuketimi-esp32-2)
- [Adafruit MAX98357A](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts)
- [BTS7960B datasheet](https://components101.com/sites/default/files/component_datasheet/BTS7960B-Datasheet.pdf)
- [XL4016 datasheet (XLSEMI)](https://www.radiolocman.com/datasheet/pdf.html?di=185685)
