# gezinme: rota izleme, başsız düzenek, koridor senaryoları

## Robot ölçüleri (labirent ve keşif ajanları için; ölçüm `olcum_robot.py` -> `sonuc/robot_olculeri.json`)

Varsayılan gezinme robotu **ONERI** (öneri firmware + ön omni, küre modeli; VARSAYIM). Koridor deneyi
(`deneyler/koridor_karisiklik/ortak.py` `SURUS_VARYANTI = "ONERI"`, `kos.py` 322) bununla koştu, **ONERI-MAKARA ile
değil**; brief'teki ONERI-MAKARA varsayımı yerine deneyinki alındı. Bugünkü robot (V0) modelde dönemiyor. Çerçeve:
taban gövdesi kökeni (gövde merkezi; ayak izinin ortası), +x ileri, +y sol, açı saat yönü tersi +.

| Ne | Değer | Kaynak |
| --- | --- | --- |
| En yüksek ileri hız | **0,39 m/s** (teker azamisi, firmware kırpar; ölçülen 0,390). Gezinme varsayılan seyir 0,25 m/s | ölçüm, `teker_azami_hiz_m_s` TAHMİN |
| Dönüş hızı (yerinde) | komut tavanı **1,0 rad/s** (firmware `W_GIRIS_SINIRI`); ölçülen **0,89 rad/s** (komut 0,6 -> 0,53); 90° 1,4 s + `dur` sonrası ≈ 5,7° aşma | ölçüm, µ / tork TAHMİN |
| Yay | v 0,25 + w 1 komutu -> gerçek v 0,19 m/s, w 0,59 rad/s (yarıçap ≈ 0,32 m) | ölçüm |
| Taban ayak izi (en × boy) | çarpışma kutusu **0,523 m (y) × 0,528 m (x)**: gövde kutusu x ±0,264, y ±0,262 (etek ±0,2625 / ±0,26; CAD 520 × 525 mm). Ön omni küre modeli y ±0,279'a taşar (yalnız z < 0,125 m) | `lale.xml` `c_govde`, `c_etek` |
| Dingiller | ön / arka teker merkezi x **+0,185 / −0,185**, iz y ±0,216 | `lale.xml` |
| Dönme merkezi (yerinde) | ölçülen **x −0,180 m**, y +0,01 (arka dingilin ortası ≈ −0,185) | ölçüm, çember uydurma |
| Yerinde dönüşte süpürülen çap | arka dingil çevresinde **1,04 m** (yarıçap 0,52: ön köşe x 0,264 + 0,185, y 0,262); gövde merkezi çevresinde olsaydı 0,74 m | geometri + ölçüm (ölçülen merkezle 1,043) |
| LiDAR yeri | gövdede **x +0,190, y 0, z 0,295 m**, yaw 0 (dönme merkezinden 0,37 m önde); kör sektör [139,2°, 220,8°] + 5° pay (arkada) | `lidar_ozellik.json` |
| Odometri noktası | enkoder arka tekerde: artım arka dingil ortasının (x −0,185); konumlayıcı `odometri_noktasi_x = −0,185` | deney BENIOKU |

ONERI-MAKARA (makaralı omni) aynı ölçümde: v 0,390, yerinde w 0,90 (0,6 -> 0,53), dönme merkezi x −0,182, süpürülen
çap 1,046 m, yay w 0,62, 90° 1,40 s / aşma 5,2°: gezinme için iki model eşdeğer.

