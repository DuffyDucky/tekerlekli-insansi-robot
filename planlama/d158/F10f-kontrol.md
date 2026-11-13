# F10f bağımsız kontrol (P10.5, kol içi kablo yolu rehberde), 12.11.2026

Kontrolcü: ayrı ajan (B). Uygulama ajanının günlüğünü (`F10f-gunluk.md`) iddia olarak okudum; aşağıdaki sayılar kendi ölçümüm.
Geçici dosyalar scratchpad `f10f-b/` içinde, depoya kopyalanmadı. Depoda yazdığım tek dosya bu rapor. Üretici, depodaki doğrulama
betikleri ve FreeCAD koşulmadı. HEAD karşılaştırması `5831e2f` üzerinden yapıldı: veri ve rehber `git archive` ile scratchpad'e alındı.

## 1. Hüküm

**DÜZELTME GEREKLİ.**

Yolun geometrisi kaynağa sadık: 28 şemanın 28'inde kaynaktan en büyük sapma 0,0723 mm. Merkez çizgisi hiçbir katının içinden
geçmiyor. 28 şemanın 56 karesinde (iki tema) şema ekranda: en az 3473 px. Konsol hatası 0, 121 / 121 konum açılıyor. Pakette
kaldıran sorunlar şunlar:

1. **Birim hatası (metin).** G4 maddesi (41.4 ve 41.5) "iç koşu 125,3 mm, dış 10,2 mm" ile "10,1 mm / 74,9 mm" yazıyor. Kaynakta
   bu değerler açı: `s1_poz` a_i ve a_o, derece. Kod satırı `rehber_kol_kablo.py:735-736`. Aynı değerler mm olarak hesaplanınca
   89,9 / 13,0 ve 7,3 / 95,6 çıkıyor. Ajanın `metin_sayilar` denetimi geçti; denetim birimi görmüyor.
2. **F10f-K1 istisnası geniş.** 46 satırlık uçuş istisnasının 46'sı da F10f'den önce de vardı. 26 parçanın `d` değeri değişti; bu
   değişiklik 46'nın 0'ına yol açıyor. Ama istisna çarpan parçayı ve derinliği sınırlamıyor. Bugün temiz olan 8 satırı da önceden
   muaf tutuyor. 15 parça türünden 11'i rehberde düzeltilebilir: yön ya da işaret değişir, birlikte uçurulur. 1'i duruşa bağlı
   (Kaset cıvatası ψ200). 1'i temsil sorunu (Kaset kapağı). **2'si tasarım / montaj sırası sorusu:** Kol çatalı + 625ZZ dış bilezik,
   ve Dirsek çatalı ↔ horn merkez vidası. Ayrıntı 3.2'de.
3. **41.4 / 41.5 uç duruş kareleri karşılaştırılamıyor.** İki karenin kamerası farklı ([306, 1248, 27] D150 ile [349, 1296, 54]
   D194), çerçeve yerleşimi farklı (alt şerit / sağ sütun). Renk de değişiyor: −45° karesinde yol turuncu, yani servo rengine yakın.
   Her biri tek başına "zor"; ikisini kıyaslayıp U'nun nasıl kaydığını görmek "anlaşılmıyor".
4. **Metin çelişkisi (40.2 ↔ 48.2).** 40.2 "uzatmalarını tüp penceresinden çıkar" diyor, 48.2 "G3'te tüp penceresinden içeri
   girdi" diyor. Uzatma ucunun 40 ile 48 arasında nerede beklediğini hiçbir okur metni söylemiyor. JR'nin pencere dışında takılıp
   sonra itileceği yalnız kod yorumunda (`EL_YOK`) yazıyor. 41.2'deki "F4'te dışarı alınan uçlar buraya bağlanır" yanıltıcı:
   kaynakta tek ve kesintisiz 1856 mm uzatma var.
5. Daha küçük sorunlar 3.3'te: S2 0° lopu pigtail gibi görünüyor (r_min 6,299 mm, sınır 11,2). Okur metninde "voksel" iç terimi
   geçiyor. Lejantta "Kablo yolu" kırmızı kare, çizgiler turuncu / yeşil. 36.5 sol ucu yeşil ile camgöbeği K2 çizgileri karışıyor.
   Depo kökünde boş ve izlenmeyen bir `rehber_metin.py` var.

