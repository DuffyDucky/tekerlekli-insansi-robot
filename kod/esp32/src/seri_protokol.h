// seri_protokol.h -- Pi ile konuşma: USB-UART, 115200 baud, her satır bir JSON.
//
// Pi -> ESP32 (kod/robot/seri.py ile aynı adlar):
//   {"k":"jest","ad":"selam"}            kayıtlı jesti oynat
//   {"k":"sur","v":0.3,"w":0.0}          v: ileri m/s, w: dönüş rad/s (ikisi de -1..1'e kırpılır)
//   {"k":"dur"}                          motorları ANINDA durdur, oynayan jesti kes
//   {"k":"servo","kanal":0,"aci":90}     tek servoyu elle (kanal: 0-15 ya da "sag_omuz" gibi ad)
//   {"k":"ping"}                         canlı mısın?
// ESP32 -> Pi:
//   her komuta bir cevap: {"ok":true,"k":"..."}  ya da  {"ok":false,"k":"...","hata":"..."}
//   açılışta bir kez:     {"k":"hazir","surum":"...","pca9685":true}
//   isteğe bağlı (DURUM_YAYINI=1): 1 s'de bir {"k":"durum","jest":"...","sur":[v,w],"wd":true}
#pragma once
#include <stdint.h>

// Seri portu açar ve "hazir" mesajını gönderir.
void seri_baslat();

// Gelen baytları okur; tamamlanan her satırı komut olarak işler. Her döngüde çağrılır, beklemez.
void seri_isle(uint32_t simdi_ms);

// {"k":"durum",...} mesajını gönderir.
void seri_durum_gonder();
