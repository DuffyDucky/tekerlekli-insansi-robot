**DÜZELTME GEREKLİ**

# F10j kontrol · P10.7b2b bağımsız kontrol (kaynak düzeyi, salt okuma)

15.11.2026; ilk ölçülen koşu 08:08, rapor 08:21 (saat okundu; başlangıç saati okunmadı). Dal `lale-duzeltme`, HEAD = uzak = `4a097fb`.
Depoda yazılan tek dosya bu rapor. FreeCAD, `rehber_uret.py` tam koşusu ve F10* doğrulayıcıları koşmadı; bozmalar, kopyalar ve başsız
tarayıcı depo dışındaki geçici klasörde (tarayıcı kapandı, açık süreç 0). Commit / push / `git add` yok. `git status --short` başta ve
sonda 23 satır (paket dışı 14 + paketin 8 değişen dosyası + `F10j-gunluk.md`; bu rapor ile 24); depoda `__pycache__` yok.

Hüküm gerekçesi: F1'deki G07 karar ağacı (düzeltme 1) bir durumda yanlış sonuca gidiyor ve harfiyen okunduğunda kapsamı belirsiz;
K2 madde 5'in ilk cümlesi AU3 için sırayı geri sarıyor (düzeltme 2); kuyrukta küçük bir yanlış sayı (düzeltme 3). Kod, yerleşim,
onay kaydı, eşikler ve gizlilik geçiyor.

## Düzeltme gerekli

### D1 · F1 G07 ölçümünün karar ağacı (`tasarim/freecad/rehber/rehber_metin.py:917-939`; kurallar `rehber_denetim.py:339-350`)

Ölçüm: metin `rehber_metin` içe aktarılarak çözüldü (`COZUM_HATA` boş, çözülmemiş `{…}` / `⟦?⟧` 0); dört durum tek tek izlendi.

- **Kapsam belirsiz:** "Okuma … aralığının altında ya da üstündeyse: … değerlendir." cümlesi noktayla bitiyor; ardından gelen "Akü
  gerilimi 12,8–14,4 V içindeyse ya da … belirgin farklıysa bölücü bozuk" ayrı, koşulsuz bir cümle. Harfiyen okuyan, akü aralıkta ve
  okuma aralıktayken (doğru kurulum) de "bölücü bozuk" sonucunu okur.
- **Çelişen teşhis:** daha önceki "aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış" cümlesi (`:928`) koşulsuz duruyor.
  Akü 14,4 V'un üstündeyken (şarjdan hemen sonra; E2 14,6 V'u anıyor) sağlam bölücü de aralığın üstünü okur: önce "alt direnç eksik",
  sonra "bölücü sağlam" deniyor.
- **Dört durum:**
  1. Akü aralıkta, okuma orana uygun → okuma 1,95–2,20 V içinde → geçer. **Doğru.**
  2. Akü aralıkta, okuma orana uygun değil → okuma aralık dışıysa "bölücü bozuk": **doğru**. Okuma aralık içindeyse (oran birkaç
     yüzde kaymış) hiçbir dal yok, "karşılaştır" cümlesi eylem vermiyor. Kalibrasyonla düzelir denebilir; **eksik ama zararsız**.
  3. Akü aralık dışında, okuma orana uygun → okuma aralık dışı → "akü aralığa gelene kadar devam etme" sonucu **doğru**. Ama
     "yakınsa" ölçütü sayısız; yukarıdaki çelişen teşhis de önce okunuyor.
  4. Akü aralık dışında, okuma orana uygun değil → okuma aralık dışıysa "belirgin farklıysa bozuk": sonuç doğru ama ölçüt sayısız.
     Okuma aralık içine düşerse (ör. akü aralığın biraz altında, oran biraz yüksek) **hiçbir dal yok, aşama 2'ye geçilir**; "akü
     aralığa gelene kadar devam etme" kuralı işlemiyor. **Yanlış.**
- **Sayılar:** oran 18 / 118 = 0,15254 → "0,1525"; 12,8 × oran = 1,9525 → 1,95; 14,4 × oran = 2,1966 → 2,20; 14,6 V → 2,23 V, ESP32
  ADC 11 dB doğrusal bölgesi ≤ 2,45 V içinde (`planlama/adim3/elektrik.md:234`). Doğru.
