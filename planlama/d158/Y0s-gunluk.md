# Y0s günlüğü: sahte ESP32 simülasyonu (protokol tek kaynağı, sahte taban + 2B harita, güvenlik senaryoları) (A ajanı)

Paket: **Y0s** (yazılım planı `planlama/yazilim-plani.md` Y0 "protokol belgesi, Pi ↔ ESP32 alışverişi" paketinin robotsuz
sınama kısmı; Y1 bekçi, Y2 servo sınırı, Y3 güvenlik / sonar kurallarının çalıştırılabilir modeli). Ad bilerek `P<sayı>.<sayı>`
biçiminde değil: `dongu-158.md` CAD / rehber döngüsünün paketi değil, `F9c-dogrula` konu önekini saymaz. Önerilen commit öneki
`Lale Y0s:` (commit ve push C adımında). A başlangıcı 22.11.2026 18:57 (saat okundu). Dal `lale-duzeltme`, HEAD `fb8a3f1`
(yerel = uzak). `git add` / commit / push yapılmadı. CAD, rehber, `planlama/d158/` denetim betikleri, 21 eski kirli dosya kapsam dışı.

Kesilirse devam: bu dosyanın § 10 "Durum" bölümü en son yapılanı ve sıradakini yazar.

## 1. Başlangıç durumu (ölçülen)

| Ne | Değer |
| --- | --- |
| HEAD | `fb8a3f1` (yerel = uzak) |
| Eski kirli dosyalar | 21 (`Y0s-olcum/git-status-bas.txt`: 14 M + 7 ??); md5 `Y0s-olcum/kir-bas.md5` |
| `kod/` (bu dal) | yalnız `kod/ortak/eklem_sinirlari.json` + `eklem_sinirlari_uret.py` |
| Python | 3.14.0 (`python`); `pytest` **yok** → standart `unittest` (sanal ortam açılmadı) |

## 2. Önemli bulgu: `main` dalında gerçek ESP32 firmware'i ve sözleşmesi var

Brief "robotun yazılımı henüz yok" diyor; bu dalda doğru, ama **`origin/main` (71cf76d, 14.11) `kod/esp32/` altında Efe'nin
firmware'ini (sürüm **0.5.0**, pin haritası sürüm 4 için; "derlendi, kartta denenmedi") ve Pi tarafını (`kod/robot/seri.py`)
taşıyor.** Okundu, değiştirilmedi (`git archive origin/main kod` → yalnız geçici klasör). Sözleşme `kod/esp32/src/seri_protokol.h`:

- çerçeve: 115200, satır başına bir JSON, `\n` biter, `\r` atılır, satır ≤ 200 bayt (fazlası `satir_cok_uzun`);
- alan adı **`k`** (planın taslağındaki `t` değil); komutlar `arm`, `birak`, `reset`, `jest`, `sur` (v, w), `dur`, `rampa`, `servo`,
  `ping`, `odo_sifirla`; her komuta `{"ok":true|false,"k":..,"hata":..}`; olaylar `hazir`, `guc`, `odo` (10 Hz), isteğe bağlı `durum`;
