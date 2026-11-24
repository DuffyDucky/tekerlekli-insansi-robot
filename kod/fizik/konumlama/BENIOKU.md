# konumlama: 2B LiDAR ile "hangi haritadayım, neresindeyim"

Çok haritalı küresel konumlama (parçacık filtresi, MCL). Durum = (harita, x, y, θ). Koridor deneyinin "karar veren"
kısmı: 6 koridor haritası arasında LiDAR'ın ne zaman, ne kadar yanıldığını ölçmek için. Yalnız **numpy + standart
kitaplık**; MuJoCo'ya bağlı değil (Pi'de de koşar). numpy 2.5.5 (sanal ortam) ve 2.3.5 (sistem `py -3`) ile sınandı.

    py -3 kod\fizik\konumlama\kos.py            # testler (≈ 5 dk), sonda ölçüm tablosu
    py -3 kod\fizik\konumlama\kos.py --uzun     # + 20 tohumlu benzer çift ve MuJoCo kaydı testleri (≈ 40 dk)
    cd kod\fizik && py -3 -m konumlama.testler  # aynısı

## Dosyalar

| Dosya | İş |
| --- | --- |
| `harita2b.py` | `Harita2B`: JSON harita (biçim `kod/SIMULASYON.md` "Yeni harita"), vektörleştirilmiş ışın izleme (parça, kutu, daire), analitik uzaklık ızgarası, serbest alan (pay + başlangıçtan erişilebilirlik), log-olasılık tablosu önbelleği |
| `tarama.py` | `LidarOzellik` (`lidar_ozellik.json` ya da geçici değerler), `tarama_hazirla` (sözleşme -> dizi), `sentetik_tarama` (2B ışın izlemeyle sözleşme biçiminde tarama) |
| `olcum.py` | `OlcumParametreleri`, `log_olasilik`: karışım modeli ("alan" / "isin") |
| `hareket.py` | `HareketGurultusu`, `hizdan_artim(v, w, dt)`, `artim_birlestir`, gürültülü örnekleme |
| `mcl.py` | `CokHaritaliMCL`, `MCLAyarlari`, `Tahmin`, `karar_ani(gecmis)` |
| `sinifla.py` | `tek_taramadan_sinifla` (hareketsiz, tek tarama), `kafes_puanla` |
| `benzet.py` | `yol_uret`, `goreli`, `odometri_boz`, `yol_boyunca`, `konum_hatasi` (test + deney yardımcıları) |
| `testler/`, `kos.py` | 30 test (ışın, uçtan uca, simetri, harita kanıtı, süre, gerçek dosyalarla duman); 2'si yalnız `--uzun` ile (MuJoCo kaydı) |

## Arayüz

```python
from konumlama import CokHaritaliMCL, LidarOzellik, karar_ani, tek_taramadan_sinifla

oz = LidarOzellik.varsa_dosyadan()            # kod/fizik/lidar_ozellik.json; yoksa 12 m / 0,72° / 10 Hz / 3 cm
mcl = CokHaritaliMCL(["koridor_1", ..., "koridor_6"], ozellik=oz, tohum=42, parcacik_sayisi=3000)
for tarama, (dx, dy, dth) in akis:             # tarama = {"t", "acilar", "mesafeler"}; artım gövde çerçevesinde
    tah = mcl.guncelle(tarama, artim=(dx, dy, dth))      # ya da hiz=(v, w, dt); mcl.hareket(...) ile ayrı da verilir
    tah.olasiliklar, tah.en_olasi, tah.kararsiz, tah.fark          # harita
    tah.x, tah.y, tah.theta, tah.std_x, tah.std_y, tah.std_theta   # en olası haritadaki ana mod
    tah.konum_payi, tah.konum_kararsiz, tah.modlar                 # çok modluluk
karar_ani(mcl.gecmis, dogru_harita="koridor_3")   # {adim, t, gidilen_yol_m, ...}: kararın verilip bozulmadığı ilk adım
tek_taramadan_sinifla(haritalar, tarama, ozellik=oz)  # {olasiliklar, en_olasi, kararsiz, pozlar, ...}
```

