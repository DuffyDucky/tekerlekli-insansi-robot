# Kablolama ön kararları (P10.7): üçüncü (son) bağımsız bakış, 14.11.2026 (03:04)

Kontrol edilen (HEAD `b1c2a8d`, çalışma ağacı): `planlama/adim3/kablolama-on-kararlar.md` (**R**), `planlama/adim3/pin-haritasi.md` sürüm 4 +
14.11 düzeltmesi (**PH**), `planlama/adim3/elektrik.md` (**EL**), `planlama/d158/karar-kuyrugu.md` (**KK**), `planlama/d158/kablolama-onkarar-gunluk.md`
(**G**), `planlama/d158/pin-karari-gunluk.md` (fark), ikinci kontrol `kablolama-onkarar-kontrol-2.md` (**K2R**), Efe'ye pano taslağı (depo dışı)
ve pano #8 mesaj #24'ün gönderilen gövdesinin depo dışı kopyası. Karşılaştırma: `planlama/maliyet.json` (**MJ**), `planlama/dongu-158.md`.
Panoya yazılmadı, pano okuma komutu koşulmadı. FreeCAD ve rehber / doğrulama betikleri koşulmadı. Hesaplar elle ve depo dışı küçük iki betikle
(BJT hesabı; pin tablosu karşılaştırması `git show b1c2a8d:` ile); hiçbir şey ölçülmedi. Depoda bu dosya dışında hiçbir şey değişmedi.

**Bu bakışta açılan veri sayfaları (önceki ajanlarınkine dayanılmadı):**
- Vishay *BC337 / BC338*, Doc. 85112 Rev. 1.2 (02-Nov-04): hFE tablosu, ICES, VEBO, ayak çizimi (sayfa 1).
- onsemi *BC337/D* Rev. 8 (Kasım 2013; Farnell kopyası): hFE tablosu, TO-92 CASE 29 STYLE 17 ayak dizilişi.
- Diotec *BC337 … BC338* (2017-02-09): hFE tablosu (grup bazında 300 mA değeri), ayak çizimi.
- DC Components *BC337* (Rapid kopyası) ve Lumimax *BC337/BC338* Rev 1.3 (Digi-Key kopyası): hFE(2) satırı, ayak dizilişi.
- Espressif *ESP32 Series Datasheet* v5.3: Tablo 5-3 (VOH, IOH, RPU / RPD) ve IO_MUX not 8 (sürüş kademeleri).
- Meishuo *MAH3* 40A / 60A otomotiv rölesi, Schedule 1 "COIL DATA (23 °C)".
- Hongfa tabanlı *JQC-3FF* veri sayfası (satıcı Direnc.net'in barındırdığı kopya), "COIL DATA".

## Hüküm: **GEÇER** (kayıtlı açık işlerle)

Düzeltme turu 2'nin asıl değişikliği doğru: **taban → GND 2,2 kΩ ile kapalı hâl veri sayfasıyla güvenli** (K2 bobini en kötü köşede bile
mV mertebesinde, bırakma garantisi 1,2 V). Açık hâlde röle en kötü köşede de **çeker** ve transistör sınırlarının içinde kalır. 270 Ω /
2,2 kΩ / BC337-40 değerleri bütün belgelerde aynı; pin tablosu HEAD ile aynı. K14 riski proje sahibinin anlayacağı açıklıkta yazılmış.

Kablajı değiştiren bulgu yok. Bir bulgu (A1) röleyle ilgili olduğu için ayrıca gerekçelendirildi: belgede yazan "≈ 3,9 kat aşırı sürüş"
sayısı satın alınacak üreticinin veri sayfasında garanti değil. Bu sayı düzeltildiğinde bile röle çekiyor, transistör sınırların içinde
kalıyor ve kapalı hâl değişmiyor. Bu yüzden A1 metin düzeltmesi olarak C adımına gider. Orkestratör "röleyle ilgili her bulgu durdurur"
kuralını harfiyen uygularsa A1 tek durduran bulgu olur. O durumda da düzeltme yalnız metindir; değer ve kablaj değişmez.

## Bulgular (önem sırasıyla; hepsi kayıtlı açık iş, C adımında metin)

### A1 · "hFE en az ≈ 170 @ 300 mA → ≈ 3,9 kat aşırı sürüş" satın alınacak parçanın veri sayfasında garanti değil; "VCE en kötü 0,7 V" bir sınır değil (röle sürücüsü) — durdurmaz, C'de metin

- **Nerede:** PH:37 (BJT kaynak satırı), PH:302 (D9 "-16 sınıfında hFE 300 mA'de en az 60 olabilir"), PH:321-327 (D9 zorunlu β ve VCE(sat)),
  R:278, R:280, R:284-285, EL:268 ("hFE en az ≈ 170 @ 300 mA"), G §7.2.
