# Pin kararı sürüm 3: üçüncü bağımsız kontrol, 14.11.2026

Kontrol edilen: `planlama/adim3/pin-haritasi.md` (sürüm 3), `planlama/adim3/elektrik.md` (çalışma ağacı farkı), `planlama/d158/pin-karari-gunluk.md`
(§7 ve §9 "Düzeltme turu 2"), önceki iki kontrol, depo dışındaki pano #8 taslağı ve gövdesi (sürüm 3). Dal `lale-duzeltme`, HEAD `9145164`;
kod `origin/main` `2be1c63`'ten okundu (dal değiştirilmedi). Başlangıç 14.11 01:13, rapor 01:23 sonrası yazıldı (saat makineden). Hiçbir
dosya düzeltilmedi; commit, `git add`, pano yazımı yok; FreeCAD ve rehber betikleri koşulmadı.

Kaynakları **kendim indirdim** (A adımının ve önceki kontrollerin kopyalarına dayanmadan): Arduino-ESP32 etiket `2.0.17`, `3.0.7`, `3.3.0`
(`cores/esp32/HardwareSerial.h`, `HardwareSerial.cpp`, `esp32-hal-uart.c`, `esp32-hal-misc.c`, `variants/esp32/pins_arduino.h`); ESP-IDF
`v5.1.4` `components/driver/uart/uart.c`; PlatformIO `platform-espressif32` `v6.9.0` `platform.json` ve `boards/esp32dev.json`; Espressif
*ESP32 Series Datasheet* v5.3 (PDF, Espressif sitesinden); Alpha & Omega *AO3400A* (Rev 3.1, Temmuz 2023) ve Infineon *IRLML6344TRPbF*
veri sayfaları (üreticilerden).

## Hüküm: **GEÇER**

Göndermeyi durduran bulgu yok. Düzeltme turu 2'nin dört değişikliği (UART / çekirdek kuralı, 4,7 kΩ gate, MOSFET şartı, diyotsuz IS
bölücüsü) kaynakla ve hesapla tutuyor. Tablo dört yerde aynı. Pin numaralarında iki kontrolün kaçırdığı bir hata bulmadım.

Aşağıdaki bulguların hepsi **kayıtlı açık iş olarak gidebilir**: hiçbiri bir pini, bir direnç değerini ya da Efe'nin yazacağı açılış /
röle / motor kuralını değiştirmiyor. İkisi (Ö1, Ö2) montajda uygulanacak test adımlarının metni; o testler yapılmadan önce düzeltilmeli.
Ö3 Efe'nin akım ölçümüyle yanlış bir şey kurmaması için kayda girmeli. Gönderimden önce üç cümlelik düzeltme mümkünse (C adımında)
Ö1–Ö3'ün birer cümlesi yeter; mümkün değilse proje sahibine açık iş olarak gider.

Brief'teki "güvenliği ilgilendiren her bulgu durdurur" kuralını Ö1 ve Ö2 için ayrıca tarttım; gerekçe her bulgunun altında.

## Bulgular (önem sırasıyla; hepsi "gidebilir")

### Ö1. T2'de "mantık analizörü" 0,5 V ölçütünü ölçemez; osiloskopsuz ekip için yol yazılmamış

- **Ne:** T2 (`pin-haritasi.md:345`) "Osiloskop **ya da** mantık analizörü" diyor, geçme ölçütü "(a)–(e)'de 4 ve 19 hiçbir anda > 0,5 V değil".
  Mantık analizörü yalnız eşik geçişini (tipik 1,2–1,6 V) görür, 0,5 V'u göremez; ölçüt bu araçla sınanamaz. Osiloskobu olmayan bir ekip
  için yedek yol da yazılmamış.
- **Kendi değerlendirmem:** pratikte kaçırılacak tehlike dar. Pini süren bir şey (UART TX, GPIO çıkışı) tam HIGH verir; mantık analizörü
  bunu yakalar. Pull-up kaynaklı durum 4,7 kΩ ile ≤ 0,49 V kalır (D1, hesabı aşağıda doğruladım). Analizörün kaçıracağı ara düzey
  (≈ 0,5–1,4 V) ancak belgelenenden çok güçlü bir iç pull-up (≈ 10 kΩ altı) ile olur. Yine de bu düzeyde AO3400A iletmeye başlayabilir
  (eşik tipik 1,05 V). Ölçüt ile araç bu yüzden uyuşmalı.
