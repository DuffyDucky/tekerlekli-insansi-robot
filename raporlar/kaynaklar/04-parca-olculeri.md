---
title: "Kanıt: Gerçek parça ölçüleri (CAD için)"
created: 2026-09-26
---

> Claude Opus alt ajan raporu, 26 Eylül 2026. Parça tabloları kısaltıldı; değerler, kaynaklar ve güven işaretleri rapordaki gibi. Bu değerler `tasarim/cad/robot_cad.py` başındaki ölçü tablosuna işlendi.
> Özet: 19 parçadan 12'si üretici çiziminden doğrulandı (Pi 5, Active Cooler, Camera Module 3, Waveshare 7", ESP32-DevKitC, DS3218, MG996R, PCA9685, Emas B200E60, sigma kesiti, köşe bağlantı, Adafruit kartları); diğerleri satıcı verisi. "Tahmini" değerler parça gelince kumpasla ölçülmeli.

| Parça | Ana ölçüler (mm) | Güven | Kaynak |
|---|---|---|---|
| JGB37-520 enkoderli | Redüktör Ø37; boy oranla değişir: 1:56–90 → 24, ≥1:131 → 26,5 · motor Ø33 × 22 · enkoder ~Ø33–35 × 17–20 (tahmini) · mil Ø6 D (düzlük 5,5) × 15, **7 mm kaçık** · ön yüz 6× M3, Ø31 daire | satıcı / tahmini-orta | https://probots.co.in/jgb37-520-dc12v-320-rpm-miniature-speed-reduction-gear-dc-motor.html · https://probots.co.in/jgb37-520-dc12v-7-rpm-miniature-speed-reduction-gear-dc-motor.html · https://www.hotmcu.com/encoder-geared-motor-aslongjgb37520%EF%BC%88107rpm-p-126.html |
| 37 mm L braket | 46 × 42 × 40, sac 1,5, delik Ø3,5. Satıcıların çoğu ortalı milli GA37 braketi satıyor; JGB37'nin kaçık mili ve Ø31 delik düzeni kontrol edilmeli | orta | Amazon listeleri (arama özeti) |
| 125×58 tekerlek | Ø125 × 58, 12 mm altıgen göbek, 140 g | doğrulandı | https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm · https://www.indianhobbycenter.com/products/125mm-atv-robotics-wheel-with-coupler-all-terrain-robot-monster-off-road-wheel-blue |
| Kaplin | 12 altıgen × 30, Ø6 delik, pirinç, 35 g (Robotistan kaplinsiz gönderiyor) | boy/delik doğrulandı | https://www.indianhobbycenter.com/products/30mm-long-hex-coupling-for-robot-smart-car-atv-wheel-6mm-shaft |
| DS3218MG | 40 × 20 × 40,4; kulaklarla 54,5; delik 49,5 × 10; kulak alt yüzü tabandan 27,7; mil kenardan ~10 (tahmini); 25T | doğrulandı | https://itgresa.com/wp-content/uploads/2025/10/DS-Servo-20kg-DS3218-PRO-datasheet-PDF.pdf |
| MG996R | 40,7 × 19,7 × 42,9 (kasa üstü 36,6, horn dahil 47,6); kulaklarla 53,6; kulak alt yüzü 26,6; 25T | doğrulandı | https://www.electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf |
| Raspberry Pi 5 | 85 × 56; delik Ø2,7, 58 × 49, kenardan 3,5; bileşenler ~16 (tahmini) · Active Cooler 63,5 × 42,5 × 13,7 | doğrulandı | https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008347-DS-1-raspberry-pi-5-mechanical-drawing.pdf · https://www.olimex.com/Products/RaspberryPi/RPi5-ACOOL/resources/raspberry-pi-active-cooler-mechanical-drawing.pdf |
| Camera Module 3 | 25 × 23,86 × 1,12; delik Ø2,2, 21 × 12,5; lens Ø5,75, blok 10,8, lens merkezi alt kenardan 14,4; toplam 11,3 | doğrulandı | https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008153-DS-1-camera-module-3-standard-mechanical-drawing.pdf |
| Waveshare 7" HDMI LCD | Kulaklarla 164,9 × 124,25; PCB 148,9 × 107,02; delik 156,9 × 114,96; aktif alan 154,21 × 85,92; panel 3,5, modül ~15 | doğrulandı (kalınlık tahmini) | https://www.waveshare.com/img/devkit/LCD/7AP/Exterior-Size.jpg · https://www.waveshare.com/wiki/7inch_HDMI_LCD_(C) |
| ESP32 DevKit | DevKitC V4 54,3 × 27,94 · DOIT 30 pin ~52 × 28 | doğrulandı / orta | https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf |
| BTS7960 | 50 × 50 × 43, 4× M3 (aralık tahmini) | satıcı | https://envistiamall.com/blogs/learn/bts7960-double-43a-high-power-motor-driver-module-user-guide |
| PCA9685 | 62,2 × 25,4 × 3; delik Ø2,5, 55,9 × 19,05 | doğrulandı | https://www.adafruit.com/product/815 |
| LiFePO4 12,8V 20Ah | Landport LFP12-20 181 × 77 × 167, 2,8 kg · BATE 181 × 77 × 170, 2,9 kg · WattCycle 185 × 84 × 170, 2,05 kg | doğrulandı | https://www.oro2u.com/battery-lithium-12v-lfp12-20-20ah-12v-lithium-lifepo4-2-8kg-l-181-x-w-77-x-h-167 · https://batteryservice.cz/wp-content/uploads/2024/02/DataSheet-12.8V-20Ah-Lifepo4-Battery.pdf · https://www.wattcycle.com/products/wattcycle-12v-20ah-lifepo4-battery |
| 40×40 ağır sigma | Kanal 10,2; merkez Ø9; köşe delik Ø5,1 @ 30,2; 1,99 kg/m; kesit 7,32 cm² · köşe bağlantı 37 × 37 × 37,7, 75 g | doğrulandı | https://witcdn.robolinkmarket.com/40x40-agir-sigma-profil-kanal-10-1-metre-robolink-market-10848-77-B.jpg · https://sigmaprofil.com.tr/urun-detay/40x40-agir-sigma-profil-303 · https://witcdn.robolinkmarket.com/40x40-genis-kose-baglanti-robolink-market-2067-66-B.jpg |
| Emas B200E60 | Mantar Ø60; panel önü 28; arkası 48; delik Ø22,4; arka gövde 42 × 30 | doğrulandı | https://www.emaselectric.com/Export/File?fileUrl=%2FImages%2Fmedia%2FProduct%2FB200E60.jpg |
| HC-SR04 | 45 × 20 × 15; transdüser Ø16 | doğrulandı / tahmini | https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf |
| XL4016 | Tek soğutuculu 65 × 47 × 23,5; delik 58 × 26 | orta | https://www.mikrocontroller.net/attachment/534859/XL4016_Step_Down_Buck_DC_DC_Converter.pdf |
| BNO055 (Adafruit) | 27 × 20 × 4; delik 20 × 12 | doğrulandı | https://www.adafruit.com/product/2472 |
| MAX98357A / hoparlör | 19,4 × 17,8 × 3 / Ø40 × 20, 27 g | doğrulandı | https://www.adafruit.com/product/3006 · https://www.adafruit.com/product/3968 |
| 50 mm sarhoş teker (Emes) | Toplam yükseklik 74; tabla 50 × 50; delik 38 × 38 | doğrulandı | https://www.tekerteker.com/emes-tablali-pvc-doner-tekerlek-50-mm-cap |

