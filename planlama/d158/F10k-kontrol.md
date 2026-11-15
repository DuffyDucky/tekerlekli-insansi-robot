**DÜZELTME GEREKLİ (3 kalem)**: kablo uçları, pin ve kanal tabloları, levha geçişleri ve kayıt doğru. Düzeltilmesi gereken üç şey var ve üçü de montajcının ekranda gördüğü bilgiyle ilgili: şemaya tıklayınca çıkan boy, U06'nın yanlış çizilmiş ucu, dağıtım kartı C'nin adı.

# F10k kontrolü · P10.7b2c (22 kablonun gösterim şemaları ve bağlantı tabloları; kaynak düzeyi)

15.11.2026, bitiş 13:14 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `b6022c3`; paket commit edilmemiş. Salt okuma: depoda
yalnız bu dosya yazıldı. Koşulardan önce ve sonra `git status` ile planlama, rehber, lale158 ve rehber dosyalarının özeti alındı: ikisi
aynı, depoda `__pycache__` yok. Bozma denemeleri bellekteki kopyada ve karalama klasöründeki geçici `kablolar.json` kopyasında yapıldı.
Günlük (`F10k-gunluk.md`) iddia olarak okundu. Sayılar kendi betiklerimden ya da koşulardan çıktı.

## Bulgular (önem sırasıyla)

### D1 (orta-yüksek) Şemaya tıklayınca çıkan "~N mm" kesim boyu sanılabilir

- Yer: `rehber/app.js:1123` (`semaSec`: " · ~" + boy_mm + " mm"), değer `tasarim/freecad/rehber/rehber_veri.py:33` (`boy_mm`).
  Kartta bu sayının yanında kesim boyu yok (`kb` satırı uç, kesit, sigorta ve acil stop bilgisini taşıyor, boyu taşımıyor). "Gösterim
  şeması, ölçüm değil" etiketi de kartta yok; bu not yalnız adımın kablo listesinde duruyor. Kesim boyu yalnız `kablolar.md`'de
  (K1: "boy için tablodaki tahmin kuralı"). Basılı sayfa bu sayıyı göstermiyor (`yazdir.html:172` yalnız "(şema)" yazıyor).
- Aynı adımda çelişki var: E3a kontrol listesinde "D24V50F5 → Pi USB-C yaklaşık 10 cm" (`rehber_metin.py:648`) yazıyor, K03
  şemasının kartı "~47 mm" gösteriyor.
- Farkın büyük olduğu yeni şemalar (şema / kayıt, mm): K01 14 / 200, SV3 39 / 300, K03 47 / 200, C01 70 / 300, K02 71 / 200,
  B02 116 / 400, G22 240 / 500, Q02 228 / 450, Q01 305 / 550, G07 281 / 450, G16 240 / 400, M02 384 / 600. Eski şemalarda da aynı
  durum var (K04 114 / 300, U04 217 / 350, U03 617 / 920).
- Montajda ne olur: kabloyu harfiyen kesen montajcı SV3'ü 4 cm, K01'i 1,5 cm keser. Kablo uca yetişmez, ya da kısa ek yapılır.
- En dar düzeltme: `app.js:1123`'teki etiketi "çizim yolu ~N mm (kesim boyu değil: `kablolar.md`)" yap. İkinci yol: `rehber_veri.py`
  gösterim şeması kaynakları (taban, kafa_ici; istenirse hepsi) için `boy_mm` yazmasın.

### D2 (orta) U06 (ESP32 USB) şemasının taban ucu ESP32'de değil, ama montajcıya söylenmiyor

- Yer: `rehber_kablo.py` `SEMA_GEO_ISTISNA` ("ESP32 USB", "U06 b" ve "son"); `rehber_metin.py:1909` (SEMA adı "→ ESP32 (taban)") ve
  `:894` (K2: "geçerli yol \"ESP32 USB\" şemasında").
- Kendi ölçümüm: şemanın ucu (51,6; 190; −120) güç panelinin üstünde ve ESP32 kutusuna 114,9 mm uzak. İstisnanın gerekçesi dürüst
  ("şema yeniden çizilmeli", karar kuyruğunda). Yine de istisna sınamayı susturuyor ve rehberde bunu gösteren hiçbir cümle yok. K2
  metni montajcıyı tam bu şemaya yönlendiriyor.
