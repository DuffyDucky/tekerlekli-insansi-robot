# Sağ omuz modülü (2 eksen) + üst kol bağlantısı

FreeCAD 1.1 · `omuz_montaj.py` ile üretildi · 70 parça · çizim ve kontroller betikle tekrarlanabilir.

## Özet

| | |
|---|---|
| Eksenler | Öne-arka (S1, X ekseni) ve yana açma (S2, Z ekseni); iki eksen tek noktada kesişir |
| Yük yolu | Öne-arka: 6808-2RS rulman taşır, S1 yalnız döndürür. Yana açma: çatal iki taraftan tutulur (horn + 625ZZ) |
| Montaj kontrolü | 70 parça, ev pozunda **0 çakışma** (tolerans 0,5 mm³), tüm parçalar tek ve geçerli katı |
| Öne-arka serbest aralık | -60° … 180° arası hiçbir yere çarpmıyor (taranan aralığın tamamı) |
| Yana açma serbest aralık | 0° … 120° (her öne-arka açısında) |
| En küçük boşluk (kol aşağıda) | Kol × gövde 4.0 mm (Kol catali ↔ Rulman kapagi) |
| En kötü tork (eklem sınırları içinde) | Öne-arka 5.6 kg·cm, yana açma 5.7 kg·cm · DS3218MG ≈ 20 kg·cm → ≈ 3.5× pay |
| Hareketli kütle | Göbek grubu 148 g, kol grubu 108 g + dirsek ve aşağısı (tahmini) 260 g |

## Hangi parça neye, nasıl bağlanıyor

| Bağlantı | Nasıl oturuyor | Bağlantı elemanı |
|---|---|---|
| Omuz yuvası → sigma traversi | Yuva traversin ucuna 30 mm geçer (0,2 mm boşluk), uç duvarına dayanır. | 4× M6×16 DIN 912 + 4× M6 pul + 4× M6 çekiç somun (kanal 10), dört yüzde birer |
| S1 servo → omuz yuvası | Servo plakadaki yuvaya dışarıdan girer, kulakları plakanın dış yüzüne oturur. | 4× M4×16 DIN 912 + 4× M4 DIN 985 kontra somun (somunlar plakanın iç yüzünde) |
| S1 horn → S1 mili | 25 dişli mile geçer. | M3 merkez vidası (servo ile gelir) |
| Rulman kapağı → omuz yuvası | Kapağın iki kulağı yuvanın kollarına dayanır. | 4× M3×12 DIN 912 → yuvadaki 4× M3 ısıl gömme somun |
| 6808-2RS rulman → rulman kapağı | Dış bilezik Ø52 yuvaya sıkı geçer, servo tarafındaki dudağa dayanır. | Sıkı geçme (bağlantı elemanı yok) |
| Omuz göbeği → S1 horn + 6808 | Göbeğin Ø40 mili rulmanın iç bileziğinden geçer, Ø45 omzu iç bileziğe dayanır; ön yüzü horn'a oturur. | 4× M3×12 DIN 912, göbekteki havşalardan horn'un dişli deliklerine (3 mm diş) |
| S2 servo → omuz göbeği | Servo kulak plakasına önden girer, kulaklar plakanın ön yüzüne oturur. | 4× M4×16 DIN 912 + 4× M4 DIN 985 kontra somun |
| S2 horn → S2 mili | 25 dişli mile geçer. | M3 merkez vidası (servo ile gelir) |
| Kol çatalı (ön kol) → S2 horn | Çatalın ön kolu horn'un dış yüzüne oturur. | 4× M3×8 DIN 912 → horn dişli delikleri |
| Kol çatalı (arka kol) → omuz göbeği (karşı yatak) | 625ZZ çatalın Ø16 yuvasına sıkı geçer. Cıvata iç bileziği göbekteki Ø8 dayamaya sıkar, çatal serbest döner. Servo mili kolu tek başına taşımaz. | 1× M5×12 DIN 912 + 1× M5 pul → göbekteki M5 ısıl gömme somun |
| Üst kol tüpü → kol çatalı | Tüp çatalın Ø50,8 pimine 20 mm geçer, Ø56 bileziğe dayanır. | 2× M3×8 DIN 912 karşılıklı → çataldaki 2× M3 ısıl gömme somun |

## Montaj sırası

