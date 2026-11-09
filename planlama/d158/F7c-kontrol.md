# F7c kontrolü (P7.3, rehberde kalanlar): bağımsız kontrol ajanı B, 09.11.2026

**Kapsam.** A'nın F7c paketi (`planlama/d158/F7c-gunluk.md`), brief `planlama/d158/F7c-brief.md`. A'nın sonuçlarına güvenilmedi; her madde kaynaktan ve B'nin kendi koşularıyla denetlendi.

**B'nin çalışma koşulları.**
- Çalışma klasörü: scratchpad `f7c-b` (aşağıda `SPB`).
- FreeCAD koşulmadı, kilide yazılmadı. Kilit "boş" (6 bayt, A'nın bıraktığı gibi).
- Git'e yazılmadı, hiçbir şey silinmedi. Python `-B` ve `PYTHONDONTWRITEBYTECODE=1` ile koşuldu.
- Depoya yazma yok. Kanıt: başta ve sonda bütün dosyaların sha1'i (`.git` hariç 1.429 dosya) ve `git status --porcelain` aynı. Bu dosya tek istisna.

## Madde tablosu

| # | Madde | Etiket |
|---|---|---|
| 1 | Güvenlik metinleri (aşama 1 / 2, mantar ölçümü, 50 adım taraması) | **KOŞULLU**: sıra kaynakla tutarlı; köprüleme ya da akülü bağlantı talimatı 0. Ancak aşama 1'de sigorta durumu eksik ve mantar ölçüm noktası tanımsız (O-1, O-2) |
| 2 | Denetim: B'nin 20 enjeksiyonu + 4 yanlış pozitif denemesi | **GEÇER** (sınırları belgeli): hedeflenen denetim 12 / 20 yakaladı; kaçanların 6'sı kalıp dışı anlatım, 2'si kalıp boşluğu (D-1). "akü … takılı" kalıbı yanlış pozitif veriyor (D-2) |
| 3 | PDF | **GEÇER**: 52 sayfa, en küçük yazı 8,1 pt (pypdf ve PyMuPDF), eşleme doğru, A'nın bakmadığı 7 sayfa görüldü |
| 4 | Üretim (`--cikti SPB --veri-yok`) | **GEÇER**: 50/50, konsol 0, 1192 ↔ 1192, 360 px 7 / 0; depoya yazma 0 |
| 5 | Demo | **GEÇER**: kopyada üretilen demo bayt bayt aynı; `F9b-dogrula.py` 0; 127 anahtarın hiçbiri değişmedi |
| 6 | D-6 ölçü geri yazımı | **GEÇER**: 22 farklı vida adı model geometrisiyle birebir; 327 parçanın 327'si eksiz kardeşiyle aynı ad ve aynı ölçü |
| 7 | Karar taslakları | **GEÇER**: KT-F7c-1 veri sayfası ve alıntılar doğru; KT-F7c-2 ve KT-F7c-3 atıfları doğru |
| 8 | Bütünlük, diff, ad / yol, liste | **GEÇER**: tarama 0, regresyon 0; brief dışı değişiklik yok; takma ad 0, yerel yol 0 |

## 1. Güvenlik metinleri

### 1a. Kaynak karşılaştırması

B kaynakları kendisi açtı: `planlama/adim3/elektrik.md:230-266` (E2 / E3) ve `:425-462` (E9), `planlama/d158/testler/00-genel.md:30-52`, `T13-rampada-acil-stop.md:110-125`. Rehber metni `rehber/veri/rehber-veri.json`'dan okundu.

| Metin (adım) | Kaynak | Sonuç |
|---|---|---|
| Aşama 1: "Devreye alma komutu Pi'den gelir … röle K1 ve K2 kapanmaz" (F1) | `:255` (röle yalnız mantar serbest + GPIO12 = 1), `:106` (komut Pi'den) | Mantık doğru, ama "kapanmaz" ESP32 yazılımına bağlı (O-1) |
| Aşama 1: "röle K1 açık; F3 takılı olmadığı için yalnız F4 / F5 girişleri" (F1) | `:460-461` (F3 / F4 / F5) | Uyarlama doğru. Göğüs dalı (K11 varsayılanı a) burada sayılmamış (O-1) |
| Aşama 2 dizisi: ön koşul → K2 → 300 ms → PC817 #2 LOW → K1 → 100 ms → K2 bırak → PC817 #2 teyidi (F5) | `:455-457`, adım (1)–(6) | **aynı**. E3 ön koşulundaki "PWM = 0" (`:257`) atlanmış (D-3) |
| D-11: "Mantara basınca K1 düşer (K2 … zaten bırakıldı), bara kesilir (PC817 #2 HIGH)" (F5) | `:437`, `:457` (acil stopta iki pin LOW), `:233` (PC817 #2 LOW = güç var) | doğru; "iki röle de düşüyor" veride 0 |
| "Mantarı bırak: röle kendiliğinden çekmez" (F5) | `:255` | doğru |
| "ESP32 … resetlenmemeli (boot mesajı yok)" (F5) | `:260-264` | doğru |
| "erişim alanında kimse yok, bir kişi yalnız mantarda" (F5) | `00-genel.md:32-34`, `:49-51` | doğru |
| Tekerlekler yerden kesik, şasi takozda (F1, F5) | `T13:118-119` | uyumlu; metinde "doğrulanmadı" işareti var |
| Aşama 2: "Akü XT60 ayrıkken F3 (kafa) sigortasını tak" (F5) | kaynakta sıra yok | **Güvenli**: akü ayrık; H1 kapağı F5 madde 3'e kadar açık, sigorta kutusuna erişim var |

**Sonuç.** Aşama 1 ve aşama 2 sırası `elektrik.md` ile tutarlı. Kaynakta olmayan adımlar metinde "doğrulanmadı" diye işaretli. Açık kalan iki nokta aşağıda (O-1, O-2).

### 1b. Betikli tarama (50 adım)

- Betik: `SPB/tara.py`.
- Taranan: 50 adımın 9 metin alanı (`baslik`, `is_`, `baglanti_md`, `alet`, `erisim`, `tezgah`, `kontrol`, `kablo`, `not_`), cümle cümle.
- Desenler: köprü / jumper / atlama teli / kısa devre / devre dışı / baypas / iptal / yerine tel / birleştir; akü / XT60; enerji / gerilim / "ana anahtar aç" / açıkken / sigorta tak / sigorta takılı / canlı / 12 V ver / çalışırken / dönerken.
- 49 isabet, hepsi elle okundu:
  - **Köprüleme isteyen talimat: 0.**
    - K1 ×2, E3a, E4: "köprülenmez / köprülenmedi".
    - F2 "kelepçe köprüsü" ve F3 "cep üst kenarı köprü": parça adı.
    - K1 "kısa devre yok": ölçüm.
  - **Akü bağlıyken bağlantı: 0.**
    - Bağlantı adımları akü ayrıkken: B3 "Aküyü şimdi BAĞLAMA", K1 "Bağlarken akü ayrık", K2 "Enerjisiz çalış: akü XT60 ayrık", F1 "Bağlarken akü ayrık".
    - Aşama 1 ve 2 "aküyü XT60'tan ayır" diye bitiyor.
  - **Enerjiliyken takma / sökme: 0.**
    - F3 "uçlarını enerjisizken tak".
    - F5 aşama 2'de bağlantı talimatı yok; F3 sigortası akü ayrıkken takılıyor.
    - G / H adımlarında konnektör işi aşama 1'in "aküyü ayır" sonundan sonra geliyor.

### 1c. Bulgular

**O-1 (orta). Aşama 1'de sigortaların durumu eksik; "röle kapanmaz" donanımla değil, yazılımla güvenceli; açıkta gerilimli uç kalabiliyor.**
- **Kanıt:** `tasarim/freecad/rehber/rehber_metin.py:427-433` (F1 aşama 1).
  - Metin şunları söylüyor: "ana sigorta takılı; F3 (kafa) sigortası takılı değil" ve "yalnız F4 / F5 girişleri".
  - Şunları söylemiyor: F1 20 A (röle ve ön şarj kolunun beslemesi, `elektrik.md:440-441`), hat sigortaları A, B, C ve göğüs mini 2 A takılı mı?
  - Ana sigortayı, F4'ü ve F5'i akü ayrıkken takan bir adım da yok. B5a "Sigortaları henüz takma" diyor, sonra hiçbir adım taktırmıyor.
  - Ortak kural 1 bunu istiyor: "ana sigorta ve ilgili dal sigortası takılı olmadan enerji verilmez" (`00-genel.md:38-39`).
- **Röle neden kapanabilir?** Aşama 1'de ESP32 F4 çevre 5 V ile çalışır ve içindeki yazılım bilinmez.
  - K2'nin sürücüsü GPIO2'dir, bu da DevKit'in LED pinidir (`elektrik.md:458`). Hazır bir "blink" ya da deneme yazılımı K2'yi açıp kapatır.
  - F1 20 A takılıysa bara 5,6 Ω üzerinden enerjilenir. Hat sigortaları da takılıysa XL4016 A / B / C ve servolar enerjilenir. Bu adımda S1, pan ve tilt servoları takılı.
  - Pi'nin olmaması bunu engellemez. Metin "röle K1 ve K2 kapanmaz" diye kesin konuşuyor ve bu ifade "doğrulanmadı" işaretinin kapsamına girmiyor.
- **Açıkta gerilimli uç:** göğüs ekranı 12 V dalının ucu K2'de "ekran arkasında bırakılır" (`rehber_metin.py:387-388`) ve ekrana ancak F3'te takılır.
  - K11 varsayılanı (a) dalı ana anahtardan sonraya, rölenin önüne bağlar (`elektrik.md:68`).
  - Göğüs mini 2 A takılıysa, aşama 1'de ana anahtar açıldığında bu boştaki uç 12 V'ta olur.
- **Önem:** 12 V düzeyinde; yuvalar sigortalı ve regülatör akım sınırlı. Kritik değil. Ama brief'in "röle kapanmaz" kabulünü donanımla güvenceye almak tek satırlık bir iş.
- **Düzeltme (A):** aşama 1'in başına şunu yaz: "Akü XT60 ayrık, ana anahtar kapalıyken ana sigorta (30 A), F4 ve F5'i tak. F1 (20 A), F3, hat sigortaları A / B / C ve göğüs 2 A takılı değil: bara ve göğüs dalı enerjisiz (doğrulanmadı)."
  - F5 aşama 2'de "F3 (kafa) sigortasını tak" yerine şunu yaz: "F1, F3 ve A / B / C sigortalarını tak".
  - Göğüs 2 A sigortası F3 adımında, regülatör ölçümünden önce ve akü ayrıkken takılsın; bu satır F3'e eklenir.
  - `ZORUNLU`'ya F1 için "F1 (20 A) … takılı değil" deseni eklenir.

**O-2 (orta). Aşama 1 mantar ölçümünde ölçüm noktası ve GND referansı yazmıyor; uçların sökülme anı yok.**
- **Kanıt:** `rehber_metin.py:431-432`: "Mantar: basınca mantar sonrası F5 hattı 0 V, bırakınca 12 V (multimetre; ölçü uçları enerji yokken takılır)". Bu kaynakta yok; A "doğrulanmadı" diye işaretlemiş.
- **Sorun:** okuyan "mantar sonrası" düğümü en kolay mantarın kendi NC uçlarında bulur.
  - İki NC ucunun yanına takılan klipsli uç kayarsa mantarı köprüler. Bu, rehberin yasakladığı durumun ta kendisi.
  - Siyah uç (GND) için bir nokta verilmemiş.
  - Ölçüm sırasında açıkta duran tek gerilimli düğüm F5 hattı (12 V, 2 A sigortalı). O-1 uygulanmazsa göğüs dalının ucu da açıkta kalır.
- **Düzeltme (A):** ölçüm noktasını adıyla yaz: "kırmızı uç arayüz kartındaki PC817 #1 giriş klemensine, siyah uç WAGO GND yıldız noktasına; mantar uçlarına klips takılmaz".
  - Bitiş sırasını yaz: "ana anahtarı kapat, aküyü ayır, sonra ölçü uçlarını sök".
  - Bunlar kaynakta yok, "doğrulanmadı" işareti kalır.

**D-3 (düşük). Aşama 2'de küçük eksikler.**
- `rehber_metin.py:611-621`: mantara basınca K1 düşer ve servo gücü kesilir, kollar düşer (`elektrik.md:262`, `:508`). Metinde bu uyarı yok.
  - "Erişim alanında kimse yok" kuralı bunu kısmen karşılıyor, ama kolların düşme hattı ayrıca anılmalı.
- E3 ön koşulundaki "PWM = 0" atlanmış (`elektrik.md:257`).
- İki aşamada da "Aküyü XT60'tan tak, ana anahtarı aç" yazıyor. "Ana anahtar kapalıyken tak" açıkça yazmıyor.
- Ortak kural 8 (saat, yüzük, takı çıkarılır; `00-genel.md:52`) iki aşamada da anılmıyor.

**D-5 (düşük, F7b'den kalma, F7c dışı).** F3 iş metni (`rehber_metin.py`, F3 madde 3): "ölçünce enerjiyi kes". Ana anahtar mı kapatılacak, akü mü ayrılacak, belirsiz. Bir sonraki metin turunda "ana anahtarı kapat, aküyü XT60'tan ayır" olsun.

**D-12 sapması (B6a) yerinde.** PC817'li arayüz kartı B6a'da takılıyor: PDF s. 15 parça listesinde "Arayüz kartı (E2/E3)", `robot-bom.csv:126` "PC817 x2". B6a satırı brief'in gerekçesine uyuyor.

## 2. Denetim (`rehber_denetim.py`)

**Yöntem.**
- `rehber_denetim.py`, `rehber_metin.py` ve `rehber-veri.json` `SPB/denetim/`'e kopyalandı. sha1 depodakiyle aynı: `6a1610f22416`, `ccbf2a8d8c09`, `6a813c48f99a`.
- Temiz kopya: çıkış 0; zorunlu eksik 0 / 21, yasak 0, istisna 5, kopya eki 0.
- Enjeksiyonlar bellek içinde yapıldı (`SPB/enjekte_b.py`). Yakalanma yalnız hedeflenen denetimle sayıldı (yasak, zorunlu ya da kopya eki > 0); ASCII kalıntısı ayrıca yazıldı.
- A'nın 14 denemesinden hiçbiri tekrarlanmadı.

| # | Enjeksiyon (B) | Hedeflenen | ASCII |
|---|---|---|---|
| J1 | F1'e "Test sırasında acil stop mantarını devre dışı bırak" (kalıp dışı) | **kaçtı** (denetim geçti) | 0 |
| J2 | K1'e "Acil stop kablosunu klemenste kısa devre et …" (kalıp dışı) | **kaçtı** | 1 (yalnız ASCII) |
| J3 | F5'e "F3 sigortası yoksa sigortanın yerine tel koy" (kalıp dışı) | **kaçtı** | 2 (yalnız ASCII) |
| J4 | K1'e "AKÜ BAĞLIYKEN KABLOLARI BAĞLA" (büyük harf, ı / I) | yakaladı | 1 |
| J5 | K1'e "Mantar uçlarını KÖPRÜLEYİN" (büyük İ) | yakaladı | 0 |
| J6 | G2'ye "Akü bağlı durumdayken S2 servo konnektörünü tak" | yakaladı | 1 |
| J7 | H1'e "XT60 takılıyken servo konnektörlerini sök" ("akü" kelimesi yok) | **kaçtı** (denetim geçti) | 0 |
| J8 | F5'e "Ana anahtar açıkken röle bobin uçlarını değiştir" (fiil listede yok) | **kaçtı** | 1 (yalnız ASCII) |
| J9 | F3'e "Enerji verilmişken mantar konnektörünü çıkar" | yakaladı | 0 |
| J10 | F1'e "Mantar henüz takılı değil, uçlarını köprüle" (aynı cümlede "değil") | **kaçtı**: "değil" istisna saydı (denetim geçti) | 0 |
| J11 | K2'ye "F3 sigortası takılıyken kafa fişini tak" (iyelik eki) | **kaçtı** (denetim geçti) | 0 |
| J12 | K1'e "Gerilim varken klemens vidalarını sık" | **kaçtı** | 1 (yalnız ASCII) |
| J13 | F5 "Mantara basınca K1 düşer" → "röleler düşer" | yakaladı (zorunlu F5) | 0 |
| J14 | F1 aşama 1'den "; BTS EN = 0" silindi | yakaladı (zorunlu F1) | 0 |
| J15 | F1 "röle K1 ve K2 kapanmaz" → "röle K2 kapanmaz" | yakaladı (zorunlu F1) | 0 |
| J16 | B5a "XL4016 C 6 V" → "XL4016 6 V" | yakaladı (zorunlu B5a) | 0 |
| J17 | F5 "Akü XT60 ayrıkken F3" → "Akü bağlıyken F3" | yakaladı (yasak) | 0 |
| J18 | F5 "Akü XT60 ayrıkken F3 … tak" → "Ana anahtar açıkken F3 … tak" | yakaladı (yasak) | 0 |
| J19 | bir "M3x8" parça adı "M3x001" yapıldı | yakaladı (kopya eki) | 0 |
| J20 | F3 "enerjisizken tak" → "enerji varken tak" | yakaladı (yasak) | 1 |

**Sonuç: 12 / 20 yakalandı.**
- Kaçan 8 denemenin 4'ü (J2, J3, J8, J12) yalnız ASCII denetimiyle, rastlantıyla düştü; 4'ü (J1, J7, J10, J11) denetimi tümden geçti.
- Bugünkü metinde bu biçimlerin hiçbiri yok (§1b, elle okundu). Bu yüzden engelleyici değil.

**D-1 (düşük). Kalıp boşlukları.**
- `rehber_denetim.py:131-140`.
- (a) **Olumsuzlama penceresi.** ±40 karakterdeki herhangi bir "değil", başka bir yan cümleye ait olsa da talimatı aklar (J10). F7b-kontrol 8'deki "değilse" kalıbının "değil," biçimi bu yüzden geçiyor.
- (b) "sigortalar?\s+takılıyken" kalıbı iyelik ekli biçimi kaçırıyor ("sigortası takılıyken", J11).
- (c) "XT60 takılıyken / bağlıyken" kalıpta yok (J7).
- (d) "gerilim varken" kalıpta yok (J12).
- (e) Fiil listesi dar: "değiştir", "bağlantı yap" yok (J8).
- (f) Kalıp dışı anlatım ("devre dışı bırak", "kısa devre et", "yerine tel koy") hiç aranmıyor (J1–J3). A bunu açık 5'te kısmen yazmış.
- **Öneri (sonraki tur, engelleyici değil):**
  - Olumsuzlamayı yalnız eşleşmenin kendi yan cümlesinde (virgüle kadar) ara.
  - Kalıplar: `sigorta\w*\s+takılıyken`, `XT60\w*\s+(?:takılı|bağlı)\w*yken`, `gerilim\s+varken`, `devre\s*dışı\s*bırak`, `kısa\s*devre\s*(?:et|yap)`, `yerine\s+tel`, `baypas`.

**D-2 (düşük). Yanlış pozitif: "akü … takılı" kalıbı geniş.**

| # | Doğru metin (eklendi) | Sonuç |
|---|---|---|
| P1 | B1a: "Akü ön takozu ısıl gömmeye takılı" | **yanlış bulgu** |
| P2 | B3: "Akü kayışları takılı, toka yanda" | **yanlış bulgu** |
| P3 | B3: "Akü kutupları bantlı; bant takılı kalsın" | temiz (";" cümleyi bölüyor) |
| P4 | F5: "Enerjiliyken hiçbir konnektörü sökme" | temiz (olumsuz biçim) |

- Kalıp "akü"den sonraki 25 karakterde herhangi bir "takılı / bağlı" görünce tutuyor (`rehber_denetim.py:134`). Öznesi akü olmasa da tutuyor.
- Bugünkü metinde bu tür cümle yok. Gerçek veride istisna 5, B tek tek okudu, **5'i de doğru**:
  - K1 "köprülenmez", K1 "köprülenmedi", E3a "köprülenmez", E4 "köprülenmez": olumsuz biçim.
  - K2 "akü XT60 ayrık, F3 (kafa) takılı değil": "takılı" F3 için; "değil" olumsuzlaması doğru akladı. Kalıp burada da öznesi akü olmayan "takılı"yı tuttu.
- **Öneri:** kalıbı `akü(?:yü|nün)?\s+(?:XT60\s+)?(?:bağlı|takılı)` gibi daralt; "takoz / kayış / kutup" sonrası eşleşmeyi atla.

## 3. PDF

**B'nin ölçümü (`SPB/pdf_olc.py`):**
- Ölçülen dosyalar: depodaki PDF (sha1 `554da292f2ed…`) ve B'nin ürettiği PDF.

| Ölçüt | Depo PDF'i | B'nin PDF'i |
|---|---|---|
| Sayfa (pypdf / PyMuPDF) | 52 / 52 | 52 / 52 |
| En küçük yazı, pypdf (`font_size × Tm × CTM`) | 8,1 pt | 8,1 pt |
| En küçük yazı, PyMuPDF | 8,1 pt | 8,1 pt |
| 8 pt altı sayfa | 0 | 0 |
| "Sayfa i / 52" alt bilgisi | 52 sayfada doğru | 52 sayfada doğru |
| "(devam)" sayfaları | 33, 35 | 33, 35 |

- 8,1 pt'teki metin 14.093 karakter: alt / üst bilgi ve gri açıklamalar.
- Görüntülerin içindeki raster yazı (3B lejantı) ölçüme girmez. Kabul metin yazısı için.
- B'nin PDF'i ile depo PDF'inin metni, üretim saati maskelenince 52 sayfanın 52'sinde aynı.

**Sayfa eşlemesi.**
- Her sayfanın üst bilgisindeki "Adım N / 49" okunarak eşleme yeniden kuruldu.
- `kontrol.json` `yazdir.sayfa_esleme` ile **aynı**:
  - 0…30 → 1…31;
  - 31 (E4) → 32, 33;
  - 32 (K2) → 34, 35;
  - 33…49 → 36…52.
- `esleme_tutarli` true, `tasan` boş, `kucuk_yazi` boş.

**Görülen sayfalar (A'nın bakmadıkları, 100 dpi, `SPB/sayfa/`).**

| Sayfa | Adım | Görülen |
|---|---|---|
| 1 | 0 Hazırlık | tek sayfa, alt bilgi "Sayfa 1 / 52" |
| 13 | 12 B5a | "Sigortaları henüz takma" ve yeni "Kartlar takılmadan tezgâhta … XL4016 C …" satırı; taşma yok |
| 15 | 14 B6a | parça listesinde "Arayüz kartı (E2/E3)"; yeni PC817 tezgâh satırı; taşma yok |
| 30 | 29 E3a | TVS ve "iki 5 V hattı köprülenmez" notları; gövde biraz küçük ama okunaklı; tek sayfa |
| 31 | 30 E3 | tek sayfa, kısa adım |
| 38 | 35 F3 | "12 V fişini takmadan önce regülatör çıkışını yeniden ölç … enerjisizken tak"; tek sayfa |
| 51 | 48 H1 | tek sayfa; üst bilgi "Adım 48 / 49", alt bilgi "Sayfa 51 / 52" |

Hepsinde metin doğru adımda, kesik satır yok, en küçük yazı alt / üst bilgi.

## 4. Üretim

**Komut:** `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok --cikti SPB/uret`
- Çıkış 0. Süre yaklaşık 4 dakika.
- Koşudan önce FreeCAD süreci 0, kilit "boş".

**`SPB/uret/kontrol.json`:**
- **50 / 50**, konsol hatası **0**, **1192 ↔ 1192**, her parça tek adımda, 13 şema.
- Telefon 360 px: 7 adım, tümü **360 / 0** (0, 9, 24, 31, 32, 35, 49).
- PDF 52 sayfa (devam 2), HTML 52, eşleme tutarlı, taşan yok. En küçük yazı DOM 8,1 / PDF 8,1 pt.
- Denetim:
  - ASCII 0, gruplama 0, çelişki 0;
  - zorunlu eksik 0 / 21, yasak 0 (istisna 5), kopya eki 0.

**Depoya yazma: 0.** `SPB/sha_once.txt` ile `SPB/sha_sonra1.txt` arasında fark yok (1.429 dosya). `git status --porcelain` aynı.

**`--veri-yok` yeterli mi?** A'nın tespiti doğru. Metin `rehber-veri.json`'a yalnız `rehber_veri.py` ile girer, o da FreeCAD altında koşar. O-1 ve O-2 düzeltmesi için veri aşaması yine kilit altında koşulmalı.

## 5. Demo

- **Kopyada üretim.**
  - Yer: `SPB/demo_kopya/`. İçinde `demo_uret.py`, şablon, 10 kaynak, karar kuyruğu ve `rehber/veri/*.js` var.
  - Koşu: `py -3 -B -X utf8 tasarim/cad/demo_uret.py` → çıkış 0; 127 sayı anahtarı, 14 karar, 153 kalem, 1192 düğüm.
  - Sonuç: depodaki demo ile **bayt bayt aynı** (sha1 `d4ae0587c69a`).
- **HEAD ile karşılaştırma** (`git show HEAD:…` ↔ çalışma ağacı).
  - Değişen yalnız `<script id="kaynak">` içindeki `rehber/veri/rehber-veri.json` parmak izi: `4b35d3edf72c` → `5ccc1e10af16`.
  - 127 anahtarın değeri, kararlar ve kalem işaretleri aynı.
  - `kaynak` bloğu dışındaki HTML aynı.
- **Doğrulama:** `py -3 -B -X utf8 planlama/d158/F9b-dogrula.py` → **0** ("GECER (hata 0)").
  - Maliyet 153 kalem; sayfa kuralı 121 kalem, ara toplam 103.188,02, genel toplam **118.666,22 TL**.
  - Bu tutar F9b commit'iyle aynı. Demo sayıları değişmedi.

## 6. D-6 ölçü geri yazımı

**Veri karşılaştırması (HEAD ↔ çalışma ağacı).**
- 1192 parçanın yalnız `ad` alanı değişti, 327 parçada; başka alan 0.
- Adımlarda değişen yalnız B3, B5a, B6a, K1, F1, F5. `semalar` ve `mesh` aynı.

**Geometriyle karşılaştırma (`rehber/veri/robot.glb`, parça düğümünün mesh sınır kutusu).**

| # | Eski → yeni ad (kod) | Mesh kutusu (mm) | Boy − ad ölçüsü |
|---|---|---|---|
| 1 | S1 kulak cıvatası M4x001 → M4x16 (M4x16 DIN 912) | 7,0 × 7,0 × 20,0 | 4 = M4 baş |
| 2 | Yuva bağlantı cıvatası M6x001 → M6x16 | 10 × 10 × 22 | 6 = M6 baş |
| 3 | Kapak cıvatası M3x001 → M3x12 | 5,5 × 5,5 × 15 | 3 = M3 baş |
| 4 | Tambur cıvatası M3x001 → M3x8 | 5,5 × 5,5 × 11 | 3 |
| 5 | Çatal-horn cıvatası M3x001 → M3x8 (omuz) | 5,5 × 5,5 × 11 | 3 |
| 6 | Çatal-horn cıvatası M3x001 → M3x12 (dirsek; aynı eski ad, farklı ölçü) | 5,5 × 5,5 × 15 | 3 |
| 7 | VESA cıvatası M4x001 → M4x12 | 7 × 7 × 16 | 4 |
| 8 | Taşıyıcı cıvatası M6x001 → M6x18 | 10 × 10 × 24 | 6 |
| 9 | Hoparlör kelepçe cıvatası M3x001 → M3x20 | 5,5 × 5,5 × 23 | 3 |
| 10 | Boyun cıvatası M6x001 → M6x20 | 10 × 10 × 26 | 6 |
| 11 | Rulman yuvası cıvatası M3x001 → M3x10 | 5,5 × 5,5 × 13 | 3 |
| 12 | Tilt servosu kulak cıvatası M4x001 → M4x16 | 7 × 7 × 20 | 4 |

- Toplam boy = nominal boy + DIN 912 baş yüksekliği (k = d) bağıntısı 22 farklı vida adının **22'sinde** tutuyor.
- 327 parçanın tamamı (vida, somun, pul) aynı adlı eksiz bir kardeşle birebir aynı mesh ölçüsünde (en büyük fark 0,000 mm).
- Tüm veride ad ile kod arasında ölçü farkı 0.
- **Yanlış ölçü yazılan parça yok.**

## 7. Karar taslakları

**KT-F7c-1.**
- Veri sayfası URL'den indirildi; içerik veri olarak okundu, talimat sayılmadı. PyMuPDF ile, ayrı klasörde ve `-I` ile açıldı.
- Doğrulanan alıntılar:
  - "Document number: DS21502 Rev. 20 - 4";
  - "August 2024";
  - "Marking: Unidirectional - Type Number and Cathode Band";
  - "Marking: Bidirectional - Type Number Only";
  - "OBSOLETE – PART DISCONTINUED".
- P6KE6V8A satırı: VRWM 5,80 V; VBR 6,45 / 7,14 V; VC 10,5 V; IPP 57,0 A. Hepsi A'nın yazdığıyla **aynı**.
- "Katot +5 V'a" yönünün sayfada yazmadığı, çıkarım olduğu da doğru.

**KT-F7c-2.**
- `maliyet.json` `kalemler[66]`: "P6KE6V8A Transil Diyot", **adet 2**, 6,05 TL, Direnc.net, "dogrulandi".
- `robot-bom.csv:144`: "P6KE6V8A TVS (kafa ekrani 5 V);**1**".
- İkisi de doğru. Maliyet etkisi 0 TL doğru.

**KT-F7c-3.**
- Doğrulanan kalemler:
  - `[146]` LM2577 + LM2596, adet 1, 275,67 TL;
  - `[86]` "2A Mini Alçak Profil", adet 1, 7,34 TL, notu "F5 2 A standart";
  - `[90]` standart 2 A, 4,28 TL;
  - `[85]` hat sigortası yuvası, adet 5, 36,72 TL; notu 4 kullanım sayıyor.
- `elektrik.md:46` "×5 (A, B, C, şarj + göğüs)", `:60-62` göğüs dalı.
- `robot-bom.csv`: yalnız `:113` 6 yollu kutu ve `:137` 30 A ana sigorta yuvası var; regülatör, mini 2 A ve hat yuvası yok.
- Atıfların hepsi doğru. Fiyat uydurulmamış.

## 8. Bütünlük, diff, ad ve yol

**Tarama ve regresyon:**
- `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` → **0** ("izlenen 17 dosyanin ozetleri kayitla ayni");
- `py -3 -B planlama/d158/regresyon.py --yazma` → **0** ("GEÇER").

**Diff incelemesi.**
- A'nın 14 izlenen dosyasındaki diff'ler günlükteki önce / sonra metniyle birebir:
  - `rehber_metin.py`: B3, B5a, B6a, K1, F1, F5 ve `kopya_eki_sil`;
  - `rehber_veri.py`: tek satır, `gorunen_ad`;
  - `rehber_denetim.py`: (6), (7), `ZORUNLU` 21, sözlük;
  - `rehber_uret.py`: PDF kabulü;
  - `yazdir.html`: devam sayfası, 8,1 pt; dış kaynak eklenmedi;
  - `R-gunluk.md`: iki giriş.
- Brief dışı değişiklik yok.

**Bu paketin olmayan değişiklikler.**
- `tasarim/freecad/kabuk/gorsel/*.png` (13 dosya, 14:28) ve `tasarim/freecad/montaj/yerlesim-kontrol.json` (03.11): F7c brief'inden (18:48) önce değişmişler, A'nın değil.
- `planlama/dongu-158.md`: orkestratörün.
- Bunlar listeye girmez.

**Kural sapması (`__pycache__` silme).**
- Klasör izlenmiyor (`.gitignore:1`) ve FreeCAD koşusu yeniden üretti.
- Depoya etkisi yok; bildirim yeterli.

**Ad ve yol taraması (`SPB/ad_tara.py`).**
- Takma ad ve soyad çalışma anında türetildi, yazılmadı:
  - takma ad: F7b-kontrol'deki yöntemle, `647cafc` farkından;
  - soyad: `00-genel.md`'den.
- Taranan 13 dosya:
  - `F7c-brief.md`, `F7c-gunluk.md`;
  - 4 betik, `yazdir.html`, `R-gunluk.md`;
  - `rehber-veri.json` / `.js`, `kontrol.json`, demo;
  - PDF: metin ve meta.
- Sonuç:
  - takma ad **0**, soyad **0**, "ad + büyük harfli kelime" **0**;
  - yerel kullanıcı yolu **0**.
- Yol isabetleri yalnız 3 yanlış pozitif ve HEAD'de zaten var:
  - `rehber_veri.py:3` ve `rehber_uret.py:40`: FreeCAD kurulumunu gösteren ortam değişkeninin adı (yol değil);
  - `rehber_uret.py:180`: Chrome'un pencere genişliğini anlatan bir docstring cümlesi (yol değil).
- B'nin bu dosyasında da yerel yol yok.

## Genel karar

**KOŞULLU.** F7c'nin altı bulgusu (D-10, D-11, D-12, D-1', D-3, D-6) ve madde 7 kabul düzeyinde yapılmış:
- PDF ≥ 8 pt;
- denetimler, üretim, demo, tarama ve regresyon 0;
- D-6 geometriyle doğru;
- karar taslakları kaynakla doğru;
- köprüleme, akülü bağlantı ya da enerjiliyken takma / sökme talimatı 0.

Ancak en önemli madde olan güvenlik metninde iki orta bulgu var:
- **O-1:** aşama 1'de sigortaların durumu eksik. "Röle kapanmaz" donanımla güvencede değil; göğüs dalının boştaki ucu gerilimli olabilir.
- **O-2:** mantar ölçüm noktası tanımsız.

İkisi de kısa metin düzeltmesi. Commit, A'nın düzeltmesinden ve B'nin dar yeniden kontrolünden sonra yapılmalı.

**Bulgu sayısı:**
- kritik 0;
- orta 2: O-1, O-2;
- düşük 4: D-1, D-2, D-3, D-5. D-1, D-2 ve D-5 engelleyici değil, sonraki tura bırakılabilir.

## A için düzeltme listesi

1. **O-1 (zorunlu).** `rehber_metin.py` değişiklikleri:
   - **F1 aşama 1:** "Akü XT60 ayrık, ana anahtar kapalıyken ana sigorta (30 A), F4 ve F5'i tak; F1 (20 A), F3 (kafa), hat sigortaları A / B / C ve göğüs 2 A takılı değil: anahtarlı bara ve göğüs dalı enerjisiz (doğrulanmadı)".
   - **F5 aşama 2:** "Akü XT60 ayrıkken F1, F3 ve A / B / C sigortalarını tak".
   - **F3 madde 3:** regülatör ölçümünden önce "akü ayrıkken göğüs 2 A sigortasını tak".
   - **`rehber_denetim.py` `ZORUNLU`:** F1 için `F1 \(20 A\).*takılı değil` satırı.
2. **O-2 (zorunlu).** F1 aşama 1 mantar ölçümü:
   - kırmızı uç PC817 #1 giriş klemensine (arayüz kartı), siyah uç WAGO GND yıldız noktasına;
   - mantar uçlarına klips takılmaz;
   - uçlar akü ayrıkken takılır, "ana anahtarı kapat, aküyü ayır" sonrasında sökülür;
   - "doğrulanmadı" işareti kalır.
3. **D-3 (önerilir, aynı turda ucuz).** F5 aşama 2:
   - "mantara basınca servo gücü kesilir, kollar düşer: düşme hattında kimse yok" (`elektrik.md:262`);
   - ön koşula "PWM = 0";
   - iki aşamada "ana anahtar kapalıyken aküyü XT60'tan tak";
   - "saat, yüzük, bileklik çıkarılır" (kural 8).
4. **Yeniden üretim.**
   - Veri aşaması kilit altında `--gorsel-yok`, sonra `--veri-yok`.
   - `demo_uret.py` ve `F9b-dogrula.py` 0.
   - `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0.
   - Günlüğe önce / sonra metni.
5. **Sonraki turlar (engelleyici değil).**
   - D-1: denetimde olumsuzlama penceresini yan cümleyle sınırla; kalıp ekleri (§2).
   - D-2: "akü … takılı" kalıbını daralt.
   - D-5: F3 "enerjiyi kes" ifadesini açık yaz.

## C için kesin `git add` listesi

A'nın düzeltmesi ve B'nin dar kontrolü GEÇER olunca geçerli. Düzeltme turunda başka bir adım PNG'si de değişirse (ör. `planlama/rehber/goruntu/adim-33.png`), B'nin dar kontrolü onu listeye ekler.

```
git add tasarim/freecad/rehber/rehber_metin.py \
        tasarim/freecad/rehber/rehber_veri.py \
        tasarim/freecad/rehber/rehber_denetim.py \
        tasarim/freecad/rehber/rehber_uret.py \
        rehber/yazdir.html \
        rehber/veri/rehber-veri.json \
        rehber/veri/rehber-veri.js \
        planlama/rehber/R-gunluk.md \
        planlama/rehber/kontrol.json \
        planlama/rehber/Lale-montaj-rehberi.pdf \
        planlama/rehber/goruntu/adim-17.png \
        planlama/rehber/goruntu/adim-49.png \
        planlama/rehber/goruntu/telefon-360-adim-49.png \
        tasarim/Robot-Tasarim-Demosu.html \
        planlama/d158/F7c-brief.md \
        planlama/d158/F7c-gunluk.md \
        planlama/d158/F7c-kontrol.md
```

**Girmez:**
- `planlama/d158/FREECAD-KILIT.txt`, `planlama/dongu-158.md`;
- `tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json` (başka paketlerin);
- `__pycache__/`;
- `rehber/veri/robot.glb` ve `robot-glb.js`: yeniden yazıldı ama içerik aynı, git fark göstermiyor.

## Commit mesajı

```
Lale P7.3: rehberde kalanlar: ilk enerji iki aşamalı (F1 kafasız, sigortalı; F5 devreye alma), mantarda K1 düşer, B3/B5a/B6a tezgâh ayarı, denetimde yasak talimat taraması, PDF ≥ 8 pt (52 sayfa, eşleme kontrol.json), FreeCAD eki temiz, demo parmak izi (F7c)
```

## Kanıtlar (komut → çıktı, özet)

```
sha1 (.git hariç 1.429 dosya) önce ↔ sonra                      → aynı; git status --porcelain aynı
SPB/tara.py (50 adım, 9 alan)                                     → 49 isabet; köprüleme / akülü bağlantı / enerjiliyken tak-sök talimatı 0
SPB/denetim: rehber_denetim.py (kopya)                           → 0; zorunlu 0/21, yasak 0, istisna 5, kopya eki 0
SPB/enjekte_b.py                                                  → 20 enjeksiyonun 12'si yakalandı; P1, P2 yanlış bulgu, P3, P4 temiz
SPB/pdf_olc.py (depo PDF ve B PDF)                                → 52 / 52 sayfa; en küçük 8,1 pt (pypdf, PyMuPDF); eşleme = kontrol.json
rehber_uret.py --veri-yok --cikti SPB/uret                        → 0; 50/50, konsol 0, 1192 ↔ 1192, 360 px 7/0, PDF 52, 8,1 pt
SPB/demo_kopya: demo_uret.py                                      → 0; demo bayt bayt aynı (d4ae0587c69a); 127 anahtar aynı
F9b-dogrula.py                                                    → 0 (GECER, hata 0); genel 118.666,22 TL
GLB sınır kutusu ↔ geri yazılan ad                                → 22/22 vida adı; 327/327 parça eksiz kardeşle aynı ölçü
Diodes DS21502 Rev. 20-4 (PyMuPDF metni)                          → KT-F7c-1 alıntıları ve P6KE6V8A değerleri aynı
carpisma_kos.py kontrol / regresyon.py --yazma                    → 0 / 0
SPB/ad_tara.py (13 dosya + PDF metin/meta)                       → takma ad 0, soyad 0, ad + büyük harf 0, yerel yol 0
```

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

**Kapsam.** A'nın "Düzeltme turu 1" kaydı (`planlama/d158/F7c-gunluk.md:290-`). Bu tur dar bir kontrol: O-1, O-2, D-3, D-1 ve D-2 ile bunlara bağlı üretim ve bütünlük.

**B'nin çalışma koşulları.**
- Çalışma klasörü: `SPB/t1/`.
- FreeCAD koşulmadı, kilide yazılmadı; kilit "boş".
- Git'e yazılmadı, hiçbir şey silinmedi. Python `-B` ve `PYTHONDONTWRITEBYTECODE=1` ile koşuldu.
- Depoya yazma yok:
  - kontrol başında ve sonunda alınan sha1 listeleri (`SPB/t1/sha_once.txt` ↔ `sha_sonra.txt`) aynı;
  - `git status --porcelain` aynı;
  - bu bölümün eklenmesi tek istisna.

**Bu turda değişen dosyalar.** B'nin önceki kaydıyla karşılaştırıldı.
- Kaynak: `rehber_metin.py`, `rehber_denetim.py`.
- Üretilen: `rehber-veri.json`, `rehber-veri.js`, `kontrol.json`, PDF; `adim-17`, `adim-35`, `adim-49`, `telefon-360-adim-35` ve `telefon-360-adim-49` PNG'leri; demo.
- Kayıt: `R-gunluk.md`, `F7c-gunluk.md`.
- Ayrıca `__pycache__/rehber_metin.cpython-311.pyc`: izlenmiyor, A'nın üretim koşusu yazdı.
- `planlama/dongu-158.md` orkestratörün.

A'nın listesiyle aynı. `rehber_veri.py`, `rehber_uret.py`, `yazdir.html` ve `robot.glb` değişmedi.

**Veri karşılaştırması (önceki tur ↔ bu tur).**
- Parçalar, şemalar ve mesh aynı.
- Değişen yalnız şu alanlar: K1 `is_`, F1 `kontrol`, F3 `is_`, F5 `is_`.

## Madde sonuçları

| # | Madde | Etiket |
|---|---|---|
| 1 | Sigorta ve röle mantığı (aşama 1 / 2, F3 göğüs 2 A) | **GEÇER**: O-1 kapandı |
| 2 | Mantar ölçümü | **GEÇER**: O-2 kapandı; düşük bir eksik var (D-8) |
| 3 | Denetim: J1–J20, P1–P4, 11 yeni enjeksiyon, 4 yeni olumsuz deneme, 3 silme | **GEÇER** (sınırları belgeli): J 20 / 20; yeni denemelerin 5 / 11'i; silmelerin 0 / 3'ü yakalandı; 120 karakterlik pencere bir doğru cümlede yanlış alarm verdi, gerçek veride 0 (D-6', D-7) |
| 4 | PDF | **GEÇER**: 53 sayfa, en küçük yazı 8,1 pt; değişen 4 sayfa ve yeni sayfa 53 görüldü |
| 5 | Bütünlük | **GEÇER**: 50/50, konsol 0; demo bayt bayt aynı; F9b 0; tarama 0; regresyon 0; takma ad ve yerel yol 0 |
| 6 | Liste ve commit mesajı | güncellendi (aşağıda) |

## 1. Sigorta ve röle mantığı

B kaynağı kendisi açtı: `elektrik.md:91` (sigorta dalları), `:323-339` (blok şeması), `:362-372` (sigorta listesi), `:440-445` (E9 devresi), `:458` (GPIO2).

| Metin (F1 aşama 1 / F5 aşama 2 / F3) | Kaynak | Sonuç |
|---|---|---|
| Takılı: ana 30 A, F4 5 A (XL4016 çevre: ESP32), F5 2 A (mantar, röle bobinleri) | `:364`, `:368`, `:369`; `:338-339` | **aynı** |
| Takılı değil: F1 20 A (K1 ve K2 kolu), F3 5 A, hat A 7,5 / B 7,5 / C 5 A, göğüs mini 2 A | `:365`, `:367`, `:370-371`; `:91` | **aynı**. Hat sigortaları anahtarlı baradan beslendiği için F1 yokken zaten enerjisiz |
| "F1 takılı olmadığı için K1 ve K2'nin kontakları enerjisiz; K2 GPIO2 / LED programıyla tıklayabilir" | `:440-441` (iki kontak da F1'den sonra), `:443-445` (bobinler F5'ten), `:458` | doğru. Röle hangi programla çekerse çeksin bara enerjisiz: **donanımla güvencede** |
| Sigortalar "akü XT60 ayrık, ana anahtar kapalıyken" takılıyor (F1, F5, F3) | 00-genel kural 1 | **aşama 1, aşama 2 ve F3'te üçü de akü ayrıkken.** Doğru |

**Aşama 1'de açıkta gerilimli uç var mı? Yok.** Yalnız F4 ve F5 dalları enerjili; ikisinin de uçları kapalı.
- **F4** (`:338`): XL4016 çevre 5 V → ESP32 VIN, sonar ×3, enkoder, PCA9685 / BNO055 mantığı.
  - Hepsi B3, B6a, B7 ve K1'de kartlara ve klemenslere bağlanmış durumda.
  - Tek boştaki uç ESP32 USB kablosunun hub ucu. Bu uç 1N5819'un anot tarafında (K2 madde 4), çevre 5 V oraya geri beslenemez.
- **F5** (`:339`): mantar NC → K1 / K2 bobinleri → IRLZ44N → GND; PC817 #1 girişi.
  - Mantar F1 madde 3'te bağlandı, bobinler güç panelinde, IRLZ44N arayüz kartında.
  - Boşta uç yok.
- **Diğer dallar:** F3 (kafa), göğüs dalı ve bara enerjisiz. Göğüs ekranının boştaki 12 V ucu artık enerjisiz.
- Aşama 1'deki "tekerlekler yerden kesik" düzeni artık fazladan önlem; zararı yok.

**Aşama 2.**
- "Akü XT60 ayrık, ana anahtar kapalıyken F1 (20 A), F3 (5 A, kafa) ve XL4016 hat sigortalarını … tak" sırası doğru.
- BMS satırında "K11 a ise göğüs ekranı dalı da" tutarlı: göğüs 2 A sigortası F3'te takıldı.
- "Kollar aşağıda başlar … kollar düşer", "BTS EN = 0 ve PWM = 0" ve kural 8 eklenmiş. D-3 kapandı.

**F3 göğüs 2 A sırası güvenli.**
- Sigorta akü ayrık, ana anahtar kapalıyken takılıyor.
- Sonra regülatör çıkışı fiş takılmadan ölçülüyor (`elektrik.md:67`: "ekrana bağlamadan … 12 V'a ayarla").
- Fiş enerjisizken takılıyor.
- İki düşük eksik var, D-9'da.

## 2. Mantar ölçümü

Kaynak devre: `elektrik.md:235` (PC817 kanal 1 = mantar NC sonrası düğüm), `:249-251`, `:339`, `:341` (toprak: WAGO yıldız noktası).

- "Kırmızı uç PC817 #1 giriş klemensi, siyah uç WAGO GND yıldız noktası" ölçümü mantar sonrası düğümün gerilimini verir. Kaynakla **tutarlı**.
  - Mantar serbestken akü gerilimi; basılıyken 0 V.
  - Aşama 1'de K2 tıklasa da bobin akımı küçük (`:369`, F5 2 A dalı); okumayı etkilemez.
- **Köprüleme riski kalmadı.**
  - PC817 modülünde yalnız mantar **sonrası** düğüm var. Mantar öncesi düğüm (F5 çıkışı) modülde yok.
  - Kayan bir kıskaç olsa olsa bu düğümü GND'ye kısa devre eder ve F5 2 A atar. Mantarı köprüleyemez.
  - Ayrıca "ölçü kıskacını mantar uçlarına takma" yazıyor; bu satır `ZORUNLU`'da korunuyor.
  - Sökme sırası doğru: "ana anahtarı kapat, aküyü ayır, sonra ölçü uçlarını sök".

**D-8 (düşük). Multimetre kademesi ve klemens ucu yazmıyor.**
- Multimetre akım kademesinde (10 A soketi) bırakılırsa bu bağlantı mantar sonrası düğümü GND'ye kısa devre eder ve F5 2 A atar. `00-genel.md`'deki multimetre kuralı bunu yasaklıyor.
- Öneri: "multimetre DC V kademesinde, kırmızı uç V soketinde".
- "Giriş klemensi" modülde + ve − uçlarından hangisi, yazmıyor. Öneri: "girişin + ucu".

## 3. Denetim

**Yöntem.**
- Depodaki `rehber_denetim.py` (`2e9fb8230d9e`), `rehber_metin.py` (`96d9182310f8`) ve `rehber-veri.json` (`09ca1380e7b3`) `SPB/t1/denetim/`'e kopyalandı.
- Temiz kopya: çıkış 0; zorunlu eksik 0 / 23, yasak 0, istisna 4 (hepsi "köprülenmez / köprülenmedi"), kopya eki 0.
- Betikler: `SPB/t1/enjekte_t1.py`, `SPB/t1/enjekte_sil.py`.
- Metni değişen üç deneme yeni metne uyarlandı:
  - J15: "röle K1 ve K2'nin kontakları enerjisiz" → "röle K1 kapanır";
  - J17 ve J18: "Akü XT60 ayrık, ana anahtar kapalıyken F1" → "Akü bağlıyken F1" / "Ana anahtar açıkken F1".

**J1–J20 (B'nin ilk turdaki seti): 20 / 20 yakalandı** (ilk turda 12 / 20).
- Kalıp dışı J1 "devre dışı bırak", J2 "kısa devre et" ve J3 "yerine tel koy" artık yasak bulgusu.
- J7 "XT60 takılıyken", J8 "değiştir", J10 "takılı değil, uçlarını köprüle", J11 "sigortası takılıyken" ve J12 "gerilim varken" de yakalanıyor.

**P1–P4 (doğru metinler): 4 / 4 temiz.** P1 ve P2'deki yanlış alarm kalktı; D-2 kapandı.

**Yeni enjeksiyonlar (B, bu tur).**

| # | Enjeksiyon | Sonuç |
|---|---|---|
| K1 | F1'e "Ölçüm için mantar NC uçlarını birleştir" | **kaçtı** (denetim geçti) |
| K2 | F5'e "F1 sigortası yoksa sigorta yerine tel kullan" | yakaladı ("yerine tel kullan") |
| K3 | F1'e "Ölçerken mantarın iki ucunu kıskaçla birbirine bağla" | **kaçtı** |
| K4 | F5'e "Akü takılıyken F1 sigortasını tak" | yakaladı |
| K5 | F5'e "Ana anahtarı açtıktan sonra F1'i tak" | **kaçtı** |
| K6 | F5'e "Yazılım hazır değilse röleyi elle kapat" | **kaçtı** (F5 notundaki "röleler elle kapatılmaz" ile çelişiyor, ama korunmuyor) |
| K7 | F1'den "Ölçü kıskacını mantar uçlarına takma." silindi | yakaladı (zorunlu) |
| K8 | F1 "göğüs ekranı mini 2 A takılı değil" → "takılı" | yakaladı (zorunlu) |
| K9 | F3 "Akü XT60 ayrık, ana anahtar kapalıyken göğüs …" → "Ana anahtar açıkken göğüs …" | yakaladı (yasak) |
| K10 | F1 "akü ayrıkken multimetrenin kırmızı ucunu …" → "enerji varken …" | **kaçtı**: "bağla" 120 karakterden uzakta |
| K11 | F1 sökme sırası bozuldu: "ölçü uçlarını sök, ana anahtarı kapat, aküyü ayır" | **kaçtı** |
| S1 | F3'teki göğüs 2 A cümlesi tümden silindi | **kaçtı** |
| S2 | F5'teki "F1, F3, A / B / C sigortalarını tak" cümlesi silindi | **kaçtı** |
| S3 | F5'teki "Kollar aşağıda başlar … kollar düşer" cümlesi silindi | **kaçtı** |

| # | Doğru metin (eklendi) | Sonuç |
|---|---|---|
| P5 | F1'e "Ana anahtar açıkken yalnız BMS ışığını gözle, bitince ana anahtarı kapat, aküyü ayır ve ölçü uçlarını sök" | **yanlış alarm** (120 karakterlik pencere "sök"e uzanıyor) |
| P6 | F5'e "Enerji varken yalnız ölç, hiçbir kablo takma" | temiz |
| P7 | F1'e "Mantar NC uçları ayrı kalır, kısa devre yapmaz" | temiz |
| P8 | F5'e "Sigortanın yerine tel koyma" | temiz |

**D-6' (düşük). Kalan denetim boşlukları.**
- K1 "mantar NC uçlarını birleştir" yakalanmıyor. Orkestratörün istediği örnek buydu. K3 "birbirine bağla" da kaçıyor; "köprüle" dışındaki eş anlamlılar kalıpta yok.
- Kalıp dışı kalanlar: K5 "açtıktan sonra … tak", K6 "röleyi elle kapat".
- Yeni güvenlik cümlelerini koruyan `ZORUNLU` satırı yok: S1 (F3 göğüs 2 A), S2 (F5 sigortaları), S3 (kollar düşer), K11 (sökme sırası).
- Öneri (sonraki tur):
  - `ZORUNLU`'ya şu satırlar: F3 `ana anahtar kapalıyken göğüs ekranı mini 2 A`; F5 `kapalıyken F1 \(20 A\).*tak`; F5 `kollar düşer`; F1 `XT60'tan ayır, sonra ölçü uçlarını sök`.
  - Yasak kalıba: `(?:mantar|acil stop)\w*[^.]{0,40}(?:uçlarını|ucunu)[^.]{0,30}(?:birleştir|birbirine bağla)` ve `röle\w*\s+elle\s+kapat`.
  - Bugünkü metinde bu biçimlerin hiçbiri yok. Engelleyici değil.

**D-7 (düşük). 120 karakterlik pencerenin yanlış alarmı.**
- Gerçek veride enerji önekinin ("ana anahtar açıkken", "enerji varken", "XT60 takılıyken" vb.) geçtiği yer **0**, yani bugün yanlış alarm 0.
- Ama P5 gibi doğru ve olası bir cümle yasak bulgusu veriyor. Pencere öneki ve fiili yan cümle sınırına bakmadan bağlıyor.
- J18'in liste içi virgülleri yüzünden yalnız virgülde kesmek yetmez. Öneri: "sonra / bitince / ardından / ve" bağlaçlarında kes, virgülde kesme.
- Engelleyici değil.

## 4. PDF

- B'nin ölçümü (`SPB/pdf_olc.py`), depo PDF'i (sha1 `0fd7c550afa2`) ve B'nin PDF'i üzerinde:
  - pypdf ve PyMuPDF **53** sayfa; en küçük yazı **8,1 pt**; 8 pt altı sayfa 0;
  - "Sayfa i / 53" alt bilgisi 53 sayfada doğru;
  - "(devam)" sayfaları 33, 35 ve 53.
- Başlıktan kurulan eşleme `kontrol.json` `yazdir.sayfa_esleme` ile aynı; 49 (F5) → 52, 53.
- B'nin PDF'i ile depo PDF'inin metni, saat maskelenince 53 sayfanın 53'ünde aynı.
- **Değişen sayfalar** (önceki 52 sayfalık PDF'e göre metni değişen): 18, 36, 38, 52. Bir de yeni sayfa 53. Hepsi görüldü (100 dpi, `SPB/t1/sayfa/`).

| Sayfa | Adım | Görülen |
|---|---|---|
| 18 | 17 K1 | Madde 6: "F1 takılı değil, anahtarlı bara enerjisiz". Kablo yolu 10: "F5 → mantar (NC) → röle bobini → MOSFET (arayüz kartı)". E3 ile tutarlı; tek sayfa |
| 36 | 33 F1 | Aşama 1 metni tam: sigorta listesi, ölçü noktası, kıskaç uyarısı, sökme sırası. Gövde 9,6 pt; tek sayfa |
| 38 | 35 F3 | Madde 3'te göğüs 2 A satırı; tek sayfa |
| 52 | 49 F5 | Aşama 2 metni tam; gövde 8,7 pt, sık ama okunaklı; notlar ve kontrol listesi bu sayfada |
| 53 | 49 F5 (devam) | Yalnız "Erişim notu" (bir satır); taşma değil, kabul "her adım ≥ 1 sayfa" |

## 5. Bütünlük

**Üretim:** `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok --cikti SPB/t1/uret` → çıkış **0**.
- **50 / 50**, konsol **0**, **1192 ↔ 1192**, her parça tek adımda.
- Telefon 360 px: 7 adım, 7 / 0 taşma.
- PDF 53 sayfa (devam 3), HTML 53, eşleme tutarlı, taşan yok, en küçük yazı 8,1 / 8,1 pt.
- Denetim: zorunlu eksik 0 / 23, yasak 0, kopya eki 0.

**Demo.**
- Kopyada üretim (`SPB/t1/demo_kopya/`): `demo_uret.py` → 0; depodaki demo ile **bayt bayt aynı** (sha1 `d3f8fcd89029`).
- HEAD'e göre fark yalnız `rehber-veri.json` parmak izi (`4b35d3edf72c` → `85a3cc196adb`). 127 anahtar, kararlar ve kalemler aynı; `kaynak` bloğu dışındaki HTML aynı.
- `F9b-dogrula.py` → **0** (GECER, hata 0); genel toplam 118.666,22 TL.

**Tarama ve regresyon:**
- `carpisma_kos.py kontrol` → **0**;
- `regresyon.py --yazma` → **0** ("GEÇER").

**Ad ve yol (`SPB/ad_tara.py`).**
- Taranan: `F7c-gunluk.md`, `rehber_metin.py`, `rehber_denetim.py`, `R-gunluk.md`, `rehber-veri.json` / `.js`, `kontrol.json`, PDF (metin ve meta), demo.
- Sonuç: takma ad **0**, soyad **0**, "ad + büyük harf" **0**, yerel yol **0**.

## Düşük bulgular (bu tur)

**D-9 (düşük). F3'te iki eksik var.**
- "K11 b seçilirse bu ölçüm F5 aşama 2'ye kalır" deniyor, ama aynı maddede 12 V fişi koşulsuz olarak F3'te takılıyor. B seçeneğinde fiş ölçülmeden takılmış olur; bu `T7-gogus-ekrani-12v.md`'deki "ekrana bağlamadan önce" kuralıyla çelişir.
- Ölçüm için "ana anahtar kapalıyken aküyü tak, ana anahtarı aç" yazmıyor. Önceki D-5 ("ölçünce enerjiyi kes" belirsizliği) de açık.
- K11 karar bekliyor ve metinde "doğrulanmadı" var. Engelleyici değil.

**D-10 (düşük, bilgi). Şarj girişi rehberde yok.** Şarj girişi mini 10 A (`elektrik.md:372`: "XT60 şarj girişi → akü + (ana anahtar öncesi)") rehberin hiçbir adımında geçmiyor. Kablolanırsa aşama 1'deki "takılı değil" listesine girmeli. Bu, F7c'den önceki bir eksik.

## Genel karar (düzeltme 1 sonrası)

**GEÇER. F7c commit edilebilir.**
- **O-1 kapandı.** Aşama 1'de F1 takılı değil, bu yüzden röle ne yaparsa yapsın bara enerjisiz. Bu artık donanımla güvencede. Açıkta gerilimli uç yok. Sigortalar her aşamada akü ayrıkken takılıyor.
- **O-2 kapandı.** Ölçüm noktası kaynakla tutarlı, mantarı köprüleme riski yok, sökme sırası doğru.
- **D-3, D-1 ve D-2 kapandı.** Denetimde 20 / 20 yakalama ve 4 / 4 temiz.
- Üretim, PDF, demo, tarama, regresyon, ad ve yol kontrolleri 0.

**Açık bulgular:**
- kritik 0, orta 0;
- düşük 6: D-5, D-6', D-7, D-8, D-9, D-10.

Hiçbiri commit'i engellemez. Bir sonraki metin ya da denetim turuna önerilir.

## C için kesin `git add` listesi (19 dosya)

```
git add tasarim/freecad/rehber/rehber_metin.py \
        tasarim/freecad/rehber/rehber_veri.py \
        tasarim/freecad/rehber/rehber_denetim.py \
        tasarim/freecad/rehber/rehber_uret.py \
        rehber/yazdir.html \
        rehber/veri/rehber-veri.json \
        rehber/veri/rehber-veri.js \
        planlama/rehber/R-gunluk.md \
        planlama/rehber/kontrol.json \
        planlama/rehber/Lale-montaj-rehberi.pdf \
        planlama/rehber/goruntu/adim-17.png \
        planlama/rehber/goruntu/adim-35.png \
        planlama/rehber/goruntu/adim-49.png \
        planlama/rehber/goruntu/telefon-360-adim-35.png \
        planlama/rehber/goruntu/telefon-360-adim-49.png \
        tasarim/Robot-Tasarim-Demosu.html \
        planlama/d158/F7c-brief.md \
        planlama/d158/F7c-gunluk.md \
        planlama/d158/F7c-kontrol.md
```

**Girmez:**
- `planlama/d158/FREECAD-KILIT.txt`, `planlama/dongu-158.md`;
- `tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json` (başka paketlerin);
- `__pycache__/`;
- `rehber/veri/robot.glb` ve `robot-glb.js` (içerik aynı, git fark göstermiyor).

## Commit mesajı (güncel)

```
Lale P7.3: rehberde kalanlar: ilk enerji iki aşamalı (F1 kafasız, F1/F3/dal sigortaları takılı değil, mantar PC817 #1 ↔ GND; F5 sigortalar + devreye alma + ön şarj, mantarda K1 düşer, kollar düşer), B3/B5a/B6a tezgâh ayarı, denetimde yasak talimat taraması (köprüleme, akülü / enerjili iş, devre dışı, kısa devre, yerine tel), PDF ≥ 8 pt (53 sayfa, eşleme kontrol.json), FreeCAD eki temiz, demo parmak izi (F7c)
```

## Kanıtlar (bu tur)

```
sha1 (.git hariç) SPB/t1/sha_once ↔ sha_sonra                        → aynı; git status --porcelain aynı; kilit "boş"
SPB/t1/denetim: rehber_denetim.py (kopya)                            → 0; zorunlu 0/23, yasak 0, istisna 4, kopya eki 0
gerçek veride enerji öneki isabeti                                    → 0 (120 karakterlik pencerede yanlış alarm 0)
SPB/t1/enjekte_t1.py                                                  → J 20/20; K 5/11; P1–P4 ve P6–P8 temiz, P5 yanlış alarm
SPB/t1/enjekte_sil.py                                                 → S1–S3 0/3 (ZORUNLU yok)
SPB/pdf_olc.py (depo PDF ve B PDF)                                    → 53/53 sayfa; en küçük 8,1 pt; eşleme = kontrol.json; devam 33, 35, 53
rehber_uret.py --veri-yok --cikti SPB/t1/uret                         → 0; 50/50, konsol 0, 1192 ↔ 1192, 360 px 7/0, PDF 53
SPB/t1/demo_kopya: demo_uret.py                                       → 0; bayt bayt aynı (d3f8fcd89029); 127 anahtar aynı
F9b-dogrula.py / carpisma_kos.py kontrol / regresyon.py --yazma      → 0 / 0 / 0
SPB/ad_tara.py (9 dosya + PDF metin/meta)                            → takma ad 0, soyad 0, ad + büyük harf 0, yerel yol 0
```
