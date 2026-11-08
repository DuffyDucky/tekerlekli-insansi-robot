# Karar kuyruğu (Lale 1,58 m) — açıldı 08.11.2026

Kural (`planlama/dongu-158.md:34-35, §2 "Karar gereken yerde durma"`): Ahmet'in kararını isteyen madde buraya yazılır; döngü varsayılanla **ilerlemez**, o maddeye
bağlı olmayan işe geçer. "Önerilen varsayılan" yalnız öneridir. Kapanmış maddeler kaynağıyla birlikte "kapandı" gösterilir.

Kaynaklar: `dongu-158.md` bölüm 4 (K1–K9), `tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md` (sorular, satır 143–147),
`tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md` (karar gereken noktalar, satır 146–155),
`tasarim/freecad/lale158/kafa-yerlesim/secenekler.md` (sorular, satır 332–341), `planlama/y3/Y3-kontrol.md`,
`planlama/kararlar-2026-10-29.md`, `planlama/adim3/elektrik.md` (çalışma kopyası), P0.1 sınıflandırması.
Sayıların hepsi dosyadan okundu; yanında dosya:satır ya da JSON anahtar yolu var. Kısaltma: `KY/` = `tasarim/freecad/lale158/kafa-yerlesim/`.

## Özet

| # | Karar | Durum | Önerilen varsayılan | Bloke ettiği |
|---|---|---|---|---|
| K1 | Altıncı USB cihazı | **açık** (Efe'de, pano #5) | 5 cihaz + 2 boş hub portu | P4.1, P8.1 |
| K2 | AI HAT+ × arka üst boss: boss taşı / HAT yönü | **açık** | Boss taşı | P1.3 seçimi, P6.1 |
| K3 | Düz zeminde elde yük sınırı | **açık** (P3.1 tablosu eklendi, F3a) | b: her elde ≤ 100 g, yalnız düz zeminde; rampada yüksüz | P3.1 sonucu, P3.2, P9.3 |
| K4 | Listede olmayan 6 kablo kalemi | **açık** | Koşullu kalem, fiyatsız | P4.2, P8.1 |
| K5 | Hub ve ses kartı arka kabuk yan duvarında, servis | kapandı (B + R1) | — | — |
| K6 | Hoparlör duvara paralel / yatay eksene kama | **açık** | Paralel, ölçümden sonra yeniden | P1.7, P8.3 |
| K7 | Dizi kabuğun altında: "kafanın üstü" ifadesi kabul mü | **açık** (yalnız ifade; yer kapandı) | Kabul | P9.3 |
| K8 | H1 sigorta erişimi | kapandı (29.10, seçenek a) | — | — |
| K9 | El yükü 0,5 kg: servo değişimi mi 100 g sınırı mı | **açık** (1,58 m'de yeniden hesaplandı, F3a) | a: her elde ≤ 100 g | P3.2, P5.1, P8.1 |
| K10 | PAM8403 5 V besleme noktası | **açık** | D24V50F5 (Pi hattı) | P1.2, P4.1, P8.3 |
| K11 | Göğüs ekranı 12 V dalının girişi (acil stopta ekran) | **açık** | Ana anahtar sonrası, röle öncesi | P4.1, P4.2, P7.2 |
| K12 | Kafa havalandırması: yarık / 30 mm fan | **açık** | Yarıklar kalsın, fan yeri ayrılı | P8.1, P8.3 |
| K13 | ReSpeaker LED'leri görünmese olur mu | **açık** | Görünmesin | P4.3 (yalnız "görünsün" seçilirse) |
| K14 | Boyun demeti (Efe teyidi) | **açık** (dış teyit) | CAD'deki gibi | P5.2, P5.3, P4.1 |
| K15 | Omuz bölümü taraması koşulsun mu | kapandı (08.11 onayı) | — | — |
| K16 | MAX98357A mı PAM8403 + USB ses kartı mı | kapandı (04.11) | — | — |
| K17 | Yerleşim A/B/C, dizi R1/R2, ReSpeaker kafada mı | kapandı (05.11, B + R1) | — | — |
| K18 | `tubitak-2209b/` depoya girsin mi | **açık** | Dışla (`.gitignore`) | P0.1 (git status temiz) |
| K19 | `kvkk/` depoya girsin mi | **açık** | Dışla | P0.1 |
| K20 | `rapor/` (tek sayfa rapor) depoya girsin mi | **açık** | Dışla | P0.1 |
| K21 | `KY/kaynak/` satıcı dosyaları | **açık** | Dışla, adres `.gitignore`'da | P0.1, P6.1 (temiz klonda) |
| K22 | `tasarim/solidworks/` ve hareket makrosu | **açık** | Betik + makro commit, STEP'ler dışla | P0.1 |
| K23 | 03.11 ara çıktıları (Y2b-ivme, yerleşim kontrolü, kabuk görselleri) | **açık** | "Ara çıktı" diye commit | P0.1 |
| K24 | G4 öncesi 11,6" raporundaki iki satır (yerel hafıza yolu + takma ad) | **açık** | G4'ten önce temizle | G4 commit'i, P0.1 |

**Açık: 19** (biri, K14, Ahmet'in değil Efe'nin teyidi). **Kapandı: 5** (K5, K8, K15, K16, K17). Toplam 24 madde.

---

## K1 · Altıncı USB cihazı
- **Soru:** `elektrik.md` 6 USB cihaz diyor, adı belli olan 5 (`elektrik.md:58`). Altıncısı ne ve nerede?
- **Seçenekler:**
  a) Cevap gelene kadar 5 cihaz; hub'da 2 port boş (bugünkü model: `KY/uygulama-notu.md:131-132`).
  b) Altıncı cihaz kafada: Pi'de boş port kalmaz, kablo boyundan inip geri çıkar; yerleşim B zayıflar, A öne geçer (`KY/secenekler.md:281`).
  c) Altıncı cihaz gövdede: hub'ın boş portuna girer, hub'da 1 port kalır.
