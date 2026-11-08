# F8c günlüğü (P8.3 ölçüm ve test kâğıtları) — tasarım ajanı A, 08.11.2026

Brief: `planlama/d158/F8c-brief.md`. Plan: `planlama/dongu-158.md` §3 F8, kilit satırı `dongu-158.md:44`.
Yazma alanı: `planlama/d158/testler/` ve bu dosya. CAD betikleri koşulmadı, commit/push yok.

## Okunan kaynaklar
`planlama/adim3/elektrik.md` (tamamı), `planlama/dongu.md`, `planlama/dongu-158.md`, `planlama/kararlar-2026-10-29.md`,
`planlama/d158/karar-kuyrugu.md` (K1, K6, K9–K12), `planlama/adim3/T-taban-guc-pi.md`, `T2-takip.md`, `K3-kontrol.md` (JGB37 satırları),
`raporlar/kaynaklar/06-aku-secimi.md:15`, `raporlar/kaynaklar/07-gogus-ekrani-ve-5v.md`, `tasarim/freecad/lale158/kafa-yerlesim/secenekler.md`,
`uygulama-notu.md`, `tasarim/freecad/taban/taban-analiz.json` (`donus`, `motor`), `tasarim/freecad/arayuz.py:661-665`,
`kod/ortak/eklem_sinirlari.json:105-109`, `tubitak-2209b/taslak/oneri-taslak-v8.md` (H1 satır 68, yöntem 199, düzenek 175–187, 260; salt okundu).

## Üretilenler
| Dosya | İçerik |
|---|---|
| `testler/00-genel.md` | Kâğıt listesi, sıra, ortak kurallar, ortak alet listesi, kaynak kısaltmaları |
| `testler/T1-jgb37-durma-torku.md` … `T9-zemin-rampa.md` | 9 kâğıt: amaç, neden, varsayım tablosu (dosya:satır), alet, güvenlik, yöntem, boş kayıt tablosu, geçer/kalır, yönlendirme |
| `testler/testler_html.py` | .md → `testler.html` üretici (yalnız standart kütüphane) + `--kontrol` |
| `testler/testler.html` | A4 yazdırılabilir, harici kaynaksız, açık/koyu tema (sistem + düğme), her kâğıt yeni sayfada |

## Kontrol (tarayıcısız)
- `py -3 testler_html.py --kontrol` → "md dosyası: 10 (kâğıt T: 9), HTML bölümü: 10, iç bağlantı: 35, id: 117, KONTROL GEÇTİ".
  Denetlenen: her .md'nin HTML'de bölümü var; HTML'deki her `href="#…"` bir id'ye gidiyor; `<link>`, `src=`, `@import`, dış `url()` yok;
  .md içi bağlantıların hedef dosyası var; HTML .md'lerden yeniden üretilenle bayt bayt aynı; tema ve A4 kuralları var.
- Ek denetim: HTML gövdesinde kalan `**`, `*`, ters tırnak 0; .md tablo sayısı 53 = HTML tablo sayısı 53; bütün .md başlıkları HTML'de var.
  İlk sürümde kod içeren kalın satırlar (`**…`kod`…**`) çevrilmiyordu; çevirici düzeltildi, yeniden üretildi.
