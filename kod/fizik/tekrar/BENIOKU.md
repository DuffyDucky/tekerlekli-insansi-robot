# tekrar: labirent koşularını tarayıcıda yeniden oynatan rapor

`labirent-rapor.html` tek dosyadır, çevrimdışı açılır (CDN yok, veri gömülü). Üstte sonuç özeti, ortada oynatıcı,
sonra başarısızlıklar, koridor senaryosu ve dürüstlük notları.

## Yeniden üretme

    py -3 kod\fizik\tekrar\uret.py                  # depo kökünden; ≈ 75 s, tek süreç, tek iş parçacığı, düşük öncelik
    py -3 kod\fizik\tekrar\uret.py --lidar-hz 2     # dosyayı küçültmek için LiDAR'ı seyrelt

Üretici o anda diskte ne varsa onu kullanır. Son 20 s içinde değişmiş (yazılıyor olabilecek) ya da okunamayan kayıt
atlanır ve raporun "Bu raporun kendi sınırları" listesinde adıyla yazılır. Sonuç dosyası yoksa ilgili kutu "henüz yok"
der. Gömülü veri 14,5 MB bütçeyi aşarsa LiDAR sıklığı kendiliğinden yarıya indirilir. İlerleme `.durum` dosyasına yazılır.

## Okuduğu dosyalar (hiçbirini değiştirmez)

| Dosya | Ne için |
| --- | --- |
| `kesif/sonuc/mujoco*.csv` | MuJoCo özet tablosu (sürüm başına), üst kutular, başarısızlık nedenleri (beyin olayları, son mod, kurtarma) |
| `kesif/sonuc/ilk.csv` | 2B benzetici: keşif / sağ duvar / rastgele kıyası, 2B başarısızlıklar |
| `kesif/sonuc/odometri.csv`, `hafiza.csv` | 2B odometri duyarlılığı ve hafızalı ek tur |
| `kesif/sonuc/ham/**/*.npz` (yolunda `mujoco` geçenler) | Oynatılan kayıtlar (`gezinme.duzenek.Kayit` biçimi) |
| `sahneler/labirent_*.json` (`labirent` alanı), `../araclar/haritalar/*.json` | Gerçek duvarlar, START/FINISH, çözüm yolu (yalnız izleyici için) |
| `labirent/hakem.py` | Kayıttaki yer gerçeğiyle yeniden koşturulur: anlık ilerleme (p_en), çarpma, gezilen hücre, puan |
| `gezinme/kayit/*.npz`, `gezinme/sonuc/ham/<ad>.json` | Koridor senaryosu kayıtları (varsa) |

CSV'ler ekleme kipinde yazıldığı için aynı koşu (sürüm, labirent, tohum) iki kez varsa sonuncusu geçerli sayılır.
CSV'deki `kayit` yolu (tam ya da `kesif/`e göreli) rapora girmez; kayıtlar `ham/` altına göreli adla gösterilir.

## Beyin sürümü ve küme

- **Sürüm** (v1, v2 …): CSV'de `surum` / `beyin_surum` / `surum_etiket` sütunu varsa o; yoksa kayıt meta'sında
  `beyin_surum` / `surum_etiket`; yoksa dosya ya da klasör adındaki `_v2` (`mujoco_v2.csv`, `ham/mujoco_v2/`,
  `…_t0_v2.npz`); hiçbiri yoksa v1. Meta'daki `surum` kayıt biçiminin sürümüdür, beyin sürümü sayılmaz.
- **Küme**: CSV ya da meta'da `kume` (geliştirme / sınama) varsa o; yoksa labirent tohumu t1–t3 geliştirme, t4 ve
  sonrası sınama.
- Birden çok sürüm varsa üst kutular, boyut tabloları ve oynatıcı seçicisi sürüm başına ayrılır; sınama kümesi
  ayrı tabloda durur. Tek sürüm varsa sayfa sürüm etiketi göstermez. `mujoco_2b*.csv` MuJoCo sonucu sayılmaz.

## Çizim ve sıkıştırma

- Pozlar 20 Hz'ten 10 Hz'e seyreltilir (çarpma bayrağı pencerede en büyük), mm / mrad tamsayı, fark kodlu, zlib.
- Robotun haritası (5 cm log-odds, 2 s'de bir) ortak bir çerçevede 10 cm'ye havuzlanır (2×2 blokta bir dolu varsa
  dolu, yoksa bir boş varsa boş), ardışık görüntülerin XOR farkı saklanır. Tarayıcı farkları iki yöne de uygular;
  arada en yakın önceki görüntü gösterilir, ara görüntü üretilmez.
- LiDAR 5 Hz'e ve her 2. ışına seyreltilir, mesafe 5 cm adımla `uint8`. Tarama ortasındaki gerçek pozdan çizilir.
- Her koşu ayrı bir base64 + zlib bloğudur; seçilince tarayıcının `DecompressionStream`'i ile açılır.
- Beynin haritası, tahmini pozu, hedefi ve planı başlangıç çerçevesindedir (`ek.cerceve == "baslangic"`); kayıttaki
  başlangıç pozuyla (sahnedeki `labirent.start.poz` ile aynı olduğu denetlenir) dünyaya çevrilir.

## Denetimler (üretimde)

- İlk karede robot ile hayalet arasındaki fark (tüm labirent kayıtlarında 0 cm çıkmalı).
- LiDAR zaman kayması: kayıttaki `tarama_t` mutlak benzetim saatinde, satırların `t`'si koşu başından sayılıyor ve
  aradaki fark kayıtta yok. Üretici noktaları gerçek duvara en iyi oturtan kaymayı (−1,5…+0,5 s, 0,05 s adım) seçer
  ve rapora yazar (bu kayıtlarda −0,65…−0,60 s; ortanca nokta–duvar uzaklığı kaymasız 5–10 cm, kaymayla ≈ 0,8 cm).
- Yeniden koşturulan hakemin sonucu, kaydın kendi hakem sonucu ve CSV satırı karşılaştırılır; uyuşmazlık rapora yazılır.

## Tarayıcıda deneme

URL parametreleri: `?kosu=mj-9x9_t1_t0&t=150&hiz=64&oynat=1&tema=koyu&katman=-lidar,+cozum&yakin=1`.
`yalniz=oynatici` yalnız o bölümü gösterir (ekran görüntüsü için). `test=1` konsol hatalarını ve çizim ölçümlerini
`<pre id="test-cikti">` içine yazar:

    chrome --headless --dump-dom "file:///.../labirent-rapor.html?test=1&kosu=mj-9x9_t1_t0&t=0"
    chrome --headless --window-size=1280,1500 --screenshot=x.png "file:///...?kosu=mj-9x9_t1_t0&t=150&yalniz=oynatici"

Klavye: boşluk oynat/duraklat, ← → 5 s (Shift ile 30 s), Home/End.

## Sınırlar

- Yalnız MuJoCo kayıtları oynatılır; 2B benzetici koşularının kaydı yok (yalnız tablo). Strateji kıyası ve hafızalı
  tur da yalnız 2B'de var.
- Dönen taramanın çarpıklığı çizimde yok. Harita 10 cm'de duvarları biraz kalın gösterir.
- Koridor senaryosunda robotun haritası kayıtta yok (harita robota verilir); insan engeli `insan_cekildi_s` anına
  kadar çizilir.
- Tarayıcı `DecompressionStream` desteklemeli (Chrome 80+, Firefox 113+, Safari 16.4+).
