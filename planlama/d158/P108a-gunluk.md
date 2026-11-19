# P10.8a: kupon dosyaları (K54, K55, K31 kupon C) · uygulama günlüğü

Tarih: 19.11.2026 · dal `lale-duzeltme`, başlangıç `e3aaf94` (yerel = uzak) · commit, push ve `git add` yok.
Paket: P10.8'in 1. basamağı (`P109c-gunluk.md` § 4). Dosya üretildi; kuponlar basılmadı, denenmedi.

**Sonuç: TAMAM.** Üç kupon dosyası hazır. Ölçüler kaynak CAD'den okundu ve kaynakla fark 0. Baskı adedi 74 değişmedi, BOM değişmedi.
Kuponlar Parti 0'ın yanında "toplama katılmaz" bölümüne girdi.

## 1. Tanımlar nereden geldi

| Kupon | Tanım kaynağı | Bu paketteki karşılığı |
|---|---|---|
| K54 c | `karar-kuyrugu.md` K54 (kafa yanakları arası 54,4 = yığın 54,4, sıfır boşluk; c: "kupon basılıp denenir"), ölçüler `F10c-gunluk.md` D1 | Yanak kuponu (gerçek kafa iskeleti dilimi) + yığın mastarı |
| K55 a | `karar-kuyrugu.md` K55 (bindirme dili esneterek; b: pah / ters bindirme), ölçüler `F10d-gunluk.md` § 11.5 | Bant kuponu: orta bant sağ (dil) + göğüs bandı sağ (dudak), dikiş y 1005 |
| K31 kupon C | `karar-kuyrugu.md` K31 teknik yarısı (17.11): M5 Rhino ID5 OD7 L7, delik Ø6,7–6,8; `P109c-kontrol.md` O4 | Kupon C'nin (ve B'nin) M5 delikleri Ø6,6 / 6,7 / 6,8 |

Özetten fark: özet K31 için yalnız kupon C diyordu. Kupon B'nin M5 delikleri de aynı insert içindi ve Ø6,2–6,6 idi, yani yeni
insertle uymazdı; B'yi de değiştirdim (Echo kararı, § 4). K55 için özet tek bir bant demiyordu; en zor dikiş olan orta–göğüs
(1005) seçildi.

## 2. Kupon başına ölçü kaynağı

- **Yanak kuponu:** `kafa/kafa-montaj.FCStd` (md5 `777c6b27…`, koşu öncesi ve sonrası aynı) → "Kafa iskeleti" ∩ kutu. Kutu x (sol dış − 1,
  sağ dış + 1), y iskelet bbox ± 1, z eksen ± 20. Yanak yüzleri dört hatta ölçüldü (`yanak-kuponu.json` `karsilastirma`): 54,4 / 54,4, fark 0.
  Asıl ölçünün betikteki yeri `kafa7_parcalar.py:64-71` (`X_SAG`, `X_SOL`, `X_RUL`); betik bunları içe aktarmaz, FCStd'den ölçer.
- **Yığın mastarı:** aynı FCStd. Dayama x −24,2 ("Egme catali" ∩ eksen çevresi y/z ± 12), kol dış yüzü −23,2, horn 26,9…30,2,
  r 12,5. Mastar boyu 54,4 = yığın 54,4.
- **Bant kuponu:** `kabuk/kabuk-montaj.FCStd` (md5 `54273a1b…`) → "Govde orta bandi sag" ve "Gogus bandi sag" ∩ y [995, 1025].
  Üst sınır göğüs cebi altının (1026,57) altında; betik bunu assert eder. Duvar katmanları yan, ön ve arka hatta kaynakla aynı
  (dil 1,25, dudak 1,5, boşluk 0,25; arkada arka kapak kesiği yüzünden dil 6,2 tam kalınlık, boşluk 0).
- **Kupon B / C:** `arayuz.INSERT[5]` = (7,0, 7,0) assert; delik çapı kupon betiğinde yerel parametre (`M5_DELIK_K31`, `M5_K31`).
  `arayuz.INSERT_DELIK[5]` = 6,4 değişmedi.

## 3. Komutlar ve çıkış kodları

