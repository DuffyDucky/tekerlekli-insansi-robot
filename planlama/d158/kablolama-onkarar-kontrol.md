# Kablolama ön kararları (P10.7): bağımsız kontrol (B adımı), 14.11.2026

Kontrol edilen: `planlama/adim3/kablolama-on-kararlar.md` (**R**), `planlama/adim3/elektrik.md` farkı (**EL**), `planlama/d158/karar-kuyrugu.md`
farkı (**KK**), `planlama/d158/kablolama-onkarar-gunluk.md` (**G**), Efe'ye pano taslağı (depo dışı). Karşılaştırma: `pin-haritasi.md` (**PH**),
`planlama/maliyet.json` (**MJ**), pano #5 / #6 / #7 (veri olarak okundu; panoya yazılmadı). Hesaplar elle; hiçbir şey ölçülmedi, betik koşulmadı.
Bu dosya dışında depoda hiçbir şey değişmedi.

## Hüküm: **DÜZELTME GEREKLİ**

Kararların yönü (K1 a, K10 a, K11 a, K14 a, ses ReSpeaker çıkışından, hub USB beslemeli, reset teli yok) savunulabilir ve acil stop listesi
şemayla tutuyor; ama üç güvenlik / besleme bulgusu kapanıştan önce metinde düzelmeli: K10'un "%32 pay"ı yanlış tabana dayanıyor (D1),
K11'in sigorta yuvası girişi yalnız ana 30 A ile korunan bir uçtan alınıyor (D2), R §9'daki "BC337 + 1 kΩ" yedeği K1 rölesini doyuramaz (D3).
Üçü de metin / şart düzeltmesi; kararların seçeneği değişmiyor.

## Durduran bulgular

### D1 · K10: "tepede Pi hattı %66–68, %32 pay" tepe değil, normal + PAM tepesi (besleme) — **durdurur**
- **Nerede:** R:39-40, R:47 ("a'nın tepe payı (%32) yeterken"); EL:52-53; KK K10 Durum satırı ("tepe payı %32").
- **Sorun:** 2,67 A **normal** karşılama değeri ve kalem dökümü yok (`KY/uygulama-notu.md:98`: "2,67 A'nın kalem dökümü dosyada yok";
  EL:31 "Hesap"). 3,28–3,38 A = normal + PAM tepesi; Pi'nin tam yük tepesi içinde değil (EL:29 ve EL:348 "tepe hesaplanmadı").
  AI HAT+ 26T (K2, PAKET A'da planlı; KK:126, 169) Pi'nin 5 V'undan beslenir ve bütçede hiç yok. Kaynak notu da zaten uyarıyor:
  `raporlar/kaynaklar/07-gogus-ekrani-ve-5v.md:47` "Pi 5 tepe akımı (5 V/5 A, USB 1,6 A dahil) sınırda".
- **Kendi hesabım (5 V tarafı, tahmini kalemler işaretli):** Pi 5 + Active Cooler yoğun 12 W (EL:395) = 2,40 A; ReSpeaker 0,18 A (Seeed wiki);
  hub yükü ≈ 0,13 A (göğüs dokunmatiği 0,08 EL:26 + hub denetleyicisi ~0,05 tahmin); kamera 0,7 W (EL:397) = 0,14 A; QLED Touch ~0,05 A (tahmin);
  PAM 3 W ÷ 0,83 (PAM8403 veri sayfası, 4 Ω %10 THD verimi) ÷ 5 V = 0,72 A. **Toplam ≈ 3,6 A (%72).** AI HAT+ takılınca: Hailo-8 tipik
  2,5 W (yalnız satıcı / ikincil kaynak, resmi değer bulunamadı) → +0,5 A ≈ **4,1 A (%82)**; bir incelemedeki "yük altında +4,5 W" ile
  ≈ **4,5 A (%90)**. Pi 5'in kendi tasarım zarfı 5 A (USB 1,6 A dahil; raspberrypi.com güç tablosu): teoride Pi tek başına düşürücüyü doldurabilir.
  Ayrıca PAM akımı sinüs tepesinde ortalamanın ≈ 2 katı (≈ 1,4 A anlık), kondansatörle karşılanır.
- **Sonuç:** a hâlâ seçilebilir (en gerçekçi durumda %72, AI HAT+ ile %80–90), ama "pay %32, yeterli" gerekçesi tutmuyor ve AI HAT+ ile
  sınır daralıyor.
- **Önerilen düzeltme:** R §2, EL:52-53 ve KK K10'daki "%32 pay" yerine "normal + PAM tepesi %66–68; Pi tam yük + PAM ≈ %72, AI HAT+ ile
  ≈ %80–90 (tahmini)" yazılsın. KT1 (T4) şartı genişlesin: Pi stres (stress-ng) + en yüksek ses + (varsa) AI HAT+ çıkarımı aynı anda;
  geçme ölçütü düşük gerilim uyarısı yok **ve** D24V50F5 çıkış akımı ≲ 4 A (ölçüm akım pensi / şönt). Geçmezse c (+61,20 TL). AI HAT+
  siparişi K10'a bağlanmalı (KK K2'ye not).