## 2. Kabul ölçütleri

| Ölçüt (brief "Kabul") | Durum | Ölçüm |
| --- | --- | --- |
| Yolun her parçası kaynaktan türetilmiş, uçlar tolerans içinde | **doğrulandı** | `yol.py`: 28 şema, kaynağa göre en büyük sapma 0,0723 mm. Sabit çoklu çizgiler 0,05. lop_dirsek ↔ FreeCAD analiz 0,0722. s1_−45 / s1_+135 ↔ analiz 0,0617 / 0,0645. Ayna: 13 çift, sapma 0,0. U çözümü (kendi merkezi fark çözücüm): l 68,5222, δ 13,1103, uç 34,1378, Rmin 12,9115; analiz 68,52 / 13,11 / 34,14 / 12,912 |
| Kaynakta olmayan parça uydurulmamış | **doğrulandı (uyarıyla)** | Ajanın "tanımsız" dediği 5 kalem kaynak değerinden geliyor: JR 26 mm birleşim ±13; makaron borunun girişinden 25. Uyarı: karede iki ek işareti tek çizgi üstünde, okur bunu tek kabloda seri iki ek gibi okur. S2 0° lopunun analiz referansı yok; S2 lopu yalnız S2 5'te karşılaştırılabildi |
| Kol adımlarında yol karede görünür | **doğrulandı** | `b_kare.py`: 28 şema × 2 tema = 56 kare, gerçek ekran farkı. Sayfa fonksiyonu ile birebir aynı. En az 3473 px (sol gecis_s1, koyu tema). Geri çizimden sonra fark 0 |
| Uçları doğru parçada | **doğrulandı** | 18 sıfır pikselli uç (her temada 9: s13a, s16b, s19a, s23a, s28a, s31b, s34a, s38a, s40b). Hepsi `ucOrtu` ile açıklandı: varış parçası p0597 / p0654 / p0096 / p0169 ya da devam eden şema. s40b (36.5 sol gövde iç ucu): `ucOrtu` null, kural (3) ile kabul ediliyor; gözle bakınca yeşil uç camgöbeği K2 çizgilerine karışıyor |
| S1 kaseti için yakın kare var | **doğrulandı (kalite: zor)** | 41.4 ve 41.5 var, yalnız kendi alt adımlarında görünüyor (`b_gez`: 26 / 27 başka konumda gizli). İkisi karşılaştırılamıyor (bulgu 3) |
| Sağ / sol ayırt ediliyor | **doğrulandı** | Sağ ve sol ayrı alt adımlar. Başlık ve mini etiket doğru. Karelere baktım |
| Yol hiçbir katının içinden geçmiyor | **doğrulandı** | `geo.py`, 15 kesit, genelleştirilmiş sargı sayısı: 0 nokta içeride. En yakın omuz bandı yüzeyi 2,98 mm. En küçük merkez açıklıkları: lop_s2 ↔ Rulman kapağı 0,6 mm, s1_lop ↔ Üst kol tüpü 1,3 mm; demet kalınlığıyla bu iki yerde S2 0° duruşunda çakışma var (bkz. 3.1 bulgu 6) |
| Sıra denetimi: kablo adımlarında ulaşılamaz 0 | **çürütüldü (istisnayla sağlanıyor)** | Kol adımlarında uçuş satırı HEAD'de 240, şimdi 353. 46 satır F10f-K1 ile muaf, 9 gizli parça perdelenme istisnasıyla muaf. Ayrıntı 3.2 |
| Metinde pin / kanal eşlemesi yok | **doğrulandı** | Kol adımı metinlerinde "kanal" yalnız fiziksel kaset kanalı anlamında geçiyor. Pin, GPIO ya da elektrik kanalı eşlemesi 0 |
| Sayılar kaynakla aynı | **çürütüldü** | 30'dan fazla sayı kaynakla aynı (3.4). G4'teki 4 sayı yanlış birimde (bulgu 1) |
| 50 / 50, konsol 0 | **doğrulandı** | `b_gez`: 121 / 121 konum açıldı, konsol hatası 0 |
| 1192 ↔ 1192 | **doğrulandı** | Veri karşılaştırması: 1192 parça, alan farkı yalnız 26 parçanın `d` değerinde. `u` farkı 0 |
| Denetim 0, ulaşılamaz 0, girilemez 0, görünmeyen yeni parça 0 | **ölçülmedi (kendim)** | Depo doğrulama betiklerini koşmak yasak. `kontrol.json` yalnız okundu. Görünmeyen parça: 9 gizli parça HEAD'dekiyle aynı, yeni değil |
| Yazdırma kareleri boş 0, PDF sayfa / en küçük yazı | **ölçülmedi** | PDF'i açmadım. Ajanın iddiası 74 sayfa / 8,1 pt |
| F10e renk / vurgu / işaret ölçütleri hâlâ geçer | **kısmen doğrulandı** | Kol dışı 14 adres × 2 temada HEAD ile ekran farkı (3.5): beklenmeyen değişiklik 0. F10e'nin kendi ölçütleri koşulmadı |
| `F9b-dogrula` 0, `carpisma_kos` 0, regresyon 10 / 10 | **ölçülmedi** | Koşmak yasak. Betiklerin mtime'ı paketten önce (değişmemişler) |
| Model geometrisi değişmedi | **doğrulandı** | `robot.glb` ve `robot-glb.js` HEAD ile aynı. vendor, arayuz, dirsek, omuz, kod, README, karar-kuyrugu değişmemiş |

