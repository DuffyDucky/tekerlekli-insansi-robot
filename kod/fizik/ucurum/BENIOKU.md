# ucurum: aşağı inen merdiven ve zemin boşluğunda durma (uçurum sensörü)

Robot (158 cm, devrilebilir; LiDAR yerden 0,295 m'de yatay tarar, aşağı inen basamağı görmez) için tabanın önüne aşağı
bakan VL53L1X türü lazerli mesafe sensörleri ve ESP32'de Pi'den bağımsız motor kesme / fren mantığı ölçülür. Sonuç ve
hüküm: `sonuc/SONUC.md`. Robot varyantı **ONERI** (öneri firmware + ön omni; VARSAYIM, bugünkü robot V0 değil).

> **Durum (bağımsız inceleme 3, 2026-11-26): onaylanmış seçim yok.** `secim.json`'daki on dört sensörlü
> `8WRD+4AD+2YR40`, **ölçütü SAĞLAMAYAN en iyi adaydır**, onaylanmış seçim değildir. Önceden konan ölçüt (0 hakem düşmesi,
> 0 yanlış durma) `t2_hukum`'da 1 / 3476 hakem düşmesiyle sağlanmadı (fiziksel 0). On sensörlü `6OD+4AD` de `t_hukum`'da
> sağlamadı (27 hakem, 6 fiziksel). Son commit edilen seçim altı sensörlü `4OD+2AD`. Tamamlama turu ve tamamlama 2 commit
> edilmedi. Üç düzenin tehlike sınıfına göre karşılaştırması: `sonuc/katmanli_oneri.md`. Aşağıda "seçim" ya da "seçilen"
> diye anılan 14 sensörlü düzen bu anlamda okunmalı.

## Çalıştırma (`%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe`, `kod\fizik\ucurum` içinde)

| Ne | Komut | Süre (bu PC, 1 süreç) |
| --- | --- | --- |
| Durma mesafesi + devrilme (3, 5) | `%V% deney.py durma` | ≈ 2,5 dk |
| Yanlış alarm denetimi (1; gölge denetçilerle eşik x onay taraması) | `%V% deney.py denetim` | ≈ 25 dk |
| Rampaya çapraz girişte yanlış alarm ayrıntısı | `%V% deney.py rampa_ayrinti` | ≈ 2 dk |
| Ana ızgara, geliştirme 1 (4) | `%V% deney.py gelistirme` | ≈ 30 dk |
| Geliştirme 2: arka sensörlü, çapraz köşe, eşik 40 / 100 mm | `%V% deney.py gelistirme2` | ≈ 9 dk |
| Çapraz köşe yerleşiminin yanlış alarmı | `%V% deney.py denetim2` | ≈ 2 dk |
| Sensör kusurları (6) | `%V% deney.py kusur` | ≈ 15 dk |
| Sınama: seçilen yerleşim, ayrı tohum + yeni geometri (8) | `%V% deney.py sinama` (CSV'deki koşu politika `ucurum` ile) | ≈ 19 dk |
| Sınama, seçilen politika `yavasla` ile (ileri + yanlış alarm, tohum 101–105) | `%V% deney.py sinama_y --surec 2` | ≈ 6 dk |
| Dar açıklık, geliştirme: 3 aday yerleşim x 6 genişlik x yanal kayma; ek sensörün geniş kenar / yanlış alarm / ölü sensör denetimi | `%V% deney.py dar_gelistirme --surec 3` | ≈ 6 dk (3 süreç) |
| Sınama 2 (yeni seçim `4OD+2AD`): ilk sınamanın bütün ızgarası + 8 dar açıklık sahnesi + 5 yeni yanlış alarm sahnesi | `%V% deney.py sinama2 --surec 3` | ≈ 12 dk (3 süreç) |
| Sınama 2 karşılaştırma (seçilmeyen 2KD+2AD ve 3KOD+2AD, yalnız dar açıklık; seçime girmez) | `%V% deney.py sinama2_karsi --surec 3` | ≈ 8 dk (3 süreç) |
| **Tamamlama turu** (bağımsız incelemenin açık bıraktıkları; hepsi `--surec 3`, süreler 2–3 süreçle) | | |
| 1a: delik tehlikesi (denetçi kapalı; kare delik / 1 m yarık, 4–35 cm) ve yarık boyu (20–70 cm) | `%V% deney.py t_delik_tehlike`, `t_delik_boy` | ≈ 1,5 + 2 dk |
| 1b: dar delik / yarıkta algılama, 3 aday (`4OD+2AD`, `4TD+2AD`, `6OD+2AD`); yarıkta fiziksel sonuç | `t_delik_gel`, `t_delik_fiz` | ≈ 8 + 2 dk |
| 2: açıklığa geri giderek / yerinde dönerek yaklaşma (`4OD+2AD`, `4OD+4AD`); dönüş hızı tavanı | `t_yaklasma_gel`, `t_donus_w` | ≈ 4 + 3 dk |
| 3: altı sensörde tek tek ölü sensör, dönüşsüz örnek %5 / 20 / 50 | `t_kusur6` | ≈ 2,5 dk |
| 4: 10° inişte fren ivmesi taraması + tutma freni (yok / konum / mekanik); iniş rampası ucunda düşüş | `t_rampa_fren`, `t_rampa_ucurum` | ≈ 2 + 2 dk |
| 5 + 6: sensör zamanlama kipleri (VL53L1X) ve duyarlılık (gecikme, µ, montaj, yük, gürültü, fren ivmesi) | `t_duyar` | ≈ 11 dk |
| Seçim öncesi son denetim (`6OD+4AD`, kısa kip, konum tutma) | `t_aday_son` | ≈ 3 dk |
| 7: hüküm (secim.json + `hukum_kosul`, tohum 201–205, sınama 2 + yeni geometriler) | `t_hukum` | ≈ 31 dk |
| Hükümden sonra, yalnız rapor: hakemin düşme saydığı yarik_14 ve dar açıklık dönüş görevleri, koşu sürer (fiziksel sonuç) | `t_hukum_fiz` | ≈ 5 dk |
| Tamamlama tabloları | `py -3 tamamla_analiz.py` -> `sonuc/tamamlama_tablolar.md` ve `sonuc/tamamlama2_tablolar.md` | ≈ 2 s |
| **Tamamlama 2** (bağımsız incelemenin engelleyicileri; hepsi `--surec 3` ya da toplam 3 süreç) | | |
| Ayar: yarık düzeltmesi, 3 aday (`6OD+4AD`, `6WD+4AD` iz y ±0,216, `6WRD+4AD` + iz ROI 15°), tohum 1–2 | `t2_yarik_gel` | ≈ 7 dk (2 süreç) |
| Ayar: dar açıklık yanında yerinde dönüş, yan sensör adayları (`+2Y30`, `+2Y35`), tohum 1–2 | `t2_donus_gel` | ≈ 12 dk (1 süreç) |
| Ayar: yarık, sonradan eklenen aday `8WRD+4AD` (çift iz, ROI 15°); dönüş, ROI'li yan sensör `+2YR37` / `+2YR40` | `t2_yarik_gel2`, `t2_donus_gel2` | ≈ 2 + 4 dk (2 süreç) |
| Ayar: seçilen düzende tek tek ölü sensör + dönüşsüz oran; tekil duyarlılık satırları (tohum 1) | `t2_kusur`, `t2_duyar` | ≈ 2 + 5 dk |
| Hüküm 2 (secim.json, tohum 206–210, d 0,35–0,50 dönüş, 9–28 cm yarık) | `t2_hukum` | ≈ 22 dk (3 süreç) |
| Hükümden sonra, yalnız rapor: hakemin düşme saydığı yarık durumunun görevleri, koşu sürer | `t2_hukum_fiz` | ≈ 10 s |
| Kütle merkezi ve el hesabı devrilme ivmesi (5) | `%V% kutle_merkezi.py` | ≈ 3 s |
| LiDAR merdiveni görüyor mu (7) | `%V% lidar_denetim.py` | ≈ 5 s |
| Tablolar / görseller | `py -3 analiz.py` -> `sonuc/tablolar.md`; `py -3 ciz.py` -> `gorsel/*.png` | ≈ 5 s |
| Birim testleri | `py -3 -m unittest discover -s ucurum/testler -t .` (`kod\fizik` içinde; MuJoCo testleri `%V%` ile) | ≈ 3 s (ikisi de; 34 test, venv'de hepsi geçer, py -3'te 7'si atlanır) |
| 3B gösterim (9) | `kod\ucurum.bat [sahne]` (varsayılan `merdiven_17x30`; `kose`, `kuyu`, `bosluk_3m`, `merdiven_15x28` ...) | - |

`deney.py` kaldığı yerden sürer (`sonuc/ham/<aşama>.jsonl`), `--surec N` ile en çok üç süreç (`SUREC_TAVAN`), her süreç
tek iş parçacığı ve düşük öncelik. Aşamalar arası seçim (`secim.json`: sınamaya giden yerleşim, eşik, onay, politika, fren)
geliştirme ve denetim sonuçlarından elle yazıldı; gerekçe SONUC.md'de. **Güncellendi (tamamlama turu):** `secim.json` şimdi
`6OD+4AD` (on sensör), kısa kip zamanlaması ve konum tutma freni (`hukum_kosul`), hız önerisi 0,25 m/s taşır ve yalnız
`t_hukum` onu okur. Dar açıklık düzeltmesinin seçimi (`4OD+2AD`) `deney.SECIM_2`'de donduruldu: `sinama2`, `sinama2_karsi`
ve `t_hukum` / `t_aday_son` dışındaki tamamlama aşamaları onunla koşuldu (görev listesi değişmeden yeniden üretilir).
Önceki not: `secim.json` dar açıklık düzeltmesinden sonraki seçimi taşıyordu (`4OD+2AD`, `yavasla`) ve yalnız `sinama2` /
`sinama2_karsi` onu okuyordu. İlk seçim (`2KD+2AD`) `deney.SECIM_1`'de
donduruldu: `kusur`, `sinama` (politika `ucurum`) ve `sinama_y` sıfırdan yeniden koşulunca ilk koşudaki görevleri birebir
üretir (görev listeleri ham kayıtla karşılaştırıldı, 0 fark).

3B gösterim: `kod\ucurum.bat` robotu `merdiven_17x30` kenarına 0,25 m/s sürer; Pi tarafı (YuruBeyni) uçurumu bilmez,
ESP32 denetçisi durdurur, durum satırı "UCURUM: DURDU (sensör, neden, fren)" yazar. Başka sahne: `kod\ucurum.bat kose`;
hız: `kod\ucurum.bat merdiven_17x30 --beyin-arg v=0.39`; F7 baştan. `UCURUM_EKRAN=<png>` verilirse 9. sanal saniyede
pencere görüntüsü yazılır.

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `sahne.py` | sonlu zemin kutuları: merdiven (basamak R x T), dik boşluk (3 m), kuyu (menzil dışı), sahanlık köşesi; robottan dar açıklık (`acik_<cm>`: zeminde 2 m boyunda, 0,40–1,00 m genişliğinde dikdörtgen delik, yan zemin açıklığın dibine dek iner; `acik_60_sig` 0,4 m derin; `dar_merdiven_60/80`: açıklığın içinde 18 x 27 cm merdiven); denetim sahneleri (düz, 20 mm eşik, derz, koyu şerit, 10° iniş rampası, 5 / 10 mm halı; yalnız sınamada: 25 mm eşik, geniş derz, 30 cm koyu bant, 8° iniş rampası, 15 mm halı). `kur()` yalnız bu süreçte `dunya.sahne_xml`'i sarmalar: `ucurum` alanlı sahnede sonsuz düzlem (`zemin_duz` plane) sonlu kutularla değişir, öbür sahnelerde çıktı aynı (test) |
| `sensor.py` | VL53L1X türü sensör modeli (17 ışınlı koni, öbek kuralı, gürültü, dönüşsüz örnek, 50 Hz + bir örnek gecikme, arıza) ve aday yerleşimler |
| `denetci.py` | ESP32 uçurum denetçisi (saf mantık): kalibrasyon, eşik + art arda onay, dönüşsüz örnek politikası, donmuş çıktı denetimi, fren kipi |
| `kosu.py` | `UcurumEsp32` (FizikEsp32 alt sınıfı: denetçi firmware döngüsünde, motor çıkışını keser / frenler), hakem, senaryolar (ileri, geri, yerinde dönüş, yay), `kos()` |
| `deney.py` | aşama koşucusu; `analiz.py` tablolar; `ciz.py` görseller; `lidar_denetim.py` LiDAR denetimi |
| `demo.py` | 3B pencere eklentisi (`gorunum3b.py --eklenti ucurum.demo`; `kod\ucurum.bat`) |
| `tamamla_analiz.py` | tamamlama turu tabloları (`sonuc/t_*.csv` -> `sonuc/tamamlama_tablolar.md`) |
| `testler/test_tamamlama.py` | yeni yerleşimler gövdeye sığar, montaj bozusu izi yaklaştırır, yeni sahneler / hakem payı, 33 ms zamanlama ve varsayılan zamanlamanın ilk sürümle aynılığı; MuJoCo: konum tutma 10° inişte kaymayı durdurur, tutmasız kayar |
| `testler/test_ucurum.py` | denetçi, öbek kuralı, yerleşimin gövdeye sığması (seçilen ve aday düzenler dahil), sahne sarmalaması, dikdörtgen delik payı, dar açıklık sahnesi; MuJoCo: kafa kafaya dur / motor kesmede düş, 0,5 m açıklıkta dört köşe düzeni düşer / ön sensörlü düzen durur, denetçisiz alt sınıf = FizikEsp32 (bit düzeyinde) |

## Model ve varsayımlar

**Robot çerçevesi** (gövde merkezi, +x ileri, +y sol): etek x ±0,2625 y ±0,26 z 0,035–0,265; teker merkezleri x ±0,185,
y ±0,216, yarıçap 0,0625, genişlik 0,058 (`lale.xml`). Sensör modülü etek içinde: x ≤ 0,255, |y| ≤ 0,250 (z 60 mm'de alt açıklıktan,
seçilen z 120 mm / 30° çapraz yerleşimde ışın etek köşesinin ön-yan yüzünden, yaklaşık 2–3 cm yolda dışarı çıkar: köşede
pencere gerekir; simülasyonda robot geometrisi ışını kesmez, pencere kenarının koniyi kırpması modellenmedi); köşe sensörü tekerin önünde (x 0,255 > teker ön ucu 0,2475) ve dışında (y 0,250 > teker dış yüzü 0,245).
Koninin hiçbir ışını kendi tekerlerine çarpmıyor (`SensorDizisi.teker_ortusmesi`, bütün yerleşimlerde 0).

| Yerleşim | Sensörler (x, y m) |
| --- | --- |
| `2K` | ön köşeler (0,255, ±0,250) |
| `2I` | ön iç (0,255, ±0,120) |
| `3KO` | ön köşeler + ön orta (0,255, 0) |
| `4O` | ön köşeler + ön iç (0,255, ±0,085) |
| `+2A` | ek olarak arka köşeler (−0,255, ±0,250), geriye yatık |
| `2KD+2AD` | dört köşe, eğim düzlemi çapraz dışa: önde yön ±45°, arkada ±135° (ilk seçim; dar açıklıkta düşer) |
| `3KOD+2AD` | `2KD+2AD` + ön orta (0,255, 0), düz öne yatık |
| `4OD+2AD` | `2KD+2AD` + ön iç (0,255, ±0,085), düz öne yatık: altı sensör (dar açıklık düzeltmesindeki seçim; `deney.SECIM_2`'de donduruldu) |
| `4TD+2AD` | iç sensörler ±0,150'de (tamamlama adayı, seçilmedi) |
| `4OD+4AD` | `4OD+2AD` + arka iç (−0,255, ±0,085), düz geriye: sekiz sensör (tamamlama adayı) |
| `6OD+2AD` | `4OD+2AD` + ön iz sensörleri (0,255, ±0,190), düz öne, teker hizası: sekiz sensör (tamamlama adayı) |
| `6OD+4AD` | önde altı (köşe ±0,250 çapraz, iz ±0,190, iç ±0,085) + arkada dört (köşe çapraz, iç ±0,085): on sensör (tamamlama turunun seçimi; `deney.SECIM_3`'te donduruldu) |
| `6WD+4AD` / `6WRD+4AD` | iz sensörleri teker ekseninin önünde (±0,216); `R`: iz sensörlerinde ROI 15° koni (tamamlama 2 adayı) |
| `8WR` ön düzen | köşe ±0,250 çapraz, her teker hizasında iki iz ±0,196 / ±0,236 (ROI 15°), iç ±0,085: sekiz ön sensör |
| `+2Y30` / `+2Y35` / `+2YR37` / `+2YR40` | üçüncü parça, yan sensörler: x 0,10 (2Y35: 0,09), y ±0,250, dışa (yön ±90°), dikeyden 30 / 35 / 37 / 40°; `R`: ROI 15° |
| `8WRD+4AD+2YR40` | önde sekiz + arkada dört + yanda iki: **on dört sensör, ölçütü sağlamayan en iyi aday** (`secim.json`'da; tamamlama 2, hükümden geçmedi, onaylanmış seçim değil; SONUC.md) |

"D" soneki yalnız köşe sensörlerini (|y| = 0,250) çapraz dışa çevirir; orta / iç sensörler hep düz öne (yön 0) bakar.

Ad biçimi `<düzen>_z<yükseklik mm>_e<eğim °>` (ör. `2KD+2AD_z120_e30`; eğim dikeyden, yön düzleminde). Ön dingile göre: sensör x 0,255, ön teker temas
noktası x 0,185: dik bakan sensörün zemin izi tekerin 70 mm önünde; öne eğim θ ve yükseklik z ile iz z·tanθ kadar
daha ileride (z 0,06 / θ 30°: +35 mm; z 0,12 / θ 30°: +69 mm).

**Sensör (VARSAYIM; masada doğrulanmalı).** Koni tam açısı 27° (VL53L1X varsayılanı), 17 ışın; ölçüm = toplam ağırlığın
≥ %25'ini taşıyan en yakın öbek (kötümser: koninin yarısı boşluğu görse de zemin der). Gürültü σ 2,5 mm + %0,2 · d, 1 mm
çözünürlük; koyu yüzeyde σ × 2 ve %5 dönüşsüz; menzil 0,04–4 m, dışı = dönüş yok. 50 Hz, sensör fazı 0 / 10 ms, ölçüm
20 ms sonra kullanılabilir.

**Denetçi (ESP32).** 100 Hz döngü (firmware dilimi 10 ms). Açılışta robot dururken 26 örnek ortancası = beklenen zemin
mesafesi. Kanıt: okuma − beklenen > eşik. Dönüşsüz örnek politikası: `ucurum` (kanıt sayılır), `yok_say` (atlanır),
`yavasla` (0,5 s hız sınırı 0,10 m/s; art arda 5 dönüşsüz = kanıt; seçilen). Aynı mm değeri art arda 25 kez = donmuş
sensör, okumaları dönüşsüz sayılır. Art arda `onay` kanıt = tetik (mandallı). Tetik anında Pi'nin `sur` komutları ezilir.

**Fren kipleri ve motor modeli** (modelin kendisi değişmedi; `dunya.py` motor modeli, öneri firmware PI'ı):
`kes` = EN LOW, sürücü boşta (tork 0, yalnız dişli / yuvarlanma sürtünmesi); `fren` = EN HIGH + PWM 0: kısa devre freni
`tau = -tau_durma · w / w0` (rampasız, bekçi duruşuyla aynı); `rampa a` = teker hedefi 0'a `a` m/s² ile iner, öneri
firmware PI'ı (KP 4, KI 20, TAHMİN) rampayı izler (gerekirse ters PWM), rampa bitince PWM 0 (kısa devre freni). Motor
durma torku 21 kg·cm, dişli sürtünmesi 0,05 N·m, µ (TAHMİN; `fizik_parametreleri.json`). Kısa devre freni sıfır hızda tork
vermez: eğimde robotu tutmaz (bilinen bulgu, `kod/SIMULASYON.md`).

**Tamamlama turu eklentileri (varsayılanlarla davranış aynı; `sinama2` görevleri yeniden koşulup ham kayıtla birebir aynı
çıktı).** `SensorDizisi(periyot_ms, butce_ms)`: VL53L1X ölçüm aralığı ve zamanlama bütçesi (örnek alınır, bütçe sonunda 10 ms
dilime yukarı yuvarlanıp kullanılır; kip menzili `menzil_maks_m`). `sensor.montaj_bozu`: ±5 mm / ±3° montaj toleransı
(rastgele ya da sistematik en kötü: iz robota yaklaşır). `kosu.kos(..., gecikme_ms)`: tetik ile fren arasına ek denetim
gecikmesi; `degis` fizik parametreleri (µ); `ek_kutle` tabana nokta kütle (`yuk_ekle`; atalete kaba paralel eksen terimi,
yuvarlanma direnci statik yükten değişmez). **Tutma freni** (`tutma`, VARSAYIM): fren rampası bitince devreye girer.
`("konum", kp, ki)` = firmware enkoder konum tutması (arka enkoderler, her yanın iki motoru, u = kp·e + ki·∫e, |u| ≤ 1,
kp 40 PWM/m, ki 100 PWM/(m·s); ek donanım yok, **seçilen**); `("mekanik", N·m)` = teker başına sabit fren torku (yay baskılı
fren varsayımı; MuJoCo eklem sürtünmesi yük altında sızdığı için kısıt sertleştirildi). 10° inişte tutma için teker başına
≈ 0,70 N·m gerekir: motor sürekli torkunun (0,618 N·m, TAHMİN) üstünde, uzun süre konum tutma motoru ısıtır.
Hakeme teker merkezi z düşüşü (`teker_dz_min_mm`) ve gövde-zemin teması eklendi (delikte fiziksel sonuç); `surdur`
görevlerinde hakem "düştü" dedikten sonra koşu sürer. Yeni sahneler: `kare_<cm>` (w x w delik), `yarik_<cm>` (w x 1 m),
`yarik_<w>x<boy>`, `rampa_10_uzun` (4 m iniş), `rampa_10_ucurum` / `rampa_8_ucurum` (iniş rampasının ucunda 3 m düşüş;
z düşüşü ölçütü kapalı), `iskele_90` (0,9 m şerit, üç yanı boşluk), `merdiven_burun_18x28` (3 cm basamak burnu),
`basamak_12` (tek 12 cm basamak).

**Hakem (yalnız ölçüm).** Her 10 ms: dört teker merkezinin kenara yatay payı (sahnenin `kenarlar` listesi: yarı düzlemler
ve dar açıklıkta `["dik", x0, x1, y0, y1]` dikdörtgen delik; delik içinde pay negatif = en yakın delik kenarına uzaklığın
eksisi, dışında deliğe uzaklık), gövde eğimi, z. Düştü = herhangi bir tekerin merkezi kenarı geçti (pay < 0), ya da eğim > 15°, ya da z 3 cm'den çok düştü.
Pay = koşu boyunca dört tekerin en küçük payı.

**Dürüstlük.** Denetçi yalnız sensör okumalarını görür; yer gerçeği yalnız hakemde. Geliştirme (ayar) tohumları 1–3 ve
geometriler `merdiven_17x30`, `bosluk_3m`; sınama tohumları 101–110 ve geometriler `merdiven_15x28`, `merdiven_19x25`,
`kuyu`, `kose` (geliştirmede hiç koşulmadı) ve ızgarada olmayan açılar. Dar açıklıkta geliştirme `acik_40/50/60/70/80/100`,
tohum 1–2, yanal −0,2 … 0,2; sınama `acik_45/55/65/75/90`, `acik_60_sig`, `dar_merdiven_60/80`, tohum 101–105, yanal −0,15 …
0,25, ve beş yeni yanlış alarm sahnesi. Başarısız ve hatalı koşular CSV'de durur. Tamamlama turunda ayar (seçim) koşuları
`t_delik_*`, `t_yaklasma_gel`, `t_donus_w`, `t_kusur6`, `t_rampa_*`, `t_duyar`, `t_aday_son`: tohum 1–3, geliştirme sahneleri
ve yeni ölçüm sahneleri (`kare_4..35`, `yarik_4..35`, `yarik_<w>x<boy>`, `rampa_10_*`); hüküm `t_hukum`: tohum 201–205
(o ana dek hiç kullanılmamıştı; 206–210 ayrıldı, tamamlama 2 hükmünde kullanıldı), sınama geometrileri + `t_hukum`'dan
önce hiç koşulmamış `iskele_90`, `merdiven_burun_18x28`, `basamak_12`, `yarik_14/17/22/28`, `rampa_8_ucurum`. Bu
geometriler `t2_hukum`'da yeniden kullanıldı: `t2_hukum`'un 4016 görevinden 2992'si `t_hukum`'la birebir aynı (yalnız
tohum farklı). `t2_hukum`'da hiç koşulmamış sahne yalnız `yarik_9/11/13` (bağımsız inceleme 3).

## Modellenmeyenler

Gerçek VL53L1X histogram işleme, ortam ışığına bağlı menzil, eğik gelişte sinyal kaybı, cam / ayna / parlak siyah zemin,
sensör camında toz, çapraz konuşma (yan yana sensörler aynı anda); basamak burnu ve halı kaplı basamak; teker lastiği
esnekliği; IMU (firmware'de yok: eğimi bilmez); sensör kablosu / I2C kopması (ölü sensör olarak modellendi);
kalibrasyonun halı üstünde yapılması (denetim sahnesinde halı başta, kalibrasyon halı üstünde: gerçek kullanımla aynı).
Robottan dar açıklık bağımsız denetimden sonra eklendi (`acik_*`, `dar_merdiven_*`): ilk seçim olan dört köşe düzeni
0,45–0,75 m açıklıkta düşüyor (sınamada 191 / 1800), seçim altı sensörlü `4OD+2AD`'ye değişti (sınamada 0 / 1800). Sınanmayan:
0,40 m'den dar delik (ön izler arası ≈ 0,21 m boşluk; teker hizasında ≈ 0,2 m'lik delik hiçbir izin altına girmeyebilir),
dikdörtgen olmayan açıklık, açıklığa geri giderek ya da yerinde dönerek yaklaşma. **Güncellendi (tamamlama turu):** dar
delik, geri ve yerinde dönüş ölçüldü (SONUC.md, "Tamamlama turu"); seçim `6OD+4AD`'ye değişti. Hâlâ sınanmayan:
dikdörtgen olmayan / eğik kenarlı delik, yan zemine eğik inen boşluk, kısa kip dışındaki menzil davranışı (gerçek
histogram), çapraz konuşma (on sensör aynı anda); dar açıklığın yanında yerinde dönüş çözülmedi (SONUC.md).

## Tamamlama turu (2026-11-26)

Bağımsız incelemenin açık bıraktığı sekiz madde ölçüldü; sonuç ve hüküm `sonuc/SONUC.md` "Tamamlama turu", bütün tablolar
`sonuc/tamamlama_tablolar.md` (`py -3 tamamla_analiz.py`). Kısaca:

- **Seçim değişti:** `6OD+4AD` (on sensör: önde köşe ±0,250 çapraz, iz ±0,190 ve iç ±0,085 düz öne; arkada köşe çapraz ve
  iç ±0,085 düz geriye; hepsi z 120 mm, dikeyden 30°), eşik +100 mm / 3 örnek, `yavasla`, fren rampası 2,0 m/s² +
  **konum tutma** (firmware enkoder), VL53L1X **kısa kip, 20 ms bütçe, 20 ms aralık** (veri sayfası DS12385 Rev 8 3.5.2,
  Tablo 5), **hız 0,25 m/s** (tek öneri, ilk deneme ve nihai).
- Hüküm (tohum 201–205, sınama 2 + yeni geometriler, 3412 koşu; hakem 27 düşme sayar): 2872 uçurum koşusunda fiziksel düşme 6 (hepsi 14 cm x 1 m yarık,
  iç kenarı iz sensörünün 3 cm içinde), 540 yanlış alarm koşusunda 0 durma. Açık: o yarık durumu ve dar açıklığın 0,40 m
  yakınında yerinde dönüş (hakem düşme sayar, fiziksel 0; 0,35 m'de geliştirmede pay −8 cm).
- Simülasyonda yeni: delik / yarık / iskele / burunlu basamak / rampa ucu sahneleri, sensör zamanlaması, montaj toleransı,
  ek gecikme, ek yük, tutma freni, tekerin fiziksel inişi (bkz. "Model", "Tamamlama turu eklentileri"). Basamak burnu
  artık modellendi (`merdiven_burun_18x28`, 3 cm); halı kaplı basamak hâlâ yok.
- Gösterim (`kod\ucurum.bat`) `secim.json`'daki `hukum_kosul`'u da uygular; `gorsel/demo_pencere.png` on sensörle yeniden
  çekildi.

## Tamamlama 2 (2026-11-26)

Bağımsız inceleme tamamlama turunu "koşullu" bıraktı; üç engelleyicisi bu turda ele alındı. Sonuç ve hüküm `sonuc/SONUC.md`
"Tamamlama 2"de, tablolar `sonuc/tamamlama2_tablolar.md`'de (`py -3 tamamla_analiz.py`).

- **Hüküm: geçmedi.** Önceden konan ölçüt (hakem 0 düşme, 0 yanlış durma) bir koşuda sağlanmadı: `t2_hukum` (tohum
  206–210, 4016 koşu, 0 hata) 3476 uçurum koşusunda 1 hakem düşmesi saydı. Bu koşu `yarik_11`, y 0,285, 10°: teker merkezi
  kenarı 3 mm geçti, fiziksel iniş 0. 540 yanlış alarm koşusunda durma 0. İlk hükümde (`6OD+4AD`) hakem 27, fiziksel 6
  düşme vardı.
- **Aday değişti, hükümden önce donduruldu:** `8WRD+4AD+2YR40`, on dört sensör. Hükümden geçmediği için ölçütü
  sağlamayan en iyi adaydır, onaylanmış seçim değildir. Önceki seçim `deney.SECIM_3`'te
  donduruldu, `t_hukum` / `t_hukum_fiz` görevleri ham kayıtla aynı. `secim.json` eski değerine döndürülmedi, çünkü eski
  seçim aynı ölçütü daha çok düşmeyle geçemiyor. Gerekçe SONUC.md'de.
  - Yarık: incelemenin önerdiği iki düzeltme (iz y ±0,216 ve ROI 15°) ayarda yetmedi (400 koşuda 23 ve 13 hakem düşmesi).
    Her teker hizasına iki dar iz konunca 0 / 400.
  - Dar açıklık yanında yerinde dönüş: ROI'li iki yan sensörle ayarda 0 / 240 (önce 48 / 240); hükümde d 0,35–0,50'de
    0 / 360.
- Kusur (`t2_kusur`) ve tekil duyarlılık (`t2_duyar`) seçilen düzenle koşuldu. Ölü sensörde kaçırma 0. Tekil koşullarda
  0,25–0,39 m/s'de düşme yalnız uzun kip 100 ms'de; en kötü tekil pay 0,25 m/s'de 7,9 cm.
- Bedel: on dört VL53L1X (I2C / XSHUT), altı sensörde ROI (sinyal kaybı modellenmedi), etek yanında pencere. Robot yan
  kenarı bir uçuruma ≈ 9 cm'den yakınken durur.
- Gösterim (`kod\ucurum.bat`) yeni seçimi okur. `gorsel/demo_pencere.png` on dört sensörle yeniden çekildi.
