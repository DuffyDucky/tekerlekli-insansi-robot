// motorlar.cpp -- bkz. motorlar.h
//
// GÜÇ: BTS7960'ın B+/B- girişi ANAHTARLI BARADAN (K1 rölesinin arkası; pin haritası sürüm 4). Röle
// bırakıkken motor sürücüsünde güç yoktur. Mantık tarafı (VCC) 5 V; IN uçları ESP32'nin 3,3 V PWM'ini
// alır (kart gelince doğrulanacak, rapor T4). Toprak ortak.
// EN (GPIO13, dört uç ortak) bu dosyada DEĞİL, guc.cpp'de: yalnız "devrede" iken HIGH olur.
#include "motorlar.h"

#include <Arduino.h>
#include <driver/pcnt.h>

#include "guc.h"
#include "pinler.h"
#include "sinirlar_verisi.h"   // IVME_DUZ_SURUS, IVME_DUZ_FREN, IVME_RAMPA_SURUS, IVME_RAMPA_FREN (üretilir)

namespace {

// ---------------- AYARLAR (hepsi TAHMİNİ; robot üstünde ölçülüp düzeltilecek) ----------------
constexpr float DT = 0.020f;                  // motorlar_guncelle() aralığı, saniye (50 Hz)
constexpr float TEKER_CAPI_M = 0.125f;        // 125 x 58 arazi tekerleği
constexpr float IZ_GENISLIGI_M = 0.426f;      // sol ve sağ teker merkezleri arası (CAD: 2 x 213 mm); ÖLÇ
constexpr float TEKER_AZAMI_HIZ = 0.39f;      // %100 PWM'de teker hızı (60 dev/dk JGB37 + 125 mm). ÖLÇ
// İvme sınırları burada YAZILMAZ: src/sinirlar_verisi.h (kod/ortak/eklem_sinirlari.json'dan üretilir).
// Devrilme payı analizinden gelir (planlama/kopru-mekanik-yazilim.md F8); artırma, JSON'u Ahmet günceller.
constexpr float GIRIS_SINIRI = 1.0f;          // v ve w bu değere kırpılır (protokol: -1..1)

// Enkoder: tekerleğin BİR turunda kaç tik sayılır? JGB37-520 Hall enkoderi motor milinde 11 darbe
// verir; A kanalının İKİ kenarını saydığımız için 22 x dişli oranı. Oran motora göre değişir
// (60 dev/dk modelde ~1:90 tahmini). ÖLÇ: tekerleği elle 10 tur çevir, tik farkını 10'a böl.
// 0.5.0'da sayım PCNT'ye geçti ama çözünürlük AYNI (A'nın iki kenarı, B yön): değer değişmedi.
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

// PCNT (donanım darbe sayacı; rapor Y8: GPIO kenar kesmesi errata [GPIO-3.14] yüzünden güvenilmez).
// Sayaç 16 bittir ve -PCNT_SINIR..+PCNT_SINIR arasında döner: sınıra varınca kendiliğinden 0'a
// döner. Biz sayacı her okumada önceki okumayla karşılaştırıp farkı 32 bit toplama ekleriz
// ("mod PCNT_SINIR" fark). İki okuma arasında PCNT_SINIR/2'den (15000 tik ~ 7 teker turu) az sayım
// olduğu sürece doğrudur; okuma en geç 20 ms'de bir yapılır (motorlar_guncelle), o sürede ~40 tik.
constexpr int16_t PCNT_SINIR = 30000;
// Süzgeç: APB saatinin (80 MHz) bu kadar çevriminden kısa darbeler sayılmaz. 1000 -> 12,5 us.
// Enkoder en hızlı ~1 kHz (darbe ~500 us); TAHMİNİ, gürültü görülürse artır (en çok 1023).
constexpr uint16_t PCNT_SUZGEC = 1000;
// ---------------------------------------------------------------------------------------------

// Bir enkoder: hangi PCNT birimi, son ham okuma, 32 bit toplam. Hepsi yalnız loop() görevinden
// okunur/yazılır (kesme yok), bu yüzden kilit gerekmez.
struct Enkoder {
  pcnt_unit_t birim;
  uint8_t pin_a, pin_b;
  bool hazir;            // PCNT kurulumu başarılı mı (değilse toplam hep 0, PID kapalı kalır)
  int16_t son_ham;
  int32_t toplam;        // açılıştan (ya da odo_sifirla'dan) beri; ~400 km'de taşar, sorun değil
};

Enkoder sol_enk = {PCNT_UNIT_0, PIN_SOL_ENK_A, PIN_SOL_ENK_B, false, 0, 0};
Enkoder sag_enk = {PCNT_UNIT_1, PIN_SAG_ENK_A, PIN_SAG_ENK_B, false, 0, 0};

struct Teker {
  uint8_t pin_ileri, pin_geri;   // BTS IN1 (RPWM), IN2 (LPWM)
  uint8_t ledc_ileri, ledc_geri;
  bool motor_ters, enkoder_ters;
  Enkoder* enk;
  float hedef_hiz;        // m/s, "sur"dan gelen
  float rampa_hiz;        // m/s, ivme sınırıyla hedefe yaklaşan değer (motora giden)
  float integral;
  float onceki_hata;
  int32_t onceki_tik;
};

Teker sol = {PIN_SOL_ILERI_PWM, PIN_SOL_GERI_PWM, LEDC_SOL_R, LEDC_SOL_L,
             SOL_MOTOR_TERS, SOL_ENKODER_TERS, &sol_enk, 0, 0, 0, 0, 0};
Teker sag = {PIN_SAG_ILERI_PWM, PIN_SAG_GERI_PWM, LEDC_SAG_R, LEDC_SAG_L,
             SAG_MOTOR_TERS, SAG_ENKODER_TERS, &sag_enk, 0, 0, 0, 0, 0};

float son_v = 0.0f, son_w = 0.0f;
bool rampa_kipi = false;      // true: IVME_RAMPA_* sınırları (eğimde)

// PCNT birimini kurar: darbe = A, kontrol = B. A'nın yükselen kenarında +1, düşen kenarında -1;
// B LOW iken yön ters çevrilir. Sonuç eski kesme koduyla aynı: A == B ise +1, farklıysa -1.
//   A yükseldi, B=1 -> +1 | A yükseldi, B=0 -> -1 | A düştü, B=1 -> -1 | A düştü, B=0 -> +1
// Her ESP-IDF çağrısının sonucu denetlenir; biri başarısızsa enkoder "yok" sayılır.
bool enkoder_kur(Enkoder& e) {
  // Dahili pull-up (enkoder çıkışı açık kollektör olabilir; rapor Y3, T7). PCNT'den ÖNCE ayarlanır.
  pinMode(e.pin_a, INPUT_PULLUP);
  pinMode(e.pin_b, INPUT_PULLUP);
  pcnt_config_t ayar = {};
  ayar.pulse_gpio_num = e.pin_a;
  ayar.ctrl_gpio_num = e.pin_b;
  ayar.lctrl_mode = PCNT_MODE_REVERSE;
  ayar.hctrl_mode = PCNT_MODE_KEEP;
  ayar.pos_mode = PCNT_COUNT_INC;
  ayar.neg_mode = PCNT_COUNT_DEC;
  ayar.counter_h_lim = PCNT_SINIR;
  ayar.counter_l_lim = -PCNT_SINIR;
  ayar.unit = e.birim;
  ayar.channel = PCNT_CHANNEL_0;
  if (pcnt_unit_config(&ayar) != ESP_OK) return false;
  if (pcnt_set_filter_value(e.birim, PCNT_SUZGEC) != ESP_OK) return false;
  if (pcnt_filter_enable(e.birim) != ESP_OK) return false;
  // Sınır olaylarını aç: sayaç sınıra varınca 0'a dönsün (pcnt_unit_config bunları kapatır).
  // Kesme (ISR) KURULMAZ; toplam yoklamayla tutulur.
  if (pcnt_event_enable(e.birim, PCNT_EVT_H_LIM) != ESP_OK) return false;
  if (pcnt_event_enable(e.birim, PCNT_EVT_L_LIM) != ESP_OK) return false;
  if (pcnt_counter_pause(e.birim) != ESP_OK) return false;
  if (pcnt_counter_clear(e.birim) != ESP_OK) return false;
  if (pcnt_counter_resume(e.birim) != ESP_OK) return false;
  e.son_ham = 0;
  e.toplam = 0;
  return true;
}

// Ham sayacı okur, son okumadan beri farkı (mod PCNT_SINIR) 32 bit toplama ekler.
void enkoder_topla(Enkoder& e) {
  if (!e.hazir) return;
  int16_t ham = 0;
  if (pcnt_get_counter_value(e.birim, &ham) != ESP_OK) return;
  int32_t fark = ((int32_t)ham - (int32_t)e.son_ham) % PCNT_SINIR;   // (-SINIR, SINIR)
  if (fark > PCNT_SINIR / 2) fark -= PCNT_SINIR;                       // sınırdan dönüş: ileri
  else if (fark < -PCNT_SINIR / 2) fark += PCNT_SINIR;                 // sınırdan dönüş: geri
  e.son_ham = ham;
  e.toplam += fark;
}

float kirp(float x, float sinir) {
  if (x > sinir) return sinir;
  if (x < -sinir) return -sinir;
  return x;
}

// Arduino-ESP32 2.x ve 3.x'te LEDC işlevleri farklı; ikisini de destekle (ama çekirdek 2.0.17'de SABİT).
// Görev oranı (duty) pin bağlanmadan ÖNCE 0 yazılır: pin PWM'e bağlandığı an çıkış 0'dır (rapor Y2).
void pwm_kur(uint8_t pin, uint8_t ledc) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)ledc;
  ledcAttach(pin, PWM_FREKANS, PWM_BIT);
  ledcWrite(pin, 0);
