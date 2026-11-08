# F8d günlüğü (P8.4 ek test kâğıtları) — tasarım ajanı A, 08.11.2026

Brief: `planlama/d158/F8d-brief.md`. Plan satırı: `planlama/dongu-158.md:137` (P8.4).
Yazma alanı: `planlama/d158/testler/` ve bu dosya. CAD betikleri koşulmadı; commit, push, silme yok.

## Okunan kaynaklar
`planlama/d158/testler/00-genel.md`, T1, T3, T4, T9 (tamamı), `testler_html.py`; `planlama/d158/F8c-kontrol.md` (üç tur, güvenlik bulguları G1–G6,
R1–R6 ve "kalan öneriler"); `F8c-gunluk.md`; `planlama/d158/karar-kuyrugu.md` (K2 notu, K8, K12, satır 298);
`tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md:97-119`; `planlama/duzeltme-plani.md:28-34`, `:63`; `planlama/adim1/P-pi-kafada.md` (ısı ve servo
satırları); `planlama/adim3/elektrik.md` (`:16-28`, `:50-62`, `:215-232`, `:266-272`, `:286-347`, `:474-480`); `planlama/kararlar-2026-10-29.md:70-126`;
`planlama/y3/Y3-kontrol.md` (tamamı), `Y3-gunluk.md:1-74`; `planlama/adim4/M6-montaj-sirasi.md:200-240`; `tasarim/freecad/arayuz.py` (`:436-449`,
`:655-667`, `:950-977`); `tasarim/freecad/kabuk/kabuk_parcalar.py:685-716`, `kabuk_montaj.py:155-200`, `kabuk-analiz.json` (braket kontrolleri);
`tasarim/freecad/taban/taban-analiz.json` (`robot.pozlar[ev]`, `donus.kutle_kg`, `motor`); `kafa-yerlesim/uygulama-ivme.json` (`yontem`, `ev`, `izgara_yuk_*`);
`planlama/adim5/maliyet_duzelt.py:233-235`.