- bekçi: 500 ms `sur` gelmezse motorlar **ani** durur (`watchdog.cpp`); devredeyken 5 s hiç geçerli komut yoksa güç bırakılır,
  `ariza` / `sessizlik` (`guc.h`); kalp atışı = `ping` (Pi ~1 s'de bir);
- güç durum makinesi `birakik` / `onsarj` / `devrede` / `ariza`; arıza kilitli, yalnız yeni `arm` çözer; `arm` mantar basılıyken
  `acil_stop` ile reddedilir; ön şarj 500 ms (`kod/ortak/pinler.json` "arm": 300 → 500, kanal mesajı #26 / #28).

`yazilim-plani.md` § "Seri protokol (ilk taslak)" (`t`, `drv`, `jnt`, `hb`, `st`, `ev`) bu firmware'den önce yazılmış ve
güncellenmemiş. **Karar (A, gerekçe):** protokolün tek kaynağı 0.5.0 sözleşmesini aynen alır; planın taslak tablosu "eskimiş taslak"
diye belgelenir. Gerekçe: brief'in amacı "robot gelince aynı testler gerçek ESP32'ye karşı koşsun"; gerçek ESP32'ye yüklenecek kod
0.5.0'dır, `t` şemasını konuşan bir sahte kart gerçek kartla hiç konuşamazdı. Bu planla çelişki sayılabilir; planın kendisi tabloyu
"ilk taslak" diye işaretliyor ve 0.5.0 aynı plandaki kuralları (E3 / E9 dizisi, 500 ms bekçi, DTR/RTS) uyguluyor. Orkestratör / B
bakmalı (§ 9 madde 1).

Plan isteyip 0.5.0'da olmayanlar (sahte kartta **TASLAK** eklenti olarak): sonar telemetrisi ve 30 cm durma (Y3), servo bağımlı sınırı
(S1 ≥ 120° iken S2 ≤ 117°, `eklem_sinirlari.json` `bagimli`). Bunlar protokolde `taslak: true` işaretli; gerçek 0.5.0 kartına karşı
koşulunca ilgili testler "yetenek yok" diye atlanır (başarısız sayılmaz, atlandığı yazılır).

## 3. Plan ve kaynaklar arası çelişki / eksik (düzeltilmedi, yalnız kayıt)

| # | Ne | Kaynaklar | Sahte kartta kullanılan |
| --- | --- | --- | --- |
| Ç1 | Protokol alan adları | `yazilim-plani.md` taslak (`t`) ↔ `main` 0.5.0 (`k`) | 0.5.0 (§ 2) |
| Ç2 | Ön şarj bekleme | `pin-haritasi.md` Y4 "300 ms" ↔ `elektrik.md` E9 "en az 300, boş akü için 500 önerilir", E3 "500 ms içinde" ↔ `main` `pinler.json` 500 | 500 ms |
| Ç3 | Teker izi | README "teker izi 432 mm (x ±216)", `arayuz.py` `_X_WH3` 216 ↔ `main` `motorlar.cpp` `IZ_GENISLIGI_M` 0,426 ("CAD: 2 × 213; ÖLÇ") ve Pi odometrisi `main` `kod/ayarlar.yaml` `konum.odometri.iz_genislik_m` 0,426, `kod/robot/konum/odometri.py` (B'nin bulduğu kaçan kaynak) | **§ 11'den sonra ikisi ayrı:** komut → teker hızı 0,426 (firmware), robotun gerçek dönüşü 0,432 (CAD). Ölçülen etki (`test_tasarim_bulgulari` `test_e`): Pi odometrisi 363,3° dönüş derken gerçek 358,3°, yani 360° başına −5,0° (%1,4; oran 0,426 / 0,432). Komut tarafında `w` = 1 rad/s istenince gerçek 0,986 rad/s. Hangisi doğru: ölçülecek, karar verilmedi |
| Ç10 | Ç3'ün Pi tarafı | Pi odometrisi (`ayarlar.yaml` 0,426) firmware sabitiyle aynı, CAD'den farklı | Ç3 satırında |
| Ç11 | Bağımlı servo sınırı: kırp mı reddet mi | B: plan Y2 "yasak bölge reddediliyor" → reddet. Plan: `yazilim-plani.md` satır 76 Y2 kabul ölçütü "Sınır dışı komut kırpılıyor, yasak bölge reddediliyor"; aynı belgede "yasak bölge" satır 35 ve 67'de **kafa-kol** yasak bölgesi (`eklem_sinirlari.json` `kafa_kol_yasak`, `"aktif": false`); `bagimli` ayrı anahtar | kırpma (TASLAK) kaldı; plan bağımlı sınır için "reddet" demiyor. Yoruma açık, Efe / Ahmet kararı (§ 11 B4) |
| Ç4 | Bekçi tetiği | plan "500 ms Pi'den **mesaj** gelmezse teker DUR" ↔ 0.5.0 "500 ms **sur** gelmezse" (ping bekçiyi beslemez) | 0.5.0 (`sur`) |
| Ç5 | Reset olayı | plan `ev reset` ↔ 0.5.0 açılışta `{"k":"hazir",...,"guc":"birakik"}` | 0.5.0 |
| Ç6 | Yay çizerek dönüş (K1: `w` sınırı hıza bağlı) | plan "Donanımdan gelen kurallar" ↔ 0.5.0'da yok (`w` yalnız ±1'e kırpılır) | modellenmedi (açık) |
| Ç7 | Döngü hızı | plan "100 Hz döngü" ↔ 0.5.0 motor ve servo 50 Hz (`main.cpp` 20 ms) | çekirdek 10 ms adım, rampa gerçek zamanlı (sonuç aynı) |
| Ç8 | Sonar adları | pin haritası `SONAR_SAG_ECHO` (GPIO39) "sağ" = önden bakanın sağı (K65) ↔ yazılım robotun kendi çerçevesi | protokol alanları robotun kendi solu / sağı; eşleme belgede |
| Ç9 | Yavaşlama | plan Y3 "sonarla yavaşlama ve durma", yavaşlama mesafesi yok | TASLAK 60 cm'den doğrusal |

## 4. Yapılanlar (adım adım)

(aşağıda zaman sırasıyla)

1. Tek kaynak: `kod/ortak/protokol.json` (çerçeve, zamanlar, sınırlar, güvenlik, güç durumları, arıza nedenleri, genel hatalar,
   10 komut, 7 mesaj, yetenekler, 10 servo, 4 jest, eskimiş taslak eşlemesi; her öğede `kaynak` ve `taslak`),
   `kod/ortak/robot_parametreleri.json` (her parametrede `durum` kaynakli / TAHMIN ve `kaynak`), okuyucu `kod/ortak/lale_protokol.py`
   (kodla / çöz / komut ve mesaj denetimi; servo sınırları `eklem_sinirlari.json` + ofsetten hesaplanır).
2. Sahte kart `kod/araclar/sahte_esp32/`: `cekirdek.py` (saf, `adim(ms)`), `harita.py` (ışın izleme, çarpışma), `tasima.py`
   (bellek içi), `tcp_sunucu.py` (gerçek zaman + TCP). Haritalar `kod/araclar/haritalar/` (oda_bos, oda_engelli, acik_alan).
3. Pi istemcisi `kod/pi/lale_pi/` (`tasima.py`: arayüz + TcpTasima + SeriTasima yer tutucu; `istemci.py`).
4. Testler `kod/testler/` (`duzenek.py`: hedef seçimi + Ortam + hakem; `test_guvenlik.py`; koşucu `kos.py`). 19:11 ilk tam koşu
   27 / 27 (iki test düzeltmesi: onsarj olayının arm cevabıyla aynı turda gelmesi, rampa ivmesinin geçen süreye göre ölçülmesi).
5. `kod/ortak/protokol_belge_uret.py` → `kod/ortak/PROTOKOL.md` (üretilir; `--denetle` eskiyse çıkış 1). İşaret: "0.5.0" /
   **TASLAK**.
6. `test_protokol_kaynak.py` (7), `test_harita.py` (4; belirlenimcilik dahil), `test_tcp_duman.py` (6; gerçek soket).
   Toplam 44 test. Harita testinde benim beklentim yanlıştı (30° ışın yan duvara çarpar); test düzeltildi, kod değil.
7. Görünüm `kod/araclar/sahte_esp32/gorunum.py` + `gorunum.html` (ThreadingHTTPServer, yoklama 100 ms, dış JS yok), giriş
   `kod/araclar/sahte_esp32/__main__.py`, Ahmet'in tek komutu `kod/simulasyon.bat`. Belge `kod/SIMULASYON.md`.
8. 3 ardışık koşu (`py -3 kod/testler/kos.py`): 44 / 44, çıkış 0, 6,3 / 6,8 / 6,4 s (`Y0s-olcum/kosu-1..3.txt`).
9. Bozma deneyi 1: `cekirdek.py` `self.bekci_ms = z["bekci"] + 1000` → çıkış 1, 5 test kaldı (Bekci ×2, BaglantiKopmasi,
   BozukMesaj, TcpDuman.soket_kapaninca) (`bozma-bekci.txt`). Geri alındı, sha1 yedekle aynı, 44 / 44.
   Bozma deneyi 2: sonar eşiği 30 → 20 cm → yalnız `SonarDurma.test_30cm_esiginde_durur` kaldı (`bozma-sonar.txt`). Geri alındı.
10. `LALE_HEDEF=tcp` (gerçek zaman, 115 s): ilk koşuda 2 ivme testi zaman payından kaldı (0,110 > 0,105); ivme sınırına
    `self.tol` payı eklendi (bellekte 10 ms, değişmez), tcp'de SinirDisiHiz 4 / 4 (`hedef-tcp-ilk.txt`). Tcp tam koşu
    düzeltmeden sonra yinelenmedi.
11. Görünüm tarayıcıda (Chrome, 19:15 civarı) açıldı, bakıldı: oda_engelli çizildi, robot ve yeşil / gri sonar ışınları görünür;
    R → devrede; ileri ok → 0,25 m/s, kolona yaklaşınca sonar 82 → 30 cm, robot 31,7 cm'de durdu, engel "VAR", çarpışma 0;
    sola dönüp sürünce yeniden 0,25 m/s; Boşluk → hız 0, güç ariza / acil_stop; mantar bırakılınca hâlâ ariza (kilit), R ile
    devrede ve sürülebildi. Konsolda ileti yok (yeniden yükleme sonrası da). Ekran görüntüleri `Y0s-olcum/gorunum-*.jpg`.
    Süreçler kapatıldı (py.exe + python.exe, kalan 0).

## 9. B'nin bakması gerekenler

1. `protokol.json` firmware 0.5.0'ı doğru aktarıyor mu: `main` `kod/esp32/src/seri_protokol.cpp`, `guc.cpp`, `watchdog.cpp`
   ile alan alan (özellikle hangi komutun bekçiyi / sessizliği beslediği, `guc` olay alanları, `odo` alanları).
2. Ç1–Ç9 doğru mu, eksik çelişki var mı (§ 3).
3. TASLAK uzantılar (sonar mesajı, 30 cm durma, 60 cm yavaşlama, en az sürünme hızı 0,05, bağımlı servo sınırı) Efe'nin
   firmware'iyle uyuşabilir mi; yoksa protokolden çıkarılmalı mı.
4. Testlerin "Dayanak" satırları gerçekten o bölümü gösteriyor mu (`Y0s-olcum/test-listesi.txt`).
5. TAHMİN parametreleri (enkoder 1980 tik / tur, 0,39 m/s, sonar ±15°) makul mu.
6. 21 eski dosya md5'le değişmemiş (`md5sum -c planlama/d158/Y0s-olcum/kir-bas.md5`).

## 11. Düzeltme turu (B kontrolü `Y0s-kontrol.md` "KOŞULLU GEÇER" sonrası, 22.11 19:40–)

Koordinatörün listesi A1, B2–B4, C5–C7, D8–D9, E10. Kurallar aynı (git add / commit / push yok; 21 eski dosya, kapsam dışı yerler
ve `origin/main` çalışma ağacı dokunulmaz). İlerleme aşağıda madde madde; yarıda kalırsa "Durum" satırına bak.

- **A1 yapıldı (19:45).** `Y0s-olcum/bozma-bekci.txt`, `bozma-sonar.txt`, `hedef-tcp-ilk.txt` (8 satır) yerel yol → depo köküne
  göreli; cp1254 → UTF-8 (kosu-*.txt, test-listesi.txt da UTF-8'e çevrildi, yol yoktu). `Y0s-kontrol.md` satır 15'teki yol örneği
  sözle değiştirildi (tek kelime düzeltmesi, B'nin içeriği aynı). Tarama (koordinatörün verdiği dört desen: Windows ve
  POSIX kullanıcı klasörü yolu, bulut klasörü adı, kullanıcı adı; `kod/` + `planlama/d158/Y0s-*`): 0. Yeni ölçüm çıktıları aynı süzgeçten geçirilecek (betik scratchpad'de `yol_temizle.py`).

- **B2 yapıldı.** `robot_parametreleri.json`: `iz_genisligi_m` 0,432 = FİZİKSEL iz (CAD, haritadaki hareket);
  yeni `firmware_iz_genisligi_m` 0,426 (main `motorlar.cpp` `IZ_GENISLIGI_M`, Pi `kod/ayarlar.yaml` `konum.odometri.iz_genislik_m`,
  `kod/robot/konum/odometri.py`). `cekirdek.py` `_teker_hedefleri` firmware sabitini, `_hareket` / `hakem()` fiziksel izi kullanır.
  Hangisinin doğru olduğuna karar verilmedi; ölçülen etki § 3 Ç3 ekinde.
- **B3 yapıldı.** `ping` `aku`: ana anahtar kapalıyken `null` (main `guc.cpp` `aku_olc`, `AKU_YOK_V = 1.0` "ana anahtar kapalı").
- **B4 değiştirilmedi (B'nin iddiası düzeltildi).** Plan cümlesi: `planlama/yazilim-plani.md` § İş paketleri tablosu satır 76, Y2
  kabul ölçütü "Sınır dışı komut kırpılıyor, yasak bölge reddediliyor". Aynı belgede "yasak bölge" iki kez daha geçiyor ve ikisi de
  **kafa-kol yasak bölgesi**: satır 35 (mimari "güvenlik ... eklem sınırı · kafa-kol yasak bölgesi"), satır 67 ("Eklem sınırları
  ve yasak bölge tek kaynaktan gelir: `eklem_sinirlari.json`"). `eklem_sinirlari.json`'da yasak bölge `kafa_kol_yasak` anahtarıdır
  (`"aktif": false`, "kafa-kol yasak kutusu yok"); modeldeki `bagimli` kuralı (S1 kaseti: S2 lobu ↔ kaset kapağı flanşı) ayrı bir
  anahtar, yani planın sözlüğünde "eklem sınırı" tarafında. Bu yüzden plan bağımlı sınır için "reddet" demiyor; kırpma Y2'nin
  "sınır dışı komut kırpılıyor" kısmına uyuyor. Model aynı kaldı (TASLAK). Yoruma açık: bağımlı sınır da bir tür yasak bölge
  sayılırsa karar değişir; Efe / Ahmet'e bırakıldı (Ç11).
- **C5 yapıldı.** `gorunum.py`: `surus_dogrula` (sonlu sayı, bool değil, ±1'e kırpar); `/surus` eksik alan / sayı olmayan / NaN /
  sonsuz / nesne olmayan gövde → 400; pilot döngüsü her turu `try` içinde koşar, beklenmedik hatada isteği sıfırlar ve yaşamaya
  devam eder (`/durum` → `pilot.canli`, son 3 hata). Sayfa "Pi pilotu durdu" / "bağlantı yok" rozetini gösterir (B § 4 küçük eksik).
  Test `kod/testler/test_gorunum.py` `test_kotu_surus_istegi_reddedilir_pilot_yasar` (13 kötü gövde + içeriden bozuk istek).
- **C6 yapıldı.** Her istekte Host ∈ {127.0.0.1, localhost}:kendi portu; Origin varsa aynı köken; `Sec-Fetch-Site` varsa
  `same-origin` / `none`; aksi 403. Gövde ≤ 4096 bayt. Test `test_yalniz_ayni_koken`.
- **C7 yapıldı.** `harita.py` `_parca_kesisir`: eşdoğrusal üst üste binme ve uç / T değmesi kesişim sayılır (ε = 1e-12); duvar
  parçasının iki ucu da çokgen içinde yoklanır. Test `test_esdogrusal_ve_degen_kenar_carpisma_sayilir`; eski işlevle bu test kalıyor
  (elle denendi). Kalan bilinen açık: robot bir kutunun tamamen içine ışınlanırsa (`konum_ayarla`) çarpışma görülmez.

- **D8 yapıldı (8 / 8; dayanağı bulunamayan yok).** Yeni `kod/testler/test_sozlesme.py` (6 test) + iki mevcut test güçlendirildi:
  | B bozması | Davranış | Test | Dayanak |
  | --- | --- | --- | --- |
  | B10 | 200 bayt kabul, 201 `satir_cok_uzun` | `SatirSiniri.test_200_bayt_kabul_201_red` | `seri_protokol.cpp` `SATIR_UZUNLUGU = 200`, `satir_boy < SATIR_UZUNLUGU` |
  | B11 | güç olayı cevaptan sonra (arm, birak) | `OlaySirasi.test_guc_olayi_komut_cevabindan_sonra` | `seri_protokol.cpp` satır 276, `guc.h` `guc_olay_gonder` |
  | B12 | 3 × 100 ms I2C cevapsız → `i2c` | `KorumaArizalari.test_i2c_kopunca_ariza` (yeni ortam adımı `i2c(False)`) | `guc.cpp` `I2C_YOKLAMA_MS`, `I2C_ARDISIK_HATA` |
  | B13 | devredeyken bara gidince `bara_gitti` (+ B3: `aku` null) | `KorumaArizalari.test_devredeyken_bara_gidince_ariza_ve_aku_null` | `guc.cpp` satır 251, `aku_olc` |
  | B14 | histerezis davranışı | `SonarDurma.test_engelde_geri_gidilir_engel_histerezisle_kalkar` (engel ≥ 35 cm'de kalkar ve 30–35 arasında ölçüm geldiği halde kalkmamış olmalı) | TASLAK `protokol.json` `sonar_histerezis_cm` |
  | B15 | `odo_sifirla` tikleri sıfırlar | `Odometri.test_odo_sifirla_tikleri_sifirlar` | `seri_protokol.h`, `motorlar.cpp` `toplam = 0` |
  | B16 | reset sonrası `ms` ve odo sıfırdan | `AcilStop.test_acilis_ve_reset_guc_kapali` (ping ms reset sonrası < önce; ilk odo 0 / 0) | `seri_protokol.cpp` `ESP.restart()` |
  | B18 | `yon_uygulandi` yalnız `isaret`'te true | `JestYonu.test_yon_uygulandi_yalniz_varyanti_olan_jestte` | `jestler.h`, `jest_verisi.h` JEST_TABLOSU |
- **D9 yapıldı.** `test_guvenlik.py`'de `hakem()` (atlatan) çağrısı kalmadı; asıl iddialar protokolden: hız ve durma `odo`
  farkından (`duzenek.py` `odo_hizlari`, `sur_olc`, `enkoder_duruyor`; `TIK_M` = π·0,125 / 1980, TAHMİN), güç durumu `ping` / olay,
  fren yolu (`dur` + `ping` aynı satır paketinde → kart saatiyle dur anı; beklenen 0,3² / (2·1,8) = 0,025 m, kabul 0,5–1,5 katı),
  ivme (ardışık 100 ms pencere hızlarının farkı ≤ 0,5 + 0,06 / 0,1 + 0,05 m/s²), kablo kopmasında kat edilen yol ≤ 0,3 m/s ×
  (son sur + 500 ms + pay). `hakem_varsa()` yalnız ek kontrol. `kablo_cekilince` testindeki iç güç durumu okuması (`hakem()["guc"]`)
  kaldırıldı; yeniden bağlanınca `ping` ile. `LALE_HAKEM=yok` (yeni) sahte kartta hakemi kapatır: 27 / 27 güvenlik testi hakemsiz
  geçti, atlanan 0 (önce 13 / 27 koşabiliyordu). Gerçek kartta ek şart: 4 test operatör adımı ister (mantar ×2, ana anahtar, kablo),
  5 test TASLAK sonar yeteneği ve robotu konuma koyma ister; `bagimli_sinir` testinde servo konumu protokolde yayımlanmadığı için
  son kontrol yalnız hakemle (protokol yarısı: cevaptaki kırpılmış açı). Yapılamayan test yok.
- **E10 yapıldı.** `kod/SIMULASYON.md` "Simülasyonun gösterdiği tasarım bulguları" (a) arka sonar yok, (b) engel varken yerinde
  dönüşte köşe çarpar, (c) `engel` varken 30–35 cm sürünme, (d) ek: duvara ~20°'den dar açıyla giderken köşe sürtünür (yankı yok),
  (e) iz farkı. `kod/testler/test_tasarim_bulgulari.py` (5 test, `BILINEN_DAVRANIS = True`, hep bellek içi); `kos.py --liste`
  "[BİLİNEN DAVRANIŞ / TASARIM SORUSU]" yazar, ÖZET ayrıca sayar. Model değiştirilmedi.

- **Bozmalar yeniden (B'nin `bozma.py` kopyası, scratchpad `y0s-a2/`).** 18 bozmanın 18'i yakalandı (çıkış 1), hakemli ve
  `LALE_HAKEM=yok` ile ayrı ayrı; önceden kaçan 8'inin her birini § 11 D8 tablosundaki test yakalıyor (hakemli: B10, B11, B12,
  B13, B15, B16, B18 birer test; B14 üç test: histerezis testi, `test_c` sürünme, `belge_guncel`). Her bozmadan sonra dosya eski
  baytlarla geri yazıldı; `protokol.json` ve `cekirdek.py` md5'i koşu öncesi = sonrası (`Y0s-olcum/duzeltme-bozma-md5.txt`).
  Çıktılar `Y0s-olcum/duzeltme-bozma-hakemli.txt`, `duzeltme-bozma-hakemsiz.txt`.
- **Koşular (son kod):** `py -3 kod/testler/kos.py` 3 kez: 58 / 58, çıkış 0, 9,5 / 9,7 / 9,6 s. `LALE_HEDEF=tcp` tam: 58 / 58,
  çıkış 0, 125,8 s. `LALE_HAKEM=yok`: 58 / 58, atlanan 0 (`Y0s-olcum/duzeltme-*.txt`). `PROTOKOL.md` üreticiden yeniden üretildi
  (`--denetle` güncel). Yeni test sayısı 44 → 58 (+6 sözleşme, +2 görünüm, +1 harita, +5 tasarım bulgusu).
- **Görünüm (Chrome, ≈ 20:00):** ilk açılışta sayfa 403 verdi: köken denetimim `Sec-Fetch-Site` başlığını GET'te de istiyordu,
  uzantının açtığı sekme "cross-site" gönderiyor. Düzeltme: o başlık yalnız POST'ta denetlenir (Host her istekte, Origin POST'ta).
  Sonra: R → devrede; ileri 0,25 m/s, sonar 82 cm; sayfadan 4 kötü `/surus` (1e400, NaN, metin, eksik w) → hepsi 400,
  `pilot.canli` true, hata yok; ardından sola dönüş + ileri yine 0,25 m/s; Boşluk → hız 0, güç ariza / acil_stop; mantar bırak +
  R → devrede, yine 0,25 m/s. "bağlantı yok" rozeti boş (bağlı). Konsolda ileti yok. Görüntü `Y0s-olcum/gorunum-duzeltme.jpg`.
  Süreçler kapatıldı (kalan 0), sekme kapatıldı. Bu düzeltmeden sonra 3 × bellek + tcp yeniden koşuldu (yukarıdaki sayılar).
- Yol taraması (dört desen, `kod/` + `planlama/d158/Y0s-*`): 0. 21 eski dosya md5: 21 / 21 OK. git add / commit / push yok.

Durum: 20:05 düzeltme turu bitti. Kalan açıklar: Ç3 (iz) ve Ç11 (bağımlı sınır kırp / reddet) kararı Efe / Ahmet'te;
`is_sol/is_sag` modellenmedi; robot kutunun tamamen içine ışınlanırsa çarpışma görülmez; gerçek kart `Ortam` (operatör) yok.

## 10. Durum

- 18:57–19:00 kaynak okuma, § 1–3. 19:00–19:11 § 4 madde 1–4. 19:11–19:25 madde 5–11.
- A bitti. 21 eski dosya md5 aynı (21 / 21 OK). git add / commit / push yapılmadı. Sıradaki: B (§ 9), sonra C.
- 19:40–20:05 B "KOŞULLU GEÇER" sonrası düzeltme turu: § 11. Sıradaki: C (commit, push).

## 12. Kapanış (C)

C ajanı, 22.11 (saat okundu: 20:19). Komutlar depo kökünden, `PYTHONIOENCODING=utf-8`.

**Adım 1, paket commit'i `0f469f4`** ("Lale Y0s: sahte ESP32 simülasyonu: …"; 53 dosya).
- Ön kontrol: `git fetch` sonrası yerel = uzak = `fb8a3f1`; `F9c-dogrula.py --tarayicisiz` GEÇMEZ, hata 3 (P10.8g kayıt eşitlemesinden
  beri beklenen yapısal 3, K68: commit sayısı, eşleşmeyen commit, `fb8a3f1` konu öneki); `py -3 kod/testler/kos.py` 58 / 58, 9,7 s.
- Açık yollarla `git add`: B'nin "Yeniden kontrol" listesi (`kod/` 31, `Y0s-gunluk.md`, `Y0s-kontrol.md`, `Y0s-olcum/` 20); `__pycache__`
  `.gitignore`'da, sahnede 0. Sahnelenmeyen yalnız 21 eski kir.
- Konu öneki `Lale Y0s:`: `F9c-uret.py` / `F9c-dogrula.py` commit'i pakete yalnız konu önekindeki `P<sayı>.<sayı>` kodu, `(F…)` etiketi ya da
  plan § 3 / § 5'teki hash'iyle bağlar; Y0s döngü paketi değil, bu yüzden eşleşmeyen sayılır (emsal: `9145164`, `f658f15` "Lale:"),
  `P` öneki kullanılmadı (yanlış pakete bağlardı). Sayfada not.
- Gizlilik taraması (`git diff --cached`, eklenen ≈ 5.400 satır; 3 JPG): e-posta, telefon, anahtar / belirteç, parola sözcükleri,
  yerel kullanıcı yolu, IBAN, 11 haneli sayı, resmî metin / kimlik sözcükleri. Bulunan: "parola" yalnız `Y0s-kontrol.md`'nin tarama
  cümlelerinde; "sözleşme" = protokol sözleşmesi; `%TEMP%\claude\...` ortam değişkeni (kullanıcı adı yok). JPG'ler gözle: yalnız simülasyon
  ekranı. Bulgu yok.

**Adım 2, kayıt eşitlemesi** (bu bölümle aynı commit).
- `planlama/dongu-158.md`: § 5'e Y0s satırı; § 3 F5 tablosunun altına Y0s'un yeri notu (döngü paketi değil, yazılım planı Y0–Y3'ün
  donanımsız ön çalışması). Plan belgeleri ve `yazilim-plani.md` değişmedi.
- `planlama/d158/karar-kuyrugu.md`: K69–K74 (teker izi, sonar güvenliği, bağımlı servo sınırı, arka sonar, engel yakınında dönüş / dar
  açı, sürünme) özet tablosu ve gövdeleriyle; açık 28 → 34, toplam 68 → 74; giriş notuna Y0s satırı; yeni bölüm "Y0s … kapanışından açık
  iş" (Ç1–Ç11, TAHMİN parametreler, modellenmeyenler, B'nin Y1–Y3 notları, gerçek kart hazırlığı, B'nin iki "bakılmadı" listesi).
- `planlama/d158/F9c-uret.py`: `Y0S`, `Y0SK`; `GRUP` K69–K74 (taslak); iki sayfa notu; başlıkta "Y0s kayıt eşitlemesi". `F9c-dogrula.py`
  değişmedi. Sayfa yeniden üretildi: "toplam 74, açık 34"; `--tarayicisiz` GEÇER (hata 0); `--goruntu` GEÇER (1400 / 360 px konsol 0,
  taşan 0).
- Bu commit'ten sonra yapısal hata beklenir (K68); Y0s öneki P paketine bağlanmadığı için konu öneki hatası beklenmez. Push ve commit
  sonrası ölçüm orkestratöre raporda.
- İlk push denemesini `pre-push` kancası takma ad nedeniyle durdurdu (kancanın öbür kalıpları bu aralıkta temizdi); ad bu günlükte 1,
  `Y0s-kontrol.md`'de 3 satırda geçiyordu, "Ahmet" ya da "takma ad" diye yazıldı. İki yerel commit push edilmeden yeniden yazıldı
  (orkestratör kararı, saat 20:22; `--no-verify` kullanılmadı); paket ağacı yalnız bu 4 satırla değişti.
