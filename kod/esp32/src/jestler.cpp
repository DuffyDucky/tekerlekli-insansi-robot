// jestler.cpp -- bkz. jestler.h
#include "jestler.h"

#include <string.h>

#include "jest_verisi.h"
#include "servolar.h"

namespace {

const JestTanim* aktif = nullptr;   // oynayan jest; nullptr = jest yok
const JestKare* aktif_kareler = nullptr;   // oynayan kare dizisi (varsayılan ya da yön varyantı)
uint8_t aktif_kare_sayisi = 0;
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

int jest_yon_indeksi(const char* yon) {
  if (yon == nullptr) return -1;
  for (uint8_t y = 0; y < YON_SAYISI; y++) {
    if (strcmp(YON_ADLARI[y], yon) == 0) return y;
  }
  return -1;
}

bool jest_baslat(const char* ad, const char* yon, uint32_t simdi_ms, bool* yon_uygulandi) {
  if (yon_uygulandi != nullptr) *yon_uygulandi = false;
  if (ad == nullptr) return false;
  for (uint8_t j = 0; j < JEST_SAYISI; j++) {
    const JestTanim& t = JEST_TABLOSU[j];
    if (strcmp(t.ad, ad) != 0) continue;
    const JestKare* kareler = t.kareler;
    uint8_t sayi = t.kare_sayisi;
    const int y = jest_yon_indeksi(yon);
    if (y >= 0 && t.yon_kareleri[y] != nullptr && t.yon_kare_sayisi[y] > 0) {
      kareler = t.yon_kareleri[y];
      sayi = t.yon_kare_sayisi[y];
      if (yon_uygulandi != nullptr) *yon_uygulandi = true;
    }
    aktif = &t;
    aktif_kareler = kareler;
    aktif_kare_sayisi = sayi;
    baslangic_ms = simdi_ms;
    jestler_guncelle(simdi_ms);             // ilk kareyi hemen hedefle
    return true;
  }
  return false;
}

void jest_durdur() { aktif = nullptr; }

void jestler_guncelle(uint32_t simdi_ms) {
  if (aktif == nullptr) return;
  const JestKare* k = aktif_kareler;
  const uint8_t n = aktif_kare_sayisi;
  if (k == nullptr || n == 0) { aktif = nullptr; return; }   // üretici bunu engeller; yine de koru
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
