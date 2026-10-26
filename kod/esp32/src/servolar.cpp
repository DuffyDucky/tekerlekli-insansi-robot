// servolar.cpp -- bkz. servolar.h
//
// GÜÇ UYARISI: Servolar PCA9685'in V+ klemensinden AYRI bir hattan beslenir (5-7,4 V, servo
// datasheet'ine bak; DS3218 ve MG996R 6 V'ta güvenli). Durma akımı servo başına ~2-2,5 A olabilir;
// 6 servo aynı anda zorlanırsa 10 A'yı aşar, DC-DC/BEC buna göre seçilir. PCA9685'in VCC pini
// (mantık) ESP32'nin 3,3 V'undan beslenir. Servoların gücü ASLA ESP32'den ya da Pi'nin USB'sinden
// alınmaz: ani akım voltajı düşürür, Pi/ESP32 kendini resetler (brownout). Topraklar ortak.
#include "servolar.h"

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#include "pinler.h"
#include "jest_verisi.h"

namespace {

constexpr float GUNCELLEME_SANIYE = 0.020f;   // servolar_guncelle() çağrı aralığı (20 ms)

Adafruit_PWMServoDriver pca(PCA9685_ADRES);
bool pca_var = false;

float simdiki[SERVO_SAYISI];   // şu an servoya yazılmış robot açısı
float hedef[SERVO_SAYISI];     // gidilmek istenen robot açısı

float sinira_kirp(uint8_t i, float aci) {
  const ServoTanim& t = SERVO_TABLOSU[i];
  if (aci < t.min_aci) return t.min_aci;
  if (aci > t.max_aci) return t.max_aci;
  return aci;
}

// Robot açısını darbe genişliğine (mikrosaniye) çevirip PCA9685'e yazar.
void pca_yaz(uint8_t i, float robot_acisi) {
  if (!pca_var) return;
  const ServoTanim& t = SERVO_TABLOSU[i];
  float servo_acisi = t.ters ? (180.0f - robot_acisi) : robot_acisi;
  float us = t.min_us + (t.max_us - t.min_us) * (servo_acisi / 180.0f);
  pca.writeMicroseconds(t.kanal, (uint16_t)(us + 0.5f));
}

}  // namespace

bool servolar_baslat() {
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(400000);
  Wire.setTimeOut(20);                     // I2C takılırsa en çok 20 ms bekle (sonsuza kadar değil)

  pca_var = pca.begin();                   // cihaz cevap vermezse false
  if (pca_var) {
    // PCA9685'in iç osilatörü 25 MHz yazılır ama kartlar arası 23-27 MHz değişir. Servo açısı
    // kaymışsa osiloskopla 1500 us ölçüp bu sayıyı düzelt.
    pca.setOscillatorFrequency(27000000);
    pca.setPWMFreq(SERVO_PWM_FREKANS);
    delay(10);
  }

  // Açılışta servonun gerçek konumu bilinmez; ilk darbe servoyu boşta duruşa TEK SEFERDE götürür
  // (bu hareket yumuşatılamaz). Bu yüzden ilk açılışta kolların önü boş olmalı.
  for (uint8_t i = 0; i < SERVO_SAYISI; i++) {
    simdiki[i] = hedef[i] = sinira_kirp(i, BOSTA_DURUS[i]);
    pca_yaz(i, simdiki[i]);
  }
  return pca_var;
}

bool servolar_hazir() { return pca_var; }

uint8_t servo_sayisi() { return SERVO_SAYISI; }

const char* servo_adi(uint8_t sira) {
  return sira < SERVO_SAYISI ? SERVO_TABLOSU[sira].ad : "";
}

int servo_sira_kanaldan(int kanal) {
  for (uint8_t i = 0; i < SERVO_SAYISI; i++) {
    if (SERVO_TABLOSU[i].kanal == kanal) return i;
  }
  return -1;
}

int servo_sira_addan(const char* ad) {
  if (ad == nullptr) return -1;
  for (uint8_t i = 0; i < SERVO_SAYISI; i++) {
    if (strcmp(SERVO_TABLOSU[i].ad, ad) == 0) return i;
  }
  return -1;
}

float servo_hedef_ayarla(uint8_t sira, float robot_acisi) {
  if (sira >= SERVO_SAYISI) return 0.0f;
  hedef[sira] = sinira_kirp(sira, robot_acisi);
  return hedef[sira];
}

void servolar_bostaya() {
  for (uint8_t i = 0; i < SERVO_SAYISI; i++) hedef[i] = sinira_kirp(i, BOSTA_DURUS[i]);
}

void servolar_guncelle() {
  for (uint8_t i = 0; i < SERVO_SAYISI; i++) {
    if (simdiki[i] == hedef[i]) continue;             // yerinde: I2C'ye boşuna yazma
    float fark = hedef[i] - simdiki[i];
    float adim = SERVO_TABLOSU[i].hiz * GUNCELLEME_SANIYE;
    if (fark > adim) {
      simdiki[i] += adim;
    } else if (fark < -adim) {
      simdiki[i] -= adim;
    } else {
      simdiki[i] = hedef[i];                          // son adım: tam hedefe otur
    }
    pca_yaz(i, simdiki[i]);
  }
}
