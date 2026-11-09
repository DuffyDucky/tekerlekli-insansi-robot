# Baskı listesi (1,58 m ana tasarım; 03.11.2026)

Önceki sürümler: 125 cm V3 (11 / 15 Ekim 2026, 50 parça) ve 1,65 m (29 Ekim 2026, 63 parça). Bu liste 1,58 m ana montaja (`tasarim/freecad/montaj/`, 1.150 parça, baskı 65 adet; `tasarim/freecad/lale158/lale158-kontrol.json`) göre güncellendi. Kaynak: modül analizleri `tasarim/freecad/<modül>/<modül>-analiz.json` (`baski` alanı; %80 doluluk,
10 mm³/s) ve omuz için M4 baskı analizi `tasarim/freecad/omuz/omuz-baski.json` (PETG-CF doluluk 0,8–0,9; 29 Ekim 2026'da 1650 omuz FCStd'sinden koşuldu; 158 cm'de omuz ve kollar yalnız aşağı indi, geometri değişmedi). Toplamlar ve tablolar `planlama/y2/Y2b-baski.py` → `Y2b-baski.json`.
Yazıcı: Bambu Lab X2D (246 × 246 × 250 mm); **65 parçanın hepsi X2D'ye ve okul tablasına (250³) sığıyor** (en büyük ölçü 235 mm, `Y2b-baski.json`).
**13 adet destekli** basılır: omuzda omuz yuvası, omuz göbeği, kol çatalı, S1 kablo tamburu (ikişer), **kafa kabuğunun sağ ön
(yüz kabuğu sağ) ve sağ arka parçası** (karar 29 Ekim 2026: dikiş dili 16 mm şerit, ~1,25 mm konsol bölgeleri destekli; dikiş biçimi
değişmez), göğüs bandı sağ ve sol (cep üst kenarı), göğüs ekranı VESA taşıyıcı. Diğer 52 parça desteksiz. Göğüs bantlarında 11,6" gömülü ekran cebi var; bantlar Parti 1'de.

## 158 cm güncellemesi (03.11.2026)

Boy 1,58 m, göğüste 11,6" gömülü ekran. Kafa satırları hâlâ 7" ekranlı modelden: 10,1" QLED kararı (03.11 gece) modele girince kafa iskeleti ve kafa kabukları değişecek, adet ve gram o zaman yenilenir. Kabuk ve kafa satırları `*-analiz.json`'dan güncellendi. Güncel toplam **65 parça, 7,63–7,68 kg, 159–160 sa** (`planlama/y2/Y2b-baski.py`, 6,47 kg PETG + 1,16–1,21 kg PETG-CF).
Ekran tutucu tırnaklar kalktı. Değişen baskılar: göğüs bandı, orta bant, omuz bandı (basamak), uzatma bantları (157,5), üst arka kapak, kafa kabukları (ekran yuvası), kafa iskeleti, boyun mili ve servo yuvası (kablo penceresi), boyun adaptörü (62,8). Aşağıdaki tablolarda satırı olmayan parçalar:

| Parça | Adet | Ölçü (mm) | Filament (g) | Süre (sa) | Yön | Destek |
|---|---|---|---|---|---|---|
| Ust arka servis kapagi | 1 | 168 × 150 × 3 | 80 | 1,70 | dis yuzu tablada | desteksiz |
| Etek servis kapagi H1 (sigorta kutusu) | 1 | 111 × 111 × 3 | 24 | 0,50 | duz (alt yuzu tablada) | desteksiz |
| Etek servis kapagi H2 (ana sigorta) | 1 | 70 × 56 × 3 | 14 | 0,30 | duz (alt yuzu tablada) | desteksiz |
| Gogus ekrani cercevesi sag | 1 | 207 × 147 × 10 | 29 | 0,60 | arka yuzu (flans) tablada | desteksiz |
| Gogus ekrani cercevesi sol | 1 | 207 × 147 × 10 | 29 | 0,60 | arka yuzu (flans) tablada | desteksiz |
| Gogus ekrani VESA tasiyici | 1 | 107 × 100 × 65 | 114 | 2,40 | VESA plakasi tablada; arka flans destekli | destekli |

Kabukta destek isteyen parçalar: Gogus bandi sag, Gogus bandi sol, Gogus ekrani VESA tasiyici.

## Özet

| Parti | Ne zaman | Adet | Filament | Baskı süresi |
|---|---|---|---|---|
| 1 | Hemen | 24 | 3,28–3,29 kg | ≈ 68–69 sa |
| 2 | Servo ve horn gelip ölçülünce | 25 | 1,33–1,38 kg | ≈ 28–29 sa |
| 3 | 10,1" QLED yüz ekranı gelip ölçülünce | 5 | 0,80 kg | ≈ 17 sa |
| 4 | Etek tasarım kararından sonra (M6 CAD) | 11 | 2,21 kg | ≈ 46 sa |
| **Toplam** | | **65** | **7,63–7,68 kg** | **≈ 159–160 sa** |

**Filament:** net **düz PETG 6,47 kg** (S1 kaseti dahil) + **PETG-CF 1,16–1,21 kg** (`Y2b-baski.json`; omuz doluluğu 0,8–0,9
ve destek dahil; 29.10: boyun yükseltme adaptörü 70 g PETG'den CF'ye geçti, toplam aynı). Tolerans kuponları ayrıca ≈ 0,1 kg PETG ve ≈ 0,2–0,3 kg PETG-CF. Başarısız baskı payıyla **9 makara beyaz PETG + 1,5 kg siyah PETG-CF (3 × 0,5 kg)** (v4 malzeme listesi; filamenti firma + ekip karşılar, satın alınmaz). Parça + kupon PETG-CF 1,36–1,51 kg: 1,5 kg'de pay neredeyse yok, doğrulanmadı.

## Renk (Ahmet, 11 Ekim 2026: "Tamamen beyaz")

| Renk | Parçalar |
|---|---|
| **Beyaz PETG** | Düz PETG'den basılan her şey: kabuk (gövde, uzatma ve göğüs bantları), etek ve dolgu şeritleri, kafa kabukları, kafa iskeleti, kafa ekranı tırnakları (10,1" QLED modeliyle gelecek), göğüs ekranı çerçevesi (gövde renginde, 04.11) ve VESA taşıyıcı, üst kol tüpü, ön kol, el, sonar tutucular, akü takozu, servis kapakları, S1 kaseti |
| **Siyah PETG-CF** | Yük taşıyan 11 tür (17 adet). Omuz ve dirsek eklemleri siyah görünür, kafa iç parçaları kabuğun içinde kalır |

## Malzeme

| Malzeme | Nereye | Neden |
|---|---|---|
| **PETG** (beyaz) | Yukarıdaki beyaz parçalar | Yükü az, büyük parçalar. PETG tok, kolay basılır (camsı geçiş ≈ 80 °C, tahmini). Etekteki ısı ölçülünce kontrol edilmeli (E7) |
| **PETG-CF** | Servo torkunu ya da rulman yükünü taşıyan 11 tür (aşağıda) | Düz PETG'den rijit, sıkı geçmede ve vida sıkıştırmasında daha az akma (tahmini) |

**PETG-CF ile basılacak parçalar (toplam PETG-CF ≈ 1,16–1,21 kg):**

| Modül | Parça | Adet | Taşıdığı yük |
|---|---|---|---|
| omuz | Omuz yuvası | 2 | Bütün kolun momenti; travers ucuna M6 ile bağlı |
| omuz | Rulman kapağı | 2 | 6808-2RS sıkı geçme (Ø52) |
| omuz | Omuz göbeği | 2 | S1 horn torku (DS3235) + rulman mili Ø40 |
| omuz | Kol çatalı | 2 | S2 horn torku (DS3235) + 625ZZ yuvası |
| dirsek | Dirsek çatalı | 2 | Dirsek horn torku; dış kol 8 mm, horn cıvatası M3×12 + 2 pul |
| dirsek | Bilek flanşı | 2 | Bilek horn bağlantısı |
| kafa | Servo yuvası | 1 | Kafanın tamamı bunun üstünde (kütle `kafa-analiz.json`; 10,1" QLED modelinde değişecek) |
| kafa | Rulman yuvası | 1 | 6808-2RS yuvası |
| kafa | Boyun mili | 1 | Pan horn torku |
| kafa | Eğme çatalı | 1 | Tilt horn torku (tilt sınırı ±13°, karar 29.10). Montajda tilt servosundan **önce** takılır (M6 C3) |
| kafa | Boyun yükseltme adaptörü | 1 | Pan torku ve kafa ağırlığı (boyun mili ile eğme çatalı arasında; karar 29.10) |

**Karar 29.10 (Ahmet):** Y2a'da eklenen **boyun yükseltme adaptörü** (boyun mili ile eğme çatalı arasında, pan torku ve kafa ağırlığı
yolunda) **PETG-CF** ile basılır; CAD'de (`kafa10_lib.py`) malzeme PETG-CF. Kütle aynı (ρ 1,27 tahmini, doluluk 0,8: 66,4 g; filament 70 g).

**Neden PA-CF değil:** Nem çeker, kurutma ister, pahalı. Bu yüklerde (el yükü ≈ 100 g sınırı, jestler) PETG-CF yeterli olmalı (tahmini).

**Yazıcı şartı:** Karbon katkılı filament sertleştirilmiş çelik nozul ister (X2D fabrikadan 0,4 mm sertleştirilmiş çelik). Okul
yazıcısında nozulun değiştirilmediğini kontrol edin.

**Ayar (PETG-CF):** duvar 5–6, üst/alt 5 katman, doluluk %50–60 gyroid, filament kuru. **Tolerans kuponları (Parti 0) asıl
malzemeyle basılmalı.**

**Destekli kafa kabuğu (karar 29.10):** yüz kabuğu (ön) sağ ve arka kafa kabuğu sağ, x = 0 dikiş dilinde (16 mm şerit, iç yarı duvar)
yüzü tablada baskıda ~1,25 mm yükseklikte konsol bırakıyor (çıkıntı 26,1 / 52,3 cm², `Y2a-kontrol.md`). Dilimleyicide yalnız bu
bölgelere destek ("support on build plate only" yeterli değilse boyalı destek); destek dil yüzünden temizlenmeli, dil 1,3 mm et.

**Süre:** ≈ 159–160 saat; yazıcı hiç durmazsa ≈ 6,7 gün. Okul yazıcısı paylaşımlıysa gerçekçi süre 4–5 hafta (tahmini). Parti 1 hemen başlamalı.

## Sıralama mantığı

1. **Parti 0, ilk gün tolerans kuponları** (`tasarim/freecad/test/`, aşağıda). Seçilen ölçü CAD'e girer, büyük parçalar sonra basılır.
2. **Parti 1:** ölçüsü elimizdeki parçaya pek bağlı olmayanlar: gövde, uzatma, göğüs ve omuz bantları, göğüs ekranı çerçevesi ve VESA taşıyıcı, arka ve üst arka servis kapakları, sonar tutucular,
   rulman kapağı, üst kol tüpü (S1 kontrolü Y1/Y1b'de geçti, artık beklemiyor).
3. **Parti 2:** horn delik dizilimi tahmini (25T disk, M3 delikler 8,5 mm yarıçapta) ve servo gövdeleri (DS3235, MG996R). Gelince
   kumpasla ölçülür, CAD güncellenir, sonra basılır.
4. **Parti 3:** kafa ekranı 10,1" QLED 1280×720 (WaveShare, kod 20789; 03.11 gece). Vida deliği yok, tırnakla tutulur; kütle doğrulanmadı. Model güncellenince ve ekran gelip ölçülünce kafa iskeleti ve kafa kabukları basılır. Aşağıdaki satırlar henüz 7" modelden.
5. **Parti 4:** etek ana anahtar deliği (M6 K7) ve H1, H2 servis kapakları (M6 K5, K6) Y3'te CAD'e girdi; etek ısı/havalandırma kararı bekliyor (E7). Akü **yerinde** (karar 29.10); takoz akü gelince teyit edilip basılır.

## Tolerans (CAD'de)

| Geçme | CAD değeri | Not |
|---|---|---|
| Vida geçiş delikleri | M3 Ø3,4 · M4 Ø4,5 · M5 Ø5,5 · M6 Ø6,6 (ISO 273 orta) | `arayuz.CLEAR` |
| Servo cepleri | Her yanda +0,2 mm | |
| Omuz yuvası ↔ sigma travers | Her yanda +0,2 mm | |
| Üst kol tüpü ↔ çatal ve dirsek pimi (Ø50,8) | Tüp içi Ø51,3, her yanda 0,25 mm | `arayuz.GECME["tup_pim"]` |
| Isıl gömme somun deliği | M3 Ø4,0 (ruthex M3×5,7), M5 Ø6,4 (tahmini) | `arayuz.INSERT_DELIK`; kuponla doğrulanacak |
| Kabuk bindirmesi | 0,25 mm boşluk | `arayuz.KABUK_BINDIRME_BOSLUK` |
| Rulman yuvaları (6808 Ø52, 625ZZ Ø16), Ø40 mil | Tam ölçü (sıkı geçme) | **Kupondan sonra** seçilen ölçü uygulanacak |
| Horn delik dizilimi | Tahmini | Horn gelince kumpasla |

### Tolerans kuponları (Parti 0)

M7 kuponları (`tasarim/freecad/test/README.md`): C ısıl gömme L + 1 (PETG **ve** PETG-CF), D1 / D2 dirsek kelepçesi (**PETG-CF**),
E tüp halkası (PETG). Toplam ≈ 104 g (tahmini doluluk) / 205 g (%100), ~3 sa.

| Dosya | Malzeme | Ne denenir | Ölçü | Kütle |
|---|---|---|---|---|
| `test/stl/kupon-a-rulman-O52.stl` | PETG-CF | 6808-2RS dış bileziği: 4 halka Ø52,0 / 52,1 / 52,2 / 52,3 | 124 × 124 × 7 | ≈ 26 g |
| `test/stl/kupon-b-yuva-mil-somun.stl` | PETG-CF **ve** beyaz PETG | 625ZZ yuvası Ø16,0…16,3 · Ø40 boru mil Ø39,8…40,1 · M3 somun deliği Ø3,8…4,1 · M5 Ø6,2 / 6,4 / 6,6 | 200 × 95 × 11 | ≈ 60–88 g |

Rulman elle (ya da mengeneyle hafif) bastırınca oturmalı; ısıl gömme somun havyayla düz girmeli, vida sıkınca dönmemeli. Sonucu Echo'ya
söyleyin, CAD'e uygulanır ve STL'ler yeniden çıkarılır.

## STL durumu

Omuz STL'leri (`tasarim/freecad/omuz/stl/`, 1650 omuzdan; 158 cm'de omuz geometrisi değişmedi) ve kuponlar (`tasarim/freecad/test/stl/`) var. Diğer modüllerin baskı
parçaları kupon sonucundan sonra FreeCAD'den toplu dışa aktarılmalı (açık iş; Y4'te modüller yeniden üretilirken).

