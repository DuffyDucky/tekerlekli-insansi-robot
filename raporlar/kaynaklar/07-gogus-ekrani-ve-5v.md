# 07 – Göğüs ekranı (1080p) ve Pi 5 için korumalı 5 V düşürücü

Tarih: 01.11.2026

Kapsam: yalnız Robotistan, Motorobit, Robocombo, Direnc.net. Fiyatlar ürün sayfasından, KDV dahil TL. Stok sayfa durumudur (Robotistan "Sepete Ekle" bayrağı, Direnc stok bayrağı, Motorobit "Stokta N ürün", Robocombo mağaza servisi adedi); kesin teyit sipariş anında yapılmalı. `planlama/maliyet.json` değiştirilmedi. Önceki tarama (06-onayli-satici-A/B) tekrarlanmadı.

Yöntem notu: Robotistan, Motorobit, Direnc arama ve kategori sayfaları ile ürün sayfaları açıldı. Robocombo ürünleri sitenin mağaza servisi ve ürün sayfasından okundu. Dış ölçü, Robotistan/Direnc sayfalarında metin olarak yok; Robotistan 11.6" sayfasındaki Waveshare bağlantısından (waveshare.com ürün sayfası, "Exterior-Size.jpg" ölçü çizimi) ve aynı çizimin 13.3" karşılığından okundu. Bunlar satıcı değil üretici datasheet çizimidir; yalnız ölçü için kullanıldı.

## Bulgu özeti

- 10,1" + 1920×1080 (ya da 1920×1200) HDMI kapasitif IPS: dört onaylı sitede BULUNAMADI. 10,1" seçeneklerin hepsi 1024×600, 1280×720 (QLED) ya da 1280×800 (Direnc B, stok yok). Arama: 10.1 / 1920x1080 / 1920x1200 / full hd / hdmi lcd / waveshare 10.1, dört sitede. Motorobit'in 1080p ekranları yalnız 15,6" ve 27".
- 1080p seçenekler 11,6" ve 13,3" ("boyut büyük"). Stokta olan: Robotistan 11,6", Direnc 11,6", Robocombo 13,3".
- Pololu D24V50F5 (5 V, 5 A, tüm korumalı) Robotistan'da stokta; Pololu D36V50F5 yok.

## Tablo 1 – Göğüs ekranı adayları (HDMI, 1080p, kapasitif, IPS)

