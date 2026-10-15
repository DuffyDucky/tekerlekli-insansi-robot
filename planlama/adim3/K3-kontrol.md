# K3: 3. adım bağımsız kontrol (taban güç, Pi kafada, elektrik)

Kontrol ajanı: Opus (bağımsız). HEAD `a158211`, değişiklikler commit'lenmemiş.
Kapsam: `tasarim/freecad/taban/`, `tasarim/freecad/kafa/`, `planlama/maliyet.json`, `planlama/adim3/`,
`arayuz.py` taban/kafa/elektrik bölümleri. Omuz/kabuk/dirsek ve arayuz OMUZ/KOL_KABLO bölümleri kapsam dışı (S1 ajanı).

Durum: **TAMAMLANDI** (15 Ekim 2026). Web erişimi bir ara kesildi, sonra datasheet doğrulamaları tamamlandı.

## İlerleme
- [x] 1. E0 dönüş hesabı (GEÇTİ, notlu)
- [x] 2. Elektrik E1–E4 (GEÇTİ, 1 tutarsızlık)
- [x] 3. CAD (GEÇTİ)
- [x] 4. Isı (kapalı makul, yarıklı iyimser)
- [x] 5. Maliyet (GEÇTİ)
- [x] 6. Belge/rapor tutarlılığı (KALDI: eski Pi metinleri, VBUS çelişkisi)

## 1. E0 dönüş hesabı — GEÇTİ (notlu)

Bağımsız betik: `K3_donus.py` (donus_hesap.py'yi import etmez; yerinde dönüşte sağ/sol simetriden vz = 0, iç döngü Fx(vx)=0,
dış döngü M(w)=0, ikisi de bisection) → `K3_donus_sonuc.json`. Girdiler: 21,7144 kg, AM z −13,8 (`taban-analiz.json` robot ev pozu =
tabansız 13.716,8 + kafa düzeltmesi 68,2 + taban 7.529,4 + kablo 400 g; toplam tutuyor), x 178, z 185, r 62,5, Crr 0,03.

| μ | Benim (kayma c 0,05) | Benim (rijit Coulomb) | Tasarımcı | Üst sınır (Wong) benim / tasarımcı | Omni benim c 0,05 / rijit | Tasarımcı omni |
|---|---|---|---|---|---|---|
| 0,4 | 12,07 (ön 9,2) | 12,27 | 12,06 | 17,48 / 17,49 | 2,70 / 3,58 | 2,69 |
| 0,5 | 14,90 (ön 11,3) | 15,07 | 14,89 | 21,58 / 21,58 | 2,58 / 3,15 | 2,58 |
| 0,6 | 17,73 (ön 13,4) | 17,86 | 17,71 | 25,68 / 25,68 | 2,93 / 2,72 | 2,93 |

- El sağlaması (eşit yük, merkezde dönme, F_boy = μN·sin α, tan α = 185/178): 10,8 / 13,25 / 15,7 kg·cm = ön ve arka ortalaması (10,6 / 13,1 / 15,6). Tutarlı.
- Dönme merkezi arka aksa 26 mm kayıyor (benim 26,0–26,4). Aks yükleri 98,6 / 114,5 N doğru. İvme payı 0,77 kg·cm (I_z 0,855) doğru.
- Sürekli 6,3 = 21 × 0,30: kaynak `01-donanim-maliyet.md` satır 116 ("%25–30"), durma 21 kg·cm Direnc.net sayfası (`05-fiyat-arastirmasi.md` satır 92). Oranlar ×1,91/×2,36/×2,81 ve durmanın %57/71/84'ü doğru.
- **Not (risk, 3. adımın hatası değil):** 21 kg·cm satıcı etiketi. `06-aku-secimi.md` satır 15'teki Aslong tablosu aynı motorun 1:90 (66 dev/dk) sürümü için durma **9 kg·cm** veriyor; 60 dev/dk (≈1:100) için bu ≈10 kg·cm demek. Gerçek değer buna yakınsa μ 0,4'te bile yerinde dönüş durma torkunu aşar. K1 ölçümü bu yüzden şart; omni önerisi bu senaryoda daha da güçlenir.
- **Omni duyarlılığı:** 2,6–2,9 kg·cm kayma ölçeği c = 0,05 ve omni yanal direnç 0,05 varsayımına bağlı; rijit Coulomb ile 2,7–3,6 (×0,43–0,57). Sonuç (sürekli değerin altında) değişmiyor, ama raporda "varsayıma duyarlı" denmeli.
- **Tek yerden güncelleme:** evet. `arayuz.TABAN['donus']` içindeki `mu_olculen`, `stall_kgcm_olculen`, `stall_A_olculen`; `taban_montaj.py` motor torku da `DH.motor_degerleri()`'nden okuyor (satır 388–392). Elle güncellenmesi gereken yalnız `elektrik.md` tabloları ve akım bütçesindeki "8,0 A yerinde dönüş" satırı.
  Küçük kusur: ölçülen μ senaryo değerlerinden birine eşitse (ör. 0,5) listeye iki kez girer, `etiket` "olculen" olur; sonuç doğru, tablo çift satır.

