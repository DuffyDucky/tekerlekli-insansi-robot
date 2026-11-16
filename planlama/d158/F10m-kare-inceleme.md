# F10m kare incelemesi: P10.7b2e üretimi (commit öncesi, bağımsız)

16.11.2026. Salt okunur inceleme; depoda yalnız bu dosya yazıldı. Bakılan: çalışma ağacındaki `rehber/goruntu/*.png` (web kareleri,
1200 × 720), `planlama/rehber/goruntu/*.png` (basılı sürüm ekran görüntüleri, 1400 × 900), `planlama/rehber/Lale-montaj-rehberi.pdf`
(86 sayfa), `rehber/veri/rehber-veri.json` (kart metni). Eski kareler `git show HEAD:<yol>` ile depo dışına çıkarıldı; piksel farkı
eşik 24 ile ölçüldü.

Ölçüt (F10l ile aynı): öğrenci kablonun iki ucunu, konektörü ve tarafı kareden ve kart metninden bulabiliyor mu; metnin "karede"
dediği görünüyor mu; kare ile metin çelişiyor mu (renk, numara, taraf, alt adım).

Sıra: § 1 hükümleri önceki incelemeyi ve paket günlüğünü okumadan yazıldı. § 2'den sonrası karşılaştırmadır.

## 1. Kendi hükmüm (önceki incelemeyi okumadan)

Taraf denetimi: kamera vektöründen hesapla (+X = robota önden bakanın sağı) her karede "bakış" etiketi, görünen ön yüz (sonarlar) ve
metindeki "önden bakınca sağ / sol" birbirini tutuyor. Taraf çelişkisi bulmadım.

