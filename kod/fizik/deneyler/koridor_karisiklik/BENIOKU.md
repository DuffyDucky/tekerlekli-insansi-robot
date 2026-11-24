# Koridor karışıklık deneyi

Sanal 2B LiDAR (RPLIDAR C1 taklidi) ve çok haritalı konumlayıcı (MCL), 6 koridor arasında hangi koridorda olduğunu ne
ölçüde karıştırıyor? Benzer çift `koridor_5` / `koridor_6` (farklar yalnız `koridor_6`'da, s 15,70–17,25 m). Sonuç:
`rapor.html`.

## Nasıl koşulur

`%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe` (kurulum `kod/SIMULASYON.md` "Fizik simülasyonu").

    %V% kod\fizik\deneyler\koridor_karisiklik\kos.py                  # bütün koşular (A, B, D, C), 3 işçi, ≈ 30 dk
    %V% kod\fizik\deneyler\koridor_karisiklik\kos.py --sure-dk 8      # 8 dk sonra yeni görev almaz; yeniden çağır, kaldığı yerden sürer
    %V% kod\fizik\deneyler\koridor_karisiklik\kos.py --liste          # görevler ve hangisi bitti
    %V% kod\fizik\deneyler\koridor_karisiklik\tani_ikiz.py            # tanı: aynı kayıt × 10 MCL tohumu + ikiz harita (≈ 4 dk)
    py -3 kod\fizik\deneyler\koridor_karisiklik\analiz.py            # tablolar + görseller (matplotlib; sanal ortamda yok)
    py -3 kod\fizik\deneyler\koridor_karisiklik\rapor.py             # rapor.html (görseller gömülü, tek dosya; yorum metni metin.json)

Son koşu (24.11.2026): 152 görev, 3 işçiyle ≈ 26 dk; tanı ≈ 4 dk. `ham/` ≈ 18 MB JSON.
`ham/` ve `.durum` depoya girmez (`.gitignore`); bütün tohumlar sabit olduğundan `kos.py` aynı ham sonuçları yeniden üretir.

- Kaldığı yerden: bitmiş görev `ham/<bölüm>/<id>.json` olarak durur ve yeniden koşmaz. Bir görevi yeniden koşmak için
  dosyasını sil. Koşucu açılırken eski `.kilit` dosyalarını siler (yarıda kalan görev yeniden başlar).
- İlerleme: `.durum` (10 s'de bir); işçi günlükleri `ham/isci_<n>.log`.
- Bellek: işçi başına ≈ 150 MB; en çok 3 işçi (`--isci`).

## Dosyalar

| Dosya | İş |
| --- | --- |
| `ortak.py` | yollar, insan yerleştirme, düzenek (`lidar.LidarDeneyi` kurulumunun kopyası + bellekte insan silindiri), saf izleme sürücüsü, kayıttan konumlayıcı akışı, MCL koşusu, ölçütler; deney eki `baslat_poz_cok_harita` |
| `kos.py` | görev listesi, A (tek tarama) ve B/C/D (hareket) koşuları, işçiler, koşucu |
| `analiz.py` | `sonuc/*.csv`, `sonuc/ozet.json`, `gorsel/*.png` |
| `tani_ikiz.py` | benzer çiftte yanlış kesinliğin tanısı -> `sonuc/tani_ikiz.json` |
| `rapor.py`, `metin.json` | `rapor.html` (sayılar `ozet.json`'dan, yorum ve sonuç metni `metin.json`'dan) |
| `ham/A`, `ham/B`, `ham/C`, `ham/D` | görev başına ham sonuç (JSON; B/C/D'de adım adım olasılıklar, tahmin ve gerçek poz) |

## Deney tasarımı (özet)

| Bölüm | Ne | Koşu |
| --- | --- | --- |
| A | durağan tek tarama, `tek_taramadan_sinifla` (6 harita) | koridor başına 36 rastgele poz (orta hat boyunca katmanlı, yan ±0,3 m, yön ±10°, yarısı ters yön) + benzer çiftte her 1 m'de iki yön (92 poz) |
| B | hareket, küresel konumlama (`CokHaritaliMCL`, varsayılan ayarlar); konumlayıcıya yalnız enkoder odometrisi + tarama | 6 koridor × 3 başlangıç (`bas`, `son`, `orta`) × 5 tohum = 90 |
| C | B + haritada olmayan 3 duran insan (silindir Ø0,4 m, duvar tarafında) | 6 × 3 × 1 = 18 |
| D | bilinen başlangıç (park noktası, `baslat_poz`), başlangıç ucundan sona | 6 × 3 tohum = 18 |

Tohumlar (hepsi sonuç dosyasında): A pozu `70000 + 1000·k + j` (yoğun `90000 + ...`), LiDAR gürültüsü pozun tohumu; B/C/D
LiDAR `1000·tohum + 10·k + başlangıç`, MCL `500000 + LiDAR tohumu`, başlangıç sapması (yan ±0,10 m, yön ±3°)
`10000 + 31·tohum + 7·k + başlangıç`, insan yerleri `50000 + ...`.

Sürüş: 0,25 m/s, saf izleme (ileri bakış 0,7 m), yer gerçeğiyle; U dönüşünde yerinde döner. Robot modeli **ONERI**
(öneri firmware + ön omni, VARSAYIM): bugünkü robot (V0) modelde dönemiyor (`kod/SIMULASYON.md` "Dönüş"), L / T / U dönüşü
için Ahmet'in 23.11.2026 kararının modeli kullanıldı. A'da robot sürülmez (V0, poz doğrudan konur).

Konumlayıcı parametreleri değiştirilmedi (ayar koşusu yok).
