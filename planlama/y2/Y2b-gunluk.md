# Y2b — veri / belge güncellemesi (1,65 m) — günlük

Brief: `planlama/y2/Y2b-brief.md`. **Önce bu günlüğü ve `git status`'u oku, yapılanı tekrarlama.**

## Plan
| # | İş | Durum |
|---|---|---|
| 0 | Okuma (dongu, Y2a kontrol/günlük, kararlar, arayuz, hedef belgeler, main'deki mikrofon) | ✅ |
| 1 | Maliyet (`maliyet.json` + türevleri) | ✅ |
| 2 | Baskı listesi | ✅ |
| 3 | Elektrik / akü belgeleri | ✅ |
| 4 | İvme sınırı hesabı + arayuz notu + eklem_sinirlari üretimi | ✅ |
| 5 | README, proje planı, demodan lidar/otonomi | ✅ |
| 6 | Y2a belge düzeltmeleri (başlık, sehim) | ✅ |
| 7 | `kabuk_rapor.py` | ✅ |
| 8 | dongu.md, commit | ✅ |

## Günlük
- 2026-10-29: başladı (HEAD `2b07779`). Okundu: dongu.md, Y2a-kontrol, Y2a-gunluk, Y2a-brief, kararlar-2026-10-29.
  Lidar/otonomi: `c8c4de7` demoya "Otonomi (öneri)" düğmesi + paneli eklemiş; hoca kararı 21.10 "otonomi iptal, ROS 2 yok"
  (DuffyOS günlüğü) ve taslak-170 "otonomi kapsam dışı" → demodan kaldırılacak.
- **4 İvme (bitti).** Betik `planlama/y2/Y2b-ivme.py` → `Y2b-ivme.json` (FreeCAD, ~2 dk). Yöntem Y2a kontrolünün aynısı
  (`Y2a-K-devrilme.py`): parça kütle merkezlerinden AM (poz = `moduller.beklenen`, +400 g kablo payı), teker merkez hattı
  x ±216 (iz 432) / z ±185, a_dev = g (d cos θ − h sin θ) / h; pay = a_dev / a_robot, ölçüt ≥ 1,5 ⇒ **a_sınır = a_dev,min / 1,5**.
  Izgara: S1 −45…135 (15°) × S2 5/30/60/90/120 (S1 ≥ 120 → S2 ≤ 117) × dirsek 0/35/70/105, simetrik + tek kol; el yükü 0 / 100 / 500 g
  (her el). Kontrol: ev AM (−0,20; 521,39; −13,15), düz geri 3,233, rampa 5° en kötü geri 2,222 (S1 75/S2 120) → Y2a ile birebir.

  | El yükü | düz, en küçük a_dev (yön, poz) | a_sınır (pay 1,5) | rampa 5°, en küçük a_dev | rampa a_sınır |
  |---|---|---|---|---|
  | 0 | geri **3,089** (S1 75 / S2 120 / dirsek 0); ileri 3,492; yan 3,943 | **2,06 m/s²** | geri 2,222 | 1,48 |
  | 100 g | geri **3,023** (aynı poz); ileri 3,387; yan 3,877 | **2,02 m/s²** | geri 2,157 | 1,44 |
  | 500 g | geri **2,781** (S1 105 / S2 120 / dirsek 35); ileri 3,009 | **1,85 m/s²** | geri 1,915 | 1,28 |

  Örnek el hesabı (ev pozu, düz, geri): d = 185 − 13,15 = 171,85 mm, h = 521,39 → a = 9,81 × 171,85 / 521,39 = 3,233 m/s².
  **Sonuç:** düz zeminde devrilme payı ≥ 1,5'i tutan ivme sınırı **≈ 2,0 m/s²** (el yükü ≤ 100 g; 0,5 kg'da 1,85). Devrilme düzde
  bağlayıcı değil: mevcut **≤ 0,5 m/s²** sınırı korunur (gerekçesi motor: `taban-analiz.json` `motor.duz` 0,5'te sürekli torkun %50'si);
  0,5'te en kötü pay 2,78 / 0,5 = 5,6. Acil stop freni (1,5 m/s², tahmini) düzde pay ≥ 1,85 (0,5 kg) / 2,0 (100 g) ✔; rampada
  ev pozunda 1,58 ✔ (Y2a). Rampada **≤ 0,1 m/s²** (karar 29.10) motor gereğidir: 0,1'de sürekli torkun ≈ %78'i (`motor` rampa5
  0 → 0,5 m/s² arası doğrusal: 4,54 + 0,2 × (6,51 − 4,54) = 4,93 kg·cm / 6,3); eski "rampada ≤ 0,25" (%88) bu kararla kalktı.
  Not: `duzeltme-plani.md` E6 "yazılım freni ≤ 2 m/s²" düzde ileri devrilmede 100 g ile pay 3,387 / 2 = 1,69 ✔, geri yönde 3,023 / 2 = 1,51
  (sınırda), 0,5 kg'da 1,39 ✘ → fren ≤ 2 yalnız el yükü ≤ 100 g iken tutarlı (E6 metnine dokunulmadı; raporda).
  Değişen: `arayuz.py` `eklem_sinirlari()` teker notu, `kod/ortak/eklem_sinirlari.json` (betikle, `--kontrol` güncel),
  `eklem_sinirlari_uret.py` yorumu "1,70 m" → "1,65 m".
