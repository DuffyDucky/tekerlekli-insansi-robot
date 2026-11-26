# Sanal ray sonucu: LiDAR'sız gezinme (kamera + etiket + enkoder + ön sonar)

## Tamamlama turu (2026-11-26): eksik ve yanlış yerdeki etiket robotun gördüğü etiketlerden

**Hüküm (güncel; aşağıdaki dayanıklılık turunun eksik etiket ve yanlış yer sonuçlarının yerine geçer).** Eksik tek bir
etiket A'dan B'yi bozmuyor: robotun rotada ölçtüğü etiketlerden biri kaldırılınca **24/24**, en çok ölçüleni
kaldırılınca da **24/24** başarılı; temas yok. Yanlış asılmış etiket ise ilk turun dediğinden **daha ağır**. 1 m kaymış
tek etiketle sonuç **15/24**; ilk turdaki 9/12 iyimserdi, etkili koşularda 3/6 idi. **2 koşuda robot duvara dayanıp süre
doldurdu** (toplam 206 s temas). Kırılma noktası 0,25 ile 0,5 m arasında: 0,25 m'de 24/24, 0,5 m'de 20/24.

- **İncelemenin bulgusu doğru.** İlk turda eksik / yanlış yer etiketi `Cekilis.sira` ile bütün plandan seçiliyordu.
  12 koşunun 6'sında seçilen etiket robotun rotada hiç ölçmediği bir etiketti. Bu 6 koşu temiz koşuyla birebir aynı:
  varış, kabul / ret sayısı, süre ve yanal sapma. Ham kayıtlardan yeniden sayım (`dayaniklilik_rota.md`): eksik etiket
  etkili 6/6, yanlış yer etkili 3/6. Hafif yırtıkta 3 koşu etkisiz, kalan 9/9. Etkisiz koşular aynı 6 koşu (koridor_2 t3,
  koridor_4 t1/t2, koridor_5 t2, koridor_6 t1/t3).
- **Kök neden düzeltmesi.** `kusur.gercek_plan(..., aday=...)`: eksik / yanlış yer etiketi artık yalnız aday
  etiketlerden seçiliyor. Aday, aynı koridor, hedef ve tohumun kusursuz koşusunda süzgecin en az bir ölçümünü **kabul
  ettiği** etiket. İki seçim var: "rota" tohumdan çekilen sırayla seçiyor, "kritik" en çok kabul edilen etiketi alıyor.
  Aday listesi deney tasarımına ait, hakem tarafında kalıyor; Beyin hep nominal planı kullanıyor ve listeyi görmüyor.
  Sayaç, kusursuz koşuda Beyin'in algılama ve süzgeç çağrılarını yalnız sayıyor, davranışı değiştirmiyor: tohum 1-3 ilk
  turla **12/12 birebir aynı**. Yeni koşuların hiçbiri temiz koşuyla aynı değil (etkisiz 0/144). `aday=None` ilk turun
  seçimidir; varsayılan bu.
- **Örneklem.** 4 sınama koridoru, orta hedef, kafa sabit, dönüş fazlası %25, tohum 1-6: koşul başına 24 koşu. Tohum
  1-3 ilk turla aynı başlangıç sapması ve kusur çekilişi; 4-6 yeni. Bu koşular yalnız hüküm için; hiçbir ayar
  değişmedi. Adaylar: koridor_2'de rotada yalnız 2 etiket ölçülüyor (3'ten), koridor_4'te 5 (8'den), koridor_5 ve
  koridor_6'da 3 (6'dan). Seçilen etiket temiz koşudaki kabul edilen ölçümlerin ortalama %40'ını taşıyordu ("kritik"te
  %50).
- **Yanlış yerin mekanizması.** Kapı kaymış etiketi önce reddediyor. Arka arkaya 6 ret olunca yeniden başlatma kancası
  süzgeci yakındaki etiketten yeniden kuruyor ve bu etiket kaymış etiketin kendisi olabiliyor. Örnek koridor_4 tohum 2:
  34 s'de "yeniden başlatıldı: etiket 152". Ardından doğru etiketler reddediliyor (745 ve 1090 ret), robot duvara dayanıyor
  ve ön sonar eğik duvarı görmüyor. Kalan 7 başarısızlıkta Beyin "bitti" diyor ama hedefin 0,30-1,04 m uzağında. 0,5 m'de
  bir koşuda (koridor_5 tohum 4) yeniden başlatma 6,4 m konum hatası üretti, robot hedefin 1,65 m uzağında durdu.
- **Eksik etiket bedelsiz değil.** koridor_6'da başlangıçtaki etiket (251) kaldırılınca yanal sapma 0,25 m'ye çıktı
  (temizde en çok 0,12 m). Başarı ve temas değişmedi.
- **Altyapı arızası (algoritma sonucu değil).** 3 süreç aynı anda başlarken biri, ötekinin yarım yazdığı kameralı model
  kopyasını okudu ve 2 koşu istisnayla bitti ("teker_on_sol gövdesi bulunamadı"). Düzeltme: `etiket.kamerali_model_xml`
  dosyayı içerikten adlandırıyor ve geçici dosya + `os.replace` ile yazıyor. İki koşu yeniden koşuldu ve temiz koşuyla
  birebir aynı çıktı. İstisna kayıtları `ham/dayaniklilik_rota_log/istisna/` altında.

