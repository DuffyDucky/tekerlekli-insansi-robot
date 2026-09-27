# Proje planı

Kaynak: `raporlar/Humanoid-Robot-Fizibilite-Raporu.html` (26 Eylül 2026). Tarihler güz dönemine göre;
rakamların çoğu tahmin, teklif ve bölüm onayıyla kesinleşecek.

## Kapsam

**1. dönem hedefi:** konuşan, tekerlekle gezen, kollarıyla kayıtlı jest yapan robot.
**Esnek hedef (yetişirse 1. dönem sonu, yoksa 2. dönem):** kamerayla yüzü algılayıp kafayı kişiye
çevirme, düğmeyle "ne görüyorsun?".
**Kapsam dışı:** yüz tanıma (kimlik), otonom gezinme (ROS 2 / Nav2), eşya tutan kol.

Kapsam 2. haftada yazılı olarak dondurulur; yeni fikirler 2. dönem listesine yazılır.

## Takvim (güz dönemi ≈ 15 hafta)

| Hafta | İş | Çıktı |
|---|---|---|
| 1–2 (29 Eyl – 12 Eki) | Rol dağılımı, hoca onayı, kapsam belgesi. SolidWorks'te yerleşim, tork ve devrilme hesabı. Malzeme listesi ve sipariş | Onaylı kapsam, sipariş |
| 3–5 | Paralel: masada konuşan düzenek (Pi + mikrofon + hoparlör) · taban şasi, motorlar, ESP32 hız kontrolü, kumandayla sürüş · güç dağıtımı ve acil stop | Üç alt sistem ayrı ayrı çalışıyor |
| **6** | **İlk uçtan uca sürüm:** konuşan kafa tabanın üstünde, kumandayla geziyor. Bundan sonra her hafta entegrasyon testi | Çalışan ilk robot |
| 7–10 | 3D baskı gövde ve kollar, jest kütüphanesi, yüz ekranı, davranış akışı, çevrimdışı yedek mod | Tam görünüşlü robot |
| 11–12 | Hafif görüntü (yetişirse) | Kişiye dönen kafa |
| **13–15** | Sağlamlaştırma: 3 senaryo × 20 deneme, yedek parça, demo kontrol listesi, rapor | Teslim / demo |
| 2. dönem | Görüntü modülünü olgunlaştırma, belki tek hazır kolla (SO-101) nesne tutma, Teknofest / TÜBİTAK 2209-A | Genişletme |

Kapasite (tahmini): 4 kişi × haftada ≈ 8 saat × 15 hafta ≈ 480 kişi-saat. Yazılım 150–220 saat,
mekanik + elektrik + montaj 150–250 saat → 1. aşama sığar, hafif görüntü sınırda.

## Roller

| Rol | Kim | İş |
|---|---|---|
| Mekanik + proje lideri | Duffy | Tasarım (SolidWorks), montaj, takvim, satın alma, hoca ve sponsor ilişkisi |
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
| Devrilme, servo yetersizliği | CAD hesabı baskıdan önce; akü en altta |
| 2. dönemde staj | Bölüme sor; asıl hedefi 1. döneme göre kur |
| Yazılım sorumlusunun ayrılması | Ortak depo; ikinci kişi de konuşma zincirini çalıştırabilsin |

## İlk iki hafta

1. Robotun amacını hocayla netleştir (karşılama / tanıtım / rehber).
2. 4 kişinin rollerini yaz.
3. Bölümde hazır malzemeyi listele.
4. Tasarımı SolidWorks'e taşı (`tasarim/cad/Humanoid-Robot-Montaj.step`), ölçüleri gözden geçir.
5. Malzeme listesini kesinleştir (`tasarim/cad/parca-listesi.csv` + raporun bütçe tablosu), siparişi ver.
6. İşletmede Mesleki Eğitim takvimini bölüme sor.