- **"Belirgin farklı" / "yakın":** kaynakta dayanak yok. E2 satırı (`elektrik.md:234`) yalnız değer, oran ve "bir kez multimetreyle
  kalibre et" diyor; tolerans yok. "Küçük fark kalibrasyonla düzelir" E2'nin söylediğinden biraz fazlası ama zararsız. İlk kez kuran
  biri "belirgin" ile karar veremez. Önerim sayı uydurmadan ölçütü gereksiz kılmak: akü aralık dışındaysa bölücüye hiç geçilmez; akü
  aralıktayken bant birebir eşlendiği için karar yalnız {v.aku_olcum} bandıyla verilir.
- **Ölçüm güvenliği:** sıra güvenli (akü ayrıkken akü gerilimi; uçlar bağlanır; ana anahtar kapalıyken akü takılır, sonra açılır;
  aralık dışında kapat → ayır → sök). Uyarı eksiği: akü tarafındaki XT60'ın erkek mi dişi mi olduğu kayıtta yok
  (`planlama/adim3/kablolar.json:561`); metin "pimine" diyor. Nötr "kontağına" ve "bir uç iki kontağa birden değmesin" daha doğru.
  Multimetre kademesi ve V soketi önceki maddede kurulduğu için A soketi kısa devresi bu sırayla açılmıyor.
- **Okunurluk:** çözülmüş madde 2.102 karakter. Brief'teki ≈ 2.300 karakter mantar maddesi (`kontrol[1]`, 2.330). Bölünmesi önerilir:
  `ZORUNLU_SIRA` ve `ZORUNLU_ALAN` aynı alanın maddelerini birleştirip sınadığı için üç maddeye bölmek kuralları bozmaz.

**Önerilen metin** (üç kontrol maddesi; yer tutucular aynı, devre değeri değişmez):

> Akü ölçüm teli (G07), aşama 1'de mantar ölçümünden sonra: ana anahtar kapalı, akü XT60'tan ayrıkken multimetreyi DC V kademesinde
> bırak (kırmızı uç V soketinde). Önce akünün kendi gerilimini oku: akü XT60'tan ayrıkken kırmızı ucu akünün XT60'ındaki (akü tarafı)
> + kontağına, siyah ucu − kontağına değdir (bir uç iki kontağa birden değmesin, iki uç birbirine değmesin), okunanı not al: bu akü
> gerilimidir. Akü gerilimi {v.aku_aralik} dışındaysa burada dur: bölücü ölçümüne geçme, ana anahtarı açma, aşama 2'ye (F5) geçme;
> akü {v.aku_aralik} aralığına gelince bu maddeyi baştan yinele (akünün şarjı bu adım için kaynakta yok, doğrulanmadı).

> Akü gerilimi {v.aku_aralik} içindeyse: kırmızı ucu arayüz kartındaki akü ölçüm bölücüsünün orta noktasına (G07'nin kart ucu), siyah
> ucu yıldız barasının akü dönüşü (G05) saplamasına bağla. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: okunan
> gerilim akü geriliminin bölücü oranı ({oran.aku_olcum}) katıdır: akü {v.aku_aralik} iken bölücünün orta noktasında {v.aku_olcum}
> okunur (`planlama/adim3/elektrik.md` E2). Bölücü okumasını not al; beklenen bölücü okuması = akü gerilimi × bölücü oranı
> ({oran.aku_olcum}): ikisi ESP32'nin bir kez yapılan multimetre kalibrasyonunda kullanılır (E2; dirençlerin toleransı kaynakta yok,
> kablajda teyit). Okuma {v.aku_olcum} içindeyse bölücü geçer. Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök.

> Okuma {v.aku_olcum} aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Akü
> gerilimi {v.aku_aralik} içinde olduğu için bölücü bozuk: hiç gerilim okunmadıysa G07'nin pabucu, direnci ya da kart ucu kopmuş;
> aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış. Akü ayrıkken bölücüyü kontrol et: G07'nin direnci (pabuç ile
> bölücünün orta noktası arası, K1 kontrolündeki direnç ölçümü), direncin ve G07'nin iki ucundaki lehim, bölücünün alt direnci.
> Bölücünün orta noktası ESP32'nin akü ölçüm pinine bağlı (B6a, X01): bölücü düzelip okuma aralığa girene kadar ana anahtarı yeniden
> açma, ESP32'ye bu bölücüyle enerji verme, aşama 2'ye (F5) geçme. Bölücüde kusur bulunmazsa da devam etme: akü gerilimini ve okumayı
> kayda yaz (tolerans kaynakta yok).

