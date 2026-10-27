# ESP32 alt denetleyici (kollar, kafa, tekerlekler)

> **Donanımda doğrulanmadı (26 Ekim 2026).** Kod derleniyor; ama pinler, motor/enkoder yönleri,
> servo sınırları, enkoder tik sayısı ve teker hızı tahmini. Aşağıdaki kontrol listesini sırayla uygula.
> 27 Ekim 2026 eki (odometri yayını, `odo_sifirla`, jest `yon`, IMU iskeleti) de yalnız derlendi, kartta denenmedi.

ESP32'nin işi basit: Pi'den gelen tek satırlık JSON komutları uygular. Konuşma, yapay zekâ, yüz
hep Pi'de (`kod/`). ESP32 servoları (PCA9685 ile) ve iki tekerleği (BTS7960 ile) sürer.

```
Pi (kod/robot/seri.py) --USB kablo, 115200--> ESP32 --I2C--> PCA9685 --> 6 servo
                                                 \--PWM--> 2 x BTS7960 --> JGB37 motorlar
                                                 <--kesme-- 2 enkoder
```

## 1. Dosyalar

| Dosya | İş |
|---|---|
| `platformio.ini` | Kart (esp32dev), kütüphane sürümleri (sabit), monitör ayarı, `DURUM_YAYINI` / `ODO_YAYINI` / `IMU_VAR` anahtarları |
| `include/pinler.h` | Bütün pinler tek yerde (önerilen; kablajda doğrula) |
| `src/main.cpp` | Güç notu, `setup()` ve `loop()`: her iş kendi zamanında (50 Hz), `delay()` yok |
| `src/seri_protokol.*` | Satır okuma, JSON çözme, komutları ilgili modüle iletme, cevaplar |
| `src/servolar.*` | PCA9685, açı → darbe (µs), sınıra kırpma, yumuşak geçiş (her 20 ms sınırlı adım) |
| `src/jestler.*` | Jest oynatıcı: iki kare arası doğrusal ara değer, bitince boşta duruş |
| `src/jest_verisi.h` | **Üretilir**, elle düzenlenmez: `py -3 kod/jestler/jest_uret.py` |
| `src/motorlar.*` | v/w → sol/sağ teker, rampa, enkoder kesmesi, PID iskeleti (katsayılar 0), tik sayaçlarını sıfırlama |
| `src/watchdog.*` | 500 ms komut bekçisi + 2 s döngü bekçisi |
| `src/imu.*` | IMU arayüz **iskeleti** (`imu_baslat/imu_var/imu_yaw_derece`); IMU yok, yaw hep `null` |

Jestler `kod/jestler/` klasöründe YAML olarak yazılır (`selam`, `isaret`, `evet`, `bosta`);
servo kanal tablosu ve sınırlar `kod/jestler/kanallar.yaml`'da (tek kaynak).

## 2. Kurulum, derleme, yükleme

İki yoldan biri:

- **VS Code:** Eklentiler'den "PlatformIO IDE" kur. `kod/esp32` klasörünü aç; alttaki ✓ derler, → yükler.
- **Komut satırı:** `py -3 -m pip install platformio` (ilk derlemede ESP32 araç zinciri iner, birkaç yüz MB).

Depo kökünden:

```
py -3 kod/jestler/jest_uret.py              # jest YAML'ı değiştiyse önce bunu çalıştır
py -3 -m platformio run -d kod/esp32        # derle
py -3 -m platformio run -d kod/esp32 -t upload        # ESP32 USB'ye takılıyken yükle
py -3 -m platformio device monitor -d kod/esp32       # seri monitör (çıkış: Ctrl+C)
```

Yükleme "Connecting...." de takılırsa ESP32 kartındaki **BOOT** düğmesini basılı tut, yükleme
başlayınca bırak. Windows'ta port görünmüyorsa kartın USB çipinin sürücüsünü kur (CP2102 ya da CH340).

## 3. Seri monitörde elle deneme

Monitörü aç, satırı yazıp Enter'a bas. Açılışta ESP32 şunu yazar: `{"k":"hazir","surum":"0.2.0","pca9685":true}`

Sonra saniyede 10 kez `{"k":"odo",...}` satırı akar (aşağıda "Odometri telemetrisi"). Elle denerken
kalabalık ederse geçici olarak `-DODO_YAYINI=0` ile derle; cevaplar yine aralarda görünür.

