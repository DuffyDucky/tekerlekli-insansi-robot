// motorlar.h -- iki tekerlek (sol/sağ) BTS7960 ile sürülür.
//
// Akış (her 20 ms, 50 Hz):
//   "sur" komutu (v, w)  ->  sol/sağ teker hedef hızı (m/s)  ->  rampa (ivme sınırı)
//   ->  ileri besleme + PID düzeltmesi  ->  PWM (-1..1)  ->  BTS7960
// Enkoder yoksa ya da PID katsayıları sıfırsa yalnız ileri besleme çalışır (açık çevrim).
//
// İVME SINIRLARI (29 Ekim 2026; tek kaynak kod/ortak/eklem_sinirlari.json -> src/sinirlar_verisi.h):
//   hızlanma (|hız| büyüyor)                     düz zemin IVME_DUZ_SURUS 0,5 m/s^2
//   yavaşlama / fren (|hız| küçülüyor, dur, bekçi) düz zemin IVME_DUZ_FREN 1,8 m/s^2
//   RAMPA KİPİNDE ikisi de IVME_RAMPA_SURUS / IVME_RAMPA_FREN (0,1 m/s^2): uzun robot eğimde devrilmesin.
// Yön değişiminde (ileri -> geri) önce fren sınırıyla 0'a inilir, sonra hızlanma sınırıyla çıkılır.
// Sınır her tekerin kendi hızına uygulanır. Acil stop gücü keser: motorlar boşa düşer, bu sınır işlemez.
//
// Robot 4 JGB37 ile kurulursa: her taraftaki iki motor aynı BTS7960'a paralel bağlanır,
// her taraftan bir enkoder okunur. Yazılım değişmez.
#pragma once
#include <stdint.h>

// Pinleri, PWM'i ve enkoder kesmelerini kurar; motorlar duruk ve sürücüler etkin başlar.
void motorlar_baslat();

// Hedef hız. v: ileri hız (m/s, + ileri), w: dönüş hızı (rad/s, + sola/saat yönü tersi).
// Değerler -1..1'e kırpılır (Pi tarafı zaten v<=0,5, w<=1,0 gönderir). Rampa ile ulaşılır.
void motorlar_hedef(float v, float w);

// Hedefi sıfırlar; tekerler FREN sınırıyla durur (düzde 1,8 m/s^2 -> 0,39 m/s'den ~0,22 s;
// rampa kipinde 0,1 m/s^2 -> ~3,9 s). "dur" komutu ve watchdog bunu çağırır. (0.4.0'dan önce anında
// PWM 0 idi; 29 Ekim kararı: fren de sınırlı.)
void motorlar_dur();

// Rampa kipi: true iken hızlanma ve fren rampa sınırlarıyla (IVME_RAMPA_*). Yalnız ivme sınırını
// seçer; kolları ev pozuna almak seri_protokol'ün işi (rampa_kipi_*). Açılışta kapalı.
void motorlar_rampa_modu(bool acik);
bool motorlar_rampa_modu_mu();

// Her 20 ms'de bir çağrılır: rampa, PID, PWM yazma.
void motorlar_guncelle(uint32_t simdi_ms);

// Son kabul edilen hedef (durum mesajı için).
float motorlar_hedef_v();
float motorlar_hedef_w();

// Enkoder sayıları: açılıştan (ya da son sıfırlamadan) beri toplam tik, yönü düzeltilmiş
// (ileri dönüşte artar). Odometri telemetrisi ({"k":"odo",...}) ve kalibrasyon bunları kullanır.
int32_t motor_sol_tik();
int32_t motor_sag_tik();

// İki tik sayacını kesme güvenli şekilde sıfırlar ({"k":"odo_sifirla"} komutu).
void motor_tik_sifirla();
