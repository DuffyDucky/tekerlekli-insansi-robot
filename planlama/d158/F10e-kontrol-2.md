# F10e ikinci bağımsız kontrol (düzeltme turu 1'in kontrolü)

Kontrol: 12.11.2026, dal `lale-duzeltme`, HEAD `90c270a`, paket çalışma ağacında. Brief: scratchpad'deki `F10e-B2-brief.md`.
Kaynak etiketleri: **[B3]** bu kontrolde ölçüldü / gözle bakıldı; **[D1]** düzeltme ajanının iddiası (`F10e-gunluk.md` §12);
**[B]** ilk kontrol (`F10e-kontrol.md`).

Bütün ölçümler salt okuma: başsız Chrome (tek süreç, ön planda, dilim başına < 8 dk), `rehber/index.html` `file://` üzerinden; HEAD
karşılaştırması için `rehber/` HEAD'den scratchpad'e `git archive` ile çıkarıldı. Betikler ve kareler scratchpad'de (`f10e-b3/`).
Boş bellek her ağır komuttan önce 3,08–3,22 GB.

## 1. Hüküm

**GEÇER** (küçük notlarla; hiçbiri engelleyici değil).

- İlk kontrolün koyu tema bulgusu kapandı: 6 bindirme cıvatası koyu temada 78–144 px (ilk kontrolde 0–3 px); ölçülen 25 parçanın
  hepsi eşiği geçiyor. **Düzeltilmiş `gorunurlukFark` gerçek ekran görüntüsü farkıyla 25 / 25 parçada birebir aynı sayıyı veriyor.**
- 31.3 `p0762` iki temada görünür (ekran farkı açık 156, koyu 155 px; yalnız 142).
- Çizim sırası değişikliği opak örtüyü bozmuyor (kod: derinlik testi açık; gözle 10 konumda opak parçanın önüne geçen cıvata yok).
  Bedeli: saydam katmanın **önündeki** tonu kayboluyor, cıvata katmanın üstünde gibi duruyor (yeni bulgu 2).
- Değişiklik günlükte yazılandan geniş: kabuk dışı 46.1 / 46.2 de değişti (≈ 9 600–9 900 px); karede bozulma yok (yeni bulgu 1).
- Benzer çiftler küçük görünüm etiketiyle ayrılıyor; etiket metni 8 konumda bağımsız hesapla aynı; ana tuval boyutu HEAD ile aynı.
  3B sahnenin kendisi değişmedi; ayrım bir yazı etiketinden (kısmen kapandı, brief'in izin verdiği yol).
- Kayıtlar: 893 / 1188, P10.7 devri, 9a "42" sayısı ve adım 41 metni günlükle / veriyle tutuyor; veride HEAD'e göre ilk kontrolün
  listesi dışında değişen tek alan adım 41 `is_` ilk satırı. Zincir çıkış kodları `.durum` dosyalarıyla aynı.

## 2. İlk kontrolün bulguları

### Bulgu 1: koyu temada görünürlük

Yöntem [B3]: B1'in `b_ekran.py` yöntemi (scratchpad'e kopyalandı, `olc.py`): `?adim=<a>&cekim=1&tema=<t>&isaret=0`, 1400 × 900, başsız
Chrome; sayfanın gerçek ekran görüntüsü; parça `visible=false`, sayfa kendi çizer, yeniden ekran görüntüsü; tuval bölgesinde (araç
çubuğunun altı, küçük görünüm ve lejant kutusu dışarıda) Σ|ΔRGB| > 24 olan piksel. Aynı sayfa yüklemesinde düzeltilmiş
`RehberTest.gorunurlukFark({ids})` ve `RehberTest.gorunurluk().yalniz` (kimlik tamponu, parça tek başına) de okundu. Her parçadan
sonra geri açılınca kare ilk kareye döndü (fark 0, 25 / 25).

