**COMMIT EDİLEBİLİR**

# F10i kontrol 4 · P10.7b2a basılı sayfa düzeltmesine bağımsız bakış (commit öncesi son kontrol)

15.11, 06:50–07:00 (saat okundu). Dal `lale-duzeltme`, HEAD `1328b60`, değişiklikler commit edilmemiş çalışma ağacında. Kapsam:
`F10i-gunluk.md` "Basılı sayfa düzeltmesi ve yeniden üretim" (`rehber/yazdir.html`, `rehber_uret.py` `pdf_tamlik()`, yeniden
üretilen PDF). `rehber_uret.py`, FreeCAD, F10* doğrulayıcıları ve `rehber_kol_kablo.py --yazma` koşmadı. Denetimler depo dışındaki
geçici bir kopyada koştu; yalnız okuyan `kablolar_denetim.py` (`git show` gerektiriyor) depoda koştu. Depoda yazılan tek dosya bu
rapor. Ajanın `pdf_tamlik()` kodu tamlık ölçümünde kullanılmadı.

Basılı sayfada eksik, yinelenen ya da sırası bozuk talimat; okunmayı bozan yerleşim hatası; gevşetilmiş eşik; kaynakla uyumsuz çıktı;
bu paketin getirdiği bir gizlilik sorunu bulunmadı. Bulguların hepsi kayıtlı açık iş ya da bilgi.

## 1. PDF tamlığı (kendi yöntemim)

