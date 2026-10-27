// OTOMATIK URETILDI: kod/jestler/jest_uret.py -- ELLE DUZENLEME.
// Kaynak: kod/jestler/kanallar.yaml ve kod/jestler/*.yaml
// Degistirmek icin YAML'i duzenle, sonra: py -3 kod/jestler/jest_uret.py
// Bu dosya yalniz servolar.cpp ve jestler.cpp tarafindan include edilir.
#pragma once
#include <stdint.h>

#define SERVO_PWM_FREKANS 50
#define SERVO_SAYISI 6
#define JEST_SAYISI 4
#define YON_SAYISI 4
#define ACI_YOK (-1.0f)   // bu jest bu kanala dokunmaz

// Seri protokoldeki "yon" degerleri; JestTanim.yon_* dizilerinin sirasi.
static const char* const YON_ADLARI[YON_SAYISI] = {"sol", "sag", "ileri", "arka"};

struct ServoTanim {
  const char* ad;      // kanallar.yaml'daki ad (ör. sag_omuz)
  uint8_t kanal;       // PCA9685 cikisi 0-15
  uint16_t min_us;     // servo acisi 0 derecedeki darbe
  uint16_t max_us;     // servo acisi 180 derecedeki darbe
  float min_aci;       // izin verilen robot acisi (alt)
  float max_aci;       // izin verilen robot acisi (ust)
  float hiz;           // en fazla derece/saniye
  bool ters;           // true: servo acisi = 180 - robot acisi
};

struct JestKare {
  uint16_t ms;                 // jest basindan beri gecen sure
  float aci[SERVO_SAYISI];     // her kanalin robot acisi; ACI_YOK = dokunma
};

struct JestTanim {
  const char* ad;
  const JestKare* kareler;                    // varsayilan (yon yok ya da varyanti yok)
  uint8_t kare_sayisi;
  const JestKare* yon_kareleri[YON_SAYISI];   // YON_ADLARI sirasi; nullptr = varyant yok
  uint8_t yon_kare_sayisi[YON_SAYISI];
};

// Dizi sirasi = kanal numarasi sirasi (SERVO_TABLOSU[i].kanal ile PCA9685 cikisi bulunur)
// Ayna (yonlu jest 'sol' varyanti) uretim aninda uygulanir; burada yalniz bilgi icin yazili.
static const ServoTanim SERVO_TABLOSU[SERVO_SAYISI] = {
  {"sag_omuz", 0, 500, 2500, 0.0f, 160.0f, 90.0f, false},  // DS3218, ayna: sol_omuz (ayni)
  {"sag_dirsek", 1, 500, 2500, 0.0f, 110.0f, 120.0f, false},  // MG996R, ayna: sol_dirsek (ayni)
  {"sol_omuz", 2, 500, 2500, 0.0f, 160.0f, 90.0f, true},  // DS3218, ayna: sag_omuz (ayni)
  {"sol_dirsek", 3, 500, 2500, 0.0f, 110.0f, 120.0f, true},  // MG996R, ayna: sag_dirsek (ayni)
  {"kafa_pan", 4, 500, 2500, 45.0f, 135.0f, 90.0f, false},  // MG996R, ayna: kafa_pan (180-aci)
  {"kafa_tilt", 5, 500, 2500, 70.0f, 110.0f, 60.0f, false},  // MG996R, ayna: kafa_tilt (ayni)
};

// Bosta durus: bosta.yaml son karesi. Acilista ve her jest bitince servolar buraya doner.
static const float BOSTA_DURUS[SERVO_SAYISI] = {10.0f, 15.0f, 10.0f, 15.0f, 90.0f, 90.0f};

// bosta: Kollar hafif açık aşağıda, kafa ileri
//   sutunlar: sag_omuz, sag_dirsek, sol_omuz, sol_dirsek, kafa_pan, kafa_tilt
static const JestKare JEST_BOSTA[] = {
  {0, {10.0f, 15.0f, 10.0f, 15.0f, 90.0f, 90.0f}},
  {1000, {10.0f, 15.0f, 10.0f, 15.0f, 90.0f, 90.0f}},
};

