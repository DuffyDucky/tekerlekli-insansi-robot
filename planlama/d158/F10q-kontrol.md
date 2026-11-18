# F10q kontrol: P10.7b2h (17.11 kararlarının rehber metni)

Bağımsız kontrol, 18.11.2026. Taban `376fe90`, çalışma ağacı (commit yok). Kaynak dosyalara dokunulmadı.

## Hüküm: DÜZELTMEYLE GEÇER

## Bulgular

1. **`tasarim/freecad/rehber/rehber_metin.py:1471-1472` (G3 madde 1): sıra hatası. Önem: düzeltilmeli (montajda yapılamayan adım).**
   Sentil sınaması ("S2'ye 5 komutunu ver: dişle kol arasında 0,3 mm sentil...") madde 1'de, ama kol çatalı horna madde 2'de takılıyor
   (`Kol çatalı → horn (4 × M3×8)`). Kol yokken dişle kol arasına sentil sokulamaz. Karar metni (`karar-kuyrugu.md:773, :778`) sırayı söylemiyor;
   sorun rehberin yerleşiminden geliyor. Öneri: madde 1'de yalnız "hornu S2 = 4,3° konumunda tak (kol takılınca dişe dayanacak)" kalsın;
   "5 komutu + sentil + zımpara" kısmı kol çatalı ve mafsal cıvatası takıldıktan sonraki maddeye taşınsın. Alt adım 1 parantezi
   ("sentil sınaması ana adımda") ve kontrol satırı değişmez. ZORUNLU G3 deseni `.*` ile iki parçayı bağladığından taşıma sonrası da tutar.
   Ek not (çıkarım): servoya komut vermek için o aşamada S2'nin besli ve sürülebilir olması gerekir; rehberin bu aşamada güç / sürücü
   bağlı olup olmadığına bakmadım, doğrulanamadı.
