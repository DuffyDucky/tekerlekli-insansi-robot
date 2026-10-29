# Lale: tarama bulguları ve düzeltme planı (11 Ekim 2026)

Dört inceleme ajanı (mekanik, çakışma ve hareket, elektrik ve malzeme, kod ve belge) projeyi yalnız okuyarak taradı.
Kritik ve yüksek bulguların hepsini orkestratör kaynak koddan ya da hesaptan yeniden kontrol etti
(✔ = orkestratör doğruladı, ◐ = ajan ölçtü/hesapladı, ○ = olası, ölçüm ya da datasheet gerekiyor).
**Hiçbir düzeltme uygulanmadı. Duffy "başla" deyince başlanacak.**

## Önce bilinmesi gerekenler (baskı ve siparişi şimdiden etkiliyor)

1. **Üst kol tüpü ve kol çatalı basılmamalı.** Baskı listesinde Parti 1'de ("hemen") duruyorlar, ama dirsek kabloları
   tüpün içinden omuza çıkamıyor (bkz. M1). Bu iki parça M1 düzeltilene kadar bekler. ✔
2. **Yerinde dönüş, motor hesabında hiç yok.** Tekerlekler kare yerleşimde (iz 356 mm, aks arası 370 mm). Bu düzende
   yerinde dönerken tekerlekler yana sürtünür. Ajanın hesabına göre bu, motor başına 10–15 kg·cm ister: sürekli
   değerin %165–240'ı (sürtünme katsayısı 0,4–0,6 varsayımıyla). ✔ (hesapta yok) ◐ (sayılar)
3. **10 servonun tamamı tek bir 8 A düşürücüden besleniyor.** Hepsi birden zorlanırsa toplam 25 A çekebilir. ✔
4. **5 V sonar sinyali 3,3 V'luk ESP32 girişine doğrudan bağlanıyor.** Arada gerilim bölücü yok, ESP32 girişi zarar
   görebilir. ✔ (malzeme listesinde direnç yok)

## Duffy'nin vereceği kararlar (plan buna göre dallanır)

| # | Karar | Seçenekler | Önerim |
|---|---|---|---|
| K1 | Dönüş sorunu | (a) Ön iki teker yerine omni teker. Aks yerleri aynı kalır, dönüşte yana sürtünme büyük ölçüde kalkar. (b) 2 tahrikli teker + 2 sarhoş teker. (c) Yazılımda yerinde dönüş yok, yalnız geniş yay çizerek dönüş. (d) Daha güçlü motor. | **Önce ölç** (tek motorun durma torku ve zemin sürtünmesi, ~1 saat). Ölçüm sonucu kötü çıkarsa **(a)**, en az CAD değişikliği bu. (c) ek olarak her durumda uygulanmalı. |
| K2 | Göğüs ekranı | Nextion NX1060P101 (CAD'de bu var, maliyet listesinde yok) / Waveshare 10,1" HDMI (maliyet listesinde bu var, CAD'deki ekran açıklığına sığmıyor) | Nextion: tek HDMI kablo yeter, Pi'de USB yuvası boşta kalır, CAD hazır. Waveshare seçilirse göğüs bandı yeniden çizilir. |
| K3 | Akü | Victron SuperPack 12,8/20 (akü raporunun 1. önerisi) / Limacell 24 Ah (maliyet listesinde bu var) | Akü raporundaki karar. Ölçü teyidi gelince CAD'deki yuva ve takoz güncellenir. |
| K4 | Kamera bağlantısı | CSI şerit kablo yaklaşık 1,3 m gerekiyor, bu uzunluk sınırda ve kafa dönerken kablo bükülür / USB kamera | USB kamera: pan bükülmesine dayanıklı. Camera Module 3 alındıysa CSI'dan HDMI'a çeviren uzatıcı. |
| K5 | Depo boyutu | Büyük üretilmiş dosyalar (STEP 18 MB, rapor.html sayfaları toplam ~15 MB) her güncellemede depoya yeniden giriyor. `.git` şimdiden 86 MB. | Bunları GitHub "Release" eki yap, depoda yalnız betikler ve küçük dosyalar kalsın. |

