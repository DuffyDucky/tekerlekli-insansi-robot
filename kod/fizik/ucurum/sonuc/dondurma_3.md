# Dondurma 3: iki aday (3A donanım, 3B pratik), hükümden önce

**Dondurma anı: 2026-11-26 06:13:46 (yerel saat).** Bu andan sonra aday kodu (aşağıdaki dosyalar) değiştirilmez. Hüküm
burada yok: başka bir koşuda, 200 ve üstü hiç kullanılmamış tohum ve yeni sahnelerle yapılacak. `secim.json` değişmedi
(hüküm verilmeden seçim değişmez). Önceden konan ölçüt aynen geçerli: uçurum koşularında 0 hakem düşmesi, yanlış alarm
koşularında 0 durma.

**Kısa hüküm (yalnız ayar verisi, iyimser okunmalı):** 3A ayarda iki zayıf sınıfı da 0 hakem düşmesiyle geçti, ama yarıkta
en küçük pay yalnız 0,4 cm. 3B dar açıklık yanındaki dönüşü 0 / 240 ile kapattı. 3B dar yarığı kapatamadı: 9–12 cm'de
10 / 168 hakem düşmesi kaldı, en küçük pay −3,7 cm. 3B bu hâliyle ölçütü sağlayamaz.

## 1. 14 sensörlü düzenin tek hüküm düşmesinin kök nedeni (`t2_hukum-02838`)