| Kare | Hüküm | Neden |
|---|---|---|
| 17.1 | anlaşılmıyor | Kare değişmedi. İki bara modelde yok (metin söylüyor); karede bu alt adımın hiçbir ucu yok. Görünen kısa siyah parça metinde açıklanmamış; soluk sarı SV3 açıklanmış |
| 17.2 | zor | Kare değişmedi. İki kırmızı hat görünüyor ama hangisinin G02 / G03 / G04 / G06 olduğu, ana sigorta yuvası ve sigorta kutusu etiketsiz; metindeki yer tarifi işi taşıyor |
| 17.3 | zor | Kare değişmedi. G07'nin iki ucu da kadraj dışında ya da direğin arkasında; karede yalnız gövdesi var |
| 17.4 | zor | Yeni açı (sol-ön-üstten) doğru tarafı gösteriyor: röle K1 ve ön şarj kartı sol arkada, metinle tutuyor. Ama iki kutu etiketsiz, turuncu çizgilerden hangisinin G09 / G11, hangisinin G12 olduğu ayrılmıyor |
| 17.5 | zor | Kat saydam, alt kat görünür oldu (önceden kartlar katın altında görünmüyordu). BTS7960B / XL4016 etiketsiz, birçok turuncu çizgi |
| 17.6 | zor | Kare değişmedi. G22'nin PC817 ucu belirsiz, bara ucu boşlukta (bara modelde yok, metin söylüyor) |
| 17.7 | zor | Kare değişmedi. Vurgulu tek çizgi G18 ve bir kısmı eski çizim (metin "uygulanmaz" diyor) ama eski kısmın nerede başladığı karede ayrılmıyor; adımın dört kablosundan üçü başka karelere havale |
| 17.8 | zor | Kare değişmedi. Mantar ve düğüm kartı modelde yok; yeşil uçlar havada biter. Yön tutarlı (A01 sağ arkaya, mantarın yerine) |
| 17.9 | zor | Kare değişmedi. G19 görünür, alt kat ucu kat deliğinde kaybolur; SV1 / SV2 32.1'e havale ve 32.1'de taban kısmı çok küçük |
| 17.10 | zor | Yeni açı (sol-ön-üstten) ve saydam kat doğru tarafı açıyor, ama yedi mor hat (N01, N02, B01, B02, Q01–Q03) düğüm halinde, karede ayrılmıyor; B01'in "eski" dikey kısmı da kadrajda |
| 17.11 | zor | Önceden tam robot (küçük); şimdi PCA9685 ve ESP32 taşıyıcısına yakın. Vurgulu kablo yok (metin dürüstçe söylüyor: P03 çizimsiz), kartlar etiketsiz, "Robotun neresi" balonunda işaret ve konum yazısı yok |
| 17.12 | zor | Son kontrol, genel bakış; iş metinde. Yeni: direk boyunca mor bir çizgi (Kablo yolu 12'nin eski dikey kısmı) çıktı, kare açıklamıyor |
| 32.1 | açık | Sağ-arkadan; sarı uzatmalar direğin arka yüzünden travers altına ve iki omuza okunuyor. Taban ucu (dağıtım A / B) küçük ama metin tarif ediyor |
| 32.2 | zor | Önceki kare boştu; şimdi travers / boyun düğümünde sarı çizgiler görünüyor. Taban ucu (dağıtım kartı C, modelde yok) karede yok; pan / tilt ayrılmıyor |
| 32.3 | açık | G17 direğin ön yüzünden boyuna net. Yeni: hemen yanında açıklanmamış mor çizgi (Kablo yolu 12'nin eski kısmı); 32.3 metni bundan söz etmiyor |
| 32.4 | zor | Sağ-arkadan, gri USB çizgisi gri direk üstünde düşük karşıtlık; taban ucu yanlış yerde çizili (güç paneli) ama uyarı aynı alt adımın altında, kart ile çelişki açıkça yazılı |
| 32.5 | zor | Sol-arkadan; HDMI'nin direğin soluna çıkışı doğru tarafta. Tünel içi görünmez; beş kablodan yalnız ikisi (HDMI, USB) lejantta |
| 32.6 | zor | Kafa içi saydam kabukla görünür, hoparlör kablosunun kafa ucu okunuyor; PAM8403 etiketsiz, "gövdeye inenler" kadraj dışında |
| 32.7 | açık | Sağ-arkadan; G21 direğin arka yüzünden yukarı ve soluna dönüyor, metinle aynı. İki uç (regülatör, ekran) modelde yok, metin söylüyor |
| 32.8 | zor | Kare değişmedi. Genel bakış; "S1 uçları travers arkasında" karede seçilmiyor |
| 31.4 | açık | Sağ-önden açık ön taraftan: sol arka kabuk solda, ses kablosu ReSpeaker'dan PAM8403'e, 5 V PAM'dan tablaya. Küçük not: yedek (takılmaz) USB ses kartı da yeşil kart olarak görünür; bunu 31.3 metni söylüyor, 31.4 söylemiyor |
| F1 kontrol (adim-33) | zor | Kare değişmedi. Metin "ölçü noktaları karede görünmez" diyor ve yerlerini tarif ediyor: dürüst, çelişki yok. Mantar (+X arka) adım 0 örneğiyle tutuyor |
| B6a (adim-14) | açık (sınırda) | Kare değişmedi; kartlar etiketsiz ama metindeki yer tarifi (önden bakınca) sağ-önden karede birebir tutuyor. BNO055 oku karede yok, metin söylüyor |

Dağılım (23 kare): açık 5, zor 17, anlaşılmıyor 1.

Bu pakette değişen öteki kareler:

| Kare | Hüküm | Ne değişti |
|---|---|---|
| 0 | açık | Kare aynı (web), basılı panelde tanım cümlesi. Mantar karede +X arkada, tanımla tutuyor. Adım 0 karesinde "bakış" etiketi yok (`app.js` `kareBaslik`, s = 0 gizli) |
| 17 (K1 ana) | gerileme | Önceden taban yakın plan (y 30–260), şimdi direğin tepesine kadar (y 30–1330): taban küçüldü, kablolar okunmuyor |
| 22 | istenmeyen | Mekanik adım; direk üstünde, traversin önünden geçen soluk mor çizgi eklendi (Kablo yolu 12'nin eski dikey kısmı) |
| 31 | küçük | Web: yalnız lejant adı. Basılı: lejant üç satıra çıktı, 3B kadraj biraz kaydı, küme işaretleri yeniden gruplandı (×3 → ×4); içerik değişmedi |
| 31.2 | iyileşme | Sağ-arkadan kapalı kabuk yerine önden (alttan) açık kabuk: ReSpeaker ve USB kablosu görünüyor |
| 32 | küçük | Direk boyunca giden mor çizgi K2 ana karesinden kalktı, lejanttan "Sinyal (mor)" düştü, analog ses lejant adı uzadı |
| 32.3 | istenmeyen | G17'nin yanına mor çizgi eklendi (aynı neden) |
| 18, 24, 25 | istenmeyen | Aynı mor çizgi "önceki adım" olarak görünür (yan yana bakıldı) |

## 1a. Nedeni: Kablo yolu 12'nin kapısı değişti

`rehber-veri.json` parça farkı: `p1191 Kablo yolu 12` (B01; adında "şemanın direkten kafaya çıkan kısmı eski") `a` / `b` 32 → 17.
Kaynak: `tasarim/freecad/rehber/rehber_veri.py` `RM.kablo_kapisi(p["bb"][3], RM.kablo_yolu_no(p["ad"]))` ("istisna (Kablo yolu
12)"). Şema artık K1'de takılıyor sayıldığı için tamamı, eski dikey kısmı dahil, K1 ana karesinin ve 17.12'nin kadrajına girdi
(kadraj direğin tepesine uzadı) ve 18–31 arası bütün karelerde "önceki adım" olarak direk üstünde görünüyor. 17.10'da "odak" kadrajı
sabitlediği için orada taşma yok. K2 ana karesinden de bu yüzden kalktı.

## 2. Önceki inceleme ile karşılaştırma (F10l-kare-inceleme.md ve F10m-gunluk.md § 8, § 13 bundan sonra okundu)

| Kare | F10l → F10m | Bulgu ne oldu |
|---|---|---|
| 17.1 | anlaşılmıyor → anlaşılmıyor | **Metinle örtüldü.** "Karede görünmez" + yer tarifi, sarı "V" açıklandı (SV3). Bara ve saplamalar hâlâ hiçbir yerde görünmüyor |
| 17.2 | zor → zor | **Metinle örtüldü** (yer tarifi). Kare aynı; G06 hâlâ çizilmiyor |
| 17.3 | zor → zor | **Metinle örtüldü** (yer tarifi). Kare aynı |
| 17.4 | anlaşılmıyor → zor | **Kısmen giderildi.** Kamera doğru tarafa döndü, röle ve ön şarj kartı kadrajda; kutular etiketsiz |
| 17.5 | anlaşılmıyor → zor | **Kısmen giderildi.** Kat saydam, kamera yakın; G14 / G15 karede hâlâ yok, metin 32.1'e gönderiyor (32.1'de taban kısmı çok küçük) |
| 17.6 | zor → zor | **Metinle örtüldü.** Kare aynı |
| 17.7 | zor → zor | **Metinle örtüldü.** Kartta "eski çizim, uygulanmaz" uyarısı ve G19 / A01 / G17 göndermeleri; karede eski kısmın sınırı hâlâ seçilmiyor |
| 17.8 | zor → zor | **Metinle örtüldü.** Kare aynı |
| 17.9 | zor → zor | **Metinle örtüldü.** SV1 / SV2 göndermesi 32.1'e |
| 17.10 | zor → zor | **Kısmen giderildi.** B01 artık bu karede; açı ve saydam kat iyi. Yedi mor hat hâlâ ayrılmıyor; B01'in eski dikey kısmı burada vurgulu |
| 17.11 | anlaşılmıyor → zor | **Giderildi** (17.12'nin kopyası değil, kartlara yakın). Vurgu yok, kart nedenini söylüyor; mini haritada halka yok (günlük N9) |
| 17.12 | açık → zor | Ölçüt farkı + **yeni küçük sorun**: direk boyunca eski mor çizgi |
| 32.1 | zor → açık | **Giderildi** (arka kamera) |
| 32.2 | anlaşılmıyor → zor | **Kısmen giderildi.** Boş kare değil, sarı hat görünür; taban ucu yok |
| 32.3 | açık → açık | Bulgu yoktu. **Yeni küçük sorun**: G17'nin yanında açıklanmamış mor çizgi |
| 32.4 | anlaşılmıyor (çelişki) → zor | **Çelişki giderildi** (vurgulu çizgi artık U06). Kalan: soluk eski B01 çizgisi direkte (günlük N4), taban ucu yanlış yerde ama uyarı alt adımın hemen altında; gri üstüne gri |
| 32.5 | zor → zor | **Lejant giderildi** ("açık temada koyu çizilir"). Tünel ve geçiş sırası hâlâ görünmüyor |
| 32.6 | anlaşılmıyor → zor | **Kısmen giderildi.** AU3'ün kafa ucu görünür; gövdeye inen üç yol kadraj dışında |
| 32.7 | zor → açık | **Giderildi** (arka kamera) |
| 32.8 | açık → zor | Kare aynı; fark ölçütten ("S1 uçları" seçilmiyor; F10l de bunu not etmişti) |
| 31.4 | zor → açık | **Giderildi.** Ses kablosu ve K05 görünüyor, "Karede: 5 V" artık doğru, "(görünümü döndür)" kalktı |
| F1 kontrol | anlaşılmıyor → zor | **Metinle örtüldü.** Kare aynı; kart artık "ölçü noktaları karede görünmez" diyor ve yerlerini tarif ediyor. Ölçü noktası karesi yok |
| B6a | zor → açık (sınırda) | **Metinle örtüldü.** Yer tarifi karede birebir tutuyor; BNO055 oku ve kart adları hâlâ yok |

Dağılım: F10l açık 3 / zor 12 / anlaşılmıyor 8 → F10m açık 5 / zor 17 / anlaşılmıyor 1.

Bulgu sayımı (23 kare): tam giderildi 4 (32.4 çelişkisi, 31.4, 32.1, 32.7), kısmen giderildi 7 (17.4, 17.5, 17.10, 17.11, 32.2, 32.5,
32.6), yalnız metinle örtüldü 9 (17.1, 17.2, 17.3, 17.6, 17.7, 17.8, 17.9, F1, B6a), bulgu yoktu 3 (17.12, 32.3, 32.8; ikisinde yeni
küçük sorun, 32.8'de yalnız ölçüt farkı). F10l § 3.1'deki sağ / sol tanım eksiği **giderildi** (adım 0, K65).

F10l § 4'teki "yanlış bilgi veren üç kare"den: 32.4 ve 31.4 giderildi; 17.7 metinle örtüldü (karede eski kısım hâlâ ayrılmıyor ama kart
"uygulanmaz" diyor ve bu alt adımda o uca dokunulmuyor: G18'in XL4016 ucu B3'te bağlandı).

Günlük § 13.4'ün "açıkça bozuk kare bulmadım" sonucuna büyük ölçüde katılıyorum. Eklediğim: § 13.4'te "doğrulanmadı" denen K1 / 17.12
farkının nedeni doğrulandı (§ 1a) ve bunun 18–31 arası karelere ve 32.1 / 32.3 / 32.4 / 32.7'ye de taşındığı.

## 3. Commit'e engel bulgular

**Yok.** Okuru yanlış bağlamaya götüren çelişki, yanlış taraf, yanlış alt adım ya da boş kare bulmadım. Taraf etiketleri ve "önden
bakınca" yer tarifleri bakılan her karede tutuyor; 32.4'ün eski çelişkisi giderildi, kalan sapma (U06 taban ucu) aynı alt adımda yazılı.

Engel değil ama commit'ten önce bilinçli karar verilmesi gereken bir istenmeyen değişiklik var (§ 4.1).

## 4. Bulunan istenmeyen değişiklik ve yeni küçük sorunlar

1. **Kablo yolu 12'nin K1'e geçmesinin yan etkisi** (§ 1a). (a) K1 ana karesi tabandan direk tepesine açıldı: taban yaklaşık dörtte bir
   boyuta indi, kablolar okunmuyor. Bu, K1'in genel bakışı için açık bir gerileme. (b) 17.12, 18, 22, 24, 25, 31 (basılı), 32.1, 32.3,
   32.4, 32.7'de direk üstünde, kartı hiç anmayan bir mor çizgi (05.11 öncesi ESP32 → kafa yolu). 32.3'te G17'nin hemen yanında,
   lejantta karşılığı olmadan duruyor. Yanlış bağlatmaz (o adımlarda sinyal kablosu döşenmiyor; K2 kablo listesi "eski" diyor), ama ilk
   kez kuran biri "direkte bir sinyal kablosu daha mı var" diye sorar. Öneri (en ucuzdan): 32.3 / 32.4 kartlarına tek cümle (FreeCAD'siz;
   N4 de böyle kapanır); 17.12'ye `odak` ile tabana kadraj (FreeCAD'siz, `alan_isle` artık `odak` işliyor); K1 ana karesinin kadrajı
   için adım düzeyinde kamera / odak (veri alanı var, `kamera: null`; FreeCAD'siz olup olmadığını doğrulamadım). Kalıcı çözüm: Kablo
   yolu 12'nin eski dikey kısmını CAD şemasından silmek ya da ayrı parça yapıp gizlemek (`lale158/kablo_yolu_taban.py`; FreeCAD'li).
2. **31.4:** yedek, takılmayan USB ses kartı ikinci yeşil kart olarak kadrajda; 31.3 kartı bunu söylüyor, 31.4 söylemiyor. 31.4'e yarım
   cümle (FreeCAD'siz).
3. **32 ana karesi:** lejanttan "Sinyal (mor)" düştü, tabandaki K1 mor hatları ise karede renkli duruyor. Küçük.
4. **Adım 0 karesinde "bakış" etiketi yok** (`app.js` `kareBaslik`, `s === 0` gizli): tanımın örneği (mantar sağ arkada) karede
   görülüyor ama okur karenin hangi yandan çekildiğini kareden okuyamıyor. Yalnız adım 0 için etiketi açmak (`app.js`, FreeCAD'siz).
5. **32.4:** gri hazır USB kablosu gri direk üstünde zor seçiliyor (karşıtlık). Lejant rengi koyulaştırılabilir (FreeCAD'siz).

## 5. Adım 0 sağ / sol tanımı

Okur için açık ve doğru. Eksen hesabı (sağ elli, +Y yukarı, +Z ön → +X önden bakanın sağı, robotun kendi solu) tutuyor; adım 0 ve F1
karelerinde mantar +X arkada, tanımın örneğiyle aynı; "SOL" yazılı kol örneği adım 0 kontrol listesindeki "üstüne 'SOL' yaz" ile tutarlı;
"arkadan çalışırken önden bakanın sağı senin solunda" cümlesi K2'nin arka kareleri için tam yerinde. K1 sağ / sol kurulum testi de
tanımla tutarlı (robot kendi soluna dönerken önden bakınca soldaki, yani robotun kendi sağ tekerleri ileri; o teker yazılımın `sag`
sayacı).

Okuru zorlayabilecekler (engel değil):
- PDF s. 1'de tanım, giriş paragrafına bitişik düz metin; bütün rehberi etkileyen bir kural için ayrı kutu ya da kalın başlık daha
  görünür olur.
- Adım 0 karesinde bakış etiketi yok (§ 4.4).
- B6a P01 / P02 tablolarında yazılım adları (`sag_omuz` → dağıtım kartı A) duruyor; tanım "yazılım adları robotun kendi sağıdır" dediği
  için okur `sag_omuz`'un fiziksel sol kola (robotun kendi) gittiğini görünce takılabilir. Tablo doğru (donanım adıyla bağlatıyor);
  "(yazılım adı)" notu yeter.
- Kurulum testi K1 kontrol listesinde ama K1'de işaretlenemez (F5'te yapılır, F5'te de var). F5'e taşınıp K1'de tek satır gönderme
  bırakılabilir.
- Öğrenci rehberinde `planlama/d158/sag-sol-karari.md` göndermesi bir planlama belgesine gidiyor; okur için gerekli değil.

## 6. Kalan zor / anlaşılmayan kareler için öneriler

| Kare | Öneri | FreeCAD'li mi |
|---|---|---|
| 17.1 | Saplama yerleşimini (yıldız 1–5, anahtarlı 1–4) bağlantı tablosu ya da küçük şema olarak ver; kalıcısı bara gösterim parçası | Tablo hayır; parça evet |
| 17.2, 17.3, 17.6, 17.8 | Uç bileşenlerine kısa etiket (XT60, 30 A yuvası, sigorta kutusu, arayüz kartı, PC817): yeni `app.js` alanı | Hayır (yeni kod) |
| 17.4, 17.5 | Aynı etiket; röle K1 ve ön şarj kartına "bağlandığı yer" pembesi | Hayır |
| 17.7 | Eski kısmı kadraj dışına alacak kamera; kalıcısı Kablo yolu 9'u bölmek | Kamera hayır; bölme evet |
| 17.9 (ve 17.5) | SV1 / SV2, G14 / G15 için 32.1'e gönderme yetmiyor (32.1'de taban küçük): Kablo yolu 5 / 7'yi taban ve direk kısmına bölmek | Evet |
| 17.10 | Şema uçlarına kimlik etiketi ya da alt adımı enkoder / BTS / sonar diye bölmek | Etiket hayır; bölme evet |
| 17.11 | Mini haritaya halka (N9) | Hayır |
| 17.12, K1 ana | § 4.1 | 17.12 hayır; kalıcı çözüm evet |
| 32.2 | Pan / tilt ayrımı için etiket; taban ucunu (dağıtım C) metin zaten anlatıyor | Hayır |
| 32.4 | Karşıtlık; U06 taban ucunu yeniden çizmek | Renk hayır; şema evet |
| 32.5 | Boyun / servo yuvası saydam, yandan-arkadan kamera | Hayır |
| 32.6 | Gövdeye inen üç yol için kadrajı genişletmek ya da ikinci kare | Kamera hayır; yeni alt adım evet |
| 32.8 | Travers arkasına yakın kamera (S1 uçları) | Hayır |
| F1 kontrol | Aşama 1 ölçü noktaları için ayrı kare (etek saydam, üstten) | Evet (yeni alt adım) |

Bu turdaki asıl kaldıraç uç etiketleridir: on bir "zor" karenin çoğunda yol görünüyor, eksik olan uçların adı.

## 7. Bakamadıklarım

- **Koyu tema:** bakamadım. Tarayıcı açmadım; üretilmiş PNG'lerin ve PDF'in hepsi açık tema. Analog ses lejantının ("açık temada koyu
  çizilir") koyu temadaki karşılığını görmedim.
- Etkileşim (tıklayınca kablo kimliği, döndürme, mini harita balonu) denenmedi.
- PDF'te yalnız s. 1 (adım 0), s. 21 (K1 kontrol ve kurulum testi), s. 24 (17.4–17.6), s. 48 (32.3–32.6) çizdirilip bakıldı; öteki
  sayfalar yalnız metin aramasıyla.
- Telefon 360 px kareleri, 31.5 / 31.9 / 35.3 / 35.5 / 49.5'teki küçük farklar ve 33.x alt adım kareleri kapsam dışı, bakılmadı.
- Yer tariflerini ("önden bakınca solda") parça koordinatıyla tek tek sınamadım; karedeki görünüşle ve `sag-sol-karari.md` § 1'deki
  koordinatlarla tutarlılığına baktım.
- Önerilerdeki "FreeCAD'li / FreeCAD'siz" ayrımı kod okumasına (F10l § 2, bu paketteki `rehber_gorunum.py` farkı) dayanıyor; üretim
  çalıştırılmadı.
