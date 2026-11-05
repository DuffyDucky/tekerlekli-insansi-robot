Seçim: B + R1, 05.11.2026, uygulandı, bkz. uygulama-notu.md.
Aşağıdaki metin seçimden önceki karşılaştırmadır; "model kesinleşmedi" ifadesi o tarihe aittir.

# Lale 158 cm: kafa içi ses ve USB yerleşim seçenekleri

Tarih: 05.11.2026. Bu belge seçim içindir, model kesinleşmedi. Mevcut model ve kod dosyaları değiştirilmedi; seçenek parçaları yalnız bu klasördeki betiklerde var.

Ahmet Yorulmaz kararları (04.11.2026): PAM8403 + USB ses kartı kalıyor. MAX98357A modelden seçimle birlikte çıkacak; burada yalnız kütle hesabında düşüldü, modelde duruyor. Elde yük bu çalışmanın dışında.

## Kısa sonuç

**Önerim B: dizi kafa tavanının altında sağ yarıda (R1), ses kartı ve PAM sol duvarda, hub gövdede servis kapağının içinde, hoparlör göğüs ekranının altında.**

| | A: hub kafada | **B: hub gövdede (öneri)** | C: hoparlör kafada | R2 çeşidi: B + dizi pan ekseninde |
|---|---|---|---|---|
| Mikrofon-hoparlör, tüm pozlarda en az | 574,3 mm | **574,3 mm** | **222,2 mm: H1'i sağlamaz** | 579,5 mm |
| Boyun kanalı doluluğu (bugün %44,8) | %52,9 | **%44,8** | %44,8 | %44,8 |
| Tilt payı, ±15 (bugün 3,89) | 3,47 | **3,64** | 3,28 | 3,67 |
| Pan payı (bugün 2,20) | 2,16 | **2,21** | 2,08 | 2,22 |
| SY8205 ile USB çakışması (bugün 249,7 mm³) | 0, açıklık 15,45 mm | **0, açıklık 15,45 mm** | 0, açıklık 15,45 mm | 0, açıklık 15,45 mm |
| Kabuk işi | Tavan + göğüs alt duvarı | **Tavan + göğüs alt duvarı + kapak içi hub yuvası** | Tavan + sol duvar | Tavan iki yarıda + tepe cıvatası taşınır |
| Hub'a erişim | Ön kabuk çıkar | **7 cıvatalı kapak çıkar, kafa kapanık kalır** | Ön kabuk çıkar | 7 cıvatalı kapak |
| Listede olmayan kablo ve parça | 5 kalem | 6 kalem, biri 1 m uzatma | 5 kalem | 6 kalem |
| Öneri metniyle uyum | Uyumlu | **Uyumlu** | **Çelişir** (satır 68, 158, 173) | Uyumlu |

Seçimi değiştirebilecek tek büyük soru: altıncı USB cihazı. Kafadaysa B zayıflar, A öne geçer (bkz. "Seçimi değiştirebilecek varsayımlar").

## Seçenekler

Bütün seçeneklerde PAM ve ses kartı **sol duvarda** (x -131,5...-120,5) ve üst üste duruyor. Bugünkü yerinde PAM, ses kartının USB fişinin önünde: gerçek boylu fiş PAM'e 621 mm³ giriyor. Bu yüzden ses kartı arkaya, PAM yukarı (y 72) alındı.

| Parça | A | B | C |
|---|---|---|---|
| ReSpeaker | R1, x +40, z -30, PCB üstü y 92,62 | Aynı | Aynı |
| Hoparlör | Göğüs altı duvar, x +45, y 982,5 (global) | Aynı | Kafa sol duvarı, y -70, z -40 |
| Hub | Modeldeki yer: sağ duvar, y 50, z -28 | **Üst arka servis kapağı içi**, x 35...60, y 1085...1157 (global) | Modeldeki yer |
| Ses kartı | Sol duvar, y 47, z -58...-10 | Aynı | Aynı |
| PAM | Sol duvar, y 72, z -31,5...-7,5 | Aynı | Aynı |

Koordinatlar tilt ekseni çerçevesinde (`bas`) mm, aksi yazmıyorsa. Kafa ev pozunda global = bas + (0; 1478,878; 25).

**Kafadan çıkanlar ve nedeni:**
- **Hoparlör (A, B):** İç köşegen üst sınırı 362,9 mm, yani 400 mm'den kısa. Dizi kafadayken kafa içinde hiçbir hoparlör yeri 40 cm şartını sağlayamaz. C bunu ölçülü gösteriyor: 222,2 mm.
- **Hub (yalnız B):** Göğüs dokunmatiği ve ESP32 kablosu boyundan inmekten kurtuluyor; yerlerine tek hub kablosu iniyor. Hoparlör kablosu eklense bile boyun bugünkü dolulukta kalıyor. Hub 25 g da kafadan çıkıyor ve kafa açılmadan erişilebiliyor.

