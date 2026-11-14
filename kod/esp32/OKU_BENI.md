# ESP32 alt denetleyici (güç, kollar, kafa, tekerlekler)

> **Bu firmware (0.5.0) YALNIZ pin haritası sürüm 4 kablajına yüklenir** (14 Kasım 2026; karar
> `planlama/adim3/pin-haritasi.md`, dal `lale-duzeltme`; tek kaynak `kod/ortak/pinler.json`). 0.4.0 ve
> öncesi bu kablaja yüklenmez (röle ve IS pinlerini yanlış sürer); 0.5.0 da eski kablaja yüklenmez.
>
> **Donanımda doğrulanmadı.** 0.5.0 (14 Kasım 2026: röle K1/K2, acil stop ve bara izleme, arıza durum
> makinesi, PCNT enkoder, yeni pinler) yalnız derlendi (RAM %6,9, flash %24,3, `-Wall` uyarısız), kartta
> denenmedi. Önceki ekler (0.3.0 odometri/yönlü jest, 0.4.0 10 servo/rampa kipi) de kartta denenmedi.
> Aşağıdaki "İlk enerjili deneme" listesini sırayla uygula.

ESP32'nin işi basit: Pi'den gelen tek satırlık JSON komutları uygular. Konuşma, yapay zekâ, yüz
hep Pi'de (`kod/`). ESP32 gücü (K1/K2 röleleri) devreye alır ve bırakır, servoları (PCA9685 ile) ve
iki tekerleği (BTS7960 ile) sürer.

```
Pi (kod/robot/seri.py) --USB kablo, 115200--> ESP32 --I2C--> PCA9685 --> 10 servo
                                                 |--PWM 25/26/27/14 + EN 13--> 2 x BTS7960 --> JGB37 motorlar
                                                 |<--PCNT 18/17, 16/15-- 2 enkoder
                                                 |--GPIO4 K1, GPIO19 K2--> röle sürücüleri (BC337-40) --> anahtarlı bara
                                                 |<--GPIO23 acil stop, GPIO5 bara-- PC817 optokuplörler
                                                 |<--ADC 32/33 BTS IS, 36 akü
```

## 1. Dosyalar

| Dosya | İş |
|---|---|
| `platformio.ini` | Kart (esp32dev), kütüphane ve **çekirdek sürümü sabit** (6.9.0 = Arduino-ESP32 2.0.17; değiştirme, pin haritası Y13), `DURUM_YAYINI` / `ODO_YAYINI` / `IMU_VAR` / `SESSIZLIK_BIRAK_MS` anahtarları |
| `include/pinler.h` | **Üretilir**, elle düzenlenmez: `py -3 kod/ortak/pin_uret.py` (kaynak `kod/ortak/pinler.json`) |
| `src/main.cpp` | Güç notu, kurulum sırası, `setup()` ve `loop()`: her iş kendi zamanında (50 Hz), `delay()` yok; LED |
| `src/guc.*` | Röle K1 (4) / K2 ön şarj (19), EN (13), acil stop (23) ve bara (5) girişi, BTS IS arıza bayrağı (32/33), akü (36); durum makinesi `birakik` / `onsarj` / `devrede` / `ariza`; K2'yi 1 s'de düşüren `esp_timer` |
| `src/seri_protokol.*` | Satır okuma, JSON çözme, komutları ilgili modüle iletme, cevaplar, `guc` olayı. **Sözleşme başlık dosyasında** |
| `src/servolar.*` | PCA9685, açı → darbe (µs), sınıra kırpma, yumuşak geçiş (her 20 ms sınırlı adım), `servolar_yokla` |
| `src/jestler.*` | Jest oynatıcı: iki kare arası doğrusal ara değer, bitince boşta duruş |
| `src/jest_verisi.h` | **Üretilir**, elle düzenlenmez: `py -3 kod/jestler/jest_uret.py` |
| `src/sinirlar_verisi.h` | **Üretilir**, elle düzenlenmez (aynı betik): `IVME_DUZ_SURUS` 0,5, `IVME_DUZ_FREN` 1,8, `IVME_RAMPA_SURUS` 0,1, `IVME_RAMPA_FREN` 0,1 m/s² (`kod/ortak/eklem_sinirlari.json` `teker.ivme_sinir_m_s2`) |
| `src/motorlar.*` | v/w → sol/sağ teker, ivme sınırı (hızlanma ve fren ayrı; `dur` fren sınırıyla), `motorlar_ani_dur` (rampasız: bekçi ve güç bırakma), `motorlar_rampa_modu`, **PCNT** enkoder sayacı (16 bit → 32 bit toplam), PID iskeleti (katsayılar 0) |
| `src/watchdog.*` | 500 ms komut bekçisi (motorları ANINDA durdurur, röleye dokunmaz) + 2 s döngü bekçisi |
| `src/imu.*` | IMU arayüz **iskeleti** (`imu_baslat/imu_var/imu_yaw_derece/imu_egim_derece`); IMU yok, yaw `null`, eğim NAN |