| alt adım | tema | parça | ekran farkı (px > 24) | düzeltilmiş fonksiyon | yalnız (kimlik) | oran | ölçüt (≥ 30, ≥ 0,20) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 34.3 | koyu | p0244 | 127 | 127 | 218 | 0,58 | geçer |
| 34.4 | koyu | p0242 | 144 | 144 | 265 | 0,54 | geçer |
| 34.4 | koyu | p0304 | 115 | 115 | 228 | 0,50 | geçer |
| 34.4 | koyu | p0306 | 132 | 132 | 266 | 0,50 | geçer |
| 34.5 | koyu | p0256 | 129 | 129 | 222 | 0,58 | geçer |
| 34.6 | koyu | p0254 | 141 | 141 | 266 | 0,53 | geçer |
| 34.6 | koyu | p0308 | 111 | 111 | 227 | 0,49 | geçer |
| 34.6 | koyu | p0310 | 139 | 139 | 265 | 0,52 | geçer |
| 35.1 | koyu | p0280 | 78 | 78 | 105 | 0,74 | geçer |
| 35.2 | koyu | p0282 | 84 | 84 | 110 | 0,76 | geçer |
| 34.2 | koyu | p0300 | 87 | 87 | 165 | 0,53 | geçer |
| 34.2 | koyu | p0302 | 99 | 99 | 174 | 0,57 | geçer |
| 34.2 | koyu | p0324 | 102 | 102 | 191 | 0,53 | geçer |
| 34.8 | koyu | p0272 | 54 | 54 | 77 | 0,70 | geçer |
| 34.9 | koyu | p0266 | 53 | 53 | 94 | 0,56 | geçer |
| 34.9 | koyu | p0312 | 66 | 66 | 108 | 0,61 | geçer |
| 34.9 | koyu | p0314 | 74 | 74 | 118 | 0,63 | geçer |
| 36.1 | koyu | p0288 | 81 | 81 | 154 | 0,53 | geçer |
| 36.1 | koyu | p0290 | 86 | 86 | 157 | 0,55 | geçer |
| 35.3 | koyu | p0434 | 504 | 504 | 2082 | 0,24 | geçer |
| 35.3 | açık | p0434 | 504 | 504 | 2082 | 0,24 | geçer |
| 35.3 | açık | p0432 | 273 | 273 | 750 | 0,36 | geçer |
| 34.5 | açık | p0256 | 133 | 133 | 222 | 0,60 | geçer |
| 31.3 | açık | p0762 | 156 | 156 | 142 | 1,10 | geçer |
| 31.3 | koyu | p0762 | 155 | 155 | 142 | 1,09 | geçer |

- 6 bindirme cıvatası (ilk kontrolde 0–3 px): koyu temada 78–144 px [B3]. İlk kontrolün koyu temada eşik altı bulduğu öbür
  14 parçanın 14'ü ve açık temada 35.3 p0434 ölçüldü; hepsi geçiyor.
- **Düzeltilmiş fonksiyon = ekran görüntüsü, 25 / 25 parçada birebir aynı sayı** [B3]. D1'in kök neden açıklaması (eski fonksiyon
  render target'a doğrusal yazıyordu) bu kontrolde ayrıca sınanmadı; sonuç olarak fonksiyonun şimdiki hâli ekranla tutuyor.
- 35.3 p0434 iki temada aynı sayıyı veriyor (504 / 535 / en büyük Σ 264): somun artık saydam taşıyıcının üstünde ve arkasında opak
  direk var; arka plan temadan bağımsız, beklenen.
- D1'in sayıları (§12.2) bu ölçümle aynı: 31.3 p0762 açık 156 / koyu 155, yalnız 142 [B3 = D1].

**Sonuç: kapandı** (ölçülen 25 parça; 42 alt adımın tam iki temalı koşusu bu kontrolde tekrarlanmadı).