Bugünkü sağ/sol duvar yeri de aday olarak denendi: A, hub'ı aynen orada tutuyor. Hub için sorun yok. Ses kartı için gerçek boyla (48 + 12 mm fiş, varsayım) yer değişikliği gerekiyor.

**R2'yi ayrı tuttum:** R1 ile R2 arasındaki fark çok küçük (pan payı 2,21 ve 2,22), ama R2 kabuğu zorlaştırıyor.

## Görseller

| Görsel | Dosya |
|---|---|
| Bugünkü model ve üç sorun | `gorsel/0-mevcut-kafa-arka-acik.png` |
| A | `gorsel/A-kafa-arka-acik.png`, `A-kafa-seffaf.png`, `A-kafa-kesit.png`, `A-dizi-yakin.png`, `A-ust.png`, `A-govde.png` |
| B | `gorsel/B-kafa-arka-acik.png`, `B-kafa-seffaf.png`, `B-kafa-kesit.png`, `B-ust.png`, `B-govde.png`, `B-hub-kapak.png` |
| C | `gorsel/C-kafa-arka-acik.png`, `C-kafa-seffaf.png`, `C-kafa-kesit.png`, `C-ust.png`, `C-govde.png` |
| R2 | `gorsel/R2-kafa-kesit.png`, `R2-dizi-yakin.png`, `R2-ust.png` |

## Ölçülen değerler

Modelden gerçek geometriyle hesaplandı (`distToShape`, `common`). Doğrulama: aynı betik bugünkü değerleri geri verdi: statik 0,083, tilt 2,416 / pay 3,89, pan 4,264 / pay 2,2, SY8205 çakışması 249,7 mm³.

Girdide varsayım olan satırlar "Varsayımlı girdi" sütununda işaretli; geometri ölçülü olsa da sonuç o varsayıma bağlı.

### 1. Boşluklar (mm)

Tilt -15...+15 (5° adım) ve pan -90...+90 (30° adım, tilt -15/0/15). Sürekli tarama değil, ızgara.

| Parça | En yakın parça | Kabuk veya kapak | Boyun (tilt ±15) | Gövde (pan × tilt) | Varsayımlı girdi |
|---|---|---|---|---|---|
| ReSpeaker R1 (A, B, C) | 12,10 ısıl somun; Pi 27,42 | 0,60 (jak ucu, tasarım seçimi) | 65,99 eğme çatalı | 177,50 rulman yuvası | Hayır, üretici STEP |
| ReSpeaker R2, bugünkü cıvatayla | **1,05** ısıl somun; cıvata 1,82 | **0,00: kabuğa değiyor** (tepe cıvata göbeği ve z +10 dikişi bölgesi; hangisi olduğu ayrı ölçülmedi) | 62,17 eğme çatalı | 177,04 | Hayır |
| R2, cıvata z -72'ye taşınınca | Yeni göbek-dizi 8,71 | Yeni göbek arka duvara 11,39; köşe payı 8,89 | Aynı | Aynı | Hayır |
| Dizi USB fiş zarfı R1 | 32,62 hub (A, C); 43,87 Pi (B) | 0,60 | 88,79 | | Evet, fiş 20 × 8 × 11 |
| Ses kartı gövdesi | 9,01 iskelet | 1,00 | 91,16 | | Evet, ölçüler |
| Ses kartı USB fişi | 17,49 iskelet | 1,00 | 113,52 | | Evet |
| L USB dirsek | 9,61 iskelet | 0,64 | 112,07 | | Evet, ürün seçilmedi |
| Uzatma dişi ucu | 3,00 tabla cıvatası | 3,89 | 89,54 | | Evet |
| L 3,5 mm fiş | 10,74 iskelet | 1,00 | 92,31 | | Evet |
| PAM8403 (y 72) | 18,00 kabuk cıvatası; ses kartı 4,00 | 1,00 | 108,81 | | Hayır, model zarfı sayfadan büyük |
| Hub, kafada (A, C) | 4,51 tabla cıvatası | 1,00 | 89,28 | | Hayır, model |
| Hub, kapakta (B) | 3,17 göğüs bandı; ısıl somun 7,00 | 1,03 kapak | Hareketsiz | Hareketsiz | Yönü varsayım |
| Hub fiş payı 40 mm (B) | 4,48 gövde braketi; direk 15,03 | | Hareketsiz | Hareketsiz | Evet |
| Hoparlör, göğüs (A, B) | 8,51 göğüs bandı; ekran 12,61 | 0,50 (tasarım seçimi) | Hareketsiz | Hareketsiz | Boy üründen; kap benim çizimim |
| Hoparlör kabı, göğüs | 5,52; ekran 9,18 | 0,20 | Hareketsiz | Hareketsiz | Evet |
| Hoparlör, kafa (C) | 31,23 kabuk cıvatası | 0,50 | 82,00 adaptör | 61,60 S1 kaset gövdesi (pan 0, tilt -15) | Kap benim çizimim |

