# P5.1 — 10 servoluk kanal tablosu önerisi (Efe için, 08.11.2026)

Bu bir **öneri belgesidir**: `kod/` altında hiçbir dosya değişmedi, karar yok. Kod tarafı `main` dalından okundu
(`git show main:...`, son commit `84bc2b4`, 29.10.2026). CAD tarafı `lale-duzeltme` dalının çalışma kopyasından okundu.
CAD betikleri koşturulmadı; `eklem_sinirlari.json` ile `arayuz.py` elle karşılaştırıldı, 10 eklemin sınırı birebir aynı.

## Kaynak kısaltmaları

| Kısa | Dosya |
|---|---|
| AY | `tasarim/freecad/arayuz.py` (CAD eklem sınırları için tek kaynak) |
| EJ | `kod/ortak/eklem_sinirlari.json` (AY'den üretilir; **yalnız `lale-duzeltme` dalında var, `main`'de yok**: `git ls-tree main` içinde `kod/ortak` 0 dosya) |
| KY | `main:kod/jestler/kanallar.yaml` (kodun servo tablosu, tek kaynak) |
| JV | `main:kod/esp32/src/jest_verisi.h` (KY'den üretilmiş) |
| SV | `main:kod/esp32/src/servolar.cpp` |
| OR / OM | `tasarim/freecad/omuz/omuz_rapor.py` / `omuz_montaj.py` |
| DR | `tasarim/freecad/dirsek/dirsek_rapor.py` |
| KM / KR | `tasarim/freecad/kafa/kafa_montaj.py` / `kafa_rapor.py` |
| EL | `planlama/adim3/elektrik.md` |
| YP | `planlama/yazilim-plani.md` |

## 1. Önerilen tablo (10 satır)

Açılar CAD işaretiyle verildi: işaretli derece, 0 = ev pozu (EJ'nin ve YP:44 `jnt` mesajının birimi). Mevcut kodun 0–180
"robot açısı"na çevrimi tablonun altında.

| # | Ad (kod) | EJ anahtarı | PCA9685 | Servo | Sınır (°) | Ev pozu (°) | Servo orta (90°) hangi eklem açısında | Sol / ayna | Mevcut kod (KY) | Fark |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | `sag_omuz` | `r_s1` | 0 | DS3235 | −45 … 135 | 0 | S1 = 45 (horn servo 45°'deyken, kol aşağıda takılır) | ayna `sol_omuz`, `ayni` | DS3218, 0 … 160, boşta 10, servo orta = 90 | model; üst 160 → 135; alt 0 → −45; ev 10 → 0; sıfır 45° kayık |
| 1 | `sag_dirsek` | `r_dirsek` | 1 | MG996R | 0 … 105 | 0 | dirsek = 52,5 | ayna `sol_dirsek`, `ayni` | 0 … 110, boşta 15, servo orta = 90 | üst 110 → 105; ev 15 → 0; sıfır 37,5° kayık |
| 2 | `sol_omuz` | `l_s1` | 2 | DS3235 | −45 … 135 | 0 | S1 = 45 (aynalı) | `ters: true` | 0 … 160, `ters: true` | satır 0 ile aynı |
| 3 | `sol_dirsek` | `l_dirsek` | 3 | MG996R | 0 … 105 | 0 | dirsek = 52,5 | `ters: true` | 0 … 110, `ters: true` | satır 1 ile aynı |
| 4 | `kafa_pan` | `pan` | 4 | MG996R | −90 … 90 | 0 | pan = 0 | ayna kendisi, `180-aci` | 45 … 135 (= CAD +45 … −45) | kod daha dar (±45); işaret ters (aşağıda) |
| 5 | `kafa_tilt` | `tilt` | 5 | MG996R | −13 … 13 | 0 | tilt = 0 | ayna kendisi, `ayni` | 70 … 110 (= CAD +20 … −20) | **kod ±20, CAD ±13** |
| 6 | `sag_omuz_yana` (yeni) | `r_s2` | 6 | DS3235 | 5 … 120; S1 ≥ 120 iken ≤ 117 | 5 | **belirsiz** (horn servo 30°'de takılır; kolun o anki pozu yazmıyor) | ayna `sol_omuz_yana`, `ayni` | yok | yeni kanal |
| 7 | `sag_bilek` (yeni) | `r_bilek` | 7 | MG996R | −90 … 90 | 0 | bilek = 0 (avuç içe bakar) | ayna `sol_bilek`, `ayni` | yok | yeni kanal |
| 8 | `sol_omuz_yana` (yeni) | `l_s2` | 8 | DS3235 | 5 … 120; S1 ≥ 120 iken ≤ 117 | 5 | belirsiz (satır 6) | `ters: true` | yok | yeni kanal |
| 9 | `sol_bilek` (yeni) | `l_bilek` | 9 | MG996R | −90 … 90 | 0 | bilek = 0 | `ters: true` | yok | yeni kanal |

Kanal 10–12 sonar trig, 13–15 yedek (YP:31, YP:65, EL:455): 0–9 ile çakışma yok.

**Hücre kaynakları**

- **Ad:** mevcut 6 ad KY:44–49. Yeni 4 ad bu belgenin önerisi; biçim KY'deki `<taraf>_<eklem>` kalıbı. EJ anahtarları EJ `eklemler`.
- **PCA9685:** 0–5 KY:44–49 (korundu, brief); 6–9 öneri (brief: yeni 4 servo 0–5'ten sonra, 10–12'ye değmeden). Alternatif düzen §3.
- **Servo:** DS3235 AY:182 (`servo_kod`), AY:179, README.md:39; 180° sürüm `planlama/maliyet.json:47`. MG996R AY:505 (dirsek, bilek), AY:583 (pan, tilt), README.md:39.
- **Sınır:** S1 AY:175 = EJ `r_s1.min/max`; S2 AY:176 = EJ `r_s2.min/max`; bağımlı sınır EJ `bagimli[0..1]` (S1 120 … 135 iken S2 5 … 117);
  dirsek AY:504 = EJ `r_dirsek`; bilek AY:509 = EJ `r_bilek`; pan AY:579 = EJ `pan`; tilt AY:582 = EJ `tilt`. Sol kol sınırları sağ ile aynı (EJ `l_*`).
- **Ev pozu:** S1 0 ve S2 = yana alt sınırı (5) OM:35–37; dirsek 0, bilek 0 AY:478; pan 0, tilt 0 AY:522.
- **Servo orta:** S1 OR:111 ("S1'i 45° konumuna getir, horn'u kol aşağıdayken tak") ve AY:175; S2 OR:114 ("S2'yi 30° konumuna getir, horn'u tak",
  kol pozu yazılmamış); dirsek DR:239 (servo orta = dirsek (0 + 105) / 2 = 52,5); bilek DR:237 (orta konum, avuç içe); pan KM:861; tilt KR:220.
  "Sıfır kayması" sütunu bu iki sayının farkı: S1 90 − 45 = 45, dirsek 90 − 52,5 = 37,5 (hesap).
- **Sol / ayna:** ayna eşlemesi ve `ayni` / `180-aci` kuralı KY:26–33, KY:44–49; sol kolun ters işareti EJ `sol_isaret.deger = −1`
  ("tahmini; montajdan sonra her servo tek tek doğrulanır") ve KY:46–47 `ters: true`. Yeni sol kanallara aynı kural önerildi.
- **Mevcut kod:** KY:44–49 = JV:44–49; boşta değerleri `main:kod/jestler/bosta.yaml:7–8` = JV:53; "servo orta = robot 90" KY:13 ve SV `pca_yaz`
  (servo açısı = robot açısı, sıfır kayması alanı yok).

**Kodun 0–180 robot açısına çevrim** (KY:8–12'deki tanım ile AY'deki yön tanımları karşılaştırıldı):

| Eklem | Kod tanımı | CAD tanımı | Çevrim | Kod biriminde sınır |
|---|---|---|---|---|
| omuz (S1) | 0 aşağı, 90 öne yatay (KY:9) | + öne kaldırır; +90'da el ucu öne 140 mm, yukarı (montaj `eklem-dogrulama.json` `yon[0]`) | bugünkü tanımla kod = CAD (−45 … 135, **yazılamaz**, aşağıdaki not). Öneri: **kod = CAD + 45** | 0 … 180 |
| dirsek | 0 düz, 90 dik bükük (KY:10) | + ön kolu öne büker (AY:503) | kod = CAD; §4 madde 4 seçenek (a) seçilirse kod = CAD + 37,5 | 0 … 105; (a)'da 37,5 … 142,5 |
| kafa_pan | 90 ileri, küçük = robotun sağı (KY:11) | + yüz robotun sağına (AY:578) | kod = 90 − CAD | 0 … 180 |
| kafa_tilt | 90 düz, küçük = aşağı (KY:12) | + baş öne, yüz aşağı (AY:581) | kod = 90 − CAD | 77 … 103 |
| S2 | kodda yok | AY:176 | öneri: kod = CAD | 5 … 120 |
| bilek | kodda yok | AY:509 | öneri: **kod = CAD + 90** | 0 … 180 |

Not: kodun üreticisi açı sınırını yalnız 0 … 180 içinde kabul eder (`main:kod/jestler/jest_uret.py:63` `0 <= min_aci < max_aci <= 180`,
min_aci < 0 reddedilir); SV:38–39'da da servo açısı = robot açısı olduğundan < 0 yazılamaz. Bu yüzden S1 −45 … 135 ve bilek −90 … 90 kod biriminde
kaydırılarak yazılır:
- **Bilek:** kod = CAD + 90 → 0 … 180, ev pozu kod 90. Servo orta = bilek 0 (DR:237), yani kod 90 = servo orta: KY:13 montaj kuralıyla uyumlu, sıfır kayması gerekmez.
- **Omuz (S1):** kod = CAD + 45 → 0 … 180, ev pozu (kol aşağıda) kod 45. Servo orta = S1 45 (OR:111, AY:175), yani kod 90 = servo orta: KY:13 ile uyumlu,
  sıfır kayması gerekmez. Bedeli: KY:9'daki "0 = kol aşağıda" tanımı "45 = kol aşağıda" olur ve bütün jestlerin omuz değerleri +45 kayar (§4 madde 4).

## 2. Mevcut 6 servoluk kodda CAD ile çelişen satırlar (11)

| # | Kod (main) | Kodda | CAD / plan | CAD kaynağı | Risk |
|---|---|---|---|---|---|
| Ç1 | KY:44, 46; JV:44, 46 | omuz `DS3218` | DS3235 (karar 24.10) | AY:180–182, README.md:39 | darbe aralığı ve tork farklı; KY:6 bunu zaten not etmiş |
| Ç2 | KY:44, 46 | omuz 0 … 160 | S1 −45 … 135 | EJ `r_s1` | 135–160 arası komut CAD sınırının dışında; −45 … 0 kullanılamıyor |
| Ç3 | KY:45, 47 | dirsek 0 … 110 | 0 … 105 | EJ `r_dirsek`; AY:504 (110'da boşluk 1,6 mm, 115 çarpar) | yazılım sınırı aşılıyor |
| Ç4 | KY:49 | tilt 70 … 110 (= ±20) | ±13 | EJ `tilt`; AY:582 (ilk çakışma +18 / −17) | **çakışma bölgesine komut gidebilir** |
| Ç5 | KY:48 | pan 45 … 135 (= ±45) | ±90 | EJ `pan` | güvenli taraf (kod daha dar); bilgi |
| Ç6 | KY:13, SV `pca_yaz` | servo orta (1500 µs) = robot 90; sıfır kayması yok | S1 horn servo 45°'de kol aşağıda; dirsek servo orta = 52,5° | OR:111, AY:175, DR:239 | **CAD talimatıyla takılıp bugünkü kodla sürülürse:** omuz 0 komutu S1 −45, dirsek 0 komutu dirsek −37,5 olur (dirsek alt sınırı 0 çatal dayanağı: EJ `r_dirsek.neden`). Uyarı: "S1 −45 = kol 45° geriye" yorumu servonun dönüş yönünün S1'in + yönüyle aynı olduğunu varsayar (AY:175 aralık eşlemesinden; sağ kol için tutarlı). OR:111 taraf belirtmiyor: sol kolda (aynalı) horn açısı ve yön montajda doğrulanmalı (EJ `sol_isaret` "tahmini") |
| Ç7 | `bosta.yaml:7–8`, JV:53 | boşta omuz 10, dirsek 15 | ev pozu S1 0, S2 5, dirsek 0, bilek 0 | OM:35, AY:478 | rampa kuralı "kollar ev pozunda" (YP:62); devrilme payları CAD ev pozuyla hesaplı (EJ `teker.not_`). Boşta pozunun paya etkisi **hesaplanmadı** |
| Ç8 | `selam.yaml:8, 15`; `isaret.yaml:29–30` | `sag_omuz: 150` | S1 ≤ 135 | EJ `r_s1.max` | sınır daraltılınca `jest_uret.py` kareyi reddeder (`main:kod/jestler/jest_uret.py:111–112`; genel kural KY:19) ya da SV kırpar |
| Ç9 | `evet.yaml:7, 9` | `kafa_tilt: 75` (= CAD +15) | tilt ≤ +13 | EJ `tilt.max` | çakışma payını yiyor |
| Ç10 | JV:9 | `SERVO_SAYISI 6` | 10 servo | README.md:39, YP:31 | S2 ve bilek sürülmüyor |
| Ç11 | KY:46–47 | sol omuz 2, sol dirsek 3 | 0–4 hat A (sağ kol + pan), 5–9 hat B (sol kol + tilt) | EL:455; blokların içeriği EL:105 ("A = sağ kol + pan, B = sol kol + tilt") ve EL:181–182 (hat tablosu); EL:97: kafa servolarının beslemesi sonradan C hattına geçti, kanal numaraları aynı | kablaj düzeni; KY:5 "sol kol kanalları önerilen, kablajda doğrula" diyor |

**Belge ↔ belge (kodla ilgisiz, bilgi):** brief, `dongu-158.md:87` (P2.1) ve OR:122 S2 alt sınırını **+3°** (C1, 14.10) diyor;
güncel kaynak **+5°** (AY:176 "0 → +3 (C1, 14 Ekim) → +5 (S1 kablo kaseti, 15 Ekim 2026)", EJ `r_s2.min`, README.md:43). Tabloda +5 kullanıldı.

## 3. Kanal düzeni: iki seçenek

| Kanal | Seçenek 1 (brief: 0–5 aynen, yeni 4 → 6–9) | Seçenek 2 (EL:455 bloklarına uyar) |
|---|---|---|
| 0–1 | sag_omuz, sag_dirsek | sag_omuz, sag_dirsek |
| 2–3 | sol_omuz, sol_dirsek | **sag_omuz_yana, sag_bilek** |
| 4–5 | kafa_pan, kafa_tilt | kafa_pan, kafa_tilt |
| 6–7 | sag_omuz_yana, sag_bilek | **sol_omuz, sol_dirsek** |
| 8–9 | sol_omuz_yana, sol_bilek | sol_omuz_yana, sol_bilek |
| Değişen eski kanal | 0 | 2 (sol_omuz 2 → 6, sol_dirsek 3 → 7) |

Seçenek 2'de sağ kol + pan 0–4, sol kol + tilt 5–9 olur (EL:455). Kanal numarası elektrik için zorunlu görünmüyor: servo gücü dağıtım kartından gelir,
PCA9685'ten yalnız sinyal köprüsü gider (EL:193); bu bir çıkarım, kablajı yapan teyit etmeli.

## 4. Efe'ye uygulanacak değişiklik listesi (kod yazılmadı, yalnız madde)

1. KY'ye 4 kanal (`sag_omuz_yana`, `sag_bilek`, `sol_omuz_yana`, `sol_bilek`), `SERVO_SAYISI` 10 (JV `jest_uret.py` ile yeniden üretilir). Kanal numaraları §3'teki seçime göre.
2. Omuz modeli `DS3218` → `DS3235` (KY:44, 46 ve KY:38 açıklaması). DS3235'in darbe aralığı (`min_us` / `max_us`) depodaki kaynaklarda **yok**: servo gelince ölçülür.
3. Sınırlar EJ'den: S1 −45 … 135 (kod biriminde 0 … 180, kod = CAD + 45), S2 5 … 120, dirsek 0 … 105, bilek −90 … 90 (kod biriminde 0 … 180,
   kod = CAD + 90), pan ±90 (kodun ±45'i kalabilir), tilt ±13 (kod biriminde 77 … 103). Kod birimindeki bütün sınırlar `jest_uret.py:63` şartına (0 … 180) uyar.
   YP:67–68 "sınırlar elle iki yerde yazılmaz" diyor; bunun için EJ'nin `main`'e girmesi ve KY'nin (ya da C başlığının) EJ'den üretilmesi gerekir.
4. Servo sıfırı (Ç6), üç yol:
   (a) kod birimi kaydırılır: omuz kod = CAD + 45, bilek kod = CAD + 90 (§1); dirsek için aynı mantıkla kod = CAD + 37,5 (DR:239'dan hesap). Sıfır kayması alanı
   gerekmez, KY:13 montaj kuralı korunur; ama KY:9–10 tanımları ve jestlerin omuz / dirsek değerleri kayar.
   (b) KY / SV'ye eklem başına sıfır kayması alanı (S1 45°, dirsek 37,5°; bilek, pan, tilt 0; S2 belirsiz); kod birimi ve jestler aynı kalır, S1 −45 için yine (a) ya da
   `jest_uret.py:63` şartının değişmesi gerekir.
   (c) Horn'lar KY:13 kuralına göre takılır ve CAD montaj talimatı (OR:111, DR:239) değişir.
   Aynı anda yalnız biri geçerli olabilir. YP:76 (Y2) zaten "servo başına kalibrasyon (sıfır kayması)" diyor. Hangi yol seçilirse seçilsin sol kolda horn açısı
   ve dönüş yönü montajda doğrulanmalı (OR:111 taraf belirtmiyor; EJ `sol_isaret` tahmini).
5. Bağımlı sınır: S1 ≥ 120 iken S2 ≤ 117, iki kolda (EJ `bagimli`). Kodda bağımlı sınır yapısı yok.
6. Ev pozu: S2 açılışta ve boştayken 5'te; 0'a hiç komut gitmez (OR:122, güncel alt sınır 5). Rampa / eğim kuralındaki "ev pozu" CAD ev pozu mu, boşta pozu mu: netleşmeli (Ç7).
7. Jestler: `selam`, `isaret` (arka) S1 150 → CAD biriminde ≤ 135 (seçenek a'da kod ≤ 180; mevcut 150 + 45 = 195 olacağı için yeniden yazılır); `evet` tilt 75 → ≥ 77 (kod birimi). S2 ve bilek sütunu eklenince mevcut jestlerde bu iki kanal `ACI_YOK` kalabilir.
8. Yeni sol kanallar `ters: true` (EJ `sol_isaret` −1, tahmini); montajdan sonra her servo tek tek doğrulanır.
9. Yeni 4 kanalın `hiz` değeri için kaynak yok; Efe belirler.
10. Adlar: YP:44 `jnt` mesajı EJ adlarını (`r_s1` …), kod KY adlarını (`sag_omuz` …) kullanıyor. Tablodaki eşleme ya kodda tutulur ya da tek ad setine geçilir.
11. EL:455 ile kanal düzeni (§3) Efe ve kablajı yapanla birlikte seçilir.

## 5. Açık noktalar

- **S2 horn açısı:** OR:114 "S2'yi 30° konumuna getir, horn'u tak" diyor ama kolun o anki yana açma açısını yazmıyor. S2 sıfır kayması bu yüzden belirsiz; montaj talimatına kol pozu eklenmeli (Ahmet / CAD).
- **K9 (karar kuyruğu):** el yükü 0,5 kg için servo değişimi seçilirse "Servo" sütunu değişir (`planlama/d158/karar-kuyrugu.md`, K9: "Bloke: … P5.1 (servo modeli sütunu)").
- **1,58 m:** kol eklemleri 1,58 m'de değişmedi (AY:22–23: yalnız düz gövde bandı kısaldı, omuz, kollar ve kafa rijit olarak 70 mm aşağı indi); servo payları 1,58 m'de yeniden ölçülmedi (P3.2).
