# F10c günlüğü: rehber sıra düzeltmeleri + kalıcı sıra denetimi (P10.3), 11.11.2026

Brief: `planlama/d158/F10c-brief.md`. Dal `lale-duzeltme`, başlangıç `ada0b87`. Commit / push yok. Orkestratörün sıra kontrolü
notu, betikleri ve sanal ortamı scratchpad'de (salt okunur); bu paketin geçici dosyaları da scratchpad'de. Depoya scratchpad ya da
sanal ortam yolu yazılmadı.

## Özet

| Kabul ölçütü | Sonuç |
| --- | --- |
| 50/50, konsol 0 | 50/50, konsol 0 |
| Parça 1192 ↔ 1192 | 1192 ↔ 1192; parça alanlarında fark 0 (adım `a`, bağlanma `b`, tezgâh `t`, eksen `u` aynı). **Taşınan parça yok** (E3 karara kaldı, aşağıda) (düzeltme turu 1'de düzeltildi, bkz. D1: 5 parça taşındı) |
| Denetim 0 | ASCII kalıntı 0, gruplama 0, çelişki 0, zorunlu uyarı eksik 0 / 40 |
| Sıra denetimi "ulaşılamaz" 0 | **0** (önce 18 bu modelle; brief'teki "önce 4" yalnız tabla cıvataları, fark aşağıda) (düzeltme turu 1'de düzeltildi, bkz. D3: 4 gerçek + 11 yapay + 3 veri eki) |
| Bilinen kapalı örnek sınaması | geçti (5/5 sınama) (düzeltme turu 1'de düzeltildi, bkz. D3: yalnız 20 mm el payında geçiyor) |
| E3'te kafa en az bir yönden serbest | **KALDI / karar gerekiyor**: hiçbir sırada serbest değil (ölçüldü, aşağıda) (düzeltme turu 1'de düzeltildi, bkz. D1: P1 sırasıyla +y serbest) |
| Perdelenme tablosu 50 adım | yazıldı (`kontrol.json` "perdelenme", 50 satır; toplam tamamen gizli 290) |
| F10a-dogrula | depodaki betik HEAD'e bağlı, doğrudan koşu çıkış 1 (önceden var olan sorun). Kopyası (önce = `749627b~1`): bütün F10a ölçütleri geçti; yalnız "veri değişmedi" ölçütü tanım gereği kaldı (§9) (düzeltme turu 1'de düzeltildi, bkz. D4) |
| F9b-dogrula 0 | 0 (GECER) |
| carpisma_kos kontrol 0 | 0 |
| regresyon 10/10 | 10/10 GEÇER |
| PDF sayfa / en küçük yazı | önce 54 sayfa, 8,1 pt; sonra 55 sayfa, 8,1 pt (devam sayfası 4 → 5: K1 iki sayfaya çıktı) |
| Model değişmedi | `tasarim/freecad/` altında benim değişikliğim yalnız `rehber/` (diğer satırlar önceden vardı, aşağıda) |

## Komutlar ve çıkış kodları

