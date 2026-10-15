# M1: kol kablo yolu (düzeltme planı 2. adım, KRİTİK; tasarım ajanı)

Başlangıç: 14 Ekim 2026, akşam. Git commit yok; tam çakışma taraması ve ana montaj koşulmaz (6. adım).
Dokunulabilir: `arayuz.py`, `dirsek/`, `omuz/` (`omuz_baski.py` hariç), `kabuk/`. Omuz parçalarını aynı anda M4 ajanı okuyor: omuz geometrisi değişirse hangi parça değişti aşağıda net yazılır.

## Durum
- [x] 1 Mevcut geometri ve sorunun doğrulanması
- [x] 2 Gerçek kablo demeti ölçüleri (kaynaklı)
- [x] 3 Seçenekler + seçim
- [x] 4 arayuz.py kablo kaydı (`KOL_KABLO`)
- [~] 5 Geometri: dirsek (oluk, çentik, tırnak) ve omuz (tüp penceresi) **yapıldı**; kabuk (Ø84 halka payı) + S1 geçişi **AÇIK, karar gerekli** (aşağıda "S1 sonucu")
- [x] 6 Kalıcı kablo kontrolü (dirsek + S2 lopları, sabit yollar, geçitler, boy); S1 kısmı karar sonrası
- [x] 7 Yeniden üretim + kontroller (omuz, dirsek, kabuk)

## Günlük
- Okundu: omuz_parcalar.py. Kol çatalı (omuz, sağ yerel): iki plaka (z 25,5…30,5 horn tarafı, z −33…−28 rulman tarafı) + köprü (x 165…205, y −34…−28, z −33…30,5) + yaka r28 (y −34…−40) + **dolu pim r25,4 (y −40…−60)**. Tüp r28/25,65, y −40…−140; pimde 2× M3 (y −50, ±Z). Köprünün üstünde plakalar arasında S2 servosu: tüpün üstü tamamen kapalı. Doğrulandı.
- Okundu: dirsek_parcalar.py. Ön kol başı R21 (dirsek ekseni y −173), çatal köprüsü alt yüzü y −148 → 4 mm (doğrulandı). Dirsek servosunun kablosu servonun **üst** ucundan (mil ucu, y −162,8, taban tarafı x ≈ 182) çıkıyor; bilek servosunun kablosu mil ucundan (iç yan, x ≈ 174,8, y ≈ −221). Çatalın Ø10 kablo deliği doğrudan başın üstünde: kablo bu yoldan giderse dirsek bükülünce başla köprü arasındaki 4 mm'de ezilir. Bilek kablosunun yukarı çıkışını ara duvar (y −215…−212,5, tam genişlik) kesiyor.
- Okundu: kabuk omuz deliği: Ø84 + baskı için 45° damla ucu aşağı (tepe eksenden 59,4 mm aşağıda); rulman kapağı (sabit, r30, x 146…160) kulakları ±Z'de (|y| ≤ 12, r ≤ 39,9) halkanın içinde. S1 eksenini servo, horn ve rulman dolduruyor: eksen içinden geçiş yok.

### Kablo ölçüleri (kaynaklı)
| Ölçü | Değer | Kaynak |
|---|---|---|
| MG996R kablo boyu | 300 mm, 3 pin "S" (JR/Futaba) dişi | Tower Pro MG996R datasheet (electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf) |
| DS3218 kablo boyu | 300 ± 5 mm, JR 3 pin 2,54 | DSServo DS3218 PRO datasheet (itgresa.com/.../DS-Servo-20kg-DS3218-PRO-datasheet-PDF.pdf) |
| Kablo çıkışı | iki serviste de mil ucundaki kısa yüz, tabana yakın (≈ 5 mm, çizimden okuma, tahmini) | aynı datasheet çizimleri |
| Uzatma kablosu | 22 AWG, 3 damar düz, 60 tel; iletken 0,34 mm² | Pololu 780/785 özellikleri; Maplin Futaba 22AWG |
| Düz kablo kesiti | 4,2 × 1,4 mm (damar dış çapı ≈ 1,4: 0,66 mm iletken + PVC; **tahmini, kumpasla ölçülmeli**) | hesap |
| JR dişi gövde | 7,9 × 2,75 × 14,0 mm | Pololu 1924 ölçü çizimi |
| JR erkek gövde (uzatmanın erkek ucu) | 10,3 × 4,0 × 18,0 mm | Pololu 1925 ölçü çizimi |
| Eşleşik bağlantı (erkek + dişi) | 10,3 × 4,0 × ≈ 26 mm | tahmini (18 + dişinin dışarıda kalan ~8 mm) |
| En küçük bükülme yarıçapı | dinamik 10 × kalınlık = 14 mm; sabit 5 × kalınlık = 7 mm (yassı kablo ince yönünde bükülür) | muhafazakâr kural; Helukabel örneği sabit 4×d / dinamik 7,5×d, Lapp: sabit döşemede daha küçük yarıçap serbest |

