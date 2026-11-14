**Hüküm: DÜZELTME GEREKLİ.** Üç durduran bulgu var. Başka düzeltme turu açılmayacağı için üçü de proje sahibine gider:

- **D-A (sipariş, 16.11'den önce):** Tablo, ince telli silikon kabloyu yalnız tek telli (solid) iletken alan WAGO 2273-203 klemense sokuyor: kafa 12 V girişi ve acil stop düğümü. A06'nın 22 AWG teli ayrıca klemensin en ince kesitinin de altında. Bu klemens `maliyet.json`'da 10 adet sipariş kalemi olarak duruyor.
- **D-B (denetim):** `sayi_metin` sınaması, söz verdiği sınıfı yakalamıyor. G22'nin (22 AWG, 2 A) adına ya da hat sigortası metnine "7,5 A" yazılınca hata çıkmıyor. `not` alanlarındaki sayılar hiç sınanmıyor.
- **D-C (denetim):** Röle K1'in arkasındaki elemanlar (BTS7960 ×2, XL4016 A / B / C hat sigortaları, PC817 #2) blok şemayla sınanmıyor. XL4016 A ya da BTS sol tablo içinde tutarlı biçimde röle öncesine alınınca hata çıkmıyor. Bu durumda servo kolu ya da motor acil stopta enerjili kalır. Üstelik denetimin hata iletileri, tek alanlık bir yanlıştan başlayan düzenleyiciyi tam bu tutarlı yanlış tabloya götürüyor.

Bugünkü tablo değerleri doğru. Uçlar, 25 pin, PCA kanalları, sigortalar, kesitler, acil stop bayrakları ve besleme zincirleri ikinci kontrolün doğruladığı hâlle alan alan aynı. D1′'in istediği belge karşılaştırmaları gerçekten çalışıyor: ikinci kontrolün 55 bozmasının hepsi yakalanıyor. D3'ün metin düzeltmeleri de yapılmış.

# P10.7a üçüncü (son) bağımsız bakış: kablo tablosu + 16.11 sipariş listesi (düzeltme turu 2 sonrası)

Kontrol 14.11.2026'da yapıldı. Rapor 07:16'dan sonra yazıldı; saat saatten okundu.

- **Depo durumu:** Dal `lale-duzeltme`, HEAD `9a0c6fe`, değişiklikler çalışma ağacında. Kod tarafı `origin/main` (`kanallar.yaml`, `git show` ile okundu).
- **Bozma denemeleri:** Depo dışında, geçici bir kopyada koştu. Her denemede kopya baştan kuruldu, bozma uygulandı, görünüm `kablolar_uret.py` ile yeniden üretildi ve denetim çıkış koduyla koştu. Böylece `gorunum` sınaması bir bozmayı tek başına "yakalamış" sayılmadı.
- **Depoda yazılan tek dosya** bu rapor. FreeCAD ve `rehber_uret.py` koşmadı.

Kısaltmalar:

- **KJ** `planlama/adim3/kablolar.json`
- **KD** `planlama/adim3/kablolar_denetim.py`
- **EL** `planlama/adim3/elektrik.md`
- **KOK** `planlama/adim3/kablolama-on-kararlar.md`
- **MJ** `planlama/maliyet.json`
- **GN** `planlama/d158/kablo-tablosu-gunluk.md`
- **K2R** ikinci kontrol, `planlama/d158/P107a-kontrol-2.md`

## 1. Göndermeyi durduran bulgular

### D-A. WAGO 2273-203 ince telli silikon kabloya uygun değil (yanlış uç türü + yanlış sipariş kalemi)

**Yer:**

- KJ'de `uc_turu` `wago-2273` olan damarlar:
  - G17 + / −, K01 + / −, K02 + / −: "Kafa giriş klemensi", 18 AWG silikon, F3 5 A.
  - A02 (iki uç) ve A04: acil stop düğümü, 18 AWG silikon.
  - A06: acil stop düğümü, **22 AWG**, 0,33 mm².
- Uç türü sözlüğü: KD:118 (`"wago-2273": 2.5`, yalnız üst sınır).
- Sipariş: MJ:99, kalem 62, "2273-203 3 Pin Buat Klemensi (Wago)" × 10. Karar satırı: KOK:447 (O-6).

**Nasıl ölçüldü:**

- WAGO'nun ve dağıtıcıların 2273 serisi veri sayfaları web'de açıldı. Seri **yalnız tek telli (solid) iletken** için, 0,5–2,5 mm². Telli ve ince telli iletken alan seriler başka (aynı belgede 773; kollu 221).
- Tablodaki bu kabloların malzemesi `silikon-18` ve `sinyal-22`. İkisi de ince telli.
- Geçmiş: Başlangıçta 221-413 seçilmişti (`planlama/d158/F8a-siparis.md:140`, `raporlar/kaynaklar/06-onayli-satici-A.md:22`). P8.1'de onaylı satıcı yüzünden 2273-203'e geçildi. `F8a-siparis.json:1178`'de "muadil" deniyor; yalnız en büyük kesit karşılaştırılmış.

**Neden durdurur:**

- Bu, "tabloda yanlış uç" ve "yanlış sipariş kalemi" sınıfı.
- İnce telli iletken itmeli solid klemenste güvenilir tutmaz. Kafa 12 V hattı (F3 5 A) bu düğümden geçiyor; gevşek temas ısınır ve kesik kesik keser.
- Acil stop düğümünde gevşeme güvenli yöne düşer (röleler bırakır). Ama robot "kendiliğinden" durur ve arızası zor bulunur.
- A06'nın 22 AWG teli 0,5 mm²'lik alt sınırın da altında.
- Sipariş 16.11'de; kalem bugün yanlış.

**Önerilen düzeltme (proje sahibinin kararı, çünkü onaylı satıcı dışına çıkılabilir):**

- MJ kalem 62, ince telli iletken alan kollu bir klemensle değişsin: başta seçilen 221-413 ya da eşdeğeri. Kesit aralığı (22 AWG dahil) sipariş sayfasından doğrulansın.
- Ya da bu uçlarda yüksük + vidalı klemens kullanılsın.
- KJ `uc_turu` ve KD `UC_TURU_SINIRI`'ye uç türünün **iletken sınıfı ve alt kesiti** girsin. Ardından KOK:447 ve `F8a` notu güncellensin.
- Denetim bu sınıfı bugün göremiyor; sözlükte yalnız üst sınır var.

### D-B. `sayi_metin` dişsiz: yanlış sigorta değeri ad / metin içinde sessizce geçiyor; `not` alanı sınanmıyor

**Yer:** KD:1633-1675.

- Ad için izin verilen sayılar, kablonun kendi zincirinin yanında, kablonun ağlarına **komşu bütün koruyucuları** da kapsıyor (KD:1644-1647).
- Sınanan alanlar yalnız `ad` ve `kesit_not` (KD:1657).
- "F<n> N A" taraması da `not` alanına ve damar `ara` metnine bakmıyor (KD:1666-1667).
- Ajanın iddiası "kablo adı, kesit notu, **not** ve koruyucu adı"; GN:571 de böyle diyor. D2 brief'i ad ve notları açıkça istiyordu.

**Ölçüm (kendi bozmalarım, geçici kopya):**

| Bozma | Gerçek etkisi | Sonuç |
|---|---|---|
| T44 G22 adı "Anahtarlı bara → **7,5 A** hat sigortası → PC817 #2 girişi" | Rehberi okuyan, 22 AWG tele (45 °C'de 2,46 A) 7,5 A takar | **Kaçtı**, çıkış 0 (bara ağına komşu hat-A / hat-B 7,5 A "izinli") |
| T45 G22 + damarının `ara` metni "7,5 A mini hat sigortası yuvası" | aynı | **Kaçtı** |
| T26 G16 adı 5 → 7,5 A; T27 G14 adı 7,5 → 5 A | Hat C / A'ya yanlış sigorta | **Kaçtı** (ikisi de) |
| T28 G19 `not` "XL4016 çevre 8 A sınırı" (K2R'nin D3 metni) | Eski koruma metni | **Kaçtı** |
| T29 K03 `not` "20 AWG" | Eski kesit metni | **Kaçtı** |
| T30 G06 + `ara` "10 A mini" | Eski şarj sigortası | **Kaçtı** |
| T31 G18 `not` "F4 10 A" | Yanlış sigorta | **Kaçtı** |
| T32 G20 `sonlandirma` "F6 5 A" | | Yakalandı (`sayi_metin`) |

**Neden durdurur:** "Gerçek güvenlik etkisi olan akla yatkın tek alanlık düzenleme hatasını sessizce geçiren denetim" sınıfı. T44 / T45 komşu kablonun adından kopyalamayla olur. Montaj rehberi adı ve metni bu tablodan alacak. Bu sınama D3'ün "kalıcı çaresi" olarak getirildi.

**Bugünkü içerik temiz:** 74 kaydın ad, kesit notu, not, sonlandırma, teyit ve damar metinlerindeki bütün "N A" / "N AWG" geçişlerini (97 geçiş) kendi betiğimle alanlarla karşılaştırdım. Çelişen yok; geçmiş değerler "10 → 7,5 A" biçiminde işaretli.

**Önerilen düzeltme (KD, küçük):**

- `ad`, damar `ara` ve `not` alanlarında izinli küme yalnız kablonun kendi `besleme_zinciri` + `koruma` + `ara_koruyucu` kümesi olsun. Komşu koruyucu ancak adıyla anılıyorsa ("ana sigorta 30 A", "F4 5 A") geçsin.
- `not` ve damar `ara` / `not` alanları sınamaya katılsın. "N → M" tarihçe kalıbında yalnız M sınansın.
- T44, T28 ve T30 `--bozma-denemesi` listesine eklensin.

### D-C. Röle sonrası elemanlar blok şemayla sınanmıyor: XL4016 A ya da BTS röle öncesine alınınca geçiyor

**Yer:**

- KD:169-170: `DIYAGRAM_ADI` yalnız K1 kontağı, XL4016 çevre, D24V50F5, SY8205, göğüs regülatörü ve mantarı içeriyor.
- EL:325-331: blok şemada F1 → röle K1 kontağı → anahtarlı bara altında BTS7960 sol / sağ, 7,5 A → XL4016 A, 7,5 A → XL4016 B, 5 A → XL4016 C, PC817 #2.
- Bu elemanların "anahtarlı baradan, yani K1 / K2 kontağından sonra beslenir" şartı hiçbir sınamada belgeyle karşılaştırılmıyor. §12 karşılaştırması tutarlı biçimde değişen dal adını (`F1-kontak-oncesi`, Enerjili listesinde) doğru buluyor.

**Ölçüm:**

| Bozma | Gerçek etkisi | Sonuç |
|---|---|---|
| T40c (tek alan) G14 + ucu "Sigorta kutusu · F1 çıkışı" | | Yakalandı. İletiler: "arada hat-A (anahtarli-bara → …) ama uçlar f1-cikis → …", uç türü, `uc_a.parca`. Düzenleyiciyi hat-A girişini değiştirmeye yönlendiriyor |
| T40b T40c + `hat-A.giris` f1-cikis, `uc_a`, `uc_turu`; zincir / dal / acil stop bayrağı denetimin kendi işlevleriyle (iletinin "devreden …" dediği değer) yeniden yazıldı | XL4016 A ve sağ kolun dört servosu **acil stopta enerjili** | **Kaçtı**, çıkış 0 |
| T42c BTS7960 sol aynı biçimde röle öncesine (B+ düğümü dahil) | Sol motorlar acil stopta sürücüye bağlı, enerjili | **Kaçtı**, çıkış 0 |
| T41b PC817 #2 algı teli (G22) röle öncesine | Bara durumu hep "var" okunur; E9 ön şarj denetimi kör | **Kaçtı**, çıkış 0 |

**Neden durdurur:**

- K2R'nin N1b'siyle (dalın tutarlı biçimde başka sigortaya taşınması) aynı sınıf. D2 brief'i bunun yakalanmasını istemişti. Ajan bunu yalnız `DIYAGRAM_ADI`'deki altı eleman için kapattı.
- Belge (EL blok şeması) değişmeden yalnız tablo değişiyor. Yani bu, "tablo + belge birlikte tutarlı bozuldu, yakalanamaz" türü değil.
- Etkisi acil stopun servo kolunu ya da motoru kesmemesi.

**Önerilen düzeltme (KD, küçük):**

- `DIYAGRAM_ADI` K1 alt bloğuyla genişlesin: `BTS7960-sol` "BTS7960 sol", `BTS7960-sag` "BTS7960 sağ", `hat-A` / `hat-B` / `hat-C` "XL4016 A / B / C", `hat-G22` "PC817 #2".
- Blok şemada `röle K1 kontağı` satırının alt öğesi olan her elemanın zincirinde `K1-kontak` bulunsun (girişi `anahtarli-bara`).
- T40b, T42c ve T41b `--bozma-denemesi`'ne eklensin.

## 2. Kayıtlı açık iş olarak gidebilecek bulgular

Her biri tek satır; ölçüm yöntemi parantez içinde.

1. **Yıldız köprüleri: şart ters yönde, yarılama kuralı kendi kuralını garanti etmiyor** (KD:1061, KJ `kopruler.sart`).
   - Kendi hesabım. Yıldızda 5 saplama, zincir köprü. Yanlarda (1 + 2 ve 4 + 5) beşer, ortada iki iletken yeri var.
   - F1'den beslenen dönüşler (G12, G13, G14, G15, G16 ve G22) toplamda F1 20 A ile sınırlı. Öbürleri F3 5, F4 5, F6 3 A. Şarj dönüşü G06 ters yönde akar ve toplamaz.
   - Bugünkü şartla (G12 − ve G13 − ortanın iki yanında) bir yanda tek bir BTS'nin dönüşü 20 A'e kadar çıkabilir. F3 / F4 / F6 dönüşleri de o yandaysa sigortaların toplamı 33 A olur; ana sigorta bunu 30 A'de keser. Bu, 12 AWG'nin etekteki 20,5 A'inin üstünde.
   - Önerim: F1 dönüşlerinin hepsi (G12–G16) bir yanda, en çok 20 A. F3 / F4 / F6 / G22 öbür yanda, en çok 15 A. G05 ve G06 ortada (sayım: 5 + 4 + 2 yer). Böylece paketin kendi kuralı her köprüde sağlanır.
   - Köprü 50 mm ve en kötü durum bütün sigortaların aynı anda dolması; fiilî risk düşük. Rehberden (P10.7b) önce şart ve denetim (yan başına sigorta toplamı) buna göre değişsin.
2. **1N4007 yönü serbest metin:** K1 diyotunun `yon` alanı ters yazılınca ("katot bobin −") geçiyor (T22; KD:1354 yalnız boş olup olmadığına bakıyor). Ters takılan diyot BC337-40'ı yakar ya da F5'i attırır; güvenli yöne düşer. "katot … +" kalıbı sınansın.
3. **`kesit.awg` ile `kesit.mm2` arasında tutarlılık yok:** K01 `{awg 12, mm2 2.0}` yazılınca WAGO sınırından kaçıyor (T24). mm² değeri `kesit_kurali.tablo`'dan türetilsin.
4. **Sigorta listesi ayrıştırıcısı ilk sayıyı alıyor:** "5 A standart, sonra 10 A" sessizce 5 A okunuyor (P06). Öbür biçim bozmalarının hepsi hata verdi, sessiz geçen yok (P01–P05, §3.2).
5. **Donanım adetlerinde kapsam dışı kalemler:** BC337-40 3 → 1, 2200 µF 5 → 4, WAGO 10 → 1 ve 5,08 klemens 12 → 2 geçiyor (T34–T36, T39). D2'nin saydığı kalemler (yuva, sigortalar, saplama, pabuç, diyot) tam yakalanıyor. Bu dördü küçük ekleme.
6. **Ani akım "≈ 100 ms" dolu akü (14,6 V) içindir** (EL:448).
   - Kendi hesabım: bara dolumu ½ · 2 mF · 14,6² ≈ 0,21 J ✓; servo kondansatörleri 0,198 / 0,88 ≈ 0,23 J ✓; bekleme kaybı 0,4² · 5,6 · 0,3 ≈ 0,27 J ✓. Toplam ≈ 0,7 J, ortalama ≈ 2,3 W, ilk anda ≈ 38 W ✓.
   - Süre ise gerilime duyarlı. 12,8 V'ta (nominal) 5 W bekleme yükü dirençte büyük pay alır. XL4016 girişi 8–9 V'un üstünde kalacaksa kondansatörlere ≈ 1–1,9 W kalır. Dolma ≈ 120–200 ms, toplam ≈ 180–260 ms; 300 ms penceresine yaklaşır.
   - Dolmazsa K1 küçük bir kalan adımla kapanır. Tehlikeli değil. E9 tezgâh denemesinde boş akü gerilimiyle bakılsın, Efe'ye not olarak gitsin (hesap, ölçülmedi).
7. **P10.7b listesi eksik (GN:782):** `tasarim/freecad/rehber/rehber_metin.py`'de "şarj 10 A" ayrıca :626, :711 ve :1291'de geçiyor. :634'te "göğüs ekranı mini 2 A" de var. Listede yalnız :251 ve :634 "şarj" var. Rehber bu paketin yasak alanı; yalnız listelendi.
8. **G22'nin 22 AWG (0,33 mm²) dönüş teli kırmızı pabuçla (0,5–1,5 mm²) yıldız saplamasına gidiyor** (KJ G22 sonlandırma, `pabuc_sayimi` sınıfı "18–22"). Tel ikiye katlanarak ya da kısa bir 18 AWG ara parçayla sıkılsın; denemede bakılsın.
9. **Denetim, kendi bozma listesinde N7b'yi `alanlar` ile "yakalıyor":** Eski `klemensler` alanı tanımsız alan diye hata veriyor. Gerçek sınama ajanın N7b′ bozmasında (`uc_turu`) var ve çalışıyor (`klemens`). Bilgi.
10. **`koruyucular.hat-sarj.not`:** "10 → 7,5 A" tarihçesi "önceki değer 7,5 A'e indi" diye yazılmış; eski değer okunmuyor. Bilgi.

## 3. Ölçümler

### 3.1 D1′: bağımsız kaynak

Kodu okudum, ardından belge tarafını bozarak sınadım:

- **Koruyucu akımı ve biçimi:**
  - EL "Sigorta listesi" tablosundan ayrıştırılıyor (KD:448-486; tek tablo şartı, parantez atılıyor, Hat satırı "mini: …").
  - Blok şemadaki `├─ Fn N A ──` satırlarıyla (KD:500-513), K11 / KT3 / O-18 / O-19 / şarj karar satırlarıyla (KD:161-167) ve MJ modelindeki amperle (KD:516, :586) karşılaştırılıyor.
  - BMS EL:323'ten, XL4016 EL:222'den okunuyor; D24V50F5 / SY8205 / BTS belgesiz (`None` zorunlu).
  - Yalnız belge değişince (T05 F4 7,5 A, T06 Hat C 7,5 A, T07 blok F4 10 A, T08 BMS 40 A, T09 KOK F6 5 A, T10 MJ F4 "10 Amper") hepsi yakalandı.
  - Yalnız tablo tutarlı biçimde değişince (T01 F3 7,5 A + ad, T02 hat-çevre 3 A + ad, T03 F5 5 A + ad, T04 XL4016-A 15 A) hepsi belgeden yakalandı.
- **İstisnalar:**
  - Üye listesi ve en ince kesit betikte sabit (KD:128-143). Zincirden türetilen koruyan istisnanın kümesinde aranıyor; akım üst sınırla, kesit en ince kesitle karşılaştırılıyor. Üst sınırın sayısı kaynak satırında aranıyor (KD:871-949).
  - T11 (üst sınır 10 → 15), T12 (30 → 25), T13 (G17 kapsam dışı istisna) yakalandı.
  - Not: Üst sınır, kaynak satırında başka bir sayı olarak geçen değere değiştirilirse geçebilir. KOK:456'da "30 A" ve "25 A" var. Büyütme yönünde bu satırda başka sayı yok; denedim (T12), küçültme de yakalanıyor.
- **Dal ↔ sigorta ↔ acil stop:** §12 tam öğe eşleşmesi ve F blokları çalışıyor (N1b, N2c, N16 yakalandı). Eksik: röle K1 alt bloğu (D-C).
- **Köprüler ve kart içi bağlar:**
  - T15 (yıldız köprüsü 16 AWG), T16 (besleme saplaması 2), T17 (bara köprüsü 18 AWG) yakalandı.
  - T18 (düğümün ağı 5v-pi, tek alan) ve T19 (var olan kart içi bağ 5 V Pi ↔ çevre) yakalandı.
- **Yer tutucu, uç türü, kaynak, 1N4007, donanım:**
  - T20 (K2 diyot alanı silindi), T21 (A05'ten "1N4007"), T23 (12 AWG WAGO'ya), T25 (BTS ucu 5,08 klemens), T33 (2 A mini 2 → 1), T37 (1N4007 3 → 10), T38 (mavi pabuç 2 → 8) yakalandı.
  - Kaçanlar §2-2, -3, -5'te.

### 3.2 Bozma denemeleri (toplam)

- **Temiz tablo:**
  - Gerçek depoda ve kopyada çıkış 0, 19 sınama GEÇER, yanlış alarm yok.
  - `--bozma-denemesi` kopyada 97 / 97, çıkış 0.
  - Kaynak yokken çıkış 2: `--tablo` yanlış yol ve `elektrik.md` kaldırılarak denendi.
- **K2R'nin 55 bozması** (K2R'nin betiği salt okundu; kopyası kendi klasörümü gösterecek biçimde koştu): **55 / 55 yakalandı.** K2R'de kaçan 22'nin (B5c, N1b, N2c, N4b, N5b, N5c, N7b, N7c, N8a, N8c, N8d, N8e, N8f, N9b, N9c, N9d, N10a, N10b, N11c, N11d, N14, N16) hepsi yakalanıyor. N8a / N8c / N8e / N8f'nin ilk iletisi adın sayısından; tutarlı ad varyantı belgeden yakalanıyor (T01–T03).
- **Kendi bozmalarım: 52 deneme** (T01–T45, P01–P06, varyantlar).
  - Biçim (P01–P06): 5 hata verdi, 1 sessiz geçti (P06).
  - Yakalanmayanlar:
    - D-B: T26–T31, T44, T45.
    - D-C: T40b, T41b, T42c.
    - Açık iş: T22, T24, T34–T36, T39.
  - Ağırlığı tek alanlık dikkatsiz hatalar oluşturuyor. Sigorta akımı, dal, istisna, üst sınır, ince dönüş, köprü, 5 V birleşmesi, 1N4007 ve klemens kesiti sınıflarında tek alanlık hata **yakalanıyor**. Kaçan sınıflar ad / metin sayısı, röle alt bloğu ve kapsam dışı adetler.

### 3.3 Düzeltme turu tabloyu bozmadı mı

- **Karşılaştırma tabanı:** K2R'nin kopyasındaki `kablolar.json` (14.11 05:49). Bugünkü tabloyla alan alan karşılaştırıldı.
- **74 kablonun hepsinde aynı kalanlar:** damar uçları (`a` / `b`), damar sayısı, GPIO, pin adı, PCA kanalı, `koruma`, `dal`, `kesit`, `acil_stopta_enerjili`, `besleme_zinciri`.
- **Kablolarda değişenler** (GN §16.1 / §16.3 ile tutarlı):
  - Her damara `uc_turu` eklendi; `klemensler` alanı kalktı.
  - G06 adı / kesit notu (7,5 A), G19 ve K03 kesit notu.
  - G05 sonlandırması ortadaki saplama; G12 / G13 notu.
  - G08 kesin → teyit (klemens maddesi); G04 / G10'a teyit maddesi.
  - G05 / G16 / G17 / G21 kaynakları; C01 parça adı.
- **Üst alanlarda değişenler:**
  - `koruyucular`: yalnız `bicak`, `siparis`, XL4016 kaynağı ve hat-A / B / C adlarının parantezi. **`akim_a`, `giris` ve `cikis` hiçbirinde değişmedi.**
  - `anahtarlar`: diyot alanı.
  - `dallar.anahtarli-bara.p12` metni.
  - İstisnalara `koruyucular`; köprüye `besleme_saplamasi` 3.
  - `dugumler` ve `aglar` değişmedi.
- **25 pin:** PH §9 JSON'u ile tablodaki ESP32 uçları kendi betiğimle karşılaştırıldı.
  - 21 harici GPIO'nun işlevi, pin adı ve karşı ucu birebir aynı.
  - 1 / 3 kart üstü UART, 2 yalnız LED, 12 boş.
  - 3V3, VIN, GND ve micro USB uçları yerinde.
- **PCA9685:** K0–K9 `main` `kanallar.yaml` ile, K10–K12 PH ile aynı.
- **20 rastgele kablo (tohum 4233):** A04, A05, C01, G03, G07, G13, G15, G19, H02, I01, M02, M03, M04, N02, Q02, S05, S07, S09, S10, U01. Zincirleri EL:323-341 ve E9 devresinden (EL:441-444) kurdum, tablodakiyle aynı.
  - Ana sigorta → ana anahtar.
  - Anahtar sonrası 100 kΩ (G07).
  - F1 → K1 ∥ K2 → bara → hat-B / hat-C → XL4016.
  - F4 → XL4016 çevre → 2 A mini → ESP32 3V3.
  - F5 → mantar → K2 bobini.
  - F3 → D24V50F5.
- **`pin-haritasi.md`:** `git diff 9a0c6fe` yalnız satır 43 (MJ satırının "BC337-40; önce IRLZ44N" metni). Pin tablosu ve kurallar aynı.

### 3.4 Belgeler ve toplamlar

- **EL "Sigorta listesi"** (EL:360-372): Tek tablo; Değer hücreleri "N A standart / mini", Hat satırı tek hücrede beş mini. Tablo ile denetimin okuduğu değerler aynı:
  - Ana 30 A, F1 20 A, F3 5 A, F4 5 A, F5 2 A, F6 3 A: standart.
  - A / B 7,5 A, C 5 A, G22 2 A, çevre 2 A, şarj 7,5 A: mini.
- **EL'de kalan eski görünen satırlar** (:93, :106, :138, :220, :367 "önce 10 A") tarihçe olarak işaretli ya da modül anma değeri (XL4016 "8 A modül"). Yanlış yönlendiren yok.
- **`maliyet_toplam.py`:** ara 105.165,27; genel **120.940,06**; koşullularla **126.511,53**; V3 kalem 126.
  - `sonuc-rapor.html` `data-j`: 120.940,06 / 126.511,53 / 96.044,31 / 104.344,95.
  - README:50 ve `proje-plani.md:11`: ≈ 120.900 / 126.500 (F9d README uyuşmazlığı 0).
  - Demo gömülü kopyasında 1N4007 adedi 3. `F8a-siparis.md` 14.11 tablosu 35 satır; S24 1N4007 2 → 3.
- **Doğrulamalar** (gerçek depoda; yazmayan koşu, `-B`, `GIT_OPTIONAL_LOCKS=0`; `git status` önce ve sonra 44 satır):
  - `kablolar_uret.py --kontrol` güncel (0).
  - F9b `--tarayicisiz` GEÇER (0).
  - F9d 0.
  - `testler_html.py --kontrol` geçti.
  - F9c 28 hata. K2R'nin kaydettiği küme ile satır satır aynı, yalnız sıra farkı.
  - F9b tarayıcı kısmı bakılmadı.

### 3.5 D3 taraması

- **Depo geneli** (`git grep`; `kod/`, `rehber/`, `planlama/rehber/`, `tubitak-2209b/`, tarihli günlük / kontrol raporları hariç). Aranan: şarj "10 A", "20 AWG", "8 A sınır", IRLZ44, AO3400, WAGO 221, "6 takım", "5 pabuç", hat yuvası × 2–5.
- **Kalanların hepsi** tarihçe olarak işaretli ya da tarihli:
  - `Lale-Proje-Ozeti.txt:98` ("IRLZ44N çıktı").
  - `B-malzeme-plan.md:44-45` (tarihçe notu), `:64`.
  - KOK :305, :309, :329, :418.
  - PH :38, :342.
  - `F8a-siparis` (S87 "ALMA").
  - `maliyet_duzelt.py` (tarihî betik).
  - Akü raporu ve `06-onayli-satici-A.md:35` (tarihli).
- **Yalnız listelenenler:**
  - `tasarim/freecad/rehber/` (§2-7).
  - `tasarim/freecad/taban/taban_rapor.py:360` ve `taban/rapor.html` (IRLZ44N).
  - `tasarim/freecad/taslak-170/` (eski taslak).
- **74 kaydın metinlerindeki sayılar:** §1 D-B'de; çelişki yok.

### 3.6 Küçük maddeler

- **1N4007:** MJ kalem 76, 3 adet. Yapısal alan `anahtarlar.K1-bobin` / `K2-bobin.geri_tepme_diyodu`:
  - K1: A03; soket kuyruğu 86 / 85; katot 86'ya (bobin +).
  - K2: A05; bobin klemensinde; katot bobin +.
  - Yön ters paralel söndürme diyodu için doğru.
- **Akü dönüşü ortada:** G05 sonlandırması "yıldız barasının ortadaki (3.) saplamasına"; `kopruler.Yıldız barası · GND.besleme_saplamasi` 3. Köprü hesabı §2-1'de.
- **Ani akım:** §2-6.
- **Efe'ye bildirilecek (GN §16.6):**
  - (1) BTS IS → EN.
  - (2) Çevre 5 V'un düşmesi arıza sayılır.
  - (3) USB'den geri besleme sorusu.
  - Brief'in saydığı üç madde tam. Önerilen ek: §2-6 (boş akü gerilimiyle 300 ms penceresi; E9 adımı 3'teki PC817 #2 teyidi kondansatörlerin dolduğunu göstermez).
- **Ahmet'e (GN §16.7):**
  - (1) Mini sigortanın yuvaya oturması.
  - (2) XT60E-M kapağı.
  - (3) T8 E + E2 kısa devre denemeleri.
  - (4) K04 kesit yazısı.
  - (5) Kafa ekranının akımı.
  - (6) 1N5819 1 A.
  - (7) Akü dönüşü ortada.
  - (8) K1 soket kuyruğu.
  - Brief'in saydığı maddeler tam. Önerilen ekler: D-A (WAGO kararı, siparişten önce); §2-8 (22 AWG kırmızı pabuç).

### 3.7 Gizlilik ve sınırlar

- **Taranan:** `git diff 9a0c6fe` ile eklenen satırlar (`tasarim/freecad/` hariç) ve izlenmeyen 7 dosyanın tamamı; 17.032 satır.
- **Aranan kalıplar:** yerel kullanıcı yolu, sürücü harfli yol, bulut / geçici klasör, kullanıcı adı, takma ad, depo dışı dökümün adı, e-posta, parola / anahtar, ağ adı.
- **Sonuç:** Bulgu yok. URL'ler satıcı sayfaları.
- **Soyad:** Eklenen satırlarda iki eşleşme var, ikisi de `testler.html`'in yeniden üretilmiş satırları. Aynı soyad HEAD'deki test kâğıtlarında zaten var: `testler.html` HEAD 14 satır, şimdi 13; T3 2 / 2; T8 1 / 1. Paket soyad eklemedi, bir tane azalttı. Soyadının depodan temizlenmesi ayrı iş.
- **Sınırlar:**
  - `rehber/`, `planlama/rehber/`, `kod/` altında değişiklik yok.
  - `tasarim/freecad/` altında yalnız brief'in "bu paketten değil" dediği 13 PNG ve `montaj/yerlesim-kontrol.json` var.
- **Bu kontrolün kendi sınır ihlali:** K2R'nin bozma betiği ilk koşuda, kopyasında yol değişikliği tutmadığı için bir kez K2R'nin kendi geçici klasöründe koştu. Etkisi: o klasördeki çalışma kopyası (betiğin her koşuda zaten yeniden kurduğu kopya) yeniden kuruldu, sonuç dosyası (`bozma-sonuc.json`) üzerine yazıldı. K2R'nin metin çıktısına ve temiz kopyasına dokunulmadı. Depo etkilenmedi. Geçici klasör dışında dosya taşınmadı ya da silinmedi.

### 3.8 C adımı için liste

- **Commit'e girecekler:** GN §17-4 listesi `git status` ile birebir tutuyor: 23 değişen + 7 izlenmeyen; 13 PNG ve `yerlesim-kontrol.json` hariç. Bu rapor (`planlama/d158/P107a-kontrol-3.md`) eklenir.
- **`dongu-158.md` (GN §17-1, -2):** Metin "üçüncü kontrol `P107a-kontrol-3.md`: DÜZELTME GEREKLİ, bulgular proje sahibine (D-A WAGO, D-B / D-C denetim)" diye tamamlanmalı. "97 / 97 bozma" yanında bu kontrolün kaçan sınıfları anılmalı. Bugünkü satır hâlâ "A adımı 14.11 ≈ 03:50" diyor.
- **`karar-kuyrugu.md` (GN §17-3):** 1235, 1260 ve 1264 kapanışları doğru. Ek olarak:
  - (a) D-A için yeni karar maddesi: klemens serisi, onaylı satıcı dışı, 16.11'den önce.
  - (b) D-B ve D-C denetim düzeltmesi açık iş olarak P10.7b'den önce.
  - (c) §2-1 köprü şartı ve §2-7 rehber satırları P10.7b listesine.

## 4. Bakılmadı

- WAGO 2273'ün üretici sayfası doğrudan açılmadı. Dağıtıcı veri sayfaları ve WAGO'nun seri kataloğu arama sonuçlarından okundu; 221 serisinin 22 AWG'yi aldığı da doğrulanmadı.
- NEC, NFPA 79 ve 33 CFR tabloları bu turda yeniden açılmadı (K2R ve ilk kontrol okumuştu).
- XL4016 Rev 1.3; BTS7960 akım sınırı; sigorta kutusu, BTS güç klemensi, 5,08 mm klemens ve röle soketinin aldığı kesit.
- Web fiyatı: bu turda hiçbir fiyat sayfası açılmadı.
- F9b'nin tarayıcı kısmı.
- Hiçbir akım, boy ya da sıcaklık ölçülmedi (malzeme yok). Ani akım ve köprü değerleri hesaptır.
