# Pin kararı sürüm 2: ikinci bağımsız kontrol, 14.11.2026

Kontrol edilen: `planlama/adim3/pin-haritasi.md` (sürüm 2), `planlama/adim3/elektrik.md` (çalışma ağacı farkı), `planlama/d158/pin-karari-gunluk.md`
(§8 "Düzeltme turu 1" dahil), ilk kontrol `planlama/d158/pin-karari-kontrol.md`, depo dışındaki pano #8 taslağı ve gövdesi (sürüm 2). Kod
`origin/main` = `2be1c63`'ten okundu (dal değiştirilmedi). Başlangıç 14.11 00:47, rapor 00:56 sonrası yazıldı (saat makineden). Hiçbir dosya
düzeltilmedi; commit, `git add`, pano yazımı yok; FreeCAD ve rehber betikleri koşulmadı.

Kaynaklar bu kontrolde **kendim indirdim** (A adımının kopyalarına dayanmadan): Arduino-ESP32 etiket `2.0.17`, `3.0.7`, `3.1.1`, `3.2.0`,
`3.3.0`; ESP-IDF `v4.4.7` ve `v5.1.4`. Espressif *ESP32 Series Datasheet* v5.3'ün IO_MUX sayfasını (Ek A, s. 69) metin çıkarımıyla değil,
**sayfayı görüntüye çevirip satır satır okuyarak** doğruladım.

## Hüküm: **DÜZELTME GEREKLİ**

K1 → GPIO4, K2 → GPIO19 seçimi sürüm 1'den açıkça daha güvenli ve doğru yönde. 4 ve 19'un reset durumu, strapping dışında kalması,
2.0.17'de hiçbir açılış kodunun onları sürmemesi ve 16 / 17'deki enkoder + 1 kΩ çözümü kaynakla tutuyor. Tablo dört yerde birebir aynı.
Ama raporun K1 gerekçesindeki "GPIO4 hiçbir UART varsayılanı değil" iddiası **Arduino-ESP32 3.x için yanlış**: 3.x'te ESP32'nin `Serial2`
varsayılan RX pini **GPIO4**'tür ve ESP-IDF RX pinine dahili pull-up açar. Rapor 3.x'i açıkça destekleyen bir firmware tarif ediyor (Y2,
`motorlar.cpp`), Y1'deki yasak yalnız "Serial2 (16 / 17)" diyor. Röle çekmez (hesap aşağıda), ama röle güvenliğinin gerekçesi kaynakla
tutmuyor ve pay ince; brief'e göre röleyle ilgili olduğu için **durdurur** (R1). Düzeltmesi küçük: metin + (önerilen) gate pull-down'ı
10 kΩ → 4,7 kΩ.

## Durduran bulgu

### R1. Arduino-ESP32 3.x'te GPIO4 = `Serial2` RX varsayılanı (dahili pull-up açılır); ayrıca 3.x'te `Serial1` / `Serial2` TX'leri 27 ve 25'te

