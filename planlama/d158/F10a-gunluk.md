# F10a günlüğü: rehber arayüzü küçükleri (P10.1), 11.11.2026

Brief: `planlama/d158/F10a-brief.md`. Ahmet (10.11): "tıkladığım parçanın ismi gözüküyor ancak seçtiğim zaman farklı bir renkte
gözükse iyi olur"; kabuk adımlarında (31, 33) "neyi nereye monte ediliyor pek anlaşılmıyor". Yalnız sayfa kodu değişti; `rehber/veri/`
ve model değişmedi. FreeCAD çalıştırılmadı; `rehber_uret.py` yalnız `--veri-yok` ile koşuldu. Commit yok (kayıt ajanı C atar).

## Kabul ölçütleri

| Ölçüt | Ölçülen | Durum |
|---|---|---|
| `kontrol.json` 50/50, konsol 0, 1192 ↔ 1192 | 50/50, konsol 0, 1192 ↔ 1192, her parça tek adımda: evet (00:49) | geçti |
| denetim 0 | ASCII kalıntı 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 40, yasak 0 | geçti |
| 360 px taşma 0 (`rehber_uret` 7 adım; `F10a-dogrula` 50 adım) | rehber_uret 7 × 0 px; F10a-dogrula 50 adımda en çok 0 px, küçük görünüm × panel kesişimi 0 | geçti |
| PDF sayfa sayısı ve en küçük yazı değişmedi (önce 54 sayfa, 8,1 pt) | 54 sayfa, en küçük 8.1 pt (DOM ve PDF), taşan 0 | geçti |
| Seçim sınaması 6/6 (kabuk, kablolama, tezgâh adımı dahil) | 6/6 (12 tezgâh, 17 kablolama, 31 / 33 / 34 kabuk, 44 tezgâh); ek: Esc, önceki adım parçası, şema, patlat / tak, kısayollar hepsi geçti | geçti |
| Ağsız açılış: dış istek 0, konsol 0 | istek 18 (hepsi file://), dış 0, konsol 0, model 1192 mesh (3 sayfa) | geçti |
| Kadraj: hiçbir adımda yeni parça kare dışında değil | taşan adım önce 0 → sonra 0; taşan parça 0; araç / lejant / küçük görünüm altında kalan yeni parçalı adım 0 | geçti |
| Kadraj: yeni parça alan oranı ortancası öncekinden büyük | ortanca 0.1733 → 0.4013 (ortalama 0.164 → 0.376); 50 adımın 50'inde büyüdü, küçülen 0 | geçti |
| Oranı 0,05 altında kalan adımlar gerekçeli | 1 adım (25 E2a, 0,0307) | listelendi (aşağıda) |
| Küçük görünüm 50/50 | 1400 px 50/50, 360 px 50/50 | geçti |
| `F9b-dogrula` 0, `carpisma_kos kontrol` 0, regresyon 10/10 | F9b 0 (hata 0), carpisma_kos kontrol 0 (17 dosya kayıtla aynı), regresyon 10/10 aynı, GEÇER | geçti |
| `rehber/veri/` değişmedi (`git diff --quiet HEAD -- rehber/veri`) | çıkış 0 | geçti |

## Yapılanlar

### 1. Seçim vurgusu (`rehber/app.js`, `stil.css`)
- Tıklanan parça **açık yeşil `#7cfc00`** (öz ışıma `#3f8f00`), aynı kalemin o adımdaki öbür kopyaları **soluk yeşil `#cdf7a6`**.
  Yeşil seçildi çünkü sınıf renklerinde (turuncu, lacivert, camgöbeği, mavi, mor, koyu turuncu, sarı, kırmızı) ve kablo / şema
  renklerinde yok; ilk aday macenta, şema rengi `#e84393` ile çakıştığı için bırakıldı. FreeCAD'in seçim rengi de yeşil. İki temada
  okunuyor (`F10a-goruntu-31-koyu-secim.png`, `F10a-goruntu-44-acik-secim.png`).
- Seçilen parçaların bir de "röntgen" silueti var (aynı geometri, derinlik testi kapalı, %30 opak yeşil): kabuğun ya da çatalın içinde
  kalan parça da önündekinin arkasından görünür (44'te rulman çatal içinde, 31'de QLED kabuk içinde).
- Kopya kümesi: panel satırının `ids` listesi; parça önceki bir adımdansa o adımın satırı (`satirBul`). Satırı olmayan parça (K1
  kabloları) tek başına.
- Boş alana tıklama ve **Esc** temizler; adım değişince (`git`) temizlenir. Önceki adımın gri parçası seçilebilir. Saydam kipte ışın
  önce bu adımın parçalarını verir (saydam kabuğun arkasındaki yeni parça tıklanabilsin).
- Panelde parça ve bağlantı elemanı satırları (`data-satir="p:i" / "b:i"`) ve kablo kancasındaki kablo / şema satırları tıklanır; aynı
  vurgu gelir, satır yeşil şeritle işaretlenir; aynı satıra ikinci tıklama temizler. Modelde tıklanan parçanın satırı da işaretlenir.
- Kablo şeması tüpleri tıklanır (ışın süzgeci `userData.sema` da kabul eder): etikette ad, adım, boy; tüp vurgulu.
- Vurgu kalıcı değil: `uygula()` asıl malzemeyi `userData.mat0`'da tutar, temizlenince geri konur; uygula her çağrıldığında önce asıl
  malzeme atanır, vurgu sonra.
- Etiket araç çubuğunun altına alındı (`.sahne-ust` sütunu); eskiden sağ üstteydi, uzayan araç çubuğuyla çakışırdı.

### 2. Öncekiler opak / saydam / gizli + patlat ve sıralı tak
- "öncekileri gizle" kutusu üç seçenekli gruba döndü: **opak / saydam / gizli** (kısayol **O** ya da **Ö**, sırayla döner; seçim yerel
  kayıtta). Saydam: önceki parçalar %18 opak (kablolar %20), derinlik yazmaz.
- **⇱ patlat (P)**: adımın yeni parçaları uçuş başlangıcında (`taban + u·d`, alt montajda `ub`) bekler; uçuş yönü olmayanlar (kablo
  parçası, şema) gizlenir; kamera yerindeki ve patlak konumdaki köşeleri birlikte kadraja alır. İkinci basış **⇲ topla**.
- **▶ tak (Boşluk)**: panel sırasıyla bir satır 0,9 s'de yerine gider. Sıra: bağlanan alt montaj (varsa) → parça satırları → bağlantı
  elemanı satırları → kablo şemaları. Takılan satır seçili (yeşil) ve panelde işaretli; etikette "Sıra k / n". **Shift+Boşluk** son
  satırı geri çıkarır. Patlak değilken Boşluk önce patlatır. Düğmede "tak k/n".
- Saydam kipte, bu adımda daha önce takılmış satırlar da saydamlaşır (o an takılan ve bekleyenler opak): 31'de yüz kabuğu takıldıktan
  sonra QLED, tırnaklar ve vidalar kabuğun içinde görünür (`F10a-goruntu-31-koyu-saydam-patlat.png`), 33'te etek bantları
  (`F10a-goruntu-33-koyu-saydam-patlat.png`).
- **↻ uçuş (R) korundu**: adım açılınca ve R'de adımın bütün parçaları birlikte uçar (hızlı genel bakış); patlat / tak bunun yanında
  atölye kipi. Gerekçe: adım değiştirirken her seferinde satır satır beklemek yavaş; tek kısayolla ikisi de var. R ve adım değişimi
  patlak kipi kapatır.
- Uçuş yönü verisi değişmedi (yalnız zamanlama ve sıra). URL'den: `?onceki=saydam`, `?patlat=1&tak=N` (görüntü almak için).

### 3. "Robotun neresi" küçük görünümü ve kadraj
- Sahnenin sağ altında küçük görünüm (aynı tuvalde ikinci görüş alanı, `setScissor`): bütün robot soluk gri (%20, derinlik yazmaz),
  bu adımın yeni parçaları (robot adımında `simdi` + `alt`, tezgâh adımında o alt montajın bu adımdaki parçaları, robottaki son
  yerinde) **kehribar `#ffb000`**; tezgâhta aynı alt montajın önceki parçaları biraz koyu gri. Vurgu saydam geçişte soluk robottan sonra
  çizilir (renderOrder 10): içeride kalan parça soluk katmanların altında kaybolmaz. Vurgulu kutuya CSS halka; 6 px'ten küçük kalan
  parçanın (horn, burç) yerine kehribar nokta (parça başına). Kamera yönü adımın ana kamera yönüyle aynı (arka / alttan dahil).
- Genişlik `clamp(84px, 14vw, 170px)`, en-boy 3:4. **M** ya da başlıktaki × ile kapanır, ▣ konum düğmesiyle açılır (yerel kayıtta).
  Telefonda başlık yazısı gizli, lejant küçülür. Yazdırılabilir sürümün görüntüsünde (`?sahne=1`) de açık (kâğıtta döndürme yok;
  kapat düğmesi gizli).
- Kadraj (`kameraYerlestir`): eski küre formülü (`max(70, r0·1,1, min(rg·0,3, r0·2,2))`, bağlam için 2,2 kata kadar açılıyordu) yerine
  yeni parçaların yerel sınır kutusu köşeleri (parça başına 8, dünya koordinatında) kameraya izdüşürülür; uzaklık ve hedef yinelemeli
  bulunur, köşeler araç çubuğu, lejant ve küçük görünüm dışındaki alana %3 payla sığar. Küçük görünüm için sağ sütun ya da alt şerit
  ayrılır, hangisi daha büyük görüntü veriyorsa o. En yakın uzaklık: hedef derinliğinde ~90 mm yükseklik. Kamera yönü ipuçları
  değişmedi (ön-sağ-üst; B1 / B1a alttan; `kamera: "arka"` arkadan). Bağlam artık küçük görünümde.

### 4. İnternetsiz açılma
- `rehber/vendor/three-0.160.0-paket.min.js`: npm `three@0.160.0` paketinden (sürüm CDN'deki ile aynı) three + `GLTFLoader` +
  `OrbitControls` + `toCreasedNormals`, esbuild 0.20.2 ile tek klasik IIFE betiği (`window.LALE_UC`); kod değiştirilmedi, giriş dosyası
  ve komut betiğin başındaki yorumda. `REVISION "160"`. Lisans `rehber/vendor/LICENSE-three.txt` (MIT, paketteki LICENSE).
  Gerekçe: `file://` altında ES modülü yerel dosyadan yüklenemiyor; `rapor/vendor/three.min.js` r145 ve eklentisiz (orkestratör
  denetim notu). Paketleme indirme ve derleme scratchpad'de yapıldı (yalnız paket adı ve sürümü).
- `index.html`: import map ve modül betiği kalktı; `vendor/…` + `app.js` + `RehberBaslat(window.LALE_UC)`. `rehber/` içinde CDN
  bağlantısı 0 (`F10a-dogrula` taraması; vendor'da yalnız CDN alan adları arandı: 0).
- `rehber/yazdir.html` 3B kullanmıyor (PNG görüntü); değişmedi.
- Demo (`tasarim/cad/viewer-template.html`, paket dışı): three.js r128'i `cdnjs.cloudflare.com`'dan klasik betikle alıyor (satır 283),
  modeli `../rehber/veri/*.js`'ten; internetsiz 3B açılmaz ("3B görünüm açılamadı" yedeği gösterilir). Yerel paket istenirse
  `../rehber/vendor/` kullanılabilir ama r128 → 0.160 API farkı denenmeli. Dokunulmadı.

### 5. Doğrulama betiği `planlama/d158/F10a-dogrula.py` → `F10a-dogrula.json`
Chrome DevTools protokolü (websockets), `file://`. "Önce" = HEAD'deki `rehber/app.js`, `index.html`, `stil.css` geçici klasörde
(veri ve three.js aynı 0.160 yerel paket; app.js'e kamerayı okumak için tek satır). Sınama kancası `window.RehberTest` (salt okuma
+ patlat / tak çağrıları; davranışı değiştirmez).
- Kadraj: 1400 × 900, `?cekim=1`, açık tema; yeni parçaların bütün vertex'leri izdüşürülür; oran = kareye kırpılmış ekran kutusu / kare
  (sahne alanı 1000 × 796); taşan = bir vertex'i kare dışında ya da kamera arkasında kalan yeni parça.
- Küçük görünüm: `readPixels` ile alan içinde arka plandan farklı (> 200) ve kehribar tonlu (> 0) piksel; 360 px'te (mobil öykünme)
  ayrıca yatay taşma, sahne içinde olma, panelle kesişme.
- Seçim: gerçek fare olayları (`Input.dispatchMouseEvent`), tuşlar `Input.dispatchKeyEvent`.

## Doğrulama sayıları
Son koşu 11.11 00:49 (`rehber_uret.py --veri-yok`) ve ardından `F10a-dogrula.py` (380 s). Seçim ayrıntısı:

| Adım | Tür | Parça tıklama (vurgulu / satır ids) | Panel satırı | Boş tık | → sonra |
|---|---|---|---|---|---|
| 12 B5a | tezgah | 8 / 8 | 8 / 8 | 0 | 0 |
| 17 K1 | kablolama | 1 / 1 | 1 / 1 | 0 | 0 |
| 31 E4 | robot | 11 / 11 | 17 / 17 | 0 | 0 |
| 33 F1 | robot | 22 / 22 | 22 / 22 | 0 | 0 |
| 44 H0c | tezgah | 8 / 8 | 8 / 8 | 0 | 0 |
| 34 F2 | robot | 32 / 32 | 34 / 34 | 0 | 0 |

Küçük görünüm ilk koşuda 1400 px 48/50, 360 px 43/50 kaldı (21, 25 ve 360'ta 10, 26, 28, 45, 46: horn / burç alt piksel ya da üst üste soluk katmanların altında). Düzeltme: vurgu soluk robottan sonra çizilir + 6 px altı parçaya nokta. Sonra 50/50 ve 50/50.

Kadraj, adım başına yeni parça alan oranı (önce HEAD → sonra):

| Adım | Kod | Önce | Sonra |
|---|---|---|---|
| 0 | 0 | 0.1651 | 0.2131 |
| 1 | A1 | 0.2076 | 0.4391 |
| 2 | A2 | 0.0516 | 0.0625 |
| 3 | A3 | 0.0861 | 0.3898 |
| 4 | B1a | 0.2031 | 0.5125 |
| 5 | B1 | 0.2035 | 0.5125 |
| 6 | B2a | 0.2657 | 0.4674 |
| 7 | B2b | 0.2413 | 0.3900 |
| 8 | B2 | 0.2877 | 0.4783 |
| 9 | B3 | 0.2371 | 0.5302 |
| 10 | B4 | 0.2562 | 0.5223 |
| 11 | C0 | 0.2322 | 0.3702 |
| 12 | B5a | 0.2320 | 0.4667 |
| 13 | B5 | 0.2256 | 0.4667 |
| 14 | B6a | 0.2433 | 0.4042 |
| 15 | B6 | 0.1773 | 0.4041 |
| 16 | B7 | 0.0470 | 0.3667 |
| 17 | K1 | 0.1556 | 0.3981 |
| 18 | C1 | 0.1904 | 0.2111 |
| 19 | D1a | 0.2229 | 0.4463 |
| 20 | D1b | 0.2097 | 0.4032 |
| 21 | D1c | 0.1513 | 0.3332 |
| 22 | D1 | 0.1471 | 0.4452 |
| 23 | E1a | 0.2522 | 0.4021 |
| 24 | E1 | 0.0579 | 0.4128 |
| 25 | E2a | 0.0116 | 0.0307 |
| 26 | E2b | 0.0494 | 0.3714 |
| 27 | E2c | 0.0296 | 0.2654 |
| 28 | E2 | 0.0498 | 0.2650 |
| 29 | E3a | 0.2141 | 0.4006 |
| 30 | E3 | 0.0704 | 0.4006 |
| 31 | E4 | 0.2090 | 0.5138 |
| 32 | K2 | 0.0996 | 0.1148 |
| 33 | F1 | 0.1437 | 0.3511 |
| 34 | F2 | 0.1751 | 0.2556 |
| 35 | F3 | 0.2413 | 0.5406 |
| 36 | F4 | 0.1357 | 0.4108 |
| 37 | G0 | 0.1426 | 0.3592 |
| 38 | G1 | 0.1172 | 0.3592 |
| 39 | G2 | 0.0994 | 0.4145 |
| 40 | G3 | 0.2082 | 0.4896 |
| 41 | G4 | 0.1105 | 0.4236 |
| 42 | H0a | 0.2015 | 0.4818 |
| 43 | H0b | 0.1386 | 0.3069 |
| 44 | H0c | 0.1715 | 0.3700 |
| 45 | H0d | 0.1206 | 0.2511 |
| 46 | H0e | 0.1302 | 0.2742 |
| 47 | H0f | 0.2070 | 0.4462 |
| 48 | H1 | 0.2538 | 0.5243 |
| 49 | F5 | 0.1220 | 0.1331 |

### Oranı 0,05'in altında kalan adımlar
- **25 E2a (pan servosu ortaya, horn): 0,0307** (önce 0,0116). Yeni parça tek horn (~25 mm); kadrajın en yakın sınırı (hedef derinliğinde ~90 mm yükseklik) devreye giriyor. Daha yakına gitmek görüntüyü düzeltmez: horn yuvanın / gövde halkasının içinde, bu kamera yönünden görünmüyor (denetim notunda GİZLİ, puan 1). Çözüm kamera yönü / alt adım verisi (F10d sonrası); bugün saydam kip ve küçük görünümdeki kehribar nokta yeri gösteriyor.
- Önce (HEAD) 0,05 altında 5 adım vardı (25, 27, 16, 26, 28); sonra yalnız 25.

## Komutlar ve çıkış kodları
| Komut | Çıkış | Not |
|---|---|---|
| `npm install three@0.160.0 esbuild@0.20.2 --ignore-scripts` (scratchpad) | 0 | yalnız paket adı ve sürümü |
| `esbuild giris.js --bundle --format=iife --minify --target=es2019 --legal-comments=none` (scratchpad) | 0 | 705 kB, sonra başlık yorumuyla `rehber/vendor/` |
| `py -3 -X utf8 planlama/d158/F10a-dogrula.py` (1. koşu) | 2 | küçük görünüm 48/50 + 43/50; öbürleri geçti |
| `py -3 -u -X utf8 planlama/d158/F10a-dogrula.py` (2. koşu, düzeltmeden sonra) | 0 | hepsi geçti |
| `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (1.) | 0 | 50/50, PDF 54, 8,1 pt |
| `py -3 -X utf8 planlama/d158/F9b-dogrula.py` | 0 | |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | |
| `py -3 planlama/d158/regresyon.py --yazma` | 0 | 10/10 aynı |
| (`?sahne=1` görüntüsünde küçük görünüm açıldı, ardından son zincir) `rehber_uret.py --veri-yok` → `F10a-dogrula.py` → `F9b-dogrula.py` → `carpisma_kos.py kontrol` → `regresyon.py --yazma` | 0, 0, 0, 0, 0 | 00:49; tablodaki sayılar bu koşudan |
| `git diff --quiet HEAD -- rehber/veri` | 0 | |

## Bakılan kareler (Read ile açıldı)
`F10a-goruntu-12-acik-once/sonra`, `17-koyu-once/sonra`, `33-acik-once`, `33-koyu-saydam-patlat`, `44-acik-secim`, `44-koyu-sonra`, `31-koyu-secim`; geliştirme sırasında scratchpad'de 31 (açık, koyu, saydam + patlat, seçim), 33 saydam + patlat (açık, koyu), 360 px 31 (koyu), `?sahne=1` 38 ve 25; `rehber/goruntu/adim-38.png`. Gözlem: 12 ve 17'de önce karesinde yeni parçalar karenin ortasında küçük, sonra kareyi dolduruyor (44'ün yalnız sonra karesine
bakıldı: iki kol yan yana, ikisi de kadrajda); 31 / 33 opakta tek turuncu blok kalıyor (yeni parça kabuğun kendisi), saydam + tak ile içerisi görünüyor; seçim yeşili açık ve koyu temada okunuyor, röntgen silueti çatal içindeki rulmanı gösteriyor. Görüntüler: adım 12, 17, 31, 33, 44 × açık / koyu × önce / sonra = 20, + 31 ve 33 saydam + patlat, + seçim 31 koyu ve 44 açık = 24 PNG (`planlama/d158/F10a-goruntu-*.png`).

## Dokunulan dosyalar (commit listesi)
Kaynak: `rehber/app.js`, `rehber/index.html`, `rehber/stil.css`, yeni `rehber/vendor/three-0.160.0-paket.min.js`, `rehber/vendor/LICENSE-three.txt`.

Üretici çıktısı (`rehber_uret.py --veri-yok`): `planlama/rehber/kontrol.json`, `planlama/rehber/goruntu/*.png` (adim-00…49, telefon-360-*), `planlama/rehber/Lale-montaj-rehberi.pdf`, `rehber/goruntu/adim-00…49.png` (yazdırılabilir sürümün 3B kareleri; yeni kadraj + küçük görünüm).

Paket: `planlama/d158/F10a-dogrula.py`, `F10a-dogrula.json`, `F10a-gunluk.md`, `F10a-goruntu-*.png` (24).

Dokunulmadı: `rehber/veri/`, `rehber/yazdir.html`, `tasarim/freecad/rehber/rehber_uret.py` (yeni düğmeler başsız kontrolü bozmadı), F10b alanı.

## Açık kalanlar ve brief dışı gözlemler
- `README.md:28` ve `:138` "3B için internet gerekir" diyor; `planlama/rehber/R-gunluk.md:98` ve `:117` da CDN diyor. İkisi de bu paketin
  yazma alanı dışında: kayıt ajanı / orkestratör güncellemeli (rehber artık internetsiz; demo hâlâ CDN).
- Adım 25 (E2a pan hornu) sıkı kadrajda da görünmüyor: horn yuvanın / gövde halkasının içinde (denetim notunda GİZLİ). Kadraj değil
  kamera yönü sorunu; alt adım / kamera verisi (F10d ya da sonrası) çözer. Saydam kipte ve küçük görünümde yeri görünüyor.
- Patlatılmış konumlar verinin `u·d`'sinden: E4'te kabuklar ve QLED birbirine yakın uçuyor, F1'de bantlar 630-830 mm açılıyor
  (kare genişliyor). Yön / uzaklık düzeltmesi F10d'de.
- `kontrol.json` "her parça tek adımda" denetimi hâlâ yalnız `visible` bayrağına bakıyor (perdelenme ölçülmüyor; denetim notu §1).
- Sıkı kadrajın bedeli: yeni parça çok küçükse (horn, burç) ana görünüm yakın plan, bağlam yalnız küçük görünümde. ⌖ görünüm (V) aynı
  kadrajı verir; uzaklaşmak için fare tekerleği.

## Düzeltme turu 1 (11.11.2026)

Girdi: `planlama/d158/F10a-kontrol.md` (DÜZELTME GEREKLİ; B-1 engelleyen, B-3 ve B-4 bu turda). B-2 ve B-5 bu turda düzeltilmedi
(aşağıda "Açık kalanlar"). Commit yok. FreeCAD yok; `rehber_uret.py` yalnız `--veri-yok` ile koşuldu. Deney betikleri, sayfa kopyaları
ve ara görüntüler scratchpad'de (`scratchpad/f10a-d1/`), depoya kopyalanmadı.

### B-1: yazdırma karelerinin boş çıkması

**Kök neden (ölçümle):**
- Mekanizma: `--screenshot` görüntüyü almadan hemen önce pencereyi yeniden boyutlandırıyor. `ResizeObserver` -> `boyut()` ->
  `renderer.setSize()` tuvalin çizim tamponunu temizliyor; `boyut()` yeniden çizimi `ciz()` ile bir sonraki kareye (rAF) bırakıyordu.
  `ResizeObserver` boyamadan hemen önce koştuğu için o kare temizlenmiş tuvalle boyanıyor; görüntü bu kareden alınırsa boş.
- Kanıt 1 (zaman çizelgesi): sayfanın ölçüm kopyasında `render`, `setSize`, `boyut`, `hazir` olayları zamanlarıyla görüntünün üstüne
  yazıldı (8 adım x 2 = 16 kare, 3'ü boş). Bütün karelerde son olaylar ~25,6 s'de (sanal zaman bütçesinin sonu) `boyut | setSize
  1200x720` (önceki boyut 1182x624). Dolu karelerde ardından aynı anda `render` var; **boş karelerin üçünde de son olay `setSize`, sonrasında
  `render` yok**. HEAD sayfasının aynı ölçüm kopyasında da aynı son `setSize` var, ardından `render` geliyor.
- Kanıt 2 (ikiye bölme; aynı komut, 1200 x 720, `?adim=N&cekim=1&sahne=1&tema=light`, ölçü aşağıda):

  | Sayfa | Kare | Boş |
  |---|---|---|
  | Düzeltme öncesi çalışma ağacı (3 koşu) | 5 + 50 + 100 | 3 + 7 + 2 |
  | Aynı sayfa, küçük görünüm kapalı (`&mini=0`) | 50 + 50 | 0 + 0 |
  | HEAD sayfası (aynı 0.160 yerel paket, klasik betik) | 50 | 0 |
  | Düzeltme öncesi + yalnız `boyut()`'ta eşzamanlı `render()` | 150 (3 tur) | 0 |

  Betik yükleme biçimi (modül -> klasik betik) etkili değil: HEAD + yerel klasik paket 0 boş. Boşluğu açığa çıkaran değişiklik küçük
  görünüm: `?sahne=1`'de açık, aynı tuvalde ikinci bir çizim geçişi (bütün robot, saydam). Kapatınca 100 karede 0. Çizim pahalılaşınca
  rAF çizimi görüntü alınmadan yetişemiyor (yorum; kare süresi ayrıca ölçülmedi). Asıl kusur iki sürümde de var olan "temizle, sonra
  bir kare sonra çiz" deseni; HEAD'de tek çizim geçişiyle yarış görülmedi (bu turda 0 / 50, kontrolde 0 / 65).
- Düzeltme: `rehber/app.js:562-572` `boyut()` `setSize`'dan sonra aynı karede `render()` çağırıyor (eskiden `ciz()`).

**Kalıcı koruma** (`tasarim/freecad/rehber/rehber_uret.py`, yalnız yazdırma karesi):
- `cizim_orani()` (`:167-195`, sabitler dahil): karede sahne zemininden (`stil.css` `--sahne`) farklı piksel oranı, 4 px adımla. Lejant şeridi (alt
  %7) ve küçük görünüm köşesi (sağ alt 1/6 x %36; CSS halka) sayılmaz, çünkü boş karede de bunlar var. Eşik `CIZIM_ESIK = 0.01`.
  - Ayrım: teslim edilen eski 19 boş karede 0,0000; 400 dolu karede en düşük 0,0596 (yeni sayfa), HEAD karelerinde en düşük 0,0205.
  - İlk sürüm tüm kareyi 0,06 eşiğiyle ölçüyordu. HEAD'in 4 dolu karesini (37, 42-44: küçük parça, ızgara yok) boş sanıyordu,
    bu yüzden bırakıldı.
- `sahne_goruntu()` (`:198-226`): boş karede en çok `CIZIM_TEKRAR = 3` yeniden çekim yapıyor. Hâlâ boşsa adım
  `kontrol.json` `yazdir_goruntu.bos` listesine giriyor ve üretim çıkış 2 veriyor (`:437`). PIL yoksa denetim geçmiyor.
  - `kontrol.json`'a ek alanlar: `cizim_esik`, `yeniden_cekim`, `en_dusuk_cizim_orani`, `cizim_orani` (adım başına),
    `piksel_denetimi`. Öbür davranış değişmedi.
- Sınama: eski (boş) çıktılarda `cizim_orani` 19 boş kare buldu. Bunlar 00, 01, 02, 03, 04, 06, 17, 18, 21, 26, 29, 31, 32, 38, 41,
  42, 43, 45, 46; kontroldeki listeyle aynı.

**Kararlılık:** son kodla (depodaki `rehber/`) üreticinin çekim komutu art arda 3 tam tur koşuldu: **150 karede 0 boş**. Ek olarak:
- düzeltme sürerken bir tur daha: 50 / 0;
- üreticinin kendi koşusu: 50 / 0, yeniden çekim 0, en düşük oran 0,0595.

### B-3: `F10a-dogrula.py` kimlikle karşılaştırıyor ve yazdırma karelerini ölçüyor
- Vurgu artık `RehberTest.vurgu()`'dan okunmuyor (`:229-245`). Görünür mesh'lerin gerçek malzeme rengi okunuyor: ana `#7cfc00`,
  kopya `#cdf7a6`. Sonuç kimlik kümesi olarak karşılaştırılıyor.
- Parça tıklaması: tıklamadan önce vurgu 0; ana = [tıklanan]; kopyalar = satırın görünen öbür `ids`'i; vurgulu küme = satırın görünen
  `ids` kümesi. `fazla`, `eksik` ve `gizli_kopya` JSON'a yazılıyor.
- Panel satırı: vurgulu küme = satırın görünen `ids` kümesi.
- Esc, önceki adım parçası, şema ve patlat / tak sınamaları da kimlikle karşılaştırılıyor.
- Yazdırma kareleri: `yazdir_kareleri()` (`:439-498`), üreticiyle aynı ölçü, bağımsız uygulama.
  - `rehber/goruntu/adim-NN.png` 50 karede çizim oranı;
  - PDF'teki 3B görüntüler (PyMuPDF), boş sayfa listesi.
  - Eski çıktılarda 19 kare ve 19 PDF sayfası buldu (1, 2, 3, 4, 5, 7, 18, 19, 22, 27, 30, 32, 34, 42, 45, 46, 47, 49, 50). Kontrolün
    bulgusuyla aynı.
- Sonuç: 6 / 6 adımda parça ve panel kümesi birebir (`fazla` 0, `eksik` 0, gizli kopya 0). Yazdırma kareleri 50 / 50 çizili; PDF'te 50
  görüntü, boş sayfa 0, en düşük oran 0,0595.

### B-4: tak bitince sıkı kadraj
- `rehber/app.js:360-361`: patlatırken iki kadraj saklanıyor, yerindeki köşeler (`siki`) ve patlak kutu (`patlak`).
- `:384-387` (`tak()` sonu): son satır yerine oturunca (uçuş bitince; `?cekim=1`'de hemen) kamera `siki` kadraja dönüyor. Bu, adım açılışında ve V'de
  verilen kadrajın aynısı.
- `:392-397` (`geriAl()`): Shift+Boşluk tam takılı durumdan geri alınca patlak kadraja dönülüyor, geri çıkan satır kadrajda kalsın. Brief'in
  istediğinin simetriği olduğu için eklendi.
- Ölçüm (`F10a-dogrula.json` `secim.ek.tak_kadraj`): kamera uzaklığı D, sırasıyla açılış / patlak / hepsi takılı / geri al.
  - 33: 1402 / 3266 / 1402 / 3266;
  - 31: 607 / 1391 / 607 / 1391;
  - 12: 481 / 608 / 481 / 608.
- Görüntü: `F10a-goruntu-33-koyu-saydam-tak-son.png`. 11 / 11 satır takılı, robot kareyi dolduruyor (kontroldeki
  `tak-33-koyu-saydam-son` karesinde robot ortada küçüktü).

### Komutlar ve çıkış kodları (düzeltme turu 1)
| Komut | Çıkış | Not |
|---|---|---|
| `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` | 0 | 50/50, konsol 0, 1192 ↔ 1192, her parça tek adımda; yazdırma karesi boş 0, yeniden çekim 0; telefon 7 x 0 px; PDF 54 sayfa, 8,1 pt; denetim 0 |
| `py -3 -u -X utf8 planlama/d158/F10a-dogrula.py` | 0 | seçim 6/6 (kimlik), ek 6/6 (tak kadrajı dahil), ağsız dış 0 konsol 0, kadraj ortanca 0,1733 -> 0,4013, taşan 0, küçük görünüm 50/50 + 50/50 (360 px taşma 0), CDN 0, yazdırma 50/50, PDF boş 0 |
| `py -3 -X utf8 planlama/d158/F9b-dogrula.py` | 0 | GEÇER (hata 0) |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | 17 dosya kayıtla aynı |
| `py -3 planlama/d158/regresyon.py --yazma` | 0 | 10/10 aynı, GEÇER |
| `git diff --quiet HEAD -- rehber/veri` | 0 | |
| çekim komutu x 3 tam tur (scratchpad betiği, üreticiyle aynı Chrome argümanları) | — | 150 kare, boş 0 |

### Kabul ölçütleri (düzeltme turu 1 sonrası)
| Ölçüt | Ölçülen | Durum |
|---|---|---|
| `kontrol.json` 50/50, konsol 0, 1192 ↔ 1192 | 50/50, 0, 1192 ↔ 1192 | geçti |
| denetim 0 | ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 40, yasak 0 | geçti |
| 360 px taşma 0 | üretici 7 x 0 px; F10a-dogrula 50 adım en çok 0 px | geçti |
| PDF sayfa sayısı ve en küçük yazı | 54 sayfa, 8,1 pt (DOM ve PDF) | geçti |
| Yazdırma kareleri çizili (yeni) | 50 / 50; PDF 50 görüntü, boş 0; 3 tur x 50 boş 0 | geçti |
| Seçim 6/6 | 6/6, kimlik kümesi birebir | geçti |
| Ağsız: dış istek 0, konsol 0 | 0, 0 | geçti |
| Kadraj: taşan 0, ortanca büyüdü | taşan 0; 0,1733 -> 0,4013; 0,05 altı yalnız 25 (0,0307, gerekçe yukarıda) | geçti |
| Küçük görünüm 50/50 | 1400 px 50/50, 360 px 50/50 | geçti |
| F9b 0, carpisma_kos 0, regresyon 10/10 | 0, 0, 10/10 | geçti |
| `rehber/veri/` değişmedi | çıkış 0 | geçti |

### Bakılan kareler (Read ile)
- `rehber/goruntu/adim-00 ... 49.png`, 50 karenin hepsi (iki pano hâlinde, scratchpad). Hepsinde model ve küçük görünüm çizili (gözle).
  - 43, 45, 46'da yeni parçalar karenin kenarında ya da gri blokların arkasında (B-2, açık).
  - 25'te horn görünmüyor (bilinen).
- PDF sayfaları: 1 (adım 0), 2 (1), 18 (17), 22 (21), 32 (31), 34 (32), 42 (38), 49 (45). Hepsinde 3B görüntü dolu.
- `F10a-goruntu-33-koyu-saydam-tak-son.png`.
- Ölçüm sırasında: boş ve dolu karelerdeki olay günlükleri; HEAD ölçüm kopyası 31; HEAD 37 (oranı düşük ama dolu: eşik seçimi).

### Dokunulan dosyalar (bu tur)
- `rehber/app.js` (`boyut()` eşzamanlı çizim; patlat / tak / geri al kadrajı);
- `tasarim/freecad/rehber/rehber_uret.py` (yalnız yazdırma karesi piksel denetimi; başlık yorumunda bir satır);
- `planlama/d158/F10a-dogrula.py`, `F10a-dogrula.json`, `F10a-gunluk.md` (bu bölüm),
  `F10a-goruntu-*.png` (yeniden üretildi; yeni `F10a-goruntu-33-koyu-saydam-tak-son.png`);
- üretici çıktısı: `rehber/goruntu/adim-*.png`, `planlama/rehber/kontrol.json`, `planlama/rehber/goruntu/*.png`,
  `planlama/rehber/Lale-montaj-rehberi.pdf`.
- Dokunulmadı: `rehber/veri/`, `rehber/index.html`, `rehber/stil.css`, `F10a-kontrol.md`, `tasarim/freecad/` içindeki öbür dosyalar.

### Açık kalanlar
- **B-2, F10d'ye devredildi.** İki kollu tezgâh adımlarında (21 D1c, 43 H0b, 45 H0d, 46 H0e) sıkı kadraj iki küçük parçayı karenin
  iki kenarına itiyor; parçalar gri blokların arkasında kalıyor. Yazdırma karelerinde de görülüyor.
  - Oran ölçüsü birleşik kutudan alındığı için bunu "iyileşme" sayıyor.
  - Seçenekler kontrolde (B-2).
- **B-5, F10d'ye devredildi.** "Saydam" tek başına 31 ve 33'te içeriyi göstermiyor; yeni parça kabuğun kendisi ve opak. İçerisi
  saydam + patlat / tak ile görünüyor; Ahmet'e "saydam + tak" diye anlatılmalı.
- `RehberTest.miniOlc()` ölçmeden önce kendisi `render()` çağırıyor (kontrol B-6). Küçük görünüm ölçümü bu yüzden "sayfa kendi
  başına çizdi mi"yi değil "çizebiliyor mu"yu ölçüyor. Bu turda dokunulmadı. Piksel ölçüsü küçük görünüm köşesini dışarıda bırakıyor;
  yazdırma karelerinde küçük görünümün çizildiğine yalnız gözle bakıldı (50 / 50).
- Kare süresinin küçük görünümle ne kadar uzadığı ölçülmedi. Kök nedendeki "çizim pahalılaşınca yarış açılıyor" kısmı yorum;
  mekanizma ve ikiye bölme ölçümle.
