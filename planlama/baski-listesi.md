# Baskı listesi (1,58 m ana tasarım; 09.11.2026)

Önceki sürümler: 125 cm V3 (11 / 15 Ekim 2026, 50 parça), 1,65 m (29 Ekim 2026, 63 parça) ve 1,58 m'nin ilk listesi (03.11.2026, 65 parça;
kafa satırları o gün 7" modelden). Bu liste 09.11.2026'da güncel ana modele göre yenilendi (F4c / P4.3): 10,1" QLED kafa, göğüs ekranı
çerçevesi ve VESA taşıyıcı, hub takozlu üst arka kapak, hoparlör kabı ve kelepçesi, omuz göbeği durdurucu dişi.
**Kaynak zinciri (F6b, P6.2: tek analiz):** bütün baskı parçaları tek yöntemle `tasarim/freecad/lale158/baski_analiz_ortak.py` (FreeCAD;
geometri modüllerin `*_parcalar.py`'sinden, FCStd nesnesinin hacmiyle eşit) → `tasarim/freecad/lale158/baski-analiz.json` (yön, destek alanı ve
filamenti, g, süre, X2D; 45° eşik, tasarım yönü; doluluk kabuk 0,9, küçük parça 0,8, omuz PETG-CF 0,8–0,9; 10 mm³/s) → `planlama/y2/Y2b-baski.py` →
`planlama/y2/Y2b-baski.json` → bu dosya. Kabuk ve kafa satırlarını `tasarim/freecad/lale158/baski_listesi_guncelle.py` yazar; öteki
satırlar, ek sütunlar ve parti planı F4c'den (`planlama/d158/F4c-partiler.md`). Denetim: `py -3 planlama/d158/F4c-dogrula.py` (her satırın
JSON anahtarı, toplamlar, betik çıktısı, tek analizde her parça bir kez). Ana montajın BOM'u (`tasarim/freecad/montaj/robot-bom.csv`, `Baski` satırları) aynı 72 parçayı sayıyor.
Yazıcı: Bambu Lab X2D (246 × 246 × 250 mm); **72 parçanın hepsi X2D'ye sığıyor** (tek analiz `x2d_sigar`; en büyük ölçü 235,0 mm, göğüs
bandı yüksekliği). **13 adet destekli** basılır (9 tür): Göğüs bandı sağ (kabuk), Göğüs bandı sol (kabuk), Göğüs ekranı VESA taşıyıcı (kabuk), Omuz yuvası (omuz, ×2), Omuz göbeği (omuz, ×2), S1 kablo tamburu (omuz, ×2), Kol çatalı (omuz, ×2), Yüz kabuğu (ön) sağ (kafa), Arka kafa kabuğu sağ (kafa). Diğer 59 parça desteksiz. Filament ve süreye destek malzemesi dahil
(toplam 124 g, tahmini: destek hacmi × 0,15 × 1,27 g/cm³; dilimleyicinin verdiği esastır).

## 158 cm güncellemesi (09.11.2026)

Boy 1,58 m, göğüste 11,6" gömülü ekran, kafada 10,1" QLED. Kabuk ve kafa satırları bu betikle `Y2b-baski.json`'dan; öteki satırlar ve ek sütunlar F4c'de (denetim `planlama/d158/F4c-dogrula.py`). Güncel toplam **72 parça, 7,67–7,73 kg, 160–161 sa** (`planlama/y2/Y2b-baski.py`, 6,47 kg PETG + 1,19–1,25 kg PETG-CF).
Parti tablolarında satırı olmayan kabuk / kafa parçası:

yok.

Kabukta destek isteyen parçalar: Gogus bandi sag, Gogus bandi sol, Gogus ekrani VESA tasiyici.

## F6b farkı: tek baskı analizi (09.11.2026, P6.2)

Önce = F6a sonu (`4d1898a:planlama/y2/Y2b-baski.json`; modül analizleri + omuz-baski), sonra = `baski-analiz.json`. Satır başına adet × g;
yalnız fark ≥ 1 g ya da destek var/yok değişen satırlar. Nedenler `planlama/d158/F6b-gunluk.md` §3.

| Parça | Adet | Önce (g) | Sonra (g) | Destek (g, sonra) | Destek önce → sonra |
|---|---|---|---|---|---|
| kabuk Göğüs bandı sağ | 1 | 219,0 | 234,3 | 15,6 | var → var |
| kabuk Göğüs bandı sol | 1 | 215,0 | 229,1 | 14,1 | var → var |
| kabuk Üst arka servis kapağı | 1 | 85,0 | 85,1 | 0,0 | var → yok |
| kabuk Göğüs ekranı VESA taşıyıcı | 1 | 113,0 | 144,8 | 31,7 | var → var |
| omuz Omuz yuvası | 2 | 162,0–179,8 | 163,0–180,4 | 23,0 | var → var |
| omuz Kol çatalı | 2 | 197,4–219,2 | 200,0–222,0 | 25,4 | var → var |
| **Toplam (72 parça)** | **72** | **7604,8–7662,4** | **7668,9–7726,7** | **124,5** | 14 → 13 adet destekli |

| Toplam | Önce (F6a) | Sonra (F6b) | Fark |
|---|---|---|---|
| Adet | 72 | 72 | 0 |
| Filament | 7,60–7,66 kg | 7,67–7,73 kg | +64,1 / +64,3 g |
| PETG | 6,45 kg | 6,47 kg | +28,3 / +28,3 g |
| PETG-CF | 1,16–1,22 kg | 1,19–1,25 kg | +35,8 / +36,0 g |
| Süre | 158,2–159,4 sa | 159,9–161,1 sa | +1,68 / +1,66 sa |

