# T8 · Servo hatları: XL4016 A / B / C yükte

Kâğıt T8 / 13 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Servolar üç ayrı düşürücüden beslenir: **A** sağ kol, **B** sol kol, **C** kafa (pan + tilt); her biri 6 V'a ayarlı bir XL4016
(`elektrik.md:83-91`). Bu kâğıt üç hattın gerçekten ayrı olduğunu, yük altında gerilimin ne kadar düştüğünü, akımı ve XL4016 soğutucusunun
ısınmasını ölçer.

## Neden önemli

Hat akımları hesap: kol hatları yoğun kullanımda 4,87 A, yani XL4016 için önerilen 5 A sürekli sınırın %97'si; "sınırda kalıyor, hat akımı
ölçümü yine gerekli" (`elektrik.md:95`, `kararlar:49-51`). Gerilim çok düşerse servo resetlenir, kol düşer ya da titrer.

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Üç ayrı hat: A sağ kol (4 servo), B sol kol (4), C pan + tilt | `elektrik.md:83-91`, `kararlar:47-48` | Karar 29.10 |
| Hat gerilimi 6 V | `elektrik.md:85`, `elektrik.md:295-297` | Tasarım |
| Yoğun / tepe akım: A ve B 4,87 / 7,24 A; C 1,5 / 5,0 A | `elektrik.md:89-91` | Tahmini (`kol-analiz.json`) |
| XL4016: 8 A modül, sürekli ≤ 5 A önerilir | `elektrik.md:187` | Satıcı/önceki rapor |
| Hat sigortaları: A 7,5 A, B 7,5 A, C 5 A mini | `elektrik.md:89-91` | Tasarım |
| Servo ucunda durma akımında ~0,5 V düşüm, servo ≈ 5,5 V görür | `elektrik.md:76` | Tahmini (1,93 m uzatmayla; 1,58 m'de dirsek/bilek 1,86 m, `elektrik.md:31`) |
| Isı ölçütü: XL4016 soğutucusu ≤ 80 °C | `elektrik.md:285` | Tasarım ölçütü |
| Yük testi: 1,33 Ω / 30 W direnç (6 V'ta 4,5 A), 30 dk | `elektrik.md:284` | Tasarım yöntemi |
| Toprak: tek yıldız noktası (güç paneli) | `elektrik.md:308` | Tasarım |

## Gereken alet

- Multimetre ×2, DC akım pensi (en az 10 A)
- **1,33 Ω / 30 W** yük direnci (alüminyum gövdeli, soğutucuya vidalı) ×1
- Temaslı termometre (NTC/termokupl) ya da kızılötesi termometre
- Kronometre, küçük düz tornavida (XL4016 trimpotu)
- **Uzun test kablosu:** bilek servosu için servo Y-ara kablosu (erkek–dişi + üçüncü kol) ya da konnektöre lehimli test ucu; ölçü telleri
  **en az 1 m**, ucu krokodil ya da muzlu fiş (D bölümü)
- Robot: akü, güç paneli, XL4016 A / B / C, dağıtım kartları; kollar ve kafa servoları (son bölüm için)

## Güvenlik

- **Akü:** ana sigorta 30 A, F1 20 A ve hat sigortaları takılı. Kısa devre akü akımı çok yüksektir: ölçü ucu kayarsa iki ucu birden değdirme,
  saat ve yüzük çıkar.
- **Servo:** servo gücü verilmeden önce yazılım hedefleri son konuma yazılmış olmalı (`elektrik.md:224`); yoksa kollar ani hareket eder.
  Kolların ve kafanın erişim alanında kimse durmaz, parmak eklem aralarına girmez. Acil stop [00-genel.md](00-genel.md) ortak kural 1'e göre hazır (görevi yalnız mantar olan ayrı kişi; "devreden çıkar" komutu varsa düz zeminde denenmiş).
- **Hareket varken prob tutulmaz, kola ya da konnektöre el uzatılmaz.** Hareketli parçadaki her ölçü ucu enerji yokken bağlanır, teli erişim
  alanının dışına çıkarılır; multimetre ve pens göstergesi alan dışında okunur. Komutları veren kişi de alanın dışındadır. Erişim alanı:
  tam uzanmış kolun ulaşabileceği yer + 0,5 m (varsayım).
- **Multimetreyle akım:** [00-genel.md](00-genel.md) "Multimetreyle akım ölçümü" kuralı. Bu kâğıtta akım **pensle** ölçülür (30 dk'lık yük
  testinde multimetre seri kullanılmaz); multimetre yalnız gerilim ve direnç için, kırmızı uç V soketinde.
- **Yük direnci 27 W ısı verir:** yanar. Masaya değmesin, yanına plastik/kablo koyma, test bitince 10 dk soğumadan tutma.
- XL4016 soğutucusu 80 °C'ye yaklaşabilir: elle değme, termometre kullan.
- İlk ayar **servolar bağlı değilken** yapılır: XL4016 çıkışı ayarsız gelir, 6 V'tan yüksekse servo yanar.

## Yöntem

**A. Ayrılık (enerji yok, akü ayrık)**

1. Direnç kademesinde: A çıkışı V+ ↔ B çıkışı V+, A ↔ C, B ↔ C. Hepsi açık devre (OL) olmalı.
2. A GND ↔ B GND ↔ C GND: neredeyse 0 Ω olmalı (ortak toprak, `elektrik.md:308`).
3. Hat sigortalarını gözle: A 7,5 A, B 7,5 A, C 5 A.

**B. Boşta ayar (servolar bağlı değil)**

4. Akü bağlı, röle çekili (anahtarlı 12 V var). Her XL4016'nın çıkışında multimetreyle trimpotu çevirip **6,00 V**'a ayarla.
5. Girişteki 12 V'u ve çıkışı yaz.

**C. Yük direnciyle (`elektrik.md:284` yöntemi)**

6. Enerjiyi kes. **Servolar dağıtım kartından sökülü** (bu bölümde hiçbir servo bağlı değil). A hattının çıkışına (dağıtım kartı girişine)
   1,33 Ω / 30 W direnci bağla. Etek kapalı, ortam 25–30 °C (`elektrik.md:284`).
7. Enerji ver. 0, 5, 10, 20 ve 30. dakikada: çıkış gerilimi, çıkış akımı (pens), giriş akımı, soğutucu sıcaklığı.
8. Enerjiyi kes, direnci soğumaya bırak. B ve C hatları için 6–7'yi tekrarla. (C hattı 5 A sigortalı: 4,5 A yük sigortanın altında.)

**D. Gerçek yük (servolar takılı)**

9. **Enerji yokken:** kollar ve kafa servoları bağlı; pensi A hattının güç panelindeki çıkış kablosuna tak; bilek servosunun konnektörüne
   Y-ara kablosunu ya da test ucunu tak, ölçü tellerini kol boyunca bantlayıp erişim alanının dışına çıkar, multimetreyi (DC V, MIN tuşu)
   alanın dışına koy. Herkes alanın dışına çıktıktan sonra enerji ver. Hareket profili (komut alan dışından):
   - **D1 bekleme:** ev pozu, servolar konum tutuyor, 1 dk.
   - **D2 jest:** karşılama jesti 10 kez tekrar.
   - **D3 yoğun:** kollar öne uzanmış ve tutuyor + jest, 2 dk (`elektrik.md:179` "kol uzanmış tutuyor + hareket").
10. Her profilde en yüksek ve ortalama akımı pens göstergesinden, bilek servosundaki en düşük gerilimi multimetrenin MIN değerinden **alan dışında**
    oku. Hareket sürerken kimse kola, tele ya da konnektöre uzanmaz; tel takılırsa ya da gevşerse önce acil stop, enerji kes, sonra düzelt.
    Profil değiştirirken MIN değerini alan dışından sıfırla. Not: multimetrenin MIN yakalaması çok kısa (yaklaşık 100 ms altı) çökmeleri
    kaçırabilir; bu yüzden **asıl ölçüt servo reset / titreme gözlemidir** (adım 12), MIN değeri yardımcıdır.
11. Aynısını B hattı için yap (pens ve test ucu yine enerji yokken taşınır). C hattında: pan ve tilt sınırlar arasında 10 kez gidip gelsin (tilt ±13°, `kararlar:19`).
12. Servolardan reset, titreme, ses değişimi var mı, not al.

## Kayıt tablosu

**A. Ayrılık**

| Ölçüm | Okunan | Beklenen |
|---|---|---|
| V+ A ↔ V+ B | | OL |
| V+ A ↔ V+ C | | OL |
| V+ B ↔ V+ C | | OL |
| GND A ↔ GND B | | ≈ 0 Ω |
| GND A ↔ GND C | | ≈ 0 Ω |
| Hat sigortaları A / B / C | / / | 7,5 / 7,5 / 5 A |

**B. Boşta ayar**

| Hat | Giriş (V) | Çıkış (V) |
|---|---|---|
| A | | |
| B | | |
| C | | |

**C. Yük direnci (1,33 Ω)** Ortam: ______ °C, etek ☐ kapalı

| Hat | Dakika | Çıkış (V) | Çıkış akımı (A) | Giriş akımı (A) | Soğutucu (°C) |
|---|---|---|---|---|---|
| A | 0 | | | | |
| A | 5 | | | | |
| A | 10 | | | | |
| A | 20 | | | | |
| A | 30 | | | | |
| B | 0 | | | | |
| B | 5 | | | | |
| B | 10 | | | | |
| B | 20 | | | | |
| B | 30 | | | | |
| C | 0 | | | | |
| C | 5 | | | | |
| C | 10 | | | | |
| C | 20 | | | | |
| C | 30 | | | | |

**D. Gerçek yük**

| Hat | Profil | Ortalama akım (A) | En yüksek akım (A) | Uç servoda en düşük gerilim (V) | Reset/titreme |
|---|---|---|---|---|---|
| A | D1 bekleme | | | | |
| A | D2 jest | | | | |
| A | D3 yoğun | | | | |
| B | D1 bekleme | | | | |
| B | D2 jest | | | | |
| B | D3 yoğun | | | | |
| C | pan + tilt | | | | |

**E. Uzatma ve ana hat kısa devresi (tezgâh, kablo tablosu düzeltme turu 1: `servo-uzatmasi` ve `servo-ana-hat-16awg` istisnalarının şartı)**

Tek bir 1 m servo uzatması XL4016 A çıkışına (dağıtım kartı A çıkış 1) takılır, servo takılmaz; uzatmanın servo ucunda V+ ile GND pens ampermetreli kalın bir köprüyle **en çok 2 s** kısa devre edilir (yanmaz zemin, yangın söndürücü yanında, ölçüm bir kez). Uzatmanın ortasına temas termometresi.

E2 (ana hatlar, O-20 c): aynı deneme SV1, SV2 ve SV3'te (16 AWG, XL4016 A / B / C → dağıtım kartı A / B / C) yapılır: dağıtım kartı klemensinde V+ ile GND **en çok 2 s** kısa devre, servolar ve uzatmalar sökülü, termometre ana hattın ortasında.

| Ölçüm | Okunan | Beklenen |
|---|---|---|
| XL4016 çıkış akımı, ilk 0,5 s (pens) | | ≤ 10 A |
| XL4016 davranışı (kesiyor / akımı düşürüyor / sürdürüyor) | | kesiyor ya da düşürüyor |
| Uzatma sıcaklığı, 2 s sonra | | < 80 °C, yalıtım bozulmamış |
| E2 SV1: XL4016 A akımı / davranışı / kablo sıcaklığı | | ≤ 10 A, kesiyor ya da düşürüyor, < 80 °C |
| E2 SV2: XL4016 B akımı / davranışı / kablo sıcaklığı | | ≤ 10 A, kesiyor ya da düşürüyor, < 80 °C |
| E2 SV3: XL4016 C akımı / davranışı / kablo sıcaklığı | | ≤ 10 A, kesiyor ya da düşürüyor, < 80 °C |

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| Hatlar ayrı | V+ arası üçünde de **OL**; GND arası ≈ 0 Ω | `elektrik.md:83-91`, `elektrik.md:308` |
| C: yük direnciyle 30 dk boyunca XL4016 çıkışı | **≥ 5,85 V** | **Varsayım:** kaynakta regülatör çıkışı için eşik yok. 6,0 V ayardan en çok 0,15 V düşüş; servo ucundaki 5,5 V'a (`elektrik.md:76`) uzatma kablosunun düşümü (`elektrik.md:194`: ~0,34 V) için pay kalsın diye. Kesin ölçüt D'deki servo ucu |
| XL4016 soğutucusu, 30. dk | **≤ 80 °C** | `elektrik.md:285` |
| D3 yoğun profilde hat ortalama akımı | **≤ 5,0 A** | `elektrik.md:187` |
| D: bilek servosu ucundaki en düşük gerilim | **≥ 5,5 V** | `elektrik.md:76` (servo ucunda varsayılan gerilim) |
| D'de servo reset/titreme | **0** | Gözlem |
| E / E2: uzatma ve SV1–SV3 kısa devresinde XL4016 akımı ve kablo sıcaklığı | XL4016 **≤ 10 A'de kesiyor ya da düşürüyor**; kablo **< 80 °C** | `planlama/adim3/kablolar.json` `kesit_kurali.istisnalar` (servo-uzatmasi ve servo-ana-hat-16awg şartları); XL4016 çip sınırı 10 A tipik (XLSEMI veri sayfası Rev 1.2, `koruyucular`) |

Ölçülen yoğun akım hesaptan (A/B 4,87 A, C 1,5 A) farklıysa değer `elektrik.md:89-91` tablosuna işlenir; sınırın altındaysa kalır sayılmaz.

## Sınır aşılırsa

- **Hat > 5 A sürekli:** kaynakta yazan çözüm "o hat için 20 A düşürücü" (`elektrik.md:95`, `elektrik.md:189`); karar **Ahmet Yorulmaz**'da,
  maliyet `planlama/maliyet.json` (P8.1).
- **Soğutucu > 80 °C:** önce fan + etek yarıkları, yine aşılırsa servo hattı 20 A modüle (`elektrik.md:285`). Fan kalemi P8.1.
- **C'de çıkış < 5,85 V:** XL4016 yükte gerilim tutamıyor; D yine yapılır, karar D'nin servo ucu sonucuyla verilir. Tasarım ajanına.
- **D'de servo ucu < 5,5 V ya da servo reset:** uzatma kablosu kesiti (22 AWG, `elektrik.md:194`) ve dağıtım kartı kondansatörü (2200 µF, `elektrik.md:192`)
  tasarım ajanına.
- **E / E2 kalırsa (XL4016 kesmiyor ya da kablo ısınıyor):** ilgili istisna (`servo-uzatmasi` / `servo-ana-hat-16awg`) düşer; çıkışta hat sigortası ya da kalın kablo, orkestratöre (O-20'de çıkış sigortası kolu düşürme riski yüzünden seçilmemişti).
- **Hatlar ayrı değil (V+ arası bağlı):** kablolama hatası; enerji verme, kabloyu `elektrik.md` blok şemasına (`elektrik.md:295-297`) göre düzelt.

## Sonuç

☐ GEÇER  ☐ KALIR    A en yüksek: ______ A   B en yüksek: ______ A   C en yüksek: ______ A   Soğutucu en sıcak: ______ °C

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
