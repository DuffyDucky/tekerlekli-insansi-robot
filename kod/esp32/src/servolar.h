// servolar.h -- PCA9685 üzerinden servo sürme, yumuşak geçiş.
//
// Fikir: her servonun bir "hedef" açısı ve bir "şimdiki" açısı var. Jest ya da elle komut yalnız
// HEDEFİ değiştirir. servolar_guncelle() her 20 ms'de şimdiki açıyı hedefe doğru en çok
// (hiz * 0,02) derece kaydırır. Böylece servo hiçbir zaman ani sıçramaz.
// Açılar "robot açısı"dır (bkz. kod/jestler/kanallar.yaml); sınır dışı istek sınıra kırpılır.
#pragma once
#include <stdint.h>

// I2C ve PCA9685'i başlatır, servoları boşta duruşa gönderir. PCA9685 bulunamazsa false.
bool servolar_baslat();

// PCA9685 açılışta bulundu mu? (bulunamadıysa servo komutları hata döner)
bool servolar_hazir();

// Kanal sayısı ve sıra numarasıyla bilgi (sıra = jest_verisi.h'deki SERVO_TABLOSU sırası).
uint8_t servo_sayisi();
const char* servo_adi(uint8_t sira);

// PCA9685 kanal numarası (0-15) ya da kanal adından sıra numarası bulur; yoksa -1.
int servo_sira_kanaldan(int kanal);
int servo_sira_addan(const char* ad);

// Hedef açıyı ayarlar (sınıra kırpar). Kırpılmış (uygulanan) hedefi döner.
float servo_hedef_ayarla(uint8_t sira, float robot_acisi);

// Tüm servoları boşta duruşa hedefler (yumuşak geçişle gider).
void servolar_bostaya();

// Her 20 ms'de bir çağrılır: şimdiki açıyı hedefe doğru sınırlı adımla yürütür, PCA9685'e yazar.
void servolar_guncelle();
