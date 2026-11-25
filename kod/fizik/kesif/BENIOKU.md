# kesif: bilinmeyen labirentte haritalayarak çıkış arayan beyin

`kesif.beyin:KesifBeyni`, gezinme `Beyin` protokolünü uygular: `adim(t, tarama, artim) -> (v, w)` ve `durum()`.
Beyin ızgara varsaymaz. Hücre boyunu ve FINISH'in yerini bilmez. Bildiği yalnızca kurallar ve kendi başlangıcıdır:
START çizgisinin 0,45 m içindedir ve içeri bakar.

    from kesif.beyin import KesifBeyni, olustur
    b = KesifBeyni()                       # ön bilgisiz (MuJoCo labirent koşuları böyle)
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
    py -3 -m unittest kesif.testler.test_kesif -v      # 7 sınama (birim + 5x5 uçtan uca)
    py -3 -m kesif.kos ilk | odometri | hafiza          # deney matrisi -> sonuc/*.csv (en çok 2 süreç)
    py -3 -m kesif.kos rapor                            # -> sonuc/SONUC.md
    py -3 -m kesif.ayar ara --n 16 ; py -3 -m kesif.ayar sina
    %LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe -m kesif.kos_mujoco --is 3   # MuJoCo, kayıtlar sonuc/ham/mujoco

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

- Döngü kapatma yok. Uzun koşuda yön yanlılığı birikir; mükemmel (döngüsüz) labirentte kabul edilebilir, döngülü
  labirentte değil.
- Çıkış tanıma "dışarısı geniş" varsayımına dayanır. FINISH dar bir koridora açılırsa beyin çıkışı tanımaz; sınır
  olarak görür ve yalnız şans eseri geçer.
- START çizgisinin boyu kurala göre bilinmiyor; ön bilgisiz kurulumda 1,3 m + 2 × 0,4 m pay varsayıldı.
- Tarama işleme Python/numpy; Pi 5'te ölçülmedi (bu makinede ortalama 5–6 ms).
