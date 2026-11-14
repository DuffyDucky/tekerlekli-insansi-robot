**Hüküm: DÜZELTME GEREKLİ.** İki durduran bulgu var:

- **D1′:** Denetim betiği, koruyucu (sigorta) değerlerini ve istisna kapsamını yine tablonun kendisiyle sınıyor. Ana sigortayı 30 A'den 40 ya da 60 A'e çıkaran tek bir düzenleme sessizce geçiyor.
- **D3:** Tablonun ve elektrik belgesinin okunan metinlerinde eski sigorta ve kesit değerleri kalmış: şarj kolu "10 A hat sigortası", K03 "20 AWG".

Bugünkü tablo değerleri doğru: uçlar, pinler, kanallar, sigortalar, kesitler, acil stop bayrakları ve 74 kablonun besleme zinciri. Sipariş paketi (D2) düzelmiş. İlk kontrolün kaçan on bozmasının hepsi yakalanıyor.

# P10.7a ikinci bağımsız kontrol: kablo tablosu + 16.11 sipariş listesi (düzeltme turu 1 sonrası)

Kontrol 14.11.2026'da yapıldı, rapor 06:13'ten sonra yazıldı (saat saatten okundu).

- **Depo durumu:** Dal `lale-duzeltme`, HEAD `9a0c6fe`. Değişiklikler çalışma ağacında. Kod tarafı `origin/main` (`2be1c63`).
- **Bozma denemeleri:** Depo dışında, geçici bir kopyada koştu. Her denemede kopya baştan kuruldu, tablo bozuldu ve görünüm `kablolar_uret.py` ile yeniden üretildi. Böylece `gorunum` sınaması her bozmayı yapay olarak yakalamadı; düzenleyen kişi görünümü de üretmiş sayıldı. Ardından denetim çıkış koduyla koştu.
- **Depoda yazılan tek dosya** bu rapor. Hiçbir komut FreeCAD'i ya da `rehber_uret.py`'yi koşmadı.

Kısaltmalar:

- **KJ** `planlama/adim3/kablolar.json`
- **KD** `planlama/adim3/kablolar_denetim.py`
- **KM** `planlama/adim3/kablolar.md`
- **EL** `planlama/adim3/elektrik.md`
- **KOK** `planlama/adim3/kablolama-on-kararlar.md`
- **MJ** `planlama/maliyet.json`
- **GN** `planlama/d158/kablo-tablosu-gunluk.md`
- **K1R** ilk kontrol, `planlama/d158/P107a-kontrol.md`

## 1. Göndermeyi durduran bulgular

### D1′. Denetim, koruyucu değerlerini ve istisnaları bağımsız kaynakla sınamıyor

**Ne iyileşti:** İlk kontrolün kaçan 10 bozmasını kendi biçimimle yeniden uyguladım; yakalanmayan yok (§3.1). Pin, PCA kanalı, besleme zinciri, koruma kimliği, dal, dönüş damarı, 5 V Pi / çevre teli, kesit × ortam ve malzeme sınamaları artık gerçekten dişli.

**Ne açık kaldı:** Kesit ↔ koruma sınamasının dayandığı iki veri, koruyucunun akımı (`koruyucular.*.akim_a`) ve istisna kapsamı, yine yalnız tablonun içinde. Bağımsız bir kaynakla karşılaştırılmıyorlar.

- **Koruyucu kaynağı yalnız terimle sınanıyor.** `s_kaynak` koruyucunun kaynak satırında yalnız bir terimin ("f6", "sigorta") geçmesine bakıyor (KD:906-909). Satırdaki akım değerine bakmıyor.
- **İstisnadaki kablo hiç sınanmıyor.** İstisna taşıyan kablo kesit sınamasından tümüyle çıkıyor (KD:541-550). İstisnanın kendi koruyucusu ya da bir üst akım sınırı yok. Kapsama kablo eklemek de tablonun kendi alanı.
- **Ölçüm:** Kendi bozmalarım, geçici kopyada; görünüm yeniden üretildi.