- **Sayısal etki:** A'ya dönülürse boyun yuva kanalı %44,8 → %52,9, tilt payı 3,64 → 3,47, pan payı 2,21 → 2,16 (`KY/secenekler.md:17-19`).
  Tilt payı 3,47 ≥ 3,0 ve pan 2,16 ≥ 2,0 eşikleri yine sağlar (`dongu-158.md:25, §1 korunan değerler`).
- **Varsayılan:** a (`dongu-158.md:136, §4 K1`).
- **Bloke:** P4.1 ("6. cihaz Efe cevabına göre", `dongu-158.md:88, §3 P4.1`), P8.1 sipariş paketi.
- **Durum:** açık. Efe'ye soruldu, pano #5 (`dongu-158.md:136,150, §4 K1 ve §5 günlük`); `KY/secenekler.md:336`, `KY/uygulama-notu.md:151`.

## K2 · AI HAT+ zarfı × arka üst cıvata boss'u
- **Soru:** AI HAT+ 26T gelince zarfı boss'a giriyorsa boss mu taşınır, HAT yönü mü değişir?
- **Seçenekler:** a) boss'u taşı; b) HAT'i çevir (yön değiştir). Her ikisi de P1.3'te çakışma 0 olacak şekilde üretilir (`dongu-158.md:64, §3 P1.3`).
- **Sayısal etki:** bugün çakışma 77,69 mm³ `Arka kafa kabugu sag`, 7,97 mm³ somun, 3,18 mm³ cıvata (`KY/uygulama-notu.md:9`);
  zarf ile dizi arası 24,97 mm (`KY/uygulama-notu.md:64`). Zarf ölçüsü varsayım: 65 × 56,5, yığın 16, 30 g, CAD'de yok (`KY/secenekler.md:275`).
  Hangi seçeneğin pay ve kütleye etkisi olduğu P1.3'ten önce **ölçülmedi**.
