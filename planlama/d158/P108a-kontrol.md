# P10.8a: kupon dosyaları · bağımsız kontrol

Tarih: 19.11.2026 · dal `lale-duzeltme`, HEAD = uzak = `e3aaf94` · paket çalışma ağacında, commit'siz. Bu kontrol yalnız bu dosyayı yazdı.
Kaynaklar: `P108a-gunluk.md`, `karar-kuyrugu.md` K29 / K31 / K42 / K43 / K54 / K55, `P109c-gunluk.md` § 4, `F10d-gunluk.md` § 11.5.

**Karar: DÜZELTMEYLE GEÇER.** Kupon dosyaları doğru ölçüyü taşıyor, STL'ler sağlam, M7 STEP'inde D1 / D2 / E geometrisi HEAD ile aynı,
Kupon B'nin değişmesi kararla uyumlu, gizlilik temiz. Düzeltilecekler ölçüde değil, kuponla rehber ve baskı listesi arasındaki
bağda: K55 kuponunun denediği yol rehberin yazdığı yol değil (O1), K55'in rehberde kupon sözü verilen öbür bantları yok (O2),
D1 / D2 / E'nin eskidiği baskı listesinde yazmıyor (O3).

## 1. Bulgular

### ORTA

**O1. K55 kuponu rehberin yolunu denemiyor. Rehber cümlesi de geometriye göre ters.**
- Kupon (`test/README.md` K55, `kabuk/bant_kuponu.py`): üst parça yukarıdan (+y) indiriliyor. Dudak dilin dışından geçiyor.
- Rehber F3 (`rehber-veri.json` adım 35, grup 0): "Göğüs bandı sağı +x'ten getir … Bandı hafifçe esneterek dilini orta bandın arkasına sok".
  F10d § 11.5'e göre +x yolunda orta bantla ortak hacim 1–159 mm. +y yolunda 1–13 mm.
- Geometri: dil orta bandın iç yarısı. Göğüs bandının alt kenarı dış yarı (dudak), dilin dışında kalıyor. `bant-kuponu.json`'da yan hatta
  dil x 147,1–148,4, dudak 148,6–150,1. Yani orta bandın dili göğüs bandının arkasına giriyor, tersi değil. Aynı kalıp F3 grup 1'de, F4'te
  (omuz) ve çerçeve cümlesinde de geçiyor ("dilini göğüs bandının arkasına sok").
- Girişim "hafifçe" sözünü karşılamıyor. Kalan iniş 10 mm'de önde 6,8 mm, ön-yan köşede (60°) 7,8 mm (§ 3.4).
- Etki: kupon geçse bile rehberdeki "+x'ten getir" talimatını doğrulamaz.
- Öneri: kupon sonucu yazılırken rehber F3 / F4 takma metni kupondaki yola göre yeniden yazılsın (yukarıdan indir, alt kenar alttaki
  bandın dilinin dışından geçer). Rehber üretimli sonraki pakete ve kuyruğun K55 "Uygulaması açık" satırına not düşülsün.
  Bu kontrol rehbere dokunmadı.

**O2. K55'in kupon kapsamı rehberin verdiği sözden dar.**
- Rehber, K55'in dört bandının sekiz yarısında "baskı kuponunda denenir" diyor.
- F1 (adım 33, grup 2 ve 4) etek ön için ayrıca şunu yazıyor: "kuponda bu bant ayrıca, somun takılıyken denenir". Böyle bir kupon yok.
- Paket yalnız göğüs | orta dikişinin sağ yarısını kesti. Gerekçesi (`bant_kuponu.py:8-9`, günlük § 4.3) makul: dil, boşluk ve duvar
  bütün bantlarda aynı.
- Kuponda olmayanlar: x = 0 dikişi ve sol yarı. F10d'ye göre sol göğüs bandının +y yolunda sağ bantla 1–19 mm ortak hacmi var.
  Omuz ve çerçeve de kuponda yok.