- **Ne:** `espressif/arduino-esp32` `cores/esp32/HardwareSerial.h`, ESP32 hedefi:
  - `2.0.17` (projenin çekirdeği): RX1 = 9, TX1 = 10, **RX2 = 16, TX2 = 17** (satır 141–153, 167–179). Raporun söylediği doğru.
  - `3.0.7` (satır 152, 170, 192, 200), `3.1.1`, `3.2.0`, `3.3.0` (aynı tanımlar): **RX1 = 26, TX1 = 27, RX2 = 4, TX2 = 25**.
  - Arduino 3.x `uartSetPins` → ESP-IDF `uart_set_pin()`; IDF `v5.1.4` `components/driver/uart/uart.c:621-623`: RX pini için
    `gpio_set_pull_mode(rx_io_num, GPIO_PULLUP_ONLY)` (pull-down'ı da kapatır). Aynı dosya `:615-618`: TX pini `gpio_set_level(tx, 1)`
    ile HIGH başlatılır.
- **Sonuç (hesap):** 3.x ile derlenmiş, varsayılan pinlerle `Serial2.begin()` çağıran bir program (GPS, seri ekran, Efe'nin bir deneme
  programı) K1 gate'ine dahili pull-up ile 10 kΩ pull-down arasında bölücü kurar: 3,3 × 10 / (10 + 45) ≈ **0,60 V** (tipik 45 kΩ,
  DS Tablo 5-3); DS Ek A not 8'deki "~75 µA" çekme gücüyle ≈ **0,75 V**. Pin sürülmez (RX girişi), ama bu, ilk kontrolün N5'te 19 için
  "şans, kural değil" dediği payın aynısı ve K1 (40 A ana röle) için geçerli. IRLZ44N eşiği en az 1,0 V (Infineon); alınacak VBsemi
  IRLZ44NPBF-VB'nin belgesi bulunamadı (yakın VBsemi parçaları için 1,9 V ve 3 V gibi değerler görüldü, ama başka parça numarası). Bu
  yüzden röle büyük olasılıkla çekmez; ama T2'nin kendi geçme ölçütünü (> 0,5 V olmaz) **bozar** ve raporun iddiasının kaynağı tutmaz.
  Aynı 3.x programı `Serial1` / `Serial2` açarsa 27 (sağ IN1) ve 25 (sol IN1) sürekli HIGH olur; 13 (EN) LOW kaldıkça motor dönmez
  (BTS7960 INH = 0 → iki anahtar kapalı), ama "yanlış program en kötü bir enkoder kanalını bozar" cümlesi de 3.x için tam doğru değil.
- **Nerede:**
  - `pin-haritasi.md:82` (GPIO4 satırı: "UART / SPI / I2C / PSRAM varsayılanı değil"), `:171` (aday tablosu: "yok"), `:11-13`
    (röle kuralı: "yanlış program en kötü ihtimalle bir girişi bozar"), `:231-232` (Y1 yalnız "`Serial2` / UART2 hiç açılmaz (16 / 17
    enkoder)"), `:179` (25 / 26 / 27 değerlendirmesi 3.x'in TX1 / TX2'sini anmıyor).
  - `elektrik.md:259` ("hiçbir çekirdek açılış işi ya da varsayılan çevre birimi (UART2, …) onu sürmez"), `:483`.
  - Pano gövdesi satır 3 ("4 = dahili pull-down, strapping değil"; "yanlış program en kötü bir enkoder kanalını bozsun"), satır 7
    ("Serial2 / UART2 ve SPI açılmaz").
- **Önerilen düzeltme:**
  1. GPIO4 satırına ve §3.1 aday tablosuna: "Arduino-ESP32 3.x'te `Serial2` RX varsayılanı (dahili pull-up açılır; sürmez)". 25 ve 27'ye
     "3.x'te `Serial2` / `Serial1` TX varsayılanı".
  2. Y1: "**`Serial1` ve `Serial2` hiçbir çekirdek sürümünde açılmaz**; açılacaksa pinleri her zaman açıkça verilir ve 4, 19, 13, 25, 26,
     27, 14 hiçbir kütüphaneye pin olarak verilmez." Pano gövdesinde aynı cümle.
  3. (Önerilen donanım, karar sizin) **Gate pull-down'ları 10 kΩ → 4,7 kΩ** (4 ve 19, D1). Hesap: dahili pull-up karşısında
     3,3 × 4,7 / 49,7 ≈ **0,31 V** (75 µA ile ≈ 0,35 V); 3.x `Serial2`, eski `main` firmware'inin 19'a `INPUT_PULLUP` vermesi ve indirme
     kipinde ROM'un olası bir SDIO pull-up'ı (aşağıda B2) üçü de 0,5 V'un altına iner, T2 ölçütü tutarlı olur. Pin HIGH sürerken ek yük
     3,3 / 4,92 kΩ ≈ 0,7 mA (sorun değil). 220 Ω seri değişmez. 4,7 kΩ'un direnç setinde olduğu doğrulanmadı.
  4. Rapor sürüm satırına hangi çekirdek sürümlerinin sınandığı yazılsın (2.0.17 ve 3.x).
- **Sınıf:** durdurur (röle güvenlik gerekçesi). Pin değişikliği gerekmiyor; 4 hâlâ elimdeki en iyi K1 adayı (B4).

