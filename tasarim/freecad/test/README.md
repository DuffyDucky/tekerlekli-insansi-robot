# Test kuponları

Büyük parçaları basmadan önce geçme, ısıl gömme somun ve kelepçe ölçülerini denemek için küçük baskılar. Hepsi desteksiz,
tek başına basılır. Ölçüler `arayuz.py`'den okunur. Kupon betikleri arayüzü değiştirmez: sonucu ekip ölçer, karar
`arayuz.py`'ye elle yazılır (her kuponun "sonuç nereye yazılır" satırı).

| Betik | Kuponlar | Çıktı |
|---|---|---|
| `tolerans_kuponu.py` (11 Ekim) | A: 6808 dış bilezik Ø52 yuvaları · B: 625ZZ yuvası, 6808 iç bilezik mili, M3/M5 ısıl gömme (dikey, L + 0,5) | `stl/kupon-a-*`, `stl/kupon-b-*`, `tolerans-kuponu.step` |
| `m7_kuponlari.py` (15 Ekim, M7) | C: ısıl gömme L + 1, dikey + yatay · D1/D2: dirsek sıkma bileziği · E: üst kol tüpü halkası | `stl/kupon-c..e-*`, `m7-kuponlari.step`, `m7-kupon-sonuc.json` |
| `../kafa/yanak_kuponu.py` (19 Kasım, K54 c) | Yanak kuponu (kafa iskeleti dilimi) + yığın mastarı | `../kafa/stl/yanak-kuponu.stl`, `../kafa/stl/yanak-kuponu-mastar.stl`, `../kafa/yanak-kuponu.json` |
| `../kabuk/bant_kuponu.py` (19 Kasım, K55 a) | Bant kuponu: orta bant dilimi (dil) + göğüs bandı dilimi (dudak) | `../kabuk/stl/bant-kuponu-alt.stl`, `../kabuk/stl/bant-kuponu-ust.stl`, `../kabuk/bant-kuponu.json` |

**M5 ısıl gömme delikleri (19 Kasım, P10.8):** K31'in teknik yarısı M5 için Rhino ID5 OD7 L7'yi seçti; satıcı kuralı delik Ø6,7–6,8.
Kupon B'nin M5 delikleri Ø6,6 / 6,7 / 6,8, kupon C'ninki Ø6,6 … 6,8 oldu (eskiden ikisinde de Ø6,2 … 6,6). Değer kupon betiğinde yerel
parametre (`M5_DELIK_K31`, `M5_K31`). Asıl parçaların deliği `arayuz.INSERT_DELIK[5]` hâlâ 6,4. Kupon sonucu bu değere sonraki tam
taramalı CAD paketinde yazılır (`arayuz.py` çarpışma taramasının izlediği dosya). Deneme aralığı tek yönlü: üstte satıcı kuralının
üst ucu (6,8) var, üstü yok. PETG-CF'de basılan delik genelde küçük çıktığı için 6,8 de sıkı gelirse kupon C 6,9 ile yeniden üretilip
basılır (`M5_K31` nominalini 6,8 yapmak damlaları 6,7 / 6,8 / 6,9 yapar; delik sayısı ve K43 sayımı değişmez).

Çalıştırma (README'deki başlatıcıyla, ~10 s):
`FC_SCRIPT=$R/test/m7_kuponlari.py "$FC" $L`

**D / E onarıldı (19 Kasım, P10.8c; `planlama/d158/P108c-gunluk.md` § 3):** Y2a'dan (`tup_uc_y` −140 → −170, `catal_dis_kol`
5 → 8) beri D / E bölümü 125 cm sabitleriyle ("width of box too small") koşmuyordu ve D1 / D2 / E STL'leri 15 Ekim'den kalmıştı. Bölüm
artık ölçüleri `dirsek/dirsek_parcalar.py`'den okur (import; dosya yazılmaz), D1 hâlâ `dirsek-montaj.FCStd`'deki gerçek çatalın
dilimiyle ve import edilen çatalla iki yönlü karşılaştırılır (fark 0 değilse çıktı yazılmaz). `M7_YALNIZ_C=1` kipi kalktı (tam kip
koşuyor). Radyal geçme ölçüleri değişmedi; D1 / D2'de değişen tüp ucunun yeri ve 3 mm kalın dış kol / köprü (genişlik 70,9 → 73,9).

## M7 kuponları (`m7_kuponlari.py`)

| Kupon | Ölçü (mm) | Malzeme | Kütle %100 / tahmini | Süre (tahmini) | Baskı |
|---|---|---|---|---|---|
| C ısıl gömme L + 1 | 61 × 17,2 × 14 | PETG **ve** PETG-CF (iki kez) | 13,2 / 7,4 g | 13 dk | 46° üstü çıkıntı yalnız yatay delik tepeleri (≤ Ø6,8) |
| D1 kelepçe, kesiksiz | 73,9 × 72 × 33 | çatalın malzemesi (şu an PETG) | 90,3 / 41,8 g | 71 dk | ters (bilezik ağzı tablada); yatay tavan yalnız V oluğun 0,25 mm basamakları |
| D2 kelepçe, kökte boşaltmalı | 73,9 × 72 × 33 | D1 ile aynı | 88,6 / 42,3 g | 72 dk | aynı; boşaltma dik yarık (köprü yok) |
| E tüp halkası | Ø56 × 36 | üst kol tüpünün malzemesi (PETG) | 17,9 / 14,3 g | 24 dk | dik, uç tablada; 5 mm brim |
| **Toplam** (C bir kez) | | | **210 / 106 g** | **~3 sa** | C ikinci malzemede +7,5 g, +13 dk |

