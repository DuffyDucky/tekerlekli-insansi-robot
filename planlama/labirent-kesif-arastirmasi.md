# Labirent keşfi: tasarım notu (Lale, simülasyon)

Tarih: 2026-11-25. Kapsam: MuJoCo + düz Python/numpy, ROS yok, 2B LiDAR + teker odometrisi, IMU yok.
Bu not uygulama ajanları için yazıldı. Her başlıkta önce öneri ve gerekçe, sonra kaynak ve tuzak var. "Değerlendirme" diye işaretli kısımlar benim çıkarımım, kaynakta yazmıyor.

## Karar özeti

1. **Keşif:** Sınır tabanlı keşif (Yamauchi 1997). Sınır, haritadaki bilinen boş hücrenin bilinmeyen hücreye komşu olduğu yerdir. Duvar izleme ve Trémaux yalnız yedek olarak kalır. Hedef sınırı seçerken maliyet, robotun bulunduğu yerden **yol mesafesi**dir (Dijkstra/wavefront). Bunun üstüne iki küçük bonus eklenir: **açık-dış bonusu** (o sınırdan dönüşsüz ışınlar kaçıyorsa) ve hafif bir **START'tan uzaklaşma** eğilimi. Bir hedef seçildikten sonra robot ona bağlı kalır (histerezis). Çıkmaz sokakları ayrıca elemek gerekmez. Ucu LiDAR'la görülmüş bir çıkmazda sınır kalmadığı için robot oraya zaten gitmez. START'tan geri çıkmayı **sanal duvar + sınır kara listesi + kesin durdurma** önler.
2. **SLAM:** 5 cm çözünürlükte log-odds doluluk ızgarası. Konum, taramayı haritaya eşleştirerek bulunur: odometri tahminiyle başlanır, ilintisel arama (Olson 2009) yapılır, sonra Gauss–Newton ile inceltilir (Hector tarzı). Döngü kapatma yok, çünkü labirentte döngü yok ve gerek de yok. Dönüşlerde her tarama eşleştirilir. Eşleşmesi kötü taramalar haritaya yazılmaz. Odometrinin dönüş ölçeği çalışırken düzeltilir (yaklaşık ×0,88).
3. **Planlama ve izleme:** 10 cm planlama ızgarası kullanılır. Engeller robotun yarı genişliği + 5 cm kadar sert şişirilir. Bunun üstüne koridor ortasına çeken bir açıklık maliyeti eklenir, A* bu ızgarada çalışır. Yolu arka dingile göre saf takip (pure pursuit) izler, ileri bakış 0,4–0,6 m. Yön hatası 35°'yi geçerse robot durur ve yerinde döner. Ama yalnız **süpürme dairesi sığıyorsa** döner, aksi halde önce daha geniş bir noktaya ilerler.
4. **Puan:** Başarıda 1000 + 500·(1 − t/900) verilir. Başarısızlıkta en iyi jeodezik ilerlemeye göre kısmi puan verilir. Her çarpma −50. START'tan çıkış −200. Ek tur için ayrı bir 0–300 puan var. Formül §4'te.
5. **Öğrenme:** PPO **yok**. Puan amaç fonksiyonu yapılır ve 6–8 strateji parametresi CMA-ES (ya da rastgele arama) ile ayarlanır. Eğitim ve sınama labirentleri ayrı tohumlardan gelir. Arama hızlı bir 2B vekil simülatörde yapılır, en iyi 3 aday MuJoCo'da doğrulanır.
6. **Yapılabilirlik uyarısı:** 15 dk × 0,25 m/s ≈ 225 m eder, dönüşler ve duruşlarla gerçekte ~150 m. 17×17 bir labirentte (hücre 1,35 m) yalnız çözüm yolu bile bunu aşabilir. Her üretilen labirent için alt sınır t_min = L*/v hesaplanmalı ve "kuramsal olarak çözülemez" labirentler ayrıca raporlanmalı.

