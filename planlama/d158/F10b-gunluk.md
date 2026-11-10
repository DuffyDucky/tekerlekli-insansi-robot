# F10b günlüğü (P10.2): ön şarj kartı × elektronik katı, 11.11.2026

Ajan A. Brief `planlama/d158/F10b-brief.md`. **Sonuç: girişim var (gerçek katılarla doğrulandı), model değiştirilmedi.
Paket "Karar gerekiyorsa" maddesinde durdu** (§4). Değişen depo dosyası yalnız `planlama/d158/F10b-*`.

## 1. Komutlar

| Saat | Komut | Çıkış |
|---|---|---|
| 00:07 | Ön koşul: çalışan FreeCAD 0, boş bellek 3,34 GB, `FREECAD-KILIT.txt` "boş" → satır yazıldı | – |
| 00:07 | `FC_SCRIPT=planlama/d158/F10b-olcum.py freecadcmd %USERPROFILE%\.robot-cad\run_fc.py` (ilk koşu, 109 s) | 0 |
| 00:14 | Aynı betik, B3'te kartın kendi alt vidası engelden çıkarıldı (ilk koşuda burç ↔ kendi alt vidası 0 mm "temas" gibi sayılıyordu), 73 s | 0 |
| 00:16 | `FREECAD-KILIT.txt` → "boş"; çalışan FreeCAD 0 | – |
| 00:16 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 ("17 dosya kayitla ayni") |
| 00:16 | `py -3 planlama/d158/regresyon.py --yazma` | 0 (GEÇER, 10 değer aynı) |

Koşu günlükleri scratchpad'de (depoda değil). Çıktı `planlama/d158/F10b-olcum.json`.

## 2. Yöntem

`F10b-olcum.py`: `taban_parcalar` (355 parça) + `iskelet_parcalar` (59) + kabuk etek braketleri (`kabuk_parcalar`, grup "Etek braketleri")
FreeCAD katıları, global koordinat. Hareketli grup takılı konumundan +Y yönünde 0…60 mm (M5x40 burç boyu + 20), **0,5 mm adım** (121 konum).
Her konumda aday çiftlerde (XZ izdüşümü 5 mm içinde) ortak hacim `common().Volume` (> 1e-4 mm³ sayılır) ve en küçük boşluk `distToShape`;
sınır kutusu aralığı > 3 mm olan çiftte kesin ölçüm yok (boşluk ≥ kutu aralığı). dy = 0'da tasarım oturması (kat / panel → M5x40 burç,
kart → alt plaka) boşluktan ayrı sayıldı.

- **B6** hareketli: elektronik katı alt montajı (kat ön + "Elektronik" grubu, 80 parça). Engel: B6'dan önce takılı her şey (güç paneli alt
  montajı dahil); sonar, acil stop, ana anahtar ve kat ön cıvataları hariç.
- **B5** hareketli: güç paneli alt montajı (panel + XL4016 C + ön şarj kartı + sigorta kutusu + röle + ana sigorta, burç / vida / pul / somun;
  39 parça). Engel: iskelet, B1–B4, etek braketleri, alt plaka kartları, akü.
- **B3** hareketli: her alt plaka kartı (kart + burç + üst vida) ayrı; 0…28 mm (burç 8 + 20). Engel: iskelet, plaka, tahrik, öbür kartlar, akü.

## 3. Ölçüm (madde 1)

