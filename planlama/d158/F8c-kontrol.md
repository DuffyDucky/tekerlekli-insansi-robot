# F8c kontrolü (P8.3 ölçüm ve test kâğıtları) — bağımsız kontrol ajanı B, 08.11.2026

Brief: `planlama/d158/F8c-brief.md`. İncelenen: `planlama/d158/testler/` (00-genel, T1–T9 .md, `testler_html.py`, `testler.html`),
`planlama/d158/F8c-gunluk.md`. Yazılan tek dosya bu. CAD betiği koşulmadı; commit/push/silme yok.

## Genel karar

**GEÇMEZ (düzeltmeyle geçer, tek tur yeter).** Atıflar, türetilen eşikler ve HTML sağlam. Ama brief'in güvenlik ölçütüne göre
iki kâğıt geçmiyor: **T8** (yükte servo ölçümü öğrenciyi kol hareket alanına sokuyor) ve **T9** (rampada tek emniyet önlemi,
gevşek tutulan ve omuzdan bağlı bir ip; ayrıca 0,1 m/s² sınırı seçilen aletle güvenilir okunamıyor). Akım ölçülen dört kâğıtta
multimetre bağlantı uyarısı eksik (ortak düzeltme). Düzeltme listesi aşağıda; 1–6 zorunlu, 7–15 önerilir.

| Kâğıt | Karar | Gerekçe (kısa) |
|---|---|---|
| 00-genel | KOŞULLU | Ortak kurallarda ampermetre bağlantı kuralı, takı çıkarma yok (düzeltme 1) |
| T1 JGB37 | KOŞULLU | Eşikler doğru; ama kaynak 5 A sınırında iken "akım > 5 A" okunamaz, tork da geçersizleşir; gevşek ip darbe tepesi okutur (2, 7, 8, 9) |
| T2 QLED VBUS | **GEÇER** | Pi'ye takmama şartı başlıkta, güvenlikte ve "sınır aşılırsa"da; ölçüm sırası mantıklı; eşikler varsayım diye işaretli (öneri 14) |
| T3 kafa 5 V | KOŞULLU | Pi hattına seri multimetre: 30 dk yükte 10 A kademe süre sınırı ve şönt düşümü ölçülen gerilimi/`get_throttled`'ı bozar (1, 3) |
| T4 PAM + ses kartı | KOŞULLU | Aynı seri ölçüm sorunu (P1); BTL uyarısı çok iyi (1, 3) |
| T5 hub girişi | KOŞULLU | L2'de F4'ün enerji varken mi çekileceği yazmıyor; USB ölçerin kendi düşümü U1−U2'ye girer (10, 11) |
| T6 akustik | **GEÇER** | Kaynaklar tam, varsayımlar dürüst, servo güvenliği var (öneri 15) |
| T7 göğüs 12 V | KOŞULLU | "Giriş akımı / ekran akımı" ölçümünde seri bağlantı ve 10 A soketi yazmıyor; kart girişi kutup kontrolü yok (1, 12) |
| T8 servo hatları | **GEÇMEZ** | Adım 10: kollar hareket ederken bilek servosu konnektöründe prob; kendi "erişim alanında kimse durmaz" kuralıyla çelişiyor (4). C'de çıkış ≥ 5,5 V eşiği mantıksız gevşek (5) |
| T9 zemin + rampa | **GEÇMEZ** | Acil stop rampada robotu durdurmuyor (kâğıt bunu söylüyor) ama asıl denemelerde ip "gevşek", omuzdan bağlı (6); telefon ivmeölçeri 0,1 m/s²'yi çözemez (13) |

## 1. Atıf denetimi (`dosya:satır`)

Uygulayıcının "123 atıf doğru" iddiasından bağımsız olarak **90'ı aşkın atıf** açıldı (sed ile satır, JSON için `py -3` ile anahtar). **Hepsi doğru
satıra düşüyor, değer ve bağlam tutuyor.** Örnek (en az 25):