- Öneri: ya etek ön (perçin somunuyla) ve sol yarı için kupon eklensin, ya da rehber ve kuyruk "yalnız göğüs | orta sağ denendi,
  öbürleri bu sonuçtan çıkarım" desin. Karar sahibinde.

**O3. D1 / D2 / E'nin eskidiği yalnız README'de ve JSON'da yazıyor.**
- `test/README.md` uyarısı ve `m7-kupon-sonuc.json` `yalniz_c` alanı doğru.
- Ama `planlama/baski-listesi.md` Parti 0 tablosu ve `F4c-partiler.md` D1 / D2 / E'yi uyarısız listeliyor. Parti 0'ı basan kişi bu listeyi okur.
- JSON'da saklanan arayüz değerleriyle bugünkü `arayuz.py`'yi karşılaştırdım. Saklanan `DIRSEK` alanlarından yalnız `tup_uc_y`
  değişmiş (−140 → −170). `GECME` (0,25 / 0,25 / 0,3) ve `TUP_PIM_R` (25,4) aynı.
- Radyal geçme denemesi büyük olasılıkla hâlâ anlamlı. Çatal diliminin bugünkü dirsek çatalıyla aynı olduğu doğrulanmadı.
- Öneri: baskı listesinin Parti 0 bölümüne tek satır eklensin: "D1 / D2 / E 15.10 dirseğinden (Y2a öncesi). Basmadan önce
  `m7_kuponlari.py` D / E bölümü güncellenmeli ya da bilerek eski hâliyle basılmalı."

### DÜŞÜK

