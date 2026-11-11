# F10d kontrolü (alt adımlar, kabuk adımlarının bölünmesi, takma yönleri, görünürlük): bağımsız kontrol ajanı B, 11.11.2026

Kontrol edilenler:
- `F10d-brief.md`;
- `F10d-gunluk.md` ve `F10d-dogrula.py`: iddia olarak okundu;
- `git diff HEAD` (`tasarim/freecad/rehber/`, `rehber/app.js`, `rehber/veri/`, `planlama/rehber/kontrol.json`, PDF);
- `F10d-dogrula.json`, `F10d-gizli-piksel.json`, `F10d-goruntu-*.png`.

Esas: çalışma ağacı, dal `lale-duzeltme`, HEAD `10b60d6`, commit yok. Asıl soru Ahmet'in şikâyetiydi: "adım 31 ve 33'te neyin
nereye monte edildiği pek anlaşılmıyor (kabuk montajının tamamında)". Sayılar geçse bile bu çözülmediyse paket geçmez.

Kendi ölçümlerim scratchpad'de (`scratchpad/f10d-b/`). A'nın ölçü fonksiyonlarını kullanmadım:
- **Kareler.** `kare.py`, başsız Chrome, çalışma ağacı ve HEAD kopyası, açık + koyu tema. Kendi kimlik tamponum ayrı bir
  `WebGLRenderer`'da, üç kipte:
  - sert: her parça örter;
  - yumuşak: saydam çizilen parça örtmez;
  - yalnız: parça tek başına çizilir.
  Mini görünüm ve lejant dışarıda.
- **Hacimsel süpürme.** F10c-kontrolündeki `supur.py`: yüzeyden 0,15 mm içeri kaydırılmış noktalar karşı katının içinde mi, iki yönlü
  parite. Dinlenmedeki (yerindeyken) ortak nokta sayısı her yönde çıkarılır; **≥ 5 nokta artışı çarpışmadır**. Temas ve ortak yüz
  çarpışma değildir.
- **Gerçek nokta–üçgen derinliği.** `k3c.py`.
- **Isıl gömme ev sahibi taraması.** `k2c.py`: somun hangi parçanın malzemesinin içinde?
- **Gezinme.** `gez.py`.
- **PDF sayfaları.** PyMuPDF.

Yazdığım tek depo dosyası bu dosya. Commit, push, silme, checkout, reset, stash yok. Üretici ve `F10a-dogrula.py` /
`F10d-dogrula.py` koşulmadı. FreeCAD açılmadı; kilit baştan sona "boş" kaldı. Koşulanlar:
- `F9b-dogrula`;
- `carpisma_kos kontrol`;
- `regresyon.py --yazma`.

Bu üçü depoya yazmıyor. Arka planda iş kalmadı.

## Karar: **DÜZELTME GEREKLİ**

Engelleyen 3, engellemeyen 9 bulgu.

- **Şikâyet büyük ölçüde çözüldü, tamamen değil.** HEAD'de adım 31 ve 33 tek karede yalnız dış kabuğu gösteriyordu. Şimdi 37 kabuk
  alt adımının 29'u açık. İç parçalar kabuk kapanmadan önce kendi karelerinde görünüyor; masa / bağla ayrımı okunuyor. Bu gerçek bir
  iyileşme.
- **İki alt adım anlaşılmıyor:** alt adımın konusu kendi karesinde 0 piksel (B-1).
  - 34.4: hoparlör grubu.
  - 35.4: VESA cıvataları ve pulları.
- **Altı alt adım zor** (B-1).
- **Isıl gömme ev sahibi yanlış (B-2).** 34 ısıl gömme somun yanlış parçaya bağlı ya da hiç bağlı değil:
  - 26'sının ev sahibi yanlış;
  - 8'i ev sahipsiz.
  Bu yüzden:
  - 49.1 okura somunları kapağa taktırıyor;
  - somunlar yanlış parçayla uçuyor;
  - A'nın K1 ve K3 gerekçelerinin bir kısmı bu hatadan doğuyor.
- **Masa kipi başka adımların kablolarını havada çiziyor (B-3).** 33.5, 33.8, 34.4 ve 49.1 karelerini kirletiyor. Kaynak `app.js`
  `semaDurum`. A bunu yalnız 34.4 için "F10e'ye not" diye geçmiş; anlaşılırlığı doğrudan bozduğu için engelleyen.
- **Doğru olanlar:**
  - yapı: 1192 ↔ 1192, taşınan 0, `robot.glb` aynı, E4 sırası F10c'deki gibi;
  - gezinme ve adresleme;
  - yazdırma (66 sayfa, 95 görüntü, boş 0);
  - devredilen küçükler;
  - F9b, çarpışma ve regresyon çıkışları.