| Yaz | Beklenen cevap |
|---|---|
| `{"k":"ping"}` | `{"ok":true,"k":"ping","surum":"0.2.0","ms":...,"pca9685":true,"odo":true,"jestler":["bosta","evet","isaret","selam"]}` |
| `{"k":"servo","kanal":"kafa_pan","aci":70}` | `{"ok":true,"k":"servo","kanal":"kafa_pan","aci":70}` (kanal numarası da olur: `"kanal":4`) |
| `{"k":"jest","ad":"evet"}` | `{"ok":true,"k":"jest","ad":"evet"}` |
| `{"k":"jest","ad":"isaret","yon":"sol"}` | `{"ok":true,"k":"jest","ad":"isaret","yon":"sol"}` (yön şimdilik yalnız cevaba yazılır; jest hâlâ sağ kolla oynar) |
| `{"k":"jest","ad":"isaret","yon":"yukari"}` | `{"ok":false,"k":"jest","hata":"yon_gecersiz"}` (geçerli: `sol`, `sag`, `ileri`, `arka`) |
| `{"k":"sur","v":0.1,"w":0}` | `{"ok":true,"k":"sur"}` → tekerlek döner, **0,5 s sonra kendiliğinden durur** (bekçi) |
| `{"k":"dur"}` | `{"ok":true,"k":"dur"}` → motorlar anında durur, jest kesilir |
| `{"k":"odo_sifirla"}` | `{"ok":true,"k":"odo_sifirla"}` → sonraki `odo` satırında `sol` ve `sag` 0'dan başlar |
| `merhaba` | `{"ok":false,"hata":"json_bozuk"}` |

Hata kodları: `json_bozuk`, `k_yok`, `bilinmeyen_komut`, `ad_yok`, `yon_gecersiz`, `bilinmeyen_jest`,
`v_w_sayi_olmali`, `kanal_yok`, `bilinmeyen_kanal`, `aci_sayi_olmali`, `pca9685_yok`, `satir_cok_uzun`.

`sur` birimleri `seri.py` ile aynı: `v` m/s (ileri +), `w` rad/s (sola +); ESP32 ikisini de -1..1'e kırpar.
Robot sürülürken Pi `sur`'u ~200 ms'de bir yeniden göndermeli; 500 ms gelmezse motorlar durur.
Durum mesajı (`{"k":"durum","jest":"yok","sur":[0,0],"wd":true}`, 1 s'de bir) için `platformio.ini`'de
`-DDURUM_YAYINI=1` satırının başındaki `;` işaretini sil. `wd:true` = bekçi motorları durdurmuş.

### Odometri telemetrisi

Pi robotun konumunu tekerlek tiklerinden (ölü hesap) bulur; ESP32 bunun için ham sayıları yayınlar:

```
{"k":"odo","sol":1234,"sag":1251,"yaw":null,"ms":104200}
```

| Alan | Anlamı |
|---|---|
| `sol`, `sag` | Açılıştan (ya da son `odo_sifirla`'dan) beri **toplam** enkoder tiki, int32. İleri dönüşte artar (yön `motorlar.cpp`'deki `*_ENKODER_TERS` ile düzeltilmiş). |
| `yaw` | IMU'dan dönüş açısı, derece (sola +). **IMU yok → hep `null`.** IMU gelince `src/imu.*` doldurulur, `-DIMU_VAR=1`. |
| `ms` | ESP32'nin `millis()` değeri; iki satır arası süreyi Pi bununla hesaplar (49 günde bir sıfıra döner). |

- **Sıklık:** varsayılan 10 Hz (`ODO_ARALIK_MS` = 100). Değiştirmek için `platformio.ini`'de `-DODO_ARALIK_MS=...`.
- **Varsayılan AÇIK.** Kapatmak için `platformio.ini`'de `-DODO_YAYINI=0` satırının başındaki `;` işaretini sil.
  Pi `ping` cevabındaki `"odo":true` ile yayının açık olduğunu anlar; eski firmware'de (0.1.0) bu alan yok.
- **Komut değildir, cevap değildir:** `ok` alanı yoktur; Pi komut cevabı beklerken `"k":"odo"` satırlarını ayıklamalı.
  Yayın komut bekçisini beslemez: `sur` gelmezse motorlar yine 0,5 s'de durur.
- **Sıfırlama:** `{"k":"odo_sifirla"}` iki sayacı kesme güvenli şekilde (kilitle) sıfırlar. Motorları durdurmaz.
- **Pi tarafı:** `kod/robot/konum/odometri.py` bu satırları okur.

> **Uyarı (tutarlılık):** ESP32 tik gönderir, metreye Pi çevirir. `TIK_PER_TUR` (şimdi 22 × 90 = 1980,
> tahmini), teker çapı (`TEKER_CAPI_M` = 0,125 m) ve iz genişliği (`IZ_GENISLIGI_M` = 0,426 m) `motorlar.cpp`'de
> ve Pi'deki `ayarlar.yaml` → `konum.odometri` altında **aynı ölçülmüş değerler** olmalı. Birini değiştirirsen
> öbürünü de değiştir; yoksa hız kontrolü ile konum hesabı farklı robotlar varsayar.

## 4. Pi tarafı

`kod/ayarlar.yaml`:

```yaml
seri:
  port: /dev/ttyUSB0     # DevKit (CP2102/CH340 çipli) genelde bu; ESP32-S3/C3 doğrudan USB ise /dev/ttyACM0
  hiz: 115200
```

Hangisi olduğunu bulmak için ESP32'yi Pi'ye tak ve `ls /dev/ttyUSB* /dev/ttyACM*` yaz.
Kullanıcın porta erişemiyorsa: `sudo usermod -aG dialout $USER`, sonra oturumu kapatıp aç.

**Tuzak:** Pi seri portu açtığında DevKit kendini yeniden başlatır (USB çipinin DTR/RTS hattı).
İlk ~1 s ESP32'nin açılış yazıları gelir (`seri.py` bunları "bozuk satır" diye log'a yazar, sorun değil);
`{"k":"hazir",...}` görülünce komut göndermek güvenli.

