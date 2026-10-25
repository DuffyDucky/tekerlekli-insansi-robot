# S1 / Ø84 kablo geçişi: A′ döner U-lop kaseti (tasarım ajanı günlüğü)

Orkestratör kararı: bağımsız kontrolün (K-kontrol.md) A′ önerisi uygulanır. Bu dosya ilerledikçe güncellenir;
ajan kesilirse buradan devam edilir.

> **Güncel durum (25 Ekim 2026, Y1b):** ikinci bağımsız kontrol (`K2-s1-kontrol.md`) KOŞULLU GEÇTİ; K1–K6 düzeltmeleri uygulandı →
> en alttaki **"Y1b düzeltmeleri"** bölümü geçerlidir. Aşağıdaki 15 Ekim metninde **kablo tipi ("22 AWG silikon") ve montaj sırası
> ("+x yönünden kaydırılır") ESKİDİR**; ayrıntı günlüğü `S1-duzeltme-gunluk.md`.

## Durum
- [x] 0. Okuma (CLAUDE.md, README, dongu, M1, K-kontrol, K-s1, kablo_yolu, arayuz OMUZ/KOL_KABLO/13, omuz_parcalar, kabuk_parcalar)
- [x] 1. A′ geometrisi (tambur omuz, kaset gövdesi + kapağı kabuk, ped ısıl gömmeleri + yarık; arayuz KOL_KABLO['s1'])
- [x] 2. Kablo: S1 U lopu kablo_yolu modeline, dirsek_montaj kalıcı kontrolüne; uzatma kablosu boyları
- [x] 3. S2 alt sınırı 5° + "yana 0" kalıntıları (arayuz, eklem_sinirlari.json, omuz_gorsel/goster, carpisma JEST ev, gui metni, yorumlar)
- [x] 4. M4 açıkları: PETG-CF etiket + doluluk kütlesi, tork payları
- [x] 5. Modülleri yeniden üret + kontroller + omuz_baski (+ omuz/dirsek raporu)

## Günlük
- 2026-10-15: dosya açıldı.
- Kesintiden sonra (limit yenilendi): `git diff` HEAD a158211 → omuz/, kabuk/, dirsek/, kod/ortak/ temiz (yarım düzenleme yok).
  arayuz.py farkı yalnız TABAN bölümünde (3. adım ajanı), OMUZ / KOL_KABLO / 13 değişmemiş.

