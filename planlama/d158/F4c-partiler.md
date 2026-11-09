# F4c baskı partileri (Parti 0–4) — 09.11.2026

Üreten: `py -3 planlama/d158/F4c-partiler.py` (bu dosya ve `F4c-partiler.json`). Parça satırları `planlama/y2/Y2b-baski.json`'dan,
parti numaraları `Y2b-baski.py` `parti()` ile aynı (yani `planlama/baski-listesi.md` Özet'i ile aynı). Bağımlılık ve montaj adımı sütunları
elle (`F4c-partiler.py` `META`); montaj adımları `planlama/adim4/M6-montaj-sirasi.md` §2 (125 cm tablosu; 1,58 m'de göğüs ekranı,
QLED, uzatma bandı, hoparlör ve hub adımları henüz yok). Toplamların doğrulaması: `py -3 planlama/d158/F4c-dogrula.py`.

## Özet

| Parti | Ne zaman | Adet | PETG | PETG-CF | Toplam | Süre | Durum A takvimi (`proje-plani.md`) |
|---|---|---|---|---|---|---|---|
| Parti 0 | İlk gün (S'den önce) | 8 baskı (6 kupon) | 0,08–0,12 kg | 0,18–0,30 kg | 0,26–0,42 kg | ≈ 7,3–12,0 sa | S = 16.11 için 9–10.11 (proje-plani.md, Durum A) |
| Parti 1 | Hemen (Parti 0 sonucu CAD'e girip STL çıkınca) | 27 | 3,16 kg | 0,14–0,15 kg | 3,31 kg | ≈ 68,9–69,0 sa | ≈ S−0,5 → S+1,5; akü takozu (Parti 4) bu partinin arasında basılır |
| Parti 2 | Servo ve horn gelip kumpasla ölçülünce | 25 | 0,32 kg | 1,01–1,07 kg | 1,33–1,38 kg | ≈ 27,7–28,8 sa | ≈ S+1,5 → S+2,3 |
| Parti 3 | QLED gelip ölçülünce | 9 | 0,75 kg | 0,00 kg | 0,75 kg | ≈ 15,7 sa | ≈ S+2,3 → S+2,8 |
| Parti 4 | E7 havalandırma CAD'e girince; akü takozu akü gelince | 11 | 2,21 kg | 0,00 kg | 2,21 kg | ≈ 45,9 sa | ≈ S+2,8 → S+4–4,5 |
| **Parti 1–4** | | **72** | **6,45 kg** | **1,16–1,22 kg** | **7,60–7,66 kg** | **≈ 158,2–159,4 sa** | |

Kontrol (betik): Parti 1–4 toplamı = `Y2b-baski.json` `toplam` (adet evet, g evet, sa evet, PETG-CF evet); her parti Y2b `toplam.parti` ile aynı: evet; her parça tam bir partide: evet. Kuponlar parça toplamına katılmaz.

## Parti 0 — tolerans kuponları

Bağımlılık: Kupon STL'leri hazır. Değerlendirme için 6808-2RS, 625ZZ, M3/M5 ısıl gömme somun ve kupon D vidaları elde (K29 erken alım; K31 insert varyantı).
Sonrası: Sonuç CAD'e (arayuz.INSERT_DELIK, rulman yuvaları, GECME) → STL dışa aktarma (FreeCAD, açık iş) → Parti 1.

| Kupon | STL | Malzeme | Ne denenir | Filament (g) | Süre (sa) | Kütle kaynağı |
|---|---|---|---|---|---|---|
| A | `kupon-a-rulman-O52.stl` | PETG-CF | 6808-2RS dış bileziği: Ø52,0 / 52,1 / 52,2 / 52,3 (omuz rulman kapağı, kafa rulman yuvası) | 26,0 | 0,74 | STL hacmi × 1,27 (%100; tahmini değer yok) |
| B | `kupon-b-yuva-mil-somun.stl` | PETG-CF | 625ZZ Ø16,0…16,3 · Ø40 mil Ø39,8…40,1 · M3 Ø3,8…4,1 / M5 Ø6,2…6,6 dikey (L + 0,5) | 60,0–87,9 | 1,71–2,50 | alt 60 g: 03.11 listesi (kaynağı yazılmamış); üst STL %100 |
| B | `kupon-b-yuva-mil-somun.stl` | PETG | aynı kupon beyaz PETG'de (kabuk ısıl gömme delikleri) | 60,0–87,9 | 1,71–2,50 | aynı |
| C | `kupon-c-isil-gomme-L1.stl` | PETG-CF | Isıl gömme L + 1: M3 Ø3,9…4,1, M5 Ø6,2…6,6, yatay + dikey | 7,5–13,4 | 0,21–0,38 | m7-kupon-sonuc.json |
| C | `kupon-c-isil-gomme-L1.stl` | PETG | aynı kupon beyaz PETG'de | 7,5–13,4 | 0,21–0,38 | m7-kupon-sonuc.json |
| D1 | `kupon-d1-kelepce-kesiksiz.stl` | PETG-CF | Dirsek kelepçesi (çatal dilimi), kesiksiz | 40,9–87,9 | 1,16–2,50 | m7-kupon-sonuc.json |
| D2 (koşullu) | `kupon-d2-kelepce-bosaltmali.stl` | PETG-CF | Dirsek kelepçesi, kökte boşaltmalı (D1 geçerse yalnız karşılaştırma) | 41,4–86,2 | 1,18–2,45 | m7-kupon-sonuc.json |
| E | `kupon-e-tup-halkasi.stl` | PETG | Üst kol tüpü halkası (tüp–pim / tüp–bilezik geçmesi) | 14,3–17,9 | 0,41–0,51 | m7-kupon-sonuc.json |
| **Toplam** | | | | **257,6–420,6** | **7,32–11,96** | PETG 81,8–119,2 g, PETG-CF 175,8–301,4 g |

Süre `tasarim/freecad/test/README.md` yöntemiyle: hacim (g / 1,27) ÷ 10 mm³/s × 1,3; alt değer tahmini kütle, üst değer %100 dolu. Dilimleyicinin verdiği esastır. D2 basılmazsa (D1 geçerse) ≈ 6,2–9,5 sa. `proje-plani.md`'deki "≈ 3 sa" yalnız M7 kuponları (C bir kez, D1, D2, E); A, B ve iki malzemeli B/C eklenince ≈ 7,3 sa (tahmini kütleyle).

**Isıl gömme (K31 açık; A/B/C seçeneğine göre kupon):**

| K31 seçeneği | Delik (satıcı kuralı, `F8a-siparis.md` §4.1) | Kupon B / C | Parti 0'a etkisi |
|---|---|---|---|
| A: Rhino ID3 OD4 L4 (önerilen varsayılan) | Ø3,8–3,9 | B'de Ø3,8 / 3,9 (dikey), C'de Ø3,9 damla | Kupon değişmez; C'nin derinliği 6,7 (L 5,7 + 1) L4 için fazla ama deneme için engel değil |
| B: Rhino ID3 OD5 L6 | Ø4,8–4,9 | Uymaz (Ø3,8–4,1) | B ve C yeniden üretilir (`arayuz.INSERT`, FreeCAD); A, D1, D2, E beklemeden basılır, B/C gecikir |
| C: ruthex RX-M3x5.7 | Ø4,0–4,2 | B'de Ø4,0 / 4,1, C'de Ø4,0 / 4,1 | Kupon değişmez; tedarik takvime yetişmez (K31) |
| M5: Rhino ID5 OD7 L7 | Ø6,7–6,8 | Uymaz (Ø6,2–6,6) | M5 delikleri büyütülür ya da başka ürün (K31, önerilen varsayılan yok) |

**Omuz dişi kökü:** Kupon yok. K39 (açık, varsayılan d): kök +x iç köşesine ≥ 1,5 mm yarıçap/pah P6.1'de; öneri: göbeğin kendisi P6.1 sonrası Parti 2'nin ilk işi, S2 5°'te sentille 0,3 mm boşluk kontrolü (F2-gunluk madde 9) + DS3235 düşme ölçümü (K39).

## Parti 1 — Hemen

27 adet · 3,31 kg (PETG 3,16, PETG-CF 0,14–0,15) · ≈ 68,9–69,0 sa. Bağımlılık: Parti 0 sonucu + STL dışa aktarma. Satın alınan parçaya bağlı 7 satır partinin sonunda, ilgili kalem gelip ölçülünce basılır: üst arka kapak (USB hub), hoparlör kabı ve kelepçesi (8 Ω hoparlör, K36/K6), göğüs ekranı çerçevesi sağ/sol ve VESA taşıyıcı (11,6" göğüs ekranı; VESA delik yeri doğrulanmadı, `arayuz.py:342`; F4c-kontrol B-2). Montaj (M6): 16 (sonar), 20 (rulman kapağı), 34–36 (bantlar, göğüs ekranı), 40 (üst kol tüpü), F5 (kapaklar). Takvim: ≈ S−0,5 → S+1,5; akü takozu (Parti 4) bu partinin arasında basılır.

**Partinin sonuna bırakılan (satın alınan parçaya bağlı):** 7 adet, 275,0 g (PETG-CF 113,0 g), ≈ 5,80 sa: Üst arka servis kapağı, Göğüs ekranı çerçevesi sağ, Göğüs ekranı çerçevesi sol, Göğüs ekranı VESA taşıyıcı, Hoparlör kabı ön halka, Hoparlör kabı arka (flanşlı), Hoparlör kelepçesi. Tablonun son satırları; parça gelip kumpasla ölçülmeden basılmaz, ölçü tutmazsa CAD düzeltilir (P6.1). Yanlış basılan VESA taşıyıcı KT-F4c-1'deki dar PETG-CF payını yer.

| Modül | Parça | Adet | Malzeme | g/adet | sa/adet | Bağlı olduğu kalem | M6 adımı | Not |
|---|---|---|---|---|---|---|---|---|
| taban | Sonar tutucu sol | 1 | PETG | 5 | 0,11 | — | 16 (B7) |  |
| taban | Sonar tutucu orta | 1 | PETG | 6 | 0,12 | — | 16 (B7) |  |
| taban | Sonar tutucu sağ | 1 | PETG | 5 | 0,11 | — | 16 (B7) |  |
| kabuk | Gövde alt bandı sağ | 1 | PETG | 299 | 6,20 | Kupon B/C (ısıl gömme deliği) | 34 (F2) |  |
| kabuk | Gövde alt bandı sol | 1 | PETG | 280 | 5,80 | Kupon B/C | 34 (F2) |  |
| kabuk | Gövde uzatma bandı 1 sağ | 1 | PETG | 224 | 4,70 | Kupon B/C | 34 (F2) ile; M6'da satırı yok |  |
| kabuk | Gövde uzatma bandı 1 sol | 1 | PETG | 211 | 4,40 | Kupon B/C | 34 (F2) ile; M6'da satırı yok |  |
| kabuk | Gövde uzatma bandı 2 sağ | 1 | PETG | 224 | 4,70 | Kupon B/C | 34 (F2) ile; M6'da satırı yok |  |
| kabuk | Gövde uzatma bandı 2 sol | 1 | PETG | 211 | 4,40 | Kupon B/C | 34 (F2) ile; M6'da satırı yok |  |
| kabuk | Gövde orta bandı sağ | 1 | PETG | 272 | 5,70 | Kupon B/C | 34 (F2) |  |
| kabuk | Gövde orta bandı sol | 1 | PETG | 262 | 5,40 | Kupon B/C | 34 (F2) |  |
| kabuk | Göğüs bandı sağ | 1 | PETG | 219 | 4,60 | Kupon B/C; 11,6" ekran cebi | 35 (F3) |  |
| kabuk | Göğüs bandı sol | 1 | PETG | 215 | 4,50 | Kupon B/C; 11,6" ekran cebi | 35 (F3) |  |
| kabuk | Omuz bandı sağ | 1 | PETG | 184 | 3,80 | Kupon B/C | 36 (F4) |  |
| kabuk | Omuz bandı sol | 1 | PETG | 178 | 3,70 | Kupon B/C | 36 (F4) |  |
| kabuk | Arka servis kapağı | 1 | PETG | 98 | 2,00 | — | F5 (son) |  |
| omuz | Rulman kapağı | 2 | PETG-CF | 15–17 | 0,32–0,36 | 6808-2RS (kupon A) | 20 (D1b) |  |
| omuz | Üst kol tüpü | 2 | PETG | 54 | 1,13 | Kupon E (tüp–pim geçmesi) | 40 (G3) |  |
| kabuk | Üst arka servis kapağı | 1 | PETG | 85 | 1,80 | USB hub 4'lü (72 × 25 × 19) ölçüsü: hub takozu | F5 (son); M6 §4 K4 | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| kabuk | Göğüs ekranı çerçevesi sağ | 1 | PETG | 31 | 0,60 | 11,6" göğüs ekranı kasası (284,65 × 182,25) | 35 (F3) ile; M6'da 1,58 m adımı yok | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| kabuk | Göğüs ekranı çerçevesi sol | 1 | PETG | 31 | 0,60 | 11,6" göğüs ekranı kasası (284,65 × 182,25) | 35 (F3) ile; M6'da 1,58 m adımı yok | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| kabuk | Göğüs ekranı VESA taşıyıcı | 1 | PETG-CF | 113 | 2,40 | 11,6" göğüs ekranı VESA delikleri (yer ve derinlik doğrulanmadı, `arayuz.py:342`) | 35 (F3) ile; M6'da 1,58 m adımı yok | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| kabuk | Hoparlör kabı ön halka | 1 | PETG | 3 | 0,10 | 8 Ω hoparlör (K36 stok, K6 yön); kap ölçüsü VARSAYIM | 34 (F2) öncesi, orta bant sağ; M6'da yok | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| kabuk | Hoparlör kabı arka (flanşlı) | 1 | PETG | 7 | 0,20 | 8 Ω hoparlör (K36, K6); VARSAYIM | 34 (F2) öncesi; M6'da yok | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |
| kabuk | Hoparlör kelepçesi | 1 | PETG | 5 | 0,10 | 8 Ω hoparlör (K36, K6); VARSAYIM | 34 (F2) öncesi; M6'da yok | Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır |

## Parti 2 — Servo ve horn gelip ölçülünce

25 adet · 1,33–1,38 kg (PETG 0,32, PETG-CF 1,01–1,07) · ≈ 27,7–28,8 sa. Bağımlılık: DS3235, MG996R, 25T horn (teslim S+1); omuz göbeği ayrıca K39 kök yarıçapı (P6.1); S1 kaseti kablo kalınlığı (K1). Montaj (M6): 19–28 (omuz yuvası, boyun), 37–47 (göbek, kol, dirsek, el), 41 (S1 kaseti). Takvim: ≈ S+1,5 → S+2,3.

| Modül | Parça | Adet | Malzeme | g/adet | sa/adet | Bağlı olduğu kalem | M6 adımı | Not |
|---|---|---|---|---|---|---|---|---|
| kabuk | S1 kaset gövdesi sağ | 1 | PETG | 10 | 0,20 | Kablo kalınlığı ≤ 1,4 mm (K1) | 41 (G4) |  |
| kabuk | S1 kaset kapağı sağ | 1 | PETG | 7 | 0,10 | — | 41 (G4) |  |
| kabuk | S1 kaset gövdesi sol | 1 | PETG | 10 | 0,20 | Kablo kalınlığı ≤ 1,4 mm (K1) | 41 (G4) |  |
| kabuk | S1 kaset kapağı sol | 1 | PETG | 7 | 0,10 | — | 41 (G4) |  |
| kafa | Servo yuvası | 1 | PETG-CF | 152 | 3,16 | MG996R gövdesi | 23 (E1a) |  |
| kafa | Rulman yuvası | 1 | PETG-CF | 27 | 0,56 | 6808-2RS (kupon A) | 23 (E1a) |  |
| kafa | Boyun mili | 1 | PETG-CF | 41 | 0,85 | Pan horn delik dizilimi | 26 (E2b) |  |
| kafa | Eğme çatalı | 1 | PETG-CF | 36 | 0,75 | Tilt horn delik dizilimi | 27 (E2c) |  |
| kafa | Boyun yükseltme adaptörü | 1 | PETG-CF | 70 | 1,46 | — | 26–27 arası; M6'da satırı yok |  |
| dirsek | Dirsek çatalı | 2 | PETG-CF | 97 | 2,03 | Dirsek horn delik dizilimi; kupon D1/D2 | 44 (H0c) |  |
| dirsek | Ön kol gövdesi | 2 | PETG | 57 | 1,18 | MG996R gövdesi | 42 (H0a) |  |
| dirsek | Bilek flanşı | 2 | PETG-CF | 4 | 0,09 | Bilek horn delik dizilimi | 46 (H0e) |  |
| dirsek | El | 2 | PETG | 78 | 1,64 | — | 47 (H0f) |  |
| omuz | Omuz yuvası | 2 | PETG-CF | 81–90 | 1,70–1,88 | DS3235 gövdesi, çekiç somun | 19 (D1a) |  |
| omuz | Omuz göbeği | 2 | PETG-CF | 63–70 | 1,32–1,47 | S1 horn delik dizilimi; K39 kök yarıçapı (P6.1) | 37–38 (G0, G1) |  |
| omuz | S1 kablo tamburu | 2 | PETG | 6 | 0,12 | Göbekle birlikte | 37 (G0) |  |
| omuz | Kol çatalı | 2 | PETG-CF | 99–110 | 2,07–2,30 | S2 horn delik dizilimi | 40 (G3) |  |

## Parti 3 — 10,1" QLED yüz ekranı gelip ölçülünce

9 adet · 0,75 kg (PETG 0,75, PETG-CF 0,00) · ≈ 15,7 sa. Bağımlılık: 10,1" QLED (K32: hocadan mı satın alma mı), K2 (AI HAT / boss, P6.1'de kafa modeline). Montaj (M6): 29–31 (kafa içi, kafa → tilt hornu, kafa kabukları). Takvim: ≈ S+2,3 → S+2,8.

| Modül | Parça | Adet | Malzeme | g/adet | sa/adet | Bağlı olduğu kalem | M6 adımı | Not |
|---|---|---|---|---|---|---|---|---|
| kafa | Yüz kabuğu (ön) sağ | 1 | PETG | 91 | 1,89 | QLED (K32) + K2 (P6.1) | 31 (E4) |  |
| kafa | Yüz kabuğu (ön) sol | 1 | PETG | 84 | 1,76 | QLED (K32) + K2 (P6.1) | 31 (E4) |  |
| kafa | Arka kafa kabuğu sağ | 1 | PETG | 229 | 4,78 | QLED (K32) + K2 (P6.1) | 31 (E4) |  |
| kafa | Arka kafa kabuğu sol | 1 | PETG | 215 | 4,49 | QLED (K32) + K2 (P6.1) | 31 (E4) |  |
| kafa | Kafa iskeleti | 1 | PETG | 128 | 2,66 | QLED + kamera delikleri; K2 (P6.1) | 29 (E3a) |  |
| kafa | Ekran tırnağı üst sağ | 1 | PETG | 2 | 0,03 | QLED kasa ölçüsü | 29 (E3a) |  |
| kafa | Ekran tırnağı üst sol | 1 | PETG | 2 | 0,03 | QLED kasa ölçüsü | 29 (E3a) |  |
| kafa | Ekran tırnağı alt sağ | 1 | PETG | 2 | 0,03 | QLED kasa ölçüsü | 29 (E3a) |  |
| kafa | Ekran tırnağı alt sol | 1 | PETG | 2 | 0,03 | QLED kasa ölçüsü | 29 (E3a) |  |

## Parti 4 — Etek tasarım kararından sonra (M6 CAD)

11 adet · 2,21 kg (PETG 2,21, PETG-CF 0,00) · ≈ 45,9 sa. Bağımlılık: E7 etek havalandırma yarıkları (elektrik.md:499); akü (K30) → akü takozu. Montaj (M6): 33 (etek, H1/H2), 4 (akü takozu, öne alınır). Takvim: ≈ S+2,8 → S+4–4,5.

| Modül | Parça | Adet | Malzeme | g/adet | sa/adet | Bağlı olduğu kalem | M6 adımı | Not |
|---|---|---|---|---|---|---|---|---|
| taban | Akü ön takozu | 1 | PETG | 72 | 1,50 | Akü (K30) gelince ölçü teyidi | 4 (B1a) | Parti 1 arasında basılır (M6 adım 4 taban aşamasında lazım; proje-plani.md kritik yol 4–5) |
| kabuk | Etek arka sağ | 1 | PETG | 366 | 7,60 | E7 havalandırma yarıkları CAD'e; ana anahtar (M6 K7) + XT60 + H1 (K5) | 33 (F1) |  |
| kabuk | Etek arka sol | 1 | PETG | 362 | 7,50 | E7 havalandırma yarıkları CAD'e; ana anahtar (M6 K7) + XT60 + H1 (K5) | 33 (F1) |  |
| kabuk | Etek orta sağ | 1 | PETG | 217 | 4,50 | E7 havalandırma kararı | 33 (F1) |  |
| kabuk | Etek orta sol | 1 | PETG | 217 | 4,50 | E7 havalandırma kararı | 33 (F1) |  |
| kabuk | Etek ön sağ | 1 | PETG | 372 | 7,70 | E7 havalandırma kararı | 33 (F1) |  |
| kabuk | Etek ön sol | 1 | PETG | 363 | 7,60 | E7 havalandırma kararı | 33 (F1) |  |
| kabuk | Etek dolgu şeridi arka | 1 | PETG | 98 | 2,00 | — | 33 (F1) |  |
| kabuk | Etek dolgu şeridi ön | 1 | PETG | 107 | 2,20 | — | 33 (F1) |  |
| kabuk | Etek servis kapağı H1 (sigorta kutusu) | 1 | PETG | 24 | 0,50 | — | 33 (F1) / F5 (M6 K5) |  |
| kabuk | Etek servis kapağı H2 (ana sigorta) | 1 | PETG | 14 | 0,30 | — | 33 (F1) / F5 (M6 K6) |  |

## Takvim kontrolü (paylaşımlı yazıcı, haftada 32–40 sa)

Durum A sırası: Parti 1 S−0,5'te başlar, Parti 2 en erken S+1 (servo gelir), partiler tek yazıcıda sırayla; akü takozu Parti 1 arasında.
Değerler S'ye göre hafta (parti bitişi, üst süreyle).

| Parti | 40 sa/hf | 32 sa/hf | `proje-plani.md` (Durum A) | Fark (32 sa/hf) |
|---|---|---|---|---|
| 1 | S+1,26 | S+1,70 | S+1,5 | +0,20 hf (≈ +1 gün) |
| 2 | S+1,98 | S+2,60 | S+2,3 | +0,30 hf (≈ +2 gün) |
| 3 | S+2,38 | S+3,09 | S+2,8 | +0,29 hf (≈ +2 gün) |
| 4 | S+3,49 | S+4,48 | S+4–4,5 | −0,02 hf (≈ 0 gün) |

Okuma: haftada 40 sa'te her parti plandan önce biter. 32 sa'te ara bitişler 1–2 gün kayar (Parti 1 ≈ S+1,70, Parti 2 ≈ S+2,60, Parti 3 ≈ S+3,09), baskının sonu (≈ S+4,48) plandaki ≈ S+4,5 ile aynı kalır; aşama 8'in ilk adımları (S+3) Parti 2'yi beklemez. Plan Parti 1'i ≈ 34,5 sa/hf ile hesaplamış (69 sa / 2 hf). Asıl risk sayı değil bağımlılık: Parti 1 STL dışa aktarmaya (FreeCAD, açık iş), Parti 2'nin göbeği K39 / P6.1'e, Parti 3 QLED'e (K32) ve K2'ye (P6.1), Parti 4 E7 havalandırma CAD'ine bağlı. Öneriler günlükte (`F4c-gunluk.md`), `proje-plani.md` değişmedi.