### D2 · K11: hat sigortası yuvasının girişi yalnız ana 30 A ile korunuyor (sigorta yeri) — **durdurur**
- **Nerede:** R:66-68 ("sigorta kutusunun besleme ucuna … yuva bu uca olabildiğince yakın"), EL:62, EL:68, EL:371, KK K11 Durum satırı.
- **Sorun:** Kutunun besleme ucu ana 30 A'nın arkasındaki bara. Yuva MJ:122 "Su Geçirmez Mini/Micro Bıçak Sigorta Yuvası - **16AWG**": giriş
  pigtail'i 16 AWG ve onu koruyan tek sigorta 30 A. "Olabildiğince yakın" ölçüsüz; uzunluk ve kesit şartı yok. Öbür hat yuvaları (XL4016 A / B / C)
  F1 20 A'nın arkasında, bu dal tek başına 30 A'ya kalıyor.
- **Doğrulanan kısım:** Giriş ana anahtardan sonra (EL:323 blok şema): ana anahtar kapalıyken ekran gerçekten kesiliyor; röleden önce olduğu için
  acil stopta açık. Akım: 6 W ÷ 0,8 ÷ 12,8 V = 0,59 A, 10 V'ta 0,75 A (R'nin sayıları doğru). Ama "~0,5 A" Waveshare wiki'nin tipik değeri, kutudaki
  adaptör 12 V / 1 A (`07-gogus-ekrani-ve-5v.md:19`): ekran 1 A çekerse 10 V'ta ≈ 1,5 A, 2 A sigorta payı 2,7× değil ≈ 1,3× (hâlâ atmaz, pay dar).