**Yöntem:** metni **pypdf** ile çıkardım (ajan PyMuPDF kullanıyor). Adımın sayfalarını DOM eşlemesinden değil, PDF'teki üst satırdan
("Adım N / 49") buldum: 80 sayfa, 50 adım + 30 devam, sayfa sırası kesintisiz; `kontrol.json` `sayfa_esleme` ile birebir aynı.
Kaynak ve PDF NFKC, bütün boşluklar silinip `**` / `` ` `` işaretleri düşüldü. Ajandan farkı: `is_`'i tek dizi olarak değil
**paragraf paragraf** saydım. Her paragraf adımın sayfalarında tam bir kez ve bir öncekinden sonra geçmeli. Bütün olarak bulunamayan
paragrafı bölünmüş saydım: en uzun önek ve kalan ayrı ayrı arandı, aradaki metin dökülüp elle okundu (bölme sınırında yinelenen sözcük
burada görünür). Maddeler (`not_`, `kontrol`, `kablo`, alt adım `is_`) adımın sayfalarında sayıldı; PDF'teki sayı kaynaktakinden
fazlaysa "yinelenen" sayıldı. Ayrıca `erisim`, `baglanti_md`, `alet`, `baslik` ve bütün parça adları da tarandı.

| Ölçüm | Sonuç |
|---|---|
| `is_` paragrafı | 131 paragraf, 31525 karakter (boşluksuz); **eksik 0, sırası kayan 0** |
| Bölünen paragraf | 1 (K1 madde 5). Önek 236 / 1057 karakter; arada yalnız işaret satırı, sayfa altı / üstü ve devam başlığı var; yinelenen sözcük yok |
| Madde | 304 madde, 38922 karakter; eksik 0 |
| `erisim`, `baglanti_md`, `alet`, `baslik`, parça adları | eksik 0 |
| Adımlar arası fazla (60 karakterden uzun paragraf PDF'te kaynaktan çok) | 0 |
| İlk taramadaki 11 "yinelenen / sıra" işareti | Hepsi yanlış alarm, tek tek doğrulandı: B5 ve B6'nın tek satırlık `is_`'i başlıkla aynı; F1 ve F4'te kısa cümle kaynakta iki kez geçiyor; E4'te (31) 3 ve F3'te (35) 1 alt adım `is_`'i ana `is_`'in içinde de var. Her birinde PDF sayısı = adımın bütün kaynak alanlarındaki sayı. Alt adım kartlarının sırası (son geçişe göre) doğru |

**K1 elle** (pypdf metni, sayfa 19–22 birleşik): 11 paragrafın her birinin ilk ve son üç sözcüğü sırayla, tekil:

| Paragraf | Başı | Sonu |
|---|---|---|
| Giriş | "Kabuk takılmadan önce" s19 | "parantez içinde); sırayla:" s19 |
| 1 | "1. Ana hat" s19 | "(F1 aşama 1)." s19 |
| 1 (G07) | "Akü ölçüm teli" s19 | "yakın okunur (kontrol)." s19 |
| 2 | "2. Toprak (G05," s19 | "… kablolar.json yerleşim kaydı)." s19 |
| 3 | "3. F1 20" s19 | "bağlıyken enerji verme." s19 |
| 4 | "4. Sigorta kutusundan" s19 | "bu karara bağlı." s19 |
| 5 | "5. Acil stop" s19 | "karar bekliyor (K60)." **s20** (bölünme: s19 "… ön şarj kartındaki K2" / s20 "bobini (+; A04) …") |
| 5 (alt kat) | "Alt kat kartlarının" s20 | "mm (sıra kontrolü)." s20 |
| 6 | "6. Enkoder, BTS" s20 | "mantar F1'de takılır." s20 |
| 7 | "7. Direğe çıkacak" s20 | "Yukarısı K2'de." s20 |
| 8 | "8. K1'de enerji" s20 | "kaynakta yok, doğrulanmadı." s20 |

## 2. Bölme kodu (`rehber/yazdir.html:236-286`)

**Deneme yöntemi:** `bol()` ve yerleşim döngüsünün **gerçek kodu** dosyadan satır satır alınıp Node'da sahte sığma modeliyle (sayfa
maliyeti = başlık + karakter + blok ağırlığı + işaret satırı) koşturuldu. Her denemede sayfalardaki iş parçaları yeniden birleştirildi
(parça içinde `\n`, bölünen yerde boşluk).

| Sınır koşulu | Sonuç |
|---|---|
| Tek sözcüklük 400 paragraf | Paragraf sınırında akar, metin tam, işaretler "sürüyor" / "önceki sayfa ile devam" |
| Boşluksuz 5000 karakterlik tek sözcük | Bölünmez (`yer` boş → `null`), sayfa `data-tasma`'ya yazılır, metin tam, döngü biter |
| `**kalın**` içinde sınır (200 sözcüklük kalın) | Kalının içinden bölmez; kalın sayfadan uzunsa taşar (sayılır); parçalarda `**` sayısı çift |
| `` `kod` `` içinde sınır | Aynı: kodun önünde bölündü, `` ` `` çiftleri bütün |
| Madde numarası | Baş parçada en az 6 sözcük (`lo ≥ BOL_EN_AZ-1`): "5." sayfa sonunda tek kalmaz. Liste HTML `<ol>` değil, `white-space: pre-line` düz metin: devam sayfasında sayaç yeniden başlamaz, numara kaybolmaz (PDF s20 "bobini (+; A04) …" ile başlıyor, "6." doğru yerde) |
| Art arda bölme (1200 sözcük, 8 sayfa) | 7 kez bölündü, metin tam, her sayfada "yarım kaldı", devamda "yarım kalan yer burada sürüyor" (`parca` bayrağı doğru taşınıyor) |
| İlk sayfaya hiçbir şey sığmıyor | İlk sayfa taşan sayılır, metin sonraki sayfalara akar, döngü biter |
| Devam sayfasına 6 sözcük bile sığmıyor | `bol` `null`, `k = 1` ile her turda bir blok ilerler: sonsuz döngü yok, her sayfa taşan sayılır |
| Çift boşluk, boş satırlı paragraf, tam 11 sözcüklük paragraf | Metin tam; 11 sözcük bölünmez (eşik `2·6−1`) |

**Karakter kaybı:** bölmede yalnız bölünen tek boşluk `\n` + sayfa sonu olur; çıkan metin `pre-line` ile aynı okunur. Bulunmadı.

