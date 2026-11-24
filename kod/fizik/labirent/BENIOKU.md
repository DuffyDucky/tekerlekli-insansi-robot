# Labirent dünyası (keşif deneyi)

Deney: robot karmaşık bir labirentin **START** açıklığından, labirent hakkında hiçbir ön bilgi olmadan başlar. LiDAR'la
haritalayarak **FINISH** açıklığını bulur. Tek başarı, FINISH'ten dışarı çıkmaktır. START'tan geri çıkmak ya da 15 dakikayı
(simülasyon zamanı) aşmak başarısızlıktır, yeni deneme yine START'tan başlar. Bu klasör yalnız **dünyayı** kurar: üretici,
sahneler, hakem ve puan. Robotun beyni (SLAM, keşif) `kod/fizik/kesif/` altında, sürücü ve başsız düzenek
`kod/fizik/gezinme/` altında.

| Dosya | İş |
| --- | --- |
| `uretici.py` | Labirent üretimi (tohumlu, mükemmel), 2B + 3B sahne JSON'u, görseller, fizibilite, doğrulama. Tek kaynak budur, JSON'lar elle düzeltilmez |
| `hakem.py` | `Hakem`: kurallar. Yalnız yer gerçeğine bakar, robota bilgi sızdırmaz |
| `puan.py` | Puan formülünün tek yeri (ödül–ceza) |
| `testler/test_labirent.py` | Üretici, hakem ve puan birim testleri (19 test, mujoco gerekmez) |
| `gorsel/labirent_*.png` | Üstten görünüm: duvarlar siyah, START yeşil, FINISH kırmızı, çözüm yolu mavi, çıkmazlar gri x |

## Robot ölçüleri ve geçit genişliği

Ölçüler `model/lale.xml` çarpışma geom'larından alındı (ev pozu). `kod/fizik/gezinme/BENIOKU.md` "Robot ölçüleri"
bölümüyle aynıdır.

| Ölçü | Değer |
| --- | --- |
| Ayak izi (çarpışma kutusu `c_govde`) | x ±0,264, y ±0,262 m, yani 0,528 × 0,523 m (etek 0,525 × 0,520) |
| Yerinde dönüşte süpürme | Arka dingil (gövde merkezinin 0,185 m gerisi, ön omnili öneride dönme merkezi) çevresinde **r = 0,520 m, çap 1,040 m**. En uzak nokta ön köşe: √(0,449² + 0,262²). Gövde merkezi çevresinde olsaydı çap 0,744 m olurdu |
| En yüksek ileri hız | 0,39 m/s (teker azamisi, TAHMİN). Gezinmenin seyir hızı 0,25 m/s |
| LiDAR | x +0,190, z **0,295 m** (`lidar_ozellik.json`) |

**Hücre (geçit) genişliği: 1,30 m.** Bu değer duvar ekseninden duvar eksenine ölçülür, duvarlar arası serbest genişlik 1,298 m'dir.
- **Yerinde dönüş her hücrede sığar.** Arka dingil hücre merkezinde olunca süpürme dairesi her duvardan **0,129 m** uzak kalır (geometrik kontrolle ölçüldü). Araştırma notunun koşulu (açıklık ≥ r + 0,05 m) bu durumda 0,079 m pay bırakarak sağlanır. Bu pay konum hatasını ve dönüşte dönme merkezinin kaymasını karşılar; makaralı omnide ölçülen dönme merkezi x −0,182, süpürme çapı 1,046 m.
- **Düz giderken** her yanda 0,387 m pay kalır.
- **1,20 m'de** dönüş payı 0,079 m'ye düşerdi; konum hatası ve dönüş kayması için yetersiz. **1,50 m** ise yolları %15 uzatır ve 15 dakikalık sınırı daha da zorlar (aşağıdaki fizibiliteye bakın). 1,30 m bu ikisinin arasında bilinçli bir uzlaşmadır.

**Duvarlar** koridor sahneleriyle aynıdır: 2B'de kalınlıksız çizgi, 3B'de `dunya.sahne_xml` iç duvar levhası. Kalınlık 2 mm
(`ic_duvar_kalinligi_m`), yükseklik 1,0 m (`duvar_yuksekligi_m`). LiDAR düzlemi (z 0,295) duvarı keser. Aynı doğrultudaki
bitişik duvarlar tek parça, yani tek kutu olarak yazılır: 17×17'de 133–144 parça çıkar. `dunya.py`'ye dokunulmadı.

