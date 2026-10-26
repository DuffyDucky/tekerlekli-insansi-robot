// pinler.h -- ESP32 DevKit (ESP32-WROOM-32) pin tablosu. TEK YER: pin değişirse yalnız burası değişir.
//
// DURUM: ÖNERİLEN pinler, KABLAJDA DOĞRULANACAK (26 Ekim 2026, donanımda denenmedi).
//
// Seçim mantığı (ESP32 tuzakları):
//  - GPIO 0, 2, 5, 12, 15 "strapping" pinleri: açılışta seviyeleri önemli. Motor/enkoder bağlanmadı.
//    (GPIO 2 yalnız karttaki LED için kullanılıyor, sorun değil.)
//  - GPIO 6-11 dahili flash'a gider, ASLA kullanma.
//  - GPIO 34-39 yalnız giriş ve dahili pull-up yok; burada kullanılmadı.
//  - GPIO 16/17: kart ESP32-WROVER ise (PSRAM'li) bunlar PSRAM'e gider! O durumda sağ enkoderi
//    34/35'e al ve iki pine 10k pull-up (3,3 V'a) ekle.
//  - Motor PWM pinleri (25, 26, 32, 33) açılışta sinyal üretmeyen pinlerden seçildi.
//
// GÜÇ VE TOPRAK (bkz. src/main.cpp başı): ESP32 3,3 V mantık. BTS7960 girişleri 3,3 V'u kabul eder.
// Enkoderi 3,3 V ile besle (5 V beslersen çıkışı 5 V olur, ESP32 pinine 5 V verme).
#pragma once

// --- PCA9685 servo sürücü (I2C) ---
#define PIN_I2C_SDA       21
#define PIN_I2C_SCL       22
#define PCA9685_ADRES     0x40   // kart üstündeki A0-A5 lehim köprüleri açıksa 0x40

// --- BTS7960 sol motor sürücüsü ---
#define PIN_SOL_RPWM      25     // ileri PWM
#define PIN_SOL_LPWM      26     // geri PWM
#define PIN_SOL_EN        27     // R_EN ve L_EN birlikte bu pine. 10k ile GND'ye çek (açılışta kapalı)

// --- BTS7960 sağ motor sürücüsü ---
#define PIN_SAG_RPWM      32
#define PIN_SAG_LPWM      33
#define PIN_SAG_EN        13     // R_EN + L_EN; 10k ile GND'ye çek

// --- Enkoderler (JGB37-520 Hall, A/B kanalı) ---
#define PIN_SOL_ENK_A     18     // kesme bu pinde
#define PIN_SOL_ENK_B     19     // yön için okunur
#define PIN_SAG_ENK_A     16     // WROVER ise bkz. yukarıdaki not
#define PIN_SAG_ENK_B     17

// --- Durum LED'i ---
#define PIN_DURUM_LED     2      // DevKit üstündeki mavi LED

// Not: Emas acil stop butonu ESP32'ye BAĞLI DEĞİL. Motor ve servo güç hattını doğrudan keser;
// yazılım çökse de çalışır. (İstenirse ileride bir yardımcı kontağı giriş olarak okunabilir.)
