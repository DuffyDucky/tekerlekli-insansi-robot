# P10.8b: rehber açıkları · bağımsız kontrol

Tarih: 19.11.2026 · dal `lale-duzeltme`, HEAD = uzak = `1d7fb71` · paket çalışma ağacında, commit'siz. Bu kontrol yalnız bu dosyayı yazdı.
Kaynaklar: `P108b-gunluk.md`, `P108b-olcum/`, `P108a-kontrol.md` (O1, O2), `F10d-gunluk.md` § 11.5, `bant-kuponu.json`, `kabuk_parcalar.py`
(bindirme yapısı), `sag-sol-karari.md`. Bant ölçümü kaynak FCStd'lerden (FreeCAD 1.1, `m6_yukle.yukle`, B-rep, salt okunur, depo dışı).

**Karar: DÜZELTMEYLE GEÇER.** Dil yönü düzeltmesi FCStd'den doğrulandı (bütün dikişlerde dil alttaki / ortadaki bantta, çerçevede
çerçevede). ESP32 yön denetimi, `--kaynak` CAD adları ve D6 istendiği gibi çalışıyor; onay kaydı yalnız bu paketin cümlelerini değiştirmiş;
kaynak sınamaları ve bozmalar beklenen sayılarda. Düzeltilecekler bant metninde: göğüs inişindeki girişim "hafifçe" değil (O1), omuz
metni ölçülmeyen bir dil engeli tarif ediyor (O2), etek ön / F10d çelişkisi çözülmedi ve bu kontrolde de ölçülemedi (O3).

**Ölçüm yarım kaldı:** FreeCAD yol koşusu bellek yetersizliği yüzünden sistem tarafından durduruldu (komutun hatası değil); yeniden
başlatılmadı. Ölçülen: dil yönü (hepsi), çerçeve, göğüs sağ (bütün yollar), göğüs sol (iniş 0–16 / 0–24, yanal L=24). Ölçülemeyen:
göğüs sol yanal L=16, omuz sağ / sol, etek ön sağ / sol (F10d çelişkisi dahil).

## 1. Bulgular

### ORTA

