# P10.8g günlüğü: ufak beş (17.1 / 17.5 saplama numarası, basılı 17.11 şema notu, PDF'te etiket yazısı, F9c yapısal 3 hata, `P108f-etiket-olc.py` teslim karesi) (A ajanı)

Paket: P10.8g, A (uygulama). Başlangıç 22.11 02:28 (saat okundu). Dal `lale-duzeltme`, yerel = uzak = `94cd024`. Commit / push / `git add`
yapılmadı (B kontrol, C commit). CAD geometrisi değişmedi: FreeCAD açılmadı, `FREECAD-KILIT.txt`'e dokunulmadı; zincirde `carpisma_kos
kontrol` iki kez 0 (§ 8). Tam çakışma taraması koşulmadı (gerekmedi). Kilit tablosuna satır yazılmadı (orkestratörün alanı).

Kaynaklar: `planlama/d158/karar-kuyrugu.md` "P10.8f kapanışından açık iş" (5 madde), `P108f-gunluk.md` § 2, § 11–§ 13,
`P108f-kontrol.md` § 8, § 10 N3 / N4, `planlama/dongu-158.md` P10.8 hücresi.

## 1. Başlangıç durumu (ölçülen)

| Ne | Değer |
| --- | --- |
| HEAD | `94cd024` (yerel = uzak) |
| Eski kirli dosyalar | 21 (`P108g-olcum/git-status-bas.txt`); `md5sum -c P108f-olcum/kir-bas.md5` 21 / 21 OK |
| `F9c-dogrula.py --tarayicisiz` | GEÇMEZ, **hata 3** (`P108g-olcum/once/F9c-tarayicisiz.log`; § 5) |
| 17.1 / 17.5 saplama numarası | veri `etiket` alanı yok: **0 / 9** ve **0 / 9** (17.4: 9 / 9) |
| Basılı 17.11 şema notu | HEAD PDF s. 26'da "yalnız taban bölümü" metni **yok** (PyMuPDF metin araması) |
| PDF'te etiket yazısı | **B5a 2,42 pt, 17.4 2,51 pt** (em; koyu piksel yüksekliği 2,08 / 1,79 pt) (`once/yazi-pt.log`, § 4) |
| `P108f-etiket-olc.py` B5a | ölçtüğü kare teslim edilen kare değil: farklı piksel **sahne 343.395, etkileşimli 225.649**; 17.4 0 / 0 (`once/eski-olc/teslim-fark.txt`) |
| Önce kareleri | `P108g-olcum/once/kare/` (`adim-*` = yazdırma `rehber/goruntu/`, `etk-adim-*` = etkileşimli `planlama/rehber/goruntu/`) |

## 2. Madde 1: 17.1 ve 17.5 saplama numaraları

`rehber_metin.py`: 17.4'ün deseni ve notu `_SAPLAMA` sabitine alındı; `PARCA_ETIKET[("K1", 1)]` ve `[("K1", 5)]` aynı kalıpla eklendi
(17.1 metni "yıldız barasının ortadaki (3 numaralı) saplaması" ve yığın kuralı, 17.5 metni "anahtarlı baranın 1 numaralı …" diyor).
`etiket_isle` numaraların x'e göre 1..N sırasını iki yeni konumda da denetledi (üretim durmadı). Panel metni değişmedi.

Sonuç (üretim + ölçüm, § 6 / § 7): 17.1 **9 / 9**, 17.5 **9 / 9**, iki kipte; lejantta "A1–A4: … Y1–Y5: …" notu (etkileşimli lejant,
yazdırma karesinin şeridi ve basılı sayfada "Karedeki yazılar:" satırı; PDF s. 23 ve 24'te üç satır, HEAD'de bir). Üretim: "parca
etiketi 4 konumda 28 yazi" (önce 2 / 10). Kadraj dışı yazı: 0 (§ 6'daki "karenin dışında" denetimi dahil).
Etkileşimli lejant notu ikinci satıra indi: kadraj D 17.1 267 → 275, 17.5 733 → 764 (P10.8f'te 17.4'teki D 336 → 349 ile aynı tür).

## 3. Madde 2: basılı lejantta 17.11 şema notu

`rehber/yazdir.html`: `semaOnMetin(g)` (alt adım kartında `lejantMetin`'den sonra): `sira_grup[].sema_on[].not_` varsa app.js lejantıyla
aynı metin, "<şema adı>: <not>". Sonuç: PDF s. 26, 17.11 karesinin altında "ESP32 USB (U06): yalnız taban bölümü (direk dibinden
ESP32'ye); tamamı K2 madde 4'ün karesinde" (8,1 pt satır; HEAD PDF'te yok, şimdi var; s. 26 110 dpi bakıldı). PDF sayfa sayısı 90 aynı.

## 4. Madde 3: PDF'te etiket yazısı

**Ölçüt.** Rehberin kendi ölçütü var: basılı sayfanın en küçük yazısı 8,1 pt (`yazdir.html`; "kare içi lejant ≈ 2,5 pt kalıyordu,
karenin altına ≥ 8,1 pt" emsali F10f) ve `rehber_uret.py` `YAZI_ALT_PT = 8` (PDF metni). Bu kullanıldı (6 pt varsayımına gerek kalmadı).
**Basılı ölçek (PDF'ten ölçüldü):** alt adım karesi 75,9 mm (0,1794 pt/px), ana adım karesi en dar 73,3 mm (B5a s. 13; `GH_MIN`
döngüsünün son değeri 44 mm yükseklik; 0,1731 pt/px). 8,1 pt / 0,1731 = 46,8 → yazdırma karesinde parça etiketi **47 px** (etkileşimli
kip 12 px, değişmedi). `app.js` `ETK` (SAHNE) F 14 → 47, kutu H 22 → 58.

**Yerleşim.** 47 px yazıyla P10.8f'in "önce hemen üstü" açgözlü yerleşimi 17.4 / 17.5'te bağlantı çizgilerini çaprazlıyordu (önizleme
`P108g-olcum/onizleme/ilk/`). `app.js`'e ikinci yerleşim: "radyal" (yazılar noktaların ağırlık merkezinden dışarı, açı sırasıyla, 16
yön). Seçim ölçülür: önce çizilemeyen yazı sayısı, sonra çizgi kusuru (iki çizginin kesişmesi ya da çizginin başka kutudan geçmesi);
eşitse eski yerleşim. Sonuç: 17.1 ve B5a "üst" (eski kural), 17.4 ve 17.5 yazdırma karesinde "radyal", kusur 0; etkileşimli kipte dördü de
"üst" (17.4 / B5a etkileşimli kare HEAD ile bayt bayt aynı). Güvenli alan, çakışma, nokta kuralları değişmedi.

**Sonuç (PDF'ten ölçüldü, `P108g-yazi-pt.py`; `sonra/yazi-pt.log`).** Yöntem: PDF'teki görüntüler çıkarılıp teslim edilen yazdırma
karesiyle piksel eşleştirildi (eşleşme farkı 0,000), ölçek = basılı genişlik / 1.200 px; yazı (em) = ölçülen `yazi_px` × ölçek; ikinci ölçü
PDF'ten çıkarılan görüntüde kutu içindeki koyu piksel yüksekliği.

| Konum (PDF sayfası) | Önce em / koyu yükseklik | Sonra em / koyu yükseklik |
| --- | --- | --- |
| B5a (s. 13) | 2,42 / 2,08 pt | **8,14 / 7,10 pt** |
| 17.1 (s. 23) | yok | **8,43 / 5,92 pt** |
| 17.4 (s. 24) | 2,51 / 1,79 pt | **8,43 / 5,92 pt** |
| 17.5 (s. 24) | yok | **8,43 / 5,92 pt** |

Koyu yükseklik "A1" gibi büyük harf / rakamda ≈ 0,7 em (5,92 pt), "Acil stop düğüm kartı"nda ğ / ü ile 7,10 pt. Hepsi ≥ 8,0 pt (em):
`P108g-yazi-pt.py` GECTI. **Kapsam:** yalnız parça etiketi yazısı. Uç etiketi numaraları (yazdırma karesinde R 13 px daire, 13 px
rakam ≈ 2,3 pt) değişmedi: adları ve numaraları basılı sayfada karenin altında 8,1 pt ("Uçlar:" satırı), karedeki numara yalnız eşleme
işareti; büyütmek 23 konum / 59 etiketin yerleşimini ve F10d'yi değiştirir. Görüldü, dokunulmadı (§ 10).

## 5. Madde 4: F9c'nin yapısal 3 hatası

**Kaydın düzeltilmesi.** `P108f-gunluk.md` § 2 (satır 64), § 11 "Doğrulanmayanlar", § 13 sonu: "TAHMİN" yanlarına ölçülen değer yazıldı
(silinmedi): `f4870bf`'ten sonra 3 (C'nin ölçümü, § 13 adım 1), `94cd024`'ten sonra 3 (bu paketin ölçümü): `komit_sayisi` sayfa 117 /
hesap 118, `komit_eslesmeyen` 2 / 3, "paket P10.8: konu öneki bu pakette olan 94cd024 commit hücresinde yok".

**Neden yapısal (F9c-dogrula.py okundu).** Üç kural HEAD'e kadarki `git log`'la hesaplanır: (1) `komit_sayisi` = F0 tabanından HEAD'e
commit sayısı; (2) `komit_eslesmeyen` = sayfanın hiçbir commit hücresinde geçmeyen döngü commit'leri; (3) konusu `Lale P10.8…` olan her
commit P10.8 satırının commit hücresinde olmalı. Sayfayı içeren commit'in kısa hash'i sayfanın içeriğine bağlı; sayfa onu taşıyamaz, bu
yüzden sayfayı commit'leyen her commit (2) ve (3)'ü, sayıyı da (1)'i bozar.

**Denetimin tanımını değiştirmeden çözüm yok.** Seçenekler:

| # | Seçenek | Değerlendirme |
| --- | --- | --- |
| S1 | **Taban commit'i** (önerilen): üretici sayfaya üretildiği anki HEAD'i yazar (`data-taban`); denetim üç git kuralını `taban`'a kadar hesaplar; `taban..HEAD` aralığı **tek** commit ve o commit sayfayı değiştiren son commit (`git log -1 -- planlama/d158/sonuc-rapor.html`) ise o commit ayrı satırda "sayfanın kendi commit'i" diye raporlanır; aralıkta başka her commit eskisi gibi hata (sayfa bayatlığı yakalanmaya devam eder) | Gerçek bir bayatlığı gizlemez; ama denetimin tanımı değişir (HEAD yerine sayfanın beyan ettiği taban) ve bir commit'i kuraldan ayırır. Görev "tanımı değiştirmeden çözülemiyorsa kapatma" dediği için **uygulanmadı**; `F9c-dogrula.py` ve `F9c-uret.py` değişikliği, orkestratör onayı ister |
| S2 | İçerik özeti: sayfa kaynak dosyalarının özetini taşır, git kuralları kaldırılır | Commit kuralları (eşleşmeyen commit, konu öneki) tamamen kalkar: gevşetme. Reddedildi |
| S3 | Commit'ten sonra sayfayı yeniden üretip `--amend` | Hash değişir, aynı sorun döner (sabit nokta yok); geçmişi yeniden yazma. Reddedildi |
| S4 | Kısa hash'i "madencilikle" sabitlemek (sayfaya X yaz, commit hash'i X ile başlayana kadar ileti değiştir) | ≈ 2^28 deneme; hile, dürüst değil. Reddedildi |
| S5 | Bugünkü uygulama: denetim commit'ten hemen önce 0, commit'ten sonra 3 yapısal sapma kayıtta, sonraki yenilemede kapanır | Değişiklik yok; sayı kayıtta açık durur |

**Öneri:** S1 (orkestratör / Ahmet onayıyla, ayrı küçük paket: `F9c-dogrula.py` + `F9c-uret.py` + bozma sınaması: "taban..HEAD'de ikinci
commit", "taban sayfayı değiştiren commit'in atası değil", "taban git log'da yok"). Onaya kadar S5.

**Bu paketteki ölçüm.** Sayfa yeniden üretildi (`F9c-uret.py` çıkış 0, 155.221 bayt; fark yalnız 2 satır: commit sayısı 117 → 118 ve
P10.8 commit hücresine `94cd024`; elle yazılmış metne dokunulmadı): çalışma ağacında `--tarayicisiz` 3 → **0** (`sonra/F9c-tarayicisiz.log`).
Bu yapısal 3'ün çözümü değil, yenileme: C'nin commit'inden sonra yine **3** beklenir (TAHMİN; üç ölçülmüş emsal `e3aaf94`, `f4870bf`,
`94cd024`). **Madde 4 kapanmadı.**

## 6. Madde 5: `P108f-etiket-olc.py` teslim edilen kareyi ölçüyor

**Bulgu (ölçüldü).** Üretim alt adımı olmayan adımın karesini `rehber_uret.ortak_arg` + `--screenshot` ile çeker. Bu çağrıda sayfa önce
Chrome'un başlangıç görüntü alanında (1200 × 720 pencerede 1182 × 624; 1400 × 900'de 1382 × 804, `--dump-dom` ile ölçüldü) yüklenip çizilir,
çekimden önce görüntü alanı pencere boyuna büyür, kadraj ve etiketler yeniden çizilir. P10.8f aracı DevTools'ta doğrudan 1200 × 720 açıyordu
(farklı kadraj). Aynı çağrının `--dump-dom`'u da büyümeden önceki DOM'u verir (B5a kutusu DOM'da x 52, karede x 342; denendi, kullanılmadı).
**Benzetim:** CDP'de önce başlangıç alanında aç, pencere boyuna büyüt, bekle, çek: `--screenshot` çıktısıyla **piksel farkı 0** (iki kipte).

**Düzeltme (`P108f-etiket-olc.py`).** Alt adım: `rehber_uret.Cdp` ile `alt_kontrol`'ün açma / bekleme / çekim adımları birebir. Alt adımsız:
yukarıdaki benzetim (başlangıç alanı her koşuda ölçülür, sabit yazılmadı). **Her çekim teslim edilen kareyle piksel piksel karşılaştırılır;
fark 0 değilse HATA.** Ek denetim: kutu çekilen karenin (PNG) içinde (tuvalin sayfadaki yeri `RehberTest.etiket().tuval.x / y`, app.js'e
eklendi; ölçülmezse HATA). `--rehber` kopyasında teslim edilen kare yoksa `--teslimsiz` (sonuçta yazar). Kural seti P10.8f'le aynı.
`app.js`'te `RehberTest.etiket()` çıktısına `yazi_px`, `kutu_h`, `yerlesim`, tuval yeri eklendi (sınama arayüzü; çizime etkisi yok).

**B5a yeniden ölçüldü.**
- Önce (HEAD rehberi geçici kopyada, depodaki teslim karelerine karşı; `once/yeni-olc/`): 12 sahne ve etkileşimli **teslim farkı 0 / 0**,
  17.4 0 / 0; yazı 1 / 1 ve 9 / 9 çizilmiş, güvenli alanda, çakışma yok. (HEAD app.js tuval yeri vermediği için 4 "ölçülmedi" satırı;
  beklenen.) B5a'nın teslim edilen karesindeki kutu x 184–337, y 166–188 (P10.8f aracının DevTools karesindeki yerinden farklı).
- Yakalama sınaması: çalışma ağacının app.js'i (47 px) ile eski teslim karelerine karşı: **KALDI**, "ölçülen kare teslim edilen kare değil"
  12 sahne 33.920 px, 17.4 sahne 46.229 px (etkileşimli 0 / 0: 12 px yerleşim değişmemiş) (`ara/teslim-bozma/`).
- Sonra (üretimden sonra, `sonra/etiket-olc.log`): **4 konum, 28 yazı, 8 çekimin 8'inde teslim farkı 0, hata 0, GECTI** (B5a sahne 1 / 1,
  etkileşimli 1 / 1).

## 7. Üretim

`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok`: 02:47:50–03:26:17, **çıkış 0**, Traceback 0 (`P108g-olcum/uretim.log`,
`uretim.durum`). Parça etiketi 4 konum 28 yazı; uç etiketi 24 konum 59 (üretimin sayımı); "rehber_metin alanlari, degisen 0"; alt adım
91 / 91; tarayıcı 50 / 50, konsol 0, "ek kontrol sorunlu: -"; PDF **90 sayfa** (adım 50, devam 40), tasan -, en küçük yazı 8,1 pt
(DOM ve PDF), 19.502 kB. Dosya kilidi hatası yok (PDF 03:03'te yazıldı).

**Ön sınamalar (üretimden önce, `ara/`):** `node --check rehber/app.js` tamam; `rehber_denetim.py --kaynak` 0 (ascii 0, onay farkı 0:
219 / 258 / 1201, CAD ad/kod 973); `rehber_kablo.py` 0 GEÇER; `F10l-birlesim.py` 0 GECER; `P108f-etiket-bozma.py` 0, sağlam 28 yazı,
8 / 8; önizleme kopyasında (`P108g-onizleme.py uc --uc`) `F10d-dogrula.py --yalniz-uc` 23 konum, 59 etiket, hata 0.

**Değişen kareler (`git status`):** `rehber/goruntu/adim-12, -17-01, -17-04, -17-05`; `planlama/rehber/goruntu/adim-17-01, -17-05`
(etkileşimli 12 ve 17-04 bayt bayt aynı) ve gürültü `adim-33-07` (HEAD'e göre 68 px farklı, Σ|ΔRGB| > 24 olan 0, kutu 907…935 ×
743…809, küçük görünüm köşesi; P10.8f'teki gibi). Sonra kareleri `P108g-olcum/sonra/kare/`; PDF sayfaları 13, 23, 24, 26 `sonra/pdf-s*.png`.

## 8. Zincir

`bash planlama/d158/P108g-zincir.sh` (P108f-zincir.sh kopyası, yalnız log yolu), üretimden sonra: 03:26:59–04:22:11, loglar
`P108g-olcum/zincir/`, ilerleme `zincir.durum`. **15 adımın 15'i çıkış 0**, 15 logda Traceback 0.

| # | Komut | Çıkış | Sonuç |
| --- | --- | --- | --- |
| 0a | `carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |
| t1 / t2 | `kupon_tazelik.py` / `--bozma-denemesi` | 0 / 0 | TAZE (16) / 4 / 4 |
| 2a | `rehber_kablo.py --veri …` | 0 | GEÇER |
| 2b | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 136 / 136 |
| 2c | `rehber_denetim.py --kaynak` | 0 | ascii 0, onay farkı 0 (219 / 258 / 1201) |
| 3 | `rehber_denetim.py` | 0 | ascii 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0 |
| 4 | `F10f-dogrula.py` | 0 | GECTI (593 s) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | GECTI (1.028 s); `renk_demo` KALDI (bilinen karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 0 | GECTI (1.037 s); uç etiketi 23 konum, 59 etiket, hata 0 |
| 6g | `F10d-dogrula.py --gizli …` | 0 | bilgi: 103 / 116 (P10.8f ile aynı) |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | GECTI (468 s) |
| 8 | `F9b-dogrula.py` | 0 | GECER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 0 | kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | GEÇER, kötüleşen yok |

Zincirden sonra: `F9c-dogrula.py --tarayicisiz` 0 ve tarayıcılı (görüntü yazmadan) 0 (`sonra/F9c-*.log`); `md5sum -c
P108f-olcum/kir-bas.md5` 21 / 21 OK; `F9c-dogrula.py` ve `carpisma-sonuc.json` HEAD ile aynı (`git diff --quiet`).

**`git status --short` (son, `sonra/git-status-son.txt`):** 35 M + 12 ??. Bunlardan 21'i eski kir (14 M + 7 ??, md5 aynı); paketin
değişikliği 21 M (§ 11 listesi: kaynak 5, çıktı 12, F10 JSON 4) + 5 yeni (`P108g-gunluk.md`, `-onizleme.py`, `-yazi-pt.py`, `-zincir.sh`,
`P108g-olcum/`). Kanıt klasörü 21 MB (önizleme 8,3 MB: dört deneme klasörü `ilk`, `iki`, `uc`, `uc2`; tamamının girmesi şart değil,
orkestratörün kararı; `ilk` reddedilen yerleşimin kanıtı).

## 9. Gözle bakılan kareler (A)

- **17.1** (yazdırma ve etkileşimli): dokuz saplamada A1–A4 / Y1–Y5, yazılar saplamanın hemen üstünde, kadraj içinde, üst üste binen yok.
  Y1 / Y2 saplamaları solda yarı saydam direklerin ardında; yazıları ve noktaları orada (saplama soluk görünüyor). Uç 1 "Yıldız barası"
  Y3'ün yanında (metindeki "3 numaralı saplama" ile tutarlı).
- **17.4** (yazdırma): radyal yerleşim; her yazı kendi saplamasının yanında, çizgiler kesişmiyor, dört uç numarası serbest. A3 ile A4 kutusu
  arka sıranın üstünde; A4 kadraj içinde (P10.8f'teki A4 kadraj dışı hatası yok). Büyük kutular modelin bir kısmını örtüyor.
- **17.5** (yazdırma): dokuz saplama karede ≈ 150 × 100 px'lik bir alanda (uzak kamera); yazılar çevreye açıldı, çizgiler kesişmiyor
  (ölçülen kusur 0) ama küme kalabalık: Y3 ile Y4 kutusu yan yana, çizgileri uç 3'ün yanından geçiyor; okunuyor, eşleme dikkat istiyor.
  Etkileşimli kipte (12 px) dokuzu da saplamanın hemen üstünde, sade.
- **B5a** (yazdırma, PDF s. 13): "Acil stop düğüm kartı" büyük yazısı arkadaki küçük yeşil kartın üstünde, çizgiyle karta bağlı; kutu
  arkadaki siyah kutunun (sigorta kutusu / röle) üst yarısını örtüyor. İki uç numarası yerinde.
- **Lejant sayfası (PDF s. 26):** 17.11 karesinin altında U06 notu var; s. 23 / 24'te 17.1, 17.4, 17.5 altında "Karedeki yazılar:" satırı.
- **Örnek sayfa (PDF s. 24, 110 dpi):** 17.4 ve 17.5 karelerindeki yazılar basılı ölçekte okunuyor (önce 17.4'te ancak 300 dpi'de).

## 10. Görüldü, dokunulmadı

- Uç etiketi numaraları yazdırma karesinde ≈ 2,3 pt (13 px) kalıyor; kare başlık şeridi ve kare içi lejant şeridi de ≈ 2,5 pt (anlamları
  karenin altında 8,1 pt). Madde 3'ün kapsamı parça etiketiyle sınırlı tutuldu.
- Alt adımı olmayan adımların teslim karesi, sayfa 1182 × 624'te yüklenip 1200 × 720'ye büyütülerek çekiliyor (kadraj küçük alana göre,
  kare büyük alanda). F10d uç etiketi ölçümü de bu kareleri DevTools'ta doğrudan 1200 × 720 açarak ölçüyor (P108f-kontrol N4'ün F10d
  tarafı): F10d'nin alt adımsız karelerdeki uç etiketi ölçümü teslim edilen kare değil. Bu pakette düzeltilmedi.
- 17.5'te dokuz saplama uzak kamerada küçük; okunurluk için 17.5'e odaklı ikinci bir kare ya da kamera değişikliği düşünülebilir (rehber kararı).
- `F9c-uret.py`'nin elle yazılmış metni P10.8f'in beş açığını açık yazıyor; P10.8g commit'inden sonraki kayıt eşitlemesinde güncellenmeli.

## 11. Kapanış tarifi (commit ajanı için)

Depo kökünden, `export PYTHONIOENCODING=utf-8`; Python `py -3 -B -X utf8 …`.

**Elle düzenlenen kaynaklar:** `tasarim/freecad/rehber/rehber_metin.py` (`_SAPLAMA`, `PARCA_ETIKET` K1.1 / K1.5); `rehber/app.js`
(ETK 47 px / 58, iki yerleşim ve seçim, `RehberTest.etiket` alanları); `rehber/yazdir.html` (`semaOnMetin`); `planlama/d158/P108f-etiket-olc.py`
(teslim karesi çekimi ve karşılaştırması); `planlama/d158/P108f-gunluk.md` (TAHMİN → ölçülen 3, üç yer). Yeni: `planlama/d158/P108g-gunluk.md`,
`P108g-onizleme.py`, `P108g-yazi-pt.py`, `P108g-zincir.sh`.

**Üretilen çıktılar:** `rehber/veri/rehber-veri.js`, `.json`; `rehber/goruntu/adim-12, -17-01, -17-04, -17-05.png`; `planlama/rehber/`
(`kontrol.json`, PDF, `goruntu/adim-17-01, -17-05`, gürültü `adim-33-07`); `planlama/d158/sonuc-rapor.html` (2 satır); zincirin yazdığı
F10 JSON'ları; kanıt klasörü `planlama/d158/P108g-olcum/`.

**`git add` listesi**
```
git add planlama/d158/P108g-gunluk.md planlama/d158/P108g-onizleme.py planlama/d158/P108g-yazi-pt.py planlama/d158/P108g-zincir.sh \
  planlama/d158/P108g-olcum planlama/d158/P108f-etiket-olc.py planlama/d158/P108f-gunluk.md planlama/d158/sonuc-rapor.html \
  planlama/d158/F10a-dogrula.json planlama/d158/F10d-dogrula.json planlama/d158/F10e-dogrula.json planlama/d158/F10f-dogrula.json \
  planlama/rehber rehber/app.js rehber/yazdir.html rehber/veri rehber/goruntu tasarim/freecad/rehber/rehber_metin.py
```
**Dışarıda kalanlar:** 21 eski kir (P108f § 10 listesi; md5 `P108f-olcum/kir-bas.md5`), `FREECAD-KILIT.txt`.

**Commit'ten önce / sonra:** commit'ten hemen önce `F9c-dogrula.py --tarayicisiz` 0 olmalı; sonra 3 beklenir (yapısal, § 5, muaf değil).

**Commit mesajı önerisi**
```
Lale P10.8g: ufak beş: 17.1 / 17.5 saplama numaraları, basılı 17.11 şema notu, yazdırma karesinde parça etiketi 47 px (PDF'te 8,1–8,4 pt, önce 2,4–2,5), P108f-etiket-olc teslim edilen kareyi ölçüyor (B5a); F9c yapısal 3 hata ölçüldü, çözüm önerisi günlükte (açık)
```

## 12. Durum

| Madde | Durum | Önce → sonra (ölçülen) |
| --- | --- | --- |
| 1 17.1 / 17.5 numara | kapandı | 0 / 9 ve 0 / 9 → 9 / 9 ve 9 / 9 (iki kipte, teslim karesinde) |
| 2 basılı 17.11 notu | kapandı | PDF s. 26'da yok → var |
| 3 PDF etiket yazısı | kapandı (parça etiketi; uç numaraları kapsam dışı) | 2,42 / 2,51 pt → 8,14 / 8,43 pt (em, ölçüt 8,0) |
| 4 F9c yapısal 3 | **kapanmadı** (tanım değişikliği gerekir; öneri S1) | kayıt TAHMİN → ölçülen 3; çalışma ağacında yenilemeyle 3 → 0, commit'ten sonra 3 (TAHMİN) |
| 5 etiket-olc teslim karesi | kapandı | B5a ölçülen kare ≠ teslim (343.395 / 225.649 px) → 8 / 8 çekimde fark 0 |

**Doğrulanmayanlar:** koyu temada kareler açılmadı; basılı kâğıtta (gerçek yazıcı) bakılmadı, PDF 110 dpi görüntüsüyle bakıldı; 17.5'in
kalabalığının kullanıcı için yeterliliği insan gözüyle değerlendirilmedi.

## 13. Kapanış (C)

C ajanı, 22.11 (saat okundu: 04:42). Komutlar depo kökünden, `PYTHONIOENCODING=utf-8`, `py -3 -B -X utf8`.

**Adım 1, paket commit'i `8d6a7c7`** ("Lale P10.8g: ufak beş: …"; 153 dosya).
- Ön kontrol: `git fetch` sonrası yerel = uzak = `94cd024`; `F9c-dogrula.py --tarayicisiz` GEÇER (hata 0); `md5sum -c
  P108f-olcum/kir-bas.md5` 21 / 21 OK; `FREECAD-KILIT.txt` `.git/info/exclude`'da.
- Açık yollarla `git add`: § 11 listesi + `P108g-kontrol.md` + `P108g-olcum/` tamamı (127 dosya; B'nin önerisi, emsal `P108f-olcum/`).
  Sahnede 153 = 26 + 127; sahnelenmeyen yalnız 21 eski kir (14 M + 7 ??).
- Gizlilik taraması (`git diff --cached`, eklenen ≈ 19.700 satır): e-posta, telefon (+90 / 05xx), anahtar / belirteç kalıpları,
  parola / şifre / token sözcükleri, yerel kullanıcı yolu (Windows ve Git Bash biçimi, kullanıcı adı, eşitleme ve uygulama verisi
  klasörü), IBAN, 11 haneli sayı, resmî metin ve kimlik sözcükleri. Bulunan: kalıp sözcükleri yalnız `P108g-kontrol.md` § 10'da (B'nin
  tarama listesi, veri değil); 11 hane = etiket ölçüm JSON'larında koordinat ondalığı; "masaustu" = görünüm adı ("masaustu 50/50");
  "kimlik" = kablo kimliği. Gerçek ya da sınırda bulgu yok.

**Adım 2, kayıt eşitlemesi** (bu bölümle aynı commit).
- `planlama/dongu-158.md`: § 5'e P10.8g satırı (P10.8f satırı yazılmamıştı, geriye dönük yazılmadı); P10.8 hücresinin rehber
  listesinde P10.8f'in dört açığı "kapandı: P10.8g `8d6a7c7`", yapısal 3 hata "açık, karar: K68", P10.8g'nin açıkları adlarıyla.
- `planlama/d158/karar-kuyrugu.md`: **K68** (sayfanın yapısal 3 hatası; seçenekler § 5, öneri S1, Ahmet'in onayı) özet tablosu ve
  gövdesiyle, açık 27 → 28, toplam 67 → 68; giriş notuna P10.8g satırı; "P10.8f kapanışından açık iş" maddelerine kapanış / K68
  işaretleri; yeni bölüm "P10.8g kapanışından açık iş" (17.5 basılı karesinde eşleme, etiket kutusunun saplamayı örtmesi ve kusur
  sayımı, uç numaraları / şeritler ≈ 2,3–2,5 pt, `P108g-yazi-pt.py` ayar okuyor ve zincirde değil, F10d alt adımsız karede başka çekim,
  360 px bilgi notu, kanca notu, B'nin "bakılmadı" listesi).
- `planlama/d158/F9c-uret.py`: kaynak sabitleri `P108G`, `P108GK`; `GRUP["K68"]` C (TASLAK, orkestratör onaylar; yoksa `KeyError`);
  P10.8 satırına P10.8g; F10 tablosunda rehber "Bitti" / "Açık iş" P10.8g'ye göre, depo satırının karar sütununa K68; aciliyet notu ve
  yeni kayıt notu; başlıkta "P10.8g ve kayıt eşitlemesi, 22.11.2026". `F9c-dogrula.py`'ye dokunulmadı, muafiyet yok.
- Sayfa yeniden üretildi: `F9c-uret.py` çıkış 0, "toplam 68, açık 28", P10.8 commit hücresi `… 94cd024 8d6a7c7`, 157.709 bayt;
  `--tarayicisiz` **GEÇER (hata 0)**; `--goruntu` **GEÇER (hata 0)**, 1400 ve 360 px konsol hatası 0, taşan öğe 0.
- Bu commit'ten sonra F9c'nin yapısal 3 hatası beklenir (K68). Push ve commit sonrası ölçüm bu günlüğe yazılmadı (izlenen dosyada
  değişiklik bırakılmadı), orkestratöre raporda.
