**KAYNAK GEÇER**

# F10j kontrol-2 · P10.7b2b düzeltme turu 1'e dar bakış (kaynak düzeyi, salt okuma)

15.11.2026; başlangıç 08:37, koşular 08:41, rapor 08:45 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `4a097fb`. Depoda yazılan tek
dosya bu rapor. FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları, başsız tarayıcı ve `rehber_kol_kablo.py --yazma` koşmadı; bozmalar
bellekte ya da depo dışı geçici klasörde. Commit / push / `git add` yok. Kapsam yalnız bu turun değiştirdikleri: turdan önceki kopya
(ajanın depo dışı "önce" kopyası) ile bugünkü dosyalar karşılaştırıldı. Kopyanın onay kaydı SHA-256'sı ilk kontrolün gördüğü kayıtla
(E33E52F6…) aynı, yani kopya gerçekten turdan önceki durum.

Hüküm gerekçesi: F1'in dört durumu güvenli ve tek anlamlı; K2 madde 5 geri sarmıyor; sayılar kayıtla aynı; onay kaydı farkında
istenmeyen değişiklik yok; bütün koşular çıkış 0; kendi bozmalarımın hiçbiri sessiz geçmedi (kuralın kaçırdıklarını onay kaydı
yakaladı); kanca eşleşmesi 0. Aşağıdakiler kayıtlı açık iş.

## F1 · G07 ölçümünün üç maddesi (`tasarim/freecad/rehber/rehber_metin.py:922-945`)

Ölçüm: `rehber_metin` içe aktarıldı (yer tutucular `rehber_deger` ile çözülür). `COZUM_HATA` boş, çözülmemiş `{…}` / `⟦?⟧` 0. F1
`kontrol` 5 madde; G07 maddeleri 631 / 831 / 888 karakter (günlükle aynı). Çözülmüş metin günlükteki "Yeni (çözülmüş, üç madde)"
metniyle harfi harfine aynı.

**Dört durum** (metin harfiyen izlendi):

| Akü gerilimi | Bölücü okuması | Varılan yer | Yargı |
|---|---|---|---|
| aralıkta | bant içinde | madde 2: "bölücü geçer"; kapat → ayır → sök | güvenli, tek anlamlı |
| aralıkta | bant dışında | madde 3: kapat → ayır → sök; bölücü bozuk; listedeki yerler; düzelene kadar ana anahtar, ESP32 ve aşama 2 yasak; kusur yoksa da dur, kayda yaz | güvenli, tek anlamlı |
| aralık dışında | (okunmaz) | madde 1: "burada dur"; bölücüye geçilmez, ana anahtar açılmaz, aşama 2 yok | güvenli, tek anlamlı |
| aralık dışında | (okunmaz) | aynı | güvenli, tek anlamlı |

Akü aralık dışındayken bölücü ölçümüne geçilemiyor: madde 2 "Akü gerilimi … içindeyse:" koşuluyla açılıyor, madde 1 "bölücü ölçümüne
geçme" diyor. İlk kontrolün bulduğu yanlış yol (akü biraz dışarıda, okuma bant içine düşüp aşama 2'ye geçiliyor) artık yok.
"İçindeyse" / "dışındaysa" birbirinin tam tümleyeni, sınır değerde boşluk yok.

