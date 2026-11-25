# Uçurum sensörü: sonuç ve hüküm

Ne ölçüldü: aşağı inen merdiven, dik boşluk, kuyu, sahanlık köşesi ve robottan dar aşağı inen açıklıkta robotun zamanında durup durmadığı; aşağı bakan
VL53L1X türü sensörün sayısı, yeri, eğimi ve eşiği; ESP32 durdurma mantığı; ani frende devrilme; sensör kusurları;
LiDAR'ın merdiveni görüp görmediği. Hepsi MuJoCo modelinde, varyant ONERI (öneri firmware + ön omni; bugünkü robot
V0 değil). Bütün tablolar `analiz.py` ile CSV'lerden üretilir (`tablolar.md`); bu dosya özet ve hükümdür.

## Hüküm

**Önerilen düzen (dar açıklık düzeltmesinden sonra), sınamadan geçti:** altı sensör: dört köşe (eğim düzlemi çapraz
dışa) + önde iki iç sensör (düz öne). İlk hükümdeki dört köşe düzeni (`2KD+2AD`) **robottan dar açıklıkta düşüyor**;
bağımsız denetimin bulgusu doğrulandı (aşağıda, "Dar açıklık").

| | Değer (robot çerçevesi: gövde merkezi, +x ileri, +y sol) |
| --- | --- |
| Sensör | **6 adet** VL53L1X türü (koni 27°), 50 Hz (`4OD+2AD`) |
| Yer | köşeler: ön sol (+255, +250) mm, ön sağ (+255, −250), arka sol (−255, +250), arka sağ (−255, −250); **ön iç: (+255, +85) ve (+255, −85)**; hepsi yerden 120 mm (köşelerde etek penceresi) |
| Eğim | dikeyden 30°. Köşeler: önde yön ±45° (öne-dışa), arkada ±135° (geriye-dışa), zemin izi köşeden ≈ 49 mm ileri + 49 mm dışarı. Ön iç sensörler: düz öne (yön 0), zemin izi (+324, ±85) mm. Ön izler ön teker temas noktasının ≈ 120–140 mm önünde |
| Eşik | açılışta ölçülen zemin mesafesinden (≈ 139 mm) **+100 mm** fazlası, **art arda 3 örnek** (sensör başına) |
| Dönüşsüz örnek | `yavasla`: 0,5 s hız sınırı 0,10 m/s; art arda 5 dönüşsüz örnek = dur (bkz. Sensör kusurları) |
| Döngü | ESP32 100 Hz (10 ms; tetik → motor komutu aynı dilimde) |
| Fren | etkin fren: teker hedefi 2,0 m/s² rampayla 0'a, PI izler, sonra kısa devre freni. Yalnız motor kesme YETMEZ |
| Güvenli en yüksek hız | 0,39 m/s (ölçülen tavan); sınama 2'de en küçük pay 3,0 cm (dar açıklık), geniş kenarda 4,2 cm |

**Sınama 2** (`sinama2.csv`; seçim `dar_gelistirme`'den, sınama koşulmadan önce yapıldı; tohum 101–110, politika `yavasla`
baştan): ilk sınamanın bütün ızgarası (15x28 ve 19x25 cm merdiven, kuyu, sahanlık köşesi; açılar 10 / 22 / 37 / 52 / 68 /
85°; geri, yerinde dönüş, yay) + geliştirmede hiç koşulmamış **8 dar açıklık sahnesi** (0,45 / 0,55 / 0,65 / 0,75 / 0,90 m
genişlik, 0,6 m genişlikte 0,4 m sığ açıklık, 0,6 ve 0,8 m genişlikte dar merdiven; yeni yanal kaymalar −0,15 … +0,25 m;
açı 0 / 10 / 30°) + **5 yeni yanlış alarm sahnesi**: **2900 uçurum koşusunda 0 düşme**, 540 yanlış alarm koşusunda 0
yanlış durma, toplam 3440 koşu, 0 hata. En küçük pay: dar açıklıkta 3,0 cm (0,39 m/s; sığ açıklık ve 0,6 m dar merdiven,
yanal −0,15 m), geniş kenarda ileri 4,2 cm (köşe, 37°) / düz kenar 4,5 cm, geri 6,8 cm, yerinde dönüş 4,4 cm, yay 8,5 cm.

İlk sınama (`sinama.csv` + `sinama_y.csv`, 2210 koşu, eski 4 sensörlü seçim) geniş kenarlarda 0 düşme verdi; o sonuç yerinde
duruyor ama dar açıklığı kapsamadığı için hükmü taşımıyor.

Sadece ileri giden ve **geri gitmesi firmware'de yasak** bir robot için arka iki sensör çıkarılabilir (`4OD`, dört ön
sensör); geri giderken arka sensörsüz her koşu düştü (geliştirmede 144 / 144).

