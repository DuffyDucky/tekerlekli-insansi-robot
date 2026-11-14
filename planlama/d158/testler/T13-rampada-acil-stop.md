# T13 · Rampada acil stop: kayma yolu ve ip yükü

Kâğıt T13 / 13 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

5°'lik rampada acil stop basılınca (motor ve servo gücü kesilince) robotun **kendi kendini tutup tutmadığını** ölçmek: taban ipinin
taşıdığı yük, robotun rampadan aşağı kayma yolu ve hareket hâlindeyken acil stopla duruş yolu. Sonuç, fren ya da kilit gerekip
gerekmediği kararına (karar kuyruğu) veri olur.

## Neden önemli

Acil stopta röle K1 bırakır, motor sürücüleri güçsüz kalır, motorlar boşa düşer. Rampada bu durumda robotun kayması ivme sınırıyla
kapanmıyor; dinamik fren "isteğe bağlı" bırakıldı (`kararlar:83`, `duzeltme-plani.md:63`). Robotu tutan tek şey motorların dişli kutusudur;
dişli kutusunun geri sürülüp sürülmediği bilinmiyor. Geri sürülüyorsa 26 kg'lık, 1,58 m'lik robot acil stoptan sonra rampadan yuvarlanır.
Tersine, dişli kutusu aniden kilitlenirse inişte ani duruş robotu öne devirebilir.

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Acil stopta motorlar boşa düşer; rampada kayma bu sınırla kapanmaz | `kararlar:83`, `duzeltme-plani.md:63` (E6) | **Açık risk**, ölçülmedi |
| Röle yalnız mantar serbest ve "devreye al" komutu varken çeker; komut kalkınca ya da mantara basılınca bırakır | `elektrik.md:216-222` | Tasarım |
| Rampa 5°; rampada sürüş ve fren ≤ 0,1 m/s² | `kararlar:7-8`, `kararlar:77` | Karar 29.10 |
| Robot kütlesi 25,911 kg | `taban-analiz.json` `donus.kutle_kg` | Model (akü 3,0 kg güncellemesi P1.1 öncesi); [T9](T9-zemin-rampa.md) A'da tartılan değer kullanılır |
| Yuvarlanma direnci katsayısı 0,03 | `arayuz.py:667` | Hesap varsayımı |
| Rampada ev pozunda devrilme ivmesi (en kötü yön) 2,41 m/s²; pay 1,5 ile izin verilen 2,41 ÷ 1,5 = 1,61 m/s² | `taban-analiz.json` `robot.pozlar[ev].rampa5.geri` (2,41 ÷ 1,5; pay ≥ 1,5: `uygulama-notu.md:35`) | Hesap, ölçülmedi |
| Acil stop mantarı etek plakasında; elde taşınan uzaktan acil stop yok | `arayuz.py:436`, `arayuz.py:466` | Tasarım |
| Röle bıraktıktan sonra PC817 #2 bara kontrolü 500 ms | `elektrik.md:225` | Yazılım kuralı, denenmedi |
| Pi'den 500 ms mesaj gelmezse tekerler durur; kumandada ölü adam tuşu (bırakınca durur) | `yazilim-plani.md:35`, `yazilim-plani.md:75`, `yazilim-plani.md:78` | Yazılım planı, denenmedi |
| Kablosuz kumanda koparsa Pi kalp atışını sürdürür, son hız komutu kalabilir | `tubitak-2209b/taslak/hakem-v9/hakem-3.md:105` (salt okunur) | Risk notu, doğrulanmadı |
| Elde yükle rampa yasak | `karar-kuyrugu.md` K9 | Hesap |

**Bu kâğıtta türetilen değerler (hesap, m = robot kütlesi, α = 5°):**
- Robotu rampada tutmak için gereken kuvvet (hiç direnç yoksa): m × sin 5° = 25,911 × 0,0872 = **2,26 kg** (kantar kg gösterir).
  Robot ipe tamamen asılırsa kantar en çok bunu okur.