#else
  ledcSetup(ledc, PWM_FREKANS, PWM_BIT);
  ledcWrite(ledc, 0);
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

// cikis -1..1: + ileri (IN1), - geri (IN2). 0 iken iki PWM de 0 = BTS7960'ta fren (iki alt
// transistör iletimde; EN HIGH iken). EN LOW iken (bırakık) motor boştadır.
void teker_yaz(const Teker& t, float cikis) {
  if (t.motor_ters) cikis = -cikis;
  cikis = kirp(cikis, 1.0f);
  uint32_t deger = (uint32_t)(fabsf(cikis) * PWM_TAM + 0.5f);
  if (cikis >= 0.0f) {
    pwm_yaz(t.pin_geri, t.ledc_geri, 0);        // önce karşı yönü kapat (rapor Y6)
    pwm_yaz(t.pin_ileri, t.ledc_ileri, deger);
  } else {
    pwm_yaz(t.pin_ileri, t.ledc_ileri, 0);
    pwm_yaz(t.pin_geri, t.ledc_geri, deger);
  }
}

void teker_kur(Teker& t) {
  pwm_kur(t.pin_ileri, t.ledc_ileri);
  pwm_kur(t.pin_geri, t.ledc_geri);
  teker_yaz(t, 0.0f);
}