Birlikte değişmesi gerekenler: `ZORUNLU_ALAN` F1 maddeleri (`rehber_denetim.py:339-350`). "pimine" kalıbı `:341`, "içindeyse ya da …
belirgin" `:344` ve "dışındaysa ve … yakınsa" `:346` bugünkü kusurlu cümleleri kilitliyor. Yerlerine "dışındaysa burada dur", "Akü
gerilimi … içindeyse: kırmızı ucu", "içinde olduğu için bölücü bozuk" ve "kusur bulunmazsa da devam etme" gelmeli. `ZORUNLU_BOZMA` F1
satırları (`:1830-1845`); ASCII izinli listeye yeni sözcükler gerekebilir; onay kaydı yenilenir. `ZORUNLU_SIRA` F1 maddesi metinle
uyumlu kalır.

### D2 · K2 madde 5'in ilk cümlesi AU3 için sırayı geri sarıyor (`rehber_metin.py:827`)

Ölçüm: çözülmüş metin harfiyen izlendi. Madde beş kabloyu (U03, H02, S10, AU3, G17) sayıyor, sonra "Kafa ucunda bağla (…)" diyor. Bu
AU3'ü de kapsıyor. Ardından gelen "lehimden önce … + damarını … bul" cümlesi, AU3'ü bağlamış birini geri gönderiyor. Öbür sıra doğru:
enerjisiz koşul lehimden önce; lehim, kutup kontrolü ve "Sonra dikişleri sık" bu sırada; PAM8403 eşlemesi kayıtla aynı (+ → L+,
− → L−; `kablolar.json` AU3 damarları). "Dikişleri sıkmadan önce" iki kez geçiyor (yinelenen hatırlatma; iş iki kez yaptırılmıyor).

**Önerilen metin** (yalnız ilk parça değişir; `ZORUNLU` K2 deseni `rehber_denetim.py:188-192` ve `ZORUNLU_SIRA` olduğu gibi tutar):

> Öbür dört kabloyu (U03, H02, S10, G17) kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). Hoparlör kablosu (AU3), dikişleri
> sıkmadan önce, enerjisizken (akü XT60 ayrık): lehimden önce hoparlör kablosunun (AU3) + damarını iki ucunda multimetrenin süreklilik
> kademesiyle bul ve işaretle (iki ucu da boşta). Hoparlör kablosunun (AU3) kafa ucunu PAM8403'ün sol kanal çıkışına lehimle: …

### D3 · Kuyrukta yanlış sayı (`planlama/d158/karar-kuyrugu.md:1461`; ayrıca `F10j-gunluk.md:127`)

"yeni yakalanan 6 doğru Türkçe sözcük" yazıyor; izinli listeye `rehber/index.html` için **7** sözcük girdi (`rehber_denetim.py:138`:
"neresi" de var). Önerilen: "yeni yakalanan 7 doğru Türkçe sözcük (\"Robotun neresi\"nin \"neresi\"si dahil)". Yedisi de doğru Türkçe.

## Öbür bulgular (kayıtlı açık iş)

- **K1 G07 (`rehber_metin.py:325-333`):** sıra uygulanabilir. Makaron geçirilir, uzakta tutulur; direnç tele lehimlenir; bacak kovana
  sıkılır ve lehimlenir; soğuyunca makaron kaydırılıp büzülür. Makaron cümlesi lehimlerden önce okunuyor; çelişki ve yinelenen iş yok.
- **Basılı sayfa:** taşma yok (aşağıda). F1'in G07 maddesi 46. sayfada tek blok, yazı 9,1 → 8,7 pt; K2'nin ilk sayfası (42) 8,9 →
  8,6 pt. Alt sınır 8 pt'un üstünde.
