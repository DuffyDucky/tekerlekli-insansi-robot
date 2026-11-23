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


## 12. Ek kontrol 2: firmware önerisi ve omni (`Y0f-gunluk.md` § 15)

Depo `749d6ee` üstüne çalışma ağacındaki ek ve depo dışı öneri dalı `oneri/donus-omni` (`e308120`; `origin/main` `71cf76d`
üstüne üç commit). Kalıcı yazı yok: derleme çıktısı ve deneyler geçici klasörde; öneri dalının çalışma ağacı `git status` temiz.

**Hüküm.** `lale-duzeltme` commit'i: **KOŞULLU GEÇER** (kod / veri engeli yok; 12.5'teki B1–B3 belge cümleleri düzeltilmeli).
Firmware önerisi Efe'ye: **HENÜZ HAZIR DEĞİL** (F1 enkoder arızasında kaçma riski not ya da kodda karşılanmalı; F2, F3 not
düzeltmesi). Kod mantığında hata bulunmadı; güvenlik yolları (bekçi, acil stop, `dur`, arm / bırak) PI durumunu doğru sıfırlıyor.

### 12.1 Firmware farkı (`motorlar.cpp` +47 / −14, `motorlar.h` 1 yorum satırı)

Satır satır okundu; `pio run` yeniden üretildi (ayrı derleme klasörüne): SUCCESS, RAM %6,9, Flash %24,3.
- **Sıfırlama yolları doğru.** Bekçi (`watchdog.cpp` -> `motorlar_ani_dur`), acil stop / arıza / bırak (`guc.cpp` -> `motorlar_ani_dur`)
  -> `teker_ani_dur`: hedef, rampa, integral, önceki hata 0, PWM hemen 0. `dur`: rampa fren sınırıyla 0'a iner; o adımda PID dalına
  girilmez, `integral = onceki_hata = 0`, çıkış 0. Güç devrede değilken savunma satırı hâlâ önce koşuyor. Yeniden devreye almada
  integral 0'dan başlar, `onceki_tik` güncel: sıçrama yolu yok. `dur` / acil stop sonrası birikmiş integralle kendiliğinden hareket
  yolu yok (hedef 0 -> çıkış 0).
- **Sarma önleme.** Hızlanma rampasında integral durur (`|rampa| >= |hedef| − 1e-4`); hedefte, frende ve yön değişiminin
  yavaşlama yarısında çalışır. Doyumda geri alma `cikis * onceki_hata > 0` ile; `onceki_hata` o adımda yeni hatayla güncellendiği
  için koşul "çıkış, bu adımın hatasıyla aynı yönde" demek: doğru, ad yanıltıcı (öneri: `hata` diye ayrı tutmak). Bölme yalnız
  `en_buyuk > 1` iken: sıfıra bölme yok. `DT` sabit 20 ms; döngü `main.cpp` 20 ms'lik yakalamalı zamanlayıcı (eski kodla aynı varsayım).
- **`INTEGRAL_SINIRI` 1,0.** Anlamı: integral teriminin PWM'e katkısı en çok ±1,0 (integralin kendisi ±0,05 m). Gerekçe sayısal
  olarak desteklenmiyor: A'nın kendi duyarlılığında 0,3 ile sonuç aynı (0,968), Efe notu satır 71 de "0,3 simülasyonda yetti"
  diyor. Değişiklik gereksiz yetki ekliyor; 0,3'te bırakmak ya da gerekçeyi masaya bırakmak daha temiz (F3).
- **F1 (risk, notta eksik): enkoder takılı / kopuk / ters.** `hazir` yalnız açılışta (`enkoder_kur`) belirleniyor; çalışırken kopan ya
  da takılan enkoder 0 hız okur, ters bağlı enkoder işaretli okur. B'nin modelde denemesi (ONERI, düz v 0,10 komutu, µ 0,8):
  enkoder sağlam 0,100 m/s (PWM 0,31); **iki yan takılı 0,396 m/s (PWM 1,0), ters 0,394 m/s (PWM 1,0), tek yan takılı v 0,21 + w −0,50
  rad/s (kendiliğinden döner)**. `dur`, bekçi ve acil stop bunu durduruyor (hepsinde PWM 0, v 0). Kodda algılama yok. Efe notu
  satır 64 ve 80 yalnız ters yönü yazıyor ve "okunamazsa (`hazir` false) açık çevrime düşer" diyor: çalışırken kopmada doğru değil.
  Öneri: (a) notta açık risk olarak yaz; (b) basit makullük denetimi (|çıkış| ≥ 0,8 iken |ölçülen| < 0,02 m/s 300 ms sürerse o yanı
  açık çevrime düşür ya da arıza olayı ver) ya da PI düzeltmesini ileri beslemenin ±0,5'iyle sınırla.
- **Uyum.** Adlandırma ve yapı Efe'nin koduyla uyumlu (`teker_adim`, `kirp`, `Teker` alanı, Türkçe yorumlar). Fark küçük; tek
  davranışsız ek `W_GIRIS_SINIRI` (1,0, eskisiyle aynı): belgeleme amaçlı, kabul edilebilir. `teker_adim` başka yerden çağrılmıyor.

### 12.2 Model ↔ C++

`fizik_esp32.py` `_oneri_adim` ve `varyantlar.py` `ONERI_FW` satır satır C++ ile karşılaştırıldı: sabitler, tik farkından hız,
ileri besleme, PI, rampa kapısı, integral kırpma, `rampa == 0` sıfırlama, birlikte doyum + geri alma aynı. Farklar A'nın yazdığı
gibi: rampa 10 ms dilimle (C++ 20 ms, `teker_adim` içinde), PWM 20 ms'de bir; ek olarak `_surucu` rampa 0 olunca PWM'i 20 ms
beklemeden 0 yapar (C++'ta `teker_ani_dur` da hemen yazar; `dur` sonunda en çok 20 ms fark). Modelin C++'ta olmayan bir kolaylığı
bulunmadı; sayılar bu firmware'in modeli.

### 12.3 Güvenlik testleri ve bozma deneyleri (B'nin kendi koşucusu, Y0s testleri fizikte, varyant yamalı)

V0 58 / 58 (koşucu doğrulaması); ONERI 57 / 58, ONERI-T 57 / 58 (A ile aynı, kalan aynı test).
- Bozma 1, bekçi motoru durdurmuyor: ONERI'de 4 güvenlik testi kalıyor (bekçi × 2, bozuk satır, kablo; "firmware teker hedefi
  sıfırlanmadı", PWM 0,75–0,79). Yakalanıyor.
- Bozma 2, integral sıfırlanmıyor ve rampa 0'da PWM integralden geliyor (C++'ta `else` dalı ve `rampa == 0 -> 0` satırı silinmiş
  gibi): 7 test kalıyor (bekçi × 2, bozuk satır, kablo, `dur` freni, sonar 30 cm, odo sıfırlama; "kısa devre freni yok", PWM 0,008).
  Yakalanıyor. İkisi de yalnız bellekte (yama); paket dosyası değişmedi.

**Kalan test yorumu doğru.** `test_cok_buyuk_w_kirpilir_donus_orani_korunur` (v 0,3, w 5): firmware hedefleri 0,066 / 0,39 (kırpma
ve oran doğru, testin bu kısmı geçiyor). PWM oranı PI'da hız hatasına göre değiştiği için tutmaz (iç teker robotça sürükleniyor,
PI iç PWM'i 0'a indiriyor). Korunan özelliğin fiziksel karşılığı enkoder oranı: beklenen 0,170; ONERI 0,214, açık çevrim omni (V3)
0,295, lastikle (V0 / ONERI-T) 0,99 (yay yok). Öneri oranı açık çevrimden iyi tutuyor ama tam değil: dış teker PWM 1'de 0,39'a
ulaşmıyor. Bu yüzden notun "oran = dönüş yarıçapı korunur" cümlesi (satır 17) fazla: korunan PWM oranı, hız oranı doyumda korunmaz.
Testi fizikte enkoder oranına (±%30) çevirmek daha anlamlı olur; gevşetmemek de savunulabilir (bilerek kalan, belgeli).