Geometri (katılardan): kat ön kenarı z 24,25; güç paneli kenarı z 23,75. Ön şarj kartı x −132,5…−62,5, z −26,0…24,0 (PCB üstü y 189,1).
Ön burçlar (altıgen AA 5,5, köşe ±z'de) z 18,325…**24,675**, y 179,5…187,5; üst M3 vida başı z …**24,25**, y 183,1…192,1.

### B6 (elektronik katı aşağı inerken) — konum başına

| dy (mm) | Ortak hacim, ön şarj grubu (mm³) | En küçük boşluk, ön şarj grubu (mm) | Güç panelinin öbür parçaları: ortak hacim / boşluk | Öbürleri (iskelet, taban) |
|---|---|---|---|---|
| 0 (takılı) | 0 | 0 (ön burçlar kat ön üst yüzüne değiyor) | 0 / 0,50 (panel aralığı) | 0 / ≥ 4,25 (direk) |
| 0,5 | 0,314 (2 × 0,157) | 0 | 0 / 0,50 | 0 |
| 1,0 | 0,627 | 0 | 0 / 0,50 | 0 |
| 2,0 | 1,254 | 0 | 0 / 0,50 | 0 |
| 3,0 | 1,881 | 0 | 0 / 0,50 | 0 |
| 4,0 | 2,508 | 0 | 0 / 0,50 | 0 |
| 5,0 … 8,0 | **3,135** (2 × 1,567, en büyük) | 0 | 0 / 0,50 … 0,90 | 0 |
| 10,0 | 1,881 | 0 | 0 / 0,75 (XL4016 C) | 0 |
| 12,0 | 0,627 | 0 | 0 / 0,75 | 0 |
| 12,5 | 0,314 | 0 | 0 / 0,75 | 0 |
| 13,0 … 17,5 | 0 | 0 (üst M3 vida başı kat kenarı düzleminde) | 0 / 0,75 … 1,6 | 0 |
| 18,0 | 0 | 0,40 | 0 / 3,5 | 0 |
| 18,5 | 0 | 0,90 | 0 / 4,0 | 0 |
| 20,0 | 0 | 2,40 | 0 / 4,25 | 0 |
| 25 … 60 | 0 | ≥ 4,25 | 0 / ≥ 3,58 | 0 / ≥ 4,25 |

Ortak hacimli konumlar: dy 0,5…12,5 (25 konum), hepsi kat ön ↔ ön şarj ön burçları 1 ve 3 (x −130 / −65, z +21,5). Boşluk < 0,5 mm:
dy 0…18,0 (37 konum). PCB kenarı kat kenarına analitik olarak 0,25 mm (24,25 − 24,0; ölçümde vida başı 0 mm'si bunu örtüyor).
Güç panelinin öbür parçaları ve iskelet / etek braketi: hiçbir konumda ortak hacim yok, boşluk ≥ 0,50 mm (panel ↔ kat aralığı, tasarım).

**Sonuç: girişim var: en çok 3,135 mm³ (iki ön burç × 1,567 mm³), dy 0,5…12,5 mm; ayrıca dy 12,5…18 mm arası vida başıyla 0 mm boşluk.**
Bbox ölçümü (0,5 mm taşma) doğrulandı: gerçek taşma 0,425 mm (24,675 − 24,25), burç köşesinden.

### B5 (güç paneli) ve B3 (alt plaka kartları)

| İniş | Ortak hacim (tüm konumlar) | En küçük boşluk (oturma hariç) | Nerede |
|---|---|---|---|
| B5 güç paneli | 0 | 1,30 mm (dy 0) | panel ↔ akü kayışı z −140; direk 2,0 mm |
| B3 BTS7960 sol / sağ | 0 | 2,5 mm (dy 0) | kart ↔ şase uzun rayı |
| B3 XL4016 B / çevre / A | 0 | > 3 mm (yakın çift yok) | – |

İniş yolunda başka takılan yok (oturma burcundan kalkış boşluğu = dy, sayılmadı).

### Ek: ön şarj burçlarının panele oturması (önceden var olan durum)

| Burç (x, z) | Taban alanı mm² | Panelde desteklenen mm² | Oran | Alt M3 vida başı oranı |
|---|---|---|---|---|
| 0 (−130; −23,5) | 19,13 | 17,12 | 0,895 | 0,618 |
| 1 (−130; +21,5) | 19,13 | 15,64 | 0,817 (0,5 mm panel aralığına taşıyor) | 0,573 |
| **2 (−65; −23,5)** | 19,13 | **7,48** | **0,391** | **0,264** |
| 3 (−65; +21,5) | 19,13 | 15,64 | 0,817 | 0,573 |
| (karşılaştırma) XL4016 C burçları | 19,13 | 17,12 | 0,895 | 0,618 |

Burç 2, güç panelindeki akü kablo yarığının (x −80…−40, z −37…−23; `taban_parcalar.py` "aku kablolari") üstüne biniyor; alt vida deliği
yarığa açık. F10b'den bağımsız, modelde zaten var.

## 4. Seçenekler (bellekte denendi, modele dokunulmadı) ve neden durdum

| Seçenek | Kat inişi: ortak hacim / en küçük boşluk (ön şarj grubu) | Bozduğu | Değişen kaynak |
|---|---|---|---|
| Mevcut | 1,567 mm³ (tek burç) / 0 | – | – |
| a) Kart −z 1,0 mm | 0 / 0,575 | burç 2 oturma 7,48 → **1,98 mm²**, alt vida başı 6,28 → **1,19 mm²** | `arayuz.py` |
| a) Kart −z 1,5 mm (brief önerisi, boşluk ≥ 1) | 0 / 1,075 | burç 2 **0,13 mm²**, vida başı **0,09 mm²** (yarığın içinde kalıyor) | `arayuz.py` |
| a) Kart −z 2,0 mm | 0 / 1,575 | burç 2 ve vida başı **0** | `arayuz.py` |
| b) Kat önde çentik 1,5 mm, x −134,25…−60,75 (kart ± 1,5 mm), z 24,25 → 25,75 | 0 / 1,075 | yok (kat ön −550,4 mm³ ≈ −0,37 g; yalnız malzeme çıkıyor, yeni çakışma olamaz) | `arayuz.py` + `taban_parcalar.py` |
| c) `kat_ayrim_z` 24,0 → 25,5 (iki plaka 1,5 mm kayar) | 0 / ~1,075 (analitik, ölçülmedi) | BOM `kod` metinleri "270 x 226" / "270 x 274" eskir; iki plakanın kütlesi değişir | `arayuz.py` |
| d) Modele dokunmadan rehber notu (katı 1–2 mm önde indir, geri it; ya da ön burçları düz yüzü +z'ye bakacak vidala → 24,25, 0 mm) | modelde girişim kalır | brief kabulünü karşılamaz; rehber F10a / F10c alanı | – |

**Durma gerekçeleri (brief "Karar gerekiyorsa"):**
1. Brief'in önerdiği kaydırma (a) bir şeyi bozuyor: burç 2'nin panel oturması %39'dan %0,7'ye, alt vida başınınki %26'dan %0,4'e düşüyor
   (kart −z yönünde akü kablo yarığının üstüne kayıyor). Bozmayan tek geometri seçeneği (b) çentik.
2. Her geometri seçeneği tarama kaynağını değiştiriyor (`arayuz.py`, (b)'de `taban_parcalar.py` da; `carpisma_kos.KAYNAK_SABIT`). Kaynak özeti
   md5 olduğundan 9 bölümün hepsi eskir; `carpisma_kos kontrol` 0 kabulü yalnız tam tarama (~4 saat, F6a'da omuz 12.293 s) ile sağlanır, o da
   yasak ("tam tarama yalnız P6'da"). Önceki paketlerde "referans yenileme" yöntemi bulamadım: F1a / F1b bölümleri yeniden koştu ve omuz eskimiş
   kaldı (`kontrol` 1), F6a tam tarama koştu. Bölüm JSON'larındaki `kaynak` özetlerini elle yazmak yeni bir yöntem olur; benim kararım değil.

**Öneri:** (b) çentik 1,5 mm. Kablo yolu: kat_kesik_on (z 150…175) ve akü kablo yarıkları etkilenmez; aralık 0,5 → 2,0 mm olur
(x −135…−60,75 boyunca). H1 / H2 servis kapakları: etek arkasında, dokunulmaz. Komşular: kat ön M5 deliği (x −115, z 40) çentik kenarına
11,5 mm, pul 9,25 mm; arayüz kartı z ≥ 55. Kart "zarf tahmini": gerçek pertinaks 70 × 50'den büyük gelirse çentik kart konumuna değil
x aralığına bağlı, `arayuz.py`'de tek yerde değiştirilir. Kat ön köşesinde 0,75 mm'lik ince şerit kalmasın diye uygulamada x0 = −136
(çentik yana açık) alınmalı. Çakışma kabulü için orkestratörden biri gerekiyor:
- (i) zincir + hedefli `carpisma_kos.py taban statik` (~3 dk), `kontrol` 1 (öbür 7 bölüm eskimiş) kabul edilir, tam tarama P6 kuralına bırakılır; ya da
- (ii) hedefli bölümlerden sonra öbür 7 bölümün `kaynak` özetinin yenilenmesine onay (çentik yalnız tabandan malzeme çıkarır; kol / kafa / omuz
  taramalarında taban hedefi y ≤ 290'da, kolun en alt noktası y ≈ 626);
- (iii) bekletip bir sonraki tam taramaya (P6 kuralı) bağlamak.

## 5. Değişen JSON anahtarları

Yok (model ve analiz çıktıları değişmedi). Yeni dosya `planlama/d158/F10b-olcum.json`.

## 6. Dokunulan dosyalar (commit listesi)

- `planlama/d158/F10b-olcum.py` (yeni)
- `planlama/d158/F10b-olcum.json` (yeni)
- `planlama/d158/F10b-gunluk.md` (bu dosya)
- `planlama/d158/FREECAD-KILIT.txt`: koşu boyunca satır, sonunda yine "boş" (içerik başlangıçla aynı)

`git status` farkı (başlangıca göre): F10b-olcum.py / .json ve bu günlük. Ayrıca `rehber/app.js`, `rehber/index.html`, `rehber/stil.css`,
`rehber/vendor/` değişikliği F10a'nın (paralel paket), bana ait değil.

## 7. Açık kalanlar

1. **Karar:** §4 seçenek (b) / (a) / (c) / (d) ve `kontrol` 0 kabulünün nasıl sağlanacağı (i / ii / iii).
2. Önceden var olan: ön şarj burcu 2 (x −65, z −23,5) akü kablo yarığına biniyor (oturma %39, alt vida başı %26, delik yarığa açık). Seçenek (b)
   bunu çözmez; ayrı iş (yarığı x −80…−70'e daraltmak ya da burç yerini değiştirmek). Kartın gerçek ölçüsü gelince birlikte bakılmalı.
3. Ön burçlar 1 ve 3 panel aralığına 0,925 mm taşıyor (oturma %82); (c) bunu da çözerdi, (b) çözmez (işlevsel sorun değil).
4. Rehber verisinde (F10c) B6 adımı: hangi seçenek uygulanırsa ona göre; (d) seçilirse not metni F10a / F10c'de.
5. Model ölçümü altıgen köşesini +z'de varsayıyor (`taban_lib.burc`, düz yüz x'e bakıyor); gerçekte vidalanan burcun dönüşü rastgele, en kötü
   durum bu.
