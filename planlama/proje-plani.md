# Proje planı

Kaynak: `raporlar/Humanoid-Robot-Fizibilite-Raporu.html` (26 Eylül 2026). Tarihler güz dönemine göre;
rakamların çoğu tahmin, teklif ve bölüm onayıyla kesinleşecek. Tasarımın tek kaynağı FreeCAD modeli (`tasarim/freecad/`; **29 Ekim 2026'dan
beri 1,65 m ana tasarım**: 1.073 parça, 24,4 kg, kol başına 4 servo, omuz DS3235, 10,1" kafa, göğüste ekran yok, taban 520 mm),
malzeme listesi `planlama/maliyet.json` (≈ 109.000 TL, %15 pay ve yedek dahil), 1,65 m iş planı `planlama/dongu.md` (Y1–Y6).

**Tek takvim (15 Ekim 2026, D6):** hafta numarası **dönem haftasıdır**, H1 = 28 Eylül – 4 Ekim 2026 (pazartesi başlar).
`yazilim-plani.md` aynı numarayı kullanır. Takvim, yazılım planının 11 Ekim takvimine hizalandı: eski "H6 ilk uçtan uca sürüm"
hedefi, sipariş Ekim ortasına kaydığı için H9'a taşındı. Teslim tarihi 1–2 hafta oynayabilir (Duffy, 11 Ekim 2026).

## Kapsam

**1. dönem hedefi:** konuşan, tekerlekle gezen, kollarıyla kayıtlı jest yapan robot.
**Esnek hedef (yetişirse 1. dönem sonu, yoksa 2. dönem):** kamerayla yüzü algılayıp kafayı kişiye
çevirme, düğmeyle "ne görüyorsun?".
**Kapsam dışı:** yüz tanıma (kimlik), otonom gezinme (ROS 2 / Nav2, lidar, haritalama; hoca 21 Ekim 2026: otonomi iptal, ROS 2 yok), eşya tutan kol.
Kumanda telefondan.

Kapsam 2. haftada yazılı olarak dondurulur; yeni fikirler 2. dönem listesine yazılır.

## Takvim (güz dönemi ≈ 15 hafta + 1 hafta pay; dönem haftası)

| Hafta (tarih) | İş | Çıktı |
|---|---|---|
| H1–2 (28 Eyl – 11 Eki) | Rol dağılımı, hoca onayı, kapsam belgesi. FreeCAD V3 yerleşim, tork ve devrilme hesabı. Malzeme listesi | Onaylı kapsam, V3 CAD (125 cm) |
| H3–4 (12 – 25 Eki) | Düzeltme planı (CAD ve malzeme), sipariş. Masa düzeneği: Pi ↔ ESP32 protokolü, 1 motor + 2 servo (yazılım Y0). Hoca 1,70 m + 10" kafa istedi (21 Ekim) | Sipariş verilmedi; sipariş listesi hocaya iletildi (29.10 itibarıyla; 17 Ekim listesi, 125 cm V3: 99.673 TL). Masa düzeneği konuşuyor (H4); taslak 1,70 m |
| H5–8 (26 Eki – 22 Kas) | Paralel: masada konuşan kafa (Pi + mikrofon + hoparlör, H7) · taban şasi, motorlar, ESP32 hız kontrolü, kumandayla sürüş · güç dağıtımı ve acil stop · 3D baskı (Parti 0–2) | Üç alt sistem ayrı ayrı çalışıyor |
| **H9 (23 – 29 Kas)** | **İlk uçtan uca sürüm / ilk sürüş:** elektrik robotta, kumandayla geziyor, kollar sınırlar içinde. Bundan sonra her hafta entegrasyon testi | Çalışan ilk robot |
| H10–14 (30 Kas – 3 Oca) | Gövde ve kollar (baskı Parti 3–4), jest kütüphanesi, yüz ekranı, davranış akışı, çevrimdışı yedek mod; konuşan + jest yapan robot (H11); tam görünüş ve hafif görüntü (yetişirse, H12–14) | Tam görünüşlü robot |
| **H15–16 (4 – 17 Oca)** | Sağlamlaştırma: 3 senaryo × 20 deneme, yedek parça, demo kontrol listesi, rapor | Teslim / demo |
| 2. dönem | Görüntü modülünü olgunlaştırma, belki tek hazır kolla (SO-101) nesne tutma, Teknofest / TÜBİTAK 2209-A | Genişletme |

**1,65 m geçişi (H4–5, 21–29 Ekim):** hoca 1,70 m + 10" kafa istedi, Duffy 1,65 m'ye çekti; Y2a (CAD + bağımsız kontrol) ve Y2b
(maliyet, baskı listesi, elektrik, belgeler) bitti, kararlar 29.10 (akü yerinde, tilt ±13). Sırada Y3 M6 CAD, Y4 tam tarama, Y5 montaj
rehberi, Y6 belgeler (`planlama/dongu.md`). Sipariş ve baskı bu sayılarla; hocadaki listenin güncel tasarımla farkı `planlama/siparis-farki-2026-10-29.md` (+9.328 TL; eski kalemlerde ekleme / çıkarma serbest, Duffy 29.10). Takvim satırları değişmedi.

Kapasite (tahmini): 4 kişi × haftada ≈ 8 saat × 15 hafta ≈ 480 kişi-saat. Yazılım 150–220 saat,
mekanik + elektrik + montaj 150–250 saat → 1. aşama sığar, hafif görüntü sınırda.

## Roller

| Rol | Kim | İş |
|---|---|---|
| Mekanik + proje lideri | Duffy | Tasarım (FreeCAD V3 modeli), montaj, takvim, satın alma, hoca ve sponsor ilişkisi |
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
| Mekanik tasarım, acil stop | Ekip içi (Duffy), hoca kontrolü |

## Finansman

Ana kaynak bölüm / hoca bütçesi ve eldeki malzeme. MCBÜ BAP hoca üzerinden. Sponsorluk hemen
denenebilir (Manisa OSB). TÜBİTAK 2209-A ve 2209-B takvimi bir döneme yetişmez, 2. dönem için.

## Riskler

| Risk | Önlem |
|---|---|
| Kapsam şişmesi | 2. haftada yazılı kapsam |
| Servolar yüzünden Pi'nin yeniden başlaması | Ayrı güç hatları, ortak toprak, kondansatör |
| Parça stoğu / kargo | İlk iki haftada sipariş, her kalem için ikinci satıcı |
| Demo günü internet ve gürültü | Mobil modem, çevrimdışı yedek mod, bas-konuş düğmesi |
| Devrilme, servo yetersizliği | CAD hesabı baskıdan önce; akü en altta. 1,65 m: akü yerinde → yazılımda rampada kollar ev pozunda + ivme ≤ 0,1 m/s², düzde ≤ 0,5, fren ≤ 1,8 m/s² (29.10); el yükü ≈ 100 g (0,5 kg'da servo payı < 1; açık konu) |
| 2. dönemde staj | Bölüme sor; asıl hedefi 1. döneme göre kur |
| Yazılım sorumlusunun ayrılması | Ortak depo; ikinci kişi de konuşma zincirini çalıştırabilsin |

## İlk iki hafta (H1–2; çoğu yapıldı, sipariş H3–4'e kaydı)

1. Robotun amacını hocayla netleştir (karşılama / tanıtım / rehber).
2. 4 kişinin rollerini yaz.
3. Bölümde hazır malzemeyi listele.
4. Tasarım FreeCAD'de (`tasarim/freecad/`, 1,65 m; eski CadQuery V1/V2 modeli `tasarim/cad/` altında kaldı; oradaki `demo_uret.py` yalnız maliyet sayfasını üretir). Ölçüleri gözden geçir.
5. Malzeme listesini kesinleştir (`planlama/maliyet.json`, sayfası `tasarim/Robot-Tasarim-Demosu.html`), siparişi ver.
6. İşletmede Mesleki Eğitim takvimini bölüme sor.
