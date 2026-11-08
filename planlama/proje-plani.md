# Proje planı

Kaynak: `raporlar/Humanoid-Robot-Fizibilite-Raporu.html` (26 Eylül 2026). Tarihler güz dönemine göre;
rakamların çoğu tahmin, teklif ve bölüm onayıyla kesinleşecek. Tasarımın tek kaynağı FreeCAD modeli (`tasarim/freecad/`).
**Ana tasarım 1,58 m** (03.11.2026'dan beri, `planlama/baski-listesi.md`; iş döngüsü `planlama/dongu-158.md`): boy 1.580,0 mm ve
1.177 parça (`tasarim/freecad/lale158/lale158-kontrol.json`, `toplam_boy_mm`, `parca`), kütle 25.910,6 g (400 g kablo payı dahil;
`tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json`, `ev.kutle_g`), 10 servo (kol başına 4: omuz S1 ve S2 DS3235, dirsek ve
bilek MG996R; kafada pan + tilt MG996R; `planlama/d158/servo-10-oneri.md`), kafada 10,1" QLED (1280×720), göğüste 11,6" 1080p gömülü ekran.
Malzeme listesi `planlama/maliyet.json` henüz 1,65 m sayılarıyla (29.10; ≈ 103.800 TL, %15 pay ve yedek dahil); 1,58 m sipariş
paketi P8.1'de çıkacak. Önceki ana tasarımlar tarihçedir: 125 cm V3 (Ekim başı) ve 1,65 m (29.10 – 03.11; 1.120 parça, 24,6 kg,
kol başına 4 servo, iş planı `planlama/dongu.md` Y1–Y6).

**Tek takvim (15 Ekim 2026, D6):** hafta numarası **dönem haftasıdır**, H1 = 28 Eylül – 4 Ekim 2026 (pazartesi başlar).
`yazilim-plani.md` aynı numarayı kullanır. Teslim tarihi 1–2 hafta oynayabilir (Ahmet, 11 Ekim 2026).
**08.11.2026 (P9.1):** sipariş verilmedi (`planlama/siparis-farki-2026-10-29.md:3`; liste hocada). Eski takvimdeki H9 (23–29 Kas)
"ilk sürüş" hedefi sipariş olmadan tutmaz. Takvim artık **sipariş gününe göre** yazılır: S = siparişin verildiği gün, S+n = n hafta sonra.
15 Ekim takvimi aşağıda tarihçe olarak duruyor.

Dönem haftaları (kalan): H7 9–15 Kas · H8 16–22 Kas · H9 23–29 Kas · H10 30 Kas – 6 Ara · H11 7–13 Ara · H12 14–20 Ara ·
H13 21–27 Ara · H14 28 Ara – 3 Oca (1 Ocak tatil) · **H15 4–10 Oca · H16 11–17 Oca (teslim / demo)**.

## Kapsam

**1. dönem hedefi:** konuşan, tekerlekle gezen, kollarıyla kayıtlı jest yapan robot.
**Esnek hedef (yetişirse 1. dönem sonu, yoksa 2. dönem):** kamerayla yüzü algılayıp kafayı kişiye
çevirme, düğmeyle "ne görüyorsun?".
**Kapsam dışı:** yüz tanıma (kimlik), otonom gezinme (ROS 2 / Nav2, lidar, haritalama; hoca 21 Ekim 2026: otonomi iptal, ROS 2 yok), eşya tutan kol.
Kumanda telefondan.

Kapsam 2. haftada yazılı olarak dondurulur; yeni fikirler 2. dönem listesine yazılır.

## Kritik yol (08.11.2026)

Süreler hafta (hf). Kaynağı olmayan süre **varsayım** diye yazıldı. Rol: mekanik, elektrik, gömülü (ESP32 + test), yazılım.
"Nominal" kritik yolun toplamında kullanılan değer; parantez içi aralık.