## 3. Bulgular

### 3.1 Önem sırası

| # | Önem | Bulgu | Ölçüm |
| --- | --- | --- | --- |
| 1 | yüksek | G4 açıları mm diye yazılmış | `rehber_kol_kablo.py:735-736` `"%s mm" % f(round(x["a_i"], 1))` ve `a_o` aynı. a_i / a_o `s1_poz` içinde derece |
| 2 | yüksek | F10f-K1 istisnası geniş; 2 tasarım / sıra sorusu var | 3.2 |
| 3 | orta | 41.4 / 41.5 kıyaslanamıyor | 1. bölüm bulgu 3: kamera / yerleşim / renk farkı |
| 4 | orta | 40.2 ↔ 48.2 çelişkisi; uzatma ucunun 40–48 arasında nerede beklediği yok; 41.2 "F4'te dışarı alınan uçlar" yanıltıcı | metin, kaynak `s1_boy` 1856 tek uzatma |
| 5 | orta | S2 0° lopu karede pigtail, r_min 6,299 mm (sınır 11,2) | `yol.py`. Metin "çizim modeldeki duruşta, S2 0°" diye uyarıyor ama kare okuru yanıltıyor |
| 6 | düşük | Demet kalınlığıyla S2 0° çakışması: lop_s2 ↔ Rulman kapağı merkez açıklığı 0,6 mm (2 şerit), s1_lop ↔ Üst kol tüpü 1,3 mm (3 şerit, ajanın tahmini −0,8) | `geo.py`. Analizde tasarım alt sınırı 0,93 mm (S2 5…120). S2 0° aralığın dışında olduğu için tasarım sorunu sayılmaz, çizim sorunu |
| 7 | düşük | Okur metninde "voksel" (F4 madde 2) | metin |
| 8 | düşük | Lejant "Kablo yolu" kırmızı kare, çizilen yollar turuncu / yeşil | karelere baktım |
| 9 | düşük | 36.5 sol ucu: yeşil uç camgöbeği K2 çizgilerine karışıyor; `ucOrtu` null, kural (3) ile kabul | `b_kare` s40b |
| 10 | düşük | Ayna asimetrisi: sağ dirsek / bilek kulak cıvatası d 65, sol 100,7 | veri farkı |
| 11 | düşük | Depo kökünde boş, izlenmeyen `rehber_metin.py` (0 bayt, 12.11 09:22) | `git status`: `??`. Üretici betikleri `sys.path.insert(0, HERE)` ile kendi klasörünü öne aldığı için şu an gölgelemiyor; depo kökünden `-c` ile yapılan içe aktarmada gölgeler |
| 12 | düşük | Sona varma testi ("icinde") yalnız kutu ile yapılıyor, zayıf | kod okuması |

### 3.2 F10f-K1 (uçuş istisnası)

