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
| K25 | Depodaki `CLAUDE.md` içindeki takma ad | **açık** | b: ad değişimi (3 satır) | P4.5 kabul ölçütü |
| K26 | GitHub hesap adı (depo adresi ve Pages bağlantıları) | **açık** | a: şimdilik bırak | P4.5 kabul ölçütü (`index.html:49,92`) |
| K27 | Hocadaki liste: 17.10 Excel mi, 03.11 v4 mü | **açık** (F8a) | b: v4, §2.2 farkı | Fark iletimi, K28, P8.1 onayı |
| K28 | Bütçe farkı (≈ +29.545 TL) hocaya bildirilsin mi | **açık** (F8a) | a: siparişten önce | P8.1 onayı (S = 16.11) |
| K29 | Erken alım: bu hafta mı, okul mu kişisel mi | **açık** (F8a) | Bu hafta, insert 168; okul/kişisel için yok | P9.1 kupon, kritik yol 1 |
| K30 | Akü zamanlaması: Atakale bu hafta / S'de / Limacell | **açık** (F8a) | a: Atakale bu hafta; biterse Limacell S'de | Dal 2b, taban adım 9 |
| K31 | Isıl gömme insert A/B/C (M3 ve M5) | **açık** (F8a) | M3: A (OD4 L4); M5: yok | K29, kupon C, P4.3 |
| K32 | Kafa ekranı: hocadan mı, satın alma mı | **açık** (F8a) | Kayıtta yok | `maliyet.json` öneri 8, K28, Parti 3 |
| K33 | M6×16: ikinci satıcı / paslanmaz / fosfat şartı | **açık** (F8a) | a: paslanmaz DIN 912 A2 | Taban (aşama 5) |
| K34 | 3B baskı hizmeti ücretli mi, teklif | **açık** (F8a) | a: teklif S'den önce | K28, `maliyet.json` öneri 10 |
| K35 | Onaylı olmayan satıcılar (6.063,11 TL) hocaya nasıl | **açık** (F8a) | Kayıtta yok | P8.1 liste biçimi, K29 |
| K36 | 8 Ω hoparlör (PAKET A) stok 1 < 3 | **açık** (F8a) | Kayıtta yok | PAKET A siparişi |
| K37 | Kamera Module 3 tükendi | **açık** (F8a) | a: S'de yeniden bak | Görüntü (ikinci aşama) |
| K38 | S2 alt bölge hız sınırı ve kapanma sırası | **açık** (F2) | a: S2 < 20°'de ≤ 60°/s (yüklü ≤ 30°/s); kapanmada S2 ≤ 15° | `kod/` hareket planlayıcısı, kapanma |
| K39 | Omuz durdurucu güçlendirme | **açık** (F2) | d: kök yarıçapı (P6.1) + DS3235 düşme ölçümü, sonra gerekirse | P6.1, ölçüm kâğıdı, K38 |
| K40 | S2 sıfır kalibrasyonu ve sınır metni (`yana_alt_bosluk_mm`) | **açık** (F2) | a: horn dişe dayalı takılır; metin P6.1'de | P6.1, P7.1, `eklem_sinirlari.json` |
| K41 | S1 yazılım aralığı: kod 0…160 ↔ CAD −45…135 | **açık** (F2 + F5) | a: kod −45…135 | `kod/` eklem sınırları, P5.1 |
| K42 | PETG-CF miktarı: 1,5 kg yetmiyor | **açık** (F4c; F6b notu eklendi) | a: +1 makara (4 × 0,5 = 2,0 kg), +1.114,03 TL | S siparişi filament satırı, K34, Parti 0/2 |
| K43 | Isıl gömme somun adedi: M3 177, M5 21 (plan 168 / 6) | **açık** (F4c) | Erken alımda M3 177 + pay, M5 21 + pay | K29, K31, Parti 0 kuponları |
| K44 | `eklem_sinirlari.json`'un `kod/`'a yazılması | **açık** (F6a) | a: Ahmet onayıyla `kod/`'a yazılır + Efe'ye pano bilgisi | `kod/ortak/eklem_sinirlari.json` güncelliği, K2/K3 regresyon betikleri, P4.5 (`kod/`) |
| K45 | S2 darbe hız sınırı (K38'i sayısallaştırır) | **açık** (F6a) | Kayıtta yok (a / b / c) | K38, `kod/` hareket planlayıcısı, K39 ölçümü |
| K46 | Destek azaltma geometri önerileri (VESA, omuz yuvası, kol çatalı, omuz göbeği, göğüs bandı) | **açık** (F6b) | Şimdilik değişiklik yok; Parti 0 kuponundan sonra karar | Parti 1–2 dilimleme, K42 payı, tam tarama (geometri değişirse) |

**Açık: 41** (biri, K14, Ahmet'in değil Efe'nin teyidi). **Kapandı: 5** (K5, K8, K15, K16, K17). Toplam 46 madde.
P8.1 (F8a, 09.11.2026) Ahmet listesinin 14 maddesi (`planlama/d158/F8a-siparis.md` §9): 10'u 11 yeni madde oldu (K27–K37; madde 3
erken alım K29 ve insert K31 diye bölündü); 4'ü (madde 6, 7, 8, 9) var olan K4, K9, K1 / K10 / K11 / K12 ve K2'ye not olarak eklendi.
P2.1 (F2, 09.11.2026) karar taslakları KT-F2-1…4 → K38–K41, B'nin düzeltilmiş metinleriyle (`planlama/d158/F2-kontrol.md`); KT-F2-4 F5 bulgusuyla tek karar (K41).
P4.3 + P8.2 (F4c, 09.11.2026) karar taslakları KT-F4c-1…2 → K42–K43, B'nin metinleriyle (`planlama/d158/F4c-kontrol.md`; K43 B-1 düzeltmesiyle M5 21).
P6.1 + P4.5 (F6a, 09.11.2026) karar taslakları KT-F6a-1 → K44, KT-F6a-2 → K45 (`planlama/d158/F6a-gunluk.md` §4, B düzeltmeleriyle `F6a-kontrol.md` O-2).
KT-F6a-3…5 karar değil, iş olarak kapandı (sondaki bölüm).
P6.2 (F6b, 09.11.2026) karar taslakları KT-F6b-1 → K42'ye F6b notu, KT-F6b-3 → K46 (`planlama/d158/F6b-gunluk.md` §5–6, B düzeltmesiyle
`F6b-kontrol.md` O-1). KT-F6b-2 karar değil, iş (sondaki bölüm).

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
- **Not (F8a P8.1, 09.11.2026):** maliyet etkisi a 0 TL; c 0 – 76,24 TL (Robotistan micro USB 1,5 m, stok 90; cihaz bilinmediği için kablo
  tipi doğrulanmadı); b doğrulanmadı (`planlama/d158/F8a-siparis.md` §6, §9 madde 8). Sipariş paketi varsayılan a ile K1'siz verilebiliyor.
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
- **Not (F8a P8.1, 09.11.2026), bütçe sorusu:** AI HAT+ (26T) PAKET A'da (TÜBİTAK önerisi, okul toplamına girmez): Robotistan 6.978,88 TL,
  stok 23. Açık soru: TÜBİTAK desteği gelmezse kart okul bütçesine mi eklenir (+6.978,88; okul bütçesi 93.538,38 → 100.517,26)?
  Yerleşim seçeneği a/b'nin maliyet etkisi 0 (yalnız baskı geometrisi). Kaynak: `planlama/d158/F8a-siparis.md` §5.7, §6, §9 madde 9.
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
- **Not (F4a, 09.11.2026):** P4.2 (09.11): 9 kablo/fiş adayı + PAM8403 + USB ses kartı `maliyet.json`'a fiyatsız (`fiyat_bekliyor`, toplam dışı) eklendi; fiyat P8.1'de.
- **Not (F8a P8.1, 09.11.2026):** 4 kablo sayfada fiyatlandı: USB-A uzatma 30 cm 77,46 (Robotistan), 1 m 214,20 (Motorobit), kısa micro USB
  38,42 (Robotistan), hoparlör kablosu 2 × 30,60 (Motorobit); toplam **+391,28 TL** (a: koşullu, genel toplam dışı, 0; c: +391,28).
  L USB-A dirsek ve L 3,5 mm kısa kablo onaylı sitelerde bulunamadı. `maliyet.json` (09.11, P8.1 kaydı): dört satır fiyatlı ve
  `secenek: kosullu` (koşullu toplama giriyor), iki satır `fiyat_bekliyor` kaldı. F8a önerisi: bu iki kablo P4.2'de kablo yarıçapıyla
  yeniden değerlendirilsin (`planlama/d158/F8a-siparis.md` §5.3, §6, §9 madde 6).
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
- **Not (F8a P8.1, 09.11.2026), b'nin maliyeti (sayfa fiyatları; kütle etkisi yine hesaplanmadı):**
  - pay ≥ 1: dirsekte 2 MG996R → DS3218MG (2 + 1 yedek) **+2.332,50 TL** (Robocombo 980,00, stok 4; ikinci satıcı Motorobit 1.315,80 ile +3.339,90).
  - pay ≥ 2: 6–8,4 V'ta stoklu ≥ 62,4 kg·cm servo yok: Motorobit RDS5180 80 kg (2.876,40) ve RDS51150 150 kg (3.672,00) tükendi;
    Robocombo DES220 220 kg **24 V** 15.075,00 stok 5 (24 V servo hattı gerekir). DS5160 60 kg·cm (5 adet +3.195,00) eşiğin altında
    (60 < 62,4). Dirsek ≥ 25,2 için DS3235: +4.819,50. Kaynak: `planlama/d158/F8a-siparis.md` §6, §9 madde 7; `F8a-kontrol.md` §2.3.
