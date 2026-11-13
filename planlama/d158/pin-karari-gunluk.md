# Pin kararı günlüğü (P10.7 ön koşulu: ESP32 pin haritası), 13–14.11.2026

Ajan A. Kapsam: pano #8'deki pin haritası sorusunun kesin cevabı (Ahmet 13.11.2026 gecesi kararı bize bıraktı: "kararını sen
oluşturabilirsin, projede ona uyarız"), Efe için rapor, `elektrik.md` pin planının hizalanması, pano mesajı taslağı (depo dışında,
gönderilmedi). **Sürüm 1 sonucu (§1–§4): Efe'nin tarafının önerisi (K1 → GPIO16, K2 → GPIO17) aynen alınmıştı. Bağımsız kontrol
(`pin-karari-kontrol.md`) iki durdurucu bulgu verdi; düzeltme turu 1'de (§8) röleler GPIO4 / GPIO19'a, 16 / 17 enkodere alındı. İkinci kontrol (`pin-karari-kontrol-2.md`) pinleri onayladı;
düzeltme turu 2'de (§9) gate 4,7 kΩ, MOSFET şartı, IS bölücüsü ve UART / çekirdek kuralları geldi (rapor sürüm 3).** §1–§4 sürüm 1'in
kaydıdır; §5–§6 düzeltme turu 1'e göre güncellendi; §7 sürüm 3'e göre baştan yazıldı (C adımı yalnız onu kullanır). Commit, push, `git add` yok; panoya yazılmadı.
Dosya adı `F10*` kalıbında değil: o kalıp aynı anda çalışan rehber ajanının (F10g) alanı.

## 1. Komutlar ve okunanlar