**O1. Göğüs bandı inişi "hafifçe esneterek" değil.**
- Yer: `rehber_metin.py` F3 alt adım 1 ve 2 ("son 12 mm'de bandı hafifçe esneterek alt kenarını orta bandın dilinin dışından geçir").
- Kanıt: B-rep inişte orta bantla ortak hacim 1–12 mm boyunca, en çok 2.221 mm³ (sağ) / 2.083 mm³ (sol); kupon diliminin iniş eğrisiyle
  aynı (`bant-kuponu.json` 2 mm'de 2.221 mm³). Kuponun radyal girişimi 10 mm'de önde 6,8 mm, yanda 2,1 mm; P108a-kontrol O1 bunu
  "hafifçe sözünü karşılamıyor" diye yazmıştı. Kesitte ön yüz dikişte 0,7 mm / mm, yan yüz 0,24 mm / mm genişliyor; arka yüz dik. Tek bir
  öteleme ön ve arkayı birlikte serbest bırakamaz.
- "En az girişimli yol" (günlük § 2.3) ortak hacmin derinliğine ya da hacmine değil, engelin hangi mm aralığında görüldüğüne dayanıyor.
  Yani yolun kolaylığı ölçülmedi.
- Öneri: "hafifçe" kalksın; cümle girişimin büyüklüğünü (önde ≈ 7 mm'ye kadar, kupon ölçümü) ve bu geçişin kuponla karara bağlanacağını
  söylesin. "Bu geçme kuponla denenmedi" notu yerinde.

**O2. Omuz metni ölçülmeyen bir dil engeli tarif ediyor.**
- Yer: F4 alt adım 1 ve 2 ("sonra aşağı indir: hafifçe esneterek alt kenarını göğüs bandının dilinin dışından geçir … Bu yolda engel
  bant değil, Ø84 rulman kapağı").
- Kanıt: y 1198 dikişinde kesit dik. Göğüs dili x 149,0–150,25 ve omuz dudağı 150,5–152,0, y 1200 / 1204 / 1208'de ve z −50 / 0 / 60'ta
  aynı. Düz inişte dil dudağa değmez. Uygulama ajanının kendi tablosunda (§ 2.3, "Omuz sağ +y 16, sonra +x") inişte bant engeli yok,
  yalnız rulman kapağı var. Cümlenin ilk yarısı (esnet, dilin dışından geçir) ikinci yarısıyla (engel bant değil) çelişiyor.
- Not: omuz yolunu bu kontrol B-rep ile ölçemedi (koşu durdu). Bulgu kesit profiline ve ajanın kendi verisine dayanıyor.
- Öneri: F4'te dil cümlesi "dil göğüs bandında; inişte dil engel değil" olsun, esnetme talimatı rulman kapağına bağlansın.

**O3. Etek ön / F10d çelişkisi açık; Notlar'daki eski cümle de duruyor.**
- F10d § 11.5 ve rehberde kalan `ucus_ok` (F1 alt adım 3 / 5, Notlar): "+z'de yalnız braket perçin somunu 1–7 mm, sonra serbest".
  P108b ışın ölçümü aynı yolda 24–162 mm'de şase uzun rayı ve alt plaka buldu. Hangisinin doğru olduğunu bu kontrol ölçemedi (koşu
  etek önden önce durdu).
- Metin iki parçalı yolu (+z 10 mm, sonra yana) yazdığı için düz +z bulgusu yeni cümleyi doğrudan etkilemiyor. "Yanal bacak serbest"
  iddiası ise bağımsız doğrulanmadı.
- P108b haklıysa F10d kaydı ve Notlar'daki "sonra serbest" yanlış. Bu ayrı bir bulgu olur ve metin kapanıştan önce düzeltilmeli.
- Öneri: kapanıştan önce etek ön için +z ve iki parçalı yol, tek FreeCAD süreciyle ve az bellekle (yalnız etek bantları ve engel adayları)
  ölçülsün. Sonuca göre ya `ucus_ok` düzeltilsin ya da P108b § 2.3 geri çekilsin.

### DÜŞÜK

- **D1. F1 notu "kupon sonucu gelince"** etek ön için yanlış beklenti veriyor: o bant için kupon yok (P108a O2). Öneri: F1'de "etek ön
  için ayrı kupon yok; engel perçin somunu" denmesi.
- **D2. Göğüs sol inişi:** B-rep orta bant sağla da 1–4 mm (138 mm³) ortak hacim buldu. Metin x 0'da yalnız göğüs bandı sağı ve ısıl
  gömmeleri sayıyor. Küçük bir eksik.
- **D3. YASAK "bant dili ters" dar.** "Bandı / bandı … dilini X bandın arkasına" kalıbını yakalıyor (büyük / küçük harf fark etmez).
  "Bandın dilini orta bandın arkasına sok", "Göğüs bandının dilini …", "dilini alttaki orta bandın arkasına" geçiyor. Eski cümleye karşı
  yeterli, yeni yazıma karşı değil.
- **D4. `u06_yon_denetle` taşma izi kırılgan.** İz yalnız 1 mm (port taşması); DevKit taşıyıcıda −0,6 mm kayınca "okunamıyor" HATA
  veriyor (yanlış alarm, kaçırma değil; 0,5 mm'de port yüzü denetimi de zaten kırılıyor). Kütle izi sağlam (3,4 mm). Eşik yorumu
  docstring'de var. Kabul edilebilir.
- **D5. `cad_ad_eskime` yalnız bilgi.** montaj-analiz'den bir parça adı düşünce (kaynakta değişince) satır basılıyor, çıkış 0 kalıyor.
  ASCII ve elektrik denetimi artık güncel adlardan yapıldığı için zararsız. Yine de `analizde_eski > 0` uyarı sayılabilir. Üretimin
  `malzeme` alanı da `tr()` ile görünüyor ama `cad_kaynak_metinleri`'ne girmiyor (yeni ASCII malzeme adı `--kaynak`'ta görülmez).
- **D6. 17.4'te saplama numarası yazılı değil.** Metin anahtarlı bara saplama 3 (G09 / G11) diyor. Karede bir sırada 4 saplama sayılabiliyor
  ve "önden bakınca soldan sağa" kuralıyla okunabiliyor, ama kare başlığı "bakış: ön-üstten" diyor, kamera hafif soldan. Gözle kabul
  edilebilir, kesin değil.

## 2. Bant: kendi ölçümüm (FCStd, B-rep)

Dil yönü: dikişin bindirme bölgesinde radyal hatlarla iki bandın kesişim aralıkları. "İçte 1,25 mm" dil, "dışta 1,5 mm" dudak.

| Dikiş | Hat | Dil (içte) | Dudak (dışta) | Ajanla |
|---|---|---|---|---|
| y 1005 sağ / sol | yan z 0, ±60; ön x 60; arka x 100; y 1007 / 1011 / 1015 | orta bant | göğüs bandı | aynı |
| y 1198 sağ / sol | yan z 0, −50; y 1200 / 1204 / 1208 | göğüs bandı | omuz bandı | aynı |
| ön basamak y 1228 (z ≥ 66) | ön x 40 / 80; y 1230–1238 | göğüs bandı | omuz bandı | ajan ölçmedi |
| basamak dikeyi z 66 | yan z 60; y 1205–1225 | göğüs bandı | omuz bandı | ajan ölçmedi |
| z 87,5 sağ / sol | yan; y 60–230; z 90 / 94 / 98 | etek orta | etek ön | aynı |
| çerçeve / göğüs bandı | göğüs normali boyunca 50 × 50 ızgara | çerçeve (15 / 15 satırda arkada, bant iç yüzüne değiyor) | göğüs bandı | aynı |

`kabuk_parcalar.py` yapısı da aynı şeyi söylüyor: iç hücre sınırı dikişten 12 mm yukarıda / önde, yani dil alttaki / ortadaki bandın
iç yarısı. Eski "dilini orta / göğüs bandının arkasına sok" cümlesi ters, çerçeve cümlesi doğruydu.

Yollar. Bandın kendi ısıl gömmeleri bantla birlikte taşındı. Engel: ajanla aynı alt adım kümesi. Ölçü ortak hacim > 1 mm³, iniş 1 mm,
yanal 1 / 2 mm adım. Dinlenmede ortak hacim 0.

| Bant, yol | Benim sonucum | Ajan |
|---|---|---|
| Göğüs sağ iniş 0–16 / 0–24 | orta bant 1–12 (en çok 2.221 mm³), perçin somunu M5 1–13, ısıl gömmeler 1–10 | orta 2–12, gömme / somun 2–14 |
| Göğüs sağ yanal +x, L=16 | serbest | serbest |
| Göğüs sağ yanal L=24 | serbest | serbest |
| Göğüs sağ tarama L=8 / 12 / 20 / 32 | L=8 orta bant 0–158; L=12 sınırda (orta bant 5 mm³, somun 7 mm³); L=20 serbest; L=32 rulman kapağı 0–10 | denenmedi |
| Göğüs sol iniş 0–16 / 0–24 | orta bant sol 1–12 (2.083 mm³), orta bant sağ 1–4, göğüs bandı sağ 1–16 / 1–18, gömmeler, perçin somunu 1–13 | aynı (orta bant sağ yok) |
| Göğüs sol yanal −x, L=24 | serbest | serbest |
| Göğüs sol L=16, omuz, etek ön, düz +z | ölçülemedi (koşu durdu) | günlük § 2.3 |

L=16 göğüs sağda serbest pencerenin içinde. Alt sınır ≈ 12–14 mm, üst sınır 20 ile 32 arasında.

## 3. ESP32 yönü (`u06_yon_denetle`)

Depo dışı kopyada `taban-analiz.json` ve rehber metni bellekte bozuldu:
- (c) değişiklik yok: 0 hata.
- (a) DevKit 180° (kutu ve kütle merkezi taşıyıcı merkezinde aynalı): yön 7 hata (4 port + 3 WROOM cümlesi), toplamda port yüzü
  denetimiyle 8.
- Yalnız kütle izi ters: çelişki HATA. Yalnız kutu ters: çelişki HATA.
- (b) dört cümlenin her biri ayrı ayrı "sağ" → "sol": her biri 1 hata.
- B6a'da yalnız "WROOM sağda": 1 hata. "önden bakınca" silinip sayı 3'e düşünce: 1 hata ("en az 4").
- Kayma (dönme yok): ±0,3 mm 0 hata. −0,6 mm'de "okunamıyor" HATA (D4).

Modelde port gerçekten +x'te: `taban_lib.esp_local` port bileşeni +l/2 ucunda, WROOM −l/2'de. +x, önden bakanın sağı (`sag-sol-karari.md`).
Denetim modeli rehberin dört cümlesiyle karşılaştırıyor. 111 → 114 bozmanın üçü: b104 tam 180°, b105 izler çelişik, b106 B6a "solda".

## 4. `--kaynak` CAD adları

- Kopyada `kabuk-montaj.FCStd` Document.xml'inde bir etikete "cikintisi yesil" eklendi: `--kaynak` çıkış 1, iki ASCII bulgusu.
  Aynı koşuda eskime satırı "analizde olup kaynakta olmayan 1" bastı.
- Çeviri yolu: denetim `RM.tr(etiket)`, üretim `RM.tr(RM.kopya_eki_sil(ad, kod))`. Fark yalnız FreeCAD sayı eki; ASCII için önemsiz.
- 311 → 323 bozmanın 12'si: 5 YASAK_BOZMA (eski F3, eski F4, çerçeve yakalanmamalı, iki kupon iddiası), 4 CAD kaynak (TR_EK'ten
  "saplamasi" / "anahtarli" çıkarma, yeni ASCII parça, FCStd okunamıyor), 3 boy (D6).

## 5. D6

`{boy.<kimlik>}` `kablolar.json` `boy.onerilen_mm`'den çözülüyor. Çözülmüş K2 cümlesi HEAD'deki sayılarla aynı: 950, 920, 1.560, 1.030,
1.720. Cümleye yalnız kimlikler eklendi. Kayıtta boyu olmayan kimlik (G01) ya da bilinmeyen kimlik KeyError veriyor.

## 6. Kareler (depo dışı önizleme, 1200 × 720, açık tema; gözle)

- **17.4:** Röle, anahtarlı bara (4 saplama) ve yıldız barası saplamaları büyük ve seçilebiliyor; etiket 1–4 karede. Sigorta kutusu kadraj
  dışında (UC_ORTULU). Eski karede bara küçüktü ve 5 etiket vardı. Saplama numarası yazılı değil (D6).
- **17.10:** Önden-üstten bakış eskisinden temiz; 8 etiketin 8'i karede. Katın kesiğinden geçiş ancak kısmen seçiliyor. Sonar 8'in mor
  çizgisi sonara ulaşmadan bitiyor; bu eski karede de böyle, bu paketten değil.
- **17.11:** Yeni "2" etiketi ESP32 kartının üstünde; geri kalan kare HEAD çıktısıyla gözle aynı. Çizgi yok, metin
  32.4'e gönderiyor.
- **32.1:** Kamera değişmedi (farkta yok).
- Önizleme verisi: `rehber_gorunum` kopyada çıkış 0. Değişen alanlar yalnız K1.4 kamera / saydam / odak, K1.10 kamera, K2 kablo ve F1 / F3 /
  F4 metinleri. Uç etiketi karede 58.

## 7. Denetim altyapısı

- `rehber_kritik_onay.json`: HEAD'e göre 10 kayıt çıktı, 33 kayıt girdi; `aciklama` aynı. Hepsi F1.3 / F1.5 / F3.1 / F3.2 / F3.5 / F4.1 /
  F4.2 metni, K2 kablo (D6), LISTE ZORUNLU 6 ve LISTE YASAK 2. Kablo bölümü 220 → 220, değişmemiş. Alakasız onay yenilenmemiş.
- `ZORUNLU` 6, `YASAK` 2, `YASAK_BOZMA` 5 yerinde. `ASCII_TAMAM`'daki 7 sözcüğün (dilinin, somunun, kuponla, sonucu, yerinin, kenara,
  yanal) yedisi de doğru Türkçe yazım; hiçbiri bir yazım hatasını aklamıyor.