## Durdurmayan bulgular (önem sırasıyla)

### B1. PSRAM yoklamasının kaynak atfı yanlış satıra gidiyor; 16'nın yoklama sonrasındaki durumu belirsiz

- **Ne:** `pin-haritasi.md:26` (IDF44 `spiram_psram.c:111-112, 583-608, 860-863`), `:160-161`, günlük `:139` ve pano `--kaynak` satırı
  "`:583` `GPIO_OUTPUT_SET(CS, 1)`" diyor. IDF `v4.4.7`'de 583–608 `psram_2t_mode_enable()` içinde, `#if CONFIG_SPIRAM_2T_MODE` (satır
  495–669) bloğunda; Arduino 2.0.17 `sdkconfig:747` bu ayarı **kapalı** tutuyor, yani o kod derlenmiyor. Gerçek yol: `psram_enable()`
  → CLK 17'ye `SPICLK_OUT` (`:914`, 80 MHz kipi, `sdkconfig:682`), `psram_gpio_config()` → CS 16'ya `SPICS1_OUT` (`:761`), iki pin
  `PIN_FUNC_GPIO` (`:779-780`), ID iki kez okunur, geçersizse `ESP_FAIL` (`:944-953`). Sonuç (16 SPI CS'si = boşta HIGH, 17 saat) aynı;
  yalnız atıf yanlış.
- **Ek:** PSRAM bulunamayınca Arduino `pinMatrixOutDetach(16 / 17)` ile pinleri `SIG_GPIO_OUT_IDX`'e bağlar (`esp32-hal-psram.c:69-76`,
  `esp32-hal-matrix.c`). O andan sonra pin, GPIO çıkış kaydını (0) çıkarır; çıkış sürücüsünün açık kalıp kalmadığı ROM'un `gpio_matrix_out`
  davranışına bağlı, kaynağı yok. Yani 16 / 17 firmware `pinMode` çağırana kadar **LOW sürülü kalabilir**; "≤ 1 ms tahmini" (`:217`, `:55`)
  bu durumda kısa kalır. 1 kΩ seri dirençle çekişme yine ≤ 3,3 mA (aşağıda B3), zararsız. Ayrıca yoklama yalnız D0WDQ6'da değil,
  D0WD-V3 (WROOM-32D / 32E) paketinde de aynı pinlerle yapılır (`:860-863`, Q5 = D0WD).
- **Öneri:** atıflar `spiram_psram.c:761, 779-780, 914, 944-953` olsun (pano `--kaynak` dahil); `:217` "yoklama süresince 16 HIGH / 17 saat;
  sonrasında firmware ayarlayana kadar LOW sürülü kalabilir (doğrulanmadı)".
- **Sınıf:** durdurmaz (enkoder pini; pano protokolü madde 3 gereği gönderimden önce düzeltilmeli).

### B2. GPIO4 ve indirme kipi: belge yok, ama en kötü makul durum zararsız