## 03.11 → 09.11 farkı (F4c)

| Değişiklik | Parça | Adet | Filament | Süre | Neden ve kaynak |
|---|---|---|---|---|---|
| Yeni | Hoparlör kabı ön halka, hoparlör kabı arka (flanşlı) | +2 | +10 g | +0,3 sa | 05.11 B + R1 ses yerleşimi (`d26c7e7`); `kabuk/baski[31]`, `[32]` |
| Yeni | Hoparlör kelepçesi | +1 | +5 g | +0,1 sa | F1a P1.7 arka tutucu (`76a5701`); `kabuk/baski[33]` |
| Yeni | Ekran tırnağı üst / alt, sağ / sol (10,1" QLED tutucu) | +4 | +6,4 g | +0,12 sa | QLED kafa (`bcaa6df`, 04.11); `kafa/baski[10…13]` |
| Değişti | Üst arka servis kapağı: hub takozu (USB hub kapak içinde) | 0 | +5 g | +0,1 sa | 05.11 (`d26c7e7`); kalınlık 3 → 12,5 mm, desteksiz → destekli (`kabuk/baski[13]`) |
| Değişti | Kafa kabukları (QLED ekran yuvası) | 0 | −53,6 g | −1,12 sa | Yüz sağ 119 → 91, yüz sol 110 → 84, arka sağ / sol +0,2 / +0,1 g (QLED `bcaa6df` 04.11, arka sağ B + R1 `d26c7e7` 05.11; `kafa/baski[5…8]`) |
| Değişti | Boyun yükseltme adaptörü | 0 | −3,6 g | −0,08 sa | Yükseklik 62,8 → 58,9 mm (QLED `bcaa6df` 04.11; `kafa/baski[4]`) |
| Değişti | Göğüs ekranı çerçevesi sağ / sol, VESA taşıyıcı | 0 | +4 g / −1 g | 0 | Çerçeve 29 → 31 g (×2), VESA 114 → 113 g ve 64,8 → 63,4 mm (`bcaa6df`, 04.11) |
| Değişti | Omuz göbeği (S2 durdurucu dişi F2, diş kökü r 1,5 F6a) | 0 | +5,4–5,8 g | +0,10–0,12 sa | Ölçü 66 → 77 mm, adet başına 60,6–67,5 → 63,3–70,4 g, destek 5,2 → 5,7 g (`omuz-baski/parcalar[2]`, F2 `ff1c2e9`; kök yayı F6a +0,1 g alt uçta) |
| Malzeme | Göğüs ekranı VESA taşıyıcı | 0 | 0 | 0 | Model PETG-CF (`kabuk_parcalar.py:375-376`, `malzeme="PETG-CF"`) ve `Y2b-baski.py` CF kümesi; eski Renk tablosu beyaz PETG diyordu, düzeltildi |
| **Fark toplamı** | 65 → **72** parça | **+7** | 7,63–7,68 → **7,60–7,66 kg** (−22,4 / −22,0 g) | 158,7–159,9 → **158,2–159,4 sa** (−0,48 / −0,46) | PETG 6,47 → 6,45 kg; PETG-CF 1,16–1,21 → 1,16–1,22 kg |

Kafa satırlarındaki düşüş, 03.11 listesinin kafa satırlarının 7" modelden kalmasından: QLED modeli (04–05.11) yüz kabuklarını inceltti.
Parça sayısının 65 → 72 artışı yalnız küçük parçalardan (en büyüğü 7 g); filament ve süre neredeyse aynı kaldı.

## Özet

| Parti | Ne zaman | Adet | Filament | Baskı süresi |
|---|---|---|---|---|
| 0 | İlk gün: tolerans kuponları (toplama katılmaz) | 8 baskı | 0,26–0,42 kg | ≈ 7–12 sa |
| 1 | Hemen | 27 | 3,37 kg | ≈ 70 sa |
| 2 | Servo ve horn gelip ölçülünce | 25 | 1,33–1,39 kg | ≈ 28–29 sa |
| 3 | 10,1" QLED yüz ekranı gelip ölçülünce | 9 | 0,76 kg | ≈ 16 sa |
| 4 | Etek tasarım kararından sonra (M6 CAD) | 11 | 2,21 kg | ≈ 46 sa |
| **Toplam** | | **72** | **7,67–7,73 kg** | **≈ 160–161 sa** |

| Malzemeye göre | Düz PETG (beyaz) | PETG-CF (siyah) |
|---|---|---|
| Parti 1 | 3,19 kg | 0,18 kg |
| Parti 2 | 0,32 kg | 1,02–1,07 kg |
| Parti 3 | 0,76 kg | 0,00 kg |
| Parti 4 | 2,21 kg | 0,00 kg |
| **Parçalar** | **6,47 kg** | **1,19–1,25 kg** |
| Parti 0 kuponları | 0,08–0,12 kg | 0,18–0,30 kg |
| **Parça + kupon** | **6,56–6,59 kg** | **1,37–1,55 kg** |

Parti ayrıntısı, bağımlılıklar, montaj adımı ve takvim kontrolü: `planlama/d158/F4c-partiler.md`.

**Filament:** parçalar **düz PETG 6,47 kg** + **PETG-CF 1,19–1,25 kg** (`Y2b-baski.json`; omuz doluluğu 0,8–0,9; bütün satırlarda destek dahil,
toplam 124 g, F6b). Kuponlar (Parti 0) PETG 0,08–0,12 kg, PETG-CF 0,18–0,30 kg.
Plan: **9 makara beyaz PETG + 1,5 kg siyah PETG-CF (3 × 0,5 kg)** (`planlama/maliyet.json` `kalemler[107–109]`).
- **PETG yetiyor:** parça + kupon 6,56–6,59 kg, 9 kg'de ≈ 2,4 kg pay (≈ %37).
- **PETG-CF 1,5 kg sınırda, yetmiyor sayılmalı:** parça + kupon 1,37–1,55 kg; 1,5 kg'de pay 130 g (doluluk 0,8 ve kuponların tahmini kütlesiyle) ile −53 g
  (doluluk 0,9 ve %100 kupon). D2 kuponu basılmazsa pay 33–172 g. En büyük CF parçası (kafa servo yuvası) 152 g: tek bir başarısız baskı alt
  durumdaki payı bitiriyor. Karar taslağı `planlama/d158/F4c-gunluk.md` (KT-F4c-1: +1 makara, 0,5 kg, 1.114,03 TL; %15 payla 1.281,13 TL).

## Renk (Ahmet, 11 Ekim 2026: "Tamamen beyaz")

| Renk | Parçalar |
|---|---|
| **Beyaz PETG** | Düz PETG'den basılan her şey: kabuk (gövde, uzatma ve göğüs bantları), etek ve dolgu şeritleri, kafa kabukları, kafa iskeleti, kafa ekranı tırnakları (10,1" QLED), göğüs ekranı çerçevesi (gövde renginde, 04.11), hoparlör kabı ve kelepçesi, üst kol tüpü, ön kol, el, sonar tutucular, akü takozu, servis kapakları (hub takozlu üst arka kapak dahil), S1 kaseti ve kablo tamburu |
| **Siyah PETG-CF** | Yük taşıyan 12 tür (18 adet). Omuz ve dirsek eklemleri siyah görünür; kafa iç parçaları kabuğun, VESA taşıyıcı göğüs ekranının arkasında kalır |

## Malzeme

| Malzeme | Nereye | Neden |
|---|---|---|
| **PETG** (beyaz) | Yukarıdaki beyaz parçalar | Yükü az, büyük parçalar. PETG tok, kolay basılır (camsı geçiş ≈ 80 °C, tahmini). Etekteki ısı ölçülünce kontrol edilmeli (E7) |
| **PETG-CF** | Servo torkunu, rulman yükünü ya da ekran ağırlığını taşıyan 12 tür (aşağıda) | Düz PETG'den rijit, sıkı geçmede ve vida sıkıştırmasında daha az akma (tahmini) |

**PETG-CF ile basılacak parçalar (toplam PETG-CF 1,19–1,25 kg):**

| Modül | Parça | Adet | Taşıdığı yük |
|---|---|---|---|
| omuz | Omuz yuvası | 2 | Bütün kolun momenti; travers ucuna M6 ile bağlı |
| omuz | Rulman kapağı | 2 | 6808-2RS sıkı geçme (Ø52) |
| omuz | Omuz göbeği | 2 | S1 horn torku (DS3235) + rulman mili Ø40; S2 durdurucu dişi (F2) |
| omuz | Kol çatalı | 2 | S2 horn torku (DS3235) + 625ZZ yuvası |
| dirsek | Dirsek çatalı | 2 | Dirsek horn torku; dış kol 8 mm, horn cıvatası M3×12 + 2 pul |
| dirsek | Bilek flanşı | 2 | Bilek horn bağlantısı |
| kafa | Servo yuvası | 1 | Kafanın tamamı bunun üstünde (QLED kafa, kütle `kafa-analiz.json`) |
| kafa | Rulman yuvası | 1 | 6808-2RS yuvası |
| kafa | Boyun mili | 1 | Pan horn torku |
| kafa | Eğme çatalı | 1 | Tilt horn torku (tilt sınırı ±13°, karar 29.10). Montajda tilt servosundan **önce** takılır (M6 C3) |
| kafa | Boyun yükseltme adaptörü | 1 | Pan torku ve kafa ağırlığı (boyun mili ile eğme çatalı arasında; karar 29.10) |
| kabuk | Göğüs ekranı VESA taşıyıcı | 1 | 11,6" göğüs ekranının ağırlığı (VESA 4 × M4, taşıyıcı 2 × M6); model malzemesi PETG-CF (`kabuk_parcalar.py:375-376`) |

**Karar 29.10 (Ahmet):** Y2a'da eklenen **boyun yükseltme adaptörü** (boyun mili ile eğme çatalı arasında, pan torku ve kafa ağırlığı
yolunda) **PETG-CF** ile basılır; CAD'de (`kafa10_lib.py`) malzeme PETG-CF.