Tahmin: 4 çevre + %25 dolgu, 10 mm³/s ortalama debi (`arayuz.PETG_HACIM_HIZI`, tahmini) × 1,3 hareket payı. Dilimleyicinin
verdiği değer esastır. Kuponları gerçek parçalarla aynı profille basın (katman, çevre sayısı, sıcaklık); yoksa sonuç aktarılmaz.
Önce **D1 + E** basılabilir: D1 geçerse D2 yalnız karşılaştırma için gerekir.

### Kupon C: ısıl gömme somun deliği, derinlik L + 1, dikey ve yatay

Neden: kupon B'nin delikleri dikey ve L + 0,5 derin. Oysa omuz yuvasının M3 × 4 ve göbeğin M5 delikleri yatay basılıyor
(`planlama/adim2/M4-omuz-baski.md`): delik tepesi sarkar, somun eğik oturabilir.

Yapı: basamaklı tek blok. M3 bölümü (11 mm yüksek) delikleri −Y yüzünde, M5 bölümü (14 mm) +Y yüzünde. Arada 2,5 mm ortak
arka duvar var. Derinlik `INSERT` boyu + 1: M3 6,7, M5 8,0. Üst yüzdeki nokta sayısı = sıra.

| Nokta | M3 (yatay, eksen z 5) | M5 (yatay, eksen z 6,5) |
|---|---|---|
| 1 | Ø4,0 yuvarlak | Ø6,7 yuvarlak |
| 2 | Ø3,9 damla | Ø6,6 damla |
| 3 | Ø4,0 damla | Ø6,7 damla |
| 4 | Ø4,1 damla | Ø6,8 damla |
| noktasız (üst yüz) | Ø4,0 dikey, 6,7 derin | Ø6,7 dikey, 8,0 derin |

M5 sütunu 19 Kasım'dan (K31, yukarıda); önceki değerler Ø6,4 / 6,2 / 6,4 / 6,6 / 6,4. M3 sütunu değişmedi: K31 M3 seçeneği A'nın
(Rhino ID3 OD4 L4) kuralı Ø3,8–3,9; C'de Ø3,9 damla, B'de Ø3,8 / 3,9 dikey bunu dener. Derinlik L4 için fazla (6,7), deneme için engel değil.

Damla: daire + üstte 45° sivri uç (tepe merkezden r·√2 yukarıda).

**Test:**
1. Somunu her deliğe aynı yöntemle takın: lehim havyası, ısıl gömme ucu, üreticinin PETG için önerdiği sıcaklık. Yüzeyle aynı
   hizaya kadar bastırın, düz bir yüzle 5 s tutun.
2. Ölçün:
   - (a) Yüzeyden çıkıntı/çöküntü (kumpas derinlik ucu).
   - (b) Eğiklik: M3 × 20 / M5 × 20 vidayı takın, gönye ile 20 mm boyda sapmayı ölçün.
   - (c) Ağızdan taşan erimiş plastik, delik dibinde sıkışma (somun sonuna kadar girdi mi).
   - (d) Yatayda tepe duvarında çatlak ya da şişme.
   - (e) Vidayı tork anahtarıyla (yoksa alyanı sabit kolla) M3 0,5 N·m, M5 1,5 N·m sıkın (plastik için tahmini). Somun dönüyor mu?
3. Aynı nominal çapta kupon B (dikey, L + 0,5) ile C (dikey, L + 1) sonucunu yan yana yazın.

**Kabul:** çıkıntı −0,2…+0,1 mm; eğiklik ≤ 0,35 mm / 20 mm (≈ 1°); somun tam derinliğe giriyor ve ağızdan plastik
taşmıyor; tork altında dönme yok; yatay tepede çatlak yok.

**Sonuç nereye yazılır:**
- Dikey çap → `arayuz.INSERT_DELIK[3]`, `[5]` (B ile birlikte).
- Derinlik payı şu an `ortak_lib.insert_hole(extra=0.5)` içinde sabit. L + 1 seçilirse arayüze yeni bir sabit eklenmeli
  (`INSERT_DERINLIK_PAY`) ve `insert_hole` varsayılanı oradan okunmalı. Bu değişiklik `ortak_lib.py`'yi ve dolayısıyla tüm
  modülleri etkiler; 6. adımdaki yeniden üretimden önce yapılmalı.
- Yatay delik nominalden farklı çap ya da damla isterse: yeni `INSERT_DELIK_YATAY` ve `INSERT_YATAY_DAMLA`. Uygulanacak yerler:
  omuz yuvası M3 × 4, göbek M5, S1 göbek M3 × 3.

### Kupon D1 / D2 + E: tüp–bilezik geçme halkası ve sıkma bileziği

