# F10l kare incelemesi: P10.7b2d (78d160d) bağımsız bakış

Tarih: 2026-11-16. İnceleyen: bağımsız ajan (salt okunur). Bakış açısı: robotu ilk kez kuracak bir öğrenci.
Yöntem: Kareleri `rehber/goruntu/*.png` (1200 × 720; `yazdir.html` de bu dosyaları kullanıyor) Read aracıyla görsel olarak
açtım. Kart metnini `rehber/veri/rehber-veri.json` içindeki `sira_grup[].is_` alanından, karede vurgulanan parçaları `ref` / `sema`
alanlarından okudum. Basılı hâl için `planlama/rehber/Lale-montaj-rehberi.pdf` sayfa 21, 42 ve 46'yı PyMuPDF ile 90 dpi'da
çizdirip baktım ve metnini çıkardım. Tarayıcı açmadım. Hükümler § 1–3'te; üretim ajanının tablosunu (`F10l-gunluk.md` § 10.6)
bunları yazdıktan sonra okudum, karşılaştırma § 4'te.

Hüküm ölçeği. **Açık**: Kartın istediği iş kareden ve metinden yapılabiliyor. **Zor**: Yol ya da yer görünüyor, ama uçlar, konektör
ya da taraf ancak metinle, tahminle veya ekranda döndürerek bulunuyor. **Anlaşılmıyor**: Kare kartın işini göstermiyor ya da
metinle çelişiyor.

## 1. Kare başına hüküm