Hiçbir seçenek parçası model parçasıyla çakışmıyor (eşik 0,5 mm³). Bosslar kabukla kasıtlı birleşiyor: 1,05 ve 2,78 mm³.

### 2. Kütle ve servo payı

Kafa grubu kütlesi; `kafa_montaj.py` §6 formülü aynen, durma momenti 9,4 kg·cm. Kablo kütlesi mevcut 59 g payının üstüne eklendi, biraz kötümser.

| | Kütle g | Statik, ±13 kg·cm | Statik, ±15 kg·cm | Tilt toplam | Tilt payı ±13 / ±15 | Pan toplam | Pan payı |
|---|---|---|---|---|---|---|---|
| Bugün | 1531,3 | 0,083 | 0,083 | 2,416 | 3,89 / 3,89 | 4,264 | 2,20 |
| A | 1595,5 | 0,237 | 0,250 | 2,693 | 3,49 / 3,47 | 4,359 | 2,16 |
| **B** | 1570,8 | 0,143 | 0,152 | 2,574 | 3,65 / 3,64 | 4,255 | 2,21 |
| C | 1634,6 | 0,334 | 0,336 | 2,862 | 3,28 / 3,28 | 4,524 | 2,08 |
| R2 | 1570,4 | 0,125 | 0,134 | 2,553 | 3,68 / 3,67 | 4,237 | 2,22 |

Duyarlılık (hepsi varsayımlı kütlelerle):

| | Dizi 18 g: tilt / pan payı | Dizi 70 g: tilt / pan payı | AI HAT+ 30 g eklenince: statik, tilt / pan payı |
|---|---|---|---|
| A | 3,61 / 2,16 | 3,14 / 2,14 | 0,442; 3,18 / 2,15 |
| **B** | 3,79 / 2,21 | 3,27 / 2,19 | 0,348; 3,32 / 2,20 |
| C | 3,39 / 2,08 | 2,97 / 2,06 | 0,538; 3,01 / 2,07 |
| R2 | 3,81 / 2,22 | 3,32 / 2,21 | 0,330; 3,34 / 2,21 |

Proje dosyalarında (`arayuz.py`, `kafa_montaj.py` taraması) sayısal bir pay eşiği bulamadım, bu yüzden "geçti" demiyorum. Bugünkü değerlerle karşılaştır.

Statik moment 2-4 katına çıkıyor, çünkü ağırlık tavana yaklaşıyor. Mutlak değer tilt toplamının küçük bir parçası kalıyor. Asıl artış eylemsizlikten geliyor. Servo kapalıyken kafanın kendi kendine öne düşüp düşmediği ayrıca denenmeli.

### 3. Kablo yolu ve boyu

Yol: orta çizgi mm. Sipariş boyu: yol × 1,25. Kablo tüpü model parçalarıyla kesiştirildi. Port girişlerindeki küçük kesişimler (Pi 2,5-11,8 mm³, hub 10,6 mm³) beklenen uç temasıdır. Boyun mili 1,17 mm³ bugünkü yolda da var, bu çalışmada doğmadı.

| Kablo | A | B | C | Listede |
|---|---|---|---|---|
| Göğüs dokunmatik USB | 824 → 1030; pi'den | **395 → 490; hub'dan** | 824 → 1030 | v4 satır 58, 2 m: yeter |
| Hub kablosu / uzatması | 66 → sabit 130 mm kablo yeter | **617 → 770: hub'ın 130 mm kablosu + ~1 m uzatma** | 66 | Uzatma yok |
| Ses kartı USB | Hub'dan 208 → 260 | Pi'den 217 → 270 | Hub'dan 208 → 260 | Yok |
| Dizi USB, Pi → micro B | 85 → 110 | 85 → 110 (R2: 69 → 90) | 85 → 110 | Yok; 30 cm olan ekran için, 2 m'likler göğüs ve ESP32 için |
| Hoparlör | 823 → 1030 | 823 → 1030 | 153 → 190 | Robot için yok; 2 × 0,75 kordon test düzeneğinin sarfı |
| 3,5 mm → PAM | 36 → 40 | 36 → 40 | 36 → 40 | Robot için yok; AUX 1,5 m sarf |
| PAM 5 V (varsayım: D24V50F5) | 64 → 80 | 64 → 80 | 64 → 80 | Besleme noktası `elektrik.md`'de doğrulanmadı |