### 12.4 Ölçümler (yeniden üretim ve sınıf)

Yeniden üretim (yerinde, komut w 1; µ 0,5 / 0,8): ONERI 21 kg·cm 0,977 / 0,968, 9 kg·cm 0,860 / 0,720; ONERI-T 21 kg·cm 0,085 /
0,077, 9 kg·cm 0,001 / 0,001; 90° (A'nın yöntemi) 2,12 s, aşma 13,4°. Tabloyla aynı.

- **Yerinde dönüş ONERI 0,97 / 0,72–0,86:** ayar ve kazançlara duyarsız (A'nın duyarlılığı, B'nin yeniden üretimi); omni
  idealleştirmesine (küre + makara) ve TAHMİN'lere (durma torku, µ, makara sürtünmesi) bağlı. "Komutu izler" 21 kg·cm'de sağlam;
  9 kg·cm sayısı makara sürtünmesine çok duyarlı (aşağıda).
- **ONERI-T ≈ 0,08:** sağlam yön (lastikle kapalı çevrim de dönmüyor); sayı V1 gibi temas ayarına duyarlı olabilir (yeniden
  ölçülmedi).
- **90° aşması 8–15° "dur sonrası frenden" yanlış.** Ölçüm yönü `sur_tut`'un 200 ms'lik döngüsünde denetliyor. B yönü 10 ms'de bir
  denetleyince: `dur` 90,3°'de (w 0,96), son yön 95,0°: **frenden aşma ≈ 5°** (µ 0,5 / 0,8 aynı); kalan 8–10° ölçümün 200 ms denetim
  gecikmesi (w 1'de ort. ≈ 5,7°, en çok 11,5°). 0,213 m/s'den 1,8 m/s² ile el hesabı ≈ 3,4° + 20 ms döngü ≈ 1,1° = 4,5°: uyumlu.
  Pi tarafına öneri (erken / yavaşlayarak durma) yine geçerli ama gerekçe sayısı ≈ 5°.
- **`dur` 0,046 m (V0 0,070):** sağlam mekanizma: PI rampayı izliyor (açık çevrimde robot rampanın arkasından süzülüyordu). Rampa
  ivme sınırı aynı; Y1 testleri geçiyor.
- **Rampada tutma değişmedi:** sağlam (hedef 0 -> PWM 0 -> PI kapalı; tutma yalnız sürtünmeden). C++'ta da aynı.
- **Eşik 15 mm:** ONERI-T (lastik) de 15 mm geçiyor: kazanç **PI'nın düşük hızda tork vermesinden**, omniden değil. Ön omni küre
  olarak modellendi (makarasız, sürekli çember, µ 0,8 tutuş): gerçek omni tekerin basamak kenarına makara ya da makara arası
  boşlukla çarpması modelde yok. ONERI / ONERI-ADAY sütunundaki 15 mm ön omni için savunulamaz; belgede "lastikle (ONERI-T)
  ölçüldü; omniyle eşik geçişi modellenmedi, masada denenmeli" diye yazılmalı.
- **Makara yanal sürtünmesi, 13 N / 5 N eşikleri:** model eklemde sabit Coulomb sürtünmesi = katsayı × ortalama statik teker yükü
  (≈ 66 N) × r; yükle değişmez (dönerken teker yükü std ≈ 100 N çırpıyor, gerçek makara direnci yükle artar), yumuşak kısıt. Eşikler
  **TAHMİN'e (durma torku, µ) ve bu modele bağlı**; 21 kg·cm'de 13 N ile 20 N arası geçiş, 9 kg·cm'de 3–7 N arası geçiş yumuşak.
  Mertebe için kullanılabilir, karar sınırı olarak değil. Masadaki ölçüm tarifi (notta daha açık yazılmalı): teker gerçek yükte
  (≈ 65 N; robotun kendisi ya da ağırlık), gerçek zeminde, tekeri **yana yavaş ve sabit hızla** iten / çeken kuvvet ölçerle
  **sürekli (kinetik) kuvveti** oku, ilk kopma tepesini değil; birkaç makara geçişi boyunca ortalama ve en büyük; iki yön; ayrıca yük
  yarıya / 1,5 katına çıkınca kuvvetin değişimi (modelin sabit kabulünü sınar). Karşılaştırılacak sütun "yanal kuvvet N / teker".
- **Yan eğim 0,05 m, yana devrilme 23,5–23,9°:** geometri sağlam (ön temas noktası içeri), kayma omni idealleştirmesine bağlı.
- **Tork / sürekli:** "sürekli = durmanın %30'u" VARSAYIM'ı; 9 kg·cm'de 2,1–2,5 kat (ısınma) yön olarak sağlam.

### 12.5 Belgeler

Düzeltilecekler (`kod/SIMULASYON.md` = SIM, `donus-oneri.md`, Efe notu `ONERI-donus.md` = NOT):
- **B1, SIM 367 ve NOT 44:** 90° aşması 8–15° ve "dur sonrası fren" -> frenden ≈ 5°, gerisi ölçüm denetim aralığı (200 ms).
- **B2, SIM 373 ve NOT 47:** eşik 15 mm'nin kaynağı PI; omniyle eşik geçişi modellenmedi (ONERI-T'nin değeri lastik).
- **B3, SIM 356–358 ve NOT 25:** "Güvenlik davranışı aynı" -> bekçi / acil stop / güç yolları aynı; yeni risk: enkoder takılı /
  ters / kopukken PI tam güce çıkar (F1).
- **F2, NOT 64 / 80:** "okunamazsa (`hazir` false) açık çevrime düşer" yalnız açılışta geçerli; çalışırken kopma / takılma eklenmeli.
  Masada güvenli sıra öneri: (1) tekerlek havada, **KP = KI = 0** ile yön ve enkoder işareti (odo artıyor mu); (2) enkoder kablosu
  çekilerek / teker tutularak davranış (PI açıkken kaçma görülür: düşük KP ile ve elde acil stop); (3) KP, sonra KI; (4) yerde düşük
  hız, sonra dönüş. Notun 1. maddesi (1) i söylüyor; kodun varsayılanı KP 4 / KI 20 olduğu için "ilk yüklemede KP = KI = 0'a çek"
  açık yazılmalı.
- **F3, NOT 71 ve `motorlar.cpp` `INTEGRAL_SINIRI` yorumu:** 1,0 gerekçesi simülasyonda yok (0,3 ile aynı sonuç); iki metin
  birbirini tutmuyor ("0,3 yetmeyebilir" / "0,3 yetti").
- **NOT 17:** "oran = dönüş yarıçapı korunur" -> PWM oranı korunur; doyumda hız oranı (yarıçap) tam korunmaz (12.3).
- **NOT 20:** "ivme 0,575 m/s² (sınır 0,5)": testin eşiği 0,56 (SIM'de doğru).
- "Masada doğrulanacak" uyarısı ve "öneri, birleştirilmedi, karta yüklenmedi" açık; TAHMİN etiketleri (KP / KI, makara sürtünmesi,
  durma torku) yerinde. Taraf tutmuyor.

### 12.6 Pencere (`kod\simulasyon3b-omni.bat`, gerçek tarama kodlu tuş olayları)

Temiz açıldı, üstte "VARSAYIM: ONERI firmware oneri + on omni (bugunku robot DEGIL)". 6 -> arm; Sağ basılı 1,6 s -> −70°, Sol
1,6 s -> +70° (yerinde dönüyor); Yukarı -> ileri. 8 + Yukarı -> durum kutusunda "sur: acil stop: komut reddedildi" (ekran görüntüsü).
Odak başka pencereye geçince "odak kayboldu" + `dur`; arkadayken basılan oklar sürmedi. Kapatınca süreç kalmadı. Kolon dolaşma
tuşlarla denenmedi (başsız ölçüm var).
- **Backspace (R1):** B pencereye bilerek Backspace gönderdi: MuJoCo görüntüleyicisi `mj_resetData` yapıyor, robot modelin
  sıfır pozuna (odanın dışında, dünya başlangıcı) ışınlanıp **devrildi** (pitch −82°, teker yükleri 0); firmware durumu sürüyor.
  Kullanıcı sürerken yanlış tuşla "robot devrildi" görüntüsü üretir, yanlış bulgu riskidir. Öneri: modelin `qpos0`'ını başlangıç
  pozuna (serbest eklem + servo açıları) eşitlemek (Backspace başa koyar), ya da her döngüde `d.time` geri sıçramasını algılayıp
  "MuJoCo sıfırlaması: sahne başa kondu" yazmak; tuş ipucuna "Backspace: MuJoCo sıfırlama, kullanmayın" eklemek. A'nın gördüğü
  dışarıdan Backspace'in kaynağı bulunamadı (B'nin denemesinde kendiliğinden gelmedi); pencere sınamalarında iki kez nedeni
  bilinmeyen odak kaybı da görüldü (robot durdu: odak güvenliği çalışıyor).

### 12.7 Varsayılan, özel veri, commit

- 2B 58 / 58; V0 fizik koşusu çıkış 0, sayı özeti `f3507f3911bd53da`; `olcum.json`, `olcum.md`, `donus-varyantlar.json`,
  `donus-hareket.json` için `git diff` boş; 21 eski dosya md5 21 / 21.
- Kanca kalıpları (`+` önekli eklenecek satırlar: depoda 3.450, öneri dalında 149): **0 isabet**. Satır başı `@`: yalnız
  `simulasyon3b-omni.bat`'ta `@echo off` (noktasız, kalıba takılmaz). Öneri dalının commit yazarı bilgisi depodaki öbür
  commit'lerle aynı (kanca üst veriyi taramaz; mevcut düzen).
- **Girecek (`lale-duzeltme`):** `kod/SIMULASYON.md`, `kod/simulasyon3b.bat`, yeni `kod/simulasyon3b-omni.bat`, `kod/fizik/dunya.py`,
  `fizik_esp32.py`, `gorunum3b.py`, `olcum_varyantlar.py`, `varyantlar.py`, yeni `kod/fizik/olcum_oneri.py`,
  `planlama/d158/Y0f-olcum/donus-oneri.json|md`, `planlama/d158/Y0f-gunluk.md`, `planlama/d158/Y0f-kontrol.md`. **Girmeyecek:**
  21 eski dosya, `__pycache__/`. Öneri dalı ayrı (Efe'nin deposuna gidecekse F1–F3 sonrası).

### 12.8 Bakılmayanlar

ONERI-ADAY sayıları ve makara taraması yeniden üretilmedi (tablo okundu, model kodu incelendi); ONERI-T'nin temas duyarlılığı;
kolonu tuşlarla dolaşma; `gorunum3b.py`'nin reddedilen `sur` gösterimi dışındaki yeni satırları; karta yükleme ve gerçek enkoder
(yapılamaz); derlemede uyarı listesi (yalnız sonuç satırları okundu).

## 13. Ek kontrol 3: § 12 düzeltmeleri (dar ikinci kontrol)

B ajanı, 23.11 (02:15 – 02:45). Yalnız değişene bakıldı: öneri dalı `f22a149` (kod) ve `11b2931` (not), `lale-duzeltme` çalışma
ağacındaki commit edilmemiş değişiklikler (`Y0f-gunluk.md` § 16). A'nın iddiaları doğru sayılmadı; her biri koşuyla ya da
kodla denendi. Denemeler geçici dizinde, paket dosyalarına yazılmadı (paket dosyalarının son yazılma saati 02:12, bu turdan önce;
öneri çalışma ağacında `git status` boş).

**Hüküm.** `lale-duzeltme` commit'i: **GEÇER** (B1–B3 yapıldı; testler, özetler ve kanca temiz). Firmware önerisi Efe'ye:
**KOŞULLU HAZIR**: kodda engel yok, F1 koruması çalışıyor; koşul notta dört cümle (13.5: N1–N4). Test boşluğu (13.2) engel değil.

### 13.1 F1 kodda ve modelde

Kod (`git diff e308120..11b2931`): katman 1 `pay = DUZELTME_ORANI × |ileri besleme| + DUZELTME_TABANI`, düzeltme paya kırpılır,
payda iken integral artışı hatayla aynı yöndeyse geri alınır; katman 2 `supheli = payda && (|ölçülen| < 0,02 || ölçülen × rampa < 0)`,
25 ardışık adımda (500 ms) `enk_arizali` kilitlenir, o adımın çıkışı ileri beslemeye döner, integral / hata sıfırlanır. Model
(`fizik_esp32.py` `_oneri_adim`) aynı koşulları aynı sırayla uyguluyor; `kusku` sayaç sıfırlaması C++'ta `teker_ani_dur`'da, modelde
rampa 0 olunca (bir adım sonra, etkisi aynı). Küçük: `KUSKU_ADIM = KUSKU_SURE_MS / 20` DT yerine sabit 20 kullanıyor (DT
değişirse sessizce kayar).

Arıza senaryoları (B'nin betiği; sağlam enkoderle `once` süresince sür, sonra arıza, 3 s daha aynı komut; µ 0,8, 21 kg·cm; açı ve yol
arıza anından):

| Senaryo | Korumasız: yol / açı / son hız | Korumalı: yol / açı / son hız | Tespit |
| --- | --- | --- | --- |
| iki yan takılı, v 0,10 | 1,28 m / 0° / 0,396 m/s | 0,38 m / 0° / 0,077 | 550 ms |
| iki yan ters, v 0,10 | 1,28 m / 0° / 0,396 | 0,37 m / 0° / 0,077 | 510 ms |
| tek yan takılı, v 0,10 | 0,65 m / −88° / 0,20, w −0,50 | 0,36 m / −6,3° / 0,098, w +0,01 | 550 ms (yalnız o yan) |
| v 0,25'te iki yan kopma | 1,30 m / 0° / 0,396 | 0,88 m / 0° / 0,242 | 510 ms |
| tam hızda (0,39) iki yan kopma | 1,32 m / 0° / 0,396 | 1,32 m / 0° / 0,396 | 510 ms |
| tam hızda tek yan kopma | 1,00 m / −21,9° / 0,30 | 1,25 m / −2,6° / 0,39 | 510 ms |
| yerinde dönüşte (w 1) tek yan kopma | w 1,04, v −0,071 | **w 0,73, v 0,055** (sağlam: w 0,97, v 0,005) | 510 ms |
| aralıklı kopma (100 ms kopuk / 100 ms sağlam), v 0,2 | 0,76 m / 0° / 0,149 | aynı | **tetiklenmez** |
| yarı sayan sol enkoder, v 0,2 | 0,84 m / **−48,3°** / 0,261, w −0,27 | aynı | **tetiklenmez** |

Karşılaştırma, sağlam: v 0,10'da 3 s 0,33 m; tam hızda 1,30 m. Yani korumalı "0,36–0,38 m"nin ≈ 0,04 m'si arızadan, gerisi
komutun kendisi: 500 ms penceresinin bedeli küçük. Tam hızda koruma gerekmiyor (ileri besleme zaten 1, kaçacak pay yok); kilit
yine de 510 ms'de kuruluyor (zararsız). A'nın sayıları (1,22 m / 0,36–0,37 m / 510–550 ms / −84° / −6,3°) testte birebir çıktı;
benim betiğimde korumasız yol 1,28 m / −88° (ölçüm penceresi 100 ms dilimli, `ping`'li; fark yöntemden).

- **Korumanın yan etkisi (yeni tehlike?).** Düz gidişte küçük: tek yan kilitliyken öbür yan kapalı çevrimde kalıyor, sapma tam
  hızda −2,6°, v 0,10'da kilitten sonra w +0,01. Yerinde dönüşte belirgin: tek teker açık çevrime düşünce w 0,97'den 0,73'e iniyor
  ve robot 0,055 m/s ile kayarak çember çiziyor (korumasızda da kayma vardı, ters yönde). Tehlike değil, ama notta yok (N3).
- **Kilit sonrası `dur`, acil stop, bekçi** (tam hızda iki yan kilitli): `dur` 0,072 m (V0 0,070), acil stop 0,228 m (V0 0,228),
  bekçi 0,188 m; üçünde PWM 0. Doğru.
- **Kilit `birak` + `arm` ile kalkmıyor** (modelde denendi: `[True, True]` kaldı); C++'ta da yalnız yeniden açılışta (statik ilk
  değer) temizleniyor. Seçim doğru: kopuk enkoder `arm` ile düzelmez, yeniden açılış bilinçli bir adım olur. Ama not ve kod yorumu
  "yeniden başlatmaya dek kalır (`motorlar_baslat`)" diyor; `motorlar_baslat` `enk_arizali`'yi **sıfırlamıyor** (yalnız `teker_kur`,
  enkoder kurulumu, `onceki_tik`). Davranış doğru (`motorlar_baslat` yalnız `main.cpp:107` `setup`'ta çağrılıyor), cümle yanıltıcı (N1).
- **Gerçek durmada kilit kullanıcıya nasıl görünür:** hiç görünmez. Eşikte bir kez 500 ms takılan teker o oturumun sonuna dek açık
  çevrimde kalır; PI'nın getirdiği eşik kazancı ve dönüş hızı sessizce kaybolur (tek yan: yukarıdaki w 0,73). Protokol alanı yok
  (notta öneri var). Masa sırasının 2. adımı (tekeri elle tutma) kilidi kurar; sonraki adımdan önce yeniden başlatma yazılmalı (N2).
- **Kalan kaçma ve asıl güvence.** Takılı / ters enkoderde kalan kaçma küçük (yukarıda). Ama koruma yalnız "≈ 0 ya da ters" hızı
  görür: **yarı sayan enkoder** (ya da kayan kayış, yanlış `TIK_PER_TUR`) yakalanmaz ve robot v 0,2 komutunda 3 s'de −48° döner,
  hız 0,26; korumalı ile korumasız aynı. Aralıklı kopma da yakalanmaz (bu desende kaçma yok, robot yavaşlıyor). Bu durumlarda asıl
  güvence Pi'nin yön / odometri denetimi, `dur` ve acil stop; notun Riskler bölümü bunu söylemiyor (N3). PI kapalıyken (ilk
  yükleme) bu risklerin hiçbiri yok.
- **Yanlış alarm, iki koşuldan fazlasında yeniden üretildi:** yerinde dönüş 21 ve 9 kg·cm × µ 0,5 / 0,8 × w 0,5 / 1,0 (8 koşu;
  9 kg·cm µ 0,8 w 1'de gerçek w 0,72), 9 kg·cm ile 5° ve 10° yokuşta v 0,2 (10°'de gerçek hız 0,040, eşiğin hemen üstü; tetiklenmedi),
  21 kg·cm ileri 0,3'ten ani geri 0,3: hepsinde `arizali` `[False, False]`. 10° / 9 kg·cm koşusu sınıra yakın: biraz daha dik ya da
  ağır yükte gerçek durma sayılıp kilitlenebilir (o zaman doğru davranış).

### 13.2 Mutasyon (bellekte, dosyaya dokunmadan)

| Bozma | 4 testten kalan |
| --- | --- |
| yok | 0 |
| katman 2 kapalı (`kusku_adim` 10⁹) | 3 (iki yan takılı, iki yan ters, tek yan) |
| katman 1 sınırsız (`duzeltme_tabani` 100; payda hiç olmadığı için katman 2'yi de kapatıyor) | 3 |
| **yalnız katman 1 kırpması kaldırıldı** (payda tespiti duruyor) | **0** |

Testler katman 2'yi ve "korumanın tamamını" yakalıyor; katman 1'in asıl işi olan 500 ms boyunca çıkışı 2 × ileri besleme + 0,3'te
tutmak test edilmiyor (kırpma kaldırılınca yol 0,37 -> 0,40 m, testler yine geçti). Öneri (engel değil): pencere içinde PWM'in
`2 × ileri besleme + 0,3`'ü aşmadığını ya da ilk 500 ms yolunu denetleyen bir satır.

### 13.3 F2: `ONERI_PI_ACIK 0`

İki hâl de derlendi (öneri ağacı değişmedi, derleme dizini geçici): PI 0: RAM 22712 B (%6,9), Flash 319301 B (%24,4); PI 1: RAM aynı,
Flash 319329 B. Not satır 4 doğru. Kodda PI 0 iken `KP = KI = KD = 0` -> düzeltme 0 < pay (≥ 0,3) -> `payda` hiç olmaz, kilit
kurulmaz; çıkış = ileri besleme ve `motorlar_hedef` iki yanı 0,39'a ölçeklediği için |çıkış| ≤ 1: birlikte doyum ölçeklemesi de
hiç devreye girmez. Davranış 0.5.0 ile aynı (ikili 0.5.0 derlemesiyle karşılaştırılmadı; koddan). Not satır 15 "yeni olan yalnız
birlikte doyum ölçeklemesi" doğru ama PI kapalıyken o da etkisiz (N4, küçük). Simülasyonun PI açıkken yapıldığı açık: not satır 18
"Simülasyon sayılarının hepsi PI açıkken", `SIMULASYON.md` 368 "ONERI (öneri, PI açık + ön omni ...)".

### 13.4 F3, B1

- **F3:** 9 kg·cm, yerinde w 0,5, son 1,5 s ortalaması, µ 0,5 / 0,8: integral sınırı 0,3 -> 0,357 / 0,298; 0,6 -> 0,490 / 0,464;
  1,0 -> 0,490 / 0,464. A'nın 0,30–0,36 / 0,46–0,49'u doğru.
- **B1:** yön 10 ms'de bir, 90°'de `dur`: µ 0,5 `dur` 90,2°, son 95,1° (aşma 4,9°); µ 0,8 90,3° / 95,0° (4,8°). § 12'deki kendi
  değerimle (90,3° / 95,0°) aynı; A'nın 4,4–6,3° aralığıyla tutarlı.

### 13.5 Belgeler

Yapılanlar (satır numaraları güncel dosyada): B1 not 74, SIM 386; B2 not 77, SIM 387; B3 not 35–38, SIM 363–367; F2 not 13–18 (ilk
yükleme kapalı) ve 37 (`hazir` yalnız açılışta); § 12'deki NOT 17 (PWM oranı) not 25–27. TAHMİN'e dayanıp hüküm gibi yazılmış cümle
bulmadım (eşik, kazanç, süre, makara sayıları TAHMİN / "mertebe" etiketli).

Kalan (Efe'ye gitmeden):
- **N1, not 48 ve `motorlar.cpp` 66:** "yeniden başlatmaya dek kalır (`motorlar_baslat`)" -> "yalnız kartın yeniden açılışında
  temizlenir; `arm` / `birak` / `motorlar_baslat` temizlemez".
- **N2, not 95–96 (masa sırası 2):** tekeri elle tutma ya da fişi çekme kilidi kurar; 3. adımdan önce kartı yeniden başlat.
- **N3, not 49–51 ve Riskler 110 (SIM 363–367 de):** koruma yalnız takılı / ters enkoderi yakalar; yarı sayan / kayan enkoder ve
  aralıklı kopma yakalanmaz (simülasyonda yarı sayan sol enkoder, v 0,2: 3 s'de −48°); asıl güvence Pi'nin yön denetimi, `dur`,
  acil stop. Kilidin sessiz sonucu: gerçek durmada (eşik) o oturum boyunca o teker açık çevrimde; yerinde dönüşte tek teker
  kilitliyken w 0,97 -> 0,73 ve 0,055 m/s kayma.
- **N4, not 15 (küçük):** PI kapalıyken birlikte doyum da hiç devreye girmez; ilk yükleme davranışça 0.5.0.
- **K75:** Pakette önerilmiş bir K75 karar metni bulamadım. `karar-kuyrugu.md` K75 satırı hâlâ "açık / Önerilmedi", `SIMULASYON.md`
  416 hâlâ "seçenekler, öncelik sırası olmadan"; Ahmet'in 23.11 kararı (ön omni + firmware düzeltmesi, sarhoş teker yok) yalnız
  SIM 357'de ve günlükte. Kuyruğa yazılacak metin benim sınıflamamla tutarlı olmak için: geometri sağlam; dönüş sayıları ve
  makara sınırı TAHMİN (durma torku, µ, makara sürtünmesi) ve omni idealleştirmesine bağlı; masada doğrulanmadı. Kuyruğu
  güncellemek bu paketin işi mi, orkestratör kararı.

### 13.6 R1, gerçek Backspace

`simulasyon3b-omni.bat` penceresi, gerçek tuş olayları: 6, Sağ 1 s, Yukarı 1,5 s, **Backspace**, Yukarı 1,5 s, Yukarı basılıyken
Backspace. İki sıfırlamada da günlükte "MuJoCo sifirlandi (Backspace): robot basa kondu, dur", ekran görüntüsünde durum kutusunda
"sifir" satırı, robot başlangıçta dik (pitch 0,0, roll −0,0, teker yükleri 61 / 68 / 61 / 68 N), güç "devrede". Sonra Yukarı ile
robot sürülüyor (başlangıç x 1,50'den 1,80'e; başsız tekrarla doğrulandı: ONERI 1,5 s'de 0,323 m, V0 0,293 m; öneri modelinde
`arizali` yanlış alarm yok, PWM ve rampa sıfırlamadan sonra 0). Basılıyken Backspace: sıfırlama `dur` yapar, tuş hâlâ basılı
olduğu için sonraki döngüde sürüş yeniden başlar (basılı tut mantığıyla tutarlı). R1 kapandı.

### 13.7 Commit hazırlığı ve depo

- 2B 58 / 58; fizik testleri 10 / 10 (yeni 4 test dahil); Y0s fizikte V0 58 / 58, ONERI 57 / 58 (aynı test, aynı biçim: iç teker
  PWM'i ≈ 0); V0 sayı özeti `f3507f3911bd53da` (geçici dizine). `olcum.json|md`, `donus-varyantlar.json|md`, `donus-hareket.json|md`
  farkı boş. 21 eski dosya md5 aynı.
- Kanca kalıpları: `lale-duzeltme` çalışma ağacındaki 14 dosyanın tamamı ve öneri dalının `origin/main..11b2931` eklenen 300 satırı:
  0 bulgu. Satır başı süsleyici: `test_enkoder_ariza.py` yalnız girintili `@classmethod` (noktasız, girintili; kalıba takılmaz).
- `.git/index.lock` olayı: kilit dosyası yok, `git fsck --no-dangling` temiz (çıkış 0), `MERGE_HEAD` / `CHERRY_PICK_HEAD` /
  `rebase-*` yok, `git status` normal. Yarım kalmış işlem izi yok.
- **Girecek (`lale-duzeltme`, 14):** `kod/SIMULASYON.md`, `kod/simulasyon3b.bat`, yeni `kod/simulasyon3b-omni.bat`,
  `kod/fizik/dunya.py`, `fizik_esp32.py`, `gorunum3b.py`, `olcum_varyantlar.py`, `varyantlar.py`, yeni `kod/fizik/olcum_oneri.py`,
  yeni `kod/fizik/testler/test_enkoder_ariza.py`, yeni `planlama/d158/Y0f-olcum/donus-oneri.json|md`, `planlama/d158/Y0f-gunluk.md`,
  `planlama/d158/Y0f-kontrol.md`. **Girmeyecek:** 21 eski dosya, `P108d*` dosyaları (başka paket), `__pycache__/`. Öneri dalı
  (`a41815f`, `120a9a7`, `e308120`, `f22a149`, `11b2931`) ayrı; N1–N4'ten sonra Efe'ye.

### 13.8 Bakılmayanlar

PI kapalı ikilisinin 0.5.0 ikilisiyle bayt karşılaştırması (yalnız koddan); başka aralıklı kopma desenleri (ör. 400 / 100 ms) ve
gürültülü (rastgele) enkoder; ONERI-ADAY ve ONERI-T'de arıza senaryoları; `donus-oneri.json` yeniden üretimi (A'nın md5'i
okunmadı); kolonun tuşlarla dolaşılması; karta yükleme ve gerçek enkoder (yapılamaz).

## 14. Ek kontrol 4: makaralı omni ve web demosu

B ajanı, 23.11 (03:00 – 04:20). Depo `lale-duzeltme` = uzak = `ff2e4a2`; iki iş commit edilmemiş. İş 1: makaralı omni
(`Y0f-gunluk.md` § 18). İş 2: web demosu (`tasarim/Robot-Tasarim-Demosu.html`). İddialar doğru sayılmadı. Denemelerin hepsi
geçici dizinde yapıldı: demo sayfası geçici dizine yeniden üretildi, tarayıcı profilleri geçici. Paket dosyalarına yazılmadı.

**Hüküm.**
- İş 1 (makaralı omni): **KOŞULLU GEÇER.** Kodda ve sayılarda engel yok; V0 yolu değişmedi; iki sayısal ayar savunulabilir ve
  yeniden üretildi. Koşul: 14.5'teki S1–S6 belge cümleleri düzeltilmeli.
- İş 2 (web demosu): **GEÇER.** Bir koşulla: "merkez lastikle aynı" cümlesi hüküm gibi duruyor, fizik modeli farklı bir kabul
  yapıyor (D1).
- **Enkoder konumu bulgusu doğru**, sonuçları K75'e ve Efe notuna girmeli (14.4).

### 14.1 V0 ve ONERI yolu

- `dunya.py`: makaralı dal yalnız `on_teker == "makara"` iken çalışıyor. Teker geom kümeleri lastik ve küre tekerde tek geom
  döndürüyor. `ccd_tolerance` yalnız makaralı dalda değişiyor. Küre ve sarhoş dalı `in ("omni", "sarhos")` ile daraltıldı; bu,
  ONERI ve ONERI-ADAY'ın `on_teker` değerleriyle aynı sonuç veriyor.
- `kod/testler/duzenek.py` (+4 satır): yalnız `_fizik_karti` içinde `LALE_VARYANT` ortam değişkeni varsa varyantlı fizik kartı
  kuruluyor. `FIZIK_FARKLARI` ve 2B yolu değişmedi; muafiyet gevşemedi. Risk: değişken ortamda unutulursa Y0s bugünkü robotu
  değil varyantı sınar. Koşucu bunu çıktıda göstermiyor (küçük).
- `test_enkoder_ariza.py`: varsayılan yine ONERI; korumasız kopya artık seçilen varyanttan türetiliyor.
- Sonuçlar:
  - 2B 58 / 58; fizik testleri 10 / 10; Y0s fizikte V0 58 / 58.
  - V0 sayı özeti `f3507f3911bd53da` (geçici dizine).
  - `Y0f-olcum` altında yalnız yeni `omni-makara.*` dosyaları; `donus-*` ve `olcum.*` farkı boş.
  - 21 eski dosya md5 aynı.
  - ONERI-MAKARA ile: Y0s 57 / 58 (aynı test, aynı biçim); arıza testi 4 / 4. Değerler: 0,37 / 0,36 m; −7,1°; 510–550 ms.

### 14.2 İki sayısal ayar

**Sürtünme kısıtı sertliği (`solimpfriction`).** Tek teker düzeneği kuruldu: kilitli makaralı teker (`omni_makara.teker_xml`),
62 N yük, 0,8 µ. Kızak yana 0,01 m/s ile çekildi.

| `solimpfriction` | yatak 0 N | 2 N | 5 N | 13 N | 200 N |
| --- | --- | --- | --- | --- | --- |
| 0,9 (varsayılan) | 0,00 | 0,03 | 0,03 | 0,03 | 0,03 |
| 0,9999 | 0,00 | **2,00** | **5,01** | **13,02** | 16,98 (temas kayıyor) |

Tablodaki değerler yanal çekme kuvveti (N), tek makara temasta.

- Varsayılanla eklem sürtünmesi yok hükmünde. Gerekçe: küçük atalette düzenleme terimi büyüyor. 0,9999 ile ölçülen kuvvet
  beklenen değerle birebir: sürtünme momenti / makara yarıçapı = parametre.
- Yönden bağımsız; 0,1 m/s'de 2,00 N. Yalnız 0,001 m/s'de 1,70 N, çünkü temasın kendi kayması devreye giriyor. 200 N'da
  yumuşak temas sürünüyor: 0,001 / 0,01 / 0,1 m/s'de 1,7 / 17 / 49,6 N; µN = 49,6.
- Robotta: 9 kg·cm, µ 0,8, yerinde w komutu 1.
  - `solimpfriction` 0,9: 2 N ile 0,884, 200 N ile 0,882 (A'nın "aynı sonuç" gözlemi yeniden üretildi).
  - 0,9999: 2 N ile 0,776, 200 N ile 0,004.
- Ayar sonucu bir yöne çekmek için seçilmiş değil: modele, parametrenin anlamını veren tek değer bu.
- **İki satır birden temasta iken direnç ikiye katlanıyor.** Faz 8,2°'de 2 N için 4,28 N, 5 N için 10,69 N. Sürüşte iki satır
  birden temasta: düz gidişte zamanın %30'u, yerinde dönüşte %10'u.
- Gerçekte pim sürtünmesi yükle bölünür; iki makaraya bölünen yükte toplam aynı kalır. Model ise makara başına sabit moment
  veriyor. Yani modeldeki "2 N", tek temas fazında tekerin yanal direnci; iki temas fazında ≈ 4,3 N. Yerinde dönüşte etkin
  ortalama ≈ 2,2 N, düz gidişte ≈ 2,7 N. Belgede "eşdeğer yanal kuvvet teker başına" diye geçiyor (S4).

**ccd toleransı.** Senaryo: 15° rampa, 21 kg·cm, v 0,25, ön enkoder. Ön makaralar ile kutu (rampa ve zemin) arasındaki her
temasın normali kutu yüzlerine göre ölçüldü.

| durum | normal > 2° sapan | en büyük | 14,4 m'ye varış |
| --- | --- | --- | --- |
| elipsoid, 1e-6 (varsayılan) | **%8,2** | 28,2° | **22,1 s** |
| elipsoid, 1e-7 / 1e-8 | %1,9 / %1,0 | 28,2° | 29,1 / 29,8 s |
| elipsoid, 1e-9 (seçilen) | %1,3 | 16,2° | 30,6 s |
| 5 küre (kesin küre çarpışması; 1e-6 ve 1e-9 aynı) | %1,1 | 16,3–18,3° | 31,0 / 31,5 s |
| küre modeli ONERI-ADAY | %1,4 | 15,4° | 28,9 s |

- Kalan ≈ %1, kenar temasları (rampa başı ve sonu); her biçimde var.
- 1e-9, ccd'ye bağlı olmayan kesin çarpışmalı iki modelle aynı sonucu veriyor; 1e-6 tek başına sapıyor. Seçim
  savunulabilir.
- "Sahte çekiş" yeniden üretildi: 1e-6 ile rampa 8 s erken çıkılıyor.
- Sayı farkı: A "%3, 28°" diyor, ben %8,2 ölçtüm (ölçüt farklı: ben bütün kutu temaslarını, 2° eşiğiyle saydım). Nitel hüküm
  aynı. `omni_teker.json` `ccd_toleransi.kaynak` "0,16 m/s yerine 0,10" diyor; ölçüm dosyası ve SIM 0,166 / 0,088 diyor (S6).

### 14.3 Makaralı modelin fiziği (yeniden üretilenler)

| Ölçüm | B | A | Sınıf |
| --- | --- | --- | --- |
| dururken 10 s (güç kapalı) | kayma 0,17 mm, makara hızı 1e-4 rad/s | - | model ürünü (yumuşak temas sürünmesi); enerji üretimi yok |
| boş yanal yuvarlanma direnci (yatak 0 N) | 0,00 N | - | sağlam (model kurgusu) |
| düz v 0,25: ön çevre / gövde hızı; makara hızı | 1,0002; ort. 0,00, en çok 0,02 rad/s | - | sağlam: eksen boyunca kayma yok, makara düz gidişte dönmüyor |
| yük paylaşımı, düz (ön sol) | satır a / b 32,2 / 31,1 N; iki satır temasta %30 | - | geometri (sıra aralığı 10 mm TAHMİN) |
| yerinde w 1: makara hızı | ort. 41 rad/s (≈ 0,39 m/s yanal) | - | geometri |
| yerinde w 1, 21 kg·cm, µ 0,5 / 0,8 | 1,066 / 1,062 | 1,066 / 1,062 | TAHMİN'e bağlı (tork, µ, yatak) |
| yerinde w 1, 9 kg·cm, µ 0,5 / 0,8 | 0,928 / 0,776 | 0,928 / 0,776 | TAHMİN'e bağlı; yatak sürtünmesine çok duyarlı |
| yatak 2 / 5 N, 9 kg·cm µ 0,8 | 0,776 / 0,403 | 0,776 / 0,403 | TAHMİN'e bağlı |
| yatak 2 / 5 N, 21 kg·cm µ 0,8 | 1,062 / 1,058 | 1,062 / 1,058 | TAHMİN'e bağlı |
| eşik v 0,2, 21 kg·cm: 15 / 20 / 25 mm | geçti / geçti / **geçti** | md: geçti / geçti / geçti | model ürünü + TAHMİN |
| eşik, küre modeli (ONERI-ADAY): 15 / 20 / 25 mm | geçti / geçti / **ön çıktı, geçmedi** | aynı | |
| eşik 9 kg·cm: 15 / 20 / 25 mm | geçmedi ×3 | 10 mm'den itibaren geçmedi | TAHMİN'e bağlı |

Sayıların hepsi A'nınkiyle birebir çıktı.

**Eşik hükmü nasıl yazılmalı.** "21 kg·cm'de 20 mm eşik çıkıyor" hüküm olarak yazılamaz:
- Küre modeli de 20 mm'yi geçiyor; sonuç teker yarıçapı (63,5 mm), motor torku (TAHMİN) ve kenar sürtünmesinden (µ 0,8,
  TAHMİN) geliyor.
- Makaraya özgü üç şey modelde yok: göbek tırnağı ve makara arası boşluk, makara ucunun kenara takılması, kauçuğun ezilmesi.
- Elipsoid temas fiziksel makara boyunu aşıyor (a 24,9 mm, makara yarı boyu 11 mm). Fazlası teker çemberinin içinde kalıyor ama
  sivri kenarda boşluk yerine yüzey veriyor.

Önerilen cümle: "Modelde 21 kg·cm motorla v 0,2'de 25 mm'ye dek geçiyor (küre modeli 20 mm); 9 kg·cm motorla yalnız 5 mm. Bu
teker çapı ve TAHMİN tork / µ'nün sonucu; makara-tırnak-kenar etkileşimi modellenmedi, eşik masada denenmeli."

**Titreşim nasıl sunulmalı.** 0,09–0,15 mm (elipsoid) ile 1,6–2,5 mm (kapsül) iki model kabulünün sonucu, gerçek değerin
sınırları değil. Gerçek tekerde makara arası boşluk, kauçuk esnekliği ve imalat salgısı var; ikisinde de yok. Önerilen cümle:
"Model kabulüne bağlı: elipsoidle 0,09–0,15 mm, kaba kapsülle 1,6–2,5 mm (1,58 m noktası, ileri t-t); gerçek değer bilinmiyor,
masada ölçülecek. Baskın frekans makara geçişi (v 0,25'te ≈ 14 Hz)."

### 14.4 Enkoder konumu

**Depoda enkoderler arka motorlarda.** Dayanaklar:
- `planlama/adim3/pin-haritasi.md` 100–103: GPIO 18 / 17 "sol arka JGB37 Hall A / B", 16 / 15 "sağ arka JGB37"; 398: "Ön
  enkoderler: bağlanmadı (pin yok)".
- `planlama/adim3/elektrik.md` 488–489 (aynı pinler, "Enkoder sol arka / sağ arka") ve 495 ("Ön motorların enkoderleri
  bağlanmadı").
- `planlama/adim3/kablolar.md` N01 / N02 (908–945: "JGB37 arka sol / arka sağ → GPIO18 / 17, 16 / 15").
- Firmware `origin/main` `kod/esp32/include/pinler.h` 35–38: `PIN_SOL_ENK_A 18` … `PIN_SAG_ENK_B 15`; tekerin adı yok, pinler
  pin planıyla aynı.
- Tutarsızlık: `elektrik.md` 204 "ön enkoderler kayma tespiti içindir" (eski cümle, 495 ile çelişiyor).

**Sonuç.** Simülasyon varsayılanı (`fizik_parametreleri.json` 18 `enkoder_teker: on`, kaynak "kaynakta yok") pin planıyla
çelişiyor. Kendi koşum (µ 0,8, yerinde w komutu 1, arka / ön enkoder):

| | 21 kg·cm | 9 kg·cm |
| --- | --- | --- |
| ONERI (bu gecenin `donus-oneri`'si) | 0,892 / 0,968 | 0,742 / 0,720 |
| ONERI-MAKARA | 0,904 / 1,062 | 0,805 / 0,776 |

`donus-oneri` sayıları (ONERI 21 kg·cm 0,97–0,98) yalnız ön, yani omni tekerde enkoder olsaydı geçerli. Pin planıyla
21 kg·cm'de ≈ 0,89–0,90: ön omni kayması enkoderde görünmüyor, PI arka lastiğin hızını tutuyor. 9 kg·cm'de fark küçük ve ters
yönde. 15° rampada arka enkoder daha iyi: 0,12 m/s, ön enkoderle 0,09 (A'nın ölçümü). V0 sonuçları etkilenmiyor: açık
çevrimde enkoder yalnız odometri.

Olumlu yan sonuç: enkoderli teker arka Ø125 lastik olduğundan `TEKER_CAPI_M` 0,125 doğru kalıyor. Aday omninin Ø127'si
firmware'e girmiyor; Efe notundaki "%1,6 sapar" riski ortadan kalkıyor.

**Düzeltilecek cümleler** (öneri ağacına yazmadım; metin önerisi):
- **Efe notu** (`ONERI-donus.md`, öneri dalı `fc940a0`) 89–92: "enkoderin hangi tekerde olduğu kaynakta yazmıyor (simülasyon
  önde kabul etti) … Kural: `TEKER_CAPI_M` = enkoderli tekerin çapı. Yanlış kalırsa … %1,6" ->
  "Enkoderler pin planına göre arka motorlarda (`planlama/adim3/pin-haritasi.md` 100–103; ön motorlarda enkoder yok). Arka teker
  Ø125 lastik kaldığı için `TEKER_CAPI_M` 0,125 doğru, ön omni çapı firmware'e girmez. Simülasyon tablosu ön enkoderle alındı;
  arka enkoderle yerinde w (komut 1) 21 kg·cm'de 0,89–0,90, 9 kg·cm'de 0,74–0,81."
- Notun yerinde dönüş satırı ve masa sırası 98'deki "enkoderin hangi tekerde olduğunu belirle" -> "arka enkoderin yönünü
  doğrula".
- **SIM 376** (ONERI tablosu) ve 357–372 paragrafı: "enkoder ön (TAHMİN); pin planında arka: arka enkoderle 0,89 (21 kg·cm)"
  notu. SIM 398'de zaten "enkoder arka tekerde 0,89" var, tabloya taşınmalı.
- **`fizik_parametreleri.json` 18** `kaynak`: "kaynakta yok" yanlış -> "pin planı arka (pin-haritasi.md 100–103); simülasyon ön
  seçti (TAHMİN, karşılaştırma için)". Varsayılanı "arka" yapmak ayrı bir paket işi; V0 özeti değişmeyebilir ama `donus-*` ve
  `donus-oneri` yeniden üretilir.
- **K75'e madde:** "Enkoderler arka (lastik) motorlarda (pin planı). Simülasyonda öneri + ön omni, arka enkoderle yerinde w
  (komut 1) 21 kg·cm 0,89–0,90 rad/s, 9 kg·cm 0,74–0,81 rad/s; ön enkoderli sayılar (0,97–1,06) bugünkü pin planında geçerli
  değil. Sayılar TAHMİN parametrelere (durma torku, µ, makara yatak sürtünmesi) bağlı, masada doğrulanmadı."

### 14.5 Belgeler: `SIMULASYON.md` "Makaralı omni" ve `omni-makara.md`

- **S1, SIM 418:** "pencerede 12–16 × gerçek zaman" -> "başsız ölçümde 12–16 × gerçek zaman. Pencere gerçek zamanda koşar (B:
  37 s'de sanal = duvar, en uzun döngü 168 ms; ONERI'de 95 ms)."
- **S2, SIM 442–443:** "20 mm'ye dek geçer, 25–30 mm'de ön teker çıkıp arka takılır … (küre modeliyle aynı)" yanlış. Ölçüm
  dosyası ve B: makarayla 25 mm geçiyor, 30 mm'de ön çıkıyor; küre modelinde 25 mm'de ön çıkıyor. 14.3'teki cümleyle
  değiştirilmeli. Günlük § 18 394 ("eşik aynı") da.
- **S3, SIM 443–444:** "gerçek değer bu ikisinin arasında" TAHMİN'i hüküm gibi yazıyor -> 14.3'teki titreşim cümlesi.
- **S4, SIM 444–446 ve `omni-makara.md` "Makara yatağı sürtünmesi":** "eşdeğer yanal kuvvet" -> "makara başına; iki satır birden
  temasta iken model direnci ≈ 2,1 katına çıkıyor (yerinde dönüşte zamanın %10'u, düz gidişte %30'u)".
- **Teker seçimi ölçütü** şöyle aktarılmalı: "Masada ölçülen, teker gerçek yükte (≈ 62 N) yavaşça yana çekilirken sürekli
  kuvvet, modeldeki parametreyle doğrudan karşılaştırılır (tek temas fazı). Modelde 9 kg·cm motorla 2 N'da w 0,78–0,93, 5 N'da
  0,40–0,53, 7 N'da dönmüyor; 21 kg·cm ile 7 N'a dek etkisiz. Mertebe, sınır değil (sabit Coulomb, yükten bağımsız; 2 N değeri
  pim µ 0,2 TAHMİN'inden)."
- **S5, `omni_teker.json` `makara_yatak_surtunmesi_N.kaynak`:** yukarıdaki "makara başına" bilgisi eklenmeli.
- **S6, `omni_teker.json` `ccd_toleransi.kaynak`:** "0,16 m/s yerine 0,10" -> "0,17 yerine 0,09" (ölçüm dosyasıyla aynı).
- SIM 427: "%3" ölçütü yazılmalı (14.2).

### 14.6 Pencere (`simulasyon3b-omni.bat`, gerçek tuşlar, şimdiki hâli)

Pencere temiz açıldı: "ONERI-MAKARA (VARSAYIM)", hata akışı boş.

- **Sürüş:** 6 -> arm ok. Sağ 1,5 s -> −70° dönüş. Yukarı 2 s ve Yukarı+Sol yay çalıştı.
- **Görünüm:** 1 tuşu gövde ağını gizledi; yakın kırpımda ön tekerler makaralı (turuncu makara çizgileri), arka tekerler
  lastik.
- **Odak:** Yukarı basılıyken odak başka pencereye alındı -> "odak kayboldu … dur".
- **Acil stop:** 8 + Yukarı -> "ariza ACIL STOP", "acil stop: komut reddedildi", gerçek hız 0.
- **Backspace:** "MuJoCo sifirlandi … basa kondu, dur". Sonra Yukarı ile 1,50 -> 1,81 m sürüldü.
- **Hız:** sanal 37,0 s = duvar 37,0 s, en uzun döngü 168 ms.
- **Kusur (küçük):** makaralıda üstte eklenen "1 tusu …" satırıyla tuş ipucunun son satırı kesiliyor ("Shift+8 basa koy  Shi").
  Shift+9 / Shift+Enter / fare ipucu görünmüyor; acil stop sırasında Enter'dan sonrası da. MuJoCo katman metni sınırı;
  ipucu kısaltılmalı.
- Varsayılan kamerada tekerler küçük; makaralar ancak yakın bakışta seçiliyor.

### 14.7 İş 2: web demosu

- **Yeniden üretim:** `demo_uret.build` çıktıyı geçici dizine yazacak biçimde koşuldu. Sonuç paketteki sayfayla bayt bayt
  aynı (198 031 B, md5 `31fb8345…`). Elle düzenleme yok.
- **Doğrulayıcı:** `F9b-dogrula.py` (tarayıcılı, `--goruntu`suz, yazma yok) **GEÇER**, hata 0. 1400 ve 360 px'te taşma yok,
  konsol hatası 0.
- **Başsız Chrome:** varsayılan, yan, ön ve izometrik görünümler; `?teker=lastik`; 360 px.
  - Omni ön tekerler makaralı, yere değiyor.
  - Ön görünümde göbek adaptörü görünüyor (omni lastiğin merkezinde, dışa doğru).
  - Opak kabukta etek tekerleri örtüyor; eteğe ya da gövdeye girme görmedim.
  - `?teker=lastik` eski görünümü veriyor (iki görüntü yan yana karşılaştırıldı; KPI'daki omni kütle cümlesi kayboluyor).
- **Sayılar:**
  - Kütle: omni 480 − lastik 140 = +340 g / teker; +680 g; 25,88 -> 26,56 kg. Kaynak anahtarlarından (`omni_kutle`,
    `lastik_kutle`, `kutle_g`) JS ile hesaplanıyor, tutuyor.
  - "ön uç ≈ 1 mm yükselir" = (127 − 125) / 2.
  - Kaplinin göbeğe ≈ 1 mm girmesi bilinen kusur olarak yazılmış; görsel olarak ayrıca ölçmedim.
- **Kaynaklar:**
  - three.js aynı kaynaktan: `cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js` (fark yok).
  - `rehber/`, GLB ve kök `index.html` değişmemiş (`git status`).
- **Pages:** `gh api repos/…/pages`: `source.branch = main`, path `/`, legacy build. **`lale-duzeltme`'nin push'u yayını
  değiştirmez**; yayın ancak `main`'e birleştirilince değişir. Ama depo **public**: push edilen dalın içeriği yayında olmasa da
  herkese açık.
- **D1:** Sayfa notu "Merkez lastikle aynı (aks, iz ve aks aralığı değişmez)" diyor. Bu bir demo kabulü (`taban_lib.py`
  `omni_local`), karar değil:
  - CAD içinde çelişki var (`arayuz.py` "içeri kayar").
  - Fizik modeli öbür kabulü kullanıyor: `varyantlar.ADAY_TEKER` `on_teker_y_iceri_m` 14,5 mm, iç yüz aynı, ön iz 29 mm dar.
  - Cümle "demo kabulü; fizik modeli iç yüzü aynı tutuyor (merkez 14,5 mm içeri); karar açık" olmalı.

**İki parametre dosyası** (`tasarim/cad/omni-teker.json` ve `kod/fizik/omni_teker.json`):
- **Aynı:** Ø127, 29 mm, 2 sıra, 22 makara, 480 g, makara Ø19 × 22 (boy TAHMİN), göbek deliği 6 mm (TAHMİN; CAD 12 mm altıgen
  adaptör diyor, teyit), sıra ofseti ±5 mm (fizik "aralık 10").
- **Çelişen:**
  1. Teker merkezi: CAD aynı merkez + adaptör; fizik 14,5 mm içeri.
  2. Göbek Ø57 × 25 yalnız CAD'de; kaynağı "brief'te ürün sayfası değeri olarak verildi", fizik ürün sayfasında bulamamış.
  3. Ürün sayfası adresi `ozrobotics.com` ile `www.ozrobotics.com` (aynı sayfa).
- **Birleştirme önerisi:**
  - Tek kaynak `tasarim/cad/omni-teker.json`: ürün ve geometri alanları, alan başına `durum` / `kaynak` (fizik dosyasının
    biçimi), merkez kararı tek alan. CAD de buradan beslenmeli; model `lale.xml` CAD'den üretildiği gibi.
  - `kod/fizik/omni_teker.json` yalnız modelleme alanlarını tutmalı (makara kütlesi, pim µ, yatak sürtünmesi, sönüm,
    `solimpfriction`, ccd, temas biçimi) ve geometriyi CAD dosyasından okumalı.
  - CAD adımında `arayuz.py` `TABAN['omni']` aynı dosyayı okumalı; merkez çelişkisi o adımda karara bağlanmalı.
  - Birleştirmeyi yapmadım.

### 14.8 Commit hazırlığı

- Kanca kalıpları, iki işin 19 dosyasının tamamında: 0 bulgu.
- Satır başı süsleyici:
  - `@echo off` (iki `.bat`) noktasız.
  - Demo ve şablondaki `@media(…)` satırları: `@`'den sonra nokta değil parantez geliyor; e-posta kalıbına takılmaz.
- 1 MB üstü dosya yok (en büyük: demo sayfası 198 KB, `omni-makara.json` 131 KB). 21 eski dosya md5 aynı.
- **Commit 1, makaralı omni (15):**
  - `kod/SIMULASYON.md`, `kod/fizik/dunya.py`, `gorunum3b.py`, `varyantlar.py`, `testler/test_enkoder_ariza.py`
  - `kod/simulasyon3b.bat`, `kod/simulasyon3b-omni.bat`, `kod/testler/duzenek.py`
  - yeni: `kod/fizik/omni_makara.py`, `omni_teker.json`, `olcum_makara.py`
  - yeni: `planlama/d158/Y0f-olcum/omni-makara.json|md`
  - `planlama/d158/Y0f-gunluk.md`, `planlama/d158/Y0f-kontrol.md`
- **Commit 2, web demosu (4):** `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/demo_uret.py`, `viewer-template.html`, yeni
  `tasarim/cad/omni-teker.json`.
- **Girmeyecek:**
  - 21 eski dosya: 13 `kabuk/gorsel/*.png`, `montaj/yerlesim-kontrol.json`, `geometri*_*.py` (3), `gez.js`, `uc.js`, `P108d*`
    (2).
  - `__pycache__/`.

### 14.9 Bakılmayanlar

- Demoda parça tıklama (bilgi kutusu ve omni notu) ve `?teker=lastik` konsolu (F9b yalnız varsayılanı denetliyor).
- Kaplinin göbeğe girme ölçüsü.
- Makara çapı (Ø15 / 23) ve kapsül eşik taraması; titreşim ve hız tablosu (RTF) yeniden üretilmedi.
- 9 kg·cm 15° rampa kilitleri.
- `omni-makara.json` yeniden üretimi (≈ 6,5 dk).
- Gerçek teker, karta yükleme.