**14 Ekim 2026 kararları (Duffy: "önerilerin tamam"):** K1 önce ölç, kötüyse ön iki teker omni; yay çizerek dönüş her
durumda. K2 Nextion. K3 Victron SuperPack 12,8/20. K5 büyük dosyalar Release ekine. **K4 açık:** Duffy Pi 5'i kafaya
koymayı düşünüyor ("şerit kablo için, tam kararlaştıramadım"); USB kamera ile karşılaştırılacak.
**K4 kararı (14 Ekim 2026, akşam):** Pi 5 kafaya gider, havalandırma yarıklarıyla (Duffy, önerilen seçeneği seçti).
Dayanak `planlama/adim1/P-pi-kafada.md`: yer sığıyor, eğme servosu payı ≈1,96×, kafa içi ≈49 °C (servo sınırı 55 °C).
Boyundan 12 V + tek veri kablosu geçer, kafada 5 V çevirici; kamera şeridi 300 mm. İş 3. adıma girer.

## Faz 1: Mekanik CAD düzeltmeleri

Kural gereği her modül iki ajana bölünür: önce tasarım ajanı, sonra ayrı bir ajan çakışma, regresyon ve rapor işini yapar.

| # | Önem | İş | Dosyalar | İş miktarı |
|---|---|---|---|---|
| M1 | KRİTİK | **Kol kablo yolu.** Üst kol tüpüne ve kol çatalına kablo penceresi ve oluk. Ön kol başı ile çatal köprüsü arasında 4 mm kalıyor, dirsek dönerken kablo burada sıkışır; buraya kablo kanalı. Omuz S1 ekseninden geçiş için kabuktaki Ø84 deliğe kablo halkası payı ve servis lopu. ✔ | omuz, dirsek, kabuk | L |
| M2 | ORTA | Tüp dış yüzü ile dirsek bileziği arası her yanda 0,1 → 0,25 mm. Dirsek kontrolü tüp iç çapını eski sabitten (25,5) okuyor; `A.GECME`'den okusun, kabul sınırı 0,3. (11 Ekim değişikliğimde gözden kaçmıştı.) ✔ | arayuz, dirsek | S |
| M3 | ORTA | M6 vida ucunun somunu geçme payı 0,1 mm, çok az. Omuz yuvasında pul kaldırılır ya da M6×18 kullanılır. Taban plakasında da en az 0,5 mm pay şartı konur. ◐ | omuz, taban | S |
| M4 | YÜKSEK | Omuzun 10 baskı parçası için baskı yönü, destek ve çıkıntı analizi yok, oysa baskı listesi hepsine "desteksiz" diyor. Analiz eklenir, PETG-CF doluluğu 0,8–0,9 alınır. ✔ | omuz | M |
| M5 | ORTA | Kabuk bindirmesindeki 0,2 mm boşluğu ölçen bir kontrol yok. Dil ile komşu parça arası en az 0,15 mm şartı konur. ✔ | kabuk | S |
| M6 | ORTA | **Montaj sırası ve alet erişimi.** Kabuk kapanınca gövde braketinin M5 vidalarına erişilemiyor. Omuz bandındaki Ø84 delik kapalı bir halka; kol takılıyken bant çıkmaz. Bunların için ya kesin bir montaj sırası yazılır ya da banda yarık açılır. Etek arkasına sigorta ve servis kapağı. ○ | kabuk, taban, montaj rehberi | M |
| M7 | ÖNERİ | Test kuponuna ısıl gömme somun deliği için derinlik çeşidi (L + 1) ve tüp-bilezik geçme halkası eklenir. | test | S |
| M8 | DÜŞÜK | Sigma kesim planı: ilk çubukta yalnız 3,5 mm artık kalıyor, stok boy toleransı yok. Orta ara ray 3. çubuğa alınır. ✔ | iskelet | S |
| M9 | ÖNERİ | Bağlantı elemanı çeşidini azaltma. Şu an M3'te 7, M6'da 5 farklı vida tipi var. | tüm modüller | M |
| M10 | ÖNERİ | Ağırlık azaltma: kabuk duvarı 3 → 2,4 mm yaklaşık −1 kg ve −25 saat baskı eder (önce kupon testi gerekir). 30×30 sigma da değerlendirilebilir. Hafiflemek motor payını doğrudan artırır. | kabuk, iskelet | L |