Pratik sonuç: yerinde dönüş için **dönme merkezi (arka dingil ortası) her duvardan ≥ 0,52 m + pay** uzakta olmalı.
Gövde orta hatta ve koridor boyunca bakarken arka dingil de orta hattadır: en dar koridorda (2,0 m) pay 1,0 − 0,52 =
0,48 m. Yerinde dönüşte gövde merkezi 0,18 m yarıçaplı çember çizer (180° dönüşte 0,36 m yer değiştirir).

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `izleyici.py` | `YolIzleyici` rota izleyici (saf mantık, yalnız standart kütüphane) + `on_mesafe_hesapla` |
| `duzenek.py` | `Duzenek` başsız MuJoCo düzeneği, `Kayit` / `kayit_oku`, `HedefHakemi`, `varsayilan_varyant` |
| `beyinler.py` | `OdometriBeyni` (yalnız odometri), `AbBeyni` (tek harita MCL), `KayipBeyni` (6 harita MCL + keşif), `Kesif` |
| `rota.py` | koridor çizgesi (`Cizge`), duraklar (`k5_kapi_3`, `k5_bas`, `k5_son` ...), `rota()` |
| `senaryo_ab.py`, `senaryo_kayip.py`, `senaryo_ortak.py` | senaryo koşucuları; ölçüm sonucu `sonuc/SONUC.md` |
| `canli.py` | 3B pencere katmanı (`gorunum3b.py --senaryo ab|kayip`, `--beyin modul:Sinif`) |
| `ornek_beyin.py` | `--beyin` kancası + harita katmanı örneği (odometri ızgarası; SLAM değil) |
| `olcum_robot.py` | yukarıdaki robot ölçüleri |
| `testler/` | `test_izleyici` (13, saf), `test_duzenek` (5, MuJoCo; yoksa atlanır) |

## Arayüzler

**İzleyici** (`izleyici.py`): `YolIzleyici(ayar=None)` (`IzleyiciAyar(**degis)`; alanlar dosyada, seyir 0,25 m/s,
yerinde 0,8 rad/s, ileri bakış 0,6 m, varış payı 0,05 m); `yol_ver(noktalar)` (dünya (x, y) listesi; tek nokta =
şimdiki yerden oraya, boş = bitti); `komut(poz, on_mesafe=None) -> Komut(v, w, bitti, durdu, mod, hedef, kalan_m)`.
`poz` gövde merkezi; izleme noktası dönme merkezi (arka dingil, `donme_merkezi_x` −0,185). 60°'den keskin köşede bacağa
böler, yerinde döner (histerezisli). `on_mesafe` ön yüzden (x 0,2642) engele m: < 0,30 dur (`durdu`), > 0,40 kalk,
< 0,80 yavaşla; yerinde dönüşte 0,08 m altında durur. `on_mesafe_hesapla(tarama, genislik_m)`: tarama sözleşmesinden
ön şerit (genişlik_m) mesafesi; `None` girişte `None`, şerit boşsa `inf`.

**Düzenek** (`duzenek.py`, protokolün tamamı dosya başında): `Duzenek(sahne, varyant=None, tohum=0, baslangic=None,
*, ek_engeller=(), lidar_ayar=None, sonar_acik=True)`. `sahne` ad, yol ya da sözlük; `varyant` None ise koridor_* /
labirent_* ONERI, öbürleri V0; `baslangic` None ise labirentte `labirent.start.poz`, öbürlerinde sahne `baslangic`.
`kos(beyin, sure_s, hakem=None, kayit=None, denetim_hz=20, olay=None)` -> sözlük (bitis "hakem" | "beyin" | "sure",
yol_m, temas_olay, temas_kenar, temas_sure_s, rtf, son_gercek ...). `ek_engeller` [{"tur": "daire", x, y, r}],
`engel_tasi(i, x, y)` koşu sırasında taşır. `olay(duzenek, t)` her denetim adımında çağrılır (senaryo betiği için).