- **`pdf_tamlik` kapsamı dar:** (a) devam sayfasında sondan ikinci satırın yinelenmesi yakalanmıyor; (b) devam sayfasının ilk satırının
  sayfa sonunda yeniden basılması yakalanmıyor; (c) bir maddenin yarısının yeniden basılması yakalanmıyor. B4b yalnız son 20
  karakteri arıyor; B5 madde bütününü sayıyor. (d) Yanlış alarm riski: sayfa başlığında ya da sayfa etiketinde de geçen kısa bir madde
  (ör. adım adı, "Kontrol listesi") çok sayfalı adımda yineleme sayılıyor. Taban sayfa başlığını her devam sayfası için saymıyor.
  Bugünkü veride 0; ileride kısa erişim / kontrol maddesi üretimi düşürebilir. Öneri: tabana sayfa sayısı × başlık ekle ya da B5'i
  TAM_EN_AZ'dan kısa maddelere uygulama. `pdf_tamlik_bozma` hiçbir komuttan çağrılmıyor (yalnız elle).
- **`ZORUNLU_SIRA` K2 kalıbı dar:** `dikişleri\s+sık(?!\w)` "dikişlerini sık" ve "dikişleri sıkıp" biçimlerini görmüyor. Dikişleri
  baştan sıkan bu iki bozma kural sayımında kaçtı; ilkini onay kaydı yakaladı (fark 1), ikincisine onay kaydıyla bakılmadı. Öneri: `dikiş\w*\s+sık(?!madan|ılmadı)\w*`.
- **AU3 lehim cümlesinin kutbu kilitli değil:** "+ → L−" ters çevrilmesini `ZORUNLU` / `ZORUNLU_SIRA` görmüyor (yalnız kutup kontrolü
  cümlesi kilitli); onay kaydı yakalıyor. "(iki uç birbirine değmesin)" ve "okunanı not al" silinmesi de yalnız onay kaydıyla yakalanıyor.
- **A1 kalıbı (`rehber_denetim.py:549-550`):** ünsüz yumuşaması kaçıyor: "aynı kontağa" ve "tek kontağın vidasına" yakalanmıyor.
  Meşru "tek tek kontak vidalarına" yanlış alarm veriyor. Öneri: `konta[kğ]\w*` ve "tek tek" dışlaması.
- **A2 bağlamı (`:1229`):** `\bokuma\b` çekimli biçimleri ("Okunan 2,0 V", "Okumayı 2,1 V …") ve "Bölücü çıkışında 2,05 V" biçimini
  görmüyor. "Okuma için … 20 V kademesine al" biçiminde yanlış alarm veriyor. Bugünkü kaynakta alarm 0.
- **A3 (`:1382`):** bugünkü kaynakta eski ve yeni kalıpla talimat sayılan kablo kümesi aynı: 74 / 74, fark yok. Kalan sınır: "N tel:"
  biçimli gerçek bir ok talimatı hâlâ liste sayılıyor.
- **A7 (`:421`):** "vb." ile biten bir cümleden sonra gelen cümle artık ayrılmıyor ("…makaron vb. Sonra …" tek parça). Küçük bir
  gevşeme; `ZORUNLU_CUMLE` aynı cümleyi arıyor.
- **A8:** kendi altı bozmam yakalandı (`index.html` aria-label ve placeholder, `app.js` placeholder ataması, `innerText +=`, şablon
  title); karşılaştırma dizgesi yakalanmadı (doğru). Görünen dizge 137, ASCII kalıntı 0.
- **`rehber_kablo.py` (R8):** dört bozma (G19, G20, G24, G26) ve b41–b44 onaysız da yakalanıyor. Sistematik bozmalarım:
  - Her yoldan tek kablo çıkarınca geometri 27 / 39'u yakaladı. Kaçan 12'nin hepsi bilinen sınıfta: tek kablolu yol (2, 8, 9, 12),
    vekil yan (G09, G11, G12, G13) ya da elle bakılan yan (S09, S10, A04, A06). Bunları onay kaydı ve 51 / 23 sayımı koruyor.
  - Her yola aynı sınıftan bir kablo ekleyince geometri 127 / 135'i yakaladı. Kaçan 8 (yol 1 + G06; G09 / G11 / G12 yol 5 / 7'de;
    G10 yol 1 / 8'de) vekil, muaf ya da elle bakılan yan.
  - Dikkat: "XT60E-M" artık haritada "modelsiz". Önceden G06'yı bir yola eşlemek "haritada yok" hatası veriyordu; bugün yalnız onay
    kaydı yakalıyor.
  - Elle bakılan yan dal kuralında da "sağlanmış" sayılıyor (`rehber_kablo.py:762`).
