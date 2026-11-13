# 06 - Onaylı satıcı taraması (B grubu)

Tarih: 01.11.2026
Kapsam: yalnız Robotistan, Motorobit, Robocombo, Direnc.net. Referans: `planlama/maliyet.json` (değiştirilmedi).
Kural: ihtiyacı karşılayan en ucuz stoklu ürün; gereğinden üstün/pahalı muadil seçilmedi. Fiyatlar KDV dahil, sayfada görünen TL.
"Fark TL" = (yeni birim − eski birim) × adet; eksi = ucuzladı. Bulunamayan kalemlerde fiyat yok.

Yöntem notu: Robotistan, Motorobit, Direnc.net ürün sayfaları açıldı (fiyat/stok sayfadan: JSON-LD, stok bayrağı). Robocombo arama sayfası JS ile yüklendiği için sitenin kendi mağaza arama servisi (aynı veri, tarayıcının kullandığı) sorgulandı; seçilen Robocombo ürünlerinin sayfası açıldı (sayfada "Fiyatlarımıza KDV dahildir" ve JSON-LD fiyatı API ile aynı).

| Kalem | İhtiyaç (kısa) | Adet | Site | Ürün adı | URL | Birim fiyat TL | Eski birim TL | Fark TL | Stok | Durum | Fark ve not |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Göğüs ekranı | 10,1" HDMI, 1280×800 IPS, kapasitif, kasalı | 1 | Robotistan | WaveShare 10.1inç Kapasitif Dokunmatik LCD (E) Ekran Modülü, 1024×600, HDMI, IPS tam lamine | https://www.robotistan.com/101-inc-lcd-ekran-modulu | 5.969,63 (liste 6.716,06; indirimli) | 12.424,50 | -6.454,87 | Var | muadil | 1024×600 (istenen 1280×800 değil), kasasız, 10 noktalı kapasitif, 6H cam, HDMI + USB dokunmatik, 5V/900 mA. Tam model (10.1" HDMI LCD (B) muhafazalı 1280×800 IPS kapasitif) Direnc.net'te var ama stokta yok (8.126,92 TL). Dış ölçü (mm) hiçbir sayfada yazmıyor. |
| Kafa ekranı | 8" HDMI, dokunmatiksiz olabilir (karar değişti) | 1 | Robotistan | WaveShare 7 Inch HDMI Kapasitif Dokunmatik LCD Ekran, 1024×600 (C) | https://www.robotistan.com/7-hdmi-kapasitif-dokunmatik-lcd-ekran-1024x600 | 2.388,70 (liste 2.813,85; Kasım indirimi) | 12.424,50 (10,1" yüz ekranı referansı) | -10.035,80 | Var | muadil | 4 onaylı sitede 8" HDMI ekran yok. En yakın ve en ucuz stoklu: 7". Dokunmatikli (kapasitif), 1024×600, HDMI + USB dokunmatik, 5V mikro USB. Dokunmatiksiz 7" (Direnc 7inch HDMI LCD 1024×600 IPS, 3.174,89) stokta yok ve daha pahalı. Dış ölçü sayfada yok. 8" yerine 7" tasarımı küçültür. |
| Mikrofon dizisi | USB 4 mikrofon, DOA / gürültü bastırma / AEC (XVF3800 muadili) | 1 | Robotistan | ReSpeaker Mic Array v2.0 (SeeedStudio) | https://www.robotistan.com/respeaker-mic-array-v20 | 6.652,29 | 5.500,00 | +1.152,29 | Var | muadil | XVF3800 değil, XMOS XVF-3000 tabanlı eski nesil. 4 dijital MEMS mikrofon (ST MP34DT01TR-M, -26 dBFS, SNR 61 dB, çok yönlü), USB Audio Class 1.0, çip üstü DoA / beamforming / AEC, 12 RGB LED, Ø70 mm, maks. örnekleme 16 kHz. Fiyat referanstan pahalı; aynı işi yapan daha ucuz onaylı ürün bulunamadı (bkz. seçenekler). |
| Mikrofon (ReSpeaker Lite) | 2 mikrofon, gürültü bastırmalı | 1 | Robotistan | ReSpeaker 2 Mikrofonlu Pi HAT | https://www.robotistan.com/respeaker-2-mikrofonlu-pi-hat | 1.220,16 | 2.617,54 | -1.397,38 | Var | muadil | USB değil, Pi GPIO HAT; WM8960 codec, 2 mikrofon. Sayfada gürültü bastırma / DSP yazmıyor (Lite'ta var). Pi 5 uyumu sayfada belirtilmiyor. Mic Array v2.0 alınırsa bu kalem gereksiz kalabilir. |
| Yönlü mikrofon kolu | Kardioid shotgun mikrofon + USB ses kartı | 1 | Robocombo + Motorobit | Max9814 Mikrofon Amplifikatör (CMA-4544PF-W) + USB 7.1 Kanal Kulaklık + Mikrofon Ses Kartı | https://www.robocombo.com/max9814-mikrofon-amplifikator-cma-4544pf-w-yuksek-3865 ; https://www.motorobit.com/usb-71-kanal-kulaklik-mikrofon-ses-karti | 241,80 (150,00 + 91,80) | 2.000,00 | -1.758,20 | Var (69 / 10+) | muadil (zayıf) | Kardioid / shotgun mikrofon onaylı sitelerde yok. MAX9814: otomatik kazançlı (40/50/60 dB) elektret modül, sayfada yönlülük yazmıyor; yönlü mikrofon yerine geçmez. USB kart: tak-çalıştır, analog çıkış + mikrofon girişi. Gerçek yönlülük için bu kalem onaylı satıcıdan karşılanamıyor. |
| Ses amfisi | MAX98357A I2S 3 W | 1 | Robotistan | 2*3 W Mini Amfi Devresi - PAM8403 | https://www.robotistan.com/23w-mini-amfi-devresi-pam8403 | 21,86 | 737,28 | -715,42 | Var | muadil | MAX98357A onaylı sitelerde yok. PAM8403 analog (I2S değil), 2×3 W. Pi 5'te analog çıkış yok; USB ses kartının kulaklık çıkışından beslenir (yukarıdaki USB kart kullanılabilir). 2. seçenek: Robocombo PAM8403 2x3W, 24,00, stok 68. |
| Kamera kablosu | Pi 5 FPC 22 pin 0,5 mm → 15 pin 1 mm, ~300 mm | 1 | Direnc.net | Raspberry Pi 5 Kamera FPC Kablosu - 300mm | https://www.direnc.net/raspberry-pi-5-kamera-fpc-kablosu-300mm | 175,43 | 156,25 | +19,18 | Var (liste) | aynı | Sayfa: Pi 5 için 22 pinli 0,5 mm uç özel FPC kablosu. Daha ucuz: Motorobit "Raspberry Pi 300mm Esnek Kamera Kablosu" 107,10 (stok 100+) ama sayfada Pi 5 / 22 pin yazmıyor, uyumsuz olabilir; seçilmedi. Robocombo Pi 5 30 cm 195,00 (stok 48). |
| Omni teker | Ø127 mm, ≥30 kg, 12 mm altıgen göbek | 2 | - | - | - | fiyat yok | 2.269,59 | - | - | bulunamadı | Onaylı sitelerde Ø127 mm omni yok. Bulunanlar: Motorobit 80 mm "Omni Mecanum" 459,00 (mecanum, Ø80, taşıma kapasitesi/göbek yazmıyor), Robotistan 50 mm plastik omni 26,21 ve 60/80 mm mecanum setleri. Hiçbiri 30 kg / 12 mm altıgen şartını karşılamaz. |
| Motor montaj braketi | 37 mm metal motor tutucu | 4 (2 paket) | Robotistan | Aluminyum L tipi 37D Motor Tutucu (İkili) PL-1084 (Pololu) | https://www.robotistan.com/aluminyum-l-tipi-37d-motor-tutucu | 761,62 / paket (2 adet) | 114,00 / adet | +1.067,24 | Var | muadil | L tipi alüminyum, ikili paket; 4 adet için 2 paket = 1.523,24. Çok pahalı. Daha ucuz: Motorobit "37 mm Motor Tutucu" 107,10 / adet (4 adet 428,40; referanstan da ucuz) ama şu an "Gelince Haber Ver" (stok yok). Stok gelirse onu seç. Delik düzeni JGB37 için kontrol edilmeli. |
| Servo horn 25T | Alüminyum 25T disk horn | 10 | Motorobit | 25T Servo Motor Kolu - Gri / Siyah | https://www.motorobit.com/25t-servo-motor-kolu-gri | 76,50 | 82,32 | -58,20 | Var (100+) | muadil | MG995 / MG946R / MG996R / MG945 / S3003 uyumlu; bağlantı delikleri merkezden 20 ve 24 mm; vidalar dahil. Malzeme sayfada yazmıyor (alüminyum doğrulanmadı). Robocombo "Metal" yazan 25T kol 159,00 ama stok yok. |
| Çok amaçlı servo braketi | Alüminyum, MG996R/DS3218 boyu | 2 | Robotistan | Çok Fonksiyonlu Servo Motor Tutucu | https://www.robotistan.com/cok-fonksiyonlu-servo-motor-tutucu | 64,99 | 89,10 | -48,22 | Var | aynı | 2 mm sert alüminyum, 58 × 37 × 26 mm, 16 g, siyah; uyumlu: MG995/MG996/SG5010 ve 40×20×36 mm standart servo. DS3218 adı yazmıyor ama aynı gövde ölçüsü sınıfında; delik düzeni tasarımda kontrol edilmeli. |
| Uzun U servo braketi | Alüminyum, kafa eğme | 1 | Robotistan | U Tipi Uzun Servo Motor Çerçevesi | https://www.robotistan.com/u-tipi-uzun-servo-motor-cercevesi | 92,32 | 89,10 | +3,22 | Var | aynı | 2 mm sert alüminyum, 64,5 × 56 × 25,5 mm, 21 g, siyah. Daha ucuz onaylı alternatif yok: Robocombo U Tipi Uzun 120,00 (stok yok). |
| Rulman 6808-2RS | 40×52×7 | 4 | - | - | - | fiyat yok | 106,80 | - | - | bulunamadı | Dört sitede de arama ve rulman kategorilerinde yok (yalnız lineer rulman, 624/608 3D yazıcı rulmanı). |
| Rulman 625ZZ | 5×16×5 | 5 | - | - | - | fiyat yok | 29,67 | - | - | bulunamadı | Motorobit "625ZZ Rulman 5mm - Plastik Kaplı" (91,80, stok 459) sayfada 5×21,5×7 mm; dış çap / genişlik farklı, tasarıma uymaz. Seçilmedi. |
| PETG filament siyah | 1,75 mm, 1 kg, toplam 11 kg | 11 | Direnc.net | Siyah PETG Filament 1.75mm 1Kg - Tri-d | https://www.direnc.net/siyah-petg-filament-175mm-1kg-tri-d | 680,53 | 389,00 | +3.206,83 | Var (listede 12) | aynı | En ucuz stoklu. Aynı sitelerde ikinci: Robotistan Fibromast PETG siyah 731,86 (stok var). Robocombo Creality CR-PETG siyah 750,00 ve Porima 810,00 stokta yok. Referanstaki 389 TL (Microzey) onaylı sitelerde yok. |
| PETG filament beyaz (1) | 1,75 mm, 1 kg | 5 | Direnc.net | Beyaz PETG Filament 1.75mm 1Kg (Tri-d) | https://www.direnc.net/beyaz-petg-filament-175mm-1kg | 680,53 | 389,00 | +1.457,65 | Var (listede 5) | aynı | Direnc'te beyaz stoğu listede yalnız 5. |
| PETG filament beyaz (2) | 1,75 mm, 1 kg | 4 | Robotistan | Fibromast 3D 1,75 mm PETG Filament - Beyaz | https://www.robotistan.com/fibromast-3d-175-mm-petg-filament-beyaz | 731,86 | 389,00 | +1.371,44 | Var | aynı | Kalan 4 kg için. Net ağırlık 1 kg (1000 g), 230-250 °C. Robocombo Creality Hyper PETG beyaz 1.050,00 (stok 3) pahalı; CR-PETG beyaz 750,00 stokta yok. |
| PETG-CF filament | PETG-CF 1,75 mm, toplam ~1,5 kg | 3 (0,5 kg) | - | - | - | fiyat yok | 1.114,03 | - | - | bulunamadı | Dört sitede PETG-CF / karbon katkılı PETG yok. Tek karbon katkılı filament: Robotistan Fibromast ABS CF 1.275,43 (stok var), ama ABS bazlı (kapalı kasa gerekir, ısıl davranış farklı), spool ağırlığı sayfada yazmıyor; PETG-CF yerine önerilmez, toplama katılmadı. |
| Isıl gömme somun M3 | Pirinç insert, delik Ø4,0×5,7 | 168 | - | - | - | fiyat yok | 5,22 | - | - | bulunamadı | Direnc.net "İnsert Somun M3" 12,70 TL, stokta yok; sayfada paslanmaz çelik / alaşım, dış çap 6 mm, boy 5 mm (pirinç değil, Ø4,0 delik için büyük). Başka sitede yok. |
| Isıl gömme somun M5 | Pirinç insert | 6 | - | - | - | fiyat yok | 6,27 | - | - | bulunamadı | Hiçbir sitede insert M5 yok. |

