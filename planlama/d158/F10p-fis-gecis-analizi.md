# F10p · Boyun tüneli fiş geçiş analizi (P10.7b2h-ön)

17.11.2026 sabahı. **Yalnız analiz:** tasarım, rehber, maliyet ve karar kuyruğu değişmedi. FreeCAD açılmadı. Betik:
`planlama/d158/F10p-fis-gecis.py` (depo kökünden çalışır). Amaç: sipariş kesinleşmeden önce uyarı. **Asıl cevabı deneme parçasıyla
yapılacak fiziksel deneme verecek.**

## 1. Soru

Boyundan geçen fişli üç kablo (U03 hub uzatmasının USB-A erkek ucu, H02 göğüs HDMI'sinin micro HDMI ucu, S10 tilt servo uzatmasının
3 pinli ucu) alt çıkıştan girip kanal → basamak → kablo odası → mil penceresi → Ø32 mil içi yolunu fişi takılı hâlde izleyebilir mi?

## 2. Yöntem

- **Geometri:** `tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl` (md5 `fae01178…`). Kablo yolu gerçek tünelle aynı (F10o-kontrol, 25 ölçüm
  ≤ 0,02 mm). STL 0,25 mm vokselle katı / boş ayrıldı; boş alan yalnız gerçek kablo yolu bölgesinde (`boyun_tunel_deneme.py:93-95` YOL)
  sayıldı. Parçanın kesim sınırında açık kalan yerler (oda yanları x ±20, mil ucu y 96) açık sayılmadı. Doğrulama: kanal z −27 … −19,25,
  basamak y 45 z −23 … −12,5, y 48,5 z −27,5 … −20, oda / pencere y 56–58 z −27,5 … 16: `boyun-tunel-deneme.json` ile ≤ 0,25 mm uyumlu.
- **Fiş modeli:** katı dikdörtgen prizma (genişlik w × kalınlık t × rijit boy L). Genişlik x yönünde (kanal 20 mm geniş), kalınlık ve boy
  dönüş düzleminde (y–z). Arama 4 boyutlu: fişin x konumu (1 mm adım), y, z (0,5 mm) ve eğim (2°). Her konum ve eğim için boş alan fiş
  dikdörtgeniyle aşındırıldı (konfigürasyon uzayı), sonra alt çıkışın arkasındaki yatay başlangıçtan mil içine (fişin tamamı y > 64,
  pencerenin üstü) erişim arandı.
- **Birikme (kaba):** pan servo kablosu (yassı ≈ 3,6 × 1,4 mm) kanal / alt çıkış tabanında, yarık hizasında (x −3 … 0,6). Önce geçmiş
  kablolar (U03 Ø 4,5; H02 Ø 6) +x duvarına yaslı katı şerit: H02 için 4,5 mm, S10 için 10,5 mm.
- **Analitik çapraz kontrol:** "köşeden merdiven" formülü (L_max = min_φ [a / sin φ + b / cos φ − t / (sin φ cos φ)]) ve basamaktaki
  kademe için t_max ≈ √(1,9² + örtüşme²).

## 3. Fiş ölçüleri (hepsi VARSAYIM)

Depoda ve sipariş satırlarında fiş ölçüsü yok (`kablo_yolu_ekran.py:5`; `maliyet.json` MJ:137, MJ:191 yalnız şart yazıyor). Değerler
standart konnektör ölçüleri ve yaygın kalıplı kablolardan tahmin; **ölçülmedi**.

