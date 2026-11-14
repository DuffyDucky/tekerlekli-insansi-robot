**Hüküm: DÜZELTME GEREKLİ.** Tablonun bugünkü değerleri (pin, PCA kanalı, sigorta, kesit, acil stop bayrağı) doğru. Ama denetim betiği elektrik güvenliği sınıflarında dişsiz, 16.11 siparişinin paketi (P8.1, F8a) de bayat duruyor.

# P10.7a bağımsız kontrol (B adımı): kablo tablosu + 16.11 sipariş listesi

Kontrol 14.11.2026'da yapıldı, rapor 04:55'te yazıldı (saat saatten okundu). Dal `lale-duzeltme`, HEAD `9a0c6fe`, değişiklikler çalışma ağacında. Kod tarafı `origin/main` (`2be1c63`) üzerinden okundu. Bozma denemeleri depo dışındaki geçici bir kopyada koştu. Depoda yazılan tek dosya bu rapor. Hiçbir komut FreeCAD'i ya da `rehber_uret.py`'yi koşmadı.

Kısaltmalar: **KJ** `planlama/adim3/kablolar.json`, **KD** `planlama/adim3/kablolar_denetim.py`, **EL** `planlama/adim3/elektrik.md`, **KOK** `planlama/adim3/kablolama-on-kararlar.md`, **PH** `planlama/adim3/pin-haritasi.md`, **MJ** `planlama/maliyet.json`, **GN** `planlama/d158/kablo-tablosu-gunluk.md`.

## 1. Göndermeyi durduran bulgular

### D1. Denetim betiği elektrik güvenliği sınıflarında dişsiz (bozma denemelerimin 15'inden 10'u yakalanmadı)

Betik gerçek depoda çıkış 0 veriyor. Ajanın kendi 31 bozması, kopyada `--bozma-denemesi` ile koşunca 31 / 31 yakalanıyor. Kendi 15 bozmamın sonucu aşağıda. Her bozmada kopya yeniden kuruldu, betik çıkış koduyla koşturuldu. Son geri yüklemeden sonra çıkış 0.

| # | Bozma | Sonuç |
|---|---|---|
| B1 | GPIO23 iki işe verildi (X01) | Yakalandı (ayni_nokta, esp32_pin) |
| B2 | SOL_GERI_PWM GPIO26 → 27 (B01) | Yakalandı |
| B3 | Uç `ESP32 · GPIO 12` yazıldı (boşluklu yazım, boş pin) | **Yakalanmadı.** `s_esp32_pin` yalnız `ESP32 · GPIO\d+$` biçimini tanıyor (KD:155-) |
| B4 | G18'in − (GND) damarı silindi, dönüşü olmayan güç kablosu | **Yakalanmadı.** Dönüş damarı sınaması yok |
| B5 | S03'ün bir ucu `?` yapıldı | **Yakalanmadı.** `s_iki_uc` yalnız alanın boş olmadığına bakıyor (KD:130) |
| B6 | G16'nın devre türü "sinyal" yapıldı, 22 AWG + 5 A verildi | **Yakalanmadı.** `s_kesit` yalnız `devre.startswith(GUC)` olan kabloları sınıyor (KD:55, KD:268). Devre türü serbest metin |
| B7 | K05 22 AWG + 5 A (düz) | Yakalandı (kesit) |
| B8 | G12 (anahtarlı bara) F4 dalına alındı, enerjili yazıldı | **Yakalanmadı.** `s_acil_stop` kablonun bayrağını tablonun kendi `acil_stop_dallari` listesiyle karşılaştırıyor (KD:402-423). Dal ataması uçtan ya da korumadan türetilmiyor. §12 için de yalnız bazı ifadelerin metinde geçip geçmediğine bakıyor (KD:56). Bu, kendi kendini doğrulayan bir sınama |
| B9 | G17'nin koruma adı F4 yazıldı (dalı F3) | **Yakalanmadı.** Koruma ↔ dal çapraz sınaması yok |
| B10 | X01'de ESP32 VIN, D24V50F5 Pi hattından beslendi (5 V Pi / çevre karışması) | **Yakalanmadı.** 5 V hat sınıfı sınaması yok |
| B11 | G08'in kaynağı `elektrik.md:1` yapıldı (ilgisiz satır) | **Yakalanmadı.** `s_kaynak` yalnız satırın var olup olmadığına bakıyor (KD:457-) |
| B12 | Kafa tilt PCA K13'e alındı | Yakalandı (pca_kanal) |
| B13 | `kablolar.md` elle değiştirildi (GPIO19 → 18) | Yakalandı (gorunum) |
| B14 | SV1'in koruması 2 A yazıldı, kesiti 22 AWG yapıldı | **Yakalanmadı.** `koruma.akim_a` beyan edilen değer. Gerçek korumayla (XL4016 sınırı, dal sigortası) bağı sınanmıyor |
| B15 | Servo uzatma adedi 23 → 230 | Gerçek anlamda **yakalanmadı.** Hata çıktı ama yalnız biçimden: dosyayı tek satıra yazınca kaynak satır numaraları kaydı. `s_malzeme` yalnız eksik miktarı sınıyor (KD:383-), şişmeyi görmüyor |