- Kendi kaynağım: DS v5.3 Ek A IO_MUX (görüntüden okundu): GPIO4 (pin 24) "At Reset: oe=0, ie=1, wpd", "After Reset: oe=0, ie=1, wpd";
  Function0 = GPIO4; Function3 = HS2_DATA1, Function4 = SD_DATA1 (SDIO slave). Tablo 3-1 strapping listesinde değil. Arduino 2.0.17
  `sdkconfig:64-65`: `BOOTLOADER_FACTORY_RESET` ve `APP_TEST` kapalı (ESP-IDF'in fabrika sıfırlama pini varsayılanı 4'tür; kapalı olduğu
  için ikinci aşama yükleyici 4'e pull-up koymaz). `pins_arduino.h:34` T0 = 4 yalnız `touchRead` ile.
- İndirme kipinde ROM SDIO slave'i hazırlıyor (esptool belgesi: `DOWNLOAD_BOOT(UART0/UART1/SDIO_REI_REO_V2)`); ROM'un pinlere ne
  yaptığına Espressif kaynağı bulamadım. SDIO slave DAT1'i ancak ana birimin saati (CLK = GPIO14, burada BTS girişi, saat vermez) ve
  komutuyla sürer; kesme işareti DAT1'i LOW çeker. En kötü makul durum ROM'un pull-up açması: 10 kΩ ile ≈ 0,6–0,75 V, 4,7 kΩ ile ≈ 0,35 V.
  T2 (c) bunu ölçüyor; doğru sırada. **Durdurmaz**; R1'in 4,7 kΩ önerisi bu durumu da kapatır.
- Arama sırasında "GPIO_STRAP kaydı GPIO4'ü de örnekler ama hiçbir açılış kipi kullanmaz" diyen eski bir esptool cümlesinin özeti
  görüldü; resmî sayfada birebir bulamadım (doğrulanmadı). Doğruysa da sonucu değiştirmez.

### B3. 16 / 17'de enkoder + 1 kΩ: hesap doğru, kenarları bozmaz; PCNT bölünmesi sorun değil

- Çekişme: itme-çekme enkoder HIGH, pin LOW (ya da tersi): 3,3 V / 1 kΩ ≤ **3,3 mA** (pin ve enkoder çıkış direnci eklenince daha az).
  Kesintisiz sürse de dirençte ≈ 11 mW. Doğru.
- Kenar: JGB37-520 12 V 60 dev/dk (`maliyet.json:33`). Enkoder çözünürlüğü ve motor devri depoda yok; tipik 11 darbe / motor turu ve
  ≈ 10.000 dev/dk boşta motor devri varsayımıyla (satıcı sayfası açılmadı, **doğrulanmadı**) kanal başına ≈ 11 × 10.000 / 60 ≈ 1,8 kHz
  (14,6 V'ta ≈ 2,2 kHz), periyot ≈ 450 µs. 1 kΩ × (pin birkaç pF + ~1 m kablo ~100 pF) ≈ 0,1 µs: dört kat yüksek varsayımda bile ihmal
  edilir. Açık kollektörde asıl yavaşlatan dahili 45 kΩ pull-up (45 kΩ × 100 pF ≈ 4,5 µs), 1 kΩ değil; yine sorun değil. LOW seviyesi
  ≈ 0,07 V (rapordaki hesap doğru).
- PCNT: ESP32'de PCNT darbe ve denetim girişleri GPIO matrisi üzerinden her pine bağlanır; A / B'nin 18 + 17 ve 16 + 15 olarak
  ayrılması sayaç açısından fark etmez. GPIO15 (MTDO) açılışta enkoderce LOW tutulursa yalnız ROM açılış yazısı susar (DS Tablo 3-4);
  doğru.
- Not: 16 / 17 IO_MUX'ta **VDD_SDIO** güç alanında (DS Ek A, pin 25 / 27). WROOM'da VDD_SDIO 3,3 V; GPIO12 açılışta HIGH olursa 1,8 V'a
  düşer ve 3,3 V enkoder bu pinlere gerilim basar. 12'nin boş kalıp wpd ile LOW kalması bunu da koruyor; bilgi.

### B4. "Daha iyi çözüm kaçtı mı" ve "en az dört iş": tuttu

- Kendi sayımım (betik, `pin-haritasi.md` §9 JSON): 24 pin, tekrar yok; dışarıdaki 25 GPIO'dan boş yalnız **12**. Röle için ölçüt
  (reset boyunca LOW ya da yüzer + dış pull-down, strapping değil, hiçbir çekirdek sürümünde ve varsayılan kütüphanede çıkış değil):
  - **19:** her iki çekirdekte VSPI MISO = giriş (`esp32-hal-spi.c:232` 2.0.17; `pins_arduino.h:14` 3.x'te de MISO = 19); UART
    varsayılanı değil (U0CTS yalnız IO_MUX işlevi). Reset: oe=0 ie=0 → ie=1, çekme yok (görüntüden). Dış 10 kΩ ile kaçak: IIL / IIH en
    çok 50 nA (DS Tablo 5-3) ve IRLZ44N IGSS ±100 nA → ≤ 1,5 mV. **Geçer.**
  - **4:** 2.0.17'de geçer; 3.x'te `Serial2` RX (R1: sürmez, pull-up açar). Yine de kalan adaylardan iyidir: 25 / 26 / 27 3.x'te TX1 / TX2
    (sürer), 18 / 23 SPI çıkışı, 21 / 22 I2C, 5 / 14 / 15 wpu, 2 / 12 strapping, 13 EN, 16 / 17 PSRAM + 2.x UART2.
  - Böylece iki röle için iki yeni güvenli pin gerekir, boş güvenli pin yok; her röle bir işi yerinden eder, yerinden edilen iş 16 / 17'ye
    gider: **en az dört iş** iddiası doğru. 12'yi kullanan üç işlik seçeneğin reddi (strapping + gate arızası kartı açmaz yapar) yerinde.
- Bilgi: 3.x açısından 25 / 26 / 27'nin röleye reddedilmesi raporun yazdığından da güçlü (TX1 = 27, TX2 = 25).

### B5. BTS IS koruması (D7): yön doğru; IIS(lim) değerini bağımsız doğrulayamadım; ölçek ve kaçak notu eksik

- **IIS(lim) = 4 / 4,5 / 7 mA:** Infineon tam veri sayfasına (Rev. 1.1) bu kontrolde erişemedim (Infineon bağlantısı 404, aynalar 403;
  indirilebilen kopyalar yalnız 2 sayfalık ürün özeti ve satıcı kılavuzu). Değer yalnız ilk kontrolün aktarımı; **doğrulanmadı**. Aşağıdaki
  hesap bu aralığı varsayar.
- **Hesap (D7 topolojisi: IS → 1 kΩ → pin, pin → 1N5819 → 3V3):**
  - Kartta RIS yoksa: hata akımının tamamı 1 kΩ ve diyottan 3V3'e: 4–7 mA (IS1 + IS2 birlikte hata verirse 14 mA'e kadar). Pin
    ≈ 3,3 + VF (1N5819 birkaç mA'de ~0,2–0,3 V) ≈ 3,5–3,6 V: mutlak sınır VDD + 0,3 V'un (DS Tablo 5-3) **sınırında**.
  - Kartta her IS ucunda 1 kΩ RIS varsa (IS1 + IS2 birleşince 500 Ω): tek kanal 7 mA'de düğüm ≈ 3,5 V, diyottan akım ≈ 0; pin ≈ 3,5 V.
  - 3V3 hattına geri basma: en çok ≈ 2 × 14 mA; ESP32'nin kendi tüketimi (onlarca mA) bunu emer, regülatör hattı yükselmez (hesap,
    ölçülmedi).
- **Ölçek:** D7 "2,8 A ≈ 0,33 V" diyor; bu tek 1 kΩ RIS ve kILIS 8500 (forum alıntısı, doğrulanmadı) varsayımı. IS1 + IS2 aynı pine bağlı
  ve kartta iki RIS varsa paralel 500 Ω → ≈ 0,165 V. Ayrıca 1N5819'un ters kaçağı (3 V ters gerilimde onlarca µA'ya kadar, sıcaklıkla
  artar; veri sayfası 25 °C'ta 40 V'ta en çok 1 mA) RIS üstünde 10–50 mV kayma yapabilir: 0,17 V'luk sinyalde %5–30. "Normal ölçümde fark
  edilmez" (`:270`) iddiası bu yüzden zayıf.
- **Öneri:** D7'ye "IIS(lim) değeri kontrol aktarımı, veri sayfasından teyit"; Schottky olarak düşük kaçaklı küçük sinyal diyodu (ör. BAT54
  sınıfı) ya da kaçak T6'da ölçülüp kalibrasyona alınması; ölçek için "kartta RIS varsa IS1 + IS2 paralelinde 500 Ω" notu. Sınıf:
  durdurmaz (ESP32 pini hasarı ve ölçüm doğruluğu, motor / röle değil).

