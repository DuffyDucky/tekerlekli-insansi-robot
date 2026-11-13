# Lale: ESP32 pin haritası (kesin)

Sürüm 3, 14.11.2026. Sürüm 1 ve 2 aynı gün yazıldı. Bağımsız kontroller düzeltme istedi: `planlama/d158/pin-karari-kontrol.md` (§3.1) ve
`planlama/d158/pin-karari-kontrol-2.md`; üçüncü kontrol `pin-karari-kontrol-3.md` GEÇER dedi (metin notları C adımında işlendi). Sürüm 3'te pinler değişmedi; değişenler gate direnci, IS koruması, röle MOSFET şartı ve çekirdek
sürümü kuralı. Sınanan çekirdek sürümleri: Arduino-ESP32 **2.0.17** (projenin çekirdeği) ve **3.0.7 / 3.3.0** (UART varsayılanları).
**Karar: Ahmet'in 13.11.2026 yetkilendirmesiyle** ("kararını sen oluşturabilirsin, projede ona uyarız"; pano #8 sorusunun cevabı).
Bu dosya pin haritasının tek yazılı kaynağıdır, ta ki `kod/ortak/pinler.json` açılıp `pinler.h` ve `elektrik.md` tablosu ondan üretilene
kadar (§9). `elektrik.md` "Pin planı" bölümü bu tabloyla aynıdır.

Okuyucu: firmware'i yazacak olan (Efe ve Efe'nin Claude'u). Bu dosya tek başına okunup firmware yazılabilsin diye yazıldı; donanım
şartları ve "kablajda teyit edilecek" maddeleri montaj içindir.

**Röle kuralı (bu sürümün temeli):** röle gate'leri yalnız hiçbir açılış kodunun ve hiçbir varsayılan çevre biriminin sürmediği, reset
boyunca kendiliğinden LOW kalan pinlere bağlanır. Bu, projenin çekirdeği (2.0.17) için kaynakla sınandı. 3.x'te GPIO4 `Serial2`'nin RX
varsayılanıdır (sürmez; 3.0.7 pull-up açar, 3.3.0 açmaz); bu yüzden UART'lar hiçbir sürümde varsayılan pinlerle açılmaz (Y1) ve çekirdek sürümü sabittir (Y13).
Gate pull-down'ı 4,7 kΩ: dahili pull-up açılsa da gate 0,5 V'un altında kalır (§6 D1).

Kaynak kısaltmaları:

| Kısa | Kaynak |
|---|---|
| DS | Espressif, *ESP32 Series Datasheet* v5.3 (2026.07). §2.3.1, §2.6 Tablo 2-5/2-6, §3 Tablo 3-1…3-5 (Tablo 3-2 "Joint Download Boot": SDIO + UART), Tablo 5-1, Tablo 5-3 (VOH ≥ 0,8 VDD = 2,64 V; RPU / RPD 45 kΩ tipik, en az değer yok; IIH / IIL ≤ 50 nA), Ek A not 8 (wpu / wpd ~75 µA), 9, 10, Ek A.4 IO_MUX |
| ER | Espressif, *ESP32 Series SoC Errata* v3.1: [GPIO-3.11] (madde 3.12), [GPIO-3.14] (madde 3.11), [RES-3.4] (madde 3.13) |
| W32E | Espressif, *ESP32-WROOM-32E & WROOM-32UE Datasheet* v2.1: Tablo 1 (sürümler; çip D0WD-V3 / D0WDR2-V3, PSRAM'li sürümler yalnız R2), pin tablosu notu 3 |
| W32D | Espressif, *ESP32-WROOM-32D & WROOM-32U Datasheet* v2.8: çip ESP32-D0WD; pin düzeni (IO16 pin 27, IO17 pin 28) |
| WRV | Espressif, *ESP32-WROVER-E & WROVER-IE Datasheet* v2.4: Şekil 5 pin düzeni (pin 27, 28 = NC), sürüm tablosu (18,0 × 31,4 mm) |
| IDF | ESP-IDF GPIO API sayfası (docs.espressif.com, esp32, sürüm v6.1): strapping, SPI0/1, GPI, ADC2 ve Wi-Fi, JTAG notları |
| ADC | ESP-IDF v4.4.7 ADC sayfası (esp32): ölçülebilir aralık 0 dB 100–950 mV, 2,5 dB 100–1250 mV, 6 dB 150–1750 mV, 12 dB 150–2450 mV |
| AR | Arduino-ESP32 **2.0.17** kaynağı (projenin `platform = espressif32@6.9.0`, `kod/esp32/platformio.ini:8`): `cores/esp32/HardwareSerial.h:167-179` (RX2 = 16, TX2 = 17), `tools/sdk/esp32/sdkconfig:683-684` (`CONFIG_SPIRAM=y`, `SPIRAM_BOOT_INIT` kapalı), `:730-731` (PSRAM CLK = 17, CS = 16), `:747` (`SPIRAM_2T_MODE` kapalı), `:64-65` (fabrika sıfırlama / test pini kapalı), `cores/esp32/esp32-hal-misc.c:246` (`initArduino` → `psramInit`), `cores/esp32/esp32-hal-psram.c:57-76`, `cores/esp32/esp32-hal-spi.c:194, 232, 270` (SCK ve MOSI çıkış, MISO giriş), `libraries/SPI/src/SPI.cpp:93-101`, `variants/esp32/pins_arduino.h` (SS 5, MOSI 23, MISO 19, SCK 18, SDA 21, SCL 22, T0 = 4) |
| AR3 | Arduino-ESP32 **3.0.7** `cores/esp32/HardwareSerial.h:151-152, 169-170, 191-192, 199-200` ve **3.3.0** aynı dosya `:194-195, 216-217, 242-243, 250-251`: ESP32'de **RX1 = 26, TX1 = 27, RX2 = 4, TX2 = 25**. ESP-IDF v5.1.4 `components/driver/uart/uart.c:615-623` (`uart_set_pin`: TX pini HIGH başlatılır, RX pinine pull-up açılır; 3.0.7 bunu kullanır). 3.3.0 kendi pin işlevini kullanır, RX'e pull-up koymaz (üçüncü kontrol Ö4: `esp32-hal-uart.c:353-418`; ben okumadım) |
| IDF44 | ESP-IDF v4.4.7 `components/esp_hw_support/port/esp32/spiram_psram.c`: `:111-112` (D0WD CS 16 / CLK 17), `:761` (CS → `SPICS1_OUT`), `:779-780` (CS pinleri GPIO işlevine), `:860-863` (D0WDQ6 / D0WD paketinde bu pinler seçilir), `:914` (CLK 17 → `SPICLK_OUT`), `:944-953` (kimlik iki kez okunur, geçersizse `ESP_FAIL`) |
| BTS | Infineon, *BTS 7960 Data Sheet* Rev. 1.1 (2004-12-07) §4.4.5–4.4.7: INH = 0 → iki anahtar kapalı; IIS(lim) en az 4, tipik 4,5, en çok 7 mA; kILIS 8500 (nominal). **IIS(lim) ikinci elden** (ilk kontrolün aktarımı); tam veri sayfasını açamadım: hesapta en kötü değer 7 mA, iki IS birlikte 14 mA |
| MOS | Alpha & Omega *AO3400A* veri sayfası: VDS 30 V, VGS(th) 0,65 / 1,05 / 1,45 V (ID 250 µA), RDS(on) < 48 mΩ (VGS 2,5 V). Infineon *IRLML6344TRPbF*: VDS 30 V, VGS(th) 0,5 / 0,8 / 1,1 V, RDS(on) en çok 37 mΩ (VGS 2,5 V). Infineon *IRLZ44NPbF*: VGS(th) 1,0–2,0 V, RDS(on) yalnız 4–10 V gate'te tanımlı |
| EL | `planlama/adim3/elektrik.md` (E2, E3, E9, blok şema, pin planı) |
| PH | `kod/esp32/include/pinler.h`, `main` dalı `2be1c63` |
| MC | `kod/esp32/src/motorlar.cpp`, `main.cpp`, `main` `2be1c63` |
| KY | `kod/jestler/kanallar.yaml`, `main` `2be1c63` |
| MJ | `planlama/maliyet.json` (ESP32, BTS7960B, röle MOSFET'i :106, K1 :107, K2 :109, direnç seti :115) |
| P8 | Pano #8, mesaj #19 (soru, 10.11) ve #20 (Efe'nin tarafının cevabı, 13.11) |

Espressif belgeleri ve Arduino-ESP32 / ESP-IDF kaynakları 14.11.2026'da Espressif'in resmî belge sitesinden ve GitHub depolarından
(etiket `2.0.17`, `3.0.7`, `3.3.0`, `v4.4.7`, `v5.1.4`) indirildi ve okundu. MOSFET veri sayfaları üreticilerin sitesinden indirildi.

## 1. Kart ve modül

- **Alınacak kart:** "ESP32 Wi-fi + Bluetooth Geliştirme Kartı (30 pin, CP2102)", Robocombo (MJ "Alt kontrolcü"; `planlama/d158/F8a-siparis.md` S53).
  Satıcı sayfası (14.11 okundu) çipi **ESP32-D0WDQ6** diye yazıyor; modül adı, PSRAM, flash boyu, LED pini ve pin diyagramı **yazmıyor**.
  Yedek satıcı Direnc.net "ESP32-WROOM-32D" (MJ `alt`). Proje belgeleri kartı "ESP32-WROOM-32 DevKit 30 pin" diye anıyor
  (`tasarim/freecad/taban/taban_parcalar.py:472`, `planlama/yazilim-plani.md:29`, PH başlığı).
- **Çipten çıkan:** D0WDQ6 doğruysa modül yalnız **eski ESP32-WROOM-32** ya da **eski bir WROVER** olabilir. WROOM-32D'nin çipi D0WD
  (W32D), WROOM-32E'ninki D0WD-V3 / D0WDR2-V3 (W32E Tablo 1; PSRAM'li 32E sürümleri yalnız R2, R8 yok).
- **Modül türü güvenlik şartı değil, işlev şartıdır.** Röleler 4 ve 19'da; ikisi de her modülde serbest. PSRAM'li modülde etkilenen
  yalnız 16 / 17'deki iki enkoder kanalıdır:
  - WROVER-E'de modülün 27 / 28 numaralı ayakları (WROOM'da IO16 / IO17) **NC** (WRV Şekil 5): sağ enkoder A ve sol enkoder B çalışmaz.
  - WROOM-32E **N4R2 / N8R2 / N16R2**'de **IO16 paket içi PSRAM'in CS'sine bağlı** (W32E pin notu 3): sağ enkoder A çalışmaz ve
    PSRAM'i bozabilir.
  - Her iki durumda kart PSRAM'siz bir kartla değiştirilir (T1). Röle tarafı etkilenmez.
