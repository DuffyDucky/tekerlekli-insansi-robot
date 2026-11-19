# P10.9c bağımsız kontrol: faz sonu (F10), sonuç raporu, tek tablo

Kontrol ajanı, 19.11.2026 14:57–15:05 (sistem saati, +03:00). Dal `lale-duzeltme`, HEAD = uzak = `89134d5`. Uygulama ajanının
günlüğüne (`P109c-gunluk.md`) güvenmeden bakıldı. Bu dosyadan başka depo dosyası yazılmadı; commit, push, `git add` yok.

## Karar: DÜZELTMEYLE GEÇER

Sayılar, üretim ve denetimler doğru ve yeniden üretilebilir: sayfa üreticiden bayt bayt aynı çıkıyor, `F9c-dogrula` (statik ve
tarayıcılı) 0, `F9b-dogrula --tarayicisiz` 0, tarama taze, gizlilik temiz. Sorun metinde: F10 tablosunun "Açık iş" sütununda
kayıtta açık duran dört konu yok, bir "açık" iş aslında 15.11'de kapanmış, push satırı kancanın atlandığını söylemiyor, P10.8
sırasının ilk basamağı kendi ilkesiyle çelişiyor. Paket envanteri tablosu 1400 px'te okunmaz hâle gelmiş. Hepsi üretici metni ve tek
satır CSS ile düzeltilir; FreeCAD ya da rehber üretimi gerekmez.

## 1. Değişen dosyalar (teyit)

`git status --porcelain -uall` 33 satır: 19 eski kir (13 kabuk PNG'si, `yerlesim-kontrol.json`, kökteki 5 betik) + paketin 15 dosyası
(`dongu-158.md`, `F9c-uret.py`, `sonuc-rapor.html`, 10 `F9c-goruntu-*.png`, yeni `P109c-gunluk.md`). Günlükteki liste ile aynı; fazlası
ya da eksiği yok. `planlama/maliyet.json`, `karar-kuyrugu.md`, `tasarim/Robot-Tasarim-Demosu.html`: `git diff --quiet HEAD` üçü de 0.

## 2. Bulgular (önem sırasıyla)

### YÜKSEK

**Y1. F10 tablosunun "Açık iş" ve "Ahmet'in kararı" sütunlarında kayıtta açık duran konular yok.** Yer: `F9c-uret.py` `f10` listesi,
"CAD ve çakışma taraması", "Elektrik ve kablolama", "Parçalar gelince" satırları. Tablo kendini konu başına tam liste olarak sunuyor
("açık iş (karar değil, iş)"), ama şunlar eksik:
- K52 göğüs regülatörü kartının modeli: kart ölçüsü ve panel yeri yok, b2j'de de girmedi (kuyruk K52 "Not (19.11.2026)"; `F10t-gunluk.md`
  § 1.8). Tablo K52'yi yalnız "Bitti" sütununda "kararları rehberde" diye anıyor. Ayrıca `F10u-gunluk.md` "Ahmet'e sorulacaklar" K52 kart
  ölçüsü / ürününü soruyor; ne tabloda ne günlüğün § 5 sorularında var.
- Kabuk ve etek takılıyken güç panelindeki bara somunlarına üstten anahtarla erişim ölçülmedi (kuyruk K64 "Düzeltme turu 1", "Açık
  (ölçülmedi)"; `F10u-kontrol.md` bulgu 3). İlk hafta sonu sıkmasıyla ilgili güvenlik maddesi.
- `u06_port_denetle` 180° ters takılmış ESP32 DevKit'i yakalamaz (kuyruk P10.7b2i bölümü, "düzeltme turu 1" maddesi; `F10u-kontrol.md`
  § 4). Ters takılma ilk enerjide 5 V'u bir GPIO pinine getirir; rehberdeki kontrol tek önlem.
- CAD kablo yolu 11 ve kırpılmış yol 12 elektronik katını ön kesiğin dışından deliyor, yol 10 ön şarj kartına 0,1 mm değiyor (kuyruk K64
  "Açık, CAD"; `F10v-gunluk.md` "önceden olan"). Tablodaki "taban yollarının yeniden tasarımından kalan" ifadesi bunu adlandırmıyor.

Ayrıca (daha küçük): K53'ün "burç 2 oturma sorunu ayrı iş" maddesi (kuyruk K53 "Uygulama"), PC817 çıkış jumper'ının modül gelince
seçilmesi, N02 boyu ve kondansatör yedeği (kuyrukta "Ahmet'e: sipariş" / "proje sahibinin kararı" diye duran, K numarasız iki alım
sorusu), `uygulama-notu.md`'deki kişi adı geçen satırlar (F10y § 2, "karar Ahmet'te").
**Öneri:** "CAD" satırının Açık iş'ine K52 kart zarfı + yer, yol 10 / 11 / 12; "Elektrik" satırına ters DevKit kilidi ve kabuk takılıyken
bara somunu erişimi; "Sipariş" satırının Ahmet sütununa K52 kart ürünü / ölçüsü, N02 boyu, kondansatör yedeği. P10.8 sırasının 3.
basamağına (teyit) K52 kart ölçüsü ve PC817 jumper'ı, 6. basamağına (CAD paketi) K52 zarfı ve yol 10 / 11 / 12.

### ORTA

