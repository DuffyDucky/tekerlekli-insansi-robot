# kesif: bilinmeyen labirentte haritalayarak çıkış arayan beyin

`kesif.beyin:KesifBeyni`, gezinme `Beyin` protokolünü uygular: `adim(t, tarama, artim) -> (v, w)` ve `durum()`.
Beyin ızgara varsaymaz. Hücre boyunu ve FINISH'in yerini bilmez. Bildiği yalnızca kurallar ve kendi başlangıcıdır:
START çizgisinin 0,45 m içindedir ve içeri bakar.

    from kesif.beyin import KesifBeyni, olustur, surum_ayari
    b = KesifBeyni()                       # ön bilgisiz, varsayılan sürüm (v3; MuJoCo labirent koşuları böyle)
    b = KesifBeyni(ayar=surum_ayari("v1")) # ilk teslim davranışı
    b = olustur("labirent_9x9_t1")         # sahneden YALNIZ START çizgisi (ön bilgisiz kurulumla aynı çizgi çıkar)

Çerçeve: başlangıç gövde merkezi (`durum()["ek"]["cerceve"] = "baslangic"`). `harita.izgara[satır = y, sütun = x]`
değerleri: −1 bilinmeyen, 0 boş, 100 dolu.

## Yöntem

| Katman | Dosya | Özet |
| --- | --- | --- |
| Izgara | `izgara.py` | 5 cm log-odds. Isabet +0,85, ıska −0,4; dolu hücreye ıska yalnız −0,1 (2 mm duvar sıyırma açısında silinmesin). Sınırlar [−2, 3,5]. Gerektikçe büyür. Hücre başına isabet ortalaması tutulur (alt-hücre duvar yeri). |
| SLAM | `slam.py`, `eslestir.py` | Odometri önseli (arka dingil artımı gövde merkezine çevrilir). Dönen tarama çarpıklığı odometri geçmişiyle giderilir. Eşleştirme: kaba ilintisel arama (±0,15 m, ±(3° + 0,15·|Δθ|)) + Gauss–Newton. Önsel bilgi matrisi koridorda yozlaşan yönü odometriye bırakır. Kalite kapısı: kötü eşleşen tarama haritaya yazılmaz. Dönüş ve ileri ölçeği çevrimiçi öğrenilir (k_don ≈ 0,88). Döngü kapatma yok. |
| Kaba harita | `planla.py` | 10 cm. Engel max-havuz + morfolojik kapama. Açıklık (pah uzaklığı) alanları. |
| Planlama | `planla.py` | İki katmanlı 4 komşulu BFS: önce açıklık ≥ 0,50 m bandı (koridor ortası), olmazsa sert sınır ≥ 0,36 m + ceza. Douglas–Peucker sadeleştirme (köşeler kavşak ortasına düşer). |
| Sınır | `sinir.py` | Boş/bilinmeyen sınır kümeleri. < 0,5 m olanlar elenir. Bakış noktası: ulaşılabilir, sınırı GÖREN (görüş hattı), açıklığı yüksek hücre. Maliyet = yol + 0,3·|Δθ| − 3·(dönüşsüz ışın oranı) − 0,5·min(1, d_START/10). Histerezis: yeni aday %30 ve 2 m daha ucuzsa değişir. |
| Çıkış tanıma | `sinir.py` | Yarıçapı 1,25 m, tamamen BİLİNEN BOŞ disk = dış alan (VARSAYIM: dışarısı koridordan belirgin geniş). Varılır ve hakem bitirmezse "sahte çıkış" listesine girer. |
| START koruması | `beyin.py` | Çizgi gerisi yasak bölge + sanal duvar (sınır ve plan görmez). Gövde merkezini çizgiye 0,30 m'den yaklaştıracak komut 0,3 s öngörüyle kesilir. |
| Sürüş | `gezinme.izleyici.YolIzleyici` | Arka dingilde saf takip; köşede yerinde dönüş. Beyin her yerinde dönüşten önce süpürmeyi haritaya karşı sınar. Sığmazsa ters yönden döner; o da sığmazsa yön boyunca ±0,6 m düz kayar. |
| Kurtarma | `beyin.py` | Önde engel > 1,5 s ya da 3 s hareketsizlik olursa (harita boşsa) 0,25 m geri çekilir. Sınır kalmazsa kademeli: gevşet → zayıf duvarları unut → 20 s sağ el duvar izleme (START sanal duvar) → yeniden sınır. |