| Atıf | Kâğıt | Satırda olan | Sonuç |
|---|---|---|---|
| `elektrik.md:16` | T3, T4 | D24V50F5 5 V ±%4, 5 A sürekli, ≤ 38 V | ✔ |
| `elektrik.md:17` | T2 | Power ve Touch ayrı micro USB | ✔ |
| `elektrik.md:18` | T3 | SY8205 7–30 V, 3,7 A, koruma yazmıyor; QLED 0,9 A varsayım | ✔ |
| `elektrik.md:19` | T7 | 12 V ~0,5 A, LM2577+LM2596 12 V, 2 A dal | ✔ |
| `elektrik.md:21` | T4 | PAM besleme noktası ve akımı doğrulanmadı | ✔ |
| `elektrik.md:22`, `:24`, `:25`, `:26` | T3 | 3,57 A; 2,67 A (%53); 0,9 A (%24); 12 V ≈ 1,55 A | ✔ |
| `elektrik.md:43` | T2 | Touch VBUS iç bağı doğrulanmadı | ✔ |
| `elektrik.md:54` | T7, T1 | Regülatörü ekrana bağlamadan 12 V'a ayarla; akü 12,8–14,4 V | ✔ |
| `elektrik.md:60` | 00, T1, T8 | Ana 30 A → F1 20 A (BTS ×2 + XL4016 A/B/C), F3 5 A, F4 5 A | ✔ (bkz. düzeltme 8) |
| `elektrik.md:76` | T8 | 2 × 1,93 × 0,052 × 2,5 ≈ 0,50 V düşüm, servo ≈ 5,5 V | ✔ |
| `elektrik.md:89-91`, `:95` | T8 | 4,87 / 7,24 A; C 1,5 / 5,0 A; %97, "ölçüm yine gerekli" | ✔ |
| `elektrik.md:118-119` | T1 | Yalnız `*_olculen` alanları doldurulur | ✔ |
| `elektrik.md:124`, `:126`, `:127` | T1 | 21 kg·cm, %30 = 6,3; 2,8 A; birimsiz etiket; Aslong 9 kg·cm / 1,2 A | ✔ |
| `elektrik.md:136`, `:139` | T1 | 9 kg·cm ise dönemez; "≤ 10 kg·cm omni yetmeyebilir" | ✔ |
| `elektrik.md:170`, `:173-175` | T1, T9 | > 2,0 A'de kes; 100 mm kol + kantar; μ = F/(mg) | ✔ |
| `elektrik.md:187`, `:189` | T8 | XL4016 8 A modül, sürekli ≤ 5 A; aşarsa 20 A modül | ✔ |
| `elektrik.md:224`, `:229`, `:231` | T5, T6, T8 | Servo hedefi son konuma; ESP32 reset → kollar düşer | ✔ |
| `elektrik.md:247-248`, `:249` | T3, T7 | `PSU_MAX_CURRENT=5000`, `usb_max_current_enable=1`; şarj 14,6 V | ✔ |
| `elektrik.md:284`, `:285` | T8 | 1,33 Ω / 30 W, 30 dk; soğutucu ≤ 80 °C | ✔ |
| `elektrik.md:308`, `:334`, `:338` | T8, T3, T7 | Yıldız toprak; F3 5 A; göğüs mini 2 A | ✔ |
| `elektrik.md:472`, `:478`, `:480` | T3, T7 | Açık iş 8, 14, 16 | ✔ |
| `kararlar:7`, `:8`, `:19`, `:47-51`, `:77`, `:83` | T1, T6, T8, T9 | ivme ≤ 0,1; 5°; tilt ±13°; hat akımları; fren 0,1; acil stopta kayma | ✔ |
| `dongu.md:39`; `dongu-158.md:24`, `:25` | T1, T6, T9 | JGB37 riski; 1,517; 574,3 mm | ✔ |
| `06-aku-secimi.md:15` | T1 | Boşta 0,08–0,15 A; Aslong 9 kg·cm / 1,2 A | ✔ |
| `07-gogus.md:19`, `:39`, `:47`, `:48`, `:51` | T3, T5, T7 | 12 V/1 A adaptör; USB 1,6 A; D24V150F5; SY8205 3,7 A | ✔ |
| `secenekler.md:197`, `:213-215`, `:231`, `:248`, `:251`, `:254`, `:262`, `:274` | T5, T6 | 3 vida; 4,9 / 7,4 mm; Ø3 varsayım; 595,7 / 574,3; fan; hub; hoparlör | ✔ |
| `uygulama-notu.md:35-36`, `:45`, `:98`, `:100`, `:106`, `:113`, `:125-132` | T4, T5, T6, T9 | 1,61 / 1,517; 4 × Ø3; 0,71 A, %66–68; ölçülmedi; 920 mm; PAM varsayım; port tablosu | ✔ |
| `arayuz.py:661-665` | T1, T9 | `mu_olculen`, `stall_kgcm_olculen`, 21,0, 2,8 | ✔ |
| `eklem_sinirlari.json:105-109` | T9 | `rampa_surus` 0,1, `rampa_fren` 0,1 | ✔ |
| `oneri-taslak-v8.md:68`, `:160`, `:175`, `:185`, `:187`, `:199`, `:260` | T3, T6 | H1; A ağırlıklı yavaş; 1,6 m; 60 dB(A) @1 m; fan ayrı rapor, kayıt tutulmaz; ≤ 40 dB(A) | ✔ |
| `karar-kuyrugu.md:21`, `:25`, satır 165, K9 (`:159`) | T4, T6, T9 | K6; K10 varsayılan D24V50F5; K10 başlığı; 500 g'da 1,327 | ✔ |
| `taban-analiz.json` `donus.karar`, `motor.rampa5_*`, `donus.varsayim` | T1, T9 | 15,76 / 3,16; 4,74 / 5,77; μ 0,4/0,5/0,6, `mu_olculen: null` | ✔ |

Atıfla gösterilen dosyaların hepsi var (`uygulama-ivme.json`, `kafa_parcalar.py`, `maliyet.json`, `taban_montaj.py` dahil).
Küçük not: T9'da K9 satırsız (`karar-kuyrugu.md` K9; değer `:159`'da).

## 2. Türetilen eşikler (yeniden hesap)

**T1, 17,2 ve 10,5 kg·cm.** `taban-analiz.json` `motor` bölümü şu modeli kullanıyor (F_N değerlerinden geri çözüldü, sapma < 0,1 N):
toplam F = m·(g·sin 5° + c_rr·g·cos 5° + a), m = 25,911 kg, c_rr = 0,03, teker yarıçapı 62,5 mm, **4 motor eşit pay**, tork teker
milinde (dişli kutusu çıkışı; ayrıca dişli oranı ya da verim çarpanı yok, satıcı torku zaten çıkış milinde).

| a (m/s²) | F toplam (N) | Motor başına (kg·cm) | ÷ 0,30 → gereken durma (kg·cm) |
|---|---|---|---|
| 0 | 29,75 | 4,739 (JSON 4,74 ✔) | 15,8 |
| **0,1** | **32,34** | **5,151** | **17,17 → 17,2 ✔** |
| 0,25 | 36,23 | 5,770 (JSON 5,77 ✔) | 19,2 |
| 0,5 | 42,71 | 6,802 (JSON 6,80 ✔) | 22,7 |

