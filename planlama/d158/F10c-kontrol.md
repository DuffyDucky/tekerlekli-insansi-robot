# F10c kontrolü (P10.3: rehber sıra düzeltmeleri + kalıcı sıra denetimi): bağımsız kontrol ajanı B, 11.11.2026

Kontrol edilenler: `F10c-brief.md`, `F10c-gunluk.md` (iddia), `git diff HEAD` (`tasarim/freecad/rehber/rehber_{metin,veri,uret,denetim}.py`,
yeni `rehber_sira.py`, `rehber/app.js`, `rehber/veri/`, `planlama/rehber/kontrol.json`, PDF), `F10c-goruntu-*.png`, A'nın scratchpad
betikleri (`scratchpad/f10c/`, `scratchpad/ajan-sira/`). Esas: çalışma ağacı, dal `lale-duzeltme`, HEAD `ada0b87`.

Kendi ölçümlerim scratchpad'de (`scratchpad/f10c-b/`). A'nın ölçü fonksiyonlarını kullanmadan yazdım: GLB okuyucu (`yukle.py`),
kesit haritası (`kesit.py`), hacimsel süpürme (`supur.py`: hareketli ve engel yüzeyinden 0,15 mm içeri kaydırılmış noktalar karşı
katının içinde mi, iki yönlü parite; temas eden ya da ortak yüzlü parçalar çarpışma sayılmaz), ışınla L alyan erişimi (`e4_b.py`).
`rehber_sira.py`'yi yalnız A'nın sonuçlarını yeniden üretmek için, scratchpad kopyasıyla koştum (eski veri ve el 12 / 15 / 20).

Yazdığım tek depo dosyası bu dosya. Commit, push, silme, checkout, reset, stash yok. FreeCAD açılmadı (kilit baştan sona "boş");
üretici koşulmadı. Arka planda iş kalmadı.

## Karar: **DÜZELTME GEREKLİ**

Engelleyen 1 (E3), engellemeyen 8 bulgu.

- **E3 (adım 30): A'nın "geometrik olarak kilitli" hükmü tutmuyor.** Kafa yalnız eğme çatalına karşı +Y'de (yukarıdan inerek)
  ortak hacimsiz giriyor. Tam engel kümesiyle de giriyor; tek şart parça sırası: horn E2'de servoya vidasız, 625ZZ tek parça olarak
  sol yanakta, pim + pul ve horn merkez vidası kafa indikten sonra yanak deliklerinden. Bu, tasarımın kendi montaj tarifi
  (`tasarim/freecad/kafa/kafa_rapor.py:199-200`). Brief'in kabul ölçütü ("kafa en az bir yönden serbest") yalnız sıra
  değişikliğiyle karşılanabilir; geometri kararı gerekmiyor. Ayrı hüküm aşağıda.
- Öbür işler büyük ölçüde doğru. E4 C5 sırası tabla cıvatalarını gerçekten açıyor (bağımsız ışın ölçümü). Eski veriyle "ulaşılamaz 18"
  aynen çıkıyor. Kalıcı denetim eski sırayı kapalı buluyor. 1192 ↔ 1192, taşınan 0, `robot.glb` aynı. `app.js` değişikliği en küçük,
  sıralı takma yeni sırayı izliyor. ASCII istisnaları gerçek Türkçe kelimeler.

## E3 hükmü: **şu yolla giriyor (kanıt)**

### Geometri (GLB köşe koordinatları, mm; tilt ekseni x yönünde, y 1478,88, z 25)
| Yüz | x |
|---|---|
| Sol yanak dış / iç yüzü | −35,2 / −24,2 (yuvada 625ZZ dış bilezik, r 8; dış yüzde delik r 6,5) |
| Çatal sol kolu dış yüzü | −23,2 (yanağa 1,0 mm; `kafa_rapor.py:146` "yanak ile çatal arası 1 mm") |
| Çatal dayaması (iç bilezik oturağı, r ≤ 4,1) | −24,2: yanak iç yüzüyle **aynı düzlemde**, taşmıyor |
| Servo çıkış mili ucu / horn dış yüzü | 30,2 / 30,2 |
| Sağ yanak iç / dış yüzü | 30,2 / 35,2 (merkezde delik r 4,5) |
| Horn merkez vidası başı | 30,2…33,2, r 2,75 (sağ yanak deliğinin içinde) |
| Pim M5×12 başı + pul | −35,2…−29,2, r ≤ 5 (sol yanak deliğinin içinde) |

