# tekrar: labirent koşularını tarayıcıda yeniden oynatan rapor

`labirent-rapor.html` tek dosyadır, çevrimdışı açılır (CDN yok, veri gömülü). Sıra: hüküm (sınama kümesi), "neden
17×17'de takılıyor" (zaman dökümü + grafik), v1/v2 ve strateji ve hafıza kıyası, oynatıcı, kural dışı 30 dakikalık
ölçüm, başarısızlıklar, koridor senaryosu, dürüstlük notları.

Rapor yerelde üretilir, depoda yok (`.gitignore`); üretim için `kesif/sonuc/ham/` kayıtları gerekir, onlar da git dışıdır.

## Yeniden üretme

    py -3 kod\fizik\tekrar\uret.py                  # depo kökünden; ≈ 4–5 dk, tek süreç, tek iş parçacığı, düşük öncelik
    py -3 kod\fizik\tekrar\uret.py --butce-mb 15    # daha küçük sayfa: daha az koşu gömülür
    py -3 kod\fizik\tekrar\uret.py --lidar-hz 2     # LiDAR'ı seyrelt (koşu başına boyut düşer)

Üretici o anda diskte ne varsa onu kullanır. Son 20 s içinde değişmiş (yazılıyor olabilecek) ya da okunamayan kayıt
atlanır ve raporun "Bu raporun kendi sınırları" listesinde adıyla yazılır. Sonuç dosyası yoksa ilgili kutu "henüz yok"
der. İlerleme `.durum` dosyasına yazılır.

## Okuduğu dosyalar (hiçbirini değiştirmez)

| Dosya | Ne için |
| --- | --- |
| `kesif/sonuc/mujoco*.csv` | MuJoCo sonuçları: `mujoco.csv` (v1, geliştirme, eski biçim), `mujoco_v2.csv`, `mujoco_sinama_v1/v2.csv`, `mujoco_uzatilmis_v2.csv`. Hüküm kutusu, tablolar, başarısızlık nedenleri |
| `kesif/sonuc/tani_*.csv` | Zaman dökümü (düz sürüş payı, ölçülen hız, çözüm yolu): "neden 17×17" bölümü |
| `kesif/sonuc/ilk.csv`, `v2_2b.csv` | 2B benzetici: strateji kıyası (v1), 2B v1/v2 satırı |
| `kesif/sonuc/odometri.csv`, `hafiza.csv` | 2B odometri duyarlılığı ve 2B hafızalı tur |
| `kesif/sonuc/ham/**/*.npz` (yolunda `mujoco` geçenler) | Oynatılan kayıtlar (`gezinme.duzenek.Kayit` biçimi) |
| `kesif/.durum` | Yalnız "uzatilmis bitti" satırı: uzatılmış ölçüm bitti mi |
| `sahneler/labirent_*.json` (`labirent` alanı), `../araclar/haritalar/*.json` | Gerçek duvarlar, START/FINISH, çözüm yolu (yalnız izleyici için) |
| `labirent/hakem.py` | Kayıttaki yer gerçeğiyle yeniden koşturulur: anlık ilerleme (p_en), çarpma, gezilen hücre, puan |
| `gezinme/kayit/*.npz`, `gezinme/sonuc/ham/<ad>.json` | Koridor senaryosu kayıtları (varsa) |

CSV'ler ekleme kipinde yazıldığı için aynı koşu (sürüm, küme, koş, labirent, tohum) iki kez varsa sonuncusu geçerli
sayılır. CSV'deki `kayit` yolu rapora girmez; kayıtlar `ham/` altına göreli adla gösterilir.

## Sürüm, küme, koş

- **Sürüm** (v1, v2): CSV `surum` sütunu > kayıt meta'sı `beyin_surum` > dosya/klasör adındaki `_v2` > v1.
  Meta'daki `surum` kayıt biçiminin sürümüdür, beyin sürümü sayılmaz.
- **Küme**: `kume` alanı (`gelistirme` / `sinama` / `uzatilmis`) > yoldaki ad > labirent tohumu (t1–t3 geliştirme,
  t4+ sınama).
- **Koş**: `kos` alanı (`ilk` / `hafiza`) > dosya adındaki `_hafiza`.
- Hüküm kutusu yalnız **sınama, v2, ilk koşu** satırlarından. Geliştirme kümesi ayrı kartta. Uzatılmış (30 dk)
  koşular hiçbir 15 dakikalık sayıya girmez; kendi bölümü ve "kural dışı: 30 dk" rozeti var, oynatıcıda süre
  "/ 30:00" ve 15:00 anı işaretli.

## Hangi kayıtlar gömülür (boyut ≤ `--butce-mb`, varsayılan 19 MB)

