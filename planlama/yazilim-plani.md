# Yazılım planı (11 Ekim 2026)

Kaynak: mimari önerisi `raporlar/kaynaklar/02-yazilim-yapay-zeka.md`, donanım ve eklem sınırları
`tasarim/freecad/OZET.md`, modül BOM'ları, elektrik kararları `planlama/adim3/elektrik.md`. Saatler **tahmini**.
**Hafta numarası dönem haftasıdır** (proje planıyla tek takvim, 15 Ekim 2026 D6): H1 = 28 Eylül – 4 Ekim, H3 = 12–18 Ekim,
H16 = 11–17 Ocak. (Bu planın 11 Ekim sürümündeki "hafta 1" = H3; bütün haftalar +2 kaydırıldı.)
Teslim tarihi 1–2 hafta oynayabilir (Duffy, 11 Ekim 2026).

## İlke

- **Robot bitmeden yazılım başlar.** Ses hattı, yüz ekranı ve jest aracı masada (robot olmadan) yazılır.
  Motor ve servo kodu ise 1 motor + 2 servoluk bir masa düzeneğinde yazılır. Robot H9'da elektriği
  alınca kod büyük ölçüde hazır olur.
- **ROS 2 yok.** Kullanılan yapı düz Python (Pi 5) + ESP32 (Arduino çatısı, PlatformIO) + seri JSON.
- **Ters kinematik yok.** Kollar, kayıtlı jestleri oynatır.
- **Güvenlik iki katmanda.** Donanım acil stop gücü keser; güç ancak ESP32'nin "devreye al" komutuyla geri gelir (E3).
  ESP32 sınırları her komutta tekrar kontrol eder. Pi'den yanlış komut gelse de kol kabuğa giremez.

## Mimari (V3 donanımına göre)

```
 Raspberry Pi 5 — KAFADA (K4; Python asyncio, tek süreç, systemd ile açılışta başlar)
 ├─ ses        bas-konuş düğmesi → ReSpeaker Lite (USB) → STT (bulut) → LLM → TTS → MAX98357A (I2S, kafada)
 ├─ davranis   durum makinesi: BEKLE / DİNLE / DÜŞÜN / KONUŞ / JEST / ACİL
 ├─ yuz        7" HDMI LCD (micro HDMI, kafa içi): göz-ağız animasyonu (pygame), duruma göre ifade
 ├─ gorus      Camera Module 3 (CSI, 300 mm FPC): yüz algılama → kafa hedefi, düğmeyle VLM (esnek hedef)
 └─ seri       USB 1,25 m boyundan tabana (ESP32 CP2102), 115200, satır başına bir JSON mesajı; DTR/RTS kapalı açılır (aşağıda)
                    │
 ESP32-WROOM-32 — TABANDA (alt kontrolcü, 100 Hz döngü)
 ├─ tahrik     2 × BTS7960 (her biri bir yanın iki JGB37'sini paralel sürer), yan başına bir enkoder (PCNT, arka), yan başına hız PID
 ├─ servo      PCA9685 (I2C, mantık 3V3) → 10 servo: 2 × (omuz S1, S2, dirsek, bilek) + kafa pan, tilt; kanal 10–12 sonar trig
 ├─ sensör     3 × HC-SR04 (echo bölücüyle), BNO055 (I2C), akü gerilimi (GPIO36, 100k/18k), PC817 #1 acil stop / #2 anahtarlı 12 V
 ├─ güç        röle K1 "devreye al" (GPIO12) + ön şarj rölesi K2 (GPIO2): E3 + E9 dizisi
 ├─ gogus      Nextion NX1060P101 10,1" (K2), UART2 (GPIO17/16): menü ve durum çubuğu; Pi komutu ESP32 üzerinden
 ├─ güvenlik   500 ms Pi'den mesaj gelmezse teker DUR, kol yerinde kalır · eklem sınırı · kafa-kol yasak bölgesi
 └─ teleop     Bluetooth gamepad (Bluepad32): Pi çökse de robot kumandayla sürülür
```

### Seri protokol (ilk taslak)