- **"Bilgi" 4 → 6 (S09 / S10 kart ucu):** önceki "sınama" kartı yanlış yerde (kafa bölgesinde) varsayıp geçiyordu. Şimdi kararla
  (P7b2a-6) tutarlı ve açıkça "elle bakıldı"; günlükte (`F10j-gunluk.md` R8) ve kuyrukta kayıtlı, savunulabilir. Kalan tutarsızlık
  kayıtta: `kablolar.json`'da S09 / S10 / SV3 / P03 uçlarının parça adı hâlâ "Dağıtım kartı C (kafa)". Paket dışı; açık iş.
- **Kayıtlar:** `dongu-158.md:42`, `:164` ve § 5 girdisi (`:184`) gerçekle aynı. Commit `4a097fb` yazar zamanı 07:03:17, commit zamanı
  07:04:28; sayılar 49 / 14 / 63, 216, 44, 167, 10 / 10, 38, 51 / 23, bilgi 4 → 6 ölçümümle aynı. P10.7b2a / K63 ile aynı satırda
  "bekliyor" 0. K62 açık kaldı, not "karar verilmiş değil" diyor. K52 / K60 / K61 değişmedi. Kontrol-3 A1–A7 ve kontrol-4 A1–A6
  kuyrukta eksiksiz. `R-gunluk.md` sayıları (50 adım, 1192 parça, 49 şema, alt adım 71, PDF 80; F10i 79 → 80, ≈ 3645; F10g / F10h)
  kaynaklarıyla aynı.
- **Ön bilgi (bu paketin değil):** aşama 1'de F4 takılı olduğu için G07 ölçümü ESP32'yi de besliyor. "ESP32'ye bu bölücüyle enerji
  verme" ancak ilk okumadan sonrası için geçerli; akımı 100 kΩ sınırlıyor (`F10i-kontrol-3.md` § 6 bilgi).

## Nasıl ölçtüm

1. **Çözülmüş metin:** `rehber_metin` içe aktarıldı; `4a097fb`'deki sürümle alan alan karşılaştırıldı. Yalnız K1 `is_`, K2 `is_`,
   F1 `kontrol` değişmiş; bugünkü veride üçü eski metne eşit.
2. **Basılı sayfa:** `rehber/` kopyasında (`yazdir.html`, `stil.css`, `goruntu/`, veri) yalnız bu üç alan yeni çözülmüş metinle
   değiştirildi. Aynı tarayıcı bayraklarıyla (`--dump-dom` ve `--print-to-pdf`) koşuldu. Temiz kopya bugünkü `kontrol.json` sayfa
   eşlemesini birebir verdi (yöntem doğrulandı). Sonuç:
   - Yeni metin: HTML 80, PDF 80 sayfa, taşan yok, 8 pt altı yok, en küçük 8,1 pt.
   - Sayfa eşlemesi değişmedi: K1 19–22, K2 42–43, F1 44–49.
   - `pdf_tamlik` yeni PDF'te geçer: eksik 0, yineleme 0.
   - Değişen yalnız iki sayfanın yazı boyu (yukarıda).
   - Tahmin değil ölçüm; gerçek üretimde görüntüler yeniden çekilir, sayfa düzeni aynı CSS ile aynı kalmalı.
3. **Onay kaydı:** iki sürüm girdi girdi karşılaştırıldı. Kablo 94 → 100, liste 180 → 193, metin 991 → 997; fark 38 (kablo 7, liste 17,
   metin 14) ve ayrıca iki girdinin yalnız "neden" etiketi değişmiş. Silinen uyarı yok; E3a TVS cümlesi aynı metin, tek girdi. G22,
   X01, P01–P03, AU3 / H02 girdileri bozulmamış; K52 / K60 / K61 metni yok.
