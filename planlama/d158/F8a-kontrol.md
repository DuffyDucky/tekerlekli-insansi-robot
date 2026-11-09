# F8a kontrolü (ajan B): 158 sipariş paketi (P8.1) — 09.11.2026

Denetlenen: `planlama/d158/F8a-siparis.md`, `F8a-siparis.json`, `F8a-gunluk.md` (A). Denetim listesi: `F8a-brief.md`.
Yöntem: JSON'dan toplamlar ayrı betikle yeniden hesaplandı; `maliyet.json` (git `79fb383`, `c7f9af4`), 17.10 sürümü (`git show b27fd80`),
v4 Excel (`tubitak-2209b/`, yalnız okundu, stdlib zip ile), `proje-plani.md`, `karar-kuyrugu.md` okundu. Satıcı sayfaları 09.11.2026
04:14–04:20 arasında `curl` ile indirildi (49 sayfa + 24 arama), 2 sayfa ayrıca WebFetch ile okundu. Sipariş verilmedi, sepete ürün
eklenmedi, satıcıya yazılmadı, hesap açılmadı. FreeCAD açılmadı. Ara dosyalar oturumun geçici klasöründe; depoya yalnız bu dosya yazıldı.

## Genel karar: **KOŞULLU**

Aritmetik, kalem fiyatları ve `.md` ↔ `.json` uyumu sağlam (aşağıda). Ama paketin **`maliyet.json` kıyası yanıltıcı**: "aynı yöntemle
158 listesi 4.643,42 TL fazla" cümlesi elde kalemleri farklı sayıyor; gerçek fark "alınacaklar" bazında **≈ +29.539 TL**. Ayrıca bir
kritik-yol vidası stokta yetmiyor (M6×16 fosfat: stok 2, gereken 18), erken alımdaki M3 insert için sayfada CAD'e uyan varyant (L 5,7)
yok, akü için planın yedeği (Limacell) sayfası okunduğu hâlde "doğrulanmadı" bırakılmış ve 4 `maliyet.json` önerisi birebir
uygulanamaz durumda. Küçük düzeltmeler aşağıda "Koşullar"da; büyükler A'ya düzeltme turu.

## 1. Madde tablosu

