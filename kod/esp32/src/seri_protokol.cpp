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

#define FIRMWARE_SURUM "0.4.0"   // 0.2.0: odo yayını, odo_sifirla, jest "yon"
                                 // 0.3.0: jest "yon" uygulanır, cevapta "yon_uygulandi"
                                 // 0.4.0: 10 servo, ivme/fren sınırı ayrı, rampa kipi ("rampa" komutu)

namespace {

constexpr uint32_t SERI_HIZ = 115200;
constexpr size_t SATIR_UZUNLUGU = 200;   // bir komut satırı en çok bu kadar bayt (fazlası atılır)

char satir[SATIR_UZUNLUGU + 1];          // sabit tampon: çalışma sırasında bellek ayırma yok
// Not: JsonDocument (ArduinoJson 7) her komutta kısa ömürlü küçük bir bellek ayırır ve fonksiyon
// bitince geri verir. Satır 200 baytla sınırlı olduğu için bu miktar da sınırlı (~birkaç yüz bayt).
size_t satir_boy = 0;
bool satir_tasti = false;                // tampon doldu: satır sonuna kadar gelenleri at

bool rampa_elle = false;                 // Pi istedi ("rampa" komutu ya da sur.rampa)
bool rampa_imu = false;                  // main.cpp IMU eğim histerezisi

// Etkin rampa kipini motorlara uygular; kapalıdan açığa geçişte kolları ev pozuna alır.
void rampa_uygula() {
  const bool yeni = rampa_elle || rampa_imu;
  const bool eski = motorlar_rampa_modu_mu();
  motorlar_rampa_modu(yeni);
  if (yeni && !eski) {
    jest_durdur();                       // oynayan jest kesilir
    servolar_bostaya();                  // BOSTA_DURUS = ev pozu (servo hız sınırıyla gider)
  }
}

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

void komut_jest(JsonDocument& d, uint32_t simdi_ms) {
  const char* ad = d["ad"];
  if (ad == nullptr) return cevap_hata("jest", "ad_yok");
  // Rampa kipinde kollar ev pozunda kalır: yalnız "bosta" (= ev pozu) oynatılabilir.
  if (rampa_kipi_acik() && strcmp(ad, "bosta") != 0) return cevap_hata("jest", "rampa_modunda");
  const char* yon = nullptr;                       // nullptr = yön verilmedi
  JsonVariantConst yon_alani = d["yon"];
  if (!yon_alani.isNull()) {
    if (!yon_alani.is<const char*>()) return cevap_hata("jest", "yon_gecersiz");
    yon = yon_alani.as<const char*>();
    if (jest_yon_indeksi(yon) < 0) return cevap_hata("jest", "yon_gecersiz");   // sol|sag|ileri|arka
  }
  if (!servolar_hazir()) return cevap_hata("jest", "pca9685_yok");
  bool yon_uygulandi = false;      // jestin bu yön için varyantı yoksa varsayılan oynar -> false
  if (!jest_baslat(ad, yon, simdi_ms, &yon_uygulandi)) return cevap_hata("jest", "bilinmeyen_jest");
  JsonDocument c;
  c["ok"] = true;
  c["k"] = "jest";
  c["ad"] = ad;
  if (yon != nullptr) {
    c["yon"] = yon;
    c["yon_uygulandi"] = yon_uygulandi;
  }
  gonder(c);
}

void komut_sur(JsonDocument& d, uint32_t simdi_ms) {
  float v, w;
  if (!sayi_al(d["v"], v) || !sayi_al(d["w"], w)) return cevap_hata("sur", "v_w_sayi_olmali");
  JsonVariantConst rampa = d["rampa"];             // isteğe bağlı: elle rampa kipini de ayarlar
  if (!rampa.isNull() && !rampa.is<bool>()) return cevap_hata("sur", "rampa_bool_olmali");
  if (!rampa.isNull()) {
    rampa_elle = rampa.as<bool>();
    rampa_uygula();                                // önce kip: bu hedef yeni sınırla izlenir
  }
  motorlar_hedef(v, w);
  watchdog_besle(simdi_ms);
  if (rampa.isNull()) return cevap_ok("sur");
  JsonDocument c;
  c["ok"] = true;
  c["k"] = "sur";
  c["rampa"] = rampa_kipi_acik();
  gonder(c);
}

// Elle rampa kipi: {"k":"rampa","ac":true|false}. Cevapta etkin kip ("rampa") ve kaynakları.
void komut_rampa(JsonDocument& d) {
  JsonVariantConst ac = d["ac"];
  if (!ac.is<bool>()) return cevap_hata("rampa", "ac_bool_olmali");
  rampa_elle = ac.as<bool>();
  rampa_uygula();
  JsonDocument c;
  c["ok"] = true;
  c["k"] = "rampa";
  c["rampa"] = rampa_kipi_acik();
  c["elle"] = rampa_elle;
  c["imu"] = rampa_imu;
  gonder(c);
}

// Enkoder tik sayaçlarını sıfırlar. Motorlara ve bekçiye dokunmaz.
void komut_odo_sifirla() {
  motor_tik_sifirla();
  cevap_ok("odo_sifirla");
}

void komut_dur() {
  motorlar_dur();          // fren sınırıyla (düz 1,8 / rampa 0,1 m/s^2)
  jest_durdur();           // kollar olduğu yerde kalır
  cevap_ok("dur");
}

void komut_servo(JsonDocument& d) {
  if (rampa_kipi_acik()) return cevap_hata("servo", "rampa_modunda");   // kollar ev pozunda kalır
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
  c["rampa"] = rampa_kipi_acik();
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
  else if (strcmp(k, "rampa") == 0) komut_rampa(d);
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
  c["rampa"] = rampa_kipi_acik();
  gonder(c);
}

void rampa_imu_bildir(bool egimde) {
  if (egimde == rampa_imu) return;
  rampa_imu = egimde;
  rampa_uygula();
}

bool rampa_kipi_acik() { return rampa_elle || rampa_imu; }

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
