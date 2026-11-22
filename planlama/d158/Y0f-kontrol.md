# Y0f bağımsız kontrol (B ajanı)

22.11.2026. Dal `lale-duzeltme`, HEAD `bec3f03`; A'nın commit edilmemiş işi üstünde. Paket dosyaları değiştirilmedi (iki geçici
deney geri alındı, md5 aynı: § 4). B'nin betikleri ve ham çıktıları depo dışında geçici klasörde; sayılar burada.

## 0. Hüküm: **KOŞULLU GEÇER**

Model CAD ile aynı (kütle, AM, teker düzeni, eklem yönleri; hata bulunmadı). Fizik koşusu belirlenimci, A'nın sayıları yeniden
üretildi, el hesaplarıyla uyuşuyor. Commit'ten önce düzeltilmesi gerekenler belgede ve koşucuda (§ 7, K1–K5): bir yanlış hüküm
(dişli 0,2 N·m'de "durur"), karar için eksik bir neden (dönmeme firmware'in açık çevrim PWM tavanından), bir ölçüm ürünü sayının
hüküm gibi yazılması (bekçi "tepe 3,1–3,2", "0 N 60–100 ms") ve test düzeyindeki muafiyetin fizikte bir güvenlik gerilemesini
örtmesi (gösterildi).

## 1. Koşular

| Ne | Sonuç |
| --- | --- |
| 2B `py -3 kod\testler\kos.py` | 58 / 58, 9,5 s |
| Fizik `kos_fizik.py` × 2 (çıktı depo dışına) | ikisi de çıkış 0; fizik 6 / 6; Y0s 48 + 10 beklenen fark; sayı özeti `70a9a5a6e4b0dd5c` ikisinde ve A'nın `olcum.json`'unda aynı; 172 s |
| Sistem Python'u (mujoco yok) `kos_fizik.py` | "ATLANDI", çıkış 0 |
| Sistem Python'u `LALE_HEDEF=fizik kos.py` | 25 geçer, 33 atlandı, 0 kalan |
| Sistem Python'u `test_fizik.py` | 6 / 6 atlandı |

## 2. Model sadakati (B'nin kendi hesabı, A'nın tablosuna bakılmadan)

`lale.xml` MuJoCo'da derlendi, gövde kütleleri ve `subtree_com` okundu; beklenen değer `montaj-analiz.json` (25.876,13 g, AM CAD
(0,034; 526,183; −9,71)) + `taban-analiz.json` `kablo_payi` (400 g, CAD (0; 150; −60), "tahmini") el ile birleştirildi.

| | Kütle (g) | AM x / y / z (mm, robot çerçevesi) |
| --- | --- | --- |
| Model (MuJoCo) | 26.276,14 | −10,475 / +0,034 / 520,456 |
| Montaj + kablo payı (el) | 26.276,13 | −10,476 / +0,033 / 520,456 |
| Fark | +0,01 | 0,00 / 0,00 / 0,00 |

- Çerçeve dönüşümü (robot x = CAD Z, y = CAD X, z = CAD Y) döngüsel permütasyon: sağ elli, yansıma yok. CAD +X = robotun kendi solu
  (K65 ile aynı; `sag-sol-karari.md`).
