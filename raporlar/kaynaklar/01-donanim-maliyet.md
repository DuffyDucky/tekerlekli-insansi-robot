---
title: "Kanıt: Donanım ve maliyet"
created: 2026-09-26
---

> Claude Opus alt ajan raporu, 26 Eylül 2026, olduğu gibi. Rakamlar ajanın beyanıdır; "(t)", "tahmini", "doğrulanmadı" işaretleri korunmuştur.

# Tekerlekli insansı robot: donanım ve maliyet araştırması (Eylül 2026)

**Fiyatlar hakkında:** TL fiyatları KDV dahildir ve 26.09.2026'da mağaza sayfalarından tek tek kontrol ettim. Kur varsayımı **1 USD ≈ 49 TL** (Investing, 26.09.2026 aralığı 48,77–49,01). "(t)" işareti tahmin demek: ya doğrulanmış bir TR fiyatı bulamadım ya da global fiyatı çevirdim. **Önemli:** Robotistan ve Robolink'teki çoğu kalem (Pi 5, JGB37, MG996R, BTS7960, DS3218, Jetson, Pi Cam 3) kontrol anında **"Tükendi"** görünüyordu. Alışverişten önce stok ve fiyata tekrar bakın.

## 1) MİNİMUM: yalnız ses, 2 DoF'lu basit kollar, ~10-15 kg

| Kalem | Model | Adet | Birim (TL) | Toplam (TL) | Kaynak |
|---|---|---|---|---|---|
| Tahrik motoru | JGB37-520 12V enkoderli (60-110 RPM) | 2 | 639,29 | 1.278,58 | Direnc.net |
| Motor sürücü | BTS7960B 43A | 2 | 227,31 | 454,62 | Direnc.net |
| Tekerlek | 125×58 mm arazi tekerleği | 2 | 353,63 | 707,26 | Robotistan |
| Kaplin 6 mm | metal göbek | 2 | 150 (t) | 300 | — |
| Sarhoş teker | 50 mm tablalı | 2 | 75 | 150 | Yollabize |
| Şasi | 4-6 mm kontrplak, lazer kesim (~5 TL/dk) | 1 | 1.000 (t) | 1.000 | Dönmez Reklam İzmir |
| Kol + kafa servo | MG996R (9,4-11 kg·cm, stall 2,5 A) | 6 | 230,99 | 1.385,94 | Robotistan |
| Servo sürücü | PCA9685 16 kanal | 1 | 345 | 345 | Robolink |
| Göz | 0,96" OLED | 2 | 150 (t) | 300 | — |
| Ana işlemci | Raspberry Pi 5 8GB | 1 | 11.966,22 | 11.966,22 | Robotistan |
| SD + soğutucu | — | 1 | 600 (t) | 600 | — |
| Alt kontrolcü | ESP32-WROOM-32D | 1 | 275,22 | 275,22 | Direnc.net |
| Mikrofon | USB konferans mikrofonu | 1 | 800 (t) | 800 | — |
| Amfi + hoparlör | PAM8403 + 2×3W | 1 | 120,15 (t) | 120,15 | Robotistan (amfi 20,15) |
| Mesafe sensörü | HC-SR04 | 3 | 60 (t) | 180 | — |
| Acil stop | Emas B200E60, 22 mm, kalıcı | 1 | 308,88 | 308,88 | Akakçe |
| Batarya | LiPo 4S 5200 mAh 40C | 1 | 3.147,60 | 3.147,60 | F1Depo |
| Denge şarj cihazı | iMax B6 sınıfı | 1 | 1.800 (t) | 1.800 | — |
| DC-DC | XL4016 (servo 6V + Pi 5V) | 2 | 250 (t) | 500 | — |
| Sigorta, XT60, anahtar, kablo | — | 1 set | 800 (t) | 800 | — |
| Filament | Microzey PETG 1 kg | 3 | 565,28 | 1.695,84 | Akakçe (25.09.2026) |
| Vida, somun, rulman | — | 1 set | 1.000 (t) | 1.000 | — |
| Yedek | 2 MG996R + 1 BTS7960 | — | — | 689,29 | — |
| **Ara toplam** | | | | **29.805** | |
| **+%25 beklenmeyen (kargo, tekrar baskılar)** | | | | **7.451** | |
| **TOPLAM** | | | | **≈ 37.250 TL ≈ 760 USD** | |