## Üretilenler ve değişenler
| Dosya | İş |
|---|---|
| `testler/T10-kafa-isi.md` | Yeni: kapalı kafada tilt servosu, kafa içi hava, SoC; ortam düzeltmesi; kollar sigortasız |
| `testler/T11-h1-sigorta-acikligi.md` | Yeni: gerçek sigorta kutusu + 64 × 50 karton şablon; açıkta yuva sayısı |
| `testler/T12-percin-somun.md` | Yeni: M5/M3 perçin somun ölçüsü, kupon + pul yığını ile kavrama (tur sayımı), ana anahtar ve acil stop delikleri |
| `testler/T13-rampada-acil-stop.md` | Yeni: A ip yükü (ip bağlı, boşluksuz), B kayma (2 cm boşluk), C hareket hâlinde duruş yolu; sıra kuralı A → B → C |
| `testler/T1-jgb37-durma-torku.md` | Ek (adım 5): 12,8 V'ta motor ucu 12,0 V'a ulaşmazsa seri multimetreyi çıkarmak **zorunlu**; çıkınca da ulaşmazsa kablo düzeltilir, deneme "düşük V" |
| `testler/T4-pam8403-ses-karti.md` | Ek (adım 5): ilk dinleme ve telefonun yerleştirilmesi **acil stop mantarı basılıyken** (`elektrik.md:216,222,227`); mantar ancak herkes alan dışındayken bırakılır |
| `testler/00-genel.md` | Başlık "P8.3, P8.4"; `:3` durum satırı (T1–T9 GEÇER, P8.4 kontrol bekliyor); kâğıt tablosuna T10–T13; sıra; akım bölümü; alet listesi (+4 satır); kısaltma tablosuna 9 dosya |
| T2–T9 | Yalnız başlık sayacı "/ 9" → "/ 13" |
| `testler/testler_html.py` | Yalnız açıklama satırı ve sayfa başlığı ("P8.3, P8.4"); çevirici aynı (glob T10–T13'ü kendisi alıyor, sıralama sayısal) |
| `testler/testler.html` | Yeniden üretildi |

## Kontrol (tarayıcısız)
- `py -3 planlama\d158\testler\testler_html.py --kontrol` → "md dosyası: 14 (kâğıt T: 13), HTML bölümü: 14, iç bağlantı: 68, id: 166,
  KONTROL GEÇTİ", çıkış 0.
- Ek: .md tablo sayısı 81 = HTML tablo sayısı 81; HTML gövdesinde kod dışında kalan `**` 0, ters tırnak 0; `testler/` içinde takma ad 0.
- Yeni ve değişen metindeki `dosya:satır` atıflarının hepsi betikle açılıp okundu. İlk taramada iki kayma bulundu ve düzeltildi:
  `M6-montaj-sirasi.md:227 → :228` (45 mm satırı), `elektrik.md:340-344 → :341-344`. `karar-kuyrugu.md` başka bir ajan tarafından değiştirilmiş
  (dosya sonuna ekleme); atıf verilen satırlar (25, 94, 149, 184, 189, 298) yerinde.
- JSON anahtarları `py -3` ile okundu: `taban-analiz.json` `robot.pozlar[0]` (ev) `rampa5.geri` 2,41, `pay_geri` 1,61, `donus.kutle_kg` 25,911;
  `uygulama-ivme.json` `yontem` "a_sinir = a_dev_min / 1.5".
- Kendi bulduğum hata (düzeltildi): T13'te duruş yolu sınırı ilk yazımda "v² ÷ 3,22 (cm)" idi; formül metre verir. Şimdi "31 × v² ≤ d ≤ 500 × v² (d cm, v m/s)".

## Kâğıtlar: geçer sınırları ve doğruladığı varsayım
| Kâğıt | Geçer sınırı | Doğruladığı varsayım (kaynak) |
|---|---|---|
| T10 kafa ısısı | S2 stres sonunda tilt servo gövdesi, 30 °C ortama düzeltilmiş **≤ 50 °C**; SoC **≤ 75 °C**; `get_throttled` **0x0**; durdurma kuralı (servo ölçülen 55 °C, SoC 80 °C) **işlemedi** | Yarıklı kafa yeter, fan gerekmez (`qled-not:119`, K12 varsayılanı a); kafa içi 48,2 / 50,9 °C hesabı (`qled-not:116-117`) |
| T11 H1 açıklığı | Açıkta (şablonda tamamen içte, kenara ≥ 3 mm, pense ile çıkar) yuva **≥ 4**; kutu **≤ 105 × 60 × 35 mm**; delikler **iki, aralık 94 mm** | 64 × 50 açıklık yeter, uç yuvalar yedek (`kararlar:114-115`, `elektrik.md:345-347`); kutu zarfı tahmini (`arayuz.py:655`) |
| T12 perçin + delikler | Flanş M5 ≤ Ø10,6 × 1,1, M3 ≤ Ø7,6 × 0,9; gövde M5 ≥ 8,3, M3 ≥ 6,3 mm; kavrama aralığı 3,0 / 2,0 mm'yi içerir; somun dönmesi **0**; kavrama **≥ 5 tur**; ana anahtar geçen kısım + 1 ≤ **30,0 mm** (30–40,8 KOŞULLU), üstte kalan ≤ **46,8 mm**; acil stop gövde + 0,1 ≤ **22,4 mm** | Perçin somun ölçüleri tahmini (`arayuz.py:961-965`); "kavrama ~2 diş olabilir" (`Y3-kontrol.md:42-43`); gövde ≥ 8,3 (`kararlar:121-122`); K7 Ø30 tahmini (`arayuz.py:976-977`); acil stop "etek deliği kontrol" (`elektrik.md:62`) |
| T13 rampada acil stop | A: F_acil − F_ön **≤ 0,10 kg**; B: 30 s'de kayma **≤ 1,0 cm**, ip gerilmedi; C: **31 × v² ≤ d ≤ 500 × v²** (cm), sonra 30 s'de ≤ 1,0 cm, teker kalkması / devrilme ipi **0** | Acil stopta robot rampada kendini tutar mı (`kararlar:83`, E6 `duzeltme-plani.md:63`: açık risk); devrilme 2,41 m/s² ÷ 1,5 = 1,61 (`taban-analiz.json`); rampa fren 0,1 (`kararlar:77`) |

## Kaynak bulunamayan değerler (kâğıtlarda "varsayım" ya da "dış kaynak" diye işaretli)
- **T10:** ortam düzeltmesi (artış ortamdan bağımsız, düzeltilmiş = ölçülen + 30 − ortam); ortam 20–30 °C; termokupl teli ≥ 1,5 m; kafa erişim alanı + 0,5 m (T8'den);
  okuma aralığı 10 dk; süre S1 60 dk, S2 en az 60 en çok 120 dk; kararlılık ≤ 0,5 °C / 10 dk; uzun testte ses %50 (T4'ün 30 s kuralından türetildi).
- **T11:** pense için kenara ≥ 3 mm; gerçek kutu dış çerçevesinin merkezinden modeldeki yere bağlanır.
- **T12:** kavrama ≥ 5 tur (≈ 0,8 × çap, standart somun yüksekliği; dış kaynak, depoda yok); M5 0,8 / M3 0,5 mm diş adımı (ISO kaba diş, dış kaynak);
  pul yığını ± 0,2 mm; ana anahtar için 1 mm geçiş payı ve H1'e en az 3 mm et; acil stop için 0,1 mm geçiş payı.
- **T13:** A eşiği 0,10 kg (kantar çözünürlüğünün 10 katı); B/C 1,0 cm (şerit/video okuma payı, T9'un varsayımı); B'de 30 s bekleme; ölçüm noktası
  uçlara en az robot boyu. Türetilenler (hesap, yeni varsayım değil): 2,26 kg = m × sin 5°; 0,56 m/s² (c_rr 0,03 `arayuz.py:667`); 0,15 m/s; d sınırları.

## Bulgular (karar değil, orkestratöre)
1. **`karar-kuyrugu.md:298` iki ayrı açığı birleştiriyor:** "K7 perçin delik çapı". Kaynakta (`Y3-kontrol.md:113-115`) K7 **ana anahtar deliği**
   (Ø30 tahmini, `arayuz.py:976-977`), perçin somun ölçüleri ayrı madde. T12 ikisini de kapsıyor (Bölüm A/B perçin, C delikler); acil stop deliği
   (`elektrik.md:62` "etek deliği kontrol") de C'ye eklendi.
2. **T13 acil stopu yazılım komutuyla tetikliyor.** Mantar etekte; basmak için düşme hattına girmek gerekir. Kâğıt "devreden çıkar" komutunu (röle
   K1 bırakır, etkisi aynı) kullanıyor ve komutun var olduğunun Efe tarafından teyidini istiyor. Ortak kural 1'deki "acil stop elde" ifadesinin
   donanımda karşılığı (uzatma kablolu düğme ya da kumanda) kaynakta tanımlı değil: bu T6, T8, T9 için de geçerli bir açık.
3. **T13'ün iki yönlü riski:** dişli kutusu geri sürülüyorsa robot yuvarlanır; sürülmüyorsa inişte ani durur. Kâğıt ikisini de ölçüyor (C alt ve üst sınır).
   Kaba enerji hesabım (nokta kütle, ev pozu, Δh ≈ 15 mm) ani duruşta devrilme için v ≈ 0,58 m/s veriyor (> 0,393 m/s en yüksek hız); kâğıda
   ölçüt olarak konmadı, tasarım ajanı doğrulamalı. Dinamik fren yuvarlanmayı yavaşlatır, durarak tutmaz (sürünme kalabilir): kâğıtta not.
4. **T10'da tilt servosu güçlü olmalı** (hesapta servonun kendi ısısı yok); kollar güçsüz kalsın diye XL4016 A/B hat sigortaları enerji kesikken
   çıkarılıyor. Bu, ortak kural 1'e ("dal sigortası takılı olmadan enerji verilmez") uyuyor: sigortasız dal enerjisiz.
5. **T12 braketlerden ve etekten önce yapılmalı:** delik çapı ya da ölçü değişirse delinmiş braket / basılmış etek boşa gider. 00-genel sırasına yazıldı.
6. Değerler 1,65 m Y3 modelinden gelenler (H1 açıklığı boşlukları 8,4 / 3,4 mm, perçin geometri kontrolleri) 1,58 m'de yeniden ölçülmedi; kâğıtlarda yazılı.

## Düzeltme turu 1 (08.11.2026)

Girdi: `planlama/d158/F8d-kontrol.md` (GEÇMEZ: T13 C güvenliği). 1–8 zorunlu, 9–16 öneri; hepsi uygulandı.

| # | Düzeltme | Yer | Durum |
|---|---|---|---|
| 1 | Ön şartlar D1 (Efe komut teyidi), D2 (düz zeminde bara ≤ 0,5 s, 3 deneme, `elektrik.md:225`, varsayım), D3 (bağlantı kopunca ≤ 0,5 s duruş, `yazilim-plani.md:35`, `:75`; risk `hakem-3.md:105`), D4 (yedek yol). C bunlar olmadan **YAPILMAZ**, "C yapılmadı" kuyruğa; Tablo 0 eklendi | T13 güvenlik, Yöntem başı, C başlığı, adım 10, geçer tablosu, Sonuç | ✅ |
| 2 | Komut 1 s içinde barayı düşürmezse 5 adım (ölü adam tuşu, ipler gergin, D4'te denenmiş ESP32 reset `elektrik.md:226`, `:229`, kimse düşme hattına girmez, mantara yalnız robot hareketsizken yandan) | T13 güvenlik | ✅ |
| 3 | Çıkışta ip durdurmaz: gidiş doğrultusu boş (üst uçtan sonra ≥ 3 m, varsayım), dayanak ve ip tutan doğrultu dışında (≥ 1 m yanda, varsayım); çıkışta acil stop alt yarıda | T13 güvenlik, Yöntem, adım 10–11; T9 güvenlik | ✅ |
| 4 | En az 3 kişi (taban ipi, devrilme ipi, kumanda; kumandayı tutan ip tutmaz), video tripodda | T13 güvenlik, Tablo 0 görevler; T9; 00-genel kural 1 | ✅ |
| 5 | 00-genel kural 1 yeniden: mantar etekte, uzaktan acil stop yok; görevi yalnız mantar olan ayrı kişi, erişilemiyorsa test yok; rampa kâğıtları istisna (D1–D3 doğrulanmış komut + iki ip). T9 adım 13 "acil stop düğmesiyle" kaldırıldı → T13 A; T9 "acil stopu tutan" → "kumandayı tutan"; T9-B'ye D1–D3 şartı; T6, T8, T10 "acil stop elde" → kural 1 | 00-genel, T9, T6, T8, T10 | ✅ |
| 6 | T10 pens ve gerilim uçları enerji yokken gövdede (F3 sonrası kafa 12 V teli), kablolar dışarı, okuma alan dışından ya da fotoğraf, olmazsa "okunmadı"; T3 N1 yerine bu nokta | T10 alet, adım 3 | ✅ |
| 7 | T12 kupon kenarları eğeyle; mengene tablaya/tezgâha sabit | T12 alet, güvenlik | ✅ |
| 8 | T12 C: delik alt sınırı (üretici ±0,3 mm ya da dış çap ≥ delik + 4 mm, varsayım) → KOŞULLU; dönme kilidi tırnağı → KOŞULLU; mantar kilitlenmesi satırı **varsayım, doğrulanmadı** | T12 varsayım tablosu, adım 10, Tablo 4 altı, geçer tablosu, Sınır aşılırsa | ✅ |
| 9 | T4: bırakmadan önce GPIO12 = 0 kontrolü, arkadan uzan, eli çek; NP2 BE102 kilitlenmesi "doğrulanmadı" | T4 adım 5 | ✅ |
| 10 | T11 delik aralığı 94 ± 0,5 mm (varsayım) | T11 geçer tablosu | ✅ |
| 11 | T11 şablon takozlarla 45 mm yüksekte (`M6-montaj-sirasi.md:228`, 125 cm modeli) | T11 alet, adım 4 | ✅ |
| 12 | T13 kaynak "`rampa5.geri` 2,41 ÷ 1,5"; pay ≥ 1,5 `uygulama-notu.md:35`. B'deki ±0,5 cm gerekçelendi (duran robot, mm şeritten doğrudan okuma; T9'un ±1 cm'si hareketli okuma) | T13 varsayım ve geçer tabloları | ✅ |
| 13 | d < 31·v² ama teker kalkmadı ve ip gerilmedi → **KOŞULLU: ani duruş** | T13 sonuç kuralı, Sınır aşılırsa, Sonuç kutusu | ✅ |
| 14 | C'de kantar ipin robot ucuna yakın ya da çıkarılır; rampa kısaysa v düşürülür (≥ 0,1 m/s, T9 adım 10) | T13 Yöntem, adım 10 | ✅ |
| 15 | T10 Tablo 2: okuma 10 dk, tamamı `T10-pi.log`; sigorta listesi F1, F3, F4, F5 (`elektrik.md:60`) | T10 güvenlik, Tablo 2 | ✅ (F4'ü "ESP32" diye yazmadım: `elektrik.md:60` F4'ü "XL4016 çevre" diyor) |
| 16 | T12: siparişte yalnız 2 yedek (`Y3-kontrol.md:63`), ek perçin somun önerisi (2'şer, varsayım) | T12 Sınır aşılırsa | ✅ |

Ek: 00-genel kısaltma tablosuna `yazilim-plani.md` eklendi; durum satırı "düzeltme turu 1 yapıldı, yeniden kontrol bekliyor"; T13 satırına "önce D1–D4".

**Yeni sonuç (orkestratöre):** kural 1 yeni hâliyle T9-B'yi de D1–D3'e bağlıyor. Efe "devreden çıkar" komutunu teyit edip düz zeminde
denenmeden hiçbir rampa denemesi yapılmaz. T13 A/B de D1–D3 istiyor (robot rampaya sürülüyor); kontrol C ile sınırlıydı, ben tutarlılık için genişlettim.
**Kaynak çelişkisi:** `arayuz.py:660` "Elde B200E-E (40 mm mantar)" diyor, `elektrik.md:62` alınan parçayı NP2 BE102 diye yazıyor; T12 C ikisini ölçüyle ayırır.

Kontrol: `py -3 testler_html.py --kontrol` → md 14 (kâğıt T: 13), HTML bölümü 14, iç bağlantı 86, id 166, **KONTROL GEÇTİ** (çıkış 0).
Tablo: md 82, HTML 82. Yeni `dosya:satır` atıfları betikle satır içeriğine karşı okundu. Takma ad yok.

## Düzeltme turu 2 (08.11.2026, son tur)

Girdi: `F8d-kontrol.md` "Yeniden kontrol 1" (KOŞULLU, GEÇER'e yakın). R1–R3 uygulandı; Ö1 açık iş olarak aşağıda, kâğıda dokunulmadı.

| # | Düzeltme | Yer | Durum |
|---|---|---|---|
| R1 | D3 (bağlantı kopma) robot yürümeden: esas düzen tekerler havada, şasi takozlarla kaldırılmış (`yazilim-plani.md:75` kabul denemesiyle aynı); olmuyorsa robot yerde, taban ipi arkadaki dayanağa ≤ 0,5 m boşlukla bağlı. Durmazsa: D2 komutu denenmez (aynı bağlantı), mantara tekerlerden uzak, arka köşeden basılır. Tablo 0'a düzen kutusu. T9-B'deki D3 tanımı aynı düzene bağlandı | T13 D3, Tablo 0; T9 güvenlik | ✅ |
| R2 | "Komut çalışmazsa" adım 4: bara açık, kollar güçlü; mantar arka-sağ köşede (`arayuz.py:436`); rampanın üst tarafından, arka köşeden, kol hizasının arkasından, tek kolla, gövde alt tarafa geçmez, devrilme ipi gergin. Arka köşe rampanın altına bakıyorsa uzanılmaz (ip sabitlenir, Efe'ye). D4'ün aynı telsiz bağlantısına bağlı olduğu notu D4'e ve adım 2'ye | T13 güvenlik, D4 | ✅ |
| R3 | T12 C başına "Robota takılacak acil stop: ☐ NP2 BE102 (`elektrik.md:62`) ☐ Emas B200E-E 40 mm, elde (`arayuz.py:660`) ☐ başka"; varsayım tablosuna çelişki satırı; adım 10, Tablo 4 satırı ve kilitlenme satırı "takılacak parça"ya; Sınır aşılırsa'ya çelişki maddesi. T4:69 "NP2 BE102'nin" → "takılan mantarın" | T12, T4 | ✅ |

**Tasarım ajanına:** acil stop parça çelişkisi. `elektrik.md:62` "acil stop NP2 BE102 (CAD 60 mm B200E60; etek deliği kontrol)",
`arayuz.py:660` "Elde B200E-E (40 mm mantar)". Hangisinin takılacağı T12 C'de işaretlenir; kaynaklardan biri ona göre düzeltilmeli.

**Açık iş (Ö1, kâğıda dokunulmadı):** mantar kişisinin duracağı yer. Mantarın (0,26 m yükseklik, `arayuz.py:44` Y_COV1; arka-sağ köşe,
`arayuz.py:436`) T8'in "tam uzanmış kolun ulaşabileceği yer + 0,5 m" bölgesinin (`T8:52`) dışında kalıp kalmadığı kol tarama hacmiyle
kontrol edilmedi. Kural 1 güvenli yönde işliyor ("erişilemiyorsa test yapılmaz") ama T6-B ve T8'i durdurabilir. Tasarım ajanı mantar
kişisinin yerini (robotun arkası, arka-sağ köşe) kol tarama hacmine göre bir kez işaretlemeli.

Kontrol: `py -3 testler_html.py --kontrol` → md 14 (kâğıt T: 13), HTML bölümü 14, iç bağlantı 86, id 166, **KONTROL GEÇTİ** (çıkış 0).
Tablo: md 82, HTML 82. Takma ad yok. Yeni atıflar (`yazilim-plani.md:75`, `arayuz.py:436`, `:660`, `elektrik.md:62`) satır içeriğine karşı okundu.
Yeni varsayım: D3'teki ≤ 0,5 m ip boşluğu (kontrolün önerdiği değer, kaynağı yok; T13 ve T9'da "varsayım" diye işaretli).

## Durum
Düzeltme turu 2 (son tur) bitti. Kontrolün notuna göre diff ve `--kontrol` yeterli.

## Kayıt ajanı: K1/K2 uygulandı (08.11.2026)

Girdi: `F8d-kontrol.md` "Yeniden kontrol 2" (GEÇER, K1 ve K2 koşuluyla; "diff'e bakmak yeter"). Kontrolün metni dışında satır eklenmedi;
yeni sayılar (0,1 m/s, 5 dk) kâğıtta "varsayım" diye işaretli.

| Kontrol maddesi | Kâğıttaki karşılığı | Uyum |
|---|---|---|
| K1: yedek düzende hız ≤ 0,1 m/s (varsayım) | T13 D3 "Takozla kaldırmak olmuyorsa" maddesinin sonu: "Bu düzende hız **≤ 0,1 m/s** (varsayım; ip birden gerilince daha hızlı robot öne devrilebilir)" | ✅ |
| K1: devrilme ipi T9'daki gibi omuz altından bağlı ve elde, ≤ 10 cm boşluk | aynı yer: "devrilme ipi T9'daki gibi omuz altından bağlı ve elde, boşluk ≤ 10 cm" (T9'a bağlantı) | ✅ |
| K1: 1,6 m'lik düşme hattında kimse yok | aynı yer: "1,6 m'lik düşme hattında kimse yok" | ✅ |
| K1: 0,1 m/s'ye inilemiyorsa yalnız "tekerler havada" | aynı yer: "0,1 m/s'ye inilemiyorsa yalnız "tekerler havada" düzeni kullanılır" | ✅ |
| K1, T9 tarafı (kontrol: "D3 tanımı T13'e bağlı") | T9 güvenlik, D3 parantezi: "≤ 0,5 m boşlukla bağlıyken **ve hız ≤ 0,1 m/s iken**, varsayım; T13 D3" (özetin eksik kalmaması için yalnız bu ibare) | ✅ |
| K2.1: devrilme ipi de üst taraftaki ikinci sabit noktaya bağlanır, elde tutulmaz | T13 "komut çalışmazsa" adım 4, "Bu dalda beklerken" alt maddesi 1 | ✅ |
| K2.2: tekerlerin dönmediği, koku/ısınma olmadığı alan dışından izlenir | aynı dal, alt madde 2 | ✅ |
| K2.3: bağlantı en çok 5 dk (varsayım) gelmezse, iki ip sabitken mantara rampaya dik, yandan uzanılır; ayaklar arka kenarın yukarısında, tek kol, gövde aşağıya geçmez; devrilme rampa boyunca, yana değil (`rampa5.yan` 3,16 m/s²) | aynı dal, alt madde 3; atıf `taban-analiz.json` `robot.pozlar[ev].rampa5.yan` 3,16 m/s² (dosyadan okundu: ev pozu `rampa5.yan` = 3.16, `pay_yan` 2,11 en büyük) | ✅ |

**Diff özeti:**
- `T13-rampada-acil-stop.md`: D3 yedek düzen maddesine 3 satır (K1). Adım 4'e "Bu dalda beklerken" + 3 alt madde, 7 satır (K2).
  Bir mevcut cümleye ek ibare: "robot ancak bağlantı yeniden kurulup bara komutla kesildikten sonra **(ya da aşağıdaki 5 dk kuralıyla
  mantara basıldıktan sonra)** indirilir". Gerekçe: K2.3 ile "ancak" sözcüğü çelişmesin.
- `T9-zemin-rampa.md`: D3 parantezine "ve hız ≤ 0,1 m/s iken" (1 ibare).
- `00-genel.md:4` durum satırı: "kontrol GEÇMEZ ... yeniden kontrol bekliyor" → "bağımsız kontrol GEÇER (yeniden kontrol 2; T13 için K1, K2
  kayıt ajanınca eklendi)". `dongu-158.md` P8.4 satırı ⏳ → ✅ (satır "`00-genel.md:3` satırı da güncellenir" diyordu).
- Başka satır değişmedi. Tablo 0'a hız alanı eklenmedi (kontrol istemedi).

Kontrol: `py -3 testler\testler_html.py` (yeniden üretildi), `--kontrol` → md 14 (kâğıt T: 13), HTML bölümü 14, iç bağlantı **87**
(86'dan: K1'deki T9 bağlantısı), id 166, **KONTROL GEÇTİ** (çıkış 0).