**(a) F10f'den önce var mıydı?** İstisna sayısı 58 = 12 eski + 46 F10f-K1. 46'nın 44'ünde `u` ve `d` HEAD'dekiyle aynı. Kalan
2 satır Kaset cıvatası ψ200 (p0463, p0467): d 27,5 → 100,7 oldu, ama ilk çarpışma yolu 3,0 mm, yani HEAD'deki d'den kısa. **46'nın
0'ı d değişikliğinden çıkıyor.** HEAD'de kol adımları alt adım değildi, o yüzden uçuş yolu ölçülmüyordu. HEAD'in alt adımları: 21,
31, 33, 34, 35, 36, 43, 45, 46, 49. Sorun eskiden vardı, F10f onu görünür kıldı. 9 gizli parça da HEAD'de aynı adım sonu perdelenme
listelerinde: 42 {p0590, p0647, p0649}, 44 {p0583, p0584, p0628, p0640, p0641}, 48 {p0569}. Perdelenme istisnası HEAD'de 102, şimdi
115 = 102 + 4 ısıl gömme (40.1) + 9.

**(b) Ne kadar dar?** İstisna parça adı ve alt adımla sınırlı (alt dize eşleşmesi: `k in r["ad"]`). Çarpan parça ve derinlikle
sınırlı değil: o parçanın uçuşunda her derinlikte her engel muaf. Bugün temiz olduğu halde önceden muaf tutulan satır 8: S2 horn
merkez vidası ×2 ("S2 horn" anahtarı onu da yakalıyor), kaset cıvatası ψ226 ×2, Bilezik pulu (baş) ×4. `sema_yalniz` kuralı dar ve
doğru. 32 ASCII sözcüğün hepsi doğru Türkçe yazım; tek istisna "voksel" (bulgu 7).

**(c) 15 parça türü.** Yöntem: `rehber_giris` yön testini 26 yönde (h 0,5, eşik 0,2) kendim koştum; azami = d içinde çarpan yoksa yön
temiz sayıldı. Hedefli denemelerde engel tek tek kaldırıldı.

| Parça türü | Ölçüm | Sınıf |
| --- | --- | --- |
| S2 horn | +z temiz | rehberde düzelir (u +z) |
| Üst kol tüpü | −y temiz (21 mm) | rehberde düzelir |
| S1 kaset gövdesi | +z 76 mm temiz (ön radyal) | rehberde düzelir. (d): metin ve S1-kaset K5 adım 4 doğru, uçuş yanlış |
| Dirsek servosu | −z temiz (30 mm) | rehberde düzelir |
| Bilek servosu çıkış mili | Ayrı satır; yalnız kendi servo gövdesine çarpıyor | rehberde düzelir (servoyla birlikte uçur) |
| Dirsek servo kontra somunu | −x, d ≤ 15 iken temiz (yol 15,5 / 17) | rehberde düzelir |
| 625ZZ iç bilezik (44.1) | −x temiz (13,5) | rehberde düzelir (bilezikler birlikte) |
| Çatal-horn pulu | Kendi cıvatasına takılıyor; cıvata kalkınca serbest | rehberde düzelir (cıvatayla birlikte, +x) |
| Bilezik pulu (somun) | −x, d 25 için temiz (yol 25,5) | rehberde düzelir (işaret ters) |
| Bilezik kontra somunu | −x, d ≤ 20 iken temiz (yol 20,5 / 21,5) | rehberde düzelir. 21,5 mm aralıkta el erişimi ölçülmedi |
| Kaset cıvatası ψ200 | +x'te 3 mm sonra tüpe çarpıyor (1,47) | duruşa bağlı: tasarım bunu S1 −45 / S2 90'da sıkıyor. Rehberde düzelir (duruş göster) |
| Kaset kapağı | Her yön kapalı (+x 1,5 mm sonra kol çatalı 0,62). Tasarım K5 adım 7 S2 ≥ 30 ve iki parçalı yol istiyor (+z, sonra −x 3,3) | rehberde temsil sorunu; duruş ölçülmedi |
| **Kol çatalı** | 26 yönün hiçbiri temiz değil. Tek engel kaldırmak yetmiyor. p0116 iç bilezik + p0117 pul + p0118 mafsal cıvatası kaldırılınca +x / −y açılıyor | **montaj sırası / tasarım sorusu:** çatal, horn ile G2'nin çataldan önce taktığı avara 625ZZ / pim arasında kalıyor |
| **625ZZ dış bilezik (40.1)** | −z yalnız çatalın oturma çakışması sayılmadığı için serbest. Rulman G2 (iç) ve G3 (dış) arasında bölünmüş | **sıra sorusu**, Kol çatalıyla birlikte |
| **Dirsek çatalı** | Eşik 0,3'te bile temiz yön yok (horn merkez vidası 3,05–3,13 mm). Vida kaldırılınca ±z / +y açılıyor | **tasarım / montaj sırası sorusu:** çatal horn merkez vidasının üstünden geçemiyor |

