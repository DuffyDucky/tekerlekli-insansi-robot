# sanalray: LiDAR'sız gezinme (kafa kamerası + duvar etiketi + enkoder + ön sonar)

Soru: robot LiDAR olmadan, yalnız kafadaki tek kamera, duvardaki AprilTag 36h11 etiketleri, arka tekerlek enkoderleri ve
ön sonarla A'dan B'ye gidebilir mi, rastgele bırakılınca yerini etiketten bulabilir mi; kaç etiket, nerede, hangi boyda
gerekir? Sonuç ve hüküm: `sonuc/SONUC.md`. Robot modeli ONERI (öneri firmware + ön omni, VARSAYIM: bugünkü robot DEĞİL;
gezinme deneyinin robotu). LiDAR düzenekten ayrılır (`dz.lidar.ayir()`), hiç hesaplanmaz.

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `etiket.py` | etiket dokusu (OpenCV `generateImageMarker`), etiket planı üretimi (`plan_uret`, `planlar/*.json`), sahneye ekleme (`etiketli_sahne`), kafa kameralı model kopyası |
| `kamera.py` | mercek tablosu (üretici belgesi), `Kamera` (mujoco.Renderer), bozulmalar (`boz`), `Bulucu` (aruco + solvePnP IPPE_SQUARE), `olcum_2b` |
| `gorunurluk.py` | görünürlük haritası ve hız ölçümü |
| `konum.py` | `EtiketEKF`: arka dingil ölü hesabı + dönüş ölçeği + etiket menzil / kerteriz / psi güncellemesi |
| `algilayici.py` | SENSÖR tarafı: kamera karesi (bulanıklık gerçek dönüş hızından), ön sonar, odometri bozma, kafa servosu; `SensorBeyni` uyarlayıcısı |
| `beyin.py` | ALGORİTMA tarafı: `SanalRayBeyni` (A'dan B'ye, kayıp robot arama, sabit / tarayan kafa) |
| `deney.py` | odometri ölçümü, A'dan B'ye ve rastgele bırakılma ızgaraları, geliştirme / sınama kümeleri |
| `rapor.py` | ham -> `sonuc/*.csv`, `sonuc/tablolar.md`; `--ciz` -> `gorsel/gorunurluk.png`. `kayip_*.csv` içinde `ilk_etiket_s` = herhangi bir etiketin ilk algılanması, `lokalize_s` / `lokalize_yol_m` = süzgecin 3,5 m içindeki etiketten başlatıldığı an (konumlanma) |
| `demo.py` | 3B pencere (`kod\sanalray.bat`) |
| `testler/test_sanalray.py` | birim testleri (saf + MuJoCo / cv2 varsa görüntü ve fizik) |
| `kusur.py` | (dayanıklılık turu) kusur modeli: gerçek etiket planı (konum / açı hatası, eksik, yanlış yer, yırtık doku), `KusurluAlgilayici` (odak, montaj eğimi, gecikme, kare düşmesi, örtülme, parlama, titreşim bulanıklığı); kusur sıfırken `Algilayicilar` ile birebir aynı |
| `dayaniklilik.py` | (dayanıklılık turu) kusur ızgarası koşucusu ve raporu -> `sonuc/dayaniklilik_ab.csv`, `sonuc/dayaniklilik_kayip.csv`, `sonuc/dayaniklilik.md`; ham `sonuc/ham/dayaniklilik/` |
| `testler/test_dayaniklilik.py` | kusur planı, doğrulamalı başlatma, takılma denetimi, arındırılmış yanal sapma testleri (MuJoCo gerekmez) |
| (tamamlama turu) `kusur.gercek_plan(aday=...)`, `dayaniklilik.py` grupları `rota_temiz` / `rota`, `rapor_rota` | eksik / yanlış yer etiketi, aynı koridor / tohumun kusursuz koşusunda süzgecin kabul ettiği etiketlerden seçilir -> `sonuc/dayaniklilik_rota_ab.csv`, `sonuc/dayaniklilik_rota.md`; ham `sonuc/ham/dayaniklilik_rota/` |

Sanal ray testleri depo koşusuna bağlıdır: `py -3 kod\testler\kos.py` `kod/testler/test_sanalray_bag.py` üzerinden
`test_sanalray` ve `test_dayaniklilik`'i de koşar (MuJoCo / cv2 yoksa ilgili testler atlanır).

## Çalıştırma (`cd kod\fizik`, `%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe`)

