// motorlar.cpp -- bkz. motorlar.h
//
// GÜÇ: BTS7960'ın B+/B- girişi doğrudan akü hattından (12 V, sigortalı, acil stop SONRASI).
// Mantık tarafı (VCC) ESP32'nin 3,3 V'u ya da 5 V; BTS7960 3,3 V girişi kabul eder. Toprak ortak.
// Acil stop (Emas) motor güç hattını keser; bu kod çökse de motor durur.
#include "motorlar.h"

#include <Arduino.h>

#include "pinler.h"

namespace {

// ---------------- AYARLAR (hepsi TAHMİNİ; robot üstünde ölçülüp düzeltilecek) ----------------
constexpr float DT = 0.020f;                  // motorlar_guncelle() aralığı, saniye (50 Hz)
constexpr float TEKER_CAPI_M = 0.125f;        // 125 x 58 arazi tekerleği
constexpr float IZ_GENISLIGI_M = 0.426f;      // sol ve sağ teker merkezleri arası (CAD: 2 x 213 mm); ÖLÇ
constexpr float TEKER_AZAMI_HIZ = 0.39f;      // %100 PWM'de teker hızı (60 dev/dk JGB37 + 125 mm). ÖLÇ
constexpr float HIZLANMA = 0.5f;              // m/s^2; uzun robot devrilmesin diye yumuşak. Artırma!
constexpr float GIRIS_SINIRI = 1.0f;          // v ve w bu değere kırpılır (protokol: -1..1)

// Enkoder: tekerleğin BİR turunda kaç tik sayılır? JGB37-520 Hall enkoderi motor milinde 11 darbe
// verir; A kanalının iki kenarını saydığımız için 22 x dişli oranı. Oran motora göre değişir
// (60 dev/dk modelde ~1:90 tahmini). ÖLÇ: tekerleği elle 10 tur çevir, tik farkını 10'a böl.
constexpr float TIK_PER_TUR = 22.0f * 90.0f;
constexpr bool ENKODER_VAR = true;            // enkoder bağlı değilse false: saf açık çevrim

// PID katsayıları: SIFIR = kapalı, yalnız ileri besleme. Robot üstünde (tekerlek havada başla!)
// önce KP'yi küçük artır, salınım başlayınca yarıya indir; sonra KI ile kalıcı hatayı kapat.
constexpr float KP = 0.0f;
constexpr float KI = 0.0f;
constexpr float KD = 0.0f;
constexpr float INTEGRAL_SINIRI = 0.3f;       // integralin PWM'e katkısı en çok bu kadar olsun

// Montaj yönü: bir teker "ileri" komutta geri dönüyorsa onun MOTOR_TERS'ini true yap.
// Enkoder ileri dönüşte eksi sayıyorsa ENKODER_TERS'i true yap. (Sağ motor aynalı takılır.)
constexpr bool SOL_MOTOR_TERS = false;
constexpr bool SAG_MOTOR_TERS = true;
constexpr bool SOL_ENKODER_TERS = false;
constexpr bool SAG_ENKODER_TERS = true;

// PWM: BTS7960 25 kHz'e kadar çıkar; 20 kHz duyulmaz (vınlama yok). 10 bit = 0..1023.
constexpr uint32_t PWM_FREKANS = 20000;
constexpr uint8_t PWM_BIT = 10;
constexpr uint32_t PWM_TAM = (1u << PWM_BIT) - 1;
// LEDC kanalları (Arduino-ESP32 2.x): her PWM pini kendi kanalında.
constexpr uint8_t LEDC_SOL_R = 0, LEDC_SOL_L = 1, LEDC_SAG_R = 2, LEDC_SAG_L = 3;
// ---------------------------------------------------------------------------------------------

// Enkoder sayaçları kesmede artar. 32 bit hizalı okuma ESP32'de bölünmez (atomik), ve yalnız
// kesme yazdığı için ana döngüde kilit gerekmez. "volatile": derleyici değeri önbelleğe almasın.
volatile int32_t sol_tik = 0;
volatile int32_t sag_tik = 0;

struct Teker {
  uint8_t pin_r, pin_l, pin_en;
  uint8_t ledc_r, ledc_l;
  bool motor_ters, enkoder_ters;
  volatile int32_t* sayac;  // bu tekerin enkoder sayacı
  float hedef_hiz;        // m/s, "sur"dan gelen
  float rampa_hiz;        // m/s, hızlanma sınırıyla hedefe yaklaşan değer
  float integral;
  float onceki_hata;
  int32_t onceki_tik;
};

Teker sol = {PIN_SOL_RPWM, PIN_SOL_LPWM, PIN_SOL_EN, LEDC_SOL_R, LEDC_SOL_L,
             SOL_MOTOR_TERS, SOL_ENKODER_TERS, &sol_tik, 0, 0, 0, 0, 0};
Teker sag = {PIN_SAG_RPWM, PIN_SAG_LPWM, PIN_SAG_EN, LEDC_SAG_R, LEDC_SAG_L,
             SAG_MOTOR_TERS, SAG_ENKODER_TERS, &sag_tik, 0, 0, 0, 0, 0};

float son_v = 0.0f, son_w = 0.0f;

// Kesme: A kanalı her değiştiğinde çalışır. A ile B aynıysa bir yön, farklıysa öbür yön.
// Kesme kısa olmalı: yalnız say, hesap yapma. IRAM_ATTR: kod hızlı RAM'de dursun.
void IRAM_ATTR sol_enkoder_kesme() {
  if (digitalRead(PIN_SOL_ENK_A) == digitalRead(PIN_SOL_ENK_B)) sol_tik++; else sol_tik--;
}
void IRAM_ATTR sag_enkoder_kesme() {
  if (digitalRead(PIN_SAG_ENK_A) == digitalRead(PIN_SAG_ENK_B)) sag_tik++; else sag_tik--;
}

float kirp(float x, float sinir) {
  if (x > sinir) return sinir;
  if (x < -sinir) return -sinir;
  return x;
}

// Arduino-ESP32 2.x ve 3.x'te LEDC işlevleri farklı; ikisini de destekle.
void pwm_kur(uint8_t pin, uint8_t ledc) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)ledc;
  ledcAttach(pin, PWM_FREKANS, PWM_BIT);
