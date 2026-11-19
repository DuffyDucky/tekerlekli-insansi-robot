# P10.8b: rehber açıkları (K55 bant metni, ESP32 yönü, --kaynak CAD adları, kare okunurluğu, D6) · uygulama günlüğü

Tarih: 19.11.2026 · dal `lale-duzeltme`, başlangıç `1d7fb71` (yerel = uzak) · commit, push ve `git add` yok.
Paket: P10.8'in rehber kaynağı tarafı (parça beklemeden kapanabilen beş iş). Rehberin tam üretimi (`rehber_uret.py`) koşulmadı;
yalnız kaynak sınamaları ve depo dışı tek kare önizleme. FreeCAD hiç açılmadı (ölçümler üretimin `robot.glb` mesh'inden, aşağıda).

**Sonuç: TAMAM.** Beş işin beşi kaynakta yapıldı (görev 4'te 32.1 karesi denendi, değiştirilmedi; § 5). Kaynak sınamaları çıkış 0,
bozma sayıları arttı (§ 7). Bağımsız kontrol ve kapanış üretimi bekleniyor.

**Düzeltme turu 1 (§ 13):** kontrol (`P108b-kontrol.md`) DÜZELTMEYLE GEÇER dedi. Göğüs inişi "hafifçe" değil (sıkı geçme, sayılarla),
omuzda dil engeli yok (engel rulman kapağı), etek ön ve omuz yolları FreeCAD B-rep ile ölçüldü. Etek ön +z'de F10d doğru, bu günlüğün
§ 2.3'teki mesh sonucu (şase rayı / alt plaka 24–162 mm) yanlıştı. Güncel kapanış tarifi § 15 (düzeltme turu 2 sonrası, tek başına okunur).

## 1. Tanımlar nereden geldi

| İş | Tanım kaynağı |
|---|---|
| 1. K55 bant metni | `karar-kuyrugu.md` "Karar değil, iş" K55 notları (dil cümlesi düzeltmesi; yol kupon sonucuna göre, README K55 karar ağacı); `P108a-kontrol.md` O1 (c) "kupon basılmadan rehber üretimi olursa geçici metin olarak +y yazılmalı", O2 (etek ön bandı için kupon yok); ölçüm tabanı `F10d-gunluk.md` § 11.5; kupon `tasarim/freecad/kabuk/bant_kuponu.py` |
| 2. 180° ters ESP32 | `F10u-kontrol.md` § 7 (U06 port kilidi DevKit 180° dönerse yakalamaz); `F10u-gunluk.md` açık iş listesi |
| 3. `--kaynak` yeni CAD adlarını görmüyor | `F10y-gunluk.md` (b2k kapanışında 9 sözcük `TR_EK`'e yalnız tam üretimde görülüp eklendi) |
| 4. Kare okunurluğu | `F10y-gunluk.md` (17.1 / 17.6 önden-üstten kamera); 17.4, 32.1, 17.10, 17.11 kuyruktaki iş maddesi; `F10u-gunluk.md` "17.11 açık" |
| 5. D6 | `F10r-kontrol.md` D6 ("K2 Önerilen boylar sayılarını yer tutucuyla (`{boy.U06}` benzeri) kayıttan bas"); kuyruk P10.7b2k açık işleri |

Özetten fark: özet görev 1'de göğüs bandı için "+y" diyordu (P108a O1 c). Ölçümde düz +y yolu 32 mm'den sonra omuz ve kafa
parçalarına giriyor (§ 2.3); metne düz +y değil, iki parçalı yol yazıldı (yandan getir, sonra indir). Özet "dil cümlesi çerçeve
metninde de ters" diyordu; ölçüm çerçevede dil yönünün doğru olduğunu gösterdi (§ 2.2), çerçeve cümlesinin yalnız kupon iddiası
değişti.

## 2. Görev 1: K55 bant metni

### 2.1 Ölçüm yöntemi

FreeCAD'siz: rehber üretiminin `rehber/veri/robot.glb` + `rehber-veri.json` dosyaları (1d7fb71; CAD 043fb09'dan bu yana
değişmedi, `kabuk-montaj.FCStd`'den çıkar). Betikler ve ham sonuç `planlama/d158/P108b-olcum/`:
- **Dil / dudak** (`bant_dil.py`): dikişin bindirme bölgesinde (dikiş + 1…11 mm) radyal ışın satırlarında (ışın aralıkları 1 mm,
  `rehber_giris.Isinlar`) iki bandın hangisinin o yüzde dışta olduğu sayıldı. Yüz başına ayrı: ön (z ışını, z > 40), arka (z < −40), yan
  (x ışını, |x| > 100; etekte |x| > 200 ve üst y > 200).
- **Yol profili** (`bant_profil.py`) ve **iki parçalı yol** (`bant_iki.py`): F10d § 11.5 ile aynı yöntem (`rehber_giris.Giris.carpisma`,
  ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, temas sayılmaz), 2 mm adım. Engel = bandın kendi alt adımında yerinde olanlar
  (`rehber_sira.Denetim.durumlar`), bandın grubu (braket, cıvata) hariç. Engel başına ilk–son mm (yerinden çekme mesafesi).

### 2.2 Dikiş tablosu (dil hangi bantta)

| Dikiş | Dil (içte) | Dudak (dışta) | Ölçüm (dışta olanın satır sayısı / öbürü) |
|---|---|---|---|
| y 1005 sağ: orta bant sağ / göğüs bandı sağ | orta bant | göğüs bandı | ön 1477 / 0, arka 673 / 0, yan 2076 / 0 |
| y 1005 sol: orta bant sol / göğüs bandı sol | orta bant | göğüs bandı | ön 1360 / 0, arka 676 / 0, yan 2076 / 0 |
| y 1198 sağ: göğüs bandı sağ / omuz bandı sağ | göğüs bandı | omuz bandı | arka 734 / 0, yan 1449 / 0; önde 20 satırda göğüs dışta (köşede uç uca, z 66 ortak yüz; bindirme değil) |
| y 1198 sol: göğüs bandı sol / omuz bandı sol | göğüs bandı | omuz bandı | arka 734 / 0, yan 1449 / 0; önde 10 satır, sağdaki gibi |
| z +88 sağ: etek orta sağ / etek ön sağ | etek orta | etek ön | yan 2016 / 0, üst 336 / 0 |
| z +88 sol: etek orta sol / etek ön sol | etek orta | etek ön | yan 2016 / 0, üst 338 / 0 |
| çerçeve sağ / göğüs bandı sağ (ön yüz) | çerçeve (bandın arkasında) | göğüs bandı | üst üste gelen 1143 satırın hepsinde göğüs bandı önde |
| çerçeve sol / göğüs bandı sol | çerçeve | göğüs bandı | 1143 / 0 |

Sonuç: bant dikişlerinin hepsinde dil alttaki (etekte arkadaki, orta) bantta; takılan bandın kenarı dilin dışından geçer. Eski metin
("dilini orta / göğüs bandının arkasına sok") F1, F3, F4'te tersti. Çerçevede ise dil gerçekten çerçevede, cümle doğru.
Ölçülmeyen dikişler (metni değişmedi): F2 bant dikişleri (y 400 / 530 / 688 / 791,5; metinde dil cümlesi yok), etek arka z −88
(metinde dil cümlesi yok), x 0 dikişleri.

### 2.3 Yol ölçümü (engel: ilk–son mm, yerinden çekme yönünde)

| Bant | Yol | Engeller | Ayrıldı |
|---|---|---|---|
| Göğüs sağ | +x | orta bant sağ 2–160; ısıl gömme (y 1005 arka) 18–110 | 174 mm |
| Göğüs sağ | +y | orta bant sağ 2–12; dikiş ısıl gömmeleri 2–10, 2–8; y 1095 braket perçin somunu 2–14; **rulman kapağı 32–294, S1 horn / servo, yüz kabuğu, yüz ekranı …** | ayrılmadı (300 mm) |
| Göğüs sağ | +y 16 mm, sonra +x | iniş: orta bant 2–12, ısıl gömme / perçin somunu 2–14; yan yol serbest | 174 mm |
| Göğüs sol | −x | orta bant sol 2–136; ısıl gömme 18–86 | 162 mm |
| Göğüs sol | +y | orta bant sol 2–12, orta bant sağ 2–4, göğüs bandı sağ 2–18, ısıl gömmeler, perçin somunu 2–14; rulman kapağı 32–294 … | ayrılmadı |
| Göğüs sol | +y 16 / 24 mm, sonra −x | 16'da yan yolda göğüs bandı sağ 0–8, ısıl gömme (x 0) 0–6; 24'te yan yol serbest | 162 mm |
| Etek ön sağ | +z | perçin somunu (z +105 braket) 2–8; ~~şase uzun rayı sağ ve alt plaka 24–162~~ (düzeltme turu 1: B-rep bunu doğrulamadı, yalnız somun 2–8; § 13.3) | 182 mm |
| Etek ön sağ | (1, 0, 1) (çizilen uçuş) | sonar sağ 2,8–11,3; şase rayı 33,9–152,7; alt plaka 33,9–206,5 (yalnız mesh; ray / plaka kısmı B-rep ile denenmedi, § 13.3) | 229 mm |
| Etek ön sağ | +z 10 mm, sonra +x | perçin somunu 2–8; yan yol serbest | 236 mm |
| Etek ön sol | +z / +z 10 sonra −x | sağdaki gibi; iki parçalı yolun yan bacağı serbest | 182 / 224 mm |
| Omuz sağ | +x | rulman kapağı 2–98, göğüs bandı sağ 2–160, yuva cıvatası M6 4–28, ısıl gömmeler 18–106, 44–132 | 174 mm |
| Omuz sağ | +y | rulman kapağı 6–100, kapak cıvataları, omuz yuvası, S1, kafa kabukları … | ayrılmadı |
| Omuz sağ | +y 16, sonra +x | iniş: rulman kapağı 6–16; yan yol: rulman kapağı 0–4, kapak cıvatası 2–6 | 174 mm |
| Omuz sağ | +y 24, sonra +x | iniş: rulman kapağı 6–24, kapak cıvatası 18–24, omuz yuvası 22–24; yan: rulman kapağı 0–14, rulman dış bileziği 2–12 | 174 mm |
| Omuz sol | −x / +y / +y 16 sonra −x | sağın aynası (göğüs bandı sol 2–136) | 162 mm |
| Çerçeve sağ | +z | göğüs bandı sağ 2–10, göğüs ekranı 4–8, orta bant sağ 6 | 64 mm |

Seçilen yol (düzeltme turu 1 notu: "en az girişimli" denmişti; seçim engelin görüldüğü mm aralığına dayanıyor, girişimin hacmine ya
da derinliğine değil; yolun kolaylığı ölçülmedi, § 13.2): göğüs bantları ve omuz bantları için "dikişin 16 mm (göğüs solda 24 mm) üstünde yandan getir, sonra indir";
etek ön bantları için "yerinin 10 mm önünde yandan getir, sonra önden içeri it"; çerçeve için önden (+z). Hiçbiri tamamen serbest değil:
son milimetrelerde dil (göğüs), perçin somunu (etek ön) ve rulman kapağı (omuz) var; metin bunu söylüyor.

**F10d ile fark (kontrol ajanı baksın):** F10d § 11.5 etek ön bandı için "+z'de yalnız braket perçin somunu 1–7 mm, sonra serbest"
diyor. Bu ölçümde +z yolunda 24–162 mm'de şase uzun rayı ve alt plaka da çıktı. Engel kümesi aynı yöntemle (alt adım izin kümesi)
kuruldu; farkın nedeni incelenmedi (F10d'nin ilk çarpışmada durması ya da engel kümesi olabilir). Metin iki parçalı yolu yazdığı için
(+z yalnız 10 mm) bu fark metni etkilemiyor. **Düzeltme turu 1:** B-rep ölçümü (§ 13.3) F10d'yi doğruladı: +z'de yalnız perçin somunu
(1–8 mm), ray ve plaka ortak hacmi yok. Bu paragraftaki mesh sonucu geri çekildi.

### 2.4 Değişen rehber cümleleri (`rehber_metin.py`)

- **F1 ön sağ / ön sol bant (alt adım 3 / 5)**
  - eski: "Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir). Bu bantta engel dil değil,
    z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir."
  - yeni: "Dil orta bantta: bu bandın z +88 kenarı orta bandın dilinin dışından geçer (ölçüm). Bandı yerinin 10 mm önünde yandan (+x / −x)
    getir (bu yol serbest, ölçüm), sonra önden içeri (−z) it: bu son 10 mm'de engel dil değil, z +105 braketinin perçin somunu (2–8 mm,
    ölçüm); bandı hafifçe esneterek somunun üstünden geçir (K55 a, geçici). Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım
    yeniden yazılabilir."
- **F3 göğüs bandı sağ (alt adım 1)**
  - eski: "… Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir)."
  - yeni: "… Dil orta bantta. Bandı dikişin 16 mm üstünde yandan getir (bu yol serbest, ölçüm), sonra aşağı indir: son 12 mm'de bandı
    hafifçe esneterek alt kenarını orta bandın dilinin dışından geçir (K55 a, geçici; inişte dikişin ısıl gömmeleri ve y 1095 braketinin
    perçin somunu da kenara değer, 2–14 mm, ölçüm). Bu geçme kuponla denenmedi; …" ("+x'ten getir" başı kaldı.)
- **F3 göğüs bandı sol (alt adım 2):** aynısı, "24 mm üstünde (… 16 mm'de göğüs bandı sağa değer)", inişte x 0 dikişinde göğüs bandı
  sağın bindirmesi 2–18 mm.
- **F3 çerçeve (alt adım 5)**
  - eski: "… dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir)."
  - yeni: "… dilini göğüs bandının arkasına sok (K55 a, geçici; ölçüm: çerçeve kenarı göğüs bandının iç yüzünde). Bu geçme kuponla
    denenmedi; …"
- **F4 omuz bandı sağ / sol (alt adım 1 / 2)**
  - eski: "Bant düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı
    kuponunda denenir)."
  - yeni (sağ): "Bant düz bir yoldan girmiyor (ölçüm, Notlar). Dil göğüs bandında. Bandı dikişin 16 mm üstünde yandan (+x) getir, sonra
    aşağı indir: hafifçe esneterek alt kenarını göğüs bandının dilinin dışından geçir (K55 a, geçici). Bu yolda engel bant değil, Ø84
    rulman kapağı (yanal yolun son 4 mm'si ve inişte dikişin 16–6 mm üstü) ve kapak cıvataları (2–6 mm, ölçüm). Bu geçme kuponla
    denenmedi; …" Sol: "(−x)", "Engel sağdaki gibi rulman kapağı ve kapak cıvataları (ölçüm)."
- F3 yorum satırı güncellendi. **Uçuş çizimi (`ucus`) ve Notlar'daki giriş ölçümü metni (`ucus_ok`) değişmedi** (§ 8 karar 2).

Tam liste (eklenen 25, silinen 10 cümle, etiketli): `planlama/d158/F10l-birlesim.py` `P108B_EKLENEN` / `P108B_SILINEN`.

### 2.5 Denetim listeleri

- `rehber_denetim.py` `ZORUNLU`: F1 / F3 / F4 dil cümlesi ve yolu (sağ + sol, iki kez), F1 / F3 / F4 "kuponla denenmedi" notu (F3'te üç:
  iki bant + çerçeve). 6 satır.
- `YASAK`: "bant dili ters (K55)" (`Bant / Bandı … dilini <x> band… arkasına`; "Çerçeve" cümlesini tutmaz) ve "kuponda denenir
  iddiası (K55)". `YASAK_BOZMA`: 5 satır (eski F3, eski F4, çerçeve yakalanmamalı, iki kupon iddiası).
- `ASCII_TAMAM`: 7 kelime (dilinin, somunun, kuponla, sonucu, yerinin, kenara, yanal).
- `rehber_kritik_onay.json`: `--kritik-onay-yenile` iki kez (33 fark, sonra YASAK deseni genişleyince 1 fark). Farklar: F1 / F3 / F4
  alt adım metinleri, K2 kablo (D6), LISTE ZORUNLU 6, LISTE YASAK 2.
- `F10l-birlesim.py`: `BEKLENEN["1d7fb71"]`, varsayılan taban `1d7fb71`.

## 3. Görev 2: 180° ters ESP32 (`rehber_kablo.py`)

- Yeni `u06_yon_denetle(analiz, RM)`, `u06_port_denetle`'nin sonuna bağlı (`sema_geometri_denetle` RM'yi geçirir). FreeCAD'siz, iki
  bağımsız iz (`taban-analiz.json`, `taban_lib.esp_local`'dan):
  (a) taşma: micro USB portu kart kenarından 1 mm taşar → DevKit kutusu taşıyıcının merkezinden (x 80) port tarafına daha uzun
  (bugün +x 27 / −x 26 mm);
  (b) kütle: WROOM portun karşı ucunda → hacim merkezi kutu merkezinden WROOM tarafına kayar (bugün 77,09 < 80,5).
  İkisi ayrı yön derse HATA; eşik altıysa HATA ("okunamıyor"). +x = robota önden bakınca sağ.
- Rehber cümleleri: `micro USB (portu|fişini) … önden bakınca (sağ|sol)` model yönüyle aynı olmalı, `WROOM modülü (sağ|sol)da`
  karşı yönde; cümle sayısı 4 (B6a iş, B6a kontrol, F1 kontrol, K1 17.11). Azalırsa HATA.
- Bozma (3 yeni): b104 DevKit tam 180° (kutu 53…106, merkez aynalı) → 8 hata; b105 yalnız kütle izi ters (kutu aynı; F10u-kontrol'ün
  "kutu aynı kalır" durumu) → 1 hata; b106 B6a cümlesi "solda" → 2 hata. Not: F10u-kontrol § 7 "180° dönerse kutu aynı kalır" yalnız
  yaklaşık doğru: kutu 1 mm kayar ve eski +x yüz denetimi de (0,5 mm toleransla) yakalardı; yeni denetim yönü ayrıca ve metinle bağlar.

## 4. Görev 3: `--kaynak` CAD adları (`rehber_denetim.py`)

- Kök neden: `kaynak_denetle` ASCII denetimine CAD adlarını hiç sokmuyordu; `cad_ad_metinleri` (montaj-analiz.json) yalnız elektrik
  denetimine giriyordu. F10y'deki 9 sözcük `TR_EK`'ten çıkarılınca --kaynak 0 ASCII buluyordu.
- Yeni `cad_kaynak_metinleri()`: etiket / kod güncel kaynaktan, `rehber_gorunum.cad_parcalar()` (modül FCStd'lerinin Document.xml'i;
  FreeCAD istemez, 0,4 s; üretimin okuduğu dosyalar). "Kablo yolu N:" etiketleri atlanır (veride KABLO_AD adıyla görünür, o metin zaten
  denetimde). ASCII ve elektrik denetimine girer; okunamazsa None → denetim geçmez. Bugün 1216 metin, ASCII 0.
- `cad_ad_eskime` (bilgi): montaj-analiz.json'da olup kaynakta olmayan ad 0, kaynakta olup analizde olmayan 271 (analiz HARIC
  parçaları ve bazı kodları taşımıyor). Çıktıda bir satır.
- Bozma (4 yeni, `cad_kaynak_bozma_denemesi`): TR_EK'ten "saplamasi" çıkınca 1, "anahtarli" çıkınca 1, kaynağa ASCII etiketli yeni
  parça 2, FCStd okunamıyor 1.

## 5. Görev 4: kareler

Depo dışı önizleme: `rehber/` kopyası + `rehber_gorunum.isle(yazma=True)` (güncel `rehber_metin` alanları, uç etiketleri) + headless
Chrome `?adim=N.J&cekim=1&sahne=1&tema=light`, 1200 × 720 (yazdırma karesi). Görüntülere gözle bakıldı.

- **17.4** (yol 3 anahtarlı 3 → 2 → 1 → yıldız 1; yol 4 anahtarlı 2'den): eski (−0,85, 0,9, 0,5). Önden-üstten (0,35, 1, 0,7) bütün
  robotu gösterdi, saplamalar küçük kaldı. Seçilen: kamera (−0,35, 1, 0,7), odak röle + ön şarj kartı + anahtarlı bara tutucusu,
  gövde direği saydam. Karede anahtarlı baranın 4 saplaması ve turuncu yolların saplamalara gelişi seçiliyor; etiketler 1 röle K1,
  2 anahtarlı bara, 3 ön şarj kartı, 4 yıldız barası. Sigorta kutusu kadraj dışı → `UC_ORTULU[("K1", 4)]` "Sigorta kutusu": dışarıda.
  Hangi saplamanın 1, hangisinin 3 olduğu karede yazılı değil (sıra metinde); gözle "yol 3 baradan geçiyor" okunuyor, numara okunmuyor.
- **17.10** (yol 11 / 12 katı kesik dışından deliyor): eski (−0,6, 0,9, 0,5). Seçilen (0, 1, 0,45): saydam katın ön kesiği ve mor
  çizgilerin kesik dışından geçişi görülüyor; 8 etiketin 8'i karede.
- **32.1** (yol 5 / 7 anahtarlı 1'den): üç bakış denendi (önden-üstten tüm robot; taban odaklı; bara odaklı). Taban / bara odağında
  omuz uçları (etiket 2, 4) kadraj dışına düşüyor, tüm robot bakışında saplama seçilmiyor. **Değiştirilmedi** (sağ-arkadan bakış kaldı).
  Saplama ayrıntısı K1 17.5'in karesinde; kapanışta sahibine sorulacak.
- **17.11** (U06 çizilmiyor): neden rehber tarafında. U06'nın şeması K2'ye ait (32.4, `DEMET_ALT` K2 `sema=("(U06)",)`); app.js
  `semaDurum` kendi adımından önceki karede şemayı çizmez, her şema tek alt adımda. Uç etiketi (`uc_isle`) yalnız o alt adımda çizilen
  kabloları etiketliyordu. Düzeltme: `DEMET_ALT` K1 alt adım 11'e `etiket_kablo=("U06",)`; `rehber_gorunum.uc_isle` bu alandaki
  kimlikleri etiket kümesine ekler (kimlik kablo tablosunda ve alt adım metninde değilse SystemExit). Önizlemede 17.11'de "2 ESP32"
  etiketi DevKit'in üstünde; "USB hub" ucu "bu adımda takılı değil". Çizginin kendisi çizilmiyor (app.js'e adım ötesi şema özelliği
  gerekir; yapılmadı). Metin zaten "U06'nın şeması alt adım 32.4'ün karesinde" diyor.

## 6. Görev 5: D6 (`rehber_deger.py`, `rehber_metin.py` K2)

- Yeni yer tutucu `{boy.<kimlik>}` → `kablolar.json` `kablolar[<k>].boy.onerilen_mm`, binlik noktayla ("1.560"); bağlam kuralı
  kimlik (cümlede geçmeli). `boy` kaydı zaten `boy_tazelik` ile `lale158-kontrol.json`'a bağlı.
- K2 cümlesi: "HDMI (H02) {boy.H02}, hub uzatması (U03) {boy.U03}, ESP32 USB (U06) {boy.U06}, hoparlör (AU3) {boy.AU3}, göğüs 12 V
  (G21) {boy.G21} mm". Çözülmüş sayılar eskisiyle aynı (950, 920, 1.560, 1.030, 1.720); cümleye kimlikler eklendi.
- Bozma (3 yeni, `boy_bozma_denemesi`): kayıtta U06 1.360 → metin izler; kayıtta boy yok → çözülmez; cümleden U06 kimliği silinir →
  bağlam yakalar. `elektrik.md`'deki aynı sayılar bu pakette bağlanmadı (rehber dışı; § 9).

## 7. Komutlar ve çıkış kodları

Hepsi depo kökünden, `py -3 -B -X utf8`. Başlangıç (16:34) ve son.

| Komut | Başlangıç | Son |
|---|---|---|
| `tasarim/freecad/carpisma_kos.py kontrol` | 0, "izlenen 17 dosyanin ozetleri kayitla ayni" | 0, aynı |
| `rehber_denetim.py --kaynak` | 0 | 0 (ASCII 0, CAD kaynak 1216 metin) |
| `rehber_denetim.py --bozma-denemesi` | 0, 311 / 311 | 0, 323 / 323 (+5 yasak, +4 CAD kaynak, +3 boy) |
| `rehber_kablo.py` | 0, GEÇER | 0, GEÇER |
| `rehber_kablo.py --bozma-denemesi` | 0, 111 / 111 | 0, 114 / 114 |
| `planlama/adim3/kablolar_denetim.py` | 0, GEÇER | 0, GEÇER |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0, toplam 174 | 0, toplam 174 |
| `planlama/d158/F10l-birlesim.py` | 0, GECER (taban 896c9a7) | 0, GECER (taban 1d7fb71; eklenen 25, silinen 10) |
| `rehber_denetim.py --kritik-onay-yenile` | – | 0 (33 fark, sonra 1 fark) |

İlk son koşuda `rehber_denetim --bozma-denemesi` 322 / 323 verdi (çıkış 1): "kuponda bu bant ayrıca, somun takılıyken denenir"
virgül yüzünden yasak desenine girmedi. Desen `kupon… [^.;]{0,40} denenir` yapıldı, onay kaydı yenilendi, yeniden koşuldu (son satır).

## 8. Kararlar (Echo; geri alınabilir)

1. Dil cümlesi ölçüme göre düzeltildi (alttaki bandın dili; çerçeve dokunulmadı). Yol, modeldeki en az girişimli yol olarak
   yazıldı ve "bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir" notu yedi yere eklendi. "Baskı kuponunda
   denenir" ve "kuponda bu bant ayrıca denenir" iddiaları kalktı (kupon basılmadı; etek ön için kupon yok).
2. Uçuş çizimi (`ucus`) değişmedi: ±x (göğüs, omuz) ve (±1, 0, 1) (etek ön) çizimi iki parçalı yolun ana bacağına yakın; değiştirmek
   `rehber_sira` uçuş denetiminin (dize `ucus_ok` anahtarı, istisna_bos) tam üretimde yeniden geçmesini isterdi. Bir ara (0, 1, 0) /
   (0, 0, 1) yazıldı, ölçüm düz +y'nin kafaya girdiğini gösterince geri alındı.
3. P108a O1 (c)'deki "geçici metin +y" uygulanmadı: düz +y 32 mm'den sonra rulman kapağı, S1, yüz kabuğu ve ekranla çakışıyor.
4. 32.1 karesi değiştirilmedi (§ 5).
5. 17.11'de çizgi değil uç etiketi (app.js değişmedi).
6. D6'da cümleye kablo kimlikleri eklendi (bağlam denetimi için; kısa ve okura bilgi).

## 9. Yapılmayan / bakılmayan

- Tam üretim yok: yeni metin, 17.4 / 17.10 kamerası ve 17.11 etiketi `rehber/` çıktısında yok; `F10d-dogrula` U-sınamaları (U4 görünürlük)
  ve `rehber_sira` uçuş denetimi yeni veriyle koşmadı.
- `elektrik.md`'deki önerilen boylar kayda bağlanmadı (rehber dışı belge).
- Etek ön +z yolunda F10d ile ölçüm farkı (§ 2.3) incelenmedi.
- F2 ve etek arka dikişleri ölçülmedi (metinlerinde dil cümlesi yok).
- 32.1 için öneri yok; 17.4'te saplama numaraları karede yazılı değil.
- FreeCAD açılmadı: ölçümler `robot.glb` mesh'inden (FCStd'nin üretimle dışa aktarılmış hâli), FCStd'den doğrudan değil.

## 10. Kapanış tarifi (eskidi: güncel tarif § 15)

1. `carpisma_kos.py kontrol` (0, "kayitla ayni").
2. Kaynak sınamaları: `rehber_denetim --kaynak` 0; `rehber_kablo` 0; `kablolar_denetim` 0; `F10l-birlesim` GECER (taban 1d7fb71);
   bozmalar: denetim 323 / 323, kablo 114 / 114, kablolar 174.
3. Tam üretim `rehber_uret.py` (≈ 41 dk, arka planda, `.durum`): beklenen GEÇER. Özellikle bak: `rehber_sira` uçuş satırı istisna_bos 0
   (F1 / F3 / F4 `ucus_ok` metinleri değişmedi, anahtarlar aynı); uç etiketi sayısı bir artar (17.11'de ESP32); kritik onay farkı 0.
4. `F10d-dogrula.py` (U1–U6): 17.4'te "Sigorta kutusu" UC_ORTULU kaydı kullanılıyor olmalı (U6); 17.11 ESP32 etiketi karede (U4).
5. Kareler gözle: 17.4 (anahtarlı baranın 4 saplaması ve yol 3 / yol 4 turuncu çizgileri), 17.10 (mor çizgilerin kesik dışından geçişi),
   17.11 (ESP32 etiketi), 35.1 / 35.2 / 33.3 / 33.5 / 36.1 / 36.2 / 35.5 metinleri (paneldeki K55 cümleleri).
6. Commit, push.

## 11. Kontrol ajanı için riskli yerler

- § 2.2 ölçüm yöntemi: dil yönü "dış yüzün hangisi dışta" sayımıyla; y 1198 ön yüzdeki 20 / 10 satır yorumum (köşede uç uca).
- § 2.3: iki parçalı yolun "serbest" sonucu 2 mm adımla; yükseklik 16 / 24 mm iki değer denendi, en küçük değer aranmadı. Etek ön +z'deki
  F10d farkı.
- Yeni metin uzun; özellikle F3 göğüs sol cümlesi. Kısaltılabilir.
- `u06_yon_denetle` eşikleri (0,4 / 0,5 mm) ve "taşma" izinin taşıyıcı merkezine dayanması (taşıyıcı kayarsa iz değişir; o durumda
  zaten başka denetimler de kırılır).
- `cad_kaynak_metinleri` CAD etiketlerini `RM.tr` ile çevirir; veri üretimi (`rehber_veri`) aynı çeviriyi mi kullanıyor, tek tek
  karşılaştırılmadı (prototipte 1216 metin, ASCII 0).
- `ZORUNLU` K55 desenleri `[\s\S]*` ile iki / üç tekrar arar (adım metni kısa, süre sorunu görülmedi).
- 17.4 kamerası: bara saplamalarının numarası karede okunmuyor; "okunurluk" yarım.

## 12. Önerilen kayıt

**Plan (`dongu-158.md` P10.8 hücresi), dikey çizgisiz:** "P10.8b (19.11, `P108b-gunluk.md`): K55 bant metni ölçümden (dil alttaki
bantta; yol yandan getir + indir, kuponla denenmedi notu), ESP32 180° yön denetimi, --kaynak CAD adlarını FCStd'den görür, 17.4 / 17.10
kamera ve 17.11 U06 uç etiketi, D6 {boy.<kimlik>}. Kaynak sınamaları geçti; tam üretim ve kontrol kapanışta."

**Kuyruk ("Karar değil, iş"):**
- K55: "Dil cümlesi düzeltildi, yol iki parçalı yazıldı (P108b § 2). Kupon sonucu gelince F1 / F3 / F4 metni yeniden yazılır (README K55
  karar ağacı). Etek ön için kupon yok (P108a O2)."
- F10u-kontrol § 7 (ESP32 180°): "Kapandı: `u06_yon_denetle` (P108b § 3)."
- F10y --kaynak: "Kapandı (P108b § 4)."
- 17.4 / 17.10 / 17.11: "Kaynakta yapıldı; kapanış üretiminde gözle bakılacak. 32.1 açık (P108b § 5)."
- D6: "Rehber tarafı kapandı (P108b § 6); `elektrik.md` açık."
- ~~Yeni: "Etek ön +z yolunda F10d § 11.5 ile ölçüm farkı … incelenecek."~~ Düzeltme turu 1: gerek kalmadı, B-rep F10d'yi
  doğruladı (§ 13.3). Güncel önerilen kayıt § 13.8.

## 13. Düzeltme turu 1 (kontrol: `P108b-kontrol.md`, DÜZELTMEYLE GEÇER)

Aynı kısıtlar: commit / push / `git add` yok, tam üretim yok, izlenen 17 dosyaya ve montaj betiklerine dokunulmadı, `dongu-158.md`,
`karar-kuyrugu.md`, `sonuc-rapor.html` ve demo değişmedi. Kararlar Echo kararıdır, geri alınabilir.

### 13.1 Bulgu → yapılan

| Bulgu | Yapılan |
|---|---|
| O1 göğüs inişi "hafifçe" değil | F3 alt adım 1 / 2: "hafifçe" kalktı; sıkı geçme sayılarla, sonucu kupon belirler, oturmazsa zorlama, kupon ya da K55 b beklenir |
| O2 omuzda ölçülmeyen dil engeli | F4 alt adım 1 / 2: esnet + dilin dışından geçir kalktı; dil engel değil (kesit dik); engel rulman kapağı ve kapak cıvataları (B-rep) |
| O3 etek ön / F10d çelişkisi | B-rep ölçüldü: F10d doğru, bu günlüğün mesh sonucu yanlış (§ 13.3); `ucus_ok` değişmedi, § 2.3 düzeltildi |
| D1 etek ön "kupon sonucu gelince" | F1 notu "Bu geçme denenmedi; bu bant için kupon henüz yok." (omuz için de, § 13.6 karar 3) |
| D2 göğüs sol orta bant sağ | Eklendi: "orta bant sağ (1–4 mm)" |
| D3 YASAK dar | Özne şartı kalktı; "çerçeve" geçen cümle dışlanır; 6 yeni bozma (4 yakalanmalı, 2 yakalanmamalı) |
| D4 ESP32 taşma izi kırılgan | Kod değişmedi; `u06_yon_denetle` docstring'ine ve buraya bilinen sınır (§ 13.5) |
| D5 `cad_ad_eskime` yalnız bilgi | `analizde_eski > 0` artık HATA (`gecti` düşer); şu an 0. `kaynakta_yeni` 271 bilgi kalır. 1 yeni bozma |
| D5 malzeme adları `--kaynak`'ta yok | Yapılmadı; önerilen kayda eklendi (§ 13.8) |
| D6 17.4 saplama numarası | K1 alt adım 4'e numara kuralı cümlesi eklendi (alt adımda yoktu; B5a'da ve K1'in başka maddesinde vardı) |

### 13.2 Göğüs inişi (O1) ve "en az girişimli yol"

Sayılar kontrolün B-rep ölçümünden (orta bantla ortak hacim 1–12 mm, en çok 2.221 mm³ sağ / 2.083 mm³ sol) ve kupon diliminden
(`bant-kuponu.json` `inis.girisim_mm`: 10 mm kala önde 6,756 mm; ön-yan köşe 7,8 mm `P108a-kontrol.md` § 3.4). Bu turda göğüs yolu
yeniden ölçülmedi. Metinde "≈ 2.200" (sağ) ve "≈ 2.100" (sol) yuvarlak yazıldı. § 2.3'teki "en az girişimli yol" sözü düzeltildi: seçim
engelin hangi mm aralığında görüldüğüne dayanıyordu, girişimin hacmine ya da derinliğine değil; yolun kolaylığı ölçülmedi.

### 13.3 B-rep yol ölçümü (FreeCAD 1.1, bu tur)

Yöntem: `P108b-olcum/brep_liste.py` engel adaylarını FreeCAD'siz seçer (alt adımın izin kümesi, yol koridoru + 2 mm, glb kutusu);
`P108b-olcum/brep_yol.py` yalnız o nesneleri modül modül açıp kopyalar, belgeyi kapatır (m6_yukle yerleşimi), bandı (ve grubundaki ısıl
gömmeleri) yol boyunca öteler. Ölçüt ortak hacim > 1 mm³ (kontrolle aynı); kalk bacağı 1 mm, çık bacağı 2 mm adım; dinlenmede ortak
hacim 0 (dört vakada da). Tek FreeCAD süreci, sırayla dört koşu (184–318 s), boş bellek 2,5–2,8 GB, tarayıcı açık değil. Kaynak
FCStd'ler kaydedilmedi (md5 öncesi / sonrası aynı, `git status`'ta yok). Sonuç: `P108b-olcum/brep-yol.json`.