**Neden PA-CF değil:** Nem çeker, kurutma ister, pahalı. Bu yüklerde (el yükü ≈ 100 g sınırı, jestler) PETG-CF yeterli olmalı (tahmini).

**Yazıcı şartı:** Karbon katkılı filament sertleştirilmiş çelik nozul ister (X2D fabrikadan 0,4 mm sertleştirilmiş çelik). Okul
yazıcısında nozulun değiştirilmediğini kontrol edin.

**Ayar (PETG-CF):** duvar 5–6, üst/alt 5 katman, doluluk %50–60 gyroid, filament kuru. **Tolerans kuponları (Parti 0) asıl
malzemeyle basılmalı.**

**Destekli kafa kabuğu (karar 29.10):** yüz kabuğu (ön) sağ ve arka kafa kabuğu sağ, x = 0 dikiş dilinde (16 mm şerit, iç yarı duvar)
yüzü tablada baskıda ~1,25 mm yükseklikte konsol bırakıyor. Dilimleyicide yalnız bu bölgelere destek ("support on build plate only"
yeterli değilse boyalı destek); destek dil yüzünden temizlenmeli, dil 1,3 mm et. F6b tek analizi aynı iki parçayı buldu, yalnız dikiş
dilinde (x ≈ −8, tabladan 1,2–2,3 mm; yüz sağ 12,3 cm², arka sağ 30,6 cm², ikisi birlikte ≈ 1,3 g destek; `baski-analiz.json` `destek_bolge`).

