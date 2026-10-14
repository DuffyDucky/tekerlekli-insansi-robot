# Yazılım planı (11 Ekim 2026)

Kaynak: mimari önerisi `raporlar/kaynaklar/02-yazilim-yapay-zeka.md`, donanım ve eklem sınırları
`tasarim/freecad/OZET.md`, modül BOM'ları. Saatler **tahmini**. Hafta 1 = 12–18 Ekim, hafta 14 = 11–17 Ocak.
Teslim tarihi 1–2 hafta oynayabilir (Duffy, 11 Ekim 2026).

## İlke

- **Robot bitmeden yazılım başlar.** Ses hattı, yüz ekranı ve jest aracı masada (robot olmadan) yazılır.
  Motor ve servo kodu ise 1 motor + 2 servoluk bir masa düzeneğinde yazılır. Robot hafta 7'de elektriği
  alınca kod büyük ölçüde hazır olur.
- **ROS 2 yok.** Kullanılan yapı düz Python (Pi 5) + ESP32 (Arduino çatısı, PlatformIO) + seri JSON.
- **Ters kinematik yok.** Kollar, kayıtlı jestleri oynatır.
- **Güvenlik iki katmanda.** Donanım acil stop gücü keser. ESP32 sınırları her komutta tekrar kontrol eder.
  Pi'den yanlış komut gelse de kol kabuğa giremez.

## Mimari (V3 donanımına göre)

