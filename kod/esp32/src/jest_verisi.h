// OTOMATIK URETILDI: kod/jestler/jest_uret.py -- ELLE DUZENLEME.
// Kaynak: kod/jestler/kanallar.yaml ve kod/jestler/*.yaml; aci sinirlari
//         kod/ortak/eklem_sinirlari.json (robot acisi = eklem acisi + eklem_ofset)
// Degistirmek icin YAML'i duzenle, sonra: py -3 kod/jestler/jest_uret.py
// Bu dosya yalniz servolar.cpp ve jestler.cpp tarafindan include edilir.
#pragma once
#include <stdint.h>

#define SERVO_PWM_FREKANS 50
#define SERVO_SAYISI 10
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
  {"sag_omuz", 0, 500, 2500, 0.0f, 180.0f, 85.0f, false},  // DS3235, eklem r_s1 +45, ayna: sol_omuz (ayni)
  {"sag_omuz_yan", 1, 500, 2500, 5.0f, 120.0f, 85.0f, false},  // DS3235, eklem r_s2 +0, ayna: sol_omuz_yan (ayni)
  {"sag_dirsek", 2, 500, 2500, 0.0f, 105.0f, 120.0f, false},  // MG996R, eklem r_dirsek +0, ayna: sol_dirsek (ayni)
  {"sag_bilek", 3, 500, 2500, 0.0f, 180.0f, 120.0f, false},  // MG996R, eklem r_bilek +90, ayna: sol_bilek (ayni)
  {"kafa_pan", 4, 500, 2500, 0.0f, 180.0f, 90.0f, false},  // MG996R, eklem pan +90, ayna: kafa_pan (180-aci)
  {"sol_omuz", 5, 500, 2500, 0.0f, 180.0f, 85.0f, true},  // DS3235, eklem l_s1 +45, ayna: sag_omuz (ayni)
  {"sol_omuz_yan", 6, 500, 2500, 5.0f, 120.0f, 85.0f, true},  // DS3235, eklem l_s2 +0, ayna: sag_omuz_yan (ayni)
  {"sol_dirsek", 7, 500, 2500, 0.0f, 105.0f, 120.0f, true},  // MG996R, eklem l_dirsek +0, ayna: sag_dirsek (ayni)
  {"sol_bilek", 8, 500, 2500, 0.0f, 180.0f, 120.0f, true},  // MG996R, eklem l_bilek +90, ayna: sag_bilek (ayni)
  {"kafa_tilt", 9, 500, 2500, 77.0f, 103.0f, 60.0f, false},  // MG996R, eklem tilt +90, ayna: kafa_tilt (ayni)
};

// Bosta durus: bosta.yaml son karesi. Acilista ve her jest bitince servolar buraya doner.
static const float BOSTA_DURUS[SERVO_SAYISI] = {45.0f, 5.0f, 0.0f, 90.0f, 90.0f, 45.0f, 5.0f, 0.0f, 90.0f, 90.0f};

// bosta: Ev pozu: kollar aşağıda gövde yanında, kafa ileri
//   sutunlar: sag_omuz, sag_omuz_yan, sag_dirsek, sag_bilek, kafa_pan, sol_omuz, sol_omuz_yan, sol_dirsek, sol_bilek, kafa_tilt
static const JestKare JEST_BOSTA[] = {
  {0, {45.0f, 5.0f, 0.0f, 90.0f, 90.0f, 45.0f, 5.0f, 0.0f, 90.0f, 90.0f}},
  {1000, {45.0f, 5.0f, 0.0f, 90.0f, 90.0f, 45.0f, 5.0f, 0.0f, 90.0f, 90.0f}},
};

// evet: Başla onaylama
//   sutunlar: sag_omuz, sag_omuz_yan, sag_dirsek, sag_bilek, kafa_pan, sol_omuz, sol_omuz_yan, sol_dirsek, sol_bilek, kafa_tilt
static const JestKare JEST_EVET[] = {
  {0, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
  {350, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 80.0f}},
  {700, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 100.0f}},
  {1050, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 80.0f}},
  {1400, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 100.0f}},
  {1750, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
};

// isaret: Sağ kolla sağa doğru işaret
//   sutunlar: sag_omuz, sag_omuz_yan, sag_dirsek, sag_bilek, kafa_pan, sol_omuz, sol_omuz_yan, sol_dirsek, sol_bilek, kafa_tilt
static const JestKare JEST_ISARET[] = {
  {0, {45.0f, 5.0f, 0.0f, 90.0f, 90.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
  {1200, {70.0f, 80.0f, 0.0f, 90.0f, 70.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
  {2700, {70.0f, 80.0f, 0.0f, 90.0f, 70.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
};

// isaret yon=sol (varsayilanin aynasi)
static const JestKare JEST_ISARET_SOL[] = {
  {0, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f, 45.0f, 5.0f, 0.0f, 90.0f, 90.0f}},
  {1200, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 110.0f, 70.0f, 80.0f, 0.0f, 90.0f, 90.0f}},
  {2700, {ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 110.0f, 70.0f, 80.0f, 0.0f, 90.0f, 90.0f}},
};

// isaret yon=ileri (kendi kareleri)
static const JestKare JEST_ISARET_ILERI[] = {
  {0, {45.0f, 5.0f, 0.0f, ACI_YOK, 90.0f, 45.0f, 5.0f, 0.0f, ACI_YOK, 90.0f}},
  {1200, {135.0f, 10.0f, 0.0f, ACI_YOK, 90.0f, 135.0f, 10.0f, 0.0f, ACI_YOK, 85.0f}},
  {2700, {135.0f, 10.0f, 0.0f, ACI_YOK, 90.0f, 135.0f, 10.0f, 0.0f, ACI_YOK, 85.0f}},
};

// isaret yon=arka (kendi kareleri)
static const JestKare JEST_ISARET_ARKA[] = {
  {0, {45.0f, 5.0f, 0.0f, 90.0f, 90.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
  {1700, {10.0f, 40.0f, 0.0f, 90.0f, 45.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
  {3200, {10.0f, 40.0f, 0.0f, 90.0f, 45.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, 90.0f}},
};

// selam: Sağ elle el sallama
//   sutunlar: sag_omuz, sag_omuz_yan, sag_dirsek, sag_bilek, kafa_pan, sol_omuz, sol_omuz_yan, sol_dirsek, sol_bilek, kafa_tilt
static const JestKare JEST_SELAM[] = {
  {0, {45.0f, 5.0f, 0.0f, 90.0f, 90.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {1700, {75.0f, 100.0f, 60.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {2100, {75.0f, 100.0f, 90.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {2500, {75.0f, 100.0f, 60.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {2900, {75.0f, 100.0f, 90.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {3300, {75.0f, 100.0f, 60.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {3700, {75.0f, 100.0f, 90.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {4100, {75.0f, 100.0f, 60.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
  {4500, {75.0f, 100.0f, 60.0f, 90.0f, 80.0f, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK, ACI_YOK}},
};

// {ad, varsayilan, kare sayisi, {sol, sag, ileri, arka} kareleri, ayni sirada kare sayilari}
static const JestTanim JEST_TABLOSU[JEST_SAYISI] = {
  {"bosta", JEST_BOSTA, 2, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},
  {"evet", JEST_EVET, 6, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},
  {"isaret", JEST_ISARET, 3, {JEST_ISARET_SOL, JEST_ISARET, JEST_ISARET_ILERI, JEST_ISARET_ARKA}, {3, 3, 3, 3}},
  {"selam", JEST_SELAM, 9, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},
};