**(d) G4 ön radyal ↔ yan uçuş.** Metin ve S1-kaset K5 adım 4 ön radyal diyor; +z 76 mm temiz. Rehberdeki uçuş yandan, o yüzden
istisnaya düşüyor. Rehberde düzelir.

**(e) 9 gizli parça.** Hepsi HEAD'de de aynı listede, yani F10f'nin getirdiği bir şey değil. Okurun bunları 42 / 44 / 48 karelerinde
görüp göremediği **ölçülmedi**.

**Hüküm:** İstisna "bu paketin sorunu değil, önceden vardı" gerekçesiyle **kabul edilebilir ama bu haliyle değil**. Önce anahtar
"parça + alt adım + çarpan parça + en çok derinlik" biçimine daraltılmalı; bu, bugün temiz olan 8 satırın önceden muaf tutulmasını
da kaldırır. 11 türün yönü / grubu rehberde düzeltilmeli. Kalan 2 kalem (Kol çatalı + 625ZZ sırası, Dirsek çatalı ↔ horn vidası)
istisnayla kapatılmamalı; karar kuyruğuna tasarım / montaj sırası sorusu olarak gitmeli. Ahmet'in fiziksel montajda cevaplayacağı
türden sorular bunlar.

### 3.3 Sayıların kaynakla karşılaştırması (madde 5)

Kaynakla aynı (`arayuz.KOL_KABLO`, `kablo_yolu`, analiz):
- ψ 100 / 280; U ψ 225,35 / 290,13; L 171,4; ψ 214; 226,5 / 230; L 80; L 120; ψ 145.
- 1856 / 1700 (analiz `s1_boy`); 102,4 ve 0,5 artan; y −105; −122…−62.
- JR 26; makaron 25 / Ø4,5; çentik 6×5 (6 × 5,01); yarık 12×6; oluk 6 / 4,5; jr_pay 30.

Kaynakla farklı: G4'teki 125,3 / 10,2 / 10,1 / 74,9 (birimi mm yazılmış, gerçekte derece).

Veri HEAD ile karşılaştırıldı: 1192 parça, değişen tek alan 26 parçanın `d` değeri. `u` değişikliği 0, başka parça alanında değişiklik 0.

### 3.4 Elle ulaşılabilirlik (madde 3)

- 18 "el yok" noktası tüp deliğinin içinde: tüp duvarına uzaklık 25,4 mm. Gerekçe tutarlı.
- Eşikler (EL 20, ESIK 0,2) eski modüllerden geliyor; bu paket için ayarlanmamışlar.
- Bilezik kontra somunu için 21,5 mm aralıkta anahtar / el erişimi ölçülmedi.

### 3.5 Regresyon ve zincir

- Kol dışı 14 adres × 2 tema HEAD rehberiyle karşılaştırıldı (1400×900, `b_head.py`). Adresler: 0, 5, 12, 17, 21.1, 25, 31.3, 31.9,
  33.4, 34.7, 35.3, 46.2, 49.3, 49.4. Fark px (açık / koyu):

  | Adres | Fark (açık / koyu) |
  | --- | --- |
  | 0 | 68 / 82 |
  | 5 | 82 / 57 |
  | 12 | 157 / 134 |
  | 17 | 211 / 188 |
  | 21.1 | 233 / 218 |
  | 25 | 313 / 297 |
  | 31.3 | 383 / 355 |
  | 31.9 | 423 / 412 |
  | 33.4 | 505 / 482 |
  | 34.7 | 630 / 618 |
  | 35.3 | 695 / 685 |
  | 46.2 | 3784 / 3734 |
  | 49.3 | 50 / 24 |
  | 49.4 | 1535 / 1488 |

  Farkın nereden geldiğine baktım:
  - y 20–25 bandı: ilerleme çubuğu. Alt adım sayısı arttı, o yüzden artış adres büyüdükçe artıyor.
  - Sağ alt küçük bölge (x ≈ 890–920): mini harita.
  - 46.2 (3660 px) ve 49.4 (1495 px): yeni dirsek lopu şeması sonraki adımlarda da çiziliyor. Kırpıp gözle baktım: başka değişiklik
    yok.
  - Beklenmeyen değişiklik 0.