| Yön | Mesaj | Örnek |
|---|---|---|
| Pi → ESP | sürüş | `{"t":"drv","v":0.20,"w":0.0}` (m/s, rad/s) |
| Pi → ESP | eklem hedefi | `{"t":"jnt","q":{"r_s1":30,"r_s2":10},"ms":600}` (derece, varış süresi) |
| Pi → ESP | kalp atışı | `{"t":"hb"}` (5 Hz) |
| ESP → Pi | durum | `{"t":"st","v":0.19,"enc":[...],"imu":[r,p,y],"son":[80,120,95],"es":0,"vb":13.1,"q":{...}}` (20 Hz) |
| ESP → Pi | olay | `{"t":"ev","k":"estop"}` · `"sinir"` · `"engel"` · `"egim"` · `"reset"` (ESP32 yeniden başladı, güç kapalı) |
| Pi → ESP | devreye al | `{"t":"arm"}` (E3 + E9 dizisi; yalnız mantar serbestken) |

### Donanımdan gelen kurallar (düzeltme planı 3. ve 5. adım, `planlama/adim3/elektrik.md`)

- **Seri port DTR/RTS kapalı açılır (E3).** DevKit'in otomatik reset devresi, Pi portu açıp kapatırken ESP32'yi resetleyebilir. Reset →
  GPIO12 LOW → röle bırakır → servo ve motor gücü kesilir, **kollar düşer**. pyserial'de `ser.dtr = False; ser.rts = False` ayarlanıp
  sonra `ser.open()`; Linux'ta ayrıca `stty -F /dev/ttyUSB0 -hupcl`. İlk bağlantı testinde ESP32'nin boot mesajı basmadığı görülmeli.
- **ESP32 reseti = güç kapalı.** Reset sonrası röle kapalı açılır; ESP32 `ev reset` gönderir, Pi ACİL durumuna geçer ve yeniden devreye
  alma ancak operatör komutuyla olur.