Yanakların arası (54,4 mm) çatal + servo + horn yığınına tam eşit: iki yanda sıfır boşluklu, temas eden yüzler. Kafanın çatal x
aralığına (−24,2…13,9) giren her parçası tablanın üstünde (y ≥ 1505,9); çatal en üstte 1493,8. Çatalın ±30'a açılan tek yeri göbek,
y ≤ 1447,9; yanakların altı 1463. Yani yukarıdan inişte yanaklar çatalın yanından geçer; kilit yalnız eksenel geçmelerde.

### Süpürme (hacimsel, 0,15 mm içeri kaydırma, 1 mm adım; `scratchpad/f10c-b/e3_p1.log`)
| Varyant | Hareketli | Engel | +Y (kafa yukarı = iniş yolu) | Çarpan |
|---|---|---|---|---|
| V0 bugünkü sıra | kafa (horn + vidası + dış bilezik) | E2'ye kadar her şey | 0 mm | horn ve horn vidası ↔ servo mili (horn milin kanalında, eksenel geçme) |
| V8 (A'nınkiyle aynı küme) | bütün kafa | yalnız eğme çatalı | **serbest** (kutular ayrılana kadar ortak hacim 0); dinlenmede ortak hacim 0 | – |
| **P1** | kafa − horn − horn vidası + iç bilezik (625ZZ tek parça) | E2'ye kadar her şey − pim − pul − iç bilezik + horn (servoda) | **serbest** | – |
| P1b | P1 gibi | P1 + horn vidası servoda | 1 mm | kafa iskeleti ↔ horn vidası başı |
| P2 | kafa (horn kafada) + iç bilezik | pim / pul yok | 0 mm | horn ↔ servo mili |

V8'de A'nın 28,2 mm'si benim ölçümümde yok: kafa +Y'de çatala hiç girmiyor. Sebep büyük olasılıkla A'nın süpürmesinin (0,05 mm tol,
ışın) x = −24,2'deki ortak yüzü çarpışma sayması. A'nın V8 / V9 sonucunun scratchpad'de dosyası da yok: `e3_olc3.py`'nin JSON'u yalnız
betik sonunda yazılıyor ve koşu V6'da kesilmiş (`F10c-gunluk.md:31`); 28,2 mm yalnız konsol çıktısı. A'nın V9'u (1,8 mm, horn
vidası) benim P1b'mle (1 mm) tutarlı. Eksik deneme: horn servoda ama **merkez vidası sonra**.

Kafa indikten sonra aletler (ışın, E3 sonunda takılı her şey engel): pim için yanak dışından −x yönünde 130 mm serbest (alyan 4 uzun kol
110 + 20); horn vidası için +x yönünde 80 mm serbest (PH1). Sol delik r 6,5 pulu (r 5) ve pim başını (r 4,25), sağ delik r 4,5 horn
vidası başını (r 2,75) geçiriyor.

### Tasarımın montaj niyeti
`tasarim/freecad/kafa/kafa_rapor.py:199-200` (SIRA): "tilt servosunu … U plakaya … (horn servo ortasında)" → "625ZZ'yi kafa iskeletinin
sol yanağına pres et; iskeleti indir, sağ yanağı horn'a 4× M3×8, sol pimi M5×12 + pul ile sık". Rehber bunun tersini yapıyor:
`rehber_metin.py:311` E2'de "Karşı yanağa 625ZZ ve M5 pimi tak", `:325-326` E3a'da horn kafada ve "Hornun önce servoya mı yanağa mı
takılacağı kaynakta yok". Kaynak var; A ve önceki rehber turu bulmamış. 625ZZ gerçekte tek parçadır; modeldeki iç / dış bilezik
ayrımı yalnız çizim içindir.

