# Baskı listesi (FreeCAD V3, 11 Ekim 2026)

Kaynak: modül analizleri `tasarim/freecad/<modül>/<modül>-analiz.json` (`baski` alanı). Filament ve süre
analizdeki dilimleme tahmininden gelir (%80 doluluk, PETG). Omuz analizinde süre yok; süresi diğer
parçaların ortalaması 48 g/saat ile **tahmini** hesaplandı. Yazıcı: Bambu Lab X2D (kullanılabilir hacim
246 × 246 × 250 mm). 44 parçanın hepsi tablaya sığıyor ve hepsi desteksiz basılıyor (analizlerin
`sigar` ve `desteksiz` alanları).

## Özet

| Parti | Ne zaman | Adet | Filament | Baskı süresi |
|---|---|---|---|---|
| 1 | Hemen | 14 | 1,69 kg | ≈ 35 sa |
| 2 | Servo ve horn gelip ölçülünce | 18 | 0,99 kg | ≈ 21 sa |
| 3 | Ekranlar gelip ölçülünce | 5 | 1,12 kg | ≈ 23 sa |
| 4 | Etek tasarım kararından sonra | 7 | 1,94 kg | ≈ 40 sa |
| **Toplam** | | **44** | **5,73 kg** | **≈ 120 sa** |

**Filament:** Net ihtiyaç 5,73 kg. Bunun 0,79 kg'ı PETG-CF, 4,94 kg'ı düz PETG (bkz. Malzeme).
Başarısız baskı ve yeniden basım payıyla **6 makara beyaz PETG + 1 kg siyah PETG-CF** öneriyorum (tahmini
pay %20–25). `maliyet.json`'da (11 Ekim 2026): 6 × Microzey HS PETG beyaz (389 TL) + 2 × 0,5 kg Polymaker PETG-rCF08 siyah
(1.105,87 TL; stok belirsiz, siparişten önce sorulmalı). Kanıt `raporlar/kaynaklar/05-fiyat-arastirmasi.md` bölüm 5.

## Renk (Duffy, 11 Ekim 2026: "Tamamen beyaz")

| Renk | Parçalar |
|---|---|
| **Beyaz PETG** | Düz PETG'den basılan her şey: kabuk, etek, kafa kabukları, üst kol tüpü, ön kol, el, sonar tutucular, akü takozu, servis kapağı |
| **Siyah PETG-CF** | Yük taşıyan 10 parça. PETG-CF neredeyse yalnız siyah satılıyor. Omuz ve dirsek eklemleri siyah görünür, kafa iç parçaları kabuğun içinde kalır. |
| Siyah akrilik | Yüz vizörü (lazer kesim, değişmedi) |

Not: Etek yere en yakın parça. Beyazda sürtünme izi ve kir belli olur, sökmeden silinebilir olması işe yarar.

## Malzeme

İki malzeme kullanıyoruz. Daha fazlası yazıcıda makara değiştirme, ayar ve hata riskini artırır,
kazancı azdır.

| Malzeme | Nereye | Neden |
|---|---|---|
| **PETG** (beyaz) | Kabuk, etek, kafa kabukları, sonar tutucular, akü takozu, üst kol tüpü, ön kol, el, arka servis kapağı | Yükü az, büyük parçalar. PETG tok, kolay basılır, iç mekânda yeterli ısı dayanımı var (camsı geçiş ≈ 80 °C, tahmini). Etekteki sürücü ve düşürücülerin ısısı ölçülünce kontrol edilmeli. |
| **PETG-CF** (karbon katkılı PETG) | Servo torkunu ya da rulman yükünü taşıyan 10 parça (aşağıda) | Düz PETG'den daha rijit. Vida sıkıştırmasında ve rulmanın sıkı geçtiği yuvada zamanla akma (sünme) daha az, yani boşluk yapmıyor (tahmini). Düz PETG gibi basılır, ayarı benzer. |

**PETG-CF ile basılacak parçalar (≈ 0,79 kg):**

