# Lale: kablo tablosu (okunur görünüm)

> **Bu dosya üretilmiştir, elle düzenlenmez.** Tek kaynak `planlama/adim3/kablolar.json`; görünüm `py -3 planlama/adim3/kablolar_uret.py` ile, denetim `py -3 planlama/adim3/kablolar_denetim.py` ile.

Tablo sürümü 3, tarih 2026-11-14. Robottaki kabloların tek kaynağı. Okunur görünüm planlama/adim3/kablolar.md bu dosyadan planlama/adim3/kablolar_uret.py ile üretilir; denetim planlama/adim3/kablolar_denetim.py. Bir kaydı değiştirince ikisini de koş. Sürüm 2 (14.11, P10.7a ikinci tur): orkestratör kararları O-1 … O-14 işlendi (kararlar), kesit kuralı web kaynaklı tabloya bağlandı, boyu bilinmeyenlere etiketli kaba tahmin (boy_tahmin), klemens türleri ve malzeme özeti eklendi. Üçüncü tur (14.11): O-15 … O-18 ve O-3 / O-4 revizeleri; boy tahmininden 150 mm pay kaldırıldı. Sürüm 3 (14.11, düzeltme turu 1): düğümler / ağlar / koruyucular / anahtarlar / dallar ve her kablonun besleme zinciri; koruma kablodaki sayıdan değil koruyucular tablosundan; kesit kuralına ortam sıcaklığı düzeltmesi; denetim acil stop, dönüş, 5 V ayrımı ve kesiti devrenin yapısından türetir.

## Özet

- **74 kablo** (çok damarlı demet ve çiftler tek kayıt; damar sayısı 175).
- Durum: kesin 31, kablajda teyit edilecek 42, karara bağlı 1.
- Boyu CAD'de tasarlanmış yoldan ya da listeden belli: 17; belli değil: 57 (bunlarda yalnız etiketli kaba üst sınır var, `boy_tahmin`: tahmin, P10.7b'de ölçülecek).
- Kesit kuralının kayıtlı istisnası: 25 kablo; kesit ↔ koruma uyuşmazlığı karara bağlı: 0 (-).
- Acil stopta enerjili kalan: 44; enerjisiz: 30.

| Demet | Kablo | Karara bağlı | Teyit | Kesin |
|---|---|---|---|---|
| taban alt kat | 12 | 0 | 8 | 4 |
| taban (K1) | 17 | 1 | 13 | 3 |
| taban elektronik katı | 10 | 0 | 5 | 5 |
| taban sonar | 3 | 0 | 0 | 3 |
| etek (F1) | 4 | 0 | 2 | 2 |
| gövde (K2) | 3 | 0 | 2 | 1 |
| boyun | 5 | 0 | 5 | 0 |
| kafa içi | 11 | 0 | 6 | 5 |
| göğüs | 1 | 0 | 1 | 0 |
| kol sağ | 4 | 0 | 0 | 4 |
| kol sol | 4 | 0 | 0 | 4 |

## Renk kuralı

İletken rengi kutbu gösterir: + kırmızı, − / GND siyah (listedeki 12 / 16 / 18 AWG silikon kablolar yalnız kırmızı ve siyah: maliyet.json 12, 16, 18 AWG satırları). Devre türü iki uçta ~2 cm renkli makaronla gösterilir (listedeki 328 parça renkli makaron seti; setteki renkler doğrulanmadı, eksik renk olursa uç etiketi) ve rehber çiziminde aynı renk kullanılır. Çizim renkleri rehberin bugünkü kablo paletinden (tasarim/freecad/rehber/rehber_veri.py kablo_rengi), anahtar kelime yerine devre türüne bağlanır. Belgelerde yazılı bir kablo rengi bulunmadı; korunacak renk yok.

