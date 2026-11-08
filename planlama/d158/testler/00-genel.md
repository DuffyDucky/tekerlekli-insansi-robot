# Lale 1,58 m: ölçüm ve test kâğıtları (P8.3, P8.4)

Sürüm 08.11.2026. Hazırlayan: tasarım ajanı A (Claude Code). T1–T9 (P8.3): bağımsız kontrol **GEÇER** (`planlama/d158/F8c-kontrol.md`,
yeniden kontrol 2). T10–T13 ve T1, T4 ekleri (P8.4): bağımsız kontrol **GEÇER** (`planlama/d158/F8d-kontrol.md`, yeniden kontrol 2; T13 için K1, K2 kayıt ajanınca eklendi). Proje: Ahmet Yorulmaz.
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
| [T10](T10-kafa-isi.md) | Kafa ısı testi: kapalı kafada tilt servosu ve Pi | Kafa kapanınca, T3'ten sonra | Akü, kafa servoları (kollar sigortasız) |
| [T11](T11-h1-sigorta-acikligi.md) | H1 servis kapağı: sigorta kutusu açıklığı | Sigorta kutusu gelince, **kablolamadan önce** | Yok (kablosuz kutu) |
| [T12](T12-percin-somun.md) | Perçin somun ve etek delikleri | Perçin somun, ana anahtar ve acil stop gelince, **braketler delinmeden, etek basılmadan önce** | Yok (matkap) |
| [T13](T13-rampada-acil-stop.md) | Rampada acil stop: kayma yolu ve ip yükü | T9-B GEÇER olunca, aynı gün ve aynı ip düzeneğiyle; önce düz zeminde ön şartlar D1–D4 | Akü, motor, devrilme |

Önerilen sıra: T2 ve T7 ilk (yanlış bağlantı parçayı yakar); T11 ve T12 parçalar gelir gelmez (sigorta kutusu kablolanmadan, braketler
delinmeden ve etek basılmadan önce); T1 ve T9-A omni siparişinden önce; sonra T3 → T4 → T5, T8, T10 (kafa kapanınca); en son T6, T9-B ve
hemen ardından T13.

## Ortak kurallar

1. **Önce güvenlik.** Acil stop mantarı robotun etek plakasındadır (`arayuz.py:436`, `arayuz.py:466`); elde taşınan uzaktan acil stop
   **yoktur**. Akülü ya da servolu her kâğıtta: **görevi yalnız mantar olan ayrı bir kişi** vardır ve mantara hareketli parçaların
   (teker, kol, kafa) erişim alanına ve düşme hattına girmeden uzanabilir. Böyle erişilemiyorsa (robot rampada, mantar duvara dönük)
   test yapılmaz. Kumandadaki "devreden çıkar" komutu (röle K1 bırakır, `elektrik.md:216-222`) varsa ek yoldur; denemeden önce robot düz
   zeminde dururken bir kez denenir. **Rampa kâğıtları** ([T9](T9-zemin-rampa.md)-B, [T13](T13-rampada-acil-stop.md)) bu kuralın tek
   istisnasıdır: orada durdurma, T13 ön şartlarıyla (D1–D3) düz zeminde doğrulanmış komut ve iki emniyet ipidir; mantara yalnız robot
   ipte hareketsizken, yandan uzanılır. Komut doğrulanmadıysa rampa kâğıtları yapılmaz. Akü ana sigortası (30 A) ve ilgili dal sigortası
   takılı olmadan enerji verilmez (`elektrik.md:60`). Yalnız çalışma yok: en az iki kişi; rampa kâğıtlarında en az üç (iki ip, bir
   kumanda; kumandayı tutan ip tutmaz).
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

Akım ölçen T1, T3, T4, T7 ve T8 bu bölüme bağlanır (T10'da akım yalnız pensle ve isteğe bağlı). Kısa tekrarı her kâğıdın güvenlik bölümünde var.

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
| DC akım pensi (en az 10 A, 0,01 A çözünürlük) ya da hatta seri ölçüm köprüsü (klemens) | T3, T4, T8, T9, T10 |
| Ayarlı laboratuvar güç kaynağı 0–30 V / en az 5 A, akım sınırlamalı | T1, T3, T7 |
| USB gerilim/akım ölçer (USB-A erkek–dişi, 0,01 V / 0,01 A) | T4, T5 |
| Dijital el kantarı (bagaj tartısı) ve banyo baskülü | T1, T9, T13 |
| Kumpas, şerit metre, su terazisi, 1 m düz çıta | T1, T6, T7, T9, T11, T12, T13 |
| Ses seviyesi ölçer, dB(A) (yoksa telefon uygulaması, yalnız ayar tekrarı için) | T6 |
| Telefon ivmeölçer uygulaması (ör. phyphox) ya da BNO055 kaydı | T9, T13 |
| Temaslı ya da kızılötesi termometre | T8 |
| K tipi termokupl ×3 (ince tel, ≥ 1,5 m) + okuyucu (K tipi girişli multimetre ya da çok kanallı termometre) | T10 |
| İki emniyet ipi, sabit dayanak, kilitli karabina, tripod + telefon (≥ 30 kare/s) | T9, T13 |
| Karton, maket bıçağı, kesme altlığı (açıklık şablonu); sigorta pensesi | T11 |
| Perçin somun pensesi M3–M6, matkap + Ø5,1 / Ø7,1 uç, mengene, hurda 2 mm ve 3 mm Al lama, koruyucu gözlük | T12 |
| Yük dirençleri: 1,33 Ω / 30 W, 24 Ω / 10 W | T8, T7 |

## Kaynak dosyalar (kısaltma → tam yol)

| Kısaltma | Tam yol |
|---|---|
| `elektrik.md` | `planlama/adim3/elektrik.md` |
| `dongu.md` | `planlama/dongu.md` |
| `dongu-158.md` | `planlama/dongu-158.md` |
| `yazilim-plani.md` | `planlama/yazilim-plani.md` |
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
| `qled-not` | `tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md` |
| `P-pi-kafada.md` | `planlama/adim1/P-pi-kafada.md` |
| `duzeltme-plani.md` | `planlama/duzeltme-plani.md` |
| `Y3-kontrol.md` | `planlama/y3/Y3-kontrol.md` |
| `M6-montaj-sirasi.md` | `planlama/adim4/M6-montaj-sirasi.md` |
| `kabuk_parcalar.py` | `tasarim/freecad/kabuk/kabuk_parcalar.py` |
| `kabuk-analiz.json` | `tasarim/freecad/kabuk/kabuk-analiz.json` |
| `uygulama-ivme.json` | `tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json` |
| `adim5/maliyet_duzelt.py` | `planlama/adim5/maliyet_duzelt.py` |
| USB 2.0 belirtimi | USB-IF, *Universal Serial Bus Specification Rev. 2.0*, §7.2.1, Tablo 7-7. **Dış kaynak, depoda yok** |

Satır numaraları 08.11.2026 sürümüne göredir; belge değişirse satır kayabilir, değer aynı kalmalıdır.