```
%V% sanalray\gorunurluk.py --hiz                 # görüntü üretimi / algılama hızı -> sonuc/hiz.csv (≈ 30 s)
%V% sanalray\gorunurluk.py                       # görünürlük haritası -> sonuc/gorunurluk.csv (≈ 4 dk, tek süreç)
%V% sanalray\deney.py odometri                   # MuJoCo enkoder odometrisinin doğal oranı -> sonuc/odometri.json
%V% sanalray\deney.py ab --kume gelistirme --parca 0/2   (ve 1/2; en çok 2 süreç)
%V% sanalray\deney.py ab --kume sinama --aralik 5 --komsu 8 --parca 0/2
%V% sanalray\deney.py kayip --kume sinama --aralik 5 --parca 0/2
%V% sanalray\deney.py tek --koridor koridor_3 --aralik 5 --donus 0.25 [--kafa tarayan] [--kayit x.npz]
%V% sanalray\rapor.py ; py -3 sanalray\rapor.py --ciz
%V% -m unittest sanalray.testler.test_sanalray -v
%V% sanalray\dayaniklilik.py kos --grup tek_agir --parca 0/2    (ve 1/2; gruplar: temiz, tek_agir, ara --kosullar a,b,
                                                                  birlesik, kayip_tek, baslatma_gel, baslatma_sin)
%V% sanalray\dayaniklilik.py rapor
%V% sanalray\dayaniklilik.py kos --grup rota_temiz --parca 0/3   (önce; kusursuz koşu + ölçüm sayacı = aday etiketler)
%V% sanalray\dayaniklilik.py kos --grup rota --parca 0/3         (sonra; [--kosullar yanlis025_rota,...])
%V% sanalray\dayaniklilik.py rapor_rota
kod\sanalray.bat koridor_3 ab        kod\sanalray.bat koridor_5 kayip --kafa tarayan
```

Ağır betikler `_yol.dusuk_oncelik()` çağırır (BELOW_NORMAL, tek iş parçacığı, `cv2.setNumThreads(1)`). İlerleme `.durum`,
ham koşu kayıtları `sonuc/ham/` (git dışı; üretilen dokular ve kameralı model kopyası `sonuc/ham/onbellek/`).

## Nasıl kuruldu

- **Kamera.** CAD (`tasarim/freecad/montaj/montaj-analiz.json`, "Kamera Raspberry Pi Camera Module 3" merkezi) ->
  gövde çerçevesinde x 0,0651, y 0, z 1,565 m; kafa_bas gövdesinde, pan / tilt ile döner; yatay ileri bakar (tilt 0).
  `lale.xml` değişmedi: bu süreçte kameralı bir kopya derlenir (`etiket.kamerali_model_xml`). Görüş açıları Raspberry Pi
  belgesinden (Camera Module 3: yatay 66° / dikey 41°; Wide: 102° / 67°); MuJoCo iğne deliği `fovy` = dikey açı.
  İşleme 1152 x 648 (VARSAYIM; Pi 5 notu `sonuc/SONUC.md` içinde). Navigasyonda görüntü doğrudan bu çözünürlükte
  üretilir; görünürlük haritasında 1536 x 864'te üretilip küçültülür. 10 Hz. Pozlama 10 ms.
- **Etiket.** AprilTag 36h11 (OpenCV aruco `DICT_APRILTAG_36h11`), boy = siyah kare kenarı, 1 hücre beyaz pay. 1 mm
  ince kutu, yalnız görsel (grup 2, çarpışmasız, ışınlar görmez). Sahne JSON'ları değişmedi: etiket planı
  `planlar/<koridor>_<aralık>_<boy>_<yükseklik>.json`. Duvarlar kamera için 2,7 m yüksek ve opak bir görsel kopyayla
  uzatıldı (asıl duvar 1,0 m ve yarı saydam). Plan kuralı: her hattın iki ucunda karşı duvar, L köşesinde iki dış duvar, T
  kavşağında yan kolun karşısı ("kavsak"); ek olarak yan duvarlarda her N m'de bir, sırayla sol / sağ, kapı girintisi ve
  açıklığından kaçınarak (koridora paralel).
- **Algılama / poz.** `ArucoDetector` (alt piksel köşe), `solvePnP` IPPE_SQUARE; yatay düzlemde menzil, kerteriz ve etiket
  normalinin açısı (psi).