Jestler `kod/jestler/` klasöründe YAML olarak yazılır (`selam`, `isaret`, `evet`, `bosta`);
servo kanal tablosu `kod/jestler/kanallar.yaml`'da (tek kaynak). Açı sınırları ve `bagimli` kısıtı
`kod/ortak/eklem_sinirlari.json`'dan (Ahmet'in CAD betiği üretir; robot açısı = eklem açısı + `eklem_ofset`).
Pinler `kod/ortak/pinler.json`'dan (tek kaynak; değişince önce `pin_uret.py`, sonra derle).

## 2. Kurulum, derleme, yükleme

İki yoldan biri:

- **VS Code:** Eklentiler'den "PlatformIO IDE" kur. `kod/esp32` klasörünü aç; alttaki ✓ derler, → yükler.
- **Komut satırı:** `py -3 -m pip install platformio` (ilk derlemede ESP32 araç zinciri iner, birkaç yüz MB).

Depo kökünden:

```
py -3 kod/ortak/pin_uret.py                 # pinler.json değiştiyse önce bunu çalıştır (--kontrol: güncel mi)
py -3 kod/jestler/jest_uret.py              # jest YAML'ı değiştiyse bunu çalıştır
py -3 -m platformio run -d kod/esp32        # derle
py -3 -m platformio run -d kod/esp32 -t upload        # ESP32 USB'ye takılıyken yükle
py -3 -m platformio device monitor -d kod/esp32       # seri monitör (çıkış: Ctrl+C)
py -3 -m pytest kod/ortak kod/jestler -q    # üreticilerin testleri
```

Yükleme "Connecting...." de takılırsa ESP32 kartındaki **BOOT** düğmesini basılı tut, yükleme
başlayınca bırak. Windows'ta port görünmüyorsa kartın USB çipinin sürücüsünü kur (CP2102 ya da CH340).
Yükleme ve reset anında röleler bırakır (çıkışlar kapanır, taban dirençleri LOW tutar): **kollar düşer**.

## 3. Seri monitörde elle deneme

Monitörü aç, satırı yazıp Enter'a bas. Açılışta ESP32 şunu yazar:
`{"k":"hazir","surum":"0.5.0","pca9685":true,"guc":"birakik"}`

Sonra saniyede 10 kez `{"k":"odo",...}` satırı akar (aşağıda "Odometri telemetrisi"). Elle denerken
kalabalık ederse geçici olarak `-DODO_YAYINI=0` ile derle; cevaplar yine aralarda görünür.
Güç devredeyken 5 s komut yazmazsan güç "sessizlik" arızasıyla bırakır: elle denerken ya sık `ping` yaz
ya da `-DSESSIZLIK_BIRAK_MS=0` ile derle (yalnız masada!).

