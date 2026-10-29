# Lale: elektrik kararları (düzeltme planı 3. adım: E0–E4, E7, K4)

Tarih: 15 Ekim 2026. Tek yer: bu dosya. CAD karşılığı `tasarim/freecad/taban/` ve `kafa/`, sayılar `taban-analiz.json`
(`donus`, `aku`) ve `kafa-analiz.json` (`tork`, `isi`, `pi`). "Tahmini" yazan değer ölçülmedi ya da kaynaktan türetildi.
Pin planı E5'in başlangıcıdır, kesin değildir. Akü süreleri E8'in (5. adım) işi, burada yalnız anlık akımlar var.
T2 takip düzeltmesi (15 Ekim 2026, bağımsız kontrol `K3-kontrol.md`): JGB37 tork uyarısı, ESP32 beslemesi ifadesi, DTR/RTS, ön şarj, PC817 3,3 V, Pololu akımı, kafa ısısı (`T2-takip.md`).

## 1,65 m güncellemesi (Y2b, 29 Ekim 2026)

Bu dosyanın gövdesi 125 cm tasarım (15 Ekim) içindir; Nextion satırları yerinde [ESKİ] işaretlendi. 1,65 m ana tasarımda değişen ve
geçerli kalanlar aşağıda. Kaynak: `tasarim/freecad/taban/taban-analiz.json` (Y2a, robot 24,80 kg), `planlama/y2/Y2b-aku.py` →
`Y2b-aku.json` (E8 yeniden), `planlama/y2/Y2b-ivme.json`, `planlama/kararlar-2026-10-29.md`. Yeni yük değerleri tahmini.