**Dar açıklık (bağımsız denetimin engelleyici bulgusu; `dar_gelistirme.csv`, `sinama2*.csv`).** Bulgu doğru: köşe
sensörlerinin zemin izi y ≈ ±0,30 m'de, teker merkezleri ±0,216 m'de. Robot dar bir açıklığa ortadan girerse iki köşe izi
de açıklığın yan zeminine ya da yan duvarına düşer (çapraz dışa bakan ışın yan duvarı yakın görür, okuma eşiği aşmaz),
teker boşluğa iner. Geliştirmede (tohum 1–2, 6 genişlik 0,40–1,00 m, 3 m derin, 5 yanal kayma, açı 0 / 20 / 40°, üç hız;
aday başına 540 koşu):

| aday | 0,40 m | 0,50 | 0,60 | 0,70 | 0,80 | 1,00 | toplam düştü | en küçük pay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2KD+2AD` (ilk seçim, 4 sensör) | 21 / 90 | 19 / 90 | 6 / 90 | 3 / 90 | 0 / 90 | 0 / 90 | **49 / 540** | −13,2 cm |
| `3KOD+2AD` (+ ön orta, 5 sensör) | 2 / 90 | 0 | 0 | 0 | 0 | 0 | **2 / 540** | −2,7 cm |
| `4OD+2AD` (+ ön iç ±85 mm, 6 sensör) | 0 / 90 | 0 | 0 | 0 | 0 | 0 | **0 / 540** | +1,6 cm |

`3KOD+2AD`'nin iki düşmesi 0,40 m açıklık, 0,39 m/s, 20°, yanal −0,20 m (iki tohum da): orta iz açıklığın kenarına düşer,
geç tetikler. Seçim kuralı (her geliştirme senaryosunda 0 düşme, sonra en büyük en küçük pay) `4OD+2AD`'yi seçer. Ek iki
sensör geniş kenar ve yanlış alarm sonucunu bozmuyor (geliştirme sahneleri, `yavasla`): ileri 0 / 36 (pay 5,7 cm; eski 3,4),
geri 0 / 6 (7,0), yerinde dönüş 0 / 16 (5,2), yay 0 / 2 (6,5), yanlış durma 0 / 84. Ön iç sensörlerden biri ölüyse (donmuş
ya da hep dönüşsüz) denetçi onu fark edip durduruyor (16 / 16 koşu tetik, 0 düşme).

Sınamada seçilmeyen iki aday da aynı dar açıklık ızgarasında koşuldu (`sinama2_karsi.csv`, yalnız rapor, seçime girmedi):
bkz. 7. bölüm.

**Sınırlar (önemli):** (1) Sınanan en dar açıklık 0,40 m (geliştirme) / 0,45 m (sınama). Ön izler arası boşluk (iç iz
±0,085 m ile köşe izi ±0,30 m arası) ≈ 0,21 m: bu aralıkta, teker hizasında duran ≈ 0,2 m'den dar bir delik (ızgara,
kapak boşluğu) geometrik olarak hiçbir izin altına girmeyebilir; sınanmadı. (2) Açıklıklar 2 m boyunda dikdörtgen; yuvarlak
ya da eğik kenarlı açıklık, basamak burnu, korkuluk dikmesi yok.

**Öbür sınırlar:** eşik 100 mm, 30° eğik ışında ≈ 87 mm'den sığ düşüşü görmez (tek basamaklı kaldırım 5–8 cm
yakalanmaz). Daha düşük eşik 10° iniş rampasına çapraz girişte robotu durduruyor (aşağıda). Kısa devre freni sıfır
hızda tork vermediği için **10° inişte robot tam durmuyor: frenden sonra ≈ 0,10 m/s ile kaymaya devam ediyor** (modelde
her fren kipinde; `durma.csv`'de inişte hiçbir koşu 0,005 m/s altına inmedi); rampa dibinde uçurum varsa bu düzen
yetmez, tutma freni gerekir.

**Bağımsız denetimin "sınanmamış geometri" bulgusu kapandı:** dar açıklık sahnesi (`sahne.acik`, hakemde dikdörtgen delik
payı) eklendi, adaylar geliştirme tohumlarıyla karşılaştırıldı, seçim değişti (`2KD+2AD` → `4OD+2AD`) ve sınama yeni
tohum / sahnelerle yeniden koşuldu (yukarıda). Denetçinin kısa denemesi (0,45–0,70 m'de `2KD+2AD` düşer, ön ortalı düzen
durur) bu ızgarada yinelendi.

## 1. Durma mesafesi (düz zemin, tetik zorla verildi; `durma.csv`, iki tohum, deterministik)

| fren | 0,10 m/s | 0,25 m/s | 0,39 m/s | 0,39'da tepe yavaşlama | 0,39'da arka aks en az |
| --- | --- | --- | --- | --- | --- |
| motor kesme (EN LOW, boşta) | 1,4 cm | 9,2 cm | 22,3 cm (1,13 s) | 0,35 m/s² | 123 N |
| kısa devre freni (EN HIGH, PWM 0) | 0,5 | 1,7 | 3,3 | 3,0 | 0 N (60 ms) |
| rampa 1,0 m/s² | 0,7 | 3,3 | 7,7 | 1,3 | 88 N |
| rampa 1,5 | 0,6 | 2,4 | 5,3 | 1,8 | 68 N |
| rampa 2,0 | 0,6 | 2,0 | 4,2 | 2,3 | 46 N |
| rampa 2,5 – 5,0 | 0,5 | 1,8 | 3,6 – 3,8 | 2,8 – 3,2 | 0 N (10–70 ms) |

Durma yolu tetikten itibaren; tetikten önce sensör gecikmesi (20 ms + 3 örnek) eklenir. Statik arka aks yükü 136 N.

**Model varsayımı:** motor modeli `tau = tau_durma · (u · k_V − w / w0)` (dunya.py); kesme = tork 0 (yalnız dişli ve
yuvarlanma sürtünmesi), kısa devre freni = `−tau_durma · w / w0`, rampa = öneri firmware PI'ı (KP 4, KI 20, TAHMİN)
teker hedefini rampayla 0'a indirir. Motor durma torku 21 kg·cm ve sürtünmeler TAHMİN.

## 2. Devrilme (görev 5)

Kütle merkezi modelden (`kutle_merkezi.json`): kütle 26,3 kg, x = −10 mm (gövde merkezinin 1 cm arkası), yerden
**520 mm**. Rijit gövde, kaymayan teker için öne devrilme (arka aks yükü 0) yavaşlaması:
**düz zeminde 3,68 m/s², 10° inişte 1,93 m/s².**

Ölçülen: hiçbir fren kipinde tekerlek kalkması yok (≤ 0,07 mm, temas sızması mertebesinde), öne yatma tepe ≤ 0,011°.
Düz zeminde rampa ≤ 2,0 m/s²'de arka aks hep ≥ 46 N (`durma.csv` 46,5); ≥ 2,5 m/s² ve kısa devre freninde 10–70 ms 0 N (tepe yavaşlama
2,8–3,2 m/s², el hesabı sınırının %80'i; kısa vuru, temas sertliği). 10° inişte arka aks yükü frenden önce 71 N
(en az 64 N) ve motor kesme dışındaki her fren kipinde 0,25–0,39 m/s'de 20–160 ms 0 N'a iniyor (0,10 m/s'de 0–20 ms),
ama gövde yatmıyor.

**Güvenli en büyük yavaşlama: düz zeminde 2,0 m/s²** (arka aks ≥ 46 N, el hesabı sınırının yarısı); 10° inişte el hesabı
sınırı 1,93 m/s², yani 2,0 m/s² rampası (ölçülen tepe 2,3) inişte sınırda. Firmware'de eğim bilgisi (IMU) yok; öneri:
rampa kipinde (firmware'in mevcut `rampa` ivme kipi) uçurum freni 1,5 m/s² ve hız ≤ 0,25 m/s (el hesabından). Ölçüm
bu öneriyi DESTEKLEMİYOR: `durma.csv`'de 10° inişte 1,5 m/s² rampasında arka aks 0,25 m/s'de 70 ms, 0,39'da 110 ms
0 N'a iniyor; 1,0 m/s²'de bile 0,25'te 40 ms, 0,39'da 90 ms. Gövde yatmıyor, ama inişte güvenli fren ivmesi ölçülerek
belirlenmedi.

10° iniş rampasında frenden 0,6 s sonra robot 0,10 m/s ile kaymaya devam ediyor (motor kesmede 0,75–0,88 m/s'ye
hızlanıyor). Kısa devre freni sıfır hızda tutmaz (bilinen bulgu, `kod/SIMULASYON.md`). Rampa üstünde uçurum durdurması
ancak tutma freniyle (sıfır hızda PI tutuşu, sonsuz vida, mekanik fren) çalışır.

## 3. Yanlış alarm ve eşik (görev 1; `denetim*.csv`, gölge denetçiler)

Gölge denetçi aynı okumaları görür, robotu durdurmaz: bir koşuda 18 eşik x onay çifti birlikte ölçülür.

| eşik / onay | düz | 20 mm eşik | derz | koyu şerit | 10° iniş rampası | halı 10 mm | halı 5 mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 15 mm / 2 | 0 / 144 | 72 / 144 | 0 / 144 | 56 / 144 | 138 / 144 | 47 / 144 | 0 / 144 |
| 30 mm / 2 | 0 | 41 | 0 | 53 | 84 | 0 | 0 |
| 40 mm / 2 (geliştirme 1) | 0 | 1 | 0 | 53 | 72 | 0 | 0 |
| 40 mm / 3 | 0 | 0 | 0 | 0 | 72 | 0 | 0 |
| 80 mm / 3 | 0 | 0 | 0 | 0 | 9 | 0 | 0 |

(2K ve 3KO, z 60 / 120 mm, eğim 0 / 15 / 30°, üç hız, açı 0 / 30°, tohum 1–2.)

- 20 mm eşik çıkışı: 30 mm altı eşikte her koşuda durur. Koyu şerit: onay 2'de dönüşsüz örneklerden durur, onay 3'te durmaz.
- 10° iniş rampası belirleyici: kafa kafaya girişte 40 mm eşikte bile durmaz, ama **çapraz girişte** (30–45°) tek köşe
  tekeri rampaya inmeden köşe sensörü rampa yüzeyinin 30 cm içine bakar ve mesafe 6 cm'ye kadar artar
  (`rampa_ayrinti`). Giriş açısı x eşik (onay 3): 60 mm'de 45° girişte 24 / 24, 80 mm'de 8 / 24, **100 mm'de 0 / 120**.
- Çapraz köşe yerleşiminde (`denetim2`, 2KD, z 60 / 120, eğim 15 / 30°): **100 mm / onay 3'te yedi sahnede 0 / 168.**

## 4. Yerleşim (görev 2, 4; geliştirme: `gelistirme*.csv`, tohum 1–2, `merdiven_17x30` ve `bosluk_3m`)

Geliştirme 1 (2928 koşu, 40 mm / onay 2, fren rampa 2,0 ve kısa devre): ileri yaklaşmada

| düzen | düştü (z 60 + 120, rampa 2,0) | en küçük pay cm |
| --- | --- | --- |
| 2K / 3KO / 4O, eğim 30° | 0 / 72 her biri | 3,2 – 3,3 |
| 2K / 3KO / 4O, eğim 15° | 0 / 72 | 1,8 – 2,6 |
| 2K / 3KO / 4O, eğim 0° (dik) | 4 – 8 / 72 | −0,8 |
| 2I (iç, y ±120), her eğim | 32 – 60 / 72 | −6 … −8 |

- **Orta / iç sensör bu sahnelerde katkı vermiyor:** 3KO ve 4O'nun düşme sayıları ve en küçük payları 2K ile aynı
  (540 eşleşik ileri koşunun 20'sinde, hepsi dik e0 / z 60, pay ±0,8 cm farklı; 84 koşuda ilk tetik orta / iç
  sensörden). Çapraz gelişte kenarı önce köşe tekeri geçer; iç sensörler onu korumaz (2I düşer). **Bu yalnız robottan
  geniş kenarlar için doğru:** robottan dar açıklıkta köşe sensörleri yetmiyor, ön iç sensörler gerekiyor (`dar_gelistirme`,
  Hüküm "Dar açıklık"; seçim bu yüzden `4OD+2AD` oldu). Çapraz köşelerle birlikte düz öne bakan iç sensörlerin izi köşe
  izinden 2 cm ileride olduğu için geniş kenarda da kafa kafaya payı artırıyor (0,39 m/s'de 3,4 → 4,5 cm, sınama 2).
- Dik bakan sensör 0,39 m/s'de geç kalır (iz tekerin yalnız 70 mm önünde, durma 42 mm + gecikme). 30° eğim izi 35–69 mm öne
  alır.
- Geri giderken: arka sensörsüz 144 / 144 düştü; +2A ile 0 düşme (en küçük pay 2,2–6,8 cm).
- Kenarda yerinde dönüş (dönme merkezi kenardan 0,3–0,6 m, ±1 rad/s; köşe 0,46 m/s ile süpürür): ileri bakan köşe
  sensörleriyle pay 0,5 cm, 100 mm eşikte 16 koşudan 1–4 düşme. **Çapraz dışa (yön ±45°) köşelerle 0 düşme, pay 5,2 cm**
  (z 120, eğim 30°, 100 mm / 3). Seçimin nedeni bu.

Geliştirme 2 (960 koşu, ön + arka köşe, düz / çapraz, z 60 / 120, eğim 15 / 30°, eşik 40 / 2 ve 100 / 3):

| yerleşim, eşik | ileri | geri | yerinde dönüş | dönüşlü yörünge |
| --- | --- | --- | --- | --- |
| **2KD+2AD z120 e30, 100 mm / 3 (seçilen)** | 0 / 36, pay 3,4 | 0 / 6, 7,2 | 0 / 16, 5,2 | 0 / 2, 6,5 |
| 2KD+2AD z120 e30, 40 / 2 | 0 / 36, 4,2 | 0 / 6, 7,7 | 0 / 16, 5,7 | 0 / 2, 7,0 |
| 2K+2A z120 e30, 100 / 3 | 0 / 36, 3,1 | 0 / 6, 6,5 | **1 / 16**, −0,0 | 0 / 2, 7,6 |
| 2KD+2AD z60 e30, 100 / 3 | 0 / 36, 1,8 | 0 / 6, 5,2 | 0 / 16, 1,6 | 0 / 2, 4,4 |
| 2K+2A z60 e15, 100 / 3 | 0 / 36, 1,1 | 0 / 6, 4,2 | **3 / 16**, −0,2 | 0 / 2, 3,4 |

Seçim kuralı: her geliştirme senaryosunda 0 düşme ve en büyük en küçük pay, yanlış alarmda 0 (100 mm / 3). 40 mm eşik
payı 0,8 cm artırıyor ama rampaya çapraz girişte durduruyor. Geliştirme 2'nin seçimi (`2KD+2AD`) dar açıklık
geliştirmesinde (`dar_gelistirme`, Hüküm) aynı kuralla `4OD+2AD`'ye değişti; köşe yerleşimi, yükseklik, eğim, eşik
değişmedi.

## 5. Sensör kusurları (görev 6; `kusur.csv`, ilk seçim `2KD+2AD`, geliştirme sahneleri ve tohumları 1–3)

Yeni seçimin ek ön iç sensörleri için yalnız ölü sensör denetimi koşuldu (`dar_gelistirme`, alt `kusur`: 0,50 / 0,70 m
açıklık, donmuş / hep dönüşsüz, 16 koşu): her koşuda denetçi arızayı fark edip durdu, 0 düşme. Zemini parlak yüzey (dönüşsüz oran)
taraması yeni düzenle yinelenmedi; sensör sayısı 4'ten 6'ya çıktığı için %5 dönüşsüzde yanlış durma olasılığı artar
(`yavasla` ile sınama 2'nin 540 yanlış alarm koşusunda, koyu yüzeyli iki sahne dahil, 0).

Ön sensörlerden biri ölü (donmuş değer ya da hep menzil dışı), uçuruma 0 / 30 / 60°, 0,25 / 0,39 m/s:

| politika | arızasız | donmuş değer | hep menzil dışı |
| --- | --- | --- | --- |
| `ucurum` (veri yok = uçurum) | 0 / 36 düştü | 0 / 72 (donma 0,5 s'de fark edilip durur) | 0 / 72 (açılışta durur) |
| `yavasla` | 0 / 36 | 0 / 72 | 0 / 72 |
| `yok_say` (veri yoksa atla) | **18 / 36** | **48 / 72** | **48 / 72** |

`yok_say` arızasızken bile 3 m boşlukta düşüyor: o derinlikte ışın menzil dışına çıkar, ölçüm "dönüş yok" olur.
Dönüşsüz örneği yok saymak güvensiz.

Zemini parlak yüzey (her örnek bu olasılıkla dönüşsüz), uçurum koşusu / düz zeminde 4 m yol:

| politika | dönüşsüz | uçurumda düştü | düz zeminde yanlış durma |
| --- | --- | --- | --- |
| `ucurum` | %5 | 0 / 36 | 6 / 18 |
| `ucurum` | %20, %50 | 0 / 36 | 18 / 18 |
| `yavasla` | %5 | 0 / 36 | **0 / 18** |
| `yavasla` | %20, %50 | 0 / 36 | 18 / 18 (yavaş gider, sonra durur) |
| `yok_say` | her oran | 18 / 36 | 0 / 18 |

**Seçilen politika `yavasla`:** kaçırma 0, %5 dönüşsüzde yanlış durma yok. %20 ve üstü dönüşsüz zeminde her politika ya
durur ya düşer: o zeminde robot sürülmemeli (masada ölçülmeli).

## 6. LiDAR merdiveni görüyor mu (görev 7; `lidar_denetim.json`)

Görmüyor. Robot merdiven kenarına 0,295 m'de, öne bakarken ±60° sektördeki 167 ışının hepsi 4,29 m'deki duvarı
ölçüyor; merdivenli ve merdivensiz sahnede en büyük fark **0,0 mm** (LiDAR düzlemi 0° ve 1,5° öne yatık). Yatay tarama
düzlemi (z 0,295) zeminin altına inen hiçbir şeyi kesmez.

## 7. Sınama (görev 8; ilk sınama `sinama.csv`, `sinama_y.csv`; sınama 2 `sinama2.csv`, `sinama2_karsi.csv`)

### 7a. İlk sınama (eski seçim; dar açıklığı kapsamaz)

İlk seçim (`deney.SECIM_1`: 2KD+2AD, z 120 mm, eğim 30°, 100 mm / 3, fren rampa 2,0), yeni tohumlar ve geometriler.

İleri yaklaşma, en küçük pay cm (düşme / koşu), politika `ucurum` tohum 101–110 | `yavasla` tohum 101–105:

| geometri | 0,10 m/s | 0,25 m/s | 0,39 m/s |
| --- | --- | --- | --- |
| merdiven 15 x 28 | 7,6 (0 / 80) · 7,6 (0 / 40) | 6,8 (0 / 80) · 6,9 (0 / 40) | 3,4 (0 / 80) · 3,8 (0 / 40) |
| merdiven 19 x 25 | 7,6 · 7,6 | 6,8 · 6,9 | 3,4 · 3,8 |
| kuyu (menzil dışı) | 7,6 · 7,6 | 6,8 · 7,5 | 3,4 · 5,1 |
| sahanlık köşesi (iki kenar, eğik gelen) | 4,2 · 4,2 | 4,2 · 4,2 | 3,4 · 4,2 |

En kötü açı 0° (kafa kafaya, en hızlı yaklaşma) ya da köşede 37°. Politika `ucurum` ile ayrıca: geri giderken 60 koşu
(15x28 ve 19x25 merdiven, 0 / 25 / 50°, 0,10 / 0,25 m/s) 0 düşme, pay ≥ 6,8 cm; kenarda yerinde dönüş 60 koşu 0 düşme,
pay ≥ 4,4 cm (3 koşuda dönüş kenara ulaşmadı, tetik yok); eğik gelen dönüşlü yörünge 20 koşu 0 düşme, pay ≥ 8,4 cm.

Yanlış durma (yedi denetim sahnesi x 3 hız x açı 0 / 20 / 40° x 5 tohum = 315 koşu):

| politika | düz | 20 mm eşik | derz | koyu şerit | 10° iniş rampası | halı 10 mm | halı 5 mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ucurum` | 0 / 45 | 0 / 45 | 0 / 45 | **4 / 45** (dönüşsüz) | 0 / 45 | 0 / 45 | 0 / 45 |
| `yavasla` (seçilen) | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 | 0 / 45 |