- **"Devreye al" dizisi (E3 + E9).** Önkoşul: mantar serbest (PC817 #1 LOW), PCA9685 çıkışları servoların **son bilinen konumunda**,
  BTS EN = 0 ve PWM = 0, açık komut (Nextion düğmesi ya da Pi `arm`). Sonra: K2 (GPIO2) = 1 → 300 ms → PC817 #2 LOW teyidi → K1 (GPIO12) = 1
  → 100 ms → K2 = 0. PC817 #1 HIGH görülünce GPIO12 hemen 0 ve kilit. K2 en çok 1 s açık kalır.
- **Yay çizerek dönüş (K1).** Kare teker düzeninde yerinde dönüş motorları zorlar (E0). Sürüş yazılımı her durumda yay çizerek döner
  (`w` sınırı hıza bağlı); yerinde dönüş yalnız JGB37 ölçümü ve omni kararından sonra, sınırlı açısal hızla açılır. İvme düz zeminde ≤ 0,5 m/s²,
  rampada / eğimde ≤ 0,1 m/s² ve kollar ev pozunda (Y1; karar 29 Ekim 2026, akü yerinde: `planlama/kararlar-2026-10-29.md`).
- **Pi kafada (K4).** Besleme Pololu 5 V (PD yok): EEPROM `PSU_MAX_CURRENT=5000`, `config.txt` `usb_max_current_enable=1`
  (Y0 kurulum adımı). ESP32 kafadaki Pi'ye tek USB kablosuyla bağlı; HDMI ve CSI boyundan geçmez.
- **Sonar trig PCA9685'ten** (kanal 10–12, I2C ile ≥ 10 µs darbe); echo GPIO39/34/35. Akü ADC'si tek seferlik multimetre kalibrasyonu ister.

Eklem sınırları ve yasak bölge **tek kaynaktan** gelir: `kod/ortak/eklem_sinirlari.json`. Değerler
`OZET.md`'deki tablodan alınır, ESP32 için C başlık dosyası buradan üretilir. Sınırlar elle iki yerde yazılmaz.

## İş paketleri

| # | Paket | İçerik | Bağımlı | Kabul testi | Saat | Hafta |
|---|---|---|---|---|---|---|
| Y0 | Altyapı | `kod/` deposu (esp32/, pi/, ortak/, araclar/), Pi OS + SSH (Pi 5 güç ayarları), PlatformIO, protokol belgesi, `eklem_sinirlari.json`, seri port DTR/RTS kapalı açılış | — | Pi ile ESP32 `hb`/`st` alışverişi yapıyor | 6–8 | 3–4 |
| Y1 | Tahrik | BTS7960 PWM, enkoder (yan başına bir), yan başına PID, ivme rampası (düz zeminde ≤ 0,5, rampada ≤ 0,1 m/s² + kollar ev pozunda; 29.10), yay çizerek dönüş, watchdog | Masa düzeneği | Tekerlek havadayken hedef hızın ±%10'unda, kablo çekilince 500 ms içinde duruyor | 15–20 | 4–6 |
| Y2 | Servo | PCA9685, servo başına kalibrasyon (sıfır kayması, sol kolda işaret tersliği), hız sınırlı yumuşak geçiş, sınırlar, yasak bölge, açılışta servoları sırayla güçlendirme | Masa düzeneği, Y0 | Sınır dışı komut kırpılıyor, yasak bölge reddediliyor, açılışta sıçrama yok | 12–16 | 5–7 |
| Y3 | Güvenlik ve sensör | Acil stop algılama (PC817) → ACİL durumu, "devreye al" dizisi (K1 + ön şarj K2), ESP32 reset durumu, sonarla yavaşlama ve durma, BNO055 eğim alarmı, akü gerilim uyarısı | Y1 | 30 cm'de engel olunca duruyor, 15° eğimde alarm veriyor, düşük gerilimde uyarıyor | 10–12 | 7–8 |
| Y4 | Teleop | Bluetooth gamepad ile sürüş ve hazır jest tuşları, ölü adam tuşu (bırakınca durur) | Y1 | Pi kapalıyken kumandayla sürülüyor | 6–8 | 6–7 |
| Y5 | Ses hattı | Düğme + LED, akışlı STT (Deepgram), LLM (kısa cevap, Türkçe kişilik istemi), akışlı TTS, yarım dupleks | Pi + mikrofon + hoparlör (robot gerekmez) | Masada 10 soruda ortalama tepki ≤ 2 s | 25–35 | 4–9 |
| Y6 | Çevrimdışı yedek | Vosk small-tr ile sabit komutlar + Piper TTS, internet kesilince otomatik geçiş | Y5 | İnternet kesikken 10 komutun en az 8'i tanınıyor | 8–10 | 11–12 |
| Y7 | Davranış | Durum makinesi, LLM cevabındaki jest etiketi (`[el_salla]`) → jest, yüz ifadesi eşlemesi | Y5, Y8 | 3 senaryo baştan sona hatasız akıyor | 12–15 | 9–11 |
| Y8 | Jest kütüphanesi | Jest dosyası (zaman damgalı eklem kareleri, JSON) + kayıt aracı. **Jest önce FreeCAD modelinde** oynatılıp çakışma kontrolünden geçer, sonra robota gider. Bunun için **yeni bir araç yazılır** (jest JSON → eklem açıları → `carpisma.py` / `eklem_dogrulama.py` ile kontrol). `hareket_dongu.py` jest oynatmaz: yalnız montajdaki sabit `Kollari_oynat` simülasyonunu döngüde gösterir | Y2 | 8 jest (selam, el sallama, işaret etme, düşünme, onaylama, hayır, karşılama, veda) FreeCAD'de çakışmasız, robotta düzgün | 15–20 | 8–12 |
| Y9 | Yüz ekranı | 7" LCD'de göz ve ağız animasyonu, konuşurken ağız hareketi, ifadeler (mutlu, düşünüyor, dinliyor, şaşkın) | Pi + LCD (robot gerekmez) | 30 fps, durum değişince 200 ms içinde ifade değişiyor | 10–12 | 7–10 |
| Y10 | Göğüs ekranı | Nextion Editor'da menü (tanıtım, soru sor, jest göster, "devreye al"), durum çubuğu; ESP32 UART2 sürücüsü, dokunmatik olaylar Pi'ye | Nextion (K2), Y0 | Dokunuşla jest tetikleniyor | 8–10 | 10–11 |
| Y11 | Görüntü (esnek) | MediaPipe yüz algılama → kafa pan/tilt takibi, düğmeyle "ne görüyorsun?" (bulut VLM) | Y2, kamera kablosu | Kafa 1–2 m'deki kişiyi takip ediyor | 20–30 | 12–14 |
| Y12 | Entegrasyon ve test | Açılışta otomatik başlatma, kayıt (log), demo modu, 3 senaryo × 20 deneme, hata listesi | Hepsi | 60 denemenin en az 55'i başarılı | 15–20 | 13–15 |
| | **Toplam** | | | | **≈ 160–215** | |

Araştırmadaki tahmin (150–220 saat) ile uyumlu. Y11 yetişmezse 2. döneme kayar. Robot onsuz da tam bir ürün olarak kalır.

## Kilometre taşları

| Hafta | Taş | Ölçüt |
|---|---|---|
| H4 | Masa düzeneği konuşuyor | Pi ↔ ESP32 protokolü çalışıyor, 1 motor ve 2 servo komutla dönüyor |
| H7 | Masada konuşan kafa | Y5: düğmeye basınca Türkçe soruya sesli cevap veriyor |
| H9 | **İlk sürüş** | Elektrik robotta, kumandayla geziyor, kollar sınırlar içinde hareket ediyor |
| H11 | Konuşan + jest yapan robot | Y5 + Y7 + Y8 birlikte çalışıyor |
| H14 | Tam görünüş + (esnek) görüntü | Kabuk takılı, yüz takibi varsa çalışıyor |
| H15–16 | Teslim | Y12 testleri geçti, demo videosu çekildi |

## Rol önerisi

| Kişi | Paketler |
|---|---|
| Gömülü / test | Y0 (ESP32 tarafı), Y1, Y2, Y3, Y4 |
| Yazılım / YZ | Y0 (Pi tarafı), Y5, Y6, Y7, Y11 |
| Arayüz | Y9, Y10 |
| Duffy (mekanik + jest) | Y8 (FreeCAD modelini en iyi bilen kişi), Y12 test liderliği |

## Hemen sipariş edilmesi gerekenler (masa düzeneği)

Masada çalışmanın başlaması için robotun gelmesi beklenmez, şu parçalar ilk siparişe girer: ESP32,
1 × BTS7960, 1 × JGB37, PCA9685, 2 × MG996R, Pi 5 + hafıza kartı, ReSpeaker Lite, MAX98357A + hoparlör,
7" LCD, 12 V masa güç kaynağı (bölümde varsa).

`maliyet.json` durumu (15 Ekim 2026): Bluetooth gamepad (Y4) 5. adımda eklendi (tahmini 750 TL, ekipte varsa düşer); akü bölücü
dirençleri 3. adımın direnç setinde. Fuar / demo için mobil erişim noktası listede yok (telefon da olur).

## Açık kararlar (yazılımı etkileyenler)

| Karar | Etki |
|---|---|
| Göğüs ekranı: **karar verildi (K2, 14 Ekim 2026): Nextion NX1060P101** | Arayüz Nextion Editor'da çizilir; ESP32 UART2 ile sürülür, Pi komutları ESP32 üzerinden gider (K4 sonrası boyundan ayrı sinyal geçmez). Waveshare ve ikinci HDMI düştü. |
| Bulut sağlayıcıları (STT / LLM / TTS) ve API anahtarlarını kimin hesabı taşıyacak | Y5 başlamadan seçilmeli; aylık ≈ 10–20 $ (tahmini) |
| Rampada motor torku ve devrilme (1,65 m, akü yerinde) | **Karar 29 Ekim 2026:** rampada ivme ≤ 0,1 m/s² (motor sürekli torkunun ≈ %78'i) ve kollar ev pozunda (devrilme payı 1,58). Düzde ≤ 0,5 m/s² (devrilme sınırı ≈ 2,0 m/s², `planlama/y2/Y2b-ivme.json`). Daha güçlü motor alınırsa rampa sınırı yeniden hesaplanır. |
| Sol kol servo işareti (tahmini: ters) | Y2'de montajdan sonra her servo tek tek doğrulanır |