- **Konumlama.** EKF, durum (x, y, yön, dönüş ölçeği). Gerekçe `konum.py` başında: etiket kimliği tekil (eşleme
  belirsizliği yok) ve olabilirlik tek tepeli; parçacık süzgecine gerek yok. Dönüş ölçeği durumda, çünkü odometrinin
  dönüş yanlılığı (%14 / %25) bağımsız gürültü sayılınca 90° köşeden sonra süzgeç aşırı emin kalıp doğru etiketleri
  reddediyordu (geliştirme, koridor_3: 0,62 m sapma -> ölçekle 0,11 m). Etiket görünmezken kovaryans odometri gürültüsüyle
  büyür. Mahalanobis kapısı; arka arkaya 6 ret olursa 3,5 m içindeki etiketten yeniden başlatma.
- **Sanal ray.** Rota = sahne `orta_hat` çizgesinde en kısa yol (`gezinme.rota`), izleyici `gezinme.izleyici.YolIzleyici`
  (yerinde dönüş tavanı 0,5 rad/s: bulanıklık), engel için yalnız ön sonar (tek mesafe, 3 ışınlı dar koni, 4 m, dur-bekle).
  Yerinde dönüş bitince 0,6 s "dur-bak".
- **Odometri hata kademeleri.** MuJoCo enkoder odometrisi (ONERI, iz 0,426) gerçek dönüşün 1,124 katını bildiriyor
  (`sonuc/odometri.json`). Algılayıcı bunu bölüp istenen fazlalıkla çarpar: dönüş fazlası %0 / 14 / 25 (keşif deneyinin
  modeli), ötelemede +%2 yanlılık, %2 öteleme ve %3 dönüş std; yanal kayma MuJoCo'nun kendi teker kaymasından.
- **Kayıp robot araması.** Sabit kafa: yerinde 0,45 rad/s tam tur; tarayan kafa: gövde durur, kafa -80 / -40 / 0 / 40 / 80°
  (her birinde 0,6 s), gövde 180° döner, yine tarar. Etiket yoksa tarama sırasında sonarın en uzak gördüğü yöne döner,
  0,15 m/s ile en çok 3 m ya da sonar 0,9 m'ye dek ilerler, yeniden tarar. İlk etiket 3,5 m içindeyse süzgeç o etiketin
  tam pozundan başlar, kimliğinden koridor bilinir, hedefe rota kurulur.

## Dürüst ayrım

Geliştirme (ayar ve plan seçimi): koridor_1, koridor_3, tohum 101 (kayıpta bırakma tohumu +500). Sınama (hüküm):
koridor_2, koridor_4, koridor_5, koridor_6, tohum 1. Süzgeç gürültü değerleri görünürlük haritasından (ayrı, yapay duvar
sahnesi) ve geliştirme koşularından. Beyin yer gerçeğini görmez; hakem (varış, yanal sapma, konum hatası, temas) görür.

Dayanıklılık turu (2026-11-26, `dayaniklilik.py`): kusur ölçümleri sınama koridorlarında, tohum 1-3; hiçbir ayar bunlara
göre seçilmedi. Doğrulamalı başlatmanın eşikleri geliştirme kümesinde (koridor_1, koridor_3, bırakma 0-3, +500 tohumu;
üç tasarım, ikisi atıldı), hüküm sınamada (bırakma 10-13) ve birleşik orta kurulumda. `beyin.py` varsayılanı
`baslatma="tek"` (ilk sürüm) kaldı; ayrıntı `sonuc/SONUC.md` "Dayanıklılık turu".

Tamamlama turu (2026-11-26, bağımsız incelemeden sonra): ilk turda eksik / yanlış yer etiketi bütün plandan seçilmiş,
12 koşunun 6'sında robotun hiç görmediği bir etiket olmuştu (koşu temizle birebir aynı). Artık etiket, aynı koridor /
tohumun kusursuz koşusunda süzgecin kabul ettiği etiketlerden seçiliyor; bu liste deney tasarımı (hakem tarafı), Beyin
görmez. Ölçümler sınama koridorlarında, tohum 1-6 (1-3 ilk turla aynı), yalnız hüküm; hiçbir ayar değişmedi. Ayrıntı
`sonuc/SONUC.md` "Tamamlama turu".

## Sınırlar (simülasyonun iyimserliği)

Kusursuz baskı ve düz duvar, yansıma / parlak laminasyon yok (parlama bozulması ayrıca ölçüldü), mercek bozulması yok
(geniş mercek iğne deliği), yuvarlanan deklanşör yok, kafa titreşimi ve gövde eğimi yok, aydınlatma düzgün (ortam ışığı
artırıldı), insanlar ve hareketli engel yok, kafa servosu modeli ile Beyin'in servo modeli aynı hız tablosundan. Sonar
idealleştirilmiş (dar koni, 1 cm gürültü, karışma yok).