İlk sınamanın sonucu: eski düzen bu 2210 koşunun hiçbirinde düşmedi; `yavasla` ile yanlış durma yok. 0,39 m/s'de en küçük
pay 3,4 cm (`ucurum`) / 3,8 cm (`yavasla`). Dar açıklığı kapsamadığı için hüküm 7b'ye dayanır.

### 7b. Sınama 2 (seçilen `4OD+2AD`, politika `yavasla`; 3440 koşu)

Geniş kenar ileri yaklaşma, en küçük pay cm (düşme / koşu; tohum 101–110, açılar 7a ile aynı):

| geometri | 0,10 m/s | 0,25 m/s | 0,39 m/s |
| --- | --- | --- | --- |
| merdiven 15 x 28 | 7,6 (0 / 80) | 7,5 (0 / 80) | 4,5 (0 / 80) |
| merdiven 19 x 25 | 7,6 (0 / 80) | 7,5 (0 / 80) | 4,5 (0 / 80) |
| kuyu (menzil dışı) | 7,6 (0 / 80) | 7,5 (0 / 80) | 5,8 (0 / 80) |
| sahanlık köşesi | 4,2 (0 / 80) | 4,2 (0 / 80) | 4,2 (0 / 80) |

Geri 60 koşu 0 düşme, pay ≥ 6,8 cm; yerinde dönüş 60 koşu 0 düşme, pay ≥ 4,4 cm (3 koşuda dönüş kenara ulaşmadı); yay 20
koşu 0 düşme, pay ≥ 8,5 cm. Yanlış durma: yedi eski denetim sahnesinde 0 / 315, beş yeni sahnede 0 / 225 (25 mm eşik,
geniş derz, 30 cm koyu bant, 8° iniş rampası, 15 mm halı; her biri 0 / 45).

