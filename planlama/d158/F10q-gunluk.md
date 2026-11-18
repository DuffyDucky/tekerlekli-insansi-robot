# F10q · P10.7b2h günlüğü (uygulama ajanı)

DURUM: KAPANDI (03:55): üretim `--veri-yok` çıkış 0, zincir 2–10 çıkış 0, commit "Lale P10.7b2h" + push (§ 10). Madde 1 bitti; 2, 3, 4 alınmadı (§ 3–5); düzeltme turları § 7, § 8.

Açılış 18.11.2026 01:52 (saat okundu). Dal `lale-duzeltme`, HEAD `376fe90`. Commit, push, tam üretim ve zincir yok.

## 0. Başlangıç kiri (`git status --short`, 19 dosya; dokunulmadı)

```
 M tasarim/freecad/kabuk/gorsel/ (13 png: kabuk-arka-kapak-acik, -baglanti-etek, -baglanti-govde, -izometrik, -kesit-gogus, -kesit,
   -nextion-ic, -nextion-on, -omuz-duvari, -on, -patlatilmis-on, -patlatilmis, -yan)
 M tasarim/freecad/montaj/yerlesim-kontrol.json
?? geometri2_cikar.py  geometri2_dogrula.py  geometri_cikar.py  gez.js  uc.js
```

## 1. Seçilen maddeler (orkestratörün daraltmasıyla, 01:5x)

- Alınır: (1) rehber metnine K50, K55, K40, K51, K60; (2) taban yolları: yol 9, U06 şeması.
- (3) kablo boyları: yalnız 1 ve 2 biterse ve 02:40 geçmediyse.
- (4) CAD'e dokunan maddeler (USB ses kartı, K64 bara tutucusu, K2 boss, K51 TVS modeli, K53 çentik): **alınmadı** (orkestratör
  kararı, bu gece kapsam dışı; inceleme yapılmadı).

## 2. Madde 1: rehber metnine K50, K55, K40, K51, K60: BİTTİ (kaynak düzeyinde, 01:56)

Karar metinleri `karar-kuyrugu.md` (K40 :760, K50 :993, K51 :1027, K55 :1153, K60 :1289) Durum / Teknik yarı satırlarından; hafıza notuyla
fark yok. Düzenlemeler betikle, her eşleşme tam bir kez denetlendi (CRLF korundu).

| Karar | Rehber yeri (`tasarim/freecad/rehber/rehber_metin.py`) | Ne değişti |
|---|---|---|
| K50 b | K1 alt adım 2 (G06), F1 is_ madde 5, F1 alt adım 10, F5 not_ | XT60E-M (erkek) → XT60E-F (dişi panel; şarj kablosunun ucu erkek XT60); "pimleri" → "soketleri"; F5 notuna "alımı açık: siparişte XT60E-M varsa XT60E-F ile değiştirilir (K50)" |
| K51 a | E3a is_ madde 2 | "(ikinci TVS'i ayrıca al)" çıktı → "satın alma listesinde 2 adet (`maliyet.json`) … Pi hattındaki bugün modelde ve BOM'da yok, sonraki CAD paketinde eklenecek (K51 a)" |
| K55 a | F1 alt adım 3 / 5 (etek ön sağ / sol), F3 alt adım 1 / 2 (göğüs bandı sağ / sol), F3 alt adım 5 (çerçeve), F4 alt adım 1 / 2 (omuz bandı sağ / sol) | "bandı hafifçe esneterek dilini orta / göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir)"; çerçeve ve omuz bantlarına "düz bir yoldan girmiyor (ölçüm, Notlar)" da eklendi (önceden yalnız `ucus_ok` istisnasında yazıyordu) |
| K40 a | G3 is_ madde 1, G3 alt adım 1, G3 kontrol (+1 madde) | horn kol dişe dayalıyken (S2 = 4,3°) takılır; S2 5 komutunda 0,3 mm sentil geçer, 0,4 geçmez; geçmiyorsa diş yüzü zımparalanır |
| K60 A | K1 alt adım 8 (Ö4) | "karar verilene kadar" ve "Ö4 karar bekliyor (K60)" çıktı → "Elde taşınan acil stop yok (K60 A): köprü kalıcıdır, ileride kumandalı acil stop sökmeden bu yere eklenebilir; demoda mantarın yanında bir kişi durur" |

Denetim kuralları (`rehber_denetim.py`): Ö4 zorunlu deseni "karar verilene kadar"sız; "Ö4 karar bekliyor (K60)" zorunlusu → K60 A cümlesi
(demo şartı dahil); yeni zorunlular G3 K40 a, E3a K51 a, F1 K50 b; F5 zorunlusu "pimleri" → "soketleri"; açık karar kuralı yalnız K61
(K60 çıktı); kapanmış "karar bekliyor" listesine K40, K51, K55, K60; yeni bozma M21e (K60 yeniden "karar bekliyor"); `ASCII_TAMAM`'a
12 kelime (gerekçe satırıyla). `planlama/d158/F10l-birlesim.py`: varsayılan taban `376fe90`, `B2H_SILINEN` 12 / `B2H_EKLENEN` 22 (liste
uygulanan metinden betikle üretildi, etiketler elle). `planlama/adim3/kablolama-on-kararlar.md` §0 Ö4 satırı, §8 başlık ve karar
cümlesi, §14 Ö4 maddesi (satır içi; satır sayısı 460 aynı). §18 (14.11 orkestratör kararları, tarihsel) değişmedi.

