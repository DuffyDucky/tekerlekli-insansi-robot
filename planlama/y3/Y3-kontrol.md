# Y3 — M6 CAD (erişim düzeltmeleri): bağımsız kontrol

Kontrol ajanı (bağımsız; tasarım dosyalarına dokunmaz). Dal `lale-duzeltme`, Adım 0 `59367ab`, Y3 `87473ae` (öncesi `c32e0d7`). Girdi:
`planlama/dongu.md` (Y3 tanımı), `Y3-brief.md`, `Y3-gunluk.md` (tasarım ajanı), `kararlar-2026-10-29.md`, `adim4/M6-montaj-sirasi.md`.
Durum: **kapandı — KOŞULLU GEÇTİ** (29 Ekim 2026; aşağıda "Sonuç").

## Yöntem
- `git show --stat`: `59367ab` 12 dosya, `87473ae` 48 dosya; hepsi brief kapsamında (`tasarim/solidworks/` izlenmiyor, commit'te yok ✔).
- **Erişim:** `Y3_erisim.py` scratch kopyasıyla (çıktı scratch'e) modül FCStd'lerinde yeniden koşuldu; `Y3-erisim-sonra.json` ile sayaç ve
  bağlantı bağlantı sonuçlar birebir. Ek olarak kendi FreeCAD betiğim: (1) **takma yolu** — cıvatayı baş yönünde 0…16 mm kaydırıp
  göbek / ön kol ile ortak hacim (alet değil, cıvatanın kendisi kanaldan geçer mi); (2) cep somunlarının cepten çıkış yolu (S2 −z, dirsek
  ve tilt −x, 12 mm) ve oturma boşluğu; (3) ana montajda Y3'te yeni / değişen 149 parçanın 1.120 parçayla çakışması (bb ön süzgeç, 0,5 mm³).
- **Devrilme:** `planlama/y2/Y2b-ivme.py` scratch kopyası (yalnız çıktı yolu farklı) yeni modül JSON'larıyla koşuldu; montaj kütle / AM
  `montaj-analiz.json` 1.120 parçadan kendi toplamım.
- **Kabuk / taban:** `kabuk-analiz.json`, `taban-analiz.json` sayıları yeniden sayıldı; baskı ölçüm yöntemi `kabuk_montaj.py:298-386`
  okundu; K4 / H1 / K7 geometrisi `kabuk_parcalar.py` farkından ve bindirme vidası listesinin önce / sonra karşılaştırmasından.
- **Maliyet:** `adim5/maliyet_toplam.py` üç sürümde (`c32e0d7`, `59367ab`, `87473ae`); BOM farkı `git diff robot-bom.csv`; demodaki gömülü
  `cost` JSON'u = `maliyet.json`. `eklem_sinirlari_uret.py --kontrol`. Belgeler `git grep`.

## Bulgular

### a. Erişim (C1–C3) — KISMEN (C1 kanalı cıvata başını geçirmiyor)
`Y3_erisim` yeniden koşusu: göbek–horn 4 DÜZ, S2 4 DÜZ + 2 açık ağız + 2 CEP, dirsek 8 DÜZ + 8 CEP, tilt 4 DÜZ + 2 açık ağız + 2 CEP,
saplama 4 LOKMA → YOK 0 ✔ (önce modülde 2 + 2 + 5 + 1 = **10**; robotta iki kolla **19**, `M6-montaj-sirasi.md:38`). Günlük / dongu.md /
commit mesajındaki "12" aritmetik hata (19'un hepsi C1–C3'e düşer).
- **C1 ✘:** Ø5 kanal 2,5 alyanı (r 2,05) geçiriyor ama M3 DIN 912 başı Ø5,5 (CAD'de ölçüldü). Takma taraması: z +6'daki iki cıvata baş
  yönünde 7,5 mm kayınca göbeğe girmeye başlıyor, 8–14 mm'de 8,56 mm³ (havşa Ø6,6 x 169'da bitiyor, kanal Ø5). Havşa yanal kapalı, S2
  penceresinden indirilen cıvata da x 168,5…174,5 boğazından geçemez → **bu iki cıvata takılamaz** (z −6'dakiler 0). M6 planı Ø6 diyordu.
  DÜZELTİLDİ 29.10: kanal Ø6; aynı tarama 0…45 mm'de dört cıvata 0 mm³ (aşağıda "Düzeltilecek" 1).
- C2 ✔: Ø8 delik M4 DIN 912 başını (dk 7) ve 3 alyanı geçiriyor; takma taraması 0. Dirsek / tilt / S2 cepleri s 7 + 0,2 = 7,2, derinlik
  m 5 + 0,2; 30° döndürme testi kilitli (CEP), cepten çıkış yolları açık (0 mm³), oturmada ortak hacim 0.

### b. Kabuk — GEÇTİ (notlu)
312 parça (baskı 28, bağlantı 270, satın 14), çoklu katı 0 (kendi sayımım), çakışma 0 / 767 çift, braket 14/14, kapak cıvatası 8/8,
bindirme **vidası** 84/84 (bindirme boşluğu çiftleri ayrı: 33/33, en az 0,188 ≥ 0,15). Desteksiz ölçümü: 1 mm katman dilimi, önceki
katman 1 mm ofset (45°) dışında kalan bölge 1 mm içe ofsetten sonra > 15 mm ise sorun; 28/28 bu ölçütle temiz ✔. Sınırı: ilk 0,5 mm'yi
görmez — üst arka kapakta 28,8 cm² (%5,5) çıkıntı tablaya 0,05…0,4 mm yükseklikte (dış yüz kavisli, kalınlık 3,0, parça 3,4): pratikte
tablaya çöker, dilimleyicide bakılmalı. K4: 1268 dikişi arka bindirmesi ±93 / ±120'ye kaçtı, göğüs sağ / sol arka x0 cıvataları (1130 / 1215)
kalktı; arkada iki yarıyı artık kapağın 7 M3'ü bağlıyor (kapak açıkken göğüs arkası y 1100…1268 serbest; servis için kabul). H1 ±32:
dolgu şeridi tek katı, iki yanda 6 mm et, kapak vidaları şeridin dışında (x ±50) ✔. Ø30 anahtar deliği H1 kapağına 8,4 mm, düğme
zarfı (Ø40) 3,4 mm ✔. **Sigorta erişimi:** kutu 105 × 60, açıklık 64 × 50; 2 × 3 dizilişte altı sigorta açıkta, 1 × 6 dizilişte uçtaki
ikisi kapak altında → gerçek kutu seçilince karar (bkz. Duffy). **K1 vida boyu:** M5×16 ucu braket iç yüzünden 3,3 mm içeride; perçin
somunun dişi gövdenin uç kısmındadır (yakın kısım çökme bölgesi) → kavrama ~2 diş olabilir; kontrol yalnız "dibe vurmuyor" bakıyor.

### c. Taban — GEÇTİ
355 parça (342 + 13 referans), bağlantı 127/127 (XL4016 C ve ön şarj kartı burçları 8/8), iç çakışma 0 / 575 çift, taban × kabuk 0,
bölge 48 / 0. XL4016 C güç paneli üstünde (x 65…130, z ±23,5), akünün önünde (akü z ≤ −29; alt vidalar z ±15,8 → akü üstüne gelmez ✔);
yük 1,5 / 5,0 A, ısı sorunu yok. Ön şarj kartı (x −132,5…−62,5) K1'den ~135 mm (elektrik.md:370 "K1 yanında" gevşek ama kablo kısa, akım
anlık). Zarf yüksekliği 10,1 mm < JQC-3F 15,5 + pertinaks 1,6; bölge 28 mm bunu karşılıyor. Kablo yolu C yalnız direk üstünden (y 1285+)
çizili; taban → direk kısmı yok (Y4 / rehber).

### d. Ana montaj ve devrilme — GEÇTİ
1.120 parça, 24.554,2 g, AM (−0,079; 525,807; −12,491) kendi toplamımla ✔. Yeni / değişen 149 parça × 1.120: 2.229 çift, çakışma 0.
`yerlesim-kontrol.json`: ev 0, kol 40 poz 0, kafa 15 poz 0 (kafa süpürmesinde bb çifti hiç oluşmuyor; zayıf ama `c32e0d7`'de de aynı).
Devrilme (Y2b-ivme yöntemi, yeni AM; ev + 400 g kablo (−0,08; 519,83; −13,25)): düz ileri / geri / yan 3,741 / 3,241 / 4,075, rampa 5° geri
**2,374**. Izgarada en küçük (düz) 0 / 100 / 500 g: **3,097 / 3,031 / 2,789** → fren 1,8'de pay **1,72 / 1,68 / 1,55** (≥ 1,5 ✔); rampa en
kötü 2,230 (yüksüz) / 0,1 = 22 ✔. Y2b'den (3,089 / 3,023 / 2,781) biraz iyi.

### e. BOM ve maliyet — GEÇTİ
BOM farkı: XL4016 3 → 4, M5 ısıl gömme 13 → 5, + M5 perçin 8, + M3 perçin 6, M5×16 ISO 7380 8, M3×14 ISO 7380 6, M5×10 −8, M5 pul 21 → 13,
pertinaks kartı +1, burç 36 → 44, Pi 4GB ✔. `maliyet_toplam.py`: `c32e0d7` 109.001,35, `59367ab` **103.166,51** (ara 94.783,78 → 89.710,01
= 12.105,35 − 7.031,58 = 5.073,77 × 1,15 = 5.834,84 ✔), `87473ae` **103.767,58** (99 kalem, ara 90.232,68; +601,07), koşullularla 109.056,64 ✔.
Maliyet adetleri BOM + pay (M5×16 9, M3×14 7, perçin 16) ✔; demo `cost` = `maliyet.json` ✔.

### f. Adım 0 ivme sabiti — GEÇTİ
`arayuz.py:698` `ivme_sinir_m_s2` (0,5 / 1,8 / 0,1 / 0,1) → `eklem_sinirlari.json` `teker`; `--kontrol` "güncel". README, proje planı,
yazılım notu kural 3–4, `duzeltme-plani.md` E6, `elektrik.md` çelişkisiz. Eski 0,25 metinleri (OZET.md, taban_rapor.py) Y4 / Y6'da.

### g. dirsek-analiz.json S2 — KISMEN
`kablo.s1_boy.uzatma[2]` S2 (DS3235) 20 + 23,9 + 171,4 + 238 + 1.286,5 + 30 = **1.770** ✔ (Y2b 1.769,8). Ama `elektrik.md:24` hâlâ "JSON'daki
S2 satırı hâlâ eski yarık yolu 1.490 … Y4'te yeniden üretilir" diyor → artık yanlış. DÜZELTİLDİ 29.10 ("Düzeltilecek" 2).

### h. dongu.md Y3 tanımı — GEÇTİ
C1–C3, K1–K7 ve ön şarj kartı yapılmış (C1 kusurlu, a). Y4'e bırakılanlar gerekçeli: tam tarama (dongu.md kuralı: tek sefer Y4'te),
`M6_erisim` / `M6_ek` (adım seçicileri 125 cm y eşikleri; Y3_erisim hedefli yerine geçti), `dirsek_montaj` K3 sonrası (yarık yalnız malzeme
kaldırır). Y4 için ek: `M6_erisim.py:27` `ISO7380_S`'de M5 yok → yeni M5×16 ISO 7380 erişim koşusunda sessizce atlanır.

## Sonuç (29 Ekim 2026) — KOŞULLU GEÇTİ

| # | İddia | Ölçülen (bağımsız) | Durum |
|---|---|---|---|
| a | YOK 12 → 0; Ø5 / Ø8 / cepler | YOK 10 (robot 19) → 0; Ø5 başı geçirmiyor (2 cıvata takılamaz); Ø8 ve cepler doğru | KISMEN |
| b | 312, 0, 14/14, 84/84, 8/8, 28 desteksiz | aynı; 84 = bindirme vidası; yöntem ilk 0,5 mm'yi görmez; H1 erişimi kutuya bağlı | GEÇTİ (notlu) |
| c | 355, 127/127, 0; XL4016 C + ön şarj | aynı; yerleşim ve ısı makul | GEÇTİ |
| d | 1.120, 24.554,3, AM; 0 çakışma; paylar | aynı; yeni parçalar 0; fren 1,8 pay 1,72 / 1,68 / 1,55, rampa ≫ | GEÇTİ |
| e | BOM farkı, 103.767,58, Pi geçişi | aynı | GEÇTİ |
| f | ivme JSON betikle, belgeler | güncel, çelişkisiz | GEÇTİ |
| g | dirsek S2 1.770 | JSON doğru; `elektrik.md:24` eski | KISMEN |
| h | dongu.md eksiksiz | eksik yok, Y4 gerekçeleri yerinde | GEÇTİ |

**Düzeltilecek (koşul: 1. madde Y4 başlamadan):**
1. `tasarim/freecad/arayuz.py:860` `gobek_horn_kanal` d 5,0 → **≥ 6,0** (M3 DIN 912 başı 5,5 + pay; havşa 6,6) ya da cıvatalar z −6'ya
   (M6 planı C1 b); `omuz_montaj` + ana montaj yeniden, takma (cıvata başı) kontrolü eklenmeli.
   DÜZELTİLDİ 29.10: d 6,0 (plaka eti kanal altında 0,51 mm, taşıyıcı değil; z −6 gerekmedi); takma taraması 0…45 mm → 4 cıvata 0 mm³;
   omuz, iskelet, dirsek, ana montaj, taban, yerleşim, `Y3_erisim` yeniden (1.120 parça, 24.554,1 g, AM y 525,80; çakışma 0). `Y3-gunluk.md`.
2. `planlama/adim3/elektrik.md:24`: "S2 satırı hâlâ eski … Y4'te yeniden üretilir" → "Y3'te yeniden üretildi, 1.770 mm".
   DÜZELTİLDİ 29.10: cümle "Y3'te `dirsek_montaj.py` ile yeniden üretildi: DS3235 1.770 mm".
3. "12 YOK" → "modülde 10, robotta 19": `planlama/dongu.md:60`, `planlama/y3/Y3-gunluk.md:22` (commit mesajı geçmişte kalır).
   DÜZELTİLDİ 29.10: iki yerde "modülde 10 / robotta 19" (`M6-montaj-sirasi.md:38` kaynağıyla).
4. `planlama/adim4/M6_erisim.py:27` `ISO7380_S`'e `"M5x": 3.0` (Y4 koşusundan önce).
   DÜZELTİLDİ 29.10: eklendi (ISO 7380-1 M5 s 3); kısa koşuda 8 M5×16 artık atlanmıyor (kabukta 8 DÜZ, alyan 3).
5. Küçük, Y3 öncesinden: `elektrik.md:296-299` sigorta seti paragrafı "yuvalar × 3", "7,5 A × 2 + şarj 10 A" (C hattının 5 A yuvası yok;
   maliyet 4 yuva).
   DÜZELTİLDİ 29.10: 7,5 A × 2 + 5 A (C) + şarj 10 A, yuva × 4, ek bıçak sigorta 6 (`maliyet.json` ile aynı).

**Duffy kararı gerektirenler:**
- **H1 sigorta erişimi:** gerçek 6 yollu kutu 1 × 6 dizilişliyse uçtaki iki sigorta kapak altında kalır. Seçenek: (a) kutu seçilince ölç,
  uç yuvalara yedek / boş koy; (b) dolgu şeridi dikişlerini kaydırıp açıklığı ±44'e çıkar (kabuk yeniden).
  KARAR 29.10: (a) açıklık ±32 kalır; kutu alınınca ölçülür, uçtaki iki yuva yedek sigorta için ayrılır (`elektrik.md`, karar 14).
- **K1 M5 boyu:** perçin somun tipi seçilince diş boyuna göre M5×16 yeterli mi bak; yetmezse M5×18 (maliyet etkisi yok denecek kadar).
  KARAR 29.10: M5×18 ISO 7380; uzayan uç ana montajda hiçbir parçaya değmiyor (0 mm³), kabuk / ana montaj / taban / yerleşim yeniden,
  çakışma 0, 24.556,6 g; maliyet aynı (karar 15).
- Brief'teki açıklar sürüyor: boyun adaptörü PETG → PETG-CF, KZ2 el yükü ~100 g; K7 delik çapı ve perçin somun ölçüleri tahmini.
  KARAR 29.10: boyun adaptörü PETG-CF (kütle aynı, CF 1,04–1,10 kg, maliyet aynı; karar 13). Pi 5, 4 GB RAM teyit (karar 12).
  KZ2 el yükü, K7 ve perçin somun ölçüleri açık.

### Değiştirilen / eklenen dosyalar
Yalnız `planlama/y3/Y3-kontrol.md` (bu). Erişim kopyası, takma / cep taraması, montaj çakışma ve devrilme betikleri kontrol scratchpad'inde;
tasarım dosyalarına dokunulmadı.
