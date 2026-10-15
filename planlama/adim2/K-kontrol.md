# K: Tasarım ajanının (G + M1) işinin bağımsız kontrolü

Ajan: analiz ve bağımsız kontrol (tasarım değiştirmez). Başlangıç: 15 Ekim 2026. HEAD = `25de259`.
Yazılan dosyalar: bu günlük (`planlama/adim2/K-*`), ölçüm betikleri `K-olcum.py`, `K-s1.py`, `K-regresyon.py` ve çıktıları `K-olcum.json`, `K-s1.json`, M4 günlüğü, `omuz/omuz-baski.json`.

## İlerleme
- [x] Günlük açıldı
- [x] Kaynaklar okundu (G-takip, M1-kablo-yolu, kablo_yolu.py, arayuz KOL_KABLO / DIRSEK, git diff)
- [x] 1. Değerlerin geometriden yeniden ölçülmesi
- [x] 2. Regresyon (analiz JSON'ları HEAD ile)
- [x] 3. Baskı: omuz_baski.py yeniden koşu (tüp)
- [x] 4. S1 (Ø84) seçenek değerlendirmesi

## Yöntem
- Ölçümler yeniden üretilmiş FCStd'lerin geçici kopyasından yapıldı; ajanın JSON'undaki sayılar kullanılmadı. Kullanılan dosyalar:
  dirsek 14.10 23:46:56, omuz 23:48:08, kabuk 23:56:48, iskelet 22:41:40.
- Betikler (yeniden koşulabilir, yalnız okur):
  - `planlama/adim2/K-olcum.py` → `K-olcum.json` (441 s)
  - `K-s1.py` → `K-s1.json`
  - `K-regresyon.py` (sistem Python'u; analiz JSON'larını git sürümüyle karşılaştırır)
- Kablo lopları için ajanın çözücüsü (`kablo_yolu.elastika`, Gauss-Newton, N 120) kullanılmadı. Bağımsız bir çözücüyle yeniden çözüldü:
  scipy SLSQP, N 150, ilk pozda dal seçimi enerjiyle, sonra süreklilikle. Boşluk FCStd parçalarına ölçüldü; S2 lopunda gerçek kabuk
  (omuz + göğüs bandı sağ, S1 −45…135, 15° adım) da hesaba katıldı. Ajan yalnız düz referans duvarı kullanmıştı.

## 1. Değerlerin yeniden ölçülmesi

| Kontrol | Ajanın değeri | Benim ölçümüm (geometriden) | Sonuç |
|---|---|---|---|
| Bilezik yarığı | 4,0 | 4,000 mm (y −118 / −127 / −136 kesitlerinde düz kenarlar x 183 / 187; iç yay boşluğu 4,003) | ✔ |
| Kapanma | 0,637 | 4,000 / 2π = 0,6366 mm | ✔ |
| Toplam radyal boşluk | 0,5 | bilezik iç r 28,25 − tüp dış 28,00 = 0,25; tüp iç 25,65 − pim 25,40 = 0,25 → 0,50 | ✔ |
| Kalan ön yük (≥ 0,1) | 0,137 | 0,1366 mm (düzgün kapanma varsayımıyla) | ✔ ama aşağıdaki çekince |
| Omuz M6: kanal tabanı / somun geçme (≥ 0,5) | 0,8 / 1,7 | ışın izi 0,8 / 1,7 (4/4; ilk kesişim omuz traversi) | ✔ |
| İskelet köşe M6: somun geçme / taban | 0,6 / 1,9 | 0,6 / 1,9 (8/8) | ✔ (en ince pay 0,6) |
| (ek) Kabuk M6 braketleri | — | somun geçme 1,1–1,7, taban 0,8–1,4 (14/14) | ✔ |
| Kabuk cam–duvar (≥ 0,05) | 0,102 | yalnız cam (Nextion'dan PCB katmanı ayrıldı) ↔ omuz ve göğüs bandı: 0,1022 | ✔ (PCB göğüs bandının boss'larına 0,0 ile oturuyor; montaj gereği) |
| Dirsek lopu (L 120, 0…105°) | R 12,95 / boşluk 0,61 | R_min **13,03** (105°), boşluk **0,61** (ön kol, 105°), toplam dönüş −180…−285° | ✔ (sınır 11,2) |
| S2 lopu (L 80, 3…120°) | R 12,36 / boşluk 1,57 | R_min **12,39** (120°), boşluk **1,57** (kol çatalı, 3°); gerçek kabuk dahil değişmedi | ✔ |
| Ø10 kablo deliği ← dişi JR köşegeni 8,37 | 1,64 | Ø10,000 → pay 1,635 | ✔ |
| Tüp penceresi | JR geçer | pencere x 180…190, y −89…−65; 10,0 genişlik, JR + 0,5 pay 15,6 mm boyunca sığıyor | ✔ |
| Tüp içi iki eşleşik JR | sığar | köşegen 13,0, tüp içi Ø51,3 | ✔ |
| Kablo boyu artanı (≥ 10) | 102 / 32,9 | 102,4 / 32,9. Servo kablo çıkışları servo gövdesine 0,5 mm (yol uçları doğru yerde). JR gövdesi (14 mm) boydan düşülürse 88,4 / **18,9** | ✔ |

**Kelepçe çekincesi (ölçüldü, kaldırmıyor ama ciddi):** Yarık y −140'ta alın kapağına bağlı halkada bitiyor (`dirsek_parcalar.py`
kesimi `TUC…−114`). Bu yüzden kapanma kökte sıfır, uçta (y −114) en büyük olmalı. Doğrusal dağılımla:
- bilezik tüpe ancak y ≥ −129,8'den itibaren değer;
- tüpü pime ancak y ≥ −119,6'dan itibaren bastırır, yani 26 mm'lik bileziğin yalnız uçtaki **5,6 mm**'sinde.

