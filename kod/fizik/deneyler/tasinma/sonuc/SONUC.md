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

## Tamamlama turu (2026-11-26): dört kip aynı koşullarda, "emin değilim" ölçütü

`kipler.py`, `emin.py`, `kipler_rapor.py`; tablolar `kipler_tablolar.md`, koşu başına `kipler_2b.csv`, özet
`kipler_ozet.json`. A'dan B'ye (tek harita, bilinen başlangıç), 2B benzetici, ONERI.

### Hüküm

- **Hiçbir kip her koşulda iyi değil; seçim taşınma riskine ve haritanın eskiliğine göre.** Varsayılan v3 DEĞİŞMEDİ
  (tam gerileme koşusu yok). Öneri tablosu aşağıda.
- **"algi" eskimiş haritada kullanılamaz durumda:** taşınma YOKKEN kapı %25'te 11 / 12, cam %50'de 11 / 12, kapı %50'de
  11 / 12, okul günü hafif 8 / 12, orta 10 / 12, ağır 12 / 12 koşuda boşuna "kayboldum" dedi. Nedeni neredeyse hep aynı:
  alarm taramasında **geçiş > 0,10** (açılmış kapının ya da camın arkasındaki odayı görmek, haritaya göre "duvarın
  arkası"); uyum < 0,60 hiçbirinde değil. Sonuç güvenli ama işe yaramaz: robot durup yardım bekliyor (kapı %25: 9 / 12
  güvenli durma, 3 / 12 varış). Dönüşsüz yüzey %50'de yalnız 1 / 12 alarm (dönüşsüz ışın NaN, geçişi büyütmüyor).