- **Önerilen düzeltme (T2 metni):** "0,5 V ölçütü osiloskopla ölçülür. Mantık analizörü yalnız tam HIGH darbesini görür. Osiloskop yoksa:
  (1) her durumda (a)–(e) multimetreyle kararlı gate gerilimi < 0,5 V; (2) F5 takılı, bara yüksüz kurulumda röle kontağının çıkışı
  (bara ya da PC817 #2 çıkışı) mantık analizörüyle ya da ikinci bir mikrodenetleyicinin kesme girişiyle izlenir. Rölenin çekmesi için
  gereken darbe (ms düzeyi) kontakta iz bırakır." İkinci yol 0,5 V ölçütünden zayıftır ama asıl tehlikeyi, yani rölenin çekmesini doğrudan
  sınar. Okulda osiloskop ödünç alınabiliyorsa birinci yol yeter.
- **Sınıf: gidebilir.** Tasarım değişmiyor (pin, direnç, MOSFET). Sorun, montajda yapılacak doğrulamanın araç tarifi. T2 uygulanmadan
  önce düzeltilmeli.

### Ö2. T6'daki "mümkünse akım sınırında" adımı tehlikeli ve gereksiz

- **Ne:** T6 (`pin-haritasi.md:349`): "Sonra motor durma akımında ve mümkünse akım sınırında pin gerilimi". BTS7960'ın akım sınırı onlarca
  amperdir. Oraya varmak için çıkışın neredeyse kısa devre edilmesi gerekir; bu da F1 20 A'yı attırır, 12 AWG hattı ve bara bağlantılarını
  zorlar. Ayrıca 14 mA'lik hata durumunun bölücüde ≤ 3,2 V verdiğini sınamak için akım sınırına çıkmak gerekmez.
- **Önerilen düzeltme:** "akım sınırında" yerine **akım enjeksiyonu** yazılsın: BTS bağlı değilken IS düğümüne (kart IS direnci + R1 / R2
  takılı) akım sınırlı laboratuvar kaynağından seri dirençle 14 mA verilir ve pin gerilimi ölçülür. Ölçüt: ≤ 3,2 V. Motor yalnız durma
  akımında ölçülür.
- **Sınıf: gidebilir.** Kablaj ve firmware değişmiyor, "mümkünse" diye isteğe bağlı yazılmış. T6'dan önce düzeltilmeli.

### Ö3. D7 bölücüsü, `elektrik.md:203`'teki "motor başına > 2,0 A'de dönüşü kes" kuralını işlevsiz bırakıyor; rapordaki 2,8 A örneği motor / kart karışık

- **Ne:**
  - `elektrik.md:203`: "BTS7960 IS çıkışları (GPIO32/33) motor başına > 2,0 A ölçülürse 2 s sonra dönüşü kes". Aynı kural
    `elektrik.md:170`'te ve `planlama/d158/testler/T1-jgb37-durma-torku.md:149`'da anılıyor.
  - D7 ile ölçek 24,2 mV / A (hesabı doğruladım), ADC 0 dB'de belgelenen alt sınır 100 mV, yani **≈ 4,1 A**. Her BTS kartı **iki motor**
    sürüyor (`elektrik.md:495`). "Motor başına 2 A" kart başına 4 A demek: sınırın tam üstünde (≈ 97 mV, belgelenen aralığın altında).
    Tek teker durduğunda (2,8 + 0,12 A ≈ 2,9 A ≈ 71 mV) ve normal sürüşte (2 × 0,45 A ≈ 22 mV) okuma yok. İki teker birden
    durduğunda (5,6 A ≈ 136 mV) okunur. Durma akımı 1,2 A senaryosunda (`elektrik.md:161`) hiçbir durma okunmaz.
  - Rapor (`pin-haritasi.md:262`, `:318`) "2,8 A durma ≈ 68 mV" diyor. 2,8 A tek motorun durma akımı (`elektrik.md:157`); IS ise
    kartın, yani iki motorun toplamını ölçer. Sonuç ("4 A altı okunmaz") doğru, örnek yanıltıcı.
  - Rapor 4 A altını "ayrı karar" diye bırakıyor (`:324`, `:359`), ama yürürlükteki `elektrik.md:203` kuralıyla çeliştiğini söylemiyor.
    Efe 2 A eşiğini IS ile kurmaya kalkabilir.
- **Önerilen düzeltme:** Y7'ye bir cümle: "IS yalnız hata işareti ve iki teker birden durduğunda (kart başına ≳ 4 A) kullanılır.
  `elektrik.md:203`'teki motor başına 2 A kesme IS ile yapılamaz. Durma algılama **enkoderle** yapılır (PWM > 0 iken N ms sayım yok →
  dönüşü kes; pin gerekmez)." Örnek "kart başına (iki motor)" diye düzeltilir. `elektrik.md:203` C adımında bu kurala bağlanır.
