# Pin kararı: bağımsız kontrol (B adımı), 14.11.2026

Kontrol edilen: `planlama/adim3/pin-haritasi.md` (yeni), `planlama/adim3/elektrik.md` (çalışma ağacı farkı), `planlama/d158/pin-karari-gunluk.md`,
depo dışındaki pano #8 taslağı ve gövdesi. Kod `origin/main` = `2be1c63`'ten okundu (dal değiştirilmedi). Başlangıç 14.11 00:16 civarı,
rapor 00:30'da yazıldı (saat makineden). Hiçbir dosya düzeltilmedi; commit, `git add`, pano yazımı yok; FreeCAD ve rehber betikleri koşulmadı.

## Hüküm: **DÜZELTME GEREKLİ**

Pin tablosu ESP32'nin strapping, yalnız giriş, flaş, ADC ve reset kısıtlarıyla genel olarak tutarlı ve dört yerde birebir aynı. Ama
K1 / K2'nin 16 / 17'ye konmasının ana gerekçesi ("17 hiçbir hazır programın dokunduğu pin değil") yanlış: 16 / 17 Arduino çekirdeğinin
**UART2 varsayılan pinleri** ve projenin kullandığı Arduino-ESP32 çekirdeği **her açılışta PSRAM yoklamasıyla bu iki pini sürüyor**. İkisi de
röle kapısıyla (motor / bara güvenliği) ilgili olduğu için gönderimi durdurur (D1, D2).

## Durduran bulgular

### D1. GPIO17 = Arduino `Serial2` TX (boşta HIGH), GPIO16 = RX: herhangi bir `Serial2` kullanan program K2'yi sürekli çektirir

- **Ne:** Arduino-ESP32 2.0.17'de `HardwareSerial.h` ESP32 için `RX2 = 16`, `TX2 = 17` tanımlar (kaynak:
  `espressif/arduino-esp32` etiket `2.0.17`, `cores/esp32/HardwareSerial.h` satır 167–177). Kartın serigrafisi de bu pinleri "RX2 / TX2" diye
  yazar (rapor §1 ve T1 bunu kendisi söylüyor). UART TX boşta **HIGH** tutulur. `Serial2.begin(...)` çağıran her program (GPS, Nextion, seri
  ekran örnekleri; ayrıca projenin kendi yazılım planı: `planlama/yazilim-plani.md:34` "Nextion … UART2 (GPIO17/16)") K2 gate'ini sürekli 3,3 V
  yapar. Mantar serbestken K2 çeker ve K1 açıkken bara sürekli 5,6 Ω ön şarj kolundan beslenir; yük akımı bu dirençten geçer (EL E9'un hata
  hesabı 32–38 W, direnç 11 W). Bu, GPIO2 için kaçınılan "LED yakıp söndüren program K2'yi açar kapar" hatasının **daha kötü** biçimi (1 Hz
  yerine sürekli).
- **Nerede:** `pin-haritasi.md:145` ("17 hiçbir hazır programın dokunduğu pin değil"), `:143-145` (K2 gerekçesi), `:71`, `:291`;
  `elektrik.md:458-459` ("Neden: LED yakıp söndüren herhangi bir program …"); pano gövdesi satır 3 ("Gerekçe raporda §3.1").
