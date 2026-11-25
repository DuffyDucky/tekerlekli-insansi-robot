# Harita eskimesi deneyi

Robotun haritası ile dünya artık aynı olmadığında koridor gezinmesi (A'dan B'ye, kayıp robot) ne kadar bozuluyor?
Gezinme ölçümü (`kod/fizik/gezinme/sonuc/SONUC.md`: A'dan B'ye 36/36, kayıp 30/30, temas 0) sahne ile konumlayıcı
haritası aynı dosyadan gelirken alındı; bu deney aynı beyinleri (`gezinme.beyinler.AbBeyni`, `KayipBeyni`, v3
konumlayıcı, varsayılan ayarlar) **değiştirmeden**, dünyayı haritadan saptırarak koşturur. Sonuç ve hüküm:
`sonuc/SONUC.md`.

## Ne değişir, ne değişmez

- Robotun haritası hep bozulmamış `kod/araclar/haritalar/koridor_N.json`; rota, duraklar, konumlayıcı aynı.
- Dünya (çarpışma + LiDAR'ın gördüğü geometri + insanlar + sensör ve odometri hataları) koşula göre bozulur
  (`ortak.dunya_kur`). Algoritma yalnız taramayı ve odometri artımını görür; dünya, gerçek poz ve insanlar yalnız
  benzetici / hakem tarafında.
- Geometri hataları (ölçek, eğrilme) dünyayı haritadan T ile türetir (başlangıç sabit nokta): hedefin gerçek yeri
  T(hedef); konum hatası harita çerçevesinde (T⁻¹(gerçek poz) ile tahmin), varış hatası dünyada ölçülür.

| Etken | Kademeler | Nasıl |
| --- | --- | --- |
| a. kapı | %10 / 25 / 50 / 100 kapının durumu ters | kapalı (girinti) -> açık + arkasında oda (çakışmasız, en çok 3 x 3 m); açık -> kapalı (kanat 5 cm içeride). İç içe: aynı tohumda büyük kademe küçüğünü kapsar |
| b. eşya | 0,5 / 1 / 2 / 4 adet / 10 m | kutu 0,5 x 0,5, sıra 1,2 x 0,4, çöp kovası Ø0,4, dolap 0,9 x 0,45; duvar dibinde, kapı önü (± 0,8 m), uç ve köşeler (1,5 m) boş |
| c. insan | 0,5 / 1 / 2 / 4 kişi / 10 m | bacak çifti (2 x Ø0,12 m, LiDAR düzleminde); %60 yürüyen (0,9–1,4 m/s, robota yol verir, gerekirse durur), %40 duvar dibinde duran |
| c. grup | duvardan 0,6 / 0,9 / 1,2 / 1,5 m içeri | 3–4 kişi rotanın ortasında yan yana durur; robot 3 m'ye geldikten 30 s sonra dağılır |
| d. ölçek | %0,5 / 1 / 2 / 3 | dünya = başlangıç çevresinde (1 + k) kat |
| d. genişlik | 2,5 / 5 / 7,5 / 10 cm | bir uzun duvar dış normali boyunca kaydırılır (tohuma göre geniş ya da dar); üretici (`koridor_sahneleri`) bellekte yeniden koşar |
| d. eğrilme | 0,5 / 1 / 2 / 4 ° / 20 m | başlangıçtan başlangıç yönünde sabit eğrilik (haritalama yön kayması gibi); duvarlar 1 m parçalara bölünüp eğilir |
| e. gürültü | σ 2 / 3 / 5 / 8 cm (taban 1 cm) | Gauss + 15 mm yuvarlama |
| e. dönüşsüz | %10 / 25 / 50 / 75 yüzey | dünya duvarları 1 m parçalara bölünür, oran kadarı dönüş vermez (siyah / parlak / cam yüzey): ışın NaN |
| e. cam kapı | %25 / 50 / 75 / 100 kapalı kapı | LiDAR camdan arkasındaki odayı görür, robot geçemez |
| e. menzil | 8 / 6 / 4 / 2 m (taban 12) | gerçek uzaklık sınırın ötesindeyse NaN; konumlayıcı 12 m sanmaya devam eder |
| f. odometri ölçek | +%2 / 5 / 7,5 / 10 öteleme | enkoder öteleme fazla |
| f. dönüş hatası | +%5 / 10 / 15 / 25 (tabandaki %14'e ek) | enkoder dönüş fazla |
| f. ani kayma | 0,5 / 1 / 2 / 4 olay / dk hareket | olayda odometri sahte 0,10–0,30 m öteleme + 3–10° dönüş bildirir (teker döner, gövde gitmez) |
| g. okul günü | hafif / orta / ağır | etkenlerin birleşimi (`ortak.OKUL_GUNU`) |

## Nasıl çalıştırılır (`cd kod\fizik\deneyler\harita_eskimesi`)

`%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe` (yalnız MuJoCo için). Bütün betikler süreci düşük önceliğe
alır, numpy iş parçacığını 1'e indirir.

    py -3 kos2b.py --senaryo ab --isci 3                  # 2B A'dan B'ye ızgarası: 60 koşul x 6 koridor x 2 tohum
    py -3 kos2b.py --senaryo kayip --isci 3 --kosul taban,okul_hafif,okul_orta,kapi_2,cam_1,menzil_3,esya_4,donussuz_4,odo_kayma_4,insan_4,kapi_4,cam_4,menzil_4,okul_agir,egrilme_4,olcek_4,odo_donus_4,odo_olcek_4,gurultu_4,grup_4
    py -3 kos2b.py --tek ab:kapi_2:koridor_5:2            # tek koşu, sonucu ekrana
    py -3 kos_varyant.py                                  # isteğe bağlı dayanıklılık varyantı (AYRI tohumlar)
    %V% kos_mujoco.py --kosul taban,kapi_2,... --kosu koridor_5:1,koridor_1:2,koridor_3:2
    py -3 analiz.py                                       # CSV, sonuc/tablolar.md, sonuc/ozet.json, gorsel/*.png
    py -3 ciz_dunya.py koridor_4                          # harita / dünya üstten görünüm
    py -3 -m unittest discover -s testler -v              # birim testleri (≈ 3 s)

Süreler (bu PC, tek iş parçacığı): 2B A'dan B'ye koşusu 3–15 s, kayıp 6–90 s, MuJoCo A'dan B'ye 5–55 s. Ölçümde
A'dan B'ye ızgarası 2 işçiyle ≈ 35 dk, kayıp 20 koşul 2 işçiyle ≈ 45 dk, varyant 1 işçiyle ≈ 50 dk, MuJoCo ≈ 35 dk.
İki `kos2b.py` aynı anda çalışabilir (görev başına `.kilit`); yarıda öldürülen koşunun `.kilit` dosyası elle silinir.
İnsan modeli `insan.SURUM` = 2 (sürüm 1'in kilitlenen sonuçları silinip yeniden koşuldu; ham sonuçta `insan.surum`).

Bitmiş koşu `sonuc/ham/<2b/ab | 2b/kayip | mujoco | varyant>/<id>.json` olarak durur, yeniden koşmaz (kaldığı yerden).
`sonuc/ham/` ve `.durum` depoya girmez; bütün tohumlar sabit olduğundan aynı ham sonuçlar yeniden üretilir.

## Dosyalar

| Dosya | İş |
| --- | --- |
| `ortak.py` | yollar, koşul ızgarası (`KADEMELER`, `OKUL_GUNU`), bozucular (`dunya_kur`, kapı aç / kapat, eşya, genişlik, `Donusum`) |
| `insan.py` | `Kalabalik`: yürüyen / duran insanlar ve grup, bacak çifti daireleri |
| `benzet2b.py` | `Benzet2B`: kapalı çevrim 2B benzetici (kinematik ONERI, dönen LiDAR, bozuk odometri, çarpışma) |
| `kos2b.py` | 2B koşu tanımları (tohumlar gezinme senaryolarıyla aynı), işçi havuzu |
| `kos_mujoco.py` | aynı dünyalarla `gezinme.duzenek.Duzenek` (MuJoCo) doğrulaması; sensör / odometri bozucusu beyin sarmalayıcısında |
| `kos_varyant.py` | isteğe bağlı dayanıklılık varyantı, ayrı tohumlar |
| `analiz.py`, `ciz_dunya.py` | tablolar, kırılma noktaları, görseller |
| `testler/` | birim testleri (dönüşüm, kapı, eşya, insan, menzil / dönüşsüz yüzey, belirlenimcilik) |

## Tohumlar

A'dan B'ye: başlangıç sapması `random.Random(10000 + 31 t + 7 k)` ve MCL `500000 + t` (`gezinme/senaryo_ab.py` ile aynı),
t ∈ {1, 2}; hedef t = 1'de `hedefler(kor)[1]`, t = 2'de en uzak hedef. Kayıp: bırakma `random.Random(20000 + 100 k + i)`,
MCL `600000 + 10 k + i` (`senaryo_kayip.py` ile aynı), i ∈ {0, 1}. Dünya bozucusu: crc32(senaryo, etken, koridor, tohum)
(kademeden bağımsız: kademeler iç içe); benzetici gürültüsü crc32("sim", senaryo, koridor, tohum) (koşuldan bağımsız:
taban ile ortak rastgele sayılar). Varyant: t ∈ {3, 4} (ayar / hüküm ayrımı aşağıda SONUC.md'de).