2. **`rehber_metin.py:1147, :1161` (F1 etek ön sağ / sol, K55 a): fiziksel kuşku. Önem: not.**
   Ölçüm kaydı (`karar-kuyrugu.md:1161, :1177`) etek ön bandını tutan şeyin bindirme dili değil braket z+105'teki **perçin somunu**
   olduğunu söylüyor (0,5 mm'de 0,8 mm ortak hacim). "Dilini orta bandın arkasına esneterek sok" tarifi bu iki bant için engeli
   tarif etmiyor; esnetmenin rijit somunu aşacağı belli değil. Karar dört bant için a'yı geçici kabul ettiğinden ve rehber "geçici;
   baskı kuponunda denenir" diyerek bunu kesinmiş gibi yazmadığından engelleyici değil. Öneri: etek ön iki cümleye "engel braket perçin
   somunu; kuponda somun tarafı denenir" eki ya da kupon listesine etek ön için ayrı not.
3. **Kablo tablosu / uç etiketleri hâlâ XT60E-M (madde 4). Önem: düzeltilmeli (üretimden önce).** Bkz. aşağıdaki öneri.
4. **`rehber_metin.py:1063` (F1 madde 5): karardan fazla açıklama. Önem: not.** "akü tarafı gömük soket, şarj kablosunun ucu erkek XT60"
   karar satırında (`karar-kuyrugu.md:65`) yok; teknik olarak XT60E-F dişi panel için doğru (çıkarım), ama kaynağı belirtilmemiş. Ayrıca K50
   hâlâ **açık** (alım yarısı Ahmet'te); "alımı açık" ibaresi yalnız F5 notunda var, K1 / F1 cümleleri XT60E-F'yi kesin yazıyor. Kabul
   edilebilir (teknik yarı kapalı), ama F1 madde 5'e de "(alım açık, F5 notu)" eklemek tutarlılığı artırır.

Diğer cümleler kararla uyuşuyor (gördüm):
- K40: "horn kol dişe dayalıyken (S2 = 4,3°)", "0,3 geçmeli / 0,4 geçmemeli", "geçmiyorsa diş yüzü zımparala" `karar-kuyrugu.md:773-778` ile birebir.
- K51: `planlama/maliyet.json:103` P6KE6V8A `"adet": 2` (gördüm). "sonraki CAD paketinde eklenecek" karar "tam taramalı CAD paketinde" ile uyumlu.
- K55: dört bant + çerçeve (K55 başlığındaki dört parça: etek ön, göğüs, omuz, çerçeve) hepsinde "geçici; baskı kuponunda denenir" var.
- K60: "elde taşınan acil stop yok, köprü kalıcı, ileride sökmeden eklenebilir, demoda mantarın yanında bir kişi" karar ve
  `kablolama-on-kararlar.md` §8 yeni metniyle aynı.

## Denetleyici gevşetildi mi (madde 3): hayır, tek tek

- Kapanan-karar deseni (`rehber_denetim.py:1087`): K40/K51/K55/K60 eklendi, `(?! a)(?! A\b)` K60 A'yı geçirir. Bu kural **sıkılaştırma**:
  artık bu dört kod "a/A" olmadan yazılırsa yakalanır. K50 listede değil (doğru, hâlâ açık).
- K61 kuralı daraltması (`:1075`): K60 artık "karar bekliyor" demek zorunda değil, çünkü kapandı. Ters yön yeni bozma denemesi M21e ile
  sınanıyor: koştum, `M21e K60 yeniden 'karar bekliyor' (kapandı) YAKALANDI (1)`. K61 kuralı aynen duruyor. Gevşetme yok.
- ZORUNLU: K1 deseninden yalnız "karar verilene kadar" çıktı (karar kapandığı için doğru); köprü / kesit / "köprü yoksa röle çekmez" kısmı korunuyor.
  "Ö4 karar bekliyor" deseni yerine K60 A + demo şartı zorunlu. F5 "pimleri"→"soketleri" eşdeğer. Yeni G3, E3a, F1 desenleri ek güvence.
- ASCII izin listesi 12 kelime (ileride, eklenebilir, demoda, eklenecek, soket, soketleri, dilini, kuponunda, sentil, komutunda, soketlere,
  sokma): hepsi Türkçe karakter içermeyen doğru yazım. Uygun.
- F10l beklenen listeleri uygulanan metinden üretilmiş (kendi kendini doğrulama riski). Bağımsız karşılaştırma: `git diff` farkını
  kendim okudum; 12 silinen / 22 eklenen cümlenin her biri yukarıdaki beş karardan birine ait, karar dışı değişiklik görmedim
  (6 K55 cümlesi tekrarlı metin, 6 adımda bir kez). Bu, cümle ayrıştırıcısıyla değil diff okumasıyla yapıldı.

## Madde 4 önerisi: bu pakette çevirme; ayrı küçük paket (P10.7b2i), bir sonraki tam üretimden önce

Rehberin kablo tablosu ve uç etiketleri `kablolar.json` G06'dan geldiği için okuyan aynı kitapta metinde "XT60E-F (dişi)", tabloda
"XT60E-M şarj girişi" görecek: gerçek çelişki. Ama çevirmenin dokunduğu yerler bu paketten geniş (gördüm, grep):
- `planlama/adim3/kablolar.json:919, 928, 935, 946, 965, 1013, 8925, 10051` (ad, parça, uç adları, sonlandırma, not, uç sözlüğü anahtarı);
- `tasarim/freecad/rehber/rehber_kablo.py:152, 185, 271` (eşleme anahtarları);
- `planlama/adim3/kablolar_denetim.py:211` (`hat-sarj` regex `^XT60E-M`; çevrilmezse kırmızı olur) ve `:2765` (bozma örneği, eski ad);
- `rehber_kablo.py` "onay kaydı (kablo bölümü)": uç adı değişince parmak izi değişir, onay yenilenmesi gerekir (çıkarım);
- türev `kablolar.md` ve rehber kablo kartları yeniden üretilmeli; `--veri-yok` üretim kablolar.json'u veri kaynağı olarak okuduğundan
  yeter mi doğrulanamadı.
`maliyet.json:111` alım kararını beklediği için değişmez; bu yüzden çeviri sonrası maliyet ile kablolar.json arasında bilinçli bir
fark kalır, rehber F5'teki "alımı açık" cümlesi bunu karşılıyor. Kısa yol (bu pakette olmazsa): bir sonraki rehber üretiminden önce
P10.7b2i olarak yapılsın; yapılmadan tam üretim alınırsa çelişki basılı kitaba geçer.

## Başka kırılabilecek doğrulayıcı (madde 6, öngörü)

- `tasarim/cad/demo_uret.py` KARARLAR (satır 146-151): K40/K50/K51/K55/K60 yok, etkilenmez (gördüm).
- `planlama/d158/F9b-dogrula.py`: bu kodları içermiyor (grep 0).
- `planlama/d158/F9c-uret.py:334, :369`: K50 ve K60 için sabit metin var; K60 "Kalan"dan P10.9b'de zaten çıkarılmış (`:440`). K50 hâlâ
  açık, sorun beklemem; K60 satırının (`:369`) "B seçilirse..." metni eski kalmış olabilir, F9c çıktısında görünür mü bakmadım.
- `kablolar_denetim.py`: bu pakette G06 değişmediği için GEÇER (koştum). Madde 4 yapılırsa `:211` kırılır.

## Koştuğum sınamalar (PYTHONIOENCODING=utf-8; ilk koşu cp1254 konsolda UnicodeEncodeError verdi, betik hatası değil)

- `rehber_denetim.py --kaynak`: çıkış 1, 28 KRITIK satırı. Hepsi K1 alt 2 / alt 8, E3a, F1 (ana, alt 3, 5, 10), F3 alt 1/2/5, F4 alt 1/2,
  F5 not_, G3 (ana, alt 1, kontrol) ve ZORUNLU listesi: beş kararın dokunduğu yerler; başka bölüm yok. Onay yenilenmesi beklenen çıkış.
- `rehber_denetim.py --bozma-denemesi`: çıkış 0, KACTI 0, "303 / 303 yakalandi; bozulmamis kaynakta hata 0", M21e yakalandı.
- `F10l-birlesim.py`: çıkış 0, "eklenen 22 (beklenen 22), silinen 12 (beklenen 12)", "birlesim sinamasi: GECER".
- `planlama/adim3/kablolar_denetim.py`: çıkış 0, "SONUÇ: GEÇER".
- `rehber_kablo.py`: çıkış 0, "onay kaydı (kablo bölümü): tutuyor", "SONUÇ GEÇER".
- `git diff --check` (paket dosyaları): temiz (yalnız CRLF uyarısı).

Bakamadıklarım: `rehber_uret.py` ve tam zincir (yasak); render edilmiş sayfa; `kablolama-on-kararlar.md` §14 (diff yalnız §8 ve tabloyu
değiştirdi, §14'e bakmadım); `F10q-gunluk.md` iddiaları tek tek; S2'nin G3 aşamasında sürülebilir olup olmadığı.

## Tur 1 kontrolü (18.11.2026)

Tur 0 farkı (`b2h-tur0.diff`) ile şimdiki `git diff` satır satır karşılaştırıldı; yalnız yeni satırlar okundu.

### Hüküm: DÜZELTMEYLE GEÇER (tek düzeltilmesi gereken: F5 sentil güvenlik cümlesi)

### Bulgular

T1. **`rehber_metin.py:1767-1769` (F5 aşama 2, S2 sentil sınaması). Önem: düzeltilmeli (insan güvenliği; üretimden önce).**
  (a) Enerjisiz ölçüm kararın tarifini karşılamaz (çıkarım, karar metninden): K40 a "S2 **5 komutunda** dişle 0,3 mm sentil geçer"
  diyor (`karar-kuyrugu.md:773, :778`); ölçülen şey servonun 5°'te **tuttuğu** konum. Aynı adım "servo gücü kesilince kollar düşer"
  diyor (`:1756`), yani enerji kesilince kol 5°'te kalmaz. Servo tutarken ölçmek zorunlu.
  (b) Cümle yeterince sınırlı değil. Yazan: "kol dururken yalnız sentili tutan kişi kola yaklaşır, öbürü mantarda". Eksikler: kişi
  yakındayken hiçbir komut gönderilmeyeceği; mantardaki kişinin yalnız mantara bakıp kumandaya / telefona / klavyeye dokunmayacağı;
  komutu veren kişinin kim olduğu (iki kişiyle komutu veren ya mantarda ya kolda olur); el çekilmeden yeni komut verilmeyeceği;
  parmak / elin dişle kol arasına (sıkışma hattı; 4,3°'e dönüşte servo 98 N stall, `karar-kuyrugu.md:767`) girmeyeceği, sentilin
  ucundan tutulacağı; ikinci kola geçmeden önce elin çekilmesi.
  (c) Çelişki kalıyor: `:1756-1757` "Kolların erişim alanında ve düşme hattında ... kimse yok, bir kişi yalnız mantarda (kural 1 ve 7)"
  istisnasız yazıyor; yeni cümle buna istisna olduğunu söylemiyor. Kural 1 / 7'nin metnine bakmadım (doğrulanamadı).
  Önerilen cümle (yerine):
  "S2 sentil sınaması (K40 a; horn G3'te dişe göre takıldı). Bu sınama aşamadaki 'kolların erişim alanında kimse yok' kuralının tek
  istisnasıdır ve yalnız şöyle yapılır: komutu mantardaki kişi verir; S2'ye 5 komutunu ver, kol durduktan sonra 3 saniye bekle;
  mantardaki kişi bundan sonra kumandaya, telefona ve klavyeye dokunmaz, eli mantarın üstünde kalır. Öbür kişi yalnız sentilin ucundan
  tutarak dişle kol arasına 0,3 mm sentili sokar, parmağını dişle kol arasına sokmaz: 0,3 mm geçmeli, 0,4 mm geçmemeli. Kişi elini
  çekip kolun erişim alanından çıkmadan yeni komut verilmez; ikinci kol için aynı sıra. Kol beklenmedik biçimde kıpırdarsa mantara bas.
  0,3 geçmiyorsa ana anahtarı kapat, aküyü ayır, sonra diş yüzünü zımparala ve sınamayı yinele."
  ZORUNLU F5 deseni (`S2 sentil sınaması \(K40 a.*0,3 mm sentil geçmeli, 0,4 mm geçmemeli`) bu metinle de tutar; istisna ve "komut
  verilmez" ibarelerinin de zorunlu desene eklenmesi önerilir (silinirse yakalansın).

T2. **Kabuk takılıyken sentil aralığa ulaşır mı: doğrulanamadı. Önem: düzeltilmeli (çekince cümlesi).** F5'ten önce F3 / F4'te göğüs
  ve omuz bantları takılıyor (rehber sırası); S2 dişinin kabuk altında açık kalıp kalmadığını CAD'den bu sürede ölçmedim. Öneri, F5
  cümlesine ek: "Bantlar takılıyken sentil dişle kol arasına düz giremiyorsa sınamayı zorlama; ölçülemedi diye kaydet ve omuz bandını
  sökmeden önce proje sahibine sor (aralığın kabuk altında erişilebilirliği CAD'de doğrulanmadı)." Ayrıca bir sonraki CAD paketine
  ölçüm işi.

T3. **XT60 çevirisi: tam (gördüm). Önem: yok.** `tasarim/` ve `planlama/adim3/` içinde `XT60E-M` yalnız iki yerde: F5 notundaki
  "siparişte XT60E-M varsa XT60E-F ile değiştirilir" cümlesi (`rehber_metin.py:1809`, alım; doğru) ve onun onay kaydı
  (`rehber_kritik_onay.json:9103`). `maliyet.json:111` bilerek değişmedi. `kablolar_denetim.py:211` regex `^XT60E-M` → `^XT60E-F`:
  tam değiştirme, `[MF]` gibi gevşeme yok. `:2765` bozma örneği de çevrilmiş. `planlama/d158` altındaki tarihsel geçişlere bakmadım.

T4. **Onay yenilemeleri: meşru görünüyor. Önem: not.** `rehber_kritik_onay.json` farkındaki eklenen girdilerin `yer` alanları yalnız
  F1 alt 3/5, F3 alt 1/2/5, F4 alt 1/2, F5 is_ / kontrol / not_, G3 is_ ve LISTE ZORUNLU: hepsi bu paketin dokunduğu yerler. Değişen
  (eski→yeni) girdileri tek tek okumadım. Kablo onay kaydı: `rehber_kablo.py` "tutuyor" diyor; farkını açmadım.

T5. **Denetim desenleri: gevşetme yok.** Tur 0'daki G3 deseni kaldırılıp iki G3 + bir F5 deseniyle değiştirildi (horn konumu, "burada
  yapılmaz" yönlendirmesi, F5 sınaması); kapsam arttı. `ASCII_TAMAM`'a 7 kelime (engel, dil, braketinin, kuponda, dururken, sentili,
  tutan): hepsi Türkçe harfsiz doğru yazım.

T6. **Etek ön perçin somunu notu ve F1 "alımı açık": tamam (gördüm),** tur 0 bulgu 2 ve 4'ü karşılıyor. G3 alt adım 1 ve ana adımın
  "sentil F5 aşama 2'de" yönlendirmesi tutarlı; kontrol satırına "iki kolda da" eklenmiş (F5'te "her kolda" ile tutarlı).

### Madde 6: `--veri-yok` yeter mi

Kodu okudum: `rehber_uret.py:806-812`: `--veri-yok` yalnız FreeCAD `veri()` adımını atlar; `--cikti` verilmediği sürece
`rehber_gorunum.isle()` çağrılır ve `isle(yazma=False)` varsayılanında `yaz(V)` ile `rehber-veri.json` yazılır (`rehber_gorunum.py:668-669`;
parametre adı ters: `yazma=False` = yazar). Bugünkü `rehber/veri/rehber-veri.json`'da `XT60E-M` 4 satırda, hepsi metin alanı (K1 alt
adım, F1 madde 5, F1 alt adım, F5 not_), kablo / uç alanı yok (gördüm). Yani ajanın dayanağı kodla tutuyor: **`--veri-yok` (ama
`--cikti` olmadan) yeterli görünüyor** (çıkarım; koşmadım). Dikkat: `--cikti` ile koşulursa `isle()` atlanır ve depo verisi değişmez.
Yeterlilik kanıtı, üretimden sonra: `rehber/veri/rehber-veri.json` ve `rehber/veri/rehber-veri.js` içinde `XT60E-M` yalnız
"siparişte XT60E-M varsa" cümlesinde (1'er geçiş) kalmalı; `XT60E-F` K1 / F1 / F5 metinlerinde ve G06 uç adlarında görünmeli; kablolar.md
ve rehber kablo kartında (`rehber_kablo.py` çıktısı) `XT60E-M` 0 olmalı.

### Koştuklarım (tur 1, PYTHONIOENCODING=utf-8)

- `rehber_denetim.py --kaynak`: çıkış 0, KRITIK 0.
- `rehber_denetim.py --bozma-denemesi`: çıkış 0, KACTI 0, "303 / 303 yakalandi; bozulmamis kaynakta hata 0".
- `F10l-birlesim.py`: çıkış 0, "eklenen 26 (beklenen 26), silinen 12 (beklenen 12)", GECER.
- `kablolar_denetim.py`: "SONUÇ: GEÇER". `rehber_kablo.py`: "SONUÇ GEÇER".
- `git diff --check`: temiz.

Bakamadıklarım: S2 dişinin kabuk altında erişilebilirliği (CAD); kural 1 / 7 metni; `kablolar.json` / `kablolar.md` / `elektrik.md` /
`F9c-uret.py` / `dongu-158.md` farkları tek tek (yalnız grep); onay dosyasındaki değişen girdilerin içeriği; çalışma ağacındaki
`tasarim/freecad/kabuk/gorsel/*.png` ve `montaj/yerlesim-kontrol.json` değişikliklerinin bu turdan olup olmadığı.