- **P1.3 ölçümü (F1a, 08.11.2026):** betik `KY/hat_secenek.py` (bayrak `HAT_SECENEK=0/a/b`; ana model değişmedi, `kafa10_lib.SECENEK`
  varsayılanı bugünkü değer). Sonuçlar `KY/hat-secenek-0.json`, `-a.json`, `-b.json`; görseller `KY/gorsel/HAT-{0,a,b}-{arka,kesit}.png`.
  HAT ölçüsü üretici ürün özetinden: kart 65 × 56,5, delikler 58 × 49, 16 mm yığın başlığı (RP-008133-DS-1, Raspberry Pi Ltd, Ekim 2024,
  "Physical specification"). Kütle 30 g, bileşen zarfı 3,0 mm, yığın başlığının HAT üstünde 8,5 mm'si, FFC halkası 5 × 18 mm **varsayım**
  (üretici belgesinde yok). HAT takılınca Pi'nin 4 üst M2,5×5 vidası çıkar (yerine ayak + HAT vidası).
  - **Seçenek a (boss'u taşı):** arka duvar üst dikiş boss'u baş çerçevesinde (x −8, y 60) → (x −5, y 76): üst yarık bandının yüksekliğinde,
    iki yarık sütununun arasında (yarık kenarına 1 mm). Dikiş cıvatası ve ısıl gömme somun onunla taşınır.
  - **Seçenek b (yığını değiştir):** Pi 5 + AI HAT+ yığını 5 mm öne (baş çerçevesinde z +5; tabla burç delikleri ve tabla üstü kablo yolu
    zarfı da 5 mm öne). HAT'i çevirmek (yön) uygulanabilir değil: HAT Pi'nin GPIO başlığına yığın başlığıyla takılır, kart Pi ile aynı
    yönde durmak zorunda; yığını yükseltmek de çözmez, çünkü yığın başlığı sütunu boss yüksekliğini zaten geçiyor (`KY/hat_secenek.py` başlığı).

  | Ölçüt (kaynak anahtar) | 0: bugünkü model + HAT | a: boss taşı | b: yığın 5 mm önde |
  |---|---|---|---|
  | Kafa içi çakışma, HAT ile (`cakisma_hatli`, > 0,5 mm³) | 8 çift: arka kabuk sağ 28,09 + 13,63 + 66,44 mm³, somun 2,78 / 3,58 / 1,61, cıvata 0,56 / 2,62 | **0** | **0** |
  | Kafa içi çakışma, HAT'sız (`cakisma_hatsiz`) | 0 | 0 | 0 |
  | Eski zarf × parçalar (`eski_zarf_cakisma`) | 77,69 / 7,97 / 3,18 (bugünkü sayı tekrarlandı) | 0 | 0 |
  | HAT – dizi açıklığı (`aciklik.hat_dizi_mm`) | 24,97 mm | 24,97 mm | 24,97 mm |
  | HAT – en yakın parça (`aciklik.hat_en_yakin`) | 0 (çakışıyor) | 3,0 arka kabuk; boss somunu 6,3 | 2,05 arka kabuk sağ (boss); somun 3,55 |
  | HAT arka kenarı – arka duvar iç yüzü / yarık (`hat_arka_kenar_duvar_ic_mm`, `hat_yarik_mm`) | 3,0 / 3,0 mm | 3,0 / 3,0 mm | 8,0 / 8,0 mm |
  | HAT altı – Active Cooler (`hat_alti_sogutucu_mm`) | 1,4 mm | 1,4 mm | 1,4 mm |
  | HAT × "Fan yeri 30×30×10 (listede yok)" zarfı (`hat_fan_yeri_kesisim_mm3`) | 98,2 mm³ | 98,2 mm³ | 19,61 mm³ |
  | Vida erişimi: HAT vidaları yukarı, Ø6 alet (`erisim`) | 36,86 / 29,64 / 36,86 / 36,86 mm | aynı | aynı |
  | Vida erişimi: dizi vidası 1 aşağı, Ø8 alet | 57,77 mm (engel iskelet) | 57,77 mm | 27,55 mm (engel HAT bileşen zarfı) |
  | Vida erişimi: dikiş cıvatası dışarıdan, Ø6 | ≥ 60 mm | ≥ 60 mm | ≥ 60 mm |
  | Kafa grubu kütlesi, HAT ile / HAT'sız (`tork_hatli`, `tork_hatsiz` `.kafa_grubu_g`) | 1.598,9 / 1.570,8 g | 1.598,9 / 1.570,8 g | 1.598,9 / 1.570,8 g |
  | Tilt payı ±15°, HAT ile / HAT'sız (`.pay_tilt15`, kafa_montaj §6 yöntemi) | 3,30 / 3,64 | 3,30 / 3,64 | 3,37 / 3,70 |
  | Pan payı, HAT ile / HAT'sız (`.pan_pay_iki_hane`) | 2,20 / 2,21 | 2,20 / 2,21 | 2,20 / 2,21 |
  | Tilt −15°'de kafa – pan grubu en yakın (`tilt_sinir_en_yakin`) | 3,05 mm | 3,05 mm | 3,05 mm |
  | Baskı: arka kabuk sağ destek sorunu (`baski`, KL.baski_analiz) | 1 (bugün de 1, `kafa-analiz.json`) | 1 | 1 |

  Notlar: (1) Seçenek 0 satırındaki HAT × arka kabuk 108,16 mm³, bu betiğin ayrıntılı HAT takımıyla (kart + bileşen + başlık); 77,69 eski
  kutu zarfla. (2) Fan yeri zarfı HAT ile her seçenekte kesişiyor: K12'de fan seçilirse fan yeri taşınmalı (b'de kesişim küçük). (3) b'de
  kablo yolları 5 mm kaydı, kablo boyu/kütle yeniden hesaplanmadı (**doğrulanmadı**); tork kütlesindeki kablo kalemleri bugünkü yoldan.
  (4) Dizi vidası 0 ve 2 için aşağı erişim üç seçenekte de 0 mm çıkıyor (alet silindiri dizi kartının içinden başlıyor): ölçüm yöntemi sorunu,
  HAT'ten bağımsız, **doğrulanmadı**. (5) İki seçenekte de korunan değerler sağlanıyor (tilt ≥ 3,0, pan ≥ 2,0).
- **Varsayılan:** a, boss taşı (`dongu-158.md:137, §4 K2`).
- **Bloke:** P1.3'ün seçimi (iki çözüm de üretilir, seçim buraya), P6.1 tam model.
- **Durum:** açık (`KY/uygulama-notu.md:149`).