## 2. Elektrik E1–E4 — GEÇTİ (iki tutarsızlıkla)

| Kontrol | Ölçtüğüm / bulduğum | Sonuç |
|---|---|---|
| Servo A / B yoğun | A: 1,5+0,9+0,9+0,5+0,6 = 4,4 A; B: …+0,9 = 4,7 A; jest 2,8 / 2,9 | ✔ |
| "Gerçekçi tepe 7,7 A" | belgedeki servo başı değerlerden yeniden üretilemedi (hangi iki servonun kalktığına göre 7,0–8,3 A) | küçük; tahmini değer |
| 7,5 A hat sigortası | giriş 7,7 × 6 / 0,88 / 12,8 = 4,10 A; teorik durma 12,7 A'de giriş 6,8 A → sigorta atmaz, XL4016 kendi sınırında keser | ✔ |
| 16 AWG 0,6 m | 13,2 mΩ/m × 0,6 = 7,9 mΩ, 7,7 A'de 0,061 V | ✔ |
| 22 AWG uzatma | 2,6 m × 52,9 mΩ/m × 2,5 A = 0,34 V | ✔ |
| XL4016 sürekli ≤ 5 A | `05-fiyat-arastirmasi.md` satır 288 (Motorobit "sürekli 5 A") | ✔ |
| Sonar bölücü | 5 × 10/14,7 = 3,401 V ≤ VDD + 0,3 (3,6 V) | ✔ |
| Akü ADC 100k/18k | oran 0,1525: 14,6 V → 2,23 V, 10,0 V → 1,53 V; 11 dB önerilen 150–2450 mV içinde; 0,124 mA | ✔ |
| E3 açılış | GPIO12 → 220 Ω → gate, gate–GND 10 kΩ: boot'ta GPIO12 LOW (strap; yüksek olsa flaş 1,8 V'a düşerdi, bu da önleniyor), MOSFET kapalı, röle çekmez | ✔ |
| E3 mantar bırakılınca | bobin yolu = mantar NC **ve** MOSFET; MOSFET yalnız GPIO12 = 1 iken açık, yazılım PC817 #1 HIGH'da kilitliyor → kendiliğinden çekmez | ✔ (yazılım kuralına bağlı; belgede açık) |
| IRLZ44N 3,3 V kapı | VGS(th) 1,0–2,0 V; RDS(on) 25 mΩ @5 V, 35 mΩ @4 V (IRLZ44NS datasheet özeti, alldatasheet); bobin 0,15 A için 3,2 V kapı yeterli (3,3 V'ta RDS(on) belirtilmemiş, akım çok küçük) | ✔ |
| Flyback | 1N4007 bobine ters paralel (şemada var) | ✔ |
| PC817 modülü | Direnc.net: giriş 3,6–24 V, 43,59 TL (doğrulandı). Çıkış tarafı "3,6–30 V, 10 mA", jumper'la yüksek/düşük seçiliyor: ESP32 3,3 V tarafı nominalin altında; çıkışı açık kolektör + ESP32 pull-up bağlayıp montajda multimetreyle doğrulayın | küçük |
| Pololu D36V50F5 | pololu.com/product/4091: giriş 5,5–50 V, 5 V %4, **5,5 A 36 V girişte** (özellik listesi 3,5–8 A, girişe ve ısıya bağlı), ters gerilim 40 V, UV/OV/OC/kısa devre/ısı koruması, 25,4 × 25,4 × 9,5, 7,0 g, 39,95 USD. Kafa tepe 18,7 W → 3,74 A: yeter | ✔ (elektrik.md'deki "12 V'ta tipik 3,5–8 A" yanlış okuma: 3,5–8 A tüm giriş aralığı içindir) |
| Pi 5 PD'siz besleme | raspberrypi.com: `PSU_MAX_CURRENT` "PD pazarlığını atla, verilen akımı varsay; tipik 3000 ya da 5000" | ✔ |
| Pi gerilimi | çevirici 5,0 V ±%4 → en düşük 4,80 V; 10 cm 20 AWG USB-C ~0,02 V. Resmi besleme 5,1 V; Pi 5 düşük gerilim eşiği resmi kaynakta bulunamadı | düşük risk; testte `vcgencmd get_throttled` |
| Boyun 12 V 18 AWG | 2,5 m × 20,95 mΩ/m = 52 mΩ; 1,62 A tepede 0,085 V (%0,7) | ✔ |
| TVS | P6KE6.8A: VRWM 5,8, VBR 6,45–7,14, VC ≈ 10,5 V; P6KE18A: VRWM 15,3, VBR 17,1–18,9, VC ≈ 25,2 V (LiFePO4 14,6 V altında) | ✔ (not: P6KE6.8A sızıntısı 5,8 V'ta 1 mA'e kadar; 10,5 V kenetleme Pi için yüksek, SMBJ5.0A daha sıkı) |
| ESP32 tek kaynak + 1N5819 | anot Pi tarafında: Pi'ye geri besleme yok, CP2102 VBUS algısı sürüyor. Ama bu "tek kaynak" değil, diyotlu VEYA: çevre 5 V düşerse ESP32 Pi'den ~4,4 V alır (zararsız) | ✔ (ifade düzeltilmeli) |
| Eski bağlantılar | taban parça listesi: Pi, Pi burç/vidası, amfi, köpük bant, "Pi 5,1 V" XL çıktı; kablo yolu 12 (HDMI/FPC/USB mikrofon/hoparlör) kalktı; kafa kablo gösterimi "12 V + ESP32 USB + tilt" | ✔ CAD'de; ✘ metinde (bkz. 6) |

**Tutarsızlık E-1 (orta):** ESP32 USB kablosu iki farklı tarifle yazılmış.
"VBUS kesik / yalnız veri": `kafa_montaj.py` → `kafa-analiz.json` `pi.boyun_kablolari` ve kafa/rapor.html; `taban_parcalar.py` kablo yolu 12; `kafa_parcalar.py` kablo gösterimi notu.
"VBUS'ta seri 1N5819": `elektrik.md` E4, `maliyet.json` (diyot + USB kablosu notu), `taban_rapor.py` satır 373. CP2102'nin VBUS pini bağlantı algısıdır; VBUS kesilirse
kart USB'de görünmeyebilir. Doğrusu elektrik.md'deki diyot; diğer metinler buna çekilmeli.

**Not E-2 (düşük):** Pi seri portu açınca DevKit'in DTR/RTS otomatik reset devresi ESP32'yi resetler → GPIO12 LOW → röle bırakır (kollar düşer). Port DTR/RTS kapalı açılmalı
(yazılım planına satır). Ayrıca E3 ile röle her "devreye al"da yeniden çekecek: 4 × 2200 µF + XL/BTS giriş kondansatörleri Victron BMS'i kestirebilir (`06-aku-secimi.md` satır 61, 164); E9 ön şarj işi bu yüzden önem kazandı.

## 3. CAD — GEÇTİ

Ölçüm: `K3_cad_olcum.py` (dosyaların `%TEMP%\k3` kopyası; omni yalnız bellekte), sonuç `K3_cad_sonuc.json`. JSON farkı HEAD ile parça adı bazında.

**Taban (292 → 316 parça, 7.493,4 → 7.529,4 g):** çıkan 15 (Pi 58 g, 4 burç, 8 vida, amfi, köpük), giren 39 (arayüz kartı 24 g, dağıtım A/B 29'ar g, 12 M3 naylon burç, 12 M3×6 üst + 12 M3×8 alt); iki XL yalnız yeniden adlandı (yer aynı).
Kütle farkı elle: −68,7 + 105,0 = +36,3 g ✔. Değişen tek gövde parçası "Elektronik katı (ön)" (−0,28 g): DXF'te 4 Pi deliği (Ø2,9) çıktı, 12 yeni Ø3,4 delik girdi; konumlar parça listesiyle aynı ✔.
Bağlantı 119/119, iç çakışma 0, iskelet 0 / kabuk 0, bölge ihlali 0 (JSON). Bağımsız: 65 yeni/yeniden adlı parça × tüm taban parçaları ortak hacim **0**; dağıtım kartları en yakın M5×12 kat cıvatasına 4,25 mm. Kasıtsız fark yok.
Boşalan Pi yeri arayüz kartında (−90,5; 80) ✔. Kalıntı: `arayuz.py` satır 251–252 BOLGELER döngüsünde "Raspberry Pi 5 (elektronik kati)" ve "MAX98357A (elektronik kati)" bölgeleri duruyor (eski V3 yerleri; P raporu "kalkar" demişti). Zararsız ama yanıltıcı.

**Kafa (98 → 115, 1.363,1 → 1.431,3 g):** giren 17 (Pi 58, çevirici 7, amfi 2, 4 burç, 8 vida, 2 köpük) + 4 kablo gösterimi; arka kabuk −7,55 g (22 yarık ≈ 6,6 cm³ × 1,14 g/cm³ ✔), iskelet −0,13 g (4 × Ø2,9). Toplam +68,2 g ✔.

| Ölçü | Benim | Tasarımcı |
|---|---|---|
| Pi ↔ kafa iskeleti / arka kabuk | 6,60 / 7,50 mm, ortak hacim 0 | 6,6 / 7,5 ✔ |
| Pi gövdesi, tilt −25…40 × pan ±90, Pan/Gövde'ye en az | **31,6 mm** (−25°, eğme çatalı) | 31,6 ✔ |
| Pi alt vidası (M2,5×8 başı, tabla altı), aynı tarama | 19,8 mm (−25°, eğme çatalı) | raporda yok (bilgi) |
| Havalandırma | 22/22 yarık açık; yarık önlerinde 5 mm içinde parça yok | ✔ |
| microSD çekme yolu (−X, 50 mm) | yol üstünde parça yok; arka kabuk sökülünce erişilir | ✔ |
| Eğme payı | 9,4 / (2,617 + 2,021) = 2,03 (AM–eksen 54,8 mm, 30°'de yatay kol 28,2 mm, I 0,00757) | ✔ |
| Bağlantı / ev pozu | 44/44, tarama sonucu HEAD ile aynı | ✔ |

**Omni:** taban_parcalar bellekte TABAN_OMNI=1 ile kuruldu (8.209 g ✔), etekler kabuk dosyasının kopyasından: ön omni ↔ etek ön **10,55 mm** (en yakın nokta tekerin önü, z 248,9), arka 12,0 ✔.
Sorun değil: temas yok, omni koşullu ve varsayılan kapalı; 12 mm kabuk tasarım payı. Omni alınırsa kabuk açık işi (etek ön bant +1,5 mm) yeter.

## 4. Isı — kapalı tahmin makul, yarıklı tahmin iyimser

- Betikten yeniden: Q = (Pi + 2,45 + 0,5 + 0,3) / 0,9 → 7,2 / 11,4 / 14,5 W; kapalı 30 + Q × 1,3 = 39,3 / 44,8 / 48,9 °C ✔; yarıklı ΔT = Q / (1,16 · 1007 · V̇) → 34–42 °C ✔ (aritmetik doğru).
- R 1,3 K/W: yüzey 0,1926 m², iç ve dış film ~9 W/m²K seri + PETG 0,0125 m²K/W → 1,23 K/W. Makul (±%30).
- **Yarıklı senaryo iyimser:** (1) Active Cooler fanı sıcaklık kontrollü, SoC ~50 °C altında durur; (2) fan kabuk yarıklarına kanalla bağlı değil, havayı kafa içinde döndürür; (3) giriş (y 192–227) ile çıkış (y 198–246) arasında ~12 mm yükseklik farkı var, baca etkisi çok zayıf. Gerçek değer büyük olasılıkla 42–49 °C arasında.
  (4) Pi üst bölmede (tabla üstü): orada hava ortalamadan sıcak; servo alt bölmede (servo için iyi).
- Öneri: çıkış yarıklarını yan duvarın en üstüne (y ~240–265) ya da tavana almak; test şartı (SoC ≤ 75 °C, servo ≤ 50 °C) korunmalı. 25–30 mm egzoz fanı için yer ayırmak ucuz sigorta. Engel değil.

## 5. Maliyet — GEÇTİ

- `adim: "3"` 17 kalem = 13 yeni + 2 değişen (FPC, micro HDMI) + 2 koşullu (omni, fan). XL4016'da yalnız not değişti.
- Toplam (viewer-template `on()` kuralı, V3, yedek hariç): HEAD 69.793,60 → 72.560,88 = **+2.767,28 TL** ✔; yedek dahil 71.426,41 → 74.193,69; %15 payla 82.140 → 85.323.
- Koşullular `secenek: "kosullu"` → `on()` yalnız yazıcı seçeneğini aldığı için toplama girmiyor ✔ (4.487 + 60 = 4.547 TL).
- Kaynaklar: Pololu 39,95 USD × 48,878 = 1.952,68 ✔ (sayfa açıldı); Adafruit 5819 300 mm 22→15 pin 3,16 USD = 154,45 ✔ (stokta); PC817 43,59 ✔; OzRobotics 14075 45,90 USD, Ø127 × 29, 22 makara, 480 g, 30 kg ✔ (göbek tipi sayfada yok, adaptör doğru biçimde "tahmini");
  Direnc.net `/mosfet` kategori sayfasının görünen kısmında IRLZ44N yok (kalem zaten "tahmini"). Diğer 8 kalem URL'siz "tahmini": kurala uygun.

## 6. Belge / rapor tutarlılığı — KALDI (küçük)

- ✔ E0 tablosu (taban/rapor.html, elektrik.md, T günlüğü) betik çıktısıyla aynı; kafa ısı tablosu, eğme payı, yer ölçüleri kafa-analiz.json ile aynı.
- ✔ `carpisma-sonuc.json` eskime uyarısı iki raporun başında görünüyor (taban ve kafa bölümleri "kaynağı eskimiş" listesinde).
- ✘ taban/rapor.html (kaynak `taban_rapor.py`) hâlâ eski düzeni anlatıyor: satır 158 (görsel altyazısı "Elektronik katı (ön): Pi 5 + Active Cooler … MAX98357A"), 178 (elektronik katı tarifi), 220 (bağlantı tablosu "Pi 5, PCA9685, BNO055 ↔ ön kat"), 222 ("MAX98357A ↔ ön kat"), 349 (direk görseli "servo, 5 V ve Pi kabloları"). 503/518/521 tarihçe olarak kalabilir.
- ✘ VBUS çelişkisi (bölüm 2, E-1).
- Küçük: elektrik.md çıkış yarıkları "y 198–249", geometri 198–246; raporda E0 karar cümlesi ASCII ("KOTU: yerinde donus …"); donus_hesap'te ölçülen μ bir senaryo değerine eşitse çift satır.

## Sonuç

Commit'e **engel yok**: hesaplar, geometri, çakışma ve maliyet doğru. Commit'ten önce kısa metin düzeltmesi önerilir (yapılmazsa açık iş olarak yazılsın):
1. VBUS: `kafa_montaj.py` `pi.boyun_kablolari`, `kafa_parcalar.py` kablo notu, `taban_parcalar.py` kablo yolu 12 → "ESP32 USB (VBUS'ta seri 1N5819)"; bir sonraki kafa/taban koşusunda JSON ve raporlar düzelir.
2. `taban_rapor.py` 158/178/220/222/349 metinleri; `arayuz.py` 251–252 Pi ve MAX98357A bölgeleri.
3. elektrik.md: Pololu akım ifadesi, "tek kaynak" yerine "diyotlu VEYA", DTR/RTS reset notu, yarıklı ısı için "iyimser" uyarısı, çıkış yarığı y 246.

Risk (ölçüm işi): JGB37 durma torku 21 kg·cm satıcı etiketi (Direnc.net sayfası yalnız "Tork 21KG", birim ve durma/nominal ayrımı yok); Aslong 1:90 tablosu 9 kg·cm diyor. K1 ölçümü omni siparişinden önce şart.
