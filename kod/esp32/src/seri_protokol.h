// seri_protokol.h -- Pi ile konuşma: USB-UART, 115200 baud, her satır bir JSON.
// SÖZLEŞME: Pi tarafı (kod/robot/seri.py) aynı adları kullanır. ADLARI DEĞİŞTİRME; ekleme yapılırsa
// iki tarafta birlikte yapılır.
//
// Pi -> ESP32:
//   {"k":"arm"}                          güç devreye al (K2 ön şarj -> K1). Hemen cevap:
//                                          {"ok":true,"k":"arm","guc":"onsarj"}  ya da
//                                          {"ok":false,"k":"arm","hata":"acil_stop"|"pca9685_yok"|
//                                                       "zaten_devrede"|"mesgul"|"zamanlayici_yok"}
//                                        Sonuç ~600 ms sonra "guc" olayıyla gelir (devrede ya da ariza).
//   {"k":"birak"}                        gücü bırak (her durumda kabul): {"ok":true,"k":"birak","ms":<millis>}
//                                        Arızadaysa arıza kalır (kilit yalnız yeni "arm" ile çözülür).
//   {"k":"reset"}                        önce bırak, {"ok":true,"k":"reset"}, sonra ESP32 yeniden başlar
//                                        (ardından "hazir" gelir; güç "birakik").
//   {"k":"jest","ad":"selam"}            kayıtlı jesti oynat
//   {"k":"jest","ad":"isaret","yon":"sol"}  yon isteğe bağlı: sol|sag|ileri|arka; cevapta
//                                        "yon" ve "yon_uygulandi" (false = jestin o yön varyantı
//                                        yok, varsayılan oynadı; bkz. jestler.h)
//   {"k":"sur","v":0.3,"w":0.0}          v: ileri m/s, w: dönüş rad/s (ikisi de -1..1'e kırpılır).
//                                        Güç "devrede" DEĞİLSE {"ok":false,"k":"sur","hata":"devrede_degil"}
//                                        (bekçi beslenmez, rampa alanı uygulanmaz).
//   {"k":"sur","v":0.1,"w":0,"rampa":true}  "rampa" isteğe bağlı: verilirse elle rampa kipini de ayarlar
//   {"k":"dur"}                          motorları FREN sınırıyla durdur (düz 1,8 / rampa 0,1 m/s^2),
//                                        oynayan jesti kes. Gücü bırakmaz.
//   {"k":"rampa","ac":true}              elle rampa kipi aç/kapa; cevap {"ok":true,"k":"rampa",
//                                        "rampa":<etkin>,"elle":..,"imu":..}
//   {"k":"servo","kanal":0,"aci":90}     tek servoyu elle (kanal: 0-15 ya da "sag_omuz" gibi ad)
//   {"k":"ping"}                         canlı mısın? Pi devredeyken saniyede bir atar (5 s sessizlik kuralı)
//   {"k":"odo_sifirla"}                  iki enkoder tik toplamını sıfırla
//   jest ve servo güç devrede DEĞİLKEN de kabul edilir (masa denemesi): PCA9685 mantığı ESP32'nin
//   3,3 V'undan beslenir ama servoların gücü röle (K1) arkasındadır; kollar kıpırdamaz.
//
// ESP32 -> Pi:
//   her komuta bir cevap: {"ok":true,"k":"..."}  ya da  {"ok":false,"k":"...","hata":"..."}
//   açılışta bir kez:     {"k":"hazir","surum":"0.5.0","pca9685":true,"guc":"birakik"}
//   ping cevabı:          {"ok":true,"k":"ping","surum":..,"ms":..,"pca9685":..,"odo":..,"rampa":..,
//                          "guc":"birakik|onsarj|devrede|ariza","acil":<bool>,"bara":<bool>,
//                          "aku":<volt|null>,"ariza":<neden|null>,"jestler":[...]}
//   GÜÇ OLAYI (komutsuz, "ok" alanı yok; güç durumu her değiştiğinde, komut cevabından SONRA):
//                         {"k":"guc","guc":"birakik|onsarj|devrede|ariza","neden":"..."|null,"ms":<millis>}
//     neden (yalnız ariza'da; diğerlerinde null): acil_stop, bara_yok, bara_gitti, is_sol, is_sag,
//     i2c, sessizlik, onsarj_sure.
//   isteğe bağlı (DURUM_YAYINI=1): 1 s'de bir {"k":"durum","jest":"...","sur":[v,w],"wd":true,
//                         "rampa":false, + ping'deki guc/acil/bara/aku/ariza}
//   "acil": true = mantar basılı ya da F5 attı (GPIO23 HIGH). "bara": true = bara gerilimli (GPIO5 LOW).
//   "aku": volt, KALİBRE EDİLMEDİ (100k/18k bölücü); ölçüm yoksa null.
//   Açılışta ve resetten sonra güç ASLA kendiliğinden devreye girmez: Pi "arm" göndermelidir.
//
// RAMPA KİPİ (29 Ekim 2026; planlama/kopru-mekanik-yazilim.md F8): eğimde teker ivmesi ve freni
// <= 0,1 m/s^2 (motorlar.*) ve KOLLAR EV POZUNDA. Etkin kip = elle (Pi "rampa" komutu ya da sur'daki
// "rampa") VEYA IMU eğimi (main.cpp histerezis; IMU yoksa yalnız elle). Elle açıkken IMU kapatamaz.
// Kip açıldığı an oynayan jest kesilir ve servolar BOSTA_DURUS'a (ev pozu) gider. Kip açıkken
// "bosta" dışındaki jest ve elle "servo" komutu {"ok":false,...,"hata":"rampa_modunda"} ile reddedilir.
//
// ODOMETRİ: varsayılan AÇIK (ODO_YAYINI=1): ODO_ARALIK_MS'de bir (100 ms = 10 Hz)
//                         {"k":"odo","sol":<toplam tik>,"sag":<toplam tik>,"yaw":<derece|null>,"ms":<millis>}
//   Odo yayını cevap değildir, komut beklemez; komut bekçisini (watchdog) ve sessizlik sayacını etkilemez.
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

// {"k":"guc","guc":...,"neden":...|null,"ms":...} olayını gönderir (guc.cpp çağırır).
void seri_guc_olayi_gonder(const char* guc, const char* neden, uint32_t ms);

// Rampa kipi (bkz. yukarıda RAMPA KİPİ). main.cpp IMU eğim histerezisinin sonucunu bildirir;
// etkin kip = elle || imu. Kip kapalıdan açığa geçince jest kesilir, kollar ev pozuna gider.
void rampa_imu_bildir(bool egimde);
bool rampa_kipi_acik();