| Konu | 125 cm (bu dosyanın gövdesi) | 1,65 m (geçerli) |
|---|---|---|
| Akü | Victron SuperPack 12,8/20, taban arka bölmesi | **Aynı yerde** (75 mm öne geometrik olarak olmadı). Karar 29.10: rampada / eğimde kollar ev pozunda ve taban ivmesi ≤ 0,1 m/s²; düzde ≤ 0,5 m/s² (devrilme sınırı ≈ 2,0 m/s², `Y2b-ivme.json`) |
| Acil stop, devreye alma (E3, E9) | K1 40 A (GPIO12, IRLZ44N #1), K2 7 A + 5,6 Ω ön şarj (GPIO2, IRLZ44N #2), PC817 #1 mantar sonrası (GPIO23), #2 anahtarlı bara (GPIO5), F5 2 A | **Değişmedi.** Devreye alma komutu Pi'den (telefon kumandası; Nextion yok). CAD'de güç panelinde K1 + soket ve ana sigorta var; K2 ve ön şarj direnci CAD'de yok (M6 CAD, Y3). Pin tablosundaki "GPIO2 boş" çelişkisi Y2b'de düzeltildi |
| Göğüs Nextion | UART2 (GPIO16/17), çevre 5 V'tan 0,8 A | **Yok** (25 Ekim). GPIO16/17 boş, F4 yükü −0,8 A |
| Yüz ekranı | 7" LCD, 2,5 W | 10,1" HDMI (hoca verecek; CAD'de Waveshare 10.1" (B)), 5 V ≈ 0,75 A (≈ 3,75 W, tahmini), Pi USB-A'dan |
| Mikrofon | ReSpeaker Lite, 0,5 W | XVF3800 USB dizi (Efe, 26 Ekim): akımı belgesiz, ~1 W varsayıldı → ölçülecek |
| Kafa 5 V tepe | 18,7 W → 3,7 A | ≈ 20,5 W → **4,1 A** (12 V'tan ≈ 1,8 A; F3 5 A yeter). Pololu D36V50F5'in 12 V'taki sürekli akımı (açık iş 8) daha önemli hâle geldi |
| Omuz servoları (E1) | DS3218MG; hat yoğun 4,4 / 4,7 A | **DS3235** (durma 2,1 A @6 V datasheet; tasarımda 3,0 A ihtiyatlı). Kol ×1,25 ile hat yoğun ≈ **5,4 A**, tepe 7,8 A (taslak kol analizi) → XL4016'nın sürekli 5 A önerisinin üstünde: **hat akımı ölçülmeli**; yetmezse o hat için 20 A düşürücü. Hat sigortası (giriş 7,8 A × 6 / 0,88 / 12,8 ≈ 4,2 A) 7,5 A'de kalır |
| Servo uzatmaları | ~1,3 m | dirsek / bilek 1,93 m, S2 ≈ 1,77 m (`dirsek-analiz.json` `kablo.s1_boy`); durma akımında 2 × 1,93 × 0,052 × 2,5 A ≈ 0,50 V düşüm (servo ≈ 5,5 V görür; tahmini) |
| ESP32 – Pi USB | 1,25 m | ≈ 1,64 m → **2 m** kablo (`maliyet.json`) |
| Kafa 12 V (18 AWG çift) | boyundan | +0,385 m; 1,8 A'de ek düşüm < 0,03 V (ihmal) |
| Taban, dönüş (E0) | 21,73 kg, iz 356 (x ±178) | 24,80 kg, AM (−0,2; 521,3; −13,2), iz 432 (x ±216). Yerinde dönüş μ 0,5: en yüklü motor 15,7 kg·cm = sürekli ×2,49, 2,12 A; ön omniyle ×0,47. Karar aynı: önce ölç, μ ≥ 0,4 → ön omni |
| Akü süreleri (E8) | Victron boşta / normal / yoğun 10,9 / 5,7 / 2,0 sa | **12,2 / 5,9 / 1,8 sa** (akü tarafı 17,0 / 34,9 / 113,4 W; yoğun omniyle 2,1; ders 5,8, fuar 5,1 sa → 8 saatlik fuar için öğle şarjı ya da ikinci akü, değişmedi) |
| Yedek GPIO | GPIO2 (E9 ile K2'ye gitti) | GPIO16 / 17 |

## Özet: ne değişti

| Konu | Önce | Sonra |
|---|---|---|
| Pi 5 | Tabanda, XL4016 "Pi 5,1 V" ile | **Kafada** (K4). Boyundan 12 V + ESP32 USB çıkar; kafada Pololu D36V50F5 5 V/5,5 A |
| Servo beslemesi (E1) | 10 servo tek XL4016 (8 A), güç PCA9685 V+ üstünden | **İki hat:** A = sağ kol + pan, B = sol kol + tilt. İki XL4016 (biri Pi'den boşaldı), 16 AWG, iki dağıtım kartı; PCA9685 V+ boş |
| Sonar (E2) | 5 V echo doğrudan ESP32'ye | 4,7 kΩ / 10 kΩ bölücü (3,40 V) |
| Akü ölçümü (E2) | Yok | 100 kΩ / 18 kΩ bölücü + 100 nF, GPIO36 |
| Acil stop durumu (E2) | Okunmuyor | PC817 #1 mantar sonrası 12 V'u okur; PC817 #2 anahtarlı 12 V barayı okur |
| PCA9685 / BNO055 mantık (E2) | 5 V | 3V3 (ESP32 regülatörü) |
| Acil stop yeniden başlatma (E3) | Mantar bırakılınca röle kendiliğinden çeker | Bobin: F5 → mantar NC → bobin → MOSFET (ESP32 "devreye al", GPIO12). Bırakmak gücü vermez |
| ESP32 beslemesi (E4) | Pi USB'si + çevre 5 V birlikte | Diyotlu VEYA (iki kaynak): asıl çevre 5 V (VIN); USB kablosunun VBUS teline seri 1N5819 (anot Pi tarafında). Pi'ye geri besleme yok, CP2102 VBUS algısı sürer |
| Amfi | Tabanda (I2S 1 m boyundan) | Kafada, Pi'nin yanında |
| Etek ısısı (E7) | Pi + 3 XL4016 + 2 BTS kapalı etekte | Pi ve onun XL'i çıktı (≈ −8…11 W). Fan yeri ayrıldı (ölçüme bağlı), ölçüm planı aşağıda |

## E0: dönüş yükü ve K1

**Hesap:** `tasarim/freecad/taban/donus_hesap.py` (FreeCAD gerekmez; `taban_montaj.py` çağırır → `taban-analiz.json` `donus`).
**Ölçüm gelince yalnız** `arayuz.TABAN['donus']` içindeki `mu_olculen`, `stall_kgcm_olculen`, `stall_A_olculen` doldurulur;
hesap "ölçülen" senaryoyu ekler, karar ona göre verilir.

Varsayımlar (hepsi açık):
- Robot ev pozu 21,73 kg, AM (−0,2; 372,9; −13,8) mm (taban + güncel kafa + montajın geri kalanı + 400 g kablo payı; T2 kafa perdesiyle 21,71 → 21,73, tablo değerleri yuvarlamada aynı). Arka aks daha yüklü: ön 98,6 N, arka 114,5 N.
- Kare yerleşim: iz 356 (teker düzlemi x ±178), aks arası 370 (z ±185), teker r 62,5 mm. Her yandaki iki motor aynı BTS7960'tan paralel sürülür, yani aynı hızda döner.
- JGB37-520 60 dev/dk: durma 21 kg·cm (Direnc.net sayfası), sürekli = durmanın %30'u = 6,3 kg·cm (projedeki ölçüt). Durma akımı 2,8 A (tahmini, `06-aku-secimi.md`), boşta 0,12 A; akım torkla doğrusal.

> **Uyarı (JGB37 torku doğrulanmadı, K3):** 21 kg·cm yalnız satıcı etiketi: Direnc.net sayfasında "Tork 21KG" yazıyor, birim yok, durma mı nominal mi belli değil.
> Aynı motorun Aslong tablosu 1:90 (66 dev/dk) için **durma 9 kg·cm / 1,2 A** veriyor (`raporlar/kaynaklar/06-aku-secimi.md` satır 15); 60 dev/dk (≈ 1:100) için bu ≈ 10 kg·cm.
> Hesap değeri değişmedi (21), yalnız senaryo koşuldu: `T2_donus_9kg.py` (`donus_hesap.py`'yi import eder, arayüz değişmez). Durma 9 kg·cm, sürekli 2,7 kg·cm, durma akımı 1,2 A ile:
>
> | μ | Yerinde dönüş (arka) | Durmanın | Üst sınır | Ön omni | Omni / sürekli 2,7 | Omni düz gidiş çekişmesi |
> |---|---|---|---|---|---|---|
> | 0,4 | 12,1 kg·cm | **%134** | %194 | 2,7 kg·cm | ×1,00 | ×0,68 |
> | 0,5 | 14,9 kg·cm | **%165** | %240 | 2,6 kg·cm | ×0,95 | ×0,86 |
> | 0,6 | 17,7 kg·cm | **%197** | %285 | 2,9 kg·cm | ×1,08 | ×1,08 |
>
> Sonuç: tork gerçekten ~9 kg·cm ise standart tekerle robot **yerinde dönemez** (μ 0,4'te bile motorlar durur); ön omniyle dönüş durmanın %29–33'ü, yani sürekli sınır (%30) civarında (×0,95–1,08; sınırda, ısıl yük izlenmeli).
> Omni + Ø127/Ø125 çap farkı düz gidişte de sürekli değere yaklaşır: Ø125'e yakın omni ya da hız düzeltmesi gerekir. Yazılımdaki "> 2,0 A'de kes" eşiği bu senaryoda geçersiz (durma akımı 1,2 A): eşik ölçümden sonra yazılır.
> Düz sürüşte de pay daralır: `taban-analiz.json` `motor` düz 0,5 m/s² ivmede 2,75 kg·cm (2,7'nin ×1,02), 5° rampa + 0,5 m/s² 5,7 kg·cm (×2,1; durmanın %63'ü).
> **Motor (durma torku + akımı) ve zemin μ ölçümü omni siparişinden ÖNCE yapılmalı** (ölçüm aşağıda). Tork ≤ 10 kg·cm çıkarsa omni tek başına yetmeyebilir: daha düşük devirli (daha yüksek oranlı) JGB37 ya da daha güçlü motor da değerlendirilmeli.
- Sürtünme: Coulomb, her tekerde kuvvet ≤ μN, yönü kayma hızının tersi. Lastik esnemesi için kayma ölçeği 0,05 (kaymanın hıza oranı 0,05'te kuvvet ≈ 0,7 μN; tahmini). Yuvarlanma direnci Crr 0,03. Omni makarası yanal direnci 0,05 (tahmini).
- **Üst sınır** modeli ayrıca: yanal sürtünme tam μN, dönüş direnci katsayısı μ_t = μ / (0,925 + 0,15 R/B) (Wong, *Theory of Ground Vehicles*, kayarak yönlenme yarı ampirik bağıntısı).

| μ | Yerinde dönüş, en yüklü motor (arka) | Sürekli 6,3'ün | Durma 21'in | Akım | Üst sınır (R 0) | Ön omni ile |
|---|---|---|---|---|---|---|
| 0,4 | 12,1 kg·cm | ×1,91 | %57 | 1,7 A | 17,5 (×2,78; durmanın %83'ü) | 2,7 kg·cm (×0,43) |
| 0,5 | 14,9 kg·cm | ×2,36 | %71 | 2,0 A | 21,6 (×3,43; **durmanın %103'ü**) | 2,6 kg·cm (×0,41) |
| 0,6 | 17,7 kg·cm | ×2,81 | %84 | 2,4 A | 25,7 (×4,08; **%122**) | 2,9 kg·cm (×0,46) |

- Ön motorlar 9,2 / 11,3 / 13,4 kg·cm. Dönme merkezi ağır arka aksa ~26 mm kayar.
- Dönüş ivmesi payı (1 rad/s², I_z ≈ 0,85 kg·m²) motor başına +0,8 kg·cm.
- **Yay çizerek dönüş** (aynı model, u_sol = k·u_sağ): R ≈ 0,12 / 0,37 / 1,10 m için μ 0,5'te 14,8 / 14,4 / 13,0 kg·cm (×2,34 / ×2,29 / ×2,06).
  Üst sınırda R 0,5 / 1 / 2 m: 17,8 / 15,2 / 11,8 kg·cm. Kare yerleşimde yanal kayma yarıçaptan bağımsız olduğu için yay **çok az** yardım eder.
  R ≥ 2 m bile μ 0,5'te sürekli değerin ×1,9'u.
- **Ön omni** (Nexus 14075, Ø127 × 29, 22 makara Ø19, 480 g, 30 kg; [ozrobotics](https://ozrobotics.com/shop/double-aluminum-omni-wheel-5-inches-basic-14075/)): robot arka aks ortası (z −184) etrafında döner, arka tekerler neredeyse saf yuvarlanır.
  Motor yükü 2,6–2,9 kg·cm (×0,41–0,46). Omni Ø127, teker Ø125: aynı motor hızında önler %1,6 hızlı, düz giderken ön motorlara 1,8–2,9 kg·cm çekişme biner (arka 0,2–0,8 fren).
  Kabul edilebilir, ama Ø125'e yakın omni bulunursa o seçilmeli. **Omni teker düzlemi standartla aynı olmalı (x 178):** farklı x'te (163,5) hesap, ayni yandaki ön/arka motorun birbirine karşı çalıştığını gösterdi (arka motor 17 kg·cm fren).

**Sonuç (μ 0,5, ölçüm yok): KÖTÜ.** Yerinde dönüş sürekli değerin %236'sı; üst sınır modelinde durma torkunu aşıyor (μ ≥ 0,5'te robot dönemeyebilir).
**K1 önerisi:** Kararınız aynı kalıyor: önce ölç (aşağıda). Ölçümde μ ≥ 0,4 çıkarsa (beklenen) **(a) ön iki teker omni**. CAD hazır, bayrakla açılır:
`arayuz.TABAN['omni']['aktif'] = True` ya da `TABAN_OMNI=1`. Varsayılan geometri değişmedi.

**Omni CAD (bayrak açıkken, `taban_montaj.py` ile denendi):** 316 parça, taban 8.209,4 g (+680 g: 2 × (480 − 140)), robot 22,39 kg, AM z −7,8 (öne kayar).
Çakışma: taban içi 0, iskelet 0, kabuk 0, bağlantı 119/119. **Teker–etek boşluğu 10,55 mm (hedef 12):** omni 1 mm büyük ve göbek adaptörü ön yüzde. Kabuk ajanı için açık iş (etek ön bant 1,5 mm).
Omni aks yeri aynı olduğu için zeminde 1 mm aşağı çiziliyor; gerçekte ön 1 mm kalkar (0,15°, önemsiz). Göbek: 12 mm altıgen → omni flanşı adaptörü (tahmini; Nexus göbek delik düzeni satıcıdan teyit).
Ana montaj yükleyicisi (`montaj/moduller.py`) teker gruplarını "Teker 125 x 58 (…)" adıyla kuruyor; omni açılırsa "Omni teker 127 x 29 (…)" adı da eklenmeli (montaj klasörü bende değil).

**Yazılım kısıtı (her durumda, K1 (c)):**
- Standart tekerle: yerinde dönüş komutu en çok 90° ve ω ≤ 0,6 rad/s (≈ 2,6 s), ardından en az 3 kat dinlenme (ısıl yük). Yaw ivmesi ≤ 1 rad/s².
  Sürüş sırasında yön değişimi yay ile (R ≥ 1 m, k ≥ 0,5). Bu, yükü yalnız %10–15 azaltır; asıl çözüm omni.
- Akım izleme: BTS7960 IS çıkışları (GPIO32/33) motor başına > 2,0 A ölçülürse 2 s sonra dönüşü kes (μ 0,5'te yerinde dönüş akımı 2,0 A).
- Omni ile: dönme merkezi arka aks ortası. Odometri modeli arka aksta diferansiyel sürüş; ön enkoderler kayma tespiti içindir.

**Ölçüm (ekip, ~1 saat):** (1) Bir JGB37'yi laboratuvar kaynağında 12 V'ta mil kilitli tut, durma akımını oku; tork için 100 mm kol + el kantarı
(F × 0,1 m). (2) Robotu (ya da eşit yüklü tabanı) zeminde yanlamasına el kantarıyla çek: μ = F / (m g). Kullanılacak zeminlerin hepsinde (sınıf, koridor).
(3) Sonuçları `arayuz.TABAN['donus']`'a yaz, `taban_montaj.py` koş.

## E1: servo beslemesi

| Hat | Servolar | Bekleme | Jest anı | Yoğun (kol uzanmış tutuyor + hareket) | Gerçekçi tepe (≤ 100 ms) | Teorik (hepsi durma) |
|---|---|---|---|---|---|---|
| **A**: sağ kol + pan | S1, S2 (DS3218MG; 1,65 m'de DS3235, Y2b bölümü), dirsek, bilek, pan (MG996R) | 0,3 A | 2,8 A | **4,4 A** | 7,7 A | 12,7 A |
| **B**: sol kol + tilt | S1, S2, dirsek, bilek, tilt | 0,4 A | 2,9 A | **4,7 A** | 7,7 A | 12,7 A |

Servo başına varsayım (tahmini): jestte S1 0,8, S2 0,6, dirsek 0,6, bilek 0,4, pan 0,4, tilt 0,5 A; yoğunda 1,5 / 0,9 / 0,9 / 0,5 / 0,6 / 0,9 A;
kalkış anı 2,5 A (MG996R durma 2,5 A @6 V, DS3218MG 2,6 A @6,8 V; `06-aku-secimi.md`). Gerçekçi tepe = 2 servo kalkışta + diğerleri hareket.

- **Seçim: iki XL4016 (8 A modül, sürekli ≤ 5 A önerilir).** Biri yeni değil: K4 ile boşalan Pi XL4016'sı servo B oldu, XL sayısı 3 kalır. Hat başına yoğun yük 4,4 / 4,7 A, sınırın altında.
  Kafa servolarını iki hatta bölmek (pan A, tilt B) yükü dengeliyor. "Sağ kol + kafa / sol kol" bölüşümünde A 5,3 A olurdu.
- Teorik durma (12,7 A) XL4016'nın kendi akım sınırına çarpar: gerilim düşer, servo resetlenebilir, tehlikeli değil. Ölçümde hat sürekli > 5 A ise yedek: o hat için 20 A / 300 W düşürücü modül (fiyat doğrulanmadı).
- XL4016 girişleri: anahtarlı 12 V baradan (röle sonrası), her biri **7,5 A hat sigortası** ile (giriş tepe 7,7 A × 6 V / 0,88 / 12,8 V ≈ 4,1 A).
- XL → dağıtım kartı: **16 AWG** silikon çift (≈ 0,3 m; 0,6 m gidiş-dönüş 8 mΩ → 7,7 A'de 0,06 V).
- **Dağıtım kartı A / B** (ön kat ön bandı, (±72; 205); 70 × 50 pertinaks): 16 AWG klemens → V+ ve GND barası (kalın tel) → 2200 µF (mevcut 4 kondansatörden 2'şer) → 6 adet 3 pinli çıkış (servo uzatmaları).
  Sinyal: PCA9685 kanalından kısa 3 pinli köprüyle kartın sinyal girişine. Bu köprünün V+ ucu kartta bağlı değil. **PCA9685 V+ klemensi boş kalır.**
- Uzatma: servo başına 22 AWG, ~1,3 m. Durma akımında 2,6 m × 0,052 Ω/m × 2,5 A ≈ 0,34 V düşüm (servo 5,66 V görür); kabul. Daha az düşüm istenirse dağıtım traverse seviyesine taşınabilir (iskelet/kabuk işi, açık).

## E2: gerilim seviyeleri

| Sinyal | Çözüm | Değer |
|---|---|---|
| HC-SR04 echo ×3 (5 V) | Bölücü (arayüz kartında): seri 4,7 kΩ, toprağa 10 kΩ | 5 × 10/14,7 = 3,40 V (ESP32 ≤ 3,6 V). Trig 3,3 V yeterli (PCA9685 kanalından, aşağıda). HC-SR04P yalnız yeni alımda: 3,3 V beslenirse echo 3,3 V |
| Akü gerilimi | 100 kΩ / 18 kΩ + 100 nF, ana anahtar sonrası (kapalıyken akım çekmez) | 14,6 V → 2,23 V, 10,0 V → 1,53 V (ESP32 ADC 11 dB doğrusal bölge ≤ 2,45 V). Akım 0,12 mA. Bir kez multimetreyle kalibre et |
| Acil stop durumu | PC817 2 kanal modülü ([Direnc.net, 43,59 TL](https://www.direnc.net/pc817-2-kanal-optokuplor-izolasyon-icin-modul); giriş 3,6–24 V). Kanal 1 mantar NC sonrasındaki düğüm | LOW = mantar serbest, HIGH = basılı ya da F5 attı. **Modülün çıkış tarafı 3,6–30 V için verilmiş, ESP32 3,3 V bunun altında:** montajda 3,3 V'ta çıkışın tam LOW/HIGH verdiği multimetreyle ölçülecek (aşağıdaki not) |
| Anahtarlı 12 V durumu | PC817 kanal 2, röle sonrası bara | LOW = motor/servo gücü var |
| PCA9685 mantık | VCC ← ESP32 3V3 (I2C pull-up'lar 3,3 V'a); OE → GND | Servo gücü V+'tan değil, dağıtım kartından |
| BNO055 | VIN ← 3V3 | Adafruit kartı 3–5 V kabul eder |
| JGB37 enkoder | VCC ← 3V3 (Hall çıkışı 3,3 V) | 5 V gerekirse çıkışa 4,7k/10k bölücü (ölç) |
| ~~Nextion TX (3,0–5,0 V)~~ | **[ESKİ, Y2b: göğüs Nextion kaldırıldı (25 Ekim 2026); bölücü yok, GPIO16/17 boş]** | — |

**PC817 modülü 3,3 V'ta (K3 notu):** modülün giriş tarafı 3,6–24 V (12 V için uygun), ama çıkış tarafı da satıcı sayfasında "3,6–30 V" ve jumper'la yüksek/düşük seçiliyor; ESP32 tarafı 3,3 V nominalin altında.
Montajda: çıkışı açık kolektör gibi kullan (modülün çıkış besleme ucu 3V3'e ya da boş, sinyal ESP32 GPIO'suna dahili pull-up ile), girişe 12 V verip kesip multimetreyle 3,3 V tarafında LOW < 0,4 V ve HIGH > 2,5 V gör.
Olmazsa **alternatif (önerilen yedek, ~10 TL):** arayüz kartına doğrudan iki PC817 (DIP-4): giriş LED'ine seri 2,2 kΩ (12,8 V'ta (12,8 − 1,2) / 2,2 k ≈ 5,3 mA, 14,6 V'ta 6,1 mA, 0,08 W; 1/4 W yeter),
LED'e ters paralel 1N4148 (ters gerilim koruması), çıkış kolektörü → GPIO23 / GPIO5 + 10 kΩ pull-up 3V3'e, emetör GND. PC817 CTR ≥ %50 (5 mA'de ≥ 2,5 mA) → 3,3 V / 10 kΩ = 0,33 mA'i rahat doyurur. Mantık aynı: LED yanık = çıkış LOW.

## E3: acil stop ve yeniden başlatma

```
F5 2 A ─── mantar NC ───┬─── röle K1 bobini (+) ── bobin (−) ── IRLZ44N drain       (bobine ters paralel 1N4007)
                        │                                       IRLZ44N source ── GND
                        └── PC817 #1 giriş (12 V algı)          IRLZ44N gate ── 220 Ω ── GPIO12 ;  gate ── 10 kΩ ── GND
K1 kontağı (40 A): F1 20 A ──> anahtarlı 12 V bara ──> BTS7960 sol/sağ, XL4016 A, XL4016 B  (PC817 #2 bu barayı okur)
```

- Röle yalnız **mantar serbest ve ESP32 "devreye al" (GPIO12 = 1)** iken çeker. Mantar bırakılınca hiçbir şey olmaz; güç ancak operatör komutuyla gelir (Pi komutu: telefon kumandası; Nextion "Devreye al" düğmesi Y2b ile kalktı).
- Yazılım kuralı (ESP32): PC817 #1 HIGH görünce GPIO12'yi hemen 0 yap ve kilitle. Yeniden devreye almadan önce:
  (1) mantar serbest, (2) PCA9685 çıkışları servoların **son bilinen konumuna** yazılmış, (3) BTS EN = 0 ve PWM = 0, (4) açık komut. Sonra GPIO12 = 1.
  PC817 #2 500 ms içinde LOW olmazsa hata ver.
- Açılışta güvenli: GPIO12 boot'ta LOW olmalı (strapping pini). Gate'teki 10 kΩ pull-down hem bunu sağlar hem röleyi kapalı tutar. ESP32 kilitlenirse görev izleyicisi (watchdog) resetler; reset anında pin LOW'a düşer → röle bırakır.
- Kalan risk: yazılım hatası pini 1'de bırakıp mantar bırakılırsa röle yeniden çeker. Donanımla kapatılacaksa: röle kontağına paralel ikinci (kendini tutma) kontak + ayrı başlat butonu (iki kontaklı röle gerekir). Şimdilik yazılım kuralı + watchdog.
- **Pi seri portu DTR/RTS (K3 E-2, yazılım planına satır):** DevKit'teki otomatik reset devresi (CP2102 DTR/RTS → EN/GPIO0) ESP32'yi Pi seri portu açıp kapatırken resetleyebilir.
  Reset → GPIO12 LOW → röle bırakır → servo ve motor gücü kesilir, **kollar düşer**. Pi tarafı portu DTR/RTS değiştirmeden açmalı: pyserial'de port açılmadan önce
  `ser.dtr = False; ser.rts = False` ayarlanıp sonra `ser.open()`, Linux'ta ayrıca `stty -F /dev/ttyUSB0 -hupcl` (kapanışta DTR düşmesin). İlk bağlantı testinde
  ESP32'nin boot mesajı basmadığı (resetlenmediği) görülmeli. Yazılım yine de "ESP32 resetlendi" durumunu ele almalı: reset sonrası röle kapalı açılır, yeniden devreye alma E3 kuralıyla.
- **Ön şarj (E9) önemi arttı (K3):** E3 ile röle her "devreye al"da yeniden çeker. Her seferinde anahtarlı bara üstündeki kondansatörler (XL4016 / BTS giriş kondansatörleri; XL çıkışındaki
  4 × 2200 µF servo kondansatörü de XL üzerinden) boş halden dolar. Victron BMS yüksek kapasitif yükte kesebilir, ~10 s sonra yeniden dener (`06-aku-secimi.md` satır 61, 164).
  Önceden yalnız açılışta olan darbe artık her acil stop sonrasında olur. E9 (5. adım): röle kontağına paralel 10 Ω / 5 W ön şarj direnci + gecikmeli çekme ya da ≥ 30 A NTC; değer için bara kapasitesi ölçülecek.
- MOSFET: IRLZ44N (mantık seviyeli, TO-220; Direnc.net ~26 TL, fiyat doğrulanmadı). Bobin akımı ~0,15 A. Alternatif BC337 + 1 kΩ.
- F5 2 A: bobin 0,15 A + PC817 ~5 mA. Önceki 5 A bu devre için büyüktü, 5 A artık F3/F4'te.

## E4: Pi 5 beslemesi (K4: Pi kafada)

- **Boyundan:** 12 V çift (18 AWG, F3 5 A) + ESP32 USB (veri; 1,25 m; **1,65 m'de ≈ 1,64 m → 2 m kablo**, Y2b) + tilt servo (3 tel). HDMI ve CSI boyundan çıktı (`kafa-analiz.json` `pi`).
- **Kafada çevirici:** Pololu **D36V50F5** ([pololu.com/product/4091](https://www.pololu.com/product/4091)): giriş 5,5–50 V, çıkış 5 V (%4), tipik 5,5 A **36 V girişte**; ürün sayfasındaki 3,5–8 A aralığı **tüm giriş aralığı** içindir (giriş gerilimine ve ısıya bağlı), 12 V'a özel bir değer değildir.
  12 V girişteki sürekli akım üreticinin grafiğinden okunup teyit edilecek (açık iş 8); kafa tepe 3,7 A kısa süreli, tipik 2,3 A.
  Ters gerilim −40 V, aşırı akım, kısa devre, aşırı sıcaklık, çıkış alt/üst gerilim koruması, yumuşak başlatma. 25,4 × 25,4 × 9,5 mm, 7 g.
  P raporundaki D24V50F5 yerine bu seçildi: 50 V giriş payı (12 V hatta motor/röle sıçramaları) ve korumalar. Türkiye stoğu bulunamadı (USD 39,95).
- **Kafa 5 V bütçesi:** Pi 5 12 W tepe + 7" LCD 2,5 W (Pi USB-A'dan) + amfi 3 W tepe + kamera 0,7 + mikrofon 0,5 ≈ 18,7 W → 3,7 A (36 V'taki 5,5 A'in %68'i; aralığın alt ucu 3,5 A'in biraz üstü, bu yüzden 12 V eğrisi teyit edilmeli). 12 V'tan 1,6 A tepe.
- **Bağlantı:** çevirici VOUT → kısa USB-C erkek ucu (20 AWG, ~10 cm) → Pi USB-C. PD yok, bu yüzden:
  - EEPROM'a `PSU_MAX_CURRENT=5000` (`sudo rpi-eeprom-config --edit`): firmware PD pazarlığını atlar, 5 A kaynak varsayar ([raspberrypi.com](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html), bootloader yapılandırması).
  - `config.txt`: `usb_max_current_enable=1` (aynı belge; USB-A çıkış sınırını kaldırır, LCD için gerekli).
- **TVS:** 5 V çıkışa P6KE6.8A (5,8 V tutma, 6,45–7,14 V kırılma), kafa girişinde 12 V'a P6KE18A (15,3 V tutma; LiFePO4 şarjda 14,6 V). Delikli gövde, klemense lehimlenir.
- **ESP32 çift besleme (diyotlu VEYA, iki kaynak):** asıl kaynak çevre 5 V → VIN. Pi'ye giden USB kablosunun VBUS teline seri **1N5819** (anot Pi tarafında). VBUS kesilmez:
  CP2102'nin VBUS pini bağlantı algısıdır, kesilirse kart USB'de görünmeyebilir. Diyot sayesinde çevre 5 V Pi'ye geri beslemez; çevre 5 V düşerse ESP32 Pi'den ~4,4–4,7 V alır (zararsız, ESP32 çalışır).
  Kartın kendi VBUS→VIN diyodu doğrulanırsa (DOIT DevKit V1 şemasında var) bu diyot gerekmez. Montajda multimetreyle bakılacak.
- ~~**Nextion** artık Pi'den değil ESP32'den sürülür (UART2).~~ **[ESKİ, Y2b: göğüs Nextion kaldırıldı; ESP32 Nextion sürücüsü işi düştü.]**

## K4: kafa CAD özeti (sayılar `kafa-analiz.json`)

| | Önce | Sonra |
|---|---|---|
| Parça / kütle | 98 / 1.363,1 g | 115 / 1.431,3 g (+68,2: Pi + soğutucu 58, 4 burç + 8 vida ~3, çevirici 7, amfi 2, köpük); T2 yarık + perde sonrası **1.443,5 g** |
| Tilt grubu (kablo payı 25 g dahil) | 833,4 g, 4,46 kg·cm, **pay 2,11** | 926,6 g, 4,64 kg·cm (yerçekimi 2,62 @30° + ivme 2,02), **pay 2,03** (P tahmini 1,96); T2 sonrası 938,8 g, 4,67 kg·cm, **pay 2,01** |
| Pan | 2,6 kg·cm, pay 3,6 | 2,64 kg·cm, pay 3,6; üst rulman eksenel 10,1 → 11,0 N |
| Tilt mili yük paylaşımı | horn 4,07 N / pim 4,11 N | 4,55 / 4,54 N (açık iş: tilt servosuna ikinci rulman) |
| Hareket aralığı | tilt −25…40 serbest, pan ±180 | aynı (çarpan poz kümesi birebir aynı) |

- Yer: Pi kartı köşesi (x −34, z +1), kart altı y 191 (4 × M2,5×8 pirinç burç; alttan M2,5×8 tabladan, üstten M2,5×5; tabla delikleri Ø2,9).
  Pi ↔ kafa iskeleti 6,6 mm, ↔ arka kabuk 7,5 mm; tilt taramasında (−25…30°) Pan/Gövde grubuna en az 31,6 mm. Soğutucu üstü y 208,5, tavana 64 mm.
- Çevirici (−75; 44) ve amfi (65; 44) tablada 1 mm köpük bant + kablo bağıyla. Çevirici ↔ kablo geçişi ~25 mm, amfi ↔ LCD HDMI bloğu 11,6 mm.
- Kamera FPC **300 mm** (Pi 5 22 pin 0,5 mm → 15 pin 1 mm); micro HDMI → HDMI **25–30 cm**; kısa USB-C güç ucu. Kafa içi kablolar referans (kütleye 25 g nokta yük olarak tork hesabında).
- **Havalandırma (arka kabuk; T2 ile baca etkisi için yeniden yerleşti):** giriş **altta**: arka duvar alt bandı 2 × 5 yarık 3 × 40 = 1.200 mm² (y 185–220, Pi'nin hemen arkası).
  Çıkış **üstte**: arka duvar üst bandı 2 × 4 yarık (y 234–261) + iki yan duvarın düz bölgesinin en üstü 2'şer yarık (y 234–246, z −50…−10) = 1.440 mm². Giriş–çıkış merkez yükseklik farkı 42,5 mm (önce 12,5 mm; önceki çıkış y 198–246).
  **Emiş perdesi:** arka kabukla tek parça 2 mm yatay levha (x −45…48, y 221–223, arka duvardan z −5'e), Active Cooler'ın 12,5 mm üstünde: taze hava giriş yarıklarından perde altından fana, sıcak hava perdenin önünden yukarı ve üst banttan dışarı; üstteki sıcak havanın fana geri emilmesini azaltır.
  Eski 8 alt yarık (1.120 mm², servo bölmesi) yerinde. Arka kabuk baskısı desteksiz kaldı (0 sorun), 263,1 → 275,3 g (perde +12 g); tilt payı 2,03 → 2,01.
- **Isı (el hesabı, 30 °C ortam, kafa içi ortalama hava; `kafa-analiz.json` `isi`):** kafa gücü boşta / tipik / en kötü 7,2 / 11,4 / 14,5 W.
  Kapalı kafa 39 / 45 / **49 °C** (servo sınırı 55 °C).
  **Önceki "yarıklı 34–42 °C" iyimserdi (K3):** fanın bütün debisinin yarıklardan geçtiğini varsayıyordu. Active Cooler fanı SoC ~50 °C altında durur, kanalsız fan havayı kafa içinde döndürür, giriş–çıkış farkı 12 mm'ydi.
  Yeni hesap iki sınırla, ikisinde de duvar kaybı paralel: (1) **yalnız doğal çekiş** V̇ = C<sub>d</sub>·A<sub>ef</sub>·√(2gHΔT/T) (C<sub>d</sub> 0,6 tahmini): önceki yarıklarla 38,7 / 43,6 / 47,2 °C, yeni yarıklarla **38,3 / 42,8 / 46,1 °C**
  (kafa küçük, çekiş yalnız ~0,08–0,11 L/s: yükseklik farkını 3 kat artırmak ~1 K kazandırıyor); (2) **iyimser**: fan debisinin tamamı yarıklardan: 33–34 / 34–36 / 36–38 °C.
  **Dürüst aralık: boşta 33–38, tipik 34–43, en kötü 36–46 °C**; perde fanı taze havaya bağladığı ölçüde alt uca yaklaşır, fan duruyorsa (boşta) üst uç geçerli. Pi üst bölmede, oradaki hava ortalamadan sıcak.
  Test şartı (değişmedi): kafa kapalı, stres (stress-ng + animasyon), SoC ≤ 75 °C, tilt servosu gövdesi ≤ 50 °C. Yazılım SoC > 75 °C'de animasyon FPS düşürür. Aşılırsa üst bant arkasına 25–30 mm egzoz fanı (yer var: perde üstü ile tavan arası ~50 mm).
- **Servis:** microSD −X'e bakar (x −49…−34, z −17…−37). Arka kabuk 2 vidayla (x ±105, z −30) sökülünce SD, USB-A ve Ethernet erişilir. Ön kabuk ve LCD yerinde kalır.
- **Kablo listesi (boyun, dar boğaz 137 mm² mil penceresi):** 12 V çift 18 AWG (7,6 mm²) + ESP32 USB (9,6) + tilt servo (8,5) + pan servo (gövdede) ≈ 26 mm² (%19). Hoparlör yeri açık (Duffy kararı): göğüste olursa +2 tel.
- **Tabanda boşalan Pi yeri** (−90,5; 80): E2/E3 arayüz kartı (70 × 50 pertinaks: bölücüler, PC817, IRLZ44N + 1N4007, klemens).

## E7: etek içi ısı

- **Isı kaynakları (Pi gittikten sonra; tahmini):** XL4016 A/B (hat başına yoğun 4,5 A × 6 V = 27 W çıkış → kayıp 3,7 W), XL4016 çevre (6 W → 0,8 W), BTS7960 ×2 (dönüşte ~0,3 W),
  röle bobini 1,8 W, ESP32 + kartlar ~1 W. Tipik ~8 W, yoğun ~11,5 W. Önceki düzende bunlara Pi (7–10 W) ve onun XL'i (~1 W) ekleniyordu: etek ısısı yaklaşık yarıya indi.
- **Isı yolu:** XL4016 modülünde ısı, IC'nin ve diyodun vidalı olduğu **üstteki** alüminyum soğutucuda. Kart altı ile alt plaka arasına ped koymak ısı kaynağına değmez. 8 mm naylon burç kalıyor (kısa devre koruması), ped/plaka önerilmiyor.
  Isıyı soğutucu üstündeki hava taşır.
- **Fan (ölçüme bağlı):** 40 × 40 × 10 12 V fan, üç XL4016'nın ortasında kat altına asılı, aşağı üfler. Yer `arayuz.BOLGELER` "E7 fan yeri" (x ±25, y 162,5–174,5, z 85–135) olarak ayrıldı; iskelet/kabukla ihlal 0.
  Sıcak hava etek üst açıklığından gövdeye ve etek altından çıkar. Etek arka bandında havalandırma yarıkları: **kabuk için açık iş** (kabuk benim dosyam değil).
- **Ölçüm planı:** 3 XL4016 soğutucusuna, bir BTS7960'a, etek içi havaya (orta) ve akü yüzeyine NTC/termokupl (multimetre ya da ESP32).
  Kabuk kapalı, 25–30 °C ortam, 30 dk "yoğun" profil: servo hatlarına 1,33 Ω / 30 W yük direnci (6 V'ta 4,5 A) ya da kollar uzanmış tutarken. Ardından 5 dk yerinde dönüş/sürüş döngüsü.
  **Ölçüt:** XL4016 soğutucusu ≤ 80 °C, etek havası ≤ 45 °C, akü yüzeyi ≤ 45 °C. Aşılırsa fan + etek yarıkları; yine aşılırsa servo hattı 20 A modüle.

## Blok şema (metin)

```
Akü Victron SuperPack 12,8 V 20 Ah (BMS 30 A sürekli) ── XT60 ── Ana sigorta 30 A ── ASW-A01 ana anahtar ── sigorta kutusu (6 yol)
  │                                                                                   │
  └─ (anahtar sonrası) akü ADC bölücü 100k/18k ── ESP32 GPIO36                         ├─ F1 20 A ── röle K1 kontağı ── anahtarlı 12 V bara (WAGO)
                                                                                      │        ├─ BTS7960 sol ── ön sol + arka sol JGB37 (paralel)
                                                                                      │        ├─ BTS7960 sağ ── ön sağ + arka sağ JGB37 (paralel)
                                                                                      │        ├─ 7,5 A ── XL4016 A 6 V ── 16 AWG ── dağıtım A ── sağ kol (4) + pan
                                                                                      │        ├─ 7,5 A ── XL4016 B 6 V ── 16 AWG ── dağıtım B ── sol kol (4) + tilt
                                                                                      │        └─ PC817 #2 (bara durumu) ── ESP32 GPIO5
                                                                                      ├─ F2 15 A ── yedek
                                                                                      ├─ F3 5 A ── 18 AWG çift, direk ön yüzü, boyun ── KAFA: P6KE18A ── D36V50F5 5 V ── P6KE6.8A
                                                                                      │                                              ├─ USB-C ── Raspberry Pi 5 ── USB-A: 10,1" yüz LCD (dokunmatik+güç), XVF3800 mikrofon dizisi (1,65 m, Y2b)
                                                                                      │                                              │                          ├─ micro HDMI: LCD ; CSI: Camera Module 3 (FPC 300 mm)
                                                                                      │                                              │                          └─ I2S: MAX98357A ── hoparlör (yer açık)
                                                                                      ├─ F4 5 A ── XL4016 çevre 5 V ── ESP32 VIN, sonar ×3, enkoder (3V3 ESP32'den), PCA9685/BNO055 mantık (3V3)
                                                                                      └─ F5 2 A ── mantar NC ── röle K1 bobini ── IRLZ44N ── GND   (PC817 #1 mantar sonrası)
Veri: Pi (kafa) ── USB 1,25 m (VBUS'ta 1N5819) ── ESP32 (taban) ── I2C: PCA9685 (10 servo + 3 sonar trig), BNO055 ; PWM/EN/IS: BTS ×2 ; enkoder ×2 (A/B)
Toprak: akü − ── WAGO yıldız noktası (güç paneli) ── tüm dönüştürücüler; kafa GND 12 V dönüşüyle
```

## Akım bütçesi (anlık, akü tarafı 12,8 V; dönüştürücü verimi XL 0,88, Pololu 0,90, BTS 0,95)

| Yük | Hat | Tipik | Yoğun | Tepe |
|---|---|---|---|---|
| Kafa (Pi + LCD + kamera + amfi + mikrofon) | F3 | 0,89 A (11,4 W) | 1,13 A | 1,62 A |
| Servo A | F1 → 7,5 A | 1,5 A (jest 2,8 A × 6 V) | 2,3 A (4,4 A) | 4,1 A (7,7 A) |
| Servo B | F1 → 7,5 A | 1,5 A | 2,5 A (4,7 A) | 4,1 A |
| Motorlar ×4 (BTS) | F1 | 0,9 A (düz, sabit hız) | **8,0 A (yerinde dönüş μ 0,5: 4 × 2,0)** | 11,2 A (4 × durma) |
| Çevre 5 V (ESP32 0,24 + sensör/enkoder/opto ~0,15; Nextion 0,8 A Y2b ile çıktı) | F4 | 0,4 A [ESKİ, Nextion dahil] | 0,5 A | 0,6 A |
| Röle bobini + PC817 | F5 | 0,15 A | 0,15 A | 0,15 A |
| **Toplam** | | **5,3 A** | **14,6 A** | **21,8 A** (teorik) |

- F1 yükü: yoğun 12,8 A, teorik 19,4 A (≤ 20 A). Ana 30 A ve Victron BMS 30 A sürekli içinde. Omni ile yerinde dönüşte motorlar 4 × 0,45 A, yoğun toplam ≈ 8,4 A.
- Zaman ortalaması ve akü süresi: `taban-analiz.json` `aku` (hat verimleri güncellendi; röle bobini hesapta 0,3 W, gerçekte ~1,8 W: E8, 5. adım).

## Sigorta listesi

| Yer | Değer | Besler | Not |
|---|---|---|---|
| Ana | 30 A | akü + → her şey | XT60 sonrası kablolu yuva (mevcut) |
| F1 | 20 A | röle K1 (ve paralel ön şarj kolu K2 + 5,6 Ω, E9) → anahtarlı 12 V bara | motorlar + iki servo hattı. Ön şarj kolu da F1'den sonra, ayrı sigorta yok |
| F2 | 15 A | yedek | |
| F3 | **5 A** (önce 10 A Pi) | kafa 12 V (18 AWG) | kafa tepe 1,6 A |
| F4 | 5 A | XL4016 çevre 5 V | **ikinci 5 A** (E9): sette tek 5 A var, F3 onu alır |
| F5 | **2 A** (önce 5 A) | acil stop / röle K1 + K2 bobinleri | sette yok: yeni. K1 0,15 A + K2 ~0,03 A + PC817 |
| Hat | 7,5 A × 2 | XL4016 A ve B girişi | kapaklı mini bıçak sigorta yuvası × 2 (yeni) |
| Şarj | 10 A (mini) | XT60 şarj girişi → akü + (ana anahtar öncesi) | E9 / akü raporu önerisi; üçüncü kapaklı yuva (yeni). Şarj cihazı 6 A |

**Sigorta seti (E9, 5. adım):** kutudaki set 5, 10, 2 × 15, 2 × 20 (standart/ATO bıçak). F3 ve F4 iki 5 A ister, bir tane var:
**ikinci 5 A** ve F5 için **2 A** standart bıçak eklenir. Hat yuvaları mini bıçak: 7,5 A × 2 + şarj girişi 10 A. Maliyette tek satır
"Bıçak sigorta (ek)" (5 adet; standart/mini ayrımı modelde), yuvalar "Hat sigortası yuvası" × 3. Setteki 10 A ve bir 15 A yedek kalır.

## E8: akü süreleri (5. adım, akü raporuyla hizalı)

Yöntem akü raporununki (`raporlar/aku-secimi/rapor.html`, `06-aku-secimi.md`): kullanılabilir = nominal × 0,90 (DoD) × 0,90 (yaşlanma,
soğuk, BMS) = **× 0,81**; süre = Wh × 0,81 ÷ akü tarafı W. Akü **Victron SuperPack 12,8/20 = 256 Wh** (K3). Hesap betiği
`planlama/adim5/e8_aku.py` → `e8-aku.json`. Yük değerleri tahmini (yalnız Nextion akımı datasheet'ten).

3. adımın yeni tüketicileri dahil: Pi kafada **Pololu D36V50F5 üzerinden (verim 0,90)**, röle bobini **0,15 A × 12,8 V = 1,9 W** (önce 0,3 / 1,5 W),
XL4016 boşta 0,4 W, PC817 girişleri ~0,13 W, servo bekleme akımı E1 tablosundan (0,7 A × 6 V = 4,2 W). Fan (E7, koşullu) ayrı satırda.

| Yük (yük tarafı, W) | Hat (verim) | Boşta | Normal | Yoğun |
|---|---|---|---|---|
| Pi 5 + Active Cooler | kafa (0,90) | 4,0 | 6,5 | 12,0 (tam yük) |
| 7" yüz LCD | kafa (0,90) | 1,7 | 2,45 | 2,5 |
| Kamera 0,7 + mikrofon 0,5 + amfi | kafa (0,90) | 1,2 | 1,7 | 2,7 |
| Nextion 10,1" | 5 V (0,88) | 2,5 | 3,5 | 4,0 |
| ESP32 + sensör + mantık | 5 V (0,88) | 0,8 | 1,0 | 1,3 |
| Servolar A + B | 6 V (0,88) | 4,2 (bekleme) | 10,2 (%20 jest) | **34,2** (sürekli jest, E1 5,7 A × 6 V) |
| Tahrik 4 × JGB37 | 12 V (0,95) | 0,3 | 5,0 | **36,1** (%40 düz, %20 ivme, %25 rampa, %15 yerinde dönüş 2,0 A/motor) |
| Sabit: röle 1,9 + XL boşta 0,4 + PC817 0,1 | akü | 2,5 | 2,5 | 2,5 |
| **Akü tarafı** | | **19,0 W (1,5 A)** | **36,3 W (2,8 A)** | **104,4 W (8,2 A)** |

| Senaryo | Akü W | Victron 256 Wh | 24 Ah (307 Wh) | 30 Ah (384 Wh) |
|---|---|---|---|---|
| Boşta (sunum bekleme) | 19,0 | 10,9 sa | 13,1 sa | 16,4 sa |
| Normal etkileşim | 36,3 | 5,7 sa | 6,9 sa | 8,6 sa |
| **Yoğun** | **104,4** | **2,0 sa** | 2,4 sa | 3,0 sa |
| Yoğun, ön tekerler omni | 91,9 | 2,3 sa | 2,7 sa | 3,4 sa |
| Ders karışımı (%40 / %50 / %10) | 36,2 | 5,7 sa | 6,9 sa | 8,6 sa |
| Fuar karışımı (%35 / %50 / %15) | 40,5 | 5,1 sa | 6,1 sa | 7,7 sa |
| + E7 fanı (1,2 W, koşullu) | | yoğun 1,96 sa, normal 5,5 sa | | |

- **Yoğun senaryo düzeltme planındaki şartı karşılıyor (≥ 100 W).** Planın "≈ 2,5 sa" değeri 307 Wh (24 Ah) içindi; bu hesapta 24 Ah ile 2,4 sa.
  Seçilen Victron ile **≈ 2,0 sa**.
- **3 saatlik ders:** 134 Wh nominal gerekir (10,5 Ah). Victron 5,7 sa ile rahat.
- **8 saatlik fuar:** 400 Wh nominal gerekir (31 Ah). Victron 5,1 sa ile yetmez: öğle şarjı (6 A ile ≈ 3,5 sa) ya da ikinci akü. Akü raporunun
  sonucuyla aynı.
- Akü raporuyla fark: boşta 14,6 → 19,0 W (servo bekleme 1,5 → 4,2 W, röle 1,5 → 1,9 W, Pololu kaybı), normal 31 → 36 W, yoğun 73 → 104 W
  (yoğun tanımı sürekli jest + yerinde dönüş payı ile ağırlaştırıldı). OZET / `taban-analiz.json` `aku` hâlâ 307 Wh × 0,80 ve röle 0,3 W ile
  hesaplı (10,9 / 32,6 / 80,7 W): **CAD tarafında açık iş** (`tasarim/freecad` bu adımda değişmedi; 6. adımda taban yeniden üretilirken 256 Wh,
  × 0,81 ve bu tablo alınmalı).
- En büyük belirsizlik: servo bekleme ve jest akımı (E1 tahmini) ve yerinde dönüş akımı (K1 ölçümü). Ölçümden sonra `e8_aku.py` yeniden koşulur.

## E9: ön şarj (5. adım kararı)

**Sorun:** E3 ile röle K1 her "devreye al"da çeker. Anahtarlı bara üstündeki boş kondansatörler aküye doğrudan bağlanır: XL4016 A/B ve
BTS7960 ×2 modül giriş elektrolitleri (tahmini 4 × ~470 µF ≈ **2 mF**, ölçülecek) ve XL çıkışındaki 4 × 2200 µF servo kondansatörü (XL üzerinden).
Kablo + kontak ≈ 30 mΩ ile tepe ≈ 13,3 V / 0,03 Ω ≈ 440 A, ~60 µs (tahmini). Victron datasheet dipnotu: yüksek giriş kapasitesinde akü
kesebilir, ~10 sn sonra yeniden dener (`06-aku-secimi.md`). Önceden yalnız açılışta olan bu darbe artık her acil stop sonrasında olur.

| Seçenek | Sonuç |
|---|---|
| Röle kontağına **kalıcı** paralel direnç | **Red.** K1 açıkken (acil stopta) bara direnç üzerinden beslenir: XL4016'lar servolara zayıf güç verir, acil stop delinir. Bara yüklüyse direnç yanar |
| Seri NTC (≥ 30 A) | **Red.** Sürekli akım yolunda: yoğun 12,8 A'de birkaç W ve 100 °C üstü (PETG etek, Tg ≈ 80 °C). Acil stoptan hemen sonra NTC sıcak kalır, darbeyi sınırlamaz. Yük adımlarında gerilim düşürür |
| **Ön şarj rölesi K2 + direnç, K1'e paralel kol** | **Seçildi.** Kol yalnız devreye alma anında ~300 ms kapalı; acil stop iki röleyi birlikte bırakır |

**Devre:**
```
F1 20 A ──┬── K1 kontağı (40 A) ─────────────────────┬── anahtarlı 12 V bara (BTS ×2, 7,5 A ── XL4016 A/B)
          └── K2 kontağı (7 A) ── R_ön 5,6 Ω 11 W ───┘
F5 2 A ── mantar NC ──┬── K1 bobini ── IRLZ44N #1 (GPIO12)      (her bobine ters paralel 1N4007)
                      └── K2 bobini ── IRLZ44N #2 (GPIO2; 220 Ω seri, 10 kΩ pull-down)
```
- **R_ön = 5,6 Ω, 11 W taş (çimento) direnç** (Direnc.net 13,95 TL); **K2 = 12 V 7 A sinyal rölesi** JQC-3F(T73) (18,23 TL), ikinci IRLZ44N + 1N4007.
- **Tepe ön şarj akımı:** 14,6 V / 5,6 Ω = **2,6 A** (BMS 30 A sürekli sınırının onda biri). τ = 5,6 Ω × 2 mF = 11 ms; %99 dolum 56 ms.
  Ön şarj penceresi **300 ms**: XL çıkışındaki 8,8 mF servo kondansatörü de buck üzerinden dolsun.
- **Enerji:** bara ½ · 2 mF · 14,6² ≈ 0,21 J + servo kondansatörleri ½ · 8,8 mF · 6² ≈ 0,16 J; dirençte < 0,5 J, 11 W için ihmal.
- **Ön şarjda yük:** XL4016 A/B servoları bekleme akımıyla besler (≈ 5 W, ≈ 0,4 A): R'de ≈ 2,2 V düşüm, bara ≈ 11 V'a çıkar. K1 kapanınca
  kalan adım ≈ 2 V (darbe enerjisi doğrudan bağlamanın ≈ %2'si). BTS EN = 0 olmalı (E3 kuralı); motorlar ön şarjda çekmez.
- **Hata durumu:** K1 kapanmazsa ya da bara kısa devreyse R'de 13,3² / 5,6 ≈ 32 W (14,6 V'ta 38 W). F1 bu akımı görmez; yazılım K2'yi
  **≤ 1 s** içinde bırakır. Taş direncin kısa süreli aşırı yük dayanımı (tipik 5–10 × P_n, 5 s) seçilen ürün sayfasında yok: doğrulanmadı.
- **Yer:** güç paneli, K1 yanında; direnç panel yüzeyinden ≥ 5 mm yukarıda (ısı), PETG'ye ve kablo demetine değmez. Montaj rehberi B5a adımı.
- **Yazılım (ESP32, E3 dizisine ek):** (1) E3 ön koşulları: mantar serbest, servo hedefleri son konumda, BTS EN = 0, açık komut;
  (2) GPIO2 = 1 (K2); (3) 300 ms bekle, PC817 #2 LOW olmalı (bara var), değilse GPIO2 = 0 ve hata; (4) GPIO12 = 1 (K1);
  (5) 100 ms sonra GPIO2 = 0; (6) PC817 #2 LOW teyidi. Reset ya da acil stopta iki pin de LOW (pull-down), iki röle de bırakır.
- **GPIO2:** E5 pin planındaki son yedek pin (DevKit LED'i; strapping, boot'ta LOW/boş olmalı, 10 kΩ pull-down uygun). Artık yedek GPIO yok.
  PCA9685 kanal 13 alternatifi önerilmez: ESP32 resetlenince PCA çıkışını korur, K2 kapalı kalabilir.
- **Ana anahtar açılışı:** K1 açık olduğundan yalnız F3/F4/F5 girişleri bağlanır (Pololu + XL çevre girişi, tahmini ≤ 0,6 mF). BMS'in bunu kesip
  kesmediği ilk açılışta gözlenir; keserse aynı yöntem ana anahtara uygulanır (malzeme eklenmedi, ölçüme bağlı).
- **Ölçüm (montajda):** bara kapasitesi multimetrenin kapasite kademesiyle (K1 açık, akü ayrık). 2 mF'tan çok büyükse ön şarj penceresi
  5τ + XL dolum payına göre uzatılır; R değişmez.

## Pin planı taslağı (ESP32 DevKit 30 pin; E5 başlangıcı)

| GPIO | İşlev | Not |
|---|---|---|
| 36 (VP) | Akü gerilimi | ADC1; 100k/18k |
| 39 (VN) | Sonar sağ echo | yalnız giriş; bölücü |
| 34 | Sonar orta echo | yalnız giriş; bölücü |
| 35 | Sonar sol echo | yalnız giriş; bölücü |
| 32 | BTS sol IS (R_IS + L_IS) | ADC1; IS direnci modül şemasından (tahmini 1 kΩ) |
| 33 | BTS sağ IS | ADC1 |
| 25 / 26 | BTS sol RPWM / LPWM | |
| 27 / 14 | BTS sağ RPWM / LPWM | 14 boot'ta kısa PWM verir: EN düşük olduğu için zararsız |
| 13 | BTS EN (dört R_EN/L_EN ortak) | 10 kΩ pull-down |
| 12 | Röle "devreye al" (IRLZ44N gate) | strapping: boot'ta LOW olmalı → gate'teki 10 kΩ pull-down sağlar |
| 23 | Acil stop durumu (PC817 #1) | dahili pull-up |
| 5 | Anahtarlı 12 V durumu (PC817 #2) | strapping (SDIO zamanlaması, normal açılışı etkilemez) |
| 21 / 22 | I2C SDA / SCL (PCA9685, BNO055) | 3V3 |
| 17 / 16 | **Boş** (Y2b: Nextion kaldırıldı; önce UART2) | yedek |
| 18 / 19 | Enkoder sol arka A / B | PCNT |
| 4 / 15 | Enkoder sağ arka A / B | 15 strapping: boot'ta yüksek olabilir, sorun değil |
| 1 / 3 | UART0 (USB → Pi) | |
| 2 | **Ön şarj rölesi K2** (IRLZ44N #2 gate; E9) | strapping: boot'ta LOW/boş olmalı → 220 Ω seri + 10 kΩ pull-down (E9). Kart LED'i de bu pinde (yanması zararsız) |

- **PCA9685 kanalları:** 0–4 hat A servoları, 5–9 hat B servoları, 10–12 **sonar trig** (3,3 V, I2C ile ≥ 10 µs darbe), 13–15 yedek. Böylece üç GPIO kazanıldı.
- Ön motorların enkoderleri bağlanmadı (pin yok). Yandaki iki motor aynı sürücüde olduğu için yan başına bir dörtlü enkoder yeter. Ön enkoder istenirse I2C GPIO genişletici (PCF8574 yavaş; PCNT gerekir) ya da ESP32-S3: E5'te karar.
- Kalan yedek (Y2b): GPIO2 E9 ile K2'ye gitti; Nextion kalkınca **GPIO16 / 17** boşaldı (16, 17 ADC değil). XL4016 NTC (E7 ölçümü) için ADC1 pini kalmadı: ölçüm geçici olarak multimetreyle ya da BNO055 sıcaklığıyla.

## Malzeme değişikliği (yalnız bu adım; `planlama/maliyet.json`)

Eklenen ve değişen kalemler maliyet dosyasında `"adim": "3"` alanıyla işaretli. Fiyatı doğrulanmayanlar `durum: tahmini` ve notta "fiyat doğrulanmadı".
Koşullu kalemler (omni, fan) `secenek: "kosullu"` ile toplama girmez.

| Değişiklik | TL |
|---|---|
| Yeni: Pololu D36V50F5 (ithal, 39,95 USD) | 1.952,68 |
| Yeni: USB-C güç ucu, TVS ×2, PC817 modülü (Direnc 43,59, doğrulandı), IRLZ44N, diyot ×2, direnç seti, pertinaks ×3, klemens/header, 16 AWG 2 m, hat sigortası yuvası ×2, bıçak sigorta ×4, ESP32–Pi USB 1,5 m | 730,59 |
| Değişen: kamera FPC 200 → 300 mm (Adafruit 3,16 USD, ithal; 70,44 → 154,45) | +84,01 |
| Değişen: micro HDMI 1,5 m → 25–30 cm (fiyat doğrulanmadı, aynı yazıldı) | 0 |
| XL4016 ×3 (görev değişti, adet aynı), HC-SR04 ×3 (bölücüyle kaldı) | 0 |
| **V3 toplamı (pay ve yedek hariç)** | **69.793,60 → 72.560,88 (+2.767,28; %15 payla +3.182)** |
| Koşullu, toplama girmez: omni ×2 (45,90 USD × 2 = 4.487 TL, ithal) + fan 60 TL | 4.547 |

`tasarim/cad/demo_uret.py` (maliyet sayfası) bu adımda koşulmadı: dosyası bu adımın kapsamında değil.

## Açık işler

1. **Ölçüm (K1):** JGB37 durma torku ve akımı, zemin μ → `arayuz.TABAN['donus']`.
2. **Kabuk:** omni seçilirse etek ön bantta teker boşluğu 10,55 → 12 mm (1,5 mm). Etek arka bandına havalandırma yarıkları (E7). Hoparlör yeri.
3. **Montaj:** `montaj/moduller.py` omni teker adı; ana montaj ve tam tarama (6. adım). `carpisma-sonuc.json` taban ve kafa bölümleri eskidi.
4. **E5:** pin planı kesinleşmesi (ön enkoderler).
5. **E8/E9 (5. adım):** akü süreleri (Victron 256 Wh, röle 1,8 W), sigorta seti.
6. ESP32 kartında VBUS→VIN diyodu kontrolü; JGB37 enkoderinin 3,3 V'ta çalıştığı; BTS7960 modülünde IS direnci.
7. Tilt servosu radyal yük (4,55 N): ikinci rulman açık işi sürüyor.
8. Pololu D36V50F5 Türkiye stoğu yok: ithal ya da 5 V ≥ 5 A ve ≥ 24 V girişli eşdeğer (koruma özellikleri aranır).
   Ayrıca 12 V girişte sürekli akım ürün grafiğinden teyit edilecek (3,5–8 A aralığı tüm giriş için; kafa tepe 3,7 A).
9. **JGB37 tork riski (T2):** 21 kg·cm satıcı etiketi; 9 kg·cm (Aslong 1:90) senaryosunda standart tekerle yerinde dönüş imkânsız, omni sınırda. Motor ve zemin ölçümü omni siparişinden önce.
10. PC817 modülünün 3,3 V çıkış tarafı montajda ölçülecek; olmazsa arayüz kartına doğrudan PC817 + 2,2 kΩ (E2 notu).
11. Yazılım planına: Pi seri portu DTR/RTS değiştirmeden açılır (E3); ESP32 reset = röle bırakır = kollar düşer.
12. E9 ön şarj: röle her "devreye al"da yeniden çektiği için öncelik arttı (E3).
13. Kafa ısı testi (perde + yarıklar): tahmin aralığı geniş (tipik 34–43 °C); ölçümde aşılırsa 25–30 mm egzoz fanı.