| Bozma | Gerçek etkisi | Sonuç |
|---|---|---|
| N8c `koruyucular.ana-sigorta.akim_a` 30 → 40 | G03 / G04 (12 AWG) 40 A ile korunur; istisnanın kendi gerekçesi "30 A" | **Kaçtı**, çıkış 0 |
| N8d `aku-bms` 30 → 100, ana sigorta 60 | ana hat fiilen korumasız | **Kaçtı**, çıkış 0 |
| N9d G18 (F4 5 A arkası) 22 AWG yapıldı, `kafa-5v-donusturucu-arkasi` istisnası verildi, kapsama eklendi | 22 AWG tel 5 A sigortayla; istisna D24V50F5 / SY8205 için yazılmıştı, G18'in koruyanı F4 | **Kaçtı**, çıkış 0 |
| N9c G08 (F1 arkası 12 AWG) `ana-hat-12awg` kapsamına eklendi | sessiz muafiyet | **Kaçtı**, çıkış 0 |
| N1b çevre dalı tutarlı biçimde F4'ten F3'e taşındı (G18 ucu, XL4016 çevre girişi düğümü, aşağı akış dalları) | yanlış sigorta arkası, belgeyle (EL:368) çelişir | **Kaçtı**, çıkış 0 |
| N2c F6 röle arkasına alındı, G20 / G21 bayrakları ve zincirleri buna göre yazıldı; `dallar.F6.p12` = "anahtarlı bara" | göğüs ekranı acil stopta enerjisiz görünür | **Kaçtı**. §12 karşılaştırması alt dize araması (KD:811); §12'nin öbür listesinde geçen bir ifade yazınca atlatılıyor |
| N8a F6 3 → 5 A, N8e hat-A 7,5 → 8 A, N8f şarj 7,5 → 8 A | kablo kuralı içinde kalıyor ama kararlaştırılan sigorta bu değil; koruyucunun `ad`'ı hâlâ "3 A" / "7,5 A" | Kaçtı (kablo güvenliği bozulmuyor; karar ↔ tablo farkı) |

- **Neden durdurur:** "Gerçek bir güvenlik sınıfını kaçıran denetim" ölçütü bu. Ana hattın sigortası robotun en önemli koruma değeri. Montaj rehberi değeri bu tablodan okuyacak. Tek bir sayının değişmesi ana hattı korumasız bırakıyor ve denetim bunu geçiriyor. İstisna mekanizması da herhangi bir kablo için sınırsız bir kaçış kapısı (N9d). Orkestratörün D1 hedefi ("tabloyu tablonun kendisiyle değil bağımsız kaynakla sınasın") bu iki noktada karşılanmamış. Bugünkü değerler doğru; sorun gelecekteki düzenlemeye karşı korumanın olmaması. K1R'nin D1'iyle aynı gerekçe, daraltılmış hâli.
- **Önerilen düzeltme (KD, küçük):**
  - (a) Her koruyucunun `akim_a` değeri bağımsız kaynakla karşılaştırılsın. Sigortalar için EL "Sigorta listesi"ndeki (EL:362-372) satırın "Değer" hücresindeki sayı; ana sigorta ve BMS için EL:323 / :364 satırı. Ayrıca koruyucunun kendi `ad`'ındaki sayıyla ve MJ'deki sigorta satırının değeriyle. Tutmazsa hata. Bu karşılaştırma bugün EL:372'deki "10 A" çelişkisini de yakalar (D3).
  - (b) Her istisna kendi koruyucu kimliklerini (ör. `ana-hat-12awg`: `aku-bms`, `ana-sigorta`; `kafa-5v-donusturucu-arkasi`: `D24V50F5`, `SY8205`) ve bir üst koruma akımını taşısın. Kapsamdaki kablonun devreden türetilen koruyanı bu listede olmalı. Akım sınırı yazılı koruyucularda (ana sigorta, BMS, XL4016) akım üst sınırın altında kalmalı. Kapsamdaki her kablo `kararlar` listesindeki kaydına bağlanmalı.
  - (c) §12 karşılaştırması alt dizeyle değil liste öğesiyle yapılsın (öğenin tam eşleşmesi). Bir `p12` ifadesi iki listede birden geçmesin.
  - (d) N1b, N2c, N8c ve N9d `--bozma-denemesi` listesine eklensin.

### D3. Tabloda ve elektrik belgesinde eski sigorta / kesit metni: şarj kolu "10 A", K03 "20 AWG"

| Yer | Yazan | Doğrusu |
|---|---|---|
| KJ:822 G06 `ad` (KM:1143 başlık) | "Şarj kolu: akü + → **10 A** hat sigortası → XT60E-M" | 7,5 A (`koruyucular.hat-sarj`, düzeltme turu 1, D1-4) |
| KJ:853 G06 `kesit_not` (KM:1147) | "16 AWG: 10 A hat sigortası ≤ 16 AWG'nin 10 A'i" | 7,5 A ≤ 8,2 A (45 °C düzeltmeli) |
| KJ:6298 K03 `kesit_not` (KM:1357) | "**20 AWG** (EL:279): D24V50F5 5 A ≤ 20 AWG'nin 5 A'i, sınırda" (alanın kesiti 18 AWG) | 18 AWG, istisna `kafa-5v-donusturucu-arkasi` |
| EL:372 "Sigorta listesi" Şarj satırı, **Değer** hücresi | "10 A (mini)" (Not hücresinde "10 → 7,5 A") | 7,5 A (mini) |
| EL:375-376 "Sigorta seti" | "… + şarj girişi 10 A" | 7,5 A |
| EL:279 Pi bağlantısı | "kısa USB-C erkek ucu (20 AWG, ~10 cm …)" | 18 AWG (D1-4) |