Tablolarda ölçü analizdeki baskı yönündeki kutu (mm), filament ve süre adet başına; omuz satırlarında aralık doluluk 0,8–0,9.

## Parti 1 — hemen basılabilir

Özet'e göre 24 adet · 3,28–3,29 kg filament · ≈ 68–69 saat (tabloda 20 satır; üst arka kapak, 2 çerçeve ve VESA taşıyıcı yukarıdaki 158 cm tablosunda). 1,65 m'deki satır: 20 adet · 3,44–3,45 kg · ≈ 72 saat.

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü |
|---|---|---|---|---|---|---|---|
| ☐ | taban | Sonar tutucu sol | 1 | 61 × 61 × 8 | 5 | 0,11 | arka yüzü (ray tarafı) tablada |
| ☐ | taban | Sonar tutucu orta | 1 | 66 × 66 × 8 | 6 | 0,12 | arka yüzü (ray tarafı) tablada |
| ☐ | taban | Sonar tutucu sağ | 1 | 61 × 61 × 8 | 5 | 0,11 | arka yüzü (ray tarafı) tablada |
| ☐ | kabuk | Gövde alt bandı sağ | 1 | 170 × 137 × 226 | 299 | 6,20 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde alt bandı sol | 1 | 170 × 125 × 226 | 280 | 5,80 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde uzatma bandı 1 sağ | 1 | 170 × 137 × 170 | 224 | 4,70 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde uzatma bandı 1 sol | 1 | 170 × 125 × 170 | 211 | 4,40 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde uzatma bandı 2 sağ | 1 | 170 × 137 × 170 | 224 | 4,70 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde uzatma bandı 2 sol | 1 | 170 × 125 × 170 | 211 | 4,40 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde orta bandı sağ | 1 | 214 × 162 × 227 | 272 | 5,70 | dik (alt kenarı tablada) |
| ☐ | kabuk | Gövde orta bandı sol | 1 | 214 × 150 × 227 | 262 | 5,40 | dik (alt kenarı tablada) |
| ☐ | kabuk | Göğüs bandı sağ (gömülü 11,6" cep) | 1 | 217 × 164 × 235 | 219 | 4,60 | dik (alt kenarı tablada), **destekli: cep üst kenarı (köprü ~150 mm)** |
| ☐ | kabuk | Göğüs bandı sol (gömülü 11,6" cep) | 1 | 217 × 152 × 235 | 215 | 4,50 | dik (alt kenarı tablada), **destekli: cep üst kenarı (köprü ~150 mm)** |
| ☐ | kabuk | Omuz bandı sağ | 1 | 164 × 156 × 102 | 184 | 3,80 | ters (üst kapak tablada) |
| ☐ | kabuk | Omuz bandı sol | 1 | 156 × 152 × 102 | 178 | 3,70 | ters (üst kapak tablada) |
| ☐ | kabuk | Arka servis kapağı | 1 | 190 × 160 × 3 | 98 | 2,00 | dış yüzü tablada |
| ☐ | omuz | Rulman kapağı **(PETG-CF)** | 2 | 76 × 60 × 14 | 15–17 | 0,32–0,36 | +X: x = 146 yüzü tablada, Ø52 yuva yukarı (desteksiz) |
| ☐ | omuz | Üst kol tüpü | 2 | 130 × 56 × 56 | 54 | 1,13 | +Y: uç tablada, brim (desteksiz) |

## Parti 2 — servo ve horn gelip ölçülünce

Özet'e göre 25 adet · 1,33–1,38 kg filament · ≈ 28–29 saat (omuz doluluk 0,8–0,9).

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü |
|---|---|---|---|---|---|---|---|---|
| ☐ | omuz | Omuz yuvası **(PETG-CF)** | 2 | 76 × 76 × 67 | 81–90 | 1,70–1,88 | −Y: y = 25 üst yüzü tablada, **destekli** (manşon içi + S1 penceresi) | DS3235 gövdesi, çekiç somun |
| ☐ | omuz | Omuz göbeği **(PETG-CF)** | 2 | 66 × 51 × 49 | 61–68 | 1,27–1,41 | +X: Ø40 mil ucu tablada, **destekli** (flanş altı) | **horn delik dizilimi** |
| ☐ | omuz | S1 kablo tamburu | 2 | 87 × 71 × 10 | 6 | 0,12 | +X: −x dudak tablada, **destekli** (+x dudak altı) | göbekle birlikte |
| ☐ | omuz | Kol çatalı **(PETG-CF)** | 2 | 76 × 64 × 56 | 99–110 | 2,07–2,30 | −Z: horn kulağı tablada, **destekli** | **horn delik dizilimi** |
| ☐ | kabuk | S1 kaset gövdesi sağ / sol | 2 | 112 × 111 × 6 | 10 | 0,20 | arka yüzü (x 152) tablada | kablo kalınlığı (≤ 1,4 mm, K1) |
| ☐ | kabuk | S1 kaset kapağı sağ / sol | 2 | 112 × 111 × 4 | 7 | 0,10 | flanş dış yüzü tablada | — |
| ☐ | dirsek | Dirsek çatalı **(PETG-CF)** | 2 | 74 × 72 × 74 | 97 | 2,03 | ters: pim ve bilezik ucu tablada, kollar yukarı | **horn delik dizilimi** |
| ☐ | dirsek | Ön kol gövdesi | 2 | 130 × 129 × 34 | 56 | 1,17 | ön yüzü tablada, açık arka yukarı | MG996R gövdesi |
| ☐ | dirsek | Bilek flanşı **(PETG-CF)** | 2 | 28 × 28 × 8 | 4 | 0,09 | horn yüzü tablada, havşalar yukarı | **horn delik dizilimi** |
| ☐ | dirsek | El | 2 | 56 × 56 × 85 | 78 | 1,64 | ters: parmak ucu ve avuç altı tablada, yaka yukarı (45° koni) | — |
| ☐ | kafa | Servo yuvası **(PETG-CF)** | 1 | 88 × 88 × 43 | 152 | 3,16 | dik: kulak flanşı tablada | MG996R gövdesi |
| ☐ | kafa | Rulman yuvası **(PETG-CF)** | 1 | 68 × 60 × 36 | 27 | 0,56 | dik: kulaklar tablada, rulman yuvası yukarı | 6808-2RS |
| ☐ | kafa | Boyun mili **(PETG-CF)** | 1 | 60 × 60 × 48 | 41 | 0,85 | dik: horn diski tablada, flanş yukarı (45° koni) | **horn delik dizilimi** |
| ☐ | kafa | Eğme çatalı **(PETG-CF)** | 1 | 74 × 60 × 49 | 36 | 0,75 | dik: taban tablada, duvarlar yukarı | **horn delik dizilimi** |
| ☐ | kafa | Boyun yükseltme adaptörü **(PETG-CF)** | 1 | 60 × 60 × 63 | 74 | 1,54 | dik: alt flanş tablada (45° koni) | — (PETG-CF, karar 29.10) |

## Parti 3 — 10,1" QLED yüz ekranı gelip ölçülünce

Özet'e göre 5 adet · 0,80 kg filament · ≈ 17 saat (7" modelden; ekran tırnakları kalktı). 1,65 m'deki satır: 9 adet · 0,76 kg · ≈ 16 saat.

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü |
|---|---|---|---|---|---|---|---|---|
| ☐ | kafa | Kafa iskeleti | 1 | 224 × 115 × 48 | 128 | 2,66 | ters: tabla tablada, yanaklar yukarı | 7" ekran kulak delikleri (04) + kamera delikleri |
| ☐ | kafa | Yüz kabuğu (ön) sağ | 1 | 215 × 151 × 37 | 119 | 2,49 | ön yüzü tablada, **destekli: dikiş dili (16 mm şerit, ~1,25 mm konsol), karar 29.10** | 7" ekran ölçüsü |
| ☐ | kafa | Yüz kabuğu (ön) sol | 1 | 215 × 135 × 37 | 110 | 2,29 | ön yüzü tablada | 7" ekran ölçüsü |
| ☐ | kafa | Arka kafa kabuğu sağ | 1 | 215 × 151 × 107 | 229 | 4,77 | arka yüzü tablada, **destekli: dikiş dili (16 mm şerit, ~1,25 mm konsol), karar 29.10** | 7" ekran ölçüsü |
| ☐ | kafa | Arka kafa kabuğu sol | 1 | 215 × 135 × 107 | 215 | 4,49 | arka yüzü tablada | 7" ekran ölçüsü |

## Parti 4 — tasarım kararından sonra (etek, akü)

Özet'e göre 11 adet · 2,21 kg filament · ≈ 46 saat (tabloda 9 satır; H1 ve H2 kapakları yukarıdaki 158 cm tablosunda). 1,65 m'deki satır: 9 adet · 2,19 kg · ≈ 46 saat.

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü |
|---|---|---|---|---|---|---|---|---|
| ☐ | taban | Akü ön takozu | 1 | 125 × 125 × 25 | 72 | 1,50 | alt yüzü tablada | Victron ölçüsü (akü yerinde, karar 29.10); akü gelince teyit |
| ☐ | kabuk | Etek arka sağ | 1 | 234 × 190 × 227 | 366 | 7,60 | ters (üst plakası tablada) | **ana anahtar (M6 K7) + XT60 + sigorta kapağı (M6 K5), havalandırma (E7)** |
| ☐ | kabuk | Etek arka sol | 1 | 222 × 175 × 227 | 362 | 7,50 | ters (üst plakası tablada) | **ana anahtar (M6 K7) + XT60 + sigorta kapağı (M6 K5), havalandırma (E7)** |
| ☐ | kabuk | Etek orta sağ | 1 | 222 × 199 × 227 | 217 | 4,50 | ters (üst plakası tablada) | havalandırma kararı |
| ☐ | kabuk | Etek orta sol | 1 | 222 × 199 × 227 | 217 | 4,50 | ters (üst plakası tablada) | havalandırma kararı |
| ☐ | kabuk | Etek ön sağ | 1 | 234 × 190 × 227 | 372 | 7,70 | ters (üst plakası tablada) | havalandırma kararı |
| ☐ | kabuk | Etek ön sol | 1 | 222 × 175 × 227 | 363 | 7,60 | ters (üst plakası tablada) | havalandırma kararı |
| ☐ | kabuk | Etek dolgu şeridi arka (520 taban) | 1 | 192 × 88 × 227 | 98 | 2,00 | ters (üst plakası tablada) | — |
| ☐ | kabuk | Etek dolgu şeridi ön (520 taban) | 1 | 192 × 88 × 227 | 107 | 2,20 | ters (üst plakası tablada) | — |
