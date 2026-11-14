// main.cpp -- Tekerlekli insansı robot, ESP32 alt denetleyici (MCBÜ Mekatronik). Sürüm 0.5.0.
//
// ESP32'nin işi: Pi'den gelen kısa komutları (seri JSON) uygulamak.
//   - güç: K1 / K2 röleleri, acil stop ve bara izleme, arıza durum makinesi (guc.*)
//   - kollar ve kafa: PCA9685 + servolar, kayıtlı jestler (servolar.*, jestler.*)
//   - tekerlekler: 2 x BTS7960 + JGB37 enkoderli motor, PCNT sayaç (motorlar.*)
//   - güvenlik: 500 ms komut bekçisi + döngü bekçisi (watchdog.*); ivme/fren sınırı ve rampa kipi
//     (motorlar.*, seri_protokol.*; IMU eğimi geçerliyse rampa kipi burada otomatik açılır)
//   - konum: 10 Hz odometri yayını {"k":"odo",...} (enkoder tikleri + IMU yaw; IMU şimdilik yok, imu.*)
//   - haberleşme: seri_protokol.*  |  pinler: include/pinler.h (ÜRETİLİR: kod/ortak/pinler.json)
//
// BU FIRMWARE YALNIZ PİN HARİTASI SÜRÜM 4 KABLAJINA YÜKLENİR (14.11.2026; planlama/adim3/pin-haritasi.md,
// dal lale-duzeltme). 0.4.0 ve öncesi bu kablaja, 0.5.0 eski kablaja yüklenmez.
//
// ======================= GÜÇ NOTU (kablajdan ÖNCE oku) =======================
// 1) ANAHTARLI BARA: motor sürücüleri (BTS7960) ve servo DC-DC'leri (üç XL4016: sağ kol A, sol kol B,
//    kafa C) akünün anahtarlı barasından beslenir. Barayı K1 rölesi (GPIO4) bağlar; önce K2 (GPIO19)
//    barayı 5,6 ohm ön şarj direnciyle doldurur. Sıra guc.cpp'de ("arm"); açılışta bara HEP kapalıdır.
// 2) ACİL STOP: Emas mantarı iki rölenin BOBİN beslemesini keser (mantar NC kontağı bobinden önce).
//    Basılıyken firmware ne yaparsa yapsın röle çekmez, bara düşer: motorlar boşa düşer, KOLLAR DÜŞER
//    (bilinen, kabul edilmiş davranış). ESP32 mantarın durumunu GPIO23'ten yalnız OKUR.
// 3) MANTIK AYRI: ESP32 ve Pi kendi temiz 5 V hatlarından beslenir (bara kapalıyken de çalışır).
//    PCA9685'in mantığı ESP32'nin 3,3 V'undan: bara kapalıyken de I2C'de cevap verir.
//    Servo asla Pi'nin USB'sinden beslenmez (ani akım -> brownout -> reset).
// 4) ORTAK TOPRAK: akü eksi, DC-DC eksileri, BTS7960 GND, ESP32 GND, Pi GND birleşir.
// 5) Reset / çökme / yükleme / USB sökme anında 4, 19, 13 çıkışı kapanır; taban (2,2 kOhm) ve EN (10 kOhm)
//    pull-down dirençleri onları LOW tutar: röleler bırakır, motorlar kilitli kalır (rapor §4).
// =============================================================================
//
// KURULUM SIRASI (rapor Y2): 1) 4, 19, 13 LOW çıkış  2) motor PWM'leri görev oranı 0 ile, PCNT
// 3) LED, acil stop / bara girişleri, ADC, K2 zamanlayıcısı  4) I2C + PCA9685  5) IMU  6) seri ("hazir")
// 7) döngü bekçisi. Serial1 / Serial2 / SPI hiç açılmaz; GPIO12 hiç ayarlanmaz.
//
// DURUM: Donanımda DOĞRULANMADI (14.11.2026, 0.5.0 yalnız derlendi). Pinler kesin karar; yönler,
// sınırlar, enkoder sayısı, IS eşiği ve akü ölçeği tahmini. Döngü: delay() yok, her iş kendi zamanında.
#include <Arduino.h>
#include <math.h>

#include "guc.h"
#include "imu.h"
#include "jestler.h"
#include "motorlar.h"
#include "pinler.h"
#include "seri_protokol.h"
#include "servolar.h"
#include "watchdog.h"

static_assert(PIN_HARITASI_SURUM == 4,
              "Bu firmware (0.5.0) pin haritasi surum 4 icin yazildi; kod/ortak/pinler.json surumunu denetle");

