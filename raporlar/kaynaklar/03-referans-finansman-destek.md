---
title: "Kanıt: Referans projeler, finansman ve destek alanları"
created: 2026-09-26
---

> Claude Opus alt ajan raporu, 26 Eylül 2026, olduğu gibi. Rakamlar ajanın beyanıdır; "(t)", "tahmini", "doğrulanmadı" işaretleri korunmuştur.
> Not (Echo): Ajan tek kişilik ve 2 dönemlik bir proje varsaydı. Duffy'nin cevabı: 4 kişi, normalde 1 dönem, başarılı olursa 2 dönem, okul/hoca destekli bütçe. Birleşik rapor buna göre düzeltildi.

# Tekerlekli insansı robot projesi: araştırma raporu (Eylül 2026)

## Önce bilmen gereken üç şey
1. **Zaman kısa.** Öğrenci 2. sınıfta, yani büyük ihtimalle Haziran 2027'de mezun olacak. Elde kabaca 2 dönem, yaklaşık 8 ay var.
2. **TÜBİTAK parası zamanında gelmeyebilir.** 2025'te süreç şöyle işledi: başvuru Ekim–Kasım 2025, sonuç Nisan 2026, danışman onayı Mayıs–Haziran 2026. Aynı takvim tekrarlanırsa 2026 çağrısının parası 2027 ortasında gelir, bu da mezuniyete denk düşer. 2209-A'yı "yol başı" parası diye planlamak yanlış olur.
3. **Hedef, pahalı ticari robotların basitleştirilmiş bir kopyası olmalı.** Akınsoft Mini Ada (690.000 TL + KDV) 123 cm boyunda, 45 kg, 10 motorlu, 3 eksenli kollara sahip. Bu ölçü, "kollar jest yapar, nesne tutmaz" kapsamının ticari karşılığı ve hedef için iyi bir referans.

## 1. Referans projeler

| Proje | Maliyet | Ekip / süre | Açık kaynak | Ödünç alınabilecek |
|---|---|---|---|---|
| **InMoov** | Yaklaşık 1.500 €, bunun ~300 $'ı filament | Tek kişi, birkaç hafta; asıl zaman baskıya gidiyor | Evet, CC-BY-NC (ticari kullanım yasak) | Kafa (göz kamerası, çene) ve omuz STL'leri. Topluluk InMoov'u 3 tekerlekli basit bir tabana oturtmuş, yani bizim konseptle aynı. Uyarı: tam InMoov kolu çok ağır ve servo yakar. |
| **Poppy Torso** | 4.000–6.000 €; kit 5.300 € (Dynamixel motorlar) | Araştırma ekibi (INRIA) | Evet (GitHub) | Gövde kinematiği ve modüler yapı fikri. Motorları bu bütçe için fazla pahalı. |
| **Reachy 2** | 70–75 bin $ (hareketli tabanlı) | Pollen/Hugging Face, profesyonel ekip | Yazılım açık | Mimari: 3 omni tekerlek + gövde + 2 kol + LiDAR |
| **Reachy Mini** | 299 $ Lite / 449 $ Wireless (sonradan 399/499 $ diye de geçiyor) | Kit, kendin kuruyorsun | Evet, Python SDK | Kafa ifadesi (anten, baş hareketi) ve ses/görüntü etkileşim yazılımı. Kafa modülü için doğrudan örnek. |
| **XLeRobot** (LeRobot tabanlı) | Yaklaşık 660 $; SO-101 + LeKiwi zaten varsa ~250 $ | Tek geliştirici; montaj 4 saatten az; ~12 kg | Evet (GitHub, STL, BOM) | **En yakın referans.** IKEA arabası gövde, 2 adet SO-101 kol, 3 omni tekerlekli taban, hazır powerbank. BOM ve kablaj doğrudan kopyalanabilir. |
| **SO-101 / LeKiwi** | SO-101 kol 100–270 $, LeKiwi 260 $'dan başlıyor | Kit | Evet | Hazır kol ve taban. Kol tasarımıyla hiç uğraşmama seçeneği. |
| **Pepper** (SoftBank) | 198.000 yen (~1.790 $) + abonelik; üretim durdu (2020/21), 27 bin adet üretildi | Kurumsal | Hayır | Ders: sınırlı işlev ve güvenilmezlik ticari robotu bile bitirdi. Sağlam ve basit 3 senaryo, 20 kırılgan senaryodan iyidir. |
| **TIAGo** (PAL) | 34–100 bin $ | Kurumsal | ROS paketleri açık | ROS navigasyon ve manipülasyon mimarisi (ileri aşama için) |
| **Akınsoft Mini Ada / Ada-7** | Mini Ada 690.000 TL + KDV (sitede); Ada-7 655–730 bin TL (arama özeti, doğrulanmadı) | Ticari | Hayır | Özellik listesi hedef belirlemek için iyi: 10,1" ekran, LED yüz, acil stop, LiDAR, 0,6 m/s hız |
| **BTÜ "Moria"** (Bursa Teknik Üniv.) | Açıklanmadı | Mekatronik, EEM ve makine lisans/yüksek lisans öğrencileri + 2 öğretim üyesi; Şubat 2024'te başladı | Hayır | Türkiye'de akademik emsal: soru-cevap, yüz takibi. Ekip boyutu ve süresi doğrulanmadı. |