## Faz 2: Güç ve elektrik (taban modülü + malzeme listesi)

| # | Önem | İş | İş miktarı |
|---|---|---|---|
| E0 | KRİTİK | **Dönüş yükünü taban hesabına ekle**, sonra K1 kararını uygula. Ölçüm: bir JGB37'nin durma torku ve akımı (güç kaynağıyla), robotun tekerleğinin zemin sürtünmesi. ✔ | M (+ K1'e göre L) |
| E1 | YÜKSEK | Servo beslemesini ikiye ayır: iki 6 V düşürücü (sağ kol + kafa / sol kol) ya da tek 15–20 A düşürücü. Kablo 16 AWG. Servo gücü PCA9685 kartının üstünden değil, dağıtım klemensinden doğrudan gitsin. ✔ | S |
| E2 | YÜKSEK | Gerilim seviyeleri: HC-SR04 çıkışına gerilim bölücü (ya da 3,3 V uyumlu HC-SR04P), akü gerilimi için ADC bölücüsü, acil stopun durumunu okumak için 2. kontak (NO) ya da optokuplör, PCA9685 mantık beslemesi 3V3'ten. ✔ / ○ | S |
| E3 | YÜKSEK | **Acil stop yeniden başlatma.** Mantar bırakılınca röle kendiliğinden çekiyor, servolar tanımsız bir anda güç alıyor. Röle bobini ESP32'den bir "devreye al" komutuyla kumanda edilsin; mantar butonun NC kontağı seri kalsın. ◐ | M |
| E4 | YÜKSEK | Pi 5 beslemesi: düz 5,1 V ile USB'lere 600 mA sınırı geliyor. `usb_max_current_enable=1` ayarı, 5 V hattına aşırı gerilim koruması (TVS). ESP32 iki yerden besleniyor (Pi USB'si ve çevre 5 V hattı), araya diyot konur ya da tek kaynağa inilir. ○ | S |
| E5 | ORTA | ESP32 pin planı tablosu (26 sinyal, ~24 kullanılabilir GPIO). Başlangıçta durumu önemli pinler ve ADC2 kullanılmaz. | S |
| E6 | ORTA | Fren: acil stopta motorlar boşa düşer. Yazılım freni ≤ 1,8 m/s² ile sınırlanır (karar 29.10, 1,65 m: düzde 0,5 kg el yüküyle bile devrilme payı ≥ 1,54; `planlama/y2/Y2b-ivme.json` `fren_pay`). İsteğe bağlı: motor uçlarını röleyle kısa devre eden dinamik fren. Güç kesilince kollar düşer, bunun için yavaş düşüş çözümü. ○ | M |
| E7 | ORTA | Etek içi ısı: XL4016'ların ısıyı aktaracağı bir yol yok (naylon burç üzerinde duruyorlar). Ölçüm planı, ısı pedi, etek arkasında delik ya da fan. ○ | M |
| E8 | ORTA | Akü sürelerini akü raporuyla hizala. Yoğun kullanım senaryosu 100 W ve üstü alınır (≈ 2,5 saat). ◐ | S |
| E9 | DÜŞÜK | Sigorta: 5 A iki yerde (F4 ve F5) kullanılıyor ama sette bir tane var. İkinci 5 A sigorta eklenir. Ön şarj direnci ya da NTC değerlendirilir. ✔ | S |

## Faz 3: Malzeme listesi (`maliyet.json`)