## Anlaşılırlık hükmü (göz; kendi karelerim, açık + koyu)

37 kabuk alt adımı: **açık 29 · zor 6 · anlaşılmıyor 2.** Koyu temaya özgü sorun yok; iki temada da hüküm aynı.

| alt adım | hüküm | neden |
|---|---|---|
| 31.1–31.4 | açık | Masada kabuk + ReSpeaker / ses kartı, sonra birim kafada; parçalar karenin ortasında |
| 31.5 | **zor** | Tabla → raf cıvataları. Saydam kabuklar arasında raf ayırt edilmiyor, 4 cıvata küçük, kablo öne çıkıyor |
| 31.6–31.8 | açık | Masada yüz grubu: kamera, QLED arkadan, tırnaklar |
| 31.9 | **zor** | Yüz grubu kafaya: birim belli, ama metindeki 4 kablo bağlantısı (CSI, HDMI, Power, Touch) karede yok |
| 31.10 | **zor** | 9 dikiş cıvatasının 4'ü karede 0 px (arka dikiş; yalnız kendi başına çizilince 217 px); kalanlar büyük gri kafada küçük |
| 33.1–33.4, 33.6, 33.7, 33.9 | açık | Bantlar sırayla, yön okları okunuyor. 33.6 / 33.9'da kontak / anahtar gövdesi etek altında kalıyor, ama birim bağlama anlaşılıyor |
| 33.5 | **zor** | Masada acil stop: kontak gövdesi 7 px; başka adımların kabloları havada (B-3) |
| 33.8 | **zor** | Masada ana anahtar: ince şerit; havada kablolar (B-3) |
| 34.1–34.3, 34.5, 34.6 | açık | Bantlar alttan üste. Arka dikiş cıvataları kendi karesinde 0 px; ama bant görünüyor, cıvata yeri metinden okunuyor |
| 34.4 | **anlaşılmıyor** | Hoparlör, kab ön halka, köpük ped, 1 kelepçe cıvatası 0 px (sert ve yumuşak); ızgara duvarının arkasında. Karede yalnız orta bant ve havada kablolar (B-3). A'nın JSON'u da 0 px |
| 35.1–35.3, 35.5 | açık | 35.3'te çekiç somunu kanalda görünmüyor (gerekçeli) |
| 35.4 | **anlaşılmıyor** | Yeni 9 parçanın 8'i (4 VESA cıvatası + 4 pul) 0 px. Kendi başlarına çizilince 75–352 px; demek eski parçalar örtüyor. Karede ekran ve kablolar. `F10d-gunluk.md:345` "VESA cıvataları görünür" diyor, A'nın kendi JSON'u 0 diyor |
| 36.1, 36.2 | açık | Sağ / sol omuz bandı ayrı karede |
| 49.1 | **zor** | Masada kapak + hub. Kablolar kapağın üstünden geçiyor (B-3); 7 ısıl gömme kapakta gösteriliyor, gerçekte bantta (B-2) |
| 49.2–49.5 | açık | 49.3 ile 49.4 neredeyse aynı kadraj; ayrımı küçük görünüm ve vurgu sağlıyor |

