# F4c günlüğü: baskı listesi (P4.3) + baskı partileri (P8.2) — 09.11.2026

Brief: `planlama/d158/F4c-brief.md`. A (tasarım/uygulama) ajanı. FreeCAD kullanılmadı; `tasarim/freecad/` altındaki `.py` kaynaklarına
dokunulmadı; git yazma işlemi yok. F2'nin dosyaları (omuz analizleri, `F2-*`, `karar-kuyrugu.md`) yalnız okundu; F2 C, bu paket
koşarken `ff1c2e9`, `b7c7cb8`, `33d2f76` commit'lerini attı (omuz kaynakları artık HEAD'de).

Kısaltmalar: `TF/` = `tasarim/freecad/`, `Y2b` = `planlama/y2/Y2b-baski.json`.

## 1. Komutlar

| # | Komut | Sonuç |
|---|---|---|
| 1 | `py -3 planlama/y2/Y2b-baski.py` | Çıkış 0. `Y2b` yeniden üretildi: 62 satır, **72 parça**, 7.604,6–7.662,4 g, 158,22–159,42 sa (PETG 6.446,6 g, PETG-CF 1.158,0–1.215,8 g). Önceki (03.11): 65, 7.627,2–7.684,4 g, 158,70–159,88 sa |
| 2 | `py -3 planlama/d158/F4c-partiler.py` | Çıkış 0. `F4c-partiler.json` + `.md`. İç kontrol: Parti 1–4 toplamı = `Y2b` toplamı, her parti = `Y2b` `toplam.parti`, her parça tam bir partide |
| 3 | `py -3 planlama/d158/F4c-liste.py` | `planlama/baski-listesi.md` yazıldı (274 satır). Metin, aşağıdaki YAMA'lı `baski_listesi_guncelle.py`'den (bellekte, geçici kopyada) iki kez geçirildi; iki geçiş aynı (sabit nokta) |
| 4 | `py -3 planlama/d158/F4c-dogrula.py` | Çıkış 0, **SONUÇ: GEÇTİ** (7 kontrol; §5) |

Yeniden üretim sırası: 1 → 2 → 3 → 4. Hepsi FreeCAD'siz, birkaç saniye.

**Kodlama notu (F4c-kontrol B-3):** Windows'ta çıktı yönlendirilince (`>`, `|`; konsol cp1254) `Y2b-baski.py` `print`'teki `☐` karakterinde
`UnicodeEncodeError` ile düşer ve JSON'u yazmadan çıkış 1 verir. Zinciri `PYTHONIOENCODING=utf-8` ile koş (Git Bash:
`export PYTHONIOENCODING=utf-8`; PowerShell: `$env:PYTHONIOENCODING = "utf-8"`). `Y2b-baski.py` değiştirilmedi (sahibi `planlama/y2`;
öneri: betiğin başına `sys.stdout.reconfigure(encoding="utf-8")`). `F4c-dogrula.py` kendi çıktısını UTF-8'e çeviriyor.

## 2. Kaynaklar ve güncellik ("eski analiz" taraması)

Zincir: `TF/<modül>/<modül>-analiz.json` (`baski`) + `TF/omuz/omuz-baski.json` → `planlama/y2/Y2b-baski.py` → `Y2b` →
`TF/lale158/baski_listesi_guncelle.py` → `planlama/baski-listesi.md`. Her modülde analiz dosyasının tarihi, o modülün geometri kaynaklarının
(`*_parcalar.py`, `*_lib.py`, `arayuz.py`) son değişikliğiyle karşılaştırıldı (dosya zamanı + `git log`):

