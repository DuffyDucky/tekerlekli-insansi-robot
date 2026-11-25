# ucurum: aşağı inen merdiven ve zemin boşluğunda durma (uçurum sensörü)

Robot (158 cm, devrilebilir; LiDAR yerden 0,295 m'de yatay tarar, aşağı inen basamağı görmez) için tabanın önüne aşağı
bakan VL53L1X türü lazerli mesafe sensörleri ve ESP32'de Pi'den bağımsız motor kesme / fren mantığı ölçülür. Sonuç ve
hüküm: `sonuc/SONUC.md`. Robot varyantı **ONERI** (öneri firmware + ön omni; VARSAYIM, bugünkü robot V0 değil).

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
| Kütle merkezi ve el hesabı devrilme ivmesi (5) | `%V% kutle_merkezi.py` | ≈ 3 s |
| LiDAR merdiveni görüyor mu (7) | `%V% lidar_denetim.py` | ≈ 5 s |
| Tablolar / görseller | `py -3 analiz.py` -> `sonuc/tablolar.md`; `py -3 ciz.py` -> `gorsel/*.png` | ≈ 5 s |
| Birim testleri | `py -3 -m unittest discover -s ucurum/testler -t .` (`kod\fizik` içinde; MuJoCo testleri `%V%` ile) | ≈ 1 s (ikisi de; 19 test) |
| 3B gösterim (9) | `kod\ucurum.bat [sahne]` (varsayılan `merdiven_17x30`; `kose`, `kuyu`, `bosluk_3m`, `merdiven_15x28` ...) | - |

`deney.py` kaldığı yerden sürer (`sonuc/ham/<aşama>.jsonl`), `--surec N` ile en çok üç süreç (`SUREC_TAVAN`), her süreç
tek iş parçacığı ve düşük öncelik. Aşamalar arası seçim (`secim.json`: sınamaya giden yerleşim, eşik, onay, politika, fren)
geliştirme ve denetim sonuçlarından elle yazıldı; gerekçe SONUC.md'de. `secim.json` şimdi dar açıklık düzeltmesinden sonraki
seçimi taşır (`4OD+2AD`, `yavasla`) ve yalnız `sinama2` / `sinama2_karsi` onu okur. İlk seçim (`2KD+2AD`) `deney.SECIM_1`'de
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
| `4OD+2AD` | `2KD+2AD` + ön iç (0,255, ±0,085), düz öne yatık: altı sensör (**seçilen**, dar açıklık düzeltmesinden sonra) |

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

**Hakem (yalnız ölçüm).** Her 10 ms: dört teker merkezinin kenara yatay payı (sahnenin `kenarlar` listesi: yarı düzlemler
ve dar açıklıkta `["dik", x0, x1, y0, y1]` dikdörtgen delik; delik içinde pay negatif = en yakın delik kenarına uzaklığın
eksisi, dışında deliğe uzaklık), gövde eğimi, z. Düştü = herhangi bir tekerin merkezi kenarı geçti (pay < 0), ya da eğim > 15°, ya da z 3 cm'den çok düştü.
Pay = koşu boyunca dört tekerin en küçük payı.

**Dürüstlük.** Denetçi yalnız sensör okumalarını görür; yer gerçeği yalnız hakemde. Geliştirme (ayar) tohumları 1–3 ve
geometriler `merdiven_17x30`, `bosluk_3m`; sınama tohumları 101–110 ve geometriler `merdiven_15x28`, `merdiven_19x25`,
`kuyu`, `kose` (geliştirmede hiç koşulmadı) ve ızgarada olmayan açılar. Dar açıklıkta geliştirme `acik_40/50/60/70/80/100`,
tohum 1–2, yanal −0,2 … 0,2; sınama `acik_45/55/65/75/90`, `acik_60_sig`, `dar_merdiven_60/80`, tohum 101–105, yanal −0,15 …
0,25, ve beş yeni yanlış alarm sahnesi. Başarısız ve hatalı koşular CSV'de durur.

## Modellenmeyenler

Gerçek VL53L1X histogram işleme, ortam ışığına bağlı menzil, eğik gelişte sinyal kaybı, cam / ayna / parlak siyah zemin,
sensör camında toz, çapraz konuşma (yan yana sensörler aynı anda); basamak burnu ve halı kaplı basamak; teker lastiği
esnekliği; IMU (firmware'de yok: eğimi bilmez); sensör kablosu / I2C kopması (ölü sensör olarak modellendi);
kalibrasyonun halı üstünde yapılması (denetim sahnesinde halı başta, kalibrasyon halı üstünde: gerçek kullanımla aynı).
Robottan dar açıklık bağımsız denetimden sonra eklendi (`acik_*`, `dar_merdiven_*`): ilk seçim olan dört köşe düzeni
0,45–0,75 m açıklıkta düşüyor (sınamada 191 / 1800), seçim altı sensörlü `4OD+2AD`'ye değişti (sınamada 0 / 1800). Sınanmayan:
0,40 m'den dar delik (ön izler arası ≈ 0,21 m boşluk; teker hizasında ≈ 0,2 m'lik delik hiçbir izin altına girmeyebilir),
dikdörtgen olmayan açıklık, açıklığa geri giderek ya da yerinde dönerek yaklaşma.
