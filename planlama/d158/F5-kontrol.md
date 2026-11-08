# F5 bağımsız kontrol (ajan B) — 08.11.2026

Dal `lale-duzeltme`. Kontrol edilen: `servo-10-oneri.md`, `kablo-kurali-notu.md`, `F5-pano-taslak.md` (+ `F5-gunluk.md`). Ölçüt: `F5-brief.md`.
Her hücre kaynaktan yeniden okundu (AY, EJ, KY, JV, SV, jest YAML'leri `git show main:` ile; CAD betikleri yalnız okundu, koşturulmadı).
Yazılan tek dosya bu. Commit / push / pano yok.

## Özet

| Paket | Sonuç |
|---|---|
| P5.1 `servo-10-oneri.md` | **KOŞULLU**: 10 satırın sayıları doğru, horn iddiası doğru; bilek için önerilen kod birimi mevcut üreticide yazılamaz, 2 atıf düzeltmesi var |
| P5.2 `kablo-kurali-notu.md` | **KOŞULLU**: 5 kablo, boylar ve %44,8 doğru, 4 soru; bir atıf kaymış ve kesişme cümlesi yanlış anlatılmış |
| P5.3 `F5-pano-taslak.md` | **GEÇER**: 1.563 karakter, karar yok, yalnız "Efe"; iddiaları belgelerle aynı (2 isteğe bağlı ifade önerisi) |

## 1. Servo tablosu: hücre hücre

**Sınırlar (AY ↔ EJ, 10 eklem):** S1 −45…135 (AY:175, EJ `r_s1`/`l_s1`), S2 5…120 (AY:176, EJ `r_s2`/`l_s2`), dirsek 0…105 (AY:504),
bilek −90…90 (AY:509), pan ±90 (AY:579), tilt ±13 (AY:582). EJ'deki 10 eklem AY ile birebir aynı. Bağımlı sınır EJ `bagimli[0..1]`
(S1 120…135 → S2 5…117) doğru. **Doğru.**

**Ev pozu:** S1 0 / S2 = yana alt sınırı (OM:35–38, `EV_TH = yana_aralik[0]` = 5); dirsek 0, bilek 0 (AY:478); pan 0, tilt 0 (AY:522). **Doğru.**

**Servo modeli:** DS3235 S1 ve S2 (AY:179, AY:182; karar 24.10 AY:180–181; README.md:39); `planlama/maliyet.json:47` DS3235 180°, :46 DS3218MG
"ver v1,v2"; MG996R dirsek/bilek (AY:505), pan/tilt (AY:583), maliyet.json:48 adet 6. **Doğru.**

**Kanal ve mevcut kod:** KY:44–49 = JV:44–49 (kanal 0–5, omuz DS3218 0…160, dirsek 0…110, pan 45…135, tilt 70…110, sol `ters: true`); JV:9
`SERVO_SAYISI 6`; boşta 10/15/90/90 `bosta.yaml:7–8` = JV:53. Sonar 10–12 (YP:31, YP:65, EL:455). **Doğru.**

**S2 alt sınırı: +5° güncel.** AY:176 "0 → +3 (C1, 14 Ekim) → +5 (S1 kablo kaseti, 15 Ekim)" satırı `git blame` ile 834b386 (18.10.2026);
OR:122'deki "+3°" a158211 (15.10.2026), yani daha eski. EJ +5 (59367ab, 29.10.2026), README.md:43 "S2 ≥ +5°". +3 diyen brief
ve `dongu-158.md:87` (P2.1) eski. Belgenin seçimi (+5) doğru. Plan satırı P2.1 düzeltilmeli; F5'in dışında, orkestratöre bilgi.

**Kod ↔ CAD açı çevrimi:** KY:9–12 ile AY:503 / 578 / 581 karşılaştırıldı. Omuz ve dirsek için kod = CAD, pan ve tilt için kod = 90 − CAD.
Kod tilt 70…110 = CAD +20…−20, ±13 = 77…103; pan 45…135 = CAD +45…−45. Omuz yönü: `montaj/eklem-dogrulama.json` `yon[0]`
(S1 +90 → el ucu y +140,3, z +139,8). **Doğru.**

## 2. "Horn sıfırı" iddiası (Efe'ye gidecek): DOĞRU

- **Omuz:** OR:111 "S1'i 45° konumuna getir …, horn'u kol aşağıdayken tak" (2306e54, 07.10). AY:175 "horn kol asagidayken 45'te" ve aralık −45…135
  (a158211, 15.10'dan beri aynı; b1f9547'de yalnız model adı değişti). Servo 0…180 ↔ S1 −45…135 eşleşiyor, yani servo orta 90 = S1 45. ✔
- **Dirsek:** DR:239 "Dirsek servosunu orta konuma (90) getir. Horn'u ön kol dirsek %s°'deyken tak" ve `ar = DI["aralik"]` (DR:100),
  `DI = A.DIRSEK` (DR:15), aralık (0, 105) (AY:504). (0 + 105) / 2 = 52,5. ✔
- **Bilek / pan / tilt:** DR:237 (bilek orta, avuç içe), KM:861 (servo orta = pan 0), KR:220 (horn'lar orta konumda = ev pozu). ✔
- **Kod tarafı:** KY:13 "servo merkezdeyken (1500 us) korna, robot açısı 90'a denk gelecek şekilde takılır". SV:38–39 servo açısı = robot açısı
  (`ters` hariç), sıfır kayması alanı yok. Ç6 doğru: CAD'e göre takılır, bugünkü kodla sürülürse omuz 0 → servo 0 → S1 −45, dirsek 0 →
  dirsek −37,5 olur.
- **Çıkarım uyarısı (bilgi):** "omuz 0 komutu kolu 45° geriye götürür" ifadesi servo dönüş yönünün S1'in + yönüyle aynı olduğunu varsayıyor.
  Bu varsayım AY:175'teki aralık eşlemesinden çıkıyor ve sağ kol için tutarlı. OR:111 taraf belirtmiyor: sol kolda (aynalı) horn açısı ve
  yönü montajda doğrulanmalı (EJ `sol_isaret` "tahmini").

## 3. Tilt, jest ve omuz iddiaları: DOĞRU

- Tilt kod ±20 (KY:49, JV:49) ↔ CAD ±13 (AY:582; ilk çakışma +18 / −17). ✔
- `evet.yaml:7, 9` `kafa_tilt: 75` = CAD +15 > +13. ✔ (`evet.yaml:8, 10` 95 = −5, sınır içinde.)
- Omuz 160 (KY:44, 46) ↔ 135 (EJ `r_s1.max`). ✔
- `selam.yaml:8, 15` ve `isaret.yaml:29–30` (arka varyantı) `sag_omuz: 150`. ✔

## 4. Kablo notu

- **Eski kural:** `0b8a245^:planlama/yazilim-plani.md:64` "HDMI ve CSI boyundan geçmez", :124 Nextion / "boyundan ayrı sinyal geçmez". ✔
  0b8a245 commit mesajındaki "05.11 B + R1 … henüz yok: P4.1" alıntısı ✔.
- **5 kablo:** KYE:6 (HDMI, hub uzatması, hoparlör, 12 V, tilt). LK `mevcut` 12 V 10,6 + tilt 5,9 mm²; HDMI Ø6, hub ve hoparlör Ø4.
  Toplam 10,6 + 5,9 + 28,27 + 12,57 + 12,57 = 69,97 → LK `boyun_demet_alan_mm2` 69,9. Seti doğruluyor. ✔
- **Boylar:** LK `kablo` HDMI 757/950, hub uzatması 617/920 (+150), hoparlör 823/1.030; boyundan geçmeyen dokunmatik 395/640, ESP32 971/1.360,
  12 V 1.376/1.720. `uygulama-olcum.json` `kablo_listesi` aynı. Kural yol × 1,25 (+150) AY:1003. ✔
- **%44,8:** LK `gecis` "Servo yuvası arka kanalı 20 × 7,8" 156 mm², doluluk 0,448 (= 69,9 / 156); mil penceresi 0,399, alt çıkış 0,343. ✔
- **Diğer atıflar:** KYE:7, 19, 21, 23, 127 (+134: yüz HDMI şeridi `hdmi0`'a), AY:997, EL:17, 19, 21, 29, 30, 38, 44, 50–51, 56, 242, 267, 272,
  YP:52, 63–64, 124, `main:kod/ayarlar.yaml:36` ✔.
- **Soru sayısı:** 4 ✔.

## 5. Pano taslağı

- Çizgiler arası 1.563 karakter (satır sonları hariç 1.545), LF. Sınır 1.800. ✔
- KARAR yok: "karar senin" ve "Öneri:" geçiyor, hüküm cümlesi yok. ✔ Kişi adı yalnız "Efe", takma ad yok. ✔
- İddialar §1–§4 ile aynı (11 fark, DS3218↔DS3235, 160/150↔135, tilt ±20↔±13 ve 75, dirsek 110↔105, horn 45° / 52,5°, S2 ≥ 5 ve ≤ 117,
  5 kablo, ~950 mm, HDMI0/HDMI1, 1280×720 ↔ 1280×800, vc4hdmi0). ✔ Sorular a–b servo §4 madde 4 ve 11; c–f kablo notunun 4 sorusu.

## Bulgular (düzeltme gerektiren)

| # | Belge | Bulgu | Kaynak |
|---|---|---|---|
| B1 | servo §1 çevrim tablosu ("S2, bilek: kod = CAD … −90 … 90") ve §4 madde 3 | Bilek −90…90 mevcut üreticide **yazılamaz**: `jest_uret.py:63` `0 <= min_aci < max_aci <= 180` şartını zorunlu tutuyor, SV:38–39'da servo açısı < 0 olur. Belge bu sorunu yalnız S1 için not etmiş (satır 68). | `main:kod/jestler/jest_uret.py:63–64`; SV:38–39 |
| B2 | servo satır 68 | S1 −45 notu yalnız SV formülüne dayanıyor. Engel daha önce üreticide çıkıyor (`jest_uret.py:63`, min_aci < 0 reddedilir). | aynı |
| B3 | servo Ç8 | "`jest_uret.py` reddeder (KY:33)" atfı yanlış. KY:33 yalnız ayna varyantını anlatıyor. Kare açısını reddeden `jest_uret.py:111–112`; genel kural KY:19. | KY:19, 33; `jest_uret.py:111–112` |
| B4 | kablo "Yollar kesin değil" | Atıf `planlama/dongu-158.md:161` kaymış: çalışma kopyasında o satır F5 günlüğü, sayılar :163'te. O satır da bir günlük satırı, birincil kaynak değil. Birincil kaynak LK `kablo_tup_cakisma` (`lale158-kontrol.json:392`). | `dongu-158.md:161, 163`; LK |
| B5 | kablo, aynı cümle | "şema yolları kablo tüpüyle kesişiyor" ifadesi yanlış. Doğrusu: kablo tüpleri **göğüs ekranı kasasıyla** kesişiyor (HDMI 897,1, 12 V 617,3, USB dokunmatik 167,6 mm³; parça adı "Gogus ekrani 11,6 in HDMI … kasali"). | LK `kablo_tup_cakisma` |
| B6 | kablo, boyun bölümü | Boyundaki kesişmeler not edilmemiş: HDMI × boyun mili 15,1 ve × servo yuvası 1,7; hub uzatması × boyun mili 1,2; hoparlör × boyun mili 1,2 mm³. LK `kablo_tup_notu` bunlar için "mil / servo yuvası varsa o kablo geçişi elle bakılmalı" diyor. | LK `kablo_tup_cakisma`, `kablo_tup_notu` |
| B7 | kablo, yazılım etkisi 1 | `main:kod/ayarlar.yaml:39–40` → **:40–41** (genişlik 1280, yükseklik 800; 39 `etkin`). | `ayarlar.yaml:39–41` |
| B8 | kablo, B4 cümlesi | "P1.4 yolu değiştirecek": P1.4'ün tanımı (`dongu-158.md:78`) yalnız USB dokunmatik ↔ SY8205'i (249,7 mm³) kapsıyor. Göğüs ekranı kesişmeleri P1.4'e yalnız F0 günlüğünde bağlanmış (:163). | `dongu-158.md:78, 163` |
| B9 | servo Ç11 / §3 (bilgi) | EL:455 tek başına hangi kafa servosunun hangi blokta olduğunu söylemiyor. "A = sağ kol + pan, B = sol kol + tilt" EL:105 ve EL:181–182'de açıkça yazılı; atıfa eklenebilir. | EL:105, 181–182 |

## Numaralı düzeltme listesi (ajan A için)

1. **(B1)** `servo-10-oneri.md` §1 çevrim tablosunda bilek satırı "kod = CAD + 90 (0 … 180); servo orta = bilek 0, KY:13 montaj kuralıyla uyumlu, sıfır kayması gerekmez" olsun. S2 satırı "kod = CAD (5 … 120)" olarak ayrı kalsın. §4 madde 3'te bilek "kod biriminde 0 … 180" diye yazılsın.
2. **(B2)** Satır 68'e "`jest_uret.py:63` min_aci < 0 kabul etmez" eklensin.
3. **(B3)** Ç8 risk hücresi: "KY:33" → "`jest_uret.py:111–112` (KY:19)".
4. **(B4 + B5)** `kablo-kurali-notu.md` "Yollar kesin değil" cümlesi şöyle olsun: "göğüsteki şema yollarının kablo tüpleri göğüs ekranı kasasıyla kesişiyor (HDMI 897,1 / 12 V 617,3 / USB dokunmatik 167,6 mm³, LK `kablo_tup_cakisma`)".
5. **(B6)** Aynı nota bir satır eklensin: boyunda HDMI × boyun mili 15,1, × servo yuvası 1,7; hub uzatması ve hoparlör × boyun mili 1,2 mm³. LK `kablo_tup_notu` gereği bu geçişler elle bakılacak.
6. **(B7)** `ayarlar.yaml:39–40` → `:40–41`.
7. **(B8)** "P1.4 yolu değiştirecek" → "F0 günlüğünde P1.4'e bağlandı (`dongu-158.md:163`); P1.4 tanımı (:78) şimdilik yalnız USB dokunmatik ↔ SY8205".
8. **(B9, isteğe bağlı)** Ç11 kaynak hücresine EL:105, EL:181–182 eklensin.
9. **(isteğe bağlı, pano)** "evet jestindeki 75 sınır dışı" → "evet jestindeki 75 (= +15°) CAD sınırı dışı"; "kuralı CAD'de artık yok" → "CAD bu kurala artık uymuyor". İkisi de yanlış değil; ilki bugünkü kod sınırı (70) içinde kaldığı için belirsiz okunabilir.
10. **(F5 dışı, orkestratöre)** `dongu-158.md:87` (P2.1) ve F5 brief'i S2 alt sınırını +3° diyor; güncel +5° (AY:176 18.10 > OR:122 15.10; EJ, README.md:43). OR:122 metni de +3° anlatıyor (CAD rapor betiği; Ahmet / CAD tarafı).

Düzeltmeler pano metnini değiştirmiyor (B1–B8 pano taslağında geçmiyor).

## Genel karar

**KOŞULLU.** Efe'ye gidecek kritik iddialar kaynakla birebir tutuyor: horn sıfırı (OR:111, DR:239, AY:175), sınırlar, modeller, jest değerleri, 5 kablo, boylar ve %44,8.
Madde 1–7 düzeltilince P5.1 ve P5.2 GEÇER olur. Pano taslağı bugünkü haliyle GEÇER. Yeniden kontrol için yalnız 1–7'nin uygulandığına bakmak yeterli.

---

## Yeniden kontrol 1 (düzeltme turu 1 + pano hizalaması)

Belgeler yeniden okundu; atıflar ve sayılar kaynaktan tekrar doğrulandı (günlükteki "doğrulandı" notlarına dayanılmadı).

| Paket | Sonuç |
|---|---|
| P5.1 `servo-10-oneri.md` | **KOŞULLU** (iki küçük tutarlılık düzeltmesi: R2, R3) |
| P5.2 `kablo-kurali-notu.md` | **GEÇER** (R4 isteğe bağlı) |
| P5.3 `F5-pano-taslak.md` | **KOŞULLU** (R1: (a) sorusu belgeden eksik) |

**Madde 1–6 uygulandı mı:**
1. ✔ Bilek kod = CAD + 90 (0 … 180): servo §1 satır 67, 72; §4 madde 3.
2. ✔ `jest_uret.py:63` notu: satır 69–71.
3. ✔ Ç8 atfı `jest_uret.py:111–112` (KY:19).
4. ✔ Kesişme göğüs ekranı kasasıyla, kaynak `lale158-kontrol.json:392` (satır doğru: `"kablo_tup_cakisma": {`). P1.4 ifadesi kaldırıldı ("ayrıca ölçülecek").
5. ✔ Boyun içi kesişmeler HDMI × mil 15,1, × servo yuvası 1,7; hub × mil 1,2; hoparlör × mil 1,2. LK `kablo_tup_cakisma` ile birebir aynı.
   12 V ve tilt tüp değil, yalnız kesit (KYE:32 `MEVCUT`): doğru. `kablo_tup_notu` `lale158-kontrol.json:456`: satır doğru.
6. ✔ `ayarlar.yaml:40–41`.
Ek olarak horn uyarısı Ç6'ya ve §4 madde 4'e, EL:105 / 181–182 Ç11'e eklenmiş (doğru).

**Yeni kod birimleri ↔ `jest_uret.py` ↔ mevcut jestler:**
- **Omuz kod = CAD + 45:** −45 … 135 → 0 … 180, `jest_uret.py:63` ile uyumlu. Kod 90 = S1 45 = servo orta (OR:111), KY:13 korunur. ✔
  Mevcut jest omuz değerleri {10, 70, 90, 150} → {55, 115, 135, 195}. 195, `jest_uret.py:111–112` ile reddedilir; bu Ç8'in aynısı, yeni sorun değil.
- **Bilek kod = CAD + 90:** 0 … 180; servo orta = bilek 0 (DR:237) = kod 90. ✔ Mevcut jestlerde bilek yok.
- **Dirsek kod = CAD + 37,5** (§4 madde 4a): 0 … 105 → 37,5 … 142,5, şartla uyumlu. Kod 90 = dirsek 52,5 = servo orta (DR:239). ✔
  Mevcut dirsek değerleri {0, 15, 40, 80, 90} → {37,5, 52,5, 77,5, 117,5, 127,5}, hepsi aralıkta. Ondalık değer sorun değil: üretici int/float kabul ediyor (`jest_uret.py:111`), JV float.
- §4 madde 4(b)'deki "S1 −45 için yine (a) ya da `jest_uret.py:63` değişmeli" doğru.

**Pano:** çizgiler arası **1.701** karakter (satır sonları hariç 1.683), ≤ 1.800 ✔. Karar yok ("karar senin", "Öneri:", soru biçimi) ✔.
Kişi adı yalnız "Efe" ✔. "45° geriye … (servo yönü varsayımıyla; sol kolda yön montajda doğrulanmalı)" belgeyle (Ç6) aynı ✔. Diğer sayılar değişmedi ✔.

**Kalan maddeler:**
- **R1 (pano ↔ belge):** (a) sorusu "kod birimi kaydırılsın mı (omuz CAD + 45, bilek CAD + 90)" diyor. Belgedeki (a) ise dirseği de kapsıyor
  (§4 madde 4a: dirsek CAD + 37,5), ve Ç6'nın dirsek yarısını çözen o. Pano bu haliyle (a)'yı yalnız omuz çözümü gibi okutuyor.
  Düzeltme: "(omuz CAD + 45, dirsek CAD + 37,5, bilek CAD + 90)". Yaklaşık +20 karakter, toplam ~1.720, sınır içinde.
- **R2 (servo §1 ↔ §4):** çevrim tablosunda dirsek satırı (63) koşulsuz "kod = CAD, 0 … 105" diyor; §4(a) ise CAD + 37,5 öneriyor.
  Dirsek satırına "(a) seçilirse kod = CAD + 37,5 → 37,5 … 142,5" eklenmeli.
- **R3 (servo §4 madde 7):** "S1 150 → ≤ 135" biriminin belirtilmesi gerekiyor. (a)'da kod sınırı 180'dir: kod 150 = CAD 105 geçerli olur, mevcut 150 ise +45 kayınca 195 olur.
  Düzeltme: "S1 CAD biriminde ≤ 135 (seçenek a'da kod ≤ 180; mevcut 150 → 195 olacağı için yeniden yazılır)".
- **R4 (isteğe bağlı, kablo satır 40):** tırnak içindeki `kablo_tup_notu` metni kaynağın birebir alıntısı değil ("rulman yuvası" eksik). Ya tam alıntı yapılmalı ya tırnak kaldırılmalı.
- Önceki madde 10 (`dongu-158.md:87` / brief'teki +3°): orkestratörde, F5 belgelerini etkilemiyor.

**Genel karar (yeniden kontrol 1): KOŞULLU.** Kaynak ve sayı hatası kalmadı. R1–R3 üç kısa metin düzeltmesi.
Uygulandıklarında P5.1 ve P5.3 GEÇER olur; yeniden kontrol için yalnız bu üç satıra ve pano karakter sayısına (≤ 1.800) bakmak yeterli.

---

## Yeniden kontrol 2 (düzeltme turu 2: R1–R4)

- **R1 ✔** Pano (a) sorusu (`F5-pano-taslak.md:19`): "(omuz CAD + 45, dirsek CAD + 37,5, bilek CAD + 90)". Servo §4 madde 4(a) ile aynı.
- **R2 ✔** Servo §1 çevrim tablosu dirsek satırı (`servo-10-oneri.md:63`): "kod = CAD; §4 madde 4 seçenek (a) seçilirse kod = CAD + 37,5", sınır "0 … 105; (a)'da 37,5 … 142,5".
- **R3 ✔** Servo §4 madde 7 (`servo-10-oneri.md:126`): "CAD biriminde ≤ 135 (seçenek a'da kod ≤ 180; mevcut 150 + 45 = 195 …)". Hesap doğru.
- **R4 ✔** Kablo notu satır 40: "Listede rulman yuvasi, servo yuvasi, mil varsa o kablo gecisi elle bakilmali." `lale158-kontrol.json` `kablo_tup_notu` içinde birebir geçiyor (programla karşılaştırıldı).
- **Pano karakter sayısı ✔** Çizgiler arası **1.720** (satır sonları hariç 1.702); iddia ile aynı, ≤ 1.800. Karar yok, kişi adı yalnız "Efe" (yeniden tarandı).

| Paket | Son karar |
|---|---|
| P5.1 `servo-10-oneri.md` | **GEÇER** |
| P5.2 `kablo-kurali-notu.md` | **GEÇER** |
| P5.3 `F5-pano-taslak.md` | **GEÇER** (gönderilmedi) |

**Genel karar: GEÇER.** Kalan madde yok. F5 dışı tek not hâlâ açık: `dongu-158.md:87` (P2.1) ve brief S2 alt sınırını +3° diyor, güncel +5° (orkestratör).