- **Nasıl ölçüldü:** KJ'nin kablo metin alanlarında ve EL'de eski değer araması yapıldı (`10 A`, `20 AWG`, `8 A`). Satırlar okundu.
- **Neden durdurur:** "Tabloda yanlış sigorta / kesit" ve "montajcıyı yanlış yönlendirecek belge" sınıfı. Montaj rehberi kablo adını ve notunu bu tablodan alacak. G06'nın adı montajcıya 10 A sigorta diyor; koruma alanı 7,5 A diyor. EL kendini "bir kesit ya da sigorta değişirse önce buradaki karar" diye tanımlıyor (EL:5) ama Değer sütunu eski. K1R'nin 17 açık iş maddesinden 4'ü (şarj akımı) "yapıldı" yazılmış; Değer hücresi kalmış.
- **Önerilen düzeltme:**
  - Altı satır düzeltilsin. Aynı geçişte G19 `kesit_not`'u da düzeltilsin (KJ:2799, KM:467: "XL4016 çevre 8 A sınırı"; koruyan artık `hat-cevre` 2 A).
  - Görünüm `kablolar_uret.py` ile yeniden üretilsin.
  - D1′ (a) bu türü kalıcı olarak yakalar. Kablo `ad` / `kesit_not` metnindeki "N A" / "N AWG" sayılarının kayıttaki koruyucu ve kesitle tutarlı olduğunu sınayan küçük bir kural da önerilir.

## 2. Kayıtlı açık iş olarak gidebilecek bulgular

Her biri tek satır; ölçüm yöntemi parantez içinde.

1. **Yer tutucu kalıbı eksik (KD:73):** "…", "bilinmiyor", "sonra bakılacak" kesin kayıtta geçiyor (N5b, N5c kaçtı). GN:379 "…"nün yasak olduğunu söylüyor ama kalıpta yok. Kalıba eklensin; istisna alanlarına da uygulansın. Şu an "?" gerekçeli istisna geçiyor (N9b).
2. **12 AWG, sonlandırma metniyle klemense girebiliyor:** G10'un sonlandırması "ön şarj kartı ucu: 2 pin 5,08 mm vidalı klemens" yazılınca geçiyor (N7c). `s_klemens` yalnız `klemensler` alanına bakıyor (KD:716). Klemens türünün sınırı da kaynaksız değiştirilebiliyor: `klemens-508` 4 mm² + G11 geçiyor (N7b; kaynak terimsiz çözülüyor, KD:712). Öneri: sonlandırmada "klemens" geçen her uç `klemensler`'de olsun; klemens sınırı kaynağıyla karşılaştırılsın.
3. **Kaynak sınaması genel terimle geçiyor:** G18 → `elektrik.md:5` ve SV1 → `elektrik.md:341` ilgisiz satırları geçti (N10a, N10b). "sigorta", "gnd", "kutusu" gibi her satırda bulunan sözcükler terim sayılıyor. Kablo kimliği ya da uç parçası adı şart koşulsun.
4. **1N4007 yalnız serbest metin:** A03'ün sonlandırmasından diyot silinince denetim görmüyor (N14). Diyot `anahtarlar.K1-bobin` / `K2-bobin` için yapısal bir alan olsun (yer, yön).
5. **`ic_baglar` 5 V ağlarını birleştirebiliyor:** D24V50F5 çıkışı ↔ arayüz kartı çevre 5 V kart içi bağı geçti (N4b). `ic_baglar` yalnız toprak sürekliliğinde kullanılıyor (KD:633). 5 V sınıf sınaması `ic_baglar`'a da uygulansın.
6. **Kayıt düzeyi `uc_a` / `uc_b` damar uçlarıyla karşılaştırılmıyor:** "Kablajda teyit" durumundaki G17'nin `uc_b.nokta`'sı "?" yapılınca geçiyor (B5c). Bu kayıtlar da rehbere gidecek. Uç parçası damar uçlarından birinin parçası olsun.
7. **Donanım adetleri denetimde yok:** Hat yuvası 6 → 3 ve bara saplaması 10 → 2 geçiyor (N11c, N11d). Kendim saydım, bugünkü adetler doğru (§3.5). Hat yuvası = `ara_koruyucu` sayısı, saplama = düğüm saplaması toplamı + yedek sınaması kolay eklenir.
8. **Yıldız köprüleri kesit sınamasının dışında:** Akü dönüşü (G05) bir saplamaya iner; öbür saplamaların dönüşü 12 AWG köprülerden geçer, yani 30 A'e kadar (`klemens_turleri.bara-pabuc.kopruler`). 12 AWG'nin 45 °C sınırı 20,5 A. Köprüler `ana-hat-12awg` kapsamına adıyla girsin ya da G05 ortadaki saplamaya insin. 50 mm'lik köprüde fiilî risk düşük (KJ köprü kaydı okundu, hesap).
9. **2 A çevre sigortası atınca ESP32 sönmeyebilir:** ESP32, hub'dan VBUS'taki 1N5819 ile de besleniyor (EL:284-286, EL:88). Çevre hattının yükleri (sonar, BTS mantığı, PC817 çıkışı) bu 1 A'lik diyot ve Pi USB'si üstünden geri beslenir. ESP32 tümüyle sönerse güvenli taraf doğru: GPIO4 / 19'da 2,2 kΩ taban → GND ile BC337-40'lar kesilir, K1 / K2 bırakır; BTS EN'de 10 kΩ pull-down var. Efe'ye: çevre 5 V'un düştüğü (VIN algısı ya da sensör sessizliği) yazılımda arıza sayılsın. Ahmet'e: 1N5819'un sürekli akımı 1 A (EL:283-290 okundu, hesap).
10. **Ani akım hesabı (EL:447-449):** Kendi hesabım:
    - Tepe 14,6 V / 5,6 Ω = 2,6 A ✓.
    - Bara τ = 5,6 Ω × 2 mF = 11 ms, 5τ = 56 ms ✓.
    - Servo kondansatörleri ½ · 11 mF · 6² = 0,198 J ✓. V²/4R ile en az ≈ 21–25 ms ✓.
    - Ama ön şarjda servoların bekleme akımı (≈ 0,4 A) aynı direnci paylaşıyor. Kondansatörlere kalan güç ≈ 4,5 W, dolma ≈ 50 ms. Toplam ≈ 100 ms; "≲ 80 ms" iyimser ama 300 ms penceresinin içinde.
    - Direnç enerjisine bekleme akımı kaybı (0,4² × 5,6 ≈ 0,9 W × 0,3 s ≈ 0,27 J) katılmamış. Toplam ≈ 0,7 J; "0,5 J sınırı"nın kaynağı belgede yok. 11 W taş direnç için ihmal edilebilir.
    - Hesap metni düzeltilsin. Karar değişmez.