`F10e-dogrula.py` kodu [B3, okundu]: `gorunurluk()` `TEMALAR = ("light", "dark")` üzerinde döner; `gecti` = iki temanın her alt adımı
(`ok and not kalan and bk`) ve iki temada `SOLUK` iki parçası (31.3 p0762, 34.7 p0440). Eşik `PX_ESIK, ORAN_ESIK, FARK_ESIK = 30, 0.20,
24` (gevşetilmemiş). İstisna yalnız verideki `piksel_ok` gerekçesiyle; ısıl gömmeler `gomme` listesine ayrılıyor ve geçme şartına
girmiyor (brief'in "ayrı sayılır" kuralı; iki temada 0 olduğu için bu koşuda fark etmiyor). Sessiz atlama: alt adımın kendi satırında
olup sahnede hiç görünmeyen parça `px`'te olmadığı için sayılmaz; F10d'nin kimlik tamponu ölçüsü bunu ayrıca yakalıyor. Tek tema
`GOR_EK` / `TEMALAR` değişkeni yalnız scratchpad betiğinden değiştiriliyor, tam koşuda boş / iki tema.

### Bulgu 2: 31.3 `p0762`

Ekran görüntüsü farkı açık 156 px, koyu 155 px (yalnız 142) [B3, tablo]. Gözle (açık + koyu, `?ustte=0` ile yan yana): önce halkanın
içi boştu; şimdi pirinç ısıl gömme halkanın içinde, yeşil kartın üstünde tam renkte seçiliyor [B3]. **Kapandı.** (Not: kartın önünde
duruyormuş gibi görünüyor; yeni bulgu 2.)

### Bulgu 3: 34.7

Açık ve koyu kareye baktım (önce / sonra yan yana ve tam kare) [B3]: hoparlör grubu sağ üstte küçük, katmanlar yine ayrılmıyor; ısıl
gömmeler ve kelepçe cıvataları halkada renkli. Bu turda kötüleşme yok (sahne, kamera aynı; yalnız bağlantı elemanları tam renkte).
Günlük "zor" diyor ve "hoparlör kara" ifadesini "koyu gri" diye düzeltmiş. **Sınıflama dürüst; bulgu kayıtta kapandı, karede açık
(zor).** Sayım açık 40 / zor 2: bu kontrolde 42'nin hepsine yeniden bakılmadı (aşağıda örneklem).

### Bulgu 4: benzer çiftler

Etiket ölçümü [B3, `lbl.py`; etiket DOM'dan, beklenen değer yeni parçaların dünya kutusundan, ayrı yazılmış kodla]:

| konum | etiket (sayfa) | bağımsız hesap | merkez x / z (mm) | y aralığı (ham, mm) |
| --- | --- | --- | --- | --- |
| 34.3 | sağ · y 470–660 | aynı | 57 / 0 | 465–657 |
| 34.5 | sağ · y 620–810 | aynı | 57 / 0 | 623–815 |
| 34.4 | sol · y 480–650 | aynı | −63 / 0 | 475–647 |
| 34.6 | sol · y 630–800 | aynı | −63 / 0 | 633–805 |
| 49.3 | orta-arka · y 810–1010 | aynı | 0 / −84 | 815–1005 |
| 49.4 | orta-arka · y 1030–1200 | aynı | 0 / −74 | 1026–1202 |
| 5 | orta · y 90–120 | aynı | 0 / 0 | 86–119 |
| 2 | orta · y 110–1250 | aynı | 0 / 0 | 115–1250 |

- Taraf: verinin koordinat tanımı "+X sağ, +Z ileri"; adımların adlarıyla (34.3 "sağ", 34.4 "sol") tutuyor.
- Yazı: masaüstü 12 px kalın, telefon 9,5 px kalın. Renk açık temada `#1d1f22` / beyaz %82 zemin, koyuda `#ececec` / koyu %82 zemin
  (ikisi de yüksek karşıtlık). Gözle okunuyor: etkileşimli 1400 (açık, koyu), `?sahne=1`, 360 px (açık, koyu), üretilmiş basılı kare
  `rehber/goruntu/adim-34-03`, `-34-05`, `-49-03`, `-49-04` (1200 × 720) [B3].
- Üst üste binme: etiket küçük görünüm kutusunun alt şeridinde; kehribar halka (`mini-hal`) ile kesişmiyor (8 konumda kutular ölçüldü;
  en dar durum adım 5, 360 px: halka alt kenarı 401, etiket üst kenarı 407). 360 px'te 49.3 etiketi iki satıra kırılıyor ("y 810–" /
  "1010"); okunuyor, biçim kusuru.
- Sahne boyutu: ana tuval 1400 × 900'de 1000 × 796, 360 px'te 360 × 384 (CSS 385), `?sahne=1`'de 1400 × 900; HEAD sürümüyle **aynı**.
- Kareden ayırt: 34.3 / 34.5 ve 34.4 / 34.6 artık etiketten (ve kehribarın küçük yükseklik farkından) ayrılıyor; 3B kare hâlâ aynı.
  **Kısmen kapandı**: brief'in izin verdiği "bindirilmiş taraf / konum etiketi" yolu, yazısız 3B ayrım yok.

### Bulgu 5–8 (kayıt)

- 893 / 1188: §12.6 ve eski satırlarda "düzeltildi" notu var; veride 893 benzersiz `ip` farkı ilk kontrolle aynı. **Kapandı.**
- Kablo yolu 12 parça: istisna ve "P10.7'ye devredildi (kablo içeriği)" yazılı; §1'deki "tek kaynak" satırlarında not var. **Kapandı (karar).**
- 9a: "Denenen 42 iki bacaklı öteleme yolunda bulunmadı; dönme ve ara açılar denenmedi." 42, günlüğün §7.1 anlatımıyla tutuyor
  (bacak 1: 6 yön × 6 uzunluk = 36; ters sıra: +z 2 uzunluk × 3 yön = 6). Not: §7.1'e göre ölçüm iki bant (33.3 sağ, 33.5 sol) için
  yapılmış; 42 bant başına. Süpürme bu kontrolde koşulmadı. **Kapandı (metin).**
- Adım 41: veride `is_` ilk satırı "Sırayı bozma. CAD duruşunda yandan kaydırılamaz (+x'te üst kol tüpüne, −x'te omuz bandına değer);
  önden radyal tak." Öbür 6 satır HEAD ile aynı; `rehber_metin.py` G4 ile aynı. İki engel de §7.3'te ölçülmüş (+x üst kol tüpü,
  −x omuz bandı). **Kapandı** (ölçülenle sınırlı; okura "CAD duruşu" ifadesi yabancı, küçük not).
