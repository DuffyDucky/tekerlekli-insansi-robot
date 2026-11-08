# T10 · Kafa ısı testi: kapalı kafada tilt servosu ve Pi sıcaklığı

Kâğıt T10 / 13 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Kafa kapalıyken, Pi 5 + 10,1" QLED + ses düzeni yükte uzun süre çalışırken **tilt servosunun gövde sıcaklığını**, kafa içi havayı ve
Pi'nin işlemci (SoC) sıcaklığını ölçmek. Sonuç, kafaya 30 mm egzoz fanı eklenip eklenmeyeceğine (karar kuyruğu K12) veri olur.

## Neden önemli

Kafada Pi, iki 5 V düşürücü, ekran ve yükselteç ısı verir; kafa içi sıcaklık yalnız el hesabıyla bulundu. 30 °C ortamda yarıklı kafada
hesap normal yükte 48,2 °C, yükte 50,9 °C veriyor; hesapta servonun kendi ısısı yok, sonuçlar "kesin sınır değil, karşılaştırma içindir"
(`qled-not:114-119`). Tilt servosu (MG996R) üreticiye göre en çok 55 °C'de çalışır (`P-pi-kafada.md:45`). Tasarımın kuralı: stres testinde
tilt servo gövdesi 50 °C'yi geçerse 30 mm fan eklenir (`qled-not:119`, `karar-kuyrugu.md` K12).

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Kafa içi hava, 30 °C ortam, yarıklı: normal (19,8 W) 48,2 °C, yük (22,9 W) 50,9 °C; kapalı 49,7 / 52,8 °C; fanlı 36,9–40,5 °C | `qled-not:114-117` | El hesabı; servo ısısı, alt bölme ve boyun girişi yok (`qled-not:119`) |
| Normal karşılamada kafa 12 V girişi ≈ 19,8 W (3,57 A × 5 V ÷ 0,90) | `elektrik.md:28` | Hesap, ölçülmedi |
| Fan kuralı: stres testinde tilt servo gövdesi > 50 °C → 30 mm egzoz fanı | `qled-not:119`, `elektrik.md:270`, `karar-kuyrugu.md` K12 (satır 189) | Öneri; karar açık (varsayılan: yarıklar kalsın) |
| Test şartı: kafa kapalı, stres (stress-ng + 30 kare/s animasyon), SoC ≤ 75 °C, tilt servo gövdesi ≤ 50 °C | `P-pi-kafada.md:73`, `elektrik.md:270` | Tasarım şartı |
| MG996R çalışma sıcaklığı 0…55 °C | `P-pi-kafada.md:45` (üretici datasheet'i) | Üretici |
| Pi 5: işlemci 80–85 °C arasında kendini yavaşlatır | `P-pi-kafada.md:66` (Raspberry Pi belgesi) | Üretici |
| Tilt servosu MG996R, XL4016 C hattında (pan ile birlikte) | `elektrik.md:91`, `elektrik.md:297` | Tasarım |
| Fan yeri (30 × 30 × 10) ayrıldı, parça yok; AI HAT+ zarfıyla kesişiyor | `qled-not:119`, `karar-kuyrugu.md:94` | Model |

**Ortam düzeltmesi (bu kâğıdın yöntemi, varsayım):** hesap 30 °C ortam içindir. Kafa içi sıcaklık artışı ortamdan bağımsız kabul edilir:
düzeltilmiş sıcaklık = ölçülen + (30 − ortam). Örnek: ortam 22 °C, servo 44 °C → 44 + 8 = **52 °C**. Pi'nin fanı sıcaklıkla hızlandığı için
SoC'de bu düzeltme tutucu (gerçekten biraz yüksek) sonuç verir.

## Gereken alet

- **K tipi termokupl ×3**, ince telli, en az 1,5 m (varsayım: kafadan erişim alanının dışına uzanmak için), ve okuyucu: K tipi girişli
  multimetre ya da 2–4 kanallı dijital termometre. Kızılötesi termometre kapalı kafanın içini göremez; bu testte kullanılmaz.
- Alüminyum bant (termokuplu servo gövdesine yapıştırmak için), kablo bağı
- Ortam için ayrı bir dijital termometre (termokupllardan biri de olur)
- Pi'de terminal: `vcgencmd`, `stress-ng`; yüz animasyonu programı (30 kare/s); konuşma kaydı (döngüde çalınacak)
- İsteğe bağlı: **DC akım pensi** (0,01 A) ve multimetre (kafanın 12 V gücünü hesapla karşılaştırmak için; ölçüm noktası **gövdedeki F3 sonrası kafa 12 V teli**, kafa kapalı olduğu için
  [T3](T3-kafa-5v-akim.md) N1 kullanılmaz)
- Kronometre, tekerlerin önüne ve arkasına takoz

## Güvenlik

- Testten önce **[T3](T3-kafa-5v-akim.md) GEÇER** olmalı (Pi ve ekran hatları yükte sorunsuz). Akü: ana sigorta 30 A, F1, F3, F4 ve F5 takılı (`elektrik.md:60`; F5 acil stop devresidir).
- **Kollar bu testte güç almaz:** **enerji kesikken** XL4016 A ve XL4016 B hat sigortaları (7,5 A × 2, `elektrik.md:60`) çıkarılır. Yalnız XL4016 C
  (pan + tilt) hattı takılı kalır; tilt servosu kafayı gerçek kullanımdaki gibi tutar. Kollar ev pozunda, aşağıda serbest durur.
- Motor sürücüleri de anahtarlı baradadır: yazılımda motor komutu yok (EN = 0, PWM = 0), robot düz zeminde, tekerler takozlu.
- **Kafa ve boyun enerjiliyken kimse kafaya, boyna, termokupl teline el uzatmaz** (ortak kural 7). Termokupllar **enerji yokken** takılır,
  teller kablo bağıyla hareketli parçalardan (tilt çatalı, servo kolu, pan mili) uzak tutturulur, okuyucu kafanın erişim alanının dışında
  durur (kafa erişim alanı + 0,5 m; varsayım, [T8](T8-servo-hatlari.md) ile aynı). Acil stop [00-genel.md](00-genel.md) ortak kural 1'e göre hazır (görevi yalnız mantar olan ayrı kişi; "devreden çıkar" komutu varsa düz zeminde denenmiş).
- **Durdurma kuralı:** tilt servo gövdesi **ölçülen** 55 °C'ye (üreticinin üst sınırı) ya da SoC 80 °C'ye ulaşırsa, koku, duman, ıslık
  sesi olursa test hemen durdurulur: Pi'ye uzaktan `sudo poweroff`, sonra anahtarlı bara ve enerji kesilir. Kafa 10 dk soğumadan açılmaz;
  düşürücüler sıcaktır, elle tutulmaz.
- Ses orta seviyede: uzun süre en yüksek ses çalınmaz ([T4](T4-pam8403-ses-karti.md) en yüksek seste en çok 30 s).
- Saat, yüzük, bileklik çıkar.

## Yöntem

1. **Ortam:** testi rüzgârsız, güneş almayan bir odada yap; ortam 20–30 °C arasında olmalı (varsayım: düzeltme payı ≤ 10 K kalsın).
   Ortam termometresini robottan 1 m uzağa, kafa yüksekliğine, ısı kaynağından uzak koy.
2. **Enerji yokken, kafa açıkken** termokuplları tak:
   - **TK1 tilt servosu:** servo gövdesinin yan yüzüne (servo kolu ve milin karşısındaki yüze değil, gövdenin düz yan yüzüne) alüminyum bantla;
     ucu gövdeye tam değsin.
   - **TK2 kafa içi hava:** üst bölmede, Pi soğutucusunun hava akışından ve hiçbir yüzeyden uzakta, askıda (kablo bağıyla tutturulur).
   - **TK3 ortam** (ya da ayrı termometre): adım 1'deki yerde.
   Telleri boyun kablo yolundan dışarı çıkar; havalandırma yarıklarından geçirme (yarığı kapatır, sonucu değiştirir). Kafayı tüm vidalarıyla
   kapat. Yarıklar açık, bantlanmamış; fan yok.
3. **Enerji yokken** XL4016 A ve B hat sigortalarını çıkar (güvenlik). İsteğe bağlı: akım pensini ve multimetrenin gerilim uçlarını,
   yine **enerji yokken**, gövde içinde aynı yerde (F3 sonrası kafa 12 V teli, kolların erişiminden uzak) tak; gerilim uçlarını
   klipsle sabitle, kabloları gövdeden dışarı al ki okuma kafanın ve kolların erişim alanının dışından yapılsın. Pensin ekranı dışarıdan
   okunamıyorsa okuma anında telefonla fotoğraflanır (telefon önceden tripoda kurulur); bu da olmuyorsa pens takılmaz, sütun "okunmadı".
4. Enerjiyi ver, Pi açılsın. Herkes kafanın erişim alanının dışına çıkar. Anahtarlı barayı aç: yalnız XL4016 C hattı güç alır, kafa ev
   pozunda (tilt 0) tutar. Hareket komutu verilmez.
5. Pi'de kayıt döngüsünü başlat (her 10 dk; dosya `T10-pi.log`):
   `while true; do date +%T; vcgencmd measure_temp; vcgencmd get_throttled; sleep 600; done | tee T10-pi.log`
6. **S1 normal karşılama, 60 dk:** yüz animasyonu (30 kare/s), kamera açık, ReSpeaker kaydediyor, QLED parlaklık %100, konuşma kaydı döngüde,
   sistem sesi %50 ([T3](T3-kafa-5v-akim.md) S1 ile aynı düzen). 0. dakikadan başlayarak **her 10 dk** TK1, TK2, TK3, SoC ve
   `get_throttled` yaz (pens takılıysa kafa 12 V akımı ve gerilimi de).
7. **S2 stres:** S1 biter bitmez, durdurmadan, `stress-ng --cpu 4 --timeout 120m` başlat; animasyon, kamera, ses aynı kalır. Her 10 dk oku.
   En az **60 dk** sür; son iki okuma (10 dk arayla) arasında TK1 farkı **≤ 0,5 °C** olunca dur, en çok **120 dk** (süreler varsayım:
   3D baskı kafanın ısınma süresi bilinmiyor). Kararlı olmadan 120 dk dolarsa "kararlı değil" yaz.
8. S2 sonunda `stress-ng`'yi durdur, Pi'yi kapat, anahtarlı barayı ve enerjiyi kes. Kafa 10 dk soğumadan açılmaz. Hat sigortalarını
   **enerji kesikken** geri tak.
9. Her senaryonun son okumasında düzeltilmiş değerleri hesapla: düzeltilmiş = ölçülen + (30 − ortam). Ortam olarak o senaryonun
   ortam okumalarının ortalamasını kullan.

## Kayıt tablosu

Robot: ☐ kafa kapalı, tüm vidalar  ☐ yarıklar açık  ☐ fan yok  ☐ XL4016 A/B sigortaları çıkarıldı   Termokupl fotoğrafı: ______

Tablo 1: sıcaklıklar (°C)

| Dakika | Senaryo | TK3 ortam | TK1 tilt servo gövdesi | TK2 kafa içi hava |
|---|---|---|---|---|
| 0 | S1 | | | |
| 10 | S1 | | | |
| 20 | S1 | | | |
| 30 | S1 | | | |
| 40 | S1 | | | |
| 50 | S1 | | | |
| 60 | S1 son / S2 başı | | | |
| 70 | S2 | | | |
| 80 | S2 | | | |
| 90 | S2 | | | |
| 100 | S2 | | | |
| 110 | S2 | | | |
| 120 | S2 | | | |
| 130 | S2 | | | |
| 140 | S2 | | | |
| 150 | S2 | | | |
| 160 | S2 | | | |
| 170 | S2 | | | |
| 180 | S2 (en çok) | | | |

Tablo 2: Pi ve kafa gücü (okuma her 10 dk; SoC ve `get_throttled`'ın 10 dk'lık tamamı `T10-pi.log`'dadır, burada 30 dk'da bir yazılır)

| Dakika | SoC (°C) | get_throttled | Kafa 12 V akımı (A, pens) | Kafa 12 V gerilimi (V) |
|---|---|---|---|---|
| 0 | | | | |
| 30 | | | | |
| 60 | | | | |
| 90 | | | | |
| 120 | | | | |
| 150 | | | | |
| 180 | | | | |

Özet (her senaryonun son okuması):

| Senaryo | Ortam ortalaması (°C) | TK1 ölçülen → düzeltilmiş (°C) | TK2 ölçülen → düzeltilmiş (°C) | SoC en yüksek → düzeltilmiş (°C) |
|---|---|---|---|---|
| S1 normal | | | | |
| S2 stres | | | | |

S2 kararlı mı: ☐ evet (dakika ______) ☐ hayır, 120 dk doldu   Durdurma kuralı işledi mi: ☐ hayır ☐ evet, sebep: ______

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| TK1 tilt servo gövdesi, S2 sonu, **düzeltilmiş** | **≤ 50 °C** | `qled-not:119`, `elektrik.md:270`, K12 |
| SoC, S2'de en yüksek, düzeltilmiş | **≤ 75 °C** | `P-pi-kafada.md:73`, `elektrik.md:270` |
| `get_throttled`, S2 sonu | **0x0** (düşük gerilim ve yavaşlama yok) | `oneri-taslak-v8.md:68` |
| Test sırasında durdurma kuralı (servo ölçülen 55 °C, SoC 80 °C) | **işlemedi** | `P-pi-kafada.md:45`, `P-pi-kafada.md:66` |

TK2 kafa içi hava ve kafa 12 V gücü (U × I) yalnız kayıttır: S1 normal 48,2 °C ve 19,8 W, S2 yük senaryosu 50,9 °C ve 22,9 W hesaplarıyla
karşılaştırılır (`qled-not:116-117`). Ortam üstü artış (düzeltilmiş TK2 − 30) hesabınkinden (S1 18,2 K, S2 20,9 K) %30'dan fazla saparsa
(el hesabının payı, `P-pi-kafada.md:117`) not düşülür, kalır sayılmaz.

## Sınır aşılırsa

- **Tilt servo gövdesi > 50 °C (düzeltilmiş):** sonuç `karar-kuyrugu.md` **K12**'ye veri olarak eklenir; kaynaktaki öneriye göre 30 mm egzoz
  fanı (seçenek b) gündeme gelir, karar **Ahmet Yorulmaz**'da. Fan seçilirse fan yeri AI HAT+ zarfıyla kesiştiği için taşınmalı
  (`karar-kuyrugu.md:94`): tasarım ajanına.
- **SoC > 75 °C ya da `get_throttled` ≠ 0x0:** yazılım ekibine (Efe): SoC 75 °C üstünde animasyon kare hızı düşürülür (`elektrik.md:270`).
  Düşük gerilim biti varsa [T3](T3-kafa-5v-akim.md) "Sınır aşılırsa" bölümü geçerlidir.
- **Durdurma kuralı işlediyse:** sonuç KALIR; fan kararı beklenmeden tasarım ajanına ve Ahmet Yorulmaz'a bildirilir. Fan takılmadan kafa
  kapalı uzun çalışma yapılmaz.
- Her sonuçta: ölçülen değerler `elektrik.md:28` ("Ölçülecek") ve açık iş 13 (`elektrik.md:477`) satırlarına işlenmek üzere tasarım ajanına verilir.

## Sonuç

☐ GEÇER  ☐ KALIR    Tilt servo S2 düzeltilmiş: ______ °C   SoC en yüksek düzeltilmiş: ______ °C   Ortam: ______ °C

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