| # | Önem | İş | İş miktarı |
|---|---|---|---|
| B1 | ORTA | CAD'de olup maliyette olmayan kalemler: 6808-2RS ×4, 625ZZ ×5, 25T Al horn ×10, Al bükme braketler, iç köşe bağlantı ×8, M4/M5 çekiç somun ×16, M5×16 set vida ×8, röle + soket, ESP32 taşıyıcı, M2,5 burç, cırt kayış, XT60 şarj girişi, servo uzatma kabloları (~8 m), konnektörler, dirençler, diyotlar. Fiyatlar satıcı sayfasından doğrulanır. ◐ | M |
| B2 | ORTA | Adet ve sürüm hataları: M5×40 burç 4 → 8; sigma kesim listesi eski (CAD: 3×190, 200, 2×500, 800,5; 3 m stok); T-somun 40 → 18; lazer plaka ölçüsü 340×500 → 270×500; V1/V2'den kalan 3 kalem (`ver`); baskı hizmeti V3 için 5,73 kg; HDMI kablo adedi (K2'ye bağlı). ✔ | S |
| B3 | ÖNERİ | Ucuz eşdeğerler: MAX98357A muadili (≈ −500 TL), K2 kararıyla ekran farkı (≈ −5,7 bin TL olası). | S |

## Faz 4: Eklem sınırları, çakışma taraması

| # | Önem | İş | İş miktarı |
|---|---|---|---|
| C1 | YÜKSEK | Omuz yana açma (S2) alt sınırı 0° → **+3°**. 0°'de boşluk 4,7 mm; −2°'de 0,6 mm; −3°'de temas var. Servo sıfırı da buna göre kalibre edilir. ◐ | S |
| C2 | YÜKSEK | Kafa-kol yasak bölgesi tek kutu olarak verilir: **pan 25…60° (sol kolda −60…−25), tilt 20…30°**. Tablonun hemen kenarında sıfır boşluklu pozlar var. Yazılım satır satır tabloyu değil bu kutuyu kullanır. ◐ | S |
| C3 | ORTA | Omuz sınırları `arayuz.OMUZ`'a taşınır (şu an üç yerde elle yazılı). Bütün sınırlardan `kod/ortak/eklem_sinirlari.json` üreten küçük bir betik yazılır (yazılım planı bunu istiyor). ✔ | S |
| C4 | ORTA | Sol kolda her servonun yönü ve sıfır kayması için bir tablo. Montajdan sonra servolar tek tek doğrulanır (rehbere bir adım olarak girer). ○ | S |
| C5 | ORTA | `carpisma.py`: ince tarama eşiği (şu an 5 mm) adım × yarıçapa göre ayarlanır (30–50 mm). Sınır taramasında komşu pozlar bütün parça çiftleriyle ölçülür. ◐ | M |
| C6 | ORTA | `carpisma_kos.py` hangi dosyalar değişince sonucun eskidiğini izliyor; listesine `*_lib.py`, `sigma_profil.py`, `kafa-analiz.json` eklenir. Raporlar sonucun eskidiğini gördüğünde uyarı basar. ✔ | S |
| C7 | — | Faz 1–2'deki CAD değişikliklerinden sonra tam çakışma taraması **bir kez** yeniden koşulur (11 Ekim değişikliği sonucu bozmadı ◐, ama M1 ve E-işleri geometriyi değiştirecek). | Makine ~1,5 sa |
| C8 | ÖNERİ | Taramayı hızlandırma: bölümleri paralel koşmak, sol kolu sağın aynası saymak (~30 dk kazanç), değişmeyen bölümü atlamak. | M |

## Faz 5: İş akışı, belgeler, depo

