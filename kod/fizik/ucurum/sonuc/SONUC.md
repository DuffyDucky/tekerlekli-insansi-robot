# Uçurum sensörü: sonuç ve hüküm

Ne ölçüldü: aşağı inen merdiven, dik boşluk, kuyu, sahanlık köşesi ve robottan dar aşağı inen açıklıkta robotun zamanında durup durmadığı; aşağı bakan
VL53L1X türü sensörün sayısı, yeri, eğimi ve eşiği; ESP32 durdurma mantığı; ani frende devrilme; sensör kusurları;
LiDAR'ın merdiveni görüp görmediği. Hepsi MuJoCo modelinde, varyant ONERI (öneri firmware + ön omni; bugünkü robot
V0 değil). Bütün tablolar `analiz.py` ile CSV'lerden üretilir (`tablolar.md`); bu dosya özet ve hükümdür.
Tamamlama turunun tabloları `tamamla_analiz.py` ile `tamamlama_tablolar.md`'ye üretilir (CSV: `t_*.csv`).
Tamamlama 2'nin tabloları aynı betikle `tamamlama2_tablolar.md`'ye üretilir (CSV: `t2_*.csv`).

> **Durum (bağımsız hüküm 3, 2026-11-26): onaylı seçim `8WRaD+4AD+2YR40` (SECIM_3A, on dört sensör).** Önceden konan
> ölçütü (0 hakem düşmesi, 0 yanlış durma) taze kümede, yani tohum 211–220 ve hiç koşulmamış geometrilerle sağlayan tek
> düzen bu. Sayılar: hakem 0 / 2742, yanlış durma 0 / 585. **Ama pay dar:** en küçük pay 0,35 cm, 12 koşuda 1 cm'nin
> altında. Aşağıda "Bağımsız hüküm 3". Bu kutunun altındaki önceki durum notu tarih olarak duruyor.
>
> **Önceki durum (bağımsız inceleme 3, 2026-11-26): onaylanmış seçim YOK.** `secim.json`'daki on dört sensörlü
> `8WRD+4AD+2YR40` **ölçütü SAĞLAMAYAN en iyi adaydır**, onaylanmış seçim değildir. Önceden konan ölçüt (uçurum
> koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma) `t2_hukum`'da sağlanmadı: hakem 1 / 3476, fiziksel 0,
> yanlış durma 0 / 540. On sensörlü `6OD+4AD` de kendi hükmünde (`t_hukum`) sağlamadı: hakem 27 / 2872, fiziksel 6. Son
> commit edilen seçim altı sensörlü `4OD+2AD`'dir. Onun sınamasında dar yarık, dar açıklığa geri gitme ve dar açıklık
> yanında dönme yoktu. Üç düzenin tehlike sınıfına göre karşılaştırması ve seçenekler:
> **[`katmanli_oneri.md`](katmanli_oneri.md)**. İnceleme sayıları CSV'den yeniden saydı, hepsi tuttu. Görev listeleri ham
> kayıtla 0 farkla aynı, sızıntı yok. Sınırlama: `t2_hukum`'un 4016 görevinden 2992'si `t_hukum`'la birebir aynı sahne ve
> senaryo (yalnız tohum farklı). Hiç koşulmamış sahne yalnız 9 / 11 / 13 cm yarık (328 koşu).

## Bağımsız hüküm 3 (2026-11-26): güncel hüküm

**Hüküm: yalnız 3A (`8WRaD+4AD+2YR40`, 14 sensör) GEÇTİ. Öbür dört düzen GEÇMEDİ.** Karar kuralı gereği 3A
`secim.json`'a "onaylı seçim" olarak yazıldı. Hükmü, tasarım ajanından ayrı bir ajan koştu ve adayların ayarına dokunmadı.

- **Ön kayıt** (`sonuc/on_kayit_3.md`, 06:27, koşudan önce):
  - Ölçüt önceki iki hükümle aynı: uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma. Izgaradaki
    bütün hızlar sayılır, hatalı koşu geçti sayılmaz.
  - İkincil ölçütler: fiziksel düşme (koşu sürdürülerek) ve en küçük pay.
  - Görev listesinin özeti (sha1) koşudan sonra yeniden hesaplandı ve aynı çıktı: `3e938d1e…`.
