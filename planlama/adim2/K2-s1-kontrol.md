# K2 — S1 kablo kaseti bağımsız kontrol

Kontrol ajanı (bağımsız, tasarım değiştirmez). HEAD `6bb1eff` (önceki ajan `c299754`'te başladı; aradaki commit yalnız M7 kuponları /
M6 montaj sırası, CAD analiz JSON'larına dokunmuyor) + çalışma ağacındaki S1 değişiklikleri. Ölçümler `planlama/adim2/K2-*.py`.
Girdi FCStd'ler (değişmedi): omuz 09:27:09, kabuk 09:21:08, dirsek 09:32:14. Kaset türetilmiş değerleri güncel kaynakla birebir (`K2-tazelik.json`).
Durum: **2. ajan devam ediyor** (2026-10-15). Önceki ajan limitte kesildi; ölçümleri tekrarlanmadı, eksikler koşuluyor.

| # | Kontrol | Durum | Ölçülen | Not |
|---|---|---|---|---|
| 1 | Kablo (S1 U lopu, dirsek/S2 lopları) | sürüyor | U: R_min 12,91–12,99 (≥ 11,9 ✔, 10 d 15,4 ✘); S2 lopu × kaset **−0,30** (S2 120, S1 ≥ 125) ✘; U ucu ↔ cep üst ucu 0,34 (L +1 mm / S1 +1,5° ile temas) ✘ | aşağıda |
| 2 | Geometri (tambur, kaset, açıklıklar) | sürüyor | cıvata 2/2 sağ (kavrama 3,5, et ≥ 2,0, dip ≥ 1,0) ✔ | tarama koşuyor |
| 3 | Regresyon (parça, kütle, sınırlar) | geçti (notlu) | omuz 66→73, kabuk 194→206, dirsek 53; sınırlar tutarlı | bayat çıktılar + yasak kutu |
| 4 | Tork payları | geçti | S1 2,46 / 0,82, S2 2,40 / 0,81; izinli 57,5 / 51,6 g | tasarımcıyla aynı |
| 5 | Baskı (çıkıntı) | geçti (notlu) | gövde 0; kapak 38,4 mm² (2× Ø6 havşa tavanı, köprü); tambur +X 917 mm² (dudak altı 855) destekli | |
| 6 | Montaj sırası | bekliyor | | tarama koşuyor |
| 7 | Uzatma kablosu boyları | bekliyor | | |

## Günlük
- (1. ajan) Okundu: CLAUDE.md, freecad README, K-kontrol, S1-kaset.md, kablo_yolu.py, arayuz OMUZ / 13 / KOL_KABLO s1, `git diff`.
- (1. ajan) Betikler: `K2-ortak.py`, `K2-u.py` (bağımsız çözücü: bütün kablo bağdan bağa tek ayrık elastika, engel kısıtlı, temas
  topolojisi varsayılmaz), `K2-kablo.py` (s1 | duy | lop | yol), `K2-geo.py` (civata | baski | tork koşuldu), `K2-ek.py` (cep),
  `K2-ek2.py` (S2 lopu ↔ kaset haritası), `K2-yuk.py`, `K2-regresyon.py`, `K2-tazelik.py`, `K2-tarama.py` (yazılmış, koşmamış).
- (2. ajan) `K2-tarama.py` hiç çıktı vermemişti: `MeshPart.meshFromShape(MaxLength=…, LinearDeflection=…)` FreeCAD 1.1'de
  "Wrong arguments" → yalnız `MaxLength` ile düzeltildi, 4 adım (tambur, kaset, gobek, montaj) koşuyor.

### 1. Kablo — ölçülen (1. ajanın JSON'larından, 2. ajanın değerlendirmesi)
- **U lopu (`K2-kablo-s1.json`, S1 −45…135, 43 poz, N 240):** R_min 12,914–12,991 (tasarımcı 12,91 ✔). Sınır 7,5 d (3 şerit) 11,90 ✔,
  10 d 15,40 ✘. Koşu açısı en az: iç 19,9° (φ 135), dış 10,1° (φ −45). Demet ↔ kaset gövdesi/duvarı temas (tasarım gereği) giriş
  0,03–0,46 mm³ (ayrıklaştırma); temas dışı en küçük boşluk kapak flanşı 0,30 (eksenel pay, tasarımla aynı), rulman kapağı / bant 1,8.
- **İç koşu tambura sarılmıyor:** merkez çizgisi tamburdan φ −45'te 3,3, 0'da 1,0, ≥ 45'te ≤ 0,25 mm kalkıyor (aralık dışı −70'te 5,1).
  Demet iç kenarı r 39 + 3,3 = 42,3 < dudak r 43,7 → dudaklar arasında hâlâ 1,4 mm kalıyor. S1 ekseni yatay (x), yerçekiminin eksenel
  bileşeni yok. Dudak ↔ flanş / arka plaka (x, r) kaçış aralığı ayrıca ölçülüyor (`K2-dudak.py`).