| # | Ürün | Site / URL | Çözünürlük / panel | Dokunmatik | Aktif alan (mm) | Dış ölçü (mm) | Kalınlık | Besleme | Kasa | Fiyat TL (KDV dahil) | Stok | Boyut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | WaveShare 11.6" Kapasitif Dokunmatik LCD, 1920×1080 HDMI IPS (H, kasalı) | Robotistan https://www.robotistan.com/116-inc-lcd-ekran-modulu | 1920×1080, IPS | 10 noktalı kapasitif, 6H cam, USB | 257,3 × 145,4 (Waveshare çizimi) | 284,65 × 182,25 (Waveshare çizimi; sayfada yok) | 29,5 (çizim, yan görünüş) | 12 V adaptör kutuda; Waveshare wiki: çalışma ~12 V / 0,5 A, 12 V/1 A adaptör; dokunmatik USB 5 V ~80 mA | Var (ABS kasa, halka stand; 75×75 mm M4 duvar deliği) | 9.328,88 (indirimli; liste 10.722,14) | Var | büyük |
| 2 | 11.6inch HDMI LCD Ekran Muhafazalı 1920x1080 IPS (WS16642) | Direnc.net https://www.direnc.net/116inch-hdmi-lcd-ekran-raspberry-pi-uyumlu-1920x1080-ips-teknik-ozellikleri | 1920×1080, IPS | 10 nokta, 6H cam, USB | yazmıyor (1. satırla aynı model: 257,3 × 145,4) | sayfada yok; aynı Waveshare modeli: 284,65 × 182,25 | sayfada yok (çizim 29,5) | 12 V adaptör (AB fiş) dahil | Var (muhafazalı), halka stand, 75×75 mm | 12.695,09 | Var | büyük |
| 3 | 13.3" 1080p Kapasitif Dokunmatik IPS Ekran (Raspberry Pi Uyumlu) | Robocombo https://robocombo.com/13-3-1080p-kapasitif-dokunmatik-ips-ekran-raspbe-4329 | 1920×1080 Full HD, IPS 178° | 10 nokta kapasitif, USB | yazmıyor | sayfada "yaklaşık 310 × 190 mm (çerçeve dahil)" | yazmıyor | sayfada "5V/2A veya 12V DC (modeline göre)" (belirsiz) | "ince gövde, stand ile gelebilir" (kesin değil) | 9.600,00 | Var (6 adet) | büyük |
| 4 | 13.3 inç HDMI LCD (H) Muhafazalı, 1920x1080 IPS (16643) | Direnc.net https://www.direnc.net/13-3-inc-hdmi-lcd-h-1920x1080-ips-dokunmatik-ekran | 1920×1080, IPS | 10 nokta, 6H cam, USB | yazmıyor (sayfada "Ekran Dış Boyutları" görseli var, metin yok) | Waveshare 13.3 (H) çizimi: 329,5 × 207,9 | 22,5 (çizim) | 12 V/1 A adaptör dahil, çalışma ~0,6 A (Waveshare wiki) | Var; 100×100 mm duvar deliği, 60° stand | 11.372,31 | YOK | büyük |
| 5 | 13.3inch HDMI LCD (H) Muhafazalı V2 (WS16644) | Direnc.net https://www.direnc.net/133inch-hdmi-lcd-h-kilifla-v2-1920x1080-ips | 1920×1080, IPS | 10 nokta, 6H cam, USB | yazmıyor | V2 için çizim bakılmadı; V1 çizimi 329,5 × 207,9 | yazmıyor | 12 V adaptör dahil | Var | 11.339,86 | YOK | büyük |
| 6 | 13.3inç Kapasitif Dokunmatik LCD Ekran 1920x1080 IPS | Robotistan https://www.robotistan.com/133-inc-kapasitif-dokunmatik-ekran | 1920×1080, IPS | 10 nokta, 6H cam, USB | yazmıyor | sayfada yok (Waveshare 13.3: 329,5 × 207,9) | yazmıyor | 12 V adaptör dahil (12 V/1 A) | Sayfa hem standlı kasalı hem "muhafazasız versiyona dikkat" diyor, hangisi olduğu belirsiz | 8.886,12 (indirimli; liste 10.356,51) | YOK (tükendi) | büyük |
| 7 | 13.3 inç Kapasitif Dokunmatik Ekran LCD 1920×1080 HDMI IPS (WS17978) | Direnc.net https://www.direnc.net/133-inc-kapasitif-dokunmatik-ekran-lcd-19201080-hdmi-ips | 1920×1080, IPS | kapasitif, 6H cam | yazmıyor | yazmıyor | yazmıyor | yazmıyor | Kasasız görünüyor (sayfada kasa yazmıyor) | 10.600,13 | YOK | büyük |
| 8 | WaveShare 15.6" 1920×1080 Kapasitif Dokunmatik HDMI Ekran | Motorobit https://www.motorobit.com/waveshare-156-19201080-kapasitif-dokunmatik-hdmi-ekran | 1920×1080 | kapasitif | yazmıyor | yazmıyor | yazmıyor | yazmıyor | yazmıyor | 20.073,60 | Var (7 adet) | ÇOK büyük, sığmaz (listelendi, önerilmiyor) |

10,1" ama 1080p OLMAYANLAR (şartı sağlamaz, bilgi için):