- Montajda ne olur: U06 güç paneline doğru döşenir, ESP32'nin USB'sine ulaşmayan yanlış bir hat kurulur.
- En dar düzeltme: K2 kablo listesine bir cümle ekle: "ESP32 USB şemasının taban ucu yanlış yerde, güç panelinin üstünde çizili
  (yeniden çizilecek); kablonun ucu ESP32 taşıyıcısındaki ESP32'nin USB girişine takılır." İstersen aynı not SEMA adına da girer.
  Yeniden çizim FreeCAD koşusuyla yapılır (günlükteki U06 kararı yerinde).

### D3 (düşük-orta) Bağlantı tablosunda "Dağıtım kartı C (kafa)" adı kartın gerçek yeriyle çelişiyor

- Yer: `rehber_metin.py:501` (K1, P03 satırı). Çözülmüş metin: "… → Dağıtım kartı C (kafa) pan sinyal girişi …. Dağıtım kartı C
  modelde yok, yeri çizilmez". Kart güç panelinde, XL4016 C'nin yanında duruyor (kablolar.json P7b2a-6; `MODELSIZ_KONUM`). Ajan
  günlüğü bunu kaydetmiş, metin düzeltilmemiş.
- Montajda ne olur: K1'de kafa henüz yokken montajcı "kafa" adını okuyup P03'ü bağlamadan bırakabilir ya da kartı kafada arayabilir.
- En dar düzeltme: satıra "(kart güç panelinde, XL4016 C'nin yanında; adındaki 'kafa' beslediği pan / tilt servolarıdır)" ekle.
  Kayıttaki ada dokunma.

### Öneri (düzeltme şartı değil)

- Ö1: `KABLO_AD` 9 (`rehber_metin.py:1875`, çevre 5 V) G19 için "bu şemada çizili değil" diyor, K1'deki yeni G19 şemasını
  göstermiyor. Aynı adımda XL4016 çevreden iki hat çiziliyor: eski yol 9 doğrudan ESP32'ye gidiyor, yeni G19 arayüz kartına. Kart
  metni eskinin hangisi olduğunu söylediği için montajcı yönünü bulabilir. Yine de KABLO_AD 4'teki gibi "kendi gösterim şeması K1'de"
  eki 9, 11 (Q01, Q02) ve 12'ye (N01, N02, B02) de girsin.