int32_t tik_oku(Teker& t) {
  enkoder_topla(*t.enk);                         // her okumada güncel (yoklama)
  int32_t ham = t.enk->toplam;
  return t.enkoder_ters ? -ham : ham;
}

// Rampa: hızı hedefe doğru bir adım (DT) yürütür.
//   |hız| küçülüyorsa (yavaşlama, dur, yön değişiminin ilk yarısı) FREN sınırı,
//   |hız| büyüyorsa HIZLANMA sınırı. Yön değişiminde 0'ın öbür yanına fren adımıyla geçilmez:
//   o adım 0'da biter, sonraki adımlar hızlanma sınırıyla devam eder.
float rampa_adimi(float simdiki, float hedef) {
  const float surus = rampa_kipi ? IVME_RAMPA_SURUS : IVME_DUZ_SURUS;
  const float fren = rampa_kipi ? IVME_RAMPA_FREN : IVME_DUZ_FREN;
  const float fark = hedef - simdiki;
  const bool yavasliyor = (simdiki > 0.0f && fark < 0.0f) || (simdiki < 0.0f && fark > 0.0f);
  if (yavasliyor) {
    float yeni = simdiki + kirp(fark, fren * DT);
    if ((simdiki > 0.0f && yeni < 0.0f) || (simdiki < 0.0f && yeni > 0.0f)) yeni = 0.0f;
    return yeni;
  }
  return simdiki + kirp(fark, surus * DT);
}