- **Bloke:** P3.2, P5.1 (servo modeli sütunu), P8.1.
- **Durum:** açık (`kararlar-2026-10-29.md:23` "AÇIK (karar değil)").

## K10 · PAM8403 5 V besleme noktası
- **Seçenekler:** a) D24V50F5 (Pi hattı); b) SY8205 (kafa ekranı hattı); c) ayrı küçük düşürücü.
- **Sayısal etki:** a) Pi hattı normalde 2,67 A, 5 A'nın %53'ü (`elektrik.md:24`); PAM tepesi 0,71 A ile tepe 3,28–3,38 A, %66–68
  (`KY/uygulama-notu.md:98`). b) ekran hattı 0,9 A **varsayım**, 3,7 A'nın %24'ü (`elektrik.md:25`); PAM eklenince ~1,6 A, ekran
  akımı ölçülmeden belirsiz. c) maliyet ve yer **doğrulanmadı**. Akımların hepsi hesap, ölçülmedi.
- **Varsayılan:** a (model bunu varsayım olarak kullanıyor: `KY/uygulama-notu.md:97`; P1.2 tanımı da a: `dongu-158.md:63, §3 P1.2`).
- **Bloke:** P1.2 (`elektrik.md` metni), P4.1, P8.3 (PAM akımı testi).
- **Not (F4a B çekincesi, 09.11.2026):** PAM tepe 0,71 A (`uygulama-notu.md:98`); Pi tam yük tepesiyle birlikte ölçülmeden 'sınırda değil' denmez (P8.3 testi).
- **Not (F8a P8.1, 09.11.2026):** maliyet etkisi a ve b 0 TL; c +61,20 TL (Motorobit 5 V 3 A düşürücü, stok 459; ikinci Robotistan
  163,45, stok 361); yer ve ölçü doğrulanmadı (`planlama/d158/F8a-siparis.md` §6, §9 madde 8).
- **Durum:** açık (`KY/secenekler.md:338`, `KY/uygulama-notu.md:152`).

## K11 · Göğüs ekranı 12 V dalının girişi
- **Soru:** Dal ana anahtardan sonra mı, röle K1'in anahtarlı barasından mı alınsın? Bu, ekranın acil stopta açık kalıp kalmayacağını
  belirler (`elektrik.md:55` "karar yok").
- **Seçenekler:** a) ana anahtar sonrası, röle öncesi (sigorta kutusundan ayrı 2 A dal): acil stopta ekran açık; b) anahtarlı bara: acil stopta ekran kapanır.
- **Sayısal etki:** dal mini 2 A, ekran ~0,5 A @ 12 V (`elektrik.md:316`, `:19`); F1 20 A anahtarlı bara (`elektrik.md:60`).
  Kafa F3 5 A dalı röleden önce (`elektrik.md:60`): Pi acil stopta açık kalıyor.
- **Varsayılan:** a. Gerekçe: Pi açık kaldığı için ekran acil stop durumunu gösterebilir. Bu bir öneri; güvenlik açısından **doğrulanmadı**.
- **Bloke:** P4.1, P4.2 (kablo boyu), P7.2 (göğüs ekranı montaj adımı, `R-gunluk.md:33-35`).
- **Not (F8a P8.1, 09.11.2026):** maliyet etkisi ≈ 0 TL: iki seçenekte parçalar aynı (12 V regülatör, mini yuva, 2 A sigorta v4'te);
  kablo boyu farkı ölçülmedi (`planlama/d158/F8a-siparis.md` §6, §9 madde 8).
- **Durum:** açık (`elektrik.md:55`).

## K12 · Kafa havalandırması: mevcut yarıklar mı, 30 mm fan mı
- **Seçenekler:** a) mevcut arka yarıklar, fan yeri ayrılı ama parça yok; b) 30 mm egzoz fanı şimdi.
- **Sayısal etki (el hesabı):** normal 19,8 W'ta kapalı 49,7 °C, yarıklı 48,2 °C, fanlı 36,9–39,1 °C; yükte 22,9 W'ta 52,8 / 50,9 /
  38,0–40,5 °C (`qled-cerceve-tasarim-notu.md:114-117`). Sınır: servo 55 °C, tilt servo gövdesi 50 °C (`qled-cerceve-tasarim-notu.md:119`).
  Yarıklı sonuç yükte 0,9 K aşım veriyor; hesap karşılaştırma içindir.
- **Varsayılan:** a; stres testinde tilt servo gövdesi 50 °C'yi geçerse fan eklenir (`qled-cerceve-tasarim-notu.md:119`).
- **Bloke:** P8.1 (fan kalemi), P8.3 (ısı testi kâğıdı).
- **Not (F8a P8.1, 09.11.2026):** a 0 TL; b 30 mm 12 V fan +66,07 TL (Motorobit, stok 526; ikinci Robotistan 90,87, stok 97). Fan yeri
  zarfı AI HAT+ zarfıyla kesişiyor (K2 notu) (`planlama/d158/F8a-siparis.md` §6, §9 madde 8).
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
- **Not (F4b B, 09.11.2026):** izlenmeyen `tasarim/solidworks/renkler.md:63` takma ad taşıyor; klasör depoya alınırsa önce temizlenmeli
  (`planlama/d158/F4b-kontrol.md` madde 20).

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

## K25 · Depodaki `CLAUDE.md` içindeki takma ad
- **Soru:** Depo kökündeki `CLAUDE.md` (yapay zekâ oturumları için bağlam dosyası) takma adı 3 satırda taşıyor: satır 3 (robot adının
  kimin kararı olduğu), satır 4 (proje sahibinin tanıtımı: mekanik, montaj, kablaj, SolidWorks; yazılımı yapay zekâyla yazıyor), satır 22
  (projenin takma adlı not deposu oturumundan yönetildiği, tercih tarihi 26 Eylül 2026). P4.5a bu dosyaya dokunmadı
  (`planlama/d158/F4b-gunluk.md` §4 ve §5 K-F4b-1).
- **Seçenekler:**
  a) Olduğu gibi bırak.
  b) Ad değişimi: satır 3'te "adı Ahmet'in kararı", satır 4'te "Proje sahibi Ahmet Yorulmaz;", satır 22'de "kişisel not deposu (vault)
     oturumundan yönetiliyor (Ahmet'in tercihi, 26 Eylül 2026)".
  c) Dosyayı izlemeden çıkar (`git rm --cached` + `.gitignore`), yerelde kalsın.
- **Etki:** a) herkese açık depoda 3 satır takma ad kalır; P4.5 kabul ölçütü hiçbir zaman tam temiz olmaz; ajan davranışı değişmez.
  b) depo temizlenir; bu klasörde açılan ajanlar sahibine "Ahmet" diye atıf yapar (resmî ad kuralıyla uyumlu); not deposunun kendi
  talimatları ayrı dosyada olduğundan oradaki oturumlar etkilenmez; risk düşük. c) herkese açık son sürümde görünmez, ama ekip üyelerinin
  (Efe) ajanları bu bağlamı kaybeder; silme sayıldığı için ayrıca onay ister.
