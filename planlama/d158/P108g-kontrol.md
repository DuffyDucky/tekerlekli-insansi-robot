# P10.8g bağımsız kontrol (B ajanı)

Paket: P10.8g "ufak beş", A'nın commit edilmemiş çalışma ağacı. Dal `lale-duzeltme`, HEAD `94cd024`. Kontrol 22.11 04:25–04:50 (saat okundu).
B hiçbir paket dosyasını değiştirmedi; `git add` / commit / push yok; rehber yeniden üretilmedi; tam çakışma taraması koşulmadı.
Geçici çıktılar depo dışında (oturum scratch klasörü `p108g-b\`). Depoya yazılan tek dosya bu belge.

## 1. Hüküm: **KOŞULLU GEÇER**

Commit'i engelleyen kusur yok. Beş iddianın dördü teslim edilen çıktıdan doğrulandı, beşincisi (F9c) iddia edildiği gibi açık.
Koşullar (commit'i durdurmaz; kayıt eşitlemesinde kuyruğa yazılmalı): § 4 K1–K4. Özetle: 17.5 basılı karesi tek başına dokuz saplamayı
güvenilir biçimde ayırt ettirmiyor; büyük yazı bazı saplamaların gövdesini örtüyor; uç numaraları kâğıtta hâlâ ≈ 2,4 pt.

## 2. Kapsam ve dokunulmazlar (ölçülen)

| Ne | Sonuç |
| --- | --- |
| `git status --short` | 47 satır: 35 M + 12 ?? (A'nın `sonra/git-status-son.txt`'iyle aynı) |
| 21 eski kir (14 M + 7 ??) | `git-status-bas.txt` listesiyle aynı; `md5sum -c P108f-olcum/kir-bas.md5` 21 / 21 OK (izlenen md5 dosyası HEAD ile aynı) |
| CAD kaynakları | `tasarim/` altında değişen: yalnız 13 `kabuk/gorsel/*.png` + `montaj/yerlesim-kontrol.json` (eski kir, mtime 3.11 / 9.11, md5 aynı) ve `rehber/rehber_metin.py` (rehber metni, CAD geometrisi değil). `tasarim/cad/**` ve FCStd / geometri betiği değişmedi |
| `carpisma_kos.py kontrol` | çıkış 0, "izlenen 17 dosyanın özetleri kayıtla aynı"; `carpisma-sonuc.json` HEAD ile aynı |
| Denetim betikleri | `F9c-dogrula.py`, `F9c-uret.py`, `F9b-dogrula.py`, `F10*-dogrula.py`, `rehber_denetim.py`, `rehber_kablo.py`, `rehber_uret.py`, `rehber_gorunum.py`, `regresyon.py`, `carpisma_kos.py`, `P108f-etiket-bozma.py`: `git diff HEAD` boş. Muafiyet / gevşetme yok |
| Değişen denetim aracı | yalnız `P108f-etiket-olc.py` (satır satır okundu, § 5): kural seti P10.8f'ten gevşemedi, iki yeni HATA dalı eklendi (teslim farkı ≠ 0, kutu karenin dışında) |

## 3. Maddeler: B'nin ölçümü ve A ile farkı

| # | A'nın iddiası | B'nin ölçümü (bağımsız yol) | Hüküm |
| --- | --- | --- | --- |
| 1 | 17.1 ve 17.5'te 9 / 9, kadraj içinde | Veri: `rehber-veri.json` HEAD'e göre yapısal fark yalnız 17.1 ve 17.5'e `etiket` (A1–A4, Y1–Y5, 9 ayrı parça kimliği) + `etiket_not` ve iki sayaç (8 fark, başka değişiklik yok). Kendi `P108f-etiket-olc.py` koşum: 4 konum, 28 yazı, 8 / 8 çekimde teslim farkı 0, çizilmeyen 0, kadraj dışı 0. Gözle: 17.1, 17.5 yazdırma + etkileşimli karede dokuzu da var, kadraj içinde, kutu kutuya binmiyor | **Doğrulandı** (okunurluk sınırı § 4 K1–K2) |
| 2 | 17.11 U06 notu PDF s. 26'da | PyMuPDF metin araması: "yalnız taban bölümü" HEAD PDF'te hiçbir sayfada yok, çalışma ağacı PDF'te yalnız s. 26; satır 8,1 pt, y 649 pt, 17.11 karesinin (y 517–647) hemen altında; s. 26 100 dpi gözle bakıldı. `semaOnMetin` app.js lejantıyla aynı metni kuruyor (`SEMA[i].ad.split(":")[0] + ": " + not_`); veride `sema_on` tek kayıt (17.11) | **Doğrulandı** |
| 3 | parça etiketi 2,4 → 8,1–8,4 pt | Bağımsız yol: PDF sayfası MuPDF ile 1.200 / 2.400 dpi rasterleştirildi, etiket kutusu içindeki koyu satır yüksekliği ölçüldü (A'nın `yazi_px × ölçek`'i kullanılmadı). Büyük harf / rakam yüksekliği: s. 23 (17.1) 5,88–5,94 pt, s. 24 (17.4) 5,94–6,00 pt, s. 24 (17.5) 5,88–5,94 pt, s. 13 (B5a, yalnız "A") 5,73 pt. Aynı yöntemle sayfanın 8,1 pt gövde metninin büyük harfi ("Karedeki", s. 23; "ESP32", s. 26) 5,64 pt. Yani etiket yazısı 8,1 pt gövde metninden %2–6 büyük (em ≈ 8,2–8,6 pt). Önce (HEAD PDF): B5a 1,74 pt, 17.4 "A1" 1,80 pt büyük harf (em ≈ 2,5 pt). Kare basılı genişliği: alt adım 75,9 mm, B5a 73,3 mm; PDF'teki 141 karenin en darı 73,3 mm (47 px'in dayandığı alt sınır doğru) | **Doğrulandı** (parça etiketi için). Uç numarası: rakam ≈ 9–10 px ≈ 1,7 pt büyük harf (≈ 2,4 pt em), değişmedi |
| 4 | F9c kapanmadı; TAHMİN ölçülenle düzeltildi; çalışma ağacında 0 | `F9c-dogrula.py --tarayicisiz` B koşumu: GEÇER (hata 0). `P108f-gunluk.md` farkı yalnız üç ekleme (eski TAHMİN metni silinmemiş, yanına ölçülen 3). `sonuc-rapor.html` farkı yalnız 117 → 118, `f4870bf` → `94cd024`, P10.8 hücresine `94cd024` (kelime düzeyinde diff). HEAD'deki 3 hata A'nın `once/F9c-tarayicisiz.log`'undan okundu; B HEAD sayfasıyla ayrıca koşmadı (izlenen dosyayı geri almak gerekirdi) | **Doğrulandı**; commit'ten sonra 3 beklenir (yapısal, muaf değil) |
| 5 | `P108f-etiket-olc.py` teslim karesini ölçüyor | B koşumu: 8 / 8 fark 0 (çıkış 0). **Bozma sınaması (B):** rehber kopyasında yalnız `ETK.F` 47 → 46 px yapıldı, araç teslim karelerine karşı koşuldu: çıkış 2, KALDI, 4 HATA "ölçülen kare teslim edilen kare değil" (12: 43.448 px, 17.1: 7.038, 17.4: 7.104, 17.5: 7.172). 1 px yazı farkını yakalıyor | **Doğrulandı** |

## 4. Bulunan kusurlar (önem sırasıyla; hiçbiri commit'i engellemiyor)

- **K1 (orta) 17.5 basılı karesi: dokuz saplama tek başına ayırt edilemez.** Yazılar okunuyor (≈ 8,4 pt) ama saplama kümesi basılı
  karede ≈ 27 × 18 pt (≈ 10 × 6 mm); saplamalar 1 mm'lik lekeler, bağlantı çizgileri ≈ 0,2 pt. Etiket noktası ile kutu ölçüsü
  (`sonra/etiket-olc.json`, 17.5 sahne): 9 yazının 6'sında nokta **başka bir yazının kutusuna kendi kutusundan daha yakın** (A1 noktası
  Y1 kutusuna 5 px, kendi kutusuna 36 px; A3 70 / 5; Y3 115 / 33; Y4 70 / 16; Y2, A2 benzer). Y3'ün çizgisi uç 3 dairesinin altından
  geçiyor. 300 dpi'de bakıldı (s. 24): eşlemeyi ancak çizgi takibiyle ve numaralama kuralıyla ("soldan sağa") yapmak mümkün.
  **B hükmü: montajcı 17.5 karesinden tek başına dokuz saplamayı güvenilir biçimde ayırt EDEMEZ;** 17.1 ve 17.4 (aynı numaralar, daha
  yakın kamera) ve etkileşimli rehberle birlikte kullanılabilir. A'nın "okunuyor ama kalabalık" notundan daha sert: yazı okunuyor, eşleme güvenilir değil.
  Öneri (rehber kararı): 17.5'e saplamalara odaklı ikinci kare / kamera, ya da basılı sayfada 17.5 karesine "saplamalar için 17.1 / 17.4
  karesine bak" notu. Kuyruğa açık iş olarak yazılmalı.
- **K2 (orta) Büyük yazı kutuları saplamanın kendisini örtüyor.** Nokta parçanın üst yüzünde, yazı noktanın altına düştüğünde kutu
  saplama gövdesini / somununu kapatıyor: 17.1 A2, A3 (kutu noktanın 7 px altında; HEAD karesinde görünen saplama gövdesi ve somun yazının
  arkasında kaldı), 17.4 A2, A3, Y2. 17.4'te G09 / G11'in takılacağı A3 saplaması örtülü. Yerleşim kuralı yalnız noktayı korur
  (`app.js` `eNokta` 3 px kuralı); "kusur" sayımı yazının parçayı örtmesini saymaz. B5a'da yazı arkadaki siyah kutunun üst yarısını
  örtüyor (A da yazdı).
- **K3 (düşük) "kusur" ölçüsü eksik sayıyor.** `app.js` `kusur()` yalnız parça etiketi çizgilerinin birbirini kesmesini ve çizginin başka
  parça etiketi kutusundan geçmesini sayar; uç etiketi dairesi / çizgisiyle kesişme sayılmaz (17.5'te Y3 çizgisi uç 3 dairesinden geçiyor,
  ölçülen kusur 0). `kutuKes` 8 örnekle bakar; kutunun köşesinden geçen çizgiyi kaçırabilir. Seçim sezgisi olarak kabul edilebilir;
  "kusur 0" bir kalite kanıtı olarak sunulmamalı.
- **K4 (düşük, iddia düzeltmesi) Etkileşimli kip her zaman "üst" değil.** A: "etkileşimli kipte dördü de üst". Bu 1400 × 900 için doğru
  (B de ölçtü). 360 px telefonda (CDP, `mobile=True`) 17.4 radyal (kusur 1), 17.5 radyal (kusur 4) seçiliyor. Kutu çakışması yok
  (parça-parça 0, parça-uç kutusu 0), konsol hatası 0, yatay taşma 0; ama 17.5 telefonda Y4 ve Y5 kutusunu uç 4 / uç 1 çizgisi ve
  dairesi kısmen örtüyor. Aynı tür örtüşme HEAD'de 17.4 telefonda da vardı (A2, A4, Y3), yeni bir bozulma değil; 17.5'te yeni içerik.
- **K5 (düşük) `P108g-yazi-pt.py`'nin GEÇTİ ölçütü yapılandırmayı okur.** "em" = `yazi_px` (app.js `ETK.F`) × ölçek: çizilen glifi değil,
  ayarlanan değeri ölçer; tek gerçek ölçü ikinci sütun (koyu piksel yüksekliği). B'nin bağımsız ölçümü bu sütunla uyuşuyor (5,92 / 5,94 pt).
- **K6 (bilgi) Sabit ölçü.** `ETK.F = 47` yazdir.html'in bugünkü en dar karesine (73,3 mm, `GH_MIN` döngüsü) bağlı; yazdır yerleşimi
  değişirse sessizce 8 pt'nin altına düşer. Bugün koruyan şey `P108g-yazi-pt.py` (zincirde değil). Zincire alınması önerilir.

Kod incelemesinde **yanlış sonuç veren mantık hatası bulunmadı**: `eYerlestir` sekiz yönlü kipte eski kodla aynı (`Math.abs(dx)` ↔
`dx ? 1 : 0`); radyal yalnız "üst" yerleşimde kusur / çizilemeyen varsa ve nokta > 2 ise denenir, seçim önce çizilemeyen sayısı, sonra
kusur, eşitte eski yerleşim. `ETK.cizilmedi` sıfırlanıp birleştiriliyor (önceki itmeler kaybolmuyor). `RehberTest.etiket()` eklemeleri
yalnız sınama arayüzü. `_SAPLAMA` sözlüğü üç anahtarda paylaşılıyor; `etiket_isle` onu değiştirmediği sürece sorun değil (üretim 9 / 9 ×
3 verdi). `P108f-etiket-olc.py`: PIL yoksa / teslim karesi yoksa `teslim_fark` None → HATA (sessiz geçiş yok); başlangıç görüntü alanı
`--dump-dom` ile ölçülüyor (sabit değil); geçici çekim klasörü `%TEMP%`'te silinmeden kalıyor (depo dışı, önemsiz). `P108g-onizleme.py`
`VERI_DIR`'i kopyaya çeviriyor; `rehber_gorunum` yalnız `VERI_DIR`'e yazıyor (depoya yazmaz). `P108g-zincir.sh` = `P108f-zincir.sh`, fark
yalnız iki yorum satırı ve log yolu.

## 5. Etkileşimli rehber (`rehber/index.html`)

CDP (rehber_uret.Cdp), çekim kipi olmadan, 1400 × 900: 17.5, 17.4, 12, 33.7, 5 açıldı; `error` / `unhandledrejection` / `console.error`
yakalayıcısı: **0**. 17.5 / 17.4 / 12'de parça etiketi 9 / 9 / 1, çizilmeyen 0, 12 px, "üst". 33.7 ve 5'te parça etiketi yok (beklenen).
360 px: § 4 K4. Etkileşimli teslim kareleri 12 ve 17-04 HEAD ile bayt bayt aynı; 33-07 farkı 68 piksel, en büyük Σ|ΔRGB| 5 (gürültü).
Koyu tema açılmadı.

## 6. Zincirin geçerliliği

Zincir 03:26:59–04:22:11 (`zincir.durum`: 15 / 15 çıkış 0). Zincirin girdisi olan dosyaların son değişikliği: kaynaklar 02:33–02:48,
kareler 02:53–03:00, PDF 03:03, `kontrol.json` 03:26:17, `sonuc-rapor.html` 03:27:34 (F9c-uret, zincir 2b'den önce; F9b 04:22'de
okudu). 04:22:11'den sonra değişen tek dosya `P108g-gunluk.md` (04:22:51, zincir girdisi değil). **Zincir sonucundan şüphe yok;
yeniden koşulmadı.** Ucuz denetimler B tarafından koşuldu (§ 7).

## 7. B'nin koştuğu komutlar (depo kökünden, `PYTHONIOENCODING=utf-8`, `py -3 -B -X utf8`)

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `cd tasarim/freecad && carpisma_kos.py kontrol` | 0 | 17 dosya kayıtla aynı |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0 | ascii 0, onaylı kritik girdi farkı 0 (219 / 258 / 1201), CAD 975 |
| `tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | SONUÇ GEÇER |
| `planlama/d158/F9c-dogrula.py --tarayicisiz` | 0 | GEÇER (hata 0) |
| `node --check rehber/app.js` | 0 | |
| `planlama/d158/P108f-etiket-olc.py --json <scratch> --png <scratch>` | 0 | 4 konum, 28 yazı, 8 / 8 teslim farkı 0, GECTI |
| aynı araç, rehber kopyasında `ETK.F` 46 px (bozma) | 2 | KALDI, 4 HATA (beklenen) |
| B betikleri (scratch): PDF metin araması, 1.200 / 2.400 dpi glif yüksekliği, görüntü yerleşimi, `rehber-veri.json` yapısal fark, CDP etkileşimli + 360 px | 0 | § 3–§ 5 |

Yazma denetimi: koşulardan önce ve sonra `git status --short` aynı, değişen / izlenmeyen 173 dosyanın md5'i aynı, `git ls-files -s`
özeti aynı, `kir-bas.md5` 21 / 21 OK. Koşulan denetimlerin hiçbiri izlenen dosya yazmıyor (okundu: `rehber_kablo` yalnız `--sema-boy-yaz`
ile, `carpisma_kos` yalnız `birlestir` / koşuda yazar).

## 8. Kapsam kararı (madde 3)

Kaynak tanım (`karar-kuyrugu.md` "P10.8f kapanışından açık iş", `P108f-kontrol.md` N3): "PDF'te etiket yazısı çok küçük: … 14 px yazı ≈
2,4 pt (uç numaraları da aynı ölçekte)". 14 px parça etiketinin boyu (uç numarası 13 px); uç numaraları parantez içinde bağlam olarak
anılıyor ve N3 "uç numaraları da öyle olduğu için yeni bir kusur değil" diyor. **Sınırlama metnin lafzına göre savunulabilir.** Ama
gerekçe ("kâğıtta çok küçük") uç numaraları için de geçerli: uç adı karenin altında 8,1 pt, onu karedeki yere bağlayan tek şey ≈ 2,4 pt
rakam. Bu yüzden "madde 3 kapandı" yalnız parça etiketi için yazılmalı; uç numaraları (ve ≈ 2,5 pt kare başlık / lejant şeritleri,
anlamları karenin altında tekrarlandığı için daha düşük öncelik) kuyrukta ayrı açık iş olarak kalmalı. A § 10'da yazdı; kuyruğa
taşınması kayıt eşitlemesinin işi.

## 9. Commit listesi önerisi

**A'nın § 11 listesi doğru ve eksiksiz** (21 M + 5 yeni; 21 eski kir ve `FREECAD-KILIT.txt` dışarıda). Ek: bu belge
`planlama/d158/P108g-kontrol.md`.

**`P108g-olcum/` (20,7 MB, 127 dosya): tamamı girsin.** Emsal: `f4870bf` `P108f-olcum/`'un tamamını (11 MB, `onizleme/` dahil) ve
`P108f-kontrol-olcum/`'u aldı. Ayrıca gerçek depo büyümesi küçük: dosyaların git blob özeti B tarafından hesaplandı; HEAD'de ya da bu
committeki teslim karelerinde zaten bulunan ya da klasör içinde tekrar eden içerik 17,9 MB (`once/kare` = HEAD kareleri,
`sonra/kare` ve `sonra/etiket-cekim/*-sahne` = teslim kareleriyle bayt bayt aynı, `onizleme/iki`, `uc`, `uc2` kareleri teslim edilenle
aynı). **Yeni benzersiz içerik ≈ 2,8 MB.** Klasörden ayıklamak yerden kazandırmaz, kanıt zincirini bozar. `onizleme/ilk` reddedilen
yerleşimin tek kanıtı, kalmalı.

**Girmeyecek:** 21 eski kir (14 `tasarim/freecad/kabuk/gorsel/*.png` + `montaj/yerlesim-kontrol.json` M; `geometri*_cikar.py`,
`geometri2_dogrula.py`, `gez.js`, `uc.js`, `P108d-kontrol-olcum/b2-tarama.nabiz`, `P108d-olcum/ara1.json` ??), `FREECAD-KILIT.txt`.

**Commit'ten önce / sonra:** önce `F9c-dogrula.py --tarayicisiz` 0 (B 04:4x'te 0 ölçtü); sonra 3 beklenir (yapısal, § 3 madde 4).

## 10. Özel veri taraması (gidecek dosyalar)

§ 11 listesinin metin dosyaları ve `P108g-olcum/` (34 log, 12 json, 3 txt, 2 durum) tarandı: e-posta 0, telefon (+90 / 05xx) 0,
API anahtarı / belirteç (`sk-`, `ghp_`, `AKIA`, özel anahtar başlığı, bearer) 0, parola / şifre / token sözcüğü yalnız
`P108f-gunluk.md:288`'de (önceki taramanın kalıp listesi, veri değil), yerel kullanıcı yolu (`C:\Users`, kullanıcı adı, `AppData`,
`Masaüstü`) 0, öğrenci no / kimlik no / IBAN / adres 0, resmî başvuru / sözleşme belgesi yok. `rehber/veri/robot-glb.js` base64
geometri (rastgele eşleşme, değişmedi). PDF üst verisi: yazar boş, üretici HeadlessChrome / Skia. 76 PNG rehber kareleri ve PDF sayfa
görüntüleri; kişisel içerik görülmedi (her biri tek tek açılmadı: açılanlar § 3–§ 5'tekiler). **Bulgu yok.**

## 11. Bakılmayanlar

Koyu tema; gerçek yazıcı çıktısı (PDF 100 / 300 dpi görüntüsüyle bakıldı); HEAD sayfasıyla F9c'nin 3 hatası (A'nın logundan okundu);
F10a / d / e / f ve tam zincir yeniden koşulmadı (zamanlama şüphesi yok); tam çakışma taraması koşulmadı (yasak); `P108g-olcum/`'daki
PNG'lerin tamamı tek tek açılmadı; 17.5'in yeterliliği gerçek bir montajcıyla sınanmadı (B'nin hükmü göz + ölçü).
