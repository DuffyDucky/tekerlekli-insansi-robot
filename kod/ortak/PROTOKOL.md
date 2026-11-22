# Lale Pi ↔ ESP32 seri protokolü (sürüm 0.5.0+y0s.1)

> **Bu belge üretilir, elle düzenlenmez.** Tek kaynak `kod/ortak/protokol.json`; üretici `py -3 kod/ortak/protokol_belge_uret.py`. Tarih 2026-11-22.

Taban sözleşme: firmware **0.5.0** (`origin/main` `kod/esp32/src/seri_protokol.h`, Efe; derlendi, kartta denenmedi). Kaynak: origin/main 71cf76d kod/esp32/src/seri_protokol.h (firmware 0.5.0 sozlesmesi; Efe) + planlama/yazilim-plani.md + planlama/adim3/pin-haritasi.md surum 4 + planlama/adim3/elektrik.md E3/E9. Belge: kod/ortak/PROTOKOL.md (bu dosyadan uretilir, elle duzenlenmez).

**İşaretler:** "0.5.0" = firmware 0.5.0 sözleşmesinde aynen olan (planla bağı Kaynak sütununda; planda olmayan 0.5.0 kuralı da bu işareti taşır, ör. 5 s sessizlik). **TASLAK** = plan istiyor ama ayrıntıyı vermiyor ya da 0.5.0'da yok; Y0s paketinde (sahte ESP32) karar verildi, gerçek firmware'e girmeden önce Efe / Ahmet onayı ister. Sahte ESP32 bunları uygular; gerçek kartta yoksa ilgili testler "yetenek yok" diye atlanır.

**Dürüstlük notu:** sahte ESP32 bu sözleşmenin çalıştırılabilir modelidir; gerçek ESP32'nin C++ kodunu sınamaz. İkisi ayrışırsa önce bu belge (JSON) düzeltilir.

## 1. Çerçeve

| Ne | Değer |
| --- | --- |
| baud | 115200 |
| satir_sonu | '\n' |
| atilan_bayt | '\r' |
| en_cok_bayt | 200 |
| kodlama | utf-8 |
| bos_satir | sessizce gecilir, cevap yok |
| uzun_satir | 200 bayttan uzun satir atilir, satir sonunda {"ok":false,"hata":"satir_cok_uzun"} |
| json_olmayan_gelen_satir_pi | Pi yok sayar (pin-haritasi.md Y10: ROM acilis yazisi gelebilir) |
| port_acilisi | DTR/RTS reset yapmayacak sirayla acilir (yazilim-plani.md 'Donanimdan gelen kurallar' E3; main kod/robot/seri.py port_ac) |

Kaynak: seri_protokol.cpp SATIR_UZUNLUGU, seri_isle; yazilim-plani.md mimari 'satir basina bir JSON'.

## 2. Zamanlar (ms)