**Üst arka servis kapağı (hub takozlu): desteksiz.** F4c'deki "z 2,5'te 197 cm²" (`kabuk-analiz.json` `baski[13]`) kesit hatasıydı: kapak
baskı yönüne 2,27° eğik, flanşın üst yüzü tabladan 1,4988 mm'de; eski yöntemin z 1,5 kesiti bu yüze 1,2 µm yakın düşüp ters normalli yüz
verdi ve bir sonraki katmanın tamamı desteksiz sayıldı. Aynı iki katmanın gerçek farkı 5,01 mm² (45° payının içinde). Tek analiz: destek 0.
Kanıt `baski-analiz.json` `kapak_tani`, `planlama/d158/F6b-gunluk.md` §2.

**Süre:** ≈ 160–161 saat; yazıcı hiç durmazsa ≈ 6,7 gün. Paylaşımlı okul yazıcısında haftada 32–40 sa ile ≈ 4,0–5,0 hafta (tahmini). Parti 1 hemen başlamalı.

## Sıralama mantığı

1. **Parti 0, ilk gün tolerans kuponları** (`tasarim/freecad/test/`, aşağıda). Seçilen ölçü CAD'e girer, büyük parçalar sonra basılır.
2. **Parti 1:** ölçüsü elimizdeki parçaya pek bağlı olmayanlar: gövde, uzatma, göğüs ve omuz bantları, arka servis kapağı, sonar
   tutucular, rulman kapağı, üst kol tüpü. **Partinin sonunda, ilgili kalem gelip ölçülünce:** üst arka servis kapağı (USB hub takozu),
   hoparlör kabı ve kelepçesi (8 Ω hoparlör), göğüs ekranı çerçevesi sağ/sol ve VESA taşıyıcı (11,6" göğüs ekranı; VESA deliklerinin
   kasadaki yeri ve derinliği doğrulanmadı, `arayuz.py:342`). 7 adet, ≈ 6,4 sa; Parti 1 tablosunun son satırları (`F4c-partiler.md`).
3. **Parti 2:** horn delik dizilimi tahmini (25T disk, M3 delikler 8,5 mm yarıçapta) ve servo gövdeleri (DS3235, MG996R). Gelince
   kumpasla ölçülür, CAD güncellenir, sonra basılır. Omuz göbeğinin diş kökü yarıçapı (r 1,5) F6a'da uygulandı; DS3235 düşme ölçümü (K39) açık.
4. **Parti 3:** kafa ekranı 10,1" QLED 1280×720 (WaveShare, kod 20789). Vida deliği yok, 4 ekran tırnağıyla tutulur; kütle doğrulanmadı.
   Ekran gelip ölçülünce (K32: hocadan mı satın alma mı) ve K2 (AI HAT / boss, P6.1) modele girince kafa iskeleti, kabuklar ve tırnaklar basılır.
5. **Parti 4:** etek ana anahtar deliği (M6 K7) ve H1, H2 servis kapakları (M6 K5, K6) CAD'de; etek havalandırma yarıkları (E7) bekliyor.
   Akü **yerinde** (karar 29.10); akü takozu akü gelince teyit edilip **Parti 1 arasında** basılır (M6 adım 4).

## Tolerans (CAD'de)

| Geçme | CAD değeri | Not |
|---|---|---|
| Vida geçiş delikleri | M3 Ø3,4 · M4 Ø4,5 · M5 Ø5,5 · M6 Ø6,6 (ISO 273 orta) | `arayuz.CLEAR` |
| Servo cepleri | Her yanda +0,2 mm | |
| Omuz yuvası ↔ sigma travers | Her yanda +0,2 mm | |
| Üst kol tüpü ↔ çatal ve dirsek pimi (Ø50,8) | Tüp içi Ø51,3, her yanda 0,25 mm | `arayuz.GECME["tup_pim"]` |
| Isıl gömme somun deliği | M3 Ø4,0 (ruthex M3×5,7), M5 Ø6,4 (tahmini) | `arayuz.INSERT_DELIK`; kuponla doğrulanacak; insert varyantı K31 (A/B/C) açık |
| Kabuk bindirmesi | 0,25 mm boşluk | `arayuz.KABUK_BINDIRME_BOSLUK` |
| Rulman yuvaları (6808 Ø52, 625ZZ Ø16), Ø40 mil | Tam ölçü (sıkı geçme) | **Kupondan sonra** seçilen ölçü uygulanacak |
| Horn delik dizilimi | Tahmini | Horn gelince kumpasla |

### Tolerans kuponları (Parti 0)