- `haritalar`: ad (`kod/araclar/haritalar/<ad>.json`), dosya yolu, JSON sözlüğü ya da `Harita2B`. Ad tekil olmalı.
- `mcl.gecmis`: her `guncelle` çağrısında bir `Tahmin.sozluk()` (JSON'a yazılabilir). `mcl.parcaciklar()` çizim için.
- `mcl.baslat()` küresel yeniden başlatma; `mcl.baslat_poz(harita, x, y, θ, std_xy=0.2, std_theta=0.2,
  diger_haritalar=True)` bilinen başlangıç: parçacıkların çoğu verilen haritada pozun çevresinde; öbür her haritada
  en az kota (N/K × 0,10) serbest alana saçılmış, olasılıkları tabanda (1e-6). Çok haritada çalışır (c34618b'de
  IndexError veriyordu). `diger_haritalar=False`: öbür haritalar parçacıksız başlar, ilk yeniden örneklemede en az
  kotayla geri gelir; parçacıksız harita ölçülemediği taramada olasılık tabanında tutulur (ölçülmeden kazanmaz).
- Aynı `tohum` + aynı girdi = aynı sonuç (test edildi). `MCLAyarlari` alanları kurucuya anahtar sözcükle verilebilir.

## Nasıl karar verir

1. **Başlangıç (`baslangic="kafes"`).** Poz ve yön bilinmiyor: ilk tarama, *bütün* haritaların serbest alanını
   kaplayan düzenli kafeste (0,2 m × 3°, harita başına en çok 4000 nokta) geniş sigmayla (0,25 m) değerlendirilir.
   Harita olasılığı = kafes üstünde marjinal olabilirlik (eşit harita önseli); parçacıklar harita içinde bu sonsaldan
   çekilir. Rastgele saçma (`baslangic="rastgele"`) da var ama açısal havza ~0,03 rad olduğu için 3 oda testinde
   yanlış haritaya kesin karar verdi; kafes bu yüzden varsayılan.
2. **Hareket.** Odometri artımları biriktirilir, ölçümden hemen önce gürültüyle uygulanır. Ölçüm, son ölçümden beri
   ≥ 5 cm ya da ≥ 0,1 rad hareket varsa işlenir (durağan robot aynı kanıtı tekrar tekrar saymasın).
3. **Ölçüm.** 60 eşit aralıklı ışın; "alan" modeli (aşağıda). Uyarlamalı tavlama: tarama harita içi N_etkin/n'i
   0,10'un altına düşürecekse log-olasılık β < 1 ile çarpılır (`Tahmin.tavlama`).
4. **Harita olasılığı ölçüm kanıtından.** Her harita kendi bulutuyla ayrı filtre gibi yürür; harita olasılığı
   parçacık ağırlık payından değil, harita başına biriken log-kanıttan (`lz`) gelir: kafes başlangıcının marjinal
   olabilirliği + her işlenen taramada `beta × en iyi uyum`. En iyi uyum, 3 × 3 × 3 desen aramasıyla (4 tur, 4 cm /
   0,02 rad'dan yarılayarak) bulunan en büyük log-olasılık; uzaklık ızgarası çift doğrusal ara değerle okunur (poza
   göre sürekli). Arama haritanın kendi en iyi parçacığından *ve* öteki haritaların en iyi pozlarından (bu haritanın
   serbest alanındaysa, `capraz_tohum`) başlar: en büyük değer aday eklemekle bozulmaz, ama doğru poz kendi bulutunda
   ölmüşse de bulunur. Kazanan yabancı tohumun 0,1 m / 0,1 rad çevresinde haritanın parçacığı yoksa en düşük
   ağırlıklı %5'i oraya taşınır (karışım MCL'deki ikili öneri gibi; ağırlık = en iyi parçacığın önseli × kendi
   olasılıkları). Tek haritada ya da haritalar farklı çerçevedeyse etkisiz kalır.
   Yeniden örnekleme harita içindedir ve kanıtı değiştirmez; parçacık sayısı olasılığa göre, en az N/K × 0,10.
   Harita olasılığı en iyinin 1e-6 katının altına inmez (geri dönüş olanağı). Eski tahminci `harita_kaniti="ortalama"`
   ile seçilebilir (yalnız karşılaştırma için).
