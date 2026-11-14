**Hüküm: GEÇER.** Durduran bulgu yok. Üçüncü bakışın üç durduran bulgusu (D-A, D-B, D-C) kapandı. Ek tur tabloyu ve sipariş listesini bozmadı. Kalan bulgular kayıtlı açık iş olarak gidebilir. İkisi, belge Efe'ye ve rehbere gitmeden önce düzeltilmeli (§2-1, §2-2).

- **D-A kapandı.** Tablonun hiçbir ucu WAGO 2273'e gitmiyor. Kafa 12 V girişi ve acil stop düğümü 5,08 mm vidalı klemensli iki küçük karta geçti. 22 AWG uçlar klemense girmiyor; lehim + makaron, "kablajda teyit". `maliyet.json` (klemens 16, pertinaks 7, WAGO V3 dışı) tablodan sayınca tutuyor. Toplamlar ve bağımlı dosyalar güncel. Satıcı sayfası klemensin kesit aralığını gerçekten vermiyor. Aynı sınıftaki üretici veri sayfası 18 ve 16 AWG'yi aralığın içinde veriyor. "Kesin" yazılması kabul edilebilir.
- **D-B kapandı (söz verilen sınıf).** Üçüncü bakışın örneklerinin hepsi yakalanıyor: T44 ve T45 (G22 "7,5 A"), G19 "XL4016 çevre 8 A", K03 "20 AWG". `not` ve damar `ara` alanları sınanıyor. Kalan ince bir alt sınıf var (§2-2), ama sipariş bugünkü hâliyle bunu kablo aşırı yüküne çevirmiyor.
- **D-C kapandı.** Karşılaştırma koddan okundu. `elektrik.md` blok şeması ağaç olarak ayrıştırılıyor; her koruyucu ve anahtar şemadaki tek bir öğeye bağlanıyor. Üçüncü bakışın üç örneği ve benim 13 bozmamın hepsi yakalandı. Şema bozulunca ya da ayrıştırılamayınca da hata çıkıyor.

# P10.7a dördüncü (dar kapsamlı, kesin son) bağımsız bakış: ek tur sonrası

Kontrol 14.11.2026'da yapıldı, rapor 08:06'dan sonra yazıldı (saat saatten okundu).

- **Depo durumu:** Dal `lale-duzeltme`, HEAD `9a0c6fe`. Değişiklikler çalışma ağacında.
- **Bozma denemeleri:** Depo dışında, yalnız bu kontrolün geçici klasöründeki kopyada koştu. Her denemede kopya baştan kuruldu, bozma uygulandı, görünüm yeniden üretildi, denetim çıkış koduyla koştu.
- **Üçüncü bakışın betikleri:** `boz3.py` ve temiz tablosu yalnız okundu. Betik kopyalanıp yolları bu kontrolün klasörüne çevrildi; yollar koşmadan önce gözle doğrulandı.
- **Depoya dokunma:** Depoda yazılan tek dosya bu rapor. `git status` kontrolün başında ve sonunda aynı (45 satır). FreeCAD ve `rehber_uret.py` koşmadı.

Kısaltmalar:

| Kısaltma | Dosya |
|---|---|
| KJ | `planlama/adim3/kablolar.json` |
| KD | `planlama/adim3/kablolar_denetim.py` |
| EL | `planlama/adim3/elektrik.md` |
| PH | `planlama/adim3/pin-haritasi.md` |
| MJ | `planlama/maliyet.json` |
| GN | `planlama/d158/kablo-tablosu-gunluk.md` |
| K3R | üçüncü bakış, `planlama/d158/P107a-kontrol-3.md` |

## 1. Göndermeyi durduran bulgular

Yok.

Durdurma ölçütüne göre aranan üç sınıf ve sonuç:

- **Montajcıyı ya da siparişi yanlış yönlendiren değer:** §3.1, §3.4. Uç, pin, sigorta, kesit, acil stop bayrağı ve besleme zinciri üçüncü bakışın doğruladığı hâlle aynı. Parçaya girmeyen kablo kalmadı.
- **Güvenlik etkili tek adımlık hatayı geçiren denetim:** §3.2, §3.3. Kaçan sınıfların her birinin nasıl oluşacağı ve sonucu §2-2'de.
- **Gizlilik:** §3.7.