Kuponlar `tasarim/freecad/test/stl/` (A, B: `tolerans_kuponu.py`; C, D1, D2, E: `m7_kuponlari.py`, `test/README.md`). 8 baskı:
B ve C hem PETG-CF hem beyaz PETG; D2 yalnız D1 geçmezse ya da karşılaştırma için. Toplam PETG 0,08–0,12 kg, PETG-CF 0,18–0,30 kg, ≈ 7,3–12,0 sa
(tahmini kütleyle alt, %100 dolulukla üst değer; D2'siz ≈ 6,2–9,5 sa). Kupon tablosu, K31 seçeneğine göre etkisi ve omuz dişi kökü notu: `planlama/d158/F4c-partiler.md`.

| Kupon | Malzeme | Ne denenir | Filament (g) |
|---|---|---|---|
| A | PETG-CF | 6808-2RS dış bileziği: Ø52,0 / 52,1 / 52,2 / 52,3 (omuz rulman kapağı, kafa rulman yuvası) | 26,0 |
| B | PETG-CF | 625ZZ Ø16,0…16,3 · Ø40 mil Ø39,8…40,1 · M3 Ø3,8…4,1 / M5 Ø6,2…6,6 dikey (L + 0,5) | 60,0–87,9 |
| B | PETG | aynı kupon beyaz PETG'de (kabuk ısıl gömme delikleri) | 60,0–87,9 |
| C | PETG-CF | Isıl gömme L + 1: M3 Ø3,9…4,1, M5 Ø6,2…6,6, yatay + dikey | 7,5–13,4 |
| C | PETG | aynı kupon beyaz PETG'de | 7,5–13,4 |
| D1 | PETG-CF | Dirsek kelepçesi (çatal dilimi), kesiksiz | 40,9–87,9 |
| D2 (koşullu) | PETG-CF | Dirsek kelepçesi, kökte boşaltmalı (D1 geçerse yalnız karşılaştırma) | 41,4–86,2 |
| E | PETG | Üst kol tüpü halkası (tüp–pim / tüp–bilezik geçmesi) | 14,3–17,9 |

Rulman elle (ya da mengeneyle hafif) bastırınca oturmalı; ısıl gömme somun havyayla düz girmeli, vida sıkınca dönmemeli. Sonuç CAD'e uygulanır ve STL'ler
yeniden çıkarılır.

## STL durumu

Omuz STL'leri (`tasarim/freecad/omuz/stl/`, 09.11 F2 koşusu; `omuz-gobegi.stl` dişli) ve kuponlar (`tasarim/freecad/test/stl/`) var. Diğer
modüllerin baskı parçaları kupon sonucundan sonra FreeCAD'den toplu dışa aktarılmalı (açık iş; P6.1'de modüller yeniden üretilirken).

## Parti tabloları

Sütunlar: ölçü tek analizdeki baskı yönündeki kutu (mm), filament ve süre adet başına, destek dahil (omuz PETG-CF satırlarında aralık doluluk
0,8–0,9). Malzeme `Y2b-baski.py` CF kümesinden. Destek sütununda alan ve destek filamenti (`baski-analiz.json` `destek_alan_mm2`, `destek_g`).
Kaynak: `baski-analiz/parcalar[i]` = `tasarim/freecad/lale158/baski-analiz.json` → `parcalar[i]` (yön, destek bölgeleri, en az destekli aday yön,
FCStd nesnesi); `Y2b[i]` = `planlama/y2/Y2b-baski.json` → `satirlar[i]`. X2D: tek analizdeki `x2d_sigar` ve ölçü ≤ 246 × 246 × 250.
Montaj adımları `F4c-partiler.md`'de. **Eski analiz:** yok; tek analiz 2026-11-09 tarihli, geometri her modülün `*_parcalar.py`'sinden yeniden
üretildi ve FCStd'lerle hacimce eşit (`kaynak.hacim_esit`; eşit olmayan: yok). Ayrıntı `planlama/d158/F6b-gunluk.md`.

## Parti 1 — Hemen

