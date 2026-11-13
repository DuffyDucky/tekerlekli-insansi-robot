# 06 – Onaylı satıcı taraması A (güç, sürücü, bağlantı, sarf)

Tarih: 01.11.2026

Kaynak liste: `planlama/maliyet.json` (değiştirilmedi). Satıcılar: Robotistan, Motorobit, Robocombo, Direnc.net. Fiyatlar ürün sayfalarından, KDV dahil TL. Fark TL = (yeni birim − eski birim) × adet. Stok sayfa durumudur, kesin teyit sipariş anında yapılmalı.

| Kalem | İhtiyaç (kısa) | Adet | Site | Ürün adı | URL | Birim fiyat TL | Eski fiyat TL | Fark TL | Stok | Durum | Fark ve not |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Akü | 12,8 V LiFePO4, 20–24 Ah, BMS ≥30 A, ~167×181×77 mm | 1 | - | - | - | - | 4.768,22 | - | - | bulunamadı | Dört sitede 12,8 V LiFePO4 akü paketi yok (aramalar: lifepo4, akü, lityum akü, 12.8v, 12v 20ah/24ah). Yalnız 3,2 V tek hücre (Robotistan IFR32700 5000/6000 mAh, Direnc 1500 mAh) ve BMS/balans kartları var; bunlarla paket kurmak aynı ürün değil (24 Ah için 16 hücre). Eski fiyat Limacell 24 Ah (4768,22); Victron seçeneği 12680,70. |
| Akü şarj cihazı | LiFePO4 4S, 6 A | 1 | Robocombo | IMAX B6 Şarj Cihazı 80W Adaptörlü | https://robocombo.com/imax-b6-sarj-cihazi-80w-adaptorlu-3245 | 1.800,00 | 1.661,40 | 138,60 | var (252 adet) | muadil | Sayfada Li-ion/LiPo/LiFe 1–6 hücre yazıyor ('LiFePO4' geçmiyor); en çok 5,0 A (istenen 6 A değil), giriş 11–18 V DC, adaptör 12 V/5 A (kutu içeriği teyitsiz). Eski fiyattan 138,60 TL pahalı; ucuz onaylı alternatif yok: Motorobit '6V 12V 6A araç akü onarım şarj' 918 TL kurşun-asit tipi, LiFePO4 desteği belirtilmiyor, önerilmez. |
| Kafa 5 V düşürücü (Pi 5) | 12 V giriş → 5 V ≥5 A | 1 | Robocombo | XL4016 8A DC-DC Step Down Voltaj Regülatörü | https://robocombo.com/xl4016-8a-dc-dc-step-down-voltaj-regulatoru-2991 | 120,00 | 1.975,38 | -1.855,38 | var | muadil | Pololu D36V50F5 onaylı sitelerde yok. Ayarlanabilir 8 A step-down; 5,1 V'a multimetreyle ayarlanır. Pololu'daki ters gerilim/aşırı akım/ısı koruması yok (harici sigorta + TVS şart). Daha ucuz: Direnc XL4015 5A 102,84 TL (var) ama 5 A sınırda, Pi 5 tepe akımı için önerilmez. Motorobit HW468 5V 5A 306 TL tükendi. |
| Motor sürücü BTS7960B | BTS7960B 43 A (IBT-2 tipi), yedek dahil | 3 | Robocombo | BTS7960B DC 43A Çift Motor Sürücü | https://robocombo.com/bts7960b-dc-43a-cift-motor-surucu-2867 | 270,00 | 281,08 | -33,24 | var | aynı | Motorobit (459 TL), Direnc (241,97 TL) ve Robotistan (264,20 TL) sayfaları var ama üçü de tükendi. Robocombo sayfası BTS7960B 43 A olarak listeli; kart görseli/üzerindeki yazı teyit edilmedi. |
| Servo sürücü PCA9685 | 16 kanal I2C | 1 | Robocombo | PCA9685 16 Kanal 12 Bit PWM Sürücü Lehimli | https://robocombo.com/pca9685-16-kanal-12-bit-pwm-surucu-lehimli-4603 | 180,00 | 199,53 | -19,53 | var | aynı | Aynı fiyatta lehimsiz sürüm de var (pca9685-16-kanal-12-bit-pwm-servo-motor-surucusu). Diğerleri: Motorobit 397,80 (var), Robotistan klon 246,58 (tükendi), Direnc 241,97 (tükendi). |
| Hafıza kartı | 64 GB A2 microSD | 1 | Robocombo | Sandisk Ultra 64GB MicroSD Kart | https://robocombo.com/sandisk-ultra-64gb-micro-sd-2910 | 990,00 | 2.192,40 | -1.202,40 | var (14 adet) | muadil | Sayfada A1/A2/UHS bilgisi yok, yalnız '120MB/s'. A2 doğrulanamadı. Diğerleri: Direnc SanDisk Ultra 64GB 1361,07 (var); Direnc 64GB Class 10 393,20, Direnc Samsung EVO Plus 937,63, Robocombo Kioxia 64GB 339 ve Samsung EVO Plus 510, Robotistan 64GB 1128,45 hepsi tükendi. |
| Ana sigorta yuvası | Kablolu kapaklı bıçak sigorta yuvası, 12 AWG | 1 | - | - | - | - | 550,00 | - | - | bulunamadı | Robotistan 'Kablolu Bıçak Sigorta Yuvası Standart Boy (ATO/ATC)' 47,98 TL sayfada var ama TÜKENDİ; kablo kesiti sayfada belirtilmiyor. Motorobit/Direnc/Robocombo'da standart boy kablolu yuva yok. |
| Hat sigortası yuvası | Kapaklı mini bıçak sigorta yuvası, kablolu | 4 | Motorobit | Su Geçirmez Mini/Micro Bıçak Sigorta Yuvası - 16AWG | https://www.motorobit.com/su-gecirmez-minimicro-bicak-sigorta-yuvasi-16awg | 36,72 | 40,00 | -13,12 | var | aynı | 16 AWG kablo, 20 A'e kadar sigorta, su sıçramasına karşı kapaklı. Robotistan 'Mini Boy (ATM)' yuvası sayfada var, stokta görünüyor ama fiyat 0,00 görünüyor: fiyat yok. |
| Bıçak sigorta (ek) – standart | Standart bıçak 5 A + 2 A | 2 | Motorobit | 5 Amper ve 2 Amper Oto Sigorta - Bıçak Sigorta (Standart) | https://www.motorobit.com/5-amper-oto-sigorta-bicak-sigorta ; https://www.motorobit.com/2a-maksi-oto-sigorta-bicak-sigorta | 4,28 | 5,00 | -1,44 | var | aynı | İki ayrı ürün; sayfada 'Standart Bıçak Sigorta', 19,1×18,7 mm, 4,28 TL/adet. |
| Bıçak sigorta (ek) – mini | Mini bıçak 7,5 A ×2 + 5 A + 10 A | 4 | Motorobit | 7.5A / 5A / 10A Mini Alçak Profil Oto Sigorta | https://www.motorobit.com/75a-mikro-oto-sigorta-bicak-sigorta ; https://www.motorobit.com/5a-mikro-oto-sigorta-bicak-sigorta ; https://www.motorobit.com/10a-mikro-oto-sigorta-bicak-sigorta | 7,34 | 5,00 | 9,36 | var | muadil | Mini (ATM) değil 'Mini Alçak Profil' (10,9×8,73 mm) sigorta; yuvaya uyumu doğrulanmadı. Sayfada gerçek mini boy yalnız 40 A var. Eski fiyattan pahalı; aynı akımlar standart boyda 4,28 TL ama mini yuvaya girmez. |
| Röle K1 | 12 V 40 A, 5 fişli oto röle (diyotlu) | 1 | Motorobit | MAH-112-C-4 12V 30/40A Otomotiv Rölesi 5-Pin | https://www.motorobit.com/mah-112-c-4-12v-30/40a-otomotiv-rolesi-5-pin | 183,60 | 166,32 | 17,28 | var | muadil | SPDT, 12 V bobin, 30/40 A @14 VDC; sayfada dahili diyot belirtilmiyor (harici 1N4007). Eski fiyattan 17,28 TL pahalı. Daha ucuz adaylar doğrulanamadı: Direnc SLB-12Vdc-SL-CE 40 A 87,71 TL (pin/kontak tipi sayfada yok), Direnc Tianbo TRKP L-S-Z1 87,11 TL (7 pin, uygun değil). |
| Röle soketi | ISO mini, 5 fişli, kablolu | 1 | - | - | - | - | 120,00 | - | - | bulunamadı | Dört sitede oto röle soketi yok (yalnız 8/10/11 pin endüstriyel soketler). Motorobit JD2912-1H (12V 40A, 4 pin, kablolu soketli röle) 385,56 TL var ama 4 pin ve çok pahalı. |
| Acil stop butonu | 40 mm mantar, 1NC, kalıcı | 1 | Motorobit | NP2 BE102 NC Metal Acil Stop Butonu | https://www.motorobit.com/np2-be102-nc-metal-acil-stop-butonu | 306,00 | 231,66 | 74,34 | var | muadil | NC, Ith=10 A, IP40; sayfada 40 mm baş ve kalıcı (kilitli) bilgisi yok: doğrulanmadı. Eski fiyattan 74,34 TL pahalı. Daha ucuz: Direnc Drn956 16 mm (baş 27 mm) 217,77 TL, 40 mm şartını sağlamaz. |
| Hızlı klemens | WAGO 221-413 tipi, 10'lu | 1 | Motorobit | 2273-203 3 Pin Buat Klemensi (Wago) x10 | https://www.motorobit.com/2273-203-3-pin-buat-klemensi | 122,40 | 328,00 | -205,60 | var | muadil | Birim 12,24 TL × 10 adet. Wago 2273: 0,5–2,5 mm² (221-413: 4 mm²'ye kadar); 12 AWG ana kablolarda kullanılamaz, itmeli (kolsuz). 221-413 hiçbir sitede yok. |
| Güç konnektörü XT60 çift | XT60 erkek + dişi | 5 | Robocombo | Amass XT60H-F Dişi (30) + XT60H-M Erkek (30) | https://robocombo.com/amass-xt60h-f-disi-lipo-batarya-guc-konnektor-4912 ; https://robocombo.com/amass-xt60h-m-erkek-lipo-batarya-guc-konnektor-4913 | 60,00 | 43,12 | 84,40 | var | aynı | Çift = iki ürün. Eski fiyattan pahalı; daha ucuz seçenekler stokta yok: Motorobit 15,30+15,30 ve Robotistan 41,30+41,30 tükendi, Direnc XT60 takım 18,87 tükendi. XT60E çifti Robocombo'da 75 TL. |
| XT60 panel tutucu | XT60 panel tutucu, mevcut XT60 dişi ile | 1 | Motorobit | XT60E-M Panel Tipi Erkek Konnektör - XT60 | https://www.motorobit.com/xt60e-m-panel-tipi-erkek-konnektor-xt60 | 61,20 | 60,00 | 1,20 | var | aynı | Mevcut dişi fişle eşleşmesi için panel erkek seçildi. Daha ucuz ama yanlış cins: Direnc XT60E panel DİŞİ 51,42 TL. |
| Makaron seti | 328 parça, kutulu | 1 | Motorobit | 328 Parça Renkli Makaron Seti | https://www.motorobit.com/328-parca-renkli-makaron-seti | 116,28 | 232,50 | -116,22 | var | aynı | 'Kutulu' bilgisi sayfada kontrol edilmedi. Robotistan 328 adet 124,51 (tükendi), Robocombo kutulu 117,00 (tükendi) / ısıyla daralan 135,00 (var). |
| Silikon kablo 16 AWG | Kırmızı + siyah, 1'er m | 2 | Robocombo | 16AWG Kırmızı + 16AWG Siyah Silikon Kablo 1m (2×60) | https://robocombo.com/16awg-kirmizi-silikon-kablo-1m ; https://robocombo.com/16awg-siyah-silikon-kablo-1m | 120,00 | 55,00 | 130,00 | var | aynı | Birim = 1 kırmızı + 1 siyah. Daha ucuz karma: Motorobit kırmızı 52,02 (var) + Robocombo siyah 60 = 112,02/set (Motorobit siyah tükendi); iki site siparişi gerekir. |
| Direnç seti | 1/4 W metal film, karışık | 1 | Robocombo | 300 Parça 30 Çeşit Direnç Seti - 1/4W | https://robocombo.com/300-parca-30-cesit-direnc-seti-14w-3923 | 90,00 | 150,00 | -60,00 | var (649 adet) | muadil | 30 çeşit × 10 adet; metal film/karbon film belirtilmiyor, istenen 8 değerin listede olduğu doğrulanamadı. Motorobit 500 adet set 183,60 tükendi. |
| TVS diyot P6KE6.8A | P6KE6.8A (kafa 5 V) | 1 | Direnc.net | P6KE6V8A Transil Diyot | https://www.direnc.net/p6ke6v8a | 9,07 | 10,00 | -0,93 | var | aynı | Motorobit aynısı 16,52 TL (var). |
| TVS diyot P6KE18A | P6KE18A (kafa 12 V girişi) | 1 | Motorobit | P6KE18A Transil Diyot | https://www.motorobit.com/p6ke18a-transil-diyot | 16,52 | 10,00 | 6,52 | var | aynı | Direnc'te P6KE18A bulunamadı (16A ve 33A var). Eski fiyattan 6,52 TL pahalı; daha ucuz onaylı alternatif yok. |
| Diyot 1N4007 | 1N4007 (röle K1 ve K2 bobini) | 2 | Motorobit | 1N4007 - 1000V 1A Diyot | https://www.motorobit.com/1n4007-1000v-1a-diyot | 0,61 | 3,00 | -4,78 | var | aynı | Direnc 'MIC' 0,73 (var). |
| Diyot 1N5819 | 1N5819 (ESP32 USB VBUS) | 1 | Motorobit | 1N5819 - 1A 40V Diyot | https://www.motorobit.com/1n5819-1a-40v-diyot | 1,22 | 3,00 | -1,78 | var | aynı | Robocombo 1,50, Direnc 1,57. |
| Delikli pertinaks | 70×50 mm | 5 | Direnc.net | 6x13 Delikli Plaket | https://www.direnc.net/6x13-delikli-plaket | 24,20 | 25,00 | -4,00 | var | muadil | 60×130 mm; 70×50 mm kesilerek elde edilir. 5×7 cm olanlar tükendi: Robocombo 39 TL, Robotistan 44,34 TL, Direnc 27,22 TL. |
| Klemens ve pin header | 2'li 5,08 klemens ×4 + 40'lı erkek header ×2 + 15'li dişi header ×2 | 1 | Robocombo + Motorobit | 2 Pin 5.08mm Klemens ×4 (5,50) + 1x40 Erkek Header ×2 (4,28) + 40 pin Dişi Header ×1 (6,00) | https://robocombo.com/2-pin-1-no-508mm-klemens-2511201001 ; https://www.motorobit.com/1x40-erkek-header-40-pin-254mm-180-derece-beyaz ; https://robocombo.com/40-pin-disi-header-180-derece | 36,56 | 80,00 | -43,44 | var | aynı | Toplam 22,00+8,56+6,00. 15'li dişi header için 40'lıdan 2×15 kesilir (1 adet yeter). İki site siparişi gerekir. Robocombo'nun 40 pin erkek header'ı tükendi. |
| ESP32–Pi USB kablosu | USB-A → micro USB, 2 m, veri | 1 | Robocombo | 2 Metre Micro USB 2.0 Kablo | https://robocombo.com/2-metre-micro-usb-2-0-kablo-sarj-kablosu-4143 | 75,00 | 80,00 | -5,00 | var (294 adet) | aynı | Sayfada şarj ve veri bağlantısı yazıyor. |
| USB-C güç ucu | USB-C erkek, lehimli/vidalı uç, ~10 cm 20 AWG | 1 | Motorobit | USB Type-C Erkek 24-Pin Test Kartı | https://www.motorobit.com/usb-type-c-erkek-24-pin-test-karti | 153,00 | 60,00 | 93,00 | var | muadil | Kablosuz erkek Type-C breakout; 20 AWG kabloyu kendin lehimlersin. Eski fiyattan 93 TL pahalı. Daha ucuz: Robocombo Type-C–USB-A 30 cm kablo 51 TL (var) kesilerek kullanılabilir, ancak ince kablo olduğundan 5 A için uygun değil. |
| Etek fanı | 40×40×10 mm 12 V | 1 | Robocombo | 12V Fan (40x40x10mm) | https://robocombo.com/12v-fan-40x40x10mm | 48,00 | 60,00 | -12,00 | var (58 adet) | aynı | Motorobit'te 12 V 40×40×10 yok (10 V ve 24 V var); Direnc 143,37 (tükendi). |
| JR konnektör seti | JR erkek + dişi gövde ×12'şer + krimp pin | 1 | - | - | - | - | 150,00 | - | - | bulunamadı | Hazır JR/servo konnektör seti yok. Motorobit'te Dupont 2,54 gövde/terminal ayrı satılıyor (3 pin gövde 1,22; dişi terminal 0,61 tükendi); JR uyumu sayfada belirtilmediği için eşdeğer sayılmadı. |
| M2,5 pirinç distans seti | M2,5 distans + vida + somun ≈240 parça | 1 | Direnc.net | YP-600 6mm Plastik Distans - M2.5 Vidaya Uygun - 20 Adet | https://www.direnc.net/yp-600-6mm-plastik-distans-m25-vidaya-uygun-20-adet | 65,33 | 300,00 | -234,67 | var | muadil | Pirinç değil plastik, yalnız 20 adet, vida/somun yok. Vida-somun için Robocombo 'M2.5 YSB vida-somun-pul seti 1200 parça' (m2-5-ysb-vida-somun-pul-seti-1200-parca-4511) var, fiyatı çekilmedi: fiyat yok. Pirinç M2.5 distans bulunamadı. |
| Kablo bağı ve yapışkanlı taban | Kablo bağı 2,5×100 (100'lü) + yapışkanlı taban 20×20 (100'lü) | 1 | Direnc.net | 2.5mm x 100mm Kablo Bağı (100 Adet) Siyah | https://www.direnc.net/25mm-x-100mm-kablo-bagi-100-adet-siyah | 27,95 | 180,00 | -152,05 | var | muadil | KISMİ: yalnız kablo bağı bulundu. Yapışkanlı taban yok: Robotistan 19×19 mm 100'lü 106,89 TL tükendi; Motorobit ACT-17 yapışkanlı kablo bağı tek tek 10,40 TL. Eski fiyat iki parça için 180 TL. |
| Cırt kayış | 25 mm, akü bağı (2 × ~0,6 m) | 2 | Motorobit | Lipo Pil Tutucu Cırt Bant 20x400mm - Siyah | https://www.motorobit.com/lipo-pil-tutucu-cirt-bant-20x400mm-siyah | 52,02 | 30,00 | 44,04 | var | muadil | 20 mm genişlik ve 400 mm boy: istenen 25 mm / ~600 mm'den küçük; akü çevresi için kısa kalabilir. Robotistan 20 mm cırt 1 m 118,43 (tükendi). |
| Akü kutup pabucu | M5 halka pabuç 12 AWG ×2 + M5 yaylı pul | 1 | - | - | - | - | 40,00 | - | - | bulunamadı | M5 halka pabuç yok. Motorobit JG6-6 M6 kablo pabucu 11,02 TL (M6 delik) M5 kutup için uymaz. Robocombo 'İzole Pabuç Seti' (285 TL, stok 246) içeriği doğrulanamadı. |
| Bluetooth gamepad | PS4 / Xbox uyumlu kablosuz kol | 1 | - | - | - | - | 750,00 | - | - | bulunamadı | Dört sitede gamepad/PS4/Xbox kolu yok (yalnız micro:bit GamePad 1266,93 TL, uyumlu değil). |