- 121 / 121 konum, konsol hatası 0.
- Ok tuşuyla gezinme: 36.1→36.5→37.0 ve 41.1→41.6→42.0 doğru.
- 360 px mini etiket her yerde tek satır. Yazı 49.4'te 7 px, 49.3'te 7,5 px: sınırda okunur. title metni doğru.
- Zincir:
  - Kod dosyaları en geç 12:05'te yazılmış (app.js 10:00, metin 11:48, uret 11:11, denetim 12:05).
  - Veri 12:06; kareler 12:06–12:20; PDF 12:20; `kontrol.json` 12:42 (tam5 bitişi); `F10f-dogrula.json` 12:50; F10e / F10d / F10a
    json 13:08 / 13:20 / 13:28.
  - Önceki doğrulama betikleri değişmemiş: mtime 11-11 / 12-12 01:53, paketten önce.
  - Sıra tutarlı.
- Kural ihlali:
  - Yazma alanı dışında paket kaynaklı değişiklik görmedim. kabuk / gorsel png (11-09) ve `yerlesim-kontrol.json` (11-03) paketten
    önce. `dongu-158.md` farkı orkestratörün günlük satırı.
  - Tek istisna depo kökündeki boş `rehber_metin.py` (izin verilen alan dışında, bulgu 11).

## 4. Bakılan kareler

28 şema her temada 14 benzersiz kareye düşüyor (hash ile denetlendi). 28 görüntünün hepsine baktım.

| Kare | Sınıf | Neden |
| --- | --- | --- |
| 42.2, 42.3, 44.2, 44.3 | açık | Yol, uçlar ve çatal oluğu okunuyor |
| 36.4, 36.5 | zor | Yeşil yol ile camgöbeği K2 çizgileri birbirine benziyor |
| 40.2, 40.3 | zor | S2 0° lopu pigtail gibi. Üç parça tek renk; K, G2 ve tambur bağı karede işaretli değil |
| 41.2, 41.3 | zor | Tambur ve kaset duvarı okunmuyor |
| 48.2, 48.3 | zor | İki ek işareti tek çizgi üstünde, tüp soluk |
| 41.4, 41.5 | her biri zor; ikisini karşılaştırmak **anlaşılmıyor** | Kamera, çerçeve yerleşimi ve renk farklı (bulgu 3) |

Kol dışı HEAD karşılaştırma kareleri (3.5): 46.2, 49.4 ve 12'nin fark bölgelerini kırpıp gözle baktım.

## 5. Ölçülemeyenler

| Kalem | Neden |
| --- | --- |
| `F9b-dogrula`, `carpisma_kos`, F10a/d/e/f doğrulama betikleri, denetim / ulaşılamaz / girilemez sayıları | Brief depodaki doğrulama betiklerini koşmayı yasaklıyor. Yalnız çıktı json'ları okundu |
| PDF sayfa sayısı ve en küçük yazı | Zaman; PDF'i açmadım. Ajanın iddiası 74 sayfa / 8,1 pt |
| Devir (a): 15 parça × 4 kol konumunda HEAD'e göre piksel | Zaman. Dolaylı kanıt: `u` farkı 0, değişen yalnız 26 parçanın `d` değeri; robot.glb aynı |
| 9 gizli parçanın 42 / 44 / 48 karelerinde okurca görülüp görülmediği | Zaman. HEAD'dekiyle aynı oldukları ölçüldü |
| 40.1 ve 44.1 karelerinde K1 içe girmesinin gözle görünüşü | Zaman |
| Kaset kapağının S2 ≥ 30 duruşunda iki parçalı uçuşu | Rehber bu duruşu çizmiyor; FreeCAD yasak |
| Bilezik kontra somunu için 21,5 mm aralıkta el / anahtar erişimi | Takım ölçüsü kaynakta yok |
| `F10f-dogrula.py` sınamalarının ve uç kabul kuralı (3)'ün kendi başına doğruluğu | Okundu, koşulmadı |
| S2 0° lopunun gerçek analiz referansı | Kaynakta yok; analiz S2 lopunu yalnız S2 5'te çözüyor |