| Modül | Analiz (son koşu) | Geometri kaynağının son değişikliği | Karar |
|---|---|---|---|
| taban | 09.11 03:31 (F2 zinciri; `baski` HEAD ile aynı) | `taban_parcalar.py` / `taban_lib.py` 08.11 20:31 | Güncel |
| kabuk | 09.11 01:18 (P1.5, `409d521`; 357 parça, 34 baskı) | `kabuk_parcalar.py` 08.11 20:34 (F1a P1.7). `kabuk_montaj.py` 02:17 P1.5 `baski_analiz` düzeltmesi; analizde `kesit_kaydirma` alanı var, yani koşu düzeltmeden sonra | Güncel |
| kafa | 05.11 17:01 (`d26c7e7`, QLED + B/R1; `kafa-montaj.FCStd` aynı an) | `kafa10_lib.py`, `kafa_lib.py`, `kafa7_parcalar.py` 08.11 (F1a). `F1a-kontrol.md` P1.3 GEÇER: `SECENEK` varsayılanı eski sabitlerle birebir, model değişmedi | Güncel (geometri aynı). K2 seçilince P6.1'de değişecek |
| dirsek | 09.11 03:29 (F2 zinciri; `baski` HEAD ile aynı) | `dirsek_parcalar.py` 29.10 | Güncel |
| omuz | `omuz-baski.json` 09.11 03:25 (F2; girdi FCStd 03:20:54), `omuz-analiz.json` 07:31 (F2 regresyonu) | `omuz_parcalar.py`, `arayuz.py` 09.11 02:38 | Güncel. 07:31 koşusu aynı kaynaktan (F2-gunluk §regresyon) |

**Sonuç: "eski analiz" satırı yok.** Hiçbir satır P6.1'e "yeniden üretilecek" diye bırakılmadı. Bağımsız çapraz kontrol: ana montaj BOM'u
(`TF/montaj/robot-bom.csv`, `Baski` satırları, F2 zinciri 09.11) 62 kalem / 72 adet, ad ve adet `Y2b` ile birebir (`F4c-dogrula.py` 2).

Not: `planlama/y2/Y2b-baski.json` 03.11'de çalışma kopyasındaki 7" kafa analiziyle üretilmiş: o günkü kafa değerleri (yüz kabuğu sağ
119,4 g, adaptör 62,8 mm) hiçbir commit'teki `kafa-analiz.json`'da yok (`f95f96b`: 93,6 g / 58,3; `bcaa6df`: 90,9 / 58,9). 03.11 → 09.11 kafa
farkı bu yüzden "7" → QLED" farkı.

## 3. P4.3 sonuç: 03.11 → 09.11 farkı

| | 03.11 (`fa49caa`) | 09.11 (F4c) | Fark | Neden |
|---|---|---|---|---|
| Parça | 65 | **72** | +7 | Hoparlör kabı ön halka + arka (2 kap parçası, `d26c7e7` 05.11), hoparlör kelepçesi (F1a P1.7, `76a5701`), 4 QLED ekran tırnağı (`bcaa6df` 04.11) |
| Filament | 7,63–7,68 kg | **7,60–7,66 kg** | −22,6 / −22,0 g | Kafa yüz kabukları −53,6 g (QLED); adaptör −3,6; yeni parçalar +21,4 (kap 10, kelepçe 5, tırnak 6,4); hub takozu +5; çerçeveler +4, VESA −1; omuz göbeği dişi +5,2–5,8 |
| PETG | 6,47 kg | **6,45 kg** | −23,2 g | yukarıdaki PETG parçalar |
| PETG-CF | 1,16–1,21 kg | **1,16–1,22 kg** | +0,6 / +1,2 g | omuz göbeği +5,2–5,8, adaptör −3,6, VESA −1 |
| Süre | 158,7–159,9 sa (listede "159–160") | **158,2–159,4 sa** ("158–159") | −0,48 / −0,46 sa | aynı kalemler |
| Destekli | 13 adet | **14 adet** | +1 | Üst arka servis kapağı (hub takozuyla) |

### Kontrol listesi (brief madde 2)