Kayıt: `yarik_11` (11 cm x 1 m), y 0,285, açı 10°, 0,25 m/s, tohum 207. Hakem: `teker_on_sol` merkezi pay −0,3 cm, tetik
yok. Aynı görev sürdürülünce (`t2_hukum_fiz-00009`) robotu `on_ic_sol` ("yok") 2,81 s'de durduruyor, teker inmiyor.
Hüküm tohumu (207) yeniden koşulmadı. Mekanizma, aynı sahne, y ve açıyla geliştirme tohumlarında (1–3, başlangıç açısı tam
10°'ye sabit) kayıtlı olarak yeniden üretildi. Tohum 2 aynı biçimde düşüyor (pay −0,04 cm).

- **Geometri.** Robot merkezi yarığın orta hattının 0,285 m sağında. 10° açıyla, sol ön teker başlangıçta yarığın y
  aralığının içinde ama yarığın önünde (x < 16). Teker yarığın uzak yan kenarına (y1) doğru kayıyor ve yakın kenara
  (x = 16) tam **köşede** varıyor. Teker merkezi köşeyi birkaç mm kırpıyor, yarığın üstünden geçmiyor. Pay önce
  2,5 mm / 10 ms hızla (ileri hız, x kenarına yaklaşma) sıfıra iniyor, sonra 0,43 mm / 10 ms hızla (yanal hız
  0,25 · sin 10°) yeniden artıyor.
- **Sensörler neden görmedi.** Çift iz sensörlerinin izleri teker yolunun ±2 cm yanından ve 0,139 m önünden geçiyor.
  Köşe tekerin sağında kalıyor. Dış iz (y 0,236) yarığa hiç girmiyor. İç iz (y 0,196) köşeden yalnız ince bir üçgen
  kesiyor (dik uzaklık ≈ 2 cm + kırpma payı). 10°'de üçgenin iç teğet çemberi ≈ 0,46 x 2 cm ≈ 0,9 cm, ROI 15° izin zemin
  yarıçapı ≈ 1,8 cm. Öbek kuralı (zemin ışınları ağırlığın %25'ini taşıdıkça "zemin") yüzünden sensör hep zemin diyor.
  Kayıtta iç iz okuması 2,19–2,35 s'de beklenenin 10–19 mm üstüne çıkıyor (yarık duvarına değen ışınlar). Bu, 100 mm
  eşiğin çok altında. Köşe sensörü (y 0,299, çapraz) ve öbür izler zemin görüyor. Teker 2,46 s'de köşeyi kırpıyor.
  Yarığın içine ancak 13 cm içerideki `on_ic_sol` giriyor: 2,71 s'de ilk dönüşsüz örnek, yavaşlama, 5 dönüşsüz örnekten
  sonra 2,79 s'de tetik. O an teker köşeyi çoktan geçmiş.
- **Pay neden eksi.** Bu bir kaçırma değil, bir köşe kırpması: teker merkezi deliğin dikdörtgeninin köşesine birkaç mm
  giriyor (hükümde 3 mm). Teker 58 mm genişliğinde ve 62,5 mm yarıçapında, bu yüzden fiziksel iniş 0. Hakem kuralı
  (teker merkezi kenarı geçti) bunu düşme sayıyor.
- Ayar ızgarasında aynı mekanizma ±10°'de başka y'lerde de çıkıyor: 14 sensörlü düzen `t3_a_gel`'de 5 / 1248 (9–11 cm,
  pay −0,31…−0,03). Bunların ikisinde tetik hiç yok, üçünde köşe sensörü geç tetikliyor.

## 2. Adaylar (tam tanım)

Ortak (iki aday): z 120 mm, dikeyden 30° (aksi yazılmadıkça), koni 27° (ROI'li sensörlerde 15°). Eşik +100 mm, art arda 3
onay, dönüşsüz politika `yavasla` (0,5 s 0,10 m/s, art arda 5 dönüşsüz = tetik). Fren rampası 2,0 m/s² ve konum tutma
(kp 40, ki 100). VL53L1X kısa kip, 20 ms bütçe, 20 ms aralık, menzil 1,3 m. Hız önerisi 0,25 m/s. Kalibrasyon: açılışta
26 örnek ortancası. Robot çerçevesi: +x ileri, +y sol, m. Yön: 0 ileri, ±45 çapraz ön, ±135 çapraz arka, 180 geri,
±90 yana.

### SECIM_3A (donanım adayı): `8WRaD+4AD+2YR40`, 14 sensör (`deney.SECIM_3A`, `sensor.ADAY_3A`)

14 sensörlü adaydan (`secim.json`, `8WRD+4AD+2YR40`) **tek fark: iz çiftinin aralığı ±2 cm'den ±2,5 cm'ye** çıktı. Sayı,
yükseklik, eğim, ROI, eşik ve denetçi aynı.

| sensör | x | y | z | eğim ° | yön ° | koni ° |
| --- | --- | --- | --- | --- | --- | --- |
| on_sol / on_sag | 0,255 | ±0,250 | 0,12 | 30 | ±45 | 27 |
| on_iz_dis_sol / _sag | 0,255 | ±0,241 | 0,12 | 30 | 0 | 15 (ROI) |
| on_iz_ic_sol / _sag | 0,255 | ±0,191 | 0,12 | 30 | 0 | 15 (ROI) |
| on_ic_sol / _sag | 0,255 | ±0,085 | 0,12 | 30 | 0 | 27 |
| arka_sol / arka_sag | −0,255 | ±0,250 | 0,12 | 30 | ±135 | 27 |
| arka_ic_sol / _sag | −0,255 | ±0,085 | 0,12 | 30 | 180 | 27 |
| yan_sol / yan_sag | 0,10 | ±0,250 | 0,12 | 40 | ±90 | 15 (ROI) |

Gerekçe: köşe kırpmasında izin kestiği üçgenin boyu iz ile teker yolunun aralığıyla büyüyor. 9 cm yarığın tam ortada
olduğu en kötü durumda iç iz ±2,5 cm'de kenarın hâlâ 2,0 cm içinde (±2 cm'de 2,5 cm). Denenen öbür iki değişiklik (iz
çifti z 60 mm / 40°, `8WL`, ±2 cm) yarıkta 4 / 1248 düştü. `8WLa` (z 60 mm / 40° + ±2,5 cm) `8WRa` ile aynı sonucu verdi
(0 / 1248, pay 0,4). En küçük değişiklik olduğu için `8WRa` seçildi.

### SECIM_3B (pratik aday): `6OD+4AD`, 10 sensör + firmware davranış kuralları (`deney.SECIM_3B`, `sensor.ADAY_3B`)

Donanım `SECIM_3` (on sensör) ile birebir aynı: önde köşe ±0,250 (±45°), iz ±0,190 ve iç ±0,085 (düz öne), arkada köşe
±0,250 (±135°) ve iç ±0,085 (180°). Hepsi z 0,12, 30°, koni 27°. Davranış kuralları denetçide (`denetci.py`,
`DenetciAyar(kural=...)`, `UcurumDenetci.komut` / `hiz_siniri`). Kurallar yalnız sensör okumasını ve Pi'nin `sur`
komutunu (v, w) görür, hakemi ya da gerçek pozu okumaz:

| kural | değer | ne yapar |
| --- | --- | --- |
| `donus_yay_r` | −1,00 m | Pi yerinde dönüş isterse (abs v < 0,02 m/s, abs w > 0,02 rad/s), firmware dönüşü **geri yaya** çevirir: v = −1,0 · abs w, dönüş yönü korunur. Arka sensörler tekerlerin gideceği zemini önce görür. |
| `donus_w_tavan` | 0,25 rad/s | yerinde dönüşte w tavanı |
| `geri_tavan` | 0,15 m/s | geri gidişte hız tavanı (v ve w birlikte ölçeklenir, yarıçap korunur). Geri yayda v −0,15 m/s, w 0,15 rad/s olur. |
| `supheli_esik_m` / `surunme_hiz` / `supheli_s` | 0,02 m / 0,05 m/s / 1,0 s | herhangi bir sensörde okuma − beklenen > 20 mm ise 1 s sürünme (0,05 m/s). Durdurmaz, tetik eşiği (100 mm) aynı. |

Bedel: robot yerinde dönemez. 90° dönüş ≈ 1,6 m geri yay ister (≈ 10 s). Geri yaya alan gerekir. Sürünme, yanlış alarm
sahnelerinin 30 / 72'sinde başladı (eşik, halı, koyu bant, rampalar), yani bu zeminlerde robot yavaşlar. Ayarda denenen
öbür kurallar: ileri yay r 0,3 / 0,5 / 0,8 / 1,0 (dönüş 36 / 21 / 25 / 22 / 240 düştü: dönülen yandaki kenar teğet
geçiliyor ve tetik yok) ve geri yay r 0,5 (0 / 240, pay 2,4). Geri yay r 1,0 en büyük payı verdiği için (4,1) seçildi.

## 3. Ayar (geliştirme) ölçümü

Yalnız geliştirme tohumları 1–2 (izin verilen 1–3) ve daha önce kullanılmış sahneler: `yarik_9…15` (9 / 11 / 13 yalnız
`t2_hukum`'da, ötekiler ayarda ve `t_hukum`'da kullanılmıştı), `acik_40…100`, `merdiven_17x30`, `bosluk_3m`,
`DENETIM_GELISTIRME` ve `DENETIM_SINAMA_YENI` (yanlış alarm, tohum 1). Hücre: `hakem düşme / koşu · en küçük pay cm`.
Yanlış durma satırında `durma / koşu`. Bütün koşular `sonuc/t3_a_gel.csv` ve `sonuc/t3_b_gel.csv` dosyalarında, ham
kayıtlar `sonuc/ham/t3_*.jsonl` altında (git dışı). Hata 0.

**`t3_a_gel`** (6280 koşu; yarık: 6 genişlik x 13 y (0–0,30) x açı −10 / 0 / 10 / 15 x 0,25 / 0,39 m/s x tohum 1–2)

| sınıf | `8WRD` (14, secim.json) | **`8WRaD` (3A)** | `8WLD` | `8WLaD` |
| --- | --- | --- | --- | --- |
| yarık 9–15 cm | 5 / 1248 · −0,3 | **0 / 1248 · 0,4** | 4 / 1248 · −0,1 | 0 / 1248 · 0,4 |
| dönüş, dar açıklık yanı d 0,35–0,50 (tohum 1) | 0 / 120 · 1,6 | 0 / 120 · 1,6 | 0 / 120 · 1,6 | 0 / 120 · 1,6 |
| geri, dar açıklık 0,40–0,60 | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 |
| ileri, dar açıklık 0,40 / 0,50 | 0 / 60 · 7,2 | 0 / 60 · 7,2 | 0 / 60 · 5,9 | 0 / 60 · 6,7 |
| ileri, geniş kenar | 0 / 18 · 6,5 | 0 / 18 · 6,5 | 0 / 18 · 5,3 | 0 / 18 · 5,3 |
| geri, geniş kenar | 0 / 4 · 8,7 | 0 / 4 · 8,7 | 0 / 4 · 8,7 | 0 / 4 · 8,7 |
| dönüş, geniş kenar | 0 / 12 · 5,2 | 0 / 12 · 5,2 | 0 / 12 · 5,2 | 0 / 12 · 5,2 |
| yanlış durma (12 sahne) | 0 / 72 | 0 / 72 | 0 / 72 | 0 / 72 |

3A yarıkta genişliğe göre: 9 cm 0 / 208 (pay 0,4), 10: 0 / 208 (0,4), 11: 0 / 208 (0,9), 12: 0 / 208 (0,4), 13: 0 / 208
(3,9), 15: 0 / 208 (4,8). En küçük paylar ±10°'de: −10° / y 0,15'te köşe sensörü (`on_sol`, sapma), +10° / y 0,30'da iç
sensör (`on_ic_sol`, yok).

**`t3_b_gel`** (4270 koşu; yarık: 6 genişlik x 7 y x açı 0 / 10 x 2 hız x tohum 1; dar açıklık dönüşü tohum 1–2)

| sınıf | `yok` (10, SECIM_3) | `yay30` | `yay50` | `yay80` | `yay100` | `geri50` | **`geri100` (3B)** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yarık 9–15 cm | 13 / 168 · −4,7 | 10 / 168 · −3,7 | 10 / 168 · −3,7 | 10 / 168 · −3,7 | 10 / 168 · −3,7 | 10 / 168 · −3,7 | **10 / 168 · −3,7** |
| dönüş, dar açıklık yanı d 0,35–0,50 | 48 / 240 · −8,2 | 36 / 240 · −4,7 | 21 / 240 · −4,5 | 25 / 240 · −5,4 | 22 / 240 · −4,1 | 0 / 240 · 2,4 | **0 / 240 · 4,1** |
| geri, dar açıklık | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 | 0 / 36 · 8,9 |
| ileri, dar açıklık | 0 / 60 · 5,6 | 0 / 60 · 5,6 | 0 / 60 · 5,6 | 0 / 60 · 5,6 | 0 / 60 · 5,6 | 0 / 60 · 5,6 | 0 / 60 · 5,6 |
| ileri, geniş kenar | 0 / 18 · 5,7 | 0 / 18 · 7,0 | 0 / 18 · 7,0 | 0 / 18 · 7,0 | 0 / 18 · 7,0 | 0 / 18 · 7,0 | 0 / 18 · 7,0 |
| geri, geniş kenar | 0 / 4 · 8,5 | 0 / 4 · 10,6 | 0 / 4 · 10,6 | 0 / 4 · 10,6 | 0 / 4 · 10,6 | 0 / 4 · 10,6 | 0 / 4 · 10,6 |
| dönüş, geniş kenar | 0 / 12 · 4,5 | 0 / 12 · 6,2 | 0 / 12 · 5,6 | 0 / 12 · 6,0 | 0 / 12 · 6,2 | 0 / 12 · 6,7 | 0 / 12 · 7,0 |
| yanlış durma (12 sahne) | 0 / 72 | 0 / 72 | 0 / 72 | 0 / 72 | 0 / 72 | 0 / 72 | 0 / 72 |

3B yarıkta: 9 cm 2 / 28, 10: 3 / 28, 11: 3 / 28, 12: 2 / 28, 13: 0 / 28 (pay 0,3), 15: 0 / 28. Düşmelerin çoğu açı 0 ve
y 0,25'te: yarık iz sensörünün (±0,19) dışında, köşe sensörü izinin (±0,30) içinde, teker çizgisinin üstünde kalıyor ve
hiçbir sensör tetiklemiyor. Kural bunu düzeltemez: o yarığı gören sensör yok. Sürünme, düşmeyi 13'ten 10'a indirdi.
Ayrıca 10° / y 0,30'da iki köşe kırpması var.

**Ayar süreci (dürüstlük).** Adaylar ve kural değerleri sonuçlar görüldükten sonra seçildi. `t3_b_gel`'e kural
çeşitleri iki kez eklendi (önce `yay80` / `yay100`, sonra `geri50` / `geri100`), önceki görevlerin kimliği değişmedi. Bu
yüzden bu tablolar iyimser okunmalı, hüküm sayılmaz. Hüküm tohumu (200 ve üstü) bu çalışmada hiç koşulmadı.

## 4. Bilinen zayıflıklar (hükümden önce yazıldı)

- 3A: yarıkta pay 0,4 cm. Köşe kırpması mekanizması ±10°'de yalnız daraldı, kapanmadı. Hükümde yeni açı ya da y
  (ör. ±8° / ±12°, 9–10 cm) eksi pay verebilir. Dar açıklık yanında dönüşte pay 1,6 cm (değişmedi).
- 3A: iz çifti ±2,5 cm'de dış iz y 0,241'de, etek sınırına (0,250) 9 mm. ROI kaybı, çapraz konuşma ve iki I2C hattı yine
  modellenmedi.
- 3B: dar yarık (9–12 cm) açık, ölçütü sağlayamaz. Yerinde dönüş geri yaya çevrildiği için robotun arkasında ≈ 1,6 m boş
  alan gerekir. Geri yayın kendisi yalnız dar açıklık ve merdiven yanında ölçüldü, dar koridorda, kapı eşiğinde ya da
  arkada engel varken ölçülmedi. Pi'nin gezinmesi yerinde dönüşü varsayıyorsa davranış değişir (tasarım kararı).
- 3B: sürünme (+20 mm) eşik, halı, koyu bant ve rampalarda başlıyor (30 / 72). Durma yok, ama bu zeminlerde robot
  0,05 m/s'ye iner.
- İki aday da yalnız tohum 1–2 ile ayarlandı. Dar açıklık dönüşünde 3A tohum 1, kusur ve duyarlılık ızgarası
  (`t2_kusur`, `t2_duyar`) yeni adaylarla koşulmadı.

## 5. Dosya özetleri (sha1, dondurma anında)

| dosya | sha1 |
| --- | --- |
| `sensor.py` | ce1e024bfcd30ef9858d5c2cb71c90cb101be6f2 |
| `denetci.py` | c1bd5c34b6719f9447986031db0e9395a0b7c457 |
| `kosu.py` | 9d8fc4b3e3d90610c88e420d27640c5b7108d09e |
| `deney.py` | bcdb67bb7116cd0bf7a8d7ddf5556b30c6efa11f |
| `sahne.py` (değişmedi) | 7437fc9275d537edb2e26a2d481cc49d012e4dff |
| `secim.json` (değişmedi) | fac7ef8e8de7a3d6e322a925bbf0d4941460094f |
| `testler/test_aday3.py` | 0f25d89f6dec4e05d02193879a21ba9119c9413f |

Önceki görev listeleri değişmedi: `t2_hukum`, `t_hukum`, `t2_donus_gel2`, `sinama2`, `t3_a_gel` ve `t3_b_gel` bugünkü
koddan yeniden üretildi, ham kayıtla 0 fark. `_ana()` yalnız seçimde `kural` alanı varsa onu taşıyor, eski seçimlerde bu
alan yok. Testler: `ucurum/testler` venv'de 44 / 44, py -3'te 44 (8 atlanan); `kod/testler/kos.py` 78 geçen, 2 atlanan,
0 kalan.

Hüküm için kullanım: yerleşim `sensor.yerlesim(S["yerlesim"]["ad"], 0.12, 30)`, denetçi `DenetciAyar(**deney._ana(S))`,
koşul `S["hukum_kosul"]` (S = `deney.SECIM_3A` ya da `deney.SECIM_3B`).