### Kalan risk (ölçülmedi)
- İki yanda sıfır boşluklu kayma: 625ZZ iç bileziği çatal dayamasına, sağ yanak horn yüzüne değerek iner. Baskı toleransında
  yanakların hafif açılması gerekebilir. Modelde ortak hacim 0, ama gerçek parçada "zorlamasız iner" ölçülmedi.
- FreeCAD katılarıyla `common()` ölçümü yapılmadı (FreeCAD açmadım). Sonuç mesh çözünürlüğüne bağlı değil: ayrım yüz koordinatlarından
  (tablo) doğrudan okunuyor; süpürme yalnız teyit.
- Horn spline'ının servo ortasında takılması (tilt sıfırı) ve vidanın yanak deliğinden PH1 ile sıkılması: tork / görüş ölçülmedi.

## Ölçüt tablosu: B ↔ A
| Ölçüt | B | A | Not |
|---|---|---|---|
| Eski veriyle (HEAD `rehber-veri.json`) ulaşılamaz | 18 (tabla 4, tırnak 4, kamera 4, dizi 3, F3 taşıyıcı 1, G4 kaset 2); sınama 5 / 5 | 18, 5 / 5 | `rs/once_head.log` |
| Yeni veriyle ulaşılamaz (el 20) | 0 (adım 31, 35, 41, 42; tam koşu A'nın `kontrol.json`'unda 0) | 0 | |
| "18 → 0"ın kaynağı | Gerçek sıra düzeltmesi 4 (tabla). 11'i (tırnak, kamera, dizi) eski metnin zaten söylediği adım içi sıranın veriye girmesi; 3'ü F3 sırası ve G4 pozu verisi | A da günlükte ayırıyor (§7) | B-4 |
| Bilinen kapalı sınama, el 20 / 15 / 12 | geçti / **kaldı** / **kaldı** (eski sıra da L ulaşılır görünüyor) | 20'de geçti | B-3 |
| E4 tabla cıvataları C5, el 20 / 15 / 12 | 4 L / 4 L / 4 L | aynı | |
| Tabla cıvatası düz alet yolu (bağımsız ışın) | 63,4 mm (çatı: arka kabuk) | 63,5 | |
| L uzun kol 90 mm serbest yön (24 yönde), C5 → eski | ön cıvatalar 9 / 10 yön, kol ucu kafanın dışında (z 88–100); arka cıvatalar 5 / 4 yön, kol ucu ön açıklıkta (z 37–40). Yüz kabuğu takılıyken ön cıvatalarda yalnız içe dönük 3–4 yön | açık / kapalı | C5'in faydası bağımsız ölçümde de var |
| Tırnak, kamera, dizi vidaları (masada) | DUZ (el 12, 15, 20) | DUZ | Masa grubunda yalnız grubun kendi parçaları engel (B-5) |
| G4 kaset cıvatası | POZA_BAGLI (yalnız ışın; pozda el katmanı yok) | aynı | metin S1 −45 / S2 90 ile tutarlı |
| F3 sırası | veri `sira_grup` = metin 1–5 (bant → taşıyıcı → ekran + VESA → çerçeve) | aynı | |
| E3 kafa serbest | **P1 sırasıyla +Y serbest** | hiçbir sırayla değil | B-1 |
| Parça kaydı | 1192 ↔ 1192, alan farkı 0, taşınan 0; her parça tek satırda | aynı | |
| Değişen adımlar | 9, 15, 17, 31, 35, 36, 41, 42 (+ `uretim`) | aynı | |
| `robot.glb`, `robot-glb.js` | bayt aynı (`git diff --quiet` 0) | aynı | |
| Perdelenme toplamı | eski veriyle 290 | 290 | 50 satır var |
| PDF | 54 → 55 sayfa; en küçük yazı 8,1 pt; görüntüsüz 5 sayfa = 5 devam sayfası (19, 34, 36, 40, 55) | aynı | sayfa 33, 41'e baktım |
| Konsol (başsız Chrome; 31, 35, 9, `31&patlat=1&tak=7`) | yalnız WebGL "GPU stall" performans iletisi, JS hatası 0 | 0 | |
| Sıralı takma | `tak 7/21` → seçili satır `b:1` (tabla cıvatası M3×10), sıra `sira` ile aynı | aynı | |
| `F9b-dogrula`, `carpisma_kos kontrol`, regresyon, tam F10a-dogrula | **ölçülmedi** (üretici ve tarayıcı zinciri yeniden koşulmadı) | 0, 0, 10 / 10, F10a kopyayla geçti | |