**SY8205 çakışması nasıl çözülüyor:** Şematik yol bugün `(50, 47, -20) → (50, 38, 20)` ile kartın içinden geçiyor. Bütün seçeneklerde boyuna inen USB, tablanın üstünden z ≈ -14'te, SY8205'in önünden geçiyor (`KORIDOR`): SY8205 çakışması 0, açıklık 15,45 mm, tablaya 2,5 mm, Pi'ye 11,73 mm. Model değişikliği gerektirmiyor. B'de bu koridordan göğüs dokunmatiği değil hub kablosu geçiyor, göğüs dokunmatiği kafaya hiç girmiyor.

**Boyun demeti** (geçiş kesitinin dolulukları, `kablo_yolu_ekran.py` GECIS):

| | Alan mm² | Mil Ø32 | Çatal Ø28 | Mil penceresi | Yuva kanalı | Yuva çıkışı |
|---|---|---|---|---|---|---|
| Bugün ve C | 69,9 | %8,7 | %11,4 | %39,9 | %44,8 | %34,3 |
| A | 82,5 | %10,3 | %13,4 | %47,1 | %52,9 | %40,4 |
| **B** | 69,9 | %8,7 | %11,4 | %39,9 | %44,8 | %34,3 |

**Pi portları:**

| Port | A ve C | B |
|---|---|---|
| Pi 1 | ReSpeaker | ReSpeaker |
| Pi 2 | Göğüs dokunmatik | Ses kartı |
| Pi 3 | Hub | Hub |
| Pi 4 | Kafa ekranı dokunmatik | Kafa ekranı dokunmatik |
| Hub | Ses kartı, ESP32, 2 boş | Göğüs dokunmatik, ESP32, 2 boş |

**Dizi USB'sinin güç kablolarına uzaklığı** (öneri satır 199): SY8205 40,82; D24V50F5 120,78; TVS 55,36; PAM 5 V 129,79; hoparlör kablosu 89,54 (C: 132,68) mm. B'yi önce sağ duvarla denedim: PAM 5 V 9,84 ve hoparlör kablosu 12,05 mm'ye düştü, bu yüzden sol duvara aldım.

### 4. Kabuk değişikliği ve baskı

`KL.baski_analiz` ile önce/sonra. Bu analiz yalnız çıkıntı ve destek bakıyor; Ø3 deliğin yuvarlaklığını ve yüzey kalitesini değerlendirmiyor, bunu deneme baskısı söyler.

| Değişiklik | Parça | Destek sorunu | Çıkıntı oranı | Kütle g | Süre sa |
|---|---|---|---|---|---|
| Bugün | Arka kabuk sağ | **1** (z 2,5, 2723 mm², değişiklikten bağımsız) | %3,25 | 218,2 | 4,77 |
| R1: 4 Ø3 delik + 3 damla boss + pilot | Arka kabuk sağ | **1, aynı sorun** | %3,29 | 218,5 | 4,78 |
| Bugün | Arka kabuk sol | 0 | %1,35 | 205,1 | 4,49 |
| R2 | Sağ + sol | Sağ 1, sol 0 | %3,26 / %1,36 | 218,5 / 205,2 | 4,78 / 4,49 |
| Hoparlör, kafa (C): 19 Ø3,5 delik + 2 boss | Arka kabuk sol | 0 | %1,49 | 205,2 | 4,49 |
| Bugün | Gövde orta bandı sağ | 0, ofset uyarısı 9 | %0,44 | 258,8 | 5,66 |
| Hoparlör, göğüs (A, B): 19 Ø3,5 delik + 2 boss | Gövde orta bandı sağ | 0, ofset uyarısı 9 | %0,50 | 258,9 | 5,66 |
| Hoparlör kabı, ayrı parça | 62,5 × 62,5 × 22 | **2, iki yönde de** | | 9,3 | 0,2 |