1. Isıl gömme somunları havyayla bas: yuvaya 4× M3 (kol uçları), göbeğe 1× M5 (arka plaka), çatala 2× M3 (pim).
2. 6808-2RS'yi rulman kapağına, 625ZZ'yi çatalın arka koluna bastır.
3. 4 çekiç somunu traversin dört kanalına sok. Yuvayı traverse geçir, 4× M6×16 + pulla sık.
4. S1'i yuvaya dışarıdan sok, 4× M4×16 + kontra somunla bağla.
5. S1'i 45° konumuna getir (Pi ya da servo test cihazıyla), horn'u kol aşağıdayken tak, merkez vidasını sık.
6. Rulmanlı kapağı yuvanın kollarına 4× M3×12 ile bağla.
7. Göbeği rulmandan geçirip horn'a oturt. 4× M3×12'yi havşalardan sık. **S2'den önce:** S2 takılınca bu vidalara erişilmez.
8. S2'yi göbeğe önden sok, 4× M4×16 + kontra somun. S2'yi 30° konumuna getir, horn'u tak, merkez vidasını sık.
9. Çatalı tak: ön kol horn'a 4× M3×8; arka kol M5×12 + pulla göbekteki somuna (rulmanı sıkar, çatal döner).
10. Üst kol tüpünü çatalın pimine geçir, 2× M3×8 ile sabitle.

## Satın alınacaklar

| Parça | Adet |
|---|---|
| 25T aluminyum disk horn | 2 |
| 625ZZ rulman 5x16x5 | 1 |
| 6808-2RS rulman 40x52x7 | 1 |
| DS3218MG servo | 2 |
| Sigma 40x40 agir kanal 10, 200 mm | 1 |

## Bağlantı elemanları

| Eleman | Adet |
|---|---|
| M3 isil gomme somun | 6 |
| M3x12 DIN 912 | 8 |
| M3x5 horn vidasi (servo ile) | 2 |
| M3x8 DIN 912 | 6 |
| M4 DIN 985 kontra somun | 8 |
| M4x16 DIN 912 | 8 |
| M5 DIN 125 pul | 1 |
| M5 isil gomme somun | 1 |
| M5x12 DIN 912 | 1 |
| M6 DIN 125 pul | 4 |
| M6 cekic somun, kanal 10 | 4 |
| M6x16 DIN 912 | 4 |

## Baskı parçaları (PETG)

| Parça | Ölçü (mm) | Kütle (g, %60 doluluk) | Yazıcıya sığar (230 mm) | STL |
|---|---|---|---|---|
| Omuz yuvasi | 76 × 76 × 67 | 50 | evet | `stl/omuz-yuvasi.stl` |
| Rulman kapagi | 76 × 60 × 14 | 11 | evet | `stl/rulman-kapagi.stl` |
| Omuz gobegi | 66 × 51 × 49 | 40 | evet | `stl/omuz-gobegi.stl` |
| Kol catali | 76 × 64 × 56 | 62 | evet | `stl/kol-catali.stl` |
| Ust kol tupu | 100 × 56 × 56 | 32 | evet | `stl/ust-kol-tupu.stl` |

## Kontrollerde bulunup düzeltilenler

- Rulman kapağı cıvatalarının başı kapak halkasına 0,75 mm³ biniyordu (cıvata oturmazdı). Delikler 1 mm dışarı alındı (z = ±33).

## Doğrulanacaklar ve açık işler

- **Horn delik dizilimi:** 25T disk horn'da M3 delikler 8,5 mm yarıçapta varsayıldı. Horn eline geçince kumpasla ölçülmeli, göbek ve çatal delikleri ona göre güncellenir.
- **Servo sürümü:** Eklem sınırları 180° servoya göre (öne −45…+135°, yana 0…120°). DS3218MG'nin 270° sürümü alınırsa sınırlar genişler, horn takma açıları değişir.
- **Gövde kabuğu:** V3 kabuğunun yan yüzü x = 152'de düz duvar varsayıldı. Omuz için kabukta Ø84 delik gerekiyor; V3 kabuğunda bu delik yok.
- **S2 kablosu:** Göbekle birlikte dönüyor. Kanal açılmadı; gevşek bir kablo halkasıyla gövdeye girmeli.
- **Tahmini ölçüler:** Çekiç somun 16×10×5, ısıl gömme somun M3 Ø4,6×5,7 / M5 Ø7×7, PETG baskı yoğunluğu %60. Parçalar gelince kumpasla doğrulanmalı.
- **Sıkı geçmeler:** Ø52 (6808) ve Ø16 (625ZZ) yuvalar nominal çizildi. Yazıcının toleransı için önce küçük bir deneme halkası basılmalı.
- **Omuz genişliği:** Yana açma ekseni gövde merkezinden 185 mm dışarıda (eski tasarımda kol ekseni 166). Omuzdan omuza ≈ 426 mm.
- **Dirsek ve aşağısı:** Tork hesabında 260 g ve omuzdan 200 mm aşağıda varsayıldı (eski modelden). Dirsek tasarlanınca hesap yenilenir.

## Dosyalar

- `omuz-montaj.FCStd`: FreeCAD montajı (3 grup, 2 döner eklem). `omuz-montaj.step`: tüm parçalar.
- `stl/`: 5 baskı parçası. `gorsel/`: görünümler, patlatılmış montaj, hareket animasyonu, çalışma alanı haritası.
- `omuz_lib.py` (parça ve standart eleman kütüphanesi), `omuz_montaj.py` (montaj + kontroller), `omuz_gorsel.py`, `omuz_rapor.py`.