### B6. Eski `main` firmware'i yeni kablajda: K2 zinciri yazılmamış

- `pin-haritasi.md:185-189` K1'in 0 V kalmasından "bara enerjisiz, motor dönemez" diyor. Tam zincir: `main` 19'a `INPUT_PULLUP` verir
  (`motorlar.cpp:206`) → K2 gate 0,60–0,75 V. K2 bir an iletirse bara 5,6 Ω ön şarj direncinden beslenir; aynı firmware 13'ü ve 27'yi
  HIGH yapar (`:216-217`; 27 artık sağ IN1), 14'e dokunmaz (reset sonrası wpu). Sağ BTS'te IN1 HIGH, IN2 zayıf HIGH ya da kartın kendi
  çekmesine göre LOW: LOW okunursa sağ motorlar ön şarj direnci üstünden ileri sürülür ve direnç aşırı yüklenir. Olasılık düşük (K2'nin
  0,75 V'ta iletmesi gerekir), ama metin "K1 çekmediği için" diye tek yolu yazıyor. R1'deki 4,7 kΩ bu zinciri de 0,35 V'a indirir.
- **Öneri:** §3.1'e K2 yolu bir cümle. Sınıf: durdurmaz (Y1 kuralı zaten bu firmware'i yasaklıyor), ama R1 düzeltmesiyle birlikte yazılmalı.