## 5. Pin tablosu (önerilen; kablajda doğrula)

| İşlev | ESP32 GPIO | Not |
|---|---|---|
| PCA9685 SDA / SCL | 21 / 22 | PCA9685 VCC = ESP32 3,3 V; V+ = ayrı servo beslemesi |
| IMU SDA / SCL (ileride) | 21 / 22 | PCA9685 ile **aynı** I2C hattı; MPU6050 0x68 / BNO055 0x28, adres çakışmaz |
| Sol BTS7960 RPWM / LPWM / EN | 25 / 26 / 27 | R_EN ve L_EN birlikte EN'e; EN'i 10k ile GND'ye çek |
| Sağ BTS7960 RPWM / LPWM / EN | 32 / 33 / 13 | aynı |
| Sol enkoder A / B | 18 / 19 | enkoderi 3,3 V ile besle |
| Sağ enkoder A / B | 16 / 17 | kart **WROVER** ise 16/17 kullanılamaz → 34/35 + 10k pull-up |
| Durum LED'i | 2 | 1 Hz = çalışıyor, 5 Hz = PCA9685 bulunamadı |

Kullanılmaması gerekenler: GPIO 6-11 (flash), 0/2/5/12/15 strapping pinleri (açılışı bozabilir).

## 6. Güç (kısaca; ayrıntı `src/main.cpp` başında)

- Servolar **ayrı** DC-DC'den (5-7,4 V, 6 servo için 10 A+ tepe), PCA9685'in V+ klemensinden. Yanına büyük kondansatör.
- ESP32 ve Pi kendi temiz 5 V hatlarından. **Servo asla Pi'nin USB'sinden beslenmez** (brownout → reset).
- Bütün topraklar ortak.
- Emas acil stop motor ve servo güç hattını doğrudan keser; yazılımdan bağımsızdır.

## 7. İlk çalıştırma kontrol listesi (sırayla)

1. **Yalnız ESP32, USB'den.** Hiçbir şey bağlı değil. Yükle, monitörde `{"k":"ping"}` → cevap gelmeli.
   PCA9685 bağlı olmadığı için `pca9685:false` ve LED hızlı yanıp söner; bu beklenen.
2. **PCA9685 bağlı, servolar SÖKÜK** (V+ beslemesi de yok). `ping` → `pca9685:true`, LED yavaşladı.
   Varsa osiloskopla kanal 0'da 50 Hz, ~1500 µs darbe gör (`{"k":"servo","kanal":0,"aci":90}`).
3. **Tek servo, kornası takılı değil**, V+ beslemesi açık. `servo` komutuyla 90 → 60 → 120 dene;
   yavaş ve yumuşak gitmeli. Sonra 90'da kornayı tak (bkz. `kanallar.yaml` açı kuralı).
4. **Kollar takılı, robot sabit.** Her kanalı `servo` ile tek tek, küçük adımlarla uçlara götür;
   çarpmadan önceki açıyı not et ve `kanallar.yaml`'daki `min_aci`/`max_aci`'yi daralt.
   Yön tersse `ters: true`. Sonra `py -3 kod/jestler/jest_uret.py` ve yeniden yükle.
5. **Jest:** önce `evet` (yalnız kafa), sonra `isaret`, sonra `selam`. Bitince `bosta`ya dönmeli.
6. **Motorlar: tekerlekler HAVADA** (robot takoz üstünde), acil stop elinin altında.
   `{"k":"sur","v":0.05,"w":0}` → iki teker de İLERİ dönmeli, 0,5 s sonra durmalı.
   Ters dönen teker: `motorlar.cpp`'de `SOL/SAG_MOTOR_TERS`. `{"k":"dur"}` anında durdurmalı.
7. **Enkoder:** ileri dönüşte sayı artmalı (`ENKODER_TERS`). Tekerleği elle 10 tur çevir, tik farkını
   10'a böl → `TIK_PER_TUR`. Tam PWM'de teker hızını ölç → `TEKER_AZAMI_HIZ`. İz genişliğini ölç.
   Tikleri monitördeki `odo` satırlarından oku: önce `{"k":"odo_sifirla"}`, sonra 10 tur çevir.
   Bulunan değerleri Pi'deki `ayarlar.yaml` → `konum.odometri`'ye de yaz.
8. **Yerde, açık alanda, düşük hız** (`v` 0,1). PID'i ancak bundan sonra, küçük `KP` ile aç.
9. **Pi ile:** `ayarlar.yaml`'da port, `py -3 kod/ana.py`, jest ve dur komutlarının ESP32'ye gittiğini gör.

Bekçi testi: ESP32 ayrı beslemedeyken (USB'den değil) Pi `sur` gönderirken Pi programını kapat
ya da USB veri kablosunu çek → motor 0,5 s içinde durmalı.