## Üretici

Algoritma **özyinelemeli geri izlemedir** (yığınla DFS; START hücresinden başlar, rastgelelik yalnız
`random.Random(tohum).random()`'dan gelir, Python sürümleri arasında kararlıdır). Sonuç mükemmel bir labirenttir: tam bağlı, döngüsüz.

Seçim gerekçesi, 17×17, 50 tohum (`uretici.py istatistik`):

| Algoritma | Çözüm hücre | Çıkmaz | Çap hücre |
| --- | --- | --- | --- |
| geri izleme (seçilen) | 109 [43–179] | 30 [21–38] | 167 [130–194] |
| büyüyen ağaç p 0,75 | 57 [35–105] | 49 [39–60] | 97 |
| büyüyen ağaç p 0,5 | 45 | 64 | 78 |
| Wilson (düzgün ağaç) | 50 [39–87] | 84 [74–94] | 76 |

Geri izleme, örnekteki gibi uzun ve dolambaçlı geçitler üretir. Çıkmaz sayısı daha azdır (≈ 30) ama her çıkmaz **uzun** bir daldır.
Wilson ve Kruskal çok sayıda çıkmaz verir, ama bunların çoğu tek hücrelik ceplerdir. LiDAR (12 m) bu cepleri koridordan geçerken
görür, yani sınav olarak zayıf kalırlar. Robotu gerçekten zorlayan, girilmeden ucu görülemeyen uzun yanlış dallardır. Araştırma
notu sınamada başka bir üretecin de kullanılmasını öneriyor; bunun için `--algoritma wilson` ve `--algoritma agac:0.75` hazır.

Parametreler: satır, sütun, `--hucre` (m), `--tohum`, `--start kenar:hucre` (varsayılan `ust:0`, yani sol üst hücrenin üst
kenarı), `--finish kenar:hucre` (varsayılan `alt:-1`, yani sağ alt hücrenin alt kenarı). Kenar `ust`, `alt`, `sol` ya da `sag`
olabilir. Dış sınırda START ve FINISH için birer hücrelik açıklık bırakılır. Labirentin çevresinde 3 m açık zemin vardır:
MuJoCo zemini sonsuzdur, 2B haritada çevre duvarı kapalıdır. Böylece robot iki açıklıktan da dışarı çıkabilir, FINISH'in
dışında da LiDAR boşluk görür (doğrulamada sınandı).

**START pozu:** gövde merkezi START çizgisinin **0,45 m içinde**, içeri bakar. Ayak izinin tamamı içeride kalır (arka kenar
0,186 m içeride). Arka dingil etrafında yerinde dönülse bile gövde merkezi çizgiye en çok 0,080 m yaklaşır, yani hakem yanlış tetiklenmez.

### 3B sahne JSON'undaki `labirent` alanı

`satir`, `sutun`, `hucre_m`, `tohum`, `algoritma` alanlarına ek olarak:
- `start`: `kenar`, `hucre`, `cizgi` [[x1, y1], [x2, y2]], `ic_normal`, `poz` [x, y, th rad].
- `finish`: `kenar`, `hucre`, `cizgi`, `ic_normal`.
- `cozum_yolu`: hücre merkezleri. Bununla birlikte `cozum_hucre_sayisi`, `cozum_uzunlugu_m` (= hücre sayısı × hücre; çizgiden
  çizgiye, merkezlerden geçen kırık çizgi) ve `cozum_donus` {d90, d180}.
- `toplam_gecit_m` (= (hücre − 1) × hücre) ve `gecit_sayisi`.
- `cikmaz_sayisi`: tek açık kenarlı hücreler; açıklık da açık kenar sayılır.
- `cap_hucre`, `duvar_takip` {sol_el_hucre, sag_el_hucre}.
- `sinir` [x0, y0, x1, y1]: dış sınır.
- `hucreler`: satır başına onaltılık dize; açık kenar bitleri K 1 (+y), D 2 (+x), G 4 (−y), B 8 (−x), r = 0 en üst satır.

Yükleyiciler (`dunya.sahne_oku`, `gorunum3b.Pencere`, `Harita`) bilinmeyen anahtarlara bakmaz. **Keşif beyni bu alanı OKUMAMALI**
(ön bilgi yasak). Alan yalnız hakem ve değerlendirme içindir.

## Sahneler

| Sahne | Amaç | Boyut | Kenar m | Çözüm m (hücre) | Toplam geçit m | Çıkmaz | Duvar parçası |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `labirent_5x5_t1` | geliştirme | 5×5 | 6,5 | 14,3 (11) | 31,2 | 2 | 14 |
| `labirent_7x7_t1` | geliştirme | 7×7 | 9,1 | 32,5 (25) | 62,4 | 4 | 24 |
| `labirent_9x9_t1` | sınama | 9×9 | 11,7 | 40,3 (31) | 104,0 | 9 | 42 |
| `labirent_9x9_t2` | sınama | 9×9 | 11,7 | 29,9 (23) | 104,0 | 10 | 36 |
| `labirent_9x9_t3` | sınama | 9×9 | 11,7 | 55,9 (43) | 104,0 | 10 | 34 |
| `labirent_13x13_t1` | sınama | 13×13 | 16,9 | 76,7 (59) | 218,4 | 12 | 73 |
| `labirent_13x13_t2` | sınama | 13×13 | 16,9 | 71,5 (55) | 218,4 | 14 | 76 |
| `labirent_13x13_t3` | sınama | 13×13 | 16,9 | 144,3 (111) | 218,4 | 22 | 85 |
| `labirent_17x17_t1` | final | 17×17 | 22,1 | 92,3 (71) | 374,4 | 26 | 133 |
| `labirent_17x17_t2` | final | 17×17 | 22,1 | 118,3 (91) | 374,4 | 28 | 135 |
| `labirent_17x17_t3` | final | 17×17 | 22,1 | 131,3 (101) | 374,4 | 30 | 144 |

Tohum, adın sonundaki t numarasıdır. Aile tohumları 1–3 sırayla alındı, seçilmedi. 17×17 ailesinin çözüm yolları DFS
ortalamasının (142 m) altında kalıyor; bu bir şans sonucudur, ayıklama yapılmadı. Başka tohum ya da boyut için:
`py -3 kod\fizik\labirent\uretici.py uret --satir 9 --sutun 9 --tohum 7` komutu `labirent_9x9_t7` sahnesini üretir. Hücre boyu
varsayılandan farklıysa adın sonuna `_h<cm>` eklenir.

## Fizibilite (15 dakika)

**Model:** düz kısımlar v hızıyla, her 90° dönüş 2,3 s, her 180° dönüş 4,6 s sürer. 90° süresi `dur` ve aşmayla birlikte
gezinmenin ölçtüğü 1,4 s'nin ve ONERI tablosundaki 2,0–2,6 s'nin üstünde; hızlanma bu sürelere gömülü sayıldı. Hesap TAHMİN'dir,
kaba ama iyimser değildir. Stratejiler:
- (a) Çözüm yolunu bilerek yürümek: alt sınır; ön bilgisiz robot bunu yapamaz.
- (b) Her geçidi bir kez gezmek: ağaçta fiziksel olarak olanaksız, yalnız ölçek göstergesi.
- (c) Tam DFS keşfi: her geçit iki kez, FINISH'e giden yol bir kez.
- Duvar takibi (sol el / sağ el): ön bilgisiz ve FINISH'i garanti eden en basit strateji.
- "Görüş budaması": LiDAR'la uçtan uca görülen düz çıkmazlara girilmez (idealize).

`uretici.py fizibilite`, sahne başına (dk):

| Sahne | t_min = L*/0,39 | (a) çözüm yolu @0,39 / 0,30 / 0,25 | (b) geçitler bir kez @0,30 | (c) tam DFS @0,39 / 0,30 | sol / sağ el @0,30 | sol / sağ el + budama @0,30 |
| --- | --- | --- | --- | --- | --- | --- |
| 5x5_t1 | 0,6 | 0,9 / 1,1 / 1,2 | 2,4 | 3,6 / 4,3 | 2,5 / 1,1 | 2,2 / 1,1 |
| 7x7_t1 | 1,4 | 2,0 / 2,4 / 2,8 | 4,5 | 6,5 / 7,7 | 4,4 / 5,0 | 4,0 / 4,2 |
| 9x9_t1 | 1,7 | 2,5 / 3,0 / 3,4 | 7,7 | 11,8 / 14,0 | 6,0 / 3,5 | 4,8 / 3,0 |
| 9x9_t2 | 1,3 | 1,7 / 2,1 / 2,5 | 7,3 | 11,6 / 13,9 | 6,0 / 2,1 | 4,6 / 2,1 |
| 9x9_t3 | 2,4 | 3,3 / 4,0 / 4,6 | 7,1 | 10,1 / 12,0 | 4,8 / 7,2 | 4,0 / 5,5 |
| 13x13_t1 | 3,3 | 4,8 / 5,8 / 6,6 | 15,6 | 23,4 / 28,0 | 10,5 / 21,7 | 8,8 / 19,1 |
| 13x13_t2 | 3,1 | 4,3 / 5,2 / 6,0 | 15,7 | 24,0 / 28,7 | 10,4 / 21,2 | 8,9 / 18,8 |
| 13x13_t3 | 6,2 | 8,8 / 10,7 / 12,3 | 15,7 | 21,4 / 25,1 | 15,7 / 15,4 | 13,1 / 12,5 |
| 17x17_t1 | 3,9 | 5,7 / 6,9 / 7,9 | 27,3 | 43,1 / 51,6 | 19,2 / 37,4 | 17,5 / 31,7 |
| 17x17_t2 | 5,1 | 7,1 / 8,6 / 9,9 | 27,4 | 42,3 / 50,4 | 12,9 / 27,9 | 11,3 / 24,8 |
| 17x17_t3 | 5,6 | 7,9 / 9,6 / 11,0 | 27,1 | 41,4 / 49,3 | 40,8 / 14,5 | 35,5 / 12,4 |

**Dağılım:** boyut başına 100 yeni tohum (1001–1100), v 0,25 m/s, `uretici.py fizibilite --dagilim --v 0.25`. "Rastgele el"
sütunu, el önceden bilinmeden seçildiğinde de başarıyı gösterir: iki elin ikisi de 15 dakikaya sığmalıdır.

| Boyut | L* ort. [min–max] m | (a) çözüm yolu > 15 dk | en iyi el ≤ 15 dk | en iyi el + budama ≤ 15 dk | rastgele el (iki el de) + budama ≤ 15 dk | tam DFS ≤ 15 dk |
| --- | --- | --- | --- | --- | --- | --- |
| 5×5 | 19 [12–30] | %0 | %100 | %100 | %100 | %100 |
| 7×7 | 32 [17–56] | %0 | %100 | %100 | %100 | %100 |
| 9×9 | 50 [25–87] | %0 | %100 | %100 | %100 | %52 |
| 13×13 | 99 [35–162] | %0 | %63 | %88 | %18 | %0 |
| 17×17 | 142 [58–272] | **%18** | %23 | %29 | **%7** | %0 |

Duyarlılık (aynı 100 tohum, v 0,30): 17×17'de (a) > 15 dk oranı %11, rastgele el + budama %8; hücre 1,20 m'de %10 ve %10;
v 0,39'da %3 ve %14. Üreteç değişince sonuç değişmiyor: büyüyen ağaç ve Wilson'da çözüm yolu hep sığıyor (L* 64–77 m), ama
rastgele el + budama başarısı %0–1.

**Hüküm (15 dakika kuralı değişmeden):**
- **5×5–9×9:** her strateji sığar, tam DFS bile (9×9'da v 0,25'te yarı yarıya). Geliştirme ve ilk sınama için uygundur, keşfin kalitesini ayırt etmez.
- **13×13: kuralla anlamlı sınav budur.** Çözüm yolu her zaman sığar (en uzunu 12 dk). Tam keşif hiç sığmaz. Kör duvar takibi kabaca yarı yarıya kalır, akıllı bir keşif (sınır tabanlı, uzağı görme) fark yaratır.
- **17×17 (final):** 15 dakika çok sıkı. 0,25 m/s'de labirentlerin %18'inde **çözüm yolunun kendisi bile** sığmıyor. Ön bilgisiz basit stratejiler %7–29 arası başarıya ulaşıyor. Bizim üç final labirentinde çözüm yolu sığıyor (0,25'te 7,9 / 9,9 / 11,0 dk), yani bunlar olanaksız değil, ama yalnız iyi bir keşifle geçilir. Sınavın anlamlı olması için iki seçenek var (kural değişmeden):
  1. **Final boyutunu 13×13–15×15 tut**, ya da 17×17'yi "üst sınıf" sınavı olarak ayrı raporla. Başarı oranından çok `p_en` ve süre üzerinden karşılaştır.
  2. **Hız sınırını 0,39 m/s'ye çıkar** (teker azamisi). Çözüm yolu sığmama oranı %18'den %3'e iner, ama keşif başarısı yine düşük kalır (%14). Hücreyi 1,20 m'ye küçültmek ise çok az kazandırır (%7 → %10) ve dönüş payını bitirir. Önerilmez.

  Darboğaz geometri değil, keşfin kat ettiği yol. 17×17'nin 15 dakikada geçilmesi keşif beyninin işi.

## Hakem

```
from hakem import Hakem               # sys.path'e kod/fizik/labirent
h = Hakem("labirent_9x9_t1", sure_siniri_s=900.0, ayar=None)   # ad ya da 3B sahne sözlüğü
h.guncelle(t, (x, y, th), temas_var)  # her denetim adımında; gövde merkezi yer gerçeği; temas_var = dunya.temas_engel()
h.bitti, h.sonuc                       # sonuc: durum, sure_s, yol_m, carpma_sayisi, carpma_suresi_s, kesfedilen_hucre,
                                       # toplam_hucre, cozum_uzunlugu_m, yol_verimi, p_en, sikisma_sebebi, puan, puan_dokumu, olaylar
```

Kurallar, öncelik sırasıyla (aynı adımda FINISH önce gelir):

| Sonuç | Koşul | Eşik ve gerekçe |
| --- | --- | --- |
| `basari` | Gövde merkezi FINISH çizgisini içeriden dışarı geçer | Geçiş, merkez çizginin **0,05 m** dışına çıkınca onaylanır (histerezis; çizgi üstünde titreşim iki kez saymaz). Yanlarda çizgi ucundan 0,10 m pay |
| `fail_start` | Gövde merkezi START çizgisini içeriden dışarı geçer | Aynı histerezis. START pozu 0,45 m içeride; titreşim, 0,35 m geri kayma ve arka dingil çevresinde tam tur tetiklemez (test) |
| `fail_sure` | t − t0 ≥ 900 s | t0, ilk `guncelle` çağrısındaki t'dir |
| `fail_sikisma` (hareketsiz) | Son **60 s** boyunca **arka dingil noktası** pencere başındaki yerinden **0,20 m**'den fazla uzaklaşmadı | Duvara dayanıp teker çevirme ve yerinde dönüp durma da hareketsizdir. Arka dingil seçildi, çünkü yerinde dönüşte gövde merkezi 0,37 m'lik çember çizer ve hareket ediyormuş gibi görünürdü. 60 s ve 0,2 m araştırma notundaki değerdir. Meşru bir duruş (tarama, plan) birkaç saniye sürer |
| `fail_sikisma` (ilerlemesiz) | **300 s** boyunca yeni hücreye girilmedi | İki dal arasında gidip gelen ya da döngüye giren beyni yakalar. 300 s sürenin üçte biridir; 0,25 m/s'de 75 m, yani 17×17'de bile uzun bir geri dönüşe yeter. Ayar: `ilerlemesiz_s` |
| Çarpma | `temas_var` False → True geçişi bir olaydır. Önceki temasın bitişinden sonraki **1 s** içinde yeniden başlayan temas aynı olay sayılır | Sürekli sürtünme tek olaydır, ama süresi ayrıca `carpma_suresi_s` olarak toplanır |

Ek kayıtlar:
- `kesfedilen_hucre`: gövde merkezinin girdiği hücre sayısı (görülen değil, ziyaret edilen hücre).
- `yol_m`: gövde merkezinin kat ettiği yol.
- `yol_verimi` = min(1, çözüm / yol).
- `olaylar`: zaman damgalı liste (baslangic, carpma, sonuç, `sinir_disi_uyari`). `sinir_disi_uyari`, merkezin açıklık dışında labirentten çıkması demektir, yani duvar delinmiş olabilir.

Hakem robota hiçbir şey döndürmez, robotun beynine bilgi sızdırmaz. Ayarlar `ayar={...}` ile değişir; bilinmeyen anahtar hata verir.

**Jeodezik uzaklık g(x):** gerçek labirent grafiğinde FINISH çizgisine uzaklıktır. Her hücrenin iskeleti, merkezden açık
kenarların ortasına uzanan yarım kenarlardır. Nokta en yakın yarım kenara izdüşürülür:
- FINISH'e giden yarım kenarda g = d·h + h/2 − s,
- dallarda g = d·h + h/2 + s.

Burada d, hücrenin FINISH'e adım sayısı; s, merkezden uzaklıktır. Hücre sınırlarında g süreklidir (test). g(START) = L* − 0,45 m.
FINISH'e kuş uçuşu yakın ama labirentte uzak bir çıkmaz düşük ilerleme verir.

## Puan (`puan.py`, formülün tek yeri)

Formül araştırma notu § 4'ten alındı (`planlama/labirent-kesif-arastirmasi.md`). T = 900 s,
p_en = maks_t (1 − g(x_t) / g(START)) ∈ [0, 1].

```
basari        S1 = 1000 + 500 · (1 − t/T)
fail_sure     S1 = 400 · p_en
fail_sikisma  S1 = 400 · p_en − 100
fail_start    S1 = −200
her durumda      − 50 · carpma_sayisi − 10 · carpma_suresi_s
ek tur (ana tur başarılıysa)  S2 = 300 · min(1, t*/t2) − 50 · çarpma,  t* = cozum_uzunlugu_m / 0,39;  değilse 0
```

Ölçek: tek tur −200…1500. Başarı 1000–1500 alır, başarısızlık en çok 400. Döküm `sonuc["puan_dokumu"]` içinde görünür,
terimlerin toplamı puana eşittir.

**Oyunlanabilirlik** (testli):
- **Kımıldamamak** sıkışmaya düşer: −100 olur, yani her zaman aşımından kötüdür.
- **İleri geri salınmak** puan toplamaz, çünkü p_en en iyi değerdir, birikmez.
- **START'tan çıkmak** ilerleme ne olursa olsun −200'dür.
- **Duvara sürtünerek 10 s kazanmak** +5,6 süre primi getirir, karşılığında en az −50 − 10·s ceza yer. Hiçbir zaman kârlı değildir.
- Çarpma cezasına **tavan konmadı.** Tavan olsaydı, tavana ulaşan robot için sonraki her çarpma bedava olurdu. Bu yüzden çok çarpan bir başarı, temiz bir başarısızlığın altına düşebilir (örneğin 20 çarpma −1000). Bunu bilerek kabul ettim: gerçek robotta duvara 20 kez çarpmak, bitirememekten kötüdür.

**Taslaktan ve nottan farklar:**
- Brief'teki taslakta yol verimi primi ve keşfedilen hücre oranı da vardı. İkisini **puana koymadım**, ama sonuçta ayrı alan olarak duruyorlar:
  - Yol verimi süreyle neredeyse aynı şeyi ölçer; iki kez saymak olurdu.
  - Keşif oranı, başarısızlıkta çıkmazlara dalmayı ödüllendirir. Asıl hedefle (FINISH) çelişir, ilerlemeyi zaten p_en ölçüyor.
- Ölçek 0–1000 değil 1500'e kadar (notun ölçeği). Parametre araması için ölçek önemsiz.
- Notta çözülmemiş bir ayrıntı vardı: p_en'in kesikli hücre adımı yerine sürekli olması. Bunu yukarıdaki iskelet izdüşümüyle çözdüm; amaç fonksiyonu olarak daha pürüzsüz.

## Doğrulama

`"%LALE_SIM_VENV%\Scripts\python.exe" kod\fizik\labirent\uretici.py dogrula [sahne ...]` her sahnede şunları kontrol eder. Son
sonuçlar `testler/dogrulama_son.json` dosyasına yazılır.
- 3B pencerenin kendi kurulumu (`gorunum3b.Pencere`) derlenir.
- START pozunda ve 5 s sonra temas yoktur, kayma < 5 mm.
- **Geometrik kontroller:**
  - Çözüm yolu boyunca (START pozundan FINISH'in 0,6 m dışına, 5 cm adımla, yol yönüne bakan) ayak izi ile duvar arasında en küçük açıklık 0,385 m.
  - **Her hücrede** arka dingil merkezde dururken 0–360° yerinde dönüşte açıklık 0,129 m; gövde merkezi çevresinde dönüşte 0,277 m.
  - START'ta dönüşte gövde merkezi çizginin 0,080 m içinde kalır.
- Açıklıklar açıktır; dış sınırda tam iki açıklık vardır.
- Labirent mükemmeldir: bağlı ve kenar sayısı = hücre − 1.
- **LiDAR:** çözüm yolundaki her hücre merkezinde 360 ışın, z 0,10 / 0,20 / 0,295 m (3B) ve 2B ile atılır. Kaçan her ışının labirentten **yalnız START ya da FINISH açıklığından** çıktığı denetlenir: duvar arasından sızan ışın olmamalı. FINISH'in 1 m dışında dışarıya bakan 81 ışının hepsi boşluk görmelidir.
- Başsız adım hızı ölçülür.

### Doğrulama sonuçları (2026-11-25, 11 / 11 TAMAM)

Her sahnede ortak sonuçlar:
- START'ta ve 5 s sonra temas yok, kayma 0,00 mm, yaw 0,000°.
- Duvar arası sızan ışın 0 (3B ve 2B).
- FINISH dışı boşluk 81 / 81.
- Açıklık: yol 0,385 m, dönüş (arka dingil) 0,129 m, dönüş (merkez) 0,277 m, START 0,387 m. START dönüşünde merkez çizginin 0,080 m içinde kalıyor.
- Labirent mükemmel, 2 açıklık.

Kaçan ışınların hepsi START ya da FINISH açıklığından çıkıyor.

| Sahne | geom | 3B ışın / kaçan | en uzak isabet m | RTF yalnız fizik / firmware çekirdeğiyle |
| --- | --- | --- | --- | --- |
| 5x5_t1 | 44 | 11 880 / 849 | 6,3 | 46 / 20 |
| 7x7_t1 | 54 | 27 000 / 828 | 7,2 | 38 / 19 |
| 9x9_t1 / t2 / t3 | 72 / 66 / 64 | 33 480 / 24 840 / 46 440 | 6,3 / 8,7 / 11,1 | 41 / 24 / 42 ; 18 / 11 / 20 |
| 13x13_t1 / t2 / t3 | 103 / 106 / 115 | 63 720 / 59 400 / 119 880 | 9,8 / 8,7 / 11,1 | 39 / 33 / 38 ; 17 / 17 / 18 |
| 17x17_t1 / t2 / t3 | 163 / 165 / 174 | 76 680 / 98 280 / 109 080 | 12,4 / 9,8 / 11,0 | 32 / 37 / 35 ; 17 / 19 / 18 |

**MuJoCo maliyeti:**
- Derleme 0,02 s (ilk açılışta 0,05 s).
- Robot dururken 17×17'de bile gerçek zamanın 17 katından hızlı.
- **LiDAR açık, 0,25 m/s sürüşte** (`lidar.LidarDeneyi`, başka bir doğrulama süreciyle aynı anda ölçüldü, yani alt sınır):
  - `koridor_4` V0 14,0 / ONERI-MAKARA 7,5.
  - `labirent_9x9_t1` 11,0 / 6,3.
  - `labirent_17x17_t3` **10,0 / 5,5**.

900 s'lik bir deneme en kötü durumda (makaralı omni + LiDAR) ≈ 2,7 dk sürer. 17×17 gerçek zamandan yavaş değil. Duvar birleştirmesi
zaten yapıldığı için geom sayısı sorun olmuyor. 9x9_t2 satırındaki düşük RTF, o an makinedeki yükten kaynaklanıyor.

**Depo testleri:** `kod\testler\kos.py` 58 / 58 geçiyor; yeni haritalar `test_harita` taramasına giriyor, başlangıç temassız.
İlk koşuda 1 hata vardı: yük altında, bilinen gerçek zamanlı test. İkinci koşu temiz geçti.

## Komutlar

| Ne | Komut |
| --- | --- |
| Aileyi üret / tek labirent | `py -3 kod\fizik\labirent\uretici.py uret` / `... uret --satir 9 --sutun 9 --tohum 7` |
| Üstten görünüm PNG'leri | `py -3 kod\fizik\labirent\uretici.py ciz [sahne ...]` (matplotlib) |
| Fizibilite tablosu / dağılım | `py -3 kod\fizik\labirent\uretici.py fizibilite` / `... fizibilite --dagilim --v 0.25 [--hucre 1.2] [--algoritma wilson]` |
| Algoritma karşılaştırması | `py -3 kod\fizik\labirent\uretici.py istatistik --boyut 17` |
| Birim testleri | `py -3 -m unittest discover -s kod\fizik\labirent\testler -v` (≈ 15 s) |
| Başsız doğrulama | `%V% kod\fizik\labirent\uretici.py dogrula [sahne ...]` |
| 3B pencere | `kod\simulasyon3b.bat labirent_9x9_t1` |
| 2B görünüm | `kod\simulasyon.bat --harita labirent_9x9_t1` |