| Saat | Ne | Sonuç |
|---|---|---|
| 13.11 23:58 | `git status`, dal `lale-duzeltme`, HEAD `9145164` | Çalışma ağacında başka ajanın değişiklikleri (rehber, freecad, karar kuyruğu, döngü); hiçbirine dokunulmadı |
| 23:58 | `planlama/adim3/elektrik.md` tamamı (517 satır), `PROTOKOL.md` | – |
| 23:59 | `git show origin/main:kod/esp32/include/pinler.h`, `motorlar.cpp`, `main.cpp`, `servolar.cpp`, `platformio.ini`, `kod/robot/seri.py`, `kod/jestler/kanallar.yaml` (`main` = `origin/main` = `2be1c63`) | Kod değiştirilmedi, dal değiştirilmedi |
| 23:59 | Pano: `oku 8`, `oku 5`, `oku 6`, `oku 7` (`--tumu`) | Okundu işaretlendi (#20, #21, #22, #23'e kadar). Yazma yok |
| 14.11 00:00 | Espressif belgeleri indirildi (geçici klasör, depoya alınmadı): ESP32 Series Datasheet v5.3, WROOM-32E v2.1, WROOM-32D v2.8, WROVER-E v2.4, SoC Errata v3.1; Infineon IRLZ44NPbF | Metne çevrilip okundu; IO_MUX tablosu (Ek A.4, s. 69, döndürülmüş sayfa) kelime koordinatlarından satır satır yeniden kuruldu |
| 00:01–00:05 | Satıcı sayfaları: Robocombo ESP32 (MJ "Alt kontrolcü"), Robotistan BTS7960B (MJ "Motor sürücü"); ESP-IDF GPIO sayfası (v6.1) | §2 |
| 00:05 | `grep "elektrik.md" --include=*.py` ve `.md` okuyan betik taraması | Aşağıda §4 |
| 00:09–00:15 | `pin-haritasi.md` yazıldı, JSON bloğu `json.loads` ile denetlendi (24 pin, tekrar yok, ASCII), `elektrik.md` düzenlendi | – |

## 2. Neye dayandım (ölçüm değil, belge)

Bu pakette **hiçbir donanım ölçülmedi** (kart yok). Olgular:

- **Strapping:** GPIO0 pull-up, GPIO2 pull-down, MTDI (12) pull-down, MTDO (15) pull-up, GPIO5 pull-up (DS Tablo 3-1). MTDI = 1 → VDD_SDIO 1,8 V
  LDO (DS §3.2). MTDO = 0 → ROM açılış yazısı kapalı (Tablo 3-4). GPIO5 ve MTDO yalnız SDIO slave zamanlaması (Tablo 3-5). GPIO0 = 1 iken
  GPIO2 önemsiz, GPIO0 = 0 iken GPIO2 = 0 olmalı (Tablo 3-3).
- **Reset durumu (IO_MUX "At Reset / After Reset"):** 25, 26, 27, 32, 33: oe=0 ie=0 / aynı. 16, 17, 18, 19, 21, 22, 23: oe=0 ie=0 / ie=1.
  13 (MTCK): ie=0 / ie=1 wpd. 14 (MTMS): ie=0 / ie=1 wpu. 12 (MTDI), 2, 4: wpd / wpd. 15 (MTDO), 0, 5, 1, 3: wpu / wpu. 34–39: ie=0.
  Reset sırasında bütün çıkışlar kapalı (Tablo 6-1 not 9); sonra Function 0 (not 10). Dahili çekme 45 kΩ tipik (Tablo 5-3).
- **Modüller:** WROOM-32E N4R2 / N8R2 / N16R2'de IO16 paket içi PSRAM'e bağlı (W32E pin notu 3, Tablo 1); WROVER-E'de pin 27 / 28 NC (Şekil 5);
  WROOM 18,0 × 25,5 mm, WROVER-E 18,0 × 31,4 mm.
- **Errata:** [GPIO-3.11] ADC1 / ADC2 / AMP açılırken GPIO36 ve 39 ~80 ns LOW; [GPIO-3.14] aynı gruptaki kenar kesmesi başka kesmeyle birlikte güvenilir değil.
- **ADC2 Wi-Fi açıkken kullanılamaz** (IDF). 32 / 33 / 36 ADC1 (DS Tablo 2-1).
- **IRLZ44N VGS(th) 1,0–2,0 V** (Infineon). Alınacak parça VBsemi "IRLZ44NPBF-VB" (MJ): onun belgesi bulunamadı, eşiği **doğrulanmadı**.
- **Kart:** Robocombo sayfası "30 pin, CP2102", çip "ESP32-D0WDQ6"; modül, PSRAM, LED pini, pin diyagramı yazmıyor.
- **BTS7960B kartı:** Robotistan sayfası "VCC +5 VDC, IS1 / IS2 akım test, EN1 / EN2 PWM girişleri, IN1 / IN2 yön"; lojik seviye ve tampon yazmıyor.
- **Hesap (ölçüm değil):** eski firmware 16 / 17'yi `INPUT_PULLUP` yaparsa gate ≈ 3,3 × 10 / 55 ≈ 0,6 V.
- **Bulamadıklarım:** BTS7960 IS hata akımı (IIS(lim)) değeri (Infineon datasheet'inin tam metnine erişilemedi); WROOM modüllerinin flaş
  geriliminin 3,3 V olduğunu açık yazan cümle (yalnız WROVER-E tablosunda VDD_SDIO 3,3 V var); 30 pinli kartın üretici pin belgesi.

## 3. Karar özeti

Kesin tablo `planlama/adim3/pin-haritasi.md` §2. Eski plandan fark: K1 12 → 16, K2 2 → 17, 2 yalnız LED, 12 boş. Efe'nin önerisinden fark yok.
Ek: sonar trig PCA9685 kanalları 10 sağ / 11 orta / 12 sol (önce yazılı değildi). PCA9685 servo kanalları `main` `2be1c63` `kanallar.yaml`
ile aynı (değişmedi); pano #6 mesaj #21'deki "0–5 aynen, 6–9 …" cümlesi bu düzenle çelişiyor, Efe'ye soru olarak taslağa girdi.

## 4. `elektrik.md`'yi okuyan betik var mı

`grep -rn "elektrik.md" --include=*.py`: eşleşmelerin hepsi yorum ya da rapor metni içinde yol adı (ör. `arayuz.py`, `rehber_metin.py`,
`taban_rapor.py`, `uygulama_rapor.py`); dosyayı açıp ayrıştıran üretici ya da doğrulama betiği yok. `planlama/adim2/K2-regresyon.py`
depodaki bütün `.md` dosyalarını eski S2 sınırı kalıpları için tarıyor (`yana 0`, `3…120` vb.); yeni metinde bu kalıplar yok.
Bu yüzden `elektrik.md` doğrudan düzenlendi.

**Değişen yerler:** satır 5 (pin planı kesinleşti), v4 muadilleri BTS7960B adları, 1,65 m tablosu "Acil stop" ve "Yedek GPIO" satırları
(tarihçe, yalnız not), "Özet" E3 satırı, E3 şeması ve metni (GPIO12 → GPIO16, açılış gerekçesi), E9 şeması, dizisi ve GPIO2 paragrafı
(→ 16 / 17), "Pin planı" bölümü (başlıkta "taslak" kalktı, tablo `pin-haritasi.md` ile aynı, PCA9685 sonar sırası), açık işler 4 ve 19.
**Satır kayması:** "Pin planı" bölümü 5 satır uzadı ve E9'daki GPIO2 paragrafı 1 satır uzadı; 458'den sonraki satır numaraları +1,
pin planından sonrakiler +6 kayar. Başka belgelerdeki `elektrik.md:4xx-5xx` atıfları (ör. `testler/T3`, `T7`, `T10`, `F8c-kontrol.md`) zaten
eski numaralardı; düzeltilmedi.

## 5. Bu pinleri anan, tutarsız kalan belgeler (düzeltilmedi; listelendi)

| Yer | Ne yazıyor | Yeni karar | Kimin işi |
|---|---|---|---|
| `kod/esp32/include/pinler.h` (`main`) | eski kod tablosu (32 / 33 PWM, 27 / 13 EN, 16 / 17 enkoder) | `pin-haritasi.md` | Efe (`pinler.json` → `pinler.h`) |
| `planlama/yazilim-plani.md:33` | K1 GPIO12, K2 GPIO2 | 4, 19 | yazılım planı güncellemesi |
| `planlama/yazilim-plani.md:34` | Nextion UART2 (GPIO17 / 16) | Nextion 25.10'da çıktı (aynı dosyanın 124. satırı, `maliyet.json:21`, `elektrik.md:26`); 16 / 17 enkoder, UART2 kullanılmaz | aynı |
| `planlama/yazilim-plani.md:53, 58-59` | GPIO12 / GPIO2 dizisi | 4 / 19 | aynı |
| `planlama/d158/testler/T13-rampada-acil-stop.md:64, 81` | "GPIO12'yi 0 yapar", "reset anında GPIO12 LOW" | GPIO4 | test kâğıdı (ve `testler.html` üretimi) |
| `planlama/d158/testler/T4-pam8403-ses-karti.md:72` | "GPIO12 = 0" | GPIO4 = 0 | aynı |
| `planlama/maliyet.json:106, 109` (notlar) ve onu gömen `tasarim/Robot-Tasarim-Demosu.html:399` | "K2 için (GPIO2)", "IRLZ44N ile GPIO2" | GPIO19 | maliyet notu (demo yeniden üretilir) |
| `planlama/adim5/B-malzeme-plan.md:44` | K2 "GPIO2" | GPIO19 | tarihçe notu yeter |
| `planlama/adim3/K3-kontrol.md:49-50, 67`; `planlama/y2/Y2b-*`; `planlama/kararlar-2026-10-29.md:68`; `F5b`, `F7c`, `F8c`, `F8d` kontrol / günlükleri; `dongu-158.md:242, 263` | GPIO12 / GPIO2 o günün kararı | – | tarihçe, değişmez |
| **Rehber (yalnız listelendi, P10.7):** `tasarim/freecad/rehber/rehber_metin.py:637` → `rehber/veri/rehber-veri.json:10879`, `rehber-veri.js` | "K2'yi süren GPIO2 kartın LED pini …, LED yakıp söndüren hazır bir program K2'yi açıp kapatabilir" | Artık K2 GPIO19; uyarı geçersiz, yerine "yalnız `pin-haritasi.md`'ye göre yazılmış firmware yüklenir" | kablolama paketi P10.7 |

Rehberde başka GPIO numarası geçmiyor (`GPIO[0-9]+`, `IO1x`, `RX2/TX2` taraması: yalnız bu tek GPIO2). Rehberin E3 / E9 dizi metni
(`rehber_metin.py:1265-1268`) pin numarası anmıyor, PC817 #2 ve röle sırasıyla yazılmış; yeni kararla çelişmiyor.

## 6. Açık kalanlar

- Kart gelmeden doğrulanamayanlar (`pin-haritasi.md` §7 T1–T8): modül türü (PSRAM'siz WROOM varsayımı), röle gate gerilimleri, EN kilidi,
  BTS7960B kartında EN / IN ↔ INH / IN eşlemesi ve 3,3 V lojik, PC817 çıkışı, IS gerilimi (hata akımı değeri bulunamadı), enkoder çıkış türü,
  kart LED'i.
- VBsemi IRLZ44NPBF-VB kullanılmayacak (sürüm 3, D9): yerine mantık seviyeli SOT-23 MOSFET (öneri AO3400A + SOT-23 adaptörü);
  seçilen parçanın kesin çekme / bırakma davranışı T2'de ölçülür. Satıcı ve stok doğrulanmadı.
- PCA9685 kanal düzeni için Efe'nin teyidi (pano taslağındaki soru).
- Pi'den ESP32'yi bilerek resetleme hattı (pano #7 madde 5): pin kararına girmedi; Pi pini + boyundan yeni tel (K14 demeti).
- Sürüm 1 ve 2 bağımsız kontrolden geçti (`pin-karari-kontrol.md`, `pin-karari-kontrol-2.md`, ikisi de DÜZELTME GEREKLİ); sürüm 3 üçüncü kontrolde GEÇER (`pin-karari-kontrol-3.md`); küçük bulguları C adımında kapatıldı (§10). Güncel açıklar §9.3 ve §10.3.

## 7. Kayda girecek (sürüm 3; C adımı yerleştirir; `karar-kuyrugu.md` ve `dongu-158.md` bu pakette değiştirilmedi)

Bu bölüm düzeltme turu 2'de (§9) sürüm 3 tablosuyla baştan yazıldı; C adımı yalnız buradaki metinleri kullanır. §8.4'teki eski girdi
geçersizdir.

**Karar kaydı önerisi (`karar-kuyrugu.md`, yeni madde):**

> | K58 | ESP32 pin haritası (pano #8) | kapandı (14.11; Ahmet 13.11 "kararını sen oluşturabilirsin, projede ona uyarız") | — | P10.7 |
>
> ## K58 · ESP32 pin haritası
> Soru: `pinler.h` (`main`) ile `elektrik.md` pin planı aynı pinlere farklı iş veriyor (pano #8, mesaj #19). Efe'nin tarafı (#20): plan esas, K1 → 16,
> K2 → 17. Karar (Ahmet'in 13.11.2026 yetkilendirmesiyle, 14.11, rapor sürüm 3): `elektrik.md` planı + **K1 GPIO4, K2 GPIO19**, sağ enkoder A GPIO16,
> sol enkoder B GPIO17, GPIO2 yalnız LED, GPIO12 boş; sonar trig PCA9685 10 / 11 / 12 = sağ / orta / sol. Efe'nin 16 / 17 önerisinden sapıldı:
> 17 Arduino 2.0.17'de `Serial2` TX varsayılanı, 16 / 17'yi çekirdek açılışta PSRAM yoklamasıyla sürer (kontrol D1 / D2). Röle kuralı: röle yalnız
> açılış kodunun ve varsayılan çevre biriminin sürmediği, reset boyunca LOW kalan pinde. Firmware: `Serial1` / `Serial2` hiçbir çekirdek sürümünde
> varsayılan pinlerle açılmaz (3.x'te RX2 = 4); çekirdek espressif32@6.9.0'da sabit, 3.x'e geçiş rapor gözden geçirilmeden yapılmaz. Donanım:
> gate pull-down 4,7 kΩ; röle MOSFET'i gerçek mantık seviyeli (VGS(th) ≤ ≈ 2 V, RDS(on) 2,5 V'ta tanımlı; ör. AO3400A), listedeki VBsemi
> IRLZ44NPBF-VB değişecek; 16 / 17'ye 1 kΩ seri; 32 / 33'e diyotsuz IS bölücüsü (kart IS direnci ölçülünce; 500 Ω için 6,8 kΩ / 5,1 kΩ).
> Efe'nin itiraz hakkı açık (pano #8). Kaynak: `planlama/adim3/pin-haritasi.md`, `planlama/d158/pin-karari-gunluk.md`,
> `planlama/d158/pin-karari-kontrol.md`, `pin-karari-kontrol-2.md`, `pin-karari-kontrol-3.md`. Pano #8'e bilgi + soru mesajı (taslak hazır; Ahmet'in insan oturumu
> teyidi ve commit sonrası).

(Madde numarası K58 öneridir; kuyrukta K57'den sonra boş numara ne ise o kullanılır.)

**Paket satırı önerisi (`dongu-158.md` §3):**

> | P10.6b | Pin haritası kararı ve raporu (Ahmet 13.11 yetkilendirmesi): `planlama/adim3/pin-haritasi.md` sürüm 3, `elektrik.md` pin planı, pano #8 bilgi taslağı | Her pin Espressif belgesi ve Arduino-ESP32 2.0.17 / 3.x, ESP-IDF 4.4.7 / 5.1.4 kaynağıyla sınanmış; kod ↔ plan ↔ öneri ↔ yeni farkı; firmware ve donanım şartları (4,7 kΩ gate, mantık seviyeli MOSFET, IS bölücüsü); `pinler.json` önerisi | P10.6 cevabı (#20) sonrası | 🔄 A sürüm 3 (düzeltme turu 2) bitti |
>
> P10.7 satırındaki "⛔ (pin kararı)" → "⛔ (K10 / K11 / K14)" (pin kararı commit sonrası kalkar).

**Döngü günlüğü girdisi önerisi (`dongu-158.md` günlük; tek girdi, eski 00:15 / 00:45 girdileri kullanılmaz):**

> - 2026-11-14 01:15 Pin kararı (Ahmet 13.11 gecesi kararı bıraktı; iki bağımsız kontrol ve iki düzeltme turu sonrası sürüm 3): K1 GPIO4, K2 GPIO19, sağ enkoder A GPIO16, sol enkoder B GPIO17, GPIO2 LED, GPIO12 boş; sonar trig PCA9685 10 / 11 / 12. Efe'nin 16 / 17 önerisinden sapma: 17 = Arduino 2.0.17 `Serial2` TX, 16 / 17 açılışta PSRAM yoklamasıyla sürülüyor (kaynak koddan doğrulandı). Firmware: `Serial1` / `Serial2` varsayılan pinlerle açılmaz (3.x'te RX2 = 4), çekirdek 2.0.17'de sabit. Donanım: gate pull-down 4,7 kΩ, mantık seviyeli röle MOSFET'i (VBsemi klonu değişecek; ör. AO3400A), 16 / 17'ye 1 kΩ seri, 32 / 33'e diyotsuz IS bölücüsü. `pin-haritasi.md` sürüm 3, `elektrik.md` pin planı; pano taslağı depo dışında. C adımında: `baski-listesi.md:286` (ve `F4c-partiler.py:127`) `elektrik.md:499` → 505.

**C adımında düzeltilecek:**

- **`planlama/baski-listesi.md:286`** `elektrik.md:499` → **`elektrik.md:505`** (açık iş 2 "Kabuk", E7 etek yarıkları). Satırı üreten
  `planlama/d158/F4c-partiler.py:127` aynı düzeltmeyi ister (çıktıları `F4c-partiler.md:127`, `F4c-partiler.json:2275`). Betik bu pakette
  koşulmadı. `elektrik.md` 522 satır; düzeltme turu 1 ve 2'de satır sayısı değişmedi, kayma yalnız sürüm 1'den (+6).
- **Malzeme / değiştirilecek parça (`maliyet.json`'a bu pakette dokunulmadı):**
  - MJ:106 "Röle sürücü MOSFET" VBsemi IRLZ44NPBF-VB ×2 → **değiştirilecek** (eşik belgesiz; D9). Öneri AO3400A ×2 (+ yedek), ikinci seçenek
    IRLML6344; ikisi de SOT-23 → 2 adet SOT-23 → DIP adaptör kartı eklenir. Satıcı / fiyat / stok doğrulanmadı.
  - Gate pull-down 4,7 kΩ ×2, IS bölücüsü 6,8 kΩ ×2 + 5,1 kΩ ×2 (gerekirse 2,2 kΩ ya da 470 Ω), enkoder seri 1 kΩ ×2: mevcut direnç setinden
    (MJ:115; satıcı sayfasında 470 Ω, 1 / 2,2 / 4,7 / 5,1 / 6,8 kΩ var, onar adet).
  - Sürüm 2'deki "1N5819 + 2 adet" notu **kaldırıldı** (diyotsuz bölücü seçildi).
  - MJ:106 ve :109 notlarındaki "GPIO2" atfı → GPIO19 (§5).
- **Rehber (P10.7, yalnız listelendi):** `rehber_metin.py:637` uyarısı artık K2 = GPIO19 için değişir; kablolama paketi arayüz kartına iki
  4,7 kΩ gate direnci, iki SOT-23 MOSFET, 16 / 17'deki iki seri 1 kΩ ve 32 / 33'teki iki bölücüyü almalı; `elektrik.md:268`'deki MOSFET şartı.

## 8. Düzeltme turu 1 (14.11.2026 00:30–00:45)

Girdi: bağımsız kontrol `planlama/d158/pin-karari-kontrol.md` (DÜZELTME GEREKLİ: D1, D2 durdurucu; N1–N9). Yön (orkestratör, Ahmet'in
yetkisiyle): röleler hiçbir açılış kodunun ve varsayılan çevre biriminin sürmediği, reset boyunca kendiliğinden LOW kalan pinlere; yanlış
modül ya da program en kötü bir girişi bozsun. Kontrolün önerisi (K1 → 4, K2 → 19, sağ enkoder A → 16, sol enkoder B → 17) olduğu gibi
alınmadı, aynı ölçütle sınandı.

### 8.1 Okunanlar (kaynak kod; geçici klasöre indirildi, depoya alınmadı)

| Saat | Ne | Sonuç |
|---|---|---|
| 00:30 | Arduino-ESP32 `2.0.17` etiketi: `cores/esp32/HardwareSerial.h`, `esp32-hal-misc.c`, `esp32-hal-psram.c`, `esp32-hal-gpio.c`, `esp32-hal-spi.c`, `esp32-hal-matrix.c`, `libraries/SPI/src/SPI.cpp`, `variants/esp32/pins_arduino.h`, `tools/sdk/esp32/sdkconfig` | D1, D2 doğrulandı (aşağıda) |
| 00:32 | ESP-IDF `v4.4.7` `components/esp_hw_support/port/esp32/spiram_psram.c`, `components/esp_rom/include/esp32/rom/gpio.h` | D2 yolu doğrulandı |
| 00:35 | `nextion` adı için depo taraması; `planlama/maliyet.json`, `yazilim-plani.md`, `elektrik.md` | Nextion tasarımda yok (§8.3) |
| 00:36 | ESP32 Datasheet v5.3 §3 metni ("Joint Download Boot": SDIO + UART) | İndirme kipinde SDIO slave pinleri (4 dahil) ROM'un elinde olabilir; ne yaptığı belgede yok → T2 |

### 8.2 Bulgu başına yapılan

| Bulgu | Doğrulama | Yapılan |
|---|---|---|
| **D1** 17 = `Serial2` TX | `HardwareSerial.h:167-179`: ESP32'de RX2 = 16, TX2 = 17 (2.0.17) | K2 17 → **19**. Y1'e "`Serial2` / UART2 hiç açılmaz"; §3.1'deki yanlış "17 hiçbir hazır programın dokunduğu pin değil" cümlesi kaldırıldı |
| **D2** PSRAM yoklaması 16 / 17'yi sürer | `sdkconfig:683` `CONFIG_SPIRAM=y`, `:684` `BOOT_INIT` kapalı, `:730-731` CLK 17 / CS 16; `esp32-hal-misc.c:246` `initArduino` → `psramInit()`; `esp32-hal-psram.c:59-75` (D2WD / PICO-D2 hariç `esp_spiram_init()`, başarısızsa 16 / 17 `pinMatrixOutDetach`); `spiram_psram.c:860-863` D0WDQ6 / Q5 → CS 16, CLK 17, CLK `SPICLK_OUT`'a bağlanır; `:583` `GPIO_OUTPUT_SET(CS, 1)`, `:608` CS `SPICS1_OUT`'a | K1 16 → **4**. 16 / 17'ye yalnız giriş (enkoder) ve **1 kΩ seri** (D6). §1, §2, §4'teki "firmware'e kadar yüzer" cümleleri düzeltildi; `elektrik.md:259` aynı |
| Aday sınaması | `esp32-hal-spi.c:194` SCK `OUTPUT`, `:232` MISO `INPUT`, `:270` MOSI `OUTPUT`; `SPI.cpp:93-101` VSPI 18 / 19 / 23 / 5, HSPI 14 / 12 / 13 / 15; `pins_arduino.h` T0 = 4, DAC 25 / 26, I2C 21 / 22 | 4 (wpd / wpd, strapping değil, sürücü yok) ve 19 (yüzer, MISO = giriş) ölçütü geçti; 18 / 23 (SPI çıkış), 21 / 22, 5 / 14 / 15 (wpu), 12 / 2 (strapping), 25–27 (motor PWM'ini 16 / 17'ye taşır) elendi. Tablo `pin-haritasi.md` §3.1. 12'yi kullanan üç işlik seçenek reddedildi (röle strapping pinine döner). Kontrolün önerisi aynen alındı; sapma yok |
| Enkoder seri direnci | Hesap: 3,3 V / 1 kΩ ≤ 3,3 mA; açık kollektörde LOW ≈ 0,07 V (45 kΩ pull-up ile) | İtme-çekme ve açık kollektör için aynı: 16 ve 17'de 1 kΩ zorunlu (D6, `elektrik.md` pin tablosu) |
| **N1** IS 4–7 mA | Kontrolün aktardığı Infineon değeri (BTS §4.4.7); kendi indirdiğim BTS7960 PDF'inde tam metin yoktu, değeri kontrol raporundan aldım | D7 "her durumda": 1 kΩ seri + 3V3'e 1N5819; ölçek direnci RIS ölçülünce. T6 "her durumda". Malzeme: 1N5819 + 2 (kayda girecek) |
| **N2** satır atıfları | `kanallar.yaml` 61–73; EL PCA satırı 494 | Rapor ve pano taslağında düzeltildi. `elektrik.md` bu turda satır sayısı değişmeden düzenlendi (522), 494 doğru kalır |
| **N3** satır kayması | `baski-listesi.md:286` ve `F4c-partiler.py:127` hâlâ `elektrik.md:499` (boş satır); hedef 505 (açık iş 2 "Kabuk"), bu turda kayma yok | Betik koşulmadı; §8.4'te kayda girecek |
| **N4** modül / T1 | W32D çip D0WD; W32E D0WD-V3 / D0WDR2-V3, PSRAM'li yalnız R2 | §1 yeniden yazıldı (D0WDQ6 ⇒ eski WROOM-32 ya da eski WROVER); T1'e `esptool.py chip_id` (paket, revizyon, PSRAM) ve ER [RES-3.4] eklendi. T1 artık işlev şartı |
| **N5** 0,6 V tipik | DS yalnız tipik 45 kΩ; ~75 µA ile ≈ 0,75 V | §3.1'de iki değer ve "VBsemi eşiği doğrulanmadı"; eski firmware'in 32 / 33'ü PWM sürmesi yazıldı. Yeni tabloda eski firmware 4'e dokunmaz: K1 0 V. Pano gövdesinden 0,6 V iddiası çıkarıldı |
| **N6** Y2 ve 3.x | – (kontrolün 3.0.7 atfı; ben 3.x kaynağını okumadım) | Y2: 2.0.17 ve 3.x için ayrı sıra, `gpio_set_level` seçeneği; "bu sıra açılış öncesini korumaz" notu |
| **N7** GPIO14 darbesi | Espressif'te kaynak bulunamadı | §2 notu "topluluk gözlemi, kaynaksız"; T3'te osiloskopla bakılır |
| **N8** §6.1 cümlesi | – | Kontrolün önerdiği açık cümle yazıldı |
| **N9** pano taslağı | – | Takma ad çıkarıldı; gövde 3148 → 2412 karakter; sapma ve itiraz hakkı açıkça; #21'in pano #6'da olduğu yazıldı; `--kaynak` satırları satır numaralı (`motorlar.cpp:205-208`, `kanallar.yaml:61-73`, Arduino / IDF dosyaları); "Ahmet'in insan oturumu teyidi önerilir" notu taslağa girdi |
| T2 | – | Osiloskop / mantık analizörü, EN tetikli, ≥ 2 s; normal açılış, USB, **indirme kipi** ve yükleme, boşta, `arm` / `birak`; ölçüt "hiçbir anda > 0,5 V" |

Dört yer aynı: `pin-haritasi.md` §2 tablosu, §9 JSON (`json.loads` geçti, ASCII, 24 pin, tekrar yok), `elektrik.md` pin planı (466–496) ve
pano gövdesindeki tablo satırı; karşılaştırma betikle yapıldı (geçici klasörde), fark yok.

### 8.3 Nextion

Tasarımda yok: 25.10.2026'da çıktı, göğüs ekranı 11,6" HDMI + USB dokunmatik, Pi'den sürülür (`elektrik.md:26`, `maliyet.json:21`,
`yazilim-plani.md:124`, `siparis-farki-2026-10-29.md:35`). Depo kökündeki `nextion/` klasöründe yalnız boş `lale-deneme/` alt klasörü var
(izlenmiyor). Pin gerekmez. `yazilim-plani.md:34` (UART2 17 / 16) ve `:84` (Y10 Nextion sürücüsü) eski atıf: §5 tablosunda.

### 8.4 Kayda girecek / C adımında düzeltilecek

**Sürüm 2 metni; geçersiz.** Güncel kayda girecek metinler ve C adımı listesi §7'de (sürüm 3).

- **`planlama/baski-listesi.md:286`** `elektrik.md:499` → **`elektrik.md:505`** (açık iş 2 "Kabuk", E7 etek yarıkları). Satırı üreten
  `planlama/d158/F4c-partiler.py:127` aynı düzeltmeyi ister (çıktıları `F4c-partiler.md:127`, `F4c-partiler.json:2275`). Betik bu pakette
  koşulmadı. Kayma sürüm 1'den (+6); bu tur ek kayma yok.
- **Malzeme:** 1N5819 + 2 adet (IS koruması, D7; MJ:114'teki 1 adet VBUS içindir). 1 kΩ dirençler mevcut direnç setinden (MJ:115).
  Arayüz kartına iki seri 1 kΩ (16, 17) ve iki 1 kΩ + diyot (32, 33).
- **K58 metni** §7'de güncellendi (K1 4, K2 19, sapma ve gerekçe).
- **Rehber (P10.7, yalnız listelendi):** `rehber_metin.py:637` uyarısı artık K2 = GPIO19 için değişir; kablolama paketi arayüz kartına
  yukarıdaki dört direnç / iki diyodu ve 4 / 19 gate bağlantısını almalı.
- **Döngü günlüğü girdisi önerisi:**

> - 2026-11-14 00:45 Pin kararı düzeltme turu 1: bağımsız kontrol D1 (17 = `Serial2` TX) ve D2 (Arduino-ESP32 2.0.17 PSRAM yoklaması `setup()`'tan önce 16 / 17'yi sürer) kaynak koddan doğrulandı. Röleler GPIO4 (K1) / GPIO19 (K2), 16 / 17 enkodere (sağ A / sol B) alındı; Efe'nin önerisinden sapma, pano taslağında gerekçe ve itiraz hakkıyla. Ekler: 16 / 17'ye 1 kΩ seri, 32 / 33'e IS koruması (BTS IIS(lim) 4–7 mA), T1 esptool, T2 osiloskopla ve indirme kipinde. `baski-listesi.md:286` atfı 505'e düzeltilecek. İkinci kontrol bekliyor.

### 8.5 Açık kalan

- İndirme kipinde ROM'un GPIO4'e (SDIO DATA1) ne yaptığı: belge yok, T2 ölçer. Sorun çıkarsa K1 için sıradaki aday yok (hepsi elendi);
  o durumda karar Ahmet'e döner.
- PSRAM yoklama darbesinin süresi ölçülmedi (artık röleyi ilgilendirmiyor; enkoder seri direnci bu yüzden).
- BTS IIS(lim) değeri kontrolün aktarımı; Infineon tam metnini ben açamadım.
- Arduino-ESP32 3.x davranışı (N6) yalnız kontrolün atfıyla; 3.x kaynağını okumadım.
- Sürüm 2'nin bağımsız kontrolü yok; Efe'nin itirazı ve Ahmet'in teyidi bekleniyor.

## 9. Düzeltme turu 2 (14.11.2026 00:58–01:15)

Girdi: ikinci bağımsız kontrol `planlama/d158/pin-karari-kontrol-2.md` (DÜZELTME GEREKLİ: R1 durdurur; B1–B8). Pinler değişmedi.
Orkestratörün kararları (Ahmet'in yetkisiyle) uygulandı; her hesabı yeniden yaptım (betik, geçici klasörde).

### 9.1 Okunanlar

| Saat | Ne | Sonuç |
|---|---|---|
| 00:58 | Arduino-ESP32 `3.0.7` ve `3.3.0` `cores/esp32/HardwareSerial.h`; ESP-IDF `v5.1.4` `components/driver/uart/uart.c` | R1 doğrulandı |
| 01:00 | IDF `v4.4.7` `spiram_psram.c` 495, 669, 761, 779–780, 914, 944–953; Arduino 2.0.17 `sdkconfig` 64–65, 682, 747; `esp32-hal-psram.c` 57–76 | B1 doğrulandı |
| 01:02 | ESP32 Datasheet v5.3 Tablo 5-3 (VOH ≥ 2,64 V, RPU 45 kΩ yalnız tipik), Ek A not 8 (~75 µA); ESP-IDF v4.4.7 ADC sayfası (zayıflatma aralıkları) | D1, D7 hesapları |
| 01:03 | BTS7960 tam veri sayfası: üretici dışı kopyalar (iki satıcı PDF'i, iki veri sayfası arşiv sitesi, web arşivi) | Açılamadı (HTML / 403 / bot engeli; bir satıcı PDF'i yalnız modül kılavuzu). IIS(lim) **doğrulanmadı**, en kötü 7 mA alındı |
| 01:05 | AO3400A (Alpha & Omega) ve IRLML6344 (Infineon) veri sayfaları üreticiden; distribütör araması | D9 |
| 01:06 | Robocombo direnç seti sayfası (MJ:115) | 470 Ω, 1 / 2,2 / 4,7 / 5,1 / 6,8 kΩ sette var |
| 01:07 | `elektrik.md` E3 (:268 bobin ~0,15 A), `maliyet.json:106-109` (K1 bobin ~0,15 A, K2 JQC-3FF) | D9 |

### 9.2 Karar başına yapılan

| # | Karar | Doğrulama / hesap | Yapılan |
|---|---|---|---|
| 1 | **R1** 3.x'te GPIO4 = `Serial2` RX | 3.0.7 `HardwareSerial.h:151-152, 169-170, 191-192, 199-200` ve 3.3.0 `:194-195, 216-217, 242-243, 250-251`: RX1 26, TX1 27, RX2 4, TX2 25. IDF 5.1.4 `uart.c:615-623`: TX HIGH başlar, RX'e pull-up | Y1 yeniden yazıldı (Serial1 / Serial2 hiçbir sürümde varsayılan pinlerle açılmaz; pinler açıkça verilir; tabloda yeri olmayan pin kullanılmaz). 4, 25, 26, 27 satırlarına 3.x notu; aday tablosu, röle kuralı, `elektrik.md:259, 470, 480, 481, 483` sürüm belirterek düzeltildi. Yeni Y13: çekirdek espressif32@6.9.0'da sabit, 3.x'e geçiş rapor gözden geçirilmeden yok |
| 2 | Gate pull-down 10 → 4,7 kΩ | Sürülü gate: VOH 3,3 V → 3,15 V; VOH en az 2,64 V → 2,52 V. Pin akımı 0,54–0,67 mA (tepe 15 mA, 220 Ω). Boşta dahili pull-up: 0,31 V (45 kΩ), 0,35 V (75 µA), varsayımsal en kötü 0,49 V (30 kΩ, 3,6 V; DS en az değer vermiyor) → T2'nin 0,5 V ölçütüyle tutarlı, en kötüde pay 10 mV. Sette var | D1, §4, §9 JSON, `elektrik.md:251, 259, 444, 483, 484`, pano |
| 3 | Röle MOSFET şartı | Bobin K1 ~0,15 A (12,8 V) → 14,6 V'ta ≈ 0,17 A; K2 ~0,03 A. AO3400A: VGS(th) 0,65–1,45 V, RDS(on) < 48 mΩ @ 2,5 V → en kötü gate 2,52 V'ta ≥ 1,07 V pay, VDS ≈ 8 mV, 1,4 mW; kapalıda 0,49 V'a karşı en düşük eşik 0,65 V (0,16 V pay). IRLML6344: eşik 0,5–1,1 V, RDS(on) ≤ 37 mΩ @ 2,5 V; kapalı payı yok denecek kadar az → ikinci seçim. VDS ≤ ≈ 15,6 V (1N4007 kenetli) < 30 V. Orijinal IRLZ44N de şartı karşılamaz (RDS(on) yalnız ≥ 4 V'ta tanımlı) | D9 (yeni), T2 (f)–(g) "kesin çeker / kesin bırakır" ölçümü (F5 takılı, bara yüksüz, 11 V ve 14,6 V'ta 20'şer kez); `elektrik.md:268, 446` ve şemalarda "IRLZ44N" → "MOSFET"; VBsemi parçası "değiştirilecek" olarak §7'de |
| 4 | **B5** IS koruması yeniden | Formül V = I × (Rb ∥ (R1 + R2)) × R2 / (R1 + R2), şart 14 mA'de ≤ 3,2 V. Rb = 500 Ω için 6,8 / 5,1 kΩ → 2,88 V (7 mA: 1,44 V; Rb +%10: 3,17 V); Rb = 1 kΩ → 6,8 / 2,2 kΩ, 3,08 V; kartta direnç yoksa + 470 Ω → 2,71 V. Ölçek 24,2 mV / A: 2,8 A ≈ 68 mV, 0 dB aralığı (100–950 mV) ≈ 4,1 A'den başlar. Diyotlu (1 kΩ + 1N5819): 2,8 A ≈ 165 mV ama hata anında pin ≈ 3,6 V (mutlak sınır), kaçak 10–50 mV | **Diyotsuz bölücü seçildi** (D7, Y7, T6 ilk adım kart direnci, JSON, `elektrik.md:478-479`, pano). 1N5819 notu kaldırıldı. **Kısmen tutmayan:** "normal ölçüm aralığı okunabilir" şartı 4 A altında sağlanmıyor (fiziksel oran sınırı); rapora ve aşağıya yazıldı |
| 5 | **B6** eski firmware K2 yolu | 19 `INPUT_PULLUP` → 0,31 / 0,35 / 0,49 V; AO3400A en düşük eşik 0,65 V → K2 iletmez; iletseydi bara 5,6 Ω'dan, 13 + 27 HIGH ile sağ motor direnç üstünden sürülürdü. 32 / 33 PWM'i 6,8 kΩ üstünden ≤ 0,5 mA | §3.1 K1 / K2 / IS yolları ayrı ayrı; sonuç cümlesi "yalnız yeni firmware (Y1)" |
| 6 | **B1** PSRAM atıfları | `:583-608` `#if CONFIG_SPIRAM_2T_MODE` (495–669) içinde, `sdkconfig:747` kapalı → derlenmiyor. Doğru yol `:761, 779-780, 860-863, 914, 944-953` | IDF44 satırı, §1, §3.1, §4, pano `--kaynak`; "PSRAM bulunamayınca 16 / 17 LOW sürülü kalabilir (doğrulanmadı)" notu; yoklama D0WD(-V3)'te de |
| 7 | **B7** günlük | – | §7 sürüm 3 tablosuyla baştan yazıldı (eski "K1 GPIO16, K2 GPIO17" girdisi silindi); N3 (`baski-listesi.md:286`, `F4c-partiler.py:127`, 499 → 505) §7 "C adımında düzeltilecek" listesinde. `elektrik.md` 522 satır, bu turda değişmedi |
| 8 | Sürüm 3, dört yer aynı | Betik: rapor §2, §9 JSON (`json.loads`, ASCII, 24 pin, tekrar yok), `elektrik.md` 466–496, pano gövdesindeki tablo satırı pin pin aynı | Pano gövdesi 2517 karakter (sürüm 2: 2412); 4,7 kΩ, Serial kuralı, çekirdek sabitleme, MOSFET şartı birer cümle |

B2 (indirme kipi) ve B3 (enkoder kenarı) kontrolde "durdurmaz / doğru" çıktı; B2'nin en kötü durumu 4,7 kΩ ile 0,35 V. B8: "D0WDQ6 paketinde" → "D0WDQ6 ve D0WD(-V3)".

### 9.3 Hâlâ doğrulanamayanlar

- BTS7960 IIS(lim) (4 / 4,5 / 7 mA) ve kILIS 8500: tam veri sayfası açılamadı; ikinci elden, en kötü 7 mA (iki IS birlikte 14 mA) alındı.
- ESP32 dahili pull-up'ının en düşük değeri: DS vermiyor; 0,49 V'luk en kötü hesap varsayım (30 kΩ). T2 ölçer.
- Kart IS direnci (R): bilinmiyor; D7 formülle verildi, T6'nın ilk adımı.
- 4 A altında motor akımı ölçümü: diyotsuz bölücüyle belgelenen ADC aralığında değil. Durma algılama gerekiyorsa ayrı karar (karşılaştırıcı /
  yükselteç).
- AO3400A / IRLML6344 için Türkiye'de satıcı, fiyat ve stok doğrulanmadı (aramada bir distribütörde AO3400A listeli, stok 0).
- Röle bobin akımları ölçülmedi (~0,15 A ve ~0,03 A belge değeri).
- PSRAM yoklaması sonrasında 16 / 17'nin LOW sürülü kalıp kalmadığı (ROM davranışı), indirme kipinde ROM'un GPIO4'e ne yaptığı: T2.
- Arduino 3.x'in `initArduino` düzeyinde 4 / 19'a dokunup dokunmadığı okunmadı (Y13 bu yüzden).

## 10. C adımı (14.11.2026, başlangıç 01:30)

Girdi: üçüncü bağımsız kontrol `planlama/d158/pin-karari-kontrol-3.md` (**GEÇER**; Ö1–Ö8 metin notları). Pinler değişmedi. Satır
numaraları bu adımın sonundaki dosyalara göredir.

### 10.1 Bulgu başına yapılan

| Bulgu | Yapılan (dosya:satır) |
|---|---|
| Ö1 T2 aracı | `pin-haritasi.md:353` T2: 0,5 V ölçütü osiloskopla ölçülür; mantık analizörü bu ölçüt için araç değildir. Osiloskop yoksa yedek yol: (a)–(e)'de multimetreyle kararlı gate gerilimi + F5 takılı, bara yüksüz kurulumda röle kontağının çıkışı mantık analizörüyle ya da ikinci bir mikrodenetleyicinin kesme girişiyle izlenir (0,5 V ölçütünden zayıf, rölenin çekmesini doğrudan sınar); geçme ölçütü yedek yol için ayrı yazıldı |
| Ö2 T6 | `pin-haritasi.md:357` T6: "akım sınırında" kalktı; yerine laboratuvar kaynağıyla IS düğümüne 14 mA enjeksiyonu (bölücü çıkışı ≤ 3,2 V) |
| Ö3 durma algılama | Karar (orkestratör, 14.11): durma / sıkışma enkoderle algılanır; IS yalnız arıza bayrağı ve kaba gösterge. `pin-haritasi.md:264` Y7 iki motorlu kart için yeniden yazıldı (kart başına ≈ 4,1 A altı okunmaz; 71 / 22 / 136 mV örnekleri); D7 ve §8 metni aynı yönde. `elektrik.md:203` eski kural üstü çizili + "14.11: kural enkodere taşındı" (eşik ve süre ölçümden sonra; değer yazılmadı); `elektrik.md:170` aynı satıra işaret |
| Ö4 Y1 | `pin-haritasi.md:241-246` Y1: `HardwareSerial(1)` / `(2)` ve bunları açan kütüphaneler, varsayılan pinler (2.0.17: 16 / 17, 9 / 10; 3.x: 26 / 27, 4 / 25), LEDC istisnası (`pinMode`, `digitalWrite`, `ledcSetup` / `ledcAttachPin`, `ledcAttach` serbest); 3.0.7 pull-up açar / 3.3.0 açmaz (`:15`, `:30`, `:177`); 3.x'te `Serial1` / `Serial2` açılırsa 25 / 27 HIGH sürülür ve EN HIGH iken motor bir yönde döner, **bunu yalnız Y1 ve Y13 önler, donanım önlemez** (`:84`, `:86`, `:246`) |
| Ö5 IRLZ44N kalıntısı | `elektrik.md:306` "IRLZ44N + 1N4007" → "röle MOSFET'i (D9, SOT-23 adaptörlü) + 1N4007"; `elektrik.md:339` şemada "IRLZ44N" → "MOSFET". `elektrik.md:106` tarihçe sütunu olduğu için kaldı. Önceki turda silinen "Alternatif BC337 + 1 kΩ" geri geldi (`elektrik.md:268`, "eski seçenek, delikli; 220 Ω / 4,7 kΩ ağı ona göre yeniden hesaplanır, doğrulanmadı"); `pin-haritasi.md:296` D9'a aynı not |
| Ö7 (isteğe bağlı) | `pin-haritasi.md:296` D9 şartına "VGS ±8 V ya da üstü, ID ≥ 1 A" eklendi |
| Ö8 sayı ve ifade | `pin-haritasi.md:322` 3,17 → **3,15 V**; `:290` D3 ve `:329` "DS Tablo 5-3: VIH en çok VDD + 0,3 V" ifadesi; T4 / T7 / T8 sayısal ölçütleri (`:355` IN ucunda HIGH ≥ 2,6 V, kart girişi eşiği kart gelince; `:358` LOW ≤ 0,8 V, HIGH ≥ 2,5 V; `:359` sayısal ölçüt kart gelince, uydurulmadı); bu günlükte §6'daki eskimiş VBsemi cümlesi düzeltildi, §7 kaynaklarına `pin-karari-kontrol-3.md` eklendi |
| Ö6 pano gövdesi | Depo dışı taslağa iki cümle: "`main` `2be1c63` firmware'i bu kablaja yüklenmez; `pinler.h` bu tabloya göre yeniden yazılmadan kart kablaja takılmaz" ve devreye alma sırasında "19 en çok 1 s; 5 LOW değilse 19 = 0 ve hata". Kaynak listesine üç kontrol raporu. Panoya yazılmadı |

Tablo dört yerde (rapor §2, §9 JSON, `elektrik.md` pin planı, pano gövdesindeki tablo satırı) betikle karşılaştırıldı: fark 0.

### 10.2 Kayda girenler

- `planlama/d158/karar-kuyrugu.md`: **K58** (ESP32 pin haritası, kapandı; karar orkestratörün, Ahmet'in 13.11.2026 yetkilendirmesiyle).
  K1'e pano #5 mesaj #23 notu (Efe'nin tarafı "yok, 5 cihaz" yazdı; kuyruğun kapanış kalıbı Ahmet kararı olduğu için **"cevap geldi,
  kapanış kaydı bekliyor"**), K14'e pano #6 mesaj #21 notu (dış teyit), pano #7 mesaj #22 ve #6 #21'deki önerilere "yeni soru" satırları
  (karar açılmadı), "Karar değil, iş" bölümüne pin kararının işleri. Özet sayımı: açık 52, kapandı 6, toplam 58.
- `planlama/dongu-158.md`: P10.6 satırı (karar verildi, rapor yolu), P10.7'nin kalan engelleri (K10 / K11 / K14 + parça ve ölçüm işleri),
  §5 günlük girdisi.
- `planlama/baski-listesi.md:286` ve `planlama/d158/F4c-partiler.py:127`: `elektrik.md:499` → `elektrik.md:505` (satır yeniden sayıldı:
  "Kabuk" açık işi 505'te). Betik koşulmadı; çıktıları `F4c-partiler.md:127` ve `F4c-partiler.json:2275` eski numarayı taşıyor (betik bir
  sonraki koşuda yazar).
- Gizlilik taraması (sahnelenen fark): `pin-karari-kontrol.md:150, :189`'daki asistan takma adı ayıklandı (anlam aynı); başka yerel
  yol, e-posta, anahtar, ağ adı bulunmadı.

### 10.3 Açık kalan

- §9.3'teki doğrulanamayanlar aynen (IIS(lim), dahili pull-up en düşük değeri, kart IS direnci, MOSFET satıcı / stok, bobin akımları,
  PSRAM yoklaması sonrası 16 / 17, indirme kipinde 4, 3.x `initArduino`).
- Delikli BJT seçeneğinin (BC337) 220 Ω / 4,7 kΩ ağıyla hesabı yapılmadı.
- T4 / T8 sayısal ölçütleri kart gelince yazılacak.
- §5'teki tutarsız belgeler (yazılım planı, test kâğıtları, maliyet notları, rehber metni) düzeltilmedi; kuyruğun "Karar değil, iş" bölümünde.