- **Benim piksel sayımım.** Kabuk alt adımları ve 21 / 25 / 43 / 45 / 46, ısıl gömmeler hariç. Yeni 283 parçanın 78'i kendi
  karesinde 0 px. Bunların çoğu beklenen durum:
  - `bag` alt adımında birimin içinde kalan parçalar (31.9'da 16, 31.2 / 31.4'te 4'er);
  - arka dikiş cıvataları.
  Beklenmeyenler 34.4 ve 35.4.
- **İki kollu adımlar** (21.x, 43.x, 45.x, 46.x) ve 25: yeni parçaların hepsi > 0 px; karelere baktım, açık.
- **Patlatma kareleri** (`?patlat=1`): yönler makul. Bir görsel tutarsızlık var: 49.5'te patlatılmış kapak cıvataları (25 mm)
  kapağın kendi patlatma mesafesinin (45–64 mm) altında kalıyor, cıvata kapağın içinden geçiyor gibi (B-11).

## İstisna hükmü

### 107 perdelenme istisnası: 74 ısıl gömme + 31 "voksel yanlış pozitif" + 2 çekiç somun

- **Isıl gömme, 74.** Gerekçe kategorik ("baskıya gömülü"); bu tek başına savunulabilir. Ama 74'ün 23'ü B-2'deki yanlış yerleşimli
  somunlar. Doğru adımlarına (33 / 34 / 35) taşındığında sayı değişir. A'nın piksel testi ısıl gömmeleri hiç ölçmüyor
  (`F10d-dogrula.py:131`).
- **Voksel yanlış pozitif, 31.** A'nın piksel yöntemi:
  - görünür eşiği "> 0 piksel" (31.8 köpük bant 4–5 px "görünür");
  - alt adımın kendi kamerasına ek olarak 9 yön.
  Benim ölçümüm:
  - 31'in 19'u alt adımın kendi karesinde görünüyor;
  - 12'si yalnız başka kameradan (arka dikiş / kapak cıvataları, 161–447 px).
  "Tamamen gizli" ölçütü yönden bağımsız tanımlı, bu yüzden 31'i de ölçüte göre gerekçeli. Ama 12'si okurun gördüğü karede yok.
- **Çekiç somun, 2.** Gerekçeli; kanalın içinde.
- **Hüküm.** 107'nin 84'ü gerekçeli: 51 ısıl gömme (ev sahibi doğru), 31 voksel, 2 çekiç. 23'ünün gerekçesi doğru ama adımı yanlış
  (B-2). "Okurun karesinde görünür" ölçütüyle sayılırsa 12 düşer.
- **Günlükte yanlış özet.** `F10d-gunluk.md:296` "kabukta görünmeyenlerin hemen hepsi ısıl gömme somun ve ince bağlantı elemanı".
  Yanlış: 34.4'te hoparlör ve kabı, 35.4'te pullar ve VESA cıvataları var (B-6).

### 25 uçuş istisnası (+ 2 giriş)

| sınıf | adet | B'nin hükmü |
|---|---|---|
| Bindirme dudağı (K1) | 8 | Göğüs bandı sağ **gerçekten kilitli**, ama ilk engel A'nın yazdığı gibi değil (K1 hükmü). Etek ön, çerçeve, omuz: **ölçülmedi**. Omuz bandında da B-2 hatası var (36: 6 somun); gerekçe yeniden ölçülmeli |
| İki parçalı yol (33.3 dolgu) | 1 | ölçülmedi |
| Yön yuvarlama | 12 | **12 / 12 gerçek eksende serbest** (`yuv.py`: uygulamanın kullandığı yuvarlanmamış `p.u`, 0,5 mm adım, h 0,3). Gerekçe doğru, ama istisna gereksiz (B-5) |
| Model girişimi (K3), uçuş | 2 | **Gerekçe yanlış.** 31.6 kamera: "dinlenmede 3,91 mm" yapay (gerçek derinlik 0,277 mm, K3). 49.4 üst arka kapak: 0,5 mm'lik çarpışma B-2'deki yanlış ev sahipli somunlardan |
| Model girişimi (K3), giriş (34.5, 49.4) | 2 | **Gerekçe yanlış:** 5,53 / 1,5 mm yapay (K3); 49.4 B-2 |
| Çekiç somun | 2 | ölçülmedi; gerekçe makul |

Hüküm:
- 25 uçuş istisnasından gerekçesi ölçümle doğrulanan 13: yuvarlama 12, K1 göğüs bandı sağ 1.
- Göğüs bandı sol için simetri varsayıldı.
- Gerekçesi yanlış olan 2: K3 uçuş.
- Ölçülmeyen 10: K1'in 7'si, iki parçalı yol 1, çekiç somun 2.

## Yön düzeltmeleri (kendi giriş ölçümüm)

Yöntem: `scratchpad/f10d-b/yon.py`. Hacimsel süpürme, 0,15 mm içeri kaydırma, 0,5 mm adım (ekran 1 mm). Dinlenmedeki ortak noktalar
çıkarılır, **≥ 5 nokta artışı çarpışma**; temas ve ortak yüz çarpışma değil. "Serbest": patlatma mesafesi + 20 mm içinde ya
çarpışma yok ya da sınır kutuları ayrılıyor. Engeller:
- robot adımında: önceki adımların hepsi + adımın önceki satırları;
- masa adımında: birimin önceki parçaları.

| adım | parça | yeni yön (A) | sonuç | eski yön (HEAD) | sonuç | hüküm |
|---|---|---|---|---|---|---|
| 21 D1c | S1 hornu sağ (`p0088`) | (1, 0, 0) | serbest (4,5 mm'de kutular ayrılıyor) | (0, 1, 0) | 0,5 mm'de S1 çıkış mili | A doğru |
| 28 E2 | tilt hornu (`p0830`) | (1, 0, 0) | serbest (134,5 mm) | (0,75, 0, 0,66) | 0,5 mm'de tilt çıkış mili | A doğru |
| 31.7 masa | QLED (`p0781`) | (0, 0, −1) | serbest (35,5 mm) | (0, 0, 1) | 0,5 mm'de yüz kabuğu sağ / sol | A doğru |
| 49.5 | H1 + H2 kapağı | (0, 1, 0) | serbest (29 mm) | (0, 0, −1) | 19,5 mm'de acil stop mantarı | A doğru |
| 35.4 | göğüs ekranı (`p0407`) | (0, 0,243, 0,97) | **ölçülmedi** (271 engel, 1 mm adım; 20 dk sınırında ilk yön bitmedi) | (0, 0, 1) | ölçülmedi | A'nın sonucu |
| (12 satır) | yuvarlama istisnaları | gerçek `p.u` | 12 / 12 serbest | – | – | B-5 |

Bağımsız olarak doğrulanan yön düzeltmesi 4 (+ 12 yuvarlama satırı); dördünde de A'nın seçtiği yön serbest, HEAD'in yönü
çarpıyor.

İlk S1 koşusu engel kümesine servoyu almadı. Tezgâh adımında servo `b` = 22 olduğu için bu sonuç kullanılmadı; servo ve mil
açıkça eklenerek (`s1b`) yeniden koşuldu.

## K1 / K2 / K3 hükümleri

### K1 (bindirme dudakları): **gerçek, gerekçe kısmen yanlış**

Ölçüm: göğüs bandı sağ, adım 35 başında, hacimsel süpürme, 2 mm örnek, `k1.py`.

| atama | yön | sonuç |
|---|---|---|
| A'nınki (somunlar bantla uçar) | +x | 0,5 mm'de yanlış ev sahipli y1005 somunları ↔ orta bant (81 / 73 / 30 nokta) |
| A'nınki | +y | 0,5 mm'de aynı somunlar + orta bant |
| düzeltilmiş (y1005 somunları orta bantta sabit) | +x | 2 mm'den 130 mm'ye kadar orta bantla artan ortak hacim (9 → 1378 nokta); 180 mm'de serbest |
| düzeltilmiş | +y | 1–8 mm orta bant (1102–2181 nokta), 12 mm perçin somunu M5, 40 mm'den sonra rulman kapağı / S1 |

- Bant düz yoldan gerçekten girmiyor. Bu dil kilidi: `kabuk_rapor.py:211-213`'te "iç yarı komşunun dış yarısının arkasına 12 mm
  dil".
- A'nın "ilk adımda dudak" ifadesi ise A'nın atamasıyla somunların çarpışması. Dudak 2 mm'den başlıyor.
- Tasarım belgesi takma sırasını ve esneterek takmayı tarif etmiyor.
- Etek ön sağ / sol, çerçeve ve omuz bandı: **ölçülmedi.**

### K2 (F5 ısıl gömmeleri): **gerçek, A'nın yazdığından geniş**

`k2c.py`: her ısıl gömme somun için malzemesinin içinde olduğu parça.

| adım | somun | A'nın ev sahibi | malzemesi | doğru adım |
|---|---|---|---|---|
| 35 | y1005 ön / arka / yan × 2 = 6 | göğüs bandı sağ / sol | gövde orta bandı sağ / sol | 34 (F2) |
| 36 | y1198 arka / ön = 6 | omuz bandı sağ / sol | göğüs bandı sağ / sol | 35 (F3) |
| 49 | arka kapak 7 | arka servis kapağı | orta bant sağ (4) / sol (3) | 34 (F2) |
| 49 | üst arka kapak 7 | üst arka servis kapağı | göğüs bandı sağ (4) / sol (3) | 35 (F3) |
| 49 | H1 / H2 8 | yok (uçmaz) | etek arka sağ (6) / sol (2) | 33 (F1) |

- Toplam 34: 26'sının ev sahibi yanlış, 8'i ev sahipsiz.
- A'nın K2'si yalnız H1 / H2 ve arka kapağın somunlarını (15) anıyor. Üst arka kapağın 7 somununu ve 35 / 36'daki 12'yi görmemiş.
- Kök neden `rehber_veri.py:361-363`: ev sahibi yalnız aynı adımın ana parçaları arasından, sınır kutusuyla seçiliyor. Somun içteki
  (önceki adımın) bandın boss'undaysa doğru parça aday listesinde yok. `:351`'deki yorum bunu "bindirmede dış bant da kutuyu içerir"
  diye biliyor, ama yalnız aynı adım içinde çözüyor.

### K3 (model girişimleri): **yapay**

Gerçek nokta–üçgen derinliği (`k3c.py`):

| çift | A (eksen ışını) | B (derinlik, en çok) |
|---|---|---|
| orta bant sağ ↔ uzatma 2 sağ | 5,53 mm | 0,28 mm (medyan 0) |
| üst arka kapak ↔ göğüs bandı sağ | 1,5 mm | 0,057 mm |
| arka servis kapağı ↔ orta bant sağ | 1,5 mm | 0,23 mm |
| kamera ↔ yüz kabuğu sağ | 3,91 mm | 0,277 mm (sol ile 0) |

- A'nın sayıları, eksen ışınının yüzeye teğet geçtiği yerdeki kiriş boyu; derinlik değil. B'nin değerleri üçgenleme düzeyinde.
- FreeCAD katı analizleri aynı çiftleri sıfır buluyor: `kabuk-analiz.json` kabuk içi 952 çift, `kafa-analiz.json` statik 498 çift,
  eşik 0,5 mm³, çakışma 0.
- `carpisma.py:246-262` modül içi çiftleri hiç taramıyor. "Tam tarama" önerisinin konusu zaten modül analizlerinde 0.
- 49.4'teki 0,5 mm'lik uçuş çarpışması K3 değil, B-2.

## Ölçüt tablosu: B ↔ A

| Ölçüt | B | A | Not |
|---|---|---|---|
| Anlaşılırlık (kabuk alt adımları) | açık 29 · zor 6 · anlaşılmıyor 2 | sınıflama yok; "boş ya da bozuk kare görmedim", 35.4 "VESA görünür" | B-1, B-6 |
| Kabuk alt adımlarında yeni parça 0 px (ısıl gömme hariç) | 78 / 283 | "hemen hepsi ısıl gömme ve ince eleman" | B-6 |
| Görünürlük sınırı (21, 25, 43, 45, 46) | hepsi > 0 px | GEÇTİ | |
| Perdelenme istisnası | 107 = 74 ısıl + 31 voksel + 2 çekiç; 84 gerekçeli, 23 yanlış adım | 107, gerekçesiz 0 | B-2 |
| Voksel istisnası kendi karesinde | 19 / 31 görünür, 12 yalnız başka kameradan | 31 / 33 en az bir kamerada | eşik > 0 px |
| Uçuş istisnası | 25 (giriş 2); doğrulanan 13, gerekçe yanlış 2, ölçülmedi 10 | 25, çarpışan 0 | |
| Yön yuvarlama 12 | gerçek eksende 12 / 12 serbest (etek bindirme ×4, kelepçe ×2, y792 yan ×2, VESA ×4) | yuvarlanınca 0,32–0,65 mm, gerçek eksende serbest | yuvarlama yalnız A'nın ölçüm aracında; `app.js:333` gerçek ekseni kullanıyor |
| Yön düzeltmeleri (kendi süpürmem, 5 + 1) | yeni yön serbest, eski yön çarpar: S1 hornu, tilt hornu, QLED, H1 / H2; göğüs ekranı ölçülmedi (zaman aşımı) | aynı | aşağıdaki tablo |
| K1 göğüs bandı | kilitli; ilk engel A'nın atamasıyla somun (0,5 mm), düzeltilmiş atamayla orta bant dili (2 mm) | kilitli, "ilk adımda dudak" | K1 hükmü |
| K2 | 34 somun (26 yanlış + 8 ev sahipsiz) | 15 (H1 / H2 + arka kapak) | B-2 |
| K3 | 0,057–0,28 mm (yapay) | 1,5–5,53 mm | K3 hükmü |
| Parça kaydı | 1192 ↔ 1192; `a` / `b` farkı 0; alan farkı yalnız `d` 330, `u` 176, `h` 137; her parça tek grupta | aynı | Referans parçaları (p1084, kablo yolları) satırda yok, doğru |
| `sira` = grupların birleşimi | 6 adımda doğru | aynı | |
| E4 sırası | F10c'deki gibi | aynı | |
| `robot.glb`, `robot-glb.js`, `vendor` | bayt aynı | aynı | |
| `app.js`'teki iki hata (sözdizimi, `takili`) | HEAD'de yok: HEAD `app.js` temiz, `takili` kapsamı doğru; A'nın kendi ara hatası | "ilk koşu: düzeltildi" | |
| Gezinme | `?adim=31.3`, `#31.3`, `#49.5`, `31`, `31.0` doğru; `31.99` → 31.10; ileri 30 → 31.0 … 31.10 → 32 → 33.0 → 33.1 ve tersi doğru; sayaç "Adım 31 / 49 · alt adım 3 / 10" | GEÇTİ (20 örnek) | B-10 |
| Dış istek / konsol / 360 px taşma | 0 / 0 / 0 (9 adres) | 0 / 0 / 0 | |
| PDF | HEAD 55 → 66 sayfa; en küçük yazı 8,1 pt; görüntüsüz 3 (19, 34, 39); 95 görüntü, hepsi çizili (en düşük oran 0,047) | 95 görüntü, boş 0 | 16 sayfaya baktım (33–37, 41, 42, 46, 49–51, 58, 61, 64–66) |
| Üreticinin yazdırma denetimi | `kontrol.json` `yazdir_goruntu` yalnız 50 kare; alt adım kareleri dışında | 50 / 50 | B-9 |
| Devredilen küçükler | 28 araç "alyan 3, 7 mm anahtar", 29 "alyan 2, yan keski": düzelmiş; "çevre'nin" 0; E3 cümlesi ölçülene indirilmiş | aynı | B-12 |
| `F9b-dogrula`, `carpisma_kos kontrol`, `regresyon --yazma` | 0 (hata 0), 0 (17 güncel), 0 (10 / 10) | aynı | B koştu |
| `F10a-dogrula`, `F10d-dogrula` | **ölçülmedi** (depoya yazdıkları için koşulmadı) | GEÇTİ | A'nın sonucu |

## Bulgular

### B-1 (engelleyen). 34.4 ve 35.4 anlaşılmıyor, 6 alt adım zor
- **Kanıt.** Kendi kimlik tamponum (`scratchpad/f10d-b/olcum.jsonl`, özet `ozet.txt`) ve kareler (`kare/`, `sheet/`).
  - 34.4: hoparlör `p0438`, kab ön halka `p0236`, köpük ped `p0443`, kelepçe cıvatası `p0440` sert ve yumuşak kipte 0 px.
  - 35.4: VESA cıvataları `p0425 / 27 / 29 / 31` ve pulları `p0424 / 26 / 28 / 30` 0 px; yalnız çizilince 75–352 px.
  - A'nın `F10d-dogrula.json`'u da bu alt adımlar için 0 veriyor. Kabuk alt adımlarında sınır olmadığı için geçmiş.
- **Yanlış yer.** Alt adım kamerası `rehber_metin.py`'deki grup `kamera` alanı: 34.4 `(-1, 0,45, 0,6)`, 35.4 `(0,85, 0,62, -1,25)`.
  `saydam` ikisinde de boş.
- **Yeniden üretme.** `?adim=34.4&cekim=1` ve `?adim=35.4&cekim=1`, ardından `RehberTest.gorunurluk()`.
- **Düzeltme önerisi:**
  - 34.4: kamera ızgaranın içinden (−z tarafından) bakmalı, ya da orta bant saydam olmalı;
  - 35.4: kamera zaten alttan-arkadan bakıyor ama VESA yüzünü taşıyıcı ve bant örtüyor; bu ikisi saydam çizilmeli.
  - Zor alt adımlar:
    - 31.5'te raf vurgusu;
    - 31.9'da kablo uçlarının gösterimi ya da metinde "karede yok" notu;
    - 31.10'da arka dikiş için ikinci kare ya da arkadan kamera;
    - 33.5 / 33.8 / 49.1'de B-3.
  - Kabul için öneri: kabuk alt adımlarında da "yeni ana parça kendi karesinde > 0 px, eşik ≥ 30 px" sınırı. İstisna yalnız `bag`
    birimi içi.

### B-2 (engelleyen). 34 ısıl gömme somunu yanlış ev sahibinde ya da ev sahipsiz
- **Kanıt.** K2 hükmündeki tablo (`scratchpad/f10d-b/k2c.log`).
- **Sonuçlar:**
  - 49.1 karesi ve `is_` metni üst arka kapağın 7 somununu kapakta gösteriyor; gerçekte göğüs bandında.
  - Somunlar kapakla birlikte uçuyor; 49.4'te 0,5 mm "K3" çarpışması bundan.
  - 35.1 / 35.2'de göğüs bandı y1005 somunlarıyla uçuyor, ilk engel olarak bunlar görünüyor (K1).
  - 36.1 / 36.2'de de aynı durum büyük olasılıkla var: ölçülmedi.
  - 23 perdelenme istisnası yanlış adımda.
- **Yanlış yer:**
  - `tasarim/freecad/rehber/rehber_veri.py:361-363`: aday listesi `ANA_ADIM[p["a"]]`;
  - `:377-391`: ev sahipsizler için yalnız "uçmaz" çaresi;
  - `F10d-gunluk.md` K2 maddesi yalnız 49'u sayıyor.
- **Yeniden üretme.** `scratchpad/f10d-b/k2c.py`: her ısıl gömme somunun iç örnek noktaları hangi parçanın katısının içinde.
- **Düzeltme önerisi (uygulamadım):**
  - aday listesine önceki adımların ana parçalarını da al; malzeme içi testi sınır kutusuna yeğle;
  - somunu ev sahibinin adımına taşı (F1 33, F2 34, F3 35);
  - 49.1 metnini düzelt;
  - sonra K1 süpürmesini, perdelenmeyi ve sıra denetimini yeniden koş.

### B-3 (engelleyen). Masa kipi başka adımların kablolarını havada çiziyor
- **Kanıt.** 33.5, 33.8, 34.4, 49.1 karelerinde masa birimiyle birlikte gövde içi kablo yolları çiziliyor. Masa karesinde robot yok;
  kablolar boşlukta.
- **Yanlış yer.** `rehber/app.js:202-206`: `semaDurum`'un alt adım kolu yalnız `s.a === adim` olan şemaları ele alıyor (masa grubunda
  "gizli"). Başka adımlardan gelen şemalar `:209-210`'a düşüp "onceki" çiziliyor.
- **Neden engelleyen.** Şikâyet "neyin nereye monte edildiği". Masa karesinde ilgisiz kablo, okura birimin parçası gibi görünüyor.
- **Düzeltme önerisi.** `if (j && ADIM[adim].alt && G[j-1].tezgah && s.a !== adim) return "gizli";`. A'nın notu
  (`F10d-gunluk.md:379`) yalnız 34.4'ü anıyor.

### B-4 (engellemeyen). K3 sayıları derinlik değil
- K3 hükmüne bakın.
- **Yanlış yer:**
  - `F10d-gunluk.md` K3 maddesi;
  - 31.6 / 34.5 / 49.4 grup `ucus_ok` / `giris_ok` metinleri ("3,91 mm", "5,53 mm", "1,5 mm").
- **Düzeltme önerisi.** Gerekçeyi "üçgenleme düzeyinde temas (≤ 0,3 mm), katı analizinde 0" diye yaz. K3'ü kuyruktan düş.

### B-5 (engellemeyen). Yön yuvarlama istisnaları A'nın ölçüm aracından doğuyor
- `rehber_sira.py:832` ve `:911` / `:977`'de yön tam sayıya yuvarlanıyor. Uygulama yuvarlanmamış `p.u` ile uçuruyor
  (`app.js:333`).
- Gerçek eksende 12 / 12 serbest (`scratchpad/f10d-b/yuv.py`, `yuv.log`). Okurun gördüğü yol çarpışmıyor; istisna
  A'nın ölçüm aracından doğuyor.
- Öneri: `ucus_yolu` yuvarlanmamış `u` ile ölçsün. 12 istisna ve gerekçe metinleri silinsin.

### B-6 (engellemeyen). Günlükte gözlemle çelişen iki cümle
- `F10d-gunluk.md:345` "35.4 ekran (…) ekran + VESA cıvataları görünür": kendi JSON'u ve benim ölçümüm 0 px.
- `:296` "kabukta görünmeyenlerin hemen hepsi ısıl gömme somun ve ince bağlantı elemanı": 34.4'te hoparlör ve kabı (ana parça).

### B-7 (engellemeyen). Piksel görünürlüğünün eşiği > 0
- `F10d-dogrula.py` görünürlüğü ve gizli piksel testi 1 pikseli "görünür" sayıyor. 31.8 köpük bandı 4–5 px'le geçiyor.
- Öneri: ≥ 30 px ve alt adımın kendi kamerası. Başka kameradan görünme bilgi olarak kalsın.

### B-8 (engellemeyen). Gizli piksel testi ısıl gömmeleri hiç ölçmüyor
- `F10d-dogrula.py:131` gerekçesinde "ısıl gömme" geçen istisnayı listeden atıyor.
- Kategorik gerekçe makul, ama B-2'deki 23 yanlış yerleşimli somunu da görünmez kılıyor.

### B-9 (engellemeyen). Üreticinin yazdırma görüntü denetimi alt adım karelerini kapsamıyor
- `planlama/rehber/kontrol.json` `yazdir_goruntu` 50 kare sayıyor; PDF'te 95 görüntü var.
- F10a-dogrula 95'i kapsıyor (A'nın sonucu); kendi denetimimde 95'in hepsi çizili.
- Öneri: kalıcı denetimi 95'e genişlet.