**D1. Yanak kuponu: 625ZZ yoksa sol yanakta dinlenmede temas yok.**
- Mastarın dayaması r 4. Sol yanağın iç yüzünde Ø16 rulman yuvası var: 5 mm derin, dibi x −29,2.
- STL ışın ölçümünde yuva hizasında aralık 59,4 (1102 ışından 60'ı), öbür her yerde 54,4.
- 625ZZ olmadan dayama yuvaya düşer. Bu durumda README adım 3'teki "eksenler hizalanana kadar" ve adım 4'teki sol sentil ölçümü anlamsız.
  İnişteki sıfır boşluk yalnız yuvanın altındaki şeritte sınanır (eksenden 8–16 mm).
- Öneri: README'ye "sol taraf ölçümü için 625ZZ şart" cümlesi eklensin, ya da adım 4 yalnız sağ taraf için yazılsın.

**D2. M5 çap aralığı tek yönlü.**
- Denenen çaplar 6,6 / 6,7 / 6,8. Satıcı kuralı 6,7–6,8. Üst tarafta deneme yok, oysa PETG-CF'de basılan delik genelde küçük çıkar.
- Görüş: B'deki üç delikten biri ya da C'deki damlalardan biri 6,9 olabilir. Delik sayısı ve K43 sayımı değişmez.

**D3. Kupon tazeliğini otomatik yakalayan denetim yok.**
- Yanak ve bant betikleri ölçüyü gerçekten kaynak FCStd'den okuyor. Gömülü sabit yalnız kutu payları, ölçüm hatlarının konumu ve
  M5'in yerel çapı (bilerek; `assert A.INSERT[5] == (7.0, 7.0)` insert değişirse durdurur).
- JSON'lar kaynak md5'i tutuyor, ama hiçbir betik bunu karşılaştırmıyor. `carpisma_kos.py` izlediği 17 dosyada kuponları saymıyor.
- Kafa iskeleti ya da bantlar değişirse kupon, betik yeniden koşulana kadar eski kalır.
- Öneri: K54 b / K55 b paketlerinin iş listesine "kupon betiğini yeniden koş" maddesi, ya da md5 karşılaştıran küçük bir denetim.

**D4. `m7-kupon-sonuc.json` `arayuz` bloğu karışık tarihli.**
- `INSERT_DELIK` 19.11'de bugünkü arayüzden yeniden yazıldı. `DIRSEK` (`tup_uc_y` −140) 15.10'dan kaldı.
- `yalniz_c` alanı durumu açıklıyor, ama blok okura tek tarihliymiş gibi görünüyor.

**D5. Eski Parti 0 sayıları tarihsel dosyalarda kalıyor.**
- `F4c-rapor.html`, `F4c-gunluk.md`, `F4c-kontrol.md` ve `karar-kuyrugu.md:810` eski sayıları anıyor (fark ≤ 0,6 g).
- Bu sayıları denetleyen bir betik yok.
- `sonuc-rapor.html`'de yalnız "≈ 7,3 sa" var ve bu sayı değişmedi. Demoda ve rehber verisinde Parti 0 sayısı yok
  (`rehber-veri.json`'daki "257.6" eşleşmeleri koordinat).

**D6. Parti 0 gününün baskı yükü tabloda görünenden fazla.**
- Yanak ve bant kuponları (≈ 2,5 sa, 88–142 g PETG) Parti 0 toplamına katılmıyor. Baskı listesi bunu açıkça yazıyor; yalnız bilgi.

## 2. Açık görüşler

**M7 yaklaşımı: kabul edilebilir.**
- `m7-kuponlari.step`'te D1 / D2 / E gövdeleri HEAD ile geometrik olarak aynı: hacim, sınır kutusu, yüz ve kenar sayısı aynı, simetrik
  fark 0 mm³.
- STEP'te iki sürümde de yalnız genel bir ürün adı var. Yani yeniden yazılan etiketler bilgi kaybettirmedi.
- STEP'e hiç dokunmamak C gövdesini eski delik çaplarıyla (Ø6,4) bırakırdı. Dosya STL ve JSON'la çelişirdi.
- A, D1, D2, E STL'leri bayt bayt aynı. JSON'da D / E kayıtları değişmemiş.
- Kipsiz (varsayılan) koşudaki fark yalnız amaçlananlar: C'nin M5 çapları, damla adımı ±0,1 ve yeni `k31_m5` anahtarı.
  Yeniden düzenlenen `baski_kontrol` / `kupon_bilgi` / `toplam` kodu satır satır öncekiyle aynı.
- Tam kipin D / E hatasını statik olarak doğruladım: `Y_KAPAK` −148 sabit, `DIRSEK.tup_uc_y` −170. Tam kipi koşmadım.
- Eksik olan tek şey O3'teki baskı listesi uyarısı.

**Kupon B'nin değişmesi: doğru ve gerekli.**
- K31'in M5 satırındaki "Ø6,2 / 6,4 / 6,6, derinlik 7,5" kupon B'nin değerleri. Kupon C'nin derinliği 8,0.
- K43'ün teknik yarısı "delikler Ø6,7–6,8" diyor. Yalnız C'yi büyütmek B'yi yeni insertle denenemez bırakırdı.
- Kuponun asıl değerden (`arayuz.INSERT_DELIK[5]` 6,4) farklı çapla basılması deneme mantığına uygun: kuponun işi asıl değeri seçmek.
- Bu fark `test/README.md`'de, `tolerans_kuponu.py` başlığında ve `F4c-partiler.md` K31 tablosunda açıkça yazıyor.
- Risk: M5'li asıl parçalar (ön kol gövdesi, eğme çatalı, omuz göbeği) CAD güncellenmeden basılırsa delik 6,4 kalır. Parti planı
  "Parti 0 sonucu CAD'e girip STL çıkınca" kapısını koyuyor.

## 3. Ölçümler (bağımsız yol)

### 3.1 STL sağlamlığı
FreeCAD Mesh ile okundu: `isSolid`, `hasNonManifolds`, `hasSelfIntersections`, bileşen sayısı.

| STL | Kapalı | Manifold dışı | Öz kesişim | Bileşen | Ölçü (mm) |
|---|---|---|---|---|---|
| `kafa/stl/yanak-kuponu.stl` | evet | yok | yok | 1 | 72,4 × 40 × 48 |
| `kafa/stl/yanak-kuponu-mastar.stl` | evet | yok | yok | 1 | 30 × 30 × 54,4 |
| `kabuk/stl/bant-kuponu-alt.stl` | evet | yok | yok | 1 | 161,8 × 214,2 × 23,4 |
| `kabuk/stl/bant-kuponu-ust.stl` | evet | yok | yok | 1 | 164 × 217,2 × 20 |
| `test/stl/kupon-b-yuva-mil-somun.stl` | evet | yok | yok | 1 | 200 × 95 × 11 |
| `test/stl/kupon-c-isil-gomme-L1.stl` | evet | yok | yok | 1 | 61 × 17,2 × 14 |

### 3.2 Delik çapları (STL kesit poligonunun genişliği)

| Kupon | M5 | M3 | HEAD'de M5 |
|---|---|---|---|
| B, z 7, dikey | 6,6 / 6,7 / 6,8 | 3,8 / 3,9 / 4,0 / 4,1 (değişmedi) | 6,2 / 6,4 / 6,6 |
| C, y 14, yatay | yuvarlak 6,7; damla 6,6 / 6,7 / 6,8 | (y 3) 4,0; 3,9 / 4,0 / 4,1 (değişmedi) | 6,4; 6,2 / 6,4 / 6,6 |
| C, z 10, dikey | 6,7 | 4,0 (değişmedi) | 6,4 |

Damla yükseklikleri r(1 + √2) ile tutuyor: 6,6 için 7,97.

### 3.3 Yanak kuponu ve mastar
- **Yanak kuponu (STL):** x'e paralel 1102 ışın attım. Aralık 1042 ışında 54,4, 60 ışında 59,4 (rulman yuvası hizası, D1).
  Yanaklar sol −35,2…−24,2, sağ 30,2…35,2.
- **Kaynak (`kafa-montaj.FCStd`, mesh + ışın):** yanak iç yüzleri −24,2 ve 30,2. 625ZZ iç bileziği −29,2…−24,2, horn 26,9…30,2.
  Yığın 54,4, aralık 54,4, fark 0.
- **Mastar (STL):** boy 54,4. z 0,5–3,2'de r ≈ 12,5 (horn diski), z 20'de r 15, z 53,9'da r 4 (dayama).

### 3.4 Bant kuponu ve K55 girişimi
**Duvar katmanları (STL, x ışınları, en dıştaki aralık, en sık değer):**

| Parça | Kesit | Kalınlık |
|---|---|---|
| alt | z 5 (dikiş altı) | 3,0 (88 ışın) |
| alt | z 13 / 16 / 20 (dil) | 1,25 (94–99 ışın) |
| üst | z 3 / 6 / 10 (dudak) | 1,5 (96–102 ışın) |
| üst | z 16 (tam duvar) | 3,0 (105 ışın) |

**K55 girişimi.**
- Yöntem: kaynak FCStd'deki tam bantlar (dilim değil), y düzleminde kesit. Gövde merkezinden açılı ışınlarla alttaki bandın dil dış
  yarıçapı ile üstteki bandın dudak iç yarıçapı karşılaştırıldı.
- Bu, uygulama ajanının eksene paralel hat yönteminden farklı bir yol.
- Pozitif değer girişim demek. Açı +x'ten (yan) +z'ye (ön) doğru ölçülüyor.

| Kalan iniş | 0° (yan) | 30° | 60° | 75° | 90° (ön) | −30° |
|---|---|---|---|---|---|---|
| 0 mm (dinlenme) | −0,25 | −0,29 | −0,29 | −0,26 | −0,25 | −0,29 |
| 2 mm | 0,48 | 0,26 | 1,33 | 1,19 | 1,15 | 0,26 |
| 6 mm | 1,43 | 1,36 | 4,57 | 4,09 | 3,95 | 1,36 |
| 10 mm | 2,13 | 2,46 | 7,80 | 7,00 | 6,76 | 2,46 |

- Uygulama ajanının değerleri (önde 6,8, yanda 2,1) doğrulandı. En büyük girişim ön-yan köşede: 10 mm'de 7,8.
- Arka bölümde (−60°, −90°) ışın arka kapak açıklığına düştü, ölçemedim.
- Tam bantlarla ortak hacim (mm³): 2 mm'de 2221, 6 mm'de 1458, 10 mm'de 262, 13 mm'de 0,37, 14 mm'de 0. Kupon dilimiyle aynı.
- Bu ölçüm rehberin F3 adımını etkiliyor: O1.

### 3.5 STEP (HEAD ↔ çalışma ağacı, `Part.read`)

| Dosya | Gövde | Hacim (mm³) | Yüz / kenar | Simetrik fark |
|---|---|---|---|---|
| m7 | C | 10 554,7 → 10 426,6 | 81 / 155 aynı | 128 mm³ (amaçlanan) |
| m7 | D1 | 69 176,9 | 43 / 121 | 0 |
| m7 | D2 | 67 844,9 | 56 / 169 | 0 |
| m7 | E | 14 126,0 | 6 / 12 | 0 |
| tolerans | A | 20 457,6 | 38 / 106 | 0 |
| tolerans | B | 69 207,2 → 69 138,1 | 157 / 294 | 69 mm³ (amaçlanan) |

Sınır kutuları bütün gövdelerde aynı.

### 3.6 Bayt düzeyi
- A, D1, D2, E STL'leri HEAD ile aynı md5.
- `F4c-partiler.py`, çıktısı depo dışına yönlendirilerek yeniden koşuldu. JSON ve MD, çalışma ağacındakilerle bayt bayt aynı.
- Kaynak FCStd'ler ölçümden önce ve sonra aynı md5: kafa `777c6b27…`, kabuk `54273a1b…`.

## 4. Koşulan adımlar

| Komut | Çıkış | Sonuç |
|---|---|---|
| `tasarim/freecad/carpisma_kos.py kontrol` (başta ve sonda) | 0 / 0 | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| `git diff --quiet HEAD`: `arayuz.py`, `karar-kuyrugu.md`, `dongu-158.md`, `sonuc-rapor.html`, demo, `maliyet.json`, iki kaynak FCStd, `rehber/` | hepsi 0 | değişmemiş |
| `planlama/d158/F4c-dogrula.py` | 0 | SONUC: GECTI (2, 3, 4a, 4b, 5a, 5b, 6); 74 adet, 7722,7–7780,5 g |
| `planlama/d158/F9b-dogrula.py --tarayicisiz` | 0 | GECER (hata 0) |
| `planlama/d158/F9c-dogrula.py --tarayicisiz` | **1** | 3 hata, üçü de git geçmişi kaynaklı: komit sayısı sayfada 108 / hesapta 109, eşleşmeyen 2 / 3, `e3aaf94` commit hücresinde yok. Sayfayı üreten commit'in kendisi sayfada olamaz; paketle ilgisi yok. Parti 0 ya da kuponla ilgili hata yok. Sonraki sayfa yenilemesinde kapanır |
| `F4c-partiler.py` (çıktı depo dışına) | 0 | depodakiyle bayt bayt aynı; Parti 0 257,4–420,0 g, 7,32–11,94 sa |
| FreeCAD 1.1.4, iki salt okunur ölçüm betiği (çıktı depo dışına; loglar okundu) | 0 / 0 | § 3 |
| `git status` (koşulardan önce ve sonra) | — | aynı (40 satır) |

Baskı listesini ya da partileri okuyan zincir adımlarını grep ile aradım: `F4c-dogrula`, `F4c-liste`, `F4c-kontrol-sayim`,
`baski_listesi_guncelle`, `F9c-uret` (yalnız `partiler.N.toplam.adet` okuyor; adet değişmedi). F10a / F10d / F10e / F10f /
F10l-birlesim bu dosyaları okumuyor; F10l'deki eşleşmeler rehber metni. `F4c-kontrol-sayim.py` depoya yazdığı için koşulmadı. Girdisi
`kupon_c_delikler` M3 5 / M5 5 ve betikteki kupon B sayısı M3 4 / M5 3; ikisi de değişmedi.

## 5. Gözle bakılanlar

Görüntüler depo dışında, STL'den çizildi.
- **Yanak kuponu:** tabla dilimi tablada, iki yanak dik. Sol yanakta Ø16 yuva, sağda horn delikleri. Yatay deliklerin tepesi köprü
  (asıl parçayla aynı), ince duvar yok, desteksiz basılabilir.
- **Mastar:** horn diski tablada, 45° koni, r 15 gövde, tepede r 4 dayama. Desteksiz.
- **Bant alt / üst:** sağ yarının L / U şeridi. Ön kol tam, arka kol arka kapak kesiği yüzünden kısa, iç yüzde boss'lar var. Alt parçada
  1,25 mm'lik dil 3 mm duvarın üstünde. Üst parçada z 12'de iç yarıda 1,5 mm'lik yatay basamak var. Asıl göğüs bandında da aynı yerde
  ve "destekli" yazısıyla uyumlu.
- **Kupon B:** dört 625ZZ deliği, dört Ø40 mil, M3 ve M5 blokları, nokta işaretleri yerinde.
- **Kupon C:** M5 yatay delikleri +Y yüzünde (yuvarlak + üç damla), dikey delikler üst yüzde. Şekil mantıklı.

## 6. Bakılmayanlar

- Tam kip `m7_kuponlari.py` koşulmadı. D / E hatası yalnız statik olarak doğrulandı.
- Hiçbir kupon basılmadı. Süre ve kütle tahmini; dilimleyiciyle bakılmadı.
- Kuponların esneme davranışı modellenmedi. Destek z 12 basamağından temiz çıkar mı bilinmiyor.
- +y iniş yolunun öbür parçalarla (braket, ekran, kablolar) serbest olup olmadığını yeniden ölçmedim. F10d tablosu +y'de yalnız
  orta bandı engel gösteriyor.
- K55 girişiminin arka bölümü ölçülemedi.
- Tarayıcılı denetimler (F9b / F9c `--goruntu`), F10a / F10d / F10e / F10f, `regresyon.py`, montaj betikleri ve rehber üretimi koşulmadı.
- Yanak kuponunun kaynakla nokta nokta aynılığı denetlenmedi. Yalnız ışın aralıkları ve sınır kutusu karşılaştırıldı.

## 7. Gizlilik

`.git/hooks/pre-push` kalıpları uygulandı: anahtar, parola ataması, e-posta, IBAN / telefon, yerel yol, takma ad, ekip soyadı.
Taranan metin:
- çalışma ağacı farkının eklenen satırları (10 izlenen dosya),
- beş yeni metin dosyası.

Toplam 1771 satır, **eşleşme 0**. Yeni dosya adları yasak yol kalıplarına uymuyor.

`m7-kuponlari.step`'te telefon kalıbına uyan tek dizi (bir koordinat ondalığı) HEAD'de de var, çalışma ağacında da. Eklenen satırlarda
0. `tolerans-kuponu.step`'te 0. Betik yorumlarındaki ev dizini kısaltması kanca kalıbına uymuyor ve kişisel bilgi taşımıyor.

## Tur 1 kontrolü (19.11.2026, düzeltme turu 1'den sonra)

**Karar: DÜZELTMEYLE GEÇER.** O1–O3 ve D1–D4 kapandı. Tek düzeltme: `dongu-158.md` P10.8 hücresindeki kaçışsız `|` plan tablosunu
bozuyor (T1-1).

### Bulgular

**T1-1 (ORTA). Plan tablosu satırı bozuldu.**
- Yer: `planlama/dongu-158.md` P10.8 satırının Durum hücresi, "K55 a bant kuponu (orta | göğüs sağ yarı; …)".
- Kanıt: satırdaki `|` sayısı HEAD'de 6, şimdi 7. Hücre bölünüyor.
- `F9c-uret.py` (`plan_paketleri`, `durum = h[-1]`) ve `F9c-dogrula.py` durumu son hücreden okuyor. Son hücrede emoji olmadığı için durum
  "?" çıkıyor.
- `F9c-dogrula --tarayicisiz` artık 6 hata veriyor; ilk turda 3 hata vardı. Yeni üçü:
  - `paket_⏳` sayfada 1, hesapta 0;
  - "paket P10.8 durum hücresi plandaki ?'yi içermiyor";
  - "faz F10 durum hücresi …".
- Commit sayısından gelen üç hata aynı kaldı. Sayfa bir sonraki üretimde de P10.8'i yanlış okur.
- Öneri: o hücrede "orta | göğüs" yerine "orta–göğüs" yazılsın (ya da `\|`). Sonra `F9c-dogrula --tarayicisiz` 3 hataya inmeli.
- Kuyruk, baskı listesi ve README'deki aynı ifade tablo dışında olduğu için zararsız.

**T1-2 (DÜŞÜK). "BİLİNEN ESKİ" yeni bir eskimeyi maskeleyebilir.**
- `kupon_tazelik.py`, bir farkı yalnız anahtar adı `yalniz_c.neden` metninde geçiyor diye bilinen sayıyor; değere bakmıyor.
- Depo dışı kopyada `DIRSEK.tup_uc_y` −180 yapıldı. Sonuç yine "BİLİNEN ESKİ", çıkış 0.
- Ad eşleşmesi alt dize araması: kısa anahtar adları (ör. `INSERT_DELIK.5` → "5") metinde geçerse başka farklar da yanlışlıkla
  "bilinen" sayılabilir. Bugün eşleşen yok.
- Öneri: bilinen farkı JSON'daki `arayuz_fark_bugun` değeriyle tam karşılaştır (anahtar ve bugünkü değer aynıysa bilinen).

### Kapandı mı

| Madde | Durum | Not |
|---|---|---|
| O1 | kapandı | README'de iki yol ve karar ağacı. +x denemesi yarım kuponla yapılabilir: iki U dilimi yanyana kaydırılabiliyor, yol boyu ortak hacim beklenen sonuç. `bant-kuponu.json` `inis_x` 1–160 mm'de çakışıyor, 170'te serbest; F10d tam bant 1–159 / 173 ile uyumlu. Ters dil cümlesi ve yol sorusu kuyrukta açık iş, önerilen cümle geometriye uygun |
| O2 | kapandı (kupon yok, gerekçe kayıtla tutarlı) | Etek ön engeli z +105 braketinin perçin somunu; F10d +z 1–7 mm ve kuyruk K55 F10e notuyla aynı. Braket `arayuz.KABUK_ETEK_BRAKET` t 2,0, notu "2 mm Al L"; perçin somunu M3, delik Ø5,1 (`arayuz.py` etek braketi). Rehber F1 (adım 33, grup 2 / 4) sözü kuyrukta açık iş olarak duruyor |
| O3 | kapandı | Uyarı üreticide: `m7_eski_uyari`, bugünkü `arayuz.py` ile fark hesaplıyor, `yalniz_c` yoksa boş dönüyor. `F4c-partiler.md`'de ve `baski-listesi.md`'de birer kez var |
| D1–D4 | kapandı | 625ZZ şartı ve 59,4 açıklaması README'de; 6,9 notu var; `kupon_tazelik.py` yazıldı (T1-2 dışında doğru); JSON'da `arayuz_kosu` ve `arayuz_fark_bugun` var |

### Denetimler

| Komut | Çıkış | Sonuç |
|---|---|---|
| `kupon_tazelik.py` (depo) | 0 | 6 TAZE, 1 BİLİNEN ESKİ |
| `kupon_tazelik.py` (depo dışı kopya, yanak JSON'unda kaynak md5 bozuk) | 1 | ESKİ VAR |
| `kupon_tazelik.py` (kopya, bant alt STL'ye bayt eklendi) | 1 | |
| `kupon_tazelik.py` (kopya, `tup_uc_y` −180) | 0 | maskelendi (T1-2) |
| `F4c-dogrula.py` | 0 | GECTI |
| `F4c-partiler.py` (çıktı depo dışına) | 0 | depodakiyle bayt bayt aynı; 74 adet, 7722,7–7780,5 g |
| `F9b-dogrula.py --tarayicisiz` | 0 | GECER |
| `F9c-dogrula.py --tarayicisiz` | 1 | 6 hata (T1-1) |
| `carpisma_kos.py kontrol` | 0 | kayıtla aynı |
| FreeCAD STEP karşılaştırması | 0 | D1 / D2 / E ve A simetrik fark 0; C ve B yalnız amaçlanan delik farkı |

Depoya yazmadığı denetlenenler:
- `kupon_tazelik.py` depoyu değiştirmedi: `git status` koşudan önce ve sonra aynı. Kod yalnız okuyor.
- `git diff --quiet HEAD` 0 çıkanlar: `arayuz.py`, `maliyet.json`, `sonuc-rapor.html`, `rehber/`, `tasarim/freecad/rehber/`, iki kaynak
  FCStd, `robot-bom.csv`, `Y2b-baski.json`.
- Kupon STL'lerinin md5'i ilk bakışla aynı: A, B, C, D1, D2, E, yanak, mastar, bant alt / üst.

Kuyruk ve plan farkı:
- **Kuyruk:** yalnız ekleme (25 satır, "Karar değil, iş" sonunda). `## K` başlığı 67, KAPANDI 40: HEAD ile aynı. "Durum" satırı eklenmedi.
- **Demo:** tek satır değişti; içinde yalnız kuyruk sha256'sının ilk 12 hanesi (`c25cfb2c9027` → `cb7998d71614`). Değer bugünkü kuyrukla
  tutuyor.
- **Plan:** yalnız P10.8 hücresi ve § 5'te bir satır. İfade doğru ("hazır (19.11), basılmadı / denenmedi"). `sonuc-rapor.html`'in
  yenilenmemesi kendi başına yeni bir kırılma getirmiyor; F9c'deki yeni hatalar T1-1'den.

Dosya listesi ve gizlilik:
- **Dosya listesi:** 19 eski kir dışında `git status` tam olarak verilen 16 değişen + 11 yeni dosya. `__pycache__`, `FREECAD-KILIT.txt`
  ve `.FCBak` gibi dosyalar `.gitignore`'da; listede yok.
- **Gizlilik:** kanca kalıpları 2315 eklenen ya da yeni satıra uygulandı, eşleşme 0. STEP'lerde eklenen satırlarda telefon kalıbı 0.

### Bakılmayanlar

- `F4c-liste.py` yeniden koşulmadı (depoya yazar). `F4c-dogrula` 5a / 5b'nin geçmesi ve uyarının listede bir kez olması yeterli sayıldı.
- Tam kip `m7_kuponlari.py`, tarayıcılı denetimler, F10a / d / e / f ve rehber üretimi koşulmadı.
- T1-1'in düzeltilince F9c'yi 3 hataya indirdiği denenmedi (plan dosyasına yazmak yasak).