F, a'ya doğrusal olduğundan kâğıttaki doğrusal ara değer (4,74 + 1,03 × 0,4 = 5,152) kesin değerle aynı. Omni dönüşü: `donus.karar.omni_kgcm`
3,16 (μ 0,5) → 3,16 / 0,30 = 10,53 → **10,5 ✔**.
İki not (kâğıda eklenmeli, düzeltme 9): (a) aynı JSON'da omni μ 0,6 için 3,63 kg·cm → 12,1 kg·cm; T9 μ ≤ 0,6'yı GEÇER saydığına göre
"ağır" eşiği ölçülen μ'ye bağlanmalı. (b) Kütle P1.1 öncesi (akü 2,8 → 3,0 kg); +0,2 kg ile 17,2 → ~17,3. Etki küçük, ama T1'de
"25,911 kg, P1.1 öncesi" yazmalı (T9'da yazıyor).

**T8, 4,87 A ve 1,5 A.** 1,80 + 1,83 + 0,84 + 0,40 = 4,87 ✔; 4,87 / 5 = %97,4 ✔; C: 0,6 + 0,9 = 1,5 ✔. Giriş (6 V × I / 0,88 / 12,8 V):
A/B 2,59 / 3,86 A, C 0,80 / 2,66 A → `elektrik.md:89-91`'deki 2,6 / 3,9 ve 0,8 / 2,7 ✔. Yük direnci 6 V / 1,33 Ω = 4,51 A, 27,1 W ✔.

**T3, 2,67 A + 0,9 A.** 2,67 + 0,9 = 3,57 A ✔; × 5 V = 17,85 W ✔; 12 V girişi 3,57 × 5 / 0,90 / 12,8 = 1,549 A ✔; %53 ve %24 ✔.
**T4** 0,71 A = 3 W / 0,85 / 5 V = 0,706 ✔. **T7** 24 Ω: 12 V → 0,5 A, 6 W ✔; 10 V girişte ekranla (12 W, η ≈ 0,85) giriş ≈ 1,4 A < 2 A ✔.
**T9** h = tan 5° × 100 = 8,75 cm ✔.

## 3. Güvenlik bulguları

**G1 (T8, GEÇMEZ).** T8 adım 10: D profillerinde (jest, kol uzanmış) "en uzak servonun (bilek) konnektöründe, hareketin başladığı anda"
gerilim okunuyor. Bilek uzatmasının konnektörü kolun içinde/ucunda; prob tutan el kolun hareket alanına girer. Bu, aynı kâğıdın
"Kolların ve kafanın erişim alanında kimse durmaz, parmak eklem aralarına girmez" kuralıyla çelişir (`T8-servo-hatlari.md:47` ↔ `:77`).

**G2 (T9, GEÇMEZ).** Kâğıt doğru tespit ediyor: acil stopta motorlar boşa düşer, robot rampada aşağı kayar (`kararlar:83`,
`T9-zemin-rampa.md:51`). Ama asıl B denemelerinde (adım 9) tek tutucu önlem "gevşek ama hazır" tutulan, **omuz altından** bağlı ip.
Bir sorun anında operatör acil stopa basacak, robot boşta yuvarlanacak, gevşek ip ani gerilecek; ip omuz yüksekliğinde olduğu için
taban kaymaya devam ederken gövde ipe doğru, yani rampanın üstündeki kişiye doğru dönebilir. Kayma tabandan, devrilme üstten tutulmalı;
ip boşluğu sınırlanmalı; ipi tutan kişi düşme hattında olmamalı.

**G3 (ortak; 00-genel, T1, T3, T4, T7: KOŞULLU).** Akımı multimetreyle seri ölçtüren kâğıtlarda şu yok: kırmızı uç **10 A soketine**,
ölçüm **yalnız seri** (asla iki uç arasına); iş bitince kırmızı uç **V soketine geri**, aksi halde sonraki gerilim ölçümü akü/kaynağı
multimetre üzerinden kısa devre eder. 10 A kademesinin süre sınırı da yok: çoğu el multimetresinde ≥ 5 A için "en çok 10–30 s,
arada 15 dk" vardır; T3 S2 ve T4 A4+S2 30 dk boyunca 2,7–5 A geçiriyor. Saat/yüzük çıkarma uyarısı yalnız T8'de.

**G4 (T1).** Kaynak 5,0 A'de akım sınırına girerse motor gerilimi düşer, okunan tork **gerçeğin altında** kalır; tablo bu durumda
"KALIR: tork < 17,2" verir ama sebep motor değil kaynaktır. "Akım > 5,0 A" ise bu düzenekte hiç okunamaz (`T1:49` ↔ `T1:112`).
Ayrıca "4 × 5 A = F1 20 A" gerekçesi F1'den XL4016 A/B/C'nin de beslendiğini atlıyor (`elektrik.md:60`).

**G5 (T5).** L2 "F4 sigortası çıkarılmış": enerji varken mi çekileceği yazmıyor. Sigorta bloğu akü barasının yanında; enerji kesilip
çekilmeli, sonra enerji verilmeli.

**G6 (T7).** LM2577+LM2596 kartının giriş kutbu için kontrol adımı yok (kartlarda ters kutup koruması genelde yok). Kaynak 2 A sınırlı
olduğu için tehlike düşük, ama "girişte kırmızı = +" kontrolü bir satır.

Sorunsuz bulunanlar: T2 (Pi'ye takmama şartı üç yerde; akü/servo yok; statik ve cam uyarısı), T3 ters kutup + 1 A ilk enerji, T4 BTL
çıkışı (hoparlör ucunu GND'ye/osiloskop toprağına bağlama) ve kulak, T6 servo hedefi + acil stop + takoz + kayıt silme, T8 ilk ayarı
servosuz yapma + 27 W direnç + 80 °C soğutucu, T9-A ipi alçaktan çekme (aks yüksekliğinde çekişte kayma devrilmeden önce gelir:
62,5 mm × μ ≪ 216 mm), T9-B'nin T1'e bağlanması ve elde yük yasağı.

## 4. Biçim ve dürüstlük

Dokuz kâğıdın dokuzunda amaç, neden önemli, doğruladığı varsayım (kaynaklı), alet, güvenlik, adım adım yöntem, boş kayıt tablosu,
sayısal geçer sınırı ve "sınır aşılırsa" (belge + kişi) var. Varsayım/dış kaynak işaretleri dürüst: T2 eşikleri, T3 30 dk, T4 30 s ve BTL
(datasheet, depoda yok), T5 4,75 V hedefi, T6 C eşikleri (KOŞULLU'ya bağlanmış), T7 ±%5, T8 5,5 V'un 1,93 m kaynaklı olduğu, T9 0,5 s
ortalama, USB 2.0 Tablo 7-7 (4,75 / 4,40 V, 0,5 A; dış kaynak olarak doğru). T6'daki ReSpeaker 6 kanal düzeni ve `sox remix 1/2`
eşlemesi doğru; AEC referansı sorusu dürüstçe "doğrulanmadı".

Veri geçerliği bulguları (güvenlik değil):
- **V1 (T3, T4):** Pi hattına seri multimetre şönt + uç direnci ~0,05–0,1 Ω; 3–5 A'de 0,15–0,5 V düşüm. N2 gerilimi ve `get_throttled`
  ölçü aletinin kendisi yüzünden kalabilir. Pens tercih edilmeli; seri ölçümse gerilim Pi tarafında okunmalı.
- **V2 (T1):** "Kol ipi gerer, motor durur": ip gevşekse kol ivmelenip ipe çarpar; kantarın "en yüksek" değeri darbe tepesidir, torku büyük
  gösterir. İp enerji vermeden önce boşluksuz gerilmeli; değer 1–2 s sonraki kararlı okuma olmalı.
- **V3 (T9):** Telefon "doğrusal ivme" yerçekimini füzyonla çıkarır; 0,5° eğim hatası 0,086, 1° hatası 0,17 m/s² sızdırır. Rampa girişinde
  gövde 5° yatarken füzyon gecikir. 0,10 m/s² sınırı bu aletle güvenilir ayrılamaz. Hız profili (enkoder kaydı ya da videoda bant işaretleri:
  0,39 m/s'ye ≥ 3,9 s'de çıkıyor mu) çok daha sağlam.
- **V4 (T9):** B tablosunda "düzde duruş" sütunu da 0,10 sınırına tabi görünüyor; düz zeminde fren sınırı 1,8 m/s² (`kararlar:78`).
- **V5 (T8):** C'de "çıkış ≥ 5,5 V" eşiği `elektrik.md:76`'dan alınmış, ama orada 5,5 V **servo ucundaki** değer (6 V − 0,5 V kablo).
  Regülatör çıkışı 5,5 V'a inerse servo ~5,0 V görür. Çıkış eşiği 6,0 V'a yakın olmalı (ör. ≥ 5,85 V, varsayım diye işaretli).
- **V6 (T5):** Her USB ölçer araya ~0,05–0,1 Ω ekler; U1 ve U2 aynı anda takılıysa düşüm iki ölçerin direncini de içerir. Not düşülmeli.
- **V7 (T2):** "Herhangi bir direnç değeri → KALIR" tutucu; çip girişleri üzerinden kΩ–MΩ okunup yanlış KALIR çıkabilir. Güvenli yönde
  hata, zorunlu değil.

## 5. HTML ve betik

`py -3 planlama\d158\testler\testler_html.py --kontrol` → "md dosyası: 10 (kâğıt T: 9), HTML bölümü: 10, iç bağlantı: 35, id: 117,
KONTROL GEÇTİ", çıkış 0; `testler.html` zaman damgası değişmedi (21:14:15). Bağımsız sayım: `<table>` 53 = .md tablo 53; HTML'de kalan
`**` ya da ters tırnak 0; dış kaynak (`<link>`, `src=`, `href="http`) 0. Baskı CSS'i: `@page A4 12 mm`, her `.kagit` yeni sayfada
(ilki hariç), başlıktan sonra kırılma yok, `tr`/`pre` bölünmez, baskıda koyu tema beyaza döner, üst çubuk ve içindekiler gizli.
Açık/koyu tema `:root` + `prefers-color-scheme` + `data-theme` üçlüsüyle, `localStorage` try/catch içinde. Tablolar okunur; tek zayıf yer
A4 dikeyde 8–9 sütunlu kayıt tabloları (T3, T4, T5): sütun ~20 mm, boş satır 2,2 em (≈ 6,6 mm), elle yazmak için dar (öneri 15).

## 6. Takma ad ve kişisel veri

`testler/` ve `F8c-gunluk.md` içinde takma ad **0**. Kişi adı olarak yalnız proje sahibinin adı ve yazılımcının ilk adı geçiyor; ikisi de
depoda zaten açık (`dongu-158.md`, `elektrik.md`, `uygulama-notu.md`). Telefon, e-posta, kimlik yok. Not: kaynak `elektrik.md:83`'te takma ad
geçiyor; kâğıtlara taşınmamış (bu paketin dışı).

## 7. Düzeltme listesi

Zorunlu:
1. **00-genel ortak kurallar + T1, T3, T4, T7 güvenlik:** "Akım ölçümü: kırmızı uç 10 A soketine, multimetre yalnız seri; enerji kapalıyken
   bağla; iş bitince kırmızı ucu V soketine geri tak (yoksa sonraki gerilim ölçümü kısa devre yapar). 10 A kademesinin süre sınırına
   uy (aletin etiketi); 30 dk'lık ölçümlerde pens kullan. Saat, yüzük, bileklik çıkar." (G3)
2. **T1:** Kaynak akım sınırına girerse (CC lambası ya da gerilim < 11,8 V) o denemenin torku geçersiz, sonuç "akım ≥ 5 A → KALIR" diye
   yazılır; "akım > 5,0 A" satırı "kaynak 5,0 A sınırına girdi" diye değişmeli. (G4)
3. **T3, T4:** Pi hattı ve PAM akımı için pens öncelikli; seri multimetre ancak 5 dk'lık S0/S1'de ve aletin 10 A süre sınırı içinde.
   Seri ölçümde N2 gerilimi ölçerin **Pi tarafında** okunur, şönt düşümü not edilir. (G3, V1)
4. **T8 adım 10:** Bilek konnektörüne, **enerji yokken**, uzun ölçü telli (≥ 1 m) servo Y-ara kablosu ya da lehimli test ucu tak; telleri
   erişim alanının dışına çıkar; multimetre (MIN tuşu) alan dışında okunur. Hareket sırasında kimse kola ya da konnektöre uzanmaz.
   Güvenlik bölümüne "hareket varken prob tutulmaz" satırı. (G1)
5. **T8 C:** "Çıkış ≥ 5,5 V" eşiğini regülatör çıkışına uygun bir değerle değiştir (ör. ≥ 5,85 V, **varsayım** işaretli; ya da kaynakta
   çıkış eşiği olmadığını yazıp tasarım ajanına sor). D satırındaki uç servo ≥ 5,5 V kalabilir. Adım 6'ya "servolar dağıtım kartından
   sökülü" açıkça yazılsın. (V5)
6. **T9 B güvenliği:** İki bağlantı: kayma için **taban** yüksekliğinden bir ip (rampa üstünde sabit bir noktadan ya da kişiden, boşluk
   ≤ 10 cm), devrilme için omuz altı ip ayrı. İpi tutan kişi robotun tam arkasında değil yanda-üstte. Acil stopun rampada robotu
   durdurmadığı, durdurucunun ip olduğu adım 9'un başına yazılsın; ilk deneme düşük hızla. (G2)

Önerilir:
7. **T1 adım 4–5:** İp enerji vermeden önce boşluksuz gerilir; kantarda darbe tepesi değil 1–2 s sonraki kararlı değer okunur. (V2)
8. **T1 güvenlik:** "4 × 5 A = F1 20 A" gerekçesini düzelt (F1 servo hatlarını da besler); 5 A yalnız laboratuvar düzeneği sınırıdır. (G4)
9. **T1:** "Ağır" eşiği ölçülen μ'ye bağlansın (μ 0,5 → 10,5; μ 0,6 → 12,1 kg·cm, `donus.yerinde_omni`); kütlenin P1.1 öncesi olduğu yazılsın. (§2)
10. **T5 L2:** "Enerjiyi kes, F4'ü çıkar, enerji ver." (G5)
11. **T5:** USB ölçerin araya girdiği düşüm notu; U1−U2 tek ölçerle sırayla alınırsa koşul aynı tutulsun. (V6)
12. **T7 adım 5:** Kart girişinin kutbunu kaynak kapalıyken kontrol et; akım ölçümü için seri bağlantı ve kademe (madde 1). (G6)
13. **T9 B ölçümü:** Ana ölçüt olarak hız profili (enkoder kaydı ya da video + bant işaretleri, dv/dt), telefon ivmesi yardımcı; "düzde duruş"
    sütunu 0,10 sınırının dışında tutulsun (≤ 1,8 ya da yalnız kayıt). (V3, V4)
14. **T2:** KALIR satırına "< 10 Ω doğrudan bağ; kΩ üstü değer: adım 5–6 belirler" ayrımı; Power kablosunun A ucu kesildiyse adım 5'te
    çıplak tellerin adaptöre nasıl bağlanacağı (klemensle, enerji yokken). (V7)
15. **HTML / T6:** T3, T4, T5 kayıt tabloları için baskıda yatay sayfa (`@page` adlı sayfa) ya da tabloyu iki tabloya bölme; boş satır
    yüksekliği ≥ 8 mm. T6 C1'de diziyi sökmeden önce Pi'yi kapat.

## 8. Uygulayıcının iddiaları

Günlükteki iddialar doğrulandı: `--kontrol` sonucu birebir; tablo sayısı 53 = 53; takma ad 0; örneklenen 90'ı aşkın atıf doğru; `taban-analiz.json`
anahtarları doğru. Günlükteki "kaynak bulunamayan değerler" listesi kâğıtlarla tutarlı. Günlükte olmayan, bu kontrolün bulduğu konular:
G1, G2, G3, G4 ve V1–V5.

---

# Yeniden kontrol 1 (düzeltme turu 1 sonrası) — ajan B, 08.11.2026

Okunan: `testler/` altındaki 10 .md (21:24–21:30 sürümleri) baştan sona, öğrencinin uygulayacağı sırayla; `F8c-gunluk.md` "Düzeltme turu 1".
Yalnız bu bölüm eklendi; başka dosya değişmedi.

## Genel karar

**KOŞULLU (paket geçer; iki küçük zorunlu düzeltme kaldı, ikisi de tek cümle).** 15 maddenin 15'i uygulanmış. Önceki iki GEÇMEZ
sebebi (T8 bilek ölçümü, T9 rampa ipi) giderilmiş. Okurken iki kalan sorun buldum: T4'te servo gücü açıkken hoparlöre 10 cm'den kulak
verme adımı (erişim alanına girme) ve T1'de 11,8 V kuralının seri ölçer ve kablo düşümüyle yanlış "CC" (dolayısıyla yanlış KALIR) üretebilmesi.
Aküyü kısa devre ettirecek ya da öğrenciyi yaralayacak başka adım bulmadım.

| Kâğıt | Önceki | Şimdi | Kalan |
|---|---|---|---|
| 00-genel | KOŞULLU | **GEÇER** | — |
| T1 | KOŞULLU | **KOŞULLU** | R2 (11,8 V ↔ CC ayrımı) |
| T2 | GEÇER | **GEÇER** | — |
| T3 | KOŞULLU | **GEÇER** | R5 öneri |
| T4 | KOŞULLU | **KOŞULLU** | R1 (servo açıkken 10 cm dinleme) |
| T5 | KOŞULLU | **GEÇER** | — |
| T6 | GEÇER | **GEÇER** | — |
| T7 | KOŞULLU | **GEÇER** | — |
| T8 | GEÇMEZ | **GEÇER** | R6 öneri |
| T9 | GEÇMEZ | **GEÇER** | R3, R4 öneri |

## 15 maddenin doğrulaması

| # | Madde | Kâğıtta gördüğüm | Durum |
|---|---|---|---|
| 1 | Ortak ampermetre kuralı | `00-genel.md:41-54` (7 madde: 10 A soketi, yalnız seri, enerji kapalı, uç V'ye geri, süre sınırı → pens, yük tarafında gerilim, pens tek tele) + ortak kural 7 (hareketli parçaya el yok), 8 (takı). Bağlantı ve kısa tekrar: T1:60-61, T3, T4, T7, T8:53-54 | ✔ |
| 2 | T1 CC | Adım 5 (`T1:81-82`) ve KALIR satırı `T1:130` | ✔ (ama bkz. R2) |
| 3 | T3/T4 pens, seri düşüm | T3: S2 yalnız pens, pens yoksa S2'de akım yok, gerilim Pi tarafında, "seri" notu; T4: N2 yalnız pens, P1 gerilimi PAM tarafında | ✔ |
| 4 | T8 bilek ölçümü | Alet: Y-ara ≥ 1 m (`T8:40-41`); güvenlik "hareket varken prob tutulmaz", erişim alanı + 0,5 m (`T8:50-52`); adım 9–11 enerji yokken bağla, alan dışından oku, gevşerse acil stop → enerji kes → düzelt | ✔ |
| 5 | T8 C eşiği | XL4016 çıkışı ≥ 5,85 V (varsayım, gerekçeli `T8:151`); servo ucu ≥ 5,5 V D'de; adım 6 "servolar sökülü" | ✔ |
| 6 | T9 rampa güvenliği | İki ip (taban: şasi, aks yüksekliği, sabit dayanak, ≤ 10 cm; devrilme: omuz altı, ≤ 10 cm); 1,6 m düşme hattı, ipçiler ve kamera dışarıda, yan-üst çaprazda; "acil stop rampada durdurmaz, taban ipi durdurur" hem güvenlikte (`T9:53-54`) hem adım 9 başında; ilk deneme ölçüm değil | ✔ |
| 7 | T1 ip ön gerilme | Adım 4 enerji yokken boşluksuz ger; adım 5 kararlı değer; sütun "Kantar, kararlı" | ✔ |
| 8 | T1 F1 gerekçesi | "yalnız bu düzeneğin sınırı, robottaki sigortayla ilgisi yok" (`T1:58-59`) | ✔ |
| 9 | T1 μ'ye bağlı eşik | Tablo `T1:39-45`, T9 yoksa 12,1; kütle P1.1 öncesi notu `T1:30` | ✔ |
| 10 | T5 F4 sırası | Güvenlik ve L2: enerjiyi kes → F4 çıkar → enerji ver → bitince kes, geri tak | ✔ |
| 11 | T5 ölçer düşümü | Adım 5 "iki ölçer / tek ölçer" koşulu, 0,05 V varsayımı | ✔ |
| 12 | T7 kutup, seri akım | Adım 5 kaynak kapalıyken IN+/IN−; adım 7 ve 10 seri, 10 A soketi, gerilim ekran tarafında, bitince uç V'ye | ✔ |
| 13 | T9 ivme yöntemi | Enkoder Δv/Δt ya da video 1 s yol ≤ 5,0 cm; telefon yalnız yardımcı; düzde duruş ayrı tablo ≤ 1,8 | ✔ |
| 14 | T2 KALIR ayrımı | `< 10 Ω` doğrudan bağ, kΩ üstü adım 5–6'ya; kesik uç için test kartı/klemens, adaptör prizden çıkmışken | ✔ |
| 15 | HTML, T6 C1 | En geniş kayıt tablosu artık T3 6, T4 5, T5 6 sütun; baskıda `td:empty{height:8mm}`; T6 C1 iki yönde "Pi'yi kapat, enerjiyi kes" | ✔ |

## Yeniden hesap: T1 μ eşikleri

`taban-analiz.json` `donus.yerinde_omni[*].en_cok_kgcm` = 2,77 / 3,16 / 3,63 (μ 0,4 / 0,5 / 0,6). ÷ 0,30 → **9,23 / 10,53 / 12,10** → kâğıttaki
**9,2 / 10,5 / 12,1 ✔**. μ < 0,4 için 9,2 kullanmak tutucu yönde (düşük μ daha az tork ister). 17,2 kg·cm önceki hesapla aynı ✔.
Yeni atıflar: `kararlar:78` (düz fren 1,8, sürüş 0,5) ✔, `eklem_sinirlari.json:106-107` ✔, `elektrik.md:450-451` (arka enkoderler) ✔,
`motor.hiz_m_s` = 0,393 ✔.

T9 video yönteminin matematiği doğru: sabit ivmede d(1 s) = ½·a; v ≥ 0,1 m/s iken a > 0,1 ise ya d = ½a > 5 cm ya da (hıza 1 s'den önce
ulaşırsa) d = v − v²/2a > v/2 ≥ 5 cm. Yani sabit ivme varsayımıyla d ≤ 5,0 cm ⇔ a ≤ 0,10 m/s². Sınırı: ivme 1 s içinde sabit değilse (sona
yığılan bir tepe) kaçabilir; kâğıt "sabit ivmeli harekette" diyerek bunu söylüyor (bkz. R4).

## Yeni varsayım değerleri

| Değer | Nerede | İşaretli mi | Makul mü |
|---|---|---|---|
| 11,8 V | T1 adım 5 | ✔ "varsayım: 0,2 V pay" | Pay olarak makul, ama CC'nin tek göstergesi olarak yanlış sonuç verebilir (R2) |
| 5,85 V | T8 C | ✔ gerekçeli | ✔ 5,85 − 0,34 (`elektrik.md:194`) = 5,51 ≈ servo ucu 5,5 V; tutarlı |
| 0,05 V | T5 adım 5 | ✔ | ✔ USB ölçer fiş + şönt düşümü birkaç yüz mA'de onlarca mV; doğru büyüklükte |
| +0,5 m | T8 erişim alanı | ✔ | ✔ alt sınır olarak makul |
| 1,6 m | T9 düşme hattı | Kâğıtta "robot boyu kadar" diye gerekçeli, "varsayım" sözcüğü yok (günlükte var) | ✔ robot 1,58 m; devrilen gövdenin tepesi pivottan ~1,58 m'ye düşer. Yuvarlanma için ayrıca taban ipi var |
| 4–6 cm | T9 sınır bandı | "sınırda, tekrarla" diye yazılı, "varsayım" sözcüğü yok | ✔ ±1 kare (33 ms) ≈ ±0,34 cm, şerit okuma ±0,5 cm; ±1 cm bant uygun |

## Güvenlik okuması (sırayla, öğrenci gözüyle)

- **00-genel:** Ampermetre kuralı tam ve doğru sırada; "akım kademesinde iki noktaya değdirme = kısa devre" ve "uç V'ye geri" açık. ✔
- **T1:** Laboratuvar kaynağı 5 A sınırlı; enerji varken kola/ipe/kantara el yok, kantar sabit, uzaktan okunur; ip ön gerilmesi enerji
  yokken. Yaralanma ya da kısa devre adımı yok. ✔
- **T2:** Akü/servo yok; kesik uçta teller adaptör prizden çıkmışken klemense. ✔
- **T3:** S2'de seri ölçer yok; köprüyü kapatma ortak kural 3 ile enerji kapalıyken. ✔ (R5: S0/S1 5 dk'lık bekleme, aletin süre sınırından
  uzun olabilir; kâğıt "süre sınırı içinde" diyor, ama hangisinin önce geldiği açık değil.)
- **T4 — R1 (kalan, zorunlu):** Adım 5: önce "hoparlöre 10 cm'den kulak ver", sonra "anahtarlı bara açık, servolar konum tutuyor ... dinleyen kişi
  erişim alanına girmez, hoparlöre yandan yaklaşır" ve "tekrar dinle" (`T4:67-69`). Anahtarlı bara kafa servolarının yanında **kol servolarını**
  ve motor sürücülerini de besler (`elektrik.md:60`); hoparlör göğüste, ev pozundaki kolların hemen yanında. Göğse 10 cm'ye yaklaşmak erişim
  alanına girmektir; adım kendi içinde çelişiyor ve ortak kural 7'ye aykırı. Düzeltme: servo açıkken dinleme erişim alanının dışından yapılır
  (ya da telefon/ses ölçer enerji yokken hoparlörün 10 cm önüne sabitlenir, kayıt alan dışından izlenir); "kafa servolarına güç ver" yerine
  "anahtarlı barayı aç (kollar da güçlenir)".
- **T5:** Sigorta yalnız enerji kesikken; servo gücü kapalı ya da kollar destekli. ✔
- **T6:** B2'de kimse yaklaşmıyor; C1 söküm enerji kesikken. ✔
- **T7:** Giriş kutbu kontrolü kaynak kapalıyken; seri ölçer bağlama/sökme enerji kapalıyken, uç V'ye geri; kaynak 2 A sınırlı. ✔
- **T8:** Bilek ölçümü uzun uçla, alan dışından; komut veren de dışarıda; yük direnci ve soğutucu uyarıları yerinde. ✔
- **T9:** Acil stop cümlesi iki yerde; iki ip; düşme hattı; hareket varken el yok; aletler düz zeminde enerjisizken; ilk deneme düşük hız.
  A'da ip aks yüksekliğinde (kayma devrilmeden önce gelir). ✔ Kalan öneriler: R3 (ip boyu), R4.

## Kalan düzeltmeler

Zorunlu (küçük):
- **R1 (T4 adım 5):** Servo/anahtarlı bara açıkken hoparlöre 10 cm'den dinleme kaldırılsın; dinleme erişim alanının dışından ya da enerji
  yokken yerleştirilmiş telefon/ses ölçerle. "Kafa servolarına güç ver" → "anahtarlı barayı aç (kol servoları ve motor sürücüsü de güç alır)".
- **R2 (T1 adım 5 ve KALIR satırı):** CC kararı **kaynağın CC lambası ya da akım göstergesinin 5,0 A'de olmasıyla** verilsin. Motor ucu 11,8 V'un
  altında ama kaynak CC'de değilse (seri multimetre ve kablo düşümü: 2,8 A × ~0,1 Ω ≈ 0,3 V) bu CC değildir: kaynak gerilimi motor ucunda
  12,0 V okunana kadar artırılır (en çok 12,8 V) ya da seri ölçer çıkarılıp kaynağın kendi göstergesi kullanılır. Aksi halde "durma akımı ≥ 5 A"
  diye yanlış KALIR çıkar.

Önerilir:
- **R3 (T9 alet):** Taban ipi boyu "en az 3 m" yerine "rampa boyu + dayanaktan ipçiye mesafe + 1 m"; ipçinin 1,6 m dışında durabilmesi için
  3 m çoğu rampada yetmez. Robotu süren/acil stopu tutan kişi de düşme hattı dışındakiler listesine yazılsın. İsteğe bağlı adım 13'teki ip
  kantarı adım 8'de (enerji yokken) takılsın.
- **R4 (T9):** 1,6 m ve 4–6 cm değerlerinin yanına "(varsayım)" yazılsın; adım 10'a "ivme 1 s içinde sabit değilse (S eğrili kalkış) enkoder
  kaydı esastır" notu.
- **R5 (T3):** "S0/S1'de seri multimetre yalnız aletin süre sınırı 5 dk'yı karşılıyorsa; karşılamıyorsa S0/S1'de de pens."
- **R6 (T8):** Multimetre MIN yakalaması ~100 ms'nin altındaki çökmeleri kaçırabilir; "reset/titreme gözlemi" asıl ölçüt olarak kalsın (zaten tabloda).

## HTML ve betik

`py -3 planlama\d158\testler\testler_html.py --kontrol` → "md dosyası: 10 (kâğıt T: 9), HTML bölümü: 10, iç bağlantı: 41, id: 118, KONTROL GEÇTİ",
çıkış 0; `testler.html` zaman damgası değişmedi (21:30:55.356). Bağımsız: `<table>` 58 = .md tablo 58; HTML'de `**`/ters tırnak 0; dış kaynak 0;
baskıda boş hücre 8 mm. Takma ad `testler/` ve günlükte 0; yeni kişisel veri yok.

---

# Yeniden kontrol 2 (düzeltme turu 2 sonrası) — ajan B, 08.11.2026

Kapsam: R1–R6 ve değişen beş kâğıt (T1, T3, T4, T8, T9; 21:36 sürümleri). Yalnız bu bölüm eklendi.

## Son karar

**Paket: GEÇER.** R1–R6'nın altısı da uygulanmış. Öğrenciyi yaralayacak ya da aküyü kısa devre ettirecek kalan bir adım yok.

| Kâğıt | Son karar |
|---|---|
| 00-genel | GEÇER |
| T1 | GEÇER |
| T2 | GEÇER |
| T3 | GEÇER |
| T4 | GEÇER |
| T5 | GEÇER |
| T6 | GEÇER |
| T7 | GEÇER |
| T8 | GEÇER |
| T9 | GEÇER |

## R1–R6 doğrulaması

| # | Kâğıtta gördüğüm | Durum |
|---|---|---|
| R1 | `T4:67-72`: (1) anahtarlı bara kapalı, ses yok, 10 cm'den dinle; (2) **enerji yokken** telefon hoparlörün 10 cm önüne sabitlenir, herkes erişim alanı dışına; (3) anahtarlı bara açılır ("kol ve kafa servoları ile motor sürücüsü de güç alır", `elektrik.md:60`), hareket komutu yok; dinleme alan dışından ya da telefon kaydından; (4) bara kapatılır, telefon sonra alınır | ✔ |
| R2 | `T1:81-85`: CC'yi yalnız kaynağın CC lambası ya da 5,0 A göstergesi belirler; motor ucu < 12,0 V ama CC yoksa enerjiyi kes, kaynağı artır (en çok 12,8 V), motor ucunda 12,0 V; ya da seri ölçeri çıkar. KALIR satırı `T1:133` "düşük gerilim tek başına CC sayılmaz". 11,8 V kâğıtlardan kalkmış (yalnız günlüğün tur 1 satırlarında tarihçe olarak duruyor) | ✔ |
| R3 | `T9:46` taban ipi ≥ rampa boyu + dayanaktan ipçiye mesafe + 1 m; `T9:61` robotu süren / acil stopu tutan da düşme hattı dışında; `T9:90` kantar adım 8'de, enerji yokken; `T9:110` alan dışından okunur | ✔ |
| R4 | `T9:60` 1,6 m "varsayım" + gerekçe; `T9:101` 4–6 cm "varsayım"; `T9:103-104` S eğrili kalkış/duruşta enkoder esas, video yalnız not | ✔ |
| R5 | `T3:37`, `T3:59`: seri ölçer S0/S1'de yalnız 10 A süre sınırı 5 dk'yı karşılıyorsa, yoksa pens | ✔ |
| R6 | `T8:89-90`: MIN ~100 ms altını kaçırabilir; asıl ölçüt reset/titreme gözlemi | ✔ |

## R1: bara kapalıyken gerçekten hiçbir servo ya da motor güç almıyor mu?

`elektrik.md:60`, `elektrik.md:219` ve blok şema (`elektrik.md:286` sonrası): ana 30 A → F1 20 A → **röle K1 kontağı** → anahtarlı 12 V bara → BTS7960 sol/sağ
(dört JGB37), XL4016 A (sağ kol), XL4016 B (sol kol), XL4016 C (pan + tilt). Bütün servo ve motor güç yolları K1'den sonra. K1 kapalıyken
röleden önce kalanlar F2 (yedek), F3 (kafa: Pi, QLED, PAM), göğüs ekranı dalı, F4 (çevre 5 V: ESP32, sonar, enkoder, PCA9685/BNO055
**mantığı**) ve F5 (röle bobini). PCA9685'in mantık beslemesi olması servoyu hareket ettirmez, servo V+ XL4016'dan gelir. **Sonuç: bara kapalıyken
hiçbir servo ya da motor güç almaz ✔.** Röle yalnız mantar serbest ve GPIO12 = 1 iken çeker (`elektrik.md:222`), boot'ta pull-down ile kapalı.

Not (öneri, karar değiştirmez): `elektrik.md:227` kalan riski yazıyor: yazılım hatası ya da biri "devreye al" derse röle çekebilir.
10 cm'den dinlerken **acil stop mantarını basılı tutmak** (F5 → mantar NC → K1 bobini, donanımla keser) "bara kapalı"yı yazılımdan bağımsız
garanti eder. Bir cümle: "ilk dinlemede mantar basılı".

## R2: 12,8 V üst sınırı güvenli mi?

Evet. (1) Motor robotta zaten akünün 12,8–14,4 V'unu görüyor (`elektrik.md:54`); 12,8 V çalışma aralığının alt ucu. (2) Durma akımı gerilimle
orantılı: 2,8 A × 12,8 / 12,0 ≈ 3,0 A, kaynağın 5,0 A sınırının altında; sınır değişmiyor, gerçek akım büyükse kaynak yine CC'ye girer ve deneme
"CC" sayılır. (3) Durmadaki ısı V² ile ~%14 artar; deneme en çok 5 s, arada 1 dk soğuma: önemsiz. (4) Ayar enerji kesikken yapılıyor. (5) Ölçüt
motor ucunda 12,0 V olduğu için 12,8 V'a çıkmak torku şişirmez. Küçük boşluk (öneri): 12,8 V'ta da motor ucu 12,0 V'a ulaşmazsa (> 0,8 V
düşüm) seri ölçerin çıkarılması zorunlu olsun; şimdi "istersen" diye yazıyor.

## Değişen kâğıtlarda yeni sorun taraması

T1, T3, T4, T8, T9 baştan okundu. Yeni bir güvenlik ya da hesap hatası yok. T1 μ eşikleri (9,2 / 10,5 / 12,1) ve 17,2 değişmemiş.

## HTML ve betik

`py -3 planlama\d158\testler\testler_html.py --kontrol` → "md dosyası: 10 (kâğıt T: 9), HTML bölümü: 10, iç bağlantı: 41, id: 118, KONTROL GEÇTİ",
çıkış 0; `testler.html` değişmedi (21:36:05.423). `<table>` 58 = .md tablo 58; `**`/ters tırnak 0; yeni metinler HTML'de var
("anahtarlı barayı aç", "yalnız kaynağın kendisi"). Takma ad 0.

## Kalan öneriler (karar değiştirmez)

1. T4 adım 5: ilk dinlemede acil stop mantarı basılı.
2. T1 adım 5: 12,8 V'ta da motor ucu 12,0 V'a ulaşmıyorsa seri ölçer çıkarılır (kâğıttaki "istersen" yerine "çıkar").