| Yaz | Beklenen cevap |
|---|---|
| `{"k":"ping"}` | `{"ok":true,"k":"ping","surum":"0.5.0","ms":...,"pca9685":true,"odo":true,"rampa":false,"guc":"birakik","acil":false,"bara":false,"aku":12.61,"ariza":null,"jestler":["bosta","evet","isaret","selam"]}` |
| `{"k":"arm"}` | `{"ok":true,"k":"arm","guc":"onsarj"}`, ardından `{"k":"guc","guc":"onsarj","neden":null,"ms":...}`; ~600 ms sonra `{"k":"guc","guc":"devrede","neden":null,"ms":...}` (ya da `ariza` + neden) |
| `{"k":"arm"}` (mantar basılı) | `{"ok":false,"k":"arm","hata":"acil_stop"}` |
| `{"k":"birak"}` | `{"ok":true,"k":"birak","ms":...}`, devredeyse ardından `{"k":"guc","guc":"birakik","neden":null,"ms":...}` |
| `{"k":"reset"}` | `{"ok":true,"k":"reset"}`, sonra ESP32 yeniden başlar ve `hazir` gelir (güç `birakik`) |
| `{"k":"sur","v":0.1,"w":0}` (devrede değil) | `{"ok":false,"k":"sur","hata":"devrede_degil"}` |
| `{"k":"sur","v":0.1,"w":0}` (devrede) | `{"ok":true,"k":"sur"}` → tekerlek döner, **0,5 s sonra ANINDA durur** (bekçi, rampasız) |
| `{"k":"dur"}` | `{"ok":true,"k":"dur"}` → motorlar **fren sınırıyla** durur (düzde 1,8 m/s², 0,39 m/s'den ~0,2 s), jest kesilir, güç devrede kalır |
| `{"k":"servo","kanal":"kafa_pan","aci":70}` | `{"ok":true,"k":"servo","kanal":"kafa_pan","aci":70}` (kanal numarası da olur: `"kanal":4`). Güç devrede değilken de kabul edilir, ama servoların gücü röle arkasında: kıpırdamaz |
| `{"k":"jest","ad":"evet"}` | `{"ok":true,"k":"jest","ad":"evet"}` (devrede değilken de kabul; kollar güçsüz) |
| `{"k":"jest","ad":"isaret","yon":"sol"}` | `{"ok":true,"k":"jest","ad":"isaret","yon":"sol","yon_uygulandi":true}` → sol kol işaret eder, kafa sola (110) |
| `{"k":"jest","ad":"isaret","yon":"arka"}` | `{"ok":true,"k":"jest","ad":"isaret","yon":"arka","yon_uygulandi":true}` → sağ kol geriye (S1 10) ve yana açık (S2 40), kafa robotun sağına (pan 45) |
| `{"k":"jest","ad":"selam","yon":"sol"}` | `{"ok":true,"k":"jest","ad":"selam","yon":"sol","yon_uygulandi":false}` (selam'ın yön varyantı yok; varsayılan oynar) |
| `{"k":"jest","ad":"isaret","yon":"yukari"}` | `{"ok":false,"k":"jest","hata":"yon_gecersiz"}` (geçerli: `sol`, `sag`, `ileri`, `arka`) |
| `{"k":"rampa","ac":true}` | `{"ok":true,"k":"rampa","rampa":true,"elle":true,"imu":false}` → ivme ve fren 0,1 m/s², jest kesilir, kollar ev pozuna gider |
| `{"k":"jest","ad":"selam"}` (rampa açıkken) | `{"ok":false,"k":"jest","hata":"rampa_modunda"}` (yalnız `bosta` oynar; elle `servo` da reddedilir) |
| `{"k":"sur","v":0.1,"w":0,"rampa":false}` | `{"ok":true,"k":"sur","rampa":false}` (`rampa` isteğe bağlı; verilirse elle kipi ayarlar) |
| `{"k":"odo_sifirla"}` | `{"ok":true,"k":"odo_sifirla"}` → sonraki `odo` satırında `sol` ve `sag` 0'dan başlar |
| `merhaba` | `{"ok":false,"hata":"json_bozuk"}` |

Hata kodları: `json_bozuk`, `k_yok`, `bilinmeyen_komut`, `ad_yok`, `yon_gecersiz`, `bilinmeyen_jest`,
`v_w_sayi_olmali`, `kanal_yok`, `bilinmeyen_kanal`, `aci_sayi_olmali`, `pca9685_yok`, `satir_cok_uzun`,
`rampa_modunda`, `ac_bool_olmali`, `rampa_bool_olmali`, `devrede_degil` (sur), `acil_stop`, `zaten_devrede`,
`mesgul`, `zamanlayici_yok` (arm; sonuncusu K2 süre zamanlayıcısı kurulamadı demek, normalde görülmez).

`sur` birimleri `seri.py` ile aynı: `v` m/s (ileri +), `w` rad/s (sola +); ESP32 ikisini de -1..1'e kırpar.
Robot sürülürken Pi `sur`'u ~200 ms'de bir yeniden göndermeli; 500 ms gelmezse motorlar **anında** durur
(0.5.0'dan beri rampasız; röle bırakılmaz). Durum mesajı (`{"k":"durum","jest":"yok","sur":[0,0],"wd":true,
"rampa":false,"guc":...,"acil":...,"bara":...,"aku":...,"ariza":...}`, 1 s'de bir) için `platformio.ini`'de
`-DDURUM_YAYINI=1` satırının başındaki `;` işaretini sil. `wd:true` = bekçi motorları durdurmuş.

### Güç: devreye alma, bırakma, arıza (0.5.0)

Kural kaynağı pin haritası §4–§5 (Y2, Y4–Y8). Açılışta ve resetten sonra güç **hiçbir zaman kendiliğinden
devreye girmez**; Pi `{"k":"arm"}` göndermelidir.

| Durum | Ne demek | GPIO 19 / 4 / 13 |
|---|---|---|
| `birakik` | Röleler bırakık, bara kapalı. Açılış ve `birak` sonrası | 0 / 0 / 0 |
| `onsarj` | Arm sırası yürüyor | 1 / 0→1 / 0 |
| `devrede` | K1 çekili, bara gerilimli, motor sürülebilir | 0 / 1 / 1 |
| `ariza` | Bir koruma bıraktı. **Kilitli**: yalnız yeni `arm` temizler (`birak` temizlemez) | 0 / 0 / 0 |

**Arm sırası** (süreler `kod/ortak/pinler.json` → `arm`): ön koşul mantar serbest (23 LOW), PCA9685 I2C'de
cevap veriyor, EN = 0, PWM = 0. Sonra **19 = 1** (K2, ön şarj) → **500 ms** → bara (5) LOW değilse 19 = 0 ve
arıza `bara_yok` → **4 = 1** (K1) → **100 ms** → **19 = 0** → bara LOW teyidi (değilse arıza `bara_gitti`) →
13 = 1, `devrede`. Ön şarj süresi raporda 300 ms yazar; 14 Kasım'da 500 ms'ye çıkarıldı (kanal #26/#28).
**GPIO19 hiçbir koşulda 1 s'den uzun HIGH kalmaz:** ana döngüden bağımsız tek atımlık `esp_timer` (1000 ms)
pini düşürür; döngü takılsa da çalışır. Ön şarj bitmeden dolarsa arıza `onsarj_sure` (normalde görülmez).

**Bırakma** aynı döngü turunda: 13 = 0, dört PWM 0, 4 = 0, 19 = 0. Tetikleyenler (onsarj ya da devrede iken):

| Neden | Ne zaman | Sonuç |
|---|---|---|
| (komut) | `{"k":"birak"}` | `birakik` (arıza değil) |
| `acil_stop` | 23 HIGH (mantar basılı ya da F5 attı) | `ariza` |
| `bara_gitti` | K1 çekiliyken 5 HIGH | `ariza` |
| `bara_yok` | ön şarjın sonunda bara gelmedi | `ariza` |
| `is_sol` / `is_sag` | BTS IS ucu art arda 3 örnek (10 ms arayla) doymada (ham ≥ 4000, **TAHMİNİ**, T6 ölçümünden sonra yazılır) | `ariza` |
| `i2c` | devredeyken PCA9685 100 ms'lik yoklamada art arda 3 kez cevap vermedi | `ariza` |
| `sessizlik` | devredeyken 5 s hiçbir geçerli komut satırı yok (`SESSIZLIK_BIRAK_MS`, 0 = kapalı). Pi devredeyken saniyede bir `ping` atar | `ariza` |

- Girişler (23, 5) yoklamayla okunur (kesme yok), 2 ms'de bir; art arda 3 aynı okuma = kabul (~6 ms, **TAHMİNİ**).
  Mantar zaten röle bobinini donanımla keser; bu gecikme güvenliği azaltmaz.
- 500 ms komut bekçisi yalnız motorları durdurur; **K1'i bırakmaz** (onu sessizlik kuralı yapar).
- Röle bırakınca bara düşer: **kollar düşer** (bilinen, kabul edilmiş davranış). `arm` ile güç gelince servolar
  PCA9685'in o anki darbesine tek seferde gider: kolların önü boş olmalı.
- **IS** yalnız arıza bayrağıdır: kart başına ~4 A altı okunmaz (0 dB, 24 mV/A); teker sıkışma algılaması enkoderle
  yapılacak (henüz yok). **Akü** `aku` alanı volt, 100k/18k bölücü, 11 dB; **kalibre edilmedi** (multimetreyle
  karşılaştır, `guc.cpp` `AKU_OLCEK`). 1 V altı = `null`.
- LED: arıza = **çift yanıp sönme** (1,2 s'de iki kısa parlama), PCA9685 yok = 5 Hz, normal = 1 Hz.

### İvme sınırları ve rampa kipi (29 Ekim 2026, sürüm 0.4.0)

Değerler `kod/ortak/eklem_sinirlari.json` → `teker.ivme_sinir_m_s2`'den `src/sinirlar_verisi.h`'ye üretilir
(devrilme payı analizi, `planlama/kopru-mekanik-yazilim.md` F8). Her teker için:

| Durum | Düz zemin | Rampa kipi |
|---|---|---|
| Hızlanma (\|hız\| büyüyor) | 0,5 m/s² | 0,1 m/s² |
| Yavaşlama / fren (\|hız\| küçülüyor, `dur`) | 1,8 m/s² | 0,1 m/s² |

- 0.5.0'dan beri **500 ms bekçi ve güç bırakma rampasızdır** (PWM hemen 0); yalnız `dur` fren sınırıyla durur.
- Yön değişiminde (ileri → geri) önce fren sınırıyla 0'a inilir, sonra hızlanma sınırıyla çıkılır.
- **Rampa kipi** = elle (`{"k":"rampa","ac":true}` ya da `sur`'daki `rampa`) **veya** IMU eğimi. IMU eğimi
  geçerliyse `main.cpp` 3,0° üstünde açar, 1,5° altında kapatır (histerezis, TAHMİNİ); IMU yoksa (bugün)
  yalnız elle. Elle açık kip IMU'dan bağımsız açık kalır.
- Kip açıldığı an oynayan jest kesilir, servolar `BOSTA_DURUS`'a (ev pozu) gider; açıkken `bosta` dışındaki
  jest ve elle `servo` `rampa_modunda` hatası alır. Pi tarafı: `seri.rampa(ac)`, telefonda "Rampa" anahtarı.
- **Acil stop** röleleri bıraktırır, bara düşer: motorlar boşa düşer, bu sınırlar o anda işlemez (rampada kayma ayrı konu).
- Doğrulanmadı: gerçek ivme (enkoderle ölç), IMU sürücüsü ve eğim eşikleri.

### Yönlü jest

Pi `{"k":"jest","ad":"isaret","yon":"sol|sag|ileri|arka"}` gönderir (`kod/robot/seri.py`). Yön
varyantları jest YAML'ında `yonler:` bölümüyle yazılır; `jest_uret.py` onları da denetleyip
`src/jest_verisi.h`'ye koyar, ESP32 yalnız doğru kare dizisini seçer (çalışırken açı hesabı yok).

| `yon` | `isaret` ne yapar (açılar TAHMİNİ) | Kaynağı |
|---|---|---|
| `sag` | sağ kol yana-öne (S1 70, S2 80), kafa sağa (pan 70) | `kareler` olduğu gibi |
| `sol` | sol kol yana-öne (S1 70, S2 80), kafa sola (pan 110) | `kareler`'in **aynası**, otomatik |
| `ileri` | iki kol öne yatay (S1 135 = eklem 90), S2 10, kafa düz | `yonler.ileri` kareleri |
| `arka` | sağ kol geriye (S1 10 = eklem −35) + yana açık (S2 40), kafa sağa (pan 45) | `yonler.arka` kareleri |
| yok | `sag` ile aynı | varsayılan |

- **Ayna kuralı** (`kod/jestler/kanallar.yaml`, `ayna` + `ayna_aci`): kol kanalı karşı kola geçer, açı
  aynı kalır (sol servolar `ters: true` olduğu için robot açısı iki kolda aynı anlama gelir); `kafa_pan`
  açısı `180 - açı` olur, `kafa_tilt` aynen. Ayna açısı da sınır denetiminden geçer.
- Jestin o yön için varyantı yoksa (ör. `selam`) varsayılan oynar ve cevapta `"yon_uygulandi":false` olur.
  Geçersiz yön (`"yukari"`, sayı) yine `yon_gecersiz` hatasıdır. `yon` verilmezse cevapta iki alan da yoktur.
- **Bellek:** varyant başına ayrı kare dizisi (10 servoda kare = 44 bayt); `isaret`'in 3 ek dizisi ~396 bayt
  flash. `sag` kopya değildir.
- **Omuzda yana açma ekseni (S2) var** (29 Ekim 2026, kol başına 4 servo): eski "omuz üstünden 150" `arka`
  çözümü kalktı. S2 hiçbir karede 5'in altına inmez; S1 eklem ≥ 120 (robot ≥ 165) iken S2 ≤ 117
  (`bagimli` kısıtı) — `jest_uret.py` kareleri ve aradaki doğrusal yolu denetler.

**Kablaj doğrulama (yönlü jestten önce, kollar takılı, robot sabit, güç devrede):**

1. Kanal planı (elektrik notu): 0-4 sağ kol (S1, S2, dirsek, bilek) + kafa pan, 5-9 sol kol + kafa tilt,
   10-12 sonar trig (10 sağ, 11 orta, 12 sol). `{"k":"servo","kanal":"sol_omuz","aci":60}` → **sol** omuz kıpırdamalı;
   `sol_omuz_yan`, `sol_dirsek`, `sol_bilek` için de aynısı. Kol içi sıra kablajda doğrulanmadı: yanlış
   eklem oynuyorsa `kanallar.yaml`'da `kanal` numaralarını düzelt.
2. Ayna yönü: sırayla `{"k":"servo","kanal":"sag_omuz","aci":60}` ve `{"k":"servo","kanal":"sol_omuz","aci":60}`.
   İki kol da aynı yöne (öne-aşağı) gitmeli. Sol kol geriye gidiyorsa `sol_omuz` için `ters` yanlıştır
   (değiştir); `omuz_yan` (`aci` 30 → iki kol da yana açılmalı), dirsek ve bilek için de aynı deneme.
3. Kafa: `{"k":"servo","kanal":"kafa_pan","aci":70}` robotun **sağına** bakmalı. Tersse `kafa_pan` `ters: true`.
4. `py -3 kod/jestler/jest_uret.py`, yeniden yükle; `isaret` jestini `sag`, `sol`, `ileri`, `arka` ile dene.
   `sol` hareketi `sag`'ın tam aynası olmalı. `arka`'da elin gövdeye çarpmadığını gözle (yavaş hız).

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

- **Sayım (0.5.0): PCNT donanım sayacı** (pin haritası Y8: GPIO kenar kesmesi errata [GPIO-3.14] yüzünden
  güvenilmez). A'nın iki kenarı sayılır, B yönü verir: çözünürlük 0.4.0'daki kesmeyle **aynı**, `TIK_PER_TUR`
  değişmedi. Donanım sayacı 16 bit (±30000'de 0'a döner); firmware her okumada farkı 32 bit toplama ekler.
  Darbe süzgeci 12,5 µs (TAHMİNİ).
- **Sıklık:** varsayılan 10 Hz (`ODO_ARALIK_MS` = 100). Değiştirmek için `platformio.ini`'de `-DODO_ARALIK_MS=...`.
- **Varsayılan AÇIK.** Kapatmak için `platformio.ini`'de `-DODO_YAYINI=0` satırının başındaki `;` işaretini sil.
  Pi `ping` cevabındaki `"odo":true` ile yayının açık olduğunu anlar; eski firmware'de (0.1.0) bu alan yok.
- **Komut değildir, cevap değildir:** `ok` alanı yoktur; Pi komut cevabı beklerken `"k":"odo"` ve `"k":"guc"`
  satırlarını ayıklamalı. Yayın komut bekçisini ve sessizlik sayacını beslemez.
- **Sıfırlama:** `{"k":"odo_sifirla"}` iki toplamı sıfırlar. Motorları durdurmaz.
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

**Güç (0.5.0):** Pi sürmeden önce `{"k":"arm"}` gönderir ve `guc` olayında `devrede`'yi bekler; devredeyken
saniyede bir `ping` atar (5 s sessizlik kuralı). `guc` olaylarını (`ok` alanı yok) komut cevaplarından ayırır.

**Tuzak:** Pi seri portu açtığında DevKit kendini yeniden başlatabilir (USB çipinin DTR/RTS hattı).
29 Ekim 2026'dan beri `seri.py` portu **DTR/RTS kapalı** açar (`port_ac`); Linux'ta ayrıca bir kez
`stty -F /dev/ttyUSB0 -hupcl`. Yine de reset olabilir: `SeriBaglanti` açılışta en çok 3 s
`{"k":"hazir",...}` satırını **ya da** ping cevabını bekler (reset olduysa hazir, olmadıysa ping gelir).
Reset olursa ilk ~1 s açılış yazıları gelir (`seri.py` "bozuk satır" diye log'a yazar, sorun değil); GPIO15
açılışta LOW ise ROM açılış yazısı hiç gelmez (pin haritası Y10). Reset röleleri bıraktırır: güç `birakik`.
Pi'de denenmedi.

## 5. Pin tablosu (KESİN, pin haritası sürüm 4, 14 Kasım 2026)

Tek kaynak `kod/ortak/pinler.json` (rapor §9'un aynısı + `arm` süreleri); `include/pinler.h` ondan üretilir.
Donanım şartlarının ayrıntısı ve kablajda teyit listesi (T1–T8) raporda: `git show origin/lale-duzeltme:planlama/adim3/pin-haritasi.md`.

| GPIO | Yön | İşlev | Donanım şartı / not |
|---|---|---|---|
| 4 | çıkış | **K1 "devreye al" rölesi** (BC337-40 tabanı) | 270 Ω seri + 2,2 kΩ taban → GND zorunlu; açılışta LOW |
| 19 | çıkış | **K2 ön şarj rölesi** | aynı; **en çok 1 s HIGH** (esp_timer) |
| 13 | çıkış | BTS EN, dört uç ortak | 10 kΩ → GND zorunlu; yalnız `devrede` iken HIGH |
| 25 / 26 | PWM | sol BTS IN1 (ileri, RPWM) / IN2 (geri, LPWM) | 20 kHz, 10 bit |
| 27 / 14 | PWM | sağ BTS IN1 / IN2 | 14'te reset sonrası zayıf pull-up (EN LOW iken zararsız) |
| 23 | giriş, pull-up | acil stop (PC817 #1): **HIGH = basılı / F5 attı** | pull-up yalnız 3V3'e |
| 5 | giriş, pull-up | bara (PC817 #2): **LOW = gerilimli** | strapping (yalnız SDIO zamanlaması) |
| 32 / 33 | ADC1, 0 dB | sol / sağ BTS IS (IS1+IS2): yalnız arıza bayrağı | IS → 6,8 kΩ → pin → 5,1 kΩ → GND (önce kart IS direnci ölçülür, T6) |
| 36 | ADC1, 11 dB | akü gerilimi | 100 kΩ / 18 kΩ + 100 nF |
| 18 / 17 | giriş (PCNT) | sol enkoder A / B | 17'de 1 kΩ seri zorunlu (açılışta PSRAM yoklaması sürer) |
| 16 / 15 | giriş (PCNT) | sağ enkoder A / B | 16'da 1 kΩ seri zorunlu; 15 strapping (LOW = ROM yazısı susar) |
| 39 / 34 / 35 | giriş | sonar sağ / orta / sol echo (**sürücü yok**, kapsam dışı) | 4,7 kΩ / 10 kΩ bölücü; 39 errata GPIO-3.11 (36 okunurken ~80 ns LOW) |
| 21 / 22 | I2C | PCA9685 (0x40), ileride BNO055 (0x28/0x29) | pull-up'lar 3V3'e |
| 1 / 3 | UART0 | CP2102 → USB → Pi | başka iş yok |
| 2 | çıkış | kart üstü durum LED'i | dışarıya hiçbir şey bağlanmaz |
| 12 | – | **BOŞ** | hiçbir şeye bağlanmaz, firmware hiç ayarlamaz |

PCA9685 kanalları: 0-4 sağ kol + kafa pan, 5-9 sol kol + kafa tilt (`kod/jestler/kanallar.yaml`), **10 / 11 / 12
sonar sağ / orta / sol trig** (sürücü yok), 13-15 yedek.

**Firmware kuralları (rapor Y1–Y13, bu kodda uygulandı):** `setup()`'ın ilk işi 4, 19, 13 LOW çıkış
(`digitalWrite(p, LOW); pinMode(p, OUTPUT);`, 2.0.17 sırası); sonra PWM'ler görev oranı 0 ile bağlanır.
`Serial1` / `Serial2` / `SPI` hiç açılmaz (varsayılan pinleri röle ve motor pinlerine düşer). GPIO12 hiç
ayarlanmaz. 4 ve 19'un sürüş gücü değiştirilmez. Kullanılmaması gerekenler: GPIO 6-11 (flash), 12.
JTAG kullanılamaz (13-15 dolu). Kart **PSRAM'siz** olmalı (WROVER ya da ...R2 modülde 16/17 enkoder çalışmaz).

## 6. Güç (kısaca; ayrıntı `src/main.cpp` başında ve `planlama/adim3/elektrik.md` E3, E9)

- Motor sürücüleri ve servo DC-DC'leri (üç XL4016: sağ kol A, sol kol B, kafa C) **anahtarlı baradan**; barayı
  K1 bağlar, önce K2 5,6 Ω ön şarj direnciyle doldurur. Açılışta bara hep kapalı; `arm` gerekir.
- Acil stop mantarı iki rölenin bobin beslemesini keser: basılıyken röle çekmez. ESP32 mantarı yalnız okur (23).
- ESP32 ve Pi kendi temiz 5 V hatlarından (bara kapalıyken de çalışır). **Servo asla Pi'nin USB'sinden beslenmez.**
- Bütün topraklar ortak.

## 7. İlk enerjili deneme (sırayla; her adım geçmeden sonrakine geçme)

Kart ve kablaj teyitleri (T1 modül/PSRAM, T2a/T2 röle sürücüsü, T3 EN kilidi, T4 BTS kartı, T5 PC817,
T6 IS direnci, T7 enkoder, T8 LED) raporun §7'sinde; aşağıdaki adımlar onların firmware tarafıdır.

1. **Yalnız ESP32, USB'den, hiçbir şey bağlı değil.** Önce `esptool.py chip_id` (T1: PSRAM yok, revizyon v0.0 değil).
   Yükle. `{"k":"ping"}` → `pca9685:false`, `guc:"birakik"`, `acil:true` (23 boşta pull-up ile HIGH = "basılı"
   sayılır: güvenli yön), `bara:false`, `aku:null`. LED 5 Hz. `{"k":"arm"}` → `acil_stop`. `{"k":"sur",...}` →
   `devrede_degil`. Multimetreyle 4, 19, 13 → GND: 0 V.
2. **Mantık tezgâhı (röle, BTS, bara YOK; 4/19/13'e yalnız ölçü aleti ya da seri dirençli LED).** PCA9685'i
   bağla (VCC 3,3 V, V+ boş). 23 → GND köprüsü (mantar serbest gibi). `arm` → `onsarj`, ~500 ms sonra
   `ariza` + `bara_yok` (5 boşta HIGH); 19 ~500 ms HIGH olup düşmeli, 4 hiç HIGH olmamalı. Sonra 5 → GND
   köprüsü de tak: `arm` → ~600 ms sonra `devrede`; 19 ≈ 600 ms HIGH, 4 ve 13 HIGH kalır. 5 köprüsünü çek →
   aynı turda `ariza` + `bara_gitti`, 4/13 LOW, LED çift yanıp söner. 23 köprüsünü çek → `acil_stop`.
   Devredeyken 5 s komut yazma → `sessizlik`. PCA9685'in SDA'sını çek → ~300 ms içinde `i2c`. `birak` →
   `birakik`; arızadayken `birak` arızayı temizlemez, `arm` temizler. `reset` → `hazir`, güç `birakik`.
3. **Röle sürücüleri (rapor T2a ve T2), F5 takılı, bara yüksüz, akım sınırlı kaynak.** Açılış, USB tak/sök,
   indirme kipi ve yüklemede röle kontağı hiç kapanmamalı, bobin ≤ 0,12 V. `arm`/`birak` ile T2 (f) ve (g).
   Çekiliyken VCE > 0,3 V ise seri direnç 270 → 220 Ω (rapor D1).
4. **Bara gerçek, BTS ve XL girişleri bağlı, motor ve servo SÖKÜK.** `arm` → `devrede`; bara voltajı ve
   `aku` alanı multimetreyle karşılaştırılır (ölçek `guc.cpp` `AKU_OLCEK`). Mantara bas → `acil_stop`,
   bara düşer.
5. **PCA9685 + tek servo, kornası takılı değil** (güç devrede). `servo` komutuyla 90 → 60 → 120 dene;
   yavaş ve yumuşak gitmeli. Sonra 90'da kornayı tak (bkz. `kanallar.yaml` açı kuralı). `birak` → servo gevşer.
6. **Kollar takılı, robot sabit.** Her kanalı `servo` ile tek tek, küçük adımlarla uçlara götür;
   çarpmadan önceki açıyı not et. Sınır `kanallar.yaml`'da DEĞİL, `kod/ortak/eklem_sinirlari.json`'da:
   farkı Ahmet'e bildir (CAD betiği JSON'u yeniden üretir), sonra JSON'u tazele. Yön tersse `ters: true`.
   Sonra `py -3 kod/jestler/jest_uret.py` ve yeniden yükle. Röle bırakınca **kollar düşer**: altı boş olsun.
7. **Jest:** önce `evet` (yalnız kafa), sonra `isaret`, sonra `selam`. Bitince `bosta`ya dönmeli.
   Yönlü `isaret` için önce bölüm 3 "Yönlü jest" kablaj doğrulaması.
8. **Motorlar: tekerlekler HAVADA** (robot takoz üstünde), mantar elinin altında. `arm`, sonra
   `{"k":"sur","v":0.05,"w":0}` → iki teker de İLERİ dönmeli, 0,5 s sonra **anında** durmalı.
   Ters dönen teker: `motorlar.cpp`'de `SOL/SAG_MOTOR_TERS`. `{"k":"dur"}` ~0,2 s içinde (fren sınırı) durdurmalı.
   `{"k":"rampa","ac":true}` sonra aynı `sur`: teker çok yavaş hızlanmalı, `dur` ~4 s'de durdurmalı.
   Sürerken mantara bas: motorlar boşa düşmeli, `acil_stop` olayı gelmeli. Bu adımda IS eşiği (T6) bilinmiyorsa
   yanlış `is_sol`/`is_sag` arızası görülebilir: ham değerleri ölçüp `guc.cpp` `IS_ARIZA_HAM`'ı yaz.
9. **Enkoder (PCNT):** ileri dönüşte sayı artmalı (`ENKODER_TERS`). Tekerleği elle 10 tur çevir, tik farkını
   10'a böl → `TIK_PER_TUR`. Tam PWM'de teker hızını ölç → `TEKER_AZAMI_HIZ`. İz genişliğini ölç.
   Tikleri monitördeki `odo` satırlarından oku: önce `{"k":"odo_sifirla"}`, sonra 10 tur çevir.
   Bulunan değerleri Pi'deki `ayarlar.yaml` → `konum.odometri`'ye de yaz.
10. **Yerde, açık alanda, düşük hız** (`v` 0,1). PID'i ancak bundan sonra, küçük `KP` ile aç.
11. **Pi ile:** `ayarlar.yaml`'da port, `py -3 kod/ana.py`; Pi `arm` + saniyede bir `ping` gönderiyor mu,
    jest ve dur komutları ESP32'ye gidiyor mu gör.

Bekçi testi: ESP32 ayrı beslemedeyken (USB'den değil) Pi `sur` gönderirken Pi programını kapat
ya da USB veri kablosunu çek → motor 0,5 s içinde anında durmalı; 5 s sonra güç `sessizlik` ile bırakmalı.

**Bu sürümde YOK (yapılmadı):** sonar sürücüsü (echo 39/34/35, trig PCA 10-12), enkoderle teker sıkışma
algılaması, IMU sürücüsü, eklem sıfır kayması / tilt sınırı.