- **Git geçmişi:** üç seçenekte de git geçmişi eski metni taşır (P4.5'teki bütün dosyalar için geçerli); geçmişten silmek geçmişi yeniden
  yazmayı gerektirir (`dongu-158.md` §2 "Yapılmayacaklar": onaysız yapılmaz). Ayrı karar konusu.
- **Önerilen varsayılan:** b (`F4b-gunluk.md` §5 K-F4b-1; B kontrolü Koşul 2 ile satır metinleri netleşti: `F4b-kontrol.md` madde 18).
- **Bloke:** P4.5 kabul ölçütü (`git grep -i <takma ad>` yalnız tarihçe / hafıza dosyalarında).
- **Durum:** açık.

## K26 · GitHub hesap adı (depo adresi ve Pages bağlantıları)
- **Soru:** `tasarim/freecad/index.html:49` ("Tek sayfa özet") ve `:92` ("GitHub deposu") bağlantıları deponun GitHub adresine gidiyor;
  adresin hesap kısmı, yani hesap adı takma adı içeriyor. Deponun `origin` adresi ve Pages adresi de aynı hesap adını taşıyor; bu iki
  satır depo adresinin kendisinden fazlasını açığa çıkarmıyor. Yayındaki hâli `main`'de (Pages); bu dalda değiştirmek siteyi birleştirmeye
  kadar etkilemez (`F4b-gunluk.md` §5 K-F4b-2; `F4b-kontrol.md` madde 14).
- **Seçenekler:**
  a) Şimdilik bırak.
  b) Göreli bağlantı (`OZET.md`, `./`).
  c) Yer tutucu.
  d) Depoyu hesap adında takma ad olmayan bir hesaba / organizasyona taşı ya da hesap adını değiştir.
- **Etki:** a) bağlantılar çalışır; hesap adı zaten depo / Pages adresinde; P4.5 kabul listesinde gerekçeli kapsam dışı.
  b) hesap adı bu dosyadan kalkar; ama Pages'te `.md` dosyası Jekyll ile işlenirse `OZET.md` bağlantısı 404 olabilir, "Kaynak dosyalar"
  bağlantısı GitHub kod görünümü yerine site klasörüne gider; denenmeli. c) bağlantılar kırılır; önerilmez. d) tek kalıcı çözüm; `origin`,
  Pages adresi ve paylaşılmış bağlantılar değişir (GitHub depo web / git bağlantılarını yönlendirir; **Pages adresi yönlendirilmez**,
  paylaşılmış site linkleri kırılır: GitHub belgesi "Transferring a repository", `F4b-kontrol.md` madde 19).
- **Önerilen varsayılan:** a, şimdilik bırak (`F4b-gunluk.md` §5 K-F4b-2).
- **Bloke:** P4.5 kabul ölçütü (`index.html:49,92`).
- **Durum:** açık.

<!-- K27–K37: P8.1 sipariş paketi (F8a, 09.11.2026), kaynak `planlama/d158/F8a-siparis.md` §9. Sipariş verilmedi. -->

## K27 · Hocadaki liste: 17.10 Excel mi, 03.11 v4 mü
- **Soru:** Okulun siparişi için hocaya giden son malzeme listesi hangisi? Fark tablosu buna göre iletilir.
- **Kaynak çelişkisi:** `planlama/siparis-farki-2026-10-29.md` 17.10 Excel'i (= `maliyet.json` `b27fd80`) gösteriyor;
  `tubitak-2209b/BAGLAM.md:221-222` v4'ün (03.11) hocanın öğrencisine gittiğini ve beğenildiğini, `tubitak-2209b/malzeme-listesi/rapor.md:4`
  "Liste gönderilmedi" diyor (`F8a-siparis.md` §2, `F8a-kontrol.md` madde 10).
- **Seçenekler:**
  a) 17.10 Excel hocada: iletilecek fark `F8a-siparis.md` §2.1.
  b) v4 (03.11) hocada: iletilecek fark §2.2.
- **Sayısal etki:** a) 15 satır grubu (44 satır) eklenen, 8 grup (10 satır) çıkan, 37 grup değişen; 17.10 genel 99.673,04 (pay, elde ve
  kargo dahil) ↔ 158 okul bütçesi 93.538,38 (pay, elde ve kargo yok). b) 8 eklenen satır (K4 kabloları 6 + F1b 90° micro USB ve DC jak; 2'si
  fiyatsız) +491,34 TL; 1 satıcı değişimi (tırtıllı somun M5: Robotistan tükendi → CNC Marketi, 297,20 → 31,68); 1 model değişimi (625ZZ
  "BGR (Karbon)", 29,67 → 30,04); 24 satırda fiyat değişimi (site satırları 68.219,82 → 67.995,98).
- **Önerilen varsayılan:** b, v4 hocada sayılır ve §2.2 farkı iletilir (`F8a-siparis.md` §9 madde 1). Yalnız öneri.
- **Bloke:** hocaya fark iletimi, K28, P8.1 siparişinin onayı (S = 16.11).
- **Durum:** açık.

## K28 · Bütçe farkı hocaya bildirilsin mi
- **Soru:** 158 sipariş paketi README'deki eski tutarın üstünde; fark sipariş öncesi hocaya bildirilecek mi?
- **Seçenekler:** a) siparişten önce bildir (fark tablosu + köprü, `F8a-siparis.md` §7); b) sipariş günü (S) bildir; c) önce K32 (kafa ekranı)
  ve K34 (baskı hizmeti) netleşsin, sonra tek seferde bildir.
- **Sayısal etki:** 158 alınacaklar (pay dahil, kargo hariç) **107.569,14 TL**. README'deki eski ≈ 78.000'e (`maliyet.json` 29.10 + F4a,
  elimizdekiler düşülmüş 78.023,96) göre **≈ +29.545**; elde dahil kıyasla 116.845,70 ↔ 102.919,71 → +13.925,99 (`F8a-siparis.md` §7).
  Güncel `maliyet.json` (09.11, P8.1 kaydı) elimizdekiler düşülmüş 93.770,47 ↔ 107.569,14: **+13.798,67**; bu farkın kalemleri kafa
  ekranı QLED +8.300,64 (K32), baskı hizmeti − filament +5.412,95 (K34), K4 + F1b koşullu kalemler +617,83, insert/vida/köşe/kamera/köpük
  bant +179,10, kargo satırı −711,85 (hepsi × 1,15). c'de K32 ve K34 farkı ≈ 13.700 TL oynatabiliyor.
- **Önerilen varsayılan:** a (`F8a-siparis.md` §9 madde 2). Yalnız öneri.
- **Bloke:** P8.1 siparişinin onayı (S = 16.11).
- **Durum:** açık.

## K29 · Erken alım: bu hafta mı, okul siparişi mi kişisel mi
- **Soru:** P9.1 erken alımı (rulmanlar, ısıl gömme somunlar, kupon D vidaları) bu hafta yapılacak mı; satıcılar onaylı listede olmadığı için
  okul siparişi mi kişisel alım mı?
- **Seçenekler:** a) bu hafta (H7), okul siparişi; b) bu hafta, kişisel alım; c) S'de (16.11) ana siparişle birlikte.
- **Sayısal etki:** bugün **1.515,90 TL** (plan 1.496,37; +19,53), Rhino3DPrinter kargosuyla **1.654,90 TL** (139 TL; Rulmanal ve
  paslanmazcivata.ist eşik altı, ücret sayfada yok). Insert 176 alınırsa 1.558,22. Satıcılar: Rulmanal (stok 51 / 8.398), Rhino3DPrinter
  (stokta, adet yok), paslanmazcivata.ist. Plan: S = 16.11 yalnız erken kupon alımıyla tutuyor (`F8a-siparis.md` §3; `proje-plani.md:71, 119`);
  c'de kupon basımı ve kritik yol 1 kayar (gün sayısı hesaplanmadı).
- **Önerilen varsayılan:** bu hafta (H7), insert 168, fark 8 P4.3'te (`F8a-siparis.md` §9 madde 3). Okul / kişisel ayrımı için önerilen
  varsayılan yok. Yalnız öneri.
- **Bloke:** P9.1 kupon basımı, kritik yol adım 1; K31'e bağlı (insert varyantı).
- **Durum:** açık.