Dar açıklık (tohum 101–105; 3 açı x 5 yanal kayma x 3 hız x 5 tohum = sahne başına 225 koşu), düşme / koşu (en küçük pay cm):

| yerleşim | 0,45 m | 0,55 | 0,65 | 0,75 | 0,90 | 0,60 sığ (0,4 m) | dar merdiven 0,60 | dar merdiven 0,80 | toplam |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`4OD+2AD` (seçilen)** | 0 (4,3) | 0 (4,3) | 0 (4,3) | 0 (4,8) | 0 (5,0) | 0 (3,0) | 0 (3,0) | 0 (4,5) | **0 / 1800**, pay ≥ 3,0 |
| `3KOD+2AD` (karşılaştırma) | 0 (2,5) | 0 (2,5) | 0 (3,1) | 0 (3,6) | 0 (5,2) | 0 (1,2) | 0 (1,2) | 0 (4,5) | 0 / 1800, pay ≥ 1,2 |
| `2KD+2AD` (ilk seçim) | **65** | **46** | **17** | **3** | 0 (3,4) | **30** | **30** | 0 (2,1) | **191 / 1800**, pay −13,2 |

Seçilen düzenin dar açıklıkta en küçük payı yanal kaymaya göre (0,10 / 0,25 / 0,39 m/s): −0,15 m'de 8,0 / 5,7 / 3,0;
−0,05'te 8,0 / 6,6 / 4,3; 0,05'te 9,9 / 7,8 / 4,5; 0,15'te 6,4 / 5,4 / 4,5; 0,25'te 6,0 / 6,2 / 4,5 cm. 94 / 1800 koşu
açıklığa hiç girmeden yanından geçti (hepsi 30° açı, yanal ≥ 0,05; tetik yok, pay ≥ 5,1 cm): bunlar düşme sayılmadı ama
"durdu" da sayılmadı.