## K3 · Düz zeminde elde yük sınırı
- **Soru:** Robot elinde en çok ne kadar yük taşısın (düz zemin)?
- **Seçenekler:** a) yük yok (yalnız boş el); b) ≤ 100 g her elde; c) ≤ 500 g yalnız düz zeminde, rampada yüksüz.
- **Sayısal etki (güncel model, `KY/uygulama-ivme.json`):**
  - Düz zemin devrilme payı (en kötü yön): 0 g 2,095, 100 g 2,055, 500 g 1,905 (`izgara_yuk_{0,100,500}g.a_sinir_pay15.duz_geri`).
  - Düz zemin fren 1,8 m/s²: 1,746 / 1,713 / 1,587 (`izgara_yuk_*.fren_pay.duz_min`); üçü de ≥ 1,5.
  - Rampa 5°: 1,517 / 1,477 / 1,327 (`izgara_yuk_*.a_sinir_pay15.rampa5_geri`); 100 g ve 500 g eşik 1,5'in altında.
  - Düzde devrilme sınırlamıyor; sınırı servo payı belirliyor (K9).
  - F1b P1.1 (akü 3,0 kg, 08.11.2026) sonrası aynı anahtarlar: düz 2,097 / 2,057 / 1,907; fren 1,748 / 1,714 / 1,589; rampa 5° 1,519 / 1,479 / 1,329
    (K9'daki 500 g rampa 1,327 → 1,329). 100 g ve 500 g rampada yine < 1,5; seçeneklerin sonucu değişmedi.
  - **P3.1 tablosu (F3a, 09.11.2026; `planlama/d158/F3a-yuk.json`, betik `F3a-yuk.py`, FreeCAD'siz, `uygulama_ivme.py` ve `dirsek_montaj.py`
    yöntemi aynen; 0 / 100 / 500 g UI ve DA sayılarını birebir üretti; B kontrolü KOŞULLU, koşullar uygulandı `F3a-kontrol.md`):** yük her iki elde.

    | Elde yük | Düz devrilme | Fren 1,8 | Rampa 5° | S1 | S2 | Dirsek |
    |---|---|---|---|---|---|---|
    | 0 g | 2,097 | 1,748 | 1,519 | 2,78 | 2,72 | 3,88 |
    | 50 g | 2,077 | 1,731 | 1,499 | 2,34 | 2,30 | 2,73 |
    | 100 g | 2,057 | 1,714 | 1,479 | 2,03 | 2,00 | 2,11 |
    | 200 g | 2,017 | 1,681 | 1,440 | 1,59 | 1,58 | 1,45 |
    | 500 g | 1,907 | 1,589 | 1,329 | 0,97 | 0,97 | 0,74 |

    Kaynak anahtarlar: `izgara_yuk_*.a_sinir_pay15.duz_geri`, `.fren_pay.duz_min`, `.a_sinir_pay15.rampa5_geri` (0 / 100 / 500 UI, 50 / 200
    `F3a-yuk.json P3_1.izgara`); servo DA `tork.sonuc` (0 / 500) ve `F3a-yuk.json P3_1.tablo` (50 / 100 / 200). Bilek her yükte ≥ 14.
  - Bağlayan ölçüt servo: pay ≥ 1 için ≤ 342 g (dirsek), pay ≥ 2 için ≤ 99 g (S2). Düz devrilme ≥ 1,5 1.000 g'a kadar, fren ≥ 1,5 810 g'a kadar tutuyor.
  - Rampa ızgara payı 50 g'da 1,499 (< 1,5); kollar ev pozunda 100 g ile 1,601, 500 g ile 1,563.
  - AI HAT+ (K2; 30 g varsayım, Pi'nin 4 üst vidası çıkınca net 28,1 g: HS `kafa_grubu_g` farkı) eklenince yüksüz rampa 1,519 → 1,515, düz 2,097 → 2,093
    (a ve b aynı; 30 g ile de 1,515); sonuç değişmiyor.
  - İvme torkuyla (60° / 0,4 s) S1 payı 100 g'da ≈ 1,1, 200 g'da < 1 (B kaba tahmini, `F3a-kontrol.md`; taslak-170 kol ataleti; doğrulanmadı).
- **Önerilen varsayılan (F3a P3.1 sonrası; öneri, karar Ahmet'in):** b, her elde ≤ 100 g (iki elde toplam ≤ 200 g), yalnız düz zeminde; rampada yüksüz.
  c (500 g) ancak K9 b ile (500 g'da S1 / S2 0,97, dirsek 0,74). Alternatif: rampada kollar ev pozunda zorlanırsa ≤ 100 g (1,601; SO Ç7'ye bağlı:
  `planlama/d158/servo-10-oneri.md` Ç7). Önceki ön öneri: `dongu-158.md:153, §4 K3`.
- **Bloke:** P3.1'in önerisi, P3.2, P9.3 rapor.
- **Durum:** açık (`qled-cerceve-tasarim-notu.md:128`; KZ2 açık: `planlama/y3/Y3-kontrol.md:115`, `planlama/kararlar-2026-10-29.md:23-24`).

## K4 · Listede olmayan 6 kablo kalemi
- **Soru:** USB-A uzatma ~30 cm, USB-A uzatma ~1 m, L USB-A dirsek, kısa micro USB, hoparlör kablosu ~1,1 m, L 3,5 mm fişli kısa kablo
  (`KY/uygulama-notu.md:134`) malzeme listesine girsin mi?
- **Seçenekler:** a) `maliyet.json`'a "koşullu" kalem, fiyat satıcı sayfası doğrulanınca; b) bütçe dışı, ekip karşılar; c) v4 listesine kesin kalem.
- **Sayısal etki:** sipariş boyları 920, 270, 110, 1.030, 40 mm ve dirsek (`KY/uygulama-notu.md:106-112`). TL etkisi **doğrulanmadı** (fiyat yok).
- **Varsayılan:** a (`dongu-158.md:139, §4 K4`).
- **Bloke:** P4.2, P8.1.
- **Durum:** açık (`KY/uygulama-notu.md:150`, `KY/secenekler.md:341`).

## K5 · Hub ve ses kartı arka kabuk yan duvarında, servis için kabul mü — KAPANDI
- **Soru (eski düzen):** `qled-cerceve-tasarim-notu.md:147`.
- **Seçenekler o zaman:** a) arka kabuk yan duvarı (kafa açılmadan erişim yok); b) başka yer (secenekler A/B/C).
- **Sayısal etki:** B'de hub gövde servis kapağının içinde, 7 cıvatalı kapakla erişim, kafa ve QLED açılmıyor (`KY/secenekler.md:304`);
  hub kapak dayamasına 0,25 mm, göğüs bandına 3,17 mm (`KY/uygulama-notu.md:58`).