| # | Aşama | Süre | Bağlı olduğu | Rol | Dayanak |
|---|---|---|---|---|---|
| 0 | Ön hazırlık: 1,58 m sipariş listesi (P8.1), lazer kesim DXF ve teklif, akü ve stoksuz kalem teyidi, Parti 0 kuponları | S'den önce | — | mekanik | Kupon ≈ 3 sa (`baski-listesi.md`, Parti 0) |
| 1 | **Sipariş (S)** | — | Hoca onayı + ödeme | mekanik (satın alma) | Verilmedi (`siparis-farki-2026-10-29.md:3`) |
| 2 | **Teslim: Türkiye'de stoklu kalemler** (sigma profil dahil: satıcı ölçüye kesip gönderir) | **1** (0,5–2) | 1 | mekanik | Stok sayfadan (29.10 – 01.11: `maliyet.json`, `raporlar/kaynaklar/05`, `06`, `07`); kargo süresi **varsayım**. MAX98357A ve ReSpeaker Lite sayfalarında (Robotsepeti) "tedarik süresi yaklaşık 7–12 iş günü" (`05-fiyat-arastirmasi.md:578–579`) ≈ 1,5–2,5 hf; başka satıcıya genellenmedi |
| 2a | **Lazer kesim** (alt plaka 346 × 500, 14 bükme braket, 2 kontrplak) | **1** (1–2) — **koşul: DXF ve teklif S'den önce hazır, atölye ≤ 1 hf**; koşul yoksa 1,5 | 1, DXF | mekanik | **Varsayım** (`maliyet.json`: atölye, fiyat ve süre tahmini). Taban adım 4–15 (alt plaka, etek braketi, kontrplak güç paneli ve elektronik katı) ve 18 (gövde braketi) buna bağlı; lazersiz yalnız adım 1–3 (iskelet) yapılır |
| 2b | Akü | 1 (1–2) | 1 | elektrik | Victron sayfada stok 1 (15.10, `maliyet.json`); biterse Limacell "özel üretim, ort. 3 iş günü" (`06-aku-secimi.md:121`) + kargo (varsayım) |
| 2c | XVF3800 mikrofon dizisi (ithal, ön sipariş) | 4 (3–6) | 1 | yazılım | **Varsayım** (`maliyet.json`: RobotShop EU, ön sipariş). Kritik yolda değil: gelene kadar masadaki mikrofonla |
| 3 | Kupon değerlendirmesi → CAD → STL dışa aktarma | 0,5 | Parti 0 + 6808 rulman ve ısıl gömme somun elde | mekanik | `baski-listesi.md` "Tolerans", "STL durumu" (açık iş); süre varsayım |
| 4 | Baskı Parti 1–4: 65 parça, 7,63–7,68 kg, 159–160 sa; **tek yazıcı, partiler sırayla** | 4–5 (paylaşımlı yazıcı, haftada ≈ 32–40 sa) | 3; Parti 2 servo + horn (2); Parti 3 QLED + 10,1" kafa modeli; Parti 4 etek kararı E7 + akü. Akü takozu (Parti 4, 1,5 sa) adım 4 için Parti 1 arasında basılır | mekanik | `baski-listesi.md` Özet ve satır 84 (4–5 hf tahmini; durmadan ≈ 6,7 gün) |
| 5 | **Taban + iskelet** (M6 adım 1–16) | **1** | 2, 2a (adım 4–15), 2b (adım 9 akü); akü takozu Parti 4'ten öne alınır (1,5 sa) | mekanik | `planlama/adim4/M6-montaj-sirasi.md` §2; süre varsayım |
| 6 | **Elektrik:** kartlar masada (arayüz, dağıtım A/B, ön şarj), K1 kablolama (adım 17), devreye alma testi | **1** (1–1,5) | 2, 2b, 5 (kartlar 5 ile paralel) | elektrik | M6 kural 2 (elektrik testi kabuktan önce), `planlama/adim3/elektrik.md`; süre varsayım |
| 7 | **İlk sürüş** (kolsuz, kabuksuz; acil stop geçici tutucuda) | 6'nın son günleri → **S+3** | 6; ESP32 Y1 tahrik, Y3 güvenlik, Y4 kumanda masada hazır | gömülü | `yazilim-plani.md` Y1, Y3, Y4; hazır olmaları varsayım |
| 8 | **Gövde, omuz, boyun ve kafa, K2, kabuk** (M6 adım 18–36) | **2** (1,5–2,5) | 7; Parti 2 ilk günlerde lazım: omuz yuvası (adım 19, D1a), kafa servo yuvası (adım 23, E1a); Parti 3 kafa (adım 29–31); Parti 1 bantlar (adım 34–36); Parti 4 etek (adım 33) | mekanik + elektrik | M6 kural 3 (kafa kabuktan önce); süre varsayım |
| 9 | **Kollar** (M6 adım 38–41, 48) + F5 | **0,5** (0,5–1) | 8 (M6 kural 4: kollar kabuktan sonra); kol alt montajları (adım 37, 42–47) 8 ile paralel tezgâhta | mekanik | Süre varsayım |
| 10 | **Servo kalibrasyonu** (10 servo: sıfır kayması, sınırlar, sol kol işareti) | **0,5** (0,5–1) | 9; servo tablosu P5.1 (kod ↔ CAD 11 çelişki, `dongu-158.md` §5) | gömülü | `yazilim-plani.md` Y2; süre varsayım |
| 11 | **Jest + davranış:** 8 jest robotta, konuşma zinciriyle birlikte | **1** (1–2) | 10; jestler önceden FreeCAD'de (Y8), Y5, Y7 | yazılım + mekanik | `yazilim-plani.md` Y7, Y8; süre varsayım |
| 12 | **Sağlamlaştırma:** 3 senaryo × 20 deneme, yedek parça, demo listesi | **1** (1–2) | 11 | hepsi | `yazilim-plani.md` Y12; süre varsayım |
| 13 | Teslim / demo | — | 12 | hepsi | H15–16 (4–17 Oca) |