```
 Raspberry Pi 5 (Python asyncio, tek süreç, systemd ile açılışta başlar)
 ├─ ses        bas-konuş düğmesi → ReSpeaker Lite (USB) → STT (bulut) → LLM → TTS → MAX98357A (I2S)
 ├─ davranis   durum makinesi: BEKLE / DİNLE / DÜŞÜN / KONUŞ / JEST / ACİL
 ├─ yuz        7" HDMI LCD: göz-ağız animasyonu (pygame), duruma göre ifade
 ├─ gogus      10,1" göğüs ekranı (Nextion ise UART, Waveshare ise ikinci HDMI; bkz. açık kararlar)
 ├─ gorus      Camera Module 3: yüz algılama → kafa hedefi, düğmeyle VLM (esnek hedef)
 └─ seri       USB-UART 115200, satır başına bir JSON mesajı
                    │
 ESP32-WROOM-32 (alt kontrolcü, 100 Hz döngü)
 ├─ tahrik     2 × BTS7960 (tahmini: her biri bir yanın iki JGB37'sini sürer), 4 enkoder (PCNT), yan başına hız PID
 ├─ servo      PCA9685 (I2C) → 10 servo: 2 × (omuz S1, S2, dirsek, bilek) + kafa pan, tilt
 ├─ sensör     3 × HC-SR04, BNO055 (I2C), acil stop kontak bloğu (giriş), akü gerilimi (ADC, bölücüyle)
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
| ESP → Pi | olay | `{"t":"ev","k":"estop"}` · `"sinir"` · `"engel"` · `"egim"` |

Eklem sınırları ve yasak bölge **tek kaynaktan** gelir: `kod/ortak/eklem_sinirlari.json`. Değerler
`OZET.md`'deki tablodan alınır, ESP32 için C başlık dosyası buradan üretilir. Sınırlar elle iki yerde yazılmaz.

## İş paketleri

| # | Paket | İçerik | Bağımlı | Kabul testi | Saat | Hafta |
|---|---|---|---|---|---|---|
| Y0 | Altyapı | `kod/` deposu (esp32/, pi/, ortak/, araclar/), Pi OS + SSH, PlatformIO, protokol belgesi, `eklem_sinirlari.json` | — | Pi ile ESP32 `hb`/`st` alışverişi yapıyor | 6–8 | 1–2 |
| Y1 | Tahrik | BTS7960 PWM, 4 enkoder, yan başına PID, ivme rampası (düz zeminde ≤ 0,5, rampada ≤ 0,25 m/s²), watchdog | Masa düzeneği | Tekerlek havadayken hedef hızın ±%10'unda, kablo çekilince 500 ms içinde duruyor | 15–20 | 2–4 |
| Y2 | Servo | PCA9685, servo başına kalibrasyon (sıfır kayması, sol kolda işaret tersliği), hız sınırlı yumuşak geçiş, sınırlar, yasak bölge, açılışta servoları sırayla güçlendirme | Masa düzeneği, Y0 | Sınır dışı komut kırpılıyor, yasak bölge reddediliyor, açılışta sıçrama yok | 12–16 | 3–5 |
| Y3 | Güvenlik ve sensör | Acil stop algılama → ACİL durumu, sonarla yavaşlama ve durma, BNO055 eğim alarmı, akü gerilim uyarısı | Y1 | 30 cm'de engel olunca duruyor, 15° eğimde alarm veriyor, düşük gerilimde uyarıyor | 10–12 | 5–6 |
| Y4 | Teleop | Bluetooth gamepad ile sürüş ve hazır jest tuşları, ölü adam tuşu (bırakınca durur) | Y1 | Pi kapalıyken kumandayla sürülüyor | 6–8 | 4–5 |
| Y5 | Ses hattı | Düğme + LED, akışlı STT (Deepgram), LLM (kısa cevap, Türkçe kişilik istemi), akışlı TTS, yarım dupleks | Pi + mikrofon + hoparlör (robot gerekmez) | Masada 10 soruda ortalama tepki ≤ 2 s | 25–35 | 2–7 |
| Y6 | Çevrimdışı yedek | Vosk small-tr ile sabit komutlar + Piper TTS, internet kesilince otomatik geçiş | Y5 | İnternet kesikken 10 komutun en az 8'i tanınıyor | 8–10 | 9–10 |
| Y7 | Davranış | Durum makinesi, LLM cevabındaki jest etiketi (`[el_salla]`) → jest, yüz ifadesi eşlemesi | Y5, Y8 | 3 senaryo baştan sona hatasız akıyor | 12–15 | 7–9 |
| Y8 | Jest kütüphanesi | Jest dosyası (zaman damgalı eklem kareleri, JSON) + kayıt aracı. **Jest önce FreeCAD modelinde** (`hareket_dongu.py` altyapısı) oynatılıp çakışma kontrolünden geçer, sonra robota gider | Y2 | 8 jest (selam, el sallama, işaret etme, düşünme, onaylama, hayır, karşılama, veda) FreeCAD'de çakışmasız, robotta düzgün | 15–20 | 6–10 |
| Y9 | Yüz ekranı | 7" LCD'de göz ve ağız animasyonu, konuşurken ağız hareketi, ifadeler (mutlu, düşünüyor, dinliyor, şaşkın) | Pi + LCD (robot gerekmez) | 30 fps, durum değişince 200 ms içinde ifade değişiyor | 10–12 | 5–8 |
| Y10 | Göğüs ekranı | Menü (tanıtım, soru sor, jest göster), durum çubuğu, dokunmatik olaylar | Ekran kararı | Dokunuşla jest tetikleniyor | 8–10 | 8–9 |
| Y11 | Görüntü (esnek) | MediaPipe yüz algılama → kafa pan/tilt takibi, düğmeyle "ne görüyorsun?" (bulut VLM) | Y2, kamera kablosu | Kafa 1–2 m'deki kişiyi takip ediyor | 20–30 | 10–12 |
| Y12 | Entegrasyon ve test | Açılışta otomatik başlatma, kayıt (log), demo modu, 3 senaryo × 20 deneme, hata listesi | Hepsi | 60 denemenin en az 55'i başarılı | 15–20 | 11–13 |
| | **Toplam** | | | | **≈ 160–215** | |

Araştırmadaki tahmin (150–220 saat) ile uyumlu. Y11 yetişmezse 2. döneme kayar. Robot onsuz da tam bir ürün olarak kalır.

## Kilometre taşları

| Hafta | Taş | Ölçüt |
|---|---|---|
| 2 | Masa düzeneği konuşuyor | Pi ↔ ESP32 protokolü çalışıyor, 1 motor ve 2 servo komutla dönüyor |
| 5 | Masada konuşan kafa | Y5: düğmeye basınca Türkçe soruya sesli cevap veriyor |
| 7 | **İlk sürüş** | Elektrik robotta, kumandayla geziyor, kollar sınırlar içinde hareket ediyor |
| 9 | Konuşan + jest yapan robot | Y5 + Y7 + Y8 birlikte çalışıyor |
| 12 | Tam görünüş + (esnek) görüntü | Kabuk takılı, yüz takibi varsa çalışıyor |
| 13–14 | Teslim | Y12 testleri geçti, demo videosu çekildi |

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

`maliyet.json`'da görünmeyen ve eklenmesi gereken kalemler (tahmini, ucuz):
- Bluetooth gamepad (Y4)
- Akü gerilim bölücü dirençleri (Y3)
- Fuar / demo için mobil erişim noktası (telefon da olur)

## Açık kararlar (yazılımı etkileyenler)

| Karar | Etki |
|---|---|
| Göğüs ekranı: **Nextion NX1060P101** (CAD) mı, **Waveshare 10,1" HDMI** (`maliyet.json`) mı? | Nextion: arayüz Nextion Editor'da çizilir, Pi seri porttan komut gönderir. Waveshare: Pi'nin ikinci HDMI'ı kullanılır, arayüz Python'da yazılır. Baskı listesindeki göğüs bandı da bu karara bağlı. |
| Bulut sağlayıcıları (STT / LLM / TTS) ve API anahtarlarını kimin hesabı taşıyacak | Y5 başlamadan seçilmeli; aylık ≈ 10–20 $ (tahmini) |
| Rampada motor torku %90 | Yazılımda ivme ≤ 0,25 m/s² ile çözülüyor (Y1). Daha güçlü motor alınırsa sınır gevşer. |
| Sol kol servo işareti (tahmini: ters) | Y2'de montajdan sonra her servo tek tek doğrulanır |
