# Katmanlı öneri: 6, 10 ve 14 sensörlü düzen yan yana (ve dondurma 3 adayları)

## Taze küme: bağımsız hüküm 3 (2026-11-26)

Kaynak: `hukum3.csv` ve `hukum3_fiz.csv` (`hukum3_tablo.md`). Ön kayıt: `on_kayit_3.md`.

- Beş düzen AYNI görev listesinde koşuldu: tohum 211–220 (hiçbir önceki CSV'de yok), bütün sahneler yeni (`h3_*`).
- Düzen başına 2742 uçurum ve 585 yanlış alarm koşusu. Üç tur da tamam, 0 hata.
- Önceden konan ölçüt aynı: uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma, bütün hızlar.

Hücre: `hakem düşme / koşu · fiziksel düşme / sürdürülen · en küçük pay cm`. Hakem düşmesi 0 ise fiziksel de 0'dır. Her
hücre ölçüldü.

| tehlike sınıfı | 6 `4OD+2AD` | 10 `6OD+4AD` | 14 `8WRD+4AD+2YR40` | **3A `8WRaD+4AD+2YR40`** | 3B `6OD+4AD` + kural |
| --- | --- | --- | --- | --- | --- |
| Merdiven başı / sahanlık kenarı, ileri (16x29, 18x26, burunlu 17x30) | 0 / 162 · 0 · 4,3 | 0 / 162 · 0 · 4,9 | 0 / 162 · 0 · 6,2 | 0 / 162 · 0 · 6,2 | 0 / 162 · 0 · 6,3 |
| Sahanlık köşesi, ileri (D 1,5 / 0,6 m) | **2 / 108** · 1 / 2 · −6,3 | 0 / 108 · 0 · 4,9 | 0 / 108 · 0 · 6,2 | 0 / 108 · 0 · 6,2 | 0 / 108 · 0 · 5,8 |
| Kuyu, ileri (dikdörtgen, menzil dışı) | 0 / 96 · 0 · 5,6 | 0 / 96 · 0 · 6,2 | 0 / 96 · 0 · 7,5 | 0 / 96 · 0 · 7,5 | 0 / 96 · 0 · 6,2 |
| Dar açıklık 0,48–0,85 m, ileri | 0 / 360 · 0 · 3,3 | 0 / 360 · 0 · 5,7 | 0 / 360 · 0 · 5,7 | 0 / 360 · 0 · 5,7 | 0 / 360 · 0 · 5,7 |
| Dar açıklığa geri | **21 / 288** · 19 / 21 · −9,2 | 0 / 288 · 0 · 5,1 | 0 / 288 · 0 · 4,9 | 0 / 288 · 0 · 4,9 | 0 / 288 · 0 · 6,5 |
| Geniş kenara geri | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 9,8 |
| Yerinde dönüş, geniş kenar (d 0,33–0,48) | 0 / 72 · 0 · 3,9 | 0 / 72 · 0 · 3,9 | 0 / 72 · 0 · 4,4 | 0 / 72 · 0 · 4,4 | 0 / 72 · 0 · 7,9 |
| Yerinde dönüş, dar açıklık yanında (d 0,33 / 0,38 / 0,43 / 0,48) | **109 / 384** · 0 / 109 · −9,5 | **110 / 384** · 0 / 110 · −9,3 | 0 / 384 · 0 · 0,4 | 0 / 384 · 0 · 0,4 | 0 / 384 · 0 · 3,8 |
| Dar yarık 8,5–16 cm | **238 / 840** · 118 / 238 · −7,6 | **68 / 840** · 17 / 68 · −5,1 | **2 / 840** · 0 / 2 · −0,4 | 0 / 840 · 0 · **0,3** | **61 / 840** · 27 / 61 · −4,5 |
| Eğik yarık 15–45° | **83 / 288** · 26 / 83 · −7,2 | **11 / 288** · 1 / 11 · −4,7 | 0 / 288 · 0 · 4,1 | 0 / 288 · 0 · 4,6 | **5 / 288** · 1 / 5 · −1,5 |
| İniş rampasının ucunda düşüş (6° / 9°) | 0 / 72 · 0 · 2,7 | 0 / 72 · 0 · 3,4 | 0 / 72 · 0 · 3,8 | 0 / 72 · 0 · 3,8 | 0 / 72 · 0 · 3,5 |
| **Yanlış durma** (13 sahne: koyu şerit, eşik, halı, derz, parlak zemin, iniş rampası) | 0 / 585 | 0 / 585 | 0 / 585 | 0 / 585 | 0 / 585 (sürünme 265 / 585) |
| **Uçurum toplamı** | **453 / 2742** · 164 | **189 / 2742** · 18 | **2 / 2742** · 0 | **0 / 2742** · 0 | **66 / 2742** · 28 |
| **Ön kayıtlı ölçüt** | GEÇMEDİ | GEÇMEDİ | GEÇMEDİ | **GEÇTİ** | GEÇMEDİ |

- **Karar kuralı** (ön kayıt): ölçütü sağlayan en az sensörlü düzen onaylı seçimdir. Tek geçen 3A, `secim.json`'a
  "onaylı seçim" olarak yazıldı.
- **Sınır:** 3A'nın payı ince. En küçük pay 0,35 cm, 12 koşuda 1 cm'nin altında (10'u dar yarık, 2'si dar açıklık yanında
  dönüş). Aynı görevlerde ±2 cm'lik çift izli 14 sensörlü düzen iki kez 0,1–0,4 cm geçti.
- **6 sensörlü düzen** burada ortak koşulla ölçüldü: kısa kip K20 ve konum tutma (ön kayıt kararı). Rampa ucundaki 0 / 72
  bu koşulun sonucudur.
- **Bedel ve modellenmeyenler** aşağıdaki "Bedel" tablosunda: 3A için de 14 VL53L1X, 6 ROI'li sensör, yanda pencere,
  ≈ 0,70 m'den dar şeritte durma. Ek olarak 3A'da dış iz etek sınırına 9 mm.
- **3B'nin bedeli:** yerinde dönüş yok, 1 m geri yay yapar. Sürünme yanlış alarm koşularının 265 / 585'inde başladı.

## Önceki, görülmüş ızgara (bağımsız inceleme 3; yeni koşu yoktu)

Bağımsız inceleme (2026-11-26, üçüncü). Yeni koşu yok, bütün sayılar mevcut `sonuc/*.csv` dosyalarından sayıldı.
Bu tablo karar vermez, seçenekleri gösterir. **Hiçbir düzen önceden konan ölçütü ("uçurum koşularında 0 hakem düşmesi,
yanlış alarm koşularında 0 durma") kendi hüküm koşusunda tümüyle sağlamadı.** 14 sensörlü düzen `secim.json`'da duruyor,
ama durumu "ölçütü SAĞLAMAYAN en iyi aday"dır, onaylanmış seçim değildir.

### Nasıl okunur

- Hücre: `hakem düşme / koşu · fiziksel düşme · en küçük pay cm`. Pay = koşu boyunca dört teker merkezinin kenara en
  küçük yatay uzaklığı. Eksi pay, teker merkezinin kenarı o kadar geçtiği anlamına gelir.
- **Hakem düşmesi**: teker merkezi kenarı geçti, ya da eğim > 15°, ya da gövde z'si 3 cm'den çok düştü. Ölçüt bu sayıya
  bakar.
- **Fiziksel düşme**: teker 20 mm'den çok iner ya da eğim 5°'yi geçer (VARSAYIM ölçüt). Hakem düşmesi olan koşu ancak
  hakemden sonra sürdürülürse (`*_fiz` aşamaları) fiziksel sonuç bilinir. Sürdürülmeyen koşuda "ölçülmedi" yazar. Hakem
  düşmesi 0 ise fiziksel düşme de 0'dır, çünkü teker merkezi kenarı geçmeden teker inmez.
- **Kaynak türü**: **H** = hüküm ya da sınama koşusu (ayarda kullanılmamış tohum). **A** = ayar koşusu (tohum 1–2,
  düzeni seçmek için kullanıldı; iyimser okunmalı). "ölçülmedi" = o düzenle o sınıf hiç koşulmadı. Tahmin yapılmadı.
- Düzenler ve kaynakları:
  - **6 sensör** `4OD+2AD` (son commit edilen seçim): H = `sinama2` (tohum 101–110, dar açıklıkta 101–105). Bu koşular
    ilk zamanlama modeliyle (50 Hz, 4 m) ve konum tutmasız koşuldu; öbür ikisi kısa kip K20 ve konum tutmayla. Düz
    zeminde K20 aynı payı veriyor (`t_duyar`, SONUC T5). A = `t_delik_gel`, `t_delik_fiz`, `t_yaklasma_gel`,
    `t_rampa_ucurum`.
  - **10 sensör** `6OD+4AD`: H = `t_hukum` (tohum 201–205; dar açıklık, yarık, dönüş ve kötü birleşimde 201–203), fiziksel
    sonuç `t_hukum_fiz`. A = `t_aday_son`, `t2_yarik_gel`.
  - **14 sensör** `8WRD+4AD+2YR40`: H = `t2_hukum` (tohum 206–210; yarıkta 206–207, dar açıklık / dönüşte 206–208),
    fiziksel sonuç `t2_hukum_fiz`. A = `t2_donus_gel2`, `t2_yarik_gel2` (bu aşama yan sensörsüz `8WRD+4AD` ile koşuldu).

### Tehlike sınıflarına göre

| tehlike sınıfı | 6 sensör `4OD+2AD` | 10 sensör `6OD+4AD` | 14 sensör `8WRD+4AD+2YR40` |
| --- | --- | --- | --- |
| Merdiven başı ve sahanlık kenarı / köşesi, ileri (merdiven 15x28, 19x25, köşe; 10 ve 14'te ayrıca burunlu merdiven ve 12 cm basamak) | H 0 / 720 · 0 · 4,2 (burunlu merdiven ve 12 cm basamak ölçülmedi) | H 0 / 570 · 0 · 4,8 | H 0 / 570 · 0 · 2,1 (köşe: başlangıçta teker yan kenara 2,2 cm, yan sensör 0,08 s'de durdurur) |
| Kuyu, ileri | H 0 / 240 · 0 · 5,8 | H 0 / 120 · 0 · 6,1 | H 0 / 120 · 0 · 7,3 |
| Dar açıklık 0,45–0,70 m, ileri (acik_45 / 55 / 65, acik_60_sig, dar_merdiven_60) | H 0 / 1125 · 0 · 3,0 | H 0 / 675 · 0 · 4,8 | H 0 / 675 · 0 · 5,5 |
| (ek) dar açıklık 0,75–0,90 m, ileri | H 0 / 675 · 0 · 4,5 | H 0 / 405 · 0 · 4,8 | H 0 / 405 · 0 · 5,5 |
| Geri gidiş, geniş kenar (merdiven) | H 0 / 60 · 0 · 6,8 | H 0 / 100 · 0 · 8,2 | H 0 / 100 · 0 · 8,3 |
| Geri gidiş, dar açıklığa | H ölçülmedi. A (acik_40–100): **24 / 200** (0,40–0,60 m'de 24 / 120) · ölçülmedi (koşu düşmede kesildi) · −9,2 | H 0 / 81 · 0 · 7,5 | H 0 / 81 · 0 · 6,8 |
| Yerinde dönüş, geniş kenar (merdiven, d 0,35 / 0,45 / 0,55) | H 0 / 60 · 0 · 4,4 | H 0 / 60 · 0 · 4,5 | H 0 / 60 · 0 · 6,7 |
| Yerinde dönüş, dar açıklık yanında, d 0,35 m | ölçülmedi | H ölçülmedi. A: **31 / 60** · ölçülmedi · −8,2 | H 0 / 90 · 0 · 7,6 (A 0 / 60) |
| … d 0,40 m | H ölçülmedi. A: **17 / 60** · ölçülmedi · −3,2 | H **18 / 54** · fiziksel 0 / 54 (sürdürülünce teker kenarı 2 cm geçer, inmez) · −1,6 (sürdürülünce −2,0) | H 0 / 90 · 0 · **0,5** (A 0 / 60) |
| … d 0,45 m | ölçülmedi | ölçülmedi | H 0 / 90 · 0 · 3,8 |
| … d 0,50 m | H ölçülmedi. A: 0 / 60 · 0 · 7,0 | H 0 / 54 · 0 · 8,9 | H 0 / 90 · 0 · 8,8 |
| Dar yarık 9 cm x 1 m | ölçülmedi | ölçülmedi | H 0 / 108 · 0 · **0,6** |
| … 10 cm | H ölçülmedi. A: **18 / 56** · fiziksel **6 / 56** · −4,8 | H ölçülmedi. A: **12 / 80** ve 3 / 21 · ölçülmedi · −4,2 | ölçülmedi (A, yan sensörsüz `8WRD+4AD`: 0 / 80) |
| … 11 cm | ölçülmedi | ölçülmedi | H **1 / 108** · fiziksel 0 / 12 · **−0,3** |
| … 12 cm | ölçülmedi | H ölçülmedi. A: **11 / 80** · ölçülmedi · −5,0 | ölçülmedi (A, yan sensörsüz: 0 / 80) |
| … 13 cm | ölçülmedi | ölçülmedi | H 0 / 108 · 0 · 2,6 |
| … 14 cm | ölçülmedi | H **9 / 108** · fiziksel **6 / 108** (y 0,23: teker 41–54 mm iner, gövde 6–14° eğilip zemine değer) · −3,8 | H 0 / 120 · 0 · 4,3 |
| **9–14 cm, hüküm toplamı** | **ölçülmedi** | **9 / 108** (yalnız 14 cm), fiziksel 6 | **1 / 444**, fiziksel 0 |
| (ek) yarık 15–20 cm, ayar | A 15 cm **20 / 56**, fiziksel **18 / 56**; 20 cm **16 / 56**, fiziksel **14 / 56** | A 15 cm 5 / 80, 20 cm 0 / 80 (fiziksel ölçülmedi) | A yan sensörsüz: 0 / 160 |
| (ek) yarık 17–28 cm, hüküm | ölçülmedi | H 0 / 324 · 0 · 3,6 | H 0 / 324 · 0 · 5,2 |
| (ek) iniş rampasının ucunda düşüş | H ölçülmedi. A (10°, tohum 1): konum tutma + 2,0 m/s² ile 0 / 10, tutmasız 30 / 30 düşer | H (8°) 0 / 40 · eğim rampanın kendisi · 7,6 (0,25 m/s) / 3,5 (0,39) | H (8°) 0 / 40 · aynı · 8,3 / 4,8 |
| (ek) iskele 0,9 m (üç yanı boşluk) | ölçülmedi | H 0 / 135 · 0 · 6,2 | H 0 / 135 · 0 · 6,6 |
| (ek) kötü koşulların birleşimi (+20 ms, montaj en kötü, µ 0,5, +10 kg; 0,25 / 0,30 m/s) | ölçülmedi | H 0 / 126 · 0 · 4,9 | H 0 / 142 · 0 · 2,1 |
| **Yanlış durma** (12 sahne: derz, eşik, halı, koyu bant, rampalar, düz) | H 0 / 540 | H 0 / 540 | H 0 / 540 (A ayrıca 0 / 84, 0 / 192) |
| **Uçurum koşularının hüküm toplamı** | H 0 / 2900 (bu ızgarada dar yarık, dar açıklığa geri ve dar açıklık yanında dönüş yoktu) | H **27 / 2872**, fiziksel **6** | H **1 / 3476**, fiziksel 0 (rampa ucu hariç 0 / 3436) |

### Bedel

| | 6 sensör | 10 sensör | 14 sensör |
| --- | --- | --- | --- |
| VL53L1X sayısı (sensör başına bir XSHUT hattı) | 6 | 10 | 14 |
| ROI ile 15° koni | 0 | 0 | 6 (dört çift iz, iki yan). ROI'nin sinyal / menzil kaybı modellenmedi |
| I2C hattı | modellenmedi: simülasyon bütün sensörleri 20 ms'de gecikmesiz okur | modellenmedi | modellenmedi. SONUC'taki tahmin: büyük olasılıkla iki hat (ölçülmedi) |
| Etekte pencere | köşelerde | köşelerde | köşelerde ve iki yanda |
| Sürülebilir en dar şerit, ölçülen | ölçülmedi | 0,90 m iskele: 0 / 135 | 0,90 m iskele: 0 / 135 |
| Sürülebilir en dar şerit, geometrik hesap (simülasyonda ölçülmedi) | ≈ 0,60 m (köşe izi y ±0,30) | ≈ 0,60 m (köşe izi y ±0,30) | ≈ 0,70 m (yan iz y ±0,35; robot yan kenarı bir uçuruma ≈ 9 cm'den yakınken durur) |
| Durum | son commit edilen seçim | ilk hükmünde ölçütü sağlamadı (27 hakem, 6 fiziksel) | ölçütü sağlamayan en iyi aday (1 hakem, 0 fiziksel); commit edilmedi |

Gövde genişliği 0,52 m. Hız önerisi üçünde de 0,25 m/s.

### Hüküm verisinin bağımsızlığı (sınırlama)

- Tohumlar ayrı: `t2_hukum`'un 206–210'u başka hiçbir CSV'de yok, `t_hukum`'un 201–205'i ondan önce hiçbir CSV'de
  yoktu. Görev listeleri bugünkü koddan yeniden üretildi, ham kayıtla 0 fark.
- Geometri ve senaryo çoğunlukla yeni değil: `t2_hukum`'un 4016 görevinden **2992'si** `t_hukum`'la birebir aynı
  (sahne, senaryo, açı, hız, dönüş hızı, d, yanal), yalnız tohum farklı. Tohum yalnız ±2° açı, yanal ve başlangıç
  uzaklığı oynamasını, sensör gürültüsünü ve fazını değiştirir. 2303 görev `sinama2`'yle de aynı. Hiç koşulmamış sahne
  yalnız `yarik_9 / 11 / 13` (328 koşu).
- İlk hükmün düşen durumları (`yarik_14` y 0,23 ve dar açıklık yanında d 0,40 dönüşü) düzeltmeyi yönlendirdi ve
  `t2_hukum`'da aynen yinelendi (12 + 108 görev). O görevler bu düzen için artık görülmüş veridir.
- Yanlış alarm sahnelerinin 7'si (315 koşu) geliştirme sahnesi. Yan sensörlerin yanlış alarmı bu yedi sahnede ayarlandı
  (`t2_donus_gel`, `t2_donus_gel2`, tohum 1–2).
- Sızıntı yok: denetçi (`denetci.py`) yalnız `(t, sensör, okuma)` alır. Sensör modeli gerçek pozu yalnız ışın
  izlemek için kullanır. Hakem yalnız ölçer. `zorla_tetik` yalnız durma ve fren ölçümünde var, hükümde yok.

### Tek cümlelik sonuç

Simülasyonda, gerçek bir okul binasındaki merdiven başını, sahanlık kenarını / köşesini, kuyuyu ve 0,45–0,90 m dar
açıklığa ileri yaklaşmayı üç düzen de 0 düşmeyle kapsıyor. Dar açıklığa geri gitmeyi 10 ve 14 sensör kapsıyor, 6 sensör
ayarda 24 / 200 düşüyor. Dar açıklığın yanında yerinde dönmeyi yalnız 14 sensör kapsıyor (d 0,40'ta pay 0,5 cm); 10
sensörde 18 / 54 hakem düşmesi var, fiziksel 0. İniş rampasının ucunu konum tutmalı 10 ve 14 sensör kapsıyor. **9–14 cm
dar yarık açık kalıyor**: 6 sensörde hükümde hiç ölçülmedi, ayarda 10 cm'de 6 / 56 fiziksel düşme var. 10 sensörde 14 cm'de
6 / 108 fiziksel düşme var. 14 sensörde fiziksel düşme 0, ama 11 cm'de hakem düşmesi 1 / 444 ve 9–11 cm'de pay −0,3…+0,6 cm,
yani ölçütün sınırında.

### Seçenekler (satın alma kararı burada verilmez)

1. **6 sensör** (commit edilen): en ucuz. Kullanmak için ya dar yarık, dar açıklığa geri gitme ve dar açıklık yanında
   yerinde dönme yasaklanmalı ya da bu yerler binada fiziksel olarak kapatılmalı (kapak, korkuluk). Bu üç sınıf bu
   düzenle hükümde hiç ölçülmedi.
2. **10 sensör**: dar açıklığa geri gitmeyi de kapsıyor. Açık kalanlar: dar açıklığın 0,45 m yakınında yerinde dönme
   (hakem düşmesi var, fiziksel 0) ve 14 cm yarık (fiziksel düşme var).
3. **14 sensör**: ölçülen bütün sınıflarda fiziksel düşme 0. Ölçüt 11 cm yarıkta bir hakem düşmesiyle sağlanmadı.
   Bedeli: 14 sensör, 6 ROI'li sensör (sinyal kaybı ölçülmedi), olası ikinci I2C hattı, yanda pencere, ≈ 0,70 m'den dar
   şeritte durma.
4. Bir düzenin onaylanması için: yeni bir düzeltme, ayar ve hiç kullanılmamış tohum ve geometriyle yeni bir hüküm. Ya
   da ölçütün kendisi (hakem mi, fiziksel mi) karar verecek kişi tarafından açıkça yeniden konmalı. Bu belge ölçütü
   değiştirmez.