- **Önerilen düzeltme:** röleleri hiçbir çekirdek / kütüphane varsayılanının ve açılış işinin dokunmadığı pinlere almak (aşağıda "Önerilen
  pin değişikliği"). 16 / 17'de kalınacaksa en azından §3.1 gerekçesi düzeltilmeli, Y1'e "`Serial2` ve UART2 kullanılmaz" kuralı ve
  `yazilim-plani.md:34`'ün düzeltilmesi eklenmeli; ama bu, D2'yi çözmez.
- **Sınıf:** durdurur (röle).

### D2. Arduino-ESP32 çekirdeği her açılışta, `setup()`'tan önce GPIO16'yı (PSRAM CS) ve GPIO17'yi (PSRAM CLK) sürer

- **Ne:** Projenin derleme ortamı `platform = espressif32@6.9.0` (Arduino-ESP32 2.0.17; `origin/main:kod/esp32/platformio.ini:8`). Bu
  çekirdeğin hazır derlenmiş ESP32 ayarlarında `CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_BOOT_INIT` kapalı, `CONFIG_D0WD_PSRAM_CS_IO=16`,
  `CONFIG_D0WD_PSRAM_CLK_IO=17` (`tools/sdk/esp32/sdkconfig` satır 683–684, 730–731). `initArduino()` bu durumda `psramInit()` çağırır
  (`cores/esp32/esp32-hal-misc.c`, `#if CONFIG_SPIRAM_SUPPORT || CONFIG_SPIRAM`). `psramInit()` → `esp_spiram_init()` → ESP-IDF v4.4
  `psram_enable()`: çip paketi D0WDQ6 / D0WDQ5 ise CS = 16, CLK = 17 seçilir, CLK SPI saatine bağlanır, CS önce `GPIO_OUTPUT_SET(CS, 1)` ile
  HIGH yapılır, kimlik (ID) iki kez okunur (`components/esp_hw_support/port/esp32/spiram_psram.c` v4.4.7, satır 583, 860–863, 940–955).
  PSRAM yoksa hata döner ve Arduino 16 / 17'yi `pinMatrixOutDetach` ile GPIO çıkışına bırakır (`esp32-hal-psram.c`, 2.0.17; 3.0.7'de de aynı,
  satır 65–71). Satıcı çipi tam olarak **D0WDQ6** diye yazıyor (`pin-haritasi.md:33`), yani bu yol bu kartta çalışır.
- **Sonuç:** reset bitince ve firmware'in `setup()`'ı başlamadan önce K1 gate'i kısa bir süre HIGH, K2 gate'i SPI saatiyle sürülür. Süre
  kod okumasından mikro saniyeler ile 1 ms'nin altı arası **tahmin**; ölçülmedi. Bu sürede röle mekanik olarak büyük olasılıkla çekmez (gate
  220 Ω ile hızlı dolar, bobin akımı ise endüktansla sınırlı), ama:
  - Raporun olgu iddiası yanlış: "Reset sonrasında 25, 26, 27, 16, 17 yüzer … Firmware pinleri ayarlayana kadar bu durum sürer"
    (`pin-haritasi.md:170-171`), "reset, çökme, watchdog, firmware yükleme ve USB sökme anlarında ikisi de pull-down ile LOW" (`:188-189`),
    `elektrik.md:259` "reset sırasında ve firmware ayarlayana kadar çıkışı kapalı". Arduino ile derlenmiş her firmware'de doğru değil.
  - T2 (`pin-haritasi.md:248`) multimetreyle ölçüyor; bu darbeyi göremez.
  - Y2'nin "her şeyden önce" sırası (`:195`) bu darbeyi engelleyemez; darbe `setup()`'tan önce.
- **Önerilen düzeltme:** D1 ile aynı: röleleri 16 / 17'den almak. Kalınacaksa: §2, §4 ve `elektrik.md:259` düzeltilir; T2'ye osiloskop ya
  da mantık analizörüyle açılış darbesi ölçümü (gerçek firmware ile, F5 takılı değilken) ve "K1 + K2 aynı anda HIGH süresi" geçme ölçütü
  eklenir; PSRAM'i kapalı derlemenin yolu (Arduino'nun hazır kütüphanesiyle `CONFIG_SPIRAM` kapatılamıyor; ESP-IDF ya da yeniden derlenmiş
  kütüphane gerekir) Efe'ye ayrı iş olarak yazılır.
- **Sınıf:** durdurur (röle; raporun "açılışta röle kapalı" güvencesinin kaynağı tutmuyor).

### Önerilen pin değişikliği (D1 + D2 için; karar Ahmet'in / orkestratörün)