Ek olarak:
- **R2:** "Arka üst" tepe cıvatasını z -39,9'dan z -72'ye taşımak gerekiyor; bu taşıma yukarıdaki baskı rakamlarında yok. Mikrofon delikleri x = 0 dikişinin iki yanına düşüyor (dikişe en yakın delik 20,83 mm), boss'lar iki parçaya bölünüyor (sağ, sol, sağ).
- **B:** Kapak iç yüzü eğik: y 1085'te z -82,37, y 1157'de z -79,51. Hub'ı yatay tutmak için 1...3,9 mm takoz ya da eğik yuva gerekiyor. Bu yuva çizilmedi, baskısı analiz edilmedi.
- **Ses kartı ve PAM:** Bugünkü gibi köpük bant; delik veya boss gerekmiyor.
- **Hoparlör montajı:** Üründe delik görünmüyor, köpük kenarlı. Kap ve kelepçe benim çizimim, ürün elde görülmeden kesinleşmez.

### 5. Isı

Hepsi model geometrisi. Isıl hesap yeniden yapılmadı.

| | Yarık | Yarık arkası 20 mm prizma | Fan yeri (30 × 30 × 10) |
|---|---|---|---|
| Dizi R1 | 21,42 mm | 0 mm³ | 12,42 mm, kesişim 0 |
| Dizi R2 | 27,22 mm | 0 mm³ | 18,88 mm, kesişim 0 |
| Ses kartı | 80,66 mm | 0 | 134,44 mm |
| PAM | 98,26 mm | 0 | 146,38 mm |
| Uzatma dişi ucu | 44,59 mm | 0 | 102,18 mm |
| Hub, kafada | 71,12 mm | 0 | 71,27 mm |

- Hiçbir parça yarık prizmasına veya fan yerine girmiyor.
- Dizi, Pi + soğutucunun 27,42 mm üstünde (R1). Fan yerinin üst 7 mm'si dizi yüksekliğine rastlıyor; arada 12,42 mm var (R1). Hava akışına etkisi ölçülmeden söylenemez.
- C'de hoparlörün de kafada olması, 3 W tepe alındığında R 0,992 K/W ile en çok +3 K demek. Bu hesap, ölçüm değil, ve sürekli 3 W kötümser bir kabul.
- Hub kapakta: gövde içi ısı için bu çalışmada hesap yok.

### 6. Servis erişimi

Normal servis: ön kabuk ve ekran çıkar; arka kabuk tablaya bağlı kalır. Derinlik, z = +10 dikişinden itibaren.

| | Derinlik mm | Önünde engel | Not |
|---|---|---|---|
| Dizi R1 | 75,8 | Yok | 3 vida alttan; kısa tornavida gerekir: tablaya kadar 57,8 mm serbest (Ø8 tornavida silindiri ile) |
| Dizi R2 | Dikişe kadar uzanıyor | Yok | Üçüncü vidada AI HAT+ varsa serbest boy **27,6 mm** (AI HAT+ varsayımı) |
| Dizi USB fişi R1 | 27,7...38,7 | Yok | Dizi sökülmeden çıkar |
| Ses kartı | 68,0 | Yok | Köpük bantlı |
| PAM | 41,5 | Yok | Köpük bantlı |
| Hub, kafada | 2...74 | Yok | Ön kabuk gerektirir: QLED ve kabloları ayrılmalı |
| Hub, kapakta (B) | Kapak kalkınca doğrudan | Yok | 7 M3 cıvata; **kafa açılmıyor**. Kablolarda kapak sökme payı gerekir |
| Hoparlör (A, B) | Arka kapaktan z farkı yaklaşık 155...194 | Ölçülmedi | Kutu ölçüsünden; elle ulaşılabilirliği ölçülmedi, orta bant açılması gerekebilir |
| Hoparlör (C) | 70 | Yok | |

### 7. Akustik geometri

Yalnız geometri. Performans iddiası yok.

| | R1 (A, B, C) | R2 |
|---|---|---|
| Mikrofon portu → tavan iç yüzü | 4,9 mm | 4,9 mm |
| Port → dış hava | 7,4 mm (duvar 2,5) | 7,4 mm |
| Delik | Ø3 (varsayım), port Ø0,7 (STEP) | Aynı |
| QLED | 57,7 | 53,9 |
| Pi + soğutucu | 36,8 | 36,2 |
| Soğutucu üst yüz merkezi | 44,8 | 43,2 |
| Fan yeri | 24,2 | 30,1 |
| Arka yarık | 33,1 | 38,1 |
| SY8205 | 56,9 | 56,0 |
| D24V50F5 | 103,5 | 71,6 |
| Kamera | 44,7 | 39,8 |
| Tilt servosu / pan servosu | 83,9 / 241,1 | 83,9 / 241,3 |
| Pan eksenine uzaklık | 40,3 | 0 |

