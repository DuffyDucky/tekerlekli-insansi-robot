// watchdog.h -- iki ayrı bekçi:
//
// 1) KOMUT BEKÇİSİ (500 ms): Pi robot sürerken "sur" komutunu ~200 ms'de bir yeniden gönderir.
//    Son "sur"dan 500 ms geçerse (Pi çöktü, kablo çıktı, program takıldı) motorlar durdurulur.
//    "dur" komutu bekçiyi beklemez, her zaman ANINDA durdurur.
// 2) DÖNGÜ BEKÇİSİ (ESP32 donanım zamanlayıcısı, 2 s): ESP32'nin kendi programı bir yerde takılırsa
//    komut bekçisi de çalışamaz (o da aynı döngüde). Bu yüzden döngü 2 s boyunca "ben iyiyim"
//    demezse ESP32 kendini yeniden başlatır; açılışta EN pinleri LOW olduğu için motorlar durur.
//
// İKİSİ DE YAZILIMDIR. Asıl güvenlik donanımsal Emas acil stop butonudur: motor ve servo güç
// hattını doğrudan keser, bu koddan tamamen bağımsızdır.
#pragma once
#include <stdint.h>

// Döngü bekçisini kurar. setup() sonunda bir kez çağrılır.
void watchdog_baslat();

// "sur" geldiğinde çağrılır: sayacı sıfırlar.
void watchdog_besle(uint32_t simdi_ms);

// Her döngüde çağrılır: süre dolduysa motorları durdurur, döngü bekçisine "iyiyim" der.
void watchdog_kontrol(uint32_t simdi_ms);

// Komut bekçisi şu an motorları durdurmuş mu? (açılışta, henüz "sur" gelmediği için true)
bool watchdog_tetikli();