| Kalem | Adet | Ölçü (mm) | Malzeme | g/adet | sa/adet | Yön | Destek | X2D | Kaynak |
|---|---|---|---|---|---|---|---|---|---|
| Hub takozlu üst arka servis kapağı (F4a/P4.1 hub yeri; takoz `TF/kabuk/kabuk_parcalar.py:798-818`) | 1 | 168,3 × 150 × 12,5 | PETG | 85 | 1,8 | dış yüzü tablada | destekli (analiz) | sığar | `kabuk/baski[13]`, Y2b[17] |
| Hoparlör kabı ön halka | 1 | 45,8 × 45,8 × 7 | PETG | 3 | 0,1 | düz | desteksiz | sığar | `kabuk/baski[31]` |
| Hoparlör kabı arka (flanşlı) | 1 | 62,5 × 62,5 × 13,3 | PETG | 7 | 0,2 | flanş yüzü tablada | desteksiz | sığar | `kabuk/baski[32]` |
| Hoparlör kelepçesi (2 kap parçasına ek, F1a P1.7) | 1 | 56,6 × 56,6 × 14,3 | PETG | 5 | 0,1 | köprü üstü tablada | desteksiz | sığar | `kabuk/baski[33]` |
| Göğüs ekranı çerçevesi sağ / sol | 1 + 1 | 207,2 × 147 × 10 | PETG | 31 | 0,6 | arka yüzü (flanş) tablada | desteksiz | sığar | `kabuk/baski[24]`, `[25]` |
| Göğüs ekranı VESA taşıyıcı | 1 | 106,2 × 100 × 63,4 | **PETG-CF** | 113 | 2,4 | VESA plakası tablada | destekli (28 katman) | sığar | `kabuk/baski[26]` |
| QLED kafa: yüz kabuğu sağ / sol, arka kabuk sağ / sol, iskelet | 5 | 215 × 151/135 × 37/106,9; iskelet 224 × 114,9 × 48 | PETG | 90,9 / 84,4 / 229,4 / 215,4 / 127,5 | 1,89 / 1,76 / 4,78 / 4,49 / 2,66 | ön / arka yüzü tablada; iskelet ters | sağ kabuklar destekli (karar 29.10) | sığar | `kafa/baski[5…9]` |
| QLED ekran tırnağı × 4 | 4 | 24 × 14,4/14,2 × 7,8 | PETG | 1,6 | 0,03 | plaka tablada | desteksiz | sığar | `kafa/baski[10…13]` |
| Omuz göbeği (diş dahil) | 2 | 77 × 51 × 49 (66'dan) | PETG-CF | 63,2–70,4 (destek **5,7 g**; F2 öncesi 5,2) | 1,32–1,47 | +X, x = 150 tablada | destekli | sığar | `omuz-baski/parcalar[2]`, `omuz-analiz.json` `baski[2].olcu` |
| Etek kapakları H1 / H2 | 1 + 1 | 111,3 × 111,3 × 3 / 70 × 56 × 3 | PETG | 24 / 14 | 0,5 / 0,3 | düz | desteksiz | sığar | `kabuk/baski[22]`, `[23]` |

**VESA taşıyıcı malzemesi:** PETG-CF. Kaynak model: `TF/kabuk/kabuk_parcalar.py:375-376` (`malzeme="PETG-CF", kod="PETG-CF baski"`);
`Y2b-baski.py:11-12` CF kümesi; `TF/kabuk/kabuk_rapor.py:281`. Brief "F1b kararı" diyor; F1b günlüğünde ve karar kuyruğunda VESA malzemesi için
ayrı bir karar kaydı bulunamadı. Tutarsızlık daha önce `P0.1-siniflandirma.md:95`, `F0-gunluk.md:61` ve `TF/lale158/qled-cerceve-tasarim-notu.md:140`'ta
yazılmıştı (eski listenin Renk tablosu beyaz PETG diyordu). Listede malzeme sütunu ve Renk/Malzeme tabloları modele göre düzeltildi
(PETG-CF 12 tür, 18 adet).

**X2D:** 72 parçanın hepsi analizdeki `sigar` = true ve baskı yönündeki ölçü ≤ 246 × 246 × 250 (en büyük 235, göğüs bandı yüksekliği;
etek 233,7 genişlik).

## 4. P8.2 sonuç: partiler

Ayrıntı `planlama/d158/F4c-partiler.md`. Parti numaraları `Y2b-baski.py` `parti()` ile aynı (Özet tutarlı kalsın diye); akü takozu
Parti 4'te sayılır, Parti 1 arasında basılır (`proje-plani.md` kritik yol 4–5).

| Parti | Adet | PETG kg | PETG-CF kg | Toplam kg | Süre sa |
|---|---|---|---|---|---|
| 0 (kupon, toplama katılmaz) | 8 baskı (6 kupon) | 0,08–0,12 | 0,18–0,30 | 0,26–0,42 | 7,3–12,0 (D2'siz 6,2–9,5) |
| 1 | 27 | 3,16 | 0,14–0,15 | 3,31 | 68,9–69,0 |
| 2 | 25 | 0,32 | 1,01–1,07 | 1,33–1,38 | 27,7–28,8 |
| 3 | 9 | 0,75 | 0 | 0,75 | 15,7 |
| 4 | 11 | 2,21 | 0 | 2,21 | 45,9 |
| **1–4** | **72** | **6,45** | **1,16–1,22** | **7,60–7,66** | **158,2–159,4** |

03.11'e göre partiler: Parti 1 24 → 27 (hoparlör 3 parça; +23 g, +0,5 sa), Parti 2 aynı adet (göbek +1,6–2,2 g), Parti 3 5 → 9
(tırnaklar; QLED kabuklarla −47 g, −1,0 sa), Parti 4 aynı.

**Parti 0:** A (6808 Ø52), B (625ZZ, Ø40 mil, M3/M5 dikey; PETG-CF + PETG), C (ısıl gömme L + 1; PETG-CF + PETG), D1, D2 (dirsek kelepçesi,
PETG-CF; D2 koşullu), E (tüp halkası, PETG). Kütleler: A ve B'nin %100'ü STL hacminden (26,0 / 87,9 g); B'nin alt değeri 60 g eski listeden
(kaynağı yazılmamış); C–E `TF/test/m7-kupon-sonuc.json`. Süre `TF/test/README.md` yöntemi (g / 1,27 ÷ 10 mm³/s × 1,3).
`proje-plani.md:40, 72`'deki "≈ 3 sa" yalnız M7 kuponları (C bir kez + D1 + D2 + E, `m7-kupon-sonuc.json` `toplam.sure_tahmini_dk` 178);
A, B ve iki malzemeli B/C ile ≈ 7,3 sa (tahmini kütle). K31'e göre kupon etkisi `F4c-partiler.md` tablosunda: A ve C seçeneklerinde
kupon değişmez, B seçeneğinde B/C kuponları yeniden üretilmeli (FreeCAD), M5 Rhino ürünü kupon deliklerine uymuyor.
**Omuz dişi kökü:** kupon yok; K39'un varsayılanı (kök yarıçapı P6.1'de) uygulanmadan göbek basılmamalı. Öneri: P6.1'den sonra göbeğin
kendisi Parti 2'nin ilk işi; S2 5°'te sentille 0,3 mm boşluk kontrolü (`F2-gunluk.md` madde 9) ve DS3235 düşme ölçümü (K39).

## 5. Kabul ölçütleri

| Ölçüt | Sonuç | Kaynak |
|---|---|---|
| P4.3: `baski_listesi_guncelle.py` (ve `Y2b-baski.py`) çıktısı ile `baski-listesi.md` aynı | **Geçti, koşullu:** `Y2b-baski.py` çıktısı depodaki `Y2b` ile birebir (kontrol 1). Betiğin **yamasız** hâli bütün parça satırlarını aynen bırakıyor (kontrol 5a: parça satırlarında fark 0); 19 metin satırı farklı: betik başlığa "03.11", üst bölüme "kafada 7\" ekran", Parti 3 etiketine "7\" yüz ekranı" yazıyor ve "69–69 sa" biçiminde aralık basıyor. Önerilen yamayla (§6) çıktı listeyle satır satır aynı (kontrol 5b, sabit nokta) | `F4c-dogrula.py` 1, 5a, 5b |
| P4.3: her satır bir JSON anahtarına bağlı | **Geçti:** 62 satırın her biri tek `Y2b` satırına ve analiz anahtarına (`<modül>/baski[i]` ya da `omuz-baski/parcalar[i]`) bağlı; adet, ölçü, g, sa, malzeme, destek, yön, X2D, parti JSON ile aynı; her `Y2b` satırı bir kez | `F4c-dogrula.py` 3 |
| P4.3: "eski analiz" satırları gerekçeli | **Geçti (satır yok):** §2 tablosu, her modül için tarih karşılaştırması | §2 |
| P8.2: partilerin toplamı baskı listesine eşit (adet, kg, sa; betikle) | **Geçti:** 72 adet, 7.604,6–7.662,4 g, 158,22–159,42 sa, PETG 6.446,6 g, PETG-CF 1.158,0–1.215,8 g; Özet tablosu `Y2b` `toplam.parti` ile aynı | `F4c-dogrula.py` 4a, 4b; `F4c-partiler.json` `kontrol` |
| P8.2: her parçanın bir partisi var | **Geçti** | `F4c-dogrula.py` 4b |

## 6. `baski_listesi_guncelle.py` sorunları ve önerilen yama (değiştirilmedi)

Betik 03.11 öncesine göre yazılmış. Bulunanlar:
1. **10,1" → 7" çevirileri ters yönde yanlış:** satır 38 (`r` değişimleri), 58 (`_ADI[3]`), 74–75 (Parti 3 başlığı). QLED modelinde "10,1\"" doğru.
2. **Üst bölüm metni sabit ve eski:** satır 47–51 ("03.11", "kafada 7\" ekran", "giriş ve renk metinleri 1,65 m tarihli", değişen baskılar listesi);
   satır 73 başlık tarihi "03.11.2026".
3. **İdempotent değil:** satır 13 `kat()` betiğin kendi yazdığı "(gömülü 11,6\" cep)" ekini atmıyor; ikinci koşuda göğüs bantları eşleşmez,
   "satırı olmayan parça" tablosuna mükerrer düşer. (Yeni listede ad sütunu ek taşımıyor; sorun bu yüzden şimdilik tetiklenmiyor.)
4. **`_ar` aralığı:** yuvarlanmış iki uç aynıyken "3,31–3,31 kg", "≈ 69–69 sa" yazıyor (satır 61–62).
5. **Kapsam:** yalnız kabuk ve kafa satırlarını güncelliyor; taban, dirsek ve omuz satırları (omuz göbeği dahil) betikle değişmiyor.
   Bu paket bu satırları `F4c-liste.py` ile yazdı ve `F4c-dogrula.py` 3 hepsini JSON'la karşılaştırıyor. Öneri (P6.1): betik bütün modülleri
   ve aralıkları (`Y2b-baski.py` `aralik`) yazsın ya da `F4c-liste.py` onun yerine geçsin.
6. Herhangi bir satırı "| **Toplam** |" ile başlayan her tabloyu Özet toplamıyla eziyor (satır 70); başka tabloda bu başlık kullanılmamalı
   (listedeki fark tablosu "Fark toplamı" diye adlandırıldı).

Yama (`F4c-dogrula.py` `YAMA`, 11 metin değişikliği; her eski metin kaynakta tam bir kez): Y1 `kat()` ek atma, Y2 satır 38 → `r = m.group(7)`,
Y3 üst bölüm (tarih 09.11, QLED, satırı olmayan parça yoksa "yok."), Y4 `_ADI[3]` → `10,1" QLED yüz ekranı gelip ölçülünce`, Y5 `_ar` iki uç
biçimlenmiş hâliyle karşılaştırılır, Y6 başlık tarihi 09.11, Y7 Parti 3 başlığı değiştirilmez. Sahibi `tasarim/freecad/` (tarama kaynak
listesinde değil ama kural gereği F4c değiştirmedi); P6.1'de ya da döngü yöneticisinin onayıyla uygulanmalı.

`Y2b-baski.py` için öneri (değiştirilmedi): `parti()` satın alınan parçaya bağlı 7 satırı Parti 1'e koyuyor ("hemen"): hub takozlu üst
arka kapak (USB hub 72 × 25 × 19), hoparlör kabı ön/arka ve kelepçesi (8 Ω hoparlör: K36 stok 1 < 3, K6 yön; kap ölçüsü analizde
"VARSAYIM"), göğüs ekranı çerçevesi sağ/sol (11,6" kasa 284,65 × 182,25) ve VESA taşıyıcı (VESA deliklerinin kasadaki yeri ve derinliği
doğrulanmadı, `TF/arayuz.py:342`; F4c-kontrol B-2). Düzeltme turu 1'de bu 7 satır (7 adet, 275 g, PETG-CF 113 g, ≈ 5,8 sa) Parti 1'de
kaldı ama sona alındı ve "Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır" notu aldı (`F4c-partiler.py` `SONA`; `F4c-partiler.md`
Parti 1 bölümü ve tablonun son 7 satırı; `baski-listesi.md` "Sıralama mantığı" madde 2 ve Parti 1 tablosu). Parti numarası ve toplamlar
değişmedi. İstenirse `parti()`'de bu satırlar Parti 2'ye ("parça gelip ölçülünce") alınabilir; ekran S siparişinde (`maliyet.json`
`kalemler[145]`), Parti 1 S−0,5'te başlıyor.

## 7. Karar taslakları (karar kuyruğuna yazılmadı; döngü yöneticisi taşır)

### KT-F4c-1 · PETG-CF miktarı: 1,5 kg yetmiyor
- **Soru:** PETG-CF 3 × 0,5 kg (1,5 kg; `planlama/maliyet.json` `kalemler[109]`, v3) yetiyor mu?
- **Sayılar:** parçalar 1.158,0–1.215,8 g (`Y2b` `toplam.cf_g`; 12 tür, 18 adet; VESA taşıyıcı 113 g dahil, maliyet notundaki "1,04–1,10 kg,
  17 adet" VESA'sız). Kuponlar 175,8–301,4 g. Toplam 1.333,8–1.517,2 g. 1,5 kg'de pay **+166 g … −17 g**; D2 basılmazsa +69 … +208 g.
  En büyük CF parçası 151,5 g (kafa servo yuvası): tek başarısız baskı alt durumdaki payı bitiriyor. VESA taşıyıcının destek malzemesi
  (28 katman) kabuk analizinde sayılmıyor.
- **Seçenekler:** a) +1 makara (4 × 0,5 = 2,0 kg; pay 483–666 g). b) 1,5 kg'de kal; D2 basılmaz, kuponlar tahmini dolulukla; başarısızlıkta
  yeniden sipariş. c) K34 (baskı hizmeti) netleşince karar ver.