## K30 · Akü zamanlaması: Atakale bu hafta / S'de / Limacell
- **Soru:** Victron 20 Ah (Atakale, onaylı satıcı) "7 gün içinde tedarik" diyor ve stok 1; akü ne zaman, kimden alınacak?
- **Seçenekler (varış tahmini: sayfadaki kargoya veriliş + taşıma 1–3 iş günü varsayımı, `F8a-siparis.md` §3.1):**
  a) Atakale Victron 20 Ah, erken alımla bu hafta (10–12.11): kargoya ≤ 17–19.11, varış ≈ 18–24.11; adım 9'a (≈ 25–26.11) yetişir.
     Stok 1: o güne kadar satılmazsa. S'den önce ödeme ve hoca onayı gerekir.
  b) Atakale, S'de (16.11): kargoya ≤ 23.11, varış ≈ 24–28.11; adım 9 için **sınırda / geç** (0–3 gün bekleme).
  c) Limacell 12 V 24 Ah (Geçersun Enerji, onaylı değil), S'de: ortalama hazırlanma 3 iş günü, varış ≈ 20–24.11; yetişir.
  d) Limacell, bu hafta: sayfa 09.11 siparişi için "en geç 12 Kasım" kargoda diyor, varış ≈ 13–17.11.
- **Sayısal etki:** Atakale **12.680,70 TL**; Limacell **4.814,86 TL** (havale 4.622,27; 3.000 TL üzeri kargo ücretsiz), Atakale'den
  −7.865,84. Limacell'in ölçü ve kütlesi sayfada yok, CAD akü yuvasıyla kontrol edilmedi; 30 A sürekli deşarj sınırının motor tepe akımı ve
  ana sigortayla uyumu doğrulanmadı; özel üretim olduğu için iade yok. `maliyet.json` akü satırında Limacell artık 2. satıcı (`alt`, 09.11).
- **Önerilen varsayılan:** a; Atakale biterse c (`F8a-siparis.md` §9 madde 4). Yalnız öneri.
- **Bloke:** kritik yol dalı 2b, taban adım 9 (aşama 5, ≈ 25–26.11).
- **Durum:** açık.

## K31 · Isıl gömme insert seçeneği A/B/C (M3 ve M5)
- **Soru:** CAD'in M3 insert'i (boy 5,7, delik Ø4,0; `arayuz.INSERT`) Rhino3DPrinter sayfasında yok. Erken alımda hangi varyant alınacak;
  M5 için kupon deliği uyuyor mu?
- **Seçenekler (M3, `F8a-siparis.md` §4.1):**
  A) Rhino ID3 OD4 L4: Rhino kuralıyla delik Ø3,8–3,9; kupondaki Ø3,8 ve 3,9 delikleri bunu dener, kupon değişmez; diş boyu 1,7 mm kısa,
     CAD boyu P4.3'te 4'e çekilir.
  B) Rhino ID3 OD5 L6: delik Ø4,8–4,9; kupon delikleri (Ø3,8–4,1) uymaz, kupon ve CAD deliği büyütülür (FreeCAD işi); kupon basımı gecikir.
  C) ruthex RX-M3x5.7 (dış çap 4,6, üretici deliği 4,0–4,2): CAD Ø4,0 ile uyumlu; Türkiye'de satıcı bulunamadı, fiyat / teslim / gümrük
     doğrulanmadı; erken alım takvimine (11–12.11) yetişmesi beklenmez.
- **M5:** CAD kupon delikleri Ø6,2 / 6,4 / 6,6, derinlik 7,5; Rhino'da ID5 OD7 L7 var, kurala göre delik Ø6,7–6,8 (kupondakilerden büyük).
  Seçenek: kupon M5 deliklerini Ø6,7–6,8'e büyütmek ya da başka ürün; M3 ile aynı soru (`F8a-siparis.md` §4.1, §9 madde 3).
- **Sayısal etki:** fiyatlar taban (M3 5,29, M5 6,35; varyant fiyatı sepete eklemeden görünmedi). M3 adedi 168 (plan, `maliyet.json`) ↔
  176 (v4): fark 8 adet +42,32 TL. Yanlış varyant erken alımı boşa çıkarır (kuponun amacı geçme denemesi, `F8a-kontrol.md` D3).
- **Önerilen varsayılan:** M3 için A (`F8a-siparis.md` §9 madde 3). M5 için önerilen varsayılan yok. Yalnız öneri.
- **Bloke:** K29 (erken alım), kupon C basımı, P4.3 (insert boyu ve adedi). `maliyet.json` insert satırlarında yalnız not var (09.11).
- **Durum:** açık.

## K32 · Kafa ekranı: hocadan mı gelecek, satın mı alınacak
- **Soru:** README ve `maliyet.json` notu "yüz ekranı 10,1" HDMI'yı hoca verecek" diyor; v4 (03.11) QLED'i satın alma satırı yapıyor. Hangisi?
- **Seçenekler:** a) hocadan gelir: `maliyet.json`'da V3 Waveshare 10,1" (B) satırı `elde` kalır, toplam değişmez;
  b) satın alınır: QLED 10,1" Robotistan, `maliyet.json` öneri 8 uygulanır (QLED satırı eklenir, Waveshare V3'ten çıkar).
- **Sayısal etki:** QLED Robotistan **7.217,95 TL** (indirimli; liste 8.124,85, indirim bitince +906,90), **stok 2** (v4'te 4); ikinci
  satıcı Motorobit 15.300,00 (stok 10, +8.082,05); Direnc 8.523,08 tükendi. b'de `maliyet.json` V3 ara −5.206,55 (genel −5.987,53:
  118.666,22 → 112.678,69); "elimizdekiler düşülmüş" toplam +8.300,64 (93.770,47 → 102.071,11).
- **Önerilen varsayılan:** kayıtta yok. F8a önerisi: alınacaksa S'nin ilk partisinde; stok 1'e düşerse öne alınsın (`F8a-siparis.md` §9
  madde 5; `F8a-gunluk.md` §5 öneri 8). Yalnız öneri.
- **Bloke:** `maliyet.json` öneri 8, K28 (bütçe rakamı), Parti 3 kafa ekranı siparişi.
- **Durum:** açık.

## K33 · M6×16 cıvata: ikinci satıcı / paslanmaz / fosfat şartı
- **Soru:** `maliyet.json` M6×16 fosfat (18 adet, CNC Marketi) satırında CNC'de yalnız 2 adet var. Hangi cıvata alınacak; fosfat şartı gerekli mi?
- **Seçenekler:**
  a) paslanmaz DIN 912 A2 M6×16 (paslanmazcivata.ist, taban 3,89, ürün stoğu 322.514, boy ayrımı yok): baş şekli aynı; dayanım sınıfı
     farkı (A2-70 ↔ fosfat; sınıf sayfada yok) sigma bağlantısı için kontrol edilmedi.
  b) CNC Marketi M6×16 fosfat **bombe başlı** 4,80 (stok 235): sigma ve T-somunla tek kargo; baş şekli CAD'le kontrol edilmedi.
  c) CNC'deki 2 fosfat + 16 başka satıcıdan.
- **Sayısal etki:** a 18 × 3,89 = 70,02 TL (fosfat 64,80'e göre +5,22; F8a tutarı bununla); b 86,40 TL (+21,60). Fosfat şartının kaynağı
  bulunamadı (`maliyet.json` notu yalnız "CAD M6×16 = 16 + 2 yedek"). CNC'de M6×12 ve M6×20 fosfat allen de tükendi.
- **Önerilen varsayılan:** a (`F8a-siparis.md` §9 madde 11). `maliyet.json` satırı değiştirilmedi (satıcı değişimi bu karara bağlı). Yalnız öneri.
- **Bloke:** taban (aşama 5) sigma bağlantıları; sigma / T-somun siparişiyle aynı gün gelmesi gerekiyor (`F8a-kontrol.md` D2).
- **Durum:** açık.

## K34 · 3B baskı hizmeti: anlaşmalı firma ücretli mi, teklif alınacak mı
- **Soru:** 03.11'de filament firma / ekipten, baskı anlaşmalı firmadan denmişti. Baskı hizmeti ücretli mi; ücretliyse teklif ne zaman istenecek?
- **Seçenekler:** a) ücretli, teklif S'den önce istenir; b) ücretsiz (okul / firma anlaşması); c) ekip yazıcısı + filament (`maliyet.json` yazıcı modu).
- **Sayısal etki:** F8a tahmini **11.550 TL** (7,7 kg × 1.500 TL/kg, teklif yok); okul bütçesi 93.538,38 bu tutarı içeriyor (b'de 81.988,38).
  `maliyet.json` V3 genel: yazıcı modu (filament 6.843,09) 118.666,22, hizmet modu 124.079,17.
- **Önerilen varsayılan:** a; teklif gelene kadar `maliyet.json`'a fiyatlı baskı hizmeti satırı yazılmaz (F8a öneri 10 geri çekildi;
  `F8a-siparis.md` §9 madde 10). Yalnız öneri.
- **Bloke:** K28 (bütçe rakamı), `maliyet.json` öneri 10.
- **Durum:** açık.

