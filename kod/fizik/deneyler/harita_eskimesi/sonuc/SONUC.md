# Harita eskimesi: sonuç (2026-11-25)

Robotun haritası ile dünya artık aynı değilken koridor gezinmesi. Beyinler (`AbBeyni`, `KayipBeyni`), konumlayıcı (v3 çok
haritalı MCL) ve izleyici **değiştirilmeden, varsayılan ayarlarla** koşuldu; yalnız dünya bozuldu. Robot ONERI (öneri
firmware + ön omni, VARSAYIM). Kurulum ve etkenlerin tanımı: `../BENIOKU.md`. Tablolar `analiz.py` ile `ham/`'dan üretilir
(`tablolar.md`, `ozet.json`, `*.csv`).

## Hüküm

**Geometrisi düzgün, kapıları sabit bir koridorda güvenilir; haritanın ayırt edici yapıları değişince ya da LiDAR yüzeyden
dönüş alamayınca güvenilmez, ve bozulma zarif değil, ani.**

- Kırmayanlar (en ağır kademede de A'dan B'ye 12/12, kayıp 12/12 ya da 11/12): ölçek hatası %3, koridor genişliği ±10 cm,
  eğrilme 4° / 20 m, menzil gürültüsü σ 8 cm, odometri öteleme +%10, dönüş +%25 (tabandaki %14'e ek), yol veren insanlar
  4 kişi / 10 m, duvardan 1,2 m'ye dek giren grup. Bunlar konum hatasını büyütür (ölçek %3: 8 cm, genişlik 10 cm: 5 cm,
  odometri +%10: 9 cm ortalama) ama sıçratmaz.