27 adet · 3,37 kg filament (PETG 3,19, PETG-CF 0,18) · ≈ 70,2–70,3 saat. Bağımlılık: Parti 0 sonucu + STL dışa aktarma. Satın alınan parçaya bağlı 7 satır partinin sonunda, ilgili kalem gelip ölçülünce basılır: üst arka kapak (USB hub), hoparlör kabı ve kelepçesi (8 Ω hoparlör, K36/K6), göğüs ekranı çerçevesi sağ/sol ve VESA taşıyıcı (11,6" göğüs ekranı; VESA delik yeri doğrulanmadı, `arayuz.py:342`; F4c-kontrol B-2).

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Malzeme | Tabla yönü | Destek | X2D | Kaynak (JSON) | Bağlı olduğu kalem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | taban | Sonar tutucu sol | 1 | 61 × 61 × 8 | 5 | 0,11 | PETG | arka yüzü (ray tarafı) tablada | desteksiz | sığar | `baski-analiz/parcalar[1]` · Y2b[1] | — |
| ☐ | taban | Sonar tutucu orta | 1 | 66 × 66 × 8 | 6 | 0,12 | PETG | arka yüzü (ray tarafı) tablada | desteksiz | sığar | `baski-analiz/parcalar[2]` · Y2b[2] | — |
| ☐ | taban | Sonar tutucu sağ | 1 | 61 × 61 × 8 | 5 | 0,11 | PETG | arka yüzü (ray tarafı) tablada | desteksiz | sığar | `baski-analiz/parcalar[3]` · Y2b[3] | — |
| ☐ | kabuk | Gövde alt bandı sağ | 1 | 170 × 137 × 226 | 299 | 6,23 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[4]` · Y2b[4] | Kupon B/C (ısıl gömme deliği) |
| ☐ | kabuk | Gövde alt bandı sol | 1 | 170 × 125 × 226 | 280 | 5,84 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[5]` · Y2b[5] | Kupon B/C |
| ☐ | kabuk | Gövde uzatma bandı 1 sağ | 1 | 170 × 137 × 170 | 224 | 4,67 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[6]` · Y2b[6] | Kupon B/C |
| ☐ | kabuk | Gövde uzatma bandı 1 sol | 1 | 170 × 125 × 170 | 211 | 4,39 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[7]` · Y2b[7] | Kupon B/C |
| ☐ | kabuk | Gövde uzatma bandı 2 sağ | 1 | 170 × 137 × 170 | 224 | 4,67 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[8]` · Y2b[8] | Kupon B/C |
| ☐ | kabuk | Gövde uzatma bandı 2 sol | 1 | 170 × 125 × 170 | 211 | 4,39 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[9]` · Y2b[9] | Kupon B/C |
| ☐ | kabuk | Gövde orta bandı sağ | 1 | 214 × 162 × 227 | 272 | 5,66 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[10]` · Y2b[10] | Kupon B/C |
| ☐ | kabuk | Gövde orta bandı sol | 1 | 214 × 150 × 227 | 262 | 5,45 | PETG | dik (alt kenarı tablada) | desteksiz | sığar | `baski-analiz/parcalar[11]` · Y2b[11] | Kupon B/C |
| ☐ | kabuk | Göğüs bandı sağ | 1 | 217 × 164 × 235 | 234 | 4,90 | PETG | dik (alt kenarı tablada) | **destekli**: 10,7 cm², 15,6 g; cep üst kenarı (köprü 160 mm) + z 12–15'te alt kenar çıkıntısı | sığar | `baski-analiz/parcalar[12]` · Y2b[12] | Kupon B/C; 11,6" ekran cebi |
| ☐ | kabuk | Göğüs bandı sol | 1 | 217 × 152 × 235 | 229 | 4,79 | PETG | dik (alt kenarı tablada) | **destekli**: 3,6 cm², 14,1 g; cep üst kenarı (köprü 148 mm) | sığar | `baski-analiz/parcalar[13]` · Y2b[13] | Kupon B/C; 11,6" ekran cebi |
| ☐ | kabuk | Omuz bandı sağ | 1 | 164 × 156 × 102 | 184 | 3,84 | PETG | ters (üst kapak tablada) | desteksiz | sığar | `baski-analiz/parcalar[14]` · Y2b[14] | Kupon B/C |
| ☐ | kabuk | Omuz bandı sol | 1 | 156 × 152 × 102 | 178 | 3,71 | PETG | ters (üst kapak tablada) | desteksiz | sığar | `baski-analiz/parcalar[15]` · Y2b[15] | Kupon B/C |
| ☐ | kabuk | Arka servis kapağı | 1 | 190 × 160 × 3 | 98 | 2,04 | PETG | dış yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[16]` · Y2b[16] | — |
| ☐ | omuz | Rulman kapağı | 2 | 71 × 71 × 14 | 15–17 | 0,32–0,36 | PETG-CF | +X: x = 146 yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[57]` · Y2b[57] | 6808-2RS (kupon A) |
| ☐ | omuz | Üst kol tüpü | 2 | 56 × 56 × 130 | 54 | 1,13 | PETG | +Y: y = -170 yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[61]` · Y2b[61] | Kupon E (tüp–pim geçmesi) |
| ☐ | kabuk | Üst arka servis kapağı | 1 | 168 × 150 × 12 | 85 | 1,77 | PETG | dış yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[17]` · Y2b[17] | USB hub 4'lü (72 × 25 × 19) ölçüsü: hub takozu; Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| ☐ | kabuk | Göğüs ekranı çerçevesi sağ | 1 | 207 × 147 × 10 | 31 | 0,65 | PETG | arka yüzü (flanş) tablada | desteksiz | sığar | `baski-analiz/parcalar[28]` · Y2b[28] | 11,6" göğüs ekranı kasası (284,65 × 182,25); Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| ☐ | kabuk | Göğüs ekranı çerçevesi sol | 1 | 207 × 147 × 10 | 31 | 0,65 | PETG | arka yüzü (flanş) tablada | desteksiz | sığar | `baski-analiz/parcalar[29]` · Y2b[29] | 11,6" göğüs ekranı kasası (284,65 × 182,25); Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| ☐ | kabuk | Göğüs ekranı VESA taşıyıcı | 1 | 106 × 100 × 63 | 145 | 3,05 | PETG-CF | VESA plakası tablada; arka flanş destekli | **destekli**: 38,1 cm², 31,7 g; arka flanş (z 32–58) | sığar | `baski-analiz/parcalar[30]` · Y2b[30] | 11,6" göğüs ekranı VESA delikleri (yer ve derinlik doğrulanmadı, `arayuz.py:342`); Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| ☐ | kabuk | Hoparlör kabı ön halka | 1 | 46 × 46 × 7 | 3 | 0,06 | PETG | VARSAYIM kap; ön halka, düz (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[35]` · Y2b[35] | 8 Ω hoparlör (K36 stok, K6 yön); kap ölçüsü VARSAYIM; Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| ☐ | kabuk | Hoparlör kabı arka (flanşlı) | 1 | 62 × 62 × 13 | 7 | 0,15 | PETG | VARSAYIM kap; flanş yüzü tablada (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[36]` · Y2b[36] | 8 Ω hoparlör (K36, K6); VARSAYIM; Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| ☐ | kabuk | Hoparlör kelepçesi | 1 | 57 × 57 × 14 | 4 | 0,09 | PETG | VARSAYIM; köprü üst yüzü tablada, bacaklar yukarı (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[37]` · Y2b[37] | 8 Ω hoparlör (K36, K6); VARSAYIM; Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |

## Parti 2 — Servo ve horn gelip ölçülünce

25 adet · 1,33–1,39 kg filament (PETG 0,32, PETG-CF 1,02–1,07) · ≈ 27,9–29,0 saat. Bağımlılık: DS3235, MG996R, 25T horn (teslim S+1); omuz göbeği kök yarıçapı r 1,5 F6a'da uygulandı (K39 DS3235 düşme ölçümü açık); S1 kaseti kablo kalınlığı (K1).

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Malzeme | Tabla yönü | Destek | X2D | Kaynak (JSON) | Bağlı olduğu kalem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | kabuk | S1 kaset gövdesi sağ | 1 | 112 × 111 × 6 | 10 | 0,20 | PETG | arka yüzü (x 152) tablada | desteksiz | sığar | `baski-analiz/parcalar[31]` · Y2b[31] | Kablo kalınlığı ≤ 1,4 mm (K1) |
| ☐ | kabuk | S1 kaset kapağı sağ | 1 | 112 × 111 × 4 | 7 | 0,15 | PETG | flanş dış yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[32]` · Y2b[32] | — |
| ☐ | kabuk | S1 kaset gövdesi sol | 1 | 112 × 111 × 6 | 10 | 0,20 | PETG | arka yüzü (x 152) tablada | desteksiz | sığar | `baski-analiz/parcalar[33]` · Y2b[33] | Kablo kalınlığı ≤ 1,4 mm (K1) |
| ☐ | kabuk | S1 kaset kapağı sol | 1 | 112 × 111 × 4 | 7 | 0,15 | PETG | flanş dış yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[34]` · Y2b[34] | — |
| ☐ | kafa | Servo yuvası | 1 | 88 × 88 × 43 | 152 | 3,16 | PETG-CF | dik: kulak flanşı tablada | desteksiz | sığar | `baski-analiz/parcalar[38]` · Y2b[38] | MG996R gövdesi |
| ☐ | kafa | Rulman yuvası | 1 | 68 × 60 × 36 | 27 | 0,56 | PETG-CF | dik: kulaklar tablada, rulman yuvası yukarı | desteksiz | sığar | `baski-analiz/parcalar[39]` · Y2b[39] | 6808-2RS (kupon A) |
| ☐ | kafa | Boyun mili | 1 | 60 × 60 × 48 | 41 | 0,85 | PETG-CF | dik: horn diski tablada, flanş yukarı (45 derece koni) | desteksiz | sığar | `baski-analiz/parcalar[40]` · Y2b[40] | Pan horn delik dizilimi |
| ☐ | kafa | Eğme çatalı | 1 | 74 × 60 × 49 | 36 | 0,75 | PETG-CF | dik: taban tablada, duvarlar yukarı | desteksiz | sığar | `baski-analiz/parcalar[41]` · Y2b[41] | Tilt horn delik dizilimi |
| ☐ | kafa | Boyun yükseltme adaptörü | 1 | 60 × 60 × 59 | 70 | 1,46 | PETG-CF | dik: alt flanş tablada | desteksiz | sığar | `baski-analiz/parcalar[42]` · Y2b[42] | — |
| ☐ | dirsek | Dirsek çatalı | 2 | 74 × 72 × 74 | 97 | 2,03 | PETG-CF | ters: pim ve bilezik ucu tablada, kollar yukarı | desteksiz | sığar | `baski-analiz/parcalar[52]` · Y2b[52] | Dirsek horn delik dizilimi; kupon D1/D2 |
| ☐ | dirsek | Ön kol gövdesi | 2 | 130 × 129 × 34 | 57 | 1,18 | PETG | ön yüzü tablada, açık arka yukarı | desteksiz | sığar | `baski-analiz/parcalar[53]` · Y2b[53] | MG996R gövdesi |
| ☐ | dirsek | Bilek flanşı | 2 | 28 × 28 × 8 | 4 | 0,09 | PETG-CF | horn yüzü tablada, havşalar yukarı | desteksiz | sığar | `baski-analiz/parcalar[54]` · Y2b[54] | Bilek horn delik dizilimi |
| ☐ | dirsek | El | 2 | 56 × 56 × 85 | 78 | 1,64 | PETG | ters: parmak ucu ve avuç altı tablada, yaka yukarı | desteksiz | sığar | `baski-analiz/parcalar[55]` · Y2b[55] | — |
| ☐ | omuz | Omuz yuvası | 2 | 76 × 76 × 67 | 82–90 | 1,71–1,89 | PETG-CF | -Y: y = 25 yüzü tablada | **destekli**: 22,6 cm², 11,5 g; manşon içi + S1 penceresi | sığar | `baski-analiz/parcalar[56]` · Y2b[56] | DS3235 gövdesi, çekiç somun |
| ☐ | omuz | Omuz göbeği | 2 | 77 × 51 × 49 | 64–71 | 1,33–1,48 | PETG-CF | +X: x = 150 yüzü tablada | **destekli**: 24,3 cm², 5,9 g; flanş altı + diş | sığar | `baski-analiz/parcalar[58]` · Y2b[58] | S1 horn delik dizilimi; kök yarıçapı r 1,5 F6a'da uygulandı (K39 DS3235 düşme ölçümü açık) |
| ☐ | omuz | S1 kablo tamburu | 2 | 87 × 87 × 10 | 6 | 0,12 | PETG | +X: x = 152,5 yüzü tablada | **destekli**: 8,6 cm², 0,8 g; +x dudak altı | sığar | `baski-analiz/parcalar[59]` · Y2b[59] | Göbekle birlikte |
| ☐ | omuz | Kol çatalı | 2 | 76 × 56 × 64 | 100–111 | 2,10–2,32 | PETG-CF | -Z: z = 30,5 yüzü tablada | **destekli**: 20,4 cm², 12,7 g; horn kulağı | sığar | `baski-analiz/parcalar[60]` · Y2b[60] | S2 horn delik dizilimi |

## Parti 3 — 10,1" QLED yüz ekranı gelip ölçülünce

9 adet · 0,76 kg filament (PETG 0,76, PETG-CF 0,00) · ≈ 15,7 saat. Bağımlılık: 10,1" QLED (K32: hocadan mı satın alma mı), K2 (AI HAT / boss, P6.1'de kafa modeline).

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Malzeme | Tabla yönü | Destek | X2D | Kaynak (JSON) | Bağlı olduğu kalem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | kafa | Yüz kabuğu (ön) sağ | 1 | 215 × 151 × 37 | 91 | 1,90 | PETG | ön yüzü tablada | **destekli**: 12,3 cm², 0,4 g; dikiş dili (karar 29.10) | sığar | `baski-analiz/parcalar[43]` · Y2b[43] | QLED (K32) + K2 (P6.1) |
| ☐ | kafa | Yüz kabuğu (ön) sol | 1 | 215 × 135 × 37 | 84 | 1,76 | PETG | ön yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[44]` · Y2b[44] | QLED (K32) + K2 (P6.1) |
| ☐ | kafa | Arka kafa kabuğu sağ | 1 | 215 × 151 × 107 | 230 | 4,80 | PETG | arka yüzü tablada | **destekli**: 30,6 cm², 0,9 g; dikiş dili (karar 29.10) | sığar | `baski-analiz/parcalar[45]` · Y2b[45] | QLED (K32) + K2 (P6.1) |
| ☐ | kafa | Arka kafa kabuğu sol | 1 | 215 × 135 × 107 | 215 | 4,49 | PETG | arka yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[46]` · Y2b[46] | QLED (K32) + K2 (P6.1) |
| ☐ | kafa | Kafa iskeleti | 1 | 224 × 115 × 48 | 128 | 2,66 | PETG | ters: tabla tablada, yanaklar yukarı | desteksiz | sığar | `baski-analiz/parcalar[47]` · Y2b[47] | QLED + kamera delikleri; K2 (P6.1) |
| ☐ | kafa | Ekran tırnağı üst sağ | 1 | 24 × 14 × 8 | 2 | 0,03 | PETG | plaka tablada, dil yukarı (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[48]` · Y2b[48] | QLED kasa ölçüsü |
| ☐ | kafa | Ekran tırnağı üst sol | 1 | 24 × 14 × 8 | 2 | 0,03 | PETG | plaka tablada, dil yukarı (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[49]` · Y2b[49] | QLED kasa ölçüsü |
| ☐ | kafa | Ekran tırnağı alt sağ | 1 | 24 × 14 × 8 | 2 | 0,03 | PETG | plaka tablada, dil yukarı (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[50]` · Y2b[50] | QLED kasa ölçüsü |
| ☐ | kafa | Ekran tırnağı alt sol | 1 | 24 × 14 × 8 | 2 | 0,03 | PETG | plaka tablada, dil yukarı (desteksiz) | desteksiz | sığar | `baski-analiz/parcalar[51]` · Y2b[51] | QLED kasa ölçüsü |

## Parti 4 — Etek tasarım kararından sonra (M6 CAD)

11 adet · 2,21 kg filament (PETG 2,21, PETG-CF 0,00) · ≈ 46,0 saat. Bağımlılık: E7 etek havalandırma yarıkları (elektrik.md:505); akü (K30) → akü takozu.

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Malzeme | Tabla yönü | Destek | X2D | Kaynak (JSON) | Bağlı olduğu kalem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ☐ | taban | Akü ön takozu | 1 | 125 × 125 × 25 | 72 | 1,50 | PETG | alt yüzü tablada | desteksiz | sığar | `baski-analiz/parcalar[0]` · Y2b[0] | Akü (K30) gelince ölçü teyidi; Parti 1 arasında basılır (M6 adım 4 taban aşamasında lazım; proje-plani.md kritik yol 4–5) |
| ☐ | kabuk | Etek arka sağ | 1 | 234 × 190 × 227 | 366 | 7,62 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[18]` · Y2b[18] | E7 havalandırma yarıkları CAD'e; ana anahtar (M6 K7) + XT60 + H1 (K5) |
| ☐ | kabuk | Etek arka sol | 1 | 222 × 175 × 227 | 362 | 7,54 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[19]` · Y2b[19] | E7 havalandırma yarıkları CAD'e; ana anahtar (M6 K7) + XT60 + H1 (K5) |
| ☐ | kabuk | Etek orta sağ | 1 | 222 × 199 × 227 | 216 | 4,51 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[20]` · Y2b[20] | E7 havalandırma kararı |
| ☐ | kabuk | Etek orta sol | 1 | 222 × 199 × 227 | 216 | 4,51 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[21]` · Y2b[21] | E7 havalandırma kararı |
| ☐ | kabuk | Etek ön sağ | 1 | 234 × 190 × 227 | 372 | 7,75 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[22]` · Y2b[22] | E7 havalandırma kararı |
| ☐ | kabuk | Etek ön sol | 1 | 222 × 175 × 227 | 363 | 7,55 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[23]` · Y2b[23] | E7 havalandırma kararı |
| ☐ | kabuk | Etek dolgu şeridi arka | 1 | 192 × 88 × 227 | 98 | 2,04 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[24]` · Y2b[24] | — |
| ☐ | kabuk | Etek dolgu şeridi ön | 1 | 192 × 88 × 227 | 107 | 2,24 | PETG | ters (üst plakası tablada) | desteksiz | sığar | `baski-analiz/parcalar[25]` · Y2b[25] | — |
| ☐ | kabuk | Etek servis kapağı H1 (sigorta kutusu) | 1 | 111 × 111 × 3 | 24 | 0,51 | PETG | düz (alt yüzü tablada) | desteksiz | sığar | `baski-analiz/parcalar[26]` · Y2b[26] | — |
| ☐ | kabuk | Etek servis kapağı H2 (ana sigorta) | 1 | 70 × 56 × 3 | 14 | 0,28 | PETG | düz (alt yüzü tablada) | desteksiz | sığar | `baski-analiz/parcalar[27]` · Y2b[27] | — |