| # | Denetim maddesi | Sonuç | Kanıt |
|---|---|---|---|
| 1 | Fiyat/stok, rastgele 15 satır | **14/15 tutuyor**; 1 stok uyuşmazlığı | §2 tablo. A151 M6×16 fosfat: sayfada "2 adet stokta", A "stokta (adet yok)", gereken 18. S83 stok 9 → 8 (saat farkı, önemsiz) |
| 2 | Fiyat/stok, kritik yol + erken alımın tamamı | **Fiyatların hepsi tutuyor**; 3 eksik | §2 tablo. Eksikler: (a) CNC Marketi sayfalarında stok adedi ve kargo yazıyor (A "adet yok", "sayfada görülmedi"); (b) Rhino3DPrinter M3 insert sayfasında L 5,7 varyantı yok; (c) Limacell sayfası okunmuş ama sonuç yazılmamış |
| 3 | URL arama sayfası mı, başka ürüne mi gidiyor | **Temiz** | JSON'daki 219 satıcı URL'sinin hiçbiri arama sayfası değil. Adı yanıltıcı 3 slug (S13 `022r-11w…`, S92 `usb-hub-3lu…`, S85 `bts7960b-20-amper…`) açıldı: sayfa başlıkları doğru ürün (5.6R 11W 9,98; USB Hub 4lü 187,23; BTS7960B 40 A 265,30). Stok adedinin bir kısmı Robotistan arama sayfasından (A bunu günlükte açıkça yazmış; yöntem olarak kabul) |
| 4 | Aritmetik: toplamlar | **Tutuyor** (kuruşu kuruşuna) | Betikle JSON'dan: doğrulanmış 72.621,24 (86 onaylı 68.455,64 + 8 onaysız 4.165,60); kısmen 1.892,29; doğrulanmamış 4.629,63 (10 satır); parça 79.143,16; hizmet 14.390,00; okul 93.533,16; ×1,15 107.563,13; koşullu dahil ×1,15 112.838,97; kararsız hariç 93.141,88; PAKET A 14.215,11; erken alım 1.515,90 (176 ile 1.558,22) |
| 5 | Adet × birim | **Tutuyor** | 166 kalemde uyumsuz satır 0. F1a 90° HDMI JSON'da `cift: true`, toplama ikinci kez girmiyor (doğru) |
| 6 | `.md` ↔ `.json` | **Tutuyor** | 137 tablo satırı tutar ve adetle karşılaştırıldı: uyumsuz 0. Satıcı toplamları (Robotistan 26 / 33.022,98, Motorobit 34 / 4.881,20, CNC 5 / 3.457,32) yeniden üretildi. Tek eksik: `toplamlar`'da "koşullu dahil ×1,15 = 112.838,97" ve "×1,15 kararsız hariç" yok (md'de var) |
| 7 | `maliyet.json` hâlâ 29.10 mu | **A'nın iddiası doğru**, ifade eksik | `tarih: "2026-10-29"`; Waveshare 10,1" (B) `elde: true` 12.424,50; göğüs ekranı yalnız `ver: v2` satırında. F4a (`79fb383`) yalnız MAX98357A'yı V3'ten çıkardı, 11 `fiyat_bekliyor` ekledi, iki notu güncelledi ("göğüs ekranı … P8.1'de girecek"). A F4a sonrası sayıları (102.919,71; 11 aday) kullanmış, köprüde MAX98357A'yı ikinci kez düşmemiş: doğru. Ama "hâlâ 29.10 listesi" yerine "29.10 listesi + F4a'nın 09.11 kısmi eklemeleri" denmeli |
| 8 | Köprü kalemleri kaynaklı mı | **Kalemler kaynaklı; köprü tablosunda 3 satır hatalı, sonuç cümlesi yanlış** | +16.585,74 (9.367,79 + 7.217,95), +3.187,50 (5 × (1.809 − 1.171,50); `maliyet.json` 4 + 1 yedek × 1.171,50), −21.648,48 (7.031,58 + 2.192,40 + 12.424,50, üçü `elde: true`) doğru. Hatalar: (i) md:471 "−6.843,09 + 11.550,00" yazıyor ama ara toplama yalnız −6.843,09 giriyor; (ii) md:472 "lazer + bükme 0" yazıyor ama 56.723,83'e varmak için −2.840,00 düşülüyor (102.919,71 − 13.424,31 − 21.648,48 − 1.440 − 6.843,09 = 59.563,83; −2.840 = 56.723,83); (iii) md:475 "toplam dışı" md:469 ile çelişiyor (`maliyet.json` elde kalemleri genel toplama katıyor). "Diğer +425,43" kalıntı (geri hesap), kalem kalem kaynak yok: öyle etiketlenmeli |
| 9 | "%15 payla fark 4.643,42" | **Yanlış/yanıltıcı** | 107.563,13 elde kalemsiz, 102.919,71 elde kalemli (+ kargo). Aynı esasla: `maliyet.json` "elimizdekiler düşülmüş" 78.023,96 (`F4a-gunluk.md:74`; README ≈ 78.000) → 158 **+29.539,17**; elde dahil (Pi 7.071,58 + microSD 995, bugünkü fiyat) (93.533,16 + 8.066,58) × 1,15 = 116.839,70 → **+13.919,99**. Ayrıca md:24 "Aynı tutar" bir üst satırı (93.141,88) gösteriyor, değer 93.533,16'dan |
| 10 | Hocadaki liste belirsizliği | **Doğru tespit** | `siparis-farki-2026-10-29.md` 17.10 Excel = `b27fd80` diyor; `tubitak-2209b/BAGLAM.md:222` "… listeyi beğendi (04.11)", `malzeme-listesi/rapor.md:4` "Liste gönderilmedi". Çelişki doğru raporlanmış, karar Ahmet'e bırakılmış |
| 11 | Fark sayıları 44/10/37 ve 8/1/1/0 | **Tutuyor** (örnekleme) | Eklenen tablo satırları 1+3+2+2+2+1+1+3+1+2+5+1+6+13+1 = 44 (15 grup); çıkan 10 (8 grup); değişen tablo 37 satır. `b27fd80`'de örnek: DS3218MG 4 × 964,50, Waveshare 7" 2.790,25, Pi 5 8 GB, şarj UserPil 1.661,40, D36V50F5 1.975,38, sigma 3 × 908,33, T-somun 50, bükme 10, plaka 270 × 500, vida 198/70/56/20/32, insert 125/12, XL4016 3, servo uzatma 14, hat yuvası 3, bıçak 5, TVS 2 tahmin, 18 AWG 10, pertinaks 4, gamepad var, perçin somun `kosullu` (A "koşullu satırdı" dedi: doğru). v4 Excel: "SİTELER TOPLAMI 81 / 68.219,82" ve satır 28 90° HDMI var; 2.2'deki +491,34 = 391,28 + 100,06 |
| 12 | Karara bağlı kalemler | **Maliyetler doğru, seçenekler kuyrukla aynı; 1 iddia düzeltilmeli** | K9 b pay ≥ 1: 3 × 980 − 3 × 202,50 = 2.332,50 (Robocombo DS3218 stok 4); ikinci 3 × 1.315,80 − 607,50 = 3.339,90; DS5160 5 × 2.448 − 9.045 = 3.195,00; dirsek DS3235 3 × 1.809 − 607,50 = 4.819,50. K1 a/b/c, K4 a/b/c, K10 a/b/c, K11 a/b, K12 a/b `karar-kuyrugu.md` ile aynı. **K9 b pay ≥ 2 "onaylı sitede yeterli servo yok" kısmen yanlış:** Motorobit'te RDS5180 80 kg (2.876,40) ve RDS51150 150 kg (3.672,00) var ama **tükendi**; Robocombo'da DSSERVO DES220 **24 V** 220 kg 15.075,00 (indirimli 14.773,50) **stok 5** var (24 V servo hattı gerektirir, 5 adet ≈ 75.000 TL). Doğru ifade: "6–8,4 V'ta stoklu ≥ 62,4 kg·cm servo yok" |
| 13 | Varsayılan karar gibi yazılmış yer | **Biri var (küçük)** | Başlık "Okul bütçesi 93.533,16" K4'ü (açık karar) toplama katıyor; K4 a'nın `maliyet.json` anlamı "koşullu = genel toplam dışı". §6'da "a: koşullu kalem +391,28" bu yüzden çelişkili. "Kararsız hariç 93.141,88" verilmiş (brief'in istediği), ama başlık "K4 dahil" diye etiketlenmeli. K9/K10/K11/K12 varsayılanları "öneri" olarak yazılmış: doğru |
| 14 | Takvim riskleri | **Yönü doğru, iki eksik** | Akü: sayfada "Ürün Stok : 1" + "7 gün içinde … özel sipariş" (genel ibare; stoktaki adet için de geçerli mi belli değil, A ihtiyatlı okumuş: kabul). `proje-plani.md:44` 2b = 1 (1–2) hf ve yedeği Limacell "özel üretim, ort. 3 iş günü": A bunu kaçırmış (sayfa 03:50'de okunmuş, sonuç yok). Bugün Limacell 12 V 24 Ah 4.814,86 TL, InStock, "ortalama hazırlanma süresi 3 iş günü". Nicelik: S = 16.11'de sipariş → varış ≈ 24–28.11 (7 gün + koli 1–5 gün); taban (aşama 5) S+1 → S+2, akü adım 9'da: sınırda. QLED stok 2 doğru (arama `quantity` 2; liste fiyatı 8.124,85, indirim bitince +906,90). Kamera kritik yolda değil (`proje-plani.md:138`): doğru. **Not:** WebFetch Robotistan QLED sayfasını "Tükendi" okudu; JSON-LD `InStock` ve arama adedi 2 (A'nın §1.4'teki gizli blok uyarısı doğru) |
| 15 | Akü/QLED önerisi karar mı | **Öneri olarak çerçevelenmiş** | Günlük §6 KT3/KT4 "Öneri", "karar Ahmet'in"; md:172 "2b dalı en geç S'de başlamalı" plan çıkarımı. Panoya karar yazılmamış. Eksik: KT2 "insert adedi P4.3 BOM'uyla netleşince al" erken alımı geciktirebilir; plan durum A için erken alımı bu hafta istiyor (`proje-plani.md:71, 119`) |
| 16 | `maliyet.json` 20 öneri | **13 onay, 3 koşullu, 4 ret** | §4 |
| 17 | Kurallar | **Temiz** | `git status`: F8a'dan yalnız 3 yeni `F8a-*` dosyası; `maliyet.json`, `karar-kuyrugu.md`, `proje-plani.md` değişmemiş. Brief'ten (03:32) sonra değişen dosyalar: `F8a-*`, `F2-gunluk.md` (F2), `dongu-158.md` (orkestratör). `tubitak-2209b/` dosyalarının değişiklik zamanı 03–04.11. Günlükte ve URL'lerde sepet/giriş/ödeme izi yok (tek eşleşme ürün adı "…-mikrofon-girisi"). Takma ad yok; başka öğrenci/danışman adı ya da soyadı yok ("hocanın öğrencisi" denmiş). Yalnız ekip üyesi ön adı "Efe" bir kez |

## 2. Fiyat örnekleme tablosu (kontrol: 09.11.2026, 04:14–04:20)

"A" sütunu `F8a-siparis.json` birincil fiyat/stok. KDV dahil. ✓ = aynı.

### 2.1 Rastgele 15 satır (havuz: 79 "doğrulandı" satırı, kritikler hariç; tohum 20261109)

| Satır | Kalem | A'nın değeri | Benim bulduğum | URL | Sonuç |
|---|---|---|---|---|---|
| S35 | Mini sigorta 2 A | 7,34 · stok 381 | 7,34 · stok 381 | https://www.motorobit.com/2a-mikro-oto-sigorta-bicak-sigorta | ✓ |
| S15 | P6KE6V8A | 6,05 · stok 1210 | 6,05 · InStock | https://www.direnc.net/p6ke6v8a | ✓ (adet aramadan, bakılmadı) |
| S82 | Kart burcu M3×8 | 1,83 · stok 2457 | 1,83 · stok 2457 | https://www.robotistan.com/8mm-m3-disidisi-plastik-aralayici | ✓ |
| S49 | XT60E-M panel | 61,20 · stok 960 | 61,20 · stok 960 | https://www.motorobit.com/xt60e-m-panel-tipi-erkek-konnektor-xt60 | ✓ |
| S29 | Wago 2273-203 ×10 | 12,24 · stok 18 | 12,24 · stok 18 | https://www.motorobit.com/2273-203-3-pin-buat-klemensi | ✓ |
| S71 | Ana sigorta yuvası | 48,18 · stok 41 | 48,18 · stok 41 | https://www.robotistan.com/kablolu-bicak-sigorta-yuvasi-standart-boy | ✓ |
| S62 | 12 AWG kırmızı | 118,00 · stok 386 | 118,00 · stok 386 | https://robocombo.com/12awg-kirmizi-silikon-kablo-1m | ✓ |
| A151 | M6×16 fosfat ×18 | 3,60 · stokta (adet yok) | 3,60 · **2 adet stokta** (WebFetch ile de) | https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata | **✗ stok yetmez** |
| S10 | Kablo bağı 100'lü | 27,95 · stokta | 27,95 · InStock | https://www.direnc.net/25mm-x-100mm-kablo-bagi-100-adet-siyah | ✓ |
| S79 | Micro HDMI plug | 247,61 · stok 92 | 247,61 · stok 92 | https://www.robotistan.com/micro-hdmi-plug-diy-hdmi-kablo-ile-birlikte-kullanilabilir | ✓ |
| S24 | 1N4007 | 0,61 · stok 23592 | 0,61 · stok 23592 | https://www.motorobit.com/1n4007-1000v-1a-diyot | ✓ |
| S38 | Mini sigorta 10 A | 7,34 · stok 913 | 7,34 · stok 913 | https://www.motorobit.com/10a-mikro-oto-sigorta-bicak-sigorta | ✓ |
| S83 | ReSpeaker Mic Array v2.0 | 6.680,04 · stok 9 | 6.680,04 · stok 8 | https://www.robotistan.com/respeaker-mic-array-v20 | ✓ (stok −1) |
| S39 | Röle K1 MAH-112 | 183,60 · stok 94 | 183,60 · stok 94 | https://www.motorobit.com/mah-112-c-4-12v-30/40a-otomotiv-rolesi-5-pin | ✓ |
| K4a | USB-A uzatma 30 cm | 77,46 · stok 26 | 77,46 · stok 26 | https://www.robotistan.com/usb-erkek-disi-donusturucu-30cm | ✓ |

### 2.2 Kritik yol ve erken alım (tamamı)

| Satır | Kalem | A'nın değeri | Benim bulduğum | URL | Sonuç |
|---|---|---|---|---|---|
| S5 | Akü Victron 20 Ah | 12.680,70 · stok 1 · 7 gün | 12.680,70 (liste 12.798,66) · "Ürün Stok : 1" · 7 gün ibaresi var | https://atakale.com/index.php?product_id=438&route=product%2Fproduct | ✓ |
| — | Akü yedeği Limacell 24 Ah | "bugün okunmadı/doğrulanmadı", 4.746,02 | **4.814,86** · InStock · özel üretim ort. 3 iş günü · 3.000 TL üzeri kargo ücretsiz | https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya | **✗ eksik** (sayfa A'nın listesinde, sonuç yok) |
| S9 | JGB37-520 60 dev/dk ×4 | 665,41 · stok 25 | 665,41 · InStock | https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor | ✓ |
| S84 | Motor tutucu (2 paket) | 764,79 · stok 5 | 764,79 · stok 5 | https://www.robotistan.com/aluminyum-l-tipi-37d-motor-tutucu | ✓ |
| S84 (2.) | Motorobit 37 mm | 107,10 · tükendi | 107,10 · OutOfStock | https://www.motorobit.com/37-mm-motor-tutucu | ✓ |
| S20 | Altıgen kaplin ×4 | 122,40 · stok 384 | 122,40 · stok 384 | https://www.motorobit.com/6mm-motor-safti-ile-uyumlu-hex-tekerlek-kaplini | ✓ |
| S72 | Arazi tekerleği ×4 | 362,27 · stok 7 | 362,27 · stok 7 | https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi | ✓ |
| A162 | Sigma 40×40 ağır ×3 m | 934,08 · stokta (adet yok) | 934,08 (liste 1.514,70) · "120,9 adet [m] stokta" · kargo 132 TL, 2.400 TL üzeri ücretsiz | https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip | ✓ fiyat; stok/kargo eksik yazılmış |
| A163 | T-somun M6 ×62 | 3,90 · stokta (adet yok) | 3,90 · 36.790 adet stokta | https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu-m6 | ✓ |
| S91 | T-somun M5 ×8 (CNC) | 3,96 · stokta (adet yok) | 3,96 · 42.761 adet stokta | https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu10-kanal-profil-tirtilli-somunu | ✓ |
| S91 (v4) | Robotistan M5 T-somun | 37,20 · tükendi | 37,20 · OutOfStock | https://www.robotistan.com/40-serisi-m5-t-somun | ✓ |
| A134 | Gizli köşe ×8 | 39,60 · stokta | 39,60 · 989 adet stokta | https://www.cnc-marketi.com/urun/45x45-gizli-kose-baglanti-90-k10 | ✓ |
| A133 | Geniş köşe ×4 | CNC 25,38 tükendi; Otomasyoncu 31,36 | CNC 25,38 "Stokta yok"; Otomasyoncu 31,36 KDV dahil (stok yazmıyor) | https://www.otomasyoncu.net/urun/40x40-kose-baglanti-genis | ✓ |
| S76 | QLED 10,1" | 7.217,95 · stok 2 | 7.217,95 (liste 8.124,85) · arama adedi 2 · JSON-LD InStock | https://www.robotistan.com/101-inc-qled-ekran-modulu | ✓ |
| S76 (2.) | Motorobit QLED | 15.300,00 · stok 10 | 15.300,00 · stok 10 | https://www.motorobit.com/waveshare-101-1280720-qled-kapasitif-dokunmatik-hdmi-ekran | ✓ |
| S74 | Göğüs 11,6" | 9.367,79 · stok 10 | 9.367,79 (liste 10.766,86) · arama adedi 10 | https://www.robotistan.com/116-inc-lcd-ekran-modulu | ✓ |
| S74 (2.) | Direnc 11,6" | 12.695,09 · stok 4 | 12.695,09 · InStock | https://www.direnc.net/116inch-hdmi-lcd-ekran-raspberry-pi-uyumlu-1920x1080-ips-teknik-ozellikleri | ✓ |
| S60 | DS3235 ×5 | 1.809,00 · stok 85 | 1.809,00 (liste 1.930) · stok 85 (SKU 2507311001) | https://robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4534 | ✓ |
| A159 | 6808-2RS ×4 | 108,16 · stok 51 | 108,16 · stok 51 | https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman | ✓ |
| A158 | 625ZZ ×5 | 30,04 · stok 8398 · BGR | 30,04 · stok 8398 · "625 ZZ BGR 5x16x5 (Karbon)" | https://www.rulmanal.com.tr/urun/625-zz-kwc-5-16-5-rulman | ✓ |
| A135 | Insert M3 ×168/176 | 5,29 taban; "Ø4,0 × 5,7 varyantının fiyatı ayrı doğrulanmadı" | 5,29 taban · varyantlar: ID3 OD4 L4; ID3 OD5 L4/5/6/7/8 — **L 5,7 yok** · kargo 139 TL, 2.500 TL üzeri ücretsiz | https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3 | **fiyat ✓, ürün uyumu ✗** |
| A136 | Insert M5 ×6 | 6,35 taban | 6,35 taban · varyantlar ID5 OD7 L4/6/7/8/10 (CAD L 7,5) | https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5 | ✓ (varyant seçilmeli) |
| A142 | M3×20 DIN 912 (kupon D) | 1,30 | `salePrice` 1,296 (KDV %20 dahil) · "Stoktan teslim 15:00'e kadar aynı gün kargo" | https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912 | ✓ (kargo ibaresi A'da "yok") |
| A127 | Pul M3 (kupon D) | 0,40 | 0,396 | https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125 | ✓ |
| A131 | DIN 985 M3 (kupon D) | 1,02 | 1,02 | https://www.paslanmazcivata.ist/urun/paslanmaz-fiberli-somun-cesitleri-din985 | ✓ |

### 2.3 K9 için ek bakılanlar

| Kalem | Değer | URL |
|---|---|---|
| DS3218 20 kg (K9 b pay ≥ 1) | 980,00 (liste 1.010,50) · stok 4: A ile aynı | https://www.robocombo.com/dsservo-ds3218-20kg-servo-motor-180-derece-su--4151 |
| DS5160 60 kg | 2.448,00 · stok 6: A ile aynı | https://www.motorobit.com/ds5160-hv-60kg-dijital-servo-motor |
| RDS5180 80 kg | 2.876,40 · **tükendi** | https://www.motorobit.com/rds5180-80kg-dijital-servo-motor-180-u-servo-braket-dahil |
| RDS51150 150 kg | 3.672,00 · **tükendi** | https://www.motorobit.com/rds51150-150kg-dijital-servo-motor-180-u-servo-braket-dahil |
| DSSERVO DES220 24 V 220 kg | 15.075,00 (indirimli 14.773,50) · stok 5 (DS3235 sayfasının ürün verisinde) | https://robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4534 |

## 3. Koşullar

### 3.1 Birebir düzeltmeler (kayıt ya da A uygular; ≤ 2 satır)

1. `F8a-siparis.md:24`
   eski: `| Aynı tutar `maliyet.json` gibi %15 payla | 107.563,13 TL (`maliyet.json` 102.919,71 → fark 4.643,42) |`
   yeni: `| Okul bütçesi (93.533,16) × 1,15 | 107.563,13 TL; kararsız hariç × 1,15: 107.113,16. Kıyas: `maliyet.json` elimizdekiler düşülmüş 78.023,96 → +29.539,17 (§7) |`
2. `F8a-siparis.md:471`
   eski: `| − filament + baskı hizmeti | −6.843,09 + 11.550,00 | 03.11: filament firma/ekipten; baskı anlaşmalı firma (tahmini) |`
   yeni: `| − filament | −6.843,09 | 03.11: filament firma/ekipten; baskı hizmeti aşağıda hizmetlerle eklenir |`
3. `F8a-siparis.md:472`
   eski: `| lazer + bükme hizmeti | 0 | İkisinde de 2.840,00 |`
   yeni: `| − lazer + bükme hizmeti | −2.840,00 | İkisinde de 2.840,00; aşağıda hizmetlerle geri eklenir |`
4. `F8a-siparis.md:475`
   eski: `(29.10'da Waveshare 10,1" 'elde', toplam dışı)`
   yeni: `(29.10'da Waveshare 10,1" 'elde'; yukarıda elde kalemlerle düşüldü)`
5. `F8a-siparis.md:484` satır sonuna ekle: `Kalıntı: köprü toplamından geri hesaplandı, kalem kalem ayrıştırılmadı.`
6. `F8a-siparis.md:489` ikinci cümle
   eski: `Elde kalemler, pay ve kargo çıkınca fark tersine dönüyor. Aynı yöntemle (pay dahil) 158 listesi `maliyet.json`'dan 4.643,42 TL fazla.`
   yeni: `Aynı esasla (pay dahil, kargo hariç): alınacaklar 107.563,13 ↔ `maliyet.json` elimizdekiler düşülmüş 78.023,96 → +29.539,17; elde dahil 116.839,70 ↔ 102.919,71 → +13.919,99.`
7. `F8a-siparis.md:360` (A151): `· 3,60 · stokta (adet yok)` → `· 3,60 · stok 2 (gereken 18)`; durum sütununa ` · Stok yetmez: ikinci satıcı gerekli`. JSON `A151.birincil.stok_adet` → `2`.
8. `F8a-siparis.md:434` (K9 b pay ≥ 2, not sütunu) sonuna ekle: `Motorobit RDS5180 80 kg 2.876,40 ve RDS51150 150 kg 3.672,00 tükendi; Robocombo DES220 220 kg 24 V 15.075,00 stok 5 (24 V hat gerekir).` Aynı düzeltme `F8a-gunluk.md:618` "onaylı sitede yeterli servo yok" → "6–8,4 V'ta stoklu yeterli servo yok (80/150 kg tükendi; 220 kg yalnız 24 V)".
9. `F8a-gunluk.md:586` (öneri 2)
   eski: `F1b göğüs ekranı kablosu olduğu için `elektronik` (90° DC jak ile aynı grup) olmalı.`
   yeni: `F1b göğüs ekranı kablosu olduğu için `elektronik` (USB-A uzatma satırlarıyla aynı grup; 90° DC jak `guc`ta kalır) olmalı.`
10. `F8a-gunluk.md:571` (Victron ikinci satıcı)
    eski: `06-aku-secimi.md: Limacell 24 Ah (gecersunenerji) 4.746,02 bugün okunmadı/doğrulanmadı`
    yeni: `Plan yedeği Limacell 12 V 24 Ah (gecersunenerji, onaylı değil) 09.11: 4.814,86, InStock, özel üretim ort. 3 iş günü; ölçü/kütle CAD yuvasıyla kontrol edilmedi`
11. `F8a-siparis.md:180` ve `:344` notu: `Ø4,0 × 5,7 varyantının fiyatı ayrı doğrulanmadı` → `Sayfada L 5,7 varyantı yok (ID3 OD4 L4; ID3 OD5 L4–8); CAD deliği Ø4,0 / L 5,7 ile uyum doğrulanmadı`.
12. `F8a-siparis.md:21` başlık satırı: `**Okul bütçesi (parça + hizmet), doğrulanmamış dahil**` → `**Okul bütçesi (parça + hizmet), doğrulanmamış ve K4 dahil**`.

### 3.2 A'ya düzeltme turu (büyük)

- **D1 · Kargo ve stok adetleri:** CNC Marketi (5 satır; sayfada "N adet stokta", kargo 132 TL, eşik 2.400 → sipariş 3.457,32 eşiği geçiyor), Rhino3DPrinter (kargo 139 TL, eşik 2.500 → erken alımda ve siparişte eşik altı, +139), paslanmazcivata.ist ("15:00'e kadar aynı gün kargo") için §3 ve §8 tablolarını sayfadaki değerlerle doldur; JSON `satici_toplamlari` aynı. Rulmanal ve Otomasyoncu kargosunu da oku.
- **D2 · M6×16 fosfat (A151):** stok 2 < 18. Onaylı ve onaylı olmayan satıcılarda ikinci kaynak bul (ör. paslanmaz DIN 912 M6×16 paslanmazcivata.ist M6 sayfası; fosfat şartının kaynağını yaz). Sigma/T-somun siparişiyle aynı gün gelmesi taban (aşama 5) için gerekli.
- **D3 · Erken alım insertleri:** Rhino M3 sayfasında CAD'in L 5,7 insert'i yok; tolerans kuponu delikleri Ø3,8–4,1 (`tasarim/freecad/test/tolerans_kuponu.py:8`). Hangi varyantın (OD 4 / OD 5, L 5–6) ya da hangi başka satıcının (ruthex M3×5,7) bu deliğe uyduğunu kaynakla göster; uymuyorsa Ahmet'e iki seçenek yaz (varyant + kupon deliği güncellemesi / başka satıcı). Kuponun amacı geçme denemesi olduğu için yanlış insert erken alımı boşa çıkarır. KT2'deki "P4.3 BOM'uyla netleşince al" önerisini plan takvimiyle (`proje-plani.md:71, 119`: erken alım bu hafta) çelişmeyecek biçimde yeniden yaz (ör. 168 al, fark P4.3'te).
- **D4 · Akü takvimi:** Limacell'i ikinci seçenek olarak §3 ve S5 satırına ekle (onaylı değil, 24 Ah, ölçü kontrolü gerekli). "S'de sipariş → varış ≈ 24–28.11; taban adım 9 ≈ S+1,5 hf" nicel karşılaştırmasını yaz; akünün erken alımla birlikte alınması seçeneğini (stok 1) Ahmet'e karar taslağı olarak koy.
- **D5 · `maliyet.json` önerileri 12, 13, 18 ve 1:** birebir uygulanabilir hâle getir (§4).

## 4. `maliyet.json` önerileri (günlük §5)

| # | Öneri | Karar | Gerekçe / koşul |
|---|---|---|---|
| 1 | 9 `fiyat_bekliyor` satırına fiyat | **Koşullu onay** | Fiyatlar doğru. Kayıt ajanı için satır satır hedef yazılmalı: PAM8403 ve USB ses kartı → `secenek` kaldırılır (`maliyet.json` notu: "kararlıdır (K16) … genel toplama girer"); K4a/b/d/e → `secenek: kosullu`; F1b 3 fiş → `secenek: kosullu` ya da kesin (Ahmet; 90° HDMI v4'te zaten kesin). F1b micro USB satırına "adaptör değil, 90° kablo; boy sayfada yok" notu |
| 2 | 90° HDMI / micro USB `g: ses` → `elektronik` | **Onay, parantez düzeltilerek** | Kaynak doğru (`maliyet.json` iki satır `g: ses`); 90° DC jak `guc` (Koşul 9) |
| 3 | DS3235 1.171,50 → 1.809,00 (+ yedek) | Onay | Sayfa 1.809 (liste 1.930), stok 85. `not`'a "indirimli fiyat" yazılsın |
| 4 | MG996R 199 → 202,50 | Onay | Robocombo 202,50 (liste 211,50), stok 393 |
| 5 | XVF3800 → ReSpeaker v2.0 6.680,04 | Onay | Sayfa doğru; kaynak K17 (05.11 R1) + v4 |
| 6 | D36V50F5 → D24V50F5 2.266,93 | Onay | v4 kararı; fiyat A'dan (benim örneklememde yok) |
| 7 | 11,6" + 12 V regülatör + HDMI 1,5 m ekle | Onay | 9.367,79 sayfada doğru; F4a notu "P8.1'de girecek" |
| 8 | Waveshare 10,1" elde → QLED 7.217,95 | **Koşullu** | README ve `maliyet.json` notu hâlâ "yüz ekranı hocadan gelirse" diyor; v4 QLED'i satın alma satırı yapıyor. Ahmet teyidi olmadan `elde` işareti değişmesin. "Genel toplamı değiştirmez" cümlesi yanlış: fiyat değişimiyle genel ara −5.206,55 değişir |
| 9 | Kafa satırları (SY8205, micro USB 30 cm, hub, HDMI şerit seti) | Onay | Fiyatlar sayfada (S79 247,61 doğrulandı); PAM/ses kartı öneri 1 ile çift yazılmasın |
| 10 | Filament → baskı hizmeti 7,7 kg × 1.500 | **Ret (kayıt ajanı uygulamaz)** | Tahmini fiyatı fiyatlı satır yapar; A da "Ahmet kararı" demiş. Karar listesinde |
| 11 | Gamepad ve perçin aleti çıkar | Onay | `BAGLAM.md:222` "oyun kolu olmayacak perçine pensesini de biz ayarlarız onları düş" (03.11) |
| 12 | Kargo satırı yeniden | **Ret (birebir değil)** | "Ayrı tahmin" sayı vermiyor. D1 sonrası satıcı başına tutar yazılsın (CNC 0, Rhino 139, …) |
| 13 | Insert M3 adet + 5,22 → 5,29, M5 6,27 → 6,35 | **Ret (fiyat kısmı)** | Taban fiyat; CAD varyantı sayfada yok (D3). `durum: dogrulandi` yapılmasın; yalnız `not`'a "09.11 taban 5,29 / 6,35, varyant doğrulanmadı" eklenebilir. Adet P4.3'te |
| 14 | Rulman fiyatları + 625ZZ model 'BGR (Karbon)' | Onay | 108,16 / 30,04, stok 51 / 8398, sayfa adı doğrulandı |
| 15 | T-somun M5 3,96, M6 3,90, adet 62 | Onay | CNC sayfaları; stok 42.761 / 36.790 |
| 16 | Geniş köşe: CNC tükendi, Otomasyoncu ikinci | Onay, açık yazılarak | Birincil CNC `stok: "yok"` + `alt` Otomasyoncu 31,36 mı, yoksa birincil Otomasyoncu mu: A belirtsin (F8a tutarı Otomasyoncu'yla) |
| 17 | Akü notu (7 gün, stok 1) | Onay + ek | `alt`: Limacell 4.814,86 (09.11, onaylı değil, 24 Ah, ölçü kontrolü) |
| 18 | "~40 satır" satıcı/model aktarımı | **Ret (birebir değil)** | Liste yok; kayıt ajanı `maliyet.json` satırı ↔ F8a id eşlemesi olmadan uygulayamaz, "kısmen"/v4 yaklaşık fiyatları da taşıyabilir. A eşleme tablosu versin (D5) |
| 19 | Adet değişenler | Onay | §2.1 sayıları `b27fd80` ve v4 ile örneklemede tuttu |
| 20 | `tarih` → 09.11 | **Koşullu** | En son uygulanır; biçim `"2026-11-09"` (ISO, mevcut alan gibi); "kısmen" ve "doğrulanmadı" satırları `dogrulandi` yapılmaz; 1,58 m geçişi tamamlanmadıysa `notlar[0]`'da "kısmen" kalır |

Özet: onay 1 (koşullu), 2, 3, 4, 5, 6, 7, 9, 11, 14, 15, 16, 17, 19 · koşullu 8, 20 · ret 10, 12, 13 (fiyat), 18.

## 5. Ahmet'e gidecek kararlar

1. **Hocadaki liste:** 17.10 Excel mi, 03.11 v4 mü (`BAGLAM.md:222` "beğendi" ↔ `rapor.md:4` "gönderilmedi"). Fark tablosu buna göre iletilir.
2. **Bütçe farkı:** 158 alınacaklar (pay dahil, kargo hariç) ≈ 107.563 TL; README'deki ≈ 78.000 TL'den ≈ +29.539 TL. Hocaya bildirilecek mi?
3. **Erken alım (1.515,90 TL + Rhino kargosu 139):** bu hafta mı; satıcılar onaylı değil (okul siparişi mi kişisel mi); M3 insert varyantı (D3 sonucu).
4. **Akü:** Atakale stok 1, "7 gün" ibaresi. S'de mi, erken alımla mı; biterse Limacell 24 Ah (4.814,86, 3 iş günü, ölçü kontrolü).
5. **Kafa ekranı:** hocadan mı gelecek, alınacak mı (README ↔ v4). Alınacaksa QLED stok 2, indirimli 7.217,95 (liste 8.124,85; Motorobit 15.300): erken mi, S'de mi.
6. **K4** (6 kablo, +391,28; 2 kalem onaylı sitede yok).
7. **K9** el yükü: a (0 TL, varsayılan) / b pay ≥ 1 (+2.332,50, DS3218 stok 4) / b pay ≥ 2 (6–8,4 V'ta stoklu servo yok).
8. **K1, K10, K11, K12:** etkileri 0–76 TL (bütçe açısından önemsiz; tasarım kararı).
9. **K2 / AI HAT+:** PAKET A'da (6.978,88); TÜBİTAK desteği gelmezse okul bütçesine mi.
10. **3B baskı hizmeti 11.550 TL (tahmini):** anlaşmalı firma ücretli mi; teklif alınacak mı.
11. **M6×16 fosfat:** 18 gerekiyor, CNC'de 2 var: başka satıcı ya da paslanmaz muadil (D2 sonucuyla).
12. **Onaylı olmayan satıcılar** (CNC Marketi, Rulmanal, Rhino3DPrinter, paslanmazcivata.ist, Otomasyoncu; 6.057,89 TL): hocanın öğrencisine URL'siz (a) grubu olarak mı gidecek.

---

## Yeniden kontrol (tur 1) — 09.11.2026, 04:41–04:50

Denetlenen: A'nın yeniden ürettiği `F8a-siparis.md` / `.json` / `F8a-gunluk.md` (04:38–04:40). Toplamlar JSON'dan aynı betikle yeniden
hesaplandı; 6 sayfa 04:41'de `curl` ile yeniden indirildi; öneri 18 eşleme tablosu `maliyet.json` (`c7f9af4`) satır satır karşılaştırıldı.
Sipariş, sepet, giriş, satıcıya yazma yok; FreeCAD yok. `git status`: tur 1'de değişen yalnız 3 `F8a-*` dosyası (+ orkestratörün
`dongu-158.md`'si); `maliyet.json`, `karar-kuyrugu.md`, `proje-plani.md`, `tubitak-2209b/` değişmemiş.

### Karar: **KOŞULLU** (yalnız aşağıdaki 6 birebir düzeltme; yeni A turu gerekmez)

İlk turun 12 küçük koşulu ve D1–D4 kapandı. D5 (`maliyet.json` önerileri) büyük ölçüde kapandı; öneri 18'in satır numarası (idx)
kayması ve `model` alanı, öneri 1'in varsayılanı ve aynı adlı V1/V2–V3 satırları birebir düzeltmeyle kapanır.

### Koşulların durumu

| Koşul | Durum | Kanıt |
|---|---|---|
| 3.1/1 md kıyas satırı | ✓ | `F8a-siparis.md:25` |
| 3.1/2–3 köprü filament / lazer | ✓ | §7: 102.919,71 − 13.424,31 − 21.648,48 − 1.440 − 6.843,09 − 2.840 = 56.723,83 (yeniden hesaplandı) |
| 3.1/4 "yukarıda elde kalemlerle düşüldü" | ✓ | §7 köprü |
| 3.1/5 "Diğer" kalıntı | ✓ | +430,65 (= 425,43 + 5,22); köprü toplamı 79.148,38 tutuyor |
| 3.1/6 sonuç cümlesi | ✓ | +29.545,18 / +13.925,99 (yeniden hesaplandı) |
| 3.1/7 A151 stok 2 | ✓ | md:392; JSON `A151.birincil.stok_adet = 2`, `kullanilan: ikinci`, `durum: kismen_dogrulandi` |
| 3.1/8 K9 b pay ≥ 2 | ✓ | md:466, md:576, günlük:722 |
| 3.1/9 öneri 2 parantez | ✓ | günlük:616 |
| 3.1/10 Limacell | ✓ | günlük:600 |
| 3.1/11 insert notu | ✓ | md:197, 207, 376 |
| 3.1/12 başlık "K4 dahil" | ✓ | md:22 |
| D1 kargo/stok | ✓ | §3 ve §8 (CNC 132 TL / 2.400, Rhino 139 / 2.500, paslanmazcivata 2.000, Rulmanal 2.500); onaylı olmayan toplam 3.392,52 + 993,17 + 969,14 + 582,84 + 125,44 = 6.063,11 (yeniden hesaplandı; md:581 ile aynı) |
| D2 M6×16 | ✓, bir not eksik | Paslanmaz A2 3,89 sayfada doğru; öneri (md:580) dayanım sınıfı farkından söz etmiyor (Düzeltme T1-5) |
| D3 insert | ✓, M5 kısmı §9'a girmemiş | §4.1 A/B/C; Rhino kuralı ("dış çapından 0,1–0,2 mm dar delik") sayfada doğrulandı. M5 kupon delikleri (Ø6,2–6,6) OD 7 için dar: md:221'de var, §9/3'te (md:572) yok (Düzeltme T1-6) |
| D4 akü | ✓ | §3.1; Limacell sayfası doğrulandı (aşağıda) |
| D5 öneriler | Kısmen | Öneri 18 eşleme doğru, uygulama sırası ve `model` eksik; öneri 1 seçimi açık; öneri 11 silme idx kaydırır (Düzeltme T1-1…T1-4) |
| JSON `toplamlar` yeni alanlar | ✓ | `kararsiz_haric_pay15`, `kosullu_dahil_pay15`, `fark_alinacaklar`, `fark_elde_dahil`, `elde_dahil_pay15`, `maliyet_elde_dusulmus` |
| Karar listesi 14 madde, öneri dilinde | ✓ | md §9; panoya yazılmamış |

### Toplamlar (JSON'dan yeniden hesap)

| Toplam | A | Benim | |
|---|---|---|---|
| Doğrulanmış (86 onaylı + 7 onaysız) | 72.556,44 | 72.556,44 | ✓ (A151 kısmen'e geçti) |
| Kısmen (27 satır) | 1.962,31 | 1.962,31 | ✓ |
| Doğrulanmamış (10) | 4.629,63 | 4.629,63 | ✓ |
| Parça | 79.148,38 | 79.148,38 | ✓ |
| Okul bütçesi | 93.538,38 | 93.538,38 | ✓ (+5,22 = 18 × (3,89 − 3,60)) |
| × 1,15 | 107.569,14 | 107.569,14 | ✓ |
| Kararsız hariç / × 1,15 | 93.147,10 / 107.119,16 | aynı | ✓ |
| Koşullu dahil × 1,15 | 112.844,97 | 112.844,97 | ✓ |
| Kıyas: alınacaklar − 78.023,96 | +29.545,18 | +29.545,18 | ✓ |
| Kıyas: elde dahil 116.845,70 − 102.919,71 | +13.925,99 | +13.925,99 | ✓ |
| Adet × birim uyumsuz satır | — | 0 | ✓ |

### Yeniden açılan sayfalar (09.11.2026, 04:41)

| Sayfa | A'nın iddiası | Benim bulduğum | Sonuç |
|---|---|---|---|
| https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya (Limacell) | 4.814,86; 3 iş günü; 30 A sürekli | 4.814,86; "KARGO BEDAVA"; "En geç 12 Kasım, 2026 Perşembe günü kargoda"; "en fazla 30 amperlik"; özel üretim ort. 3 iş günü | ✓ |
| https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912 (M6×16 ikinci satıcı) | 3,89 taban; ürün stoğu 322.514; 2.000 TL üzeri ücretsiz | "3,24 TL + KDV" (`salePrice` 3,888); ölçü listesinde 6x16 var; `stockamount` 322514; "2.000₺ Üzeri … Ücretsiz Kargo" | ✓ (stok ürün geneli, ölçü bazında değil) |
| https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata (CNC kargo) | 3,60; stok 2 | 3,60; "2 adet stokta"; kargo 132 TL, 2.400 TL üzeri ücretsiz | ✓ |
| https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip | 934,08; stok 120,9 m; kargo 132 / 2.400 | aynı | ✓ |
| https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3 (Rhino kargo + insert) | varyantlar ID3 OD4 L4, OD5 L4–8; kargo 139 / 2.500; delik kuralı | aynı 6 varyant (L5,7 yok); "2500 TL Üzeri Kargo Bedava, Yurtiçi Kargo 139TL"; "somun dış çapından yaklaşık 0.1 mm - 0.2 mm daha dar bir delik" | ✓ |
| https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman | 108,16; stok 51; 16:00 aynı gün; 2.500 eşik | "Aynı Gün Kargo Saat 16:00'a kadar", "2500 ₺ ve Üzeri Ücretsiz Kargo", "51 STOKTA", 108,16 | ✓ |

### Öneri 18 eşleme tablosu (günlük §5.1)

51 `maliyet.json` satırı + 21 bölünme satırı denetlendi: **idx ↔ `ad` 51/51 aynı**, hepsi V3'te görünür, F8a birimleri JSON'la aynı,
eşlenen F8a satırlarının hepsi `dogrulandi` / `dogrulandi_onaysiz_satici` (kısmen ya da v4 yaklaşık satır yok). İki uygulama sorunu:
(1) öneri 11 gamepad'i (idx 80) silerse ya da 18 satır bölerse 105, 106, 120, 121, 126 numaraları kayar; (2) metin yalnız `satici`, `url`,
`tl`, `durum`, `stok` diyor: satıcısı değişen satırlarda `model` eski kalır (ör. acil stop, şarj cihazı).

### Birebir düzeltmeler (A ya da kayıt ajanı; ≤ 2 satır)

- **T1-1** `F8a-gunluk.md:632` (öneri 18) sonuna ekle: `idx'ler kayıt öncesi maliyet.json (c7f9af4) içindir; 18 ilk uygulanır, sondan başa (126 → 0); model alanı da F8a urun'üyle değişir.`
- **T1-2** `F8a-gunluk.md:625` (öneri 11): `çıkarılsın (Ahmet'in 03.11 kararı, v4 raporu).` → `V3'ten çıkarılsın: ver "v1,v2" + not (F4a'nın MAX98357A deseni; satır silinmez, idx kaymaz; Ahmet'in 03.11 kararı, v4 raporu).`
- **T1-3** `F8a-gunluk.md:615` (öneri 1): `→ secenek: kosullu ya da kesin (Ahmet; 90° HDMI v4'te zaten kesin)` → `→ secenek: kosullu (Ahmet kesin derse kaldırılır; 90° HDMI v4'te kesin)`.
- **T1-4** `F8a-gunluk.md:617, 622, 631` (öneri 3, 8, 17): satır adları V1/V2 satırlarıyla ortak; hedef yazılsın: 3 → `idx 14 ve 124 (ver v3)`, 8 → `idx 33`, 17 → `idx 48`.
- **T1-5** `F8a-siparis.md:580` (§9/11) sonuna ekle: `Dayanım sınıfı farkı (A2-70 ↔ fosfat; sınıf sayfada yok) sigma bağlantısı için kontrol edilmedi.`
- **T1-6** `F8a-siparis.md:572` (§9/3) sonuna ekle: `M5 için de aynı karar: kupon delikleri Ø6,2–6,6, Rhino OD 7 kuralıyla Ø6,7–6,8 gerekir (§4.1).`

Bunlar uygulanınca paket **GEÇER**; yalnız metin eklemeleri, sayı değişmiyor, B'nin yeniden bakmasına gerek yok.

### Kayıt ajanı (C) için `maliyet.json` önerilerinin son listesi

Uygulama sırası: önce 18 (sondan başa), sonra 1–17 ve 19 (yeni satırlar dosya sonuna), en son 20. idx'ler `c7f9af4` içindir; her satırda
`ad` da karşılaştırılır. F8a id'leri `F8a-siparis.json` `kalemler[].id`; fiyat, URL ve satıcı oradan.

| Sıra | No | Kısa tanım | Hedef (`maliyet.json` idx) | Onay |
|---|---|---|---|---|
| 1 | 18 | Satıcı/model/fiyat aktarımı, eşleme tablosu (günlük §5.1); `model` dahil | 51 satır (§5.1) | **Onay** (T1-1 ile) |
| 2 | 1 | Fiyatsız adaylara fiyat: S89, S47 → `secenek` kaldır; K4a/b/d/e → `kosullu`; F1a/b/c → `kosullu`; K4c, K4f kalır; F1b `not` | 41, 42, 83–91 (K4c, K4f değişmez) | **Onay** (T1-3 ile) |
| 3 | 2 | 90° HDMI ve 90° micro USB `g: ses` → `elektronik` | 89, 90 | **Onay** |
| 4 | 3 | DS3235 1.171,50 → 1.809,00 (S60), `not` "indirimli, liste 1.930" | 14, 124 | **Onay** (T1-4) |
| 5 | 4 | MG996R 199 → 202,50 (S56) | 15, 125 | **Onay** |
| 6 | 5 | XVF3800 → ReSpeaker Mic Array v2.0 6.680,04 (S83) | 38 | **Onay** |
| 7 | 6 | D36V50F5 → D24V50F5 2.266,93 (S70) | 61 | **Onay** |
| 8 | 7 | Yeni: göğüs ekranı 11,6" (S74), 12 V regülatör (S75), HDMI 1,5 m (S77) | yeni | **Onay** |
| 9 | 8 | Kafa ekranı QLED 7.217,95 (S76) ekle, Waveshare 10,1" (B) V3'ten çıkar | 33 + yeni | **Koşullu**: yalnız Ahmet "alınacak" derse (§9/5); yoksa dokunma |
| 10 | 9 | Kafa: SY8205 (S31), micro USB 30 cm (S81), USB hub (S92) yeni; "Ekran kablosu" → DIY HDMI seti (S78–S80) | 36 + yeni | **Onay** |
| 11 | 10 | Filament → baskı hizmeti | — | **Ret** (A geri çekti; §9/10 Ahmet sorusu) |
| 12 | 11 | Gamepad ve perçin somun aleti V3'ten çıkar (`ver: "v1,v2"` + not, silme yok) | 80, 129 | **Onay** (T1-2 ile) |
| 13 | 12 | Kargo adet 12 → 4 (120 kalır, not); yeni "Rhino3DPrinter kargosu" 1 × 139 | 122 + yeni | **Onay** |
| 14 | 13 | Isıl gömme M3/M5 yalnız `not` (taban 5,29 / 6,35; L 5,7 yok); `tl`, `durum`, adet değişmez | 117, 118 | **Onay** (yalnız not) |
| 15 | 14 | Rulman 108,16 / 30,04; 625ZZ model "BGR (Karbon)" | 16, 17 | **Onay** |
| 16 | 15 | Tırtıllı somun M5 3,96; M6 3,90, adet 62 | 7, 10 | **Onay** |
| 17 | 16 | Geniş köşe: CNC birincil `stok: "yok"`, `alt` Otomasyoncu 31,36 | 9 | **Onay** |
| 18 | 17 | Akü `not` (7 gün, stok 1); `alt` Limacell 4.814,86 (onaylı değil, 3 iş günü, ölçü/30 A kontrolü) | 48 | **Onay** (T1-4) |
| 19 | 19 | Adet değişenler (servo uzatma 19, 18 AWG 14, hat yuvası 5, bıçak 7, TVS 3, pertinaks 5, USB kablo 2, vida satırları §2.1) | ilgili satırlar | **Onay** |
| 20 | 20 | `tarih` → `"2026-11-09"`; yalnız F8a "doğrulandı" satırları `dogrulandi`; `notlar[0]` "kısmen" kalır | kök alan | **Onay** (en son) |

Kapsam dışı (C uygulamaz): M6×16 satıcı değişimi (Ahmet §9/11), insert varyantı ve adedi 168 ↔ 176 (Ahmet §9/3, P4.3), K4/K9 seçimleri, öneri 10.