4. **`pdf_tamlik`:** bugünkü PDF + veri ile doğrudan çağrı: geçer, adım 50, madde 402, eksik 0, yineleme 0, fazla 0. Ajanın
   `pdf_tamlik_bozma`'sı 10 / 10. Kendi bozmalarım:
   - Yakalandı: son iki satırın yinelenmesi; son satırın yarısı; F1'de kontrol, alt adım ve erişim maddesinin ikinci kez basılması;
     F1 `kablo`, F5 `baglanti_md`, H0a `erisim` ortasından 25 karakter silinmesi.
   - Kaçtı: (a)–(c) yukarıda.
   - Meşru durumlar: başka adımda aynı cümle, aynı cümle iki alanda, "M3×14" geçti. Başlıkta / sayfa etiketinde geçen kısa madde
     yanlış alarm verdi (d).
   - Eşik `TAM_EN_AZ` 20 aynı; `gecti` sıkılaştı.
5. **Denetim kuralları:** depodaki modüller içe aktarılıp bellekte bozuldu (dosya yazılmadı).
   - `ZORUNLU` / `ZORUNLU_SIRA`: 16 geçerli bozmamdan 11'i kural sayımıyla yakalandı ("lehimden sonra geçir", makaron iki lehimden
     sonra, "Hemen makaronu", dikiş cümlesi silindi, enerjili, F1 akü gerilimi sona taşındı (iki biçim), "dışındaysa ya da", uçlar
     enerjiliyken sökülüyor, "robot tarafı", "devam et"). 5'i kaçtı ("dikişlerini sık", "dikişleri sıkıp", AU3 kutbu ters, "değmesin"
     silindi, "not al" silindi); bunların dördü onay kaydıyla yakalandı, "dikişleri sıkıp" onay kaydıyla sınanmadı. Bir deneme metin
     bulunamadığı için atlandı.
   - Yasak, çıplak, liste, cümle bölücü, A8 sonuçları bulgularda.
6. **Kuyruk:** özet tablosunun 63 satırı (`karar-kuyrugu.md:16-78`) durum sütunuyla tek tek sayıldı: açık 49, kapandı 14, başka durum
   0, eksik ya da yinelenen numara 0. Kapandı listesi `:80` ile aynı.

## Koşular (çıkış kodu; 08:16–08:18)

| Koşu | Çıkış | Sonuç |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel |
| `kablolar_denetim.py` | 0 | GEÇER |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 167 |
| `rehber_denetim.py --kaynak` | 0 | onay farkı 0 (100 / 193 / 997), tamlık 172 / eksik 0 / muaf 21, kablo 74 / 74, ASCII dizge 137 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 216 / 216, bozulmamış kaynakta hata 0 |
| `rehber_kablo.py` | 0 | 51 / 23, geometri hata 0, bilgi 6, ayırt edilemeyen 0, onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 0 | 44 / 44 |
| `rehber_kol_kablo.py --yazma` | 0 | GEÇTİ |
| `py_compile` (çıktı depo dışında): `rehber_denetim`, `rehber_kablo`, `rehber_metin`, `rehber_uret` | 0 | |
| `node --check rehber/app.js` | 0 | |

## Sınırlar ve gizlilik

- `git diff 4a097fb -- planlama/adim3/kablolar.json` boş. Şunların farkı da boş: `pin-haritasi.md`, `elektrik.md`, `maliyet.json`,
  `kod/`, `rehber/` (veri, görüntü, sayfalar), `planlama/rehber/kontrol.json` ve PDF, `F10h-kontrol*`, `F10i-kontrol*`, taban CAD
  kaynakları. Paketin değiştirdiği dosyalar kapsamla aynı (R1, R2, R3, R4, R6, R8, R10, R29); R5, R7, R9 yapılmamış.
- Kanca: `pre-push`'un yedi içerik kalıbı (anahtar biçimleri, anahtar / parola ataması, e-posta, IBAN / telefon, yerel kullanıcı yolu
  ve bilgisayar adı öneki, takma ad, ekip soyadları) ve yasak yol / ofis belgesi kuralları dosyadan okunup uygulandı. Kapsam: paketin
  8 dosyasının eklenen bütün satırları + `F10j-gunluk.md` (966 satır) ve bu rapor. Eşleşme 0. Tarayıcı yapay örneklerle sınandı (dört
  kalıp tuttu).

## Bakılmadı

Gerçek üretim (FreeCAD verisi, adım görüntüleri, zincir), tarayıcıda ekran görünümü ve "gerçek renk" kipi, `kablolar_denetim.py`'nin
iç kuralları (paket değiştirmedi), PAM8403 ve akü XT60'ının gerçek uç etiketleri (parça yok).