- **PSRAM'siz kartta da 16 / 17 açılışta sürülür (AR, IDF44):** derleme ortamının hazır ayarlarında PSRAM desteği açık; `setup()`'tan önce
  çekirdek PSRAM'i yoklar. D0WDQ6 ve D0WD(-V3) paketinde CS = 16 (SPI CS çıkışı, boşta HIGH) ve CLK = 17 (SPI saati) olur
  (IDF44 `:761, 779-780, 860-863, 914`). Kimlik okunamazsa (`:944-953`) Arduino 16 / 17'yi GPIO çıkış sinyaline bağlar
  (`esp32-hal-psram.c:69-76`); bu andan sonra pinler firmware `pinMode` çağırana kadar **LOW sürülü kalabilir (doğrulanmadı;** ROM'un
  `gpio_matrix_out` davranışının kaynağı yok). Yoklamanın süresi ölçülmedi. Bu yüzden 16 / 17'de yalnız giriş var ve seri direnç şart (§6 D6).
- **Revizyon:** ER [RES-3.4]: v0.0 çipte brown-out reset'ten sonra açılış olmaz (güvenli yöne düşer, röle bırakık; ama robot güç kesilmeden
  geri gelmez). T1'de revizyon okunur.
- **30 pinli DevKit'te dışarı çıkan GPIO'lar:** satıcı belgesi yok. Yaygın 30 pinli düzende 25 GPIO dışarıdadır: 36, 39, 34, 35, 32, 33, 25, 26, 27,
  14, 12, 13 (bir yan) ve 23, 22, 1, 3, 21, 19, 18, 5, 17, 16, 4, 2, 15 (öbür yan); GPIO0 ve 6–11 dışarıda değildir. Bu tablo yalnız bu 25'i kullanır.
  **Kart gelince serigrafiden teyit (T1).** Kart üstü mavi LED'in GPIO2'de olduğu yalnız PH ve EL:458'de yazıyor, kart belgesiyle doğrulanmadı.

## 2. Kesin tablo

"Reset sırasında → sonrası" sütunu DS Ek A.4 IO_MUX tablosundan: reset sırasında bütün pinlerin çıkışı kapalıdır (Tablo 6-1 not 9); reset
bitince her pin "Function 0"a döner (not 10). wpu / wpd = dahili zayıf pull-up / pull-down, 45 kΩ tipik (DS Tablo 5-3). "Yüzer" = çıkış
kapalı, dahili çekme yok. "Açılışta / varsayılan olarak süren" sütunu: firmware'in `setup()`'ından önce ya da varsayılan bir kütüphane
çağrısında pine dokunan kod; aksi yazmadıkça 2.0.17 (AR, IDF44), "3.x" yazanlar AR3.