## Toplamlar

- Eşleşen kalemler: eski 9.530,03 TL, yeni 6.163,19 TL, fark -3.366,84 TL.
- Bulunamayan kalemlerin eski fiyatı (yeni toplama dahil değil): 6.378,22 TL.
- Genel eski toplam 15.908,25 TL; yeni toplam 6.163,19 TL (bulunamayanlar hariç).
- Durum sayıları (tablo satırı): {'bulunamadı': 6, 'muadil': 13, 'aynı': 15}.
- Akü satırının eski fiyatı Limacell 24 Ah (4.768,22 TL) alındı; Victron seçeneği 12.680,70 TL idi.

## Bulunamayanlar

- Akü 12,8 V LiFePO4 20–24 Ah (hiçbir sitede paket yok)
- Ana sigorta yuvası (tek aday Robotistan 47,98 TL tükendi)
- Röle soketi (ISO mini 5 fişli)
- JR konnektör seti
- Akü kutup pabucu (M5 halka 12 AWG)
- Bluetooth gamepad (PS4/Xbox uyumlu)
- Kısmi: yapışkanlı kablo bağı tabanı (kablo bağı bulundu)
- Sayfası var ama tükenen: BTS7960B Motorobit/Direnc/Robotistan, XT60 tekil Motorobit/Robotistan, 5×7 pertinaks (hepsi)

## Muadilde dikkat

- Şarj cihazı: IMAX B6 en çok 5 A, LiFePO4 adı geçmiyor (LiFe yazıyor), eski fiyattan pahalı.
- 5 V düşürücü: XL4016 ayarlı modül; koruma yok, çıkış 5,1 V'a elle ayarlanmalı, sigorta + TVS şart.
- Hafıza kartı: A2 doğrulanamadı.
- Mini bıçak sigorta: 'alçak profil' boy, yuva uyumu doğrulanmadı.
- Röle K1: dahili diyot belirtilmiyor; eski fiyattan pahalı.
- Acil stop: 40 mm baş ve kalıcı kilit bilgisi yok.
- Hızlı klemens: Wago 2273-203 yalnız 2,5 mm²; 12 AWG ana kabloda kullanılamaz.
- Direnç seti: metal film ve değer listesi doğrulanamadı.
- Pertinaks: 60×130 plaket kesilecek.
- USB-C ucu: lehimli breakout, kabloyu kullanıcı bağlar.
- Distans: plastik, 20 adet, pirinç değil.
- Cırt kayış: 20 mm / 400 mm, istenenden küçük.