## Toplam (fiyatı bulunan 14 tablo satırı; bulunamayanlar hariç)

| | TL |
|---|---|
| Eski toplam (bulunan kalemlerin maliyet.json karşılığı) | 45.186,57 |
| Yeni toplam (onaylı satıcı) | 32.996,33 |
| Fark | -12.190,24 |
| Bulunamayan 6 kalemin eski toplamı (fiyat yok, ayrıca eklenecek) | 9.371,40 |

Not: Fark büyük ölçüde iki ekran kaleminin 12.424,50 TL'lik referansından geliyor (kafa ekranı referansı 10,1" idi, 7" ile -10.035,80; göğüs ekranı 1024×600 ile -6.454,87). Ekranlar hariç tutulursa yeni toplam referansın üstüne çıkar (filament +6.035,92, motor braketi +1.067,24, mikrofon dizisi +1.152,29).

## Bulunamayanlar

- Omni teker Ø127 mm / ≥30 kg / 12 mm altıgen (2 adet): onaylı sitelerde yok.
- Rulman 6808-2RS (4 adet): yok.
- Rulman 625ZZ 5×16×5 (5 adet): yok (Motorobit'tekinin ölçüsü 5×21,5×7).
- PETG-CF filament (1,5 kg): yok.
- Isıl gömme somun M3 (168 adet) ve M5 (6 adet): yok (Direnc M3 insert stoksuz ve ölçü uyumsuz).
- Tam ürün olarak yok: 8" HDMI kafa ekranı (7" ile ikame), kardioid/shotgun mikrofon (yönlü), MAX98357A I2S amfi, XVF3800 mikrofon dizisi, ReSpeaker Lite.