- **Durum:** kapandı. Ahmet 05.11 B + R1'i seçti (`KY/uygulama-notu.md:3`, `KY/secenekler.md:1`); hub gövdeye, ses kartı ve PAM kafanın sol
  duvarına taşındı, modele işlendi (`d26c7e7`). Soru eski yerleşime aitti. Ses kartı ve PAM kafada sol duvarda kaldı
  (`KY/secenekler.md:12`); servis erişimleri B seçimiyle kabul edilmiş sayılır, ayrı bir onay kaydı yok.

## K6 · Hoparlör ekseni: duvara paralel mi, yatay eksene kama mı
- **Seçenekler:** a) duvara paralel (bugünkü model: eksen yatayın 35° altında, kama yok, `KY/uygulama-notu.md:59`); b) yatay eksene kama.
- **Sayısal etki:** 1,6 m kulak yüksekliğinde 1 m'deki dinleyiciye eksen dışı açı a) 68,1°, b) 33,2° (`KY/secenekler.md:240`).
  b geometrik olarak sığıyor (duvara 0,41 mm, ekrana 23,29 mm) ama kama boşluğu 0,5–28 mm, ayrı akustik hazne sorunu (`KY/secenekler.md:243`).
  Duyulabilirlik **ölçülmedi** (`KY/secenekler.md:253`).
- **Varsayılan:** a, ölçümden sonra yeniden (`dongu-158.md:141, §4 K6`).
- **Bloke:** P1.7 hoparlör kabı tutucu, P8.3 akustik test.
- **Durum:** açık (`KY/secenekler.md:337`). Model a ile kuruldu; bu Ahmet kararı değil.

## K7 · Dizi kabuğun altında: "kafanın üstü" böyle kabul mü
- **Seçenekler:** a) kabul: dizi kabuğun 2,5 mm altında, delikli tavan (`KY/secenekler.md:299`); b) dizi kabuğun üstüne.
- **Sayısal etki:** b en az 13 mm boy aşar (`KY/secenekler.md:286`): boy 1.580,0 → ≥ 1.593 mm, korunan değer "boy 1.580,0" bozulur
  (`dongu-158.md:24, §1 korunan değerler`). Mikrofon-hoparlör a ile 574,3 mm ≥ 400 (`KY/uygulama-olcum.json mic_hoparlor.poz_min_mm`).
- **Varsayılan:** a (`dongu-158.md:142, §4 K7`).
- **Bloke:** P9.3 (rapor dili). 2209-B v14 metni değişmeyecek (`dongu-158.md:39, §2 2209-B kuralı`); soru yalnız ifadenin kabulü.
- **Durum:** yer kapandı (R1, 05.11: `KY/secenekler.md:1`); ifade sorusu açık (`KY/secenekler.md:339`).

## K8 · H1 sigorta erişimi — KAPANDI
- **Seçenekler o zaman:** a) açıklık ±32 kalır, kutu gelince ölçülür, uçtaki iki yuva yedek; b) dolgu şeridi dikişlerini kaydırıp
  açıklığı ±44'e çıkar, kabuk yeniden (`planlama/y3/Y3-kontrol.md:107-108`).
- **Sayısal etki:** 1 × 6 dizilişte uçtaki 2 sigorta kapak altında; 2 × 3'te 6'sı açıkta (`Y3-kontrol.md:41-42`).
- **Durum:** kapandı. "KARAR 29.10: (a)" (`Y3-kontrol.md:109`), commit `f95f96b` ("H1 uç yuvalar yedek").
  Kalan iş karar değil: kutu alınınca ölçüm (P8.3).

## K9 · El yükü 0,5 kg: servo değişimi mi, 100 g sınırı mı
- **Seçenekler:** a) el yükü ≤ 100 g (yazılım ve kullanım kuralı); b) S1/S2 ve dirsek için daha güçlü servo.
- **Sayısal etki:** 0,5 kg'da S1/S2 payı 0,97, dirsek 0,74 (< 1); 2× pay için ~100 g (`planlama/kararlar-2026-10-29.md:24`).
  1,58 m modelinde yeniden hesaplandı (F3a P3.2, 09.11.2026, `F3a-yuk.json P3_2`): 500 g elde S1 0,97, S2 0,97, dirsek 0,74;
  1,65 m sayılarıyla aynı (kol geometrisi ve kütlesi değişmedi, DA 400,5 g). b seçilse de 500 g ile rampa payı 1,329 < 1,5
  (`KY/uygulama-ivme.json izgara_yuk_500g.a_sinir_pay15.rampa5_geri`, F1b P1.1 sonrası): rampada yük yine yasak kalır (yalnız kollar ev pozunda 1,563).
  b'nin maliyeti ve kütle etkisi **hesaplanmadı**.
  - **b'nin servo gereksinimi** (F3a, aynı statik yöntem, el ucunda 500 g): pay ≥ 1 için S1 ≥ 31,2, S2 ≥ 31,5, dirsek ≥ 12,6 kg·cm stall;
    pay ≥ 2 için S1 ≥ 62,4, S2 ≥ 63,0, dirsek ≥ 25,2 kg·cm. Daha ağır dirsek servosu S1 / S2 torkunu da büyütür; bu etki ve maliyet **hesaplanmadı**.
  - Pan / tilt için karar gerekmiyor (F3a P3.2): en düşük K2 a, kod sınırında tilt 3,27 ≥ 3,0, pan 2,16 ≥ 2,0 (pan ekstrapolasyon).