| Kablo | Durum | w × t × L (mm) | Dayanak |
| --- | --- | --- | --- |
| U03 USB-A erkek | metal kabuk, kalıpsız (alt sınır) | 12 × 4,5 × 14 | USB-A kabuk standart ≈ 12 × 4,5 |
| | ince kalıp | 12,5 × 5,5 × 25 | ince kablolu ürünler (tahmin) |
| | depo şartının üstü | 13 × 7 × 30 | MJ:137 şartı "≤ 13 × 7" (boy şartı yok) |
| | tipik kalıp | 16 × 8 × 35 | yaygın uzatma kabloları (tahmin) |
| H02 micro HDMI | metal uç, kalıpsız (alt sınır) | 6,4 × 2,8 × 8 | Type D uç standart ≈ 6,4 × 2,8 |
| | ince kalıp | 10 × 4,5 × 18 | tahmin |
| | tipik kalıp | 11,5 × 6 × 24 | tahmin |
| | depo şartının üstü | 18 × 7 × 30 | MJ:191 şartı "≤ 7 kalın, ≤ 18 geniş, ≲ 30 boy" |
| S10 3 pinli servo ucu | Dupont 2,54 | 7,6 × 2,6 × 14 | tahmin |
| | JR / Futaba | 8 × 3,6 × 15 | tahmin |
| | üst | 8,5 × 4,5 × 17 | tahmin |

## 4. Sonuç

İki darboğaz çıktı (ikisi de gerçek tünelde, parça sınırı değil):

- **A · Alt çıkış dik dönüşü (boy sınırı):** delik 12 mm yalnız ortada (x −8 … 0); 12 mm genişliğindeki bir fiş için etkin yükseklik
  ≈ 10 mm, arka duvar 3 mm, kanal 7,75 mm derin. Kalın ve uzun fiş dönemez. Pan servo kablosu tabanda olunca ≈ 1,4 mm daha daralır.