- **Sınıf: gidebilir.** Kendiliğinden hareket ya da pin hasarı yolu yok. Kaybedilen şey bir motor koruma işlevi; enkoderle pin
  değişmeden karşılanabiliyor. Kayda girmeli.

### Ö4. Seri hat kuralı (Y1): metin boşlukları, hepsi küçük

Kaynaktan okuduklarım (rapordaki satır atıflarının hepsi tuttu):

- 2.0.17 `HardwareSerial.h:141, 153` RX1 = **9**, TX1 = **10** (flaş pinleri); `:169, 177` RX2 = 16, TX2 = 17.
- 3.0.7 `:152, 170, 192, 200` ve 3.3.0 `:195, 217, 243, 251`: RX1 = 26, TX1 = 27, RX2 = 4, TX2 = 25.
- `HardwareSerial.cpp` (2.0.17 `:299-315`, 3.3.0 `:344-365`): varsayılanlar `_uart_nr`'ye göre ve **yalnız RX ve TX ikisi de verilmezse**
  kullanılıyor. Yani `HardwareSerial ornek(2)` nesnesi de `Serial2` ile aynı varsayılanları alır.

Boşluklar:

- **(a)** Y1 kalın cümlesi yalnız "`Serial1` ve `Serial2`" diyor. Aynı UART'ı açan `HardwareSerial(1)` / `HardwareSerial(2)` nesneleri ve
  kendi içinde `Serial2.begin(baud)` çağıran kütüphaneler (seri ekran, GPS örnekleri) adıyla anılmıyor. Sonraki cümle ("UART1 / UART2
  gerekirse pinler açıkça verilir") pratikte kapsıyor. Öneri: "UART1 / UART2'yi açan her kod (`Serial1`, `Serial2`, `HardwareSerial(n)`,
  bunu içeriden yapan kütüphaneler)".
- **(b)** Y1'in son cümlesi "4, 19, 13, 25, 26, 27, 14 hiçbir kütüphaneye pin olarak verilmez" diyor. 25 / 26 / 27 / 14 LEDC'ye
  (`ledcAttach`) verilmek zorunda. Öneri: "çekirdeğin GPIO / LEDC çağrıları dışında".
- **(c)** 3.x'teki RX pull-up iddiası (`pin-haritasi.md:30`, `:89`, `:85`) **3.0.7 için doğru**: 3.0.7 `esp32-hal-uart.c:200` IDF
  `uart_set_pin`'i çağırıyor, IDF v5.1.4 `uart.c:621-622` RX'e `GPIO_PULLUP_ONLY` veriyor. **3.3.0'da** Arduino kendi
  `_uartInternalSetPin`'ini kullanıyor (`esp32-hal-uart.c:353-418`): RX'e yalnız `gpio_input_enable`, pull-up yok. Rapor güvenli taraftaki
  durumu almış; bilgi notu.
- **(d)** 3.x'te 25 / 27 satırları (`:84`, `:86`) "EN LOW iken zararsız" diyor; doğru. Ama EN HIGH iken (robot devrede) varsayılan pinlerle
  açılan `Serial2` / `Serial1` TX'i sol / sağ IN1'i sürekli HIGH tutar, yani o motoru tam yol ileri sürer. Bu yolu kapatan yalnız Y1 +
  Y13 kuralıdır, donanım değil. Öneri: iki satıra "EN HIGH iken o motor tam yol ileri döner" eklensin ki kuralın ağırlığı görünsün.
- **(e)** Wi-Fi / Bluetooth: pinlere dokunduklarını gösteren bir kaynak bulmadım. Wi-Fi'nin tek etkisi ADC2'nin analog okunamaması; 4
  (ADC2_CH0) burada sayısal çıkış, etkilenmez. Dokunmatik T0 = 4 yalnız `touchRead` ile (`pins_arduino.h`, üç sürümde aynı).
- **Sınıf: gidebilir** (metin; 2.0.17 sabit olduğu sürece hiçbir yol röleye ya da motora varmıyor).