- **Varsayılan:** a (`dongu-158.md:144, §4 K9`). F3a sonrası öneri değişmedi: a (her elde ≤ 100 g; K3 b ile aynı sınır). Öneri; karar Ahmet'in.
- **Bloke:** P3.2, P5.1 (servo modeli sütunu), P8.1.
- **Durum:** açık (`kararlar-2026-10-29.md:23` "AÇIK (karar değil)").

## K10 · PAM8403 5 V besleme noktası
- **Seçenekler:** a) D24V50F5 (Pi hattı); b) SY8205 (kafa ekranı hattı); c) ayrı küçük düşürücü.
- **Sayısal etki:** a) Pi hattı normalde 2,67 A, 5 A'nın %53'ü (`elektrik.md:24`); PAM tepesi 0,71 A ile tepe 3,28–3,38 A, %66–68
  (`KY/uygulama-notu.md:98`). b) ekran hattı 0,9 A **varsayım**, 3,7 A'nın %24'ü (`elektrik.md:25`); PAM eklenince ~1,6 A, ekran
  akımı ölçülmeden belirsiz. c) maliyet ve yer **doğrulanmadı**. Akımların hepsi hesap, ölçülmedi.
- **Varsayılan:** a (model bunu varsayım olarak kullanıyor: `KY/uygulama-notu.md:97`; P1.2 tanımı da a: `dongu-158.md:63, §3 P1.2`).
- **Bloke:** P1.2 (`elektrik.md` metni), P4.1, P8.3 (PAM akımı testi).
- **Durum:** açık (`KY/secenekler.md:338`, `KY/uygulama-notu.md:152`).

## K11 · Göğüs ekranı 12 V dalının girişi
- **Soru:** Dal ana anahtardan sonra mı, röle K1'in anahtarlı barasından mı alınsın? Bu, ekranın acil stopta açık kalıp kalmayacağını
  belirler (`elektrik.md:55` "karar yok").
- **Seçenekler:** a) ana anahtar sonrası, röle öncesi (sigorta kutusundan ayrı 2 A dal): acil stopta ekran açık; b) anahtarlı bara: acil stopta ekran kapanır.
- **Sayısal etki:** dal mini 2 A, ekran ~0,5 A @ 12 V (`elektrik.md:316`, `:19`); F1 20 A anahtarlı bara (`elektrik.md:60`).
  Kafa F3 5 A dalı röleden önce (`elektrik.md:60`): Pi acil stopta açık kalıyor.
- **Varsayılan:** a. Gerekçe: Pi açık kaldığı için ekran acil stop durumunu gösterebilir. Bu bir öneri; güvenlik açısından **doğrulanmadı**.
- **Bloke:** P4.1, P4.2 (kablo boyu), P7.2 (göğüs ekranı montaj adımı, `R-gunluk.md:33-35`).
- **Durum:** açık (`elektrik.md:55`).

## K12 · Kafa havalandırması: mevcut yarıklar mı, 30 mm fan mı
- **Seçenekler:** a) mevcut arka yarıklar, fan yeri ayrılı ama parça yok; b) 30 mm egzoz fanı şimdi.
- **Sayısal etki (el hesabı):** normal 19,8 W'ta kapalı 49,7 °C, yarıklı 48,2 °C, fanlı 36,9–39,1 °C; yükte 22,9 W'ta 52,8 / 50,9 /
  38,0–40,5 °C (`qled-cerceve-tasarim-notu.md:114-117`). Sınır: servo 55 °C, tilt servo gövdesi 50 °C (`qled-cerceve-tasarim-notu.md:119`).
  Yarıklı sonuç yükte 0,9 K aşım veriyor; hesap karşılaştırma içindir.
- **Varsayılan:** a; stres testinde tilt servo gövdesi 50 °C'yi geçerse fan eklenir (`qled-cerceve-tasarim-notu.md:119`).
- **Bloke:** P8.1 (fan kalemi), P8.3 (ısı testi kâğıdı).
- **Durum:** açık; notta "öneri", Ahmet kararı kayıtta yok.

## K13 · ReSpeaker LED'leri görünmese olur mu
- **Seçenekler:** a) görünmesin (bugün 12 LED kabuğun altında); b) ışık borusu ya da saydam parça.
- **Sayısal etki:** 12 LED kabuğun altında kalıyor (`KY/secenekler.md:330`); dizi kabuğun 2,5 mm altında (`KY/secenekler.md:299`);
  ReSpeaker Ø70 (`KY/yerlesim_lib.py:54`). a için değişiklik yok. b için ışık borusu ya da saydam parçanın ölçüsü, kütlesi ve
  baskı etkisi **hesaplanmadı**.
- **Varsayılan:** a.
- **Bloke:** yalnız b seçilirse P4.3 ve P6.1.
- **Durum:** açık (`KY/secenekler.md:340`).

## K14 · Boyun demeti (Efe teyidi)
- **Soru:** Göğüs ekranı HDMI'si ve hub uzatması boyundan iniyor; Efe'nin eski kuralı "HDMI ve CSI boyundan geçmez"di
  (`planlama/yazilim-plani.md:64`, HEAD). Efe bu düzeni kabul ediyor mu?
- **Seçenekler:** a) CAD'deki gibi: boyunda 12 V + tilt + HDMI + hub uzatması + hoparlör (`KY/uygulama-notu.md:99`);
  b) eski kural: göğüs ekranı boyundan sinyal almaz, başka sürücü gerekir (çözüm modellenmedi).
