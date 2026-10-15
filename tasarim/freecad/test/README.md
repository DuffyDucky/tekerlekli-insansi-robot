# Test kuponları

Büyük parçaları basmadan önce geçme, ısıl gömme somun ve kelepçe ölçülerini denemek için küçük baskılar. Hepsi desteksiz,
tek başına basılır. Ölçüler `arayuz.py`'den okunur. Kupon betikleri arayüzü değiştirmez: sonucu ekip ölçer, karar
`arayuz.py`'ye elle yazılır (her kuponun "sonuç nereye yazılır" satırı).

| Betik | Kuponlar | Çıktı |
|---|---|---|
| `tolerans_kuponu.py` (11 Ekim) | A: 6808 dış bilezik Ø52 yuvaları · B: 625ZZ yuvası, 6808 iç bilezik mili, M3/M5 ısıl gömme (dikey, L + 0,5) | `stl/kupon-a-*`, `stl/kupon-b-*`, `tolerans-kuponu.step` |
| `m7_kuponlari.py` (15 Ekim, M7) | C: ısıl gömme L + 1, dikey + yatay · D1/D2: dirsek sıkma bileziği · E: üst kol tüpü halkası | `stl/kupon-c..e-*`, `m7-kuponlari.step`, `m7-kupon-sonuc.json` |

Çalıştırma (README'deki başlatıcıyla, ~10 s):
`FC_SCRIPT=$R/test/m7_kuponlari.py "$FC" $L`

## M7 kuponları (`m7_kuponlari.py`)

| Kupon | Ölçü (mm) | Malzeme | Kütle %100 / tahmini | Süre (tahmini) | Baskı |
|---|---|---|---|---|---|
| C ısıl gömme L + 1 | 61 × 17,2 × 14 | PETG **ve** PETG-CF (iki kez) | 13,4 / 7,5 g | 13 dk | 46° üstü çıkıntı yalnız yatay delik tepeleri (≤ Ø6,6) |
| D1 kelepçe, kesiksiz | 71 × 72 × 33 | çatalın malzemesi (şu an PETG) | 87,9 / 40,9 g | 70 dk | ters (bilezik ağzı tablada); yatay tavan yalnız V oluğun 0,25 mm basamakları |
| D2 kelepçe, kökte boşaltmalı | 71 × 72 × 33 | D1 ile aynı | 86,2 / 41,4 g | 71 dk | aynı; boşaltma dik yarık (köprü yok) |
| E tüp halkası | Ø56 × 36 | üst kol tüpünün malzemesi (PETG) | 17,9 / 14,3 g | 24 dk | dik, uç tablada; 5 mm brim |
| **Toplam** (C bir kez) | | | **205 / 104 g** | **~3 sa** | C ikinci malzemede +7,5 g, +13 dk |

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
| 1 | Ø4,0 yuvarlak | Ø6,4 yuvarlak |
| 2 | Ø3,9 damla | Ø6,2 damla |
| 3 | Ø4,0 damla | Ø6,4 damla |
| 4 | Ø4,1 damla | Ø6,6 damla |
| noktasız (üst yüz) | Ø4,0 dikey, 6,7 derin | Ø6,4 dikey, 8,0 derin |

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
bilezik kökte (y −140) alın kapağına bağlı olduğu için kapanma kökte sıfır, uçta en büyük. Doğrusal kabulle tüp pime
yalnız uçtaki ~5,6 mm boyunca bastırılır.

- **D1** gerçek çatalın y −148…−115 dilimidir: alın kapağı, köprü bandı, 45° destek, pim (içi boş, 45° tavan), 4 mm yarıklı
  bilezik, kulaklar, 2 × M3 deliği, M1 kablo oluğu. Ölçüler `arayuz.DIRSEK`, `GECME`, `TUP_PIM_R`; arayüzde olmayanlar
  `dirsek_parcalar.py` 97–127. satırlarla aynıdır.
  - **Doğrulama:** `dirsek-montaj.FCStd` içindeki "Dirsek catali" aynı dilimle kesildi. Hacim 69.176,9 mm³, iki yönlü fark
    0,000 mm³ (`m7-kupon-sonuc.json` → `d1_fcstd_dogrulama`). Çatal değişirse betik bunu yakalar.
- **D2:** D1 + kökte boşaltma (K önerisi: bilezik kapaktan ~270° ayrılsın).
  - Desteksiz basılsın diye ayrılma yatay bir kesik değil. Kapak boyunca **dik halka yarığı**: r 28,1…29,3 (1,2 mm), θ −225…45°
    (θ tüp ekseni çevresinde −Z'den +X'e). Ölçülen bağlı sektör θ 45…120°.
  - Bağlı sektör bilerek **+X köprü bandına** (θ 59…121) konuldu. Gerçek çatalda dış kol ve horn yükü pime köprü üzerinden
    gider, bu yol kesilemez. Bu yüzden simetrik "ön 90° bağlı" seçenek gerçek parçaya uygulanamaz.
  - Tüp alın yuvasında V oluk yerine pimden dışa yükselen 45° koni tavan var (askıda kenar kalmasın diye). Bu yüzden tüp
    0,25 mm daha derine (y −140,25) oturur. Kavrama testine etkisi yok.
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
   tahmini). Kalan yarığı sentille ölçün: uçta (y −121 cıvatası, ağız tarafı) ve kökte (y −132 cıvatası, kapak tarafı).
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
