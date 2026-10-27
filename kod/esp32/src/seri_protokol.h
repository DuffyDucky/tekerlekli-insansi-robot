// seri_protokol.h -- Pi ile konuşma: USB-UART, 115200 baud, her satır bir JSON.
//
// Pi -> ESP32 (kod/robot/seri.py ile aynı adlar):
//   {"k":"jest","ad":"selam"}            kayıtlı jesti oynat
//   {"k":"jest","ad":"isaret","yon":"sol"}  yon isteğe bağlı: sol|sag|ileri|arka (şimdilik cevaba
//                                        aynen yazılır, oynatıcı henüz yön ayırmaz; bkz. jestler.h)
//   {"k":"sur","v":0.3,"w":0.0}          v: ileri m/s, w: dönüş rad/s (ikisi de -1..1'e kırpılır)
//   {"k":"dur"}                          motorları ANINDA durdur, oynayan jesti kes
//   {"k":"servo","kanal":0,"aci":90}     tek servoyu elle (kanal: 0-15 ya da "sag_omuz" gibi ad)
//   {"k":"ping"}                         canlı mısın? (cevapta "odo":true = odo yayını açık)
//   {"k":"odo_sifirla"}                  iki enkoder tik sayacını sıfırla
// ESP32 -> Pi:
//   her komuta bir cevap: {"ok":true,"k":"..."}  ya da  {"ok":false,"k":"...","hata":"..."}
//   açılışta bir kez:     {"k":"hazir","surum":"...","pca9685":true}
//   isteğe bağlı (DURUM_YAYINI=1): 1 s'de bir {"k":"durum","jest":"...","sur":[v,w],"wd":true}
//   varsayılan AÇIK (ODO_YAYINI=1): ODO_ARALIK_MS'de bir (100 ms = 10 Hz)
//                         {"k":"odo","sol":<toplam tik>,"sag":<toplam tik>,"yaw":<derece|null>,"ms":<millis>}
//   Odo yayını cevap değildir, komut beklemez; komut bekçisini (watchdog) etkilemez.
#pragma once
#include <stdint.h>

// Odometri yayını: varsayılan AÇIK (Pi konum hesabı için gerekli). Kapatmak için platformio.ini
// build_flags'e -DODO_YAYINI=0. Aralık -DODO_ARALIK_MS=... ile değişir (varsayılan 100 ms = 10 Hz).
#ifndef ODO_YAYINI
#define ODO_YAYINI 1
#endif
#ifndef ODO_ARALIK_MS
#define ODO_ARALIK_MS 100
#endif

// Seri portu açar ve "hazir" mesajını gönderir.
void seri_baslat();

// Gelen baytları okur; tamamlanan her satırı komut olarak işler. Her döngüde çağrılır, beklemez.
void seri_isle(uint32_t simdi_ms);

// {"k":"durum",...} mesajını gönderir.
void seri_durum_gonder();

// {"k":"odo","sol":...,"sag":...,"yaw":...,"ms":...} mesajını gönderir. Sabit tamponla yazılır
// (10 Hz'de her seferinde bellek ayırmasın diye JsonDocument kullanılmaz).
void seri_odo_gonder(uint32_t simdi_ms);