Tabanlar (`taban.py`): `SagDuvarBeyni` (sağ el kuralı) ve `RastgeleBeyni` (rastgele tepkisel). İkisi de haritasız karar
verir. Konumu yalnızca START sanal duvarını yerinde tutmak için aynı HafifSLAM'dan alırlar; salt odometride sanal duvar
2 dakikada kayıyor, taban START'tan çıkıyordu.

## 2B benzetici (`benzet2b.py`)

Arka dingil kinematiği; hız ve ivme sınırı var, teker sınırı |v| + |w|·iz/2 ≤ 0,39. LiDAR modeli: 500 ışın, 10 Hz, dönen
tarama (saat yönünde, 0°'den başlar; tarama boyunca poz değişir), σ 10 mm gürültü, 15 mm yuvarlama, kör sektör
[134°, 226°]. Odometri: %14 dönüş fazlası, %3 dönüş std, %2 öteleme fazlası, %2 std; yerinde dönüşte yanal kayma.
Çarpışmada hareket geri alınır, odometri yarısını bildirir. Hakem: `labirent.hakem` (yer gerçeği). 900 s'lik koşu
yaklaşık 20–45 s sürer.

Bilinen farklar (MuJoCo'ya göre): tekerlek dinamiği, sürtünme ve kayma modeli yok. Çarpışma "dur ve geri al"
biçiminde, temas kuvveti yok. Işınlar 2B parçalara çizilir (yükseklik, eğim ve gövdeye çarpan ışın yok).

## Çalıştırma

    cd kod/fizik
    py -3 -m unittest kesif.testler.test_kesif -v      # 10 sınama (birim + 5x5 uçtan uca, v1, v2, v3)
    py -3 -m kesif.kos ilk | odometri | hafiza          # deney matrisi -> sonuc/*.csv (en çok 2 süreç)
    py -3 -m kesif.kos rapor                            # -> sonuc/SONUC.md
    py -3 -m kesif.ayar ara --n 16 ; py -3 -m kesif.ayar sina
    py -3 -m kesif.tani --csv sonuc/mujoco.csv --surum v1 --cikti sonuc/tani_v1.csv   # MuJoCo kaydı zaman dökümü
    set PY=%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe
    %PY% -m kesif.kos_mujoco --is 2 --surum v2 --cikti mujoco_v2.csv --kayit-dizin mujoco_v2      # geliştirme
    %PY% -m kesif.kos_mujoco --is 2 --surum v2 --kume sinama --tam labirent_13x13_t4,... --tohum 0,1 ^
        --cikti mujoco_sinama_v2.csv --kayit-dizin mujoco_sinama_v2 --hafiza                     # sınama + hafızalı

MuJoCo çıktıları: CSV koşu başına tek satır (dosya her koşuda yeniden yazılır; `--ekle` ile eklenir), sütunlar
`surum`, `kume`, `kos` (ilk / hafiza), `zaman`; `kayit` sütunu `kesif/` klasörüne göreli yol. `.npz` meta'sında
`beyin_surum`, `kume`, `kos`. `sonuc/mujoco.csv` ve `sonuc/ham/mujoco/` v1 geliştirme kaydıdır, üzerine yazılmaz.
`durum()["ek"]` v2'den beri `sinirlar` ([merkez_x, merkez_y, boy_m, bakış_x, bakış_y, maliyet], son plan),
`secilen_sinir` ve `surum` alanlarını da taşır.

## Ölçülen sonuçlar (2026-11-25)

Ayrıntı: `sonuc/SONUC.md` (CSV'lerden üretilir). Ham kayıtlar `sonuc/ham/` altında ve git dışında: MuJoCo `.npz`
kayıtları, hata görselleri ve loglar.

2B benzetici, %14 dönüş hatası, 5 tohum (başarı · başarılı koşuların ortalama süresi):

| strateji | 5x5 | 7x7 | 9x9 (3 lab.) | 13x13 (3 lab.) | 17x17 (3 lab.) |
| --- | --- | --- | --- | --- | --- |
| kesif | 5/5 · 63 s | 5/5 · 214 s | 15/15 · 244 s | 14/15 · 480 s | 13/15 · 514 s |
| sağ el | 5/5 · 189 s | 4/5 · 449 s | 5/15 · 550 s | 3/15 · 676 s | 0/15 |
| rastgele | 2/5 · 360 s | 0/5 | 0/15 | 0/15 | 0/15 |

- **Çarpma:** kesif'in 55 koşusunda toplam 2 çarpma olayı.
- **MuJoCo** (`gezinme.duzenek`, ön bilgisiz `KesifBeyni()`, 3 tohum):
  - Başarı 28/33: 5x5 3/3, 7x7 3/3, 9x9 9/9, 13x13 7/9, 17x17 6/9. Çarpma 0.
  - Aynı labirent ve tohumda 2B benzetici 31/33. MuJoCo süresi 2B'nin ortalama 1,12 katı.
  - Maks poz hatası ortalaması: MuJoCo 0,42 m, 2B 0,39 m.
  - Öğrenilen k_don ≈ 0,876; MuJoCo da yaklaşık %14 fazla dönüş bildiriyor.
- **Odometri duyarlılığı:** dönüş fazlası %0 / %14 / %25 için başarı 47/55, 52/55, 49/55. Fark tohumlar arası
  oynaklık düzeyinde; k_don öğrenmesi hatayı karşılıyor.
- **Hafızalı koşu** (3 tohum):
  - İkinci koşu süresi çözüm yolunun alt sınırına eşit (ör. 7x7: 131 s, çözüm/0,25 = 130 s).
  - Kazanç ilk koşunun ne kadar dolaştığına bağlı: 17x17_t1'de %6 (ilk koşu zaten neredeyse doğrudan), 7x7'de %43.
  - 0,39 m/s denendi: kazanç yok, 7x7'de çarpma oldu.
- **Ayar** (rastgele arama, 9 aday, 8 eğitim labirenti 7–11 hücre; amaç ort + 0,5 × en kötü %20):
  - Eğitimde J 1944 → 1994 (aday03, v_seyir 0,36).
  - Sınama kümesinde başarı 52/55 → 52/55, puan ort 1250 → 1265 (+%1,3).
  - Sonuç: **anlamlı kazanç yok**; varsayılanlar değişmedi. Aday `sonuc/ayar_en_iyi.json`'da.
- **Adım süresi** (bu PC, tek iş parçacığı):
  - Tarama adımı ortalama 9 ms; p95 16 ms (yeniden plan olan adımlar dahil); en kötü 101 ms (17x17'de plan).
  - Plan ortalama 22 ms, en kötü 89 ms.
  - MuJoCo'da tarama adımı ortalama 7,5 ms.
- **Başarısızlıklar** (2B kesif: 3 koşu):
  - 17x17_t3 (2 koşu, `fail_sure`): çözüm 131 m, 0,25 m/s'de alt sınır 525 s. Robot 152 hücre gezmişti. Harita
    sağ yarıda yaklaşık 3° dönmüş, poz hatası 0,6–1,0 m (döngü kapatma yok).
  - 13x13_t2 t0: duvar ucunda tekrarlanan `on_engel` kurtarması ve konumlanma yüzünden zaman kaybı, 900 s doldu.
  - MuJoCo'da 17x17_t3'ün üç koşusu da ve 13x13_t2'nin iki koşusu süre doldu.
- **Düzeltilen hatalar** (ölçümlerden önce):
  - Sıkışma algısı net yer değiştirmeye bakıyordu. Geri çekil + ileri döngüsünde kurtarma kendini yeniden
    tetikliyordu (MuJoCo 9x9_t2'de 40 kurtarma) ve sınırları kara listeye atıyordu. Hatalı ölçüm
    `sonuc/ham/mujoco_v0_kurtarma_hatasi.csv`'de duruyor.
  - Sağ el tabanının sağ açıklık algısı yanlıştı.
  - Rastgele taban START'tan çıkıyordu; ona da START süzgeci eklendi.
  - Benzeticinin anlık tarama kipinde yanlış poz kullanılıyordu.

## v2 (2026-11-25 gece): tanı, değişiklik, sınama

**Tanı** (`kesif.tani`, v1 MuJoCo geliştirme kayıtları, 33 koşu; `sonuc/tani_v1.csv`). Kalemler ayrık; "tekrar"
ve "çözüm dışı" kesişen kalemler:

| kalem | toplam sürenin payı |
| --- | --- |
| düz sürüş (ölçülen ort hız 0,21 m/s, komut 0,25) | %83 |
| yerinde dönüş | %11 |
| kurtarma (geri çekil, konumlan, duvar izle) | %5 |
| durup bekleme / plan | %1 |
| tekrar (önceden girilip çıkılmış hücrede) | %9 |
| çözüm yolu dışı hücrelerde | %23 |

- Başarılı koşularda yürünen yol / çözüm yolu 0,87–1,16; girilen çıkmaz kollarının hiçbiri girişten önce haritada
  tamamen görülmüş değildi ("uzaktan elenebilirdi" = 0). Sınır seçimi israf etmiyor.
- 17x17_t3 (3 başarısızlık): 900 s'nin ~767'si düz sürüş, yol/çözüm 1,33, 150 hücre gezilmiş; çözüm 131 m ve 0,21 m/s'de
  yalnız çözüm yolu 625 s. 15 dakikada darboğaz hız görünüyordu; uzatılmış ölçümde yol/çözüm 2,55 (keşif). 13x13_t2 (2 başarısızlık): yol/çözüm 2,3, tekrar 165 s, çözüm dışı 570 s;
  2B görselde FINISH bölgesi en son keşfedilen köşede kalmış (keşif sırası şansı).
- Poz hatası süreyle büyüyor (17x17_t3 t0: sürenin %25'inde en çok 0,32 m, %50'sinde 0,56 m, sonda 0,78 m).

**v2 değişikliği: hız profili** (`BeyinAyari.hiz_profili`, `surum_ayari("v2")`). Önceki 0,39 m/s denemesi (hafızalı
koşu, 7x7) neden çarptı: 2B'de çarpma anlarına bakıldı (`sonuc/ham/carpma_bak.py`). Önü 1,07 m açıkken 0,39 m/s'de
yay çizerken (w ≈ −0,13…−0,43) gövde duvar ucuna yandan sürtünüyordu; ikinci tip yerinde dönüşten ~1 s sonra, yön
oturmadan hızlanınca. Fren mesafesi (0,39²/2 = 0,08 m) sorun değildi. Bu yüzden v_hizli = 0,39 yalnız şu üçü birlikte
sağlanınca: son taramada gövde önünde 1,0 m ve gövde şeridinin her yanına +0,15 m genişlikte boşluk (gövde
çerçevesi, SLAM hatasından bağımsız); son açısal komut ≤ 0,12 rad/s; son yerinde dönüş / kurtarmadan beri ≥ 1,5 s.
Hızlıyken izleyicinin engel yavaşlama rampası 0,70 m'den başlar. Aksi hâlde v1 gibi 0,25.

2B denemeler (4 geliştirme labirenti x 2 tohum): kapısız hız profili 1 çarpma; yalnız şerit kapısı 4 çarpma; üç
kapı birlikte 0 çarpma ve ~%8 kısa süre. **Akıcı köşe** (izleyicinin köşe eşiği 100°, `surum_ayari("v2k")`, deneysel)
%15–25 kısa süre ama 8 koşuda 9 çarpma verdi; varsayılan yapılmadı. Dik açı / ızgara varsayımı hiçbir sürümde yok.

**MuJoCo sonuçları** (ön bilgisiz `KesifBeyni`, aynı tohumlar; tablolar `sonuc/SONUC.md` "v1 / v2"):

| küme | v1 başarı | v2 başarı | çarpma v1 / v2 | puan ort v1 / v2 | süre v2 / v1 (ikisi de başarılı) |
| --- | --- | --- | --- | --- | --- |
| geliştirme (11 labirent x 3 tohum) | 28/33 | 27/33 | 0 / 0 | 1152 / 1137 | ort 0,96, ortanca 0,93 (26 çift) |
| sınama (13x13_t4..t8, 17x17_t4..t8 x 2 tohum) | 14/20 | 14/20 | 0 / 0 | 909 / 921 | ort 0,95, ortanca 0,94 (14 çift) |

- Ölçülen düz sürüş hızı 0,209 → 0,228 m/s (+%9); hızlı kip sürenin yalnız ~%17'sinde açık. Kısa koridor
  bacaklarında (1,3 m hücre) önü 1 m açık ve dönüşten 1,5 s geçmiş an az.
- **Karar:** kural (sınamada başarı az değil, çarpma artmadı) sağlandı, `VARSAYILAN_SURUM = "v2"`. Kazanç küçük;
  geliştirme kümesinde v2 bir koşu az (17x17_t2 t1 süre doldu, 13x13_t2 t1 bu kez başarısız, t2 başarılı).
  `KesifBeyni()` artık v2 kurar; v1 `KesifBeyni(ayar=surum_ayari("v1"))`.
- **Kalan başarısızlıklar** (sınama, iki sürümde aynı 6 koşu: 17x17_t4, t5, t7 x 2 tohum): çözüm yolu 152–183 m.
  0,21–0,23 m/s düz hızla yalnız çözüm yolu 660–870 s. Yürünen yol / çözüm 0,92–1,22, poz hatası sonda ≤ 0,58 m;
  ama bu oran 15 dakikada KESİLEN koşulardan. **Düzeltme:** uzatılmış ölçümde (1800 s, `sonuc/SONUC.md`) 17x17_t3,
  t4, t5'te robot çözümün 1,9–2,6 katını yürüyüp bilinen bölgede dolanıyor: sorun çoğunlukla keşif, yalnız t7'de hız.
- **Hafızalı ek tur** (v2, sınama, ilk koşusu başarılı 14 koşu): 14/14 başarı, çarpma 0, kazanç ort %16
  (−%3 … %57). Uzun çözümlü labirentte ikinci koşu da hız sınırında (17x17_t8: 702 s).
- 2B (11 geliştirme labirenti x 5 tohum, `sonuc/v2_2b.csv`): v1 ve v2 52/55, çarpan koşu 2 / 2; başarılı koşu
  süresi ortalaması 13x13 480 → 439 s, 17x17 514 → 469 s, 7x7 214 → 176 s. Sınama kümesi zaman dökümü
  `sonuc/tani_sinama_v1.csv`, `tani_sinama_v2.csv`.
- Üretici gözlemi: aynı tohumla üretilen farklı boyutlu labirentlerin START çevresi aynı (geri izleme aynı sırayla
  oyar). Rastgele ve sağ el tabanlarının `t1` labirentlerinde boyuttan bağımsız birebir aynı sonuç vermesi bundan:
  erken takılan koşu yalnız ortak bölgeyi görüyor. Hata değil; sınama kümesinde 13x13_tN ile 17x17_tN de START
  çevresini paylaşır.

**Sıradaki en büyük kaldıraç** (ölçülmedi): köşelerde dur–dön–kalk yerine güvenli yay ya da daha hızlı yerinde dönüş.
Akıcı köşenin ilk biçimi çarptı; yay sığma denetimi (süpürme haritaya karşı) eklenmeden açılmamalı.

## v3 (2026-11-25 öğle): dolanma tanısı ve dışa açık sınır önceliği

**Tanı** (`sonuc/tani_dolanma.md`, `kesif.tani_dolanma`; v2'nin kural dışı 1800 s kayıtları). Dolanan dört koşunun
(17x17_t3, t4, t5, 13x13_t2) en uzun "yeni hücresiz" aralığında aday nedenlerin dördü yok:
- gidip gelme yok: aralık başına 1 hedef değişimi;
- ulaşılamayan sınır yok: plan sınırsız 0, `yol_yok` 0, kara liste 0–1;
- sahte sınır yok: 1538 sınır örneğinin 0'ı;
- sınır tükenmesi yok: her an 2–5 sınır;
- START kesmesi yok: 0.

Baskın neden kalan sınırlar arasında uzun yol. Hedefin yol uzaklığı ortalama 36–85 m, en çok 101 m; 0,2 m/s ile
300 s'de varılamıyor. Kökü: FINISH ağzındaki sınır çok önce görülmüştü (17x17_t3: 651 s, robot 3 hücre ötede,
maliyet 3,1). Daha yakın sınır seçildi (0,3), robot 800 s başka dallarda kaldı.

Dönüşsüz ışın oranı ≥ 0,3 olan sınır, beynin izinli alanında yalnız FINISH ağzında görüldü:
- 2B: 2198 FINISH dışı örnekte 0.
- MuJoCo yeniden oynatma: yalnız START ötesinde, orası yasak bölge.

**Değişiklik** (`surum_ayari("v3")` = v2 + `disa_acik_bonus_m = 25`): böyle bir sınırın maliyeti 25 m düşer, yeri
1,5 m yarıçapla hatırlanır (`dis` görüş açısıyla titriyor). `durum()["ek"]["disa_acik"]` listesi eklendi. v1 / v2
birebir aynı: bonus 0, testle denetleniyor. Izgara, dik açı, hücre boyu ya da labirent bilgisi kullanılmaz; START
koruması aynen kalır.

**Sonuçlar** (MuJoCo, 900 s; tablo `sonuc/SONUC.md` "v2 / v3"):

| küme | v2 | v3 | çarpma v2 / v3 |
| --- | --- | --- | --- |
| geliştirme (eski 33 + 17x17_t4, t5 x 2) | 27/37 | 30/37 | 0 / 0 |
| sınama2 (13x13_t9..t13, 17x17_t9..t13 x 2) | 15/20 | 15/20 | 0 / 0 |
| uzatılmış (kural dışı 1800 s, 9 koşu) | 6/9, fail_sikisma 3 | 7/9, fail_sikisma 2 | 0 / 0 |

- Geliştirme: 17x17_t3 üç tohumda da çözüldü (900 s → 668–710 s; yol / çözüm 1,39 → 1,07). 17x17_t2 %13 kısa.
  Başka hiçbir koşu değişmedi.
- Sınama2'de fark yok: başarılar aynı, ortanca süre aynı (731 s), puan ortalaması 958 / 958.
- 2B (21 labirent x 2 tohum): ikisi de 38/42, çarpma aynı. 13x13_t4 %43, 17x17_t2 %13 kısa.
- **Karar:** kural (sınama2'de başarı az değil, çarpma artmadı) sağlandı, `VARSAYILAN_SURUM = "v3"`.
  Sınama2 kazanç göstermedi; kazanç yalnız geliştirme kümesinde. O kazanç da (27 → 30) düzeltmenin üzerinde
  tasarlandığı labirentten, 17x17_t3'ten geliyor; bu yüzden genel bir iyileşme kanıtı sayılmaz.

**Kalan başarısızlıklar:**
- **sınama2 hız sınıfı** (17x17_t11 x 2, t12 x 2): çözüm 165–207 m, yol / çözüm 0,85–1,03; ~0,22 m/s ile
  sığmıyor.
- **sınama2 keşif sınıfı** (17x17_t9 t1): yol / çözüm 2,3.
- **1800 s'de hâlâ dolanan** (13x13_t2, 17x17_t5): FINISH sınırı dar açıyla görüldüğü için `dis` 0 kalıyor; v3 bunu
  yakalamaz.

## Araştırma notuyla ayrılıklar (`planlama/labirent-kesif-arastirmasi.md`)

1. **A* + yumuşak maliyet yerine iki katmanlı BFS + DP.** Numpy'de eş maliyetli dalga cephesi, Python A* yığınından
   hem hızlı hem basit (scipy yok). Koridor ortası tercihini maliyet yerine iki eşikle sağladım: önce ≥ 0,50 m bandı,
   olmazsa ≥ 0,36 m. Ayrıca 8 değil 4 komşu: 8 komşuda yol iç köşeyi 45° kesiyordu. İzleyici 60°'den küçük köşeyi yayla
   alıp arka dingili izlediği için gövde duvar ucuna sürtüyordu (5x5'te 6 çarpma → 0).
2. **Dönüşsüz ışın boş yazımı 11,5 m değil 6 m.** Uzun boş ışınlar sıyırma açısında ince duvarları siliyordu.
3. **START durma mesafesi gövde merkezine göre (0,30 m).** Ayak izi köşelerine göre olsaydı başlangıç pozunda arka
   yüz çizgiye 0,186 m olduğu için ilk yerinde dönüş bile kesilirdi.
4. **k_don 0,88'den değil 1,0'dan öğrenilir.** Önsel değer bilinmez varsayıldı; 9x9 koşularında 0,88'e yakınsıyor.
5. **Eşleştirme kesmesi 0,30 m değil 0,15 m.** 0,30 m'de yakın ama yanlış duvar eşleşmeyi çekiyor, yön yanlılığı
   birikiyordu (9x9'da poz hatası maks 1,3 m). 0,15 m'de 0,06–0,2 m. Hücre içi duvar yeri için isabet ortalamasına
   nokta–doğru uzaklığı eklendi.
6. **Hız 0,39 m/s'ye çıkarılmadı (varsayılan 0,25).** Ayar aramasında `v_seyir` 0,22–0,39 aralığında; sonuç aşağıda.

## Zayıflıklar

- 15 dk sınırında 17x17 kaybı çoğunlukla keşif: uzatılmış ölçümde t3, t4, t5 yol / çözüm 1,9–2,6, robot bilinen
  bölgede dolanıyor (`fail_sikisma`); yalnız t7'de darboğaz hız (~0,22 m/s düz hız, çözüm 183 m).
- Döngü kapatma yok. Uzun koşuda yön yanlılığı birikir; mükemmel (döngüsüz) labirentte kabul edilebilir, döngülü
  labirentte değil.
- Çıkış tanıma "dışarısı geniş" varsayımına dayanır. FINISH dar bir koridora açılırsa beyin çıkışı tanımaz; sınır
  olarak görür ve yalnız şans eseri geçer.
- START çizgisinin boyu kurala göre bilinmiyor; ön bilgisiz kurulumda 1,3 m + 2 × 0,4 m pay varsayıldı.
- Tarama işleme Python/numpy; Pi 5'te ölçülmedi (bu makinede ortalama 5–6 ms).