Boşta kalan pin sayımı raporla aynı: 30 pinli düzende dışarıda 25 GPIO var, tablo 24'ünü kullanıyor, boş yalnız 12. Yeni boş pin yok; çözüm
**girişlerle yer değiştirmek**. 16 / 17'ye giriş (enkoder) konursa PSRAM'li modülde ya da `Serial2` açılırsa olan şey "bir enkoder kanalı
çalışmaz" olur, röle çekmez.

| İş | Şimdiki | Öneri | Gerekçe |
|---|---|---|---|
| K1 | 16 | **4** | Strapping değil, PSRAM / UART varsayılanı değil; reset sırasında ve sonrasında **wpd** (IO_MUX), gate pull-down'a ek |
| K2 | 17 | **19** | Strapping değil; VSPI'de MISO (SPI kütüphanesi açarsa giriş yapar, sürmez); reset sonrasında yüzer, gate pull-down tutar |
| Sağ enkoder A | 4 | 16 | Giriş; WROVER / N4R2'de yalnız işlev kaybı |
| Sol enkoder B | 19 | 17 | Giriş; aynı |

Bu öneri de bağımsız kontrolden geçmeden kesinleşmemeli. Açık soru: ROM'un indirme (download) kipinde SDIO slave pinlerine (GPIO4 = HS2_DATA1,
13, 14, 15, 2, 12) ne yaptığı Espressif belgelerinde bulunamadı; T2 bu yüzden **indirme kipinde de** (BOOT basılıyken reset) ölçülmeli.
Bu değişiklikle §3.3 yedek tablo gereksizleşir ve T1 güvenlik şartı olmaktan çıkar, işlev şartı olur. Efe'nin önerisinden (16 / 17) sapma
olduğu için pano mesajında açıkça gerekçesiyle söylenmeli.

## Durdurmayan bulgular (önem sırasıyla)

### N1. BTS7960 IS hata akımı biliniyor: 1 kΩ'ta 4–7 V, ESP32 pinine doğrudan bağlanamaz

- **Ne:** Infineon *BTS 7960 Data Sheet* Rev. 1.1 (2004-12-07) §4.4.7: IIS(lim) **en az 4, tipik 4,5, en çok 7 mA** (RIS = 1 kΩ). Hata ya da
  akım sınırında IS ucu 4–7 V olur; ESP32 girişi VDD + 0,3 V'u geçemez (DS Tablo 5-3). Günlük bu değeri "bulunamadı" diyor
  (`pin-karari-gunluk.md:40`); rapor şartı ölçüme bırakıyor (`pin-haritasi.md:63-64`, T6 `:252`). Ayrıca IS1 + IS2 aynı pine bağlanınca iki
  kaynak paralel olur. Normal ölçümde (2,8 A durma ≈ 0,33 V) T6 geçer, hata durumu ancak sonra ortaya çıkar.
- **Öneri:** D tablosuna kalıcı donanım şartı: 32 / 33'e seri direnç + 3V3'e Schottky kenetleme ya da 7 mA'da ≤ 3,3 V veren bölücü; değer
  kartın RIS'i ölçülünce. T6'nın "kalmazsa" sütunu "her durumda" olmalı.
- **Sınıf:** durdurmaz (motor / röle / açılış değil; ESP32 pini hasarı). Aynı düzeltme turunda eklenmesi önerilir.

### N2. Kaynak satır atıfları yanlış

- `kanallar.yaml:44-53` (`pin-haritasi.md:88`, `:109`; pano taslağı `--kaynak` satırı 17 ve gövde satır 17): `main` `2be1c63`'te 44–53 yorum
  satırları (ayna kuralı). Kanal tablosu **61–73** (`kanallar:` 61, kanallar 63–67 ve 69–73).
- `EL:488` (`pin-haritasi.md:88`): yeni `elektrik.md`'de 488 "18 / 19 enkoder" satırı; PCA9685 satırı **494** (eski dosyada 488'di).
- `EL:458` (`:49`) ve `EL:130-131` (`:96`) yeni dosyada doğru yere düşüyor.
- **Sınıf:** durdurmaz; gönderimden önce düzeltilmeli (pano protokolü madde 3).

### N3. `elektrik.md` satır kayması: bozulan atıflar