**Oran uyarısı (ajan):** 60 dev/dk hangi orana denk gelir, motorun boştaki devrine bağlı. ~6000 rpm motorda 1:90–100 (redüktör 24 mm), ~10000 rpm motorda 1:168 (26,5 mm). Modelde 24 mm kullanıldı.

## V2 ekranları (2 Ekim 2026, hoca geri bildirimi)

Kaynak: Claude Opus alt ajanı Waveshare çizimlerinden okudu; orkestratör fiyat ve stoğu sayfa verisinden yeniden kontrol etti.

| Parça | Ölçü (mm) | Durum | Kaynak |
|---|---|---|---|
| Waveshare 10.1inch HDMI LCD (B), kasalı | Kasa ön plakası 274,12 × 187,00 (R6); ön cam 253,96 × 168,60; cam penceresi 217,96 × 136,60; panel aktif alanı 216,96 × 135,60; çıplak panel 229,46 × 149,20 × 4,8; camdan arka plakaya 18,0; köşe delikleri Ø3,0, 265,11 × 179,0. CAD'de kasa ön plakası kullanılmadı, çerçeveyi gövde yapıyor (cam + 0,5 boşluk + 2,5 duvar). Kütle doğrulanmadı (CAD'de 0,60 kg tahmini) | doğrulandı (kütle tahmini) | https://files.waveshare.com/wiki/10.1inch_HDMI_LCD_B_with_case/10.1inch_HDMI_LCD_B_with_case_2D_PDF_20260116.pdf · https://files.waveshare.com/upload/9/9b/10.1inch_HDMI_LCD_B_panel_dimension.pdf |
| Waveshare 1.28inch LCD Module (GC9A01) | PCB Ø37,5, dil dahil 40,4; aktif Ø32,4; konnektörle 11,05, konnektörsüz ≈ 5,45; 4 pirinç burç Ø3,5 / Ø1,7, 18,6 × 26,7; PH2.0 8 pin. Kütle doğrulanmadı (CAD'de 8 g tahmini) | doğrulandı (kütle tahmini) | https://www.waveshare.com/wiki/1.28inch_LCD_Module · https://files.waveshare.com/upload/4/49/1.28inch_LCD_Module_3D_Drawing.zip |

## Kabuk modülü (8 Ekim 2026): 3D yazıcı ve göğüs ekranı

Kaynak: Claude Opus, FreeCAD kabuk modülü oturumu. Yazıcı değerleri üreticinin teknik sayfasından okundu; Nextion ölçüleri `donanim/datasheet/` altındaki çizimden. Bu değerler `tasarim/freecad/arayuz.py` içindeki `YAZICI` ve `NEXTION` sözlüklerine işlendi.

| Parça | Ölçü (mm) | Durum | Kaynak |
|---|---|---|---|
| Bambu Lab X2D (ekibin yazıcısı) | Baskı hacmi ana nozül 256 × 256 × 260; yardımcı nozül ve çift nozül 235,5 × 256 × 256; iki nozül toplam 256 × 256 × 260 · iki nozül (ana + yardımcı) · aktif ısıtmalı hazne en çok 65 °C · nozül 300 °C, tabla 120 °C · PLA, PETG, ABS, ASA, TPU, PA, PC, PET, PVA ve "Support for PLA/PETG" destek malzemesi. Kabukta kullanılabilir hacim her eksende 10 mm pay ile 246 × 246 × 250 (pay tahmini). Eski 250³ / PRINT_MAX 230 varsayımı geçersiz | doğrulandı (pay tahmini) | https://bambulab.com/en/x2d/specs |
| Nextion NX1060P101_011 (10,1", Intelligent) | PCB 258,00 × 152,00 × 1,60; cam (LCD + dokunmatik) 236,80 × 144,80; toplam kalınlık 9,80 ± 0,2 (sayfada bileşenlerle 11,5); aktif alan 222,72 × 125,28; görünen alan 235 × 143; delikler 4× Ø3,20, 251,60 × 145,60 (kenardan 3,2); cam PCB uzun kenarından 10,40, kısa kenarından 3,80; 535 g. 4 pin XH2.54 konnektörün yeri (alt kenardan 7,81, soldan 68,44, 15,12 genişlik) ve arka bileşen yüksekliği (6,00) çizimden yorum | doğrulandı (konnektör yeri tahmini) | `donanim/datasheet/NX1060P101-011C-I_dimension.pdf` · https://nextion.tech/datasheets/nx1060p101-011c-i/ |
| M3 ISO 7380 bombe başlı imbus | Baş Ø5,7 × 1,65, anahtar 2 (bindirme cıvataları) | standart (nominal) | ISO 7380-1 |