#else
  ledcSetup(ledc, PWM_FREKANS, PWM_BIT);
  ledcAttachPin(pin, ledc);
#endif
}

void pwm_yaz(uint8_t pin, uint8_t ledc, uint32_t deger) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)ledc;
  ledcWrite(pin, deger);
#else
  (void)pin;
  ledcWrite(ledc, deger);
#endif
}

// cikis -1..1: + ileri (RPWM), - geri (LPWM). 0 iken iki PWM de 0 = BTS7960'ta fren (iki alt
// transistör iletimde). EN pini HIGH kalır.
void teker_yaz(const Teker& t, float cikis) {
  if (t.motor_ters) cikis = -cikis;
  cikis = kirp(cikis, 1.0f);
  uint32_t deger = (uint32_t)(fabsf(cikis) * PWM_TAM + 0.5f);
  if (cikis >= 0.0f) {
    pwm_yaz(t.pin_l, t.ledc_l, 0);              // önce karşı yönü kapat
    pwm_yaz(t.pin_r, t.ledc_r, deger);
  } else {
    pwm_yaz(t.pin_r, t.ledc_r, 0);
    pwm_yaz(t.pin_l, t.ledc_l, deger);
  }
}

void teker_kur(Teker& t) {
  pinMode(t.pin_en, OUTPUT);
  digitalWrite(t.pin_en, LOW);                  // kurulum bitene kadar sürücü kapalı
  pwm_kur(t.pin_r, t.ledc_r);
  pwm_kur(t.pin_l, t.ledc_l);
  teker_yaz(t, 0.0f);
}

void teker_sifirla(Teker& t) {
  t.hedef_hiz = t.rampa_hiz = 0.0f;
  t.integral = t.onceki_hata = 0.0f;
  teker_yaz(t, 0.0f);
}

int32_t tik_oku(const Teker& t) {
  int32_t ham = *t.sayac;
  return t.enkoder_ters ? -ham : ham;
}