**Kritik yol:** 1 → max(2, 2a) → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.

**Durum A (iki koşul sağlanırsa): S → demo hazır = 8 hafta nominal.** Koşullar:
(a) **Baskı, tek yazıcıda (haftada ≈ 32–40 sa ayrılmış) şu sırayla:** kupon parçaları erken alınır (aşağıda "S'yi beklemeden"),
Parti 0 basılıp değerlendirilir, STL'ler dışa aktarılır; **Parti 1 (68–69 sa) S'den önce, ≈ S−0,5'te başlar ve ≈ S+1,5'te biter**;
Parti 2 (28–29 sa; servo S+1'de gelip ölçülünce) ≈ S+1,5 → S+2,3; Parti 3 (≈ 17 sa) ≈ S+2,3 → S+2,8; Parti 4 (≈ 46 sa) ≈ S+2,8 →
S+4–4,5. **Baskının tamamı ≈ S+4,5'te biter.** Aşama 8'in ilk adımları (omuz yuvası adım 19, kafa servo yuvası adım 23) Parti 2'yi
ister; Parti 2 S+2,3'te bittiği için S+3'te başlayan aşama 8 beklemez, etek (Parti 4, adım 33) aşamanın ortasına yetişir. Parti 1
S+3'e kadar sürerse Parti 2–4 (≈ 91 sa) S+5,3–5,8'e kayar ve A'nın 8 haftası tutmaz.
(b) Lazer kesim ≤ 1 hf (DXF ve teklif S'den önce).
Tablodaki aralıklardan: iyimser 1 + 1 + 1 + 1,5 + 0,5 + 0,5 + 1 + 1 = **7,5**; nominal 1 + 1 + 1 + 2 + 0,5 + 0,5 + 1 + 1 = **8**;
kötümser 2 + 1 + 1,5 + 2,5 + 1 + 1 + 2 + 2 = **13** hf (aşama sırasıyla: max(2, 2a), 5, 6, 8, 9, 10, 11, 12).

**S = 16.11 için A'nın hazırlık takvimi (hepsi ≈ 12.11'e kadar):** 9.11 kupon parçalarının erken alımı (karar) ve sipariş; 9–10.11
Parti 0 kuponları (≈ 3 sa); 11–12.11 parçalar gelir (stoklu satıcı, 2–3 iş günü **varsayım**), kupon değerlendirmesi, CAD ve STL dışa
aktarma (açık iş, FreeCAD) — **varsayım (plandaki 0,5 haftalık aşama bir güne indirildi)**; **12.11 Parti 1 başlar** → ≈ 25.11 biter; Parti 2 ≈ 25.11 → 1.12; Parti 3 → ≈ 5.12; Parti 4 → ≈ 17.12.
Bir gün kayma Parti 1'in bitişini bir gün kaydırır; Parti 1 16.11'de başlarsa baskı ≈ S+5'te biter, aşama 8 ≈ 0,5 hf kayar.
S = 30.11 için aynı hazırlığın son günü ≈ 26.11 (Parti 1 → ≈ 9.12, baskı ≈ 31.12).

**Durum B (koşullar yoksa): ≈ 9,5–10 hafta nominal.** Kupon için rulman ve ısıl gömme somun siparişle gelir; kupon
değerlendirmesi + STL dışa aktarma sonrası baskı ≈ S+1,5'te başlar, 159–160 sa paylaşımlı yazıcıda (haftada ≈ 32–40 sa, 4–5 hf
tahmininden) biter ≈ S+5,5–6,5; aşama 8 ≈ +1,5–2 hf gecikir (gövde + kabuk S+6,5–7). Lazer 1,5 hf sürerse ilk sürüş S+3,5'e kayar,
ama bu yarım hafta aşama 8'in baskıyı beklediği sürenin içinde kalır; toplama ayrıca eklenmez.

