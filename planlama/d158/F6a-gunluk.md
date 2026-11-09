# F6a günlüğü: tarama kaynakları temizliği + birikmiş model düzeltmeleri + tam çakışma taraması (P6.1, P4.5 kalanı) — tasarım ajanı A, 09.11.2026

Brief: `planlama/d158/F6a-brief.md`. Plan: `planlama/dongu-158.md` §3 F6 (P6.1, P4.5). Dal `lale-duzeltme`. Bu günlükte takma ad yazılmaz; "takma ad" denir.
Kısaltmalar: `TF/` = `tasarim/freecad/`, `KY/` = `TF/lale158/kafa-yerlesim/`, `SP/` = oturum scratchpad klasörü (depo dışı,
`C:\Users\Victus\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad\f6a`). Önceki durumun kopyaları `SP/once/`
(`src/` değişen kaynaklar, `json/` `TF/` altındaki bütün izlenen JSON/CSV'ler, `kod/ortak/eklem_sinirlari.json`, regresyon tabanı, baskı listesi, `Y2b-baski.json`).
FreeCAD 1.1, başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py`. Tek tek koşular `SP/fc.sh` (F2 `fc.sh` kopyası), zincirler `SP/zincir.py` / `SP/zincir2.py`
(her adımdan önce boş bellek ≥ 2 GB ve çalışan `freecadcmd`/`freecad` 0 denetimi, koşu boyunca 5 dk'da bir boş bellek `SP/bellek.log`'a, adım başarısızsa durur,
yeniden başlatmaz; özet `SP/zincir_<kosu>.json`, çıktı `SP/zincir.out`).

## 0. Başlangıç (08:33)
- `py -3 planlama/d158/regresyon.py --yazma` (08:33:30; taban 07:32:32): çıkış 0, "GEÇER", 10 değer "aynı" (rampa 1,519).
- `py -3 TF/carpisma_kos.py kontrol`: çıkış 0 ("izlenen 17 dosyanin ozetleri kayitla ayni"; F2 sonu).
- Boş bellek 4,48 GB; çalışan FreeCAD süreci yok. F4c commit'li (`f7ed8c4`, `e796f15`; HEAD `e796f15`).
- `git status` başlangıçta (bu paketten önce): `planlama/dongu-158.md`, 13 kabuk görseli + `TF/montaj/yerlesim-kontrol.json` (K23) değişik;
  izlenmeyenler `kvkk/`, `rapor/`, `raporlar/*` (4), `tubitak-2209b/`, `tasarim/solidworks/`, `KY/kaynak/`, `TF/montaj/lale_dongu*`, F5/F5b pano metinleri.

## 1. Kaynak düzeltmeleri (tarama öncesi, hepsi birlikte; 08:34–08:45)

### 1a. Takma ad (P4.5 kalanı)
`git grep -il <takma ad>` başta 11 dosya: `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html` (üçü kapsam dışı: K25, `kod/`, K26) ve 8 tarama kaynağı.
F4b §4'teki 9. dosya `KY/yerlesim_lib.py` HEAD'de zaten temiz (F4b `c7f9af4` ile temizlenmiş; `git show HEAD:… | grep -ic` 0), dokunulmadı.
Hepsi kişiye atıf (karar / ifade sahibi) → "Ahmet"; kişisel tanımlayıcı (hesap, yol) yoktu. Yalnız ad satırları değişti (eklenen = silinen satır).

| Dosya | Değişen satır | Not |
|---|---|---|
| `TF/arayuz.py` | 17 | 16 yorum + `eklem_sinirlari()` teker notu metni (satır ~798; bu metin `kod/ortak/eklem_sinirlari.json:111`'e gider → 1g önerisinde düzelir) |
| `TF/kabuk/kabuk_lib.py` | 1 | yorum |
| `TF/kabuk/kabuk_parcalar.py` | 3 | yorum |
| `TF/kafa/kafa10_lib.py` | 4 | yorum |
| `TF/kafa/kafa_lib.py` | 1 | yorum |
| `TF/kafa/kafa_parcalar.py` | 1 | yorum |
| `TF/omuz/omuz_parcalar.py` | 1 | yorum |
| `TF/taban/taban_parcalar.py` | 2 | yorum |
Sonra `git grep -il <takma ad>`: yalnız `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html` (kapsam dışı üçü). Tarama kaynaklarında 0.

### 1b. `TF/kabuk/kabuk_parcalar.py:733` yorumu
`72 x 10 kopru` → `70 x 10 kopru` (1 satır; kelepçe köprüsü e1 −35…35 = 70, satır 772 ile tutarlı).

### 1c. Kesit kaydırması (P1.5 kalıbı, dört yer)
Kalıp: `TF/kabuk/kabuk_montaj.py` `baski_analiz()` (F1b P1.5; kök neden F1b-kontrol madde 14: kesit düzlemi yatay eksenli deliğe teğet). Teller kapalı değilse
`makeFace` çağrılmaz; düzlem 0,05 / −0,05 / 0,1 / −0,1 / 0,25 / −0,25 mm kaydırılıp yeniden kesilir, yüz katman düzlemine geri taşınır, kaydırılan katman
`kesit_kaydirma` [(z, dz)] olarak yazılır; hiç kapanmazsa "kesit teli kapanmadi" destek sorunu sayılır. Uygulanan yerler (yama betiği `SP/yama_kesit.py`, her eski metin tam bir kez):

| Dosya | Önceki davranış | Şimdi | Satır (+/−) |
|---|---|---|---|
| `TF/kafa/kafa_lib.py` (~265, baskı katman döngüsü) | `slice`/`makeFace` hatası → `yuz=None`, katman sessizce atlanır; geçersiz yüz → `atlanan_katman` | kalıp; ek olarak geçersiz yüzde de kaydırma denenir, yalnız hep geçersiz kalırsa eskisi gibi `atlanan_katman`; yeni alan `kesit_kaydirma` | +32 / −10 |
| `TF/dirsek/dirsek_lib.py` (~141) | hata → katman sessizce atlanır | kalıp birebir; yeni alan `kesit_kaydirma` | +24 / −6 |
| `TF/omuz/omuz_baski.py` (~201, `kesit()`) | `kesit()` hata / geçersiz yüzde `None` → `atlanan_kesit` | yeni `kesit_k()` kaydırmayı dener (açık tel ve geçersiz yüz), `kesit()` onu sarar; hep açık kalırsa `bolgeler`'e "kesit teli kapanmadi" (destek=True, tur hata; kabuk ile aynı anlam); yeni alanlar `kesit_kaydirma`, `kesit_kaydirma_sayi` | +40 / −13 |
| `KY/uygulama_tani.py` (~30, tanı betiği) | `makeFace` hatası betiği durdururdu | kalıp; katman kaydına `kaydirma` (dz) | +21 / −2 |

Sonuç sayıları (önce `SP/once/json/…` ↔ sonra depo; karşılaştırma `SP/baski_ozet.py`, `SP/jfark.py`):

| Modül (JSON) | Kaydırılan katman | Kapanmayan (yeni sorun) | Önce → sonra sayısal fark | Not |
|---|---|---|---|---|
| kafa (`TF/kafa/kafa-analiz.json` `baski[]`) | **0** (14 parça) | 0 | `destek_sorun_sayi` toplam 3 → 3, `atlanan_katman` / `kutle_g` / `cikinti_orani` aynı | yalnız boş `kesit_kaydirma` alanları eklendi (+15 satır) |
| dirsek (`TF/dirsek/dirsek-analiz.json` `baski[]`) | **0** (4 parça) | 0 | `destek_sorun_sayi` 0 → 0; baskı sayıları aynı | ayrıca `tork.grup.omuz_Gobek.am` 173,983 / 7,611 / −2,322 → 173,982 / 7,606 / −2,321 (1d kök dolgusu, kesitle ilgisiz) |
| omuz (`TF/omuz/omuz-baski.json` `parcalar[].yonler`) | **0** (6 parça × 6 yön) | 0 | `atlanan_kesit` hepsi aynı; seçilen yönler ve `destek_filament_g` aynı (göbek +X, 5,7 g) | göbek değişimleri yalnız 1d dolgusundan: +Y `destek_alan_mm2` 1488,7 → 1456,9, bölge 7 → 8; −X 2763,7 → 2618,4; +Z 3617,4 → 3617,8; −Z 3191,2 → 3191,6 (seçilmeyen yönler) |
| uygulama_tani (`KY/uygulama-tani.json`) | §2.3'te | | | |
| kabuk (kalıbın kaynağı, değişmedi) | 16 (önceki gibi) | — | `kabuk-analiz.json` `sure_s`/`tarih` dışında **0 fark** (`SP/jfark.py`); `destek_sorun_sayi` 31 → 31 | karşılaştırma için |
**Sayısal etki:** üç modülde kesit düzlemi hiçbir katmanda açık tele / geçersiz yüze düşmedi; eski "sessizce atla" yolu bu modelde hiç tetiklenmiyormuş. Kalıp artık gizli
katman kaybını görünür kılıyor (ileride bir geometri değişikliğinde sessiz kayıp olmaz). Baskı sayıları değişmedi.

### 1d. Omuz durdurucu dişinin kökü (F2 B-2)
**Geometri** (`SP/probe1.py` → `SP/probe1.json`, 3 s): dişin +x (çekme) yüzü 4,3° eğik (`x = 166,673` @ y −23, 167,5 @ y −34); iç duvar (x 163…168) alt yüzü
y −23'te; dişle duvarın +x yüzü (x 168) arasında 1,33 mm'lik basamak; z 2,5…7,5'te basamağın üstünde S2 plakası (alt yüzü y −22). Keskin iç köşe (85,7°) (166,673; −23)'te.
r 1,5'lik yay iki yüze birden teğet **sığmıyor** (basamak 1,33 mm; en çok r 1,23). Bu yüzden: **r 1,5 yay** dişin yüzüne y −25'te teğet başlar, **duvar köşesine
(168; −23) teğet doğruyla** biter. Yüzey dişten yaya teğet sürekli; doğru x 168 yüzüne 138°'lik dış köşeyle bağlanır; basamak (keskin iç köşe) ortadan kalkar.
- `TF/arayuz.py` OMUZ `durdurucu`: yeni `kok_r=1.5`, `kok_teget_y=-25.0` (+ açıklama yorumu). 
- `TF/omuz/omuz_parcalar.py`: `_kok_dolgu()` (yay + teğet doğru + malzeme içine örtüşen kapanış; z −8…21, diş genişliği), `DURDURUCU = DURDURUCU.fuse(KOK_DOLGU)`;
  "Omuz gobegi" notuna "kok ic kosesi r 1.5 yay (F6a)". +42 / −3 satır (1'i 1a).
- Noktalar (`SP/olc_dis.json` `kok_nokta`): T (166,8233; −25,0) yay başı, O (168,3191; −24,8875) merkez, U (167,2043; −23,884) yay sonu, K (168; −23).

**Ölçüm** `SP/olc_dis.py` (freecadcmd, 08:42:09–08:43:00, 51 s, rc 0; F2 `olc_f2.py` c / a / b yöntemi; sonuç **`SP/olc_dis.json`**, log `SP/olc_dis.log`):

| Ölçüm | F2 (`SP/../f2/olc_sonra.json`, F2-kontrol) | F6a | JSON anahtarı |
|---|---|---|---|
| Kol çatalı ↔ diş ilk temas | 4,3002° (B 4,3003) | **4,3002°** | `c_kol_x_durdurucu.sonuc.temas` |
| S2 5°'te dişe boşluk | 0,344 mm (B 0,3436) | **0,3436 mm** | `c_kol_x_durdurucu.noktalar.5.00.mesafe` |
| Ortak hacim 4,29° / 4,2° / 3,8° | 0,70 / 7,09 / 36,46 mm³ | 0,7047 / 7,0917 / 36,4592 | `noktalar` |
| Temas yüzü | 133,17 mm², kutu x 167,156…167,5, y −34…−29,421 | aynı | `temas_yuzu_alan_mm2`, `temas_yuzu_kutu` |
| Kuvvet kolu (S2 ekseni) | 30,30 mm | 30,296 mm | `kuvvet_kolu_mm` |
| Diş hacmi / geçerli / katı | 2975 mm³ (`darbe.json`) | 3021,5 mm³ / true / 1 | `durdurucu_hacim_mm3` … |
| Kol ↔ S1 tamburu ilk temas; 4,3° / 5°'te boşluk | 3,647°; 0,400 / 0,825 | 3,647°; 0,4002 / 0,825 | `a_kol_x_gobek.S1 kablo tamburu` |
| Kol ↔ tüm göbek ilk temas | 4,2998° | 4,2998° | `a_kol_x_gobek.Omuz gobegi` |
| Kol ↔ kabuk (S1 20/90/140), 4,3° / 5° | 0,831 / 1,358 mm | 0,8309 / 1,3582 mm (S1 0: 2,195 / 2,690) | `b_kol_x_kabuk` |
| Kök dolgusu: hacim (örtüşme dahil), geçerli | — | 97,69 mm³, tek katı, geçerli; göbek tek katı, geçerli, 54.000,3 mm³ | `k_kok_dolgu` |
| Kol ↔ kök dolgusu en küçük boşluk, S2 0 / 4,3 / 5 / 10 / 30 / 60–90 / ≥ 120 | — | 3,00 / 4,43 / 4,69 / 6,53 / 11,02 / 13,06 / (kutu dışı) mm; S2 −10'da 0,08, −20'de 59 mm³ (aralık dışı, dişin ötesi) | `k_kok_dolgu.kol_mesafe` |
| z 6,5 kesit profili | keskin köşe | doğru (166,823; −25) → (167,5; −34); **yay r 1,5** (166,823; −25) → (167,204; −23,884); doğru → (168; −23) | `k_kok_dolgu.kesit_z6_5_profil` |
| Diş kesit kalınlığı (x 161'den), y −23 / −24 / −25 / −26 / −28 | 5,673 / 5,75 / 5,82 / 5,90 / 6,05 | 7,0 / 6,11 / **5,823** (en ince) / 5,898 / 6,049 | `s_kesit_x_araliklari_z6_5` |
Temas açısı ve 5°'te boşluk **korundu** (temas yüzü değişmedi); dolgu kirişe ≥ 3 mm uzak (S2 ≥ 0).

**Gerilme yığılması** `SP/kt_fem.py` (2B düzlem gerilme, doğrusal üçgen; ağ `gmsh.exe`, çözüm scipy; FreeCAD'in `python.exe`'si, FreeCAD import edilmez; sonuç **`SP/kt_fem.json`**).
Model: diş + kök kolonu (x 161…168, y −34…−10), üst kenar ankastre, temas şeridine (y −34…−29,42) normal yönde yayılı yük. K_t,etkin = FE en büyük asal gerilme
(dişin +x kökü) / F2 nominali (F·h/W, kök y −23, t 5,673, kol 8,71, W 155,5 mm³). Ağ 0,08 / 0,04 / 0,02 mm ile yakınsadı. Doğrulama: kökten uzak kesitlerde (y −26…−28)
FE yüzey gerilmesi kiriş teorisinin 1,1–1,15 katı (kısa, kalın kiriş; oturumda `kt_fem.py` ağı üzerinde elle hesaplandı, JSON'a yazılmadı).

| Geometri | K_t,etkin (h 0,02) | En büyük gerilme yeri |
|---|---|---|
| F6a: r 1,5 yay + teğet doğru | **1,45** (0,08 / 0,04 mm ağda 1,46 / 1,46) | (166,86; −24,52), yayın içinde |
| F2 keskin köşe, baskı iç köşe yarıçapı 0,4 mm (varsayım) | 2,73 | (166,72; −23,26) |
| F2 keskin köşe, 0,2 mm (varsayım) | 3,64 | (166,71; −23,11) |
(Keskin köşe FE'de tekil; gerçek baskıda köşe nozul izinden ~0,2–0,4 mm yuvarlanır, bu yüzden iki varsayım.) Kök yuvarlatması en büyük gerilmeyi **1,9–2,5 kat** düşürür.

**Darbe emniyeti (F2 yöntemi + K_t)** `SP/darbe_f6a.py` (F2 `darbe.py` kopyası; girdi `olc_dis.json` + F2 `olc_sonra.json` `g_eylemsizlik`; gerilme × K_t,etkin) → **`SP/darbe_f6a.json`** `f6a.tablo`.
Malzeme ve izinler F2 ile aynı (PETG-CF XY 59,8 × 0,9 × K_T 0,85; sürekli × 0,45 → 20,6 MPa; darbe 45,7 MPa). Rijitlik F2 varsayımı (k_lin = k_diş/2, kol esnek; kθ 980 N·m/rad).

| Senaryo | Kuvvet (N) | F2 tablosu (K_t yok) | F2 keskin köşe (K_t 2,73…3,64) | **F6a kök r 1,5 (K_t 1,45)** | F6a, rijitlik aralığı (rijit … esnek) |
|---|---|---|---|---|---|
| Stall, statik, sürekli | 98,4 | 3,73 | 1,37 … 1,03 | **2,57** | 2,57 |
| 1,5 rad/s yüksüz | 364 | 2,24 | 0,82 … 0,62 | **1,54** | 0,84 … 1,65 |
| 1,5 rad/s, elde 500 g | 618 | 1,32 | 0,48 … 0,36 | **0,91** | 0,46 … 0,99 |
| Kaçak servo tam hız, yüksüz | 1526 | 0,54 | 0,20 … 0,15 | **0,37** | 0,18 … 0,40 |
| Kaçak servo tam hız, 500 g | 2886 | 0,28 | 0,10 … 0,08 | **0,19** | 0,09 … 0,21 |
| Güç kesik, S2 30°'den düşme | 554 | 1,48 | 0,54 … 0,41 | **1,01** | 0,47 … 1,12 |
| Güç kesik, S2 90°'den | 1526 | 0,54 | 0,20 … 0,15 | **0,37** | 0,17 … 0,41 |
| Güç kesik, S2 120°'den | 1870 | 0,44 | 0,16 … 0,12 | **0,30** | 0,14 … 0,33 |
"Rijit": k_lin = k_diş, kol rijit (B'nin alt ucu); "esnek": k_lin = k_diş/3, kol esnek. İzinli darbe (F6a, F2 rijitliği): emniyet 2 → 281 N, yüksüz **59°/s**, 500 g ile **30°/s**,
güç kesik düşme S2 ≤ **15,5°**; emniyet 1,5 → 375 N, 89°/s / 46°/s, düşme S2 ≤ **20,4°** (hızlar `f6a.izinli`; düşme `f6a.duzeltme1.dusme_S2_derece_servosuz`).
*Düzeltme turu 1 (F6a-kontrol O-2):* ilk sürümdeki düşme sınırı (10,6° / 15,3°) servo stall torkunu düşen formülle hesaplanmıştı; güç kesikken servo torku yok,
doğrusu tepe tork = F·r_F (B'nin `darbe_b.json` sayılarıyla aynı). **Rijitlik aralığı** (`f6a.izinli`, `f6a.duzeltme1`): rijit alt sınırda (k_lin = k_diş, kol rijit)
emniyet 2 için **27 / 14°/s** gerekir ve 59 / 30°/s'de emniyet **1,14 / 1,15** olur; esnek uçta 65 / 33°/s (59 / 30°/s'de 2,13 / 2,14). Düşme sınırı rijitte 8,1° / 10,2°,
esnekte 17,0° / 22,4° (emniyet 2 / 1,5). Yük temas şeridinin ucuna kayarsa (eğilme kolu × 1,26) F2 rijitliğinde emniyet 2 için ≈ 40 / 20°/s (B). Sonuç: 59 / 30°/s,
**F2 rijitlik varsayımında** K38'deki B önerisiyle (≤ 60°/s, yükle ≤ 30°/s) örtüşüyor; rijit alt sınırda bu hızlarda emniyet ≈ 1,15.
**Değerlendirme:** F2'nin K_t'siz sayıları iyimserdi; keskin köşeyle gerçek emniyet stall'da ~1,0–1,4, 1,5 rad/s'de < 1 olurdu. Kök yuvarlatması stall'u 2,57'ye,
1,5 rad/s yüksüzü 1,54'e çıkarır (kabul edilebilir); elde yükle ve kaçak / düşme senaryolarında emniyet < 1 kalır (KT-F6a-2).
Kütle: diş hacmi 2975 → 3021,5 mm³ (+46,5 mm³; dolgunun bir kısmı göbek duvarıyla örtüşür); göbek parçası 53.972,55 → 54.000,26 mm³ (+27,7 mm³),
61,691 → **61,722 g (+0,031 g / omuz**, ρ × doluluk; `TF/montaj/montaj-analiz.json` `parcalar[91]`, `TF/omuz/regresyon/sonra.json`); `omuz-analiz.json` `kutle.Gobek` 177,6 → 177,6 g (grup, 0,1 g yuvarlama).
Görsel: **`planlama/d158/F6a-dis-kok.png`** (z 6,5 kesiti: F2 keskin köşe, F6a yay + doğru, kiriş 4,3° / 5°; çizim `SP/ciz_kok.py`, veri `olc_dis.json`, `kt_fem.json`).

### 1e. "horn/dişli yük almaz" yorumları (F2 B-1)
- `TF/omuz/omuz_parcalar.py:167`: "servo horn'u ve dislisi yuk yolunda degil" → "servo horn'u ve dislisi tork almaz (tork dislilerden once durdurucuda karsilanir);
  carpma kuvvetinin buyuk kismi (~%88) S2 mafsalina radyal yuk olarak gider (horn + servo mili, 625ZZ + M5; F2-kontrol B-1)".
- `TF/arayuz.py` OMUZ durdurucu yorumuna aynı anlamda iki satır ("Yuk yolu (F2-kontrol B-1) …; rotor eylemsizligi dislilerden gecer").
`git grep` ile başka "yük yolunda değil / yük almaz" ifadesi aranıp bulunmadı (`dirsek_parcalar.py:12` "servo mili yanal yuk tasimaz" dirsek pimi için, F2 ile ilgisiz; dokunulmadı).

### 1f. `arayuz.py` `yana_alt_bosluk_mm` ve `eklem_sinirlari()` metni (F2 B-3, K40)
- Eski: `yana_alt_bosluk_mm={0: 4.7, -2: 0.6, -3: 0.0}` (C1, 14.10, "−3'te kabuk teması"; kaset ve durdurucudan önce).
- Yeni: `yana_alt_bosluk_mm={5.0: 0.34, 4.3: 0.0}` (S2 → kol çatalı ile en yakın engel = durdurucu dişi; F6a ölçümü 0,3436 / 0) + yeni
  `yana_alt_temas=dict(durdurucu=4.3, s1_tambur=3.65, s1_kaset_kapagi=3.21)` (durdurucusuz ilk temaslar, F2; tambur F6a'da yeniden 3,647).
- `eklem_sinirlari()` S2 "neden" metni sayıları bu iki alandan üretir; `bosluk_mm` anahtarları `"%g"` ("5", "4.3"); yeni `temas_derece` alanı.
**Okuyanlar** (`git grep`): `OMUZ["yana_alt_bosluk_mm"]` yalnız `arayuz.eklem_sinirlari()` (→ `kod/ortak/eklem_sinirlari_uret.py` → `eklem_sinirlari.json`). `bosluk_mm` / `eklem_sinirlari.json`
`kod/` içinde başka hiçbir betikte okunmuyor; FreeCAD betikleri `OMUZ["yana_aralik"]`'ı okur (değişmedi). Tarihçe betikleri `planlama/adim2/K2-regresyon.py:95`, `K3-regresyon.py:91,95`
JSON ↔ üretici eşitliğini denetler: `kod/` yeniden üretilene kadar "eşit değil" derler (yeniden koşulmadı). Tarama, montaj ve regresyon sayılarına etkisi yok (yalnız metin + yeni alan).

### 1g. `kod/ortak/eklem_sinirlari.json` önerisi (kod/'a yazılmadı)
- `py -3 kod/ortak/eklem_sinirlari_uret.py --kontrol`: "eklem_sinirlari.json ESKI ya da yok", çıkış 1 (beklenen: `arayuz.py` değişti). Dosya yazılmadı; `git status kod` boş.
- Kopya `SP/eklem_sinirlari_uret_oneri.py` (`SP/kopya_uret.py` ile üretildi; yalnız `KOK` sabit depo kökü ve `CIKTI` = `planlama/d158/F6a-eklem_sinirlari-oneri.json`), çıkış 0
  (`kontrol_et` geçti) → **`planlama/d158/F6a-eklem_sinirlari-oneri.json`** (takma ad 0).
- Eski ↔ yeni fark (`diff kod/ortak/eklem_sinirlari.json planlama/d158/F6a-eklem_sinirlari-oneri.json`; 4 blok):

| Yer (eski satır) | Alan | Eski | Yeni |
|---|---|---|---|
| `eklemler.r_s2` (:20) ve `l_s2` (:61) | `neden` | "alt sinir +5 (S1 kablo kaseti: kol S2 3'te tambura/flansa yaklasir, 5'te 0,77 mm); kabuk boslugu 0'da 4,7 mm, -3'te temas" | "alt sinir +5; mekanik durdurucu (omuz gobegi disi) 4,3'te dayanir, 5'te dise 0,34 mm; durdurucusuz ilk temas S1 tamburu 3,65, S1 kaset kapagi (kabuk) 3,21; kol <-> kabuk 5'te 1,36 mm, 4,3'te 0,83 mm (1,58 m modeli, F2 / F6a olcumu)" |
| ″ (:21–24, :62–65) | `bosluk_mm` | {"0": 4.7, "-2": 0.6, "-3": 0.0} | {"5": 0.34, "4.3": 0.0} |
| ″ (yeni) | `temas_derece` | — | {"durdurucu": 4.3, "s1_tambur": 3.65, "s1_kaset_kapagi": 3.21} |
| `teker.not_` (:111) | metin | "… (karar 29 Ekim 2026, <takma ad>; …)" | "… (karar 29 Ekim 2026, Ahmet; …)" |
Sayısal sınırlar (`min`/`max` bütün eklemlerde, `bagimli`, `kafa_kol_yasak`, `teker.ivme_sinir_m_s2`) **değişmedi**.

### 1h. Göğüs ekranı port girintisi
Uygulanmadı: ekran henüz gelmedi / ölçülmedi. `lale158_kontrol.py` uç bölgesi hariç tutma kutusu (`kablo_yolu_ekran.uc_bolgesi`) yerinde kalıyor. **Ekran ölçülünce**
`arayuz.GOGUS_EKRAN["port"]`, kasa modeline girinti geometrisi ve `uc_bolgesi` birlikte güncellenmeli (hariç tutma kalkar).

### 1i. `TF/lale158/baski_listesi_guncelle.py` (tarama kaynağı değil)
F4c-dogrula.py `YAMA` (Y1–Y7, 11 metin değişikliği) kalıcı uygulandı (`SP/yama_baski.py`; her eski metin tam bir kez; CRLF korundu): +11 / −11 satır.
**Yan etki (F4c alanı, dokunulmadı):** `planlama/d158/F4c-liste.py` ve `F4c-dogrula.py` 5b, aynı YAMA'yı betiğin geçici kopyasına yeniden uygular; kaynak artık yamalı
olduğu için eski metinler bulunmaz ve bu iki betik "tam bir kez" denetiminde durur. Baskı listesi yeniden üretimi bu yüzden §6'daki yolla yapıldı.

## 2. Yeniden üretim, tarama, doğrulama

### 2.1 Modüller (zincir 1, koşu kimliği `20261109-084522`)
Komut (`SP/` içinde, arka planda, ön planda ≤ 3 dk'lık `until` döngüleriyle izlendi):
`py -3 -u zincir.py 20261109-084522 iskelet_montaj omuz_montaj omuz_baski kafa_montaj kabuk_montaj dirsek_montaj taban_montaj carp:statik carp:kol_sag carp:kol_sol carp:kolkol carp:kafa_sabit carp:kafa_sag carp:kafa_sol carp:taban carp:omuz birlestir kontrol > zincir.out`
Özet `SP/zincir_20261109-084522.json`, her adımın günlüğü `SP/<adim>.log` (çarpışma bölümleri `%TEMP%/carpisma-<bolum>.log`).

| Adım (betik) | Yazdığı JSON / dosya | Süre | rc | Boş bellek baş → son (GB) | Önce → sonra (`SP/jfark.py`, `SP/baski_ozet.py`) |
|---|---|---|---|---|---|
| `iskelet_montaj` (`TF/iskelet/iskelet_montaj.py`) | `iskelet-analiz.json`, `iskelet-montaj.FCStd/.step` | 14 s | 0 | 4,50 → 4,47 | 72 sayı: travers yükü F 13,0234 → 13,0477 N (+2,48 g / omuz: dosya F2'den beri eskiydi; F2 dişi +2,43 g + F6a dolgusu +0,05 g), eğilme / gerilme aynı oranda (σ_direk 0,8052 → 0,8055 MPa), emniyetler 4. hanede |
| `omuz_montaj` | `omuz-analiz.json`, `omuz-montaj.FCStd/.step`, `stl/omuz-gobegi.stl` | 45 s | 0 | 4,47 → 4,45 | 8 sayı: `kol_gobek` S2 −15 / −20 ortak hacim 1888,4 → 1890,6 / 2153,3 → 2170,5 mm³ (aralık dışı; dolgu); `tork` 6 hücrede ±0,01; `kutle.Gobek` 177,6 → 177,6 g |
| `omuz_baski` | `omuz-baski.json` | 278 s | 0 | 4,45 → 4,44 | §1c tablosu |
| `kafa_montaj` | `kafa-analiz.json`, `kafa-montaj.FCStd/.step`, `kafa-zarf.brep` | 222 s | 0 | 4,44 → 4,54 | yalnız boş `kesit_kaydirma` alanları |
| `kabuk_montaj` | `kabuk-analiz.json`, `kabuk-montaj.FCStd/.step` | 3922 s | 0 | 4,54 → 4,26 (en düşük 3,48, 09:19) | `sure_s` / `tarih` dışında 0 fark |
| `dirsek_montaj` | `dirsek-analiz.json` (+ FCStd/step) | 238 s | 0 | 4,26 → 4,29 | boş `kesit_kaydirma` + `tork.grup.omuz_Gobek.am` 4. hane |
| `taban_montaj` | `taban-analiz.json`, `taban-bom.csv` | 85 s | 0 | 4,29 → 4,28 | 88 sayı, hepsi kütle +4,9 g'den: `robot.pozlar[0].kutle_g` 26.115,6 → 26.120,5; AM y 522,7 → 522,8; `aks.mu_gereken_rampa5` 0,168 → 0,169; `motor.rampa5.F_N` 43,0 → 43,1; `motor.rampa5_yavas.oran` 0,923 → 0,924; statik eğim 4. hanede |
Not: kabuk görselleri (13 PNG) ve `TF/montaj/yerlesim-kontrol.json` F6a'dan önce de değişikti (K23, başka paket); bu paket onları yeniden üretti / dokunmadı (§2.3).

### 2.2 Tam çakışma taraması (aynı zincir; omuz en son)
Tarama başladıktan sonra hiçbir tarama kaynağına dokunulmadı (yorum dahil). Bölümler `TF/carpisma.py` (`CARPISMA_BOLUM`, `CARPISMA_KOSU=20261109-084522`), ayrı `freecadcmd` süreçleri:

| Bölüm | Süre (zincir) | rc | Boş bellek baş → son (GB) | Tepe bellek (MB, `bolumler`) | `carpisma-bolum/<b>.json` önce ↔ sonra (`pid`, süre, kaynak özetleri hariç) |
|---|---|---|---|---|---|
| statik | 74 s | 0 | 4,28 → 4,24 | 733 | 1 fark: `sonuc.kutle_toplam_g` 25.720,5 → 25.720,6 (kök dolgusu 2 × 0,05 g) |
| kol_sag / kol_sol | 229 / 230 s | 0 / 0 | 4,24 → 4,25 | 748 / 745 | 0 |
| kolkol | 56 s | 0 | 4,25 → 4,25 | 198 | 0 |
| kafa_sabit / kafa_sag / kafa_sol | 159 / 481 / 471 s | 0 | 4,25 → 4,06 | 738 / 620 / 626 | 0 |
| taban | 86 s | 0 | 4,06 → 4,15 | 739 | 0 |
| omuz | 12.293 s (10:35:15–14:00:09) | 0 | 4,15 → 3,15 (en düşük 2,63, 13:30; freecadcmd 442 MB, düşüş başka süreçlerden) | 747 | 0 (S2 −10…−20 aralık dışı çakışmalar dahil aynı) |
| `py -3 TF/carpisma_kos.py birlestir` | 14:00:09 | 0 | | | "tek kosu: True, eksik: [], TOPLAM cakisma 364 eklem araliginda 0" |
| `py -3 TF/carpisma_kos.py kontrol` | 14:00:09 | **0** | | | "izlenen 17 dosyanin ozetleri kayitla ayni" (**eskimiş 0**) |
Bellek kaydı `SP/bellek.log` (5 dk'da bir; tarama boyunca 2,63–4,28 GB, hep ≥ 2 GB). Süreç ölmedi, yeniden başlatma olmadı.

**`TF/carpisma-sonuc.json` (sonra) ↔ `SP/once/json/carpisma-sonuc.json` (F2, koşu 20261109-033441)** (`SP/sonuc_ozet.py`, `SP/jfark.py`):

| Alan | Önce | Sonra |
|---|---|---|
| `tek_kosu` | true | **true** (koşu 20261109-084522, 10:06:29–14:00:08) |
| `ev_pozu_cakisma` | [] | **[]** (0) |
| `toplam.eklem_araliginda` (kol / kafa / taban) | 0 (0 / 0 / 0) | **0** (0 / 0 / 0) |
| `toplam.cakisma` (aralık dışı dahil) | 364 | 364 |
| `ev_pozu_cakisma_s2_0` (S2 0, ev pozu dışı) | 4 çift (üst kol tüpü × S1 kaset kapağı 6,42 mm³ ×2; M5 cıvata × dirsek çatalı 20,53 mm³ ×2) | aynı |
| `tarama.omuz_*` çakışan poz / eklem aralığında | 116 / 0 | 116 / 0 |
| `kutle_toplam_g` | 25.720,5 | 25.720,6 |
| `agirlik_merkezi` | [−0,03; 528,59; −9,25] | aynı |
| `arayuz_uyumu` | ayni ×2 | ayni ×2 |
| `sure_s` | 14.093,8 | 14.073,7 |
Süre / koşu / kaynak özeti alanları dışında **tek fark** `kutle_toplam_g` +0,1 g. Kök dolgusu kol çatalının hiçbir tarama pozunda yeni temas üretmedi
(§1d: S2 ≥ 0'da ≥ 3 mm). `kaynak` md5'i değişen dosyalar: `arayuz.py`, `dirsek_lib.py`, `kabuk_lib.py`, `kabuk_parcalar.py`, `kafa-analiz.json`,
`kafa10_lib.py`, `kafa_lib.py`, `kafa_parcalar.py`, `omuz_parcalar.py`, `taban_parcalar.py` (= §1 düzenlemeleri + yeniden üretilen kafa analizi).

### 2.3 Tarama sonrası zincir (zincir 2, `SP/zincir2.py`, kimlik `20261109-084522-b`)
Komut: `py -3 -u zincir2.py 20261109-084522-b ana_montaj taban_montaj uygulama_ivme lale158_kontrol uygulama_olc uygulama_tani eklem_dogrulama omuz_regresyon iskelet_regresyon gui:montaj_gorsel gui:iskelet_gorsel gui:omuz_gorsel gui:kabuk_gorsel gui:dirsek_gorsel gui:kafa_gorsel gui:taban_gorsel > zincir2.out`
(zincir 1 ile aynı denetimler; `gui:` adımları `freecad.exe` + başlatıcı, 60 dk zaman aşımında öldürülür ve zincir durur; regresyonlar `REG_ETIKET=sonra`.
Regresyonlar görsellerden önce: `omuz_regresyon` `omuz_montaj.py`'yi yeniden koşup omuz çıktılarını yeniden yazar.) Özet `SP/zincir_20261109-084522-b.json`.

| Adım | Yazdığı JSON | Süre | rc | Boş bellek (GB) | Önce (`SP/once/json`) → sonra |
|---|---|---|---|---|---|
| `ana_montaj` (`TF/montaj/ana_montaj.py`) | `montaj-analiz.json`, `robot-bom.csv`, `robot-montaj.FCStd` | 98 s | 0 | 3,15 → 3,11 | 23 sayı: `kutle_g` 25.720,49 → **25.720,55**; AM y 528,593 → 528,595; omuz modülü 570,01 → 570,04 g; omuz göbeği parçası 61,691 → **61,722 g** (+0,031 g / taraf). Çarpışma ile karşılaştırma: `karsilastirma.kutle.fark_carpisma` 4,887 → −0,05 g, `am.fark_carpisma_mm` 0,133 → 0,007 (montaj analizi F2'den beri eskiydi, şimdi tutarlı) |
| `taban_montaj` (ikinci kez, ana montajdan sonra) | `taban-analiz.json` | 84 s | 0 | 3,11 → 3,09 | §2.1 ile aynı |
| `uygulama_ivme` (`KY/uygulama_ivme.py`) | `KY/uygulama-ivme.json` | 61 s | 0 | 3,09 → 3,07 | 22 sayı, hepsi kütle 26.120,5 → 26.120,6 ve 4. hane; **rampa payı (yüksüz) 1,519 → 1,519** |
| `lale158_kontrol` | `TF/lale158/lale158-kontrol.json` | 10 s | 0 | 3,07 → 3,11 | 1 sayı: `baski[58]` omuz göbeği ölçüsü 66 → 77 mm (F2 dişi; dosya F2'den beri eskiydi). Toplam boy 1580 |
| `uygulama_olc` | `KY/uygulama-olcum.json` | 433 s | 0 | 3,11 → 3,64 (14:10'da **2,04**; freecadcmd 1628 MB) | **0 fark** |
| `uygulama_tani` (1c) | `KY/uygulama-tani.json` | 46 s | 0 | 3,64 → 3,63 | yalnız yeni `kaydirma` alanı: 13 katmanda 0,0 (z 0,5 boş katmanda null); **kaydırılan katman 0**; alanlar, `dest_alan`, `ofsetsiz_tasma_mm2` aynı |
| `eklem_dogrulama` | `TF/montaj/eklem-dogrulama.json` | 158 s | 0 | 3,63 → 3,60 | **0 fark** (66 vaka; en büyük sapma 2,3e-10 mm) |
| `omuz_regresyon` | `TF/omuz/regresyon/sonra.json`, `fark.json` (+ omuz çıktıları yeniden) | 45 s | 0 | 3,60 → 3,59 | §2.4 |
| `iskelet_regresyon` | `TF/iskelet/regresyon/sonra.json`, `fark.json` | 2 s | 0 | 3,59 → 3,58 | §2.4 |
| `gui:montaj_gorsel` (`TF/montaj/montaj_gorsel.py`) | `TF/montaj/gorsel/*.png`, `robot-montaj.FCStd` GUI kaydı | 635 s | **1** | 3,58 → 3,44 | **koşmadı**: betik üst düzeyde "'NoneType' object is not subscriptable" ile durdu (`SP/gui_montaj_gorsel.log`; iç günlük boş → hata `animasyon_kontrol()` içinde, dosya açılmadan önce). Neden: `TF/montaj/montaj_gorsel.py:101` `Y["kol_kosulu"][k]` (ve :98 `kutu_*_kol`) → `arayuz.KAFA_KOL_YASAK` 1,65 m'den beri `aktif=False`, `kol_kosulu=None`, `kutu_sag_kol=None` (`b1f9547`, 29.10). F6a'dan bağımsız, önceden var (montaj görselleri en son 11–14.10). GUI penceresi açık kaldı; zaman aşımını beklemek yerine süreç 14:27'de `taskkill` ile kapatıldı (çökme / bellek değil, betik hatası); zincir kuralı gereği DUR. Kaynak değiştirilmedi → açık A3 |
| `gui:iskelet_gorsel` … `gui:taban_gorsel` (zincir 3, kimlik `-c`, `SP/zincir3.out`) | `TF/<modül>/gorsel/*.png` | 13 / 15 / 22 / 16 / 24 / 33 s | 0 ×6 | 3,48 → 3,41 | yeniden üretildi: iskelet 11, omuz 4 (+ `gorsel/kare/` 106 kare), kabuk 13, dirsek 14, kafa 17, taban 18 PNG (`git status`: 77 PNG değişik; kabuk 13'ü F6a'dan önce de değişikti, K23) |
Görsel yolları: `TF/iskelet/gorsel/`, `TF/omuz/gorsel/`, `TF/kabuk/gorsel/`, `TF/dirsek/gorsel/`,
`TF/kafa/gorsel/`, `TF/taban/gorsel/` (`robot-tam-*.png` tam robot), ayrıca `planlama/d158/F6a-dis-kok.png` (§1d). Montaj görselleri (`TF/montaj/gorsel/`) eski (11–14.10).

### 2.4 Omuz ve iskelet regresyonu (referanslar değiştirilmedi)
Referanslar: `TF/omuz/regresyon/once.json` (14.10.2026, `a158211`), `TF/iskelet/regresyon/once.json` (08.10.2026). Karşılaştırma `SP/reg_fark.py`.
Betiklerin kendi `fark.json` tabloları F2'nin (07:31) tablolarıyla **bayt bayt aynı** (yalnız "en büyük fark" özetleri; F6a'nın küçük farkları bunları değiştirmiyor).

**Omuz** (`fark.json` `hepsi_ayni: false`; sonra.json 75 parça):

| Ölçüt (`fark.json`) | 14.10 referansı | Şimdi | Neden |
|---|---|---|---|
| parça sayısı / adlar | 70 | 75 | S1 kablo kaseti (`834b386`, `6594c63`): + S1 kablo tamburu, tambur cıvatası M3x8, ısıl gömme M3 (göbekte), S1 tambur bağlama ipi; servo DS3218MG → DS3235 (S1, S2; `6594c63` / `b1f9547`); − "Yuva bağlantı pulu M6" (M6 pulsuz, 14.10 kararı `a158211`) |
| statik çakışma (S2 5) | 0 | 0 | aynı |
| boşluk Kol-Gövde | 4,0 mm | 6,293 mm | kol / yuva bağlantısı değişiklikleri (`a158211` M1 kol kablo yolu, M6 cıvata) |
| boşluk Kol-Göbek, Göbek-Gövde | 0 / 0 | 0 / 0 | aynı (horn ↔ mil teması, tasarım gereği) |
| tarama kol_göbek: çakışan poz | 8 | 11 | yeni çakışan S2 −10, −5, 0: S1 kablo tamburu (kaset) + **F2 durdurucu dişi** (S2 < 4,3'te dişe dayanır); hepsi alt sınır +5'in **dışında**. F6a: yalnız S2 −15 / −20 hacimleri 1888,4 → 1890,6 / 2153,3 → 2170,5 mm³ (kök dolgusu) |
| tarama göbek_gövde | 0 | 0 | aynı |
| tarama kol_gövde: çakışan poz | 94 | 94 (53 pozda hacim / çift farklı, hepsinde S2 −5…−20, aralık dışı) | üst kol tüpü / kaset değişiklikleri |
| tork tablosu (875 poz, en büyük fark) | 5,722 kg·cm (en büyük) | 6,116 | baskı yoğunluğu ρ × doluluk (PETG-CF 0,9, PETG 0,8; `834b386`), DS3235, tambur, F2 dişi; **F6a payı ≤ 7,7e-5 kg·cm** |
| BOM | 17 kalem | 17 (DS3235 ×2, M3 ısıl gömme 6 → 9, M3x8 6 → 9, bağlama ipi; − DS3218MG, M6 pul) | yukarıdaki gibi |
| parça kütlesi toplam | 852,6 g | 962,2 g | ρ × doluluk (`834b386`), DS3235, tambur, F2 dişi (+2,43 g), F6a dolgusu (+0,031 g) |
| omuz göbeği (parça) | 52.066 mm³ / 39,67 g | 54.000,3 mm³ / 61,72 g; kutu +11 mm | ρ (`834b386`); F2 dişi (`ff1c2e9`); F6a kök dolgusu +27,7 mm³ (F2 sonrası 53.972,55 → 54.000,26) |
F2 sonrası (07:31) → F6a farkı yalnız: omuz göbeği hacmi +27,71 mm³, kütle 61,691 → 61,722 g, merkez ≤ 0,016 mm; `kol_gobek` S2 −15 / −20; torkta ≤ 7,7e-5.
Geri kalan her şey (BOM, boşluklar, statik, kol_gövde, göbek_gövde) F2 ile aynı.

**İskelet** (`fark.json` `hepsi_ayni: false`): F2 sonrası `sonra.json` ile **birebir aynı** (md5 `9b45698e…`; `git status` değişiklik göstermiyor). 08.10 referansına göre
farkların hepsi 1,58 m uzamasından (`UZAMA` 315, `bcaa6df`; 1,65 m ara adımı `b1f9547`): direk hacmi 581.402 → 810.186 mm³ (1569,8 → 2187,5 g), travers ve 14 bağlantı
elemanı +315 mm yukarıda (kutu / merkez 315 mm), toplam AM y 314,49 → 418,61, toplam kütle 5793,1 → 6410,8 g. Parça sayısı, adlar, katı / geçerlilik, iç çakışma (0),
bağlantılar (12), ayrılmış bölge ihlali (0) aynı.

**Öneri (yeni referans):** `planlama/d158/F6a-regresyon-oneri/omuz-once.json` (= şimdiki `TF/omuz/regresyon/sonra.json`, md5 `26c1e48c…`) ve
`planlama/d158/F6a-regresyon-oneri/iskelet-once.json` (= `TF/iskelet/regresyon/sonra.json`, md5 `9b45698e…`). Kabul edilirse ikisi `TF/<modül>/regresyon/once.json`
yerine kopyalanır; bundan sonra iki betik "AYNI" der ve her yeni fark bu pakete göre ölçülür. Referanslar bu pakette **değiştirilmedi** (karar taslağı §4).

### 2.5 `planlama/d158/regresyon.py`
- 14:20:16 `py -3 planlama/d158/regresyon.py --yazma` (deneme): çıkış 0, GEÇER.
- 14:30:50 `py -3 planlama/d158/regresyon.py` (normal; öncesinde `regresyon.json` ve `regresyon-son-kosu.json` `SP/once/`'a kopyalandı): **çıkış 0**, "Sonuç: GEÇER (hepsi okundu,
  kötüleşen yok)"; çıktı `SP/regresyon_normal.out`. 10 değer tabana göre **aynı**: boy 1580, kafa içi / kabuk içi / kabuk × iskelet / ev pozu çakışma 0, rampa (yüksüz) 1,519
  (eşik 1,5), tilt payı 3,64, pan payı 2,21, mik ↔ hoparlör 574,3 mm, SY8205 × USB 0. Betik tabanı yazdı: `regresyon.json` (+29/−14: tarih, kaynak sha256'ları, çarpışma
  koşu kimliği, önceki taban geçmişe), `regresyon-son-kosu.json` (+14/−14).

## 3. Baskı listesi (1i, en son, yalnız betikle; F4c commit'li `f7ed8c4`, `e796f15`)
1. `PYTHONIOENCODING=utf-8 py -3 planlama/y2/Y2b-baski.py` (14:31): çıkış 0 → `planlama/y2/Y2b-baski.json` 5 değer (+5/−5): `satirlar[58]` omuz göbeği `g` 63,2 → **63,3**
   (alt uç), `toplam.cf_g` 1158,0 → 1158,2, `toplam.g` 7604,6 → 7604,8, `parti[2].g` 1330,6 → 1330,8, `omuz_baski_tarih` → 08:50:59. (Kök dolgusu, 2 × ~0,1 g.)
2. `PYTHONIOENCODING=utf-8 py -3 TF/lale158/baski_listesi_guncelle.py` (yamalı): çıkış 0, "guncellendi 48 yeni [] destekli [Gogus bandi sag, Gogus bandi sol,
   Ust arka servis kapagi, Gogus ekrani VESA tasiyici]". **`planlama/baski-listesi.md` değişmedi** (`git diff` boş; yamalı betik sabit noktada, F4c-dogrula 5b ile tutarlı).
   Betik yalnız kabuk / kafa satırlarını yazar; omuz göbeği satırı (`baski-listesi.md:239` "63–70 g", yuvarlamada aynı) ve toplam (7,60–7,66 kg) zaten tutarlı.
   Bayat kalan metinler (betik kapsamı dışı, elle / `F4c-liste.py` ile güncellenmeli → açık A5): `:36` fark tablosu "63,2–70,4 g" (artık 63,3–70,4),
   `:134` ve `:239` "K39 kök yarıçapı (P6.1)" bekliyor diyor (F6a'da uygulandı).

## 4. Karar taslakları (karar-kuyrugu.md'ye yazılmadı)
**karar taslağı KT-F6a-1: `kod/ortak/eklem_sinirlari.json` yenilenmesi.** Ahmet onayıyla `py -3 kod/ortak/eklem_sinirlari_uret.py` koşulup `kod/`'a yazılır
(içerik = `planlama/d158/F6a-eklem_sinirlari-oneri.json`; sayısal sınır değişmez, S2 `neden` / `bosluk_mm` / yeni `temas_derece` ve teker notunda "Ahmet") + Efe'ye pano bilgisi
(S2 alt sınırı +5 aynı; gerekçe artık mekanik durdurucu 4,3° ve 5°'te 0,34 mm; `bosluk_mm` anahtarları "5" / "4.3"). Ardından `planlama/adim2/K2-regresyon.py`, `K3-regresyon.py` eşit der.

**karar taslağı KT-F6a-2: S2 darbe hız sınırı (K38 ile).** Kök yuvarlatmasıyla K_t'li emniyet: stall 2,57, 1,5 rad/s yüksüz 1,54, elde 500 g 0,91, kaçak / düşme < 1.
Emniyet 2 için S2 aşağı yönde durdurucuya yaklaşırken ≤ **59°/s** yüksüz, ≤ **30°/s** 500 g ile — **F2 rijitlik varsayımında** (k_lin = k_diş/2, kol esnek) K38'deki
B önerisiyle (60 / 30) örtüşüyor. Rijitlik aralığı: rijit alt sınırda emniyet 2 için 27 / 14°/s gerekir, 59 / 30°/s'de emniyet 1,14 / 1,15; esnek uçta 2,13 / 2,14;
yük temas ucunda ≈ 40 / 20°/s (B). Güç kesilince (servo torku yok) düşme emniyet 2'de S2 ≤ **15,5°**, emniyet 1,5'te ≤ **20,4°** (F2 rijitliği; rijitte 8,1° / 10,2°).
Karar için öneri: K38 sınırı 60 / 30°/s rijitlik ölçülene kadar "emniyet 1,15–2" diye yazılsın ya da tutucu 27 / 14°/s alınsın; yazılımda S2 < ~20°'de hız sınırı +
yükle yavaşlatma; kaçak servo / güç kesik düşme için mekanik çözüm (yumuşak durdurucu / sönüm) ayrı değerlendirilmeli. (Düzeltme turu 1, F6a-kontrol O-2.)

**karar taslağı KT-F6a-3: omuz ve iskelet regresyon referansının yenilenmesi.** `planlama/d158/F6a-regresyon-oneri/omuz-once.json` ve `iskelet-once.json` →
`TF/omuz/regresyon/once.json`, `TF/iskelet/regresyon/once.json` (14.10 ve 08.10 referanslarının yerine; §2.4'teki her fark bir değişikliğe bağlı). Ahmet / döngü yöneticisi onayıyla.

**karar taslağı KT-F6a-4: F4c betiklerinin YAMA takibi.** `baski_listesi_guncelle.py` artık yamalı; `planlama/d158/F4c-dogrula.py:28` `YAMA` ve `F4c-liste.py` (`DG` üzerinden) aynı
yamayı yeniden uygulamaya çalışır, `F4c-dogrula.py:70-71` "1 olmalı" denetiminde durur. Öneri: iki betikte YAMA boş listeye indirilsin (ya da "yama zaten uygulanmış" durumu
kabul edilsin) ve `baski-listesi.md:36,134,239` bayat metinleri `F4c-liste.py` ile yenilensin. Sahibi F4c / `planlama/d158`; bu pakette dokunulmadı.

**karar taslağı KT-F6a-5: `montaj_gorsel.py` yasak kutu denetimi.** `TF/montaj/montaj_gorsel.py:96-103` `KAFA_KOL_YASAK["aktif"]` false iken kutu denetimini atlamalı
(1,65 m'den beri betik koşmuyor; montaj görselleri 11–14.10'dan kalma). Tarama kaynağı değil; onayla tek koşul eklenip `gui:montaj_gorsel` yeniden koşulur.

## 5. Açıklar
- **A1** `kod/ortak/eklem_sinirlari.json` eski (`--kontrol` çıkış 1) — KT-F6a-1 onayı bekliyor; o zamana kadar `kod/` dosyası `bosluk_mm` {"0": 4.7, …} ve takma adlı teker notunu taşır.
- **A2** Göğüs ekranı port girintisi: **ekran ölçülünce** (`GOGUS_EKRAN["port"]`, kasa girintisi, `lale158_kontrol` `uc_bolgesi` hariç tutma kutusu birlikte).
- **A3** `montaj_gorsel.py` 1,65 m'den beri koşmuyor (KT-F6a-5); montaj görselleri ve GUI'den kaydedilmiş `robot-montaj.FCStd` (eklem görünümü, "Kollari_oynat") bu modelde yenilenmedi.
  `ana_montaj.py` FCStd'yi betikle kaydetti (gizli gelen montaj, eklem görünümü yok).
- **A4** Darbe: elde yükle 1,5 rad/s, kaçak servo ve güç kesik düşme senaryolarında K_t'li emniyet < 1 (KT-F6a-2). FE 2B düzlem gerilme; 3B etki ve baskı katman yönü
  (diş kökü katman sınırına denk gelirse Z dayanımı) ölçülmedi; F2'nin rijitlik varsayımı aynen alındı.
- **A5** `baski-listesi.md:36,134,239` bayat metinler; `F4c-liste.py` / `F4c-dogrula.py` YAMA ile kırık (KT-F6a-4).
- **A6** Basılı parçada kök yayı: r 1,5 yay XY düzleminde (göbek +X yönünde basılıyor, `omuz-baski.json`); dilimleyicide yayın çözünürlüğü ve diş tabanı desteği (+Y yönünde
  bölge 7 → 8) baskıdan önce önizlemede kontrol edilmeli.
- **A7** `TF/montaj/yerlesim-kontrol.json` ve 13 kabuk görseli F6a'dan önce değişikti (K23); bu paket yerleşim dosyasına dokunmadı (`SP/once` ile bayt bayt aynı), kabuk görsellerini yeniden üretti.
- **A8** `eklem-dogrulama.json` ana montajda S2 sınırını [0, 120] kullanıyor (yazılım alt sınırı +5 değil); F6a'dan önce de böyle, değişmedi — bilgi.

## 6. Kabul ölçütleri

| Ölçüt | Durum | Kaynak |
|---|---|---|
| `git grep -il <takma ad>` tarama kaynaklarında boş | **Geçti** (yalnız kapsam dışı `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html`) | §1a |
| `carpisma-sonuc.json` `tek_kosu: true` | **Geçti** (koşu 20261109-084522) | `TF/carpisma-sonuc.json` `tek_kosu`, `birlestirme_notu` |
| eskimiş 0 | **Geçti** (`carpisma_kos.py kontrol` çıkış 0, "17 dosya kayitla ayni") | `SP/zincir.out` |
| ev pozu 0 | **Geçti** | `carpisma-sonuc.json` `ev_pozu_cakisma` [] |
| eklem aralığında 0 | **Geçti** (kol 0, kafa 0, taban 0) | `carpisma-sonuc.json` `toplam.eklem_araliginda` |
| diş kökü yuvarlatılmış, temas açısı korunmuş (ölçülü) | **Geçti**: r 1,5 yay (z 6,5 kesitinde Circle r 1,5); ilk temas 4,3002°, 5°'te 0,3436 mm (F2 ile aynı) | `SP/olc_dis.json` `k_kok_dolgu.kesit_z6_5_profil`, `c_kol_x_durdurucu` |
| darbe emniyeti K_t ile yeniden | **Yapıldı**: K_t,etkin 1,45 (keskin 2,73–3,64); stall 2,57, 1,5 rad/s 1,54 | `SP/kt_fem.json`, `SP/darbe_f6a.json` |
| `regresyon.py` 0 | **Geçti** (normal mod çıkış 0) | `planlama/d158/regresyon-son-kosu.json` |
| kesit kaydırması dört yerde | **Geçti** (kafa_lib, dirsek_lib, omuz_baski, uygulama_tani; kaydırılan katman 0 / 0 / 0 / 0) | §1c; `kafa-analiz.json`, `dirsek-analiz.json`, `omuz-baski.json`, `uygulama-tani.json` |
| eklem_sinirlari önerisi + fark tablosu | **Geçti** | `planlama/d158/F6a-eklem_sinirlari-oneri.json`, §1g |
| omuz / iskelet regresyon farkları tablolu, öneri ayrı klasörde | **Geçti** (referanslar değişmedi) | §2.4, `planlama/d158/F6a-regresyon-oneri/` |
| `eklem_dogrulama`, modül görselleri | **Geçti** (0 fark; 6 modül görseli) | `TF/montaj/eklem-dogrulama.json` |
| `montaj_gorsel` | **Kaldı** (önceden var olan betik hatası, A3 / KT-F6a-5; düzeltme turu 1'de yasak kutu koruması eklendi, betik bu kez animasyon sınır denetiminde durdu, §9) | `SP/gui_montaj_gorsel.log` |

## 7. Dokunulan dosyalar (commit için)
Kaynak (elle): `tasarim/freecad/arayuz.py` (+34/−21), `tasarim/freecad/kabuk/kabuk_lib.py` (+1/−1), `tasarim/freecad/kabuk/kabuk_parcalar.py` (+4/−4),
`tasarim/freecad/kafa/kafa10_lib.py` (+4/−4), `tasarim/freecad/kafa/kafa_lib.py` (+32/−10), `tasarim/freecad/kafa/kafa_parcalar.py` (+1/−1),
`tasarim/freecad/taban/taban_parcalar.py` (+2/−2), `tasarim/freecad/dirsek/dirsek_lib.py` (+24/−6), `tasarim/freecad/omuz/omuz_baski.py` (+40/−13),
`tasarim/freecad/omuz/omuz_parcalar.py` (+42/−3), `tasarim/freecad/lale158/kafa-yerlesim/uygulama_tani.py` (+21/−2), `tasarim/freecad/lale158/baski_listesi_guncelle.py` (+11/−11).
Yeni (elle): `planlama/d158/F6a-gunluk.md`, `planlama/d158/F6a-eklem_sinirlari-oneri.json`, `planlama/d158/F6a-dis-kok.png`, `planlama/d158/F6a-regresyon-oneri/omuz-once.json`,
`planlama/d158/F6a-regresyon-oneri/iskelet-once.json`.
Betikle yeniden üretilen: `tasarim/freecad/carpisma-sonuc.json`, `tasarim/freecad/carpisma-bolum/*.json` (9), `tasarim/freecad/iskelet/iskelet-analiz.json`, `iskelet-montaj.FCStd/.step`,
`tasarim/freecad/omuz/omuz-analiz.json`, `omuz-baski.json`, `omuz-montaj.FCStd/.step`, `omuz/stl/omuz-gobegi.stl`, `omuz/regresyon/sonra.json`,
`tasarim/freecad/kafa/kafa-analiz.json`, `kafa-montaj.FCStd/.step` (`kafa-zarf.brep` bayt aynı), `tasarim/freecad/kabuk/kabuk-analiz.json`, `kabuk-montaj.FCStd/.step`,
`tasarim/freecad/dirsek/dirsek-analiz.json`, `dirsek-montaj.FCStd/.step`, `tasarim/freecad/taban/taban-analiz.json`, `taban-montaj.FCStd/.step`,
`tasarim/freecad/montaj/montaj-analiz.json`, `robot-montaj.FCStd/.step`, `tasarim/freecad/lale158/lale158-kontrol.json`,
`tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json`, `uygulama-olcum.json` (yalnız `sure_s`), `uygulama-tani.json`, 77 PNG (`iskelet/`, `omuz/`, `kabuk/`, `dirsek/`, `kafa/`, `taban/` `gorsel/`),
`planlama/d158/regresyon.json`, `planlama/d158/regresyon-son-kosu.json`, `planlama/y2/Y2b-baski.json`.
Bu paketten olmayan, önceden değişik: `planlama/dongu-158.md`, `tasarim/freecad/montaj/yerlesim-kontrol.json` (K23); izlenmeyenler (`kvkk/`, `rapor/`, `raporlar/…`, `tubitak-2209b/`,
`tasarim/solidworks/`, `KY/kaynak/`, `TF/montaj/lale_dongu*`, F5/F5b pano metinleri) commit'e girmemeli. Dokunulmadı: `kod/`, `tubitak-2209b/`, `kvkk/`, `rapor/`, `KY/kaynak/`, `karar-kuyrugu.md`. `planlama/baski-listesi.md` ilk turda değişmedi, düzeltme turu 1'de betikle değişti (§9).

## 8. Komutlar ve yardımcı betikler (hepsi `SP/`, depo dışı)
- `probe1.py` (freecadcmd, 3 s) → `probe1.json`: göbek / diş geometri yoklaması. `olc_dis.py` (freecadcmd, 51 s, rc 0) → `olc_dis.json`, `olc_dis.log`.
- `kt_fem.py` (FreeCAD `bin/python.exe` + `gmsh.exe`) → `kt_fem.json`, ağlar `kt_*.geo/.msh`; kiriş teorisiyle karşılaştırma (y −26…−28, FE / kiriş 1,1–1,15) oturumda elle yapıldı, JSON'da yok.
- `darbe_f6a.py` (sistem Python) → `darbe_f6a.json`. `ciz_kok.py` (matplotlib) → `planlama/d158/F6a-dis-kok.png`.
- `kopya_uret.py` → `eklem_sinirlari_uret_oneri.py` → `planlama/d158/F6a-eklem_sinirlari-oneri.json`. `yama_kesit.py` (1c), `yama_baski.py` (1i).
- Karşılaştırma: `jfark.py`, `baski_ozet.py`, `sonuc_ozet.py`, `reg_fark.py`. Zincirler: `zincir.py` (`zincir.out`), `zincir2.py` (`zincir2.out`, `zincir3.out`); bellek `bellek.log`.
- Son denetim (14:35, bütün koşulardan sonra): `py -3 TF/carpisma_kos.py kontrol` çıkış 0 ("17 dosya kayitla ayni"); çalışan FreeCAD süreci 0.
- Kişi adı: bu günlükte ve dokunulan dosyalarda takma ad yok (`git grep -il`: yalnız kapsam dışı `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html`); başka öğrenci / danışman soyadı geçmedi.

## 9. Düzeltme turu 1 (F6a-kontrol O-1, O-2, D-4; 09.11 14:40–15:00)
Önceki dosyalar `SP/once/f4c/` (F4c betikleri, `F4c-partiler.json/.md`, `baski-listesi.md`), `SP/once/src/montaj_gorsel.py`, `SP/darbe_f6a_tur0.json`.

**1. F4c zinciri (O-1) — yapıldı.** Yama betiği `SP/yama_f4c.py` (her eski metin tam bir kez; satır sonları LF korundu):
- `planlama/d158/F4c-dogrula.py` (+7/−4): eski liste `YAMA_F4C` adıyla kayıtta, `YAMA = []` (gerekçe yorumu: F6a 1i'de Y1–Y7 kaynakta kalıcı; Y1'in eski metni yeninin
  öneki olduğundan "uygulanmışsa atla" yetmez); docstring 5. madde buna göre.
- `planlama/d158/F4c-partiler.py` (+4/−4): K39 şablonları (göbek bağımlılık satırı, Parti 2 bağımlılığı, "Omuz dişi kökü" notu, okuma paragrafı) → "kök yarıçapı r 1,5
  F6a'da uygulandı; DS3235 düşme ölçümü (K39) açık".
- `planlama/d158/F4c-liste.py` (+3/−3): fark tablosu omuz göbeği satırı 63,2 → **63,3–70,4 g**, +5,2 → +5,4–5,8 g, "kök yayı F6a"; "Fark toplamı" −22,6 → **−22,4** g
  (Y2b `toplam.g[0]` 7604,8); Parti 2 notu K39 → "F6a'da uygulandı".
- Koşular (`PYTHONIOENCODING=utf-8`): `py -3 planlama/d158/F4c-partiler.py` → çıkış 0 (liste toplamı 72 adet, 7604,8–7662,4 g, CF 1158,2–1215,8 g; `SP/f4c_partiler.out`);
  `py -3 planlama/d158/F4c-liste.py` → çıkış 0, "yazildi 275 satir" (`SP/f4c_liste.out`); `py -3 planlama/d158/F4c-dogrula.py` → **çıkış 0**, 1, 2, 3, 4a, 4b, 5a, 5b hepsi
  GEÇTİ, "SONUC: GECTI" (4b: 72 adet, 7604,8–7662,4 g; `SP/f4c_dogrula.out`).
- Betikle değişen: `planlama/baski-listesi.md` (+6/−6: :36 omuz göbeği 63,3–70,4 g, :38 fark toplamı −22,4, :134 K39 notu, :221 Parti 2 bağımlılığı, :239 göbek satırı
  notu, bir de D2 kupon payı 69–208 → 69–207 g hesaplanan), `planlama/d158/F4c-partiler.json` (+10/−10: liste / parti 2 toplamları, göbek 63,2 → 63,3),
  `planlama/d158/F4c-partiler.md` (+4/−4: :49, :87, :105, :155). Elle düzenleme yok.
- Denetim: `grep "63,2\|K39 kök yarıçapı (P6.1)\|K39'a bağlı\|K39 / P6.1\|≥ 1,5 mm yarıçap"` iki md dosyasında **0 satır**.

**2. Darbe metni (O-2) — yapıldı.** `SP/darbe_f6a.py` sonuna servo torksuz düşme ve 59 / 30°/s'de emniyet hesabı eklendi (önceki alanlar değişmedi, `tablo` ve `izinli`
`SP/darbe_f6a_tur0.json` ile aynı) → `SP/darbe_f6a.json` `f6a.duzeltme1`:

| Rijitlik | Düşme sınırı, emniyet 2 / 1,5 (servosuz) | Emniyet 2 için hız (yüksüz / 500 g) | 59 / 30°/s'de emniyet |
|---|---|---|---|
| F2 varsayımı (k_diş/2, kol esnek) | **15,5° / 20,4°** (ilk sürüm 10,6 / 15,3, yanlış formül) | 59 / 30°/s | 2,00 / 2,01 |
| Rijit (k_diş, kol rijit) | 8,1° / 10,2° | **27 / 14°/s** | **1,14 / 1,15** |
| Esnek (k_diş/3, kol esnek) | 17,0° / 22,4° | 65 / 33°/s | 2,13 / 2,14 |
B'nin `darbe_b.json` sayılarıyla birebir aynı. §1d metni ve KT-F6a-2 güncellendi ("F2 rijitlik varsayımında K38 ile örtüşüyor"; rijit alt sınır ve düşme sınırları eklendi).

**3. `montaj_gorsel` (D-4) — koruma eklendi, görsel üretilemedi.** Dosya `tasarim/freecad/montaj/montaj_gorsel.py` (mesajdaki `lale158/` yolu yok; doğru yol bu).
Tarama kaynağı **değil**: `carpisma_kos.kaynak_listesi()` 17 dosya, içinde `montaj` / `gorsel` yok. Değişiklik `SP/yama_gorsel.py` ile (CRLF korundu), +2/−1:
`:98` döngüsü `... if Y.get("aktif") else ()` (+ bir satır yorum). Koşu: boş bellek 2,81 GB, çalışan FreeCAD 0; `py -3 -u zincir2.py 20261109-084522-d gui:montaj_gorsel`
(`SP/zincir4.out`, `SP/gui_montaj_gorsel.log`; tur 0 günlüğü `SP/gui_montaj_gorsel_tur0.log`) 14:57:30–14:57:33, **rc 1**: koruma çalıştı, yasak kutu hatası yok; ama betik
kendi animasyon denetiminde (`:107-110`, tasarım gereği `SystemExit`) **48 ihlalle** durdu (iç günlük `%TEMP%/robot-montaj-kare/montaj_gorsel.log`):
- `Kafa_Tilt` formülü `0.25*sin(...)` (`:47`) ±14,32°'ye çıkıyor; tilt sınırı Y2a'dan (29.10) beri ±13 (`arayuz.KAFA["tilt_aralik"]`).
- `OmuzSag/Sol_Yana` t = 0'da 5,00 "sınır dışı (5,0, 120,0)": formül (`:40-41`) `%.6f` ile 0,087266 rad yazıyor → 4,99997°, 1e-9 toleransını aşıyor.
Süreç çökmedi, betik kendini durdurdu; yeniden koşulmadı. Dosya açılmadan durduğu için `robot-montaj.FCStd` ve `TF/montaj/gorsel/` bu koşuda yazılmadı (yeni görsel yok).
Önceden var olan iki sorun daha; düzeltmesi bu turun yetkisi dışında (KT-F6a-5'e ek): tilt genliği ≤ 0,226 rad (örn. 0,22 → ±12,6°) ve Yana formülünde `%.9f` ya da
denetimde 1e-6 tolerans. İkisi de tarama kaynağı değil.

**Son denetimler:** `py -3 tasarim/freecad/carpisma_kos.py kontrol` → **çıkış 0** ("17 dosya kayitla ayni"); `py -3 planlama/d158/regresyon.py --yazma` → **çıkış 0**
(GEÇER, 10 değer aynı; dosya yazılmadı). Çalışan FreeCAD süreci 0. Takma ad bu turda yazılmadı.

**Commit listesine ek (§7'ye):** `planlama/d158/F4c-dogrula.py`, `planlama/d158/F4c-partiler.py`, `planlama/d158/F4c-liste.py`, `planlama/d158/F4c-partiler.json`,
`planlama/d158/F4c-partiler.md`, `planlama/baski-listesi.md` (artık betikle değişti), `tasarim/freecad/montaj/montaj_gorsel.py`. `planlama/y2/Y2b-baski.json` bu dosyalarla
birlikte girmeli (O-1). Yeni görsel yok (`TF/montaj/gorsel/` değişmedi).

**3. madde devamı (orkestratör onayı, 15:00).** Yalnız `tasarim/freecad/montaj/montaj_gorsel.py` (tarama kaynağı değil; `arayuz.py` ve tasarım sınırları değişmedi).
Değişiklik `SP/yama_gorsel2.py` ile (CRLF korundu, her eski metin tam bir kez; önceki hâli `SP/once/src/montaj_gorsel_tur1.py`). Dosyanın tur 1 toplamı +6/−5 satır:
- `:33` yorum: tilt "−14…+14 derece (sinir −25…30)" → "−12,6…+12,6 derece (sinir ±13, Y2a)".
- `:40`, `:41` `OmuzSag_Yana` / `OmuzSol_Yana`: `%.6f` → `%.9f`. Tolerans seçeneği yetmezdi: `%.6f` ile Y0 4,999965° oluyordu, kayma 3,5e-5° > 1e-6.
  `%.9f` 0,087266463 rad yazar (≥ 5°). Değişen satır sayısı iki seçenekte de iki; geçerli olan bu.
- `:47` `Kafa_Tilt`: `0.25*sin(...)` → `0.22*sin(...)` (±12,61°, sınır ±13).
- `:98–99` (tur 1): `if Y.get("aktif")` koruması (yorum satırıyla).
Ön denetim (FreeCAD'siz, betiğin kendi `animasyon_kontrol()`'ü, arayuz sınırlarıyla): 161 kare, **ihlal 0**; uçlar Yana 5,0…68,75, Tilt −12,61…12,61.
GUI koşusu: boş bellek 3,19 GB, çalışan FreeCAD 0. `py -3 -u zincir2.py 20261109-084522-e gui:montaj_gorsel` (`SP/zincir5.out`, `SP/gui_montaj_gorsel.log`),
14:59:38–15:00:30, 52 s, **rc 0**, boş bellek 3,19 → 3,04 GB; tek koşu, yeniden başlatma yok. İç günlük (`%TEMP%/robot-montaj-kare/montaj_gorsel.log`):
"animasyon kontrolu: 161 kare … ihlal 0"; "GUI kurulumu kaydedildi: eklem 21 simulasyon Kollari_oynat hareket 14"; 3 poz görseli; "hareket karesi 81".
- **Üretilen görseller (11):** `tasarim/freecad/montaj/gorsel/` `montaj-on.png`, `montaj-yan.png`, `montaj-izometrik.png`, `montaj-omuzlar.png`, `montaj-dirsek.png`,
  `montaj-kafa.png`, `montaj-taban.png`, `montaj-taban-ic.png`, `montaj-poz-selam.png`, `montaj-poz-one.png`, `montaj-poz-kafa.png`. 81 hareket karesi depo dışında
  (`%TEMP%/robot-montaj-kare/`). Yenilenmeyenler: `montaj-gui-*.png` (5, elle alınmış GUI ekranları) ve `montaj-hareket.gif` (`montaj_rapor.py` üretir, koşulmadı).
- **`robot-montaj.FCStd` yazıldı** (GUI'den kaydedildi, 14:59:54, 5.766.891 bayt): eklem görünümü 21 eklemde, "Kollari_oynat" simülasyonu 14 hareketle.
- Not: GUI günlüğünde 84 traceback var. Hepsi FreeCAD'in `ViewProviderJoint` geri çağrılarından (`app_obj` 42, `switch_JCS1` 21, `switch_JCS2` 21 AttributeError).
  Ölümcül değil (rc 0, bütün çıktılar yazıldı). Ama FCStd GUI'de açılıp eklem görünümünün geldiği gözle doğrulanmadı (açık A9).
- Bilgi, değiştirilmedi: poz görsellerinde kafa tilt 25° / 20° (`POZ_GORSEL`, `:54-66`) ±13 sınırının dışında. Bunlar animasyon denetiminden geçmez, doğrudan yerleştirilir.
Sonra: `py -3 tasarim/freecad/carpisma_kos.py kontrol` → **çıkış 0** ("17 dosya kayitla ayni"). `py -3 planlama/d158/regresyon.py --yazma` → **çıkış 0** (GEÇER).
Çalışan FreeCAD süreci 0.
**Commit listesine ek:** `tasarim/freecad/montaj/montaj_gorsel.py`, `tasarim/freecad/montaj/robot-montaj.FCStd` (zaten listede, şimdi GUI kaydı),
11 PNG `tasarim/freecad/montaj/gorsel/montaj-{on,yan,izometrik,omuzlar,dirsek,kafa,taban,taban-ic,poz-selam,poz-one,poz-kafa}.png`.

## 10. Düzeltme turu 2 (F6a-kontrol O-3 kamera kadrajı, D-8 poz tilt'i; 09.11 15:10–15:35)

Kapsam yalnız montaj görselleri. Tek değişen kaynak `tasarim/freecad/montaj/montaj_gorsel.py` (tarama kaynağı değil). `arayuz.py`'ye ve tarama kaynaklarına dokunulmadı.
Satır sonu korundu: 289 CRLF, yalın LF 0. Bayt düzeyi yama betikleri (`SP/yama_gorsel3.py` 13 değişiklik, `SP/yama_gorsel4.py` 2 değişiklik) eski metnin bir kez geçtiğini doğrular.
Önceki sürümlerin kopyaları `SP/once/src/montaj_gorsel_tur2.py` ve `montaj_gorsel_tur2a.py` içinde. Bu dosyanın toplam farkı (tur 1 dahil) `git diff --numstat`: +21 / −17.

**Değişen satırlar (son hâl):**
- `:37–39` yeni: iki yorum satırı ve `TAM = A.BOY / (A.BOY - A.UZAMA) * 1.03`. Değeri 1580 / 1265 × 1,03 = 1,2865: boy oranı 1,249, üstüne %3 kadraj payı. Elle sabit sayı yok.
- `:61` poz-selam merkezi `(0, 820 + A.UZAMA, 0)`.
- `:64` poz-one kafa `tilt=12.0` (önce 25.0).
- `:65` poz-one merkezi `(0, 900 + A.UZAMA, 120)`. Önce 860'tı; koşu 1'den sonra 900 yapıldı (aşağıya bakın).
- `:66` poz-kafa kafa `tilt=12.0` (önce 20.0), pan 45 değişmedi.
- `:68` poz-kafa merkezi `(0, 1090 + A.UZAMA, 30)`.
- `:195` izometrik `1080 * TAM, (0, A.BOY / 2, 0)`. Önce `1000, (0, 640, 0)`; koşu 1'de `1000 * TAM` idi, koşu 1'den sonra 1080 yapıldı.
- `:197`, `:199` ön ve yan `790 * TAM, (0, A.BOY / 2, 0)`. Önce `790, (0, 635, 0)`.
- `:201` kafa `(0, 1080 + A.UZAMA, 20)`. `:203` omuzlar `(0, 900 + A.UZAMA, 20)`. `:205` dirsek `(150, 790 + A.UZAMA, 0)`.
- `:262` hareket kareleri `1340 * TAM, (0, A.BOY / 2, 40)`. Önce `1340, (0, 650, 40)`.
- Taban görünümleri (`(0, 190, 0)` h700, `(0, 170, 0)` h640) değişmedi; zaten doğru kadrajdaydı.

**Açılar:**
- Poz kafa açıları (pan / tilt): selam 30 / −10, one 0 / 12, kafa 45 / 12. Üçü de ±13 içinde.
- Animasyon `Kafa_Tilt` ucu ±12,61° (tur 1'den, değişmedi).
- FreeCAD'siz ön kontrol (betiğin üst kısmı, sahte modüllerle): animasyon 161 kare, 0 ihlal; pozlar 0 ihlal.

**Koşular** (`zincir2.py`, tek FreeCAD süreci, ön planda beklendi):
- **Deneme, 15:14:02 (`zincir6.out`):** boş bellek 1,98 GB, "BELLEK AZ, DUR". Koşmadı, koşu sayılmaz. Bellek 15 sn arayla izlendi; 1,66–1,98 GB arasında gezdi, 15:23:11'de 2,24 GB oldu.
- **Koşu 1, 15:23:17–15:24:14 (`zincir7.out`, 57 sn):** rc 0, bellek 2,21 → 2,51 GB, animasyon ihlali 0.
  - Dokuz görsel kabul edildi.
  - İzometrikte alttaki teker hafif kesikti; poz-one'da kafa tepesi üst kenara değiyordu.
  - Yalnız kamera değeri düzeltildi (`yama_gorsel4.py`): izometrik h `1000 * TAM` → `1080 * TAM`, poz-one merkezi y 860 → 900 (+UZAMA).
  - Koşu 1 görselleri `SP/gorsel_tur2a/` içinde.
- **Koşu 2, 15:25:12–15:26:09 (`zincir8.out`, 57 sn; izin verilen tek ek koşu):** rc 0, bellek 2,51 → 2,48 GB, "ZINCIR TAMAM".
  - `montaj_gorsel.log`: 161 kare, ihlal 0; eklem 21, simülasyon hareketi 14; 3 poz görseli; 81 hareket karesi.
  - GUI günlüğünde yine 84 ölümcül olmayan `ViewProviderJoint` traceback var (açık A9, değişmedi). Koşu sonrası çalışan FreeCAD süreci 0.

**Görsel kabulü (koşu 2, 11 görselin her birine Read ile bakıldı):**

| Görsel | Kadraj | Not |
| --- | --- | --- |
| `montaj-on.png` | KABUL | Kafa, iki omuz, iki dirsek ve teker tabanı tam kadrajda |
| `montaj-yan.png` | KABUL | Kafa üstten tekerlere kadar tam; omuz ve dirsek görünüyor |
| `montaj-izometrik.png` | KABUL | Kafa, omuzlar, dirsek ve tekerler kadrajda (koşu 1'deki alt kesik giderildi) |
| `montaj-kafa.png` | KABUL | Kafa tam, iki omuz başı görünüyor |
| `montaj-omuzlar.png` | KABUL | İki omuz eklemi tam kadrajda. Konu omuz olduğu için kafa yalnız alt kısmıyla girer (görünüm h 360) |
| `montaj-dirsek.png` | KABUL | Omuz, üst kol ve dirsek eklemi tam; alt kol alt kenarda |
| `montaj-taban.png` | KABUL | Taban ve tekerler tam |
| `montaj-taban-ic.png` | KABUL | İç taban, 4 teker ve kartlar tam |
| `montaj-poz-selam.png` | KABUL | Kafa, iki omuz, kalkık kol ve dirsek tam |
| `montaj-poz-one.png` | KABUL | Kafa tepesi artık kenarda değil; iki kol ve dirsek tam |
| `montaj-poz-kafa.png` | KABUL | Kafa (pan 45, tilt 12) tam; iki omuz görünüyor |

Kesik görsel kalmadı; açık madde yok.

**Denetimler:**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` → **çıkış 0** ("izlenen 17 dosyanin ozetleri kayitla ayni").
- `py -3 planlama/d158/regresyon.py --yazma` → **çıkış 0** ("Sonuç: GEÇER (hepsi okundu, kötüleşen yok)").

**Bu turda değişen dosyalar:**
- `tasarim/freecad/montaj/montaj_gorsel.py`
- 11 PNG: `tasarim/freecad/montaj/gorsel/montaj-{on,yan,izometrik,omuzlar,dirsek,kafa,taban,taban-ic,poz-selam,poz-one,poz-kafa}.png`
- `tasarim/freecad/montaj/robot-montaj.FCStd` (GUI kaydı, 15:25)
- `planlama/d158/F6a-gunluk.md` (bu bölüm)

`montaj-analiz.json`, `robot-montaj.step` ve `yerlesim-kontrol.json` bu turda yazılmadı.