| Modül | Parça | Adet | Taşıdığı yük |
|---|---|---|---|
| omuz | Omuz yuvası | 2 | Bütün kolun momenti; travers ucuna M6 ile bağlı |
| omuz | Rulman kapağı | 2 | 6808-2RS sıkı geçme (Ø52) |
| omuz | Omuz göbeği | 2 | S1 horn torku + rulman mili Ø40 |
| omuz | Kol çatalı | 2 | S2 horn torku + 625ZZ yuvası |
| dirsek | Dirsek çatalı | 2 | Dirsek horn torku |
| dirsek | Bilek flanşı | 2 | Bilek horn bağlantısı (küçük, ama tork doğrudan horn'dan geçiyor) |
| kafa | Servo yuvası | 1 | Kafanın tamamı (1,37 kg) bunun üstünde |
| kafa | Rulman yuvası | 1 | 6808-2RS yuvası |
| kafa | Boyun mili | 1 | Pan horn torku |
| kafa | Eğme çatalı | 1 | Tilt horn torku. Tilt payı 2,1× ile servoların en düşüğü |

**Neden PA-CF (naylon karbon) değil:** Daha güçlü ama nem çekiyor, her baskıdan önce kurutma ister,
fiyatı daha yüksek. Bu yüklerde (el ucunda ≈ 50 g, jest hareketleri) PETG-CF yeterli olmalı (tahmini).
Bir parça kırılırsa ya da boşluk yaparsa önce baskı ayarı güçlendirilir, sonra o parça PA-CF ile basılır.

**Yazıcı şartı:** Karbon katkılı filament pirinç nozulu aşındırır, sertleştirilmiş çelik nozul gerekir.
X2D fabrikadan 0,4 mm sertleştirilmiş çelik nozulla geliyor (Tom's Hardware incelemesi). Okuldaki yazıcıda
nozulun değiştirilmediğini kontrol edin.

**Ayar (PETG-CF parçaları):** Dayanımı malzemeden çok baskı ayarı belirler.
- Duvar (perimeter) 5–6, üst ve alt katman 5. Isıl gömme somun ve horn vidası etrafındaki et duvardan oluşur.
- Doluluk %50–60 gyroid. Duvar sayısı yüksekken doluluğu %100'e çıkarmak ağırlık katar, dayanımı az artırır (tahmini).
- Filament kuru olmalı. Makara açık bekleyecekse kurutucuda ya da nem alıcıyla saklayın.
- **Tolerans kuponları (Parti 0) asıl malzemeyle basılmalı.** Sıkı geçme toleransı malzemeye göre değişir. Düz
  PETG'de tutan ölçü PETG-CF'de tutmayabilir.

**Ağırlık:** PETG-CF yoğunluğu düz PETG'ye yakın (tahmini ≈ 1,25–1,3 g/cm³). CAD'deki kütle ve ağırlık
merkezi pratikte değişmez.

**Süre:** 120 saat, yazıcı hiç durmazsa 5 gün eder. Okul yazıcısı paylaşımlıysa ve gece baskısı
yapılamıyorsa gerçekçi süre 3–4 hafta (tahmini). Bu yüzden Parti 1 hemen başlamalı.

## Sıralama mantığı

1. **Parti 0, ilk gün tolerans kuponları** (`tasarim/freecad/test/`, aşağıda). Rulman, mil ve ısıl gömme somun
   delikleri burada denenir. Seçilen ölçü CAD'e girer, büyük parçalar ondan sonra basılır. Bütün kabuk ısıl
   gömme somunla tutturulduğu için 23 saatlik gövde bantlarından önce bu test şart.
2. **Parti 1:** Ölçüsü elimizdeki parçaya pek bağlı olmayan parçalar. Gövde bantları uzun sürüyor, yazıcı
   bu sırada boş kalmaz.
3. **Parti 2:** Horn delik dizilimi tahmini (25T disk, M3 delikler 8,5 mm yarıçapta). Horn'lar gelince
   kumpasla ölçülür, CAD güncellenir, sonra basılır. Bu parçalar küçük, baskısı hızlı.
4. **Parti 3:** Ekran açıklıkları ölçüye bağlı. Not: CAD'de göğüs ekranı **Nextion NX1060P101**,
   `maliyet.json`'da ise **Waveshare 10,1" HDMI**. Hangisinin alınacağı kesinleşmeden göğüs bandı basılmamalı.
5. **Parti 4:** Etek üst plakasına ana anahtar deliği ve XT60 şarj girişi henüz çizilmedi. Etekteki ısı
   ve havalandırma kararı da bekliyor. Akü ön takozu ise akü seçimine bağlı.

## Tolerans (CAD'de, 11 Ekim 2026)

| Geçme | CAD değeri | Not |
|---|---|---|
| Vida geçiş delikleri | M3 Ø3,4 · M4 Ø4,5 · M5 Ø5,5 · M6 Ø6,6 (ISO 273 orta) | `arayuz.CLEAR` |
| Servo cepleri | Her yanda +0,2 mm | Değişmedi |
| Omuz yuvası ↔ sigma travers | Her yanda +0,2 mm | Değişmedi |
| Üst kol tüpü ↔ çatal ve dirsek pimi (Ø50,8) | Tüp içi Ø51,3, **her yanda 0,25 mm** (önce 0,1) | `arayuz.GECME["tup_pim"]`; dirsekteki tüp oturma oluğu da buna göre |
| Isıl gömme somun deliği | **M3 Ø4,0** (ruthex M3×5,7 tablosu), **M5 Ø6,4** (tahmini). Önce somun dış çapıyla aynıydı (Ø4,6 / Ø7,0), somun tutunmazdı. | `arayuz.INSERT_DELIK`; kuponla doğrulanacak, başka marka alınırsa onun tablosu |
| Kabuk bindirmesi (dil ↔ komşunun dış yarısı) | **0,2 mm boşluk** (dil 1,5 → 1,3 mm). Vida yerlerindeki Ø8 boss'lar yüzeye değer, vida dudağı oraya sıkar. | `arayuz.KABUK_BINDIRME_BOSLUK` |
| Rulman yuvaları (6808 Ø52, 625ZZ Ø16), rulmandan geçen Ø40 mil | Tam ölçü (sıkı geçme) | **Kupondan sonra** seçilen ölçü uygulanacak |
| Horn delik dizilimi | Tahmini | Horn gelince kumpasla |

### Tolerans kuponları (Parti 0)

| Dosya | Malzeme | Ne denenir | Ölçü | Kütle |
|---|---|---|---|---|
| `test/stl/kupon-a-rulman-O52.stl` | PETG-CF | 6808-2RS dış bileziği: 4 halka Ø52,0 / 52,1 / 52,2 / 52,3 | 124 × 124 × 7 | ≈ 26 g |
| `test/stl/kupon-b-yuva-mil-somun.stl` | PETG-CF **ve** beyaz PETG (iki kez) | 625ZZ yuvası Ø16,0…16,3 · 6808 iç bileziği için boru mil Ø39,8…40,1 · M3 somun deliği Ø3,8…4,1 · M5 somun deliği Ø6,2 / 6,4 / 6,6 | 200 × 95 × 11 | ≈ 60–88 g |

Her ölçünün yanındaki nokta sayısı sırasını gösterir, 1 nokta en küçük ölçü. Rulman elle (ya da mengene ile hafif)
bastırınca oturmalı, eğilmeden düz girmeli. Isıl gömme somun havyayla düz girmeli, soğuyunca vidayı sıkınca
dönmemeli. Kabuk düz PETG olduğundan M3 deliği PETG kuponundan seçilir. Sonucu Echo'ya söyleyin, CAD'e
uygulanır ve STL'ler yeniden çıkarılır.

## STL durumu

Omuz modülünün STL'leri (`tasarim/freecad/omuz/stl/`, tolerans düzeltmesiyle yeniden üretildi) ve tolerans
kuponları (`tasarim/freecad/test/stl/`) var. Diğer modüllerin baskı parçaları kupon sonucundan sonra FreeCAD'den
toplu olarak dışa aktarılmalı (açık iş).

## Parti 1 — hemen basılabilir (ölçüye az bağlı)

14 adet · 1.69 kg filament · ≈ 35 saat baskı

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü | STL |
|---|---|---|---|---|---|---|---|---|---|
| ☐ | taban | Sonar tutucu sol | 1 | 61 × 61 × 8 | 5 | 0.1 | arka yuzu (ray tarafi) tablada | HC-SR04 standart ölçü | yok |
| ☐ | taban | Sonar tutucu orta | 1 | 66 × 66 × 8 | 6 | 0.1 | arka yuzu (ray tarafi) tablada | HC-SR04 standart ölçü | yok |
| ☐ | taban | Sonar tutucu sag | 1 | 61 × 61 × 8 | 5 | 0.1 | arka yuzu (ray tarafi) tablada | HC-SR04 standart ölçü | yok |
| ☐ | omuz | Rulman kapagi **(PETG-CF)** | 2 | 76 × 60 × 14 | 12 | 0.2 (tahmini) | — | 6808-2RS Ø52 sıkı geçme (kupon A sonucu) | `omuz/stl/rulman-kapagi.stl` |
| ☐ | omuz | Ust kol tupu | 2 | 100 × 56 × 56 | 32 | 0.7 (tahmini) | — | — | `omuz/stl/ust-kol-tupu.stl` |
| ☐ | kabuk | Govde alt bandi sag | 1 | 170 × 137 × 226 | 300 | 6.2 | dik (alt kenari tablada) | ısıl gömme somun ölçüsü | yok |
| ☐ | kabuk | Govde alt bandi sol | 1 | 170 × 125 × 226 | 281 | 5.8 | dik (alt kenari tablada) | ısıl gömme somun ölçüsü | yok |
| ☐ | kabuk | Govde orta bandi sag | 1 | 183 × 150 × 227 | 262 | 5.5 | dik (alt kenari tablada) | ısıl gömme somun ölçüsü | yok |
| ☐ | kabuk | Govde orta bandi sol | 1 | 183 × 138 × 227 | 252 | 5.3 | dik (alt kenari tablada) | ısıl gömme somun ölçüsü | yok |
| ☐ | kabuk | Omuz bandi sag | 1 | 164 × 162 × 102 | 202 | 4.2 | ters (ust kapak tablada) | ısıl gömme somun ölçüsü | yok |
| ☐ | kabuk | Omuz bandi sol | 1 | 162 × 152 × 102 | 194 | 4.0 | ters (ust kapak tablada) | ısıl gömme somun ölçüsü | yok |
| ☐ | kabuk | Arka servis kapagi | 1 | 190 × 160 × 3 | 98 | 2.0 | dis yuzu tablada | — | yok |

## Parti 2 — servo ve horn gelip ölçülünce

18 adet · 0.99 kg filament · ≈ 21 saat baskı

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü | STL |
|---|---|---|---|---|---|---|---|---|---|
| ☐ | omuz | Omuz yuvasi **(PETG-CF)** | 2 | 76 × 76 × 67 | 52 | 1.1 (tahmini) | — | DS3218MG gövdesi, çekiç somun | `omuz/stl/omuz-yuvasi.stl` |
| ☐ | omuz | Omuz gobegi **(PETG-CF)** | 2 | 66 × 51 × 49 | 42 | 0.9 (tahmini) | — | **horn delik dizilimi** | `omuz/stl/omuz-gobegi.stl` |
| ☐ | omuz | Kol catali **(PETG-CF)** | 2 | 76 × 64 × 56 | 66 | 1.4 (tahmini) | — | **horn delik dizilimi** | `omuz/stl/kol-catali.stl` |
| ☐ | dirsek | Dirsek catali **(PETG-CF)** | 2 | 72 × 71 × 74 | 94 | 2.0 | ters: pim ve bilezik ucu tablada, kollar yukari | **horn delik dizilimi** | yok |
| ☐ | dirsek | On kol govdesi | 2 | 101 × 63 × 28 | 44 | 0.9 | on yuzu tablada, acik arka yukari | MG996R gövdesi | yok |
| ☐ | dirsek | Bilek flansi **(PETG-CF)** | 2 | 28 × 28 × 8 | 4 | 0.1 | horn yuzu tablada, havsalar yukari | **horn delik dizilimi** | yok |
| ☐ | dirsek | El | 2 | 56 × 56 × 66 | 64 | 1.3 | ters: parmak ucu ve avuc alti tablada, yaka yukari | — | yok |
| ☐ | kafa | Servo yuvasi **(PETG-CF)** | 1 | 88 × 88 × 43 | 152 | 3.2 | dik: kulak flansi tablada | MG996R gövdesi | yok |
| ☐ | kafa | Rulman yuvasi **(PETG-CF)** | 1 | 68 × 60 × 36 | 27 | 0.6 | dik: kulaklar tablada, rulman yuvasi yukari | 6808-2RS | yok |
| ☐ | kafa | Boyun mili **(PETG-CF)** | 1 | 60 × 60 × 48 | 41 | 0.8 | dik: horn diski tablada, flans yukari (45 derece koni) | **horn delik dizilimi** | yok |
| ☐ | kafa | Egme catali **(PETG-CF)** | 1 | 74 × 60 × 49 | 36 | 0.7 | dik: taban tablada, duvarlar yukari | **horn delik dizilimi** | yok |

## Parti 3 — ekranlar gelip ölçülünce

5 adet · 1.12 kg filament · ≈ 23 saat baskı

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü | STL |
|---|---|---|---|---|---|---|---|---|---|
| ☐ | kafa | Kafa iskeleti | 1 | 205 × 116 × 69 | 116 | 2.4 | ters: kafa tablasi tablada, yanaklar yukari | **7" LCD + kamera delikleri** | yok |
| ☐ | kafa | Yuz kabugu (on) | 1 | 210 × 180 × 55 | 179 | 3.7 | yuz asagi: on yuz tablada, dikis yukari | **7" LCD ölçüsü** | yok |
| ☐ | kafa | Arka kafa kabugu | 1 | 210 × 180 × 101 | 284 | 5.9 | arka yuz tablada, dikis dili yukari | 7" LCD ölçüsü | yok |
| ☐ | kabuk | Gogus bandi sag | 1 | 209 × 163 × 205 | 275 | 5.7 | dik (alt kenari tablada) | **10,1" ekran ölçüsü** | yok |
| ☐ | kabuk | Gogus bandi sol | 1 | 209 × 151 × 205 | 265 | 5.5 | dik (alt kenari tablada) | **10,1" ekran ölçüsü** | yok |

## Parti 4 — tasarım kararından sonra (etek, akü)

7 adet · 1.94 kg filament · ≈ 40 saat baskı

| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Tabla yönü | Bağlı olduğu ölçü | STL |
|---|---|---|---|---|---|---|---|---|---|
| ☐ | taban | Aku on takozu | 1 | 125 × 125 × 25 | 72 | 1.5 | alt yuzu tablada | **akü seçimi (ölçü)** | yok |
| ☐ | kabuk | Etek arka sag | 1 | 234 × 190 × 227 | 372 | 7.8 | ters (ust plakasi tablada) | **ana anahtar + XT60 deliği, havalandırma kararı** | yok |
| ☐ | kabuk | Etek arka sol | 1 | 222 × 175 × 227 | 364 | 7.6 | ters (ust plakasi tablada) | **ana anahtar + XT60 deliği, havalandırma kararı** | yok |
| ☐ | kabuk | Etek orta sag | 1 | 222 × 199 × 227 | 197 | 4.1 | ters (ust plakasi tablada) | havalandırma kararı | yok |
| ☐ | kabuk | Etek orta sol | 1 | 222 × 199 × 227 | 197 | 4.1 | ters (ust plakasi tablada) | havalandırma kararı | yok |
| ☐ | kabuk | Etek on sag | 1 | 234 × 190 × 227 | 371 | 7.7 | ters (ust plakasi tablada) | havalandırma kararı | yok |
| ☐ | kabuk | Etek on sol | 1 | 222 × 175 × 227 | 362 | 7.5 | ters (ust plakasi tablada) | havalandırma kararı | yok |
