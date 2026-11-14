// OTOMATIK URETILDI: kod/ortak/pin_uret.py -- ELLE DUZENLEME.
// Kaynak: kod/ortak/pinler.json (pin haritasi TEK KAYNAK; planlama/adim3/pin-haritasi.md, dal lale-duzeltme)
// Degistirmek icin JSON'u duzenle, sonra: py -3 kod/ortak/pin_uret.py
// Pin haritasi surum 4, tarih 2026-11-14. Cekirdek: espressif32@6.9.0 (Arduino-ESP32 2.0.17); 3.x'e gecis raporu gozden gecirmeden yapilmaz
//
// BU FIRMWARE YALNIZ BU SURUMUN KABLAJINA YUKLENIR (rapor Y1). Eski (0.4.0) firmware yeni kablaja
// yuklenmez; yeni firmware eski kablaja yuklenmez.
//
// Hatirlatma (ayrinti raporda ve kod/esp32/OKU_BENI.md'de):
//  - GPIO 6-11 modul flasi, ASLA kullanilmaz. GPIO12 strapping (MTDI): bos, firmware hic ayarlamaz.
//  - Serial1 / Serial2 / SPI / HSPI varsayilan pinleriyle ACILMAZ (roleler ve motorlar o pinlerde).
//  - 34-39 yalniz giris, dahili pull yok. 4, 19, 13 setup()'in ilk satirlarinda LOW cikis (guc.cpp).
#pragma once

#define PIN_HARITASI_SURUM 4

// --- GPIO ---
#define PIN_AKU_ADC         36  // analog; ADC1_CH0; 100k/18k + 100nF
#define PIN_SONAR_SAG_ECHO  39  // giris; yalniz giris; 4.7k/10k bolucu; errata GPIO-3.11 ~80 ns LOW
#define PIN_SONAR_ORTA_ECHO 34  // giris; yalniz giris; 4.7k/10k bolucu
#define PIN_SONAR_SOL_ECHO  35  // giris; yalniz giris; 4.7k/10k bolucu
#define PIN_SOL_IS          32  // analog; sol BTS IS1+IS2; ADC1_CH4; 0 dB; IS -> 6.8k -> pin, pin -> 5.1k -> GND (kart IS direnci birlesik 500R ise; once olculur)
#define PIN_SAG_IS          33  // analog; sag BTS IS1+IS2; ADC1_CH5; 0 dB; IS -> 6.8k -> pin, pin -> 5.1k -> GND (kart IS direnci birlesik 500R ise; once olculur)
#define PIN_SOL_ILERI_PWM   25  // pwm; sol BTS IN1 (RPWM); 3.x: Serial2 TX varsayilani
#define PIN_SOL_GERI_PWM    26  // pwm; sol BTS IN2 (LPWM); 3.x: Serial1 RX varsayilani
#define PIN_SAG_ILERI_PWM   27  // pwm; sag BTS IN1 (RPWM); 3.x: Serial1 TX varsayilani
#define PIN_SAG_GERI_PWM    14  // pwm; sag BTS IN2 (LPWM); reset sonrasi zayif pull-up
#define PIN_BTS_EN          13  // cikis; sol EN1+EN2, sag EN1+EN2; 10k -> GND
#define PIN_ROLE_K1         4   // cikis; role surucusu #1, BC337-40 tabani; 270R seri, 2.2k taban -> GND, bobine ters 1N4007; BC337-40; surus gucu varsayilan (2) ya da ustu; 3.x: Serial2 RX varsayilani
#define PIN_ROLE_K2_ONSARJ  19  // cikis; role surucusu #2, BC337-40 tabani; 270R seri, 2.2k taban -> GND, bobine ters 1N4007; BC337-40; surus gucu varsayilan (2) ya da ustu
#define PIN_ACIL_STOP_DURUM 23  // giris_pullup; PC817 #1; HIGH = mantar basili / F5 atti
#define PIN_BARA_DURUM      5   // giris_pullup; PC817 #2; LOW = bara gerilimli; strapping, yalniz SDIO zamanlamasi
#define PIN_I2C_SDA         21  // i2c
#define PIN_I2C_SCL         22  // i2c
#define PIN_SOL_ENK_A       18  // giris; PCNT
#define PIN_SOL_ENK_B       17  // giris; PCNT; 1k seri; acilista PSRAM yoklamasi surer
#define PIN_SAG_ENK_A       16  // giris; PCNT; 1k seri; acilista PSRAM yoklamasi surer
#define PIN_SAG_ENK_B       15  // giris; PCNT; strapping: LOW ise yalniz ROM acilis yazisi susar
#define PIN_UART0_TX        1   // uart; CP2102 -> Pi
#define PIN_UART0_RX        3   // uart; CP2102 -> Pi
#define PIN_DURUM_LED       2   // cikis; kart ustu LED; strapping; disariya baglanmaz
// GPIO12: BOS -- strapping (MTDI); hicbir seye baglanmaz

// --- I2C ---
#define PCA9685_ADRES 0x40
// BNO055: 0x28 / 0x29 (ayni hat, SDA/SCL yukarida)

// --- PCA9685 kanallari (servo kanallarinin tek kaynagi kod/jestler/kanallar.yaml; burada bilgi) ---
// 0 sag_omuz, 1 sag_omuz_yan, 2 sag_dirsek, 3 sag_bilek, 4 kafa_pan, 5 sol_omuz, 6 sol_omuz_yan, 7 sol_dirsek, 8 sol_bilek, 9 kafa_tilt, 10 sonar_sag_trig, 11 sonar_orta_trig, 12 sonar_sol_trig, 13 yedek, 14 yedek, 15 yedek
#define PCA_KANAL_SONAR_SAG_TRIG 10
#define PCA_KANAL_SONAR_ORTA_TRIG 11
#define PCA_KANAL_SONAR_SOL_TRIG 12

// --- Devreye alma (arm) zamanlamasi, ms (rapor Y4; guc.cpp) ---
#define ARM_ONSARJ_BEKLEME_MS 500   // K2 (GPIO19) cekildikten sonra bara (GPIO5) LOW beklenir
#define ARM_K1_SONRASI_MS 100   // K1 (GPIO4) cekildikten sonra K2 birakilir
#define ARM_K2_EN_COK_MS 1000   // K2 bundan uzun HIGH kalmaz (esp_timer zorlar)