FreeCAD 1.1.4 `freecadcmd`, başlatıcı `~/.robot-cad/run_fc.py` (`FC_SCRIPT=…`). Her seferinde tek süreç. Her log okundu, çünkü freecadcmd
hata verse de çıkış 0 dönüyor.

| Komut | Çıkış | Log |
|---|---|---|
| `carpisma_kos.py kontrol` (başta) | 0 | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| `kafa/yanak_kuponu.py` (son koşu) | 0 | `karsilastirma.sonuc` true, iniş ortak hacmi 0, STL denetimi geçti |
| `kabuk/bant_kuponu.py` (son koşu) | 0 | `karsilastirma` true, STL denetimi geçti |
| `test/tolerans_kuponu.py` | 0 | "bitti"; A STL'si bayt bayt aynı (md5 `0ece3b5e…`), B ve STEP değişti |
| `test/m7_kuponlari.py` (tam) | 0, **ama hata** | `bilezik_kesiti(False)` → `ValueError: width of box too small` (§ 7); çıktı yazmadı |
| `M7_YALNIZ_C=1 test/m7_kuponlari.py` | 0 | "yalniz C bitti [61.0, 17.2, 14.0] 7.4 …" |
| `planlama/d158/F4c-partiler.py` | 0 | liste 74 adet, 7722,7–7780,5 g |
| `planlama/d158/F4c-liste.py` | 0 | "yazildi 348 satir" |
| `planlama/d158/F4c-dogrula.py` | 0 | SONUC: GECTI (4b, 5a, 5b) |
| `carpisma_kos.py kontrol` (sonda) | 0 | "izlenen 17 dosyanin ozetleri kayitla ayni" |

Montaj betikleri (`kafa_montaj`, `kabuk_montaj`, ana montaj) koşulmadı. `regresyon.py` koşulmadı. Kuyruk, plan, `sonuc-rapor.html`,
`maliyet.json` ve `arayuz.py` için `git diff --quiet` çıkışı 0.

## 4. Echo kararları (geri alınabilir)

1. **Kupon B de değişti**, yalnız C değil. B'nin M5 delikleri Ø6,6 / 6,7 / 6,8 (eskiden 6,2 / 6,4 / 6,6), C'ninki Ø6,7 yuvarlak, Ø6,6 /
   6,7 / 6,8 damla, Ø6,7 dikey. Neden: satıcı kuralı 6,7–6,8; bir alt ölçü (6,6) sıkı geçme payını dener. Delik sayısı aynı kaldı
   (B'de 3, C'de 5), böylece K43 sayımı (`F4c-kontrol-sayim`) geçerli kalıyor.
2. **M3 değişmedi.** K31 M3 seçeneği henüz açık; mevcut Ø3,8…4,1 aralığı seçenek A'nın kuralını (3,8–3,9) zaten kapsıyor.
3. **K55 kuponu orta–göğüs dikişi, sağ yarı.** Bu dikiş genişleyen gövdenin en zor yeri; § 11.5'teki girişim de burada ölçüldü.
4. **Mastar PETG, tek parça.** b varyantı (pay verilmiş yanak) üretilmedi; K54 b kupon sonucu kötü çıkarsa uygulanacak bir seçenek.
5. **Yeni kuponlara STEP yok**, yalnız STL + JSON (`boyun_tunel_deneme.py` kalıbı). M7 STEP'inde C gövdesi değişti, D1 / D2 / E
   gövdeleri dosyadan aynen geri okundu (hacim eşleşmesiyle denetlendi).
6. **Kuponlar baskı listesinde elle yazılan bölümde**, Parti 0 tablosunda değil. F4c-liste'nin koruduğu aralıkta, "toplama katılmaz".
   74 adet, kg, sa ve BOM değişmedi. Parti 0 toplamı B ve C'nin hacmi yüzünden çok az değişti: 257,6–420,6 g → 257,4–420,0 g,
   7,32–11,96 sa → 7,32–11,94 sa.
7. **`m7_kuponlari.py`'ye `M7_YALNIZ_C=1` kipi eklendi.** Aynı yöntemle `kupon_bilgi` / `toplam` fonksiyonlarına ayrıldı. D / E
   hatası düzeltilmedi; düzeltmek D1 / D2 / E kuponlarını değiştirir ve ayrı iştir.

## 5. Ölçü karşılaştırmaları