**Neden durdurur:** Brief "dişsiz denetim" sınıfını göndermeyi durduran bulgu sayıyor. Rehberin kablolama adımları bu tablodan beslenecek ve tabloyu bundan sonra koruyan şey bu betik. Kesit ↔ koruma ve acil stop sınamaları, tabloya yanlış yazılmış bir sigorta, dal ya da devre türünü sessizce geçiriyor (B6, B8, B9, B14). Tablonun bugünkü değerlerini elle doğruladım (§3), yani bugün yanlış kablo yok. Sorun, gelecekteki bir düzenlemeye karşı korumanın olmaması.

**Önerilen düzeltme (KD):**
- (a) Kesit sınaması devre türüne değil damar / kesit varlığına bağlansın. Ya da devre türü kapalı bir listeden seçilsin, listede olmayan tür hata versin.
- (b) Her kablonun `koruma.ad` / `akim_a` değeri dal tanımından türetilsin: dal → sigorta (F1–F6, hat sigortaları, XL4016 / D24V50F5 sınırı) tablosu bir kez yazılsın, kablodaki değer onunla eşleşmezse hata versin.
- (c) Acil stop bayrağı daldan değil uç zincirinden ya da en azından dal ↔ koruma eşlemesinden türetilsin. B8 türü "anahtarlı bara kablosu enerjili dalda" çelişkisi hata versin.
- (d) Güç devrelerinde her + damarın bir − / GND damarı ya da kayıtlı ortak dönüşü olsun.
- (e) ESP32 uçları için gevşek bir regex (`GPIO\s*\d+`) kullanılsın. Biçim dışı her ESP32 ucu hata versin. `?`, `TBD` gibi yer tutucular yasaklansın.
- (f) 5 V Pi (D24V50F5) ve 5 V çevre (XL4016 çevre) uçları için hat sınıfı eklensin. Bir kablo iki sınıfı birleştirirse hata versin.
- (g) Malzeme sınaması iki yönlü yapılsın (ihtiyaç × pay ile liste arasında üst sınır).

Ardından B3–B11 ve B14 türü bozmalar `--bozma-denemesi` listesine eklensin.

### D2. 16.11 siparişinin paketi bayat: `F8a-siparis` hâlâ IRLZ44N ve eski kalemleri listeliyor