## Muadilde dikkat

- Göğüs ekranı: 1024×600 (CAD 1280×800 varsayıyorsa çözünürlük ve en-boy oranı değişir), kasasız (gömme için kasa / çerçeve tasarlanmalı), dış ölçü sayfada yok. Waveshare wiki sayfasından mm ölçüsü alınmalı.
- Kafa ekranı: 8" yerine 7" (dokunmatikli, HDMI + USB dokunmatik kablosu gerekir). Kafa içi mikro HDMI kablosu ayrı kalem.
- Mikrofon dizisi: v2.0 (XVF-3000) araştırmada ana mikrofon ise XVF3800'e göre eski; 16 kHz örnekleme sınırı sayfada yazıyor. Gürültü bastırma ayrı bir madde olarak sayfada yok, yalnız "konuşma algoritmaları, DoA, BF, AEC".
- Yönlü mikrofon: MAX9814 yönlü değil. Araştırmanın merkezindeki yönlü kayıt için bu kalem tasarımda yeniden düşünülmeli.
- Ses amfisi: PAM8403 analog; I2S bağlantısı yok, USB ses kartı çıkışına bağlanır.
- Motor braketi: Pololu L tipi, düz kelepçe değil; JGB37 7 mm kaçık mil / delik düzeni görselden kontrol edilmeli.
- Servo horn: malzeme belirtilmiyor.
- Filament: Direnc stok adedi listeden alındı (siyah 12, beyaz 5); büyük siparişte stok teyidi gerekir. Karbon katkı yok.

