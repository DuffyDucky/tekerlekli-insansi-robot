# Lale 1,58 m: ölçüm ve test kâğıtları (P8.3)

Sürüm 08.11.2026. Hazırlayan: tasarım ajanı A (Claude Code), kontrol bekliyor. Proje: Ahmet Yorulmaz.
Bu kâğıtlar parçalar gelince ekibin yapacağı ölçümler içindir. Hiçbiri sipariş ya da karar değildir; sonuç ilgili belgeye
işlenir, karar gerekiyorsa Ahmet Yorulmaz verir.

## Kâğıtlar

| Kod | Kâğıt | Ne zaman | Akü / servo var mı |
|---|---|---|---|
| [T1](T1-jgb37-durma-torku.md) | JGB37-520 durma torku ve akımı | Motorlar gelince, **omni siparişinden önce** | Laboratuvar kaynağı, motor |
| [T2](T2-qled-vbus.md) | 10,1" QLED: Power ↔ Touch VBUS bağı | QLED gelince, **Pi'ye takmadan önce** | Yok (yalnız 5 V adaptör) |
| [T3](T3-kafa-5v-akim.md) | Kafa 5 V hatları: gerilim ve akım | Kafa elektroniği kurulunca, T2'den sonra | Akü ya da laboratuvar kaynağı |
| [T4](T4-pam8403-ses-karti.md) | PAM8403 + USB ses kartı: besleme ve akım | T3'ten sonra | Akü ya da laboratuvar kaynağı |
| [T5](T5-usb-hub-girisi.md) | USB hub girişinde gerilim (yükte) | Hub ve uzatma kablosu takılınca | Akü, ESP32 tabanda |
| [T6](T6-akustik.md) | Akustik: Ø3 delikler, mikrofon–hoparlör, gürültü tabanı | Kafa ve göğüs kapanınca | Akü, servo |
| [T7](T7-gogus-ekrani-12v.md) | Göğüs ekranı 12 V dalı ve jak | Ekran ve regülatör kartı gelince, **ekrana bağlamadan önce** | Laboratuvar kaynağı ya da akü |
| [T8](T8-servo-hatlari.md) | Servo hatları: XL4016 A / B / C yükte | Güç paneli kurulunca, kollar takılmadan önce başlar | Akü, servo |
| [T9](T9-zemin-rampa.md) | Zemin sürtünmesi ve rampa denemesi | Robot yürür hale gelince (sürtünme kısmı daha önce) | Akü, motor, devrilme |

Önerilen sıra: T2 ve T7 ilk (yanlış bağlantı parçayı yakar), T1 ve T9-A omni siparişinden önce, sonra T3 → T4 → T5, T8,
en son T6 ve T9-B.

## Ortak kurallar

1. **Önce güvenlik.** Akülü ya da servolu kâğıtta acil stop düğmesi elde ve bir kez denenmiş olmalı. Akü ana sigortası (30 A)
   ve ilgili dal sigortası takılı olmadan enerji verilmez (`elektrik.md:60`). Yalnız çalışma yok: en az iki kişi.
2. **Varsayım nedir?** Her kâğıdın "Doğruladığı varsayım" tablosunda tasarımın kabul ettiği değer ve kaynağı (dosya:satır) yazar.
   Ölçüm bu değeri doğrular ya da çürütür. "Varsayım" yazan değerin üretici ya da ölçüm dayanağı yoktur.
3. **Yazım.** Ondalık virgül (12,8 V). Her sayının birimi yazılır. Okunmayan değer boş bırakılmaz, "okunmadı" yazılır.
   Ölçü aletinin markası/modeli kâğıdın başına yazılır.
4. **Fotoğraf.** Her düzeneğin bir fotoğrafı çekilir, dosya adı kâğıda yazılır (ör. `T3-duzenek-1.jpg`).
5. **Sonuç.** Kâğıdın sonundaki GEÇER / KALIR kutusu işaretlenir, ölçen ve kontrol eden imzalar. Kalan maddeyi kâğıdın
   "Sınır aşılırsa" bölümündeki belgeye ve kişiye iletin; tasarım değerlerini ekip değiştirmez.
6. **Ses kaydı.** T6'da kayıtlar yalnız seviye hesabı içindir; hesaplanınca silinir (`oneri-taslak-v8.md:199`).
7. **Hareketli parçaya el uzatılmaz.** Motor, servo, kol, kafa ya da teker enerjiliyken hiç kimse ona, konnektörüne ya da ölçü ucuna
   uzanmaz. Hareket varken okunacak her değer için ölçü ucu **enerji yokken** bağlanır, teller hareket alanının dışına çıkarılır,
   alet alan dışında okunur.
