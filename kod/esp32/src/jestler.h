// jestler.h -- kayıtlı jestleri (anahtar kare dizileri) oynatır.
//
// Jest = zaman damgalı kareler: {ms, her kanalın açısı}. Oynatıcı her 20 ms'de "jest başladığından
// beri kaç ms geçti?" diye bakar, içinde bulunduğu iki kare arasında doğrusal ara değer bulur ve
// servoların HEDEFİNİ ayarlar (servoyu doğrudan sürmez; yumuşatmayı servolar modülü yapar).
// Jest bitince bütün servolar boşta duruşa hedeflenir.
// Jest verisi kod/jestler/*.yaml'dan üretilir (src/jest_verisi.h), elle yazılmaz.
//
// YÖNLÜ JEST (27 Ekim 2026): "jest" komutu isteğe bağlı "yon" (sol|sag|ileri|arka) alır.
// Yön varyantları jest_uret.py ile ÜRETİM anında hazırlanır (YAML'da "yonler:" bölümü), ESP32
// çalışırken açı hesaplamaz, yalnız doğru kare dizisini seçer:
//   sag   = varsayılan kareler (aynı dizi, kopya yok)
//   sol   = varsayılanın aynası (kanallar.yaml "ayna"/"ayna_aci": kol kanalı yer değiştirir,
//           açı aynı; kafa_pan 180 - açı)
//   ileri / arka = YAML'da elle yazılmış kareler
// Jestin o yön için varyantı yoksa varsayılan kareler oynar ve yon_uygulandi = false olur.
#pragma once
#include <stdint.h>

// Yön adının sıra numarası (jest_verisi.h YON_ADLARI); geçersiz ya da nullptr ise -1.
int jest_yon_indeksi(const char* yon);

// Adı verilen jesti baştan başlatır (çalışan jest varsa yarıda keser). Ad bilinmiyorsa false.
// yon: nullptr = yön yok (varsayılan kareler). Geçerli bir yön verilip jestin o yön varyantı
// varsa onu oynatır. yon_uygulandi (nullptr olabilir): varyant oynuyorsa true, varsayılan
// oynuyorsa false. Geçersiz yön adı da varsayılanı oynatır (false); doğrulama seri_protokol'de.
bool jest_baslat(const char* ad, const char* yon, uint32_t simdi_ms, bool* yon_uygulandi = nullptr);

// Çalışan jesti yarıda keser; servolar o anki hedefte kalır (boşta duruşa DÖNMEZ).
void jest_durdur();

// Her 20 ms'de bir çağrılır. Jest bittiyse boşta duruşa döner.
void jestler_guncelle(uint32_t simdi_ms);

// Şu an oynayan jestin adı; jest yoksa "yok".
const char* jest_aktif_adi();

// Kayıtlı jest sayısı ve adları (ping cevabında listelemek için).
uint8_t jest_sayisi();
const char* jest_adi(uint8_t sira);