- **Yer:** `planlama/d158/F8a-siparis.md:327` (S87 "Röle sürücü MOSFET: VBsemi Elec IRLZ44NPBF-VB (TO-220)", 2 adet) ve `planlama/d158/F8a-siparis.json:3232-3258`. Dosyanın kontrol tarihi 09.11 (F8a-siparis.md:3). Son commit'i P8.1'den. Başında "yerini `maliyet.json` aldı" diyen bir not yok.
- **Nasıl ölçüldü:** `git grep IRLZ44` ve dosya başlığı okundu. `proje-plani.md:92` ve `karar-kuyrugu.md:43, :499, :512` siparişi "P8.1 sipariş paketi (S = 16.11)" diye anıyor. `README.md:50` de paketin toplamını (≈ 107.600) F8a'dan veriyor. P10.7a değişiklikleri yalnız MJ'de: BC337-40TA ×3, hat yuvası, pabuçlar, 12 / 16 / 18 / 20 AWG artışları, jumper, 3 A standart sigorta vb. 10 yeni kalem F8a'da yok.
- **Neden durdurur:** "Yanlış sipariş kalemi" sınıfı. Sipariş P8.1 paketinden verilirse artık devrede olmayan MOSFET alınır, BC337-40 ve P10.7a kalemleri eksik kalır.
- **Önerilen düzeltme:** C adımından önce iki yoldan biri seçilsin. (a) F8a-siparis.md ve .json'un başına "14.11'den beri sipariş kalemleri için tek kaynak `planlama/maliyet.json`; S87 ve şu satırlar geçersiz" notu eklensin, README:50'deki paket toplamı da buna göre işaretlensin. (b) Sipariş paketi MJ'den yeniden üretilsin. En azından (a) siparişten önce yapılmalı.

## 2. Kayıtlı açık iş olarak gidebilecek bulgular

Her biri tek satır; ölçüm yöntemi parantez içinde.