## K35 · Onaylı olmayan satıcılar hocaya nasıl gidecek
- **Soru:** Onaylı sitelerde bulunamayan kalemler (rulman, sigma profil, T-somun, köşe bağlantı, paslanmaz vida, insert) beş onaylı olmayan
  satıcıdan. Hocanın öğrencisine URL'siz (a) grubu olarak mı gidecek?
- **Seçenekler:** a) v4 biçiminde URL'siz (a) grubu; b) URL'lerle; c) okul siparişi dışında (kişisel alım, K29 gibi).
- **Sayısal etki:** **6.063,11 TL**: CNC Marketi 3.392,52 (4 satır), paslanmazcivata.ist 993,17 (25), Rhino3DPrinter 969,14 (2), Rulmanal
  582,84 (2), Otomasyoncu 125,44 (1). Kargo: CNC eşiği geçiyor (2.400); Rhino +139; diğer üçünde ücret sayfada yok (`F8a-siparis.md` §8).
  Tırtıllı somun M5 Robotistan'da (onaylı) tükendi; F8a önerisi CNC Marketi (M6 somun ve sigmayla aynı sipariş).
- **Önerilen varsayılan:** kayıtta yok (`F8a-siparis.md` §9 madde 12).
- **Bloke:** P8.1 sipariş listesinin hocaya giden biçimi; K29 (erken alım satıcıları da onaylı değil).
- **Durum:** açık.

## K36 · 8 Ω hoparlör (PAKET A): stok yetmiyor
- **Soru:** PAKET A'daki kutulu pasif hoparlör (8 Ω 5 W, 3 adet) Robotistan'da stok 1, fiyat sayfada görünmüyor. Ne yapılacak?
- **Seçenekler:** a) ikinci satıcı aranır; b) adet 1'e düşer; c) PAKET A'dan çıkar.
- **Sayısal etki:** v4 yaklaşık fiyatı 3 × 166,41 = 499,23 TL (bugün doğrulanmadı); b'de 166,41 (−332,82). PAKET A toplamı 14.215,11 TL
  (TÜBİTAK önerisi; okul toplamına girmez). İkinci satıcı aranmadı (F8a kapsamı dışı).
- **Önerilen varsayılan:** kayıtta yok; F8a önerisi "ikinci satıcı ya da adet düşürme" (`F8a-siparis.md` §9 madde 13).
- **Bloke:** PAKET A siparişi; okul siparişini bloke etmiyor.
- **Durum:** açık.

## K37 · Kamera Module 3 tükendi
- **Soru:** Raspberry Pi Camera Module 3 ve NoIR Module 3 bugün her onaylı sitede tükendi. Ne zaman / nereden?
- **Seçenekler:** a) S'de (16.11) yeniden bakılır; b) NoIR (v4 notu "gelmezse NoIR"; o da Robotistan'da tükendi); c) ithal
  (`maliyet.json` notu: Adafruit 29,25 USD + kargo; kargo ve gümrük doğrulanmadı).
- **Sayısal etki:** son sayfa fiyatı 1.835,13 TL (Robotistan, tükendi); F8a toplamında "doğrulanmamış" olarak var. Kamera kritik yolda
  değil (`proje-plani.md:138`; görüntü projenin ikinci aşaması).
- **Önerilen varsayılan:** a (`F8a-siparis.md` §9 madde 14). Yalnız öneri.
- **Bloke:** görüntü işleri (ikinci aşama); kritik yolu bloke etmiyor.
- **Durum:** açık.

<!-- K38–K41: P2.1 omuz durdurucu (F2, 09.11.2026), kaynak `planlama/d158/F2-gunluk.md` "Karar taslakları" KT-F2-1…4, metinler B'nin
düzeltilmiş önerisiyle (`planlama/d158/F2-kontrol.md` "Karar taslaklarına yorum"). -->

## K38 · S2 alt bölge hız sınırı ve kapanma sırası (KT-F2-1)
- **Soru:** Omuz durdurucu dişi (S2 4,30°) stall'u karşılıyor ama hızlı çarpma ve güç kesik düşmede emniyeti varsayıma bağlı. Yazılım S2'nin alt
  bölgesinde hızı sınırlasın mı, kapanmadan önce kolları indirsin mi?
- **Seçenekler:**
  a) B'nin önerisi: S2 < 20° bölgesinde açısal hız ölçüm gelene kadar ≤ 60°/s (elde yük varsa ≤ 30°/s); güç kesilmeden önce iki kol S2 ≤ 15°'ye
     indirilir.
  b) A'nın taslağı: ≤ 100°/s yüksüz, ≤ 50°/s yüklü (emniyet 2 hedefiyle; B-2 yüzünden sağlam değil).
  c) Sınır yok; durdurucuya ve acil stoptaki düşmeye güvenilir.
- **Sayısal etki:** diş emniyeti (`F2-gunluk.md` darbe tablosu; B aralıkları `F2-kontrol.md` B-2): stall 3,73; 1,5 rad/s yüksüz 2,24 (varsayıma göre
  1,22…2,57; kök köşesi hesapta yok); 1,5 rad/s 500 g 1,32 (0,67…1,55); kaçak servo tam hız 0,54; S2 30°'den güç kesik düşme 1,48 (0,69…1,78).
  Darbe kuvvetinin ~%88'i S2 mafsalına (horn/servo mili + 625ZZ) radyal gider; rotorun yansıyan eylemsizliği 1,5 rad/s'de dişliye stall'ın
  1,4…2,1 katı yük bindirir (B-1).
- **Önerilen varsayılan:** a. "K38 · S2 alt bölge hız sınırı: S2 < 20° bölgesinde açısal hız ölçüm gelene kadar ≤ 60°/s (elde yük varsa ≤ 30°/s).
  Güç kesilmeden önce iki kol S2 ≤ 15°'ye indirilir. Acil durdurmada kolun yüksekten düşebileceği kabul edilir; diş kırılırsa kol tambura ve
  kaset kapağına (3,65° / 3,21°) dayanır. Sahibi `kod/`; CAD değişmez. Gerekçe: F2-gunluk darbe tablosu ve F2-kontrol B-1/B-2." Yalnız öneri.
- **Bloke:** `kod/` hareket planlayıcısı ve kapanma betiği (Efe'nin alanı; panoya yalnız bilgi/soru); K39 ölçümü sınırı gevşetebilir.
- **F6a notu:** diş kökü r 1,5 yayı uygulandı, K_t 1,45; emniyet sayıları K_t ile yeniden hesaplandı. Sayısal hız sınırı için K45'e bakın.
- **Durum:** açık.

## K39 · Durdurucu güçlendirme (KT-F2-2)
- **Soru:** Diş, kaçak servo ve yüksekten güç kesik düşmede tek başına yetmiyor (emniyet < 1). Durdurucu güçlendirilsin mi, nasıl?
- **Seçenekler:**
  a) Dişe TPU (Shore 95A) ped 1–1,5 mm: tepe kuvvet ~√k ile azalır; 3,65…5° penceresi ~0,37 mm boşluk bıraktığı için yalnız c ile birlikte.
  b) Metal diş (ör. 3 mm alüminyum köşebent, 2 × M3): dayanım ×4 civarı, parça sayısı +3.
  c) S2 yazılım alt sınırı 5 → 8°: pencere 3,65…8° (≈ 2,3 mm), ped ve kalın diş sığar; `eklem_sinirlari.json` ve ev pozu değişir (kollar 3° daha açık).
  d) Önce en ucuz adım: kök yarıçapı + ölçüm, sonra gerekirse a/b/c.
- **Sayısal etki:** diş kökü t 5,67 mm, izin 20,6 MPa (sürekli) / 45,7 MPa (darbe); kök +x iç köşesi 90° keskin, 1,5…2 kat gerilme yığılmasıyla
  1,5 rad/s yüksüz emniyet ≈ 1,1…1,5 (`F2-kontrol.md` B-2). Kiriş 4,3°'de y ≈ −29'un altında, köşe y −23'te: yarıçap için ≈ 4 mm yer var.
- **Önerilen varsayılan:** d. "K39 · Durdurucu güçlendirme: (1) dişin kök +x iç köşesine ≥ 1,5 mm yarıçap/pah (sonraki taramalı pakette, P6.1).
  (2) Bir DS3235 ile ölçüm: güç kesikken S2 30 / 60 / 90°'den bırakılıp düşme süresi ölçülür. Bu ölçüm geri sürme sürtünmesini ve gerçek darbe
  enerjisini verir. Mümkünse rotor eylemsizliği de tahmin edilir. (3) Ölçüm emniyet < 1,5 gösterirse (b) S2 alt sınırı 5 → 8° ve TPU ped, ya da
  (c) metal diş. (b) seçilirse `eklem_sinirlari.json` ve ev pozu değişir." (Alıntıdaki (b)/(c) B'nin harflemesi: (b) = bu maddede c + a,
  (c) = bu maddede b.) Yalnız öneri.