Mikrofon-hoparlör, 7 tilt × 13 pan:

| | Ev pozu | En az | En çok | H1 (≥ 400) |
|---|---|---|---|---|
| A, B | 595,7 | 574,3 (pan -90, tilt -15) | 623,8 | Sağlıyor |
| R2 | 595,3 | 579,5 | 613,6 | Sağlıyor |
| C | 222,2 | 222,2 (kafayla döner) | 256,4 | **Sağlamıyor** |

Hoparlörün yönü: duvara paralel eksen yatayın 35° altına bakıyor. 1,6 m kulak yüksekliğinde bir dinleyiciye eksen dışı açı:

| Dinleyici uzaklığı | Duvara paralel | Yatay eksen (kama gerekir) |
|---|---|---|
| 0,5 m | 89,1° | 54,2° |
| 1,0 m | 68,1° | 33,2° |
| 1,5 m | 58,1° | 23,2° |

Yatay eksen geometrik olarak sığıyor (duvara 0,41 mm, ekrana 23,29 mm), ama kama boşluğu 0,5...28 mm: ayrı bir akustik hazne sorunu çıkarır.

R1'de dizi pan ekseninden 40,3 mm uzakta. Pan 90° iken 1 m'deki kaynağa geometrik yön sapması en çok 2,3°. Öneri metni satır 173'e göre robot dinlerken kafa hareket etmediğinden R2'nin ana kazancı azalıyor.

**Ölçülmesi gerekenler** (hiçbiri ölçülmedi):
1. Ø3 deliklerin frekans tepkisine ve yön bulmaya etkisi; deliksiz ve kapaksız diziyle karşılaştırma.
2. Port ile delik arasındaki 4,9 mm boşluğun etkisi; keçe veya conta gerekip gerekmediği.
3. Hoparlörden mikrofona giden ses düzeyi ve yankı gidermenin bu mesafede yeterliliği; gövde içinden geçen titreşim.
4. Soğutucu fanı ve 30 mm fan çalışırken mikrofondaki gürültü (H1, en çok 3 dB).
5. Servo ve motor güçleri açıkken gürültü tabanı (H1).
6. Izgaralı duvarın ve kapalı kabın hoparlör sesine etkisi; yatay/eğik eksen farkı.
7. Hub kablosu uzayınca hub girişindeki gerilim (B).

## Varsayımlar

| Ölçü | Değer | Durum |
|---|---|---|
| ReSpeaker kütlesi | 30 g | **Varsayım.** Üretici net vermiyor: 70 g brüt (Farnell), 18 g doğrulanmamış satıcı. Duyarlılık hesaplandı |
| ReSpeaker geometrisi | Ø70, 13,1, 3 × Ø2,2 delik, mikrofon portları | **Üretici STEP'inden.** Çizim PCB'yi 1,5, STEP 1,2 gösteriyor; toplam 13,1 (STEP), 13,3 (Farnell) |
| Hoparlör boyu | Ø40 × 20, 4 Ω, 3 W | **Satıcı sayfası** (Motorobit, v4 satır 30) |
| Hoparlör kütlesi | 27 g | **Varsayım** (Adafruit 3968, başka ürün) |
| Hoparlör montajı | Delik yok, kap + kelepçe | **Varsayım**, fotoğraftan |
| Ses kartı | 48 × 24 × 11, fiş 12 | **Varsayım.** Sayfada ölçü yok; fotoğraftan USB-A eni 12 mm ölçeğiyle; kalınlık `kafa_lib` tahmini |
| Ses kartı kütlesi | 8 g | **Varsayım** |
| PAM8403 | Model 24 × 18 × 5 kullanıldı | Sayfa 21 × 18 × 3,4; model daha büyük, kötümser. Kütle 3 g **varsayım** |
| Hub | 72 × 25 × 19, 25 g, kablo 130 mm | **Satıcı sayfası** (24/26 g, 72/73 × 25/26 değişiyor). Port yönü **varsayım** |
| L USB dirsek | 16 × 18 × 12, 5 g | **Varsayım**, ürün seçilmedi |
| Uzatma dişi ucu | 30 × 18 × 11, 6 g | **Varsayım** |
| L 3,5 mm fiş | 16 × 10 × 10, 3 g | **Varsayım** |
| Kablo | USB Ø4, 30 g/m; diğerleri 15 g/m | **Varsayım** |
| Pi USB ağzı konumu | Model + yaklaşık | **Varsayım** ±2 mm |
| Mikrofon deliği | Ø3 | **Varsayım** |
| AI HAT+ 26T | 65 × 56,5, yığın 16, 30 g | **Varsayım.** v4 satır 114 ve öneride var, **CAD modelinde yok** |
| Dizi plastik boss | M2 × 8 kendinden diş | **Varsayım** |
| Kablo yolları | Köşeli orta çizgi | **Şematik**, gerçek kablo bükümü modellenmedi |