## Bulgular

### B-1 (engelleyen). E3 "kilitli" yanlış; sıra değişikliğiyle açılıyor
- Kanıt ve sayılar yukarıda (E3 hükmü).
- Yanlış yer: `F10c-gunluk.md:87-93` (V8 satırı ve "geometrik olarak kilitli … sırasını değiştirmek bunu açmaz"), `:96-103`
  (seçenekler hep geometri), `:282`.
- Yeniden üretme: `scratchpad/f10c-b/e3_p1.py` (çıktı `e3_p1.log`). V8 için `supur.Supur(kafa, ["p0718"])`, yön (0, 1, 0).
- Düzeltme (A için, brief 2. madde kapsamında): parça taşı:
  - `p0830` tilt hornu: E3a → E2 (28), servoya, merkez vidası olmadan;
  - `p0831` horn merkez vidası: E3a → E3 (30), kafa indikten sonra sağ yanak deliğinden PH1;
  - `p0733` 625ZZ iç bilezik: E2 → E3a (29), dış bilezikle birlikte, tek parça olarak sol yanağa pres;
  - `p0734` pul + `p0735` pim M5×12: E2 → E3 (30), sol yanak deliğinden alyan 4.
- Metin: E2 (`rehber_metin.py:309-315`), E3a (`:325-326`), E3 (`:344-349`) yukarıdaki sıraya ve `kafa_rapor.py:199-200`'e göre.
- Sıfır boşluklu iniş için E3'e bir kontrol satırı; "baskı toleransında doğrulanmadı" diye.
- Sonra kafanın +Y'den serbest girdiğini ve E2 / E3 bağlantılarının sıra denetiminde ulaşılır kaldığını ölç.

### B-2 (engellemeyen). Günlükte el payı diye yazılan sayıların ikisi el payı değil
- `F10c-gunluk.md:55` "L tutacağına el payı 15 mm". `rehber_sira.py:591` `ulas(..., s0=15.0)`: 15, L uzun kolu boyunca el bölgesine
  girilen ilk noktanın uzaklığı. Örnekleme 15'ten başladığı için dört cıvatada da tam 15 çıkıyor. El payı (eşik) 20 mm.
- `rehber_metin.py:631` ve `:636` (H0a) "el payı 25,5–36 mm": bu da `acik_agiz_el_mm`, anahtar şeridi boyunca el bölgesine olan uzaklık,
  açıklık değil. Öneri: "anahtar el bölgesine 25,5–36 mm'de ulaşıyor".
- Ölçü doğru, adı yanlış. Metinde okura yanlış güven veriyor.

### B-3 (engellemeyen). Sıra denetimi yalnız EL = 20'de ayırt ediyor; E4 metni duyarlılığı tam yazmıyor
- El 15 ve 12'de "bilinen kapalı" sınamaların ikisi de kalıyor: E3 + E4 ve eski E4 sırası L ulaşılır görünüyor (`rs/yeni_el15.log`,
  `yeni_el12.log`). Yani C5'in eski sıraya üstünlüğü 20 mm el varsayımına bağlı (orkestratörün 10.11 notunda da "EL 15'te açık görünüyor").
- `rehber_metin.py:376` "4/4 ulaşılır, el payı 12, 15 ve 20 mm'de. Eski sırada … 20 mm el payında 4/4 kapalı": doğru ama yarım. Önerilen ek:
  "15 mm ve altında eski sıra da açık görünüyor; fark 20 mm el varsayımına dayanıyor".