- Dişli kutusu hiç tutmazsa robotun boşta ivmesi: 9,81 × (sin 5° − 0,03 × cos 5°) = **0,56 m/s²**. 2 cm ip boşluğunu aldığında hızı
  √(2 × 0,56 × 0,02) = **0,15 m/s** olur (B'deki ip boşluğu bu yüzden küçük).
- Hareket hâlindeyken acil stopla duruş yolu d ve hız v için ortalama yavaşlama a = v² ÷ (2 × d). Devrilme sınırı a ≤ 1,61 m/s² →
  d ≥ v² ÷ 3,22 (metre), yani **d ≥ 31 × v² cm**; yazılımın rampadaki normal duruşu (0,1 m/s²) → d ≤ v² ÷ 0,2 (metre), yani **d ≤ 500 × v² cm**
  (v m/s cinsinden). Örnek v = 0,20 m/s: 31 × 0,04 = 1,2 cm ≤ d ≤ 500 × 0,04 = 20 cm.

## Gereken alet

- **[T9](T9-zemin-rampa.md) B düzeneğinin tamamı:** iki emniyet ipi (taban ipi ve devrilme ipi), sabit dayanak, şerit metre, bant işareti,
  tripodda telefon (en az 30 kare/s), enkoder kaydı varsa o
- **Dijital el kantarı** (bagaj tartısı, 10 g çözünürlük): taban ipinde, robot ile dayanak arasında
- Kumanda (sürüş ve "devreden çıkar"; hangisi olduğu D1'de yazılır) ve ESP32 yazılım kaydı (bara durumu PC817 #2; enkoder varsa)
- Telefon ivmeölçer uygulaması (C'de yardımcı), kronometre
- Taban ipini dayanağa **sabitlemek** için kilitli karabina ya da sağlam düğüm (A ve B'de ip elde değil, bağlı durur)
- İpte boşluğu işaretlemek için renkli bant

## Güvenlik

- **Ön şart:** [T1](T1-jgb37-durma-torku.md) GEÇER ya da KOŞULLU ve [T9](T9-zemin-rampa.md) B **GEÇER**. T13, T9-B ile aynı gün, aynı ip düzeneğiyle
  yapılır. T9'un bütün güvenlik maddeleri geçerlidir (iki ip, düşme hattı 1,6 m, hareket varken robota el yok, elde yük yok).
- **Bu kâğıtta durdurucu yalnız taban ipidir.** Acil stop motorları keser, robotu durdurmaz; ölçülen şey de budur.
- **Acil stop bu kâğıtta kumanda komutuyla verilir.** Mantar robotun etek plakasındadır (`arayuz.py:436`, `arayuz.py:466`); robot
  rampadayken ona düşme hattının dışından ulaşılamaz ve elde taşınan uzaktan acil stop yoktur ([00-genel.md](00-genel.md) ortak kural 1).
  Kumandadaki "devreden çıkar" komutu ESP32'de GPIO4'ü 0 yapar (14.11 pin kararı sürüm 4; önceden GPIO12), röle K1 bırakır, anahtarlı bara kesilir: mantara basmakla aynı sonuç
  (`elektrik.md:216-222`). Bu yol, Yöntem'deki **ön şartlar D1–D3** düz zeminde sağlanmadan ve D4 yazılmadan rampada kullanılmaz. Robotun üstündeki mantara
  basmak için kimse düşme hattına girmez (istisna: aşağıdaki "komut çalışmazsa" adım 4).
- **En az 3 kişi, ayrı görevlerle:** (1) taban ipi, (2) devrilme ipi, (3) kumanda (sürüş ve "devreden çıkar"). **Kumandayı tutan ip tutmaz;
  ip tutan kumanda tutmaz.** Video tripodda kendi kendine çeker; dördüncü kişi varsa kantarı ve kaydı izler. Üç kişi yoksa T13 yapılmaz.
- **Sıra kuralı:** D1, D2 ve D3 sağlanmadan T13'ün hiçbir bölümü yapılmaz (A ve B'de de robot rampaya sürülür ve acil stop komutla
  verilir; [00-genel.md](00-genel.md) ortak kural 1). A GEÇER olmadan B yapılmaz.
  **C, ancak A ve B GEÇER ve D1, D2, D3 sağlanmışsa yapılır. Biri eksikse C YAPILMAZ;** sonuç kutusuna "C yapılmadı: doğrulanmış durdurma
  yolu yok" yazılır ve karar kuyruğuna gider. Robot ipe asılıyorsa (A KALIR) robota ipte boşluk bırakılmaz.
- **Çıkışta ipler robotu durdurmaz.** Taban ipi robotu yalnız aşağı yönde tutar; devrilme ipi çekmek için kullanılmaz ([T9](T9-zemin-rampa.md)
  güvenlik). Çıkışta robot durmazsa rampanın üst ucuna ve ötesine gider. Bu yüzden: **robotun gidiş doğrultusu boştur** (rampanın üst ucundan
  sonra da en az 3 m; varsayım); **dayanak ve taban ipini tutan kişi bu doğrultunun dışında**, üst ucun yanında durur (doğrultudan en az 1 m
  yanda; varsayım). Çıkış denemelerinde acil stop rampanın **alt yarısında** verilir. İnişte de rampanın alt ucu ve ötesi boştur, orada
  kimse durmaz ([T9](T9-zemin-rampa.md) güvenlik).
- **Komut 1 s içinde barayı düşürmezse** (robot 1 s sonra hâlâ aynı hızla gidiyor ya da kayıt barayı açık gösteriyor):
  1. Kumandayı tutan "ip!" diye bağırır, sürüş komutunu sıfırlar ve ölü adam tuşunu bırakır (`yazilim-plani.md:78`). İpleri tutanlar
     ipleri gergin tutar; inişte taban ipi robotu tutar.
  2. D4'te denenmiş yedek yol varsa uygulanır (ESP32'yi uzaktan resetlemek: reset anında GPIO4 LOW, röle bırakır; `elektrik.md:226`,
     `elektrik.md:229`). D4 aynı telsiz bağlantısına bağlıdır, bağlantı koptuysa o da çalışmayabilir. D4'te denenmemiş bir yol rampada denenmez.
  3. **Kimse düşme hattına ve robotun gidiş doğrultusuna girmez,** robotun önüne geçilmez.
  4. Robot ipte hareketsiz durunca (ipler gergin) ya da düz zemine çıkıp durunca mantara basılır. Bu anda bara açıktır: **kollar da
     güçlüdür** ve yazılım hatalı olabilir. Mantar etek plakasının arka-sağ köşesindedir (`arayuz.py:436`). Görevi yalnız mantar olan
     kişi **rampanın üst tarafından**, mantarın bulunduğu **arka köşeden**, **kol hizasının arkasından**, **tek kolla** uzanır; gövdesi
     rampanın alt tarafına geçmez; devrilme ipi bu sırada gergin tutulur; basınca eli hemen çeker. Arka köşe rampanın alt tarafına
     bakıyorsa (robot yukarı dönük) mantara uzanılmaz: taban ipi dayanağa sabitlenir, ipler gergin kalır, durum Efe'ye bildirilir; robot
     ancak bağlantı yeniden kurulup bara komutla kesildikten sonra (ya da aşağıdaki 5 dk kuralıyla mantara basıldıktan sonra) indirilir. Bara kesildikten sonra robot iplerle düz zemine indirilir.
     Bu dalda beklerken:
     - **Devrilme ipi de** rampanın üst tarafındaki **ikinci bir sabit noktaya** bağlanır ve elde tutulmaz.
     - Tekerlerin dönmediği ve koku ya da ısınma olmadığı **alan dışından** izlenir.
     - Bağlantı **en çok 5 dk** içinde (varsayım) geri gelmezse, iki ip sabitken mantara rampa doğrultusuna dik, **yandan** uzanılır:
       ayaklar robotun arka kenarının yukarısında, tek kolla, gövde robotun aşağısına geçmeden. Rampada devrilme, ipler sabitken rampa
       boyunca olur, yana olmaz (`taban-analiz.json` `robot.pozlar[ev].rampa5.yan` 3,16 m/s², en büyük pay). Mantara basılınca bara
       kesilir; robot iplerle düz zemine indirilir.
  5. T13 durdurulur; sonuç "KALIR: durdurma yolu çalışmadı", karar kuyruğuna ve yazılım ekibine (Efe).
- **İp boşlukları:** A'da taban ipi boşluksuz ve dayanağa bağlı; B'de bağlı ve **tam 2 cm** boşluklu; C'de T9'daki gibi elde, boşluk **≤ 10 cm**.
  Devrilme ipi her bölümde elde, boşluk ≤ 10 cm.
- Kantar ve ip, robotla dayanak arasındadır; kantar ekranı alan dışından okunur (gerekirse ekran telefonla çekilir). İpin doğrultusunda durulmaz.
- Acil stoptan sonra kollar güçsüz kalır; ev pozunda oldukları için yalnız biraz sarkarlar. Kol çevresinde kimse yoktur.
- **Robotu rampadan indirmek:** robot ipe asılıysa (yuvarlanıyorsa) ipler gergin tutularak yavaşça düz zemine bırakılır. Robot kendini
  tutuyorsa güçsüz itilmez: herkes yerindeyken yeniden devreye alınır (motor komutu sıfır, `elektrik.md:223-224` kuralı) ve en düşük hızla
  ipler takip ederek indirilir.
- Saat, yüzük, bileklik çıkar.

## Yöntem

**Ön şartlar (robot düz zeminde, rampaya çıkmadan; sonuç Tablo 0'a)**

- **D1:** Efe "devreden çıkar" komutunun var olduğunu ve hangi kumandada olduğunu (telefon / gamepad) yazılı teyit eder (soru:
  `dongu-158.md:162`).
- **D2:** Robot düz zeminde dururken komut **3 kez** verilir; her seferinde yazılım kaydından bara durumunun (PC817 #2) düştüğü an okunur.
  Gecikme (komut → bara düştü) her denemede **≤ 0,5 s** (varsayım; `elektrik.md:225`'teki 500 ms bara kontrolüyle aynı büyüklük).
  Yazılım kaydı yoksa D2 sağlanmamış sayılır.
- **D3:** Kumanda bağlantısı kesilince tekerler **≤ 0,5 s** içinde durur (`yazilim-plani.md:35`, `yazilim-plani.md:75`; risk:
  `tubitak-2209b/taslak/hakem-v9/hakem-3.md:105`). Bu denemede robotun durmaması da beklenen bir sonuçtur; bu yüzden robot **yürüyemez**:
  - **Esas düzen: tekerler havada** (`yazilim-plani.md:75`'teki kabul denemesiyle aynı). Enerji yokken robot şasiden takozlarla kaldırılır,
    tekerler yere değmez; takozlar şasiye oturur, gövdeye değil. Tekerler en düşük hızla dönerken bağlantı kesilir (telefon uygulaması ya da
    gamepad kapatılır). Dönen tekere ve takozlara kimse el uzatmaz.
  - Takozla kaldırmak olmuyorsa: robot yerde, **taban ipi robotun arkasındaki sabit dayanağa ≤ 0,5 m boşlukla bağlı** (0,5 m varsayım; elde değil); robot
    en düşük hızla dayanaktan uzaklaşırken bağlantı kesilir. Durmazsa ip robotu en çok 0,5 m sonra tutar; robotun önünde kimse durmaz.
    Bu düzende hız **≤ 0,1 m/s** (varsayım; ip birden gerilince daha hızlı robot öne devrilebilir); **devrilme ipi** [T9](T9-zemin-rampa.md)'daki
    gibi omuz altından bağlı ve elde, boşluk ≤ 10 cm; 1,6 m'lik düşme hattında kimse yok. **0,1 m/s'ye inilemiyorsa yalnız "tekerler havada"
    düzeni kullanılır.**
  - 3 deneme. Ölçüm tripod videosundan (havada: teker; yerde: robot): kapatan el kamerada görünür; kapatma karesi ile tekerin / robotun
    durduğu kare arası ≤ 15 kare (30 kare/s). Ölü adam tuşu varsa (`yazilim-plani.md:78`) bırakınca da durduğu bir kez görülür.
  - Durmazsa: ölü adam tuşu bırakılır, D2 komutu denenmez (aynı bağlantıdan geçer); tekerler havadaysa dönmeye bırakılır ve görevi yalnız
    mantar olan kişi mantara tekerlerden uzak, arka köşeden basar; yerdeyse robot ipte durduktan sonra aynı biçimde basılır. D3 sağlanmadı.
- **D4 (yedek yol):** ESP32'yi uzaktan resetlemek (Pi üzerinden) mümkünse düz zeminde bir kez denenir, baranın düştüğü görülür. Yoksa
  "yok" yazılır; o zaman yedek yalnız ölü adam tuşu ve iplerdir. **Not:** D4 de Pi'ye telsiz bağlantıyla ulaşır; kumanda bağlantısı
  koptuğu için komut çalışmadıysa D4 de çalışmayabilir. O durumda yedek yine ölü adam tuşu ve iplerdir.

Robot ölçüm noktası: rampanın ortası (alt uca ve üst uca en az robot boyu kadar; varsayım). Dayanak ve ipi tutan kişi robotun düşme
hattının (1,6 m) dışında ve çıkışta robotun gidiş doğrultusunun dışında kalmalı (güvenlik). Rampa eğimi ve hız [T9](T9-zemin-rampa.md)
tablosundan alınır. Rampa, ölçüm noktası şartına ve C'de sabit hıza ulaşmaya yetmiyorsa C'deki hız v düşürülür (en az 0,1 m/s,
[T9](T9-zemin-rampa.md) adım 10'un şartı). Kollar ev pozunda.

**A. Durarak ip yükü (taban ipi boşluksuz, bağlı)**

1. Robot düz zeminde, enerji yokken: kantarı taban ipine (robot ile dayanak arası) tak, şerit metre ve bant işareti T9'daki gibi.
2. Robotu en düşük hızla, ipler takip ederek rampanın ortasına sür ve durdur (yazılım "dur": motor komutu 0). 10 s bekle. Robot
   kendiliğinden kayıyorsa durma, doğrudan adım 3'e geç ve not al.
3. İpi tutan kişi taban ipini **boşluksuz** gerer (kantar birkaç on gram göstersin) ve dayanağa **sabitler**. Kantarı oku: **F_ön**.
4. 10 s sonra kantarı yeniden oku: **F_dur** (yazılım duruşunda robot ipe yük bindiriyor mu).
5. Alan dışından acil stop (devreden çıkar). İlk darbe değil, **2 s sonraki kararlı** kantar değerini oku: **F_acil**. 30 s daha bekle, yine oku.
6. Robotu yeniden devreye al (güvenlik: indirme kuralı), rampanın altına indir. A'yı **3 kez** yap.

**B. Durarak kayma yolu (taban ipi 2 cm boşluklu, bağlı) — yalnız A GEÇER ise**

7. Robotu yine rampanın ortasına sür, durdur. Taban ipini önce boşluksuz ger, sonra dayanaktaki bağlantıyı **2 cm** gevşetip yeniden sabitle
   (ipte banttan banda ölç). Tabandaki bant işaretinin şeritteki yerini yaz (**x0**, mm).
8. Video kaydını başlat. Alan dışından acil stop. **30 s** bekle (varsayım: yavaş sürünmeyi görmek için). İşaretin yeni yerini yaz (**x30**).
   Kayma = x30 − x0. İp gerildi mi (kantar F_ön'den yükseldi mi) bak.
9. Robotu devreye al, indir. B'yi **3 kez** yap.

**C. Hareket hâlinde acil stop — yalnız A ve B GEÇER ve D1, D2, D3 sağlandıysa; değilse YAPILMAZ**

10. Başlamadan Tablo 0'a bak: D1, D2, D3 işaretli değilse C yapılmaz. Görevler: taban ipi, devrilme ipi, kumanda ayrı kişilerde.
    İpler T9'daki gibi: taban ipi elde, dayanaktan geçer, boşluk ≤ 10 cm. Kantar taban ipinin **robot ucuna yakın** takılır (dayanaktan
    geçen ipte takılmasın) ya da C'de çıkarılır. **İlk deneme ölçüm değildir:** en düşük hızla
    rampada yukarı çıkarken, rampanın **alt yarısında** acil stop; ipleri ve komutu dener.
11. Ölçüm: robot [T9](T9-zemin-rampa.md)'daki sabit hızla (v, m/s) giderken alan dışından acil stop: inişte rampanın ortasında, çıkışta **alt yarısında** (güvenlik). **3 kez inişte, 3 kez
    çıkışta.** Her denemede videodan oku: hızın düşmeye başladığı kare (acil stop anı; motorlar o anda güç kaybeder) ile robotun durduğu kare
    arasındaki yol **d** (cm, şeritten). Enkoder kaydı varsa d oradan alınır, acil stop anı bara durumunun (PC817 #2) düştüğü an.
12. Robot durduktan sonra 30 s bekle; bu sürede ek kaymayı (cm) ve kantarı oku. Videoda teker kalkması ve devrilme ipinin gerilip
    gerilmediğine kare kare bak. Telefon ivmesinin duruştaki en büyük değerini (0,5 s kayan ortalama, [T9](T9-zemin-rampa.md) adım 11) yardımcı olarak yaz.

## Kayıt tablosu

Tablo 0: ön şartlar (düz zemin)

| Şart | Sonuç | Değerler |
|---|---|---|
| D1 komut teyidi (Efe) | ☐ var ☐ yok | Kumanda: ______ |
| D2 bara düşüş gecikmesi, 3 deneme (≤ 0,5 s) | ☐ sağlandı ☐ sağlanmadı | ______ / ______ / ______ s |
| D3 bağlantı kopunca duruş, 3 deneme (≤ 0,5 s) | ☐ sağlandı ☐ sağlanmadı | ______ / ______ / ______ s; düzen ☐ tekerler havada ☐ yerde, ip ≤ 0,5 m; ölü adam tuşu ☐ durdu ☐ yok |
| D4 yedek yol (ESP32 uzaktan reset) | ☐ denendi, çalıştı ☐ yok | |

Görevler: taban ipi ______  devrilme ipi ______  kumanda ______  video/kantar ______

Rampa yeri: ______  Eğim (T9): ______ °  Robot kütlesi m (T9 A): ______ kg  m × sin α = ______ kg   Acil stop yolu: ☐ yazılım komutu ☐ başka: ______

Tablo 1: A, durarak ip yükü (kg)

| Deneme | F_ön | F_dur (yazılım "dur", 10 s) | F_acil (2 s sonra, kararlı) | F_acil, 30 s sonra |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

Tablo 2: B, durarak kayma (ip 2 cm boşluklu)

| Deneme | x0 (mm) | x30 (mm) | Kayma x30 − x0 (mm) | İp gerildi mi |
|---|---|---|---|---|
| 1 | | | | ☐ hayır ☐ evet |
| 2 | | | | ☐ hayır ☐ evet |
| 3 | | | | ☐ hayır ☐ evet |

Tablo 3: C, hareket hâlinde acil stop (sabit hız v = ______ m/s; sınırlar: d ≥ 31 × v² = ______ cm, d ≤ 500 × v² = ______ cm)

| Deneme | Yön | Duruş yolu d (cm) | 30 s'de ek kayma (cm) | Teker kalktı / devrilme ipi gerildi |
|---|---|---|---|---|
| 1 | iniş | | | ☐ hayır ☐ evet |
| 2 | iniş | | | ☐ hayır ☐ evet |
| 3 | iniş | | | ☐ hayır ☐ evet |
| 4 | çıkış | | | ☐ hayır ☐ evet |
| 5 | çıkış | | | ☐ hayır ☐ evet |
| 6 | çıkış | | | ☐ hayır ☐ evet |

Telefon, duruşta en büyük ivme (yardımcı): iniş ______ m/s², çıkış ______ m/s²   Video dosyaları: ______

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| A: ip yükü artışı, F_acil − F_ön (3 denemenin en büyüğü) | **≤ 0,10 kg** (dişli kutusu robotu tutuyor; tam asılma 2,26 kg olurdu) | **Varsayım:** kantar çözünürlüğünün 10 katı; 2,26 kg türetilen |
| B: 30 s'de kayma (3 denemenin en büyüğü) | **≤ 1,0 cm** ve ip gerilmedi | **Varsayım:** robot dururken x0 ve x30 mm bölmeli şeritten doğrudan okunur, okuma payı ±0,5 cm ([T9](T9-zemin-rampa.md) adım 10'daki ±1 cm hareketli video okuması içindir) |
| C: duruş yolu d, her denemede | **31 × v² ≤ d ≤ 500 × v²** (d cm, v m/s) | Alt: `taban-analiz.json` `robot.pozlar[ev].rampa5.geri` 2,41 ÷ 1,5 = 1,61 m/s²; üst: `kararlar:77` (0,1 m/s²) |
| C: ön şartlar D1, D2, D3 | **sağlandı** (değilse C yapılmaz) | Bu kâğıdın güvenlik bölümü |
| C: durduktan sonra 30 s'de ek kayma | **≤ 1,0 cm** | B ile aynı (varsayım) |
| C: teker kalkması, devrilme ipinin gerilmesi | **0** | `uygulama-notu.md:35` (pay ≥ 1,5) |

Alt sınır (31 × v²) 1 cm'nin altında kalıyorsa video bunu ayıramaz: o zaman alt sınır yerine "teker kalkması 0" ve telefon ivmesi
≤ 1,61 m/s² esas alınır. F_dur da yalnız kayıttır: yazılım duruşunda robot ipe yük bindiriyorsa yazılım ekibine not.

Sonuç: A, B ve C GEÇER → **GEÇER** (acil stoptan sonra robot rampada kendini tutuyor). A ya da B KALIR → **KALIR: robot yuvarlanıyor**.
C'de teker kalktı ya da devrilme ipi gerildi → **KALIR: ani duruş**. C'de d alt sınırın altında ama teker kalkmadı ve devrilme ipi
gerilmedi → **KOŞULLU: ani duruş** (alt sınır ortalama yavaşlamadan türetildi, tutucudur; veri tasarım ajanında değerlendirilir).
C'de d üst sınırın üstünde ya da ek kayma > 1 cm → **KALIR: geç duruş**. Komut barayı 1 s içinde düşürmedi → **KALIR: durdurma yolu
çalışmadı**. Ön şart eksik olduğu için C yapılmadı → **C yapılmadı** (kuyruğa).

## Sınır aşılırsa

- **Her sonuçta:** `karar-kuyrugu.md`'ye yeni madde açılması için tasarım ajanına verilir: "Rampada acil stop sonrası fren / kilitleme
  gereksinimi", veri olarak bu kâğıdın tabloları. Karar **Ahmet Yorulmaz**'da. Sonuç `kararlar:83` notuna da işlenir.
- **KALIR, robot yuvarlanıyor:** kaynakta geçen seçenek dinamik fren (motor uçlarını röleyle kısa devre etmek, `duzeltme-plani.md:63`).
  Not: kısa devre freni hızla orantılı fren yapar; yuvarlanmayı yavaşlatır ama durarak tutmayabilir (yavaş sürünme kalır), bunu tasarım
  ajanı değerlendirir. Karar verilene kadar robot rampada yalnız taban ipiyle ve bu kâğıttaki düzenekle kullanılır.
- **KALIR ya da KOŞULLU, ani duruş:** dişli kutusu ani kilitleniyor; devrilme hesabı (`uygulama-ivme.json`, `taban-analiz.json` `robot.pozlar`) ölçülen d ile
  tasarım ajanında yeniden. Karar Ahmet Yorulmaz'da.
- **KALIR, geç duruş:** robot acil stoptan sonra yazılımın normal rampa duruşundan daha uzun yol alıyor; tasarım ajanına ve yazılım ekibine (Efe).
- **C yapılmadı (ön şart eksik) ya da KALIR, durdurma yolu çalışmadı:** karar kuyruğuna "rampada hareket hâlinde doğrulanmış durdurma
  yolu yok"; yazılım ekibine (Efe) D1–D3 için. Ön şart eksikse bu kapanana kadar robot rampada sürülmez ([00-genel.md](00-genel.md) ortak kural 1).
- [T9](T9-zemin-rampa.md) adım 13'teki ip yükü ölçümü bu kâğıdın A bölümüyle yapılır.

## Sonuç

A ☐ GEÇER ☐ KALIR (ΔF en büyük ______ kg)   B ☐ GEÇER ☐ KALIR ☐ yapılmadı (kayma ______ cm)   C ☐ GEÇER ☐ KOŞULLU ☐ KALIR ☐ yapılmadı (d ______ cm)

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