| Dosya | Ölçü (mm) | Hacim | Kütle %100 / tahmini | Süre | 46° üstü çıkıntı | Yazıcı |
|---|---|---|---|---|---|---|
| `kafa/stl/yanak-kuponu.stl` | 72,4 × 40 × 48 | 32,44 cm³ | 41,2 / 20,6 g | 35 dk | 207 mm² (yatay delik tepeleri, asıl parçadakiyle aynı) | X2D ve okul (230) içinde |
| `kafa/stl/yanak-kuponu-mastar.stl` | 30 × 30 × 54,4 | 36,81 cm³ | 46,7 / 16,5 g | 28 dk | 0 | içinde |
| `kabuk/stl/bant-kuponu-alt.stl` | 161,8 × 214,2 × 23,4 | 19,54 cm³ | 24,8 / 24,5 g | 42 dk | 48,9 mm² | içinde |
| `kabuk/stl/bant-kuponu-ust.stl` | 164 × 217,2 × 20 | 23,25 cm³ | 29,5 / 26,9 g | 46 dk | 656,5 mm² (z 12, iç yarı basamağı; göğüs bandının `baski-analiz.json` destek bölgesi z 12,0–14,7 ile aynı) | içinde |
| `test/stl/kupon-b-yuva-mil-somun.stl` | 200 × 95 × 11 | 69,1 cm³ | 87,8 g | — | — | içinde |
| `test/stl/kupon-c-isil-gomme-L1.stl` | 61 × 17,2 × 14 | 10,43 cm³ (eski 10,55) | 13,2 / 7,4 g | 13 dk | 61,5 mm² (eski 59,7) | içinde |

STL'lerin hepsi tek gövde, kapalı ve manifold (geri okuma). STL'den ölçülen delik çapları: B M5 6,6 / 6,7 / 6,8, B M3 3,8–4,1, C M5 dikey 6,7, C M5 yatay 6,7 / 6,6 / 6,7 / 6,8 (delik dibinde,
tüm köşeler aynı yarıçapta). D1 / D2 / E STL md5'leri koşu öncesiyle aynı.

İniş modeli: yanak kuponu +y 0…30 mm hareket boyunca mastarla ortak hacim 0, yüzler temasta (dmin 0). Bant kuponunda üst parça
14 mm yukarıda serbest. Radyal girişim önde 10 mm kala 6,8 mm, yanda 2,1 mm, arkada 0.

## 6. Gözle bakılanlar

Görüntüler scratchpad'de, depoya girmedi: yanak kuponu ve mastarın baskı STL'leri, model koordinatında yanak + mastar ile yanak + gerçek
çatal / servo / horn, bant alt ve üst STL'leri, bant montajı. Yanak kuponunda iki yanak ve tabla şeridi görünüyor, delikler yerinde.
Mastar silindir + dayama + disk. Bant parçaları L / U şeritleri; ön duvar eğimli, alt parçanın arka kolu arka kapak kesiğiyle kısa,
boss'lar görünüyor. Bant montaj görüntüsünde eksen yerleşimi karışıktı; dil-dudak ilişkisi sayısal ölçümle doğrulandı, görüntüyle değil.
Kupon B ve C'nin yeni STL'lerine bakılmadı; doğrulama sayısal (delik çapı ölçümü).

## 7. Denetlenmeyenler

