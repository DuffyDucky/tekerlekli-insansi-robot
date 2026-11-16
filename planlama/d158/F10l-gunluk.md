# F10l günlüğü: P10.7b2d-A, K1 / K2 demet alt adımları (kaynak düzeyinde)

Başlangıç 15.11.2026 16:08 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `1c4e882` (P10.7b2c). FreeCAD ve üretim koşmaz; commit yok.
Rehber çıktıları (`rehber/veri`, `rehber/goruntu`, `planlama/rehber`) elle değişmez.

## 1. Tasarım (uygulamadan önce, 16:08)

**Kural.** Alt adım = demet (`planlama/adim3/kablolar.json` `demet_sirasi`). Bir alt adımın demetleri, metninde kimliğiyle geçen
kabloların kayıttaki `demet` alanından gelir; elle yazılmış kablo listesi yok. Alt adım metni, adımın mevcut iş metninin (`is_`)
paragraflarıdır (`\n` ile ayrılan maddeler): ana metin = başlık paragrafı (uyarılar), alt adımlar = sıradaki paragraflar, sıra aynı.
Metin yeniden yazılmaz; bölme `rehber_metin.py` sonunda, `ADIM_HAM` kopyasından önce, bir yardımcıyla yapılır (`is_` dizgesi
kaynakta tek parça kalır, bölünmüş hâli ondan türetilir; tam hâli `ALT_TAM_HAM`'da, denetim için).

**Genel maddeler.** Başlık paragrafı (kabuktan önce dur, akü ayrık / enerjisiz) ana adım metninde kalır: en az metin taşır, basılıda
alt adım kartlarından önce, ekranda her alt adımın metninin üstünde görünür. K1 madde 8 ve K2 madde 8 "son kontrol" alt adımıdır.

### K1 (adım 17): 10 alt adım

| Alt adım | Ad | Madde (paragraf) | Demet (kayıttan) | Kablo kimlikleri (metinde) | Karede yeni (şema / kablo yolu) |
|---|---|---|---|---|---|
| 17.1 | Ana hat ve şarj kolu | 1 (p1) | taban (K1), etek (F1) | G01–G04, G06 (G07 anılır) | Kablo yolu 1 |
| 17.2 | Akü ölçüm teli (G07) | 1'in G07 paragrafı (p2) | taban (K1) | G07, G04 | şema G07 |
| 17.3 | Toprak ve iki bara | 2 (p3) | taban (K1) | G05 (yerleşimde G06, G09, G11–G18, G20, G22 anılır) | Kablo yolu 2 |
| 17.4 | Röle K1, ön şarj kartı, bara çıkışları | 3 (p4) | taban (K1), taban alt kat | G08–G16, G22 | Kablo yolu 3, 4; şema G16, G22 |
| 17.5 | Sigorta kutusu çıkışları | 4 (p5) | taban (K1), taban alt kat, boyun, etek (F1) | G17, G18, G19, A01, G20 | Kablo yolu 9 |
| 17.6 | Acil stop ve röle sürücüleri | 5 (p6) | taban (K1), etek (F1) | A01–A06 | Kablo yolu 10 |
| 17.7 | Alt kat kartlarının öbür uçları | madde 5'ten sonraki numarasız paragraf (p7) | taban alt kat | G12–G15, G18, G19, SV1, SV2 | şema G19 |
| 17.8 | Enkoder, BTS sinyal ve sonar | 6 (p8) | taban elektronik katı, taban sonar | B01, B02, N01, N02, Q01–Q03 | Kablo yolu 11; şema B02, N01, N02, Q01, Q02 |
| 17.9 | Direğe çıkan hatların taban kısmı | 7 (p9) | taban elektronik katı, boyun, taban (K1), gövde (K2) | P03, G17, G20, U06 | yok; P03 bağlantı tablosu bu alt adımda |
| 17.10 | Son kontrol: K1'de enerji verilmez | 8 (p10) | genel (son kontrol) | A02, A04 anılır | yok |

### K2 (adım 32): 7 alt adım

| Alt adım | Ad | Madde | Demet | Kablo kimlikleri | Karede yeni |
|---|---|---|---|---|---|
| 32.1 | Kol servo uzatmaları | 1 (p1) | kol sağ, kol sol | S01–S08 | Kablo yolu 5, 7 |
| 32.2 | Kafa servoları, hat C | 2 (p2) | gövde (K2), boyun, taban (K1) | S09, S10, SV3 | Kablo yolu 6 |
| 32.3 | Kafa 12 V | 3 (p3) | boyun | G17 | Kablo yolu 8 |
| 32.4 | ESP32 USB | 4 (p4) | gövde (K2) | U06 | şema U06; Kablo yolu 12 (B01; eski yol, gerekçeli istisna `sema_ok`) |
| 32.5 | Boyun demeti ve gövdeye inenler | 5 + 6 (p5, p6) | boyun | U03, H02, S10, AU3, G17 | şema H02, U03, AU3 |
| 32.6 | Göğüs ekranı 12 V | 7 (p7) | göğüs, taban (K1) | G20, G21 | şema G20 / G21 |
| 32.7 | Son kontrol: direğe tuttur | 8 (p8) | genel (son kontrol) | yok | yok |

**Sıradan sapma:** yok. Paragraflar kaynaktaki sırayla, her biri tam bir alt adımda. Birleştirme: K2 madde 6 (kimliksiz, boyun
demetinin devamı) madde 5 ile aynı alt adımda; K1'de madde 1'in iki paragrafı (ana hat; G07) iki ayrı alt adım.

**Altyapı.**
- `rehber_metin.py`: K1 / K2 `alt=True`, `sira` (ad, `paragraf`, `demet`, `genel`, `desen` = "Kablo yolu N:" gösterim parçaları,
  `sema` = şema adı deseni, `sema_ok` = gerekçeli istisna, `kablo_sec` = alt adımda gösterilen kablo listesi maddesi). Kablo listesi
  (`kablo`) adım düzeyinde kalır (`rehber_kablo.BAGLANTI_TABLOSU` P03 satırını orada arar); P03 satırı yalnız 17.9'da gösterilir.
- `rehber_veri.py`: grup `kablo` (kablo listesi sırası, `kablo_sec` deseninden), `demet`; kablolama adımında hiçbir alt adıma düşmeyen
  ya da iki alt adıma uyan şema üretimi durdurur (eskiden son gruba + UYARI).
- `rehber_gorunum.py` (`alan_isle`): aynı alanlar FreeCAD'siz; metinde `sira` var, veride `sira_grup` yoksa durur.
- `app.js`: demet alt adımında ana metnin uyarısı alt adım metninin üstünde; grubun kablo listesi maddesi alt adım metninin altında,
  kablo kancasında o görünümde yinelenmez. Şema / parça durumu (`semaDurum`, `durum`) değişmez: kendi alt adımında "şimdi", sonra
  "önceki", önce gizli.
- `yazdir.html`: alt adım kartının "Karede" satırına gösterim parçaları (`g.ref`) da girer; grubun kablo listesi maddesi kartta basılır,
  adımın "Kablo kancası" bloğunda basılmaz (bir kez). Satırı olmayan sıralı adımda boş tablo yerine "yeni parça yok".
- `rehber_denetim.py --kaynak`: yeni kurallar D1–D5 (paragraf kapsamı ve sırası, demet ↔ kayıt, kablo ↔ demet, şema / gösterim parçası
  tam bir alt adımda, ana metin uyarıları) + bozma; ZORUNLU_SIRA / ZORUNLU_ALAN "is_" alanı demet adımında alt adım metinlerini de kapsar.
- `rehber_uret.py` `alt_kontrol`: şema karşılığı ölçüt (her şema kendi adımının tam bir alt adımında "şimdi"); PDF tamlık bozmasının
  aday seçimi (iş metni iki sayfaya bölünen adım kalmayabilir).
- `planlama/d158/F10d-dogrula.py`: şema ölçütü (tam bir alt adımda "şimdi", hiç vurgulanmayan 0; piksel bilgi).
- Kare bulguları: G07 şemasının adına ana anahtarın F1'de takıldığı (talimatın sözcükleriyle); B6a'da "3B çizim değil" açıklaması
  tablo satırlarından önce.

## 2. Yapılan iş (16:08–16:27)

Tasarım değişmeden uygulandı. Alt adım metin uzunlukları (karakter, çözülmüş): K1 1185, 1454, 912, 1781, 435, 1272, 694, 710, 597,
939; K2 389, 241, 129, 502, 1977, 558, 88. En uzun kart 32.5 (1977) ve 17.4 (1781).

| Dosya | Değişiklik | Var olan alt adımlara etkisi |
|---|---|---|
| `tasarim/freecad/rehber/rehber_metin.py` | `DEMET_ALT` (K1 10, K2 7 grup), `_demet_bol` (is_ paragraflara, `ADIM_HAM` kopyasından önce; `ALT_TAM_HAM`), `demet_grup_alanlari`, `demet_sema_coklu`; SEMA G07 adına bir cümle; B6a kablo listesinde açıklama maddesi satırlardan önce | yok (yalnız K1 / K2 `sira` alır) |
| `tasarim/freecad/rehber/rehber_veri.py` | grup alanları `demet`, `genel`, `kablo`; adım `demet_alt`; demet adımında şema ya da kablo yolu tam bir alt adımın deseninde değilse üretim durur | yok (koşullar `demet_alt` ile) |
| `tasarim/freecad/rehber/rehber_gorunum.py` | `alan_isle`: metinde `sira` var, veride `sira_grup` yoksa durur (eski veride K1'de durduğu sınandı); demet alanları aynı kuraldan | yok; bugünkü veriyle `alan_isle` artık durur: FreeCAD'li tam üretim gerekir (bilerek) |
| `rehber/app.js` | demet alt adımında ana metin `notlar` kutusunda alt adım metninin üstünde; grubun kablo listesi maddesi metnin altında, kablo listesinde o görünümde yok | yok (`st.demet_alt` / `ag.kablo` yalnız K1 / K2'de) |
| `rehber/yazdir.html` | `altKablo` gösterim parçalarını (`g.ref`) da sayar; grup `kablo` maddeleri kartta, "Kablo kancası"nda değil; satırsız sıralı adımda "Bu adımda yeni parça yok." | bugünkü veride `g.ref` yalnız F1.9'da dolu (p1084, ana anahtar düğmesi gösterimi, renksiz: "Karede" satırına girmez, değişiklik yok); satırsız sıralı adım bugün yok, yeni veride yalnız K1 / K2 |
| `tasarim/freecad/rehber/rehber_denetim.py` | `demet_alt_denetle` (D1–D4) kaynak denetiminde; `_alan_anahtarlari` ("is_ana"; demet adımında alt adım metinleri "is_" alanına da); ZORUNLU_ALAN'a iki "is_ana" uyarısı (D5); `demet_bozma_denemesi` (25) | var olan kurallar aynı; ZORUNLU_SIRA'nın K1 G07 / K2 AU3 satırları alt adım metinlerinde çalışır |
| `tasarim/freecad/rehber/rehber_uret.py` | `alt_kontrol`: şema karşılığı ölçüt `her_sema_tek_alt_adimda` (parça ölçütü aynı); `pdf_tamlik_bozma`: iş metni iki sayfaya bölünen adım yoksa sentetik bölünme (+ `sentetik=` parametresi), önceki sayfanın son satırı iş metninin sonu olan satırdan | parça ölçütü değişmedi; şema ölçütü bugünkü veride (71 alt adım, 46 şema) birden çok 0, hiç 0 (veriden benzetim) |
| `planlama/d158/F10d-dogrula.py` | `gorunurluk`: `sema_tek` (tam bir alt adımda "şimdi", hiç vurgulanmayan 0; piksel 0 bilgi), geçme şartına eklendi | parça ölçütü aynı |
| `tasarim/freecad/rehber/rehber_kritik_onay.json` | yenilendi (§ 4) | — |
| `planlama/d158/F10l-birlesim.py` | birleşim sınaması (§ 3), FreeCAD'siz, dosya yazmaz | — |

**Uyarılar nerede.** Basılıda: ana metin (K1 "Kabuk takılmadan önce burada dur. Bağlarken akü ayrık (XT60 açık).", K2 "Kabuktan önce
dur. Enerjisiz çalış: akü XT60 ayrık, F3 (kafa) takılı değil; kafa uçları enerjisiz bağlanır.") adımın ilk sayfasında, rozetin
("Kablolama kapısı: kabuktan önce dur") ve görüntünün altında, iki sütunlu bloklardan ve bütün alt adım kartlarından önce basılır
(`yazdir.html` `bloklar`: iş metni blokları önce, kartlar en sonda). Ekranda: her demet alt adımında ana metin `notlar` kutusunda alt
adım metninin üstünde; genel bakışta ana metin. Maddelerin içindeki uyarılar (ör. 17.4 "ters bağlıyken enerji verme", 17.2 makaron
sırası, 32.5 AU3 dikiş sırası) kendi paragrafında, sırası değişmeden: ilgili işten önce. Denetim: ana metin uyarıları ZORUNLU_ALAN
"is_ana" (alt adıma taşınırsa yakalanır), madde içi uyarılar D1 (metin bölünmeden aynı) ve ZORUNLU_SIRA.

## 3. Birleşim sınaması

`py -3 -B -X utf8 planlama/d158/F10l-birlesim.py` (önceki commit `1c4e882`'nin `rehber_metin.py`'si bellekte): K1 10189 karakter, ana
metin + 10 alt adım 10189, **birebir eşit** (normalize de); K2 4064 = ana + 7 alt, birebir eşit; ham (yer tutucular çözülmeden) de
birebir. Talimat cümleleri (is_ ve alt adım is_): eski 455, yeni 455, eklenen 0, silinen 0. Bütün kaynak metinleri (yer bağımsız):
eklenen 19, silinen 1; hepsi gerekçeli:

- 17 alt adım adı (başlık, talimat değil): "Ana hat ve şarj kolu", "Akü ölçüm teli (G07)", "Toprak ve iki bara", "Röle K1, ön şarj kartı
  ve bara çıkışları", "Sigorta kutusu çıkışları", "Acil stop ve röle sürücüleri", "Alt kat kartlarının öbür uçları", "Enkoder, BTS
  sinyal ve sonar kabloları", "Direğe çıkan hatların taban kısmı", "Son kontrol: K1'de enerji verilmez", "Kol servo uzatmaları", "Kafa
  servoları, hat C", "Kafa 12 V", "ESP32 USB", "Boyun demeti ve gövdeye inenler", "Göğüs ekranı 12 V", "Son kontrol: direğe tuttur".
- G07 şemasının adı (kare bulgusu a): sonuna nokta ve "Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır), karede
  yok" (sözcükler K1 madde 1'den: "Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır)"; eklenen yalnız "karede yok").
  Silinen 1 = aynı cümlenin noktasız eski hâli.
- B6a açıklama maddesinin yeri (kare bulgusu b): metin aynı, yalnız sıra (cümle çokluğunda fark yok).

## 4. Onay kaydı farkı (`--kritik-onay-yenile`, 197 fark; kayıt kablo 165, liste 204 → 206, metin 1040 → 1058)

- **Taşınan 88** (metin aynı, yer değişti): K1 `is_` → alt adım 1 (5 cümle), 2 (10), 3 (6), 4 (10), 5 (2), 6 (7), 7 (3), 8 (5), 9 (6),
  10 (6); K2 `is_` → alt adım 1 (2), 2 (1), 3 (1), 4 (4), 5 (12), 6 (4), 7 (2); B6a `kablo` içinde 2 cümle (sıra).
- **Eklenen 20**: 17 alt adım adı; SEMA G07 "Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır), karede yok"; liste
  ZORUNLU_ALAN 2 satır (K1 / K2 "is_ana").
- **Değişen 1**: SEMA G07 ilk cümlesinin sonuna nokta.
- **Silinen 0.** Kritik değer (yer tutucu, sigorta, kesit, uç, sıra) değişmedi; uyarı silinmedi; kablo bölümü (165) aynı.

## 5. Testler (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`), 16:2x

| Sınama | Çıkış | Sonuç (önce → sonra) |
|---|---|---|
| `planlama/adim3/kablolar_uret.py --kontrol` | 0 | güncel |
| `planlama/adim3/kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 172 bozma GEÇER |
| `rehber_denetim.py --kaynak` | 0 | metin 575 → 609; zorunlu eksik 0; onay farkı 0 (yenilemeden sonra); tamlık 172 öğe, eksik 0, kablo 74 / 74; demet D1–D4 hata 0 (K1 10 alt adım, 38 kablo, 16 şema / kablo yolu; K2 7, 18, 10) |
| `rehber_denetim.py --bozma-denemesi` | 0 | 249 / 249 → **274 / 274** (25 yeni demet bozması, hepsi kendi kuralıyla yakalandı) |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | 74 kablo, 68 / 6, üç sınıf 68 / 5 / 1, onay tutuyor, GEÇER / 86 / 86 |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` / `+ --bozma-denemesi` | 0 / 0 | GEÇER / 95 / 95 (eski veriyle: veri yeniden üretilmedi) |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GEÇTİ |
| `node --check rehber/app.js` | 0 | — |
| `planlama/d158/F10l-birlesim.py` | 0 | GEÇER (§ 3) |
| `rehber_uret.pdf_tamlik_bozma` (eski PDF + eski veri, içe aktarılarak) | — | doğal aday (K1) 10 / 10; `sentetik=True` (K2) 11 / 11 |
| derleme sınaması (`compile`, dosya yazmaz): `rehber_veri.py`, `rehber_uret.py`, `rehber_gorunum.py`, `F10d-dogrula.py` | — | hatasız |
| `rehber_gorunum.alan_isle` (bellekte) | — | eski veride K1'de durdu; benzetilmiş `sira_grup` ile demet alanları yazıldı |

Yeni bozmalar (25): bozulmamış kaynak hata 0; D3 sonar cümlesi 17.8 → 17.1 (kablo yanlış alt adımda); D1 aynı taşıma; D3 17.8'in
"taban sonar" demeti silindi; D2 K2 madde 1 demetleri yer değiştirdi; D2 kayıtta olmayan demet; D2 gerekçesiz demet; D2 "genel"
işareti silindi; D1 17.6 metni silindi; D1 sıra kaydında madde 5 yok; D1 17.3 ↔ 17.4 metni yer değiştirdi; D1 K2 madde 2 ↔ 3;
D1 K2 madde 6 iki alt adımda; D1 17.4'ten "ters bağlıyken enerji verme" silindi; D5 K1 ana metinden "Bağlarken akü ayrık (XT60 açık)."
silindi; D5 K2 "kafa uçları enerjisiz bağlanır" silindi; D5 akü ayrık uyarısı ana metinden 17.1'e taşındı; ZORUNLU_SIRA 32.5'te
dikişler AU3'ten önce; D4 G19 şeması hiçbir alt adımda; D4 G19 iki alt adımda; D4 Kablo yolu 9 hiçbir alt adımda; D4 U06 şeması
kablosunu anmayan alt adımda; D4 Kablo yolu 12'nin `sema_ok` gerekçesi silindi; D4 bayat desen; D4 P03 tablosu iki alt adımda.
Depoda `__pycache__` yok.

## 6. Üretimde beklenenler (ölçülmedi)

- Alt adım **71 → 88** (K1 + 10, K2 + 7); şema **65** (değişmez; alt adımlı adımların şeması 46 → 60); parça **1192** (değişmez; K1 / K2'de
  yalnız 12 "Kablo yolu" gösterim parçası, hepsi tam bir alt adımda); çizilen 68 / 5 / 1 aynı.
- PDF: 80 sayfadan fazla (tahmin 82–86: K1 kartları 10, K2 7; ilk sayfalarda iş metni kısaldı). Ölçüt sayfa değil: taşan 0, tamlık eksik
  0, yineleme 0, en küçük yazı ≥ 8,0 pt. Tamlık maddesi artar (17 alt adım is_ maddesi), iş metni karakteri azalır (K1 / K2 ana metni yalnız
  başlık).
- `rehber_uret.alt_kontrol`: her parça tek alt adımda + her şema tek alt adımda; `F10d-dogrula.py`: `sema_tek` GEÇTİ beklenir.
- PDF tamlık bozması: iş metni iki sayfaya bölünen adım kalmazsa sentetik bölünmeyle koşar (eski PDF'te sınandı).

**Bakılacak kareler:** 17.1–17.10 ve 32.1–32.7 (ekran, iki tema; basılı kartlar). Özellikle: 17.2 (G07 tek başına, şema adında "karede
yok"), 17.4 (Kablo yolu 3 / 4 + G16 / G22; F10k'nın "K1 mor hatlar" bulgusu), 17.9 ve 17.10 / 32.7 (karede yeni öğe yok: yalnız önceki
hatlar), 32.4 (U06 + eski yollu Kablo yolu 12), 32.5 kartının boyu (1977 karakter, en uzun), K1 ilk sayfası (iş metni yalnız başlık,
"Bu adımda yeni parça yok."), B6a kablo kancası (açıklama satırlardan önce), ekranda alt adım panelinde ana metin kutusu (360 px).

## 7. Doğrulanmayanlar ve okunurluk

- FreeCAD, `rehber_veri.py`, `rehber_uret.py`, `rehber_sira.py`, `F10d-dogrula.py` koşmadı: yeni veri, kareler, PDF yerleşimi (taşma,
  yazı boyu, sayfa), perdelenme / uçuş denetiminin boş gruplu alt adımlarla davranışı, app.js değişikliğinin tarayıcıda görünümü ölçülmedi.
- Okunurluk: 32.5 ve 17.4 kartları uzun (tek kartta bölünmez; sığmazsa yazı küçülür, 8,5 pt altına inmez, yine sığmazsa taşma sayılır).
  Demet alt adımlarında karede yeni parça yok, yalnız gösterim çizgileri: 17.9, 17.10, 32.7 kareleri önceki hatları gösterir. Ekranda
  ana metin her alt adımda yinelenir (basılıda bir kez). K1'in 22 maddelik kontrol listesi adım düzeyinde kaldı (bölünmesi kapsam dışı).
  B6a'da "Bu dört satır" artık satırlardan önce: ileriye gönderme, sözcükler aynı.
- Kablo yolu 12 (B01) K2'de, B01 K1'de bağlanır: 32.4'te gerekçeli istisna (U06 şemasının yeniden çizimi kapsam dışı).

## 8. Açık (bu pakette düzeltilmedi)

- Demet ayrımı: 17.3'teki bara yerleşim listesi başka demetlerin kablolarını (G12–G18, G20, G22) yalnız saplama yeri olarak anar; D3
  onları bağlandıkları alt adımda bulur. Yerleşim listesinin ayrı bir "hazırlık" alt adımı olup olmayacağı bağımsız kontrolün yargısına.
- `rehber_gorunum.alan_isle` (FreeCAD'siz yol) bugünkü veride durur: ilk üretim FreeCAD'li tam koşu olmalı.
- F10k kare bulgularından "K1 mor hatlar", "SV3 ucu" ve ajan B'nin E3a K01 / E4 alt 4 bulguları bu pakette yok.

## 9. Düzeltme turu 1 (F10l-kontrol: DÜZELTME GEREKLİ), 2026-11-16 01:34–02:12

FreeCAD, `rehber_veri.py` ve `rehber_uret.py` tam koşusu yok; `rehber/veri`, `rehber/goruntu`, `planlama/rehber` elle değişmedi; commit
yok. Değişen dosyalar: `rehber_metin.py`, `rehber_deger.py`, `rehber_denetim.py`, `rehber_veri.py`, `rehber_gorunum.py`, `rehber_uret.py`,
`rehber_kritik_onay.json`, `rehber/app.js`, `rehber/yazdir.html`, `planlama/d158/F10l-birlesim.py`.

### 9.1 Yapılan

- **D1 bara sırası, çifte bağlatma.** Kayıt: `kablolar.json` `bara-pabuc.kopruler.*.yerlesim` (yıldız 1 G12 / G14 / G15, 2 G13 / G16,
  3 G05 / G06, 4 G17 / G18, 5 G20 / G22; anahtarlı 1 G12 / G14 / G15, 2 G13 / G16, 3 G09 / G11, 4 G22; köprüler 12 AWG; "büyük akımlı
  (12 AWG) pabuçlar yığının altında"). Fiziksel sıranın dayanağı: baralar B5a'da panelde durur (B5a kablo listesi "yıldız barası …
  anahtarlı bara … erişilebilir kalsın"), yani K1'in ilk işi baraya bağlanabilir. Bara ve yerleşim paragrafı ("2. Toprak") K1'in başına
  alındı (17.1); ana hat ve şarj kolu 17.2. Her bara ucu tam bir kartta, o kartta saplama yer tutucusuyla: G05 17.1; G06 17.2
  (`{saplama.G06}`, G05'in üstüne); G09 / G11 17.4 (`{bsaplama.G09}`, `{bsaplama.G11}`); G12–G16 17.5 "Bara çıkışları" (yeni kart:
  önce 12 AWG G12 / G13, sonra 16 AWG G14 / G15 ve G16; eskiden G12–G15 "Alt kat kartlarının öbür uçları"nda, G16'dan sonra); G22 17.6;
  G17 / G18 / G20'nin kutu ve yıldız ucu 17.7 (eskiden 17.7 + 17.9 + 17.10 üç kartta). Öbür kartlar bu uçları "alt adım 17.k'te
  bağlandı" diye anar (17.9, 17.11). Ayrı "yerleşim hazırlığı" kartı açılmadı: yerleşim listesi 17.1'de, `yerlesim=True` (U4 muaf).
  Saplama sırası kayıtla: yıldız s1 köprü → G12 → G14 / G15; s2 köprü → G13 → G16; s3 G05 → G06; s4 G17 / G18; s5 G22 (17.6) → G20
  (17.7), ikisi 18 AWG; anahtarlı s1 G12 → G14 / G15; s2 G13 → G16; s3 G09 / G11; s4 G22. Saplama numaraları "N numaralı saplamasına"
  biçiminde: "N. saplamasına" cümle bölücüde (`}.` + boşluk) cümleyi ikiye bölüyordu, anahtar-bağlam denetimi kabloyu bulamıyordu.
- **D2 numara uyuşmazlığı.** Çapalar ("1. ", "3b. ") kaynakta kalır, üretilen metinden silinir; "madde N" / "K1 madde N" / "K2 madde N"
  türetilerek "alt adım S.M" olur (S M6 sırasından: K1 17, K2 32; `rehber_veri` aynı sırayı sınar, uymazsa durur). Kendi kartına
  gönderme "bu alt adımda aşağıda / yukarıda". Kontrol listesi, kablo listesi ve başka adımlar da taranır ("B6a madde 4" başka adımın
  maddesi, çevrilmez). 14 gönderme çevrildi, çözülemeyen 0 (§ 9.3 C).
- **D3** `rehber_uret.py` `alt_kontrol`: `tek = tek_s = None` (`--adimlar` yolunda `tek_s` tanımsızdı). Koşulmadı, derlendi.
- **N3 yapıldı:** 32.1 sonuna "Karede Kablo yolu 5 ve 7'nin baradan dağıtım kartlarına giden kısmı K1'de bağlandı; burada yalnız
  uzatmaları tak." (kare değişmez, yanlış okuma metinle karşılanır). **N4 yapıldı (K2):** eski 32.5 "Hoparlör kablosu (AU3) dışındaki"
  cümlesinden önce yalnız "\n" ile bölündü (32.5 tünelden geçirme, 32.6 kafa uçları + AU3 + inenler; cümle değişmez). 17.4'ün bölünmesi
  D1 ile kendiliğinden oldu (17.4 / 17.5 / 17.6). **N1 kısmen:** D3 genişletilmedi (kablo başına sahip kart kaydı ister, kapsam dışı);
  bara uçlu kablolar için D6 U2 yakalar, bozması eklendi ("G22 talimatı 17.1'e taşındı" → D6 2). Bara ucu olmayan kablo taşınırsa yine
  yalnız onay kaydı yakalar. N5, N6: dokunulmadı.
- **Gerilim yer tutucuları (F1 kontrol):** "akü en çok 14,6 V" → `{v.aku_en_cok}` (yeni; `elektrik.md` E2 "Akü gerilimi" satırındaki
  "N V →" değerlerinin en büyüğü, 14,6 V; bağlam "akü"); "akü gerilimi (12,8–14,4 V)" → `{v.aku_aralik}` (var olan; `elektrik.md`:67).
  Çözülmüş metin aynı. "20 V aralığı" bırakıldı: kaynakta yok (`00-genel.md`'de de), uydurulmadı.
- **E4 lejantı:** E4 alt 4 grubuna `sema_ortulu={"Ses kablosu (AU1": "sol arka kabuğun arkasında kalır"}`. `yazdir.html` lejantı bu
  şemayı "Karede:" satırından çıkarıp "Karede görünmez: ad: neden" satırında yazar; `app.js` lejantı o alt adımda "Ad: neden (görünümü
  döndür)" notu ekler. `rehber_veri` deseni grubun şemalarından birine uymazsa durur (benzetim: 1 şemaya uyuyor). Genel bakış lejantı
  (örtülme ölçümü ister) yapılmadı.
- **Yapılmadı:** E3a K01 etiket yeri (app.js etiket paneli bindirmesi, tarayıcısız sınanamaz, risk düşük değil); K1 mor hatlar (renk
  kuralı / ΔE eşiği değişir, kablo onay kaydını etkiler); A4 (`karar-kuyrugu.md`:1496 basılı sayfa boşlukları, R5) yalnız not: bu turda
  sayfa düzenine dokunulmadı; SV3 dokunulmadı.

### 9.2 Talimat metni: eski → yeni (cümle cümle, çözülmüş; § 9.3 B'nin beklenen listesi)

Değişen 8, eklenen 3, silinen 0 talimat cümlesi (D1 7 + 1, N3 1, D1 yeni 2). Kritik değer (sigorta, kesit, uç, klemens, gerilim) hiçbirinde
değişmedi, yalnız saplama numarası eklendi; uyarı silinmedi, hepsi işten önce yerinde ("ters bağlıyken enerji verme" 17.6, "Bağlarken akü
ayrık" ana metin, "dikişleri sıkmadan önce" 32.6).

1. 17.2 G06: "… − ucu yıldız barasına (mavi pabuç)." → "… − ucu yıldız barasının 3 numaralı saplamasına, alt adım 17.1'de takılan G05'in
   üstüne (mavi pabuç)." Gerekçe: D1, kayıt s3 G05 / G06, bara 17.1'de kurulu.
2. 17.4 G09: "… G09 çıkıştan anahtarlı baraya; 12 AWG) …" → "… G09 çıkıştan anahtarlı baranın 3 numaralı saplamasına; 12 AWG) …". D1, s3.
3. 17.4 G11: "… G11 direncin öbür bacağından baraya; …" → "… G11 direncin öbür bacağından anahtarlı baranın 3 numaralı saplamasına; …". D1.
4. 17.5 G16: "XL4016 C'yi de … bağla (G16, 16 AWG)." → "… bağla (G16, 16 AWG); G16'nın + ucu anahtarlı baranın 2 numaralı, − ucu yıldız
   barasının 2 numaralı saplamasına, G13'ün üstüne." D1, s2, 12 AWG altta.
5. 17.6 G22: "PC817 #2 algı teli (G22, 22 AWG): … 2 A mini hat sigortası." → "…; G22'nin yuvasının bara kuyruğu anahtarlı baranın 4 numaralı
   saplamasına." D1, s4 (yıldız ucu s5 cümlesi değişmedi).
6. 17.9: "Alt kat kartlarının … gelmeden bağlandı." → "…; G12–G15'in bara uçları alt adım 17.5'te, G18'in kutu ve yıldız uçları alt adım
   17.7'de bağlandı." D1 (uç iki kartta "bağla" okunmasın).
7. 17.9: "Burada B3'te etiketli bırakılan öbür uçları yerlerine bağla: G12 ve G13'ün … yıldız barasına; G14 ve G15'in … (madde 3) …; G18'in
   + ucunu sigorta kutusunun F4 çıkışına (madde 4), − ucunu yıldız barasına; G19'u …" → "Burada B3'te etiketli bırakılan öbür uçları
   yerlerine bağla: G19'u …; SV1'i …, SV2'yi … (OUT+ → V+, OUT− → GND)." D1: G12–G15 17.5'e, G18 17.7'ye taşındı (F4 bilgisi 7. ve 10.
   maddede).
8. 17.11: "Kafa 12 V (G17), göğüs 12 V (G20) ve ESP32 USB'nin (U06) taban uçlarını bağla." → "Kafa 12 V'un (G17) ve göğüs 12 V'un (G20)
   taban uçları alt adım 17.7'de bağlandı; ESP32 USB'nin (U06) taban ucunu bağla." D1.
9. Yeni, 17.5: "G12–G15'in alt kat ucu B3'te bağlandı; burada B3'te etiketli bırakılan bara uçlarını bağla, kalın pabuç altta: önce G12'nin +
   ucunu anahtarlı baranın 1 numaralı, G13'ünkünü 2 numaralı saplamasına, − uçlarını yıldız barasının 1 ve 2 numaralı saplamasına; sonra
   G14 ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baranın 1 numaralı saplamasına, − uçlarını yıldız barasının 1 numaralı
   saplamasına (her biri G12'nin üstüne)." D1 (7'nin taşınan kısmı + saplama + sıra).
10. Yeni, 17.7: "G17, G18, G20 ve A01'in kutu ucunu kendi yuvasının çıkışına bağla (G17 F3, G18 F4, A01 F5, G20 F6); G17, G18 ve G20'nin −
    ucunu yıldız barasına: G17 ve G18 4 numaralı, G20 5 numaralı saplamaya (G18'in öbür ucu B3'te XL4016 çevreye bağlandı)." D1 (yuva
    numaraları aynı paragrafın sigorta listesinden).
11. Yeni, 32.1: "Karede Kablo yolu 5 ve 7'nin baradan dağıtım kartlarına giden kısmı K1'de bağlandı; burada yalnız uzatmaları tak." N3.

Yalnız biçim: 16 paragraf başı çapası silindi (K1 "1." … "8.", "3b" kaynakta kalır; K2 "1." … "8."); 14 gönderme çevrildi (17.12 köprü
listesi 4, kontrol "Pim yeri … (alt adım 17.4)" ve "yerleşim alt adım 17.1'deki gibi", kablo listesi P03 "alt adım 17.11", F5 is_ ve
F5 alt 1 "1N5819 yönü alt adım 32.4", 32.6 "gövde ucunu fişsiz bırak (bu alt adımda aşağıda)", yukarıdaki 1, 6 (2), 8). F1 kontrol iki
cümle yalnız ham metinde (yer tutucu), çözülmüşü aynı. Kart adları: K1 "Röle K1, ön şarj kartı ve bara çıkışları" → "Röle K1 ve ön şarj
kartı" + "Bara çıkışları: BTS7960B ve XL4016 A / B / C" + "PC817 #2 algı teli (G22)"; K2 "Boyun demeti ve gövdeye inenler" → "Boyun
demeti: tünelden geçirme" + "Kafa uçları, hoparlör kablosu ve gövdeye inenler". Arayüz dizgeleri (yeni): `yazdir.html` "Karede görünmez:",
`app.js` "(görünümü döndür)".

### 9.3 Denetimler

- `rehber_denetim.py`: **D6** `bara_uc_denetle` (U1 her bara ucu ve iki köprü tam bir kartta, kayıtta olmayan uç yok; U2 sahip kartta
  saplama yer tutucusu; U3 aynı saplamada 12 AWG / köprü incelerden önce, kart sırası + metin içi yer; U4 ucu başka kartta bağlanan
  kabloyu anan kart "alt adım 17.k" der, `yerlesim=True` muaf). **D7** `gonderme_denetle` (çözülemeyen yok; "madde N" kalmadı; paragraf
  başında çapa yok; her "alt adım S.M" var olan karta; kayıttaki her gönderme çapanın paragrafının bulunduğu karta, kaynaktaki gönderme
  sayısı = çevrilen + çözülemeyen). Uçlar `DEMET_ALT[..]["uc"]`'de (üretim verisine girmez). Eski bozmalar sıra numarası yerine kart adıyla
  arar (kart eklenince kaymasın). 15 yeni bozma: D6 9 (köprüler 17.4'e = eski hata, G16 G13'ten önce, "17.5'te" göstergesi silindi, direkte
  "bağla", sahip kartta yer tutucu yok, uç hiçbir kartta, **bir uç iki kartta**, kayıtta olmayan uç, N1 G22 taşındı), D7 6 (**çözülmeyen
  gönderme** "madde 9", "alt adım 17.13", çapa kaldı, F5'te "K2 madde 4", kayıt hedefi kaydı, kayda geçmeyen gönderme). K1 köprü
  ZORUNLU deseni "(madde 5)" / "(madde 2)" → "(alt adım 17.8)" / "(alt adım 17.1)".
- `F10l-birlesim.py` yeniden yazıldı: A yapı (ana + alt = `ALT_TAM_HAM`; `ALT_TAM_HAM` = çapalı kaynağın çapa / gönderme dışında aynısı,
  paragraf paragraf), B bütün kaynak metinlerinde cümle çokluğu (çapa ve gönderme biçimi eşitlenir) **beklenen listeyle tam eşit**
  (eklenen 13, silinen 9: § 9.2'nin 11 talimat cümlesi + P10.7b2d-A'nın G07 şema notu, bir cümle ikiye; listede olmayan ya da
  gerçekleşmeyen fark hata), C gönderme sayımı (14, çözülemeyen 0).
- **Onay kaydı** (`--kritik-onay-yenile`, 128 fark; kayıt kablo 165, liste 206, metin 1058 → 1064): 76 yalnız yeri değişen cümle (kart
  numarası kaydı, metin aynı); 22 cümle çapa / gönderme biçimi (§ 9.2 "yalnız biçim"); 1 kural (K1 köprü ZORUNLU deseni); içerik 12 → 18:
  talimat 8 değişen + 3 yeni (§ 9.2), kart adı 2 → 5, F1 iki cümle ham yer tutucu (`{v.aku_en_cok}`, `{v.aku_aralik}`). **Kritik değer
  farkı 0:** silinen içerikteki değer belirteçlerinden eklenende olmayan yalnız "14,6 V" ve "14,4 V" (yer tutucuya geçti, çözülmüşü aynı);
  eklenenler saplama yer tutucuları (kayıttan) ve yuva numaraları (aynı paragraftan).

### 9.4 Sınamalar (FreeCAD'siz; önce = § 5, sonra = 16.11 02:0x)

| Sınama | Çıkış | Önce → sonra |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel → güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 172 → GEÇER / 172 |
| `rehber_denetim.py --kaynak` | 0 | metin 609 → 615; zorunlu eksik 0; onay farkı 0 (yenilemeden sonra; önce 128); tamlık 172, eksik 0, kablo 74 / 74; demet D1–D4 → D1–D7 hata 0 (K1 10 → 12 alt adım, 38 kablo, 16 öğe; K2 7 → 8, 18, 10) |
| `rehber_denetim.py --bozma-denemesi` | 0 | 274 / 274 → **289 / 289** |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, onay tutuyor / 86 / 86 → aynı |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` / `+ --bozma-denemesi` | 0 / 0 | GEÇER / 95 / 95 → aynı (eski veri) |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm GEÇTİ → aynı |
| `node --check rehber/app.js` | 0 | — |
| `F10l-birlesim.py` | 0 | GEÇER (birebir) → GEÇER (beklenen listeyle tam eşit) |
| `rehber_uret.pdf_tamlik_bozma` (eski PDF + eski veri) | — | 10 / 10, sentetik 11 / 11 → aynı |
| derleme (`rehber_veri`, `rehber_uret`, `rehber_gorunum`, `F10d-dogrula`) | — | hatasız → hatasız |

**`rehber_veri.py` durma koşulları, veriden benzetim** (sınandı, üretim koşmadan): yeni koşul `ALT_ADIM_NO` = `KOD_IDX` (K1 17, K2 32,
M6 sırası eşit); `demet_sema_coklu` eski verinin K1 9 şema + 7 Kablo yolu parçası ve K2 5 + 5 ile hata 0 (her biri tam bir kartta);
`kablo_sec` P03 tek maddeye (D4 0); `sema_ortulu` deseni E4 alt 4'ün bir şemasına uyuyor. Depoda `__pycache__` yok.

### 9.5 Üretimde beklenenler (ölçülmedi)

- Alt adım **71 → 91** (K1 + 12, K2 + 8; § 6'nın 88'i yerine); şema **65**, parça **1192** (değişmez); 68 / 5 / 1 aynı.
- PDF: § 6'daki tahminden 3 kart fazla, birkaç sayfa daha (sayfa ölçüt değil: taşan 0, tamlık eksik 0, yineleme 0, en küçük ≥ 8,0 pt).
- `alt_kontrol` her parça / şema tek alt adımda; `F10d-dogrula` `sema_tek` GEÇTİ; `--adimlar` yolu artık `tek_s` hatası vermez.

**Bakılacak kareler:** 17.1 (bara + yerleşim listesi, Kablo yolu 2), 17.2 (G06 "3 numaralı saplamasına"), 17.4 (Kablo yolu 3 burada;
içindeki G12'nin bara ucu 17.5'te: küçük görsel uyumsuzluk), 17.5 (Kablo yolu 4 + G16 şeması), 17.7
(Kablo yolu 9 G18), 17.9 / 17.11 / 17.12 (göndermeler), 32.1 (N3 cümlesi), 32.5 / 32.6 (N4 bölünmesi; 32.5 1085, 32.6 899 karakter),
E4 alt 4 (ekranda not, basılıda "Karede görünmez:" satırı), F1 kontrol (14,6 V ve 12,8–14,4 V çözülmüş), kart başlıklarında "17.k".

### 9.6 Açık kalanlar

- Tarayıcıda görülmedi: `app.js` E4 notu ve `yazdir.html` "Karede görünmez:" satırı (yalnız `node --check` ve denetim).
- E3a K01 etiketi, K1 mor hatlar, E4 genel bakış lejantı, "20 V aralığı" kaynağı, SV3 ucu, A4 basılı boşluklar: bu turda yok.
- N1 bara ucu olmayan kablolar için kaba kalır (onay kaydı yakalar). Kablo yolu 3'ün G12 parçası 17.4 karesinde, ucu 17.5'te.
- İkinci bağımsız bakış, ardından FreeCAD'li tam üretim (≈ 45–50 dk) ve zincir.

## 10. Düzeltme turu 2, üretim ve zincir (2026-11-16; ikinci kontrol `F10l-kontrol-2.md` DÜZELTME GEREKLİ, küçük)

Dal `lale-duzeltme`, HEAD = uzak = `1c4e882`. Saatler sistem saatinden. Geçici dosyalar oturum scratchpad'inde (`…\scratchpad\d2\`,
`…\scratchpad\u\`); depoya ve Masaüstü'ne geçici dosya düşmedi.

### 10.1 Düzeltmeler (02:33–02:38)

Değişen kaynak: `tasarim/freecad/rehber/rehber_metin.py` (D1, D2, N2), `rehber_denetim.py` (ASCII izin listesine 1 sözcük),
`rehber_kritik_onay.json` (yenilendi), `planlama/d158/F10l-birlesim.py` (beklenen liste).

- **D1 (yapıldı)**, 17.1 "Toprak ve iki bara", `rehber_metin.py` G05 cümlesinin arkasına kontrolün önerdiği cümle harfiyen:
  eski: "Toprak (G05, 12 AWG): akü − → yıldız barasının ortadaki (3.) saplaması. İki bara da …"
  → yeni: "Toprak (G05, 12 AWG): akü − → yıldız barasının ortadaki (3 numaralı) saplaması. G05'in akü ucu XT60'ın robot tarafındaki
  − ucudur (lehim): akünün kutbuna doğrudan bağlama, akü kutupları bantlı kalır (akü ile XT60'ın akü tarafı arası G01, alt adım 17.2).
  İki bara da …". Gerekçe: kart XT60'tan önce geliyor, okur G05'i akü kutbuna bağlayabilirdi. Kayıtla tutarlılık (kendim okudum):
  `kablolar.json` G05 damarı "XT60 (robot tarafı) · −" → "Yıldız barası · GND", `uc_turu.a` "lehim"; G01 "Akü · ± kutup (M5)" →
  "XT60 (akü tarafı) · ±", iki damar; "madde 1" ana hat paragrafının çapası, `_demet_bol` "alt adım 17.2" yaptı (D7 / birleşim C).
  Yan etki: "kutbuna" ASCII kalıntı denetiminin izin listesinde yoktu (ascii kalıntı 1) → `rehber_denetim.py` izin listesine eklendi
  (Türkçe harfi olmayan doğru yazım; önceki turların aynı yöntemi, gerekçe yorumu dosyada).
- **D2 (yapıldı, tek cümle)**, 17.4 "Röle K1 ve ön şarj kartı" sonuna: eski "… (röle pimlerinin yeri kablajda teyit: röle gövdesindeki
  şema)." → yeni "… gövdesindeki şema). Karede Kablo yolu 3'ün baradan sol BTS7960B'ye giden kısmı (G12) da görünür; o uç alt adım
  17.5'te bağlanır." Gerekçe: `CAD_ESLEME[3]` G12'yi içeriyor, CAD yolu tek parça; CAD etiketi "F1 20 A → röle K1 ∥ ön şarj kolu →
  anahtarlı bara (M5 saplama) → BTS7960 sol → ön sol motor" (veri `p1182`), cümle bununla uyumlu.
- **N2 (yapıldı)**, dört "N." biçimi "N numaralı" (sayı ve yer tutucu aynı):
  1. 17.1 "ortadaki ({saplama.G05}.) saplaması" → "ortadaki ({saplama.G05} numaralı) saplaması" (çözülmüş "(3.)" → "(3 numaralı)").
  2. 17.6 "yıldız barasının {saplama.G22}. saplamasına." → "… {saplama.G22} numaralı saplamasına." (çözülmüş 5). Onay kaydında bu cümle
     eskiden "}." + boşlukta ikiye bölünüyordu ("…barasının {saplama.G22}." + "saplamasına."); şimdi tek cümle.
  3. K1 kontrol "yıldızın {saplama.G05}. saplamasında" → "yıldızın {saplama.G05} numaralı saplamasında" (aynı bölünme kalktı).
  4. F1 kontrol "akü dönüşü saplamasına (3.) bağla" → "akü dönüşü saplamasına (3 numaralı) bağla" (çıplak 3 yer tutucuya çevrilmedi:
     sözcük değişikliği dar tutuldu; çıplak kritik sayı denetimi 0).
  Gerekçe: kontrolün N2'si; kritik değer aynı, denetim bozulmadı (aşağıda).
- **N3 (yapılmadı, açık madde)**: modelde bara ya da bara tutucusu parçası yok (`rehber-veri.json` 1192 parçada "bara" adlı parça yalnız
  gösterim "Kablo yolu" çizgileri); B5a parça listesi panel, XL4016 C, burçlar, ön şarj kartı, sigorta kutusu, röle, ana sigorta yuvası;
  bağlantı elemanı M3×6 / M3×8 / M4×16 + pul + naylon somun (kartlar ve yuvalar için). `kablolar.json` bara-pabuc: "Tutucunun CAD'i
  P10.7b iş maddesi". Hangi adımda, hangi elemanla takıldığı kayıtta net değil: talimat uydurulmadı, `dongu-158.md`'ye açık madde.
- **N1, N4**: dokunulmadı, açık madde.

**Onay kaydı** (`--kritik-onay-yenile`, 8 fark; kayıt kablo 165, liste 206, metin 1064 → 1064): eklenen 2 (D1, D2 cümleleri), değişen 4
(N2'nin dört cümlesi), silinen 2 (N2 2 ve 3'te eskiden bölünen "saplamasına." / "saplamasında; T8 E …" kuyrukları, metinleri değişen
cümlenin içinde). Kendi karşılaştırmam (`…\scratchpad\d2\onayfark.py`, girdi düzeyinde, yedek ↔ yeni): silinende olup eklenende olmayan
değer belirteci yalnız "(3.)" (karşılığı "(3 numaralı)", aynı saplama); eklenende fazla olan yalnız kablo kimlikleri G05, G01, G12 ve
"3 numaralı". Sigorta, kesit, uç, saplama numarası, gerilim değişmedi; uyarı silinmedi. **Kritik değer farkı 0.**

**Birleşim** (`F10l-birlesim.py`, `1c4e882`'ye karşı): beklenen eklenen 13 → 19 (D1, D2, N2 × 4), silinen 9 → 13 (N2 × 4); A K1 12, K2 8
alt adım ALT_TAM_HAM; gönderme 14 → **16** (yeni: 17.1 → 17.2 "madde 1", 17.4 → 17.5 "madde 3b"), çözülemeyen 0. GEÇER.

### 10.2 FreeCAD'siz sınamalar (02:35–02:38; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Sınama | Çıkış | § 9.4 → bugün |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel → güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 172 → aynı |
| `rehber_denetim.py --kaynak` | 0 | metin 615 → 615; ascii 0, zorunlu 0, çıplak 0, bağlam 0; onay farkı 0 (yenilemeden önce 8); D1–D7 hata 0 (K1 12 / 38 / 16, K2 8 / 18 / 10) |
| `rehber_denetim.py --bozma-denemesi` | 0 | 289 / 289 → 289 / 289 |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, onay tutuyor / 86 / 86 → aynı |
| `rehber_kablo.py --veri …` / `+ --bozma-denemesi` | 0 / 0 | GEÇER / 95 / 95 → aynı (eski veri) |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm GEÇTİ → aynı |
| `node --check rehber/app.js` | 0 | — |
| `F10l-birlesim.py` | 0 | GEÇER (14 gönderme) → GEÇER (16) |
| `rehber_uret.pdf_tamlik_bozma` (eski PDF + eski veri) | — | 10 / 10, sentetik 11 / 11 → aynı |
| derleme (`rehber_veri`, `rehber_uret`, `rehber_gorunum`, `F10d-dogrula`, `rehber_metin`, `rehber_denetim`, `rehber_deger`) | — | hatasız |

`git status --porcelain` sınamalardan önce ve sonra aynı (34 satır); depoda `__pycache__` yok.

### 10.3 Üretim, birinci koşu: çıkış 2 (02:39:13–03:22:50), neden ve dar düzeltme

Yöntem F10k "Üretim ve zincir" ile aynı: scratchpad `u\` altında `baslat.ps1` → `sarmal.ps1` (15 s bellek bekçisi, eşik 1,2 GB art arda
iki ölçüm ya da boş commit < 2 GB) → `.durum`; bekleme ön planda ≤ 170 sn'lik yoklamalarla + arka planda 110 dk'lık bekçi
(`bekci.ps1`; veri aşaması bitince kilidi bırakır). Bellek önce 3,70 GB (chrome 0), en düşük 2,32 GB; bekçi tetiklenmedi. FreeCAD kilidi
02:39 "dolu", veri aşaması (176 s) bitince 02:42:32 "boş".

`rehber_uret.py` tam koşu: **çıkış 2, 2627 s**; tek sorunlu kalem `denetim`: "zorunlu uyarı eksik 2 / 115" (K1 ve K2 "ana metin: kabuktan
önce dur …", alan `is_ana`). Geri kalan her şey geçti (ön sınama, alt adım 91 / 91, PDF 84 sayfa, tarayıcı 50 / 50, konsol 0, kablo eşleme;
sayılar 10.4'teki ikinci koşuyla aynı).

- **Neden (açık, dar; P10.7b2d-A'dan kalan, bu turun değişikliği değil):** `rehber_denetim.tutarlilik()` (veri modu) ZORUNLU_ALAN'ı
  veri adımının `A[k][alan]` alanında arıyor. `is_ana` kaynak tarafında türetilen bir alan adı (`_alan_anahtarlari`); veride böyle bir
  anahtar yok, metin boş sayıldı. Veride K1 / K2'nin ana metni adımın kendi `is_` alanı (uyarı cümleleri orada, desen tutuyor; alt adım
  metinleri `sira_grup[..]["is_"]`'te). FreeCAD'siz sınamalar yalnız kaynak modunu koştuğu için önceki turlarda görünmedi.
- **Düzeltme** (`rehber_denetim.py`, `tutarlilik`): `A.get(k, {}).get("is_" if alan == "is_ana" else alan)`. Desen ve liste aynı (onay
  kaydı etkilenmedi, fark 0).
- **Sınama:** yeni veriyle `rehber_denetim.py` (veri) zorunlu eksik 2 → **0 / 115**, çıkış 0. Bellekte üç veri bozması yakalandı: K1
  ana metinden "Bağlarken akü ayrık (XT60 açık)." silindi → 1; K2'den "F3 (kafa) takılı değil" silindi → 1; K1 uyarısı ana metinden ilk
  alt adıma taşındı → 1. FreeCAD'siz sınamaların hepsi yeniden: hepsi çıkış 0, sayılar 10.2 ile aynı (bozma 289 / 289, 172, 86 / 86,
  95 / 95; `pdf_tamlik_bozma` bu kez yeni PDF + yeni veriyle doğal 11 / 11, sentetik 11 / 11).
- Kilit dosyası yan bulgusu: bekçi betiğim BOM'suz kaydedildiği için PowerShell 5.1 "boş"u çift kodlanmış yazdı (bayt `62 6F C3 85 C5
  B8`); ikinci koşudan önce fark edildi, dosya doğru UTF-8 ile yazıldı, betik düzeltildi.

İkinci (son) koşu 03:26:45'te başladı (bellek önce 4,11 GB).

### 10.4 Üretim, ikinci koşu: çıkış 0 (03:26:45–04:10:06)

`rehber_uret.py` tam koşu: **çıkış 0, 2606 s** (b2c'de 2820 s). Bellek önce 4,11 GB, bekçinin en düşük ölçümü 2,40 GB; bekçi tetiklenmedi.
FreeCAD kilidi 03:26 "dolu", veri aşaması (166 s) bitince 03:29:50 "boş"; son hâli "boş". Kaynağa üretimden sonra dokunulmadı.

| Ölçü | Beklenen (varsayım, ölçülmedi) | Ölçülen |
| --- | --- | --- |
| ön sınama | geçer | "kaynak denetimi gecti, onay kaydi tutuyor (kablo 165, liste 206, metin 1064)" |
| alt adım | 91 | **91**, geçti 91; her parça tek alt adımda, her şema tek alt adımda (alt adımlı adımlarda 60 şema, birden çok 0, hiç 0) |
| şema / parça | 65 / 1192 | **65 / 1192** (renk 1192, CAD sırası eşleşme 1192) |
| kablo eşleme | 68 / 5 / 1 | GEÇTİ (sayılar 10.5 `rehber_kablo --veri`'de: değişmedi) |
| denetim (veri) | elektrik 0, zorunlu 0 | ASCII 0, elektrik 0, **zorunlu eksik 0 / 115** (birinci koşuda 2), yasak 0 (istisna 10) |
| sıra / giriş / uçuş / perdelenme | hata 0 | 565 bağlantı ulaşılamaz 0; girilemez 0; uçuş 340 satır, çarpışan 0, istisna 16; ısıl gömme hata 0; perdelenme gerekçesiz 0, istisna 117 |
| kol kablo | 38 bölüm | 38 bölüm, GEÇTİ |
| yazdırma kareleri | — | 50 adım + 91 alt adım = 141 kare, piksel denetimi 141 / 141, boş yok |
| PDF | taşan 0, tamlık eksik 0, en küçük ≥ 8,0 pt | **84 sayfa** (adım 50 + devam 34; `1c4e882` 80), eşleme tutarlı, **taşan yok**, en küçük yazı DOM / PDF **8,1 pt**, 18563 kB |
| PDF tamlık | eksik 0, yineleme 0 | 50 adım, `is_` 20391 karakter (K1 / K2 ana metni artık yalnız başlık paragrafı; önce 32017), eksik 0; madde 436 (önce 416), eksik 0; yineleme 0 |
| tarayıcı | 50 / 50, konsol 0 | 50 geçti, konsol hatası 0, ek kontrol sorunlu "-" |
| telefon 360 px | taşma 0 | 7 adreste 360 / 0 |

PDF sayfa eşlemesi (`1c4e882` ↔ yeni; `…\scratchpad\u\pdfD.py`): sayfa sayısı değişen yalnız K1 (4 → 6 sayfa, s. 19–24) ve K2 (2 → 4,
s. 44–47); ilk kayan adım 17. Metni değişen adımlar B6a, K1, K2, F1, F5. Bütün PDF'te çözülmemiş yer tutucu (`{…}`, `⟦`, `⟧`) 0; her
hedef sayfada en küçük yazı 8,1 pt (resim altı / rozet); gövde: K1 s. 20 9,6, s. 21 9,0, s. 22 9,3, s. 23 8,8, s. 24 9,1; K2 s. 45 9,49,
s. 46 9,4, s. 47 9,6; F1 s. 50 9,49. FreeCAD'in Python'u `-B`'ye karşın dört `__pycache__` yazdı (önceki paketler gibi; sonda silindi).

### 10.5 Zincir (04:10:31–04:58:44; F10h § 9 2–10, b2c'deki komutların aynısı, tek sarmalayıcı altında)

`.durum`: "BITTI cikis 0 sure 2895 enaz 1.42" (bekçi tetiklenmedi; en düşük 1,42 GB F10d'de, 04:50).

| Sıra | Komut | Çıkış | Süre (s) | Beklenen | Ölçülen |
| --- | --- | --- | --- | --- | --- |
| 2 | `rehber_kablo.py --veri …` | 0 | 1 | GEÇER | SONUÇ GEÇER; yol çizimi 68 (CAD 39, kol 6, şema 29) · bağlantı tablosu 5 (I01, I02, P01, P02, P03) · hiçbiri 1 (G06); ayırt edilemeyen 0; onay tutuyor; eşlemesiz 0 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 23 | 95 / 95 | **95 / 95** |
| 3 | `rehber_denetim.py` (veri) | 0 | 1 | elektrik / yasak / zorunlu 0 | ASCII 0, elektrik 0, zorunlu eksik 0 / 115, yasak 0 (istisna 10) |
| 4 | `F10f-dogrula.py` | 0 | 577 | GEÇTİ | GEÇTİ (veri, sınama, kablo kare, sağ / sol, mini etiket; parça kare "None" önceki gibi) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | 966 | `renk_demo` önceki gibi | GEÇTİ; `renk_demo` KALDI (bilinen karar); işaret 1284 / 1284 |
| 6 | `F10d-dogrula.py --goruntu-yok` | 0 | 871 | GEÇTİ, `sema_tek` | GEÇTİ; konum **141** (50 + 91), 141 / 141 eşit; masa yabancı şema 0; 360 px taşma 0; **`sema_tek`: 60 şema, birden çok 0, hiç 0** (piksel 0 olanlar bilgi, önceki gibi) |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | 450 | GEÇTİ | GEÇTİ; seçim 6 / 6, yazdırma kareleri 50 / 50, PDF görüntü 141, boş sayfa yok, dış istek 0, konsol 0, 360 px taşma 0 ("veri değişti", bilgi) |
| 8 | `F9b-dogrula.py` | 0 | 5 | GEÇER | GEÇER, konsol 0, 360 px taşma yok |
| 9 | `carpisma_kos.py kontrol` | 0 | 0 | 17 dosya aynı | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 10 | `regresyon.py --yazma` | 0 | 0 | aynı | GEÇER, kötüleşen yok |

Zincir PDF'i, `kontrol.json`'u ve veriyi değiştirmedi (SHA-256 önce / sonra aynı). Zincirin yazdığı: `planlama/d158/F10{a,d,e,f}-dogrula.json`.
Paket dışı 18 dosyanın (13 kabuk görseli, `yerlesim-kontrol.json`, kökteki `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`,
`gez.js`, `uc.js`) SHA-1'i üretimden önceki kayıtla aynı: üretim ve zincir onları yazmadı.

**Beklenen ↔ ölçülen (brief'in varsayımları):** alt adım 91 ↔ 91; şema 65 ↔ 65; parça 1192 ↔ 1192; çizilen 68 / 5 / 1 ↔ 68 / 5 / 1;
taşan 0 ↔ 0; tamlık eksik 0 ↔ 0; en küçük yazı ≥ 8,0 ↔ 8,1 pt; `sema_tek` GEÇTİ ↔ GEÇTİ. PDF sayfası (ölçüt değil) 84.

### 10.6 Kare bakışı (04:15–05:05; ekran: kendi başsız Chrome'um, 1400 × 900, iki tema; basılı: PyMuPDF 110 dpi)

Ekran: 17.1–17.12 ve 32.1–32.8 açık temada üretimin kendi ekran kareleri (`planlama/rehber/goruntu/adim-17-NN.png`, `adim-32-NN.png`) ve
kendi çekimim; koyu tema kendi çekimim (`…\scratchpad\u\kare\`, 47 adres kaydı; panel yer tutucu 0, panel taşması 0). Basılı: K1
s. 19–24, K2 s. 44–47, E4 s. 39–43, F1 s. 48–53, B6a s. 15–16 (PNG + metin). Gözle baktığım: ekran 32 kare (açık 24 + koyu 8, temas
sayfaları), basılı 7 sayfa (s. 20, 21, 22, 23, 42, 45, 46, 50); öbür basılı sayfalar yalnız metinden.

| Kare | Hüküm | Neden |
| --- | --- | --- |
| **32.2 Kafa servoları, hat C** | **anlaşılmıyor** | Kadraj direk tepesine (R62 halkası, y 1210–1330) çok yakın; karede yalnız gri parçalar var, "Karede: Kablo: Servo gücü 6 V (sarı)" yazıyor ama sarı kablo hiç görünmüyor (ekran açık / koyu ve basılı s. 45 aynı). Metin tek başına yeterli, kare yanlış bilgi vermiyor ama hiçbir şey göstermiyor |
| 17.1 Toprak ve iki bara | zor | Karede yalnız kısa bir siyah (koyu temada açık gri) G05 parçası ve havada bitiyor: baralar modelde yok (N3). Metin açık, D1 cümlesi kartta (ekran ve basılı s. 21) |
| 17.2 Ana hat ve şarj kolu | açık | Kablo yolu 1 kırmızı, net |
| 17.3 Akü ölçüm teli (G07) | açık | Mor G07 tek başına net |
| 17.4 Röle K1 ve ön şarj kartı | zor | Kablo yolu 3 turuncu parçaları dağınık (plaka altından geçiyor); D2 cümlesi kartta; seçim etiketi "Kablo yolu 3 … → BTS7960 sol … / G12" |
| 17.5 Bara çıkışları | zor | Geniş kadraj, Kablo yolu 4 + G16 turuncu çizgileri ince ve küçük (basılı s. 23'te zor seçiliyor) |
| 17.6 PC817 #2 algı teli (G22) | açık | Turuncu G22 şeması büyük ve net |
| 17.7 Sigorta kutusu çıkışları | açık | Kablo yolu 9 kırmızı net |
| 17.8 Acil stop ve röle sürücüleri | açık | Yeşil hatlar net |
| 17.9 Alt kat kartlarının öbür uçları | açık | Mavi G19 net |
| 17.10 Enkoder, BTS sinyal ve sonar | zor | Bilinen "K1 mor hatlar": altı mor hat iç içe |
| 17.11 Direğe çıkan hatların taban kısmı | açık | Karede yeni öğe yok (bütün robot); P03 bağlantı tablosu yalnız bu kartta (basılı s. 24) |
| 17.12 Son kontrol | açık | Genel kare, metin göndermeleri "alt adım 17.k" |
| 32.1 Kol servo uzatmaları | zor | Bütün robot kadrajı, sarı uzatmalar tabanda küçük; N3 cümlesi kartta |
| 32.3 Kafa 12 V | açık | İnce kırmızı hat direk boyunca izleniyor |
| 32.4 ESP32 USB | zor | Mor + gri USB hattı uzun kadrajda ince |
| 32.5 Boyun demeti: tünelden geçirme | açık | HDMI mavi, USB / ses boyunda görünüyor |
| 32.6 Kafa uçları, hoparlör, inenler | zor | Karede yeni öğe yok (N4), "Karede:" satırı yok; iş tamamen metinde |
| 32.7 Göğüs ekranı 12 V | açık | Kırmızı G20 / G21 görünüyor |
| 32.8 Son kontrol | açık | Genel kare |
| E4 alt 4 (31.4) | açık | Ekranda lejantta "Ses kablosu (AU1, AU2): sol arka kabuğun arkasında kalır (görünümü döndür)", iki temada; basılı s. 42'de "Karede görünmez: Ses kablosu (AU1, AU2): sol arka kabuğun arkasında kalır" |
| F1 kontrol | açık | Basılı s. 50: "akü en çok 14,6 V", "(12,8–14,4 V)", "akü dönüşü saplamasına (3 numaralı)" |
| B6a | açık | Basılı s. 16: "Bu dört satır … bağlantı tablosudur, 3B çizim değil" satırlardan önce |

Sayım (23 kare): açık 15, zor 7 (17.1, 17.4, 17.5, 17.10, 32.1, 32.4, 32.6), anlaşılmıyor 1 (32.2). Yanlış bilgi veren kare
bulmadım. K1 / K2 ilk basılı sayfası (s. 19, s. 44): ana metin + "Bu adımda yeni parça yok."; kart başlıklarında "17.k" / "32.k".

### 10.7 Açık kalanlar

- **32.2 karesi** (anlaşılmıyor): kadraj kabloyu göstermiyor; düzeltmeye girişilmedi (ayrı kare incelemesine).
- **N3** (bara tutucusu hiçbir adımda panele takılmıyor; modelde bara / tutucu parçası yok) → `dongu-158.md` açık madde.
- **N1** (D6 / D7 çifte bağlatmayı yalnız beyan düzeyinde yakalar; asıl dayanak onay kaydı), **N4** (32.6'da karede yeni öğe yok):
  dokunulmadı, açık madde.
- Zor kareler (17.1, 17.4, 17.5, 17.10, 32.1, 32.4, 32.6) ve önceki paketten süren E3a K01, K1 mor hatlar, SV3 ucu, "20 V aralığı" kaynağı,
  A4 basılı boşluklar.
- `rehber_denetim.tutarlilik` veri modu düzeltmesinin kalıcı bozma denemesi yok (bellekte üç bozmayla sınandı, 10.3).