| Bant, yol | B-rep (bu tur) | Önceki mesh (§ 2.3) | Fark |
|---|---|---|---|
| Etek ön sağ, düz +z (0–200 mm) | yalnız perçin somunu (z +105 braket) 2–8 mm, en çok 8,9 mm³; ray / plaka / sonar yok | somun 2–8; şase uzun rayı ve alt plaka 24–162 | mesh'in ray / plaka bulgusu yanlış; F10d § 11.5 doğru |
| Etek ön sağ, +z 10 sonra +x (240 mm) | kalkışta somun 1–8 mm (9,4 mm³); yan bacak serbest | somun 2–8; yan bacak serbest | aynı |
| Etek ön sol, düz +z | somun 2–8 mm, 8,9 mm³ | sağdaki gibi (ray / plaka) | mesh yanlış |
| Etek ön sol, +z 10 sonra −x | somun 1–8 mm; yan bacak serbest | yan bacak serbest | aynı |
| Omuz sağ, +y 16 sonra +x (180 mm) | kalkışta rulman kapağı 7–16 mm (en çok 303 mm³); yan bacakta rulman kapağı 2–4 mm (182 mm³), kapak cıvatası M3×12 2–6 mm (2,5 mm³); bant engeli yok | rulman kapağı 6–16, 0–4; kapak cıvatası 2–6 | aynı (1 mm sınır farkı) |
| Omuz sağ, +y 24 sonra +x | rulman kapağı 7–24 (1.951 mm³), kapak cıvatası 18–24, omuz yuvası 22–24; yan: rulman kapağı 2–14 (1.586 mm³), rulman dış bileziği 2–12, kapak cıvatası 2–6 | aynı küme | aynı; 24 mm daha kötü |
| Omuz sol, +y 16 sonra −x | sağın aynısı (303 / 182 / 2,5 mm³) | "sağın aynası" (ölçülmemişti) | ilk kez ölçüldü |
| Omuz sol, +y 24 sonra −x | sağın aynısı | – | – |