| Kare | Hüküm | Neden (tek satır) |
| --- | --- | --- |
| 17.1 Toprak ve iki bara | anlaşılmıyor | Karede yalnız ≈ 60 px'lik siyah bir G05 parçası ve kimliği yazmayan saydam sarı bir "V" var. Metnin anlattığı 5 saplamalı yıldız barası, 4 saplamalı anahtarlı bara, 7 köprü ve saplama numaraları modelde yok, karede de yok. |
| 17.2 Ana hat ve şarj kolu | zor | Kırmızı ana hat görünüyor, ama akü, XT60, 30 A yuvası ve sigorta kutusu etiketsiz. Ana anahtar henüz modelde olmadığı için yol havada bitiyor. Şarj kolu G06 hiç çizilmemiş. |
| 17.3 Akü ölçüm teli (G07) | zor | Mor tel kattan direğin arkasına gidiyor, ama iki ucu (bölücü pedi, ana anahtar çıkışı) görünmüyor. Direnç ve pabuç ayrıntısı yalnız metinde. |
| 17.4 Röle K1 ve ön şarj kartı | anlaşılmıyor | Uzak kadrajda turuncu Kablo yolu 3 parçalı görünüyor. Röle K1 ve ön şarj kartı kartlar arasında seçilemiyor. Metnin kendisi, karedeki çizginin bir kısmının başka alt adıma (17.5, G12) ait olduğunu söylüyor. |
| 17.5 Bara çıkışları | anlaşılmıyor | Kadraj bütün tabana açılıyor ve vurgulu turuncu birkaç küçük parça hâlinde. Metnin bağlattığı G14, G15 (XL4016 A / B) bu karede yok: bu kabloların parçası (Kablo yolu 5 / 7) K2'ye (32.1) atanmış. |
| 17.6 PC817 #2 algı teli (G22) | zor | Turuncu G22 net, ama iki ucu (IN2 ± klemensi, yıldız 5 numaralı saplama) karede yok. Çift damarlı kablo tek boru olarak çizilmiş. Siyah ara parça ve kırmızı pabuç da yok. |
| 17.7 Sigorta kutusu çıkışları | zor | Kırmızı G18 görünüyor. Vurgulu parça Kablo yolu 9'un "XL4016 sonrası kısmı eski" diye işaretli bölümünü de taşıyor; bu uyarı kart metninde ve kare lejantında yok. G17, G20 ve A01 bu karede çizilmemiş. |
| 17.8 Acil stop ve röle sürücüleri | zor | Yeşil yol iyi vurgulu ve kartlar arasındaki gidişi okunuyor. Mantar (F1'de takılıyor), düğüm kartı, 86 / 85 kuyrukları ve BC337 yeri seçilemiyor. |
| 17.9 Alt kat kartlarının öbür uçları | zor | Mavi G19 kısa ve net: alt kattan kesikten geçip arayüz kartına çıkıyor. Metnin bağlattığı SV1 / SV2 karede yok (K2'ye atanmış). |
| 17.10 Enkoder, BTS sinyal, sonar | zor | Mor demet görünüyor ve sonarlardan çıkış okunuyor. On tel aynı renkte ve etiketsiz, hangisinin N01, N02, B02, Q01–Q03 olduğu ayrılmıyor. Metindeki B01 bu karede yok (Kablo yolu 12, K2'ye atanmış). |
| 17.11 Direğe çıkan hatların taban kısmı | anlaşılmıyor | Kare 17.12 ile piksel piksel aynı, yalnız başlık farklı (fark kutusu 45,10–352,34). Bütün robot görünüyor ve vurgu yok. P03 çizilmiyor, U06'nın taban ucu da gösterilmiyor. |
| 17.12 Son kontrol: K1'de enerji verilmez | açık | Genel bakış bu kartın amacına uyuyor. Köprüleri gösterebilirdi, ama bu kartın asıl işi kontrol listesi. |
| 32.1 Kol servo uzatmaları | zor | Bütün robot kadrajda. Sarı uzatmalar yalnız tabanda seçiliyor. Direk arka yüzündeki yol (z −26) sağ-önden bakışta direğin arkasında kalıyor. Çıkış numaraları karede yok. |
| 32.2 Kafa servoları, hat C | anlaşılmıyor | Boyun servosunun yakın çekimi, hiç kablo görünmüyor. Kablo yolu 6 (d 58,9) ya gömülü ya kadraj dışında. Lejant "Servo gücü 6 V (sarı)" diyor, ama karede sarı yok. |
| 32.3 Kafa 12 V | açık | Kırmızı G17 direk ön yüzünden boyuna net çıkıyor. Kafa giriş kartı ucu E3a'da bilindiği için bu yeterli. |
| 32.4 ESP32 USB | anlaşılmıyor (çelişki) | Vurgulu mor çizgi Kablo yolu 12 (B01, p1191). Bu çizgi direkten boyuna kadar çıkıyor, oysa kart "U06 boyuna girmez" diyor. Gerçek U06 (gri, şema 2) neredeyse görünmüyor ve taban ucu yanlış yerde (K2 kablo listesi de bunu söylüyor). |
| 32.5 Boyun demeti: tünelden geçirme | zor | HDMI, hoparlör ve hub uzatmasının boyun üstü uçları seçiliyor. Kartın asıl konusu olan servo yuvası arka kanalı (tünel, 20 × 7,8 mm) ve geçiş sırası görünmüyor. S10 ve G17 bu karede vurgulu değil. Lejant "Analog ses (beyaz)" diyor, kare koyu camgöbeği gösteriyor. |
| 32.6 Kafa uçları, hoparlör, gövdeye inenler | anlaşılmıyor | Genel bakış ve vurgu yok. Kafa içi (PAM8403 L+ / L−) ve gövdeye inen üç yol görünmüyor. |
| 32.7 Göğüs ekranı 12 V | zor | Üst ucu (direğin solu, ekran arkası) görünüyor. Direk arka yüzündeki iniş ve güç panelindeki regülatör ucu (modelde yok) seçilemiyor. |
| 32.8 Son kontrol: direğe tuttur | açık | Genel bakış yeterli. "S1 uçları travers arkasında" ise karede seçilmiyor. |
| E4 4. alt adım (31.4) Sol arka kabuk → kafa | zor | Kabuğun yerine konması açık: yeni parça gerçek renkte, bağlandığı yer pembe, taraf koordinatla tutarlı. Kartın ilk yarısı olan kablolama ise görünmüyor: ses kablosu ve K05 kabuğun arkasında. Lejant "Karede: 5 V (mavi)" diyor, ama mavi kablo karede yok. Karenin içine gömülü "(görünümü döndür)" yazısı kâğıtta işe yaramıyor. |
| F1 kontrol adımı (ana kare `adim-33.png` + kontrol listesi "İlk enerji, aşama 1") | anlaşılmıyor | Kare bitmiş eteği ve bağlantı elemanı halkalarını gösteriyor. Ölçü noktalarının hiçbiri görünmüyor: PC817 #1 giriş klemensi, yıldız barası 3 numaralı saplama, bölücü orta noktası, sigorta kutusu F4 / F5, akü XT60. Etek takılıyken bunların yeri kareden çıkarılamıyor. |
| B6a (adim-14.png) Tezgâh: elektronik katı | zor | Kartların yeri ve burç / vida halkaları net. Altı kartın hangisinin hangisi olduğu yazmıyor (üçü aynı mavi). "Servo dağıtım çıkışları direğe bakar" ve "BNO055 X oku öne" yön işareti karede yok. X01 / I01 / I02 / P01 / P02 tablo olduğu için çizilmemesi kabul edilebilir. |

**Dağılım (22 kare):** açık 3 (17.12, 32.3, 32.8), zor 12 (17.2, 17.3, 17.6, 17.7, 17.8, 17.9, 17.10, 32.1, 32.5, 32.7,
31.4, B6a), anlaşılmıyor 7 (17.1, 17.4, 17.5, 17.11, 32.2, 32.4, 32.6) + F1 kontrolü = **anlaşılmıyor 8**. Toplam 23 hüküm: K1 12,
K2 8, E4 1, F1 1, B6a 1.

### 1.1 Ekran ile basılı arasındaki farklar

- Basılıda alt adım karesi sayfa genişliğinin yaklaşık üçte biri (PDF s. 46). Bütün robotu gösteren karelerde (17.11, 17.12, 32.1,
  32.3, 32.4, 32.6, 32.8) ince kablolar kâğıtta seçilmiyor. Ekranda yakınlaştırılabiliyor, kâğıtta bu imkân yok. 32.3 ekranda açık,
  basılıda sınırda.
- Karenin içine gömülü başlık, lejant ve "Robotun neresi" kutusu basılıda okunmayacak kadar küçük. Basılı sayfa bunları kare altına
  "Karede: …" diye metin olarak yeniden yazıyor, yani bilgi kaybolmuyor.
- 31.4: Kare içindeki "(görünümü döndür)" yazısı (`rehber/app.js:1302`) basılı karede de var, ama kâğıtta döndürülemiyor. Basılı
  lejant "Karede: Kablo: 5 V (mavi)" diyor, oysa mavi K05 karede görünmüyor (PDF s. 42).
- Basılı sayfada alt adım lejantı yalnız sınıf adını yazıyor ("Kablo: Sinyal (mor)"). "Kablo yolu 12 … direkten kafaya çıkan kısmı
  eski" uyarısı ise K2'nin ana sayfasındaki "Kablo kancası" listesinde, 32.4 karesinden sayfalarca uzakta. 17.7'deki Kablo yolu 9
  için de durum aynı: uyarı PDF s. 21'deki K1 listesinde. Ekranda tıklayınca ad görünüyor (app davranışı, tarayıcıda denemedim).

## 2. "Zor" ve "anlaşılmıyor" kareler için düzeltme önerileri

Yeniden üretim türleri koddan çıkarıldı:
- **FreeCAD'siz**: `rehber_uret.py --veri-yok`. `rehber_gorunum.alan_isle` (rehber_gorunum.py:146) DEMET_ALT / sira gruplarının
  `kamera`, `is_`, `saydam`, `sema_ortulu`, `gizli_ok` alanlarını FreeCAD'siz veriye yazıyor. `app.js` değişiklikleri için de yalnız
  tarayıcı yeterli.
- **FreeCAD'li**: Hangi Kablo yolu parçasının hangi alt adımda görüneceği (`desen` → `ref`, rehber_veri.py:872–878) ve şema ataması
  (`sema` → `_sema`, rehber_veri.py:851) yalnız freecadcmd yolunda çözülüyor. Alt adım sayısı değişirse alan_isle durup "FreeCAD'li tam
  üretim gerekir" diyor (rehber_gorunum.py:179). Yeni geometri (bara saplamaları, etiket işaretleri) CAD işi.

Bu sınıflandırmayı kod okuyarak yaptım, çalıştırarak doğrulamadım.

| Kare | Öneri | Kaynak | Yeniden üretim |
| --- | --- | --- | --- |
| 32.4 | (a) Kablo yolu 12'yi (p1191) bu alt adımdan çıkar. Bu B01'in yolu, 17.10'a ait; `desen=("Kablo yolu 12:",)` ve `sema_ok` girdisini 32.4'ten 17.10'a taşı. (b) U06 şeması (şema 2) için `kamera` arka (`"arka"` ya da `(0.4, 0.5, -1.2)`) olsun ki direk arka yüzündeki yol görünsün. (c) U06'nın taban ucunu yeniden çiz (K2 kablo listesi zaten "yeniden çizilecek" diyor). | rehber_metin.py:2041–2043 (DEMET_ALT K2[3]), 2031–2032 (K1[9]). Şema: `lale158/kablo_yolu_*.py` (U06) | (a) ve (c) FreeCAD'li. (b) tek başına FreeCAD'siz. |
| 17.5 / 17.9 | G14 / G15 / SV1 / SV2 bu alt adımlarda bağlanıyor, ama çizgileri K2'deki Kablo yolu 5 / 7'de. İki yol var. Ya Kablo yolu 5 / 7'yi tabandaki (G14, SV1) ve direkteki (S01–S08) kısımlara böl, ya da en azından 17.5 / 17.9 metnine "G14 / G15 (SV1 / SV2) çizgisi 32.1 karesinde" cümlesi ekle. Kamerayı bara ve XL4016'ya yaklaştır: 17.5 için `kamera=(0.6, 0.9, 0.5)` ve `saydam=("Elektronik katı",)` ile kat altı. | rehber_metin.py:2023–2025, 2030, 2038 | Bölme FreeCAD'li (parça geometrisi ya da desen). Metin + kamera FreeCAD'siz. |
| 17.1 | Bara modelde yok. En ucuzu: karenin ve metnin baraların yerini anması ("anahtarlı bara: röle yanında, yaklaşık; yıldız barası: güç panelinde …") ve 1–5 / 1–4 numaralı saplamaları gösteren bir **bağlantı tablosu ya da çizim** (K1 `kablo` listesindeki P03 gibi). Sarı saydam "V"nin ne olduğu karede ya da lejantta yazmalı; kimliğini ben de çözemedim, muhtemelen Kablo yolu 5 / 7'nin bara başlangıcı. Kalıcı çözüm: iki baraya gösterim parçası (saplamalı Referans). | rehber_metin.py:2018–2019 (K1[0]), metin ADIM["K1"] (≈ s. 320) | Metin / tablo FreeCAD'siz. Bara gösterim parçası FreeCAD'li. |
| 17.4 | Kamerayı güç paneline yaklaştır ve röleyle ön şarj kartını kadrajın ortasına al, örneğin `kamera=(0.5, 0.8, -0.6)` (sağ-arka-üst). Ön şarj kartının (p1058) "Bağlandığı yer" pembesiyle vurgulanması iyi olur. Metin "karede G12 de görünür" diyor, bu doğru ve kalmalı. | rehber_metin.py:2022 | Kamera FreeCAD'siz. Pembe vurgu için `ev` alanı gerekiyorsa kontrol edilmeli. |
| 17.11 | P03 tablo, U06'nın taban ucu ise yanlış çizili. Kareyi ESP32 taşıyıcısına ve PCA9685'e yaklaştır (`kamera=(0.3, 1.0, 0.4)` üstten). Kare 17.12'nin kopyası olarak kalmasın. | rehber_metin.py:2033–2034 | FreeCAD'siz. |
| 32.2 | Kablo yolu 6 kısa (58,9 mm), direk üstündeki R62 halkasında. Kamerayı arkadan (`"arka"`) ve daha uzaktan al ya da boyun / servo yuvasını `saydam` yap. Dağıtım kartı C modelde olmadığı için metin "çıkışa tak" kısmının karede görünmeyeceğini söylemeli. Günlükte zaten açık madde. | rehber_metin.py:2039 | FreeCAD'siz. |
| 32.6 | Kamerayı kafa arkasına al, arka kabuklar ve boyun saydam, AU3 / U03 / H02 / G17 şemaları vurgulu: `kamera="arka"`, `saydam=("Arka kafa kabuğu",)`, `sema=("(AU3)", "(U03,", "(H02)")`. | rehber_metin.py:2045 | `kamera` ve `saydam` FreeCAD'siz. `sema` eklemek FreeCAD'li. |
| 31.4 (E4.4) | Kartı ikiye ayırmak en temizi: (i) kablolar, önden ve yüz kabuğu yokken, `kamera=(-0.85, 0.62, 1.25)`; (ii) kabuk yerine. Ayırmadan yapılacaksa: `kamera` önden-sol (yüz kabuğu bu alt adımda henüz yok, ön açık), `sema_ortulu`'ya K05'i ekle ya da lejant "Karede" demesin, `app.js:1302` basılı karede "(görünümü döndür)" yazmasın. | rehber_metin.py:808–812, rehber/app.js:1302 | Kamera ve `sema_ortulu` FreeCAD'siz. Alt adımı bölmek FreeCAD'li (grup sayısı değişir). |
| F1 kontrolü | Aşama 1 ölçümü için ayrı bir alt adım ya da kare: etek saydam (`saydam=("Etek",)`), kamera üstten, yıldız barası, arayüz kartı ve sigorta kutusu görünür. Daha ucuz yol: kontrol maddelerine "ölçü noktalarının yeri: 17.6 (IN± klemensi), 17.1 (yıldız 3)" göndermesi. Ancak bu karelerde de noktalar görünmüyor, yani gönderme tek başına yetmez. | rehber_metin.py ADIM["F1"] (s. 943 civarı, `kontrol`), `sira` sonu | Yeni alt adım FreeCAD'li. Gönderme FreeCAD'siz. |
| 17.7 | Kart metnine şu cümle eklenmeli: "Karedeki kırmızı çizginin XL4016 çevreden ESP32'ye giden kısmı eski; G19'un yolu 17.9'da". Bu kartta G17 / G20 / A01'in çizgisi yok, bunu da söylemeli. | rehber_metin.py:2027–2028, ADIM["K1"] `is_` paragraf 7 | FreeCAD'siz. |
| 17.2, 17.3, 17.6 | Ortak sorun: uçlar modelde yok ya da seçilmiyor. Uç bileşenlerine kısa etiket konmalı (XT60, 30 A yuvası, sigorta kutusu, arayüz kartı). Bu bir `app.js` özelliği olur (alt adımda `etiket` alanı, adı parçadan). Gelene kadar metinde "karede sağdaki kutu sigorta kutusu" gibi yer tarifi verilebilir. | app.js (yeni alan), rehber_metin.py:2020–2026 | Etiket özelliği FreeCAD'siz (app.js + gorunum alanı), ama yeni kod ister. |
| 17.10 | Teller aynı renkte. Alt adımı ikiye böl (enkoder + BTS / sonar) ya da her şemanın ucuna kimlik etiketi koy. B01'in (17.10'da bağlanan) çizgisi 32.4'te kalıyor, yukarıdaki 32.4 maddesiyle birlikte taşınmalı. | rehber_metin.py:2031–2032 | Bölme FreeCAD'li. Etiket FreeCAD'siz (yeni app.js özelliği). |
| 32.1, 32.7 | Direk arka yüzündeki yollar için `kamera="arka"` (ya da `(0.5, 0.6, -1.2)`) ve direk / bantlar saydam. | rehber_metin.py:2038, 2046 | FreeCAD'siz. |
| 32.5 | Tünel boyunda gizli. Boyun ve servo yuvasını `saydam` yapıp kamerayı yandan-arkadan al. Lejant sınıf adı "Analog ses (beyaz)" açık temada camgöbeği çiziliyor; ad "Analog ses (açık temada koyu camgöbeği)" olmalı ya da renk adı tamamen çıkarılmalı (rehber_kablo.py:342). | rehber_metin.py:2044, rehber_kablo.py:342 | FreeCAD'siz (lejant adı veriye rehber_veri'den mi geliyor, kontrol edilmeli). |
| B6a | Kart adlarını kareye etiket olarak koy ya da basılı parça tablosundaki renk örnekleri kartları ayırt etsin (şu an üçü aynı mavi). BNO055 için yön oku olmalı. | rehber_metin.py:255 (ADIM["B6a"]) | Etiket FreeCAD'siz (app.js). Ok bir gösterim parçası olursa FreeCAD'li. |

## 3. En önemli 5 düzeltme (öncelik sırasıyla)

1. **32.4 çelişkisi.** Vurgulanan mor çizgi (Kablo yolu 12 / B01) boyuna çıkıyor, metin ise "U06 boyuna girmez" diyor. Öğrenci USB'yi
   yanlış yoldan çeker. Kablo yolu 12'yi 32.4'ten çıkarmak FreeCAD'li yeniden üretim ister. Kamera arka FreeCAD'siz.
2. **K1'de kart ile kablo parçası ayrı adımlara düşüyor.** 17.5 (G14 / G15), 17.9 (SV1 / SV2), 17.10 (B01) ve 17.7 (G17 / G20)
   bağlantıları anlatıyor ama karede çizmiyor, çizgiler K2'de. En azından metne gönderme eklenmeli (FreeCAD'siz). Asıl çözüm
   parçaları bölmek (FreeCAD'li).
3. **Görünmeyen ya da eşleşmeyen kareler: 32.2, 32.6, 17.11.** Kablo yok ya da vurgu yok, 17.11 de 17.12'nin kopyası. Kamera ve
   saydam ayarı yeterli, FreeCAD'siz (32.6'ya şema eklemek FreeCAD'li).
4. **31.4'ün kablolama yarısı görünmüyor**, basılıda "görünümü döndür" diyor ve "Karede: 5 V" yanlış. Önden kamera ve lejant
   düzeltmesi FreeCAD'siz. Kartı bölmek FreeCAD'li.
5. **F1 aşama 1 ölçü noktaları ve 17.1 baraları hiç görünmüyor.** Bu, enerji verilen ilk adım. Ölçü noktası karesi yeni alt adım
   ister (FreeCAD'li). Bara gösterim parçası da FreeCAD'li. Arada metin ve tabloyla yer tarifi verilebilir (FreeCAD'siz).

## 3.1 Kapsam dışı ek gözlem (doğrulanmadı, kararı insana)

Verideki koordinat tanımı şu: `"+X sag, +Y yukari, +Z ileri (yuz)"` (rehber-veri.json `koordinat`, app.js:962). three.js ve FreeCAD
sağ elli koordinat kullanır. Sağ elli bir sistemde Y yukarı ve Z ileriyse, +X robotun **kendi solu**, yani karşıdan bakanın sağı
olur. Kareler bununla tutarlı: "sağ-önden" karede robotun önü ekranın solunda, +X tarafı ekranın sağında. Geometrinin kendisi doğru
olabilir; sorun adlandırmada. Öğrenci "sağ sonar (Q01)", "arka sol enkoder (N01)", "sol BTS7960B", "sağ kol → dağıtım A" sözlerini
robotun kendi sağına göre okursa ters bağlar. Rehberde "sağ = robota önden bakanın sağı mı, robotun kendi sağı mı" tanımı görmedim.
Bu çıkarımı fiziksel bir referansla sınamadım. Doğruysa rehberin başına tek cümlelik bir tanım yeter.

## 4. Üretim ajanının tablosuyla karşılaştırma (`F10l-gunluk.md` § 10.6; § 1–3 yazıldıktan sonra okundu)

Sayım farkı: üretim ajanı açık 15, zor 7, anlaşılmıyor 1 sayıyor; ben açık 3, zor 12, anlaşılmıyor 8. Farkın büyük kısmı ölçütten
geliyor. Üretim ajanı "açık" derken çoğunlukla "vurgulu çizgi net seçiliyor" ya da "metin doğru basılmış" diye bakmış. Ben "öğrenci
kablonun iki ucunu, konektörü ve tarafı kareden bulabiliyor mu" diye baktım.

| Kare | Üretim | Ben | Fark nereden geliyor |
| --- | --- | --- | --- |
| 17.1 | zor | anlaşılmıyor | Aynı gözlem (baralar modelde yok, N3). Kartın işi tamamen baralar olduğu için daha sert yazdım. Sarı saydam "V"yi o tablo anmıyor. |
| 17.2, 17.3, 17.6, 17.8, 17.9 | açık | zor | Çizgi net, bunda anlaşıyoruz. Uçlar (XT60, yuva, klemens, pabuç, saplama) karede yok. |
| 17.4, 17.5 | zor | anlaşılmıyor | 17.5'te G14 / G15'in bu karede hiç çizilmediğini (Kablo yolu 5 / 7 K2'de) o tablo anmıyor. 17.4'te röle ve ön şarj kartı seçilemiyor. |
| 17.7 | açık | zor | Vurgulu Kablo yolu 9'un "XL4016 sonrası kısmı eski" bölümünü taşıdığı ve kartın bunu söylemediği o tabloda yok. |
| 17.10 | zor | zor | Aynı. Ben B01'in eksik olduğunu (32.4'te) ayrıca not ettim. |
| 17.11 | açık | anlaşılmıyor | O tablo "karede yeni öğe yok, P03 tablo" diyerek kabul etmiş. Ben karenin 17.12 ile piksel piksel aynı olduğunu ölçtüm ve U06'nın taban ucunun bu kartta bağlandığını ama gösterilmediğini yazdım. |
| 17.12, 32.3, 32.8 | açık | açık | Aynı. |
| 32.1 | zor | zor | Aynı. |
| 32.2 | anlaşılmıyor | anlaşılmıyor | Aynı. |
| **32.4** | zor ("ince") | **anlaşılmıyor (çelişki)** | **En önemli fark.** O tablo kareyi yalnız "ince" bulmuş. Vurgulu mor çizgi Kablo yolu 12 (B01) ve boyuna kadar çıkıyor, kart ise "U06 boyuna girmez" diyor. Bu çelişkiyi o tablo görmemiş. Kaynakta `sema_ok` gerekçesi (rehber_metin.py:2042) eski yol olduğunu biliyor, ama bu bilgi karta ve lejanta yansımıyor. Üretimin kendi 1400 × 900 ekran karesinde de (`planlama/rehber/goruntu/adim-32-04.png`) mor çizgi boyuna çıkıyor; bunu gözle doğruladım. |
| 32.5 | açık | zor | Kablolar görünüyor. Kartın konusu olan tünel ve geçiş sırası görünmüyor. Lejant renk adı ("beyaz") ile çizim rengi uyuşmuyor. |
| 32.6 | zor | anlaşılmıyor | Aynı gözlem (yeni öğe yok, N4). Bir derece farkla tartılmış. |
| 32.7 | açık | zor | Üst uç görünüyor. Direk arkasındaki iniş ve regülatör ucu görünmüyor. |
| 31.4 (E4.4) | açık | zor | O tablo lejant metninin doğru basıldığına bakmış. Ben şunları buldum: kablolama yarısı görünmüyor, "Karede: 5 V (mavi)" yazıyor ama K05 karede yok, "(görünümü döndür)" basılı karede de var. |
| F1 kontrol | açık | anlaşılmıyor | O tablo metindeki değerlere (14,6 V, 12,8–14,4 V, 3 numaralı saplama) bakmış. Ben karenin ölçü noktalarını gösterip göstermediğine baktım; göstermiyor. Sonuç: metin doğru, kare yardım etmiyor. |
| B6a | açık | zor | O tablo "bağlantı tablosudur" uyarısının yerinde olduğuna bakmış. Ben kart kimliklerinin ve yön işaretinin karede olmadığına baktım. |

O tablonun "Yanlış bilgi veren kare bulmadım" sonucuna katılmıyorum. Yanlış bilgi veren üç kare buldum:
- 32.4: Karedeki yol metinle çelişiyor.
- 31.4: Lejant "Karede: 5 V (mavi)" diyor, ama mavi kablo karede görünmüyor.
- 17.7: Eski yol işaretsiz vurgulanıyor.

Bunlara ek olarak, 17.5 ve 17.9'da metnin bağlattığı kablolar karede yok. Bu yanlış bilgi değil, eksik bilgi.

O tablonun benden fazla yaptıkları: koyu temaya ve ekran düzenine bakmış, iki temada da çekim yapmış, basılı K1 / K2 / E4 / F1 / B6a
sayfalarının hepsini en azından metinden okumuş. Koyu temayla ilgili bulgularını sınamadım.

## 5. Bakamadıklarım

- Tarayıcıyı açmadım. Ekrandaki davranışları denemedim: tıklama, kablo kimliği balonu, döndürme, koyu tema. Kareleri yalnız
  üretilmiş PNG'lerden (açık tema) değerlendirdim.
- `planlama/rehber/goruntu/*.png` (1400 × 900, yan panelli ekran kareleri) dosyalarından yalnız `adim-32-04.png`'ye baktım: 32.4
  çelişkisi orada da var.
- PDF'te yalnız 21, 42 ve 46. sayfalara baktım. B6a (s. 15–16) ve F1 (s. 48–53) basılı sayfalarını açmadım.
- 17.1'deki saydam sarı "V" parçasının kimliğini çözemedim.
- F1'in diğer alt adım karelerinden yalnız 33.7 ile 33.10'a göz attım (A01 / A02 ve anahtarın dört ucu karede görünmüyor). Kapsam
  dışı oldukları için hükme koymadım.
- "FreeCAD'li / FreeCAD'siz" sınıflandırması kod okumasına dayanıyor, üretimi çalıştırmadım.