- **Sayısal etki:** a ile boyun yuva kanalı %44,8 (`KY/uygulama-notu.md:26`); HDMI yolu 757 mm, sipariş 950 (`KY/uygulama-notu.md:114`).
  b'nin etkisi **hesaplanmadı**.
- **Varsayılan:** a.
- **Bloke:** P5.2, P5.3 (pano mesajı), P4.1.
- **Durum:** açık, dış teyit (`KY/uygulama-notu.md:154`; `elektrik.md` tablosu "CAD'de böyle, Efe teyidi bekliyor").

## K15 · Omuz bölümü taraması ve omuz regresyonu — KAPANDI
- **Seçenekler o zaman:** a) koş (~4,8 sa, `KY/uygulama-notu.md:148`); b) koşma, sonuç dosyası karışık kalsın (`carpisma-sonuc.json tek_kosu` false).
- **Durum:** kapandı. Ahmet 08.11: "uzun taramalar (omuz, tam model) sırası gelince, saat fark etmeksizin koşar" (`dongu-158.md:43-44, §2 "Açık onaylar"`). P2.2'de koşacak.

## K16 · MAX98357A mı, PAM8403 + USB ses kartı mı — KAPANDI
- **Seçenekler o zaman:** a) MAX98357A (I2S); b) PAM8403 + USB ses kartı (`qled-cerceve-tasarim-notu.md:145`).
- **Durum:** kapandı. Ahmet 04.11: PAM8403 + USB ses kartı (`KY/secenekler.md:8`). Modelde MAX98357A 0 parça
  (`KY/uygulama-notu.md:57`; `kafa10_lib.py:402` "MAX98357A cikti"; `kafa-bom.csv` ve `robot-bom.csv`'de yok). Yalnız eski 7" kod
  (`kafa7_parcalar.py:489`) ve yorum/rapor metinlerinde geçiyor: P1.2'nin model kısmı zaten yapılmış, metin kısmı kalıyor.

## K17 · Yerleşim A/B/C, dizi R1/R2, ReSpeaker kafada mı — KAPANDI
- **Seçenekler o zaman:** A hub kafada, B hub gövdede, C hoparlör kafada; R1 / R2 (`KY/secenekler.md:14-20`, `:334-335`); ReSpeaker kafada mı
  (`qled-cerceve-tasarim-notu.md:146`).
- **Sayısal etki:** C'de mikrofon-hoparlör 222,2 mm < 400 (`KY/secenekler.md:16`).
- **Durum:** kapandı. "Seçim: B + R1, 05.11.2026, uygulandı" (`KY/secenekler.md:1`; `KY/uygulama-notu.md:3`), commit `d26c7e7`.

## K18 · `tubitak-2209b/` depoya girsin mi
- **Seçenekler:** a) dışla, `.gitignore`'a yaz; b) commit.
- **Sayısal etki:** 251 yol, 102 MB (`du -sh`); docx yedekleri, hakem raporları, kişi adları. Depo açık (`gh repo view`: PUBLIC).
  a'da `elektrik.md:10` (çalışma kopyası) `tubitak-2209b/BAGLAM.md` ve v4 xlsx'e atfı temiz klonda boşa düşer.
- **Varsayılan:** a. 2209-B dosyalarına dokunulmaz (`dongu-158.md:39, §2 2209-B kuralı`); `.gitignore` yalnız depo dosyasıdır, klasöre dokunmaz.
- **Bloke:** P0.1 kabul ölçütü ("git status yalnız bilinçli dışlananlar", `dongu-158.md:54, §3 P0.1`).
- **Durum:** açık (P0.1).

## K19 · `kvkk/` depoya girsin mi
- **Seçenekler:** a) dışla; b) commit.
- **Sayısal etki:** 16 dosya, 3,1 MB; docx'te proje yürütücüsü adı ve üniversite; `kvkk/fiyatlar.md:3` "Bu dosya iç dosyadır" diyor (`saglayici-secimi.md:3` kendini "asistan taslağı" diye tanımlıyor; "iç dosya" ifadesi orada yok).
- **Varsayılan:** a.
- **Bloke:** P0.1.
- **Durum:** açık (P0.1).

## K20 · `rapor/` (tek sayfa rapor) depoya girsin mi
- **Seçenekler:** a) dışla; b) yalnız son sürümler (`Lale-tek-sayfa.*`, `Lale-2209B-tek-sayfa.*`, `lale158-model.js`, `lale158-patlatma.js`,
  iki PNG, `vendor/`); c) hepsi (ara sürümler dahil).
- **Sayısal etki:** 20 dosya, 11 MB; `lale158-model.js` 2,0 MB. Sayfada ekip üyelerinin ve danışmanın adları var. Ahmet'in adı
  HEAD'de 6 izlenen dosyada zaten var (`git grep -l HEAD`, ör. `KY/secenekler.md:8`, `KY/uygulama-notu.md:3`); diğer üç öğrencinin
  soyadı ve danışmanın adı izlenen dosyalarda 0 sonuç. b'de 10 ara sürüm dosyası (`-v1*`, `-v2*`) yerelde kalır.
- **Varsayılan:** a (diğer üç öğrencinin soyadı ve danışmanın adı açık depoya ilk kez girer, onların onayı kayıtta yok; karar Ahmet'in).
- **Bloke:** P0.1.
- **Durum:** açık (P0.1).

## K21 · `KY/kaynak/` satıcı ve üretici dosyaları
- **Seçenekler:** a) dışla, indirme adresini `.gitignore` yorumuna yaz (emsal `.gitignore:6-9`, "üreticinin büyük dosyaları depoya girmez");
  b) commit.