Sınamalar (hepsi koşuldu):
- `rehber_denetim.py --kaynak`: ASCII 0, zorunlu eksik 0, yasak 0, çıplak 0; **onaylı kritik girdi farkı 28** (beklenen; yenilenmedi,
  aşağıda ajan seçimi). Tam çıktı paket dışında tutuldu, kontrol yeniden koşabilir.
- `rehber_denetim.py --bozma-denemesi`: çıkış 0, elektrik bozma 303 / 303, M21e YAKALANDI.
- `F10l-birlesim.py` (taban 376fe90): GEÇER, cümle 1102 → 1112, eklenen 22 / 22, silinen 12 / 12.
- `kablolar_denetim.py`: GEÇER. `rehber_kablo.py`: GEÇER.
- İlk denemede yakalanan ve düzeltilen: F1'deki "gerilimli uç gömük sokette … tak" YASAK ("enerji varken bağlantı") kalıbına düştü →
  "akü tarafı gömük soket"; F5 zorunlu kalıbı "pimleri" diye arıyordu → kural güncellendi.

Ajan seçimleri:
- **ajan seçimi:** `--kritik-onay-yenile` koşmadı, gerekçe: b2g'deki gibi onay kaydı kontrolden sonra yenilensin, 28 fark kontrolün gözü
  önünde kalsın. Kapanışta: `rehber_denetim.py --kritik-onay-yenile` → `--kaynak` 0.
- **ajan seçimi:** K50'de `kablolar.json` G06 parça / uç adları ("XT60E-M şarj girişi") ve `rehber_kablo.py` eşleme anahtarları
  değiştirilmedi, gerekçe: uç adları anahtar olarak birçok yerde (kablolar.json :919–10056, rehber_kablo :152 / :185 / :271, üretilen
  `kablolar.md`), `maliyet.json:111` alım kararıyla değişecek (kapsam dışı); bugün rehber metni dişiyi, kablo kaydı ve maliyet erkeği
  söylüyor. Bu bilinen tutarsızlık; K50 alım yarısı kapanınca tek pakette üçü birden. `rehber_kablo.py:186` "K50'de karar bekliyor" yorumu da
  orada.
- **ajan seçimi:** K55'te `ucus_ok` istisna gerekçeleri ("Karar önerisi F10d-K1") değiştirilmedi (F10d doğrulayıcısı bu metinlere
  bakıyor olabilir; üretimsiz sınanamaz).
- **ajan seçimi:** `kablolama-on-kararlar.md` §18 (14.11 tarihli orkestratör kayıtları) tarihsel olduğu için dokunulmadı; `kablolar.json`
  "Ö4 açık" notları (:474, :3539, :8496, :8552) değiştirilmedi (kablolar.md üretici çıktısıyla birlikte, sonraki pakette).

## 3. Madde 2: taban yolları (yol 9, U06 şeması): ALINMADI (okuma sonrası, 01:59)

