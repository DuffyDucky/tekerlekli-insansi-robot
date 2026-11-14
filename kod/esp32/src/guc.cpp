// guc.cpp -- bkz. guc.h. Beklemesiz: delay() yok; her adım millis() ile zamanlanır.
//
// Okurken akılda tut: bu kod röleyi yalnız ÇEKTİREBİLİR. Bırakmanın asıl güvencesi donanımdadır:
// mantar basılıyken bobin beslemesi yok; reset/çökme/USB sökme anında 4 ve 19'un çıkışı kapanır ve
// 2,2 kOhm taban direnci transistörü kapalı tutar (rapor §4). Yazılım korumaları bunun ÜSTÜNE eklenir.
#include "guc.h"

#include <Arduino.h>
#include <driver/gpio.h>
#include <esp_timer.h>
#include <math.h>

#include "motorlar.h"
#include "pinler.h"
#include "seri_protokol.h"
#include "servolar.h"

namespace {

// ---------------- AYARLAR (TAHMİNİ olanlar işaretli; tek yer burası) ----------------
// Giriş süzgeci (23 acil stop, 5 bara): 2 ms'de bir okunur, art arda 3 aynı okuma = kararlı değer.
// Yani bir değişim ~6 ms sonra kabul edilir. TAHMİNİ: PC817 çıkışı gürültülüyse artır. Acil stopta
// bu gecikme güvenliği azaltmaz: mantar röle bobinini zaten donanımla keser.
constexpr uint32_t GIRIS_ORNEK_MS = 2;
constexpr uint8_t GIRIS_ARDISIK = 3;

// BTS IS arıza bayrağı (rapor Y7, D7): 0 dB zayıflatmada pin ~0,95 V üstünde doyar (ham 4095).
// Arıza akımında pin >= 1,4 V olur -> doyma. Eşik ve art arda örnek sayısı TAHMİNİ:
// T6 ÖLÇÜMÜNDEN SONRA YAZILIR (kart IS direnci, bölücü ve enjeksiyon akımı ölçülünce).
// IS ile durma/sıkışma algılanmaz (kart başına 4 A altı okunmaz); o iş enkoderle yapılacak (kapsam dışı).
constexpr uint32_t IS_ORNEK_MS = 10;
constexpr uint16_t IS_ARIZA_HAM = 4000;        // 12 bit ham değer (0..4095), TAHMİNİ
constexpr uint8_t IS_ARDISIK = 3;              // art arda bu kadar örnek eşik üstünde -> arıza, TAHMİNİ

// PCA9685 yoklaması (yalnız devredeyken): 100 ms'de bir I2C adres yoklaması, art arda 3 cevapsız -> bırak.
constexpr uint32_t I2C_YOKLAMA_MS = 100;
constexpr uint8_t I2C_ARDISIK_HATA = 3;

// Akü (GPIO36): 100k / 18k bölücü -> pin = akü x 18/118. 14,6 V -> 2,23 V: 11 dB zayıflatma
// (ölçülebilir aralık ~150-2450 mV, rapor ADC kaynağı). KALİBRE EDİLMEDİ: multimetreyle karşılaştır,
// gerekirse AKU_OLCEK'i düzelt. Bölücü dirençlerinin %1-5 toleransı doğrudan hataya geçer.
constexpr uint32_t AKU_ORNEK_MS = 200;
constexpr float AKU_OLCEK = (100.0f + 18.0f) / 18.0f;   // 6,56
constexpr float AKU_YOK_V = 1.0f;              // bunun altı = ölçüm yok (ana anahtar kapalı / bölücü takılı değil)
// Not (errata GPIO-3.11): ADC GPIO36'yı okurken GPIO39'u (sonar sağ echo) ~80 ns LOW'a çeker.
// Sonar sürücüsü yazılınca bu darbe süzülmeli (kapsam dışı, bkz. OKU_BENI.md).
// --------------------------------------------------------------------------------------

enum class Durum : uint8_t { birakik, onsarj, devrede, ariza };

const char* const DURUM_ADLARI[] = {"birakik", "onsarj", "devrede", "ariza"};

// Sıçrama süzgeçli giriş. "kararli" = kabul edilmiş seviye (true = HIGH).
struct SuzulmusGiris {
  uint8_t pin;
  bool kararli;
  uint8_t farkli_sayisi;     // kararlıdan farklı art arda okuma sayısı
};

SuzulmusGiris acil = {PIN_ACIL_STOP_DURUM, true, 0};   // açılışta "basılı" varsay: önce okunmalı
SuzulmusGiris bara = {PIN_BARA_DURUM, true, 0};        // HIGH = bara yok

Durum durum = Durum::birakik;
const char* ariza_nedeni = nullptr;

// GPIO4'e en son HIGH mı yazıldı? (Pinden geri okumak yerine yazılımda tutulur: neyi istediğimizi
// bilmek istiyoruz, pinin o anki elektriksel seviyesini değil.)
bool k1_cekili = false;
uint8_t onsarj_adimi = 0;        // 0: K2 çekili, bara bekleniyor | 1: K1 de çekili, K2 bırakılacak
uint32_t adim_baslangic_ms = 0;

esp_timer_handle_t k2_zamanlayici = nullptr;
volatile bool k2_zorla_dustu = false;   // esp_timer görevi yazar, loop() okur

uint32_t son_giris_ms = 0;
uint32_t son_is_ms = 0;
uint32_t son_i2c_ms = 0;
uint32_t son_aku_ms = 0;
uint32_t son_komut_ms = 0;
uint8_t is_sol_sayac = 0, is_sag_sayac = 0;
uint8_t i2c_hata_sayac = 0;
float aku_v = NAN;

// Bekleyen olay ({"k":"guc",...}); guc_olay_gonder() yollar.
bool olay_bekliyor = false;
uint32_t olay_ms = 0;

// --- K2 (ön şarj) ---

// esp_timer görevinde çalışır (ana döngüden ayrı görev, ayrı çekirdek). Kısa: yalnız pini düşürür.
// gpio_set_level tek bir yazmaç yazımıdır; loop()'un digitalWrite'ıyla çakışması sorun değil.
void k2_zaman_doldu(void*) {
  gpio_set_level((gpio_num_t)PIN_ROLE_K2_ONSARJ, 0);
  k2_zorla_dustu = true;
}

// Önce zamanlayıcı kurulur, ANCAK kurulabildiyse K2 çekilir: süre sınırı olmadan 19 hiç HIGH olmaz.
bool k2_cek() {
  if (k2_zamanlayici == nullptr) return false;
  esp_timer_stop(k2_zamanlayici);                 // çalışmıyorsa ESP_ERR_INVALID_STATE döner; sorun değil
  k2_zorla_dustu = false;
  if (esp_timer_start_once(k2_zamanlayici, (uint64_t)ARM_K2_EN_COK_MS * 1000ULL) != ESP_OK) return false;
  digitalWrite(PIN_ROLE_K2_ONSARJ, HIGH);
  return true;
}

void k2_birak() {
  digitalWrite(PIN_ROLE_K2_ONSARJ, LOW);
  if (k2_zamanlayici != nullptr) esp_timer_stop(k2_zamanlayici);
}

// --- durum ---

void durum_degistir(Durum yeni, const char* neden, uint32_t simdi_ms) {
  durum = yeni;
  ariza_nedeni = (yeni == Durum::ariza) ? neden : nullptr;
  olay_bekliyor = true;
  olay_ms = simdi_ms;
}

// Bırakma: rapor Y5 sırasıyla, aynı turda. Önce motor kilidi (EN), sonra PWM, sonra röleler.
void cikislari_kapat() {
  digitalWrite(PIN_BTS_EN, LOW);
  motorlar_ani_dur();                             // dört PWM hemen 0, rampa sıfır
  digitalWrite(PIN_ROLE_K1, LOW);
  k1_cekili = false;
  k2_birak();
}

// Koruma bıraktı: çıkışlar kapanır, durum "ariza" + neden, olay hemen gider.
void arizaya_gec(const char* neden, uint32_t simdi_ms) {
  cikislari_kapat();
  durum_degistir(Durum::ariza, neden, simdi_ms);
  guc_olay_gonder();
}

void giris_suz(SuzulmusGiris& g) {
  const bool okunan = digitalRead(g.pin) == HIGH;
  if (okunan == g.kararli) {
    g.farkli_sayisi = 0;
  } else if (++g.farkli_sayisi >= GIRIS_ARDISIK) {
    g.kararli = okunan;
    g.farkli_sayisi = 0;
  }
}

// Ön şarj sırası (rapor Y4; süreler kod/ortak/pinler.json "arm" -> pinler.h ARM_*_MS).
void onsarj_yurut(uint32_t simdi_ms) {
  if (k2_zorla_dustu) return arizaya_gec("onsarj_sure", simdi_ms);   // döngü takılmış olmalı
  const uint32_t gecen = simdi_ms - adim_baslangic_ms;
  if (onsarj_adimi == 0) {
    if (gecen < ARM_ONSARJ_BEKLEME_MS) return;
    if (!guc_bara_gerilimli()) return arizaya_gec("bara_yok", simdi_ms);   // ön şarj barayı dolduramadı
    digitalWrite(PIN_ROLE_K1, HIGH);               // K1 çeker; K2 bir süre daha paralel kalır
    k1_cekili = true;
    onsarj_adimi = 1;
    adim_baslangic_ms = simdi_ms;
    return;
  }
  if (gecen < ARM_K1_SONRASI_MS) return;
  k2_birak();
  if (!guc_bara_gerilimli()) return arizaya_gec("bara_gitti", simdi_ms);
  // Devrede. EN yalnız burada ve yalnız K1 çekili + bara gerilimliyken HIGH olur (rapor Y6).
  son_komut_ms = simdi_ms;                         // sessizlik sayacı devreye girişten başlar
  is_sol_sayac = is_sag_sayac = 0;
  i2c_hata_sayac = 0;
  son_i2c_ms = son_is_ms = simdi_ms;
  digitalWrite(PIN_BTS_EN, HIGH);
  durum_degistir(Durum::devrede, nullptr, simdi_ms);
  guc_olay_gonder();
}

// Devredeyken korumalar. Biri tutarsa aynı turda bırakılır.
void devrede_denetle(uint32_t simdi_ms) {
  if (simdi_ms - son_is_ms >= IS_ORNEK_MS) {
    son_is_ms = simdi_ms;
    is_sol_sayac = (analogRead(PIN_SOL_IS) >= IS_ARIZA_HAM) ? is_sol_sayac + 1 : 0;
    is_sag_sayac = (analogRead(PIN_SAG_IS) >= IS_ARIZA_HAM) ? is_sag_sayac + 1 : 0;
    if (is_sol_sayac >= IS_ARDISIK) return arizaya_gec("is_sol", simdi_ms);
    if (is_sag_sayac >= IS_ARDISIK) return arizaya_gec("is_sag", simdi_ms);
  }
  if (simdi_ms - son_i2c_ms >= I2C_YOKLAMA_MS) {
    son_i2c_ms = simdi_ms;
    // Cevap yoksa Wire en çok 20 ms bekler (servolar.cpp setTimeOut); en kötü 3 x 20 ms.
    i2c_hata_sayac = servolar_yokla() ? 0 : i2c_hata_sayac + 1;
    if (i2c_hata_sayac >= I2C_ARDISIK_HATA) return arizaya_gec("i2c", simdi_ms);
  }
#if SESSIZLIK_BIRAK_MS > 0
  if (simdi_ms - son_komut_ms >= (uint32_t)SESSIZLIK_BIRAK_MS) return arizaya_gec("sessizlik", simdi_ms);
#endif
}

void aku_olc(uint32_t simdi_ms) {
  if (simdi_ms - son_aku_ms < AKU_ORNEK_MS) return;
  son_aku_ms = simdi_ms;
  const float volt = analogReadMilliVolts(PIN_AKU_ADC) / 1000.0f * AKU_OLCEK;
  aku_v = (volt >= AKU_YOK_V) ? volt : NAN;
}

}  // namespace