- **Dudak tutuyor mu (`K2-dudak.json`, 2. ajan):** (x, r) kanal haritası, φ −45 / 45 / 135 × ψ_sabit 110…320:
  - Kaset kapsamında (ψ 190…335): r 40…43,5 tambur dudakları arası x 153,5–158,3; r 43,7…44,2 arası 0,5 mm radyal halka
    aralığı +x'e açık (dudak 43,7 ↔ flanş 44,2) — 1,4 mm şerit geçemez ✔; r ≥ 44,25 arka plaka 153 ↔ flanş 158,3 ✔ (ψ 215'te r ≥ 46,5
    −x açık = çıkış yarığı, tasarım gereği).
  - **Kaset dışında (ψ < 190) r ≥ 43,75 her iki yan açık**: demeti yalnız tambur dudakları tutar.
  - İç koşu kalkması en çok φ −45'te ψ_sabit 162,9 (ψ_g 207,9) — **kasetin dışında**; kalkan bölge (> 0,5 mm) ψ_sabit 115…212.
    Demet iç kenarı r 42,30 → dudak kavraması **1,40 mm ✔** (φ −30: 2,44; 0: 3,68; 45: 4,45). Aralık dışı φ −70: kalkma 4,99, iç
    kenar 43,99 → **−0,29 (dudaktan çıkar)**.
  - **Duyarlılık (K2-kablo-duy kalkma değerlerinden):** φ −45'te L +10 → kalkma 4,10 (kavrama 0,6), L +20 → 4,97 (−0,27); tambur
    bağı 5° dışarı → 4,95 (**−0,25**), 10° → 6,69, 15° → 8,77. Yani bağ kablo tamburdan 5° dışarı açıyla bağlanırsa S1 −45'te iç
    koşu kaset dışında dudağın üstüne çıkar ve +x'e (kol tarafına; kol x ≥ 160,07) kayabilir. Yerçekiminin eksenel bileşeni yok
    ama kol/kablo teması ve titreşim yeter. Öneri: tambur bağına teğet kılavuz oluğu (bağ 0° ± 2° kalsın) + montaj talimatı;
    L toleransını tek yönlü (−5…0) tut; ya da kaset alt ucunu ψ0 190 → ~110'a uzatmayı değerlendir (kol sektörü ψ 155…201,
    x ≥ 160,07 → flanşa 0,57; ayrıca ölçülmeli).
- **Aşım (`K2-kablo-duy.json`):** S1 −70…−50: R 12,98–13,04, dış koşu 1,7°'ye iner, sorun yok. **S1 > 135:** U ucu kaset cebinin üst
  ucuna girer: 137,5'te 37 mm³, 140'ta 130 mm³ (R değişmez ama demet uç duvara ezilir).
- **Cep üst ucu (`K2-ek-cep.json`) — YENİ BULGU:** φ 135'te U ↔ cep ucu boşluğu 0,34; φ 135,5 → 0,21, 136 → 0,03, 137 → −0,34 (21 mm³).
  Lop boyu L toleransı: +0,5 mm → 0,14, **+1 mm → −0,12 (4,2 mm³)**, +2 → −0,63 (47 mm³), +5 → −2,1 (214 mm³). L −10 sorunsuz.
  Bağ açısı tamburdan dışarı 15° → R 12,07 ve cep −0,06. Yani U ucunun payı ≈ 0,4° ψ = **L +0,7 mm ya da S1 +1° aşım**; elle bağlanan
  lopta ±5–10 mm beklenir (K: ±10 mm). Dikme ψ 200 / 226 en az 4,4 / 6,5, pim ψ 331 en az 3,3 ✔.