| Komut | Çıkış | Not |
| --- | --- | --- |
| scratchpad: önce koşusu `rehber_sira.py` (eski veri) | 1 | ulaşılamaz 18, sınama geçti, 122 s |
| scratchpad: E4 aday sıraları (C0…C6, el 20 / 15 / 12) | 0 | tablo aşağıda |
| scratchpad: E3 yerleşim (orkestratör yerlesim betiği, tol 0,05 mm) V0–V5, V8–V9, V10 | 0 | V6 / V7 zamanında bitmedi (146 yönlük koşu durduruldu, 26 yönlük koşu 590 s sınırında V6'ya gelmeden kesildi) |
| `FREECAD-KILIT.txt` ← "F10c (ajan A) … 03:18 başladı" | – | boş bellek 2,74 GB, FreeCAD süreci yok |
| `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` | 0 | 9 dk 57 s toplam (veri 23 s, sıra + perdelenme 136 s) |
| `FREECAD-KILIT.txt` ← "boş" | – | |
| `py -3 -X utf8 planlama/d158/F10a-dogrula.py` | 1 | `AssertionError: HEAD kopyası yamanamadı` (aşağıda) |
| scratchpad kopyası: F10a-dogrula, "önce" = `749627b~1`, çıktı scratchpad'e | 2 | yalnız `veri_degismedi` kaldı (beklenen); öbür ölçütler geçti |
| `py -3 -X utf8 planlama/d158/F9b-dogrula.py` | 0 | GECER (hata 0) |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | 17 dosya özeti kayıtla aynı |
| `py -3 planlama/d158/regresyon.py --yazma` | 0 | 10/10 aynı |
| headless Chrome: adım 31 `patlat=1&tak=0,1,2,3,4,7,9` | 0 | `F10c-goruntu-31-tak-*.png` |

## 1. E4 (adım 31) sırası

Model: `rehber_sira.py` (aşağıda §7). Engel = önceki adımlar + adım içi önceki gruplar + grubun kendisi; "masada" grubu yalnız kendi
parçalarıyla ölçülür, sonra sıradaki yerinde robota bağlanır. Sınıf: DUZ / L / ... ulaşılır, YOK ulaşılamaz.

| Aday | Sıra | El 20 mm | El 15 mm | El 12 mm |
| --- | --- | --- | --- | --- |
| C0 (bugünkü) | yüz kabuğu + kamera + QLED → arka kabuk + ses → tabla | tabla 4 YOK, tırnak 4 YOK, kamera 4 YOK, dizi 3 YOK | tabla 4 L, dizi 1 YOK | hepsi ulaşılır (boyun sızıntısı: el 12 mm'de boyun açıklığından içeri giriyor, gerçekçi değil) |
| C1 (orkestratör önerisi) | arka kabuk robotta → tabla → yüz masada | tabla 4 L, dizi 2 YOK | – | – |
| C3 | yarım kabuk (sağ / sol ayrı) | sol tabla 2 YOK | – | – |
| C4 | yüz kabuğu robotta, sonra içi | tırnak 4 YOK, kamera 4 YOK | – | – |
| **C5 (seçilen)** | **masada arka kabuk + ReSpeaker + ses kartı + PAM → tabla cıvataları → masada yüz kabuğu + kamera + QLED + tırnak → kablolar → dikiş** | **hepsi ulaşılır** (tabla 4 L) | **hepsi ulaşılır** | **hepsi ulaşılır** |

C5 tabla cıvataları: L alyan, alet yolu 63,5 mm boş, L tutacağına el payı 15 mm (dört cıvata); düz alyanla el payı yalnız biri için
20,5 mm (el 20), el 15'te 14,5 / 32,5, el 12'de dördü 11,5 mm (düzeltme turu 1'de düzeltildi, bkz. D3: bunlar el payı değil, el bölgesine ulaşılan uzaklık; 15 mm örnekleme başlangıcı). Seçimin nedeni: orkestratörün önerisi (C1) tabla cıvatalarını açıyor
ama ReSpeaker'ın tavan vidaları (dizi vidası) kabuk kafadayken kapanıyor; ReSpeaker'ı masada vidalamak bunu çözüyor.

Üretimden sonra (gerçek veri): E4 24 bağlantı → DUZ 20, L 4; ulaşılamaz 0. Sıralı takma: `tak` sırası 1 arka kabuk, 2 köpük bant,
3 ses kartı, 4 PAM8403, 5 ReSpeaker, 6 dizi vidası, 7 tabla cıvatası M3×10 ×4, …, 9 yüz kabuğu (karelere bakıldı:
`F10c-goruntu-31-tak-0/1/2/3/4/7/9.png`; 7. karede tabla cıvataları yüz kabuğu daha patlak konumdayken seçili, 9. karede yüz kabuğu).

Satır sırası (`rehber-veri.json` adım 31 `sira_grup`):
1. Masada: arka kabuklar + ReSpeaker, ses kartı, PAM8403 (tezgâh): p:0–p:4, b:0
2. Tabla → arka kabuk rafı cıvataları: b:1, b:2
3. Masada: yüz kabuğu + kamera + QLED ve tırnaklar (tezgâh): p:5–p:10, b:3–b:5
4. Kabuk dikişi: b:6–b:8

F10a-dogrula'nın "üçüncü satır" sınaması (adım 31 `sat[2]`) artık "USB ses kartı" satırını kullanıyor (önce yüz ekranıydı).

## 2. E3 (adım 30): karar gerekiyor, uygulanmadı (düzeltme turu 1'de düzeltildi, bkz. D1)

CAD verisi doğrulandı: 625ZZ iki parça (`p0733` iç bilezik, E2 adım 28, tilt servosuyla; `p0832` dış bilezik, E3a adım 29, kafayla).
Pim M5×12 `p0735` + pul `p0734` E2'de; pim çataldaki M5 ısıl gömmeye (`p0736`) girer. Eğme çatalı `p0718` (E2c, adım 27) kafa
yanaklarının arasında kalıyor; tilt hornu `p0830` kafa tarafında (E3a).

Ölçüm: orkestratörün yerleşim betiği (süpürme, tol 0,05 mm; scratchpad), "serbest" = 400 mm boyunca engelsiz.

| Varyant | Hareketli | Engel | Yön | En iyi |
| --- | --- | --- | --- | --- |
| V0 bugünkü sıra | kafa (E3a) | E2'ye kadar her şey | 7 | 1,5 mm (+Y) |
| V1 pim + pul E3'e | kafa | – pim | 7 | 2,3 mm |
| V2 pim + pul + iç bilezik E3'e | kafa | – pim, iç bilezik | 7 | 6,8 mm (−Z) |
| V3 iç bilezik kafayla | kafa + iç bilezik | – pim | 7 | 1,8 mm |
| V4 tilt servosu da sonra | kafa | – pim, iç bilezik, servo | 7 | 13,0 mm (−X), engel eğme çatalı |
| V5 V4 + iç bilezik kafayla | kafa + iç bilezik | V4 gibi | 7 | 13,0 mm |
| V8 yalnız çatal | kafa | yalnız eğme çatalı | 26 | 28,2 mm, engel eğme çatalı (düzeltme turu 1'de düzeltildi, bkz. D1: temas yüzü çarpışma sayılmış; eşik 0,2 mm ile +y serbest) |
| V9 çatal + servo + horn servoda | kafa (hornsuz) | çatal, servo, horn | 26 | 1,8 mm, engel horn vidası |
| V10 kafa + çatal + servo + pim masada tek birim, saplama somunları sonra | kafa + çatal birimi | saplamalar, adaptör, mil | 6 (eksenler) | 8,3 mm (−Y, rulman yuvası); saplamalar birimin içinden geçiyor |

Sonuç: V8 belirleyici. Kafa yalnız eğme çatalına karşı bile 26 yönün hiçbirinden serbest girmiyor (en çok 28,2 mm): çatal ile kafa
yanakları geometrik olarak kilitli (düzeltme turu 1'de düzeltildi, bkz. D1: kilitli değil; kilit yalnız eksenel geçmelerde). 625ZZ / pim / servo / horn sırasını değiştirmek bunu açmaz; brief'teki "625ZZ + pimi E3'e taşı"
önerisi tek başına kafayı serbest bırakmıyor (V1, V2: 2,3 / 6,8 mm). Bu yüzden parça taşınmadı, E3 metni değişmedi.

Seçenekler (ölçülmedi, karar için) (düzeltme turu 1'de düzeltildi, bkz. D1: geometri kararı gerekmiyor, yalnız sıra; kalan karar sıfır boşluk, D1 karar kuyruğu önerisi):
- (a) Çatal yanaklarına ya da kafa yanaklarına açık kanal (kafa çatalın üstüne eksen yönünde iner): geometri değişikliği.
- (b) Eğme çatalını iki parça yap (kafa yanaklarının içinde birleşir): geometri değişikliği.
- (c) Kafa iskeletini yanak hizasından ikiye böl: geometri değişikliği, kabuk ve Pi yerleşimine dokunur.
- (d) Kafa + çatal + servo masada birim, birim saplamalara iner (V10): saplamalar birimin içinden geçtiği ve rulman yuvası engel
  olduğu için bu ölçümde de serbest değil; saplamanın sonradan takılması (yukarıdan) ayrıca ölçülmeli.

Önerim: (a) ya da (b) için CAD'de tek kesitlik deneme ve aynı süpürme ölçümü; karar Ahmet'te. Orkestratörün "≤ 1,5 mm" iddiası
ölçümle tutuyor (V0 1,5 mm).

## 3. K1 (adım 17) alt kat klemensleri → B3 (adım 9)

Ölçüm (orkestratörün kablo katmanı, scratchpad): kart üstünden elektronik katına 69 mm, yanda 40–150 mm. Kablo içeriği değişmedi.

| Yer | Önce | Sonra |
| --- | --- | --- |
| B3 `kablo` | "XL4016 giriş/çıkış klemensleri erişilebilir kalsın (17. adım K1)" (+ öbür satır) | 1) Alt kat klemensleri bu adımda bağlanır, üstü açıkken: iki BTS7960B güç girişi ve motor çıkışı (motor uçları B2b'de plaka üstüne alındı), XL4016 A / B / çevre giriş ve çıkış; B5 / B6'dan sonra el dar (69 mm, yanda 40–150 mm); akü ayrık. 2) Öbür ucu henüz yerinde olmayan hat: iki ucundan etiketle (kart, klemens, hat adı), K1'deki yerine yetecek boyda bırak, ucu bantla, kablo bağıyla demetleyip plaka üstünde topla, kat burçlarının (B4) ve kart üstlerinin yolunu kapatmasın; kaynakta yok, doğrulanmadı |
| B3 `kontrol` | – | + "BTS7960B ve XL4016 klemens uçları bağlandı, vidaları sıkı; boştaki uçlar etiketli ve bantlı (K1'de bağlanır)" |
| K1 `is_` madde 4 | "4. Motor + enkoder ve sonarları bağla. …" | Önüne paragraf: alt kat klemens uçları B3'te bağlandı, burada yalnız etiketli öbür uçlar bara / sigorta kutusu / hat sigortasına; alt kat klemensine uzanma (69 mm, 40–150 mm). "4. Enkoder ve sonarları bağla (motor uçları B3'te BTS7960B'ye bağlandı). …" |
| K1 `erisim` | "Kabuk yok; her yana düz erişim" | "Kabuk yok. Kat üstü açık (… el payı 6–9 mm). Alt kat kartlarının klemenslerine el dar: kart üstünden elektronik katına 69 mm, yanda raylara ve komşu karta 40–150 mm (…; ışınla, klemens yerleri modelde yok); o uçlar B3'te bağlanır" |
| K1 `kontrol` | – | + "B3'te bağlanan alt kat uçlarının etiketleri okunuyor; her biri K1'de öbür ucuna bağlandı, boşta uç kalmadı" |

## 4. F4 (adım 36): omuz yarığı

| Yer | Önce | Sonra |
| --- | --- | --- |
| `is_` | tek paragraf (bantlar) | "1." bantlar + "2. Kol servo uçlarını omuz yarığından dışarı al: K2'de travers arkasında bırakılan uzatma uçlarını, her omuzda ψ 214 yarığından (12 × 6) dışarı çıkar. Üst arka servis kapağı F5'e kadar açık … Dışarıda bekleyen uçlar G2'de (S2 eki göbekte) ve H1'de (dirsek, bilek) eklenir; G4'te demet aynı yarıktan içeri giden koşuyla kasete oturur. El yolu kaba ölçüm (10.11 sıra kontrolü: …0 mm, …6 mm), doğrulanmadı." |
| `kontrol` | 2 satır | + "Kol servo uzatma uçları iki omuzda da yarıktan dışarıda, etiketli; yarıkta ezilmiyor" |
| `kablo` | "S1 uçlarına erişim kalmalı: G4'te yarıktan girecekler" | "Geçit: ψ 214 yarığı. Travers arkasındaki kol servo uzatma uçları bu adımda yarıktan dışarı alınır (madde 2); G2, G4 ve H1 onları dışarıda kullanır" |

El yolu sayıları orkestratörün raporundan (muhtemel); bu pakette yeniden ölçülmedi, metinde "doğrulanmadı" yazıyor.

## 5. Tutmayan üç erişim iddiası

| Adım | Önce | Ölçüm | Sonra |
| --- | --- | --- | --- |
| K1 | "her yana düz erişim" | 69 mm / 40–150 mm | §3 |
| E4 `erisim` | "Düz. Kamera, tırnaklar ve QLED kabloları arka kabuk takılmadan kafanın içinden. …" | §1 | "Tabla cıvataları: L alyanla önden, yüz tarafı açıkken (alet yolu 63,5 mm boş; 4/4 ulaşılır, el payı 12, 15 ve 20 mm'de). Eski sırada (yüz kabuğu önce) 20 mm el payında 4/4 kapalı. ReSpeaker, kamera ve tırnak vidaları masada, kabuk açıkken düz; dikiş cıvataları dışarıdan düz (sıra denetimi). Servis arka kabuktan (…)" |
| E4 `is_` | sıra: yüz kabuğu → QLED → kablolar → arka kabuk → tabla | §1 | sıra: masada arka kabuk + ReSpeaker / ses / PAM → tabla (önden, L) → masada yüz kabuğu + kamera + QLED + tırnak → kablolar → dikişler |
| H0a `is_` | "Bilek somunu cepte; dirsek alt iki kulak cıvatası Ø8 erişim deliğinden, somunu cepte (Y3 C2)." | dirsek somunları 8 CEP; bilek somunları 8 ACIK_AGIZ_DAR (lokma yerel 16,4 mm sığıyor, tutacağına el yok; açık ağız 1 yön, el payı 25,5–36 mm (düzeltme turu 1'de düzeltildi, bkz. D3: açık ağzın el bölgesine uzaklığı)) | "Dirsek somunları cepte; … Bilek somunları cepte değil: 7 mm açık ağızla tek yönden tut (…, el payı 25,5–36 mm)." |
| H0a `erisim` | "Düz; somunlar cepte, dirsek alt kulaklar Ø8 delikten (Y3 C2)" | aynı | "Cıvatalar düz alyanla. Dirsek somunları cepte (8 somun), … Bilek somunları (8 somun) cepte değil: 7 mm açık ağız, tek yönden, dar (el payı 25,5–36 mm); lokmanın tutacağına el ulaşmıyor (sıra denetimi, 20 mm el)" |

## 6. B6 (adım 15): K53 notu

`not_` eklendi: "Bilinen açık konu (K53, karar bekliyor): modelde elektronik katı inerken ön şarj kartının iki ön naylon burcuna
takılıyor; burç katın ön kenarından 0,425 mm taşıyor (`planlama/d158/F10b-olcum.json`). Çözüm seçilmedi, ölçülmedi" (düzeltme turu 1'de düzeltildi, bkz. D3: seçenekler F10b'de ölçüldü). Sayı
`F10b-olcum.json`'dan: kat ön kenarı z 24,25, ön burçlar (1, 3) z üst 24,675 → 0,425 mm.

## 7. Kalıcı denetim: `rehber_sira.py` + `kontrol.json` "sira" / "perdelenme"

- Yeni modül `tasarim/freecad/rehber/rehber_sira.py` (FreeCAD'siz; `rehber/veri/rehber-veri.json` + `robot.glb`). Alet: bağlantı
  ekseninde ışın (DUZ / L / L_DAR / ACILI / YOK; somunda LOKMA / ACIK_AGIZ / CEP). El: 3 mm voksel, dışarıya bağlı ve engelden
  ≥ 20 mm bölge; aletin tutulacağı yer bu bölgeye değmeli. Adım içi sıra `sira_grup`'tan; kol pozu `poz`'dan (G4: S1 −45, S2 90).
- Üretim zinciri: `rehber_uret.py` 8. adım; `kontrol.json`'a iki alan. "sira": sınır `ulasilamaz` 0; aşılırsa ya da sınama
  kaçarsa `gecti: false` ve çıkış 2 (ek kontrol sorunlu: sira). "perdelenme": eşik yok, yalnız ölçüm (`gecti` hep true).
  Denetim çökerse "sira" `durum: hata`, `gecti: false`; üretim sürer.
- Bağımlılık: yeni yok. Yalnız numpy (depoda `tasarim/freecad/carpisma.py` zaten kullanıyor); scipy / trimesh gerekmez (mesafe
  dönüşümü ve bağlı bileşen numpy ile yazıldı, scipy ile karşılaştırıldı: fark 0). numpy yoksa iki alan da `durum: "atlandı"`,
  `gecti: true`, üretim kırılmaz.
- Süre (üretim koşusu): toplam 136,0 s = yükleme 17,8 + sıra 66,1 + perdelenme 52,2 s; voksel alanı 58, voksel 60,9 s.
  `--ek-yok` ile atlanır.
- Sınama (her koşuda):

| Sınama | Beklenen | Sonuç |
| --- | --- | --- |
| E3 yanak-horn cıvataları, kendi adımında | açık | DUZ 4, geçti |
| E3 yanak-horn cıvataları + E4 parçaları (bilinen kapalı) | kapalı | YOK 4, geçti |
| E4 tabla cıvataları, düzeltmeden önceki sıra (bütün E4 parçaları yerinde) | kapalı | YOK 4, geçti |
| A1 bağlantıları | açık | L 16, geçti |
| B1 bağlantıları | açık | DUZ 14, geçti |

- Sınıflar, önce → sonra (565 bağlantı): DUZ 456 → 469, L 36 → 39, ACIK_AGIZ 21 → 21, ACIK_AGIZ_DAR 9 → 9, CEP 14 → 14,
  LOKMA 11 → 11, POZA_BAGLI 0 → 2, **YOK 18 → 0** (düzeltme turu 1'de düzeltildi, bkz. D3: kırılım 4 + 11 + 3).
- "Önce 4" ile "önce 18" farkı: brief yalnız tabla cıvatalarını sayıyor. Bu model önce ayrıca E4 tırnak 4, kamera 4, dizi 3 (eski
  sıra), F3 taşıyıcı M6 1 (adım içi sıra yokken ekran ve çerçeve de yerinde sayılıyordu; F3 metnindeki sıra `sira` olarak eklendi:
  bant → taşıyıcı → ekran → çerçeve) ve G4 kaset cıvatası 2 (ev pozunda kapalı; G4 metnindeki S1 −45 / S2 90 `poz` olarak eklendi)
  buldu.
- Kalan dar / poz satırları (ulaşılır ama dikkat): E2c saplama somunu 1 (açık ağız, tek yön), H0a bilek somunları 8, G4 kaset 2
  (POZA_BAGLI: pozda ışın 110 mm boş; el katmanı pozda koşmuyor, yalnız ışın: bilinen kör nokta).
- Kör noktalar (modül başlığında da yazılı): alet tutacağına ulaşma tek tip el (20 mm) ile; kablo bağlantıları (klemens, fiş) alet
  isteyen bağlantı sayılmıyor; somun karşı anahtarı ile cıvata aynı anda ölçülmüyor; poz yalnız ışınla.

### Perdelenme tablosu (adımın sonunda hiçbir yönden görünmeyen yeni parçalar; eşik yok)

Tam liste (kimlik + ad) `planlama/rehber/kontrol.json` → `perdelenme.adim[].gizli_liste`; `sira_grup`'lu adımlarda grup başına da
(`grup[]`). Voksel 3 mm, 26 yönden dik izdüşüm.

| Adım | Kod | Yeni | Gizli | Parça | Bağlantı | Gizli parçalar (bağlantı elemanı dışı) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 | 0 | - |
| 1 | A1 | 29 | 8 | 0 | 8 | - |
| 2 | A2 | 15 | 2 | 0 | 2 | - |
| 3 | A3 | 15 | 2 | 0 | 2 | - |
| 4 | B1a | 46 | 2 | 0 | 2 | - |
| 5 | B1 | 28 | 10 | 0 | 10 | - |
| 6 | B2a | 28 | 0 | 0 | 0 | - |
| 7 | B2b | 20 | 0 | 0 | 0 | - |
| 8 | B2 | 16 | 2 | 0 | 2 | - |
| 9 | B3 | 28 | 0 | 0 | 0 | - |
| 10 | B4 | 24 | 2 | 0 | 2 | - |
| 11 | C0 | 30 | 6 | 0 | 6 | - |
| 12 | B5a | 39 | 0 | 0 | 0 | - |
| 13 | B5 | 8 | 0 | 0 | 0 | - |
| 14 | B6a | 80 | 0 | 0 | 0 | - |
| 15 | B6 | 8 | 0 | 0 | 0 | - |
| 16 | B7 | 14 | 4 | 0 | 4 | - |
| 17 | K1 | 0 | 0 | 0 | 0 | - |
| 18 | C1 | 48 | 9 | 0 | 9 | - |
| 19 | D1a | 22 | 0 | 0 | 0 | - |
| 20 | D1b | 20 | 8 | 0 | 8 | - |
| 21 | D1c | 4 | 0 | 0 | 0 | - |
| 22 | D1 | 16 | 8 | 0 | 8 | - |
| 23 | E1a | 27 | 10 | 0 | 10 | - |
| 24 | E1 | 6 | 0 | 0 | 0 | - |
| 25 | E2a | 2 | 0 | 0 | 0 | - |
| 26 | E2b | 7 | 0 | 0 | 0 | - |
| 27 | E2c | 18 | 8 | 0 | 8 | - |
| 28 | E2 | 14 | 1 | 0 | 1 | - |
| 29 | E3a | 23 | 3 | 3 | 0 | Köpük bant (5); Köpük bant (SY8205); Köpük bant (TVS) |
| 30 | E3 | 4 | 0 | 0 | 0 | - |
| 31 | E4 | 60 | 46 | 13 | 33 | USB ses kartı, PAM8403, ReSpeaker ve köpük bantları; 4 ekran tırnağı ve köpük bantları; kamera (tam liste kontrol.json'da). Grup sonunda gizli: masa arka 2 / 10, tabla 1 / 8, masa yüz 6 / 24, dikiş 7 / 18 |
| 32 | K2 | 0 | 0 | 0 | 0 | - |
| 33 | F1 | 61 | 21 | 0 | 21 | - |
| 34 | F2 | 87 | 30 | 0 | 30 | - |
| 35 | F3 | 54 | 23 | 0 | 23 | Grup sonunda gizli: bant 9 / 20, taşıyıcı 2 / 7, ekran 0 / 9, çerçeve 6 / 18 |
| 36 | F4 | 18 | 11 | 0 | 11 | - |
| 37 | G0 | 16 | 3 | 0 | 3 | - |
| 38 | G1 | 14 | 10 | 0 | 10 | - |
| 39 | G2 | 28 | 2 | 0 | 2 | - |
| 40 | G3 | 26 | 4 | 0 | 4 | - |
| 41 | G4 | 12 | 2 | 0 | 2 | - |
| 42 | H0a | 42 | 3 | 0 | 3 | - |
| 43 | H0b | 4 | 0 | 0 | 0 | - |
| 44 | H0c | 28 | 7 | 3 | 4 | 625ZZ rulman (iç bilezik) ×2; 625ZZ rulman (dış bilezik) |
| 45 | H0d | 4 | 0 | 0 | 0 | - |
| 46 | H0e | 10 | 0 | 0 | 0 | - |
| 47 | H0f | 10 | 6 | 0 | 6 | - |
| 48 | H1 | 16 | 1 | 0 | 1 | - |
| 49 | F5 | 50 | 36 | 2 | 34 | USB Hub 4'lü (kapak içi); Köpük bant (USB Hub kapak içi) |

Toplam 290 (önceki veride de 290; sıra değişikliği adım sonu durumunu değiştirmiyor).

## 8. Taşınan parçalar

Yok (düzeltme turu 1'de düzeltildi, bkz. D1: 5 parça taşındı, tablo orada). Adımlar arası parça taşıması yalnız E3 için düşünülmüştü (625ZZ iç bilezik + pim); ölçüm serbest giriş göstermediği için
uygulanmadı (§2). Değişen yalnız adım içi satır sırası (adım 31 ve 35: `parcalar` / `baglantilar` sırası, yeni `sira`,
`sira_grup`) ve adım 41 `poz`. Parça kaydı farkı 0 (1192 parçanın bütün alanları önce = sonra).

## 9. Kontroller

- Tarayıcı kontrolü: 50 adım, 50 geçti, konsol 0, her parça tek adımda: evet; telefon 7 adım taşma 0; yazdırma kareleri 50 / 50
  çizili (en düşük oran 0,0595).
- F10a-dogrula: depodaki betik "önce" sayfasını `HEAD`'den alıp F10a öncesi `index.html`'i (importmap) yamalıyor. F10a artık
  commit'te (`749627b`), `HEAD`'de importmap yok, betik ilk satırda `AssertionError: HEAD kopyası yamanamadı` ile çıkıyor (çıkış 1).
  Bu pakete bağlı değil. Ölçütleri yine görmek için betiğin scratchpad kopyası, "önce" = `749627b~1`, çıktı scratchpad'e:
  çıkış 2, 7 dk 44 s. Seçim 6/6 (adım 31: parça 7/7, panel 9/9), ek sınamalar (esc, önceki parça, şema, patlat_tak, kısayol,
  tak_kadraj) hepsi geçti; ağsız dış istek 0, konsol 0; kadraj ortancası 0,1733 → 0,4013, taşan 0 (F10a'daki değerle aynı);
  küçük görünüm 50/50 masaüstü, 50/50 360 px, taşma 0; CDN 0; yazdırma kareleri 50/50, PDF görüntü 50, boş sayfa 0. Kalan tek
  ölçüt `veri_degismedi` (KALDI); bu pakette tanım gereği false (veri yeniden üretildi). Yani F10a kabul ölçütlerinin hepsi geçiyor.
  `veri_degismedi` ölçütü bu pakette tanım gereği false (veri yeniden üretildi).
- F9b-dogrula: GECER (hata 0), çıkış 0. carpisma_kos kontrol: çıkış 0. Regresyon: 10/10 aynı, çıkış 0.
- PDF: önce 54 sayfa (devam 4: adım 31, 32, 35, 49), en küçük yazı 8,1 pt (DOM ve PDF); sonra 55 sayfa (devam 5: + adım 17 K1),
  8,1 / 8,1 pt, 5092 kB, eşleme tutarlı, taşan 0.

## 10. Görüntüler (kendim baktım)

`F10c-goruntu-once-NN.png` / `F10c-goruntu-sonra-NN.png` (NN = 09 B3, 15 B6, 17 K1, 30 E3, 31 E4, 36 F4): 3B sahne aynı (parça
taşınmadı); panelde 15'te K53 notu, 17'de yeni alt kat paragrafı, 36'da madde 2, 31'de yeni sıra metni görünüyor. 30 değişmedi
(E3 karara kaldı) (düzeltme turu 1'de düzeltildi, bkz. D6 görüntüler). B3 kablo satırları panelin kaydırılan kısmında (karede görünmüyor; veride ve PDF'te var).
`F10c-goruntu-31-tak-N.png`: sıralı takma yeni satır sırasını izliyor (§1).

## 11. Dokunulan dosyalar (commit listesi)

- `tasarim/freecad/rehber/rehber_sira.py` (yeni)
- `tasarim/freecad/rehber/rehber_metin.py` (B3, B6, K1, E4, F3 `sira`, F4, G4 `poz`, H0a; `sira_grup_bul`)
- `tasarim/freecad/rehber/rehber_veri.py` (adım içi sıra gruplarına göre satır dizme; `sira`, `sira_grup`, `poz` alanları)
- `tasarim/freecad/rehber/rehber_uret.py` (8. adım: sıra + perdelenme)
- `tasarim/freecad/rehber/rehber_denetim.py` (ASCII_TAMAM'a yeni metindeki 31 doğru Türkçe kelime)
- `rehber/app.js` (sıralı takma `st.sira` varsa onu izler; en küçük değişiklik, `siraKur`)
- Üretici çıktıları: `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js` (`robot.glb` / `robot-glb.js` bayt aynı),
  `planlama/rehber/kontrol.json`, `planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-15/17/31/36/42.png`,
  `planlama/rehber/goruntu/telefon-360-adim-31.png`
- `planlama/d158/F10c-gunluk.md`, `planlama/d158/F10c-goruntu-*.png` (19 dosya)
- `planlama/d158/FREECAD-KILIT.txt` (koşu sırasında satırım, sonra "boş"; dosya izlenmiyor)

## 12. Açık kalanlar

1. **E3 (karar)**: kafa eğme çatalına kilitli (§2); seçenek (a)–(d), geometri kararı. Kabul ölçütü "E3 serbest" karşılanmadı (düzeltme turu 1'de düzeltildi, bkz. D1).
2. E3 varyant V6 / V7 (horn servoda, 146 ve 26 yön) süre sınırında bitmedi; V8 sonucu bunları gereksiz kılıyor (çatal tek başına
   kilitliyor), ama ölçülmediler (düzeltme turu 1'de düzeltildi, bkz. D5: gereksiz).
3. F4 el yolu sayıları (0 mm / 6 mm) orkestratör raporundan, bu pakette yeniden ölçülmedi.
4. POZA_BAGLI yalnız ışınla ölçülüyor; pozda el katmanı yok.
5. F10a-dogrula betiği HEAD'e bağlı ve artık kırık (§9); düzeltmesi F10a-* dosyası olduğu için bu paketin yazma alanı dışında (düzeltme turu 1'de düzeltildi, bkz. D4).

## 13. Brief dışında fark edilenler (dokunulmadı)

- K2 metni arka kabuk dikişlerini K2'den sonra sıktırıyor; E4'te dikiş grubu ayrı ama E4 adımında duruyor (satırlar E4'te sayılıyor,
  iş K2'den sonra). Adım ayrımı F10d'nin konusu.
- S1 kablosunun kasete giriş anlatımı D1 / K2 / G4 arasında farklı sözcüklerle (travers arkası / yarık / kaset); F4 maddesi bunları
  bağladı ama D1 ve K2 metni yeniden okunmalı.
- `planlama/dongu-158.md` çalışma ağacında değişmiş (02:34, benim değil). `tasarim/freecad/montaj/yerlesim-kontrol.json`,
  `kabuk/gorsel/*.png` değişik; `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`,
  `tasarim/freecad/lale158/kafa-yerlesim/kaynak/` izlenmeyen: hepsi bu paketten önce / dışarıdan, dokunulmadı.
- `planlama/rehber/R-gunluk.md` bu pakette güncellenmedi.

## Düzeltme turu 1 (11.11.2026, kontrol `F10c-kontrol.md` "DÜZELTME GEREKLİ" üzerine)

Esas: çalışma ağacı, HEAD `ada0b87`, commit / push yok. Kontrolcünün betikleri ve E3 süpürme kaydı (`scratchpad/f10c-b/`) okundu,
depoya kopyalanmadı. Bu turun geçicileri `scratchpad/f10c-d1/`. Yukarıdaki metin silinmedi; tutmayan iddiaların yanına not düşüldü.

### D1. E3 (adım 30): kafa girişi, ölçüm ve sıra düzeltmesi

**Yöntem (yeni, kontrolcünün yönteminden bağımsız; `tasarim/freecad/rehber/rehber_giris.py`).** Her parça için üç eksende düzenli
ışın ızgarası (aralık h; ızgara h'nin 0,3713'ü kadar kaydırılmış, ışın yüzeyle aynı düzleme düşmesin). Kapalı mesh'te ışının giriş /
çıkış noktaları (parite) parçanın içinde kalan aralıkları verir. Hareketli küme son yerinden bir eksen yönünde h adımla çekilir; aynı
ışındaki hareketli ve engel aralıklarının kesişim boyu **eşik 0,2 mm**'den uzunsa çarpışma. Temas eden / aynı düzlemdeki yüzler ve
0,2 mm'den sığ dokunmalar çarpışma sayılmaz. "Serbest" = iki kümenin sınır kutuları ayrılana kadar çarpışma yok ve dinlenmede ortak
hacim yok. Tek sayıda kesişimli ışın o parça için düşürülür (E3 ızgarasında 11 ışın, E4'te 4). Veri: `robot.glb` (geometri değişmedi).

**Yöntem sağlaması** (yalnız eğme çatalı engel, kafa bugünkü hâliyle; `scratchpad/f10c-d1/e3_sag_h0.25.json`): −y 12,25 mm (kafa
iskeleti ↔ çatal, 10 mm derinlik), +x 1,0 mm, −x 13,0 mm (horn ↔ çatal): bilinen çarpışmalar yakalanıyor. Aynı küme **eşik 0** ile
(temas da çarpışma) +y'de 4,25 mm'de "çarpıyor", çarpan ışın 1, derinlik 0,00 mm: A'nın V8'deki "28,2 mm, kilitli" sonucu bu tür bir
temas sayımıydı (kontrolcünün tahminiyle aynı).

**Varyantlar, +y (kafa yukarı = iniş yolu), h 0,25 mm, eşik 0,2 mm** (`scratchpad/f10c-d1/e3_h0.25.json`, her varyanttan sonra diske
yazıldı):

| Varyant | Hareketli | Engel | +y | Çarpan (derinlik) |
| --- | --- | --- | --- | --- |
| V0 düzeltmeden önceki sıra | kafa (horn + horn vidası + dış bilezik) | E2'ye kadar her şey (iç bilezik, pim, pul dahil) | 0 mm | horn vidası ↔ servo mili (5,0 mm), horn ↔ servo mili (3,3 mm): eksenel geçme |
| V8 | kafa | yalnız eğme çatalı | **serbest** (31,5 mm'de kutular ayrılıyor) | – |
| **P1** | kafa − horn − horn vidası + 625ZZ iç bileziği (tek parça) | E2'ye kadar her şey − iç bilezik − pim − pul + horn (servoda, vidasız) | **serbest** (31,5 mm) | – ; dinlenmede ortak hacim 0 |
| P1b | P1 gibi | P1 + horn vidası servoda | 1,75 mm | kafa iskeleti ↔ horn vidası başı (3,0 mm) |
| P2 | kafa (horn kafada) + iç bilezik | pim, pul yok | 0 mm | horn ↔ servo mili |

P1 duyarlılık: eşik 0,05 / 0,1 / 0,2 / 0,3 mm ve h 0,2 mm'de de serbest; yalnız eşik 0 (temas çarpışma) 4,25 mm. P1 öbür yönler: +z
107 mm'de, −z 83,5 mm'de serbest (yanaklar çatalın yanından kayıyor); −y 12,25, ±x 0 mm. Kontrolcünün P1 hükmü tutuyor (B ↔ bu tur:
V0 0 / 0, P1 serbest / serbest, P1b 1 / 1,75 mm).

**Kafa indikten sonra alet ve parça yolu** (engel: E3 sonundaki her şey):
- Giriş yolu (`e3_p1_ayrinti.json`): pim + pul birlikte −x (sol yanak deliğinden dışarı) serbest, horn vidası +x (sağ yanak
  deliğinden) serbest, yanak-horn cıvataları (4) +x serbest; yanak-horn cıvataları ve horn vidası takılıyken de pim + pul serbest.
  Dinlenmede tek ortak hacim: yanak-horn cıvatası ↔ horn 3,0 mm (3 cıvata): hornun dişli deliği modelde yok, vida diş boyu.
- Sıra denetimi (üretimden sonra, gerçek veri, 20 mm el): pim M5×12 DUZ, alyan 4, alet yolu 130 mm boş, el bölgesine 20,5 mm'de;
  horn merkez vidası DUZ, PH1, 80 mm boş, 23,5 mm'de; yanak-horn 4 × DUZ, 110 mm, 19 mm. E2'deki 8 bağlantı (4 M4×16 DUZ, 4 kontra
  somun: 2 açık ağız, 2 cep) değişmedi.
- Yanak delikleri (mesh): sol delik r 6,5 pulu (r 5) ve pim başını geçiriyor; sağ delik r 4,5 horn vidası başını (r 2,75) geçiriyor.

**Ölçüler (mesh köşe koordinatları, tilt ekseni y 1478,88 / z 25 çevresi; `scratchpad/f10c-d1/olcu.py`):** sol yanak dış / iç
x −35,2 / −24,2; 625ZZ x −29,2…−24,2; çatal dayaması −24,2 (yanak iç yüzü ve 625ZZ iç bileziğiyle aynı düzlem), çatal kolu dış yüzü
−23,2; servo mili ucu ve horn dış yüzü 30,2; sağ yanak iç / dış 30,2 / 35,2. **Yanaklar arası 54,4 mm, yığın 54,4 mm: iki yanda
sıfır boşluk.**

**Taşınan parçalar (5; adım kimlikleri ve parça kimlikleri yeni veriden, `scratchpad/f10c-d1/karsilastir.log`):**

| Parça | Önce (a / b / tezgâh) | Sonra | Neden |
| --- | --- | --- | --- |
| `p0830` Tilt horn 25T alüminyum disk | E3a 29 / 30 / kafa | **E2 28** / 28 / – | servoya, merkez vidası olmadan (`kafa_rapor.py` SIRA 5: "horn servo ortasında") |
| `p0831` Tilt horn merkez vidası M3 | E3a 29 / 30 / kafa | **E3 30** / 30 / – | kafa indikten sonra sağ yanak deliğinden, PH1 (P1b: önce takılırsa kafa 1,75 mm'de takılıyor) |
| `p0733` 625ZZ rulman (iç bilezik) | E2 28 / 28 / – | **E3a 29** / 30 / kafa | dış bilezikle tek parça, sol yanağa pres (SIRA 6) |
| `p0734` Pim pulu M5 | E2 28 / 28 / – | **E3 30** / 30 / – | sol yanak deliğinden, kafa indikten sonra |
| `p0735` Pim cıvatası M5x12 | E2 28 / 28 / – | **E3 30** / 30 / – | aynı, alyan 4 |

Parça kaydı: 1192 ↔ 1192 (HEAD, A'nın üretimi ve bu tur: kimlik kümesi aynı). Alan farkı olan parça tam 5 (yukarıdakiler); farklı
alanlar `a`, `b`, `t`, uçuş yönü `u` / `ub` (yeni adımına göre yeniden hesaplandı). Her parça tek satırda, satırsız parça 0. `p0736`
M5 ısıl gömme (çatal) E2'de kaldı (baskıdan sonra takılı). Uygulama: `rehber_secici.py` E2 / E3 / E3a satırları (E2c'den sonra, E2'den
önce). Kalan görsel ayrıntı: hornun E2 patlatma yönü artık radyal (0,75, 0, 0,66), servo ekseni (+x) değil; değiştirilmedi.

**Metin (önce → sonra; `rehber_metin.py`):**
- E2 `is_`: "Tilt servosunu çatala cıvatala. Karşı yanağa 625ZZ ve M5 pimi tak." → 1. servo +X'ten U plakaya; 2. horn servo orta
  konumdayken mile, merkez vidası E3'te (burada takılırsa inen kafa vida başına takılıyor, ölçüldü); 625ZZ E3a'da, pim + pul E3'te.
  `baglanti_md` "…; 1 × M5×12 + pul" → "…; horn milde, merkez vidası E3'te". `kontrol` "pim sıkıyken 625ZZ dönüyor" E3'e taşındı.
- E3a madde 3: "Sol yanağa 625ZZ dış bileziği; tilt hornu … Hornun önce servoya mı yanağa mı takılacağı kaynakta yok, doğrulanmadı" →
  "625ZZ rulmanını sol yanağın yuvasına pres et (tek parça …). Tilt hornu bu adımda yok: E2'de servoya takıldı, kafa E3'te ona iner
  (`kafa_rapor.py`)". `baglanti_md` "horn 1 × M3×5" → "625ZZ pres geçme". (A'nın "kaynakta yok" iddiası yanlıştı: kaynak
  `tasarim/freecad/kafa/kafa_rapor.py` SIRA.)
- E3 `is_`: tek cümle → 1. kafayı yukarıdan indir (yanaklar çatalın iki yanından; 625ZZ iç bileziği çatal dayamasına, sağ yanak horna);
  2. horn merkez vidası sağ yanak deliğinden PH1; 3. 4 × M3×8; 4. pul + pim sol yanak deliğinden, alyan 4 (2 ile 3'ün sırası kaynakta
  yok). Yeni `baglanti_md`, `alet` ("alyan 2,5 ve 4, PH1"), `erisim` (130 / 80 mm alet yolu, giriş yolu), `kontrol` (+ pim / 625ZZ,
  horn vidası). Yeni `not_`: **"Bilinen açık konu: yanakların arası 54,4 mm, aradaki yığın (çatal dayaması + servo + horn) da 54,4 mm:
  kafa iki yanda sıfır boşlukla iner (modelde ortak hacim 0, yüzler temas ediyor). Baskı toleransında zorlamasız iniş ölçülmedi"**.

**Kalıcı denetim:** `kontrol.json` → `sira.giris`. Birim "E3 kafa alt montajı (E3a) → tilt hornu": hareketli 22, engel 610 parça,
serbest yön +y, +z, −z; `sira.giris.e3_kafa_serbest: true`. Sınama (her koşuda): düzeltmeden önceki E3 sırası +y kapalı (0 mm, horn vidası
↔ servo mili) geçti; yeni sıra +y açık geçti. Sıra denetimi sınaması 1 / 2 artık adım 30'un 6 bağlantısını içeriyor (yanak-horn 4 +
horn vidası + pim): kendi adımında DUZ 6, E4 parçalarıyla YOK 6.

#### Karar kuyruğu önerisi (`karar-kuyrugu.md`'ye kayıt ajanı işler; bu turda dokunulmadı)

> **K5x · E3 kafa inişinde sıfır boşluk (yanaklar arası 54,4 mm ↔ yığın 54,4 mm)**
> - **Soru:** Kafa iskeletinin iki yanağı arası 54,4 mm; aradaki yığın da 54,4 mm (sol: çatal dayaması ve 625ZZ iç bileziği
>   x −24,2, yanak iç yüzü −24,2; sağ: tilt hornu dış yüzü 30,2, yanak iç yüzü 30,2). Modelde kafa yukarıdan ortak hacimsiz iniyor
>   (yüzler temas ediyor; F10c düzeltme 1 giriş yolu ölçümü, eşik 0,2 mm). Baskı toleransında yanaklar zorlamadan inmeyebilir. Yanak iç
>   yüzlerine pay verilsin mi?
> - **Ölçüler:** tilt ekseni çevresinde yanak kalınlığı sol 11 mm (−35,2…−24,2; 625ZZ yuvası), sağ 5 mm (30,2…35,2); çatal kolu dış yüzü −23,2 (yanağa 1,0 mm, dayama
>   dışında); kafa yukarıdan 31,5 mm'de serbest, temas da çarpışma sayılırsa 4,25 mm'de duruyor (yani tek engel temas yüzleri).
> - **Seçenekler:**
>   a) Pay yok (bugünkü model). Baskı ölçüsü tutarsa iner; tutmazsa yanaklar elle açılarak (PETG esnemesi) indirilir: ölçülmedi.
>   b) Yanak iç yüzlerine 0,2–0,3 mm pay (her yanda). Geometri değişikliği: kafa çakışma taraması gerekir. Sağda 4 × M3×8 sıkılınca yanak
>      horna çekilir; solda pim sıkılınca 625ZZ iç bileziği dayamaya çekilir, rulmana eksenel yük ya da araya şim gerekebilir:
>      ölçülmedi.
>   c) İlk baskı kuponunda dene: yanak + çatal dayaması + horn kalınlığında kısa kupon basılır, iniş elle denenir; sonuca göre a ya da b.
> - **Öneri:** c (ucuz, kararı ölçüme bağlar); kupon zorlarsa b, b'nin sol yanak eksenel yük etkisi o zaman ölçülür. Karar Ahmet'te.

### D2. E4 (adım 31): C5 masa gruplarının robota giriş yolu

Yöntem D1'deki gibi; h 0,5 mm, eşik 0,2 mm, 12 yön (6 eksen + 6 çapraz). Engel: adım 31 başında robotta olanlar + o ana kadar takılan
gruplar. Kabuk dikişlerinin ve tabla rafının ısıl gömmeleri kabuklarla gelir, ölçüme hareketli ya da engel olarak girmedi (kabuk
duvarının içinde). Varyantlar tek tek, art arda koşuldu (tek süreç), her biri bitince `scratchpad/f10c-d1/e4_h0.5.json`'a yazıldı.

| Birim | Engel | Serbest yönler | Kapalı yönlerde ilk çarpan |
| --- | --- | --- | --- |
| A: sağ arka kabuk + ReSpeaker + 3 dizi vidası | adım 31 başı | **−z (arkadan)**, (+x, −z) çapraz | +y kafa iskeleti, +z kafa iskeleti, ±x Pi / rulman yuvası |
| B_A: sol arka kabuk + ses kartı + PAM8403 + 2 köpük bant | + A | **−x (soldan), −z (arkadan)**, (−x, −z) | +y kafa iskeleti; −y, +x, +z sağ arka kabuk |
| B: aynı, A yokken | adım 31 başı | −x, −z, (−x, −z) | – |
| **A_B: sağ arka kabuk, sol takılıyken** | + B | **hiçbiri** | −z ve −x sol arka kabuk (16 mm / 200 mm derinlik: dikey dikiş bindirmesi) |
| C: yüz grubu (yüz kabuğu sağ + sol, QLED, 4 tırnak + köpük + cıvata + ısıl gömme, kamera + 4 vida) | + A + B + 4 tabla cıvatası | **+z (önden)** | öbür yönler arka kabuklar |

Sonuç: C5'in üç grubu girer, ama **arka kabuklar ayrı iki birimdir ve sıra önemli: önce sağ, sonra sol.** Sol önce takılırsa sağ
hiçbir düz yönden girmiyor (dikey dikişte sağ kabuğun bindirmesi solun altında). Rehberde sıra buna göre düzeltildi:
- `rehber_metin.py` E4 `sira`: "Masada: arka kabuklar + ReSpeaker, ses kartı, PAM8403" grubu ikiye bölündü: "Masada: sağ arka kabuk +
  ReSpeaker" (p:0 sağ arka kabuk, p:1 ReSpeaker, b:0 dizi vidaları) → "Masada: sol arka kabuk + USB ses kartı, PAM8403" (p:2 sol arka
  kabuk, p:3 köpük bant, p:4 ses kartı, p:5 PAM8403) → tabla cıvataları (b:1, b:2) → yüz grubu (p:6–p:11, b:3–b:5) → dikiş (b:6–b:8).
  Panelde "Arka kafa kabuğu (sağ + sol)" satırı iki satır oldu (parça satırı 11 → 12); parça adım değiştirmedi.
- E4 `is_`: sıra cümlesi "sağ arka kabuk → sol arka kabuk → tabla → yüz → kablolar → dikişler"; madde 1 sağ ve sol ayrı; "Kabukları
  kafanın arkasına getir, önden bağla" → "Kabukları kafanın arkasında tut, kabloları kafanın açık ön tarafından tak"; "Önce sağ kabuğu
  arkadan (−z) yerine koy, sonra solu (arkadan ya da soldan) … (giriş yolu ölçümü)". Madde 4 sonu: "yüz kabuğunu önden (+z) yerine koy".
  Kontrolcünün dolambaçlı bulduğu cümle: "Yüz kabuğu takılıyken arka kabuklar kapanırsa" → "Yüz kabuğu önce takılırsa".
- E4 `erisim`: + "Giriş yolu: sağ arka kabuk arkadan, sol arka kabuk arkadan ya da soldan, yüz grubu önden serbest".

Kalıcı denetim: `sira.giris.birim`, sira_grup'taki her "tezgah" grubu için (E4'te 3 birim); sınama "E4 sağ arka kabuk, sol arka kabuk
takılıyken (yanlış sıra): kapalı" geçti. Sınır: girilemeyen birim 0 (aşılırsa `sira.gecti: false`, üretim çıkış 2). Üretimde: sağ arka
−z; sol −x, −z; yüz +z; girilemez 0. Kablo takma ("yüz kabuğu önde tutulurken") ve kablo boyu ölçülmedi (modelde yok).

`rehber_sira.py:402-405` "tezgah grubu yalnız kendi içinde ölçülür" kuralı (B-5) duruyor; grubun robota giriş yolu artık ayrıca ölçülüyor.

### D3. Dürüst sayılar ve adlar

- **"Ulaşılamaz 18 → 0" kırılımı** (B-4): 4 gerçek sıra düzeltmesi (E4 tabla cıvataları, C5 sırası) + 11 adım içi sırası tanımsız eski
  verinin yapaylığı (E4 tırnak 4, kamera 4, dizi vidası 3: `sira_grup` yokken E4'ün bütün parçaları engel sayılıyordu; eski metin de
  bunları kabuk kapanmadan yaptırıyordu) + 3 metinde zaten yazılı F3 sırasının (taşıyıcı M6 1) ve G4 pozunun (kaset cıvatası 2)
  veriye eklenmesi. `kontrol.json` `sira.aciklama` bu kırılımı yazıyor (`rehber_sira.py` `ACIKLAMA`). Rehber metninde "18" geçmiyor.
- **El payı duyarlılığı** (B-3): bilinen kapalı örnek sınamaları (E3 cıvataları + E4 parçaları; düzeltmeden önceki E4 sırasında tabla
  cıvataları) **yalnız 20 mm el payında geçiyor**. 15 ve 12 mm'de ikisi de ayırmıyor (E3 + E4: L 5, DUZ 1; eski E4 tabla: L 4): eski
  sıra da açık görünüyor (el boyun açıklığından sızıyor, 10.11 notu). C5'in eski sıraya üstünlüğü 20 mm el varsayımına dayanıyor.
  Görünürlük: `kontrol.json` `sira.sinama.sonuc[].el_mm` (20), `sira.sinama.duyarlilik` (15 / 12, `ayirdi: false`), `sira.sinama.not_`;
  konsol satırları "duyarlilik el 15 mm … AYIRMADI". E4 `erisim`'e: "15 mm ve altında eski sıra da açık görünüyor, fark 20 mm el
  varsayımına dayanıyor".
- **El payı olmayan "el payı" sayıları** (B-2):
  - §1'deki "L tutacağına el payı 15 mm" el payı değil: `rehber_sira.py` `ulas(..., s0=15.0)` L uzun kolu boyunca örneklemenin
    başladığı nokta; dört cıvatada da ilk örnek noktası el bölgesinde olduğu için 15 çıkıyor. El payı (eşik) 20 mm. Doğrusu: "L uzun
    kolu el bölgesine ilk örnek noktasında (kol boyunca 15 mm'de) ulaşıyor". Aynı satırdaki "düz alyanla el payı 20,5 / 14,5 / 32,5 /
    11,5 mm" da el payı değil, düz alyanın el bölgesine ulaştığı uzaklık.
  - H0a "el payı 25,5–36 mm" (`is_` ve `erisim`) → "açık ağız (anahtar) el bölgesine 25,5–36 mm'de ulaşıyor" (`acik_agiz_el_mm`).
  - Aynı türden üçüncüsü (brief listesinde yoktu, aynı hata): K1 `erisim` "el payı 6–9 mm" (10.11 notu: "el uzaklığı 6–9 mm") →
    "el bölgesine uzaklık 6–9 mm, el yakına ulaşıyor".
- **B6 notu** (B-6): "Çözüm seçilmedi, ölçülmedi" → "Çözüm seçilmedi (K53 karar bekliyor; seçenekleri F10b'de ölçüldü,
  `planlama/d158/F10b-gunluk.md`)". Taşma 0,425 mm aynı; çözüm seçilmiş gibi yazılmadı.
- **F4** (B-7): "kapak açıklığından travers arkasına 0 mm, yarığın iç tarafına 6 mm" → "el bölgesine uzaklık: travers arkasına 0 mm,
  yani el kapak açıklığından doğrudan ulaşıyor; yarığın iç tarafına 6 mm". Sayılar orkestratör raporundan, yeniden ölçülmedi.

### D4. `planlama/d158/F10a-dogrula.py`

- `ONCE = os.environ.get("F10A_ONCE", "749627b~1")`; "önce" sayfası `git show ONCE:rehber/…` (önceden `HEAD:`). Assert iletisi, `yontem`
  metni ve konsol satırı ONCE'u yazıyor.
- `veri_degismedi` kabul ölçütünden çıktı (`sonuc["gecti"]` artık kadraj, seçim, ağsız, CDN, küçük görünüm, yazdırma kareleri);
  alan JSON'da bilgi olarak duruyor, konsolda "degisti (bilgi)". Başka davranış değişmedi.

### D5. Devredilenler ve gereksiz kalanlar

- Panel tablolarının sırayı göstermemesi (B-8: "Parçalar" ve "Bağlantı elemanları" ayrı; listede yüz kabuğu tabla cıvatasından önce):
  bu turda düzeltilmedi, **F10d'ye devredildi** (öneri: satırları `sira_grup`'a göre grup başlıklarıyla bas).
- İlk turda yarım kalan iki E3 varyantı (V6 / V7, horn servoda, 146 ve 26 yön): artık **gereksiz**; P1 ölçümü ve bu turun süpürmesi
  soruyu kapattı.

### D6. Üretim ve kontroller

| Komut | Çıkış | Not |
| --- | --- | --- |
| scratchpad: `e3.py` / `e3_sag.py` / `e3_p1.py` (giriş yolu, E3) | 0 | tablolar D1 |
| scratchpad: `e4.py` A, B_A, B, A_B, C (art arda, tek süreç) | 0 | 20,8 / 37,3 / 37,0 / 7,6 / 5,1 s |
| scratchpad: `rehber_sira.py --veri sim-veri.json --adimlar 28,29,30,31` (taşımanın benzeri, üretimden önce) | 0 | |
| `FREECAD-KILIT.txt` ← "F10c düzeltme turu 1 … 04:42 başladı" | – | boş bellek 3,6 GB, FreeCAD süreci yok |
| `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` | 2 | 04:43 → 04:53; tek sorun denetim: 26 ASCII kelime (hepsi doğru yazımı ASCII olan Türkçe: hornunu, konumdayken, miline, indikten, inen, milde, milinde, pres, ona, tarifinden, indir, kafadaysa, pime, aradaki, ortak, hacim, temas, ediyor, soldan, dikey, bindirmesi, solun, girmiyor, grubu, eden, yani) → `rehber_denetim.py` ASCII_TAMAM |
| `FREECAD-KILIT.txt` ← "boş" | – | |
| `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` | 0 | 04:54 → 05:04; veri değişmedi (ilk koşunun verisi), yalnız denetim / görüntü / PDF yeniden |
| `py -3 -X utf8 planlama/d158/F10a-dogrula.py` (1. koşu) | 2 | yalnız `patlat_tak` kaldı: betik "üçüncü tak" için veri satır sırasını (`sat[2]` = sol arka kabuk) bekliyordu, app.js ise `st.sira`'yı izliyor (3. tak = dizi vidaları). Betiğe `st.sira` varsa onu kullanma eklendi (app.js davranışıyla aynı ölçüt); başka değişiklik yok |
| `py -3 -X utf8 planlama/d158/F10a-dogrula.py` (2. koşu) | 0 | |
| E3 `sira` eklendi (sıralı takma 2-3-4 metin sırasını izlesin: horn vidası → yanak-horn → pul + pim), yeniden üretim: `FREECAD-KILIT.txt` ← "… 2. koşu, 05:19 başladı" | – | boş bellek 3,4 GB, FreeCAD süreci yok |
| `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` (son) | **0** | 05:20 → 05:30 (10 dk 30 s); sıra denetimi toplam 214 s (giriş yolu 102,5 s: E3 52, E4 sağ 13,5, sol 24,5, yüz 3,1 s); `FREECAD-KILIT.txt` ← "boş" |
| `py -3 -X utf8 planlama/d158/F10a-dogrula.py` (son) | **0** | 05:30 → 05:37; seçim 6/6, ek sınamalar hepsi geçti, ağsız dış istek 0, konsol 0, kadraj ortancası 0,1733 → 0,4013 (önce = `749627b~1`), taşan 0, küçük görünüm 50/50 + 50/50 (360 px, taşma 0), CDN 0, yazdırma kareleri 50/50; `veri_degismedi` false (bilgi) |
| `py -3 -X utf8 planlama/d158/F9b-dogrula.py` | **0** | GECER (hata 0) |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | 17 dosya özeti kayıtla aynı |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** | 10/10 GEÇER |
| headless Chrome: adım 30 `patlat=1&tak=1,2,4`, adım 31 `tak=2` | 0 | `F10c-goruntu-d1-*.png` |

**Kabul tablosu (son üretim):**

| Ölçüt | Sonuç |
| --- | --- |
| 50/50, konsol 0 | 50/50, konsol 0 |
| Parça 1192 ↔ 1192, taşınanlar tek tek, her parça tek adımda | 1192 ↔ 1192; taşınan 5 (D1 tablosu), başka alan farkı yok; her parça tek satırda: evet |
| Denetim 0 | ASCII kalıntı 0, gruplama 0, çelişki 0, zorunlu uyarı eksik 0 / 40 |
| Sıra denetimi "ulaşılamaz" 0 | 0 (565 bağlantı: DUZ 469, L 39, ACIK_AGIZ 21, ACIK_AGIZ_DAR 9, CEP 14, LOKMA 11, POZA_BAGLI 2) |
| Bilinen kapalı örnek sınaması | geçti, **el 20 mm**; 15 / 12 mm'de ayırmıyor (bilgi, `sira.sinama.duyarlilik`) |
| E3'te kafa girişi serbest (ölçülmüş, yöntemle) | **evet**: +y (ve ±z) serbest, eşik 0,2 mm, h 0,25 mm; `kontrol.json` `sira.giris.e3_kafa_serbest: true`; giriş sınamaları 3/3 |
| C5 üç grubun giriş yolu | sağ arka −z; sol arka −x / −z (sağ takılıyken); yüz +z; sıra "sağ → sol" metne ve `sira`'ya işlendi; girilemez 0 |
| Perdelenme tablosu 50 adım | yazılı; toplam 291 (önce 290: E3'te pim pulu pim başının altında gizli; E2 14 → 12, E3a 23 → 22, E3 4 → 7 yeni parça) |
| `F10a-dogrula` depodaki hâliyle | çıkış 0 |
| `F9b-dogrula` / `carpisma_kos kontrol` / regresyon | 0 / 0 / 10/10 |
| PDF | 55 → 55 sayfa (devam 5), en küçük yazı 8,1 → 8,1 pt; 5092 → 5108 kB |
| Model değişmedi | `robot.glb` / `robot-glb.js` bayt aynı (`git diff --quiet` 0); `tasarim/freecad/` altında bu turun değişikliği yalnız `rehber/` |

**Görüntüler (kendim baktım):** `planlama/rehber/goruntu/adim-28.png` (horn servoda, panelde yeni E2 metni), `adim-29.png` (625ZZ sol
yanakta, horn yok), `adim-30.png` ve PDF sayfa 32 (yeni E3 metni, not, 4 bağlantı satırı, erişim notu); `F10c-goruntu-d1-30-tak1/2/4`:
sıralı takma 1 alt montaj (kafa) → 2 horn vidası → 3 yanak-horn → 4 pul (→ 5 pim); `F10c-goruntu-d1-31-tak2`: 1 sağ arka kabuk,
2 ReSpeaker. PDF metninde B6 "K53 karar bekliyor", F4 "el bölgesine uzaklık", H0a "25,5–36 mm'de ulaşıyor", K1 "el bölgesine uzaklık
6–9", E4 "fark 20 mm" ve "Önce sağ kabuğu" var; eski "el payı 25" ve "ölçülmedi\"" 0.

### D7. Dokunulan dosyalar (bu tur)

- `tasarim/freecad/rehber/rehber_giris.py` (yeni, izlenmiyor: commit listesine girmeli)
- `tasarim/freecad/rehber/rehber_sira.py` (giriş yolu, `ACIKLAMA`, sınama adları ve el duyarlılığı; izlenmiyor, A'dan)
- `tasarim/freecad/rehber/rehber_secici.py` (E2 / E3 / E3a satırları)
- `tasarim/freecad/rehber/rehber_metin.py` (B6, K1 `erisim`, E2, E3a, E3 + `sira`, E4 `is_` / `erisim` / `sira`, F4, H0a)
- `tasarim/freecad/rehber/rehber_denetim.py` (ASCII_TAMAM'a 26 kelime)
- Üretici çıktıları: `rehber/veri/rehber-veri.json`, `rehber-veri.js`, `rehber/goruntu/adim-28/29/30.png`, `planlama/rehber/kontrol.json`,
  `planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-28/29/30.png` (+ A'nın 15/17/31/36/42 değişiklikleri)
- `planlama/d158/F10a-dogrula.py`, `F10a-dogrula.json`; **yan etki:** betik her koşuda `planlama/d158/F10a-goruntu-*.png` (25 dosya)
  yazıyor, bunlar da yeniden yazıldı (brief'in yazma listesinde yok; kabul için betiği depodaki hâliyle koşmak gerekiyordu)
- `planlama/d158/F10c-gunluk.md`, `planlama/d158/F10c-goruntu-d1-*.png` (4), `planlama/d158/FREECAD-KILIT.txt` (koşu boyunca satır, sonra "boş")
- `rehber/app.js` bu turda değişmedi. `F10c-kontrol.md`, `karar-kuyrugu.md`, `dongu-158.md` dokunulmadı.

### D8. Açık kalanlar

1. E3 sıfır boşluklu iniş (54,4 ↔ 54,4 mm): baskı toleransında ölçülmedi; karar kuyruğu önerisi D1'de.
2. Horn spline'ının servo ortasında takılması ve horn vidasının yanak deliğinden PH1 ile sıkılması: tork / görüş ölçülmedi; vida 2 ile
   cıvata 3 arasındaki sıra kaynakta yok.
3. Giriş yolu yalnız 6 eksen yönü (scratchpad koşusunda E4 için 12 yön): eğik / dönerek giriş ölçülmüyor; sürtünme ve baskı toleransı yok.
4. E4 kablo takma ("kabloları açık ön taraftan tak", "yüz kabuğunu önde tut") ve kablo boyları: modelde yok, ölçülmedi.
5. Hornun E2 patlatma yönü radyal (servo ekseni değil): görsel, değiştirilmedi.
6. Panel tabloları sırayı göstermiyor: F10d (D5).
7. Sıra denetimi süresi 136 → 214 s (giriş yolu 102 s + el 15 / 12 duyarlılığı); üretim toplamı yaklaşık 10,5 dk.