5. **Tükenmeye karşı.** Artırılmış MCL: ışın başına ortalama log-olasılığın hızlı ortalaması yavaşın altına düşünce
   her haritada %10'a kadar parçacık serbest alana rastgele saçılır. Duvar içine giden parçacığa −8 log ceza.
6. **Çıktı.** Modlar ağırlıklı kümeleme ile (0,5 m kutu, ±0,75 m, ±0,6 rad). `kararsiz = p1 − p2 < 0,5`;
   `konum_kararsiz = ana modun en iyi harita içindeki payı < 0,8 ya da xy std > 0,5 m`. İşlenmeyen taramada
   (eşik altı hareket) bildirilen poz ve modlar biriken odometriyle gürültüsüz ileri taşınır; parçacıklar değişmez.

## Harita kanıtı: neden değişti (24.11.2026, MuJoCo deneyi bulgusu)

Eski tahmincide (c34618b) adım artımı `log sum_i w_i L_i` idi: haritanın bulutu üzerinden ortalama olasılık. Deney
(`kod/fizik/deneyler/koridor_karisiklik`) iki birebir aynı haritada olasılığın 0,95'e çıktığını, 6 koridorda yanlış
koridora kesin karar verildiğini buldu. Aşağıdaki tanı sayıları düzeltme sırasında ölçüldü (tohum sayısı yanında) ve
sonradan yeniden koşulmadı; önce / sonra sonuçları "Ölçülenler" tablosunda 20 tohumla yeniden ölçüldü.
Kök neden ölçüldü (koridor_5 MuJoCo kaydı, [koridor_5, kopya], 3 tohum):
- Ortalama olasılık, bulut ağırlığının doğru moda düşen payıyla çarpılır. Payın kalanı takma (alias) modlarda ve
  rastgele saçılmış parçacıklardadır (ortalama %2–4, kimi adımda %90). Bu pay iki filtrede rastgele ve kalıcı olarak
  farklıdır. Adım artımı farkı ile log(doğru mod payı) farkı arasında ilinti 0,53–0,59; artım farkının öz ilintisi
  (1 adım) 0,54–0,64. Fark birikir: 320 işlenen taramada 0,6–2,2 nat (rastgele yürüyüş olsaydı ≈ 0,5).