`ayrildi_mm` boş: FreeCAD BoundBox'u eğri bantlarda gevşek (etek ön bandının kutusu x −245…260), bu yüzden yollar sonuna kadar tarandı.
Mesh'in etek ön +z'de ray / plaka bulmasının nedeni incelenmedi (B-rep'te ortak hacim yok; eşik 1 mm³).

Ölçülmeyenler: göğüs sol yanal L=16 (metin artık yalnız 24 diyor, "16 mm'de değer" yan cümlesi çıkarıldı; 24 kontrolde B-rep ile
serbest), (1, 0, 1) çizim yönünün ray / plaka kısmı (yalnız mesh), F2 ve etek arka dikişleri.

### 13.4 Değişen cümleler (eski → yeni, kısa)

- **F3 sağ / sol:** "son 12 mm'de bandı hafifçe esneterek alt kenarını orta bandın dilinin dışından geçir (K55 a …)" → "İnişin son 12
  mm'sinde bandın alt kenarı orta bandın dilinin dışından geçmeli; modelde bu geçme sıkı: ortak hacim 1–12 mm, en çok ≈ 2.200 / 2.100 mm³;
  10 mm kala radyal girişim önde 6,8 mm, ön-yan köşede 7,8 mm. Ön yüz eğik, arka yüz dik: tek bir itiş ikisini birlikte kurtarmaz.
  Bandın esneyip yerine oturup oturmayacağı bilinmiyor; buna kupon karar verir (K55 a, geçici). Oturmazsa zorlama (bant kırılabilir):
  kupon sonucunu ya da tasarım değişikliğini (K55 b) bekle." Sol yanal yol: "(bu yol serbest; 16 mm'de göğüs bandı sağa değer)" →
  "(bu yol serbest)". Sol iniş engellerine "orta bant sağ (1–4 mm)" ve "braketin perçin somunu" eklendi. Sağ gömme / somun 2–14 → 1–14.
- **F4 sağ / sol:** "Dil göğüs bandında. … indir: hafifçe esneterek alt kenarını göğüs bandının dilinin dışından geçir" → "Dil göğüs
  bandında; (y 1198 dikişinde kesit dik,) düz inişte dil engel değil (ölçüm). … indir. Bu yolda engel bant değil, Ø84 rulman kapağı
  (yanal yolun son 4 mm'si ve inişte dikişin 16–7 mm üstü; ortak hacim en çok ≈ 300 mm³) ve kapak cıvataları (yanal yolun son 6 mm'si):
  bandın kenarı kapağın üstünden esnetilerek geçmeli (K55 a, geçici). Bandın esneyip geçeceği bilinmiyor; oturmazsa zorlama."
- **F1 sağ / sol ve F4 sağ / sol notu:** "Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir." → "Bu geçme
  denenmedi; bu bant için kupon henüz yok." F1 somun aralığı 2–8 → 1–8 mm (B-rep).
- **K1 alt adım 4 (17.4):** + "Saplama numaraları robota önden bakınca soldan sağa (B5a); karenin kamerası hafif soldan bakar,
  saplamaları önden bakışa göre say."
- Değişmeyen: F3 çerçeve cümlesi ve notu (kupon dilimi göğüs / orta dikişinin; çerçeve için "kuponla denenmedi" doğru), `ucus` ve
  `ucus_ok` (Notlar metni; B-rep F10d'yi doğruladı).

### 13.5 Denetim listeleri ve kod

- `ZORUNLU`: F3 deseni yeni sıkı geçme cümlesine (iki kez: "geçmeli; modelde bu geçme sıkı" … "buna kupon karar verir" … "Oturmazsa
  zorlama (bant kırılabilir)"); F4 deseni "düz inişte dil engel değil" + "rulman kapağı" + "kapağın üstünden esnetilerek geçmeli" +
  "oturmazsa zorlama" (iki kez); F1 ve F4 notu "Bu geçme denenmedi; bu bant için kupon henüz yok." (ikişer). F3 notu (üç) aynı.
- `YASAK` "bant dili ters (K55)": `^(?![^.;]*\bçerçeve)[^.;]*?\bdilini\b(?:\s+\w+){0,3}?\s+band\w*\s+arkasına`. `YASAK_BOZMA` +6:
  "Bandın dilini orta bandın arkasına sok", "Göğüs bandının dilini omuz bandının arkasına sok", "… dilini alttaki orta bandın arkasına
  sok", öznesiz "dilini göğüs bandının arkasına it" (yakalanır); "Çerçevenin dilini …" ve yeni F3 cümlesi (yakalanmaz).
- `ASCII_TAMAM` +10: say, kala, dilimi, ikisini, kurtarmaz, esneyip, oturup, oturmazsa, sonucunu, esnetilerek (hepsi doğru yazım).
  "B-rep" metinden çıkarıldı (yerine "ölçüm").
- `cad_ad_eskime`: `analizde_eski > 0` HATA (`kaynak_denetle.gecti`); `--kaynak` satırı "(HATA) 0 … (bilgi) 271". Bozma: FCStd'de bir
  parça yeniden adlanınca 1 HATA. `kaynakta_yeni` 271 bilgi. (Düzeltme turu 2: bu açıklama yanlıştı, doğrusu § 14.2.)
- **Bilinen sınır (D4, kod değişmedi):** `u06_yon_denetle` taşma izi 1 mm; DevKit taşıyıcıda dönmeden ≈ 0,6 mm kayarsa "okunamıyor" HATA
  verir (güvenli yanda yanlış alarm; ters kart kaçmaz). Kütle izi ≈ 3,4 mm, sağlam. Docstring'e yazıldı.
- `rehber_kritik_onay.json`: `--kritik-onay-yenile` bir kez (31 fark: F1 / F3 / F4 / K1.4 metinleri, LISTE ZORUNLU 5, LISTE YASAK 1).
- `F10l-birlesim.py` `P108B_EKLENEN` 25 → 37 (betiğin kendi çıktısından üretildi; etiketler "P10.8b K55 bant (ölçüm)", "P10.8b
  düzeltme turu 1 17.4 numara", "P10.8b D6 {boy.<kimlik>}"); `P108B_SILINEN` 10 aynı.
- Depoya eklenen: `P108b-olcum/brep_liste.py`, `brep_yol.py`, `brep-yol.json`.

### 13.6 Kararlar (Echo; geri alınabilir)

1. Etek ön için iki parçalı yol metinde kaldı (B-rep'te o da serbest). Düz +z de yalnız somuna değdiği için daha kısa bir yazım mümkün;
   paneldeki Notlar ("düz yol yok … +z'de yalnız braket perçin somunu") ile aynı kalsın diye değiştirilmedi.
2. Omuz metnindeki esnetme talimatı rulman kapağına bağlandı ve "hafifçe" kullanılmadı: kapakla ortak hacim ≈ 300 mm³, küçük değil.
3. F4 notu da "kupon henüz yok" yapıldı: bant kuponu göğüs / orta dikişinin dilimi; omuz ve rulman kapağı için kupon yok. Kontrol bunu
   yalnız F1 için yazmıştı; aynı yanlış beklenti F4'te de vardı.
4. `ucus_ok` (F10d kaydı) değişmedi: B-rep onu doğruladı. Uçuş denetimine etki yok.

### 13.7 Kapanış tarifi (eskidi: güncel tarif § 15)

(0) Bu tur bitti: F10l listeleri ve onay kaydı yenilendi, kaynak sınamaları koşuldu (§ 13.9). (1) `carpisma_kos.py kontrol` 0.
(2) Kaynak sınamaları ve bozmalar (§ 13.9 sayıları alt sınır). (3) Tam üretim `rehber_uret.py` (≈ 41 dk, arka planda, `.durum`); bak:
`rehber_sira` uçuş satırı istisna_bos 0 (`ucus` / `ucus_ok` değişmedi); uç etiketi bir artar (17.11 ESP32); kritik onay farkı 0.
(3b) Tam üretimden sonra `rehber_kablo` ve `rehber_denetim --kaynak` bir daha (uç etiketi onay kaydı, kablo bölümü). (4) `F10d-dogrula.py`
U1–U6: 17.10'da yeni kamerayla B01 / Q03 kadraj oranları değişir (eski 0,68 / 0,79), eşiğin altına düşerse kamera ya da kayıt; 17.4'te
odaklı kadraj "Sigorta kutusu" dışında bir ucu daha dışarıda bırakırsa `UC_ORTULU[("K1", 4)]` eksik kalır (önizlemede 17.4 4 etiket,
17.10 8). (5) `rehber/` çıktısında `git diff`: yalnız F1 / F3 / F4 / K1.4 / K1.10 / K1.11 / K2 değişmiş olmalı. (6) Kareler gözle
(17.4, 17.10, 17.11; 33.3 / 33.5 / 35.1 / 35.2 / 35.5 / 36.1 / 36.2 panel metni). (7) Bir sonraki turda `ucus_ok` metni değişirse
onay kaydı, F10l listeleri ve tam üretimde uçuş denetimi yeniden. (8) Push öncesi `.git/hooks/pre-push` kancası, sonra commit / push.

### 13.8 Önerilen kayıt (güncel; § 12'ye ek)

**Plan hücresi (dikey çizgisiz):** "P10.8b (19.11, `P108b-gunluk.md` § 13 dahil): K55 bant metni ölçümden; göğüs inişi sıkı geçme,
kuponla karara bağlanır, zorlanmaz; omuzda engel rulman kapağı; etek ön ve omuz yolları B-rep ile ölçüldü (F10d doğrulandı). ESP32 180°
yön denetimi, --kaynak CAD adları, 17.4 / 17.10 / 17.11, D6. Kaynak sınamaları geçti; tam üretim kapanışta."

**Kuyruk ("Karar değil, iş"):**
- K55: "Göğüs bandı inişi modelde sıkı (≈ 2.200 mm³, 10 mm kala önde 6,8 mm): kupon oturmazsa K55 b (tasarım). Omuz bandı rulman
  kapağına ≈ 300 mm³ değer, kupon yok. Etek ön engel yalnız perçin somunu, kupon yok (P108b § 13)."
- Yeni: "`--kaynak` CAD malzeme adlarını görmüyor (`cad_kaynak_metinleri` yalnız etiket / kod; üretimde `malzeme` de `tr()` ile görünür;
  P108b-kontrol D5)."
- Yeni (bilgi): "`u06_yon_denetle` taşma izi 1 mm; DevKit ≈ 0,6 mm kayarsa yanlış alarm (P108b § 13.5)."
- § 12'deki "Etek ön +z ölçüm farkı incelenecek" maddesi düşer (§ 13.3).

### 13.9 Komutlar ve çıkış kodları (bu tur, depo kökünden, `py -3 -B -X utf8`)

| Komut | Sonuç |
|---|---|
| `carpisma_kos.py kontrol` (başta ve sonda) | 0, "izlenen 17 dosyanin ozetleri kayitla ayni" |
| `rehber_denetim.py --kritik-onay-yenile` | 0, 31 fark |
| `rehber_denetim.py --kaynak` | 0 (ASCII 0, yasak 0, zorunlu eksik 0, onay farkı 0; CAD kaynak 1216; eskime HATA 0 / bilgi 271) |
| `rehber_denetim.py --bozma-denemesi` | 0, 330 / 330 (önce 323; +6 yasak, +1 CAD eskime) |
| `rehber_kablo.py` | 0, GEÇER |
| `rehber_kablo.py --bozma-denemesi` | 0, 114 / 114 |
| `planlama/adim3/kablolar_denetim.py` | 0, GEÇER |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0, toplam 174 |
| `planlama/d158/F10l-birlesim.py` | 0, GECER (taban 1d7fb71; eklenen 37 / 37, silinen 10 / 10) |
| FreeCAD B-rep (dört koşu, § 13.3) | log hatasız, `.durum` 0 |

İlk `--kaynak` koşusu çıkış 1 verdi (ASCII 12: yeni sözcükler ve "B-rep"); sözcükler `ASCII_TAMAM`'a eklendi, "B-rep" metinden çıktı.
İlk `F10l-birlesim` koşusu KALIR (30): liste eski cümleleri bekliyordu; liste betiğin çıktısından yenilendi.

## 14. Düzeltme turu 2 (kontrol: `P108b-kontrol.md` "Tur 1 kontrolü", GEÇER; üç düşük not)

Aynı kısıtlar (commit / push / `git add` yok, tam üretim yok, izlenen 17 dosya ve montaj betikleri dokunulmadı). Kararlar Echo
kararıdır, geri alınabilir.

### 14.1 T2 ve T3: rehber metni (`rehber_metin.py`)

- **T2, F3 çerçeve (alt adım 5):** "Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir." → "Bu geçme
  denenmedi; bu bant için kupon henüz yok." (koordinatörün verdiği cümle aynen; F1 / F4 ile aynı not). Göğüs bandı sağ / sol (alt adım
  1 / 2) "kuponla denenmedi; kupon sonucu gelince …" notunu korudu: bant kuponu tam bu dikişin (orta / göğüs) dilimi.
- **T3, tek kalıp "oturmazsa zorlama + ne beklenir":** beklenen şey kayıttan, uydurma koşul yok.
  - Kuponu olan dikiş (F3 göğüs bandı sağ / sol, değişmedi): "Oturmazsa zorlama (bant kırılabilir): kupon sonucunu ya da tasarım
    değişikliğini (K55 b) bekle."
  - Kuponu olmayan dikiş (F1 etek ön sağ / sol, F3 çerçeve, F4 omuz sağ / sol; yeni ya da düzeltildi): "Oturmazsa zorlama (bant / çerçeve
    kırılabilir): tasarım kararını (K55 b) bekle." Kayıt: `karar-kuyrugu.md` K55 seçenek b ("Geometri: dilde pah ya da ön / arka yarıda
    ters bindirme"; "b sonraki geometri paketinde"). Etek ön kuponu kuyrukta yalnız "yeni tasarım işi" önerisi (K55 notu O2); metne
    bekleme koşulu olarak yazılmadı.
  - F1'de cümle yoktu, eklendi (somun girişimi küçük, 9 mm³, ama kalıp eşit olsun). F4 sağda "…; oturmazsa zorlama." ve F4 solda
    "(K55 a, geçici); oturmazsa zorlama." yerine aynı tam cümle.
- `ZORUNLU`: F1 ve F4 not desenleri "Oturmazsa zorlama (bant kırılabilir): tasarım kararını (K55 b) bekle. Bu geçme denenmedi; bu bant
  için kupon henüz yok." (ikişer); F4 yol deseninin sonu aynı cümleye; F3 "kuponla denenmedi" deseni 3 → 2 (göğüs bantları) ve yeni F3
  çerçeve deseni ("Oturmazsa zorlama (çerçeve kırılabilir) … kupon henüz yok."). `YASAK` değişmedi. Yeni ASCII sözcük yok.
- Göğüs sağ "1–14 mm" (kontrolün B-rep'i 1–13 buldu, "önemsiz") değiştirilmedi.

### 14.2 T1: `cad_kaynak_metinleri` üretimin adını kullanır (`rehber_denetim.py`)

- Değişiklik: etiket `R.kopya_eki_sil(etiket, kod)`'dan geçer, sonra `R.tr` (üretim `rehber_veri.py` 394 / 788 / 847 ile aynı fonksiyon,
  kopyalanmadı). Kod alanı değişmedi.
- Sayılar: `--kaynak` CAD kaynak metni **1216 → 955**; `kaynakta_yeni` (bilgi) **271 → 10**; `analizde_eski` (HATA) 0.
- Tur 1'deki açıklama ("montaj-analiz HARIC parçaları ve bazı kodları taşımaz") yanlıştı. 271'in 269'u FreeCAD'in kopya eki ("…001")
  olan etiketlerdi; `cad_kaynak_metinleri` eki silmiyordu, üretim siliyor.
- Kalan 10 farkın nedeni (tek tek bakıldı):
  - 2 "(gösterim)" etiketi: "(gösterim)" ve "Ana anahtar düğmesi (gösterim, kabuk deliği gerekir)". `montaj-analiz.json`'da bu adlar yok.
  - 8 etiket, FreeCAD'in sondaki sayıyı artırmasından: "Çerçeve cıvatası M3x6 ISO 7381" … "ISO 7387" (7) ve "Yaka cıvatası M3x6 ISO
    7381" (1). FreeCAD aynı etiketi ikinci kez alınca "ISO 7380"in sonundaki sayıyı artırmış; `kopya_eki_sil` yalnız "0NN" ekini tanır.
    `montaj-analiz.json`'da bu parçaların adı doğru "… ISO 7380".
- **Yeni bulgu (düzeltilmedi, kapsam dışı):** üretim de aynı yanlış adı gösteriyor. Bugünkü `rehber/veri/rehber-veri.json`'da "Çerçeve
  cıvatası M3x6 ISO 7381 … 7387" ve "Yaka cıvatası M3x6 ISO 7381" (2) geçiyor: okur ISO 7380 yerine var olmayan standart numaraları
  görüyor. Düzeltme yeri CAD etiketi ya da `kopya_eki_sil`; CAD dosyalarına ve izlenen 17 dosyaya yazmak bu paketin dışında, kuyruk
  önerisi § 15.8.
- `cad_ad_eskime` docstring'i ve `kaynak_denetle`'deki yorum bu nedenle düzeltildi. Bozma "parça yeniden adlandı" ve "yeni ASCII etiketli
  parça" hâlâ yakalanıyor (330 / 330).

### 14.3 Listeler, onay, koşular (depo kökünden, `py -3 -B -X utf8`)

| Komut | Çıkış | Sonuç |
|---|---|---|
| `tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile` | 0 | 13 fark (F1 / F3 çerçeve / F4 metni, LISTE ZORUNLU 4 değişti + 1 eklendi); kayıt kablo 220, liste 257, metin 1199 |
| `planlama/d158/F10l-birlesim.py` (liste betiğin kendi çıktısından yenilendi) | 0 | GECER; eklenen **42** / 42, silinen 10 / 10 |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0 | ASCII 0, zorunlu eksik 0, yasak 0, onay farkı 0; CAD kaynak **955**; eskime HATA 0 / bilgi **10** |
| `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0 | **330 / 330** |
| `tasarim/freecad/rehber/rehber_kablo.py` | 0 | GEÇER |
| `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi` | 0 | **114 / 114** |
| `planlama/adim3/kablolar_denetim.py` | 0 | GEÇER |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0 | toplam **174** |
| `tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |

Kanca kalıpları (`.git/hooks/pre-push`'un `ara` satırları) değişen 7 dosyanın eklenen satırlarına ve yeni dosyalara: 0. `git status`
29 satır (19 eski kir, 7 değişmiş, 3 izlenmeyen: bu günlük, `P108b-kontrol.md`, `P108b-olcum/`).

## 15. Kapanış tarifi (güncel, tek başına okunur; § 10 ve § 13.7'nin yerine)

Kapanışı yapacak ajan için. Bu bölüm ve § 14.3'ün sayıları yeter. Başka bölüm gerekirse yeri yazılı.

### 15.1 Kurallar

- Bütün komutlar **depo kökünden** (`Robot/`) koşulur. Python `py -3 -B -X utf8` (tam üretimde F10y gibi `py -3 -X utf8`). Bash'te
  `PYTHONIOENCODING=utf-8`.
- **Uzun koşu kalıbı:** arka planda koş, çıktı ve çıkış kodu depo dışına. `$DIS` geçici bir depo dışı dizin olsun:
  `py -3 -X utf8 <betik> <argümanlar> > "$DIS/<ad>.log" 2>&1 < /dev/null; echo $? > "$DIS/<ad>.durum"`.
  Ön planda en çok 170 s yokla (`.durum` var mı). `Start-Process` kullanma. Çıkış kodunu `.durum`'dan, sonucu logdan oku: `freecadcmd`
  hata olsa da 0 dönebilir.
- **FreeCAD:** aynı anda tek süreç. Tam üretim FreeCAD'i kendisi açar ve `planlama/d158/FREECAD-KILIT.txt`'i (git dışı) doldurur;
  başlamadan önce kilit "boş" olmalı. Boş bellek ≥ 2,5 GB olmalı, tarayıcı açık kalmasın.
- **Yasaklar:**
  - `regresyon.py`'yi argümansız koşma; zincir 10'da `--yazma` ile koşulur.
  - Montaj betiklerini (`kafa_montaj`, `taban_montaj`, ana montaj) koşma.
  - İzlenen 17 dosyaya (`carpisma.py`'nin listesi) yazma.
  - Commit'e girmeyecekler: 19 eski kir (`tasarim/freecad/kabuk/gorsel/*.png` 13, `tasarim/freecad/montaj/yerlesim-kontrol.json`,
    kökteki `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`), `planlama/maliyet.json`,
    `tubitak-2209b/`, kilit dosyası.

### 15.2 Ön sınama (tam üretimden önce)

| # | Komut | Beklenen (alt sınır) |
|---|---|---|
| 0a | `tasarim/freecad/carpisma_kos.py kontrol` | 0; "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 0b | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0; ASCII 0, zorunlu eksik 0, yasak 0, onay farkı 0 (kablo 220, liste 257, metin 1199), CAD kaynak 955, eskime HATA 0 / bilgi 10 |
| 0c | `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0; ≥ 330 / 330 |
| 0d | `tasarim/freecad/rehber/rehber_kablo.py` ve `--bozma-denemesi` | 0 / GEÇER; ≥ 114 / 114 |
| 0e | `planlama/adim3/kablolar_denetim.py` ve `--bozma-denemesi` | 0 / GEÇER; toplam ≥ 174 |
| 0f | `planlama/d158/F10l-birlesim.py` | 0; GECER (taban `1d7fb71`, eklenen 42, silinen 10) |

### 15.3 Tam üretim

`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py`, arka planda, `.durum` kalıbıyla. Yaklaşık 41 dk sürer (F10y: 2436 / 2444 s).
Beklenen son satır "BITTI cikis 0" ve "ek kontrol sorunlu: -". F10y'nin ikinci üretimine göre karşılaştır (`F10y-gunluk.md` § 6):
- **veri:** 1238 parça.
- **görünüm:** alt adım 91 / 91; uç etiketi hata 0. Sayı 58'den bir artabilir (17.11'e ESP32 / U06 etiketi eklendi). Önizleme 58 saydı,
  kesin değil.
- **yazdır:** taşan sayfa 0. Sayfa sayısı 87'den ± değişebilir (metin uzadı). Kare piksel denetimi tam.
- **denetim:** ASCII 0, zorunlu eksik 0, yasak 0, elektrik iddiası 0.
- **sıra:** giriş yolu girilemez 0, sınama geçti; uçuş yolu çarpışan 0. `istisna_bos` 0 beklenir: `ucus` / `ucus_ok` bu pakette değişmedi.
- **onay farkı:** 0.
- **tarayıcı:** 50 / 50, konsol 0.

Çıkış 0 değilse logda "ek kontrol sorunlu" bölümüne bak; § 15.6'daki tabloya göre davran, gerekmeyen düzeltme yapma.

### 15.4 Zincir 2–10 (F10y § 8 sırası; tam üretimden sonra)

| # | Komut | Beklenen |
|---|---|---|
| 2a | `tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0, SONUÇ GEÇER; şema geometrisi hata 0 |
| 2b | `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi --veri rehber/veri/rehber-veri.json` | 0; F10y 129 / 129 idi. Bu paket kaynak bozmasına 3 ekledi (b104–b106); veri kipinde ≥ 129, hepsi yakalanmış |
| 2c | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` (bir daha, üretim verisiyle) | 0; onay farkı 0 (uç etiketi ve kablo bölümü) |
| 3 | `tasarim/freecad/rehber/rehber_denetim.py` (veri) | 0; ASCII 0, zorunlu eksik 0, yasak 0, elektrik iddiası 0 |
| 4 | `planlama/d158/F10f-dogrula.py` | 0, GECTI (≈ 550 s) |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | 0, GECTI (≈ 920 s); `renk_demo` KALDI bilinen (karar) |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` | 0, GECTI (≈ 960 s); uç etiketi hata 0, 360 px taşma 0; U4–U6 hata 0 (§ 15.6) |
| 6g | `planlama/d158/F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | bilgi satırı (geçme şartı değil). Girdi `kontrol.json`, `F10d-gizli-piksel.json` değil |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | 0, GECTI; dış istek 0, konsol 0, mini 50 / 50 |
| 8 | `planlama/d158/F9b-dogrula.py` | 0, GECER (hata 0). Kuyruk ya da plan değiştiyse önce § 15.7'nin demo adımı |
| 9 | `tasarim/freecad/carpisma_kos.py kontrol` | 0, kayıtla aynı |
| 10 | `planlama/d158/regresyon.py --yazma` | 0, GEÇER, kötüleşen yok |

### 15.5 Gözle bakılacak kareler ve panel metinleri

- **17.4:**
  - Röle, anahtarlı bara (4 saplama) ve yıldız barası saplamaları seçilebiliyor; kare 1–4 etiket. Sigorta kutusu kadraj dışında
    (`UC_ORTULU`).
  - Panelde yeni cümle: "Saplama numaraları robota önden bakınca soldan sağa (B5a) …".
- **17.10:** önden-üstten bakış; 8 etiketin 8'i karede. Sonar 8'in mor çizgisinin sonara ulaşmadan bitmesi eskiden beri böyle, bu
  paketten değil.
- **17.11:** "2" etiketi ESP32 kartının üstünde, çizgi yok.
- **Panel metinleri** (`rehber/` sayfasında, adım numarasıyla):
  - F1: 33.3 / 33.5. "Dil orta bantta …", "… Oturmazsa zorlama (bant kırılabilir): tasarım kararını (K55 b) bekle. Bu geçme denenmedi;
    bu bant için kupon henüz yok."
  - F3: 35.1 / 35.2 (sıkı geçme cümlesi, "kupon sonucunu ya da … (K55 b) bekle") ve 35.5 (çerçeve, "kupon henüz yok").
  - F4: 36.1 / 36.2 ("düz inişte dil engel değil", rulman kapağı, K55 b).
  - K1.4 (17.4) yeni numara cümlesi.
  - K2: "Önerilen boylar" sayıları HEAD ile aynı: 950, 920, 1.560, 1.030, 1.720.

### 15.6 Kırmızıya düşebilecek yerler ve ne yapılacağı

| Yer | Belirti | Ne yap |
|---|---|---|
| 17.10 kadraj (F10d U4 ve görünürlük) | B01 / Q03'ün karedeki oranı düşer (eski 0,68 / 0,79) ve eşiğin altına iner | Kareye bak. Parça gerçekten görünmüyorsa iki yol var: K1 alt adım 10 kamerasını HEAD değerine döndür (`kamera=(-0.6, 0.9, 0.5)`; bu paket `(0.0, 1.0, 0.45)` yaptı) ya da `UC_ORTULU`'ya nedenli kayıt ekle. İkisinde de onay yenile + F10l + § 15.2, sonra tam üretimi yinele |
| 17.4 `UC_ORTULU` (F10d U4 / U6) | Odaklı kadraj "Sigorta kutusu"ndan başka bir ucu da dışarıda bırakır: U4 "karede görünmüyor". Ya da kayıt kullanılmaz: U6 | U4: kareye bak, `UC_ORTULU[("K1", 4)]`'e ucu nedeniyle ekle (`_ARKADA` / `_DISARIDA`). U6: kullanılmayan kaydı sil. Sonra onay yenile, § 15.2, tam üretim |
| Uçuş (`rehber_sira`) | `istisna_bos` > 0 | Beklenmiyor (`ucus_ok` değişmedi). Çıkarsa hangi anahtar kullanılmadı, logdan oku; metni uydurma, koordinatöre bildir |
| ASCII (tam üretim denetimi) | Yeni CAD sözcüğü | Beklenmiyor (`--kaynak` artık üretimin adını görüyor, 955 metin). Çıkarsa doğru yazımsa `TR_EK` / `ASCII_TAMAM`'a, yazım hatasıysa koordinatöre |
| PDF | Taşan sayfa | Uzayan K55 cümleleri (35.1 / 35.2). Kısaltmadan önce koordinatöre bildir |
| F9b | Hata > 0 | Kuyruk / plan değiştiyse demo eski: § 15.7 sırası |

### 15.7 Plan ve kuyruk kayıtları (hazır metin) ve demo

Sıra: (1) plan hücresi, (2) kuyruk, (3) kuyruk değiştiği için demo yeniden üretimi `py -3 -B -X utf8 tasarim/cad/demo_uret.py` (demo
`karar-kuyrugu.md`'nin sha'sını gömer; F10y § 8), (4) `planlama/d158/F9b-dogrula.py` (0, hata 0). Demo `demo_uret.py` yalnız standart
kütüphaneyle koşar ve yalnız `tasarim/Robot-Tasarim-Demosu.html`'i yazar. Fark yalnız sayı ve sha olmalı.

**`planlama/dongu-158.md` P10.8 hücresi** (dikey çizgi yok):
"P10.8b (19.11, `planlama/d158/P108b-gunluk.md`, iki düzeltme turuyla): K55 bant metni ölçümden. Dil alttaki bantta. Göğüs inişi
modelde sıkı geçme, kupon karar verir. Omuzda engel rulman kapağı. Etek ön ve omuz yolları B-rep ile ölçüldü (F10d doğrulandı). Kuponu
olmayan dikişte oturmazsa zorlanmaz, tasarım kararı (K55 b) beklenir. ESP32 180° yön denetimi, --kaynak CAD adlarını üretimin adıyla
FCStd'den görür, 17.4 / 17.10 kamera ve 17.11 U06 uç etiketi, D6 {boy.<kimlik>}. Tam üretim ve zincir 2–10 geçti."
(Son cümleyi zincir gerçekten geçtiyse yaz.)

**`planlama/d158/karar-kuyrugu.md`:**
- **K55 bölümüne not:** "Not (P10.8b, 19.11.2026; `P108b-gunluk.md` § 2, § 13, § 14). Rehber metni ölçümden yazıldı.
  - Dil alttaki bantta; ters cümle kalktı.
  - Göğüs bandı inişi modelde sıkı geçme: ortak hacim ≈ 2.200 mm³; 10 mm kala önde 6,8 mm, ön-yan köşede 7,8 mm radyal girişim. Kupon
    karar verir; oturmazsa K55 b.
  - Omuz bandında dil engel değil; rulman kapağına ≈ 300 mm³ değer.
  - Etek ön bandında engel yalnız perçin somunu (B-rep 1–8 mm, ≈ 9 mm³; F10d § 11.5 doğrulandı).
  - Etek ön, omuz ve çerçeve için kupon yok; rehber 'oturmazsa zorlama, tasarım kararını (K55 b) bekle' diyor."
- **Yeni iş maddesi** (karar değil, iş):
  - "`--kaynak` CAD malzeme adlarını görmüyor (`cad_kaynak_metinleri` yalnız etiket / kod; P108b-kontrol D5)."
  - "Rehberde 'Çerçeve cıvatası M3x6 ISO 7381 … 7387' ve 'Yaka cıvatası M3x6 ISO 7381' görünüyor (FreeCAD etiketin sonundaki sayıyı
    artırmış; doğrusu ISO 7380). Düzeltme yeri CAD etiketi ya da `kopya_eki_sil` (P108b § 14.2)."
- **Kapandı notu:**
  - F10u-kontrol § 7 (ESP32 180°): "`u06_yon_denetle` (P108b § 3); bilinen sınır: taşma izi 1 mm, DevKit ≈ 0,6 mm kayarsa yanlış
    alarm."
  - F10y `--kaynak` CAD adları (P108b § 4, § 14.2).
  - D6 rehber tarafı (P108b § 6; `elektrik.md` açık).
  - 17.4 / 17.10 / 17.11 kaynakta yapıldı (32.1 açık).

### 15.8 Commit'e girecek dosyalar

Yol vererek ekle (`git add <yol>`). Eklemeden önce `git diff --cached --name-only`'yi § 15.1'in yasak listesiyle karşılaştır: kesişim
boş olmalı.
- **Kaynak (7):**
  - `tasarim/freecad/rehber/rehber_metin.py`
  - `rehber_denetim.py`
  - `rehber_kablo.py`
  - `rehber_deger.py`
  - `rehber_gorunum.py`
  - `rehber_kritik_onay.json`
  - `planlama/d158/F10l-birlesim.py`
- **Günlük ve ölçüm:**
  - `planlama/d158/P108b-gunluk.md`
  - `planlama/d158/P108b-kontrol.md`
  - `planlama/d158/P108b-olcum/` (7 dosya: `bant-olcum.json`, `bant_dil.py`, `bant_iki.py`, `bant_profil.py`, `brep_liste.py`,
    `brep_yol.py`, `brep-yol.json`)
- **Üretim çıktıları:** `rehber_uret.py`'nin yazdığı ve `git status`'ta görünen `rehber/` dosyaları (veri, kareler, PDF,
  `planlama/rehber/kontrol.json`) ve zincirin yazdığı JSON'lar (F10a / F10d / F10e / F10f, `F10d-gizli-piksel.json`; regresyon
  `--yazma` ile değişirse `regresyon.json` / `regresyon-son-kosu.json`).
- **Kayıtlar:** `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md`, demo yeniden üretildiyse `tasarim/Robot-Tasarim-Demosu.html`.
- **Push öncesi:** `.git/hooks/pre-push` kancası koşar (yerel yol, takma ad, e-posta, anahtar, IBAN / telefon, ekip adı). Bulgu çıkarsa
  push etme, satırı düzelt.

## 16. Kapanış (kapanış ajanı, 19.11.2026)

Tarif § 15'e göre. Bütün komutlar depo kökünden; loglar ve `.durum` dosyaları depo dışı geçici dizinde. Başlangıçta HEAD = uzak =
`1d7fb71`, `git status` 29 satır (19 eski kir, 7 değişen, 3 yeni yol), FreeCAD kilidi "boş".

### 16.1 Bellek eşiği (Echo kararı, geri alınabilir)

Ön sınamadan sonra boş fiziksel bellek 1,97 ve 1,91 GB ölçüldü (§ 15.1'in 2,5 GB şartının altında; kullanıcının tarayıcısı açık).
Kapanış ajanı tarayıcıya dokunmadı, üretime başlamadan durdu ve bildirdi. Koordinatörün kararı (18:47): 2,5 GB ön koşulu ölçülmüş bir
ihtiyaç değil, uygulama ajanının temkin notuydu; boş sanal bellek 17,7 GB, sayfa dosyasında 24,2 GB boş, FreeCAD bellek bulamayıp
düşmez, en kötü sayfalama yüzünden yavaşlar; üretim başlasın. Durma ölçütü: `freecadcmd` üretim bitmeden kaybolursa, logda bellek
hatası çıkarsa ya da CPU süresi 15 dk ilerlemezse dur. Hiçbiri olmadı.

**Ölçülen ihtiyaç (30 s'de bir yoklama, 84 ölçüm):**
- Üretim 18:48:15–19:30:05, **2.510 s** (F10y 2.436 / 2.444 s, 4,7 GB boşken).
- `freecadcmd` yalnız veri adımında (18:48–18:51, 168 s): çalışma kümesi tepe **460 MB**, CPU 151 s. Sonra süreç normal biter (üretimin
  geri kalanı FreeCAD'siz).
- `rehber_uret.py` Python süreci: sıra / giriş / uçuş denetimi sırasında çalışma kümesi ≈ **1,37 GB** (19:18 ve 19:20'de ölçüldü),
  CPU 1.503 s. Başsız Chrome (üretimin kendi tarayıcısı): tepe 643 MB.
- Boş fiziksel bellek en düşük **0,71 GB** (19:14:32, sıra denetimi sırasında); başlangıçta 1,69 GB. Hata, takılma yok.

### 16.2 Ön sınama (§ 15.2; `py -3 -B -X utf8`)

| # | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 0a | `tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |
| 0b | `rehber_denetim.py --kaynak` | 0 | ASCII 0, zorunlu eksik 0, yasak 0, onay farkı 0 (kablo 220, liste 257, metin 1199); CAD kaynak 955; eskime HATA 0 / bilgi 10 |
| 0c | `rehber_denetim.py --bozma-denemesi` | 0 | 330 / 330 |
| 0d | `rehber_kablo.py` ve `--bozma-denemesi` | 0 / 0 | GEÇER; 114 / 114 |
| 0e | `planlama/adim3/kablolar_denetim.py` ve `--bozma-denemesi` | 0 / 0 | GEÇER; toplam 174 |
| 0f | `planlama/d158/F10l-birlesim.py` | 0 | GECER; eklenen 42 / 42, silinen 10 / 10 |

### 16.3 Tam üretim (`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py`, FreeCAD veri adımlı): çıkış 0

| Bölüm | Sonuç |
|---|---|
| ön sınama | kaynak denetimi geçti, onay kaydı tutuyor (kablo 220, liste 257, metin 1199) |
| veri | 168 s; mesh 297 benzersiz / **1238 parça**, 50 adım. `robot.glb` / `robot-glb.js` HEAD ile aynı (geometri değişmedi) |
| görünüm | uç etiketi 24 konumda **58** etiket, karede görünmez 38; renk 1238 (CAD sırası eşleşir); alt adım **91 / 91** |
| yazdır | PDF **89 sayfa** (87'den; metin uzadı), taşan yok, en küçük yazı 8,1 pt, tamlık eksik 0; 141 kare piksel denetimi 141 / 141; telefon 360 px taşma 0 |
| denetim | ASCII 0, zorunlu uyarı eksik 0 / 164, yasak 0 (istisna 10), kopya eki 0, elektrik iddiası 0; parça 1238, şema 65 |
| sıra | 578 bağlantı, ulaşılamaz 0, sınama geçti; giriş yolu girilemez 0; uçuş yolu çarpışan 0, gerekçeli istisna 16, **istisna_bos 0**; ısıl gömme hata 0 |
| kol kablo / kablo eşleme | GEÇTİ / GEÇTİ |
| tarayıcı | 50 / 50, konsol hatası 0; **"ek kontrol sorunlu: -"** |

Uç etiketi sayısı 58'de kaldı (tarif "bir artabilir" demişti): 17.11'e "ESP32" eklendi, 17.4'te "Sigorta kutusu" kadraj dışına çıktı
(5 → 4 etiket, `UC_ORTULU` kaydı kullanıldı). Logda Traceback, "HATA", bellek hatası yok. Üretimden sonra kilit "boş".

**Değişen çıktılar (18 dosya):** `rehber/veri/rehber-veri.json` ve `.js`; `rehber/goruntu/adim-17-04 / 17-10 / 17-11.png`;
`planlama/rehber/goruntu/` 11 kare (17.4, 17.10, 17.11, 33.3, 33.5, 35.1, 35.2, 35.4, 35.5, 36.1, 36.2);
`planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/kontrol.json`.

**Veri farkı (`rehber-veri.json`, HEAD'e göre alan alan):** yalnız beklenen yerler. K1 alt adım 4 (kamera, odak, saydam, uçlar 5 → 4,
yeni numara cümlesi), alt adım 10 (kamera), alt adım 11 (uç "ESP32" eklendi, `uc_yok` "USB hub: bu adımda takılı değil"); K2 kablo
satırı (kimlikler eklendi, sayılar aynı: 950, 920, 1.560, 1.030, 1.720); F1 33.3 / 33.5, F3 35.1 / 35.2 / 35.5, F4 36.1 / 36.2 metinleri;
üretim tarihi ve iki süre / sayaç alanı. Başka adımda metin farkı yok.

**Kare farkı (piksel, > 24 gri düzeyi, HEAD'e göre):** 17.4 %53 / %33 (yazdırma / panelli), 17.10 %49 / %31, 17.11 %0,07 / %0,10 (yalnız
uç etiketi bölgesi); 33.x, 35.x, 36.x panelli karelerde %2,9–4,2 ve fark yalnız sağdaki panel bölgesinde (x ≥ 1019). 35.4 dosyası
değişti ama eşik üstü piksel farkı 0 (sahne yeniden çiziminden ufak gürültü); metni değişmedi.

### 16.4 Zincir 2–10 (`py -3 -B -X utf8`)

| # | Komut | Çıkış | Süre | Sonuç |
|---|---|---|---|---|
| 2a | `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | 2 s | SONUÇ GEÇER; kırpma kesimi hata 0; şema geometrisi 27, hata 0, istisnalı 4 |
| 2b | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 71 s | **132 / 132** yakalandı (F10y 129; +3 b104–b106) |
| 2c | `rehber_denetim.py --kaynak` | 0 | 1 s | onay farkı 0 (kablo 220, liste 257, metin 1199); CAD kaynak 955; eskime HATA 0 / bilgi 10 |
| 3 | `rehber_denetim.py` (veri) | 0 | 1 s | ASCII 0, zorunlu eksik 0 / 164, yasak 0, elektrik iddiası 0 |
| 4 | `planlama/d158/F10f-dogrula.py` | 0 | 564 s | GECTI |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | 0 | 964 s | GECTI; `renk_demo` KALDI bilinen (karar) |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` | 0 | 983 s | GECTI; uç etiketi 23 konum / 58, hata 0; 360 px taşma 0 |
| 6g | `planlama/d158/F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | 0 | 90 s | 103 / 116 parçanın alt adım karesinde pikseli var, 3'ü başka kamerada (bilgi; F10y ile aynı; `F10d-gizli-piksel.json` değişmedi) |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | 0 | 443 s | GECTI; dış istek 0, konsol 0, mini 50 / 50, 360 px taşma 0 |
| – | `tasarim/cad/demo_uret.py` (kuyruk değişti) | 0 | – | 127 sayı anahtarı, 6 karar, 163 maliyet kalemi, 1238 düğüm; fark yalnız gömülü `kaynak` bloğunda iki sha (`karar-kuyrugu.md`, `rehber-veri.json`); `git status` önce / sonra yalnız demo değişti |
| 8 | `planlama/d158/F9b-dogrula.py` (demodan sonra) | 0 | 5 s | GECER (hata 0) |
| 9 | `tasarim/freecad/carpisma_kos.py kontrol` | 0 | 1 s | izlenen 17 dosya kayıtla aynı |
| 10 | `planlama/d158/regresyon.py --yazma` | 0 | – | GEÇER, kötüleşen yok; `regresyon.json` / `regresyon-son-kosu.json` değişmedi |

**F10d görünürlük (bilgi, geçme şartı değil):** "KALDI (bilgi)" 23 → 25: 17.4 ve 17.10. Neden: odaklı kadrajda kablo yolunun bir ucu
kare dışında (`karede` false); yol görünür ve oranı eşiğin (0,2) çok üstünde: 17.4 yol 3 0,42 → 0,71; 17.10 yol 11 (Q03) 0,79 → 0,75,
yol 12 (B01) 0,58 → 0,54. § 15.6'daki kırmızı (oran eşiğin altına iner) olmadı; U4–U6 hata 0. 17.8 HEAD'de de aynı nedenle bilgi KALDI.

**Yeterlilik kanıtı (veriden):** 17.11 uçları "PCA9685", "ESP32"; 17.4 uçları röle K1 / anahtarlı bara / ön şarj kartı / yıldız barası,
`uc_yok` "Sigorta kutusu: bu kadrajın dışında"; 17.10'da 8 uç; uçuş `istisna_bos` 0; K2 önerilen boylar HEAD ile aynı sayılar;
"Çerçeve cıvatası M3x6 ISO 7381 … 7387" ve "Yaka cıvatası M3x6 ISO 7381" üretilmiş veride duruyor (bilinen bulgu, § 14.2; kuyrukta).

### 16.5 Gözle bakılanlar

- **17.4 (yazdırma karesi ve panelli kare):** etiketler 1 Röle K1, 2 Anahtarlı bara, 3 Ön şarj kartı, 4 Yıldız barası; anahtarlı
  baranın 4 saplaması ve yıldız barası saplamaları ayrı ayrı seçiliyor, turuncu yollar saplamalara geliyor; gövde direği saydam.
  Sigorta kutusu karede yok. Panelde yeni cümle ("Saplama numaraları robota önden bakınca soldan sağa (B5a); karenin kamerası hafif
  soldan bakar …") okunuyor. Hangi saplamanın kaç numara olduğu karede yazılı değil (metinde).
- **17.10:** önden-üstten; 8 etiketin 8'i karede (1 ESP32 … 8 sonar sol); mor yollar kat kesiği bölgesinden geçiyor.
- **17.11:** "2" etiketi ESP32 kartının üstünde, çizgi yok; "1" PCA9685.
- **Panel metinleri (panelli kareler):** 33.3 (F1 sağ: "Dil orta bantta …", "… tasarım kararını (K55 b) bekle. Bu geçme denenmedi; bu
  bant için kupon henüz yok."), 35.1 ve 35.2 (sıkı geçme cümlesi, ≈ 2.200 / 2.100 mm³, "kupon sonucunu ya da … (K55 b) bekle"),
  35.5 (çerçeve: "(çerçeve kırılabilir) … kupon henüz yok"), 36.1 ("düz inişte dil engel değil", rulman kapağı, K55 b). Taşma yok;
  metin panelde tam okunuyor. 35.5'te çerçevenin "hafifçe esneterek dilini göğüs bandının arkasına sok" cümlesi duruyor: § 13.4'e göre
  bilerek değişmedi.
- **PDF:** sayfa 24 (17.4, yeni cümle sonda), 64 (35.1 / 35.2), 67 (36.1 / 36.2): metin tam, kesik yok, kareler yerinde.
- **Bakılmayanlar:** 33.5 ve 36.2'nin panelli kareleri (metin veriden ve PDF'ten doğrulandı), PDF'te 33.x (s. 54–55), 35.5 (s. 65)
  ve K2 (s. 48) sayfaları (metin PDF'te bulundu, görüntüye bakılmadı), telefon kareleri, öbür adımlar (değişmedi). 32.1 bakılmadı.

### 16.6 Düzeltmeler

Rehber kaynağında ve üretimde düzeltme yapılmadı; hiçbir adım kırmızıya düşmedi, yineleme gerekmedi.

### 16.7 Plan ve kuyruk

- `planlama/dongu-158.md` § 3 P10.8 Durum hücresine P10.8b kaydı (dikey çizgisiz; satırın sütun ayırıcı sayısı HEAD ile aynı, 6),
  § 5'e günlük satırı. `sonuc-rapor.html` yeniden üretilmedi.
- `planlama/d158/karar-kuyrugu.md`: K55'e P10.8b notu; "Karar değil, iş" bölümünde kapanış notları (ESP32 180°, D6, 17.11 U06,
  `--kaynak` CAD adları, 17.4 / 17.10, K55 rehber metni) ve yeni blok "P10.8b rehber açıklarından" (32.1, 17.11 U06 çizgisi, ölçülmeyen
  yollar, malzeme adları, yön denetimi sınırı, `elektrik.md` boyları, yanlış ISO numarası). Karar maddelerinin durumu ve özet sayımı
  değişmedi.
- Demo yeniden üretildi, sonra F9b (§ 16.4).

### 16.8 Commit'e giren dosyalar (41)

- Kaynak (7): `tasarim/freecad/rehber/rehber_metin.py`, `rehber_denetim.py`, `rehber_kablo.py`, `rehber_deger.py`, `rehber_gorunum.py`,
  `rehber_kritik_onay.json`, `planlama/d158/F10l-birlesim.py`.
- Günlük, kontrol, ölçüm (9): bu günlük, `P108b-kontrol.md`, `P108b-olcum/` 7 dosya.
- Üretim çıktıları (18): § 16.3'teki liste.
- Zincir JSON'ları (4): `planlama/d158/F10a-dogrula.json`, `F10d-dogrula.json`, `F10e-dogrula.json`, `F10f-dogrula.json`.
- Kayıtlar (3): `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md`, `tasarim/Robot-Tasarim-Demosu.html`.

Girmeyenler: 19 eski kir, `planlama/maliyet.json`, `tubitak-2209b/`, kilit dosyası (hepsi dokunulmadı).
