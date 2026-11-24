# Koridor karışıklık deneyi

Sanal 2B LiDAR (RPLIDAR C1 taklidi) ve çok haritalı konumlayıcı (MCL), 6 koridor arasında hangi koridorda olduğunu ne
ölçüde karıştırıyor? Benzer çift `koridor_5` / `koridor_6` (farklar yalnız `koridor_6`'da, s 15,70–17,25 m). Sonuç:
`rapor.html`.

## Sürümler

| Etiket | Konumlayıcı | LiDAR | Ham / sonuç / görsel |
| --- | --- | --- | --- |
| v1 | c34618b (düzeltme öncesi) | kör sektör var | `ham/`, `sonuc/`, `gorsel/` (tarihçe; bugünkü modülle yeniden üretilmez) |
| v2 | düzeltilmiş (`kod/fizik/konumlama/BENIOKU.md`, 24.11.2026) | kör sektör var | `ham_v2/`, `sonuc_v2/`, `gorsel_v2/` |
| v2_360 | v2 ile aynı | kör sektör yok (sanal LiDAR `kor_maske=False`, konumlayıcıda kör sektör listesi boş; gövde ışını kesmez: VARSAYIM) | `ham_v2_360/`, `sonuc_v2_360/`, `gorsel_v2_360/` |
| v3 | v2 + U dönüşü düzeltmesi (çapraz enjeksiyon yok, `odometri_noktasi_x` = −0,185 m; konumlama BENIOKU) | kör sektör var | `ham_v3/`, `sonuc_v3/`, `gorsel_v3/` |
| v3_360 | v3 ile aynı | kör sektör yok | `ham_v3_360/`, `sonuc_v3_360/`, `gorsel_v3_360/` |

v2 ve v2_360 aynı fizik koşusundan çıkar: LiDAR 360° kaydedilir, v2 taraması sanal LiDAR'ın kendi maskesi sonradan
uygulanarak elde edilir (RNG maske ne olursa olsun aynı sayıda çekildiği için maskeli taramayla birebir aynı). Her v2
sonucu v1'in yer gerçeği yolu ve v1'in sakladığı taramalarla karşılaştırılır (`v1_esitlik`, A'da `v1_farkli_isin`).
v1'in ve v2'nin ham kayıtları bütün taramaları saklamadığı için yeniden besleme yapılamadı; fizik aynı tohumlarla
yeniden koşuldu. v3'ten beri tam kayıt saklanır: `akis/<bölüm>/<id>.npz` (360° taramalar 15 mm adım sayısı olarak
uint16, enkoder odometrisi, yer gerçeği, yol, sürüş bilgisi; depoya girmez, ≈ 0,5 MB / koşu). `kos.py` kayıt varsa fizik
koşmaz, onu yeniden besler (`veri_kaynagi` alanı): sonraki konumlayıcı sürümleri aynı veriyle dakikalar içinde sınanır.

Odometri noktası: deneyin odometrisi (`lidar.DeneyKaydi`, tik toplamı, ds = (sol + sağ) / 2) arka çeker dingilin
ortasının artımıdır; konumlayıcının varsayılanı (`odometri_noktasi_x` = −0,185 m) bununla tutarlı, değiştirilmedi.
Denetim: `odometri_noktasi.py` -> `sonuc_v3/odometri_noktasi.json`.

## Nasıl koşulur

`%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe` (kurulum `kod/SIMULASYON.md` "Fizik simülasyonu").

    %V% kod\fizik\deneyler\koridor_karisiklik\kos.py --etiket v3       # bütün koşular (A, B, D, C) -> ham_v3 + ham_v3_360 (+ akis/), 8 işçi
    %V% kod\fizik\deneyler\koridor_karisiklik\kos.py --sure-dk 8       # 8 dk sonra yeni görev almaz; yeniden çağır, kaldığı yerden sürer
    %V% kod\fizik\deneyler\koridor_karisiklik\kos.py --liste           # görevler ve hangisi bitti
    %V% kod\fizik\deneyler\koridor_karisiklik\tani_ikiz.py --etiket v3 # tanı: aynı kayıt × 10 MCL tohumu + ikiz harita -> sonuc_v3/tani_ikiz.json
    %V% kod\fizik\deneyler\koridor_karisiklik\tani_donus_v3.py         # tanı: U dönüşlü 36 kayıt × 3 tohum (akis/'tan) -> sonuc_v3/tani_donus_v3.json
    %V% kod\fizik\deneyler\koridor_karisiklik\odometri_noktasi.py      # denetim: odometri artımı hangi noktanın -> sonuc_v3/odometri_noktasi.json
    py -3 kod\fizik\deneyler\koridor_karisiklik\analiz.py --etiket v3      # sonuc_v3/, gorsel_v3/ (matplotlib; sanal ortamda yok); v3_360, v2, v2_360 aynı
    py -3 kod\fizik\deneyler\koridor_karisiklik\karsilastir.py            # v1 / v2 / v2_360 / v3 / v3_360 -> sonuc_v3/karsilastirma.json, gorsel_v3/karsilastirma_*.png
    py -3 kod\fizik\deneyler\koridor_karisiklik\rapor.py                  # rapor.html (görseller gömülü, tek dosya)

`ham*/`, `akis/` ve `.durum` depoya girmez (`.gitignore`); bütün tohumlar sabit olduğundan `kos.py` aynı ham sonuçları yeniden üretir.

- Kaldığı yerden: bitmiş görev `ham_<et>/<bölüm>/<id>.json` ve `ham_<et>_360/<bölüm>/<id>.json` olarak durur ve
  yeniden koşmaz. Bir görevi yeniden koşmak için iki dosyasını da sil (fizik de yeniden koşsun istenirse `akis/`'taki
  kaydını da). Koşucu açılırken eski `.kilit` dosyalarını siler.
- İlerleme: `.durum` (10 s'de bir); işçi günlükleri `ham_<et>/isci_<n>.log`.
- İşçi: varsayılan 8, en çok 8 (`--isci`); her işçide OMP / OpenBLAS / MKL iş parçacığı 1; işçi başına ≈ 150 MB.

## Dosyalar

| Dosya | İş |
| --- | --- |
| `ortak.py` | yollar, insan yerleştirme, düzenek (`lidar.LidarDeneyi` kurulumunun kopyası + bellekte insan silindiri), saf izleme sürücüsü, kayıttan konumlayıcı akışı, MCL koşusu, ölçütler; 360° taramaya sanal LiDAR maskesini uygulama (`maskele`). v1'deki `baslat_poz_cok_harita` eki v2'de kaldırıldı (modülün `baslat_poz(..., diger_haritalar=True)`'su kullanılıyor) |
| `kos.py` | görev listesi, A (tek tarama) ve B/C/D (hareket) koşuları, işçiler, koşucu |
| `analiz.py` | `sonuc_<etiket>/*.csv`, `ozet.json`, `gorsel_<etiket>/*.png` (`--etiket v1` yalnız tarihçe içindir) |
| `karsilastir.py` | v1 / v2 / v2_360 / v3 / v3_360 karşılaştırması, iki hata türü ayrı (yanlış koridora kesin; doğru koridorda yanlış yer), kesin yanlış koşuların listesi ve gözlenen nedeni: `sonuc_v3/karsilastirma.json`, `gorsel_v3/karsilastirma_*.png` (`sonuc_v2/karsilastirma.json` v2'nin commit'li çıktısı) |
| `tani_ikiz.py` | benzer çiftte yanlış kesinliğin tanısı -> `sonuc_<et>/tani_ikiz.json` (v1: `sonuc/tani_ikiz.json`) |
| `tani_donus.py` | v2'de U dönüşünde pozun koridorun uçtan uca eşine atlaması (v2 tanısı; v3 modülünde `capraz_enjekte_oran` yok, sonucu `sonuc_v2/tani_donus.json`) |
| `tani_donus_v3.py` | v3: U dönüşlü 36 kayıt × 3 konumlayıcı tohumu, `akis/`'tan yeniden besleme -> `sonuc_v3/tani_donus_v3.json` |
| `odometri_noktasi.py` | deney odometrisinin hangi noktanın artımı olduğunu yer gerçeğiyle ölçer -> `sonuc_v3/odometri_noktasi.json` |
| `rapor.py`, `rapor_v3.py`, `metin.json` | `rapor.html`: en başta güncel durum ve dört sürümün karşılaştırması (`rapor_v3.py`, sayılar `sonuc_v3/karsilastirma.json`'dan), ardından v1 tarihçesi (`metin.json` + `sonuc/ozet.json`). v2 raporunun bölüm üreticisi `rapor_v2.py` (46a8314) yerini `rapor_v3.py`'ye bıraktı |
| `akis/A`, `akis/B`, `akis/C`, `akis/D` | tam kayıt (v3'ten beri; yeniden besleme için; depoya girmez) |
| `ham*/A`, `ham*/B`, `ham*/C`, `ham*/D` | görev başına ham sonuç (JSON; B/C/D'de adım adım olasılıklar, tahmin ve gerçek poz) |

## Deney tasarımı (özet)

| Bölüm | Ne | Koşu |
| --- | --- | --- |
| A | durağan tek tarama, `tek_taramadan_sinifla` (6 harita) | koridor başına 36 rastgele poz (orta hat boyunca katmanlı, yan ±0,3 m, yön ±10°, yarısı ters yön) + benzer çiftte her 1 m'de iki yön (92 poz) |
| B | hareket, küresel konumlama (`CokHaritaliMCL`, varsayılan ayarlar); konumlayıcıya yalnız enkoder odometrisi + tarama | 6 koridor × 3 başlangıç (`bas`, `son`, `orta`) × 5 tohum = 90 |
| C | B + haritada olmayan 3 duran insan (silindir Ø0,4 m, duvar tarafında) | 6 × 3 × 1 = 18 |
| D | bilinen başlangıç (park noktası; v2'de `baslat_poz(..., diger_haritalar=True)`), başlangıç ucundan sona | 6 × 3 tohum = 18 |

Tohumlar (hepsi sonuç dosyasında): A poz üreteci `7000 + k` (k = koridor sırası; poz tohumu `70000 + 1000·k + j`, yoğun set `90000 + ...`), LiDAR gürültüsü pozun tohumu; B/C/D
LiDAR `1000·tohum + 10·k + başlangıç`, MCL `500000 + LiDAR tohumu`, başlangıç sapması (yan ±0,10 m, yön ±3°)
`10000 + 31·tohum + 7·k + başlangıç`, insan yerleri `50000 + ...`.

Sürüş: 0,25 m/s, saf izleme (ileri bakış 0,7 m), yer gerçeğiyle; U dönüşünde yerinde döner. Robot modeli **ONERI**
(öneri firmware + ön omni, VARSAYIM): bugünkü robot (V0) modelde dönemiyor (`kod/SIMULASYON.md` "Dönüş"), L / T / U dönüşü
için Ahmet'in 23.11.2026 kararının modeli kullanıldı. A'da robot sürülmez (V0, poz doğrudan konur).

Konumlayıcı parametreleri değiştirilmedi (ayar koşusu yok).