| Ürün | Site | Çözünürlük | Fiyat TL | Stok |
|---|---|---|---|---|
| WaveShare 10.1" QLED Kapasitif HDMI, 1280×720 (yazılımla 1920×1080'e kadar ölçekler, donanım 720p) | Motorobit /waveshare-101-1280720-qled-kapasitif-dokunmatik-hdmi-ekran | 1280×720 | 15.300,00 | Var (10) |
| 10.1inç QLED Kapasitif, 1280×720 | Robotistan /101-inc-qled-ekran-modulu | 1280×720 | 7.187,97 (liste 8.091,10) | Var |
| 10.1inch HDMI LCD Muhafazalı 1280×800 IPS | Direnc.net /101inch-hdmi-lcd-raspberry-pi-uyumlu-1280800-ips | 1280×800 | 8.126,92 | YOK |

Notlar:
- Waveshare 11.6" ve 13.3" ekranlar gövdeye yatay gömmek için 10,1" kadar küçük değil: 11,6" gövde 284,65 × 182,25 mm (aktif 257,3 × 145,4), 13,3" gövde 329,5 × 207,9 mm. Gömme kararı için CAD ölçüsüyle kontrol gerek.
- Ölçüler Waveshare "with case" modellerinin çizimidir. Türk satıcı sayfalarında V1/V2 ya da revizyon ayrımı net değil; sipariş öncesi satıcıdan teyit edilmeli.
- Besleme: Waveshare wiki'ye göre ekran kendi 12 V girişinden çalışır (~0,5-0,6 A); LiFePO4 (12,8-14,4 V) hattına doğrudan bağlama aralığı sayfada yok, doğrulanmadı (sigortalı, ayrı 12 V düşürücü ya da adaptör düşünülmeli). Dokunmatik USB'den 5 V ~80 mA.
- Pi 5 bağlantısı: kutuda tam boy HDMI kablosu + HDMI-mikro HDMI adaptörü (Robotistan 11.6" ve 13.3" paket içeriği) ve USB-A→Micro-B dokunmatik kablosu var. Robocombo 13.3" sayfasında uyumluluk "Pi 4/3/Zero/CM4" yazıyor, Pi 5 geçmiyor (HDMI olduğu için çalışması beklenir, sayfada teyit yok).
- Robotistan/Direnc/Motorobit 1080p ekranların hepsi Waveshare; Robocombo 13.3" markası sayfada yazmıyor.

## Tablo 2 – Pi 5 için 5 V düşürücü (12-13 V giriş, sabit 5 V, ≥5 A, korumalı)