### Seçenekler
| # | Yol | Artı | Eksi |
|---|---|---|---|
| A | Kablolar dışarıdan, spiral kılıfla gevşek halka (dirsek raporundaki geçici öneri) | geometri değişmez | 4 mm aralık ve kabuk kenarı kontrolsüz; bükülme/ezilme kanıtlanamaz; kol kabuğa 7 mm yakın |
| B | Omuz pimini ve köprüyü delip kabloyu S2 ekseni boyunca geçirmek | kablo eksene yakın | S2 ekseninde servo + 625ZZ + M5 dolu; servo gövdesi kesilemez; büyük omuz değişikliği |
| C | **Arka yol, üç serbest lop:** dirsekte köprü altında arka oluk + başın arkasında lop; tüpte arka pencere; S2'yi çatal arka plakasının arkasında lopla geç; göbekte iç kanal; S1'i kabuk dış yüzüyle göbek arasındaki 11 mm boşlukta düzlemsel lopla geç; Ø84 deliğin alt damla ucundan gövdeye gir | her eklemde kablo eksene yakın ve bükülmenin dış tarafında (gerilmez, ezilmez); yassı kablo lop düzleminde kendiliğinden kalır (kenar yönünde rijit); yalnız malzeme çıkaran küçük kesimler; Ø84 damla ucu zaten var | üç lop dışarıdan görünür (dirsek arkası, omuz arkası, omuz yanı); kablo bağı yerleri eklenmeli |
| D | Kablo kasası (saat yayı) S1 için yeni parça | çok düzenli | yeni parça + kapak, en çok geometri |
Seçim: **C** (en az geometri, çakışma imkânı yalnız ölçülerek; yeni parça yok). Ayrıntılar ve ölçümler aşağıda hesaplandıkça.

