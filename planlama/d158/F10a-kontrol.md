# F10a kontrolü (P10.1: rehber arayüzü küçükleri): bağımsız kontrol ajanı B, 11.11.2026

Kontrol edilenler: `rehber/app.js`, `rehber/index.html`, `rehber/stil.css` (`git diff HEAD`), `rehber/vendor/`, üretici çıktıları
(`rehber/goruntu/`, `planlama/rehber/kontrol.json`, `planlama/rehber/goruntu/`, `planlama/rehber/Lale-montaj-rehberi.pdf`),
`F10a-dogrula.py`, `F10a-dogrula.json`, `F10a-gunluk.md`, `F10a-goruntu-*.png`. Esas alınan: çalışma ağacı (dal `lale-duzeltme`, HEAD `9d0c58a`).

Önce kendi ölçümümü kurdum, A'nın sayılarıyla sonra karşılaştırdım. Betikler, tarayıcı profilleri ve görüntüler scratchpad'de
(`scratchpad/f10a-b/`). Yöntem: Chrome DevTools protokolü (A'nınkiyle aynı başsız Chrome, swiftshader), gerçek fare ve tuş olayları.

Vurguyu `RehberTest.vurgu()` ile okumadım. Her mesh'in gerçek malzeme rengine baktım (`#7cfc00` ana, `#cdf7a6` kopya) ve
kimlik listesini veriden (`rehber-veri.json`) beklenen satırla karşılaştırdım. Tıklama noktasını kendi raycast'imle buldum.

Yazdığım tek depo dosyası bu dosya. Commit, push, silme, checkout, reset, stash yapılmadı. FreeCAD ve üretici koşulmadı.
Arka planda Chrome ya da http sunucusu kalmadı.

## Karar: **DÜZELTME GEREKLİ**

Engelleyen 1, engellemeyen 5 bulgu.

Etkileşimli sayfa sağlam: seçim, öncekiler kipi, patlat / tak, kısayollar, küçük görünüm, kadraj ve internetsiz açılma A'nın
dediği gibi çalışıyor. Sayıların hepsini kendim ölçtüm (tablo aşağıda).

Bozuk olan yazdırılabilir sürüm. Teslim edilen `rehber/goruntu/` karelerinin 19 / 50'si boş. PDF'in 54 sayfasının 19'unda 3B
görüntü yerinde boş kutu var. Ne `rehber_uret.py` kontrolü ne `F10a-dogrula.py` bunu yakalıyor. A'nın günlüğü baktığını söylediği
`rehber/goruntu/adim-38.png`'nin son hâli de boş.

## Ölçüt tablosu: B'nin ölçtüğü ↔ A'nın sayısı

| Ölçüt | B | A | Not |
|---|---|---|---|
| Seçim sınaması | 7 / 7 adım (9 B3, 14 B6a tezgâh, 23 E1a tezgâh, 32 K2 kablolama, 35 F3 kabuk, 49 F5 kabuk, 31 E4); kimlik bazında, aşağıda | 6 / 6 (12, 17, 31, 33, 44, 34); sayı bazında | 49'da "adım değişimi" son adım olduğu için → ile değil ← ile sınandı |
| Parça tıklama: ana = tıklanan, kopyalar = satırın görünen öbür `ids`'i | 7 / 7 kimlik listesi birebir (kopya sayısı 1, 15, 3, 0, 15, 21, 10) | sayı eşit | |
| Panel satırı (A'nınkinden farklı satır: ikinci satır) | 7 / 7 kimlik birebir, satır işaretli | sayı eşit | |
| Boş tık / Esc / adım değişimi: vurgu 0, malzeme başlangıçla aynı | 7 / 7, 7 / 7, 7 / 7; görünen mesh'lerde malzeme farkı 0, röntgen alt-mesh'i 0 | 0 / 0 / 0 (yalnız sayı) | |
| Önceki adım (gri) parçası seçimi ve griye dönüş | geçti (35'te 34. adımın bandı; kopya 1, temizlenince fark 0) | geçti | |
| Saydam kipte temizleme; seçiliyken tema değişimi | fark 0; fark 0 (taze yüklenmiş sayfayla) | ölçülmemiş | |
| Kablo şeması tüpü / kablo parçası tıklama | şema 4 (32), p1190 (17): vurgulu, ad etikette | şema (32) | |
| Hızlı karışık işlem (40 rastgele tık, O, P, Boşluk, Shift+Boşluk, T, R, satır, Esc, boş tık; 31 ve 33) | kalıcı renk bozulması 0, röntgen kalıntısı 0 | ölçülmemiş | |
| Tak sırası = panel satır sırası | 31: 15 satır aynı + sonda "Kablo şemaları" satırı (A günlükte yazmış); 33: 11 / 11; 12: 12 / 12 | 3 tak denendi | |
| Patlak / takılı konum; geri al | patlakta yerinde 0; sonda 60 / 60, 61 / 61, 39 / 39 yerinde; Shift+Boşluk son satırı geri çıkarıyor (33: 6, 12: 3 parça) | geçti | |
| Kısayollar | ←/→, O, ö, Ö, M, P, Boşluk, Shift+Boşluk, R (sırayı kapatıyor + uçuş), T, V hepsi çalışıyor | O, M, P, Boşluk, Shift+Boşluk | |
| Odak | kontrol kutusu odakta: Boşluk kutuyu değiştiriyor, P / O / → tetiklenmiyor; `select` odakta P yok; odaklı düğmede Boşluk yalnız "tak", düğme tıklanmıyor | ölçülmemiş | |
| Ağsız `file://` (çevrimdışı + http/https/ws engelli) | 3 sayfa: dış istek 0, konsol hata ve uyarı 0, model 1192 mesh; `yazdir.html`: 50 / 50 görüntü yüklendi, dış istek 0 | dış 0, konsol 0, 1192 | |
| Yerel http, alt dizinden (`/lale-depo/rehber/`, GitHub Pages benzeri) | index, `?adim=33`, `yazdir.html`: 200, model 1192, sayfa hatası 0 (yalnız sunucu kökünde `favicon.ico` 404, sayfadan değil) | ölçülmemiş | |
| CDN bağlantısı (`rehber/`, `veri/` hariç) | 0. Vendor'da yalnız iki URL var: XHTML ad alanı ve three'nin bir uyarı metnindeki forum bağlantısı (istek değil) | 0 | |
| Vendor sürümü ve lisans | başlık "three.js 0.160.0", `REVISION "160"`; `LICENSE-three.txt` MIT, telif "2010-2023 three.js authors" | aynı | npm paketiyle bayt karşılaştırması yapılmadı (ağsız ölçüm) |
| Kadraj: taşan yeni parça, 50 adım, 1400 × 900 | 0 adım. Araç çubuğu, lejant ya da küçük görünümün altında kalan yeni parça noktası olan adım 0 | 0 | |
| Kadraj oranı ortancası | 0,4013 (yalnız "sonra" ölçüldü) | 0,1733 → 0,4013 | "önce"yi ayrıca ölçmedim |
| Oranı 0,05 altında | yalnız 25 E2a (0,0307) | 25 (0,0307) | aynı |
| Küçük görünüm çizildi (tuvalin son karesinden, `render()` çağırmadan) | 1400 px 50 / 50; 360 px 50 / 50; koyu 5 / 5 | 50 / 50, 50 / 50 | |
| Küçük görünüm × araç çubuğu / lejant / panel; sahne dışı | 0 / 0 / 0; 0 (1400 ve 360) | panel 0 | |
| 360 px yatay taşma | 50 adımda en çok 0 px | 0 | |
| Yazdırma görüntüsü (`?sahne=1`) gerçek zamanda | 50 / 50 çiziliyor; küçük görünüm ya da lejant altında kalan yeni parça 0 | ölçülmemiş | |
| **Teslim edilen yazdırma kareleri `rehber/goruntu/`** | **19 / 50 boş** (B-1) | "50 / 50, eksik yok" | |
| **PDF** | 54 sayfa, en küçük yazı 8,1 pt (HEAD de 54, 8,1); **19 sayfada 3B görüntü boş** | 54, 8,1 pt | |
| `rehber/veri/` | `git diff --quiet HEAD -- rehber/veri` çıkış 0 | 0 | |
| `rehber_uret.py` | değişmemiş (çıkış 0) | dokunulmadı | |
| Alan dışı değişiklik | 0 (aşağıda) | | |
| Yerel yol / takma ad | 0 (aşağıda) | | |
| `F9b-dogrula`, `carpisma_kos kontrol`, regresyon | **ölçülmedi**: üretici ve model zinciri yeniden koşulmadı | 0, 0, 10 / 10 | |

## Bulgular

### B-1 (engelleyen). Yazdırma karelerinin 19 / 50'si ve PDF'in 19 sayfası boş
**Ne:**
- `rehber/goruntu/adim-NN.png` kareleri yazdırılabilir sürümde (`rehber/yazdir.html:120`) ve PDF'te kullanılıyor.
- Bu karelerden 19'unda yalnız sahne zemini, lejant ve küçük görünümün CSS halkası var. 3B model yok, küçük görünümün kendisi de
  çizilmemiş.
- Boş kareler: 00, 01, 02, 03, 04, 06, 17, 18, 21, 26, 29, 31, 32, 38, 41, 42, 43, 45, 46.
- Hepsi 9-12 kB. HEAD'de en küçük kare 16,8 kB'tı, boş kare yoktu.
- PDF: PyMuPDF ile her sayfanın görüntüsünde zeminden farklı piksel oranına baktım.
  - Bu 19 adımın sayfalarında oran ≤ 0,021. Örnek: sayfa 34 / 54, adım 32: başlık var, görüntü kutusu boş.
  - HEAD PDF'inde en düşük oran 0,032.

**Neden yakalanmadı:**
- `rehber_uret.py:165-176` (`sahne_goruntu`) yalnız dosyanın var olup olmadığına ve tarihine bakıyor. `kontrol.json`
  `yazdir_goruntu.eksik = []` diyor.
- `F10a-dogrula.py` yazdırma karelerini hiç ölçmüyor. Kadraj ölçümü yalnız geometri; piksele bakmıyor.
- Küçük görünüm ölçümü `RehberTest.miniOlc()` önce kendisi `render()` çağırıyor (`rehber/app.js:923`). Yani sayfanın kendi başına
  çizdiğini değil, istenince çizebildiğini ölçüyor.
- Günlük (`F10a-gunluk.md:186`) `rehber/goruntu/adim-38.png`'ye bakıldığını söylüyor. 00:47'deki son üretimde bu kare boş.

**Yeniden üretme:**
- Üreticinin kullandığı komut, scratchpad'e:
  `chrome --headless=new --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars --window-size=1200,720 --virtual-time-budget=25000 --screenshot=<scratchpad>/s.png "file:///…/rehber/index.html?adim=31&cekim=1&sahne=1&tema=light"`
- Sonuç kararsız. Benim koşularım:
  - ilk koşu: 12 karede 4 boş (31, 38 iki kez, 17);
  - ikinci koşu: 15 karede 1 boş (adım 0);
  - üçüncü koşu: 20 karede 0 boş.
- HEAD sayfası (aynı 0.160 yerel paketle, A'nın "önce" kopyası gibi): 15 karede 0 boş. HEAD'in 50 karesinde de boş yok.
- Aynı sayfa gerçek zamanda (CDP, `toDataURL`) 50 / 50 çiziliyor. DOM'da hata yok, `data-hazir=1`.
- Sonuç: boşluk, sanal zaman altında ekran görüntüsü ile son çizim arasındaki bir yarış. Tuval son çizimden sonra temizleniyor ya da
  son kare sunulmadan görüntü alınıyor.
- Kök nedeni kesinleştiremedim. Denediğim hipotez (`boyut()` içinde `ciz()` yerine `render()`) 20 / 20 dolu verdi. Ama değişmemiş
  sayfa da aynı koşuda 20 / 20 doluydu, yani deney sonuçsuz.

**Önerilen düzeltme (A için):**
- Sayfa: `?cekim=1` kipinde hazır olmadan hemen önce tuvali eşzamanlı çiz (rAF'e bırakma). `ResizeObserver` → `setSize` sonrasında
  da doğrudan çiz.
- Ölçüm:
  - Yazdırma karesi üretildikten sonra piksel denetimi ekle. Zeminden farklı piksel oranı ya da en küçük dosya boyutu; altındaysa
    yeniden çek.
  - `F10a-dogrula`'ya "teslim edilen `rehber/goruntu/` 50 / 50 dolu" ölçütü ekle.
- `rehber_uret.py`'ye dokunmak brief'te yalnız "en küçük değişiklik" olarak izinli. Hangi yolun seçileceğine orkestratör karar
  versin.
- Sonra `--veri-yok` ile yeniden üret. 50 yazdırma karesine ve PDF'in 50 adım sayfasına piksel düzeyinde bak.

### B-2 (engellemeyen). İki kollu tezgâh adımlarında sıkı kadraj yeni parçayı kenara itiyor; oran ölçütü bunu "iyileşme" sayıyor
**Ne:**
- 21 D1c, 43 H0b, 45 H0d ve 46 H0e'de yeni parça sağ ve sol koldaki iki küçük horn ya da flanş. İki kol tezgâhta yan yana ve
  uzak duruyor.
- Kadraj ikisinin birleşik kutusuna sıkışıyor. İki parça karenin sol ve sağ kenarına 20-30 px kalacak biçimde dağılıyor, orta boş.
- Parçalar çoğunlukla önceki adımın gri bloklarının arkasında kalıyor. 21'de iki horn da görünmüyor (HEAD'de de yalnız bir kenarı
  görünüyordu).
- Gri bloklar karenin iki kenarından kesiliyor; HEAD'de iki kol bütün görünüyordu.
- Ölçtüğüm ekran kutuları (1400 × 900, tuval 0-1000 px):
  - 45: horn'lar x 877-973 ve 28-90;
  - 46: flanşlar x 864-972 ve 29-99;
  - 43: x 942-979 ve 19-67.
- Kare dışına taşan yok; ölçüt teknik olarak geçiyor.

**Neden ölçüte yansımadı:**
- `F10a-dogrula.py:185` oranı bütün yeni parçaların **birleşik** ekran kutusundan hesaplıyor. Birbirinden uzak iki küçük parçayı
  kenarlara yaymak oranı büyütüyor: 21: 0,15 → 0,33; 43: 0,14 → 0,31; 45: 0,12 → 0,25; 46: 0,13 → 0,27.
- Bu ölçü görünürlüğü (perdelenme) de ölçmüyor.

**Yeniden üretme:** `rehber/index.html?adim=45&cekim=1&tema=light`, 1400 × 900. Karşılaştırma için `planlama/rehber/goruntu/adim-45.png`
ile HEAD'deki aynı dosya (`git show HEAD:planlama/rehber/goruntu/adim-45.png`).

**Öneri:** brief dışı bir iş, F10d'ye not edilebilir. Seçenekler:
- tezgâhta sağ + sol kopyalardan yalnız birine kadraj;
- yeni parça çok küçükse en az bir alt montaj bağlamı;
- oran ölçüsünü parça başına ya da görünen piksel üzerinden almak.

### B-3 (engellemeyen). A'nın betiği vurguyu kimlikle değil sayıyla karşılaştırıyor
- `F10a-dogrula.py:253-255` ve `:274` `vurgu().sayi == len(ids)` karşılaştırıyor. `vurgu().ids` alınıyor ama satırın `ids`'iyle
  karşılaştırılmıyor.
- Panel satırında beklenen sayı bütün `ids`. Gizli kopya olsaydı ölçüt yanlış kalırdı.
- `vurgu()` sayfanın kendi `VURGU` nesnelerine kimlikle bakıyor (`rehber/app.js:881` ve sonrası). Sahnenin gerçek mesh'lerini okuyor;
  bu yönüyle sayfanın kendi durumu değil. Ama yalnız sayı döndüğü için yanlış parçanın vurgulanması yakalanmazdı.
- Benim kimlik bazlı ölçümüm 7 / 7 birebir çıktı. Yani sayfa doğru; zayıf olan betik.
- `tikNoktasi` tıklama noktasını sayfanın kendi `isabet()`'iyle buluyor. Tıklamanın kendisi gerçek fare olayı olduğu için bu kabul
  edilebilir.

### B-4 (engellemeyen). Kadraj, patlat sonrasındaki toplam kutuda kalıyor
- 33'te patlat → bütün satırlar tak dendiğinde kamera patlak kutuya göre kalıyor, robot karenin ortasında küçük görünüyor
  (`scratchpad/f10a-b/tak-33-koyu-saydam-son.png`).
- V (görünüm) sıkı kadraja döndürüyor.
- A bunu kısmen yazmış ("F1'de bantlar 630-830 mm açılıyor"). Topla (P) ya da son satır takıldığında yeniden kadraj düşünülebilir.

### B-5 (engellemeyen). "Saydam" tek başına 31 ve 33'te içeriyi göstermiyor; içerisi tak sırasıyla görünüyor
- 31 ve 33'te yeni parçanın kendisi kabuk. Önceki adımlar saydam olsa da yeni kabuk opak kalıyor, içerisi görünmüyor
  (`kip-33-acik-saydam.png`).
- İçerisi ancak patlat + tak ile, önceden takılan satırlar saydamlaşınca görünüyor. 31'de QLED ve kablolar, 33'te etek içi;
  kendi karelerimde baktım.
- A günlükte bunu açıkça yazmış; brief'in "içerideki yeni parçalar görünür" isteği tak kipinde karşılanıyor.
- Ahmet'e "saydam + tak" diye anlatılmalı; yalnız saydam kutusu beklentiyi karşılamaz.

### B-6 (engellemeyen, sapmaların değerlendirmesi)
- **Yazdırma görüntüsünde küçük görünüm:** gerçek zamanlı ölçümde 50 / 50 adımda yeni parçayı örtmüyor. Kâğıtta bağlam veriyor;
  kabul edilebilir. B-1 düzelince yeniden bakılmalı.
- **Etiketin yeri (araç çubuğunun altı):** 1400 ve 360 px'te araç çubuğuyla çakışma yok, kabul edilebilir.
- **`window.RehberTest` kancası:**
  - Yalnız mevcut nesnelere başvuru ve sayfanın kendi işlevlerini (patlat, tak, öncekiler, küçük görünüm) dışarı veriyor.
  - Ağ açmıyor, dışarı veri göndermiyor.
  - Çağrılmadığı sürece davranışı değiştirmiyor. `miniOlc()` çağrılınca bir `render()` yapıyor; zararsız ama ölçümü yumuşatıyor
    (B-1).
- **URL parametreleri** `?patlat=1&tak=N`, `?onceki=`, `?mini=`: zararsız.

## Yan etkiler ve gizlilik
- `git status --short`: A'nın değişiklikleri izin verilen alanda.
  - `rehber/app.js`, `index.html`, `stil.css`, yeni `rehber/vendor/` (2 dosya);
  - `rehber/goruntu/adim-*.png` (50, üretici; `rehber/` içinde);
  - `planlama/rehber/kontrol.json`, `goruntu/` (57), PDF;
  - `planlama/d158/F10a-*` (brief ve bu dosya hariç 27 dosya).
- Öbür değişiklikler A'nın değil:
  - oturum öncesinden: `tasarim/freecad/kabuk/gorsel/*.png`, `montaj/yerlesim-kontrol.json`, `dongu-158.md`;
  - izlenmeyen `kvkk/`, `rapor/`, `tubitak-2209b/`, `tasarim/solidworks/`, `raporlar/…`, `tasarim/cad/lale158-model.js` (09.11), F5 pano
    metinleri (08.11);
  - `F10c-brief.md` ve `FREECAD-KILIT.txt` orkestratör ya da F10b'nin.
- `rehber_uret.py` değişmemiş.
- Yerel kullanıcı klasörü yolu ve takma ad taraması (kullanıcı klasörü adı, bulut eşitleme klasörü, masaüstü ve geçici klasör yolları, takma ad deseni).
  - Taranan dosyalar: `F10a-gunluk.md`, `F10a-dogrula.py`, `F10a-dogrula.json`, `rehber/app.js`, `index.html`, `stil.css`, `vendor/`,
    `kontrol.json`, PDF.
  - Sonuç: 0. Betik geçici klasörü yalnız çalışırken kullanıyor, JSON'a yazmıyor.

## Ölçülmeyenler
- `F9b-dogrula`, `carpisma_kos kontrol`, regresyon: üretici ve model zinciri yeniden koşulmadı. A'nın 0 / 0 / 10 / 10'u
  doğrulanmadı. Model değişmediği için risk düşük.
- Kadrajın "önce" (HEAD) ortancası 0,1733: yalnız A'nın sayısı, ben "sonra"yı ölçtüm. B-2'deki adımlar için HEAD karelerine gözle
  baktım.
- Vendor dosyasının npm `three@0.160.0` derlemesiyle bayt bayt aynılığı: internetsiz ölçüm. Başlık ve `REVISION` tutarlı.
- Gerçek dokunmatik cihaz ve gerçek GitHub Pages: ölçülmedi; mobil öykünme ve yerel http alt dizini ile ölçüldü.

## Bakılan kareler (Read ile)
- **Etkileşimli, 1400 px:**
  - açık: 12, 17, 44;
  - koyu: 12, 17, 31, 33, 44.
- **360 px:** 31.
- **Saydam + tak:**
  - 31: iki satır sonrası ve tamamı;
  - 33: tamamı;
  - 33 saydam, tak yok.
- **Yazdırma:**
  - `rehber/goruntu/` 17, 31, 38 (boş), 05 (dolu);
  - scratchpad: 17 dolu, 45 (B-2);
  - PDF sayfa 34 (boş).
- **Kontrol kareleri:**
  - `planlama/rehber/goruntu/` 17, 45, 46;
  - HEAD'deki 21, 43, 45;
  - `F10a-goruntu-44-acik-secim.png`.
- Seçim yeşili açık ve koyu temada okunuyor, panel satırı işaretli.
- Koyu ve açık temada üst üste binen yazı ya da okunaksız öğe görmedim.