- **Sayısal etki:** a: +1.114,03 TL (`maliyet.json` `kalemler[109]` birim fiyatı, 11 Ekim; satıcı ve stok o satırdaki gibi, yeniden
  doğrulanmadı), %15 payla +1.281,13 TL. b: 0 TL; risk: bir CF parçanın yeniden basımı + sipariş gecikmesi.
- **Önerilen varsayılan:** a. Yalnız öneri.
- **Bloke:** S siparişindeki filament satırı; K34 ile birlikte düşünülmeli. `baski-listesi.md` eski notu "filamenti firma + ekip karşılar,
  satın alınmaz" diyordu; `maliyet.json` ise filamenti V3 toplamında sayıyor (`secenek "yazici"`). Bu çelişki de netleşmeli.

### KT-F4c-2 · Isıl gömme somun adedi (K29 / K31'e bilgi)
- **Sayılar:** BOM (`TF/montaj/robot-bom.csv`, 09.11) **M3 159, M5 5** (dirsek, kabuk, kafa, omuz, taban). Kuponlar: B (M3 4, M5 3) ve C
  (M3 5, M5 5) her malzemede bir kez → M3 18, M5 16 (`TF/test/tolerans_kuponu.py:8-9`, `m7-kupon-sonuc.json` `kupon_c_delikler`).
  M5'lerin yeri: ön kol gövdesi × 2 (**PETG**; `TF/dirsek/dirsek_parcalar.py:235` `insert_hole(5, …)`, `:242` "On kol govdesi" PETG;
  M6 adım 44), eğme çatalı × 1 (PETG-CF), omuz göbeği × 2 (PETG-CF). M5 iki malzemede de kullanıldığı için M5 kuponu da iki malzemede
  gerekli. Gereken (pay hariç): **M3 159 + 18 = 177, M5 5 + 16 = 21** (yalnız C kuponu PETG'de M5'le basılırsa 18).
  (İlk sürümde "M5 yalnız PETG-CF parçalarda, M5 13" yazıyordu; yanlış, F4c-kontrol B-1 ile düzeltildi.)