Fark yalnız pin kararının gerektirdiği yerleri değiştiriyor; direnç (220 Ω, 10 kΩ, 5,6 Ω 11 W), sigorta (F1–F5), röle, kablo ve akım değerlerinde
değişiklik yok (diff satır satır okundu). Kayma: eski 1–457 aynı; eski 458–491 **+1**; eski 492 sonrası **+6** (günlükteki tarif doğru).
Bozulanlar:

| Atıf | Eski hedef | Şimdi |
|---|---|---|
| `planlama/baski-listesi.md:286` `elektrik.md:499` (E7 etek yarıkları) | açık iş 2 "Kabuk" | 499 boş satır; hedef **505**. Üretici `planlama/d158/F4c-partiler.py:127` (ve `F4c-partiler.md:127`, `.json:2275`) aynı sayıyı basıyor |
| `pin-haritasi.md:88` `EL:488` | PCA9685 satırı | 494 (N2) |
| `F0-gunluk.md:81`, `F0-kontrol.md:178, 228`, `F7b-gunluk.md:230-231, 301, 313, 319`, `F7b-kontrol.md:472, 492, 610, 710`, `F7b-rapor.html:143`, `F7c-kontrol.md:71`, `F7c-rapor.html:93`, `F7c-gunluk.md:14`, `F5-gunluk.md:18` (455–462) | E9 bölümü | 458 ve sonrası +1 kaydı; tarihçe belgeleri, düzeltme gerekmez |
| `testler/T3:115-116`, `T7:30, 129`, `T10:165`, `testler.html`, `F8c-kontrol.md:53` (472–480) | bu değişiklikten **önce de** yanlıştı (eski 472 = "35 sonar", 477 = "13 BTS EN"; kastedilen açık işler 13 / 14 / 16) | şimdi +6 daha uzak (açık iş 14 → 517) |

**Sınıf:** canlı belge `baski-listesi.md` (ve onu üreten betik) kayıtlı açık iş olarak gidebilir; tarihçe belgeleri değişmez.

### N4. Modül varsayımının listesi çiple çelişiyor; T1 daha güvenilir yapılabilir

- `pin-haritasi.md:36` "WROOM-32, -32D ya da -32E": WROOM-32D'nin çekirdeği ESP32-D0WD (W32D §1), WROOM-32E'ninki D0WD-V3 / D0WDR2-V3
  (W32E satır 27, 124). Satıcının yazdığı **D0WDQ6** doğruysa modül yalnız eski WROOM-32 ya da eski WROVER olabilir; o zaman N4R2 senaryosu
  bu kartta olamaz (yedek satıcının WROOM-32D'sinde de olamaz). WROOM-32E tablosunda "R8" sürümü yok, yalnız R2 (W32E Tablo 1).
- T1 (`:247`) kapak yazısına dayanıyor; kapakta sürüm kodu (N4R2) her zaman yazmayabilir (doğrulanmadı). Daha kesin yol: kablajdan önce
  `esptool.py chip_id` çıktısındaki çip paketi ve revizyonu (D0WDR2-V3 = paket içi PSRAM) ve WROVER için modül boyu. Revizyon ayrıca önemli:
  errata [RES-3.4] v0.0 çipte brown-out reset'ten sonra açılış olmuyor (Errata v3.1 §3.13); güvenli yöne düşer (röle bırakık) ama robot
  güç kesmeden geri gelmez.
- **Sınıf:** durdurmaz (D1 / D2 önerisi uygulanırsa T1 zaten güvenlik şartı olmaktan çıkar).

### N5. "Eski firmware yeni kablajda" hesabı: tipik değer, en kötü durum değil; açılış darbesini kaçırıyor

- Yeniden hesap: 3,3 × 10 / (10 + 45) = **0,60 V** (doğru). Ama DS Tablo 5-3 RPU için yalnız tipik 45 kΩ veriyor, en az değer yok; IO_MUX
  notu çekme gücünü "~75 µA" diyor (75 µA × 10 kΩ ≈ 0,75 V). İkisi de Infineon'un en az 1,0 V eşiğinin altında; alınacak VBsemi parçanın
  eşiği doğrulanmadı (günlük `:36`). Pano gövdesi (satır 3) "IRLZ44N eşiği ≥ 1,0 V: röleler çekmez" diye olgu gibi yazıyor; rapor (`:149`)
  doğru biçimde "şans" diyor. Ayrıca eski firmware de D2'deki PSRAM yoklamasını yapar ve 32 / 33'ü (artık IS uçları) PWM çıkışı olarak
  sürer (`motorlar.cpp:105-113, 140-146`); bara enerjisiz olduğu için zararsız, ama yazılmamış.
- **Öneri:** gövde satır 3 "tipik değerle hesap; parça eşiği ölçülmedi" diye yumuşatılsın; rapora 32 / 33 notu.
- **Sınıf:** durdurmaz.

### N6. Y2'deki sıra Arduino-ESP32 3.x'te yazıldığı gibi çalışmaz

`digitalWrite(p, LOW); pinMode(p, OUTPUT);`: 3.x'te yapılandırılmamış pine `digitalWrite` reddedilir ("IO %i is not set as GPIO",
`esp32-hal-gpio.c` 3.0.7 satır 173–176). Sonuç yine LOW olur (çıkış kaydı resetten sonra 0), ama metin bunu sağladığını sanıyor; proje 2.0.17'de
çalışıyor, `motorlar.cpp` 3.x'i de destekliyor. Öneri: 3.x için `pinMode` + hemen `digitalWrite(LOW)` ya da `gpio_set_level` önce. Durdurmaz.