### Ö5. `elektrik.md`'de iki "IRLZ44N" kalıntısı ve düşen BJT seçeneği

- `elektrik.md:306` "arayüz kartı (… IRLZ44N + 1N4007 …)" ve `:339` blok şema "röle K1 bobini ── IRLZ44N ── GND". Günlük §9.2 madde 3
  "şemalarda IRLZ44N → MOSFET" diyor; bu iki yer kalmış. Öneri: "röle MOSFET'i (D9)".
- Fark eski `:268`'deki "Alternatif BC337 + 1 kΩ" seçeneğini sildi. Pin kararı bunu gerektirmiyordu (aşağıda Ö7).
- **Sınıf: gidebilir** (D9 bağlayıcı; parça adı tarihçe kalıntısı).

### Ö6. Pano gövdesi: Efe için iki eksik cümle

- Y1'in ilk ve Efe için en önemli kuralı gövdede yok: "**`main` `2be1c63` firmware'i ve hazır deneme yazılımları bu kablaja yüklenmez;
  `pinler.h` bu tabloya göre yeniden yazılmadan kart kablaja takılmaz.**" Öneri: gövdenin "Firmware için yeni olanlar" paragrafına bir
  cümle.
- Gövdedeki "arm = 19→1, 300 ms, …" dizisinde `19`'un en çok 1 s kalma sınırı ve "5 LOW değilse 19 = 0, hata" dalı yok (raporda Y4'te
  var, gövde rapora gönderiyor). İsteğe bağlı: "19 ≤ 1 s".
- "BTS hata akımı 4–7 mA" (gövde satır 9) tek kanal değeri; hesap iki IS birlikte 14 mA ile yapıldı. Bu bilgi `--kaynak` satırında
  "ikinci elden, doğrulanmadı" diye işaretli; protokol madde 3'e uyuyor.
- Gönderimde `--kaynak` listesine ve günlük §7 K58 metninin kaynak listesine (`pin-karari-gunluk.md:111-112`) bu dosya
  (`pin-karari-kontrol-3.md`) eklenmeli.
- **Sınıf: gidebilir.**

### Ö7. D9 şartının ifadesi ve delikli seçenek (bilgi)

- **Hesaplar doğru.** Kendi indirdiğim veri sayfalarından:
  - **AO3400A:** VDS 30 V, VGS ±12 V, VGS(th) 0,65 / 1,05 / 1,45 V (250 µA), RDS(on) < 48 mΩ (2,5 V, 3 A), IGSS 100 nA.
  - **IRLML6344:** VDS 30 V, VGS ±12 V, VGS(th) 0,5 / 0,8 / 1,1 V (**10 µA**), RDS(on) ≤ 37 mΩ (2,5 V), sürekli ID 4,0 A.
  - **Açık hâlde** en kötü gate 2,52 V'ta K1 bobini ≈ 0,17 A → VDS ≈ 8 mV.
  - **Bobin geri tepmesi:** her bobinde ters paralel 1N4007 var (`elektrik.md:249`, `:443`). VDS ≤ ≈ 15,6 V < 30 V.
- **Şartın ifadesi** (`pin-haritasi.md:288`) yalnız üst eşik koyuyor ("VGS(th) en çok ≈ 2 V"). Kapalı hâl için alt sınır, akım ve VGS
  sınırı yok. Pratikte bu sorun değil: eşik 10–250 µA'de tanımlı, röle çekmek için ≈ 0,1 A gerekiyor. Gate 0,49 V iken en düşük eşikli
  parça bile µA düzeyinde iletir. Bu yüzden IRLML6344'ün "ikinci seçim, pay yok" diye geri plana alınması fazla temkinli ama yanlış değil.
  Öneri (isteğe bağlı): şarta "VGS ±8 V ya da üstü, ID ≥ 1 A" eklensin.
- **Delikli seçenek:** bildiğim yaygın delikli MOSFET'ler (2N7000, BS170: eşik 3 V'a kadar; IRLZ44N, IRLB8721: RDS(on) ≥ 4–4,5 V'ta
  tanımlı) şartı karşılamıyor. Veri sayfasından teyit etmedim. SOT-23 + DIP adaptörü pertinakta makul; elle lehim ve ESD dikkati ister.
  Delikli bir yol isteniyorsa eski tasarımdaki BJT (BC337, baz direnci ≈ 1 kΩ) kullanılabilir. 220 Ω / 4,7 kΩ ağı ona göre yeniden
  hesaplanmalı; bunu bu kontrolde doğrulamadım.