- **Bloke:** P6.1 (kök yarıçapı `omuz_parcalar.py`'de; zaten plana yazıldı), P8.3 benzeri ölçüm kâğıdı (DS3235 gelince), K38'in gevşetilmesi.
- **F6a notu:** (1) yapıldı: kök yarıçapı r 1,5 uygulandı (temas 4,30° ve 5°'te 0,34 mm korundu), K_t 1,45. (2) DS3235 düşme ölçümü açık. K45'e bakın.
- **Durum:** açık.

## K40 · S2 sıfır kalibrasyonu ve sınır metni (KT-F2-3)
- **Soru:** S2 horn'u durdurucuya göre mi takılsın; `arayuz.py`'deki eski "kabuk −3°" tablosu ve `eklem_sinirlari.json` metni F2 ölçümüyle
  güncellensin mi?
- **Seçenekler:**
  a) Kalibrasyon dişe göre + sınır metni P6.1'de güncellenir (B'nin önerisi).
  b) Yalnız kalibrasyon talimatı değişir; `yana_alt_bosluk_mm` olduğu gibi kalır.
  c) Mevcut talimat (OR:114 "S2'yi 30° konumuna getir, horn'u tak") kalır.
- **Sayısal etki:** sıfır hatası > 0,7° olursa S2 5 komutunda kol dişe dayanır ve servo sürekli stall'da kalır (98 N; diş emniyeti 3,73, servo
  ısınır). Tolerans: baskı ±0,2 mm ≈ ±0,38°, 500 g ile 1,5 rad/s çarpmada çatal sapması 0,47°; toplam 0,85° tambur payını (0,65°) aşabiliyor
  (`F2-kontrol.md` B-5). **`yana_alt_bosluk_mm` / `eklem_sinirlari.json` notu:** `tasarim/freecad/arayuz.py:178` hâlâ
  `yana_alt_bosluk_mm={0: 4.7, -2: 0.6, -3: 0.0}` diyor; `eklem_sinirlari()` (`arayuz.py:772-774`) bunu "5'te 0,77 mm; kabuk boşluğu 0'da 4,7 mm,
  −3'te temas" metniyle `kod/ortak/eklem_sinirlari.json`'a (`:20`, `:61`) yazıyor. Bugünkü 158 modelinde: S1 kaset kapağı teması 3,21°, tambur
  3,65°, mekanik durdurucu 4,30°, 5°'te dişe 0,344 mm. Yazılım tarafı eski metni "5°'in altında 8° pay var" diye okuyabilir (B-3).
- **Önerilen varsayılan:** a. "K40 · S2 kalibrasyonu ve sınır metni: Horn kol dişe dayalıyken (S2 = 4,3°) takılır. S2 5 komutunda dişle 0,3 mm
  sentil geçmeli, 0,4 geçmemeli; geçmiyorsa diş yüzü zımparalanır. Aynı adımda `arayuz.OMUZ['yana_alt_bosluk_mm']` ve `eklem_sinirlari()` 'neden'
  metni F2 ölçümüyle güncellenir (kaset 3,21°, tambur 3,65°, durdurucu 4,3°, 5°'te dişe 0,344 mm). `kod/ortak/eklem_sinirlari.json` sahibi
  yeniden üretir. `arayuz.py` değiştiği için bu, taramalı bir pakette yapılır." Yalnız öneri.
- **Bloke:** P6.1 (`arayuz.py:178` ve üreteç; zaten plana yazıldı), P7.1 montaj rehberi (S2 horn adımı ve sentil kontrolü), Efe'ye bilgi (`kod/`).
- **Durum:** açık.

## K41 · S1 yazılım aralığı: kod 0…160 ↔ CAD −45…135 (KT-F2-4 + F5 Ç2)
- **Soru:** Kodda omuz öne-arka (S1) 0…160 (`planlama/d158/servo-10-oneri.md:29, 81` Ç2), CAD ve `eklem_sinirlari.json` −45…135. Kod sınırı
  CAD'e çekilsin mi; S1 için mekanik durdurucu gerekli mi?
- **Seçenekler:**
  a) Kod S1 aralığı −45…135 (CAD ile aynı); mekanik durdurucu yok.
  b) a + S1 mekanik durdurucusu için ayrı tasarım paketi (kaset U'su yerine yük taşıyan pim/omuz).
  c) Kod 0…160 kalır.
- **Sayısal etki:** omuz parçaları hiçbir S1 açısında çarpışmıyor (S1 180→330 ve −60→−210, S2 5…120: temas yok; `F2-gunluk.md` S1 bölümü).
  Sınırı yalnız kablo U lopu belirliyor: U ucu ↔ cep teması S1 ≈ 140,2° (`planlama/adim2/S1-kaset.md` KZ1); c'de kod 160'a giderse ~20° aşar,
  kablo kasete sıkışır (kol ↔ kabuk çarpışması yok). Kodda −45…0 da kullanılamıyor.
- **Önerilen varsayılan:** a. "K41 · S1 yazılım aralığı: kod 0…160 → −45…135 (`eklem_sinirlari.json` zaten −45…135). Omuz parçaları hiçbir S1
  açısında çarpışmıyor; sınırı yalnız kablo U lopu belirliyor (≈ 140,2°'de kasete sıkışır). S1 için mekanik durdurucu istenirse ayrı tasarım
  paketi açılır. Sahibi `kod/`." F5 bulgusuyla tek karar. Yalnız öneri.
- **Bloke:** `kod/` eklem sınırları (Efe'nin alanı; pano #6 Ç2 ile aynı konu), P5.1 satır 0 ve 2.
- **Durum:** açık.

<!-- K42–K43: P4.3 baskı listesi + P8.2 baskı partileri (F4c, 09.11.2026), kaynak `planlama/d158/F4c-gunluk.md` §7 KT-F4c-1…2, metinler B'nin
önerisiyle (`planlama/d158/F4c-kontrol.md` "Karar kuyruğuna girecek metin"; K43 B-1 düzeltmesiyle). -->

## K42 · PETG-CF miktarı: 1,5 kg yetmiyor (KT-F4c-1)
- **Soru:** PETG-CF 3 × 0,5 kg (1,5 kg; `planlama/maliyet.json` `kalemler[109]`) parçalara ve kuponlara yetiyor mu, kaç makara alınsın?
- **Sayılar:** parçalar 1.158,0–1.215,8 g (`planlama/y2/Y2b-baski.json` `toplam.cf_g`; 12 tür, 18 adet, VESA taşıyıcı 113 g dahil). Parti 0
  CF kuponları 175,8–301,4 g (`planlama/d158/F4c-partiler.json` `partiler.0.toplam.cf_g`). Toplam 1.333,8–1.517,2 g. 1,5 kg'de pay +166 … −17 g;
  D2 kuponu basılmazsa +69 … +208 g. En büyük CF parçası kafa servo yuvası 151,5 g: tek başarısız baskı alt durumdaki payı bitiriyor. VESA
  taşıyıcının destek malzemesi (28 katman) sayılmadı.
- **Seçenekler:** a) +1 makara (2,0 kg; pay 483–666 g). b) 1,5 kg'de kal; D2 basılmaz, başarısızlıkta yeniden sipariş (gecikme riski).
  c) K34 (baskı hizmeti) netleşince karar ver.
- **Sayısal etki:** a: +1.114,03 TL (`kalemler[109]` birim fiyatı, 11 Ekim; stok yeniden doğrulanmadı); %15 payla +1.281,13 TL. b: 0 TL.
- **Ayrıca netleşmeli:** `F8a-siparis.md:78` "filament firma ve ekipten, satın alınmaz", ama `maliyet.json` filamenti V3 toplamında sayıyor
  (`secenek` "yazici"). VESA taşıyıcının PETG-CF olması modelde (`kabuk_parcalar.py:375-376`), Ahmet'in kararına dayanmıyor (F4c-kontrol B-5).