**Beyin**: `adim(t, tarama, artim) -> (v, w)`; `durum() -> {"poz", "mod", "yol", "hedef", "harita", "ek"}`. Beyin yer
gerçeğini görmez. `tarama` sözleşme sözlüğü + `atlanan`, `artim_once`, `artim_sonra`; `artim` arka dingil noktasının
enkoder artımı. `mod == "bitti"` 1 s sürerse koşu biter. `beyin.izleyici` varsa `ayar.dt_s` denetim adımına ayarlanır.
`ek["cerceve"]`: "harita" (varsayılan, dünya) ya da "baslangic" (Beyin'in (0, 0, 0)'ı bırakıldığı gövde pozu; SLAM).
`harita`: {"cozunurluk_m", "orijin": (x0, y0) (izgara[0, 0] köşesi), "izgara": 2B dizi [satır = y, sütun = x]} float
0..1 (dolu olasılığı), uint8 0..255 ya da int8 −1 / 0 / 100 (bilinmeyen / boş / dolu; `kesif/` böyle verir); pencere
≥ 0,65 olan hücreleri en çok 3000 kutu olarak çizer (2 s'de bir). `cerceve` verilmezse pencere labirentte "baslangic",
öbür sahnelerde "harita" varsayar (`gorunum3b.py --cerceve` ezer). Labirentte `--beyin` kurucusuna `sahne` `labirent`
alanı çıkarılmış verilir, `baslangic` verilmez (ön bilgi yok). Sınandı: `kesif.beyin:KesifBeyni` labirent_5x5_t1'de
pencerede 31 s, harita duvarlarla çakışıyor, tahmin − gerçek ≈ 0,07 m.

**Hakem**: `guncelle(t, gercek_poz, temas_var)`, `.bitti`, `.sonuc`. Labirent hakemi (`labirent/hakem.py`) doğrudan
takılır (sınandı: `test_labirent_start_ve_hakem`). Temas olayı labirent hakemiyle aynı kuralla sayılır: 1 s içinde
yeniden başlayan temas aynı olay (`temas_olay`); ham başlangıç sayısı `temas_kenar`.

## Kayıt biçimi (`.npz`, `kayit_oku(yol) -> (meta, diziler)`)

Satır başına (denetim adımı): `t` (N), `gercek` (N×3, gövde merkezi x, y, th), `odo` (N×3, odometri; arka dingil
artımı gövde merkezine çevrilmiş), `tahmin` (N×3, Beyin `poz`; yoksa NaN), `komut` (N×2 v, w), `olculen` (N×2, gerçek
v, w, `dunya.hiz()` yer gerçeği), `temas` (uint8), `mod` (int16; ad listesi `meta["modlar"]`), `hedef` (N×2). Taramalar: `tarama_t`,
`tarama_mm` (uint16 mm, 0 = ölçüm yok), `acilar`. Haritalar: `harita_<i>` (2 s'de bir), `meta["haritalar"]` zaman,
çözünürlük, orijin. Meta (npz içinde `meta` JSON): surum, sahne, varyant, tohum, baslangic, denetim_hz, montaj, yollar
(her değişen rota [t, noktalar]), ek_engeller, sonuc.

## Komutlar (`cd kod\fizik`, `%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe`)

```
%V% gezinme\senaryo_ab.py --koridor koridor_3 --hedef kapi_8 --tohum 1 --kayit gezinme/kayit/ab.npz       # tek koşu
%V% gezinme\senaryo_ab.py --engel                                                   # insan engeli demosu
%V% gezinme\senaryo_kayip.py --koridor koridor_5 --birak 1 --kayit gezinme/kayit/kayip.npz
%V% gezinme\senaryo_ab.py --olcum        &  %V% gezinme\senaryo_kayip.py --olcum   # 36 + 30 koşu, kaldığı yerden sürer
%V% -m unittest gezinme.testler.test_izleyici gezinme.testler.test_duzenek
kod\gezinme-ab.bat koridor_3     kod\gezinme-kayip.bat koridor_5     kod\simulasyon3b.bat labirent_9x9_t1 --beyin modul:Sinif
```

Ağır betikler `_yol.dusuk_oncelik()` çağırır (BELOW_NORMAL, OMP / OpenBLAS / MKL 1 iş parçacığı). İlerleme
`.durum`, ham sonuç `sonuc/ham/`, kayıtlar `kayit/` (üçü de depoya girmez).

## Sınırlar

- Sahne haritası ile konumlayıcı haritası aynı: konum hatası gerçek donanıma göre iyimser (`sonuc/SONUC.md`).
- Engelde yalnız durup bekler; dolaşma yok. Rota koridor çizgesinden; serbest alan planlayıcısı yok.
- Kayıp senaryosunda ilk küresel MCL güncellemesi ≈ 2 s: pencere açılışta bir kez donar.
- Robot modeli ONERI (VARSAYIM): bugünkü robot (V0) modelde dönemiyor; sayılar öneri firmware + ön omni içindir.