// evet: Başla onaylama
//   sutunlar: sag_omuz, sag_dirsek, sol_omuz, sol_dirsek, kafa_pan, kafa_tilt
static const JestKare JEST_EVET[] = {
  {0, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
  {350, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 75.0f}},
  {700, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 95.0f}},
  {1050, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 75.0f}},
  {1400, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 95.0f}},
  {1750, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
};

// isaret: Sağ kolla öne doğru işaret
//   sutunlar: sag_omuz, sag_dirsek, sol_omuz, sol_dirsek, kafa_pan, kafa_tilt
static const JestKare JEST_ISARET[] = {
  {0, {10.0f, 15.0f, ACI_YOK, ACI_YOK, 90.0f, 90.0f}},
  {1200, {90.0f, 0.0f, ACI_YOK, ACI_YOK, 70.0f, 90.0f}},
  {2700, {90.0f, 0.0f, ACI_YOK, ACI_YOK, 70.0f, 90.0f}},
};

// isaret yon=sol (varsayilanin aynasi)
static const JestKare JEST_ISARET_SOL[] = {
  {0, {ACI_YOK, ACI_YOK, 10.0f, 15.0f, 90.0f, 90.0f}},
  {1200, {ACI_YOK, ACI_YOK, 90.0f, 0.0f, 110.0f, 90.0f}},
  {2700, {ACI_YOK, ACI_YOK, 90.0f, 0.0f, 110.0f, 90.0f}},
};

// isaret yon=ileri (kendi kareleri)
static const JestKare JEST_ISARET_ILERI[] = {
  {0, {10.0f, 15.0f, 10.0f, 15.0f, 90.0f, 90.0f}},
  {1200, {70.0f, 0.0f, 70.0f, 0.0f, 90.0f, 85.0f}},
  {2700, {70.0f, 0.0f, 70.0f, 0.0f, 90.0f, 85.0f}},
};

// isaret yon=arka (kendi kareleri)
static const JestKare JEST_ISARET_ARKA[] = {
  {0, {10.0f, 15.0f, ACI_YOK, ACI_YOK, 90.0f, 90.0f}},
  {1700, {150.0f, 90.0f, ACI_YOK, ACI_YOK, 45.0f, 90.0f}},
  {3200, {150.0f, 90.0f, ACI_YOK, ACI_YOK, 45.0f, 90.0f}},
};

// selam: Sağ elle el sallama
//   sutunlar: sag_omuz, sag_dirsek, sol_omuz, sol_dirsek, kafa_pan, kafa_tilt
static const JestKare JEST_SELAM[] = {
  {0, {10.0f, 15.0f, ACI_YOK, ACI_YOK, 90.0f, ACI_YOK}},
  {1700, {150.0f, 40.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {2100, {150.0f, 80.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {2500, {150.0f, 40.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {2900, {150.0f, 80.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {3300, {150.0f, 40.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {3700, {150.0f, 80.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {4100, {150.0f, 40.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
  {4500, {150.0f, 40.0f, ACI_YOK, ACI_YOK, 80.0f, ACI_YOK}},
};

// {ad, varsayilan, kare sayisi, {sol, sag, ileri, arka} kareleri, ayni sirada kare sayilari}
static const JestTanim JEST_TABLOSU[JEST_SAYISI] = {
  {"bosta", JEST_BOSTA, 2, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},
  {"evet", JEST_EVET, 6, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},
  {"isaret", JEST_ISARET, 3, {JEST_ISARET_SOL, JEST_ISARET, JEST_ISARET_ILERI, JEST_ISARET_ARKA}, {3, 3, 3, 3}},
  {"selam", JEST_SELAM, 9, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},
};