### B-10 (engellemeyen). Okla gezindikten sonra adres sorgusu bayat kalıyor
- `?adim=30` ile açıp okla 31.5'e gelince adres `?adim=30#31.5`. Yenilemede sorgu kazanıyor, 30 açılıyor.
- `app.js:602` yalnız hash'i yazıyor. HEAD'de de aynı; F10d'nin getirdiği bir hata değil.
- Öneri: `replaceState` sorguyu da temizlesin.

### B-11 (engellemeyen). 49.5 patlatmasında cıvatalar kapağın içinden geçiyor
- Cıvata `max(25, 2,5 × boy)` = 25 mm, kapak 45–64 mm. Patlatılmış cıvata kapağın gerisinde kalıyor (`kare/P-49.5-*.png`).
- Öneri: cıvatanın d'si, takıldığı parçanın d'sinden az olmasın (cıvata d = ev d + 25).

### B-12 (engellemeyen). "ya da önden / arkadan kaydırarak" ölçülmemiş
- Adım metninde HEAD'den kalan bu ifade için uçuş / giriş ölçümü yok. Ben de ölçmedim.

## Diğer kontroller
- **Önce / sonra.**
  - HEAD'in adım 31 karesi: tek kare, yalnız dış kabuk, iç parçalar görünmüyor.
  - Adım 33: tek kare, bütün etek; hangi bant önce belli değil.
  - Yenisi ikisinde de belirgin biçimde daha iyi.