- **Kaynak:**
  - Vishay 85112: 300 mA'deki 170 yalnız **BC338-40** satırında (ajan "vekil" demiş, doğru).
  - Diotec: grup -40 için BC337 ve BC338'e birlikte **300 mA'de en az 170**.
  - **onsemi BC337/D Rev. 8:** 300 mA, VCE 1 V'ta **bütün gruplar için tek değer: en az 60**. Lumimax'ta da 60, DC Components'ta **40**.
  - Malzeme satırı "Direnc.net **BC337-40TA**". "-40TA" ekli ad onsemi / Fairchild'in ammo paket adlandırmasıdır (çıkarım, satıcı
    sayfası bu bakışta okunmadı). O üreticinin garantisi 300 mA'de **60**; yani "-16'da 60 olabilir, -40'ta 170" ayrımı bu parça için
    belgeyle desteklenmiyor.
- **Hesabım (betik):**
  - Gereken β: I_B en kötü 4,79 mA (doğru: (2,64 − 1,2)/270 − 1,2/2200; 2,2 kΩ'un çaldığı 0,55 mA dahil). Bobin akımı 0,191 / 0,210 A.
    Gereken (zorunlu) β = 39,9 / 43,8 (doğru).
  - hFE en az 60 ise: VCE = 1 V'ta taşınabilen akım ≥ 60 × 4,79 = **287 mA > 210 mA**, pay **1,37×** (3,9× değil). Kazanç 100 mA'den 300 mA'e
    tekdüze düşüyorsa 210 mA'de de ≥ 60; log-log ara değer ≈ 95. DC Components'ın 40'ı için ara değer ≈ 73: yine yeterli.
  - **Sonuç:** veri sayfası VCE < 1 V'u garanti eder, **VCE ≤ 0,3 V'u hiçbir üretici garanti etmez.** VCE(sat) ≤ 0,7 V değeri β = 10'da
    tanımlı; β ≈ 44'te sınır değildir. hFE değerleri VCE = 1 V'ta verilir, doyum kazancı değildir. PH:326'daki "Hesap en kötü 0,7 V ile"
    bu yüzden en kötü değil; belgeyle savunulabilir sınır **1,0 V**.
- **Güvenlik sonucu değişmiyor mu? (sınadım):**
  - **Çekme:** VCE ≤ 1,0 V ile K1 bobini bara 11 V'ta 10,0 V, 10 V'ta (akü bölücüsünün alt sınırı, EL:234) 9,0 V görür. Çekme garantisi
    8,4 V (MAH3, 23 °C). K2'de β 9,4 < 10 olduğundan veri sayfasının doyum koşuluna yakın, sorun yok.
  - **Kayıp:** 0,21 A × 1,0 V ≈ 0,21 W (+ taban 6 mW). 200 °C/W ile 60 °C ortamda Tj ≈ 103 °C < 150 °C; 0,45 W izninin içinde.
  - **Kapalı hâl:** etkilenmez.
  - **Daha iyisi var mı:** 220 Ω yedeği de (β 35) doyumu belgeyle garanti etmez. β ≤ 10–20'yi garanti etmek 10–20 mA taban akımı ister,
    yani 10 mA GPIO hedefini aşar. Doğru yaklaşım bugünkü gibi T2 (g)'de **VCE ≤ 0,3 V'u ölçerek kabul** etmek. Ölçüt ve 220 Ω yedeği yerinde.
- **Önerilen düzeltme (C, yalnız metin):**
  1. PH D9, R §9, EL:268: "hFE en az 250 @ 100 mA (bütün üreticiler). 300 mA'de üreticiye göre 60 (onsemi, Lumimax) – 170 (Diotec);
     satın alınacak BC337-40TA onsemi adlandırması: 60. VCE < 1 V belgeyle garanti, VCE(sat) ölçülür (T2 g)."
  2. "≈ 3,9 kat" → "belgeyle ≥ 1,4 kat (VCE 1 V'ta); tipik eğrilerle doymuş".
  3. "VCE en kötü 0,7 V" → "belgeye göre ≤ 1,0 V: bobin 11 V'ta ≥ 10,0 V, 10 V'ta ≥ 9,0 V; kayıp ≤ 0,22 W".
  4. PH:302 ve R:284'teki "-16 sınıfında 60 olabilir" → "-40 sınıfı 100 mA'de 250 garanti eder; 300 mA değeri üreticiye göre". **-40
     şartı yine doğru**: 100 mA'deki garanti (250 / 100) ve tipik doyum için.

### A2 · K14'ün "siparişten önce baskı parçalarında elle fiş denemesi" adımı takvimle çakışıyor; adımın nasıl yapılacağı yazılı değil — durdurmaz

- **Nerede:** R:145-146, R:157-160, KT4 (R:364), EL:37, EL:518, KK K14, MJ:137 / :191.
- **Sorun:** deneme hem basılmış servo yuvası ile mili hem de denenecek fişi ister. Sipariş günü 16.11 kayıtlı (`dongu-158.md:348`,
  F8a satırı). Depoda bu parçaların basıldığına dair kayıt bulmadım. Bu durumda "siparişten önce zorunlu" adım ya siparişi bekletir ya da
  atlanır; ikisi de yazılı değil. Ayrıca denenecek fiş nereden gelecek, yazılı değil (yeni kablo sipariş edilmeden elde yok).
- **Önerilen (C, metin):**
  - (a) Deneme için yalnız tünel kesitini (20 × 7,8 mm, ≈ 34 mm boy, iki dik dönüş, mil penceresi 20 × 10) taşıyan küçük bir **deneme
    parçası** basılır. Ya da baskı parçaları hazır değilse kumpasla fiş seçilir, elle deneme teslimde yapılır.
  - (b) Denenecek fiş: evdeki herhangi bir USB 2.0 A erkek ve micro HDMI kablo.
  - (c) Deneme 16.11'e yetişmezse: USB 2.0 uzatma (ucuz kalem) şartla sipariş edilir; geçmezse yedek yol (yeniden sonlandırma) zaten tanımlı.
- **Risk bölümünün açıklığı (Madde 4 cevabı):** R:157-160 ve R §14 proje sahibinin anlayacağı dilde ve doğru. Kablo şartı somut (USB 2.0;
  erkek fiş ≤ 13 × 7 mm; HDMI Ø ≤ 6; micro HDMI ≤ 7 × 18 mm, boy ≲ 30 mm). Yedek yollar gerçekçi: USB 2.0'da dört damar yeniden
  sonlandırılabilir; şerit HDMI kafa ekranında zaten kullanılıyor (EL:57). Şerit HDMI'nin 1 m'de 1080p vermesi KT4 masa denemesine bağlı,
  yazılı. Eksik olan yalnız yukarıdaki zamanlama.

### A3 · T2a ölçütü ve ters takma açıklaması kısmen yanlış; ayak sırası doğrulandı — durdurmaz

- **Ayak sırası (veri sayfalarından):** Vishay (pin 1 = C, 2 = B, 3 = E), onsemi (STYLE 17: 1 Collector, 2 Base, 3 Emitter), Diotec (önden
  görünüş "C B E"), DC Components (1 = C, 2 = B, 3 = E). **Düz yüz önde, ayaklar aşağıda, soldan sağa C-B-E**: dört üreticide aynı.
  K2R'nin "Vishay çizimi E-B-C numaralı" ifadesi (K2R:74) yanlış okuma; Vishay çizimi de C-B-E. T2a'nın diyot testi her durumda doğru ve
  güvenli bir ön adım (lehimlemeden önce, kart bağlanmadan).
- **Ölçüt sorunu (PH:377, R:287):** "hFE soketinde ≥ 250 (doğru yönde 250–630)". Veri sayfasındaki 250–630 değeri **IC = 100 mA'de**
  tanımlı; multimetre soketi µA–mA düzeyinde ölçer. O akımda veri sayfasında alt sınır yok, yani sağlam bir parça haksız yere
  reddedilebilir. Öneri: "doğru yönde yüzler (≈ 100'ün üstü), ters yönde onlar; sınıfı gövde yazısı belirler". İkinci yol:
  diyot kademesinde B–E düşümü B–C'den birkaç mV büyüktür.
- **Ters takma açıklaması (PH:377, R:288):** "GPIO'ya ≈ 10–25 mA itilebilir" tutmuyor. C ↔ E ters takılınca fiziksel kollektör GND'de
  olur: E–B jonksiyonu delinince akım B–C jonksiyonundan GND'ye akar, taban düğümü ≈ 0,6–0,7 V'ta kenetlenir. Pine giden akım
  ≈ 0,7 / 270 ≈ **2–3 mA** (hesap). Asıl risk bobin akımı: K1'de (14,6 − ≈ 8 − 0,7)/85 ≈ 70 mA (delinme gerilimi tipik değer,
  doğrulanmadı). Cümlenin sonucu ("takmadan önce kontrol") doğru, yalnız sayı yanlış. C'de tek cümle; ayak sırası T2a'ya eklenebilir.

