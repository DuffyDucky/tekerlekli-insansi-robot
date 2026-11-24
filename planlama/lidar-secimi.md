# 2B LiDAR seçimi (araştırma, 24.11.2026)

Satın alma yok. Bu dosya bir araştırma ve öneri notu; CAD'e, `planlama/maliyet.json`'a ve sipariş dosyalarına hiçbir şey
işlenmedi. Simülasyonun okuyacağı özellikler: `kod/fizik/lidar_ozellik.json`.

Etiketler: **[BULGU]** = kaynakta okunan sayı (veri sayfası, ürün sayfası, depo dosyası). **[DEĞERLENDİRME]** = bu notun
yorumu ve hesabı. **[TAHMİN]** = ölçülmedi, kaynağı yok, makul değer seçildi.

Kullanım (brief'ten): okul koridoru, tek hat, 12–40 m uzun, 1,8–3,5 m geniş, iç mekân. İş: duvara göre ortalama, engel
görme, konum belirleme. Pi 5 kafada, LiDAR tabanda, düz Python (ROS yok).

> **Kapsam uyarısı [BULGU]:** `planlama/proje-plani.md:28` LiDAR'ı, haritalamayı ve otonom gezinmeyi kapsam dışı sayıyor
> (21 Ekim 2026, otonomi iptal, ROS 2 yok). Bu not yeni bir isteğe dayanıyor. Kapsamın değişip değişmediği "Açık sorular"da.

## 1. Öneri

**Slamtec RPLIDAR C1 (C1M1)**, onaylı satıcı **Robotistan**: **3.992,85 TL** (indirimli, KDV dahil; havale 3.912,99),
stokta (ürün verisinde adet 24). Erişim 24.11.2026.

Gerekçe [DEĞERLENDİRME]:
1. Listedeki adaylar içinde **onaylı bir satıcıda bugün stokta olan en ucuz model.** LDROBOT (LD19, LD06, STL-19P) ve
   YDLIDAR (X4 Pro, X2, T-mini Pro) dört onaylı sitenin hiçbirinde stokta yok.
2. DTOF ölçüm. Siyah hedefte de 6 m menzil var. Koridor genişliği 1,8–3,5 m olduğu için robottan duvara en çok ~1,75 m
   kalır, bu da menzilin rahatça içinde. Koridor boyunca ileri bakışta beyaz hedefte 12 m görür.
3. 0,72° açısal çözünürlük. 1,75 m'de iki ışın arası ~22 mm. 10 Hz tarama, 5 kHz örnek.
4. Motor ve çekirdek tek 5 V hattan beslenir, ayrı motor beslemesi ya da PWM gerekmez. Çalışma akımı 230 mA, kalkış
   akımı 800 mA. Tabandaki çevre 5 V hattı ikisini de taşır (§ 5).
5. 55,6 × 55,6 × 41,3 mm ve 110 g. Etek üst plakasında gövdenin önüne sığar (§ 4).
6. Eski kayıttan (26.09, 4.510,85 TL, `raporlar/kaynaklar/01-donanim-maliyet.md:85`) 518 TL ucuz.

Zayıf yanı [DEĞERLENDİRME]: C1 için olgun, bakımlı bir saf Python kütüphanesi yok (§ 6). Masada ilk iş, standart tarama
kipini pyserial ile okumak.

**Yedek: Slamtec RPLIDAR A1M8**, onaylı satıcı **Direnc.net**: 8.482,32 TL, stokta. İkinci kaynak Robocombo: 8.543,00 TL,
stok 5. Sınama yöntemi üçgenleme, 0,15–12 m (R5 ve sonrası), 1° çözünürlük, 5,5 Hz, 8 kHz örnek, 115200 baud. Klasik
protokolü eski Python kütüphanelerinin (`rplidar-roboticia`) hedeflediği seri. Eksileri:
- C1'in iki katından pahalı.
- Ayrı motor beslemesi ister (VMOTO 5–10 V) ve MOTOCTL ucu var.
- Daha büyük ve ağır: 96,8 × 70,3 × 55 mm, 170 g. Ön plakada kör sektör büyür.

C1 ilk sınamada (§ 6) Pi 5'ten okunamazsa A1M8'e geçilir.

## 2. Karşılaştırma tablosu [BULGU]

Kaynaklar § 8'de. "yok" = resmî kaynakta yok, uydurulmadı.

| Model | İlke | Menzil (beyaz / siyah) | Açı, çözünürlük | Tarama / örnek | Doğruluk | Arayüz | Besleme, akım (çalışma / kalkış) | Ölçü, kütle | Lazer düzlemi tabandan |
|---|---|---|---|---|---|---|---|---|---|
| **RPLIDAR C1** | DTOF | 0,05–12 m (%70) / 0,05–6 m (%10) | 360°, 0,72° @10 Hz | 8–12 Hz (10) / 5 kHz | ±30 mm, çözünürlük 15 mm; tarama düzlemi eğimi 0–1,5° | 3,3 V TTL UART 460800 8N1, XH2.54-5P | 4,8–5,2 V; 230 (en çok 260) / 800 mA; motor iç, komutla | 55,6 × 55,6 × 41,3 mm, 110 g; IP54, 40 klx | **29,8 mm** (çizimde yazılı) |
| RPLIDAR A1M8 | üçgenleme | 0,15–12 m (R5) / yok | 360°, 1° @5,5 Hz | 1–10 Hz (5,5) / 8 kHz | veri sayfasında yalnız çözünürlük: <0,5 mm (<1,5 m), mesafenin <%1; web: %1 (≤3 m), %2 (3–5 m), %2,5 | 3,3 V TTL 115200 | çekirdek 4,9–5,5 V 300 / 600 mA + motor VMOTO 5–10 V ~100 mA, MOTOCTL | 96,8 × 70,3 × 55 mm, 170 g | çizimde 6 mm bant, tam değer okunmuyor |
| RPLIDAR A2M12 | üçgenleme | 0,2–12 m / 10 m | 360°, 0,225° @10 Hz | 5–15 Hz (10) / 16 kHz | tabloda yok | 3,3 V TTL 256000 | 4,9–5,2 V; 450 (600) mA, kalkış 1500, ani 2500 mA; MOTOCTL PWM | Ø76 × 41 mm, 190 g | 6 mm bant, tam değer yok |
| LDROBOT LD19 (D300) | DTOF | 0,02–12 m (%70) / yok | 360°, 0,8° @10 Hz | 5–13 Hz (10) / 4,5 kHz | ortalama ±45 mm, std 10 mm (0,3–12 m); Waveshare wiki "10 mm" diyor (çelişki) | UART 230400 tek yön, 3,3 V | 4,5–5,5 V; 180 / 300 mA | 38,6 × 38,6 × 34,8 mm, 47 g; 30 klx | ~27,0 mm (hesap, çizimden) |
| LDROBOT LD06 | DTOF | 0,02–12 m (%70) / yok | 360°, 1° | 5–13 Hz (10) / 4,5 kHz | 30 mm tipik, 45 mm en çok; açı hatası ≤2° | UART 230400 | 4,5–5,5 V; 180 / 300 mA | 38,6 × 38,6 × 33,3 mm, 42 g | ~25,7 mm (hesap) |
| LDROBOT STL-19P (D500) | DTOF | 0,03–12 m (%80) / 0,03–8 m (%4) | 360°, 0,72° @10 Hz | 6–13 Hz (10) / 5 kHz | ±10 mm (<0,5 m), ±20 mm (0,5–2 m), ±30 mm (2–12 m) | UART 230400 tek yön | 4,5–5,5 V; 290 mA / kalkış "TBD" | 54 × 46,3 × 35 mm, 45 g; 60 klx | ~27,2 mm (hesap) |
| YDLIDAR X4 Pro | üçgenleme | 0,12–10 m (%80) / yok | 360°, 0,43–0,86° (6–12 Hz) | 6–12 Hz / 5 kHz | 2 cm (≤1 m), %3,5 (1–6 m) | UART 128000 tek yön | 4,8–5,2 V; 330 (380) / 800 (1000) mA | 110,6 × 71,5 × 41,4 mm, 178 g; fırçalı motor | yok (yalnız pencere 10,5 mm) |
| YDLIDAR X2 / X2L | üçgenleme | 0,10–>8 m / yok | 360°, 0,84° @7 Hz | 4–8 Hz (7) / 3 kHz | 2 cm (≤0,5 m), %1,5 (0,5–6 m), %2 (6–8 m) | UART 115200 tek yön | 4,8–5,2 V; 350 / 400 mA | 96 × Ø60,5 × 50,3 mm, 200 g; 550 lx tipik | ~42,4 mm (hesap) |
| YDLIDAR T-mini Pro | ToF | 0,02–12 m (%80) / 0,02–4 m (%10) | 360°, 0,54° en küçük | 6–12 Hz (6) / 4 kHz | 20 mm sistematik hata | UART 230400 çift yön | 4,8–5,2 V; 340 (480) / 840 (1000) mA | 38,6 × 38,6 × 33,4 mm, kütle yok | 25,7 mm (çizimden) |

Ortak [BULGU]: hiçbir veri sayfası geçersiz ya da kayıp ölçüm oranı vermiyor. C1 belgesinin bu konudaki iki notu var:
- 0,05–12 m dışındaki noktalar da çıkar, ama belge onları "yalnız referans" sayıyor.
- Doğruluk %10–90 yansıtıcılıkta sınanmış; bu aralığın dışında "biraz düşebilir".

### Yazılım (ROS'suz Python ve ileride ROS 2) [BULGU]

| Model | ROS'suz Python | Bakım | Python 3.14 / Pi 5 | ROS 2 sürücüsü |
|---|---|---|---|---|
| RPLIDAR C1 | `rplidarc1` (üçüncü taraf, asyncio + pyserial, Python ≥3.10, C1 için yazılmış, 460800) | 0.1.3, 18.04.2025 | bilinmiyor | `Slamtec/sllidar_ros2` (C1 başlatma dosyası var) |
| | `pyrplidar` | 0.1.2, 2019 | C1'de 460800'de IndexError raporu (issue #12, Pi 4), çözüm yok | |
| | Slamtec `rplidar_sdk` (C++, v2.1.0 "C1 support") | son commit 09.04.2024 | Python bağı yok; Linux'ta `make` ile derlenir | |
| | Kendi ayrıştırıcı (pyserial, standart tarama). C1 belgesi A serisinin "standart" örnekleme protokolüyle uyumlu olduğunu, ama eski sürücünün güncellenmesi gerektiğini yazıyor | — | denenmedi | |
| RPLIDAR A1M8 | `rplidar-roboticia` 0.9.5 (A1 / A2) | sürüm 2017, son push 2023 | bilinmiyor | `sllidar_ros2` |
| RPLIDAR A2M12 | aynı + `pyrplidarsdk` (aarch64 tekerleği 3.10–3.13, 3.14 yok) | 2025 | 3.14 için tekerlek yok | `sllidar_ros2` |
| LD19 / LD06 / STL-19P | resmî Python yok. LD19 protokolü pyserial'la kolay çözülür: 230400, başlık 0x54, 0x2C, paket başına 12 nokta, CRC8, 47 bayt, komutsuz kendiliğinden yayın. LD06 / STL-19P geliştirici kılavuzu okunmadı | — | — | `ldlidar_stl_ros2`, `ldlidar_ros2` (STL-19P listede yok) |
| YDLIDAR X4 Pro / X2 / T-mini Pro | `YDLidar-SDK` (C++ + SWIG Python bağı) | V1.2.7, 09.10.2024; son push 26.10.2026 | bilinmiyor | `ydlidar_ros2_driver` |

## 3. Fiyat ve stok, Türkiye, 24.11.2026 [BULGU]

Onaylı satıcılar Robotistan, Motorobit, Robocombo ve Direnc.net (`raporlar/kaynaklar/06-onayli-satici-A.md:5`,
`07-gogus-ekrani-ve-5v.md:5`). Fiyatlar ürün sayfasından alındı ve KDV dahil. Stok sayfa durumudur; kesin teyit sipariş anında
yapılır. Hepsinin erişim tarihi 24.11.2026.

Okuma notları:
- **Robotistan:** fiyat sayfa yüklemeleri arasında birkaç kuruş oynuyor, çünkü kura bağlı. C1 bir okumada 3.992,85, sayfa
  verisinde 3.994,90 TL çıktı. Sayfa şablonunda gizli (`d-none`) bir "Tükendi" yazısı var; stok için sayfa verisine bakıldı
  (`InStock`, adet 24).
- **Robocombo:** fiyat sayfa yapı verisinden alındı; site fiyatlarının KDV dahil olduğunu yazıyor.

| Model | Satıcı | Onaylı | Fiyat TL | Stok | Adaptör | URL |
|---|---|---|---|---|---|---|
| **RPLIDAR C1** | **Robotistan** | evet | liste 4.670,00 → **3.992,85** (havale 3.912,99) | **var (24)** | sayfada yazmıyor | https://www.robotistan.com/slamtec-c1-lazer-tarayici |
| RPLIDAR C1 | Direnc.net | evet | 6.334,20 | tükendi | yazmıyor | https://www.direnc.net/rplidar-c1-dtof-lidar-360-lazer-mesafe-tarayici-12m-ip54 |
| RPLIDAR C1 | Robocombo | evet | 6.712,50 | yok (stok 0) | yazmıyor | https://www.robocombo.com/rplidar-c1-dtof-360-derece-lazer-tarayici-lidar-4388 |
| RPLIDAR C1 | Motorobit | evet | bulunamadı | — | — | — |
| RPLIDAR C1 | Robotsepeti | **hayır** | 5.343,95 (KDV yazmıyor) | "stoktan gönderim" | USB adaptör kartı + Type-C kablo yazıyor | https://www.robotsepeti.com/slamtec-rplidar-c1-c1m1-r2-360-lazer-tarayici-12m-5k |
| **RPLIDAR A1M8** | **Direnc.net** | evet | **8.482,32** | **var** | yazmıyor | https://www.direnc.net/rplidar-a1m8-360-derece-lazer-tarayici-gelistirme-kiti |
| RPLIDAR A1M8-R6 | Robocombo | evet | liste 9.763,50 → 8.543,00 | var (5, "tükeniyor") | yazmıyor | https://www.robocombo.com/rplidar-a1m8-r6-360-derece-lazer-tarayici-lidar-2996 |
| RPLIDAR A1M8-R6 | Robotistan | evet | 5.534,77 | tükendi | "1 x USB Adaptörü" | https://www.robotistan.com/rplidar-360-derece-lazer-tarayici-gelistirme-kiti |
| RPLIDAR A1M8-R6 | Robotsepeti | **hayır** | 7.524,28 | var | yazmıyor | https://www.robotsepeti.com/slamtec-rplidar-a1-360-omnidirectional-lidar-22342 |
| RPLIDAR A2M12 | Robotistan | evet | liste 16.133,91 → 13.794,49 | var | yazmıyor | https://www.robotistan.com/a2m12-rplidar-360-lazer-tarayici |
| RPLIDAR A2M12 | Robocombo | evet | 16.170,50 | var (3); açıklamada "A2M8" geçiyor | yazmıyor | https://www.robocombo.com/rplidar-a2m12-360-derece-12mt-lazer-tarayici-lidar-2997 |
| RPLIDAR A2M8 | Direnc.net | evet | 16.830,00 | var | yazmıyor | https://www.direnc.net/rplidar-a2m8-360-derece-lazer-tarayici-gelistirme-kiti-dfrobot |
| RPLIDAR A2M12 | Robotsepeti | **hayır** | 14.477,24 | var | yazmıyor | https://www.robotsepeti.com/slamtec-rplidar-a2m12-360-lidar-lazer-tarayici-sensor-015-12m |
| YDLIDAR X4 Pro | Robotistan | evet | 6.779,73 | tükendi | yazmıyor | https://www.robotistan.com/ydlidar-x4-lidar-mesafe-sensoru |
| YDLIDAR X2 | Robotistan | evet | 7.396,07 | tükendi | yazmıyor | https://www.robotistan.com/ydlidar-x2-lidar-mesafe-sensoru |
| YDLIDAR T-mini Pro | dört onaylı site + Robotsepeti | — | bulunamadı | — | — | — |
| LD19 / D300, LD06, STL-19P / D500 | dört onaylı site + Robotsepeti | — | bulunamadı | — | — | — |

Ek notlar:
- Bakılamayan siteler: Hepsiburada ve Trendyol otomatik erişimi engelledi (403). Robolinkmarket listesi yüklenmedi. Ozdisan
  açılmadı.
- **Samm (onaylı değil):** bir arama sonucu "D300 Developer Kit" sayfasını gösterdi, ama sayfa ürünü yüklemedi. Fiyat ve
  stok doğrulanmadı.
- **Mouser Türkiye:** yalnız arama özetinde DFRobot LD19 kiti göründü (€102,34, 4 adet); sayfa açılmadı.
- **Robocombo:** arama betikle yükleniyor, bu yüzden LDROBOT ve YDLIDAR için "bulunamadı" sonucu orada daha zayıf bir
  kontrol.
- **Akakçe (fiyat karşılaştırma):** C1 için en düşük 6.494,00 TL, A1M8-R6 için 9.555,40 TL gösterdi. Yalnız liste
  sayfasından okundu.

## 4. Montaj önerisi ve kör sektör (CAD'e İŞLENMEDİ)

Bu bölüm bir öneri. CAD dosyalarına dokunulmadı. Ölçüler ortak ölçü dosyasından (`tasarim/freecad/arayuz.py`; taban ve
kabuk modülleri buradan okur) ve `tasarim/freecad/montaj/montaj-analiz.json`'dan alındı.

### 4.1 Çerçeveler [BULGU]

- CAD: orijin zemin ve robot merkezi; +Y yukarı, +Z ileri; mm (`arayuz.py:7`). +X önden bakanın sağı, yani robotun kendi
  solu (K65; `kod/ortak/robot_parametreleri.json` `not_`).
- Robot çerçevesi (bu not ve JSON): x ileri = CAD +Z, y robotun solu = CAD +X, z yukarı = CAD +Y. Açı 0 ileride, saat
  yönünün tersine (sola) artar.

### 4.2 Taban geometrisi [BULGU]

| Öğe | Değer | Kaynak |
|---|---|---|
| Etek (taban kabuğu) alt kenarı | yerden 35 mm; y 35–140 arası dik, yarı ölçü x 260 × z 262,5, köşe r 15 | `arayuz.py:442-446` `ETEK_KESIT` |
| Etek üst plakası (gövde kabuğunun altı) | y 262; yarı ölçü x 188 × z 245, köşe r 60 | `arayuz.py:44`, `:445` |
| Etek parça dikişleri | z = 87,5 (ön / orta / arka); x = ±38 (ortada 76 mm dolgu şeridi) | `arayuz.py:447-448` |
| Gövde kabuğu alt kesiti | y 263'te yarı ölçü x 112 × z 82 (ön ve arka), r 40; y 476,5'te 125 × 85, r 38; arası doğrusal | `arayuz.py:381-386`, `:413-416` |
| Sonarlar (3 × HC-SR04) | CAD x −79,4 / 0 / +79,4; y 110; PCB ön yüzü z 256; etek içinde, Ø17 deliklerden | `arayuz.py:452`, `:691` |
| Acil stop mantarı | CAD (117,4; 280,4; −200): arka, robotun solu | `montaj-analiz.json` "Acil stop mantari + bilezik" |
| Kollar, ev pozu | en alçak parça "El", merkez y 898,8 | `montaj-analiz.json` |
| Teker ve motorlar | etek içinde (en üst nokta y ≈ 127) | `arayuz.py:437-441` |

Etek, tekerleri ve tabanı y 35–262 arasında tamamen sarıyor. LiDAR'ı etek içine koymak 360° bir yarık ve eteğin yeniden
tasarımını ister; tekerler ve motorlar da yanları kapatır. Etek altında 35 mm boşluk var, bu da sensöre yetmez. Bu yüzden
öneri, LiDAR'ı **etek üst plakasının üstüne, gövdenin önüne** koymak.

### 4.3 Önerilen konum [DEĞERLENDİRME]

| Alan | Değer | Gerekçe |
|---|---|---|
| x_m (ileri) | **0,190** | Gövde ön yüzü 0,0825'te; LiDAR arka kenarı 0,162'de, aradaki boşluk 80 mm. Ön kenarı 0,218'de, plaka kenarına (0,245) 27 mm kalır, yani darbeye karşı plakanın içinde. |
| y_m (sol) | **0,0** | Simetri ekseni. |
| z_m (tarama düzlemi) | **0,295** | Plaka üstü 0,262 + takoz 0,003 [TAHMİN] + C1 lazer yüksekliği 0,0298. |
| yaw_derece | **0** | LiDAR'ın 0° yönü robotun ilerisine bakar. Kablo çıkışı arkada kalacak biçimde çevrilir (C1 çiziminde doğrulanacak). |

Montaj notları:
- **Dolgu şeridi:** konum x = 0'da, etek ön parçasının ortasındaki 76 mm genişliğindeki dolgu şeridinin üstüne düşer.
  C1'in 55,6 mm genişliği şeride sığar; vidalar tek parçaya gelmeli. Bu, CAD aşamasında çözülecek: 4 delik + kablo deliği.
- **Kablo geçişi:** kablo deliği plakada LiDAR'ın arkasına açılır (x_m ≈ 0,15–0,17). Altında elektronik katın ön bandı
  var: servo dağıtım kartları, CAD z 177–233, üst yüzleri y ≈ 210. Plaka alt yüzüne (y 259) kadar ~50 mm kalır [TAHMİN,
  konnektör payı ölçülmedi].
- **Yere paralellik:** C1'in kendi tarama düzlemi 0–1,5° eğik olabilir [BULGU]. 1,5° aşağı eğimde ışın yere ~11 m'de
  değer (0,295 / tan 1,5°); 2 m'deki duvarda ±52 mm sapma olur. Koridor işi için yeterli. Plaka yatay basılmalı.

### 4.4 Kör sektör hesabı [DEĞERLENDİRME]

Tarama düzlemi z = 0,295 m'de yalnız gövde kabuğu kesilir. Etek, teker ve sonarlar düzlemin altında kalır; kollar
(el ≥ 0,86 m) ve kafa üstündedir.

Gövdenin bu yükseklikteki kesiti doğrusal enterpolasyonla, t = (295 − 263) / (476,5 − 263) = 0,15 için:
- yarı genişlik a = 114,0 mm
- ön yarı derinlik bf = 82,5 mm
- köşe r = 39,7 mm

LiDAR (x = 190 mm) gövdenin ön köşe yaylarına teğet görür:
- köşe merkezi: (x, y) = (82,5 − 39,7; 114,0 − 39,7) = (42,8; 74,3) mm
- LiDAR'a uzaklık: d = √((190 − 42,8)² + 74,3²) = 164,9 mm
- merkez doğrultusunun arka eksenden açısı: atan(74,3 / 147,2) = 26,8°
- teğet payı: asin(39,7 / 164,9) = 13,9°
- kör sektörün yarı açısı: 26,8 + 13,9 = 40,8°

**Kör sektör (geometrik): [139,2°, 220,8°]** (180° çevresinde, 81,6° geniş). **Açık görüş 278,4°.** İleri yarım düzlemin
tamamı ve iki yanda ±139°'ye kadar açık, yani istenen "en az ön 180–270° açık" şartı sağlanıyor.

Sayısal kontrol: gövde kesiti 4 × 400 noktayla örneklendi; sonuç yukarıdaki elle hesapla 0,1°'den az farkla aynı.

| Düzlem z (m) | LiDAR x 0,160 | 0,175 | **0,190** | 0,205 |
|---|---|---|---|---|
| 0,290 | [131,2; 228,8] açık 262,3° | [135,6; 224,4] 271,3° | [139,4; 220,6] 278,8° | [142,7; 217,3] 285,3° |
| 0,300 | [130,9; 229,1] 261,8° | [135,4; 224,6] 270,8° | [139,2; 220,8] 278,4° | [142,5; 217,5] 284,9° |
| 0,310 | [130,7; 229,3] 261,4° | [135,2; 224,8] 270,4° | [139,0; 221,0] 278,0° | [142,3; 217,7] 284,5° |

- **Acil stop mantarı:** LiDAR'dan 163° doğrultusunda, 0,41 m uzakta. Mantarın üstü tarama düzlemine yakın [TAHMİN], ama
  kör sektörün içinde kalıyor; ek kör sektör oluşturmuyor.
- **Kendi gövdesinden yansıma:** gövde ön yüzü LiDAR'dan 0,107 m uzakta, C1'in en kısa menzili (0,05 m) bundan kısa. Yani
  gövde kör sektörde bir "duvar" olarak ölçülür. Yazılım bu sektörü maskelemeli. Montaj toleransı için her yana 5° pay
  önerilir: maske [134°, 226°].
- **Geri giderken:** kör sektör tam arkada. Arkada sonar da olmadığından (`kod/SIMULASYON.md`, bulgu a) geri sürüşte
  arka hâlâ kör.

### 4.5 Sonarlarla çakışma [DEĞERLENDİRME]

- **Mekanik:** sonarlar ve tutucuları etek içinde, y 96–125 ve z 230–257,6 arasında. LiDAR etek plakasının üstünde
  (y ≥ 262), konumda çakışma yok. LiDAR kablo deliği plakada x_m ≈ 0,16'da, sonar tutucularından (z ≥ 230) ~60 mm geride.
- **Sinyal:** LiDAR 905 nm kızılötesi lazer, HC-SR04 40 kHz ses; birbirini bozmazlar.
- **Kapsama:** LiDAR 0,295 m düzlemini görür; sonarlar 0,11 m'de ±15° koni tarar. Düzlemin altındaki alçak engelleri
  (eşik, çanta, ayak) yalnız sonarlar görür, yani ikisi birbirini tamamlar. LiDAR 0,295 m'den alçak engeli görmez.

## 5. Güç ve kablo değerlendirmesi

### 5.1 Güç [BULGU + DEĞERLENDİRME]

- **C1'in istekleri [BULGU]:** 4,8–5,2 V; kalkışta 800 mA; çalışırken 230 mA tipik, 260 mA en çok.
- **Çevre 5 V hattı [BULGU]:** tabanda, XL4016 üzerinden, F4 5 A, çıkışta 2 A mini sigorta. Bugünkü tepe yükü ≈ 0,6 A
  (`planlama/adim3/elektrik.md:338`, `:353`, `:368`).
- **Hesap [DEĞERLENDİRME]:** çalışırken 0,6 + 0,26 ≈ 0,86 A; kalkış anında 0,6 + 0,8 ≈ 1,4 A. İkisi de 2 A sigortanın
  altında, ama kalkışta pay yalnız %30. İki önlem:
  - LiDAR motorunu ESP32 ve sonarlar açıldıktan sonra yazılımla başlat (C1'de motor yalnız tarama komutuyla döner).
  - LiDAR girişine 100–470 µF kondansatör koy [TAHMİN, masada denenecek].
- **Gerilim:** çevre XL4016'nın ayar gerilimi belgede yazmıyor. C1 aralığı dar (4,8–5,2 V); LiDAR ucunda yük altında
  ölçülmeli.
- **Pi USB'sinden beslememe gerekçesi [DEĞERLENDİRME]:** C1'i Pi USB'sinden (hub üzerinden) beslemek önerilmez.
  - Hub'ın harici beslemesi yok. Pi USB toplamı bugün 600 mA sınırında; `usb_max_current_enable=1` ile 1,6 A
    (`elektrik.md:88`, `:281`).
  - 800 mA kalkış akımı ~2,5 m USB kablosunda (Pi → hub ~1 m, hub → taban ~1,5 m) 0,3 V'tan fazla düşüm yapar [TAHMİN].
    Bu da C1'in 4,8 V alt sınırının altına iner.

### 5.2 Veri kablosu [DEĞERLENDİRME]

Öneri: **USB, LiDAR'ın USB-UART adaptör kartı tabanda, kablo gövdedeki 4'lü hub'ın boş portuna.**
- **Hub:** gövdede, göğüs üst arka kapağın içinde. Port 3 ve 4 boş (`elektrik.md:80-84`).
- **Yol:** kablo ESP32'nin USB kablosuyla aynı yoldan gider. O yol 1.129 mm, önerilen boy 1.560 mm, 2 m kablo yetiyor
  (`elektrik.md:39`). LiDAR'dan ESP32 bölgesine ek ~0,2–0,3 m [TAHMİN] eklenince 2 m USB kablosu yine yeter.
- **Neden boyun değil:** kafaya, Pi'ye doğrudan gitmek boyun tünelinden (20 × 7,8 mm) geçmeyi ister; USB fişi orada zaten
  sorun (`kablolama-on-kararlar.md:423`).

Bağlantı [DEĞERLENDİRME, masada doğrulanacak]:

| Uç | Bağlantı |
|---|---|
| LiDAR VCC, GND | Çevre 5 V'tan, 2 A mini sigortadan sonra; ESP32 ve sonarlarla aynı dağıtım. |
| LiDAR TX, RX | Adaptör kartına, ortak GND ile. |
| Adaptör kartının 5 V'u | LiDAR'a gitmemeli. Ya adaptörün LiDAR'a giden 5 V'u ayrılır, ya da LiDAR'a kendi 5 telli demeti yapılır. Aksi hâlde Pi USB 5 V'u ile çevre 5 V'u birbirine bağlanır; ESP32'de aynı sorun 1N5819 ile çözülmüştü (`elektrik.md:144`). |

Neden UART doğrudan Pi'ye değil [DEĞERLENDİRME]:
- 460800 baud 3,3 V TTL'i ~1,6 m korumasız kabloyla, motor sürücülerinin yanından taşımak hata riski taşır.
- Bu yol boyundan da geçmek zorunda kalır.
- USB hem diferansiyel hem de ESP32 yoluyla aynı.

Veri hızı: 5 kHz × 5 bayt ≈ 25 kB/s [DEĞERLENDİRME]. Hub ve CP2102 için önemsiz.

Riskler:
1. **Hub tek hata noktası:** hub düşerse ESP32, göğüs dokunmatiği ve LiDAR birlikte düşer.
2. **Adaptör belirsizliği:** USB adaptörünün pakette olup olmadığı Robotistan sayfasında yazmıyor. Robotsepeti aynı ürünle
   "USB Adapter Board + Type-C kablo" veriyor. Siparişten önce sorulmalı. Yoksa onaylı bir CP2102 / CH340 3,3 V kartı
   eklenir.

## 6. Yazılım (ROS'suz, düz Python) [DEĞERLENDİRME]

1. **İlk masa denemesi:** Pi 5'te pyserial ile 460800 baud, Slamtec standart tarama komutu (A serisinin "standart"
   protokolü; C1 belgesi uyumlu diyor). Bayt başına açı ve mesafe çözülür ve 10 Hz tam tur görülür. Kütüphane bağımlılığı
   olmadan ~100 satır [TAHMİN].
2. **Olmazsa:** `rplidarc1` (2025; C1 için, asyncio + pyserial) denenir. Python 3.14'te sınanmadı, bilinmiyor.
3. **Son çare:** Slamtec C++ SDK v2.1 `ultra_simple` derlenir ve çıktısı Python'a borulanır.
4. **Açı yönü:** RPLIDAR açısını saat yönünde verir [TAHMİN, C1 protokol belgesinde doğrulanacak]. Robot çerçevesine
   çevirirken θ_robot = yaw − θ_lidar alınır.
5. **İleride ROS 2:** `Slamtec/sllidar_ros2` C1'i destekliyor.

Üç adımın hiçbiri tutmazsa yedek A1M8'e geçilir (eski Python kütüphaneleri onu hedefliyor).

## 7. Açık sorular

1. **Kapsam:** `proje-plani.md:28` LiDAR'ı kapsam dışı sayıyor (21 Ekim). LiDAR yeniden kapsama mı alındı? Alındıysa
   `maliyet.json`'a satır ve sipariş kararı ayrı iş.
2. **Paket içeriği:** C1'in Robotistan paketinde USB adaptör kartı ve kablo var mı? Satıcıya sorulacak.
3. **Montaj CAD'i:** etek ön parçasında LiDAR yuvası, 4 vida ve kablo deliği; dolgu şeridine mi, ön parçaya mı
   bağlanacak; çakışma taraması. CAD adımı, iki ajanlı kuralla.
4. **Gerilim:** çevre 5 V XL4016'nın ayar gerilimi ve LiDAR ucunda yük altındaki gerilim (C1 4,8–5,2 V).
5. **Kalkış akımı:** 2 A çevre sigortasında payı masada ölçülecek. Gerekirse LiDAR'a ayrı bir 1 A mini sigortalı kol.
6. **Pi 5 + Python 3.14 okuma denemesi:** standart kip ve `rplidarc1`. Ayrıca açı yönü ve 0° işareti doğrulanacak.
7. **Göz güvenliği:** C1 Class 1 [BULGU]. Okul ortamında ek önlem gerekmez [DEĞERLENDİRME]; yine de etiketi görünür olsun.
8. **Simülasyon:** gürültü modeli. Veri sayfası ±30 mm sınır veriyor, dağılım türü vermiyor; simülasyonda sigma olarak
   kullanmak kötümser bir seçim.

## 8. Kaynaklar (erişim 24.11.2026)

Veri sayfaları ve resmî sayfalar (bazı PDF'ler satıcı sunucusunda; belge üreticinin):
- RPLIDAR C1 veri sayfası v1.1: https://cdn.shopify.com/s/files/1/0058/3145/8904/files/SLAMTEC_rplidar_datasheet_C1_v1.1_en.pdf
  ve https://www.slamtec.com/en/C1/Spec
- RPLIDAR A1M8 rev 2.1: https://cdn-shop.adafruit.com/product-files/4010/4010_datasheet.pdf ve https://www.slamtec.com/en/Lidar/A1Spec
- RPLIDAR A2M12 rev 1.0: https://cdn.robotshop.com/media/r/rpk/rb-rpk-22/pdf/rplidar-a2m12-360-laser-range-scanner-datasheet.pdf
  ve https://www.slamtec.com/en/Lidar/A2Spec
- LD19 veri sayfası V2.5: https://ws.dfrobot.com.cn/Fi2C_5ICX6v1yCkN1mJls6WYbLvt ve geliştirme kılavuzu V2.3:
  https://elecrow.com/download/product/SLD06360F/LD19_Development%20Manual_V2.3.pdf, Waveshare wiki: https://www.waveshare.com/wiki/DTOF_LIDAR_LD19
- LD06 (Inno-maker kopyası, satıcı belgesi): https://enacrobotique.github.io/doc/datasheets/LDROBOT_LD06_Datasheet.pdf
- STL-19P EN v1.0: https://files.waveshare.com/wiki/D500-LiDAR-Kit/LDROBOT_STL-19P_Datasheet_EN_v1.0(1).pdf ve https://www.waveshare.com/wiki/D500_LiDAR_Kit
- YDLIDAR X4 Pro V1.1: https://akizukidenshi.com/goodsaffix/YDLIDAR%20X4PRO%20Datasheet%20V1.1(240124).pdf
- YDLIDAR X2 v1.2: https://files.waveshare.com/upload/b/be/YDLIDAR_X2_Datasheet.pdf ve https://github.com/YDLIDAR/YDLidar-SDK/blob/master/doc/Dataset.md
- YDLIDAR T-mini Pro V0.2.0: https://robu.in/wp-content/uploads/2022/11/YDLIDAR-T-mini-Pro-Data-Sheet_V0.2.0-220831.pdf

Yazılım:
- https://github.com/Slamtec/rplidar_sdk
- https://github.com/Slamtec/sllidar_ros2
- https://github.com/dsaadatmandi/rplidarc1
- https://github.com/Hyun-je/pyrplidar (issue #12)
- https://github.com/Roboticia/RPLidar
- https://github.com/SkoltechRobotics/rplidar
- https://github.com/dexmate-ai/pyrplidarsdk
- https://github.com/YDLIDAR/YDLidar-SDK
- https://github.com/YDLIDAR/ydlidar_ros2_driver
- https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2

Fiyat sayfaları: § 3 tablosundaki URL'ler.

Depo içi:
- `tasarim/freecad/arayuz.py:7, 44, 381-386, 413-416, 437-452, 691`
- `tasarim/freecad/montaj/montaj-analiz.json` (parça merkezleri)
- `kod/ortak/robot_parametreleri.json` (çerçeve, sonarlar)
- `planlama/adim3/elektrik.md:39, 80-88, 144, 281, 338, 353, 368`
- `planlama/adim3/kablolama-on-kararlar.md:423`
- `planlama/proje-plani.md:28`
- `raporlar/kaynaklar/01-donanim-maliyet.md:85`
- `raporlar/kaynaklar/06-onayli-satici-A.md:5`