- **F6b notu (P6.2, 09.11.2026; `planlama/d158/F6b-gunluk.md` §6 KT-F6b-1, B'nin hesabıyla `F6b-kontrol.md` madde 5d):**
  - Tek analiz (`tasarim/freecad/lale158/baski-analiz.json`) destek filamentini her parçada sayıyor. PETG-CF parçalar 1.194,0–1.251,8 g
    (`planlama/y2/Y2b-baski.json` `toplam.cf_g`; +35,8 / +36,0 g, çoğu VESA taşıyıcı desteği 31,7 g). Kuponla birlikte 1.369,8–1.553,2 g,
    yani **1,37–1,55 kg**. 1,5 kg'a göre pay **+130 / −53 g** (önce +166 / −17). Yukarıdaki "VESA desteği sayılmadı" cümlesi bununla karşılandı.
  - Tam doluluk senaryosu (bütün PETG-CF parçalara omuzdaki 0,8–0,9 aralığı; bugün yalnız omuz): CF üst sınırı **+66,1 g**
    (`baski-analiz.json` `parca_g` × 0,125), üst pay −119 g.
  - **a seçeneği (+1 makara, 2,0 kg) yine yetiyor:** pay ≥ **446,8 g** (1.500 + 500 − 1.553,2). CF desteği 91,9 g ±%50 tahmin
    belirsizliğinde de pay ≥ 400 g. Önerilen varsayılan değişmedi.
- **Önerilen varsayılan:** a. Yalnız öneri.
- **Bloke:** S siparişindeki filament satırı; Parti 0 CF kuponları ve Parti 2.
- **Durum:** açık.

## K43 · Isıl gömme somun adedi (KT-F4c-2, F4c-kontrol B-1 düzeltmesiyle)
- **Soru:** Erken alımda (K29) kaç M3 ve M5 ısıl gömme somun alınsın?
- **Sayılar:** model (`tasarim/freecad/montaj/robot-bom.csv`, 09.11) **M3 159, M5 5**. M5'lerin yeri: ön kol gövdesi ×2 (**PETG**,
  `dirsek_parcalar.py:235, 253`), eğme çatalı ×1 (PETG-CF), omuz göbeği ×2 (PETG-CF). Kuponlar iki malzemede basılıyor: B (M3 4, M5 3) ve C
  (M3 5, M5 5) → M3 18, M5 16 (`tasarim/freecad/test/tolerans_kuponu.py:8-9`, `m7-kupon-sonuc.json` `kupon_c_delikler`). Gereken (pay hariç):
  **M3 177, M5 21**. M5 yalnız C kuponu PETG'de denenirse 18.
- **Plan:** M3 168 (`maliyet.json`) / 176 (v4), M5 6. M3 kupona yetmiyor (−9); M5 modele ve kupona yetmiyor (−15).
- **Sayısal etki (taban fiyat, `F8a-siparis.md` §4.1):** M3 168 → 177: +9 × 5,29 = +47,61 TL. M5 6 → 21: +15 × 6,35 = +95,25 TL.
- **Önerilen varsayılan:** erken alımda M3 177 + pay, M5 21 + pay (pay oranı Ahmet'in). K31'in M3 varyantı (A/B/C) adedi değiştirmez; K31 M5 ürünü
  seçilmeden M5 alınmamalı (kupon delikleri Rhino M5 için küçük). Yalnız öneri.
- **İlişki:** K29'un önerisindeki "insert 168" bu maddeyle M3 177 + pay olur; K31 ürün seçimini, K43 adedi belirler.
- **Bloke:** K29 (erken alım), K31, Parti 0 kupon B/C.
- **Durum:** açık.

<!-- K44–K45: P6.1 + P4.5 kalanı (F6a, 09.11.2026), kaynak `planlama/d158/F6a-gunluk.md` §4 KT-F6a-1…2, sayılar B'nin bağımsız hesabıyla
(`planlama/d158/F6a-kontrol.md` O-2, madde 5, D-2). -->

## K44 · `eklem_sinirlari.json`'un `kod/`'a yazılması (KT-F6a-1)
- **Soru:** F6a `arayuz.py`'deki S2 sınır metnini ve `yana_alt_bosluk_mm`'yi 158 modeline göre güncelledi. `kod/ortak/eklem_sinirlari.json`
  bu yüzden eski (`py -3 kod/ortak/eklem_sinirlari_uret.py --kontrol` → "ESKI ya da yok", çıkış 1). Yeni içerik `kod/`'a yazılsın mı, kim yazsın?
- **Kaynak:** öneri dosyası `planlama/d158/F6a-eklem_sinirlari-oneri.json`. Üreticinin `uret()` çıktısıyla bayt bayt aynı, 6133 bayt (`F6a-kontrol.md` madde 5).
- **Fark (eski ↔ öneri, `F6a-gunluk.md` §1g):**
  - Sayısal sınır farkı **yok** (`min`/`max`, `bagimli`, `kafa_kol_yasak`, `teker.ivme_sinir_m_s2` aynı).
  - `r_s2` / `l_s2` `neden` metni: eski "kabuk boşluğu 0'da 4,7 mm, −3'te temas" yerine mekanik durdurucu 4,3°, 5°'te dişe 0,34 mm; durdurucusuz
    ilk temas S1 tamburu 3,65°, kaset kapağı 3,21°.
  - `bosluk_mm` {"0": 4.7, "-2": 0.6, "-3": 0.0} → {"5": 0.34, "4.3": 0.0}. Anahtar adı aynı, **anlamı değişti**: eski kol ↔ kabuk, yeni kol çatalı
    ↔ durdurucu dişi (D-2). `kod/` içinde bu alanı okuyan betik yok.
  - Yeni alan `temas_derece` {"durdurucu": 4.3, "s1_tambur": 3.65, "s1_kaset_kapagi": 3.21}.
  - `teker.not_` içinde takma ad "Ahmet" ile değişiyor.
- **Seçenekler:**
  a) Ahmet onayıyla `py -3 kod/ortak/eklem_sinirlari_uret.py` koşulup `kod/`'a yazılır; Efe'ye pano bilgisi gider (S2 alt sınırı +5 aynı,
     gerekçe artık durdurucu 4,3°; `bosluk_mm` anahtarlarının anlamı değişti).
  b) Efe'ye bırakılır: üretimi `kod/` sahibi kendi takviminde yapar; öneri dosyası o zamana kadar `planlama/d158/` altında durur.
- **Not:** `kod/` dosyası yenilenene kadar takma ad herkese açık dalda (`kod/ortak/eklem_sinirlari.json` teker notu) durur; P4.5 kabul ölçütü
  bu dosya için ancak üretimden sonra sağlanır. `planlama/adim2/K2-regresyon.py`, `K3-regresyon.py` JSON ↔ üretici eşitliğini denetler; üretime kadar
  "eşit değil" derler.
- **Önerilen varsayılan:** a. Yalnız öneri.
- **Bloke:** `kod/ortak/eklem_sinirlari.json` güncelliği, P4.5'in `kod/` kalanı, K2/K3 regresyon betikleri.
- **Durum:** açık.

## K45 · S2 darbe hız sınırı (KT-F6a-2; K38'i sayısallaştırır)
- **Soru:** Kök yayından (r 1,5, K_t 1,45) sonra S2 durdurucuya yaklaşırken hangi açısal hız sınırı yazılsın?
- **Sayılar** (`F6a-gunluk.md` §1d ve §9 tablosu; B'nin bağımsız hesabıyla aynı, `F6a-kontrol.md` O-2):
  - F2 rijitlik varsayımında (k_lin = k_diş/2, kol esnek) emniyet 2 için ≤ **59°/s** yüksüz, ≤ **30°/s** 500 g yükte.
  - Rijit uçta (k_lin = k_diş, kol rijit) emniyet 2 için **27 / 14°/s** gerekiyor; 59 / 30°/s'de emniyet **1,14** (500 g ile 1,15). Esnek uçta 59 / 30°/s'de 2,13 / 2,14.
  - Yük temas şeridinin ucuna kayarsa F2 rijitliğinde emniyet 2 için ≈ 40 / 20°/s.
  - Güç kesikken (servo torku yok) düşme sınırı: emniyet 2'de S2 ≤ **15,5°**, emniyet 1,5'te ≤ **20,4°** (F2 rijitliği; rijitte 8,1° / 10,2°).
  - K_t'li emniyet: stall 2,57; 1,5 rad/s yüksüz 1,54; 500 g ile 0,91; kaçak servo ve 30°'den yüksek güç kesik düşme < 1. Keskin köşeli F2
    geometrisine göre (K_t 2,73…3,64; stall 1,0–1,4) iyileşme; "3,73 → 2,57 düştü" diye okunmamalı.
- **K38 ile ilişkisi:** K38'in "S2 < 20°'de ≤ 60°/s (yüklü ≤ 30°/s)" önerisini sayısallaştırır. Bu sınır yalnız F2 rijitlik varsayımında emniyet ≈ 2;
  rijit alt sınırda ≈ 1,15. K38'deki "kapanmada S2 ≤ 15°" güç kesik düşme sınırıyla (15,5°) uyumlu.
- **Seçenekler:**
  a) Tutucu: 27 / 14°/s (rijit uçta da emniyet 2).
  b) 59 / 30°/s (K38 a) ve rijitlik ölçümü; ölçüm rijit uca yakın çıkarsa sınır düşürülür.
  c) Karar baskı kuponu testine kadar beklesin (kök yayı baskıda ve K39 DS3235 düşme ölçümü).