- **Taşınma varken algi fark ediyor:** temiz haritada 46 / 48 taşımada (medyan 0,8 s; 180°'de 10 / 12, 2,5 s), kapı /
  cam / dönüşsüz eskimesi altında küçük taşımada 30 / 30 (6 koşu taşımadan önce zaten alarm verip durmuştu; yapılan 30
  taşımanın 11'inde de taşımadan önce yanlış alarm vardı, bu yüzden eskimedeki fark etme oranı yanlış alarm eğilimiyle
  karışık); izleme_algi temizde 45 / 48, eskimede 29 / 30.
- **"izleme" eskimiş ama taşınmasız haritada en iyisi** (84 koşu / kip: varış 69 / 84; v3 57, algi 25, izleme_algi 27),
  **taşınmada en kötüsü** (temiz haritada 1 / 48: kendini kurtaramıyor, 36 koşuda süre doldu, 11'inde sessiz hata).
- **"emin değilim" ölçütü (sessiz hata azaltma) çalışıyor ama seçilen eşik fazla sıkı çıktı.** Geliştirmede seçilen
  kural (uyum medyanı < 0,75 VEYA ana mod std > 0,05 m) sınamada v3'ün 66 sessiz hatasının 33'ünü, izlemenin 48'inin
  41'ini durdurdu; bedeli 5 / 99 ve 5 / 86 doğru varışın gereksiz durması (geliştirme sınırı %2 idi, sınamada %5-6):
  gereksiz durmaların 17 / 21'i dönüşsüz yüzey %50'de std 0,051-0,066 m (az ışınla std büyüyor). Geliştirmenin en iyi
  TEK adaylı kuralı (uyum < 0,75) sınamada v3 29 / 66, izleme 25 / 48 sessiz hatayı durdurdu, gereksiz durma 0 / 99 ve
  0 / 86. Bu ikinci kural sınamaya bakıldıktan sonra öne çıktığı için hüküm değil, yeni tohumlarla doğrulanacak aday.

### Öneri tablosu (sınama, tohum 5, 6; hücre: doğru davranış / koşu, sessiz hata, güvenli durma)

"Doğru davranış": hedefe doğru varış; başka koridora taşımada güvenli durma. Sessiz hata: yanlış yerde "vardım" (123
sessiz hatanın 122'si hedefe > 0,5 m; 13'ü başka koridorda).

| Koşul (koşu / kip) | v3 | izleme | algi | izleme_algi | Öneri | Gerekçe |
| --- | --- | --- | --- | --- | --- | --- |
| Temiz harita, taşınma yok (12) | 12/12, 0, 0 | 12/12, 0, 0 | 12/12, 0, 0 | 12/12, 0, 0 | v3 (varsayılan) | fark yok; algi yanlış alarm 0 / 12 |
| Eskimiş harita, taşınma yok: okul günü hafif / orta / ağır + kapı %25, cam %50, kapı %50, dönüşsüz %50 (84) | 57/84, 20, 0 | 69/84, 13, 0 | 25/84, 1, 58 | 27/84, 1, 56 | **izleme** (+ "emin değilim" ölçütü) | en çok varış, v3'ten az sessiz hata; algi'nin yanlış alarmı 64 / 84 koşu |
| &nbsp;&nbsp;yalnız okul günü ağır (12) | 1/12, 7, 0 | 2/12, 8, 0 | 1/12, 1, 10 | 1/12, 1, 10 | hiçbiri; zorunluysa algi | hepsi ≤ 2 / 12; algi en azından durup yardım istiyor |
| Taşınma riski, temiz harita: 4 tür (48) | 13/48, 28, 0 | 1/48, 11, 0 | **47/48**, 1, 11 | 44/48, 4, 11 | **algi** | fark etme 46 / 48, medyan 0,8 s; v3'ün 28 sessiz hatası |
| Taşınma riski + eskime: kapı %25 / cam %50 / dönüşsüz %50, küçük (1-3 m) taşıma (36) | 17/36, 18, 0 | 4/36, 24, 0 | 11/36, 0, 23 | 11/36, 2, 22 | algi (sessiz hata 0) ya da v3 (daha çok varış, 18 sessiz hata) | iyi seçenek yok; algi'nin geçiş testi kapı / cam için düzeltilmeli |

Ek: temaslı koşu (taşınmasız eskimiş 84 koşuda) v3 5, izleme 1, algi 8, izleme_algi 4; algi'nin temaslarının 6'sı
okul günü orta / ağırda (kaynağı ayrıca incelenmedi; kurtarma evresinin keşif sürüşü olası). İstisna 0 / 720.

Bilinen başlangıçla gezinen robot için öneri (ölçülmedi, birleşik hâli): **izleme + "emin değilim" ölçütü + taşınma
algısının geçiş testi kapı açıklıklarında ve cam olabilecek yüzeylerde kapalı** (yalnız uyum ve poz sıçraması). Geçişsiz
algının yanlış alarmı ve fark etmesi koşulmadı; taşınmada 180° ve küçük kaydırmayı uyum yerine `konum_kararsiz` ve poz
sıçraması yakalıyordu (yukarıda "Fark etme süresi"), bu yüzden geçişi kapatmanın fark etmeyi ne kadar düşürdüğü açık.

### "Emin değilim, duruyorum" ölçütü (`emin.py`)

- Yalnız beynin gördüğü (pasif `kipler.Gozlemci`, komutu değiştirmez; birim testi): "vardım" anında son 10 taramada
  tahmin pozunda tarama-harita uyumu ve geçiş, konumlayıcının ana mod payı / std'si / `konum_kararsiz`'ı, koşu boyunca
  poz tahmininin odometri öngörüsünden en büyük sapması (poz sıçraması), rastgele saçma oranı. Kural vardım anında
  uygulandığı için gidişi değiştirmez; etkisi kayıtlı koşulardan çevrimdışı ve tam ölçülür.
- **Ayar ve hüküm ayrı:** geliştirme kümesi tohum 7, 8 (168 koşu: v3 ve izleme; taban, okul hafif / orta, kapı %50,
  cam %75, taşınma küçük / uzak); sınama tohum 5, 6 (720 koşu, dört kip). Seçim kuralı sınamadan önce yazıldı (`emin.py`
  başı): gereksiz durma ≤ %2, en çok yakalanan sessiz hata, eşit eşik aralığının ortası; iki adaylı kural ancak +2
  yakalarsa. Sonuç: `uyum < 0,75 VEYA std_xy > 0,05` (geliştirmede 26 / 38 yakalandı, 2 / 112 gereksiz).
- Sınama: v3 33 / 66, izleme 41 / 48, algi 1 / 2, izleme_algi 4 / 7 sessiz hata durduruldu; gereksiz durma 5 / 99,
  5 / 86, 6 / 84, 5 / 83. Std eşiği (0,05 m) normal değerin (0,02-0,05) hemen üstünde; geliştirmede dönüşsüz yüzey
  yoktu, sınamada gereksiz durmayı o yarattı. Ders: tek bir geliştirme kümesinde çıkan sıkı std eşiği taşınmıyor.
- Neyi yakalayamıyor: poz sıçraması (sic_maks) ayırt edici DEĞİL: v3 taşınmadan doğru kurtulduğunda da 0,4-16 m
  sıçrıyor (sınamada 0,4-11,8 m, geliştirmede 0,8-16,1 m; sessiz hatalarda 0,04-21,9 m).
  İzleme kipinde taşınmadan sonra sürüklenen tahmin hedefte haritaya iyi uyabiliyor (uyum 0,80-1,00): bu sessiz
  hataların bir kısmı tarama-harita uyumuyla görünmez.

### Nasıl ölçüldü, neyi değiştirdi

- Kipler aynı görevde eşli (dünya, başlangıç sapması, MCL tohumu, taşıma anı / pozu, benzetici gürültüsü). Tohum 5-8
  önceki hiçbir aşamada kullanılmadı. 6 koridorun hepsi. "algi" eşikleri önceki geliştirmede donmuştu, değişmedi.
- Hakem farkı (önceki ölçümlere göre daha katı): koşu yalnız beyin "vardım" deyince biter; "hedefte 1,5 s durdu"
  kısa yolu kapalı. Süre rota / 0,25 x 1,8 + 130 s (önceki aşamada taşınmasız koşularda + 40 s). Bu yüzden ve tohumlar
  farklı olduğundan sayılar önceki tablolarla birebir karşılaştırılmaz. Güncellendi: harita_eskimesi'nin izleme
  varyantında (tohum 3, 4) okul günü orta 12 / 12 idi, burada (tohum 5, 6) 8 / 12; kapı %50 12 / 12 burada da 12 / 12.
- Güncellendi: yukarıdaki "Yanlış alarm bedeli" yalnız insan ve eşyayla ölçülmüştü (taban / insan 0 / 48); kapı, cam ve
  okul gününde yanlış alarm 8-12 / 12 (bu bölüm).
- **Kapsam daraltıldı (süre bütçesi):** ilk plan 29 sınama koşuluydu, 15'i koşuldu. Koşulmayanlar: tek etkenlerin
  2. kademesinden eşya, insan, grup, ölçek, genişlik, menzil, ani kayma, dönüşsüz %25 (8);
  cam %75, dönüşsüz %75, menzil 4 m (3); taşınma + eskimede yalnız küçük (1-3 m) taşıma koşuldu, planlanan uzak
  taşıma (kapı %25 / cam %50 / dönüşsüz %50 ile, 3) koşulmadı (180° ve başka koridor eskimeyle planda da yoktu;
  eğrilme, gürültü ve odometri hatası bu karşılaştırmanın planında yoktu). cam_3'ün yarıda kesilen 9 koşusu ham klasörde durur, tablolara girmez. Geliştirme
  kümesi de 10'dan 7 koşula indi (dönüşsüz %75, menzil 4 m, eşya 4 / 10 m atıldı). Yalnız A'dan B'ye; 6 haritalı
  beyin ve MuJoCo bu turda koşulmadı. Koşul başına 12 koşu: 1-2 koşuluk farklar gürültü içinde.
- İyimser varsayımlar önceki bölümlerdeki gibi (2B, ideal ince duvar, cam yalnız kapılarda ve tam saydam, anlık taşıma).
- Testler (tamamlama turu sonunda): `kod/testler/kos.py` 74 geçti / 2 atlandı / 0 kalan; bu klasör 9 / 9 (yeni
  `test_kipler.py` 4); harita_eskimesi 14 / 14. Ortak dosyalara dokunulmadı.

## Öneri (ölçülmedi)

Algı tarafı iyi çalışıyor; bedel kurtarma tarafında. Poz sıçramasıyla tetiklenen alarmda bütün haritalara küresel
yeniden başlatma yerine önce durup mevcut bulutun yeniden kararlı olmasını beklemek (v3'ün kendi "poz sıçradı"
davranışı eşyalı koşularda daha iyi sonuç verdi), uyum çöktüğünde ise küresel yeniden başlatma. Bunu geliştirme
kümesinde ayarlayıp yeni tohumlarla sınamak gerekir.
