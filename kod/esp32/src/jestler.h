// jestler.h -- kayıtlı jestleri (anahtar kare dizileri) oynatır.
//
// Jest = zaman damgalı kareler: {ms, her kanalın açısı}. Oynatıcı her 20 ms'de "jest başladığından
// beri kaç ms geçti?" diye bakar, içinde bulunduğu iki kare arasında doğrusal ara değer bulur ve
// servoların HEDEFİNİ ayarlar (servoyu doğrudan sürmez; yumuşatmayı servolar modülü yapar).
// Jest bitince bütün servolar boşta duruşa hedeflenir.
// Jest verisi kod/jestler/*.yaml'dan üretilir (src/jest_verisi.h), elle yazılmaz.
//
// YÖN AYRIMI (TODO, henüz yapılmadı): "jest" komutu isteğe bağlı "yon" (sol|sag|ileri|arka) alır;
// seri_protokol bunu doğrular ve cevaba yazar, ama oynatıcı şimdilik yönü KULLANMAZ.
// Tasarım: "isaret" jestinin yalnız SAĞ kol sürümü kayıtlı. Sol kol için ikinci bir YAML yazmak
// yerine ayna kanal eşlemesi kullanılacak: kanallar.yaml'a her kanalın aynası tanımlanır
// (ör. sag_omuz <-> sol_omuz, sag_dirsek <-> sol_dirsek, kafa_pan: aci -> 180 - aci).
// Sol kol servoları zaten "ters: true" olduğu için robot açıları aynı kalır, yalnız kanal yer
// değiştirir. jest_uret.py eşlemeyi jest_verisi.h'ye yazar; jest_baslat(ad, simdi_ms, yon)
// "sol" gelince hedefleri_yaz'da kanalı aynasına çevirir. "ileri/arka" için ayrı kareler gerekir
// (ör. kafa_tilt ve omuz açısı); hangi jestlerin hangi yönleri desteklediği YAML'da yazılacak.
#pragma once
#include <stdint.h>

// Adı verilen jesti baştan başlatır (çalışan jest varsa yarıda keser). Ad bilinmiyorsa false.
bool jest_baslat(const char* ad, uint32_t simdi_ms);

// Çalışan jesti yarıda keser; servolar o anki hedefte kalır (boşta duruşa DÖNMEZ).
void jest_durdur();

// Her 20 ms'de bir çağrılır. Jest bittiyse boşta duruşa döner.
void jestler_guncelle(uint32_t simdi_ms);

// Şu an oynayan jestin adı; jest yoksa "yok".
const char* jest_aktif_adi();

// Kayıtlı jest sayısı ve adları (ping cevabında listelemek için).
uint8_t jest_sayisi();
const char* jest_adi(uint8_t sira);
