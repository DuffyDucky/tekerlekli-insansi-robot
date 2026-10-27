// seri_protokol.cpp -- bkz. seri_protokol.h
#include "seri_protokol.h"

#include <Arduino.h>
#include <ArduinoJson.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "imu.h"
#include "jestler.h"
#include "motorlar.h"
#include "servolar.h"
#include "watchdog.h"

#define FIRMWARE_SURUM "0.2.0"   // 0.2.0: odo yayını, odo_sifirla, jest "yon"

namespace {

constexpr uint32_t SERI_HIZ = 115200;
constexpr size_t SATIR_UZUNLUGU = 200;   // bir komut satırı en çok bu kadar bayt (fazlası atılır)

char satir[SATIR_UZUNLUGU + 1];          // sabit tampon: çalışma sırasında bellek ayırma yok
// Not: JsonDocument (ArduinoJson 7) her komutta kısa ömürlü küçük bir bellek ayırır ve fonksiyon
// bitince geri verir. Satır 200 baytla sınırlı olduğu için bu miktar da sınırlı (~birkaç yüz bayt).
size_t satir_boy = 0;
bool satir_tasti = false;                // tampon doldu: satır sonuna kadar gelenleri at

// Bir JSON belgesini tek satır olarak gönderir ("\n" ile biter; Pi readline() ile okur).
void gonder(const JsonDocument& belge) {
  serializeJson(belge, Serial);
  Serial.write('\n');
}

void cevap_ok(const char* k) {
  JsonDocument c;
  c["ok"] = true;
  c["k"] = k;
  gonder(c);
}

void cevap_hata(const char* k, const char* hata) {
  JsonDocument c;
  c["ok"] = false;
  if (k != nullptr) c["k"] = k;
  c["hata"] = hata;
  gonder(c);
}

// Sayı mı ve sonlu mu? (JSON'da tam sayı da gelebilir: "v":0 -> is<float>() true döner)
bool sayi_al(JsonVariantConst deger, float& sonuc) {
  if (!deger.is<float>()) return false;
  sonuc = deger.as<float>();
  return isfinite(sonuc);
}

// --------------------------- komutlar ---------------------------

// "yon" alanı isteğe bağlı. Geçerli değerler; başka her şey (sayı dahil) yon_gecersiz.
bool yon_gecerli(const char* yon) {
  static const char* const YONLER[] = {"sol", "sag", "ileri", "arka"};
  for (const char* y : YONLER) {
    if (strcmp(yon, y) == 0) return true;
  }
  return false;
}

void komut_jest(JsonDocument& d, uint32_t simdi_ms) {
  const char* ad = d["ad"];
  if (ad == nullptr) return cevap_hata("jest", "ad_yok");
  const char* yon = nullptr;                       // nullptr = yön verilmedi
  JsonVariantConst yon_alani = d["yon"];
  if (!yon_alani.isNull()) {
    if (!yon_alani.is<const char*>()) return cevap_hata("jest", "yon_gecersiz");
    yon = yon_alani.as<const char*>();
    if (!yon_gecerli(yon)) return cevap_hata("jest", "yon_gecersiz");
  }
  if (!servolar_hazir()) return cevap_hata("jest", "pca9685_yok");
  // TODO(yön): jest_baslat'a yon iletilecek (bkz. jestler.h "YÖN AYRIMI"). Şimdilik yön yalnız
  //            doğrulanıp cevaba yazılır; jest her zaman kayıtlı haliyle (isaret = sağ kol) oynar.
  if (!jest_baslat(ad, simdi_ms)) return cevap_hata("jest", "bilinmeyen_jest");
  JsonDocument c;
  c["ok"] = true;
  c["k"] = "jest";
  c["ad"] = ad;
  if (yon != nullptr) c["yon"] = yon;
  gonder(c);
}

void komut_sur(JsonDocument& d, uint32_t simdi_ms) {
  float v, w;
  if (!sayi_al(d["v"], v) || !sayi_al(d["w"], w)) return cevap_hata("sur", "v_w_sayi_olmali");
  motorlar_hedef(v, w);
  watchdog_besle(simdi_ms);
  cevap_ok("sur");
}

// Enkoder tik sayaçlarını sıfırlar. Motorlara ve bekçiye dokunmaz.
void komut_odo_sifirla() {
  motor_tik_sifirla();
  cevap_ok("odo_sifirla");
}

void komut_dur() {
  motorlar_dur();          // rampa yok, anında
  jest_durdur();           // kollar olduğu yerde kalır
  cevap_ok("dur");
}

void komut_servo(JsonDocument& d) {
  int sira = -1;
  JsonVariantConst kanal = d["kanal"];
  if (kanal.is<int>()) {
    sira = servo_sira_kanaldan(kanal.as<int>());
  } else if (kanal.is<const char*>()) {
    sira = servo_sira_addan(kanal.as<const char*>());
  } else {
    return cevap_hata("servo", "kanal_yok");
  }
  if (sira < 0) return cevap_hata("servo", "bilinmeyen_kanal");
  float aci;
  if (!sayi_al(d["aci"], aci)) return cevap_hata("servo", "aci_sayi_olmali");
  if (!servolar_hazir()) return cevap_hata("servo", "pca9685_yok");

  jest_durdur();                                   // elle komut jesti keser
  float uygulanan = servo_hedef_ayarla((uint8_t)sira, aci);
  JsonDocument c;
  c["ok"] = true;
  c["k"] = "servo";
  c["kanal"] = servo_adi((uint8_t)sira);
  c["aci"] = uygulanan;                            // sınıra kırpıldıysa farklı olabilir
  gonder(c);
}

void komut_ping(uint32_t simdi_ms) {
  JsonDocument c;
  c["ok"] = true;
  c["k"] = "ping";
  c["surum"] = FIRMWARE_SURUM;
  c["ms"] = simdi_ms;
  c["pca9685"] = servolar_hazir();
  c["odo"] = (ODO_YAYINI != 0);                    // true: bu firmware {"k":"odo",...} yayını yapıyor
  JsonArray jestler = c["jestler"].to<JsonArray>();
  for (uint8_t i = 0; i < jest_sayisi(); i++) jestler.add(jest_adi(i));
  gonder(c);
}

void satiri_isle(uint32_t simdi_ms) {
  if (satir_boy == 0) return;                      // boş satır: sessizce geç
  JsonDocument d;
  DeserializationError hata = deserializeJson(d, satir, satir_boy);
  if (hata) return cevap_hata(nullptr, "json_bozuk");
  const char* k = d["k"];
  if (k == nullptr) return cevap_hata(nullptr, "k_yok");

  if (strcmp(k, "sur") == 0)        komut_sur(d, simdi_ms);
  else if (strcmp(k, "dur") == 0)   komut_dur();
  else if (strcmp(k, "jest") == 0)  komut_jest(d, simdi_ms);
  else if (strcmp(k, "servo") == 0) komut_servo(d);
  else if (strcmp(k, "ping") == 0)  komut_ping(simdi_ms);
  else if (strcmp(k, "odo_sifirla") == 0) komut_odo_sifirla();
  else                              cevap_hata(k, "bilinmeyen_komut");
}

}  // namespace