| Sınıf | Devre | Uç makaronu | Rehber çizimi |
|---|---|---|---|
| kirmizi | 12 V doğrudan (akü, ana hat, kutu dalları F3 / F4 / F6, şarj) | kırmızı | `#d63031` |
| turuncu | anahtarlı bara ve motorlar (röle K1 sonrası; acil stopta enerjisiz) | turuncu | `#e67e22` |
| sari | servo gücü (XL4016 A / B / C 6 V ve servo uzatmaları) | sarı | `#e2b714` |
| mavi | 5 V (kafada Pi hattı, tabanda çevre 5 V; yerleri ayrı olduğu için tek renk) | mavi | `#2f86d4` |
| yesil | acil stop (F5 → mantar → bobinler, PC817 #1) | yeşil | `#2e9e4f` |
| mor | sinyal, I2C, sonar, enkoder, akü ölçümü | mor | `#8e44ad` |
| siyah | yalnız toprak kablosu | siyah | `#222222` |
| beyaz | analog ses | beyaz | `#b2bec3` |
| hazir | USB, HDMI, CSI hazır kablolar (üretici rengi; makaron yok) | yok (hazır kablo) | `#7f8c8d` |

## Kesit ve sigorta kuralı

Bir güç kablosunun kesiti, onu koruyan elemanın akımına yetmeli: sigortaysa sigorta değeri, akü BMS'iyse BMS sürekli akımı, dönüştürücünün akım sınırıysa o sınır, seri dirençse direncin sınırladığı akım tablodaki 'en çok koruma' değerini aşmaz. Kabloyu sigorta değil dönüştürücünün akım sınırı koruyorsa sınır ≤ kablonun tablodaki akımı olmalı; değilse o dal ya kalın kesitle ya da ayrı sigortayla kurulur. Akımı sınırlayan bir elemanla korunan kısa kollar o elemanın sınırladığı akıma göre kesit alır, elemanın öncesindeki parça sigortaya göre; kol başka bir yandan (ör. bara) beslenebiliyorsa o yanın koruması geçerlidir. Kesit seçimi (O-1 c): yalnız listedeki kesitler; her dal koruyanına yeten en ince listedeki kesiti alır. Tablo iki web kaynağından; iki kaynak farklıysa temkinli (küçük) değer (O-2 a + b, orkestratör, 14.11.2026). Sürüm 3 (düzeltme turu 1): koruma kablodaki sayıdan değil koruyucular tablosundan, devrenin yapısından türetilir; akım taşıyan her + / − damar (devre türü ne yazılırsa yazılsın) sınamaya girer; sınır ortam sıcaklığıyla düzeltilir (kesit_kurali.ortam). Akım sınırı belgelenmemiş bir koruyucunun arkasındaki kablo ya kayıtlı istisnadır ya da karara bağlı.

Listedeki kablolar en az 80 °C yalıtımlı kabul edildi (14.11 okundu: Robocombo 12 / 16 AWG sayfası 'PVC, 80 °C', Motorobit 18 / 20 AWG silikon 200 °C, servo uzatması PVC −30…80 °C); CFR tablosunun 80 °C, NFPA 79 tablosunun 75 °C sütunu (80 °C'yi aşmayan en yakın) alındı. Tablo ortamı 30 °C; bölge sıcaklığı düzeltmesi kesit_kurali.ortam. Demet düzeltmesi uygulanmadı: CFR Not 2'ye göre aynı demette akım taşıyan iletken 3'ü geçerse çarpan 0,70 ve altı (güç kabloları çift döşenir).

Kaynaklar (iki kaynak farklıysa küçük değer alınır):

- **cfr:** 33 CFR 183.425, Table 5 'Allowable amperage of conductors' (ABD küçük tekne düşük gerilim kablajı), 80 °C sütunu; <https://www.law.cornell.edu/cfr/text/33/183.425> (2026-11-14 okundu). 18 AWG'den başlar. 50 V altında sigorta tablodaki akımın %150'sine kadar olabilir (33 CFR 183.455(c)(1), https://www.law.cornell.edu/cfr/text/33/183.455); burada %150 payı kullanılmadı.
- **nfpa79:** NFPA 79 (2018), Table 12.5.1 'Conductor ampacity based on copper conductors with 60 °C, 75 °C and 90 °C insulation in an ambient temperature of 30 °C' (endüstriyel makine kablajı); Lutze'nin yeniden basımı, 75 °C sütunu; <https://airlinemedia.airlinehyd.com/Literature/Manufacturer_Catalogs/Lutze/datasheets/LUTZE_M120418%2099%20Ampacity%20per%20NFPA%2079.pdf> (2026-11-14 okundu). standardın kendisi değil, kablo üreticisinin yeniden basımı (PDF metni okundu).

| AWG | mm² | CFR | NFPA 79 | En çok koruma | Not |
|---|---|---|---|---|---|
| 12 | 3,31 | 35 A | 25 A | **25 A** | sürüm 1'deki 30 A (06-aku-secimi.md:162, 'genel bilgi') temkinli değerle 25 A oldu: 30 A ana hat bu kurala uymuyor (O-15) |
| 16 | 1,31 | 20 A | 10 A | **10 A** | orkestratörün beklediği ≤ 15 A'dan düşük çıktı |
| 18 | 0,82 | 15 A | 7 A | **7 A** | sürüm 1'deki 7,5 A (kablolama-on-kararlar.md:107-108, 'genel bilgi') 7 A oldu; 18 AWG'yi 7,5 A ile koruyan dal yok |
| 20 | 0,52 | — | 5 A | **5 A** | CFR tablosunda yok (18 AWG'den başlar) |
| 22 | 0,33 | — | 3 A | **3 A** | sinyal teli ve servo uzatması |
| 24 | 0,2 | — | 2 A | **2 A** | kullanılmıyor; sinyal teli 24 AWG alınırsa |

**Ortam sıcaklığı düzeltmesi.** Tablodaki akım 30 °C ortam içindir; kablonun geçtiği bölgenin iç sıcaklık sınırına göre katsayıyla çarpılır (sınır = tablo × katsayı). Bölge demetten; kablo kafaya kadar gidiyorsa ya da ucu kafadaki bir parçadaysa kafa. Kaynak: NEC 2020 Table 310.15(B)(1) (eski 310.15(B)(2)(a)) ortam sıcaklığı düzeltme katsayıları, 30 °C tabanlı, 75 °C sütunu: 41–45 °C 0,82; 46–50 °C 0,75 (<https://open-exam-prep.com/study-guides/va-electrician/conductors-and-cables/temperature-adjustment>, 2026-11-14 okundu; ikincil kaynaktan (sınav hazırlık sayfası). 14.11 düzeltme turu 1 devamı: birincil kaynak denendi, açılamadı: NEC metni NFPA'da ücretli; Schneider Electric başvuru sayfası (productinfo.se.com, NEC 310.15(B)(2)(a)) 403, Elliott Electric tablo sayfası bağlantı reddi. Aynı değerler arama sonuçlarında birden çok ikincil kaynakta (Elliott Electric ve ECM dergisi alıntıları) ve bağımsız kontrolde (P107a-kontrol.md §2-4) geçiyor. 31–40 °C satırları kullanılmadığı için yazılmadı.)

- **etek:** ≤ 45 °C (`planlama/adim3/elektrik.md:318`; etek havası ≤ 45 °C (E7 ölçütü); gövde, göğüs ve kollar için ayrı sınır yok, etek sınırı uygulanır (temkinli)); katsayı 0,82.
- **kafa:** ≤ 49 °C (`planlama/adim3/elektrik.md:302`; kapalı kafa normal karşılamada ~49 °C (hesap, ölçülecek)); katsayı 0,75.

**Kayıtlı istisna `servo-uzatmasi`** (S01, S02, S03, S04, S05, S06, S07, S08, S09, S10; orkestratör, 14.11.2026 (O-2); şart düzeltme turu 1): Tek servonun uzatması, servonun kendi fabrika kablosuyla aynı kesit (22 AWG hobi servo kablosu; fiş standardı, kalınlaştırılmaz). Kısa devrede akımı XL4016'nın çip sınırı (≈ 10 A, tipik; koruyucular.XL4016-A) keser; bu 22 AWG'nin düzeltmeli sınırından (45 °C: 2,46 A) büyük. Sürekli akım tek servonun çektiğiyle sınırlı. Birden çok servonun akımını taşıyan kablolar (SV1–SV3) istisnaya girmez. **Şart:** yalnız tek servonun uzatması; birden çok servonun akımını taşıyan kablo (SV1–SV3, dağıtım kartı) kurala uyar; tezgâhta bir uzatmanın ucu kısa devre edilir, XL4016'nın davranışı (akımı kesiyor mu, kaç A'de, ne kadar sürede) ve uzatmanın sıcaklığı gözlenir (ölçüt: XL4016 akımı ≤ 10 A'de kesiyor ya da düşürüyor, uzatma yalıtımı 80 °C'ye varmadan; T8 test kâğıdı, E bölümü). Kesmiyorsa istisna düşer, orkestratöre. **Kontrol:** E7 yük testinde uzatmaların sıcaklığına elle / termometreyle bakılır; tezgâhta kısa devre denemesi (T8 E bölümü).

**Kayıtlı istisna `ana-hat-12awg`** (G01, G02, G03, G04, G05; orkestratör kararı, 14.11.2026 (O-15)): Kayıtlı devre değerleri değişmez: 12 AWG ana hat, ana sigorta / BMS 30 A. Kablonun yalıtım sınıfı satıcı sayfasında 80 °C (Robocombo 12 AWG sayfası, 14.11 okundu: ürün adı 'silikon kablo', sayfadaki tabloda 'PVC, 80 °C'; ad ile tablo çelişiyor, teslimde kablo üstündeki yazıdan teyit). CFR Table 5'te 12 AWG 80 °C sütununda 35 A; NFPA 79'un 25 A değeri 75 °C sınıfı ve kanal içi makine kablajı içindir. Ana hat kısadır (akü → sigorta ≤ 15 cm, toplam ≤ 1,5 m: 06-aku-secimi.md:161-162) ve öbür güç kablolarıyla sıkı demetlenmeden döşenir. **Şart:** ana hat (G01–G05) öbür güç kablolarıyla sıkı demetlenmeden, ayrı döşenir; P10.7b'de boy ölçülünce gerilim düşümü (en yüksek akımda > %3 ise bir kalın kesit); teslimde kablo üstündeki sıcaklık sınıfı yazısı ≥ 80 °C. **Kontrol:** E7 yük testinde ana hattın sıcaklığı elle / termometreyle; P10.7b'de gerilim düşümü.

Beklenen sürekli akım (`planlama/adim3/elektrik.md:355`): yoğun 14,6 A; teorik tepe 21,8 A (4 motor durmada); 04.11 değişiklikleri eklenince tepe ≈ 22,6 A; tablodaki 25 A'in **altında (45 °C düzeltmeli 20,5 A'in de altında: yoğun 14,6 A)**. Akım bütçesinin toplam satırı (EL:355) 15 Ekim satırlarıyla, 'ESKİ' işaretli: göğüs ekranı (~0,5 A @12 V, EL:349) yok, kafa eski değerle. Üst sınır: 21,8 + 0,5 (göğüs) + 0,33 (kafa tepesinde yalnız Pi hattı: 4,5 A @5 V / 0,90 / 12,8 V ≈ 1,95 A, eski 1,62 A yerine) ≈ 22,6 A; kafanın tam tepesi hesaplanmadı. Zaman ortalaması yoğun senaryoda 104 W / 12,8 V ≈ 8,1 A (EL:420). Hepsi 25 A'in altında; tepe değer kısa süreli. Düzeltme turu 1: ortam düzeltmesiyle (etek 45 °C, 0,82) 12 AWG'nin tablo sınırı 20,5 A; yoğun sürekli akım 14,6 A bunun altında, kısa süreli tepe (≈ 22,6 A) üstünde.

**Kayıtlı istisna `motor-fabrika-kablosu`** (M01, M02, M03, M04; orkestratör kararı, 14.11.2026 (O-16); gerekçe düzeltme turu 1): Motorun fabrika kablosu değiştirilmez: cihazın kendi kablosu (JGB37-520, 6 damarlı, güç ve enkoder ortak). Kesiti belgede yok; motor gelince okunur ve tabloya yazılır. İnce motor kablosunu F1 20 A korumaz. Sürekli akımı motor sargısı sınırlar: durma akımı 2,8 A (tahmini, elektrik.md:157; 9 kg·cm senaryosunda 1,2 A, EL:161). Kablo içi kısa devrede koruma BTS7960 çipinin anahtarlamalı akım sınırlaması ve mandallı ısıl kapatması (Infineon veri sayfası; koruyucular.BTS7960-sol) ile yazılımın IS akım ölçümünde arıza bayrağı görünce EN'i kesmesidir (firmware şartı; Efe'ye bildirilecek, pin-haritasi.md kurallarına yeni numara verilmedi). **Şart:** BTS çıkışı ile motor kablosu arasında uzatma / ara parça gerekirse o parça 12 AWG (F1 20 A); motor kablosunun kesiti 18 AWG'den inceyse orkestratöre. **Kontrol:** motor gelince kablo kesiti okunur ve kesit alanına yazılır; E7 yük testinde motor kablosunun sıcaklığı.

**Kayıtlı istisna `kafa-5v-donusturucu-arkasi`** (K03, K05, K04; orkestratör kararı, 14.11.2026 (düzeltme turu 1), madde 5; K04 orkestratör kararı, 14.11.2026 (O-21)): D24V50F5'in akım sınırı belgelenmemiş ('5 A' tipik en çok sürekli akım, sınır değil); dönüştürücünün aşırı akım + kısa devre koruması ve ısıl kapatması var (Pololu ürün sayfası, 14.11). Pi hattında gerilim düşümü istenmediği için sigorta eklenmez. Kablolar kafa içinde, kısa, 18 AWG. K04 (O-21): SY8205'in akım sınırı da belgelenmemiş (satıcı sayfasında koruma yazmıyor; 3,7 A sürekli anma); kafa ekranı yükü 0,9 A varsayım (elektrik.md:25, üreticide değer yok), hazır micro USB kablo kısa, kafa içi. **Şart:** yalnız kafa içindeki 5 V dönüştürücülerin (D24V50F5, SY8205) çıkışından kafa içi yüklere giden kısa kablolar (K03 Pi USB-C, K05 PAM8403: 18 AWG; K04 kafa ekranı: hazır micro USB kablo); K10 masa testinde (KT1) tam yükte kablo sıcaklığına bakılır; kablo ısınıyorsa istisna düşer, orkestratöre. K04: teslimde kablonun üstündeki kesit yazısı okunur; 24 AWG'den inceyse ya da yazı yoksa 18 AWG + micro B fişle yeniden yapılır (kayıt durumu kablajda teyit). **Kontrol:** KT1 / K10 masa testi: Pi stres + en yüksek ses, D24V50F5 hattı akımı ve K03 / K05 sıcaklığı; K04: teslimde kesit yazısı, ilk açılışta ekran akımı (USB ampermetre) ve kablo sıcaklığı.

**Kayıtlı istisna `servo-ana-hat-16awg`** (SV1, SV2, SV3; orkestratör kararı, 14.11.2026 (O-20 c)): XL4016 çıkışından dağıtım kartına giden servo ana hatları (16 AWG). Kaynak akımı XL4016'nın çip sınırıyla (≈ 10 A tipik, koruyucular.XL4016-A) sınırlı. 16 AWG için iki kaynağın biri 10 A (temkinli; ortam düzeltmesiyle etek 8,2 A, kafa 7,5 A), öbürü 20 A (düzeltmeyle ≥ 15 A; kesit_kurali.tablo dayanak). Hat kısa; girişte ayrıca hat sigortası var (A / B 7,5 A, C 5 A, 12 V tarafı). Çıkışa sigorta konmaz: kol servolarının tepe akımında atıp kolu düşürür. Beklenen sürekli ve tepe akım düzeltilmiş sınırın altında (beklenen_akim_a). **Şart:** yalnız XL4016 A / B / C çıkışından dağıtım kartı A / B / C'ye giden 16 AWG ana hatlar; T8 E tezgâh kısa devre denemesi SV hatlarını da kapsar (ölçüt aynı: XL4016 ≤ 10 A'de kesiyor ya da düşürüyor, kablo < 80 °C); P10.7b'de boy ölçülünce gerilim düşümü hesaplanır; E7 yük testinde hat akımı beklenen değerin üstündeyse istisna düşer, orkestratöre. **Kontrol:** T8 E (SV1 / SV2 / SV3 dağıtım kartı ucunda kısa devre, en çok 2 s) + E7 yük testi (hat akımı, kablo sıcaklığı).

Beklenen akım (`planlama/adim3/elektrik.md:121-123 (servo hatları tablosu, 6 V tarafı; kol-analiz.json, oran 1,25; tahmini)`):

| Kablo | Hat | Sürekli (yoğun) | Tepe | Bölge | Düzeltilmiş sınır | Altında |
|---|---|---|---|---|---|---|
| SV1 | A (sağ kol) | 4,87 A | 7,24 A | etek | 8,2 A | evet |
| SV2 | B (sol kol) | 4,87 A | 7,24 A | etek | 8,2 A | evet |
| SV3 | C (kafa pan + tilt) | 1,5 A | 5 A | kafa | 7,5 A | evet |

tepe = iki servo kalkışta + diğerleri yoğunda (kısa süreli); en kötü hat A / B tepede düzeltilmiş sınırın %88'i, C %67'si. Hat akımı ölçülmedi (E7).

**Gerilim düşümü** (orkestratör, 14.11.2026 (O-1)): en yüksek akımda gerilim düşümü > %3 ise bir kalın kesit; sınama P10.7b (boylar ölçülünce). Alanı taşıyan kablolar: G06, G08, G09, G10, G11, G12, G13, G17, G18, G19, G20, A01, A02, A03, A04, A05, K01, K02, K03, K05.

### Dal başına kesit

Koruması olan güç dalları (aynı tablo `elektrik.md` sonunda üretilmiş blok olarak durur).

| Kablo | Dal | Kesit | Koruyan | Bölge | Düzeltilmiş sınır | Durum |
|---|---|---|---|---|---|---|
| A01 | F5-mantar-oncesi | 18 AWG | F5 2 A (sigorta kutusu) (`F5`, 2 A) | etek 45 °C × 0,82 | 5,74 A | kesin |
| A02 | mantar-sonrasi | 18 AWG | F5 2 A (sigorta kutusu) (`F5`, 2 A) | etek 45 °C × 0,82 | 5,74 A | kesin |
| A03 | mantar-sonrasi | 18 AWG | F5 2 A (sigorta kutusu) (`F5`, 2 A) | etek 45 °C × 0,82 | 5,74 A | kablajda teyit edilecek |
| A04 | mantar-sonrasi | 18 AWG | F5 2 A (sigorta kutusu) (`F5`, 2 A) | etek 45 °C × 0,82 | 5,74 A | kesin |
| A05 | mantar-sonrasi | 18 AWG | F5 2 A (sigorta kutusu) (`F5`, 2 A) | etek 45 °C × 0,82 | 5,74 A | kablajda teyit edilecek |
| A06 | mantar-sonrasi | 22 AWG | F5 2 A (sigorta kutusu) (`F5`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kablajda teyit edilecek |
| B01 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kablajda teyit edilecek |
| B02 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kablajda teyit edilecek |
| G01 | aku-ana | 12 AWG | Akü BMS (Victron SuperPack, 30 A sürekli) (`aku-bms`, 30 A) | etek 45 °C × 0,82 | 20,5 A (istisna: ana-hat-12awg) | kablajda teyit edilecek |
| G02 | aku-ana | 12 AWG | Akü BMS (Victron SuperPack, 30 A sürekli) (`aku-bms`, 30 A) | etek 45 °C × 0,82 | 20,5 A (istisna: ana-hat-12awg) | kablajda teyit edilecek |
| G03 | aku-ana | 12 AWG | Ana sigorta 30 A (standart bıçak, kablolu yuva) (`ana-sigorta`, 30 A) | etek 45 °C × 0,82 | 20,5 A (istisna: ana-hat-12awg) | kablajda teyit edilecek |
| G04 | aku-ana | 12 AWG | Ana sigorta 30 A (standart bıçak, kablolu yuva) (`ana-sigorta`, 30 A) | etek 45 °C × 0,82 | 20,5 A (istisna: ana-hat-12awg) | kablajda teyit edilecek |
| G05 | aku-ana | 12 AWG | Akü BMS (Victron SuperPack, 30 A sürekli) (`aku-bms`, 30 A) | etek 45 °C × 0,82 | 20,5 A (istisna: ana-hat-12awg) | kablajda teyit edilecek |
| G06 | sarj | 16 AWG | Şarj hat sigortası 7,5 A mini (akü tarafındaki ucun dibinde) (`hat-sarj`, 7,5 A) | etek 45 °C × 0,82 | 8,2 A | kablajda teyit edilecek |
| G08 | F1-kontak-oncesi | 12 AWG | F1 20 A (sigorta kutusu) (`F1`, 20 A) | etek 45 °C × 0,82 | 20,5 A | kablajda teyit edilecek |
| G09 | anahtarli-bara | 12 AWG | F1 20 A (sigorta kutusu) (`F1`, 20 A) | etek 45 °C × 0,82 | 20,5 A | kablajda teyit edilecek |
| G10 | F1-kontak-oncesi | 12 AWG | F1 20 A (sigorta kutusu) (`F1`, 20 A) | etek 45 °C × 0,82 | 20,5 A | kablajda teyit edilecek |
| G11 | anahtarli-bara | 12 AWG | F1 20 A (sigorta kutusu) (`F1`, 20 A) | etek 45 °C × 0,82 | 20,5 A | kablajda teyit edilecek |
| G12 | anahtarli-bara | 12 AWG | F1 20 A (sigorta kutusu) (`F1`, 20 A) | etek 45 °C × 0,82 | 20,5 A | kablajda teyit edilecek |
| G13 | anahtarli-bara | 12 AWG | F1 20 A (sigorta kutusu) (`F1`, 20 A) | etek 45 °C × 0,82 | 20,5 A | kablajda teyit edilecek |
| G14 | anahtarli-bara | 16 AWG | Hat sigortası A 7,5 A mini (XL4016 A girişi) (`hat-A`, 7,5 A) | etek 45 °C × 0,82 | 8,2 A | kablajda teyit edilecek |
| G15 | anahtarli-bara | 16 AWG | Hat sigortası B 7,5 A mini (XL4016 B girişi) (`hat-B`, 7,5 A) | etek 45 °C × 0,82 | 8,2 A | kablajda teyit edilecek |
| G16 | anahtarli-bara | 16 AWG | Hat sigortası C 5 A mini (XL4016 C girişi) (`hat-C`, 5 A) | etek 45 °C × 0,82 | 8,2 A | kablajda teyit edilecek |
| G17 | F3 | 18 AWG | F3 5 A (sigorta kutusu) (`F3`, 5 A) | kafa 49 °C × 0,75 | 5,25 A | kablajda teyit edilecek |
| G18 | F4 | 18 AWG | F4 5 A (sigorta kutusu) (`F4`, 5 A) | etek 45 °C × 0,82 | 5,74 A | kesin |
| G19 | F4 | 16 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 8,2 A | kesin |
| G20 | F6 | 18 AWG | F6 3 A standart (sigorta kutusu) (`F6`, 3 A) | etek 45 °C × 0,82 | 5,74 A | karara bağlı |
| G21 | F6 | 18 AWG | F6 3 A standart (sigorta kutusu) (`F6`, 3 A) | etek 45 °C × 0,82 | 5,74 A | kablajda teyit edilecek |
| G22 | anahtarli-bara | 22 AWG | Hat sigortası G22 2 A mini (bara ucunda) (`hat-G22`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kesin |
| I01 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kesin |
| I02 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kesin |
| K01 | F3 | 18 AWG | F3 5 A (sigorta kutusu) (`F3`, 5 A) | kafa 49 °C × 0,75 | 5,25 A | kesin |
| K02 | F3 | 18 AWG | F3 5 A (sigorta kutusu) (`F3`, 5 A) | kafa 49 °C × 0,75 | 5,25 A | kesin |
| K03 | F3 | 18 AWG | Pololu D24V50F5 aşırı akım koruması (`D24V50F5`, akım sınırı belgelenmemiş) | kafa 49 °C × 0,75 | 5,25 A (istisna: kafa-5v-donusturucu-arkasi) | kablajda teyit edilecek |
| K04 | F3 | — (kesit bilinmiyor) | SY8205 düşürücü (kafa ekranı) (`SY8205`, akım sınırı belgelenmemiş) | kafa 49 °C × 0,75 | — (istisna: kafa-5v-donusturucu-arkasi) | kablajda teyit edilecek |
| K05 | F3 | 18 AWG | Pololu D24V50F5 aşırı akım koruması (`D24V50F5`, akım sınırı belgelenmemiş) | kafa 49 °C × 0,75 | 5,25 A (istisna: kafa-5v-donusturucu-arkasi) | kablajda teyit edilecek |
| M01 | anahtarli-bara | — (kesit bilinmiyor) | BTS7960 sol (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sol`, akım sınırı belgelenmemiş) | etek 45 °C × 0,82 | — (istisna: motor-fabrika-kablosu) | kablajda teyit edilecek |
| M02 | anahtarli-bara | — (kesit bilinmiyor) | BTS7960 sol (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sol`, akım sınırı belgelenmemiş) | etek 45 °C × 0,82 | — (istisna: motor-fabrika-kablosu) | kablajda teyit edilecek |
| M03 | anahtarli-bara | — (kesit bilinmiyor) | BTS7960 sağ (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sag`, akım sınırı belgelenmemiş) | etek 45 °C × 0,82 | — (istisna: motor-fabrika-kablosu) | kablajda teyit edilecek |
| M04 | anahtarli-bara | — (kesit bilinmiyor) | BTS7960 sağ (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sag`, akım sınırı belgelenmemiş) | etek 45 °C × 0,82 | — (istisna: motor-fabrika-kablosu) | kablajda teyit edilecek |
| N01 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kablajda teyit edilecek |
| N02 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kablajda teyit edilecek |
| Q01 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kesin |
| Q02 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kesin |
| Q03 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kesin |
| S01 | anahtarli-bara | 22 AWG | XL4016 A akım sınırı (`XL4016-A`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S02 | anahtarli-bara | 22 AWG | XL4016 A akım sınırı (`XL4016-A`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S03 | anahtarli-bara | 22 AWG | XL4016 A akım sınırı (`XL4016-A`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S04 | anahtarli-bara | 22 AWG | XL4016 A akım sınırı (`XL4016-A`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S05 | anahtarli-bara | 22 AWG | XL4016 B akım sınırı (`XL4016-B`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S06 | anahtarli-bara | 22 AWG | XL4016 B akım sınırı (`XL4016-B`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S07 | anahtarli-bara | 22 AWG | XL4016 B akım sınırı (`XL4016-B`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S08 | anahtarli-bara | 22 AWG | XL4016 B akım sınırı (`XL4016-B`, 10 A) | etek 45 °C × 0,82 | 2,46 A (istisna: servo-uzatmasi) | kesin |
| S09 | anahtarli-bara | 22 AWG | XL4016 C akım sınırı (`XL4016-C`, 10 A) | kafa 49 °C × 0,75 | 2,25 A (istisna: servo-uzatmasi) | kesin |
| S10 | anahtarli-bara | 22 AWG | XL4016 C akım sınırı (`XL4016-C`, 10 A) | kafa 49 °C × 0,75 | 2,25 A (istisna: servo-uzatmasi) | kablajda teyit edilecek |
| SV1 | anahtarli-bara | 16 AWG | XL4016 A akım sınırı (`XL4016-A`, 10 A) | etek 45 °C × 0,82 | 8,2 A (istisna: servo-ana-hat-16awg) | kesin |
| SV2 | anahtarli-bara | 16 AWG | XL4016 B akım sınırı (`XL4016-B`, 10 A) | etek 45 °C × 0,82 | 8,2 A (istisna: servo-ana-hat-16awg) | kesin |
| SV3 | anahtarli-bara | 16 AWG | XL4016 C akım sınırı (`XL4016-C`, 10 A) | kafa 49 °C × 0,75 | 7,5 A (istisna: servo-ana-hat-16awg) | kesin |
| X01 | F4 | 22 AWG | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) | etek 45 °C × 0,82 | 2,46 A | kablajda teyit edilecek |

### Uç türleri: klemens, bara, lehim, fiş (O-3; düzeltme turu 2: her damar ucunun türü uc_turu alanında)

| Tür | Ne | En kalın kablo | Liste | Not |
|---|---|---|---|---|
| `bara-pabuc` | M5 cıvata saplama + yaylı pul + somun üstünde halka pabuç yığını, basılmış yalıtkan tutucuda (O-3 revize) | 6 mm² | `planlama/maliyet.json#kalemler.156` | Akım pabuçların yüz yüze temasından geçer (cıvata iletken sayılmaz); büyük akımlı (12 AWG) pabuçlar yığının altında, üstte düz pul + yaylı pul. Bir saplamada en çok 4 pabuç (ABYC E-11); saplamalar 12 AWG köprüyle bağlanır (köprünün iki ucu da birer pabuç; zincir köprüde n saplama n × 4 − 2(n − 1) pabuç alır). O-22 a (orkestratör kararı, 14.11): yıldız 5 saplama (12 yer, 11 iletken), anahtarlı bara 4 saplama (10 yer, 8 iletken); takım 9 + 1 yedek = 10. Köprüler: yıldız 4 + anahtarlı bara 3 = 7 adet 12 AWG (≈ 50 mm, iki ucu sarı halka pabuçlu): 14 sarı pabuç, 12 AWG siyah 4 × 0,05 = 0,2 m, kırmızı 3 × 0,05 = 0,15 m (kopruler alanı; malzeme sınamasına katılır). Kayıtlı açık iş (P10.7b): tutucu tasarlanırken sadeleştirme: saplamalar tek pirinç / bakır şerit üstünde (yıldız 3, bara 3 saplama) ya da pano tipi pirinç nötr barası; malzeme bulunursa. Tutucunun CAD'i P10.7b iş maddesi. Sarı pabuç JST R5.5-5 sınıfı 12–10 AWG için yapılmış (bağımsız kontrol §3.1); satıcı sayfası aralığı açık yazmıyor, teslimde bir deneme sıkışı. Kullanan: G05, G06, G09, G11, G12, G13, G14, G15, G16, G17, G18, G20, G22. |
| `wago-2273` | WAGO 2273-203 itmeli klemens (yalnız tek telli; tabloda kullanılmıyor) | 2,5 mm² | `planlama/maliyet.json#kalemler.62` | 0,5–2,5 mm², 24 A (Motorobit sayfası, 14.11 okundu; üretici verisi okunmadı); 12 AWG girmez (EL:93) Kullanan: -. |
| `klemens-508` | 2 pin 5,08 mm vidalı klemens (kartlarda; kafa girişi ve acil stop düğümü kartları dahil) | bilinmiyor | `planlama/maliyet.json#kalemler.80` | satıcı sayfasında kesit yazmıyor; 16 / 18 AWG uçlarda teslimde bakılır. 12 AWG bu klemense bağlanmaz (lehim / pabuç); denetim sınırı bilinmeyen klemense 12 AWG'yi reddeder Kullanan: A02, A03, A04, A05, G17, G19, K01, K02, SV1, SV2, SV3. |
| `bts-guc` | BTS7960 modülünün güç vidalı klemensi (B+ / B− / M+ / M−) | bilinmiyor | `planlama/maliyet.json#kalemler.45` | aldığı kesit satıcı sayfasında ve bakılan teknik sayfalarda yazmıyor (14.11); 12 AWG uç kablajda teyit edilir, almazsa çatal pabuç (kayıtta 'klemens:' ile başlayan teyit maddesi zorunlu) Kullanan: G12, G13, M01, M02, M03, M04. |
| `pabuc` | Cihaz saplamasına halka pabuç (akü kutbu, ana anahtar) | 6 mm² | `planlama/maliyet.json#kalemler.154` | sarı RV 5.5-5 (4–6 mm²); mavi / kırmızı pabuçlar daha ince kesit içindir Kullanan: G01, G03, G04, G06. |
| `modul-vidali` | Modülün kendi vidalı klemensi (XL4016, SY8205, göğüs regülatörü, PC817 modülü, mantar kontak bloğu) | bilinmiyor | `planlama/maliyet.json#kalemler.46` | aldığı kesit satıcı sayfalarında yazmıyor; 12 AWG bu klemense yalnız 'klemens:' teyidiyle Kullanan: A01, A02, A06, G14, G15, G16, G18, G19, G20, G21, G22, K02, K04, SV1, SV2, SV3. |
| `sigorta-kutusu` | 6 yollu sigorta kutusunun giriş / çıkış ucu | bilinmiyor | `planlama/maliyet.json#kalemler.51` | uç tipi ve aldığı kesit listede / belgede yazılı değil; teslimde bakılır (KT3). 12 AWG yalnız 'klemens:' teyidiyle Kullanan: A01, G04, G08, G10, G17, G18, G20. |
| `lehim` | Lehim (kuyruk, pim, pad, ek) + makaron | klemens değil | — | klemens değil; kesit sınırı yok Kullanan: A02, A03, A06, AU1, AU2, AU3, G01, G02, G03, G05, G06, G07, G08, G09, G10, G11, K01, K03, K05. |
| `konnektor` | Hazır fiş / başlık / jumper ucu / cihazın kendi kablosu | klemens değil | — | klemens değil; hazır kablo ya da fiş Kullanan: AU1, B01, B02, C01, G21, H01, H02, I01, I02, K04, M01, M02, M03, M04, N01, N02, P01, P02, P03, Q01, Q02, Q03, S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, U01, U03, U04, U05, U06, X01. |

## Malzeme özeti (sipariş)

Boy belliyse CAD / liste boyu, değilse kaba üst sınır tahmini; toplam × 1,3 (%30 pay) `planlama/maliyet.json` adediyle karşılaştırılır (denetimde `malzeme` sınaması). Tahminler P10.7b'de ölçülecek.

| Tür | Renk | İhtiyaç | × pay | Listede | Kalem |
|---|---|---|---|---|---|
| 22 AWG servo uzatması (100 cm parça) | hepsi | 17,52 m | 22,8 m | 23 × 1 m | 19: Servo uzatma kablosu |
| 12 AWG silikon kablo | kırmızı | 3,65 m | 4,7 m | 5 m | 57: Silikon kablo 12 AWG |
| 12 AWG silikon kablo | siyah | 1,8 m | 2,3 m | 3 m | 58: Silikon kablo 12 AWG |
| 16 AWG silikon kablo | kırmızı | 3,1 m | 4 m | 5 m | 83: Silikon kablo 16 AWG |
| 16 AWG silikon kablo | siyah | 3,1 m | 4 m | 5 m | 84: Silikon kablo 16 AWG |
| 18 AWG silikon kablo | kırmızı | 8,25 m | 10,7 m | 11 m | 59: Silikon kablo 18 AWG |
| 18 AWG silikon kablo | siyah | 7,05 m | 9,2 m | 10 m | 60: Silikon kablo 18 AWG |
| 22 AWG çok telli sinyal teli | hepsi | 26,35 m | 34,3 m | 3 × 15 m | 157: Sinyal teli 22 AWG (fiyat bekliyor) |

## Orkestratör kararları (14.11)

| Kod | Karar | Metin | Tabloda uygulama | Veren |
|---|---|---|---|---|
| O-1 | c | Yalnız listedeki kesitler (12 / 16 / 18 AWG); her dal koruyanına O-2 tablosuyla yeten en ince kesiti alır; akımı sınırlayan elemanla korunan kısa kollar o elemanın akımına göre, öncesi sigortaya göre. Gerilim düşümü P10.7b'de (> %3 ise bir kalın kesit). | G08–G13, G17–G21, A01–A05, K01, K02, K05 kesit aldı; G11'de direnç kuralı uygulanmadı (bara öbür yandan F1 ile besler, 12 AWG); M01–M04 motorun kendi kablosu: kayıtlı istisna motor-fabrika-kablosu (O-16). | orkestratör, 14.11.2026 |
| O-2 | a + b | Kaynağı gösterilen akım tablosu (iki kaynak farklıysa temkinli olanı); dönüştürücü sonrası kablolarda sınır ≤ tablodaki akım; servo uzatmaları kayıtlı istisna. | kesit_kurali: 33 CFR 183.425 (80 °C) ve NFPA 79 Table 12.5.1 (75 °C); temkinli değerler 12 AWG 25 A, 16 AWG 10 A, 18 AWG 7 A, 20 AWG 5 A, 22 AWG 3 A. 12 AWG'nin 25 A'i ana hattın 30 A'iyle çelişiyor (O-15). Üçüncü turda kayıtlı istisna ana-hat-12awg (O-15). | orkestratör, 14.11.2026 |
| O-3 | a, yoksa b | 12 AWG giren düğümlerde 6 mm² kollu yaylı klemens (WAGO 221-61x); onaylı satıcılarda yoksa saplamalı bara + 12 AWG halka pabuç; ince düğümlerde 2273. | 221-61x onaylı dört satıcıda bulunamadı → b. Üçüncü turda revize: hazır bara alınmaz; M5 saplama + yaylı pul + somun üstünde pabuç yığını, basılmış tutucuda (yıldız 3, anahtarlı bara 2 saplama). | orkestratör, 14.11.2026 |
| O-4 | a + b | Kalıcı sinyal kablajı 22–24 AWG çok telli renkli tel + Dupont gövde / uç; masa testleri için jumper seti. Pense yoksa lehim + makaron. | 16 sinyal kaydı 22 AWG; 22 AWG rulo onaylı satıcılarda stokta yok (fiyat bekliyor). Üçüncü turda revize: Dupont kiti çıktı (pense yok); uçlar hazır jumper kablolarının fabrika sıkılı dişi uçları (ortadan kesilir, sinyal teline lehim + makaron; kısa mesafede jumper doğrudan). | orkestratör, 14.11.2026 |
| O-5 | a | Akü bölücüsünün üst direnci ve PC817 #2'nin seri direnci telin kaynak ucuna. | G07 uygulandı (100 kΩ ana anahtar çıkışında). G22 uygulanamadı: PC817 #2 hazır modül; yerine O-18 b (2 A hat sigortası). | orkestratör, 14.11.2026 |
| O-6 | a / c | Acil stop düğümü güç panelinde çok çıkışlı klemens; mantar ile düğüm arasında Ö4 için köprülü iki uçlu yer. Ö4 açık (Ahmet + Efe). | A02, A04, A06; düğüm 2273-203 × 2, Ö4 yeri 2 pin klemens köprülü. | orkestratör, 14.11.2026 |
| O-7 | a | BTS VCC çevre 5 V'tan, çevre 5 V dağıtımı ve EN pull-down arayüz kartında; BTS VCC kart gelince teyit. | B01, B02, G19, X01. | orkestratör, 14.11.2026 |
| O-8 | kol yöntemi | Pan / tilt kollardaki gibi bağlanır; kollarda yazılı değilse XL4016 C yanında 3 pinli küçük dağıtım. | Kollarda yöntem yazılı: dağıtım kartı (EL:225, 16 AWG klemens → V+ / GND barası → 2200 µF → 3 pinli çıkışlar, sinyal PCA'dan köprü). Kafa için aynı: dağıtım kartı C (SV3, P03, S09, S10). | orkestratör, 14.11.2026 |
| O-9 | a | Ses bölücüsü PAM8403 giriş pedlerinin dibinde, kablo üstünde, makaronla. | AU2. | orkestratör, 14.11.2026 |
| O-10 | b | K4 Ahmet'in kayıtlı kararı, değişmez (koşullu, sipariş yine verilir). | U01, U03, AU1, AU3. | orkestratör, 14.11.2026 |
| O-11 | b | Mevcut satırlar alınır, teslimde ölçülür; onaylı satıcı dışı Ahmet'in kararı. | H02, U03 kablajda teyit. | orkestratör, 14.11.2026 |
| O-12 | açık | Bas-konuş düğmesi Efe'ye sorulacak; tabloya kablo eklenmez, sipariş kalemi değişmez. | - | orkestratör, 14.11.2026 |
| O-13 | metin | Şarj hedefi 14,4 V (4 × 3,6 V); 14,6 V yalnız en kötü durum hesap değeri. Şarj cihazı kalır; ilk şarjda kesme gerilimi ölçülür, > 14,4 V ise kullanılmaz. | elektrik.md:67, :93, :282; T7; kablolama-on-kararlar.md KT8. | orkestratör, 14.11.2026 |
| O-14 | a | Bugünkü yazılım kuralı + watchdog kalır, kablaj değişmez; kendini tutma kontağı / Ö4 açık (Ahmet + Efe). | tablo bugünkü devreyi taşır. | orkestratör, 14.11.2026 |
| O-15 | istisna | Ana hat 12 AWG / 30 A değişmez; adıyla kayıtlı istisna ana-hat-12awg (gerekçe, şart, beklenen sürekli akım). | G01–G05 kablajda teyit. | orkestratör kararı, 14.11.2026 |
| O-16 | istisna | Motorun fabrika kablosu değiştirilmez; kayıtlı istisna motor-fabrika-kablosu; uzatma gerekirse 12 AWG; 18 AWG'den inceyse orkestratöre. | M01–M04 kablajda teyit. | orkestratör kararı, 14.11.2026 |
| O-17 | uçlar | + ana sigortanın yük tarafı / ana anahtarın akü tarafı, − yıldız; 10 A sigorta akü tarafındaki ucun dibinde; akü ayrı şarj ucuyla gelirse o. | G06 kablajda teyit. | orkestratör kararı, 14.11.2026 |
| O-18 | b | G22'nin bara ucunda hat sigortası yuvası + 2 A bıçak. | G22; hat yuvası 4 → 5, 2 A mini +1 (yuva mini bıçak alır). | orkestratör kararı, 14.11.2026 |
| O-3 r | revize | Hazır güç barası alınmaz; M5 saplama + yaylı pul + somun üstünde pabuç yığını, basılmış tutucu (CAD P10.7b); saplamada ≤ 5 pabuç, fazlası 12 AWG köprü. | klemens_turleri.bara-pabuc; maliyet.json 'Güç barası' satırı saplama takımına çevrildi. | orkestratör kararı, 14.11.2026 |
| O-4 r | revize | Dupont kiti çıkar; uç olarak jumper kablolarının fabrika sıkılı dişi uçları; jumper adedi dişi uç sayısı + %30. | maliyet.json; uç sayımı günlükte. | orkestratör kararı, 14.11.2026 |
| D1-1 | uygulandı (sayı O-22 a ile) | Saplama başına en çok 4 pabuç (ABYC E-11) uygulandı. 'Yıldız 4, anahtarlı bara 3 saplama' sığmadı; O-22 a: yıldız 5, anahtarlı bara 4 saplama. | klemens_turleri.bara-pabuc: sınır 4; 5 + 4 saplama (O-22 a); maliyet.json bara saplaması 6 → 10. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-2 | uygulandı | XL4016 sınırı çipin anahtar akım sınırı (≈ 10 A); 8 A modül anması ayrı; servo uzatması istisnasına tezgâh kısa devre şartı. | koruyucular.XL4016-*; kesit_kurali.istisnalar.servo-uzatmasi.sart; SV1–SV3 ve G19 kuralı geçmiyor → O-19 / O-20. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-3 | uygulandı | motor-fabrika-kablosu gerekçesi: F1 korumaz; motor sargısı + BTS7960 akım sınırlama / ısıl kapatma + yazılım IS → EN. | istisna gerekçesi; M01–M04 koruması BTS7960; Efe'ye bildirilecek listesi (günlük). | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-4 | uygulandı | Kesit kuralına ortam düzeltmesi (etek 45 °C 0,82; kafa 49 °C 0,75); G06 şarj sigortası 10 → 7,5 A; K03 20 → 18 AWG. | kesit_kurali.ortam; koruyucular.hat-sarj; K03. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-5 | uygulandı | D24V50F5 '5 A' anma; akım sınırı belgelenmemiş; K03 / K05 kayıtlı istisna kafa-5v-donusturucu-arkasi. | koruyucular.D24V50F5 (akim_a boş); kesit_kurali.istisnalar. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-6 | uygulandı | 1N4007 iki rölede bobin uçlarının dibinde, katot bobinin + ucuna. | A03, A05 sonlandırma; elektrik.md E9 satırı. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-7 | uygulandı | 12 AWG onu almayan klemense girmez; G10 K2 pimine lehim, G11 direnç bacağına lehim; BTS güç klemensi teyitli. | G10–G13; klemens_turleri.bts-guc; denetim 'öneri' ve yer tutucuları kesin kayıtta yakalar. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| D1-9 | onay | Dağıtım kartı C (kafa servoları, O-8'in kafaya genişletilmesi) ve renk kuralı (+ kırmızı, − / GND siyah) onaylandı. | orkestratör onayı 14.11; elektrik.md:129 / :330 düzeltildi. | orkestratör kararı, 14.11.2026 (düzeltme turu 1) |
| O-19 | a | 5 V çevre hattı: XL4016 çevre çıkışında, G19'un XL ucunun dibinde 2 A mini hat sigortası. | koruyucular.hat-cevre (yük bütçesi ve açılış hesabı kayıtta); G19 + damarı ara_koruyucu; G19, X01, B01, B02, N01, N02, I01, I02, Q01–Q03 koruması hat-cevre; maliyet.json hat yuvası 5 → 6, 2 A mini 1 → 2. | orkestratör kararı, 14.11.2026 |
| O-20 | c | SV1–SV3: kayıtlı istisna servo-ana-hat-16awg; çıkışa sigorta konmaz. | kesit_kurali.istisnalar.servo-ana-hat-16awg (beklenen akım bütçesi; şart T8 E + gerilim düşümü P10.7b). | orkestratör kararı, 14.11.2026 |
| O-21 | a | K04: kafa-5v-donusturucu-arkasi istisnası genişler; teslimde kesit yazısı okunur, 24 AWG'den inceyse ya da yazı yoksa 18 AWG + micro B. | istisna kapsamı K03, K05, K04; K04 teyit maddesi, durum kablajda teyit; kafa ekranı akımı K04 notunda. | orkestratör kararı, 14.11.2026 |
| O-22 | a | Yıldız 5 saplama (12 yer, 11 iletken), anahtarlı bara 4 saplama (10 yer, 8 iletken); takım 9 + 1 yedek = 10; şerit / nötr barası sadeleştirmesi P10.7b açık işi. | klemens_turleri.bara-pabuc (dugumler, kopruler); maliyet.json sarı pabuç 3 → 4 paket. | orkestratör kararı, 14.11.2026 |
| D1-10 | onay | Ajanın kendi seçimleri onaylandı: ortam bölgesinin demetten atanması, O-18'de 2 A mini, F8a karşılaştırma tabanı 76fd4b2. | orkestratör onayı 14.11; günlük §15. | orkestratör kararı, 14.11.2026 |

## Acil stop dalları ve besleme zinciri

Dal ve acil stop bayrağı her kablonun `besleme_zinciri`nden türetilir (aküden kabloya koruyucular / anahtarlar); zincirde kontak ya da mantar türünde bir eleman varsa kablo acil stopta enerjisizdir. Denetim zinciri devrenin ağlarından yeniden kurar ve `planlama/adim3/kablolama-on-kararlar.md §12` listesiyle karşılaştırır.

| Dal | Tanımlayan eleman | §12'deki ifade | Kablo |
|---|---|---|---|
| aku-ana | `aku-bms` | sigorta kutusu baraları | 5 |
| sarj | `hat-sarj` | şarj girişi | 1 |
| aku-olcum | `R-aku-olcum` | akü ölçüm bölücüsü | 1 |
| F1-kontak-oncesi | `F1` | F1 çıkışından K1 / K2 kontak girişine kadarki hat | 2 |
| anahtarli-bara | `K1-kontak` | röle K1 / K2 kontağından sonraki anahtarlı bara | 25 |
| F3 | `F3` | F3 kafa dalı | 17 |
| F4 | `F4` | F4 çevre 5 V | 15 |
| F5-mantar-oncesi | `F5` | F5'ten mantar NC'ye kadarki hat | 1 |
| mantar-sonrasi | `mantar` | mantar NC çıkışından sonraki hat | 5 |
| F6 | `F6` | F6 göğüs ekranı dalı | 2 |

### Koruyucular ve anahtarlar

| Kimlik | Ne | Tür | Akım sınırı | Giriş ağı → çıkış ağı | Kaynak |
|---|---|---|---|---|---|
| `aku-bms` | Akü BMS (Victron SuperPack, 30 A sürekli) | bms | 30 A | kök → aku+ | `planlama/adim3/elektrik.md:323` |
| `ana-sigorta` | Ana sigorta 30 A (standart bıçak, kablolu yuva) | sigorta | 30 A | aku+ → ana-sigorta-cikis | `planlama/adim3/elektrik.md:364` |
| `F1` | F1 20 A (sigorta kutusu) | sigorta | 20 A | ana-anahtar-cikis → f1-cikis | `planlama/adim3/elektrik.md:365` |
| `F3` | F3 5 A (sigorta kutusu) | sigorta | 5 A | ana-anahtar-cikis → f3-cikis | `planlama/adim3/elektrik.md:367` |
| `F4` | F4 5 A (sigorta kutusu) | sigorta | 5 A | ana-anahtar-cikis → f4-cikis | `planlama/adim3/elektrik.md:368` |
| `F5` | F5 2 A (sigorta kutusu) | sigorta | 2 A | ana-anahtar-cikis → f5-cikis | `planlama/adim3/elektrik.md:369` |
| `F6` | F6 3 A standart (sigorta kutusu) | sigorta | 3 A | ana-anahtar-cikis → f6-cikis | `planlama/adim3/elektrik.md:371` |
| `hat-A` | Hat sigortası A 7,5 A mini (XL4016 A girişi) | sigorta | 7,5 A | anahtarli-bara → xl-a-giris | `planlama/adim3/elektrik.md:370` |
| `hat-B` | Hat sigortası B 7,5 A mini (XL4016 B girişi) | sigorta | 7,5 A | anahtarli-bara → xl-b-giris | `planlama/adim3/elektrik.md:370` |
| `hat-C` | Hat sigortası C 5 A mini (XL4016 C girişi) | sigorta | 5 A | anahtarli-bara → xl-c-giris | `planlama/adim3/elektrik.md:370` |
| `hat-G22` | Hat sigortası G22 2 A mini (bara ucunda) | sigorta | 2 A | anahtarli-bara → g22-algi | `planlama/adim3/elektrik.md:370` |
| `hat-sarj` | Şarj hat sigortası 7,5 A mini (akü tarafındaki ucun dibinde) (ortam düzeltmeli 16 AWG sınırı 8,2 A; IMAX B6 en çok 5 A × 1,25 = 6,25 A ≤ 7,5 A) | sigorta | 7,5 A | ana-sigorta-cikis → sarj-girisi | `planlama/adim3/elektrik.md:372` |
| `XL4016-A` | XL4016 A akım sınırı (anma: 8 A modül (satıcı: en çok 8 A, sürekli 5 A); çipin anahtar akım sınırı (Switch Current Limit, IL, VFB = 0) **10 A tipik**; en az / en çok değeri verilmiyor. Birincil kaynak: XLSEMI XL4016 veri sayfası Rev 1.2 ('8A 180KHz 40V Buck DC to DC Converter'), s. 5 'Electrical Characteristics (DC Parameters)' (https://static.chipdip.ru/lib/173/DOC013173704.pdf, 14.11 okundu). Sonraki revizyonların bir kısmı '12A' başlıklı (Rev 1.3; açılamadı): o sürümde sınır daha yüksekse kural sonucu yalnız kötüleşir. '8 A' modülün / çipin anma değeridir, sınır değil) | donusturucu | 10 A | xl-a-giris → servo-a | `planlama/adim3/elektrik.md:222` |
| `XL4016-B` | XL4016 B akım sınırı (anma: 8 A modül (satıcı: en çok 8 A, sürekli 5 A); çipin anahtar akım sınırı (Switch Current Limit, IL, VFB = 0) **10 A tipik**; en az / en çok değeri verilmiyor. Birincil kaynak: XLSEMI XL4016 veri sayfası Rev 1.2 ('8A 180KHz 40V Buck DC to DC Converter'), s. 5 'Electrical Characteristics (DC Parameters)' (https://static.chipdip.ru/lib/173/DOC013173704.pdf, 14.11 okundu). Sonraki revizyonların bir kısmı '12A' başlıklı (Rev 1.3; açılamadı): o sürümde sınır daha yüksekse kural sonucu yalnız kötüleşir. '8 A' modülün / çipin anma değeridir, sınır değil) | donusturucu | 10 A | xl-b-giris → servo-b | `planlama/adim3/elektrik.md:222` |
| `XL4016-C` | XL4016 C akım sınırı (anma: 8 A modül (satıcı: en çok 8 A, sürekli 5 A); çipin anahtar akım sınırı (Switch Current Limit, IL, VFB = 0) **10 A tipik**; en az / en çok değeri verilmiyor. Birincil kaynak: XLSEMI XL4016 veri sayfası Rev 1.2 ('8A 180KHz 40V Buck DC to DC Converter'), s. 5 'Electrical Characteristics (DC Parameters)' (https://static.chipdip.ru/lib/173/DOC013173704.pdf, 14.11 okundu). Sonraki revizyonların bir kısmı '12A' başlıklı (Rev 1.3; açılamadı): o sürümde sınır daha yüksekse kural sonucu yalnız kötüleşir. '8 A' modülün / çipin anma değeridir, sınır değil) | donusturucu | 10 A | xl-c-giris → servo-c | `planlama/adim3/elektrik.md:222` |
| `XL4016-cevre` | XL4016 çevre akım sınırı (anma: 8 A modül (satıcı: en çok 8 A, sürekli 5 A); çipin anahtar akım sınırı (Switch Current Limit, IL, VFB = 0) **10 A tipik**; en az / en çok değeri verilmiyor. Birincil kaynak: XLSEMI XL4016 veri sayfası Rev 1.2 ('8A 180KHz 40V Buck DC to DC Converter'), s. 5 'Electrical Characteristics (DC Parameters)' (https://static.chipdip.ru/lib/173/DOC013173704.pdf, 14.11 okundu). Sonraki revizyonların bir kısmı '12A' başlıklı (Rev 1.3; açılamadı): o sürümde sınır daha yüksekse kural sonucu yalnız kötüleşir. '8 A' modülün / çipin anma değeridir, sınır değil) | donusturucu | 10 A | f4-cikis → xl-cevre-cikis | `planlama/adim3/elektrik.md:222` |
| `hat-cevre` | Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) | sigorta | 2 A | xl-cevre-cikis → 5v-cevre | `planlama/maliyet.json#kalemler.86` |
| `D24V50F5` | Pololu D24V50F5 aşırı akım koruması (anma: 5 A (tipik en çok sürekli çıkış akımı; bir sınır değil); Pololu ürün sayfası (https://www.pololu.com/product/2851, 14.11): 'over-current and short-circuit protection, over-temperature shutoff'; eşik sayı olarak yazılmıyor, 'the current threshold decreases as the regulator temperature goes up'. Akım sınırı belgelenmemiş: kesit sınaması yapılamaz) | donusturucu | belgelenmemiş | f3-cikis → 5v-pi | `planlama/maliyet.json#kalemler.64` |
| `SY8205` | SY8205 düşürücü (kafa ekranı) (anma: 3,7 A sürekli (satıcı sayfası); satıcı sayfasında koruma / akım sınırı yazmıyor) | donusturucu | belgelenmemiş | f3-cikis → 5v-ekran | `planlama/adim3/elektrik.md:25` |
| `BTS7960-sol` | BTS7960 sol (aşırı akım sınırlama + ısıl kapatma) (anma: tepe akım yeteneği en az 33 A (Infineon veri sayfası özellik listesi); Infineon BTS7960 veri sayfası (https://components101.com/sites/default/files/component_datasheet/BTS7960B-Datasheet.pdf, 14.11): 'switched mode current limitation', 'overtemperature shut down with latch behaviour', IS ucunda akım ölçümü / durum bayrağı; sınırlama değeri tablodan okunamadı (belgelerde 43 A: raporlar/kaynaklar/01-donanim-maliyet.md:122)) | surucu | belgelenmemiş | anahtarli-bara → bts-sol-m+, bts-sol-m− | `planlama/maliyet.json#kalemler.45` |
| `BTS7960-sag` | BTS7960 sağ (aşırı akım sınırlama + ısıl kapatma) (anma: tepe akım yeteneği en az 33 A (Infineon veri sayfası özellik listesi); BTS7960-sol ile aynı) | surucu | belgelenmemiş | anahtarli-bara → bts-sag-m+, bts-sag-m− | `planlama/maliyet.json#kalemler.45` |
| `R-aku-olcum` | Akü ölçüm bölücüsünün üst direnci 100 kΩ (kaynak ucunda) | direnc | 0,00015 A | ana-anahtar-cikis → aku-olcum | `planlama/adim3/elektrik.md:234` |
| `ana-anahtar` | Ana anahtar (elle) | anahtar | — | ana-sigorta-cikis → ana-anahtar-cikis | `planlama/adim3/elektrik.md:323` |
| `K1-kontak` | Röle K1 kontağı (30 → 87) | kontak | — | f1-cikis → anahtarli-bara | `planlama/adim3/elektrik.md:441` |
| `K2-kontak` | Ön şarj kolu: K2 kontağı + 5,6 Ω (ön şarj kartı) | kontak | — | f1-cikis → anahtarli-bara | `planlama/adim3/elektrik.md:442` |
| `mantar` | Acil stop mantarı NC kontağı | mantar | — | f5-cikis → mantar-sonrasi | `planlama/adim3/elektrik.md:443` |
| `K1-bobin` | Röle K1 bobini (86 → 85) | bobin | — | mantar-sonrasi → k1-bobin-alt | `planlama/adim3/elektrik.md:443` |
| `K2-bobin` | Röle K2 bobini | bobin | — | mantar-sonrasi → k2-bobin-alt | `planlama/adim3/elektrik.md:444` |
| `gogus-regulatoru` | Göğüs regülatörü (LM2577 + LM2596, 12 → 12 V) (çıkış akımı girişten büyük olamaz varsayımı (yükseltip düşürür, 12 → 12 V): koruma F6'dan devralınır) | gecis | — | f6-cikis → gogus-12v | `planlama/adim3/elektrik.md:371` |
| `esp32-3v3` | ESP32 kartının 3V3 regülatörü (doğrusal regülatör varsayımı (çıkış akımı = giriş akımı): koruma 5 V çevreden devralınır; kart gelince regülatörün türü okunur) | gecis | — | 5v-cevre → 3v3 | `planlama/maliyet.json#kalemler.26` |

**`hat-cevre` yük bütçesi** (orkestratör kararı, 14.11.2026 (O-19 a); G19'un + damarında, XL4016 çevre OUT+ ucunun dibinde (taban alt kat, güç paneli)). 5 V çevre hattının yükü kalem kalem (5 V tarafı; 3V3 yükleri ESP32 kartının doğrusal regülatöründen geçtiği için aynı akımla 5 V'tan çekilir). Hesap, ölçülmedi.

| Yük | Tipik | Tepe | Kaynak |
|---|---|---|---|
| ESP32 geliştirme kartı (WROOM-32 + CP2102 + LED) | 0,24 A | 0,5 A | tipik: planlama/adim3/elektrik.md:353 (E4, 0,24 A); tepe: Espressif ESP32-WROOM-32E veri sayfası v2.1 Tablo 16, Wi-Fi TX 802.11b 19,5 dBm ortalama 239 / tepe 379 mA, Tablo 14 'current delivered by external power supply' en az 0,5 A (14.11 okundu); tepe olarak kaynağın en az vermesi istenen 0,5 A alındı (CP2102 ve LED dahil, temkinli) |
| HC-SR04 × 3 | 0,045 A | 0,045 A | çalışma akımı 15 mA / adet (yaygın HC-SR04 veri sayfası değeri; bu turda birincil kaynak açılmadı) |
| BNO055 (3V3) | 0,0123 A | 0,0123 A | normal mod 12,3 mA (Bosch BNO055 veri sayfası değeri; bu turda açılmadı) |
| PCA9685 mantık (3V3) | 0,006 A | 0,01 A | IDD 6 mA tipik / 10 mA en çok (NXP PCA9685 veri sayfası değeri; bu turda açılmadı); servo akımı XL4016 A / B / C'den |
| JGB37 enkoder × 2 (3V3) | 0,02 A | 0,02 A | tahmin, 10 mA / adet (Hall sensörlü enkoder; satıcı sayfasında akım yok) |
| BTS7960 modülü mantık VCC × 2 | 0,02 A | 0,02 A | tahmin, 10 mA / modül (giriş tamponu + güç LED'i; satıcı sayfasında akım yok) |
| PC817 modülü çıkış tarafı (3V3) | 0,001 A | 0,005 A | çekme direnci 3,3 V / 10 kΩ = 0,33 mA × 2 (elektrik.md:244) + modül LED'i (tahmin) |
| **Toplam** | **0,344 A** | **0,612 A** | |

**Açılış:** Sigorta XL4016 çıkışından sonra: açılışta yalnız aşağı akıştaki küçük kondansatörler (ESP32 kartı, modüller; tahmini ≤ 200 µF, çevre hattında 2200 µF yok) dolar: Q ≤ 200 µF × 5 V = 1 mC. En kötü durumda XL4016'nın 10 A sınırıyla dolsa bile ≈ 0,1 ms, I²t ≈ 10² × 1e-4 = 0,01 A²s; 2 A mini bıçak sigortanın erime I²t'si bakılan üretici değerlerinde 2,8–9 A²s (Littelfuse MINI 297, 0297002; listedeki sigorta Motorobit'in alçak profil minisi, kendi değeri yok). Ayrıca XL4016 çıkışı yumuşak açılır. **Pay:** tepe 0,61 A = sigorta anmasının %31'i; mini bıçak sigorta %110'da açmaz, %200'de (4 A) en erken 0,15 s'de açar (Littelfuse MINI 32 V zaman-akım tablosu, arama özetinden). Sonar ve Wi-Fi tepeleri birlikte gelse de 2 A'e yaklaşmaz: 3 A'e gerek yok. 22 AWG damarların 45 °C düzeltmeli sınırı 2,46 A ≥ 2 A.

## Demet demet (montaj sırasıyla)

Her kablo: devre, iki uç, damarlar uç uç, kesit, renk, koruma, acil stop, boy, rehber adımı, durum ve kaynak.
Rehber adımı: bugünkü rehber metninde geçen adım; "öneri" yazanlar önerilen adım.

### taban alt kat (12)

#### M01 · BTS7960 sol → ön sol JGB37 (motor uçları)

- **Devre:** motor (anahtarlı bara) · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** BTS7960 sol (M+ / M−) → JGB37-520 ön sol (motor + / −)
- **Kesit:** — (motorun kendi kablosu (6 damarlı, enkoderle ortak); kesit motor gelince okunur ve buraya yazılır (O-16)) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** BTS7960 sol (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sol`, akım sınırı belgelenmemiş) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → BTS7960-sol
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 145 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 7 B2b, 9 B3 · **sonlandırma:** BTS vidalı klemens; aynı yandaki iki motor aynı M+ / M− klemensine paralel
- **Uç türü (uc_turu):** a: bts-guc · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| M+ | BTS7960 sol · M+ | JGB37 ön sol · motor + |  |
| M− | BTS7960 sol · M− | JGB37 ön sol · motor − |  |

- Teyit: motor gelince kablo kesiti okunur ve tabloya yazılır; 18 AWG'den inceyse orkestratöre; uzatma gerekirse 12 AWG (O-16)
- Not: Koruma: ince motor kablosunu F1 korumaz. Sürekli akımı motor sargısı sınırlar (durma akımı 2,8 A, tahmini, EL:157); kablo içi kısa devrede koruma BTS7960'ın anahtarlamalı akım sınırlaması + mandallı ısıl kapatması (veri sayfası) ve yazılımın IS akım ölçümü arıza bayrağında EN'i kesmesi (firmware şartı, Efe'ye bildirilecek).
- Kaynak: `planlama/adim3/elektrik.md:326-327`, `planlama/adim3/elektrik.md:352` · 10.11 dökümü: #12

#### M02 · BTS7960 sol → arka sol JGB37 (motor uçları)

- **Devre:** motor (anahtarlı bara) · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** BTS7960 sol (M+ / M−) → JGB37-520 arka sol (motor + / −)
- **Kesit:** — (motorun kendi kablosu (6 damarlı, enkoderle ortak); kesit motor gelince okunur ve buraya yazılır (O-16)) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** BTS7960 sol (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sol`, akım sınırı belgelenmemiş) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → BTS7960-sol
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 600 mm; Manhattan 477 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 7 B2b, 9 B3 · **sonlandırma:** BTS vidalı klemens; aynı yandaki iki motor aynı M+ / M− klemensine paralel
- **Uç türü (uc_turu):** a: bts-guc · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| M+ | BTS7960 sol · M+ | JGB37 arka sol · motor + |  |
| M− | BTS7960 sol · M− | JGB37 arka sol · motor − |  |

- Teyit: motor gelince kablo kesiti okunur ve tabloya yazılır; 18 AWG'den inceyse orkestratöre; uzatma gerekirse 12 AWG (O-16)
- Not: Koruma: ince motor kablosunu F1 korumaz. Sürekli akımı motor sargısı sınırlar (durma akımı 2,8 A, tahmini, EL:157); kablo içi kısa devrede koruma BTS7960'ın anahtarlamalı akım sınırlaması + mandallı ısıl kapatması (veri sayfası) ve yazılımın IS akım ölçümü arıza bayrağında EN'i kesmesi (firmware şartı, Efe'ye bildirilecek).
- Kaynak: `planlama/adim3/elektrik.md:326-327`, `planlama/adim3/elektrik.md:352` · 10.11 dökümü: #13

#### M03 · BTS7960 sağ → ön sağ JGB37 (motor uçları)

- **Devre:** motor (anahtarlı bara) · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** BTS7960 sağ (M+ / M−) → JGB37-520 ön sağ (motor + / −)
- **Kesit:** — (motorun kendi kablosu (6 damarlı, enkoderle ortak); kesit motor gelince okunur ve buraya yazılır (O-16)) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** BTS7960 sağ (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sag`, akım sınırı belgelenmemiş) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → BTS7960-sag
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 145 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 7 B2b, 9 B3 · **sonlandırma:** BTS vidalı klemens; aynı yandaki iki motor aynı M+ / M− klemensine paralel
- **Uç türü (uc_turu):** a: bts-guc · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| M+ | BTS7960 sağ · M+ | JGB37 ön sağ · motor + |  |
| M− | BTS7960 sağ · M− | JGB37 ön sağ · motor − |  |

- Teyit: motor gelince kablo kesiti okunur ve tabloya yazılır; 18 AWG'den inceyse orkestratöre; uzatma gerekirse 12 AWG (O-16)
- Not: Koruma: ince motor kablosunu F1 korumaz. Sürekli akımı motor sargısı sınırlar (durma akımı 2,8 A, tahmini, EL:157); kablo içi kısa devrede koruma BTS7960'ın anahtarlamalı akım sınırlaması + mandallı ısıl kapatması (veri sayfası) ve yazılımın IS akım ölçümü arıza bayrağında EN'i kesmesi (firmware şartı, Efe'ye bildirilecek).
- Kaynak: `planlama/adim3/elektrik.md:326-327`, `planlama/adim3/elektrik.md:352` · 10.11 dökümü: #14

#### M04 · BTS7960 sağ → arka sağ JGB37 (motor uçları)

- **Devre:** motor (anahtarlı bara) · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** BTS7960 sağ (M+ / M−) → JGB37-520 arka sağ (motor + / −)
- **Kesit:** — (motorun kendi kablosu (6 damarlı, enkoderle ortak); kesit motor gelince okunur ve buraya yazılır (O-16)) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** BTS7960 sağ (aşırı akım sınırlama + ısıl kapatma) (`BTS7960-sag`, akım sınırı belgelenmemiş) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → BTS7960-sag
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 600 mm; Manhattan 476 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 7 B2b, 9 B3 · **sonlandırma:** BTS vidalı klemens; aynı yandaki iki motor aynı M+ / M− klemensine paralel
- **Uç türü (uc_turu):** a: bts-guc · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| M+ | BTS7960 sağ · M+ | JGB37 arka sağ · motor + |  |
| M− | BTS7960 sağ · M− | JGB37 arka sağ · motor − |  |

- Teyit: motor gelince kablo kesiti okunur ve tabloya yazılır; 18 AWG'den inceyse orkestratöre; uzatma gerekirse 12 AWG (O-16)
- Not: Koruma: ince motor kablosunu F1 korumaz. Sürekli akımı motor sargısı sınırlar (durma akımı 2,8 A, tahmini, EL:157); kablo içi kısa devrede koruma BTS7960'ın anahtarlamalı akım sınırlaması + mandallı ısıl kapatması (veri sayfası) ve yazılımın IS akım ölçümü arıza bayrağında EN'i kesmesi (firmware şartı, Efe'ye bildirilecek).
- Kaynak: `planlama/adim3/elektrik.md:326-327`, `planlama/adim3/elektrik.md:352` · 10.11 dökümü: #15

#### G12 · Anahtarlı bara → BTS7960 sol (B+ / B−)

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Anahtarlı bara (+) → BTS7960 sol (B+ / B−)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** F1 20 A (sigorta kutusu) (`F1`, 20 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak)
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 650 mm; Manhattan 510 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara / yıldız → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** BTS vidalı güç klemensi (B+ / B−); bara ucu sarı M5 halka pabuç, saplamada
- **Uç türü (uc_turu):** a: bara-pabuc, bts-guc · b: bara-pabuc, bts-guc

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Anahtarlı bara · + | BTS7960 sol · B+ |  |
| − | BTS7960 sol · B− | Yıldız barası · GND |  |

- Teyit: klemens: BTS7960 güç klemensinin aldığı kesit satıcı sayfasında yok; kablajda teyit, almazsa çatal pabuç
- Teyit: güç barası tutucusu (CAD P10.7b): saplama ölçüsü ve pabuç deliği teslimde
- Not: − damarı yıldızın 1. saplamasına (F1 dönüşleri yanı; kopruler.Yıldız barası · GND.yerlesim).
- Kaynak: `planlama/adim3/elektrik.md:326-327`, `planlama/adim3/elektrik.md:352` · 10.11 dökümü: #10

#### G13 · Anahtarlı bara → BTS7960 sağ (B+ / B−)

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Anahtarlı bara (+) → BTS7960 sağ (B+ / B−)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** F1 20 A (sigorta kutusu) (`F1`, 20 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak)
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 650 mm; Manhattan 511 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara / yıldız → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** BTS vidalı güç klemensi (B+ / B−); bara ucu sarı M5 halka pabuç, saplamada
- **Uç türü (uc_turu):** a: bara-pabuc, bts-guc · b: bara-pabuc, bts-guc

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Anahtarlı bara · + | BTS7960 sağ · B+ |  |
| − | BTS7960 sağ · B− | Yıldız barası · GND |  |

- Teyit: klemens: BTS7960 güç klemensinin aldığı kesit satıcı sayfasında yok; kablajda teyit, almazsa çatal pabuç
- Teyit: güç barası tutucusu (CAD P10.7b): saplama ölçüsü ve pabuç deliği teslimde
- Not: − damarı yıldızın 2. saplamasına (F1 dönüşleri yanı; kopruler.Yıldız barası · GND.yerlesim).
- Kaynak: `planlama/adim3/elektrik.md:326-327`, `planlama/adim3/elektrik.md:352` · 10.11 dökümü: #11

#### G14 · Anahtarlı bara → 7,5 A hat sigortası → XL4016 A girişi

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Anahtarlı bara (+) → XL4016 A (IN+ / IN−)
- **Kesit:** 16 AWG (1,31 mm²); hat yuvasının kuyruğu 16 AWG (MJ:122); yuva ile bara / XL arası da 16 AWG (O-1) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** Hat sigortası A 7,5 A mini (XL4016 A girişi) (`hat-A`, 7,5 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-A
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 600 mm; Manhattan 467 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** yuva kuyruğuna lehim + makaron; XL vidalı klemens; bara / yıldız ucu halka pabuç (O-3 b)
- **Uç türü (uc_turu):** a: bara-pabuc, modul-vidali · b: bara-pabuc, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Anahtarlı bara · + | XL4016 A · IN+ | ara: 7,5 A mini hat sigortası yuvası (16 AWG kuyruklu) |
| − | XL4016 A · IN− | Yıldız barası · GND |  |

- Teyit: güç barası ürünü seçilmedi (fiyat bekliyor): saplama ölçüsü ve pabuç deliği teslimde
- Kaynak: `planlama/adim3/elektrik.md:328`, `planlama/adim3/elektrik.md:223`, `planlama/adim3/elektrik.md:370`, `planlama/maliyet.json:122` · 10.11 dökümü: #16

#### G15 · Anahtarlı bara → 7,5 A hat sigortası → XL4016 B girişi

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Anahtarlı bara (+) → XL4016 B (IN+ / IN−)
- **Kesit:** 16 AWG (1,31 mm²); hat yuvasının kuyruğu 16 AWG (MJ:122); yuva ile bara / XL arası da 16 AWG (O-1) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** Hat sigortası B 7,5 A mini (XL4016 B girişi) (`hat-B`, 7,5 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-B
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 550 mm; Manhattan 421 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** yuva kuyruğuna lehim + makaron; XL vidalı klemens; bara / yıldız ucu halka pabuç (O-3 b)
- **Uç türü (uc_turu):** a: bara-pabuc, modul-vidali · b: bara-pabuc, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Anahtarlı bara · + | XL4016 B · IN+ | ara: 7,5 A mini hat sigortası yuvası (16 AWG kuyruklu) |
| − | XL4016 B · IN− | Yıldız barası · GND |  |

- Teyit: güç barası ürünü seçilmedi (fiyat bekliyor): saplama ölçüsü ve pabuç deliği teslimde
- Kaynak: `planlama/adim3/elektrik.md:329`, `planlama/adim3/elektrik.md:223`, `planlama/adim3/elektrik.md:370`, `planlama/maliyet.json:122` · 10.11 dökümü: #17

#### G18 · F4 5 A → XL4016 çevre girişi

- **Devre:** güç 12 V (çevre dalı) · **dal:** F4 · **durum:** kesin
- **Uçlar:** Sigorta kutusu (F4 5 A çıkışı / Yıldız barası) → XL4016 çevre (IN+ / IN−)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F4 5 A (sigorta kutusu) (`F4`, 5 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 550 mm; Manhattan 406 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** XL vidalı klemens
- **Uç türü (uc_turu):** a: modul-vidali, sigorta-kutusu · b: bara-pabuc, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Sigorta kutusu · F4 çıkışı | XL4016 çevre · IN+ |  |
| − | XL4016 çevre · IN− | Yıldız barası · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:338`, `planlama/adim3/elektrik.md:368` · 10.11 dökümü: #39 (bölündü)

#### G19 · XL4016 çevre 5 V → arayüz kartı 5 V klemensi

- **Devre:** 5 V çevre · **dal:** F4 · **durum:** kesin
- **Uçlar:** XL4016 çevre (OUT+ / OUT−) → Arayüz kartı (çevre 5 V / GND)
- **Kesit:** 16 AWG (1,31 mm²); 16 AWG (O-1 / O-2 dönüştürücü kuralıyla seçildi); 14.11'den beri koruyan çıkıştaki 2 A çevre hat sigortası (O-19 a): 16 AWG'nin etekteki 8,2 A'inin çok altında · **renk:** + kırmızı, − / GND siyah; makaron mavi
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 300 mm; Manhattan 208 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** iki uç vidalı klemens; çevre 5 V dağıtımı arayüz kartında (O-7 a)
- **Uç türü (uc_turu):** a: modul-vidali · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| +5 V | XL4016 çevre · OUT+ | Arayüz kartı · çevre 5 V | ara: 2 A mini hat sigortası yuvası (16 AWG kuyruklu), XL4016 çevre OUT+ ucunun dibinde (O-19 a, orkestratör kararı 14.11) |
| GND | XL4016 çevre · OUT− | Arayüz kartı · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:338`, `planlama/adim3/elektrik.md:283`, `planlama/adim3/elektrik.md:353` · 10.11 dökümü: #39 (bölündü)

#### SV1 · XL4016 A 6 V → dağıtım kartı A

- **Devre:** servo gücü · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** XL4016 A (OUT+ / OUT−) → Dağıtım kartı A (V+ / GND)
- **Kesit:** 16 AWG (1,31 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 A akım sınırı (`XL4016-A`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-A → XL4016-A
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 250 mm; Manhattan 196 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. belgede ≈ 0,3 m (EL:224) tahmini; CAD'de tasarlanmış yol yok, P10.7b'de ölçülecek
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** iki uç vidalı klemens
- **Uç türü (uc_turu):** a: modul-vidali · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | XL4016 A · OUT+ | Dağıtım kartı A · V+ |  |
| GND | XL4016 A · OUT− | Dağıtım kartı A · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:224-225`, `planlama/adim3/elektrik.md:328` · 10.11 dökümü: #19

#### SV2 · XL4016 B 6 V → dağıtım kartı B

- **Devre:** servo gücü · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** XL4016 B (OUT+ / OUT−) → Dağıtım kartı B (V+ / GND)
- **Kesit:** 16 AWG (1,31 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 B akım sınırı (`XL4016-B`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-B → XL4016-B
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 300 mm; Manhattan 223 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. belgede ≈ 0,3 m (EL:224) tahmini; CAD'de tasarlanmış yol yok, P10.7b'de ölçülecek
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** iki uç vidalı klemens
- **Uç türü (uc_turu):** a: modul-vidali · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | XL4016 B · OUT+ | Dağıtım kartı B · V+ |  |
| GND | XL4016 B · OUT− | Dağıtım kartı B · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:224-225`, `planlama/adim3/elektrik.md:329` · 10.11 dökümü: #20

### taban (K1) (17)

#### G01 · Akü kutup kabloları (akü → XT60, akü tarafı)

- **Devre:** güç 12 V ana hat · **dal:** aku-ana · **durum:** kablajda teyit edilecek
- **Uçlar:** Akü (Victron SuperPack 12,8 V 20 Ah) (+ / − kutup (M5)) → XT60 (akü tarafı) (+ / −)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** Akü BMS (Victron SuperPack, 30 A sürekli) (`aku-bms`, 30 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 100 mm; sabit: akü → ana sigorta ≤ 15 cm (akü raporu); kutup → XT60 parçası ≈ 10 cm (`raporlar/kaynaklar/06-aku-secimi.md:161`). P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 9 B3, 17 K1 · **sonlandırma:** akü ucu M5 halka pabuç + yaylı pul; öbür uç XT60 (lehim)
- **Uç türü (uc_turu):** a: pabuc · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Akü · + kutup (M5) | XT60 (akü tarafı) · + |  |
| − | Akü · − kutup (M5) | XT60 (akü tarafı) · − |  |

- Teyit: XT60'ın hangi tarafının (erkek / dişi) akü kablosunda olduğu belgede yok; teslimde
- Teyit: ana hat ayrı döşenir (sıkı demet yok); kablo üstündeki sıcaklık sınıfı ≥ 80 °C (istisna ana-hat-12awg, O-15)
- Not: 10.11 dökümü XT60'tan başlıyordu; akü kutbundan XT60'a giden kısa çift de lehimlenecek bir kablo (MJ:112 pabuç). Akü raporu: ana sigortaya ≤ 15 cm.
- Kaynak: `planlama/adim3/elektrik.md:323`, `raporlar/kaynaklar/06-aku-secimi.md:161-163`, `planlama/maliyet.json:112` · 10.11 dökümü: yeni

#### G08 · F1 20 A → röle K1 kontağı (30)

- **Devre:** güç 12 V bara · **dal:** F1-kontak-oncesi · **durum:** kablajda teyit edilecek
- **Uçlar:** Sigorta kutusu (F1 20 A çıkışı) → Röle K1 (MAH-112-C-4, soket) (30)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F1 20 A (sigorta kutusu) (`F1`, 20 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 250 mm; Manhattan 190 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 12 B5a (öneri), 17 K1 · **sonlandırma:** soket kuyruğuna lehim / pabuç (soket kablolu, MJ röle soketi)
- **Uç türü (uc_turu):** a: sigorta-kutusu · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Sigorta kutusu · F1 çıkışı | Röle K1 · 30 |  |

- Teyit: klemens: sigorta kutusunun F1 çıkış ucunun tipi ve 12 AWG alıp almadığı listede / belgede yazılı değil; teslimde bakılır (KT3)
- Kaynak: `planlama/adim3/elektrik.md:325`, `planlama/adim3/elektrik.md:365`, `planlama/adim3/elektrik.md:441` · 10.11 dökümü: #8 (bölündü)

#### G09 · Röle K1 kontağı (87) → anahtarlı bara

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Röle K1 (87) → Anahtarlı bara (+)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** F1 20 A (sigorta kutusu) (`F1`, 20 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 250 mm; Manhattan 190 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: anahtarlı bara CAD'de yok: sigorta kutusu (güç paneli) vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 12 B5a (öneri), 17 K1 · **sonlandırma:** bara: saplamalı bara + halka pabuç (O-3 b)
- **Uç türü (uc_turu):** a: lehim · b: bara-pabuc

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Röle K1 · 87 | Anahtarlı bara · + |  |

- Teyit: güç barası tutucusu (CAD P10.7b): saplama ölçüsü ve pabuç deliği teslimde
- Kaynak: `planlama/adim3/elektrik.md:325`, `planlama/adim3/elektrik.md:252`, `planlama/adim3/elektrik.md:93` · 10.11 dökümü: #8 (bölündü)

#### G10 · F1 → ön şarj kartı (K2 kontağı)

- **Devre:** güç 12 V bara · **dal:** F1-kontak-oncesi · **durum:** kablajda teyit edilecek
- **Uçlar:** Sigorta kutusu (F1 20 A çıkışı) → Ön şarj kartı (K2 JQC-3FF + 5,6 Ω 11 W) (giriş)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F1 20 A (sigorta kutusu) (`F1`, 20 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 400 mm; Manhattan 307 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 12 B5a (öneri), 17 K1 · **sonlandırma:** F1 ucu sigorta kutusu çıkış klemensi; ön şarj kartı ucu: 12 AWG kart üstünde K2'nin kontak pimine doğrudan lehim (JQC-3FF PCB pimli; pertinaks klemensi yok)
- **Uç türü (uc_turu):** a: sigorta-kutusu · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Sigorta kutusu · F1 çıkışı | Ön şarj kartı · giriş |  |

- Teyit: 12 AWG'nin K2 pimine lehimi teslimde denenir (pim 12 AWG'yi taşımıyorsa pime kısa 16 AWG köprü değil, kart üstünde kalın bakır şerit / tel köprü)
- Teyit: klemens: sigorta kutusunun F1 çıkış ucunun tipi ve 12 AWG alıp almadığı listede / belgede yazılı değil; teslimde bakılır (KT3)
- Kaynak: `planlama/adim3/elektrik.md:441-442`, `planlama/adim3/elektrik.md:365` · 10.11 dökümü: #9 (bölündü)

#### G11 · Ön şarj kartı (5,6 Ω) → anahtarlı bara

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Ön şarj kartı (çıkış) → Anahtarlı bara (+)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** F1 20 A (sigorta kutusu) (`F1`, 20 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 400 mm; Manhattan 307 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 12 B5a (öneri), 17 K1 · **sonlandırma:** ön şarj kartı ucu: 5,6 Ω taş direncin bacağına hat üstünde lehim + makaron (pertinaks klemensine 12 AWG girmez); bara ucu sarı M5 halka pabuç, saplamada
- **Uç türü (uc_turu):** a: lehim · b: bara-pabuc

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Ön şarj kartı · çıkış | Anahtarlı bara · + |  |

- Teyit: direnç bacağına 12 AWG lehimi teslimde denenir (olmazsa direnç bacağına sarı halka pabuç + M5)
- Teyit: güç barası tutucusu (CAD P10.7b): saplama ölçüsü ve pabuç deliği teslimde
- Not: O-1'deki 'direnç sonrası kol direncin akımına göre' kuralı bu kola uygulanmadı: K1 kapalıyken anahtarlı bara bu kolu öbür yandan F1 20 A ile besler, kısa devrede akımı 5,6 Ω sınırlamaz; kesit F1'e göre (12 AWG). Ön şarj kartının 12 AWG ucu 5,08 mm klemense girmez: kart üstüne lehim ya da pabuç.
- Kaynak: `planlama/adim3/elektrik.md:441-442` · 10.11 dökümü: #9 (bölündü)

#### SV3 · XL4016 C 6 V → kafa servoları klemensi

- **Devre:** servo gücü · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** XL4016 C (OUT+ / OUT−) → Dağıtım kartı C (kafa) (V+ / GND)
- **Kesit:** 16 AWG (1,31 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 C akım sınırı (`XL4016-C`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-C → XL4016-C
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 300 mm; sabit: dağıtım kartı C, XL4016 C klemensinin yanında (O-8): kısa çift (`planlama/adim3/kablolar.json#kararlar`). P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 12 B5a (öneri), 32 K2 · **sonlandırma:** XL vidalı klemens → dağıtım kartı C'nin 2 pin 5,08 mm giriş klemensi (O-8: kol dağıtım kartlarıyla aynı yöntem)
- **Uç türü (uc_turu):** a: modul-vidali · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | XL4016 C · OUT+ | Dağıtım kartı C (kafa) · V+ |  |
| GND | XL4016 C · OUT− | Dağıtım kartı C (kafa) · GND |  |

- Not: Dağıtım kartı C (kafa): XL4016 C'nin yanında küçük pertinaks; 16 AWG giriş → V+ / GND barası → 2200 µF → iki 3 pinli çıkış (pan, tilt); sinyal PCA'dan köprü (P03). Kol kartlarının yöntemi (EL:225), O-8.
- Kaynak: `planlama/adim3/elektrik.md:330`, `planlama/adim3/elektrik.md:129` · 10.11 dökümü: #21

#### A03 · Röle K1 bobini (−, 85) → BC337-40 #1 kollektörü (arayüz kartı)

- **Devre:** acil stop (röle sürücüsü) · **dal:** mantar-sonrasi · **durum:** kablajda teyit edilecek
- **Uçlar:** Röle K1 (85 (bobin −)) → Arayüz kartı (BC337-40 #1 kollektör)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron yeşil
- **Koruma:** F5 2 A (sigorta kutusu) (`F5`, 2 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F5 → mantar → K1-bobin
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 350 mm; Manhattan 243 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** arayüz kartı klemensi; 1N4007 röle K1'in bobin uçlarının dibinde, röle soketinin 86 / 85 kuyruklarının üstünde (lehim + makaron), katot (bantlı uç) bobinin + ucuna (86)
- **Uç türü (uc_turu):** a: lehim · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| − | Röle K1 · 85 | Arayüz kartı · BC337-40 #1 C |  |

- Teyit: T2a / T2 (PH §7): ayak sırası, bobin gerilimi ≤ 0,12 V
- Not: 10.11 dökümünde sürücü MOSFET idi; pin-haritasi sürüm 4 ile BC337-40 (EL:268)
- Kaynak: `planlama/adim3/elektrik.md:249-251`, `planlama/adim3/elektrik.md:268`, `planlama/adim3/elektrik.md:306`, `planlama/adim3/pin-haritasi.md:302`, `planlama/adim3/pin-haritasi.md:429` · 10.11 dökümü: #41 (bölündü; yeni uç: röle sürücü kartı)

#### A04 · Acil stop düğümü → röle K2 bobini (+) (ön şarj kartı)

- **Devre:** acil stop · **dal:** mantar-sonrasi · **durum:** kesin
- **Uçlar:** Acil stop düğümü (+) → Ön şarj kartı (K2 bobini +)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron yeşil
- **Koruma:** F5 2 A (sigorta kutusu) (`F5`, 2 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F5 → mantar · **ortak dönüş:** A05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 600 mm; Manhattan 459 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: düğüm → mantar vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** düğüm ucu: acil stop düğüm kartı (güç panelinde küçük pertinaks parçası): iki adet 2 pin 5,08 mm vidalı klemens, dört ucu kart üstünde lehimle köprülü; ince telli uç kalaylanmaz, bükülür (yüksük varsa yüksük; ek tur, orkestratör kararı 14.11, WAGO 2273 ince telli almaz); ön şarj kartı ucu K2 bobin klemensi (2 pin 5,08 mm)
- **Uç türü (uc_turu):** a: klemens-508 · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Acil stop düğümü (mantar NC çıkışı) · + | Ön şarj kartı · K2 bobini + |  |

- Kaynak: `planlama/adim3/elektrik.md:443-444`, `planlama/adim3/elektrik.md:369` · 10.11 dökümü: #42 (bölündü)

#### A05 · Röle K2 bobini (−) → BC337-40 #2 kollektörü (arayüz kartı)

- **Devre:** acil stop (röle sürücüsü) · **dal:** mantar-sonrasi · **durum:** kablajda teyit edilecek
- **Uçlar:** Ön şarj kartı (K2 bobini −) → Arayüz kartı (BC337-40 #2 kollektör)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron yeşil
- **Koruma:** F5 2 A (sigorta kutusu) (`F5`, 2 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F5 → mantar → K2-bobin
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 150 mm; Manhattan 92 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** kart klemensleri; 1N4007 ön şarj kartında K2 bobin uçlarının dibinde (bobin klemensinin / röle pimlerinin üstünde), katot (bantlı uç) bobinin + ucuna
- **Uç türü (uc_turu):** a: klemens-508 · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| − | Ön şarj kartı · K2 bobini − | Arayüz kartı · BC337-40 #2 C |  |

- Teyit: T2a / T2 (PH §7)
- Kaynak: `planlama/adim3/elektrik.md:444`, `planlama/adim3/elektrik.md:268`, `planlama/adim3/pin-haritasi.md:302`, `planlama/adim3/kablolama-on-kararlar.md:270-271`, `planlama/adim3/pin-haritasi.md:429` · 10.11 dökümü: #42 (uç değişti: IRLZ44N #2 / GPIO2 → BC337-40 #2 / GPIO19)

#### A06 · Acil stop düğümü → PC817 #1 girişi (acil stop algısı)

- **Devre:** acil stop (algı) · **dal:** mantar-sonrasi · **durum:** kablajda teyit edilecek
- **Uçlar:** Acil stop düğümü (+) → PC817 modülü (arayüz kartı) (IN1 + / IN1 −)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron yeşil
- **Koruma:** F5 2 A (sigorta kutusu) (`F5`, 2 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F5 → mantar
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 700 mm; Manhattan 523 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: düğüm → mantar vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** düğüm ucu: acil stop düğüm kartında bir klemensin kuyruğuna (kart altı) lehim + makaron (22 AWG: 5,08 mm klemensin alt sınırı belgesiz); PC817 ucu modülün vidalı klemensi; − ucu arayüz kartında GND pedine lehim + makaron
- **Uç türü (uc_turu):** a: lehim, modul-vidali · b: lehim, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Acil stop düğümü (mantar NC çıkışı) · + | PC817 modülü · IN1 + |  |
| − | PC817 modülü · IN1 − | Arayüz kartı · GND |  |

- Teyit: klemens: 5,08 mm klemensin kesit aralığı belgesiz (satıcı sayfasında yok); 22 AWG uç kartta lehim + makaron; teslimde aralık okunursa yeniden bakılır
- Kaynak: `planlama/adim3/elektrik.md:235`, `planlama/adim3/elektrik.md:251`, `planlama/adim3/elektrik.md:339` · 10.11 dökümü: #41 (bölündü: PC817 #1)

#### G02 · XT60 → ana sigorta 30 A

- **Devre:** güç 12 V ana hat · **dal:** aku-ana · **durum:** kablajda teyit edilecek
- **Uçlar:** XT60 (robot tarafı) (+) → Ana sigorta yuvası 30 A (giriş)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** Akü BMS (Victron SuperPack, 30 A sürekli) (`aku-bms`, 30 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 150 mm; sabit: akü → ana sigorta ≤ 15 cm (akü raporu); CAD'deki ana sigorta zarfı akü merkezinden 177 mm (Manhattan): yerleşimde teyit (`raporlar/kaynaklar/06-aku-secimi.md:161`). P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** XT60 lehim; yuva kablolu (kendi kuyruğu, kesiti teslimde bakılır)
- **Uç türü (uc_turu):** a: lehim · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | XT60 (robot tarafı) · + | Ana sigorta yuvası · giriş |  |

- Teyit: ana sigorta yuvasının kendi kuyruk kesiti (MJ ana sigorta yuvası, F114-C) teslimde
- Teyit: ana hat ayrı döşenir (sıkı demet yok); kablo üstündeki sıcaklık sınıfı ≥ 80 °C (istisna ana-hat-12awg, O-15)
- Kaynak: `planlama/adim3/elektrik.md:323`, `planlama/adim3/elektrik.md:364`, `raporlar/kaynaklar/06-aku-secimi.md:161-162` · 10.11 dökümü: #1

#### G04 · Ana anahtar → sigorta kutusu girişi

- **Devre:** güç 12 V ana hat · **dal:** aku-ana · **durum:** kablajda teyit edilecek
- **Uçlar:** Ana anahtar ASW-A01 (çıkış) → Sigorta kutusu (6 yollu) (giriş)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** Ana sigorta 30 A (standart bıçak, kablolu yuva) (`ana-sigorta`, 30 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 160 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1, 33 F1 · **sonlandırma:** halka pabuç; kutu ayrı girişliyse 12 AWG kısa köprüler, tek giriş klemensinden yıldız (KT3)
- **Uç türü (uc_turu):** a: pabuc · b: sigorta-kutusu

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Ana anahtar · çıkış | Sigorta kutusu · giriş |  |

- Teyit: KT3: kutu yuvaları ortak giriş baralı mı (teslimde süreklilik)
- Teyit: ana hat ayrı döşenir (sıkı demet yok); kablo üstündeki sıcaklık sınıfı ≥ 80 °C (istisna ana-hat-12awg, O-15)
- Teyit: klemens: sigorta kutusunun giriş ucunun tipi ve 12 AWG alıp almadığı listede / belgede yazılı değil; teslimde bakılır (KT3)
- Kaynak: `planlama/adim3/elektrik.md:323`, `planlama/adim3/elektrik.md:380`, `planlama/adim3/kablolama-on-kararlar.md:95-98` · 10.11 dökümü: #3

#### G05 · Akü − → Yıldız barası noktası

- **Devre:** toprak · **dal:** aku-ana · **durum:** kablajda teyit edilecek
- **Uçlar:** XT60 (robot tarafı) (−) → Yıldız barası (güç paneli) (GND)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron siyah
- **Koruma:** Akü BMS (Victron SuperPack, 30 A sürekli) (`aku-bms`, 30 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 146 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: XT60 → akü merkezi, yıldız barası → sigorta kutusu (güç paneli) vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** XT60 lehim; yıldız barasının ortadaki (3.) saplamasına sarı halka pabuç (O-3 b; akü dönüşü ortada; yerleşim kopruler.Yıldız barası · GND.yerlesim)
- **Uç türü (uc_turu):** a: lehim · b: bara-pabuc

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| − | XT60 (robot tarafı) · − | Yıldız barası · GND |  |

- Teyit: güç barası ürünü seçilmedi (fiyat bekliyor): saplama ölçüsü ve pabuç deliği teslimde
- Teyit: ana hat ayrı döşenir (sıkı demet yok); kablo üstündeki sıcaklık sınıfı ≥ 80 °C (istisna ana-hat-12awg, O-15)
- Kaynak: `planlama/adim3/elektrik.md:323`, `planlama/adim3/elektrik.md:341` · 10.11 dökümü: #4

#### G07 · Ana anahtar sonrası → akü ölçüm bölücüsü (arayüz kartı)

- **Devre:** sinyal (akü ölçümü) · **dal:** aku-olcum · **durum:** kablajda teyit edilecek
- **Uçlar:** Ana anahtar ASW-A01 (çıkış (bölücünün 100 kΩ üst direnci bu uçta)) → Arayüz kartı (akü bölücü orta noktası (18 kΩ + 100 nF))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Akü ölçüm bölücüsünün üst direnci 100 kΩ (kaynak ucunda) (`R-aku-olcum`, 0,00015 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → R-aku-olcum · **ortak dönüş:** G19
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 450 mm; Manhattan 353 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 (öneri) · **sonlandırma:** kaynak ucunda 100 kΩ telin başına lehim + makaron (O-5 a; değer EL:234); arayüz kartı ucu bölücü orta noktasının pedine lehim + makaron (22 AWG: 5,08 mm klemensin alt sınırı belgesiz)
- **Uç türü (uc_turu):** a: lehim · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Ana anahtar · çıkış | Arayüz kartı · akü bölücü orta noktası | ara: 100 kΩ telin başına lehim + makaron (O-5 a; EL:234) |

- Teyit: rehber: 100 kΩ arayüz kartında değil, ana anahtar çıkışındaki uçta; uzun yüksek empedanslı hat, ADC kalibrasyonunda bakılır
- Teyit: klemens: 5,08 mm klemensin kesit aralığı belgesiz (satıcı sayfasında yok); 22 AWG uç kartta lehim + makaron; teslimde aralık okunursa yeniden bakılır
- Kaynak: `planlama/adim3/elektrik.md:234`, `planlama/adim3/elektrik.md:325`, `planlama/adim3/pin-haritasi.md:83` · 10.11 dökümü: #7 (bölündü: güç tarafı)

#### G16 · Anahtarlı bara → 5 A hat sigortası → XL4016 C girişi

- **Devre:** anahtarlı bara · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Anahtarlı bara (+) → XL4016 C (IN+ / IN−)
- **Kesit:** 16 AWG (1,31 mm²); hat yuvasının kuyruğu 16 AWG (MJ:122); yuva ile bara / XL arası da 16 AWG (O-1) · **renk:** + kırmızı, − / GND siyah; makaron turuncu
- **Koruma:** Hat sigortası C 5 A mini (XL4016 C girişi) (`hat-C`, 5 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-C
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 400 mm; Manhattan 295 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** yuva kuyruğuna lehim + makaron; XL vidalı klemens; bara / yıldız ucu halka pabuç (O-3 b)
- **Uç türü (uc_turu):** a: bara-pabuc, modul-vidali · b: bara-pabuc, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Anahtarlı bara · + | XL4016 C · IN+ | ara: 5 A mini hat sigortası yuvası (16 AWG kuyruklu) |
| − | XL4016 C · IN− | Yıldız barası · GND |  |

- Teyit: güç barası ürünü seçilmedi (fiyat bekliyor): saplama ölçüsü ve pabuç deliği teslimde
- Kaynak: `planlama/adim3/elektrik.md:330`, `planlama/adim3/elektrik.md:129`, `planlama/maliyet.json:122` · 10.11 dökümü: #18

#### G20 · F6 3 A → göğüs ekranı regülatörü (LM2577 + LM2596) girişi

- **Devre:** güç 12 V (göğüs dalı) · **dal:** F6 · **durum:** karara bağlı
- **Uçlar:** Sigorta kutusu (F6 3 A çıkışı / Yıldız barası) → Göğüs ekranı regülatörü (LM2577 + LM2596) (IN+ / IN−)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F6 3 A standart (sigorta kutusu) (`F6`, 3 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F6
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 1.550 mm; Manhattan 1.207 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: göğüs regülatörü CAD'de yok (K52): göğüs ekranına kadar üst sınır. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1, 32 K2 · **sonlandırma:** regülatör vidalı klemens
- **Uç türü (uc_turu):** a: modul-vidali, sigorta-kutusu · b: bara-pabuc, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Sigorta kutusu · F6 çıkışı | Göğüs regülatörü · IN+ |  |
| − | Göğüs regülatörü · IN− | Yıldız barası · GND |  |

- Eksik: regülatörün panel yeri açık (K52, planlama/d158/karar-kuyrugu.md): uç yeri ve boy bu karara bağlı
- Not: 14.11 K11 a ile kaynak kutunun 6. yuvası (F6 3 A standart)
- Kaynak: `planlama/adim3/elektrik.md:62`, `planlama/adim3/elektrik.md:68`, `planlama/adim3/elektrik.md:371`, `planlama/adim3/kablolama-on-kararlar.md:88-94`, `planlama/adim3/kablolama-on-kararlar.md:342` · 10.11 dökümü: #43 (bölündü: F6 dalı)

#### G22 · Anahtarlı bara → PC817 #2 girişi (bara durumu)

- **Devre:** anahtarlı bara (algı) · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Anahtarlı bara (+) → PC817 modülü (arayüz kartı) (IN2 + / IN2 −)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron turuncu
- **Koruma:** Hat sigortası G22 2 A mini (bara ucunda) (`hat-G22`, 2 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-G22
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 500 mm; Manhattan 372 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: bara → sigorta kutusu vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1 · **sonlandırma:** bara ucunda hat sigortası yuvası (16 AWG kuyruğu mavi M5 pabuçla saplamaya), 22 AWG tel kuyruğa lehim + makaron; modül ucu vidalı klemens; yıldız ucu: 22 AWG tel ≈ 5 cm 18 AWG siyah ara parçaya lehim + makaron, ara parça kırmızı M5 pabuçla (22 AWG kırmızı pabucun 0,5 mm² alt sınırının altında; ek tur)
- **Uç türü (uc_turu):** a: bara-pabuc, modul-vidali · b: bara-pabuc, modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Anahtarlı bara · + | PC817 modülü · IN2 + | ara: mini hat sigortası yuvası + 2 A mini bıçak, bara ucunun dibinde (O-18 b) |
| − | PC817 modülü · IN2 − | Yıldız barası · GND |  |

- Not: O-18 b (orkestratör kararı, 14.11.2026): telin kaynak (bara) ucunda hat sigortası 2 A; 22 AWG (3 A) korunur. Listedeki hat yuvası mini / micro bıçak alır; 'standart' değil mini 2 A (maliyet.json '2A Mini' satırı).
- Kaynak: `planlama/adim3/elektrik.md:236`, `planlama/adim3/elektrik.md:331`, `planlama/adim3/pin-haritasi.md:97` · 10.11 dökümü: #32 (bölündü: giriş)

### taban elektronik katı (10)

#### N01 · Enkoder arka sol JGB37 → ESP32

- **Devre:** sinyal · **dal:** F4 · **durum:** kablajda teyit edilecek
- **Uçlar:** JGB37-520 arka sol (enkoder VCC / GND / A / B) → ESP32 DevKit (GPIO18 / GPIO17 / 3V3 / GND)
- **Kesit:** 22 AWG (0,33 mm²); motorun kendi kablosu yetmezse sinyal teliyle (sinyal-22) uzatma; tahmin uzatmanın üst sınırı · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 800 mm; Manhattan 607 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 7 B2b, 32 K2 · **sonlandırma:** ESP32 taşıyıcı başlığı; jumper'ın fabrika sıkılı dişi ucu, tel lehim + makaronla uzatılır (O-4 r)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| A | JGB37 arka sol · enkoder A | ESP32 · GPIO18 | GPIO18 `SOL_ENK_A` |
| B | JGB37 arka sol · enkoder B | ESP32 · GPIO17 | GPIO17 `SOL_ENK_B`; seri direnç (1 kΩ seri, pine yakın) |
| VCC 3V3 | JGB37 arka sol · enkoder VCC | ESP32 · 3V3 |  |
| GND | JGB37 arka sol · enkoder GND | ESP32 · GND |  |

- Teyit: T7 (enkoder çıkış türü), T1 (PSRAM'siz modül; 16 / 17)
- Kaynak: `planlama/adim3/pin-haritasi.md:100-103`, `planlama/adim3/pin-haritasi.md:299`, `planlama/adim3/elektrik.md:239`, `planlama/adim3/elektrik.md:488-489` · 10.11 dökümü: #46

#### N02 · Enkoder arka sağ JGB37 → ESP32

- **Devre:** sinyal · **dal:** F4 · **durum:** kablajda teyit edilecek
- **Uçlar:** JGB37-520 arka sağ (enkoder VCC / GND / A / B) → ESP32 DevKit (GPIO16 / GPIO15 / 3V3 / GND)
- **Kesit:** 22 AWG (0,33 mm²); motorun kendi kablosu yetmezse sinyal teliyle (sinyal-22) uzatma; tahmin uzatmanın üst sınırı · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 600 mm; Manhattan 452 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 7 B2b, 32 K2 · **sonlandırma:** ESP32 taşıyıcı başlığı; jumper'ın fabrika sıkılı dişi ucu, tel lehim + makaronla uzatılır (O-4 r)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| A | JGB37 arka sağ · enkoder A | ESP32 · GPIO16 | GPIO16 `SAG_ENK_A`; seri direnç (1 kΩ seri, pine yakın) |
| B | JGB37 arka sağ · enkoder B | ESP32 · GPIO15 | GPIO15 `SAG_ENK_B` |
| VCC 3V3 | JGB37 arka sağ · enkoder VCC | ESP32 · 3V3 |  |
| GND | JGB37 arka sağ · enkoder GND | ESP32 · GND |  |

- Teyit: T7 (enkoder çıkış türü), T1 (PSRAM'siz modül; 16 / 17)
- Kaynak: `planlama/adim3/pin-haritasi.md:100-103`, `planlama/adim3/pin-haritasi.md:299`, `planlama/adim3/elektrik.md:239`, `planlama/adim3/elektrik.md:488-489` · 10.11 dökümü: #47

#### I01 · I2C: ESP32 → PCA9685

- **Devre:** I2C · **dal:** F4 · **durum:** kesin
- **Uçlar:** ESP32 DevKit (GPIO21 / GPIO22 / 3V3 / GND) → PCA9685 (SDA / SCL / VCC / GND (giriş başlığı))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 100 mm; Manhattan 59 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 14 B6a (öneri) · **sonlandırma:** dişi uçlu jumper teli (O-4 r: fabrika sıkılı dişi uç, lehim + makaronla uzatılır); PCA OE → GND kart üstünde
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| SDA | ESP32 · GPIO21 | PCA9685 · SDA (giriş) | GPIO21 `I2C_SDA` |
| SCL | ESP32 · GPIO22 | PCA9685 · SCL (giriş) | GPIO22 `I2C_SCL` |
| VCC 3V3 | ESP32 · 3V3 | PCA9685 · VCC (giriş) |  |
| GND | ESP32 · GND | PCA9685 · GND (giriş) |  |

- Not: PCA9685 V+ klemensi boş kalır (EL:226); servo gücü dağıtım kartlarından.
- Kaynak: `planlama/adim3/pin-haritasi.md:98-99`, `planlama/adim3/elektrik.md:237`, `planlama/adim3/elektrik.md:487` · 10.11 dökümü: #50 (bölündü)

#### I02 · I2C: PCA9685 → BNO055

- **Devre:** I2C · **dal:** F4 · **durum:** kesin
- **Uçlar:** PCA9685 (SDA / SCL / VCC / GND (çıkış başlığı)) → BNO055 (SDA / SCL / VIN / GND)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 148 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 14 B6a (öneri) · **sonlandırma:** dişi uçlu jumper teli (O-4 r); PCA'nın çıkış başlığından zincirleme (PCA kartında I2C çıkış başlığı var)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| SDA | PCA9685 · SDA (çıkış) | BNO055 · SDA |  |
| SCL | PCA9685 · SCL (çıkış) | BNO055 · SCL |  |
| VIN 3V3 | PCA9685 · VCC (çıkış) | BNO055 · VIN |  |
| GND | PCA9685 · GND (çıkış) | BNO055 · GND |  |

- Kaynak: `planlama/adim3/pin-haritasi.md:98`, `planlama/adim3/elektrik.md:238` · 10.11 dökümü: #50 (bölündü)

#### P01 · PCA9685 kanal 0–3 → dağıtım kartı A sinyal girişleri

- **Devre:** sinyal (servo) · **dal:** F4 · **durum:** kesin
- **Uçlar:** PCA9685 (kanal 0–3 sinyal) → Dağıtım kartı A (sinyal girişleri 1–4)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 150 mm; Manhattan 94 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 14 B6a (öneri) · **sonlandırma:** 3 pinli başlıklar arası dişi-dişi jumper teli (O-4 r) PCA K0–K3 → dağıtım kartı A sinyal girişleri
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| K0 sag_omuz | PCA9685 · K0 | Dağıtım kartı A · sinyal girişi 1 | PCA K0 `sag_omuz` |
| K1 sag_omuz_yan | PCA9685 · K1 | Dağıtım kartı A · sinyal girişi 2 | PCA K1 `sag_omuz_yan` |
| K2 sag_dirsek | PCA9685 · K2 | Dağıtım kartı A · sinyal girişi 3 | PCA K2 `sag_dirsek` |
| K3 sag_bilek | PCA9685 · K3 | Dağıtım kartı A · sinyal girişi 4 | PCA K3 `sag_bilek` |

- Kaynak: `planlama/adim3/elektrik.md:225-226`, `planlama/adim3/pin-haritasi.md:116-119` · 10.11 dökümü: #51 (bölündü)

#### P02 · PCA9685 kanal 5–8 → dağıtım kartı B sinyal girişleri

- **Devre:** sinyal (servo) · **dal:** F4 · **durum:** kesin
- **Uçlar:** PCA9685 (kanal 5–8 sinyal) → Dağıtım kartı B (sinyal girişleri 1–4)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 300 mm; Manhattan 238 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 14 B6a (öneri) · **sonlandırma:** 3 pinli başlıklar arası dişi-dişi jumper teli (O-4 r) PCA K5–K8 → dağıtım kartı B sinyal girişleri
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| K5 sol_omuz | PCA9685 · K5 | Dağıtım kartı B · sinyal girişi 1 | PCA K5 `sol_omuz` |
| K6 sol_omuz_yan | PCA9685 · K6 | Dağıtım kartı B · sinyal girişi 2 | PCA K6 `sol_omuz_yan` |
| K7 sol_dirsek | PCA9685 · K7 | Dağıtım kartı B · sinyal girişi 3 | PCA K7 `sol_dirsek` |
| K8 sol_bilek | PCA9685 · K8 | Dağıtım kartı B · sinyal girişi 4 | PCA K8 `sol_bilek` |

- Kaynak: `planlama/adim3/elektrik.md:225-226`, `planlama/adim3/pin-haritasi.md:121-124` · 10.11 dökümü: #51 (bölündü)

#### X01 · Arayüz kartı → ESP32 (bölücü çıkışları, röle sürücü girişleri, PC817 çıkışları, EN, 5 V)

- **Devre:** sinyal · **dal:** F4 · **durum:** kablajda teyit edilecek
- **Uçlar:** Arayüz kartı (bölücü / sürücü / PC817 çıkış başlığı) → ESP32 DevKit (taşıyıcı kart) (GPIO ve VIN başlığı)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 250 mm; Manhattan 173 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 14 B6a (öneri) · **sonlandırma:** iki kart arası başlık + dişi uçlu tel (O-4 r: jumper dişi uçları; sinyal teli 22 AWG listede, fiyat bekliyor); jumper'ın fabrika sıkılı dişi ucu, tel lehim + makaronla uzatılır (O-4 r)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| akü ADC | Arayüz kartı · akü bölücü çıkışı (100k/18k + 100 nF) | ESP32 · GPIO36 | GPIO36 `AKU_ADC` |
| sonar sağ echo | Arayüz kartı · sonar sağ bölücü çıkışı (4,7k/10k) | ESP32 · GPIO39 | GPIO39 `SONAR_SAG_ECHO` |
| sonar orta echo | Arayüz kartı · sonar orta bölücü çıkışı | ESP32 · GPIO34 | GPIO34 `SONAR_ORTA_ECHO` |
| sonar sol echo | Arayüz kartı · sonar sol bölücü çıkışı | ESP32 · GPIO35 | GPIO35 `SONAR_SOL_ECHO` |
| sol BTS IS | Arayüz kartı · sol IS bölücü çıkışı (6,8k/5,1k) | ESP32 · GPIO32 | GPIO32 `SOL_IS` |
| sağ BTS IS | Arayüz kartı · sağ IS bölücü çıkışı (6,8k/5,1k) | ESP32 · GPIO33 | GPIO33 `SAG_IS` |
| röle K1 sürüşü | Arayüz kartı · BC337-40 #1 taban girişi (270 Ω; 2,2 kΩ → GND) | ESP32 · GPIO4 | GPIO4 `ROLE_K1` |
| röle K2 sürüşü | Arayüz kartı · BC337-40 #2 taban girişi (270 Ω; 2,2 kΩ → GND) | ESP32 · GPIO19 | GPIO19 `ROLE_K2_ONSARJ` |
| acil stop durumu | PC817 modülü · OUT1 | ESP32 · GPIO23 | GPIO23 `ACIL_STOP_DURUM` |
| bara durumu | PC817 modülü · OUT2 | ESP32 · GPIO5 | GPIO5 `BARA_DURUM` |
| BTS EN (dört uç ortak) | Arayüz kartı · BTS EN düğümü (10 kΩ → GND) | ESP32 · GPIO13 | GPIO13 `BTS_EN` |
| PC817 çıkış beslemesi | PC817 modülü · çıkış VCC | ESP32 · 3V3 | yalnız 3V3'e ya da boş (PH D3); 5 V'a bağlanmaz |
| 5 V | Arayüz kartı · çevre 5 V | ESP32 · VIN |  |
| GND | Arayüz kartı · GND | ESP32 · GND |  |

- Teyit: T5 (PC817 3,3 V tarafı), T6 (IS direnci ölçülmeden IS ucu bağlanmaz), T2
- Not: BTS EN düğümü (10 kΩ → GND) ve çevre 5 V dağıtımı arayüz kartında (O-7 a).
- Kaynak: `planlama/adim3/pin-haritasi.md:83-97`, `planlama/adim3/pin-haritasi.md:294-302`, `planlama/adim3/elektrik.md:233-236`, `planlama/adim3/elektrik.md:283`, `planlama/adim3/elektrik.md:306`, `planlama/adim3/elektrik.md:472-489` · 10.11 dökümü: yeni (bölücü / röle sürücü / PC817 çıkış uçları; #7, #32, #41, #42, #48 dökümde ESP32 ucuna kadar tek kablo sayılmıştı)

#### B01 · BTS7960 sol sinyal → ESP32 / arayüz kartı

- **Devre:** sinyal · **dal:** F4 · **durum:** kablajda teyit edilecek
- **Uçlar:** BTS7960 sol (sinyal başlığı (IN1, IN2, EN1+EN2, IS1+IS2, VCC, GND)) → ESP32 / arayüz kartı (GPIO / IS bölücü / EN düğümü)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 400 mm; Manhattan 311 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 32 K2 · **sonlandırma:** kart başlığı (dişi uçlu jumper teli, O-4 r); jumper'ın fabrika sıkılı dişi ucu, tel lehim + makaronla uzatılır (O-4 r)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| IN1 (ileri PWM) | BTS7960 sol · IN1 | ESP32 · GPIO25 | GPIO25 `SOL_ILERI_PWM` |
| IN2 (geri PWM) | BTS7960 sol · IN2 | ESP32 · GPIO26 | GPIO26 `SOL_GERI_PWM` |
| EN1 + EN2 | BTS7960 sol · EN1+EN2 | Arayüz kartı · BTS EN düğümü (10 kΩ → GND) |  |
| IS1 + IS2 | BTS7960 sol · IS1+IS2 | Arayüz kartı · sol IS bölücü girişi |  |
| VCC 5 V | BTS7960 sol · VCC | Arayüz kartı · çevre 5 V | kaynak belgede yok (PH D8: kart VCC 5 V) |
| GND | BTS7960 sol · GND | Arayüz kartı · GND |  |

- Teyit: T3 (EN kilidi), T4 (EN / IN adları, 3,3 V PWM), T6 (IS direnci önce ölçülür)
- Teyit: kart gelince BTS7960 VCC pininin dış 5 V istediği; VCC çevre 5 V'tan, arayüz kartında (O-7 a)
- Kaynak: `planlama/adim3/pin-haritasi.md:87-93`, `planlama/adim3/pin-haritasi.md:300-301`, `planlama/adim3/pin-haritasi.md:366-373`, `planlama/adim3/elektrik.md:478-482` · 10.11 dökümü: #44

#### B02 · BTS7960 sağ sinyal → ESP32 / arayüz kartı

- **Devre:** sinyal · **dal:** F4 · **durum:** kablajda teyit edilecek
- **Uçlar:** BTS7960 sağ (sinyal başlığı (IN1, IN2, EN1+EN2, IS1+IS2, VCC, GND)) → ESP32 / arayüz kartı (GPIO / IS bölücü / EN düğümü)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 400 mm; Manhattan 312 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 32 K2 · **sonlandırma:** kart başlığı (dişi uçlu jumper teli, O-4 r); jumper'ın fabrika sıkılı dişi ucu, tel lehim + makaronla uzatılır (O-4 r)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| IN1 (ileri PWM) | BTS7960 sağ · IN1 | ESP32 · GPIO27 | GPIO27 `SAG_ILERI_PWM` |
| IN2 (geri PWM) | BTS7960 sağ · IN2 | ESP32 · GPIO14 | GPIO14 `SAG_GERI_PWM` |
| EN1 + EN2 | BTS7960 sağ · EN1+EN2 | Arayüz kartı · BTS EN düğümü (10 kΩ → GND) |  |
| IS1 + IS2 | BTS7960 sağ · IS1+IS2 | Arayüz kartı · sağ IS bölücü girişi |  |
| VCC 5 V | BTS7960 sağ · VCC | Arayüz kartı · çevre 5 V | kaynak belgede yok (PH D8: kart VCC 5 V) |
| GND | BTS7960 sağ · GND | Arayüz kartı · GND |  |

- Teyit: T3 (EN kilidi), T4 (EN / IN adları, 3,3 V PWM), T6 (IS direnci önce ölçülür)
- Teyit: kart gelince BTS7960 VCC pininin dış 5 V istediği; VCC çevre 5 V'tan, arayüz kartında (O-7 a)
- Kaynak: `planlama/adim3/pin-haritasi.md:87-93`, `planlama/adim3/pin-haritasi.md:300-301`, `planlama/adim3/pin-haritasi.md:366-373`, `planlama/adim3/elektrik.md:478-482` · 10.11 dökümü: #45

#### P03 · PCA9685 kanal 4 / 9 → kafa servo hattı C sinyal birleşimi

- **Devre:** sinyal (servo) · **dal:** F4 · **durum:** kesin
- **Uçlar:** PCA9685 (kanal 4 (pan) / 9 (tilt)) → Dağıtım kartı C (kafa) (pan / tilt sinyal girişi)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre → esp32-3v3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 132 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: dağıtım kartı C → XL4016 C vekil (O-8). P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 32 K2 (öneri) · **sonlandırma:** 3 pinli köprü, dağıtım kartı C'nin sinyal girişlerine (kol kartlarıyla aynı yöntem, O-8)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| K4 kafa_pan | PCA9685 · K4 | Dağıtım kartı C (kafa) · pan sinyal girişi | PCA K4 `kafa_pan` |
| K9 kafa_tilt | PCA9685 · K9 | Dağıtım kartı C (kafa) · tilt sinyal girişi | PCA K9 `kafa_tilt` |

- Kaynak: `planlama/adim3/elektrik.md:129-132`, `planlama/adim3/pin-haritasi.md:120`, `planlama/adim3/pin-haritasi.md:125` · 10.11 dökümü: #51 (bölündü)

### taban sonar (3)

#### Q01 · Sonar sağ (HC-SR04) → elektronik katı

- **Devre:** sinyal (sonar) · **dal:** F4 · **durum:** kesin
- **Uçlar:** HC-SR04 sağ (VCC / Trig / Echo / GND) → Elektronik katı (çevre 5 V / PCA9685 / arayüz bölücü)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 550 mm; Manhattan 431 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 16 B7, 17 K1 · **sonlandırma:** sonar pin bloğu (içe bakar, B7) + dişi uçlu jumper teli (O-4 r); öbür uçlar üç ayrı noktaya (PCA K10, arayüz kartı)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| VCC 5 V | HC-SR04 sağ · VCC | Arayüz kartı · çevre 5 V |  |
| Trig | HC-SR04 sağ · Trig | PCA9685 · K10 | PCA K10 `sonar_sag_trig` |
| Echo | HC-SR04 sağ · Echo | Arayüz kartı · sonar sağ bölücü girişi |  |
| GND | HC-SR04 sağ · GND | Arayüz kartı · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:233`, `planlama/adim3/elektrik.md:494`, `planlama/adim3/pin-haritasi.md:126-128`, `planlama/adim3/pin-haritasi.md:84-86` · 10.11 dökümü: #40, #48, #49 (birleşti: sonar başına tek kablo)

#### Q02 · Sonar orta (HC-SR04) → elektronik katı

- **Devre:** sinyal (sonar) · **dal:** F4 · **durum:** kesin
- **Uçlar:** HC-SR04 orta (VCC / Trig / Echo / GND) → Elektronik katı (çevre 5 V / PCA9685 / arayüz bölücü)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 450 mm; Manhattan 351 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 16 B7, 17 K1 · **sonlandırma:** sonar pin bloğu (içe bakar, B7) + dişi uçlu jumper teli (O-4 r); öbür uçlar üç ayrı noktaya (PCA K11, arayüz kartı)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| VCC 5 V | HC-SR04 orta · VCC | Arayüz kartı · çevre 5 V |  |
| Trig | HC-SR04 orta · Trig | PCA9685 · K11 | PCA K11 `sonar_orta_trig` |
| Echo | HC-SR04 orta · Echo | Arayüz kartı · sonar orta bölücü girişi |  |
| GND | HC-SR04 orta · GND | Arayüz kartı · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:233`, `planlama/adim3/elektrik.md:494`, `planlama/adim3/pin-haritasi.md:126-128`, `planlama/adim3/pin-haritasi.md:84-86` · 10.11 dökümü: #40, #48, #49 (birleşti: sonar başına tek kablo)

#### Q03 · Sonar sol (HC-SR04) → elektronik katı

- **Devre:** sinyal (sonar) · **dal:** F4 · **durum:** kesin
- **Uçlar:** HC-SR04 sol (VCC / Trig / Echo / GND) → Elektronik katı (çevre 5 V / PCA9685 / arayüz bölücü)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** 22 AWG çok telli sinyal teli (4 renk: + kırmızı, GND siyah, sinyal sarı / mavi); makaron mor
- **Koruma:** Çevre hat sigortası 2 A mini (G19'un XL4016 çevre OUT+ ucunun dibinde) (`hat-cevre`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F4 → XL4016-cevre → hat-cevre
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 500 mm; Manhattan 384 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 16 B7, 17 K1 · **sonlandırma:** sonar pin bloğu (içe bakar, B7) + dişi uçlu jumper teli (O-4 r); öbür uçlar üç ayrı noktaya (PCA K12, arayüz kartı)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| VCC 5 V | HC-SR04 sol · VCC | Arayüz kartı · çevre 5 V |  |
| Trig | HC-SR04 sol · Trig | PCA9685 · K12 | PCA K12 `sonar_sol_trig` |
| Echo | HC-SR04 sol · Echo | Arayüz kartı · sonar sol bölücü girişi |  |
| GND | HC-SR04 sol · GND | Arayüz kartı · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:233`, `planlama/adim3/elektrik.md:494`, `planlama/adim3/pin-haritasi.md:126-128`, `planlama/adim3/pin-haritasi.md:84-86` · 10.11 dökümü: #40, #48, #49 (birleşti: sonar başına tek kablo)

### etek (F1) (4)

#### A01 · F5 2 A → acil stop mantarı (NC) girişi

- **Devre:** acil stop · **dal:** F5-mantar-oncesi · **durum:** kesin
- **Uçlar:** Sigorta kutusu (F5 2 A çıkışı) → Acil stop mantarı NP2 BE102 (NC giriş)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron yeşil
- **Koruma:** F5 2 A (sigorta kutusu) (`F5`, 2 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F5 · **ortak dönüş:** A03, A05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 158 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1, 33 F1 · **sonlandırma:** mantar kontak bloğu vidası (pabuç / yüksük)
- **Uç türü (uc_turu):** a: sigorta-kutusu · b: modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Sigorta kutusu · F5 çıkışı | Acil stop mantarı · NC giriş |  |

- Kaynak: `planlama/adim3/elektrik.md:339`, `planlama/adim3/elektrik.md:249`, `planlama/adim3/elektrik.md:369`, `planlama/adim3/kablolama-on-kararlar.md:358` · 10.11 dökümü: #41 (bölündü)

#### A02 · Mantar NC çıkışı → röle K1 bobini (+, 86)

- **Devre:** acil stop · **dal:** mantar-sonrasi · **durum:** kesin
- **Uçlar:** Acil stop mantarı (NC çıkış) → Röle K1 (86 (bobin +))
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron yeşil
- **Koruma:** F5 2 A (sigorta kutusu) (`F5`, 2 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F5 → mantar · **ortak dönüş:** A03
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 450 mm; Manhattan 332 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: düğüm güç panelinde: mantar → röle. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1, 33 F1 · **sonlandırma:** mantar vidası → Ö4 için iki uçlu yer (2 pin 5,08 klemens, köprülü) → acil stop düğüm kartı (güç panelinde küçük pertinaks parçası): iki adet 2 pin 5,08 mm vidalı klemens, dört ucu kart üstünde lehimle köprülü; ince telli uç kalaylanmaz, bükülür (yüksük varsa yüksük; ek tur, orkestratör kararı 14.11, WAGO 2273 ince telli almaz) → röle soketi kuyruğu (O-6 a / c)
- **Uç türü (uc_turu):** a: klemens-508, modul-vidali · b: klemens-508, lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Acil stop mantarı · NC çıkış | Acil stop düğümü (mantar NC çıkışı) · + |  |
| + | Acil stop düğümü (mantar NC çıkışı) · + | Röle K1 · 86 |  |

- Not: Ö4 (elde taşınan acil stop) açık: Ahmet + Efe; köprü Ö4 gelirse kumandalı rölenin kontağıyla değişir.
- Kaynak: `planlama/adim3/elektrik.md:249`, `planlama/adim3/elektrik.md:443`, `planlama/adim3/kablolama-on-kararlar.md:265-266` · 10.11 dökümü: #41 (bölündü)

#### G03 · Ana sigorta → ana anahtar

- **Devre:** güç 12 V ana hat · **dal:** aku-ana · **durum:** kablajda teyit edilecek
- **Uçlar:** Ana sigorta yuvası 30 A (çıkış) → Ana anahtar ASW-A01 (giriş)
- **Kesit:** 12 AWG (3,31 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** Ana sigorta 30 A (standart bıçak, kablolu yuva) (`ana-sigorta`, 30 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta · **ortak dönüş:** G05
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 450 mm; Manhattan 346 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1, 33 F1 · **sonlandırma:** anahtar ucu halka pabuç (saplama ölçüsü teslimde)
- **Uç türü (uc_turu):** a: lehim · b: pabuc

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Ana sigorta yuvası · çıkış | Ana anahtar · giriş |  |

- Teyit: anahtar saplama ölçüsü ve pabuç; K1'de anahtar ucu bantlı bırakılır, F1'de bağlanır
- Teyit: ana hat ayrı döşenir (sıkı demet yok); kablo üstündeki sıcaklık sınıfı ≥ 80 °C (istisna ana-hat-12awg, O-15)
- Kaynak: `planlama/adim3/elektrik.md:323`, `raporlar/kaynaklar/06-aku-secimi.md:162` · 10.11 dökümü: #2

#### G06 · Şarj kolu: akü + → 7,5 A hat sigortası → XT60E-M şarj girişi (+ / −)

- **Devre:** güç 12 V şarj · **dal:** sarj · **durum:** kablajda teyit edilecek
- **Uçlar:** Ana anahtar ASW-A01 (giriş (akü tarafı; ana sigortanın yük tarafı) / yıldız barası) → XT60E-M panel şarj girişi (+ / −)
- **Kesit:** 16 AWG (1,31 mm²); 16 AWG: 7,5 A hat sigortası ≤ 16 AWG'nin etekteki 8,2 A'i (45 °C düzeltmeli; O-1 / O-2, düzeltme turu 1) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** Şarj hat sigortası 7,5 A mini (akü tarafındaki ucun dibinde) (`hat-sarj`, 7,5 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → hat-sarj
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 400 mm; Manhattan 299 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: şarj girişi CAD'de yok (etek üst plakası arkası): ana anahtar vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 17 K1, 33 F1 · **sonlandırma:** ana anahtar girişinde mavi M5 halka pabuç (G03 ile aynı saplama); 7,5 A mini sigorta yuvası bu ucun dibinde, kuyruğuna lehim + makaron; panel ucu XT60E-M lehim; − yıldız barasına mavi pabuç
- **Uç türü (uc_turu):** a: lehim, pabuc · b: bara-pabuc, lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Ana anahtar · giriş | XT60E-M şarj girişi · + | ara: 7,5 A mini hat sigortası yuvası (16 AWG kuyruklu), ana anahtar girişindeki ucun dibinde (O-17) |
| − | XT60E-M şarj girişi · − | Yıldız barası · GND |  |

- Teyit: akü ayrı şarj ucuyla gelirse o kullanılır (O-17)
- Not: O-17 (orkestratör kararı, 14.11.2026): + ana sigortanın yük tarafına, ana anahtarın akü tarafına: ana anahtar kapalıyken şarj edilir, robot enerjisiz; şarj akımı ana sigortadan da geçer. − ana dönüş yıldız noktasına. Sigorta akü tarafındaki ucun dibinde (kısa devrede akü besler). Sigorta değeri ve gerekçesi kesit_not alanında; şarj cihazı IMAX B6 (Robocombo sayfası: en çok 50 W). XT60E-M erkek panel girişinin pinleri ana anahtar öncesinde: **pinler her zaman akü geriliminde**, kapak / koruyucu takılır (K50).
- Kaynak: `planlama/adim3/elektrik.md:372`, `planlama/adim3/elektrik.md:91`, `raporlar/kaynaklar/06-aku-secimi.md:165`, `planlama/maliyet.json:111` · 10.11 dökümü: #6

### gövde (K2) (3)

#### S09 · Servo uzatması: kafa pan (PCA K4, hat C)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı C (kafa) (pan çıkışı) → Kafa pan servosu (MG996R) (servo kablosu)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 C akım sınırı (`XL4016-C`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-C → XL4016-C
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 1.550 mm; Manhattan 1.215 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: dağıtım kartı C → XL4016 C vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 32 K2, 25 E2a (öneri) · **sonlandırma:** dağıtım kartı C'nin 3 pinli çıkışı; servo ucu JR
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı C (kafa) · pan V+ | kafa pan servosu · V+ |  |
| GND | Dağıtım kartı C (kafa) · pan GND | kafa pan servosu · GND |  |
| sinyal | Dağıtım kartı C (kafa) · pan sinyal | kafa pan servosu · sinyal | PCA K4 `kafa_pan` |

- Kaynak: `planlama/adim3/elektrik.md:129-132`, `planlama/adim3/elektrik.md:330`, `planlama/adim3/pin-haritasi.md:120` · 10.11 dökümü: #30

#### U06 · Hub 2 → ESP32 USB (VBUS'ta 1N5819)

- **Devre:** USB · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** USB hub (4'lü) (port 2) → ESP32 DevKit (micro USB)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 971 mm / önerilen 1.360 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.ESP32 USB`)
- **Rehber adımı:** 32 K2, 49 F5 · **sonlandırma:** VBUS teli kesilip 1N5819 seri lehimlenir + makaron (kartın kendi VBUS→VIN diyodu doğrulanırsa gerekmez)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** USB-A → micro B, 2 m (maliyet.json 'ESP32 – Pi USB kablosu')

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| USB | USB hub · port 2 | ESP32 · micro USB | VBUS teline seri 1N5819, anot hub (Pi) tarafında |

- Teyit: ESP32 kartında VBUS→VIN diyodu (EL:285); KT5 hub girişi gerilimi
- Kaynak: `planlama/adim3/elektrik.md:39`, `planlama/adim3/elektrik.md:83`, `planlama/adim3/elektrik.md:283-285`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.ESP32 USB` · 10.11 dökümü: #57

#### U05 · Hub 1 → göğüs ekranı Touch

- **Devre:** USB · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** USB hub (4'lü) (port 1) → Göğüs ekranı 11,6" (Touch micro USB)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 395 mm / önerilen 640 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.USB dokunmatik`)
- **Rehber adımı:** 35 F3, 49 F5 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** USB-A → micro B (v4 2 m); ekran ucunda 90° micro B adaptör (maliyet.json 'ESP32 – Pi USB kablosu' (2 adet) + 90° micro USB adaptör (koşullu))

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| USB | USB hub · port 1 | Göğüs ekranı · Touch micro USB |  |

- Teyit: port girintisi ve 90° fiş (P1.4)
- Kaynak: `planlama/adim3/elektrik.md:64`, `planlama/adim3/elektrik.md:82`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.USB dokunmatik` · 10.11 dökümü: #56

### boyun (5)

#### G17 · F3 5 A → kafa 12 V çifti (taban → direk → boyun → kafa girişi)

- **Devre:** güç 12 V (kafa dalı) · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Sigorta kutusu (F3 5 A çıkışı / Yıldız barası) → Kafa giriş klemensi (P6KE18A) (+12 V / GND)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F3 5 A (sigorta kutusu) (`F3`, 5 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 2.050 mm; Manhattan 1.633 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: kafa giriş klemensi CAD'de yok: D24V50F5 / SY8205'ten uzak olanı. toplam boy kaynakta yok (kablo-kurali-notu:26); P10.7b'de ölçülecek
- **Rehber adımı:** 17 K1, 32 K2, 29 E3a · **sonlandırma:** boyundan fişsiz geçer, uç kontakları / pabuçları geçirdikten sonra takılır (KOK §4 sıra 5); kafa ucu: kafa giriş kartı (küçük pertinaks parçası, P6KE18A üstünde): üç adet 2 pin 5,08 mm vidalı klemens, + uçları ve − uçları kart üstünde lehimle köprülü; ince telli uç kalaylanmaz, bükülür (yüksük varsa yüksük; ek tur, orkestratör kararı 14.11, WAGO 2273 ince telli almaz)
- **Uç türü (uc_turu):** a: bara-pabuc, sigorta-kutusu · b: klemens-508

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Sigorta kutusu · F3 çıkışı | Kafa giriş klemensi · +12 V |  |
| − | Yıldız barası · GND | Kafa giriş klemensi · GND |  |

- Teyit: KT4: boyun içi geçiş ve pan ±90 / tilt ±13'te büküm
- Kaynak: `planlama/adim3/elektrik.md:333`, `planlama/adim3/elektrik.md:46`, `planlama/adim3/elektrik.md:367`, `planlama/d158/kablo-kurali-notu.md:26` · 10.11 dökümü: #33

#### S10 · Servo uzatması: kafa tilt (PCA K9, hat C)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kablajda teyit edilecek
- **Uçlar:** Dağıtım kartı C (kafa) (tilt çıkışı) → Kafa tilt servosu (MG996R) (servo kablosu)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 C akım sınırı (`XL4016-C`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-C → XL4016-C
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 1.750 mm; Manhattan 1.380 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: dağıtım kartı C → XL4016 C vekil. toplam boy kaynakta yok (kablo-kurali-notu:27); P10.7b'de ölçülecek
- **Rehber adımı:** 32 K2, 28 E2 (öneri) · **sonlandırma:** dağıtım kartı C'nin 3 pinli çıkışı; servo ucu JR
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı C (kafa) · tilt V+ | kafa tilt servosu · V+ |  |
| GND | Dağıtım kartı C (kafa) · tilt GND | kafa tilt servosu · GND |  |
| sinyal | Dağıtım kartı C (kafa) · tilt sinyal | kafa tilt servosu · sinyal | PCA K9 `kafa_tilt` |

- Teyit: KT4: boyun içi geçiş, büküm
- Kaynak: `planlama/adim3/elektrik.md:129-132`, `planlama/adim3/elektrik.md:330`, `planlama/adim3/pin-haritasi.md:125`, `planlama/adim3/kablolama-on-kararlar.md:125`, `planlama/d158/kablo-kurali-notu.md:27` · 10.11 dökümü: #31

#### AU3 · PAM8403 → hoparlör (boyundan, gövde orta bandı sağ)

- **Devre:** ses · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** PAM8403 (L çıkış + / −) → Hoparlör 4 Ω 3 W (+ / −)
- **Kesit:** — (2 × 0,50 mm² kordon (liste ürünü)) · **renk:** tel türü seçilince (listede sinyal teli yok); makaron beyaz
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 824 mm / önerilen 1.030 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.Hoparlor`)
- **Rehber adımı:** 31 E4, 32 K2, 34 F2 · **sonlandırma:** iki uç lehim; boyundan fişsiz geçer (sıra 4)
- **Uç türü (uc_turu):** a: lehim · b: lehim
- **Hazır kablo:** 2 × 0,50 kordon (maliyet.json 'Hoparlör kablosu ~1,1 m' (koşullu, K4))

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | PAM8403 · L+ | Hoparlör · + |  |
| − | PAM8403 · L− | Hoparlör · − |  |

- Teyit: KT4: boyun içi geçiş
- Not: K4 Ahmet'in kayıtlı kararı: kalem koşullu kalır, sipariş yine verilir (O-10 b).
- Kaynak: `planlama/adim3/elektrik.md:28`, `planlama/adim3/elektrik.md:275`, `planlama/adim3/kablolama-on-kararlar.md:125-126`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.Hoparlor` · 10.11 dökümü: #62

#### U03 · Pi USB 3 → hub uzatması (boyundan) → USB hub

- **Devre:** USB · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Raspberry Pi 5 (USB 3) → USB hub (4'lü) (kendi 130 mm kablosunun dişi ucu)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 617 mm / önerilen 920 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.Hub uzatmasi`); hub'ın sabit 130 mm kablosu dahil yol; + 150 mm kapak sökme payı
- **Rehber adımı:** 31 E4, 32 K2, 49 F5 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** USB 2.0 A erkek → A dişi uzatma, ~1 m; şart: usb_surum 2.0, erkek_fis_govdesi_mm_en_cok [13, 7], gecis_sirasi 1 (maliyet.json 'USB-A uzatma ~1 m (Pi → hub)' (koşullu, K4))

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| USB | Raspberry Pi 5 · USB 3 | USB hub · giriş (130 mm kablo + uzatma) |  |

- Teyit: KT4: tünel deneme parçasında fiş geçişi; HDMI'den önce geçirilir
- Teyit: satır fiyat bekliyor: şarta uyan ürün onaylı satıcılarda yok; teslimde fiş ölçüsü (O-11 b)
- Not: K4 Ahmet'in kayıtlı kararı: kalem koşullu kalır, sipariş yine verilir (O-10 b).
- Kaynak: `planlama/adim3/elektrik.md:37`, `planlama/adim3/elektrik.md:80`, `planlama/adim3/kablolama-on-kararlar.md:140-146`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.Hub uzatmasi` · 10.11 dökümü: #54

#### H02 · Pi micro HDMI 1 → göğüs ekranı (boyundan)

- **Devre:** HDMI · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Raspberry Pi 5 (micro HDMI 1) → Göğüs ekranı 11,6" (HDMI (90° adaptör))
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 757 mm / önerilen 950 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.HDMI`)
- **Rehber adımı:** 32 K2, 35 F3 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** micro HDMI → HDMI A, ~1–1,5 m; şart: dis_cap_mm_en_cok 6, micro_hdmi_fis_kalinlik_mm_en_cok 7, micro_hdmi_fis_genislik_mm_en_cok 18, micro_hdmi_fis_boy_mm_yaklasik_en_cok 30, gecis_sirasi 2 (maliyet.json 'Göğüs ekranı HDMI kablosu' + 90° HDMI adaptör (koşullu))

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| HDMI | Raspberry Pi 5 · micro HDMI 1 | Göğüs ekranı · HDMI |  |

- Teyit: KT4: fiş geçişi, 1080p masa denemesi, büküm
- Teyit: teslimde dış çap Ø ≤ 6 mm ölçülür; karşılamazsa KOK §4 yedek yolları (O-11 b)
- Not: Listedeki kablo alınır, teslimde çap ölçülür (O-11 b); onaylı satıcı dışı Ahmet'in kararı.
- Kaynak: `planlama/adim3/elektrik.md:63`, `planlama/adim3/elektrik.md:37`, `planlama/adim3/kablolama-on-kararlar.md:132-143`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.HDMI` · 10.11 dökümü: #59

### kafa içi (11)

#### K01 · Kafa girişi (P6KE18A) → D24V50F5 girişi

- **Devre:** güç 12 V (kafa dalı) · **dal:** F3 · **durum:** kesin
- **Uçlar:** Kafa giriş klemensi (+12 V / GND) → Pololu D24V50F5 (VIN / GND)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F3 5 A (sigorta kutusu) (`F3`, 5 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 126 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: kafa giriş klemensi CAD'de yok: SY8205 yanı vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 29 E3a · **sonlandırma:** kafa giriş ucu: kafa giriş kartı (küçük pertinaks parçası, P6KE18A üstünde): üç adet 2 pin 5,08 mm vidalı klemens, + uçları ve − uçları kart üstünde lehimle köprülü; ince telli uç kalaylanmaz, bükülür (yüksük varsa yüksük; ek tur, orkestratör kararı 14.11, WAGO 2273 ince telli almaz); D24V50F5 ucu lehim
- **Uç türü (uc_turu):** a: klemens-508 · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Kafa giriş klemensi · +12 V | D24V50F5 · VIN |  |
| − | Kafa giriş klemensi · GND | D24V50F5 · GND |  |

- Kaynak: `planlama/adim3/elektrik.md:46-47`, `planlama/adim3/elektrik.md:333` · 10.11 dökümü: #34

#### K02 · Kafa girişi (P6KE18A) → SY8205 girişi

- **Devre:** güç 12 V (kafa dalı) · **dal:** F3 · **durum:** kesin
- **Uçlar:** Kafa giriş klemensi (+12 V / GND) → SY8205 (IN+ / IN−)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F3 5 A (sigorta kutusu) (`F3`, 5 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 126 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: kafa giriş klemensi CAD'de yok: D24V50F5 yanı vekil. P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 29 E3a · **sonlandırma:** kafa giriş ucu: kafa giriş kartı (küçük pertinaks parçası, P6KE18A üstünde): üç adet 2 pin 5,08 mm vidalı klemens, + uçları ve − uçları kart üstünde lehimle köprülü; ince telli uç kalaylanmaz, bükülür (yüksük varsa yüksük; ek tur, orkestratör kararı 14.11, WAGO 2273 ince telli almaz); SY8205 ucu modülün vidalı klemensi
- **Uç türü (uc_turu):** a: klemens-508 · b: modul-vidali

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Kafa giriş klemensi · +12 V | SY8205 · IN+ |  |
| − | Kafa giriş klemensi · GND | SY8205 · IN− |  |

- Kaynak: `planlama/adim3/elektrik.md:46`, `planlama/adim3/elektrik.md:49`, `planlama/adim3/elektrik.md:336` · 10.11 dökümü: #35

#### K03 · D24V50F5 5 V → Raspberry Pi 5 USB-C

- **Devre:** 5 V Pi · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Pololu D24V50F5 (VOUT / GND) → Raspberry Pi 5 (USB-C güç girişi)
- **Kesit:** 18 AWG (0,82 mm²); 18 AWG (düzeltme turu 1, madde 4 b): D24V50F5'in akım sınırı belgelenmemiş; kayıtlı istisna kafa-5v-donusturucu-arkasi, 18 AWG kafada 5,25 A ≥ modülün 5 A anma çıkışı · **renk:** + kırmızı, − / GND siyah; makaron mavi
- **Koruma:** Pololu D24V50F5 aşırı akım koruması (`D24V50F5`, akım sınırı belgelenmemiş) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 200 mm; Manhattan 159 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`. belgede ~10 cm (EL:279); CAD'de tasarlanmış yol yok, P10.7b'de ölçülecek
- **Rehber adımı:** 29 E3a · **sonlandırma:** USB Type-C 24 pin test kartına lehim (MJ:102)
- **Uç türü (uc_turu):** a: lehim · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| +5 V | D24V50F5 · VOUT (P6KE6V8A) | Raspberry Pi 5 · USB-C VBUS |  |
| GND | D24V50F5 · GND | Raspberry Pi 5 · USB-C GND |  |

- Teyit: KT1: Pi stres + en yüksek ses; get_throttled = 0x0
- Not: Düzeltme turu 1 (orkestratör kararı, madde 4 b): kesit ortam düzeltmeli kurala (kafa 49 °C) ve gerilim düşümüne göre. D24V50F5'in akım sınırı belgelenmediği için kayıtlı istisna kafa-5v-donusturucu-arkasi.
- Kaynak: `planlama/adim3/elektrik.md:279`, `planlama/adim3/elektrik.md:47`, `planlama/adim3/elektrik.md:282`, `planlama/maliyet.json:102` · 10.11 dökümü: #36

#### AU1 · ReSpeaker 3,5 mm jakı → ses bölücüsü (10 kΩ / 2,2 kΩ)

- **Devre:** ses · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** ReSpeaker Mic Array v2.0 (3,5 mm jak (sol kanal + kılıf)) → Ses bölücüsü (giriş)
- **Kesit:** — (hazır 3,5 mm kablo (kalkanlı, iki damar); kısa L fişli) · **renk:** tel türü seçilince (listede sinyal teli yok); makaron beyaz
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 300 mm; Manhattan 201 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: ses bölücüsü PAM giriş pedlerinin dibinde (O-9). yol ölçülmedi (KOK:340; CAD'deki 36 / 40 mm eski ses kartı ucunundu); P10.7b'de ölçülecek
- **Rehber adımı:** 31 E4 · **sonlandırma:** ReSpeaker ucu 3,5 mm (L) fiş; öbür uç kesilip bölücüye lehim
- **Uç türü (uc_turu):** a: konnektor · b: lehim
- **Hazır kablo:** 3,5 mm stereo, bir ucu L fiş, kısa (maliyet.json 'L 3,5 mm fişli kısa kablo' (fiyat bekliyor, K4))

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| sol kanal | ReSpeaker · 3,5 mm sol | Ses bölücüsü · 10 kΩ girişi |  |
| kalkan | ReSpeaker · 3,5 mm kılıf | Ses bölücüsü · GND | kalkan yalnız PAM GND'sine (KOK:182) |

- Teyit: KT2: bağlamadan önce kılıf ↔ USB GND sürekliliği (≤ 1 Ω), seviye ölçümü ve bölücü değeri, jak yönü
- Not: K4 Ahmet'in kayıtlı kararı: kalem koşullu kalır, sipariş yine verilir (O-10 b).
- Kaynak: `planlama/adim3/kablolama-on-kararlar.md:182`, `planlama/adim3/kablolama-on-kararlar.md:190-195`, `planlama/adim3/kablolama-on-kararlar.md:201-202`, `planlama/adim3/kablolama-on-kararlar.md:340`, `planlama/adim3/elektrik.md:28` · 10.11 dökümü: #61 (uç değişti: USB ses kartı → ReSpeaker)

#### AU2 · Ses bölücüsü → PAM8403 sol girişi

- **Devre:** ses · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Ses bölücüsü (çıkış (2,2 kΩ → GND düğümü)) → PAM8403 (sol giriş / GND)
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** tel türü seçilince (listede sinyal teli yok); makaron beyaz
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 100 mm; sabit: bölücü PAM giriş pedlerinin dibinde (O-9) (`planlama/adim3/kablolar.json#kararlar`). P10.7b'de ölçülecek (CAD'de tasarlanmış yol yok)
- **Rehber adımı:** 31 E4 (öneri) · **sonlandırma:** bölücü PAM8403 giriş pedlerinin dibinde, kablo üstünde, makaronla (O-9 a)
- **Uç türü (uc_turu):** a: lehim · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| sinyal | Ses bölücüsü · çıkış | PAM8403 · L giriş |  |
| GND | Ses bölücüsü · GND | PAM8403 · GND (giriş) |  |

- Teyit: KT2: alt direnç ölçümle seçilir
- Not: Ses bölücüsü PAM8403 giriş pedlerinin dibinde, kablo üstünde: ayrı bir kablodan çok lehim işi (bağımsız kontrol açık iş 16). Kablo sayımını değiştirmez.
- Kaynak: `planlama/adim3/kablolama-on-kararlar.md:190-195`, `planlama/adim3/kablolama-on-kararlar.md:201` · 10.11 dökümü: yeni (ses bölücüsü)

#### C01 · Pi CSI → Camera Module 3 (FPC 300 mm)

- **Devre:** CSI · **dal:** F3 · **durum:** kesin
- **Uçlar:** Raspberry Pi 5 (CSI (22 pin 0,5 mm)) → Kamera (Camera Module 3) (15 pin 1 mm)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 300 mm; sabit: hazır FPC 300 mm (liste satırı) (`planlama/maliyet.json#kalemler.31`). liste boyu 300 mm; kafa içi yol CAD'de tasarlanmadı, P10.7b'de ölçülecek
- **Rehber adımı:** 31 E4 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** Raspberry Pi 5 kamera FPC, 300 mm (maliyet.json 'Kamera kablosu')

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| FPC | Raspberry Pi 5 · CSI | Kamera · FPC |  |

- Kaynak: `planlama/adim3/elektrik.md:300`, `planlama/adim3/elektrik.md:335` · 10.11 dökümü: #60

#### H01 · Pi micro HDMI 0 → 10,1" QLED (30 cm şerit)

- **Devre:** HDMI · **dal:** F3 · **durum:** kesin
- **Uçlar:** Raspberry Pi 5 (micro HDMI 0) → Kafa ekranı 10,1" QLED (HDMI)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 254 mm / liste boyu 300 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kafa_ici_qled.HDMI (serit, 2 lehimsiz fis)`)
- **Rehber adımı:** 31 E4 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** DIY HDMI 30 cm şerit + micro HDMI fiş + HDMI fiş (lehimsiz) (maliyet.json 'Ekran kablosu' satırları)

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| HDMI | Raspberry Pi 5 · micro HDMI 0 | QLED · HDMI |  |

- Kaynak: `planlama/adim3/elektrik.md:57`, `planlama/adim3/elektrik.md:335`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kafa_ici_qled` · 10.11 dökümü: #58

#### K04 · SY8205 5 V → 10,1" QLED Power (micro USB)

- **Devre:** 5 V Pi (ekran hattı) · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** SY8205 (OUT+ / OUT− (P6KE6V8A)) → Kafa ekranı 10,1" QLED (Power micro USB)
- **Kesit:** — (hazır 30 cm USB-A → micro B kablonun A ucu kesilir (EL:57); damar kesiti ürün sayfasında yok) · **renk:** + kırmızı, − / GND siyah; makaron mavi
- **Koruma:** SY8205 düşürücü (kafa ekranı) (`SY8205`, akım sınırı belgelenmemiş) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → SY8205
- **Boy:** yol 114 mm / liste boyu 300 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kafa_ici_qled.Power USB (30 cm, A ucu kesik)`)
- **Rehber adımı:** 31 E4 · **sonlandırma:** SY8205 klemensine kesik uç; ekran ucu micro B fiş
- **Uç türü (uc_turu):** a: modul-vidali · b: konnektor
- **Hazır kablo:** USB-A → micro B, 30 cm (A ucu kesilir) (maliyet.json 'Kafa ekranı 5 V besleme kablosu')

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| +5 V | SY8205 · OUT+ (P6KE6V8A) | QLED · Power micro USB VBUS |  |
| GND | SY8205 · OUT− | QLED · Power micro USB GND |  |

- Teyit: Touch VBUS ile Power arası köprü ölçülecek (EL:56)
- Teyit: kesit: teslimde hazır micro USB kablonun üstündeki kesit yazısı okunur; 24 AWG'den inceyse ya da yazı yoksa 18 AWG + micro B fişle yeniden yapılır (O-21, kafa-5v-donusturucu-arkasi şartı)
- Not: Kafa ekranı (Waveshare 10,1" QLED) akımı: üretici sayfasında güç / akım değeri yok (docs.waveshare.com/10.1HP-CAPQLED-B: yalnız 'Micro USB, 5 V'; kutudan çıkan 5 V adaptörün etiket akımı bir tüketim değeri değil); tasarımda 0,9 A varsayım (planlama/adim3/elektrik.md:25), ölçülmedi. Teslimde ölçülür.
- Kaynak: `planlama/adim3/elektrik.md:49`, `planlama/adim3/elektrik.md:57`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kafa_ici_qled` · 10.11 dökümü: #37

#### K05 · D24V50F5 5 V → PAM8403 5 V

- **Devre:** 5 V Pi · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Pololu D24V50F5 (VOUT / GND) → PAM8403 (5 V / GND)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron mavi
- **Koruma:** Pololu D24V50F5 aşırı akım koruması (`D24V50F5`, akım sınırı belgelenmemiş) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 64 mm / önerilen 80 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.PAM 5 V`)
- **Rehber adımı:** 31 E4 · **sonlandırma:** lehim
- **Uç türü (uc_turu):** a: lehim · b: lehim

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| +5 V | D24V50F5 · VOUT (P6KE6V8A) | PAM8403 · 5 V |  |
| GND | D24V50F5 · GND | PAM8403 · GND |  |

- Teyit: KT1: K10 a masa denemesine bağlı; geçmezse kaynak ucu SY8205
- Kaynak: `planlama/adim3/elektrik.md:48`, `planlama/adim3/elektrik.md:52-54`, `planlama/adim3/kablolama-on-kararlar.md:341`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.PAM 5 V` · 10.11 dökümü: #38

#### U01 · Pi USB 1 → ReSpeaker Mic Array v2.0

- **Devre:** USB · **dal:** F3 · **durum:** kesin
- **Uçlar:** Raspberry Pi 5 (USB 1) → ReSpeaker Mic Array v2.0 (micro USB)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 85 mm / önerilen 110 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.Dizi USB`)
- **Rehber adımı:** 31 E4 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** USB-A → micro B, kısa (~11 cm) (maliyet.json 'Kısa micro USB kablo (ReSpeaker)' (koşullu, K4))

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| USB | Raspberry Pi 5 · USB 1 | ReSpeaker · micro USB |  |

- Not: K4 Ahmet'in kayıtlı kararı: kalem koşullu kalır, sipariş yine verilir (O-10 b).
- Kaynak: `planlama/adim3/elektrik.md:78`, `planlama/adim3/elektrik.md:334`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.Dizi USB` · 10.11 dökümü: #52

#### U04 · Pi USB 4 → 10,1" QLED Touch

- **Devre:** USB · **dal:** F3 · **durum:** kablajda teyit edilecek
- **Uçlar:** Raspberry Pi 5 (USB 4) → Kafa ekranı 10,1" QLED (Touch micro USB)
- **Kesit:** — (hazır kablo) · **renk:** üreticinin kablosu; makaron yok (hazır kablo)
- **Koruma:** — · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F3 → D24V50F5
- **Boy:** yol 217 mm / liste boyu 350 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kafa_ici_qled.Touch USB (kutu kablosu)`)
- **Rehber adımı:** 31 E4 · **sonlandırma:** hazır kablonun kendi fişleri (iki uç fişli, sonlandırma işi yok)
- **Uç türü (uc_turu):** a: konnektor · b: konnektor
- **Hazır kablo:** ekranın kutusundaki USB kablosu (350 mm)

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| USB | Raspberry Pi 5 · USB 4 | QLED · Touch micro USB |  |

- Teyit: Touch VBUS ↔ Power köprüsü ölçülecek (EL:56)
- Kaynak: `planlama/adim3/elektrik.md:81`, `planlama/adim3/elektrik.md:56`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kafa_ici_qled` · 10.11 dökümü: #55

### göğüs (1)

#### G21 · Göğüs regülatörü 12 V → 11,6" göğüs ekranı 12 V jakı

- **Devre:** güç 12 V (göğüs dalı) · **dal:** F6 · **durum:** kablajda teyit edilecek
- **Uçlar:** Göğüs ekranı regülatörü (OUT+ / OUT−) → Göğüs ekranı 11,6" (12 V jak)
- **Kesit:** 18 AWG (0,82 mm²) · **renk:** + kırmızı, − / GND siyah; makaron kırmızı
- **Koruma:** F6 3 A standart (sigorta kutusu) (`F6`, 3 A) · **acil stopta:** enerjili
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F6 → gogus-regulatoru
- **Boy:** yol 1.376 mm / önerilen 1.720 mm (`tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.12 V`); yol 'taban güç panelinden' çizildi; KOK §11 bunu regülatör → ekran boyu sayar, kutu → regülatör ayrı (G20)
- **Rehber adımı:** 32 K2, 35 F3 · **sonlandırma:** ekran ucu 90° DC jak fişi (ölçü ekran gelince; MJ 90° DC jak)
- **Uç türü (uc_turu):** a: modul-vidali · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| + | Göğüs regülatörü · OUT+ | Göğüs ekranı · 12 V jak + |  |
| − | Göğüs regülatörü · OUT− | Göğüs ekranı · 12 V jak − |  |

- Teyit: KT3: regülatör 12 V'a ayarlı, ilk açılışta F6 atmıyor; jak ölçüsü
- Kaynak: `planlama/adim3/elektrik.md:62`, `planlama/adim3/elektrik.md:69`, `planlama/adim3/kablolama-on-kararlar.md:105`, `planlama/adim3/kablolama-on-kararlar.md:342`, `tasarim/freecad/lale158/lale158-kontrol.json#kablo_ozet.kablo.12 V` · 10.11 dökümü: #43

### kol sağ (4)

#### S01 · Servo uzatması: sağ kol S1 (omuz öne-arka) (PCA K0)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı A (3 pinli çıkış 1) → Sağ kol S1 (omuz öne-arka) servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 A akım sınırı (`XL4016-A`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-A → XL4016-A
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 1.700 mm; Manhattan 1.325 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: sağ S1. S1 servosunun uzatma boyu dirsek-analiz.json s1_boy'da yok (yalnız dirsek, bilek, S2); P10.7b'de ölçülecek
- **Rehber adımı:** 32 K2, 36 F4, 41 G4 · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı A · çıkış 1 V+ | sağ S1 (omuz öne-arka) servosu · V+ |  |
| GND | Dağıtım kartı A · çıkış 1 GND | sağ S1 (omuz öne-arka) servosu · GND |  |
| sinyal | Dağıtım kartı A · çıkış 1 sinyal | sağ S1 (omuz öne-arka) servosu · sinyal | PCA K0 `sag_omuz` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:116` · 10.11 dökümü: #22

#### S02 · Servo uzatması: sağ kol S2 (omuz yana) (PCA K1)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı A (3 pinli çıkış 2) → Sağ kol S2 (omuz yana) servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 A akım sınırı (`XL4016-A`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-A → XL4016-A
- **Boy:** gereken 1.700 mm (`tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma.2.uzatma_mm`); dağıtım kartı → G2 öncesi ek (lehim + makaron ya da JR); konnektör payı 30 mm tahmini
- **Rehber adımı:** 32 K2, 36 F4, 39 G2 (öneri) · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı A · çıkış 2 V+ | sağ S2 (omuz yana) servosu · V+ |  |
| GND | Dağıtım kartı A · çıkış 2 GND | sağ S2 (omuz yana) servosu · GND |  |
| sinyal | Dağıtım kartı A · çıkış 2 sinyal | sağ S2 (omuz yana) servosu · sinyal | PCA K1 `sag_omuz_yan` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:117`, `tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma` · 10.11 dökümü: #23

#### S03 · Servo uzatması: sağ kol dirsek (PCA K2)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı A (3 pinli çıkış 3) → Sağ kol dirsek servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 A akım sınırı (`XL4016-A`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-A → XL4016-A
- **Boy:** gereken 1.856 mm (`tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma.0.uzatma_mm`); dağıtım kartı → kol içi ek (dirsek JR, bilek lehim); konnektör payı 30 mm tahmini
- **Rehber adımı:** 32 K2, 36 F4, 40 G3, 48 H1 · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı A · çıkış 3 V+ | sağ dirsek servosu · V+ |  |
| GND | Dağıtım kartı A · çıkış 3 GND | sağ dirsek servosu · GND |  |
| sinyal | Dağıtım kartı A · çıkış 3 sinyal | sağ dirsek servosu · sinyal | PCA K2 `sag_dirsek` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:118`, `tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma` · 10.11 dökümü: #24

#### S04 · Servo uzatması: sağ kol bilek (PCA K3)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı A (3 pinli çıkış 4) → Sağ kol bilek servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 A akım sınırı (`XL4016-A`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-A → XL4016-A
- **Boy:** gereken 1.856 mm (`tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma.1.uzatma_mm`); dağıtım kartı → kol içi ek (dirsek JR, bilek lehim); konnektör payı 30 mm tahmini
- **Rehber adımı:** 32 K2, 36 F4, 40 G3, 48 H1 · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı A · çıkış 4 V+ | sağ bilek servosu · V+ |  |
| GND | Dağıtım kartı A · çıkış 4 GND | sağ bilek servosu · GND |  |
| sinyal | Dağıtım kartı A · çıkış 4 sinyal | sağ bilek servosu · sinyal | PCA K3 `sag_bilek` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:119`, `tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma` · 10.11 dökümü: #25

### kol sol (4)

#### S05 · Servo uzatması: sol kol S1 (omuz öne-arka) (PCA K5)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı B (3 pinli çıkış 1) → Sol kol S1 (omuz öne-arka) servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 B akım sınırı (`XL4016-B`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-B → XL4016-B
- **Boy:** **tahmin, P10.7b'de ölçülecek:** ≤ 1.700 mm; Manhattan 1.329 mm, `tasarim/freecad/montaj/montaj-analiz.json#parcalar`; uç vekili: sol S1. S1 servosunun uzatma boyu dirsek-analiz.json s1_boy'da yok (yalnız dirsek, bilek, S2); P10.7b'de ölçülecek
- **Rehber adımı:** 32 K2, 36 F4, 41 G4 · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı B · çıkış 1 V+ | sol S1 (omuz öne-arka) servosu · V+ |  |
| GND | Dağıtım kartı B · çıkış 1 GND | sol S1 (omuz öne-arka) servosu · GND |  |
| sinyal | Dağıtım kartı B · çıkış 1 sinyal | sol S1 (omuz öne-arka) servosu · sinyal | PCA K5 `sol_omuz` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:121` · 10.11 dökümü: #26

#### S06 · Servo uzatması: sol kol S2 (omuz yana) (PCA K6)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı B (3 pinli çıkış 2) → Sol kol S2 (omuz yana) servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 B akım sınırı (`XL4016-B`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-B → XL4016-B
- **Boy:** gereken 1.700 mm (`tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma.2.uzatma_mm`); dağıtım kartı → G2 öncesi ek (lehim + makaron ya da JR); konnektör payı 30 mm tahmini
- **Rehber adımı:** 32 K2, 36 F4, 39 G2 (öneri) · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı B · çıkış 2 V+ | sol S2 (omuz yana) servosu · V+ |  |
| GND | Dağıtım kartı B · çıkış 2 GND | sol S2 (omuz yana) servosu · GND |  |
| sinyal | Dağıtım kartı B · çıkış 2 sinyal | sol S2 (omuz yana) servosu · sinyal | PCA K6 `sol_omuz_yan` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:122`, `tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma` · 10.11 dökümü: #27

#### S07 · Servo uzatması: sol kol dirsek (PCA K7)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı B (3 pinli çıkış 3) → Sol kol dirsek servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 B akım sınırı (`XL4016-B`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-B → XL4016-B
- **Boy:** gereken 1.856 mm (`tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma.0.uzatma_mm`); dağıtım kartı → kol içi ek (dirsek JR, bilek lehim); konnektör payı 30 mm tahmini
- **Rehber adımı:** 32 K2, 36 F4, 40 G3, 48 H1 · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı B · çıkış 3 V+ | sol dirsek servosu · V+ |  |
| GND | Dağıtım kartı B · çıkış 3 GND | sol dirsek servosu · GND |  |
| sinyal | Dağıtım kartı B · çıkış 3 sinyal | sol dirsek servosu · sinyal | PCA K7 `sol_dirsek` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:123`, `tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma` · 10.11 dökümü: #28

#### S08 · Servo uzatması: sol kol bilek (PCA K8)

- **Devre:** servo gücü + sinyal · **dal:** anahtarli-bara · **durum:** kesin
- **Uçlar:** Dağıtım kartı B (3 pinli çıkış 4) → Sol kol bilek servosu (servo kablosu (ek))
- **Kesit:** 22 AWG (0,33 mm²) · **renk:** servo uzatmasının üretici renkleri (GND koyu, V+ kırmızı, sinyal açık; teslimde bakılır); makaron sarı
- **Koruma:** XL4016 B akım sınırı (`XL4016-B`, 10 A) · **acil stopta:** enerjisiz
- **Besleme zinciri:** aku-bms → ana-sigorta → ana-anahtar → F1 → (K1-kontak ∥ K2-kontak) → hat-B → XL4016-B
- **Boy:** gereken 1.856 mm (`tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma.1.uzatma_mm`); dağıtım kartı → kol içi ek (dirsek JR, bilek lehim); konnektör payı 30 mm tahmini
- **Rehber adımı:** 32 K2, 36 F4, 40 G3, 48 H1 · **sonlandırma:** kart ucu 3 pinli başlık; servo ucu JR (S1 kaseti yarığı JR erkek 10,3 × 4 geçirir) / lehim ek
- **Uç türü (uc_turu):** a: konnektor · b: konnektor

| Damar | Uç A | Uç B | Pin / kanal / not |
|---|---|---|---|
| V+ | Dağıtım kartı B · çıkış 4 V+ | sol bilek servosu · V+ |  |
| GND | Dağıtım kartı B · çıkış 4 GND | sol bilek servosu · GND |  |
| sinyal | Dağıtım kartı B · çıkış 4 sinyal | sol bilek servosu · sinyal | PCA K8 `sol_bilek` |

- Not: Kol içi sıra (S1, S2, dirsek, bilek) main kanallar.yaml'da 'KABLAJDA DOĞRULA' notlu.
- Kaynak: `planlama/adim3/elektrik.md:225-227`, `planlama/adim3/elektrik.md:38`, `planlama/adim2/M1-kablo-yolu.md:26`, `planlama/adim3/pin-haritasi.md:124`, `tasarim/freecad/dirsek/dirsek-analiz.json#kablo.s1_boy.uzatma` · 10.11 dökümü: #29

## 10.11 dökümündeki 62 kabloyla eşleme

Döküm, rehberin 10.11 incelemesindeki kablo listesidir (depo dışı). Bölünen: bir döküm satırı birden çok kayda; birleşen: birden çok döküm satırı bir kayda.

| Döküm # | Tablodaki karşılığı |
|---|---|
| 1 | G02 |
| 2 | G03 |
| 3 | G04 |
| 4 | G05 |
| 5 | birleşti: yıldızdan dönüştürücü / BTS / kart toprak dalları ayrı kayıt değil; her güç çiftinin − damarı (G12–G22, SV1–SV3, G06) Yıldız barasıına gider |
| 6 | G06 |
| 7 | G07 |
| 8 | G08, G09 |
| 9 | G10, G11 |
| 10 | G12 |
| 11 | G13 |
| 12 | M01 |
| 13 | M02 |
| 14 | M03 |
| 15 | M04 |
| 16 | G14 |
| 17 | G15 |
| 18 | G16 |
| 19 | SV1 |
| 20 | SV2 |
| 21 | SV3 |
| 22 | S01 |
| 23 | S02 |
| 24 | S03 |
| 25 | S04 |
| 26 | S05 |
| 27 | S06 |
| 28 | S07 |
| 29 | S08 |
| 30 | S09 |
| 31 | S10 |
| 32 | G22 |
| 33 | G17 |
| 34 | K01 |
| 35 | K02 |
| 36 | K03 |
| 37 | K04 |
| 38 | K05 |
| 39 | G18, G19 |
| 40 | Q01, Q02, Q03 |
| 41 | A01, A02, A03, A06 |
| 42 | A04, A05 |
| 43 | G20, G21 |
| 44 | B01 |
| 45 | B02 |
| 46 | N01 |
| 47 | N02 |
| 48 | Q01, Q02, Q03 |
| 49 | Q01, Q02, Q03 |
| 50 | I01, I02 |
| 51 | P01, P02, P03 |
| 52 | U01 |
| 53 | çıktı: Pi USB 2 → ses kartı uzatması + L dirsek (14.11 KOK §5; ses kartı yedek olarak siparişte, takılmaz) |
| 54 | U03 |
| 55 | U04 |
| 56 | U05 |
| 57 | U06 |
| 58 | H01 |
| 59 | H02 |
| 60 | C01 |
| 61 | AU1 |
| 62 | AU3 |

Dökümde karşılığı olmayan yeni kayıtlar: G01, X01, AU2.

## Orkestratöre (karar gerekenler)

- **Ö4 (O-6, O-14):** Elde taşınan acil stop ve kendini tutma kontağı açık (Ahmet + Efe); tabloda Ö4 yeri köprülü klemens.
  - kablolama-on-kararlar.md §8
- **O-12:** Bas-konuş düğmesi listede, pin / kablo yok; Efe'ye sorulacak (orkestratör panodan soracak).
  - bilgi günlükte (P10.7a ikinci tur)
- **K52:** Göğüs regülatörünün panel yeri (G20'nin ucu ve boyu). Etkilenen: G20.
  - karar kuyruğunda K52