## 2. Kayıtlı açık iş olarak gidebilecek bulgular

Her bulguda yer, nasıl ölçüldüğü ve öneri var.

### 2-1. Yazılım notu "ön şarj GPIO5 LOW olana kadar" ön şarjı kısaltır

Bu madde **Efe listesi gönderilmeden önce** düzeltilmeli.

**Yer:**

- EL:448'in son cümlesi.
- GN:861, Efe maddesi 4.

**Sorun:**

- PC817 #2 baranın **varlığını** okur, dolduğunu okumaz. Modülün girişi 3,6–24 V (EL:235).
- τ = 5,6 Ω × 2 mF = 11 ms ile bara 3,6 V'a ≈ 4 ms'de çıkar. Yani GPIO5 birkaç ms içinde LOW olur.
- "LOW olana kadar" kuralı uygulanırsa K1, bara ≈ 4 V'tayken kapanır. Ön şarj neredeyse hiç olmamış gibi olur: ≈ 9 V'luk adım, ≈ 300 A tepe. Victron BMS'nin kesme riski EL:430-431'de anlatılıyor.
- Aynı E9 bölümünde EL:456 ve PH:263 hâlâ "300 ms bekle, sonra LOW olmalı" diyor. Böylece iki ayrı yönerge oluyor.
- Not PH'deki "K2 en çok 1 s" kuralıyla çelişmiyor (PH:430 `en_cok_ms` 1000). Çelişki 300 ms'lik alt sınırın kalkması.

**Kendi hesabım (boş akü, 12,8 V):**

- Bekleme yükü ≈ 5,7 W ile bara V(12,8 − V) / 5,6 = 5,7 denkleminden **9,41 V'ta** dengelenir. Ajanın ≈ 9,4 V'u doğru.
- Bara 8 V'tayken kondansatörlere ≈ 1,0 W kalır, 9 V'tayken ≈ 0,36 W. 0,20 J ≈ 0,2–0,55 s. Ajanın "0,2–0,5 s"i doğru, 300 ms'ye pay yok.
- Bu payın yokluğu zararsız. Bara boş aküde 9,4 V'un üstüne zaten çıkamaz, yani K1 her durumda ≈ 3,4 V'luk adımla kapanır (≈ 110 A, ≈ 60 µs). K1 kapandıktan sonra XL çıkış kondansatörleri buck'ın kendi akım sınırından dolar; aküden darbe çekmez.
- Ön şarj direnci 1 s boyunca: 12,8 V'ta ≈ 0,61 A, ≈ 2,1 W, ≈ 2 J; 14,6 V'ta ≈ 1,3 W. 11 W taş direnç için güvenli. Arıza durumunda 38 W × 1 s mevcut kural (EL:452-453), aşırı yük dayanımı zaten "doğrulanmadı".

**Öneri:**

- Not şöyle olsun: "en az 300 ms (boş aküde 500 ms) bekle, sonra GPIO5 LOW **teyidi**; K2 toplam ≤ 1 s; GPIO5 kondansatörlerin dolduğunu göstermez."
- Ya da madde Efe listesinden çıkıp açık işe yazılsın.
- Devre değeri değişmez.

### 2-2. `sayi_metin` kalan alt sınıfları (D-B'nin dışında kalan, yeni)

**Yer:** KD:1957-1960 (izinli küme) ve KD:1973-1976 (alanlar).

**Ölçüm (kendi bozmalarım):**