// 1 s'de bir {"k":"durum",...} gönderilsin mi? platformio.ini'de -DDURUM_YAYINI=1 ile açılır.
#ifndef DURUM_YAYINI
#define DURUM_YAYINI 0
#endif
// Odometri yayını (ODO_YAYINI, ODO_ARALIK_MS) seri_protokol.h'de: varsayılan AÇIK, 100 ms.

namespace {

constexpr uint32_t SERVO_ARALIK_MS = 20;    // servo + jest güncellemesi (50 Hz)
constexpr uint32_t MOTOR_ARALIK_MS = 20;    // motor kontrolü (50 Hz; motorlar.cpp DT ile aynı olmalı)
constexpr uint32_t DURUM_ARALIK_MS = 1000;

// Otomatik rampa kipi (IMU eğimi). Değerler TAHMİNİ: rampada ölçüp ayarla. Histerezis: eşikte
// titreşip kip açılıp kapanmasın diye açma ve kapama eşiği farklı.
constexpr float RAMPA_EGIM_AC = 3.0f;       // derece: bu eğimin üstünde rampa kipi açılır
constexpr float RAMPA_EGIM_KAPAT = 1.5f;    // derece: bunun altına inince (elle açık değilse) kapanır
constexpr uint32_t EGIM_ARALIK_MS = 100;

uint32_t son_servo_ms = 0;
uint32_t son_motor_ms = 0;
uint32_t son_durum_ms = 0;
uint32_t son_odo_ms = 0;
uint32_t son_egim_ms = 0;
bool egimde = false;

// IMU eğimi geçerliyse (sonlu) histerezisle "eğimde" kararını verir ve seri_protokol'e bildirir.
// IMU yoksa ya da değer geçersizse son karar korunur (açılışta kapalı): otomatik kip çalışmaz,
// elle kip ({"k":"rampa"}) her durumda çalışır.
void egim_denetle() {
  const float egim = imu_egim_derece();
  if (!isfinite(egim)) return;
  if (!egimde && egim >= RAMPA_EGIM_AC) egimde = true;
  else if (egimde && egim <= RAMPA_EGIM_KAPAT) egimde = false;
  rampa_imu_bildir(egimde);
}

// LED (yalnız kart üstü, GPIO2; dışarıya hiçbir şey bağlanmaz):
//   ARIZA (güç "ariza"):  çift yanıp sönme (iki kısa parlama, uzun ara; 1,2 s'de bir) -- en öncelikli
//   PCA9685 bulunamadı:   hızlı, 5 Hz
//   normal:               1 Hz (program çalışıyor)
void led_guncelle(uint32_t simdi_ms) {
  bool yanik;
  if (guc_ariza_mi()) {
    const uint32_t t = simdi_ms % 1200;
    yanik = (t < 100) || (t >= 250 && t < 350);
  } else {
    const uint32_t yarim_periyot = servolar_hazir() ? 500 : 100;
    yanik = (simdi_ms / yarim_periyot) % 2;
  }
  digitalWrite(PIN_DURUM_LED, yanik ? HIGH : LOW);
}

}  // namespace

void setup() {
  guc_pinleri_guvenle();      // İLK İŞ: röleler (4, 19) ve EN (13) LOW çıkış -- her şeyden önce
  motorlar_baslat();          // PWM'ler görev oranı 0 ile; PCNT enkoder sayaçları
  pinMode(PIN_DURUM_LED, OUTPUT);
  guc_baslat();               // acil stop / bara girişleri, IS ve akü ADC'si, K2 zamanlayıcısı
  servolar_baslat();          // I2C + PCA9685; bulunamazsa servo komutları hata döner, arm reddedilir
  imu_baslat();               // aynı I2C hattı (Wire servolar_baslat'ta açıldı); IMU yoksa yaw null
  seri_baslat();              // {"k":"hazir",...,"guc":"birakik"} gönderir
  watchdog_baslat();
  uint32_t simdi = millis();
  son_servo_ms = son_motor_ms = son_durum_ms = son_odo_ms = son_egim_ms = simdi;
}

void loop() {
  const uint32_t simdi = millis();

  guc_guncelle(simdi);        // önce güç: acil stop / bara / arıza bu turda görülsün, arm sırası yürüsün
  seri_isle(simdi);           // gelen komutlar (beklemez)
  watchdog_kontrol(simdi);    // 500 ms "sur" gelmediyse motorları ANINDA durdur (K1'e dokunmaz)

  if (simdi - son_egim_ms >= EGIM_ARALIK_MS) {
    son_egim_ms = simdi;
    egim_denetle();           // eğimde: rampa kipi (ivme 0,1 m/s^2, kollar ev pozunda)
  }

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
  // Yalnız gönderir; komut bekçisini ve sessizlik sayacını beslemez, motorları etkilemez.
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