**O1. Kapanmış bir iş "açık" yazılmış: G19 / G20 / G24 / G26.** Yer: F10 tablosu "Elektrik ve kablolama" Açık iş; `PAKET_SONUC["P10.7"]`
"Kalan"; `TUTARSIZ_F10` 3. not. Kanıt: plan P10.7 hücresinin P10.7b2b kaydı "eşleme dişleri G19 / G20 / G24 / G26 onaysız yakalanıyor";
kuyruk "P10.7b2b'de ele alınan önceki açık işler" (15.11); `F10j-kontrol.md` R8 "dört bozma … onaysız da yakalanıyor". Madde HEAD
üreticisinde de vardı, ama bu paket "Kalan" satırını yeniden yazıp tabloya da taşıdı. **Öneri:** üç yerden çıkar.

**O2. Push satırı kancanın atlandığını söylemiyor.** Yer: F10 tablosu "Depo, yayın ve kayıt" Bitti: "gizlilik taraması push öncesi
kancayla". Kanıt: `F10y-gunluk.md` § 9: kanca kuru koşusu ve push çıkış 1 (iki bulgu, ikisi de yanlış alarm gerekçesiyle), b2j / b2k
`git push --no-verify` ile gitti (Echo kararı, ana oturumun kendi taramasıyla); yalnız üçüncü, tek dosyalık kayıt commit'i (`89134d5`)
kancadan geçti. **Öneri:** "kanca iki yanlış alarm verdi (STEP koordinatı, gömülü görsel verisi); b2j / b2k ana oturumun elle taramasıyla
`--no-verify` ile gönderildi (Echo kararı), `89134d5` kancadan geçti".

**O3. Paket envanteri 1400 px'te okunmuyor.** Yer: sayfanın `#paketler` tablosu; `F9c-goruntu-1400-paketler.png`. Kanıt: tarayıcıda
ölçülen sütun genişlikleri Kod 67, **İş 73**, Durum 136, Sonuç 605, Commit 128, Rapor 57 px; "Commit lenmem iş", "Regresy on", "Modeld e",
başlıkta "RAPO R" harf ortasından bölünüyor. HEAD'deki görüntüde (F9 sonu, 36 paket) İş sütunu geniş ve okunuyordu; değişiklik öncesi
üreticinin çıktısında (uygulama ajanının `once.html`'i, 47 paket) da daralma vardı, bu paketle biraz daha daraldı. Neden: tablo
hücrelerinde `overflow-wrap:anywhere` en küçük içerik genişliğini bir harfe indiriyor, uzayan P10.7 Sonuç / Commit hücreleri yeri alıyor.
Uygulama ajanı bu görüntüye bakmamıştı (günlük § 7). Makine denetimi bunu görmüyor (taşma yok, kelime bölünmesi sınanmıyor).
**Öneri:** F10 tablosuna yapılanın aynısı: `@media (min-width:641px)` içinde paket tablosunun İş sütununa (ör. tabloya id verip
`td:nth-child(2)`) `min-width` ≈ 11em ve `overflow-wrap:normal`; başlıklarda `th{overflow-wrap:normal}`.

**O4. P10.8 sırasının 1. basamağı kendi ilkesiyle çelişiyor.** Yer: `P109c-gunluk.md` § 4 madde 1 ("K31 CAD insert boyu 4 mm", "parça
beklemeden, şimdi"); sayfada "1) … K31 kupon C deliklerini CAD'de hazırla". Kanıt: insert boyu `arayuz.py` `INSERT` sözlüğünde;
`arayuz.py` `carpisma_kos.py` `KAYNAK_SABIT`'te, yani izlenen 17 dosyadan biri: değişince tarama eskir. Kuponun M3 delik derinliği de
`tolerans_kuponu.py`'de `INSERT` boyundan türetiliyor. Günlüğün ilkesi "CAD değişiklikleri bir pakette toplanır (tam tarama ≈ 3,8 saat)".
**Öneri:** 1. basamak yalnız kupon dosyaları (`tolerans_kuponu.py`'de yerel parametre, K54 c / K55 a kuponları); `arayuz.INSERT` boyu
6. basamaktaki tek tam taramalı CAD paketine.

**O5. "Açık düşükler" bölümü F9 sonu hâlinde ve bunu söylemiyor.** Yer: `#dusukler`; görüntü `F9c-goruntu-1400-dusukler.png`. Kanıt:
"Pi hattındaki ikinci P6KE6V8A … modele eklenmedi" (b2j'de modele girdi, F10s § 3), "K11 ve K52 kararı; sonra regülatör …" (ikisi de
kapandı). Takvime "F10 sonu notu" eklendi, bu bölüme eklenmedi; günlük § 7 "güncellenmedi" diyor ama sayfa okuru bunu görmüyor.
**Öneri:** takvimdeki gibi bir not ("F9 sonu hâli; F10'da kapanan K11, K51, K52 satırları yenilenmedi") ya da satırların güncellenmesi.

**O6. K60 cümlesi güvenlik kararını ters okutabilir.** Yer: F10 tablosu "Elektrik ve kablolama" Bitti: "K60 elde acil stop … kararları
rehberde". K60'ın kararı A: elde taşınan acil stop **yok**, köprülü klemens şimdi, demoda mantarın yanında bir kişi (kuyruk K60 satırı).
Bağlamı olmayan okur "elde acil stop eklendi" anlar. **Öneri:** "K60 (elde acil stop yok; köprülü klemens; demoda mantarın yanında bir
kişi)".

### DÜŞÜK

- **D1. Parti 0'ın önkoşulu eksik yazılmış.** Sayfa: "kuponlar insertsiz denenemez"; günlük § 4.2 "İnsertler elde olmalı". Kanıt:
  `F4c-partiler.json` Parti 0 bağımlılığı: 6808-2RS, 625ZZ, M3 / M5 ısıl gömme somun ve kupon D vidaları (K29 erken alım); CF kuponları
  PETG-CF ister (K42). K54 c / K55 a kuponları insert istemez. Öneri: "Parti 0 değerlendirmesi rulman, insert ve kupon D vidası ister
  (K29); CF kuponları K42'ye bağlı".
- **D2. Kapanan kararların kimin olduğu tabloda ayrılmamış.** "Bitti" hücrelerinde K2 a, K51 a, K53 a, K64 a, K52, K60, K66 sahipsiz;
  yalnız "Kararlar" satırı "22'si orkestratörce (Echo), Ahmet'in devriyle" diyor. Öneri: Bitti hücrelerinde "(Echo kararı, geri
  alınabilir)" etiketi ya da giriş notuna bir cümle.