- **Önerilen düzeltme (biri):** (a) yuvanın girişi **F2 15 A'nın çıkışına** (F2 bugün "yedek, yük yok", EL:91, röle öncesi): 16 AWG pigtail
  15 A ile korunur, acil stop davranışı aynı, parça aynı; ya da (b) kutunun boş yuvasına standart 2 A bıçak, ayrı hat yuvası kalkar (H1 erişim
  notu EL:378-380'deki yedek yuva düzeniyle birlikte bakılmalı); ya da (c) bugünkü yer, ama "besleme ucundan yuvaya ≤ 10 cm, yuva pigtail'i
  bara kesitinde" şartı yazılsın. R §3'teki "pay ≈ 2,7×" ekran 1 A senaryosuyla birlikte yazılsın.

### D3 · R §9 yedek yolu "BC337 + 1 kΩ" K1 rölesini doyurmaz (röle sürücü) — **durdurur**
- **Nerede:** R:178 ("PH D9'daki delikli BJT yolu (BC337 + 1 kΩ …)"); aynı ifade EL:268'de (bu paketten önce de vardı).
- **Hesap:** 1 kΩ ile en kötü GPIO 2,64 V, V_BE ≈ 0,9 V: I_taban = (2,64 − 0,9) / 1 kΩ − 0,9 / 4,7 kΩ ≈ 1,55 mA. K1 bobini 0,17 A için zorlanmış
  β ≈ 110: BC337'nin en düşük hFE'si (100 @ 100 mA, büyük akımda daha düşük) bu orana yakın, doyum garanti değil; V_CE 1 V'u aşabilir, röle
  sınırda çeker. Doğru değer ve ayrıntı aşağıda "Madde 7" bölümünde (270 Ω).
- **Önerilen düzeltme:** R §9 yedek satırı "BC337(-40) + 270 Ω seri + 4,7 kΩ taban-GND" olsun; EL:268'deki "BC337 + 1 kΩ" C adımında aynı biçimde
  düzeltilsin (pin raporu bu kontrolde değiştirilmedi).

## Öbür bulgular (kayıtlı açık iş olarak gidebilir)

1. **Ses: ReSpeaker jakının şaseye bağlı olup olmadığı belli değil** (R:98-105, KT2). Seeed wiki çıkışı WM8960 kodek ile anıyor; şema
   yayımlanmamış (Seeed forumu). WM8960 kapasitörsüz kulaklık düzeninde jakın kılıfı GND değil, kodeğin orta gerilimine (OUT3) bağlanabilir. Kılıf
   PAM GND'sine bağlanınca kısa devre olur. R'deki "kalkan yalnız PAM girişi GND'sine" bunu varsayıyor. **Öneri:** KT2'ye "PAM'a bağlamadan önce
   ReSpeaker jak kılıfı ↔ USB GND süreklilik ölçümü; süreklilik yoksa kılıf bağlanmaz, girişe seri kondansatör" adımı yazılsın.
   Durdurmaz: tek parçalık ve takmadan önce yapılan bir ölçüm.
2. **Ses: seviye fazla, hoparlör aşırı yüklenebilir** (R:104-105). PAM8403 kazancı 24 dB (veri sayfası test koşulu; bir sürümde 18,5 dB).
   4 Ω'da 3 W için 3,46 V rms çıkış ≈ 0,22 V rms giriş gerekir. Kodek kulaklık çıkışı tam ölçekte ≈ 1 V rms civarında (genel değer, bu kart için
   doğrulanmadı): tam seste ≈ 13 dB kırpılma, kırpılmış kare dalga 3 W'lık hoparlöre 3 W'tan fazla verir. **Öneri:** KT2'de ALSA'da kalıcı bir
   tavan (softvol en çok) ya da girişte gerilim bölücü yazılsın, "en yüksek ses" T4'te bu tavanla denensin.
3. **Ses kararı "masada denenmeden kesinleşmez" sınıfında yazılmalı** (R:109, KK yeni sorular kaydı, EL:28). Üretici doğrulananlar: 3,5 mm
   çıkış var, kart USB ses kartı (UAC 1.0) olarak çalma aygıtı görünüyor ("Select the mic array v2.0 as output device"), AEC var, 6 kanallı
   firmware'de "Channel 5: merged playback", en yüksek 16 kHz. AEC'nin kendi çalma akışını referans aldığı yazılı **değil** (R da bunu "çıkarım"
   diyor). Yedek yol gerçekten duruyor: ses kartı (MJ:78) siparişte, Pi port 2 boş. Ama KK ve EL'de durum "kabul" diye yazılı.
   **Öneri:** "kabul, KT2 + barge-in masa denemesine bağlı" yazılsın; uzatma (−77,46 TL) KT2'den önce iptal edilmesin ya da tekrar alımı not edilsin.
4. **Ahmet'in 04.11 seçimi (K16) değişikliği kayıtta yarım.** R:113-114, R:251 ve KK "yeni sorular" kaydı açık; ama KK K16 maddesi (KK:345-349),
   özet tablo satırı (KK:31) ve EL:145 ("Özet: … PAM8403 + USB ses kartı") hâlâ eski düzeni anlatıyor. **Öneri:** C adımında K16'ya "14.11: ses
   kartı devreden çıktı, yedek; `kablolama-on-kararlar.md` §5" notu, EL:145'e tarih notu.
5. **K14: listedeki HDMI kablosu Ø ≤ 6 şartını karşıladığı bilinmiyor** (R:82). MJ'deki göğüs HDMI'si "HDMI Erkek Mikro HDMI Erkek Altın Uçlu
   Kablo, 1,5 m" (Robotistan, 117,10 TL); "ince / esnek" değil, çapı sayfada yok. R §10 ve §16 bu satırı etkilenenler arasında saymıyor.
   R:84'teki şart (3) ("HDMI fişleri boyundan geçmez: kablo boyuna fişsiz uçtan değil, ekran ucu 90° adaptörle takılır") anlaşılmıyor.
   HDMI A fişinin gövdesi 7,8 mm'lik kenardan büyük. Hangi ucun mil Ø32'den ve 20 × 7,8 kanaldan nasıl geçtiği yazılmalı (kanal açık mı,
   fiş mi geçiyor). **Öneri:** MJ satırına "ince kablo, Ø ≤ 6 doğrulanacak, gerekirse değişir" notu; KT4'e fiş geçişi.
   Kesit sayıları doğru: 10,6 + 5,9 + π·3² (28,27) + 2 × π·2² (25,13) = 69,9 mm²; ÷ 156 = %44,8; ÷ 175 = %39,9; ÷ 204 = %34,3.
   Ses kararı boyundan geçen kabloyu değiştirmiyor. Yeni 3,5 mm kablo kafa içinde, tavandaki diziden sol duvardaki PAM'a gidiyor; hoparlör
   kablosu yine PAM'dan boyundan iniyor.