- Plan: M3 168 (`maliyet.json`) / 176 (v4), M5 6. **M3 168 kupona yetmiyor (−9); M5 6, BOM + kupona yetmiyor (−15).**
- **Sayısal etki (taban fiyat, `F8a-siparis.md` §4.1):** M3 168 → 177: +9 × 5,29 = +47,61 TL; M5 6 → 21: +15 × 6,35 = **+95,25 TL** (18 ile +12 × 6,35 = +76,20 TL). İkisi birlikte +142,86 TL.
- **Önerilen varsayılan:** erken alımda M3 177 + pay, M5 21 + pay (pay oranı Ahmet'in; plan şimdiye kadar ≈ %5 pay kullanmış). Yalnız öneri.
  K31'in M3 varyantı (A/B/C) adedi değiştirmez; K31 M5 ürünü seçilmeden M5 alınmamalı (Rhino M5 Ø6,7–6,8 ↔ kupon Ø6,2–6,6).

## 8. Takvim kontrolü (öneri; `proje-plani.md` değiştirilmedi)

Tek yazıcı, partiler sırayla, Parti 2 en erken S+1, akü takozu Parti 1 arasında; üst süreyle (`F4c-partiler.json` `takvim_hafta_sonu`):

| Parti | 40 sa/hf | 32 sa/hf | Plan (Durum A) |
|---|---|---|---|
| 1 | S+1,26 | S+1,70 | S+1,5 |
| 2 | S+1,98 | S+2,60 | S+2,3 |
| 3 | S+2,38 | S+3,09 | S+2,8 |
| 4 | S+3,49 | S+4,48 | S+4–4,5 |

- 40 sa/hf'de çizelge tutuyor. 32 sa/hf'de ara bitişler 1–2 gün kayıyor, son (≈ S+4,5) aynı; aşama 8'in ilk adımları (S+3) Parti 2'yi
  beklemiyor, kafa adımları (29–31) Parti 3'ün bitişine (S+3,09) denk geliyor. Plan Parti 1'i ≈ 34,5 sa/hf ile hesaplamış.
- `proje-plani.md` için önerilen metin güncellemeleri (sahibi döngü yöneticisi / P9.x): satır 40 ve 72 "Parti 0 ≈ 3 sa" → "≈ 7 sa (A, B ve
  iki malzemeli B/C ile; D2'siz ≈ 6)"; S = 16.11 örneğinde 9–10.11'e 7 sa, paylaşımlı yazıcıda iki günün neredeyse tamamı. Satır 47, 78, 224
  "65 parça, 7,63–7,68 kg, 159–160 sa" → "72 parça, 7,60–7,66 kg, 158–159 sa"; satır 63 "Parti 3 (≈ 17 sa)" → "≈ 16 sa".
- Sayıdan büyük risk bağımlılıklar: Parti 1 STL dışa aktarmaya (FreeCAD, açık iş) ve Parti 0 sonucuna; Parti 2'nin göbeği K39 / P6.1'e
  (P6.1 S+1,5'ten önce bitmeli, S = 16.11 için ≈ 25.11); Parti 3 QLED'e (K32: hocadan mı satın alma mı; Robotistan stok 2) ve K2'ye (P6.1);
  Parti 4 etek havalandırma yarıklarının (E7, `planlama/adim3/elektrik.md:499`) CAD'e girmesine; akü takozu aküye (K30).

## 9. Açıklar

1. **Üst arka servis kapağı desteği:** `kabuk/baski[13]` `destek_sorun` z 2,5'te alan 19.667,7 mm², boy 156,1 (03.11'de 3 mm düz kapak:
   0 sorun). Takoz 3 mm plakanın iç yüzüne 1 mm gömülü prizma (`kabuk_parcalar.py:808-816`); dış yüz tablada basılınca destek gerekmemeli.
   Alan neredeyse bütün plaka kadar, analiz yöntemi kaynaklı olabilir. FreeCAD gerektiği için incelenmedi: dilimleyicide bakılmalı, P6.1'de
   kesitle doğrulanmalı. Listede analizdeki gibi "destekli".
2. Kabuk ve kafa analizinin `filament_g`'si destek malzemesini saymıyor (omuzda sayılıyor). Destekli 6 kabuk/kafa parçasının destek gramı
   bilinmiyor; PETG payı (%38) karşılar, PETG-CF'de VESA taşıyıcı KT-F4c-1'e eklenmeli.
3. M6 montaj tablosu 125 cm'den: göğüs ekranı, QLED, uzatma bantları, hoparlör, hub ve boyun adaptörü adımları yok (`proje-plani.md` "M6
   dayanağı notu"). Parti tablosunda bu parçaların adımı "M6'da yok" diye yazıldı.
4. Listede kabuk/kafa ölçüleri betik biçimiyle tam sayıya yuvarlanıyor (üst arka kapak 12,5 → "12"); kesin değer JSON'da.
5. Eski sayıları taşıyan başka belgeler (bu paketin dosyası değil): `README.md:16, 49`, `TF/OZET.md:23`, `Lale-Proje-Ozeti.txt:56`
   (65 parça, 7,63–7,68 kg, 159–160 sa; "`baski-listesi.md:12`" satır atfı artık geçersiz), `proje-plani.md` (§8), `maliyet.json`
   `kalemler[109]` notu (CF 17 adet, 1,04–1,10 kg) ve `[112]` (baskı hizmeti 7,7 kg; yeni 7,60–7,66, fark küçük).
6. `TF/kabuk/kabuk_parcalar.py:733` yorumu (72 → 70) hâlâ P6.1'de (F1a/F1b'den).
7. `dongu-158.md` P4.3 / P8.2 durum satırları döngü yöneticisinin; değiştirilmedi.