- Kâğıtlardaki `dosya:satır` atıfları (T1–T9'da 123 benzersiz) betikle açılıp satır içeriği okundu; hepsi doğru satıra düşüyor.
  JSON anahtar yolu atıfları (`taban-analiz.json` `donus.*`, `motor.*`) `py -3` ile okunarak doğrulandı.
- Takma ad taraması: `testler/` altında 0.

## Kâğıtlar ve geçer sınırları
| Kâğıt | Geçer sınırı (özet) | Doğruladığı varsayım (kaynak) |
|---|---|---|
| T1 JGB37 | Durma ≥ 21,0 kg·cm ve akım ≤ 2,8 A; 17,2–21 koşullu; < 17,2 kalır; ≤ 10,5 ağır | 21 kg·cm satıcı etiketi (`elektrik.md:124,126`), 2,8 A tahmini |
| T2 QLED VBUS | VBUS↔VBUS OL, diyot iki yönde OL, boştaki uçta ≤ 0,5 V | İç bağ yok (`elektrik.md:43`, doğrulanmadı) |
| T3 kafa 5 V | Pi hattı 4,80–5,20 V ve < 5,0 A; ekran hattı 4,75–5,25 V ve < 3,7 A; 12 V < 5 A; `get_throttled` 0x0 | 2,67 A / 0,9 A / 3,57 A (`elektrik.md:22-25`) |
| T4 PAM + ses kartı | PAM ≤ 0,71 A; Pi hattı < 5,0 A, ≥ 4,80 V; ses kartı ≤ 0,5 A; 0x0 | PAM 5 V D24V50F5'ten varsayım (`uygulama-notu.md:113`, K10) |
| T5 hub girişi | Hub çıkışı ≥ 4,40 V; hub girişi ≥ 4,75 V; Pi USB toplamı ≤ 1,6 A; kopma/reset 0 | Hub girişi ölçülmedi (`uygulama-notu.md:100`) |
| T6 akustik | Mikrofon–hoparlör ≥ 400 mm; 4 delik Ø3; gürültü artışı ≤ 3 dB; (C: ≤ 3 dB kayıp, DOA ≤ 10°, yankı ≥ 10 dB varsayım) | H1 (`oneri-taslak-v8.md:68,199`), Ø3 varsayım (`secenekler.md:274`) |
| T7 göğüs 12 V | Çıkış 11,4–12,6 V (10,0–14,6 V girişte); ekran ≤ 1,0 A; giriş < 2,0 A; kutup ve jak yazılı | 12 V ayar, ~0,5 A (`elektrik.md:19,54`), jak doğrulanmadı |
| T8 servo hatları | V+ arası OL; 30 dk yükte ≥ 5,5 V; soğutucu ≤ 80 °C; yoğun ≤ 5,0 A; reset 0 | 4,87 / 1,5 A, %97 (`elektrik.md:89-95`) |
| T9 zemin + rampa | 0,4 ≤ μ ≤ 0,6; rampa ≤ 5°; ivme ≤ 0,10 m/s²; teker kalkması 0 | μ senaryo, rampa 0,1 m/s² (`kararlar:7,77`) |

## Kaynak bulunamayan ya da dış kaynaklı değerler (kâğıtlarda "varsayım" / "dış kaynak" diye işaretli)
- USB 2.0 belirtimi Tablo 7-7: 4,75–5,25 V (yüksek güçlü port), ≥ 4,40 V (hub'dan beslenen port), 0,5 A cihaz sınırı — depoda yok (T3, T4, T5).
- T2: GND < 1 Ω, boştaki uç ≤ 0,5 V, diyot düşümü 0,1–0,8 V.
- T3: S2 stres süresi 30 dk. T4: en yüksek seste en çok 30 s; PAM8403 köprü (BTL) çıkış bilgisi üretici datasheet'i (depoda yok).
- T5: hub girişi ≥ 4,75 V hedefi; L3'te 0,5 A yükle altıncı cihaz taklidi.
- T6: C1 ≤ 3 dB kayıp, DOA farkı ≤ 10°, C2 yankı bastırma ≥ 10 dB (kaynakta hiç sınır yok); Pi 5 fan sysfs yolu doğrulanmadı;
  "motor gücü açık = röle çekili, PWM 0" yorumu; 6 kanallı ReSpeaker kanal düzeni Seeed wiki'sinden.
- T7: çıkış toleransı ±%5 (11,4–12,6 V).
- T1: deneme en çok 5 s, arada 1 dk soğuma.
- T9: ivme kaydında 0,5 s kayan ortalama; acil stop / güç kesik geri kayma için sınır yok (yalnız kayıt).
- T8: 5,5 V eşiği `elektrik.md:76`'daki tahmini düşümden (1,93 m uzatmalı 1,65 m hesabı); 1,58 m'de yeniden hesaplanmadı.

## Bulgular (karar değil, orkestratöre)
1. **Fan ve 3 dB çelişkisi:** `secenekler.md:251` soğutucu fanını H1'in 3 dB ölçütüne katıyor; `oneri-taslak-v8.md:199` fanı ayrı raporluyor, ölçüte katmıyor. T6 öneri metnini izledi.
2. **Yankı giderme referansı (doğrulanmadı):** ses ayrı USB ses kartından çalındığı için ReSpeaker'ın yankı gidermesinin referans alıp alamadığı belirsiz; T6 C2 bunu ölçer, yazılım ekibine soru.
3. **Rampada acil stop:** motorlar boşa düştüğü için robot rampada yuvarlanabilir (`kararlar:83`); T9'da yalnız ip gergin tutulurken ölçülür, sınır yok.
4. `karar-kuyrugu.md` P8.3'e üç iş daha bağlıyor, brief'teki 9 kâğıtta yok: **K12 kafa ısı testi** (stres, tilt servo gövdesi ≤ 50 °C;
   satır 184), **K8 kalan işi: sigorta kutusu alınınca H1 açıklığı ölçümü** (satır 149–153) ve **Y3 K7 perçin delik çapı / perçin somun ölçüsü**
   (satır 298). Yazılmadı; gerekirse ayrı kâğıt.
5. T1'de 1,58 m modelinden iki eşik türetildi: rampada 0,1 m/s² için motor başına 5,15 kg·cm (→ durma ≥ 17,2), omniyle dönüş 3,16 kg·cm (→ durma ≥ 10,5).
6. Robot kütlesi 25,911 kg akü 3,0 kg güncellemesinden (P1.1) önceki model; T9 robotu tartmayı istiyor.

## Durum
Tasarım bitti; bağımsız kontrol (ajan B) GEÇMEZ verdi (`F8c-kontrol.md`). Düzeltme turu 1 aşağıda.

## Düzeltme turu 1 (08.11.2026)

Kaynak: `F8c-kontrol.md` 15 madde. Yalnız `testler/` ve bu dosya değişti; CAD betiği koşturulmadı, commit yok.

| # | Madde | Durum | Nerede |
|---|---|---|---|
| 1 | Ortak multimetre akım uyarısı | Yapıldı | `00-genel.md` "Multimetreyle akım ölçümü" (7 madde) + ortak kural 7 (hareketli parçaya el uzatılmaz), 8 (saat/yüzük); T1, T3, T4, T7, T8 güvenliğinde bağlantı + kısa tekrar |
| 2 | T1 kaynak akım sınırı (CC) | Yapıldı | Adım 5: CC lambası ya da motor gerilimi < 11,8 V → tork geçersiz, "CC" yazılır; KALIR satırı "kaynak 5,0 A sınırına girdi" |
| 3 | T3/T4 pens öncelikli, seri düşüm | Yapıldı | T3: S2 yalnız pens, seri yalnız S0/S1; N2 Pi tarafında. T4: N2 toplamı yalnız pens, P1 PAM tarafında. Kayıt tabloları ikiye bölündü |
| 4 | T8 adım 10 uzun test kablosu, prob tutulmaz | Yapıldı | Alet: Y-ara ≥ 1 m; güvenlik "hareket varken prob tutulmaz", erişim alanı kol boyu + 0,5 m (varsayım); adım 9–11 |
| 5 | T8 C eşiği servo ucuna | Yapıldı | C: XL4016 çıkışı ≥ 5,85 V (varsayım); D: bilek servosu ucu ≥ 5,5 V; adım 6 "servolar dağıtım kartından sökülü" |
| 6 | T9 B güvenliği | Yapıldı | Taban ipi (şasi, aks yüksekliği, üstte sabit dayanak, boşluk ≤ 10 cm) ve devrilme ipi (omuz altı, ≤ 10 cm) ayrı; düşme hattı 1,6 m, ipi tutanlar ve kamera dışarıda, yan-üst çaprazda; "acil stop rampada durdurmaz, taban ipi durdurur" güvenlikte ve adım 9 başında; hareket varken el uzatılmaz; aletler düz zeminde enerjisizken takılır; ilk deneme düşük hız, ölçüm değil |
| 7 | T1 ip ön gerilmesi, kararlı kantar değeri | Yapıldı | Adım 4–5; tablo sütunu "Kantar, kararlı (kg)" |
| 8 | T1 F1 gerekçesi | Yapıldı | 5,0 A yalnız laboratuvar düzeneği sınırı; F1 gerekçesi kaldırıldı |
| 9 | T1 ağır eşiği μ'ye bağlı, kütle P1.1 öncesi | Yapıldı | μ 0,4 → 9,2; 0,5 → 10,5; 0,6 → 12,1 kg·cm (`donus.yerinde_omni`); T9 yoksa 12,1 |
| 10 | T5 L2 sırası | Yapıldı | "Enerjiyi kes → F4'ü çıkar → enerji ver" |
| 11 | T5 USB ölçer düşümü | Yapıldı | Ölçer düzeni satırı; iki ölçer / tek ölçer sırayla koşulu; sınıra 0,05 V yakınsa ölçersiz tekrar (varsayım) |
| 12 | T7 kutup kontrolü, seri akım | Yapıldı | Adım 5 kaynak kapalıyken kutup; adım 7 ve 10 seri bağlantı, gerilim ekran tarafında |
| 13 | T9 ivme yöntemi | Yapıldı | Ana yöntem enkoder (Δv ÷ Δt) ya da video + şerit metre: 1 s'de yol ≤ 5,0 cm (d = ½·a·1², sabit hız ≥ 0,1 m/s şartı); telefon yalnız yardımcı (1° ≈ 0,17 m/s²); düzde duruş ayrı tablo, sınır ≤ 1,8 m/s² (`kararlar:78`, `eklem_sinirlari.json:107`); A4 şeritleri kaldırıldı, teker kalkması videodan; "geri kayma" yerine isteğe bağlı ip yükü |
| 14 | T2 KALIR ayrımı, kesik kablo | Yapıldı | "< 10 Ω doğrudan bağ; kΩ ve üstü: adım 5–6 belirler"; adım 5'e kesik uç için USB-A dişi test kartı / klemens, adaptör prizden çıkmışken |
| 15 | HTML tablo, T6 C1 | Yapıldı | T3, T4, T5 tabloları ikiye bölündü (yatay sayfa yerine); baskıda boş satır `td:empty{height:8mm}`; T6 C1: Pi'yi kapat + enerjiyi kes, sonra sök |

**Yeni atıflar doğrulandı:** `kararlar:78` (düz fren 1,8 / sürüş 0,5), `kararlar:83`, `eklem_sinirlari.json:105-109`, `elektrik.md:450-451`
(arka enkoderler), `taban-analiz.json` `motor.hiz_m_s` = 0,393.

**Kontrol:** `py -3 testler_html.py` → `py -3 testler_html.py --kontrol`: md 10 (T 9), HTML bölümü 10, iç bağlantı 41, id 118,
KONTROL GEÇTİ. HTML'de kalan `**` 0; takma ad taraması 0.

**Bu turda eklenen varsayımlar (kâğıtlarda "varsayım" yazılı):**
- T1: motor gerilimi < 11,8 V → kaynak CC'ye girmiş sayılır.
- T5: sınıra 0,05 V yakın okuma → ölçersiz tekrar.
- T8: XL4016 çıkışı ≥ 5,85 V (uç ≥ 5,5 V'a hat düşümü payı); erişim alanı = tam uzanmış kol + 0,5 m.
- T9: 0,5 s kayan ortalama artık yalnız düzde duruş (telefon) için; video okumasında 4–6 cm "sınırda, tekrarla" bandı; düşme hattı robot boyu (1,6 m).
- Eski "T9: geri kayma için sınır yok" maddesi "isteğe bağlı ip yükü, yalnız kayıt" oldu.

**Durum:** Düzeltme turu 1 bitti; yeniden kontrol 1 KOŞULLU verdi (R1–R6).

## Düzeltme turu 2 (08.11.2026, son tur)

Kaynak: `F8c-kontrol.md` "Yeniden kontrol 1", R1–R6. Yalnız `testler/` ve bu dosya değişti.

| # | Madde | Durum | Nerede |
|---|---|---|---|
| R1 | T4 uğultu dinleme | Yapıldı | Adım 5: önce anahtarlı bara kapalıyken 10 cm'den dinle; sonra telefon enerji yokken hoparlörün 10 cm önüne sabitlenir, herkes erişim alanı dışına çıkar, "anahtarlı barayı aç (kol/kafa servoları ve motor sürücüsü de güç alır, `elektrik.md:60`)"; servo gücü açıkken kimse kol erişim alanına girmez, dinleme alan dışından ya da telefon kaydından |
| R2 | T1 CC kararı | Yapıldı | CC yalnız kaynağın CC lambası ya da akım göstergesi 5,0 A ile; motor ucu < 12,0 V ama CC yoksa enerji kesilip kaynak artırılır (en çok 12,8 V, `elektrik.md:54`), motor ucunda 12,0 V okunana kadar; ya da seri ölçer çıkarılır. 11,8 V varsayımı kaldırıldı. KALIR satırı: "motor ucundaki düşük gerilim tek başına CC sayılmaz" |
| R3 | T9 ip boyu, sürücü kişi, kantar | Yapıldı | Taban ipi ≥ rampa boyu + dayanaktan ipçiye mesafe + 1 m; robotu süren / acil stopu tutan da düşme hattı dışında; adım 13 kantarı adım 8'de enerji yokken takılır, alan dışından okunur |
| R4 | T9 varsayım işaretleri, S eğrisi | Yapıldı | 1,6 m ve 4–6 cm yanında "varsayım"; adım 10'a "ivme 1 s içinde sabit değilse (S eğrili kalkış/duruş) enkoder kaydı esastır" |
| R5 | T3 seri ölçer süre şartı | Yapıldı | S0/S1'de seri multimetre yalnız 10 A süre sınırı 5 dk'yı karşılıyorsa; yoksa pens (alet ve adım 3) |
| R6 | T8 MIN yakalama | Yapıldı | Adım 10 notu: MIN ~100 ms altı çökmeleri kaçırabilir, asıl ölçüt reset/titreme gözlemi |

**Kontrol:** `py -3 testler_html.py` → `--kontrol`: md 10 (T 9), HTML bölümü 10, iç bağlantı 41, id 118, KONTROL GEÇTİ (çıkış 0).
HTML'de kalan `**` 0; takma ad 0. `elektrik.md:54` (akü 12,8 V) ve `elektrik.md:60` (anahtarlı bara: BTS7960, XL4016 A/B/C) yeniden okundu.

**Varsayım değişikliği:** T1 11,8 V eşiği kalktı (CC artık kaynağın göstergesiyle). T9'da 1,6 m ve 4–6 cm kâğıtta "varsayım" diye işaretli.

**Durum:** Düzeltme turu 2 bitti.