- **Sayısal etki:** 5 dosya, 3,0 MB; ReSpeaker STEP 2,8 MB, lisansı **doğrulanmadı**; iki satıcı fotoğrafı izinsiz (`tubitak-2209b/BAGLAM.md:224`
  Şekil 3 gerekçesi). a'da temiz klonda `kafa10_lib.py:78` STEP'i bulamaz: kafa modülü dosya indirilmeden üretilemez.
- **Varsayılan:** a.
- **Bloke:** P0.1; P6.1 yalnız temiz klonda koşulursa.
- **Durum:** açık (P0.1).

## K22 · `tasarim/solidworks/` ve hareket döngüsü makrosu
- **Seçenekler:** a) `step_renkli.py`, `step_duz.py`, `renkler.md` ve `lale_dongu.FCMacro` + `.bat` commit, iki STEP dışla;
  b) hepsini dışla; c) hepsini commit.
- **Sayısal etki:** `Lale-1650-duz.step` 28,3 MB, 1,65 m (eski); b'de makro renk tablosunu bulamaz (`lale_dongu.FCMacro:216-226`).
  Önceki brief'ler klasörü commit'e almamıştı (`planlama/y2/Y2b-brief.md:15`, `planlama/y3/Y3-brief.md:25`); bu orkestratör kuralıydı, Ahmet kararı kayıtta yok.
- **Varsayılan:** a.
- **Bloke:** P0.1.
- **Durum:** açık (P0.1).

## K23 · 03.11 ara çıktıları
- **Soru:** `planlama/y2/Y2b-ivme.json`, `tasarim/freecad/montaj/yerlesim-kontrol.json` ve 13 kabuk görseli 03.11 koşusundan (QLED, çerçeve
  ve 05.11 kabuğundan önce) değişmiş duruyor (`qled-cerceve-tasarim-notu.md:19`).
- **Seçenekler:** a) "ara çıktı, eski" mesajıyla commit; P6.1 yeniden üretir; b) commit etme; `git status` P6.1'e kadar kirli kalır.
- **Sayısal etki:** Y2b-ivme kütlesi 25.467,9 g (çalışma kopyası `kutle_g`), HEAD 24.796,1 g (1,65 m), güncel model 25.910,6 g
  (`KY/uygulama-ivme.json ev.kutle_g`). Korunan değerlerin hiçbiri bu dosyalardan okunmuyor (`planlama/d158/regresyon.py`).
- **Varsayılan:** a.
- **Bloke:** P0.1.
- **Durum:** açık (P0.1).
- **Not (F1b P1.1, 08.11.2026):** `planlama/y2/Y2b-ivme.json` P1.1 güncel modelle yeniden üretti (`planlama/y2/Y2b-ivme.py`, akü 3,0 kg):
  ev kütlesi 26.115,6 g, yüksüz rampa5_geri 1,519 (`KY/uygulama-ivme.json` ile aynı). Artık 03.11 ara çıktısı değil. K23'ün öteki dosyaları
  (`montaj/yerlesim-kontrol.json`, `kabuk/gorsel/*.png`) bilerek yazılmadı, 03.11 hâlinde (`planlama/d158/F1b-gunluk.md` P1.1).

## K24 · G4 öncesi 11,6" raporundaki iki satır temizlensin mi
- **Soru:** `raporlar/11-6-inc-gogus-ekrani-sigma.md:40` ve `:59` depo dışındaki hafıza kasasının arşiv dosya adlarını ve takma adı içeriyor.
  Dosya G4 ile açık depoya ilk kez giriyor.
- **Seçenekler:** a) G4'ten önce bu iki satır temizlensin (atıf "depo dışı not" gibi nötr bir ifadeye, takma ad "Ahmet"e), sonra commit;
  b) G4 olduğu gibi commit'lensin, temizlik P4.5'e kalsın.
- **Sayısal etki:** 1 dosya, 2 satır. b'de iki satır P4.5'ten sonra da git geçmişinde kalır (geçmişi yeniden yazmak onaysız yapılmaz:
  `dongu-158.md:36-37, §2 "Yapılmayacaklar"`); a'da G4 temizlik bitene kadar bekler. P4.5 kapsamı kodda ~43 dosya (`dongu-158.md:92, §3 P4.5`).
- **Varsayılan:** a, G4'ten önce temizle.
- **Bloke:** G4 commit'i (P0.1).
- **Durum:** açık (F0 kontrolü, `planlama/d158/F0-kontrol.md` B1.5 ve düzeltme maddesi 5).

---

## Karar değil, iş (kuyruğa alınmadı)
- Kapak baskı analizinde iki sonuç (19.667,7 mm² ↔ 5,01 mm², `KY/uygulama-notu.md:68`): P6.2.
- `elektrik.md` boyun/hub satırları ve baskı listesi yeni düzene (`KY/uygulama-notu.md:153`): P4.1, P4.3.
- K7 perçin delik çapı ve perçin somun ölçüleri (`Y3-kontrol.md:115`): ölçüm, P8.3.
- Ölçülmesi gerekenler (akustik, yankı, hub girişi gerilimi; `KY/secenekler.md:248-254`): P8.3.