| # | Önem | İş | İş miktarı |
|---|---|---|---|
| D1 | YÜKSEK | Kök `README.md` ve `CLAUDE.md`'de asıl kaynak FreeCAD (`tasarim/freecad`) olarak yazılır; eski CadQuery dönemi sayıları (17,75 kg vb.) ayrı bir başlığa taşınır; maliyet ≈ 82.140 TL. ✔ | S |
| D2 | YÜKSEK | `tasarim/freecad/README.md`: gerçek çalıştırma sırası yazılır (modüller → ana montaj → taban → ana montaj). `freecad/index.html` ve README'deki 21,66 kg → 21,62 kg. ✔ | S |
| D3 | ORTA | Rapor betiklerine elle yazılmış eski değerler ("tüp 0,1 mm" ×3, "regresyon birebir aynı" metinleri) betik değişkenlerinden üretilsin. ✔ | S |
| D4 | YÜKSEK | Regresyonlar yeniden koşulur, 11 Ekim değişikliği "kasıtlı fark" olarak işaretlenir, yeni taban çizgisi bu olur. ◐ | M |
| D5 | ORTA | Baskı analizi üç ayrı kopya hâlinde ve aynı ölçütü kullanmıyor. Tek ortak modüle (`baski_lib.py`) indirilir, 44 parça yeniden analiz edilir, baskı listesi yeniden üretilir. ✔ | M |
| D6 | ORTA | Planlama dosyaları: tek takvim numarası (proje planı ile yazılım planı aynı hafta numarasına ~2 hafta farklı tarih veriyor). Proje planındaki SolidWorks ve V1 izleri temizlenir. Yazılım planındaki Y8 cümlesi düzeltilir (`hareket_dongu.py` jest oynatmıyor). Baskı listesinde eğme çatalı notu ve "desteksiz" iddiası düzeltilir. OZET'e ekran kararı açık iş olarak eklenir. ✔ | S |
| D7 | ÖNERİ | `uret.py`: tek komutla, bağımlılık sırasına göre ve yalnız eskiyen modülleri üretir. `dogrula_belge.py`: belgelerdeki sayıları analiz dosyalarıyla karşılaştırır. | M |
| D8 | — | K5 kararına göre depo temizliği. OneDrive'da `donanim/` (129 MB) senkronizasyon dışına alınır. | S–M |

## Uygulama sırası

| Adım | Ne | Neden bu sırada |
|---|---|---|
| 0 | K1–K5 kararları + JGB37 ve zemin sürtünmesi ölçümü (ekip yapar, ~1 sa) | E0 ve M1'in şekli bunlara bağlı |
| 1 | Hızlı ve bağımsız işler: M2, M3, M5, M8, C1, C2, C3, C6, D3 | Küçük işler, sonraki CAD işlerinin kontrollerini düzeltiyor |
| 2 | M1 kablo yolu (omuz, dirsek, kabuk) + M4 omuz baskı analizi | Parti 1'deki iki parçayı bekletiyor |
| 3 | E0 (+ K1), E1–E4, E7 taban ve güç | Taban CAD'i bir kez açılsın |
| 4 | M6 montaj sırası ve erişim (rehberle birlikte), M7 kupon | Montaj rehberine (A+B) girdi olur |
| 5 | B1, B2, E8, E9, D6 malzeme ve plan | CAD kesinleşince adetler doğru olur |
| 6 | Bütün modüller yeniden üretilir → C7 tam tarama (C5 ile) → D4 regresyon → D5 | Bir kez ve en sonda |
| 7 | D1, D2 belgeler; isteğe bağlı D7, C8, M9, M10, D8 | Sayılar artık kesin |

**Ajan düzeni:** CAD işlerinde modül başına iki ajan (tasarım, ardından kontrol, regresyon ve rapor). Malzeme listesi ve
belge işleri ise ayrıntılı tarifle verilir. Orkestratör her adımın sonunda kritik değerleri kendisi yeniden ölçer.
**Tahmini yük:** 1–2. adımlar bir oturum, 3. adım bir oturum, 4–7. adımlar bir iki oturum (makine süresi hariç).

## İncelemede sorunsuz çıkanlar

- Sigma eğilmesi (gerilme ≤ 0,93 MPa, sehim 0,17 mm).
- Isıl gömme somun etrafındaki et (yeni delik çapıyla da yeterli).
- Vida kavrama derinlikleri.
- 44 parçanın tablaya sığması.
- Rulman yükleri.
- Kafa kablo yolu (Ø32 boş mil).
- 11 Ekim değişikliği modüller arası çakışma sonucunu bozmuyor.
- Tarama adımları arasında kaçan çakışma bulunmadı (en dar 3,68 mm).
- Kollari_oynat hareketleri sınır içinde ve yasak bölgeye girmiyor.
- Rampada etek zemine sürtmüyor (en az 26,9 mm).
- Rampa torku, devrilme ve akü aritmetiği.
- Servo sayıları.
- Parça ve kütle toplamları (907 parça, 21.224 g).
- Site bağlantıları.