void seri_baslat() {
  Serial.begin(SERI_HIZ);
  JsonDocument c;
  c["k"] = "hazir";
  c["surum"] = FIRMWARE_SURUM;
  c["pca9685"] = servolar_hazir();
  gonder(c);
}

void seri_isle(uint32_t simdi_ms) {
  // Bir döngüde en çok 256 bayt oku: sürekli veri gelse de motor/servo güncellemesi aksamasın.
  for (int sayac = 0; sayac < 256 && Serial.available() > 0; sayac++) {
    int bayt = Serial.read();
    if (bayt < 0) break;
    if (bayt == '\r') continue;                    // Windows satır sonu (\r\n) gelirse
    if (bayt == '\n') {
      if (satir_tasti) {
        cevap_hata(nullptr, "satir_cok_uzun");
      } else {
        satir[satir_boy] = '\0';
        satiri_isle(simdi_ms);
      }
      satir_boy = 0;
      satir_tasti = false;
      continue;
    }
    if (satir_boy < SATIR_UZUNLUGU) {
      satir[satir_boy++] = (char)bayt;
    } else {
      satir_tasti = true;
    }
  }
}

void seri_durum_gonder() {
  JsonDocument c;
  c["k"] = "durum";
  c["jest"] = jest_aktif_adi();
  JsonArray sur = c["sur"].to<JsonArray>();
  sur.add(motorlar_hedef_v());
  sur.add(motorlar_hedef_w());
  c["wd"] = watchdog_tetikli();
  gonder(c);
}

void seri_odo_gonder(uint32_t simdi_ms) {
  // Örnek: {"k":"odo","sol":1234,"sag":-56,"yaw":null,"ms":104200}  (en uzun hali ~86 bayt)
  static char tampon[112];
  char yaw_metni[16];
  float yaw = imu_var() ? imu_yaw_derece() : NAN;
  if (isfinite(yaw) && fabsf(yaw) < 1.0e6f) {      // saçma büyük değer tamponu taşırmasın
    snprintf(yaw_metni, sizeof(yaw_metni), "%.2f", yaw);
  } else {
    snprintf(yaw_metni, sizeof(yaw_metni), "null");
  }
  int boy = snprintf(tampon, sizeof(tampon),
                     "{\"k\":\"odo\",\"sol\":%ld,\"sag\":%ld,\"yaw\":%s,\"ms\":%lu}\n",
                     (long)motor_sol_tik(), (long)motor_sag_tik(), yaw_metni,
                     (unsigned long)simdi_ms);
  if (boy > 0 && (size_t)boy < sizeof(tampon)) Serial.write((const uint8_t*)tampon, (size_t)boy);
}