### Kablo modeli ve ölçüt (günlük, 14 Ekim akşam)
- Serbest kablo bölümü (lop) modeli: **düzlemsel ayrık elastika** (sabit boy L, iki uç konumu ve uç teğeti kelepçeyle sabit, bükülme enerjisi en az; 100–160 parça, SQP). Yassı kablo lop düzleminde kalır (kenar yönünde rijit), düzlem dışı küçük kayma 3B kontrolde doğrusal/yumuşak geçişle verilir. Bezier denendi, uzun lopta sivri uç (cusp) ürettiği için bırakıldı.
- Bükülme ölçütü: başta kaynaksız 10 × kalınlık (14 mm) yazmıştım. Kaynaklı değere geçtim: **dinamik 7,5 × d = 10,5 mm, sabit 4 × d = 5,6 mm** (Helukabel örnek kablo, d = şerit kalınlığı 1,4). Gerekçe yalnız kaynak; tasarım bunun üstünde pay bırakacak şekilde seçildi (aşağıda). Standart PVC servo kablosu sürekli esneme sınıfı değil: açık risk, öneri silikon yalıtımlı çok telli uzatma.
- Arama sonuçları (2B hızlı tarama, sonra 3B FreeCAD kontrolü):
  - Dirsek: kelepçe M ön kolda cebin üstünde (eksenden dy 16,5, dz −6, kablolar geriye çıkar), F çatal köprüsü altındaki oluğun arka ağzı (eksenden 28,1 yukarı, 31,5 geri, kablo öne girer), **L = 110** → dirsek 0…105° boyunca R_min ≈ 12,8 mm, kiriş 24,7…41,8 mm. (L 80'de 10 mm altına iniyordu.)
  - S2: K çatal arka plakasında (S2 ekseninden 8 dış, 26 aşağı; z −35,6, kablo plakanın arkasında yan duruşta), G2 göbek iç şeridinde (x 163…168, eksenden 19,5 iç, 15 aşağı), **L = 80** → yana 3…120° boyunca R_min ≈ 12,3 mm. Çatal arka plakası S2 ekseninin iç-üst çeyreğine hiç girmez (rel x ≥ −16): G2 bu yüzden orada.
  - S1 (−45…135°, 180°): serbest düzlemsel lop ancak eksenden ~100 mm'ye taşarak çözülüyor (kabul edilmedi). Eksen çevresinde **tek tur gevşek spiral (saat yayı ilkesi)** R_min ≈ 38 mm veriyor ama gövdesiz spiral uç pozda r ≈ 90'a şişiyor. Seçim: spirali **kabuk omuz pedine eklenen 45° konik halka dudağı (r 52→61, x 152…161)** ile sınırlamak = "Ø84 delikte kablo halkası payı"; iç sınır rulman kapağı (r 30). Spiral düzlemi x ≈ 157,5 (kabuk ped yüzü 152 ile göbek kutusu 163 arası); bu dilimde yalnız sabit kapak (r ≤ 30) var, göbek ve kol parçaları x ≥ 163.
- Yassı kablo yönü: yolun her noktasında şerit genişliği eğrinin binormaline (lop düzlemine dik) döner; sabit bölümlerde ≥ 15 mm boyunca serbest burulma kabul edildi (yassı kablo kolay burulur).

### S1 sonucu (DUR: karar gerekli)
- Spiral/halka fikri geometride çöktü: yana küçükken (3…~20°) **üst kol tüpü ve yakası kabuk ped yüzünden yalnız 5–8 mm uzakta** (tüp iç yüzü x ≈ 157–160, kabuk ped x 152; A2'nin "kol ↔ kabuk 7,17 mm" ölçümüyle aynı yer). Bu yüzden S1 ekseninin **alt sektörü (y < −34, |z| < ~12) x 152…163 dilimini dolduruyor**; ekseni saran her halka/spiral/kaset buradan geçmek zorunda. Gövde içi de olmaz: S1 servosu, horn, 6808 ve yuva blokları eksen çevresini r ≈ 32'ye kadar dolduruyor, kabuk üst kapağı eksenin yalnız 30 mm üstünde.
- Denenen serbest loplar (elastika, R ≥ 10,5 + demet payı, kapak r 30 ve tüp sektörü engel):
  | Yerleşim | Sonuç |
  |---|---|
  | Göbek alt-arka (r 35) → Ø84 damla ucu (r 46), düzlemsel lop | uygun çözüm yok; R ≥ 13 için lop eksenden ~105 mm'ye taşıyor |
  | Aynı uçlar, 1 tur spiral (gövdesiz saat yayı) | R ≈ 38 ama uç pozda r ≈ 80–90'a şişiyor ve tüpün sektöründen geçiyor (yana küçükken çarpar) |
  | 2 tur spiral, L 600 | r 34…61, yine tüp sektöründen geçiyor + katlar üst üste biniyor |
  | G göbek üstünde (tüpün tam karşısı, hep 180° uzak), J kabuk ped üst-arka, yalnız üst yarıda lop | en iyi R 10,2 mm (< 10,5 sınır), lop eksenden ~95 mm'ye taşıyor, kontrolsüz |
- Sağlam çözüm için **yeni parça gerekiyor** (en az geometri ilkesinin dışında, karar Duffy/orkestratörün):
  1. **Kablo kaseti (yuvarlanan U lop):** göbeğe bağlı ince tambur halkası (r ≈ 31,5–33, x 153…161, rulman kapağını 1,5 mm boşlukla sarar) + gövdeye bağlı üst-arka yay duvarı (r ≈ 61–64, tüpün hiç girmediği ~145° sektörde). U yarıçapı ≈ (61 − 33 − 4,2)/2 ≈ 12 mm ≥ 11,2; S1 180° dönünce U ≈ 90° kayar, sektöre sığar (125° < 145°, pay az). Tambur halkası göbekte (M4'ün baskı analizindeki parça) değişiklik, yay duvarı yeni baskı parçası + kabuk üst kapağına bağlantı.
  2. **Omuz üstü büyük serbest lop** (G göbek üstü, J üst kapak/arka): ek parça yok ama R ≈ 10 (sınırın altı), lop omuzdan ~95 mm dışarı taşıyor, kontrolsüz.
  3. **S1 aralığını daraltmak** (yazılım): 180° → ör. 120° olursa serbest lop küçülür; bu bir kinematik/jest kararı, ölçülmedi.
  4. Kabloyu S1'de ayırmak (S1 ekseni yakınında konnektör + kayar halka): servo akımı (3 servo × 2,5 A tepe) ve eksenin dolu olması nedeniyle önerilmez.
- Önerim: **1 (kaset)**, kabuk üst kapağına vidalanan tek yay parçası + göbeğe eklenen tambur halkası. Karar gelirse aynı kontrol çerçevesiyle (kablo_yolu.lop_coz + duvar modeli) doğrulanabilir.
- Uygulanmadı: kabukta (Ø84 delik / halka payı) **hiçbir değişiklik yapılmadı**; göbeğe kablo bağlama yeri (G2) yalnız arayüzde tanımlı, göbek geometrisi değişmedi.

### Uygulanan geometri (dirsek + S2 geçişi)
| Parça | Değişiklik | Kütle |
|---|---|---|
| Dirsek çatalı (dirsek/) | köprü + alın kapağı altına oluk x 182…188, y −148…−143,5 (4,5 derin), Ø10 delikten kapağın arka kenarına (z −34); kablo burada sıcak tutkal noktası | 88,21 → 87,49 g |
| Ön kol gövdesi (dirsek/) | ara duvarın arka kenarına bilek kablosu çentiği (x 176,5…182,5, 5 mm); yanağın üst-arka köşesine kablo tırnağı (x 172,5…176,5, eksenden dy 10,5…16,5, dz −19,5…−13; baskıda yukarı yönlü, desteksiz) | 42,12 → 42,18 g |
| **Üst kol tüpü (omuz/)** | arka duvarda kablo penceresi: x 180…190, y −89…−65 (14 mm düz + iki ucu 45° sivri: dik baskıda desteksiz) | 30,1 → 29,8 g |
| Kol çatalı (omuz) | **değişmedi** (K noktası: arka plakanın arkasına yapışkan tabanlı kablo bağı yuvası) | — |
| Göbek, rulman kapağı, yuva, kabuk | değişmedi | — |
- Dayanım: pencere tüpün arka (≈ nötr değil, öne kaldırmada en çok gerilen) lifinde; 0,5 kg el yüküyle eğilme momenti ≈ 1,8 N·m → kesit (Ø56/51,3 PETG) gerilmesi ≈ 0,4 MPa (penceresiz ≈ 0,35), PETG akma ~50 MPa: ihmal edilebilir. Pencere kelepçe bölgesinden (y −115…−140) ve tüp M3 cıvatalarından (y −50) uzak; kelepçe işlevi değişmedi (dirsek kontrolü: kelepçe kapanma 0,637 ≥ 0,6, 22/22 bağlantı). Oluk çatalda yalnız köprünün alt 4,5 mm'sini 6 mm genişlikte kaldırıyor; köprünün üstündeki pim/bilezik kök bölgesi sağlam. Baskı analizi: çatal 0,037 / ön kol 0,007 çıkıntı oranı, destek sorunu 0.
- **M4 ajanına not:** omuz parçalarından yalnız **Üst kol tüpü** değişti (pencere); `omuz-montaj.FCStd` 14 Ekim akşamı yeniden üretildi. Kol çatalı, göbek, yuva, rulman kapağı aynı.

### Kalıcı kontrol (dirsek_montaj.py → dirsek-analiz.json "kablo"; modül: dirsek/kablo_yolu.py, tanım arayuz.KOL_KABLO)
| Kontrol | Sonuç | Şart |
|---|---|---|
| Dirsek lopu (dirsek 0…105°, 2,5° adım, 43 poz), L 120 | R_min **12,95 mm**, en dar boşluk **0,61 mm** (ön kol, 105°), kiriş 20,7…52,7 (< L) | R ≥ 11,2 (7,5 d + demet payı), boşluk ≥ 0,5 |
| S2 lopu (yana 3…120°, 3° adım, 41 poz; S1 −45…135 kabuk/kapak/yuva dahil), L 80 | R_min **12,36 mm**, en dar boşluk **1,57 mm** (kol çatalı, 3°), kiriş 31,3…52,2 | aynı |
| Sabit: dirsek servosu → tırnak | köşe R ≤ 5,8 sığar, boşluk 1,78 | R ≥ 5,6, boşluk ≥ 0 |
| Sabit: bilek servosu → çentik → tırnak | köşe R 5,8, boşluk 0,70 | aynı |
| Sabit: oluk → Ø10 → tüp içi | köşe R 22,9, boşluk 0,00 (oluk tavanına yaslanır, tasarım gereği) | R ≥ 6,3 |
| Sabit: tüp içi → pencere → tüp/yaka/köprü arkası → K | köşe R 7,1, boşluk 0,23 (tüp yüzü) | R ≥ 6,3 |
| Geçit | Ø10 delik − dişi JR köşegeni 8,36 = 1,64 mm; pencere dişi JR (7,9 × 2,75) geçer; tüp içinde iki eşleşik JR (10,3 × 8 × 26) sığar | — |
| Boy | dirsek servosu tüp içine 197,6 mm'de ulaşır (300'den 102 artar, tüp içinde toplanır); bilek servosu 267,1 mm (32,9 artar) | artan ≥ 10 |
| Uzatma | birleşim → G2: 175,7 mm; S1 + gövde içi + PCA9685'e (~967 mm, taban YOL) **açık** | — |
- Dirsek serbest aralığı (bilgi): −60…110 → −40…110 (tırnak, yazılım aralığı 0…105 dışında, eksi yönde çatala erken değiyor). Bükülme boşluğu 105°'de 4,19 mm (değişmedi).

### Yeniden üretim (14/15 Ekim gecesi)
| Modül | Koşu | Sonuç | Parça / kütle önce → sonra |
|---|---|---|---|
| dirsek | `dirsek_montaj.py` 56 s + `dirsek_rapor.py` | geçersiz 0, ev pozu çakışma 0, omuz arayüzü 0, bağlantı 22/22, kelepçe OK, baskı 4/4 destek sorunu 0, **kablo kontrolü OK (S1 açık)** | 53 / 368,7 g → 53 / 367,4 g (çatal −1,29: G yarığı −0,57 + oluk −0,72; ön kol +0,06) |
| omuz | `omuz_montaj.py` 39 s | statik çakışma 0, M6 4/4 (1,7 / 0,8), tarama sayıları aynı (yalnız kol×gövde hacimleri −1 mm³: pencere), tork ±0,01 | 66 / 848,49 g → 66 / ≈ 848,2 g (Üst kol tüpü 30,1 → 29,8 g) |
| kabuk | `kabuk_montaj.py` 8 dk (geometri değişmedi; G madde 4) | geçersiz 0, kabuk içi çakışma 0, iskelet 0, bindirme 0,1881 (21 çift), baskı 15/15 destek sorunu 0, **cam–duvar 0,102 mm geometriden** (omuz/göğüs bandı) | 194 / 4886 g (aynı) |
- `omuz/omuz_baski.py` **koşulmadı** (koordinatör koşturacak). Değişen omuz parçası yalnız **Üst kol tüpü** (arka pencere); `omuz-montaj.FCStd` 14 Ekim ~23:47'de yeniden üretildi. Kol çatalı, göbek, yuva, rulman kapağı değişmedi.
- Koşulmayan: `carpisma.py` / `carpisma_kos.py` (C7), ana montaj, görseller (GUI). Kablo lopları dirsek arkasında (eksenden ~60 mm'ye kadar) ve omuz arka plakasının arkasında: C7 taramasında kablo yoktur (Referans çizilmedi); 6. adımda isterseniz lop örnek noktaları `dirsek-analiz.json` → `kablo.*.ornek_nokta`.

### Açık işler (başkasının dosyası ya da karar)
1. **S1 geçişi** (yukarıda): kaset önerisi; karar sonrası göbek tambur halkası + yay duvarı + kabuk bağlantısı + kontrol genişletmesi.
2. Uzatma kablosu boyu S1 kararına bağlı: birleşim → G2 175,7 mm + S1 (~150–250, tahmini) + gövde içi (~100) + PCA9685'e 967 mm ≈ **1,4–1,5 m / servo** (iki kol 4 adet); DS3218 (S2) kablosu göbekte birleşir. `maliyet.json` B1 (servo uzatma ~8 m) buna göre güncellenmeli; öneri: 22 AWG silikon çok telli, uca JR sıkılmış özel boy.
3. BOM/maliyet: yapışkan tabanlı kablo bağı yuvası (K noktası, kol başına 1) + 2,5 mm kablo bağları + sıcak tutkal; dirsek tırnağında kablo bağı.
4. `baski-listesi.md`: Üst kol tüpü ve dirsek çatalı/ön kol geometrisi değişti (M1); tüp ve kol çatalı artık S1 kararı beklemeden basılabilir mi kararı orkestratörün (tüp penceresi S1 çözümünden bağımsız).
5. Kablo kesiti (4,2 × 1,4) tahmini: gerçek uzatma kablosu kumpasla ölçülüp `KOL_KABLO["serit"]` güncellenmeli, dirsek_montaj yeniden koşulmalı (kontrol kendiliğinden yeniden değerlendirir).