// Bir teker için bir kontrol adımı (rampa + ileri besleme + PID).
void teker_adim(Teker& t) {
  // 1) Rampa: hızlanma ve fren ayrı sınırlı (bkz. motorlar.h "İVME SINIRLARI").
  t.rampa_hiz = rampa_adimi(t.rampa_hiz, t.hedef_hiz);

  // 2) Ölçülen hız (enkoderden).
  int32_t tik = tik_oku(t);
  int32_t fark = tik - t.onceki_tik;
  t.onceki_tik = tik;
  float olculen = (fark / TIK_PER_TUR) * (PI * TEKER_CAPI_M) / DT;

  // 3) İleri besleme: "bu hız için kabaca şu kadar PWM gerekir".
  float cikis = t.rampa_hiz / TEKER_AZAMI_HIZ;

  // 4) PID düzeltmesi (katsayılar sıfırken etkisiz).
  if (ENKODER_VAR && t.enk->hazir && t.rampa_hiz != 0.0f) {
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

void teker_ani_dur(Teker& t) {
  t.hedef_hiz = t.rampa_hiz = 0.0f;
  t.integral = t.onceki_hata = 0.0f;
  teker_yaz(t, 0.0f);                            // PWM HEMEN 0 (sonraki 20 ms'yi beklemez)
}

}  // namespace

void motorlar_baslat() {
  // PWM'ler görev oranı 0 ile bağlanır. EN (GPIO13) guc_pinleri_guvenle() ile zaten LOW; burada
  // ona dokunulmaz, yalnız guc.cpp "devrede" iken HIGH yapar.
  teker_kur(sol);
  teker_kur(sag);
  if (ENKODER_VAR) {
    sol_enk.hazir = enkoder_kur(sol_enk);
    sag_enk.hazir = enkoder_kur(sag_enk);
  }
  sol.onceki_tik = tik_oku(sol);
  sag.onceki_tik = tik_oku(sag);
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
  // Yalnız hedef sıfırlanır; teker_adim fren sınırıyla (düz 1,8 / rampa 0,1 m/s^2) durdurur.
  son_v = son_w = 0.0f;
  sol.hedef_hiz = 0.0f;
  sag.hedef_hiz = 0.0f;
}

void motorlar_ani_dur() {
  son_v = son_w = 0.0f;
  teker_ani_dur(sol);
  teker_ani_dur(sag);
}

void motorlar_rampa_modu(bool acik) { rampa_kipi = acik; }
bool motorlar_rampa_modu_mu() { return rampa_kipi; }

void motorlar_guncelle(uint32_t simdi_ms) {
  (void)simdi_ms;
  // Savunma: güç devrede değilken motor hedefi hiç olmamalı ("sur" reddedilir, bırakma ani durdurur).
  // Yine de bir yol kaçarsa burada sıfırlanır; EN zaten LOW olduğu için motor dönmez.
  if (!guc_devrede() && (sol.rampa_hiz != 0.0f || sag.rampa_hiz != 0.0f ||
                         sol.hedef_hiz != 0.0f || sag.hedef_hiz != 0.0f)) {
    motorlar_ani_dur();
  }
  teker_adim(sol);
  teker_adim(sag);
}

float motorlar_hedef_v() { return son_v; }
float motorlar_hedef_w() { return son_w; }
int32_t motor_sol_tik() { return tik_oku(sol); }
int32_t motor_sag_tik() { return tik_oku(sag); }

void motor_tik_sifirla() {
  // Önce donanım sayacını son kez topla (son_ham güncel olsun), sonra toplamları sıfırla.
  // Hepsi loop() görevinde: kesme yok, kilit gerekmez.
  enkoder_topla(sol_enk);
  enkoder_topla(sag_enk);
  sol_enk.toplam = 0;
  sag_enk.toplam = 0;
  // PID'in "önceki tik"i de sıfırlanmalı; yoksa bir sonraki adımda dev bir hız sıçraması ölçülür.
  sol.onceki_tik = 0;
  sag.onceki_tik = 0;
}