- Ö2: E3a notu "parça sayısına girmez" ifadesini atlamış (K1, B3 ve B5a'da var). Anlamı etkilemiyor.
- Ö3 (sipariş riski, paketin hatası değil): N02'nin şema yolu 553 mm, tahmini 600 mm (pay 47 mm). Simetriği N01'in tahmini 800 mm.
  Gerçek döşeme şemadan uzun olur; N02'yi N01 boyunda almak daha güvenli.

## Doğruladıklarım (yöntem)

- **Uçlar (madde 1):** 16 yeni yolun baş ve son noktalarını `taban-analiz.json` ile `kafa-analiz.json` kutularına kendi
  hesabımla ölçtüm (kafa kutularına +1290 y eklendi). Kablo yolu, baskı, lazer, bağlantı, burç ve köpük kutuları dışarıda bırakıldı.
  Her uçta en yakın parça, kablolar.json'daki uç parçasıyla aynı. Mesafeler: G07 2,0 / 4,0; G16 röle 2,0 / XL4016 C 4,0; G22 2,0 /
  4,0; SV3 XL4016 C 4,0 / modelsiz; G19 2,5 / 4,0; M02 0 / 0; B02 2,5 / taşıyıcı 4,0; N01 ve N02 motor 0 / taşıyıcı 4,0; Q01 ve Q02
  sonar 7,0 / arayüz kartı 4,0; K01 D24 2,1; K02 SY8205 2,2; K03 2,1 / Pi 4,2; C01 Pi 2,2 / kamera 2,6; AU1 ReSpeaker 6,4 / PAM 5,5.
  Modelsiz uçlara analizlerde ve montaj analizinde ayrıca baktım: anahtarlı bara, dağıtım kartı C, kafa giriş kartı ve ses bölücüsü
  gerçekten modelde yok.
- **Geçişler:** `arayuz.TABAN` ölçülerini (`kat_kesik_on` x −60…60, z 150…175; `motor_kablo_delik` (±80; 36), Ø16) ve
  `taban_parcalar.py`'deki kesimleri okudum: kesik R5 ile `kat_on`'da, delik alt plakada gerçekten açılıyor. Geçiş noktaları: kat x 40
  (G19), 52 (B02), −50 (N01), 25 (N02), 10 (Q01) ve −10 (Q02), hepsi z ≈ 162,5'te kesiğin içinde, kenara en az r kadar uzak. Plaka
  geçişleri M02 (−80; 36,8), N01 (−85; 37,0) ve N02 (85; 37,0), hepsi deliğin içinde. N01 ile M02 aynı delikte, eksenleri 5 mm
  arayla ve r 2,5'le birbirine teğet; boru çakışmıyor.
- **Bağlantı tablosu (madde 2):** beş tablonun çözülmüş metnini (`rehber_metin.ADIM`) satır satır `kablolar.json` damarları ve
  `pin-haritasi.md` ile karşılaştırdım. Satırlar: I01'de SDA GPIO21, SCL GPIO22, 3V3 → VCC, GND; I02'de PCA çıkış başlığından
  BNO055'e; P01'de kanal 0–3 (`sag_omuz`, `sag_omuz_yan`, `sag_dirsek`, `sag_bilek`) dağıtım kartı A girişleri 1–4'e; P02'de kanal
  5–8 kartı B'ye; P03'te kanal 4 `kafa_pan` ve 9 `kafa_tilt`. Hepsi pin haritasının § tablosu ve JSON bloğuyla (`I2C_SDA` 21,
  `I2C_SCL` 22, `pca9685_kanallar`) aynı. P01–P03'te V+ ya da GND satırı yok, kayıttaki "yalnız sinyal" kuralına uyuyor. Kayıtta
  olmayan bilgi uydurulmamış: pin sırası ve dağıtım kartı C'nin pin numarası için "kayıtta yok" yazıyor. Satırdaki "madde 4" B6a'daki
  V+ uyarısını, "madde 7" K1'deki P03 maddesini gösteriyor; ikisi de doğru. Tablolar kablonun rehber kodundaki adımda: B6a ve K1.
  Ekranda (`app.js:1221`) ve basılıda (`yazdir.html:170`) aynı `kablo` alanı basılıyor.
- **Yanıltıcılık (madde 3):** K1, B3, B5a, E3a ve E4'ün kablo listelerinde "gösterim şemasıdır: çarpışma taramasından geçmedi … boy
  ölçümü değildir" notu var; modelsiz uçlar "yeri yaklaşık". AU1 ve AU2'nin KT2 bağı üç yerde görünüyor: SEMA adı, E4 kablo notu ve
  E4 alt adım metni. Çelişen yollar: G19 ile yol 9 için Ö1'e bak. M02 ile yol 4 güncellenmiş. N01, N02, B02, Q01 ve Q02 eski CAD
  yollarında "bu şemada değil" olarak geçiyor, çelişki yok. Göz ardı edilen nokta tıklama kartı (D1).
- **Sayım (madde 5):** `rehber_kablo.py` sonucu: yol çizimi 68 (kaynağa göre örtüşmeli: CAD 39, kol 6, şema 29), bağlantı tablosu 5
  (I01, I02, P01, P02, P03), hiçbiri 1 (G06: şarj girişi XT60E-M, konnektör K50'de karar bekliyor, model yok). Toplam 74. Aracın
  kaynak dökümü, taranmamış şemayı (şema 29) CAD yolundan ayırıyor.
- **Şema boyları (madde 6):** üç yolu elle topladım: SV3 17,33 + 21,54 = 38,9 → 39; K01 8,49 + 5,39 = 13,9 → 14; G16 = 240,0. 16
  yeni yolun hepsini de betikle topladım (G07 280,6 … AU1 219,5); hepsi kayıtla tutuyor. `kablolar.json` farkını anlamca
  karşılaştırdım: `sema_boy`, `surum`, `kaynak` ve `alanlar.sema_boy` dışında dosya HEAD ile birebir aynı, alan sırası değişmemiş.
  `boy` ve `boy_tahmin` ezilmemiş; `sema_boy` 27 kabloda. `maliyet.json` değişmemiş. Şemadan uzun kayıt boyu yok (0): liste doğru ve
  eksiksiz. En dar paylar K05 −16, U01 −25, H01 −46 ve N02 −47 mm.
- **Dokunulmaması gerekenler (madde 7):** `git status` ile baktım: `pin-haritasi.md`, `maliyet.json`, `README.md`, `kod/`,
  `arayuz.py`, `taban/`, `*_lib.py`, `kablo_yolu_ekran.py` ve kontrol raporları değişmemiş. Değişen kaynaklar rehber ve planlama
  betikleri; yeni dosyalar iki şema kaynağı ve günlük. Paket dışında 14 dosya var (13 PNG ve `yerlesim-kontrol.json`); bu kontrolün
  kapsamı dışında, commit'e girmemeli.
- **Talimat metni (madde 8):** F1 madde 3'ün iki cümlesi F10j-kontrol-2'nin önerisiyle harfiyen aynı. Değer ve sıra değişmemiş.
  Güvenlik koşulu da korunmuş: eskiden "aralığa girene kadar" diyen yasak artık "kusuru düzeltmeden" diyor; geçiş kararı yine
  yeniden ölçümün bant kararına bağlı, yani güvenlik koşulu zayıflamamış. Anlamı değişen öbür talimat cümleleri: E4 alt adım 4'teki
  şema durumu cümlesi (talimat aynı) ve KABLO_AD 4. Yeni kablo notları talimat vermiyor, şema durumunu söylüyor.
- **Onay kaydı (madde 9):** farkın çıkan satırlarını tek tek okudum. Dokuzunun hepsinin yerine yenisi girmiş: F1'de iki desen ve iki
  metin; K2'de iki `_DIKIS_SIK` deseni (gevşemedi, büyük harf ve araya kelime kapsandı); `TAMLIK_MUAF`'tan I2C'nin çıkması (sınamayı
  sıkılaştırıyor); E4 cümlesi; KABLO_AD 4. Kritik değer değişmemiş, uyarı silinmemiş.
- **Gizlilik (madde 11):** eklenen satırlara (tracked fark ve üç yeni dosyanın tamamı, 2444 satır) `.git/hooks/pre-push`
  kancasının yedi kalıbını uyguladım: anahtar biçimleri, anahtar ya da parola ataması, e-posta, IBAN ya da telefon, yerel kullanıcı
  yolu ve makine adı, takma ad, ekip soyadları. Eşleşme 0. Günlükte iki kez geçen "karalama klasöründe" bir yol değil.

## Kendi bozmalarım (bellekteki kopya; `sema_geometri_denetle` + `baglanti_tablosu_denetle` + `sema_boy_denetle` + `kaynak_denetle`)

Yakalananlar: N01'in sonu arayüz kartına; G19'un sonu ESP32 taşıyıcısına (yol 9'un eski tasarımı); Q01'in başı orta sonara; N01'in
başı arka sağ motora; M02'nin başı sağ BTS'ye; K02'nin sonu D24'e; K03'ün başı SY8205'e (Pi'ye yanlış 5 V); G07'nin sonu 11 mm'de
(eşik 10); G16'nın başı yıldız barasına; AU1'in sonu ses kartına; N01'in kat geçişi kenara 2 mm (r 2,5); N01 deliğin 1 mm dışında;
G19'un kat geçişi kesiğin önünde; Q02 katın içinde yatay; K01 E4'te; P03 ve tablosunun B6a'ya taşınması; AU1'den AU2'nin
çıkarılması (sema_boy "ortak" ile).
Eşik içinde kaldığı için beklenen şekilde geçenler: G07 9 mm'de; N01'in geçişi kenara 4 mm; K03'ün sonu Pi'nin CSI'sine (aynı parça).

Kaçanlar (öneri olarak; düzeltme şartı değil):

1. SV3'ün dağıtım kartı C ucu geometrik olarak serbest (`MODELSIZ_KONUM` "elle"). Ucu güç panelinin öbür köşesine taşıdım: yalnız
   `sema_boy` tazeliği yakaladı. Bu da `--sema-boy-yaz` ile susar. Öneri: `SEMA_KONUM`'a XL4016 C'nin yanında nominal bir nokta.
2. I01'de SDA ile SCL'yi kayıtta takas ettim (gpio ve pin adı birlikte, tutarlı). `_bag_uc` (`rehber_deger.py:302`) damar adını pin
   rolüne bağlamıyor; `kablolar_denetim` de yalnız görünüm tazeliğinde düşüyor, yani üretimden sonra iki denetim de geçer. Zarar
   vermez, I2C çalışmaz. Öneri: "SDA" adlı damarın pini `I2C_SDA` olmalı (SCL için de aynısı).
3. Tablo başlığındaki "madde N" atfı sınanmıyor (madde 3'e çevirdim, geçti).
4. Adımın kablo notundaki "gösterim şemasıdır" cümlesini sildim, şema adından da "yeri yaklaşık"ı. İkisini yalnız onay kaydı
   tutuyor, yapısal bir kural yok. Yeni bir taban ya da kafa_ici şeması notsuz bir adıma eklenirse hiçbir şey yakalamaz.
5. G19'u B3'e taşıdım, geçti: SEMA adımı kablonun herhangi bir rehber kodu olabiliyor.
6. Kayıt düzeyindeki takaslar (P03'te pan ↔ tilt girişi, P01 K0 → dağıtım kartı B, I01 VCC → VIN, P02 K5 ↔ K6) rehbere kayıttan
   aynen geçer. P01 için `kablolar_denetim` `ayni_nokta`, VIN için `ag` sınaması düşüyor; pan / tilt yalnız görünümle düşüyor, K5 ↔ K6
   hiç düşmüyor. Kayıt tek kaynak olduğu için bu beklenen durum, bu paketin açığı değil.
7. Yöntemi "sabit" olan bir kaydın `boy_tahmin`'ini şema boyuyla ezdim (SV3 = 39): `kablolar_denetim` yalnız görünüm tazeliğinde
   düşüyor. K01'de `tahmin` sınaması yakalıyor.

## Koşular (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Koşu | Çıkış | Sayılar |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | kablolar.md ve elektrik.md güncel |
| `kablolar_denetim.py` | 0 | GEÇER (sema_boy dahil) |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 172 bozma |
| `rehber_denetim.py --kaynak` | 0 | metin 574; ASCII 0; elektrik 0; onay farkı 0 (kablo 161, liste 202, metin 1038); tamlık 172, eksik 0, muaf 19; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 243 / 243 |
| `rehber_kablo.py` | 0 | 68 / 5 / 1; CAD geometri hata 0, bilgi 6; şema 27 (yollar 8, kafa_ici_qled 3, taban 11, kafa_ici 5), hata 0, bilgi 16, istisnalı 5; tablo hata 0; şema boyu hata 0, şema > kayıt 0; onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 0 | 70 / 70 |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | eşlemesiz çizim 0 (veri eski üretimden) |
| `rehber_kablo.py --veri … --bozma-denemesi` | 0 | 78 / 78 |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, kaynak fark 0,0007 mm, GEÇTİ |
| `node --check rehber/app.js` | 0 | |

## Üretimden sonra karede bakılacaklar

- K1: 9 yeni şema eski CAD yollarıyla aynı karede. Kat kesiğinde altı hat var; mor sinyal hatları birbirinden ayırt ediliyor mu?
  G07'nin ana anahtar ucu boşlukta (anahtar F1'de takılıyor) duruyor mu? XL4016 çevreden iki hat çıkıyor (yol 9 ve G19).
- B3 (M02, plaka altı ve delik) ile B5a (tezgâh görünümünde SV3 doğru yerde çiziliyor mu?).
- E3a: kafa giriş kartının çizildiği yer D24'e 13 mm. Montajcı kartı oraya koyar: kart sığıyor mu, boyun geçişini (x −50…−37,
  z −25…−1) kapatıyor mu? K01'in "~14 mm" kartı (D1).
- E4: "Kablolar + yüz grubu → kafa" (yüz grubu yerinde değilken C01'in ucu) ve "Sol arka kabuk → kafa" (AU1).
- Basılı: B6a'ya beş uzun tablo satırı, K1'e iki madde eklendi. PDF'te taşma ve tamlık; K1 daha önce taşmıştı.
- `rehber_veri` günlüğü: gösterim şeması 27, şemalar 65, "UYARI sema alt adimi yok" çıkmamalı.

## Bakmadıklarım

- FreeCAD, çarpışma taraması ve rehber üretimi koşmadı; kareler, PDF ve tezgâh görünümü görülmedi.
- Kafa kutularının tilt 0 kabulünü tilt açısından ayrıca doğrulamadım.
- Ses (AU1) ve kamera (C01) şemalarının kabuk kutularına teması değerlendirilmedi (kabuk kutuları içi boş).
- `kablolar_denetim.py` ile `kablolar_uret.py`'nin bu paketteki farkını yalnız sema_boy açısından okudum.
- Paket dışındaki 14 dosya ve günlüğün ajan A bölümündeki "eski 11 şema birebir" karşılaştırması yeniden yapılmadı.