- Benim bağımsız ışın ölçümüm farkı el modelinden bağımsız da gösteriyor: yüz kabuğu takılıyken ön iki cıvatanın L kolu yalnız kafanın
  içine dönüyor. Arka iki cıvatada iki sırada da kol ucu ön açıklıkta (z ≤ 40).

### B-4 (engellemeyen). "Ulaşılamaz 18 → 0" başlığı gerçek erişim düzeltmesini olduğundan büyük gösteriyor
- 18'in 11'i eski veride adım içi sıra olmadığı için E4'ün bütün parçalarını engel sayan bir model yapaylığı. Eski metin de kamerayı ve
  tırnakları kabuk kapanmadan yaptırıyordu.
- 3'ü (F3 1, G4 2) metinde zaten yazılı sıra / poz verisinin eklenmesiyle açıldı.
- Gerçek sıra düzeltmesi 4 tabla cıvatası; brief'teki "önce 4" doğru sayıydı. A §7'de bunu açıklıyor; rapor ve kuyruk metninde "18 → 0"
  yerine "4 → 0 (+ 14 model / veri eksiği)" yazılmalı.

### B-5 (engellemeyen). "tezgah" işaretli grup denetimi gevşetebilir
- `rehber_sira.py:402-405`: tezgâh grubunun bağlantıları yalnız kendi grubunun parçalarıyla ölçülüyor. E4'te doğru: masada kabuk açık.
- Ama işaret bir adıma eklenince o grubun bütün robot bağlamı ölçümden düşüyor. Grubun robota bağlanma yolu da ölçülmüyor.
- Öneri: `tezgah=True` gruplar için "grup robota hangi yönden giriyor" süpürmesi, ya da en az işaretin yalnız gözden geçirilmiş
  adımlarda kullanılması (sınama listesine kural).

### B-6 (engellemeyen). B6 notunda "ölçülmedi" yanlış
- `rehber_metin.py:175` "Çözüm seçilmedi, ölçülmedi". F10b'de seçenekler ölçüldü (çentik 1,5 mm: boşluk 1,075 mm; `karar-kuyrugu.md`
  K53). Çözüm uydurulmamış, bu iyi.
- Öneri: "Çözüm seçilmedi (K53 karar bekliyor)". Taşma sayısı doğru: `F10b-olcum.json` kat ön kenarı 24,25, burç köşesi 24,675 → 0,425 mm.

### B-7 (engellemeyen). F4 metninde "0 mm" okura ters okunuyor
- `rehber_metin.py:565` "kapak açıklığından travers arkasına 0 mm, yarığın iç tarafına 6 mm". 10.11 notunda bu sayılar "el bölgesine
  uzaklık" (0 = el doğrudan ulaşıyor).
- Okur "0 mm boşluk" diye anlar. Öneri: "el bölgesine uzaklık 0 mm (doğrudan)". A da bunu yeniden ölçmedi (günlük §12-3); ben de
  ölçmedim.

### B-8 (engellemeyen). Panel tablosu sırayı göstermiyor
- `app.js:321-324` sıralı takmayı `st.sira` ile doğru diziyor (tak 7 = tabla cıvatası).
- Ama panel "Parçalar" ve "Bağlantı elemanları" tablolarını ayrı basıyor. Okur listede yüz kabuğunu tabla cıvatasından önce görüyor,
  dizi vidası (b:0) bağlantı tablosunun başında.
- Grup başlığı yok. F10d'ye not: tablo satırlarını `sira_grup`'a göre grup başlıklarıyla bas.