- **B · Basamak → kablo odası (kalınlık sınırı):** y 40…46'da arka duvar z −23'e çıkıyor, y 47,9'dan sonra mil alt diski önde z −20'ye
  iniyor; aradaki 1,9 mm'lik katmanda örtüşme pencere hizasındaki x'lerde (x ≈ −2 … 2) yalnız ≈ 3 mm. Bu katmanı ≈ 3,5 mm'den kalın katı
  bir fiş, boyu ne olursa olsun geçemiyor (F10o-kontrol N1'in kaba 2B bulgusunu doğruluyor, sınırı daha da sıkı buluyor).

| Kablo / fiş | Sonuç | En dar yerdeki pay | Takıldığı yer |
| --- | --- | --- | --- |
| **U03** USB-A erkek (her varyant, standart metal kabuk 12 × 4,5 × 14 dahil) | **GEÇMEZ** | kalınlık ≈ −1 … −1,5 mm (B); kalıplıda boy ≈ −10 mm (A) | kalıplı: A. Yalnız metal kabuk: pan kablosu yokken A'yı geçiyor, B'de takılıyor (fiş ucu en çok y ≈ 44); pan kablosu varken A'da |
| **H02** micro HDMI, kalıplı (4,5–7 mm kalın) | **GEÇMEZ** | kalınlık −1 … −3,5 mm (B); ince kalıp 10 × 4,5 × 18'de boy ≈ −2 mm (A) | A (birikmeli ve birikmesiz aynı) |
| H02 yalnız metal uç (6,4 × 2,8 × 8, kalıpsız) | GEÇER | ≈ +0,2 … +0,7 mm (B) | — (U03 kablosu ve pan kablosu tüneldeyken de) |
| **S10** JR 3 pin (8 × 3,6 × 15) | **SINIRDA** (modelde geçmez) | ≈ −0,1 … −0,6 mm (B), çözünürlük ±0,5 | birikmesiz B; U03 + H02 kabloları yanında A |
| S10 Dupont 3 pin (7,6 × 2,6 × 14) | GEÇER (birikmeye bağlı) | ≈ +0,4 … +0,9 mm (B) | boş tünelde ve U03 + pan kablosu yanında geçiyor; 10,5 mm'lik katı şeritle (U03 + H02) oda → pencere geçişinde takılıyor: şerit modeli kötümser |

Birikme: U03, H02 ve S10 JR için sonuç birikmesiz de aynı (GEÇMEZ / sınırda); birikme yalnız takılma yerini A'ya taşıyor. Birikmenin
sonucu değiştirdiği tek fiş S10 Dupont. Koşulan tüm durumlar betikte (`isler` listesi); ham çıktı depoya yazılmadı, betik yeniden üretir
(3 süreç paralel ≈ 10 dk, süreç başı ≈ 0,5 GB bellek). Not: H02 birikmeli koşuları pencere şeridi düzeltilmeden (şerit x 1,5…6 yerine
5,5…10) koşuldu; H02 kalıplı A'da takıldığı için sonucu etkilemez. S10 birikmeli koşular düzeltilmiş şeritle tekrarlandı, sonuç aynı.

## 5. Duyarlılık ve en büyük fiş

Pan servo kablosu tabanda, başka kablo yokken (boş tünel) koşulan sınır denemeleri:

| w × t × L (mm) | Sonuç | Takıldığı yer |
| --- | --- | --- |
| 8 × 3 × 15 | geçer | — |
| 8 × 4 × 15 | geçmez | B |
| 8 × 5 × 15 | geçmez | A |
| 13 × 3 × 15 | geçmez | oda → mil penceresi (13 mm genişlik pencere ve kanal x aralıklarına birlikte sığmıyor) |
| 13 × 3,5 × 15 | geçmez | B |
| 13 × 4 × 15 | geçmez | A |
| 13 × 3 × 30 | geçmez | A |
| 6 × 3,5 × 20 | geçmez | A |

**Bu tünelden geçebilen en büyük katı fiş (model):** kabaca **≤ 8 mm geniş, ≤ 3 mm kalın (3–3,5 arası belirsiz), ≤ 15 mm rijit boy**.
Analitik çapraz kontrol aynı yerde: A için etkin delik ≈ 10 mm, kanal 7,75 mm ile L_max ≈ 17,8 (t 3,6), 16,0 (t 4,5), 10,8 mm (t 7);
B için t_max ≈ √(1,9² + 3,0²) ≈ 3,5 mm.

**Duyarlılık:** U03 sonucu fiş varsayımına **bağlı değil**: USB-A'nın standart metal kabuğu (12 × 4,5) tek başına B'yi geçemiyor, kalıp
yalnız işi kötüleştiriyor. H02'de sonuç **tamamen kalıba bağlı**: kalıpsız uç geçiyor, ≥ 3,5 mm kalınlıkta herhangi bir kalıp geçmiyor
(piyasadaki kalıplı micro HDMI fişleri genelde 5–8 mm). S10 sınırda: 0,5 mm'lik ölçü farkı sonucu değiştirir; gerçek ölçü ve yuvanın
esnekliği belirleyecek.

## 6. Seçenekler (tasarım değiştirilmedi; yalnız seçenek)

| Seçenek | Hangi kablo | Ne gerekir | Siparişe etkisi |
| --- | --- | --- | --- |
| **Fişsiz geçirip ucu sonra takmak** | U03 (4 damar), S10 (3 damar) | U03: kablo geçtikten sonra kesilip lehimli / sıkmalı USB-A erkek fiş takılır (`kablolama-on-kararlar.md` §4 3a: D+ / D− bükümü ≤ 1 cm açılır). S10: JR / Dupont yuvası geçirmeden sonra sıkılır. | MJ:137 kablosu kalır (kesilecek) ya da fişsiz kablo; **eklenir:** USB-A erkek lehim fişi, 3 pinli JR yuvası + pin, gerekirse sıkma pensesi. Fiyat bilinmiyor. |
| | H02 | 19 damarlı HDMI'yi elde sonlandırmak pratik değil. | Önerilmez. |
| **Şerit (FPC) HDMI + takılır uç adaptörleri** | H02 | Şerit düz geçer (kalınlık < 1 mm), micro HDMI ve HDMI A uçları geçirdikten sonra takılır. Kafa ekranında aynı düzen var. 1 m dolayında şeritle 1080p KT4 masa denemesiyle doğrulanmalı. | MJ:191 (micro HDMI → HDMI 1,5 m, 117,59 TL, stokta yok) yerine: DIY şerit (≈ 1 m; **fiyat bilinmiyor**, listedeki 30 cm'lik 105,51 TL) + micro HDMI uç (247,61 TL) + HDMI uç (247,61 TL), Robotistan, `maliyet.json` satır 72, 195, 196 fiyatlarıyla. |
| **Daha ince / açılı fiş** | H02, S10 | Modelde yalnız kalıpsız metal uç ölçüsündeki fiş (≈ 6,4 × 2,8 × 8) geçiyor. Kalıplı ürünlerde ≤ 3,5 mm kalınlık ve ≤ ~15 mm rijit boy bulmak zor; 90° fiş rijit boyu artırır, işe yaramaz. | Ürün sayfalarında fiş ölçüsü yok (MJ:137, MJ:191); ölçü görmeden bu yola güvenilmez. |
| **Tüneli genişletmek** (yalnız ön değerlendirme) | hepsi | (1) **Alt çıkış:** delik üstü kemerli (12 mm yalnız x −8 … 0'da; kenarlarda 12,5 → 14 → 16), duvar 3 mm, kanal 7,75 mm derin. Deliği yukarı 6–8 mm uzatmak ya da üst iç kenarına 45° pah açmak rijit boy sınırını kabaca 5–8 mm artırır. Parça: servo yuvası arka duvarı; arkadaki komşu (boyun plakası / gövde, N3) bilinmiyor. (2) **Basamak:** y 40…46'da arka duvar z −23'e çıkıyor, mil alt diski (r 20) önde z −20'ye kadar iniyor; örtüşme yalnız ≈ 3 mm. Servo yuvasının bu bölgede arka duvarını z −27'ye indirmek (≈ 4 mm, x −14…6) örtüşmeyi ≈ 7 mm'ye çıkarır. Mil diskine oyuk önerilmez (pan ile döner). | CAD değişikliği; P10.7 dışı ayrı karar. Deneme parçası yeniden kesilip basılır. Sipariş kalemi değişmez. |

## 7. Modelin sınırları

- **Yuvarlanma yok:** fiş yalnız y–z düzleminde eğiliyor, x yönünde kayıyor; x–y düzleminde yan yatma (roll) ve dikey eksende dönme
  (yaw) aranmadı. Basamakta fişin bir ucunu x −14 tarafına (örtüşme 8,7 mm) yatırmak ya da odada yana kaydırmak gerçekte biraz daha
  fazla yol açabilir: model bu yönde **temkinli**.
- **Fiş katı kutu:** gerçek fişin köşeleri yuvarlak, kalıp gövdesi kademeli (metal kabuk ince, kalıp kalın); kablonun arkadan çekmesi,
  esnemesi, eğilme yarıçapı yok. Kablonun kendisi (U03 Ø ≈ 4,5, H02 Ø ≤ 6) fiş geçtikten sonra aynı dönüşlerden geçer; hesaba katılmadı.
- **Birikme kaba:** önceki kablolar sabit, katı şerit sayıldı; gerçekte itilip yer açarlar (S10 için özellikle **kötümser**). Pan servo
  kablosunun yeri tahmin.
- **Alt çıkışın arkası** (z < −30, y < 22) boş sayıldı (komşu parça bilinmiyor, F10o-kontrol N3). Arkada gövde / plaka varsa giriş daha
  da zorlaşır.
- **Çözünürlük:** voksel 0,25 mm, arama ızgarası 0,5 mm / 2°: sonuçlar ≈ ±0,5 mm belirsiz; sınırdaki değerler "SINIRDA" sayılmalı.
- Fiş ölçüleri varsayım (§3). Teslimde kumpasla ölçülüp betikteki tabloya yazılırsa yeniden koşulabilir.
