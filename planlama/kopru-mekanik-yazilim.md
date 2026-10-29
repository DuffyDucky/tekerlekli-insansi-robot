# Mekanik ↔ yazılım köprüsü (stowent için, 29 Ekim 2026)

Yazan: Ahmet (Duffy) tarafı, yapay zekâ asistanıyla. Okuyan: stowent (Efe) ve onun yapay zekâ oturumları.
Amaç: tasarım/elektrik tarafında alınan kararlarla `kod/` arasındaki farkları tek yerde görmek. Bu dosya karar
vermez; çelişkileri ve kimin karar vereceğini listeler. Karar alınınca ilgili satır güncellenir, ayrıntı
`planlama/kararlar-*.md` karar günlüğüne yazılır (Efe'nin 27 Ekim formatı, iki taraf da bunu kullanır).

## 0. Neden bu dosya var

- `main` dalı (yazılım) `daccdbd`'den çıktı. Tasarım tarafının işi `lale-duzeltme` dalında; o dalda olup
  `main`'de olmayan **20 commit** var (14–29 Ekim düzeltme planı, elektrik kararları, 1,65 m tasarım).
- Bu yüzden şu dosyalar `main`'de **yok**: `planlama/yazilim-plani.md` (11 Ekim yazılım planı),
  `planlama/adim3/elektrik.md` (E0–E9 elektrik kararları), `kod/ortak/eklem_sinirlari.json` (CAD'den çıkan
  eklem sınırları), `planlama/yazilim-notu-stowent-170.md`, `planlama/dongu.md` (1,65 m planı). Hepsi `origin/lale-duzeltme` dalında (29 Ekim 2026'da push edildi); `git show origin/lale-duzeltme:<yol>` ile okunur.
- Sonuç: `kod/` bazı yerlerde eski ya da farklı bir donanım varsayımıyla yazılmış (aşağıdaki tablo).

## 1. Tasarımın güncel durumu (29 Ekim 2026)

| Konu | Karar | Kaynak (`lale-duzeltme`) |
|---|---|---|
| Boy | **1650 mm** (kafa tepesi). Hoca 1,70 istemişti; Duffy 29.10'da 165'e çekti | `planlama/dongu.md` |
| Kol | ×1,25 uzun kol; kol başına **4 servo**: omuz S1 (öne-arka), omuz S2 (yana açma), dirsek, bilek | `kod/ortak/eklem_sinirlari.json` |
| Servolar | Omuz S1 + S2: **DS3235** (35 kg·cm; DS3218 uzun kolda yetmiyor). Dirsek, bilek, kafa pan/tilt: MG996R | `tasarim/freecad/taslak-170/kol-analiz/rapor.html` |
| Toplam servo | 10: 2 × (S1, S2, dirsek, bilek) + kafa pan + kafa tilt | `planlama/yazilim-plani.md` |
| Ekran | Kafada 10,1" HDMI (yüz). **Göğüs Nextion kaldırıldı** (25.10) | `planlama/dongu.md` |
| Pi 5 | **Kafada** (K4). Kafada Pololu D36V50F5 5 V çevirici, PD yok | `planlama/adim3/elektrik.md` E4 |
| ESP32 | Tabanda; Pi'ye tek USB kablo (1,25 m, boyundan) | aynı |
| Taban | 520 mm; **akü yerinde** (75 mm öne geometrik olarak olmadı; karar 29.10, aşağıda) | `planlama/kararlar-2026-10-29.md` |
| Otonomi | Yok (hoca, 21.10): lidar, Nav2, haritalama kapsam dışı. Kumanda telefondan | DuffyOS kaydı, 21.10 |

## 2. Fark tablosu: tasarım ↔ `kod/`

| # | Konu | Tasarım ne diyor | `kod/` ne yapıyor | Kim karar verir |
|---|---|---|---|---|
| F1 | **Kol servo sayısı** | Kol başına 4 eklem (S1, S2, dirsek, bilek) → 10 servo | `kod/jestler/kanallar.yaml`: kol başına 2 (omuz, dirsek) → 6 servo; "omuzda yana açma ekseni yok" notu | Ekip (Duffy + Efe). Tasarım 4 eklemle çiziliyor |
| F2 | **Eklem sınırlarının tek kaynağı** | `kod/ortak/eklem_sinirlari.json` (CAD çakışma taramasından üretilir): S1 −45…135, **S2 +5…120**, dirsek 0…105, bilek −90…90, pan −90…90, **tilt −13…13** (29.10; önce ±15) (eklem açısı, 0 = ev pozu) | `kanallar.yaml` "TEK KAYNAK", 0–180 "robot açısı", sınırlar tahmini | Öneri: `kanallar.yaml` sınırları JSON'dan alsın (ya da `jest_uret.py` JSON'u denetlesin); açı dönüşümü tek tabloda |
| F3 | Omuz servo modeli | DS3235 | `kanallar.yaml`: DS3218 ("yeni model gelince güncellenir" notu var) | Karar verildi (24.10); yalnız güncelleme |
| F4 | **Acil stop / devreye alma** | E3 + E9: güç rölesi K1 (GPIO12) ve ön şarj rölesi K2 (GPIO2) ESP32'de; PC817 #1 mantar durumunu, #2 anahtarlı 12 V'u okur; güç yalnız "devreye al" komutuyla gelir | `pinler.h`: "Emas acil stop ESP32'ye BAĞLI DEĞİL, gücü doğrudan keser"; röle, ön şarj, PC817 yok; GPIO 2 LED | Ekip. Basit yol da savunulabilir, ama elektrik tasarımı (kablaj, ön şarj direnci, röleler, maliyet) şu an E3/E9'a göre |
| F5 | **ESP32 resetlenmesi** | E3: reset = röle bırakır = **kollar düşer**. Pi seri portu **DTR/RTS kapalı** açmalı (`ser.dtr = False; ser.rts = False` sonra `open()`, Linux'ta `stty -hupcl`) | Notlarda "Pi portu açınca DevKit resetlenir, `hazir` beklenmeli" | F4'e bağlı. F4'te röle kalırsa DTR/RTS kapalı açılış zorunlu |
| F6 | Pin çakışması | GPIO12 = K1, GPIO2 = K2, GPIO36 = akü ADC, GPIO39/34/35 = sonar echo, PCA9685 kanal 10–12 = sonar trig | GPIO 2 = LED; 12 bilinçli boş (strapping); sonar/akü ADC yok | F4 ile birlikte. GPIO12 strapping uyarısı haklı, kablajda pull-down ile birlikte bakılmalı |
| F7 | Sensörler | 3 × HC-SR04 (30 cm'de dur), BNO055 eğim alarmı (15°), akü gerilim uyarısı (Y3) | IMU iskeleti var; sonar ve akü izleme yok | Otonomi iptalinden sonra sonar gerekli mi: ekip. Maliyette hâlâ 3 adet var |
| F8 | **Hareket sınırları (1,65 m)** | S2 ≥ +5° (el yüze girer); insan/engel yakınında omuz ≤ ~1,5 rad/s; **rampada ivme ≤ 0,1 m/s², kollar ev pozunda** (29.10 kararıyla zorunlu: akü yerinde); düzde sürüş ≤ 0,5; **fren (yazılım / acil stop) ≤ 1,8 m/s²** (29.10, tek değer; düzde 0,5 kg el yüküyle bile devrilme payı 1,54); el yükü ~100 g (açık); yerinde dönüş yok, yay çizerek dönüş | `motorlar.cpp` `HIZLANMA = 0.5` sabit; rampa ve dönüş sınırı yok; jest hızları `kanallar.yaml`'da | Sınırlar analizden (`yazilim-notu-stowent-170.md`); uygulanması Efe'de |
| F9 | Takılma koruması | DS3235 dirseği geri sürebilir; PWM servo konum bildirmez → öneri: servo hattına akım ölçer (INA219/226) | Yok | Ekip (akım ölçer +maliyet) |
| F10 | Pi güç ayarı | Pololu ile PD yok: EEPROM `PSU_MAX_CURRENT=5000`, `config.txt` `usb_max_current_enable=1` | `kod/PI5-KURULUM.md`'de yok (masada PD adaptörle çalışıyor olabilir) | Robota takılınca şart |
| F11 | Elle sürüş | Y4: Bluetooth gamepad doğrudan ESP32'de (Bluepad32): Pi çökse de sürülür | Telefon kumandası Pi üzerinden (`kod/robot/uzaktan/`) | Ekip. Pi çökerse 500 ms bekçisi zaten durdurur; soru yalnız "Pi'siz sürüş gerekli mi" |
| F12 | Tetik | Bas-konuş düğmesi (maliyette 43 mm buton) | Düğmesiz `SesTetik` (Efe kararı 26.10); GPIO tetik seçenek olarak duruyor | Karar verildi; maliyetten düğme düşer mi: ekip |

### 29.10 kararları — yazılımı etkileyenler

Duffy, 29 Ekim 2026; ayrıntı `planlama/kararlar-2026-10-29.md`, kaynak `planlama/y2/Y2a-kontrol.md` (ikisi de `lale-duzeltme`).

1. **Taban doğrusal ivme ≤ 0,1 m/s²** (devrilme payı için; akü yerinde kalıyor, rampa 5°'de kollar geride pay 1,48–1,49, ölçüt 1,5). → F8, `motorlar.cpp` `HIZLANMA`.
2. **Rampada / eğimde kollar ev pozunda** tutulmalı (ev pozunda pay 1,58; elde 0,5 kg ileri 1,44). → F8.
3. **Kafa tilt sınırı ±13°** (önce ±15; çakışma +18° / −17°'de başlıyor): `kod/ortak/eklem_sinirlari.json` (`lale-duzeltme`). → F2.
4. **El yükü ~100 g ile sınırlı** (servo payı; 0,5 kg'da S1 0,97, dirsek 0,74). **Açık konu**, karar değil. → F8.

İkinci tur (Duffy, 29 Ekim 2026, Y2b kontrolünden sonra; `planlama/kararlar-2026-10-29.md` 5–9, `lale-duzeltme`):

5. **Fren ≤ 1,8 m/s²** (yazılım freni ve acil stop yavaşlaması; belgelerde tek değer, eski "≤ 2" / "1,5 varsayımı" kalktı). Düz zemin
   sürüş ivmesi **≤ 0,5**, rampada / eğimde **≤ 0,1 m/s² + kollar ev pozunda** aynen. Rampada 1,8 frenle ev pozu payı 1,31 (< 1,5):
   öneri rampada yavaşlamayı da ≤ 0,1'de tutmak (Duffy teyidi açık). → F8, `motorlar.cpp` `HIZLANMA` (hızlanma / yavaşlama ayrı sınır).
6. **El yükü ~100 g** (açık konu, değişmedi). → F8.
7. **Mikrofon maliyete girdi:** XVF3800 ≈ 5.500 + yönlü mikrofon kolu ≈ 2.000 = **≈ 7.500 TL (tahmini)**; `maliyet.json` genel 109.001,35 TL. → M1 kapandı.
8. **Kafa 5 V tepe ≈ 4,1 A** (10,1" ekran + XVF3800 ~1 W varsayımıyla; XVF3800 akımı ölçülmeli). → M4, F10.
9. **Pi–ESP32 USB kablosu 2 m** (gereken ≈ 1,64 m; Pi kafada, gövde uzadı). Tablo 1'deki "1,25 m" eski.
10. **GPIO16 / 17 boş** (Nextion kalktı; pin planında GPIO2 = K2). → F6.
11. **Servo beslemesi ayrı regülatörlerde (hat ayrımı):** sağ kol = hat A, sol kol = hat B, kafa pan + tilt = hat C (üç XL4016; kafa
    servosu bir kol hattına girince hat 5 A'i aşıyordu). Yoğun / tepe: kol 4,87 / 7,24 A, kafa 1,5 / 5,0 A (tahmini). Yazılıma etkisi:
    akım ölçer ya da hat kesme (F9) hat başına düşünülürse eşleme bu; PCA9685 kanalları (sinyal) değişmedi. → F9.
12. **Akü gereksinimi 2 saat kullanım:** normal / tipik 5,9 sa; yoğun kullanımda hesaplanan 1,83 sa Duffy tarafından kabul edildi (29.10).
    Akü gerilim uyarısı (F7 / Y3) bu süreye göre ayarlanabilir.

## 3. Mikrofon değişikliği (26 Ekim, Efe) ve mekaniğe etkisi

Eski plan: **ReSpeaker Lite** (2 mikrofon, 2.587 TL, `maliyet.json`'da hâlâ bu). Yeni karar
(`raporlar/mikrofon-secimi.md`): **XVF3800 4 mikrofonlu USB dizi** (≈ 5.500 TL kargo/gümrükle, tahmini) +
karşılaştırma kolu **yönlü mikrofon + USB ses kartı + kürk kılıf** (≈ 2.000 TL, tahmini). Toplam ≈ 7.500 TL.

Tasarım tarafında açılan işler:

| # | Etki | Not |
|---|---|---|
| M1 | `maliyet.json` güncellenmedi | Fark ≈ +4.900 TL (tahmini); TÜBİTAK bütçe satırları da değişecek (raporda yazıyor) |
| M2 | **Hoparlör yolu** | Rapor: AEC için hoparlör dizinin çıkışından beslenmeli. Tasarımda kafada MAX98357A I2S amfi + 40 mm hoparlör var; şu an kod HDMI sesi kullanıyor. Amfi kalır mı, dizinin çıkışına mı geçilir: Efe + Duffy |
| M3 | Kafada yer ve rüzgâr koruması | Dizi kafanın içine, büyük durgun hava hacmine gömülmeli; kasalı kartın ölçüsü CAD'e girmeli; gerekirse Flex doğrusal sürüm |
| M4 | Kafa 5 V bütçesi | E4'te mikrofon 0,5 W varsayıldı; dizinin akımı belgelenmemiş, ölçülmeli. Pi USB portları toplam 0,6–1,6 A |
| M5 | Yönlü mikrofonun yeri | Karşılaştırma kolu robota takılacaksa yeri ve kablosu belirlenmeli |

## 4. Çalışma düzeni önerisi

- **Mekanik/elektrik gerçeği:** `lale-duzeltme` dalı (`tasarim/freecad/`, `planlama/adim3/elektrik.md`,
  `kod/ortak/eklem_sinirlari.json`). **Yazılım gerçeği:** `main` / `yazilim-baslangic` (`kod/`).
- Bir taraf öbürünü etkileyen karar alınca: `planlama/kararlar-YYYY-MM-DD.md`'ye satır + bu dosyanın tablosunda
  ilgili satırı güncelle.
- Sayılar (eklem sınırı, servo modeli, pin) iki yerde elle yazılmaz; F2'deki tek kaynak kararı bunun için.
- Fiziksel donanımda doğrulanmamış her değer "tahmini" / "kablajda doğrula" diye işaretli kalır (iki taraf da
  zaten böyle yazıyor).