### Ö8. Küçük sayı ve ifade noktaları

- **`pin-haritasi.md:314`:** "Rb %10 büyük çıksa 14 mA'de ≈ 3,17 V". Hesabım: Rload = 550 ∥ 11,9 kΩ = 525,7 Ω → 7,36 V × 0,4286 = **3,15 V**.
  Sonuç değişmez.
- **`pin-haritasi.md:321`:** "3,6 V = DS mutlak sınırı (VDD + 0,3 V)". DS v5.3 Tablo 5-1 (mutlak sınırlar) yalnız besleme gerilimini
  veriyor (3,6 V). VDD + 0,3 V, Tablo 5-3'teki VIH üst sınırı. Öneri: "DS Tablo 5-3 VIH en çok (VDD + 0,3 V)". `:282`'deki
  "Tablo 5-1, 5-3" atfı da aynı nedenle yalnız 5-3 olmalı.
- **`pin-karari-gunluk.md:88`** (§6): "VBsemi … eşik gerilimi doğrulanmadı (T2 ölçümü bunu kapsar)". Parça artık değişiyor; bu cümle
  sürüm 3 ile eskidi.
- **D7, isteğe bağlı sağlamlık önerisi:** R ölçülmeden bölücü takılırsa ve kartın IS direnci 500 Ω'dan büyükse (ör. 1 kΩ ∥ 1 kΩ değil,
  yalnız 1 kΩ) 6,8 / 5,1 kΩ ile 14 mA'de pin **5,5 V** olur (hesap). T6'nın "R ölçülmeden IS ucu ESP32'ye bağlanmaz" kuralı bunu kapatıyor.
  Kuralın kendisi doğru ve yeterli. Daha sağlam bir seçenek: IS düğümü VS'yi aşamıyorsa (BTS iç yapısı, veri sayfasından **doğrulamadım**)
  k ≤ 3,2 / 14,6 ≈ 0,22 seçmek, örneğin 6,8 / 1,8 kΩ. Bununla pin, kart direncinden bağımsız ≤ ≈ 3,1 V kalır; bedeli ölçeğin yarıya
  inmesi (≈ 11,6 mV / A).
- **IS örneklemesi (bilgi):** IS akımı PWM ile kıyılır. Pin ile GND arasına 100 nF (τ ≈ 2,9 kΩ × 100 nF ≈ 0,3 ms) ADC okumasını
  ortalar. T6 kalibrasyonunda karar verilebilir.
- **T7, T4, T8 ölçütleri:** sayısal değil ("net geçiş", "3,3 V yeter", "–"). T7 için DS Tablo 5-3'ten öneri: LOW ≤ 0,25 × VDD ≈ 0,8 V,
  HIGH ≥ 0,75 × VDD ≈ 2,5 V. T4: "3,3 V PWM'de motor iki yönde döner, IN pininde ≥ 2,6 V".

## Doğruladıklarım

- **Çekirdek sürümü:** `platformio.ini:8` `espressif32@6.9.0`. `platform-espressif32` `v6.9.0` `platform.json:81-85`
  `framework-arduinoespressif32 ~3.20017.0` = Arduino-ESP32 2.0.17. `boards/esp32dev.json` variant `esp32`.