M6 dayanağı notu: M6 tablosu 125 cm modelinden; 1,58 m'de göğüs ekranı ve 10,1" kafa ekranı adımları henüz yazılmadı
(`planlama/rehber/R-gunluk.md` "Yapılacaklar" 2–4). Adım numaraları rehber yeniden üretilince kayabilir.

## Takvim (sipariş gününe göre; 08.11.2026)

Her satır bir kapıya bağlı: önceki kapı geçmeden satırın kritik işi başlamaz. Tablo durum A'yı gösterir; durum B'nin kaymaları
"İki örnek"te.

| Göreli hafta | Kritik iş | Bağlı olduğu kapı | Paralel işler | Çıktı / kapı |
|---|---|---|---|---|
| S'den önce (H7) | Sipariş listesi (P8.1), DXF ve lazer teklifi, stok teyidi | Hoca onayı | Kupon parçalarının erken alımı (karar) → Parti 0 kuponları → CAD/STL → **Parti 1 başlar ≈ S−0,5** (16.11 için 12.11); ses hattı masada (Y5); ESP32 Y1, Y3, Y4 masada; jestler FreeCAD'de (Y8) | Verilebilir sipariş |
| S → S+1 | Teslim (stoklu kalemler) + lazer kesim | S | Yazıcı: Parti 1 sürer (+ akü takozu); elektrik kartları masada | Parçalar elde |
| S+1 → S+2 | Taban + iskelet (adım 1–16) | Teslim + lazer kesim + akü | Yazıcı: Parti 1 biter ≈ S+1,5 → Parti 2 (servo S+1'de gelip ölçüldü); kartlar | Taban mekanik olarak tamam |
| S+2 → S+3 | K1 kablolama + devreye alma | Taban + akü | Yazıcı: Parti 2 biter ≈ S+2,3 → Parti 3 (QLED) ≈ S+2,8 → Parti 4 başlar | **Kapı 1: ilk sürüş** (kolsuz, kabuksuz) |
| S+3 → S+5 | Gövde, omuz, kafa, K2, kabuk (adım 18–36) | Kapı 1 + Parti 2 (adım 19, 23) + Parti 3 (adım 29–31) + Parti 1 bantlar; Parti 4 etek (adım 33) | Yazıcı: Parti 4 biter ≈ S+4–4,5; kol alt montajları tezgâhta; sürüş testleri | Robotta konuşan kafa, kapalı kabuk |
| S+5 → S+6 | Kollar (adım 38–41, 48) + kalibrasyon | Kabuk (M6 kural 4) | Jest dosyalarının son kontrolü | Kollar sınırlar içinde |
| S+6 → S+7 | Jest + davranış entegrasyonu | Kalibrasyon | Göğüs ekranı arayüzü, çevrimdışı yedek | **Kapı 2: konuşan + gezen + jest yapan robot** |
| S+7 → S+8 | Sağlamlaştırma (3 × 20 deneme) | Kapı 2 | Rapor, demo videosu | **Kapı 3: demo hazır** |
| S+8 → | Tampon / demo | Kapı 3 | Esnek hedef (yetişirse) | Teslim |

### İki örnek

Tarih, kapının bittiği günün tarihi (tam haftalarda pazar). **Durum A:** erken kupon alımı, Parti 1 ≈ S−0,5 → S+1,5, baskı ≈ S+4,5'te biter, lazer ≤ 1 hf.
**Durum B:** bu koşullar yok (baskı S+1,5'te başlar, lazer 1,5 hf olabilir).

| Kapı | A göreli | S = 16.11, A | S = 30.11, A | B göreli | S = 16.11, B | S = 30.11, B |
|---|---|---|---|---|---|---|
| Teslim (stoklu) | S+1 | 22.11 (H8) | 6.12 (H10) | S+1 | 22.11 (H8) | 6.12 (H10) |
| Taban | S+2 | 29.11 (H9) | 13.12 (H11) | S+2,5 | 3.12 (H10) | 17.12 (H12) |
| **İlk sürüş** | S+3 | **6.12 (H10)** | **20.12 (H12)** | S+3,5 | **10.12 (H11)** | **24.12 (H13)** |
| Gövde + kabuk | S+5 | 20.12 (H12) | 3.01 (H14, yılbaşı) | S+6,5–7 | 31.12 – 3.01 (H14) | 14–17.01 (H16) |
| Kollar + kalibrasyon | S+6 | 27.12 (H13) | 10.01 (H15) | S+7,5–8 | 7–10.01 (H15) | 21–24.01 (dönem sonrası) |
| **Konuşan + jest yapan robot** | S+7 | **3.01 (H14)** | **17.01 (H16)** | S+8,5–9 | **14–17.01 (H16)** | **28–31.01** |
| **Demo hazır** | S+8 | **10.01 (H15)** | **24.01** | S+9,5–10 | **21–24.01** | **4–7.02** |
| **H15–16'ya sığıyor mu** | | **Evet**, H16 bir hafta tampon | **Hayır**, ≈ 1 hf açık | | **Hayır**, ≈ 0,5–1 hf açık | **Hayır**, ≈ 2,5–3 hf açık |
| Kesinti 2 + 3 ile (≈ −1 hf) | | 3.01, iki hafta tampon | 17.01: yalnız demo H16'nın son günündeyse, tampon yok | | ≈ 14–17.01: tampon yok, yalnız demo H16'nın son günlerindeyse | ≈ 28–31.01: sığmaz |

- **S = 16.11:** **yalnız durum A'da** sığar (bir hafta tampon). Bunun için erken kupon alımı ve DXF/teklif **bu hafta (H7)** olmalı.
  Durum B'de demo hazır ≈ 21–24.01, H16'ya sığmaz; kesinti 2 + 3 ile ≈ 14–17.01, tampon yok. A'da kötümser sürelerle (+5 hf)
  de sığmaz. Yılbaşı haftası (H14) jest işine denk gelir; ekip ve kargo kapasitesinin düşmesi **varsayım**.
- **S = 30.11:** durum A'da kesinti 2 + 3 ile demo hazır 17.01 (H16 pazarı), tampon yok; yalnız demo H16'nın son günündeyse yetişir.
  Gerçekçi yol teslimi 1–2 hafta kaydırmak (yukarıdaki 11 Ekim notu), hoca kararı. Durum B'de kesintiyle de sığmaz.

**Son güvenli sipariş günü** (demo günü bilinmiyor; "tamponsuz" = demo H16'nın son günü 17.01'de):

| | Bir hafta tamponla (demo hazır 10.01) | Tamponsuz | Kesinti 2 + 3 ile, tamponsuz |
|---|---|---|---|
| Durum A (8 hf) | **16.11** | 23.11 | 30.11 |
| Durum B (9,5–10 hf) | 2–6.11 (geçti) | 9–13.11 (9.11 yarın; hoca onayı ve ödeme birkaç günde beklenmediği için fiilen kaçırıldı, varsayım) | 16–19.11 |

30.11'den sonra (A) ya da ≈ 16–19.11'den sonra (B) kesintiyle de sığmaz: teslim kaydırma kararı gerekir.

### Kesinti sırası (sığmazsa, baştan başlayarak)

Korunacak çekirdek: konuşan + tekerlekle gezen + kayıtlı jest yapan robot (1. dönem hedefi), acil stop ve devreye alma testi.

1. **Esnek hedef** (yüz takibi, "ne görüyorsun?") tamamen 2. döneme. Kritik yolu kısaltmaz ama yazılıma 20–30 sa açar (Y11); kamera zaten stokta yok (`maliyet.json`).
2. **Jest 8 → 4** (selam, el sallama, işaret etme, onaylama): aşama 11 ≈ −0,5 hf.
3. **Sağlamlaştırma 3 senaryo × 20 → 2 senaryo × 10:** aşama 12 ≈ −0,5 hf.
4. **Göğüs ekranı menüsü → sabit tanıtım ekranı (Y10), çevrimdışı yedek (Y6) → mobil modem + bas-konuş:** yazılım yükü azalır, kritik yolu kısaltmaz.

**Kesinti değil, karar maddesi: gövde kabuğu (F2–F4) tamamen dışarıda demo.** Kabuğun bir kısmını sonraya bırakmak M6 ile çelişiyor:
omuz bandı göğüs bandına bindirme cıvatalarıyla bağlı (`tasarim/freecad/kabuk/kabuk_parcalar.py`); F3'te ekran ve M5 braket omuz
bandı yokken üstten takılıyor; F4 kollardan (G1) önce olmalı (M6 kural 4). Kazanç montajda yalnız saatler (F2 + F3 ≈ 21 M3 + 4 M5
cıvata), asıl kazanç baskıda ve yalnız durum B'de (Parti 1'in çoğu bant). Bedeli: kabuğu sonradan takmak kol başına ≈ 25 cıvata
söküm ister (M6 §3); 11,6" göğüs ekranı göğüs bandının cebinde olduğu için o da ertelenir. Karar Ahmet'in; yukarıdaki tarihlere katılmadı.

### S'yi beklemeden yapılabilecekler

- Parti 0 kuponlarını şimdi basmak. Kupon değerlendirmesi şunları ister: 6808 × 4 ve 625ZZ × 5 rulman, M3 × 168 ve M5 × 6 ısıl gömme
  somun (kupon A, B, C), kupon D için 2 × M3×20 DIN 912 + 4 pul + 2 × DIN 985 (`tasarim/freecad/test/README.md`). `maliyet.json`
  birim fiyatlarıyla ≈ **1.496 TL** (427,20 + 148,35 + 876,96 + 37,62 + kupon D 6,24: M3×20 2 × 1,30 `maliyet.json:136` M3 imbus
  satırı, pul 4 × 0,40, DIN 985 2 × 1,02; M5 ısıl gömme ve bağlantı elemanı fiyatları tahmini). Bunlar bu hafta alınırsa Parti 1 (24 parça, 68–69 sa) S'den önce başlayıp ≈ S+1,5'te biter ve baskı kritik yoldan çıkar
  (durum A; S = 16.11 için hazırlık ≈ 12.11'e kadar, yukarıdaki takvim).
  **Satın alma kararı Ahmet'in.** Filamentin elde olduğu varsayıldı (`baski-listesi.md`: firma + ekip karşılar).
- Lazer kesim DXF'ini hazırlayıp teklif almak (2a ≤ 1 hf koşulu).
- Stoksuz kalemlere ikinci satıcı (P8.1); en önce kritik yoldakiler: mesafe burcu M5 × 40 (Türkiye'de bulunamadı; baskılı burç + uzun
  cıvata seçeneği `05-fiyat-arastirmasi.md` "Açık kalanlar"), ön şarj rölesi K2, optokuplör, kart burcu seti.
- Jestleri FreeCAD'de hazırlamak (Y8) ve servo tablosunu kodla eşlemek (P5.1): aşama 10–11'i kısaltır.
- 10,1" kafa modelini bitirmek (F1a): Parti 3'ün ön koşulu.

### Dış tarihler

- TÜBİTAK 2209-B rektör e-imzası: 16–23.11 (H8 – H9 pazartesi). Kaynak: Ahmet'in bildirimi (P9.1 brief'i); depoda belge yok.
  S = 16.11 senaryosunun ilk haftasıyla çakışır.
- Final sınav haftaları ve demo günü kaynaklarda yok (doğrulanmadı).

### Tarihçe: 15 Ekim takvimi (sipariş Ekim ortası varsayımıyla; 08.11'de geçersiz)

Takvim, yazılım planının 11 Ekim takvimine hizalanmıştı: eski "H6 ilk uçtan uca sürüm" hedefi, sipariş Ekim ortasına kaydığı için H9'a taşınmıştı.

| Hafta (tarih) | İş | Çıktı |
|---|---|---|
| H1–2 (28 Eyl – 11 Eki) | Rol dağılımı, hoca onayı, kapsam belgesi. FreeCAD V3 yerleşim, tork ve devrilme hesabı. Malzeme listesi | Onaylı kapsam, V3 CAD (125 cm) |
| H3–4 (12 – 25 Eki) | Düzeltme planı (CAD ve malzeme), sipariş. Masa düzeneği: Pi ↔ ESP32 protokolü, 1 motor + 2 servo (yazılım Y0). Hoca 1,70 m + 10" kafa istedi (21 Ekim) | Sipariş verilmedi; sipariş listesi hocaya iletildi (29.10 itibarıyla; 17 Ekim listesi, 125 cm V3: 99.673 TL). Masa düzeneği konuşuyor (H4); taslak 1,70 m |
| H5–8 (26 Eki – 22 Kas) | Paralel: masada konuşan kafa (Pi + mikrofon + hoparlör, H7) · taban şasi, motorlar, ESP32 hız kontrolü, kumandayla sürüş · güç dağıtımı ve acil stop · 3D baskı (Parti 0–2) | Üç alt sistem ayrı ayrı çalışıyor |
| **H9 (23 – 29 Kas)** | **İlk uçtan uca sürüm / ilk sürüş:** elektrik robotta, kumandayla geziyor, kollar sınırlar içinde. Bundan sonra her hafta entegrasyon testi | Çalışan ilk robot |
| H10–14 (30 Kas – 3 Oca) | Gövde ve kollar (baskı Parti 3–4), jest kütüphanesi, yüz ekranı, davranış akışı, çevrimdışı yedek mod; konuşan + jest yapan robot (H11); tam görünüş ve hafif görüntü (yetişirse, H12–14) | Tam görünüşlü robot |
| **H15–16 (4 – 17 Oca)** | Sağlamlaştırma: 3 senaryo × 20 deneme, yedek parça, demo kontrol listesi, rapor | Teslim / demo |
| 2. dönem | Görüntü modülünü olgunlaştırma, belki tek hazır kolla (SO-101) nesne tutma, Teknofest / TÜBİTAK 2209-A | Genişletme |

**Tarihçe — 1,65 m geçişi (H4–5, 21–29 Ekim):** hoca 1,70 m + 10" kafa istedi, Ahmet 1,65 m'ye çekti; Y2a (CAD + bağımsız kontrol) ve Y2b
(maliyet, baskı listesi, elektrik, belgeler) bitti, kararlar 29.10 (akü yerinde, tilt ±13). Sırada Y3 M6 CAD, Y4 tam tarama, Y5 montaj
rehberi, Y6 belgeler (`planlama/dongu.md`). Hocadaki listenin o günkü tasarımla farkı `planlama/siparis-farki-2026-10-29.md` (+9.328 TL; eski kalemlerde ekleme / çıkarma serbest, Ahmet 29.10).
03.11'den beri ana tasarım 1,58 m (göğüste 11,6" ekran, kafada 10,1" QLED); Y4–Y6 `planlama/dongu-158.md`'ye taşındı. Sipariş 1,58 m sayılarıyla (P8.1) verilecek.

Kapasite (tahmini): 4 kişi × haftada ≈ 8 saat × 15 hafta ≈ 480 kişi-saat. Yazılım 150–220 saat,
mekanik + elektrik + montaj 150–250 saat → 1. aşama sığar, hafif görüntü sınırda. 08.11 itibarıyla kalan H7–H16: aynı tahminle
10 hafta × 32 ≈ 320 kişi-saat; montajın büyük kısmı S+1'den sonra.

## Roller

| Rol | Kim | İş |
|---|---|---|
| Mekanik + proje lideri | Ahmet | Tasarım (FreeCAD modeli), montaj, takvim, satın alma, hoca ve sponsor ilişkisi |
| Elektrik / elektronik | — | Akü, güç dağıtımı, motor sürücüleri, acil stop devresi |
| Yazılım / yapay zekâ | — (şart) | Konuşma zinciri, davranış akışı, sonra görüntü |
| Gömülü + test | — | ESP32 kodu, haftalık entegrasyon testleri, belgeler |

## Profesyonel destek

| Alan | Öneri |
|---|---|
| Güç elektroniği, akü güvenliği | Danışman şart (EEM hocası / öğrencisi) + hazır BMS'li LiFePO4 |
| Yapay zekâ / yazılım | Ekip ortağı şart |
| KVKK (kamera, ses) | Danışman hoca, üniversite KVKK birimi. Yüz algılama evet, tanıma hayır; kayıt yok; bilgilendirme levhası |
| 3D baskı, lazer kesim | Büyük parçalarda hizmet (orta parça 500–1.500 TL; lazer 2–5 TL/dk) |
| Mekanik tasarım, acil stop | Ekip içi (Ahmet), hoca kontrolü |

## Finansman

Ana kaynak bölüm / hoca bütçesi ve eldeki malzeme. MCBÜ BAP hoca üzerinden. Sponsorluk hemen
denenebilir (Manisa OSB). TÜBİTAK 2209-A ve 2209-B takvimi bir döneme yetişmez, 2. dönem için.

## Riskler

| Risk | Önlem |
|---|---|
| **Sipariş gecikmesi** (08.11 itibarıyla verilmedi) | Her hafta gecikme demoyu bir hafta kaydırır. Kritik yol S → demo hazır nominal 8 hf **yalnız** erken kupon alımı + Parti 1 S'den önce başlayıp ≈ S+1,5'te biterse (tek yazıcı; baskı ≈ S+4,5'te biter) + lazer ≤ 1 hf ise (durum A; S = 16.11 için hazırlık ≈ 12.11'e kadar); değilse ≈ 9,5–10 hf (durum B). Son güvenli sipariş günü: A'da 16.11 (bir hafta tampon), 23.11 (tamponsuz, demo 17.01'deyse), 30.11 (kesinti 2 + 3 ile); B'de ≈ 16–19.11 ancak kesintiyle ve tamponsuz. Sonrası teslim kaydırma kararı. Bu hafta (H7): liste (P8.1), DXF teklifi, stok teyidi, kupon parçalarının erken alımı (≈ 1.496 TL, karar) |
| Kapsam şişmesi | 2. haftada yazılı kapsam |
| Servolar yüzünden Pi'nin yeniden başlaması | Ayrı güç hatları, ortak toprak, kondansatör |
| Parça stoğu / kargo | Kalem başına ikinci satıcı (P8.1); stok sipariş anında teyit. 29.10 listesinde stoksuz ya da bulunamayanlar: mesafe burcu M5 × 40, ön şarj rölesi K2, optokuplör, IMU, kart burcu seti, servo uzatma kablosu, geniş köşe bağlantı, kamera; ithal: XVF3800 (ön sipariş), kamera kablosu. Akü sayfada tek stok → yedek Limacell |
| Baskı kapasitesi (159–160 sa, paylaşımlı yazıcıda 4–5 hf tahmini) | Parti 0–1 S'den önce; yazıcıya haftalık saat ayır; gerekirse parçanın bir kısmı online baskı hizmetine (`maliyet.json`'da kalem var). PETG-CF payı neredeyse yok (`baski-listesi.md`) |
| Demo günü internet ve gürültü | Mobil modem, çevrimdışı yedek mod, bas-konuş düğmesi |
| Devrilme, servo yetersizliği | CAD hesabı baskıdan önce; akü en altta. Karar 29.10 (1,65 m'de alındı, 1,58 m'de sürüyor): akü yerinde → yazılımda rampada kollar ev pozunda + ivme ve fren ≤ 0,1 m/s², düzde ≤ 0,5, düzde fren ≤ 1,8 m/s². 1,58 m yüksüz rampa payı 1,517 (eşik 1,5; `lale158/kafa-yerlesim/uygulama-notu.md`); el yükü ≈ 100 g (0,5 kg'da servo payı < 1; açık konu K9) |
| 2. dönemde staj | Bölüme sor; asıl hedefi 1. döneme göre kur |
| Yazılım sorumlusunun ayrılması | Ortak depo; ikinci kişi de konuşma zincirini çalıştırabilsin |

## İlk iki hafta (H1–2; çoğu yapıldı, sipariş H3–4'e kaydı)

1. Robotun amacını hocayla netleştir (karşılama / tanıtım / rehber).
2. 4 kişinin rollerini yaz.
3. Bölümde hazır malzemeyi listele.
4. Tasarım FreeCAD'de (`tasarim/freecad/`, 1,58 m; eski CadQuery V1/V2 modeli `tasarim/cad/` altında kaldı; oradaki `demo_uret.py` yalnız maliyet sayfasını üretir). Ölçüleri gözden geçir.
5. Malzeme listesini kesinleştir (`planlama/maliyet.json`, sayfası `tasarim/Robot-Tasarim-Demosu.html`), siparişi ver.
6. İşletmede Mesleki Eğitim takvimini bölüme sor.