- Aks yükleri el hesabı (tekerler x ±185 mm): ön 121,59 / arka 136,18 N = `taban-analiz.json` `aks` 121,6 / 136,2.
- **Teker düzeni:** `montaj-analiz.json` 4 döner teker eklemi (`Taban_Teker{On,Arka}{Sag,Sol}`, "JGB37 mili"), CAD (±216; 62,5; ±185) →
  iz 432, aks aralığı 370, yarıçap 62,5 mm; modelde aynı, silindir 125 × 58 (BOM "Arazi tekerlegi 125 x 58" × 4; "JGB37-520 12 V
  60 dev/dk enkoderli" × 4, `robot-bom.csv` satır 123 / 144). Sarhoş / omni teker BOM'da yok, `taban-analiz.json` `omni` false.
  Dört teker tahrikli, kızak yönlendirme: doğru.
- **Atalet:** 16 gövdenin özdeğerleri pozitif, üçgen eşitsizliği hepsinde tutuyor. Mertebe: gövde (14,38 kg, 1,07 m boy) Ixx 3,14
  kg·m² ≈ iskelet çubuğu (~0,7) + kabuk kabuğu (~1,4) + omuz / kafa paralel eksen (~0,6) ≈ 2,8; Izz 0,35 ≈ 0,52 m kare kabuk 7,2 kg
  (0,32) + merkez direk: tutarlı. Teker Iyy 3,49e-4 ≈ ½ m r² = 3,48e-4. Taban 7,96 kg Izz 0,21 (plaka üst sınırı ~0,30): makul.
- **Eklem yönleri** (+0,5 rad sürülünce elin yer değiştirmesi): `*_omuz` el öne-yukarı (+174 mm x), `sag_omuz_yan` el −y (dışa),
  `sol_omuz_yan` +y (dışa), `*_dirsek` ön kol öne. Eksenler `montaj-analiz.json` eksenlerinin dönüşümüyle birebir. `kafa_pan` +
  = sola (CCW); `kod/jestler/kanallar.yaml` "küçük = robotun sağına" ve ofset 90 ile tutarlı. Teker eklemleri +y, + = ileri.
- **Ç-f1:** model gövdeleri robotun kendi çerçevesinde, CAD "Sol" grupları `sag_*` (K65'e uygun). `protokol.json` `sag_omuz → r_s1`,
  `eklem_sinirlari.json` `r_s1` "taraf sag, ayna false" (CAD adı). Sınırlar ve `bagimli` kuralı iki yanda aynı: sayılara etkisi yok.
  Ad tutarsızlığı A'dan önce var; Efe / Ahmet'in K65 § 3 eşlemesiyle kapanmalı. A'nın hükmü doğru.

## 3. Bulgular: B'nin el hesabı, duyarlılık koşuları, sınıflama

Sınıflar: **S** fizik olarak sağlam (geometri / CAD); **T** TAHMİN parametreye bağlı; **Ü** model ya da ölçüm ürünü, güvenilmez.
Ortak sayılar: m = 26,276 kg, h = 520,5 mm, d_ön 195,5, d_arka 174,5, r 62,5 mm, teker başı statik yük N ≈ 64,4 N, eklem sürtünmesi
= dişli 0,05 + crr 0,03 × N × r 0,121 = 0,171 N·m, durma torku τd 2,059 N·m, w0 6,283 rad/s, k_V 13,1 / 12.

### 3.1 Statik devrilme: **S**

atan(d / h): ileri 20,59°, geri 18,54°, yana teker merkezi 22,54°, teker dış kenarı (216 + 29 mm) 25,21°. A: 20,7 / 18,6 / 25,3. Uyuşuyor.
Belge kusuru: `SIMULASYON.md` satır 161 "atan(239 / 520) = 24,7°" yanlış; dış kenar 245 mm → 25,2° (fizikle uyan budur). Gerçek
lastiğin yuvarlak omzu 22,5–25,2 arasında bir değer verir.

### 3.2 Frende devrilme ve bekçi duruşu: mekanizma **T**, A'nın sayıları **Ü**

El hesabı (bekçi: PWM 0 + EN HIGH, kısa devre freni τ = τd w / w0; v0 0,396 m/s → w / w0 = 1,009):
- Fren kuvveti 4 (2,076 + 0,171) / 0,0625 = 143,8 N; etkin kütle m + 4 J / r² (J = teker 3,5e-4 + yansıyan 0,005) = 31,8 kg →
  **ilk an istenen yavaşlama ≈ 4,5 m/s²**, zaman sabiti ≈ 95 ms.
- Devrilme eşiği g d_ön / h = 3,68 m/s². 4,5 > 3,68: arka aks ilk ~20–30 ms'de boşalır.
- Arka tekerler yükünü kaybedince yalnız ön tekerler frenler: 2 × 2,25 / 0,0625 = 72 N → ≈ 2,5 m/s² < 3,68. Devrilme **ilerleyemez**
  (kendini sınırlar); gövde dönmez. Kollar en kötü pozda (eşik 3,15) da 2,5 < 3,15.

B'nin koşuları (ileri, ev pozu; ölçüt: arka aks yükü, AM hızının farkı, teker zemin sürtünme kuvveti / m):

| Değişken | 10 ms pencere tepe | 2 ms pencere tepe | zemin kuvveti / m tepe | arka aks en az | 0 N süresi | arka teker kalkma | en büyük eğim |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ana (dt 1 ms, solref 0,004) | 3,24 | 7,65 | 9,30 | 0 N | 61 ms | 0,037 mm | 0,007° |
| dt 0,5 ms | 3,38 | 5,30 | 8,73 | 0 | 60 | 0,015 | 0,003 |
| solref 0,002 | 3,94 | 10,73 | 19,25 | 0 | 71 | 0,063 | 0,010 |
| solref 0,008 | 3,43 | 6,08 | 6,52 | 0 | 48 | 0,058 | 0,011 |
| solref 0,002 + dt 0,5 ms | 3,50 | 5,62 | 15,72 | 0 | 70 | 0,011 | 0,002 |
| yansıyan atalet 0 / 0,01 / 0,015 | 3,25 / 3,36 / 3,01 | | | 0 | 38 / 56 / 41 | | |
| durma 15 kg·cm | 2,92 | | | 0 | 27 | | |
| durma 9 kg·cm | 1,88 | 1,90 | 1,90 | 65 N | 0 | | |

Sonuç: "arka aks boşalır" bütün sayısal / temas değişkenlerinde ve durma torku ≥ 15 kg·cm'de var, 9 kg·cm'de yok: **T** (durma
torku; kısa devre freninin doğrusal modeli). "Gövde devrilmez" el hesabıyla da sağlam (kendini sınırlama). A'nın "tepe 3,1–3,2 m/s²"
sayısı pencere genişliğinin ürünü (2 ms'de 4,6–10,7); "0 N 60–100 ms" temas sertliği ve zaman adımıyla 27–71 ms arasında oynuyor;
kalkma 0,01–0,06 mm (temas batmasının altında): **Ü**. A'nın "el hesabıyla fark açıklanamadı" notunun açıklaması yukarıda: eşik
anlık talep (≈ 4,5) ile aşılıyor, ölçülen ortalama yavaşlama ön tekerle sınırlandığı için eşiğin altında kalıyor. Tasarım için doğru
cümle: "21 kg·cm motorla tam hızda bekçi duruşunda arka tekerler kısa süre yükünü kaybeder (sıçrar); devrilme olmaz".

`dur` 1,77 m/s² (firmware 1,8 rampası): **S** (firmware belirler). Acil stop boşta kayma: el 0,39² / (2 × 10,93 N / 31,4 kg) = 0,22 m
(A 0,218), dişli 0,2'de 0,12 m (A 0,10): **T** (dişli, crr, yansıyan atalet). Yansıyan atalet yalnız aşağı yönde (0) denenmiş;
küçük fırçalı DC motor veri sayfalarında rotor ataleti ~10 g·cm² (ör. Haydon Kerk 8322S003: 9,9 g·cm²; A'nın 6e-7'sinin
~1,7 katı; 520 boy için bulunamadı). 0,015 kg·m² ile el hesabı kayma ≈ 0,30 m.

### 3.3 Rampada `dur` sonrası kayma: mekanizma **S**, sayı **T**

Firmware 0.5.0 (`git show origin/main:kod/esp32/src/motorlar.cpp`): `motorlar_dur` yalnız hedefi sıfırlar, rampa 0'a inince
`teker_adim` `cikis = 0` → `teker_yaz(t, 0)`: iki PWM 0, EN HIGH (guc.cpp) = BTS7960 iki alt transistör = kısa devre freni. Model
(`dunya.py` satır 271–275, `fizik_esp32.py` satır 63–67) bunu yapıyor: τ = −τd w / w0; boşta değil. Kısa devre freni sıfır hızda
tork vermez: tutma yalnız sürtünmeden gelir. El hesabı v = (m g sin θ r / 4 − 0,171) / (τd / w0) × r:

| Eğim / değişken | el | A | B koşusu |
| --- | --- | --- | --- |
| 3° | 0,0076 m/s | son hız −0,0077 (kayma "0") | |
| 5° | 0,0344 | 0,034 | 0,0344 (dt 0,5 ms + solref 0,002: 0,0344) |
| 10° | 0,1008 | 0,10 | 0,1009 |
| 5°, dişli 0,2 N·m | 0,0058 | son hız −0,0058, kayma "0" | 0,0058, `dur_sonrasi_duruyor` False |
| 5°, dişli 0,25 N·m | 0 (tutmalı) | | 0,0041 (MuJoCo eklem sürtünmesi yumuşak kısıt: sınırda sızar) |

Sayısal değişkenlere duyarsız. Tutma eşiği 5°'de toplam eklem sürtünmesi ≥ 0,351 N·m (dişli ≥ 0,23 N·m); dişli kutusunun geri
sürülme sürtünmesi ölçülmedi: **T**. **Kusur:** "Dişli sürtünmesi 0,2 N·m ise 5°'de durur" (`SIMULASYON.md` satır 170) yanlış:
robot 5,8 mm/s kayıyor. Kaynağı ölçüt: `olcumler.py` satır 402 `dur_sonrasi_5s_geri_kayma_m = max(0, x_dur − x_son)`, `dur` anından
ölçüyor; firmware'in 0,1 m/s² rampasıyla robot önce yukarı süzülüyor, 5 s'de başlangıç noktasının altına inmeyince "0" yazıyor
(3°'de de aynı). "5 s'de 4,9 cm / 38 cm" de kayma değil, net yer değiştirme.

### 3.4 Yerinde dönüş: geometri **S**, eşik **T**, temas modeline duyarsız (eliptik koni içinde); nedeni firmware

El hesabı (izotrop Coulomb, saf dönme, a = 185, b = 216 mm): sürekli dönmede teker boyuna kayması ω a² / b, gereken teker kuvveti
F = µ N a / √(a² + b²) = 0,650 µ N; tork T = 0,650 µ N r + 0,171. Üst sınır (yanal tam µN, boyuna ayrı): F = µ N a / b.
Firmware w = 1 rad/s (giriş tavanı) → teker hedefi 0,213 m/s → **u = 0,546** (KP = 0, açık çevrim); durmada eldeki tork
τd u k_V = 1,228 N·m.

| | µ eşiği (Coulomb) | µ eşiği (üst sınır) | fizik |
| --- | --- | --- | --- |
| 21 kg·cm, u 0,546 (firmware) | 0,40 | 0,31 | µ 0,4: 0,049; 0,45: 0,003 rad/s (A ile aynı) |
| 21 kg·cm, **u 1 (tam PWM)** | **0,79** | 0,60 | **µ 0,4: 0,17; 0,5: 0,13; 0,8: 0,13 rad/s (döner)** |
| 9 kg·cm, u 0,546 | 0,14 | 0,10 | µ 0,2 / 0,3: dönmez |
| 9 kg·cm, u 1 | 0,30 | 0,23 | µ 0,3: 0,10 rad/s |

Temas varyasyonları (u 0,546; µ 0,4 / 0,45 / 0,5, rad/s): condim 4 (burulma sürtünmesi) 0,048 / 0,003 / 0,001; küre teker (tek temas
noktası) 0,064 / 0,003 / 0,003; dar silindir 20 mm 0,056 / 0,003 / 0,001; impratio 10 0,048 / 0,002 / 0,000; dt 0,5 ms ve solref
0,002 µ 0,5'te 0,001. Yalnız **piramit koni** sonucu değiştiriyor (0,087 / 0,067 / 0,051: anizotrop sürtünme, fiziksel değil).
Eşik silindir genişliğinden, temas sayısından, burulma sürtünmesinden bağımsız; el hesabıyla 0,40'ta tutuyor: fizik, temas ürünü
değil. Bağlı olduğu TAHMİN'ler µ ve durma torku.

**Karar için eksik:** dönmemenin doğrudan nedeni motor değil firmware'in açık çevrim eşlemesi: `w` girişi 1 rad/s'ye kırpılıyor ve
PWM hıza orantılı, yerinde dönüşte PWM %55'te kalıyor. Aynı 21 kg·cm motor tam PWM'de µ 0,8'e dek dönüyor (el 0,79). `taban-analiz`
el hesabı da (µ 0,5: en yüklü teker 16,2 kg·cm, durmanın %77'si) motorun yettiğini söylüyor; "aynı eşik" yalnız u 0,55 ile. Bu,
K1 (ön omni) ile firmware çözümü (dönüşte w tavanı / ileri besleme / PID) arasında seçimi değiştirir; belgede yazmalı. 9 kg·cm
gerçekse tam PWM'de bile µ > 0,3'te dönmez: önce motor torku ölçülmeli (Ç-f3, elektrik.md satır 159 uyarısı).

Motor torku kaynağı doğrulandı: 21 kg·cm `raporlar/kaynaklar/05-fiyat-arastirmasi.md` satır 92 (Direnc.net "21 kg", birimsiz);
`planlama/adim3/elektrik.md` satır 157–160 ("durma mı nominal mi belli değil"); 9 kg·cm `06-aku-secimi.md` satır 15 (Aslong 1:90
durma 9 kg·cm / 1,2 A). PWM → tork eşlemesi: firmware `cikis = rampa_hiz / 0,39` (motorlar.cpp `teker_adim`), BTS7960'ta bir giriş
PWM öbürü 0 (yavaş sönüm) → ortalama gerilim u V; model τ = τd (u k_V − w / w0): doğru. `k_V` (13,1 / 12) ve 60 dev/dk'nın yüksüz
sayılması TAHMİN.

Yay dönüşleri (v 1 / w 1): iki yan torku farkı 2,25 × (1 − 0,17) = 1,87 N·m → eşdeğer yerinde tork 0,93 → µ eşiği ≈ 0,36; µ 0,5 / 0,8'de
düz gitmesi tutarlı (**T**).

### 3.5 Kalkış torku: gereken tork **S**/**T**, yüzdeler **T**

El: T = m (g sin θ + a_fw + g cos θ crr) r / 4 + dişli: düz 0,376, 5° kip 0,563, 10° kip 0,909 N·m; A fizik tepe 0,46 / 0,58 / 0,93
(fark yansıyan atalet geçici rejimi J a / r ≈ 0,04). Yüzdeler (%74 / %94 / %150) "sürekli tork = durmanın %30'u" (TAHMİN) üstünden;
9 kg·cm'de aynı torklar sürekli değerin ~2,3 katı. 15° rampada tırmanma hızı el 0,393 (1,09 − 1,25 / 2,059) = 0,19 m/s = A. 20° geri
devrilme geometriden (18,5°): **S**.

### 3.6 Eşik: **T** (sayısal değişkenlere duyarsız)

B: 30 mm (v 1) geçer, 40 mm etek takılır, 0,2 m/s'de 5 geçer 10 geçmez; dt 0,5 ms + solref 0,002 ile aynı. 0,2 m/s el hesabı (ön teker
kenara dayanınca gereken itme 2 N_ön tan φ; eldeki 4 τd u k_V / r − yuvarlanma): 10 mm 79 N gerek / 63 N var (geçmez), 5 mm 52 / 63
(geçer): uyuşuyor. 30 mm tam hızda yarı-statik hesap yetmiyor (kinetik enerji katkısı); sınır durma torkuna bağlı. 40 mm etek (35 mm
alt kenar): **S**. "0,2 m/s'de yalnız 5 mm" bulgusu da açık çevrimin ürünü (düşük hızda düşük PWM = düşük tork); PID'li firmware'de değişir.

### 3.7 Kol: **S** (devrilme payı), çarpışma taraması bakılmadı

Kol pozlarında a_dev = g d / h CAD AM'sinden; en kötü 3,15 / 3,46 m/s², firmware freninin 1,75–1,92 katı: aritmetik doğrulandı.
`carpisma_denetim.py` (zarf temasları, 0 / 2.760) yeniden koşulmadı, yalnız A'nın sayısı okundu.

## 4. `BEKLENEN_FARK` ve `duzenek.py`

On muafiyetin kalma iletileri okundu (`LALE_HEDEF=fizik`):

| Test | Gerçekte kalan doğrulama | Fiziksel mi |
| --- | --- | --- |
| acil stop × 2, kablo, bekçi × 3, bozuk satır (7) | enkoder hâlâ sayıyor / hakem v 0,22–0,24 m/s / reset sonrası odo (96, 96) | Evet: kısa devre freni ~95 ms zaman sabitli, boşta 0,35 m/s² |
| `test_dur_fren_siniriyla_durur` | fren yolu 0,04061 m > sınır 0,0405 m (0,1 mm) | Evet ama gerekçe metni ("anlık 0 beklentisi") yanlış ileti |
| `test_cok_buyuk_v_teker_azamisine_kirpilir` | 0,3961 ≠ 0,39 | Evet (k_V, açık çevrim) |
| `test_ivme_siniri_duz_zemin` | 0,2971 ≠ 0,3 | Evet |
| `test_cok_buyuk_w_kirpilir_donus_orani_korunur` | yan oranı 0,996 ≠ 0,170 | Evet (§ 3.4 yay); gerekçe metni "yerinde" diyor, test yay dönüşü |

Gizlenmiş fizik hatası bulunmadı. **Ama muafiyet test düzeyinde:** ilk kalan doğrulamadan sonraki bütün doğrulamalar (acil stop
kilidi, `birak` kilidi çözmez, mantar basılıyken `arm` reddi, reset sonrası 3 s kendiliğinden devreye girmeme, sessizlik kilidi)
fizikte hiç koşmuyor. Deney (geri alındı): `cekirdek.py` `_bekci_kontrol` içindeki `_motor_ani_dur()` `pass` yapıldı. 2B: 5 test
kalır (bekçi × 2, bozuk satır, kablo, TCP soket). Fizik koşucusu: bunların 4'ü zaten "beklenen fark", yalnız `test_soket_kapaninca_durur` "YENİ
KALAN" yakaladı; o test olmasa gerileme fizikte görünmezdi. Ayrıca `kos_fizik.py` satır 84–89 beklenmeyen **her** kalanı bir kez
yeniden koşup geçerse "KARARSIZ" diye yutuyor (yalnız görünüm testi için yazılmış). Firmware modeli 2B'de aynı testlerle sınandığı
için bugünkü risk düşük; fizik kancaları (`_dilim`, `_acilis`) sıfırlamaya dokunduğu halde reset testi fizikte yarıda kalıyor.

`duzenek.py`: yalnız `hedef == "fizik"` dalı eklendi, `bellek` / `tcp` yolu aynı. Gösterim yukarıda: bekçi bozulunca 2B 5 test
kalıyor. `cekirdek.py` md5 deney öncesi ve sonrası `BF8B866155E18149DCC9EA987FD50329` (iki deney de).

`fizik_esp32.py` satır 159–161: hakem hızları |v| < 1e-4 m/s'de 0'a kırpılıyor. 2B testlerin `== 0.0` beklentisini fizikte geçirmek
için arka uçta konmuş tolerans; 0,1 mm/s altı sürünmeyi hakemden gizler. Küçük, belgelenmeli.

## 5. 3B pencere

`kod\simulasyon3b.bat` temiz bir PowerShell'den `Start-Process` ile iki kez başlatıldı; tuşlar gerçek tarama kodlu `keybd_event` ile.
- 68 s (sanal = duvar 68,4 s, en uzun döngü 146 ms) boyunca her denetimde `Responding = True`, `IsHungAppWindow` false; 10 kez
  taşındı / boyutlandırıldı, her seferinde yanıt verdi.
- Ekran görüntülerine bakıldı: oda, kolon, yarı saydam duvarlar, robot CAD ağıyla; kol pozu "one-yukari"da iki kol öne-yukarı.
  Katman sol altta 5 satır ASCII, okunaklı ("birakik [oda_rampa]", "v 0.00 / 0.00 m/s", "teker yuku N 61 68 61 68"). Görüntülerde
  yalnız MuJoCo penceresi (başlık "MuJoCo : lale"); yol, ad, sekme yok. Görüntüler depoya girmedi.
- Çalışanlar (stdout günlüğü): Home → `arm ok`, Yukarı × 3 → v 0,30, Sol → w 0,25, Delete → "ACIL STOP mantari BASILDI" / bırakıldı,
  yeniden Home → `arm ok`, Page Up × 2 → kol "one", "one-yukari" (6 servo ok), F9 → `rampa ok`, F11 → başlangıca kondu, F10 → kafa
  servosu ok (ikinci koşu), **F12 → sahne `rampa_parkuru` açıldı, ikinci F12 → `oda_rampa`** (ikinci koşu; pencere kapanıp yeniden açılır).
- İlk koşuda F10 "tus -1: atanmamis", F12 hiç gelmedi; ikinci koşuda ikisi çalıştı, bu kez ilk Home / Yukarı ulaşmadı. Odak / sentetik
  olay kaynaklı görünüyor; gerçek klavyeyle bir kez denenmeli. Rampa sahnesinde sürüş B tarafından denenmedi.
- Tuş atamaları `SIMULASYON.md` ile `gorunum3b.py` satır 8–14 ve 107–153 aynı.
- Pencere WM_CLOSE ile kapatılınca yeni python süreci 0; bat'ın cmd'si çıktı.

## 6. Kararsız test `test_yalniz_ayni_koken`

40 tek başına koşu (20 sistem Python 2B, 20 sanal ortam `LALE_HEDEF=fizik`): 0 kalan. 12 tam koşu (6 bellek, 6 fizik) üç paralel
ölçüm süreciyle yük altında: 0 kalan. B'nin dört tam fizik koşusunda da 0. Toplam 0 / 56; yeniden üretilemedi. A'nın kalan koşusunun
çıktısı saklanmamış, neden belirlenemedi. Test `127.0.0.1`'e doğrudan bağlanıyor (port 0, çakışma olası değil), 5 s zaman aşımı ve
`time.sleep(0.3)` sonrası hakem okuması var: en olası neden yük altında HTTP zaman aşımı. Fizikten bağımsız.

## 7. Kusurlar (önem sırasıyla)

| # | Önem | Yer | Kusur |
| --- | --- | --- | --- |
| K1 | Orta, commit öncesi | `kod/SIMULASYON.md` 175–178 | Dönmeme nedeni firmware açık çevrim PWM tavanı (u 0,55); tam PWM'de 21 kg·cm µ 0,8'e dek döner. Yazılmalı (K1 omni kararını etkiler) |
| K2 | Orta, commit öncesi | `kod/SIMULASYON.md` 170; `olcumler.py` 402 | "dişli 0,2 N·m ise 5°'de durur" yanlış (5,8 mm/s kayıyor); kayma ölçütü yukarı süzülmeyi sayıyor, 3°'de de "0" |
| K3 | Orta, commit öncesi | `kod/SIMULASYON.md` 164–165; `Y0f-gunluk.md` § 5 | Bekçi "tepe 3,1–3,2" ve "0 N 60–100 ms" pencere / temas ürünü; doğru hüküm "arka aks boşalır, devrilme kendini sınırlar" (§ 3.2) |
| K4 | Orta | `kod/fizik/kos_fizik.py` 35–56, 84–89 | Test düzeyinde muafiyet sonraki güvenlik doğrulamalarını koşturmuyor (bekçi gerilemesi fizikte örtüldü, gösterildi); "KARARSIZ" yeniden deneme her teste açık. Öneri: fizik için toleranslı doğrulama ya da doğrulama düzeyinde muafiyet; yeniden denemeyi yalnız görünüm testine sınırla |
| K5 | Düşük | `kos_fizik.py` 44–45, 52–53 | İki gerekçe metni gerçek kalan doğrulamayla uyuşmuyor (`test_dur_fren...`: fren yolu 0,1 mm uzun; `test_cok_buyuk_w...`: yay, "yerinde" değil) |
| K6 | Düşük | `kod/SIMULASYON.md` 161 | atan(239 / 520) = 24,7° → atan(245 / 520,5) = 25,2° |
| K7 | Düşük | `fizik_parametreleri.json` 16; `olcumler.py` 47 | Yansıyan atalet yalnız 0'a doğru denenmiş; benzer motor veri sayfalarında rotor ataleti ~1,7 kat; 0,01–0,015 ile acil stop kayması ~0,3 m |
| K8 | Düşük | `fizik_esp32.py` 159–161 | Hakem 1e-4 m/s kırpması testleri geçirmek için arka uçta; belgede yok |
| K9 | Bilgi | `Y0f-olcum/olcum.md` | 6.004 satır, `olcum.json`'un JSON dökümü (125 KB); okunur özet değil. Gerekli değil |
| K10 | Bilgi | belgeler | "Karar isteyenler" listesi yok; yalnız Ç-f1 "Efe / Ahmet bakmalı". Karar isteyenler: motor torku ölçümü (Ç-f3; dönüş, bekçi, eşik, rampa hepsi buna bağlı), zemin µ, dişli geri sürülme sürtünmesi (rampada tutma), dönüş için firmware mi omni mi (K1), Ç-f1 ad eşlemesi |

## 8. Özel veri ve commit listesi

- `pre-push` kalıpları (anahtar, parola ataması, e-posta, IBAN / telefon, yerel yol, takma ad, ekip soyadları) 44 yeni / değişen
  dosyada (STL'ler `-a` ile dahil): 0 bulgu. Yasak yol ve ofis belgesi yok; pakette görüntü dosyası yok. `LOCALAPPDATA` yalnız ortam
  değişkeni adı olarak geçiyor.
- 21 eski kirli dosya: `kir-bas.md5` ile 21 / 21 aynı. `tasarim/` altında 22.11 20:50'den sonra değişen dosya yok, izlenmeyen yeni
  dosya yok: A CAD klasörlerine yazmamış.
- Boyut: paket ≈ 4,07 MB (görsel ağ 2,9 MB, en büyük `govde.stl` 1,27 MB; `cad_govdeler.json` 0,84 MB). Ağ ve `cad_govdeler.json`
  üretilebilir ama ham CAD önbelleği ve FreeCAD depo dışında; `lale.xml` ağ dosyaları olmadan derlenmez: girmeli.
  `__pycache__` `.gitignore` 1. satırla dışarıda.

**Girecek:** `kod/fizik/` (`cad_cikar.py`, `carpisma_denetim.py`, `dunya.py`, `fizik_esp32.py`, `gorunum3b.py`, `kos_fizik.py`,
`model_uret.py`, `olcumler.py`, `olcum_rapor.py`, `fizik_parametreleri.json`, `gereksinimler.txt`, `model/lale.xml`,
`model/cad_govdeler.json`, `model/kutle_karsilastirma.json`, `model/kutle_karsilastirma.md`, `model/ag/*.stl` (16),
`sahneler/oda_rampa.json`, `sahneler/rampa_parkuru.json`, `testler/test_fizik.py`), `kod/simulasyon3b.bat`, `kod/SIMULASYON.md`,
`kod/testler/duzenek.py`, `planlama/d158/Y0f-gunluk.md`, `planlama/d158/Y0f-kontrol.md`, `planlama/d158/Y0f-olcum/` (`olcum.json`,
`kosu-1..3.log`, `git-status-bas.txt`, `kir-bas.md5`; `olcum.md` isteğe bağlı, K9).

**Girmeyecek:** `__pycache__/`; 21 eski dosya (`tasarim/freecad/kabuk/gorsel/*.png` × 13, `tasarim/freecad/montaj/yerlesim-kontrol.json`,
kökteki boş `geometri*_*.py`, `gez.js`, `uc.js`, `planlama/d158/P108d-kontrol-olcum/b2-tarama.nabiz`, `planlama/d158/P108d-olcum/ara1.json`).

## 9. Bakılmayanlar

`cad_cikar.py`'nin FreeCAD'den yeniden çıkarımı (FreeCAD koşulmadı; `cad_govdeler.json` grup ataletleri parça düzeyinde
doğrulanmadı, yalnız mertebe); `carpisma_denetim.py` ve kol zarf taraması; sonar ışın modeli ve "sonar açıkken 15° rampa / 40 mm eşik
engel" bulgusu (yalnız A'nın sayısı okundu); dinamik kol salınımı; rampa sahnesinde pencereden sürüş; gerçek klavyeyle F12.


## 10. Yeniden kontrol (A'nın düzeltme turu, `Y0f-gunluk.md` § 10)

Kapsam dar: yalnız düzeltmeler. Paket dosyalarına kalıcı yazı yok; bozma denemeleri geri alındı (md5 aşağıda). Fizik
koşusunun çıktısı geçici klasöre verildi; `Y0f-olcum/` içindeki dosyaların tarihleri koşudan önceki gibi.

**Hüküm: GEÇER** (commit engeli yok). Aşağıdaki Y1 belge cümlesinin commit'ten önce düzeltilmesi önerilir, engel değil.

### 10.1 Koşular

- 2B (sistem Python, mujoco yok): 58 / 58, 9,2 s. `LALE_HAKEM=yok` ile 58 / 58, 9,8 s.
- Fizik bir tam koşu: çıkış 0, fizik 6 / 6, Y0s fizikte 58 / 58, sayı özeti **`f3507f3911bd53da`** (A'nınkiyle aynı), 177 s.
  `kosu-4.log` ve `kosu-5.log` içerikçe aynı sonuç (özet aynı; dosyalar yalnız süre satırlarında farklı).

### 10.2 K4: üç bozma deneyi (cekirdek.py md5 önce / sonra `BF8B866155E18149DCC9EA987FD50329`, her seferinde eşit)

| Bozma | md5 bozukken | 2B | Fizik |
| --- | --- | --- | --- |
| 1. `_bekci_kontrol`: `_motor_ani_dur()` -> `pass` | `FAE6F29F…` | çıkış 1, 5 kalan (bekçi × 2, bozuk satır, kablo, TCP soket) | çıkış 1, aynı 5 "YENİ KALAN"; hata "[0,3, 0,3] != [0,0, 0,0]" (sürücü hedefi) |
| 2a. `_arizaya_gec`: `_cikislari_kapat()` yerine yalnız röleler düşer | `122DC358…` | 58 / 58 | 58 / 58 (yakalanmadı) |
| 2b. 2a + `_motor_guncelle` savunma satırı (`guc != devrede` ise `_motor_ani_dur`) -> `pass` | `181C4202…` | çıkış 1, `test_acil_stop_kilitler…` | çıkış 1, aynı test (satır 158, `durus="bosta"` sürücü denetimi) |
| 3. Arıza kilidi yok: `guc == ariza` ve mantar bırakık ise kendiliğinden devrede (EN, K1) | `48108ACA…` | çıkış 1, 4 kalan (acil stop kilidi, kablo, bozuk satır, i2c) | çıkış 1, aynı 4 "YENİ KALAN" |

2a'nın yakalanmaması test deliği değil: savunma satırı bir sonraki adımda hedefi sıfırlıyor (fiziksel davranış doğru), mantar
röle bobinini donanımca kesiyor. Savunma satırı da kalkınca (2b) iki dünya da yakalıyor. Fizik koşusu artık 2B'nin
yakaladığı her bozmayı yakalıyor; K4 kapandı.

**Paylar.** Firmware gerilemesi paya değil, `surucu_kesik_dogrula`'ya takılıyor (hedef 0, fren = EN HIGH + PWM 0, boşta =
EN LOW; bozma 1 ve 2b buradan düştü); bu denetim paydan bağımsız ve kesin. Pay yalnız fiziksel duruşu sınırlıyor: fren
400 ms / 25 mm (ölçülen 270 ms / 15,6 mm, x 1,5), boşta 1,3 s / 0,20 m (870 ms / 0,128 m). Fren boşta kaymaya dönse
(0,128 m, 870 ms) fren payını aşar, yani "fren yerine boşta" gerilemesi pay tarafından da yakalanır; tersi (boşta yerine
fren) payı geçer ama `suruluyor` denetimi yakalar. x 1,5 yeterince dar. Tek gevşek yer `dur_fren_yolu` +5 mm (ölçülen
fazlalık 0,1 mm, 50 kat); üst sınır 37,5 mm'ye göre %13, engel değil.

### 10.3 `duzenek.py` / `test_guvenlik.py` farkı

Satır satır okundu. 2B ve gerçek kart yolu değişmedi: her fizik dalı `self.ortam.fizik` ile korunuyor, `Ortam.fizik` varsayılanı
False, gerçek kart `Ortam`'ı bu alanı hiç True yapmıyor; `hakem_durdu` 2B'de eski `h["v"] == 0` denetimini aynen yapıyor,
`hiz_esit` 2B'de 6 basamak. `surucu` yalnız fizik hakeminde okunuyor ve `hakem_var` False iken atlanıyor; protokol tarafı
(enkoder sabitliği, yol sınırları, olaylar, hata cevapları) hakemsiz de koşuyor (`LALE_HAKEM=yok` 58 / 58). Fizikte zayıflayan
yalnız: enkoder sabitliği pay süresinden sonra aranıyor (fiziksel karşılık), `w_kirpma` testinde enkoder oranı yerine
sürücü hedef / PWM oranı (firmware doğrulaması olarak doğru; yayın çizilmediği belgede bulgu olarak duruyor).

### 10.4 Dönüş farkı (B 0,17 / A 0,30, µ 0,4, 21 kg·cm, tam PWM): çözüldü

B'nin betiği firmware'i atlayıp dünyaya doğrudan u = -1 / +1 verdi, kollar servo hedefi verilmeden (ctrl 0) bırakıldı; 3 s
koşup son 1 s ortalandı. Aynı betikle 1 s'lik ortalamalar 0,30 / 0,28 / **0,17** / 0,17 / 0,17: ilk 2 s A ile aynı, sonra
kollar ev pozu dışında oturunca düşüyor. Kollar ev pozuna konunca 0,31 / 0,27 / 0,30 / 0,32 / 0,26; A'nın `donus_kos(tam_pwm)`
yolu bu oturumda 0,32. Gerçek firmware'in tam PWM'de vereceğine karşılık gelen A'nınki (kollar ev pozunda, devreye alma
yolu firmware'den). µ 0,4 eşiğe yakın olduğu için yük dağılımına duyarlı; µ 0,5 / 0,8'de iki yol 0,11–0,16 ile uyuşuyor.
Belgedeki "fark açıklanamadı" cümlesi bu açıklamayla değiştirilebilir (küçük).

**Y1 (belge, öneri).** "Karar isteyenler" satırı "Firmware yolu 21 kg·cm gerçekse yeter (tam PWM µ 0,8'e dek döner)" diyor.
µ 0,8'de 0,12 rad/s ≈ 7°/s: 90° için ≈ 13 s, tam tur ≈ 52 s, motorlar durmaya yakın (sürekli akım / ısınma modellenmedi).
Bu pratikte "döner" değil "zorla, çok yavaş döner"; okuyucu firmware düzeltmesinin yeterli olduğunu anlayabilir. Gövde
metni ("dönüş yavaş, motorlar durmaya yakın") doğru; tablo satırı onunla aynı dili kullanmalı. Dürüst hüküm: **21 kg·cm
motorla tam PWM'de µ 0,8 zeminde robot dakikada bir turdan az döner; firmware düzeltmesi tek başına kullanışlı yerinde
dönüş vermez, mekanik seçenek ya da ölçülmüş µ / tork olmadan karar verilemez.**

### 10.5 `SIMULASYON.md` fizik bölümü

Tamamı okundu. K1 (dönüş: geometri sağlam, eşik TAHMİN, neden firmware u 0,55), K2 (rampada tutmaz; tablo B'nin ve el hesabının
sayılarıyla aynı; "0,2 N·m'de 5°'de durur" kalktı), K3 ((a) / (b) / (c), 10 ms / 2 ms pencereleri, 9 kg·cm'de 65 N) B'nin
sınıflamasıyla uyuşuyor; "Karar isteyenler" etiketleri doğru. El hesabı yeniden: 3° / dişli 0,2'de gereken tork 0,211 < sürtünme
0,321 N·m, tutmalı; 5° / 0,2 -> 5,7 mm/s, 10° / 0,2 -> 72 mm/s (tablo doğru). 3°'teki 2,5 mm/s için "eklem sürtünmesinin
yumuşak kısıtının sızması, model ürünü" doğru (B 5° / 0,25 N·m'de el hesabı 0 iken 4,1 mm/s gördü; aynı olgu). Kesin dille
kalan küçük TAHMİN'ler: "15°'ye dek çıkar" (devrilme geometrik, çıkış durma torkuna bağlı) ve kalkış torku yüzdeleri etiketsiz;
belgenin "Doğruluk sınırı" paragrafı bunları genel olarak kapsıyor, engel değil.

### 10.6 Özel veri ve commit listesi

Pre-push kalıpları (anahtarlar, e-posta, IBAN, yerel yol, takma ad, ekip adları) değişen / yeni 50 dosyada (`kod/` ve Y0f
planlama dosyaları, yeni `k4-bozma.log`, `kosu-4/5.log` dahil): **0 isabet** (`k4-bozma.log` yolları `<depo>/` ile maskelenmiş).
21 eski dosya md5 21 / 21 değişmemiş. `kod/` altında izlenmeyen 35 dosya, `__pycache__` / `.pyc` yok (yok sayılıyor).

**Girecek:** § 8 listesi + `kod/testler/test_guvenlik.py` + `Y0f-olcum/k4-bozma.log`, `kosu-4.log`, `kosu-5.log`.
`kosu-1..3.log` eski muafiyet listesini ve eski özeti (`70a9a5a6e4b0dd5c`) taşıyor; girerse tarih olarak, girmezse kayıp yok
(öneri: dışarıda bırak ya da günlükte "düzeltme öncesi" diye an). **Girmeyecek:** § 8'deki gibi (21 eski dosya, `__pycache__/`).

### 10.7 Bakılmayanlar

`fren.bekci_duyarlilik` ve `fren.acil_stop_araligi` yeni ölçüm kodu satır satır okunmadı (sayıları önceki kontrolün tablosuyla
uyuştuğu için); pencere yeniden açılmadı; `olcum.md` (K9) bakılmadı; pay payının fiziksel bir gerileme (ör. fren torku yarıya)
karşısında denenmesi yapılmadı, yalnız sayılarla akıl yürütüldü.


## 11. Ek kontrol: kumanda, hareketli dönüş, varyantlar (commit edilmemiş ek, `Y0f-gunluk.md` § 12–13)

Depo `5d5d3e4` üstüne çalışma ağacındaki ek. Paket dosyalarına kalıcı yazı yok; deneyler geçici klasörde, fizik koşusu
geçici klasöre yazdı (`olcum.json` / `olcum.md` için `git diff` boş).

**Hüküm: KOŞULLU GEÇER.** Commit'i engelleyen kod ya da veri sorunu yok. Koşul: K75'e gidecek iki belge cümlesi (11.4'teki
E1, E2) commit'ten önce düzeltilmeli; öbürleri öneri.

### 11.1 Varsayılanın korunması

- 2B 58 / 58 (9,0 s). Fizik tam koşu çıkış 0, fizik 6 / 6, Y0s fizikte 58 / 58, sayı özeti **`f3507f3911bd53da`** (değişmedi).
- `dunya.py`, `fizik_esp32.py`, `olcumler.py` farkı satır satır okundu: her yeni dal `varyant` doluysa çalışıyor; `varyantlar.al`
  V0 / None için None döner; V0'da makara listesi boş, `tahriksiz` boş, PI yok, enkoder tekeri aynı. `olcumler.py`'de yalnız
  `Deney`'e `varyant` geçişi. `olcum.json` commit'teki hâliyle aynı. `donus-hareket.json` md5 `c8caa97b…`, `donus-varyantlar.json`
  `03d05734…` (A'nın yazdığıyla aynı).

### 11.2 Hareket hâlinde dönüş (B bulgusu)

**Firmware karışımı.** `origin/main` `motorlar.cpp` `motorlar_hedef` ve `teker_adim` okundu; model aynı (v, w ±1 kırpma, iz
0,426, büyük teker 0,39'u aşarsa ikisi birlikte ölçek, u = rampa_hiz / 0,39, KP = KI = 0, hedef 0'da PWM 0).
v 0,25 + w 1: sol 0,25 − 0,213 = 0,037, sağ 0,463 -> ölçek 0,842 -> 0,031 / 0,39 m/s -> **PWM iç 0,080 / dış 1,000** (A ile aynı).
v 0,1 + w 1: −0,290 / 0,803 (aynı).

**El hesabı (moment).** Düz gidiş dengesi (iki yan torkunun toplamı = 2 x 0,171 N·m eklem sürtünmesi): ω / ω0 = 0,506, v =
0,199 m/s (fizik 0,199); dış tork +1,20, iç −0,86 N·m (A ile aynı); teker başı kuvvet ±16,5 N; dönme momenti 4 x 16,5 x 0,216 =
**14,3 N·m**. Yerinde (u ±0,546, durmada): 4 x (1,225 − 0,171) / 0,0625 x 0,216 = **14,6 N·m**: hareketli ve yerinde neredeyse aynı
moment ("PWM farkı 1,09'la sınırlı" doğru). Yanal kayma direncinin AM çevresindeki momenti (Coulomb, saf yanal kayma, üst sınır):
µ (121,6 x 0,1955 + 136,2 x 0,1745) = **µ x 47,5 N·m**; µ 0,5'te 23,8, µ 0,8'de 38,0 N·m > 14,3. Eşik µ ≈ 0,30 (saf yanal) ile
0,40 (önceki 0,65 katsayılı hesap) arası; fizikte dönme µ 0,40–0,45'te başlıyor (B: v 0,25 + w 1'de µ 0,40 -> 0,009, 0,35 -> 0,041,
0,30 -> 0,083 rad/s; v 0,1 + w 1'de µ 0,45 -> 0,021, 0,40 -> 0,044).

**Temas / zaman adımı duyarlılığı** (V0, v 0,25 + w 1, µ 0,5 ve 0,8): ana, dt 0,5 ms, solref 0,002 / 0,008, impratio 10, noslip 5:
w 0,000–0,002; piramit koni µ 0,5'te 0,023 (µ 0,8'de 0,002). Bulgu temas ayarına duyarsız (piramit koni önceki kontrolde de tek
sapan ayardı).

**Yanal direncin hıza bağlı olmaması.** MuJoCo'da (eliptik koni, Coulomb) kayan temasta kuvvet µN, kayma hızının yönünde;
yuvarlanan tekerde en küçük yanal kayma bile tam µN yanal kuvvet ister (yumuşak kısıtın küçük sürünmesi dışında). Bu modelin
özelliği, gerçek lastiğin değil: lastikte yanal kuvvet kayma açısıyla (α ≈ a·w / v) kademeli doğar (viraj sertliği C), µN'ye ancak
birkaç derecede doyar. Sonuç: hareket hâlinde küçük w için gerçek robot modele göre daha kolay döner; sapma **kötümser** yönde.
Kaba büyüklük (TAHMİN, C ölçülmedi): kararlı yayda w ≈ M v / (4 C a²); M 14,3 N·m, v 0,2 m/s, a 0,185 m, C 200–500 N/rad ile w ≈
0,04–0,10 rad/s (90° için 15–40 s). Yani gerçekte "yayla hiç dönmez" değil, "çok yavaş, geniş yay" olabilir; kullanışlı dönüş
yine yok.

**Sınıf.** Yerinde dönmeme (µ ≥ 0,45): fizik olarak sağlam mekanizma (firmware PWM farkı sınırı, moment dengesi), eşik TAHMİN
(µ, durma torku). Hareket hâlinde "hiç dönmüyor" (w ≤ 0,001): **mekanizması sağlam, sıfır değeri model ürünü** (Coulomb yanal
temas); doğru cümle "yay yerinde dönüşten kolay değil ve kullanışlı bir dönüş vermez", "yay çizemez" değil.

### 11.3 Varyantlar

**Yeniden üretim** (B'nin betiği, `olcum_varyantlar` ile aynı kurulum, 21 kg·cm, µ 0,5 / 0,8, yerinde w rad/s): V0 0,001 / 0,001;
V1 0,118 / 0,126; V2 0,088 / 0,086; V3 0,793 / 0,711; V4 0,519 / 0,382; V1+V3 1,664 / 1,579; V3 9 kg·cm 0,431 / 0,253. Hepsi
tabloyla aynı.

**Ayar duyarlılığı (µ 0,8, yerinde; ana / dt 0,5 ms / solref 0,002 / solref 0,008 / piramit / noslip 5 / impratio 10):**
- V3: 0,711 / 0,711 / 0,717 / 0,709 / 0,738 / 0,711 / 0,709: **±%4, güvenilir.**
- V1: 0,126 / 0,119 / **0,147** / **0,063** / 0,124 / 0,123 / 0,120: temas sertliğine **−%50 / +%17** duyarlı. Belgedeki "±%5"
  V1 için yanlış. Neden: V1'de dört teker de kayarak döner, teker yükü çırpıntısı (std 108–155 N; V0 düz gidişte 4 N) temas
  sertliğiyle değişiyor. V1 sayısı "yavaş döner (≈ 0,06–0,15 rad/s)" düzeyinde okunmalı.
- V2 kazançları (µ 0,5 / 0,8): kp 2 ki 10 -> 0,088 / 0,086; kp 1 ki 5 -> 0,095 / 0,091; kp 4 ki 20 -> 0,074 / 0,073; kp 8 ki 40 ->
  0,059 / 0,063; kp 2 ki 0 -> 0,054 / 0,033. Aralık 0,03–0,10; V1'i hiçbirinde geçmiyor (PWM tavanı aynı). "V2 0,09" TAHMİN'e bağlı;
  hüküm (V1 düzeyinde ya da altında) sağlam.

**V3 makara sıfırlaması.** Gerçek omni tekerde göbek ekseni hiç yatmaz, yanal serbestliği ayrı makaralar verir; açıyı her
adımda 0'a döndürmek bunun kinematik idealleştirmesi, savunulabilir. Enerji / kuvvet üretimi aranıp bulunmadı: dururken 10 s
(güç kapalı ve devrede) kayma ≤ 1e-8 m, dönme ≤ 1e-5°; yerinde dönerken güç kesilince w tekdüze sönüyor (V3 0,55 -> 0 / 0,25 s,
hiç artış yok); 30 N x 0,2 s yanal itmede güç kapalıyken V3 / V4 0,1° döner, kendiliğinden hızlanma yok. İtme davranışı makul
(ön aks yanal serbest, arka aks tutuyor). Ancak "yanal direnç 0" bir üst sınır: gerçek makaraların yuvarlanma direnci ve
boşluğu var; V3'ün yan eğim kayması (5° yanda 5 s'de 0,24 m / 16,5°) **en kötü durum**, dönüş hızı ise **en iyi durum**.

**Belgede eksik omni sınırlamaları.** Yazılı: ayrık makara titreşimi, makara yuvarlanma direnci, boyuna tutuşun düşmesi, temas
yaması. Yazılı değil: **eşik / kablo / halı geçişi** (küçük makaralar takılır; bugünkü 30 mm eşik bulgusu V3 için geçersiz), **yük
kapasitesi** (teker başı ≈ 61–68 N statik, frende ön aks yükü artar; 125 mm sınıfı omni tekerin taşıma değeri doğrulanmalı),
zemin kirine / pürüze duyarlılık.

**V4.** Küre + iki eksen serbest, tahriksiz: bilyalı (top) sarhoş teker; belge bunu söylüyor. Gerçekte yaygın olan dönen çatallı
sarhoş teker değil: çatalın yeniden yönlenme gecikmesi ve geri dönüşte savrulma yok; V4'ün dönüş sayıları çatallı teker için
**iyimser**, yan eğim kayması (0,43 m) model ürünü (çatal yanal yükte döner ama sürtünmesi var).

**Sınıflama.**

| Sayı | Sınıf |
| --- | --- |
| V0 yerinde / yay 0,001 | mekanizma sağlam; eşik TAHMİN (µ, durma torku); yay için sıfır model ürünü (Coulomb) |
| V1 0,12–0,13, 90° 12–13 s | "yavaş döner" sağlam; sayı temas ayarına ±%50 duyarlı (model) ve durma torkuna bağlı (TAHMİN) |
| V2 0,09 | kazanç TAHMİN'i (0,03–0,10); V1'i geçmez sağlam |
| V3 0,71–0,79; 9 kg·cm 0,25–0,43 | omni idealleştirmesine bağlı (üst sınır), ayara duyarsız; µ, durma torku TAHMİN |
| V4 0,38–0,52 | bilyalı idealleştirme (çatallı teker için iyimser); 9 kg·cm'de dönmez sağlam |
| V1+V3 / V2+V3 1,0–1,7 | V1 / V2 ve V3 TAHMİN'leri birlikte |
| tork / sürekli (2,0 / 2,3 / 0,6–0,8 …) | "sürekli = durmanın %30'u" VARSAYIM'ına bağlı; oranlar arası sıra sağlam |
| kolon süreleri | A'nın basit yönlendirmesine ve sonar kuralına bağlı; yalnız karşılaştırma için |
| V3 / V4 yan eğim 0,24 / 0,43 m | en kötü durum (yanal direnç 0, makara / çatal sürtünmesi yok) |
| yanal itme 6 mm, `dur` 0,083 m (V4) | model, büyüklük mertebesi |

### 11.4 Belge (`kod/SIMULASYON.md`)

Taraf tutmuyor: varyant tablosu ve "Kazanç / bedel" maddeleri iki yanı da sayıyor; başlıkta ve pencerede V0 dışı açıkça
"VARSAYIM, bugünkü robot değil". Düzeltilecekler:
- **E1 (koşul), satır 251 ve 257–258:** "bugünkü firmware'le robot yay da çizemiyor" / "Yanal kayma direnci (Coulomb) hıza bağlı
  olmadığı için yay, yerinde dönüşten kolay değil": modelin Coulomb temasının sonucu olarak yazılmalı; gerçek lastikte küçük
  w'de yavaş, geniş yay olası (model kötümser; büyüklük viraj sertliğine bağlı, ölçülmedi). Satır 261 "küçük w hiçbir µ'de daha
  iyi değil" aynı nedenle "modelde".
- **E2 (koşul), satır 294:** "dönüş hızı çözücü ayarlarına ±%5 duyarlı" V3 için doğru, V1 için yanlış (temas sertliğiyle 0,063–0,147).
  V1 / V2 sayıları aralıkla verilmeli; V2 için kazanç aralığı (0,03–0,10).
- **E3 (öneri), satır 290:** omni / sarhoş sınırlamalarına eşik / kablo geçişi ve yük kapasitesi eklenmeli; V3 yan eğim kayması
  "en kötü durum", V3 / V4 dönüş hızı "en iyi durum" diye etiketlenmeli.
- **E4 (öneri), satır 343 (K75):** "µ ≥ 0,45'te ne yerinde ne yayla döner": düşük v'de yay µ 0,45'te 0,021 rad/s veriyor (B);
  "µ ≥ 0,5" daha doğru. Satır, varyant sayılarını tek değerle veriyor (V1 0,12–0,13); E2'deki aralıklar oraya da taşınmalı.
  Hüküm cümlesinin geri kalanı (TAHMİN'lere ve idealleştirmeye bağlı) doğru.

### 11.5 Pencere

`kod\simulasyon3b.bat` temiz açılış, gerçek tarama kodlu tuş olayları (SendInput), pencerenin kendi günlüğü:
- 6 -> `arm ok`; Yukarı basılı 2,5 s -> `surus v 0,25`, bırakınca `tus birakildi -> dur`.
- Yukarı basılıyken başka pencere (B'nin açtığı boş form) öne -> aynı anda "odak kayboldu" + `dur`.
- **Başka pencere öndeyken Yukarı 2 s basılı tutuldu: hiçbir sürüş satırı yok** (robot sürülmedi). Kod: yoklama yalnız ön
  plandaki pencerenin süreci bu süreçse; MuJoCo penceresi aynı süreçte (görüntüleyici iş parçacığı), bat konsolu ayrı süreç.
- 8 -> "ACIL STOP mantari BASILDI"; basılıyken Yukarı: pencere `sur` gönderiyor (günlükte "surus" satırı), firmware reddediyor,
  robot yerinde (x 2,28, önceki fren yolu). Pencere reddi göstermiyor (küçük kullanım eksiği, `gonder(denetle=False)`). 8 + 6 ->
  `arm ok`, yeniden sürüş.
- Aşağı+Sağ -> komut v −0,25 / w **+1,00**; Aşağı+Sol -> w −1,00 (araba direksiyonu, belgedeki gibi).
- Shift+Enter -> pencere aynı süreçte yeni modelle açıldı, günlük "varyant V1 (VARSAYIM)"; ekran görüntüsünde en üstte
  "VARSAYIM: V1 firmware w tavani 3 rad/s (bugunku robot DEGIL)", durum satırında `[oda_rampa, V1]`; V0 görüntüsünde bu satır
  yok. V1'de Sol -> komut w 3,00.
- En uzun döngü 66–148 ms; pencere kapatılınca (WM_CLOSE) bat ve python süreçleri bitti, kalan süreç 0 (üç açılışta).

### 11.6 Özel veri ve commit

Kanca kalıpları değişen ve yeni dosyaların eklenecek satırlarına uygulandı (kanca gibi `+` önekli: 6.224 satır): anahtar, parola,
e-posta, IBAN / telefon, yerel yol, takma ad, ekip adı **0 isabet**. Satır başı dekoratör: yalnız `test_fizik.py`'deki
`fizik_gerekli` (noktasız ad; e-posta kalıbı alan adında nokta istediği için takılmaz). Not: kanca `+` önekli satıra baktığı için
sütun 0'da noktalı bir dekoratör (`modul.ad` biçimi) e-posta sayılır; bu ekte yok. 21 eski dosya md5 21 / 21 aynı.

**Girecek:** `kod/SIMULASYON.md`, `kod/simulasyon3b.bat`, `kod/fizik/dunya.py`, `fizik_esp32.py`, `gorunum3b.py`, `olcumler.py`,
yeni `kod/fizik/varyantlar.py`, `olcum_varyantlar.py`, `olcum_donus_hareket.py`, `planlama/d158/Y0f-olcum/donus-hareket.json|md`,
`donus-varyantlar.json|md`, `planlama/d158/Y0f-gunluk.md`, `planlama/d158/Y0f-kontrol.md`. **Girmeyecek:** 21 eski dosya
(değişmedi), `__pycache__/`.

### 11.7 Bakılmayanlar

`gorunum3b.py`'nin kumanda dışı yeni kısımları (katman metni, kol pozu) satır satır okunmadı; Enter (kol pozu), Shift+6–9
pencerede denenmedi; `olcum_donus_hareket.py` yeniden koşulmadı (md5 ve sayılar okundu, kendi ölçümüm aynı yönde); V3 / V4 yan
eğim ve yanal itme sayıları yeniden üretilmedi; kolon dolaşma süreleri yeniden üretilmedi; manevra (20 tekrar) yeniden koşulmadı;
gerçek klavyeyle (insan eli) deneme yapılmadı.