- **Duyarlılık (φ −45 / 45 / 135):** L ±20 → R 12,88–13,02; bağ açısı ±15° → 12,07–13,10; eksen kaçıklığı ±1 → 12,53–13,32;
  h 31 / 33 → 12,53 / 13,38; şerit 1,8 (demet 5,4) → 12,47 (o zaman sınır 7,5 d = 15,3 ✘). En kötü 12,07 ≥ 11,9 ✔ (pay 0,17).
- **S2 lopu S1 × S2 (`K2-kablo-lop.json` S1 −45…135 / 5° × S2 5…120 / 3°, kabuk + kaset + omuz gövde dahil; `K2-ek2.json` dikdörtgen
  kesit):** R_min 12,39 (S2 120) ✔; göbek/kol boşluğu en az 1,90 (S2 5, kol çatalı) ✔. **Sabit parçalara: S2 ≤ 72'de ≥ 5,1 (rulman
  kapağı); S2 ≥ 75'te en yakın kaset kapağı flanşı, S2 111 → 1,08, 114 → 0,62, 117 → 0,15, 120 → −0,32 (çevrel) / −0,30 (dikdörtgen)
  — S1 ≥ 125'te.** En yakın nokta lopta x 160,7, r 42,4: flanşın iç kenarı (r 44,2, x 159,5) dairesel olduğundan S1 125…135'te aynı.
  Tasarımcının S2 lopu kontrolü (`dirsek_montaj` 8b) kaseti içermiyordu → bu çakışma görülmemiş.
  **Pah önerisi (`K2-dudak.json`, geçici kesim):** flanş iç kenarının dış (x 159,5) köşesine tam kalınlık 1,2 × 1,2 pah (iç yüz
  x 158,3'te r 44,2 korunur, tutma değişmez): S2 120 → **+0,39**, 117 → 0,89, 114 → 1,39. 1,2 × 2,0 aynı (+0,39); 0,8 × 0,8 → +0,14.
  Pah tek başına 0,5 payı vermiyor: pah + S2 üst sınırını S1 ≥ 120'de 117'ye çekmek ya da S2 lopu bağ açısını ayarlamak gerekir.
- **Dirsek lopu:** R_min 13,03 (105°), boşluk 0,61 (ön kol) → değişmedi ✔.
- **Geçiş G2 → tambur bağı (`K2-kablo-yol.json`):** 23,9 mm; göbeğe 4,28, tambura (son 8 mm hariç) 5,85, sabit parçalara 3,62
  (kaset kapağı, S1 110) — merkez çizgisi mesafesi; yarı kalınlık 2,1 / çevrel 2,97 → net ≥ 0,65 ✔ (ince). **Çıkış:** 238,0 mm;
  merkez çizgisi kaset 2,4 / bant 3,0 / omuz gövde 8,98 / göbek + tambur 8,3 → net kaset 0,30, bant 0,90 ✔; yarık ışını kapakta 1,2 mm.

- **10 × d sağlanmıyor — gerçek kablo ve döngü riski (değerlendirme, sayılar tahmini):** R 12,9 tek şerit (1,4) için ≈ 9 × d
  (3 şerit sınırının içinde 7,5 d'nin üstü). Kablo bakır yorulması tel çapıyla ölçeklenir: 0,08 mm telli 22 AWG silikonda tel
  şekil değiştirmesi ≈ 0,04 / 12,9 = %0,3, kaba telli PVC servo kablosunda (≈ 0,1–0,12 mm, tahmini) ≈ %0,4–0,5 → bakır için 10⁵+
  döngü mertebesi; asıl risk PVC kılıfın dış lifinde %5'e varan şekil değiştirmesi (soğukta çatlama) ve şeritlerin kayıp
  kabarması. Kullanım tahmini: gösteri günü ~500–1000 S1 hareketi → proje ömrü (1–2 yıl) 10⁴–10⁵ döngü: silikon için düşük-orta,
  PVC için orta risk. **Bulgu:** S1 U'sundan geçen 3 şeritten biri DS3218'in **kendi PVC kablosu** (`s2_servo_kablo`: servo kablosu
  yarığa kadar uzanıyor, birleşim kabuk içinde) → hem dinamik sınıfta değil hem de diğer iki silikon şeritten farklı sertlikte
  (karışık sertlikli şeritler U'da ayrılır). Öneri: S2 servo kablosunu göbekte (G2 öncesi) silikon uzatmaya bağla, U'dan 3 aynı
  silikon şerit geçsin; kablo kesitini ölç; M7'ye kaset + kabloyla 10⁴ döngü tezgâh kuponu ekle.

### 6. Montaj sırası (geometri mantığı; tarama sonuçları aşağıya eklenecek)
- Bant → tambur göbeğe (tezgâhta, 3 × M3×8 −x yüzden; M6: bant takılıysa başa 12,5 mm) → göbek rulmana: tambur r 43,7 Ø84 delikten
  büyük ama +x tarafta kalıyor, göbekle birlikte +x'ten takılır ✔ (M6 ile aynı).
- **"Kablo U'ya → kaset +x'ten" bu sırayla geometrik olarak mümkün değil:** kaset gövdesinin arka plakası (x 152–153, r 46,5–77)
  +x'ten kaydırılırken kanal bölgesini (x 153,8–158, r 39–75) baştan sona süpürür; U ve dış koşu orada duruyorsa plaka kablonun
  içinden geçmek zorunda. Uygulanabilir sıra: **gövde** (+x'ten; plaka iç r 46,5 > dudak 43,7, kablo yokken) → kablo: G2 → tambur
  bağı (kayış) → U elle kanala, dış koşu duvar boyunca, ψ 214'te radyal içeri, gövdenin yarığı + ped yarığından içeri (JR erkek
  10,3 × 4 / 12 × 6 ✔) → **kapak** (+x'ten; flanş iç r 44,2 > dudak 43,7, 0,5 radyal) → uç pimi + 2 dikme cıvatası. Gövde cıvatasız
  olduğundan kapak gelene dek elle tutulur. S1-kaset.md ve M6 G4 satırı (41) bu iki parçalı sıraya göre düzeltilmeli.

### 7. Uzatma kablosu (`dirsek-analiz.json` kablo.s1_boy, bağımsız toplama)
- Dirsek / bilek: birleşim → G2 175,7 + geçiş 23,9 + U 171,4 + çıkış/gövde içi 238,0 + gövde içi → dikey 0 + dikey → dağıtım A 901,5
  + konnektör 30 = **1.540,5 ✔ (1.541)**. Dikey yol bağımsız: 500 + 140,2 + 61,1 + 156,7 = 858,0 + kart A'ya ≈ 43 ✔.
- S2: servo kablosu 300 → G2 40 (tahmini) + 23,9 + 171,4 + yarığa 54,7 = 290 → kalan 10 (şart 7) ✔; uzatma 238,0 − 54,7 + 901,5 +
  30 − 10 = **1.104,8 ✔**. Kol başına 2 × 1.541 + 1.105 = 4.187; iki kol **8,37 m ✔** (B1 "~8 m" ile uyumlu).
- Makul mü: boy doğru ama payı yok. Öneri: kablo başına +%10 servis/kıvrım payı → satın alma ≈ 9,2 m (10 m makara). S2 kalan
  payı 3 mm (10 − 7) ve G2'ye 40 mm tahmini: yukarıdaki öneriyle (göbekte silikon uzatmaya geçiş) bu sınır da kalkar.
- Gerilim düşümü (tahmini, 22 AWG 52,9 mΩ/m, gidiş-dönüş): dirsek/bilek ≈ 1,84 m kablo → 0,19 Ω → 2,5 A tutukta ≈ 0,5 V (6 V'un %8'i);
  S2 ≈ 1,4 m → 0,15 Ω → ≈ 0,4 V. S2 yüklü tork payı zaten 0,81: gerilim düşümüyle daha da azalır; E1 bütçesine girmeli.

### 2. Geometri — ölçülen
- **Kaset cıvatası (`K2-geo-civata.json`, sağ ψ 200 / 226):** vida x 148,5–159,5, ısıl gömme x 146,3–152 (Ø4) → kavrama 3,5 ✔; baş
  kapakta oturuyor (temas 0, giriş 0); vida/gövde/bant girişi 0. Isıl gömme çevre eti 2,0 mm tam (2,5'te %3–4 eksik), ped kenarına
  2,0; delik dibi 0,5 boşluk + ≥ 1,0 et ✔. Sol taraf simetrik (kabuk analizi 4/4).

- **Duvar bağı (ψ 228,3) için kasette bağlama özelliği yok (`K2-yuk.json`):** ψ 220…236'da duvar kesintisiz, gövde/kapakta bu
  bölgede delik/yarık yok (küçük silindirler yalnız dikme ψ 200/226, yarık uçları ψ 214 r 49/55, pim ψ 331 ve U cebi kavisi).
  Tamburda bağ için 2 yarık var (ψ_g 148 / 156). Kablonun duvar ucu yalnız ψ 214 radyal dönüşü + 12 × 6 yarıkla tutuluyor →
  L montajda sabitlenemez, S1 hareketiyle yarıktan sürünebilir; U ucu payı L +0,7 mm olduğundan bu doğrudan cep çakışmasına gider.
- **Kaset üst ucu yük (`K2-yuk.json`, değerlendirme):** arka plaka kabuğa r 60'ta yalnız ψ 210…300, r 76'da ψ 227…233 dayanıyor;
  ψ 300…335 (r 60'ta ≈ 37 mm) konsol, kabuğa bağlı değil. Kesit (ψ 240…310): gövde tek başına A 43,6 mm², W_x 21,3 mm³; gövde +
  kapak tek kesit sayılırsa W 195 mm³; ikisi yalnız uç pimi ve dikmelerle bağlı olduğundan gerçekte ikisinin arası (ayrı çalışırsa
  ≈ 21 + 8 = 29). x yönü (gövdeye / dışarı) uç kuvveti, σ_izin 20 MPa (PETG-CF katman içi, tahmini), kol 40 mm: **≈ 15 N (ayrı) …
  100 N (tam bağlı)**. Çalışma yükü yok (U'nun duvara itmesi < 0,1 N) → işlev için yeterli; çarpma / elle bastırma (1,5 kg) için
  zayıf olabilir. Öneri: ψ ≈ 300'de gövde ↔ kapak arasına ikinci pim (kesme bağı) → tam kesite yaklaşır; M7'de uç yük kuponu.

- **Taramalar (`K2-tarama-*.json`, nokta bulutu + kesin distToShape en küçük 6 pozda; 2. ajan):**
  - Tambur ↔ sabit (omuz gövde, bant + ısıl gömme, kaset + cıvata), S1 −60…180 / 1°: **0,50** (kaset gövde/kapak, tasarım boşluğu,
    her pozda) ✔. Tambur ↔ kapak M3 cıvata başları: **0,709** ✔ (≥ 0,5; tasarımcı 0,7).
  - Tambur ↔ kol (S2): 5° → **0,825** ✔ (tasarımcı 0,82); 4,25 → 0,37, 4,0 → 0,22, 3,75 → 0,06, **3,5 → 0 (temas)**: kol mekanik
    dayanağı S2 ≈ 3,6°. ≥ 20°'de 11,7 sabit.
  - Göbek (tambur hariç) ↔ kaset + kabuk bant + ısıl gömme, S1 −60…180 / 1°: **3,50** (kaset kapağı) ✔ — önceki taramada hiç yoktu.
    Bant + kaset ↔ omuz gövde: 1,0 (bant ↔ rulman kapağı, önceden de böyle) ✔.

### 3. Regresyon — ölçülen (`K2-regresyon.json`)
- omuz 66 → 73, kabuk 194 → 206 (baskı 15 → 19), dirsek 53 → 53. Kasıt dışı parça / kütle farkı yok (kütle farkı yalnız PETG-CF
  ρ × 0,9 ve yeni parçalar; BOM yalnız kaset/tambur cıvata + ısıl gömme). Omuz serbest poz farkı yalnız S2 −5/0 (aralık dışı).
- `eklem_sinirlari.json` üreticiyle aynı; `arayuz.OMUZ` yana [5, 120] = json r_s2 / l_s2 = omuz-analiz eklem_siniri ✔.
  `eklem_dogrulama.py`, `montaj_gorsel.py`, `omuz_gorsel.py`, `omuz_goster.py`, `carpisma.py` Y0 / YANA_MIN'i arayuz'dan okuyor ✔.
- Kalıntı (kod/çıktı): **bayat üretilmiş çıktılar** `montaj/eklem-dogrulama.json` (poz adları "yana 0": betik Y0 = 5 kullanıyor, json
  yeniden koşulmamış), `montaj/gui-kontrol.json` ("sinir 0"), `carpisma-sonuc.json` + `carpisma-bolum/*.json` (C7'de yenilenecek).
  Yorum kalıntıları: `dirsek_montaj.py` 464/470/639/699 ("yana 3…120", "alt sinir 3"), `iskelet_montaj.py` 248. Rapor metinleri
  (dirsek/kabuk/iskelet/kafa/taban/montaj, OZET.md, freecad README "0…120") belge adımında (tasarımcı açık sorun 6).
- **Yasak kutu kol koşulu yana [5, 5]:** kafa-kol çakışması 15° ızgarada yalnız yana 0'da görülmüştü (yana 15'te yok); 0 ± 5 alt
  sınır 5'e kırpılınca tek nokta kaldı. Etki: yazılım koşulu yalnız yana tam 5,0'da tetikler; yana 5…15 arası **ölçülmemiş** ve
  korumasız. Öneri: C7'ye kadar koşulu yana [5, 15] (çakışmasız ölçülen ilk ızgara noktası) yap; C7'de öne 120…135 × yana 5/7,5/10/12,5/15
  × dirsek 65…105 × kafa kutusu tara, sonra daralt.

### 4. Tork (`K2-geo-tork.json`, FCStd hacim × ρ, 58.608 poz, 0,5 kg el yükü, DS3218 20 kg·cm)
- Kütle: göbek 175,17 (FCStd 175,0), kol 146,89 (146,8), üst kol 103,53, ön kol 188,92, el 74,98 g ✔.
- S1 yüksüz 8,135 kg·cm (pay 2,46), yüklü 24,35 (0,82), 2× pay izinli yük 57,5 g; S2 8,32 (2,40) / 24,60 (0,81) / 51,6 g → tasarımcıyla aynı ✔.

### 5. Baskı (`K2-geo-baski.json`, bağımsız 45° çıkıntı, tablaya 0,15 mm üstü)
- Kaset gövdesi (arka yüz x 152 tablada): çıkıntı 0 → desteksiz ✔.
- Kaset kapağı (flanş x 159,5 tablada): 38,4 mm² = 2 × 19,2 (dikme başlıklarında Ø6 havşa tabanı x 156,5, 3 mm yukarıda; Ø3,4
  delikli köprü, 6 mm açıklık) → desteksiz basılır, köprü (kurban katman önerilir) ✔.
- Tambur +X (−x dudak tablada): 917 mm² (+x dudak altı 855 = C halka r 39 → 43,7, 4,7 mm konsol; 3 × 15,9 vida oturma köprüsü);
  −X yönü 2004 mm² → +X doğru seçim, **destekli** (tasarımcı 769 mm², yöntem farkı). Destek 4,8 × 4,7 mm C-kanalı doldurur ve
  kablonun sürtündüğü r 39 yüzeyinde iz bırakır: dudak ayrı pul seçeneği (tasarımcı açık sorun 4) daha temiz.
