# kesif: bilinmeyen labirentte haritalayarak çıkış arayan beyin

`kesif.beyin:KesifBeyni`, gezinme `Beyin` protokolünü uygular: `adim(t, tarama, artim) -> (v, w)` ve `durum()`.
Beyin ızgara varsaymaz. Hücre boyunu ve FINISH'in yerini bilmez. Bildiği yalnızca kurallar ve kendi başlangıcıdır:
START çizgisinin 0,45 m içindedir ve içeri bakar.

    from kesif.beyin import KesifBeyni, olustur, surum_ayari
    b = KesifBeyni()                       # ön bilgisiz, varsayılan sürüm (v3: tüm MuJoCo kümelerinde çarpma 0)
    b = KesifBeyni(ayar=surum_ayari("v5")) # v4 hızı + dönüş / yay güvenliği (seçmeli; bkz. "v5")
    b = KesifBeyni(ayar=surum_ayari("v4")) # hız zarfı (seçmeli; sınama2'de 2 çarpma)
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
| Sürüş | `gezinme.izleyici.YolIzleyici` | Arka dingilde saf takip; köşede yerinde dönüş. Beyin her yerinde dönüşten önce süpürmeyi haritaya karşı sınar. Sığmazsa ters yönden döner; o da sığmazsa yön boyunca ±0,6 m düz kayar. v5: denetim robot durunca yapılır, kayma ±1,0 m aranır, hiçbiri sığmazsa önce geri çekilip yeniden planlanır; yay süpürmesi çarpıyorsa eğrilik çarpmayan en yakın değere itilir (`surus4.ZarfIzleyici`, v4'ten). |
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
    py -3 -m unittest kesif.testler.test_deneme -v     # 4 sınama (deneme zinciri: harita taşıma, hizalama)
    py -3 -m unittest kesif.testler.test_hiz4 -v       # 10 sınama (v4: fren zarfı, süpürme, hızlanma izni, 5x5)
    py -3 -m unittest kesif.testler.test_v5 -v         # 5 sınama (v5: durunca denetim, geri çekilme, yay kaçınma)
    py -3 -m kesif.rapor_v5                             # v5 bölümü (kesif.kos rapor da SONUC.md'ye ekler)
    bash sonuc/ham/v5_isler.sh sinama2|sinama4|gel_a|gel_b [surec]   # v5 MuJoCo koşuları (v5_kod kopyasından)
    py -3 -m kesif.kos v4_2b --is 2                     # v4 2B geliştirme (21 labirent x 2 tohum) -> sonuc/v4_2b.csv
    py -3 -m kesif.hiz_tani --dizin sonuc/ham/mujoco_v4 --cikti sonuc/hiz_tani_v4.csv   # hız / kip / duvar payı
    py -3 -m kesif.rapor_hiz4 [--gorsel]               # v4 bölümü (kesif.kos rapor da SONUC.md'ye ekler)
    py -3 -m kesif.kos ilk | odometri | hafiza          # deney matrisi -> sonuc/*.csv (en çok 2 süreç)
    py -3 -m kesif.kos rapor                            # -> sonuc/SONUC.md
    py -3 -m kesif.ayar ara --n 16 ; py -3 -m kesif.ayar sina
    py -3 -m kesif.tani --csv sonuc/mujoco.csv --surum v1 --cikti sonuc/tani_v1.csv   # MuJoCo kaydı zaman dökümü
    set PY=%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe
    %PY% -m kesif.kos_mujoco --is 2 --surum v2 --cikti mujoco_v2.csv --kayit-dizin mujoco_v2      # geliştirme
    %PY% -m kesif.kos_mujoco --is 2 --surum v2 --kume sinama --tam labirent_13x13_t4,... --tohum 0,1 ^
        --cikti mujoco_sinama_v2.csv --kayit-dizin mujoco_sinama_v2 --hafiza                     # sınama + hafızalı
    %PY% -m kesif.kos_deneme --is 4 --kume sinama2 --tam labirent_13x13_t9,... --tohum 0,1 --ablasyon ^
        --cikti deneme_sinama2.csv                     # deneme zinciri (HAFIZALI sınıf), en çok 4 deneme
    py -3 -m kesif.rapor_deneme [--gorsel]             # zincir bölümü (kesif.kos rapor da SONUC.md'ye ekler)

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

## Deneme zinciri (2026-11-25 akşam): başarısız denemenin haritası sonraki denemeye

**Sınıf: HAFIZALI.** Bu sayılar "ilk girişte, hiç bilgi olmadan" KPI'sıyla (v3 sınama2 15/20) karıştırılmaz. Ayrı
CSV'ler: `sonuc/deneme_gelistirme.csv`, `sonuc/deneme_sinama2.csv`. Her deneme ayrı satır; `sinif`, `kume`, `deneme_no`
sütunları var. Ayrı bölüm: `sonuc/SONUC.md` "Deneme zinciri".

**Kurulum** (`deneme.py`, `kos_deneme.py`; hakem ve puan dosyaları değişmedi):
- 1. deneme eski ilk giriş koşusunun aynısıdır. 27/27 koşu eski CSV'lerle aynı sonucu ve süreyi (±1 s) verdi.
- Başarısızlıkta (`fail_sure` / `fail_sikisma`) aynı beyin nesnesi `yeni_deneme` ile sıfırlanır:
  - Korunur: ızgara (dönüşsüz ışın sayacı dahil), v3 dışa açık sınır hafızası, sahte çıkışlar, k_don / k_il.
  - Sıfırlanır: poz START'a döner (harita çerçevesinde (0, 0, 0)), saat 0'dan başlar. Yol, hedef, kara liste,
    gevşetme kademesi, kurtarma ve izleyici de sıfırlanır.
- Yeni `Duzenek` robotu START pozuna koyar; `Hakem` 900 s'yi yeniden sayar. En çok 4 deneme yapılır.
- Yerleştirme hatası 2. denemeden başlar ve yalnız yer gerçeğinde kalır: std 3 cm ve 2°, kırpma 6 cm ve 4°.
  Beyin bu hatayı görmez.
- Beyin START'tan en umut verici bilinen sınıra gider. Ölçüt v3'ün olağan sınır maliyetidir; robot konumu START'tır.
- Yeniden hizalama (`HizalaliSLAM`): yeni denemenin ilk iki taraması robot duruyorken alınır. Bu taramalar ±0,20 m ve
  ±8° aramayla, zayıf önselle eski haritaya oturtulur. `hizala_kalan` 0 iken davranış `HafifSLAM` ile birebir aynıdır
  (test).

**Sonuç** (MuJoCo, v3):

| küme | zincir | 1. denemede | 2. | 3. | 4. | 4 denemede çözülmedi | toplam süre ortanca (çözülen) | çarpma | fail_start |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme (mujoco_v3'ün 7 başarısızı) | 7 | 0 | 2 | 5 | 0 | 0 | 2502 s | 0 / 19 deneme | 0 |
| sınama2 (13x13_t9..t13, 17x17_t9..t13 x 2) | 20 | 15 | 1 | 0 | 0 | 4 | 734 s | 1 / 33 deneme | 0 |

**Hüküm:**
- Sınama2'de hafızalı sınıf 16/20 çözdü (ilk giriş 15/20).
  - Kazanılan tek zincir 17x17_t9 t1. Keşif sınıfındaydı; 2. denemede 369 s'de çözdü, toplam 1269 s.
  - Hız sınıfı (17x17_t11, t12, ikişer tohum) 4 denemede de çözülmedi.
- Geliştirmede 7/7 çözüldü (2'si 2. denemede, 5'i 3. denemede). Toplam süre 1391–2612 s.
- START'tan çıkma 0, START kesmesi 0.
- Bir çarpma oldu (sınama2 17x17_t11 t0, 3. deneme, 74,6 s, 0,05 s temas). O an poz hatası 0,07 m'ydi; harita kayması
  değil. Kurtarmadan hemen sonra yerinde dönüş ve ardından yayda duvar ucuna sürtünme; v2'de anlatılan mekanizma.
- Haritanın büyümesi (m², deneme başına ortalama):
  - geliştirme: 256 → 95 → 108
  - sınama2 zincirleri: 268 → 64 → 23 → 31
  - 17x17_t12'de 2–4. denemelerde yalnız 0–19 m² büyüdü.

**Neden çözülmedi (sınama2'ye bakıldıktan sonra yapılan tanı; düzeltilmedi, ayar yapılmadı):**
- **Sınır sırası START'a göre.** Her deneme START'tan başladığı için en ucuz sınır, START'a en yakın olandır.
  - 17x17_t11 t1'in 2. denemesi FINISH'e çok yaklaştı (p_en 0,98). Bittiğinde FINISH'in hemen yanında iki sınır
    vardı, robota maliyetleri 2,7–2,8'di.
  - 3. deneme START'tan önce 104 m'lik, sonra 80 m'lik başka sınırlara gitti. FINISH yanındaki sınırlara hiç
    varmadı; p_en 0,78'e düştü. 4. deneme 131 m'lik bir sınıra gitti.
  - "Kaldığı yerden devam" bu maliyetle olmuyor. Sıradaki adım: önceki denemenin son hedefini ya da son konumuna
    yakın sınırı öne almak. Yeni geliştirme / sınama kümesiyle denenmeli; bu sınama kümesi artık görülmüş sayılır.
- **900 s'lik yarıçap.** Her denemede bilinen yolu yeniden yürümek gerekir; robot ~0,23 m/s düz hızla
  gidiyor. 17x17_t12'de kalan sınırlar 100 m'den uzak, deneme başına harita neredeyse büyümüyor.
- **207 m'lik labirent (17x17_t12) harita tam bilinse de ancak sınırda sığar.**
  - Bilinen haritada ölçülen tempo 3,86 / 4,23 / 4,75 s/m (en iyi / ortanca / en kötü). Kaynak: v2 sınamasının 14
    hafızalı koşusu.
  - Buna göre beklenen süre 798 / 874 / 982 s: ortancada 26 s pay var, en kötüde 82 s aşıyor. Keşfe zaman kalmıyor.
  - Yalnız 0,39 m/s ile alt sınır 530 s olurdu; ölçülen düz hız ise ~0,23 m/s.
  - 17x17_t11 (165 m) tam haritayla sığar (638–784 s). Kaybın nedeni sınır sırası.
  - Tam haritalı "kâhin" koşusu denendi ama güvenilir çalışmadı ve rapordan çıkarıldı: hafıza kipi konumlanma sonrası
    keşif kipine düşüyor.
- **Geliştirmede bir hareketsizlik** (17x17_t2 t1, 2. deneme, 359 s `fail_sikisma`): robot bir köşede yerinde
  dönemiyor (süpürme haritaya sığmıyor). Bu yüzden "konumlan" (düz kay) ile ileri sürüş arasında 60 s döndü. Harita o
  bölgede doğruydu (poz hatası 0,07 m). Bu, v3 beyninin önceden var olan bir döngüsü; zincire özgü değil.
  Dokunulmadı (v3 birebir korunur).

**Yeniden hizalama ölçümü:** 2. denemeden başlayarak her denemenin başında, aynı beyin kopyası ve aynı yerleştirmeyle
iki 10 s'lik sonda koşuldu (CSV: `sonuc/deneme_*_hizala.csv`). Geliştirmede 12, sınama2'de 13 çift var:

| küme | 0,5 s'de START poz hatası ort / maks (m): açık / kapalı | 10 s'de: açık / kapalı |
| --- | --- | --- |
| geliştirme | 0,011 / 0,030 ; 0,012 / 0,042 | 0,045 / 0,182 ; 0,070 / 0,460 |
| sınama2 | 0,004 / 0,009 ; 0,008 / 0,020 | 0,007 / 0,017 ; 0,007 / 0,019 |

- Olağan eşleştirme 3–4° yerleştirme hatasını da çoğunlukla düzeltiyor; hizalamanın ortalama etkisi küçük.
- Tek büyük fark geliştirmede görüldü: 17x17_t5 t0, 3. deneme. Hizalamasız 10 s'de 0,46 m'lik hata, hizalamayla
  0,18 m.
- Taşınan haritada uzak bölgelerin kayması (döngü kapatma yok) hizalamayla düzelmez. Poz hatası maksimumunun
  ortalaması 1. denemelerde 0,39 m. Sınama2'nin 2–4. denemelerinde 0,35–0,36 m (büyümedi). Geliştirmede 2. denemede
  0,33 m, 3. denemede 0,53 m (5 zincir; tek en büyük değer 0,78 m, 17x17_t2 t1): orada büyüdü, yine de 3. denemeler
  çözüldü.
- Küme notu: sınama2 bu hattan önce v2 / v3 kararında kullanılmıştı; başarısız 5 koşunun listesi zincir kurulurken
  biliniyordu. Zincirde sınama2'ye göre ayar yapılmadı, ama küme tam taze değil.

**Simülasyonun iyimser varsayımları:**
- Robot her denemede START'a 3 cm / 2° std hatayla konuyor; gerçek hata daha büyük olabilir.
- MuJoCo zemini düz; tekerlek kayması modeli düzeneğinki kadar.
- Denemeler arasında haritanın beyinde kalması kural gereği serbest varsayıldı (kullanıcının görev tanımı).
- Her denemede LiDAR gürültü tohumu farklı (tohum + 1000 (k − 1)).

## v4 (2026-11-25 akşam): labirentte hız (fren zarfı, ölçüye dayalı hızlanma izni, yay süpürme denetimi)

**Tanı** (`kesif.hiz_tani`, v3 MuJoCo kayıtları: geliştirme 37 + sınama2 20 koşu; `sonuc/hiz_tani_v3.csv`):
- Düz sürüş sürenin %81'i, ölçülen düz hız 0,225 m/s. Hızlı kip (v_komut > 0,26) düz sürenin yalnız %22'sinde açık.
- v2 kapılarının tek başına engellediği düz süre: 1,0 m ön şerit %71, |w| <= 0,12 %53, 1,5 s bekleme %19. Yalnız ön
  şerit %24, yalnız w %5, yalnız bekleme %0,3. Bekleme zamanlayıcısı neredeyse hiç tek başına bağlayıcı değil; asıl
  engel kısa bacaklarda 1,0 m ön şart ile saf takibin sürekli küçük düzeltmeleri.
- Düz sürenin hız dağılımı: < 0,10 m/s %12, 0,10–0,20 %20, 0,20–0,24 %9, 0,24–0,26 %38, >= 0,26 %22.
- 3471 düz parça, ortalama 1,64 m. Parça sonunda 0,10 m/s altında geçen "kuyruk" 3098 s, toplam sürenin %10'u. Neden:
  izleyicinin yumuşak varışı v <= 0,8 x kalan yol (doğrusal, köşeye üstel yaklaşım) ve doğrusal engel rampası.
- Üst sınır: her düz parça 0,39 m/s tavan, 0,5 m/s² hızlanma ve yavaşlamayla sürülseydi (yay ve eğrilik yok sayılarak)
  düz süre 25082 s yerine 16952 s olurdu: en çok %26 kazanç. Yerinde dönüş, plan ve kurtarma değişmez sayıldı.

**Değişiklik** (`surum_ayari("v4")` = v3 + `hiz_zarfi`; `surus4.py`, `beyin._hiz_ayarla_v4`):
- `ZarfIzleyici` (gezinme `YolIzleyici`'nin alt sınıfı; gezinmedeki dosya değişmedi): yumuşak varış ve engel rampası
  yerine fren zarfı. v · 0,15 s + v² / (2 · 0,5) <= kalan yol, ve aynısı ön serbest mesafe − 0,12 m dur payı için.
  Dur / kalk eşikleri aynı.
- Hızlanma izni (v_seyir 0,25 → v_hizli 0,39, sabit 1,5 s ve 1,0 m kapısı yok):
  - yön hatası ölçüsü: saf takip açısı |α| <= 0,25 rad tam hız, >= 0,50 rad v_seyir, arası doğrusal;
  - eğrilik: teker sınırı v (1 + κ · iz / 2) <= 0,39 ve |w| = v |κ| <= 0,6 rad/s;
  - süpürme denetimi: o anki w'den v · κ'ya a_w ile yaklaşan yay, fren mesafesi + 0,30 m ufukta sürülür. 5 cm şişirilmiş
    ayak izi son taramanın bir noktasını içine alırsa ya da çevresi haritada dolu / sanal (START) hücreye değerse izin yok.
- Süpürme v_seyir'de de çarpıyorsa ve |α| > 0,20 rad ise yay yerine önce yerinde hizalanma istenir (`hizala_iste`;
  dönüş süpürmesi her zamanki gibi `_donus_karar` ile sınanır).
- Izgara, dik açı, hücre boyu ya da labirent bilgisi kullanılmaz. START koruması (0,3 s öngörülü kesme, yasak bölge, sanal
  duvar) aynen kalır. v1–v3 birebir: `hiz_zarfi` kapalı, `YolIzleyici` kullanılır (test). Deneme zinciri v4'te aynı
  izleyici sınıfını yeniden kurar (`deneme.py`, tek satır; v3 yolu aynı).

**2B geliştirme** (yalnız geliştirme labirentleri; ara sürümler `sonuc/ham/` altında):
- İlk 3 labirentlik taramada α eşikleri 0,10 / 0,25 → 0,25 / 0,50 (%4–6 kısa, çarpma 0).
- Taslak 1 (hizalanmasız): ilk 20 koşuda 3 çarpma (17x17_t8). Hepsi v_seyir'de, yerinde / bakış dönüşünden hemen sonra
  α 0,3–0,4 rad ile yayla duvar ucuna sürtünme. Süpürme denetimi hızlı kipi zaten reddetmişti.
- Taslak 2 (+ süpürme çarpınca 0,12 m/s'ye yavaşla): 20 koşuda 8 çarpma; yavaş yay da aynı yere gidiyor. Bırakıldı
  (`zarf_v_yavas = 0`).
- Son sürüm (yalnız hizalanma): çarpmalı 4 labirentin 8 koşusunda 0 çarpma. Tam küme (21 x 2): v3 38/42, v4 37/42;
  çarpma olayı v3 2 (5,8 s temas), v4 1 (2,9 s; 17x17_t2 t0, o koşu süre doldu). Süre oranı v4/v3 ortanca 0,889
  (36 çift). **"2B'de çarpma 0" şartı tam sağlanmadı**; v3'ten az çarpma ile MuJoCo'ya geçildi.

**MuJoCo** (900 s, ön bilgisiz; tablolar `sonuc/SONUC.md` "v4"; çıktılar `sonuc/mujoco_v4.csv`,
`mujoco_sinama3_v3.csv`, `mujoco_sinama3_v4.csv`, `mujoco_sinama2_v4.csv`, `kume` sütunlu):

| küme | v3 | v4 | çarpma olayı v3 / v4 | temas (s) v3 / v4 | süre v4/v3 ortanca (çift) | düz hız (m/s) v3 / v4 | hızlı kip payı v3 / v4 | duvar payı < 5 mm koşu v3 / v4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme (21 labirentin MuJoCo'daki 37 koşusu) | 30/37 | 33/37 | 0 / 0 | 0 / 0 | 0,883 (30) | 0,227 / 0,275 | 0,23 / 0,70 | 0/37 / 4/37 |
| **sınama3** (YENİ: 13x13, 17x17 t14..t18 x 2) | 14/20 | **17/20** | 1 / 0 | 0,05 / 0 | 0,884 (14) | 0,223 / 0,269 | 0,21 / 0,68 | 2/20 / 3/20 |
| sınama2 (görülmüş, sonradan bakıldı) | 15/20 | 17/20 | **0 / 2** | 0 / **6,15** | 0,842 (15) | 0,221 / 0,272 | 0,21 / 0,69 | 2/20 / 3/20 |

- Kuyruk (0,10 m/s altı) geliştirmede 1771 → 357 s, sınama3'te 1306 → 314 s. v4'ün kalan üst sınırı (aynı ideal
  ivmelenmeyle) toplam sürenin %13'ü (v3'te %26).
- Puan ortalaması: geliştirme 1105 → 1199, sınama3 914 → 1042, sınama2 958 → 1062.
- **Karar:** kural (sınama3'te başarı az değil: 14 → 17; çarpma artmadı: 1 → 0) sağlandı, `VARSAYILAN_SURUM = "v4"`.
  **Sonra geri alındı** (bağımsız inceleme, "v5" bölümü): varsayılan yeniden v3. Sınama3 farkı 3 uyumsuz çiftten
  geliyor (üçü de aynı yönde, McNemar p ≈ 0,25) ve üç kazanç da 900 s sınırına çok yakın. "v4 daha iyi" anlamlı bir fark
  sayılmaz; doğru ifade "v4 sınama3'te koşu kaybettirmedi ve daha hızlı".
- **Uyarı (gerileme denetimi):** görülmüş sınama2'de v4 iki çarpma verdi, v3 hiç vermedi.
  - 17x17_t11 t1, 713 s: 0,38 m/s'den köşede durduktan sonra yerinde dönüşte (v 0, w 0,8) 6,1 s temas.
  - 17x17_t13 t0, 390 s: v_seyir'de (0,25 m/s, w −0,09) yayla duvar ucuna sürtünme, 0,05 s. Süpürme denetimi hızlı
    kipi reddetmişti; α küçük olduğu için hizalanma istenmedi.
  - Ayrıca gövde kutusunun duvar çizgisine geometrik olarak değdiği (pay < 5 mm) koşu sayısı v4'te arttı (geliştirme 0 → 4).
    MuJoCo bu anlarda temas bildirmedi.
  - Kural sınama3'e göre tanımlıydı; o yüzden sonuç değiştirilmedi. Gerçek robotta v3'e dönmek tek satır:
    `beyin.VARSAYILAN_SURUM = "v3"`.
- Sınama3'te kazanılan 3 koşunun üçü de sınıra çok yakın (13x13_t15 t0 892 s, 13x13_t17 877 / 895 s); pay ince. v4 sınama3'te
  hiçbir koşuyu kaybetmedi.
- **Hız sınıfı** (sınama2 17x17_t11, t12; sonradan bakıldı): yalnız 17x17_t12 t1 çözüldü (838 s). 17x17_t12 t0 p_en 0,85
  ile süre doldu. 17x17_t11 iki tohumda da p_en 0,60'ta kaldı, 203–205 m yürüdü: kayıp hızdan değil, sınır sırasından
  (deneme zinciri tanısıyla aynı).

**Kalan başarısızlıklar (v4, hepsi `fail_sure`):**
- geliştirme: 13x13_t2 t0, 17x17_t4 t0 ve t1, 17x17_t5 t1;
- sınama3: 13x13_t15 t1 (p_en 0,97), 17x17_t18 t0 ve t1 (çözüm 191 m, p_en 0,69);
- sınama2: 17x17_t11 x 2, 17x17_t12 t0.
Hiçbirinde START'tan çıkma ya da START kesmesi yok.

**Simülasyonun iyimser varsayımları ve kapsam:**
- Fren zarfı 0,5 m/s² yavaşlama ve 0,15 s gecikme varsayar. MuJoCo'da firmware freni 1,8 m/s²; gerçek zeminde
  kayma daha büyük olabilir.
- 2B benzeticide çarpışma "dur ve geri al" biçiminde; MuJoCo'nun temas bayrağı ile geometrik pay farklı şeyleri ölçüyor.
- Teker azamisi 0,39 m/s bir TAHMİNdir (`robot.py`). v4 düz sürenin ~%69'unda hızlı kipte (v_komut > 0,26); gerçek
  tavan düşükse v4'ün süre kazancı ve sınama3'te sınıra çok yakın kazanılan 3 koşu (877–895 s) kaybolabilir.
- Zarfın 0,15 s tepki payı tarama 10 Hz + denetim 20 Hz'den seçildi. Düzenekte Pi → ESP32 komutu bellek üzerinden
  gider; gerçek seri hat / USB gecikmesi eklenmedi. Gerçek robotta tepki payı büyürse fren zarfı daha erken kesmeli.
- Yerinde dönüş hızı değişmedi (90° ≈ 1,4 s); toplam sürenin ~%11'i.
- MuJoCo v4 koşularının hepsi (geliştirme, sınama3, sınama2) `sonuc/ham/v4_kod/` anlık kopyasından koşuldu
  (`sonuc/ham/v4_isler.sh`). Kopya 19:03'te alındı; v3'ün sınama3 sonuçları 18:56'da hazırdı. Arada görülen yalnız
  v3'ün sınama3 sonucudur (v4'ünki değil); yine de 7 dakikalık bu aralıkta kod düzenlenmiş olabilir. v3 sınama3 koşuları
  `sonuc/ham/v4_oncesi_kod/` kopyasından (v4 eklenmeden önceki kod). v4_kod ile canlı `beyin.py` / `surus4.py` aynı;
  tek fark `VARSAYILAN_SURUM` satırı (koşular `--surum v4` ile)
  (fark denetlendi).
- İşlemci: en çok 4 süreç (2 MuJoCo + 2 2B ya da 4 MuJoCo); MuJoCo gerçek zaman oranı 2,5–3,7.

## v5 (2026-11-25 gece): v4 çarpmalarının kök nedeni, dönüş / yay güvenliği

**Hüküm:** v5 iki v4 çarpmasının kök nedenini gideriyor ve YENİ sınama4'te v3 kadar koşu çözüyor (12/20, çarpma
0 / 0, süre oranı v5/v3 ortanca 0,845). Ama geliştirmede v5 yeni bir çarpma verdi (17x17_t1 t1, 0,25 s; v3 ve v4 orada
0). "Çarpma sıfır" yalnız v3'te bütün MuJoCo kümelerinde tutuyor. Bu yüzden `VARSAYILAN_SURUM = "v3"` (v4'ten geri
alındı). v4 ve v5 seçmeli.

**Tanı** (MuJoCo'da aynı tohumla yeniden koşu, beyin iç durumu adım adım; iki koşu da belirlenimci, kayıttaki çarpma
aynı anda yeniden çıktı):
- 17x17_t11 t1, 713 s (6,1 s temas). Robot 0,33 m/s ile giderken plan değişti; izleyici yerinde dönüşe geçti. Beyin
  dönüş süpürmesini robot henüz frenlerken (v 0,20) sınadı. Hiçbir dönüş ve ±0,6 m'lik hiçbir kayma sığmadı
  (`donus_sigmaz`). v1–v4'te bu durumda dönüş yine de başlıyor ("izleyiciye bırak"). Robot koridorda sol duvara
  0,09 m kalmış, sol duvar ucunun yanındaydı; sola dönerken gövde yanı duvar ucunu süpürdü. Sonradan alınmış haritayla
  0,2–0,7 m ileri kayınca sola dönüş sığıyordu. Yani v4'ün yeni bir hatası değil: v3'te de var olan "sığmıyorsa yine de
  dön" yolu, v4'ün hızında ve frenleme payında tetiklendi.
- 17x17_t13 t0, 390 s (0,05 s). v4'ün yay süpürme denetimi v_seyir'de 2,2 s boyunca çarpma öngördü. |α| 0,11–0,16 rad,
  yani donus_cik_rad (0,20) altında olduğu için hizalanma istenmedi ve başka önlem yoktu. Yol sağdaki bir duvar ucunun
  0,30 m yanından geçiyordu (gövde yanı ile 4 cm). Saf takip sağa yay çizerken sağ ön köşe duvar ucunu sıyırdı.
  Aynı taramalarda 389,0–389,5 s'de düz gitmek 2 cm payla çarpmıyordu; 390,0 s'den sonra düz de çarpıyordu.

**Değişiklik** (`surum_ayari("v5")` = v4 + dört alan; `beyin.py`, `surus4.py`; v1–v4 birebir, test var):
- `donus_durunca`: yerinde dönüş süpürmesi robot durunca (izleyici hızı ≤ 0,02 m/s) sınanır. Frenleme sırasında
  izleyici zaten w = 0 verir.
- `donus_kay_m` 0,6 → 1,0 m: dönüş sığmıyorsa düz kayma daha geniş aralıkta aranır.
- `donus_sigmaz_geri`: hiçbiri sığmıyorsa körlemesine dönmek yerine önce geri çekilip (`_kurtarma_baslat`, harita boşsa
  0,25 m) yeniden planlanır. Aynı yerde (0,3 m) 20 s içinde ikinci kez sığmazsa eski davranış: takılma güvencesi.
- `yay_kacin`: yay v_seyir'de de çarpıyorsa ve hizalanma yoksa, eğrilik κ + {0, ±0,15, ±0,3, ±0,5, ±0,8} 1/m
  arasından 3 cm payla çarpmayan en yakın değere bir adım için itilir (`ZarfIzleyici.kappa_iste`). Uygun aday yoksa
  v4 gibi sürer. Yalnız son tarama, kendi haritası ve robot ölçüleri kullanılır.

**MuJoCo** (900 s, ön bilgisiz; tablo `sonuc/SONUC.md` "v5"; `sonuc/mujoco_v5.csv`, `mujoco_sinama2_v5.csv`,
`mujoco_sinama4_v3.csv`, `mujoco_sinama4_v5.csv`, `mujoco_sinama4_v4.csv`; duvar payı `sonuc/hiz_tani_v5.csv`):

| küme | v3 | v4 | v5 | çarpma olayı v3 / v4 / v5 | süre oranı v5/v4 ortanca (çift) | süre oranı v5/v3 | duvar payı < 5 mm koşu v3 / v4 / v5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme (37 koşu) | 30/37 | 33/37 | 32/37 | 0 / 0 / **1** (0,25 s) | 0,999 (32) | 0,893 (29) | 0/37 / 4/37 / 1/37 |
| sınama2 (görülmüş; tanı burada yapıldı -> geliştirme sayılır) | 15/20 | 17/20 | 17/20 | 0 / 2 (6,15 s) / **0** | 0,981 (16) | 0,833 (15) | 2/20 / 3/20 / 2/20 |
| **sınama4** (YENİ: 13x13 / 17x17 t19..t23 x 2) | 12/20 | 12/20 | 12/20 | 0 / 0 / 0 | 0,964 (12) | 0,845 (12) | 0/20 / 5/20 / 0/20 |

- Sınama4'te v4 de çarpmadı (karşılaştırma koşusu), ama gövde kutusunun duvara 5 mm'den yaklaştığı koşu v4'te 5/20, v3 ve
  v5'te 0/20. v5 sınama4'te v4'ten de hızlı (ortanca 0,964).
- Kümeler: sınama4 bu aşamada üretildi (`labirent/uretici.py uret`, doğrulama 10/10 TAMAM,
  `sonuc/ham/sinama4_dogrula.log`). v5 kodu iki tanı koşusundan sonra donduruldu (`sonuc/ham/v5_kod/`); sınama2,
  sınama4 ve geliştirme koşularının hepsi bu kopyadan (`sonuc/ham/v5_isler.sh`). Sınama4 sonuçlarına bakıldıktan sonra
  kod değişmedi. v3 sınama4 koşuları v5 öncesi kopyadan (`sonuc/ham/v5_oncesi_kod/`). v4 sınama4 koşuları yalnız
  karşılaştırma; karardan sonra `sonuc/ham/v4_kod/` kopyasından koşuldu.
- Geliştirmenin geri kalanı (sınama4 kararından sonra, ayar yapılmadı): v5 13x13_t2 t2'yi kaybetti (v4 çözmüştü).
  Yeni çarpma 17x17_t1 t1, 262,9 s: yerinde dönüşten 1,5 s sonra v_seyir'de sola yayla (v 0,25, w 0,12–0,16) 0,25 s
  temas. v2'den bilinen "dönüşten hemen sonra yay" mekanizmasına benziyor. Yay kaçınmanın orada devreye girip girmediği
  yeniden koşu yapılmadan bilinemez; incelenmedi.
- Sınama2'de iki v4 çarpmalı koşu v5'te çarpmasız çözüldü: 17x17_t13 t0 701 s (v4 686 s), 17x17_t11 t1 791 s (v4 ve v3
  çözememişti). İkincisi bir kazanç gibi görünse de v5'in yörüngesi v4'ünkinden ayrıştığı için şans payı taşır.
- Geri çekilip yeniden planlama (`donus_sigmaz` kurtarması) 77 v5 koşusunda yalnız bir kez tetiklendi (geliştirme). Etkili
  değişiklikler durunca denetim ve yay kaçınma.
- Sınama4'teki v5 başarısızlıklarının hepsi `fail_sure` (17x17 t19 x 2, t20 x 2, t21 x 2, t23 x 2). 17x17_t20 t0'da
  716–760 s arası 7,7 s arayla 7 kez `on_engel` kurtarması var: önde engel beklemesi döngüsü (v3'ten kalan mekanizma;
  v3 aynı koşuda sıkışma ve duvar izlemeyle başka yerde kaldı). İncelenmedi.

**İstatistik:** sınama4'te v3 ile v5 aynı sayıda koşu çözüyor; fark yok. Çarpma sıfır sınama2 + sınama4'ün 40
koşusunda tutuyor, ama geliştirmenin 37 koşusunda 1 çarpma var. Bu sayılarla "v5 hiç çarpmaz" denemez.

**Simülasyonun iyimser varsayımları ve kapsam:**
- v4'ünkiler geçerli (0,39 m/s teker azamisi tahmin, 0,15 s tepki payı, seri hat gecikmesi yok).
- Yay kaçınmanın 3 cm payı ve süpürme öngörüsü son taramaya dayanır. MuJoCo'da temasın olduğu anda 2 cm payla
  öngörü "çarpmaz" diyebildi (17x17_t13 t0, 390,7 s): yandaki duvar ucu LiDAR'ın (x +0,19) gerisinde kalınca tarama onu
  eksik görüyor. Bu mm düzeyinde güvenilir bir denetim değildir.
- 2B benzeticide v5 koşulmadı (süre). Doğrudan MuJoCo'ya geçildi.
- Bilgi kanalı (bu hatta yeni değil): "dış alana geldik ama hakem bitirmedi" (`beyin._varis`) benzetimin sürmesinden
  çıkarılıyor ve sahte çıkış listesi buna dayanıyor. Gerçek robotta FINISH algısı ne veriyorsa o kadarı meşrudur.
- İşlemci: en çok 3 süreç (MuJoCo), her biri tek iş parçacığı, düşük öncelik; gerçek zaman oranı 3,1–4,5.

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