- **D3. Bağlamsız okunurluk.** Yeni bölüm tek başına okununca kodlar açıklamasız: "P10.7b2j", "K53 a", "D6 (`{boy.U06}`)", "E4", "17.4",
  "KT1–KT7", "G19". Ahmet kayıtları bildiği için iş görür; başkası için değil. Öneri: giriş notuna "Kodlar: K = karar kuyruğu maddesi,
  P = plan paketi, 17.4 gibi sayılar rehber alt adımı" cümlesi.
- **D4. Tarihli metin commit'te eskiyecek.** `PAKET_SONUC["P10.9"]` "çalışma ağacında, bağımsız kontrol ve commit bekliyor". Öneri: commit
  öncesi son üretimde metni ve durumu güncelle.
- **D5. Bağlantı sayısının dolaylı okunuşu kabul edilebilir.** `p_bag` demo anahtarı = `montaj-analiz.json` `parcalar[tur=Baglanti]#say`;
  kendim saydım: 937 = 937. Demo eskirse F9b-dogrula yakalar (F10y § 8'de yakaladı). Risk: F9c tek başına koşulursa demo eskiliğini
  görmez. Öneri yok; zincirde F9b koşulduğu sürece yeterli.
- **D6. "Eklem aralığında 0 çakışma" doğru, ama tarama toplamı 364.** `carpisma-sonuc.json` `toplam.cakisma` 364, hepsi aralık dışı
  (`F10x-gunluk.md:74, :112`; 09.11 ile aynı). Cümle hatalı değil; "toplam 364, hepsi eklem aralığı dışında" eklemek yanlış okumayı önler.
- **D7. F10y'de gözle bakılmayan kareler** (17.8–17.12, 32.x'in kalanı, B5a / B6 / E3a, PDF sayfaları) Bitti hücresinde ("rehber b2j
  CAD'ine uyduruldu") belirtilmemiş. Makine denetimi geçti; not olarak eklenebilir.

### Doğru bulunanlar (iddia → kanıt)

- Plan kaydı (`dongu-158.md`): `git diff --word-diff` yalnız P10.7 hücresinin sonuna ekleme; başka yer değişmedi. b2j: K2 a, K53 a
  (ortak hacim 0, en küçük boşluk 0,5 mm = F10s § 2 satır 49), K51 a, K64 a (iki tutucu, dokuz saplama), yollar 2–5, 7–9 baralara, ses kartı
  çıktı, koşu `20261119-075818`, 9 bölüm, eklem aralığında 0, 1.225 / 25,84 / 74 / 937, demo yeniden, F9b 0: `043fb09` iletisi ve F10y
  § 8–9 ile aynı. b2k: içerik, tam üretim çıkış 0, 1238 parça, PDF 87, zincir 2–10 çıkış 0, günlük adları: `3cefae0` iletisi ve F10y § 6,
  § 8 ile aynı; `89134d5` push kaydı. Günlük listesi commit iletisiyle aynı.
- "Düğüm tutucusu"nun Kalan'dan çıkması doğru: `F10h-gunluk.md:154` "düğüm tutucusu (bara)" = K64 tutucusu, b2j'de modelde (F10s § 4).
  (Acil stop düğüm kartının CAD modeli ayrı bir açık iş; hiçbir zaman bu adla Kalan'da değildi.)
- "Taban yollarının yeniden tasarımından kalan" yargısı içerik olarak doğru (yol 10 / 11 / 12 açık; Y1), ama adlandırılmalı.
- Karar sayıları: kuyruk Özet tablosunda açık satırlar K2, K13, K18–K26, K27–K37, K42, K43, K50, K62 = 26; toplam 66; kapalı 40. Grup A
  (K27–K37, K42, K43, K50) 14, B (K2, K13) 2, C (K18–K26, K62) 10. 26 açık kararın her biri F10 tablosunun Ahmet sütununda bir kez geçiyor.
- "Kararlar" satırı: 22'si 17.11'de orkestratörce, Ahmet'in 17.11 02:36 devriyle (kuyruk P10.9b bloğu) doğru. "Pano #7 mesaj #34" doğru
  (`P109b-gunluk.md` § 7). `main` birleştirme onayı (KT-F9b-1), K62 kaydı, K13 Ahmet'te: kayıtla aynı. Alım, bütçe ve sipariş tabloda
  yalnız soru olarak; Echo bir alım ya da sipariş kararı üstlenmemiş.
- Doğrulanmamış şeyler doğrulanmış gibi yazılmamış: U06 portu ve DevKit yönü "teyit" basamağında; 18 mm fiş boyu sayfada iddia edilmiyor;
  bara somunu torku geçmiyor; RV 5.5 pabuç kalınlığı ve M5 saplama başı teyit listesinde.
- P10.8 sırasının öbür bağımlılıkları tutarlı: teyitler (3) CAD paketinden (6) önce; boyun tüneli fiş denemesi demetten önce (K14);
  KT1 → AI HAT+ alımı, KT2 → USB-A uzatma / L dirsek (kuyruk); P10.8'in plandaki dar tanımı korunmuş.

## 3. Sayılar (kendi okumam)

| Sayı | Kaynak | Okunan |
|---|---|---|
| Parça 1.225, kütle 25.835,06 g | `montaj-analiz.json` `parca_sayisi`, `kutle_g` | 1225, 25835.06 |
| Bağlantı 937 | aynı dosya, `parcalar` türü `Baglanti` sayımı; demo `p_bag.deger` | 937; 937 |
| Baskı 74 | `baski-analiz.json` `toplam.adet` | 74 |
| Koşu, bölüm, aralıkta | `carpisma-sonuc.json` `bolumler.*.kosu`, `toplam` | 9 bölümün hepsi `20261119-075818` "tamam"; aralıkta 0 (toplam 364), `tek_kosu` true |
| Adım 50, PDF 87, rehber parça 1238 | `planlama/rehber/kontrol.json` | 50, 87, 1238 |
| Açık karar 26 / 66, grup 14 / 2 / 10 | kuyruk Özet tablosu (elle sayıldı) | aynı |

## 4. Koştuğum adımlar (depo kökünden, `py -3 -B -X utf8`)

| # | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 1 | `tasarim/freecad/carpisma_kos.py kontrol` | 0 | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 2 | `planlama/d158/F9c-dogrula.py --tarayicisiz` | 0 | GEÇER (hata 0): data-j 96, data-h 51, data-kaynak 517 öğe / 600 sayı, bağsız 0, plan 47 = tablo 47, kırık bağlantı 0 |
| 3 | `planlama/d158/F9c-uret.py --cikti <depo dışı>` | 0 | 140.970 bayt; depodaki `sonuc-rapor.html` ile `cmp` aynı |
| 4 | `F9c-dogrula.py --goruntu`, görüntü yolu depo dışına çevrilerek (sarmalayıcı yalnız PNG yazma yolunu değiştirdi) | 0 | GEÇER; 1400 px scrollWidth 1400, 360 px 360, konsol 0, taşan 0; üretilen 10 PNG depodakilerle bayt bayt aynı |
| 5 | `planlama/d158/F9b-dogrula.py --tarayicisiz` | 0 | GECER (hata 0) |
| 6 | Bozma (depo dışı dört kopya, `--tarayicisiz --sayfa`) | 1 / 1 / 0 / 0 | F10 tablosunda grup A 14 → 15: yakalandı (data-h). Kütle 25,84 → 25,48: yakalandı (data-j). "USB ses kartı modelden çıktı" → "modelde duruyor": **yakalanmadı**. "alt adım 91" → "alt adım 17": **yakalanmadı** (17 planda başka yerde geçiyor). Sonuç: denetim JSON'a bağlı sayıları tutuyor; elle yazılmış cümle ve kaynağın başka yerinde geçen sayı onun dışında (günlüğün § 9.4 uyarısı doğru) |
| 7 | Karşılaştırma için HEAD sayfası ve uygulama ajanının değişiklik öncesi sayfası tarayıcıda, depo dışına | 1 / 1 | beklenen (eski sayfalar bugünkü kayda uymaz); yalnız görüntü için |
| 8 | Kancanın kalıpları (anahtar, parola ataması, e-posta, IBAN / telefon, yerel yol, takma ad, ekip adı) çalışma ağacı farkının eklenen 414 satırına + yeni günlüğe | – | 0 eşleşme; "Ahmet" 38 kez (doğru ad) |
| 9 | Koşulardan sonra `git status --porcelain -uall` ve paket dosyalarının md5'i | – | başlangıçla aynı; benim koşularım depoda hiçbir dosyayı değiştirmedi |

Koşulmayanlar: FreeCAD, montaj betikleri, rehber üretimi, `regresyon.py`, `demo_uret.py`.

## 5. Gözle bakılanlar (Read ile açıldı)

- On `F9c-goruntu-*.png` dosyasının hepsi (1400 ve 360 px; üst, kararlar, takvim, paketler, düşükler). Başlık ve tarih doğru, menüde
  "F10 sonu", kartlar 47 / 26 / 66 / 10 / 10. Kesik ya da taşan metin yok; 360 px'te tablolar yığın biçiminde, etiketli. Sorunlar:
  1400-paketler İş sütunu (O3); düşükler içeriği (O5). Maliyet kartında "120.853,83 TL" 1400 ve 360 px'te iki satıra kırılıyor (F9 sonunda
  da öyleydi).
- Kendi bölüm görüntülerim (depo dışı, açık tema): F10 tablosu 1400 px (iki kare) ve 360 px (iki kare), Ahmet'in yapacakları, Sayılarla
  robot, Kayıt notları, P10.7 paket satırı. F10 tablosu 1400 px'te dört sütun, kelime bölünmesi yok, boş hücre yok ("—" bilinçli);
  360 px'te KONU / BİTTİ / AÇIK İŞ / AHMET'İN KARARI etiketleriyle okunuyor. Sayılarla robot'ta iki yeni satır yerinde.
- HEAD'in paket görüntüsü ile değişiklik öncesi sayfanın paket görüntüsü (O3 karşılaştırması).
- Görüntülerde kişisel bilgi (yerel yol, soyad, e-posta) görmedim; yalnız "Ahmet" ve "Efe".

## 6. İki plan sorusu (görüş; karar orkestratörde)

**P10.2: kapatılsın (✅).** Kabulün dört maddesi çentik için tutuyor: iniş boyunca en küçük boşluk 0,5 mm, ortak hacim 0
(`F10s-K53-olcum.json`, F10s § 2; eşik "≥ 0,5" tam sınırda, kat ↔ güç paneli tasarım aralığı); taban içi çakışma 0 (`taban_montaj`
575 çift; tam tarama taban 0); korunan değerler `regresyon.py --yazma` GEÇER, kötüleşen yok (F10y § 8 adım 10); çentik parça
eklemedi, BOM'daki plaka ölçü yazısı değişmedi (F10s § 2). "Parça sayısı ve BOM aynı" maddesinin amacı düzeltmenin yan etkisiz en
küçük değişiklik olmasıydı; b2j'deki parça artışı K51 ve K64'ten, P10.2'nin değişikliğinden değil. Durum hücresine bu ayrım bir cümleyle
yazılmalı. Burç 2'nin oturma sorunu K53'te "ayrı iş" olarak kalır.
Gerekçe (tek cümle): kabulün ölçtüğü şey çentiğin kendisi ve çentik dört maddeyi de sağlıyor; parça farkı başka kararlardan.

**P10.7: kapatılsın, "Kalan" yeni bir pakete devredilsin.** Kalan listede bugün gerçekten açık olanlar: boyların ölçümü (kablolar
gelince, fiziksel), yol 10 / 11 / 12'nin CAD düzeltmesi (sonraki tam taramalı CAD paketi), rehberin açık işleri (17.4 / 32.1 / 17.10
kareleri, D6, `--kaynak` CAD adı açığı, 17.11'de U06). G19 / G20 / G24 / G26 maddesi 15.11'de kapanmış (O1), düğüm tutucusu b2j'de
modelde. Kabul ölçütü ("Pin kararı + K10 / K11 / K14") 14.11'den beri sağlanıyor.
Gerekçe (tek cümle): kalan işler ya parça ya da sonraki CAD paketini bekliyor, yani P10.8 sırasının 3. ve 6. basamaklarına ait; P10.7'yi
🔄 tutmak fazı bu beklemeye bağlar ve yeni paket bu işleri adıyla izler.

## 7. Bakmadıklarım

- Koyu tema görüntüleri; Edge / Firefox; yazdırma görünümü; sayfadaki göreli bağlantılara tıklama (denetim yalnız varlık sınadı).
- Kuyruğun 164–1478 satırları arasındaki madde gövdelerinin hepsi (yalnız K52, K53, K64, K31, Özet ve son bölümler okundu).
- F10r, F10w, F10x, F10u-kontrol günlüklerinin tamamı (yalnız arama ile ilgili satırları).
- Sayfanın F10 tablosu dışındaki elle yazılmış eski metinleri (F9 sonu notları, takvim, korunan değerler) satır satır.
- `F9c-dogrula` [8] `TAKMA_AD` / `SOYADLAR` ortam değişkenleriyle koşmadı; yerine kancanın kalıpları elle uygulandı.

Bitiş: 19.11.2026 15:05.

## Tur 1 kontrolü (19.11.2026, ikinci bakış)

Kontrol ajanı, düzeltme turu 1'den sonra (`P109c-gunluk.md` § 10). Bu bölümden başka depo dosyası yazılmadı; commit, push, `git add` yok.

### Karar: DÜZELTMEYLE GEÇER (iki ORTA bulgu; ikisi de üretici metni / plan hücresi)

İlk turun bulgularının hepsi sayfada ve üreticide kapandı; yeni cümleler kayıtla karşılaştırıldı. Düzeltme iki yeni sorun getirdi
ya da bıraktı:

**T1-O1 (yeni). "Açık düşükler"e kendiliğinden düşen "kuyrukta kapandı: Kxx" notları bulgu kapanmış gibi okutuyor.** Yer:
`F9c-uret.py` `dusuk_not()` (satırın kodunda, bulgusunda ya da sonraki adımında geçen, kuyrukta kapalı her K kodu için not) ve bölüm
notu "Kayıtla çelişen satırların … hücresine F10 notu eklendi". Not "Önerilen sonraki adım" hücresinin sonuna düşüyor; kararın kapanması
çoğu satırda bulgudaki ölçümü ya da işi kapatmıyor. Elle bakılan satırlar:
- K10 satırı (PAM8403 akımı "hesap, ölçüm değil", "T4 ölçümü"): K10 kapandı ama kuyrukta "masa testine bağlı kabul"; ölçüm yapılmadı.
- K38 · K39 satırı ("DS3235 ile düşme ölçümü yapılmadı") ve B-1 · B-2 satırı ("K39 ölçümünden sonra … yeniden hesapla"): K39 d'nin kendisi
  DS3235 düşme ölçümü; ölçüm yapılmadı.
- Madde 18 · 33 satırı (akü süresi ölçülmedi + 6. USB cihazı): K1 kapanışı yalnız cihaz adı yarısını kapatıyor.
- F1b Madde 12 (fiş gövdeleri modelde yok) → "kapandı: K3": K3 fiş gövdeleriyle ilgisiz, yalnız eski satır atfı için anılmıştı.
- F8c :67 (T9'da satırsız atıf) → "kapandı: K9"; F9b D-8 · D-9 (demo `model-yok` metni) → "kapandı: K41": atıf ve demo işi yapılmadı.
Bu satırların hiçbiri kayıtla "çelişmiyor"; bulgular açık. Elle yazılan iki not (K51 ve K11 · K52) doğru: K51 ikinci TVS b2j'de modelde
(F10s § 3), K11 / K52 kapandı ve regülatör modeli hâlâ yok (kuyruk K52 notu).
**Öneri:** kendiliğinden notu "karar kuyrukta kapandı (Kxx); bu satırdaki ölçüm / iş ayrıca açık" biçimine çevir ya da yalnız elle
doğrulanan satırlara not düş; bölüm notundaki "kayıtla çelişen" ifadesini düzelt.

**T1-O2 (devir tamlığı). P10.7b kaynaklı bazı açık işler P10.8 "Devralınan" notunda adıyla yok.** Yer: `dongu-158.md` P10.8 Durum
hücresi; sayfadaki P10.8 satırı ve F10 tablosu. F10y § 10'un maddeleri ve P10.7'nin eski "Kalan" listesi tam devredilmiş (pre-push
istisnası F10 tablosunun Depo satırında; G19 doğru olarak düştü). Ama kuyruğun "Karar değil, iş" bölümündeki, kapanış notu olmayan şu
P10.7b işleri hiçbir yerde adıyla geçmiyor:
- acil stop düğüm kartının CAD modeli yok (kuyruk P10.7b1 "Önceki turlardan kalanlar" ve P10.7b2a "Açık kalan");
- dağıtım kartı C'nin güç panelindeki montaj yeri ve donanımı yok, kart modelde yok: "CAD işi, sonraki paket" (P10.7b2a kontrolü A12);
- 11 yeni taban şeması ve 5 yeni kafa içi / ses şeması çarpışma taramasından geçmedi; kafa giriş kartı ve kart üstü konnektör yerleri
  TAHMİN (P10.7b2c açık işleri);
- KT2 sonucu gelince AU1 / AU2 şeması ve kaydı birlikte güncellenmeli; `TABAN_DISI_BOLGE` gövde bölgesi geniş (P10.7b2b).
P10.7 ✅ olduğu için bu işlerin plandaki tek izi P10.8 notu. **Öneri:** ilk iki ve taranmamış şemalar "sonraki tam taramalı CAD paketi"
grubuna; AU1 / AU2 "parça ya da ölçüm bekleyen" grubuna; ayrıca bir cümle: "P10.7b'nin öbür kayıtlı açık işleri `karar-kuyrugu.md`
'Karar değil, iş' bölümünde izlenir."

### İlk turun bulguları (yeniden bakıldı)

| Bulgu | Durum | Kanıt |
|---|---|---|
| Y1 | kapandı | F10 tablosunda K52 modeli (Açık iş) ve ürünü / ölçüsü (Ahmet), bara somunu erişimi, 180° DevKit + 5 V GPIO sonucu, yol 10 / 11 / 12, burç 2, PC817, N02, kondansatör yedeği, kişi adı satırları; § 4 sıranın 3. / 6. / 7. basamağında. Yol değerleri (0,1 mm; kesik dışı) F10v ve kuyruk K64 ile aynı |
| O1 | kapandı | G19 / G20 / G24 / G26 sayfada, üreticide ve kayıt notunda yok |
| O2 | kapandı | Depo satırı F10y § 9 ile aynı (iki yanlış alarm, ana oturumun elle taraması, kanca atlanarak gönderim, `89134d5` kancadan geçti); kalıba uyan dizi yok (aşağıda tarama) |
| O3 | kapandı | 1400 px paket tablosu sütunları 67 / 179 / 136 / 468 / 139 / 78 px (önce İş 73); görüntüde kelime bölünmesi yok, "RAPOR" tek satır |
| O4 | kapandı | 1. basamak yalnız kupon dosyaları, `arayuz.py` insert boyu 6. basamakta |
| O5 | kısmen | bölüm notu ve iki elle not doğru; kendiliğinden notlar yeni sorun (T1-O1) |
| O6 | kapandı | K60 A: elde acil stop yok, köprülü klemens, demoda mantarın yanında bir kişi (kuyruk K60 ile aynı) |
| D1–D7 | kapandı | Parti 0 ön koşulu `F4c-partiler.json` bağımlılığıyla aynı; Bitti hücrelerinde karar sahibi ve tarih kuyrukla aynı (K58 13.11 yetkisi; K52 / K64 / K66 16.11 Echo; K2 / K51 / K53 / K60 17.11 Ahmet'in devriyle); kod açıklaması girişte; "commit bekliyor" yok; 364 tarama toplamı F10 tablosunda ve "Sayılarla robot"ta (data-j `toplam.cakisma`); bakılmayan kareler Bitti'de |

**Plan (`git diff planlama/dongu-158.md`, kelime farkı):** yalnız üç Durum hücresinde ekleme / değişiklik. P10.2: "⏳" → "✅ 19.11 …",
eski metin "Önceki kayıt:"tan sonra olduğu gibi; gerekçe F10s § 2 (0,5 mm, ortak hacim 0, çentik parça eklemedi) ve F10y § 8 ile aynı.
P10.7: "🔄" → "✅ 19.11 …", eski metin "Geçmiş:"ten sonra korunmuş, ilk turun b2j / b2k kaydı yerinde. P10.8: "⏳ Devralınan …" dört grup
(eksikleri T1-O2). P10.9 ⏳ değişmemiş. Başka satır değişmemiş.

### Koştuğum adımlar (depo kökünden, `py -3 -B -X utf8`)

| # | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 1 | `tasarim/freecad/carpisma_kos.py kontrol` | 0 | "özetleri kayitla ayni" |
| 2 | `F9c-uret.py --cikti <depo dışı>` | 0 | depodaki `sonuc-rapor.html` ile bayt bayt aynı |
| 3 | `F9c-dogrula.py --tarayicisiz` | 0 | GEÇER: data-j 98, sayım 51 (paket 47, 26 / 66, 14 / 2 / 10, düşük 47), data-kaynak 534 öğe / 655 sayı, bağsız 0, plan 47 = tablo 47 |
| 4 | `F9c-dogrula.py --goruntu`, PNG yolu depo dışına | 0 | 1400 / 360 px konsol 0, taşan 0, yatay kaydırma yok; 10 PNG depodakilerle bayt bayt aynı |
| 5 | `F9b-dogrula.py --tarayicisiz` | 0 | GECER (hata 0) |
| 6 | `git diff --quiet HEAD` `maliyet.json` / `karar-kuyrugu.md` / demo | 0 / 0 / 0 | üçü HEAD ile aynı |
| 7 | P10.9 ✅ denemesi: plan bellekte P10.9 ✅ yapılıp (dosyaya yazılmadan) `F9c-uret` + `F9c-dogrula --tarayicisiz` | 0 / 0 | GEÇER; P10.9 satırı "Bu sayfa, F10'un faz sonu yenilemesi …", plan durumları satırı P10.9 ✅, F10 faz cümlesi "Açık: P10.8". Aynı sayfa gerçek plana karşı: çıkış 1 (paket sayımı ve P10.9 durum hücresi). Yani ✅ ancak plan, sayfa ve PNG'ler birlikte üretilirse geçer |
| 8 | Kancanın kalıpları, çalışma ağacı farkının eklenen satırları + `P109c-gunluk.md` + `P109c-kontrol.md` (776 satır) | – | 0 eşleşme |
| 9 | Koşulardan sonra `git status --porcelain -uall` | – | başlangıçla aynı |

**Commit'e girecek liste:** `git status`'ta 19 eski kir dışında yalnız `planlama/dongu-158.md`, `planlama/d158/F9c-uret.py`,
`sonuc-rapor.html`, 10 `F9c-goruntu-*.png`, `P109c-gunluk.md`, `P109c-kontrol.md`. Fazla ya da eksik yok.

### Gözle bakılanlar (Read ile)

- `F9c-goruntu-1400-paketler.png`: İş sütunu okunuyor (O3 kapandı).
- Kendi görüntülerim (depo dışı): F10 tablosu 1400 px üç kare (girişteki kod açıklaması ve plan durumları satırı dahil) ve 360 px;
  "Sayılarla robot" 1400 px (tarama satırında "toplam 364 çakışma, hepsi eklem aralığı dışında" yerinde); paket tablosunda P10.8 ve
  P10.9 satırları ve altındaki düşükler başlangıcı (F10 notları görünüyor); 360 px "Ahmet'in yapacakları" iki kare. Kesik, taşan ya da boş
  hücre görmedim; kişisel bilgi yok.

### P10.9 ✅ görüşü

Kabul ölçütü sağlanıyor: sayfa F10 kayıtlarıyla yenilendi, tek tablo özet var, `F9c-dogrula` statik ve tarayıcılı 0. T1-O1 ve T1-O2
metin düzeltmeleri; ✅'yi engellemez ama aynı üretimde yapılmaları iyi olur. ✅ şu sırayla yazılabilir: plana P10.9 ✅ → `F9c-uret.py`
(depoya) → `F9c-dogrula.py --goruntu` (PNG'ler yenilenir) → çıkış 0 → hepsi aynı commit'te. Plan tek başına ✅ yapılıp sayfa yeniden
üretilmezse denetim 1 verir (adım 7).

### Bakmadıklarım

- Koyu tema; 360 px paket tablosu ve tutarlılık bölümü (üretildi, açılmadı); düşüklerin "Diğer" grubundaki satırların hepsi (yalnız
  yukarıda adı geçenler elle).
- `P109c-gunluk.md` § 10'un komut tablosunu yeniden koşmadım; yerine kendi koşularım.

Bitiş: 19.11.2026 15:20.

## Tur 2 kontrolü (19.11.2026, son bakış)

**Karar: GEÇER.** İki Tur 1 bulgusu kapandı; plan farkı doğru; sayfa ve 10 PNG depodakilerle bayt bayt aynı üretildi. Tek not
DÜŞÜK, engel değil.

### Bulgular

- **T1-O1 kapandı.** Sayfadan çıkarılan düşükler metni: otomatik notlar "F10 sonu: karar kuyrukta kapandı (Kxx); bu satırdaki ölçüm
  / iş ayrıca açık olabilir, kuyruğa bak." (K10, K1, K3, K51 … satırları); "kapandı" hükmü yalnız iki satırda (O-3 · K51 ikinci
  P6KE6V8A, K11 · K52), bölüm notu iki not türünü anlatıyor. 1400 ve 360 px düşükler görüntüsünde aynı metin.
- **T1-O2 kapandı.** P10.8 "Devralınan" notunda beş iş adıyla var (acil stop düğüm kartı modeli, dağıtım kartı C yeri / A12, 11 + 5
  şema taranmadı, AU1 / AU2 KT2'den sonra, `TABAN_DISI_BOLGE`). Üç ek madde kuyrukla aynı: fiş boyları `karar-kuyrugu.md:1772`,
  "yaklaşık 10 cm" ↔ 200 mm `:1798`, G07 bölücü toleransı `:1744`.
- **§ 11.1 "eklenmeyenler":** montajı, CAD'i ya da güvenliği değiştiren bir iş düşmemiş. SDA / SCL maddesi (`:1800`) gerçek bir takas
  değil, denetimin yakalamadığı bir bozma denemesi; XT60E-M "modelsiz" (`:1757`) eşleme denetimi notu; uç adı (`:1758`) adlandırma.
- **T2-D1 (DÜŞÜK):** `:1790` "dağıtım kartı C'deki pan / tilt giriş pininin numarası kayıtta yok" montajda kablo takarken gereken
  bir bilgi; araç / görünüm işi değil, ama rehber "kayıtta yok" diye açıkça söylüyor ve kuyruk cümlesi kapsıyor. Öneri: sonraki
  rehber paketinde P10.8 parça / ölçüm grubuna adıyla alınsın (kart gelince okunur). Bu tur için engel değil.

### Plan farkı (`git diff planlama/dongu-158.md`)

Üç hunk, 5 ekleme / 4 silme: P10.7 hücresi (Tur 1), P10.8 Devralınan notu (Tur 1 + 2), P10.9 hücresi ✅ (eski ⏳ metni "Önceki
kayıt:" altında korunmuş), § 5'in en üstüne 19.11 15:21 satırı. Başka satır değişmemiş. § 5 satırındaki iddialar (F9c statik ve
tarayıcılı 0, F9b 0, çarpışma kaydı aynı; kuyruk, demo, `maliyet.json` değişmedi) aşağıdaki koşularla tutarlı.

### Koşular (depo kökünden, `py -3 -B -X utf8`; çıktılar depo dışına)

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |
| `F9c-uret.py --cikti <depo dışı>` | 0 | `sonuc-rapor.html` ile bayt bayt aynı |
| `F9c-dogrula.py --tarayicisiz` | 0 | 51 sayım; paket 47, açık karar 26 / 66, A/B/C 14/2/10, düşük 47; GEÇER |
| `F9c-dogrula.py --goruntu` (PNG yolu depo dışına) | 0 | 1400 / 360 px konsol 0, taşan 0; 10 PNG depodakilerle bayt bayt aynı |
| `F9b-dogrula.py --tarayicisiz` | 0 | GECER |
| `git diff --quiet HEAD` kuyruk / demo / `maliyet.json` | 0 / 0 / 0 | değişmedi |
| kanca kalıpları (fark + iki yeni dosya, 956 satır) | — | 0 eşleşme |
| `git status` koşu öncesi / sonrası | — | aynı; koşular depoyu değiştirmedi |

**Commit listesi:** paket 15 satır: `dongu-158.md`, `F9c-uret.py`, `sonuc-rapor.html`, 10 `F9c-goruntu-*.png`, `P109c-gunluk.md`,
`P109c-kontrol.md`. Fazlası yok; geri kalanı 19 eski kir (dokunulmadı).

### Gözle bakılanlar (Read)

10 `F9c-goruntu-*.png`'nin hepsi: 1400 ve 360 px üst (başlık "F10 sonu, P10.9", 47 paket, 26 / 66, plan durumları satırında
P10.9 ✅, P10.8 ⏳), kararlar, takvim, paketler (P0.1–P1.7; İş sütunu okunur genişlikte), düşükler (yeni bölüm notu ve not metinleri).

### Bakılmayanlar

- PNG'ler bölümlerin yalnız ilk ekranını gösteriyor; P10.8 / P10.9 satırlarının ve F10 tablosunun alt kısmının görüntüsüne bu turda
  ayrıca bakmadım (metni HTML'den ve plandan okudum).
- Koyu tema; kuyruğun 1479–1871 dışındaki bölümleri; § 11.3 komutlarını birebir değil, kendi koşularımla.

Bitiş: 19.11.2026, Tur 2.