| Ad | Değer | Ne | Kaynak | İşaret |
| --- | --- | --- | --- | --- |
| `bekci` | 500 | son gecerli 'sur'dan bu kadar sonra motorlar ANINDA (rampasiz) durur; rolelere dokunmaz | yazilim-plani.md mimari 'guvenlik 500 ms'; Y1 kabul testi; main watchdog.cpp KOMUT_ZAMAN_ASIMI_MS | 0.5.0 |
| `sessizlik` | 5000 | guc 'devrede' iken bu kadar hic gecerli komut satiri gelmezse guc birakilir, ariza 'sessizlik' | main guc.h SESSIZLIK_BIRAK_MS | 0.5.0 |
| `ping_onerilen` | 1000 | Pi devredeyken kalp atisi ('ping') araligi | main seri_protokol.h ping satiri; plan hb 5 Hz (eskimis taslak) | 0.5.0 |
| `sur_tekrar_onerilen` | 200 | surerken 'sur' tekrar araligi (bekci 500 ms) | main kod/robot/seri.py WATCHDOG notu | 0.5.0 |
| `odo_aralik` | 100 | {"k":"odo"} yayini (10 Hz) | main seri_protokol.h ODO_ARALIK_MS | 0.5.0 |
| `onsarj_bekleme` | 500 | K2 cekildikten sonra bara bekleme; sonra bara yoksa ariza 'bara_yok' | main kod/ortak/pinler.json arm.onsarj_bekleme_ms (300 -> 500, kanal mesaji #26/#28); elektrik.md E9 '500 ms onerilir'; pin-haritasi.md Y4 hala 300 yaziyor (Y0s-gunluk.md Ç2) | 0.5.0 |
| `k1_sonrasi` | 100 | K1 cekildikten sonra K2 birakilir, bara teyidi | pin-haritasi.md Y4; main pinler.json | 0.5.0 |
| `k2_en_cok` | 1000 | K2 bundan uzun cekili kalmaz (ayri zamanlayici); dolarsa ariza 'onsarj_sure' | pin-haritasi.md Y4; main pinler.json | 0.5.0 |
| `sonar_aralik` | 100 | {"k":"sonar"} yayini (10 Hz) | TASLAK (plan belirtmiyor; plan 'st' 20 Hz idi) | **TASLAK** |

## 3. Sınırlar ve güvenlik kuralları

| Ad | Değer | Ne | Kaynak | İşaret |
| --- | --- | --- | --- | --- |
| `v_giris` | 1.0 | sur.v once +-1'e kirpilir, sonra teker azami hizina orantili kucultulur | main motorlar.cpp GIRIS_SINIRI, motorlar_hedef | 0.5.0 |
| `w_giris` | 1.0 | sur.w +-1'e kirpilir | main motorlar.cpp GIRIS_SINIRI | 0.5.0 |
| `ivme_m_s2` | — |  | kod/ortak/eklem_sinirlari.json teker.ivme_sinir_m_s2 (karar 29.10) | 0.5.0 |
| `servo_aci` | — | servo komutunun 'aci'si servo sinirina kirpilir; cevapta uygulanan aci | main servolar.cpp sinira_kirp; yazilim-plani.md Y2 'sinir disi komut kirpiliyor' | 0.5.0 |
| `servo_bagimli` | — | S1 eklemi >= 120 iken S2 eklemi <= 117 (aci servo cercevesinde: S1 >= 165, S2 <= 117) kirpilir | kod/ortak/eklem_sinirlari.json bagimli; firmware 0.5.0'da yok | **TASLAK** |
| `sonar_dur_cm` | 30 | on sonarlardan biri bu mesafenin altindaysa ileri hiz 0'a indirilir (fren sinirli); geri ve yerinde donus serbest | yazilim-plani.md Y3 kabul testi '30 cm'de engel olunca duruyor' | **TASLAK** |
| `sonar_yavas_cm` | 60 | bu mesafeden 30 cm'ye dek ileri hiz siniri dogrusal azalir | TASLAK (plan belirtmiyor; plan Y3 'sonarla yavaslama ve durma' der, mesafe yok) | **TASLAK** |
| `sonar_yavas_en_az_m_s` | 0.05 | yavaslama bolgesinde ileri hiz siniri bunun altina inmez (robot 30 cm'ye gercekten varip durur; yoksa esige asimptotik yaklasir) | TASLAK (plan belirtmiyor) | **TASLAK** |
| `sonar_histerezis_cm` | 5 | engel 30 cm altinda baslar, 30 + 5 cm ve ustunde kalkar | TASLAK (plan belirtmiyor) | **TASLAK** |
| `sonar_yankisiz` | — | menzil disi / yanki yok (null) engel sayilmaz | TASLAK (plan belirtmiyor). Bilinen risk: egik yuzey yanki vermez | **TASLAK** |

İvme sınırları (`eklem_sinirlari.json` `teker.ivme_sinir_m_s2`, m/s²): düz sürüş 0.5, düz fren 1.8, rampa sürüş 0.1, rampa fren 0.1. Bekçi ve güç bırakma **ani** durdurur (0.5.0), `dur` fren sınırıyla.

## 4. Güç durumları, arıza nedenleri, genel hatalar

Durumlar: `birakik`, `onsarj`, `devrede`, `ariza`. birakik: roleler birakik (acilis, birak). onsarj: arm sirasi. devrede: sur kabul edilir. ariza: bir koruma birakti, KILITLI; yalniz yeni arm cozer, birak cozmez. (Kaynak: main guc.h; yazilim-plani.md 'ESP32 reseti = guc kapali', E3 kilit.)

Arıza nedenleri (`guc` olayı `neden`, ping `ariza`): `acil_stop`, `bara_yok`, `bara_gitti`, `is_sol`, `is_sag`, `i2c`, `sessizlik`, `onsarj_sure`.

| Genel hata | Ne |
| --- | --- |
| `json_bozuk` | satir JSON degil (cevapta k yok) |
| `k_yok` | JSON'da 'k' alani yok (cevapta k yok) |
| `bilinmeyen_komut` | k bilinen komutlardan biri degil (cevapta k = gelen ad) |
| `satir_cok_uzun` | satir 200 bayti asti (cevapta k yok) |

Bozuk satir, bilinmeyen komut ve uzun satir bekciyi ve sessizlik sayacini BESLEMEZ.

## 5. Komutlar (Pi → ESP32)

Her komut tek satır: `{"k":"<ad>", ...}`. Her komuta bir cevap gelir: `{"ok":true,"k":"<ad>",...}` ya da `{"ok":false,"k":"<ad>","hata":"..."}`.

| Komut | Alanlar | Cevaptaki ek alanlar | Hatalar | Ne | Kaynak | İşaret |
| --- | --- | --- | --- | --- | --- | --- |
| `arm` | — | `guc` metin | `acil_stop`, `pca9685_yok`, `zaten_devrede`, `mesgul`, `zamanlayici_yok` | Gucu devreye al (E3 + E9 dizisi: K2 -> 500 ms -> bara? -> K1 -> 100 ms -> K2 birak -> bara?). Hemen cevap; sonuc 'guc' olayiyla gelir. Yalniz operator istegiyle gonderilir. | main seri_protokol.h; yazilim-plani.md 'devreye al' (plan taslaginda {"t":"arm"}); pin-haritasi.md Y4 | 0.5.0 |
| `birak` | — | `ms` tamsayi | — | Gucu birak; her durumda kabul. Arizadaysa ariza (kilit) kalir. | main seri_protokol.h; pin-haritasi.md Y5 | 0.5.0 |
| `reset` | — | — | — | Once birak, cevap, sonra ESP32 yeniden baslar; ardindan 'hazir' (guc birakik). | main seri_protokol.h | 0.5.0 |
| `sur` | `v` sayi, `w` sayi, `rampa` bool (isteğe bağlı) | `rampa` bool (yalniz istekte rampa varsa) | `devrede_degil`, `v_w_sayi_olmali`, `rampa_bool_olmali` | Surus hedefi. Guc devrede degilse reddedilir (bekci beslenmez). Kabul edilen her sur bekciyi besler. | main seri_protokol.h (plan taslaginda {"t":"drv","v","w"}) | 0.5.0 |
| `dur` | — | — | — | Motorlari fren siniriyla durdur (duz 1,8 / rampa 0,1 m/s2), jesti kes. Gucu birakmaz. Bekciyi beslemez. | main seri_protokol.h | 0.5.0 |
| `rampa` | `ac` bool | `rampa` bool, `elle` bool, `imu` bool | `ac_bool_olmali` | Elle rampa kipi: ivme ve fren 0,1 m/s2, kollar ev pozunda, 'bosta' disi jest ve elle servo reddedilir. | main seri_protokol.h RAMPA KIPI; yazilim-plani.md Y1 (karar 29.10) | 0.5.0 |
| `servo` | `kanal` tamsayi\|metin, `aci` sayi | `kanal` metin (servo adi), `aci` sayi (uygulanan) | `rampa_modunda`, `kanal_yok`, `bilinmeyen_kanal`, `aci_sayi_olmali`, `pca9685_yok` | Tek servoyu elle. kanal 0-15 ya da servo adi; aci servo cercevesinde derece (0-180), sinira kirpilir. | main seri_protokol.h; yazilim-plani.md Y2 (plan taslaginda {"t":"jnt","q":{...},"ms"}) | 0.5.0 |
| `jest` | `ad` metin, `yon` metin (isteğe bağlı) | `ad` metin, `yon` metin, `yon_uygulandi` bool | `ad_yok`, `rampa_modunda`, `yon_gecersiz`, `pca9685_yok`, `bilinmeyen_jest` | Kayitli jesti oynat. yon istege bagli (sol\|sag\|ileri\|arka). | main seri_protokol.h | 0.5.0 |
| `ping` | — | `surum` metin, `ms` tamsayi, `pca9685` bool, `odo` bool, `rampa` bool, `guc` metin, `acil` bool, `bara` bool, `aku` sayi\|null, `ariza` metin\|null, `jestler` liste, `yetenekler` liste (TASLAK), `sonar` nesne (TASLAK), `engel` bool (TASLAK) | — | Canli misin + durum ozeti. Kalp atisi: Pi devredeyken ~1 s'de bir. Sessizlik sayacini besler, bekciyi beslemez. | main seri_protokol.h (plan taslaginda {"t":"hb"} 5 Hz) | 0.5.0 |
| `odo_sifirla` | — | — | — | Iki enkoder tik toplamini sifirla. | main seri_protokol.h | 0.5.0 |

## 6. Mesajlar (ESP32 → Pi)

| Mesaj | Alanlar | Örnek | Ne | Kaynak | İşaret |
| --- | --- | --- | --- | --- | --- |
| `cevap` | `ok` bool, `k` metin (cogu zaman), `hata` metin (ok=false) | `{"ok":true,"k":"sur"}  {"ok":false,"k":"sur","hata":"devrede_degil"}` | Her komuta bir cevap. ok=false ise hata alani var. Genel hatalarda k olmayabilir. | main seri_protokol.h | 0.5.0 |
| `hazir` | `k` metin, `surum` metin, `pca9685` bool, `guc` metin, `yetenekler` liste (TASLAK) | `{"k":"hazir","surum":"0.5.0","pca9685":true,"guc":"birakik"}` | Acilista bir kez (reset sonrasi da). Guc her zaman birakik; kendiliginden arm OLMAZ. | main seri_protokol.cpp seri_baslat; plan 'ev reset' yerine | 0.5.0 |
| `guc` | `k` metin, `guc` metin, `neden` metin\|null, `ms` tamsayi | `{"k":"guc","guc":"ariza","neden":"acil_stop","ms":12345}` | Guc durumu her degistiginde (komut cevabindan SONRA). neden yalniz ariza'da. | main seri_protokol.h GUC OLAYI (plan taslaginda {"t":"ev","k":"estop"}) | 0.5.0 |
| `odo` | `k` metin, `sol` tamsayi, `sag` tamsayi, `yaw` sayi\|null, `ms` tamsayi | `{"k":"odo","sol":1234,"sag":-56,"yaw":null,"ms":104200}` | 10 Hz odometri: toplam enkoder tiki (robotun kendi solu / sagi), yaw (IMU yoksa null). Cevap degildir. | main seri_protokol.h ODOMETRI | 0.5.0 |
| `durum` | `k` metin, `jest` metin\|null, `sur` liste, `wd` bool, `rampa` bool, `guc` metin, `acil` bool, `bara` bool, `aku` sayi\|null, `ariza` metin\|null | `{"k":"durum","jest":null,"sur":[0.2,0.0],"wd":false,"rampa":false,"guc":"devrede",...}` | Istege bagli 1 s yayin (firmware'de DURUM_YAYINI=1 ile; sahte kartta kapali). | main seri_protokol.h | 0.5.0 |
| `sonar` | `k` metin, `sol` sayi\|null, `orta` sayi\|null, `sag` sayi\|null, `ms` tamsayi | `{"k":"sonar","sol":82.4,"orta":120.0,"sag":null,"ms":104200}` | 10 Hz uc on sonar, cm (robotun KENDI solu / orta / sagi). null = menzil disi ya da yanki yok. Firmware eslemesi (K65): pin haritasi SONAR_SAG_ECHO (GPIO39, onden bakanin sagi) = robotun kendi solu = 'sol'; SONAR_SOL_ECHO (GPIO35) = 'sag'. | TASLAK (plan 'st' mesajinda "son":[80,120,95]; 0.5.0'da sonar surucusu yok) | **TASLAK** |
| `engel` | `k` metin, `var` bool, `sensor` metin\|null, `cm` sayi\|null, `ms` tamsayi | `{"k":"engel","var":true,"sensor":"orta","cm":29.6,"ms":104200}` | Sonar engel kurali durum degistirince: var=true ileri hiz kesildi, var=false kalkti. | TASLAK (plan taslaginda {"t":"ev","k":"engel"}) | **TASLAK** |

Yetenekler (TASLAK; `hazir` ve `ping` cevabında `yetenekler` listesi; 0.5.0'da alan yok = hiçbiri): `sonar` sonar telemetrisi + 30 cm durma (guvenlik.sonar_*); `bagimli_sinir` servo bagimli siniri (sinirlar.servo_bagimli).

## 7. Servolar

Kanal sirasi = PCA9685 cikisi. aci = eklem acisi + ofset (servo cercevesi 0-180). Sinirlar eklem_sinirlari.json'dan + ofset ile hesaplanir (elle yazilmaz). Adlar robotun kendi cercevesi (main yazilimi); K65 donanim adlari ters taraftir. Kaynak: main kod/esp32/src/jest_verisi.h SERVO_TABLOSU (ofset ve hiz), kod/ortak/eklem_sinirlari.json (sinir), pin-haritasi.md § 9 pca9685_kanallar.

| Kanal | Ad | Eklem | Ofset | En az | En çok | Hız (°/s) | Ev |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | `sag_omuz` | `r_s1` | +45 | 0 | 180 | 85 | 45 |
| 1 | `sag_omuz_yan` | `r_s2` | +0 | 5 | 120 | 85 | 5 |
| 2 | `sag_dirsek` | `r_dirsek` | +0 | 0 | 105 | 120 | 0 |
| 3 | `sag_bilek` | `r_bilek` | +90 | 0 | 180 | 120 | 90 |
| 4 | `kafa_pan` | `pan` | +90 | 0 | 180 | 90 | 90 |
| 5 | `sol_omuz` | `l_s1` | +45 | 0 | 180 | 85 | 45 |
| 6 | `sol_omuz_yan` | `l_s2` | +0 | 5 | 120 | 85 | 5 |
| 7 | `sol_dirsek` | `l_dirsek` | +0 | 0 | 105 | 120 | 0 |
| 8 | `sol_bilek` | `l_bilek` | +90 | 0 | 180 | 120 | 90 |
| 9 | `kafa_tilt` | `tilt` | +90 | 77 | 103 | 60 | 90 |

Kanal 10 / 11 / 12 sonar tetiği, 13–15 yedek (`pin-haritasi.md` § 9): `servo` komutunda `bilinmeyen_kanal`.

- **TASLAK** bağımlı sınır: `sag_omuz` ≥ 165 iken `sag_omuz_yan` ≤ 117 (servo çerçevesi; `eklem_sinirlari.json` `bagimli`).
- **TASLAK** bağımlı sınır: `sol_omuz` ≥ 165 iken `sol_omuz_yan` ≤ 117 (servo çerçevesi; `eklem_sinirlari.json` `bagimli`).

Jestler: `bosta`, `evet`, `isaret`, `selam`; yönlü: isaret (sol/sag/ileri/arka). Kaynak: main kod/esp32/src/jest_verisi.h JEST_TABLOSU.

## 8. Eskimiş taslak (`yazilim-plani.md` "Seri protokol (ilk taslak)")

yazilim-plani.md '### Seri protokol (ilk taslak)' tablosu (11.10) firmware 0.5.0'dan once yazildi ve guncellenmedi. Karsiligi:

| Plan taslağı | Bu protokol |
| --- | --- |
| `{"t":"drv","v","w"}` | {"k":"sur","v","w"} |
| `{"t":"jnt","q":{...},"ms"}` | {"k":"servo","kanal","aci"} (tek servo; varis suresi yok, hiz servo tablosundan) ya da {"k":"jest"} |
| `{"t":"hb"} 5 Hz` | {"k":"ping"} ~1 Hz (bekciyi 'sur' besler) |
| `{"t":"st",...} 20 Hz` | {"k":"odo"} 10 Hz + ping cevabi + (TASLAK) {"k":"sonar"} 10 Hz |
| `{"t":"ev","k":"estop"\|"reset"}` | {"k":"guc","guc":"ariza","neden":"acil_stop"} / {"k":"hazir"} |
| `{"t":"ev","k":"engel"}` | (TASLAK) {"k":"engel"} |
| `{"t":"arm"}` | {"k":"arm"} |

## 9. TASLAK öğelerin listesi (onay bekler)

- `zamanlar_ms.sonar_aralik`: {"k":"sonar"} yayini (10 Hz)
- `sinirlar.servo_bagimli`: S1 eklemi >= 120 iken S2 eklemi <= 117 (aci servo cercevesinde: S1 >= 165, S2 <= 117) kirpilir
- `guvenlik.sonar_dur_cm`: on sonarlardan biri bu mesafenin altindaysa ileri hiz 0'a indirilir (fren sinirli); geri ve yerinde donus serbest
- `guvenlik.sonar_yavas_cm`: bu mesafeden 30 cm'ye dek ileri hiz siniri dogrusal azalir
- `guvenlik.sonar_yavas_en_az_m_s`: yavaslama bolgesinde ileri hiz siniri bunun altina inmez (robot 30 cm'ye gercekten varip durur; yoksa esige asimptotik yaklasir)
- `guvenlik.sonar_histerezis_cm`: engel 30 cm altinda baslar, 30 + 5 cm ve ustunde kalkar
- `guvenlik.sonar_yankisiz`: menzil disi / yanki yok (null) engel sayilmaz
- `mesajlar.sonar`: 10 Hz uc on sonar, cm (robotun KENDI solu / orta / sagi). null = menzil disi ya da yanki yok. Firmware eslemesi (K65): pin haritasi SONAR_SAG_ECHO (GPIO39, onden bakanin sagi) = robotun kendi solu = 'sol'; SONAR_SOL_ECHO (GPIO35) = 'sag'.
- `mesajlar.engel`: Sonar engel kurali durum degistirince: var=true ileri hiz kesildi, var=false kalkti.
- `yetenekler.sonar`: sonar telemetrisi + 30 cm durma (guvenlik.sonar_*)
- `yetenekler.bagimli_sinir`: servo bagimli siniri (sinirlar.servo_bagimli)