**Sıra ve güvenlik:** madde 1 ana anahtar kapalı ve akü ayrıkken akü tarafı XT60'ında elle değdirilen uçla ölçüyor; kısa devre
uyarısı iki parçalı ("bir uç iki kontağa birden", "iki uç birbirine"); "kontağına" kayıtla uyumlu (akü tarafı XT60'ının cinsi kayıtta
yok). Madde 1'de uçlar elde tutuluyor; madde 2 uçları bölücüye ve G05'e bağlatıyor, sonra "ana anahtar kapalıyken tak → aç". Madde 2'ye
geçerken probların nerede olduğu belli (madde 1'de bağlanmadılar). Söküm iki dalda da "kapat → ayır → sök" sırasında. Önceki madde
(mantar ölçümü) "kapat → ayır → sök" ile bitiyor; madde 1'in başlangıç koşuluyla uyumlu.

**"Baştan yinele" döngüsü:** kilitlenme yok. Kusur bulunamazsa döngü "devam etme, kayda yaz" ile kapanıyor; kusur düzeltilince
yeniden ölçüm madde 1'den başlıyor ve ana anahtar ancak madde 2'de, bölücü düzeltildikten sonra açılıyor. Bölücü düzeltilmeden ana
anahtarı açtıran bir yol yok. Yine de düzeltme denemesi başarısızsa her tur bölücüye yeniden enerji veriyor; akımı 100 kΩ sınırlıyor
(ilk kontroldeki ön bilgi), zararsız.

**Maddeler ayrı ayrı:** madde 1 tek başına anlaşılır. Madde 2 madde 1'e "Akü gerilimi … içindeyse" ile, madde 3 madde 2'ye "Bölücü
okuması … aralığının altında ya da üstündeyse" ile bağlanıyor (madde 2'nin terimi); yeterli.

**Sayılar:** oran 18 / (100 + 18) = 0,15254 → "0,1525"; 12,8 × oran = 1,9525 → 1,95; 14,4 × oran = 2,1966 → 2,20 V. Akü aralığı
`planlama/adim3/elektrik.md:67` (12,8–14,4 V), bölücü `:140` ve E2 `:234`; `kablolar.json` G07 kaydı 100 kΩ üst direnç ve 18 kΩ
orta nokta. Bütün sayılar yer tutucudan, çıplak değer denetimi 0.

**Ajanın iki sapması:** (1) "Bölücü okuması …" başlangıcı doğru: madde 2'nin terimiyle aynı ve anahtar ↔ bağlam denetimi cümlede
"bölücü" adını istiyor. (2) "Kusuru düzeltince ölçümü akü gerilimi maddesinden baştan yinele." doğru ve gerekli: o olmadan "bölücü
düzelip okuma aralığa girene kadar ana anahtarı yeniden açma" cümlesi yeniden ölçümün yolunu kapatırdı. İki küçük okunurluk sorunu
aşağıda (A1, A2).

## K2 madde 5 (`rehber_metin.py:827-835`)

Ölçüm: çözülmüş metin harfiyen izlendi. Sıra: dört kablo (U03, H02, S10, G17) kafa ucunda bağlanır → AU3 için, dikişler sıkılmadan
ve enerjisizken (akü XT60 ayrık) + damarı süreklilikle bulunur → kafa ucu PAM8403'e lehimlenir (+ → L+, − → L−) → kutup kontrolü →
"Sonra dikişleri sık". Geri sarma yok, hiçbir iş iki kez yaptırılmıyor, enerjiliyken lehim yok. Dikiş geçişleri: "sıkılmadı",
"sıkmadan" (2), sonda "sık" (1). Dört kablonun kimliği, `kablolar.json`'da boyun demetindeki (K14 a) beş kablodan AU3 çıkınca kalan
dördüyle aynı; eksik / fazla yok. PAM8403 eşlemesi kayıtla aynı (AU3 damarları: + → L+, − → L−).

## Onay kaydı farkı

Turdan önceki kayıt ile bugünkü kayıt girdi girdi (küme farkı) karşılaştırıldı. Kablo 100 → 100 (fark 0). Liste 193 → 198: 7 girdi
çıktı, 12 girdi girdi (F1 `ZORUNLU_ALAN` 5 eski → 8 yeni, K2 `ZORUNLU` 1 yeni, `ZORUNLU_SIRA` K2 iki desen değişti, F1 kapı sırası 1
yeni). Metin 997 → 1000: 10 girdi çıktı, 13 girdi girdi (K2 1 → 2, F1 9 → 11). Ajanın "25 fark" sayısı konumsal eşleştirmeyle; küme
farkıyla 42 girdi, içerik aynı ve hepsi bu turun cümleleri ve kuralları.

- Kritik değer değişimi yok: yer tutucular aynı, kablo bölümü aynı.
- Anlamca silinen uyarı yok. Eski "Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök" madde 2'nin geçer
  dalında; "ESP32'ye bu bölücüyle enerji verme … aşama 2'ye (F5) geçme" cümlesi değişmeden (farkta yok) madde 3'te; kısa devre uyarısı
  genişledi; "aşama 2'ye geçme" madde 1'de de var. Kalkanlar kararla aynı: "belirgin", "yakın", "küçük fark kalibrasyonla düzelir".
- K52 / K60 / K61 metni yok. Önceki turların talimatları (G22, X01, P01–P03, AU3 / H02, K1 G07) farkta yok, bozulmamış.

## Kurallar (`tasarim/freecad/rehber/rehber_denetim.py`)

Değişenler: `ZORUNLU` K2 "dört kabloyu" (`:197`), `ZORUNLU_ALAN` F1 8 madde (`:344-363`), `_DIKIS_SIK` (`:371`), `ZORUNLU_SIRA` F1 kapı
(`:378`), ASCII izinli liste 9 sözcük (`:139`), `ZORUNLU_BOZMA` 16 yeni / 4 uyarlanmış. Temiz kaynakta zorunlu eksik 0, onay farkı 0
(yanlış alarm 0). Kendi bozmalarım (depodaki modül içe aktarıldı, ham metin bellekte bozuldu; ajanınkilerden farklı):

| Bozma | Kural sayımı | Onay kaydı |
|---|---|---|
| K2 dört kablo listesinde G17 yerine AU3 | yakaladı (1) | 1 |
| K2 dört kablodan sonra "Hoparlör kablosunu (AU3) da kafa ucunda bağla." | kaçtı | 1 |
| K2 AU3'ten önce "Arka kabuğun dikiş vidalarını sık." | kaçtı | 1 |
| K2 AU3'ten önce "Dikişleri sıkıştır." | yakaladı (2) | 1 |
| K2 enerjisiz koşulu "akü takılıyken" oldu | yakaladı (1; yasak +1) | 1 |
| F1 kapı "dışındaysa" → "içindeyse" | yakaladı (2) | 1 |
| F1 madde 2 koşulu "ne olursa olsun" | yakaladı (1) | 1 |
| F1 madde 1 ile 2'nin yeri değişti | yakaladı (2) | bakılmadı |
| F1 kapı cümlesi madde 3'ün sonuna taşındı | yakaladı (1) | bakılmadı |
| F1 "bir uç iki kontağa birden değmesin" silindi | yakaladı (1) | 1 |
| F1 madde 3 başında uçlar enerjiliyken sökülür | yakaladı (1) | 1 |
| F1 madde 2 sonunda uçlar enerjiliyken sökülür | kaçtı | 1 |
| F1 "Kusuru düzeltince … baştan yinele." silindi | kaçtı | 1 |
| F1 kapıda "baştan yinele" → "aralığa gelmese de sonraki maddeye geç" | kaçtı | 1 |
| F1 bant gevşedi ("bandın biraz dışındaysa da geçer") | kaçtı | 1 |
| F1 "kusur yoksa … kayda yaz ve aşama 2'ye (F5) geç" | kaçtı | 1 |
| F1 orandan yeni ölçüt ("%10 farklıysa bölücü bozuk") eklendi | kaçtı | 1 |
| F1 "bölücü bozuk olabilir, yine de devam et" | kaçtı | 1 |

Kural sayımı 18'den 9'unu yakaladı; kaçan 9'un hepsi onay kaydıyla yakalandı (fark 1). Kaçanlar desenin önüne / arkasına ek ya da
desensiz cümle silinmesi; sessiz geçen yok. `_DIKIS_SIK` 12 örnekte: "sık", "Dikişleri sık", "dikişlerini sık", "sıkıp", "sıkılır" ve
"sıkma" (olumsuz emir; yanlış alarm yönünde, bugünkü metinde yok) tutuyor; "sıkmadan", "sıkılmadı", "sıkılmadan" tutmuyor (doğru);
"dikiş vidalarını sık", "dikişleri iyice sık" ve büyük harf "DİKİŞLERİ SIK" kaçıyor.

ASCII izinli liste: 9 yeni sözcüğün her biri listeden tek tek çıkarılınca kalıntı 0 → 1, yani dokuzu da gerekli; hepsi doğru Türkçe
yazım ve Türkçe sözlük tablosunda (TR) karşılığı olan yok. Kullanılmayan izinli sözcük ajanın dediği gibi üç değil, **altı**: "pimine",
"belirgin", "kalibrasyonuyla", "gerilimine", "gelene" (bu turda boşa düştü) ve "kayar" (önceden). Hepsi doğru yazım; zararı yalnız
kuramsal (bir doğru sözcüğün aksansız yazılmış başka bir sözcükle aynı olması; altısında böyle bir eş yok).

## Koşular (08:41; çıktı yazmayan kiplerde)

| Koşu | Çıkış | Sonuç |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel |
| `kablolar_denetim.py` | 0 | GEÇER |
| `rehber_denetim.py --kaynak` | 0 | ascii 0, elektrik 0, zorunlu eksik 0, yasak 0 (istisna 10), çıplak 0, bağlam 0, onay farkı 0 (100 / 198 / 1000); tamlık 172, eksik 0, muaf 21; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 231 / 231, bozulmamış kaynakta hata 0 |
| `rehber_kablo.py` | 0 | 51 / 23, geometri hata 0, bilgi 6, ayırt edilemeyen 0, onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 0 | 44 / 44 |
| `py_compile` (çıktı depo dışında): `rehber_denetim`, `rehber_kablo`, `rehber_metin`, `rehber_uret` | 0 | |
| `node --check rehber/app.js` | 0 | |

## Sınırlar, kayıt, gizlilik

- `git diff 4a097fb` boş: `planlama/adim3/kablolar.json`, `pin-haritasi.md`, `elektrik.md`, `planlama/maliyet.json`, `kod/`, izlenen
  bütün eski kontrol raporları. `tasarim/freecad/` altında değişen `.py` dosyaları yalnız paketin dördü (CAD kaynağı değişmedi).
  `F10j-kontrol.md` izlenmiyor; son yazma 08:23, tur 08:24'te başladı (içerik karşılaştırması için kopya yok).
- `git status --short` başta 24, sonda 27 satır: yeni üçü (`rehber/veri/rehber-veri.js`, `rehber-veri.json`,
  `planlama/rehber/goruntu/adim-06.png`) şu anda koşan üretimin çıktıları. `tasarim/freecad/` ve `planlama/adim4/` altında 08:38:56'da
  açılan `__pycache__` klasörleri (cpython-311) üretim koşusunun; bu kontrolün Python'u başka sürüm, bayt kodu yazmadı. Üçü de
  `.gitignore`'da.
- Sayım düzeltmesi iki yerde yapılmış: `karar-kuyrugu.md:1461` ve `F10j-gunluk.md:127-128` ("7"). Başka yerde eski "6" yok.
- Kuyruk özet tablosu satır satır sayıldı: açık 49, kapandı 14, başka durum 0, 63 tekil numara; `:80` ile aynı. Tablo bu turda
  değişmedi.
- Kuyruğa yazılanlar brief'in listesiyle aynı (8 madde) ama ilk kontrolün "kayıtlı açık iş" listesinden üçü eksik (A3).
- Kanca: `pre-push`'un yedi içerik kalıbı (anahtar biçimleri, anahtar / parola ataması, e-posta, IBAN / telefon, yerel kullanıcı yolu ve
  bilgisayar adı öneki, takma ad, ekip soyadları) dosyadan okunup uygulandı. Kapsam: `git diff 4a097fb`'nin eklenen 905 satırı +
  `F10j-gunluk.md` (402) + `F10j-kontrol.md` (202) + bu rapor. Eşleşme 0. Tarayıcı altı kalıpta yapay örnekle sınandı, tuttu.
  Yasak yol / ofis belgesi kuralına giren dosya yok.