**Kodda okundu, denenmedi:** `md()` paragraf başına değil sayfa başına uygulanıyor; `\*\*([^*]+)\*\*` satır sonunu da kapsadığı için
paragraflar arası kalın varsa paragraf sınırında bölme kalın işaretini açıkta bırakabilir. Bugün kaynakta tek sayılı `**` / `` ` ``
içeren paragraf **0** (ölçüldü), etkisi yok.

## 3. Göz (PyMuPDF ile 100 dpi; Read ile bakıldı)

| Sayfa | Adım | Gördüğüm |
|---|---|---|
| 19 | K1 | Başlık, rozetler, kare, "Karede:" satırı (5 sınıf) yerinde; madde 1–4 tam, madde 5 "… ön şarj kartındaki K2" ile biter; altında "İş metni yarım kaldı: devamı sonraki sayfa (K1, adım 17) →"; üst üste binme / kesilme yok |
| 20 | K1 | "← K1 iş metni: önceki sayfa sonunda yarım kalan yer burada sürüyor", sonra "bobini (+; A04) …"; madde 5 sonu, alt kat, 6, 7, 8 tam; parçalar / bağlantı. **Altta ≈ üçte bir boş** (kontrol listesi bölünemeyen blok olduğu için s21'e geçti) |
| 21 | K1 | Kontrol listesi iki sütun, kutular yerinde, maddeler bütün |
| 22 | K1 | Kablo kancası (kablo yolu 1–4, 9–11) ve erişim notu; altı yarı boş |
| 15, 16 | B6a | İş metni 1–4 tam, parça tablosu, kontrol; s16'da kablo kancası ve erişim (sayfa büyük ölçüde boş; eskisiyle aynı yapı). "Karede:" satırı yok (adımda kablo şeması yok) |
| Rastgele (`random.Random(20261115)`): 4, 30, 48, 55, 70 | A3, E2a, F1 (devam), F3, H0b | Okunuyor, kesik / binme yok. 55'te (F3) notlardan sonra ≈ dörtte bir boş; 48'de alt adım kartları 33.6–33.9 sırayla; 55 ve 70'te "Karede:" yerinde |

`kontrol.json` `yazdir.tamlik.sayfa_parca`'ya göre iş metni birden çok sayfaya bölünen tek adım K1; öbür çok sayfalı adımlarda iş metni
ilk sayfada bütün (pypdf ölçümüm de aynı: bölünen paragraf 1).

## 4. Koruyucu denetim (`rehber_uret.py:368-443`, `pdf_tamlik` `:398`; kabul `:483-484`)

İşlev kaynaktan `ast` ile alınıp tek başına çağrıldı (modül koşmadı); PDF bozmaları depo dışındaki kopyalarda.

| Bozma (ajanınkinden farklı) | Sonuç |
|---|---|
| Temiz PDF | geçti, eksik 0 |
| B1: s19'da madde 3'ün **ortasından** "anahtarlı bara (G10, G11; 12 AWG)" silindi (redaksiyon) | **Yakalandı**: K1 `is_` 5233 karakter eksik |
| B2: s21'de bir kontrol maddesinin içinden "BC337-40 #1" silindi | **Yakalandı**: K1 kontrol maddesi 1 eksik |
| B3: veri kopyasında K1 madde 6 ↔ 7 yer değişti (PDF sırası kaynağa ters) | **Yakalandı**: K1 `is_` 1894 eksik |
| B4c: s20 metin akışında "Alt kat …" paragrafı iki kez | Yakalandı (bitişiklik bozuluyor) |
| **B4b: s20'nin başına s19'un son satırı yeniden** (bölme sınırında yineleme; akış içinde) | **Yakalanmadı** (`gecti` true) |
| **B5: kontrol maddesi PDF'te iki kez** | **Yakalanmadı** (`gecti` true) |

Eşikler: `git diff 1328b60` ile `rehber_uret.py`'den silinen tek satır kabul satırı; yeni satır eskisinin bütün koşullarını (`taşan`,
`kucuk_yazi`, `kucuk_ok`, `esleme_tutarli`, sayfa sayıları) aynen tutup `tamlik.gecti`'yi ekliyor. `YAZI_ALT_PT = 8.0`
(`:348`), `yazdir.html` `FS_MIN 8.5`, `GH_MIN 46`, `8.1pt` alt sınırları değişmemiş. **Gevşetilen eşik yok.** PyMuPDF yoksa ya da PDF
yeni değilse `gecti` false (sıkı yönde).

## 5. Kapsam ve tutarlılık

- **Talimat metni bu turda değişmedi:** son yazım saatleri `rehber_metin.py` 03:12, `rehber_deger.py` 03:06,
  `rehber_kritik_onay.json` 03:15, `planlama/adim3/*` en geç 03:14 (`kablolar.md`); hepsi 03:20'den ve kontrol-3'ün bakışından
  (03:22–03:35) önce. Kontrol-3 SHA yazmamış; karşılaştırma saatle.
- **Koşular (çıkış):** `rehber_denetim.py --kaynak` 0; `kablolar_denetim.py` 0 (SONUÇ: GEÇER; depoda, salt okuma; sonra
  `git status` 110 satır, değişmedi); `kablolar_uret.py --kontrol` 0 (güncel); `rehber_kablo.py` 0 (GEÇER); `rehber_denetim.py`
  (veri) 0 (ASCII 0, zorunlu eksik 0 / 98, yasak 0, elektrik 0, parça 1192, şema 49); `rehber_kablo.py --veri` 0 (GEÇER, eşlemesiz
  çizim 0).
- **Veri ↔ kaynak:** `rehber_metin` içe aktarıldı: `COZUM_HATA` boş; `ADIM` ile `rehber-veri.json` arasında `is_`, `kontrol`,
  `kablo`, `erisim`, `baglanti_md`, `alet`, `baslik` alanlarında fark 0 (50 adım); K1 `is_` aynı (10029 karakter, ham metinde 90 yer
  tutucu, hepsi çözülmüş). Veride `{ad.alan}` biçimli yer tutucu 0, `⟦?` 0.
- **`renk_demo KALDI`:** `git show 1328b60:planlama/d158/F10e-dogrula.json`'da da `gecti_ozet.renk_demo: false` var (14.11 15:04):
  **önceki paketten kalan, bu paketin gerilemesi değil.** Genel hüküm: F10a `gecti` true (06:39), F10d true (06:26), F10e true (06:11),
  F10f true (06:01). F10a'daki `veri_degismedi: false` bilgi alanı (`git diff HEAD -- rehber/veri`), `1328b60`'ta da false.
- **`git status --short`:** beklenmeyen dosya yok. Paket: `planlama/adim3/` (4), `planlama/d158/` (7 değişen + 5 yeni ve bu rapor:
  `F10i-gunluk.md`, `F10i-kontrol*.md`, `F10i-yerlesim-say.py`), `planlama/dongu-158.md`, `planlama/rehber/`, `rehber/`,
  `tasarim/freecad/rehber/`. Paket dışı: `tasarim/freecad/kabuk/gorsel/*.png` 13, `tasarim/freecad/montaj/yerlesim-kontrol.json`.
- **Bayat sayılar (yalnız liste):**
  - `README.md:15` "(77 sayfa)": PDF 80 sayfa. Aynı satırdaki 50 adım, 71 alt adım, 1.192 parça güncel.
  - `planlama/rehber/R-gunluk.md:5` "Durum (09.11.2026 16:05, F7a / P7.1 …)" başlığı; günlükteki son PDF sayısı `:174` "PDF 75
    sayfa" (F10h ve F10i turları R-gunluk'a yazılmamış).
  - `rehber/index.html`: sayfa / adım / parça sayısı yok, bayat bir şey bulunmadı.
  - Tarihli kayıtlar (`dongu-158.md:194` "PDF 79 sayfa" 05:03 girdisi, `karar-kuyrugu.md:1401` "PDF 77 sayfa" P10.7b1 girdisi)
    kendi zamanları için doğru; bayat sayılmadı.

## 6. Gizlilik (herkese açık depo)

**Taranan:** `git diff 1328b60` eklenen bütün satırlar + izlenmeyen 5 yeni dosyanın bütün satırları (3304 satır). Kalıplar: yerel
kullanıcı yolu (`C:\Users`, `/Users/`, kullanıcı klasörü adı, `OneDrive`, `AppData`, masaüstü klasörü adı, `Temp`, `file:///`),
makine adı (Windows'un varsayılan bilgisayar adı kalıbı ve bu makinenin adı), takma adlar, e-posta (`@alan.tld`), telefon (`05xx`, `+90`), `parola`, `password`,
`token`, `api key`, `secret`, `sk-`, `ghp_`, `bearer`, `ssh-rsa`, `BEGIN … KEY`. **Bulgu yok.** Tek eşleşme "Echo" (HC-SR04 pin
adı, `kablolar.md` ve günlükte). Kişi adı olarak yalnız "Ahmet" (6) ve "Efe" (6).

**Üst veri:** PDF yazar boş, üretici "HeadlessChrome / Skia/PDF", başlık "Lale Montaj Rehberi: yazdırılabilir": kişisel bilgi yok.
Pakete giren 66 değişen PNG'de (`rehber/goruntu`, `planlama/rehber/goruntu`) metin üst verisi yok; dosya adlarında kişisel bilgi yok.

**Paket dışı, önceden var (bilgi, bu commit'i durdurmaz):** paket dışı 13 `tasarim/freecad/kabuk/gorsel/*.png`'nin PNG metin
üst verisinde (`Title`) yerel kullanıcı yolu var; `1328b60`'taki hâllerinde de var. Depoda izlenen 683 PNG'nin 172'sinde
(`tasarim/freecad/*/gorsel`, FreeCAD dışa aktarımı) ve 3 metin dosyasında (`tasarim/freecad/taslak-170/rapor.html`,
`taslak_rapor.py`, `lale158/ikinci/yavaslik/prof-head-kabuk.txt`) aynı yol zaten yayımlanmış. Bu commit'e o 13 PNG **eklenmemeli**
(paket dışı oldukları için zaten eklenmeyecek). Öneri (ayrı iş): FreeCAD PNG'lerinin `Title` / `Description` alanını temizleyen bir
geçiş ve dışa aktarımda yol yazılmaması; geçmişteki sürümler için karar Ahmet'in.

## 7. Kayıtlı açık işler (montajda zarar yok)

- **A1 · Tamlık denetimi yinelemeyi görmüyor** (`rehber_uret.py:413-418`, `:429-438`): `is_` sayfa sayfa "kalanın en uzun öneki" ile
  eşlendiği için devam sayfasının başında yinelenen metin atlanıyor (B4b); maddeler yalnız "var mı" diye arandığı için iki kez basılan
  madde geçiyor (B5). Bugünkü PDF'te ikisi de yok (bölüm 1). Öneri: devam sayfasında `is_` eşleşmesinin sayfa metnindeki konumundan
  önce, işaret satırı dışında iş metni kalmamalı; madde sayısı adımın kaynak sayısına eşit olmalı.
- **A2 · Tamlık denetimi `kablo`, `erisim`, `baglanti_md`'ye bakmıyor:** bugün eksik 0 (bölüm 1). Öneri: madde listesine ekle.
- **A3 · Kalın / kod parçası ya da boşluksuz uzun sözcük sayfadan uzunsa bölünmez** (`yazdir.html:240-245`): taşar; taşma sayacı ve
  tamlık üretimi düşürür (sessiz değil). Günlükteki "tek paragraf boş bir devam sayfasına sığmasa bile aynı yolla sayfalara akar"
  cümlesi bu durumda geçerli değil. Bugün etkisi yok.
- **A4 · Boş alan:** s20'nin ≈ üçte biri, s55'in ≈ dörtte biri, s16 ve s22'nin yarısından çoğu boş (bölünemeyen iki sütun blokları
  bütün taşınıyor). Okunmayı bozmuyor; kâğıt sayısını artırıyor. Öneri: kontrol listesi madde madde bölünebilir blok olsun.
- **A5 · Bölme yeri cümle ortası:** K1'de "… ön şarj kartındaki K2 | bobini (+; A04)" ("K2 bobini" iki sayfaya ayrılmış). İşaret
  satırları var, anlam korunuyor. Öneri: sığan en uzun baş içinde son cümle sonu (". ") tercih edilsin.
- **A6 · README / R-gunluk sayıları** (bölüm 5).

## 8. Bakılmadı

- Kâğıda basım (görünüş yalnız PyMuPDF görüntüsünden).
- Gerçek başsız Chrome'da `bol()` sınır koşulları (yalnız gerçek kodla sahte sığma modelinde denendi); PDF'in eski ↔ yeni sayfa sayfa
  düzen karşılaştırması (ajanın "düzeni değişen tek adım 17" iddiası ölçülmedi, yalnız bugünkü PDF'in tamlığı ölçüldü).
- `rehber-veri.json`'ın 05:03 hâliyle farkı (ajanın da ölçemediği süre alanları dışı fark).
- `rehber_denetim.py`, `kablolar_*`, `rehber_kablo.py` diff'lerinin bu tur dışındaki (kontrol 1–3'ün baktığı) bölümleri.
- `rehber/goruntu` ve `planlama/rehber/goruntu` karelerinin içerik farkı.