- Aynı adımlarda en iyi parçacığın uyumu farkı std 0,001–0,002 (ortalamanınki 0,017–0,030), toplamı 0,04–0,35 nat.
- Yalnız parçacık kotasını sabitlemek çözmedi (5 tohumda en büyük p 0,75–0,93): sorun dağıtım değil tahminci.
- İkinci, küçük kaynak: en iyi uyum ilk sürümde ızgara tablosundan hesaplanıyordu. Tablo hücre başına sabit, yani
  poza göre basamaklı; iki haritanın desen araması farklı platoya takılıp adım başına ±0,033 nat fark üretiyordu
  (sentetik oda_bos ikizi, 20 tohum: en büyük p1 − p2 0,50, 6900 adımın 4'ü kesin). Uyum araması artık uzaklık
  ızgarasını çift doğrusal ara değerle okuyor (`log_olasilik(..., surekli=True)`, `Harita2B.alan_uzakligi_surekli`;
  analitik yüzey uzaklığı da denendi, aynı sonuç, adım 18 -> 51 ms). Aynı 20 tohumda en büyük p1 − p2 0,011, kesin
  adım 0 / 6900. Parçacık ağırlıkları tablodan hesaplanmaya devam ediyor.
- Üçüncü kaynak, en iyi uyumun kendi zayıflığı: kanıt, doğru pozun haritanın bulutunda yaşamasına bağlı. MuJoCo
  koridor_6 kaydı, 6 koridor, tohum 911: kafesten sonra doğru pozun çevresinde her iki haritada ≈ 29 parçacık vardı
  (koridor başı çok modlu); koridor_6'da bu küme rastgele söndü (12 parçacık 19. adımda, 0 parçacık 61. adımda),
  koridor_5'te büyüdü. Sonra koridor_6 yalnız takma pozla ölçüldü, 6 m'den önce yanlış koridora kesin karar verdi
  (912 adımın 846'sı yanlış kesin, sonda da yanlış). Çapraz tohum + enjeksiyonla aynı tohum: eşin en büyük p 0,51,
  karar 6,67 m, sonda doğru.
En iyi uyum bulutun yayılımına ve mod paylarına bağlı değil; iki harita taramayı eşit iyi açıklıyorsa artımlar
eşittir. Bedeli: yalnız en iyi pozun uyumu sayılır; harita içinde kaç pozun uyduğu (hacim / Occam terimi) yalnız
ilk taramanın kafes marjinalinde var.

## Ölçüm modeli (`OlcumParametreleri`, varsayılanlar)

| Alan | Değer | Anlam |
| --- | --- | --- |
| `model` | `"alan"` | olasılık alanı: ışın ucunun en yakın yüzeye uzaklığı d; `"isin"` beklenen menzille (yavaş) |
| `sigma_isabet` | 0,15 m | sensör ±3 cm + harita / poz hatası + 0,05 m ızgara |
| `z_isabet`, `z_rastgele` | 0,80, 0,20 | p(z) = z_isabet N(d; 0, σ) + z_rastgele / menzil_maks; tabandaki terim haritada olmayan engeli (insan, açık kapı), çoklu yansımayı karşılar |
| `z_kisa`, `lambda_kisa` | 0,10, 0,5 /m | yalnız "isin": beklenmeyen yakın engel |
| `kayip` | 0,05 | menzil içinde yüzey varken dönüş gelmemesi; None ışınlar p = kayip (yüzey bekleniyorsa) ya da 1 |
| `bos_isin_sayisi` | 12 | "alan"da None ışınlardan bu kadarı ışın izlemeyle değerlendirilir |
| `isin_sayisi` | 60 | taramadan kullanılan ışın |
| `us` | 0,3 | toplam log-olasılık çarpanı: komşu ışınlar bağımsız değil. 0,5 / σ 0,10 ile `koridor_1`'de 121 adımın 15'inde poz kendinden emin yanlıştı; 0,3 / 0,15 ile 0 |

Hareket gürültüsü (`HareketGurultusu`): ileri 0,05 m/m, yanal 0,03 m/m, dönüş 0,10 rad/rad, ileriden dönüşe
0,05 rad/m, dönüşten ileriye 0,01 m/rad, taban 5 mm / 0,005 rad. Kızak yönlendirmede dönüşte kayma ve iz farkı
(360°'de −5°) bunun içinde kalacak kadar geniş. Testlerde odometri bilerek bozuk: ileri +%3, dönüş −%1,4, ileri std
%2, dönüş std %5.

## Sözleşme ve varsayımlar

- Tarama `{"t": s, "acilar": [rad], "mesafeler": [m | None | NaN]}`; açılar gövde çerçevesinde (0 ileri, saat yönü
  tersi +), ışın kökeni `montaj` (x_m, y_m). **VARSAYIM:** `acilar` montaj yaw'unu zaten içerir ve
  `kor_sektorler_derece` aynı (gövde) çerçevededir. Sensör çerçevesinde gelirse `LidarOzellik(acilar_cerceve="sensor")`.
- `lidar_ozellik.json` alanları: `mesafe_gurultu` sayı ya da sözlük (`std_m`, `sabit_m`, ...: ±3 cm std sayılır,
  kötümser); `montaj` `yaw` (rad) ya da `yaw_derece`. `menzil_min_m` altı ve `menzil_maks_m` üstü None sayılır.
- **Kör sektör maskesi sensörle aynı.** Sanal LiDAR (`kod/fizik/lidar.py`, `LidarAyar.kor_pay_derece = 5,0`)
  dosyadaki [139,2, 220,8]'i her yana +5° genişletip [134,2, 225,8]'i maskeliyor (dosyanın "önerilen yazılım
  maskesi"). Konumlayıcı aynı payı `LidarOzellik.kor_pay_derece` (varsayılan 5,0; dosyada sayı alanı olarak varsa o)
  ile uygular; ışın seçimi maskenin dışından yapılır. Önce payı 0 kullanıyordu: seçilen 60 ışından 2'si her taramada
  sahte "dönüş yok" sayılıyordu (koridor_5 ve koridor_6 MuJoCo kayıtları, 912'şer taramanın hepsinde: 2 -> 0). Kalan None ışınlar "dönüş yok" kanıtıdır.
- **Gürültü farkı bilerek bırakıldı:** konumlayıcı 3 cm std varsayar (dosyanın ±30 mm sınırı), sanal LiDAR
  1 cm Gauss üretir (`gurultu_sigma_m = 0,010`, 3 sigma = 30 mm VARSAYIMI). Konumlayıcı bu yüzden kötümser tarafta.
- Harita çerçevesi = dünya; robot pozu gövde merkezi. Serbest alan: yüzeylere ≥ 0,20 m ve başlangıç noktasından
  erişilebilir (`erisilebilir=False` ile kapatılır). Robot erişilemeyen bir bölgeye konursa filtre bulamaz.

## Ölçülenler (bu makine: AMD Family 25, Windows, Python 3.14, numpy 2.3.5; 24.11.2026)

"c34618b" = önceki sürüm, aynı betik / tohum / kayıtla. "Fark görünür" = gerçek pozdan konumlayıcının 60 ışınından en az
birinde koridor_5 ve koridor_6 izi > 5 cm farklı (menzil içinde); c34618b'nin ışın kümesiyle 6,0 / 6,1 m.

| Ne | Sonuç |
| --- | --- |
| Işın izleme | analitik kare oda / daire / kutu 1e-9 m; sahte ESP32 skaler izleyicisiyle 3 haritada 6000 ışın aynı |
| `oda_engelli` (3 harita, 3 tohum) | harita ve konum ilk taramada; son hata 0,010–0,018 m / ≤ 0,06° |
| `oda_bos` | doğru harita ilk taramada; 180° simetri: 2 mod, `konum_kararsiz` doğru |
| benzer iki koridor (sentetik A/B, fark x = 17'de; 1 tohum) | ilk 3 m'de p1 − p2 0,003 (kararsız); karar 7,72 m yolda; son hata 0,029 m |
| insan + %5 ışın kaybı | doğru harita, son hata 0,016 m |
| kare oda (90° simetri) | 4 mod sonuna dek (0,48 / 0,19 / 0,19 / 0,13), hiçbir adımda konum kesin değil |
| ikiz harita (oda_bos × 2, kısa yol, 1 tohum) | hiçbir adımda karar yok (en büyük p1 − p2 0,006) |
| ikiz harita (oda_bos × 2, ≈ 26 m / 345 tarama, 20 tohum) | kesin adım 0 / 6900; tohum başına en büyük p1 − p2 ort 0,006, en çok 0,011. c34618b: 5 / 20 tohumda kesin adım (136 / 6900), ort 0,39, en çok 0,68 |
| ikiz harita, MuJoCo `koridor_5` kaydı (912 tarama ≈ 22 m; [koridor_5, kopya]; 20 tohum, 901–920) | kesin adım 0 / 18240; en büyük p en çok 0,505. c34618b: 11 / 20 tohumda kesin (5827 adım), en büyük p en çok 0,996 |
| benzer çift, MuJoCo kayıtları, 6 koridor, 20 tohum (901–920), doğru = `koridor_6` | kendinden emin yanlış: 0 / 20 koşu; fark görünmeden (60 ışından biri > 5 cm, 5,0 m) hiçbir kesin adım yok; o zamana dek eşin en büyük p 0,53; karar 6,66 m (20 / 20), sonda doğru 20 / 20. c34618b: 8 / 20 koşuda yanlış kesin (hepsi fark görünmeden), 13 / 20'de fark görünmeden kesin, eşin p en çok 0,99, karar 1,36–10,46 m |
| aynısı, doğru = `koridor_5` | yanlış kesin 0 / 20; fark görünmeden (4,8 m) kesin adım yok, eşin p en çok 0,50; karar medyan 9,84 m [6,39, 9,84]; sonda doğru 20 / 20. c34618b: 7 / 20 yanlış kesin, 15 / 20'de fark görünmeden kesin, karar 0,34–12,64 m |
| benzer çift, sentetik, 16 m, 20 tohum (`--uzun`) | ilk 3,5 m p1 − p2 en çok 0,017; yanlış kesin adım 0; karar `koridor_5` medyan 12,15 m [11,78, 12,28], `koridor_6` 10,10 m [10,05, 10,22]; sonda doğru 40 / 40 |
| 6 koridor, her biri başlangıçtan 12 m, 5 tohum | karar: koridor_1 / 2 0 m, koridor_3 1,6–1,75 m, koridor_4 0,10–0,11 m (c34618b ile aynı: 0 / 0 / 1,3–1,85 / 0,10–0,11); koridor_5 12,1 m, koridor_6 10,1 m (c34618b: koridor_6'da bir tohum 1,64 m'de şansla, koridor_5'te bir tohum 72 yanlış kesin adım); yanlış kesin 0 |
| gerçek `koridor_5` testi (6 koridor, 1 tohum) | karar 6,40 m; kendinden emin yanlış harita / konum adımı 0 / 0 |
| işlenmeyen taramada poz (MuJoCo koridor_6, tohum 901, 300. adımdan sonra) | ileri hata ort −0,001 m, en geride −0,005 m (397 tarama). c34618b: ort −0,039 m, en geride −0,062 m |
| `baslat_poz` çok haritada (3 harita) | çökmüyor; her adımda doğru harita kesin, son hata 0,014 m |
| süre, 6 koridor (359 m², tek süreç, 3 tekrar) | ilk tarama (kafes) ≈ 2,5 s; adım: 1500 p 15,8–18,8 ms, **3000 p 24,0–28,0 ms** (p95 28–36), 6000 p 45–46 ms. c34618b aynı ölçümde: 9,0–9,4 / 15,5–17,4 / 31,5–35,7 ms. Fark harita başına uyum araması (≈ 108–190 poz) |
| tek tarama sınıflaması | 4 harita ≈ 2 s; farklı odalar p ≥ 0,82, benzer koridor 0,50 / 0,50 (kararsız) |

## Sınırlar / bilinen zayıflıklar

- **2B sentetik iyimser.** Testlerin taramaları haritanın kendisinden üretiliyor (harita kusursuz, 3B etki yok, gürültü
  Gauss). MuJoCo LiDAR'ı ve gerçek sensör (siyah yüzeyde 6 m, cam, eğik geliş) daha zor olacak.
- "alan" modeli duvarın arkasını görmez (ışın ucu bir duvara yakınsa, arada başka duvar olsa da iyi sayılır); "isin"
  doğru ama 6 koridorda adım başı ~230 ms.
- Harita kanıtı ("uyum") bulutun yoğunluğuna bağlı değil ama doğru pozun *yakınında* en az bir aday olmasına bağlı
  (haritanın kendi en iyi parçacığı ya da öteki haritaların en iyi pozu, ±7,5 cm / ±0,04 rad yerel arama). Haritalar
  farklı çerçevedeyse çapraz tohum işe yaramaz; kendi bulutunda doğru modu yitiren haritayı yalnız rastgele saçma
  kurtarır. Kafes başlangıcı ilk taramada bütün haritaları kaplıyor.
- "Uyum" adım başına en iyi pozun olabilirliği (profil olabilirlik), tam Bayes marjinali değil: harita içinde kaç
  pozun uyduğu (hacim) yalnız kafes başlangıcında sayılır, yerel arama odometriden küçük sapmaları (≤ 7,5 cm) affeder.
  Ölçülen durumlarda (aşağıdaki tablo) bu yanlış karara yol açmadı; geniş simetrik haritalarda sınanmadı.
- Deneyin eki `baslat_poz_cok_harita` (`kod/fizik/deneyler/koridor_karisiklik/ortak.py`) artık gereksiz: modülün
  `baslat_poz`'u aynı işi yapıyor. Ek hâlâ çalışır (öbür haritalara ikinci bir en az kota ekler, `mcl.lw`'yi
  yazar), ama harita olasılığı artık `mcl.lz`'den geldiği için `mcl.lw` ile harita payı ayarlamak etkisizdir.
- `us`, `sigma_isabet`, `karar_esigi` deney sonuçlarını doğrudan etkiler (aşırı / eksik güven). Değerler 3 oda +
  6 koridorda kalibre edildi, genel değil; deney bunları tarayabilir.
- Aynı harita içinde simetrik modların payı zamanla rastgele kayar (kare odada 110 adımda 0,25 -> 0,48); çok uzun
  koşuda bir mod ölebilir. Harita payları bu kaymadan korunuyor, poz modları korunmuyor.
- İlk taramanın kafes değerlendirmesi ≈ 2,5 s (6 koridor); sonraki adımlar 10 Hz'e rahat yetişir.