- **Yan etkiler.**
  - İzinli alan dışındaki değişiklikler oturumdan önce vardı: `tasarim/freecad/kabuk/gorsel/*.png` (09.11), `montaj/yerlesim-kontrol.json`
    (03.11), `planlama/dongu-158.md` (koordinatör).
  - Değişen izlenen dosya sayısı koşularımdan önce ve sonra aynı (88).
- **Yerel yol / takma ad.** Değişen dosyaların eklenen satırlarında 0.

## Karar kuyruğuna önerilen metinler

> **F10d-K1 · Kabuk bindirme dilleri: bantlar düz yoldan girmiyor**
> - **Soru:** Göğüs bandı (ölçüldü), büyük olasılıkla etek ön, omuz bandı ve çerçeve (ölçülmedi), bir alttaki bandın 12 mm
>   bindirme diline düz yoldan girmiyor. Okura nasıl tarif edilsin, geometri mi değişsin?
> - **Ölçüm** (F10d-kontrol, hacimsel süpürme):
>   - göğüs bandı sağ, +x: 2–130 mm orta bantla ortak hacim, 180 mm'de serbest;
>   - +y: 1–8 mm'de orta bant.
>   - Tasarım belgesi (`kabuk_rapor.py:211-213`) dili tarif ediyor, takma biçimini değil.
> - **Seçenekler:**
>   a) "Bandı hafifçe esneterek, dili alttaki bandın arkasına sokarak" metni + kare (geometri değişmez; baskı kuponunda denenmeli);
>   b) dil ön / arka yarıda tersine (biri içe, biri dışa) ya da dilde pah: geometri, kabuk çakışma taraması gerekir;
>   c) rehberde iki parçalı yol (önce eğik, sonra yerine).
> - **Öneri:** Önce B-2 düzeltilsin, sonra etek / omuz / çerçeve aynı süpürmeyle ölçülsün. a geçici, b bir sonraki geometri paketinde.
>   Karar Ahmet'te.