---

## 1. Keşif stratejisi

**Öneri: sınır tabanlı keşif, yol mesafesiyle sınır seçimi ve histerezis.**

Gerekçe:
- **Duvar izleme.** Basit bağlantılı bir labirentte, giriş ve çıkış dış duvardaysa, çıkışa ulaşmayı garanti eder ([Wikipedia: Maze-solving algorithm](https://en.wikipedia.org/wiki/Maze-solving_algorithm)). Ama LiDAR'ın uzağı görme avantajını tamamen boşa harcar. Bir dal 12 m öteden çıkmaz görünse bile robot içine girip duvarı izler. En kötü durumda her koridoru iki kez geçer. 17×17'de bu yaklaşık 2 × 288 × 1,35 ≈ 780 m eder, yani süre yetmez (değerlendirme).
- **Trémaux / derinlik öncelikli arama.** "İyi tanımlı geçitleri" olan labirentlerde garantilidir ([aynı kaynak](https://en.wikipedia.org/wiki/Maze-solving_algorithm)). Ama düğüm ve geçit kavramı ister, yani ızgara ya da kavşak tespiti varsayar. Döngüsüz labirentte sınır tabanlı keşif zaten DFS'e benzer davranır ve bunu ızgara varsaymadan yapar (değerlendirme).
- **Taşkın doldurma (micromouse flood-fill).** Hedef hücrenin bilinmesini ve hücre ızgarasını varsayar. Burada ikisi de yasak.
- **Sınır tabanlı keşif.** Robot, bilinen boş alanla bilinmeyen alanın sınırına tekrar tekrar gider ([Yamauchi 1997, CIRA, s. 146–151](https://ieeexplore.ieee.org/document/613851); [dblp](https://dblp.dagstuhl.de/rec/conf/cira/Yamauchi97.html)). Izgara varsaymaz ve LiDAR'ın uzaktan gördüğü her şeyi kullanır.
- **Sınırları verimli bulmak.** WFD, robotun konumundan yalnız bilinen alanda yapılan bir BFS'tir; mesafeyi ve sınırları tek geçişte verir ([Keidar & Kaminka 2014, IJRR 33(2)](https://doi.org/10.1177/0278364913494911); [tez](https://u.cs.biu.ac.il/~galk/publications/papers/matan-msc.pdf)). Bizde aynı Dijkstra hem sınır listesini hem yol maliyetini verir.

**Sınır seçme ölçütü (değerlendirme):**
```
maliyet(f) = d_yol(f) / v + t_dön(Δθ) − w_dış · dış(f) − w_uzak · min(1, d_START(f)/10 m)
```
- `d_yol`: Dijkstra'dan gelen yol mesafesi, ana terim budur. Ağaç labirentte en yakın sınıra gitmek "dalı bitirmeden başka dala geçme" davranışını kendiliğinden üretir.
- `dış(f)` ∈ [0,1]: sınırın gerisinde dönüşsüz (no-return) ya da 8 m'den uzun ışınların oranı. Dışarıdaki açık alan FINISH açıklığından görünür, bu terim robotu oraya çeker.
- `w_uzak` küçük tutulmalı. FINISH konumu bilinmiyor, bu yüzden güçlü bir yön sezgisi aşırı uydurmaya yol açar.
- Bilgi kazancı (görünmeyen alan sayımı) ayrıca gerekmez. Dar koridorda her sınırın kazancı birbirine benzer, `dış` terimi zaten işin önemli kısmını yapar.
- **Histerezis:** Mevcut hedef ancak kaybolursa (sınır kapanırsa), ulaşılamaz olursa ya da yeni aday %30'dan **ve** 2 m'den daha ucuzsa değiştirilir. Sınır seçimi 10 Hz'de değil 1 Hz'de yapılır.

**Çıkmazları girmeden eleme:**
- Ucu görülmüş bir çıkmazda boş-bilinmeyen sınırı kalmaz, yani hedef de olmaz. Ek bir algoritmaya gerek yoktur. Koşul, duvarın delik olmadan haritalanmasıdır.
- Açısal adım 0,72° olduğu için ışın aralığı 12 m'de ≈ 15 cm, 3 m'de ≈ 4 cm. Yan dallar ancak kavşaktan bakınca görünür. 0,25 m/s hızla 1,35 m'lik bir ağzın önünden geçmek ~5 s, yani ~50 tarama sürer. Kısa çıkmazlar yalnız yanından geçerken kapanır (değerlendirme).
- **Sahte sınırları süzmek:**
  1. Sınır kümesi robot genişliğinden kısaysa (< 0,5 m) atılır.
  2. Sınır tespitinden önce dolu hücrelere 1 hücrelik morfolojik kapama uygulanır, böylece sıyırma açısında oluşan duvar delikleri kapanır.
  3. Sınırın 0,5 m yakınında şişirilmiş haritada boş bir hedef hücre yoksa sınır "ulaşılamaz" sayılır ve kara listeye alınır. Kara listeden harita değişince çıkar.

**START'tan çıkmama güvencesi (üç katman):**
1. **Sanal duvar.** Robot START çizgisini geçince (iki yanda da duvar görünce) START ağzına bir sanal duvar eklenir. Ağız, yanlardaki iki duvar ucu arasıdır ve ölçülür, bulunamazsa 2 m genişlik varsayılır. Bu duvar, başlangıç pozuna sabitlenmiş harita çerçevesinde durur ve planlayıcı onu dolu görür. Başlangıçta START ağzı arka kör sektörde (92°) kalır, robot onu göremez. Yeri bu yüzden pozdan hesaplanır.
2. **Kara liste.** START çizgisinin gerisinde kalan yarım düzlemdeki sınırlar (yarıçap ~3 m) hiçbir zaman hedef olmaz.
3. **Kesin durdurma.** Robotun herhangi bir gövde noktası START çizgisine 0,3 m yaklaşırsa hız sıfırlanır ve yeniden plan yapılır.

**Çıkışı tanıma:** Asıl başarıyı simülatör ölçer. Robot tarafında bir açıklıktan geçtikten sonra iki yanda 3 m içinde duvar yoksa ve ışınların %50'sinden fazlası dönüşsüzse "dışarıdayım" denir. Robot durur, FINISH noktasını harita çerçevesinde kaydeder (ek tur için gerekli).

**Tuzak:**
- Dönüşsüz ışınlar boş olarak işlenmezse dışarıdaki alan hiç sınır üretmez ve `dış` terimi ölü kalır. Simülatörün dönüşsüz ışında 0 mı yoksa menzil üstü mü döndürdüğü netleştirilmeli.
- Bu ışınları boş olarak işlerken sınır 11,5 m'de bırakılmalı, ışının uç hücresi dolu işaretlenmemeli.

## 2. ROS'suz hafif SLAM

**Öneri:** log-odds doluluk ızgarası + tarama–harita eşleştirme. Adımlar:
1. Odometri tahmini.
2. Kaba ilintisel arama.
3. Gauss–Newton inceltme.
4. Kalite kapısı.
5. Harita güncellemesi.

Ayrı bir arka uç yok.

**Gerekçe:**
- **Olson 2009.** Olasılık temelli ilintisel eşleştirmenin daha sağlam sonuç verdiğini gösterir. Gerçek zamana çok çözünürlüklü aramayla yetişir ([Olson 2009, ICRA, s. 4387–4393, DOI 10.1109/ROBOT.2009.5152375](https://doi.org/10.1109/ROBOT.2009.5152375)).
- **Hector SLAM.** Harita gradyanlarının hızlı yaklaşık hesabı ve çok çözünürlüklü ızgarayla odometrisiz çalışır ([Kohlbrecher vd. 2011, SSRR](https://wiki.ros.org/hector_slam); [ROS kaynak kodu](https://docs.ros.org/en/fuerte/api/hector_mapping/html/HectorMappingRos_8cpp_source.html)). Güncelleme katsayıları varsayılan olarak boş için 0,4, dolu için 0,9; harita güncelleme mesafe eşiği 0,4 m.
- **Gauss–Newton tek başına neden yetmez (değerlendirme).** GN yerel minimuma takılır, ilk hata büyükse yanlış duvara oturur. Bizim odometri dönüşte %14'e kadar hata verir. Bu yüzden önce kaba ilintisel arama yapılır, GN yalnız inceltme içindir.
- **Döngüsüz labirentte kayma (değerlendirme).**
  - Robot geri dönerken aynı duvarları yeniden görür ve taramayı haritaya eşleştirir. Bu, konumu **haritaya göre** sınırlı tutar.
  - Harita bütünüyle biraz bükülse de kendi içinde tutarlıdır. Döngü olmadığı için bu bükülme hiçbir yerde çelişki üretmez. Gezinme ve ek tur yalnız yerel tutarlılık ister, bu yüzden döngü kapatmaya gerek yoktur.
  - Gerçek tehlike tek bir kötü eşleşmedir: hayalet duvar çıkar ve geçit kapanır.

**Pratik değerler:**

| Konu | Değer | Not |
| --- | --- | --- |
| Harita çözünürlüğü | 5 cm, 800×800 (40×40 m, başlangıç ortada) | float32 log-odds |
| Log-odds | isabet +0,85 (p=0,7), ıska −0,4 (p=0,4), sınırlar [−2, +3,5] | OctoMap varsayılanları ([kaynak](https://docs.ros.org/en/melodic/api/octomap/html/AbstractOccupancyOcTree_8h_source.html)) |
| Dolu / boş eşiği | L > 0,85 dolu, L < −0,8 boş | değerlendirme |
| Eşleştirme | her tarama, nokta seyreltme 500 → ~180 | |
| Kaba arama | ±0,15 m, adım 2,5 cm; açı ±(3° + 0,15·\|Δθ_odo\|), adım 0,5° | %14 dönüş hatasını kapsar |
| İnceltme | GN, 3 seviye (20/10/5 cm), 5–10 iterasyon | Hector tarzı, bilineer interpolasyon |
| Olabilirlik alanı | exp(−d²/2σ²), σ = 5–8 cm, d mesafe dönüşümünden | `scipy.ndimage.distance_transform_edt`; 1–2 Hz'de yerel pencerede güncellenir |
| Harita yazma | ≥ 5 cm ya da ≥ 3° hareket ve kalite kapısı geçilmişse | Hector 0,4 m kullanır, bizde koridor dar olduğu için daha sık |
| Dönüş ölçeği | k = Σ Δθ_eşleşme / Σ Δθ_odo (kayan ortalama, başta 0,88) | odometri tahmininde kullanılır |
| Odometri önseli | maliyete λ·‖Δx − Δx_odo‖² eklenir | uzun koridorda koridor yönünü odometri belirler |

**Hesap süresi (10 Hz bütçesi, değerlendirme):**
- İlintisel arama Olson'un hilesiyle yapılır: her açı için nokta hücre indeksleri bir kez hesaplanır, ötelemeler tamsayı kaydırmadır.
- Yük yaklaşık 13×13 öteleme × 21 açı × 180 nokta ≈ 0,64 M dizi okumasıdır. numpy ile 5–15 ms.
- Işın güncellemesi şöyle yapılır: her ışın boyunca yarım hücre aralıklarla örnek alınır, `np.unique` ile aynı hücre iki kez sayılmaz, ıskalar `np.add.at` ile yazılır. 500 ışın için ~5–10 ms.

**Hareket çarpıklığı:**
- Gerçek RPLIDAR'da bir tur 0,1 s sürer. ω = 0,5 rad/s'de taramanın başı ile sonu arasında ~2,9° kayma olur.
- Düzeltme: her noktaya t_i = i/N · 0,1 s zaman verilir, poz odometri hızıyla t_i'ye interpole edilir ve nokta taramanın son pozuna taşınır.
- Simülatör tüm ışınları aynı anda atıyorsa çarpıklık yoktur. Uygulama ajanı gerçekçilik için ışınları ardışık zamanlarla atmayı seçmeli.
- Ek güvenlik: |ω| > 0,6 rad/s iken haritaya yazılmaz, yalnız konum bulunur.

**Harita ne zaman bozulur, tuzaklar:**
- **Uzun düz koridor** (12 m menzilden uzun, ucu görünmüyor): koridor yönündeki öteleme gözlenemez. Erken işaret: GN Hessian'ının en küçük özdeğeri düşer. O yönde odometriye güvenilir.
- **Dönüş:** pencere küçükse yanlış minimum seçilir. Pencere ±45°'yi aşarsa 90°'lik simetri takması (aliasing) başlar. Öteleme penceresi de hücre periyodunun yarısından (≈ 0,6 m) küçük kalmalı.
- **Kör sektör (arka 92°):** geri giderken arka yeni gözlenmez. Robot geri giderken haritaya yazmamalı, yalnız ön yarıyla eşleştirme yapmalı.
- **Sensörün montaj noktası:** LiDAR arka dingilde değilse aradaki dönüşüm yanlış girildiğinde her dönüşte harita bulanır. Bu en sık yapılan sessiz hatadır.

## 3. Yol planlama ve izleme

**Öneri:**
- Planlama ızgarası: 5 cm harita max-pooling ile 10 cm'e indirilir.
- **Sert şişirme:** r_iç = robot yarı genişliği (≈ 0,25 m) + 0,05 m.
- **Yumuşak maliyet:** c = 1 + w·exp(−(d − r_iç)/0,1 m). Bu terim robotu koridor ortasına çeker.
- Yolu A* bulur. Hedefe göre sınırları seçen Dijkstra 1 Hz'de çalışır.

**Gerekçe:**
- 1,2 m koridorda sert şişirme sonrası ~0,6 m genişliğinde bir seyir bandı kalır.
- Robotu çevreleyen yarıçapla şişirmek (arka dingil merkezli dikdörtgen için ~0,55 m) koridoru neredeyse kapatır. Bu yüzden düz giderken iç yarıçap kullanılır, dönerken süpürme ayrıca kontrol edilir (değerlendirme).

**Yol yumuşatma:** görüş hattı kısaltması uygulanır ama yalnız segment boyunca açıklık ≥ r_iç + 0,10 m ise. Yoksa kısaltılmış yol köşeye sürtünür.

**İzleme:**
- Saf takip, eğriliği "ilerideki hedef noktaya giden yay" olarak hesaplar ([Coulter 1992, CMU-RI-TR-92-01](https://www.ri.cmu.edu/publications/implementation-of-the-pure-pursuit-path-tracking-algorithm/); [PDF](https://apps.dtic.mil/sti/pdfs/ADA255524.pdf)).
- İleri bakış kısalırsa salınım, uzarsa köşe kesme olur. 0,25 m/s için L = 0,4–0,6 m.
- Referans nokta arka dingil ortasıdır, çünkü robot o noktanın etrafında döner.
- Hız, açıklıkla ölçeklenir: d < r_iç + 0,1 m ise v yarıya iner.

**Yerinde dönüş ne zaman:**
- Yön hatası > 35° ise ve süpürme dairesi sığıyorsa.
- Süpürme yarıçapı r_süp = max(√(a² + (W/2)²), √(b² + (W/2)²)). Burada a, arka dingilden en öndeki noktaya; b, en arkadaki noktaya olan mesafedir.
- Koşul: o noktada açıklık ≥ r_süp + 0,05 m.
- Örnek: a = 0,5 ve W = 0,5 ise r_süp ≈ 0,56 m. Bu durumda 1,2 m koridorda **hiçbir yerde** sığmaz, 1,5 m'de ancak kavşak ortasında sığar.
- Sığmıyorsa:
  1. Önce açıklığın en büyük olduğu yere ilerlenir (kavşak ortası, mesafe dönüşümünün yerel tepesi).
  2. Hâlâ sığmıyorsa küçük yaylarla birkaç hamlede ileri–geri dönülür. Geri kısım yalnız daha önce geçilmiş iz üzerinde ve en çok 0,3 m yapılır (arka kör).
- Uygulama ajanı a, b ve W'yi model dosyasından alıp **ilk iş** bu hesabı yapmalı.

**Tuzaklar:**
- A* düz Python'da 160 bin hücrede 0,3 s'yi aşabilir. Planlama 10 cm'de ve kontrol döngüsünden ayrı (her 10 çevrimde bir ya da ayrı bir iş parçacığında) yapılmalı.
- Simülasyon zamanı hesap süresinden bağımsızdır, adımlı çalışır. Yine de çevrim başına < 100 ms bütçesi gerçek robota geçiş için korunmalı (değerlendirme).

## 4. Ödül–ceza (puanlama)

**Kaynaklardaki örnekler:**
- **Micromouse (UK tabanlı kurallar).** Puan = koşu süresi + arama cezası + dokunma cezası. Arama cezası, labirentte geçen sürenin 1/30'u. Dokunma cezası, koşudan önce dokunulmuşsa 3 s + koşu süresinin 1/10'u. Toplam süre sınırı 10 dk ([micromouseonline kural özeti](https://micromouseonline.com/micromouse-book/rules/)).
- APEC'te de 1/30 ceza var, süre 7 dk ([UBIEEE özeti](https://ubieee.github.io/wiki/micromouse/competition-rules)). APEC PDF'i okunamadı [DOĞRULANMADI: PDF metni]. Singapur kurallarında oran 1/60 ve dokunma cezası 2 s [DOĞRULANMADI: yalnız arama özetinden].
- Ders: arama süresi az ama sıfır olmayan bir ağırlıkla cezalandırılır. Asıl ödül en hızlı koşudur.
- **Keşif kıyaslama ölçütleri:** keşif süresi, keşif maliyeti (kat edilen mesafe), verim (keşfedilen m² / mesafe), harita tamlığı ve harita kalitesi ([Yan vd. 2015, IROS](https://yzrobot.github.io/publications/yz15iros.pdf)).
- **Pekiştirmeli öğrenmede biçimlendirme:** F = γΦ(s') − Φ(s) biçimindeki ödül eki en iyi politikayı değiştirmez ([Ng, Harada, Russell 1999, ICML](https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html)). Bizde Φ = −(FINISH'e gerçek jeodezik mesafe) olarak düşünülebilir.

**Önerilen formül (değerlendirme).** T = 900 s. g(x), gerçek labirent grafiğinde x'ten FINISH'e jeodezik mesafedir; simülatör bilir, robot bilmez. İlerleme şöyle tanımlanır:
```
p_en = max_t (1 − g(x_t) / g(START))   ∈ [0, 1]
```
En iyi değer alındığı için ileri–geri salınarak puan toplanamaz.

```
Ana tur:
  Başarı (FINISH'ten çıktı):   S1 = 1000 + 500·(1 − t/T)
  Süre doldu:                   S1 = 400·p_en
  Sıkıştı:                      S1 = 400·p_en − 100
                                (60 s boyunca 0,2 m'den az net hareket ya da simülatörün sıkışma tespiti)
  START'tan çıktı:              S1 = −200    (kural ihlali, her zaman aşımından kötü)
  Her durumda:                  − 50·çarpma_olayı − 10·(sürekli temas saniyesi)
  Çarpma olayı:                 temasın başladığı an sayılır, aynı temas 1 s içinde tekrar sayılmaz

Ek tur (yalnız ana tur başarılıysa):
  Başarılıysa:                  S2 = 300·min(1, t*/t2) − 50·çarpma
  Değilse:                      S2 = 0
  t* = L*/v_max                 (L* gerçek en kısa yolun koridor ortası uzunluğu)

Toplam: S = S1 + S2
```

**Neden bu ağırlıklar:**
- Başarısızlıktaki kısmi puan en çok 400 olabilir, en yavaş başarı ise 1000 alır. Bu yüzden başarıyla başarısızlık arasında her zaman büyük bir boşluk kalır.
- Jeodezik ilerleme kullanılır, çünkü ağaç labirentte FINISH'e kuş uçuşu yakın bir çıkmaz yanıltıcıdır.
- Micromouse tarzı bir alternatif istenirse ek tur için şu kullanılabilir: t2 + t1/30 + 3 s × çarpma, küçük olan iyidir.

**PPO mu, parametre araması mı? Parametre araması.** Dürüst değerlendirme:
- **Örnek bütçesi.** Bir bölüm 9000 adım (10 Hz × 900 s). MuJoCo'da gerçek zamanın ~10 katı hızla bölüm başına ~90 s gerekir. Bir gecede (10 saat) ~400 bölüm, yani ~3,6 M adım koşulabilir.
- **Genelleme.** Usule göre üretilen seviyelerde politikalar eğitim seviyelerine aşırı uyar, genelleme çok sayıda seviye ister ([Cobbe vd. 2019](https://arxiv.org/abs/1812.02341); [Zhang vd. 2018](https://arxiv.org/abs/1804.06893)).
- PPO'nun kendisi ([Schulman vd. 2017](https://arxiv.org/abs/1707.06347)) bu bütçeyle LiDAR'dan genelleyen bir labirent politikası öğrenebilir mi, [DOĞRULANMADI]. Benim tahminim hayır.
- Ayrıca START sanal duvarı ve çarpışma güvenliği kurallı yığında kolayca garanti edilir, öğrenilmiş bir politikada edilmez.
- **Öneri:**
  - CMA-ES ([Hansen öğretici](https://arxiv.org/abs/1604.00772); `pip install cma`), popülasyon 8–10.
  - Ya da bütçe çok azsa rastgele arama.
  - Ayarlanacak parametreler: w_dış, w_uzak, histerezis oranı, en küçük sınır genişliği, ileri bakış, v_max (kuralın izin verdiği aralıkta), şişirme payı, dönüş eşiği.
- **Hızlı vekil simülatör (değerlendirme).**
  - Aynı SLAM/keşif kodu çalışır, ama fizik yerine kinematik + numpy ışın atma kullanılır.
  - Odometri hatası modellenir (%14 dönüş, kayma), gürültü ±2 cm.
  - Hedef hız: gerçek zamanın 100 katı ve üstü.
  - Parametre araması vekilde yapılır, en iyi 3 aday MuJoCo'da en az 20 sınama labirentinde doğrulanır.
- **Aşırı uydurmayı önleme:**
  - Eğitim tohumları ile sınama tohumları ayrıdır, sınama seti aramada asla kullanılmaz.
  - Katmanlama yapılır: boyut 5–17, hücre 1,2/1,35/1,5 m.
  - Sınamada **en az bir farklı üreteç** olmalı (örneğin eğitim DFS-geri izleme ise sınama Prim/Kruskal). Robot ızgara varsaymadığı için sınamaya ara hücre boyları (1,3 m gibi) da eklenir.
  - Her aday aynı eğitim labirent kümesinde değerlendirilir (ortak rastgele sayılar).
  - Amaç: J = ortalama(S) + 0,5·alt %20 dilimin ortalaması. Kötü labirentleri gizleyen ortalamaya karşı korur.
  - Rapor her zaman sınama setinden verilir: başarı oranı, ortalama süre, çarpma/bölüm, START ihlali sayısı (0 olmalı).

## 5. Sık hata kalıpları ve erken uyarı işaretleri

| Hata | Erken işaret (günlüğe yaz) | Önlem |
| --- | --- | --- |
| Harita eğrilir, geçit kapanır | Eşleştirme puanı düşer ya da artık büyür; daha önce güvenle boş olan hücreler dolu olur (çelişki sayacı); hedefe giden yol aniden kaybolur | Kalite kapısı (kötü taramayı yazma); log-odds sınırları; yol kaybolunca yerinde 1–2 temiz tarama alıp yeniden dene, olmazsa son güvenli poza geri dön |
| Sınır titremesi, hedef değiştirip durma | 10 s'de 3'ten fazla hedef değişimi; 20 s'de < 0,3 m net yer değiştirme | Histerezis, hedefe bağlılık, seçim 1 Hz |
| Dar yerde sıkışma | v > 0 komutuna rağmen 3 s boyunca hem odometride hem eşleştirmede ~0 hareket; ön ve yan sektörde en yakın mesafe < gövde + 2 cm | Toparlanma: geçilmiş iz üzerinde ≤ 0,3 m geri, süpürme kontrolüyle dönüş; 3 başarısızlıkta o hedefi kara listeye al |
| Yerinde dönüşte köşe çarpması (arka dingil merkezli dönüş) | DÖN durumunda temas olayı | r_süp kontrolü (§3); dönüşü kavşak ortasında yap |
| START açıklığı sınır sanılır | Seçilen hedef START çizgisinin gerisinde | Sanal duvar + kara liste + kesin durdurma (§1); START ihlali test setinde 0 olmalı |
| Sahte sınır (sıyırma açısı, duvar deliği) | Çok sayıda < 0,5 m sınır kümesi; hedef duvarın içinde | Kümeyi en küçük genişliğe göre süz, morfolojik kapama, ulaşılamaz sınırı kara listeye al |
| Dönüşte yanlış eşleşme (90° takma, %14 hata) | Eşleşme ile odometri dönüşü arasında > 10° fark; harita çift duvar gösterir | Pencereyi ±(3° + 0,15·Δθ) ile sınırla (±45° altı); dönüş ölçeği k'yı öğren |
| Süre biter, çıkmaz dallarda oyalanır | %50 sürede p_en (vekilde ölçülür) < 0,3; aynı dala iki kez girme | `w_dış` ve uzaktan görmeyi artır; kavşakta kısa bakış duruşu (0,5 s) |

---

### Doğrulanamayanlar / açık sorular
- Micromouse kurallarındaki APEC 7 dk / 1/30 ve Singapur 1/60 / 2 s değerleri yalnız arama özetinden geldi, kural PDF'leri okunamadı [DOĞRULANMADI].
- Hector `map_resolution` varsayılanı (0,025 mi 0,05 mi) ve Cartographer ilintisel eşleştirici varsayılanları doğrulanamadı. Bu notta kullanılmadılar.
- Hector makalesinin TU Darmstadt PDF bağlantısı 404 döndü. İddialar arama özetinden ve ROS belgesinden alındı.
- Farklı üreteçlerde (DFS, Prim, Kruskal) 17×17 çözüm yolu uzunluğu ölçülmedi [DOĞRULANMADI]. Uygulama ajanı kendi üretecinde L* dağılımını ölçmeli. 225 m üst sınırına göre çözülemeyen labirent oranı raporlanmalı.
- PPO'nun bir gecelik bütçeyle genelleyebileceği [DOĞRULANMADI]. Değerlendirme olumsuz.
- Robot boyutları (a, b) bilinmiyor. Yerinde dönüşün sığıp sığmadığı model dosyasından hesaplanmalı.