Alt cıvata (y −132) bu bölgenin dışında kalıyor. 0,137 mm ön yük ancak halka bütün boyunca düzgün kapanırsa geçerli. Kontrol bu
yüzden idealize; G'nin de çekincesi buydu. Önerim: yarığın kökünde çevresel bir boşaltma kesiği açılsın (bilezik kapaktan
~270° ayrılsın), ya da M7 kuponunda tüp çekme / dönme testiyle doğrulansın.

**Kablo modelinin sorgulanması:**
- **7,5 × d sınırı:** Helukabel'in tek bir yuvarlak PUR "kablo zinciri" örneğinden alınmış. Standart PVC servo uzatması sürekli
  esneme sınıfında değil (ajan da açık risk diye yazmış).
  - 10 × d (14 mm, 2 şeritte 14,7) alınırsa iki lop da **kalır** (13,0 / 12,4).
  - Kalınlık tahmini 1,4 yerine gerçekte 1,8 çıkarsa sınır 14,4 olur, yine kalır.
  - Kesit (4,2 × 1,4) ölçülmeden pay belirsiz.
- **Duyarlılık (bağımsız çözücü), pay ince:**

  | Değişiklik | Dirsek lopu R_min | S2 lopu R_min |
  |---|---|---|
  | Ölçülen hâl | 13,03 | 12,39 |
  | L −10 mm | 10,83 (**sınırın altı**) | 12,22 |
  | L +10 mm | 14,08 | 12,36 |
  | Kablo bağı çıkış açısı +15° | 11,58 (pay 0,4) | 11,69 (pay 0,5) |
  | Kablo bağı çıkış açısı −15° | 12,44 | 13,56 |

  Kablo bağının açısı ve lop boyu montajda ±15° / ±10 mm sapabilir; montaj talimatına lop boyu işareti ve bağ açısı girmeli.
- **3B etkiler:**
  1. Yerçekimi modelde yok. Kaba hesap (tahmini): 22 AWG yassı kablonun EI'si ≈ 20 N·mm², ağırlığı ≈ 13 g/m. Yerçekimi uzunluk ölçeği
     (EI/q)^⅓ ≈ 50 mm, yani lop boyutuyla aynı mertebede. Kol pozuna göre lop sarkar ya da kapanır, R ve boşluk değişir. 0,61 mm'lik en
     dar boşluk bağ noktasının hemen yanında (her pozda 0,61–0,63), yerçekiminden az etkilenir.
  2. İki şerit bağlı uçlar arasında kayamazsa, −285° dönüşte iç ve dış şerit boyu ≈ 7 mm farklı olur. Bir şerit kabarır.
     Şeritler lop içinde bağlanmamalı.
  3. Düzlem dışı kayma (dirsek 5,7 mm, S2 6 mm) küçük; düzlemsel model kabul edilebilir.
  4. Kablo `carpisma.py`'de yok. Kol × gövde taramasında loplar görünmez (ajanın da notu).