### B-9 (engellemeyen). `F10a-dogrula.py` depoda çıkış 1 veriyor
- Neden: `F10a-dogrula.py:153` "önce" sayfasını `git show HEAD:rehber/...`'den alıyor.
- `:159-163` bu sayfada importmap'i yamalamayı bekliyor. F10a commit'inden (`749627b`) beri HEAD'deki `index.html`'de importmap yok
  (`git show HEAD:rehber/index.html | grep -c importmap` → 0; `749627b~1`'de 1). `re.sub` bir şey değiştirmiyor, assert düşüyor.
- En küçük düzeltme (uygulamadım):
  - betiğin başına `ONCE = os.environ.get("F10A_ONCE", "749627b~1")`;
  - `:153`'te `"HEAD:rehber/"` yerine `ONCE + ":rehber/"`;
  - `:611`'deki `veri_degismedi` ölçütü kabulden çıkarılıp bilgi alanına alınmalı. Veriyi yeniden üreten her pakette tanım gereği
    false.

## Diğer kontroller
- **Rehber metinleri:**
  - 9 / 17 (B3 / K1): kablo içeriği değişmemiş. "motor uçları B2b'de plaka üstüne alındı" B2b metniyle tutarlı. Serbest uç toplama
    "kaynakta yok, doğrulanmadı" diye işaretli. 69 mm / 40–150 mm A'nın ışın ölçümü; ben yeniden ölçmedim.
  - 31: C5 metni ölçümle tutarlı; B-3'teki eksik dışında.
    - "Yüz kabuğu takılıyken arka kabuklar kapanırsa" cümlesi anlaşılır ama dolambaçlı (`rehber_metin.py:355-356`). Öneri: "Yüz
      kabuğu önce takılırsa tabla cıvatalarına alet sığar ama el kafanın dışından ulaşamaz".
    - "Kabukları kafanın arkasına getir, önden bağla" da belirsiz: kabloyu önden takmak kastediliyor.
  - 36 (F4): G2 / G4 / H1 metinleriyle tutarlı.
  - H0a: bilek somunlarının cep oranı 0,04, dirseklerinki 0,75. "Bilek somunu cepte" eski iddiası gerçekten tutmuyor; yeni metin doğru
    (B-2'deki adlandırma dışında).
  - 30 (E3): değişmemiş; B-1'e göre değişmeli.
- **ASCII istisna listesi** (`rehber_denetim.py:98-99`, 31 kelime): hepsi doğru Türkçe yazımı ASCII olan kelimeler (burcuna, kafadayken,
  demetleyip, klemenslere …) ve hepsi yeni metinde geçiyor. Susturma yok.
- **numpy yokken** (kodu okudum, ortamı bozmadım):
  - `rehber_sira.py:42-45` içe aktarmayı yakalıyor; modül düzeyinde başka numpy kullanımı yok.
  - `denetle` (`:812-814`) iki alanı `durum: "atlandı"`, `gecti: True` döndürüyor; `ozet_yaz` erken çıkıyor.
  - `rehber_uret.py:435-441` çökmeyi ayrıca yakalıyor. Üretim kırılmaz.
  - Not: bu durumda denetim **geçti** sayılıyor; çıkış kodu görmez, yalnız konsol satırı ve `kontrol.json` söyler.
- **Görüntüler** (Read ile):
  - `F10c-goruntu-sonra-31`: panelde yeni metin var.
  - `F10c-goruntu-31-tak-7`: tabla cıvataları seçili, arka kabuk yerinde saydam, yüz yarıları patlak.
  - PDF sayfa 33 (adım 31) ve 41 (adım 36): metin tam, görüntü dolu.
  - `kontrol.json` yazdırma kareleri: eksik 0, boş 0, en düşük çizim oranı 0,0595.
  - `planlama/rehber/goruntu/` ve `rehber/goruntu/` karelerinde düz (std < 8) kare yok.
- **Yan etkiler:**
  - A'nın değişiklikleri izinli alanda: `tasarim/freecad/rehber/` (4 değişik + `rehber_sira.py` izlenmiyor), `rehber/app.js`,
    `rehber/veri/`, `planlama/rehber/`, `planlama/d158/F10c-*` (19 görüntü + günlük).
  - `planlama/dongu-158.md` (03:38, orkestratör günlük satırı), `tasarim/freecad/kabuk/gorsel/*.png` (09.11),
    `montaj/yerlesim-kontrol.json` (03.11) A'nın değil.
  - Not: `rehber_sira.py` izlenmeyen dosya; commit listesine girmeli (A'nın §11'inde var).
- **Yerel yol / takma ad:**
  - `F10c-gunluk.md`, `rehber_sira.py`, `rehber_metin.py`, `app.js`, `kontrol.json`, `rehber-veri.json` ve diff'in eklenen
    satırlarında 0.
  - `rehber_veri.py` ve `rehber_uret.py`'deki eşleşmeler HEAD'den kalma (eklenen satırda yok).

## E3 için karar kuyruğuna önerilen metin
> **K5x · E3 kafa montaj sırası (tilt hornu, 625ZZ, M5 pim)**
> - **Soru:** Rehberde kafa (E3) tilt hornuna takılamıyor: horn kafayla gelirse servo milinin kanalına eksenel girmesi gerekiyor, ama
>   yanaklar çatalı iki yandan 0 / 1 mm boşlukla sarıyor; pim ve iç bilezik E2'de takılıysa sol yanak da inemiyor. Sıra mı değişsin,
>   geometri mi?
> - **Ölçüm** (F10c-kontrol, hacimsel süpürme): bugünkü sıra +Y 0 mm. Horn servoda (vidasız), 625ZZ tek parça sol yanakta, pim + pul
>   ve horn vidası sonra: +Y **serbest**, ortak hacim 0. Horn vidası servodaysa 1 mm. Pim için yanak dışından 130 mm, horn vidası için
>   80 mm alet yolu serbest.
> - **Seçenekler:**
>   a) Yalnız sıra (önerilen): `kafa_rapor.py:199-200`'deki tarif. Horn E2'de servoya (merkez vidası yok) → 625ZZ E3a'da sol yanağa →
>      E3: kafayı yukarıdan indir, horn vidası sağ yanak deliğinden, 4 yanak-horn cıvatası, pim + pul sol yanak deliğinden. Model
>      değişmez; 5 parça adım değiştirir.
>   b) a + yanak iç yüzlerine 0,2–0,3 mm pay (sıfır boşluklu kaymayı kaldırır): geometri değişikliği, çakışma taraması kaynağı.
>   c) Geometri (A'nın a–c'si: açık kanal, iki parçalı çatal, bölünmüş iskelet): gerekmiyor.
> - **Öneri:** a. b'yi ilk baskı kuponunda (yanaklar arası 54,4 mm, yığın 54,4 mm) dene. Karar Ahmet'te.

