// main.cpp -- Tekerlekli insansı robot, ESP32 alt denetleyici (MCBÜ Mekatronik).
//
// ESP32'nin işi: Pi'den gelen kısa komutları (seri JSON) uygulamak.
//   - kollar ve kafa: PCA9685 + servolar, kayıtlı jestler (servolar.*, jestler.*)
//   - tekerlekler: 2 x BTS7960 + JGB37 enkoderli motor (motorlar.*)
//   - güvenlik: 500 ms komut bekçisi + döngü bekçisi (watchdog.*)
//   - konum: 10 Hz odometri yayını {"k":"odo",...} (enkoder tikleri + IMU yaw; IMU şimdilik yok, imu.*)
//   - haberleşme: seri_protokol.*  |  pinler: include/pinler.h
//
// ======================= GÜÇ NOTU (kablajdan ÖNCE oku) =======================
// 1) SERVO GÜCÜ AYRI: servolar PCA9685'in V+ klemensinden, kendi DC-DC'sinden beslenir (5-7,4 V;
//    DS3218/MG996R için 6 V iyi). Akım toplamı: servo başına durmada ~2-2,5 A, 6 servo -> 10 A+
//    tepe. DC-DC buna göre seçilir, V+ ile GND arasına büyük kondansatör (ör. 1000 uF) konur.
// 2) MANTIK AYRI: ESP32 ve Pi kendi temiz 5 V hatlarından beslenir. Pi'nin USB'sinden SERVO
//    BESLENMEZ: servo çektiği ani akımla voltaj düşer, Pi ve ESP32 resetlenir (brownout).
// 3) ORTAK TOPRAK: akü eksi, servo DC-DC eksi, BTS7960 GND, ESP32 GND, Pi GND birleşir.
//    Toprak ortak olmazsa PWM/I2C sinyalleri "havada" kalır, servolar titrer.
// 4) ACİL STOP: Emas butonu motor ve servo güç hatlarını DOĞRUDAN keser. Yazılımdan bağımsızdır;
//    bu kod çökse de, kilitlense de robotu durdurur. Yazılım bekçileri bunun yerine geçmez.
// =============================================================================
//
// DURUM: Donanımda DOĞRULANMADI (26 Ekim 2026). Pinler, yönler, sınırlar, enkoder sayısı tahmini.
// Döngü yapısı: delay() yok. loop() hep döner, her iş kendi zamanı gelince yapılır.
#include <Arduino.h>

#include "imu.h"
#include "jestler.h"
#include "motorlar.h"
#include "pinler.h"
#include "seri_protokol.h"
#include "servolar.h"
#include "watchdog.h"

// 1 s'de bir {"k":"durum",...} gönderilsin mi? platformio.ini'de -DDURUM_YAYINI=1 ile açılır.
#ifndef DURUM_YAYINI
#define DURUM_YAYINI 0
#endif
// Odometri yayını (ODO_YAYINI, ODO_ARALIK_MS) seri_protokol.h'de: varsayılan AÇIK, 100 ms.

namespace {

constexpr uint32_t SERVO_ARALIK_MS = 20;    // servo + jest güncellemesi (50 Hz)
constexpr uint32_t MOTOR_ARALIK_MS = 20;    // motor kontrolü (50 Hz; motorlar.cpp DT ile aynı olmalı)
constexpr uint32_t DURUM_ARALIK_MS = 1000;

uint32_t son_servo_ms = 0;
uint32_t son_motor_ms = 0;
uint32_t son_durum_ms = 0;
uint32_t son_odo_ms = 0;

// LED: normalde 1 Hz yanıp söner (program çalışıyor). PCA9685 bulunamadıysa hızlı (5 Hz) söner.
void led_guncelle(uint32_t simdi_ms) {
  uint32_t yarim_periyot = servolar_hazir() ? 500 : 100;
  digitalWrite(PIN_DURUM_LED, ((simdi_ms / yarim_periyot) % 2) ? HIGH : LOW);
}

}  // namespace

void setup() {
  pinMode(PIN_DURUM_LED, OUTPUT);
  motorlar_baslat();          // önce motorlar: sürücüler PWM=0 iken etkinleşsin
  servolar_baslat();          // I2C + PCA9685; bulunamazsa servo komutları hata döner
  imu_baslat();               // aynı I2C hattı (Wire servolar_baslat'ta açıldı); IMU yoksa yaw null
  seri_baslat();              // {"k":"hazir",...} gönderir
  watchdog_baslat();
  uint32_t simdi = millis();
  son_servo_ms = son_motor_ms = son_durum_ms = son_odo_ms = simdi;
}

void loop() {
  const uint32_t simdi = millis();

  seri_isle(simdi);           // gelen komutlar (beklemez)
  watchdog_kontrol(simdi);    // 500 ms "sur" gelmediyse motorları durdur

  if (simdi - son_motor_ms >= MOTOR_ARALIK_MS) {
    son_motor_ms += MOTOR_ARALIK_MS;
    if (simdi - son_motor_ms >= MOTOR_ARALIK_MS) son_motor_ms = simdi;   // geride kaldıysa yakala
    motorlar_guncelle(simdi);
  }

  if (simdi - son_servo_ms >= SERVO_ARALIK_MS) {
    son_servo_ms += SERVO_ARALIK_MS;
    if (simdi - son_servo_ms >= SERVO_ARALIK_MS) son_servo_ms = simdi;
    jestler_guncelle(simdi);  // jest servo HEDEFLERİNİ ayarlar
    servolar_guncelle();      // servolar hedefe sınırlı adımla gider
  }

#if DURUM_YAYINI
  if (simdi - son_durum_ms >= DURUM_ARALIK_MS) {
    son_durum_ms = simdi;
    seri_durum_gonder();
  }
#else
  (void)son_durum_ms;
  (void)DURUM_ARALIK_MS;
#endif

#if ODO_YAYINI
  // Odometri: sabit aralıkla gönder (Pi ölü hesap için zaman damgası "ms"yi kullanır).
  // Yalnız gönderir; komut bekçisini beslemez, motorları etkilemez.
  if (simdi - son_odo_ms >= (uint32_t)ODO_ARALIK_MS) {
    son_odo_ms += ODO_ARALIK_MS;
    if (simdi - son_odo_ms >= (uint32_t)ODO_ARALIK_MS) son_odo_ms = simdi;   // geride kaldıysa yakala
    seri_odo_gonder(simdi);
  }
#else
  (void)son_odo_ms;
#endif

  led_guncelle(simdi);
}