- **UART varsayılanları** (Ö4'teki satırlar): rapordaki 4, 25, 26, 27, 16, 17 notları ve AR / AR3 satır atıfları doğru.
  `pins_arduino.h` 3.0.7 ile 3.3.0 aynı; 2.0.17'de SS 5, MOSI 23, MISO 19, SCK 18, SDA 21, SCL 22, T0 = 4, A10 = 4, DAC 25 / 26.
- **IDF v5.1.4 `uart.c:615-623`:** TX `gpio_set_level(tx, 1)`, RX `GPIO_PULLUP_ONLY`.
- **DS v5.3 Tablo 5-3:**
  - VOH ≥ 0,8 VDD (2,64 V), VIH en çok VDD + 0,3 V, VIL en çok 0,25 VDD.
  - IIH / IIL ≤ 50 nA.
  - **RPU / RPD yalnız tipik 45 kΩ, en az / en çok değer yok** (rapor doğru söylüyor).
  - Ek A notu: wpu / wpd ≈ 75 µA.
- **D1 hesabı (kendim):**
  - Sürülü gate: 3,3 V → 3,15 V; 2,64 V → 2,52 V. Pin akımı 0,54–0,67 mA, tepe 15 mA.
  - Boşta dahili pull-up ile: 0,31 V (45 kΩ), 0,35 V (75 µA), 0,48 V (varsayımsal 30 kΩ, 3,6 V).
  - Kaçak ≤ 0,7 mV.
  - T2 ölçütüne göre pay 0,5 − 0,49 V. MOSFET en düşük eşiğine göre 0,16 V. Rölenin çekmesine göre çok büyük (Ö7).
  - T2'nin 0,5 V ölçütü güvenli yönde. Gerçek pull-up 30 kΩ'dan küçükse T2 yanlış alarm verebilir, tehlike vermez.
- **D9:** veri sayfası değerleri rapordakiyle aynı (Ö7). Bobin diyotları `elektrik.md`'de var. MOSFET'ler arayüz kartında, gate
  pull-down'ı gate tarafında.
- **D7 hesabı (kendim):**
  - 500 Ω: 2,88 V (14 mA), 1,44 V (7 mA). 470 Ω eklenince 2,71 V. Rb 1 kΩ + 6,8 / 2,2 kΩ: 3,08 V.
  - Ölçek 24,2 mV / A, 0 dB alt sınırı ≈ 4,1 A.
  - Eski firmware'in 32 / 33'ü sürmesi: R1 üstünden IS'e ≈ 0,45 mA.
  - Pin, R ölçülüp formül uygulandığı her durumda ≤ 3,2 V. "4 A altı okunmaz" sonucu doğru (Ö3'teki örnek hariç).
- **Eski firmware yeni kablajda** (`main` `2be1c63`, `motorlar.cpp:141-144, 205-208, 216-217`, `main.cpp:76, 82`; `Serial2`, SPI,
  `touchRead` yok):
  - K1: 4'e dokunulmuyor → 0 V.
  - K2: 19 `INPUT_PULLUP` → ≤ 0,49 V → iletmez.
  - 13 ve 27 HIGH olur, ama bara yok.
  - Rapor sonucu **kural olarak** yazıyor ("yalnız bu tabloya göre yazılmış firmware yüklenir; paylar şans, kural değil",
    `pin-haritasi.md:199`). Doğru.
- **Tutarlılık:** rapor §2, §9 JSON (betikle: `json.loads`, ASCII, 24 pin, tekrar yok), `elektrik.md:472-492` ve pano gövdesi satır 5 pin
  pin aynı; 12 boş. Pano gövdesi taslaktaki metinle bayt bayt aynı (2.517 karakter). PCA9685: `main` `kanallar.yaml:61-73` ile rapor ve
  `elektrik.md:494` aynı; sonar trig 10 / 11 / 12 başka işle çakışmıyor.
- **Kalıntılar:**
  - Üç depo dosyasında 10 kΩ gate, 1N5819 (IS için) ve GPIO12 / 2 ya da 16 / 17 röle atfı yalnız tarihçe / "14.11'e dek" / "kaldırıldı"
    bağlamında.
  - Tek istisna Ö5'teki iki "IRLZ44N".
  - `elektrik.md`'deki 1N5819'lar VBUS içindir (E4), doğru.
- **`elektrik.md` farkı:** yalnız pin / röle / MOSFET şartı / BTS adları / pin planı / açık işler 4 ve 19 değişmiş. 220 Ω, 5,6 Ω 11 W,
  F1–F5, 1N4007, kablo, akım değerleri aynı. 522 satır; `:466-496` pin planı, `:505` "Kabuk" (C adımı listesindeki 499 → 505 doğru).
- **Günlük §7** sürüm 3 ile aynı (K1 4, K2 19, 16 / 17 enkoder, 4,7 kΩ, MOSFET şartı, 1 kΩ, diyotsuz bölücü). §8.4 "geçersiz" diye
  işaretli.
- **Test sırası:**
  - T1 kablajdan önce yalnız USB ile.
  - T2 (a)–(e) F5 takılı değilken, (f)–(g) bara yüksüz ve akım sınırlı.
  - T6'da R ölçülmeden IS bağlanmıyor.
  - T4 tezgâhta akım sınırlı.
  - Sıra güvenli (Ö1 ve Ö2 hariç).
- **Pano protokolü:** bilgi + soru, durum `soru`, YZ karar seçmiyor, `--kaynak` satırları satır numaralı. "Ahmet'in insan oturumu
  teyidi" notu var. Gövde tek başına okununca neyin değiştiği (dört iş), neden (iki kaynaklı gerekçe) ve Efe'den ne beklendiği (itiraz
  hakkı, PCA9685 sorusu) anlaşılıyor; raporla çelişmiyor (Ö6'daki eksikler hariç).
- **Gizlilik:** üç depo dosyası, `elektrik.md` farkı ve pano taslağı / gövdesinde yerel yol, kullanıcı adı, makine adı, takma ad,
  e-posta, parola / anahtar, ağ adı yok (betikle tarandı). Kişi adları yalnız Ahmet / Efe.

## Bakamadıklarım / kaynağını bulamadıklarım

- **BTS7960 IIS(lim) ve kILIS:** Infineon tam veri sayfasına bu kontrolde de erişemedim.
  - Infineon bağlantıları 404 verdi; iki satıcı PDF'i, iki veri sayfası arşivi ve bir HTML aynası 403 / bot engeli verdi.
  - İndirilebilen tek "BTS7960" PDF'i modül kılavuzuydu, değer içermiyordu.
  - Değer (4 / 4,5 / 7 mA, kILIS 8500) hâlâ ikinci elden. Bir arama özeti 4,5 mA'nın başka bir parçaya (FAN7093) ait olabileceğini
    söylüyor; bunu da doğrulayamadım.
  - Hesap 14 mA en kötü varsayımıyla yapıldığı ve T6 / Ö2'deki enjeksiyon testi bunu ölçeceği için sonuç değişmiyor.
  - BTS IS düğümünün VS ile sınırlı olduğu (Ö8 öneri) da doğrulanmadı.
- **ESP32 iç pull-up'ının en düşük değeri:** Espressif vermiyor. Teknik başvuru kılavuzuna bakmadım.
- **Arduino 3.x `initArduino` (`esp32-hal-misc.c` 3.0.7 / 3.3.0)** dosyalarını indirdim, ama 4 / 19'a dokunan bir yol için satır satır
  okumadım. Y13 (çekirdek sabit) bunu kapsıyor.
- **3.3.0'ın dayandığı ESP-IDF sürümünün `uart_set_pin` davranışı:** Arduino 3.3.0 o fonksiyonu kullanmadığı için gerekmedi.
- **ROM'un indirme kipinde GPIO4'e ne yaptığı** ve PSRAM yoklaması sonrası 16 / 17'nin durumu: kaynak yok, T2 ölçüyor (önceki kontrollerle
  aynı).
- **Delikli MOSFET / BJT seçenekleri** (Ö7): veri sayfasıyla teyit edilmedi.
- **Direnç setinin içeriği** (470 Ω, 1 / 2,2 / 4,7 / 5,1 / 6,8 kΩ) satıcı sayfasından tarafımdan açılmadı.
- **Pano mesajları** (#19, #20, pano #6 #21): okunmadı (brief gereği).

## Kaynaklar (bu kontrolde açılanlar)

- `espressif/arduino-esp32` `2.0.17`, `3.0.7`, `3.3.0`: `cores/esp32/HardwareSerial.h`, `HardwareSerial.cpp`, `esp32-hal-uart.c`,
  `esp32-hal-misc.c`, `variants/esp32/pins_arduino.h`.
- `espressif/esp-idf` `v5.1.4`: `components/driver/uart/uart.c`.
- `platformio/platform-espressif32` `v6.9.0`: `platform.json`, `boards/esp32dev.json`.
- Espressif *ESP32 Series Datasheet* v5.3: Tablo 5-1, 5-2, 5-3; Ek A not (wpu / wpd ~75 µA).
- Alpha & Omega *AO3400A* veri sayfası Rev 3.1 (2023-07); Infineon *IRLML6344TRPbF* veri sayfası.
- Depo: `origin/main` `2be1c63` (`platformio.ini`, `pinler.h`, `main.cpp`, `motorlar.cpp`, `servolar.cpp`, `kanallar.yaml`),
  `planlama/maliyet.json:104-116`, çalışma ağacındaki `elektrik.md` (ve `git diff`), `pin-haritasi.md`, `pin-karari-gunluk.md`,
  `pin-karari-kontrol.md`, `pin-karari-kontrol-2.md`; pano taslağı ve gövdesi (depo dışı); `PROTOKOL.md`.
