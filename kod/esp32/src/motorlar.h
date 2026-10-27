// motorlar.h -- iki tekerlek (sol/sağ) BTS7960 ile sürülür.
//
// Akış (her 20 ms, 50 Hz):
//   "sur" komutu (v, w)  ->  sol/sağ teker hedef hızı (m/s)  ->  rampa (hızlanma sınırı)
//   ->  ileri besleme + PID düzeltmesi  ->  PWM (-1..1)  ->  BTS7960
// Enkoder yoksa ya da PID katsayıları sıfırsa yalnız ileri besleme çalışır (açık çevrim).
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

// ANINDA durdurur: rampa yok, PWM sıfır (fren). "dur" komutu ve watchdog bunu çağırır.
void motorlar_dur();

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
