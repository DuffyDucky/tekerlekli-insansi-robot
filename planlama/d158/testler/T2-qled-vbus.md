# T2 · 10,1" QLED: Power ↔ Touch VBUS bağı (Pi'ye takmadan)

Kâğıt T2 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Multimetre markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Kafa ekranının (WaveShare 10,1" QLED) iki micro USB girişi var: **Power** (besleme) ve **Touch** (dokunmatik verisi). Ekranın içinde
bu iki girişin 5 V (VBUS) uçlarının birbirine bağlı olup olmadığını, ekranı **hiçbir yere takmadan** multimetreyle bulmak.

## Neden önemli

Tasarımda Power girişi SY8205 düşürücüden, Touch kablosu Pi'den gelir (`elektrik.md:39-40`). İki 5 V kaynağı birbirine bağlanmamalı.
Ekranın içinde Touch VBUS, Power'a bağlıysa Pi'nin 5 V'u ile SY8205 çıkışı Touch kablosu üzerinden birleşir; iki düşürücü birbirini
besler, biri zarar görebilir. Ekranın iç bağlantısı **doğrulanmadı** (`elektrik.md:43`).

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Power ve Touch ayrı micro USB | `elektrik.md:17` | Üretici sayfası |
| "İki 5 V kaynağı köprülenmez", Touch'tan 5 V köprülenmez | `elektrik.md:43`, `elektrik.md:303` | Tasarım kuralı |
| Touch VBUS ile Power VBUS ekran içinde bağlı değil | `elektrik.md:43` | **Doğrulanmadı**; bu kâğıt doğrular |
| QLED akımı 0,9 A | `elektrik.md:18`, `elektrik.md:25` | Varsayım (T3 ölçer) |

## Gereken alet

- Multimetre (direnç, diyot, DC V kademeleri)
- USB-A → micro-B kablo ×2: Power kablosu (30 cm) ve kutudan çıkan Touch kablosu (`elektrik.md:44`). Power kablosunun A ucu
  henüz kesilmemiş olmalı; kesildiyse kırmızı/siyah teller doğrudan kullanılır.
- USB-A dişi test kartı ×2 (pinleri dışarı çıkan küçük kart). Yoksa USB-A fişin içindeki pinlere ince prob.
- 5 V USB şarj adaptörü (telefon şarj adaptörü). **Pi kullanılmaz.**

USB-A fişinde pin 1 = VBUS (+5 V, genelde kırmızı tel), pin 4 = GND (siyah tel). Fişe önden bakınca pinler 1-2-3-4 sırasındadır.

## Güvenlik

- Akü ya da servo yok. Ekran camı kırılgandır: yumuşak bir bezin üstünde, yüzü aşağı çalış.
- Ölçüm sırasında ekranın HDMI'ı ve iki USB'si **Pi'ye ya da bilgisayara takılı değil**.
- Statik elektriğe dikkat: ölçümden önce topraklı metale dokun.

## Yöntem

1. Ekranda hiçbir kablo yokken Power kablosunu **Power**, Touch kablosunu **Touch** girişine tak. İki kablonun USB-A uçları boşta.
   Uçları test kartına tak ya da prob için ayır. Hangi ucun hangisi olduğunu bantla etiketle.
2. **Kontrol ölçümü:** direnç kademesinde Power-GND ↔ Touch-GND. Neredeyse 0 Ω çıkmalı (iki giriş aynı toprağı paylaşır).
   OL çıkarsa prob ya da kablo yanlış: düzeltmeden devam etme.
3. **Direnç:** Power-VBUS ↔ Touch-VBUS arası direnci oku.
4. **Diyot kademesi:** kırmızı uç Power-VBUS, siyah uç Touch-VBUS; oku. Sonra uçları ters çevir; oku.
5. **Gerilimli deneme A:** 5 V adaptörü Power kablosunun A ucuna tak (ekran açılabilir). Touch kablosunun boştaki A ucunda
   VBUS–GND gerilimini oku. Power kablosunun A ucu kesildiyse: adaptör **prizden çıkmışken** çıplak kırmızı (VBUS) ve siyah (GND)
   telleri bir USB-A dişi test kartının ya da klemensin + ve − ucuna sık, teller birbirine değmesin; ancak sonra adaptörü prize tak.
6. **Gerilimli deneme B:** adaptörü çıkar, bu kez **Touch** kablosuna tak. Power kablosunun boştaki A ucunda VBUS–GND gerilimini oku.
   (Pi'nin 5 V'unun Power hattına, yani SY8205 çıkışına geri gidip gitmediğini gösterir.)
7. Adaptörü çıkar. Ekranın arka kapağı açılabiliyorsa kartın fotoğrafını çek (açma zorunlu değil).

## Kayıt tablosu

| Adım | Ölçüm | Kademe | Okunan | Birim |
|---|---|---|---|---|
| 2 | Power-GND ↔ Touch-GND | Ω | | |
| 3 | Power-VBUS ↔ Touch-VBUS | Ω | | |
| 4 | Power-VBUS (+) → Touch-VBUS (−) | diyot | | |
| 4 | Touch-VBUS (+) → Power-VBUS (−) | diyot | | |
| 5 | Power'a 5 V; Touch ucunda VBUS–GND | DC V | | |
| 5 | Adaptör gerilimi (Power ucunda) | DC V | | |
| 6 | Touch'a 5 V; Power ucunda VBUS–GND | DC V | | |
| 6 | Adaptör gerilimi (Touch ucunda) | DC V | | |

Ekran kartının fotoğrafı: ______________________

## Geçer / kalır sınırı

| Ölçüm | GEÇER (bağlı değil) | KALIR (bağlı) |
|---|---|---|
| Adım 2, GND ↔ GND | < 1 Ω (kontrol; varsayım) | Bu adım geçmezse ölçüm geçersiz |
| Adım 3, VBUS ↔ VBUS | OL (açık devre) | < 10 Ω: doğrudan bağ (KALIR). kΩ ve üstü değer: tek başına karar değil, adım 5–6 belirler |
| Adım 4, diyot iki yön | İki yönde de OL | Bir yönde 0,1–0,8 V okunur: araya diyot konmuş |
| Adım 5 ve 6, boştaki uç | ≤ **0,5 V** (varsayım: ölçüm gürültüsü payı) | 0,5 V'tan büyük; adaptör gerilimine yakınsa doğrudan bağ |

Dört satırın hepsi GEÇER ise ekran Pi'ye tasarımdaki gibi bağlanabilir. Kaynakta sayısal eşik yok; 1 Ω, 0,5 V ve 0,1–0,8 V
(silisyum/Schottky diyot düşümü) bu kâğıdın **varsayımıdır**.

## Sınır aşılırsa

- **Touch kablosunu Pi'ye takma.** Ekran yalnız Power ile ya da yalnız Touch ile denenebilir, ikisi birden iki kaynağa değil.
- Sonuç `elektrik.md:43` maddesine işlenir ("Bağlıysa çözüm o ölçümle seçilir"); tahmini çözüm yazılmadı. Yeni madde
  `karar-kuyrugu.md`'ye, karar **Ahmet Yorulmaz**'da. Diyot okunursa hangi yönde olduğu kararı değiştirir: iki yönü de yaz.

## Sonuç

☐ GEÇER (bağlı değil)  ☐ KALIR (bağlı: ☐ doğrudan  ☐ diyotla)

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