- Kıranlar (başarı %90'ın altına, 12 koşuda 10 / 12 ya da daha az): **kapı durumu** (%25 kapı değişince A'dan B'ye 9/12,
  kayıp 10/12; hepsi değişince 8/12 ve 3/12), **cam kapı** (%25'te 10/12), **en uzun menzil** (4 m'de 10/12 ve 7/12;
  2 m'de 8/12 ve 3/12), **ani teker kayması** (2 olay / dk'da 10/12), **eşya** (4 adet / 10 m'de 9/12 ve 9/12),
  **dönüşsüz yüzey** (%75'te 8/12 ve 3/12; %50'ye dek 12/12).
  *Güncellendi (tamamlama turu):* cam kapı ve ani kaymanın kırılma iddiası sınırdaki koşulara dayanıyor. 5 koşu hedefe
  0,30-0,34 m'de "vardım" dedi (sıçrama değil, pay sınırı). Katı sayım (0,3 m): cam %25'te kırar (10/12), ani kayma
  2 / dk'da (10/12). Sınırdakiler başarı sayılırsa: cam %50'de kırar (11, 10, 8, 9 /12), ani kayma hiç kırmaz
  (12, 12, 11, 11 /12), kapı yine %25'te (12, 9, 8, 8 /12). Öbür kırılma noktaları iki sayımda aynı.
- **Sıradan okul günü hafifte bile kırıyor**: hafif 9/12 ve 10/12, orta 3/12 ve 4/12, ağır 0/12 ve 0/12.
- Nasıl bozuluyor: A'dan B'ye 68 başarısızlığın 64'ünde konum tahmini 1 m'den çok sıçradı (çoğu 10–25 m: düzenli kapı
  ritmindeki "takma" bir yere), 53'ünde robot yanlış yerde durup "vardım" dedi, 54'ünde konumlayıcı bu yanlış konumdan
  "emin"di (`konum_kararsiz` False, hata > 0,5 m). Yani hata çoğunlukla fark edilmeden olur. Kayıp robotta yanlış
  koridora kesin karar tabanda 0 / 12 iken kapı %100, eşya 4 / 10 m, dönüşsüz %75'te 3 / 12, orta günde 6 / 12.
- Temas: A'dan B'ye 720 koşuda 6 temas olayı (5 koşu; hepsi robot hareket hâlindeyken), MuJoCo'da 87 koşuda 0. Kayıp
  robotun tepkisel keşfinde (önde engel yoksa ilerle) 240 koşuda 57; dönüşsüz yüzey %75'te 11, ağır günde 38: LiDAR'ın
  görmediği duvar keşif sürüşünde boş alan sayılıyor. Duran robota temas yalnız kayıpta 3 (okul günü; insan modeli yol
  verir).
- Ne zaman güvenilmez, kısaca: kapıların dörtte biri haritadakinden farklıysa, kapıların dörtte biri camsa, duvarların
  dörtte üçü dönüş vermiyorsa ya da etkin menzil ≈ 4 m'ye inerse; bunların birkaçı hafif dozda birlikte olduğunda da.
- Ucuz düzeltme önerisi (varsayılan DEĞİŞTİRİLMEDİ, ayrı tohumlarda ölçüldü, aşağıda): başlangıcı bilinen gezinmede
  artırılmış MCL'nin rastgele saçmasını kapatmak ("izleme") hafif günü 8/12'den 12/12'ye, orta günü 5/12'den 12/12'ye,
  kapı %50'yi 8/12'den 12/12'ye çıkardı; ağır günde işe yaramadı (1/12 -> 0/12; sıçrama yerine 0,3–3 m kayma ve bekleme).

## Gerçek robotta ilk ölçülmesi gereken üç şey

1. **Okulun koridorunda LiDAR'ın dönüş haritası:** rota boyunca (robotu elle iterek ya da bir arabada) taramaları kaydet;
   yüzey türüne göre dönüşsüz ışın oranı (cam kapı, cam bölme, koyu / parlak kaplama, dolap kapakları) ve etkin en uzun
   menzil. Zarar sırasının ilk dördünden üçü (düzeltilmiş sırayla cam, menzil, dönüşsüz yüzey; ilki kapı) buna bağlı;
   simülasyon bunları tahmin ediyor.
2. **Haritanın ne kadar eskidiği:** haritayı bir kez çıkar, sonra günün farklı saatlerinde aynı yerlerden tarama al;
   haritadan > 15 cm sapan nokta oranını, kapı durumu değişimini (kaç kapı, ne sıklıkla) ve duvar dibindeki eşya sayısını
   say. Bu sayılar bu deneyin kademe eksenine doğrudan yerleşir (hangi kademede yaşandığını söyler).
3. **Teker kayması olayları:** gerçek zeminde (koridor taşı, eşik, ıslak zemin) enkoder odometrisini yer işaretlerine
   (bant, ölçülü noktalar) karşı ölç: ani kayma sıklığı (olay / dk) ve büyüklüğü, dönüşte fazla bildirme. Odometri
   etkenlerinden yalnız ani kayma kırdı (2 / dk); sistematik hatalar (+%10 öteleme, +%25 dönüş) kırmadı.

## Ne ölçüldü (kapsam, tohumlar, geliştirme / sınama)

- **2B ızgara (hüküm verilen):** 60 koşul (taban + 14 alt etken x 4 kademe + okul günü 3 kademe) x 6 koridor x 2 tohum =
  **720 A'dan B'ye** koşusu; **240 kayıp robot** koşusu (20 koşul x 12; aşağıda neyin atıldığı). Tohumlar gezinme
  senaryolarıyla aynı (A'dan B'ye t = 1, 2; kayıp bırakma 0, 1); taban aynı tohumlarla bozulmasız. Dünya bozucusu
  tohumu kademeden bağımsız (kademeler iç içe), benzetici gürültüsü koşuldan bağımsız (ortak rastgele sayılar).
- **MuJoCo doğrulaması:** `gezinme.duzenek.Duzenek` (sahte ESP32 firmware modeli, enkoder odometrisi, sanal LiDAR, TASLAK
  sonar kuralı açık), aynı dünya JSON'u, A'dan B'ye, 13 alt etkenin 2. ve 4. kademesi + okul orta / ağır + taban, 3 koşu
  (koridor_5 t1, koridor_1 t2, koridor_3 t2): **87 koşu**.
- **Geliştirme / sınama:** ana ızgarada hiçbir şey ayarlanmadı (konumlayıcı, izleyici, eşikler varsayılan); 720 + 240 +
  87 koşunun hepsi sınamadır. İsteğe bağlı varyantın varsayımı ana ızgaranın başarısızlıklarından (t = 1, 2) çıkarıldı
  (geliştirme); varyant ve karşılaştırma tabanı **ayrı tohumlarda** (t = 3, 4; 16 koşul x 12 x 2 = 384 koşu) ölçüldü
  (sınama). Varyant hükmü yalnız o 384 koşudan.
- Başarı ölçütü gezinme senaryolarıyla aynı: yer gerçeği gövde merkezi hedefin GERÇEK yerinin (geometri bozucusunda
  T(hedef)) 0,3 m içinde ve robot durmuş. Konum hatası tarama başına, harita çerçevesinde (T⁻¹(gerçek)); kayıpta yalnız
  doğru koridora karar verildikten sonra. "Kesin-yanlış konum": `konum_kararsiz` False iken hata > 0,5 m.
- 12 koşuda %90 eşiği: 11 / 12 (%92) geçer, 10 / 12 (%83) kalır. Belirsizlik büyük (11 / 12'nin %95 Wilson aralığı
  %65–99): kırılma kademesi ± 1 kademe okunmalı; sıralama ortalama başarıdan.
- Sınırdaki başarısızlıklar (bağımsız denetim notu): A'dan B'ye 68 başarısızlığın 5'i hedefe 0,30–0,34 m'de "vardım"
  deyip durdu (tahmin hatası ≈ 0,28 m; sıçrama yok): cam %25 (koridor_1 t1), kapı %10 ve %50 (koridor_1 t1), ani kayma
  2 / dk (koridor_5 t1) ve 4 / dk (koridor_1 t2). Bunlar başarı sayılsaydı cam kapının kırılması %25'ten %50'ye kayar,
  ani kayma hiçbir kademede kırmazdı (11 / 12, 11 / 12): bu iki etkenin kırılma iddiası kademe başına tek kaba
  başarısızlığa dayanıyor. Başarısızlıkların çoğu iki koridorda (okul günü dışı 44'ün 21'i koridor_1, 11'i koridor_5);
  etkin örneklem koridor sayısıyla (6) sınırlı.

## Ana tablo: kırılma noktaları ve zarar sırası

| Etken | A'dan B'ye kırılma (başarı < %90) | A'dan B'ye kademe başarıları | Kayıp kırılma | Kayıp kademe başarıları |
| --- | --- | --- | --- | --- |
| a. kapı durumu değişen oran | 25 % (k2) | 11/12, 9/12, 7/12, 8/12 | 25 % (k2) | 10/12, 3/12 |
| b. eşya (adet / 10 m) | 4 (k4) | 12/12, 12/12, 12/12, 9/12 | 4 (k4) | 9/12 |
| c. insan (kişi / 10 m) | yok | 12/12, 12/12, 12/12, 12/12 | yok | 11/12 |
| c. grup (duvardan içeri m) | yok | 12/12, 12/12, 12/12, 11/12 | yok | 12/12 |
| d. ölçek hatası | yok | 12/12, 12/12, 12/12, 12/12 | yok | 12/12 |
| d. genişlik sapması (m) | yok | 12/12, 12/12, 12/12, 12/12 | yok (güncellendi: tamamlama turu) | 12/12, 12/12, 12/12, 12/12 |
| d. eğrilme (° / 20 m) | yok | 12/12, 12/12, 12/12, 12/12 | yok | 12/12 |
| e. menzil gürültüsü σ (m) | yok | 12/12, 12/12, 12/12, 12/12 | yok | 12/12 |
| e. dönüşsüz yüzey oranı | 75 % (k4) | 12/12, 12/12, 12/12, 8/12 | 75 % (k4) | 3/12 |
| e. cam kapı oranı | 25 % (k1) | 10/12, 10/12, 8/12, 9/12 | 100 % (k4) | 11/12, 6/12 |
| e. en uzun menzil (m) | 4 (k3) | 11/12, 11/12, 10/12, 8/12 | 4 (k3) | 7/12, 3/12 |
| f. odometri ölçek (+) | yok | 12/12, 12/12, 12/12, 12/12 | yok | 12/12 |
| f. dönüş hatası (+, %14 tabana ek) | yok | 12/12, 12/12, 12/12, 12/12 | yok | 12/12 |
| f. ani kayma (olay / dk) | 2 (k3) | 12/12, 12/12, 10/12, 10/12 | yok | 12/12 |
| g. okul günü (hafif / orta / ağır) | hafif (k1) | 9/12, 3/12, 0/12 | hafif (k1) | 10/12, 4/12, 0/12 |

**Zarar sırası (güncellendi, tamamlama turu; `analiz.siralama()` düzeltildi).** Sıra YALNIZ tam ızgaralı A'dan B'ye
ortalamasından (her etken 4 kademe x 12 koşu = 48), eşitlikte en kötü kademe. Kayıp ortalaması sıraya girmez, çünkü
kayıpta etkenlerin ölçülen kademe sayısı eşit değil (0-2). İki sayım: katı (0,3 m) ve sınırdaki 5 koşu başarı sayılırsa.

| Sıra | Etken | A'dan B'ye ort başarı (katı) | en kötü kademe | sınırdakiler başarı sayılırsa | Kayıp ort (ölçülen kademe sayısı), yalnız bilgi |
| --- | --- | --- | --- | --- | --- |
| 1 | a. kapı durumu değişen oran | 73 % (35/48) | 58 % | 77 % | 54 % (2) |
| 2 | e. cam kapı oranı | 77 % (37/48) | 67 % | 79 % | 71 % (2) |
| 3 | e. en uzun menzil (m) | 83 % (40/48) | 67 % | 83 % | 42 % (2) |
| 4 | e. dönüşsüz yüzey oranı | 92 % (44/48) | 67 % | 92 % | 25 % (1) |
| 5 | f. ani kayma (olay / dk) | 92 % (44/48) | 83 % | 96 % | 100 % (1) |
| 6 | b. eşya (adet / 10 m) | 94 % (45/48) | 75 % | 94 % | 75 % (1) |
| 7 | c. grup (duvardan içeri m) | 98 % (47/48) | 92 % | 98 % | 100 % (1) |
| 8-14 | insan, ölçek, genişlik, eğrilme, menzil gürültüsü, odometri ölçek, dönüş hatası | 100 % | 100 % | 100 % | 92-100 % (genişlik: bkz. "Tamamlama turu") |

Sağlam olan: kapı, cam ve menzil iki sayımda da ilk üç; dönüşsüz yüzey A'dan B'ye'de ani kaymayla eşit (44 / 48), en
kötü kademesi daha kötü (%67, ani kayma %83); sınırdakiler başarı sayılırsa ani kayma dönüşsüzün arkasına düşer (%96).

Eski sıra (YANLIŞTI, yalnız kayıt için; kayıpta eşit olmayan kademe kapsamıyla iki ortalamanın ortalaması):

| Sıra | Etken | A'dan B'ye ort başarı | en kötü kademe | Kayıp ort başarı | en kötü kademe |
| --- | --- | --- | --- | --- | --- |
| 1 | e. dönüşsüz yüzey oranı | 92 % | 67 % | 25 % | 25 % |
| 2 | e. en uzun menzil (m) | 83 % | 67 % | 42 % | 25 % |
| 3 | a. kapı durumu değişen oran | 73 % | 58 % | 54 % | 25 % |
| 4 | e. cam kapı oranı | 77 % | 67 % | 71 % | 50 % |
| 5 | b. eşya (adet / 10 m) | 94 % | 75 % | 75 % | 75 % |
| 6 | c. insan (kişi / 10 m) | 100 % | 100 % | 92 % | 92 % |
| 7 | f. ani kayma (olay / dk) | 92 % | 83 % | 100 % | 100 % |
| 8 | c. grup (duvardan içeri m) | 98 % | 92 % | 100 % | 100 % |
| 9 | d. ölçek hatası | 100 % | 100 % | 100 % | 100 % |
| 10 | d. genişlik sapması (m) | 100 % | 100 % | - | - |
| 11 | d. eğrilme (° / 20 m) | 100 % | 100 % | 100 % | 100 % |
| 12 | e. menzil gürültüsü σ (m) | 100 % | 100 % | 100 % | 100 % |
| 13 | f. odometri ölçek (+) | 100 % | 100 % | 100 % | 100 % |
| 14 | f. dönüş hatası (+, %14 tabana ek) | 100 % | 100 % | 100 % | 100 % |

Uyarı (bağımsız denetim notu): bu sıra, kayıpta eşit olmayan kademe kapsamına duyarlı. Kayıpta dönüşsüz yüzey, eşya,
insan ve ani kayma yalnız en ağır (4.) kademede, kapı / cam / menzil iki kademede koşuldu; yalnız en kötü kademesi
ölçülen etkenin kayıp ortalaması kötü görünür. Tam ızgaralı A'dan B'ye ortalamasına göre sıra: kapı (%73) > cam (%77) >
menzil (%83) > dönüşsüz (%92) = ani kayma (%92) > eşya (%94) > grup (%98) > insan (%100). "Dönüşsüz > menzil > kapı"
sıralaması sağlam değil. Sağlam olan: kapı, cam ve menzil her ölçütte ilk dörtte; dönüşsüz yüzey kayıpta en ağır
etken, A'dan B'ye ortalamada ani kaymayla eşit (44 / 48).

## A'dan B'ye, 2B (720 koşu)

| Koşul | Kademe | Başarı | Varış hatası medyan (m) | Konum hatası ort / p95 / en büyük (m) | Kesin-yanlış konum (koşu) | Temas hareketli / duran | Bekleme ort (s) | NaN ışın |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| taban (bozulmasız) | - | 12 / 12 | 0.049 | 0.005 / 0.015 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
| a. kapı durumu değişen oran | 10 % | 11 / 12 | 0.049 | 0.008 / 0.040 / 0.29 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 25 % | 9 / 12 | 0.048 | 1.672 / 4.818 / 25.06 | 3 | 0 / 0 | 0.0 | 0.02 |
|  | 50 % | 7 / 12 | 0.047 | 1.932 / 3.658 / 22.56 | 4 | 0 / 0 | 0.0 | 0.02 |
|  | 100 % | 8 / 12 | 0.048 | 2.441 / 5.342 / 25.06 | 4 | 0 / 0 | 0.0 | 0.02 |
| b. eşya (adet / 10 m) | 0.5 | 12 / 12 | 0.049 | 0.018 / 0.064 / 0.14 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 1 | 12 / 12 | 0.051 | 0.030 / 0.088 / 0.15 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 2 | 12 / 12 | 0.054 | 0.043 / 0.124 / 0.37 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 4 | 9 / 12 | 0.056 | 0.694 / 2.179 / 17.86 | 2 | 0 / 0 | 0.0 | 0.02 |
| c. insan (kişi / 10 m) | 0.5 | 12 / 12 | 0.049 | 0.008 / 0.021 / 0.07 | 0 | 0 / 0 | 0.3 | 0.02 |
|  | 1 | 12 / 12 | 0.047 | 0.012 / 0.027 / 0.11 | 0 | 0 / 0 | 0.2 | 0.02 |
|  | 2 | 12 / 12 | 0.049 | 0.014 / 0.031 / 0.09 | 0 | 0 / 0 | 0.4 | 0.02 |
|  | 4 | 12 / 12 | 0.046 | 0.023 / 0.055 / 0.25 | 0 | 0 / 0 | 0.1 | 0.01 |
| c. grup (duvardan içeri m) | 0.6 | 12 / 12 | 0.050 | 0.013 / 0.033 / 0.08 | 0 | 0 / 0 | 2.8 | 0.02 |
|  | 0.9 | 12 / 12 | 0.049 | 0.012 / 0.029 / 0.07 | 0 | 0 / 0 | 14.5 | 0.02 |
|  | 1.2 | 12 / 12 | 0.049 | 0.012 / 0.029 / 0.07 | 0 | 0 / 0 | 14.7 | 0.01 |
|  | 1.5 | 11 / 12 | 0.049 | 0.037 / 0.025 / 12.02 | 1 | 0 / 0 | 16.2 | 0.01 |
| d. ölçek hatası | 0.5 % | 12 / 12 | 0.035 | 0.016 / 0.032 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 1 % | 12 / 12 | 0.021 | 0.029 / 0.055 / 0.08 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 2 % | 12 / 12 | 0.020 | 0.057 / 0.114 / 0.17 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 3 % | 12 / 12 | 0.035 | 0.084 / 0.163 / 0.24 | 0 | 0 / 0 | 0.0 | 0.02 |
| d. genişlik sapması (m) | ± 2.5 cm | 12 / 12 | 0.050 | 0.013 / 0.020 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | ± 5 cm | 12 / 12 | 0.055 | 0.025 / 0.031 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | ± 7.5 cm | 12 / 12 | 0.061 | 0.038 / 0.044 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | ± 10 cm | 12 / 12 | 0.070 | 0.052 / 0.064 / 0.08 | 0 | 0 / 0 | 0.0 | 0.02 |
| d. eğrilme (° / 20 m) | 0.5 | 12 / 12 | 0.049 | 0.004 / 0.015 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 1 | 12 / 12 | 0.049 | 0.005 / 0.017 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 2 | 12 / 12 | 0.049 | 0.007 / 0.020 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 4 | 12 / 12 | 0.050 | 0.011 / 0.030 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
| e. menzil gürültüsü σ (m) | 0.02 | 12 / 12 | 0.048 | 0.005 / 0.016 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 0.03 | 12 / 12 | 0.051 | 0.005 / 0.018 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 0.05 | 12 / 12 | 0.047 | 0.007 / 0.020 / 0.07 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 0.08 | 12 / 12 | 0.045 | 0.010 / 0.027 / 0.08 | 0 | 0 / 0 | 0.0 | 0.02 |
| e. dönüşsüz yüzey oranı | 10 % | 12 / 12 | 0.049 | 0.006 / 0.018 / 0.06 | 0 | 0 / 0 | 0.0 | 0.12 |
|  | 25 % | 12 / 12 | 0.047 | 0.007 / 0.020 / 0.07 | 0 | 0 / 0 | 0.0 | 0.27 |
|  | 50 % | 12 / 12 | 0.050 | 0.009 / 0.029 / 0.10 | 0 | 0 / 0 | 0.0 | 0.50 |
|  | 75 % | 8 / 12 | 0.048 | 1.489 / 3.403 / 22.36 | 3 | 1 / 0 | 20.1 | 0.78 |
| e. cam kapı oranı | 25 % | 10 / 12 | 0.049 | 0.302 / 1.054 / 14.32 | 1 | 0 / 0 | 10.8 | 0.02 |
|  | 50 % | 10 / 12 | 0.050 | 1.065 / 2.141 / 15.36 | 3 | 0 / 0 | 4.4 | 0.02 |
|  | 75 % | 8 / 12 | 0.048 | 2.283 / 6.517 / 26.04 | 6 | 0 / 0 | 0.0 | 0.02 |
|  | 100 % | 9 / 12 | 0.047 | 2.941 / 5.073 / 24.86 | 5 | 0 / 0 | 17.0 | 0.02 |
| e. en uzun menzil (m) | 8 | 11 / 12 | 0.048 | 0.357 / 1.496 / 19.08 | 1 | 0 / 0 | 0.0 | 0.05 |
|  | 6 | 11 / 12 | 0.048 | 0.468 / 1.523 / 11.43 | 3 | 0 / 0 | 0.0 | 0.08 |
|  | 4 | 10 / 12 | 0.047 | 0.351 / 1.708 / 9.26 | 5 | 0 / 0 | 0.0 | 0.16 |
|  | 2 | 8 / 12 | 0.049 | 2.042 / 4.573 / 28.36 | 5 | 0 / 0 | 15.2 | 0.36 |
| f. odometri ölçek (+) | 2 % | 12 / 12 | 0.060 | 0.017 / 0.029 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 5 % | 12 / 12 | 0.077 | 0.043 / 0.066 / 0.09 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 7.5 % | 12 / 12 | 0.092 | 0.064 / 0.099 / 0.14 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 10 % | 12 / 12 | 0.106 | 0.092 / 0.153 / 0.25 | 0 | 0 / 0 | 0.0 | 0.02 |
| f. dönüş hatası (+, %14 tabana ek) | 5 % | 12 / 12 | 0.050 | 0.005 / 0.014 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 10 % | 12 / 12 | 0.050 | 0.005 / 0.016 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 15 % | 12 / 12 | 0.049 | 0.005 / 0.016 / 0.06 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 25 % | 12 / 12 | 0.050 | 0.005 / 0.017 / 0.08 | 0 | 0 / 0 | 0.0 | 0.02 |
| f. ani kayma (olay / dk) | 0.5 | 12 / 12 | 0.049 | 0.012 / 0.061 / 0.26 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 1 | 12 / 12 | 0.049 | 0.024 / 0.124 / 0.43 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 2 | 10 / 12 | 0.050 | 0.046 / 0.150 / 3.18 | 0 | 0 / 0 | 0.0 | 0.02 |
|  | 4 | 10 / 12 | 0.059 | 0.097 / 0.309 / 1.17 | 2 | 0 / 0 | 0.0 | 0.02 |
| g. okul günü (hafif / orta / ağır) | hafif | 9 / 12 | 0.048 | 2.266 / 2.705 / 21.84 | 4 | 0 / 0 | 28.0 | 0.09 |
|  | orta | 3 / 12 | 0.059 | 2.586 / 5.590 / 22.46 | 8 | 2 / 0 | 6.2 | 0.30 |
|  | ağır | 0 / 12 | - | 5.001 / 11.600 / 24.71 | 9 | 3 / 0 | 17.1 | 0.52 |

Bekleme: robotun önünde engel görüp durduğu süre (grup 0,9 m'den içeri girince ≈ 15 s; grup 30 s sonra dağılır). Başarılı
koşunun süresi medyan: taban 72 s, grup 1,5 m 93 s.

## Kayıp robot, 2B (240 koşu)

| Koşul | Kademe | Başarı | Yanlış koridora kesin karar (ilk / son) | Karar yok | Karar süresi medyan (s) | Karar yolu medyan (m) | Konum hatası ort / p95 (m, karardan sonra) | Temas hareketli / duran |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| taban (bozulmasız) | - | 12 / 12 | 0 / 0 | 0 | 6 | 1.0 | 0.008 / 0.029 | 0 / 0 |
| a. kapı durumu değişen oran | 25 % | 10 / 12 | 0 / 0 | 0 | 4 | 0.6 | 1.185 / 4.215 | 0 / 0 |
|  | 100 % | 3 / 12 | 3 / 3 | 0 | 9 | 1.5 | 6.942 / 11.494 | 0 / 0 |
| b. eşya (adet / 10 m) | 4 | 9 / 12 | 3 / 3 | 0 | 4 | 0.6 | 0.831 / 2.002 | 0 / 0 |
| c. insan (kişi / 10 m) | 4 | 11 / 12 | 0 / 0 | 0 | 6 | 1.0 | 0.019 / 0.037 | 0 / 0 |
| c. grup (duvardan içeri m) | 1.5 | 12 / 12 | 1 / 0 | 0 | 4 | 0.8 | 0.011 / 0.026 | 0 / 0 |
| d. ölçek hatası | 3 % | 12 / 12 | 0 / 0 | 0 | 7 | 1.2 | 0.105 / 0.168 | 0 / 0 |
| d. eğrilme (° / 20 m) | 4 | 12 / 12 | 0 / 0 | 0 | 5 | 0.9 | 0.013 / 0.033 | 0 / 0 |
| e. menzil gürültüsü σ (m) | 0.08 | 12 / 12 | 0 / 0 | 0 | 6 | 1.0 | 0.011 / 0.030 | 0 / 0 |
| e. dönüşsüz yüzey oranı | 75 % | 3 / 12 | 3 / 3 | 4 | 11 | 1.0 | 2.795 / 4.139 | 11 / 0 |
| e. cam kapı oranı | 25 % | 11 / 12 | 0 / 0 | 0 | 5 | 0.9 | 2.045 / 3.222 | 0 / 0 |
|  | 100 % | 6 / 12 | 2 / 3 | 0 | 5 | 0.8 | 2.518 / 6.063 | 0 / 0 |
| e. en uzun menzil (m) | 4 | 7 / 12 | 1 / 2 | 0 | 7 | 1.3 | 2.687 / 9.334 | 0 / 0 |
|  | 2 | 3 / 12 | 4 / 2 | 0 | 16 | 2.9 | 4.909 / 11.357 | 0 / 0 |
| f. odometri ölçek (+) | 10 % | 12 / 12 | 0 / 0 | 0 | 5 | 1.0 | 0.076 / 0.126 | 0 / 0 |
| f. dönüş hatası (+, %14 tabana ek) | 25 % | 12 / 12 | 0 / 0 | 0 | 5 | 0.9 | 0.020 / 0.077 | 0 / 0 |
| f. ani kayma (olay / dk) | 4 | 12 / 12 | 2 / 1 | 0 | 5 | 1.0 | 0.407 / 0.989 | 0 / 0 |
| g. okul günü (hafif / orta / ağır) | hafif | 10 / 12 | 1 / 1 | 0 | 10 | 1.9 | 1.264 / 1.601 | 1 / 1 |
|  | orta | 4 / 12 | 6 / 5 | 0 | 24 | 1.8 | 2.711 / 4.529 | 6 / 0 |
|  | ağır | 0 / 12 | 5 / 4 | 5 | 6 | 0.8 | 6.853 / 11.167 | 36 / 2 |

Kayıp başarısızlıkları (67 / 228 bozuk koşu): yanlış koridor 22, süre doldu 21, doğru koridorda yanlış yerde "bitti" 15,
karar yok 9; 26'sında temas var. Karar süresi tabanda medyan 6 s (koridor_1 / 2 / 4 hemen, koridor_5 / 6 benzer çiftte
uzun: tek koşuda 143 s).

## MuJoCo ile 2B farkı

| Koşul | MuJoCo başarı | 2B başarı (aynı tohum) | Uyuşmayan koşu | MuJoCo / 2B konum hatası ort (m) | MuJoCo / 2B varış hatası medyan (m) | Temas MuJoCo / 2B |
| --- | --- | --- | --- | --- | --- | --- |
| taban | 3 / 3 | 3 / 3 | - | 0.013 / 0.005 | 0.050 / 0.049 | 0 / 0 |
| kapi_2 | 2 / 3 | 2 / 3 | - | 2.713 / 3.304 | 0.050 / 0.047 | 0 / 0 |
| kapi_4 | 1 / 3 | 1 / 3 | - | 5.497 / 5.071 | 9.408 / 6.219 | 0 / 0 |
| esya_2 | 3 / 3 | 3 / 3 | - | 0.029 / 0.025 | 0.048 / 0.053 | 0 / 0 |
| esya_4 | 3 / 3 | 2 / 3 | koridor_3:2 | 0.055 / 0.087 | 0.048 / 0.075 | 0 / 0 |
| insan_2 | 3 / 3 | 3 / 3 | - | 0.020 / 0.014 | 0.047 / 0.047 | 0 / 0 |
| insan_4 | 3 / 3 | 3 / 3 | - | 0.040 / 0.035 | 0.049 / 0.042 | 0 / 0 |
| grup_2 | 3 / 3 | 3 / 3 | - | 0.019 / 0.014 | 0.049 / 0.049 | 0 / 0 |
| grup_4 | 3 / 3 | 3 / 3 | - | 0.019 / 0.013 | 0.047 / 0.050 | 0 / 0 |
| olcek_2 | 3 / 3 | 3 / 3 | - | 0.034 / 0.025 | 0.027 / 0.029 | 0 / 0 |
| olcek_4 | 3 / 3 | 3 / 3 | - | 0.076 / 0.067 | 0.018 / 0.017 | 0 / 0 |
| genislik_2 | 3 / 3 | 3 / 3 | - | 0.026 / 0.023 | 0.054 / 0.050 | 0 / 0 |
| genislik_4 | 3 / 3 | 3 / 3 | - | 0.048 / 0.048 | 0.065 / 0.063 | 0 / 0 |
| egrilme_2 | 3 / 3 | 3 / 3 | - | 0.011 / 0.006 | 0.049 / 0.049 | 0 / 0 |
| egrilme_4 | 3 / 3 | 3 / 3 | - | 0.013 / 0.011 | 0.048 / 0.052 | 0 / 0 |
| gurultu_2 | 3 / 3 | 3 / 3 | - | 0.012 / 0.006 | 0.051 / 0.053 | 0 / 0 |
| gurultu_4 | 3 / 3 | 3 / 3 | - | 0.017 / 0.010 | 0.044 / 0.050 | 0 / 0 |
| donussuz_2 | 3 / 3 | 3 / 3 | - | 0.012 / 0.007 | 0.050 / 0.051 | 0 / 0 |
| donussuz_4 | 3 / 3 | 2 / 3 | koridor_1:2 | 0.027 / 4.012 | 0.024 / 0.057 | 0 / 0 |
| menzil_2 | 3 / 3 | 3 / 3 | - | 0.025 / 0.013 | 0.047 / 0.047 | 0 / 0 |
| menzil_4 | 2 / 3 | 2 / 3 | - | 0.274 / 5.088 | 0.253 / 0.073 | 0 / 0 |
| odo_olcek_2 | 3 / 3 | 3 / 3 | - | 0.037 / 0.046 | 0.075 / 0.078 | 0 / 0 |
| odo_olcek_4 | 3 / 3 | 3 / 3 | - | 0.086 / 0.103 | 0.099 / 0.106 | 0 / 0 |
| odo_donus_2 | 3 / 3 | 3 / 3 | - | 0.013 / 0.005 | 0.048 / 0.050 | 0 / 0 |
| odo_donus_4 | 3 / 3 | 3 / 3 | - | 0.013 / 0.004 | 0.048 / 0.049 | 0 / 0 |
| odo_kayma_2 | 3 / 3 | 3 / 3 | - | 0.019 / 0.038 | 0.050 / 0.049 | 0 / 0 |
| odo_kayma_4 | 3 / 3 | 2 / 3 | koridor_1:2 | 0.050 / 0.054 | 0.051 / 0.214 | 0 / 0 |
| okul_orta | 1 / 3 | 0 / 3 | koridor_3:2 | 3.222 / 6.694 | 8.028 / 16.629 | 0 / 1 |
| okul_agir | 0 / 3 | 0 / 3 | - | 3.097 / 10.345 | 11.831 / 15.560 | 0 / 3 |

- **Sonuç uyuşması 83 / 87.** Uyuşmayan 4 koşunun dördünde de 2B başarısız, MuJoCo başarılı (dönüşsüz %75 koridor_1,
  eşya 4 koridor_3, ani kayma 4 koridor_1, okul orta koridor_3). 2B sonuçta biraz kötümser.
- **Konum hatası 2B'de iyimser:** tabanda ortalama 2B 0,005 m, MuJoCo 0,012–0,015 m (p95 0,020–0,021, en büyük 0,07 m);
  varış hatası ikisinde aynı (0,049 / 0,050 m). Nedeni 2B'nin kinematik robotu (teker / temas dinamiği yok, yay dönüşünde
  hız kaybı yok) ve ideal enkoder dışı hatanın yalnız Gauss olması.
- **Kapı etkeninde birebir aynı:** kapı %25 ve %100'de MuJoCo da aynı koşularda 10–25 m sıçrayıp yanlış yerde durdu.
- **Okul gününde MuJoCo daha iyimser:** MuJoCo'da cam kapı yok (ışın geom'dan geçirilemiyor), TASLAK sonar 30 cm kuralı
  temas öncesi durduruyor (2B'de sonar yok): MuJoCo temas 0, 2B okul orta / ağır 1 / 3.

## İsteğe bağlı varyant: "izleme" (AYRI tohumlar 3, 4; yalnız öneri)

Varsayım (geliştirme tohumlarından): başlangıcı bilinen gezinmede dünya haritadan saptıkça ışın başına uyum düşüyor,
artırılmış MCL (`rastgele_alfa_hizli` < `yavas`) parçacıkların %10'una dek serbest alana saçıyor; periyodik koridorda
saçılan parçacık taramayı "takma" yerde daha iyi açıklıyor ve konum oraya atlıyor. Varyant: `AbBeyni` kurulduktan sonra
`beyin.mcl.ayar.rastgele_en_cok = 0` (yalnız bu deneyin koşucusunda; varsayılan değişmedi).

| Koşul | Varsayılan başarı | izleme başarı | Varsayılan / izleme konum hatası ort (m) | en büyük (m) | Temas varsayılan / izleme |
| --- | --- | --- | --- | --- | --- |
| taban | 12 / 12 | 12 / 12 | 0.006 / 0.006 | 0.07 / 0.07 | 0 / 0 |
| kapi_1 | 11 / 12 | 12 / 12 | 0.211 / 0.006 | 13.45 / 0.07 | 0 / 0 |
| kapi_2 | 10 / 12 | 12 / 12 | 0.517 / 0.008 | 15.05 / 0.18 | 0 / 0 |
| kapi_3 | 8 / 12 | 12 / 12 | 1.485 / 0.028 | 26.51 / 0.64 | 0 / 0 |
| kapi_4 | 8 / 12 | 11 / 12 | 2.070 / 0.066 | 25.06 / 0.61 | 0 / 0 |
| esya_2 | 12 / 12 | 12 / 12 | 0.029 / 0.029 | 0.26 / 0.27 | 0 / 0 |
| esya_4 | 11 / 12 | 12 / 12 | 0.406 / 0.055 | 8.18 / 0.28 | 0 / 0 |
| insan_2 | 12 / 12 | 12 / 12 | 0.009 / 0.009 | 0.07 / 0.07 | 0 / 0 |
| insan_4 | 12 / 12 | 12 / 12 | 0.016 / 0.016 | 0.08 / 0.09 | 0 / 0 |
| donussuz_2 | 12 / 12 | 12 / 12 | 0.007 / 0.007 | 0.07 / 0.07 | 0 / 0 |
| donussuz_4 | 10 / 12 | 12 / 12 | 0.863 / 0.019 | 17.00 / 0.16 | 1 / 0 |
| cam_2 | 10 / 12 | 12 / 12 | 0.612 / 0.014 | 18.95 / 0.33 | 0 / 0 |
| cam_4 | 10 / 12 | 12 / 12 | 1.375 / 0.022 | 19.48 / 0.34 | 0 / 0 |
| okul_hafif | 8 / 12 | 12 / 12 | 1.566 / 0.030 | 21.83 / 0.40 | 0 / 0 |
| okul_orta | 5 / 12 | 12 / 12 | 2.588 / 0.167 | 18.22 / 0.73 | 1 / 0 |
| okul_agir | 1 / 12 | 0 / 12 | 4.906 / 0.976 | 19.66 / 3.29 | 0 / 1 |

- Kapı, cam, eşya, dönüşsüz, hafif ve orta günde sıçrama yok oldu (en büyük konum hatası 25 m -> ≤ 0,73 m), başarı 12 / 12
  (kapı %100'de 11 / 12).
- Ağır günde düzeltmez (0 / 12): sıçrama yerine 0,3–3,3 m kayma ve önünde duvar / grup görüp bekleme (süre doldu).
- Güncellendi (tamamlama turu, yeni tohumlar 5, 6, daha katı hakem: yalnız beyin "vardım" deyince biter): izleme
  okul günü hafif 12 / 12, orta 8 / 12 (burada 12 / 12 idi; 4 sessiz hata), ağır 2 / 12; kapı %25 12 / 12, kapı %50
  12 / 12; v3 aynı koşullarda 11, 5, 1, 10, 8. Taşınmada izleme 1 / 48 (`../../tasinma/sonuc/SONUC.md`).
- Bedeli: gerçek bir "kaçırılma" (robot elle taşındı, büyük kayma) olursa kendini kurtaramaz. Öneri: bilinen başlangıçta
  izleme kipi + ayrı bir kaçırılma algısı (ör. uyum N metre boyunca kötüyse küresel yeniden konumlama ve dur). Kayıp
  robotun karardan sonraki evresine de aynısı uygulanabilir; bu ÖLÇÜLMEDİ.
- Ölçüm modelinde beklenmeyen engel payı (z_rastgele, "isin" modeli) denenmedi: sıçramaların kaynağı engel değil,
  kapı / cam / dönüşsüz yüzey gibi harita yapısındaki farklardı.

## Tamamlama turu (2026-11-26): incelemenin açık bıraktıkları

- **Zarar sırası ve kırılma metni düzeltildi** (yukarıda, "güncellendi" notlarıyla; `analiz.siralama()` artık yalnız tam
  ızgaralı A'dan B'ye ortalamasıyla sıralıyor, `tablolar.md` "Kırılma noktaları" iki sayımı da veriyor). Doğru sıra:
  kapı %73 > cam %77 > menzil %83 > dönüşsüz %92 = ani kayma %92 (eşitlikte en kötü kademe: dönüşsüz %67, ani kayma
  %83) > eşya %94 > grup %98 > geri kalanı %100. Sınırdaki 5 koşu (hedefe 0,30-0,34 m "vardım", tahmin hatası
  0,26-0,29 m) başarı sayılırsa: kapı %77, cam %79, ani kayma %96; cam %50'de kırar, ani kayma hiç kırmaz.
- **Kayıp robotta genişlik sapması (48 koşu, ana ızgarayla aynı tohumlar 0, 1; `kos_ek.py`, `kayip_ek_2b.csv`):**
  ± 2,5 / 5 / 7,5 / 10 cm'de 12 / 12, 12 / 12, 12 / 12, 12 / 12; yanlış koridora karar 0, temas 0, karar süresi
  medyan 5-7 s (taban 6 s); karardan sonraki konum hatası ortalaması 0,016 / 0,026 / 0,038 / 0,052 m (taban 0,008):
  hata duvar kaymasının yaklaşık yarısı kadar büyüyor, sıçrama yok. Genişlik sapması kayıpta da kırmıyor.
- Kip karşılaştırması (v3 / izleme / algi / izleme + algi aynı koşullarda) ve "emin değilim" ölçütü:
  `../../tasinma/sonuc/SONUC.md` "Tamamlama turu".

## Simülasyonun iyimser varsayımları (gerçekte daha kötü olabilir)

- Duvarlar ideal ince levha, ışın sonsuz ince; karışık piksel, çoklu yansıma, geliş açısına bağlı dönüş kaybı yok
  (dönüşsüz yüzey yalnız seçilen 1 m'lik parçalarda, tam NaN). Cam yalnız kapılarda ve tam saydam (yalnız 2B).
- Açılan kapının kanadı koridora açılmıyor (engel değil); açık kapının arkasındaki oda boş, en çok 3 x 3 m.
- Eşya orta hattı kapatmayacak biçimde duvar dibine, kapı önlerine ve köşelere konmadı; gerçekte yolu kapatan eşyada robot
  durup bekler (dolaşma yok) ve başarısız olur.
- İnsanlar bacak çifti silindiri, yürüyenler robota yol verir ve önünde takılırsa geri döner (sürüm 1'de insan da robot
  da bekleyip kilitleniyordu: o sonuçlar silinip yeniden koşuldu); kalabalık sınıf çıkışı, çocuk, robota yaklaşan merak
  yok. Grup 30 s'de dağılır.
- 2B robot kinematik (dönme merkezi arka dingil, w kazancı 0,89 VARSAYIM); sonar kuralı yok. Odometri tabanı: dönüş %14
  fazla (MuJoCo ölçüsü), öteleme %0 + Gauss; ani kayma yalnız eklenen olaylar.
- Haritanın kendisi tabanda kusursuz (sahneden üretilmiş); gerçek SLAM haritasının yerel hataları yok. Geometri etkenleri
  yalnız düzgün bozulmalar (ölçek, tek duvar kayması, sabit eğrilik).
- Tek kat, düz zemin; LiDAR düzlemi eğimi, titreşim, tur hızı oynaması, gecikme yok.
- Robot ONERI (VARSAYIM): bugünkü robot (V0) modelde dönemiyor.

## Kapsamın daraltıldığı yerler

- **Kayıp robot 20 koşulda** (60 değil): taban; okul hafif / orta / ağır; kapı %25 ve %100; cam %25 ve %100; menzil 4 m ve
  2 m; eşya, dönüşsüz, ani kayma, insan, grup, eğrilme, ölçek, dönüş hatası, odometri ölçek, gürültünün yalnız 4.
  kademesi. Genişlik sapması kayıpta hiç koşulmadı (güncellendi: tamamlama turunda 4 kademe x 12 = 48 koşu eklendi,
  aşağıda); 1. ve 3. kademeler (kapı, cam, menzil dışında) yok. Neden: kayıp
  koşusu A'dan B'ye koşusunun 5–15 katı (6 harita, 3000 parçacık, 300 s'ye dek) ve süre bütçesi.
- **MuJoCo yalnız A'dan B'ye**, koşul başına 3 koşu; cam kapı etkeni MuJoCo'da yok.
- Koşul başına 12 koşu (6 koridor x 2 tohum): kırılma kademesi istatistiksel olarak ± 1 kademe.
- Her koridorun haritası kendi ölçüsünde; koridor_5 / 6 benzer çifti dahil 6 harita.

## Dosyalar

`ab_2b.csv`, `kayip_2b.csv`, `kayip_ek_2b.csv` (tamamlama turu), `mujoco.csv`, `varyant_2b.csv` (koşu başına bir satır: kimlik, koşul, koridor, tohum, sonuç,
neden, hatalar, temas), `ozet.json` (koşul özetleri, kırılma, sıralama, MuJoCo eşleşmesi), `tablolar.md` (bu tabloların
kaynağı), `../gorsel/basari_kademe.png` (başarı / kademe), `../gorsel/mujoco_2b.png` (aynı koşu 2B / MuJoCo),
`../gorsel/dunya_koridor_4.png`, `../gorsel/dunya_koridor_5.png` (harita / dünya). Ham koşular `ham/` (depo dışı).
