# Dolanma tanısı (v2, MuJoCo, 1800 s kural dışı kayıtlar)

Kaynak: `sonuc/ham/mujoco_uzatilmis_v2/*.npz`. Araçlar:
- `kesif.tani_dolanma`: yeni hücreye girilmeyen en uzun aralık, o aralıktaki sınır listesi (kayıttaki `ek`, 2 s
  aralık), yer gerçeğiyle sınıflanmış.
- `sonuc/ham/finish_sinir.py`: FINISH ağzındaki sınırın ilk görülme anı ve sırası.
- `sonuc/ham/zaman_cizelge.py`: seçilen hedeflerin zaman çizelgesi.
- `sonuc/ham/mj_dis_bak.py`: kaydı SLAM'e yeniden oynatıp sınırların dönüşsüz ışın oranını (`dis`) ölçer.
- `sonuc/ham/sinir_dis_bak.py`: aynı ölçüm 2B'de.

Yer gerçeği yalnız ölçüm içindir; beyin görmez.

## Dolanma aralığı (yeni hücresiz en uzun süre)

| labirent | durum | aralık (s) | aralıkta yürünen | sınır sayısı (min–maks) | sınıf: gerçek / sahte / dış-FINISH | hedef değişimi (varmadan) | hedefin yol uzaklığı ort / maks (m) | plan sınırsız / yol_yok / kara liste | START kesme |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17x17_t3 | fail_sikisma | 1438–1738 (300) | 47,6 m | 4–5 | 576 / 0 / 146 | 1 (1) | 85 / 101 | 0 / 0 / 0 | 0 |
| 17x17_t5 | fail_sikisma | 1400–1700 (300) | 59,9 m | 3–5 | 442 / 0 / 0 | 1 (1) | 41 / 71 | 0 / 0 / 1 | 0 |
| 13x13_t2 | fail_sikisma | 778–1078 (300) | 57,6 m | 2–3 | 296 / 0 / 0 | 1 (0) | 36 / 65 | 0 / 0 / 0 | 0 |
| 17x17_t4 | başarı 1690 s | 797–952 (155) | 29,5 m | 1–2 | 78 / 0 / 0 | 1 (0) | 20 / 35 | 0 / 0 / 0 | 0 |

## Neden payları

Aday nedenlerin dördü veride yok:

- **Hedef değiştirme (gidip gelme):** yok. Aralık başına 1 hedef değişimi var; varmadan bırakılan 0–1.
- **Ulaşılamayan sınır:** yok. Planın sınırsız kaldığı an 0, `yol_yok` 0, kara liste 0–1.
- **Sahte sınır:** yok. Aralıktaki 1538 sınır örneğinin tamamı robotun girmediği hücrelerde ya da FINISH ağzında.
- **Sınır kalmadı ama çıkış bulunamadı:** yok. Her an 2–5 sınır vardı.
- **START koruması:** yok. `start_kesme` 0. START ötesindeki açık sınır yasak bölgede kalıyor; bu doğru davranış.

**Baskın neden (dört koşunun dördünde): kalan sınırlar arasında uzun yol.** Seçilen hedefin yol uzaklığı ortalama
36–85 m, en çok 101 m. Robot ölçülen ~0,2 m/s ile 300 s'de 48–60 m yürüyor; yeni hücreye girmeden hedefe varamıyor,
hakemin "300 s yeni hücresiz" kuralı doluyor.

**Uzun yolun kökü: FINISH ağzındaki sınır çok önce görülmüş, daha yakın sınır seçilip bırakılmış.**

| labirent | FINISH sınırı ilk görülme | o an maliyet / seçilen sınırın maliyeti | robotun sonra FINISH'e en yakın gelişi | `dis` (yeniden oynatma) |
| --- | --- | --- | --- | --- |
| 17x17_t3 | 651 s (robot FINISH'e 3 hücre) | 3,1 / 0,3 | 3,46 m (1738 s'ye dek) | 1,0 (sınır boyu 2,5 m) |
| 13x13_t2 | 321 s (robot FINISH'e 3 hücre) | 2,0–4,9 / 0,5–1,1 | 2,85 m | 0,0 (boy 1,1 m) |
| 17x17_t4 | 981 s | 5,7 / — | başarı 1690 s | 0,0 |
| 17x17_t5 | 927 s (tek örnek) | 3,5 / — | 3,24 m | görülmedi |
| 17x17_t2 (başarılı) | 511 s | 3,9 | başarı 615 s | 1,0 |

Bırakılan sınırın maliyeti sonra 40–105 m'ye büyüdü. 17x17_t3'te hedef zinciri 800 s boyunca kuzeye ilerledi.
Açgözlü "en yakın sınır" seçimi derin bir dala girip FINISH'i sona bıraktı.

`dis ≥ 0,3` (sınır hücrelerinin en az %30'unda ışın dönmüyor; önü sensör menzili ötesine açık) beynin izinli alanında
yalnız FINISH ağzında görüldü:

- 2B, 13x13_t2 ve 17x17_t3: 2198 FINISH dışı örneğin hiçbirinde yok; FINISH örneklerinin 20/47'sinde var.
- MuJoCo yeniden oynatma (17x17_t2, t3, t4, t5, t7 ve 13x13_t2): FINISH dışı açık sınırlar yalnız START çizgisinin
  ötesinde. Beyin orayı yasak bölge sayıyor.
- 17x17_t3 ve t2'de FINISH sınırı `dis` 1,0 ile görüldü. 13x13_t2, t4 ve t7'de 0,0: dış alan dar açıyla, yakından
  görünüyor.

**Düzeltme (v3, en küçük değişiklik):** dışa açık sınırın maliyeti 25 m düşer; görülen yer 1,5 m yarıçapla
hatırlanır, çünkü `dis` görüş açısıyla titriyor. Izgara, dik açı, hücre boyu ya da labirent bilgisi kullanılmaz.
START koruması aynen kalır.

Beklenen etki: 17x17_t3 tipini düzeltir. 13x13_t2 tipini (FINISH sınırı `dis` 0) düzeltmez.