### A4 · T2 osiloskop yolunda "bara" iki anlamda kullanılıyor — durdurmaz

- **Nerede:** PH:378 T2: "bara (bobin gerilimi = bara − kollektör)" ve (g) "bara 11 V ve 14,6 V'ta"; aynı satırda "kontak çıkışı (bara ya da
  PC817 #2)".
- **Sorun:** projede "bara" anahtarlı bara demek (K1 sonrası). Bobin (+) ucu ise F5 → mantar NC hattıdır. K1 açıkken anahtarlı bara 0 V
  olur; "bara − kollektör" farkını anahtarlı baradan alan kişi anlamsız bir değer okur.
- **Düzeltme:** C'de "bara" → "bobin (+) ucu (F5 → mantar NC sonrası)" ve (g) için "besleme 11 V / 14,6 V". Multimetre yolu ("bobin uçları
  arası") zaten açık.
- **Not:** "F5 normal kullanımda takılmaz" (Kalmazsa sütunu) eski T2'den kalma. Anlamı "sorun giderilene dek F5 takılmaz". Yeni T2'de F5
  zaten takılı olduğu için cümle karışık okunuyor; "sorun giderilene dek robot devreye alınmaz" denebilir.

### A5 · Pano taslağı: iki küçük doğruluk sorunu — durdurmaz