`2KD+2AD`'nin düşmeleri en çok kafa kafaya ya da 10°, orta hattan ±0,15 m içinde; 0,90 m ve 0,80 m dar merdivende
düşmedi. Ön ortalı `3KOD+2AD` sınamada da düşmedi (pay ≥ 1,2 cm), ama geliştirmede 0,40 m açıklıkta 2 / 540 düştüğü için
seçilmedi; sensörden tasarruf gerekiyorsa beşli düzen ikinci seçenektir (en dar açıklık ≈ 0,45 m kabulüyle).

**Hüküm sınamadan:** seçilen altı sensörlü düzen sınama 2'nin 2900 uçurum koşusunun hiçbirinde düşmedi, 540 yanlış alarm
koşusunda hiç durmadı. 0,39 m/s'de en küçük pay 3,0 cm (dar açıklık) / 4,2 cm (geniş kenar): küçük ama sıfırdan uzak;
sensör gecikmesi (uzun kip) ya da fren modelindeki 3 cm'lik bir hata bunu yer. Gerçek robotta ilk deneyde hız 0,25 m/s
(pay ≥ 4,2 cm) önerilir.

## Geliştirme / sınama ayrımı

| | Geliştirme (ayar) | Sınama (hüküm) |
| --- | --- | --- |
| Tohum | 1, 2, 3 | 101–110 |
| Uçurum geometrisi | `merdiven_17x30` (17 x 30 cm, 8 basamak), `bosluk_3m` | `merdiven_15x28`, `merdiven_19x25`, `kuyu` (menzil dışı), `kose` (iki kenarlı sahanlık köşesi, eğik gelen kenar) |
| Açılar | 0, 15, 30, 45, 60, 80 | 0, 10, 22, 37, 52, 68, 80, 85 |
| Yanlış alarm | tohum 1–2, açı 0 / 30 | tohum 101–105, açı 0 / 20 / 40 |
| Dar açıklık (`dar_gelistirme` / `sinama2`) | genişlik 0,40 / 0,50 / 0,60 / 0,70 / 0,80 / 1,00 m, 3 m derin; yanal −0,20 … +0,20 (0,10 adım); açı 0 / 20 / 40; tohum 1–2 | genişlik 0,45 / 0,55 / 0,65 / 0,75 / 0,90 m, 0,60 m x 0,4 m sığ, 0,60 ve 0,80 m dar merdiven (18 x 27 cm); yanal −0,15 / −0,05 / 0,05 / 0,15 / 0,25; açı 0 / 10 / 30; tohum 101–105 |
| Yanlış alarm, yeni sahne (yalnız `sinama2`) | - | 25 mm eşik, geniş derz (12 x 8 mm, 0,45 m aralık), 30 cm koyu bant, 8° iniş rampası, 15 mm halı |