| Bozma | Sonuç |
|---|---|
| B06: G14 + `ara` "20 A mini" (zincirdeki F1'in değeri) | Kaçtı |
| B15: G17 adına "30 A" | Kaçtı |
| B16: G19 + `ara` "5 A mini" (zincirdeki F4'ün değeri) | Kaçtı |
| B05: G06 `not` "Sigorta 10 A" | Kaçtı |
| B17: G06 `kesit_not` "10 A hat sigortası" | Kaçtı |
| B18: G22 `not` "hat sigortası 3 A" | Kaçtı |
| B08: G18 adı "F3 5 A" (yanlış F numarası, aynı değer) | Kaçtı |
| B09: G18 sonlandırması "F3 yuvasına" (sayı yok) | Kaçtı |
| B07, B10–B14 (komşu hattın değeri, yanlış AWG, adı geçen koruyucunun yanlış değeri) | Hepsi yakalandı |

Kaçan dört sınıf, nasıl oluşabilecekleri ve sonuçları:

**(a) Zincirde yukarıdaki koruyucunun değeri** (B06, B15, B16):

- İzinli küme kablonun bütün besleme zincirini kapsıyor. Bu, K3R'nin önerdiği küme.
- Yukarıdaki değerler 20 ve 30 A. Bu değerde mini sigorta siparişte yok, montajcı bunu kitten takamaz.
- Tek gerçekçi yol B16. G19'un yuvasına, aynı XL4016 çevrenin giriş sigortası F4'ün "5 A"i yazılır; 5 A mini siparişte var (hat C için).
- Sonuç: X01'in 22 AWG 5 V damarı (2,46 A) 2 A yerine 5 A ile korunur. G19'un 16 AWG'si (8,2 A) etkilenmez.
- Kart üstünde "Koruma: hat-cevre 2 A" satırı yanı başında çelişkiyi gösterir. Sigortanın değeri de beş bağımsız yerde (sigorta listesi, blok şeması, karar satırı, MJ modeli, ad) sınanıyor.
- Bu yüzden durdurmuyor.

**(b) `not` ve `kesit_not` alanlarında kablonun kendi kesit sınırı izinli** (B05, B17, B18):

- 16 AWG'nin tablo değeri 10 A, eski şarj sigortasıyla aynı. 22 AWG'nin tablo değeri 3 A, F6'nın değeriyle aynı.
- Sonuç: değer kablonun düzeltmesiz tablo sınırına eşit kalır, aşırı yük yok. G06'da 10 A mini zaten siparişte değil.

**(c) Yanlış F numarası:**

- Aynı değerle (B08) ya da sayısız (B09) yazılırsa sınanmıyor.
- Sonuç: G18'in yapısal ucu "F4 çıkışı" doğru. Metne uyulursa G17 ile aynı 5 A yuvaya iki yük biner; sigorta erken atar, güvenli yöne düşer.

**Öneri (P10.7b'den önce, rehber bu metinleri okumadan):**

- `ad` ve damar `ara` alanlarında izinli küme yalnız `koruma` + `ara_koruyucu` olsun. Zincirdeki öbür koruyucular ancak adıyla anılırsa geçsin.
- `not` ve `kesit_not` alanlarında kesit sınırı ancak "AWG" ya da "sınır" sözcüğünün yanında geçsin.
- Sayısız "F<n>" de uç düğümüyle karşılaştırılsın.

### 2-3. Blok şemasındaki bobin satırı tek sürücü gibi okunuyor

**Yer:** EL:339, "röle K1 bobini ∥ K2 bobini ── BC337-40 ── GND".

- E9 devresinde (EL:443-444) ve PH:95'te her bobinin kendi BC337-40'ı var (#1 GPIO4, #2 GPIO19). Şema satırı ortak bir sürücü gibi okunuyor.
- Öbür üç satır düzeltmesi devrenin anlamını değiştirmiyor, kararlarla aynı:
  - Şarj kolu ana sigorta sonrası, 7,5 A mini (O-17, düzeltme turu 1).
  - "röle K1 kontağı ∥ K2 ön şarj kolu" (E9).
  - "2 A mini (O-18 b)".
- Montaj tablodan beslendiği için montajcıya etkisi yok.

**Öneri:** Satıra "(her bobin kendi BC337-40'ıyla, E9)" eklensin. Ayrıştırıcı sınansın.

### 2-4. Kırmızı pabuç satırının notu bayat (MJ:206, kalem 162)

- Not hâlâ "22 AWG G22 − … tel ucu katlanır, teslimde denenir" diyor.
- Ek tur kararıyla G22'nin yıldız ucu 18 AWG ara parça + kırmızı pabuç oldu, "katlanır" yazılmayacaktı. Adet değişmiyor (4 uç → 1 paket).

**Öneri:** Not "G22 − 18 AWG ara parçayla (ek tur)" diye düzeltilsin.

### 2-5. Belgesiz uç türüne "kesin" yazılmış uçlar

- **Sigorta kutusu:** G18 a ve A01 a, 18 AWG.
- **Modül vidalı klemensi:** SV1–SV3 a ve G19 a (16 AWG); G18 b, A01 b, A02 a ve K02 b (18 AWG); G22 b, 22 AWG.
- Sigorta kutusunun ürün sayfası bu kontrolde açıldı: uç türü ve kesit yazmıyor. Pakette yalnız sigortalar var.
- 22 AWG için ek tur kendi ölçütünü (alt sınırı belgesiz uca 0,5 mm² altı girmez) yalnız 5,08 klemense uyguladı (KD:132). G22 b, aynı belgesizlikte bir PC817 modülü klemensine "kesin" gidiyor. A06 b de aynı uçta, ama A06 teyitte.
- Bu, önceki turlardan kalma bir durum. 18 ve 16 AWG bu tür vidalı uçlara pratikte girer.

**Öneri:** G22 (ve sigorta kutusu uçları) için `klemens:` teyit maddesi eklensin, ya da `modul-vidali` de `ALT_SINIRI_BELGESIZ`'e alınsın.

### 2-6. P10.7b listesi hâlâ eksik (GN:934-935, §18.6)

- `tasarim/freecad/rehber/rehber_metin.py`'de eski "göğüs ekranı mini 2 A" (K11 a'dan önceki hâl) yalnız :634'te değil.
- Ayrıca şu satırlarda da geçiyor: :587, :611, :808, :842, :843 ve :1524.
- :1258'de şarj "10 A" bağlamı var.
- `git grep` ile okundu. Rehber bu paketin yasak alanı; yalnız listelendi.

### 2-7. Küçük maddeler

- **Malzeme iletken sözlüğü:** `malzeme_turleri.*.iletken` denetimde sabitle karşılaştırılmıyor (A05: silikon-18 "tek telli" yazılınca geçti). Denetim sabiti kullandığı için sonuç değişmiyor; tablo alanı sessizce kayabilir. Uç türü sözlüğü ise karşılaştırılıyor (A04, A12 yakalandı).
- **Kart üstü köprü:** Kafa giriş kartında F3 5 A taşıyan + ve − köprüsü "lehimle" yazılı. Delikli plaket pedleri 5 A için iz değil. Rehberde köprü ≥ 18 AWG tel olarak yazılsın.
- **K59 metin önerisi:** GN:918 "geçmezse orkestratöre döner" diyor. Brief'e göre bu bakış geçmezse paket proje sahibine gider. Bu bakış geçtiği için K59 "kapandı" diye girilebilir.

## 3. Ölçümler

### 3.1 D-A

**5,08 mm klemensin kesit aralığı:**

- MJ kalem 80'in satıcı sayfası bu kontrolde açıldı. Yalnız ad, ürün kodu 2511201001 ve stok 672 var; kesit, iletken türü ve akım yok. Ajanın iddiası doğru.
- Aynı sınıfın üretici veri sayfaları:
  - Würth WR-TBL 102 (5,00 mm vidalı): tek telli ve çok telli iletken 22–14 AWG, metrik 0,75–1,5 mm².
  - Bir 5,08 mm vidasız Würth tipi (353 serisi): 26–12 AWG.
  - KF301 dağıtıcı listeleri: 14–22 ve 16–24 AWG.
- Hepsinde 18 AWG (0,82 mm²) ve 16 AWG (1,31 mm²) aralığın içinde. Würth'ün metrik alt sınırı 0,75 mm², bu yüzden 22 AWG'yi (0,33) klemense sokmamak doğru.
- 18 AWG ince telli ucun bu klemense "kesin" yazılması kabul edilebilir: tipik aralığın ortasında, teslimde okunma maddesi var. Durdurmaz.

**Her uç için tür ↔ kesit (kendi betiğimle, 350 uç):**

| Uç türü | Uç sayısı | Kesit | Not |
|---|---|---|---|
| `wago-2273` | 0 | – | |
| `klemens-508` | 21 | 16 ve 18 AWG, ince telli | 22 AWG yok |
| `bara-pabuc` | 19 | | G22 −: uç kuyruğu 18 AWG 0,82 mm² ≥ 0,5 |
| `pabuc` | 5 | | |
| `bts-guc` | 12 | | |
| `modul-vidali` | 30 | | Belgesiz, §2-5 |
| `sigorta-kutusu` | 7 | | Belgesiz, §2-5 |
| `lehim` | 38 | | |
| `konnektor` | 218 | | |

- 12 AWG hiçbir belgesiz uca teyitsiz girmiyor.
- Pabuçların renk aralığı denetimde tek alt sınırla (0,5 mm²) sınanıyor. Renk AWG sınıfından sayılıyor. 16 AWG mavi ve 18 AWG kırmızı pabuç endüstri eşleşmesi.
- WAGO 221-413'ün aralığı (Ahmet'e seçenek) dağıtıcı veri sayfalarından okundu: ince telli 0,14–4 mm² (24–12 AWG). Yani 22 ve 18 AWG'yi alır.

**İki düğümün kuruluşu (fiziksel):**

| Kart | Klemens | Uç | Yer | Durum |
|---|---|---|---|---|
| Kafa girişi | 3 × 2 pin | 6 (G17, K01, K02'nin + / − çiftleri) | 6 | Tamam |
| Acil stop düğümü | 2 × 2 pin | 3 (A02 iki uç, A04 a) | 4 | Tamam; A06 + kuyruğa lehim, akım F5 2 A |

- `klemens_yerleri` toplamı 3 + 2 + 2 + 1 + 1 + 1 + 1 + 1 = 12. 12 × 1,3 = 15,6 → 16 = MJ. Yer başına uç sayısı her kartta ≤ 2 × adet.
- Pertinaks: 4 + 1 + 1 + 1 = 7 = MJ.

**G22 ve A06:**

- G22'nin dönüşü 22 AWG → 5 cm 18 AWG ara parça (lehim + makaron) → kırmızı M5 pabuç. Pabucun alt sınırını sağlıyor, "katlanır" yazılmamış.
- A06'nın iki ucu lehim, kayıt "kablajda teyit" (`klemens:` maddesi). G07 b de lehim.

**`maliyet.json`:**

- Fark (B3'ün temiz kopyasıyla karşılaştırma) yalnız üç kalemde:
  - kalem 62: `ver` "v1,v2" ve not;
  - kalem 79: 6 → 7;
  - kalem 80: 12 → 16.
- Kendi hesabım: −122,40 + 22,00 + 24,20 = −76,20. × 1,15 = −87,63.
  - Genel: 120.940,06 → **120.852,43**.
  - Koşullularla: 126.511,53 → **126.423,90**.
  - `maliyet_toplam.py` aynı sonucu veriyor; V3 kalem 125.
- Bağımlı dosyalar:
  - README:50 ve `proje-plani.md:11`: ≈ 120.900 / 126.400.
  - Demonun gömülü kopyası: klemens 16, pertinaks 7, WAGO "v1,v2".
  - F8a 14.11 tablosu 36 satır; S29 "V3 dışı (alma) 10 → 0", S8 5 → 7, S59 4 → 16.
  - F8a-siparis.json `guncelleme_14_11`: 120.852,43 / 126.423,9.
  - F9b ve F9d 0.

### 3.2 D-B

**Kod (KD:1934-2008):**

- Sınanan alanlar: ad, `kesit_not`, `not`, `sonlandirma`, damar `ara` ve damar `not`.
- Adıyla anılan koruyucunun değeri koruyucular tablosuyla karşılaştırılıyor. Adsız "N A" kablonun zincir değerleriyle (not / kesit_not'ta ayrıca kesit sınırlarıyla) karşılaştırılıyor.
- "N AWG" kesit ve uç kuyruğuyla karşılaştırılıyor.
- `tarihce` sınanmıyor.

**Üçüncü bakışın örnekleri:**

| Bozma | Ne | Sonuç | Yakalayan ileti |
|---|---|---|---|
| B01 = T44 | G22 adı "7,5 A" | Yakalandı | "kendi koruyucuları [2, 20, 30]" |
| B02 = T45 | G22 + `ara` "7,5 A" | Yakalandı | |
| B03 | G19 `not` "XL4016 çevre 8 A" | Yakalandı | "koruyucular.XL4016-cevre 10 A" |
| B04 | K03 `not` "20 AWG" | Yakalandı | T29'un işlemli eşdeğeri |
| B05 | G06 `not` "10 A" | Kaçtı | §2-2 (b) |

- Ajanın T30'u (`ara` "10 A mini") yakalanıyor: `ara` alanında kesit sınırı izinli değil.

**Yeni bozmalarım:** 13 bozma (B06–B18); 7'si yakalandı, 6'sı kaçtı (§2-2).

**Temiz tablo:** yanlış alarm yok, çıkış 0.

### 3.3 D-C

**Kod (KD:563-680):**

- `blok_agaci` EL "Blok şema (metin)" kod bloğunu `├─` / `└─` kollarına ve `──` öğelerine ayırıyor.
- `blok_karsilastir` her elemanı `DIYAGRAM` kalıbıyla tam bir öğeye eşliyor. Elemanın tablodaki girişini, şemadaki en yakın eşlenmiş atasının çıkışıyla karşılaştırıyor.
- Şu durumlarda hata veriyor: şema yoksa, ayrıştırma hatası varsa, kalıba uyan öğe 0 ya da birden çok ise, şemadaki bir sigorta öğesi eşlenmemişse.
- Karşılaştırma tablonun kendisiyle değil, belgeden ayrıştırılan yapıyla.
- İletilerde istenen yönlendirme metni (`YON`) var.

**Bozmalarım (tablo tutarlı biçimde, zincir / dal / bayrak denetimin kendi işlevleriyle yeniden yazıldı):**

| Bozma | Ne | Sonuç | İlk yakalayan |
|---|---|---|---|
| C01 (T40b) | XL4016 A röle öncesine | Yakalandı | `acil_stop` (blok şeması) |
| C02 (T42c) | BTS sol röle öncesine, B+ düğümü dahil | Yakalandı | blok şeması |
| C03 | XL4016 çevre F4 yerine anahtarlı baraya | Yakalandı | blok şeması + `ag` + `kesit` |
| C04 | Çevre hat sigortası girişi f4 | Yakalandı | blok şeması + `ag` |
| C05 | PC817 #2 hattı röle öncesine | Yakalandı | blok şeması |
| C06b | K2 ön şarj kolu ana anahtar çıkışına | Yakalandı | `ag` (paralel besleyen) |
| C07 | D24V50F5 F4'ten | Yakalandı | blok şeması |
| C08 | Göğüs regülatörü anahtarlı baraya | Yakalandı | blok şeması + `ag` |
| C09 | Şarj sigortası ana anahtar sonrasına | Yakalandı | blok şeması |
| C10 | XL4016 B hat-A'dan | Yakalandı | blok şeması |
| C15 | Hat-G22 tablodan silindi | Yakalandı | `koruyucu` + `ag` + `kesit` |
| C16 | K1 ve K2 kontağı F1'i atlıyor | Yakalandı | blok şeması + `kesit` |

**Şema tarafı:**

| Bozma | Ne | Sonuç |
|---|---|---|
| C11 | Bir kolun `├─` işareti silindi | Yakalandı ("kalıba uyan 0 öğe") |
| C12 | "2 A mini (O-18 b)" silindi | Yakalandı |
| C13 | Kod bloğu kaldırıldı | Yakalandı ("blok şeması bulunamadı") |
| C14 | Yalnız belgede XL4016 A kolu F4 altına taşındı | Yakalandı |

Sonuç: 16 bozmanın hepsi yakalandı.

**Şemadaki dört satır düzeltmesi:** `git diff 9a0c6fe` ve K3R'nin temiz kopyasıyla karşılaştırıldı. Satır sayısı aynı. Anlam §2-3'te.

### 3.4 Ek tur tabloyu bozmadı mı

**Karşılaştırma tabanı:** K3R'nin geçici klasöründeki temiz `kablolar.json` (14.11, 07:01). Yalnız okundu; kopya bu kontrolün klasörüne alındı. Alan alan karşılaştırıldı.

**74 kablonun hepsinde aynı kalanlar:** damar uçları (a / b), GPIO, pin adı, PCA kanalı, dal, koruma, kesit AWG, acil stop bayrağı, besleme zinciri.

**Kablolarda değişenler:**

- `uc_turu`: G07, G17, A02, A04, A06, K01 ve K02.
- `sonlandirma` metinleri.
- Notların tarihçesi `tarihce` alanına taşındı: G06, G20, K03, hat-sarj.
- A06 kesin → teyit.
- G22 `uc_kuyrugu`.
- G12 ve G13 notu.
- S01–S10 `mm2` 0,34 → 0,33.
- N01 ve N02 kesit notu.

**Üst alanlarda değişenler:**

- `klemens_turleri`: iletken, alt sınır, yerleşim.
- `malzeme_turleri.*.iletken`.
- `anahtarlar.*.geri_tepme_diyodu`: katot / anot düğümü.
- `koruyucular.hat-sarj.not` ve `tarihce`.
- Yeni alanlar: `klemens_yerleri`, `pertinaks_parcalari`, `kondansatorler`.

**Hiç değişmeyen üst alanlar:** `dugumler`, `aglar`, `ic_baglar`, `ortak_noktalar`. Koruyucuların `akim_a`, `giris` ve `cikis` alanları da değişmedi.

**Diğer kontroller:**

- **25 pin:** PH §9 JSON'undaki 24 GPIO kendi betiğimle karşılaştırıldı. 21 harici GPIO'nun pin adı birebir aynı; 1 / 3 ve 2 kart üstü; 12 boş. PH, K3R'nin kopyasıyla bayt bayt aynı.
- **PCA kanalları:** `pca_kanal` sınaması `main`'deki `kanallar.yaml` ile geçiyor; tablo alanları değişmedi.

### 3.5 Öbür bulgular (K3R §2)

**1. Yıldız köprüleri (kendi toplamım):**

- Yerleşim:
  - saplama 1: G12, G14, G15;
  - saplama 2: G13, G16;
  - saplama 3: G05, G06 (besleme saplaması);
  - saplama 4: G17, G18;
  - saplama 5: G20, G22.
- En kötü köprü akımları:

| Köprü | Hesap | Akım |
|---|---|---|
| 1–2 | Saplama 1'deki dönüşler, hepsi F1'in arkasında | ≤ 20 A |
| 2–3 | Saplama 1 ve 2 (F1 dönüşlerinin hepsi) | ≤ 20 A |
| 3–4 | F3 5 + F4 5 + F6 3 + hat-G22 2 | 15 A |
| 4–5 | 3 + 2 | 5 A |

- 12 AWG'nin etekteki sınırı 25 × 0,82 = 20,5 A; dördü de altında. Ajanın değerleriyle aynı.
- Yerleşim KJ'de saplama numarasıyla kayıtlı.
- Bozmalar: K01 (G17 ↔ G12 yer değişimi: 25 A), K02 (besleme saplaması 1: 30 A) ve K03 (G22 eksik) yakalandı.

**2. 1N4007 yönü:** Yapısal alanda. K04 (K2'de katot ↔ anot ters) yakalandı. K3R'nin T22'si de yakalandı.

**3. AWG ↔ mm²:** K05 (G18 18 AWG / 1,31 mm²) ve T24 yakalandı.

**4. Sigorta listesi hücresinde iki sayı:** P06 yakalandı.

**5. Donanım adetleri:**

- Yakalananlar: BC337-40 (T34), 2200 µF (T35, K06 kart dağılımı, K07 MJ 5 → 7), 5,08 klemens (T39, A07, A08), pertinaks (A09), WAGO (A10, kullanılmadığı hâlde V3'e dönmesi; A01, tabloda WAGO ucu ama V3 satırı yok).
- T36 (WAGO 10 → 1) geçiyor. Satır V3 dışı olduğu için anlamlı değil.

**6. Ani akım:** Hesap §2-1'de. Sayılar doğru, Efe notu yanlış kurulmuş.

**7. P10.7b listesi:** §2-6.

### 3.6 Doğrulamalar (gerçek depoda; yazmayan koşu, `-B`, `GIT_OPTIONAL_LOCKS=0`)

| Komut | Sonuç |
|---|---|
| `kablolar_denetim.py` | çıkış 0, 19 sınama GEÇER (kesin 31, teyit 42, karara bağlı 1) |
| `kablolar_denetim.py --bozma-denemesi` (kopyada) | 121 bozma, çıkış 0 |
| `--tablo` yanlış yol | çıkış 2 |
| `kablolar_uret.py --kontrol` | güncel, çıkış 0 |
| `maliyet_toplam.py` | ara 105.089,07; genel 120.852,43; koşullularla 126.423,90; V3 kalem 125 |
| `F9b-dogrula.py --tarayicisiz` | GEÇER, 0 hata |
| `F9d-tarama.py` | çıkış 0, README uyuşmazlığı 0 |
| `testler_html.py --kontrol` | KONTROL GEÇTİ |
| K3R'nin `boz3.py`'si (bu kontrolün klasörüne çevrilmiş kopya) | 56'nın 54'ü yakalandı; kaçan T29 ve T36 |

T29 ve T36'nın kaçışı ajanın açıklamasıyla aynı:

- T29'un değiştirdiği metin artık yok, bozma işlem yapmıyor. İşlemli eşdeğeri B04 yakalandı.
- T36'daki satır V3 dışı.

Kendi bozmalarım toplam 48:

- D-B: 18.
- D-C: 16 (C06'nın ilk biçimi uygulanamadı: zincir kurulamıyor; yerine C06b).
- D-A: 12.
- Küçük maddeler: 7 (K01–K07).
- Kaçan: B05, B06, B08, B09, B15–B18 (§2-2), A05 ve A06.
  - A06: arayüz kartındaki bir 16 AWG uç "lehim" yazıldı. Fiziksel sonucu yok.

### 3.7 Gizlilik ve sınırlar

- **Taranan:** `git diff 9a0c6fe` ile eklenen satırlar (`tasarim/freecad/` hariç) ve izlenmeyen 8 dosyanın tamamı, 18.164 satır. Ek turun satırları bunun içinde.
- **Aranan kalıplar:** yerel kullanıcı yolu, sürücü harfli yol, bulut / geçici klasör, kullanıcı adı, takma ad, depo dışı dökümün adı ve yolu, e-posta, parola / anahtar / jeton, ağ adı, makine adı.
- **Sonuç:** Bulgu yok. Eşleşmelerin hepsi veri sayfası metni ("Wi-Fi TX") ya da kontrol raporlarının kendi "aranan kalıplar" satırları. Ek tur soyad eklemedi; test kâğıtlarına dokunmadı.
- **Sınırlar:**
  - `rehber/`, `planlama/rehber/`, `kod/` altında değişiklik yok.
  - `tasarim/freecad/` altında yalnız önceden var olan 13 PNG ve `montaj/yerlesim-kontrol.json`.
  - Kontrol raporlarının değişiklik saatleri kendi bakışlarının saatleri (kontrol 04:57, -2 06:16, -3 07:19). Ek tur 07:50'de bitti.

### 3.8 C adımı için liste

**Commit'e girecekler:** GN §18-4 listesi `git status` ile birebir tutuyor. 23 değişen + 8 izlenmeyen dosya var (üç kontrol raporu dahil). Bu rapor (`planlama/d158/P107a-kontrol-4.md`) eklenir. Dışarıda kalanlar: 13 PNG ve `yerlesim-kontrol.json`.

**`dongu-158.md`** (GN §18-1, -2; bugünkü satır hâlâ "A adımı 14.11 ≈ 03:50"):

- Öneri metnine "dördüncü bakış `P107a-kontrol-4.md` GEÇER (açık işler: Efe notu, `sayi_metin` alt sınıfı, rehber satırları)" eklenmeli.
- "121 / 121" yanında: dördüncü bakışın 48 bozmasından kaçan sınıflar §2-2'de.

**`karar-kuyrugu.md`:**

- 1235, 1260 ve 1264 kapanışları ve K59 açılışı GN §18-3'teki gibi.
- K59'un kararı: "dördüncü bakış GEÇER, K59 kapandı" (§2-7).
- §2-1 ve §2-2 P10.7b'den önce açık iş olarak girsin. §2-1 Efe listesi gönderilmeden önce.

## 4. Bakılmadı

- 5,08 mm klemensin üretici kodu ve kendi veri sayfası (satıcı vermiyor). Okunan sayfalar aynı sınıfın başka ürünleri.
- Sigorta kutusunun uç türü (satıcı sayfası yazmıyor). PC817, XL4016 ve BTS modül klemenslerinin aralığı.
- WAGO'nun kendi ürün sayfası (221-413 dağıtıcı veri sayfalarından).
- XL4016'nın 8 V giriş alt sınırı (veri sayfası açılmadı).
- PC817 modülünün giriş eşiği: satıcı sayfasındaki "3,6–24 V" EL:235'ten okundu, modül ölçülmedi.
- F9b'nin tarayıcı kısmı ve F9c.
- Fiyat sayfaları. Bu turda değişen üç kalemin fiyatları 09.11'den, ajan da değiştirmedi.
- Hiçbir akım, süre ya da sıcaklık ölçülmedi (malzeme yok). Ani akım ve köprü değerleri hesaptır.