void guc_pinleri_guvenle() {
  // Arduino-ESP32 2.0.17 sırası: ÖNCE çıkış seviyesi LOW, SONRA pin çıkış. Böylece pin çıkışa döndüğü
  // anda zaten LOW'dur, kısa bir HIGH darbesi olmaz. (3.x'te sıra farklı; rapor Y2, çekirdek sabit: Y13.)
  // Sürüş gücü (gpio_set_drive_capability) DEĞİŞTİRİLMEZ: varsayılan BC337 tabanına yeter (rapor D9).
  const uint8_t pinler[] = {PIN_ROLE_K1, PIN_ROLE_K2_ONSARJ, PIN_BTS_EN};
  for (uint8_t p : pinler) {
    digitalWrite(p, LOW);
    pinMode(p, OUTPUT);
  }
  // GPIO12 BİLEREK hiç ayarlanmaz (strapping, boş). Serial1 / Serial2 / SPI hiç açılmaz (rapor Y1, Y11).
}

void guc_baslat() {
  // Girişler: PC817 çıkışları, pull-up yalnız 3,3 V'a (dahili + varsa dış 10k). Kesme yok: yoklama.
  pinMode(PIN_ACIL_STOP_DURUM, INPUT_PULLUP);
  pinMode(PIN_BARA_DURUM, INPUT_PULLUP);
  acil.kararli = digitalRead(PIN_ACIL_STOP_DURUM) == HIGH;
  bara.kararli = digitalRead(PIN_BARA_DURUM) == HIGH;

  // ADC1 (Wi-Fi açıkken de çalışır). 32/33/36 için pull komutu verilmez (analogRead pini ANALOG yapar).
  analogSetPinAttenuation(PIN_SOL_IS, ADC_0db);
  analogSetPinAttenuation(PIN_SAG_IS, ADC_0db);
  analogSetPinAttenuation(PIN_AKU_ADC, ADC_11db);

  // K2 süre sınırı: tek atımlık, ESP_TIMER_TASK (esp_timer görevi; ana döngüden bağımsız).
  esp_timer_create_args_t ayar = {};
  ayar.callback = &k2_zaman_doldu;
  ayar.arg = nullptr;
  ayar.dispatch_method = ESP_TIMER_TASK;
  ayar.name = "k2_sure";
  if (esp_timer_create(&ayar, &k2_zamanlayici) != ESP_OK) k2_zamanlayici = nullptr;   // arm reddedilir

  const uint32_t simdi = millis();
  son_giris_ms = son_aku_ms = son_komut_ms = simdi;
  durum = Durum::birakik;                          // açılışta ASLA kendiliğinden arm olmaz
}