### B7. Günlük §7'de sürüm 1'in döngü girdisi işaretsiz duruyor

- `pin-karari-gunluk.md:116`: "Kayda girecek" bölümünde "Efe'nin önerisi … aynen alındı: **K1 GPIO16, K2 GPIO17** …". Başlık (`:7`)
  "§5–§7 düzeltme turu 1'e göre güncellendi" diyor; C adımı §7'yi olduğu gibi kopyalarsa `dongu-158.md`'ye eski röle pinleri girer
  (doğru girdi `:174`'te). `:46` ve `:58-59` (§3, §4) sürüm 1 kaydı olarak etiketli, sorun değil.
- **Öneri:** `:116`'ya "(sürüm 1; geçersiz, yerine §8.4'teki girdi)" ya da satırın kaldırılması. Sınıf: durdurmaz; C adımından önce düzeltilmeli.

### B8. Küçük metin noktaları

- `pin-haritasi.md:60` "LED'in GPIO2'de olduğu … EL:458'de yazıyor": EL:458 artık K2 taşıma paragrafı; LED'i "DevKit LED'i" diye anıyor,
  atıf hâlâ tutuyor (bilgi).
- `pin-haritasi.md:53-54` "D0WDQ6 paketinde": yoklama D0WD(-V3) paketinde de aynı (B1). Bilgi.
- `pin-haritasi.md:20`: errata madde numaraları kontrol edilmedi (ilk kontrol doğrulamıştı; değişmedi).

## İlk kontrolün N1–N9 bulguları

| Bulgu | Durum | Not |
|---|---|---|
| D1 (17 = Serial2 TX) | **kapandı** | 2.0.17 `HardwareSerial.h:167-179` doğrulandı; K2 artık 19. Ama 3.x'te UART2 varsayılanı 4 / 25'e taşınmış: R1 |
| D2 (PSRAM yoklaması) | **kapandı** (röle açısından) | Röleler 16 / 17'de değil; atıf satırları yanlış (B1) |
| N1 IS hata akımı | kısmen | D7 eklendi, "her durumda"; değer bağımsız doğrulanamadı, ölçek / kaçak notu eksik (B5) |
| N2 satır atıfları | kapandı | `kanallar.yaml:61-73` (`main` `2be1c63`: 61 `kanallar:`, 63–67, 69–73), EL:494 PCA satırı, EL:26, EL:130-131, `elektrik.md:466-496` doğru |
| N3 satır kayması | kayıtlı açık iş | `baski-listesi.md:286` hâlâ `elektrik.md:499` (boş satır); doğru hedef 505 ("Kabuk", E7 yarıkları). Günlük §8.4'te C adımına yazılmış; `F4c-partiler.py:127` aynı |
| N4 modül / T1 | kapandı | §1 ve T1 doğru; T1 artık işlev şartı |
| N5 0,6 V tipik | kapandı | İki değer yazılmış; K2 zinciri eksik (B6) |
| N6 3.x sırası | kapandı | 3.0.7 `esp32-hal-gpio.c:173-177` doğrulandı ("IO %i is not set as GPIO") |
| N7 GPIO14 darbesi | kapandı | "kaynaksız topluluk gözlemi; T3" |
| N8 §6.1 cümlesi | kapandı | `:281-282` açık |
| N9 pano taslağı | kapandı (R1 hariç) | Takma ad yok; gövde 2.412 karakter; #21'in pano #6'da olduğu yazılı; `--kaynak` satır numaralı (B1'deki IDF satırı hariç) |

