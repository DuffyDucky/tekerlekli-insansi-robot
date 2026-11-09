# F2 günlüğü (P2.1 omuz mekanik durdurucu, P2.2 omuz çakışma taraması) — tasarım ajanı A, 09.11.2026

Brief: `planlama/d158/F2-brief.md`. Plan: `planlama/dongu-158.md` §3 F2. Dal `lale-duzeltme`.
Kısaltmalar: `TF/` = `tasarim/freecad/`, `KY/` = `TF/lale158/kafa-yerlesim/`, `SP/` = oturum scratchpad klasörü (depo dışı,
`C:\Users\Victus\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad`). Önceki durumun kopyaları `SP/f2/once/`.
FreeCAD 1.1, başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py`; her koşu `SP/f2/fc.sh` ile (koşudan önce boş bellek ≥ 2 GB ve çalışan
freecadcmd 0 denetimi, koşu boyunca 5 dk'da bir boş bellek `SP/f2/bellek.log`'a).

## Başlangıç (02:31)
- `py -3 planlama/d158/regresyon.py --yazma` (02:31:41, taban 02:17:55): çıkış 0, "GEÇER", 10 değer "aynı" (rampa 1,519).
- `py -3 TF/carpisma_kos.py kontrol`: çıkış 1, "kaynagi eskimis bolumler: omuz" (F1b sonundaki durum).
- Boş bellek 5,89 GB / 15,29 GB; çalışan FreeCAD süreci yok.
- `git status --short` başlangıçta: `dongu-158.md`, 13 kabuk görseli, `TF/montaj/yerlesim-kontrol.json` değişik (K23, bu paketten önce);
  izlenmeyenler F2/F3a/F4a brief'leri, F3a dosyaları, F5b dosyaları, K18–K22 klasörleri.
- Önceki durum kopyası `SP/f2/once/`: `omuz-analiz.json`, `omuz-baski.json`, `omuz_parcalar.py`, `omuz_montaj.py`, `arayuz.py`,
  `carpisma-sonuc.json`, `carpisma-bolum/*.json`, `montaj-analiz.json`, `dirsek-analiz.json`, `taban-analiz.json`, `uygulama-ivme.json`,
  omuz ve iskelet `regresyon/*.json`.

## P2.1 Omuz mekanik durdurucu

### Önce: S2 içe dönerken ilk temaslar (durdurucusuz model, ölçüldü)
Ölçüm betiği `SP/f2/olc_ilk_temas.py` (freecadcmd, yalnız okur; 02:33:33–02:38:37, 304 s, rc 0, boş bellek 5,90 → 5,88 GB; log `SP/f2/olc_once.log`;
sonuç **`SP/f2/olc_once.json`**). Yöntem: omuz yereli (sağ), kol (omuz `Kol` grubu: çatal, tüp, horn, cıvatalar) `Pp(S1)·Pr(S2)` ile taşınır;
S2 6°'den 1° (tambur 0,5°) adımla inilir, ilk temastan sonra 8–9 adım ikiye bölme (çözünürlük ≤ 0,004°). Temas = ortak hacim > 0,01 mm³ ya da
`distToShape` ≤ 0,0001 mm. Kabuk parçaları `kabuk_parcalar.py`'den (global → omuz yereli, y − S3).

| Çift | İlk temas, S2 (°) | Not (JSON anahtarı) |
|---|---|---|
| Kol çatalı ↔ **S1 kablo tamburu** (göbekte, S1 ile döner) | **3,6465** | S1'den bağımsız (`a_parca`) |
| Üst kol tüpü ↔ **S1 kaset kapağı sağ** (kabuk modülü) | **3,207** (S1 20…140), 3,203 (S1 150), 3,168 (S1 10), 2,609 (S1 160), 1,246 (S1 0), 0,223 (S1 170) | `b_kol_x_kabuk`; en büyük `b_en_buyuk_temas_acisi` = [3,207, S1 140] |
| Üst kol tüpü ↔ göğüs / omuz bandı (kabuk) | −1,69 (S1 −10, −20) … −3,29 (S1 −60) | S1 −60…−10 |
| Kol çatalı ↔ omuz göbeği (gövdesi) | −14,37 | |
| S1 180 | −6°'ye kadar kabukla temas yok | |

**Sonuç:** Brief'teki "kabuk teması −3°" ve "0…+2°" önerisi 14 Ekim (C1) ölçümünden, S1 kablo kasetinden (15 Ekim) önce. Bugünkü modelde kol önce
**tambura (3,65°)**, sonra **kaset kapağına (kabuk, 3,21°)** dayanır; 0…+2°'lik durdurucu tambur ve kaseti korumazdı. S1-kaset.md'deki "≈ 3,8° tambur,
≈ 3,5° flanş" yaklaşık değerlerdi; ölçülen 3,65 / 3,21. Durdurucu penceresi: **3,65° < temas < 5° (yazılım alt sınırı)**.

### Tasarım: göbeğe tek parça durdurucu dişi (temas açısı 4,3°)
Değişen kaynaklar:
- `TF/arayuz.py` OMUZ bloğu: yeni `durdurucu=dict(temas_aci=4.3, x0=161.0, x1=168.0, y=(-34.0, -10.0), z=(-8.0, 21.0))` (açıklama yorumu ile).
  `eklem_sinirlari()` değişmedi; üreteç çalıştırılmadı, `kod/ortak/eklem_sinirlari.json` dokunulmadı.
- `TF/omuz/omuz_parcalar.py`: `DURDURUCU` = iki kutu (dış altta x 161…168, y −34…−22; iç duvara kök x 161…163,5, y −23…−10), z −8…21;
  `Pr(temas_aci)` konumundaki kol çatalı kirişinin hacmi bundan çıkarılır (dişin dayanma yüzü tam 4,3° düzleminde), `hub.fuse(DURDURUCU)`.
  Parça adı, grubu ve STL adı aynı ("Omuz gobegi"), not alanına durdurucu eklendi. Sol omuz aynı parçanın aynası (montajdaki mevcut düzen).

| Konu | Karar | Gerekçe |
|---|---|---|
| Yer | Omuz göbeğinin iç duvarının (x 163…168) altında, kol çatalının çapraz kirişinin (çatal yereli x 165, y −34…−28) iç uç yüzünün karşısı | Göbek S1 ile döner, kolu S2 ekseninde taşır; durdurucu göbekte olunca S1'in her açısında aynı yerde çalışır (kabukta olsa S1'e göre kayardı). Kiriş çatalın en rijit, kolun ağırlığını taşıyan elemanı. |
| Temas açısı | **S2 = 4,3°** | Ölçülen pencere 3,65° (tambur) … 5° (yazılım alt sınırı) ortası: iki yana ~0,7° (kuvvet kolu 30,3 mm'de ≈ 0,37 mm). Baskı toleransı (±0,2 mm) ve çatal sapması (stall'da 0,075°) tambura varmadan karşılanır; normal çalışmada (≥ 5°) 0,34 mm boşluk kalır, dokunmaz. |
| Yük yolu | Kiriş uç yüzü → diş → göbek iç duvarı/S2 plakası → göbek (S1 yatakları) | Horn, servo mili ve dişliler yolda değil: durdurucu kolu servo çıkışından önce, çatal üzerinden tutar. Stall'da bile servo torku durdurucuya gider, kaset/tambur yüklenmez. |
| Malzeme | PETG-CF, göbekle tek parça (ek parça, vida, bağlantı yok) | BOM değişmez; ayrı parça gevşeyemez. |
| Kütle | Diş 2975 mm³ ≈ 3,4 g (`darbe.json`); göbek 175,1 → **177,6 g** (+2,5 g, `omuz-analiz.json` `kutle.Gobek`, dişin bir kısmı duvarla örtüşür); iki omuz +5 g | |

Görseller (kaynak `SP/f2/gorsel_veri.json`, çizim `SP/f2/ciz.py`):
- `planlama/d158/F2-durdurucu-yakin.png`: temas anı (S2 4,3°), içten ve alttan bakış; diş kırmızı, çatal turuncu.
- `planlama/d158/F2-durdurucu-kesit.png`: z 6,5 ve z −1,25 kesitleri; göbek, diş, tambur, kaset kapağı, çatal (4,3° / 5° / 0°), tüp.

### Sonra: ölçümler (durdurucu dahil)
Betik `SP/f2/olc_f2.py` (02:40:28–03:19:56, 2368 s, rc 0, boş bellek 5,85 → 5,58 GB; sonuç **`SP/f2/olc_sonra.json`**).

| Ölçüm | Sonuç | JSON anahtarı |
|---|---|---|
| Kol çatalı ↔ durdurucu ilk temas | **4,3002°** | `c_kol_x_durdurucu` |
| Ortak hacim (dişe girme) | 36,46 mm³ @ 3,8°; 7,09 @ 4,2°; 0,70 @ 4,29°; 0 @ 4,30° | ″ |
| Boşluk | 0,0049 mm @ 4,31°; 0,049 @ 4,4°; **0,344 mm @ 5°** (yazılım alt sınırı); 2,88 @ 10°; 8,93 @ 60/120/150° | ″ |
| Temas yüzü | 133,17 mm²; kutu x 167,16…167,5, y −34…−29,42, z −8…21; S2 eksenine kuvvet kolu 30,30 mm; diş geçerli, tek katı | ″, `durdurucu` |
| Kol ↔ göbek (tüm göbek) ilk temas | 4,2998° (diş); tambur teması hâlâ 3,647° → 4,3°'de tambura **0,400 mm** boşluk | `a_kol_x_gobek` |
| Kol ↔ kabuk ilk temas | değişmedi, en büyük 3,207° (S1 140) | `b_kol_x_kabuk`, `b_en_buyuk_temas_acisi` |
| **Kol ↔ kabuk, durdurucu açısında (4,3°)** | **temas 0**; en küçük boşluk **0,831 mm** (S1 20, tüp ↔ kaset kapağı) | `b_temas_acida_en_kucuk_bosluk` |
| Kol zinciri (omuz Kol + dirsek/ön kol/el) ↔ kabuk; S1 {−60, −45…150}, dirsek {0, 30, 60, 90, 105}, bilek {−90, 0, 90} | S2 4,3°: en küçük 0,831 mm, **çakışma 0**; S2 5°: en küçük 1,358 mm, çakışma 0 | `e_kol_zinciri_x_kabuk` |
| S1 aralık dışı (S2 5/30/60/90/120; S1 180→330 ve −60→−210, göbek + kol ↔ kabuk ve omuz gövdesi) | temas yok | `d_s1_aralik_disi` |
| Eylemsizlik (S2 ekseni) | omuz Kol 158,96 g, dirsek zinciri 400,49 g; toplam 559,5 g, I 0,02941 kg·m², ağırlık merkezi 199,4 mm; 500 g el yüküyle I 0,08278 | `g_eylemsizlik` |

Önceden var olan üst doğal dayanak (bilgi): çatal ↔ göbek S2 120…125° arasında (`omuz-analiz.json` `kol_gobek`), yazılım üst sınırı 120°.

### Çarpma yükü ve dayanım (kaba hesap)
Betik `SP/f2/darbe.py` → **`SP/f2/darbe.json`**. Yöntem: tek serbestlik dereceli enerji; tepe tork = √(2·E·kθ) (+ servo sürerse stall).
Diş kökü: kalınlık 5,67 mm, genişlik 29 mm, eğilme kolu 8,71 mm (W 155,5 mm³). Malzeme ve katsayılar `taslak-170/kol-analiz/kol_analiz.py`'den:
PETG-CF XY 59,8 MPa × dolu 0,9 × K_T 0,85; sürekli yükte K_sürünme 0,45 → **izin 20,6 MPa**, darbede **45,7 MPa**. Rijitlik: diş 4977 N/mm,
temas/kiriş/duvar dahil 2489 N/mm (yarısı, tahmin), kol eğilmesi 1715 N·m/rad → eşdeğer kθ 980 N·m/rad.

| Senaryo | Enerji (J) | Kuvvet (N) | Gerilme (MPa) | Emniyet | Çatal sapması (°) |
|---|---|---|---|---|---|
| Stall (30,4 kg·cm = 2,98 N·m), statik, sürekli | 0 | 98,4 | 5,51 (kayma 0,9; temas basıncı 0,74) | **3,73** | 0,075 |
| Kol 1,5 rad/s (yazılım notundaki insan yanı omuz hızı), yüksüz | 0,033 | 364 | 20,4 | **2,24** | 0,28 |
| Kol 1,5 rad/s, elde 500 g | 0,126 | 618 | 34,6 | 1,32 | 0,47 |
| Kaçak servo tam hız 8,06 rad/s, yüksüz | 0,954 | 1526 | 85,4 | 0,54 | 1,16 |
| Kaçak servo tam hız, 500 g | 3,64 | 2886 | 161,6 | 0,28 | 2,19 |
| Güç kesik, S1 0, S2 30°'den serbest düşme (sürtünmesiz), yüksüz | 0,144 | 554 | 31,0 | 1,48 | 0,42 |
| Güç kesik, S2 90°'den | 1,09 | 1526 | 85,5 | 0,54 | 1,16 |
| Güç kesik, S2 120°'den | 1,64 | 1870 | 104,7 | 0,44 | 1,42 |
| Güç kesik, S2 120°'den, 500 g | 4,63 | 3143 | 176,0 | 0,26 | 2,39 |

İzinli darbe: emniyet 2 için 408 N / 0,045 J (yüksüz 100°/s, 500 g ile 51°/s; serbest düşme S2 ≤ 17,1°); emniyet 1,2 için 681 N / 0,159 J (188°/s).
**Değerlendirme:** Durdurucu stall'u ve normal hızda (≤ 1,5 rad/s) yüksüz çarpmayı güvenle karşılar; bu, brief'in "S2 arıza/güç kaybı/yazılım sınırı
aşımı" amacının servo-tutuşlu kısmını karşılar. Tam hız kaçak ve yüksekten güç kesik düşmede tek başına yetmez (emniyet < 1). Dahil olmayan
iki etki ters yönde: servo geri sürme sürtünmesi (DS3235 dişli oranı 373; güç kesikken kolun düşmesini frenler, lehte) ve motor rotorunun
dişliler üzerinden yansıyan eylemsizliği (oranın karesiyle büyür, kaçak serviste çarpma enerjisini artırır, aleyhte). İkisi de ölçülmedi.
Karar taslakları 1–2 bu boşluk için.

### Baskı analizi (`omuz_baski.py` yöntemi)
Koşu: `TF/omuz/omuz_baski.py` (FCStd'den; 03:20:56–03:25:32, 276 s, rc 0). Sonuç `TF/omuz/omuz-baski.json` `parcalar[2]` (Omuz gobegi), önceki
`SP/f2/once/omuz-baski.json`.

| Omuz göbeği, seçilen yön +X (x = 150 yüzü tablada) | Önce | Sonra |
|---|---|---|
| `destek_gerekli` | true | true (değişmedi; göbek zaten destekli parça) |
| Destek bölgesi sayısı | 3 | 4 |
| Destek alanı / hacmi | 2020,6 mm² / 27,52 cm³ | 2352,7 mm² / 29,69 cm³ |
| Dişin bölgesi | — | z 10,23…11,23 (= dişin x 161 alt yüzü, tabladan 11 mm), 673 mm², konsol 16,7 mm, `tablaya: true`; önceki 270 mm²'lik x 160,2 bölgesiyle birleşti |
| Eğimli çıkıntı yüzü (`egim_yuz`) | 0 | 4 yüz, 73,4 mm²: robot x 183/193, y 33,4/36,6 (dişten uzak; F2 kaynaklı değil, aşağıdaki not) |
| Destek filamenti / parça kütlesi (0,90) | 5,2 g / 59,3 g | 5,7 g / 61,7 g |
| Süre (0,90) | 1,41 sa | 1,47 sa |
| Tüm omuz baskı toplamı (0,90) | 602 g, 14,4 sa | 607 g, 14,5 sa |

**Gerekçe:** Dişin x 161 alt yüzü +X yönünde tabladan 11 mm yukarıda yatay bir tavan; tabladan yükselen destekle basılır. Bu, iç duvarın (x 163)
mevcut desteğiyle aynı tür ve aynı bölge (birleşik bölge), yani yeni bir destek tipi değil. Dişin dayanma yüzü 4,3° eğik ve +X'e bakar (üst yüz,
destek gerekmez); katman basamakları bu yüzde 0,2 mm katmanda ≈ 0,015 mm (tan 4,3° × 0,2), temas için önemsiz. Diş katmanları kuvvet yönüne
(robot x) dik basılır: çarpma kuvveti katmanları birbirine bastırır, kök eğilmesi katman düzleminde (XY dayanımı geçerli; hesap XY ile yapıldı).

**`egim_yuz` notu:** `SP/f2/gobek_fark.py` (freecadcmd, 03:34:06–03:34:09, rc 0 → `SP/f2/gobek_fark.json`) F2 öncesi (`SP/f2/once/omuz_parcalar.py`)
ve sonrası göbeği karşılaştırdı: eklenen hacim 2142,8 mm³, kutusu x 161…167,5, y −34…−10, z −8…21 (yalnız diş); çıkan hacim 0. Bu 4 eğik yüz
(normal (−0,866, ±0,5, 0), 15,9 ve 20,8 mm²) **F2 öncesi geometride de aynen var** (`egim_eski` = `egim_yeni`); `omuz_baski.py` 15 Ekim'den beri
değişmedi. 29 Ekim koşusunun bunları neden raporlamadığı bu paketin kapsamı dışında: açık kalan olarak not edildi (destek alanına etkisi 63,5 mm² izdüşüm).

### Modül zinciri (P2.1 sonrası yeniden üretim) ve kütle / tork değişimi
`bash SP/f2/zincir_p21.sh omuz_montaj omuz_baski dirsek_montaj taban_montaj ana_montaj uygulama_ivme` (çıktı `SP/f2/zincir_p21.out`, loglar
`SP/f2/<ad>.log`; her adımdan önce boş bellek ≥ 2 GB ve FreeCAD süreci 0 denetimi):

| Adım | Saat | Süre | Boş bellek başta → sonda | rc | Yazılan |
|---|---|---|---|---|---|
| `TF/omuz/omuz_montaj.py` | 03:20:08–03:20:55 | 47 s | 5,55 → 5,62 GB | 0 | `omuz-analiz.json`, `omuz-montaj.FCStd`, `.step`, `stl/*.stl`, BOM |
| `TF/omuz/omuz_baski.py` | 03:20:56–03:25:32 | 276 s | 5,62 → 5,52 GB | 0 | `omuz-baski.json` |
| `TF/dirsek/dirsek_montaj.py` | 03:25:33–03:29:31 | 238 s | 5,56 → 5,52 GB | 0 | `dirsek-analiz.json` (+ FCStd/STEP) |
| `TF/taban/taban_montaj.py` | 03:29:32–03:31:01 | 89 s | 5,52 → 5,46 GB | 0 | `taban-analiz.json` (+ FCStd/STEP) |
| `TF/montaj/ana_montaj.py` | 03:31:02–03:32:33 | 91 s | 5,46 → 5,41 GB | 0 | `montaj-analiz.json`, `robot-montaj.FCStd/.step`, `robot-bom.csv` |
| `KY/uygulama_ivme.py` | 03:32:35–03:33:39 | 64 s | 5,42 → 5,34 GB | 0 | `KY/uygulama-ivme.json` |

`omuz-analiz.json` önce ↔ sonra: `statik` [] → [] (ev pozu S2 5°, çakışma 0); `kol_gobek["5"]`, `["10"]` [] → [] (yazılım aralığında temas yok);
`statik_s2_0` ve `kol_gobek` S2 ≤ 0 anahtarlarına "Kol catali ↔ Omuz gobegi" eklendi (395,8 mm³ @ 0°; S2 0 durdurucunun ötesi, beklenen: durdurucu
burada kolu tutuyor); `eklem_siniri` aynı (S1 −45…135, S2 5…120, kaynak `arayuz.OMUZ`); `joints_ok` true; `bosluk.Kol-Govde` 6,29 mm aynı.

| Kütle / tork (kaynak) | Önce | Sonra | Pay (stall 30,4 kg·cm) önce → sonra |
|---|---|---|---|
| Omuz göbeği (`omuz-analiz.json` `kutle.Gobek`) | 175,1 g | 177,6 g | |
| Omuz modülü, sağ = sol (`montaj-analiz.json` `moduller[1,2].kutle_g`) | 567,56 g | 570,01 g | |
| Robot (`montaj-analiz.json` `kutle_g`) | 25.715,59 g | 25.720,49 g (+4,9) | |
| Robot ağırlık merkezi y (`montaj-analiz.json` `agirlik_merkezi`) | 528,457 mm | 528,593 mm | |
| S1 omuz modeli en büyük tork (`omuz-analiz.json` `tork`, 875 poz; alt kol 260 g tahmini) | 5,97 kg·cm (S1 90, S2 0) | 5,98 kg·cm | 5,09 → 5,08 |
| S2 omuz modeli en büyük tork (″) | 6,12 kg·cm (S1 0, S2 90) | 6,12 | 4,97 → 4,97 |
| **S1 tam kol, yüksüz** (`dirsek-analiz.json` `tork.sonuc[0]`) | 10,95 kg·cm | 10,96 | **2,78 → 2,77** |
| **S1 tam kol, 500 g** (″) | 31,22 kg·cm | 31,23 | **0,97 → 0,97** |
| **S2 tam kol, yüksüz** (`tork.sonuc[1]`) | 11,16 kg·cm | 11,16 | **2,72 → 2,72** |
| **S2 tam kol, 500 g** (″) | 31,50 kg·cm | 31,50 | **0,97 → 0,97** |
| Göbek grubu ağırlık merkezi (`dirsek-analiz.json` `tork.grup.omuz_Gobek.am`) | (174,13; 8,11; −2,46) | (173,98; 7,61; −2,32) | |

S2 değişmez: durdurucu göbekte, S2 göbeği değil kolu döndürür. S1 yükü +2,5 g'lık göbek kütlesi kadar (S1 eksenine ~8 mm kolla) artar, ihmal edilir.
500 g yükte payın 1'in altında olması (0,97) önceden beri böyle (bilinen, F2 dışı).
`dirsek-analiz.json` kablo kontrolleri (`kablo.s1_gecis` en küçük boşluk 2,18 mm "Omuz gobegi"; `s2_lop` 1,9 mm; `s1_carpisma` tambur ↔ kol 0,82 mm @ S2 5°,
kaset ↔ kol 1,36 mm) önce ile aynı: diş S1 geçiş kablosuna ve S2 lopuna yaklaşmadı.
`taban-analiz.json`: yalnız göbek kütlesi/ağırlık merkezi ve `tabansiz_am` (±0,001 mm). `uygulama-ivme.json`: rampa yüksüz en küçük
`izgara_yuk_0g.a_sinir_pay15.rampa5_geri` **1,519 → 1,519**; diğer paylar −0,001 (ör. `rampa5_ileri` 1,713 → 1,712).

`py -3 planlama/d158/regresyon.py --yazma` (03:33:55; taban 02:17:55): **çıkış 0, "GEÇER"**, 10 değer "aynı" (rampa 1,519). Taban yazılmadı.
`py -3 TF/carpisma_kos.py kontrol`: çıkış 1, "kaynagi eskimis bolumler: statik, omuz, kol_sag, kol_sol, kolkol, kafa_sabit, kafa_sag, kafa_sol, taban"
(değişen: `arayuz.py`, `omuz/omuz_parcalar.py`; beklenen).

### S1 (öne-arka, −45…135): yalnız ölçüm
- `SP/f2/olc_sonra.json` `d_s1_aralik_disi`: S2 5 / 30 / 60 / 90 / 120°'de göbek + omuz kolu, S1 180 → 330° ve −60 → −210° (5° adım, her biri 31 ölçüm)
  boyunca kabuk (kaset dahil) ve omuz gövdesiyle **temas yok** (`sonuc: null`); en yakın çift baştan sona tambur ↔ S1 kaset gövdesi 0,5 mm (tasarım boşluğu).
  `omuz-analiz.json` `gobek_govde` (S1 −60…180) da temassız. Yani omuz parçaları S1'i mekanik olarak hiçbir açıda durdurmaz.
- S1'i sınırlayan tek şey **kablo**: S1 U lopu, U ucu ↔ cep temas eşiği S1 135 + 5,19° ≈ **140,2°** (`planlama/adim2/S1-kaset.md` KZ1). Ötesinde kablo
  kasete sıkışır. Bu bir mekanik durdurucu değil; kablo yük taşır.
- **F5 notu:** kodda omuz öne-arka 0…160 (`planlama/d158/servo-10-oneri.md`, F5), CAD −45…135. Kod 160'a gönderirse U lopu 140,2°'yi
  ~20° aşar. Kol ↔ kabuk çarpışması yok, kablo hasarı var. Karar taslağı 4.
- Kol zinciri ↔ kabuk (`e_kol_zinciri_x_kabuk`) S1 −60…150'de S2 4,3 ve 5°'te temassız (yukarıda).

## Karar taslakları (karar-kuyrugu.md'ye yazılmadı; kuyruğa alma yürütücünün)

**KT-F2-1: S2 alt bölgede hız sınırı ve kapanma sırası** (yazılım, `kod/` sahibi Efe; bu pakette koda dokunulmadı)
- Sorun: Durdurucu stall (emniyet 3,73) ve ≤ 1,5 rad/s yüksüz çarpmada (2,24) güvenli. Elde 500 g ile 1,5 rad/s (1,32), kaçak servo tam hız
  (0,54) ve S2 ≥ 30°'den güç kesik düşme (≤ 1,48) emniyet 2'nin altında (`SP/f2/darbe.json`).
- Öneri: (a) S2 < 20° bölgesinde açısal hız ≤ 100°/s (yüksüz; elde yük varken ≤ 50°/s), (b) güç kesilmeden önce iki kol S2 ≤ 15°'ye indirilir
  (serbest düşme sınırı 17,1° emniyet 2), (c) acil durdurma servo gücünü kesiyorsa kolların o an yüksekte olabileceği kabul edilir; dişin kırılması
  kabuk/tambur teması demektir (aşağıdaki seçenek 2).
- Etki: `kod/` hareket planlayıcısı ve kapanma betiği; CAD değişmez.

**KT-F2-2: Daha dayanıklı ya da esnek durdurucu (gerekirse)**
- Seçenekler: (a) dişe TPU (Shore 95A) ped 1–1,5 mm: rijitliği düşürür, tepe kuvvet ~√k ile azalır; pencere 3,65…5° yalnız ~0,37 mm boşluk
  bıraktığı için ped sıkışma payı yok → (b) ile birlikte. (b) S2 yazılım alt sınırını 5 → 8° çıkarmak: pencere 3,65…8 (≈ 2,3 mm), ped ve daha
  kalın diş sığar; `eklem_sinirlari.json` ve kodu etkiler (Efe), ev pozu S2 5 → 8 (kollar 3° daha açık, kabuk boşluğu artar). (c) Dişi metal
  (ör. 3 mm alüminyum köşebent, 2 × M3) yapmak: dayanım ×4 civarı, parça sayısı +3.
- Bu paket (a)–(c)'yi uygulamadı: brief 5° alt sınırı korunan değer sayıyor ve servo geri sürme sürtünmesi ölçülmeden gerekip gerekmediği belli değil.
- Ölçüm önerisi: güç kesikken DS3235'i S2 30 / 60 / 90°'den bırakıp düşme süresi (geri sürme sürtünmesi) — gerçek darbe enerjisini verir.

**KT-F2-3: S2 sıfır kalibrasyonu durdurucuya göre**
- Şu an OR:114 "S2'yi 30° konumuna getir, horn'u tak" (kol pozu yazmıyor; `servo-10-oneri.md:134`). Durdurucu 4,3°'de kesin bir mekanik referans verir.
- Öneri: horn takılırken kol dişe dayalı (S2 = 4,3°) tutulur, servo 4,3°'ye komutlanır, sonra horn takılır. Ardından S2 5 komutunda dişle
  0,34 mm boşluk görülmeli (0,3 mm sentil sığar, 0,4 sığmaz).
- Neden önemli: sıfır hatası > 0,7° olursa S2 5 komutunda kol dişe yaslanır ve servo sürekli stall'da kalır (98 N; diş emniyeti 3,73 ama servo
  ısınır, akım çeker). Eski ölçüt "±1,4°'yi aşarsa tambura değer" (`planlama/adim2/K2-s1-kontrol.md:246`) artık ±0,7° dişe dayanma ölçütü.

**KT-F2-4: S1 kod aralığı 160 ↔ CAD 135 (F5 ile ortak)**
- Kodda omuz öne-arka 0…160; CAD ve kablo kaseti −45…135, U lopu ~140,2°'de sıkışır. Mekanik durdurucu yok (omuz parçaları hiçbir S1 açısında
  çarpışmıyor). Öneri: kod S1 üst sınırı 135 (`eklem_sinirlari.json` zaten −45…135), alt −45. S1 mekanik durdurucusu istenirse ayrı paket
  (kaset U'su yerine yük taşıyan bir pim/omuz); tasarım bu pakette yok.

## P2.2 Çakışma taraması (dokuz bölüm, tek koşu kimliği, omuz en son)
`py -3 SP/f2/carp_zincir.py 20261109-033441 statik kol_sag kol_sol kolkol kafa_sabit kafa_sag kafa_sol taban omuz` (çıktı `SP/f2/carp_zincir.out`,
özet `SP/f2/carp_zincir_20261109-033441.json`, bölüm logları `%TEMP%\carpisma-<bölüm>.log`). Yöntem `carpisma_kos.kos()` ile aynı (her bölüm ayrı
freecadcmd, `CARPISMA_BOLUM` + `CARPISMA_KOSU`). Ek olarak her bölümden önce boş bellek ≥ 2 GB ve FreeCAD süreci 0 denetimi yapıldı, boş bellek 5 dk'da bir
`SP/f2/bellek.log`'a yazıldı, başarısız bölümde durulacaktı (yeniden başlatma yok). Koşu boyunca izlenen kaynak dosyalara dokunulmadı.

| Bölüm | Saat | Süre | Tepe bellek | Boş bellek başta → sonda | rc |
|---|---|---|---|---|---|
| statik | 03:34:41–03:35:57 | 76 s | 733 MB | 5,38 → 5,39 GB | 0 |
| kol_sag | 03:35:57–03:39:59 | 241 s | 747 MB | 5,39 → 5,37 GB | 0 |
| kol_sol | 03:39:59–03:43:52 | 233 s | 745 MB | 5,37 → 5,37 GB | 0 |
| kolkol | 03:43:52–03:44:50 | 58 s | 198 MB | 5,37 → 5,36 GB | 0 |
| kafa_sabit | 03:44:50–03:47:33 | 163 s | 746 MB | 5,36 → 5,34 GB | 0 |
| kafa_sag | 03:47:33–03:55:33 | 480 s | 624 MB | 5,34 → 5,38 GB | 0 |
| kafa_sol | 03:55:33–04:03:25 | 472 s | 627 MB | 5,38 → 5,33 GB | 0 |
| taban | 04:03:25–04:04:52 | 87 s | 742 MB | 5,33 → 5,34 GB | 0 |
| **omuz** | 04:04:52–07:29:41 | **12.289 s (3 sa 25 dk)** | 740 MB | 5,34 → 4,93 GB | 0 |

Omuz koşusunda 5 dk'lık boş bellek kayıtları (`SP/f2/bellek.log`, 04:09:52 … 07:24:57): en düşük **4,51 GB** (07:14:57), en yüksek 4,92 GB;
freecadcmd çalışma kümesi 427 → 442 MB. Bellek sorunu ya da süreç ölümü olmadı.

`py -3 TF/carpisma_kos.py birlestir` (07:30, çıkış 0): "tek kosu: True | eksik: [] | TOPLAM cakisma 364 eklem araliginda 0".
`py -3 TF/carpisma_kos.py kontrol` (çıkış 0): "carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni" → **eskimiş bölüm 0**.

`TF/carpisma-sonuc.json` önce (`SP/f2/once/carpisma-sonuc.json`) ↔ sonra:

| Değer | Önce | Sonra |
|---|---|---|
| `tek_kosu` | false (omuz 03.11 koşusundan; kaynak aynı: False) | **true** (koşu 20261109-033441, 03:35:44 … 07:29:41) |
| `ev_pozu_cakisma` (S1 0, S2 5) | [] | **[] (0)** |
| `ev_pozu_kesisen_cift` (sınır kutusu kesişen çift, çakışma değil) | 819 | 821 (+2: dişli göbeğin kutusu, iki yan) |
| `ev_pozu_cakisma_s2_0` (bilgi, S2 0 mekanik sıfır) | tüp ↔ S1 kaset kapağı 6,42 mm³ ×2; M5 cıvata ↔ dirsek çatalı 20,53 ×2 | aynı |
| `toplam.cakisma` / **`eklem_araliginda`** | 364 / 0 | 364 / **0** |
| `toplam.kafa`, `toplam.taban` | 6 / 0; 0 / 0 | aynı |
| `tarama.omuz_sag/sol.cakismalar` | — | aynı pozlar; S2 −10…−20 pozlarında (aralık dışı) ortak hacimler değişti (ör. (20, −15) 1832,8 → 2151,1 mm³), çakışma sayısı aynı |
| `kol_kol`, `taban_tarama`, `arayuz_uyumu`, `ayrilmis_bolge` | — | aynı (süre ve koşu alanları hariç) |
| `kol_tarama`, `kafa_tarama` | — | yalnız `aday` / `tam_olcum` sayıları (+8…+1510; dişin kutusu); çakışma sayıları aynı |
| `kutle_toplam_g`; `agirlik_merkezi` | 25.715,6; (−0,03, 528,46, −9,26) | 25.720,5; (−0,03, 528,59, −9,25) |

## Omuz ve iskelet regresyonları
İkisi de `REG_ETIKET=sonra` ile `SP/f2/fc.sh` üzerinden koşuldu (once.json'a dokunulmadı, referans zorlanmadı).
- **Omuz:** `TF/omuz/omuz_regresyon.py` (07:30:21–07:31:07, 46 s, rc 0, boş bellek 4,82 GB; log `SP/f2/omuz_regresyon.log`) → `TF/omuz/regresyon/sonra.json`,
  `fark.json`. Sonuç **"FARK VAR"**, referans `once.json` 14 Ekim (C1 öncesi, 70 parça).
  - Farklı çıkan satırlar: parça 70 → 75, Kol-Gövde boşluğu 4,0 → 6,29, kol_gobek çakışan poz 8 → 11, tork en büyük fark 0,394 kg·cm, BOM 16 → 17.
  - **Bu satırların hiçbiri F2 kaynaklı değil.** F2 öncesi `SP/f2/once/omuz-analiz.json` ile şimdiki karşılaştırıldı:
    - parça sayısı 75 = 75, `statik` 0 = 0, boşluklar aynı
    - `kol_gobek` dolu S2 anahtarları aynı 11 ({−20…0} ve {125…150}), `kol_govde` 94 = 94
    - S2 en büyük tork 6,12 = 6,12, BOM satırı aynı
  - Repodaki eski `sonra.json` (`SP/f2/once/omuz-regresyon/sonra.json`) 3 Kasım'dan, 66 parçalık modelden kalmaydı.
- **İskelet:** `TF/iskelet/iskelet_regresyon.py` (07:31:08–07:31:10, 2 s, rc 0) → `TF/iskelet/regresyon/sonra.json`, `fark.json`. Sonuç **"FARK VAR"**,
  referans `once.json` 8 Ekim (V3).
  - Yalnız **"Govde diregi"** farklı: hacim 581.402 → 810.186 mm³, kütle 1569,8 → 2187,5 g, kutu farkı 315 mm = `arayuz.UZAMA` (1,58 m uzatması),
    toplam ağırlık merkezi y 314,5 → 418,6.
  - Parça 59 = 59, katı/geçerlilik aynı, parça içi çakışma 0, bağlantı 12 aynı, ayrılmış bölge ihlali 0.
  - İskelet `OMUZ["durdurucu"]`'yu kullanmıyor (grep); fark F2 kaynaklı değil.
- **Değerlendirme:** İki regresyon da "F2 kaynaklı fark yok" anlamında geçer. Betiklerin kendi ölçütüyle (eski referansa göre) sonuç "FARK VAR".
  Referansları güncellemek (`REG_ETIKET=once`) brief'te yok ve tabanı zorlamak olurdu; yapılmadı (açık kalan 5).

## Regresyon (normal mod)
`py -3 planlama/d158/regresyon.py` (07:32:32; taban 02:17:55): **çıkış 0, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)"**. 10 değerin hepsi "aynı":
- boy 1580
- çakışmalar 0 / 0 / 0 / 0
- rampa yüksüz 1,519
- tilt 3,64, pan 2,21
- mik–hoparlör 574,3
- SY8205 × USB 0

Betik çıkış 0'da kendi kuralıyla `regresyon-son-kosu.json` ve `regresyon.json`'u yazdı (değerler aynı, `onceki_tarih` 02:17:55).

## Değişen dosyalar (F2)
**Elle değişen kaynak:**
- `tasarim/freecad/arayuz.py`: yalnız OMUZ bloğu (`durdurucu` + yorum)
- `tasarim/freecad/omuz/omuz_parcalar.py`: durdurucu dişi

**Betiklerin yeniden ürettikleri:**
- Omuz: `TF/omuz/omuz-analiz.json`, `omuz-baski.json`, `omuz-montaj.FCStd`, `omuz-montaj.step`, `stl/omuz-gobegi.stl`, `regresyon/sonra.json`, `regresyon/fark.json`
- Dirsek: `TF/dirsek/dirsek-analiz.json`, `dirsek-montaj.FCStd`, `dirsek-montaj.step`
- Taban: `TF/taban/taban-analiz.json`, `taban-montaj.FCStd`, `taban-montaj.step`
- Montaj: `TF/montaj/montaj-analiz.json`, `robot-montaj.FCStd`, `robot-montaj.step`, `robot-bom.csv` (Omuz gobegi 118,5 → 123,4 g, 2 adet)
- Kafa yerleşim: `KY/uygulama-ivme.json`
- Çakışma: `TF/carpisma-bolum/*.json` (9), `TF/carpisma-sonuc.json`
- İskelet: `TF/iskelet/regresyon/sonra.json`, `fark.json`
- Regresyon: `planlama/d158/regresyon.json`, `regresyon-son-kosu.json`

**Yeni:** `planlama/d158/F2-gunluk.md`, `F2-durdurucu-yakin.png`, `F2-durdurucu-kesit.png`.

**F2'den önce de değişik olanlar (bu paketin değil):** `planlama/dongu-158.md`, `TF/kabuk/gorsel/*.png` (13), `TF/montaj/yerlesim-kontrol.json`.

**Dokunulmayanlar:** `kod/` (`eklem_sinirlari.json` S2 5…120 aynı), `kabuk/` kaynakları, karar kuyruğu, F3a/F4a dosyaları, `elektrik.md`, `maliyet.json`, README/OZET.

## Açık kalanlar
1. Darbe hesabı kaba: servo geri sürme sürtünmesi ve rotorun dişliler üzerinden yansıyan eylemsizliği ölçülmedi (KT-F2-1; KT-F2-2'deki ölçüm önerisi).
2. Kaçak tam hızda ve S2 ≥ 30°'den güç kesik düşmede diş emniyeti < 1,5 (KT-F2-1/2). Yazılım tarafı Efe'de.
3. S1 kod aralığı 0…160, CAD 135; kablo U'su ~140,2°'de sıkışır (F5, KT-F2-4).
4. S2 sıfır kalibrasyon talimatı (OR:114) durdurucuya göre yeniden yazılmalı (KT-F2-3). Montaj talimatına dokunulmadı.
5. Omuz ve iskelet regresyon referansları (`once.json`) eski. Betikler "FARK VAR" diyor, F2 kaynaklı fark yok. Referans yenileme kararı yürütücüde.
6. `omuz-baski.json` `egim_yuz` 4 yüz (x 183/193, y 33–37): F2 öncesi geometride de var ama 29 Ekim koşusunda raporlanmamış. Nedeni incelenmedi.
7. Yeniden üretilmeyenler: `TF/omuz/rapor.html`, `TF/kabuk/rapor.html`, `TF/taban/rapor.html` ve `planlama/y2/Y2b-ivme.json`. Raporlardaki çakışma
   uyarıları güncel sonuca göre değişebilir; kilit tablosunda kabuk ve taban F2'nin değil.
8. F3a girdileri (`montaj-analiz.json`, `dirsek-analiz.json`, `uygulama-ivme.json`) küçük değişti (kütle +4,9 g, paylar ±0,001–0,01). F3a'ya bilgi verilmeli.
9. Dişin 4,3° yüzü baskıda 0,2 mm katmanla ≈ 0,015 mm basamaklı çıkar. İlk montajda S2 5°'te sentille 0,3 mm boşluk kontrolü önerilir.
10. B kontrolü (F2-kontrol.md): "horn/dişli yük almıyor" yalnız tork için geçerli; darbede kuvvetin ~%88'i S2 mafsalına radyal gider, rotor eylemsizliği dişliden geçer (B-1). Emniyetler kol esnekliği ve rijitlik varsayımına bağlı (1,5 rad/s yüksüz 1,22…2,57) ve kök +x iç köşesinin gerilme yığılması hesapta yok (B-2): kök yarıçapı/pahı sonraki pakette. Açık kalan 6 kapandı: eğik yüzler C3 somun cepleri; "önce" baskı JSON'u 29.10 C1–C3 öncesi (B-4).