Öncelik: (0) sınama v2'nin tamamı (ilk + hafızalı), tüm başarısızlar, tüm uzatılmışlar, her boyuttan bir v2
geliştirme başarısı (ortanca süreli); (1) v1'in v2'den farklı sonuç verdiği koşular ve eşleri; (2) bu temsilcilerin
v1 eşleri; (3) kalan v2; (4) kalan v1. Zorunlular sığmazsa LiDAR sıklığı yarıya iner; sonra öncelik sırasıyla,
aynı labirentten az olan önce, bütçe dolana dek eklenir. Dışarıda kalanlar sayfada listelenir; sayıları tablolarda.

## Çizim ve sıkıştırma

- Pozlar 20 Hz'ten 10 Hz'e seyreltilir (çarpma bayrağı pencerede en büyük), mm / mrad tamsayı, fark kodlu, zlib.
- Robotun haritası (5 cm log-odds, 2 s'de bir) ortak bir çerçevede 10 cm'ye havuzlanır (2×2 blokta bir dolu varsa
  dolu, yoksa bir boş varsa boş), ardışık görüntülerin XOR farkı saklanır. Tarayıcı farkları iki yöne de uygular;
  arada en yakın önceki görüntü gösterilir, ara görüntü üretilmez.
- Keşif sınırları (v2 kayıtları, `ek.sinirlar` = [merkez_x, merkez_y, boy_m, bakış_x, bakış_y, maliyet] ve
  `ek.secilen_sinir`, 2 s'de bir): daire (çap = sınır boyu), kesikli çizgi bakış noktasına; seçilen kalın.
- LiDAR 2,5 Hz'e (varsayılan; zorunlu koşular sığmazsa daha da) ve her 2. ışına seyreltilir, mesafe 5 cm adımla `uint8`. Tarama ortasındaki gerçek pozdan çizilir.
- Her koşu ayrı bir base64 + zlib bloğudur; seçilince tarayıcının `DecompressionStream`'i ile açılır.
- Beynin haritası, tahmini pozu, hedefi, planı ve sınırları başlangıç çerçevesindedir (`ek.cerceve == "baslangic"`);
  kayıttaki başlangıç pozuyla (sahnedeki `labirent.start.poz` ile aynı olduğu denetlenir) dünyaya çevrilir.

## Denetimler (üretimde)

- İlk karede robot ile hayalet arasındaki fark (tüm labirent kayıtlarında 0 cm çıkmalı).
- LiDAR zaman tabanı: yeni kayıtlarda meta `t0_dunya_s` (satır t = dünya saati − t0); eski v1 geliştirme
  kayıtlarında bu yok, noktaları gerçek duvara en iyi oturtan kayma (−1,5…+0,5 s, 0,05 s adım) seçilir (−0,65…−0,60 s,
  kayıttaki 0,61 s ile tutarlı). Nokta–duvar ortanca uzaklığı kaymasız ve kaymalı rapora yazılır.
- Yeniden koşturulan hakemin sonucu, kaydın kendi hakem sonucu ve CSV satırı karşılaştırılır; uyuşmazlık rapora yazılır.

## Tarayıcıda deneme

Koşu kimliği `<sürüm>-<küme ilk 3 harf>-<labirent>_t<tohum>[-h]`, örnek `v2-sin-17x17_t6_t0`, hafızalı
`v2-sin-17x17_t6_t0-h`, uzatılmış `v2-uza-17x17_t1_t0`.
URL parametreleri: `?kosu=v2-sin-13x13_t4_t0&t=150&hiz=64&oynat=1&tema=koyu&katman=-lidar,+cozum&yakin=1`.
`yalniz=oynatici` yalnız o bölümü gösterir (ekran görüntüsü için). `test=1` konsol hatalarını ve çizim ölçümlerini
`<pre id="test-cikti">` içine yazar:

    chrome --headless --dump-dom "file:///.../labirent-rapor.html?test=1&kosu=v2-sin-13x13_t4_t0&t=0"
    chrome --headless --window-size=1280,1500 --screenshot=x.png "file:///...?kosu=v2-sin-13x13_t4_t0&t=150&yalniz=oynatici"

Klavye: boşluk oynat/duraklat, ← → 5 s (Shift ile 30 s), Home/End.

## Sınırlar

- Yalnız MuJoCo kayıtları oynatılır; 2B benzetici koşularının kaydı yok (yalnız tablo). Strateji kıyası yalnız 2B'de.
- Dönen taramanın çarpıklığı çizimde yok. Harita 10 cm'de duvarları biraz kalın gösterir.
- Koridor senaryosunda robotun haritası kayıtta yok (harita robota verilir); insan engeli `insan_cekildi_s` anına
  kadar çizilir.
- Tarayıcı `DecompressionStream` desteklemeli (Chrome 80+, Firefox 113+, Safari 16.4+).
