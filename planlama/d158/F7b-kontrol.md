# F7b kontrolü (P7.2, yazdırılabilir rehber + kafa / QLED / ses / hub adımları): bağımsız kontrol ajanı B, 09.11.2026

**Genel karar: DÜZELTME TURU GEREKİYOR (kısa, yalnız metin: `rehber_metin.py` 4–6 satır + yeniden üretim).**

Ölçülebilir kabul ölçütlerinin yedisi de B'nin kendi koşularında sağlandı:
- `kontrol.json` 50/50, konsol hatası 0;
- parça 1192 ↔ 1192, her parça tek adımda;
- PDF 50 sayfa, taşan sayfa 0;
- ASCII kalıntı 0, gruplama yanlışı 0;
- 360 px taşma 0;
- `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0.

Metin kaynaklarla satır satır karşılaştırıldı. A'nın yazdığı iddiaların hepsi kaynakta var; uydurma bulunmadı. 05.11 ESP32 USB yolu kaynakla birebir aynı.

Ama elektrik güvenliği açısından kaynakta olup rehbere girmemiş üç talimat var:
- **O-1.** Göğüs ekranının 12 V regülatörü, ekrana bağlanmadan önce 12 V'a ayarlanmalı.
- **O-2.** ESP32 USB'deki 1N5819'un yönü yazmıyor.
- **O-3.** Pi 5 V hattındaki ikinci P6KE6V8A rehberde yok.

Üçü de kaynak metinden kopyalanacak birer cümle. Eksik kalırlarsa donanım zarar görebilir; rehber herkese açık.

Kritik 0, orta 3, düşük 9.

Kısaltmalar:
- `TF/` = `tasarim/freecad/`.
- `RM` = `TF/rehber/rehber_metin.py`.
- `SPB/` = B'nin scratchpad klasörü (`f7b-b`, depo dışı).

B'nin depoya yazdığı tek dosya bu dosya. B FreeCAD koşmadı ve kilide yazmadı; kilit baştan sona "boş" kaldı. Git'e yazmadı.

Depo durumu koşulardan önce ve sonra karşılaştırıldı (`git status --porcelain` + değişen / izlenmeyen 473 dosyanın sha1'i). F7b dosyalarının hepsi aynı kaldı. Arada değişen iki dosya paralel işlerin:
- `planlama/d158/F9b-gunluk.md` (yeni, F9b);
- `planlama/dongu-158.md` (orkestratör).

## Madde tablosu

| # | Madde | Sonuç | Kanıt |
|---|---|---|---|
| 1 | Metin doğruluğu | **KOŞULLU** (O-1, O-2, O-3; D-2, D-7) | §1 |
| 2 | Denetim betiği | **GEÇER** (gerçekten denetliyor; gevşek noktalar D-1) | §2 |
| 3 | Üretim ve tarayıcı | **GEÇER** (D-4: `--cikti` tam yalıtım sağlamıyor) | §3 |
| 4 | PDF | **GEÇER** (okunabilirlik önerisi D-3) | §4 |
| 5 | Telefon 360 px | **GEÇER** | §5 |
| 6 | Diff'ler, tarama kaynakları | **GEÇER** | §6 |
| 7 | Commit listesi, yayın güvenliği | **KOŞULLU** (brief ve kontrol listede yok; yerel yol önerisi D-5) | §7 |

## §1 Metin doğruluğu (E3a, E4, K2, F2, F5)

**Yöntem.** `git diff RM` satır satır okundu. Her iddia kaynakta arandı:
- `planlama/adim3/elektrik.md`;
- `TF/kafa/kafa10_lib.py`, `TF/kabuk/kabuk_parcalar.py`, `TF/arayuz.py` `SES_USB`;
- `TF/lale158/kablo_yolu_ekran.py`, `TF/lale158/kafa-yerlesim/uygulama-notu.md`;
- `karar-kuyrugu.md` (K1, K5, K6, K10, K11, K14, K16, K17).

Sayılar `rehber-veri.json`'daki adım parça / bağlantı listeleriyle karşılaştırıldı.

**Kaynakla tutan iddialar (seçme):**

| Konu | Rehber | Kaynak | Sonuç |
|---|---|---|---|
| QLED 10,1" | vida deliği yok; cam ön duvar iç yüzüne; 4 tırnak üst / alt x ±85; M3×6 ISO 7380 + ısıl gömme; 1 mm köpük | `kafa10_lib.py:2, 341-366`; `elektrik.md:24` | aynı |
| Kamera | Camera Module 3, yüz kabuğu boss'ları 4 × M2×8 PT, lens Ø9 delik ekranın üstünde | `kafa10_lib.py:53, 119` (r 4,5), `:388-393` | aynı |
| ReSpeaker | sağ arka kabuk tavanı, 3 × M2×8 PT (vida tipi varsayım) | `kafa10_lib.py:250, 435-440`; `uygulama-notu.md:139` | aynı, varsayım işaretli |
| Ses kartı, PAM8403 | sol (−X) arka kabuk yan duvarı, köpük bant + kablo bağı, ölçü tahmini | `kafa10_lib.py:421-432`; `elektrik.md:28` | aynı |
| USB portları | Pi 1 ReSpeaker, 2 ses kartı, 3 hub, 4 QLED Touch; Hub 1 göğüs Touch, Hub 2 ESP32, 3–4 boş | `elektrik.md:76-84`; `uygulama-notu.md:125-132` | aynı |
| Kafa içi kablolar | HDMI 30 cm şerit micro HDMI 0; Power SY8205, A ucu kesik; Touch Pi USB 4 | `elektrik.md:57`; `uygulama-notu.md:118-120`; `kafa10_lib.py:397` | aynı |
| Hoparlör | 40 × 20, 4 Ω, 3 W; orta bant sağ ön duvarı; kap ön halka + flanşlı arka; kelepçe 2 × M3×20 + köpük ped | `elektrik.md:28`; `kabuk_parcalar.py:730-795, 905-911` | aynı |
| Hub | üst arka kapak takozu, 2 yan dayama, 1 mm köpük; anahtar açık | `kabuk_parcalar.py:798-816, 912-914`; `elektrik.md:36` | aynı |
| Boyun demeti | 5 kablo: 12 V, tilt, göğüs HDMI, hub uzatması, hoparlör; yuva kanalı %44,8 | `elektrik.md:37`; K14 | aynı, K14 "doğrulanmadı" |
| **K2 madde 4, ESP32 USB** | boyuna girmez; ESP32 (taban) → direk arka yüzü z −26 → üst arka kapak hizası (y 1.085–1.157) → hub | `kablo_yolu_ekran.py:6, 22, 110`: `(47,5; hub)` → `(14; 1060; −26)` → `(14; 300; −26)` → … → `(51,6; 190; −120)`. Direk z ±20 (`arayuz.py:245`): z −26 arka yüzün 6 mm gerisi. Hub y 1.085–1.157 (`uygulama-notu.md:58`). 05.11 B kararı: `karar-kuyrugu.md:191` (K5), K17; `elektrik.md:37, 64` | **birebir aynı** |
| Göğüs 12 V yolu | tabandan → direk arka yüzü → travers altında direk soluna → ekran | `kablo_yolu_ekran.py:116` (z −28, `Y_KOSE − 15`, x −46) | aynı |
| Önerilen boylar | HDMI 950, hub uzatması 920, ESP32 1.360, hoparlör 1.030, göğüs 12 V 1.720 | `uygulama-notu.md:106-114` | aynı |
| İki 5 V köprülenmez, Touch VBUS | E3a not + E4 not (multimetre, takmadan, bağlıysa takma) | `elektrik.md:56`; `planlama/d158/testler/T2-qled-vbus.md` | aynı, açıkça duruyor |

**Sayımlar (veri ↔ metin):**
- E3a: burç 4 + M2,5×5 4 + M2,5×8 4 + horn M3×5 1; TVS 1; köpük 3.
- E4: M3×6 11 (4 tırnak + 7 dikiş), M3×5 2, ısıl gömme 17 (4 tırnak + 9 dikiş + 4 raf), M3×10 4, M2×8 PT 7 (4 kamera + 3 ReSpeaker), köpük 6.
- F2: M3×20 2 + ısıl gömme 2, köpük ped 1.
- F5: M3×6 22 + ısıl gömme 22 (arka 7 + üst arka 7 + H1 4 + H2 4).

Hepsi metinle aynı.

**Eski ifade taraması.** Tüm veride "7 inç", "LCD", "MAX98357A", "Nextion", "kafa USB", "vizör" geçişleri tek tek okundu. Kalanlar yalnız bağlam içinde:
- E3a: "M6'daki LCD … bu adımda yok";
- F3: "Nextion kalktı";
- K2 ve şema 12: "05.11 öncesi ESP32 → kafa USB";
- göğüs ekranı ürün kodu ("11.6inch HDMI LCD").

"Doğrulanmadı" işaretleri yerinde: E4 sırası, K14, K11, K10, K6, hoparlör kablo ucu, hub söküm payı ve giriş gerilimi, QLED kütle / akım, horn sırası. Eksik olanlar: D-7.

### O-1 (orta). Göğüs ekranı 12 V regülatörünü ayarlama talimatı rehberde yok; F3 ekranın 12 V fişini taktırıyor
- **Kaynak.** `elektrik.md:67`: "Regülatörü ekrana bağlamadan multimetreyle 12 V'a ayarla (akü 12,8–14,4 V)". LM2577 + LM2596 ayarlı bir kart; çıkışı fabrikadan 12 V gelmeyebilir.
- **Rehber.** `RM:366` (K2 madde 7) dalı anlatıyor, `RM:433` (F3 madde 3) "K2'de bırakılan HDMI ve 12 V uçlarını tak" diyor. Tüm veride (50 adım) "LM2577 / LM2596 / 12 V'a ayar" araması yalnız K2 madde 7'yi ve F3'ün K11 notunu buldu: ayarlama ve ölçme talimatı yok.
- Kartın ve mini 2 A sigortanın nereye takılacağı da yazmıyor; ikisi de modelde yok (`elektrik.md:16-17`).
- **Risk.** Ayarsız kart, ekranın 12 V girişine 12 V'tan yüksek gerilim verebilir.

### O-2 (orta). 1N5819'un yönü ve neden konduğu yazmıyor
- **Kaynak.** `elektrik.md:283`: "VBUS teline seri 1N5819 (anot Pi tarafında) … Diyot sayesinde çevre 5 V Pi'ye geri beslemez". Aynı satır: kartın kendi VBUS→VIN diyodu doğrulanırsa gerekmez, montajda multimetreyle bakılacak.
- **Rehber.** `RM:359` (K2 madde 4) ve şema adı yalnız "VBUS'ta 1N5819" diyor. Tüm veride "anot / katot" 0.
- **Risk.** Diyot ters takılırsa çevre 5 V (XL4016) hub üzerinden Pi'nin 5 V'una geri besler; bu da "iki 5 V köprülenmez" kuralının bir başka biçimi.
- 05.11'den sonra yol Pi → hub → ESP32. Doğru ifade: "anot hub (Pi) tarafında, katot ESP32 tarafında".

### O-3 (orta). Pi 5 V hattındaki ikinci P6KE6V8A rehberde yok
- **Kaynak.** `elektrik.md:47` ve `:282`: "her iki 5 V çıkışına P6KE6V8A". Biri D24V50F5 → Pi, biri SY8205 → QLED.
- **Model / BOM.** Yalnız 1 adet var: `robot-bom.csv:144` "kafa ekranı 5 V". Bu açık `F4a-gunluk.md:188`'de de yazıyor.
- **Rehber.** `RM:286` yalnız "P6KE6V8A TVS (kafa ekranı 5 V)" diyor. P6KE18A için "modelde yok" notu var (`RM:298`), ikinci P6KE6V8A için yok. TVS'in kutup yönü (tek yönlü: katot +5 V'a) da yazmıyor.

### D-2 (düşük). Enerji durumu belirsiz: E3a ölçümü, K2 bağlantıları
- `RM:295` E3a kontrolü "SY8205 çıkışı yük bağlanmadan ölçüldü: 5 V" diyor. Ama E3a tezgâh adımı ve 12 V kafaya K2'de geliyor. Ölçüm için akım sınırlı bir tezgâh kaynağı gerekir; bu yazmıyor. Ölçüm yerinde bir güvenlik adımı, yalnız yeri ve kaynağı belirsiz.
- K2 (`RM:355`) kafa 12 V'unu bağlatıyor ama "akü ayrık / F3 takılı değil" demiyor.
- F7a'dan kalan çelişki: K1 `is_` "Akü ayrık kalır" (`RM:169`) diyor, aynı adımın kontrolleri (`RM:181`, `:188`) enerjili ölçüm istiyor ("çıkış ölçülerek", "ilk açılışta").
- Rehberde sigortaların ve aküyü ilk kez takma sırasını veren bir adım yok. B5a "Sigortaları henüz takma" diyor, F5 "devreye alma testi" diyor; arası boş.

### D-7 (düşük). Küçük metin eksikleri
- F2: hoparlör kabı, kulakları ve kelepçesi varsayım (`kabuk_parcalar.py:730`: "Kap, kulak ve izgara VARSAYIM: urun elde gorulmeden kesinlesmez"; `uygulama-notu.md:141`). F2 notu (`RM:424`) yalnız kablo ucunu "varsayım" diyor.
- E4 kontrolü (`RM:333`) "tırnak cıvatası cama bastırıyor" diyor. Cama basan tırnak; cıvata tırnağı boss'a tutuyor (`kafa10_lib.py:341`).
- Öneri (zorunlu değil): E4, F5 ve E3a notları ilgili test kâğıtlarını anabilir: `planlama/d158/testler/T2-qled-vbus.md` (yöntemi E4 notuyla tutarlı), T3 (kafa 5 V akımı), T4 (PAM8403), T5 (hub girişi).

## §2 Denetim betiği (`TF/rehber/rehber_denetim.py`)

Okundu. Üç denetimin üçü de gerçek veri üzerinde çalışıyor; boş liste yüzünden geçiş yok:
- 4.626 metin;
- 1192 parça;
- 14 anma satırı (11 bileşen, hepsinin anahtarı veride bir parçayla eşleşiyor).

**Enjeksiyon** (yalnız `SPB/denetim/` kopyasında; `SPB/enjekte.py`, `enjekte2.py`; depo değişmedi):

| # | Enjekte edilen hata | Betik |
|---|---|---|
| 0 | (temiz kopya) | geçti (doğru) |
| 1 | parça satırı "Yuz kabugu" | **yakaladı** (ASCII 2 + gruplama 1) |
| 1b | kontrol satırına "kopuk" | **yakaladı** |
| 1c | sözlükte olmayan "kapagin" | **yakaladı** |
| 2 | yüz + arka kabuk tek satırda | **yakaladı** |
| 2b | satırdan bir parça düşmüş | **yakaladı** |
| 2c | bağlantı satırına farklı kodlu parça | **yakaladı** |
| 2d | bağlantı satırı (M3×20) tümden düşmüş | **kaçırdı** |
| 3 | K2'ye "ESP32 USB direk ön yüzünden boyuna çıkar." | **kaçırdı** ("çıkar" bağlam kelimesi) |
| 3b | aynı, "gider" | **yakaladı** |
| 4 | E4'e '7" ekran' | **yakaladı** |
| 4c | "Kafa LCD vidası 11,6 mm" | **kaçırdı** ("11,6" muafiyeti) |
| 4d | '7" ekran yok' | **kaçırdı** ("yok" bağlam kelimesi) |
| 5 | E4 metninden PAM8403 silindi | **yakaladı** (anma) |
| 7 | F5'te "Hub 2 → göğüs dokunmatiği" (yanlış port) | kaçırdı (betiğin kapsamında değil) |
| 8 | E4'ten Touch VBUS uyarısı silindi | kaçırdı (betiğin kapsamında değil) |

Bugünkü veride bağlam kelimesiyle "affedilen" 6 cümle tek tek okundu: hepsi gerçekten "eski / yok / girmez" bağlamında. Bugün sahte geçiş yok; gevşeklik ileriye dönük.

### D-1 (düşük). Denetimin gevşek noktaları
- `rehber_denetim.py:81` `BAGLAM` cümle düzeyinde ve çok genel ("yok", "değil", "çıkar"). Eski bir ifade aynı cümlede bu kelimelerden biriyle geçerse sayılmıyor (enjeksiyon 3, 4d).
  - Öneri: bağlam kelimesi desenin yakınında aransın (örneğin ±40 karakter);
  - "çıkar" listeden çıksın;
  - affedilen cümleler `kontrol.json`'a yazılsın (insan gözden geçirsin).
- `:78` LCD deseni cümlede herhangi bir "11,6" olunca susuyor (4c). Öneri: muafiyet yalnız "11.6inch HDMI LCD" ürün koduna.
- `:158-161` bağlantı satırlarında yalnız kod tutarlılığı denetleniyor; adımın her Baglanti parçasının bir satırda olduğu denetlenmiyor (2d). Öneri: `beklenen` gibi bir bağlantı kümesi karşılaştırması.
- Kabul 1'deki "çelişki 0" bu betikte "eski desen 0 + bileşen anılıyor" demek. Port, yön ve uyarı varlığı (7, 8) denetlenmiyor; bunları bu kontrolde B elle karşılaştırdı (§1). Öneri: Touch VBUS, "köprülenmez", K14 / K11 gibi zorunlu uyarılar için "adımda bulunmalı" listesi.

## §3 Üretim ve tarayıcı

**`--cikti` yalıtımı.** A'nın `--cikti` seçeneği depodaki `rehber/goruntu/`'ya yazmaya devam ediyor (D-4):
- `rehber_uret.py:30` `YAZDIR_GORUNTU = REHBER/goruntu`;
- `:161-166` `sahne_goruntu()`;
- belge `:20-21` "rehber/goruntu her zaman güncellenir".

Bu yüzden B betiği depoda koşmadı. Kendi kopyasını kurdu:
- `SPB/kopya/` = depodaki `rehber/` (9,8 MB) + `TF/rehber/` içinden `rehber_uret.py`, `rehber_denetim.py`, `rehber_metin.py`;
- `ROBOT` kökü kopyaya çözülüyor;
- kopyadaki `rehber/goruntu/*.png` önce silindi, görüntülerin hepsi yeniden üretildi;
- Chrome profili ayrı (`TEMP` = `SPB/tmp`).

Komut (17:37–17:44): `python -B tasarim/freecad/rehber/rehber_uret.py --veri-yok --cikti <SPB/kopya/planlama/rehber>`. rc **0**:
- **50 adım 50 geçti, konsol hatası 0**;
- her parça tek adımda: True, 1192 ↔ 1192 (mesh), şema 13, `sema_fark` hepsi boş;
- yazdır görüntüsü 50, eksik yok;
- telefon 7 × 360 / 0;
- PDF 50 sayfa (HTML 50), taşan yok, küçük yazı 31: 7,2 pt ve 32: 7,8 pt, 3.881 kB;
- denetim ASCII 0, gruplama 0 (eski kural 17), çelişki 0.

**Ek bağımsız konsol kontrolü.** `rehber_uret.py`'nin "konsol hatası", sayfanın kendi `data-hata` özniteliği. B ayrıca DevTools protokolüyle 50 adımın hepsinde gerçek kanalları dinledi (`SPB/telefon_b.py`, `telefon50.log`):
- `Runtime.exceptionThrown`: 0;
- `console.error` / `console.warn`: 0;
- `data-hazir` 50/50.

**PDF eşitliği.** B'nin PDF'i ile depodaki PDF pypdf ile sayfa sayfa karşılaştırıldı: 50 sayfanın metni aynı, A4 (594,96 × 841,92 pt).

**Depo.** Önce / sonra `git status` ve sha1 karşılaştırması: F7b dosyalarında değişiklik 0 (yukarıda). B'nin profilli Chrome süreci kalmadı (0).

## §4 PDF

- Sayfa sayısı 50 = adım 50 (pypdf).
- Meta: başlık, Chrome / Skia, tarih. Yerel kullanıcı yolu 0 (metin ve meta).

**Gözle bakılan sayfalar** (B'nin PDF'i, PyMuPDF ile 110 dpi). A'nın baktıkları (1, 10, 25, 30, 32, 33, 35, 50) dışında 8 sayfa:

| Sayfa | Adım | Yargı |
|---|---|---|
| 4 | 3 A3 omuz traversi | tek sayfa, görüntü doğru, 9,6 pt |
| 13 | 12 B5a güç paneli | ana anahtar yok (F1'e yönlendirme), "Sigortaları henüz takma", doğru |
| 18 | 17 K1 kablolama kapısı 1 | kablo şemaları renkli, liste okunur; enerji çelişkisi D-2 |
| 29 | 28 E2 tilt servosu | 625ZZ listede (F7a O-1 düzeltmesi yerinde) |
| 31 | 30 E3 kafa → tilt hornu | tek sayfa. Erişim "L; kabuklardan önce" (M6'dan gelen "L;" anlamsız, düşük) |
| 36 | 35 F3 göğüs bandı + ekran | 6 not, okunur. Madde 3 "12 V uçlarını tak" → O-1 |
| 46 | 45 H0d | tek sayfa, doğru |
| 22 | 21 D1c | tek sayfa, doğru |

Okunabilirlik için 32 (E4) ve 33 (K2) de açıldı; 32'nin bir kesiti 150 dpi'da yakından incelendi.

### D-3 (düşük). Okunabilirlik: E4 7,2 pt, K2 7,8 pt
- A4 baskıda okunuyor ama atölyede, kol mesafesinde sınırda. Yazdırılan montaj talimatı için 8,5–9 pt alt sınır önerilir.
- İki sayfada 3B görüntü 46 mm'ye inmiş ve robot karede küçük: E4 kafayı, K2 tüm robotu gösteriyor (r 863).
- Öneriler, tercih sırasıyla:
  1. Taban 8 pt olsun; sığmayan adım "Adım N (devam)" sayfasına taşsın. Denetim "PDF sayfa = adım + devam sayfası" diye güncellensin. Kabul "≥ 50 ve adım sayısıyla tutarlı" dediği için bu uyumlu.
  2. Tekrarı kısalt:
     - E4'te "Bağlantı:" paragrafı Bağlantı elemanları tablosunu yineliyor;
     - K2'de kablo kancasındaki 5 taban şeması ve 5 gösterim şeması iş metniyle örtüşüyor.
  3. K2'nin görüntüsü direk + boyun bölgesine kırpılsın.

## §5 Telefon (360 px)

- B'nin kendi CDP koşusu (`SPB/telefon_b.py`): `Emulation.setDeviceMetricsOverride` 360 × 780, mobil.
- Adımlar: önce 6 seçme adım (4, 12, 17, 29, 34, 41; A'nın 7 adımından farklı), sonra 50 adımın hepsi.
- Ölçülenler:
  - belge / body `scrollWidth` − `clientWidth`;
  - görünür her öğenin sağ kenarı > 360;
  - `overflow-x:hidden` olup içeriği taşan öğe;
  - iç yatay kaydırma kutusu;
  - `scrollTo(500, 0)` denemesi.
- **Sonuç (50/50):**
  - görüntü alanı 360;
  - belge 360 / body 360;
  - taşan öğe 0, gizlenmiş taşma 0, iç kaydırma 0;
  - kaydırma denemesi 0 / 0.
- html `overflow-x` "visible", body "auto" (`stil.css:74`). `overflow-x:hidden` hiçbir yerde yok (`grep`).
- Taşmanın gizlenmediği hem CSS'ten hem öğe taramasından doğrulandı.
- Görüntü `SPB/telefon/b-telefon-360-adim-29.png` gözle bakıldı: üst çubuk, sahne, lejant, panel ve alt gezinme 360 px içinde.

## §6 Diff'ler, tarama kaynakları

**Değişen kaynaklar, hepsi brief alanında:**
- `RM` (+294);
- `rehber_veri.py` (+98: `tr = RM.tr`, gruplama anahtarı, `semalar` bloğu; `kablo_yolu_ekran.py` yalnız import edilip okunuyor);
- `rehber_uret.py` (+248);
- yeni `rehber_denetim.py`;
- `rehber/app.js` (+73: `?sahne=1`, şema tüpleri, kadraj, `MODUL_AD`, "önceden takılı" notu);
- `rehber/stil.css` (+7);
- yeni `rehber/yazdir.html`.

Brief dışı değişiklik yok. CRLF korunmuş: HEAD'de CRLF olan dosyaların çalışma kopyalarında her satır CRLF. `rehber_veri.py` için git'in "LF will be replaced" uyarısı yalnız `autocrlf` uyarısı.

**Değişmeyenler:**
- `rehber/index.html`;
- `rehber/veri/robot.glb`, `robot-glb.js` (`git diff HEAD` boş);
- `TF/lale158/kablo_yolu_ekran.py`, `taban_parcalar.py`, `*_lib.py`;
- `M6-montaj-sirasi.md`, `karar-kuyrugu.md`.

**Tarama kaynakları (B'nin koşusu, 17:3x):**
- `py -3 TF/carpisma_kos.py kontrol` → rc **0**, "izlenen 17 dosyanin ozetleri kayitla ayni".
- `py -3 planlama/d158/regresyon.py --yazma` → rc **0**, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)".

**Durumdaki öbür değişiklikler F7b'nin değil:**
- `TF/kabuk/gorsel/*.png` (13): 14:28, K23;
- `TF/montaj/yerlesim-kontrol.json`: 03.11;
- F9b alanı: `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/*`, `planlama/d158/F9b-*`;
- `planlama/dongu-158.md` (orkestratör);
- `F5*-pano-govde.txt`;
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`, `TF/lale158/kafa-yerlesim/kaynak/`, `TF/montaj/lale_dongu*`.

## §7 Commit listesi ve yayın güvenliği

**Liste karşılaştırması.** A'nın listesi (`F7b-gunluk.md` "Dokunulan dosyalar") ile `git status --porcelain` karşılaştırıldı:
- F7b'ye ait değişikliklerin hepsi listede.
- Eksik: `planlama/d158/F7b-brief.md` (izlenmiyor; önceki paketlerin brief'leri commit'li) ve bu dosya `F7b-kontrol.md`.
- Commit dışı kalmalı: `FREECAD-KILIT.txt` (içerik "boş"; A da commit dışı diyor), F9b dosyaları, `dongu-158.md`.
- `TF/rehber/__pycache__/` `.gitignore:1` ile dışarıda.

**Takma ad.** Ad çalışma anında türetildi ve yazılmadı: `git show 647cafc^` ↔ `647cafc` `kafa_parcalar.py` satır 6'daki tek fark kelime (`SPB/ad_tara.py`). Arama büyük / küçük harf duyarsız alt dizge:
- F7b'nin 15 metin dosyası + PDF metni (pypdf, 50 sayfa) + PDF meta: **0**;
- `git grep -il` (izlenen): yalnız `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html`. Bilinen, kapsam dışı üç dosya (F6a / F7a ile aynı).

**Soyad.**
- Ahmet'in soyadı (kaynaktan çalışma anında türetildi): F7b dosyalarında ve PDF'te 0. İzlenen 39 dosyada geçiyor; hepsi önceki paketlerin, kapsam dışı.
- "Ahmet / Efe + büyük harfli kelime" kalıbı: F7b dosyalarında ve PDF'te 0.
- Başka öğrenci / danışman soyadı yok.

### D-5 (düşük). Yerel kullanıcı klasörü yolu
- F7b'nin dosyalarında 3 satır var: `rehber_uret.py:6` (yorum), `:33` (`LAUNCH`), `rehber_veri.py:3` (yorum).
- Üçü de HEAD'de zaten var. F7b eklemedi.
- Yeni dosyalarda (`rehber_denetim.py`, `yazdir.html`, `kontrol.json`, PDF, günlük) 0.
- Depoda toplam 41 izlenen dosyada var (`carpisma_kos.py` dahil; o tarama kaynağı, dokunulmaz).

**Gerekli mi?** Başlatıcının kendisi gerekli: depo yolu ASCII olmayan bir klasör adı içeriyor, `freecadcmd` bunu açamıyor (`rehber_uret.py:6` "ASCII başlatıcı"). Ama yolun sabit yazılması gerekmiyor; başlatıcı kullanıcı ev klasörünün altında.

**Öneri** (`rehber_uret.py:33`):
```python
LAUNCH = os.environ.get("LALE_FC_LAUNCH") or os.path.join(os.path.expanduser("~"), ".robot-cad", "run_fc.py")
```
- Ev klasörü yolu ASCII; davranış aynı kalır.
- Yorumlarda (`:6`, `rehber_veri.py:3`) `~/.robot-cad/run_fc.py` yazılır.
- Bu iş tarama kaynağı değil, P7.2 düzeltme turunda yapılabilir.
- Depo genelindeki 40 dosya ayrı bir temizlik işi (orkestratör).

### D-9 (düşük). İki PNG kümesi ve depo boyutu
İki küme aynı görüntü değil:
- `rehber/goruntu/adim-NN.png` 1200 × 720, yalnız 3B sahne, 3,3 MB. `yazdir.html` göreli yolla bunları kullanıyor. Yayınlanan yazdırılabilir sayfa için gerekli.
- `planlama/rehber/goruntu/adim-NN.png` 1400 × 900, panelli kontrol ekran görüntüsü, 6,3 MB. Kanıt niteliğinde. F7a'dan beri commit'li.
- PDF 3,8 MB ve 3B görüntüleri bir kez daha içeriyor.

Her yeniden üretim geçmişe yaklaşık 13–14 MB ekliyor. Öneriler:
- `rehber/goruntu/` kalsın.
- `planlama/rehber/goruntu/adim-*.png` bundan sonra commit'e girmesin: `.gitignore`'a eklensin. Kanıt `kontrol.json` + birkaç seçme görüntü olsun; örneğin telefon 7 + kafa 3.
- PDF yalnız kilometre taşlarında commit edilsin ya da GitHub release / Pages çıktısı olsun.
- Bu turda F7a ile tutarlı olsun diye hepsi alınabilir. Karar orkestratörün.

### Öbür düşükler
- **D-4.** `--cikti` tam yalıtım sağlamıyor (§3). Öneri: `--cikti` verilince `YAZDIR_GORUNTU` ve `yazdir.html` de `<çıktı>/rehber/` kopyasına gitsin, ya da belge "rehber/ klasörünü kopyala" desin.
- **D-6.** FreeCAD kopya eki tıklama etiketinde kalıyor: 327 parçanın görünen adı "…001/002" ile bitiyor. Örnek: "Yanak-horn cıvatası M3x001" (asıl M3×8), "Çekiç somun M6 (kanal 10)001". F7a verisinde de aynı (HEAD). Parça listesi satırları doğru; yalnız 3B'de tıklayınca çıkan etikette. Öneri: `RM.tr()` görünen ad katmanında sondaki `0\d\d` eki atılsın. Bu D-1'deki ASCII denetiminin kapsamında değil.
- **D-8.** Bilgi: `M6-montaj-sirasi.md` önerisi (`F7b-gunluk.md`) okundu; E3a / E4 / K2 / F2 / F5 satır önerileri bu kontrolün §1 bulgularıyla tutarlı. Dosya değiştirilmemiş.

## Genel karar

**DÜZELTME TURU GEREKİYOR (kısa).** Yeniden üretim, tarayıcı, PDF, telefon, denetim, diff ve tarama bütünlüğü bağımsız olarak geçti. Metin kaynakla tutuyor ve uydurma yok.

Ama rehber, kaynaktaki üç elektrik güvenliği talimatını eksik veriyor (O-1…O-3). Rehber herkese açık, ve bu talimatlar olmadan izlenirse donanım zarar görebilir. Düzeltmeler kaynaktan cümle almak; geometri ve parça sayısı değişmez.

| # | Madde | Etiket |
|---|---|---|
| 1 | Metin doğruluğu | KOŞULLU (O-1, O-2, O-3) |
| 2 | Denetim betiği | GEÇER (D-1) |
| 3 | Üretim ve tarayıcı | GEÇER (D-4) |
| 4 | PDF | GEÇER (D-3) |
| 5 | Telefon 360 px | GEÇER |
| 6 | Diff'ler, tarama kaynakları | GEÇER |
| 7 | Commit listesi, yayın güvenliği | KOŞULLU (brief / kontrol listede yok; D-5) |

## A için düzeltme listesi

Tarama kaynaklarına, `M6-montaj-sirasi.md`'ye ve `karar-kuyrugu.md`'ye dokunma.

**Zorunlu:**

1. **O-1.** `RM` K2 ve F3:
   - K2 kontrol satırı: "Göğüs ekranı regülatörü (LM2577 + LM2596) ekrana bağlanmadan, çıkışı multimetreyle 12 V'a ayarlandı (`planlama/adim3/elektrik.md`)".
   - F3 madde 3 başına: "12 V fişini takmadan önce regülatör çıkışını yeniden ölç: 12 V".
   - Kartın ve mini 2 A sigortanın takılacağı yer modelde yok: "doğrulanmadı" notu.
2. **O-2.** `RM:359` K2 madde 4 ve şema adı: "1N5819 VBUS teline seri, anot hub (Pi) tarafında, katot ESP32 tarafında: çevre 5 V hub'a / Pi'ye geri beslemez. ESP32 kartının kendi VBUS→VIN diyodu varsa gerekmez; multimetreyle bak (doğrulanmadı)" (`elektrik.md:283`). Uygun görürsen F5 Hub 2 maddesine kısa atıf.
3. **O-3.** `RM:286` E3a madde 2 ve not:
   - "Her iki 5 V çıkışına P6KE6V8A: D24V50F5 → Pi hattı ve SY8205 → QLED hattı. Modelde ve BOM'da yalnız QLED hattındaki var; Pi hattındaki modelde yok" (`elektrik.md:47, 282`; `F4a-gunluk.md:188`).
   - Kutup: "katot (çizgili uç) +5 V'a, anot GND'ye".
4. **D-2** (aynı turda, metin):
   - E3a SY8205 ölçümü: "akım sınırlı tezgâh kaynağıyla (12 V)" ya da K2'ye taşı.
   - K2 başına "Akü XT60 ayrık, F3 takılı değil; kafa uçları enerjisiz bağlanır".
5. **Yeniden üret**, kilit kuralıyla:
   - `rehber_uret.py --gorsel-yok` (kilit altında), sonra `--veri-yok`.
   - Beklenen: 50/50, konsol 0, 1192 ↔ 1192, PDF 50, denetim 0. E4 / K2 yazı boyu değişebilir: `kucuk_yazi`'yı günlüğe yaz.
   - Sonra `carpisma_kos.py kontrol` 0 ve `regresyon.py --yazma` 0.
6. **Günlük:**
   - Commit listesine `planlama/d158/F7b-brief.md` ve `planlama/d158/F7b-kontrol.md` ekle.
   - Düzeltme turunu ve yeni sayıları yaz.

**İsteğe bağlı** (aynı turda yapılabilir, P7.3'e de kalabilir):

7. **D-7:** F2 notuna "hoparlör kabı, kulakları ve kelepçesi varsayım (ürün elde yok)". E4 kontrolü "tırnak cama bastırıyor (cıvata tırnağı boss'a tutar)".
8. **D-1:** denetimde bağlam kelimesi desene yakın aransın, "çıkar" çıksın, LCD muafiyeti ürün koduna daralsın, bağlantı satırı kümesi denetlensin, zorunlu uyarı listesi eklensin (Touch VBUS, köprülenmez, 12 V ayarı, 1N5819 yönü).
9. **D-5:** `rehber_uret.py:33` `LAUNCH` `expanduser("~")` ya da `LALE_FC_LAUNCH` ile; yorumlarda `~/.robot-cad/run_fc.py`.
10. **D-3, D-4, D-6:** devam sayfası / 8 pt tabanı; `--cikti` tam yalıtım; görünen adda `0NN` ekinin atılması.

## C için `git add` listesi (düzeltme turu ve B'nin dar yeniden kontrolünden sonra geçerli)

Toplam 122 dosya:

| Grup | Adet |
|---|---|
| Betik | 4 |
| Web | 3 |
| Veri | 2 |
| Yazdır görüntüsü | 50 |
| `kontrol.json` | 1 |
| Kontrol görüntüsü | 50 |
| Telefon görüntüsü | 7 |
| PDF | 1 |
| `R-gunluk.md` | 1 |
| F7b belgesi | 3 |

```
git add tasarim/freecad/rehber/rehber_metin.py tasarim/freecad/rehber/rehber_veri.py \
  tasarim/freecad/rehber/rehber_uret.py tasarim/freecad/rehber/rehber_denetim.py \
  rehber/app.js rehber/stil.css rehber/yazdir.html \
  rehber/veri/rehber-veri.json rehber/veri/rehber-veri.js \
  rehber/goruntu/adim-*.png \
  planlama/rehber/kontrol.json planlama/rehber/goruntu/adim-*.png planlama/rehber/goruntu/telefon-360-adim-*.png \
  planlama/rehber/Lale-montaj-rehberi.pdf planlama/rehber/R-gunluk.md \
  planlama/d158/F7b-brief.md planlama/d158/F7b-gunluk.md planlama/d158/F7b-kontrol.md
```

- `rehber/index.html`, `robot.glb`, `robot-glb.js` değişmedi; listede yok.
- Orkestratör D-9'da kontrol PNG'lerini dışarıda tutmaya karar verirse `planlama/rehber/goruntu/adim-*.png` satırdan çıkar (72 dosya).
- Orkestratör O-1…O-3'ü P7.3'e bırakırsa aynı liste bugünkü hâliyle de commit edilebilir. Bu durumda üçü P7.3 listesine "elektrik güvenliği, yayından önce" diye yazılmalı. B bunu önermiyor: rehber herkese açık.

**Commit'e girmemeli:**
- `planlama/d158/FREECAD-KILIT.txt` (koordinasyon);
- F9b alanı: `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/` (`demo_uret.py`, `viewer-template.html`, `lale158-model.js`), `planlama/d158/F9b-*`;
- `planlama/dongu-158.md` (orkestratör);
- K23: `tasarim/freecad/kabuk/gorsel/*.png` (13), `tasarim/freecad/montaj/yerlesim-kontrol.json`;
- `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`;
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`.

**Commit'ten önce:**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` 0 olmalı.
- `git add` yalnız yukarıdaki yolları almalı. `git add -A`, `git add planlama/` ya da `git add tasarim/` kullanılmamalı; F9b ve orkestratör dosyaları aynı klasörlerde.

**Commit mesajı önerisi:**
```
Lale P7.2: yazdırılabilir montaj rehberi (yazdir.html → PDF 50 sayfa), kafa QLED / ses / hub ve K2 ESP32 USB (hub) metinleri, 13 gösterim şeması, gruplama kod + ad, TR denetimi (rehber_denetim.py), 360 px (F7b)
```

## Kanıtlar (komut → çıktı, özet)

```
git status --porcelain + sha1 (473 dosya)  → önce = sonra (F7b dosyaları); yalnız F9b-gunluk.md (yeni) ve dongu-158.md farklı (başkalarının)
py -3 TF/carpisma_kos.py kontrol           → "izlenen 17 dosyanin ozetleri kayitla ayni"  rc=0
py -3 planlama/d158/regresyon.py --yazma   → "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)"  rc=0
SPB/kopya: rehber_uret.py --veri-yok --cikti → rc=0; 50/50, konsol 0, her parça tek adımda True, sema 13,
           yazdır görüntüsü 50, telefon 7×360/0, PDF 50 (html 50, taşan -, küçük 31:7.2 32:7.8), denetim 0/0/0
SPB/telefon_b.py 0..49 (CDP, 360 px)      → taşma 0, öğe taşması 0, gizli taşma 0, iç kaydırma 0, exception/console.error 0
pypdf: B PDF ↔ depo PDF                    → 50 / 50 sayfa, metni farklı sayfa 0
SPB/enjekte.py, enjekte2.py                → 16 enjeksiyon: 11 yakalandı, 5 kaçtı (2d, 3, 4c, 4d; 7 ve 8 kapsam dışı)
SPB/ad_tara.py                             → takma ad 0, Ahmet'in soyadı 0, ad + büyük harf 0 (F7b dosyaları + PDF metin / meta)
```

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

Kapsam: A'nın düzeltme turu 1 (`F7b-gunluk.md` "Düzeltme turu 1"). Kısaltmalar yukarıdaki gibi. Bu turun çıktıları `SPB/tur1/` altında.

B FreeCAD koşmadı ve kilide yazmadı; kilit baştan sona "boş". Git'e yazmadı. Python `-B` ile koşuldu, `__pycache__` yazılmadı.

## Madde sonuçları

| # | Madde | Etiket |
|---|---|---|
| 1 | Metinler (O-1, O-2, O-3, D-2, D-7) | **KOŞULLU**: O-1…O-3 kapandı; yeni O-4 (K1 madde 6) |
| 2 | Denetim betiği, yeni kontroller | **GEÇER**: 16 enjeksiyondan 12'si yakalandı; kaçan 4'ü varlık denetiminin sınırı (D-1') |
| 3 | `--cikti` yalıtımı | **GEÇER**: D-4 kapandı |
| 4 | Bütünlük (tarama, diff, yol, ad) | **GEÇER**: D-5 kapandı |
| 5 | PDF (E3a, K1, K2, F3) | **GEÇER**; D-3 açık ama commit'i engellemez |
| 6 | Kesin `git add` listesi | aşağıda |

## 1. Metinler

**Diff.** `RM` bu turda +38 / −20 satır değişti; karşılaştırma B'nin ilk kontrol kopyasıyla yapıldı. Değişiklikler yalnız günlükte sayılan yerlerde:

- K1, E3a, K2, F3;
- E4 kontrolü, F2 notu, F5 madde 1;
- ESP32 USB şema adı;
- `TR_EK` / `ASCII_TAMAM` kelimeleri.

Başka değişiklik yok.

**Kaynak karşılaştırması** (kaynak satırlarını B kendisi açtı):

| Yeni metin | Kaynak | Sonuç |
|---|---|---|
| K2 madde 4 + şema: "1N5819: anot hub (Pi) tarafında, katot ESP32 tarafında; çevre 5 V hub'a / Pi'ye geri beslemez; kartın kendi VBUS→VIN diyodu varsa gerekmez, multimetreyle bak (doğrulanmadı)" | `elektrik.md:283` ("anot Pi tarafında", "geri beslemez"); `:285` (DevKit diyodu, montajda multimetre). 05.11 sonrası yol Pi → hub → ESP32 olduğu için "Pi tarafı" = hub tarafı | **aynı**; O-2 kapandı |
| K2 madde 7 + kontrol: regülatör ekrana bağlanmadan multimetreyle 12 V'a ayarlanır; tezgâhta akım sınırlı kaynak (2 A) ve yük direnci | `elektrik.md:67`; `testler/T7-gogus-ekrani-12v.md:37` (24 Ω ≥ 10 W yük), `:43` (ayarsız bağlama), `:45` (2,0 A sınır) | **aynı** |
| K2 / F3 notu: LM2577 + LM2596 ve mini 2 A sigorta modelde yok, yer doğrulanmadı | `elektrik.md:16-17` | **aynı**, işaretli |
| F3 madde 3: fişten önce yeniden ölç, ölçünce enerjiyi kes, fişleri enerjisizken tak | T7:43 ("her … dokunuştan sonra önce ölç") | uyumlu; O-1 kapandı |
| E3a: her iki 5 V çıkışına P6KE6V8A; Pi hattındaki modelde ve BOM'da yok | `elektrik.md:47, 49, 282`; `robot-bom.csv:144` tek adet | **aynı**; O-3 kapandı |
| E3a: "TVS tek yönlü: katot (çizgili uç) +5 V'a, anot GND'ye"; not: "depo kaynağında yazmıyor, veri sayfasıyla doğrulanmadı" | depoda kaynak yok (A da öyle diyor) | **genel bilgi olarak doğru**, işaret yerinde (aşağıda) |
| E3a kontrol: SY8205 ölçümü akım sınırlı tezgâh kaynağıyla (12 V, sınır 1 A); ters kutup koruması yazmıyor | `testler/T3-kafa-5v-akim.md:45-46` (SY8205'te koruma yazmıyor; ilk enerji lab kaynağıyla, 1 A) | **aynı**; D-2'nin E3a kısmı kapandı |
| K2 başı: "Enerjisiz çalış: akü XT60 ayrık, F3 (kafa) takılı değil" | güvenlik ifadesi | doğru; D-2'nin K2 kısmı kapandı |
| K1 kontrolü: "Akü ayrıkken: bara kapasitesi kapasite kademesiyle" | `elektrik.md:462` ("K1 açık, akü ayrık") | **aynı** |
| F2 notu: hoparlör kabı / kulak / ızgara / kelepçe varsayım. E4 kontrolü: tırnak cama basar | `kabuk_parcalar.py:730`; `kafa10_lib.py:341` | **aynı**; D-7 kapandı |

**TVS kutbunun teyidi.** A'nın yazdığı yön doğru:

- P6KE6V8A'da "C" ya da "CA" son eki yok, yani parça tek yönlü. Gövdedeki renk bandı katodu gösterir.
- Koruma bağlantısında katot korunan pozitif hatta (+5 V), anot GND'ye gider. Diyot normalde ters kutuplu kalır ve kırılma geriliminde (6,45–7,14 V) kırpar.
- Ters takılırsa 5 V hattında yaklaşık 0,7 V'ta iletir ve hattı kısa devre eder. SY8205'te de koruma yazmıyor.

Depoda kaynağı olmadığı için metindeki "veri sayfasıyla doğrulanmadı" işareti yerinde.

### O-4 (orta, bu turda doğdu): K1 madde 6, ana anahtar ve acil stop takılmadan enerjili ölçüm istiyor

- **Rehberin yazdığı.** `RM` K1 madde 6: "Enerjili ölçümler (bağlantılar bitince …): akım sınırlı tezgâh kaynağıyla **ya da aküyle, ana sigorta takılı**, F3 (kafa) takılı değil". "Enerjili (madde 6)" etiketli kontroller: XL4016 A / B / C ayarı, motor yön testi, PC817, BMS gözlemi.
- **Aynı adımın durumu.**
  - Madde 1'de ana anahtar henüz yerinde değil; ona gidecek iki uç boşta bırakılıyor.
  - Madde 4'te acil stop mantarı takılmıyor; ucu boşta bırakılıyor.
  - İkisi de F1'de takılıyor (F1 madde 3–4).
- **Kaynağın yazdığı.**
  - Anahtarlı bara (BTS ×2, XL4016 A / B / C) yalnız röle K1 kapanınca enerjilenir.
  - K1 bobini F5 → mantar (NC) üzerinden beslenir. Röle ESP32 devreye alma dizisiyle kapanır: önce ön şarj rölesi K2, 300 ms sonra K1 (`elektrik.md:440-458`).
  - BMS gözlemi ana anahtarın açılışına bağlı (`:460-461`).
- **Sonuç.**
  - Madde 6'daki XL4016 A / B / C ayarı ve motor yön testi, mantar ile ana anahtar uçları köprülenmeden yapılamaz. Metin köprüyü söylemiyor ama ölçümleri yapılabilir gösteriyor. Bu, okuyanı acil stobu ve ana anahtarı köprülemeye, ön şarjı atlamaya itiyor.
  - "Ya da aküyle, ana sigorta takılı" seçeneğinde akım yolu XT60 → 30 A ana sigorta → boştaki ana anahtar ucu, yani bu uç **gerilimli** kalıyor. Uç 12 AWG, açıkta ve LiFePO4 aküye bağlı: kısa devre tehlikesi var.
- **Aynı düzeltmeye girecek ilişkili noktalar.**
  - F1 (`RM` F1 madde 3–4) mantarı ve ana hattın iki ucunu bağlatıyor ama "akü ayrık" demiyor.
  - F1 kontrolündeki "Mantara basınca röle düşüyor" satırı enerji istiyor, ama rehberde "ilk enerji" adımı hâlâ yok.
  - Motor yön testi için "tekerlekler yerden kesik" yazmıyor.
- **Neden bu turun bulgusu.** Bu ölçümler F7a'da da K1 kontrolündeydi. F7b'de açık bir yönerge maddesine dönüştü ve "ya da aküyle, ana sigorta takılı" seçeneği eklendi.

### Düşük bulgular (bu tur)

- **D-1'.** Zorunlu uyarı denetimi yalnız cümlenin var olup olmadığına bakıyor. Bu yüzden şunları kaçırıyor:
  - doğru cümle dururken eklenen çelişkili satır (enjeksiyon 2b, 5b);
  - bağlam penceresinde "yok" geçen eski ifade, affediliyor (7b);
  - güvenliği bozan bir ekleme, örneğin "mantar uçlarını köprüle" (8).

  Engelleyici değil. Öneri: "yasak ifade" listesi (köprüle, ters yönlü diyot / TVS cümlesi).
- **D-3** açık (aşağıda).
- **D-6** açık (tıklama etiketinde `0NN`).
- **D-9** P9.3'e kaldı (orkestratör kararı).

## 2. Denetim betiği: enjeksiyon

Enjeksiyonlar yalnız `SPB/tur1/denetim/` kopyasında, bellek içinde yapıldı (`SPB/tur1/enjekte.py`); depo değişmedi. Temiz kopya geçti; zorunlu uyarı eksiği 0 / 11.

| # | Enjeksiyon | Sonuç |
|---|---|---|
| 1 | E4'ten yalnız Touch VBUS not satırı silindi | **yakaladı** ("köprülenmez@E4" eksik; uyarı o satırdaydı) |
| 1b | E4'te her "Touch VBUS" geçişi silindi | **yakaladı** ("Touch VBUS ölçümü@E4") |
| 2 | K2'de 1N5819 yönü ters yazıldı | **yakaladı** ("1N5819 yönü@K2") |
| 2b | doğru cümle durur, ters yönlü ek kontrol satırı eklenir | kaçırdı (D-1') |
| 3 | K2 regülatör kontrol satırı silindi | **yakaladı** |
| 3b | F3 "yeniden ölç" cümlesi silindi | **yakaladı** |
| 4 | F2 bağlantı satırı (M3×20) tümden düştü | **yakaladı** (gruplama 1; ilk kontroldeki 2d kapandı) |
| 4b | E4 ısıl gömme satırından tek parça düştü | **yakaladı** |
| 5 | E3a TVS kutbu ters yazıldı | **yakaladı** ("TVS kutbu@E3a") |
| 5b | doğru cümle durur, "katot GND'ye" ek satırı eklenir | kaçırdı (D-1') |
| 6 | K2 "akü XT60 ayrık" silindi | **yakaladı** |
| 7 | "ESP32 USB … boyuna çıkar." | **yakaladı** (ilk kontroldeki kaçak kapandı) |
| 7b | '7" ekran yok' | kaçırdı ("yok" pencerede; D-1') |
| 7c | "Kafa LCD vidası 11,6 mm" | **yakaladı** (ilk kontroldeki kaçak kapandı) |
| 8 | K1'e "mantar takılı değilse uçlarını köprüle" eklendi | kaçırdı (D-1') |

Bağlam nedeniyle affedilen 6 cümle `kontrol.json`'da listeleniyor. İlk kontroldeki gibi hepsi gerçekten "eski / yok / girmez" bağlamında.

## 3. `--cikti` yalıtımı

**Kod** (`rehber_uret.py`):
- `--cikti`, `--veri-yok` olmadan reddediliyor (`:318-328`).
- `yazdir.html` ve `veri/rehber-veri.js` `<çıktı>/rehber/` altına kopyalanıyor; yazdır görüntüleri ve PDF de orada üretiliyor.
- Sayfa adresi `url(kok=YAZDIR_KOK)` ile kuruluyor (`:65`, `:288`).

**B'nin koşusu** (depodan):
- Komut: `python -B tasarim/freecad/rehber/rehber_uret.py --veri-yok --cikti <SPB/tur1/cikti>`. `TEMP` scratchpad'e yönlendirildi (ayrı Chrome profili), `PYTHONDONTWRITEBYTECODE=1`.
- Sonuç: rc **0**.
  - **50 / 50**, konsol hatası 0, her parça tek adımda, **1192** parça, 13 şema.
  - Yazdır görüntüsü 50; telefon 7 adım × 360 px, taşma 0.
  - **PDF 50 sayfa** (HTML 50). Taşan yok; küçük yazı 31: 7,2 pt ve 32: 7,2 pt; 3.891 kB.
  - Denetim: ASCII kalıntı 0, gruplama 0, çelişki 0, **zorunlu uyarı eksiği 0 / 11**, affedilen 6.
- **Depoya yazma: F7b dosyalarında 0.** Koşudan önce ve sonra alınan kayıtlar:
  - `git status --porcelain`: aynı.
  - İzlenen 809 dosyanın sha1'i: tek fark `planlama/dongu-158.md` (orkestratör).
  - Değişen ve izlenmeyen 476 dosyanın sha1'i: farklar yalnız `dongu-158.md` ve `planlama/d158/F9b-kontrol.md` (F9b).
  - `find <depo> -newer <işaret>` (.git hariç): yalnız aynı iki dosya.
  - D-4 kapandı.
- **PDF eşitliği.** B'nin PDF'i ile depodaki PDF pypdf ile karşılaştırıldı: 50 / 50 sayfa, metni farklı sayfa 0.

## 4. Bütünlük

- **Tarama:** `py -3 TF/carpisma_kos.py kontrol` → rc **0**, "izlenen 17 dosyanin ozetleri kayitla ayni".
- **Regresyon:** `py -3 planlama/d158/regresyon.py --yazma` → rc **0**, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)".
- **Diff kapsamı.** Bu turun değişiklikleri yalnız brief alanında:
  - `TF/rehber/` altındaki dört betik ve `rehber/yazdir.html`;
  - üretilen dosyalar;
  - `R-gunluk.md` ve `F7b-gunluk.md`.

  `rehber/index.html`, `robot.glb`, `robot-glb.js` ve `.gitignore` değişmedi.
- **Yerel kullanıcı yolu: 0.** Taranan F7b dosyaları: 5 betik, 4 web dosyası, 2 veri dosyası, `kontrol.json`, `R-gunluk.md`, 3 F7b belgesi; ayrıca PDF metni ve meta. Yol artık kullanıcı dizinine göre kuruluyor; D-5 kapandı:
  - `rehber_uret.py:37`: `LAUNCH = os.environ.get("LALE_FC_LAUNCH") or os.path.join(os.path.expanduser("~"), ".robot-cad", "run_fc.py")`;
  - `rehber_veri.py:3`: `~/.robot-cad/run_fc.py`.
- **Takma ad ve soyad: 0.** Aranacak adlar çalışma anında türetildi, hiçbir yere yazılmadı (`SPB/ad_tara.py`). Taranan: F7b dosyaları, depodaki PDF ve B'nin PDF'i (metin ve meta). Sonuç: takma ad 0, Ahmet'in soyadı 0, "ad + büyük harfli kelime" 0.

## 5. PDF

B'nin PDF'i PyMuPDF ile 110 dpi'da açıldı.

| Sayfa | Adım | Görülen |
|---|---|---|
| 18 | 17 K1 | Madde 6: "Enerjili ölçümler … ya da aküyle, ana sigorta takılı". Kontroller "Enerjili (madde 6)" / "Akü ayrıkken" diye ayrılmış. Tek sayfa, 9,6 pt. **O-4** |
| 30 | 29 E3a | İki TVS, kutup, akım sınırlı ölçüm, ters kutup uyarısı, "veri sayfasıyla doğrulanmadı" notu. Tek sayfa |
| 33 | 32 K2 | Başta "Enerjisiz çalış: akü XT60 ayrık"; madde 4'te 1N5819 yönü; madde 7 ve regülatör kontrolü; not; şema adı. Tek sayfa, 7,2 pt |
| 36 | 35 F3 | Madde 3'te yeniden ölçüm ve "enerjisizken tak"; regülatör notu. Tek sayfa |

**D-3 kararı: commit'i engellemez.**
- E4 ve K2 sayfaları 7,2 pt'de A4 baskıda okunuyor; metin doğru, taşma yok.
- Sayfalar "taslak" etiketli; asıl kullanım ekrandaki 3B rehber.
- P7.3'e kalır. Seçenekler: 8 pt taban yazı ve "Adım N (devam)" sayfası, ya da tekrar eden "Bağlantı:" paragrafını ve K2 kablo kancasını kısaltmak.

## Genel karar (düzeltme 1 sonrası)

**KOŞULLU: K1 madde 6 için tek paragraflık son düzeltme, sonra commit.**
- **Kapanan bulgular:** O-1, O-2, O-3; D-1, D-2 (E3a ve K2 kısmı), D-4, D-5, D-7.
- **B'nin kendi koşularında geçenler:** yeniden üretim, `--cikti` yalıtımı, PDF, telefon, denetim, tarama, ad ve yol taraması.
- **Kalan tek engel: O-4.** D-2 düzeltmesi K1'de bu yeni sorunu doğurdu. Yönerge enerjili ölçümleri acil stop ve ana anahtar takılmadan istiyor ve akü seçeneğinde boştaki ana hat ucu gerilimli kalıyor. Rehber herkese açık olduğu için bu düzeltme commit'ten önce gerekli.

**Bu tur bulgu sayısı:** kritik 0, orta 1 (O-4, yeni), düşük 4 açık (D-1', D-3, D-6, D-9). D-9 P9.3'te ele alınacak.

## A için düzeltme

Yalnız `RM` değişir; geometri ve parça sayısı değişmez.

1. **K1 madde 6'yı değiştir.** Önerilen metin: "Enerjili ölçüm K1'de yapılmaz: ana anahtar ve acil stop mantarı F1'de takılır; mantar ve ana anahtar uçları hiçbir zaman köprülenmez, boştaki ana hat ucu gerilimsiz kalır (akü XT60 ayrık). XL4016 A / B / C ve çevre çıkışları kartlar panele takılmadan önce tezgâhta, akım sınırlı kaynakla (12 V girişte), yüksüz ayarlanır; PC817 ölçümü de tezgâhta. Motor yön testi ve ilk açılış (BMS) F1'den sonra yapılır. Bu sıra kaynakta yok, doğrulanmadı."
   - K1'deki "Enerjili (madde 6)" kontrollerini yeniden etiketle: XL4016 ve PC817 "Tezgâhta (kart takılmadan)"; motor yön testi ve BMS "F1 sonrası".
   - Bara kapasitesi ölçümü "akü ayrıkken" olarak kalır.
2. **F1.**
   - İş metninin başına "Bağlarken akü ayrık (XT60 açık)" ekle.
   - Kontrole bir "İlk enerji (F1 sonu)" satırı ekle: "ana anahtar ve mantar bağlı, ana sigorta takılı, F3 (kafa) takılı değil, tekerlekler yerden kesik, BTS EN = 0; ana anahtar açılışında BMS kesiyor mu (`elektrik.md:460-461`); mantara basınca röle düşüyor; devreye alma ön şarjla (`elektrik.md` E9, ESP32 yazılımı); motor yön testi".
   - Var olan "Mantara basınca röle düşüyor" satırını bu satıra kat.
3. **`rehber_denetim.py` `ZORUNLU` listesine iki satır ekle** (isteğe bağlı ama önerilir): K1 `köprülenmez` ve F1 `akü ayrık`.
4. **Yeniden üret ve doğrula.**
   - Kilit kuralıyla önce `--gorsel-yok`, sonra `--veri-yok` koşusu. Beklenen: 50 / 50, PDF 50, zorunlu uyarı eksiği 0.
   - Ardından `carpisma_kos.py kontrol` 0 ve `regresyon.py --yazma` 0.
   - Sonuçları günlüğe yaz.

Bundan sonraki B kontrolü dar olacak: yalnız K1 / F1 metni, yeniden üretim özeti ve koşu öncesi / sonrası sha1.

## C için kesin `git add` listesi

**Ne zaman:** O-4 düzeltmesinden ve B'nin dar yeniden kontrolünden sonra.

**Liste: 122 dosya.** Dosya kümesi bugünküyle aynı kalır, çünkü O-4 düzeltmesi yalnız aynı dosyaları yeniden yazar. Liste `git status` ile sayıldı: 122 dosyanın 122'si durumda. `rehber/goruntu/` yalnız 50 `adim-NN.png` içeriyor. Orkestratör kararıyla (D-9) `planlama/rehber/goruntu/` mevcut hâliyle giriyor.

| Grup | Adet |
|---|---|
| Betik | 4 |
| Web | 3 |
| Veri | 2 |
| Yazdır görüntüsü | 50 |
| `kontrol.json` | 1 |
| Kontrol görüntüsü | 50 |
| Telefon görüntüsü | 7 |
| PDF | 1 |
| `R-gunluk.md` | 1 |
| F7b belgesi | 3 |

```
git add tasarim/freecad/rehber/rehber_metin.py tasarim/freecad/rehber/rehber_veri.py \
  tasarim/freecad/rehber/rehber_uret.py tasarim/freecad/rehber/rehber_denetim.py \
  rehber/app.js rehber/stil.css rehber/yazdir.html \
  rehber/veri/rehber-veri.json rehber/veri/rehber-veri.js \
  rehber/goruntu/adim-*.png \
  planlama/rehber/kontrol.json planlama/rehber/goruntu/adim-*.png planlama/rehber/goruntu/telefon-360-adim-*.png \
  planlama/rehber/Lale-montaj-rehberi.pdf planlama/rehber/R-gunluk.md \
  planlama/d158/F7b-brief.md planlama/d158/F7b-gunluk.md planlama/d158/F7b-kontrol.md
```

**Commit'e girmez:**
- `planlama/d158/FREECAD-KILIT.txt`;
- F9b: `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/`, `planlama/d158/F9b-*`;
- `planlama/dongu-158.md`;
- K23 kabuk görselleri ve `tasarim/freecad/montaj/yerlesim-kontrol.json`;
- `F5-pano-govde.txt`, `F5b-pano-govde.txt`;
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`, `kafa-yerlesim/kaynak/`, `lale_dongu*`.

`git add -A`, `git add planlama/` ya da `git add tasarim/` kullanılmamalı. Commit'ten önce `carpisma_kos.py kontrol` 0 olmalı.

**Commit mesajı önerisi:**

```
Lale P7.2: yazdırılabilir montaj rehberi (yazdir.html → PDF 50 sayfa), kafa QLED / ses / hub ve K2 ESP32 USB (hub) metinleri, elektrik güvenliği (iki TVS, 1N5819 yönü, göğüs 12 V ayarı, enerjisiz K2, K1/F1 enerji sırası), 13 gösterim şeması, gruplama kod + ad, TR + zorunlu uyarı denetimi (rehber_denetim.py), 360 px (F7b)
```

## Kanıtlar (bu tur)

```
git status + sha1 (izlenen 809, değişen/izlenmeyen 476) önce/sonra → F7b 0 fark; yalnız dongu-158.md, F9b-kontrol.md (başkalarının)
find -newer (koşu boyunca, .git hariç)       → dongu-158.md, F9b-kontrol.md
rehber_uret.py --veri-yok --cikti <SPB/tur1/cikti>   → rc=0; 50/50, konsol 0, 1192, PDF 50, telefon 7×360/0, denetim 0, zorunlu 0/11
pypdf B PDF ↔ depo PDF                       → 50/50, metni farklı sayfa 0
py -3 TF/carpisma_kos.py kontrol              → rc=0;  regresyon.py --yazma → rc=0 GEÇER
SPB/tur1/enjekte.py                           → 16 enjeksiyon: 12 yakalandı, 4 kaçtı (2b, 5b, 7b, 8: varlık denetiminin sınırı)
SPB/ad_tara.py                                → takma ad 0, soyad 0, ad + büyük harf 0, yerel yol 0 (F7b dosyaları + iki PDF)
```

---

# Son kontrol (düzeltme 2): B, 09.11.2026

**Kapsam.** A'nın düzeltme turu 2 (`F7b-gunluk.md` "Düzeltme turu 2"; O-4) için dar kontrol. Bu turun çıktıları `SPB/tur2/` altında.

**B'nin çalışma koşulları.**
- FreeCAD koşmadı ve kilide yazmadı; kilit "boş".
- Git'e yazmadı.
- Python `-B` ile koşuldu.

## Madde sonuçları

| # | Madde | Etiket |
|---|---|---|
| 1 | K1 ve F1 metinleri, tüm adımlarda enerji / köprü taraması | **GEÇER**: O-4 kapandı; üç yeni düşük bulgu var (D-10, D-11, D-12) |
| 2 | Denetim: yeni 4 `ZORUNLU` satırı | **GEÇER**: 9 enjeksiyonun 8'i yakalandı; "köprüle" eklemesi hâlâ kaçıyor (D-1') |
| 3 | Değişen dosyalar (sha1), tarama, regresyon | **GEÇER** |
| 4 | PDF sayfa 18 (K1) ve 34 (F1) | **GEÇER** |
| 5 | Kesin liste ve commit mesajı | onaylandı (aşağıda) |

## 1. K1 ve F1 metinleri

**Diff.** Karşılaştırma B'nin tur 1 kopyasıyla yapıldı.
- `RM` değişiklikleri yalnız iki adımda:
  - K1: madde 6 ve dört kontrol satırı;
  - F1: iş metninin başı ve "İlk enerji" kontrol satırı.
- `rehber_denetim.py` değişiklikleri:
  - `ASCII_TAMAM`'a 9 kelime eklendi;
  - `ZORUNLU`'ya 4 satır eklendi, toplam 15.
- Başka değişiklik yok.

**Kaynak karşılaştırması.** B kaynakları kendisi açtı: `elektrik.md:430-462`, `T13:118`.

| Metin | Kaynak | Sonuç |
|---|---|---|
| K1 madde 6: "K1'de enerji verilmez"; mantar ve ana anahtar uçları hiçbir zaman köprülenmez; akü XT60 ayrık, boştaki uçlar gerilimsiz ve bantlı | Anahtarlı bara yalnız K1 kapanınca enerjilenir. Bobin F5 → mantar NC → IRLZ44N yolundan beslenir (`:441-444`) | doğru; O-4 kapandı |
| K1 kontrol: XL4016 A / B / C ve çevre çıkışları tezgâhta ayarlanır (12 V giriş, yüksüz, akım sınırlı); PC817 3,3 V ölçümü tezgâhta | `:242` (PC817: 12 V verip kes, 3,3 V tarafında ölç) | uyumlu. Sıra kaynakta yok, metinde "doğrulanmadı" işareti var |
| F1 başı: "Bağlarken akü ayrık (XT60 açık)" | güvenlik ifadesi | doğru |
| F1 İlk enerji: BTS EN = 0; motorlar ön şarjda çekmez | `:451` | **aynı** |
| F1 İlk enerji: "röle K2 → 300 ms → röle K1 (ESP32 yazılımı)" | `:448, 455-456`; adım (2)–(4) | **aynı**. Özet olarak yeterli; adım (5) ve PC817 #2 teyitleri yazılımda (D-11) |
| F1 İlk enerji: "Mantara basınca iki röle de düşüyor" | `:437` ("acil stop iki röleyi birlikte bırakır"); şema `:442-444` (mantar NC iki bobini de besler); `:457` | Kaynakla tutarlı. Ancak devreye almadan 100 ms sonra K2 zaten bırakılıyor (`:456`), yani gözlenen yalnız K1 (D-11) |
| F1 İlk enerji: "Ana anahtarı aç: BMS kesiyor mu gözle (röle K1 açık, yalnız F3 / F4 / F5 girişleri)" | `:460-461` | Kaynakla aynı, ama aynı satırdaki "F3 (kafa) takılı değil" ile çelişiyor (D-10) |
| F1 İlk enerji: tekerlekler yerden kesik (şasi takozda) | `T13:118` ("Esas düzen: tekerler havada"; takozlar şasiye) | uyumlu. Bu adım için kaynakta yok, metinde "doğrulanmadı" işareti var |

**Betikli tarama.** Betik: `SPB/tur2/ara.py` ve `ara2.py`. Taranan veri: `rehber-veri.json`, 50 adımın tamamı, parça adları hariç bütün metin alanları. Aranan desenler:
- "akü", "köprü", "enerjili", "sigorta takılı", "enerji ver", "enerjisiz", "gerilimli";
- F1 ve sonrası için ayrıca "XT60", "ana anahtar", "devreye", "enerji", "takılı", "sigorta", "mantar", "ölç".

Sonuçlar:
- **"Enerjili" geçişi 0.** Eski "Enerjili (madde 6)" satırlarının hepsi kalktı.
- **"Köprü" 5 geçiş, hepsi yasak ya da teyit bağlamında:**
  - K1 madde 6: "hiçbir zaman köprülenmez";
  - K1 kontrol: "köprülenmedi";
  - E3a ve E4 notu: "iki 5 V hattı köprülenmez";
  - F2 "kelepçe köprüsü" ve F3 "cep üst kenarı köprü": parça adı.

  Köprüleme isteyen talimat 0.
- **Akü bağlıyken bağlantı yaptıran talimat 0.**
  - Bağlantı yapılan adımların başında akünün ayrık olduğu yazıyor:
    - B3: "Aküyü şimdi BAĞLAMA: XT60 uçları ayrık";
    - K1: "Bağlarken akü ayrık";
    - K2: "Enerjisiz çalış: akü XT60 ayrık";
    - F1: "Bağlarken akü ayrık".
  - "Sigorta takılı" tek yerde geçiyor: F1 İlk enerji. Bu satır bağlantılar bittikten sonra geliyor ve "aküyü XT60'tan ayır" diye bitiyor.
  - F3'te fiş enerjisizken takılıyor.
  - F5 madde 2'deki devreye alma testi kapaklar açıkken yapılıyor; bu testte bağlantı talimatı yok.

### Düşük bulgular (bu turda doğanlar; hiçbiri engelleyici değil)

**D-10. F1 İlk enerji: "F3 (kafa) takılı değil" ile devreye alma ve motor yön testi bir arada.**
- **Çelişki.** Devreye alma komutu Pi'den gelir (`elektrik.md:106, :255`; rehberde F5 madde 2: "ESP32 ile Pi hub üzerinden konuşur"). Pi kafada ve F3 üzerinden beslenir. F3 takılı değilken ESP32 F4 çevre 5 V ile çalışır ama komut gelmez. Röle kapanmaz, motor yön testi yapılamaz.
- **BMS gözlemi.** Kaynağa göre ana anahtar açılışında F3 / F4 / F5 girişleri bağlıdır (Pololu girişi dahil, `:460-461`). Metin de bunu yazıyor ama F3 yokken açılış gerçek açılıştan hafif kalır.
- **Neden engelleyici değil.**
  - Tehlike yok: komut gelmezse röle kapanmaz, hareket olmaz.
  - Tam açılış (F3 takılı, hub bağlı) F5 madde 2'deki devreye alma testinde yeniden yapılıyor.
- **Öneri (P7.3).** "İlk enerji"yi iki aşamaya böl: (a) F3 takılı değil, ana anahtar aç, BMS gözle, kapat; (b) F3 tak, yeniden aç, BMS gözle, devreye alma ön şarjla, mantar, motor yön testi.

**D-11. "Mantara basınca iki röle de düşüyor" ifadesi.**
- Devreye almadan 100 ms sonra K2 zaten bırakılıyor (`:456`). Normal çalışmada mantara basınca gözlenen yalnız K1'in düşmesi.
- Metindeki ön şarj özeti adım (5)'i ve PC817 #2 teyitlerini de anmıyor.
- Öneri (P7.3): "Mantara basınca K1 düşüyor (K2 devreye almadan sonra zaten açık); dizinin tamamı `elektrik.md` E9 yazılım adımları".

**D-12. Tezgâh ayarının zamanlaması geride kalıyor.**
- XL4016 ayarı ve PC817 ölçümünün "kart takılmadan, B3 / B5a öncesi" yapılacağı yalnız K1'de (adım 17) yazıyor. Kartlar B3 / B5a'da takılıyor, yani okuyan bunu iş işten geçtikten sonra görür.
- A da günlükte bunu açık olarak yazdı. Öneri (P7.3): B3 ve B5a'ya bir kontrol satırı.

## 2. Denetim: enjeksiyon

**Yöntem.** Enjeksiyonlar yalnız `SPB/tur2/denetim/` kopyasında, bellek içinde yapıldı (`SPB/tur2/enjekte.py`). Kopyanın `rehber_denetim.py` sha1'i depodakiyle aynı (`7d47ef92398e`). Temiz kopya geçti; zorunlu eksik 0 / 15.

| # | Enjeksiyon | Sonuç |
|---|---|---|
| 9 | K1 "K1'de enerji verilmez" → "Enerjili ölçümler" | **yakaladı** |
| 10 | K1 "hiçbir zaman köprülenmez" → "gerekirse köprülenir" ("köprülenmedi" kontrolü duruyor) | **yakaladı** |
| 10b | aynı + "köprülenmedi" → "köprülendi" | **yakaladı** |
| 11 | F1 "Bağlarken akü ayrık" silindi | **yakaladı** |
| 12 | F1 İlk enerji'den "BTS EN = 0" silindi | **yakaladı** |
| 12b | F1 "ön şarj: K2 → 300 ms → K1" → "röle K1 doğrudan" | **yakaladı** |
| 12c | F1 İlk enerji satırı tümden silindi | **yakaladı** |
| 12d | İlk enerji satırı F1'den K1'e taşındı | **yakaladı** |
| 12e | F1'den "tekerlekler yerden kesik" silindi | kaçırdı (desende yok; D-1') |
| 8c | K1 "akü ayrık" → "akü bağlı olabilir" | **yakaladı** |
| 8 | K1 kontrolüne "mantar takılı değilse uçlarını köprüle" eklendi | **kaçırdı** (D-1') |
| 8b | F1 iş metnine "test için mantar uçlarını köprüle" eklendi | **kaçırdı** (D-1') |

**Sonuç.** Yeni 4 satır hedeflediği silme ve değiştirmeleri yakalıyor. Eklenen yasak talimatı ("köprüle") yakalamıyor, çünkü denetim hâlâ yalnız uyarının var olup olmadığına bakıyor (D-1').
- Bugünkü metinde böyle bir talimat yok (madde 1'deki tarama 0).
- Engelleyici değil.
- P7.3 önerisi:
  - "yasak ifade" listesi: `köprüle\b`, `uçlarını köprüle`, `akü bağlı(yken)? bağla`;
  - F1 için `yerden kesik` satırı.

## 3. Değişen dosyalar

**B'nin sha1 karşılaştırması.** Bu tur, B'nin tur 1 sonrası kaydıyla karşılaştırıldı. Kayıt git'siz `sha1sum` ile alınmıştı: izlenen 809 dosya, değişen ve izlenmeyen 476 dosya. `git status --porcelain` aynı. Değişen dosyalar:

| Grup | Dosya |
|---|---|
| A'nın bildirdiği 7 dosya | `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js`, `planlama/rehber/kontrol.json`, `planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-17.png`, `adim-33.png`, `tasarim/freecad/rehber/rehber_denetim.py` |
| Kaynak ve belge | `tasarim/freecad/rehber/rehber_metin.py` (A'nın sha1 kaydı düzeltmeden sonra alındığı için tablosunda yok, günlükte belirtilmiş), `planlama/d158/F7b-gunluk.md` |
| B'nin kendi dosyası | `planlama/d158/F7b-kontrol.md` (tur 1 eki) |
| Başkasının | `planlama/dongu-158.md` (orkestratör) |

**Değişmeyenler.** Bundan başka değişen dosya yok. Değişmeyenler arasında:
- `rehber_uret.py`, `rehber_veri.py`, `app.js`, `stil.css`, `yazdir.html`, `index.html`, `robot.glb`, `robot-glb.js`;
- 50 yazdır görüntüsü, öbür 48 kontrol PNG'si, 7 telefon görüntüsü;
- `R-gunluk.md`, `.gitignore`, F9b dosyaları.

A'nın "7 dosya değişti" iddiası doğru.

**B bu kontrolde depoya yazmadı.** Kontrol başında ve sonunda alınan sha1 ve `git status` aynı. `find -newer` 0 dosya buldu, `__pycache__` 0.

**Tarama ve regresyon:**
- `py -3 TF/carpisma_kos.py kontrol` → rc **0** ("izlenen 17 dosyanin ozetleri kayitla ayni").
- `py -3 planlama/d158/regresyon.py --yazma` → rc **0** ("Sonuç: GEÇER").

**`kontrol.json` (18:26):**
- 50 / 50, konsol hatası 0, 1192 ↔ 1192, her parça tek adımda, 13 şema;
- telefon geçti;
- PDF 50 sayfa (HTML 50), taşan yok, küçük yazı 31 ve 32 sayfalarda 7,2 pt;
- denetim: ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0; `ZORUNLU` 15 satır.

**Ad ve yol:**
- Yerel kullanıcı yolu: F7b dosyalarında, PDF metninde ve PDF metasında 0. Yalnız `%LOCALAPPDATA%` ortam değişkeni adı geçiyor; bu bir yol değil.
- Takma ad 0, Ahmet'in soyadı 0. Aranan adlar `SPB/ad_tara.py` ile çalışma anında türetildi, hiçbir yere yazılmadı.

## 4. PDF

**Karşılaştırma.** Tur 1'de B'nin ürettiği PDF ile bugünkü depodaki PDF karşılaştırıldı. Alt bilgideki üretim saati maskelenince metni farklı sayfa yalnız **18 ve 34**. Öbür 48 sayfa aynı.

| Sayfa | Adım | Görülen (110 dpi) |
|---|---|---|
| 18 | 17 K1 | Madde 6 tam ("K1'de enerji verilmez … köprülenmez … tezgâhta … doğrulanmadı"). Kontroller: "Tezgâhta (kart takılmadan …)", "köprülenmedi", "burada değil: F1 İlk enerji". "Enerjili" yazan satır yok. Tek sayfa, gövde 9,6 pt |
| 34 | 33 F1 | Başta "Bağlarken akü ayrık (XT60 açık)."; kontrolde İlk enerji satırının tamamı. Tek sayfa, okunaklı |

D-3 kararı değişmedi: 7,2 pt sayfalar (31 ve 32) commit'i engellemez.

## Son karar

**GEÇER. F7b commit edilebilir.**
- O-1, O-2, O-3 ve O-4 kapandı. Açık kritik ya da orta bulgu yok.
- Metinler kaynakla tutarlı. Kaynakta olmayan sıralar "doğrulanmadı" diye işaretli.
- Köprüleme ya da akü bağlıyken bağlantı talimatı 0.
- Üretim, PDF, telefon, denetim, tarama ve regresyon geçti. Depo yazımı beklenen 7 dosya ve 2 kaynakla sınırlı.

**Bulgu sayısı (açık):**
- kritik 0, orta 0;
- düşük 7: D-1', D-3, D-6, D-10, D-11, D-12, D-9;
- D-9 P9.3'te, ötekiler P7.3'e.

Hiçbiri commit'i engellemez.

## C için kesin `git add` listesi (122 dosya; onaylandı)

**Sayım.** Liste bugün yeniden sayıldı.
- Listedeki yollar 122 dosyaya açılıyor. `git status --porcelain -uall` bu 122 yolun 122'sini durumda gösteriyor.
- `rehber/`, `planlama/rehber/`, `tasarim/freecad/rehber/` ve `planlama/d158/F7b-*` altındaki durum satırları da toplam 122. Liste dışında kalan dosya yok.
- Orkestratör kararıyla (D-9) `planlama/rehber/goruntu/` mevcut hâliyle (57 PNG) giriyor.

```
git add tasarim/freecad/rehber/rehber_metin.py tasarim/freecad/rehber/rehber_veri.py \
  tasarim/freecad/rehber/rehber_uret.py tasarim/freecad/rehber/rehber_denetim.py \
  rehber/app.js rehber/stil.css rehber/yazdir.html \
  rehber/veri/rehber-veri.json rehber/veri/rehber-veri.js \
  rehber/goruntu/adim-*.png \
  planlama/rehber/kontrol.json planlama/rehber/goruntu/adim-*.png planlama/rehber/goruntu/telefon-360-adim-*.png \
  planlama/rehber/Lale-montaj-rehberi.pdf planlama/rehber/R-gunluk.md \
  planlama/d158/F7b-brief.md planlama/d158/F7b-gunluk.md planlama/d158/F7b-kontrol.md
```

**Girmez:**
- `planlama/d158/FREECAD-KILIT.txt`;
- F9b: `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/`, `planlama/d158/F9b-*`;
- `planlama/dongu-158.md`;
- K23 kabuk görselleri ve `tasarim/freecad/montaj/yerlesim-kontrol.json`;
- `F5-pano-govde.txt`, `F5b-pano-govde.txt`;
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`, `kafa-yerlesim/kaynak/`, `lale_dongu*`.

**Kurallar:**
- `git add -A`, `git add planlama/` ve `git add tasarim/` kullanılmaz.
- Commit'ten önce `carpisma_kos.py kontrol` 0 olmalı.
- `F7b-kontrol.md` bu bölümle birlikte eklenir.

**Commit mesajı (son hâli):**
```
Lale P7.2: yazdırılabilir montaj rehberi (yazdir.html → PDF 50 sayfa), kafa QLED / ses / hub ve K2 ESP32 USB (hub) metinleri, elektrik güvenliği (iki TVS, 1N5819 yönü, göğüs 12 V ayarı, enerjisiz K2, K1/F1 enerji sırası), 13 gösterim şeması, gruplama kod + ad, TR + zorunlu uyarı denetimi (rehber_denetim.py), 360 px (F7b)
```

## Kanıtlar (bu tur)

```
diff tur1 kopyası ↔ depo (rehber_metin.py, rehber_denetim.py)  → yalnız K1, F1, ASCII_TAMAM, ZORUNLU +4 (15)
SPB/tur2/ara.py, ara2.py (50 adım)          → "enerjili" 0; köprüleme talimatı 0; akü bağlıyken bağlantı 0
SPB/tur2/enjekte.py                          → 12 enjeksiyon: 9 yakalandı; 3 kaçtı (8, 8b, 12e: varlık denetiminin sınırı)
sha1 tur1 sonrası ↔ şimdi (809 izlenen, 476 değişen/izlenmeyen) → A'nın 7 dosyası + rehber_metin.py + F7b-gunluk.md (+ F7b-kontrol.md, dongu-158.md)
sha1 + git status kontrol başı ↔ sonu         → aynı; find -newer 0 (B depoya yazmadı)
PyMuPDF tur1 PDF ↔ depo PDF (saat maskeli)    → metni farklı sayfa: 18, 34
py -3 TF/carpisma_kos.py kontrol              → rc=0;  regresyon.py --yazma → rc=0 GEÇER
SPB/ad_tara.py                                → takma ad 0, soyad 0, yerel yol 0 (F7b dosyaları + PDF metin / meta)
git status -uall (122 yol)                    → 122 / 122; F7b alanında liste dışı dosya 0
```