### N7. GPIO14 açılış darbesi notu kaldırıldı

Eski `elektrik.md` "14 boot'ta kısa PWM verir: EN düşük olduğu için zararsız" diyordu; yeni metin (`elektrik.md:481`, `pin-haritasi.md:68`)
yalnız "zayıf HIGH" diyor. Espressif belgelerinde bu darbeye kaynak bulamadım (topluluk gözlemi). EN (13) 10 kΩ ile LOW olduğu sürece BTS7960
INH = 0 → iki anahtar da kapalı (Infineon DS §4.4.5 doğruluk tablosu), yani zararsız. Öneri: "kaynaksız topluluk gözlemi; EN LOW iken zararsız;
T3'te osiloskopla bakılır" notu kalsın. Durdurmaz.

### N8. §6.1'deki "ters çıkarsa" cümlesi iki anlama geliyor

`pin-haritasi.md:238-239` "13 → kartın IN dediği uçlara değil, INH'ye giden uçlara". Güvenlik hesabı doğru (aşağıda), ama kablocu için açık
yazılmalı: "Kartın EN1 / EN2 dediği uç INH'ye gitmiyorsa: 13 kartın IN1 / IN2 dediği uçlara, 25 / 26 / 27 / 14 kartın EN1 / EN2 dediği
uçlara." Durdurmaz.

### N9. Pano taslağı

- Gövdenin ilk satırında asistanın takma adı geçiyor. Depodaki önceki kontroller bu adı belgelerden ayıklıyor (`F9a-kontrol.md:86`);
  panoda da kullanılmaması önerilir.
- Gövde 19 satır, rapordaki tabloyu ve firmware şartlarını yeniden yazıyor; protokol madde 2 "kısa". Kesin tablo satırı kalabilir, Y-maddeleri
  rapora gönderme ile kısaltılabilir.