6. **Reset: gerekçe tutuyor, ama karar Efe'nin cevabından önce boyun demetini kilitliyor** (R:136-155).
   - Bilinçli reset mümkün: CP2102 RTS etkin + DTR etkin değil → EN LOW, IO0 HIGH → normal açılış (esptool'un yöntemi).
   - "Port açılınca reset riski donanımda zaten var" doğru, hatta R'nin yazdığından güçlü: Linux port açılışında DTR ve RTS'yi birlikte etkin
     yapar. pyserial önce DTR'yi, sonra RTS'yi bırakır. Arada DTR bırakılmış, RTS hâlâ etkin bir an kalır, o an EN LOW olur.
     (pyserial kaynağı ve bilinen davranış; burada denenmedi.)
   - Efe'nin önerisinin dayanağı "otomatik reset kapalı kalsın" (pano #7 #22 madde 5). Bu risk ancak devre donanımdan kapatılırsa kalkar; o zaman
     da ayrı bir tel gerekir. Tel kablaj bittikten sonra eklenirse boyun demeti yeniden açılır.
   - **Öneri:** boyun demetine şimdi bir yedek bükümlü çift koymak (≈ 1–2 mm², servo kanalı %44,8 → ≈ %46; R'nin kendi tahmini) ya da K14 demetini
     Efe'nin cevabından sonra kapatmak. KT6'ya "Pi servis yeniden başlatma / yeniden açılış ESP32'yi resetlemiyor" eklensin.
   - Durdurmaz: risk bu paketten önce de vardı; karar onu ne büyütüyor ne küçültüyor.
7. **Hub (Ö2) gerekçesi tutuyor; bir senaryo eksik.** Pi 5 USB çevre birimlerine 5 A kaynakla 1,6 A, aksi hâlde 600 mA verir. Bu bütçe fan
   girişiyle paylaşılır (raspberrypi.com, doğrulandı). Hub normalde ≈ 0,13 A. ESP32 VIN'den beslenir, VBUS'ta 1N5819 var: VBUS tarafı
   ≈ 4,4–4,7 V < VIN 5 V, geri besleme yolu yok. Diyot anodu Pi tarafında (EL:283).
   **Eksik:** F4 atarsa ESP32 tümüyle hub'dan beslenir (0,24 A, EL:353) ve hub ≈ 0,37 A olur. 1,6 A içinde kalır; `PSU_MAX_CURRENT` unutulursa
   600 mA'e karşı ReSpeaker 0,18 + hub 0,37 + QLED Touch ≈ 0,6 A, sınırda. KT5'e "F4 sigortası çıkarılıp hub gerilimi" eklenebilir.
8. **Pano taslağı:** kısa, kaynaklı, kişisel veri / takma ad yok. Sorular (16 kHz / firmware; `esp32_reset()` DTR / RTS ile) Efe'nin
   cevaplayabileceği ve belgelerden çıkmayan sorular. Ama taslağın 4. maddesi "K14'ü … **kapattık**" diyor, durum "kontrol bekliyor".
   "karar verdik, bağımsız kontrol bekliyor" olmalı. Bulgu 6 kabul edilirse yedek çift ve Efe'nin "donanımdan kapatma" niyeti ayrıca sorulmalı.
   Bulgu 1–3 kabul edilirse ses maddesi "masada denenecek" diye yumuşatılmalı.
9. **Acil stop listesi (R §12) doğru, bir ek not:** XL4016 çıkışındaki 8,8 mF servo kondansatörü (EL:448) acil stopta ≈ 0,16 J tutar.
   Servo bırakılırken çok kısa bir son hareket olabilir. Bu yeni değil, bilgi olarak yazılabilir.
10. **62 kablonun dökümü:** ben de depoda bulamadım. "62" yalnız `dongu-158.md:164, :259` (10.11 rehber dökümü), R ve G'de geçiyor.
    `rehber/veri/rehber-veri.json` `adimlar[].kablo` 43 metin girdisi, `semalar` 51 şema: ikisi de 62'lik liste değil. R §11 farkı (−1, ses kartı
    uzatması) dökümden bağımsız ve tutarlı: L dirsek bir kablo değil, 3,5 mm kablonun yalnız ucu değişiyor, göğüs 12 V ara kablosu belirsizliği
    yazılmış.

## Doğruladıklarım

- Acil stopta enerjili / enerjisiz listesi (R:226-234) blok şema EL:323-341, E9 devresi EL:440-444 ve sigorta listesiyle aynı. K2 bobini de mantar
  NC'den sonra (EL:443), ön şarj kolu acil stopta açılamaz. XL4016 C (pan / tilt) anahtarlı barada (EL:330); PCA9685 V+ boş (EL:226).
  Enerjili kalan hiçbir yük hareket üretmiyor (PAM / hoparlör, ekranlar, Pi, ESP32 ve sensör mantığı).
- K11: giriş ana anahtar sonrası; akım hesabı (0,59 / 0,75 A); 18 AWG 2 A için yeterli.
- K14 kesit hesabı ve oranları (yukarıda); ses ve hub kararları demete tel eklemiyor.
- Pi 5 USB 1,6 A / 600 mA ve fan paylaşımı (raspberrypi.com, "Power supply"); `PSU_MAX_CURRENT` açıklaması.
- ReSpeaker v2.0: 3,5 mm çıkış, USB çalma aygıtı, AEC, "merged playback", 16 kHz, 180 / 170 mA (Seeed wiki).
- Maliyet: −77,46 (MJ:136), MOSFET 3 × 8,56 − 2 × 24,40 = −23,12; mini 2 A +7,34 (MJ:123; o satırın notu "F5 2 A standart" diyor, göğse
  ayrılmadığı yönünde).
- KK farkı yalnız K1, K10, K11, K14 Durum satırlarına ve sondaki "yeni sorular" kaydına dokunuyor. K56, K57, K58, P10.5b ve özet tablo / sayım değişmemiş.
  EL farkı yalnız kararların gerektirdiği yerlerde (satır sayısı 522 → 522). Pin tablosu (EL:472-492), EL:5'teki K58 metni ve PH değişmemiş.
- Gizlilik: R, G, EL / KK farkı ve taslakta yerel yol, makine adı, takma ad, e-posta, parola / anahtar, ağ adı yok. "Echo" yalnız "Acoustic Echo
  Cancellation" alıntısında geçiyor.

## Madde 7 · Röle sürücüsü: BC337 mi, IRLML6344 mü (öneri; pin raporu değiştirilmedi)

**Veri (BC337, birden çok üretici veri sayfası):** I_C en çok 800 mA, P_tot 625 mW, V_CEO 45 V; hFE 100–630 @ 100 mA, 1 V
(-16: 100–250, -25: 160–400, -40: 250–630); V_CE(sat) en çok 0,7 V @ 500 mA / 50 mA; V_BE(on) en çok 1,2 V @ 300 mA.

**Taban direnci (R_B; taban-GND 4,7 kΩ akımı 0,8–0,9 V / 4,7 kΩ ≈ 0,17–0,19 mA düşülür):**

| R_B | En az I_B (GPIO 2,64 V, V_BE 0,9 V) | K1 0,17 A zorlanmış β | K2 0,03 A β | En çok GPIO akımı (3,3 V, V_BE 0,7 V) |
|---|---|---|---|---|
| 220 Ω (bugünkü MOSFET ağı) | 7,7 mA | 22 | 4 | **11,8 mA** (> 10) |
| **270 Ω** | 6,25 mA | **27** | 5 | **9,6 mA** |
| 330 Ω | 5,1 mA | 33 (> 30) | 6 | 7,9 mA |
| 1 kΩ (EL:268 / R:178) | 1,55 mA | **110** (doyum garanti değil) | 19 | 2,6 mA |

- **K1:** β ≤ 30 ve GPIO ≤ 10 mA birlikte yalnız ≈ 260–315 Ω aralığında sağlanır; **270 Ω** (E12). β ≤ 20 ile ≤ 10 mA tam tolerans
  aralığında birlikte sağlanamaz (≤ 200 Ω gerekir, o zaman 13 mA). β 27, en düşük hFE grubunun (100) yaklaşık dörtte biri: doyum yeterli.
  -40 grubu seçilirse pay büyür.
- **K2:** 270 Ω ile β ≈ 5 (fazlasıyla doymuş). İstenirse 1 kΩ (β 19, 2,6 mA). Malzemede tek değer için ikisine de 270 Ω.
- **Boşta (dahili pull-up açık, taban ≈ 0,31–0,49 V):** BC337'de 0,65 V'ta ≈ 1 mA kabulüyle 0,49 V'ta I_C ≈ 1 mA · e^(−0,16/0,026) ≈ 2 µA.
  70 °C'de (−2 mV/°C) ≈ 70 µA. Röle bırakma akımı nominalin ~%10'u (≈ 15 mA), çekme %70–75'i: **çektirmez.** Burada BJT, VGS(th) en az
  0,5 V olan IRLML6344'ten sağlam: PH'nin T2'yi ona şart koşma nedeni BJT'de yok.
- **V_CE(sat) ve ısı:** β ≈ 27'de tipik 0,1–0,2 V (veri sayfası sınırı 0,7 V daha ağır koşulda). K1'de P ≤ 0,17 A × 0,3 V ≈ 0,05 W
  (0,7 V'la bile 0,12 W) ≪ 625 mW. Taban kaybı ≈ 6 mW. Bobine 12,6 V kalır.
- **Geri tepme:** her bobine ters paralel 1N4007 var (EL:443, MJ satırı "Diyot 1N4007" adet 2). V_CEO 45 V > 14,6 + 0,7 V. Not: düz diyot
  rölenin bırakma süresini uzatır. Acil stopu mantar kendisi kestiği için güvenlik açısından önemsiz; istenirse diyota seri 18 V zener.
- **Bulunurluk (14.11, Direnc.net arama sayfası, stoktakiler filtresi):** "BC337 Transistör Bjt Npn TO-92 800mA, 45V" 1,21 TL;
  "BC337-40TA … TO-92" 3,02 TL. 3 × 3,02 = 9,06 TL (eski IRLZ44N satırına göre −39,74 TL). 270 Ω'un mevcut direnç setinde (MJ:115)
  olup olmadığı doğrulanmadı.
- **Öneri:** **BC337-40 + 270 Ω seri + 4,7 kΩ taban-GND + 1N4007** (iki röle için aynı). Delikli, adaptörsüz, onaylı satıcıda stokta,
  boştaki pull-up'a duyarsız. IRLML6344 SOT-23 ve adaptör bulunamadı; T2'ye bağlı ve boşta sınırda. Bedeli: pin başına ≈ 6–10 mA GPIO akımı
  ve ≈ 0,1–0,2 V bobin kaybı. T2 (PH §7) BJT için "GPIO = 1'de V_CE < 0,3 V, boşta bobin akımı < 1 mA" diye yeniden yazılmalı. Karar
  orkestratörde; PH ve EL:268 C adımında buna göre.

## Bakamadıklarım

- ReSpeaker v2.0 şeması (yayımlanmamış): jak kılıfı GND mi, çıkış seviyesi (bulgu 1–2 bu yüzden ölçüme bırakıldı).
- Pololu D24V50F5 akım–giriş eğrisi (EL açık iş 8); AI HAT+ 26T'nin resmi güç değeri (yalnız ikincil kaynaklar).
- Waveshare 11,6" en yüksek akımı (yalnız kaynak notundaki "~0,5 A, 12 V / 1 A adaptör"); LM2577 + LM2596 verimi.
- PAM8403 giriş empedansı, modülde ses ayarı olup olmadığı; MJ'deki HDMI kablosunun çapı.
- Motorobit / Robotistan'da BC337 (yalnız Direnc.net okundu); AO3400A ve SOT-23 adaptör aramasını yinelemedim.
- Raspberry Pi GPIO açılış çekmeleri pin pin; CAD ölçüleri ve kablo yolları (betik koşulmadı, LK değerleri yeniden üretilmedi).
- Pyserial / Linux port açılış davranışı yalnız kaynak ve genel bilgiden; donanımda denenmedi.