| koşul | seçim | tohum 1-3 | tohum 1-6 | varış ort / en (m), 1-6 | yanal ham en (m) | yanal ilk 2 m sonrası ort / en (m) | konum hatası en (m) | temas olay / süre (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz | - | 12/12 | 24/24 | 0,118 / 0,136 | 0,121 | 0,021 / 0,075 | 0,133 | 0 / 0 |
| 1 etiket eksik | rotada ölçülen, rastgele | 12/12 | 24/24 | 0,121 / 0,207 | 0,249 | 0,029 / 0,249 | 0,277 | 0 / 0 |
| 1 etiket eksik | en çok ölçülen | 12/12 | 24/24 | 0,124 / 0,204 | 0,249 | 0,031 / 0,249 | 0,277 | 0 / 0 |
| 1 etiket 0,25 m kaymış | rotada ölçülen, rastgele | 12/12 | 24/24 | 0,095 / 0,229 | 0,249 | 0,035 / 0,249 | 0,304 | 0 / 0 |
| 1 etiket 0,5 m kaymış | rotada ölçülen, rastgele | 9/12 | 20/24 | 0,235 / 1,652 | 0,622 | 0,079 / 0,622 | 6,405 | 0 / 0 |
| 1 etiket 1 m kaymış | rotada ölçülen, rastgele | 5/12 | 15/24 | 0,756 / 5,762 | 1,225 | 0,142 / 1,225 | 1,200 | **2 / 206,0** |
| 1 etiket 1 m kaymış | en çok ölçülen | 8/12 | 15/24 | 0,332 / 1,040 | 0,957 | 0,051 / 0,957 | 1,142 | 0 / 0 |
| (ilk tur) 1 etiket eksik | bütün plan | 12/12 (etkili 6/6) | - | | | | | 0 / 0 |
| (ilk tur) 1 etiket 1 m kaymış | bütün plan | 9/12 (etkili 3/6) | - | | | | | 0 / 0 |

Satırlar `dayaniklilik_rota_ab.csv`, tablolar ve başarısız koşuların listesi `dayaniklilik_rota.md`; ham kayıtlar
`ham/dayaniklilik_rota/` (git dışı). 0,25 m düzeyi, 0,5 m de kırdığı görüldükten sonra eklendi; bu düzeyler arasında ayar
yok, yalnız ölçüm.

**Gerçek koridor için (güncellendi).** Etiket–harita denetimi kurulumda **zorunlu**. Yalnız kimliği karışmış etiket değil,
0,5 m yanlış yere asılmış tek bir etiket de 24 koşunun 4'ünü bozuyor; 1 m'de 24'ün 9'unu bozuyor ve robot duvara
dayanabiliyor. ±25 cm içindeki hata zararsız. Eksik ya da düşmüş tek etiket A'dan B'yi bozmuyor; yine de yenilensin.
Algoritma için öneri (uygulanmadı, sınanmadı): yeniden başlatma kancası tek bir etiketi, başka bir etiketle ya da sonarla
çapraz denetlemeden kabul etmesin.

**Kapsam.** Yalnız A'dan B'ye, orta hedef, kafa sabit. Rastgele bırakılmada ve tarayan kafada eksik / yanlış yer
koşulmadı. Birleşik "ağır" kurulumdaki eksik ve yanlış yer etiketi hâlâ bütün plandan seçiliyor; o düzeyde sonucu yırtık
etiketler belirlediği için yeniden koşulmadı. Hafif yırtıkta (etiketlerin 1/3'ü) 3 etkisiz koşu yeniden koşulmadı;
etkili 9 koşunun 9'u başarılı.

## Dayanıklılık turu (2026-11-26): kusurlu dünyada ne kadar dayanıyor?

*Güncellendi: "1 eksik etiket 12/12" ve "yanlış yer 9/12" iyimserdi; 12 koşunun 6'sında etiket robotun görmediği
yerdeydi. Güncel sayılar yukarıdaki "Tamamlama turu"nda: eksik 24/24, 1 m yanlış yer 15/24 ve 2 temas.*

**Hüküm.** Bilinen başlangıçtan A'dan B'ye sürüş kurulum hatalarına şaşırtıcı derecede dayanıklı; zayıf noktalar
**etiketin bütünlüğü**, **yanlış asılmış etiket** ve **rastgele bırakılmada arama / konumlanma**. Etiket planı (5 m) ve
süzgeç ayarı bu turda değişmedi; kusur düzeyleri yalnız ölçüldü.

- **A'dan B'ye, tek etken, en ağır düzey (12 koşu: 4 sınama koridoru x orta hedef x 3 tohum):** harita konum hatası
  ±5 cm (ek olarak ±20 cm), açı ±5°, odak %2, montaj eğimi ±2°, algılama gecikmesi 200 ms, %50 kare düşmesi, zamanın %50'sinde örtülme,
  %50'sinde sert parlama, 33 ms pozlama + titreşim, 1 eksik etiket: **hepsinde 12/12**. Varış hatası temizde 0,118 m;
  en çok bulanıklık bozdu (0,182 m). Kırılma noktası bu etkenlerde ölçülen aralığın **dışında** (aşağıda).
- **Kıran etkenler:** etiketlerin hepsinde köşenin %25'i yırtık -> algılama sıfır, **2/12** (robot yalnız odometriyle
  gidiyor, 3 koşuda 80 s'ye yakın duvara dayalı). Köşenin %15'i yırtık, etiketlerin 1/3'ünde -> 12/12 (varış 0,145 m). Kırılma noktası bu ikisinin
  arasında: siyah çerçevenin köşesi gidince etiket okunmuyor. Bir etiket 1 m yanlış yere asılınca **9/12**: kapı bu etiketi reddetmiyor, robotu 0,96 m kaydırıyor.
  Not (denetim): tek etiketlik etkenlerde seçilen etiket 12 koşunun 6'sında robotun gördüğü kısımda değildi; bu 6
  koşu temiz koşuyla birebir aynı (varış, ölçüm sayısı, süre). Etkenin gerçekten etki ettiği koşularda eksik etiket
  6/6, yanlış yer **3/6**; hafif yırtıkta 3 koşu etkisiz, kalan 9/9.
- **Birleşik kurulum, A'dan B'ye:** hafif 12/12 (0,116 m), orta 11/12 (0,176 m; tek kayıp varışta 0,32 m), ağır 2/12
  (yırtık etiketler yüzünden; ağır düzey yırtık etkisinin altında kalıyor, ayrı bir bileşen sonucu değil).
- **Rastgele bırakılma çok daha kırılgan:** hafif 12/12, **orta 5/12**, ağır 0/12 (kafa sabit, ilk sürüm başlatma;
  kusursuzda ilk tur 11/12). Ağırda 18 temas olayı, toplam 3140 s duvara dayalı.
  Orta kurulumda tek etiketten başlatma iki koşuda 0,77 m ve 1,38 m yanlış başladı. 4 koşu 273-290 s duvara dayalı kaldı:
  üçü "süre doldu", biri "etiket bulunamadı" ile bitti (güncellendi: önceki metin dördüne de "süre doldu" diyordu).
  Bunlara 93 s'lik bir temas daha eklenince toplam 1219 s.
- **Doğrulamalı başlatma (yeni, isteğe bağlı):** ayrı tohumlarda kusursuz dünyada **16/16** (ilk sürüm 15/16; ilk sürümün
  başarısızlığı yine 275 s duvara dayanma). Bedeli konumlanmada ortalama +1,0 s, toplam sürede +1,9 s (eşleşmiş başarılı
  koşular). Orta kusurlu kurulumda **6/12** (ilk sürüm 5/12): başlatma hatası ort 0,32 -> 0,07 m'ye indi (yalnız
  konumlanan koşular: ilk sürümde 11, doğrulamalıda 7), ama 5 koşuda
  doğrulama hiç geçmedi ("etiket bulunamadı"), konumlanma 6 -> 33 s. **Varsayılan değişmedi** (`baslatma="tek"`): orta
  kurulumda konumlanma süresi ve "bulunamadı" sayısı kötüleşti.
  Temas yorumu (eklendi): doğrulamalıda temas olayı 5'ten 22'ye çıktı, toplam süre 1219 s'den 805 s'ye indi. Takılma
  denetimi enkoderden çalışıyor, yani duvara **değdikten sonra** sezebiliyor. Robot daha çok değiyor ama daha kısa
  dayanıyor. Başarılı 6 koşunun 3'ünde de temas var (1,9 s, 2,0 s ve 129 s). "Temas sıfır" ölçütüne göre doğrulamalı
  başlatma ilk sürümden kötü. Varsayılanın değişmemesinin bir nedeni de bu.
  Seçim etkisi: 0,32 -> 0,07 m karşılaştırması iki farklı alt kümeden geliyor (ilk sürümde konumlanan 11 koşu,
  doğrulamalıda 7). Konumlanamayan 5 koşu ortalamaya girmiyor.
- **İlk turun açıklaması düzeltildi:** tek başarısızlığın "yanlış tek etiket başlatması" olduğu düşünülmüştü. Bu turda
  aynı türden iki başarısızlıkta (geliştirme koridor_1 bırakma 2, sınama koridor_4 bırakma 10) başlatma hatası 0,008 m
  ve 0,18 m idi: konum doğru başladı, robot ilk yerinde dönüşten sonra (dönüş ölçeği henüz öğrenilmemişken) eğik
  sürdü, etiket görmedi, eğik duvara dayandı; ön sonar eğik yüzeyden yankı almadığı için durmadı. Asıl kusur
  **takılmanın sezilmemesi**. Kusurlu kurulumda ise tek etiket başlatması gerçekten yanlış başlıyor (0,77 / 1,38 m).
  Denetim: ilk turun kendi başarısız koşusu (sınama koridor_4 bırakma 1, kafa sabit) bu turun koşucusuyla birebir
  yeniden üretildi (hedefe 12,27 m, en büyük konum hatası 1,70 m, 262 s temas) ve başlatma hatası ölçüldü: 0,22 m,
  yön 6,0°. Başlangıç kabaca doğru; 1,7 m'lik hata sonradan büyüdü.

### Gerçek okul koridoru için kurulum özeni (bu ölçümlerden)

| Konu | Gereken | Dayanak |
| --- | --- | --- |
| Etiket yeri | ±5 cm hedeflenmeli (şerit metreyle köşe / kapı kasasından ölçmek yeter); A'dan B'ye ±20 cm'de bile 12/12, ama yanal sapma 0,07'den 0,19 m'ye çıkıyor ve rastgele bırakılmada ±20 cm ölçülmedi | konum5, konum20 |
| Etiket açısı | düz duvara düz yapıştırmak yeter (±5° 12/12) | |
| Etiketin kimliği / yeri haritayla aynı | **zorunlu**: 1 m kaymış tek etiket 3/12 koşuyu bozdu (güncellendi: robotun gördüğü etiketten seçilince 9/24 bozuldu, 2 koşuda temas oldu; 0,5 m'de 4/24 bozuldu, 0,25 m'de hiçbiri); kurulumdan sonra robotla bir tur "etiket - harita" denetimi | yanlis1, yanlis1_rota, yanlis05_rota |
| Etiket bütünlüğü | **zorunlu**: siyah çerçevenin köşesi gitmiş etiket hiç okunmuyor; sert levha / laminasyon, yıpranınca yenileme | yirtik |
| Kamera kalibrasyonu | belge değeriyle %2 odak hatasına dek sorun yok; yine de bir kez satranç tahtası kalibrasyonu ucuz ve **mercek bozulmasını** (burada modellenmedi) da giderir; Wide mercekte zorunlu | odak2 |
| Kamera montajı | ±2° eğim sorun değil | egim2 |
| Pi algılama süresi | 200 ms'ye dek A'dan B'ye sorun değil | gecikme200 |
| İnsan / parlama | zamanın yarısında örtülme ya da sert parlama A'dan B'yi bozmadı (etiketler 5 m arayla, biri kaybolunca diğeri) | ortulme50, parlama_agir |

**Çalışmadığı koşullar:** etiketler yıpranmış / köşesi kopmuş; bir etiket haritada yazdığından ≈ 1 m başka yerde
(güncellendi: 0,5 m'de de, tamamlama turu);
robot bilinmeyen yerden başlatılıyor ve kurulum "orta" kusurlu (gecikme 100 ms + %10 kare düşmesi + örtülme / parlama +
hafif harita hatası): bu durumda rastgele bırakılma yarı yarıya başarısız. Rastgele bırakılmada tek başına güvenmeden
önce insanın robotu bilinen bir noktaya koyması (A'dan B'ye kipi) gerçekçi yol.

### Ana tablo (A'dan B'ye, sınama koridorları koridor_2, 4, 5, 6; kafa sabit; dönüş fazlası %25; tohum 1, 2, 3)

Yanal sapma: "ham en" eski ölçüt (başlangıç sapmasına doyuyor: temizde 0,121 m'nin tamamı koridor başlangıcındaki
sapma); "ilk 2 m'den sonra" = rayda 2 m yol alındıktan sonraki ort / en (başlangıç sapmasından arındırılmış).

| koşul | etken | düzey | başarı | varış hatası ort / en (m) | yanal sapma ham en (m) | yanal, ilk 2 m'den sonra ort / en (m) | temas olayı | temas süresi (s) | konum hatası en (m) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz | temiz | - | 12/12 | 0,118 / 0,136 | 0,121 | 0,021 / 0,073 | 0 | 0,0 | 0,122 |
| konum5 | harita konum | ±5 cm | 12/12 | 0,115 / 0,142 | 0,126 | 0,021 / 0,093 | 0 | 0,0 | 0,128 |
| konum20 | harita konum | ±20 cm | 12/12 | 0,114 / 0,170 | 0,194 | 0,034 / 0,194 | 0 | 0,0 | 0,257 |
| aci5 | harita açı | ±5° | 12/12 | 0,119 / 0,141 | 0,121 | 0,022 / 0,072 | 0 | 0,0 | 0,122 |
| odak2 | odak | %2 | 12/12 | 0,129 / 0,177 | 0,121 | 0,022 / 0,115 | 0 | 0,0 | 0,165 |
| egim2 | montaj eğimi | ±2° | 12/12 | 0,121 / 0,146 | 0,106 | 0,021 / 0,074 | 0 | 0,0 | 0,119 |
| gecikme200 | gecikme | 200 ms | 12/12 | 0,076 / 0,107 | 0,130 | 0,021 / 0,130 | 0 | 0,0 | 0,142 |
| dusme50 | kare düşmesi | %50 | 12/12 | 0,136 / 0,159 | 0,124 | 0,021 / 0,061 | 0 | 0,0 | 0,125 |
| ortulme50 | örtülme | %50 zaman | 12/12 | 0,135 / 0,196 | 0,121 | 0,021 / 0,092 | 0 | 0,0 | 0,185 |
| parlama_agir | parlama | %50 zaman, genlik 230 | 12/12 | 0,131 / 0,185 | 0,121 | 0,024 / 0,100 | 0 | 0,0 | 0,154 |
| bulanik_agir | bulanıklık | 33 ms, titreşim 0,6 rad/s | 12/12 | 0,182 / 0,228 | 0,186 | 0,031 / 0,186 | 0 | 0,0 | 0,219 |
| yirtik_hafif | yırtık | etiketlerin 1/3'ü, köşe %15 | 12/12 | 0,145 / 0,258 | 0,121 | 0,019 / 0,070 | 0 | 0,0 | 0,211 |
| yirtik_agir | yırtık | hepsi, köşe %25 | 2/12 | 0,804 / 1,983 | 1,076 | 0,324 / 1,076 | 6 | 242,7 | 1,904 |
| kayip1 | eksik etiket | 1 etiket yok | 12/12 | 0,130 / 0,207 | 0,121 | 0,019 / 0,073 | 0 | 0,0 | 0,182 |
| yanlis1 | yanlış yer | 1 etiket 1 m kaymış | 9/12 | 0,291 / 0,957 | 0,957 | 0,056 / 0,957 | 0 | 0,0 | 1,142 |
| hafif | birleşik | hafif | 12/12 | 0,116 / 0,140 | 0,105 | 0,020 / 0,087 | 0 | 0,0 | 0,119 |
| orta | birleşik | orta | 11/12 | 0,176 / 0,317 | 0,185 | 0,028 / 0,185 | 0 | 0,0 | 0,272 |
| agir | birleşik | ağır | 2/12 | 0,809 / 1,983 | 1,076 | 0,328 / 1,076 | 6 | 242,7 | 1,904 |

*kayip1 ve yanlis1 satırları (güncellendi): 12 koşunun 6'sı etkisiz (etiket robotun görmediği yerde). Güncel sayılar
"Tamamlama turu" tablosunda.*

### Rastgele bırakılma (sınama koridorları, bırakma = tohum - 1: ilk turun bırakma noktaları; kafa sabit)

| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en (s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agir, tek, kafa sabit | 0/12 | - | - / - | 0 | - / - | 300,4 | 0 | 0 | 0 | 18 | 3140,2 |
| hafif, tek, kafa sabit | 12/12 | 0,100 | 0,049 / 0,202 | 0 | 2,9 / 13,1 | 41,9 | 0 | 0 | 0 | 0 | 0,0 |
| orta, dogrulamali, kafa sabit | 6/12 | 0,176 | 0,072 / 0,154 | 0 | 33,3 / 110,3 | 218,1 | 27 | 5 | 15 | 22 | 804,5 |
| orta, tek, kafa sabit | 5/12 | 0,144 | 0,320 / 1,381 | 2 | 6,0 / 19,4 | 134,5 | 0 | 0 | 0 | 5 | 1219,0 |

### Doğrulamalı başlatma: geliştirme ve ayrı sınama

Geliştirme (koridor_1, koridor_3, bırakma 0-3):

| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en (s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz, dogrulamali, kafa sabit | 8/8 | 0,115 | 0,023 / 0,083 | 0 | 4,0 / 8,4 | 48,5 | 0 | 1 | 0 | 4 | 1,6 |
| temiz, tek, kafa sabit | 7/8 | 0,106 | 0,035 / 0,140 | 0 | 2,7 / 7,4 | 73,0 | 0 | 0 | 0 | 1 | 276,4 |

Sınama, ayrı tohumlar (sınama koridorları, bırakma 10-13), kusursuz dünya:

| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en (s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz, dogrulamali, kafa sabit | 16/16 | 0,102 | 0,019 / 0,201 | 0 | 5,5 / 14,2 | 35,3 | 0 | 0 | 0 | 0 | 0,0 |
| temiz, tek, kafa sabit | 15/16 | 0,092 | 0,027 / 0,179 | 0 | 4,4 / 13,1 | 48,6 | 0 | 0 | 0 | 2 | 274,9 |

Doğrulamalı başlatma (`beyin.py`, `baslatma="dogrulamali"`; yalnız kayıp robot): (1) 3,5 m içindeki ilk aday etikette
gövde durur, 1 s boyunca adaylar toplanır (70°'den eğik bakılan ölçüm aday olmaz); adayların en az 3'ü ve %70'i
ortanca pozun 0,15 m / 4° içinde olmalı; (2) ön sonar bir mesafe ölçüyorsa haritadan (bina planı ön bilgisi) beklenen
mesafeyle 0,35 m içinde olmalı, yoksa ret ve 1,5 s sonra yeniden deneme; (3) konumlandıktan sonraki ilk yerinde
dönüşten sonra gövde durur, kafa 0 / ±40 / ±75°'ye bakar, bir etiket kabul edilene dek (en çok 6 s); (4) takılma
denetimi: 2,5 s ileri komuta karşın enkoder komutun %25'inden az ilerlerse 2 s geri, konum bırakılır, arama yeniden;
(5) 6 ardışık ret ya da 30 s hiç kabul yoksa konum bırakılır. Bileşenlerin ayrı ayrı katkısı ölçülmedi (ablasyon yok).

Tasarım geliştirme kümesinde iki kez değişti (kayıtlar `sonuc/ham/dayaniklilik_tasarim1/`, `..._tasarim2/`):
tasarım 1 (gelişme sınırı 55°, takılma denetimi yok) 5 koşunun 4'ünde başarısız (aday çıkmadı, arama eğik duvara
dayandı); tasarım 2 (70°, takılma denetimi, kafa taraması) 3/4, çünkü "sonar yankısız ama harita duvar bekliyor" da ret
sayılıyordu ve simüle sonar yakın duvarda bile çoğu kez yankısız. Tasarım 3 (yankısız sonar bilgi vermez) sınamadan
önce donduruldu; tasarım 2 ile sınamada hiçbir doğrulamalı koşu tamamlanmadı (zincir durduruldu, yarım kalan bir ilk
sürüm koşusu baştan koşuldu).

### Kusur modeli ve iyimser varsayımlar

Kusurlar `kusur.py` başında; kısaca: harita konumu duvar boyunca ve dikeyde U(-e, e) (duvara dik hata yok); açı yüz
normalinde U(-a, a); odak hatası Beyin'in K'sinde ±o (işaret tohumdan), asal nokta doğru, **mercek bozulması yok**;
montaj eğimi pitch; gecikme sabit (titreşimsiz), Beyin zaman damgası telafisi yapmıyor; örtülme / parlama etiket başına
ortalama 2 s'lik bölümler, örtü gri dikdörtgen (etiket kutusunun %40'ı bir yandan), parlama Gauss leke (yarıçap kutu
kenarının 0,25'i); bulanıklık pozlama + kafa titreşimi (açısal hız std); yırtık = baskının bir köşesi (beyaz pay +
siyah karenin %15 / %25'i) duvar rengi; eksik etiket ve yanlış yer etiket seçimi tohumdan. Aynı tohumda düzeyler aynı
yönde ölçeklenir. İyimser kalanlar: gecikme sabit; kare düşmesi bağımsız; örtü düz gri (insan dokusu yok); parlama tek
leke; etiketler aynı tip; ışık düzgün; yuvarlanan deklanşör, mercek bozulması, gövde eğimi yok; sonar ideal (ama eğik
yüzeyden yankısız). Kusur sıfırken koşu ilk turla birebir aynı (denetlendi: koridor_2 kapi_2 tohum 1 -> 0,0852 m /
0,0815 m, ilk turla aynı).

### Kapsam ve süre bütçesi için küçültülenler

- Tek etkenlerde yalnız **en ağır** düzey koşuldu (12 koşu); hepsi 12/12 çıktığı için ara düzeyler (±1 / 3 cm, ±1 / 2°,
  %0,5 / 1, ±1°, 50 / 100 ms, %20 düşme / örtülme, hafif parlama / bulanıklık) **koşulmadı**: tekdüzelik varsayımıyla
  onlar da geçer sayıldı (VARSAYIM). Ölçülen aralığın dışına yalnız ±20 cm konum ve hafif yırtık koşuldu; ±10 cm, ±10°,
  %5 odak, ±5° eğim kilitlenip atlandı.
- Tek etkenler ve birleşik A'dan B'ye yalnız orta hedefte (3 hedeften biri), kafa sabit, dönüş fazlası %25.
- Rastgele bırakılma tek etkenlerde hiç koşulmadı (planlanan 4 etken atlandı); birleşikte yalnız kafa sabit (tarayan
  kafa atlandı).
- Doğrulamalı başlatma yalnız kafa sabit; geliştirme 2 koridor x 4 bırakma, sınama 4 koridor x 4 bırakma (temiz) ve
  birleşik orta 12 koşu. Tek tohum ailesi; farklar 1 koşu düzeyinde, istatistiksel güç düşük.
- Ölçüm ayrımı: kusur ölçümleri sınama koridorlarında, tohum 1-3 (tohum 1 ilk turun aynı başlangıç sapması); hiçbir ayar
  bunlara göre seçilmedi. Doğrulamalı başlatmanın eşikleri geliştirme kümesinde (koridor_1, koridor_3, bırakma 0-3,
  +500 tohumu), hüküm sınamada (bırakma 10-13; ilk turda ve kusur ölçümlerinde kullanılmamış noktalar) ve birleşik orta
  kurulumda (bırakma 0-2).

Satırlar `dayaniklilik_ab.csv`, `dayaniklilik_kayip.csv`; bütün tablolar `dayaniklilik.md`. Ham kayıtlar
`ham/dayaniklilik/` (git dışı).

---

*Aşağısı ilk tur (2026-11-25); sayılar değişmedi. Güncellendi: tek rastgele bırakılma başarısızlığının nedeni için
yukarıdaki "İlk turun açıklaması düzeltildi" maddesine bakın.*

## Hüküm

**Simülasyonda evet, koşullu.** Kafadaki tek Camera Module 3 (standart mercek, 66°), göz hizasında (1,55 m) 15 cm
AprilTag 36h11 ve enkoder + ön sonarla robot, LiDAR verisi hiç kullanılmadan, sınama koridorlarında A'dan B'ye **48
koşunun 46'sında** gitti. Seçilen planda (uç, köşe ve kavşak etiketleri + yan duvarda her 5 m'de bir) **24/24** başarılı
oldu. Odometri dönüş hatası %0, %14 ve %25 kademelerinin hepsinde sonuç aynıydı. Duvara temas olmadı ve raydan en büyük
yanal sapma 8 cm'yi geçmedi.

- **Hedefe varış.** Hata LiDAR'lı tabandan yaklaşık 2,5 kat kötü: 0,12 m'ye karşı 0,048 m.
- **Rastgele bırakılma.** 24 koşunun 23'ü başarılı. Konum, 3,5 m içindeki ilk etiketten ortalama 3,8 s (sabit kafa) ve
  6,7 s (tarayan kafa) içinde kuruldu; herhangi bir etiket ilk kez ortalama 0,7 s ve 3,1 s'de göründü. LiDAR'lı karar
  ortalama 26,5 s sürüyordu. Tek başarısızlıkta süzgeç ilk saniyede 2,0 m'deki tek bir etiketten başlatıldı; koşu boyunca en
  büyük konum hatası 1,7 m oldu (başlangıçtaki hata ayrıca kaydedilmedi; olay sırası hatanın başlangıçtan geldiğini
  düşündürüyor). Yalnız 3 ölçüm kabul edildi, 0 ret oldu; yeniden başlatma kancası (arka arkaya 6 ret) bu yüzden hiç
  tetiklenmedi. Robot sonra 262 s boyunca eğik
  açıyla duvara dayalı kaldı. Ön sonar bunu durdurmadı.
- **En küçük yeterli plan.** Etiketler 15 cm, göz hizasında, yan duvarlarda 5 m arayla. Koridor başına 3 ile 8 etiket
  gerekiyor (aşağıdaki tablo).
- **Daha seyrek plan.** Yalnız uç, köşe ve kavşak etiketleri (koridor başına 2 ile 4) yetmedi: tarayan kafayla bile 8
  koşunun 6'sı başarılı oldu, yanal sapma 0,54 m'ye çıktı.
- **8 m aralık.** 8 koşunun 8'i başarılı, ancak yanal sapma 0,16 m'ye çıktı.

Hepsi **simülasyon iyimserliği** altında geçerli: kusursuz baskı, yansıma yok, mercek bozulması yok, düzgün ışık, insan
yok. Görünürlük haritasında etiketin kenarı bir şeyle örtülünce ya da üzerinde parlama olunca algılama **sıfıra** iniyor.
Gerçek koridorda bu ikisi asıl risk.

## Ana tablo (sınama koridorları: koridor_2, 4, 5, 6; tohum 1; LiDAR'lı taban aynı koridorlarda)

| Deney | Koşul | Başarı | Varış hatası ort / en (m) | Raydan yanal sapma ort / en (m) | Duvar teması |
| --- | --- | --- | --- | --- | --- |
| A'dan B'ye | 5 m, dönüş fazlası %0, kafa sabit | 8/8 | 0,121 / 0,150 | 0,054 / 0,082 | 0 |
| A'dan B'ye | 5 m, %14, sabit | 8/8 | 0,122 / 0,151 | 0,055 / 0,082 | 0 |
| A'dan B'ye | 5 m, %25, sabit | 8/8 | 0,120 / 0,151 | 0,054 / 0,082 | 0 |
| A'dan B'ye | 5 m, %25, kafa tarayan | 8/8 | 0,102 / 0,122 | 0,058 / 0,103 | 0 |
| A'dan B'ye | 8 m (komşu), %25, sabit | 8/8 | 0,128 / 0,175 | 0,098 / 0,158 | 0 |
| A'dan B'ye | yalnız uç / köşe / kavşak, %25, tarayan | 6/8 | 0,198 / 0,627 | 0,252 / 0,541 | 0 |
| A'dan B'ye, **LiDAR'lı taban** | ONERI, LiDAR + harita | 24/24 | 0,048 | (ölçülmedi) | 0 |
| Rastgele bırakılma | 5 m, %14, kafa sabit (yerinde tur) | 11/12 | 1,105 (başarılılar ≈ 0,09) | | 2 (1 koşu) |
| Rastgele bırakılma | 5 m, %14, kafa tarayan | 12/12 | 0,084 | | 0 |
| Rastgele bırakılma, **LiDAR'lı taban** | | 20/20 | 0,053 | | 0 |

| Rastgele bırakılma (sınama) | İlk etiket görülme ort / en (s) | Konumlanma süresi ort / en (s) | Konumlanana dek yol ort / en (m) | Toplam süre ort (s) | Yanlış koridor |
| --- | --- | --- | --- | --- | --- |
| kafa sabit | 0,7 / 4,2 | 3,8 / 13,0 | 0,25 / 0,90 | 61,3 | 0 |
| kafa tarayan | 3,1 / 4,5 | 6,7 / 16,3 | 0,16 / 0,50 | 46,2 | 0 |
| LiDAR'lı taban (karar) | | 26,5 | 4,91 | | |

İlk etiket görülme (`ilk_etiket_s`), herhangi bir etiketin ilk kez algılandığı an. Konumlanma (`lokalize_s`), süzgecin
3,5 m içindeki bir etiketten başlatıldığı an; LiDAR'lı tabandaki "karar" ile karşılaştırılabilir olan bu. `rapor.py`
eskiden konumlanma değerlerini "ilk etikete süre / yol" başlığıyla basıyordu; başlık düzeltildi, ilk görülme sütunu
eklendi ve `tablolar.md` yeniden üretildi (CSV'ler ham kayıtlardan birebir aynı çıktı). Yanlış koridorun 0 olması kurgu gereği: her koridorun etiket kimlikleri ayrı
ve sahnede yalnız o koridorun etiketleri var; bu, LiDAR'lı deneydeki harita eşleme kararı gibi bir sınama değil.

İki A'dan B'ye başarısızlığında (yalnız uç / köşe / kavşak planı, koridor_5 ve koridor_6, kapi_6) süzgeç hiç etiket
ölçümü kabul etmedi; robot yalnız odometriyle gitti. LiDAR'lı taban 3 hedef x 2 tohumdan; burada koşulan 2 hedef ve
tohum 1 alt kümesinde de varış hatası 0,050 m.

Yanal sapmanın bir kısmı başlangıçtaki sapmadan geliyor. Başlangıç sapması LiDAR'lı deneyle aynı tohumdan üretildi;
koridor_2'deki 0,082 m'nin hepsi bu sapma. Her koşunun satırı `ab_sinama.csv` ve `kayip_sinama.csv` dosyalarında; tüm
tablolar `tablolar.md` içinde.

## En küçük yeterli etiket planı (15 cm, 1,55 m, std mercek)

Kural: her düz hattın iki ucunda karşı duvara bir etiket, L köşesinde iki dış duvara birer etiket, T kavşağında yan kolun
karşısına bir etiket. Bunlara ek olarak yan duvarlarda her 5 m'de bir etiket, sırayla sol ve sağ duvara, koridora paralel
ve kapı girintilerinden uzak. Konumlar `planlar/<koridor>_5m_15cm_goz.json` dosyalarında.

| Koridor | Küme | Toplam | Uç | Köşe / kavşak | Yan (5 m) |
| --- | --- | --- | --- | --- | --- |
| koridor_1 | geliştirme | 7 | 2 | 0 | 5 |
| koridor_2 | sınama | 3 | 2 | 0 | 1 |
| koridor_3 | geliştirme | 8 | 2 | 2 | 4 |
| koridor_4 | sınama | 8 | 3 | 1 | 4 |
| koridor_5 | sınama | 6 | 2 | 0 | 4 |
| koridor_6 | sınama | 6 | 2 | 0 | 4 |

Aralık geliştirme koridorlarında seçildi. Ölçüt, raydan yanal sapmanın 0,15 m'nin altında kalması (%25 dönüş fazlasıyla).
Geliştirmede bulunan yanal sapma ortalama / en büyük değerleri:

| Plan | Yanal sapma ort / en (m) |
| --- | --- |
| Yalnız uç / köşe / kavşak | 0,18 / 0,25 |
| 12 m aralık | 0,16 / 0,25 |
| 8 m aralık | 0,12 / 0,18 |
| 5 m aralık | 0,08 / 0,11 |
| 3 m aralık | 0,08 / 0,11 |

5 m, ölçütü karşılayan en seyrek aralık. 3 m bir şey kazandırmıyor. Sınamada 8 m de 0,16 m ile sınırda kaldı.
Geliştirmedeki 14 koşunun hepsi başarılı.

- **Boy.** Navigasyon koşularında yalnız 15 cm denendi. 10 cm etiketin menzili görünürlük haritasında 5 m'ye düşüyor (15
  cm'de 8 m). 20 cm'de ise menzil 10 m'ye çıkıyor ama 65° bakış açısında kazanç yok (iki boyda da 4 m). 5 m aralık için 15
  cm yeterli; 10 cm sınırda.
- **Yükseklik.** Göz hizasında (1,55 m) bir etiket 0,75 m'den itibaren görülüyor. Kapı üstündeki (2,20 m) etiket kafa düz
  bakarken karşıdan 3 m'den, açılı bakışta 2 m'den yakında kadraja girmiyor; bu yüzden göz hizası öneriliyor.

## Mercek ve çözünürlük önerisi

**Öneri: Camera Module 3 standart mercek (yatay 66°, dikey 41°, f 4,74 mm), işleme 1152 x 648, 10 Hz.** Wide mercek
(102° / 67°) aynı çözünürlükte menzili yarıya indiriyor: 15 cm etiket karşıdan 4 m'de görülüyor, standart mercekte 8 m.
Kayıp robot aramasında geniş açının sağlayacağı kazancı tarayan kafa zaten veriyor. Wide mercek navigasyon koşularında
denenmedi; bu karar yalnız görünürlük haritasına dayanıyor. Görüş açıları Raspberry Pi belgesinden alındı (bağlantı
`kamera.py` içinde, `MERCEK_KAYNAK`).

En uzak güvenilir algılama mesafesi (m) aşağıda. Algılama oranı o mesafeye kadar kesintisiz 0,75 ve üstünde. Göz hizası,
temiz görüntü, 1152 x 648:

| Mercek | Boy | 0° | 30° | 50° | 65° | 75° |
| --- | --- | --- | --- | --- | --- | --- |
| std | 10 cm | 5 | 4 | 5 | 3 | 2 |
| std | 15 cm | 8 | 6 | 6 | 4 | 2 |
| std | 20 cm | 10 | 8 | 8 | 4 | 2 |
| geniş | 10 cm | 4 | 2 | 2 | 2 | 0 |
| geniş | 15 cm | 4 | 4 | 4 | 2 | 1 |
| geniş | 20 cm | 6 | 6 | 5 | 3 | 3 |

Çözünürlüğün etkisi (std, 15 cm, karşıdan): 768 x 432'de 5 m, 1152 x 648'de 8 m, 1536 x 864'te 10 m. Tablonun tamamı
`tablolar.md` içinde, ısı haritası `../gorsel/gorunurluk.png`.

**Poz hatası** (std, 1152, 15 cm, ortanca değerler):

| Mesafe | Menzil hatası | Tek etiketten konum hatası |
| --- | --- | --- |
| 2 m | 1,2 cm | 1,5 cm |
| 3 m | 1,6 cm | 5,7 cm |
| 4 m | 10 cm | 13 cm |

- **Kerteriz.** Her mesafede 0,03 ile 0,06° arasında. Uzakta bile en güvenilir ölçüm bu.
- **Etiketin yönü (psi).** 4 m'nin ötesinde ters çözümlere (100°'yi aşan hatalar) düşüyor. Bu yüzden süzgeç yönü kapıdan
  geçiriyor ve kayıp robot en çok 3,5 m'deki bir etiketten başlatılıyor.

**Bozulmalar** (std, 1152, 15 cm; en uzak güvenilir mesafe, 0° / 30° / 50° / 65°):

| Bozulma | Mesafe (m) | Not |
| --- | --- | --- |
| Temiz | 8 / 6 / 6 / 4 | |
| Okuma gürültüsü x5 | 8 / 6 / 4 / 3 | |
| Loş ışık (%12 aydınlık, 33 ms pozlama) | 8 / 6 / 6 / 2 | |
| Gövde 0,4 rad/s dönerken | 2 / 6 / 4 / 3 | Karşıdaki etiket bulanıklıkla küçülüyor |
| Gövde 0,89 rad/s dönerken | 2 / 2 / 2 / 1 | |
| Parlama lekesi (etiket üstünde, genlik 230) | 0 | Bu düzey sert seçildi; daha hafif bir düzey denenmedi |
| Kenarın %25 / %50 örtülmesi | 0 | aruco kenar karesi bozulunca kodu çözmüyor |

Gövde dönüşündeki bulanıklık yüzünden yerinde dönüşün tavanı 0,5 rad/s'de tutuldu; dönüşten sonra 0,6 s duruluyor.

## Pi 5 gerçekçiliği (VARSAYIM)

Bu bilgisayarda kare başına süreler, tek iş parçacığıyla (`hiz.csv`):

| Çözünürlük | Görüntü üretimi + bozma | Algılama | Toplam |
| --- | --- | --- | --- |
| 768 x 432 | ≈ 9 ms | 5 ms | ≈ 69 kare/s |
| 1152 x 648 | ≈ 18 ms | 13 ms | ≈ 32 kare/s |
| 1536 x 864 | ≈ 39 ms | 24 ms | ≈ 16 kare/s |

Hız ölçümündeki karelerde etiket yoktu (`hiz.csv`, bulunan = 0); etiketli karede algılama biraz daha uzun sürebilir.
Pi 5'in (Cortex-A76) bu işte 3 ile 4 kat yavaş olacağı **varsayıldı, ölçülmedi**. Bu varsayımla 1152 x 648'de algılama
40 ile 55 ms tutar, 10 Hz sığar. 1536 x 864'te 70 ile 100 ms tutar, sınırda kalır. Kamera 2304 x 1296 modunda 56 kare/s
ya da 1536 x 864 modunda 120 kare/s verir; 1152 x 648 ölçeklenmiş ISP çıkışı varsayıldı. Pozlama 10 ms, loşta en çok 33
ms.

## Kafa taraması (deney iii)

- **A'dan B'ye.** Tarayan kafa varış hatasını 0,120 m'den 0,102 m'ye indirdi; yanal sapmaya etkisi yok. Yalnız uç / köşe
  / kavşak planında tarayan kafa bile 8 koşunun 6'sında kaldı. Sabit kafa bu planla geliştirmede 2/2 başarılı oldu ama
  yanal sapma 0,25 m'ydi; bu kombinasyon sınamada koşulmadı.
- **Rastgele bırakılma.** Tarayan kafa 12/12, sabit kafa 11/12 başarılı oldu. Tarayan kafa konumunu daha geç kuruyor
  (6,7 s'ye karşı 3,8 s; ilk etiketi görmesi 3,1 s'ye karşı 0,7 s), çünkü gövde durup kafa beş yöne bakıyor. Buna karşın toplam süre daha kısa (46 s'ye karşı 61
  s), daha az yol gidiyor ve varış daha isabetli. Sabit kafanın tek başarısızlığı yukarıdaki yanlış başlatma.

## Dürüst ayrım ve kapsam

- **Geliştirme.** koridor_1 ve koridor_3, tohum 101. Plan aralığı ve süzgeç ayarları burada seçildi. Görünürlük haritası
  ayrı bir yapay duvar sahnesinde çıkarıldı.
- **Sınama.** koridor_2, 4, 5, 6, tohum 1. Bu koşulardan sonra hiçbir ayar değişmedi.
- **Geliştirmede yapılan düzeltme.** Süzgece dönüş ölçeği durumu eklendi. Neden: %25 dönüş fazlasıyla koridor_3'te 90°
  köşeden sonra süzgeç 13° yön hatasını 0,9° std ile "emin" taşıdı, doğru etiketleri reddetti ve yanal sapma 0,62 m'ye
  çıktı. Ölçek eklendikten sonra sapma 0,11 m oldu.
- **Beyin ve hakem.** Beyin yalnız odometriyi (bozulmuş), kamera karesini, sonar mesafesini ve kendi gönderdiği kafa
  açısını görür. Yer gerçeği yalnız hakemde.

**Süre bütçesi için küçültülenler (söylenmesi gerekenler):**

- Geliştirmede koridor başına yalnız en uzak hedef koşuldu. %0 dönüş fazlası yalnız kavşak planında ve 12 m aralıkta
  koşuldu.
- Sınamada 3 hedeften 2'si koşuldu (orta ve en uzak).
- Rastgele bırakılmada sınama koridoru başına 3 bırakma yapıldı (LiDAR'lı deneyde 5).
- Her koşulda tek tohum kullanıldı. Tohumlar arası çeşitlilik başlangıç sapmasından ve bırakma noktasından geliyor.
- Navigasyon koşularında yalnız 15 cm etiket, göz hizası ve std mercek kullanıldı. 10 / 20 cm, kapı üstü ve Wide mercek
  yalnız görünürlük haritasında ölçüldü.
- Parlamanın daha hafif bir düzeyi denenmedi.
- Kapı tabelası benzeri yazılı levha denemesi kapsam dışı bırakıldı (istendiği gibi yapılmadı).

## Simülasyon iyimserliği

- Baskı kusursuz, duvar düz ve mat. Yansıma ya da parlak laminasyon yok; parlama yalnız yapay bir leke olarak denendi.
- Mercek bozulması yok: Wide mercek iğne deliği modeliyle çizildi. Yuvarlanan deklanşör yok.
- Kafa titreşimi ve gövde eğimi yok. Kafa servosunun açısı Beyin'in modeliyle aynı hız tablosundan geliyor.
- Işık düzgün ve ortam ışığı artırıldı (koyu yan duvarlar için).
- İnsan, kapı kanadı ve hareketli engel yok.
- Sonar ideal: dar koni, 1 cm gürültü, karışma yok.
- Odometrinin dönüş hatası sabit bir ölçek olarak modellendi. Gerçekte zemine ve yüke göre değişir.
- Etiket haritası (her etiketin yeri ve yönü) ve kameranın iç parametresi K kusursuz biliniyor: montaj / ölçüm hatası ve
  kalibrasyon hatası yok. Etiket yönündeki 1-2°'lik bir montaj hatası süzgecin yön düzeltmesine doğrudan biner.
- Algılama gecikmesi yok: kare alındığı adımda süzgece giriyor. Pi 5'te 40 ile 55 ms varsayılan algılama süresi
  modellenmedi; sabit kafayla dönerek aramada bu gecikme kerterize birkaç derece hata ekleyebilir.

Gerçek robotta ilk ölçülmesi gerekenler:

- Gerçek bir koridorda ve gerçek ışıkta 15 cm baskı etiketin algılama menzili.
- Hareket bulanıklığı.
- Pi 5 algılama süresi.
- Tek etiketten başlatmanın güvenilirliği (sınamadaki tek başarısızlığın nedeni).