## Ölçülmeyenler
- FreeCAD katılarıyla ortak hacim (E3): yapılmadı; mesh + yüz koordinatı.
- **C5'in kabuk yolları:** ReSpeaker'lı sağ arka kabuk, ses kartı + PAM'lı sol arka kabuk ve kamera + QLED'li yüz grubu (arka kabuk
  ve tabla cıvataları takılıyken) robota hangi yönden giriyor? Süpürmesini başlattım (`scratchpad/f10c-b/e4_yol.py`). Sistem belleği
  azalınca ortam koşuyu durdurdu; sonuç yok, yeniden başlatmadım. A da ölçmemiş. Eski sırada da ölçülmemişti. Bilinen tek değişiklik
  yüz kabuğunun arka kabuktan sonra gelmesi: ön / arka dikiş (x ±129–136, z 35–42) z yönünde bindirme. Bunun yüzün −z ile girişini
  engellemesi beklenmez, ama ölçülmedi. Kabloların "yüz kabuğu önde tutulurken" takılması (madde 4) da ölçülmedi (kablo boyu
  modelde yok).
- K1 69 / 40–150 mm, F4 0 / 6 mm, H0a açık ağız yönü: A'nın ve orkestratörün sayıları, yeniden ölçmedim.
- `F9b-dogrula`, `carpisma_kos kontrol`, regresyon, F10a-dogrula kopyası, 360 px telefon görünümü: koşulmadı.
- Gerçek baskı toleransında E3 kayması, horn vidasının yanak deliğinden sıkılması: ölçülemez (fiziksel parça yok).
