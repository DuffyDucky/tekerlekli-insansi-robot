# K2 — S1 kablo kaseti bağımsız kontrol

Kontrol ajanı (bağımsız, tasarım değiştirmez). HEAD `6bb1eff` (önceki ajan `c299754`'te başladı; aradaki commit yalnız M7 kuponları /
M6 montaj sırası, CAD analiz JSON'larına dokunmuyor) + çalışma ağacındaki S1 değişiklikleri. Ölçümler `planlama/adim2/K2-*.py`.
Girdi FCStd'ler (değişmedi): omuz 09:27:09, kabuk 09:21:08, dirsek 09:32:14. Kaset türetilmiş değerleri güncel kaynakla birebir (`K2-tazelik.json`).
Durum: **kapandı — KOŞULLU GEÇTİ** (3. ajan, 2026-10-25, plan Y1; aşağıda "Sonuç"). 2. ajan 15 Ekim 22:16'da PC reset'le kesildi; girdi FCStd'ler o günden beri
değişmedi (omuz 09:27:09, kabuk 09:21:08, dirsek 09:32:14) → önceki ölçümler geçerli, tekrarlanmadı; eksikler ve taslak-170 3. ajan günlüğünde.

**KARAR (3. ajan, 25 Ekim 2026): KOŞULLU GEÇTİ** — hem 125 cm modüller hem `taslak-170` için (S1 çevresi taslakta birebir aynı).
Kaset/tambur geometrisi, eklem aralığında kol ve göbekle çakışmasızlık, tork, baskı, cıvata, regresyon ve montaj yolu geçiyor.
Geçmesi için 6 koşul (K1–K6, aşağıda "Önerilen düzeltmeler") tasarım ajanına; K1 ve K2 olmadan üretime geçilmemeli.

| # | Kontrol | Durum | Ölçülen | Not |
|---|---|---|---|---|
| 1 | Kablo (S1 U lopu, dirsek/S2 lopları) | **koşullu** | U R_min 12,91 (7,5 d 11,90 ✔; 10 d 15,40 ✘); d ≤ 1,5 ✔, **22 AWG silikon (1,7) ✘** (R ve kanal); S2 lopu × flanş **−0,30** (S2 120, S1 ≥ 125) ✘; U ucu ↔ cep 0,34 (L +0,7 / S1 +1°) ✘; **tambur bağı kayışı ↔ kapak cıvatası 0,18 mm³** ✘ | K1–K4 |
| 2 | Geometri (tambur, kaset, açıklıklar) | geçti | tambur ↔ sabit 0,50; ↔ kapak cıvatası 0,709; göbek ↔ kaset 3,50; kaset ↔ kol 1,254 (S2 5); cıvata kavrama 3,5 | |
| 3 | Regresyon (parça, kütle, sınırlar) | geçti (notlu) | omuz 66→73, kabuk 194→206, dirsek 53; sınırlar tutarlı | bayat üretilmiş çıktılar (C7/Y4) |
| 4 | Tork payları | geçti | 125: S1 2,46 / 0,82, S2 2,40 / 0,81 (DS3218); taslak DS3235: S1 2,80 (taslak hesap) | |
| 5 | Baskı (çıkıntı) | geçti (notlu) | gövde 0; kapak 38,4 mm² köprü; tambur +X destekli | dudak ayrı pul seçeneği |
| 6 | Montaj sırası | **geçti (yeni sıra)** | yalnız +x kaydırma ✘ (K2-kaydir); **önden radyal: gövde 0, kapak (x +3,3…5) 0**; cıvata erişimi S1 −45 / S2 90 ≥ 8 | K5 metin düzeltmesi |
| 7 | Uzatma kablosu boyları | geçti (notlu) | 125: 1.541 / 1.105, iki kol 8,37 m; taslak ≈ 2.006 / 2.038 / 1.540, iki kol ≈ 11,2 m | DS3235 kablosu 300 ± 5 → S2 payı en kötü 5 < 7 |
| 8 | Ev pozu (S2 0) 6 çakışması | modelleme artığı | S2 0: 97,87 / 65,01 / 7,61 mm³ (×2); S2 ≥ 3,75: 0 | K6 (kontrol pozu S2 5) |
| 9 | taslak-170 | koşullu (125 ile aynı) | S1 çevresi 67/77 parça birebir, farklı 10 yalnız tüp/dirsek; kol ↔ kaset 1,254, ön kol/el > 3 mm | aynı K1–K6 |

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


## 3. ajan (2026-10-25, Y1)
- Okundu: CLAUDE.md, dongu.md (Kurallar + 1,70 m planı), S1-kaset.md, bu günlük, K2-* JSON/py, KOL125/CATAL kontrol notları.
  Girdi FCStd tarihleri değişmemiş (yukarı). `K2-tarama.py` montaj adımı hiç çıktı vermemiş (K2-tarama-montaj.json yok);
  `K2-kaydir.json` (2. ajan, 19:14) var ama günlüğe işlenmemiş → aşağıda.
- `K2-kaydir.json` (2. ajan, işlenmemişti): kaset gövdesi / kapağı **yalnız +x yönünden** kaydırılamıyor. Kapak t 4,0'te göbeğe
  (S1 −45), t 3,0'te üst kol tüpüne (S1 0, S2 5); gövde t 10,5'te göbeğe (S1 −45), t 4,5'te tüpe (S1 0). Yani 2. ajanın "gövde +x'ten"
  sırası da olmuyor → `K2-montaj.py` ile düzlem içi (radyal) yol aranıyor.
- **Kaset cıvatası alet erişimi (`K2-montaj-erisim.json`, +x doğrusu baş üstü → x 330, göbek + kol):** S2 90'da ψ 200 cıvatası S1
  −60…155'te, ψ 226 cıvatası her S1'de ≥ 8 mm açık; S2 5'te ψ 200 için S1 −60…−30, ψ 226 için S1 −60…0 açık ✔. Önerilen montaj pozu
  S1 −45, S2 90 (iki cıvata da ≥ 8).
- **Kablo kalınlığı ≤ 1,4 şartı ↔ tasarımda yazılı kablo çelişiyor (YENİ):** S1-kaset.md ve 7. madde "22 AWG silikon çok telli" diyor.
  22 AWG 60 × 0,08 silikon dış çapı **1,7 ± 0,1 mm** (akkuteile.de veri sayfası özeti; Maplin 0,78 iletken + 0,55 yalıtım = 1,7);
  24 AWG 40 × 0,08 silikon bile 1,6 (Maplin). 1,4'ün altına ancak ince duvarlı PVC düz servo kablosu (22 AWG, kesit ölçülmeli) ya da
  26 AWG iner. Sonuç (S1 U modelinden, şerit 1,4 → R 12,91, 1,8 → 12,47 doğrusal ara değer): d 1,7'de R ≈ 12,58 < 8,5 d = 14,45 ✘ ve
  eksenel genişlik 3 × 1,7 = 5,1 > tambur dudakları arası 4,8 → **demet kanala sığmaz** ✘. Eşik: R ≥ 8,5 d → d ≤ 1,50; eksenel
  3 d + 2 × 0,3 ≤ 4,8 → d ≤ 1,40. Silikon 22 AWG için kaset h ≈ 36,6 (duvar r +4,6) ve kanal ≥ 5,7 mm gerekir.
- **Tambur kablo bağı kayışı (`K2-montaj-kayis.json`, YENİ):** bağ yarıkları (ψ_g 148 / 156) arasında halkanın altından geçen kayış
  (1,0 × 2,5, r 36…37) sabit omuz parçalarına çarpıyor: **kapak cıvatası M3x12 başı**, S1 101…114 ve 122…135'te 0,18 mm³'e kadar
  (−45'te değme). Bağ sektöründe tambur iç yüzü (r 37) ↔ rulman kapağı / kapak cıvataları en az **0,50 mm** (S1 −45) → 1,0 mm kayış
  halkanın altına sığmıyor; S1 her dönüşte kayış kilidi/ucu cıvata başına takılabilir. Tasarımda bağ yöntemi modellenmemişti.
- **taslak-170 kıyas (`K2-taslak-kiyas.json`):** taslak FCStd'den S1 çevresindeki 77 modül parçası sağ omuz yereline (− OY − DY 435)
  alındı: **67'si birebir** (hacim, merkez ≤ 0,05, ortak hacim oranı > 0,9999; iki yanda): tambur, göbek, kol çatalı, kaset gövde/kapak,
  kaset cıvataları, omuz bandı, ısıl gömmeler, omuz gövdesi. Farklı 10: üst kol tüpü (+30 uç tarafta), dirsek çatalı (8 mm, −30) ve
  bilezik cıvata/pul/somunları (dirsekle −30). Yani S1 kaseti yerel geometrisi taslakta **aynı**; 125 cm ölçümleri geçerli.
- **Ev pozu 6 çakışması taslakta yeniden (`K2-taslak-ev.json`, kol zinciri S2 ekseninde döndürülerek, iki yan aynı):**
  S2 0: kol çatalı ↔ tambur 97,87, tüp ↔ tambur 65,01, tüp ↔ kaset kapağı 7,61 mm³ (statik-yeni-444 ile birebir);
  S2 3,0: 6,98 / 0,84 / 0 (kapak yok); S2 3,5: yalnız çatal ↔ tambur 0,17; **S2 3,75 / 4 / 4,5 / 5: 0**. (En küçük mesafe 0 =
  S2 horn ↔ servo mili, eş eksen tasarım teması.)
- **Kalınlık duyarlılığı, bağımsız çözücüyle (`K2-serit.py` → `K2-serit.json`, 3 şerit radyal yığın, φ −45 / 45 / 135):**

  | tel/şerit d | duvar | R_min | sınır 7,5 d + d | eksenel 3 d (dudak arası 4,8) | sonuç |
  |---|---|---|---|---|---|
  | 1,4 | r 75,2 | 12,92 | 11,90 | 4,2 | ✔ (pay 1,02) |
  | 1,5 | r 75,2 | 12,80 | 12,75 | 4,5 | ✔ sınırda (pay 0,05; eksenel her yanda 0,15) |
  | 1,6 (24 AWG silikon) | r 75,2 | 12,69 | 13,60 | 4,8 | ✘ |
  | 1,7 (22 AWG silikon) | r 75,2 | 12,58 | 14,45 | 5,1 | ✘ (kanala da sığmaz) |
  | 1,6 | +3 (r 78,2) | 13,84 | 13,60 | 4,8 | ✔ R; eksenel ✘ |
  | 1,7 | +4,6 | 14,34 | 14,45 | 5,1 | ✘ |
  | 1,7 | +6 (r 81,2) | 14,87 | 14,45 | 5,1 | ✔ R (pay 0,42); kanal ≥ 5,7 gerekir; U ucu ψ 324,3 → 327,4 |
  Varyantlarda L dış koşu yayıyla birlikte uzatıldı (yaklaşık: L + Δr·(110° + 0,8·90°)). Sonuç: **mevcut kaset d ≤ 1,5 mm için
  geçerli**; silikon tel kullanılacaksa duvar +6, kanal +0,9 (görünüm ≈ +6 mm), U cebi/pim yeniden.
- **Montaj yolu (`K2-montaj-radyal.json`, düzlem içi yaklaşma sektör ortaortayı ψ 261,9 yönünden = önden, s 90 → 0; hedef kabuk sağ
  parçaları + göbek + kol; ortak hacim):**
  - **Gövde** x ofset 0'da (arka plaka omuz pedine yaslı kayar): S1 −45 / −20 / 0 × S2 90 ve S1 −45 × S2 5'te **çakışma 0** (en az 0 =
    omuz bandına kayma teması) ✔.
  - **Kapak** x ofset 3,3'te (pim 3,0 mm + dikme başlığı alt yüzü x 158,3 = duvar üstü): dört pozda **çakışma 0** (başlık duvar üstünü
    0 boşlukla sıyırıyor). Ofset 3,6'da S1 −45 / −20'de göbekle 0,05–1,77 mm³ ✘, **S1 0 × S2 90'da 0** (en az 0,30). Son eksenel adım
    (3,6 → 0, pim yuvasına) çakışma 0, gövdeye 0,1 ✔.
  - Uygulanabilir sıra: bant → göbek + tambur → kablo G2 → tambur bağı → **kaset gövdesi önden radyal** (kablo U'su henüz kanala
    alınmadan; gövde iç r 46,5 > dudak 43,7) → U elle kanala, dış koşu duvar boyunca, ψ 214 → yarık → **kapak önden radyal, flanş
    gövdeden ≈ 3,5 mm havada (S1 0, S2 90)** → kapak −x 3,5 mm (pim) → 2 dikme cıvatası (+x, S1 −45 / S2 90'da ≥ 8 mm açık).
    Kapak radyal kayarken başlık alt yüzü kablonun üstünden ≥ 0,3–0,6 geçer (kanal x ≤ 158,0).

## Sonuç (3. ajan, 2026-10-25) — KOŞULLU GEÇTİ

### Bulgular
| # | Bulgu | Ağırlık | Ölçüm / kaynak | 125 | taslak-170 |
|---|---|---|---|---|---|
| B1 | Kablo kalınlığı şartı ↔ yazılı kablo çelişkisi: 22 AWG silikon 1,7 mm → R 12,58 < 14,45, eksenel 5,1 > 4,8 | yüksek | `K2-serit.json` | ✘ | ✘ (aynı) |
| B2 | Tambur bağı kayışı halkanın altına sığmıyor (bağ sektöründe radyal boşluk 0,50 < 1,0), S1 101…135'te kapak cıvatası başına 0,18 mm³ | yüksek | `K2-montaj-kayis.json` | ✘ | ✘ |
| B3 | S2 lopu × kaset kapağı flanşı −0,30 (S2 120, S1 ≥ 125), aralık içinde | orta | `K2-kablo-lop.json`, `K2-ek2.json` | ✘ | ✘ |
| B4 | U ucu ↔ cep üst ucu 0,34 (L +0,7 mm ya da S1 +1° ile temas); duvar bağı yok, L sürünebilir | orta | `K2-ek-cep.json`, `K2-yuk.json` | ✘ | ✘ |
| B5 | Montaj: kaset +x'ten takılamıyor (S1-kaset.md sırası yanlış); önden radyal yol çakışmasız | orta (belge) | `K2-kaydir.json`, `K2-montaj-*.json` | ✔ yeni sırayla | ✔ |
| B6 | Ev pozu 6 çakışması yalnız S2 < 3,75°'te (aralık dışı) | bilgi | `K2-taslak-ev.json` | artık | artık |
| B7 | 10 × d (15,4) sağlanmıyor; R 12,91 = 7,5 d sınıfı | düşük-orta (ömür) | `K2-kablo-s1.json` | ⚠ | ⚠ |
| B8 | İç koşu S1 −45'te kaset dışında dudak kavraması 1,40 (bağ 5° dışarı → −0,25) | düşük-orta | `K2-dudak.json` | ⚠ | ⚠ |
| B9 | Kaset üst ucu konsol (ayrı çalışırsa ≈ 15 N) | düşük | `K2-yuk.json` | ⚠ | ⚠ |
| B10 | S2 servo kablosu U'dan geçiyor (PVC, farklı sertlik); DS3235 kablosu 300 ± 5 → yarık payı en kötü 5 < 7 | orta | datasheet (aşağıda) | ⚠ | ⚠ |
| B11 | Yasak kutu kol koşulu yana [5, 5] tek nokta | düşük (yazılım) | `K2-regresyon.json` | ⚠ | ⚠ |

Geçenler: tambur ↔ sabit 0,50 / cıvata başı 0,709 (S1 −60…180); göbek ↔ kaset 3,50; kaset ↔ kol 1,254 (S2 5, S1 15…135); taslakta
2.553 kesin pozda yine 1,254, ön kol / el / dirsek çatalı hiçbir pozda 3 mm'ye girmiyor (`K2-taslak-kolkaset.json`); U R_min 12,91 ≥
11,90 (duyarlılık en kötü 12,07); dirsek lopu 13,03; geçiş ≥ 0,65, çıkış ≥ 0,30 net; kaset cıvatası kavrama 3,5 / et 2,0; tork, baskı;
JR erkek 10,3 × 4 ve dişi 7,9 × 2,75 → yarık 12 × 6 ✔ (S2 servosunun dişi ucu dahil).

### Ev pozu 6 çakışmasının değerlendirmesi (soru 2)
- **Gerçek değil, modelleme artığı.** FCStd'ler kolu mekanik sıfırda (S2 0) tutuyor; S2 aralığı [5, 120]. Ölçüm (taslak, iki yan
  aynı): S2 0 → 97,87 / 65,01 / 7,61; 3,0 → 6,98 / 0,84 / 0; 3,5 → 0,17 (yalnız çatal ↔ tambur); **≥ 3,75 → 0**. 125'te kol ↔ tambur
  mesafesi S2 5'te 0,825 (`K2-tarama-tambur.json`). Kol S2 0'a fiziksel olarak gelemez: ≈ 3,6°'de tambur dudağına dayanır.
- **Dayanak güvenli mi:** tambur göbeğe bağlı, kol da göbekteki S2 servosuna → aynı gövde, S1 dönerken sürtünme yok. Sabit kaset
  kapağına temas ancak S2 < 3,0'te (tambur dayanağının ≈ 0,6° gerisinde) → dudak kırılmadıkça olmaz. Güçsüz kolun dayanağa yükü
  (tahmini: taslak S2 statik 10,9 kg·cm × sin 3,6° ≈ 0,07 N·m, kol ≈ 25–45 mm) **≈ 1,5–3 N**: PETG-CF dudak için küçük.
- **Geometri düzeltmesi önerilmiyor.** Önerilen en küçük değişiklik (K6): statik / ev pozu çakışma kontrolünü **yazılım ev pozunda
  (S2 5)** yapmak, S2 0'ı "bilgi" olarak raporlamak — `omuz_montaj.py`'nin 15 Ekim'den beri yaptığı gibi (`statik_s2_0`). Y2'de
  `taslak_analiz` statik bölümü, `carpisma.py` statik bölümü ve ana montaj raporu buna göre. FCStd yerleşimi S2 0'da kalır.
- **FCStd ev pozunu 5°'ye almak (alternatif) — etkisi:** eklem sıfırı kayar → `eklem_sinirlari.json` / `arayuz.OMUZ` açıları ya
  0…115'e kaydırılır ya da her yerde +5 ofset taşınır; `ana_montaj` "ev pozunda kimlik yerleşim" varsayımı, `eklem_dogrulama`
  pozları, `carpisma` ızgaraları (YANA_MIN), kol/taslak tork pozları ve montaj rehberi adımları yeniden üretilir. Kütle/AM etkisi
  ihmal edilebilir: kol AM'si yana ≈ L·sin 5° ≈ 15–20 mm (iki kol simetrik → toplam x değişmez), yukarı < 1 mm; devrilme ve tork
  tabloları pratikte aynı (ev pozu göğüs bandı boşluğu 5,91 → 17,93 iyileşir). Fayda bu iş yüküne değmez → önerilmez.
- Not: servo sıfır hatası ±1,4°'ü aşarsa S2 5 komutunda kol tambura değer (5 − 1,4 ≈ 3,6); kalibrasyonda S2 < 5 komutu verilmemeli.

### taslak-170 (soru 3)
- S1 çevresi (sağ omuz yereli, − OY − DY 435) 77 modül parçasından 67'si birebir; farklı 10 parça yalnız tüp (+30, uzak uçta),
  dirsek çatalı (8 mm, −30) ve bilezik bağlantıları. Kaset, tambur, göbek, kol çatalı, omuz bandı aynı yerde aynı şekil → 125'teki
  bütün kaset/kablo ölçümleri taslak için geçerli. Kol (tüp 130 + ×1,25 ön kol + el) ↔ kaset 2.553 poz: en az 1,254 (S2 5), S2 ≥ 9'da
  > 3 mm; ön kol / el / dirsek çatalı kasete hiç 3 mm yaklaşmıyor. Ev pozu 6 çakışması aynı (yukarıda). **Sonuç: aynı koşullarla geçiyor.**
- Taslakta farklı olanlar: uzatma boyu dirsek ≈ 1.541 + 30 + 435 ≈ 2.006, bilek ≈ 2.038, S2 ≈ 1.540 mm (kol-analiz HAT 2,0 / 2,0 /
  1,55 ile tutarlı) → iki kol ≈ 11,2 m (+%10 ≈ 12,3 m; B1 "~8 m" Y2 maliyetinde güncellenmeli). DS3235 (tasarım stall akımı 3 A) U'dan
  geçen S2 hattında; 22 AWG'de S1 stall gerilimi 5,48 V (kol-analiz). K1'i 26 AWG ile çözmek düşümü ~2,5× yapar → önerilmez.
  DS3235 kablosu 300 ± 5 mm (datasheet; bir satıcıda PRO için 320) → yarık payı 10 ± 5 (şart 7).

### Önerilen düzeltmeler (tasarım ajanı uygular; kontrol ajanı modül dosyalarına dokunmadı)
- **K1 (B1, B7):** kabloyu **ince duvarlı PVC düz 22 AWG servo kablosu** olarak belirle (S1-kaset.md, M1, maliyet notundaki "22 AWG
  silikon" yerine); alımdan önce kumpasla tel kalınlığı **≤ 1,5 mm** (tercihen ≤ 1,4) ölç. Silikon şartsa: duvar r +6 (75,2 → 81,2),
  kanal 4,8 → ≥ 5,7, L ≈ 190,5, cep/pim yeniden (görünüm ≈ +6 mm). M7'ye kaset + gerçek kabloyla 10⁴ döngü kuponu.
- **K2 (B2):** tambur bağı yeniden: halkanın altından kayış geçmez. Seçenekler: (a) bağ sektöründe (ψ_g ≈ 146…158) tambur yüzüne
  (r 39 → 43,7 içinde, dudaklar arası) baskılı **kablo kelepçesi** (sırt plakası + 2 × M2 ya da geçme), kanal dışına taşmasın;
  (b) ≤ 0,4 mm mumlu bağlama ipi (lacing). Ölçüt: bağ elemanı ↔ kapak cıvatası / rulman kapağı ≥ 0,3 (S1 −45…135); bağ açısı 0 ± 2°
  (B8: teğet kılavuz).
- **K3 (B3):** flanş iç kenarı dış köşesine 1,2 × 1,2 pah (S2 120 → +0,39) **ve** yasak kutu: S1 ≥ 120 iken S2 ≤ 117 (→ 0,89);
  ya da S2 lopu bağ açısını ayarla. `eklem_sinirlari.json` yasak kutusuna (B11 ile birlikte: kol koşulu yana [5, 15]).
- **K4 (B4):** U cebi payı u_pay 4,5 → 6,5 (hedef U ucu payı ≥ L +3 mm / S1 +4°; pim otomatik kayar, yeniden ölçülmeli) + kaset
  gövdesine duvar bağı yarığı (ψ ≈ 228, kablo bağı) + montaj talimatı L 171,4 (−5…0) ve S1 yazılım sınırı 135 kesin.
- **K5 (B5):** S1-kaset.md ve M6 G4 montaj sırası: gövde **önden radyal** (x ofset 0) → kablo U → kapak **önden radyal, x +3,5…5
  (S1 0…135, S2 ≥ 30; S1 −45'te en çok +3,3)** → −x pim → 2 cıvata (S1 −45, S2 90). Kapak ofseti ≥ 3,3 şart (pim 3,0 + başlık/duvar).
- **K6 (B6):** statik çakışma kontrolleri yazılım ev pozunda (S2 5); S2 0 bilgi. Geometri değişmez.
- Ayrıca (önceki öneriler, geçerli): S2 servo kablosunu göbekte G2 öncesi aynı tip uzatmaya bağla (B10; U'dan 3 aynı şerit geçsin,
  yarık payı sorunu da kalkar); ψ ≈ 300'de gövde ↔ kapak ikinci pim (B9); tambur +x dudağı ayrı pul (baskı izi).

### 3. ajanın değiştirdiği / eklediği dosyalar
`K2-s1-kontrol.md` (bu), yeni betikler `K2-montaj.py`, `K2-taslak.py`, `K2-serit.py`; çıktılar `K2-montaj-{ofset,radyal,erisim,kayis}.json`,
`K2-taslak-{kiyas,ev,kolkaset}.json`, `K2-serit.json`. Modül dosyaları, `arayuz.py`, `montaj/`, `tasarim/cad/`, taslak-170, demo ve
`maliyet.json`'a dokunulmadı; commit yok.
Kaynaklar (kablo/servo): 22 AWG silikon dış çap 1,7 ± 0,1 — https://www.akkuteile.de/en/silicone-cable-22-awg-0-3-mm-200-c-300v-flexible-tinned-by-the-metre_400519_3876 ,
https://pro.maplin.co.uk/products/red-silicone-lead-wire-22awg-60-0-08mm-price-per-metre ; 24 AWG silikon 1,6 —
https://pro.maplin.co.uk/products/red-silicone-lead-wire-24awg-40-0-08mm-price-per-metre ; DS3235 kablo 300 ± 5 —
https://hajim.rochester.edu/me/sites/kelley/me240/DS3235-270_datasheet.pdf (PRO 320: https://rcdrone.top/products/dsservo-25kg-35kg-coreless-servo).