**Teknofest:** Robotik kategoriler listesinde insansı, servis ya da sosyal robot kategorisi **yok**. Seçenekler "Serbest Proje" ile "İnsanlık Yararına Teknoloji" (Sağlık / Afet alt kategorileri; üniversite ve mezun seviyesi var; en fazla 6 kişi; 2025'te üniversite birinciliği 80.000 TL). Robota bir amaç lazım, örneğin "hastane/engelli rehber robotu". 2027 takvimi henüz ilan edilmedi. 2026'da son başvuru 20 Şubat'tı, festival Eylül sonu–Ekim başındaydı. Aynı düzen sürerse final mezuniyetten sonraya kalır; mezun katılımı kuralları doğrulanmadı.

## 2. Fizibilite: yapılabilir ama şu şartlarla
- **Kollar yük taşımayacak, jest yapacak.** Kol başına 2–3 serbestlik derecesi yeterli (el sallama, işaret etme). Nesne tutmak ayrı bir proje. İstenirse tek bir hazır SO-101 kol ile demo yapılır.
- **Taban ve güç sistemi hazır alınacak.** 2 motorlu diferansiyel taban (motorlarda enkoder) ve hazır BMS'li LiFePO4 batarya. LiPo kullanılmayacak.
- **Beyin bir dizüstü veya Raspberry Pi 5 olacak.** Yapay zekâ bulut üzerinden çalışacak (konuşmayı yazıya çevirme, dil modeli, yazıyı sese çevirme). İnternet kesilirse hazır cevaplarla çalışan çevrimdışı bir yedek mod olacak.
- **ROS 2 ilk sürümde kullanılmayacak.** Python + seri port yeter. ROS 2 ancak ikinci dönemde, bilgisayar mühendisliği ortağı varsa gelir.
- **Kapsam ilk ay dondurulacak.** Tahmini malzeme maliyeti 40–70 bin TL (kendi tahminim, doğrulanmadı). Kalemler: taban ve motorlar, alüminyum profil gövde, 6–8 adet 20–35 kg servo, Pi/dizüstü, mikrofon dizisi, ekran, batarya, acil stop.

**Öğrenci robot projelerinde sık görülen çöküş nedenleri** (kaynaklı bir araştırma bulamadım, bu liste saha deneyimine dayanıyor):
- Kapsam şişmesi ("yüz tanısın, yürüsün, nesne tutsun")
- Üst gövdenin ağırlığı: 3D baskı kollar ağırlaşınca servolar yetmez, robot devrilmeye yatkın hale gelir
- Güç sistemi: servolar ani akım çeker, gerilim düşer, Pi yeniden başlar; ortak toprak hatası
- Entegrasyon ancak son haftada yapılır
- Demo günü: salonda Wi-Fi olmaz ve gürültü yüzünden ses tanıma çöker

Çözüm: 6. haftadan itibaren her hafta uçtan uca çalışan bir sürüm, yanında ayrı bir 4G modem ve yakaya takılan mikrofon.

## 3. Aşamalı yol haritası

| Dönem | Kilometre taşı | Çıktı |
|---|---|---|
| Ekim 2026 (1–4. hafta) | Ekip + danışman hoca; kapsam belgesi; SolidWorks yerleşim çizimi, devrilme ve tork hesabı | Onaylı kapsam, malzeme listesi |
| Kasım (5–8. hafta) | **MVP-0:** masada duran bir kafa. Mikrofon → konuşma tanıma → dil modeli → ses; ekranda yüz ifadesi | Sesli sohbet demosu |
| Aralık–Ocak | **MVP-1:** tekerlekli taban + gövde + acil stop; kafayı tabana taşı; uzaktan kumandayla sürüş | Dönem sonu demosu |
| Şubat–Mart 2027 | **v1:** 2 kol, önceden kaydedilmiş jestler; kafa kameradan yüz algılayıp o yöne döner (kimlik tanıma yok) | "Karşılama robotu" senaryosu |
| Nisan–Mayıs | Sağlamlaştırma: 3 senaryo × 20 deneme, yedek parça, demo kontrol listesi | Bitirme ya da fuar demosu |
| Mezuniyet sonrası (isteğe bağlı) | ROS 2 navigasyon, SO-101 ile tutma, Teknofest | Takımı küçük sınıflara devret |

## 4. Finansman

| Kaynak | Tutar | Takvim | Not |
|---|---|---|---|
| **TÜBİTAK 2209-A** | 2025 çağrısında **9.000 TL**; bazı sitelerde 12.000 TL geçiyor (2026 için doğrulanmadı) | 2025: 13 Ekim–12 Kasım (18 Kasım'a uzatıldı). 2026 çağrısı muhtemelen Ekim–Kasım 2026 (doğrulanmadı) | **Önlisans öğrencisi başvurabiliyor.** Yürütücü + en fazla 3 ortak öğrenci, tam zamanlı danışman şart, proje en fazla 12 ay. Mezun olunca proje ne olur: doğrulanmadı. |
| **TÜBİTAK 2209-B** (sanayiye yönelik) | 12.000 TL | 2209-A ile aynı | Bir akademik + bir sanayi danışmanı gerekiyor (Manisa OSB firmaları uygun olabilir) |
| **Teknofest malzeme desteği** | Tutar yayımlanmıyor; "aşamaları geçen takımlara" veriliyor | 2026'da son başvuru 20 Şubat'tı | Kategori uyumu ve takvim sorunlu (yukarıya bak) |
| **MCBÜ BAP** | Komisyon belirliyor | Sürekli | Yürütücü doktoralı öğretim üyesi olmalı, yani **hoca üzerinden** başvurulur. Öğrenci proje türü var mı: doğrulanmadı. |
| **Manisa Teknokent / TTO** | Kuluçka ve hızlandırma programları | — | Ticarileşme amacı yoksa uygun değil. Teknokariyer programı MYO'ları da kapsıyor. |
| **Sponsorluk** | Ayni ya da nakdi | Hemen | Bosch Rexroth Türkiye öğrenci robot takımlarına (FRC) makine sponsorluğu yapıyor. Manisa'da Vestel ve Bosch fabrikaları var. Robot üstünde logo karşılığı malzeme istenebilir. |

**Gerçekçi finansman:** bölüm imkânları + sponsor + kişisel bütçe. 2209 ikinci aşama için ek para olur.

## 5. Profesyonel destek matrisi

| Alan | Öğrencinin durumu | Öneri | Kimden | Tahmini maliyet |
|---|---|---|---|---|
| Mekanik tasarım, tork, devrilme | Güçlü (SolidWorks, montaj) | **Kendin yap** + hoca kontrolü | Makine veya mekatronik hocası | 0 |
| Güç elektroniği, batarya | Pano ve kablaj bilgisi var, DC/batarya tarafı zayıf | **Danışman al** + BMS'li LiFePO4 paket satın al | EEM hocası veya EEM öğrencisi | Danışmanlık 0; batarya 5–10 bin TL (tahmin) |
| PCB | Yok | İlk sürümde gerek yok (hazır modül + delikli pertinaks). Sonra **hizmet satın al** | Tasarım: EEM öğrencisi. Üretim: JLCPCB türü firmalar | Birkaç yüz TL + kargo/gümrük (doğrulanmadı) |
| Gömülü yazılım (Arduino/ESP32) | Yapay zekâ yardımıyla yapıyor | **Kendin yap**, kod incelemesi için mentor | Robot kulübü | 0 |
| Yapay zekâ ve yazılım entegrasyonu | En zayıf halka | **Ekip ortağı şart** | Bilgisayar mühendisliği / yazılım öğrencisi | Bulut API kullanımı ayda birkaç yüz TL (tahmin) |
| ROS 2 | Yok | İlk sürümde erteleyip ikinci dönemde ortakla yap | Bilgisayar mühendisliği öğrencisi, IEEE RAS | 0 |
| Endüstriyel tasarım, dış görünüm | CAD var, estetik tasarım yok | **Danışman al** (tercihen gönüllü öğrenci) | İzmir'deki endüstriyel tasarım bölümleri (İYTE, İEÜ; doğrulanmadı) | 0 ile birkaç bin TL arası |
| 3D baskı, CNC, lazer | Tasarımı yapabilir | Okulun yazıcısı ya da makerspace, büyük parçalarda **hizmet** | İzmir'deki atölyeler | 3D baskı orta boy parça 500–1.500 TL; lazer ~2–5 TL/dk |
| KVKK ve etik (kamera, ses) | Yok | **Danışman al** | Danışman hoca, gerekirse etik kurul | 0 |
| İş güvenliği, acil stop | **Güçlü** (PLC, pano) | **Kendin yap** | — | 500–1.500 TL (tahmin) |

KVKK satırının ayrıntısı: yüz *tanıma* yapma, yüz *algılama* yeterli. Kayıt tutma. Robotun yanına aydınlatma levhası koy. KVKK yüz geometrisini ve ses tınısını biyometrik veri sayıyor. 2026/921 sayılı ilke kararı, işyerinde mesai takibi için biyometrik veri işlemeyi açık rızayla bile hukuka aykırı buldu; bizim durumumuz işyeri değil ama emsal olarak "kaçın" demek için yeterli.

Acil stop satırının ayrıntısı: kırmızı mantar butonlu kablolu bir acil stop, yazılımdan bağımsız olarak kontaktör ya da röleyle motor gücünü keser. Pi ve bilgisayar açık kalır. Piyasaya çıkmayacak bir prototip için CE belgesi beklenmez; bu hukuki yorumu doğrulamadım.

## 6. Ekip
**İdeal ekip 4 kişi, en fazla 5.**
- **Mekanik + proje lideri:** bu öğrenci. SolidWorks, montaj, takvim, sponsor ilişkileri.
- **Elektrik/elektronik:** güç dağıtımı, batarya, motor sürücüleri, acil stop. MYO elektrik bölümü veya bir EEM öğrencisi.
- **Yazılım/yapay zekâ:** ses zinciri, dil modeli, görüntü işleme; ileride ROS 2. Bilgisayar mühendisliği öğrencisi.
- **Gömülü + test/demo:** Arduino/ESP32, entegrasyon testleri, belgeler. Bir alt dönem öğrencisi olursa proje mezuniyetten sonra devredilebilir.
- **Danışman:** mekatronik hocası. Ayrıca EEM ya da bilgisayar mühendisliğinden bir hocanın gayriresmî desteği.

**Ortak nasıl bulunur:**
- MCBÜ mühendislik fakültesindeki kulüpler (IEEE öğrenci kolu, robotik kulübü; varlıkları doğrulanmadı)
- LinkedIn ve Teknofest takım arama grupları
- 2209-A'nın "yürütücü + 3 ortak" yapısı, kişileri resmî olarak ekibe bağlamak için kullanılabilir

## Kaynaklar
- TÜBİTAK 2209-A: https://www.tubitak.gov.tr/tr/burslar/lisans/burs-programlari/icerik-2209-a-universite-ogrencileri-arastirma-projeleri-destekleme-programi
- 2209-A/B 2025 bütçe ve tarihleri (SDÜ): https://projekoord.sdu.edu.tr/tr/haber/tubitak-2209-a-ve-2209-b-universite-ogrencileri-arastirma-projeleri-2025-yili-cagrilari-basvuruya-acildi-54788h.html
- 2209-A/B 2025 (NEVÜ TTO): https://tto.nevsehir.edu.tr/tr/51505
- 2209 2025 çağrısı (Çukurova ARGES): https://arges.cu.edu.tr/haber-detay/82/tubi-tak-2209-a-ve-2209-b-universite-ogrencileri-arastirma-projeleri-destekleme-programlari-2025-yili-cagrilari-acildi
- 2209-A sonuç takvimi: https://www.hurriyet.com.tr/bilgi/galeri/tubitak-2209-a-basvuru-sonuclari-ne-zaman-aciklanacak-2026-43148101
- 2209-B: https://tubitak.gov.tr/en/scholarships/degree-associate-degree/destek-programlari/2209-b-industry-oriented-research-project-support-programme-undergraduate-students
- Teknofest İnsanlık Yararına Teknoloji: https://teknofest.org/tr/yarismalar/insanlik-yararina-teknoloji-yarismasi/
- Teknofest robotik yarışmalar: https://www.teknofest.org/tr/yarismalar/robotik-yarismalar/
- Teknofest olanaklar: https://www.teknofest.org/tr/competitions/opportunity/
- Teknofest 2026 takvimi (İTÜ): https://haberler.itu.edu.tr/haberdetay/2026/01/14/teknofest-2026-basvurulari-basladi
- XLeRobot: https://github.com/Vector-Wangel/XLeRobot ve https://hackaday.com/2025/11/03/dual-arm-mobile-bot-built-on-ikea-cart-costs-hundreds-not-thousands/
- SO-101: https://techcrunch.com/2025/04/28/hugging-face-releases-a-3d-printed-robotic-arm-starting-at-100 ve https://www.seeedstudio.com/SO-ARM101-Low-Cost-AI-Arm-Kit-p-6426.html
- LeKiwi: https://partabot.com/products/lekiwi-robot-arm
- Reachy Mini: https://huggingface.co/blog/reachy-mini ve https://www.automate.org/robotics/industry-insights/hugging-faces-open-source-desktop-pollen-robot-starts-at-299
- Reachy 2: https://pollen-robotics.com/reachy-2/ ve https://x.com/TheHumanoidHub/status/1833562030613401840
- InMoov: https://inmoov.fr/build-yours/ ve https://en.wikipedia.org/wiki/InMoov
- InMoov tekerlekli taban: http://myrobotlab.org/content/inmoov-temporary-wheels
- Poppy: https://github.com/poppy-project/poppy-torso ve https://www.generationrobots.com/en/281-robot-poppy-torso
- Pepper: https://www.bloomberg.com/news/articles/2021-06-29/softbank-mothballs-once-hyped-1-800-pepper-humanoid-robot ve https://www.nippon.com/en/news/reu20210628KCN2E419Y/
- TIAGo: https://humanoidindex.org/robots/tiago
- Mini Ada: https://akinoid.com/akinrobotics-robotlar/ada/prd-mini-ada-insansi-robot
- Ada-7: https://akinoid.com/akinrobotics-robotlar/prd-ada-7-sosyal-robot
- BTÜ Moria: https://btu.edu.tr/tr/haber/detay/6821/bt%C3%BCde-yapay-zek%C3%A2-destekli-i%CC%87nsans%C4%B1-robot-geli%C5%9Ftirildi
- KVKK 2026/921 ilke kararı: https://www.kvkk.gov.tr/Icerik/8762/mesai-takibi-amaciyla-biyometrik-veri-islenmesi-hakkinda-kisisel-verileri-koruma-kurulunun-29-04-2026-tarihli-ve-2026-921-sayili-ilke-kararina-iliskin-kamuoyu-duyurusu
- MCBÜ BAP: https://app-bap.cbu.edu.tr/
- Manisa Teknokent başvurular: https://teknokent.cbu.edu.tr/basvurular/
- MCBÜ Teknokariyer programı: https://ika.mcbu.edu.tr/Sayfa/teknokariyerprogrami
- İzmir 3D baskı fiyatları: https://armut.com/fiyatlari/izmir-3d-baski_12669_35
- 3D baskı fiyat rehberi 2026: https://bahadirsonmez.com.tr/3d-baski-fiyatlari-2026-3d-baski-fiyat-rehberi/
- İzmir lazer kesim: https://www.donmezreklam.com.tr/lazer-kesim-izmir ve https://armut.com/fiyatlari/izmir-pleksi-lazer-kesim_27139_35
- Bosch Türkiye: https://tr.linkedin.com/company/boschturkiye

**Güvenilirlik notu:** TÜBİTAK'ın resmî sayfaları bağlantı hatası (ECONNRESET) verdiği için açılamadı; rakamlar üniversite duyurularından çapraz kontrol edildi. 2026 çağrısının tutarı ve tarihleri, Teknofest 2027 takvimi ve MCBÜ BAP'ta öğrenci proje türü olup olmadığı **doğrulanmadı**. Malzeme, servis ve danışmanlık maliyetleri kendi tahminlerim, teklif alınarak kesinleştirilmeli.
