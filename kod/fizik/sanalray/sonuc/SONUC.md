# Sanal ray sonucu: LiDAR'sız gezinme (kamera + etiket + enkoder + ön sonar)

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