## Doğruladıklarım

- **IO_MUX (DS v5.3 Ek A s. 69, görüntüden):** GPIO4 wpd → wpd (ie=1); GPIO19 oe=0 ie=0 → ie=1; GPIO16 / 17 oe=0 ie=0 → ie=1, güç alanı
  VDD_SDIO; MTCK (13) oe=0 ie=0 → ie=1 wpd; MTMS (14) oe=0 ie=0 → ie=1 wpu; MTDI (12) wpd / wpd; MTDO (15) wpu / wpu; GPIO2 wpd / wpd;
  GPIO5 wpu / wpu; 25 / 26 / 27 / 32 / 33 oe=0 ie=0 / aynı. Not 8: wpu / wpd ~75 µA; not 9: reset sırasında bütün çıkışlar kapalı;
  not 10: sonra Function 0. Raporun §2 "reset sırasında → sonrası" sütunu bunlarla aynı.
- **DS Tablo 5-3:** VIH en çok VDD + 0,3 V; IIH / IIL en çok 50 nA.
- **Arduino 2.0.17:** `HardwareSerial.h` RX2 / TX2 = 16 / 17; `sdkconfig:683-684` (`CONFIG_SPIRAM=y`, `BOOT_INIT` kapalı), `:730-731`
  (CLK 17, CS 16), `:747` 2T kapalı, `:64-65` fabrika sıfırlama / test pini kapalı; `esp32-hal-misc.c` `initArduino` → `psramInit()`;
  `esp32-hal-psram.c:57-76`; `esp32-hal-spi.c:193-194` SCK `OUTPUT`, `:232` MISO `INPUT`, `:270` MOSI `OUTPUT`; `SPI.cpp:93-101` VSPI
  18 / 19 / 23 / 5, HSPI 14 / 12 / 13 / 15; `pins_arduino.h` SS 5, MOSI 23, MISO 19, SCK 18, T0 = 4.
- **Kod (`main` `2be1c63`):** `platformio.ini:8` `espressif32@6.9.0` (2.0.17); `pinler.h` eski tablo (25 / 26 / 27 sol, 32 / 33 / 13 sağ,
  18 / 19 / 16 / 17 enkoder, 2 LED); `motorlar.cpp:205-208` dört enkoder `INPUT_PULLUP`, `:216-217` iki EN HIGH, `:105-113, 140-146` PWM.
- **Tutarlılık:** rapor §2 tablosu, §9 JSON (`json.loads` geçti, ASCII, 24 pin, tekrar yok), `elektrik.md:472-492` ve pano gövdesi satır 5
  pin pin aynı (36 / 39 / 34 / 35 / 32 / 33 / 25 / 26 / 27 / 14 / 13 / 4 / 19 / 23 / 5 / 21 / 22 / 18 / 17 / 16 / 15 / 1 / 3 / 2; 12 boş). Bir pine
  iki iş ya da bir işe iki pin yok. Üç depo dosyasında eski GPIO12 / GPIO2 röle atfı yalnız tarihçe sütununda (`elektrik.md:106`) ve
  "14.11'e dek" notlarında; 16 / 17 röle atfı yalnız sürüm 1 kaydı olarak (günlük `:5`, `:46`, `:58`; rapor `:154`) ve B7'deki satırda.
- **PCA9685:** `main` `kanallar.yaml:61-73` 10 kanallı blok düzen; `:13-14` 10–12'yi sonar trig için ayırıyor; tablo ve pano sorusu doğru
  çelişkiye dayanıyor, sonar trig 10 / 11 / 12 başka işle çakışmıyor.