| # | Ürün | Site / URL | Giriş | Çıkış / sürekli akım | Korumalar (sayfadan) | Ölçü (mm) | Fiyat TL (KDV dahil) | Stok | Değerlendirme |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Pololu 5 V, 5 A Step-Down Voltaj Regülatör D24V50F5 (PL-2851) | Robotistan https://www.robotistan.com/pololu-5v-5a-step-down-voltaj-regulator-d24v50f5-pl-2851 | maks. 38 V (alt sınır sayfada yazmıyor) | Sabit 5 V (±%4), 5 A sürekli | Entegre ters gerilim koruması, aşırı akım koruması, kısa devre koruması, aşırı sıcaklıkta kapatma (termal shutdown), soft-start, düşük gerilim kilitleme | 17,8 × 20,3 × 8,8 | 2.257,52 | Var | Pololu'nun D36V50F5 yerine geçen modeli; şartların hepsini sayfa metniyle karşılıyor. En iyi seçenek. Pi 5 tepe akımı (5 V/5 A, USB 1,6 A dahil) sınırda; sayfada tepe değeri yok. |
| 2 | Pololu 5 V, 15 A Step-Down Voltaj Regülatör D24V150F5 (PL-2881) | Robotistan https://www.robotistan.com/pololu-5v-15a-step-down-voltaj-regulator-d24v150f5-pl-2881 | 6-40 V | Sabit 5 V (±%4), 15 A sürekli (anlık 32 A) | Ters gerilim, aşırı akım, kısa devre, termal shutdown, soft-start, düşük gerilim kilitleme | sayfada yok | 7.360,46 | Var | Aynı korumalar, 3 kat akım payı; Pi 5'e fazla ve çok pahalı. Başka 5 V yükler (servo hattı) ile birleştirilecekse düşünülebilir. |
| 3 | HCW-P715 9-36V'tan 5V'a 5A Voltaj Düşürücü Regülatör Kartı | Motorobit https://www.motorobit.com/hcw-p715-9-36vtan-5va-5a-voltaj-dusurucu-regulator-karti | 9-36 V | Sabit 5 V, 5 A maks. (sürekli/tepe ayrımı yazmıyor), senkron doğrultma | Sayfada koruma yazmıyor | 63 × 27 | 168,30 | Var (10+) | Korumasız sayılır (sayfada ters gerilim/aşırı akım/termal yok); harici sigorta + TVS şart. Pi 5 için fiziksel olarak uygun, koruma şartını sağlamaz. |
| 4 | WG-1224S0510P DC-DC 12/24V'den 5V 10A Düşürücü Modül (Szwengao) | Motorobit https://www.motorobit.com/wg-1224s0510p-dc-dc-12-24vden-5v-10a-voltaj-dusurucu-modul | 8-36 V (önerilen 12-24 V) | Sabit 5 V, 10 A maks., 25 W, verim %93 | Kısa devre koruması, aşırı akım koruması (ters gerilim ve termal yazmıyor); IP68 | 63 × 32 × 18, kablolu (16 AWG), ~65 g | 630,36 | YOK (Gelince Haber Ver) | Koruma kısmen var, kablolu/IP68 gövde, ama stokta yok. |
| 5 | SY8205 7-30V'tan 5V'a 5A Düşürücü (servo güç kartı) | Motorobit https://www.motorobit.com/sy8205-7-30vtan-5va-5a-voltaj-dusurucu-servo-surucu-guc-karti | 7-30 V | Sabit 5 V; 5 A yalnız tepe/aktif soğutmayla, SÜREKLİ 3,7 A | Sayfada koruma yazmıyor | 43,5 × 20,2 × 5,0 | 146,88 | Var (10+) | Sürekli ≥5 A şartını sağlamaz; elendi. |
| 6 | HW468 5V 5A Voltaj Düşürücü | Motorobit https://www.motorobit.com/hw468-5v-5a-voltaj-dusurucu-regulator-karti | 9-35 V | Sabit 5 V, 5 A, 25 W | Koruma yazmıyor | 45 × 31 × 16 | 306,00 | YOK | Stokta yok, korumasız. |

Elenenler: Direnc.net'te sabit 5 V ≥5 A düşürücü yok (yalnız 3 A'e kadar LM2596 / Mini360 / MP1584 ve ayarlanabilir XL4015/XL4016 kartları). Robocombo'da sabit 5 V ≥5 A düşürücü yok (ayarlanabilir XL4016 / 300 W 20 A kartı ve 3 A'lik USB modül var). Pololu D36V50F5 dört sitede yok.

## Önerim

Göğüs ekranı: 10,1" 1080p onaylı sitelerde yok; 1080p şart ise Robotistan WaveShare 11.6" (1920×1080, kasalı, 284,65 × 182,25 × 29,5 mm, 9.328,88 TL, stokta) ile devam edip gövde ölçüsünü CAD'de doğrula; sığmazsa 10,1" 1280×800/1280×720 seçeneğine dön.
5 V düşürücü: Robotistan Pololu D24V50F5 (PL-2851), 2.257,52 TL, stokta; ters gerilim, aşırı akım, kısa devre ve termal korumalı sabit 5 V / 5 A. Pi 5 tepe akımı için marjı sınırlı olduğundan ana sigorta ve besleme kablosu kesitini buna göre seç.
