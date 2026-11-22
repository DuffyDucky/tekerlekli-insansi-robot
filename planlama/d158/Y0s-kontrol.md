# Y0s bağımsız kontrol (B ajanı)

Kontrol 22.11.2026 19:00–19:37. Dal `lale-duzeltme`, HEAD `fb8a3f1`. `git fetch` sonrası `origin/main` = `71cf76d` =
`git ls-remote origin main` (güncel). Firmware sürümü `seri_protokol.cpp` `FIRMWARE_SURUM "0.5.0"` (doğrulandı).
`origin/main` çalışma ağacına alınmadı: yalnız `git show` / `git ls-tree`. Paket dosyalarında kalıcı değişiklik yok (bozmalar geri
alındı, md5 aşağıda). Geçici çıktılar: `%TEMP%\claude\...\scratchpad\y0s-b\` (bozma betiği `bozma.py`, `bozma-sonuc.json`,
`tcp-tam.txt`, `bellek-1..3.txt`).

## Hüküm: KOŞULLU GEÇER

Protokol firmware 0.5.0'ı komut, alan, hata kodu ve güç durum makinesi düzeyinde doğru aktarıyor; testler gerçekten koşuyor,
belirlenimci ve TCP'de de tam geçiyor. Koşullar (commit öncesi):

1. **K1 (engelleyici, özel veri):** `planlama/d158/Y0s-olcum/bozma-bekci.txt`, `bozma-sonar.txt`, `hedef-tcp-ilk.txt` yerel kullanıcı
   yolunu içeriyor (kullanıcı klasöründen başlayan mutlak yol, 8 satır; A düzeltme turunda göreli yapıldı). Ya yol kısaltılıp yeniden yazılmalı ya bu üç dosya commit dışı
   kalmalı. (Ayrıca cp1254 bozuk karakterle yazılmışlar.)
2. Aşağıdaki "model yanlış" farkları (F1, F2) ve test boşlukları ya düzeltilmeli ya günlükte bilinen eksik olarak yazılmalı.

## 1. Protokol ↔ firmware 0.5.0 fark tablosu

Okunan: `seri_protokol.cpp/.h`, `guc.cpp/.h`, `watchdog.cpp`, `main.cpp`, `motorlar.cpp/.h`, `servolar.cpp`, `jestler.cpp`,
`jest_verisi.h` (SERVO_TABLOSU, JEST_TABLOSU), `sinirlar_verisi.h`, `include/pinler.h`, `OKU_BENI.md`, `kod/robot/seri.py`,
`kod/ayarlar.yaml` (hepsi `origin/main`). Karşılaştırılan: `protokol.json`, `cekirdek.py`, `lale_protokol.py`.

**Aynı bulunanlar (alan alan):** komut adı `k`; 10 komut; satır ≤ 200 bayt (`satir_boy < 200` → 200 kabul, 201 `satir_cok_uzun`, k'siz);
`\r` atılır, boş satır sessiz; `json_bozuk` / `k_yok` k'siz, `bilinmeyen_komut` k'li; `k` sayıysa `k_yok`; sessizlik sayacı yalnız
bilinen komutla (geçersiz `sur` da besler), bekçi yalnız kabul edilen `sur` ile; bekçi açılışta tetikli, tetiklenince rampasız
durdurur, K1'e dokunmaz; `sur` sırası devrede → v/w sayı (sonlu; bool değil) → rampa bool; `dur` fren sınırlı, jesti keser, bekçiyi
beslemez; `servo` sırası rampa → kanal (int/ad; 10–12 sonar kanalı `bilinmeyen_kanal`) → aci → pca; servo min/max ve hızları
`jest_verisi.h` ile aynı (elle karşılaştırdım: 0–180, 5–120, 0–105, 77–103; 85/120/90/60 °/s; ev pozları); `jest` sırası ad → rampa
(`bosta` serbest) → yon (null = yok) → pca → bilinmeyen; `yon_uygulandi` yalnız `isaret` için true (firmware'de `isaret` dört yön
varyantına sahip, diğerleri yok); `rampa` cevabı `rampa/elle/imu`; `arm` hata sırası `zaten_devrede` → `mesgul` → `acil_stop` →
`pca9685_yok`; arm arızayı temizler; `birak` arızada durumu değiştirmez; güç olayı cevaptan sonra, koruma bırakmasında hemen;
`neden` yalnız arızada; ön şarj 500 → K1 → 100 → K2 bırak → bara teyidi; K2 en çok 1000 ms; sessizlik 5000 ms devreye girişten;
reset: bırak → `ok` → olay → yeniden başla → `hazir` (birakik, millis 0, odo 0, elle rampa kapalı); odo 100 ms, alanlar
`sol/sag/yaw/ms`, IMU yok → `yaw null`; ping alanları; ivme 0,5 / 1,8 / 0,1 / 0,1; v, w ±1'e kırpılır, teker 0,39'a orantılı küçültülür;
enkoder 1980 tik/tur, teker 0,125 m.

| # | Fark | Firmware 0.5.0 | Model | Sınıf |
| --- | --- | --- | --- | --- |
| F1 | Teker izi (v,w → teker hızı) | `motorlar.cpp` `IZ_GENISLIGI_M = 0.426` (Pi `kod/ayarlar.yaml` `konum.odometri.iz_genislik_m: 0.426` de aynı) | `cekirdek.py:539-540` 0,432 (CAD) hem komut dönüşümünde hem fizikte | **model yanlış** (komut dönüşümü firmware sabitini kullanmalı; fizik 0,432 savunulabilir). Ç3'te kayıtlı ama `ayarlar.yaml` kaynağı kaçmış |
| F2 | Ana anahtar kapalıyken `aku` | `guc.cpp aku_olc`: < 1 V → `null` ("ana anahtar kapalı") | `cekirdek.py:511` her zaman 13,1 | **model yanlış** (küçük) |
| F3 | BTS IS arızası `is_sol/is_sag` | `devrede_denetle` | yok, ortamda tetiği de yok | model eksik (SIMULASYON.md "modellenmeyenler"de yazılı) |
| F4 | Jest kareleri | servo hedefleri karelerle oynar, bitince ev pozu | jest yalnız 2 s "aktif" (TAHMİN), servo hedefi değişmez | bilinçli basitleştirme (belgede yazılı) |
| F5 | Motor döngüsü | 50 Hz (20 ms) | 100 Hz (10 ms) | bilinçli (Ç7); ivme oranı aynı |
| F6 | Acil/bara giriş süzgeci | 3 × 2 ms ≈ 6 ms | anında (10 ms dilim) | ihmal edilebilir |
| F7 | `surum` | `"0.5.0"` | `"0.5.0+y0s.1"` | bilinçli |
| F8 | `hazir`/`ping` `yetenekler`, `sonar`, `engel`; `sonar` / `engel` mesajları; 30/60 cm; 0,05 m/s; 5 cm histerezis; bağımlı servo sınırı | yok (`OKU_BENI.md`: sonar sürücüsü yok, trig PCA9685 10–12) | var | bilinçli TASLAK uzantı (protokol.json `taslak: true`). Firmware'le uyuşabilir: sonar pinleri/trig kanalları ayrılmış, sürücü "kapsam dışı" |
| F9 | Bağımlı sınır davranışı | — | S1 ≥ 165 iken S2 hedefi 117'ye kırpılır, S1 komutu S2'yi sessizce indirir | TASLAK; plan Y2 "yasak bölge **reddediliyor**" der, model kırpıyor: ayrı karar gerek |
| F10 | JSON ayrıştırıcı hoşgörüsü | ArduinoJson ilk değerden sonra gelen fazlalığı yok sayar (ör. `{"k":"ping"}xyz`), tek tırnak kabul edebilir, NaN ayarı derleme seçeneğine bağlı | Python `json.loads`: fazlalık / tek tırnak `json_bozuk` | **firmware belirsiz** (kartta denenmeli; `test_nan_reddedilir` bunu zaten iki sonuçla kabul ediyor) |
| F11 | Yinelenen anahtar, geçersiz UTF-8 | ArduinoJson: ilk anahtar? UTF-8 denetlemez | Python: son anahtar; geçersiz UTF-8 `json_bozuk` | firmware belirsiz |
| F12 | Çok büyük tamsayı kanal (ör. 1e10 tamsayı) | `is<int>()` false → `kanal_yok` | tamsayı → `bilinmeyen_kanal` | firmware belirsiz, önemsiz |

`seri.py` (Pi) ile çelişki yok: `guc` olayı `ok`'suz, `hazir` sonrası elle rampa sıfır, `CANLI_GUC` onsarj+devrede; Pi'nin kendi
hız sınırı `EN_FAZLA_V 0.5`, `EN_FAZLA_W 1.0` (`lale_pi` istemcisi bunu uygulamaz; protokol sınırı değil, Pi politikası).

## 2. Testler

### Koşular (benim)

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `py -3 kod\testler\kos.py` (1) | 0 | 44/44, 6,8 s |
| `py -3 kod\testler\kos.py` (2) | 0 | 44/44, 6,8 s |
| `py -3 kod\testler\kos.py` (3) | 0 | 44/44, 6,4 s |
| `LALE_HEDEF=tcp py -3 kod\testler\kos.py -v` | 0 | **44/44, kalan 0, atlanan 0, 115,5 s** (A'nın tekrarlamadığı tam koşu) |

Sanal saat ile gerçek zaman arasında davranış farkı görülmedi; tcp'de yalnız tolerans 80 ms (`duzenek.py:128`). Not:
`tcp_sunucu.py:129` 200 ms'den fazla geride kalınca dilim atar (sanal saat yavaşlar; `gecikme_sayisi` yalnız bilgi).

### Testler yalnız protokolden mi konuşuyor

Komutlar ve cevaplar evet (`Esp32Istemci`, her gelen mesaj şemaya denetleniyor, `tearDown` şema hatasını yakalıyor). Ama
`test_guvenlik.py`'deki 27 testin **14'ü** kilit iddiasını `hakem()` ile (çekirdeğin `rampa_hiz`, `guc`, `servo` durumu) doğruluyor
(`hakem()` 20 kez). `hakem()` gerçek kartta `skipTest` attığı için bu 14 test gerçek kartta **tümüyle "atlandı"** olur; ör.
`test_500ms_sur_gelmezse_durur` hakemi ilk satırlarda çağırdığından içindeki protokol (odo) kontrolüne hiç varılmaz. Ayrıca
`test_kablo_cekilince_durur_ve_kilitlenir` (`test_guvenlik.py:283`) `hakem()["guc"]` ile kartın iç güç durumunu okuyor (fiziksel
değil). Bu, "aynı testler gerçek karta koşar" iddiasını zayıflatır; bellek ve tcp'de sorun değil.

### Dayanak satırları

27 güvenlik + 7 kaynak testinin dayanaklarının hepsine baktım; alıntılanan ifadeler dosyalarda var:
`yazilim-plani.md` 17 ("her komutta tekrar kontrol eder"), 27 ("satır başına bir JSON"), 29 ("100 Hz döngü"), 32 ("3 × HC-SR04"),
35 ("500 ms Pi'den mesaj gelmezse teker DUR"), 50 ("Donanımdan gelen kurallar"), 55 ("ESP32 reseti = güç kapalı"), 60 (yay
çizerek dönüş), 61–62 (0,5 / 0,1 m/s²), 67–68 (tek kaynak, "elle iki yerde yazılmaz"), 75 (Y1 "kablo çekilince 500 ms içinde
duruyor", "ivme rampası"), 76 (Y2 "Sınır dışı komut kırpılıyor, yasak bölge reddediliyor"), 77 (Y3 "sonarla yavaşlama ve durma",
"30 cm'de engel olunca duruyor"); `pin-haritasi.md` 262 (Y4), 266–267 (Y5); `elektrik.md` 246 (E3), 258 ("PC817 #2 500 ms içinde
LOW olmazsa hata"); `eklem_sinirlari.json` `bagimli` ("S1 >= 120 iken S2 <= 117"), tilt 77–103; firmware dayanakları
(`guc.h SESSIZLIK_BIRAK_MS`, `watchdog.cpp`, `seri_protokol.cpp sayi_al`) da yerinde. Küçük kayma: `test_acilis_ve_reset_guc_kapali`
"ESP32 reseti = güç kapalı" satırına dayanıyor, o satır eski `ev reset` olayını anlatıyor (Ç5'te kayıtlı).

### Bozma deneyleri

Betik: dosyayı yedekle → metin değiştir → `kos.py` → eski baytları geri yaz → md5 karşılaştır. Hepsinde "geri alındı = True"
(md5 önce = sonra). Son durum: `protokol.json` FD60697A2C867D41243799DA0314E7A8, `cekirdek.py` B11AD942BB5F86F91E3BAAF304FD3BF7
(koşu öncesiyle aynı), `git status` 61 satır, değişmedi.

| Bozma | Çıkış | Kalan test |
| --- | --- | --- |
| B1 bekçi 500 → 1500 (`protokol.json`) | 1 | 7: Bekci×2, BaglantiKopmasi, BozukMesaj.bekci, TcpDuman.soket + kaynak testleri plan_degerleri, belge_guncel. (A `cekirdek.py`'de bozdu: 5; ikisi tutarlı) |
| B2 sonar 30 → 20 cm (`protokol.json`) | 1 | 4: SonarDurma.30cm, SonarDurma.engelde_geri + plan_degerleri, belge_guncel (A: 1; yer farkı) |
| B3 `birak` arıza kilidini çözer | 1 | 1: AcilStop.kilitler |
| B4 mantar basılıyken `arm` kabul | 1 | 1: AcilStop.kilitler |
| B5 sessizlik 5000 → 8000 | 1 | 5: Sessizlik.5s, BozukMesaj.bekci, BaglantiKopmasi + 2 kaynak |
| B6 servo sınıra kırpılmaz | 1 | 1 (8 alt test): SinirDisiServo.kirpilir |
| B7 bozuk JSON'a `{"ok":true,"k":"ping"}` | 1 | 3: BozukMesaj.dogru_hata, nan, TcpDuman.bozuk |
| B8 `ping` bekçiyi besler | 1 | 1: Bekci.ping_bekciyi_beslemez |
| B9 bekçi fren sınırlı (rampalı) durdurur | 1 | 3: Bekci.500ms, BaglantiKopmasi, TcpDuman.soket |
| B17 kabul edilen `sur` bekçiyi kurmaz | 1 | 5 |
| **B10** 200 baytlık satır reddedilir (`>` → `>=`) | **0** | **yakalanmadı** (200 sınırında test yok) |
| **B11** güç olayı `arm` cevabından ÖNCE | **0** | **yakalanmadı** (cevap/olay sırası sınanmıyor; sözleşme "olay cevaptan SONRA") |
| **B12** I2C koruması (3 × cevapsız → `i2c`) yok | **0** | **yakalanmadı** (ortamda `i2c_kopar` yok, `i2c_saglam` hiç bozulmuyor) |
| **B13** devredeyken `bara_gitti` koruması yok | **0** | **yakalanmadı** (devredeyken ana anahtar kesilmiyor) |
| **B14** sonar histerezis 5 → 0 | 1 | yalnız `belge_guncel` (davranış testi yakalamadı) |
| **B15** `odo_sifirla` tikleri sıfırlamaz | **0** | **yakalanmadı** |
| **B16** reset sonrası `ms` (millis) sıfırlanmaz | **0** | **yakalanmadı** |
| **B18** `yon_uygulandi` hep true | **0** | **yakalanmadı** |

Test boşlukları: 200 bayt sınırı, olay/cevap sırası, `i2c` ve `bara_gitti` (devrede) arızaları, histerezis davranışı, `odo_sifirla`,
reset sonrası saat/sayaçların sıfırlanması, `yon_uygulandi`. Ayrıca `is_sol/is_sag` modellenmediği için sınanamıyor.

## 3. Kod incelemesi (önem sırasıyla)

1. **Orta, `gorunum.py:75-89`:** Pilot döngüsü yalnız `OSError` yakalar. `/surus`'a sonlu olmayan hız gelirse (`{"v":1e400}` →
   `inf`) `esp.gonder` `ProtokolHatasi` atar, **pilot iş parçacığı ölür**; görünüm donar, kalp atışı kesilir, robot 5 s sonra
   `sessizlik` arızasına düşer. Tarayıcıda denendi, sunucu çıktısında `ProtokolHatasi: sur.v türü sayi değil: inf` izi. (`NaN`
   denendi: `abs(nan) > 1e-6` yanlış olduğundan sessizce 0 sayılıyor, çökmüyor.) Sayfanın kendi tuşları bunu üretmez; yerel POST gerekir.
2. **Düşük, `gorunum.py:145-159`:** HTTP uçları kaynak (Origin) denetlemiyor; `127.0.0.1`'e bağlı olsa da tarayıcıda açık başka bir
   site `/komut` (`arm`) ve `/surus`'a POST atabilir (CSRF). Sahte robot için etkisi yok; gerçek Pi'ye taşınırsa önemli.
3. **Düşük, `gorunum.py:52`:** `float(v)` sayı olmayan girdide işleyicide istisna (HTTP 500, yığın izi konsola).
4. **Düşük, mantık / belge tutarsızlığı, `cekirdek.py:552-565` ↔ `638-659`:** histerezis yalnız `engel` mesajında; hız sınırı
   histerezissiz (`d < 30` → 0, `30 ≤ d < 35` → 0,05 m/s). Tarayıcıda gördüm: `engel var=true` iken robot 2,385 → 2,398 m ileri
   süründü, 30 cm altında yine durdu. Tehlikeli değil ama `engel.var=true` "ileri hız kesildi" anlamını taşımıyor.
5. **Düşük, `harita.py:131-138`:** `_parca_kesisir` katı işaret karşılaştırması; eşdoğrusal / değen parçalar kesişim sayılmaz.
   `_icinde` yalnız parçanın ilk ucunu yokluyor. Kayan nokta konumlarında pratikte görülmez; robot bir kutunun tamamen içine
   ışınlanırsa (`konum_ayarla`) çarpışma görülmez. Işın: paralel parça atlanır (doğru), köşede iki parça aynı t verir (zararsız),
   başlangıcı dairenin içindeki ışın uzak yüzü kaçırır (sensör engelin içinde olamaz, zararsız). Birimler tutarlı (m, rad; sonar cm).
6. **Bilgi:** `tcp_sunucu.py` ve `gorunum.py` yalnız `127.0.0.1`'e bağlanıyor (`0.0.0.0` yok); `TcpTasima` varsayılanı `127.0.0.1`.
   Çekirdekte duvar saati, rastgelelik, iş parçacığı yok (`test_harita` belirlenimciliği iki koşu karşılaştırarak sınıyor).
   Sessizce yutulan hata: `tcp_sunucu._yaz` gönderim hatasında istemciyi düşürür (bilinçli, kablo çekilmesi). Yarış: `_oku` istemciyi
   kilitsiz okur, `istemci_kopar` kapatırsa `recv` `OSError` → işlenmiş; sorun görmedim.

## 4. Görünüm (Chrome, kendim)

`kod\simulasyon.bat` = `cd /d %~dp0` + `py -3 araclar\sahte_esp32 %*` + `pause`. Ben `--tarayici-yok --port 5791/5792 --http
8791/8792` ile başlattım, Chrome'da yeni sekmede açtım; sürüş tuşlarını sayfanın `tus` kümesine yazarak (tuş basılı tutma eşdeğeri) yaptım.

- **oda_engelli:** devreye al → ileri: kolona sonar 29,7–30,5 cm'de durdu (hakem ön yüzey 31,7 cm), çarpışma 0. Yerinde sola dönüş
  109°: çarpışma yok. **Geri 12 s: robot güney duvara geri geri çarptı (çarpışma sayısı 0 → 2), uyarı yok.** Arkada sonar yok
  (`robot_parametreleri.json` yalnız üç ön sonar); `protokol.json` `sonar_dur_cm` "geri ve yerinde dönüş serbest" diyor, ama
  `SIMULASYON.md` "Modellenmeyenler"de ve kullanıcı belgesinde **geri giderken korumasız olduğu açıkça yazmıyor**. Acil stop (mantar)
  sürerken: v 0, güç `ariza`; mantar bırakılınca yine `ariza` (kilit); ileri tuşu etkisiz; `arm` sonrası devrede ve sürüldü.
  Histerezis tutarsızlığı (madde 3.4) burada görüldü.
- **oda_bos:** doğu duvarına dik: 29,8 cm'de durdu, çarpışma 0. 22° eğik: 29,8 cm'de durdu (sağ sonar), çarpışma 0. 67° ile duvara
  neredeyse paralel: sağ sonar 29,9 cm'de durdurdu. **Sonra yerinde sağa dönüş: köşe doğu duvarına çarptı (çarpışma 1)**:
  engel varken yerinde dönüş serbest ve taban köşesi (yarıçap ≈ 0,37 m) 30 cm'den büyük. Ekran görüntüsü yerel geçici dizinde.
  Dikdörtgen odada yankı vermeyen (> 60°) eğik yaklaşmayı canlı kuramadım; bu durum `test_egik_yuzey_yanki_vermez` ile sınanıyor.
- Konsol: sayfa ayaktayken hata yok. Sunucu kapanınca sayfa her 100 ms'de `Failed to fetch` uyarısı basıyor ve ekranda "bağlantı
  yok" göstergesi yok (eski durum donuk kalıyor) — küçük kullanılabilirlik eksiği.
- Kapatma: sekme kapatıldı; `sahte_esp32` süreçleri durduruldu (kalan süreç 0, 5791/5792/8791/8792/5760/8765'te dinleyen yok).

## 5. Dürüstlük, belge, parametreler

`SIMULASYON.md` § "Dürüst sınır" ve `PROTOKOL.md` "Dürüstlük notu" C++ kodunun sınanmadığını açıkça söylüyor; TASLAK işareti her
öğede (`test_her_oge_kaynakli_ve_isaretli`). TAHMİN değerleri: enkoder 1980 ve 0,39 m/s firmware sabitleriyle aynı (firmware'de
de "ÖLÇ"); sonar ±15°, 2–400 cm HC-SR04 için olağan; akü 13,1 V, bara 150 ms, açılış 300 ms modelleme seçimi olarak makul.
Kaçan kaynak: `origin/main` `kod/ayarlar.yaml` `konum.odometri` (`tik_tur: 1980`, `teker_cap_m: 0.125`, `iz_genislik_m: 0.426`) —
Pi odometrisi 0,426 kullanıyor, sahte fizik 0,432: sahte kartla Pi odometrisi koşulursa yön %1,4 kayar (F1). Eksik belge: geri
giderken ve yerinde dönerken çarpışma koruması yok (§ 4).

Ç1–Ç9 doğru. Eklenebilecek: Ç10 = F1'in Pi tarafı (`ayarlar.yaml` 0,426); Ç11 = plan Y2 "yasak bölge reddediliyor" ↔ model kırpıyor (F9).

## 6. Dokunulmazlar

- `md5sum -c planlama/d158/Y0s-olcum/kir-bas.md5`: 21/21 OK (14 M + 7 ??), `git status` başlangıçla aynı.
- İzlenen dosyalarda değişiklik yalnız o 14 eski dosya; `rehber/`, CAD'in geri kalanı, `planlama/` izlenen dosyalar (denetim betikleri
  dahil) değişmemiş. `planlama/` altında A'ya ait yeni dosyalar yalnız `d158/Y0s-gunluk.md` ve `d158/Y0s-olcum/` (+ bu dosya).
- `.gitignore` değişmemiş; `__pycache__/` zaten kapsanıyor (4 klasör var, hepsi `!!` yok sayılan).

## 7. Özel veri ve adlar

- Gizli anahtar, parola, belirteç, e-posta, telefon, adres, kimlik/öğrenci no: yeni dosyalarda yok (desen taraması; `+90` eşleşmeleri
  servo ofseti). Görüntüler (`gorunum-*.jpg`) yalnız simülasyon ekranı.
- **Yerel kullanıcı yolu:** `Y0s-olcum/bozma-bekci.txt` (5 satır), `bozma-sonar.txt` (1), `hedef-tcp-ilk.txt` (2). İzlenen dosyalarda aynı
  yol 3 dosyada zaten var (`tasarim/freecad/...`).
- **Kişi adları (yalnız rapor):** "Efe": `kod/SIMULASYON.md:78`, `kod/ortak/PROTOKOL.md:5,7`, `kod/ortak/protokol.json:6`,
  `kod/ortak/protokol_belge_uret.py:34,40`, `planlama/d158/Y0s-gunluk.md:22,96`. "Ahmet": `kod/SIMULASYON.md:78`, `kod/ortak/PROTOKOL.md:7`,
  `kod/ortak/protokol_belge_uret.py:40`. Takma ad: `planlama/d158/Y0s-gunluk.md:77` (1 yer). İzlenen dosyalarda (`git grep -nIw`): Efe 451 satır /
  114 dosya, Ahmet 981 / 244, takma ad 4 / 2 (firmware başlığında da "JSON'u Ahmet günceller", commit yazarı Ahmet).

## 8. Commit önerisi

Girmeli (28 `kod/` + 2 günlük/kontrol + 8 ölçüm = 38; koşullu 3; toplam yeni 41): `kod/SIMULASYON.md`, `kod/simulasyon.bat`, `kod/ortak/{PROTOKOL.md, lale_protokol.py, protokol.json,
protokol_belge_uret.py, robot_parametreleri.json}`, `kod/araclar/haritalar/*.json` (3), `kod/araclar/sahte_esp32/*` (8, `__pycache__`
hariç), `kod/pi/lale_pi/{__init__,istemci,tasima}.py`, `kod/testler/{__init__,duzenek,kos,test_guvenlik,test_harita,
test_protokol_kaynak,test_tcp_duman}.py`, `planlama/d158/Y0s-gunluk.md`, `planlama/d158/Y0s-kontrol.md`,
`planlama/d158/Y0s-olcum/{git-status-bas.txt, kir-bas.md5, kosu-1..3.txt, test-listesi.txt, gorunum-*.jpg}`.

Koşullu: `Y0s-olcum/bozma-bekci.txt`, `bozma-sonar.txt`, `hedef-tcp-ilk.txt` — yerel yol temizlenmeden girmemeli (K1).

Girmemeli: `__pycache__/` (yok sayılıyor), 14 eski M dosya (`tasarim/freecad/kabuk/gorsel/*.png`, `montaj/yerlesim-kontrol.json`),
7 eski ?? (`geometri*_*.py` ×3, `gez.js`, `uc.js`, `P108d-kontrol-olcum/b2-tarama.nabiz`, `P108d-olcum/ara1.json`).

## 9. Bakılmayanlar

Gerçek ESP32 / derleme (kart yok); `test_harita.py` ve `test_tcp_duman.py` satır satır değil, yalnız iç duruma erişim açısından
(ikisi bilerek çekirdeğe bakıyor; belgede yazılı); `PROTOKOL.md`'nin tamamı (üretici `--denetle` testi geçiyor); `jest_verisi.h`
kare verileri; ArduinoJson 7'nin hoşgörü davranışı (F10, F11) belgeden değil bilgiden — kartta denenmeli; > 60° yankısız eğik
duvara canlı yaklaşma (§ 4); rehber üretim zinciri ve çakışma taraması (brief gereği koşulmadı).

---

## Yeniden kontrol (A'nın düzeltme turu; dar kapsam)

**Hüküm: GEÇER.** Commit'i engelleyen bir şey kalmadı. K1 (yerel yol) kapandı. Satır 15'teki A düzeltmesi
("kullanıcı klasöründen başlayan mutlak yol ...") uygun, bırakıldı.

**Koşular (HEAD `fb8a3f1`, `PYTHONDONTWRITEBYTECODE=1`):** bellek 58/58 9,6 s; `LALE_HAKEM=yok` 58/58 9,1 s, atlanan 0;
TCP tam 58/58 125,2 s; hepsi çıkış 0. Özet satırı 5 bilinen davranış testini ayrıca sayıyor. Kararlılık için `LALE_HAKEM=yok`
ile 12 tam koşu daha yapıldı, 12/12 temiz.

**Bozma (kendi betiğim, her bozmadan sonra özgün bayt geri yazıldı):**
- Hakemli 10 bozma: B3, B8 (eski) ve B10, B11, B12, B13, B14, B15, B16, B18 (yeni). 10/10 yakalandı.
  B14 artık güvenlik testinde (`SonarDurma`) davranıştan da düşüyor.
- Hakemsiz 5 bozma: B1, B9, B12, B13, B16. 5/5 yakalandı.
- Geri alma: her satır "geri alindi True" yazdı. `cekirdek.py` MD5 önce ve sonra `BF8B8661…0329`, `protokol.json`
  MD5 `FD60697A…E7A8`; ikisi de değişmedi.
- Not: hakemsiz ilk B12 koşusunda `test_gorunum.test_yalniz_ayni_koken` de bir kez düştü. Aynı bozma 3 kez, görünüm
  testi 6 kez ve tam takım 12 kez yeniden koşuldu; tekrarlanmadı. Gerçek soket ve zamanlamaya bağlı, ara sıra düşen
  bir test olabilir (aşağıda Y1).

**Teker izi:** iki değer kodda ayrı yerde kullanılıyor.
- `cekirdek.py:542-543` `_teker_hedefleri` → `fw_iz` 0,426 (komut → teker hızı).
- `cekirdek.py:595` `_hareket` → `iz` 0,432 (fiziksel dönüş). `robot_parametreleri.json` iki ayrı anahtar tutuyor.
- Hesap: 360 × (1 − 0,426/0,432) = 5,00°. 358,3 / 363,3 = 0,9862 ≈ 0,426 / 0,432 = 0,9861.
- Test (`test_e`) oranı 3 ondalıkla doğruluyor. Ölçülen fark −5,0° tutarlı.

**`aku` null:** `cekirdek.py:512` ana anahtar kapalıyken `None` dönüyor. `test_sozlesme` bunu protokolden doğruluyor.

**Ç11 (bağımlı servo sınırı): belirsiz, karar ekipte.**
- A'nın okuması savunulabilir. Plan satır 35 ve 67 "kafa-kol yasak bölgesi" diyor, `kafa_kol_yasak.aktif = false`.
- Ancak `planlama/adim2/K2-s1-kontrol.md:266-267` bugünkü `bagimli` kuralını (S1 ≥ 120 → S2 ≤ 117) açıkça
  "yasak kutu" diye kuruyor. Bu yüzden Y2'deki "yasak bölge reddediliyor" ona da okunabilir.
- `SIMULASYON.md`'de açık soru olarak kalması doğru. Sessizce "kırp" diye kapatılmamalı.

**Yeni testler (6 dosya okundu: `test_sozlesme`, `test_tasarim_bulgulari`, `test_gorunum`, `test_guvenlik` hakem
kullanımı, `duzenek` yardımcıları):**
- `test_sozlesme`'nin 7 testi iddiayı protokolden doğruluyor: ms, olay sırası, `aku`, odo tikleri, `yon_uygulandi`.
- Fiziksel adımlar `ortam` üzerinden yapılıyor. Gerçek kartta bu adımlar operatöre düşüyor.
- `test_guvenlik`'te `self.hakem()` 0 kez geçiyor, 14 yerde `hakem_varsa` kullanılıyor. Hakem yalnız ek kontrol.
- `test_tasarim_bulgulari` başlığında "geçmeleri sorunun var olduğunu gösterir" diye açıkça yazıyor.
  - Her assert mesajı "tasarım değişmiş olabilir" diyor.
  - `kos.py` bu testleri ayrı sayıyor.
  - Tasarım düzelince düşecekleri açık.
- `test_gorunum` 13 kötü gövde ve köken kurallarını sınıyor.

**Köken denetimi (canlı, 5793/8793):**
- Sayfa açıldı. `arm` 200, devrede; ileri tuşu 2 s, x 1,500 → 1,955 m. Pilot canlı, hata yok.
- Başka kökenden (`localhost` → `127.0.0.1`) gelen `no-cors` POST'lar `birak` ve `mantar_bas` uygulanmadı:
  durum devrede, mantar basılı değil. CORS'lu POST tarayıcıda engellendi.
- curl ile: `Origin: kotu.example`, `Origin: null`, `Sec-Fetch-Site: cross-site` ve yabancı `Host` hepsi 403 aldı.
- `{"v":1e400}` 400 aldı, pilot yaşıyor.
- Süreçler kapatıldı. Kalan süreç 0, dinleyen port 0.

**Kod (`cekirdek.py`, `harita.py`, `gorunum.py`):** engelleyici yeni kusur yok.
- `_parca_kesisir` artık eşdoğrusal / değen kenarı ε ile sayıyor. `_icinde` iki ucu da sınıyor.
- Pilot döngüsü her istisnada `istek = (0,0)` yapıyor. `surus_dogrula` bool, NaN ve ±inf reddediyor.
- Content-Length 0–4096 dışı 413 dönüyor.

Küçük notlar (engellemez):
- **Y1:** yukarıdaki tek seferlik görünüm testi düşmesi.
- **Y2:** `test_e` 0,426'yı elle yazıyor (`firmware_iz_genisligi_m` okunmalı). Adı "gerçekte 355" diyor, ölçülen 358,3 / 363,3.
- **Y3:** `_icinde` `d == 0` için tam eşitlik kullanıyor (`_EPS` değil). Pratikte kenar kesişimi yakalıyor.

**Özel veri:** `kod/` + `Y0s-gunluk.md` + `Y0s-kontrol.md` + `Y0s-olcum/` altındaki 53 yeni dosya tarandı.
- Kullanıcı yolu, `AppData`, e-posta, anahtar, belirteç ya da parola yok. Tek eşleşme bu dosyanın § 8 cümlesi.
- `duzeltme-*.txt` dosyaları temiz.
- `gorunum-duzeltme.jpg` yalnız sayfa içeriği: sekme, adres çubuğu, yol, isim yok.
- Ad geçişleri önceki gibi (Efe / Ahmet `protokol_belge_uret.py:40`, `Y0s-gunluk.md:126`, takma ad `Y0s-gunluk.md:79`).
  Proje rolü olarak; yeni bir şey yok.

**Commit listesi:**
- Girmeli (53):
  - `kod/` altında 31 dosya: önceki 28 + `test_gorunum.py`, `test_sozlesme.py`, `test_tasarim_bulgulari.py`.
  - `planlama/d158/Y0s-gunluk.md` ve `planlama/d158/Y0s-kontrol.md`.
  - `planlama/d158/Y0s-olcum/` altında 20 dosya: 9 `duzeltme-*` ve `gorunum-duzeltme.jpg` dahil.
- Dışarıda kalmalı:
  - `planlama/d158/P108d-olcum/ara1.json` ve `planlama/d158/P108d-kontrol-olcum/b2-tarama.nabiz` (Y0s'e ait değil).
  - Mevcut 14 `M` dosya.
  - `__pycache__` yok.
- 21 eski dosya: `md5sum -c kir-bas.md5` 21/21 OK.

**Bakılmayanlar:**
- `gorunum.html` diff'i satır satır okunmadı; yalnız canlı davranışı denendi.
- `SIMULASYON.md` tasarım bölümü göz gezdirildi.
- Bozmaların 8 yenisinden 5'i (B10, B11, B14, B15, B18) yalnız hakemli koşuldu.
- Gerçek kart yok.
