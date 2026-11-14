**UYUM DÜZELTMESİ GEÇER** (yeniden bakış 14.11 15:40–15:45; S3-1 düzeldi, § 8)

İlk hüküm (13:57): **DÜZELTME GEREKLİ**. S1 ve S2 geçiyordu. S3'te beklenen değer için iddia edilen bağımsız sınama, kablo parçalarında
yoktu: `rehber_kablo.veri_denetle` `rt` alanını yalnız şemalarda denetliyordu (bulgu S3-1, § 4).

# F10h kontrol 5: üretim uyum düzeltmesinin (S1–S3) bağımsız kontrolü

14.11.2026 13:46–13:57 (saat okundu). Dal `lale-duzeltme`, HEAD `8134519`, değişiklikler çalışma ağacında. Depo yalnız okundu; bu
dosya dışında depoya bir şey yazılmadı. Kod koşuları ve bozmalar depo dışındaki geçici bir kopyada yapıldı (`-B`,
`PYTHONDONTWRITEBYTECODE=1`). Yalnız `kablolar_denetim.py` (dosya yazmıyor, `git show` istiyor) depo üstünde koşuldu; önce ve sonra
`git status` aynı. Aynı saatlerde ikinci üretim aşaması sürüyordu (kilit: "P10.7b1 üretim 2. aşama (ajan U) rehber_uret.py, 14.11 13:46
başladı"). FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları ve tarayıcı koşulmadı. Veri modundaki bütün sınamalar 13:47'de alınmış
`rehber/veri/rehber-veri.json` kopyasında yapıldı. Kopyanın dosya zamanı 12:06 (ilk üretim), JSON eksiksiz: 1192 parça, 49 şema, 50 adım.

## 1. Kapsam (düzeltme öncesi kopyalar ↔ bugünkü dosyalar)

| Dosya | Fark | Hüküm |
| --- | --- | --- |
| `tasarim/freecad/rehber/rehber_denetim.py` | `:51` KISALTMA + "VOUT", "SDA"; `:57–58` açıklama; `:66` ASCII_TAMAM yeni satır (13 kelime); `:488–501` yeni `tablo_metinleri(V=None)`; `:1314` veri modu, `:1336` `--kaynak` ASCII girdisine `tablo_metinleri` eklendi | iddiayla aynı, başka satır yok |
| `tasarim/freecad/rehber/rehber_metin.py` | yalnız `:600` `gizli_ok` anahtarı `"Köpük bant (USB ses"` → `"Köpük bant (yedek USB ses"` | iddiayla aynı. Talimat metni, gerekçe metni, desen ve başka alan değişmedi |
| `planlama/d158/F10e-dogrula.py` | `:10` açıklama; `:239–244` `beklenen_renk`; `:255` çağrı; `:261–262` `yontem` metni | iddiayla aynı. Öbür ölçütlere ve eşiklere dokunulmadı |
| `tasarim/freecad/rehber/rehber_kritik_onay.json` | bayt bayt aynı | dokunulmadı |
| `tasarim/freecad/rehber/rehber_sira.py` | **Düzeltme öncesi kopyası yok.** İlk üretimin `git status` kaydında bu dosya değişmiş görünmüyor, yani HEAD hâli düzeltme öncesi hâlidir. HEAD'e göre fark: `:1217–1220` `eslesmeyen_anahtar`, `:1339–1340` özet satırı | iddiayla aynı |
| `planlama/adim3/kablolar.json` | dosya zamanı 10:19, yani düzeltmeden önce | değişmedi |
| `rehber_kablo.py`, `rehber_deger.py`, `rehber_kritik.py`, `rehber_uret.py` | dosya zamanları 11:43–11:49, düzeltmeden önce | değişmedi |

13:33'ten sonra değişen başka dosyalar: `planlama/d158/F10h-gunluk.md` ve `planlama/dongu-158.md` (belge) ile kilit dosyası.
`tasarim/freecad/rehber/__pycache__/*.cpython-311.pyc` dosyaları 13:46 ve 13:48'de oluştu. Bunlar ikinci aşamanın FreeCAD
Python'undan (3.11) geliyor, düzeltmeden değil (günlük 13:43'te "`__pycache__` yok" diyor; gitignore'da).

Kural ve eşik açısından bakınca değişen kural listeleri yalnız ASCII_TAMAM ve KISALTMA. İkisi tasarım gereği onay kaydının dışında
(`rehber_denetim.py:1083–1087` (d) ve (e) listelerinde yoklar), dolayısıyla onay kaydı farkının 0 çıkması beklenen sonuç. Bu
kelimelerin tek güvencesi bu kontrol, aşağıda tek tek bakıldı.

## 2. S1: ASCII sınaması gevşedi mi?

**Karşılaştırma tam kelimeyle yapılıyor.** `ascii_kalinti` (`rehber_denetim.py:464–485`) kelimeleri `[A-Za-zÇĞ…]+` ile ayırıyor. Türkçe
harf taşıyan ya da 3 harften kısa kelimeleri atlıyor. Büyük harfli kelime için `KISALTMA` kümesine bakıyor. Öbürleri için koşul
`k in S or k not in ASCII_TAMAM`; burada `S`, `RM.TR` ve `TR_EK` içindeki bilinen aksansız yazımlar ve bu koşul önce geliyor. Kümede
gövde ya da önek eşleşmesi yok. Bu yüzden "koruma" eklenince "korumasi" geçmiyor, "kapatma" eklenince "kapatmasi", "beyaz" eklenince
"beyazi", "turuncu" eklenince "turuncusu" geçmiyor (bozmalar K4, K5, K8, V5, V6).

**Kelimeler.** turuncu, mor, koruma, enkoderle, okunur, kapatma, birden, besleyen, klemensi, liste, analog, beyaz, gri: hepsinin doğru
yazımında Türkçe harf yok. Hiçbiri başka bir Türkçe kelimenin aksansız yazılmış biçimine denk gelmiyor ve hiçbiri `S` sözlüğünde yok
(13'ü de `False` çıktı). "VOUT" ve "SDA" doğru kısaltmalar ve yalnız büyük harfli hâlde geçiyor; küçük harfli "sda" yine yakalanır.
**Hüküm: gevşetme yok.**

**`tablo_metinleri` kapsamı.** Panelin kablo tablosundan gelen metni `rehber/app.js` ile karşılaştırdım:

- Lejanttaki "Kablo: " + `kablo_sinif[k][1]` (`app.js:1263`). Veri modunda verideki bütün `kablo_sinif` satırları taranıyor, kaynak
  modunda `Tablo.lejant()` (hazır kablo türleri dahil).
- Tıklama kartı ve kablo listesinin `kb` satırları (`app.js:1113–1117`, `:1210–1213`). Veri modunda bütün parçaların ve şemaların
  `kb` alanı taranıyor, kaynak modunda 74 kablonun `bilgi_satiri`'ı. Kaynak modu ekranda gösterilenden fazlasını kapsıyor.

Kapsanmayan, kablo tablosundan gelmeyen panel metinleri (düzeltmeden önce de böyleydi, önemi düşük):

- (a) Kol kablo şemalarının `lejant` alanı (`app.js:1270`, ör. "S2 lopu: …", "Kablo bağı"). Ne veri modu ne kaynak modu tarıyor
  (bozma V4 kaçtı).
- (b) `app.js` sabit metinleri ("Birden çok devre sınıfı taşıyor", SINIF adları, "… ve N kablo daha"). Bunlar yalnız üretimdeki
  tarayıcı denetiminde taranıyor (bozma K9 kaçtı). Günlük § 15.1 bunu açık iş olarak yazmış.

**Bozmalar** (geçici kopya; dosya bozuldu, `--kaynak` koşuldu, dosya geri yüklendi; veri modu bellekte `denetle(V)`):

| # | Bozma | Sonuç |
| --- | --- | --- |
| K1 | `kablolar.json`'da "Yıldız barası" → "Yildiz barasi" (her yerde; `kb` uç adı) | **yakalandı**: `--kaynak` çıkış 1, ASCII 6, "Yildiz @ kablo G05 kb" dahil |
| K2 | `kablolar.json` koruyucu adı "F1 20 A (sigorta kutusu baglantisi)" | **yakalandı** (1, "kablo G08 kb") |
| K3 | lejant adı "Acil stop (yesil)" (`rehber_kablo.lejant`) | **yakalandı** (1, "lejant yesil") |
| K4 | `kb` sabiti "besleyen hattin korumasi" (izinli "koruma"nın aksansız çekimi) | **yakalandı** (2: hattin, korumasi) |
| K5 | lejant "Analog ses (beyazi)" | **yakalandı** (1) |
| K6 | lejant "Anahtarli bara" | **yakalandı** (1) |
| K7 | rehber metni E4.3 `is_` "yan duvarin ic yuzune" | **yakalandı** (2: duvarin, yuzune; "ic" 2 harf, kural gereği atlanıyor) |
| K8 | rehber metnine "listesi kapatmasi" | **yakalandı**: "kapatmasi". "listesi" doğru yazım, listede zaten var |
| K9 | `app.js` "Birden cok devre sinifi tasiyor" | **kaçtı** (`--kaynak` ASCII 0; bilinen açık iş, yalnız tarayıcı denetimi görür) |
| V1 | verideki p1180 `kb` satırına "baglantisi" | **yakalandı** ("parça p1180 kb") |
| V2 | veri `kablo_sinif.yesil` adı "Acil stop (yesil)" | **yakalandı** |
| V3 | şema 0 `kb` satırına "kirmizi" | **yakalandı** |
| V4 | kol şemasının `lejant` alanına "baglantisi" | **kaçtı** (tablo dışı alan, yukarıda (a)) |
| V5 | lejant "turuncusu" (izinli kelimenin çekimi) | **yakalandı** |
| V6 | lejant "morumsu korumasi" | **yakalandı** (2) |

Ayrıca iki ilk denemem, hedef metin seçtiğim yerde bulunmadığı için bozma yapmadı. Hedefi düzeltip yeniden koştum; tabloda düzeltilmiş
K1 ve V1 var.

## 3. S2: köpük bant anahtarı

- Yeni anahtar `"Köpük bant (yedek USB ses"` bütün veride yalnız **p0822** parçasına uyuyor (1 / 1192, adım 31). Eski anahtar hiçbir
  parçaya uymuyor. `istisna()` anahtarı yalnız kendi alt adımının (31.3) tamamen gizli yeni parçalarına uyguluyor
  (`rehber_sira.py:1238–1242`).
- Geçici kopyada adım 31'in perdelenmesini koştum. Veriyi bellekte `alan_isle` ile tazeledim, voksel hesabı gerçekti. Düzeltme öncesi
  `rehber_metin.py` ile 31.3'te gerekçesiz `['p0822']`, gerekçeli p0777, p0779, p0824 çıktı (`gecti` False, adım 31 istisna 14).
  Bugünkü dosyayla gerekçesiz `[]`, gerekçeliye yalnız p0822 eklendi (istisna 15, `gecti` True). Öbür dokuz alt adımın listeleri
  birebir aynı. **Sessizce gerekçelenen başka parça yok.**
- Gerekçe metni değişmedi (`voksel_ok(74)`: voksel kaynaklı yalancı gizlilik, kimlik tamponunda görünür).
  `planlama/d158/F10d-gizli-piksel.json` (11.11) dosyasında 31.3 p0822 için 3507 piksel kayıtlı. O kayıtta parçanın adı çeviriden
  önceki ad ("Köpük bant (USB ses kartı)"), ama günlüğe göre geometri değişmedi. Gerekçe yine geçerli. Not: § 14.4'teki kare bakışı
  bandın normal karede gözle görünmediğini söylüyor. Bu, gerekçenin "kimlik tamponunda görünür" ifadesiyle çelişmiyor (o ölçüm parçayı
  tek başına çiziyor); bilgi olarak bırakıyorum.
- `eslesmeyen_anahtar` yalnız bilgi. `gecti` formülü (`:1227`) ona bakmıyor, `rehber_uret.py` bu alanı okumuyor. Deneme: 31.6'ya
  uymayan bir anahtar eklendi; `eslesmeyen_anahtar` `['31.6 Yok boyle parca']` verdi, `gecti` True ve gerekçesiz sayısı 0 kaldı.
  Sınır: yalnız `sira_grup` içindeki ad desenli anahtarlara bakıyor. Var olmayan bir kimlik anahtarı (ör. `p9999`) ve adım düzeyindeki
  `ucus_ok`, `giris_ok`, `piksel_ok` anahtarları bu satırda görünmüyor (bilgi; günlük kimlik anahtarlarına elle baktığını yazıyor).

**Hüküm: S2 geçer.**

## 4. S3: `beklenen_renk` totoloji mi?

**Bulgu S3-1 (önem: orta; düzeltme gerekli).** `F10e-dogrula.py:239–244` kablo parçası için beklenen rengi verideki
`p["rt"][tema]` alanından okuyor, yoksa `p["renk"]`. Uygulama sahneyi `kabloTon(x) = (x.rt && x.rt[tema()]) || x.renk` ile boyuyor
(`rehber/app.js:293`, `:461`). İkisi aynı veri alanını aynı geri çekilmeyle okuyor. Bu yüzden kablo parçasında ölçüt artık yalnız
"sahne veriyi çiziyor mu" sorusunu yanıtlıyor; "verideki ton doğru mu" sorusunu yanıtlamıyor. Docstring ve günlük § 15.1 bunun için
"`rehber_kablo.py --veri` veriyi tablodan denetler" diyor, ama:

- `rehber_kablo.py:734–749` (`veri_denetle`, parça döngüsü) parçalarda yalnız `renk` alanını tabloyla karşılaştırıyor; `rt`'ye
  bakmıyor. `rt` yalnız **şemalarda** denetleniyor (`:765`).
- Bu 11 + 1 parça (p1180–p1191) tam da CAD kablo **parçaları**.

Geçici kopyada, 13:47 verisi üstünde `veri_denetle` ile denendi:

| Deneme | `veri_denetle` hata | `beklenen_renk` |
| --- | --- | --- |
| bozulmamış veri | 0 | — |
| p1180 `rt.light` = #b35a00 (turuncu tonu) | **0, kaçtı** | #b35a00 (sahne de bunu çizer, F10e geçer) |
| p1180 `rt` silindi | **0, kaçtı** | #d63031 (taban rengi; sahne de bunu çizer, F10e geçer) |
| şema 0 `rt.light` bozuldu | 1, yakalandı | — |
| `TEMA_TON` kaynakta değişti, veri eski: yeşil, turuncu, siyah, mor | **0, kaçtı** (bu dört sınıfta çizilmiş şema yok, yalnız CAD parçası var) | — |
| aynısı, kırmızı | 1 (yalnız şema 4 aracılığıyla) | — |

Bugünkü veride sorun yok: 12 kablo parçasının 12'sinde `rt` var ve `Tablo().ton(kablo[0])` ile birebir aynı. Açık temadaki beklenen
değerler § 14.3'te sahnede ölçülen 11 tona eşit. Ama düzeltmeyle birlikte kablo parçalarının tonu için bağımsız bir karşılaştırma
kalmadı. Düzeltmeden önce F10e bu parçaları (yanlış da olsa) bağımsız bir değerle, `renk` ile karşılaştırıyordu. Kaynakta
`TEMA_TON`'un değişmesi onay kaydında yakalanıyor. Kaynağı değişmiş ama yeniden üretilmemiş ya da elle bozulmuş bir veri hiçbir veri
sınamasında yakalanmıyor.

**Önerilen dar düzeltme** (FreeCAD'siz; zincirin 2. adımı zaten `--veri` ile koşuyor):

- `veri_denetle`'nin parça döngüsüne `if p.get("rt") != TB.ton(ids[0]): hata.append(...)` satırı. Bu satır eksik `rt`'yi de yakalar.
- `bozma_denemesi`'ne iki veri bozması: parça `rt` yanlış, parça `rt` yok.

Ya da `beklenen_renk` beklenen değeri `rehber_kablo.Tablo().ton(p["kablo"][0])[tema]` ile tablodan alır. Ondan sonra günlük ve
docstring cümlesi doğru olur.

Öbür sorular:

- **Öbür tema:** `renk_sahne` yalnız açık temayı ölçüyor (`:250`, düzeltmeden önce de böyleydi). `beklenen_renk` temayı parametre
  olarak aldığı için koyu temada da doğru değeri verir: p1181 için #b3b3b3, p1180 için #ef5a4c (denendi). Koyu temanın ölçülmemesi
  kapsamın daraldığı anlamına gelmiyor.
- **`rt` alanı olmayan kablo parçası:** sessizce `renk` değerine düşüyor ve geçiyor (yukarıda). Bulgu S3-1'in parçası.
- **Kapsam:** döngü, `gor`, `esit` ve `gecti` (`len(gor) == len(P) and not yanlis`) değişmedi; önce de şimdi de 1192 parçanın her
  biri en az bir konumda sayılıyor. Yalnız 12 kablo parçasının beklenen değeri değişti; kablo dışı parçalar yine `gr` ile
  karşılaştırılıyor. **Kapsam daralmadı.**
- **Çıkış kodu:** `:645–651` ana ölçütler `renk_cad`, `renk_sahne`, `karsitlik`, `ev`, `ev_dogruluk`, `isaret`, `gorunurluk`,
  `arayuz` ve konsol hatası. `renk_demo` çıkış koduna girmiyor (§ 15.1'deki iddiayla aynı).

## 5. FreeCAD'siz yeniden koşu

| Komut (nerede) | Çıkış | Sonuç | § 15.1 ile |
| --- | --- | --- | --- |
| `kablolar_uret.py --kontrol` (kopya) | 0 | "kablolar.md ve elektrik.md bloğu güncel" | tutuyor |
| `kablolar_denetim.py` / `--bozma-denemesi` (depo; yazmıyor, `git status` aynı) | 0 / 0 | GEÇER / toplam bozma 145, GEÇER (29 s) | tutuyor |
| `rehber_kablo.py` / `--bozma-denemesi` (kopya) | 0 / 0 | GEÇER, onay kaydı tutuyor / 27 / 27 | tutuyor |
| `rehber_denetim.py --kaynak` (kopya) | 0 | metin 531 (+ CAD 893, arayüz 552), ASCII 0, elektrik 0, zorunlu 0, yasak 0 (istisna 5), çıplak 0, çözülemeyen 0, bozuk 0, anahtar-bağlam 0, onay farkı 0 (kablo 90, liste 133, metin 907), tamlık 65 / eksik 0 / muaf 21, kablo kimliği 68 / 74 | tutuyor |
| `rehber_denetim.py --bozma-denemesi` (kopya) | 0 | 76 / 76 | tutuyor |
| `rehber_denetim.py` (veri modu; 13:47 veri kopyası) | 0 | ASCII 0, elektrik 0, yasak 0, zorunlu 0 / 71, parça 1192, şema 49 | tutuyor |
| `py_compile` (çıktı depo dışına) | — | `rehber_denetim.py`, `rehber_metin.py`, `rehber_sira.py`, `rehber_uret.py`, `F10e-dogrula.py` temiz | tutuyor |

`kablolar_denetim.py` kopyada koşmadı: `git show origin/main:…` istiyor. Bu yüzden depo üstünde koşuldu.

## 6. Yapılması gereken

1. **S3-1:** `rehber_kablo.veri_denetle` parçalarda `rt` alanını tablodan denetlesin (eksik `rt` dahil) ve iki veri bozması eklensin.
   Ya da `beklenen_renk` beklenen değeri tablodan alsın. Sonra `rehber_kablo.py --veri` ve `--bozma-denemesi --veri` yeniden koşulsun
   (FreeCAD gerekmez, ikinci aşamanın verisi yeniden üretilmez). F10e docstring'indeki ve günlük § 15.1'deki "`--veri` tablodan
   denetler" cümlesi bundan sonra doğru olur.
2. (Bilgi, bu düzeltmenin kapsamı dışında) Kol şemalarının `lejant` alanı ve `app.js` sabit metinleri ASCII sınamasına girmiyor
   (bozma V4, K9).

## 7. Doğrulayamadıklarım

- Sahnedeki gerçek renkler (tarayıcı koşmadı): `renk_sahne`'nin 11 → 0 iddiası yalnız verideki değerlerle ve § 14.3'te ölçülen
  sahne tonlarıyla karşılaştırılarak değerlendirildi.
- İkinci üretim aşamasının sonucu (sürüyor) ve onun yazacağı veri; bütün veri modu sınamaları 13:47'deki (12:06 üretimi) kopyada.
- Kontrollerin geçici kopyada kalıcı olmayan eski bozmaları (§ 9 madde 6) ve `rehber_kol_kablo.py --yazma`: koşulmadı.
- `F10d-gizli-piksel.json`'daki p0822 piksel ölçümünün bugünkü geometride yinelenmesi (tarayıcı gerekir).

## 8. Yeniden bakış (14.11 15:40–15:45, saat okundu): S3-1 düzeltmesi

Kilit "boş", depo üstünde yazan iş yok. Depo yalnız okundu. Sınamalar depo dışındaki geçici kopyada yapıldı; bu kopya bugünkü kaynak
dosyalarla ve 13:49'da yeniden üretilen `rehber/veri/rehber-veri.json` ile tazelendi. Kaynak dosyaları depodakilerle bayt bayt aynı
(`cmp`).

**(1) Kapsam.** Düzeltme öncesi `rehber_kablo.py` kopyasıyla bugünkü dosyanın farkı yalnız iki parça:

- `:750–751`: parça döngüsünde `if p.get("rt") != TB.ton(ids[0])` satırı ve hata mesajı.
- `:863–874`: v6, v7, v8 veri bozmaları ve bunların `deneme` listesine eklenmesi.

Başka bir satır değişmemiş. 13:47'den sonra değişen başka kaynak dosya yok (yalnız üretim çıktıları, doğrulama JSON'ları, günlük ve
döngü belgesi). Not: `rehber_kablo.py`'nin zamanı 15:39, yani zincirden (14:54–15:38) sonra. Zincirdeki `--veri` adımı bu yüzden eski
kodla koştu. Yeni satırın yeni veride geçtiğini 15:39'daki yeniden koşular ve aşağıdaki kendi koşularım gösteriyor.

**(2) Denemelerim, yeni veride** (`veri_denetle`, bellekte; `TEMA_TON` her denemeden sonra geri yüklendi):

| Deneme | Hata |
| --- | --- |
| bozulmamış (12 kablo parçası, 12'si de `rt`'li, 12 / 12 `rt == Tablo().ton`) | 0 |
| p1180 `rt.light` = #b35a00 | **1, yakalandı** |
| p1180 `rt` silindi | **1, yakalandı** ("tema tonu None") |
| `TEMA_TON` yeşil light / turuncu dark / siyah `cekirdek_dark` / mor light değişti, veri eski | **1 / 2 / 1 / 2, yakalandı** (ilk bakışta dördü de 0'dı) |
| p1190 `rt.dark` yanlış (koyu ton) | **1, yakalandı** |
| p1184 `rt` yalnız light (tek tema) | **1, yakalandı** |
| p1181 `cekirdek_dark` silindi | **1, yakalandı** |

**(3) Yanlış alarm.**

- Kablo olmayan parça: döngü `renk` alanı olmayan parçayı atlıyor. Böyle bir parçaya `rt` eklemek hata vermiyor; zaten etkisi yok,
  çünkü `app.js` `kabloTon`'u yalnız `p.renk` varsa kullanıyor.
- Karışık sınıflı parçalar: gerçek veride p1182 (kırmızı + turuncu), p1184 ve p1186 (sarı + turuncu) var, üçü de hatasız. Ton ilk
  kimlikten alınıyor, yani üretimin ve `app.js`'in kuralıyla aynı.
- `kablo` listesi boş: satıra gelinmeden "eşlemesiz" sayılıyor (hata 0, eşlemesiz 1). Çökme ya da çift sayım yok.
- Tek katılık: aynı tonun büyük harfle yazılması (#C0392B) hata veriyor, çünkü `renk` karşılaştırması küçük harfe çeviriyor, `rt`
  karşılaştırması çevirmiyor. Üretim tonu `TB.ton`'dan kopyaladığı için bu kendiliğinden olmaz. Bilgi; önem yok.

**(4) FreeCAD'siz koşular** (geçici kopya, yeni veri; `-B`, `PYTHONDONTWRITEBYTECODE=1`):

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, onay tutuyor / 27 / 27 |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | GEÇER, "veri: eşlemesiz çizim 0", geometri hata 0 / bilgi 4 |
| `rehber_kablo.py --bozma-denemesi --veri …` | 0 | **35 / 35** (v6 "tema tonu yanlış", v7 "tema tonu yok", v8 "kaynak tonu değişti, veri eski": denetim + onay) |
| `rehber_denetim.py` (veri) | 0 | ASCII 0, elektrik 0, yasak 0, zorunlu 0 / 71, parça 1192, şema 49 |
| `rehber_denetim.py --kaynak` / `--bozma-denemesi` | 0 / 0 | onay farkı 0 (90 / 133 / 907), öbür sayılar 0 / 76 / 76 |
| `py_compile` (çıktı depo dışına) | — | `rehber_kablo.py`, `rehber_denetim.py`, `rehber_metin.py`, `rehber_sira.py`, `rehber_uret.py`, `F10e-dogrula.py` temiz |

**(5) Kütükler.**

- `rehber_uret.py` (ikinci aşama, 13:46'da başladı): `.durum` "BITTI cikis 0 sure 2342". On sınama satırı geçti. Tarayıcı 50 / 50,
  "ek kontrol sorunlu: -", kablo eşleme GEÇTİ, denetim ASCII 0. Perdelenme: alt adımlarda gerekçesiz 0, istisna 117 (F10g ile aynı),
  "parca adina uymayan 0 (bilgi)".
- Zincir (14:54–15:39): `.durum` "BITTI cikis 0". Bütün adımlar çıkış 0. F10e "GECTI; renk_demo KALDI (karar)", çıkış 0.
- `planlama/d158/F10e-dogrula.json`: `renk_sahne` parça 1192, yeni görülen 1192, eşit 1192, **yanlış 0**, `gecti` true. Öbür ana
  ölçütler true, `renk_demo` false (karar, çıkış koduna girmiyor).

İddiayla tutuyor.

**Hüküm:** S3-1 kapandı. `rt` artık parçalarda da tablodan denetleniyor, ilk bakışta kaçan denemelerin hepsi yakalanıyor, yanlış alarm
yok. S1 ve S2'nin hükmü değişmedi. § 6 madde 2 (kol şeması `lejant` alanı ve `app.js` sabit metinleri ASCII sınamasının dışında) bilgi
olarak kalıyor.

Doğrulanamayanlar: sahnedeki renkler kendi ölçümümle görülmedi (yalnız F10e kütüğü ve JSON'u okundu); zincirin `--veri` adımının
yeni kodla koşmuş hâli (zincir eski kodla koştu, yeni kod 15:39'daki yeniden koşuda ve bu bakışta sınandı).