## 10. Değişen ve yeni dosyalar

- Değişti: `planlama/baski-listesi.md` (yeniden yazıldı, `F4c-liste.py`), `planlama/y2/Y2b-baski.json` (yalnız `Y2b-baski.py` ile).
- Yeni: `planlama/d158/F4c-gunluk.md` (bu dosya), `F4c-partiler.md`, `F4c-partiler.json`, `F4c-partiler.py`, `F4c-liste.py`, `F4c-dogrula.py`.

## 11. Düzeltme turu 1 (F4c-kontrol: KOŞULLU GEÇER)

| Bulgu | Yapılan | Dosya |
|---|---|---|
| B-1 (orta): M5 adedi 13 değil 21 | KT-F4c-2 düzeltildi: ön kol gövdesi PETG ve 2 × M5 alıyor (`dirsek_parcalar.py:235`, M6 adım 44), M5 kuponu iki malzemede; M5 21, +15 × 6,35 = +95,25 TL (B'nin hesabı doğrulandı). Liste ve parti dosyalarında insert adedi geçmiyor | `F4c-gunluk.md` §7 |
| B-2 (orta): göğüs ekranı çerçeveleri ve VESA taşıyıcı ekrana bağlı | Hub ve hoparlör parçalarıyla aynı "Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır" grubuna alındı; tablolarda sona sıralandı, grup toplamı yazıldı | `F4c-partiler.py/.md/.json`, `F4c-liste.py`, `baski-listesi.md` |
| B-3 (düşük): `Y2b-baski.py` yönlendirilmiş stdout'ta düşüyor | Günlüğe `PYTHONIOENCODING=utf-8` notu (§1); betik değiştirilmedi | `F4c-gunluk.md` §1 |

Zincir `PYTHONIOENCODING=utf-8` ile yeniden koşuldu: `Y2b-baski.py` 0, `F4c-partiler.py` 0, `F4c-liste.py` 0 (275 satır), `F4c-dogrula.py` 0
(7/7 GEÇTİ). `Y2b-baski.json` aynı kaldı; toplamlar değişmedi. B-4…B-8'e dokunulmadı (döngü yöneticisinin talimatı).
- Dokunulmadı: `tasarim/freecad/**` (yalnız okundu), `proje-plani.md`, `maliyet.json`, `karar-kuyrugu.md`, `dongu-158.md`, F2 dosyaları.