- `--kaynak "kod/esp32/src/motorlar.cpp (enkoder INPUT_PULLUP)"` satır numarasız; doğrusu `motorlar.cpp:205-208`.
- "#21'de … yazmışsın": mesajın pano #6'da olduğu yazılmamış (rapor `:108` yazıyor). Eklenmesi önerilir.
- Karar durumu: konu `soru` kalıyor, YZ karar durumu seçmiyor (protokol madde 4'e uygun). D1 / D2 önerisi kabul edilirse pin değişikliği
  Efe'nin önerisinden sapma olur; Ahmet'in insan oturumuyla teyidi önerilir.
- PCA9685 sorusu **gerçek bir çelişkiye dayanıyor**: `main` `kanallar.yaml:63-73` 10 kanallı blok düzen (0–4 sağ S1, S2, dirsek, bilek, pan;
  5–9 sol aynı + tilt); `84bc2b4`'teki eski düzen 6 servoluk (0 sag_omuz, 1 sag_dirsek, 2 sol_omuz, 3 sol_dirsek, 4 pan, 5 tilt), "0–5 aynen,
  6–9 = …" cümlesi o düzenin uzantısı gibi. Sonar trig 10 / 11 / 12 `main`'de kullanılmıyor, `kanallar.yaml:14` bunları sonar için ayırmış;
  çakışma yok. Yalnız satır atfı yanlış (N2).
- Sınıf: durdurmaz; gönderimden önce düzeltilmeli.

## Doğruladıklarım

- **Strapping:** GPIO0 / 2 / MTDI / MTDO / GPIO5 varsayılanları, MTDI = 1 → VDD_SDIO 1,8 V, MTDO = 0 → U0TXD susar, GPIO5 + MTDO yalnız SDIO
  slave zamanlaması, GPIO0 = 0 iken GPIO2 = 0 (DS v5.3 Tablo 3-1, 3-3, 3-4, 3-5, §3.2). GPIO4 ESP32'de strapping değil. Raporun 12, 2, 15, 5
  satırları doğru.
- **Yalnız giriş 34–39, dahili çekme yok** (DS §2 pin notu); 39 / 34 / 35 / 36'ya pull komutu verilmemesi doğru. Flaş 6–11 kullanılmıyor.
- **IO_MUX reset sütunları** (DS Ek A, metin çıkarımından satır eşleştirerek): 13 (MTCK) ie=0 → ie=1 wpd; 14 (MTMS) ie=0 → ie=1 wpu; 12 wpd / wpd;
  15 wpu / wpu; 2 ve 4 wpd / wpd; 16 / 17 oe=0 ie=0 → ie=1 (çekme yok). Not 9: reset sırasında bütün çıkışlar kapalı; not 10: sonra Function 0.
  RPU / RPD 45 kΩ tipik (Tablo 5-3). (D2: "firmware'e kadar" kısmı Arduino'da tutmuyor.)
- **Modüller:** WROVER-E 27 / 28 = NC (Şekil 5 metni); WROOM-32E N4R2 / N8R2 / N16R2'de IO16 paket içi PSRAM'e bağlı (pin notu 3); DS'te
  "GPIO16 CE#'ye bağlıysa pull-up ekleyin" notu var. Raporun "WROVER'da röle hiç çekmez, N4R2'de K1 tehlikeli" sonucu doğru.
- **Errata v3.1:** [GPIO-3.11] madde 3.12 (GPIO36 / 39 ~80 ns LOW), [GPIO-3.14] madde 3.11 (aynı grupta kenar kesmesi) doğru numaralı; Y8 / Y9 yerinde.
- **BTS7960 (Infineon DS Rev. 1.1 §4.4.5–4.4.6):** INH = 0 → iki anahtar kapalı (stand-by); INH = 1, IN = 0 → alt; IN = 1 → üst. Giriş eşiği
  VIH en çok 2,15 V (3,3 V lojik çipin kendisine yeter; kart üstünde tampon varsa T4 gerekir). **T4 senaryosu:** adlar ters çıkarsa (13 → IN,
  PWM → INH) 13 LOW iken iki IN de LOW: INH yüksekse iki alt anahtar = fren, değilse stand-by; çalışırken iki IN HIGH, tek INH açık → bir uç
  B+'ta, öbürü stand-by → akım yolu yok. Yani tablo ters adlarda da motoru döndürmez; §4 ve pano gövdesi doğru.
- **Satıcı sayfaları (14.11 okundu):** Robocombo "ESP32-D0WDQ6", modül / PSRAM yazmıyor; Robotistan BTS7960B "EN1, EN2: PWM girişleri; IN1, IN2:
  motor yön kontrol pinleri; VCC +5 VDC". Rapordaki aktarım doğru.
- **Eski firmware:** 16 / 17 `INPUT_PULLUP` (`motorlar.cpp:205-208`), 27 ve 13 HIGH (`:216-217`), LED 500 ms yarım periyot (`main.cpp:75`).
- **Tutarlılık:** rapor tablosu, §9 JSON (geçerli, ASCII, 24 pin, tekrar yok), `elektrik.md` pin planı (`:472-492`) ve pano gövdesi pin pin aynı;
  bir pine iki iş ya da bir işe iki pin yok; dışarıdaki 25 GPIO'dan yalnız 12 boş. `elektrik.md`'de eski GPIO12 / GPIO2 röle atfı yalnız
  tarihçe sütununda (`:106`) ve "14.11'e dek" notlarında kalmış. Diğer belgelerdeki eski atıflar günlük §5'te listeli (sayımı tutuyor).
- **`elektrik.md` farkı** yalnız pinle ilgili satırlara dokunuyor; değer, direnç, sigorta, kablo kesiti değişmemiş.
- **Gizlilik:** depoya girecek üç dosyada yerel yol, makine adı, e-posta, parola / anahtar, ağ adı yok; kişi adları yalnız Ahmet / Efe.
  Pano taslağında tek sorun takma ad (N9).

## Bakamadıklarım / kaynağını bulamadıklarım

- Pano mesajları (#19, #20, #6'daki #21) okunmadı (brief gereği): Efe'nin önerisinin içeriği ve "dosyayı sen açarsın dedin" aktarımı doğrulanmadı.
- PSRAM yoklamasının gerçek süresi ve K1 / K2 bobininde oluşan akım: kod okumasıyla tahmin, ölçülmedi.
- ROM'un indirme kipinde SDIO slave pinlerine (2, 4, 12, 13, 14, 15) çekme ya da sürüş uygulayıp uygulamadığı: Espressif kaynağı bulunamadı.
- GPIO14'ün açılış darbesi: Espressif kaynağı bulunamadı.
- IO_MUX tablosu PDF'te döndürülmüş sayfa; metin çıkarımı karışık, satırları sütun düzeninden eşleştirdim, PDF'i görsel olarak açmadım.
- ESP-IDF GPIO sayfası (v6.1; ADC2 ↔ Wi-Fi, JTAG notları) yeniden açılmadı.
- BTS7960B kartının şeması (tampon entegresi, giriş çekmeleri, RIS değeri), VBsemi IRLZ44NPBF-VB eşiği, 30 pinli kartın üretici pin belgesi:
  bulunamadı; rapordaki T3 / T4 / T6 / T1 ölçümleri bunları kapsıyor.

## Kaynaklar (bu kontrolde açılanlar)

- Espressif *ESP32 Series Datasheet* v5.3, *WROOM-32E* v2.1, *WROOM-32D* v2.8, *WROVER-E* v2.4, *SoC Errata* v3.1 (A adımının indirdiği
  kopyalar; başlık ve sürüm satırları belgelerle tutuyor).
- `espressif/arduino-esp32` etiket `2.0.17`: `cores/esp32/esp32-hal-misc.c`, `esp32-hal-psram.c`, `HardwareSerial.h`, `tools/sdk/esp32/sdkconfig`;
  etiket `3.0.7`: `esp32-hal-misc.c`, `esp32-hal-psram.c`, `esp32-hal-gpio.c`.
- `espressif/esp-idf` `v4.4.7`: `components/esp_hw_support/port/esp32/spiram_psram.c`.
- Infineon *BTS 7960 Data Sheet* Rev. 1.1 (infineon.com).
- Satıcı sayfaları (Robocombo ESP32, Robotistan BTS7960B), 14.11.2026.
- Depo: `origin/main` `2be1c63` (`platformio.ini`, `pinler.h`, `main.cpp`, `motorlar.cpp`, `kanallar.yaml`), `84bc2b4:kod/jestler/kanallar.yaml`,
  `planlama/yazilim-plani.md:34`, `planlama/baski-listesi.md:286`.