11. **Bayat ama yönlendirmeyen satırlar:**
    - EL:41 (hat yuvası "×5", bugün 6), EL:418 ("6 A ile"), EL:429 ("ani akım hesabı yeniden yapılmadı"), EL:515 ("8,8 mF ≈ 0,16 J").
    - `planlama/adim5/B-malzeme-plan.md:43` ("şarj girişi 10 A mini"; tarihçe notu sigortayı kapsamıyor).
    - `planlama/adim3/pin-haritasi.md:43` ("bugün IRLZ44N").
    - `Lale-Proje-Ozeti.txt:175` ("PAM8403 … karar bekliyor, K10"; K10 a kapandı).
    - `planlama/d158/karar-kuyrugu.md:1260` ("hat yuvası 5 → 4"; bugün 6).
    - KOK:458 (O-17 karar metni "10 A"; karar kaydı, tarihçe sayılabilir).
12. **Denetimin hata metni:** Damar düzeyinde kesit verilince ileti kaydın kesitini yazıyor ("G18/−: **18** AWG … 2,46 A"; hesap 22 AWG ile, doğru). Yanıltıcı ileti, sonuç doğru (N3).
13. **`F8a-siparis.json` `guncelleme_14_11`:** V3 dışı satırlarda `adet: 1` + `v3: false` yazılı; MD tablosu "1 → **0**" diyor. `v3` bayrağı var; okuyan betik için `adet` 0 yazılması daha açık olur.
14. **1N4007 yedeği yok:** MJ satır 76, 2 adet (K1, K2). 0,61 TL; bir yedek önerilir.
15. **Teyit kalanlar:**
    - K1 soketinin (MJ satır 71, "ISO mini, 5 fişli, kablolu") kuyruk kesiti.
    - G10'un 12 AWG'sinin JQC-3FF pimine doğrudan lehimi (mekanik).
    - BTS7960 güç klemensinin aldığı kesit (KJ'de `klemens:` teyidi var).
    - Ajanın da doğrulayamadığı uç tipleri.
16. **`rehber_metin.py:637`:** Bilerek P10.7b'ye bırakılmış (K1R §2-17). Kayıtta duruyor.

## 3. Ölçümler

### 3.1 Denetim betiği

- **Temiz tablo, gerçek depo:** Denetim çıkış 0, 16 sınama GEÇER. `--bozma-denemesi` 67 / 67 (geçici kopyada).
- **Yanlış alarm yok.** Geçici kopyada ilk koşu iki hata verdi (`raporlar/kaynaklar/06-aku-secimi.md` yok). Sebep kopyada o dosyanın eksik olmasıydı; dosya eklenince çıkış 0. Depoda geçiyor.
- **Çıkış kodları:** 0 geçer, 1 sınama hatası. Kaynak yokken 2 (`KaynakYok`) kodda okundu, bozarak denenmedi. Bir sınama istisna atarsa ("sınama çalışamadı") hata sayılıyor (KD:952). Bu, bozma denemelerinde bir çöküşü de "yakaladı" saydırabilir. Benim denemelerimde çöküş çıkmadı.
- **İlk kontrolün kaçan 10 bozması**, kendi biçimimle (ajanın `k_B*` işlevleri kullanılmadı):

| # | Uygulama | Yakalayan |
|---|---|---|
| B3a | X01 röle K1 ucu `ESP32 · GPIO 12` (gpio alanı 4 kaldı) | `ag`, `esp32_pin` |
| B3b | aynı + düğüm listeye eklendi, gpio 12 | `esp32_pin` |
| B4 | G18 − damarı silindi | `donus` |
| B5a | S03 V+ ucu `?` | `ag`, `yer_tutucu` |
| B5b | S03 `uc_b.nokta` `?` (damarlar aynı) | `yer_tutucu` |
| B6 | G16 "sinyal" + 22 AWG | `kesit` |
| B8 | G12 dalı F4, enerjili | `acil_stop` |
| B9 | G17 koruması F4 | `kesit` |
| B10a | X01 5 V damarı D24V50F5'ten | `ag`, `kesit`, `acil_stop` |
| B10b | aynı + `ESP32 · VIN` düğümü 5v-pi ağına (tel tek ağda) | `kesit`, `acil_stop` |
| B11 | G08 kaynağı `elektrik.md:1` | `kaynak` |
| B14 | SV1 koruması `hat-cevre`, 22 AWG | `kesit` |
| B15 | MJ servo uzatma 23 → 230 | `malzeme` (üst eşik 24 m) |

- **Kendi yeni bozmalarım (40):**
  - Yakalananlar: N1a (G18 ucu F3'e, giriş f4'te; `ag`), N2a (G20 enerjisiz; `acil_stop`), N2b (F6 röle arkasında, p12 aynı; `acil_stop` §12 ile), N3 (− damar 22 AWG), N3b (16 AWG'nin ortak dönüşü 22 AWG kablo), N4 (yeni kablo D24V50F5 → ESP32 VIN), N5a ("belirlenecek"), N6a (yıldıza 13. iletken), N6b (5 → 4 saplama), N7a (G05 → 5,08 klemens), N8b (F5 5 A), N8g (F1 25 A), N9a (gerekçe anahtarı silindi), N10c (F6 kaynağı F3 satırı), N11a / b / e (18 AWG 14 m / 10 m, sinyal teli 6 rulo), N12 (güç damarları ağsız yeni düğümlere: `donus`, `acil_stop`), N13 (G19 hat sigortası `hat-G22`), N15 (SV3 bölge "etek").
  - Kaçanlar: N1b, N2c, N4b, N5b, N5c, N7b, N7c, N8a, N8c, N8d, N8e, N8f, N9b, N9c, N9d, N10a, N10b, N11c, N11d, N14, N16 (`dallar.F4.p12` = "akü", alt dize, her yerde geçer), B5c. Sınıflandırma §1 ve §2'de.
  - Yeni sınamaların bağımsız kaynağı:
    - pin haritası §9 JSON'u ve `main` `kanallar.yaml`: gerçekten bağımsız;
    - §12: bağımsız ama alt dize ile, atlatılabiliyor;
    - MJ (malzeme metreleri): bağımsız;
    - koruyucu akımları, istisna kapsamı, ağ ve düğüm modeli: **tablonun kendisi** (D1′).
  - İzinli değer kümeleri (`devre_turleri`, `dallar`, `koruyucular`) atlatılamıyor; koruma ve dal artık devreden türetiliyor. Ama kümelerin kendisi (dalın p12'si, istisna kapsamı, klemens sınırı) aynı dosyada serbestçe değiştirilebiliyor.

### 3.2 Düzeltme turu tabloyu bozmadı mı

Karşılaştırma tabanı: ilk kontrolün kopyasındaki `kablolar.json`, ajanın `kablolar-tur3` kopyasıyla SHA-256 olarak aynı. Bugünkü tabloyla 74 kablo alan alan karşılaştırıldı.

- **Değişmeyenler:**
  - 74 kablonun bütün damar uçları, GPIO, pin adı, PCA kanalı ve adı aynı.
  - `dal` ve `acil_stopta_enerjili` 74'ünde aynı.
  - Kesit yalnız K03'te değişmiş (20 → 18 AWG, D1-4).
- **Koruma değişiklikleri (hepsi kararla tutarlı):**
  - G06 10 → 7,5 A (D1-4).
  - S01–S10 ve SV1–SV3 8 → 10 A (XL4016 çip sınırı).
  - K03 / K05 5 A → D24V50F5 "belgelenmemiş"; K04 3,7 A → SY8205 "belgelenmemiş" (D1-5).
  - M01–M04 F1 20 A → BTS7960 (D1-3).
  - G19, X01, B01, B02, N01, N02, I01, I02, Q01–Q03 → `hat-cevre` 2 A (O-19).
- **Sonlandırma değişiklikleri:**
  - Kesin kayıtlarda "öneri" sözcüğü kalkmış.
  - A04'e "WAGO 2273-203 (acil stop düğümü)" yazılmış: önceden de karar olan O-6 düğümü, MJ satır 62.
  - 1N4007 A03 / A05'e yazılmış.
- **Besleme zinciri:** 74 kablonun zincirini EL blok şemasından (EL:323-341), EL:441-444 ve EL:46-49'dan kendim kurdum ve tablodaki `besleme_zinciri` ile karşılaştırdım. Hepsi tutuyor:
  - G01–G05 akü / ana sigorta;
  - G06 ana sigorta yük tarafı → şarj sigortası;
  - G07 ana anahtar sonrası 100 kΩ;
  - G08 / G10 F1, K1 / K2 öncesi;
  - G09, G11–G16, G22, M01–M04, S01–S10, SV1–SV3 anahtarlı bara (K1 ∥ K2) ve kendi hat sigortaları ya da XL4016'ları;
  - G17, K01–K05, U, H, C, AU F3 ve kafa dönüştürücüleri;
  - G18 F4; G19, X01, B01, B02, Q01–Q03 `hat-cevre`; N01, N02, I01, I02, P01–P03 ESP32 3V3;
  - G20 / G21 F6 (röle öncesi);
  - A01 F5; A02–A06 mantar sonrası.
- **Yeni alanlar:**
  - `koruyucular` ve `anahtarlar` grafı EL ile aynı yapıda.
  - `dugumler`: 294 uç, ağları yazılı.
  - Yıldız 11 / bara 8 iletken: kendi sayımım aynı.

### 3.3 Kararların kendisi

- **Ortam katsayısı:** Ajanın gösterdiği ikincil sayfayı açtım. NEC Table 310.15(B)(1), 75 °C sütunu, 41–45 °C 0,82, 46–50 °C 0,75. Değerler doğru. NEC'in birincil metni bakılmadı. Etek 45 °C (EL:318 ölçütü) ve kafa 49 °C (EL:302, hesap) bölgeleri kaynağıyla tutarlı.
- **XL4016:** Veri sayfası Rev 1.2 indirildi, s. 5 okundu: "Switch Current Limit IL, VFB = 0, 10 A" (yalnız tipik). Aynı sayfada çıkış kısa devresinde frekans 48 kHz'e düşüyor (Fosp). Ajanın değeri doğru. Rev 1.3 bakılmadı.
- **Şarj sigortası:** Robocombo sayfası okundu: şarj akımı 0,1–5,0 A, en çok şarj gücü 50 W, adaptör 12 V / 5 A. Ürün başlığındaki "80W" adaptörle tutarsız, ama şarj akımını değiştirmiyor. 5 A × 1,25 = 6,25 ≤ 7,5 ≤ 8,2 A (16 AWG, 45 °C). Karar doğru.
- **D24V50F5:** Pololu sayfası okundu. Aşırı akım sınırı akım ve sıcaklığa bağlı, eşik verilmiyor; düşük girişte "well over 5 A" çalışma noktaları olabiliyor. Kafa içi, kısa, 18 AWG silikon kablo için kayıtlı istisna + KT1 masa testinde kablo sıcaklığı savunulabilir. Tam yükteki kısa devre akımı bakılmadı (tezgâh işi).
- **Servo ana hatları (O-20 c):**
  - Çıkışa 7,5 A sigorta konsa SV1 / SV2 tepe 7,24 A'de anmanın %97'sinde çalışır; sıcak etekte zamanla atıp kolu düşürebilir. Gerekçe doğru.
  - Kural içinde kalan yol 12 AWG'dir (20,5 A ≥ 10 A); 14 AWG kural tablosunda yok. Dağıtım kartının 5,08 klemensi 12 AWG almıyor.
  - İstisna (beklenen akım 4,87 / 7,24 ≤ 8,2 A; şart T8 E2) savunulabilir. Durdurmaz.
- **2 A çevre sigortası (O-19):**
  - Tepe 0,61 A, anmanın %31'i; açılışta atmaz.
  - 22 AWG damarların 45 °C sınırı 2,46 A ≥ 2 A.
  - Atarsa davranış §2-9'da.
- **K04 istisnaya alındı (O-21):** Kablo hazır, kesiti bilinmiyor; teslimde kesit yazısı şartı var. Savunulabilir.
- **Saplama başına 4 pabuç + zincir köprü (O-22):**
  - ABYC kuralı ve n × 4 − 2(n − 1) yer formülü doğru. Yıldız 5 saplama = 12 yer (11 iletken); bara 4 saplama = 10 yer (8 iletken).
  - Köprü akımı §2-8'de.
- **`motor-fabrika-kablosu` yeni gerekçesi:** "F1 korumaz; sargı + BTS7960 akım sınırlama / ısıl kapatma + yazılımın IS → EN kesmesi" doğru yönde. BTS7960'ın akım sınırı eşiği belgede yok (kayıtta da öyle). Efe'ye bildirilecek madde var.
- **1N4007:** K1'de soket kuyruğu 86 (+) / 85 (−) üstünde, K2'de bobin klemensinde; katot bobinin + ucunda. Ters paralel söndürme diyodu için yön doğru: katot besleme tarafında, anot BC337 kollektörü tarafında. Birincil kaynak bakılmadı; yön standart devre bilgisi.
- **12 AWG uçları:**
  - G10 K2 pimine lehim, G11 direnç bacağına hat üstünde lehim. G12 / G13 BTS klemensinde `klemens:` teyidiyle.
  - Röle (MAH-112-C-4) uç tipi bakılmadı. MJ'de "ISO mini, kablolu soket" var, 12 AWG soket kuyruklarına eklenecek.
- **Ani akım:** §2-10.

### 3.4 Sipariş paketi (D2)

- `F8a-siparis.md` başında 14.11 notu var, `.json`'da `guncelleme_14_11` var. Güncel kaynak tek ve açık: `planlama/maliyet.json`.
- S87 IRLZ44N iki yerde "ALMA" işaretli (satır 13 ve §5.1 satır 374).
- MJ'nin `76fd4b2` hâli ile bugünkü hâlini kendi betiğimle karşılaştırdım:
  - 33 kalem değişmiş; tablonun 34 satırı bunların hepsini kapsıyor (69 numaralı kalem "ALMA" + "BC337-40 eklendi" diye iki satır).
  - Adet, birim fiyat ve satıcı 33'ünde MJ ile aynı. V3 dışına çıkanlar tabloda "→ 0" yazılı.
  - `76fd4b2` ile HEAD arasında MJ değişmemiş.
- Siparişi anan belgeler güncel kaynağa işaret ediyor: `proje-plani.md:92`, `karar-kuyrugu.md:43, :499, :512`, `README.md:50` (paket toplamı "P10.7a'dan önceki liste" notuyla).
- 16.11'de paketi açan biri, notu okumadan §5'ten sipariş verirse eski kalemleri alır. Not ilk satırda, kalın ve gözden kaçmıyor. Durdurmaz.

### 3.5 Toplamlar, bağımlılar, doğrulamalar (gerçek depoda; yazmayan betikler, `-B`, `GIT_OPTIONAL_LOCKS=0`)

- **Toplamlar:**
  - `maliyet_toplam.py`: genel **120.939,36**, koşullular dahil **126.510,83**, V3 kalem 126.
  - `sonuc-rapor.html` dört `data-j`: 120.939,36 / 126.510,83 / 96.043,61 / 104.344,25.
  - README:50 ve `proje-plani.md:11` ≈ 120.900 / 126.500 / 96.000 / 104.300. Tutuyor.
- **Doğrulama betikleri:**
  - `kablolar_uret.py --kontrol` güncel (0). Denetim 0.
  - F9b `--tarayicisiz` GEÇER (0). Tarayıcı kısmı bakılmadı.
  - F9d 0; README uyuşmazlığı 0.
  - `testler_html.py --kontrol` geçti.
- **F9c:** Çalışma ağacında 28 hata. `git archive 9a0c6fe` geçici klasöre açıldı; F9c orada, deponun `.git`'i yalnız okunarak koştu: 28 hata. İki hata kümesi satır satır aynı. Ajanın iddiası doğrulandı.
- **Donanım adetleri** (tablodan kendi sayımım; MJ):
  - Hat yuvası 6 (A, B, C, şarj, G22, çevre) = 6.
  - Mini sigorta: 2 A × 2, 5 A × 1, 7,5 A × 3. Hepsi tam, yedeksiz.
  - Standart sigortalar 30 A × 2, 5 A, 2 A, 3 A (+ kutudaki set).
  - Bara saplaması 5 + 4 + 1 = 10. BC337-40 3, 1N4007 2.
  - Pabuçlar: kırmızı 4 (G17−, G18−, G20−, G22−) ≤ 10; mavi 9 ≤ 20; sarı ≈ 25–30 (köprüler 14 dahil) ≤ 40.
- **Kablo metreleri:** Denetimin iki yönlü malzeme sınaması geçiyor; N11a / b ile üst ve alt sınırın çalıştığı görüldü.

### 3.6 17 açık iş maddesi

1 – 16'nın her biri dosyada görüldü. İstisnalar:

- **4 / 8 (şarj):** EL:372 Değer hücresi ve EL:376 kalmış → D3.
- **8 (WAGO):** EL ve KOK:342'de yıldız / bara için WAGO ifadesi kalmadı. KJ'deki WAGO yalnız 2273 acil stop düğümü (O-6) ve O-3 karar kaydı.
- **10 (8,8 mF):** KOK §12 düzeltilmiş; EL:515'te kalmış → §2-11.
- **12:** `maliyet_duzelt.py` tarihî betik diye bilerek bırakılmış. `pin-haritasi.md:43` listede yoktu → §2-11.
- **17:** Bilerek açık.

Depo genelinde yeniden arama yapıldı (WAGO, IRLZ44, AO3400, "mini 2 A", "dağıtım kartı yok / gerekmez", 8,8 mF, eski pinler, şarj 10 A, 20 AWG). Tarihli günlükler ve kontrol raporları, brief'ler, `main`, `kod/`, `rehber/`, `planlama/rehber/`, `tasarim/freecad/`, `tubitak-2209b/` hariç tutuldu.

- **Kalanlar:** §1 D3 ve §2-11.
- **Tarihçe işaretli, sorun değil:**
  - EL:106, :114, :143, :458-459, :496;
  - `raporlar/aku-secimi/rapor.html:72` ve `raporlar/kaynaklar/06-aku-secimi.md:165` (akü raporunun 11.10 kaydı, "UserPil 6 A … 10 A");
  - `raporlar/kaynaklar/05-fiyat-arastirmasi.md` (WAGO 221, tarihli fiyat araştırması).

### 3.7 Gizlilik ve sınırlar

- **Taranan:** Paketin eklediği satırlar: `git diff 9a0c6fe` artı satırlar, `tasarim/freecad/` hariç, ve izlenmeyen 6 dosyanın tamamı; ≈ 14.800 satır.
- **Aranan kalıplar:** Yerel kullanıcı yolu, sürücü harfli yol, bulut / geçici klasör, depo dışı dökümün adı, e-posta, parola / anahtar, ağ adı.
- **Sonuç:** Bulgu yok.
- **Soyad:** Tek soyad eşleşmesi `testler.html` içindeki T8 satırı ("Hat > 5 A sürekli … karar …"). Satır HEAD'de de aynı; paket bölümü yeniden üretirken satır yeniden yazılmış, bu turda eklenmemiş. T8 kaynağında duruyor. Soyadının depodan temizlenmesi ayrı iş.
- **Sınırlar:**
  - `rehber/`, `planlama/rehber/`, `kod/` altında değişiklik yok.
  - `tasarim/freecad/` altında yalnız brief'in "bu paketten değil" dediği 13 PNG ve `yerlesim-kontrol.json` var.
  - Depoda koşturduğum doğrulamalar dosya yazmadı. `git status` rapordan önce 41 satır, sonra 42 (yalnız bu rapor eklendi).

### 3.8 C adımı için liste

- **Commit'e girecekler:** Ajanın listesi `git status` ile birebir tutuyor; 13 PNG ve `yerlesim-kontrol.json` hariç. Bu rapor (`planlama/d158/P107a-kontrol-2.md`) eklenir. D1′ ve D3 düzeltmesi yapılırsa KD, KJ, KM ve EL yeniden girer.
- **`dongu-158.md` (GN §16-1, -2):**
  - Metin, düzeltmeden sonra "ikinci bağımsız kontrol `P107a-kontrol-2.md` (DÜZELTME GEREKLİ → düzeltme turu 2 …)" diye tamamlanmalı.
  - Bozma sayısı düzeltmeden sonraki sayıyla yazılmalı.
  - "F8a paketine 14.11 bayatlık notu" doğru.
- **`karar-kuyrugu.md`:** GN §16-3'teki 1235, 1260, 1264 kapanışlarına ek olarak 1260'taki "hat yuvası 5 → 4" ifadesi bugünkü 6 ile düzeltilmeli.
- **"Efe'ye bildirilecek" eksik.** GN §15.9 listesinde tek madde var (BTS7960 IS → EN). Eklenmesi önerilenler:
  - (2) Çevre 5 V'un düşmesi (2 A sigorta attı; ESP32 USB'den yaşamaya devam eder) yazılımda arıza olarak algılansın (§2-9).
  - (3) Ön şarjda K2 ≤ 1 s kuralı ve 300 ms penceresi. Var olan E9 dizisi; hesap güncellenince haber verilir.
- **"Ahmet'e" listesi** (5 madde) tam. Eklenmesi önerilenler:
  - (6) 1N5819'un 1 A sınırı ve çevre hattının USB'den geri beslenmesi (§2-9).
  - (7) Yıldız saplamalarında akü dönüşünün (G05) ortadaki saplamaya bağlanması (§2-8).
  - (8) K1 soket kuyruklarının kesiti (§2-15).

## 4. Bakılmadı

- NEC 310.15(B)(1)'in birincil metni (ikincil sayfa açıldı).
- NFPA 79 ve 33 CFR tabloları: bu turda yeniden açılmadı (K1R §3.1 okumuştu).
- XL4016 Rev 1.3; BTS7960 akım sınırı eşiği; MAH-112-C-4 ve soketinin uç / kuyruk kesiti; 5,08 mm klemensin ve BTS7960 güç klemensinin aldığı kesit.
- HC-SR04, BNO055, PCA9685 veri sayfası akımları; 2 A mini sigortanın zaman-akım eğrisi.
- F9b'nin tarayıcı kısmı (yalnız `--tarayicisiz` koştu).
- Web fiyatı: bu turda yalnız şarj cihazı sayfası açıldı. Öbür fiyatlar K1R §3.5'te.
- Kaynak okunamadığında çıkış kodu 2: kodda okundu, bozarak denenmedi.
- Hiçbir akım, boy ya da sıcaklık ölçülmedi (malzeme yok).