- **Yazılım belgeleri (ivme):** `yazilim-plani.md` (3 yer: "rampada ≤ 0,25" → "≤ 0,1 + kollar ev pozunda, düzde ≤ 0,5"),
  `yazilim-notu-stowent-170.md` "1,65 m / akü yerinde" diye yeniden yazıldı (kural 3–4 + tilt ±13 + el yükü ~100 g açık; Y2a KZ1/KZ2 isteği).
- **2 Baskı listesi (bitti).** `omuz/omuz_baski.py` 1650 omuz FCStd'siyle yeniden koşuldu (eski json 25 Ekim, tüp 100 mm idi; yalnız
  üst kol tüpü değişti 41,7 → 54,4 g, 0,87 → 1,13 sa). `planlama/y2/Y2b-baski.py` → `Y2b-baski.json`: **63 adet** (= robot-bom baskı 63),
  7,71–7,77 kg (PETG 6,75, CF 0,97–1,03), ≈ 161–162 sa, destekli 10 adet (omuz 8 + kafa kabuğu sağ ön / sağ arka). `baski-listesi.md`
  yeniden yazıldı (Parti 1 20 / 2 25 / 3 9 / 4 9; göğüs bantları Parti 1'e: Nextion yok). Açık soru: boyun yükseltme adaptörü CAD'de PETG.
- **1 Maliyet (bitti).** `planlama/y2/Y2b-maliyet.py` (bir kez koşar; `adim5/maliyet_duzelt.py` biçimi) → `maliyet.json` 118 → 122 kalem
  (V3'te 97 → 96). Değişenler: omuz DS3235 4 + yedek 1 (1.171,50; DS3218 satırları v1,v2 arşiv), sigma 3,0 m × 934,08 (CNC Marketi
  29 Ekim, satıcı ölçüye keser; eski satır arşiv), göğüs Nextion ve 3 mm akrilik yüz paneli silindi (10" kafada panel yok, CAD'de yok),
  yüz ekranı 7" → 10,1" Waveshare (B) 12.424,50 `elde` (hoca verecek), ReSpeaker → XVF3800 ≈ 5.500 + yönlü mikrofon kolu ≈ 2.000
  (ikisi tahmini, main `raporlar/mikrofon-secimi.md`), servo uzatma 14 → 19 m, ESP32–Pi USB 1,5 → 2 m, PETG 6 → 8 (+1) makara, baskı
  hizmeti 7,7 kg, alt plaka 346 × 500, gövde/etek braketi 10 → 14, T-somun 50 → 60, M4 tırtıllı somun silindi (CAD'de yok), vida /
  somun / pul / ısıl gömme adetleri `robot-bom.csv`'den, M3 saplama satırı eklendi. Toplam (`adim5/maliyet_toplam.py`, V3, yazıcı,
  yedek, %15 pay): ara 86.672,21 → **94.496,38**, genel 99.673,04 → **108.670,84 TL** (+8.997,80), koşullular dahil 105.638,76 →
  **114.636,55**; "elimizdekiler düşülmüş" (Pi, SD, yüz ekranı) 77.940,25; baskı hizmetiyle 114.083,78. Farkın büyüğü: yüz ekranı +9.634
  (hoca verirse 0), mikrofon +4.882, Nextion −9.160, DS3235 +1.035, PETG +778. Demo: `viewer-template.html`'den `c8c4de7` lidar /
  otonomi parçaları ters uygulandı (`git apply -R`, temiz), `demo_uret.py` koşuldu; sayfada "lidar/otonom" 0, betikler `node --check` OK
  (tarayıcıda açılmadı: dosya erişimi verilmedi).
- **3 Elektrik (bitti).** `adim3/elektrik.md`: başa "1,65 m güncellemesi" tablosu; Nextion satırları [ESKİ]; pin tablosunda GPIO2 "boş" →
  K2 (E9 ile çelişiyordu), yedek GPIO16/17; USB 2 m; DS3235 hat yoğun ≈ 5,4 A (> XL4016 5 A önerisi, ölçüm). E8 yeniden:
  `planlama/y2/Y2b-aku.py` → `Y2b-aku.json` (Victron 12,2 / 5,9 / 1,8 sa).
- **5 README / proje planı / demo (bitti).** README: başa "Güncel tasarım: 1,65 m" tablosu, klasör tablosuna freecad / eklem_sinirlari /
  dongu / y2, eski CadQuery bölümleri "geçmiş" diye işaretlendi, otonomi iptali; `proje-plani.md`: 1,65 m tek kaynak cümlesi, kapsam dışı
  (lidar, ROS 2; hoca 21.10), 1,65 m geçişi notu, devrilme riski satırı. Lidar/otonomi demodan kaldırıldı (yukarıda).
- **6 Y2a belge düzeltmeleri (bitti).** `Y2a-gunluk.md` başlığı 1,70 → 1,65, görev satırına direk 1.185,5; sehim: kaynak
  `iskelet-analiz.json` `egilme.en_kotu` iki ayrı değer veriyor: **0,336** = en büyük gerilme pozundaki sehim (S1 90/S2 5 + S1 90/S2 45),
  **0,370** = ızgaradaki en büyük tepe sehimi (iki kol S1 90/S2 5); adlı poz "iki kol öne + 0,5 kg" 0,371. Günlük "en büyük sehim 0,370"
  diye düzeltildi (kontrolün 0,371'i adlı pozun değeri; ikisi de doğru, 0,336 en büyük sehim değil).
- **7 `kabuk_rapor.py` (dokunulmadı).** `A.NEXTION` (satır 191, 281) arıyor → AttributeError. Bu modül rapor üreticisi (kabuk/rapor.html);
  dongu.md'de Y2b "veri/belge" (planlama belgeleri) kapsamında değil, modüllerin yeniden üretildiği **Y4**'e ait (aynı yerde `kabuk_gorsel.py`;
  `rehber/rehber_metin.py` → Y5, sonuç `rapor.html` → Y6).
- **8 Kapanış.** `dongu.md` Y2b satırı + günlük satırı. Tek yerel commit (push yok).

## Kapsam dışı fark edilenler (dokunulmadı)
- `duzeltme-plani.md` E6 "yazılım freni ≤ 2 m/s²": el yükü 0,5 kg'da pay 1,39 (< 1,5); yalnız ≤ 100 g iken tutarlı.
- `yazilim-plani.md`: göğüs ekranı "karar Nextion" satırı ve "Nextion düğmesi" devreye alma metni eski (yalnız ivme satırları düzeltildi).
- `tasarim/freecad/OZET.md`, `taban_rapor.py` metinleri (rampada 0,25, fren tabloları), `Lale-Proje-Ozeti.txt` (125 cm, "rampada ≤ 0,25"),
  `raporlar/kaynaklar/05-fiyat-arastirmasi.md` toplam tablosu (99.673,04): eski → Y4 / Y6.
- `kafa7_parcalar.py` "975" yorumu, kafa10 ısıl gömme kavraması (Y2a kontrol notu) → Y3/Y4.
- Boyun yükseltme adaptörü CAD'de PETG, yük yolunda (PETG-CF kararı açık).
- Bas-konuş düğmesi maliyette duruyor (Efe düğmesiz `SesTetik` seçti; köprü F12).
- Viewer şablonunun geri kalanı (DS3218, 125 cm V3 metinleri) eski CadQuery demosu; yalnız lidar/otonomi çıkarıldı.

## Köprü notuna eklenecekler (main `planlama/kopru-mekanik-yazilim.md`; bu adımda dokunulmadı)
1. F8: düz zeminde ivme ≤ 0,5 m/s² sürer, devrilme sınırı ≈ 2,0 m/s² (el yükü ≤ 100 g); fren ≤ 2 m/s² yalnız el yükü ≤ 100 g iken; rampada ≤ 0,1.
2. M1: `maliyet.json` (lale-duzeltme) güncellendi: XVF3800 ≈ 5.500 + yönlü mikrofon kolu ≈ 2.000 (tahmini); genel 108.670,84 TL.
3. M4: kafa 5 V tepe ≈ 4,1 A (10,1" ekran + XVF3800 varsayımıyla); XVF3800 akımı ölçülmeli.
4. ESP32–Pi USB kablosu 2 m (1,64 m gerekiyor); F6: GPIO16/17 boşaldı, pin tablosunda GPIO2 = K2 düzeltildi.
5. Servo hattı yoğun ≈ 5,4 A (DS3235, uzun kol) > XL4016 5 A önerisi: hat akımı ölçümü (F9 akım ölçerle birlikte düşünülebilir).
