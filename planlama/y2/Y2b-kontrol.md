# Y2b — 1,65 m veri / belge güncellemesi: bağımsız kontrol

Kontrol ajanı (bağımsız; tasarım dosyalarına dokunmaz). Dal `lale-duzeltme`, Y2b commit'i `d823435` (öncesi `2b07779`). Girdi:
`planlama/dongu.md` (Y2b tanımı), `Y2b-brief.md`, `Y2b-gunluk.md` (tasarım ajanı), `kararlar-2026-10-29.md`, `Y2a-kontrol.md`.
Durum: **kapandı — KOŞULLU GEÇTİ** (29 Ekim 2026; aşağıda "Sonuç").

## Yöntem
- `git show --stat d823435`: 24 dosya, hepsi brief kapsamında (`tasarim/solidworks/` commit'te yok, izlenmiyor ✔).
- **Devrilme, bağımsız model (FreeCAD'siz):** `montaj/montaj-analiz.json` 1.073 parçanın kütle ve global merkezinden (ev pozu) kendi
  rijit-gövde zincirim: dirsek (eksen −X, (±216,6; 1.137; −1,25)) → S2 (eksen ±Z, (±185; 1.340; 20,2)) → S1 (eksen −X, (±150; 1.340; 0));
  eksenler `eklemler`'den, +Z ileri (`arayuz.py` 7. satır). Kablo payı 400 g (0; 150; −60), el yükü `DIRSEK.el_ucu` (185; 932,6; −1,25).
  Devrilme hatları dört teker merkezi (`arayuz._X_WH` ±216, `_Z_WH` ±185; taban eklemleri aynı): ileri d = 185 − z, geri d = 185 + z,
  yan d = 216 − |x|; a = g (d cos θ − h sin θ) / h. Izgara tasarımcınınkinden sık: S1 −45…135 (5°) × S2 5…120 (5°) × dirsek 0…105 (15°),
  simetrik + tek kol. Not: montaj dosyası S2 = 0'da kayıtlı (S2 5 = +5° döndürme); bunu bulunca ev AM birebir tuttu.
  Betik kontrol scratchpad'inde (depoya yazılmadı).
- **Maliyet:** `adim5/maliyet_toplam.py` yeniden koşuldu (yeni ve `2b07779` sürümü) + kendi filtreli toplamım; adetler `robot-bom.csv`
  bağlantı satırlarından (`N x` çarpanlı) toplandı.
- **Baskı:** `Y2b-baski.json` satırları `robot-bom.csv` Baski satırlarıyla ad ad karşılaştırıldı; toplamlar yeniden toplandı;
  `omuz-baski.json` eski/yeni farkı.
- **Elektrik/akü:** `Y2b-aku.py` scratchpad kopyasında yeniden koşuldu (çıktı birebir) + yoğun senaryo elle; kafa 5 V ve sigorta elle.
- **Demo:** iki HTML'nin satır içi betikleri `node --check`; `python -m http.server` (127.0.0.1) + tarayıcı panelinde yükleme;
  getElementById hedefleri, gömülü `cost` JSON'u ve göreli bağlantılar.
- **Belgeler:** `git grep` (0,25 / ivme / fren / 1,70), `iskelet-analiz.json` `egilme`.

## Bulgular

### 1. Düz zemin ivme sınırı — GEÇTİ
| | ev AM | düz geri / ileri / yan | rampa 5° geri |
|---|---|---|---|
| Bağımsız | (−0,20; 521,39; −13,15), 24.796,0 g | 3,233 / 3,728 / 4,060 | 2,366 |
| Tasarımcı | (−0,20; 521,39; −13,15), 24.796,1 g | 3,233 / 3,728 / 4,06 | 2,366 |

Montaj AM (−0,203; 527,432; −12,385) + 400 g kablo payı = ev AM ✔. Tasarımcının pozlarında birebir: S1 75 / S2 120 / dirsek 0 →
AM (−0,20; 531,37; −17,68), geri **3,089**; 100 g → **3,023**; 500 g S1 105 / S2 120 / dirsek 35 → 2,781.

| El yükü | sık ızgarada en küçük (bağımsız) | a_sınır (pay 1,5) | tasarımcı |
|---|---|---|---|
| 0 | geri 3,089 (S1 70 / S2 120 / d 0); ileri 3,491 (S1 110 / S2 5); yan 3,943 | **2,06** | 2,06 |
| 100 g | geri 3,023 (S1 70 / S2 120); ileri 3,387 | **2,02** | 2,02 |
| 500 g | geri **2,775** (S1 115 / S2 120 / d 60); ileri 3,009 | **1,85** | 1,85 (2,781) |

Sık ızgara tasarımcının 15° ızgarasından en çok %0,2 daha kötü (2,775 / 2,781): sonuç değişmiyor. Kollar ileri (S1 90–110) AM'yi
z −13 → −4,5 (500 g'da +10,9) öne, y 521 → 533 (568) yukarı kaydırıyor; ileri yön 3,49 (3,01). Fren ≤ 2: 500 g'da geri 2,775 / 2 = **1,39** ✘,
ileri 3,009 / 2 = 1,50; 100 g'da 1,51 / 1,69 → iddia doğru (fren ≤ 2 yalnız el yükü ≤ 100 g iken). Rampa 0,1'de motor
4,54 + 0,2 × (6,51 − 4,54) = 4,93 / 6,3 = %78 ✔ (`taban-analiz.json` `motor`). `eklem_sinirlari_uret.py --kontrol` "güncel" ✔.

### 2. Maliyet — GEÇTİ
`maliyet_toplam.py`: V3 96 kalem, ara 94.496,38, genel **108.670,84**, koşullularla **114.636,55** ✔ (kendi toplamım aynı); `2b07779`
sürümü 99.673,04 / 105.638,76 ✔. XVF3800 5.500 + yönlü mikrofon 2.000 = 7.500, ikisi `durum: tahmini`, `stok: belirsiz` ✔. Nextion ve akrilik
panel silinmiş, DS3235 4 + 1 yedek ✔, MG996R 6 (BOM 6) ✔. BOM bağlantı adetleri (M3 DIN 912 174, ISO 7380 96, M5 21, M6×14 36 + ×20 2,
fiberli 8 + 47, pul 32 / 15 / 21 / 16, ısıl gömme M3 142 / M5 13, T-somun 56 + 2, saplama 4) = notlardaki "CAD" sayıları; maliyet adetleri
bunun %5–15 fazlası (pay) ✔. Demodaki gömülü `cost` JSON'u `maliyet.json` ile özdeş ✔.

### 3. Baskı listesi — GEÇTİ
63 adet = `robot-bom.csv` Baski 63, ad ad fark 0 ✔. Filament 7.714–7.772 g (PETG 6.745, CF 969–1.027), 160,6–161,8 sa ✔ (parti 20 / 25 / 9 / 9).
Destekli 10: omuz 8 + kafa kabuğu sağ ön / sağ arka; ikisinin satırında "destekli: dikiş dili (16 mm şerit, ~1,25 mm konsol), karar 29.10" ✔.
`omuz-baski.json` yeniden koşumunda yalnız üst kol tüpü değişti 41,7 → 54,4 g (tüp 100 → 130 mm, ×1,30) ✔.

### 4. Kablo — GEÇTİ (kaynak notlu)
S2 uzatması `dirsek-analiz.json` `kablo.s1_boy` parçalarından: G2 öncesi 20 + geçiş 23,9 + S1 lopu 171,4 + gövde içi 238 + dikey 1.286,5 +
konnektör 30 = **1.769,8 mm** ✔; kol başına 1.926 × 2 + 1.770 = 5,62 m, iki kol 11,24 + (4,3 + 4 × 0,385) 5,84 = 17,08 × 1,1 = 18,8 → **19** ✔.
USB 1,25 + 0,385 = 1,64 → **2 m** ✔. Ama aynı JSON'daki S2 satırı hâlâ "DS3218, 300 mm kablo … uzatma 1.490" (eski yarık yolu;
`dirsek/dirsek_montaj.py:1004` üretiyor) ve `elektrik.md:23` "S2 ≈ 1,77 m" için bu alanı kaynak gösteriyor → kaynak çelişkisi (Y4).

### 5. Elektrik / akü — KISMEN (bir metin çelişkisi)
Hat yoğun: taslak `kol-analiz.json` `yogun_A` 5,43–5,47, tepe 7,84 → "≈ 5,4 A > XL4016 5 A" ✔ (5,47 için "≈ 5,5" daha doğru). Sigorta
7,8 × 6 / 0,88 / 12,8 = 4,16 A ✔. Kafa 5 V: 18,7 − 2,5 (7") − 0,5 (ReSpeaker) + 3,75 (10,1") + 1,0 (XVF3800) = 20,45 W → **4,09 A** ✔.
E8 yoğun (elle): kafa 18,95 / 0,9 + 5 V 1,3 / 0,88 + servo 40,81 / 0,88 + tahrik 39,95 / 0,95 + sabit 2,45 = **113,4 W** → 256 × 0,81 / 113,4 =
**1,83 sa** ✔; `Y2b-aku.py` kopya koşusu `Y2b-aku.json` ile birebir. GPIO2 = K2 pin tablosu ve E9 (`elektrik.md:341, 353`) uyumlu ✔,
GPIO16/17 boş (pin tablosu, 387. satır) ✔; **ama `elektrik.md:355` hâlâ "Artık yedek GPIO yok."** diyor (Y2b'den önce doğruydu).

### 6. Demo — GEÇTİ
`Robot-Tasarim-Demosu.html` ve `cad/viewer-template.html`: "lidar / otonom" 0; satır içi 2 + 2 betik `node --check` OK; kalan `LID*` / `auto` /
`otonomi` başvurusu yok; 40 getElementById hedefinin hepsi sayfada. Yerel sunucuda (127.0.0.1) yüklendi: three.js r128 yüklü, 1 canvas,
sayfa hatası yok, maliyet "108.670,84" görünüyor. Göreli bağlantılar (`freecad/index.html`, `cad/parca-listesi-V2/-V3.csv`,
`cad/Humanoid-Robot-Montaj(-V2/-V3).step`) var ✔.

### 7. Belgeler — KISMEN
README "Güncel tasarım: 1,65 m" tablosu (1.650, direk 1.185,5, 1.073 / 24,40 kg, AM, iz 432 / ±216, 63 parça 6,75 + 1,0 kg, ≈ 108.700 TL)
kaynakla tutarlı ✔; proje planı 1,65 m ✔; `Y2a-gunluk.md` başlığı 1,65 ✔. Sehim: `iskelet-analiz.json` `egilme.en_kotu`
`direk_sehim_mm` 0,336 (en büyük gerilme pozu), `sehim_tepe_mm` **0,370** (ızgara, S1 90 / S2 5), `adli[0]` "iki kol öne + 0,5 kg" 0,371 →
günlükteki düzeltme doğru (mutlak en büyük 0,371 adlı yüklü poz; metin ikisini de veriyor). Etkin belgelerde (README, proje planı,
yazılım planı / notu, elektrik, `eklem_sinirlari.json`) "rampada ≤ 0,1 / düzde ≤ 0,5 / devrilme ≈ 2,0" çelişkisiz ✔. Kalanlar:
- `0,25 m/s²` hâlâ: `tasarim/freecad/OZET.md:28, 43`, `taban/taban_rapor.py:143, 301, 539, 547` (→ `taban/rapor.html`),
  `Lale-Proje-Ozeti.txt:138` (tasarımcı listeledi → Y4 / Y6; `raporlar/` ve `taslak-170/` geçmiş kaydı, sorun değil).
- Fren iki değerli: `duzeltme-plani.md:63` E6 "yazılım freni ≤ 2 m/s²" ↔ `arayuz.py` teker notu / yazılım notu "acil stop freni 1,5
  varsayımı"; 2'de 0,5 kg el yüküyle pay 1,39 (< 1,5). Ancak el yükü ≤ 100 g iken tutarlı (KZ2 açık).
- `Y2a-gunluk.md:114–134` zaman damgaları (03:05–03:35) Y2a kontrolünün işaret ettiği gibi düzeltilmedi (brief'te yoktu; küçük).
- `proje-plani.md:27` H3–4 çıktısı "Sipariş verildi, masa düzeneği konuşuyor" → "Masa düzeneği konuşuyor; taslak 1,70 m" oldu: "sipariş
  verildi" bilgisi brief dışında silinmiş (doğru olabilir; Duffy teyit etmeli).

### 8. dongu.md Y2b tanımı — GEÇTİ
Tanımdaki yedi iş (eklem_sinirlari, maliyet.json, baskı listesi, elektrik/akü, README, proje planı, demodan lidar/otonomi) yapılmış;
`kabuk_rapor.py` (A.NEXTION) gerekçeli olarak Y4'e bırakılmış, dongu.md'de yazılı. Y2a kontrolünün Y2b'ye verdiği yazılım notu güncellemesi
(KZ1 kural 3, KZ2 el yükü ~100 g) yapılmış ✔. Kapsam dışı dosya değişikliği yok.

## Sonuç (29 Ekim 2026) — KOŞULLU GEÇTİ

| # | İddia | Ölçülen (bağımsız) | Durum |
|---|---|---|---|
| 1 | Düz zemin sınırı ≈ 2,0 (2,06 / 1,85); en kötü 3,089 / 3,023; fren ≤ 2 → 1,39 | kendi modelim 3,089 / 3,023 / 2,775; 2,06 / 2,02 / 1,85; 1,39 | GEÇTİ |
| 2 | 108.670,84 (114.636,55); adetler BOM; mikrofon ≈ 7.500 tahmini | aynı; BOM + pay; tahmini işaretli | GEÇTİ |
| 3 | 63 parça, 6,75 kg PETG, 7,71–7,77 kg, ≈ 162 sa, kafa kabuğu destekli | aynı; BOM fark 0; not var | GEÇTİ |
| 4 | S2 ≈ 1.770, 19 m, USB 2 m | 1.769,8; 18,8 → 19; 1,64 → 2 | GEÇTİ (JSON'daki eski S2 satırı) |
| 5 | 5,4 A, kafa 4,1 A, yoğun 1,8 sa, GPIO2/K2, GPIO16/17 | 5,43–5,47; 4,09; 1,83; uyumlu | KISMEN (`elektrik.md:355`) |
| 6 | Demodan lidar/otonomi, sözdizimi | 0 iz; node OK; tarayıcıda hatasız | GEÇTİ |
| 7 | README / plan / Y2a başlık 1,65, sehim 0,370, ivme ifadeleri | tutarlı; eski 0,25 metinleri Y4/Y6'da; fren 1,5 / 2 | KISMEN |
| 8 | dongu.md Y2b eksiksiz | eksik yok | GEÇTİ |

**Düzeltilecek (küçük; Y2b commit'ini durdurmaz):**
- `planlama/adim3/elektrik.md:355`: "Artık yedek GPIO yok." → "yedek GPIO16 / 17 (Nextion kalktı, Y2b)".
  - KARAR 29.10: düzeltildi ("GPIO16 / 17 boş").
- `tasarim/freecad/dirsek/dirsek_montaj.py:1004` → `dirsek-analiz.json` `kablo.s1_boy` S2 satırı (DS3218, yarık yolu, 1.490) göbek eki
  yoluna (≈ 1.770) çevrilmeli; `elektrik.md:23` bu alanı kaynak gösteriyor (Y4, modüller yeniden üretilirken).
  - KARAR 29.10: betik düzeltildi (S2 = G2 öncesi + dirsek / bilekle aynı yol ≈ 1.770); JSON FreeCAD'le Y4'te yeniden üretilir; `elektrik.md` kaynağı Y2b hesabına (1.769,8) çevrildi.
- 0,25 m/s² artıkları: `OZET.md:28, 43`, `taban_rapor.py:143, 301, 539, 547`, `Lale-Proje-Ozeti.txt:138` (Y4 / Y6).
  - KARAR 29.10: Y4 / Y6'ya bırakıldı (dokunulmadı).
- `Y2a-gunluk.md:114–134` zaman damgaları (isteğe bağlı).

**Duffy kararı gerektirenler:**
- **Fren sınırı:** E6 "≤ 2 m/s²" el yükü 0,5 kg'da pay 1,39. Ya el yükü ≤ 100 g kararı (KZ2) ya da fren ≤ 1,85 m/s² (0,5 kg'da pay 1,5).
  Belgelerde tek fren değeri seçilmeli (1,5 varsayım mı, ≤ 2 sınır mı).
  - KARAR 29.10: tek fren değeri **≤ 1,8 m/s²**; düzde pay 0,5 kg 1,54 / 100 g 1,68 / yüksüz 1,72 (`Y2b-ivme.json` `fren_pay`); düz sürüş ≤ 0,5, rampada ≤ 0,1 kalır. Açık: rampada 1,8 frende ev pozu payı 1,31 → rampada yavaşlama da ≤ 0,1 önerildi.
- **Servo hattı ≈ 5,5 A > XL4016 5 A:** ölçüm, gerekirse hat başına 20 A düşürücü (maliyet etkisi).
  - KARAR 29.10: sağ kol / sol kol ayrı XL4016, kafa pan + tilt üçüncü XL4016 (3 → 4): kol hattı yoğun 4,87 / tepe 7,24 A, kafa 1,5 / 5,0 A; genel 109.001,35 TL. Ölçüm yine gerekli.
- **Akü:** yoğun kullanımda 1,8 sa, fuar karışımı 5,1 sa (8 saatlik fuar için öğle şarjı ya da ikinci akü; değişmedi).
  - KARAR 29.10: gereksinim 2 saat kullanım; yoğun kullanımda hesaplanan 1,83 sa Duffy tarafından kabul edildi (29.10). Normal 5,9 sa. Tasarım değişikliği yok.
- `proje-plani.md:27`: "sipariş verildi" silinmesi doğru mu.
  - KARAR 29.10: sipariş verilmedi; sipariş listesi hocaya iletildi (17 Ekim listesi). Fark: `planlama/siparis-farki-2026-10-29.md`.

### Değiştirilen / eklenen dosyalar
Yalnız `planlama/y2/Y2b-kontrol.md` (bu). Bağımsız devrilme betiği ve akü kopya koşusu kontrol scratchpad'inde; tasarım dosyalarına
dokunulmadı.