> **F10d-K2 · Isıl gömme somunlarının adımı (rehber verisi, geometri değil)**
> - **Soru:** 34 ısıl gömme somunu yanlış adımda / yanlış parçayla:
>   - y1005 (6) ve y1198 (6) üstteki banda;
>   - arka kapak (7) ve üst arka kapak (7) kapağa bağlı;
>   - H1 / H2 (8) ev sahipsiz.
>   Hepsi bir alttaki bandın malzemesinde.
> - **Öneri:** Rehber verisi düzeltmesi, karar gerekmez. Somunlar ev sahibi bandın adımına (F1 33, F2 34, F3 35) taşınsın; 49.1
>   metni düzeltilsin. Sayı aynı kalır, adım değişir. Sonra sıra / perdelenme / uçuş denetimi yeniden.

> **F10d-K3 · (önerilen: kuyruktan düşsün)**
> - 4 "model girişimi" gerçek derinlikte 0,057–0,28 mm (üçgenleme). FreeCAD katı analizinde kabuk 952 ve kafa 498 çiftte çakışma 0.
>   Geometri değişikliği gerekmez.
> - Rehberde gerekçe metni düzeltilsin. 49.4'teki çarpışma K2 ile çözülür.

## Ölçülmeyenler
- 35.4 göğüs ekranı yönü (0, 1, 4): koşu zaman aşımına uğradı.
- K1: etek ön sağ / sol, çerçeve sağ / sol, omuz bandı sağ / sol süpürmesi. Göğüs bandı sol (simetrik varsayıldı).
- 33.3 dolgu şeridinin iki parçalı yolu, 35.3 çekiç somunu, 31.6 kamera uçuşu (yalnız derinlik ölçüldü).
- B-2 düzeltilmiş atamayla 36.x ve 49.4'ün yeniden süpürmesi.
- `F10a-dogrula` ve `F10d-dogrula`: depoya yazdıkları için koşulmadı; sonuçları A'nın.
- Toplam konum sayısı (95) ve 95 / 95 panel = takma: bağımsız sayılmadı. 31 ve 33 çevresinde 30 konumda yol doğru.
- FreeCAD katılarıyla ortak hacim: yapılmadı. K3'teki katı değerleri mevcut analiz dosyalarından.
- Gerçek baskıda bant esnemesiyle takılabilirlik: fiziksel parça yok.