Neden: G ve K çekincesi (`planlama/adim1/G-takip.md`, `planlama/adim2/K-kontrol.md`). 4 mm yarık kapanınca bileziğin iç
yarıçapı 0,637 mm düşer. Toplam radyal boşluk 0,5 mm (tüp–pim 0,25 + tüp–bilezik 0,25), yani ideal ön yük 0,137 mm. Ama
bilezik kökte (y −170) alın kapağına bağlı olduğu için kapanma kökte sıfır, uçta en büyük. Doğrusal kabulle tüp pime
yalnız uçtaki ~5,6 mm boyunca bastırılır.

- **D1** gerçek çatalın y −178…−145 dilimidir (tüp ucu −170; 125 cm'de −148…−115): alın kapağı, köprü bandı, 45° destek, pim (içi boş, 45° tavan), 4 mm yarıklı
  bilezik, kulaklar, 2 × M3 deliği, M1 kablo oluğu. Ölçüler `arayuz.DIRSEK`, `GECME`, `TUP_PIM_R`; arayüzde olmayanlar
  `dirsek_parcalar.py` 97–127. satırlarla aynıdır.
  - **Doğrulama:** `dirsek-montaj.FCStd` içindeki "Dirsek catali" aynı dilimle kesildi. Hacim 71.079,65 mm³ (19 Kasım,
    P10.8c), iki yönlü fark 0,000 mm³; import edilen `dirsek_parcalar` çatalıyla da 0 (`m7-kupon-sonuc.json` → `d1_fcstd_dogrulama`;
    pim, bilezik, yarık ve kelepçe deliklerinin kuponla gerçek çatalda aynı yöntemle ölçümü `arayuz_olcum`). Çatal değişirse betik bunu yakalar.
- **D2:** D1 + kökte boşaltma (K önerisi: bilezik kapaktan ~270° ayrılsın).
  - Desteksiz basılsın diye ayrılma yatay bir kesik değil. Kapak boyunca **dik halka yarığı**: r 28,1…29,3 (1,2 mm), θ −225…45°
    (θ tüp ekseni çevresinde −Z'den +X'e). Ölçülen bağlı sektör θ 45…120°.
  - Bağlı sektör bilerek **+X köprü bandına** (θ 59…121) konuldu. Gerçek çatalda dış kol ve horn yükü pime köprü üzerinden
    gider, bu yol kesilemez. Bu yüzden simetrik "ön 90° bağlı" seçenek gerçek parçaya uygulanamaz.
  - Tüp alın yuvasında V oluk yerine pimden dışa yükselen 45° koni tavan var (askıda kenar kalmasın diye). Bu yüzden tüp
    0,25 mm daha derine (y −170,25) oturur. Kavrama testine etkisi yok.
- **E:** tüp halkası, r 25,65…28 (`TUP_PIM_R + GECME['tup_pim']` … `DIRSEK['tup_ro']`), 36 mm boy. 25 mm bileziğe girer,
  dışarıda kalan 11 mm'nin ortasında Ø6 kol deliği var.
- Geometri kontrolü: tüp, iki bilezikle de çakışmıyor (0 mm³). Yarık uçta ve kökte 4,0 mm (açık hâl).

**Gerekenler:**
- Bağlantı elemanları: 2 × M3 × 20 DIN 912, 4 × M3 pul, 2 × M3 DIN 985 (çatal BOM'u ile aynı).
- Aletler: 2,5 mm alyan, 5,5 mm anahtar, kumpas, sentil (ya da matkap uçları), kalıcı kalem.
- Test için: Ø5–6 çubuk (uzun M5 cıvata ya da tornavida), ip, 2 kg ve 3 kg ağırlık (su şişesi + bagaj tartısı).

**Test prosedürü (D1, sonra D2; aynı E halkası, ikincide yeni boya):**
1. **Montaj öncesi ölçüm:** pim Ø (50,8), bilezik iç Ø ağızda (56,5), tüp dış/iç Ø (56,0 / 51,3). Her biri üç yönde ölçülür,
   ovallik yazılır. Yarık uçta (4,0) ölçülür.
2. **Takma (cıvatalar gevşek):** tüp elle, aletsiz sonuna kadar girmeli. Hafif radyal oynama hissedilmeli.
3. **Boya:** tüpün dış yüzüne ve iç yüzüne kalemle dört boyuna şerit çizin: yarık tarafı, karşısı ve iki yan. Tüp ağzıyla
   bilezik ağzının üstüne tek bir hiza çizgisi çizin.
4. **Sıkma:** iki cıvatayı sırayla, kulaklar değene kadar ya da belirgin sertleşene kadar sıkın (M3 plastikte ≈ 0,6 N·m,
   tahmini). Kalan yarığı sentille ölçün: uçta (y −151 cıvatası, ağız tarafı) ve kökte (y −162 cıvatası, kapak tarafı).
   Kulaklar değdiyse not edin.
5. **Sarsma:** tüpü elle her yöne eğin. Tıkırtı ya da boşluk var mı?
6. **Eksenel:** kupon kapak üstte sabitlenir, tüp aşağı sarkar. Ø6 delikten iple 3 kg asılır, 60 s beklenir. Hiza çizgisinin
   eksenel kayması ölçülür.
7. **Burulma:** Ø6 delikten çubuk geçirin. Tüp ekseninden 100 mm uzağa 2 kg asın (1,96 N·m), 60 s bekleyin. Hiza çizgisinin
   çevresel kayması ölçülür.
8. **Sökme:** boya izlerini okuyun. Bilezik–tüp ve tüp–pim temas izinin tüp ucundan itibaren boyu, yarık tarafında ve
   karşısında ölçülür.

**Kabul ölçütleri:**

| No | Ölçüt | Sınır | Dayanak |
|---|---|---|---|
| K1 | Takma (gevşek) | aletsiz girer | GECME 0,25 (M2): baskı toleransı |
| K2 | Sıkınca | kulaklar değmeden tüp kavranır; kökteki kalan yarık yazılır | kulak teması = kapanma boşluğu yemiş, ön yük yok |
| K3 | Eksenel 3 kg, 60 s | kayma ≤ 0,5 mm | dirsek modülü 367 g + 0,5 kg tasarım yükü ≈ 0,87 kg × 3 (dinamik + emniyet; tahmini) |
| K4 | Burulma 1,96 N·m, 60 s | kayma ≤ 0,5 mm (≈ 1°) | dirsek 0°'da bilek MG996R durma torku (0,92 N·m @4,8 V, 1,08 @6 V) tüpe burulma olarak gelir, × ~1,8 |
| K5 | Boya izi | bilezik–tüp teması yarık tarafında ≥ 15 mm (25 mm'nin) | G/K çekincesi: kökte kapanma yok; doğrusal kabul 5,6 mm öngörüyor |
| K6 | Sarsma | tıkırtı yok | pim merkezleme |

**Sonuca göre karar ve CAD sabiti:**

| Sonuç | Karar | Nereye yazılır |
|---|---|---|
| D1 K1–K6 geçer | çekince kalkar, CAD değişmez | `dirsek_montaj` kelepçe kontrolüne "kuponla doğrulandı" notu; `arayuz.DIRSEK` aynı |
| D1 K3/K4/K5 kalır, D2 geçer | çatala kökte boşaltma eklenir (D2 geometrisi) | yeni `arayuz.DIRSEK["bilezik_bosaltma"] = dict(r=(28.1, 29.3), teta=(-225, 45))` → `dirsek_parcalar.py` (V oluk bağlı sektörde kalabilir) + kontrol: bağlı sektör köprü bandını kapsar |
| ikisi de kayar, kulaklar değmiyor | sıkma kuvveti/sürtünme yetersiz: yarık büyür | `arayuz.DIRSEK["bilezik_yarik"]` 4 → 5 (kapanma 0,80, ön yük 0,30; kulak 5 → 4,5 mm), `bilezik_on_yuk_min` gözden geçirilir |
| ikisi de kayar, kulaklar değiyor | boşluk kapanmıyor | `arayuz.GECME["tup_bilezik"]` K1'deki ölçülen boşluğa göre 0,25 → 0,15 (`kabul_max` aynı) ya da tüpe radyal M3 pim (pozitif kilit) |
| K1 kalır (takılmıyor) | boşluk dar | `GECME["tup_bilezik"]` / `["tup_pim"]` 0,3; yarık + ön yük `dirsek_montaj` kontrolüyle yeniden hesaplanır |

Ölçülen değerler bu tabloya, tarih ve malzemeyle yazılır:

| Tarih | Kupon | Malzeme | Ø ölçümleri | Kalan yarık uç / kök | K1 | K2 | K3 | K4 | K5 (mm) | K6 | Not |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | D1 | | | | | | | | | | |
| | D2 | | | | | | | | | | |

## K54 yanak kuponu (`../kafa/yanak_kuponu.py`, 19 Kasım)

Neden: K54 seçenek c (`planlama/d158/karar-kuyrugu.md`). Kafa iskeletinin iki yanağı arası 54,4 mm. Aradaki yığın da 54,4 mm: solda
eğme çatalının dayaması ve 625ZZ iç bileziği, sağda tilt hornunun dış yüzü. Kafa bu yüzden iki yanda sıfır boşlukla iner. Baskı
toleransında zorlamadan inip inmediği ölçülmedi.

Yapı (iki baskı, ölçüler `kafa/kafa-montaj.FCStd`'den okunur, elle yazılmaz):
- **Yanak kuponu:** gerçek "Kafa iskeleti" ile bir kutunun kesişimi. İçinde iki yanak (sol 11 mm, 625ZZ yuvalı; sağ 5 mm, horn
  delikli) ve aralarındaki tabla dilimi var. Ekleme yok. Baskı yönü kafa iskeletininki: tabla dilimi tablada, yanaklar yukarı.
- **Yığın mastarı:** tilt ekseni boyunca tek parça. Çatal dayaması (r 4, 625ZZ iç bileziğine dayanır), çatal kolu çapında gövde (r 15;
  sol yanağa 1 mm, gerçek çatal kolu gibi) ve tilt hornu diski (r 12,5, 3,3 mm). Boyu dayama yüzünden horn dış yüzüne 54,4 mm. Horn
  diski tablada, dik basılır.
- Kaynakla karşılaştırma `kafa/yanak-kuponu.json` → `karsilastirma`. Yanak aralığı dört hatta 54,4 = 54,4, mastar boyu 54,4 = yığın
  54,4, fark 0. İniş yolunda (+y, 0–30 mm) ortak hacim 0; yüzler temas ediyor.

| Parça | Ölçü (mm) | Malzeme | Kütle tahmini / %100 | Süre (tahmini) | Destek |
|---|---|---|---|---|---|
| Yanak kuponu | 72,4 × 40 × 48 | PETG (kafa iskeletinin malzemesi) | 20,6 / 41,2 g | 35 dk | desteksiz (kafa iskeleti gibi; yatay delik tepeleri köprü) |
| Yığın mastarı | 30 × 30 × 54,4 | PETG | 16,5 / 46,7 g | 28 dk | desteksiz |

Gerekenler: kumpas, sentil. İnsert ve vida gerekmez. **Sol taraf ölçümü için bir 625ZZ şart** (aşağıda). Rulman yoksa yalnız sağ taraf
ve yuvanın altındaki şerit sınanır.

Sol yanağın iç yüzünde Ø16 rulman yuvası var: 5 mm derin, dibi x −29,2. Rulman takılı değilken yuva hizasında yanak aralığı **59,4 mm**,
öbür her yerde 54,4 (P108a-kontrol § 3.3, STL ışın ölçümü). Mastarın dayaması r 4, yani rulman yokken dayama yuvaya düşer ve sol yanağa
değmez. Sıfır boşluklu iniş (54,4 = 54,4) solda yalnız 625ZZ iç bileziği yuvada, yüzü yanağın iç yüzüyle aynı düzlemdeyken sınanır.

**Test:**
1. **Ölçüm:** kumpasın iç çenesiyle yanaklar arasını ölçün. Rulman yuvasının dışında, üç yerde ölçün: tablaya yakın, yuvanın altındaki
   şerit (eksenden 8–16 mm), yanak ucu (nominal 54,4). Rulman yokken yuva hizasında 59,4 ölçülür; bu beklenen değerdir, kusur değildir.
   Mastarın boyunu dış çeneyle dayama yüzünden horn diski yüzüne kadar iki yönde ölçün (nominal 54,4).
2. **625ZZ'yi takın:** rulmanı sol yanağın Ø16 yuvasına bastırın (asıl montajdaki E3a gibi). İç bileziğin yüzü yanağın iç yüzüyle aynı
   düzlemde olmalı. Sonra yuva hizasında aralığı yeniden ölçün: rulman iç bileziğinden sağ yanağa nominal 54,4.
3. **İniş:** mastarı yatay tutun. Yanak kuponunu tabla dilimi üstte olacak şekilde üstüne indirin. Dayama sol yanağa (625ZZ tarafı),
   horn diski sağ yanağa (dört küçük delikli taraf) gelmeli. Eksenler hizalanana kadar yalnız elle bastırın; yanakları elle açmayın.
   Rulman yoksa "eksenler hizalandı" denemez; o zaman iniş yalnız sağ yanak ↔ horn diski ve yuvanın altındaki şerit için yazılır.
4. İndikten sonra sentille ölçün, ikişer noktada: **sağda** yanak ↔ horn diski; **solda** yalnız 625ZZ takılıyken, iç bilezik ↔ dayama.
   Rulmansız denemede sol sentil sütununa "rulman yok" yazın.
5. Eğme çatalı (Parti 2), MG996R ve 25T horn gelince aynı inişi asıl yığına yapın: çatal, servo ve horn E2 sırasıyla takılır. Bunu kafa
   iskeletini (Parti 3) basmadan önce yapın.

**Geçti:** 625ZZ takılıyken kupon alet kullanmadan ve yanaklar açılmadan iner (hafif sürtünme kabul). Yanakta beyazlama ya da çatlak
olmaz. Bu durumda K54 a geçerli olur ve CAD değişmez. Bu sonuç asıl yığınla (adım 5) da tekrarlanmalı. Rulmansız deneme yalnız sağ
tarafı geçirir; sol taraf için sonuç "denenmedi" kalır.

**Kaldı:** kupon inmez ya da ancak yanaklar açılarak iner. Bu durumda K54 b uygulanır: yanak iç yüzlerine her yanda pay verilir.
Pay = (mastar boyu − yanak aralığı) / 2 + 0,1 mm, karar aralığı 0,2–0,3 mm. Değişecek asıl ölçüler: sağ yanağın iç yüzü
(`kafa7_parcalar.py` `X_SAG[0]` = horn dış yüzü 30,2) ve sol yanağın iç yüzü (`X_SOL[1]` −24,2; 625ZZ yuvası `X_RUL` aynı düzlemde).
Bu bir kafa geometrisi değişikliğidir ve kafa çakışma taraması gerekir. Sağda 4 × M3×8 sıkılınca yanak horna çekilir. Solda pim
sıkılınca 625ZZ iç bileziği dayamaya çekilir; şim ya da eksenel yük o zaman ölçülür (K54 b).

| Tarih | Malzeme | Yanak aralığı (3 yer; 625ZZ var / yok) | Mastar boyu | İniş (elle / zor / inmedi) | Sentil sol / sağ | Asıl yığınla | Not |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## K55 bant kuponu (`../kabuk/bant_kuponu.py`, 19 Kasım)

Neden: K55 seçenek a, geçici çözüm. Rehber metni "bandı hafifçe esneterek dili alttaki bandın arkasına sok" diyor. Üst bant alttaki
bandın 12 mm bindirme diline hiçbir düz yoldan girmiyor (`planlama/d158/F10d-gunluk.md` §11.5). Gövde yukarı doğru genişliyor; bu
yüzden göğüs bandı yukarıdan inerken son 13 mm'de orta bandın diliyle çakışıyor.

Yapı (iki baskı, gerçek CAD dilimi, `kabuk/kabuk-montaj.FCStd`):
- **Alt:** "Govde orta bandi sag", y 995 … dil ucu. Dil yukarıda, 1,25 mm (yarım duvar 1,5 − 0,25 boşluk).
- **Üst:** "Gogus bandi sag", y 1005–1025. Dudak aşağıda, 1,5 mm dış yarı, 12 mm boyunda. Üstünde 8 mm tam duvar var; göğüs ekranı
  cebinin altında kalır.
- İkisi de bantların baskı yönünde basılır: dik, alt kenarı tablada. Kaynakla karşılaştırma `kabuk/bant-kuponu.json`. Duvar katmanları
  yan, ön ve arka hatta kaynakla aynı; dil 1,25, dudak 1,5, boşluk yanda ve önde 0,25.
- Modelde iniş: üst parça dinlenme konumundan 14 mm yukarıdayken serbest, altında ortak hacimli. Dudağın iç yüzü ile dilin dış yüzü
  arasındaki radyal girişim (`inis.girisim_mm`):

  | Kalan iniş | Önde | Yanda | Arkada |
  |---|---|---|---|
  | 2 mm | 1,2 mm | 0,2 mm | 0 |
  | 6 mm | 4,0 mm | 1,2 mm | 0 |
  | 10 mm | 6,8 mm | 2,1 mm | 0 |

  En zor yer ön bölüm, yani bel–göğüs geçişi.

| Parça | Ölçü (mm) | Malzeme | Kütle tahmini / %100 | Süre (tahmini) | Destek |
|---|---|---|---|---|---|
| Alt (orta bant dilimi) | 161,8 × 214,2 × 23,4 | PETG (beyaz) | 24,5 / 24,8 g | 42 dk | desteksiz (orta bant gibi) |
| Üst (göğüs bandı dilimi) | 164 × 217,2 × 20 | PETG (beyaz) | 26,9 / 29,5 g | 46 dk | **destekli**: z 12'deki iç yarı basamağı (6,6 cm²). Göğüs bandının "z 12–15 alt kenar çıkıntısı" ile aynı yer (`baski-analiz.json`); destek dudağın içinden temiz çıkmalı |

Kısıt: dilimler kısa (alt 24, üst 20 mm), gerçek banttan daha esnek. Kupon geçerse gerçek bant için kesin sonuç değildir; kalırsa
gerçek bant da kalır.

**Kapsam: bu kupon neyi dener, neyi denemez (19 Kasım, P10.8a düzeltme 1).**
- Dener: orta–göğüs dikişinin (y 1005) **sağ yarısı**. Dil / dudak geçmesi iki yoldan: +y (yukarıdan iniş) ve +x (rehberin yolu).
- Denemez: sol yarı, x = 0 dikişi, etek ön bandı (perçin somunu engeli), omuz bandı (rulman kapağı engeli) ve göğüs ekranı çerçevesi.
  Bunlar için sonuç bu kupondan **çıkarımdır, deneme değildir**. Dil, boşluk ve duvar bütün bantlarda aynı (`KABUK_BINDIRME` 12,
  `KABUK_BINDIRME_BOSLUK` 0,25, `KABUK_T` 3), ama girişim ve engel bant başına farklı. Sol göğüs bandı +y yolunda sağ bantla da
  1–19 mm ortak hacimli (F10d § 11.5); bu kuponda yok.
- Etek ön bandının kendi kuponu ayrı: `../kabuk/etek_kuponu.py` (19 Kasım, P10.8c; aşağıda "K55 etek ön bandı kuponu").

**Neden iki yol.** Rehber F3 (adım 35) "Göğüs bandı sağı +x'ten getir … dilini orta bandın arkasına sok" diyor. Geometride durum
bunun tersi. Dil orta bandın iç yarısı; göğüs bandının alt kenarı dış yarıdır (dudak) ve dilin dışından geçer (yan hatta dil x 147,1–148,4,
dudak 148,6–150,1). +x yolunda kupon dilimi alt parçayla 1–160 mm boyunca ortak hacimli, 170 mm'de serbest (`bant-kuponu.json`
`inis_x`; tam bantla F10d'de 1–159 / 173). +y yolunda yalnız son 13 mm ortak hacimli (`inis`). Bu yüzden ana deneme +y. +x denemesi
rehberdeki yolun kendisini sınar.

**Test:**
1. **Deneme 1 (+y, ana deneme):** alt parçayı dil yukarı bakacak şekilde masaya koyun. Üst parçayı dudak aşağı bakacak şekilde
   yukarıdan getirin. Dudak dilin dışında kalmalı. Önce arka ve yan bölümü indirin, en son ön bölümü. Ön bölümde dudağı dışa, dili içe
   hafifçe esnetin. Alet kullanmayın. Modelde en büyük girişim ön-yan köşede: 10 mm kala 7,8 mm (P108a-kontrol § 3.4).
2. Dudağın alt kenarı alt parçanın dış yarısına dayanınca dikiş aralığını sentille ölçün: önde, yanda ve arkada.
3. Söküp üç kez tekrarlayın. Dilde ve dudakta beyazlama, çatlak ya da kalıcı eğilme var mı bakın.
4. **Deneme 2 (+x, rehberin yolu):** üst parçayı alt parçanın +x yanında, dinlenme yüksekliğinde tutun: dudağın alt kenarı alt parçanın dış
   yarısının üst kenarında (y 1005 omzu) dursun. Omuz yüksekliği tutar. Üst parçayı −x yönünde, omuz üstünde kaydırarak yerine getirmeyi
   deneyin; alt parçayı kaldırmayın. Modelde yol boyunca 1–160 mm ortak hacim var, girmesi beklenmez. Nerede durduğunu (dinlenmeden kaç mm
   önce) ve hangi kolun takıldığını (ön / arka) yazın.

**Karar ağacı (sonuç tabloya yazılınca):**
- **Deneme 1 geçer** (aletsiz, üç tekrarda dil çatlamaz ve kalıcı eğilmez, dikiş her yerde ≤ 0,5 mm kapanır): K55 a kalır. Rehber F3 / F4
  takma metni kupondaki yola göre yeniden yazılır: "yukarıdan (+y) indir; alt kenar alttaki bandın dilinin dışından geçer, önce arka ve
  yan, en son ön". Rehber "+x'ten getir" yolunu yalnız deneme 2 de geçerse tutar; deneme 2 geçmezse rehber +y yolunu yazar.
- **Deneme 1 geçmez** (dil ya da dudak kırılır, ön bölüm girmez ya da dikiş açık kalır): K55 b sonraki geometri paketinde uygulanır. Dilde
  pah ya da ön / arka yarıda ters bindirme olur. Değişecek yer bindirme dili (`kabuk_parcalar.py` dil bölgesi; `arayuz.KABUK_BINDIRME` 12,
  `KABUK_BINDIRME_BOSLUK` 0,25); kabuk çakışma taraması gerekir. Hangi bölümün takıldığını (ön / yan / arka) yazın.
- Her iki durumda sol yarı, x = 0 dikişi, omuz ve çerçeve için yazılan sonuç "sağ yarı kuponundan çıkarım" diye işaretlenir (etek ön
  kendi kuponuyla denenir, aşağıda).

| Tarih | Malzeme | Deneme 1 +y (elle / zor / girmedi) | Takılan bölüm | Dikiş aralığı ön / yan / arka | 3 tekrar sonrası dil | Deneme 2 +x (durduğu yer, kol) | Not |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Gerekenler: sentil, kumpas. İnsert ve vida gerekmez; dilimdeki ısıl gömme boss'ları ve delikleri kullanılmaz.

## K55 etek ön bandı kuponu (`../kabuk/etek_kuponu.py`, 19 Kasım, P10.8c)

Rehber F1 (adım 33) ön sağ / sol bandı "yerinin 10 mm önünde yandan getir, sonra önden içeri (−z) it" diye takar. Son 10 mm'de engel
z +105 L braketinin M3 perçin somunu flanşı. Kupon gerçek parçaların dilimi (`kabuk-montaj.FCStd`, sağ):
- **Üst parça** (`../kabuk/stl/etek-kuponu-ust.stl`, 8,0 × 42,5 × 29,5 mm, ≈ 3,6 g, 6 dk): "Etek on sag" dilimi; dudak, z +105 boss'u,
  flanş cebi, Ø3,4 geçiş.
- **Alt parça, flanşlı** (`etek-kuponu-alt-flansli.stl`, 20,0 × 52,5 × 33,0 mm, ≈ 8,8 g, 15 dk; **ilk deneme bununla**): "Etek orta sag" dilimi
  (dil) + "Etek braketi sag z+105" dik ayağı + perçin somununun CAD şekli tek parça + taşıyıcı (ayak arkasında blok, üstte plaka).
- **Alt parça, delikli** (`etek-kuponu-alt.stl`, ≈ 8,6 g): aynı, ayakta Ø5,1 delik; gerçek M3 perçin somunu takılır (perçin aleti gerekir).

Modelde rehberin yolu kuponda ve tam bantla aynı ortak hacim eğrisini veriyor: yan bacak serbest, −z bacağında perçin somunu dz
0,5–8,5 mm, en çok 10,0 mm³; yerinde 0 (`../kabuk/etek-kuponu.json` `yol`).

**Sınır.** Dilim kısa (y 106,5–136) ve gerçek banttan serttir; taşıyıcı gerçek braketten serttir. Elde serbest tutulan dilim flanşın üstünden döndürülerek geçirilebilir, gerçek bant (234 × 175 mm, z +88 dikişine bağlı) geçirilemez. Bu yüzden 'geçti' yalnız aşağıdaki kısıtlı hareketle gerçek bant için kanıt sayılır. 'Geçmedi' gerçek bant için kesin değildir (gerçek bant esneyebilir): belirsiz, K55 b. Kupon sağ banttan kesildi; sol bant için sonuç ayna çıkarımıdır.

**Malzeme.** Kuponda perçin somunu PETG ayağa takılır, gerçek parçada ayak 2 mm alüminyumdur: sıkınca ayak ezilebilir ya da çatlayabilir, flanş yüksekliği gerçektekinden farklı olabilir. İlk deneme flanşlı biçimle (alet istemez); delikli biçim perçin somunu ve aleti gelince, flanşın ayak üstündeki yüksekliği kumpasla ölçülerek (tasarım 0.8 mm).

**Baskı.** PETG, bant yönünde (ters). Üst parçanın tablaya teması dar (3 × ≈ 36 mm, boy 29,5 mm): brim (≥ 5 mm) önerilir.

**Test (hareketi kısıtlı):**
- Alt parça (ilk deneme flanşlı biçim) üst plakası alta gelecek şekilde mengeneye ya da masaya kıskaçla sabitlenir; dil ve braket ayağı serbest kalır.
- Üst parçanın dış yüzü (dudak yüzü) düz bir takoza (cetvel ya da tahta blok) bant / yapıştırıcıyla tutturulur; üst parça yalnız takozdan itilir, elle eğilmez, döndürülmez. Takoz yüzü alt parçanın dış duvarına paralel tutulur.
1. Üst parçayı yerinin 10 mm önünde (dikişten 10 mm uzakta) alt parçanın +x yanına koy; yalnız x ekseninde (−x yönünde) kaydırarak duvar hizasına getir. Model: bu bacak serbest.
2. Yalnız −z yönünde (dikişe doğru) 10 mm it; takoz duvara paralel kalır, üst parça dönmez. Model: dz 0,5–8,5 mm arasında perçin somunu flanşı ile en çok 10,0 mm³ ortak hacim.

**Geçti:** Elle itişle (alet ve çekiç yok) dudak dikişe oturur: dikiş aralığı ≤ 0,5 mm (sentil), boss deliği somunla eksenli (M3×14 elle girer); flanşta, boss'ta ve dudakta beyaz iz, çatlak ya da kalıcı eğilme yok. Üç kez sök-tak, aynı sonuç.

**Geçmedi:** Elle itişle oturmaz, ancak üst parça döndürülerek / eğilerek geçer, ya da beyazlama / çatlak çıkar. Sonuç belirsiz sayılır (gerçek bant esneyebilir): K55 b ya da tam bantla deneme.

**Sonuca göre:** Geçti: K55 a etek ön için kalır; rehber F1 'kuponla denenmedi' notu 'kuponla denendi (tarih)' olarak yeniden yazılır. Geçmedi: belirsiz; K55 b (tasarım değişikliği) ya da gerçek bantla deneme, karar Ahmet'te.

Sonuç bu tabloya yazılır:

| Tarih | Malzeme | Biçim (flanşlı / delikli) | Hareket 1 (x) | Hareket 2 (−z): oturdu / takıldığı dz mm | Dikiş aralığı | İz / çatlak | Not |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Gerekenler: mengene ya da kıskaç, düz takoz, sentil, kumpas; delikli biçim için M3 perçin somunu (düz flanşlı, 2 mm Al için) ve perçin
aleti; M3×14 ISO 7380.

## Kupon tazeliği denetimi (`kupon_tazelik.py`, 19 Kasım)

Kupon betikleri ölçüyü kaynak parçadan okur. Kaynak değişirse kupon, betik yeniden koşulana kadar eski kalır. Denetim FreeCAD istemez
ve depoya yazmaz:
- yanak, bant ve etek ön bandı kuponlarında JSON'daki kaynak FCStd md5'ini ve STL md5'ini bugünkü dosyalarla karşılaştırır;
- M7'de kaynak `dirsek-montaj.FCStd` md5'ini, kupon STL md5'lerini ve `arayuz` bloğunu bugünkü `arayuz.py` ile karşılaştırır.
  19 Kasım P10.8c'den beri "BİLİNEN ESKİ" istisnası yok (D / E onarıldı): her fark ESKİ.

`py -3 tasarim/freecad/test/kupon_tazelik.py` (depo kökünden). Çıkış 0: taze; 1: en az bir eski ya da eksik dosya. `--kati` artık
etkisiz (uyumluluk için kabul edilir). Zincire bağlı değil; kupon basmadan önce ve kafa ya da kabuk değişen her paketin sonunda elle koşulur. Eski
çıkarsa ilgili kupon betiğini yeniden koşun (`../kafa/yanak_kuponu.py`, `../kabuk/bant_kuponu.py`, `../kabuk/etek_kuponu.py`, `m7_kuponlari.py`).
