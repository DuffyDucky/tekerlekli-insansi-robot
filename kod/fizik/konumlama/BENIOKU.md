# konumlama: 2B LiDAR ile "hangi haritadayım, neresindeyim"

Çok haritalı küresel konumlama (parçacık filtresi, MCL). Durum = (harita, x, y, θ). Koridor deneyinin "karar veren"
kısmı: 6 koridor haritası arasında LiDAR'ın ne zaman, ne kadar yanıldığını ölçmek için. Yalnız **numpy + standart
kitaplık**; MuJoCo'ya bağlı değil (Pi'de de koşar). numpy 2.5.5 (sanal ortam) ve 2.3.5 (sistem `py -3`) ile sınandı.

    py -3 kod\fizik\konumlama\kos.py            # testler (≈ 80 s), sonda ölçüm tablosu
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
| `testler/`, `kos.py` | 21 test (ışın, uçtan uca, simetri, süre, gerçek dosyalarla duman) |

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
- `mcl.baslat()` küresel yeniden başlatma; `mcl.baslat_poz(harita, x, y, θ)` bilinen başlangıç (izleme).
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
4. **Yeniden örnekleme harita içinde.** Her haritanın toplam ağırlığı korunur, parçacık sayısı olasılığa göre ama
   en az N/K × 0,10 dağıtılır. Böylece harita olasılığı yeniden örneklemenin rastgele kaymasından etkilenmez ve hiçbir
   harita hipotezi ölmez. Harita olasılığı 1e-6'nın altına inmez (geri dönüş olanağı).
5. **Tükenmeye karşı.** Artırılmış MCL: ışın başına ortalama log-olasılığın hızlı ortalaması yavaşın altına düşünce
   her haritada %10'a kadar parçacık serbest alana rastgele saçılır. Duvar içine giden parçacığa −8 log ceza.
6. **Çıktı.** Modlar ağırlıklı kümeleme ile (0,5 m kutu, ±0,75 m, ±0,6 rad). `kararsiz = p1 − p2 < 0,5`;
   `konum_kararsiz = ana modun en iyi harita içindeki payı < 0,8 ya da xy std > 0,5 m`.

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
  kötümser); `montaj` `yaw` (rad) ya da `yaw_derece`. Kör sektördeki ışınlar atılır (dönüş yok sayılmaz); kalan
  None ışınlar "dönüş yok" kanıtıdır. `menzil_min_m` altı ve `menzil_maks_m` üstü None sayılır.
- Harita çerçevesi = dünya; robot pozu gövde merkezi. Serbest alan: yüzeylere ≥ 0,20 m ve başlangıç noktasından
  erişilebilir (`erisilebilir=False` ile kapatılır). Robot erişilemeyen bir bölgeye konursa filtre bulamaz.

## Ölçülenler (bu makine: AMD Family 25, Windows, Python 3.14, numpy 2.5.5)

| Ne | Sonuç |
| --- | --- |
| Işın izleme | analitik kare oda / daire / kutu 1e-9 m; sahte ESP32 skaler izleyicisiyle 3 haritada 6000 ışın aynı |
| `oda_engelli` (3 harita, 3 tohum) | harita ve konum ilk taramada; son hata 0,010–0,018 m / ≤ 0,06° |
| `oda_bos` | doğru harita ilk taramada; 180° simetri: 2 mod, `konum_kararsiz` doğru |
| benzer iki koridor (fark x = 17'de) | ilk 3 m'de p1 − p2 ≤ 0,26 (kararsız); karar 7,7 m yolda (fark 8 m'ye girince); son hata 0,03 m |
| insan + %5 ışın kaybı | doğru harita, son hata 0,016 m |
| kare oda (90° simetri) | 4 mod sonuna dek (0,48 / 0,19 / 0,19 / 0,13), hiçbir adımda konum kesin değil |
| ikiz harita | hiçbir adımda karar yok (en büyük p1 − p2 0,18) |
| gerçek `koridor_5` (6 koridor) | karar 10,2 m; kendinden emin yanlış harita / konum adımı 0 / 0 |
| süre, 6 koridor (359 m²) | ilk tarama (kafes) ≈ 2,5 s; adım: 1500 p 8,9 ms, **3000 p 15,7 ms** (p95 17,9), 6000 p 31,7 ms; "isin" 3000 p 234 ms |
| tek tarama sınıflaması | 4 harita ≈ 2 s; farklı odalar p ≥ 0,82, benzer koridor 0,50 / 0,50 (kararsız) |

## Sınırlar / bilinen zayıflıklar

- **2B sentetik iyimser.** Testlerin taramaları haritanın kendisinden üretiliyor (harita kusursuz, 3B etki yok, gürültü
  Gauss). MuJoCo LiDAR'ı ve gerçek sensör (siyah yüzeyde 6 m, cam, eğik geliş) daha zor olacak.
- "alan" modeli duvarın arkasını görmez (ışın ucu bir duvara yakınsa, arada başka duvar olsa da iyi sayılır); "isin"
  doğru ama 6 koridorda adım başı ~230 ms.
- Harita kanıtı parçacıkların yoğunluğuna bağlı: bir haritada iyi pozu bulan parçacık yoksa o harita haksız yere
  düşer. Kafes başlangıcı bunu ilk taramada çözüyor; sonradan kaybolan haritayı yalnız rastgele saçma kurtarır.
- `us`, `sigma_isabet`, `karar_esigi` deney sonuçlarını doğrudan etkiler (aşırı / eksik güven). Değerler 3 oda +
  6 koridorda kalibre edildi, genel değil; deney bunları tarayabilir.
- Aynı harita içinde simetrik modların payı zamanla rastgele kayar (kare odada 110 adımda 0,25 -> 0,48); çok uzun
  koşuda bir mod ölebilir. Harita payları bu kaymadan korunuyor, poz modları korunmuyor.
- İlk taramanın kafes değerlendirmesi ≈ 2,5 s (6 koridor); sonraki adımlar 10 Hz'e rahat yetişir.