- **Önerilen varsayılan:** kayıtta yok; A'nın taslağı a ile b arasında bırakıyor. Kaçak servo ve güç kesik düşme için mekanik çözüm (yumuşak
  durdurucu / sönüm) K39'da.
- **Bloke:** K38, `kod/` hareket planlayıcısı (Efe'nin alanı), K39 ölçümünün yorumu.
- **Durum:** açık.

<!-- K46: P6.2 tek baskı analizi (F6b, 09.11.2026), kaynak `planlama/d158/F6b-gunluk.md` §5 ve §6 KT-F6b-3, e seçeneği B'nin düzeltmesiyle
(`planlama/d158/F6b-kontrol.md` O-1; a–d madde 6b). -->

## K46 · Destek azaltma geometri önerileri (KT-F6b-3)
- **Soru:** Destek oranı en yüksek parçalarda geometri ya da baskı yönü değiştirilerek destek azaltılsın mı; ne zaman?
- **Sayılar** (`tasarim/freecad/lale158/baski-analiz.json` `parcalar[]`, tasarım yönü, 45° eşik; destek g = destek hacmi × 0,15 × 1,27, tahmini):
  toplam destek 124,5 g (9 tür / 13 adet). VESA taşıyıcı 31,7 g (destek oranı %21,9), omuz yuvası 2 × 11,5 g (%14,1), kol çatalı 2 × 12,7 g
  (%12,7), omuz göbeği 2 × 5,9 g (%9,3), göğüs bandı sağ / sol 15,6 / 14,1 g (%6,7 / %6,1).
- **Seçenekler:**
  a) VESA taşıyıcının arka flanşı altına 45° kaburga (≈ 26 g PETG-CF).
  b) Omuz yuvasında manşon içi tavanına 45° kemer / damla (≈ 2 × 9 g PETG-CF).
  c) Kol çatalında horn kulağı altına 45° kaburga (≈ 2 × 10 g PETG-CF).
  d) Omuz göbeği −Y baskı yönü: destek 5,9 → 2,8 g, tabla teması 1.153 → 1.070 mm²; ama horn ekseni katman düzlemine yatar. Kupon / K39
     ölçümünden sonra.
  e) Göğüs bandı: geometri önerisi yok. Cep tavanı 2,8 mm, altında 207 mm boşluk, 148–160 mm açık uçlu açıklık; pah ya da kemer taşımaz.
     (i) destek kalsın (dilimleyicide yalnız bu bölgeye boyalı destek) ya da (ii) yatık baskı (±X, 1,6 g; yüzey ve bant tutarlılığı bozulur).
- **Sayısal etki:** a–c birlikte ≈ 64 g destek düşüşü, hepsi PETG-CF (K42 payına ≈ +64 g). e için tasarruf tahmini yok. Destek g tahmini
  ±%50 belirsiz; dilimleyici esastır (göğüs bantlarında ızgara duyarlılığı ≈ +%15, `F6b-gunluk.md` §7 açık 7).
- **Not:** a–c geometri değişikliğidir ve tarama kaynaklarını değiştirir (`tasarim/freecad/kabuk/kabuk_parcalar.py`,
  `tasarim/freecad/omuz/omuz_parcalar.py` / `omuz_lib.py`; `carpisma_kos.kaynak_listesi()`). Uygulanırsa tam tarama gerekir. d yalnız
  baskı yönü; geometri değişmez.
- **Önerilen varsayılan:** şimdilik değişiklik yok; Parti 0 kuponundan sonra karar. Yalnız öneri.
- **Bloke:** Parti 1 (göğüs bantları, VESA) ve Parti 2 (omuz PETG-CF) dilimleme ayarı; K42 payı.
- **Durum:** açık.

---

## Karar değil, iş (kuyruğa alınmadı)
- Kapak baskı analizinde iki sonuç (19.667,7 mm² ↔ 5,01 mm², `KY/uygulama-notu.md:68`): P6.2. F6b'de kapandı (aşağıda).
- `elektrik.md` boyun/hub satırları ve baskı listesi yeni düzene (`KY/uygulama-notu.md:153`): P4.1, P4.3.
- K7 perçin delik çapı ve perçin somun ölçüleri (`Y3-kontrol.md:115`): ölçüm, P8.3.
- Ölçülmesi gerekenler (akustik, yankı, hub girişi gerilimi; `KY/secenekler.md:248-254`): P8.3.
- F6a (09.11.2026), kapandı:
  - KT-F6a-3: omuz ve iskelet regresyon referansları (`tasarim/freecad/omuz/regresyon/once.json`, `iskelet/regresyon/once.json`) C'de
    `planlama/d158/F6a-regresyon-oneri/` önerileriyle yenilendi (md5 aynı; B her farkı bir değişikliğe bağladı).
  - KT-F6a-4: F4c betikleri (`F4c-dogrula.py` `YAMA = []`, K39 şablonları) düzeltme 1'de uyarlandı; `F4c-dogrula.py` çıkış 0.
  - KT-F6a-5: `montaj_gorsel.py` yasak kutu koruması düzeltme 1'de eklendi; kadraj ve poz tilt'i düzeltme 2'de.
- F6a'dan açık iş:
  - Göğüs ekranı port girintisi: ekran ölçülünce (`arayuz.GOGUS_EKRAN["port"]`, kasa girintisi, `lale158_kontrol` hariç tutma kutusu birlikte).
  - `montaj-hareket.gif` ve 5 GUI ekran görüntüsü (`montaj-gui-*.png`) yenilenmedi (D-10).
  - Dilimleyicide kök yayı önizlemesi (r 1,5 yayın katman çözünürlüğü, diş tabanı desteği) baskıdan önce.
- F6b (09.11.2026), kapandı:
  - Kapaktaki iki sonuç: üst arka servis kapağı baskı yönüne 2,27° eğik, flanş üstü z 1,4988. `kabuk_montaj`'ın z 1,5 kesiti bu yüze teğet
    düşüyor, ters normalli yüz üretiyor ve sahte 19.667,7 mm² veriyor. Gerçek fark 5,01 mm², 45° payı içinde; destek 0
    (`planlama/d158/F6b-gunluk.md` §2, B'nin FreeCAD ölçümü `F6b-kontrol.md` madde 2).
- F6b'den açık iş:
  - KT-F6b-2 (seçenek b şimdi): modül JSON'larındaki eski `baski` alanları zincir dışında; belgelerde "eski, zincir dışı" diye
    işaretli (bu madde, `F6b-gunluk.md` §6), JSON'ların kendisine dokunulmadı. `kabuk-analiz.json` kapak değeri
    (`baski[13]`, 19.667,7 mm²) hatalı. Bir sonraki geometri işinde modül betikleri tek analize (`baski_analiz_ortak.py`) yönlendirilecek.
    Bu alanı okuyan betikler: `tasarim/freecad/kabuk/kabuk_rapor.py:128`, `tasarim/freecad/dirsek/dirsek_rapor.py:93`,
    `planlama/adim5/baski_toplam.py:16`, `planlama/d158/F4c-kontrol-sayim.py:37`.
  - (C ölçümü) `baski-analiz.json` `parcalar[].malzeme` 6 türde (kafa servo yuvası, rulman yuvası, boyun mili, eğme çatalı; dirsek çatalı,
    bilek flanşı; 8 adet, 458,4 g) "PETG" diyor; etiket modül `*_parcalar.py` `malzeme` alanından geliyor. Zincir PETG-CF ayrımını
    `planlama/y2/Y2b-baski.py` `CF` kümesinden (12 tür / 18 adet) alıyor; liste ve toplamlar doğru. JSON'u tek başına okuyan CF'yi
    735,6–793,4 g sanar. Aynı geometri işinde etiket tek kaynağa bağlanmalı.