- `F10l-birlesim.py`: taban `1d7fb71`, `BEKLENEN["1d7fb71"]`. Koşu "eklenen 25 (beklenen 25), silinen 10 (beklenen 10)", GECER.

## 8. Kendi koşularım (depo kökü, `py -3 -B -X utf8`)

| Komut | Çıkış | Sonuç |
|---|---|---|
| `carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| `rehber_denetim.py --kaynak` | 0 | ASCII 0, CAD kaynak 1216, eskime analizde 0 / kaynakta 271 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 323 / 323 |
| `rehber_kablo.py` | 0 | GEÇER |
| `rehber_kablo.py --bozma-denemesi` | 0 | 114 / 114 |
| `kablolar_denetim.py` | 0 | GEÇER |
| `kablolar_denetim.py --bozma-denemesi` | 0 | toplam 174 |
| `F10l-birlesim.py` | 0 | GECER |

- Koşulardan önce ve sonra çalışma ağacındaki 31 kirli / izlenmeyen dosyanın md5'i aynı; koşuların yan etkisi yok.
- `git diff --quiet HEAD`: `kabuk-montaj.FCStd`, `planlama/dongu-158.md`, `karar-kuyrugu.md`, `sonuc-rapor.html`,
  `Robot-Tasarim-Demosu.html`, `demo_uret.py`, `planlama/maliyet.json` değişmemiş.

## 9. Kapanış tarifi ve tam üretim riskleri

Tarife eklenmeli:
- (0) O1–O3 düzeltmesi, ardından `F10l-birlesim` listeleri ve `--kritik-onay-yenile`, sonra kaynak sınamaları yeniden.
- (3'ten sonra) `rehber_kablo` ve `--kaynak` tam üretim verisiyle bir daha (uç etiketi onay kaydı, kablo bölümü).
- `rehber/` çıktısında `git diff` ile yalnız beklenen adımların değiştiğine bakılması.
- Push öncesi kanca.

Kırmızıya düşebilecek yerler:
- F10d kadrajı / U4–U6: 17.10'da yeni kamerayla B01 / Q03 kadraj oranları (eski 0,68 / 0,79) değişir. 17.4'te odaklı kadraj
  "Sigorta kutusu" dışında başka bir ucu da dışarıda bırakırsa UC_ORTULU kaydı eksik kalır. Önizlemede 17.4 4 etiket, 17.10 8 etiket.
- Uçuş denetimi: `ucus` ve `ucus_ok` değişmedi, istisna_bos 0 beklenir. O3 sonucu `ucus_ok` metnini değiştirirse onay ve birleşim
  listeleri de yenilenmeli.
- Yazım denetimi: O1 / O2 düzeltmesi yeni sözcük getirirse ASCII_TAMAM / TR_EK.
- Onay farkı: kaynakta 0; tam üretimde veri metni aynı kalırsa 0.

`P108b-olcum/` (68 KB, 3 betik + 1 JSON): kanca kalıplarına uyan içerik yok, yerel yol yok. Depoya girebilir. `bant_dil.py`'nin yol kısmı
kendi notuna göre kullanılmadı; bunu belirtmek yeter.

## 10. Gizlilik

`.git/hooks/pre-push` kalıpları paketin değişen 7 dosyasının eklenen satırlarına ve yeni dosyalara (günlük, 3 betik, ölçüm JSON'u;
3.070 satır) uygulandı. Anahtar 0, atama 0, e-posta 0, IBAN / telefon 0 (koordinat dizileri dahil), yerel yol 0, takma ad 0, ekip soyadı 0.
Depodaki ad da geçmiyor.

## 11. Bakılmayanlar

Göğüs sol L=16, omuz ve etek ön yolları B-rep ile ölçülmedi (koşu durdu; § 2). F2 ve etek arka dikişleri ölçülmedi. Rehberin tam
üretimi, `F10d-dogrula`, PDF koşulmadı. Panel metinleri tarayıcıda okunmadı. 32.1 karesi görüntülenmedi. `elektrik.md` boyları
bakılmadı.

## Tur 1 kontrolü

Tarih: 19.11.2026 · aynı sınırlar; FreeCAD yeniden koşulmadı (bellek). Kaynak: `P108b-gunluk.md` § 13, `P108b-olcum/brep_liste.py`,
`brep_yol.py`, `brep-yol.json`, çalışma ağacı farkı.

**Karar: GEÇER.** O1, O2, O3 ve D1–D6 kapandı. Aşağıdaki üç not engel değil, kapanışta ya da sonraki turda düzeltilebilir.

### Bulgu kapanışı

- **O1 (F3):** "hafifçe" kalktı. Cümle sıkı geçmeyi sayıyla veriyor: ≈ 2.200 / 2.100 mm³ (ölçümüm 2.221 / 2.083), 10 mm kala önde 6,8,
  köşede 7,8 mm. Ön eğik / arka dik ayrımı ve "oturmazsa zorlama (bant kırılabilir): kupon sonucunu ya da K55 b'yi bekle" açık.
  Sol inişe orta bant sağ 1–4 mm eklendi; ölçümümle aynı. Denenmemiş bir şeyi denenmiş gibi anlatan cümle yok. Göğüs sol yan yolu yalnız
  24 mm diyor; 24'ü ben B-rep ile serbest ölçmüştüm.
- **O2 (F4):** Dil talimatı çıktı. "Kesit dik, düz inişte dil engel değil" benim kesit ölçümümle aynı. Rulman kapağı (inişte dikişin 16–7 mm
  üstü, ≈ 300 mm³; yanal son 4 mm) ve kapak cıvataları serbest gibi değil, engel olarak anlatılıyor. Esnetme kapağa bağlı, "bilinmiyor;
  oturmazsa zorlama" var.
- **O3 (etek ön):** `brep-yol.json` düz +z'de yalnız perçin somunu 2–8 mm (8,9 mm³) veriyor; F10d § 11.5 ve Notlar doğru, `ucus_ok`'un
  değişmemesi doğru. İki parçalı yolda somun kalkışta 1–8 mm (9,4 mm³), yan bacak serbest.
  - F1'deki "1–8" iki parçalı yolun 1 mm adımlı kalkış bacağından geliyor. Düz +z'deki "2–8" aynı hareketin 2 mm adımla ölçümü.
    Tablo ile metin tutarlı.
  - Mesh'in ray / plaka bulgusunun nedeni incelenmemiş; B-rep esas alındığı için kabul.
- **D1–D6:** F1 / F4 notu "Bu geçme denenmedi; bu bant için kupon henüz yok." YASAK genişledi (+6 bozma). ESP32 sınırı docstring'de.
  `analizde_eski > 0` HATA (+1 bozma). K1 alt adım 4'te "soldan sağa (B5a)" cümlesi var.

### B-rep betikleri (koşmadan okundu)

- `brep_liste.py`: engel = alt adım izin kümesi, grup ve referans hariç, glb kutusuyla yol koridoru + 2 mm. Bandın ısıl gömmeleri bantla
  birlikte taşınıyor (benim yöntemimle aynı). Parça eşlemesi `cad_parcalar` sırasıyla (veri sırasıyla aynı; benim koşumda modül ve tür
  1238 / 1238 uyuşmuştu).
- `brep_yol.py`: nesneler modül modül kopyalanıyor, belge kapanıyor. Yerleşim `m6_yukle._global` ile. Ortak hacim > 1 mm³; kalk bacağı 1 mm,
  çık bacağı 2 mm adım. Dinlenme atlaması var ama dört vakada dinlenme boş, yani bir şey maskelenmedi.
- Yollar metinle aynı: etek +z 10 sonra ±x, omuz +y 16 / 24 sonra ±x. `brep-yol.json` günlük § 13.3 tablosuyla sayı sayı aynı.
- Benim dil yönü ve kesit ölçümlerimle çelişen bir sonuç yok.

### Notlar (DÜŞÜK, engel değil)

- **T1. `kaynakta_yeni` 271'in açıklaması eksik.** Günlükteki "montaj-analiz HARIC parçaları ve bazı kodları taşımaz" doğru değil.
  271 metnin 269'u FreeCAD kopya ekli etiket. `cad_kaynak_metinleri` `RM.kopya_eki_sil` uygulamıyor; üretim uyguluyor. Kalan 2'si
  "(gösterim)" etiketleri. ASCII denetimi için zararsız, ama denetlenen metin üretimin gösterdiği metinle birebir değil ve bilgi satırı
  anlamsız. Öneri: `kopya_eki_sil` uygulanması ya da açıklamanın düzeltilmesi.
- **T2. F3 çerçeve notu** hâlâ "kupon sonucu gelince bu adım yeniden yazılabilir" diyor; çerçeve için de kupon yok (F1 / F4'teki D1 ile
  aynı durum).
- **T3. "Oturmazsa zorlama" talimatları eşit değil.** F1'de hiç yok (somun girişimi küçük, 9 mm³). F4'te var ama F3'teki gibi "ne
  beklenir" kısmı yok. Göğüs sağdaki "1–14 mm" aralığını benim B-rep ölçümüm 1–13 mm buldu; önemsiz.

### Denetim altyapısı

- Onay kaydı HEAD'e göre 10 kayıt çıktı, 45 kayıt girdi. Hepsi F1.3 / F1.5 / F3.1 / F3.2 / F3.5 / F4.1 / F4.2 / K1 alt adım 4 / K2 kablo ve
  LISTE ZORUNLU 6 / YASAK 2. Kablo bölümü 220 → 220, değişmemiş; alakasız onay yok.
- `ASCII_TAMAM` +10 (say, kala, dilimi, ikisini, kurtarmaz, esneyip, oturup, oturmazsa, sonucunu, esnetilerek): hepsi doğru yazım,
  hiçbiri bir yazım hatasını aklamıyor.
- `F10l-birlesim`: eklenen 37 / 37, silinen 10 / 10, GECER.

### Koşular (`py -3 -B -X utf8`, depo kökü)

| Komut | Çıkış | Sonuç |
|---|---|---|
| `carpisma_kos.py kontrol` | 0 | 17 dosya kayıtla aynı |
| `rehber_denetim.py --kaynak` | 0 | ASCII 0, onay farkı 0, CAD kaynak 1216, eskime HATA 0 / bilgi 271 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 330 / 330 |
| `rehber_kablo.py` | 0 | GEÇER |
| `rehber_kablo.py --bozma-denemesi` | 0 | 114 / 114 |
| `kablolar_denetim.py` | 0 | GEÇER |
| `kablolar_denetim.py --bozma-denemesi` | 0 | toplam 174 |
| `F10l-birlesim.py` | 0 | GECER |

- Koşulardan önce ve sonra çalışma ağacı md5'leri aynı.
- `git diff --quiet HEAD`: `kabuk-montaj.FCStd`, plan, kuyruk, `sonuc-rapor.html`, demo ve `maliyet.json` değişmemiş.

### Gizlilik

Kanca kalıpları farkın eklenen satırlarına ve yeni dosyalara (`P108b-olcum/` 80 KB dahil, 3.933 satır) uygulandı: bütün kalıplar 0.

### Kapanış tarifi ve commit listesi

- § 13.7 tam: önceki önerilerin hepsi girmiş (3b tekrar koşusu, `rehber/` farkı, kadraj riskleri, kanca).
- `git status`: 19 eski kir + 7 değişen dosya (`F10l-birlesim.py` ve 6 rehber dosyası) + 3 yeni yol (`P108b-gunluk.md`,
  `P108b-kontrol.md`, `P108b-olcum/`). Beklenenle aynı. 19 eski kir commit'e girmemeli.

### Bakılmayanlar

B-rep yeniden koşulmadı. Göğüs sol L=16 hiç ölçülmedi; metin artık bunu kullanmıyor. Tam üretim, panel metinleri ve kareler bu turda
yeniden görüntülenmedi.