- Veri HEAD ile alan alan [B3, ilk kontrolün HEAD kopyasıyla]: adımlarda değişen `ev` 49, `sira_grup.ev` 50, `sira_grup.kamera` 10,
  `sira_grup.saydam` 1, `is_` 1 (adım 41); parçalarda `gr` 1192, `ip` 893; üst alanlarda `ev_kaynak`, `renk_kaynak`. İlk kontrolün
  listesine yalnız adım 41 `is_` eklenmiş. `semalar`, `kablo`, `kablolama` değişmedi.
- Günlükte düzeltme notu olmadan duran çürütülmüş iddia: taradığım satırlarda (1188, tek kaynak, iki bacaklı yol, açık 41 / zor 1,
  hoparlör kara, 40 / 142, ayırt ediliyor, uyarı tutuyor) bulmadım. §2 satır 163'teki "panel başlığından … ayırt edilir" doğru olduğu
  için notsuz kalması sorun değil.

## 2b. Tutarlılık, zincir, kurallar

- Dosya saatleri (12.11): kod `app.js` 01:52, `index.html` 01:47, `stil.css` 01:52, `rehber_metin.py` 01:50, `F10e-dogrula.py` 01:53;
  veri 07:01; `planlama/rehber/goruntu` 107 kare 07:01–07:11, `rehber/goruntu` 100 kare 07:06–07:11; PDF 07:12; `kontrol.json` 07:31
  (içinde `tarih 2026-11-12 07:31`); F10d / F10a / F10e `.json` 07:43 / 07:50 / 08:05, `tarih` 07:34 / 07:43 / 07:50. Hepsi son kod
  değişikliğinden sonra ve tek üretimden. Not: verinin `uretim` alanı "2026-11-11 15:34" (`--veri-yok` geometriyi eski tam üretimden
  alıyor; dosya 07:01'de yeniden yazılmış).
- `gecti`: F10e `true` (`gecti_ozet`'te yalnız `renk_demo` `false`), F10d `true`, F10a `true`. `renk_demo` geçme koşulu dışında: kodda
  `ana` demeti `renk_demo`'yu içermiyor, `gecti = all(ana) and not konsol_hatasi` [B3, okundu].
- `.durum` dosyaları: üretim 0 (1862 s), F10d 0, F10a 0, F9b 0, çarpışma 0, regresyon 0, F10e 0, kareler 0; sarmalayıcı denemesi 3
  (beklenen). Günlük §12.7 ile aynı. Kayıtların sonu: F10e "GECTI … renk_demo KALDI", F10d "GECTI", F10a "GECTI", regresyon "GEÇER".
- Konum ve konsol [B3]: 100 / 100 konum açıldı (50 açık + 50 koyu tema), hazır 100, konum doğru 100, `window.__hata` 0.
- Kurallar: bu turda değişen dosyalarda yerel kullanıcı klasörü yolu 0 (`rehber_uret.py`'deki `LOCALAPPDATA` ortam değişkeni ve
  "Masaüstü Chrome" sözcüğü HEAD'den / A'dan kalma, yol değil). Bu turda (01:29 sonrası) yazılan dosyalar: `rehber/` üç kod dosyası,
  veri, kareler, PDF, `kontrol.json`, `tasarim/freecad/rehber/` içinde `rehber_metin.py`, `rehber_gorunum.py` ve `rehber_veri.py`
  (son ikisi içerikçe: `rehber_veri.py` HEAD ile aynı, kadraj denemesi geri alınmış; `rehber_gorunum.py` izlenmeyen dosya, bu turdaki
  değişikliği ölçülmedi, içinde `kadraj` kalıntısı yok), `planlama/d158/` F10e günlüğü / doğrulama dosyaları. `kod/`, `README.md`,
  `karar-kuyrugu.md`, `rehber/vendor/` ve `tasarim/freecad/` içinde `rehber/` dışı: bu turda yazılan 0. `dongu-158.md` 08:11 girdisi
  orkestratörün. `robot.glb` / `robot-glb.js` HEAD ile aynı (`git diff --quiet` 0).

## 2c. Geri bozulma örneklemi

Açık temada gözle (tam kare ya da `?ustte=0` ile yan yana) [B3]: kabuk 31.1, 31.5, 31.9, 31.10, 33.1, 33.5, 33.8, 34.1, 34.2, 34.7,
34.8, 35.1, 35.3, 35.4, 36.2, 49.1, 49.5 (17); kabuk dışı 2, 8, 12, 17, 21.1, 21.2, 25, 41, 43.1, 45.2, 46.1, 46.2, 48 (13). Koyu: 31.3,
33.3, 34.3, 34.5, 34.7, 35.1, 35.3, 36.1. İlk kontrolde açık olan karelerden bozulan görmedim; etiket her karede küçük görünümün altında.
`?ustte=0` ile piksel farkı: 21.1, 21.2, 25, 36.3 açık 0; 33.3 koyu 84; 31.3 ≈ 500; 34.x / 35.1 ≈ 950–1 430; 35.3 ≈ 3 900–4 160;
46.1 9 940, 46.2 9 615.


## 3. Yeni bulgular

Engelleyici yok. Önem sırasıyla:

1. **Çizim sırası değişikliği kabuk dışına da uzanıyor ve günlükte yazmıyor (küçük).** Koşul (`app.js` 525–530): konumun saydam
   listesi doluysa (`sira_grup[].saydam`, alt adım yoksa adımın `saydam`'ı), o konumun her yeni bağlantı elemanı (`r === "baglanti"`,
   kendisi saydam listede değil, malzemesi saydam değil) `ustteKoy` alır; `?ustte=0` kapatır. Saydam listesi olan konumlar: 21.1, 21.2,
   25, 31.x (7), 33.x (6), 34.1–34.9, 35.1–35.5, 36.1–36.3, 46.1, 46.2, 49.1, 49.5. Kabuk dışında karesi gerçekten değişen: **46.1 ve
   46.2** (bilek flanşı: 4 cıvata ve 2 ısıl gömme saydam flanşın içinde; önce kahverengi tonlu, şimdi gri / pirinç tam renkte). Gözle
   bozulma yok, okunurluk bence daha iyi. Ama günlük §12 değişikliği yalnız kabuk için anlatıyor, bu iki konumun karesine bakıldığı
   yazmıyor ve F10e görünürlük ölçümü kabuk dışını kapsamıyor. Öneri: günlüğe "46.1 / 46.2 de etkileniyor, karesi bakıldı" satırı.
2. **Saydam katmanın önündeki derinlik ipucu kayboluyor (küçük, bilgi).** Kod: `ustMat` opaklık 1, `depthWrite` açık, `renderOrder` 10,
   saydam geçişte çiziliyor; opak parçalar önce çizilip derinlik yazdığı için cıvata opak parçanın önüne geçemez (gözle 10 konumda (31.3, 31.10, 34.3, 34.5, 34.7, 35.1, 35.3, 36.1, 46.1, 46.2)
   örnek yok). Saydam katmanlar derinlik yazmadığı için cıvata, önündeki saydam katmanın **üstüne** boyanıyor: katmanın tonu cıvatada
   görünmüyor, cıvata katmanın önündeymiş gibi duruyor. Yalnız opak kenar çizgileri (derinlik yazan) önündeyse cıvatanın üstünden
   geçiyor. Örnekler: 31.3 `p0762` iki yeşil kartın arkasındaki boss'ta ama kartın yüzüne yapışık gibi görünüyor (kartın vida yeri
   olduğu için yanlış parça izlenimi zayıf); 35.3 çekiç somunlar saydam taşıyıcının önünde gibi; 46.x cıvatalar flanşın önünde gibi.
   Halkalar yeri gösterdiği için okuru yanlış parçaya yönlendiren bir kare görmedim. Öneri: gerekirse ustte malzemeye hafif bir
   ton / kesik kenar ("arkada" işareti) verilebilir; bu turda düzeltme gerekmiyor.
3. **Etiketin açıklama metni "yerden yükseklik" diyor, değer ise y koordinatı (küçük).** `miniYer` `title`: "yerden yükseklik y0–y1
   mm". Robotun en alt noktası y = −89 mm [B3, bütün parçaların dünya kutusu]; yani yerden yükseklik etikettekinden ≈ 90 mm fazla.
   Görünen etiket "y 470–660" dediği için yanıltıcı değil; yalnız fareyle üstüne gelince çıkan metin. Öneri: "y (mm)" ya da yere göre
   düzelt.
4. **360 px'te uzun etiket kırılıyor (biçim).** 49.3 / 49.4: "orta-arka · y 810–" / "1010". Öneri: telefonda kırılmayı `·`'den sonra
   yap ya da "o-arka" kısaltması.
5. **Adım 41 metninde "CAD duruşunda" (biçim).** Okur için anlamı belirsiz; doğru ama "robot CAD'deki duruşundayken (kollar düz)" gibi
   açıklanabilir.

## 4. Ölçülemeyenler

- **Bütün kabuk alt adımlarının iki temalı tam görünürlük koşusu:** tekrarlanmadı; 25 parçada ekran görüntüsüyle ölçüldü (D1'in tam
  koşusunun sayıları bu 25'te aynı).
- **Eski fonksiyonun neden farklı verdiği (render target doğrusal çıktı):** D1'in açıklaması sınanmadı; yalnız yeni fonksiyonun
  ekranla aynı verdiği ölçüldü.
- **Kabuk dışı konumlarda okurun pikseli** (46.1 / 46.2 dahil): ölçülmedi, yalnız gözle.
- **9a süpürmesi ve adım 41 kol duruşu:** koşulmadı (metin / sayı tutarlılığı okundu).
- **`rehber_gorunum.py`'nin bu turdaki değişikliği:** izlenmeyen dosya, önceki hâlinin kopyası yok; ölçülmedi.
- **PDF en küçük yazı / sayfa:** bu kontrolde yeniden ölçülmedi (D1: 69 sayfa, 8,1 pt); PDF'teki etiket karesi ayrıca açılmadı
  (aynı `rehber/goruntu` karelerine bakıldı).
- **Anlaşılırlık sayımı (42 alt adımın hepsi):** yeniden yapılmadı; 22 kabuk alt adımına bakıldı, sınıflamayı değiştirecek bir şey
  görmedim.
- **Soyad / takma ad taraması:** kişi listesi elimde yok; yalnız yerel yol tarandı.
