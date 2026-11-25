# Taşınma ("kaçırılmış robot") deneyi: sonuç

Tablolar `tablolar.md` (rapor.py üretir), koşu başına satır `tasinma_2b.csv`, `mujoco.csv`, gerileme `gerileme.csv`,
özet `ozet.json`. Görseller `../gorsel/basari_tur.png` (başarı, tür x sürüm), `../gorsel/ornek_kucuk_koridor_5.png`
(bir koşunun zaman çizgisi: v3 ve algi).

## Hüküm

- **v3 taşınmayı fark etmiyor; fark eden tek düzenek artırılmış MCL'nin rastgele saçması.** A'dan B'ye beyni
  (`AbBeyni`) hiçbir koşuda tepki vermedi (0 / 48): konumlayıcı `konum_kararsiz`'ı taşımadan 0,5-2,8 s (medyan) sonra
  yükseltiyor ama beyin buna bakmıyor, yanlış poza göre sürmeye devam ediyor (medyan 5-10 s, en çok 120 s). Kurtulma
  şansa bağlı: rastgele saçılan parçacık doğru yere düşerse poz oraya atlar. A'dan B'ye hedefe varış: aynı koridorda
  uzak 5 / 12, 180° 8 / 12, küçük kaydırma 8 / 12; başka koridorda hiçbirinde kaybolduğunu bildirmedi (6'sı yanlış
  koridorda "vardım" deyip durdu, 6'sı süre sonuna dek sürdü). 48 taşımanın 20'sinde robot yanlış yerde "vardım" dedi.
- 6 haritalı izleme (`KayipBeyni` karardan sonra) taşınmaya "poz sıçradı / harita değişti" diye yeniden planla tepki
  veriyor (46 / 48, medyan 0,5-1,8 s) ama sıçramayı doğru kabul ediyor: varış 8 / 10 / 11 / 10 (/12), yanlış poza göre
  sürüş medyan 3-15 s, en çok 121 s; yanlış koridora kesin sürüş 15 koşuda (229 s; 12'si başka koridor).
- **Fark etme süresi ("algi" sürümü, sınama kümesi, 96 taşıma):** 95 / 96'da "kayboldum" dedi. Medyan 0,8 s; aynı
  koridor uzak ve başka koridor en çok 0,8 s (tarama haritaya uymuyor), 180° çevrilme ve küçük kaydırmada medyan
  0,8-1,4 s ama en çok 13-15 s (tarama yanlış pozda da haritaya iyi uyuyor; algıyı konumlayıcının poz sıçraması ya
  da `konum_kararsiz`'ı tetikliyor).
- **Yerini bulma süresi (algi):** medyan 6 s (aynı uzak), 9 s (küçük), 13 s (180°), 6 s (başka koridor, 6 haritalı
  beyinde); en çok 139 s. Varış: A'dan B'ye 12 / 12 / 12 / 11 (başka koridorda "güvenli durdu"), 6 haritalıda
  11 / 10 / 12 / 11. Taşımadan sonra yanlış poza göre sürüş medyan 0,7-1,5 s (v3: 3-15 s); tek haritalı beyni başka koridora
  taşımada 6,6 s (v3 9,9 s). Temas: iki sürümde de 0.
- **En zor tür: 180° çevrilme.** Konum aynı, yön ters; koridor kendine yakın simetrik olduğundan tarama ters yönde de
  haritaya uyuyor (uyum 0,9): en geç fark edilen (en çok 15 s), en geç bulunan (medyan 13-16 s, en çok 139 s) ve algi'nin
  en çok kaybettiği tür (6 haritalıda 10 / 12, v3 de 10 / 12). v3 için en kötüsü başka koridor (tek haritalı beyin hiç
  kurtulamaz) ve aynı koridorda uzak taşıma (5 / 12).
- **Yanlış alarm bedeli:** taşıma yokken taban ve insan (1 / 10 m) koşullarında 0 / 48 yanlış alarm. Eşya varken var:
  A'dan B'ye eşya 1 / 10 m 1 / 12 koşu, insan + eşya 1 / 10 m 1 / 12, 2 / 10 m 5 / 12; 6 haritalıda 4 / 12, 3 / 12,
  8 / 12. Bu alarmların ilkinin 22'sinden 15'i "poz sıçraması": gerçek poz doğruyken (hata 0,02-0,13 m) konumlayıcının
  kendisi 2-25 m öteye atlamıştı (önceki aşamanın "takma yer" bozulması); v3'ün 6 haritalı beyni aynı koşularda aynı
  sayıda "poz sıçradı" tepkisi verdi. 7'si gerçekten boşuna (poz doğru, eşya / insan yüzünden uyum düştü). Varışa etkisi:
  A'dan B'ye yok (12 / 12, 12 / 12, 11 / 12; v3 12, 11, 10); 6 haritalıda eşya 1 / 10 m'de 10 / 12 (v3 12 / 12),
  karma 2. kademede 12 / 12 (v3 10), 3. kademede 7 / 12 (v3 8). Kaybı yaratan yeniden başlatma: eşyalı koridorda 6
  haritalı küresel konumlama yeniden takma yere karar verip 4 kez kaybolup yardım bekledi. Eşli süre farkı (ikisi de
  vardıysa) medyan 0 s, en çok 167 s.
- **Gerileme:** koridor_karisiklik kayıtlarının alt kümesinde (54 kayıt) algı yalnız insanlı C'de 2 kez tetiklendi, ikisi
  de v3'ün zaten yanlış koridora kesin olduğu kayıtlarda; yanlış koridora kesin koşu 2 -> 2, adım 577 -> 205 (bir kayıtta
  20 -> 22), sonda doğru 54 / 54 -> 54 / 54. v3'ün yeniden beslemesi 54 kayıtta deneyin `ham_v3` kaydıyla adım adım
  birebir aynı; algının tetiklenmediği 52 kayıtta algi de. Konumlama testleri, `kod/testler/kos.py` 58 / 58, önceki aşamanın testleri 12 / 12 geçti.
- **Varsayılan v3 kaldı.** "algi" yalnız bu klasörde (`algi.TasinmaBeyni`) ve isteğe bağlı. Gerileme küçültülmüş alt
  kümede yapıldı (aşağıda), tam koridor_karisiklik koşusu ve kapalı çevrimde (sürüşlü) gerileme yapılmadı; eşyalı 6
  haritalı koşuda yanlış alarmın kurtarma bedeli de çözülmedi. Karar kullanıcının.

## Ana tablo (sınama kümesi, 2B, koşul başına 12 koşu = 6 koridor x tohum 1, 2)

Tepki: beynin davranış değiştirdiği ilk an (algi "kayboldum"; v3 6 haritalı: yeniden plan / keşfe dönüş; v3 A'dan
B'ye: tepki düzeneği yok). Bulma: taşımadan sonra poz hatası < 0,5 m ve yön hatası < 30° olup koşu sonuna dek öyle kalan
dilimin başı. Yanlış sürüş: poz yanlışken rota izleme ve hareket komutu (s). Süreler taşımadan sonra, medyan / en çok.

| Senaryo | Tür | Varış v3 | Varış algi | Tepki v3 | Tepki algi | Bulma v3 | Bulma algi | Yanlış sürüş v3 | Yanlış sürüş algi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A'dan B'ye | aynı koridor, uzak | 5/12 | 12/12 | 0/12 | 12/12 (0,8 / 0,8) | 7/12 (6,7 / 84) | 12/12 (5,5 / 64) | 5,2 / 83 | 0,8 / 27 |
| A'dan B'ye | 180° | 8/12 | 12/12 | 0/12 | 11/12 (1,1 / 15) | 8/12 (6,0 / 25) | 12/12 (13 / 34) | 6,0 / 25 | 1,5 / 15 |
| A'dan B'ye | küçük (1-3 m) | 8/12 | 12/12 | 0/12 | 12/12 (1,4 / 13) | 8/12 (11 / 48) | 12/12 (10 / 38) | 7,2 / 48 | 1,4 / 13 |
| A'dan B'ye | başka koridor | 0/12 güvenli durma | 11/12 güvenli durma | 0/12 | 12/12 (0,8 / 0,8) | (harita yok) | (harita yok) | 9,9 / 120 | 6,6 / 41 |
| 6 harita | aynı koridor, uzak | 8/12 | 11/12 | 12/12 (0,7 / 4,6) | 12/12 (0,8 / 0,8) | 8/12 (8,9 / 48) | 11/12 (6,9 / 121) | 8,8 / 48 | 0,7 / 0,8 |
| 6 harita | 180° | 10/12 | 10/12 | 11/12 (1,8 / 13) | 12/12 (1,1 / 13) | 9/12 (5,8 / 54) | 12/12 (16 / 139) | 15 / 59 | 1,1 / 13 |
| 6 harita | küçük (1-3 m) | 11/12 | 12/12 | 12/12 (0,8 / 13) | 12/12 (0,8 / 13) | 12/12 (3,4 / 122) | 12/12 (7,4 / 57) | 3,2 / 121 | 0,8 / 13 |
| 6 harita | başka koridor | 10/12 | 11/12 | 11/12 (0,5 / 1,0) | 12/12 (0,8 / 0,8) | 9/12 (8,9 / 71) | 11/12 (5,8 / 50) | 8,8 / 70 | 0,7 / 0,8 |

A'dan B'ye başka koridor: tek haritalı beyin için hedef yok; başarı = yardım bekliyor, son 10 s'de < 5 cm yol, temas
yok. algi 11 / 12'de üç kurtarma denemesinden sonra durdu (her denemede kendi haritasında yanlış bir yere karar verip
yeniden "kayboldum" dedi; 1 koşuda üçüncü kararda yanlış yerde "vardım" dedi); v3 hiçbirinde durmadı (6'sı yanlış
koridorda "vardım", 6'sı süre sonuna dek sürdü).

Yanlış alarm (taşıma yok, 12 koşu / koşul; "kayboldum" koşu sayısı (toplam olay) ve varış):

| Senaryo | taban | insan 1/10 m | eşya 1/10 m | insan + eşya 1/10 m | insan + eşya 2/10 m |
| --- | --- | --- | --- | --- | --- |
| A'dan B'ye algi | 0 (0), 12/12 | 0 (0), 12/12 | 1 (2), 12/12 | 1 (2), 12/12 | 5 (10), 11/12 |
| A'dan B'ye v3 varış | 12/12 | 12/12 | 12/12 | 11/12 | 10/12 |
| 6 harita algi | 0 (0), 12/12 | 0 (0), 12/12 | 4 (11), 10/12 | 3 (7), 12/12 | 8 (24), 7/12 |
| 6 harita v3 varış (tepki koşu) | 12/12 (0) | 12/12 (0) | 12/12 (4) | 10/12 (3) | 8/12 (8) |

## Nasıl ölçüldü

- Benzetici: önceki aşamanın 2B benzeticisi (`harita_eskimesi/benzet2b.py`, değiştirilmedi; ONERI kinematiği, dönen
  LiDAR, odometri tabanı dönüş +%14). Taşıma hakem tarafında (`kos_tasinma.Kacirici`): yer gerçeği yolu rota boyunun
  U(0,25, 0,60)'ına ulaşınca benzeticinin gerçek pozu yeni poza konur; odometri değişmez. Başka koridorda benzeticinin
  dünyası o koridorunkiyle değiştirilir. Beyin yalnız tarama + odometri görür. Birim testi: taşımada odometri artımları
  sürülen yola eşit kalıyor (`testler/test_tasinma.py`).
- Taşıma türleri (`kacirma.py`): aynı koridorda uzak (taşıma uzaklığı medyan 6,2-6,8 m), aynı yerde 180°, orta hat
  boyunca 1-3 m (medyan 1,6-1,7 m), başka koridor (öbür 5'ten biri); yerleştirme `senaryo_kayip.rastgele_birak` kuralıyla.
- İki beyin: `ab` = `AbBeyni` (tek harita); `cok` = `KayipBeyni` 6 haritayla, bilinen başlangıçla karar verilmiş
  (izleme evresi; hedef orta hat sonu, başka koridora taşınınca aynı göreli hedef o koridorda).
- Sürümler aynı görevde eşli: dünya, başlangıç sapması, konumlayıcı tohumu, taşıma anı ve pozu, benzetici gürültüsü
  ortak (`kos_tasinma.py` başı).

## "algi" sürümü (isteğe bağlı, `algi.TasinmaBeyni`; varsayılan değişmedi)

1. Algı, her taramada beynin poz tahmininde: uyum = ışın ucu harita yüzeyine 0,20 m'den yakın ışın oranı (90 ışın);
   geçiş = ölçülen menzil ışın izlemeyle beklenenden 0,5 m uzun olan ışın oranı. Tarama kötü: uyum < 0,60, geçiş > 0,10
   ya da konumlayıcı `konum_kararsiz`. Son 10 taramanın 8'i kötüyse ya da poz tahmini bir taramada odometri
   öngörüsünden 1,0 m'den çok sıçradıysa (konumlayıcı kendi kendine başka yere atladı) ya da izleyici "bitti" derken
   algı "iyi" değilse: "kayboldum".
2. Kayboldum: 1 s dur; aynı aday haritalarla yeni konumlayıcı (küresel kafes başlangıcı: adaylar bütün haritaya
   yayılır), yavaş (0,15 m/s) tepkisel keşifle `KayipBeyni`'nin karar kuralı (p >= 0,9, 10 ardışık kararlı tarama), sonra
   aynı göreli hedefe yeniden plan. 3 kurtarmadan sonra ya da 150 s'de karar yoksa durur ("yardım").
3. Güvenli hız: şüphede (son 10 taramada >= 3 kötü) ya da `konum_kararsiz` iken hız 0,12 m/s'ye kırpılır (eğrilik korunur).

Eşikler tasarım değerleriyle başladı. Geliştirme kümesinde (koridor_2, 3, 5 x tohum 901-903) koridor_5 / 901'de iki
tekil koşu (180° ve küçük kaydırma) taramanın yanlış pozda da haritaya uyduğunu gösterdi; buna göre konumlayıcının
`konum_kararsiz`'ı, poz sıçraması ve "bitti ama şüpheli" algıya eklendi. Sonra geliştirme kümesinin tamamı bir kez
koşuldu (144 koşu: taşımada 71 / 72 varış, yanlış alarm 0 / 72) ve eşikler dondu; sınama kümesi (tohum 1, 2, 6 koridor)
yalnız bir kez koşuldu. `karma_3` (insan + eşya 2 / 10 m) geliştirmede hiç koşulmadı. Geliştirmede hiç kullanılmayan
haritalarda (koridor_1, 4, 6) algi'nin taşıma varışı 46 / 48, geliştirme haritalarında (2, 3, 5; ayrı tohum) 45 / 48
(v3: 34 / 48 ve 26 / 48).

## MuJoCo doğrulaması

A'dan B'ye, taban dünya, 5 koşu (koridor_5:1, koridor_1:2, koridor_3:1, koridor_6:2, koridor_4:2) x 4 koşul x 2 sürüm.
Taşıma `Duzenek.c.konum_ayarla` (MuJoCo tabanı ışınlanır) + LiDAR'ın yarım turu atılır; Duzenek'in enkoder odometrisi
değişmez. Sonuçlar `tablolar.md` "MuJoCo doğrulaması" (bu dosyanın sonundaki sayılar oradan).

| Tür | Varış v3 | Varış algi | Tepki algi (med / maks s) | Bulma v3 | Bulma algi (med / maks s) | Yanlış sürüş v3 / algi (med s) | Temas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aynı koridor, uzak | 3/5 | 5/5 | 5/5 (0,8 / 0,8) | 3/5 | 5/5 (6,5 / 76) | 8,4 / 0,8 | 0 |
| 180° | 4/5 | 5/5 | 4/5 (6,5 / 21) | 4/5 | 5/5 (18 / 27) | 20 / 3,4 | 0 |
| küçük (1-3 m) | 1/5 | 5/5 | 5/5 (3,4 / 12) | 1/5 | 5/5 (13 / 26) | 9,0 / 3,3 | 0 |
| yanlış alarm (taban) | 5/5 | 5/5 | 0 "kayboldum" | - | - | - | 0 |

v3'te 7 koşu yanlış yerde "vardım" dedi (2B'nin aynı 15 taşımasında 4). MuJoCo ile 2B aynı görevde 35 / 40 aynı sonuç;
uyuşmayan 5'in hepsi v3: küçük kaydırma 3 (MuJoCo başarısız, 2B başarılı), 180° 2 (biri bir yana, biri öbür yana).
v3'ün küçük kaydırmada MuJoCo'da daha kötü olması (1 / 5, 2B 4 / 5): kurtulma, rastgele saçılan parçacığın doğru yere
düşmesine bağlı, gerçek dönüş kaymasıyla bu daha seyrek. algi'nin 20 MuJoCo koşusu 2B ile birebir aynı sonuç. MuJoCo'da algı 180° ve küçük kaydırmada
2B'den geç tetikleniyor (medyan 3,4-6,5 s, 2B 1,1-1,4 s): gerçek dönüşte konumlayıcının kendi belirsizliği büyük.

## Gerileme denetimi (küçültülmüş)

`gerileme.py`: koridor_karisiklik'in tam kayıtları (`akis/`, fizik koşulmaz) v3 taramasıyla (kör maske) konumlayıcıya
yeniden beslendi; algı kurulu iken "kayboldum" -> `mcl.baslat()` (küresel yeniden başlatma). Kurma: D (bilinen
başlangıç) baştan, B / C'de KayipBeyni'nin karar kuralıyla. Koşulan alt küme: B tohum 1 (18 kayıt), C (insanlı, 18), D
(18) = 54; B'nin tohum 2-5'i (72 kayıt) koşulmadı, A bölümü (tek tarama) ilgisiz. Sürüş yok (açık çevrim): durma /
yavaşlama / keşif burada sınanmadı.

| Bölüm | kayıt | algı tetiklendi | yanlış koridora kesin: koşu v3 -> algi | adım v3 -> algi | konum kesin-yanlış adım | sonda doğru v3 / algi | ham_v3 ile aynı |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B t1 | 18 | 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 | 18 / 18 | 18 |
| C | 18 | 2 | 2 -> 2 | 577 -> 205 | 0 -> 0 | 18 / 18 | 18 |
| D | 18 | 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 | 18 / 18 | 18 |

C'deki iki tetiklenme: `C_koridor_5_bas_t101` (v3 557 adım koridor_6'ya kesin; algı 4,7 m'de 9 m poz sıçramasıyla
tetiklendi, yeniden başlatma sonrası 183 adım) ve `C_koridor_4_orta_t101` (v3 20 adım, algi 22 adım: 14,95 m'de 9,7 m
sıçrama). Yanlış koridora kesin karar sayısı artmadı, toplam adım azaldı; bir kayıtta 2 adım arttı.

Testler: `kod/testler/kos.py` 58 / 58; `kod/fizik/konumlama/kos.py` 31 geçti / 2 atlandı (yalnız `--uzun` ile koşan ikisi) / 0 kalan; önceki aşamanın testleri 12 / 12;
bu klasörün testleri 5 / 5. Ortak dosyalara dokunulmadı.

## Simülasyonun iyimser varsayımları ve sınırlar

- Taşıma anlık: robot kaldırılırken LiDAR'ın tavanı / taşıyan kişiyi görmesi, tekerin havada dönmesi (odometride sahte
  hareket), konulduktan sonraki sarsıntı yok. Gerçekte kaldırma sırasında tekerler dönerse odometri sahte yol bildirir.
- Dünya bozulmamış (taşımalı koşularda); yanlış alarm yalnız insan ve eşyayla ölçüldü. Cam, dönüşsüz yüzey, kapı
  değişimi, menzil düşüşü gibi önceki aşamanın kıran etkenleriyle algının yanlış alarmı ölçülmedi: dönüşsüz yüzeyde
  ölçülebilen ışın azalır, açık kapı / cam "geçiş" oranını yükseltir; yanlış alarm artabilir.
- 2B benzetici (önceki aşamada MuJoCo'ya göre konum hatasında iyimser); MuJoCo yalnız A'dan B'ye, 5 koşu / koşul,
  başka koridor ve 6 haritalı beyin MuJoCo'da koşulmadı.
- Koşul başına 12 koşu: 1-2 koşuluk farklar gürültü içinde. Başarısızlıklar CSV'de duruyor.
- Algının maliyeti: tarama başına 90 ışınlık ışın izleme + uzaklık alanı (bu PC'de ms mertebesi; Pi 5'te ölçülmedi).
  Kurtarmada 6 haritalı kafes başlangıcı ≈ 2,5 s (konumlama BENIOKU), robot bu sürede durur.

## Öneri (ölçülmedi)

Algı tarafı iyi çalışıyor; bedel kurtarma tarafında. Poz sıçramasıyla tetiklenen alarmda bütün haritalara küresel
yeniden başlatma yerine önce durup mevcut bulutun yeniden kararlı olmasını beklemek (v3'ün kendi "poz sıçradı"
davranışı eşyalı koşularda daha iyi sonuç verdi), uyum çöktüğünde ise küresel yeniden başlatma. Bunu geliştirme
kümesinde ayarlayıp yeni tohumlarla sınamak gerekir.