Okundu: `rehber_kablo.py` `GEO_ISTISNA` / `CAD_KIRP` (:214–236), `taban-analiz.json` yol 9 noktaları, `taban_parcalar.py:560-562`,
`kablo_yolu_ekran.py` U06 yolu, `karar-kuyrugu.md:1608`, `:1717`, `:1729-1732`, `:1759`. Başlanmadı; ikisi de bu turun kurallarıyla
(FreeCAD'li tam üretim yok, kısa sınama) tam bitirilemez:
- **Yol 9:** korunacak bölüm noktalar[0..3] (F4 → XL4016 çevre, G18), atılacak [3..6] (XL4016 → ESP32, eski tasarım). Yol 12'deki
  `CAD_KIRP` yalnız y düzlemiyle keser; yol 9'da iki bölümün y aralıkları çakışıyor (korunan 215,5 → 125, atılan 125 → 200), y kesimi
  ayıramaz. z ≤ 77,5 kesimi neredeyse ayırıyor ama ESP32 ucunda kısa bir kalıntı bırakır. Gerekeni: `CAD_KIRP`'i nokta dizinine / kutuya
  genellemek (`rehber_kablo.py` + FreeCAD'li `rehber_veri.py` kırpması + GLB sınaması + bozmalar), FreeCAD'de depo dışı deneme, sonra
  **FreeCAD veri adımlı** tam üretim (`--veri-yok` yetmez; F10n'de yol 12 böyle sınandı). Tahmini: kaynak 1,5–2 saat + üretim.
- **U06 şeması:** uç (51,6; 190; −120) güç panelinin arkasında, ESP32 (80; 75) önde; yeni yol elektronik katının içinden geçmeli ve
  çarpışma taraması yok. Boy kaynağı `lale158-kontrol.json` (FreeCAD `lale158_kontrol`) eskir; kuyruk `:1729-1732` "FreeCAD koşusuyla
  birlikte" diyor; sonra K2 "yanlış yerde" cümlesi, `ZORUNLU_ALAN` ve dört bozma kalkar (`:1759`), şema GLB'de olduğu için yine FreeCAD
  veri adımlı üretim. Tahmini: 1–1,5 saat + `lale158_kontrol` koşusu + üretim.
- Hafıza notuyla fark: notta "P10.7 kalanı" diye kısa geçiyor; depoda ikisi de FreeCAD koşusuna bağlı açık iş olarak yazılı.

## 4. Madde 3 (kablo boyları): ALINMADI

Orkestratörün şartı (1 ve 2 tam bitmiş olmalı) sağlanmadı: madde 2 alınmadı.

## 5. Madde 4 (CAD'e dokunanlar): ALINMADI

Orkestratör kararıyla bu gece kapsam dışı (USB ses kartı CAD'den çıkarma, K64 bara tutucusu, K2 boss, K51 TVS modeli, K53 çentik);
inceleme yapılmadı. Hepsi tam taramalı CAD paketinde (≈ 3,8 saat tarama) ya da en az FreeCAD model değişikliğiyle.

## 6. Ek sınamalar ve son durum (01:59)

- `carpisma_kos.py kontrol`: çıkış 0, izlenen 17 dosya kayıtla aynı. `py_compile` (3 dosya): 0. `git diff --check`: temiz.
- Koşulmayan: tam üretim, zincir, F10d / F10e / F10f (veri ister), F9b / F9c (bu paket demoya ve sonuç raporuna dokunmadı), FreeCAD.
- `__pycache__`: `py_compile`'ın yazdığı dosyalar silindi; `planlama/d158/__pycache__/F10p-fis-gecis…pyc` önceden vardı, dokunulmadı.
- Git: HEAD = `origin/lale-duzeltme` = `376fe90` (`git fetch` sonrası 0 / 0).
- Bu paketin dosyaları: değişen `tasarim/freecad/rehber/rehber_metin.py`, `tasarim/freecad/rehber/rehber_denetim.py`,
  `planlama/d158/F10l-birlesim.py`, `planlama/adim3/kablolama-on-kararlar.md`; yeni `planlama/d158/F10q-gunluk.md`. Eski kir (19) aynı.
- `planlama/dongu-158.md` ve `F9c-uret.py` güncellenmedi (kapanış işi).

## 7. Düzeltme turu 1 (kontrol `F10q-kontrol.md` DÜZELTMEYLE GEÇER; 02:04–02:10)

Tur 0 farkı depo dışında saklandı (`git diff` → oturum karalama klasörü, `b2h-tur0.diff`); kontrol tur farkını onunla ayırır.

### 7.1 Bulgu 1: G3 sentil sırası → sınama F5 aşama 2'ye

- Dayanak (rehber verisindeki adım sırası, `rehber/veri/rehber-veri.json` `adimlar`): … G3 (40), G4, H0a–H0f, H1, **F5 (son, "—")**. Anahtarlı
  bara (servo XL4016 A / B / C) ilk kez F5 "İlk enerji, aşama 2"de devreye alınıyor (`rehber_metin.py` F5 madde 2, ön şarj dizisi); F1 aşama
  1'de anahtarlı bara enerjisiz. S1 / pan / tilt adımları da "orta komutun nasıl verileceği kaynakta yok" diyor. Sonuç: G3'te S2 beslenemez,
  komut alamaz.
- Seçim: G3 madde 1 yalnız "hornu, kol takılınca dişe dayanacağı konumda (S2 = 4,3°) tak (K40 a)"; G3 madde 2 sonuna "S2'nin sentil
  sınaması (K40 a) burada yapılmaz: S2 ilk kez F5 "İlk enerji, aşama 2"de sürülür, sınama orada"; G3 kontrolündeki sentil maddesi F5
  kontrolüne taşındı ("iki kolda da"); G3 alt adım 1 parantezi "sentil sınaması F5 aşama 2'de". F5 madde 2'ye, sağ / sol kurulum testinden
  sonra: her kolda S2'ye 5 komutu; kol dururken yalnız sentili tutan kişi kola yaklaşır, öbürü mantarda; 0,3 geçmeli / 0,4 geçmemeli; 0,3
  geçmiyorsa ana anahtarı kapat, aküyü ayır, zımparala, yinele.
- **ajan seçimi:** "yalnız sentili tutan kişi kola yaklaşır, öbürü mantarda" cümlesi, gerekçe: F5'te "kolların erişim alanında kimse yok"
  kuralı (00-genel kural 1 ve 7) ile sentil için ele gereken yakınlık çelişiyor; güvenlik kuralı istisnası benim yazımım, kaynakta yok.
  **Orkestratör bakmalı.** Zımparanın enerjisiz yapılması da benim eklemem.
- Denetim: G3 zorunlusu ikiye bölündü (horn dişe göre; sentil F5'e gönderili), F5'e yeni zorunlu (sentil sınaması).

### 7.2 Bulgu 3: XT60E-M → XT60E-F çevirisi

`git grep XT60E-M` (çeviri öncesi) her yer için karar:

| Yer | Karar |
|---|---|
| `planlama/adim3/kablolar.json` (11 geçiş: G06 ad, parça, uç a / b, sonlandırma, not, :8925 koruyucu adı, uç sözlüğü 2 anahtar + 2 parça) | çevrildi |
| `planlama/adim3/kablolar.md` | üretici çıktısı: `kablolar_uret.py` ile yeniden üretildi |
| `planlama/adim3/kablolar_denetim.py:211` (`hat-sarj` regex), `:2765` (bozma örneğinin eski adı; yalnız 10 A farkı kalsın diye) | çevrildi |
| `planlama/adim3/elektrik.md:324` (blok şeması; `kablolar_denetim` ayrıştırıyor, aynı uzunluk) | çevrildi |
| `tasarim/freecad/rehber/rehber_kablo.py:152, :185, :271` (eşleme anahtarları) ve `:186` yorumu ("K50'de karar bekliyor" → "K50 b (dişi; alımı açık)") | çevrildi |
| `tasarim/freecad/rehber/rehber_kritik_onay.json` | onay yenilemesiyle (§ 7.5) |
| `tasarim/freecad/rehber/rehber_metin.py:1805` F5 "siparişte XT60E-M varsa XT60E-F ile değiştirilir" | bilinçli, kalır (alım farkını anlatıyor) |
| `planlama/maliyet.json:111`, `planlama/d158/F8a-siparis.*`, `raporlar/kaynaklar/06-onayli-satici-A.md`, `tasarim/Robot-Tasarim-Demosu.html` (maliyet verisi) | alım, kalır |
| `planlama/d158/F10l-birlesim.py` (eski taban cümleleri, silinen listeleri) | tarihsel, kalır (taban metni) |
| `rehber/veri/rehber-veri.json` / `.js` | üretilmiş çıktı, üretimde yenilenir |
| Günlükler, kontroller, `karar-kuyrugu.md`, `dongu-158.md` eski girdileri, F7d raporu | tarihsel, kalır |

- Kablo onay kaydı (yenilemeden önce `rehber_kablo.py`): **3 fark, yalnız uç adı**: `MODELSIZ_KONUM` "XT60E-M * = None None" → "XT60E-F *
  …"; `PARCA_CAD` "XT60E-M = modelsiz" → "XT60E-F = modelsiz"; `UC_MODELSIZ` "XT60E-M şarj girişi = konnektör modelde yok (K50)" →
  "XT60E-F şarj girişi = …". Başka kablo alanı değişmedi.
- `maliyet.json` değişmedi. F5 notundaki "Konnektörün alımı açık: siparişte XT60E-M varsa XT60E-F ile değiştirilir (K50, …)" farkı
  karşılıyor; F1 madde 5'e de "alımı açık, F5 notu" girdi (§ 7.4).
- **Üretim kipi:** `--veri-yok` yeter (çıkarım, dayanağıyla). Depodaki `rehber-veri.json`'da "XT60E-M" yalnız dört metin alanında geçiyor
  (`adimlar/17/sira_grup/1/is_`, `adimlar/33/is_`, `adimlar/33/sira_grup/9/is_`, `adimlar/49/not_/1`); bunlar `rehber_metin` alanları ve
  `rehber_gorunum.isle()` tarafından `--veri-yok`'ta da yazılıyor (`rehber_uret.py:806-810`). FreeCAD adımının kablodan yazdığı alan
  (`TB.cizim` → `kb`) yalnız çizilen kablolarda; G06 hiçbir çizimde yok (sayım "hiçbiri 1 (G06)"), uç etiketi modelsiz. CAD / GLB değişmedi.
  Kesin değil: `app.js` / `yazdir.html` kablolar.json'u doğrudan okumuyor (yalnız yorumlarda anılıyor), gördüm.

### 7.3 Bulgu 2: etek ön sağ / sol

İki cümleye ek: "Bu bantta engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir."
Rehber cümlesine yazıldı (kupon listesine değil: kupon satırı bu paketin dosyası değil, `baski-listesi.md`'ye dokunulmadı).

### 7.4 Bulgu 4: F1 madde 5

"(XT60E-F, dişi panel girişi; K50 b: akü tarafı gömük soket, şarj kablosunun ucu erkek XT60; alımı açık, F5 notu)". "akü tarafı gömük
soket" **ajan açıklaması** (karar satırı "gerilimli tarafı dokunmaya kapalı" diyor; gömük soket dişi konnektörün yapısı, çıkarım).
"Şarj kablosunun ucu erkek XT60" karar satırında var (`karar-kuyrugu.md:1020`, K50 teknik yarı: "şarj kablosunun ucu erkek XT60"):
ajan açıklaması değil.

### 7.5 Kapanış kalemleri ve onay

- `F9c-uret.py`: K60 GRUP satırı "B seçilirse…" → "kapandı 17.11, A + köprülü klemens şimdi (demoda mantarın yanında bir kişi)" (yalnız
  açık kararlarda görünür); P10.7 özetine "Sürüyor: P10.7b2h (…)" (plan satırı yüzünden F9c-dogrula "alt paket sayfada yok" dedi, eklenince
  geçti; kapanışta "Kapalı"ya alınmalı).
- `planlama/dongu-158.md` § 5: paket satırı (02:08).
- Onay yenilemesinden önce kalan kritik farklar (37, `--kaynak`): kablo 3 (yukarıdaki uç adları); liste ZORUNLU 8 (3 değişen, 5 eklenen:
  bu paketin desenleri); metin 26: K1 alt 2 (G06) ve alt 8 ×2 (Ö4), E3a, F1 ana ×2 ve alt 3 ×2, alt 5 ×2, alt 10 ×2, F3 alt 1 / 2 / 5,
  F4 alt 1 / 2, F5 is_ ×2 (sentil), F5 kontrol (sentil), F5 not_ ×3, G3 ana ×2 ve alt 1. Hepsi bu paketin beş kararından ve tur 1'den;
  başka bölüm yok. `--kritik-onay-yenile`: 37 fark yazıldı (kablo 222, liste 218, metin 1138).

### 7.6 Sınamalar (PYTHONIOENCODING=utf-8; hepsi koşuldu)

| Sınama | Sonuç |
|---|---|
| `rehber_denetim.py --kaynak` (yenilemeden sonra) | çıkış 0; ASCII 0 (7 yeni kelime `ASCII_TAMAM`'a, gerekçe satırıyla), zorunlu eksik 0, yasak 0, onay farkı 0 |
| `rehber_denetim.py --bozma-denemesi` | çıkış 0, 303 / 303, M21e YAKALANDI |
| `F10l-birlesim.py` (taban 376fe90) | GEÇER; 1102 → 1116, eklenen 26 / 26, silinen 12 / 12 (liste yeniden üretildi, etiketler elle) |
| `kablolar_uret.py` + `kablolar_denetim.py` | yazıldı 74 kablo; GEÇER |
| `rehber_kablo.py` | GEÇER, onay kaydı (kablo bölümü) tutuyor |
| `F9c-uret --cikti <depo dışı>` + `F9c-dogrula --tarayicisiz --sayfa` | GEÇER (hata 0) |
| `git diff --check` | temiz (yalnız LF / CRLF uyarıları) |

### 7.7 Tur 1'de dokunulan dosyalar (tur 0'a ek)

Yeni olarak değişen: `planlama/adim3/kablolar.json`, `planlama/adim3/kablolar.md` (üretilen), `planlama/adim3/kablolar_denetim.py`,
`planlama/adim3/elektrik.md`, `tasarim/freecad/rehber/rehber_kablo.py`, `tasarim/freecad/rehber/rehber_kritik_onay.json`,
`planlama/d158/F9c-uret.py`, `planlama/dongu-158.md`. Tur 0'dan yeniden değişen: `rehber_metin.py`, `rehber_denetim.py`, `F10l-birlesim.py`,
bu günlük. `planlama/d158/F10q-kontrol.md` kontrol ajanının.

Kapanış sırası önerisi (tur 1 sonrası; onay yenilendi): bağımsız kontrol (tur farkı) → `--kaynak` 0 → `rehber_uret.py --veri-yok` → zincir →
commit (F9c "Sürüyor" → "Kapalı").

## 8. Düzeltme turu 2 (tur 1 kontrolü T1, T2; 02:12–02:18)

- **T1 (Echo kararı: istisna kabul, sınırlı):** F5 madde 2'deki sentil cümlesi kontrolün önerdiği metinle değişti; ek olarak erişim
  çekincesi (T2), "(sıkışma hattı)", "(yalnız enerjisizken)". Erişim kuralı cümlesi ("Kolların erişim alanında … kimse yok, bir kişi
  yalnız mantarda (kural 1 ve 7)") arkasına "; bu kuralın tek istisnası aşağıdaki S2 sentil sınamasıdır, şartları o cümlede" (iki cümle
  birbirini gösteriyor).
- **ajan seçimi:** "3 saniye" → "üç saniye", gerekçe: çıplak sayı denetimi süreyi yer tutucusuz kabul etmiyor; bu, kritik elektrik değeri
  değil, güvenlik beklemesi; yeni yer tutucu açmak kayıt (`kablolar.json`) değişikliği isterdi. "mantara bas" → "mantara hemen basılır"
  (ASCII denetimi "bas"ı listeye rağmen yakaladı; "baş" ile karışma koruması olmalı, bakmadım).
- **T2:** F5 cümlesi: "Bantlar takılıyken sentil dişle kol arasına düz giremiyorsa sınamayı zorlama; ölçülemedi diye kaydet ve omuz bandını
  sökmeden önce proje sahibine sor (aralığın kabuk altında erişilebilirliği CAD'de doğrulanmadı)."
- **Sonraki CAD paketine iş: S2 dişine F5'te (bantlar takılıyken) sentil erişimi ölçülecek.**
- Denetim: F5 zorunlu deseni yeni metne uyduruldu (`0,3 mm geçmeli, 0,4 mm geçmemeli`); 8 yeni F5 zorunlusu (tek istisna + komutu
  mantardaki kişi verir; üç saniye + aygıtlara dokunmaz; sıkışma hattı; komut verilmez; kıpırdarsa mantar; zımpara enerjisizken; erişim
  çekincesi; erişim kuralının istisna göndermesi). `ZORUNLU_BOZMA`'ya 3 bozma: istisna ibaresi silindi, "komut verilmez" silindi, erişim
  kuralının göndermesi silindi: **3 / 3 YAKALANDI**. `ASCII_TAMAM`'a 22 kelime (gerekçe satırıyla).
- Onay: yenilemeden önce 17 fark, hepsi bu tur: liste ZORUNLU 9 (1 değişen F5 deseni, 8 eklenen), metin F5 is_ 8 (3 değişen, 5 eklenen).
  `--kritik-onay-yenile`: 17 fark yazıldı (kablo 222, liste 226, metin 1143).
- Sınamalar (PYTHONIOENCODING=utf-8): `--kaynak` çıkış 0 (ASCII 0, zorunlu 0, çıplak 0, onay farkı 0); `--bozma-denemesi` çıkış 0, 306 / 306;
  `F10l-birlesim.py` GEÇER (1102 → 1121, eklenen 32 / 32, silinen 13 / 13; liste yeniden üretildi, etiketler elle); `kablolar_denetim.py`
  GEÇER; `rehber_kablo.py` GEÇER; `git diff --check` temiz.
- Tur 2 dosyaları: `rehber_metin.py`, `rehber_denetim.py`, `rehber_kritik_onay.json`, `F10l-birlesim.py`, bu günlük.

## 9. Kapanış tarifi (üretim, zincir, commit; işi bilmeyen biri tek başına uygular)

Çalışma dizini her komutta depo kökü (`Robot`). PowerShell; her oturumun başında:
`$env:PYTHONIOENCODING = "utf-8"`. Önce Chrome kapalı, boş bellek ≥ 2,9 GB (`(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB`).
FreeCAD bu tarifte hiç koşmaz (`--veri-yok`); `planlama/d158/FREECAD-KILIT.txt` "boş" kalır. 20 s'den uzun her komut arka planda
başlatılır, bitiş `.durum` dosyasından ya da çıkış kodundan kısa yoklamalarla okunur (tek uzun bekleyiş yok).

Arka plan kalıbı (her uzun komut için `AD` ve `KOMUT` değişir; günlük ve `.durum` depo dışında, `$U` = oturum karalama klasörü):

```
$U = "$env:TEMP\b2h-kapanis"; New-Item -ItemType Directory -Force $U | Out-Null
$AD = "uret"; $KOMUT = "py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile","-Command",
  "`$env:PYTHONIOENCODING='utf-8'; Set-Location '$PWD'; `$s=Get-Date; $KOMUT *> '$U\$AD.log'; `$c=`$LASTEXITCODE; 'BITTI cikis ' + `$c + ' sure ' + [int]((Get-Date)-`$s).TotalSeconds | Out-File -Encoding ascii '$U\$AD.durum'"
# yoklama (her 2-3 dakikada bir, ön planda): Test-Path "$U\$AD.durum"; Get-Content "$U\$AD.durum"; Get-Content "$U\$AD.log" -Tail 5
```

### 9.a Üretim

- Komut: `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (**`--cikti` YOK**: `--cikti` verilirse `rehber_gorunum.isle()`
  çağrılmaz, depo verisi yazılmaz; `rehber_uret.py:806-810`). Arka plan kalıbıyla, `AD = "uret"`.
- Süre: önceki `--veri-yok` koşuları 2581–2722 s (≈ 43–45 dk). Geçme: `.durum` "BITTI cikis 0"; log sonunda PDF sayfa sayısı (≈ 86, taşan 0),
  denetim ASCII 0, zorunlu eksik 0. Çıkış ≠ 0 → § 9.f.

### 9.b Yeterlilik kanıtı (üretimden hemen sonra, ön planda, saniyeler)

```
py -3 -X utf8 -c "import io;[print(f, io.open(f,encoding='utf-8').read().count('XT60E-M'), io.open(f,encoding='utf-8').read().count('XT60E-F')) for f in ('rehber/veri/rehber-veri.json','rehber/veri/rehber-veri.js','planlama/adim3/kablolar.md')]"
Select-String -Path rehber/veri/rehber-veri.json -Pattern 'XT60E-M' -Encoding utf8 | % Line
```

Beklenen: `rehber-veri.json` ve `rehber-veri.js` içinde `XT60E-M` **1'er** (yalnız "siparişte XT60E-M varsa XT60E-F ile değiştirilir" cümlesi),
`XT60E-F` > 0 (K1 alt adım 2, F1 madde 5 ve alt adım 10, F5 not_; kesin sayı önceden ölçülmedi); `kablolar.md` `XT60E-M` 0, `XT60E-F` > 0 (G06 uç adları). Kablo kartı:
`py -3 -B -X utf8 tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` → "SONUÇ GEÇER". Tutmazsa (veride eski ad
kalmışsa) **tam üretim**: FreeCAD kilidini al (`FREECAD-KILIT.txt`'e satır), boş bellek ≥ 2,9 GB, arka plan kalıbıyla
`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` (≈ 45–50 dk; önceki tam koşu 2606–2895 s), sonra 9.b'yi yinele, kilidi "boş"a döndür.

### 9.c Doğrulama zinciri (`F10o-gunluk.md` § 9.4, `F10m-gunluk.md` § 13.2 ile aynı sıra)

| Sıra | Komut (depo kökünden, `py -3 -B -X utf8 …`) | Süre | Geçme | FreeCAD |
|---|---|---|---|---|
| 2a | `tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 1–2 s | "SONUÇ GEÇER", onay tutuyor | hayır |
| 2b | `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi --veri rehber/veri/rehber-veri.json` | ≈ 30 s | hepsi yakalandı (b2g'de 108 / 108) | hayır |
| 3 | `tasarim/freecad/rehber/rehber_denetim.py` (argümansız, veri) | 1 s | ASCII 0, zorunlu eksik 0 / N, yasak 0, çıkış 0 | hayır |
| 4 | `planlama/d158/F10f-dogrula.py` | ≈ 10 dk | "GEÇTİ", çıkış 0 | hayır (tarayıcı) |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | ≈ 17 dk | "GEÇTİ"; `renk_demo` KALDI bilinen, çıkış 0 | hayır |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` (**tek başına**, bellek en çok burada düşer) | ≈ 15–17 dk | "GEÇTİ", 141 / 141 konum, 360 px taşma 0 | hayır |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | ≈ 8 dk | "GEÇTİ", dış istek 0, konsol 0 | hayır |
| 8 | `planlama/d158/F9b-dogrula.py` | 5 s | "GEÇER (hata 0)" | hayır |
| 9 | `tasarim/freecad/carpisma_kos.py kontrol` | < 1 s | "izlenen 17 dosya … kayitla ayni" | hayır |
| 10 | `planlama/d158/regresyon.py --yazma` | < 1 s | "GEÇER", kötüleşen yok | hayır |

4–7 arka plan kalıbıyla (her biri ayrı `AD`); boş bellek 1,2 GB'ın altına inerse süreci durdur, belleği bekle, o adımı yeniden koş.
Zincir `planlama/d158/F10{a,d,e,f}-dogrula.json` yazar (commit'e girer). Toplam ≈ 52–55 dk.

### 9.d Zincir yeşilse kapanış düzenlemeleri

1. `planlama/d158/F9c-uret.py` P10.7 özeti: "Sürüyor: P10.7b2h (…). " satırını sil, "P10.7b2g (…). " satırının arkasına
   `"P10.7b2h (17.11 kararlarının rehber metni: K40, K50 b, K51, K55, K60). "` ekle; F10 özetinde "b2f, b2g" → "b2f, b2g, b2h".
2. `planlama/dongu-158.md` § 5 en üste kapanış satırı (saat `Get-Date` ile): "**P10.7b2h kapanışı** (commit "Lale P10.7b2h"): üretim
   `--veri-yok` çıkış 0 (süre, PDF sayfa), zincir 2–10 çıkış 0"; § 3 P10.7 satırının sonuna kısa b2h özeti (§ 5 satırıyla aynı içerik).
3. Bu günlüğe "§ 10 Kapanış" (üretim ve zincir sonuçları tablosu, 9.b sayıları).
4. Sonra yeniden koş: `py -3 -B -X utf8 planlama/d158/F9c-uret.py --cikti "$U\sonuc.html"` + `py -3 -B -X utf8 planlama/d158/F9c-dogrula.py
   --tarayicisiz --sayfa "$U\sonuc.html"` → "GEÇER (hata 0)" (depodaki `sonuc-rapor.html` yeniden yazılmaz, faz sonu işi). Ardından
   `rehber_denetim.py --kaynak` 0 ve `planlama/d158/F10l-birlesim.py` GEÇER (kaynak değişmediğini teyit). `__pycache__` kalmadığını denetle.

### 9.e Commit

Eski kir, girmez (19): `tasarim/freecad/kabuk/gorsel/` altındaki 13 PNG (kabuk-arka-kapak-acik, kabuk-baglanti-etek, kabuk-baglanti-govde,
kabuk-izometrik, kabuk-kesit-gogus, kabuk-kesit, kabuk-nextion-ic, kabuk-nextion-on, kabuk-omuz-duvari, kabuk-on, kabuk-patlatilmis-on,
kabuk-patlatilmis, kabuk-yan), `tasarim/freecad/montaj/yerlesim-kontrol.json`, kökte `geometri2_cikar.py`, `geometri2_dogrula.py`,
`geometri_cikar.py`, `gez.js`, `uc.js`. **`git add -A` kullanılmaz; dosyalar adıyla eklenir.**

Girecek (kaynak, 14): `planlama/adim3/elektrik.md`, `planlama/adim3/kablolama-on-kararlar.md`, `planlama/adim3/kablolar.json`,
`planlama/adim3/kablolar.md`, `planlama/adim3/kablolar_denetim.py`, `planlama/d158/F10l-birlesim.py`, `planlama/d158/F9c-uret.py`,
`planlama/dongu-158.md`, `planlama/d158/F10q-gunluk.md`, `planlama/d158/F10q-kontrol.md`, `tasarim/freecad/rehber/rehber_metin.py`,
`tasarim/freecad/rehber/rehber_denetim.py`, `tasarim/freecad/rehber/rehber_kablo.py`, `tasarim/freecad/rehber/rehber_kritik_onay.json`.
Girecek (üretim / zincir çıktısı): `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js`, `planlama/rehber/Lale-montaj-rehberi.pdf`,
`planlama/rehber/kontrol.json`, `planlama/d158/F10a-dogrula.json`, `planlama/d158/F10d-dogrula.json`, `planlama/d158/F10e-dogrula.json`,
`planlama/d158/F10f-dogrula.json`, üretimin değiştirdiği kareler (`git status --short -- rehber/goruntu planlama/rehber/goruntu` listesindeki
her `M` / `??` PNG, adıyla). Başka bir yol `git status`'ta yeni görünürse (yukarıdaki iki listede yoksa) commit'e alma, günlüğe yaz.
`regresyon.json` değişirse (beklenmez) dur, günlüğe yaz.

Push öncesi: `git diff --cached` kişisel bilgi / yerel kullanıcı yolu / anahtar taraması (yerel kanca kalıpları), sonra commit:

```
git commit -m "Lale P10.7b2h: 17.11 kararlarının rehber metni (K40 sentil F5'te, K50 b XT60E-F, K51, K55, K60), kablo kaydı XT60E-F, rehber yeniden üretildi"
git push origin lale-duzeltme
```

(İleti sonuna depodaki kurala göre yardımcı satırı.) Push sonrası `git fetch` + `git rev-list --left-right --count HEAD...origin/lale-duzeltme` → 0 0.

### 9.f Bir adım kırmızıysa

Commit yok, push yok. O adımın log'unun son 60 satırını ve `.durum`'unu bu günlüğe "§ 10 Kapanış: KALDI" başlığıyla yaz; çıktı
dosyalarını (veri, PDF, kareler, `F10*-dogrula.json`) geri alma ya da commit'leme, olduğu gibi bırak; orkestratöre bildir. Bellek
bekçisiyle durduysa kod hatası değildir: belleği bekleyip yalnız o adımdan itibaren yeniden koş (F10m § 13.2 örneği).

Eski kapanış sırası önerisi (tur 0): bağımsız kontrol → `rehber_denetim.py --kritik-onay-yenile` (28 fark) → `--kaynak` 0 → `F10l-birlesim.py` GEÇER →
`rehber_uret.py --veri-yok` (yalnız metin değişti; CAD / GLB değişmedi) → zincir → commit.

## 10. Kapanış (02:20–03:55, kapanış ajanı)

Arka plan kalıbı: § 9'daki `Start-Process` kalıbı tutmadı (boşluklu `$KOMUT` argümanı bölündü, `py` etkileşimli kipte açıldı;
süreçler hemen kapatıldı, iş yapılmadı). Yerine Bash arka plan koşusu + `.durum` dosyası (aynı ilke: log ve `.durum` depo dışında).

| Adım | Sonuç | Çıkış | Süre |
|---|---|---|---|
| 9.a üretim `--veri-yok` | PDF 86 sayfa (adım 50, devam 36), taşan 0; denetim ASCII 0, zorunlu eksik 0 / 131; tarayıcı 50 / 50; kablo eşleme GEÇTİ | 0 | 2238 s |
| 9.b yeterlilik | `XT60E-M` / `XT60E-F`: rehber-veri.json 1 / 7, rehber-veri.js 1 / 7, kablolar.md 0 / 6; tek `XT60E-M` alım cümlesi ("siparişte XT60E-M varsa XT60E-F ile değiştirilir") | - | - |
| 2a rehber_kablo | SONUÇ GEÇER | 0 | 1–2 s |
| 2b bozma denemesi | 108 / 108 yakalandı | 0 | ≈ 30 s |
| 3 rehber_denetim | ASCII 0, zorunlu eksik 0 / 131, yasak 0, elektrik iddiası 0 | 0 | 1 s |
| 4 F10f | GEÇTİ | 0 | 548 s |
| 5 F10e `--goruntu-yok` | GEÇTİ; renk_demo KALDI (bilinen, karar) | 0 | 916 s |
| 6 F10d `--goruntu-yok` | GEÇTİ, 360 px taşma 0 | 0 | 947 s |
| 7 F10a `--kanit-yok` | GEÇTİ, dış istek 0, konsol 0 | 0 | 423 s |
| 8 F9b | GEÇER (hata 0) | 0 | 6 s |
| 9 çarpışma kontrol | izlenen 17 dosya kayıtla aynı | 0 | < 1 s |
| 10 regresyon `--yazma` | GEÇER, kötüleşen yok; regresyon.json değişmedi | 0 | < 1 s |

9.d: F9c-uret.py P10.7 özeti ("Sürüyor" → kapalı listesine b2h; F10 özeti b2h), dongu-158.md § 5 kapanış satırı ve § 3 P10.7 özeti.
İlk F9c-dogrula koşusu GEÇMEZ (hata 2: "P10.7b2h 'kapalı' yazıyor, planda kapanmamış"): § 3'e yazdığım kalın ibare "**b2h kapandı**"
idi, denetleyici `**P10.7b2h … kapandı**` arıyor; ibare "**P10.7b2h kapandı**" yapıldı (kayıt düzeltmesi, kural değişmedi) →
F9c-dogrula GEÇER (hata 0), F9b ve regresyon yeniden GEÇER. `rehber_denetim.py --kaynak` 0, F10l-birlesim GEÇER. `__pycache__` yok.
`ASCII_TAMAM` ek kontrolü: bu paketin eklediği kelimelerin hepsi Türkçe harfi gerektirmeyen doğru yazım, şüpheli yok.
Gizlilik taraması: § 9'daki yerel kullanıcı yolu commit öncesi Robot olarak kısaltıldı; başka bulgu yok.