- Hiçbir kupon basılmadı; dilimleyici (Bambu Studio) süre ve kütleyi vermedi; değerler `test/README.md` yöntemiyle tahmini.
- Kuponların asıl parçaya göre esnekliği: dilimler kısa, bant kuponu gerçek banttan rijit / esnek farklı davranır (README'de kısıt yazılı).
- Yanak kuponunda 625ZZ ve pim yok; sıkılınca oluşan eksenel yük kupon kapsamı dışında.
- M7 D / E bölümü bu pakette koşmadı; D1 / D2 / E kuponları 15.10 koşusundan ve Y2a sonrası dirsekle (`DIRSEK tup_uc_y` −170) **eski**.
- `F4c-rapor.html`, `F4c-gunluk.md`, `F4c-kontrol.md` ve `karar-kuyrugu.md:810` eski Parti 0 sayılarını (175,8–301,4 g CF,
  257,6–420,6 g, C 7,5–13,4 g) anıyor. Fark ≤ 0,6 g; tarihsel kayıt olarak bırakıldı, `karar-kuyrugu.md` yasak.
- `F9c-dogrula.py` koşulmadı; F9c yalnız adet okur, adet değişmedi.

## 8. Kontrol ajanı için riskli yerler

1. `m7-kuponlari.step`: C gövdesi yeni, D1 / D2 / E eski STEP'ten `Import.insert` ile geri okundu; sıra nesne adına göre. Hacim
   eşleşmesi assert'li, ama yüz / renk / ad bilgisi eskisiyle aynı değil (etiketler yeniden yazıldı). Telefon kalıbına bir eşleşme var
   (bir CARTESIAN_POINT ondalığı, D / E gövdesinde; sayı burada bilerek yazılmadı); HEAD'de de vardı, eklenen satırlarda 0. `tolerans-kuponu.step`'te 0.
2. `m7-kupon-sonuc.json`: C kaydı yeni, D / E kayıtları eski; `yalniz_c` alanı bunu yazıyor. `arayuz.INSERT_DELIK` alanı güncel arayüzden yazıldı (değer aynı, 6,4).
3. `m7_kuponlari.py` yeniden düzenlendi (`baski_kontrol`, `kupon_bilgi`, `toplam` C'den önceye taşındı). Tam kip D / E hatası
   yüzünden hâlâ koşmuyor; davranış değişikliği yalnız `M7_YALNIZ_C=1` kipinde.
4. Bant kuponu üst parçasının z 12 basamağı destek ister. Destek dudağın içinden temiz çıkmazsa ölçüm bozulur.
5. K55 ön girişimi (10 mm'de 6,8 mm) "esneterek" ile karşılanabilir mi şüpheli; kupon büyük olasılıkla K55 b'ye götürür.
6. Yeni dosyalarda yerel yol, takma ad, e-posta, anahtar, ekip soyadı kalıbı: 0 eşleşme (pre-push kalıplarıyla tarandı). Betik
   yorumlarında `~/.robot-cad` geçiyor (hook kalıbına uymuyor).

## 9. Önerilen kayıt (dokunulmadı)

- `dongu-158.md` P10.8 satırına: "1. basamak (kupon dosyaları) 19.11 bitti: yanak / mastar (K54 c), bant alt / üst (K55 a), kupon B / C M5
  Ø6,6–6,8 (K31). `P108a-gunluk.md`. Sıra: Parti 0 ile birlikte bas."
- `karar-kuyrugu.md` K54 "Uygulaması açık" altına: "kupon dosyası hazır (`kafa/yanak_kuponu.py`); sonuç `test/README.md` K54 tablosuna".
  K55'e aynısı (`kabuk/bant_kuponu.py`). K31'e: "kupon B / C M5 delikleri 6,6–6,8; `arayuz.INSERT_DELIK[5]` kupon sonucuyla tam taramalı
  pakette güncellenecek".
- Yeni açık iş: "`m7_kuponlari.py` D / E bölümü Y2a dirseğine uyarlanacak (Y_KAPAK / Y_TABLA sabitleri), D1 / D2 / E STL'leri yenilenecek".

## 10. Sahibine sorular

1. Yanak kuponunu gerçekçi denemek için bir adet 625ZZ ve Rhino M5 / M3 insertleri Parti 0'dan önce alınsın mı? (Satın alma; karar değil.)
2. K29 / K31 / K43 alımları Parti 0 gününe yetişecek mi? Kupon B / C insert olmadan anlamsız.
3. Bant kuponu (≈ 1,5 sa, 51 g) Parti 0 ile mi, yoksa K55 b'yi beklemeden doğrudan geometri değişikliğine mi gidilsin? Model önde
   6,8 mm girişim gösteriyor.
4. M7 D1 / D2 / E kuponlarının Y2a dirseğine güncellenmesi ayrı paket olarak sıraya girsin mi?

## Düzeltme turu 1 (19.11, `P108a-kontrol.md` DÜZELTMEYLE GEÇER; orkestratör kararları)

Commit, push ve `git add` yok. İzlenen 17 dosyaya yazılmadı, montaj betiği koşulmadı. Rehber kaynaklarına dokunulmadı.

### Yapılanlar

| Madde | Durum | Ne |
|---|---|---|
| O1 a | yapıldı | `test/README.md` K55: hangi yolun neden denendiği ("Neden iki yol"); +x yolu kupon diliminde denenebiliyor (üst parça y 1005 omzunda kayar), deneme 2 olarak eklendi. `bant_kuponu.py` +x yolunu ölçüyor (`bant-kuponu.json` `inis_x`): 1–160 mm ortak hacim, 170 mm'de serbest; F10d tam bantla 1–159 / 173. STL'ler bayt bayt aynı (md5 `d0d39af1…`, `858f9e86…`) |
| O1 b | yapıldı | README K55 karar ağacı: deneme 1 (+y) geçerse K55 a, F3 / F4 metni kupondaki yola göre; +x yalnız deneme 2 de geçerse; geçmezse K55 b; sol yarı ve öbür bantlar "çıkarım" |
| O1 c | yapıldı | görüş aşağıda; kuyruğa açık iş |
| O2 | yapıldı (kupon eklenmedi) | etek ön kuponu eklenmedi, gerekçe aşağıda; README, baskı listesi ve kuyrukta "sağ yarı kuponundan çıkarım" notu |
| O3 | yapıldı | `F4c-partiler.py` `m7_eski_uyari()` uyarıyı `F4c-partiler.json` `partiler.0.m7_uyari`'ya yazar; `F4c-partiler.md` Parti 0 tablosunun altında, `F4c-liste.py` üzerinden `baski-listesi.md` kupon tablosunun altında. Fark bugünkü `arayuz.py`'den hesaplanır (`DIRSEK["tup_uc_y"]` −140 → −170); tam M7 koşusu `yalniz_c`'yi silince uyarı kendiliğinden kalkar |
| D1 | yapıldı | README K54: sol ölçüm için 625ZZ şart; rulmansız yuva hizasında aralık 59,4 (beklenen), sol sentil "rulman yok"; geçti ölçütü 625ZZ takılıyken |
| D2 | yapıldı | README: 6,8 de sıkı gelirse kupon C 6,9 ile yeniden üretilir (`M5_K31` nominal 6,8 → damla 6,7 / 6,8 / 6,9); delik sayısı değişmedi |
| D3 | yapıldı | yeni `tasarim/freecad/test/kupon_tazelik.py` (FreeCAD'siz, depoya yazmaz): yanak / bant kaynak FCStd ve STL md5'i, M7 arayüz değerleri; fark çıkış 1, `yalniz_c`'de adı geçen fark "BİLİNEN ESKİ" (çıkış 0; `--kati` ile 1). Zincire bağlı değil; README'de nasıl koşulacağı |
| D4 | yapıldı | `m7_kuponlari.py` yalnız-C kipi `arayuz_kosu` (anahtar başına koşu: INSERT / INSERT_DELIK 19.11, GECME / TUP_PIM_R / DIRSEK 15.10 `6bb1eff`) ve `arayuz_fark_bugun` (`DIRSEK.tup_uc_y` −140 / −170) yazar; yeniden koşuldu, C STL'si aynı md5 (`9e5c6bda…`) |
| 6 kuyruk | yapıldı | `karar-kuyrugu.md` "Karar değil, iş" sonuna P10.8a bloğu: M7 D / E onarımı, K55 rehber metni, etek ön kuponu, çıkarım notu, Ahmet'e iki soru. Özet tablosuna ve karar sayımına dokunulmadı. Demo yeniden üretildi; fark yalnız kuyruk sha'sı (`c25cfb2c9027` → `cb7998d71614`, başka satır yok) |
| 6 plan | yapıldı | `dongu-158.md` P10.8 Durum hücresinin başına tek kayıt, § 5'e günlük satırı (16:18, saat okundu). `sonuc-rapor.html` yeniden üretilmedi: faz sonu sayfası P10.9c anını gösterir, `F9c-dogrula` zaten her yeni commit'te commit sayısından kırmızı verir |
| Baskı listesi | yapıldı | elle yazılan kupon bölümüne üç cümle: sol ölçüm 625ZZ ister; bant kuponu yalnız orta–göğüs sağ yarıyı iki yoldan dener; öbürleri çıkarım, etek ön kuponu yok |

### Echo kararları (geri alınabilir)

1. **Etek ön kuponu eklenmedi.** Engel braket perçin somunu. Braket 2 mm alüminyum L (`arayuz.KABUK_ETEK_BRAKET`); M3 perçin somunu
   alüminyuma ezilerek oturur, PETG'ye aynı biçimde oturmaz. `bant_kuponu.py` kalıbı yalnız bandın dilimini verir. "Somun takılıyken"
   denemesi için braketin ayağı ya da gerçek alüminyum braket gerekir. Bunun basılı bir eşi tasarlanmalı. F10d-K1 c'deki iki bacaklı yol
   da ölçülmedi. Bu yeni tasarım işi; kuyrukta açık iş.
2. **+x yolu ikinci deneme.** Kupon dilimi rehberin yolunu tam bantla aynı eğriyle veriyor (1–160 / 1–159 mm). Ana deneme +y kalıyor:
   +y'de yalnız son 13 mm ortak hacimli.
3. **D1 / D2 / E uyarısı üreticide.** Elle yazılmadı. Uyarı her koşuda bugünkü arayüzden hesaplanıyor.
4. **Tazelik denetiminde bilinen eski çıkış 0.** M7 D / E eskiliği kayıtlı (`yalniz_c`); yeni bir fark çıkış 1 verir. `--kati` ikisini de 1 yapar.

### O1 (c) görüşü

Ters dil cümlesi kupon sonucundan bağımsız bir rehber kusuru ve beklemeden düzeltilmeli. Kupon geçse de geçmese de dil orta bandın iç
yarısı, göğüs bandının alt kenarı dış yarı. "Dilini orta bandın arkasına sok" okuru olmayan bir dili aramaya yollar ve dudağı içe
zorlatır. Önerilen cümle: "alt kenarı alttaki bandın dilinin dışından geçir". Kalıp F1, F3 ve F4 ile çerçeve metinlerinde de geçiyor.
Terslik göğüs | orta dikişinde ölçüldü, öbür bantlarda tek tek bakılmadı.

"+x'ten getir" de kusur: ölçüm (F10d § 11.5) zaten +x'i en kötü yol gösteriyor (1–159 mm, +y'de 1–13). Ama hangi yolun yazılacağına
kupon karar vermeli. Bu yüzden ters cümle bir sonraki rehber üretimli pakette düzeltilmeli; yol cümlesi kupon sonucuyla yazılmalı
(README karar ağacı). Kupon basılmadan rehber üretimi olursa, geçici metin olarak +y yazılmalı. Kuyrukta açık iş olarak kayıtlı.

### Komutlar ve çıkış kodları

| Komut | Çıkış | Log |
|---|---|---|
| `M7_YALNIZ_C=1 test/m7_kuponlari.py` | 0 | "yalniz C bitti"; hata satırı yok; C STL md5 aynı |
| `kabuk/bant_kuponu.py` | 0 | `kars True`, `stl True`, `inis_x` serbest 170; STL'ler aynı md5 |
| `test/kupon_tazelik.py` | 0 | 6 TAZE, 1 BİLİNEN ESKİ (`DIRSEK.tup_uc_y`) |
| `test/kupon_tazelik.py --kati` | 1 | beklenen (bilinen eski de sayılır) |
| `F4c-partiler.py` / `F4c-liste.py` / `F4c-dogrula.py` | 0 / 0 / 0 | 74 adet aynı; "yazildi 352 satir"; SONUC: GECTI (4b, 5a, 5b) |
| `tasarim/cad/demo_uret.py` | 0 | 127 sayı anahtarı; fark yalnız kuyruk sha'sı |
| `F9b-dogrula.py --tarayicisiz` | 0 | GECER (hata 0) |
| `carpisma_kos.py kontrol` | 0 | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| `git diff --quiet HEAD`: `arayuz.py`, `maliyet.json`, `sonuc-rapor.html`, `rehber/`, `tasarim/freecad/rehber/` | 0 | değişmemiş |

### Bakılmayanlar

- Yeni STL üretilmedi: bant ve C STL'leri bayt bayt aynı, gözle yeniden bakılmadı.
- Tazelik denetiminin md5 uyuşmazlığı dalı gerçek bir eski dosyayla denenmedi; çıkış 1 yolu yalnız `--kati` ile sınandı.
- +x denemesinin gerçek bantla davranışı (esneme, kolların takılma yeri) modellenmedi; yalnız ortak hacim.
- F10a / F10d / F10e / F10f, `F9c-dogrula`, `regresyon.py` ve rehber üretimi koşulmadı.

## Düzeltme turu 2 (19.11, `P108a-kontrol.md` "Tur 1 kontrolü"; son tur)

| Bulgu | Durum | Ne |
|---|---|---|
| T1-1 (ORTA) | yapıldı | `dongu-158.md` P10.8 Durum hücresindeki kaçışsız dikey çizgi kalktı ("orta–göğüs dikişi"). P10.8 satırı HEAD'deki kadar hücreli (ayırıcı sayısı aynı); § 5 satırında dikey çizgi yok. Aynı ifade günlükte (tablo satırı dahil), baskı listesinde, kuyrukta ve README'de de "orta–göğüs" yapıldı. Kuyruk değiştiği için demo yeniden üretildi; F9b 0 |
| T1-2 (DÜŞÜK) | yapıldı | `kupon_tazelik.py`: bilinen fark anahtar adıyla değil, `arayuz_fark_bugun` kaydıyla (anahtar + kayıtlı eski değer + o günkü değer) tam eşleşince BİLİNEN ESKİ; bugünkü değer farklıysa ya da kayıtta olmayan anahtar değiştiyse YENİ ESKİME, çıkış 1. README güncellendi |

**Doğrulama:**
- `F9c-dogrula.py --tarayicisiz` (çıkış 1, hata 3, üçü de commit geçmişinden; P10.8 durum hücresi, F10 faz durum hücresi ve `paket_⏳`
  hataları gitti):
  - `HATA: data-h komit_sayisi: sayfa '108', hesap 109`
  - `HATA: data-h komit_eslesmeyen: sayfa '2', hesap 3`
  - `HATA: paket P10.9: konu öneki bu pakette olan e3aaf94 commit hücresinde yok`
- Tazelik, depo dışı kopyada (scratchpad): değişiklik yokken çıkış 0 (6 TAZE, 1 BİLİNEN ESKİ); `tup_uc_y` −180 → çıkış 1 (YENİ ESKİME,
  "o gün −170; bugün farklı"); `TUP_PIM_R` 25,4 → 25,5 (bundan türeyen `DIRSEK.tup_ri` kayıtta yok) → çıkış 1 (YENİ ESKİME, "arayuz_fark_bugun'da
  yok"). Depoda: çıkış 0, 6 TAZE, 1 BİLİNEN ESKİ.

## Kapanış

- Kontrol iki bakışta DÜZELTMEYLE GEÇER (`P108a-kontrol.md` ilk bakış ve "Tur 1 kontrolü"). Tur 2 düzeltmeleri uygulama ajanınca doğrulandı;
  **üçüncü kontrol bakışı yapılmadı.**
- `sonuc-rapor.html` yenilenmedi (faz sonu sayfası P10.9c anını gösterir; F9c'nin üç hatası commit geçmişinden).
- Commit'e giren dosyalar (27; 16 değişen, 11 yeni):
  - değişen: `planlama/baski-listesi.md`, `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md`, `planlama/d158/F4c-partiler.py`,
    `F4c-partiler.json`, `F4c-partiler.md`, `F4c-liste.py`, `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/freecad/test/README.md`,
    `m7_kuponlari.py`, `m7-kupon-sonuc.json`, `m7-kuponlari.step`, `tolerans_kuponu.py`, `tolerans-kuponu.step`,
    `test/stl/kupon-b-yuva-mil-somun.stl`, `test/stl/kupon-c-isil-gomme-L1.stl`;
  - yeni: `planlama/d158/P108a-gunluk.md`, `P108a-kontrol.md`, `tasarim/freecad/kafa/yanak_kuponu.py`, `yanak-kuponu.json`,
    `kafa/stl/yanak-kuponu.stl`, `kafa/stl/yanak-kuponu-mastar.stl`, `tasarim/freecad/kabuk/bant_kuponu.py`, `bant-kuponu.json`,
    `kabuk/stl/bant-kuponu-alt.stl`, `kabuk/stl/bant-kuponu-ust.stl`, `tasarim/freecad/test/kupon_tazelik.py`.
- 19 eski kirli dosya commit'e girmedi.