1. **Pabuç yığını saplama başına 5 (KJ:6742, :6747, :6951):** ABYC E-11 bir saplamaya en çok 4 iletken öneriyor (kaynak okundu). Yıldız barası 11 iletken / 3 saplama, anahtarlı bara 8 iletken / 2 saplama. İletkenleri kendim saydım: yıldız G05, G06−, G12−…G18−, G20−, G22− = 11; anahtarlı bara G09, G11, G12–G16, G22 = 8. İkisi de tam kapasitede, yedek yer sıfır. Öneri: saplama başına ≤ 4 (yıldıza 3 yerine 4 saplama, anahtarlı baraya 2 yerine 3) ya da tek bakır / pirinç şerit üstünde çok saplama. Büyük akımlı pabuçlar alta, düz pul + yaylı pul. Bara saplaması satırı (MJ, "fiyat bekliyor", 6 takım) buna göre 7–8 takım olur. Siparişten önce karar verilirse iyi olur.
2. **XL4016 akım sınırı 8 A yazılmış (KJ:182, :2057, :2145, :2233, :2512):** 8 A modülün anma değeri. Çip veri sayfasındaki anahtar akım sınırı ≈ 10 A (veri sayfası okundu). 16 AWG için tablo değeri 10 A, yani yine sınırda geçer. `servo-uzatmasi` istisnasının gerekçesi de "8 A" yerine "≈ 10 A (çip sınırı)" olmalı. Tezgâhta bir uzatmayı kısa devre ederek akım ve ısınma ölçülsün (E7'ye ek).
3. **`motor-fabrika-kablosu` gerekçesi (KJ:215):** "kısa devrede koruma F1 20 A" ifadesi, kesiti büyük ihtimalle 18 AWG'den ince olan motor kablosunu korumaz. Metin "F1 kabloyu korumaz; koruma yazılımda (BTS IS akım ölçümü ile kesme)" diye düzeltilsin. Şart (KJ:216) motor gelince tetiklenecek.
4. **Kesit kuralının ortam sıcaklığı 30 °C (KJ:82):** Varsayım açıkça yazılmış. Ama projenin kendi sınırlarına göre etek ≈ 45 °C, kafa ≈ 49 °C. NFPA 79'un 75 °C sütununa 41–45 °C için 0,82, 46–50 °C için 0,75 düzeltmesi uygulanınca K03 (20 AWG, 5 A) ve G06 (16 AWG, 10 A) temkinli tabloyu geçmiyor. Öneri: bu iki kabloya 30 °C varsayımı not olarak yazılsın; E7 ısı testinde sıcaklıklarına bakılsın.
5. **D24V50F5 akım sınırı (K03, K05):** Pololu bu kartın akım sınırını belgelemiyor; "5 A sürekli" değeri bir anma değeri, sınır değil. Kayıtta "koruma" değil "anma" diye geçsin.
6. **1N4007 yalnız K1 için yazılı, yeri belirsiz (KJ:3029, A03); K2 (A05, KJ:3157) için yok:** PH:302 ve PH:429 iki röleye de ters paralel diyot istiyor. Öneri: A05'e de eklensin, yeri "röle bobin uçlarında" diye yazılsın.
7. **G10 / G11 "kart klemensi (öneri)" ile bitiyor (KJ:1078, :1159):** Klemens alanı yok, denetim görmüyor. Kaydın kendisi 5,08 mm klemensin 12 AWG almadığını söylüyor (KJ:1101, :1182). Sonlandırma "lehim ya da saplama + pabuç" olarak kesinleştirilsin.
8. **EL'de tabloyla çelişen metin:** EL:129 "çıkış 2 servo uzatmasına küçük klemensle, dağıtım kartı gerekmez" ve EL:330 "klemens ── kafa pan + tilt" diyor. Tablo (KJ:2230, :2272) ve EL eki ise "dağıtım kartı C" diyor. EL:68, EL:341 ve KOK:342'de hâlâ "WAGO yıldız", EL:325'te "anahtarlı 12 V bara (WAGO)" var; O-3 kararı saplama + pabuç. EL:372 "Şarj cihazı 6 A" ile EL:93 "IMAX B6 ≈ 3,4 A" farklı. Bu satırlar tabloya göre düzeltilsin ya da tarihçe olarak işaretlensin.
9. **T7 hâlâ "mini 2 A" diyor:** `planlama/d158/testler/T7-gogus-ekrani-12v.md:11, :28, :119` (ve testler.html'deki karşılıkları). K11 a kararı F6 3 A standart (KOK:19, :90; EL:68). T7 bu pakette değişmiş ama bu satırlar kalmış. `planlama/d158/sonuc-rapor.html:136` (K52 metni) de aynı eski ifadeyi taşıyor.
10. **KOK:361 "8,8 mF":** Beşinci kondansatörle 5 × 2200 µF = 11 mF olur; enerji ≈ 0,20 J. Ajan bunu ani akım hesabı için zaten kaydetmiş (GN:378). Bu satır da P10.7b listesine girsin.
11. **KOK:454 "Dupont" sözü:** O-4 revizesiyle kit çıktı (KOK:436, :459). Bayat ifade.
12. **Öbür belgelerde eski MOSFET / mini sigorta:** `Lale-Proje-Ozeti.txt:97-98, :178` (mini 2 A, IRLZ44N, "K11 karar bekliyor"); `planlama/adim5/B-malzeme-plan.md:64` (IRLZ44N); `planlama/adim5/maliyet_duzelt.py:103, :166`. Yalnız listelenenler: `tasarim/freecad/taban/taban_rapor.py:360` (kapsam dışı), MJ:109 (K2 notu, "eski" diye işaretli).
13. **Alan tanımında belirsizlik (KJ:15):** `acil_stopta_enerjili` tanımındaki "(ana anahtar açık)" ifadesinde "açık" kelimesi hem "devrede" hem "kesik" diye okunabilir. "Ana anahtar devrede (ON)" yazılsın.
14. **XT60E-M şarj girişi:** Erkek panel girişinin pinleri ana anahtar öncesinde, yani sürekli akü gerilimi taşıyor (K50 ile aynı konu). G06'ya "pinler her zaman gerilimli; kapak / koruyucu" notu eklensin.
15. **Alçak profil mini sigorta ↔ "Mini/Micro" hat yuvası:** Aile tutarlı (§4), ama 2 A alçak profil mininin bu yuvaya tam oturması teslimde denensin.
16. **AU2 (ses bölücüsü → PAM8403):** Bölücü PAM pedlerinin dibinde, kablo üstünde. Ayrı bir kablodan çok lehim işi. Sayımı değiştirmez, `not` alanına yazılsın.
17. **Kart LED'i:** Tablo GPIO2'yi "yalnız LED" diye doğru gösteriyor. Rehber tarafındaki `rehber_metin.py:637` "K2 = GPIO2 LED" uyarısı bilerek P10.7b'ye bırakılmış (GN:161). Kayıtta duruyor.

## 3. Ölçümler

### 3.1 Tablo ↔ kaynaklar (madde 1)

- **ESP32, 25 pin:** Tablodaki ESP32 uçlarını PH §9 JSON'uyla (PH:405-451) kendi betiğimle karşılaştırdım. 21 harici GPIO birebir aynı: GPIO, işlev adı ve karşı uç. 1 ve 3 kart üstü UART, 2 yalnız kart LED'i, 12 boş; toplam 25.
- **Pin ayrıntıları:**
  - 16 / 17'de 1 kΩ seri direnç var (N02 A, N01 B).
  - EN ortak hattında 10 kΩ → GND var.
  - IS bölücüsü 6,8k / 5,1k, sonar bölücüsü 4,7k / 10k, akü bölücüsü 100k / 18k (100 kΩ kaynak ucunda, G07).
  - BC337-40 #1 kollektörü K1 85'e, #2 kollektörü K2 bobin −'ye gidiyor. 270 Ω ve 2,2 kΩ X01'de yazılı.
  - 1N4007 için bkz. §2-6.
- **PCA9685:** K0–K9, `main` dalındaki `kod/jestler/kanallar.yaml` ile aynı. K10–K12 sonar trig, pin haritasıyla aynı. K13–K15 boş.
- **Güç dalları ve acil stop:** 74 kablonun hepsinde dal, koruma ve `acil_stopta_enerjili` değerleri elle KOK §12 (KOK:351-363) ile karşılaştırıldı, hepsi uyumlu.
  - Enerjili kalanlar: G20 / G21 (F6 göğüs ekranı), A01, F3 / F4 dalları, akü ölçümü, şarj kolu.
  - Enerjisiz olanlar: A02–A06, G22, anahtarlı bara arkası.
  - Ana anahtar / röle öncesi-sonrası ayrımı doğru.
- **Rastgele 16 kablo** (tohum 1411): M01, G04, K02, G08, SV3, S04, A04, U05, G10, SV1, M02, H01, S01, G21, M03, Q01. İki ucu ve kaynak alanındaki satırlar açılıp okundu; satırların hepsi gösterilen içeriği taşıyor.
- **Kesit ↔ koruma kuralı kaynaktan:**
  - 33 CFR 183.425 Table 5, 80 °C sütunu: 18 AWG 15 A, 16 AWG 20 A, 12 AWG 35 A. 183.455(c)(1): 50 V altında sigorta tablodaki akımın %150'sine kadar olabilir.
  - NFPA 79 (2018) Table 12.5.1, 30 °C, 75 °C sütunu: 24 / 22 / 20 / 18 / 16 / 14 / 12 AWG = 2 / 3 / 5 / 7 / 10 / 20 / 25 A. Kaynaklar okundu.
  - Ajanın tablosu (12 AWG 25, 16 AWG 10, 18 AWG 7, 20 AWG 5, 22 AWG 3, 24 AWG 2 A) iki kaynağın küçüğü olarak doğru. 12 V akülü bir robot için temkinli ve uygun.
- **Kararların kendisi:**
  - `ana-hat-12awg` (12 AWG + 30 A): CFR'de 35 A, NFPA'nın 90 °C sütununda 30 A. Kabul edilebilir; sigortayı 25 A'ya indirmek gerekmiyor.
  - G11 itirazı doğru: kol, K1 kapalıyken baradan F1 20 A üzerinden beslenir, bu yüzden 12 AWG.
  - G22 itirazı (hazır PC817 modülü, direnç yerine 2 A sigorta) kabul edilebilir.
  - Şarj kolu G06: sigorta akü tarafında 10 A, + ucu ana sigortanın yük tarafında. BMS'li akü için doğru. Şarj akımının ana sigortadan geçmesi sorun değil.
  - Sarı pabuç: JST R5.5-5, 12–10 AWG (2,6–6,6 mm²) için yapılmış, 5 mm saplamaya uyuyor. "12 AWG'yi tutmama" riski büyük ölçüde gerçek değil. Satıcı sayfası (ISISO RV 5.5-5) aralığı açıkça yazmıyor; teslimde bir deneme sıkışı yapılsın.

### 3.2 Elektriksel tutarlılık (madde 2)

- Tabloda aynı pin ya da klemens iki işe verilmemiş. Bugünkü tabloda dönüşü eksik güç kablosu ve 5 V Pi / çevre karışması bulmadım. Bunu elle taradım; denetimin bunları görmediği D1'de.
- Boy: 17 kablo CAD'den (KJ kaynak alanı `montaj-analiz.json`, `lale158-kontrol.json`, `dirsek-analiz.json` anahtarlarına gidiyor, denetimin `kaynak_coz`'u bunları çözüyor), 57 kablo tahmin. Tahmin kuralı (Manhattan × 1,25, 50 mm'ye yukarı yuvarlama; EL:70) makul. %30 sipariş payı kısa ve ölçülmemiş boylar için yeterli.

### 3.3 62 ile mutabakat (madde 3)

60 döküm satırı eşleniyor: #5 birleşti, #53 gerekçeli çıktı. Çoklu eşlenen satırlardan 22 kablo, tekli satırlardan 49 kablo, artı 3 yeni = 74, tutuyor. X01 iki ayrı kart arasında, gerçekten ayrı bir kablo. AU2 tartışmalı (§2-16). "#40 + #48 + #49 → Q01–Q03" birleşme değil, üç satırın üç kayda yeniden bölünmesi; ifade düzeltilebilir. Sayılar tablo, `kablolar.md` başlığı, GN ve `dongu-158.md`'de aynı: 74 kablo / 175 damar / 33 kesin, 40 teyit, 1 karara bağlı.

### 3.4 Denetim ve görünüm (madde 4)

- KD gerçek depoda çıkış 0. `--bozma-denemesi` 31 / 31. Kendi bozmalarım D1'de.
- `kablolar_uret.py --kontrol` çıkış 0: "kablolar.md ve elektrik.md bloğu güncel". Bu kontrol yeniden üretimi dosyadakiyle karşılaştırıyor. Kendi kopyamda yeniden üretim de aynı dosyayı verdi; B13'te elle bozulan görünüm yakalandı.

### 3.5 `maliyet.json` (madde 5)

- **Fark:** 153 → 163 satır; değişen indeksler 19, 41, 42, 57–61, 69, 72, 78–80, 83–86, 90, 91, 96–98, 101, 147; yeni 153–162. Başka satıra dokunulmamış. JSON geçerli.
- **Toplamlar** (kendi toplamam ve `maliyet_toplam.py` aynı):
  - Eski: 118.666,22 / koşullu 124.573,11.
  - Yeni: **120.838,07 / koşullu 126.409,54**.
  - Fark genel +2.171,84. Ajanın "−89,05 + 2.260,90" ayrıştırması tutuyor. V3 kalem sayısı 129.
- **Fiyatsız 4 kalem** (USB-A uzatma, L 3,5 mm kablo, bara saplaması, sinyal teli) dosyanın önceki "fiyat_bekliyor" kalıbına uyuyor.
- **Bağımlılar:** `README.md:50` ve `proje-plani.md:10-11` ≈ 120.800 / ≈ 126.400. `sonuc-rapor.html` data-j değerleri 120.838,07 / 126.409,54 / 95.942,32 / 104.242,96. Demo sayfasındaki gömülü maliyet kopyası MJ ile birebir aynı.
- **Doğrulamalar:**
  - F9b GEÇER, 0 hata. Kendi açtığım ayrı profilli başsız tarayıcıda 1400 ve 360 px'te konsol hatası 0.
  - F9c 28 hata; hepsi kuyruk / rapor sayıları ve K1 / K10 / K11 / K14 / K53–55 / K58 ile ilgili, maliyetle ilgili hata yok.
  - F9d 0.
  - `testler_html.py --kontrol` geçti.
- **Miktarlar** (tablodaki boy × damar × 1,3, kendi sayımım; liste miktarı parantez içinde):
  - 12 AWG: kırmızı 4,55 m (5), siyah 2,08 m (3).
  - 16 AWG: kırmızı / siyah 4,03 m (5 / 5).
  - 18 AWG: kırmızı 10,46 m (11), siyah 8,90 m (9).
  - 20 AWG: 0,26 m (1 / 1).
  - Sinyal teli (`sinyal-22` kayıtları): 26,95 m × 1,3 ≈ 35 m (3 × 15 m rulo). Hepsi yeterli, şişkin kalem görmedim.
  - Servo uzatma: bakılan 5 servo kablosunun gerekli boyu 1,55–1,75 m. 1 m'lik uzatmadan ikişer gerekir → 10 kablo için 20 adet; 23 adet, 3 yedekle tutarlı.
- **Web fiyat doğrulaması** (14.11'de satıcı sayfaları açıldı):

| Kalem | Sayfada görülen | Sonuç |
|---|---|---|
| Hat sigortası yuvası (Motorobit) | "Mini/Micro", 16 AWG, en çok 20 A; 30,90 + KDV = 37,08; stok 100+ | Tutuyor |
| 2 A mini (Motorobit) | "Mini Alçak Profil", 10,9 × 8,73 mm; bugün 7,42 TL | Listede 7,34 (09.11 fiyatı, notlu); fark 0,08 TL |
| 2 A / 3 A standart (Motorobit) | Standart bıçak, 19,1 × 18,7 mm; 3,61 + KDV = 4,33 | Tutuyor (URL'de "maksi" yazıyor ama ürün standart) |
| 30 A ana sigorta | Standart, 19,1 × 18,7 mm | Tutuyor; kutu F1–F6 ve ana sigorta standart, hat yuvaları mini. Sigorta tipinde karışıklık yok |
| BC337-40TA (Direnc.net) | TO-92, 45 V, 800 mA, ON Semi (Fairchild); 2,52 + KDV = 3,02 | Tutuyor; stok adedi sayfada yok |
| Sarı pabuç RV 5.5-5 (ISISO) | 41,20 + KDV = 49,44 / 10'lu | Fiyat tutuyor; kesit aralığı sayfada açık değil |
| Göğüs HDMI (Robotistan) | 97,99 + KDV = 117,59, "Tükendi", HDMI 1.4 | Fiyat tutuyor; çap ve fiş ölçüsü sayfada yok, Ø ≤ 6 mm şartı doğrulanamadı |

### 3.6 Belgeler ve tasarım değişikliği (madde 6)

- Ajan devre tasarımını değiştirmemiş. Pin, direnç ve sigorta değerleri PH sürüm 4 ve KOK kararlarıyla aynı.
- Kesitler orkestratörün O-1 / O-2 kararıyla yazılmış.
- EL'deki eski pinler (EL:106, :114, :143, :458-459, :483-484, :496) tarihçe olarak işaretli.
- `yazilim-plani.md`, T13:64, :81 ve T4:72 GPIO4'e düzeltilmiş.
- Kalanlar §2-8, -9, -12'de.

### 3.7 Sınırlar (madde 7)

- `git status` ve `git diff 9a0c6fe --stat` ile bakıldı: `rehber/`, `planlama/rehber/` ve `kod/` altında değişiklik yok.
- `tasarim/freecad/` altındaki değişiklikler yalnız brief'te bu paketten olmadığı söylenen 13 PNG ve `montaj/yerlesim-kontrol.json`.
- Demo farkı yalnız K11 göstergesi (`demo_uret.py` KARARLAR listesinden K11 çıktı, `viewer-template.html`'de düz metin "kutunun F6 yuvası (K11 a)") ve gömülü maliyet verisi. Sayfa açılıyor, konsol hatası yok (F9b).

### 3.8 Gizlilik (madde 8)

- **Yöntem:** Paketin eklediği bütün satırlar tarandı (`git diff 9a0c6fe` ile eklenen satırlar + izlenmeyen 5 yeni dosyanın tamamı, ≈ 10.300 satır). Aranan kalıplar: yerel kullanıcı yolu, sürücü harfli yollar, kullanıcı klasörü, bulut klasörü, geçici klasör, takma ad, soyad, e-posta, depo dışı dökümün adı.
- **Sonuç:** Bulgu yok. Tek eşleşmeler sonar pininin "Echo" adı.
- Paket T7:127 ve testler.html'de soyadı kaldırmış. GN:350, tam adın daha önce depoda olan 39 dosyada / 84 satırda geçtiğini kaydediyor; bu satırlar paketten eski, bu pakette eklenmiş değil.
- Anahtar ya da parola görülmedi.

### 3.9 "Orkestratöre" listesi (madde 9)

O-1…O-18 gerçek karar soruları ve seçenekleri dürüst yazılmış. GN §12'de uygulanamayanlar (O-3 a, O-5 G22, O-16) açıkça işaretli. Ajanın kendi başına verip orkestratöre getirmesi gereken seçimler:
- (a) Kafa servo hattında "dağıtım kartı C". O-8 kol yönteminin kafaya genişletilmesi; EL:129'la çelişiyor.
- (b) Köprülü saplama kuralı ve saplama başına 5 pabuç sınırı (§2-1).
- (c) 1N4007'nin yeri.
- (d) Renk kuralı (+ kırmızı, − siyah; KJ:31). Listedeki kablolar yalnız iki renk olduğu için zorunlu ve makul, ama yine karar listesinde anılmalı.

### 3.10 C adımı listesi (madde 10)

- Commit'e girecekler: `git status`'taki değişen dosyalardan 13 PNG ve `yerlesim-kontrol.json` hariç hepsi, 5 yeni dosya ve bu rapor. GN §15'teki `dongu-158.md` ve `karar-kuyrugu.md` kayıtları içerik olarak tam.
- Eksikler:
  - (a) D1 ve D2'nin düzeltmesi.
  - (b) GN:374'teki "F9c 28 hata, P10.7a öncesiyle aynı küme" cümlesi bu kontrolde doğrulanamadı (aşağıda). C adımında ya ölçülsün ya da "ölçülmedi" diye yazılsın.
  - (c) GN:378'deki P10.7b listesine §2-2, -3, -4 ve -10 eklensin.

## 4. Bakılmadı

- F9c'nin paket öncesindeki (HEAD) hata kümesi. HEAD kopyasında betik `git log` istediği için koşmadı (çıkış 128); "aynı küme" iddiası bağımsız doğrulanamadı.
- Web'de bakılmayan satırlar: servo uzatma, 12 AWG (Robocombo), 16 / 18 / 20 AWG, mavi ve kırmızı pabuç, jumper, 5,08 mm klemens, USB 2.0 uzatma.
- 5,08 mm klemensin aldığı kesit.
- XL4016 modülünde ayarlanabilir akım sınırı bulunup bulunmadığı; kısa devre davranışı (tezgâh işi).
- Motor kablosunun gerçek kesiti (motor yok).
- Servo uzatma ihtiyacında 10 kablonun 5'inin boyuna bakıldı; öbür 5'i sayılmadı.
- Boyların hiçbiri ölçülmedi (ajan da ölçmedi).
