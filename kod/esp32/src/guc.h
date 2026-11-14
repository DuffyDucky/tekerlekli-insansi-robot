// guc.h -- güç rölesi (K1, K2 ön şarj), acil stop, anahtarlı bara ve arıza durum makinesi.
//
// NEDEN VAR (pin haritası sürüm 4, 14.11.2026; planlama/adim3/pin-haritasi.md §4, §5 Y2-Y8):
// Motorlar ve servolar "anahtarlı bara"dan beslenir. Barayı K1 rölesi bağlar; K1'den önce K2 rölesi
// barayı 5,6 ohm'luk ön şarj direnci üstünden yavaşça doldurur (kondansatörler aniden şarj olup
// kontakları yakmasın). Acil stop mantarı iki rölenin BOBİN beslemesini keser: mantar basılıyken
// firmware ne yaparsa yapsın röle çekmez. Bu modül yalnız "devreye al" ve "bırak" sırasını yürütür.
//
//   GPIO4  (çıkış) K1 "devreye al"      GPIO19 (çıkış) K2 ön şarj (en çok 1 s HIGH!)
//   GPIO13 (çıkış) BTS EN, dört uç      GPIO23 (giriş) acil stop: HIGH = basılı / F5 attı
//   GPIO5  (giriş) bara: LOW = gerilimli
//   GPIO32/33 (ADC1, 0 dB) sol/sağ BTS IS: yalnız arıza bayrağı   GPIO36 (ADC1) akü gerilimi
//
// DURUMLAR:
//   birakik  röleler bırakık, EN=0. Açılışta ve "birak" komutundan sonra. Kendiliğinden ASLA arm olmaz.
//   onsarj   arm sırası yürüyor (19=1 -> 500 ms -> bara? -> 4=1 -> 100 ms -> 19=0 -> bara?)
//   devrede  K1 çekili, bara gerilimli, EN=1: motorlar sürülebilir.
//   ariza    bir koruma bıraktı; KİLİTLİ: yalnız yeni bir "arm" temizler ("birak" temizlemez).
//
// BIRAKMA (aynı döngü turunda): 13=0, dört PWM 0, 4=0, 19=0. Tetikleyenler ve "neden":
//   "birak" komutu (arıza değil -> birakik) | acil_stop | bara_gitti | bara_yok | is_sol | is_sag |
//   i2c (PCA9685 art arda 3 kez cevap yok) | sessizlik (devredeyken SESSIZLIK_BIRAK_MS komut yok) |
//   onsarj_sure (K2 zamanlayıcısı ön şarj bitmeden doldu: döngü takıldı demek; normalde görülmez).
//
// GPIO19 HİÇBİR KOŞULDA 1 s'DEN UZUN HIGH KALMAZ: ana döngüden BAĞIMSIZ tek atımlık esp_timer bunu
// zorlar (döngü takılsa da düşer). Hata durumunda ön şarj direnci 32-38 W ısınır (rapor EL E9).
//
// DURUM: derlendi, KARTTA DENENMEDİ (14.11.2026). Eşikler TAHMİNİ (guc.cpp başı).
#pragma once
#include <stdint.h>

// Komut sessizliği: devredeyken bu kadar ms hiçbir geçerli komut satırı gelmezse bırak ("sessizlik").
// 0 = kapalı. Pi devredeyken saniyede bir "ping" atar. platformio.ini: -DSESSIZLIK_BIRAK_MS=...
#ifndef SESSIZLIK_BIRAK_MS
#define SESSIZLIK_BIRAK_MS 5000
#endif

// setup()'ın İLK satırı (seriden, I2C'den, her şeyden önce): 4, 19, 13 LOW çıkış (rapor Y2).
void guc_pinleri_guvenle();

// Girişleri (23, 5), ADC zayıflatmalarını ve K2 zamanlayıcısını kurar. guc_pinleri_guvenle()'den sonra.
void guc_baslat();

// Her döngüde çağrılır, beklemez: girişleri süzer, arm sırasını yürütür, korumaları denetler.
void guc_guncelle(uint32_t simdi_ms);

// "arm" komutu. nullptr = kabul edildi (durum "onsarj"); değilse hata kodu:
// "acil_stop", "pca9685_yok", "zaten_devrede", "mesgul", "zamanlayici_yok".
const char* guc_arm(uint32_t simdi_ms);

// "birak" komutu: her durumda kabul; çıkışlar aynı turda kapanır. Arızadaysa arıza (kilit) kalır.
void guc_birak(uint32_t simdi_ms);

// Geçerli bir komut satırı geldi (sessizlik sayacı).
void guc_komut_geldi(uint32_t simdi_ms);

// Bekleyen {"k":"guc",...} olayını gönderir. Komut cevabından SONRA çağrılır (cevap önce gitsin).
void guc_olay_gonder();

bool guc_devrede();                  // true: durum "devrede" (sur kabul edilir)
bool guc_ariza_mi();                 // true: durum "ariza" (LED deseni)
const char* guc_durum_adi();         // "birakik" | "onsarj" | "devrede" | "ariza"
const char* guc_ariza_nedeni();      // arızadaysa neden, değilse nullptr
bool guc_acil_basili();              // süzülmüş GPIO23: true = mantar basılı / F5 attı
bool guc_bara_gerilimli();           // süzülmüş GPIO5: true = bara gerilimli
float guc_aku_volt();                // akü gerilimi (V, KALİBRE EDİLMEDİ); ölçüm yoksa NAN