- **Taze küme:**
  - Tohum 211–220: 38 CSV'nin ve 35 ham kaydın hiçbirinde yok.
  - 53 yeni sahne (`h3_*`, `sahne.py`'ye yalnız ekleme): hiçbiri önceki kayıtlarda geçmiyor, hiçbirinin geometrisi eski
    bir sahneyle aynı değil. Tek bilinçli istisna `h3_parlak_3/6`: geometrisi düz zemin, yeni olan %3 / %6 dönüşsüz okuma.
  - Yeni sahneler: dar yarık 8,5 / 9,5 / 10,5 / 11,5 / 12,5 / 14,5 / 16 cm; eğik yarık (ekseni 15 / 25 / 35 / 45°
    dönük; hakemde yeni kenar türü `dikr`); merdiven 16x29 / 18x26 / burunlu 17x30; köşe D 1,5 / 0,6 m;
    dikdörtgen kuyu; dar açıklık 0,48–0,85 m (8 yeni genişlik); d 0,33 / 0,38 / 0,43 / 0,48 m'de dönüş; 6° / 9° rampa
    ucu; 13 yeni yanlış alarm sahnesi.
  - Eski 89 sahnenin sözlükleri, XML'leri ve hakem payları değişmedi.
- **Koşu:** `hukum3` 16 635 koşu, 0 hata, 39 dk (6 süreç, yük ≈ 7,5 çekirdek). Beş düzen aynı 3327 taban görevi koşar:
  2742 uçurum ve 585 yanlış alarm. Üç tur da tamamlandı, hiçbir sınıf azaltılmadı. Fiziksel doğrulama: `hukum3_fiz`,
  hakemin düşme saydığı 710 görevin hepsi, koşu sürdürülerek, 0 hata.

| düzen | sensör | hakem düşme (uçurum) | fiziksel düşme | yanlış durma | en küçük pay cm | hüküm |
| --- | --- | --- | --- | --- | --- | --- |
| `4OD+2AD` (6, son commit edilen; ortak K20 + konum tutma koşuluyla) | 6 | **453 / 2742** | 164 | 0 / 585 | −9,5 | GEÇMEDİ |
| `6OD+4AD` (10, SECIM_3) | 10 | **189 / 2742** | 18 | 0 / 585 | −9,3 | GEÇMEDİ |
| `8WRD+4AD+2YR40` (14, önceki secim.json) | 14 | **2 / 2742** | 0 | 0 / 585 | −0,4 | GEÇMEDİ |
| **`8WRaD+4AD+2YR40` (3A)** | 14 | **0 / 2742** | 0 | **0 / 585** | **0,35** | **GEÇTİ** |
| `6OD+4AD` + kurallar (3B) | 10 | **66 / 2742** | 28 | 0 / 585 | −4,5 | GEÇMEDİ |

Bütün sınıfların tablosu: `sonuc/hukum3_tablo.md`, düzen x sınıf, her hücre ölçüldü. Düşmeler sınıfa göre:

- **6 sensör:**
  - dar yarık 238 / 840 (fiziksel 118);
  - eğik yarık 83 / 288 (26);
  - dar açıklık yanında dönüş 109 / 384 (fiziksel 0);
  - dar açıklığa geri 21 / 288 (19);
  - köşe 2 / 108 (1).
- **10 sensör:**
  - dar açıklık yanında dönüş 110 / 384 (fiziksel 0; d 0,33'te 65 / 96, d 0,38'de 45 / 96);
  - dar yarık 68 / 840 (17);
  - eğik yarık 11 / 288 (1).
- **14 sensör (8WRD):** dar yarık 2 / 840, ikisinde de fiziksel 0. Koşular:
  - `h3_yarik_105`, −12°, 0,10 m/s, tetik yok, pay −0,38;
  - `h3_yarik_115`, 12°, 0,25 m/s, köşe sensörü geç, pay −0,11.

  Dondurma 3'te bulunan köşe kırpması mekanizması hiç görülmemiş ±12°'de yineledi.
- **3B:** dar yarık 61 / 840 (27), eğik yarık 5 / 288 (1).
  - Dönüş kuralı dar açıklık yanındaki dönüşü kapattı: 0 / 384, pay 3,8.
  - Dar yarık açık kaldı. Dondurma 3 bunu öngörmüştü. 61 düşmenin 59'unda hiçbir sensör tetiklemedi.
  - Sürünme 585 yanlış alarm koşusunun 265'inde başladı. Durma olmadı.
- **Bütün düzenlerde 0 düşme:** merdiven başı, kuyu, dar açıklığa ileri, geniş kenara geri, geniş kenarda dönüş ve rampa
  ucu.

**3A'nın sınırı (dürüstlük):** 3A ölçütü hakemin kuralıyla geçti, ama pay geniş değil.

- En küçük pay 0,35 cm (`h3_yarik_95`, −7°, 0,10 m/s, köşe sensörü "sapma" ile durdurdu). 12 koşuda pay 1 cm'nin altında.
  Bunların 10'u dar yarıkta, 2'si dar açıklık yanında dönüşte (en küçüğü d 0,38 m'de 0,39 cm).
- Aynı görevlerde 8WRD'nin iki hakem düşmesi var, ±2 cm ile ±2,5 cm arasındaki fark tam bu sınırda.
- Gerçek lastik birkaç mm içeri girer, hakem rijit teker merkezine bakar. Model hatası (sensör konisi, ROI kaybı, montaj)
  bu payı kolayca yiyebilir.
- Bu hüküm, simülasyonda önceden konan ölçütün sağlandığını söyler. Gerçek robotta dar yarıkta güvenlik payı olduğunu
  söylemez.
- Kusur ve duyarlılık ızgaraları (`t2_kusur`, `t2_duyar`) 3A ile koşulmadı. ROI sinyal kaybı, çapraz konuşma ve iki I2C
  hattı modellenmedi. Etek sınırına uzaklık 9 mm (dondurma 3, bölüm 4).

**Ön kayıt kararı (yorum):** 6 sensörlü düzenin kendi tanımında `hukum_kosul` yoktu. Burada ortak koşulla (K20, konum
tutma) ölçüldü. Rampa ucunda 0 / 72 düşmesi bu koşulun sonucudur. Öbür sınıflardaki düşmeler zamanlamadan bağımsız
geometri kaçırmalarıdır.

**Yeniden üretim notu:** `secim.json` değiştiği için `t2_hukum`, `t2_kusur` ve `t2_duyar` görev listeleri bugünkü dosyadan
üretilirse yerleşim adı farklı çıkar (`8WRaD` / `8WRD`; değerlerin geri kalanı aynı). Önceki değerler `hukum3.S14`'te
ve commit 06acd65'te. `t3_a_gel` görev listesi değişmedi (yeniden üretildi, 0 fark).

**Dosya bütünlüğü:**

- Aday kodunun özetleri hükümden sonra da dondurma 3'tekiyle aynı: `sensor.py`, `denetci.py`, `kosu.py`, `deney.py`.
- `sahne.py` yalnız ekleme yapıldı ve ön kayıttaki özetle aynı (c641ad4d…).
- `hukum3.py` ön kayıttan sonra yalnız tablo kodunda değişti: ondalık virgül, ayrıntı tabloları, UTF-8 çıktı. Görev
  listesi özeti aynı. Bağımsız inceleme yalnız 14 sensörlü düzenin etiketini "önceki secim.json" yaptı ve tabloyu yeniden
  üretti (sayılar aynı, görev listesi özeti yine `3e938d1e…`).
- **Bağımsız inceleme (hüküm 3):** sayılar `hukum3.csv` ve `hukum3_fiz` ham kaydından yeniden sayıldı, hepsi tuttu. Görev
  listesi ham kayıtla 0 farkla aynı, beş düzen 3327 taban görevin hepsinde aynı sahne, senaryo ve tohumla koşuldu. Tohum
  211–220 ve `h3_*` adları önceki hiçbir CSV'de ya da ham kayıtta yok. Altı görev aynı tohumla yeniden koşuldu (3A'nın en
  küçük paylı görevi ve hakemin düşme saydığı üç görev dahil), sonuç alanları birebir aynı. Denetçi ve 3B kuralları yalnız
  sensör okumasını ve Pi komutunu görüyor. İki çekince: `h3_kose_150` (D 1,5 m) sensör menzilinin (1,3 m) dışında, bu
  yüzden sensör ve hakem için eski `kose` ile aynı görünür; yalnız açılar yeni. 3B'nin dönüş görevi aynı 9 s'de geri yayla
  en çok ≈ 77° döner (w 0,15 rad/s), öbür düzenler aynı sürede w 1 rad/s ile dönmeye çalışır. 3B'nin dönüşteki
  0 / 384'ü bu yüzden eşit maruziyet değil. İkisi de 3A'nın hükmünü değiştirmez.
- `testler/test_aday3.py`'de hükümden sonra tek bir denetim değişti. Önceki denetim "secim.json değişmedi" diyordu. Yeni
  denetim 3A'yı yalnız `durum` alanı bu hükmü gösteriyorsa kabul ediyor.
- Testler: `ucurum/testler` venv'de 48 / 48, py -3'te 48 (8 atlanan); `kod/testler/kos.py` 78 geçen, 2 atlanan, 0 kalan.

## Tamamlama 2 (2026-11-26, bağımsız incelemenin üç engelleyicisi): önceki hüküm

**Hüküm: GEÇMEDİ, önceden konan ölçüte göre (bir hakem düşmesi).** Ölçüt `t2_hukum` başlamadan `.durum`'a yazıldı ve
ilk hükmünkiyle aynıydı: uçurum koşularında hakem 0 düşme, yanlış alarm koşularında 0 durma. Hakem kuralı (teker merkezi
kenarı geçti, eğim > 15°, z 3 cm düştü) değiştirilmedi.

- Aday `8WRD+4AD+2YR40` (on dört sensör, aşağıda; ölçütü sağlamadığı için onaylanmış seçim değil), `t2_hukum` başlamadan
  donduruldu ve sonra değişmedi. Hüküm tohumları 206–210 hiçbir koşuda kullanılmamıştı, ama geometri ve senaryoların çoğu
  kullanılmıştı (görevlerin 2992 / 4016'sı `t_hukum`'la aynı; aşağıda "Geliştirme / hüküm ayrımı"). `t2_hukum`: 4016
  koşu, 0 hata.
- **3476 uçurum koşusunda hakem 1 düşme saydı**: `yarik_11` (11 cm x 1 m), deliğin robota göre y'si 0,285, açı 10°, 0,25
  m/s, tohum 207 (`t2_hukum-02838`). Teker merkezi yarığın yan kenarını **3 mm** geçti, tetik yoktu. Neden: robot yarığa
  10° ile girerken öndeki izler tekerin 0,139 m önünde. Bu yüzden iz, teker çizgisinden 0,139 x sin 10° ≈ 2,4 cm yana kayar
  ve çift iz sensörlerinin ±2 cm aralığını yer: yarığın kenarı iz konisinin ortasından geçer ve sensör "zemin" der.
  Aynı aşamada `t2_hukum_fiz` (yalnız rapor, hükümden sonra) koşuldu: aynı görev koşu sürdürülünce teker hiç inmiyor (0 mm),
  eğim 0,01°, gövde zemine değmiyor, robot ön iç sensörle duruyor. Aynı durumun 12 görevinde fiziksel düşme 0 / 12.
  Bu fiziksel sonuç hükmü değiştirmez.
- **540 yanlış alarm koşusunda 0 durma** (12 sahne).
- Fiziksel düşme (teker > 20 mm iner ya da eğim > 5°): 0 / 3436. `rampa_8_ucurum` sayılmadı, çünkü orada eğim rampanın
  kendisi (40 koşunun 40'ı > 5°). Gövde-zemin teması 0 / 3476.
- İlk hükümle karşılaştırma (`t_hukum`, `6OD+4AD`, tohum 201–205): hakem 27 / 2872 ve fiziksel 6 düşme vardı. Şimdi hakem
  1 / 3476, fiziksel 0.

**Neden `secim.json` eski değerine döndürülmedi:** eski seçim (`6OD+4AD`, `deney.SECIM_3`) aynı ölçütü 27 hakem
düşmesiyle geçemedi. Ona dönmek ölçütü sağlamaz, yalnız daha kötü bir düzene döner. Hüküm verisiyle yeni bir ayar da
yapılmadı (yapılsaydı o veri artık hüküm sayılamazdı). `secim.json`'daki düzen **ölçütü sağlamayan en iyi aday** olarak
duruyor (dosyada `durum` alanı), onaylanmış seçim değil. Geçme
için ya yeni bir düzeltme, ayar ve hiç kullanılmamış tohumla yeni bir hüküm gerekiyor, ya da ölçütün kendisi açıkça
yeniden tartışılmalı. Bu belge ölçütü değiştirmez.

### Üç engelleyici ve nasıl kapandı

| engelleyici (bağımsız inceleme) | denetim (doğru mu) | ne yapıldı | sonuç |
| --- | --- | --- | --- |
| 1. Ölçüt "0 düşme" `t_hukum`'da sağlanmadı; önerilen düzeltme kodda yok | doğru: `t_hukum.csv` hakem 27 (yarik_14'te 9, d 0,40 dönüşte 18); `t_hukum_fiz` 6 fiziksel | yarık düzeltmesi üç adımda denendi (aşağıda); seçilen çift iz; yeni hüküm tohum 206–210 | yarıkta hakem 1 / 768 (önce 9 / 432); **ölçüt yine sağlanmadı** |
| 2. Hüküm ızgarasında d 0,35 dönüş ve 8–12 cm yarık yok | doğru: `t_hukum`'da dönüş d yalnız 0,40 / 0,50, yarık 14–28 cm | dönüşe yan sensör eklendi; hükümde d 0,35 / 0,40 / 0,45 / 0,50 ve 9 / 11 / 13 cm yarık (yeni genişlikler) | dönüş 0 / 360 (d 0,35 0 / 90); yarık 9: 0 / 108, 11: 1 / 108, 13: 0 / 108 |
| 3. Kusur ve duyarlılık seçilen düzenle koşulmadı | doğru: `t_kusur6`, `t_duyar` yerleşimi `4OD+2AD` | `t2_kusur` (444 koşu), `t2_duyar` (1308 koşu) seçilen düzenle | kusurda kaçırma 0; tekil duyarlılıkta 0,25–0,39 m/s'de düşme yalnız uzun kip 100 ms'de |

### Yarık düzeltmesi (ayar; `t2_yarik_gel`, `t2_yarik_gel2`; tohum 1–2, yarık 8 / 10 / 12 / 15 / 20 cm, 10 y konumu)

| aday | ön düzen | yarıkta hakem düşme (400) | en küçük pay cm | dar açıklık / geniş kenar |
| --- | --- | --- | --- | --- |
| `6OD+4AD` (önceki seçim) | iz ±0,190, koni 27° | 42 | −5,6 | 0 / 60, 0 / 18 |
| `6WD+4AD` (önerilen 1: iz teker ekseninde) | iz ±0,216, 27° | 23 | −3,4 | 0, 0 |
| `6WRD+4AD` (önerilen 1 + 2: + ROI 15°) | iz ±0,216, 15° | 13 | −3,4 | 0, 0 |
| **`8WRD+4AD`** (eklendi) | her teker hizasında iki iz, ±0,196 ve ±0,236, ROI 15° | **0** | 1,2 | 0, 0 |

İncelemenin önerdiği iki düzeltme (iz y ±0,216, ROI 15°) yetmedi. Kalan düşmeler, yarık kenarı teker ekseninin birkaç mm
yanından geçerken oluyor: tek iz o an yarı zemin görüyor ve "zemin" diyor. Tekerin iki yanına ±2 cm ile konan iki dar iz,
kenar nereden geçerse geçsin birini tümüyle yarığın üstünde bırakıyor. Hükümdeki tek düşme, bu aralığın açılı girişte
(10°) yetmediği durum (yukarıda). `8WRD+4AD` sonradan eklendiği için ayrı aşamada (`t2_yarik_gel2`), aynı ızgarayla koşuldu.

### Dar açıklığın yanında yerinde dönüş (ayar; `t2_donus_gel`, `t2_donus_gel2`; acik_40–100, ±1 rad/s, tohum 1–2)

| aday | yan sensör | d 0,35 | d 0,40 | d 0,45 / 0,50 | yanlış durma |
| --- | --- | --- | --- | --- | --- |
| `6WD+4AD` | yok | 31 / 60 (−8,2) | 17 / 60 (−3,3) | 0 | - |
| `+2Y30` | x 0,10, yana (±90°), 30°, koni 27° | 1 / 60 | 10 / 60 (−1,4) | 0 | 0 / 84 |
| `+2Y35` | x 0,09, yana, 35°, 27° | 1 / 60 | 10 / 60 (−1,4) | 0 | 0 / 84 |
| `8WRD+4AD+2YR37` | x 0,10, yana, 37°, ROI 15° | 0 / 60 (1,6) | 1 / 60 (−0,1) | 0 | 0 / 84 |
| **`8WRD+4AD+2YR40`** | x 0,10, yana, 40°, ROI 15° | **0 / 60 (1,6)** | **0 / 60 (2,3)** | 0 | **0 / 84** |

Neden yan sensör: ön omni tekerli robot arka dingil çevresinde döner, ön teker r ≈ 0,42 m çemberde süpürür. Öne bakan
sensörler kenarı ya geç görür ya da dar açıklıkta deliğin dışına düşen bir yerde görür. Yan sensörün izi tekerin dönüş
çemberinin hemen dışında (r ≈ 0,45) ve tekerden ≈ 20° önde. Kenarı tekerle aynı yerde ve ondan önce görür. Geniş koni
(27°) kenarı ancak ≈ 3,5 cm içeri girince görüyor; d 0,40'ta iz kenarı bu kadar geçmiyor, bu yüzden ROI 15° gerekti.
Denenen başka bir aday (`2YK`, ön köşeden geriye-dışa bakan) ışını kendi tekerine çarptığı (9 ışın) için koşulmadı.

**Aday (`secim.json`, `t2_hukum` öncesi donduruldu; hükümden geçmedi, ölçütü sağlamayan en iyi aday):** `8WRD+4AD+2YR40`, on dört sensör: önde köşe ±0,250 (çapraz),
çift iz ±0,196 / ±0,236 (ROI 15°) ve iç ±0,085; arkada köşe (çapraz) ve iç ±0,085; yanda x 0,10, y ±0,250, dışa 40°
(ROI 15°). Hepsi z 120 mm. Eşik, onay, politika, fren, kısa kip zamanlaması, konum tutma ve hız önerisi 0,25 m/s
değişmedi.

### Kusur, seçilen düzenle (`t2_kusur`, tohum 1; görev 3'ün yinelemesi)

- On dört sensörün her biri tek tek donmuş ya da hep dönüşsüz: **kaçırma 0** (ileri 16, yarıkta 2, geri 6, dönüşte
  4 koşu her arıza için). Bütün arızalarda denetçi arızayı fark edip durdurdu (neden "yok"), pay ≥ 4,8 cm.
- Dönüşsüz örnek oranı: %0 ve %5'te kaçırma 0 / 12, yanlış durma 0 / 4. %20 ve %50'de kaçırma 0 / 12, yanlış durma
  4 / 4 (önceki bulguyla aynı: dönüşsüz oranı %20'yi geçen zeminde robot sürülemez).

### Duyarlılık, seçilen düzenle (`t2_duyar`, tohum 1; görev 5–6'nın tekil satırları)

Her koşul `hukum_kosul`'un üstüne eklendi. Değerler ileri + dar açıklık + yarık için en küçük pay (cm) ve düşme / koşu.

| koşul | 0,25 m/s | 0,30 m/s | 0,39 m/s | geri + geniş kenar dönüş | dar açıklık dönüş d 0,35 / 0,40 |
| --- | --- | --- | --- | --- | --- |
| K20 (seçilen kip) | 9,5 | 8,6 | 6,5 | 5,4 | 6,9 |
| uzun kip 33 / 50 ms | 8,3 / 6,8 | 7,1 / 5,5 | 4,5 / 2,2 | 3,9 / 3,0 | 6,2 / 5,3 |
| uzun kip 100 ms | 1,4 | 0,2 | **−5,7 (4 / 28)** | **−1,7 (1 / 5)** | **−0,5 (1 / 4)** |
| gecikme +20 / +50 ms | 9,2 / 8,5 | 8,3 / 7,4 | 6,1 / 5,0 | 5,2 / 4,5 | 6,8 / 6,5 |
| µ 0,5 | 9,5 | 8,6 | 6,5 | 5,1 | 6,7 |
| montaj en kötü / rastgele | 7,9 / 9,2 | 7,1 / 8,6 | 5,0 / 6,5 | 3,9 / 4,5 | 5,5 / 5,9 |
| +5 kg üstte / +10 kg altta | 9,4 / 9,2 | 8,2 / 8,2 | 6,1 / 5,8 | 4,7 / 5,2 | 5,7 / 6,8 |
| gürültü σ 10 mm | 9,5 | 8,6 | 6,5 | 5,4 | 6,9 |

Yanlış durma bütün koşullarda 0 / 16. Eski düzende en kötü tekil pay 0,25 m/s'de 2,6 cm idi (montaj), yeni düzende 7,9 cm.
Bu ölçüm 0,30 m/s'yi de destekliyor (en kötü tekil 7,1, uzun kip 100 ms hariç). **Hız önerisi yine de 0,25 m/s'de
bırakıldı**, çünkü seçim hükümden önce donduruldu ve hüküm geçmedi. Uzun kip 100 ms (seçilmeyen kip) 0,39 m/s'de ve
dönüşte düşüyor.

### Hüküm ızgarası (`t2_hukum`, tohum 206–210; ayrıntı `tamamlama2_tablolar.md` H)

| grup | koşu | hakem düşme | en küçük pay cm (düşmeyen) |
| --- | --- | --- | --- |
| ileri: merdiven_15x28 / 19x25, kuyu, köşe (0,10 / 0,25 / 0,39; tohum 206–210) | 480 | 0 | 2,1 (köşe; başlangıçta teker yan kenara 2,2 cm, yan sensör 0,08 s'de durdurur) |
| geri / dönüş / yay (iki merdiven) | 140 | 0 | 6,7 |
| dar açıklık (8 sahne, tohum 206–208) | 1080 | 0 | 5,5 |
| burunlu merdiven + 12 cm basamak | 250 | 0 | 6,0 |
| iskele_90 | 135 | 0 | 6,6 |
| rampa_8_ucurum | 40 | 0 | 8,3 (0,25) / 4,8 (0,39) |
| **yarık 9 / 11 / 13** (yeni genişlik) + 14 / 17 / 22 / 28 (9 yeni y konumu; yarik_14'te ayrıca eski düşen y 0,23; tohum 206–207) | 768 | **1** (yarik_11) | 0,5 |
| geri, dar açıklık | 81 | 0 | 6,8 |
| **yerinde dönüş, dar açıklık** (acik_45 / 55 / 65 / 75 / 90; d 0,35 / 0,40 / 0,45 / 0,50; tohum 206–208) | 360 | 0 | 0,5 (d 0,40); d 0,35'te 7,6 |
| kötü koşulların birleşimi (+20 ms, montaj en kötü, µ 0,5, +10 kg; 0,25 / 0,30; yarık ve d 0,35 dönüş eklendi) | 142 | 0 | 2,1 (köşe, başlangıç) |
| yanlış alarm (12 sahne) | 540 | 0 durma | |

Toplam 4016 koşu, 0 hata. Düşmeyen koşularda en küçük pay 0,5 cm (yarık ve d 0,40 dönüş). Pay yarıkta ve dönüşte
küçük: ölçütün eşiğindeyiz, payı geniş bir sonuç değil.

**Geliştirme / hüküm ayrımı.** Ayar: `t2_yarik_gel`, `t2_yarik_gel2`, `t2_donus_gel`, `t2_donus_gel2`, `t2_kusur`,
`t2_duyar` (tohum 1–2; yarık 8 / 10 / 12 / 15 / 20 cm, acik_40–100, geliştirme sahneleri). Hüküm: `t2_hukum`, tohum
206–210, yarık genişlikleri 9 / 11 / 13 hiçbir ayarda yok, y konumları yeni, dar açıklıklar sınama sahneleri. Görülmüş
sayılması gerekenler: sınama 2 ve ilk hükmün geometri ızgarası (yeni tohumla yinelendi), `yarik_14` y 0,23 (ilk hükmün
düşmesi; düzeltmeyi o yönlendirdi), yanlış alarm sahnelerinin 7'si (geliştirme sahnesi). `t2_kusur` ve `t2_duyar` seçim
dondurulduktan sonra, hükümden önce koşuldu ve seçimi değiştirmedi.

**Bağımsız inceleme 3 (sayılarla):** `t2_hukum`'un 4016 görevinden **2992'si `t_hukum`'la birebir aynı** (sahne, senaryo,
açı, hız, dönüş hızı, d, yanal), yalnız tohum farklı. Tohum yalnız ±2° açı, yanal ve başlangıç uzaklığı oynamasını,
sensör gürültüsünü ve fazını değiştirir. 2303 görev `sinama2`'yle de aynı. Hiç koşulmamış sahne yalnız
`yarik_9 / 11 / 13` (328 koşu). Yeni görev bileşimleri: yarıkta yeni y'ler (756), dönüşte d 0,35 / 0,45 (252), kötü
birleşimde 16. İlk hükmün düşen 120 görevi (`yarik_14` y 0,23: 12; d 0,40 dönüşü: 108) düzeltmeyi yönlendirdi ve aynen
yinelendi: bu düzen için görülmüş veridir. Yanlış alarm koşularının 315'i, yan sensörlerin ayarlandığı yedi sahnede
(`t2_donus_gel`, `t2_donus_gel2`). Bu yüzden "0 / 540 yanlış durma" ve "dönüş 0 / 360" kısmen görülmüş geometride
ölçüldü. Tohum ayrımı doğru: 206–210 başka hiçbir CSV'de yok.

### Tamamlama 2'nin bedeli ve iyimser varsayımları

- **On dört VL53L1X** (önce on): sensör başına XSHUT, tek I2C hattında 20 ms'de gecikmesiz okuma varsayıldı. 14 x 50 Hz
  okuma ESP32'de büyük olasılıkla iki I2C hattı ister. Çapraz konuşma modellenmedi.
- **ROI 15°** (altı sensörde): yalnız koni daraltıldı. ROI'nin sinyal / menzil kaybı ve gürültü artışı modellenmedi
  (veri sayfası: ROI küçülünce menzil kısalır). Kısa kipte zemin 0,14–0,16 m'de olduğu için büyük olasılıkla yeter, ama
  masada ölçülmeli.
- Yan sensörler etek yan yüzünden 40° dışa bakar: pencere gerekir. İzleri gövde yanından ≈ 9 cm dışarıda. Robot yan
  kenarı bir uçuruma ≈ 9 cm'den yakın sürülürse durur ya da hiç kalkmaz (köşe sahnesinde bazı başlangıçlarda 0,08 s'de
  durdu). Güvenli, ama dar şeritte iş görmeyi kısıtlar: 0,9 m iskelede sorun yok, ≈ 0,70 m'den dar şeritte robot durur.
- Kalibrasyon hep düz zeminde başlangıçta: yan sensörün izi başlangıçta boşluğun üstündeyse yanlış "beklenen" alınır.
  Gerçek robotta kalibrasyon bir kez düz zeminde yapılmalı ve montaj yüksekliğiyle makullük denetimi eklenmeli.
  Modellenmedi.
- Hakem, yarık ve dönüşte pay 0,5 cm'ye kadar iniyor; teker ve gövde rijit. Gerçek lastik birkaç mm içeri girer.

### Tamamlama 2'de atılanlar (≈ 2,5 saat)

- `t2_duyar`: tohum 1; "taban" (ilk iyimser model), U33G, fren 1,5 / 1,0 m/s² satırları yinelenmedi.
- `t2_kusur`: tohum 1 (öncekinde 1–2).
- Dönüş ayarı yalnız ±1 rad/s (0,5 / 0,7 rad/s yinelenmedi; önceki turda dönüş hızının sonucu değiştirmediği ölçülmüştü).
- `t2_hukum`: yarık tohum 206–207, dar açıklık / geri / dönüş tohum 206–208, kare delik yok. `t_hukum_karsi` yine yok.
- Yan sensör adayları `6WD` ön düzeniyle denendi; seçilen ROI'li yan sensörler `8WRD` ile.

### Tamamlama 2'nin sayıları

Ayar: `t2_yarik_gel` 1434, `t2_yarik_gel2` 478, `t2_donus_gel` 978, `t2_donus_gel2` 708, `t2_kusur` 444, `t2_duyar`
1308 (5350 koşu). Hüküm: `t2_hukum` 4016. Yalnız rapor: `t2_hukum_fiz` 12. Toplam 9378 koşu, 0 hata. Bütün düşmeler
CSV'de durur.

İncelemenin "diğer" bulgularından düzeltilenler: `tamamla_analiz.py` başlıkları (tohum 201–205; 4a, 4b, 5–6 tohum 1;
1b "2 hız … sahne başına 56") düzeltildi ve `tamamlama_tablolar.md` yeniden üretildi. `deney._hukum` docstring'i
düzeltildi (201–205 kullanıldı). `secim.json`'un notu yenisiyle değişti; eski seçim `deney.SECIM_3`'te donduruldu.
`gorevler("t_hukum")` ve `t_hukum_fiz` ham kayıtla 0 farkla aynı. `gorsel/demo_pencere.png` on dört sensörle yeniden
çekildi (robot merdiven kenarında durdu, "on_iz_dis_sol, sapma").

## Tamamlama turu (2026-11-26): hüküm (**güncellendi**: güncel hüküm yukarıda, "Tamamlama 2")

Bağımsız inceleme sınama 2'yi "koşullu" geçirdi ve sekiz açık bıraktı (dar delik, geri / dönerek yaklaşma, altı sensörde
kusur, iniş rampası, sensör zamanlaması, duyarlılık, yeni tohumlu hüküm, demo). Hepsi ölçüldü. **Seçim değişti:** altı
sensörlü `4OD+2AD` yarıkta ve geri giderken dar açıklıkta düşüyor; yeni seçim on sensörlü `6OD+4AD`, kısa kip VL53L1X
zamanlaması, konum tutma freni ve **tek hız önerisi 0,25 m/s** (aşağıda). Aşağıdaki "Hüküm (sınama 2)" bölümü olduğu gibi
duruyor; çelişen yerlerine "güncellendi" notu düşüldü.

**Güncellendi (tamamlama 2):** bu hüküm bağımsız incelemede "koşullu" kaldı. Önceden konan ölçüt (0 düşme) sağlanmamıştı;
iki açık ve kusur / duyarlılık yukarıda, "Tamamlama 2"de yeniden ölçüldü.

**Hüküm (tamamlama turu): GEÇMEDİ** (önceden konan "0 hakem düşmesi" ölçütü 27 hakem ve 6 fiziksel düşmeyle sağlanmadı;
bu satır önce yanlışlıkla "koşullu geçer" diyordu, bağımsız inceleme 3 düzeltti). Düzen (`6OD+4AD`, kısa kip, konum tutma,
0,25 m/s) bu hükümden önce hiç kullanılmamış tohumlarla koşuldu: 201–205; dar açıklık, kötü birleşim, yarık ve yeni geri /
dönüş için 201–203. 206–210 o turda ayrıldı, sonra tamamlama 2 hükmünde kullanıldı. Geometri sınama 2'ninki ve yeni
geometriler (`t_hukum`, 3412 koşu, 0 hata). Düzeltme (bağımsız inceleme): "seçimde hiç koşulmamış geometri" yalnız yeni
gruplar için doğru. Sınama 2 geometrileri önceki hükümde kullanılmıştı. Yanlış alarm sahnelerinin 7'si geliştirme
sahnesiydi ve seçimden önce `t_aday_son`'da da koşuldu:

- **2872 uçurum koşusunda hakem 27 düşme saydı; fiziksel düşme 6** (hepsi aynı durum, aşağıda). Sınama 2'nin bütün
  ızgarası (merdiven, kuyu, köşe, geri, dönüş, yay, sekiz dar açıklık), yeni geometriler (`iskele_90`, burunlu merdiven,
  tek 12 cm basamak, 8° iniş rampasının ucunda düşüş) ve kötü koşulların birleşimi (+20 ms gecikme, en kötü montaj, µ 0,5,
  +10 kg; 0,25 ve 0,30 m/s) **0 düşme**. 540 yanlış alarm koşusunda (12 sahne) **0 yanlış durma**.
- Düşmeyen koşularda en küçük pay: 0,25 m/s'de 5,3 cm, 0,30 m/s'de 4,9 cm (kötü birleşim), 0,39 m/s'de 3,5 cm
  (hızlı senaryolar; yerinde dönüşte d 0,40 m'de düşmeyen koşuların en küçük payı 0,3 cm).
- **Açık 1, dar yarık:** 14 cm x 1 m yarık, iç kenarı ön iz sensörünün izinin 3 cm içinde (deliğin y'si 0,23 m):
  sensör konisinin çoğu zemini görür, tetik ön teker yarığa girdikten sonra gelir: 6 / 108 koşuda teker 41–54 mm iner,
  gövde 6–14° eğilip zemine değer, robot durur (devrilmez, ama deliğe oturur). Hız bunu değiştirmiyor (0,10'da da var).
  Geliştirmede aynı kalıntı görülmüştü (`6OD+2AD` 3 / 168). Önerilen (sınanmadı): iz sensörünü teker ekseninin üstüne
  (y ±0,216) almak ya da ROI ile koniyi 15°'ye daraltmak.
- **Açık 2, dar açıklığın yanında yerinde dönüş:** dönme merkezi kenardan 0,40 m'de hakem 18 / 108 düşme sayıyor
  (sahne başına en küçük pay hükümde −1,3 … −1,6 cm, koşu sürdürülünce −1,6 … −2,0 cm); koşu sürdürülünce **fiziksel düşme 0 / 108** (teker merkezi kenarı 2 cm geçer, teker inmez).
  0,50 m'de 0. Geliştirmede 0,35 m'de pay −8 cm idi: **dar açıklığın 0,45 m yakınında yerinde dönme**; dönüş hızı tavanı
  çözmüyor (T2).
- **Seçim hükümden sonra değişmedi** (hüküm verisiyle ayar yapılmadı); `t_hukum_fiz` yalnız rapor içindir.

### T1. Dar delikler (görev 1; `t_delik_tehlike`, `t_delik_boy`, `t_delik_gel`, `t_delik_fiz`; ayar, tohum 1–3)

**Hangi delik tehlikeli (denetçi kapalı, robot deliğin üstünden geçer).** Teker çapı 125 mm, genişliği 58 mm (`lale.xml`; ön
omni küre modeli aynı yarıçap), dingil aralığı 0,37 m, iz ±0,216 m, gövde altı 35 mm.

- Tek teker izinin altındaki **kare delik 4–35 cm: hiçbirinde fiziksel düşme yok** (20 koşu; orta hattakilerle 40): teker merkezi deliğin üstünden
  geçiyor ama teker en çok 0,4 mm iniyor, eğim ≤ 0,09°, robot hep geçiyor. Rijit dört tekerli gövde o an üç tekerle taşınıyor.
  Hakemin "teker merkezi deliğin üstünde = düştü" kuralı bu boyda **fazla kötümser**; o yüzden aşağıda fiziksel sonuç da sayıldı.
- İki iz arasında (orta hatta) 35 cm'ye dek delik hiçbir tekerin altına girmiyor: zararsız (40 koşu, 0 iniş).
- **Tehlike, aynı yandaki iki teker aynı anda boşlukta kalınca başlıyor** (yarık boyu taraması, 120 koşu): boy 20 ve 30 cm'de
  0 / 6 (her genişlik), 40 cm'de 8 cm 1 / 6, 10 cm 5 / 6, 15 ve 20 cm 6 / 6; 50 ve 70 cm'de 10–20 cm genişlikte 6 / 6 (teker
  32–112 mm iner, gövde zemine değer, 70 cm boyda 15–20 cm genişlikte robot 46–56° devrilir; 12 koşudan 11'i, birinde eğim 10°). 1 m yarıkta 4 ve 6 cm genişlik
  köprülenir (teker 58 mm), 8 cm sınırda (2 koşudan 1'i), 10 cm ve üstü hep düşer.
- **Hüküm:** gerçekten tehlikeli en küçük delik, bir teker izinin altında **≈ 8–10 cm genişlik x ≥ 40 cm boy** (gidiş yönünde
  dingil aralığından uzun) yarık / şerit; daha kısa ya da teker genişliğinden dar delik bu modelde zararsız. Varsayım: rijit
  gövde, süspansiyon yok, teker lastiği rijit (gerçek robotta teker deliğe biraz daha girer).

**Algılama ve durma** (1 m yarık 10 / 15 / 20 cm + 35 cm kare; deliğin robota göre y'si 0 … 0,30, açı 0 / 15, 0,25 / 0,39 m/s;
aday başına 224 koşu; "fiziksel" = koşu hakemden sonra da sürer, teker > 20 mm iner ya da eğim > 5°):

| aday | yarıkta hakem düşmesi (168) | yarıkta fiziksel düşme (168) | 35 cm kare | dar açıklık 0,40 / 0,50 (120) | geniş kenar (18) |
| --- | --- | --- | --- | --- | --- |
| `4OD+2AD` (sınama 2 seçimi) | 54 | **38** | 0 / 56 | 0 (pay ≥ 1,6) | 0 |
| `4TD+2AD` (iç sensör ±0,15) | 29 | - | 0 / 56 | 0 (3,8) | 0 |
| `6OD+2AD` (+ iz sensörü ±0,19) | 7 | **3** | 0 / 56 | 0 (5,4) | 0 |

`4OD+2AD`'nin kaçırdığı, deliği teker hizasında (y ≈ 0,19–0,25) taşıyan yarık: iç iz (±0,085) ve köşe izi (≈ ±0,30)
arasındaki 21 cm'lik boşluk. Teker hizasına düz öne bakan iki sensör (`6OD`) bunu kapatıyor; geride kalan 3 fiziksel düşme
10 ve 15 cm yarıkta, 15° açıyla girişte. **Seçim:** ön düzen `6OD` (altı ön sensör). Kalan risk: 10 cm civarı yarıkta seyrek
kaçırma (geliştirmede 3 / 168).

### T2. Açıklığa geri giderek ve yerinde dönerek yaklaşma (görev 2; `t_yaklasma_gel`, `t_donus_w`, `t_aday_son`)

- **Geri** (0,40–1,00 m açıklık + iki geniş kenar, açı 0 / 30, 0,10 / 0,25 m/s, 5 yanal kayma, tohum 1–2; aday başına 216):
  `4OD+2AD` **24 / 216 düştü** (0,40 m 10 / 40, 0,50 m 10 / 40, 0,60 m 4 / 40; pay −9,2 cm): arkada iç sensör yok, arka köşe
  izleri (±0,30) açıklığın yan zeminine düşüyor. Arkaya iki iç sensör (`4AD`, ±0,085, düz geriye) ile **0 / 216, pay ≥ 8,6 cm**.
  **Seçim:** arka düzen `4AD`.
- **Yerinde dönüş** (robot açıklığa paralel, dönme merkezi kenardan d, ±1 rad/s): geniş kenarda 0 / 16, ama **dar açıklığın
  yanında d = 0,40 m'de düşüyor**: `4OD+2AD` ve `4OD+4AD` 17 / 136 (hepsi d 0,40; 0,50'de 0). Dönüş hızını düşürmek çözmüyor
  (0,5 ve 0,7 rad/s: d 0,35'te 29 / 60, 0,40'ta 16 / 60, 0,50'de 0 / 60); seçilen `6OD+4AD` ile de aynı (d 0,35 31 / 60,
  0,40 17 / 60, 0,50 0 / 60). Neden: ön omni tekerle yerinde dönüş arka dingil çevresinde olur, ön tekerler ≈ 0,43 m yarıçapla
  yana doğru süpürür; sensörler öne / öne-dışa bakar, açıklığın yan kenarı ön tekerin yanından gelir ve geç görülür.
  **Çözülmedi:** dar bir açıklığın 0,45 m yakınında yerinde dönüş bu düzenle güvensiz. Önerilen (sınanmadı): ön tekerlerin
  yanına yana bakan (yon ±90°) birer sensör ya da Pi'de "yerinde dönmeden önce 0,1 m geri / ileri" gibi bir kural değil,
  donanım çözümü; yalnız dönüş hızı tavanı işe yaramıyor.

### T3. Altı sensörle kusur taraması (görev 3; `t_kusur6`, `4OD+2AD`, tohum 1–2; yeni iz sensörleri `t_aday_son`)

| arıza | uçurumda düşme (kaçırma) | sonuç |
| --- | --- | --- |
| arızasız (ileri, 4 sahne x 2 açı x 2 hız) | 0 / 32 | 8 sapma, 24 dönüşsüz tetik (3 m boşluk menzil dışı) |
| her ön sensör tek tek donmuş ya da hep menzil dışı (8 arıza) | 0 / 32 her biri | hepsinde denetçi arızayı fark edip durdu (pay ≥ 34 cm) |
| her arka sensör tek tek ölü (geri, 4 arıza) | 0 / 12 her biri | fark edip durdu |
| arızasız geri (`4OD+2AD`) | **2 / 12** | dar açıklıkta arka iç boşluğu (T2; `4AD` ile kapandı) |
| yeni iz sensörleri (`6OD+4AD`) donmuş / hep dönüşsüz | 0 / 24 | 24 / 24 fark edip durdu |

Dönüşsüz örnek oranı (bütün sensörler; 3 uçurum sahnesi + düz zemin 4 m, politika `yavasla`): %0 ve %5'te kaçırma 0 / 24,
yanlış durma 0 / 8; **%20 ve %50'de kaçırma 0 / 24, yanlış durma 8 / 8** (robot yavaşlar, sonra durur). Ölü sensör robotu
durdurur (güvenli ama iş görmez); dönüşsüz oranı %20'yi geçen zeminde robot sürülemez (ilk sınamadaki bulguyla aynı).

### T4. İniş rampası (görev 4; `t_rampa_fren`, `t_rampa_ucurum`; tohum 1)

**Güvenli fren ivmesi, ölçülerek** (10° iniş, 4 m rampa, zorla tetik; frenden önce arka aks 71 N; el hesabı devrilme sınırı
1,93 m/s²):

| fren a (m/s²) | arka aks en az (0,10 / 0,20 / 0,25 / 0,39 m/s) | arka aks 0 N süresi | öne yatma tepe | durma yolu 0,25 / 0,39 (0,6 s penceresi) |
| --- | --- | --- | --- | --- |
| 0,5 | 45 / 43 / 46 / 44 N | 0 | ≤ 0,001° | 6,7 / ≥ 14,3 cm (0,6 s'de duramıyor) |
| 0,75 | 0 N (0,10'da bile) | 10–140 ms | ≤ 0,001° | 5,3 / 11,0 |
| 1,0 | 41 / 0 / 0 / 0 | 0–200 ms | ≤ 0,002° | 4,6 / 10,0 |
| 1,5 | 0 | 10–220 ms | ≤ 0,005° | 3,5 / 8,1 |
| 2,0 (seçilen) | 43 / 0 / 0 / 0 | 0–290 ms | ≤ 0,005° (mekanikte 0,017°) | 3,0 / 7,4 |

Gövde hiçbir ivmede dönmüyor (öne yatma ≤ 0,017°): **devrilme payı her ivmede var**. Arka aksın her hızda hiç yük kaybetmediği tek
ivme **0,5 m/s²**; 0,75 ve üstünde arka tekerler 10–290 ms yükünü kaybediyor (0,10 m/s'de 1,0 ve 2,0 m/s² hariç) (kısa sıçrama; frenleme o an yalnız ön omni
tekerlerde, yönsel kararlılık riski). 0,5 m/s² durma yolunu 2,2 kat uzatır ve düz zemindeki uçurum payını yer (0,39 m/s'de
≈ +10 cm). **Karar:** fren 2,0 m/s² kalır (düzde ölçülmüş en iyi pay; inişte devrilme yok), ama inişte hız ≤ 0,25 m/s
(arka aks 0 N süresi 0,25'te ≤ 110 ms, 0,39'da 290 ms). Firmware eğimi bilmediği (IMU yok) için tek ivme her yerde geçerli.

**Tutma freni** (varsayım: **motor konum tutma**, firmware'de enkoderle, ek donanım yok; karşılaştırma: yay baskılı mekanik
fren 2 N·m / teker). Kısa devre freni sıfır hızda tutmuyor: tutmasız robot frenden sonra **101 mm/s ile kayıyor** (4,5 s'de
0,46–0,49 m). Konum tutma ile tetikten 2 s sonrasından koşu sonuna (≈ 4–6 s) kayma **0,03–1,0 mm**, son 1 s hız 0,16–0,32
mm/s (mekanik fren 1,1–1,25 mm, 0,27 mm/s: ikisi de MuJoCo eklem kısıtının sızma düzeyi): **kayma bitiyor.** Bedel: 10°'de
teker başı ≈ 0,70 N·m tutma torku, motorun sürekli torkunun (0,618, TAHMİN) üstünde: uzun bekleyişte ısınır; kalıcı park için
mekanik fren ya da sonsuz vida gerekir.

**İnişte güvenli hız, kanıt** (`rampa_10_ucurum`: 10° x 2 m iniş rampasının ucunda 3 m düşüş; seçilen sensörlerle gerçek tetik;
açı 0 / 20; düşme / koşu, en küçük pay):

| fren a | tutma | 0,10 | 0,15 | 0,20 | 0,25 | 0,39 m/s |
| --- | --- | --- | --- | --- | --- | --- |
| 1,0 / 1,5 / 2,0 | yok | 2 / 2 her hızda | 2 / 2 | 2 / 2 | 2 / 2 | 2 / 2 (hepsi kayıp düşüyor) |
| 1,0 | konum | 0 (9,1) | 0 (8,1) | 0 (6,6) | 0 (4,5) | **1 / 2** (−0,7) |
| 1,5 | konum | 0 (9,2) | 0 (8,3) | 0 (7,1) | 0 (5,0) | 0 (0,7) |
| 2,0 | konum | 0 (9,3) | 0 (8,5) | 0 (7,2) | 0 (5,4) | 0 (1,3) |

Tutma freni olmadan rampa ucundaki uçurumda **her hızda düşüyor** (30 / 30). Konum tutma + 2,0 m/s² ile 0,25 m/s'de pay
5,4 cm, 0,39'da 1,3 cm. **İnişte önerilen hız 0,25 m/s** (genel öneriyle aynı; hüküm `rampa_8_ucurum`, aşağıda).

### T5. Sensör zamanlaması (görev 5; `t_duyar` zamanlama kipleri)

**Üreticinin veri sayfasından doğrulandı** (ST DS12385, Rev 8, Ağustos 2024): 3.5.2 "timing budget 20 ms … 1000 ms; 20 ms
en küçük bütçe ve **yalnız kısa mesafe kipinde**; 33 ms bütün kiplerde çalışan en küçük bütçe; 140 ms uzun kipte 4 m'ye
(karanlıkta beyaz hedef) ulaştıran bütçe". Tablo 5 (TB 100 ms, %88 beyaz hedef): en büyük menzil karanlıkta / güçlü ortam
ışığında kısa 136 / 135 cm, orta 290 / 76 cm, uzun 360 / 73 cm; Tablo 19: kısa kip 130 cm (ortam ışığında da). Ön sayfa:
"50 Hz'e dek ölçüm sıklığı", koni 27° (ROI ile 15°), en kısa menzil 4 cm, menzil hatası ±20 mm (Tablo 17). Sürekli kipte
ölçüm aralığı (inter-measurement period) ayrıca ayarlanır (3.4). **İlk modelin "50 Hz + 4 m" birleşimi veri sayfasıyla
çelişiyordu** (50 Hz yalnız kısa kipte, 4 m yalnız uzun kipte ve 140 ms bütçeyle); SONUC'un eski "uzun kip en az ≈ 33 ms"
notu doğru.

Modellenen kipler (sensör örneği alınır, bütçe sonunda kullanılır; geliştirme sahneleri, tohum 1; en küçük pay cm, düşme):

| kip | 0,25 m/s | 0,30 m/s | 0,39 m/s | geri + dönüş |
| --- | --- | --- | --- | --- |
| ilk model (50 Hz, 4 m; iyimser) | 4,0 | 3,2 | 1,6 | 5,4 |
| **K20: kısa kip, 20 ms, 1,3 m (seçilen)** | 4,0 | 3,2 | 1,6 | 5,4 |
| U33: uzun kip, 33 ms (≈ 30 Hz), 3,6 m | 3,4 | 2,5 | **0,0** | 3,9 |
| U33G: uzun kip 33 ms, güçlü ortam ışığı (0,73 m) | 3,4 | 2,5 | 0,0 | 3,9 |
| U50: uzun kip, 50 ms (20 Hz) | 2,1 | 0,6 | **−0,2 (1 / 24 düştü)** | 3,0 |
| U100: uzun kip, 100 ms (10 Hz) | **−0,7 (2 / 24)** | −3,7 (2 / 24) | −6,8 (13 / 24) | −1,8 (2 / 5) |

Kısa kip ilk modelle aynı payı veriyor: zemin 139 mm'de, 1,3 m menzil basamağı görmeye yetiyor; 1,3 m'den derin boşluk
"dönüş yok" verir, `yavasla` politikası ilk dönüşsüz örnekte hızı 0,10'a indirir ve 5 dönüşsüzde durdurur. Uzun kip
yavaşladıkça pay hızla eriyor. **Öneri: kısa kip, 20 ms bütçe, 20 ms aralık** (ortam ışığına da en dayanıklı kip; Tablo 5).
Yanlış durma bütün kiplerde 0 / 16.

### T6. Duyarlılık ve tek hız önerisi (görev 6; `t_duyar`, geliştirme sahneleri: geniş kenar 0 / 30 / 60° + 0,40–0,60 m açıklık, tohum 1)

| koşul | 0,25 m/s | 0,30 m/s | 0,39 m/s |
| --- | --- | --- | --- |
| taban (ilk model) | 4,0 | 3,2 | 1,6 |
| denetim gecikmesi +20 ms | 3,9 | 3,2 | 1,6 |
| denetim gecikmesi +50 ms | 3,7 | 3,2 | 1,5 |
| düşük sürtünme µ 0,5 | 4,0 | 3,2 | 1,6 |
| montaj, sistematik en kötü (z −5 mm, x 5 mm içeri, eğim −3°, köşe yönü −3°) | **2,6** | **2,1** | **0,1** |
| montaj, rastgele ±5 mm / ±3° | 4,0 | 3,2 | 1,6 |
| yük +5 kg tepside (z 0,9 m) | 3,9 | 3,2 | 1,6 |
| yük +10 kg altta | 3,9 | 2,5 | 0,9 |
| sensör gürültüsü σ 10 mm (veri sayfası ±20 mm) | 4,0 | 3,2 | 1,6 |
| fren 1,5 / 1,0 m/s² | 4,0 / 3,9 | 3,2 / 2,9 | 1,2 / 0,5 |
| (T5) uzun kip 33 / 50 ms | 3,4 / 2,1 | 2,5 / 0,6 | 0,0 / −0,2 |

Hiçbir tekil koşulda 0,25 ve 0,30 m/s'de düşme yok; 0,39 m/s'de pay montaj toleransında 0,1 cm'ye, uzun kipte 0'ın altına
iniyor. Yanlış durma bütün koşullarda 0 / 16. (Gecikmenin küçük etkisi: en küçük pay çoğu koşulda tetiğin örnek fazına bağlı
dar açıklık koşusundan geliyor; +50 ms 0,39 m/s'de ≈ 2 cm ek yol demek, en kötü koşunun payı yine 1,5 cm.)

**Güncellendi (tamamlama 2):** bu tablo eski `4OD+2AD` düzenine ait. Seçilen on dört sensörlü düzende tekil en kötü pay
0,25 m/s'de 7,9 cm (montaj; "Tamamlama 2", `t2_duyar`).

**Tek hız önerisi: 0,25 m/s** (gerçek robotta ilk denemeler için de, nihai seyir için de; düz, iniş ve geri aynı).
Gerekçe: tekil en kötü koşulda (montaj) pay 2,6 cm, kötü durumların birleşiminde hükümde ölçüldü (aşağıda); 0,30 m/s'de
tekil en kötü 2,1 cm ve 10 kg yükte 2,5, 0,39 m/s'de pay yok (0,1 / 0,0 / −0,2). 0,39 m/s firmware'in teker tavanıdır, güvenli
hız değildir.

### T7. Hüküm koşuları (görev 7; `t_hukum`, tohum 201–205, o ana dek hiç kullanılmamıştı; 206–210 ayrıldı, sonra tamamlama 2 hükmünde kullanıldı; `t_hukum_fiz` hükümden sonra, yalnız rapor)

Seçim (`secim.json`, `hukum_kosul`) `t_aday_son` bittikten sonra, `t_hukum` başlamadan yazıldı; hükümden sonra
değiştirilmedi. Sahne / senaryo grupları (düşme / koşu, en küçük pay cm; ayrıntı `tamamlama_tablolar.md` bölüm 7):

| grup | sahneler | koşu | hakem düşme | fiziksel | en küçük pay |
| --- | --- | --- | --- | --- | --- |
| ileri (0,10 / 0,25 / 0,39; tohum 201–205) | merdiven_15x28, merdiven_19x25, kuyu, kose | 480 | 0 | 0 | 4,8 |
| geri / dönüş / yay | iki merdiven | 140 | 0 | 0 | 4,5 |
| dar açıklık (tohum 201–203) | acik_45 … acik_90, sığ, iki dar merdiven | 1080 | 0 | 0 | 4,8 |
| kötü koşulların birleşimi (0,25 / 0,30) | merdiven_15x28, kuyu, kose, acik_45, sığ, dar merdiven 60 | 126 | 0 | 0 | 4,9 (0,30) / 6,3 (0,25) |
| **yeni** ileri / geri | merdiven_burun_18x28, basamak_12 | 250 | 0 | 0 | 4,8 |
| **yeni** iskele (0,9 m şerit, üç yan boşluk) | iskele_90 | 135 | 0 | 0 | 6,2 |
| **yeni** iniş rampası ucunda düşüş | rampa_8_ucurum (0,10 / 0,20 / 0,25 / 0,39) | 40 | 0 | 0 | 3,5 (0,39) / 7,6 (0,25) |
| **yeni** dar yarık (y 0,05 … 0,27) | yarik_14 / 17 / 22 / 28 | 432 | **9** (yarik_14) | **6** (yarik_14, y 0,23) | 3,6 (düşmeyen) |
| **yeni** geri, dar açıklık | acik_45 / 55 / 75 | 81 | 0 | 0 | 7,5 |
| **yeni** yerinde dönüş, dar açıklık | acik_45 / 55 / 75, d 0,40 / 0,50 | 108 | **18** (hepsi d 0,40) | 0 | −1,6 (koşu sürünce −2,0) |
| yanlış alarm (12 sahne, 5'i sınama 2'den) | derz, eşik, halı, koyu bant, rampalar, düz | 540 | 0 yanlış durma | | |

Toplam 3412 koşu, 0 hata. Geliştirme ile ayrım: geliştirme tohum 1–3 ve `t_*` geliştirme sahneleri; yeni geometrilerden
yarık türü (10 / 15 / 20 cm, burada 14 / 17 / 22 / 28 cm ve başka y konumları) ve rampa ucu türü (`rampa_10_ucurum`,
burada 8°) geliştirmede vardı; hükümde 8–12 cm yarık ve yerinde dönüşte d 0,35 m yok. `t_hukum_karsi`
(iyimser zamanlamayla karşılaştırma) süre için koşulmadı.

### T8. Gösterim (görev 8)

`kod\ucurum.bat` (merdiven_17x30, 0,25 m/s) `6OD+4AD` seçimiyle bir kez açıldı; `demo.py` artık `hukum_kosul`'u da uygular
(kısa kip zamanlaması, 1,3 m menzil, konum tutma). Robot merdiven kenarında durdu (pencere metni "UCURUM: DURDU (on_ic_sag,
sapma, fren rampa)"); görüntü `../gorsel/demo_pencere.png`, eski dört sensörlü görüntünün yerine. Pencere kapatıldı.

### Tamamlama turunda atılanlar (süre ≈ 2,5 saat; derinlik değil ızgara küçültüldü)

- `t_delik_gel`: 0,10 m/s atıldı, tohum 1–2; kare delik yalnız 35 cm (4–30 cm fiziksel zararsız çıktı); `t_delik_tehlike`
  tohum 1; yarık boyu yalnız açı 0 (10°'de robot yarığın yanından kayıyordu, tasarım hatası düzeltildi).
- `t_kusur6`, `t_rampa_*`, `t_duyar`: tohum 1 (kusurda 2 de var); duyarlılık her koşulda 24 + 5 + 16 koşu.
- Yük değişimi iki noktada (+5 kg tepside, +10 kg altta); ±3° montaj yalnız sistematik en kötü ve tek rastgele örnek.
- `t_donus_w` yalnız `4OD+4AD` ile (ön düzenden bağımsız çıktı: `6OD+4AD` aynı sonucu verdi).
- `t_kusur6` ve `t_duyar` `4OD+2AD` ile koşuldu (seçim o an buydu); yeni iz sensörlerinin arızası `t_aday_son`'da, seçilen
  düzenin zamanlaması ve kötü birleşimi hükümde ölçüldü. Duyarlılığın tekil satırları seçilen düzenle yinelenmedi.
- Hükümde kare delik ve `t_hukum_karsi` yok; yeni geri / dönüş tohum 201–203.
- Mekanik tutma freni yalnız `t_rampa_fren`'de; rampa ucu düşüşü yalnız konum tutmayla.

### Tamamlama turunun iyimser varsayımları

- Tutma freni varsayım: firmware enkoder konum tutması (kp 40, ki 100), motor sürücüsü sıfır hızda tork verebiliyor; 10°'de
  gereken 0,70 N·m sürekli torkun (TAHMİN 0,618) üstünde, ısınma modellenmedi.
- Kısa kip menzili 1,3 m sabit (veri sayfası: güçlü ortam ışığında da 135 cm); gerçek histogram, eğik yüzey, çapraz konuşma
  (on sensör, sensör başına XSHUT) yok. 20 ms bütçe + 20 ms aralık on sensörde I2C üzerinde gecikmesiz okunur varsayıldı.
- Teker rijit, gövde rijit, süspansiyon yok: yarık tehlike boyu (≈ 8–10 cm x 40 cm) gerçek lastikte biraz daha küçük olabilir.
- Delik ve yarık kenarları keskin, düz; yük değişimi atalet için kaba paralel eksen terimi.
- Hakemin teker merkezi kuralı küçük deliklerde kötümser (kare delik), bu yüzden fiziksel sonuç ayrıca raporlandı; fiziksel
  ölçüt (teker > 20 mm iner ya da eğim > 5°) VARSAYIM.

### Tamamlama turunun sayıları

Geliştirme / ayar: `t_delik_tehlike` 80, `t_delik_boy` 120, `t_delik_gel` 1086, `t_delik_fiz` 336, `t_yaklasma_gel` 704,
`t_donus_w` 360, `t_kusur6` 476, `t_rampa_fren` 96, `t_rampa_ucurum` 60, `t_duyar` 1488, `t_aday_son` 423 (5229 koşu).
Hüküm: `t_hukum` 3412, `t_hukum_fiz` 216. Toplam 8857 koşu, 0 hata. Bütün düşmeler CSV'de durur.

## Hüküm (sınama 2; **güncellendi**: güncel hüküm yukarıda, "Tamamlama turu")

**Önerilen düzen (dar açıklık düzeltmesinden sonra), sınamadan geçti:** altı sensör: dört köşe (eğim düzlemi çapraz
dışa) + önde iki iç sensör (düz öne). İlk hükümdeki dört köşe düzeni (`2KD+2AD`) **robottan dar açıklıkta düşüyor**;
bağımsız denetimin bulgusu doğrulandı (aşağıda, "Dar açıklık").

| | Değer (robot çerçevesi: gövde merkezi, +x ileri, +y sol) |
| --- | --- |
| Sensör | **6 adet** VL53L1X türü (koni 27°), 50 Hz (`4OD+2AD`) |
| Yer | köşeler: ön sol (+255, +250) mm, ön sağ (+255, −250), arka sol (−255, +250), arka sağ (−255, −250); **ön iç: (+255, +85) ve (+255, −85)**; hepsi yerden 120 mm (köşelerde etek penceresi) |
| Eğim | dikeyden 30°. Köşeler: önde yön ±45° (öne-dışa), arkada ±135° (geriye-dışa), zemin izi köşeden ≈ 49 mm ileri + 49 mm dışarı. Ön iç sensörler: düz öne (yön 0), zemin izi (+324, ±85) mm. Ön izler ön teker temas noktasının ≈ 120–140 mm önünde |
| Eşik | açılışta ölçülen zemin mesafesinden (≈ 139 mm) **+100 mm** fazlası, **art arda 3 örnek** (sensör başına) |
| Dönüşsüz örnek | `yavasla`: 0,5 s hız sınırı 0,10 m/s; art arda 5 dönüşsüz örnek = dur (bkz. Sensör kusurları) |
| Döngü | ESP32 100 Hz (10 ms; tetik → motor komutu aynı dilimde) |
| Fren | etkin fren: teker hedefi 2,0 m/s² rampayla 0'a, PI izler, sonra kısa devre freni. Yalnız motor kesme YETMEZ |
| Güvenli en yüksek hız | 0,39 m/s (ölçülen tavan); sınama 2'de en küçük pay 3,0 cm (dar açıklık), geniş kenarda 4,2 cm. **Güncellendi:** 0,39 m/s güvenli hız değil, teker tavanı; tek öneri **0,25 m/s** (ilk deneme ve nihai; "Tamamlama turu", T6) |

**Sınama 2** (`sinama2.csv`; seçim `dar_gelistirme`'den, sınama koşulmadan önce yapıldı; tohum 101–110, politika `yavasla`
baştan): ilk sınamanın bütün ızgarası (15x28 ve 19x25 cm merdiven, kuyu, sahanlık köşesi; açılar 10 / 22 / 37 / 52 / 68 /
85°; geri, yerinde dönüş, yay) + geliştirmede hiç koşulmamış (sonra `t_hukum` ve `t2_hukum`'da yeniden kullanılan) **8 dar açıklık sahnesi** (0,45 / 0,55 / 0,65 / 0,75 / 0,90 m
genişlik, 0,6 m genişlikte 0,4 m sığ açıklık, 0,6 ve 0,8 m genişlikte dar merdiven; yeni yanal kaymalar −0,15 … +0,25 m;
açı 0 / 10 / 30°) + **5 yeni yanlış alarm sahnesi**: **2900 uçurum koşusunda 0 düşme**, 540 yanlış alarm koşusunda 0
yanlış durma, toplam 3440 koşu, 0 hata. En küçük pay: dar açıklıkta 3,0 cm (0,39 m/s; sığ açıklık ve 0,6 m dar merdiven,
yanal −0,15 m), geniş kenarda ileri 4,2 cm (köşe, 37°) / düz kenar 4,5 cm, geri 6,8 cm, yerinde dönüş 4,4 cm, yay 8,5 cm.

İlk sınama (`sinama.csv` + `sinama_y.csv`, 2210 koşu, eski 4 sensörlü seçim) geniş kenarlarda 0 düşme verdi; o sonuç yerinde
duruyor ama dar açıklığı kapsamadığı için hükmü taşımıyor.

Sadece ileri giden ve **geri gitmesi firmware'de yasak** bir robot için arka iki sensör çıkarılabilir (`4OD`, dört ön
sensör); geri giderken arka sensörsüz her koşu düştü (geliştirmede 144 / 144).

**Dar açıklık (bağımsız denetimin engelleyici bulgusu; `dar_gelistirme.csv`, `sinama2*.csv`).** Bulgu doğru: köşe
sensörlerinin zemin izi y ≈ ±0,30 m'de, teker merkezleri ±0,216 m'de. Robot dar bir açıklığa ortadan girerse iki köşe izi
de açıklığın yan zeminine ya da yan duvarına düşer (çapraz dışa bakan ışın yan duvarı yakın görür, okuma eşiği aşmaz),
teker boşluğa iner. Geliştirmede (tohum 1–2, 6 genişlik 0,40–1,00 m, 3 m derin, 5 yanal kayma, açı 0 / 20 / 40°, üç hız;
aday başına 540 koşu):

| aday | 0,40 m | 0,50 | 0,60 | 0,70 | 0,80 | 1,00 | toplam düştü | en küçük pay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2KD+2AD` (ilk seçim, 4 sensör) | 21 / 90 | 19 / 90 | 6 / 90 | 3 / 90 | 0 / 90 | 0 / 90 | **49 / 540** | −13,2 cm |
| `3KOD+2AD` (+ ön orta, 5 sensör) | 2 / 90 | 0 | 0 | 0 | 0 | 0 | **2 / 540** | −2,7 cm |
| `4OD+2AD` (+ ön iç ±85 mm, 6 sensör) | 0 / 90 | 0 | 0 | 0 | 0 | 0 | **0 / 540** | +1,6 cm |

`3KOD+2AD`'nin iki düşmesi 0,40 m açıklık, 0,39 m/s, 20°, yanal −0,20 m (iki tohum da): orta iz açıklığın kenarına düşer,
geç tetikler. Seçim kuralı (her geliştirme senaryosunda 0 düşme, sonra en büyük en küçük pay) `4OD+2AD`'yi seçer. Ek iki
sensör geniş kenar ve yanlış alarm sonucunu bozmuyor (geliştirme sahneleri, `yavasla`): ileri 0 / 36 (pay 5,7 cm; eski 3,4),
geri 0 / 6 (7,0), yerinde dönüş 0 / 16 (5,2), yay 0 / 2 (6,5), yanlış durma 0 / 84. Ön iç sensörlerden biri ölüyse (donmuş
ya da hep dönüşsüz) denetçi onu fark edip durduruyor (16 / 16 koşu tetik, 0 düşme).

Sınamada seçilmeyen iki aday da aynı dar açıklık ızgarasında koşuldu (`sinama2_karsi.csv`, yalnız rapor, seçime girmedi):
bkz. 7. bölüm.

**Sınırlar (önemli):** (1) Sınanan en dar açıklık 0,40 m (geliştirme) / 0,45 m (sınama). Ön izler arası boşluk (iç iz
±0,085 m ile köşe izi ±0,30 m arası) ≈ 0,21 m: bu aralıkta, teker hizasında duran ≈ 0,2 m'den dar bir delik (ızgara,
kapak boşluğu) geometrik olarak hiçbir izin altına girmeyebilir; sınanmadı. (2) Açıklıklar 2 m boyunda dikdörtgen; yuvarlak
ya da eğik kenarlı açıklık, basamak burnu, korkuluk dikmesi yok.

**Öbür sınırlar:** eşik 100 mm, 30° eğik ışında ≈ 87 mm'den sığ düşüşü görmez (tek basamaklı kaldırım 5–8 cm
yakalanmaz). Daha düşük eşik 10° iniş rampasına çapraz girişte robotu durduruyor (aşağıda). Kısa devre freni sıfır
hızda tork vermediği için **10° inişte robot tam durmuyor: frenden sonra ≈ 0,10 m/s ile kaymaya devam ediyor** (modelde
her fren kipinde; `durma.csv`'de inişte hiçbir koşu 0,005 m/s altına inmedi); rampa dibinde uçurum varsa bu düzen
yetmez, tutma freni gerekir.

**Bağımsız denetimin "sınanmamış geometri" bulgusu kapandı:** dar açıklık sahnesi (`sahne.acik`, hakemde dikdörtgen delik
payı) eklendi, adaylar geliştirme tohumlarıyla karşılaştırıldı, seçim değişti (`2KD+2AD` → `4OD+2AD`) ve sınama yeni
tohum / sahnelerle yeniden koşuldu (yukarıda). Denetçinin kısa denemesi (0,45–0,70 m'de `2KD+2AD` düşer, ön ortalı düzen
durur) bu ızgarada yinelendi.

## 1. Durma mesafesi (düz zemin, tetik zorla verildi; `durma.csv`, iki tohum, deterministik)

| fren | 0,10 m/s | 0,25 m/s | 0,39 m/s | 0,39'da tepe yavaşlama | 0,39'da arka aks en az |
| --- | --- | --- | --- | --- | --- |
| motor kesme (EN LOW, boşta) | 1,4 cm | 9,2 cm | 22,3 cm (1,13 s) | 0,35 m/s² | 123 N |
| kısa devre freni (EN HIGH, PWM 0) | 0,5 | 1,7 | 3,3 | 3,0 | 0 N (60 ms) |
| rampa 1,0 m/s² | 0,7 | 3,3 | 7,7 | 1,3 | 88 N |
| rampa 1,5 | 0,6 | 2,4 | 5,3 | 1,8 | 68 N |
| rampa 2,0 | 0,6 | 2,0 | 4,2 | 2,3 | 46 N |
| rampa 2,5 – 5,0 | 0,5 | 1,8 | 3,6 – 3,8 | 2,8 – 3,2 | 0 N (10–70 ms) |

Durma yolu tetikten itibaren; tetikten önce sensör gecikmesi (20 ms + 3 örnek) eklenir. Statik arka aks yükü 136 N.

**Model varsayımı:** motor modeli `tau = tau_durma · (u · k_V − w / w0)` (dunya.py); kesme = tork 0 (yalnız dişli ve
yuvarlanma sürtünmesi), kısa devre freni = `−tau_durma · w / w0`, rampa = öneri firmware PI'ı (KP 4, KI 20, TAHMİN)
teker hedefini rampayla 0'a indirir. Motor durma torku 21 kg·cm ve sürtünmeler TAHMİN.

## 2. Devrilme (görev 5)

Kütle merkezi modelden (`kutle_merkezi.json`): kütle 26,3 kg, x = −10 mm (gövde merkezinin 1 cm arkası), yerden
**520 mm**. Rijit gövde, kaymayan teker için öne devrilme (arka aks yükü 0) yavaşlaması:
**düz zeminde 3,68 m/s², 10° inişte 1,93 m/s².**

Ölçülen: hiçbir fren kipinde tekerlek kalkması yok (≤ 0,07 mm, temas sızması mertebesinde), öne yatma tepe ≤ 0,011°.
Düz zeminde rampa ≤ 2,0 m/s²'de arka aks hep ≥ 46 N (`durma.csv` 46,5); ≥ 2,5 m/s² ve kısa devre freninde 10–70 ms 0 N (tepe yavaşlama
2,8–3,2 m/s², el hesabı sınırının %80'i; kısa vuru, temas sertliği). 10° inişte arka aks yükü frenden önce 71 N
(en az 64 N) ve motor kesme dışındaki her fren kipinde 0,25–0,39 m/s'de 20–160 ms 0 N'a iniyor (0,10 m/s'de 0–20 ms),
ama gövde yatmıyor.

**Güvenli en büyük yavaşlama: düz zeminde 2,0 m/s²** (arka aks ≥ 46 N, el hesabı sınırının yarısı); 10° inişte el hesabı
sınırı 1,93 m/s², yani 2,0 m/s² rampası (ölçülen tepe 2,3) inişte sınırda. Firmware'de eğim bilgisi (IMU) yok; öneri:
rampa kipinde (firmware'in mevcut `rampa` ivme kipi) uçurum freni 1,5 m/s² ve hız ≤ 0,25 m/s (el hesabından). Ölçüm
bu öneriyi DESTEKLEMİYOR: `durma.csv`'de 10° inişte 1,5 m/s² rampasında arka aks 0,25 m/s'de 70 ms, 0,39'da 110 ms
0 N'a iniyor; 1,0 m/s²'de bile 0,25'te 40 ms, 0,39'da 90 ms. Gövde yatmıyor, ama inişte güvenli fren ivmesi ölçülerek
belirlenmedi.

10° iniş rampasında frenden 0,6 s sonra robot 0,10 m/s ile kaymaya devam ediyor (motor kesmede 0,75–0,88 m/s'ye
hızlanıyor). Kısa devre freni sıfır hızda tutmaz (bilinen bulgu, `kod/SIMULASYON.md`). Rampa üstünde uçurum durdurması
ancak tutma freniyle (sıfır hızda PI tutuşu, sonsuz vida, mekanik fren) çalışır.

## 3. Yanlış alarm ve eşik (görev 1; `denetim*.csv`, gölge denetçiler)

Gölge denetçi aynı okumaları görür, robotu durdurmaz: bir koşuda 18 eşik x onay çifti birlikte ölçülür.

| eşik / onay | düz | 20 mm eşik | derz | koyu şerit | 10° iniş rampası | halı 10 mm | halı 5 mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 15 mm / 2 | 0 / 144 | 72 / 144 | 0 / 144 | 56 / 144 | 138 / 144 | 47 / 144 | 0 / 144 |
| 30 mm / 2 | 0 | 41 | 0 | 53 | 84 | 0 | 0 |
| 40 mm / 2 (geliştirme 1) | 0 | 1 | 0 | 53 | 72 | 0 | 0 |
| 40 mm / 3 | 0 | 0 | 0 | 0 | 72 | 0 | 0 |
| 80 mm / 3 | 0 | 0 | 0 | 0 | 9 | 0 | 0 |

(2K ve 3KO, z 60 / 120 mm, eğim 0 / 15 / 30°, üç hız, açı 0 / 30°, tohum 1–2.)

- 20 mm eşik çıkışı: 30 mm altı eşikte her koşuda durur. Koyu şerit: onay 2'de dönüşsüz örneklerden durur, onay 3'te durmaz.
- 10° iniş rampası belirleyici: kafa kafaya girişte 40 mm eşikte bile durmaz, ama **çapraz girişte** (30–45°) tek köşe
  tekeri rampaya inmeden köşe sensörü rampa yüzeyinin 30 cm içine bakar ve mesafe 6 cm'ye kadar artar
  (`rampa_ayrinti`). Giriş açısı x eşik (onay 3): 60 mm'de 45° girişte 24 / 24, 80 mm'de 8 / 24, **100 mm'de 0 / 120**.
- Çapraz köşe yerleşiminde (`denetim2`, 2KD, z 60 / 120, eğim 15 / 30°): **100 mm / onay 3'te yedi sahnede 0 / 168.**

## 4. Yerleşim (görev 2, 4; geliştirme: `gelistirme*.csv`, tohum 1–2, `merdiven_17x30` ve `bosluk_3m`)

Geliştirme 1 (2928 koşu, 40 mm / onay 2, fren rampa 2,0 ve kısa devre): ileri yaklaşmada

| düzen | düştü (z 60 + 120, rampa 2,0) | en küçük pay cm |
| --- | --- | --- |
| 2K / 3KO / 4O, eğim 30° | 0 / 72 her biri | 3,2 – 3,3 |
| 2K / 3KO / 4O, eğim 15° | 0 / 72 | 1,8 – 2,6 |
| 2K / 3KO / 4O, eğim 0° (dik) | 4 – 8 / 72 | −0,8 |
| 2I (iç, y ±120), her eğim | 32 – 60 / 72 | −6 … −8 |

- **Orta / iç sensör bu sahnelerde katkı vermiyor:** 3KO ve 4O'nun düşme sayıları ve en küçük payları 2K ile aynı
  (540 eşleşik ileri koşunun 20'sinde, hepsi dik e0 / z 60, pay ±0,8 cm farklı; 84 koşuda ilk tetik orta / iç
  sensörden). Çapraz gelişte kenarı önce köşe tekeri geçer; iç sensörler onu korumaz (2I düşer). **Bu yalnız robottan
  geniş kenarlar için doğru:** robottan dar açıklıkta köşe sensörleri yetmiyor, ön iç sensörler gerekiyor (`dar_gelistirme`,
  Hüküm "Dar açıklık"; seçim bu yüzden `4OD+2AD` oldu). Çapraz köşelerle birlikte düz öne bakan iç sensörlerin izi köşe
  izinden 2 cm ileride olduğu için geniş kenarda da kafa kafaya payı artırıyor (0,39 m/s'de 3,4 → 4,5 cm, sınama 2).
- Dik bakan sensör 0,39 m/s'de geç kalır (iz tekerin yalnız 70 mm önünde, durma 42 mm + gecikme). 30° eğim izi 35–69 mm öne
  alır.
- Geri giderken: arka sensörsüz 144 / 144 düştü; +2A ile 0 düşme (en küçük pay 2,2–6,8 cm).
- Kenarda yerinde dönüş (dönme merkezi kenardan 0,3–0,6 m, ±1 rad/s; köşe 0,46 m/s ile süpürür): ileri bakan köşe
  sensörleriyle pay 0,5 cm, 100 mm eşikte 16 koşudan 1–4 düşme. **Çapraz dışa (yön ±45°) köşelerle 0 düşme, pay 5,2 cm**
  (z 120, eğim 30°, 100 mm / 3). Seçimin nedeni bu.

Geliştirme 2 (960 koşu, ön + arka köşe, düz / çapraz, z 60 / 120, eğim 15 / 30°, eşik 40 / 2 ve 100 / 3):

| yerleşim, eşik | ileri | geri | yerinde dönüş | dönüşlü yörünge |
| --- | --- | --- | --- | --- |
| **2KD+2AD z120 e30, 100 mm / 3 (seçilen)** | 0 / 36, pay 3,4 | 0 / 6, 7,2 | 0 / 16, 5,2 | 0 / 2, 6,5 |
| 2KD+2AD z120 e30, 40 / 2 | 0 / 36, 4,2 | 0 / 6, 7,7 | 0 / 16, 5,7 | 0 / 2, 7,0 |
| 2K+2A z120 e30, 100 / 3 | 0 / 36, 3,1 | 0 / 6, 6,5 | **1 / 16**, −0,0 | 0 / 2, 7,6 |
| 2KD+2AD z60 e30, 100 / 3 | 0 / 36, 1,8 | 0 / 6, 5,2 | 0 / 16, 1,6 | 0 / 2, 4,4 |
| 2K+2A z60 e15, 100 / 3 | 0 / 36, 1,1 | 0 / 6, 4,2 | **3 / 16**, −0,2 | 0 / 2, 3,4 |

Seçim kuralı: her geliştirme senaryosunda 0 düşme ve en büyük en küçük pay, yanlış alarmda 0 (100 mm / 3). 40 mm eşik
payı 0,8 cm artırıyor ama rampaya çapraz girişte durduruyor. Geliştirme 2'nin seçimi (`2KD+2AD`) dar açıklık
geliştirmesinde (`dar_gelistirme`, Hüküm) aynı kuralla `4OD+2AD`'ye değişti; köşe yerleşimi, yükseklik, eğim, eşik
değişmedi.

## 5. Sensör kusurları (görev 6; `kusur.csv`, ilk seçim `2KD+2AD`, geliştirme sahneleri ve tohumları 1–3)

Yeni seçimin ek ön iç sensörleri için yalnız ölü sensör denetimi koşuldu (`dar_gelistirme`, alt `kusur`: 0,50 / 0,70 m
açıklık, donmuş / hep dönüşsüz, 16 koşu): her koşuda denetçi arızayı fark edip durdu, 0 düşme. Zemini parlak yüzey (dönüşsüz oran)
taraması yeni düzenle yinelenmedi; sensör sayısı 4'ten 6'ya çıktığı için %5 dönüşsüzde yanlış durma olasılığı artar
(`yavasla` ile sınama 2'nin 540 yanlış alarm koşusunda, koyu yüzeyli iki sahne dahil, 0).

Ön sensörlerden biri ölü (donmuş değer ya da hep menzil dışı), uçuruma 0 / 30 / 60°, 0,25 / 0,39 m/s:

| politika | arızasız | donmuş değer | hep menzil dışı |
| --- | --- | --- | --- |
| `ucurum` (veri yok = uçurum) | 0 / 36 düştü | 0 / 72 (donma 0,5 s'de fark edilip durur) | 0 / 72 (açılışta durur) |
| `yavasla` | 0 / 36 | 0 / 72 | 0 / 72 |
| `yok_say` (veri yoksa atla) | **18 / 36** | **48 / 72** | **48 / 72** |

`yok_say` arızasızken bile 3 m boşlukta düşüyor: o derinlikte ışın menzil dışına çıkar, ölçüm "dönüş yok" olur.
Dönüşsüz örneği yok saymak güvensiz.

Zemini parlak yüzey (her örnek bu olasılıkla dönüşsüz), uçurum koşusu / düz zeminde 4 m yol:

| politika | dönüşsüz | uçurumda düştü | düz zeminde yanlış durma |
| --- | --- | --- | --- |
| `ucurum` | %5 | 0 / 36 | 6 / 18 |
| `ucurum` | %20, %50 | 0 / 36 | 18 / 18 |
| `yavasla` | %5 | 0 / 36 | **0 / 18** |
| `yavasla` | %20, %50 | 0 / 36 | 18 / 18 (yavaş gider, sonra durur) |
| `yok_say` | her oran | 18 / 36 | 0 / 18 |

**Seçilen politika `yavasla`:** kaçırma 0, %5 dönüşsüzde yanlış durma yok. %20 ve üstü dönüşsüz zeminde her politika ya
durur ya düşer: o zeminde robot sürülmemeli (masada ölçülmeli).

## 6. LiDAR merdiveni görüyor mu (görev 7; `lidar_denetim.json`)

Görmüyor. Robot merdiven kenarına 0,295 m'de, öne bakarken ±60° sektördeki 167 ışının hepsi 4,29 m'deki duvarı
ölçüyor; merdivenli ve merdivensiz sahnede en büyük fark **0,0 mm** (LiDAR düzlemi 0° ve 1,5° öne yatık). Yatay tarama
düzlemi (z 0,295) zeminin altına inen hiçbir şeyi kesmez.

## 7. Sınama (görev 8; ilk sınama `sinama.csv`, `sinama_y.csv`; sınama 2 `sinama2.csv`, `sinama2_karsi.csv`)

### 7a. İlk sınama (eski seçim; dar açıklığı kapsamaz)

İlk seçim (`deney.SECIM_1`: 2KD+2AD, z 120 mm, eğim 30°, 100 mm / 3, fren rampa 2,0), yeni tohumlar ve geometriler.

İleri yaklaşma, en küçük pay cm (düşme / koşu), politika `ucurum` tohum 101–110 | `yavasla` tohum 101–105:

| geometri | 0,10 m/s | 0,25 m/s | 0,39 m/s |
| --- | --- | --- | --- |
| merdiven 15 x 28 | 7,6 (0 / 80) · 7,6 (0 / 40) | 6,8 (0 / 80) · 6,9 (0 / 40) | 3,4 (0 / 80) · 3,8 (0 / 40) |
| merdiven 19 x 25 | 7,6 · 7,6 | 6,8 · 6,9 | 3,4 · 3,8 |
| kuyu (menzil dışı) | 7,6 · 7,6 | 6,8 · 7,5 | 3,4 · 5,1 |
| sahanlık köşesi (iki kenar, eğik gelen) | 4,2 · 4,2 | 4,2 · 4,2 | 3,4 · 4,2 |

En kötü açı 0° (kafa kafaya, en hızlı yaklaşma) ya da köşede 37°. Politika `ucurum` ile ayrıca: geri giderken 60 koşu
(15x28 ve 19x25 merdiven, 0 / 25 / 50°, 0,10 / 0,25 m/s) 0 düşme, pay ≥ 6,8 cm; kenarda yerinde dönüş 60 koşu 0 düşme,
pay ≥ 4,4 cm (3 koşuda dönüş kenara ulaşmadı, tetik yok); eğik gelen dönüşlü yörünge 20 koşu 0 düşme, pay ≥ 8,4 cm.

Yanlış durma (yedi denetim sahnesi x 3 hız x açı 0 / 20 / 40° x 5 tohum = 315 koşu):

| politika | düz | 20 mm eşik | derz | koyu şerit | 10° iniş rampası | halı 10 mm | halı 5 mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ucurum` | 0 / 45 | 0 / 45 | 0 / 45 | **4 / 45** (dönüşsüz) | 0 / 45 | 0 / 45 | 0 / 45 |
| `yavasla` (seçilen) | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 |

İlk sınamanın sonucu: eski düzen bu 2210 koşunun hiçbirinde düşmedi; `yavasla` ile yanlış durma yok. 0,39 m/s'de en küçük
pay 3,4 cm (`ucurum`) / 3,8 cm (`yavasla`). Dar açıklığı kapsamadığı için hüküm 7b'ye dayanır.

### 7b. Sınama 2 (seçilen `4OD+2AD`, politika `yavasla`; 3440 koşu)

Geniş kenar ileri yaklaşma, en küçük pay cm (düşme / koşu; tohum 101–110, açılar 7a ile aynı):

| geometri | 0,10 m/s | 0,25 m/s | 0,39 m/s |
| --- | --- | --- | --- |
| merdiven 15 x 28 | 7,6 (0 / 80) | 7,5 (0 / 80) | 4,5 (0 / 80) |
| merdiven 19 x 25 | 7,6 (0 / 80) | 7,5 (0 / 80) | 4,5 (0 / 80) |
| kuyu (menzil dışı) | 7,6 (0 / 80) | 7,5 (0 / 80) | 5,8 (0 / 80) |
| sahanlık köşesi | 4,2 (0 / 80) | 4,2 (0 / 80) | 4,2 (0 / 80) |

Geri 60 koşu 0 düşme, pay ≥ 6,8 cm; yerinde dönüş 60 koşu 0 düşme, pay ≥ 4,4 cm (3 koşuda dönüş kenara ulaşmadı); yay 20
koşu 0 düşme, pay ≥ 8,5 cm. Yanlış durma: yedi eski denetim sahnesinde 0 / 315, beş yeni sahnede 0 / 225 (25 mm eşik,
geniş derz, 30 cm koyu bant, 8° iniş rampası, 15 mm halı; her biri 0 / 45).

Dar açıklık (tohum 101–105; 3 açı x 5 yanal kayma x 3 hız x 5 tohum = sahne başına 225 koşu), düşme / koşu (en küçük pay cm):

| yerleşim | 0,45 m | 0,55 | 0,65 | 0,75 | 0,90 | 0,60 sığ (0,4 m) | dar merdiven 0,60 | dar merdiven 0,80 | toplam |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`4OD+2AD` (seçilen)** | 0 (4,3) | 0 (4,3) | 0 (4,3) | 0 (4,8) | 0 (5,0) | 0 (3,0) | 0 (3,0) | 0 (4,5) | **0 / 1800**, pay ≥ 3,0 |
| `3KOD+2AD` (karşılaştırma) | 0 (2,5) | 0 (2,5) | 0 (3,1) | 0 (3,6) | 0 (5,2) | 0 (1,2) | 0 (1,2) | 0 (4,5) | 0 / 1800, pay ≥ 1,2 |
| `2KD+2AD` (ilk seçim) | **65** | **46** | **17** | **3** | 0 (3,4) | **30** | **30** | 0 (2,1) | **191 / 1800**, pay −13,2 |

Seçilen düzenin dar açıklıkta en küçük payı yanal kaymaya göre (0,10 / 0,25 / 0,39 m/s): −0,15 m'de 8,0 / 5,7 / 3,0;
−0,05'te 8,0 / 6,6 / 4,3; 0,05'te 9,9 / 7,8 / 4,5; 0,15'te 6,4 / 5,4 / 4,5; 0,25'te 6,0 / 6,2 / 4,5 cm. 94 / 1800 koşu
açıklığa hiç girmeden yanından geçti (hepsi 30° açı, yanal ≥ 0,05; tetik yok, pay ≥ 5,1 cm): bunlar düşme sayılmadı ama
"durdu" da sayılmadı.

`2KD+2AD`'nin düşmeleri en çok kafa kafaya ya da 10°, orta hattan ±0,15 m içinde; 0,90 m ve 0,80 m dar merdivende
düşmedi. Ön ortalı `3KOD+2AD` sınamada da düşmedi (pay ≥ 1,2 cm), ama geliştirmede 0,40 m açıklıkta 2 / 540 düştüğü için
seçilmedi; sensörden tasarruf gerekiyorsa beşli düzen ikinci seçenektir (en dar açıklık ≈ 0,45 m kabulüyle).

**Hüküm sınamadan:** seçilen altı sensörlü düzen sınama 2'nin 2900 uçurum koşusunun hiçbirinde düşmedi, 540 yanlış alarm
koşusunda hiç durmadı. 0,39 m/s'de en küçük pay 3,0 cm (dar açıklık) / 4,2 cm (geniş kenar): küçük ama sıfırdan uzak;
sensör gecikmesi (uzun kip) ya da fren modelindeki 3 cm'lik bir hata bunu yer. Gerçek robotta ilk deneyde hız 0,25 m/s
(pay ≥ 4,2 cm) önerilir. **Güncellendi:** "0,39 güvenli tavan" ile "ilk deneyde 0,25" çelişkisi kaldırıldı: tek öneri
0,25 m/s, ilk denemede de nihai seyirde de (duyarlılık ölçümüyle; "Tamamlama turu", T6).

## Geliştirme / sınama ayrımı

| | Geliştirme (ayar) | Sınama (hüküm) |
| --- | --- | --- |
| Tohum | 1, 2, 3 | 101–110 |
| Uçurum geometrisi | `merdiven_17x30` (17 x 30 cm, 8 basamak), `bosluk_3m` | `merdiven_15x28`, `merdiven_19x25`, `kuyu` (menzil dışı), `kose` (iki kenarlı sahanlık köşesi, eğik gelen kenar) |
| Açılar | 0, 15, 30, 45, 60, 80 | 0, 10, 22, 37, 52, 68, 80, 85 |
| Yanlış alarm | tohum 1–2, açı 0 / 30 | tohum 101–105, açı 0 / 20 / 40 |
| Dar açıklık (`dar_gelistirme` / `sinama2`) | genişlik 0,40 / 0,50 / 0,60 / 0,70 / 0,80 / 1,00 m, 3 m derin; yanal −0,20 … +0,20 (0,10 adım); açı 0 / 20 / 40; tohum 1–2 | genişlik 0,45 / 0,55 / 0,65 / 0,75 / 0,90 m, 0,60 m x 0,4 m sığ, 0,60 ve 0,80 m dar merdiven (18 x 27 cm); yanal −0,15 / −0,05 / 0,05 / 0,15 / 0,25; açı 0 / 10 / 30; tohum 101–105 |
| Yanlış alarm, yeni sahne (yalnız `sinama2`) | - | 25 mm eşik, geniş derz (12 x 8 mm, 0,45 m aralık), 30 cm koyu bant, 8° iniş rampası, 15 mm halı |

Bağımsızlığın sınırı: `merdiven_15x28`, `merdiven_19x25` ve `kuyu` aynı x = 16 m düz kenarı taşır; `ucurum`
politikasıyla 240 eşleşik (açı, hız, tohum) koşunun 238'inde üçü aynı payı verir. Yani bunlar pratikte tek yeni
geometri sayılır; gerçekten yeni olan `kose` ve açılardır. İlk sınamanın yanlış alarm bölümü geliştirmedeki yedi denetim
sahnesini yeni tohum ve açılarla yineler; sınama 2 buna beş yeni sahne ekler (225 koşu, 0 yanlış durma). Dar açıklık
sınaması genişlik, derinlik, merdiven ve yanal kayma bakımından geliştirmeden ayrıdır, ama aynı sahne türüdür
(dikdörtgen delik, x = 16 m'de yakın kenar).

Dar açıklık seçimi: `dar_gelistirme` (tohum 1–2) bitti, `secim.json` `4OD+2AD`'ye yazıldı, sonra `sinama2` koşuldu. Politika
`yavasla` sınama 2'den önce seçilmişti (kusur aşaması), bu yüzden sınama 2'de geri / dönüş / yay da `yavasla` ile koşuldu
(ilk sınamada `sinama_y` bunları kapsamıyordu).

Eşik, onay, yerleşim, eğim, yükseklik ve politika yalnız geliştirme ve denetim koşularından seçildi (`secim.json`).
Sınamadan sonra eşik / yerleşim / fren değiştirilmedi. Sınama, süre için kusur aşamasıyla aynı anda koşuldu; politika o
an `ucurum` idi. Kusur aşaması (geliştirme tohumları) `yavasla`'yı daha iyi bulunca sınama yalnız politika değişik olarak
yeniden koşuldu (`sinama_y`); iki sonuç da raporlandı.

## Simülasyonun iyimser varsayımları

- Sensör modeli VARSAYIM: 17 ışınlı koni, "ağırlığın ≥ %25'ini taşıyan en yakın öbek" kuralı, gürültü σ 2,5 mm + %0,2,
  koyu yüzeyde σ x 2 ve %5 dönüşsüz. Gerçek VL53L1X histogram işlemi, ortam ışığı, eğik gelişte sinyal kaybı, cam / ayna /
  parlak siyah zemin, toz, sensörler arası çapraz konuşma modellenmedi. Masada doğrulanmalı.
- Sahne kusursuz: keskin basamak burnu, düz zemin; halı kaplı basamak, yuvarlak burun, ıslak zemin yok. **Güncellendi:**
  3 cm basamak burnu tamamlama hükmünde var (`merdiven_burun_18x28`); yuvarlak burun ve halı kaplı basamak hâlâ yok.
- Firmware zamanlaması kusursuz (10 ms dilim, I2C gecikmesi yok, bir örnek gecikme). 50 Hz denetçi döngüsü ölçülmedi
  (ek ≤ 10 ms, 0,39 m/s'de ≤ 0,4 cm).
- 50 Hz örnek ile 4 m menzil birlikte varsayıldı. VL53L1X'te 20 ms zamanlama bütçesi yalnız kısa mesafe kipinde
  (≈ 1,3 m) var; uzun kip en az ≈ 33 ms ister. Kısa kipte 3 m boşluk dönüşsüz okunur (`kuyu` sınaması bu durumu kapsar);
  uzun kipte tetik ≈ 50 ms gecikir, 0,39 m/s'de pay ≈ 2 cm azalır (3,4 → ≈ 1,4 cm; ölçülmedi). Kip masada seçilmeli.
  **Güncellendi:** veri sayfasından doğrulandı ve ölçüldü (T5); seçim kısa kip 20 ms, 1,3 m menzil.
- Robot gövdesi ışını kesmiyor: seçilen z 120 mm / 30° çapraz yerleşimde ışın etek köşesinin içinden çıkar (BENIOKU);
  etek penceresi ve onun koniyi kırpması modellenmedi.
- Teker rijit, sürtünme ve motor değerleri TAHMİN; robot hep düz zeminde kalibre edildi.
- Altı sensör aynı I2C hattında 50 Hz'de, gecikmesiz ve birbirini etkilemeden okunuyor varsayıldı (adres için sensör başına
  XSHUT ucu gerekir; çapraz konuşma modellenmedi). Ön iç sensörler köşelerle aynı yükseklikte (120 mm) etek içinden
  bakıyor; etek ön yüzünde pencere gerekir. **Güncellendi:** seçim artık on sensör (`6OD+4AD`), varsayım aynı (Tamamlama
  turunun iyimser varsayımları).
- Dar açıklık sahnesinde kenarlar keskin, yan duvar dik ve düz; gerçek merdiven boşluğunda korkuluk, süpürgelik, halı kenarı
  olabilir.
- Hakem teker merkezlerinin (temas noktası) kenara yatay payını ölçer; teker yarıçapı 62,5 mm olduğundan pay 0'ın biraz
  altı hemen devrilme değildir ama düşme sayıldı (kötümser).

## Izgaradan atılanlar (süre: ≈ 2,5 saat)

- Denetim: yalnız 2K ve 3KO (yanlış alarm y konumuna değil yükseklik / eğime bağlı), tohum 1–2, açı 0 / 30, yol 1,8 m.
- Geliştirme 1: tohum 1–2 (3 değil); kısa devre freni yalnız z 60, tohum 1; geri / dönüş / yay yalnız `merdiven_17x30`.
- Geliştirme 2: tohum 1 (yerinde dönüş 1–2); denetim2 tohum 1.
- Kusur: yalnız ön sensör arızası; 0 / 30 / 60°, 0,25 / 0,39 m/s.
- Sınama: geri / dönüş / yay ve yanlış alarm tohum 101–105; `sinama_y` yalnız ileri ve yanlış alarm, tohum 101–105.
- Dar açıklık: geliştirme tohum 1–2, sınama tohum 101–105 (sınama 2'nin geniş kenar bölümü 101–110); açıklık boyu hep 2 m;
  0,40 m'den dar açıklık yok; açıklığa geri giderek ya da yerinde dönerek yaklaşma yok (yalnız ileri); yalnız z 120 / e 30
  yerleşimi; seçilmeyen adaylar sınamada yalnız dar açıklıkta (`sinama2_karsi`).
- Yeni seçimle (`4OD+2AD`) kusur aşaması (parlak zemin, köşe sensörü arızası) ve durma / devrilme yeniden koşulmadı
  (durma ve devrilme sensörden bağımsız; köşe arızası denetçide sensör başına aynı mantık).
- Sensör konisi yalnız 27° (15° ROI denenmedi); yükseklik yalnız 60 / 120 mm; tek kat merdiven ve boşluk derinliği.

## Sayılar

Koşu: durma 132, denetim 1008, rampa_ayrinti 120, denetim2 168, geliştirme 2928 + 960, kusur 1188, sınama 1415,
sinama_y 795; dar açıklık düzeltmesi: dar_gelistirme 2100, sinama2 3440, sinama2_karsi 3600. Hata (istisna) 0. Bütün
düşmeler CSV'de durur (`dustu`, `dustu_neden`, `pay_min_cm`; dar açıklıkta `yanal` sütunu orta hattan kaymayı verir).

Görseller: `../gorsel/durma_yolu.png`, `../gorsel/yerlesim_pay.png`, `../gorsel/sinama_pay.png` (ilk sınama, eski düzen),
`../gorsel/dar_aciklik.png` (dar açıklıkta üç aday, geliştirme ve sınama), `../gorsel/demo_pencere.png` (3B gösterim: robot
0,25 m/s merdivene yürür, ön sensör tetikler, durur; **güncellendi:** tamamlama turunda on sensörlü `6OD+4AD` seçimiyle
yeniden çekildi). Dar açıklık 3B'de: `kod\ucurum.bat acik_55`
(seçim `secim.json`'dan, altı sensör; bu düzeltmede pencere açılarak denenmedi; **güncellendi:** `secim.json` artık on
sensörlü `6OD+4AD`).