### Seçimi değiştirebilecek varsayımlar

1. **Altıncı USB cihazı.** `elektrik.md` 6 cihaz diyor, adı belli beşi var. v4 satır 164 "Yönlü mikrofon + USB ses kartı" olası aday, doğrulanmadı. Kafadaysa B'de Pi'de boş port kalmıyor ve kablo boyundan aşağı inip geri çıkmak zorunda: **bu durumda A öne geçer**.
2. **Ses kartının gerçek biçimi.** Kablolu bir kart ya da farklı boy çıkarsa L dirsek gereksiz kalır veya yerleşim yeniden ölçülür.
3. **Dizi kütlesi.** 70 g çıkarsa tilt payı B'de 3,27, A'da 3,14. Sıra değişmiyor.
4. **AI HAT+ yığın yüksekliği.** R1'de diziye 24,97 mm; yüksekliği büyürse hava yolu ve vida erişimi değişir. R2'de vida erişimi zaten 27,6 mm.
5. **Hoparlör ekseni.** Duyulabilirlik ölçümü yatay ekseni zorunlu kılarsa kama gerekir. Seçenekler arası fark yaratmıyor ama göğüs işini büyütür.
6. **Boy sınırı.** Dizi kabuğun altında, çünkü tepe 1.580,0 mm'de. Kabuk üstüne çıksa açıklık ve akustik iyileşebilir, ama en az 13 mm boy aşılır.
7. **İki MEMS karşılaştırma mikrofonu** (öneri satır 161 ve 189: "dizinin yanına", aralığı İP1'de belirlenecek; bütçede INMP441). Bu çalışmada modellenmedi. R1 tavanın sol yarısını boş bırakıyor; R2 ortada duruyor. Yerleri seçimi etkileyebilir.

## Öneri metniyle uyum (`oneri-taslak-v8.md`, salt okundu)

| Satır | Metin | A, B, R2 | C |
|---|---|---|---|
| 68 (H1) | Dizi kafanın üstünde, hoparlörden en az 40 cm | Uyumlu, 574 mm | **Çelişir**, 222 mm |
| 152 | Kafanın üstüne yatay | Yatay; **kabuğun altında**, delikli tavan | Aynı |
| 158 | Göğüs ekranının altına, 40 mm, 3 W | Uyumlu | **Çelişir** |
| 173 | Üst yüzey, yatay; hoparlör göğüs altında; 40 cm denetlenecek | Uyumlu | **Çelişir** |
| 199 | Dizi USB'si güç kablolarından ayrı kanal | Uyumlu, en az 40,8 mm | Uyumlu |

Satır 152 ve 173 için tek dikkat noktası: "üstüne" denirken dizi kabuğun 2,5 mm altında. Metin değiştirilmedi; değiştirilip değiştirilmeyeceğine öneri oturumu karar verir.

## Neden B

- **Boyun:** Tek seçenek ki hoparlör kablosu eklendiği halde boyun bugünkü dolulukta kalıyor. A'da yuva kanalı %44,8'den %52,9'a çıkıyor. Dönen eklemden geçen kablo sayısı bu robotun en az bozulması gereken yeri.
- **Servis:** Hub ve iki USB bağlantısına 7 cıvatalı kapakla ulaşılıyor, kafa ve QLED açılmıyor.
- **Paylar:** Tilt 3,64, pan 2,21; bugünkü pan payını koruyor. A'dan farkı küçük, tek başına belirleyici değil.
- **Ses:** Dizi USB'si güç kablolarından A kadar uzak.
- **Kabuk:** R1 tek parçada kalıyor, tepe cıvatası yerinde.

**B'nin bedeli:** 1 m'lik USB uzatma ve boyun yolunda fazladan bir bağlantı noktası; kapak içi hub yuvası çizilmedi; göğüs dokunmatiği ve ESP32 tek hub kablosuna bağlı. ESP32 A'da da hub üzerinde, fark dokunmatik.

**A ne zaman daha iyi:** Altıncı cihaz kafadaysa ya da kapak işini istemiyorsan. A'nın kabuk işi B'den bir kalem az, 1 m uzatma da gerekmiyor; bedeli boyundaki fazladan kablo ve kafa açılmadan hub'a ulaşılamaması.

**C'yi önermiyorum:** 40 cm şartı geometrik olarak imkânsız, öneri metniyle çelişiyor, paylar en düşük.

**R2'yi önermiyorum:** Dizi pan ekseninde olmasının payda kazancı 0,01. Kabuğu iki yarıya böler, tepe cıvatasını taşıtır.

## Listede olmayanlar

| Kalem | A | B | C |
|---|---|---|---|
| USB-A uzatma ~30 cm | 1 (hub → ses) | 1 (Pi → ses) | 1 (hub → ses) |
| USB-A uzatma ~1 m | | 1 (Pi → hub) | |
| L USB-A dirsek | 1 | 1 | 1 |
| Kısa micro USB (dizi) | 1 | 1 | 1 |
| Hoparlör kablosu | ~1,1 m | ~1,1 m | ~0,2 m |
| L 3,5 mm fişli kısa kablo | 1 | 1 | 1 |

Ayrıca: PAM8403 sayfasının HTML'inde "Tükendi" yazısı var, üst verisi stokta diyor, v4 stok 89 yazıyor. Sipariş öncesi bakılmalı.

ReSpeaker'ın 12 LED'i bu montajda kabuğun altında kalıyor; dışarıdan görünmez. Görünmesi istenirse ışık borusu veya saydam parça gerekir.

## Ahmet Yorulmaz için sorular

1. A, B, C içinden hangisi? Önerim B.
2. Dizi R1 mi, R2 mi? Önerim R1.
3. Altıncı USB cihazı ne, nerede duracak?
4. Hoparlör duvara paralel mi kalsın (basit, dinleyiciye 68° eksen dışı, 1 m), yoksa yatay eksene kama yapılsın mı (33°, kama hacmi sorunu)?
5. PAM'in 5 V'u D24V50F5'ten alınsın mı? `elektrik.md`'de bu nokta doğrulanmamış; Pi hattına eklenir.
6. Dizi kabuğun altında kalsın mı, yani "kafanın üstü" böyle kabul edilir mi? Boy 1.580 sınırı bunu zorluyor.
7. ReSpeaker'ın LED'leri görünmese olur mu?
8. Listede olmayan kablolar v4'e eklenecek mi, yoksa bütçe dışı mı karşılanacak?

## Kaynaklar

**Bu klasör:** `sonuc.json` (ham ölçüm), `yerlesim_lib.py` (seçenek geometrisi), `yerlesim_olc.py`, `yerlesim_koridor.py`, `yerlesim_gorsel.py`, `kaynak/RESPEAKER-MIC-3D-v2.0.stp`, `kaynak/respeaker-olcu-1.png`, `kaynak/respeaker-olcu-2.png`, `kaynak/ses-karti-motorobit.jpg`, `kaynak/hoparlor-motorobit.jpg`.

**Proje (salt okundu):** `tasarim/freecad/arayuz.py`, `kafa/kafa10_lib.py`, `kafa/kafa_lib.py`, `kafa/kafa_parcalar.py`, `kafa/kafa_montaj.py` (§6 formülü kopyalandı, içe aktarılmadı), `lale158/kablo_yolu_ekran.py`, `lale158/lale158_kontrol.py`, `lale158/lale158-kontrol.json` (249,7 mm³), `lale158/qled-cerceve-tasarim-notu.md`, `montaj/robot-montaj.FCStd` (kopyası üzerinden), `planlama/adim3/elektrik.md`, `tubitak-2209b/taslak/oneri-taslak-v8.md`, `tubitak-2209b/malzeme-listesi/` (BOM v4).

**Üretici ve satıcı:** ReSpeaker wiki: https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/ ; hoparlör: https://www.motorobit.com/speaker-4-ohm-3w-40mm ; ses kartı: https://www.motorobit.com/usb-71-kanal-kulaklik-mikrofon-ses-karti ; PAM8403: https://www.robotistan.com/23w-mini-amfi-devresi-pam8403 ; hub: https://www.robotistan.com/usb-hub-3lu-mini-usb-a-dahili-guc-anahtari

**Koşu geçmişi:** `sonuc.json` birleşik: A ve C son tam koşudan, B ve R2 sol duvar değişikliği sonrası koşudan, baskı bölümü ilk tam koşudan (dizi ve hoparlör kabuk geometrisi o tarihten beri değişmedi), koridor ve kapak bilgisi `yerlesim_koridor.py`'den. Hoparlör kabının ikinci baskı yönü de son koşudan. Kabuk zinciri ve uzun taramalar koşulmadı.