- **Sorun 1:** taslağın başlığında "Kararlar iki kontrolden geçti, üçüncü bakış bekliyor" yazıyor. İki kontrol de **DÜZELTME GEREKLİ** dedi.
  Doğrusu "iki kontrolün düzeltmeleri işlendi". Gövdede "karar verdik, üçüncü bakış bekliyor" var; bu bakış geçince C'de "karar verdik"
  olarak güncellenmeli (G §7.5 madde 6'ya eklenmeli).
- **Sorun 2:** taslağın 5. maddesi #24'teki "gate pull-down 4,7 kΩ / AO3400A / osiloskopla gate ölçümü" ifadelerinin geçersiz olduğunu
  dolaylı söylüyor ("MOSFET'ten BC337'ye döndü", "taban → GND 2,2 kΩ", "T2'nin yöntemi değişti"). Önerim: tek yan cümle, "#24'teki 4,7 kΩ
  gate / AO3400A yerine". Bir de `pinler.json` önerisinin `surum` 4 olduğu ve yalnız ROLE_K1 / K2 `uc` / `donanim` alanlarının değiştiği.
  Efe dosyayı açacak.
- **Madde 6 cevabı:** Efe kendi tarafını tek başına okuyunca neyin değiştiğini (BJT, 2,2 kΩ, T2 yöntemi, sürüş gücü kademesi ≥ 2), hangi
  kararların verildiğini (K1, K10 = PAM Pi düşürücüsünden, K14, ses, hub, reset teli yok) ve kendisine sorulanları anlıyor. Sorular: 16 kHz /
  firmware ve reset (a) / (b). Bunlar Efe'nin cevaplayabileceği, belgeden çıkmayan sorular. #24 ile çelişki yok: #24 sürüm 3'ü anlatıyordu,
  taslak değişikliği açıkça söylüyor. Firmware kuralları (Y1–Y13, `arm` dizisi) aynı. Protokol başlığı (konu, durum "soru", bekleyen
  "efe") ve "Ahmet onayıyla gönderilir" kaydı var. Kişisel veri / takma ad / yerel yol yok. K11 (acil stopta göğüs ekranı açık) taslakta
  yok; yazılımı etkilemediği için gerekmez, istenirse bir cümle.

### A6 · Sıcak bobinde çekme gerilimi (bilgi; iki kontrol de değinmedi) — durdurmaz

MAH3'ün "çekme ≤ 8,4 V" değeri 23 °C'de tanımlı. Bakır bobin ısındıkça direnç, dolayısıyla çekme gerilimi yaklaşık %0,39 / K artar
(genel değer): 60 °C bobinde ≈ 9,6 V, 80 °C'de ≈ 10,3 V (hesap). K1 saatlerce çekili kalıp bırakılır ve hemen yeniden devreye alınırsa,
akü 10–11 V'a inmişken röle çekmeyebilir. Bu, güvenli yöne düşen bir arızadır (bara gelmez, Y4 "5 LOW değil" hatası verir). Sürücüden
bağımsızdır, MOSFET'te de aynıdır. T2 (g) soğuk bobinle yapılır. Önerim: C'de PH T2'ye ya da EL E3'e bir cümle: "uzun çalışmadan hemen
sonra düşük akü gerilimiyle devreye almada çekmeme olasılığı; Y4 hata yolu bunu yakalar".

### A7 · Küçük kayıt notları — durdurmaz

- PH:26 / PH:314: ESP32 Tablo 5-3'teki IOH 40 mA **tipik** sütunda. Not 2'ye göre aynı alandan akım veren pin sayısı arttıkça ≈ 29 mA'e
  iner. 10–13 mA için fark etmez; "40 mA'e kadar tanımlı" ifadesi "tipik 40 mA (en yüksek kademe)" olmalı. IO_MUX not 8 kademeleri
  ≈ 5 / 10 / 20 / 40 mA ve varsayılanı 2 olarak doğruluyor (R:292'deki "bu turda kaynaktan okunmadı" kapanabilir).
- PH:25 RÖ satırı "ikinci elden" diyor. Bu bakışta iki röle verisi de üretici tablosundan doğrulandı: MAH3 12 V satırı ≤ 8,4 / ≥ 1,2 / 85 Ω
  ±%10 / ≈ 1,7 W; JQC-3FF 12 V satırı 9,00 / 1,2 / 400 Ω ±%10, en çok 15,6 V (25 °C). C'de "ikinci elden" kaldırılabilir. K1'in kendi
  satıcı adı MAH-112-C-4; MAH3 kardeş tablo olarak kalır.
- EL:390 "röle bobini 0,15 A × 12,8 V = 1,9 W" ifadesi eski (MAH3 ≈ 1,7 W, 12,8 V'ta ≈ 0,15 A doğru, çarpım 1,9 W). Bu paketten eski,
  bilgi.
- K2R:74 "Vishay çizimi E-B-C" yanlış (A3). K2R depoya girecek; bu dosya onu düzeltir.

## Madde 1 · Röle sürücüsü, baştan hesap (betik; veri sayfaları yukarıda)

| Büyüklük | Benim değerim | Ajanın değeri | Not |
|---|---|---|---|
| Boşta taban (45 kΩ, 3,3 V / 30 kΩ, 3,6 V; 270 Ω dahil) | 0,153 / 0,244 V | 0,154 / 0,246 V | aynı |
| 70 °C kollektör, taban 0,244 V; V₁(25 °C) 0,60 / 0,55 V | 0,12 / 0,67 µA | 0,13–0,72 µA | aynı. V₁ = 0,45 V gibi aşırı kötümser varsayımda bile 20 µA → K2 bobini 8,7 mV |
| Bobin gerilimi kapalı, en kötü | K2 ≤ 0,3 mV (model), ICES 10 µA sınırıyla ≤ 4,4 mV | aynı | bırakma garantisi 1,2 V (MAH3, JQC-3FF; üreticiden doğrulandı): pay ≥ 270× |
| I_B en kötü / VBE 1,0 / 0,85 / tipik | 4,79 / 5,62 / 6,24 / 8,90 mA | aynı | 2,2 kΩ payı (−0,55 mA) dahil |
| GPIO en çok 3,3 / 3,6 V | 9,81 / 10,93 mA | 9,8 / 10,9 | aynı; varsayılan kademe 2 (≈ 20 mA) içinde |
| 220 Ω yedeği | I_B 6,00 mA; GPIO 12,05 / 13,41 mA | aynı | aynı |
| K1 bobin akımı | 0,191 A; soğuk 0,210 A | aynı | MAH3 85 Ω ±%10 doğrulandı |
| Zorunlu β K1 / K2 | 39,9 / 43,8; 8,6 / 9,4 | aynı | – |
| Aşırı sürüş | belgeyle ≥ 1,37× (onsemi 60); Diotec ile 3,9× | ≈ 3,9× | **A1** |
| VCE en kötü (belge) | < 1,0 V | "0,7 V" | **A1**; bobin 11 V'ta ≥ 10,0 V |
| K1 kaybı en kötü | ≤ 0,22 W, Tj ≈ 103 °C (60 °C ortam) | 147 mW | **A1**; 0,45 W izninin içinde |

- **Kapalı hâl (soru 1):** dahili pull-up açık, 2,2 kΩ, 70 °C: bobin gerilimi bırakma garantisinin binde birkaçı. Doğru ölçüt kullanılmış
  (bırakma gerilimi). Sonuç sağlam: belirsiz parametreleri çok kötümser alsam da mV mertebesinde kalıyor.
- **Açık hâl:** düşük VOH (2,64 V), en yüksek VBE (1,2 V), soğuk bobin ve en düşük belgelenmiş hFE köşesinde röle kesin çekiyor.
  Transistörün **doyumu** ise belgeyle değil, T2 (g)'nin VCE ≤ 0,3 V ölçümüyle kabul ediliyor (A1). "hFE ≈ 170" Vishay'de yalnız
  BC338-40, IC 300 mA, VCE 1 V koşulu. Bu bir doğrusal bölge kazancı; doyum payı için doğru değer değil.
- **Bırakma, geri tepme:** 1N4007 bobine ters paralel, kollektör en çok ≈ 15,6 V < VCEO 45 V (doğru). VEBO 5 V yalnız ters takmada aşılır (A3).

## Madde 2 · Tutarlılık

- **Değerler:** 270 Ω seri + 2,2 kΩ taban → GND + BC337-40 + 1N4007 şu yerlerde aynı: PH (başlık :7-8, röle kuralı :19, satır 4 :94 ve
  19 :95, §3.1 :182 ve :199-202, §4 :228-229 ve :242, D1 :294, D9 :302, D1 / D9 hesabı, T2 :378, JSON :424-425), EL (E3 :251 ve :259,
  :268, E9 :443-444 ve :446, pin satırları :483-484, :143, :306, :339), R (§0 :24, §9, §13 KT7, §15), KK (K58 :1128, :1134-1137, iş maddesi
  :1223-1226) ve pano taslağı (madde 5).
- **Kalıntı taraması:** "4,7 kΩ", "gate", "MOSFET", "AO3400A", "IRLML", "IRLZ", "220 Ω", "çekme akımı / katı" aranıp her eşleşme okundu.
  Kalanların hepsi ya tarihçe olarak işaretli (PH:4-8, :38 "sürüm 3; kullanılmıyor", :43 MJ:106 "bugün IRLZ44N", :47, :294 değişiklik
  tarihçesi, :311 "4,7 kΩ ile bunlar …'tu", :335, :337-339; EL:106 tarihçe sütunu, :259 tarihçe; R:267-268; `pin-karari-gunluk.md` eski
  bölümleri), ya da başka devrelerin değeri (sonar 4,7 kΩ / 10 kΩ, EN 10 kΩ, ses bölücüsü 10 kΩ / 2,2 kΩ). 220 Ω yalnız yedek olarak
  geçiyor. "Çekme akımının katı" ölçütü yalnız "geçerli değildi" diye anılıyor (PH:331-332). Kalıntı yok.
- **Pin tablosu (kendi betiğim, `git show b1c2a8d:` ile):**
  - PH §2: 28 satır, GPIO / yön / işlev **aynı**. Değişen yalnız 4 ve 19 satırlarının "bağlı parça" ve "donanım şartı" sütunları.
  - JSON: 24 pin + "bos" 12 = 25. `gpio` / `yon` aynı; değişen yalnız `surum` 3 → 4 ve ROLE_K1 / K2'nin `uc` / `donanim` alanları;
    `tarih`, `kaynak`, `cekirdek`, `kart`, `bos`, `i2c`, `pca9685_kanallar` aynı.
  - EL pin planı: değişen yalnız 4 ve 19'un işlev parantezi ve not sütunu.
  - Çalışma ağacında PH tablo ↔ JSON ↔ EL aynı 25 pin, aynı işlevler. **Ajanın "25 pin, üç yerde aynı" iddiası doğru.**
- **KK:** K1 / K10 / K11 / K14 Durum ve özet satırları "karar verildi, üçüncü bakış bekliyor". Sayım :75 "Açık: 50 … Kapandı: 8" değişmemiş
  (doğru, kapanış C'de). K56 / K57 / P10.5b'de fark yok. K58'de yalnız donanım / açık kalan / not / iş maddesi satırları değişmiş.

## Madde 3 · T2 / T2a

- **Yapılabilir ve sırası güvenli:** T2a lehimlemeden önce yapılıyor. T2 bütün durumlarda F5 takılı, bara yüksüz (BTS ve XL girişleri
  ayrık), akım sınırlı kaynakla. Röle istemeden çekerse yalnız yüksüz bara gerilimlenir.
- **Ölçütler sayısal:** kontak hiç kapanmıyor; bobin ≤ 0,12 V; çekişte VCE ≤ 0,3 V; 40 / 40 çek-bırak; bobin dirençleri 85 / 400 Ω ±%10.
  Tek eksik "bara" sözcüğü (A4).
- **Osiloskopsuz yol duruyor:** multimetre (mV kademesi) ile kararlı bobin ve pin gerilimi; kontak çıkışı mantık analizörüyle ya da ikinci
  bir mikrodenetleyicinin kesme girişiyle izleniyor. Geçici bir çekmeyi kontak izlemesi yakalar.
- **T2a:** ayak sırası C-B-E dört veri sayfasıyla doğrulandı; ölçüt ve ters takma sayısı A3.

## Madde 4 · K14 riski

A2'de. Risk bölümü açık, kablo şartı somut, yedek yollar gerçekçi. Eksik olan: elle denemenin **ne zaman ve neyle** yapılacağı (sipariş
16.11; baskı parçaları yoksa deneme parçası ya da teslimde deneme).

## Madde 5 · İkinci kontrolün bulgularının kapanışı

| K2R | Durum | Nerede |
|---|---|---|
| D1 kapalı hâl | **Kapandı** (2,2 kΩ, bırakma gerilimi ölçütü; hesap doğru) | PH D1 / D9 / T2, EL:251 / :268 / :444 / :483-484, R §9, KK K58 |
| 1 K14 fiş geçişi | **Kapandı**; zamanlama eksik: A2 | R §4, §14, KT4; EL:37, :518; KK K14 |
| 2 K1 bobin akımı | **Kapandı** (0,191 / 0,21 A; T2'de 85 Ω ±%10) | PH D9, R §9, EL:268 |
| 3 -40 sınıfı, ayak sırası | **Kapandı**; sınıf gerekçesinin sayısı A1, T2a ölçütü A3 | PH D9, T2a; R §9; EL:268 |
| 4 T2 yedeği | **Kapandı** (VCE > 0,3 V → 220 Ω, T2 yinelenir) | PH T2, R KT7 |
| 5 ortak giriş | **Kapandı** (KT3 teslimde; ayrı girişliyse 12 AWG, kısa, tek klemens) | R §3, EL:68, :380, KK K11 |
| 6 mini / standart | **Kapandı** (kutu standart; F5 2 A, ek 5 A, F6 3 A standart C'de) | R §3, §10, §14; KK K11; G §7.5 |
| 7 K10 testi | **Kapandı** (DC pens / şönt, `pmic_read_adc` EXT5V_V, `get_throttled` 0x0; Raspberry Pi belgesiyle). EL:29 / :278 / :511 "tepe hesaplanmadı" C'de (G §7.5 madde 5) | R §2, KT1; EL:53; KK K10 |
| 8 ses bölücüsü | **Kapandı** (10 kΩ / 2,2 kΩ; oran 0,180 / 0,164; 1 V rms ile 1,69–2,04 W; R formülü doğru) | R §5, §11, KK kayıt |
| 9 pano taslağı | **Kapandı** (T2 yöntemi, sürüş gücü, 2,2 kΩ); yeni küçük not A5 | taslak madde 5 |
| 10 `pin-karari-gunluk.md` | **Kapandı** (R §16, G §7.1 ek) | R:393 |
| 11 E9 F6 dalı | **Kapandı** | EL:461 |
| 12 EL:446 K2 verisi | **Kapandı** (JQC-3FF-12VDC 10 A, 19,36 TL; MJ:109 ile aynı) | EL:446 |

## Madde 6 · Pano taslağı

A5'te. Kısa ve kaynaklı, protokole uygun; #24 ile çelişmiyor; gizlilik temiz. İki küçük metin düzeltmesi var.

## Madde 7 · Gizlilik

- Taranan dosyalar: R, G, `kablolama-onkarar-kontrol.md`, `-kontrol-2.md`, bu dosya; PH / EL / KK / `pin-karari-gunluk.md`'nin `b1c2a8d`'ye
  göre **eklenen** satırları; pano taslağı. Aranan: yerel kullanıcı yolu (`Users`, `AppData`, sürücü harfi, masaüstü / bulut klasörü adı),
  makine adı, takma ad, e-posta, parola / anahtar / belirteç, ağ adı (SSID), soyad.
- **Sonuç: hiçbiri yok.** "Echo" yalnız üreticinin "Acoustic Echo Cancellation" alıntısında (R:167) ve sonar "echo" uçlarında; kişi adı
  olarak yalnız "Ahmet" ve "Efe". Depoda önceden olan satırlarla bu paketin ekledikleri ayrı tarandı: eklenen satırlarda bulgu yok.
- MJ satırlarındaki satıcı URL'leri bu paketin eki değil (MJ değişmedi).

## Madde 8 · C adımı için liste

**Commit'e girecek dosyalar (bu paket):** `planlama/adim3/kablolama-on-kararlar.md`, `planlama/adim3/elektrik.md`,
`planlama/adim3/pin-haritasi.md`, `planlama/d158/karar-kuyrugu.md`, `planlama/d158/pin-karari-gunluk.md`,
`planlama/d158/kablolama-onkarar-gunluk.md`, `planlama/d158/kablolama-onkarar-kontrol.md`, `-kontrol-2.md`, `-kontrol-3.md` (bu dosya).
**Girmeyecek:** `tasarim/freecad/kabuk/gorsel/*.png` ve `tasarim/freecad/montaj/yerlesim-kontrol.json` (bu paketten önce de değişikti; başka
iş, G §7.3).

**G §7.5 ile karşılaştırma:** liste tam ve rapordaki kalemlerle tutarlı. MJ satır numaraları ve içerikleri okundu ve tutuyor: :106
IRLZ44N, :109 JQC-3FF, :115 direnç seti, :122 hat yuvası × 5, :123 2 A mini, :136 30 cm uzatma 77,46 TL, :137 "USB 3.0 Dişi-Erkek" 214,20 TL
(koşullu, K4), :138 L dirsek, :141 L 3,5 mm kablo, :191 HDMI 117,10 TL. Eklenmesi gerekenler:

1. **KK sayımı:** K1, K10, K11, K14 kapanınca :75 "Açık: 50 → **46**", "Kapandı: 8 → **12**" (K1, K10, K11, K14 eklenir; K14 Efe teyidi
   notu düşer). K10 "masa denemesine bağlı" kaydı kalır.
2. **A1 metin düzeltmesi:** PH D9 / BJT satırı / :302 / :326, R §9 (:278, :280, :284), EL:268, G §7.2'ye not. Değer ve kablaj değişmez.
3. **A3:** PH T2a ve R:286-289 (ölçüt "≈ 100'ün üstü"; ayak sırası C-B-E; ters takmada pin akımı ≈ 2–3 mA, bobin akımı asıl risk).
4. **A4:** PH T2'de "bara" → "bobin (+) ucu / besleme"; "F5 normal kullanımda takılmaz" cümlesi.
5. **A2:** R §4 / KT4, EL:37 / :518, KK K14: elle denemenin zamanı ve aracı (deneme parçası ya da teslimde; 16.11 siparişi).
6. **A5:** pano taslağı başlığı ("iki kontrolün düzeltmeleri işlendi"), gönderimden önce "üçüncü bakış bekliyor" → "karar verildi"; #24'e
   yan cümle; `pinler.json` `surum` 4 notu.
7. **A6 / A7:** PH T2 ya da EL E3'e sıcak bobin cümlesi; PH:25 RÖ "ikinci elden" → üretici tabloları (MAH3, JQC-3FF); PH:26 / :314 IOH "tipik".
8. `planlama/dongu-158.md` P10.7 satırı ve §5 girdisi (G §7.5 madde 2): üçüncü bakış **GEÇER** (bu dosya) ve açık işler A1–A7.

## Doğruladıklarım (kısa)

- BC337-40 hFE 250 / 400 / 630 @ 100 mA (Vishay, onsemi, Diotec, Lumimax, DC Components aynı); 300 mA değeri üreticiye göre 40 / 60 / 170 (A1).
- VCE(sat) ≤ 0,7 V @ 500 / 50 mA, VBE ≤ 1,2 V @ 300 mA, VEBO 5 V, VCEO 45 V, IC 800 mA, Ptot 625 mW, RθJA 200 °C/W, ICES ≤ 100 nA (125 °C'de
  ≤ 10 µA; Vishay, Diotec).
- Ayak sırası C-B-E (dört üretici).
- ESP32: VOH ≥ 0,8 × VDD, IOH tipik 40 mA (en yüksek kademe), RPU / RPD tipik 45 kΩ, IIH / IIL ≤ 50 nA, sürüş kademeleri ≈ 5 / 10 / 20 / 40 mA,
  varsayılan 2.
- MAH3 12 V: ≤ 8,4 V / ≥ 1,2 V / 85 Ω ±%10 / ≈ 1,7 W (23 °C). JQC-3FF 12 V: 9,00 / 1,2 / 400 Ω ±%10 / en çok 15,6 V.
- Bütün D1 / D9 sayıları (tablo, Madde 1); 220 Ω yedeği; ses bölücüsü ve güç; K10 toplamı 3,61 A; F6 %50 / %30.
- Pin tablosu HEAD ile ve üç yerde aynı (kendi betiğim). KK'de K56 / K57 / P10.5b dokunulmamış. Kalıntı yok. Gizlilik temiz.
- MJ:137'nin USB 3.0 olduğu (satır içeriği ve URL).

## Bakamadıklarım

- Direnc.net "BC337-40TA" ürününün üreticisi ve sayfası (bu bakışta açılmadı; "-40TA" adından onsemi / Fairchild çıkarımı). Üretici
  Diotec çıkarsa A1'deki 170 değeri geçerli olur; sonuç değişmez.
- onsemi'nin güncel sitesindeki BC337/D sürümü (site PDF yerine sayfa döndürdü; Farnell'deki Rev. 8 kopyası okundu).
- MAH-112-C-4'ün kendi veri sayfası (kardeş MAH3 tablosu okundu; K2R ile aynı sınırlama). Bobinin sıcaklık katsayısı veri sayfasında yok
  (A6'da bakırın genel değeri).
- Baskı parçalarının (servo yuvası, mil) basılıp basılmadığı: depoda kayıt bulamadım (A2).
- Pano #8 #24'ün sunucudaki hâli (yalnız depo dışındaki gönderim kopyası okundu; pano komutu koşulmadı).
- Ölçülebilecek hiçbir şey ölçülmedi (kart, röle, transistör yok).