## Kayıtlı açık işler

- **A1 · "akü gerilimi maddesi" belirsiz** (`rehber_metin.py:943`). Madde 2 de "Akü gerilimi … içindeyse" ile başlıyor; okuyan madde 2'den
  yineleyip aküyü yeniden ölçmeyebilir (zarar yok, akü birkaç dakika önce aralıktaydı). Önerilen: "Kusuru düzeltince ölçümü baştan,
  akünün kendi gerilimini okuduğun maddeden yinele."
- **A2 · madde 3'te harfiyen çelişki** (`rehber_metin.py:941-943`). "bölücü düzelip okuma aralığa girene kadar ana anahtarı yeniden açma"
  ile yeniden ölçüm (madde 2 ana anahtarı açtırır) harfiyen çatışıyor; sonraki "baştan yinele" cümlesi çözüyor. Önerilen (kural ve
  onay kaydı birlikte): "bölücüdeki kusuru düzeltmeden ana anahtarı yeniden açma, ESP32'ye bu bölücüyle enerji verme, aşama 2'ye (F5)
  geçme."
- **A3 · kuyrukta eksik üç açık iş** (`karar-kuyrugu.md` son madde). İlk kontrolden: AU3 lehim cümlesinin kutbu ("+ → L−" ters) ve F1
  "okunanı not al" silinmesi yalnız onay kaydıyla yakalanıyor; A3 kalıbında "N tel:" biçimli gerçek ok talimatı liste sayılıyor;
  `rehber_kablo.py:762` elle bakılan yan dal kuralında "sağlanmış" sayılıyor. Önerilen satır: "- AU3 kutbu ve F1 'okunanı not al' kural
  kilidi yok (yalnız onay kaydı); A3: 'N tel:' biçimli ok talimatı liste sayılıyor; `rehber_kablo.py` elle bakılan yan dal kuralında
  sağlanmış sayılıyor (`F10j-kontrol.md`)."