| GPIO | Yön | İşlev | Bağlı parça / uç | Reset sırasında → sonrası (DS A.4) | Açılışta / varsayılan olarak süren | Donanım şartı | Not |
|---|---|---|---|---|---|---|---|
| 36 (VP) | giriş, analog | Akü gerilimi | 100 kΩ / 18 kΩ bölücü + 100 nF, ana anahtar sonrası (EL E2) | yüzer (yalnız giriş) | – | bölücü | ADC1_CH0 |
| 39 (VN) | giriş | Sonar **sağ** echo | HC-SR04 sağ, seri 4,7 kΩ + toprağa 10 kΩ (EL E2) | yüzer (yalnız giriş) | – | bölücü | ER [GPIO-3.11]: ADC açılırken ~80 ns LOW (Y9) |
| 34 | giriş | Sonar **orta** echo | HC-SR04 orta, aynı bölücü | yüzer | – | aynı | yalnız giriş |
| 35 | giriş | Sonar **sol** echo | HC-SR04 sol, aynı bölücü | yüzer | – | aynı | yalnız giriş |
| 32 | giriş, analog | Sol BTS akım (IS1 + IS2 birlikte) | sol BTS7960B kartı IS1, IS2 | yüzer | – | **IS bölücüsü zorunlu (D7)** | ADC1_CH4: Wi-Fi açıkken de okunur (IDF) |
| 33 | giriş, analog | Sağ BTS akım (IS1 + IS2) | sağ BTS7960B kartı IS1, IS2 | yüzer | – | **IS bölücüsü zorunlu (D7)** | ADC1_CH5 |
| 25 | çıkış, PWM | Sol motor **ileri** | sol BTS7960B **IN1** (IBT-2 düzeninde RPWM) | yüzer → yüzer | 2.0.17: yok (DAC1 yalnız çağrılırsa). **3.x: `Serial2` TX varsayılanı** (sürer, HIGH) | yok (EN LOW iken zararsız). **3.x'te robot devredeyken (EN HIGH) varsayılan `Serial2` açılırsa sol motor tam yol ileri döner; bunu yalnız Y1 ve Y13 önler, donanım önlemez** | Y1 |
| 26 | çıkış, PWM | Sol motor **geri** | sol BTS7960B **IN2** (LPWM) | yüzer → yüzer | 2.0.17: yok (DAC2 yalnız çağrılırsa). **3.x: `Serial1` RX varsayılanı** (3.0.7'de pull-up) | yok | Y1 |
| 27 | çıkış, PWM | Sağ motor **ileri** | sağ BTS7960B **IN1** (RPWM) | yüzer → yüzer | 2.0.17: yok. **3.x: `Serial1` TX varsayılanı** (sürer, HIGH) | yok (EN LOW iken zararsız). **3.x'te EN HIGH iken varsayılan `Serial1` açılırsa sağ motor tam yol ileri döner; bunu yalnız Y1 ve Y13 önler, donanım önlemez** | Y1 |
| 14 | çıkış, PWM | Sağ motor **geri** | sağ BTS7960B **IN2** (LPWM) | yüzer → **wpu**, MTMS | HSPI SCK (yalnız `SPIClass(HSPI)` açılırsa) | yok (EN LOW iken zararsız) | Topluluk gözlemi: açılışta kısa darbe (kaynaksız; T3) |
| 13 | çıkış | **BTS EN**, dört uç ortak | sol EN1 + EN2, sağ EN1 + EN2 (IBT-2'de R_EN, L_EN) | **yüzer** → wpd, MTCK | HSPI MOSI (yalnız HSPI açılırsa) | **10 kΩ → GND zorunlu** | Motorun tek kilidi (§4) |
| **4** | çıkış | **Röle K1 "devreye al"** | röle MOSFET'i #1 gate (EL E3; MOSFET şartı D9) | **wpd → wpd** | 2.0.17: **yok** (strapping değil; UART / SPI / I2C / PSRAM varsayılanı değil; yalnız dokunmatik T0 ve ADC2_CH0 adı). **3.x: `Serial2` RX varsayılanı** (sürmez; 3.0.7 pull-up açar, 3.3.0 açmaz) | **220 Ω seri + 4,7 kΩ gate → GND zorunlu** | İndirme kipinde SDIO DATA1 olabilir: T2 |
| **19** | çıkış | **Ön şarj rölesi K2** | röle MOSFET'i #2 gate (EL E9; D9) | yüzer → yüzer (ie=1) | **yok** (2.0.17 ve 3.x: VSPI MISO, `SPI.begin()` onu **giriş** yapar, AR `esp32-hal-spi.c:232`) | **220 Ω seri + 4,7 kΩ gate → GND zorunlu** | Dahili çekme yok: LOW'u gate direnci tutar |
| 23 | giriş | Acil stop durumu (PC817 #1): **LOW = mantar serbest**, HIGH = basılı ya da F5 attı | PC817 #1 çıkışı | yüzer → yüzer (ie=1) | VSPI MOSI (yalnız `SPI.begin()` çağrılırsa; Y11) | pull-up **yalnız 3V3'e** | Strapping değil |
| 5 | giriş | Anahtarlı bara (PC817 #2): **LOW = bara gerilimli** | PC817 #2 çıkışı | wpu → wpu | VSPI SS (yalnız SPI donanım SS'i açılırsa) | pull-up **yalnız 3V3'e** | Strapping, yalnız SDIO slave zamanlaması (DS Tablo 3-5) |
| 21 | I2C SDA | PCA9685 (0x40), BNO055 (0x28/0x29) | ortak hat | yüzer → yüzer | I2C (açık savak) | pull-up'lar 3V3'e (modül üstü) | PH ile aynı |
| 22 | I2C SCL | aynı | ortak hat | yüzer → yüzer | I2C | aynı | PH ile aynı |
| 18 | giriş | Sol enkoder A | sol arka JGB37 Hall A (3V3 beslemeli) | yüzer → yüzer | VSPI SCK (yalnız `SPI.begin()`; Y11) | enkoder 3V3'ten | PCNT (Y8) |
| **17** | giriş | **Sol enkoder B** | sol arka JGB37 Hall B | yüzer → yüzer | **evet:** PSRAM yoklamasında SPI saati (AR, IDF44); 2.0.17'de `Serial2` TX varsayılanı | **1 kΩ seri zorunlu (D6)** | PSRAM'li modülde çalışmaz (§1) |
| **16** | giriş | **Sağ enkoder A** | sağ arka JGB37 Hall A | yüzer → yüzer | **evet:** PSRAM yoklamasında CS (AR, IDF44); 2.0.17'de `Serial2` RX varsayılanı | **1 kΩ seri zorunlu (D6)** | PSRAM'li modülde çalışmaz (§1) |
| 15 | giriş | Sağ enkoder B | sağ arka JGB37 Hall B | wpu → wpu (MTDO) | HSPI SS (yalnız HSPI) | enkoder 3V3'ten | Strapping: LOW ise yalnız ROM açılış yazısı susar (DS Tablo 3-4) |
| 1 | UART0 TX | Seri → CP2102 → USB → hub → Pi | kart üstü | wpu | ROM açılış yazısı | başka iş yok | |
| 3 | UART0 RX | aynı | kart üstü | wpu | – | başka iş yok | |
| 2 | çıkış | Kart üstü durum LED'i (yalnız) | kart üstü LED | wpd → wpd | – | **dışarıya hiçbir şey bağlanmaz** | Strapping (DS Tablo 3-3) |
| 12 | – | **Boş** | hiçbir şey | wpd → wpd (MTDI) | HSPI MISO (giriş) | **hiçbir şeye bağlanmaz** | Strapping: açılışta HIGH = flash beslemesi 1,8 V (DS §3.2) |
| 0 | – | 30 pinli kartta dışarıda değil (BOOT düğmesi) | – | wpu | – | – | |
| 6–11 | – | Modül flaşı | – | – | – | kullanılmaz | DS §2.3.1, IDF |
| EN | – | Reset (CHIP_PU) | CP2102 DTR/RTS otomatik reset devresi | – | – | Pi portu DTR/RTS kapalı açar (EL E3) | Pi'den bilinçli reset hattı ayrı karar (§8) |

**PCA9685 kanalları (I2C, ESP32 pini değil; kablo tablosu için):** `main` `2be1c63` KY:61-73 ile EL:494 aynı, değişmedi.

| Kanal | Eklem (KY adı) | Güç hattı |
|---|---|---|
| 0 | `sag_omuz` (S1) | A |
| 1 | `sag_omuz_yan` (S2) | A |
| 2 | `sag_dirsek` | A |
| 3 | `sag_bilek` | A |
| 4 | `kafa_pan` | C (29.10'dan beri; sinyal kanalı aynı, EL:130-131) |
| 5 | `sol_omuz` (S1) | B |
| 6 | `sol_omuz_yan` (S2) | B |
| 7 | `sol_dirsek` | B |
| 8 | `sol_bilek` | B |
| 9 | `kafa_tilt` | C |
| 10 | Sonar **sağ** trig (yeni atama) | – (3,3 V lojik) |
| 11 | Sonar **orta** trig (yeni atama) | – |
| 12 | Sonar **sol** trig (yeni atama) | – |
| 13–15 | yedek | – |

Sonar trig sırası (10 sağ, 11 orta, 12 sol) hiçbir belgede yazılı değildi; echo sırasıyla (39 sağ, 34 orta, 35 sol) aynı yöne dizildi.
Not: pano #6 mesaj #21'deki "0–5 aynen, 6–9 = sag_omuz_yana, sag_bilek, sol_omuz_yana, sol_bilek" ifadesi `main`'in eski 6 servoluk
düzenine (`84bc2b4`) göre yazılmış görünüyor; `main` `2be1c63` zaten yukarıdaki 10 kanallı blok düzenini taşıyor (KY:61-73). Kablo tablosu
yukarıdaki düzene göre çıkar; Efe'nin bunu teyit etmesi istenir (pano mesajında soru).

**Göğüs ekranı pin istemez:** Nextion 25.10.2026'da tasarımdan çıktı; yerine 11,6" HDMI + USB dokunmatik, Pi'den sürülür (EL:26;
`planlama/maliyet.json:21`; `planlama/yazilim-plani.md:124`). `yazilim-plani.md:34`'teki "Nextion … UART2 (GPIO17/16)" eski atıftır;
UART1 / UART2 bu tabloda kullanılmaz (Y1).

## 3. Kod ↔ eski plan ↔ yeni tablo

| GPIO | Kod (`main` PH) | Eski plan (EL, "taslak") | Efe'nin önerisi (P8 #20) | **Yeni** |
|---|---|---|---|---|
| 36 | – | akü | akü | akü |
| 39 / 34 / 35 | – | sonar sağ / orta / sol echo | aynı | aynı |
| 32 / 33 | sağ RPWM / LPWM | sol / sağ BTS IS | aynı | sol / sağ BTS IS (+ bölücü, D7) |
| 25 / 26 | sol RPWM / LPWM | sol RPWM / LPWM | aynı | sol IN1 / IN2 (= RPWM / LPWM; §6.1) |
| 27 / 14 | sol EN / – | sağ RPWM / LPWM | aynı | sağ IN1 / IN2 |
| 13 | sağ EN | dört EN | aynı | dört EN |
| **4** | – | sağ enkoder A | sağ enkoder A | **K1** |
| **19** | sol enkoder B | sol enkoder B | sol enkoder B | **K2** |
| **16** | sağ enkoder A | boş | K1 | **sağ enkoder A** |
| **17** | sağ enkoder B | boş | K2 | **sol enkoder B** |
| 18 | sol enkoder A | sol enkoder A | aynı | sol enkoder A |
| 15 | – | sağ enkoder B | aynı | sağ enkoder B |
| 12 | – | K1 | boş | boş |
| 2 | durum LED'i | K2 (+ LED) | yalnız LED | yalnız LED |
| 23 / 5 | – | PC817 #1 / #2 | aynı | aynı |
| 21 / 22 | I2C | I2C | I2C | I2C |
| 1 / 3 | UART0 | UART0 | UART0 | UART0 |

Efe'nin önerisinden fark: **dört iş yer değiştirdi** (K1 16 → 4, K2 17 → 19, sağ enkoder A 4 → 16, sol enkoder B 19 → 17). Gerisi önerinin aynısı.

### 3.1 Efe'nin önerisinden neden saptık

Sürüm 1 Efe'nin önerisini (K1 = 16, K2 = 17) aynen almıştı. Bağımsız kontrol iki durdurucu bulgu verdi; ikisini kaynağından doğruladım:

- **17 Arduino 2.0.17'nin `Serial2` TX varsayılanıdır** (AR `HardwareSerial.h:175-177`; RX2 = 16, `:167-169`). UART TX boşta HIGH'tır.
  `Serial2.begin()` çağıran her program (seri ekran, GPS örnekleri, projenin kendi eski planı `yazilim-plani.md:34`) K2'yi sürekli
  çektirir: mantar serbestken bara 5,6 Ω ön şarj direncinden sürekli beslenir (EL E9 hata hesabı 32–38 W).
- **Projenin derleme ortamı 16 / 17'yi her açılışta, `setup()`'tan önce sürer** (AR `sdkconfig:683-684, 730-731`, `esp32-hal-misc.c:246`,
  `esp32-hal-psram.c:57-76`; IDF44 `spiram_psram.c:761, 779-780, 860-863, 914, 944-953`): PSRAM yoklaması 16'yı SPI CS'si (boşta HIGH)
  yapar, 17'ye SPI saati verir; sonrasında pinler LOW sürülü kalabilir (doğrulanmadı). Bu, firmware'in ilk satırından önce olur; firmware
  bunu önleyemez, multimetre de göremez. Darbenin röleyi çektirip çektirmediği ölçülmedi; çektirmese de röleyi böyle bir pine koymak
  gereksiz bir risk.

**Neden 4 ve 19 (kontrolün önerisi; aynı ölçütle sınandı):** dışarıdaki 25 GPIO'nun hepsi dolu (12 hariç), yani röleye yer ancak bir girişle
takasla açılır. Ölçüt: reset boyunca LOW, strapping değil, açılış kodu ya da varsayılan çevre birimi sürmüyor (iki çekirdek kuşağında).

| Aday | Reset → sonrası | Strapping | Açılışta / varsayılan sürücü | Sonuç |
|---|---|---|---|---|
| **4** | wpd → wpd | hayır | 2.0.17: yok. 3.x: `Serial2` RX (sürmez; 3.0.7 pull-up açar → 4,7 kΩ ile gate ≤ 0,49 V, D1). Dokunmatik T0 yalnız `touchRead` ile; SDIO DATA1 yalnız indirme kipinde, belgesi yok → T2 | **K1** (kalan adayların en iyisi) |
| **19** | yüzer → yüzer | hayır | iki kuşakta yok (VSPI MISO: kütüphane giriş yapar; U0CTS yalnız akış denetimi açılırsa) | **K2** |
| 16 / 17 | yüzer | hayır | **PSRAM yoklaması; 2.0.17'de Serial2** | röleye olmaz → enkoder |
| 18 / 23 | yüzer | hayır | VSPI SCK / MOSI (`SPI.begin()` sürer) | olmaz |
| 21 / 22 | yüzer | hayır | I2C | olmaz |
| 5 / 15 / 14 | wpu | 5, 15 evet | açılışta zayıf HIGH; 5 VSPI SS | olmaz |
| 12 | wpd | **evet** (MTDI) | HSPI MISO (giriş) | boş kalır: gate hattını HIGH'a çeken bir arıza hem kartı açılmaz yapar hem K1'i çektirir |
| 2 | wpd | **evet** | LED, "blink" programları | olmaz (eski K2 sorunu) |
| 25 / 26 / 27 | oe=0 ie=0 | hayır | 2.0.17: yok. **3.x: TX2 = 25, TX1 = 27 sürer** | olmaz (3.x'te `Serial1` / `Serial2` açan program röleyi çektirir) |

En az iş oynatan güvenli çözüm budur: iki röle iki yeni pin ister, boş güvenli pin yok, o yüzden en az iki giriş taşınır (dört iş). 12'yi
kullanan üç işlik seçenek (K1 → 12) rölenin strapping pinine dönmesi demek; reddedildi. Sol enkoderi 18 / 19'dan bölmek (18 + 17) gerekli:
19 K2'ye gidince sol B'ye kalan tek yer 17.

**Bugünkü `main` firmware'i yeni kablaja yanlışlıkla yüklenirse:** kod 16, 17, 18, 19'u `INPUT_PULLUP` yapar (MC `motorlar.cpp:205-208`), 4'e
dokunmaz; 13 ve 27'yi HIGH yapar (`:216-217`; 27 artık sağ IN1), 32 / 33'ü (artık IS uçları) PWM çıkışı sürer (`:105-113, 140-146`).
- **K1 yolu:** 4'te dahili pull-down + 4,7 kΩ → gate 0 V; K1 çekmez.
- **K2 yolu:** 19'un dahili pull-up'ı 4,7 kΩ gate direnciyle bölücü kurar: 3,3 × 4,7 / 49,7 ≈ **0,31 V** (tipik 45 kΩ), ~75 µA çekme gücüyle
  ≈ 0,35 V, varsayımsal en kötü (30 kΩ, 3,6 V) ≈ 0,49 V (hesap; DS en az değer vermiyor). D9'daki MOSFET'in en düşük eşiği 0,65 V
  (AO3400A, MOS): K2 iletmez. K2 bir an iletseydi bara 5,6 Ω ön şarj direncinden beslenir, 13 ve 27 HIGH olduğu için sağ motorlar bu direnç
  üstünden ileri sürülebilir ve direnç aşırı yüklenirdi (EL E9).
- **IS uçları:** 32 / 33'ün PWM sürüşü D7 bölücüsünün 6,8 kΩ'u üstünden IS ucuna gider, ≤ 0,5 mA (hesap); zararsız.
- **Sonuç: bu kablaja yalnız bu tabloya göre yazılmış firmware yüklenir (Y1).** Yukarıdaki paylar şans, kural değil.

### 3.2 Efe'nin iki uyarısı

- **GPIO15 (sağ enkoder B):** katılıyorum. 15'in açılış değeri yalnız UART0'ın ROM açılış yazısını (LOW = susar, DS Tablo 3-4) ve SDIO slave
  zamanlamasını (Tablo 3-5) seçer. Enkoder açılışta 15'i LOW tutarsa yalnız açılış yazısı gelmez; Pi tarafı bunu beklememeli (Y10).
- **GPIO5 (PC817 #2):** uyarı gereğinden sıkı. GPIO5'in açılış değeri **yalnız SDIO slave zamanlamasını** seçer (DS §3.4 Tablo 3-5);
  projede SDIO slave yok, yani LOW okunması açılışı bozmaz. Normal devrede zaten HIGH olur: reset anında K1 bırakır (4 wpd, gate pull-down),
  bara enerjisiz, PC817 #2 LED'i söner, çıkış transistörü kapalı, pin pull-up ile HIGH. Sıcak resette bara kondansatörleri birkaç ms dolu
  kalıp pini LOW tutabilir; bunun da tek sonucu SDIO zamanlaması. PC817 modülünün 3,3 V tarafı montajda ölçülecek (EL E2, T5).

### 3.3 Yedek tablo

Gerek kalmadı: PSRAM'li modülde röleler etkilenmez (§1). Böyle bir kart gelirse değiştirilir (T1); iki enkoder kanalı olmadan robot
çalışmaz ama güvenlik sorunu yoktur.

## 4. Açılış ve reset anında çıkışlar: ne olur, neden zararsız

Reset sırasında bütün pinlerin çıkışı kapalıdır (DS Tablo 6-1 not 9). Reset sonrasında 25, 26, 27, 19 yüzer; 13 ve 4 wpd; 14 wpu (DS A.4).
`setup()`'tan önce Arduino 2.0.17 çekirdeği yalnız **16 / 17**'yi (PSRAM yoklaması; artık enkoder girişleri) ve UART0'ı (1 / 3) sürer (AR, IDF44).

| Pin | Reset / açılış anında | Bağlı donanım o an | Sonuç |
|---|---|---|---|
| 4 (K1) | wpd, hiçbir kod sürmez | gate 4,7 kΩ ile GND'de | K1 bırakık; bara enerjisiz |
| 19 (K2) | yüzer, hiçbir kod sürmez | gate 4,7 kΩ ile GND'de | K2 bırakık |
| 13 (EN) | reset sırasında yüzer, sonra wpd | 10 kΩ ile GND'de | BTS çıkışları kapalı |
| 25 / 26 / 27 | yüzer | BTS IN | EN LOW olduğu için anlamsız |
| 14 | wpu (zayıf HIGH) | BTS IN2 (sağ) | EN LOW olduğu için anlamsız |
| 16 / 17 | PSRAM yoklaması: 16 CS, 17 saat; sonra LOW sürülü kalabilir (doğrulanmadı) | enkoder çıkışı, 1 kΩ seri | çekişme akımı ≤ 3,3 mA (D6); enkoder sayımı açılışta başlamadığı için etkisiz |
| 2 | wpd | LED | LED söner ya da sönük kalır |

**Motor kilidi tek pinde:** her BTS7960B kartında motor yalnız bir yarım köprü HIGH, öbürü LOW sürülürken döner; bunun için INH ve IN
birlikte gerekir (BTS §4.4.5). 13 her dört EN ucuna bağlı ve 10 kΩ ile LOW. Satıcının adları ters çıksa bile (§6.1) 13 LOW iken motor en
kötü ihtimalle frenlenir, sürülmez. Bu yüzden 13'ün pull-down'ı ve "13 dört EN ucuna" kablajı motor güvenliğinin donanım şartıdır (T3).

**Röle kilidi:** K1 ve K2'nin bobini mantar NC'den sonra (EL E3, E9); mantar basılıyken firmware ne yaparsa yapsın röle çekmez. Mantar
serbestken röleyi yalnız 4 / 19'un firmware tarafından HIGH sürülmesi çektirir; reset, çökme, watchdog, firmware yükleme ve USB sökme
anlarında ikisinin de çıkışı kapanır, gate pull-down'ı LOW tutar: iki röle bırakır, bara kesilir, **kollar düşer** (EL E3, bilinen ve kabul
edilmiş davranış). İndirme kipinde (BOOT basılı reset) 4'ün durumu belgede yok: T2 ölçer.

## 5. Firmware'in uyması gereken şartlar

- **Y1. Yeni kablaja yalnız bu tabloya göre yazılmış firmware yüklenir.** `main` `2be1c63` firmware'i ve hazır deneme yazılımları bu kablaja
  yüklenmez (§3.1). **UART1 / UART2'yi açan hiçbir kod hiçbir çekirdek sürümünde varsayılan pinlerle çalışmaz:** `Serial1`, `Serial2`, aynı
  varsayılanları alan `HardwareSerial(1)` / `HardwareSerial(2)` nesneleri (RX ve TX verilmezse varsayılan kullanılır) ve bunları içeriden
  açan kütüphaneler (seri ekran, GPS örnekleri). Varsayılanlar: 2.0.17 RX1 / TX1 = 9 / 10 (flaş), RX2 / TX2 = 16 / 17; 3.x RX1 / TX1 = 26 / 27,
  RX2 / TX2 = 4 / 25 (AR, AR3). 3.x'te robot devredeyken (EN HIGH) varsayılan `Serial1` / `Serial2` açılırsa 27 / 25 HIGH olur ve o motor tam
  yol ileri döner; **bunu yalnız Y1 ve Y13 önler, donanım önlemez.** UART1 / UART2 gerekirse pinler açıkça verilir ve bu tabloda yeri
  olmayan pin kullanılmaz (bugün boş pin yalnız 12, strapping: D4). 4, 19, 13, 25, 26, 27, 14 çekirdeğin GPIO ve LEDC çağrıları
  (`pinMode`, `digitalWrite`, `ledcSetup` / `ledcAttachPin`, 3.x'te `ledcAttach`) dışında hiçbir kütüphaneye pin olarak verilmez.
- **Y2. `setup()`'ın ilk satırları, her şeyden (seri port, Wi-Fi, I2C) önce:** 4, 19, 13 LOW çıkış yapılır. Arduino-ESP32 2.0.17'de
  `digitalWrite(p, LOW); pinMode(p, OUTPUT);` sırası çalışır. 3.x'te yapılandırılmamış pine `digitalWrite` reddedilir; orada
  `pinMode(p, OUTPUT); digitalWrite(p, LOW);` art arda ya da ESP-IDF'in `gpio_set_level(p, 0)` çağrısı `gpio_set_direction`'dan önce
  kullanılır. (Çıkış kaydı resetten sonra 0 olduğu için iki sürümde de pin LOW başlar.) Ardından 25, 26, 27, 14 PWM'e (LEDC) **görev oranı 0**
  ile bağlanır. Bu sırada 13 LOW kalır. Bu sıra açılış öncesini korumaz; onu donanım (gate / EN pull-down'ları) ve pin seçimi korur.
- **Y3. Girişler:** 23 ve 5 `INPUT_PULLUP` (dış pull-up varsa da açık kalabilir). 18, 17, 16, 15 enkoder girişleri (bugünkü kod `INPUT_PULLUP`;
  enkoder çıkış türü kablajda teyit, T7). 34, 35, 39, 36, 32, 33 için pull komutu verilmez (34–39'da yok; IDF, DS Tablo 6-1 not 2).
- **Y4. Devreye alma (`arm`, EL E3 + E9 dizisi):** ön koşullar: 23 LOW (mantar serbest), PCA9685 çıkışları servoların son bilinen konumunda,
  13 = 0 ve dört PWM = 0, açık komut. Sonra: **19 = 1** (K2) → 300 ms → **5 LOW** olmalı (bara var), değilse 19 = 0 ve hata → **4 = 1** (K1)
  → 100 ms → **19 = 0** → 5 LOW teyidi. 19 hiçbir koşulda 1 s'den uzun 1 kalmaz (ayrı zamanlayıcıyla zorlanır; hata durumunda 5,6 Ω
  dirençte 32–38 W, EL E9).
- **Y5. Bırakma (`birak`, mantar, hata):** 23 HIGH görülünce ya da `birak` gelince aynı döngüde 13 = 0, PWM'ler 0, 4 = 0, 19 = 0; kilit
  (yeniden devreye alma yalnız Y4 ile). 4 = 1 iken 5 HIGH'a dönerse (bara gitti) aynı işlem ve hata.
- **Y6. Motor:** 13 yalnız 4 = 1 ve 5 LOW iken 1 yapılır. Yön değişiminde önce karşı PWM 0, sonra yeni PWM (bugünkü `motorlar.cpp` kuralı).
  Bekçi (500 ms) motor PWM'lerini 0 yapar; K1'i bırakma süresi ayrı karar (pano #7 madde 2'deki öneri).
- **Y7. Akım ölçümü ve durma algılama (karar 14.11, orkestratör):** **tekerlek durma / sıkışma algılaması enkoderle yapılır** (PWM > 0 iken
  belirli süre enkoder sayımı yok → dönüşü kes; süre ve PWM eşiği ölçümden sonra yazılır, pin gerekmez). **IS yalnız arıza (aşırı akım /
  kısa devre) bayrağı ve kaba akım göstergesidir.** 32 / 33 ADC1 (Wi-Fi açıkken de çalışır; ADC2 çalışmaz, IDF), zayıflatma **0 dB**
  (ölçülebilir aralık 100–950 mV, ADC). D7 bölücüsüyle ölçek ≈ 24 mV / A (kart IS direnci birleşik 500 Ω, kILIS 8500 nominal; hesap). Her
  BTS kartı **iki motor** sürer (EL:495), IS kartın toplamını ölçer: **kart başına ≈ 4,1 A altı belgelenen aralığın dışında.** Tek teker
  durunca (≈ 2,8 + 0,12 A ≈ 2,9 A) ≈ 71 mV, normal sürüşte (2 × 0,45 A) ≈ 22 mV: okunmaz; iki teker birden durunca (≈ 5,6 A) ≈ 136 mV.
  `elektrik.md:203`'teki "motor başına > 2,0 A'de kes" kuralı IS ile yapılamaz, enkodere taşındı. Hata akımında pin ≥ 1,4 V: 0 dB'de doyar,
  bu "IS arıza" bayrağıdır. Eşikler T6 ölçümünden sonra yazılır (EL E0 uyarısı).
- **Y8. Enkoderler PCNT ile sayılır**, GPIO kenar kesmesiyle değil: ER [GPIO-3.14] aynı gruptaki (GPIO0–31) kenar kesmesi başka kesmelerle
  birlikte güvenilir değil. 23 ve 5 yoklamayla (polling) ya da seviye kesmesiyle okunur.
- **Y9. Sonar echo 39:** ER [GPIO-3.11] ADC açılırken GPIO36 ve 39 girişi ~80 ns LOW'a çekilir. Echo ölçümü bu darbeyi elemeli (RMT alıcı
  süzgeci ya da echo penceresi sırasında ADC okumamak). 34 ve 35 etkilenmez.
- **Y10. UART0** yalnız Pi ile JSON; ROM açılış yazısı gelmeyebilir (15 LOW) ya da gelebilir: Pi tarafı açılış satırlarını yok sayar.
- **Y11. SPI ve HSPI kullanılmaz:** varsayılan `SPI.begin()` 18'i (sol enkoder A) ve 23'ü (PC817 #1 girişi) çıkış yapar (AR `esp32-hal-spi.c:194, 270`).
  GPIO2 yalnız durum LED'i; GPIO12 hiç ayarlanmaz (varsayılan giriş + wpd kalır).
- **Y12. JTAG:** 12–15 JTAG pinleridir (IDF); bu tabloda 13, 14, 15 kullanıldığı için JTAG ile hata ayıklama yapılamaz.
- **Y13. Çekirdek sürümü sabittir:** bugün `platform = espressif32@6.9.0` (Arduino-ESP32 2.0.17; `kod/esp32/platformio.ini:8`). Sürüm aralıklı
  yazılmaz; 3.x'e (ya da başka bir platform sürümüne) geçiş bu rapor gözden geçirilmeden yapılmaz (en az: UART / SPI varsayılanları, açılış
  işleri, PSRAM yoklaması, `digitalWrite` sırası).

## 6. Donanım şartları

| # | Şart | Pin | Değer | Neden |
|---|---|---|---|---|
| D1 | Gate pull-down + seri direnç (EL E3 / E9; **14.11 sürüm 3: 10 kΩ → 4,7 kΩ**) | 4, 19 | **4,7 kΩ gate → GND**, 220 Ω seri. Direnç setinde var (MJ:115, satıcı sayfası 4,7 kΩ × 10) | Aşağıdaki hesap |
| D2 | EN pull-down (değişmedi, EL pin planı) | 13 | 10 kΩ → GND, dört EN ucuna ortak | Reset sırasında 13 yüzer; motor kilidi (§4) |
| D3 | PC817 çıkışlarında pull-up yalnız 3V3'e | 23, 5 | dahili 45 kΩ; önerilen dış 10 kΩ → 3V3 | Pin ≤ 3,6 V (DS Tablo 5-3: VIH en çok VDD + 0,3 V). Modülün çıkış besleme ucu 5 V'a bağlanmaz |
| D4 | Hiçbir şey bağlanmaz | 12, 2 | – | Strapping (DS Tablo 3-1, 3-3, §3.2) |
| D5 | Sonar bölücüleri (değişmedi, EL E2) | 39, 34, 35 | 4,7 kΩ seri, 10 kΩ toprağa | 5 V echo → 3,40 V |
| D6 | **Enkoder hattına seri direnç** | 16, 17 | **1 kΩ**, ESP32 pinine yakın; enkoder 3V3'ten beslenir | Açılışta PSRAM yoklaması ve yanlış programda `Serial2` (2.0.17) bu pinleri sürer. İtme-çekme çıkışlı enkoderde iki çıkış çekişir; açık kollektörde transistör LOW çekerken pin HIGH sürer. İkisinde de akım 3,3 V / 1 kΩ ≤ 3,3 mA'ye iner (hesap). Açık kollektörde pull-up pin tarafında (dahili 45 kΩ): LOW seviyesi ≈ 3,3 × 1 / 46 ≈ 0,07 V (hesap). 1 kΩ, PCNT hızında kenarı geciktirmez |
| D7 | **BTS IS bölücüsü** (her durumda; diyotsuz) | 32, 33 | IS1 + IS2 ucu → **R1** → pin; pin → **R2** → GND. Kart IS direnci birleşik 500 Ω için **R1 = 6,8 kΩ, R2 = 5,1 kΩ** (setten). Kartta IS direnci yoksa arayüz kartına IS → GND 470 Ω eklenir, aynı R1 / R2 | Aşağıdaki hesap |
| D8 | BTS7960B kartlarının VCC'si 5 V (satıcı sayfası "VCC: +5 VDC") | – | – | 3,3 V lojiği kabul ettiği teyit edilecek (T4) |
| D9 | **Röle sürücü MOSFET'i gerçek mantık seviyeli** (14.11 sürüm 3) | 4, 19 | VGS(th) **en çok ≈ 2 V**, RDS(on) **2,5 V ya da daha düşük gate geriliminde tanımlı**, VDS ≥ 30 V, VGS ±8 V ya da üstü, ID ≥ 1 A. Öneri: **AO3400A** (birinci), IRLML6344 (ikinci; aşağıdaki not); SOT-23, pertinakta SOT-23 → DIP adaptörüyle | Aşağıdaki hesap. Listedeki VBsemi IRLZ44NPBF-VB'nin (MJ:106) veri sayfası bulunamadı, eşiği belgesiz: **değiştirilecek parça**. Orijinal IRLZ44N de şartı karşılamaz (RDS(on) yalnız ≥ 4 V gate'te tanımlı, MOS). Delikli yol istenirse BJT (BC337 + 1 kΩ, EL E3'teki eski seçenek): 220 Ω / 4,7 kΩ ağı ona göre yeniden hesaplanır, doğrulanmadı |

**D1 hesabı (4,7 kΩ; DS Tablo 5-3, Ek A not 8):**
- Pin HIGH sürerken gate = VOH × 4,7 / 4,92: tipik VOH 3,3 V → **3,15 V**; en kötü VOH 2,64 V (DS) → **2,52 V**. Pin akımı 0,54–0,67 mA
  (10 kΩ ile 0,26–0,32 mA); gate dolarken tepe 3,3 / 220 = 15 mA, kısa süreli (DS'teki ~40 mA kaynak akımının altında).
- Boşta, dahili pull-up açıksa (3.x `Serial2` RX'i 4'te, eski firmware'in `INPUT_PULLUP`'ı 19'da, indirme kipinde olası SDIO pull-up'ı 4'te):
  tipik 45 kΩ → 3,3 × 4,7 / 49,7 = **0,31 V**; ~75 µA akım modeliyle **0,35 V**. DS en az pull-up direnci vermiyor; varsayımsal en kötü
  (30 kΩ ve VDD 3,6 V) → **0,49 V**. Üçü de T2 ölçütü 0,5 V'un altında; en kötü varsayımda pay ince (10 mV), tipik değerlerde 0,15–0,19 V.
  10 kΩ ile aynı durumlar 0,60 / 0,75 / 0,90 V'tu (0,5 V ölçütünü bozuyordu).
- Kaçak: IIH / IIL ≤ 50 nA (DS) ve MOSFET gate kaçağı ≤ 100 nA (MOS) → 4,7 kΩ'ta ≤ 0,7 mV.

**D9 hesabı (bobin akımı EL E3 / MJ:107: K1 ~0,15 A, ölçülecek; K2 JQC-3FF ~0,03 A):**
- En yüksek bara 14,6 V'ta K1 bobini ≈ 0,15 × 14,6 / 12,8 ≈ **0,17 A** (hesap, bobin direnci sabit varsayımı).
- Açık hâl: en kötü gate 2,52 V (D1). AO3400A'da eşiğin en yükseği 1,45 V → **≥ 1,07 V** üstünde; RDS(on) < 48 mΩ (2,5 V'ta tanımlı) →
  VDS ≈ 0,17 × 0,048 ≈ 8 mV, kayıp ≈ 1,4 mW. Bobin neredeyse tam bara gerilimini görür. IRLML6344: eşik en çok 1,1 V → ≥ 1,42 V pay, RDS(on) ≤ 37 mΩ.
- Kapalı hâl: boştaki en kötü gate 0,49 V (D1). AO3400A eşiğinin en düşüğü 0,65 V (250 µA'de tanımlı) → 0,16 V pay; IRLML6344'ün en düşüğü
  0,5 V (10 µA'de) → pay yok denecek kadar az. Bu yüzden **AO3400A birinci seçim**; IRLML6344 yalnız T2'de boştaki gate'in tipik
  (≤ 0,35 V) çıktığı görülürse.
- VDS: bobin ters diyotla (1N4007) kenetli, en çok ≈ 14,6 + 1 ≈ 15,6 V < 30 V.
- Satıcı: AO3400A Türkiye'de bir distribütörün (Özdisan) listesinde var, arama anında stok 0 görünüyordu; satıcı, fiyat ve stok **doğrulanmadı**
  (kayda girecek). `maliyet.json`'a dokunulmadı.

**D7 hesabı (BTS; IIS(lim) en çok 7 mA kanal başına, ikinci elden; IS1 + IS2 birlikte 14 mA; kILIS 8500 nominal):**
- Kart IS direnci **R** ise (IS1 ve IS2'nin her birinde; birleşik Rb = R / 2; kartta yoksa Rb = eklenen direnç), yük Rload = Rb ∥ (R1 + R2),
  bölme k = R2 / (R1 + R2). Pin gerilimi **V = I × Rload × k**. Şart: 14 mA'de V ≤ 3,2 V → **k ≤ 3,2 / (0,014 × Rload)**.
- R = 1 kΩ (Rb = 500 Ω, yaygın kart değeri, ölçülmedi) ve R1 = 6,8 kΩ, R2 = 5,1 kΩ: Rload = 479,8 Ω, k = 0,429 → hata 14 mA'de **2,88 V**,
  7 mA'de 1,44 V. Rb %10 büyük çıksa 14 mA'de ≈ 3,15 V. Kartta IS direnci yoksa 470 Ω eklenince 14 mA'de 2,71 V.
  Rb = 1 kΩ çıkarsa R2 = 2,2 kΩ (R1 6,8 kΩ): 14 mA'de 3,08 V.
- **Ölçek ve sınır (fizik, direnç seçimiyle değişmez):** normal sense akımı IL / 8500, hata akımı 14 mA; doğrusal bölücüde ikisinin oranı
  sabittir. 3,2 V'luk hata sınırı normal ölçeği ≈ 3,2 / (0,014 × 8500) ≈ **27 mV / A** ile sınırlar (seçilen dirençlerle 24,2 mV / A).
  Kart başına (iki motor) ≈ **4,1 A** altı ADC1 0 dB aralığının (100–950 mV, ADC) altında; tek teker durması (≈ 2,9 A) ≈ 71 mV okunmaz.
  Tek kanal hatası (7 mA) varsayılsaydı ölçek iki katına çıkardı, ama iki IS aynı pinde olduğu için 14 mA'i dışarıda bırakamadım.
- **Diyotlu çözümle karşılaştırma** (sürüm 2: 1 kΩ seri + 3V3'e 1N5819, Rb = 500 Ω): normal 2,8 A ≈ 165 mV (okunabilir); ama 14 mA hatada
  IS düğümü ≈ 5,9 V, diyot akımı ≈ 2,3 mA, pin ≈ 3,3 + VF ≈ **3,6 V = DS Tablo 5-3 VIH en çok (VDD + 0,3 V)**; 1N5819'un ters kaçağı (sıcakta onlarca
  µA) Rb üstünde 10–50 mV kayma yapar (ikinci kontrol B5); 3V3 hattına akım basar. **Seçilen: diyotsuz bölücü.** Pin her durumda sınırın
  altında, kaçak yok, davranış direnç değerleriyle belirli. Bedeli: kart başına 4 A altı akım ölçümü belgelenen ADC aralığının dışında.
  Durma algılama bu yüzden enkoderle yapılır (Y7, karar 14.11).
- 1N5819 + 2 notu kaldırıldı.

### 6.1 BTS7960B kartının pin adları

Alınacak kartın (Robotistan, MJ "Motor sürücü") satıcı sayfası (14.11 okundu): **VCC +5 VDC, GND, IS1 / IS2 "akım test pinleri",
EN1 / EN2 "PWM girişleri", IN1 / IN2 "motor yön kontrol pinleri"**, B+ / B−, M+ / M−; lojik seviye ve tampon yazmıyor. EL ve PH'deki adlar
IBT-2 düzeninindir (RPWM / LPWM / R_EN / L_EN / R_IS / L_IS).

Bu tablo **EN1 / EN2 = BTS7960 INH (etkinleştirme), IN1 / IN2 = BTS7960 IN (PWM)** varsayar: PWM IN'e, EN ortak 13'e (IBT-2 düzeni,
EL'in planı). Satıcının "EN = PWM, IN = yön" tarifi başka bir sürme biçimidir; bu tabloda kullanılmaz. Kart gelince EN1 / EN2'nin kart
üstünde hangi BTS7960 bacağına gittiği multimetreyle bakılır (T4). **Kartın EN1 / EN2 dediği uç INH'ye gitmiyorsa:** 13 kartın IN1 / IN2
dediği uçlara, 25 / 26 / 27 / 14 kartın EN1 / EN2 dediği uçlara bağlanır. Pin numaraları değişmez.

## 7. Kablajda teyit edilecek

Kararı bunlara bağlamadım; her biri montajda ölçülür, sonuç günlüğe yazılır.

| # | Ne | Nasıl | Geçme ölçütü | Kalmazsa |
|---|---|---|---|---|
| T1 | Modül, çip ve kart (işlev şartı) | Kablajdan önce yalnız USB ile: `esptool.py chip_id` (ve `flash_id`) çıktısındaki çip adı, paket, revizyon ve özellikler; modül kapağı yazısı, modül boyu (WROOM 18,0 × 25,5, WROVER 18,0 × 31,4 mm); serigrafi | Çip D0WDQ6 / D0WD(-V3), "Embedded PSRAM" ya da D0WDR2 yok; modül WROVER değil; revizyon v0.0 değil (ER [RES-3.4]); 25 GPIO dışarıda; LED GPIO2'de | Kart PSRAM'siz bir kartla değiştirilir (§1). Röle tarafı etkilenmez |
| T2 | Röle gate'leri hiçbir anda HIGH değil; röle 3,3 V gate ile kesin çekiyor ve kesin bırakıyor | **0,5 V ölçütü osiloskopla ölçülür** (mantık analizörü yalnız tam HIGH'ı görür, bu ölçüt için araç değildir). ESP32 + arayüz kartı bağlı. Kanallar: 4, 19, 13 (ve bilgi için 16, 17). EN'in yükselen kenarında tek tetik, ≥ 2 s pencere, ≤ 1 µs çözünürlük. (a)–(e) **F5 takılı değilken**: (a) gerçek firmware ile normal açılış; (b) USB tak / sök, Pi portu açılırken; (c) **indirme kipi**: BOOT basılıyken EN, ardından `esptool` ile yükleme; (d) yükleme bitip yeniden açılış; (e) firmware boşta. (f)–(g) **F5 takılı, bara yüksüz (BTS ve XL girişleri ayrık), akım sınırlı kaynak**: (f) `arm` ve `birak`; (g) bara 11 V ve 14,6 V'ta 20'şer kez çek / bırak: gate, MOSFET drain ve kontak (bara) gerilimi. **Osiloskop yoksa yedek yol:** (1) (a)–(e)'nin her birinde multimetreyle kararlı gate gerilimi; (2) F5 takılı, bara yüksüz kurulumda (a)–(e) boyunca röle kontağının çıkışı (bara ya da PC817 #2 çıkışı) mantık analizörüyle ya da ikinci bir mikrodenetleyicinin kesme girişiyle izlenir. Bu yol 0,5 V ölçütünden zayıftır, rölenin çekmesini doğrudan sınar | (a)–(e)'de 4 ve 19 hiçbir anda > 0,5 V değil (yedek yolda: kararlı gate < 0,5 V ve kontak çıkışında hiç geçiş yok); (f)'de `arm` Y4'teki sıra ve sürelerle, `birak`'ta ikisi aynı döngüde LOW; (g)'de her çekişte drain < 0,1 V ve kontak kapanıyor, her bırakışta drain bara gerilimine çıkıyor ve kontak açılıyor (40 / 40) | Gate devresi / MOSFET (D9) yeniden incelenir; F5 normal kullanımda takılmaz |
| T3 | EN kilidi ve 14'ün açılışı | BTS kartları bağlı, ESP32 resette: 13 → GND gerilimi; dört EN ucuna süreklilik; T2 kurulumunda 14'e de bakılır (topluluk gözlemi "açılışta kısa darbe", kaynaksız) | 13 < 0,3 V; dört uç 13'e bağlı. 14'te darbe olsa da 13 LOW iken zararsız | 13'ü yüksek çeken kart içi direnç aranır |
| T4 | BTS7960B kartı | EN1 / EN2 ve IN1 / IN2'nin hangi BTS7960 bacağına gittiği; 3,3 V PWM ile motorun döndüğü (tezgâh, akım sınırlı kaynak) | EN → INH, IN → IN; 3,3 V PWM'de motor iki yönde döner, IN ucunda HIGH ≥ 2,6 V. Kart girişinin eşiği kart gelince (BTS VIH en çok 2,15 V, kart üstü tampon bilinmiyor) | Adlar terse §6.1. 3,3 V yetmezse seviye çevirici (malzeme eklenir) |
| T5 | PC817 modülünün 3,3 V tarafı (EL E2) | Girişe 12 V ver / kes, 23 ve 5'te ölç | LOW < 0,4 V, HIGH > 2,5 V, hiçbir durumda > 3,6 V | EL E2'deki doğrudan PC817 + 2,2 kΩ yedeği |
| T6 | BTS IS direnci, bölücü ve ölçek | **İlk adım:** kart enerjisizken IS1 → GND ve IS2 → GND direncini ölç (R; IS1 ile IS2 kart üstünde birleşik mi). D7 formülüyle R1 / R2 seçilir ve bölücü takılır. **Akım enjeksiyonu:** motor ve BTS beslemesi bağlı değilken IS düğümüne (kart IS direnci + R1 / R2 takılı) akım sınırlı laboratuvar kaynağından seri dirençle 14 mA verilir, pin gerilimi ölçülür. Akım sınırına motorla çıkılmaz. Sonra motor yalnız durma akımında ölçülür | Hesaplanan 14 mA en kötü durumunda pin ≤ 3,2 V; durma akımında okunan değer kaydedilir (ölçek kalibrasyonu) | D7 **her durumda** takılır; R ölçülmeden IS ucu ESP32'ye bağlanmaz |
| T7 | Enkoder çıkış türü (açık kollektör mü itme-çekme mi) | 3V3 beslemede A / B'yi el ile çevirerek ölç; 16 / 17'de 1 kΩ takılıyken de | Pin tarafında LOW ≤ 0,8 V, HIGH ≥ 2,5 V (DS Tablo 5-3: 0,25 / 0,75 × VDD) | Dış pull-up eklenir |
| T8 | Kart LED'i ve GPIO2 | LED'in GPIO2'de olduğu ve dışarıda başka bağlantı olmadığı | GPIO2 = 1 iken LED yanar, 0 iken söner; 2 numaralı başlık pininden dışarıya bağlantı yok. Sayısal ölçüt kart gelince | Not düşülür |

## 8. Bu kararın dışında kalanlar

- **Pi'den ESP32'yi bilerek resetleme hattı** (pano #7 madde 5'teki öneri: Pi GPIO'su → transistör → ESP32 EN). Bu bir Pi pini ve boyundan
  inen yeni bir tel demek (boyun demeti K14). Pin haritasına girmedi; ayrı karar. O gelene kadar reset yolu CP2102'nin DTR / RTS devresi
  (Pi portu bunları kapalı açar; `main` `kod/robot/seri.py`).
- **PSRAM'i kapalı derleme:** Arduino'nun hazır kütüphanesiyle `CONFIG_SPIRAM` kapatılamaz; gerek kalmadı (16 / 17'de röle yok).
- **Motor durma algılama:** enkoderle (Y7, karar 14.11); IS yalnız arıza bayrağı.
- **Ön enkoderler:** bağlanmadı (pin yok; EL pin planı notu değişmedi).
- **XL4016 NTC (E7 ölçümü):** ADC1 pini kalmadı (EL, değişmedi).

## 9. `kod/ortak/pinler.json` için içerik önerisi

Dosyayı Efe açar; aşağıdaki içerik bu tablonun aynısıdır. `eklem_sinirlari.json` gibi ASCII yazıldı. Alan adları öneridir.

```json
{
  "surum": 3,
  "tarih": "2026-11-14",
  "kaynak": "planlama/adim3/pin-haritasi.md (lale-duzeltme); karar: Ahmet 13.11.2026 yetkilendirmesi",
  "cekirdek": "espressif32@6.9.0 (Arduino-ESP32 2.0.17); 3.x'e gecis raporu gozden gecirmeden yapilmaz",
  "kart": {
    "ad": "ESP32 DevKit 30 pin, CP2102",
    "modul_sarti": "PSRAM'siz modul (WROVER ya da D0WDR2 / ...R2 ise GPIO16/17 enkoder kanallari calismaz; roleler etkilenmez)",
    "flash_gpio_kullanilmaz": [6, 7, 8, 9, 10, 11],
    "kullanilmaz": ["Serial1 / Serial2 varsayilan pinleri (2.0.17: 16/17; 3.x: 26/27, 4/25)", "SPI ve HSPI varsayilan pinleri"]
  },
  "pinler": {
    "AKU_ADC":        {"gpio": 36, "yon": "analog", "adc": "ADC1_CH0", "not": "100k/18k + 100nF"},
    "SONAR_SAG_ECHO": {"gpio": 39, "yon": "giris", "not": "yalniz giris; 4.7k/10k bolucu; errata GPIO-3.11 ~80 ns LOW"},
    "SONAR_ORTA_ECHO":{"gpio": 34, "yon": "giris", "not": "yalniz giris; 4.7k/10k bolucu"},
    "SONAR_SOL_ECHO": {"gpio": 35, "yon": "giris", "not": "yalniz giris; 4.7k/10k bolucu"},
    "SOL_IS":         {"gpio": 32, "yon": "analog", "adc": "ADC1_CH4", "zayiflatma": "0 dB", "uc": "sol BTS IS1+IS2", "donanim": "IS -> 6.8k -> pin, pin -> 5.1k -> GND (kart IS direnci birlesik 500R ise; once olculur)"},
    "SAG_IS":         {"gpio": 33, "yon": "analog", "adc": "ADC1_CH5", "zayiflatma": "0 dB", "uc": "sag BTS IS1+IS2", "donanim": "IS -> 6.8k -> pin, pin -> 5.1k -> GND (kart IS direnci birlesik 500R ise; once olculur)"},
    "SOL_ILERI_PWM":  {"gpio": 25, "yon": "pwm", "uc": "sol BTS IN1 (RPWM)", "not": "3.x: Serial2 TX varsayilani"},
    "SOL_GERI_PWM":   {"gpio": 26, "yon": "pwm", "uc": "sol BTS IN2 (LPWM)", "not": "3.x: Serial1 RX varsayilani"},
    "SAG_ILERI_PWM":  {"gpio": 27, "yon": "pwm", "uc": "sag BTS IN1 (RPWM)", "not": "3.x: Serial1 TX varsayilani"},
    "SAG_GERI_PWM":   {"gpio": 14, "yon": "pwm", "uc": "sag BTS IN2 (LPWM)", "not": "reset sonrasi zayif pull-up"},
    "BTS_EN":         {"gpio": 13, "yon": "cikis", "acilis": 0, "uc": "sol EN1+EN2, sag EN1+EN2", "donanim": "10k -> GND"},
    "ROLE_K1":        {"gpio": 4,  "yon": "cikis", "acilis": 0, "uc": "role MOSFET #1 gate (mantik seviyeli, or. AO3400A)", "donanim": "220R seri, 4.7k gate -> GND", "not": "3.x: Serial2 RX varsayilani"},
    "ROLE_K2_ONSARJ": {"gpio": 19, "yon": "cikis", "acilis": 0, "en_cok_ms": 1000, "uc": "role MOSFET #2 gate (mantik seviyeli, or. AO3400A)", "donanim": "220R seri, 4.7k gate -> GND"},
    "ACIL_STOP_DURUM":{"gpio": 23, "yon": "giris_pullup", "aktif": "HIGH = mantar basili / F5 atti", "uc": "PC817 #1"},
    "BARA_DURUM":     {"gpio": 5,  "yon": "giris_pullup", "aktif": "LOW = bara gerilimli", "uc": "PC817 #2", "not": "strapping, yalniz SDIO zamanlamasi"},
    "I2C_SDA":        {"gpio": 21, "yon": "i2c"},
    "I2C_SCL":        {"gpio": 22, "yon": "i2c"},
    "SOL_ENK_A":      {"gpio": 18, "yon": "giris", "sayac": "PCNT"},
    "SOL_ENK_B":      {"gpio": 17, "yon": "giris", "sayac": "PCNT", "donanim": "1k seri", "not": "acilista PSRAM yoklamasi surer"},
    "SAG_ENK_A":      {"gpio": 16, "yon": "giris", "sayac": "PCNT", "donanim": "1k seri", "not": "acilista PSRAM yoklamasi surer"},
    "SAG_ENK_B":      {"gpio": 15, "yon": "giris", "sayac": "PCNT", "not": "strapping: LOW ise yalniz ROM acilis yazisi susar"},
    "UART0_TX":       {"gpio": 1,  "yon": "uart", "uc": "CP2102 -> Pi"},
    "UART0_RX":       {"gpio": 3,  "yon": "uart", "uc": "CP2102 -> Pi"},
    "DURUM_LED":      {"gpio": 2,  "yon": "cikis", "uc": "kart ustu LED", "not": "strapping; disariya baglanmaz"}
  },
  "bos": {"12": "strapping (MTDI); hicbir seye baglanmaz"},
  "i2c": {"PCA9685": "0x40", "BNO055": "0x28 / 0x29"},
  "pca9685_kanallar": {
    "0": "sag_omuz", "1": "sag_omuz_yan", "2": "sag_dirsek", "3": "sag_bilek", "4": "kafa_pan",
    "5": "sol_omuz", "6": "sol_omuz_yan", "7": "sol_dirsek", "8": "sol_bilek", "9": "kafa_tilt",
    "10": "sonar_sag_trig", "11": "sonar_orta_trig", "12": "sonar_sol_trig",
    "13": "yedek", "14": "yedek", "15": "yedek"
  }
}
```

`pinler.h` ve `elektrik.md` tablosu bu dosyadan üretilince bu rapordaki §2 tablosu tarihçe olur; o güne dek fark çıkarsa bu rapor esastır.

## 10. Kaynak ve tarih

- Sürüm 1, 2 ve 3: 14.11.2026 (Ahmet'in 13.11.2026 gecesi yetkilendirmesiyle); depo dalı `lale-duzeltme`, kod `main` `2be1c63` okundu (değiştirilmedi).
- Bu rapordaki ESP32 olguları yalnız Espressif belgelerinden ve Arduino-ESP32 / ESP-IDF kaynak kodundan; MOSFET değerleri üretici veri
  sayfalarından; satıcı bilgisi satıcı sayfasından (14.11); hesaplar "hesap" diye işaretli.
- İkinci elden: BTS7960 IIS(lim) (Infineon tam veri sayfası açılamadı; en kötü 7 mA alındı).
- Ölçülmeyenler: kartın kendisi (gelmedi), modül türü, PSRAM yoklama darbesinin süresi ve sonrası, indirme kipinde GPIO4, BTS kartının iç
  bağlantısı, IS direnci ve lojik eşiği, PC817 modülünün çıkışı, enkoder çıkış türü, röle bobin akımları, ESP32 dahili pull-up'ının gerçek
  değeri, reset anındaki gerçek pin gerilimleri. Hepsi §7'de.
- Günlük: `planlama/d158/pin-karari-gunluk.md`; bağımsız kontroller: `planlama/d158/pin-karari-kontrol.md`, `pin-karari-kontrol-2.md`.
