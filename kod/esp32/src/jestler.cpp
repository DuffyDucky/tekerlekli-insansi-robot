// jestler.cpp -- bkz. jestler.h
#include "jestler.h"

#include <string.h>

#include "jest_verisi.h"
#include "servolar.h"

namespace {

const JestTanim* aktif = nullptr;   // oynayan jest; nullptr = jest yok
uint32_t baslangic_ms = 0;

// Bir kareyi (ya da iki kare arası ara değeri) servo hedeflerine yazar.
// oran = 0 -> a karesi, oran = 1 -> b karesi.
void hedefleri_yaz(const JestKare& a, const JestKare& b, float oran) {
  for (uint8_t i = 0; i < SERVO_SAYISI; i++) {
    if (a.aci[i] == ACI_YOK) continue;        // bu jest bu kanala dokunmuyor
    float aci = a.aci[i] + (b.aci[i] - a.aci[i]) * oran;
    servo_hedef_ayarla(i, aci);
  }
}

}  // namespace

bool jest_baslat(const char* ad, uint32_t simdi_ms) {
  if (ad == nullptr) return false;
  for (uint8_t j = 0; j < JEST_SAYISI; j++) {
    if (strcmp(JEST_TABLOSU[j].ad, ad) == 0) {
      aktif = &JEST_TABLOSU[j];
      baslangic_ms = simdi_ms;
      jestler_guncelle(simdi_ms);             // ilk kareyi hemen hedefle
      return true;
    }
  }
  return false;
}

void jest_durdur() { aktif = nullptr; }

void jestler_guncelle(uint32_t simdi_ms) {
  if (aktif == nullptr) return;
  const JestKare* k = aktif->kareler;
  const uint8_t n = aktif->kare_sayisi;
  const uint32_t t = simdi_ms - baslangic_ms;   // işaretsiz çıkarma: millis() taşmasında da doğru

  if (t >= k[n - 1].ms) {                       // jest bitti
    hedefleri_yaz(k[n - 1], k[n - 1], 0.0f);
    aktif = nullptr;
    servolar_bostaya();                         // bitince boşta duruşa dön
    return;
  }
  if (t <= k[0].ms) {                           // ilk kareden önce: ilk kareyi tut
    hedefleri_yaz(k[0], k[0], 0.0f);
    return;
  }
  // t hangi iki karenin arasında? (kareler zamana göre sıralı; üretici bunu denetler)
  uint8_t i = 0;
  while (i + 1 < n && k[i + 1].ms <= t) i++;
  const JestKare& a = k[i];
  const JestKare& b = k[i + 1];
  float oran = (float)(t - a.ms) / (float)(b.ms - a.ms);
  hedefleri_yaz(a, b, oran);
}

const char* jest_aktif_adi() { return aktif ? aktif->ad : "yok"; }

uint8_t jest_sayisi() { return JEST_SAYISI; }

const char* jest_adi(uint8_t sira) { return sira < JEST_SAYISI ? JEST_TABLOSU[sira].ad : ""; }