void guc_guncelle(uint32_t simdi_ms) {
  if (simdi_ms - son_giris_ms >= GIRIS_ORNEK_MS) {
    son_giris_ms = simdi_ms;
    giris_suz(acil);
    giris_suz(bara);
  }
  aku_olc(simdi_ms);

  if (durum != Durum::onsarj && durum != Durum::devrede) return;   // röleler zaten bırakık

  // Her iki durumda geçerli korumalar (rapor Y5).
  if (guc_acil_basili()) return arizaya_gec("acil_stop", simdi_ms);
  if (k1_cekili && !guc_bara_gerilimli()) return arizaya_gec("bara_gitti", simdi_ms);

  if (durum == Durum::onsarj) onsarj_yurut(simdi_ms);
  else devrede_denetle(simdi_ms);
}

const char* guc_arm(uint32_t simdi_ms) {
  if (durum == Durum::devrede) return "zaten_devrede";
  if (durum == Durum::onsarj) return "mesgul";
  if (guc_acil_basili()) return "acil_stop";
  if (!servolar_hazir() || !servolar_yokla()) return "pca9685_yok";
  // Ön koşul: EN=0 ve PWM=0 (rapor Y4). Bırakık durumda zaten öyle; yine de zorla.
  digitalWrite(PIN_BTS_EN, LOW);
  motorlar_ani_dur();
  if (!k2_cek()) return "zamanlayici_yok";        // süre sınırı kurulamadıysa K2 hiç çekilmez
  onsarj_adimi = 0;
  adim_baslangic_ms = simdi_ms;
  durum_degistir(Durum::onsarj, nullptr, simdi_ms);   // arıza (varsa) burada temizlenir
  return nullptr;
}

void guc_birak(uint32_t simdi_ms) {
  cikislari_kapat();
  if (durum == Durum::onsarj || durum == Durum::devrede) durum_degistir(Durum::birakik, nullptr, simdi_ms);
  // birakik ve ariza: durum aynı kalır (arıza kilidi yalnız arm ile çözülür).
}

void guc_komut_geldi(uint32_t simdi_ms) { son_komut_ms = simdi_ms; }

void guc_olay_gonder() {
  if (!olay_bekliyor) return;
  olay_bekliyor = false;
  seri_guc_olayi_gonder(guc_durum_adi(), ariza_nedeni, olay_ms);
}

bool guc_devrede() { return durum == Durum::devrede; }
bool guc_ariza_mi() { return durum == Durum::ariza; }
const char* guc_durum_adi() { return DURUM_ADLARI[(uint8_t)durum]; }
const char* guc_ariza_nedeni() { return ariza_nedeni; }
bool guc_acil_basili() { return acil.kararli; }          // HIGH = basılı / F5 attı
bool guc_bara_gerilimli() { return !bara.kararli; }      // LOW = gerilimli
float guc_aku_volt() { return aku_v; }
