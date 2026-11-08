# T7 · Göğüs ekranı 12 V dalı ve jak ölçüsü

Kâğıt T7 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Göğüs ekranı (Waveshare 11,6" 1080p, kasalı) aküden ayrı bir dalla beslenir: mini 2 A sigorta → LM2577 + LM2596 kartı (12 V'a ayarlı)
→ ekranın 12 V jakı (`elektrik.md:49`). Bu kâğıt regülatörü **ekrana bağlamadan** 12 V'a ayarlatır, akünün bütün gerilim aralığında
çıkışın sabit kaldığını ve ekranın akımını ölçer, ekran jakının ölçüsünü ve kutup yönünü kaydeder.

## Neden önemli

Akü 12,8–14,4 V arasında gezer, şarjda 14,6 V'a çıkar (`elektrik.md:54`, `elektrik.md:249`); ekran 12 V ister. Regülatör kartı ayarsız gelir:
ayarlanmadan ekrana bağlanırsa ekran yanabilir (`elektrik.md:54`). Ekran jakının ölçüsü **doğrulanmadı** (`elektrik.md:19`).

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Kart LM2577 + LM2596, giriş 4–35 V, çıkış 12 V'a ayarlı | `elektrik.md:49`, `elektrik.md:54` | Tasarım; kart ayarsız gelir |
| Akü 12,8–14,4 V; şarj kesme 14,6 V | `elektrik.md:54`, `elektrik.md:249` | v4 / akü belgesi |
| Akü ölçüm aralığının alt ucu 10,0 V | `elektrik.md:201` | Tasarım (ADC bölücü hesabı) |
| Ekran ~12 V / 0,5 A; kutuda 12 V / 1 A adaptör; dokunmatik USB 5 V ~80 mA | `elektrik.md:19`, `07-gogus.md:19`, `07-gogus.md:39` | Üretici wiki'si |
| Dal sigortası mini 2 A | `elektrik.md:338`, `elektrik.md:60` | Tasarım |
| Ekran fişi: kutudaki adaptör kablosu kesilip kullanılabilir | `elektrik.md:54` | v4 |
| Ekran jakı ölçüsü | `elektrik.md:19`, `elektrik.md:480` | **Doğrulanmadı**; bu kâğıt ölçer |
| Çıkış toleransı | yok | **Kaynakta yok**; bu kâğıt ±%5 varsayar |

## Gereken alet

- Ayarlı laboratuvar güç kaynağı (0–30 V, en az 3 A, akım sınırlamalı)
- Multimetre ×2 (biri çıkış gerilimi, biri giriş akımı)
- Yük direnci **24 Ω, en az 10 W** (12 V'ta 0,5 A = 6 W; ekranın yerine, `07-gogus.md:19` akımından)
- Kumpas, küçük düz tornavida (kartın ayar trimpotu için), mini bıçak sigorta 2 A + yuvası
- Ekran, kutudaki 12 V adaptörü, HDMI görüntü kaynağı (Pi ya da bilgisayar)

## Güvenlik

- **Ekranı regülatör ayarlanmadan bağlama.** Her yeni kartta ve her trimpot dokunuşundan sonra önce yük direnciyle ölç (`elektrik.md:54`).
- Kutup yönü ters bağlanırsa ekran yanar: jakın kutbunu adaptörde ölçmeden kablo lehimleme.
- Laboratuvar kaynağında akım sınırı **2,0 A** (dal sigortasıyla aynı). Akü kullanılırsa dal sigortası takılı.
- 24 Ω direnç 6 W'ta ısınır: masaya değmesin, dokunma.
- Prizdeki adaptörle ölçerken yalnız düşük gerilim (fiş) tarafına dokun.
- **Multimetreyle akım:** [00-genel.md](00-genel.md) "Multimetreyle akım ölçümü" kuralı. Kısaca: kırmızı uç 10 A soketine, yalnız seri,
  enerji kapalıyken bağla; iş bitince kırmızı uç V soketine geri (sonraki adım gerilim ölçümü). Akımlar burada 2 A'in altında.
- Kartın **girişinde ters kutup koruması varsayılmaz**: enerji vermeden girişin kutbunu kontrol et (adım 5).
- **Saat, yüzük, bileklik çıkar.**

## Yöntem

**A. Jak ve kutup (ekran ve adaptör ile, regülatör yok)**

1. Adaptörün fişinin dış çapını ve iç deliğin çapını kumpasla ölç; fişin metal boyunu ölç.
2. Ekranın jakındaki iç pimin çapını ölç (kumpasın iç çene ucu ya da matkap ucu sapıyla).
3. Adaptörü prize tak. Multimetre DC V: kırmızı uç fişin **içine**, siyah uç **dışına**. Okuma artı ise "merkez artı". Adaptörün boştaki gerilimini yaz.
4. Fişi ekrana tak, ekranın jakta oynamadan oturduğunu ve çalıştığını gör.

**B. Regülatör ayarı (ekran bağlı değil)**

5. **Kaynak kapalıyken** kartın giriş uçlarını bul (kartta IN+ / IN− ya da VIN / GND yazısı); kaynağın kırmızı (+) kablosu IN+'ya, siyahı
   IN−'ye gidiyor mu, gözle ve yazıyla kontrol et. Sonra kaynağı aç, **12,8 V** ver (akım sınırı 2,0 A). Çıkışa yalnız multimetre (DC V) bağlı.
6. Trimpotu çevirerek çıkışı **12,0 V**'a ayarla (`elektrik.md:54`). Trimpot konumunu bir boya noktasıyla işaretle.
7. Enerjiyi kes, çıkışa 24 Ω yük direncini bağla. Giriş akımı için ikinci multimetreyi kaynak ile kart girişi arasına **seri** koy (10 A soketi)
   ya da kaynağın kendi akım göstergesini kullan. Enerji ver. Giriş gerilimini sırayla **10,0 / 12,8 / 14,4 / 14,6 V** yap; her birinde çıkış
   gerilimini ve giriş akımını yaz.
8. 12,8 V girişte 10 dk yükte bekle; çıkış gerilimini yeniden oku.

**C. Ekranla**

9. Enerjiyi kes, direnci çıkar, A'da bulunan kutba göre fişi kartın çıkışına bağla, ekranı tak. HDMI görüntü ver, parlaklığı %100 yap.
10. Ekran akımı için multimetreyi, enerji kapalıyken, kart çıkışı ile ekran fişinin + teli arasına **seri** koy (10 A soketi); gerilimi
    multimetreden sonra, ekran tarafında oku. Giriş 10,0 / 12,8 / 14,6 V'ta: çıkış gerilimi, ekran akımı, giriş akımı (kaynak göstergesi).
    Ekran kararıyor ya da yeniden başlıyor mu? Bitince seri multimetreyi enerji kapalıyken çıkar, kırmızı ucu V soketine geri tak.
11. Ekranı açıp kapatırken (fişi takıp çıkararak değil, girişten enerjiyi açıp keserek) çıkışın 12 V'u aşıp aşmadığını gözle (multimetrede en yüksek, varsa MAX tuşu).

## Kayıt tablosu

**A. Jak**

| Ölçüm | Değer |
|---|---|
| Fiş dış çapı (mm) | |
| Fiş iç çapı (mm) | |
| Fiş metal boyu (mm) | |
| Ekran jakı iç pim çapı (mm) | |
| Kutup | ☐ merkez artı ☐ merkez eksi |
| Adaptör boşta gerilimi (V) | |
| Fiş jakta oynamadan oturuyor | ☐ evet ☐ hayır |

**B. Yük direnciyle (24 Ω)**

| Giriş (V) | Çıkış (V) | Giriş akımı (A) | Not |
|---|---|---|---|
| 10,0 | | | |
| 12,8 | | | |
| 14,4 | | | |
| 14,6 | | | |
| 12,8, 10 dk sonra | | | |

**C. Ekranla (parlaklık %100)**

| Giriş (V) | Çıkış (V) | Ekran akımı (A) | Giriş akımı (A) | Ekran normal mi |
|---|---|---|---|---|
| 10,0 | | | | ☐ |
| 12,8 | | | | ☐ |
| 14,6 | | | | ☐ |
| Açılışta en yüksek çıkış (V) | | – | – | – |

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| Çıkış gerilimi, B ve C'de bütün girişlerde | **11,4–12,6 V** | **Varsayım** (12 V ±%5); üretici toleransı kaynakta yok |
| Ekran akımı (12 V tarafı) | **≤ 1,0 A** | Kutudaki adaptör 12 V / 1 A (`07-gogus.md:19`) |
| Giriş akımı, 10,0 V'ta dahil | **< 2,0 A** | Dal sigortası mini 2 A (`elektrik.md:338`) |
| Kutup | Kartın çıkış kablosu ölçülen kutupla aynı | A adımı |
| Jak | Fiş jakta oynamadan oturuyor, ölçüler yazılı | `elektrik.md:19` (doğrulanmadı) |

Ekran akımı 0,5 A'den farklı çıkarsa kalır sayılmaz; değer `elektrik.md:19` ve akım bütçesine (`elektrik.md:316`) işlenir.

## Sınır aşılırsa

- Çıkış tutmuyorsa (özellikle 10,0 V'ta düşüyor ya da 14,6 V'ta yükseliyorsa): kart bu iş için yetersiz; tasarım ajanına ve **Ahmet Yorulmaz**'a.
  Ekran bağlanmaz.
- Jak ölçüsü ve kutup `elektrik.md:19` ve açık iş 16'ya (`elektrik.md:480`) yazılır; fiş ya da kablo seçimi tasarım ajanında.
- Not: dalın girişi ana anahtardan sonra mı, anahtarlı baradan mı alınacak kararı bu testin konusu değil (`karar-kuyrugu.md` **K11**).

## Sonuç

☐ GEÇER  ☐ KALIR    Çıkış aralığı: ______ – ______ V   Ekran akımı: ______ A   Jak: ______ / ______ mm, ☐ merkez +  ☐ merkez −

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