## Ekran ve mikrofon seçenekleri

### Göğüs ekranı (10,1", HDMI, kapasitif, kasalı tercih)

| Seçenek | Site / fiyat | Çözünürlük | Dokunmatik | Kasa | Stok | Dış ölçü (mm) |
|---|---|---|---|---|---|---|
| A (seçilen) WaveShare 10.1" LCD (E) | Robotistan 5.969,63 | 1024×600 IPS, tam lamine | Kapasitif, 10 nokta, 6H cam, USB | Yok | Var | Sayfada yok |
| B WaveShare 10.1" HDMI LCD (B) muhafazalı | Direnc.net 8.126,92 | 1280×800 IPS | Kapasitif, 6H cam, USB | Akrilik arka tutucu, 45° eğim; kutuda HDMI kablosu + 5V/3A adaptör | Yok | Sayfada yok (ağırlık 0,851 kg) |
| C Raspberry Pi 10.1" 1024×600 HDMI | Robocombo 4.500,00 | 1024×600 | Dirençli (rezistif), SPI dokunmatik pinleri | Yok | 63 | Sayfada yok |
| D WaveShare 10.1" QLED | Motorobit 15.300,00 | 1280×720 | Kapasitif | - | 10 | Sayfada yok (referanstan pahalı) |

En iyi: B, stoka girerse (1280×800, kasalı, kapasitif, referanstan 4.297,58 TL ucuz). Şu an stokta olan kapasitifler arasında A. C yalnız dokunmatik gerekmez ya da dirençli kabul edilirse en ucuz (4.500).