8. **Saat, yüzük, bileklik çıkarılır.** Akü ve 12 V baraları kısa devrede çok yüksek akım verir; metal takı yanık yapar.

## Multimetreyle akım ölçümü (bütün kâğıtlar için tek kural)

Akım ölçen T1, T3, T4, T7 ve T8 bu bölüme bağlanır. Kısa tekrarı her kâğıdın güvenlik bölümünde var.

1. **Kırmızı uç 10 A soketine** takılır (mA soketi değil), kademe DC A.
2. Multimetre hatta **yalnız seri** girer: tel açılır, multimetre iki ucun arasına girer. Akım kademesindeki multimetre **asla** iki nokta
   arasına (gerilim ölçer gibi) değdirilmez; bu kaynak ya da akü için kısa devredir.
3. Bağlantı **enerji kapalıyken** yapılır ve sökülür.
4. İş bitince **kırmızı uç hemen V soketine geri** takılır. Unutulursa bir sonraki gerilim ölçümü kaynağı multimetre üzerinden kısa devre eder.
5. **10 A kademesinin süre sınırına uy:** sınır aletin üstünde yazar (çoğunda yüksek akımda birkaç on saniye, sonra uzun soğuma; değeri
   kendi aletinden oku). Dakikalar süren ölçümde multimetre seri kullanılmaz, **akım pensi** kullanılır.
6. Seri multimetre kendi iç direnciyle hatta gerilim düşürür (yüksek akımda kayda değer). Gerilimi her zaman **yükün tarafında**
   (multimetreden sonra) oku ve "seri ölçer takılıydı" diye not düş.
7. Akım pensi tek tele takılır (gidiş ya da dönüş, ikisi birden değil); takmadan önce pens sıfırlanır.

## Ortak alet listesi

| Alet | Hangi kâğıt |
|---|---|
| Dijital multimetre ×2 (DC V, DC A 10 A, direnç, diyot, süreklilik) | hepsi |
| DC akım pensi (en az 10 A, 0,01 A çözünürlük) ya da hatta seri ölçüm köprüsü (klemens) | T3, T4, T8, T9 |
| Ayarlı laboratuvar güç kaynağı 0–30 V / en az 5 A, akım sınırlamalı | T1, T3, T7 |
| USB gerilim/akım ölçer (USB-A erkek–dişi, 0,01 V / 0,01 A) | T4, T5 |
| Dijital el kantarı (bagaj tartısı) ve banyo baskülü | T1, T9 |
| Kumpas, şerit metre, su terazisi, 1 m düz çıta | T1, T6, T7, T9 |
| Ses seviyesi ölçer, dB(A) (yoksa telefon uygulaması, yalnız ayar tekrarı için) | T6 |
| Telefon ivmeölçer uygulaması (ör. phyphox) ya da BNO055 kaydı | T9 |
| Temaslı ya da kızılötesi termometre | T8 |
| Yük dirençleri: 1,33 Ω / 30 W, 24 Ω / 10 W | T8, T7 |

## Kaynak dosyalar (kısaltma → tam yol)

| Kısaltma | Tam yol |
|---|---|
| `elektrik.md` | `planlama/adim3/elektrik.md` |
| `dongu.md` | `planlama/dongu.md` |
| `dongu-158.md` | `planlama/dongu-158.md` |
| `kararlar` | `planlama/kararlar-2026-10-29.md` |
| `karar-kuyrugu.md` | `planlama/d158/karar-kuyrugu.md` |
| `06-aku-secimi.md` | `raporlar/kaynaklar/06-aku-secimi.md` |
| `07-gogus.md` | `raporlar/kaynaklar/07-gogus-ekrani-ve-5v.md` |
| `secenekler.md` | `tasarim/freecad/lale158/kafa-yerlesim/secenekler.md` |
| `uygulama-notu.md` | `tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md` |
| `taban-analiz.json` | `tasarim/freecad/taban/taban-analiz.json` |
| `arayuz.py` | `tasarim/freecad/arayuz.py` |
| `eklem_sinirlari.json` | `kod/ortak/eklem_sinirlari.json` |
| `oneri-taslak-v8.md` | `tubitak-2209b/taslak/oneri-taslak-v8.md` (salt okunur) |
| USB 2.0 belirtimi | USB-IF, *Universal Serial Bus Specification Rev. 2.0*, §7.2.1, Tablo 7-7. **Dış kaynak, depoda yok** |

Satır numaraları 08.11.2026 sürümüne göredir; belge değişirse satır kayabilir, değer aynı kalmalıdır.
