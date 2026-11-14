// watchdog.h -- iki ayrı bekçi:
//
// 1) KOMUT BEKÇİSİ (500 ms): Pi robot sürerken "sur" komutunu ~200 ms'de bir yeniden gönderir.
//    Son "sur"dan 500 ms geçerse (Pi çöktü, kablo çıktı, program takıldı) motorlar ANINDA durdurulur
//    (motorlar_ani_dur: PWM hemen 0, rampasız; 0.5.0'dan beri). "dur" komutu ise rampalıdır (fren sınırı).
//    Bu bekçi K1 rölesini BIRAKMAZ: onu guc.cpp'deki 5 s komut sessizliği kuralı yapar (SESSIZLIK_BIRAK_MS).
// 2) DÖNGÜ BEKÇİSİ (ESP32 donanım zamanlayıcısı, 2 s): ESP32'nin kendi programı bir yerde takılırsa
//    komut bekçisi de çalışamaz (o da aynı döngüde). Bu yüzden döngü 2 s boyunca "ben iyiyim"
//    demezse ESP32 kendini yeniden başlatır. Resette 4 / 19 / 13 çıkışları kapanır, taban ve EN
//    pull-down dirençleri onları LOW tutar: röleler bırakır, motorlar durur (pin haritası §4).
//
// İKİSİ DE YAZILIMDIR. Asıl güvenlik donanımsal Emas acil stop mantarıdır: röle bobinlerinin
// beslemesini keser, bu koddan tamamen bağımsızdır.
#pragma once
#include <stdint.h>

// Döngü bekçisini kurar. setup() sonunda bir kez çağrılır.
void watchdog_baslat();

// "sur" geldiğinde çağrılır: sayacı sıfırlar.
void watchdog_besle(uint32_t simdi_ms);

// Her döngüde çağrılır: süre dolduysa motorları ANINDA durdurur, döngü bekçisine "iyiyim" der.
void watchdog_kontrol(uint32_t simdi_ms);

// Komut bekçisi şu an motorları durdurmuş mu? (açılışta, henüz "sur" gelmediği için true)
bool watchdog_tetikli();