- **`elektrik.md` farkı:** yalnız pin / röle pin adları, BTS7960B adları, pin planı bölümü ve açık işler 4 / 19 değişmiş; 220 Ω, 10 kΩ,
  5,6 Ω 11 W, F1–F5, akım, kablo değerleri aynı. Sürüm 2 turunda satır sayısı 522'de kaldı; `elektrik.md:499` atfı N3'teki gibi bozuk.
- **Firmware dizisi (Y4 / Y5) ve `elektrik.md` E9 dizisi** 19 → 4 → 19 sırasıyla tutarlı.
- **Pano protokolü:** bilgi + soru, durum `soru`, YZ karar seçmiyor (madde 4); "Ahmet'in insan oturumuyla teyidi önerilir" notu taslakta.
- **Gizlilik:** üç depo dosyasında ve pano taslağında yerel yol, makine adı, takma ad, e-posta, parola / anahtar, ağ adı yok; kişi adları
  yalnız Ahmet / Efe.

## Bakamadıklarım / kaynağını bulamadıklarım

- **Infineon BTS 7960 tam veri sayfası** (IIS(lim), kILIS, IS gerilim sınırı): erişilemedi; B5'teki değerler aktarım.
- **ESP32 ROM'un indirme kipinde SDIO pinlerine (2, 4, 12–15) ne yaptığı** ve ROM `gpio_matrix_out`'un çıkış sürücüsünü açıp açmadığı:
  ROM kaynağı yayımlanmamış; T2 ölçüyor.
- **VBsemi IRLZ44NPBF-VB eşik gerilimi:** belge bulunamadı. Bilgi: VBsemi'nin benzer adlı parçalarında 1,9 V ve 3 V geçiyor; 3 V'a yakınsa
  3,3 V gate sürüşünde rölenin güvenilir çekmesi de ayrıca sorgulanmalı (pin kararının dışında; T2 (f) gate ve bobin ölçümüyle görülür).
- **JGB37 enkoderinin darbe sayısı ve motor devri:** satıcı sayfası açılmadı; B3'teki frekans varsayım.
- Arduino 3.x'in açılışta (PSRAM ve başka) 4 / 19'a dokunup dokunmadığını `initArduino` düzeyinde okumadım; yalnız UART / SPI
  varsayılanlarını okudum.
- Pano mesajları (#19, #20, pano #6 #21) okunmadı (brief gereği).
- Wi-Fi sürücüsünün ADC2 kalibrasyonu sırasında RTC pedlerine (GPIO4 = ADC2_CH0) çıkış verip vermediği: kaynak aramadım; çıkış verdiğine
  dair bir bilgiye de rastlamadım.

## Kaynaklar (bu kontrolde açılanlar)

- Espressif *ESP32 Series Datasheet* v5.3 (Ek A IO_MUX s. 69 görüntüden; Tablo 3-1, 5-3; Ek A not 8–10).
- `espressif/arduino-esp32` `2.0.17`: `cores/esp32/HardwareSerial.h`, `esp32-hal-misc.c`, `esp32-hal-psram.c`, `esp32-hal-matrix.c`,
  `esp32-hal-spi.c`, `libraries/SPI/src/SPI.cpp`, `variants/esp32/pins_arduino.h`, `tools/sdk/esp32/sdkconfig`; `3.0.7` / `3.1.1` / `3.2.0` /
  `3.3.0`: `cores/esp32/HardwareSerial.h`, `variants/esp32/pins_arduino.h`; `3.0.7`: `esp32-hal-uart.c`, `esp32-hal-gpio.c`.
- `espressif/esp-idf` `v4.4.7`: `components/esp_hw_support/port/esp32/spiram_psram.c`, `components/esp_rom/include/esp32/rom/gpio.h`,
  `components/driver/uart.c`; `v5.1.4`: `components/driver/uart/uart.c`.
- esptool belgesi "Boot Mode Selection" (ESP32), docs.espressif.com.
- Depo: `origin/main` `2be1c63` (`platformio.ini`, `pinler.h`, `motorlar.cpp`, `kanallar.yaml`), `planlama/maliyet.json`,
  `planlama/baski-listesi.md:286`, çalışma ağacındaki `elektrik.md`, `pin-haritasi.md`, `pin-karari-gunluk.md`.