## 2) ORTA: ses + görüntü, kol başına 4 DoF, ~15-20 kg

| Kalem | Model | Adet | Birim (TL) | Toplam (TL) | Kaynak |
|---|---|---|---|---|---|
| Taban (motor + sürücü + tekerlek + kaplin + sarhoş teker) | Minimumdaki gibi | — | — | 2.890,46 | yukarıdaki |
| Şasi | 40×40 sigma, 2 m (834 TL/m) + köşe bağlantı + lazer kesim tabla | — | — | 3.268 (kısmen t) | Robolink |
| Omuz servosu | DS3218MG 20 kg·cm | 4 | 1.594,50 | 6.378 | Robolink |
| Dirsek/el servosu | MG996R | 4 | 230,99 | 923,96 | Robotistan |
| Kafa pan-tilt | MG996R | 2 | 230,99 | 461,98 | Robotistan |
| Servo sürücü | PCA9685 | 1 | 345 | 345 | Robolink |
| Yüz ekranı | Waveshare 7" HDMI 1024×600 | 1 | ~59,68 USD → 2.924 | 2.924 | Robotistan (USD fiyatlı) |
| Ana işlemci | Raspberry Pi 5 8GB + aktif soğutucu + NVMe/SD | 1 | 11.966 + 1.200 (t) | 13.166,22 | Robotistan |
| Alt kontrolcü | ESP32 | 1 | 275,22 | 275,22 | Direnc.net |
| Kamera | Raspberry Pi Camera Module 3 | 1 | 1.791,36 | 1.791,36 | Robotistan |
| Mikrofon | USB konferans mikrofonu | 1 | 1.500 (t) | 1.500 | — |
| Ses | MAX98357 I2S amfi + hoparlör | 1 | 300 (t) | 300 | — |
| IMU | BNO055 (global 15-34 USD) | 1 | 980 (t) | 980 | Walmart/eBay |
| Ultrasonik + acil stop | — | — | — | 548,88 | — |
| Batarya | LiFePO4 12,8V 20Ah | 1 | 4.500 (t)* | 4.500 | *100Ah modeli 15.429 TL, Akakçe |
| LiFePO4 şarj cihazı | 14,6V | 1 | 800 (t) | 800 | — |
| DC-DC | 2× servo hattı + 1× Pi 5V/5A | 3 | 250 (t) | 750 | — |
| Sigorta ve kablo | — | 1 set | 1.200 (t) | 1.200 | — |
| Filament + hırdavat | PETG 5 kg + vida/rulman | — | — | 4.326,40 | Akakçe |
| Yedek | 1 DS3218 + 2 MG996R | — | — | 2.056,48 | — |
| **Ara toplam** | | | | **49.386** | |
| **TOPLAM (+%25)** | **Pi 5 ile** | | | **≈ 61.700 TL ≈ 1.260 USD** | |
| **TOPLAM (+%25)** | **Jetson Orin Nano Super ile** (31.282,50 TL, Robolink; Robot Sepeti'nde 40.703 TL) | | | **≈ 85.900 TL ≈ 1.750 USD** | |

## 3) İDDİALI: derinlik kamera, LiDAR, akıllı servolar, otonom gezinme, ~20-25 kg

| Kalem | Model | Adet | Birim (TL) | Toplam (TL) | Kaynak |
|---|---|---|---|---|---|
| Tahrik | 6,5" hoverboard göbek motoru | 2 | 2.450 (tükendi) | 4.900 | Trendyol |
| Sürücü | 2. el hoverboard kartı + FOC firmware (ODrive global ve pahalı) | 1 | 1.000 (t) | 1.000 | — |
| Sarhoş teker | 75-100 mm | 2 | 200 (t) | 400 | — |
| Şasi | Sigma 4 m + bağlantı + 3 mm Al sac lazer kesim | — | — | 7.036 (kısmen t) | Robolink |
| Akıllı servo | Feetech STS3215 (19,5 kg·cm, 20 USD) + ithalat | 10 | 1.470 (t) | 14.700 | Seeed Studio |
| Bus servo kartı | Seri servo sürücü | 1 | 700 (t) | 700 | — |
| Yüz ekranı | 7" HDMI | 1 | 2.924 | 2.924 | Robotistan |
| Ana işlemci | Jetson Orin Nano Super + NVMe | 1 | 31.282,50 + 1.500 (t) | 32.782,50 | Robolink |
| Alt kontrolcü | ESP32 | 1 | 275,22 | 275,22 | Direnc.net |
| Derinlik kamera | OAK-D Lite (269 USD) + kargo/vergi | 1 | 17.000 (t) | 17.000 | Luxonis |
| LiDAR | Slamtec RPLIDAR C1 | 1 | 4.510,85 | 4.510,85 | Robotistan |
| Mikrofon dizisi | ReSpeaker Mic Array v2.0 (USB) | 1 | 8.058,39 | 8.058,39 | Robot Sepeti |
| Ses, IMU, ToF, acil stop | — | — | — | 2.188,88 (t) | — |
| Batarya (24V) | 2× LiFePO4 12,8V 20Ah, seri | 2 | 4.500 (t) | 9.000 | — |
| Şarj cihazı, DC-DC, kontaktör, kablo | — | — | — | 4.200 (t) | — |
| Filament + hırdavat | PETG 8 kg + vida/rulman | — | — | 7.022,24 | Akakçe |
| Yedek | 2 STS3215 | — | — | 2.940 | — |
| **Ara toplam** | | | | **119.638** | |
| **TOPLAM (+%25)** | | | | **≈ 149.500 TL ≈ 3.050 USD** | |

Alternatifler: RealSense D435 38.260 TL (Robot Sepeti, stokta yok), Dynamixel XL430 2.905,64 TL/adet (Robot Sepeti, 10 adet ≈ 29.000 TL).

**Serbestlik derecesi (DoF) başına maliyet:** MG996R ≈ 230 TL, DS3218 ≈ 1.595 TL, STS3215 ≈ 1.470 TL (tahmini, ithal), XL430 ≈ 2.906 TL. Akıllı servolar konum, akım ve sıcaklık geri bildirimi verir. Bu sayede servo yanmadan önce fark edilir.

## Hangi beyin hangi senaryoya yeter?
- **Senaryo A (sadece ses):** Pi 5 fazlasıyla yeter. Uyandırma kelimesi cihazda çalışır, konuşmayı metne çevirme (STT), dil modeli ve metni sese çevirme (TTS) bulutta yapılır. Ekibin eski bir dizüstü bilgisayarı da iş görür ve maliyeti sıfırdır.
- **Senaryo B (ses + görüntü):** Pi 5 yüz algılamayı düşük çözünürlükte yapar ama YOLO ile kişi takibi yalnız CPU'da birkaç FPS'te kalır. Pi 5'e yapay zekâ hızlandırıcı eklemek bir seçenek, fiyatına bakmadım. Jetson Orin Nano Super (67 TOPS, 7-25 W) ise yüz, nesne ve takibi aynı anda gerçek zamanlı yapar. Intel N100 mini PC x86 kolaylığı sunar ama TR fiyatını doğrulayamadım. ESP32 ya da Arduino Mega yalnız motor PID'i, enkoder ve servo zamanlaması için kullanılmalı.

## Kritik teknik uyarılar

**1. Servo akımı ve güç dağıtımı.** MG996R durma (stall) anında 2,5 A çeker (6V). Minimumdaki 6 servo en kötü durumda 15 A, Orta'daki 10 servo 25 A üstü çeker. Bu yüzden:
- Servoları asla Pi'nin ya da Arduino'nun 5V hattından beslemeyin.
- Her kol için ayrı bir buck konvertör kullanın (gerçekçi 8-10 A; XL4016'nın "20A" etiketi soğutmasız iddiadır).
- Pi için ayrı, temiz bir 5V/5A hat çekin.
- Tüm topraklar tek noktada birleşsin (yıldız toprak). Servo hattına 1000-2200 µF kondansatör koyun.
- Batarya çıkışına ana sigorta, her kola ayrı sigorta koyun. Acil stop motor ve servo gücünü fiziksel olarak kessin; yazılımla kesmek yetmez.

**2. Motor torku, yaklaşık formül.** Gereken çekiş kuvveti F = m·(a + g·sinθ + C_rr·g·cosθ), tork T = F·r / (motor sayısı).

Örnek: m = 25 kg, a = 0,5 m/s², 5° rampa, C_rr = 0,03, r = 0,0625 m. Sonuç F ≈ 41 N, motor başına T ≈ 1,3 N·m ≈ 13 kg·cm. Güvenlik payı ×1,5-2 ile **20-26 kg·cm sürekli** tork gerekir.

JGB37'nin katalogdaki 21 kg·cm değeri durma torkudur. Sürekli çalışmada bunun kabaca %25-30'unu hedefleyin. Sonuç: JGB37 düz zeminde 10-15 kg'a kadar yeterli. 20-25 kg'ı ve rampayı 4 motor ya da hoverboard motoru taşır.

Hız v = RPM·π·D/60. 60 RPM ve 125 mm tekerlekle ≈ 0,39 m/s, iç mekân için uygun.

**Kol torku:** 30 cm'lik, 400 g kol ve eldeki yük omuzda ≈ 8-9 kg·cm yapar. MG996R bunu sınırda taşır, DS3218 2 kat pay bırakır. Omuza güçlü servo koyun, bileğe ucuzunu.

**3. Neden L298N değil.** L298N bipolar (Darlington) sürücüdür: 2 A/kanal, ~2 V+ gerilim düşümü (12V'ta %15-25 güç kaybı) ve fazla ısınma. BTS7960 (43 A) ya da Cytron MDD10A (10 A sürekli, 30 A tepe, tek kartta 2 kanal, global ~36 USD; TR'de stok bulamadım) kullanın.

**4. Ağırlık merkezi ve devrilme.** Frenlerken devrilme sınırı a_devrilme ≈ g·(d/h). Burada h ağırlık merkezinin yüksekliği, d ağırlık merkezinden teker temas kenarına olan yatay mesafe.

Örnek: h = 0,6 m, d = 0,15 m ise sınır ≈ 2,45 m/s². Ani acil stop bunu aşabilir, öne uzatılmış kollar da d'yi küçültür. Önlemler:
- Batarya en alta.
- Öne ve arkaya sarhoş teker, geniş taban (≥ 45 cm).
- Yazılımda hızlanma rampası.
- Gövdeyi ve kafayı hafif tutun (PLA/PETG, %15-20 dolgu).

**5. Çalışma süresi örneği (Orta, Senaryo B).** Ortalama tüketim yaklaşık 70 W: Pi 10 W, servolar tutarken 20-30 W, motorlar 20-30 W, çevre birimleri 5 W. LiFePO4 12,8V 20Ah = 256 Wh, kullanılabilir %80 ≈ 205 Wh, yani **≈ 2,9 saat**. LiPo 4S 5200 mAh (77 Wh) ile aynı yükte ≈ 50 dakika. LiPo ucuzdur ama delinme ve yangın riski taşır, yangına dayanıklı çanta şart. Okul ortamı için LiFePO4 daha güvenli.

## Nerede tasarruf, nerede harcama

**Tasarruf edilebilecek yerler:**
- Senaryo A için ekibin eski dizüstü bilgisayarı (≈ 12.000 TL kazanç).
- Kontrplak ya da sigma şasi.
- Kafa ve gövde kabukları 3D baskı. Yazıcınız varsa filament kilosu ≈ 565 TL; hizmette 5-20 TL/gram (t).
- Klon ESP32.
- Kafa pan-tilt ve bilekte MG996R.
- Göz için OLED, tablet yerine 7" ekran.

**Para harcanacak yerler:**
- Batarya, BMS, sigorta ve acil stop (güvenlik).
- Servo güç hattı (kaliteli buck, kalın kablo, XT60).
- Omuz servoları.
- Enkoderli motor ve düzgün sürücü.
- Senaryo B'de Jetson ya da derinlik kamera. Görüntü işleme darboğazı en çok burada hissedilir.
- Mikrofon kalitesi. Robot içindeki motor gürültüsünde ucuz mikrofon ses tanımayı bozar.

**Gizli maliyetler:**
- Servolar yanar: %20-30 yedek alın.
- 1.500 TL altı siparişlerde kargo ücretli.
- İthal parçalarda (STS3215, OAK-D) gümrük ve kargo global fiyata %30-60 ekleyebilir (t).
- En az 2 prototip turu olur. %25 pay bunun için.

## Kaynaklar (erişim 26.09.2026)
- https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor
- https://www.robotistan.com/jgb37-520-12v-1000rpm-encoderli-dc-motor
- https://www.direnc.net/bts7960b-40-amper-motor-surucu-modulu
- https://www.robotistan.com/bts7960b-40-amper-motor-driver-board
- https://www.walmart.com/ip/Cytron-MDD10A-Dual-Channel-10A-DC-Motor-Driver-Brushed-Motor-Control-Solid-State-PWM-Support-5-30V-Robotics-DIY-Projects/17366524748
- https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi
- https://www.yollabize.com/urun/sarhos-pvc-tablali-teker-50mm
- https://www.robolinkmarket.com/40x40-agir-sigma-profil-kanal-10-1-metre
- https://www.donmezreklam.com.tr/lazer-kesim-izmir
- https://www.robotistan.com/mg996-13-kg-servo-motor
- https://www.robolinkmarket.com/ds3218mg-20kg-dijital-servo-motor
- https://www.seeedstudio.com/STS3215-19kg-cm-7-4V-Serial-Servo-p-6338.html
- https://www.robotsepeti.com/dynamixel-xl430-w250-t
- https://www.robolinkmarket.com/pca9685-16-kanal-12-bit-pwm-surucu
- https://www.robotistan.com/7-inch-hdmi-rezistif-dokunmatik-lcd-1024x600
- https://www.robotistan.com/raspberry-pi-5-8-gb
- https://www.robolinkmarket.com/nvidia-jetson-orin-nano-developer-kit-8gb
- https://www.robotsepeti.com/nvidia-jetson-orin-nano-super-developer-kit
- https://www.direnc.net/esp32-wroom-32d-wifi-bluetooth-gelistirme-modulu-en
- https://www.robotistan.com/raspberrypi-camera-module
- https://shop.luxonis.com/products/oak-d-lite-1
- https://www.robotsepeti.com/intel-realsense-d435-stereo-derinlik-depth-kamerasi
- https://www.robotistan.com/slamtec-rplidar-c1-lidar-laser-scanner-en
- https://www.robotsepeti.com/respeaker-microphone-array-v2
- https://www.robotistan.com/3w-2ch-mini-sound-amp-board-pam8403
- https://www.akakce.com/kumanda-butonu/en-ucuz-22mm-mantar-stop-butonu-fiyati,817168446.html
- https://www.f1depo.com/urun/14-8v-5200mah-40c-lipo-batarya-4s-pil
- https://www.cimri.com/aku/en-ucuz-megacell-12-8-v-100-ah-lityum-lifepo-4-aku-fiyatlari,1036190388
- https://www.akakce.com/filament/en-ucuz-microzey-petg-siyah-1-75mm-1-kg-fiyati,1676232605.html
- https://armut.com/fiyatlari/3d-baski_12669
- https://www.trendyol.com/hoverway/hoverboard-elektrikli-scooter-motoru-6-5-inch-p-70200829
- https://tr.investing.com/currencies/usd-try

**Açık kalanlar:**
- TR'de doğrulanmış fiyat bulamadıklarım: Cytron MDD10A, STS3215, OAK-D Lite, BNO055, N100 mini PC (Hepsiburada ve Akakçe erişimi 403 verdi), 12,8V 20Ah LiFePO4.
- ReSpeaker 4-Mic Pi HAT Robotistan'da satışa kapalı ve sayfası yalnız Pi 4 uyumluluğundan bahsediyor. Pi 5 için USB mikrofon dizisini öneriyorum.