// Bir teker için bir kontrol adımı (rampa + ileri besleme + PID).
void teker_adim(Teker& t) {
  // 1) Rampa: hız her adımda en çok HIZLANMA*DT değişir.
  float adim = HIZLANMA * DT;
  t.rampa_hiz += kirp(t.hedef_hiz - t.rampa_hiz, adim);

  // 2) Ölçülen hız (enkoderden).
  int32_t tik = tik_oku(t);
  int32_t fark = tik - t.onceki_tik;
  t.onceki_tik = tik;
  float olculen = (fark / TIK_PER_TUR) * (PI * TEKER_CAPI_M) / DT;

  // 3) İleri besleme: "bu hız için kabaca şu kadar PWM gerekir".
  float cikis = t.rampa_hiz / TEKER_AZAMI_HIZ;

  // 4) PID düzeltmesi (katsayılar sıfırken etkisiz).
  if (ENKODER_VAR && t.rampa_hiz != 0.0f) {
    float hata = t.rampa_hiz - olculen;
    t.integral = kirp(t.integral + hata * DT, (KI > 0.0f) ? INTEGRAL_SINIRI / KI : 0.0f);
    float turev = (hata - t.onceki_hata) / DT;
    t.onceki_hata = hata;
    cikis += KP * hata + KI * t.integral + KD * turev;
  } else {
    t.integral = t.onceki_hata = 0.0f;          // dururken integral birikmesin
  }
  if (t.rampa_hiz == 0.0f) cikis = 0.0f;        // hedef sıfırsa motor tam dursun (vınlamasın)
  teker_yaz(t, cikis);
}

}  // namespace

void motorlar_baslat() {
  teker_kur(sol);
  teker_kur(sag);

  // Enkoderler: dahili pull-up açık (JGB37 enkoder çıkışı açık kollektör olabilir).
  pinMode(PIN_SOL_ENK_A, INPUT_PULLUP);
  pinMode(PIN_SOL_ENK_B, INPUT_PULLUP);
  pinMode(PIN_SAG_ENK_A, INPUT_PULLUP);
  pinMode(PIN_SAG_ENK_B, INPUT_PULLUP);
  if (ENKODER_VAR) {
    attachInterrupt(digitalPinToInterrupt(PIN_SOL_ENK_A), sol_enkoder_kesme, CHANGE);
    attachInterrupt(digitalPinToInterrupt(PIN_SAG_ENK_A), sag_enkoder_kesme, CHANGE);
  }
  sol.onceki_tik = tik_oku(sol);
  sag.onceki_tik = tik_oku(sag);

  digitalWrite(sol.pin_en, HIGH);               // PWM sıfırken sürücüleri etkinleştir
  digitalWrite(sag.pin_en, HIGH);
}

void motorlar_hedef(float v, float w) {
  v = kirp(v, GIRIS_SINIRI);
  w = kirp(w, GIRIS_SINIRI);
  son_v = v;
  son_w = w;
  // Diferansiyel sürüş: dönüşte bir teker hızlanır, öbürü yavaşlar.
  float v_sol = v - w * IZ_GENISLIGI_M / 2.0f;
  float v_sag = v + w * IZ_GENISLIGI_M / 2.0f;
  // Bir teker azami hızı aşıyorsa İKİSİNİ birlikte küçült (dönüş yarıçapı bozulmasın).
  float en_buyuk = fmaxf(fabsf(v_sol), fabsf(v_sag));
  if (en_buyuk > TEKER_AZAMI_HIZ) {
    float olcek = TEKER_AZAMI_HIZ / en_buyuk;
    v_sol *= olcek;
    v_sag *= olcek;
  }
  sol.hedef_hiz = v_sol;
  sag.hedef_hiz = v_sag;
}

void motorlar_dur() {
  son_v = son_w = 0.0f;
  teker_sifirla(sol);
  teker_sifirla(sag);
}

void motorlar_guncelle(uint32_t simdi_ms) {
  (void)simdi_ms;
  teker_adim(sol);
  teker_adim(sag);
}

float motorlar_hedef_v() { return son_v; }
float motorlar_hedef_w() { return son_w; }
int32_t motor_sol_tik() { return tik_oku(sol); }
int32_t motor_sag_tik() { return tik_oku(sag); }