### Kafa ekranı (8" istendi, bulunamadı)

| Seçenek | Site / fiyat | Çözünürlük | Dokunmatik | Stok |
|---|---|---|---|---|
| A (seçilen) WaveShare 7" HDMI (C) | Robotistan 2.388,70 | 1024×600 | Kapasitif | Var |
| B Raspberry Pi 7" Kapasitif LCD (H) | Robocombo 2.880,00 | 1024×600 (sayfa açılmadı, arama verisi) | Kapasitif | 15 |
| C Raspberry 7" HDMI LCD (C) | Direnc.net 3.051,76 | 1024×600 IPS | Kapasitif | Var (listede 3) |

Dış ölçüler üç sayfada da mm olarak yazmıyor.

### Mikrofon dizisi

| Seçenek | Fiyat | Mikrofon | Arayüz | DSP / özellik | Stok |
|---|---|---|---|---|---|
| 1 (seçilen) ReSpeaker Mic Array v2.0, Robotistan | 6.652,29 | 4, çok yönlü, SNR 61 dB | USB (UAC 1.0) | XVF-3000: DoA, beamforming, AEC, konuşma algoritmaları; 16 kHz | Var |
| 2 ReSpeaker 2 Mikrofonlu Pi HAT, Robotistan | 1.220,16 | 2 | Pi GPIO (WM8960 codec) | DSP / yön bulma yok (sayfada) | Var |
| 3 Direnc INMP441 I2S mikrofon modülü (4 adet kurulum) | 151,23 / adet (604,92) | 1 / modül, çok yönlü | I2S | Donanım DSP yok; DOA / bastırma yazılımla (liste verisi, sayfa tek tek açılmadı) | 562 |

En iyi: 1 (tek USB, çip üstü DoA/AEC içeren seçenek). Seçenek 2 ve 3 araştırma konusunun (gürültülü ortamda anlama) donanım DSP'sini sağlamaz; ucuz ama yazılım yükü getirir.

## Kaynaklar (erişim 01.11.2026)

Ürün sayfaları ve arama: robotistan.com/arama, motorobit.com/arama, direnc.net/arama, robocombo.com (mağaza arama servisi + ürün sayfaları). Karşılaştırma fiyatı: `planlama/maliyet.json` `tl` alanı.