## 2. Regresyon (analiz JSON'ları; HEAD = 25de259, iskelet c531c59^ ile)

| Modül | Parça | Geçersiz / çoklu katı / çakışma | Bağlantı | Kütle | Fark kaynağı |
|---|---|---|---|---|---|
| dirsek | 53 → 53 | 0 / 0 / 0 | 22/22 → 22/22 | 370,0 → 367,4 g | G yarığı + M1 oluk/çentik/tırnak + A1 tüp içi 25,5 → 25,65 (1. adım); serbest aralık −60 → −40 (tırnak); tork ızgarası 3…120 |
| omuz | 70 → 66 | 0 / 0 / 0 | M6 4/4 | Kol 108,3 → 105,8; Gövde 600 → 595,2; Göbek 147,5 → 147,2 | M3: 4 M6 pulu kaldırıldı (−4 parça); tüp penceresi + A1 tüp içi; göbek −0,3 g ISO 273 geçme delikleri (1. adım). kol × gövde tarama hacimleri tüp değişikliğiyle küçüldü, serbest/çakışan poz kümesi aynı |
| kabuk | 202 → 194 | 0 / 0 / 0, iskelet 0 | 10/10 | 4.925,8 → 4.886,3 g | 1. adım: M3 (8 pul, M6×16 → ×14), M5 bindirme 0,2 boşluğu, cam ölçümü eklendi. G+M1 kabuk geometrisine dokunmadı (cam–duvar aynı 0,102) |
| iskelet | 59 → 59 | 0 / 0 / 0 | 12/12 | 5.793,1 aynı | köşe M6 kontrolü eklendi; eğilme ızgarası 3…120 (σ 0,931 → 0,911 MPa, G'nin kaydıyla aynı) |

Kasıtlı değişiklikler dışında fark yok. Omuz baskı analizi de bunu doğruluyor: yuva, kapak, göbek ve çatal hacmi birebir aynı, yalnız
tüp 39,57 → 39,12 cm³.

**Eski sınır kalıntıları (kod; rapor metinleri belge adımında):**
- `omuz/omuz_gorsel.py` 99–101 ve `omuz/omuz_goster.py` 21–22: animasyon dizileri yana **0** ile başlıyor (sınır dışı kare).
- `carpisma.py` 804: JEST "ev" = (0, **0**, 0, 0). Diğer jestler `YANA_MIN` kullanıyor.
- `montaj/montaj_gui_kontrol.py` 220: beklenti metni "yana acma, iceri (sinir 0)".
- `eklem_dogrulama.py` ve `montaj_gorsel.py` `arayuz.OMUZ` ile tutarlı (Y0 = 3; Kollari_oynat 3,0…68,75°). (0, 0) sınır dışı listesine
  doğru taşınmış.
- Rapor metinlerinde "yana 0…120" geçen yerler: `dirsek_rapor`, `kabuk_rapor`, `iskelet_rapor`, `kafa_rapor`, `taban_rapor`, `montaj_rapor`.

## 3. Baskı: üst kol tüpü (omuz_baski.py yeniden koşuldu, 227 s)
- Girdi: `omuz-montaj.FCStd` 14.10 23:48:08, sha256 `be9fa876bceb…`. `omuz_parcalar.py` 23:35, FCStd güncel.
- Tüp **hâlâ desteksiz** (+Y / −Y: destek 0, katman bölgesi 0). Pencerenin 45° uçları sınırda eğim olarak geçiyor. 45° üstü çıkıntı
  12,6 → 21,4 mm², hepsi Ø10 altı delik ve uç kırıntısı. Tüp kütlesi 40,2 → 39,7 g (0,8).
- Diğer dört parça birebir aynı: yuva, göbek ve çatal destekli, kapak desteksiz. M4 sonucu değişmedi (10 parçanın 6'sı destekli).
  `omuz-baski.json` güncellendi.

## 4. S1 (Ø84) geçişi: bağımsız değerlendirme

**Ölçülen serbest hacim (`K-s1.json`).** S1 dönüşü x'i değiştirmez. Bu yüzden S1 eksenine uzaklık r dilimlerinde sabit
parçaların en büyük x'i ve dönen parçaların en küçük x'i, S1'in bütün pozları için geçerli:

| r (mm) | Sabit en büyük x | Göbek en küçük x | Kol + çatal en küçük x: S2 3° | S2 5° | S2 10° |
|---|---|---|---|---|---|
| 24–28 | 160 (kapak) | 163 | 169 | 169 | 169 |
| 30–36 | **155 (kapak M3 cıvata başları, r 30,8–36,3)** | 163 | 166,5 → 158,8 (r 34) | 160,1 | 163–170 |
| 38 | 152 (kapak kulakları, r ≤ 39,9) | 163 | 158,8 | 160,1 | 163,3 |
| 40–64 | 152 (kabuk ped yüzü) | 163 (r ≤ 50) | 158,8–160,1 | 160,1–162,2 | 163,3–167,5 |

- Kabuğun üstü eksenin 30 mm üstünde (y max 30,0). Kabuk z −83…+116.
- **Sonuç:** r 38–64'te x 152…158,8 arasında **her S1 pozunda kolun hiç girmediği 6,8 mm'lik halka dilim** var (S2 5°'de 8,1 mm).
  Tasarımcının "tüp alt sektörü doldurur" bulgusu x ≥ 158,8 için doğru. Kablo bu dilimde kalırsa sektör kısıtı yok.
- **Tasarımcının kasetinde iki ölçülmüş sorun:**
  1. Tambur (r 31,5–33, x 153–161) **kapak M3 cıvata başlarına çarpar** (r 30,8–36,3, x 152–155; tambur dönünce dört başı da süpürür).
  2. S1'den **3 şerit** geçiyor (dirsek + bilek + göbekteki S2 servosu). Sınır 7,5 × 1,4 + 1,4 = **11,9**. Önerilen U yarıçapı
     (61 − 33 − 4,2) / 2 = 11,9, yani **pay sıfır**. Bağımsız duyarlılıkta ±15° bağ açısı R'yi ±1,3 mm oynatıyor.

| Seçenek | Değişen parçalar | Bükülme R (3 şerit, sınır 11,9) | Risk | Baskı / montaj | Tahmini iş |
|---|---|---|---|---|---|
| **A′ Döner U-lop kaseti, düzeltilmiş** | göbeğe vidalı ayrı tambur (r 37–39, x 152,5–157,5; göbekle 2–3 kolla, tüp sektörü dışından bağlı); sabit yay duvarı r 68–70 (U'nun 90° gezisi + pay, üst-arka ~150°) + düz kapak flanşı (x ~157); kabuk omuz bandı: 2–3 M3 ısıl gömme + yay duvarının sabit ucunda arka kablo yarığı (r ~60, y < 30) | (68 − 39 − 4,2) / 2 ≈ **12,4**; r 70 ile **13,4** | eksenel pay dar: 0,3 + 4,2 + 0,3 + 1,0 flanş → tüpe 1,0 mm (S2 3°), 2,3 mm (S2 5°); tambur–cıvata başı 0,7 mm; yay duvarı kabuk üstünden ~40 mm taşar (görünür, kapak/örtü) | tambur ve yay ayrı, düz basılır, desteksiz; göbeğin baskısı değişmez (yalnız 2–3 ısıl gömme). Montaj: göbek → tambur → kablo U'ya → flanş | M (1 tasarım oturumu + kablo kontrolü genişletmesi) |
| A Tasarımcının kaseti (olduğu gibi) | tambur göbekte r 31,5–33, x 153–161; yay r 61–64 | 11,9 (pay 0) | **cıvata başı çakışması**; sektör kısıtı; R payı yok | tambur göbekle tek parça → göbek baskısı ağırlaşır | M |
| B Spiral kaset (saat yayı) | göbekte hub r 38; tam daire sabit muhafaza r ~70 | ≥ 38 (çok iyi) | 4,2 mm kalın 3 PVC şerit spirali: 180° için ~650 mm kablo; spiral sürtünür, kabarır, S1'e tork yükler; tam halka kabuk üstünden 40 mm taşar | muhafaza büyük; montaj zor | M+ |
| C Omuz üstü serbest lop | yalnız kabuk girişi | ≈ 10 (sınır altı) | 95 mm taşar, kontrolsüz, takılma ve ezilme | — | S |
| D S1 aralığını daraltmak | yazılım | — | geçişi çözmez; jestler kaybolur (kafa kaşıma 135, el yüze 120…135) | — | S |
| E Kabloyu S1 ekseninden geçirmek | göbek mili, kapak, yuva | — | **imkânsız:** eksende S1 servo gövdesi; horn r 12,5 + M3 vidalar r 8,5 (havşa r 11,8) göbek mili r 20'yi dolduruyor; geriye 6808 yuvasının ~3 mm duvarı kalıyor; sabit kapak dudağı (r 24…30, x 146…160) radyal çıkışı kapatıyor | — | — |
| F Kabuk deliğini büyütüp kabloyu gövde içinde döndürmek | kabuk omuz bandı (Ø130+) | — | kabuğun üstü eksenin 30 mm üstünde: tam halka gövdeye sığmaz; büyük delik bandı zayıflatır | — | — |

**Öneri: A′ (düzeltilmiş döner U-lop kaseti), S2 yazılım alt sınırını 3° → 5°'e çekerek.** Gerekçe:
- Tasarımcının fikri doğru. Kalın, çok şeritli kabloda dönen eksen için standart çözüm yuvarlanan U.
- Kablo kolun hiç girmediği x 152…158 halka diliminde tutulursa sektör kısıtı ortadan kalkar.
- Tamburu r ≥ 37'ye taşımak cıvata başı çakışmasını çözer; dış duvarı r 68–70'e büyütmek 3 şeritli sınırda gerçek pay (≥ 0,5–1,5 mm)
  verir.
- S2 5° eksenel payı 1,0'dan 2,3 mm'ye çıkarır. 2° kayıp yalnız "kol tam aşağıda" duruşunda.
- B'nin bükülme payı daha iyi, ama kalın PVC şeritlerin spiralde sürtünmesi ve kabarması kontrol edilemez; kabloyu da uzatır.
- Ayrı tambur, M4'te zaten destekli olan göbeğin baskısını ağırlaştırmaz.

Uygulayacak ajan için kontrol listesi:
1. Tambur ↔ kapak cıvata başı ≥ 0,5 mm.
2. Kaset ↔ kol: her S2 ≥ alt sınır için x boşluğu ≥ 0,5 mm (`K-s1.py` yöntemiyle).
3. U yarıçapı: 3 şerit, ±15° bağ açısı ve ±10 mm boy duyarlılığıyla ≥ 11,9.
4. Yay duvarının sabit ucundan kabuk içine giriş: köşe R ≥ 4 × 1,4 + 1,4 = 7,0.
5. Uzatma kablosu boyuna U + yay boyu eklenecek (≈ +250 mm/servo, tahmini).

## Commit'e engel var mı?
Ölçülebilir bir kontrol kalmadı, regresyonda kasıt dışı fark yok. **Engel yok.** Commit mesajında / M1 günlüğünde şunlar açık
olarak kalmalı:
- S1 geçişi açık. Kol kablo yolu S1 olmadan bütün değil; `KOL_KABLO["s1"]` "ACIK".
- Kelepçede kapanma kökte sıfır: pime bastıran boy 5,6 mm. M7 kuponu ya da boşaltma kesiği gerekli.
- Lop payı ince: 10 × d ile kalıyor; L −10 mm ya da bağ açısı +15° ile sınıra iniyor. Kablo kesiti ölçülmeli.
- Eski sınır kalıntıları: `omuz_gorsel`, `omuz_goster`, `carpisma` JEST "ev", `montaj_gui_kontrol` metni.