Bağımsızlığın sınırı: `merdiven_15x28`, `merdiven_19x25` ve `kuyu` aynı x = 16 m düz kenarı taşır; `ucurum`
politikasıyla 240 eşleşik (açı, hız, tohum) koşunun 238'inde üçü aynı payı verir. Yani bunlar pratikte tek yeni
geometri sayılır; gerçekten yeni olan `kose` ve açılardır. İlk sınamanın yanlış alarm bölümü geliştirmedeki yedi denetim
sahnesini yeni tohum ve açılarla yineler; sınama 2 buna beş yeni sahne ekler (225 koşu, 0 yanlış durma). Dar açıklık
sınaması genişlik, derinlik, merdiven ve yanal kayma bakımından geliştirmeden ayrıdır, ama aynı sahne türüdür
(dikdörtgen delik, x = 16 m'de yakın kenar).

Dar açıklık seçimi: `dar_gelistirme` (tohum 1–2) bitti, `secim.json` `4OD+2AD`'ye yazıldı, sonra `sinama2` koşuldu. Politika
`yavasla` sınama 2'den önce seçilmişti (kusur aşaması), bu yüzden sınama 2'de geri / dönüş / yay da `yavasla` ile koşuldu
(ilk sınamada `sinama_y` bunları kapsamıyordu).

Eşik, onay, yerleşim, eğim, yükseklik ve politika yalnız geliştirme ve denetim koşularından seçildi (`secim.json`).
Sınamadan sonra eşik / yerleşim / fren değiştirilmedi. Sınama, süre için kusur aşamasıyla aynı anda koşuldu; politika o
an `ucurum` idi. Kusur aşaması (geliştirme tohumları) `yavasla`'yı daha iyi bulunca sınama yalnız politika değişik olarak
yeniden koşuldu (`sinama_y`); iki sonuç da raporlandı.

## Simülasyonun iyimser varsayımları

- Sensör modeli VARSAYIM: 17 ışınlı koni, "ağırlığın ≥ %25'ini taşıyan en yakın öbek" kuralı, gürültü σ 2,5 mm + %0,2,
  koyu yüzeyde σ x 2 ve %5 dönüşsüz. Gerçek VL53L1X histogram işlemi, ortam ışığı, eğik gelişte sinyal kaybı, cam / ayna /
  parlak siyah zemin, toz, sensörler arası çapraz konuşma modellenmedi. Masada doğrulanmalı.
- Sahne kusursuz: keskin basamak burnu, düz zemin; halı kaplı basamak, yuvarlak burun, ıslak zemin yok.
- Firmware zamanlaması kusursuz (10 ms dilim, I2C gecikmesi yok, bir örnek gecikme). 50 Hz denetçi döngüsü ölçülmedi
  (ek ≤ 10 ms, 0,39 m/s'de ≤ 0,4 cm).
- 50 Hz örnek ile 4 m menzil birlikte varsayıldı. VL53L1X'te 20 ms zamanlama bütçesi yalnız kısa mesafe kipinde
  (≈ 1,3 m) var; uzun kip en az ≈ 33 ms ister. Kısa kipte 3 m boşluk dönüşsüz okunur (`kuyu` sınaması bu durumu kapsar);
  uzun kipte tetik ≈ 50 ms gecikir, 0,39 m/s'de pay ≈ 2 cm azalır (3,4 → ≈ 1,4 cm; ölçülmedi). Kip masada seçilmeli.
- Robot gövdesi ışını kesmiyor: seçilen z 120 mm / 30° çapraz yerleşimde ışın etek köşesinin içinden çıkar (BENIOKU);
  etek penceresi ve onun koniyi kırpması modellenmedi.
- Teker rijit, sürtünme ve motor değerleri TAHMİN; robot hep düz zeminde kalibre edildi.
- Altı sensör aynı I2C hattında 50 Hz'de, gecikmesiz ve birbirini etkilemeden okunuyor varsayıldı (adres için sensör başına
  XSHUT ucu gerekir; çapraz konuşma modellenmedi). Ön iç sensörler köşelerle aynı yükseklikte (120 mm) etek içinden
  bakıyor; etek ön yüzünde pencere gerekir.
- Dar açıklık sahnesinde kenarlar keskin, yan duvar dik ve düz; gerçek merdiven boşluğunda korkuluk, süpürgelik, halı kenarı
  olabilir.
- Hakem teker merkezlerinin (temas noktası) kenara yatay payını ölçer; teker yarıçapı 62,5 mm olduğundan pay 0'ın biraz
  altı hemen devrilme değildir ama düşme sayıldı (kötümser).

## Izgaradan atılanlar (süre: ≈ 2,5 saat)

- Denetim: yalnız 2K ve 3KO (yanlış alarm y konumuna değil yükseklik / eğime bağlı), tohum 1–2, açı 0 / 30, yol 1,8 m.
- Geliştirme 1: tohum 1–2 (3 değil); kısa devre freni yalnız z 60, tohum 1; geri / dönüş / yay yalnız `merdiven_17x30`.
- Geliştirme 2: tohum 1 (yerinde dönüş 1–2); denetim2 tohum 1.
- Kusur: yalnız ön sensör arızası; 0 / 30 / 60°, 0,25 / 0,39 m/s.
- Sınama: geri / dönüş / yay ve yanlış alarm tohum 101–105; `sinama_y` yalnız ileri ve yanlış alarm, tohum 101–105.
- Dar açıklık: geliştirme tohum 1–2, sınama tohum 101–105 (sınama 2'nin geniş kenar bölümü 101–110); açıklık boyu hep 2 m;
  0,40 m'den dar açıklık yok; açıklığa geri giderek ya da yerinde dönerek yaklaşma yok (yalnız ileri); yalnız z 120 / e 30
  yerleşimi; seçilmeyen adaylar sınamada yalnız dar açıklıkta (`sinama2_karsi`).
- Yeni seçimle (`4OD+2AD`) kusur aşaması (parlak zemin, köşe sensörü arızası) ve durma / devrilme yeniden koşulmadı
  (durma ve devrilme sensörden bağımsız; köşe arızası denetçide sensör başına aynı mantık).
- Sensör konisi yalnız 27° (15° ROI denenmedi); yükseklik yalnız 60 / 120 mm; tek kat merdiven ve boşluk derinliği.

## Sayılar

Koşu: durma 132, denetim 1008, rampa_ayrinti 120, denetim2 168, geliştirme 2928 + 960, kusur 1188, sınama 1415,
sinama_y 795; dar açıklık düzeltmesi: dar_gelistirme 2100, sinama2 3440, sinama2_karsi 3600. Hata (istisna) 0. Bütün
düşmeler CSV'de durur (`dustu`, `dustu_neden`, `pay_min_cm`; dar açıklıkta `yanal` sütunu orta hattan kaymayı verir).

Görseller: `../gorsel/durma_yolu.png`, `../gorsel/yerlesim_pay.png`, `../gorsel/sinama_pay.png` (ilk sınama, eski düzen),
`../gorsel/dar_aciklik.png` (dar açıklıkta üç aday, geliştirme ve sınama), `../gorsel/demo_pencere.png` (3B gösterim: robot
0,25 m/s merdivene yürür, sol ön sensör tetikler, durur; eski düzenle çekildi). Dar açıklık 3B'de: `kod\ucurum.bat acik_55`
(seçim `secim.json`'dan, altı sensör; bu düzeltmede pencere açılarak denenmedi).