### Bulgu 1: yuvarlanan U'nun gerçek bükülme yarıçapı yarım daireden ~%19 küçük
- K-kontrol'deki R = (r_o − r_i − 4,2)/2 yarım daire tahmini. Gerçek U'da kablo tambur ve duvardan ayrıldığı noktada eğrilik
  sürekli olmak zorunda (pürüzsüz temasta noktasal moment yok): içte +1/r_i'den ters işarete döner, dışta 1/r_o ile birleşir.
  Serbest parça sabit iç kuvvetli elastika. Atış yöntemiyle çözüldü (RK4 600 adım + fsolve; uçlar: iç daire teğet, κ = +1/r_i;
  dış daire teğet ters yön, κ = −1/r_o; geçerlilik r_i ≤ r ≤ r_o). Betik: scratchpad `u_atis2.py` (kablo_yolu'na taşınacak).
- Sonuç (r = demet merkez çizgisi yarıçapları, h = r_o − r_i):

  | r_i | h | R_min (elastika) | yarım daire h/2 | oran |
  |---|---|---|---|---|
  | 41,1 | 24,8 | **10,12** | 12,40 | 0,816 |
  | 41,1 | 27 | 10,98 | 13,5 | 0,813 |
  | 41,1 | 29 | 11,76 | 14,5 | 0,811 |
  | 41,1 | 31 | 12,53 | 15,5 | 0,808 |
  | 41,1 | 33 | 13,29 | 16,5 | 0,806 |
  | 44,1 | 29 | 11,79 | 14,5 | 0,813 |
  | 44,1 | 31 | 12,57 | 15,5 | 0,811 |
  | 44,1 | 33 | 13,34 | 16,5 | 0,809 |
- Yani A′'nin önerdiği r 39 / r 68 (h 24,8) gerçekte **R 10,1 < 11,9**: sınırın altında. R ≥ 12,4 için h ≥ 30,6, R 13,4 için
  h ≈ 33,3 gerekir. 10×d sınırı (3 şerit: 14 + 1,4 = 15,4) için h ≈ 38. U şekli pozdan bağımsız (yuvarlanmada yalnız döner),
  bağ açısı / boy yalnız U'nun konumunu değiştirir (koşu boyları sıfıra inmedikçe).

### Bulgu 2: U'nun açısal kapsamı ve kolun göbek çerçevesindeki yeri (ölçüm)
- U (r_i 41,1 / r_o 73,1, h 32): R_min **12,91**, serbest boy 68,5 mm, dış temas noktası iç ayrılmadan +13,1°, U'nun en uç noktası
  **+34,1°** ileride (r 57). Yani U yalnız iki koşu arasında değil, kendi önüne ~34° taşar; duvar/flanş bunu da kapsamalı.
- Duyarlılık: eksen kaçıklığı ±1 mm (h 31/33) → R 12,53 / 13,29; şerit kalınlığı 1,8 (demet 5,4) → R 12,46 (ama sınır 15,3 olur);
  K önerisi r 68 → 10,12, r 70 → 10,90.
- `S1-kol-sektor.py` (yalnız okur): göbek çerçevesinde (ψ = atan2(−z, y); +Y 0°, arka 90°, alt 180°, ön 270°) kol + üst kol x < 165
  bölgesine yalnız ψ 155,2…201,5°'de girer (S2 5°; r 36–62, x min 160,07). S2 10°'de 164,5…192 (x ≥ 163,3), S2 ≥ 20°'de hiç girmez.

### Tasarım kararları (uygulanıyor)
- **Yerleşim ön-alt → ön-üst (K'nin arka-üst önerisi yerine).** Neden: kablo G2'ye (göbek arka yüzü, ψ_g 114,7°) aşağı (+ψ) inerek
  geliyor (S2 lopu doğrulanmış, değiştirilmedi). +ψ yönünde gelen kablo tambura +ψ yönünde sarılır; U, tambur bağının +ψ önünde kalır.
  S1 −45…135'te bağ (ψ_g 145) sabit çerçevede 100…280°'yi gezer → U ön tarafta 225…290° (iç ayrılma), tepe 324°'ye kadar.
  Arka-üst yerleşim kabloyu G2'de ters çevirmeyi (ikinci bir U) ya da S2 lopunun yeniden tasarımını gerektirirdi.
- **Ölçüler:** tambur r 37–39 (cıvata başına 0,7), iki yanda dudak r 39→43,7 (iç koşu tamburla birlikte döner, dudaklar sürtünmez;
  eksenel kanal 153,5…158,3 = 4,2 + 0,6), sabit duvar r 75,2–77,2 (h 32 → R 12,91; K'nin r 68–70'i sınırın altında kalıyordu),
  flanş r ≥ 44,2, x 158,3–159,5. Kol (S2 5°) x ≥ 160,07 → tambur/dudak 0,77, flanş ≥ 1,09 mm.
- **Sahiplik:** tambur omuz (Gobek grubu, göbek ön yüzüne 3 kol + 3× M3×8 + göbekte 3 ısıl gömme). Kaset gövdesi (duvar + flanş +
  arka dolgu + 2 dikme + üst kulak) **kabuk modülü**: kabuğa vidalanıyor, arka dolgusu kabuk dış zarfına göre kesiliyor, kabuktaki
  ısıl gömme/boss/yarık kabuk kurallarıyla aynı yerde kontrol ediliyor; sağ/sol kabukta zaten ayrı kuruluyor.
- **Bağlantı:** kabuk omuz pedinde 2 dikme (ψ 200° ve 226°, r 53–54; M3×8 havşalı baş flanşta gömülü) + kabuk üst kapağına yatay
  kulak (M3×8 ISO 7380, dikey). Çıkış: bağ ψ_w 228° → duvar boyunca → ψ 214°'de radyal içeri → r 52'de pedde 12 × 6 yarık (JR erkek
  10,3 × 4 geçer) → gövde içi.
- **Montaj sırası (ESKİ, 15 Ekim; uygulanamaz → Y1b K5):** kabuk omuz bandı (Ø84 kapak kulaklarını geçer) → göbek + tambur (tezgâhta: 3× M3×8 −x yüzden; tambur göbekle
  birlikte rulmana takılır) → göbek-horn cıvataları → kablo: G2'den tambura (bağ ψ_g 145, kablo bağı), U elle → kaset gövdesi +x
  yönünden kaydırılır (göbek bu sektörde r ≤ 47'yi aşmaz; S1'i −45'e alınca kol arkada) → 2 dikme cıvatası +x'ten, üst kulak cıvatası
  yukarıdan. Tamburu sökmek için göbek sökülür.

### İlerleme kaydı
- arayuz: OMUZ yana (3→5), `baski_rho` (PETG-CF 1,27×0,9, PETG 1,27×0,8); KOL_KABLO["s1"] tam tanım; bölüm 13 metinleri (yasak kutu
  kol koşulu yana 5…5: ölçülen 0 ± 5 kırpılınca tek nokta; C7'de bakılacak).
- `kod/ortak/eklem_sinirlari.json` üreticiyle yeniden yazıldı: yalnız r_s2/l_s2 min 3→5, neden metni, yasak kutu yana 3→5.
- Kalıntılar: `omuz_gorsel.py` ve `omuz_goster.py` dizileri Y0 = arayuz alt sınırı ile; `carpisma.py` JEST "ev" (0, YANA_MIN, 0, 0);
  `montaj_gui_kontrol.py` "sinir 5"; `montaj_gorsel.py` / `eklem_dogrulama.py` yorumları (kod zaten arayuz'dan okuyordu).
- omuz_parcalar: yuva, kapak, göbek, çatal malzeme "PETG-CF"; kütle rho × doluluk; göbekte 3× M3 ısıl gömme (x 163, r 33,75, ψ −30/0/30);
  "S1 kablo tamburu" (6,4 g) + 3× M3×8 + 3 ısıl gömme (Gobek grubu). omuz_montaj: statik kontrol artık yazılım ev pozunda (S1 0, S2 5);
  mekanik sıfır S2 0'da tambur ↔ çatal 97,9 / tüp 65,0 mm³ (bilgi, `statik_s2_0`): tambur S2 ≈ 3,8°'de kol için yumuşak dayanak olur
  (flanştan önce: flanşa ≈ 3,5°'de değerdi).
- omuz_montaj sonucu: 66 → 73 parça, geçersiz 0, çoklu katı 0, statik (S2 5) 0, göbek × gövde (S1 −60…180) 0, aralık içi (S1 −45…135,
  S2 5…120) serbest olmayan poz 0. Kütle Gövde 595,2 → 625,7, Göbek 147,2 → 176,8, Kol 105,8 → 146,9 g. Omuz kendi tork tablosu (alt kol
  260 g tahmini) S1 5,59 → 5,77, S2 5,72 → 5,93 kg·cm.
- omuz_baski (tambur dahil, 275 s): tambur +X (−x dudak tablada) en iyi yön ama **desteksiz değil**: +x dudak (r 39→43,7) 4,7 mm
  dışa konsol + kolların içe konsolu. Kollar 45° pahlı dikmeye çevrildi (pah x 155,5'te r 36,8'den başlar, kapak M3 başına 0,5 eksenel),
  vida başı pah içindeki Ø6 havşada (oturma x 160,5; M3×8 göbek ısıl gömmesine 5,5 kavrar). +x dudak kablo girişi için şart (sabit
  flanşın iç kenarı r 44,2'de kalmalı, yoksa geçiş kablosu flanşa sürterdi): altında halka destek kalır (kanal dışarıdan açık, sökülür).
  Diğer 5 omuz parçasının sonucu değişmedi (yuva/göbek/çatal destekli, kapak/tüp desteksiz).
- Kaset gövdesi iki parçaya ayrıldı (tek parça U kanal hiçbir yönde desteksiz basılamıyor; arka plaka gerekli çünkü kabuk x 152 düz
  yüzü yalnız y ≤ 30, z −62…59 bölgesinde var, duvar r 77 bunun dışına taşıyor): **govde** = arka plaka x 152–153 + duvar (taban
  çizgisinin 2 mm iç şeridi) + 2 dikme (x 153–155) + üst uç pim yuvası; **kapak** = flanş x 158,3–159,5 + dikme başlıkları (x 155–159,5,
  Ø6 havşa, DIN 912 başı 156,5–159,5 gömülü) + üst uç Ø3 pimi (ψ 331,3°, r 57). Alt uç ψ0 194 → 190 (dikme başlığı alt uç duvarına
  biniyordu, 3,8 mm³). Kabuk üst kapağına kulak düşünüldü, bırakıldı (kulak hiçbir baskı yönünde desteksiz olmuyor); üst uç kabuğa
  bağlı değil, kutu kesit + pim.
- Kanal x: arka plaka yüzü 153 → demet 153,8–158,0 (merkez 155,9) → flanş 158,3: eksenel pay arka 0,8 / flanş 0,3; tambur dudakları
  arası 153,5–158,3 (her yanda 0,3).

- Tambur C halkaya çevrildi (ψ_g 142…395°): tam halka S2 lopuna S2 120°'de giriyordu (boşluk −2,52) ve geçiş yolu bağdan önce
  halkaya değiyordu (−1,07). Arka-üst ψ_g 35…142° boş; +x dudak çentiği gereksiz kaldı. Tambur 6,4 → 4,8 g.
- Çıkış yolunun dönüş köşesi duvardan 0,5 içeri alındı (köşe tam temasta −0,00 veriyordu); duvar bağının ilk 4 mm'si diğer loplardaki
  gibi bağlama noktası sayıldı.

## Sonuç (15 Ekim 2026)
| Modül | Parça önce → sonra | Kütle önce → sonra | Kontroller |
|---|---|---|---|
| omuz | 66 → 73 | Gövde 595,2 → 625,7; Göbek 147,2 → 175,2; Kol 105,8 → 146,9 g | geçersiz 0, çoklu katı 0, statik (S1 0 / S2 5) 0, göbek × gövde (S1 −60…180) 0, aralık içi (S1 −45…135, S2 5…120) çakışan poz 0, M6 4/4 |
| kabuk | 194 → 206 (baskı 15 → 19) | 4.886,3 → 4.921,5 g | geçersiz 0, kabuk içi 0 (513 çift), iskelet 0, braket 10/10, bindirme 51/51, ekran 4/4, **kaset cıvatası 4/4** (kavrama 3,5), bindirme boşluğu 0,1881, baskı 19/19 destek sorunu 0 |
| dirsek | 53 → 53 | 367,4 g (aynı) | geçersiz 0, ev pozu 0, bağlantı 22/22, baskı 4/4, **kablo OK** (S1 dahil) |

- **S1 U lopu:** L 171,4 (bağdan bağa), R_min **12,91** (sınır 7,5 d = 11,90 ✔; 10 d = 15,40 ✘), koşu açısı en az 10,1° (φ 135 iç / φ −45 dış),
  en dar boşluk **0,93** (omuz bandı ped deliği kenarı, φ −45; tambur ve kaset tasarım gereği temas yüzeyi, dışarıda). Eksenel kanal payı
  arka 0,8 / flanş 0,3 / tambur dudakları 0,3. Duyarlılık: eksen kaçıklığı ±1 → 12,53 / 13,29; şerit 1,8 → 12,46 (sınırı 15,3 olur ✘).
- **Geçiş G2 → tambur bağı:** 23,9 mm, köşe R 8,2 (≥ 7,0), boşluk 2,18 (göbek); burulma 90° ~24 mm'de (varsayım).
- **Çıkış duvar bağı → ped yarığı → gövde içi:** 238,0 mm, köşe R 8,0, boşluk 0,30 (kapak); yarık 12 × 6 JR erkek (10,3 × 4) geçer.
- **S2 lopu (S2 5…120):** R 12,4, boşluk 1,57 → **1,90** (S2 alt sınırı 5).
- **Hafif çakışma (modül içi):** tambur ↔ kol (S2 5…120) en az 0,82 (kol çatalı, S2 5); kaset ↔ kol zinciri (S1 −45…135 / 15°, S2 5…120,
  dirsek 0/52,5/105) en az 1,25 (üst kol tüpü, φ 15, S2 5); tambur ↔ kaset/kabuk/omuz gövdesi (S1 tüm aralık) 0,50 (tasarım boşluğu).
- **Uzatma kablosu (servo başına, sağ kol; sol aynı, dağıtım kartı B):** dirsek ve bilek **≈ 1.541 mm** (birleşim → G2 175,7 + geçiş 23,9 +
  S1 171,4 + çıkış/gövde içi 238,0 + dikey → dağıtım A 901,5 + konnektör payı 30). S2 servosu (DS3218, 300 mm kablo) yarığın 10 mm
  ötesine ulaşır (şart ≥ 7: dişi JR ped iç yüzünü geçer; G2'ye 40 mm tahmini) → kabuk içinde birleşir, uzatma **≈ 1.105 mm**.
  Kol başına ≈ 4,19 m, iki kol ≈ **8,4 m** (maliyete girecek: B1 "servo uzatma ~8 m" ile uyumlu; [ESKİ: 22 AWG silikon → Y1b K1: ince duvarlı PVC düz 22 AWG], uca JR sıkma,
  JR erkek/dişi 6+6 çift; S1 kasetinde kablo bağı 2/kol, kaset cıvatası M3×8 2/kol, tambur M3×8 3/kol, ısıl gömme M3 5/kol).
- **Tork (dirsek_montaj, gerçek parça kütleleri + 0,5 kg el yükü; DS3218 20 kg·cm):** S1 yüksüz 7,98 → 8,14 kg·cm (pay 2,51 → 2,46),
  yüklü 24,24 → 24,35 (0,83 → 0,82); S2 yüksüz 8,11 → 8,32 (2,47 → 2,40), yüklü 24,39 → 24,60 (0,82 → 0,81); 2× pay için izinli el yükü
  S1 62 → 58 g, S2 58 → 52 g. Dirsek/bilek değişmedi. (Omuzun kendi tablosu, alt kol 260 g tahmini: S1 5,59 → 5,77, S2 5,72 → 5,93.)
- **Baskı:** tambur +X (−x dudak tablada) destekli: +x dudak altında halka destek 769 mm² (köprü 7,0, konsol 4,2; kanal dışarıdan
  açık), 4,8 g. Kaset gövdesi (arka yüz tablada) ve kapağı (flanş tablada) desteksiz, 108,8 × 108,6 × 6,3 / 4,5 mm, 8,5 / 6,6 g.
- **Görünüm (`S1-gorunum.py` → `S1-gorunum.json`):** kaset omuz bandının üst yüzünden **26,4 mm** yukarı çıkar (ön-üst köşede, ψ ≈ 300–331°),
  yan yüzden 7,5 mm dışarı (x 159,5), önde r 77,2 omzun ön yüzünü (z ≈ 75,3) ~2 mm geçer. K'nin arka-üst önerisinin ~40 mm'sinden az.

## Açık sorunlar
1. 10 × d (15,4) sağlanmıyor (12,91); kablo kalınlığı ölçülmedi: 1,8 çıkarsa 7,5 d sınırı da (15,3) aşılır. Kablo ölçülene dek
   silikon, ince (≤ 1,4 mm) yassı kablo şart; alternatif: h'yi büyütmek (r_duvar +3 → R ~14) = görünüm +3 mm.
2. Kol S2 ≈ 3,8°'nin altında tambura (göbekle birlikte döner) dayanır, ≈ 3,5°'de sabit flanşa: S2 servosu güçsüzken kol asılı durursa
   tambur dudağı yumuşak dayanak olur; S1 elle çevrilirse sürtünme yok (aynı gövde). Servo sıfır hatası ≤ ±2° olmalı (5° alt sınır).
3. Kaset üst ucu kabuğa bağlı değil (kabuk üstünde vidalanacak düz yüzey yok; üst kapağa kulak hiçbir yönde desteksiz basılmıyor):
   2 dikme + kutu kesit + üst uç pimi. Darbeye karşı zayıf olabilir; M7 kuponunda bakılmalı.
4. Tambur baskısı destekli (+x dudak); alternatif dudak ayrı pul (yapıştırma).
5. S2 servo kablosu sınırda (yarıktan 10 mm, şart 7); G2'ye 40 mm tahmini. Yetmezse göbekte kısa uzatma.
6. Yasak kutu kol koşulu yana 5…5 (tek nokta) oldu; C7'de yeniden bakılmalı. Rapor metinlerinde "yana 0…120" (dirsek/kabuk/iskelet/
   kafa/taban/montaj raporları) belge adımında. Tam tarama (carpisma, kaset kabukta olduğu için otomatik girer) ve ana montaj 6. adımda.
7. Kablonun yerçekimi, şeritler arası kayma (U'larda ±2 mm açılma) modelde yok; montaj talimatına lop boyu (L 171,4) ve bağ yerleri girmeli.

## Y1b düzeltmeleri (25 Ekim 2026; `K2-s1-kontrol.md` K1–K6, günlük `S1-duzeltme-gunluk.md`)
Ana tasarım 1,70 m (`taslak-170/`, modülleri import eder): değişiklikler modüllerde, taslak yeniden üretildi.

| # | Ne yapıldı | Ölçülen |
|---|---|---|
| K1 | **Kablo spesifikasyonu: ince duvarlı PVC düz 22 AWG servo kablosu, tek tel (damar) ≤ 1,5 mm (tercihen ≤ 1,4), ALMADAN ÖNCE kumpasla ölçülür.** Kaset ölçüsü aynı. `arayuz.KOL_KABLO["serit"]` notu. Silikon yalnız not: gerekirse duvar r +6 (81,2), kanal ≥ 5,7, L ≈ 190,5, cep/pim yeniden (görünüm ≈ +6). 26 AWG önerilmez (gerilim düşümü). | d 1,4: R 12,91 ≥ 11,90; d 1,5: R 12,80 ≥ 12,75, eksenel 4,5 ≤ 4,8 (K2-serit) |
| K2 | Tamburdaki kayış yarıkları kaldırıldı → **Ø0,4 mumlu polyester bağlama ipi** yolu (ψ_g 148 / 156): halka iç yüzünde 0,5 oluk, iki dudak iç yüzünde 0,3 cep, halkadan radyal kanal; ilmek halka zarfının içinde. İp omuzda parça olarak modelli (`S1 tambur baglama ipi` ×2, Gobek). Baskılı kelepçe sığmadı (kanal 4,8 / demet 4,2; dudak ↔ flanş 0,5 radyal; ankraj yeri yok). | ip ↔ kapak cıvatası **0,809**, ↔ rulman kapağı 1,20, ↔ kaset kapağı 0,60 (S1 −60…180 / 1°) ≥ 0,3 ✔; ip ↔ tambur ortak 0; tambur ↔ sabit 0,50 (değişmedi) |
| K3 | Kapak flanşı iç kenarının dış (x 159,5) köşesine **1,2 × 1,2 pah** (iç yüz r 44,2 korunur) + yazılım bağımlı sınırı **S1 ≥ 120° iken S2 ≤ 117°** (`KOL_KABLO.s1.s2_s1_kosul` → `kod/ortak/eklem_sinirlari.json` `bagimli`, r ve l, gerekçeli). | S2 lopu ↔ flanş: S2 120 **+0,39** (önce −0,30); S2 117 **0,89**; S1 120 / S2 120 0,66 → izinli bölgede en az ≈ 0,66 |
| K4 | `u_pay` 4,5 → **6,5**; kaset duvarına **duvar bağı ip delikleri** (ψ 226,5 / 230: arka plaka dibinde 0,8 × 1,2 radyal yarık + duvar üst kenarında 0,8 × 1,2 çentik; kayışlı bağ 0,8 / 0,3 eksenel aralığa sığmaz); montaj talimatı **L 171,4 mm (−5…0)**, S1 yazılım üst sınırı 135 kesin (`KOL_KABLO.s1.L_tol`). | U ucu ↔ cep temas eşiği **L +2,7 mm / S1 +3,8°** (önce +0,7 / +1). Kontrolün hedefi (+3 / +4°) için u_pay ≈ 7,0 gerekirdi (açık) |
| K5 | Montaj sırası önden radyal (aşağıda, M6 G4 satırı da). | gövde x 0: S1 −45 / −20 / 0 × S2 90 ve S1 −45 × S2 5 → çakışma 0; kapak x +3,3: dört pozda 0; +3,6'da S1 −45 / −20'de göbek (önceki gibi) |
| K6 | Statik / ev pozu çakışma kontrolü yazılım ev pozunda (S1 0, S2 5), S2 0 bilgi satırı: `carpisma.py` statik (+ `carpisma_kos` birleştirme), `taslak_montaj.py`, `taslak_analiz.py` statik. Eklem sıfırı değişmedi. | carpisma statik: S2 5'te 0 (S2 0 bilgi 2); taslak_montaj: S2 5'te 0 (S2 0 bilgi 4); omuz_montaj S2 5'te 0 |
| B9 | **İkinci pim:** U'nun süpürdüğü halkaya konamaz → duvar dışı kulak ψ 300, r 80 (gövde: dikme + köprü; kapak: flanş uzantısı + Ø3 pim −x, 3 mm). | delik iç kenarı r 78,4 > duvar dış 77,2 (kanala 3,2); kabuk içi çakışma 0; kapak baskısı desteksiz |
| B10 | **S2 servo kablosu göbekte uzatmaya eklenir** (G2'den ~20 mm önce, göbeğin arka iç şeridinde; lehim + ısıyla daralan makaron Ø ≤ 4,5 ya da JR çifti; servo kablosu kısaltılır). U'dan 3 aynı PVC şerit geçer; DS3235'in 300 ± 5 mm kablosunun yarık payı sorunu (en kötü 5 < 7) kalkar. | tahmini; montajda yerinde ölçülür |

### Montaj sırası (K5)
1. Bant → göbek + tambur (tezgâhta 3 × M3×8; **bağlama ipleri tambura önceden geçirilir**, uçlar dudak ceplerinden ~80 mm dışarıda) → göbek-horn.
2. S2 servosu; **S2 servo kablosu göbekte uzatmaya eklenir**; kol çatalı, tüp.
3. Kablo G2 → tambur bağı (ψ_g 145): 3 şerit kanala teğet (bağ açısı 0 ± 2°), iki ip demetin üstünde düğümlenir (cerrah + kare düğüm, uç 3 mm).
4. **Kaset gövdesi önden radyal, x ofsetsiz** (arka plaka omuz pedine yaslı kayar; S1 −45 / −20 / 0 ve S2 90, ya da S1 −45 / S2 5).
5. U elle kanala, dış koşu duvar boyunca, ψ 214'te radyal içeri → yarık. **L 171,4 mm (−5…0)** tambur bağından duvar bağına (kabloda işaret).
6. **Duvar bağı:** iki ip (ψ 226,5 / 230) duvar deliklerinden, düğüm duvarın dışında.
7. **Kapak önden radyal, flanş gövdeden x +3,3…5 mm havada** (S1 0…135°, S2 ≥ 30°; S1 −45°'de en çok +3,3); sonra **−x itilir**: iki Ø3 pim (uç ψ 331 + kulak ψ 300) yuvasına.
8. 2 dikme cıvatası M3×8: **S1 −45° / S2 90°**'de anahtar erişimi ≥ 8 mm. (+x yönünden kaydırma olmaz: gövde/kapak göbeğe ve tüpe çarpar.)

### Uzatma kablosu boyu (B10 sonrası; `maliyet.json`'a dokunulmadı, Y2'de maliyete girecek)
| | dirsek | bilek | S2 | kol başına | iki kol | +%10 |
|---|---|---|---|---|---|---|
| 125 cm | 1.541 | 1.541 | **1.385** (göbek eki → G2 20 + 1.335,3 + konnektör 30) | 4.467 | 8,93 m | 9,8 m |
| **1,70 m taslak** | ≈ 2.006 | ≈ 2.038 | **≈ 1.820** | ≈ 5.864 | **≈ 11,7 m** | **≈ 12,9 m** |
| (taslak, eski düzen: S2 servo kablosu U'dan) | 2.006 | 2.038 | 1.540 | 5.584 | 11,2 m | 12,3 m |

DS3235 kendi kablosu (300 mm) için çözüm: göbekte ek (yukarıda, önerilen). Alternatif (önerilmez): servo kablosu U'dan geçer, yarıkta kısa uzatma —
eş JR yarıkta kalır (pay 5 < 7) ve U'da karışık sertlikli şerit kalır. `dirsek_montaj` S2 boy hesabı hâlâ eski düzende (dirsek modülü; Y2).

### Yeniden üretilenler
omuz (75 parça: 73 + 2 ip; statik S2 5 0, aralık içi çakışan poz 0), omuz_baski (tambur +X destekli 769 mm², değişmedi), kabuk (206; tüm
kontroller geçti, kaset baskısı desteksiz, kütle 4.922,3 g), dirsek (kablo kontrolü OK), taslak-170 (1.064 parça, 24.511,3 g; ev pozu S2 5'te 0).
Kısa kontrol: `S1-duzeltme-kontrol.py` → `S1-duzeltme-kontrol.json`.

### Açık (Y1b sonrası)
- U cebi payı L +2,7 / S1 +3,8° (hedef +3 / +4° için u_pay 7,0).
- Gövde kulağı ↔ kapak 0,38 mm³ modelleme bindirmesi (x 158,3'te 0,01 mm; eşik 0,5 altında), sonraki üretimde 0'a çekilebilir.
- B11 (yasak kutu kol koşulu yana [5, 15]) uygulanmadı (kafa-kol kutusu, C7/Y4).
- `dirsek_montaj` uzatma boyu S2'yi eski düzende hesaplıyor; ana montaj, `carpisma` diğer bölümleri, görseller ve rapor.html'ler bayat (Y4).
- Bağlama ipi düğümü (≈ 1–1,5 mm) modelde yok; kanal ortasında, flanş / arka plakadan uzak (eksenel ≥ 1). M7'ye kaset + gerçek kablo 10⁴ döngü kuponu önerisi duruyor.