- **A4 · kural kilidi olmayan yeni cümleler** (yalnız onay kaydı yakalıyor): "Kusuru düzeltince … yinele", madde 1'deki "aralığına
  gelince … baştan yinele", madde 2'nin geçer dalındaki söküm sırası, bandın / "kusur bulunmazsa" cümlesinin arkasına eklenen gevşetme,
  K2'de dört kablodan sonra AU3'ü yeniden bağlatan cümle ve "dikiş vidalarını sık" biçimi.
- **A5 · ASCII izinli listede kullanılmayan altı sözcük** (`rehber_denetim.py:136-139`): "kayar", "gerilimine", "pimine",
  "kalibrasyonuyla", "belirgin", "gelene". Zararsız; temizlikte çıkarılabilir. Günlükteki "üçü bırakıldı" sayısı eksik.
- Günlükteki onay farkı "25" konumsal eşleştirmeyle sayılmış; küme farkıyla 42 girdi (çıkan 17, giren 25). İçerik aynı.

## Bakılmadı

Basılı sayfa yerleşimi ve gerçek üretim (üretim ajanı koşuyor), tarayıcı görünümü, `kablolar_denetim.py --bozma-denemesi` (bu turda
değişmedi), `F10j-kontrol.md`'nin içerik değişmezliği (kopya yok, yalnız yazma zamanı), akü XT60'ının ve PAM8403'ün gerçek uç
etiketleri (parça yok).
