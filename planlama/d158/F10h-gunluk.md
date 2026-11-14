# F10h günlüğü: rehberin elektrik tarafı tek kablo kaynağına bağlandı (P10.7b1, A adımı, FreeCAD'siz kısım)

Uygulama ajanı A. Dal `lale-duzeltme`, HEAD `8134519`. Bu adım bellek kısıtıyla yalnız kaynak düzeyinde yapıldı: 14.11 08:25 ölçümünde
kullanılabilir bellek 2,25 GB (çekirdek havuzları ≈ 5,4 GB); 2 GB kuralı gereği **FreeCAD, `rehber_uret.py`'nin FreeCAD'li koşusu ve
doğrulama zinciri koşmadı**, karelere bakılmadı (brief madde 6 ve 7 yapılmadı; yerine § 9 "Üretim adımında koşulacaklar"). Çalışma
boyunca ölçülen kullanılabilir bellek 2213–2267 MB (1,2 GB durma eşiğine inmedi). Geçici dosyalar depo dışındaki geçici klasörde, depoya
kopyalanmadı. Commit / push / `git add` yok (C adımı).

**Kaynak ↔ çıktı tutarsızlığı (bilerek):** rehber kaynağı değişti, çıktılar (`rehber/veri/*`, `rehber/goruntu/*`, `planlama/rehber/*`)
yeniden üretilmedi ve elle düzenlenmedi. Bugünkü `rehber/veri/rehber-veri.json` eski metni ve eski renkleri taşıyor: yeni
`rehber_denetim.py` onu okursa **54 elektrik iddiası** (A adımının kurallarıyla; düzeltme turu 1'in kurallarıyla 55; ekran çıktısı
yalnız ilk 30 satırı basıyor, ilk yazımdaki "30" bu yüzdendi; sayım `elektrik_denetle` dönüşünden), `rehber_kablo.py --veri` 64 hata
veriyor (beklenen; üretimden sonra 0 olmalı). Eski kaynakta (HEAD `rehber_metin.py`) aynı sınamanın bulduğu 49 (§ 2) ayrı sayıdır.
**Düzeltme turu 1** (bağımsız kontrol `F10h-kontrol.md` DÜZELTME GEREKLİ): § 11; § 9 o tura göre yenilendi; § 1–8'deki bayat sayılar
yerinde işaretlendi.
Görüntüleyici kaynakları (`rehber/app.js`, `stil.css`, `yazdir.html`) yeni alanları (`kablo`, `ks`, `kb`, `karisik`, `kablo_sinif`)
okuyor; alan yoksa eski davranışa düşüyor, yani eski veriyle de açılır.

Çalışma ağacında bu işten eski 14 değişik dosya (dokunulmadı, geri alınmadı): `tasarim/freecad/kabuk/gorsel/*.png` (13),
`tasarim/freecad/montaj/yerlesim-kontrol.json`.

## 1. Dört açık iş (kablo tablosu tarafı; dördüncü bakış `P107a-kontrol-4.md` §2)

| İş | Ne yapıldı | Bozma (yeni) |
| --- | --- | --- |
| §2-2 `sayi_metin` alt sınıfları | `kablolar_denetim.py`: `ad`, `sonlandirma`, damar `ara` alanında adsız akım yalnız kablonun kendi koruması + ara koruyucusu (zincirdeki öbür koruyucu ancak adıyla); `not` / `kesit_not`'ta kesit sınırı yalnız "AWG" ya da "sınır" sözcüğünün ± 30 karakter yanında; F<n> (ad / sonlandırma / ara'da her biri, notlarda sayısız olanı) kablonun kendi zincirinde ya da uç düğümünde. Eski bozma N5c hedefi G18'den I01'e taşındı (G18 artık teyitte) | 8 (`b_sayi_metin_7` … `_14`: B05, B06, B08, B09, B15–B18) |
| §2-3 blok şemasında bobin satırı | `elektrik.md` blok şeması: "röle K1 bobini ∥ K2 bobini (her bobin kendi BC337-40'ıyla, E9)". Denetim: paralel bobinler tek şema öğesindeyse öğe sürücü sayısını kart içi bağlardaki "BC337-40 #n" sayısıyla aynı söylemeli (iki yönde) | 2 (`b_blok_6`, `_7`) |
| §2-5 belgesiz uç türüne "kesin" | `BELGESIZ_UC` (= `bts-guc`, `modul-vidali`, `sigorta-kutusu`): bu uçlu kablonun teyit listesinde o parçayı anan `klemens:` maddesi olmalı, yoksa hata. `kablolar.json`'da SV1–SV3, G18, G19, G22, A01, A02, K02 (+ teyitte olan M01–M04, G14–G17, G20, G21, A06, K04) için `klemens:` teyit maddesi eklendi | 2 (`b_klemens_14`, `_15`) |
| §2-7 malzeme iletken sözlüğü + köprü | `malzeme_turleri.*.iletken` `MALZEME_ILETKEN` sabitiyle karşılaştırılıyor. Vidalı klemens kartı üstündeki köprü "≥ N AWG tel köprü" yazmalı ve N karta giren en kalın güç kablosundan ince olmamalı. `kablolar.json`: kafa giriş kartı (G17, K01, K02) ve acil stop düğüm kartı (A02, A04) "lehimle köprülü" → "≥ 18 AWG tel köprüyle (lehim …)" | 3 (`b_klemens_16`, `_17`, `_18`) |

- **Durum sayıları (kendi ölçümüm, `kablolar.json`):** kesin **22** / teyit **51** / karara bağlı **1** (önce 31 / 42 / 1). Kesinden
  teyite geçen 9: SV1, SV2, SV3, G18, G19, G22, A01, A02, K02 (hepsi §2-5: belgesiz uç). `kablolar.md` ve `elektrik.md` bloğu yeniden
  üretildi (`kablolar_uret.py`; `--kontrol` "güncel"). Sayıyı taşıyan eski kayıtlar (`dongu-158.md` § 5 P10.7a girdisi,
  `kablo-tablosu-gunluk.md`, `P107a-kontrol-4.md`) tarihçe olduğu için değiştirilmedi; yeni sayı `dongu-158.md` P10.7 satırına yazıldı.
- K04 notunda "0,9 A varsayım" → "900 mA varsayım" (değer aynı; yeni §2-2 kuralı adsız "0,9 A"yı kablonun koruması sanıyordu).
  **Düzeltme turu 1'de geri alındı** ("0,9 A varsayım"; kural yük bağlamında daraltıldı, § 11). Durum sayıları da değişti: 21 / 52 / 1
  (A04 teyite), bozma 138; ek kararla K01 de teyite: **20 / 53 / 1**, bozma 139 (§ 11.11); açık işler turu sonunda bozma 145 (§ 12).
- `renk_kurali.ilke` metni: kaldırılan `kablo_rengi` yerine `rehber_kablo.py` anıldı.
- Devre değeri değişmedi (sigorta, kesit, pin, uç).
- `kablolar_denetim.py`: çıkış 0 (GEÇER); `--bozma-denemesi` **136 / 136** yakalandı (önce 121; +15).

## 2. Rehber metinleri tek kaynakla aynı (`tasarim/freecad/rehber/rehber_metin.py`)

Bütün kaynak metni yeni elektrik sınamasıyla (§ 4) tarandı. **Eski kaynakta (HEAD) sınamanın bulduğu: 49 iddia** (terim 19, karar 15,
sigorta 13, GPIO 1, E9 1); düzeltmeden sonra **0**. Eski satır numaraları (HEAD `rehber_metin.py`):

| Konu | Eski satır | Yeni değer (kaynak) |
| --- | --- | --- |
| "şarj 10 A" / "şarj girişi mini 10 A" | 251, 626, 634, 711, 1291 | şarj hat sigortası 7,5 A mini (XT60E-M girişi, G06; `kablolar.json` `hat-sarj`) |
| "göğüs ekranı mini 2 A" | 587, 611, 634, 808, 842, 843, 1524 | F6 3 A standart (kutunun 6. yuvası, K11 a, acil stopta açık; K52 karar bekliyor) |
| "K2 = GPIO2" | 637 | K2 GPIO19 (ön şarj), K1 GPIO4; PC817 #1 GPIO23, #2 GPIO5 (`pin-haritasi.md` § 9) |
| WAGO | 217, 255, 642, 1485–1490 | M5 saplama + halka pabuç; iki küçük kartta 5,08 mm vidalı klemens; WAGO yok |
| MOSFET (röle sürücüsü) | 1495 | BC337-40 #1 / #2 + 270 Ω + 2,2 kΩ + 1N4007 (bobine ters paralel, katot + tarafta) |
| USB ses kartı | 8, 407–528 (E4 adımı), 1528–1529 | ReSpeaker 3,5 mm → 10 kΩ / 2,2 kΩ bölücü → PAM8403; USB ses kartı yedek, takılmaz |
| "varsayım, K10" | 469, 498, 529, 1493, 1530 | K10 a kapandı: PAM 5 V D24V50F5'ten |
| K11 b dalı | 817, 832, 1258, 1266, 1271, 1284 | K11 a kapandı: F6 3 A, göğüs dalı acil stopta açık |
| ön şarj "300 ms" | 1265 | E9: en az 300 ms (boş aküde 500 ms önerilir) → GPIO5 LOW teyidi → GPIO4 → 100 ms → GPIO19=0; K2 en çok 1 s |
| "Hızlı klemens" | 282 | kaldırıldı |
| "K1 / K10 / K11 karar bekliyor" | E4, K2, F3, F5 notları | kapandı (K1, K10 a, K11 a, K14 a) |

Yeni metnin yeri (çalışma ağacı `rehber_metin.py`): B5a 206; **K1 248** (iş 1–8 baştan: ana hat G01–G04, ana sigorta 30 A, şarj kolu G06,
yıldız barası 5 saplama yerleşimi, F1 → röle / ön şarj → bara, mini hat sigortaları, F3 / F4 / F5 / F6, acil stop düğüm kartı ≥ 18 AWG
tel köprü, BC337-40 sürücüleri, PC817 #1, enkoder / sonar; "8. K1'de enerji verilmez"; kontrol: iki 1N4007 yönü, saplama başına ≤ 4
pabuç, teslimde bakılacaklar); E3a 434 (kafa giriş kartı K01 / K02 / K03 / K05, QLED akımı ilk açılışta ölçülür); **E4 496** (ses yolu
U01, AU1, AU2, K05, KT2); **K2 618** (G17; U06 ve 1N5819 1 A sınırı; boyun demeti 5 kablo, geçiş sırası, **tünel deneme parçasında fiş
denemesi** demet kurulmadan önce, Efe'nin iki cevabı; göğüs 12 V F6 3 A); **F1 680** (XT60E-M, kutuda standart / hat yuvasında mini,
aşama 1'de F6, G22 ve şarj 7,5 A takılı değil, ölçü noktası yıldız barasının 3. saplaması); **F3 876**; **F5 1323** (hub harici
beslemesiz USB 2.0; E9 dizisi); KABLO_AD 1562 (12 CAD yolu kimlikli; WAGO / MOSFET / "varsayım, K10" çıktı); SEMA 1607 (son alan artık
kimlik tuple'ı; "Ses karti uzatmasi" ve "3,5 mm -> PAM" şemaları kaldırıldı: 13 → 11).

**Karar bekliyor diye yazılanlar:** K52 (göğüs regülatörünün panel yeri: K1 is_, K2 is_ / not_, F3 not_), K60 (elde taşınan acil stop,
Ö4: K1 is_), K61 (konuşmak için basılan düğme, O-12: K2 not_; "tabloya kablo eklenmedi"). Hoparlör / hub koşullu kalem (K4 O-10 b), hub
harici beslemesiz (Ö2), KT5 notları korundu.

**Teslimde bakılacaklar** (`kablo-tablosu-gunluk.md` §17.7 "Ahmet'e"): K1 kontrol listesine uyarı olarak; K2'de tünel denemesi ve
Efe'nin cevapları iki kontrol maddesi.

## 3. Çizilen kablolar ↔ tablo (`tasarim/freecad/rehber/rehber_kablo.py`, yeni; FreeCAD istemez)

- **Bağlama:** taban CAD'indeki 12 "Kablo yolu N" parçası `CAD_ESLEME` ile, SEMA şemaları son alandaki kimlik tuple'ıyla, kol içi yol
  bölümleri `KOL_ESLEME` ile (sağ S02 / S03 / S04, sol S06–S08) tablo kimliklerine bağlı. İlk kimlik "ana" kablo.
- **Renk = ana kablonun devre sınıfı rengi** (`renk_kurali.siniflar[sinif].cizim`); anahtar kelimeyle renk verme (`kablo_rengi`)
  kaldırıldı. Eşlemesi olmayan kablo parçası UYARI + gri; denetim hata sayar.
- **Tüp yarıçapı (şema ve kol bölümleri):** r = 1,2 + 1,5 × √(kesit mm²) mm, 0,1 mm'ye yuvarlı (22 AWG 2,1; 18 AWG 2,6; 16 AWG 2,9;
  12 AWG 3,9). **Düzeltme turu 1'de değişti:** kademe tablosu 22 AWG 2,5 / 18 AWG 3,1 / 16 AWG 3,6 / 12 AWG 4,6 (§ 11).
  Hazır kablo (USB / HDMI / CSI): tabloda dış çap şartı varsa yarısı, yoksa 2,5. Kesiti tabloda yoksa 2,5. **Taban CAD
  parçalarının çapı geometri: değişmedi** (yalnız renk ve bilgi tablodan). Kablo geometrisine (yol, nokta) dokunulmadı.
- **Tıklayınca / listede:** kimlik, ad, iki uç, kesit, sigorta (`koruma` + tip), acil stopta enerjili mi (`app.js` `kabloBilgi`; karışık
  sınıflı yolda not). **Lejant:** `VERI.kablo_sinif` (renk → devre sınıfı); `app.js` ince gri çerçeveli "Kablo: …" girdisi, `yazdir.html`
  lejant metni; iki temada okunurluk **görülmedi** (§ 9).
- **Sayılar (kendi ölçümüm, kaynaktan):** tablo 74; **çizilen 55**, **çizilmeyen 19**: G06, G07, G16, SV3, G22, X01, I01, I02, P01, P02,
  P03, S01, S05, K01, K02, K03, C01, AU1, AU2 (P10.7b2'nin girdisi). Eşlenemeyen çizilmiş kablo: kaynakta 0 (veride üretimden sonra
  sayılacak). **Düzeltme turu 1'de yanlış çıktı** (kontrol Ü3: yol 4'te M02, N01 / N02 ve S01 / S05 yanlış sınıfta); yeni sayım
  **51 / 23** (§ 11).
- **Karışık sınıflı CAD yolları** (tek parça birden çok devre sınıfı taşıyor, ana kablonun rengini alır): Kablo yolu 3 (kırmızı /
  turuncu), 5 ve 7 (sarı / turuncu), 9 (kırmızı / mavi).
- Şema sayısı: rehber verisinde 51 → **49** beklenir (SEMA 13 → 11, kol 38 aynı).
- Bağlayan kaynaklar: `rehber_veri.py` (`kablo_cizim`, `kaynak_denetle` hatasında SystemExit, VERI'ye `kablo_sinif` ve `kablo_kaynak`),
  `rehber_kol_kablo.py` (`isle()` her bölüme `kol_kimlik` + `Tablo.cizim`), `rehber_uret.py` (`ek["kablo_esleme"]`, kötüler listesinde).

## 4. Kalıcı sınamalar ve bozma denemeleri

(A adımının sonucu. Düzeltme turundan sonraki sayılar § 11.7'de: kablo bozma 138, elektrik bozma 42, eşleme bozma 17; ek kararla
kablo 139. Açık işler turu sonunda (§ 12.8): kablo 145, rehber denetimi 65, eşleme 27.)

| Sınama | Ne karşılaştırır | Sonuç (kendi koşum) | Bozma |
| --- | --- | --- | --- |
| `kablolar_denetim.py` | tablo ↔ elektrik.md / maliyet / pin | GEÇER, çıkış 0 | 136 / 136 |
| `rehber_denetim.py` § 8 elektrik (`elektrik_denetle`) | rehber metnindeki GPIO, uç bağı, sigorta amperi ve tipi (F1–F6, ana, şarj, göğüs, mini değerleri), AWG, direnç ↔ `kablolar.json` + `pin-haritasi.md` § 9 JSON; eski terimler (MOSFET, WAGO, ses kartı, hızlı klemens, USB 3.0, kapanmış karar + "karar bekliyor", "varsayım, K10", K11 b, "en az"sız 300 ms, harici besleme) | `--kaynak`: metin 528, ASCII kalıntı 0, elektrik 0, zorunlu uyarı eksik 0 | **16 / 16** (eski pin, eski şarj sigortası, eski göğüs sigortası, MOSFET, WAGO, yanlış AWG, yanlış direnç, ses kartı, kapanmış karar, 300 ms, PC817 #2 pini, hızlı klemens …); bozulmamış kaynakta 0 |
| `rehber_denetim.py` zorunlu uyarılar | eski beklentiler yeni değerlere çekildi (yıldız barası, şarj 7,5 A F1 / F5, F6 3 A, K11 a, 12 V fişinden önce ölçüm) + yenileri (E9 dizisi, K2 en çok 1 s, K1 sürücüleri ve 1N4007, teslimde bakılacaklar, tünel deneme parçası, Efe, E4 ses yolu) | eksik 0 | (yukarıda) |
| `rehber_kablo.py` | eşleme: kimlik tabloda var, her şema / CAD numarası / kol bölümü eşli, sınıf renk kuralında, şemanın adımı ana kablonun rehber adımında; `--veri`: renk ve yarıçap türetilmişle aynı, lejant var | GEÇER | **9 / 9** kaynak; benzetilmiş veriyle (geçici kopyada) **14 / 14** |
| `rehber_kol_kablo.py --yazma` | kol yolu ↔ kaynak (veri yazmaz) | GEÇTİ (38 bölüm, hata 0) | — |

Göğüs sigortası penceresi 30 → 70 karakter genişletildi: eski kaynakta K2'deki "Göğüs ekranı 12 V boyundan geçmez: tabandan ayrı daldan
(mini 2 A" artık yakalanıyor (48 → 49).

`rehber_denetim.py` ASCII sözlüğüne bu paketin metinlerinden 93 kelime eklendi (gözden geçirildi; "firmware" teknik terim, "Ahmet" /
"Efe" kişi adı).

## 5. Değişen dosyalar

- **Kaynak (elle):** `planlama/adim3/kablolar.json`, `kablolar_denetim.py`, `elektrik.md` (bobin satırı; blok tablo kısmı üretilir);
  `tasarim/freecad/rehber/rehber_metin.py`, `rehber_denetim.py`, `rehber_veri.py`, `rehber_kol_kablo.py`, `rehber_uret.py`,
  `rehber_kablo.py` (yeni); `rehber/app.js`, `rehber/stil.css`, `rehber/yazdir.html`; bu günlük, `planlama/dongu-158.md`,
  `planlama/d158/karar-kuyrugu.md`.
- **Üretilmiş:** `planlama/adim3/kablolar.md`, `elektrik.md` içindeki tablo bloğu (`kablolar_uret.py`).
- **Üretilmedi (üretim adımında yeniden yazılacak):** `rehber/veri/*`, `rehber/goruntu/*`, `planlama/rehber/*`.

## 6. Orkestratöre

(Madde 1 onaylandı, madde 2 geri alındı, madde 3 Ü3'te düzeldi: yol 4 = M03, M04 (+ G13); düzeltme turunun listesi § 11.9.)

1. **Acil stop düğüm kartı köprüsü:** §2-7 yalnız kafa giriş kartını söylüyordu; aynı "lehimle köprülü" ifadesi acil stop düğüm kartında
   (A02, A04) da vardı, aynı kuralla "≥ 18 AWG tel köprü" yazıldı. Onay gerekir.
2. K04 notunda "0,9 A" → "900 mA" yalnız yazım (yeni kuralın yanlış pozitifi); istenirse kural daraltılır.
3. KABLO_AD 4 (CAD adı "sağ kol + arka") M02–M04'e bağlandı; CAD adı ile tablo motor adlandırması arasında yorum farkı olabilir.
4. ReSpeaker ses kablosu (AU1 3,5 mm, AU2 bölücü → PAM) için rehberde şema yok (eski "3,5 mm -> PAM" şeması USB ses kartı yolunu
   gösteriyordu, kaldırıldı); yeni şema P10.7b2'de çizilmeli.
5. Kol telleri devre sınıfı olarak hepsi sarı (servo 6 V): eski çizimde bölüm sınırları renkle ayrılıyordu; okunurluk kare bakışında
   görülmeli, gerekirse bölüm işaretleri ayrı tonla.
6. `kafa-yerlesim/uygulama_rapor.py` `K_AD` eski kablo adlarına atıf yapıyor (yalnız bilgi; dokunulmadı).

## 7. Bilinmeyenler

- Üretilmiş veride eşlenemeyen parça / şema sayısı, renk ve yarıçap denetimi: yalnız benzetilmiş veriyle sınandı.
- PDF sayfa sayısı: lejant satırı uzayabilir (taban 75 sayfa); ölçülmedi.
- F10f `kablo_kare` piksel ölçütü: kol bölümlerinin yarıçapı tablodan geliyor (ilk yazımda 22 AWG 2,1; düzeltme turu 1'de 2,5'e
  döndü, eski kol değeriyle aynı), görünür piksel eşiği yine üretimde ölçülür.
- Karelerde renklerin iki temada okunurluğu, karışık yolların algısı: bakılmadı.

## 8. P10.7b2'ye kalanlar

Çizilmeyen 23 kablo (§ 11.3; ilk yazımda 19) için yol / şema; ReSpeaker ses kablosu şeması; karışık sınıflı CAD yollarının (3, 5, 7, 9) devre sınıfına göre
ayrılması; K1 / K2 demet alt adımları; taban yollarının yeniden tasarımı; boyların ölçümü; düğüm tutucusu (bara); boyun tüneli deneme
parçası; K52, K60, K61 kararları gelince metin; Efe'nin iki cevabı (reset DTR / RTS, ReSpeaker 16 kHz) boyun demeti kapanmadan.

## 9. Üretim adımında koşulacaklar (bu adımda koşmadı)

Kural: FreeCAD kilidi (`planlama/d158/FREECAD-KILIT.txt`, son hâli "boş"), boş bellek ≥ 2 GB, F10f / F10g yöntemi (depo dışındaki geçici klasörde
`baslat.ps1` → `sarmal.ps1` 15 s bellek bekçisi → `yokla.ps1`, her koşunun `.durum` kaydı). Zincir **son kod yazımından sonra** başlar.
Önce FreeCAD'siz ön sınama (hepsi çıkış 0 olmalı):

(Açık işler turuna (§ 12) göre yenilendi. Her koşu `-B` ve `PYTHONDONTWRITEBYTECODE=1` ile, `__pycache__` silinmiş; bozma araçları
aynı saniyede yeniden yazılan dosyada eski derlemeyi kullanmasın.)

1. `py -3 -B -X utf8 planlama/adim3/kablolar_uret.py --kontrol` → "güncel"
2. `py -3 -B -X utf8 planlama/adim3/kablolar_denetim.py` ve `--bozma-denemesi` → GEÇER, toplam bozma **145**, GEÇER
3. `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_kablo.py` ve `--bozma-denemesi` → GEÇER, **çizilen 51 / çizilmeyen 23**,
   geometri hata 0 / bilgi 4 (yol 9 ve 12 istisnalı, acil stop düğümü elle bakıldı), ayırt edilemeyen çift 1 (A03 ↔ G22), karşıtlık,
   renk farkı (ΔE00 ≥ 15) ve yarıçap kuralı geçer, onay kaydı (kablo bölümü) tutuyor; bozma **27 / 27**
4. `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py --kaynak` ve `--bozma-denemesi` → metin **531** (+ CAD ad / kod 893,
   arayüz 552), ASCII 0, elektrik 0, zorunlu 0, yasak 0 (istisna 5), çıplak kritik sayı 0, çözülemeyen 0, bozuk yer tutucu 0,
   anahtar-bağlam 0, **onaylı kritik girdi farkı 0** (kayıt metin **907** cümle (531 metnin bütün cümleleri) / liste 133 / kablo 90),
   **tamlık: 65 öğe, eksik 0, muaf 21**, kablo kimliği 68 / 74 (bilgi); bozma **76 / 76** (düzeltme turu 2, § 13)
5. `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_kol_kablo.py --yazma` → GEÇTİ, 38 bölüm
6. Kontrolün bozmaları geçici kopyada (yöntem § 11.4, § 12.6, § 13.5; araç kalıcı değil): ilk kontrolün 28 biçimi, ikinci kontrolün
   B01–B43 (47 biçim) ve üçüncü bakışın N01–N11 (9 biçim) → hepsi yakalanır; onaysız koşuda B09, B24, B25 kaçar (onay kaydı yakalar)

**Onay kaydı zincirde nerede:** adım 4 (`--kaynak`) ve adım 3 (kablo bölümü) ön sınamada; zincirin başında bir kez, üretimden önce.
Kayıt farkı varsa üretim başlamaz. **Düzeltme turu 2:** `rehber_uret.py` bunu artık kendisi de yapar: argümanlar okunur okunmaz
`on_sinama()` `rehber_denetim.kaynak_denetle()`'yi çağırır (onay kaydı ve tamlık dahil); bir sayı sıfır değilse ya da kayıt okunamazsa
"URETIM DURDU" yazıp çıkış 1 verir, FreeCAD ve tarayıcı açılmaz. Bu kod yalnız `py_compile` ile sınandı, koşulmadı: üretim adımında
ilk satırda "on sinama: kaynak denetimi gecti, onay kaydi tutuyor (kablo 90, liste 133, metin 907)" görülmeli. **Yenileme adımı:** bir kritik cümle, kural listesi ya da eşleme / ton tablosu bilerek
değiştiyse `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile` (farkı yazar, kaydı yeniler, "bu değişiklik
bağımsız kontrolden geçmeli" der); yenilenen kayıt ve fark bağımsız kontrole gider, sonra ön sınama baştan koşar. Zincirin kendisi
kaydı asla yenilemez.

Zincir (F10g § 5 sırası; son zincir ≈ 86 dk, `rehber_uret.py` tek başına ≈ 2478 s):

| Sıra | Komut | Beklenen | Neyi doğrular |
| --- | --- | --- | --- |
| 1 | `rehber_uret.py` (FreeCAD'li tam üretim) | çıkış 0; "kablo esleme: GECTI"; parça **1192**, şema **49** (51'den: SEMA 13 → 11), alt adım 71; `kontrol.json` `kablo_esleme.gecti` true, `cizilen` **51**, `cizilmeyen` **23**, `eslesmeyen` boş; `denetim` ELEKTRİK 0 (çeviri tablosu `AD_CEVIRI` uygulanmış; eski terimli çevrilmemiş parça adı / kodu üretimi durdurur); uçuş 340 satır / çarpışan 0 / istisna 16; PDF ≈ 75 sayfa (lejant satırı nedeniyle artabilir: nedeni yazılır) | veri + kareler + PDF yeni kaynaktan; renk / ton / yarıçap tablodan |
| 2 | `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` ve `--bozma-denemesi --veri …` | hata 0 (bugün eski veride 64); veri bozmaları yakalanır | üretilmiş veride renk, tema tonu (`rt`), yarıçap, lejant |
| 2a | **Geometrik eşleme sınaması** (`rehber_kablo.py` içinde, adım 3 ön sınamasıyla aynı koşu; `taban-analiz.json` üretimde yeniden yazılırsa onunla) | hata 0; bilgi yalnız `GEO_ISTISNA` gerekçeli uçlar (bugün yol 9 ve 12) | her CAD yolunun noktaları ↔ eşlenen kabloların uç parçaları (kural § 11.3) |
| 3 | `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py` (veri) | GEÇTİ, elektrik 0, yasak 0, çıplak 0 (bugün eski veride elektrik 55) | üretilmiş metinde elektrik iddiaları, CAD ad / kodları |
| 4 | `planlama/d158/F10f-dogrula.py` | GEÇTİ; `kablo_kare` piksel ölçütü kol yarıçapı değiştiği için izlenir | kol kablo kareleri |
| 5 | `F10e-dogrula.py --goruntu-yok` | renk_demo KALDI (bilinen karar), gerisi geçti; kablo parçalarında renk = veri | parça rengi = veri |
| 6 | `F10d-dogrula.py --goruntu-yok` | geçti; yabancı şema sayısı (SEMA indeksleri kaydı) izlenir | adım / masa şemaları |
| 7 | `F10a-dogrula.py --kanit-yok` | geçti (adım 32 kablo şeması, kablo listesi tıklaması) | panel / kablo satırı |
| 8 | `F9b-dogrula.py` | GEÇER, hata 0 | BOM |
| 9 | `carpisma_kos.py kontrol` | 17 dosya aynı | geometri değişmedi |
| 10 | `regresyon.py --yazma` | GEÇER, bütün değerler aynı | ölçü regresyonu |

**Bakılacak kareler (iki tema):** K1 (adım 17: renk ve lejant, yıldız barası metni), K2 (32: boyun demeti şemaları, 5 kablo), E4 (31:
ses yolu, kaldırılan iki şema), F3 (35: göğüs 12 V), F5 (49: hub, E9 metni), kol kablo adımları G2 / G3 / G4 / H1 (hepsi sarı tel:
bölümler ayırt ediliyor mu), karışık sınıflı CAD yolları 3 / 5 / 7 (9 artık tek sınıf), lejant (açık / koyu), kabloya tıklayınca `kb`
satırları, basılı sayfada lejant satırı. Zor okunanlar sayılır.

**Düzeltme turu 1'in eklediği bakışlar:**

- **Çeviri tablosu (`rehber_metin.AD_CEVIRI`, 5 kalıp):** veride arayüz kartı kodu ve kafa parçaları (USB ses kartı, köpük bant)
  çevrilmiş görünür; `rehber_denetim.py` veri modunda parça ad / kod bulgusu 0.
- **Karşıtlık ve kalınlık:** tema tonları (§ 11.6) iki temada sahnede ve lejantta gözle; koyu temada toprak (siyah sınıf, açık gri
  #b9bec5) ve açık temada sarı / beyaz okunuyor mu; hazır kablo türleri (USB / HDMI / CSI) birbirinden ayırt ediliyor mu; kesit
  kademeleri (2,5 / 3,1 / 3,6 / 4,6) şema ve kol karelerinde gözle seçiliyor mu; taban CAD tüpleri geometri olduğu için 2,5 (fark yok).
  Renk ölçüsü yalnız renk kodlarından; 3B ışıklandırma altında görülmedi.
- **Açık işler turu (§ 12.5):** yeniden tonlanan sekiz ton (koyu toprak #b3b3b3, açık beyaz #4c7078, USB / HDMI / CSI iki temada) ve
  en yakın çiftler (açık siyah ↔ HDMI, beyaz ↔ USB; koyu turuncu ↔ CSI, mavi ↔ HDMI, siyah ↔ beyaz) iki temada gözle; ölçü ΔE00 ≥ 15
  yalnız renk kodlarından. **18 ↔ 16 AWG (3,1 / 3,6 mm):** üretimde iki temada gözle bakılacak; ayırt edilmiyorsa kademe büyütülür.
- **E4 karesi:** USB ses kartı animasyonda köpük bandıyla birlikte PAM8403'ün yanına gidiyor; metin bunun eski tasarımdan kaldığını ve
  uygulanmadığını söylüyor (düzeltme turu 2: köpük bant da cümlede). Karede metinle birlikte okunuyor mu bakılır; kartın desenden
  çıkması P10.7b2.
- **K1 karesi (düzeltme turu 2):** madde 2'de iki bara ayrı cümlede (yıldız 4 siyah, anahtarlı bara 3 kırmızı 12 AWG köprü), madde 8
  köprü listesinde anahtarlı bara, kontrol listesinde iki baranın köprüleri + süreklilik maddesi; panel ve basılı sayfada sığıyor mu.
- **Veri modu (zincir 3):** üretilmiş metinde `{`, `}`, `⟦` kalmaz (`bozuk_yer_tutucu` veri modunda da koşar). Üretilmiş verideki
  kablo tonları (`rt`) yeni tonlarla gelir; bugünkü eski veriyle `rehber_kablo.py --veri` ton farkı verir (beklenen, eski veri).

**Kontrolün "üretim adımında bakılacak" 8 maddesi (`F10h-kontrol.md` § 3) ve bugünkü karşılığı:**

| # | Madde | Bugün | Üretimde beklenen |
| --- | --- | --- | --- |
| 1 | Ü1 düzelmeden veri modu ELEKTRİK ≥ 5, üretim durur | Ü1 düzeldi: eski veriye çeviri benzetimi parça bulgusu 11 → 0 | veri modu elektrik 0 |
| 2 | Ü3 sonrası sayım ≈ 54 / 20 | 51 / 23 (kontrolün sayımına ek olarak geometrik sınamayla G19, B02, Q01, Q02 çizilmeyene, X01 çizilene geçti; § 11.3) | `kontrol.json` 51 / 23 |
| 3 | SEMA dizini 13 → 11: kare adları, yazdırma şema numaraları | kaynakta 11 | elle bakılır |
| 4 | Koyu temada siyah, açık temada sarı / beyaz | tema tonları, en düşük 3,47 | iki temada gözle |
| 5 | Kol yarıçapı 2,1 ile F10f piksel ölçütü | kol 2,5'e döndü | F10f yeniden koşar |
| 6 | K2'de H02, U03, U06 grisi | hazır kablo tür tonları (USB / HDMI / CSI) | K2 karelerinde gözle |
| 7 | Arayüz kartı ve E4 kafa kartlarında "MOSFET" / "USB ses kartı" kalmamalı | `AD_CEVIRI` (USB ses kartı "yedek, takılmaz" adıyla kalır) | kartlarda gözle |
| 8 | `rehber_kol_kablo.py --yazma` 38 bölüm, ≈ 35 s | 38 bölüm, 35 s | aynı |

## 10. C adımında yapılacaklar

- Üretim + zincir (§ 9), kare bakışı; sonuçlar bu günlüğe ve `dongu-158.md` § 5'e.
- § 6 orkestratör maddeleri için karar (özellikle 1); `karar-kuyrugu.md` "P10.7b'nin başında yapılacak" maddelerinin "yapıldı" kaydı
  üretimden sonra kesinleşir.
- Bağımsız bakış (kaynak ↔ tablo tutarlılığı, bozma denemeleri).
- Commit öncesi fark taraması (yerel yol, kişisel veri yok); 14 eski değişik dosya commit'e girmez.

## 11. Düzeltme turu 1 (14.11, bağımsız kontrol `F10h-kontrol.md` DÜZELTME GEREKLİ)

Uygulama ajanı A, kaynak düzeyinde. Bellek kısıtı sürdü: FreeCAD, `rehber_uret.py`, başsız tarayıcı koşmadı; ölçülen kullanılabilir
bellek 1817–1880 MB (1,2 GB durma eşiğine inmedi). Orkestratör onayı: acil stop düğüm kartında tel köprü kabul (§ 6 madde 1); K04
"900 mA" geri alınır, kural daraltılır (§ 6 madde 2). Kontrol raporu değiştirilmedi. Kablo geometrisi, devre değerleri,
`pin-haritasi.md`, CAD parça kaynakları değişmedi.

### 11.1 Ü1: CAD parça adı / kodu çeviri tablosu

- `rehber_metin.AD_CEVIRI`: **5 kalıp** (`tr()`'nin son adımı; her satırda kayıt kaynağı): arayüz kartı kodu "MOSFET + 1N4007" →
  "BC337-40 ×2 (röle sürücüleri; 1N4007'ler rölelerin bobin uçlarında)"; "röle sürücü MOSFET + diyot" → "röle sürücüleri BC337-40 ×2";
  kafadaki parça adı "USB ses kartı" → **"USB ses kartı (yedek, takılmaz)"**, kodu "USB ses kartı (PAM8403 girişi; …)" → "USB ses kartı:
  yedek, takılmaz (KT2 geçmezse Pi port 2'ye; …)", "Köpük bant (USB ses kartı)" → "Köpük bant (yedek USB ses kartının yeri; kart
  takılmaz)". Takılmama kaydı: `kablolama-on-kararlar.md` § 5 Ö1 (siparişte kalır, takılmaz; KT2 geçmezse Pi port 2'ye).
- `rehber_veri.py`: görünen parça adı / kodunda eski elektrik bilgisi kalırsa üretim durur (SystemExit; sessiz geçiş yok).
  `rehber_denetim.kaynak_denetle` CAD ad / kodlarını `tasarim/freecad/montaj/montaj-analiz.json`'dan (FreeCAD'siz) `tr()` ile tarıyor:
  893 metin, bulgu 0 (çevirisiz ham adlarla 4).
- **Benzetim (bugünkü eski `rehber/veri/rehber-veri.json`, bu turun kurallarıyla):** toplam 55 bulgu, parça ad / kod bulgusu 11 (kontrolün
  5 kalıcı CAD bulgusu: E4 parça satırı, p0822 ad, p0823 ad ve kod, p1085 kod; ve eski 6 "Kablo yolu" adı). `AD_CEVIRI` uygulanınca 6,
  güncel `KABLO_AD` adları da konunca **0** (toplam 44: hepsi üretimde yeniden yazılacak eski adım metinleri). Eski kurallarla aynı
  veride 54 (kontrolün ölçümüyle aynı).

### 11.2 Ü2: Ö4 köprüsü

- K1 is_ (madde 5): "Mantar ile düğüm arasında elde taşınan acil stop için ayrılan iki uçlu yer (Ö4; 2 pin 5,08 mm klemens) karar
  verilene kadar kısa bir tel köprüyle kapalı durur; köprü yoksa röle çekmez. Ö4 karar bekliyor (K60)."
- Madde 8: "Mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez (tek köprü madde 5'teki Ö4 yerinde); …"
- K1 kontrol: "Ö4 yerindeki 2 pin klemenste kısa tel köprü takılı (köprü yoksa röle çekmez); ilk enerjide (F1 aşama 1) mantar
  bırakılmışken PC817 #1 ({gpio.ACIL_STOP_DURUM}) LOW okur (HIGH = mantar basılı ya da F5 attı; pin haritası)".
- `ZORUNLU`: "K1 Ö4 yeri köprülü", "K1 köprülenmeyenler"; alan sınaması (K1 kontrol: Ö4 + PC817 #1); cümle sınaması (Ö4 öğesi + köprü
  sözcüğü aynı cümlede); `elektrik_denetle` "Ö4 köprüsüz" kuralı. Kontrolün M28'i yakalandı (§ 11.4).

### 11.3 Ü3: eşleme ve geometrik sınama

- `CAD_ESLEME`: yol 4 = M03, M04 (+ G13: bara → BTS sağ; yol geometrisi destekliyor), M02 çıktı; N01 / N02, B02 yol 12'den çıktı (yol 12
  = B01); S01 / S05 yol 5 / 7'de çizilen; geometrik sınamayla ayrıca G19 (yol 9), Q01 / Q02 (yol 11) çizilmeyene, X01 (yol 11)
  çizilene geçti. **Çizilen 51, çizilmeyen 23:** G06, G07, M02, G16, SV3, G19, G22, B02, N01, N02, I01, I02, P01, P02, P03, Q01, Q02,
  K01, K02, K03, C01, AU1, AU2. Karışık sınıflı yollar 3, 5, 7.
- **Geometrik sınama** (`rehber_kablo.geometri_denetle`, kaynak `tasarim/freecad/taban/taban-analiz.json`: yol noktaları ve parça
  kutuları, FreeCAD istemez): (1) eşlenen her kablonun iki yanı için en az bir uç parçası: modelli taban parçasıysa yol kırık çizgisi
  parçanın kutusuna ≤ 10 mm; taban dışı parçaysa (kafa, kol, gövde) yol taban dışına çıkar (y ≥ 400 mm); modelsiz düğümse sınanmaz
  (bilgi). (2) Yolun iki uç noktası: y ≥ 400 ise eşlenen bir kablonun taban dışı yanı olmalı; değilse ≤ 10 mm'deki modelli parça eşlenen
  kablolardan birinin uç parçası olmalı, yakında parça yoksa eşlenen bir kablonun modelsiz yanı olmalı. Uymayan uç ancak `GEO_ISTISNA`
  gerekçesiyle geçer (bugün yol 9: CAD yolu eski çevre 5 V tasarımını ESP32'ye kadar çiziyor; yol 12: üst kısım 05.11 öncesi ESP32 →
  kafa USB; U06 "ESP32 USB" şemasında). Haritada olmayan uç parçası hata. Bugün: hata 0, bilgi 5. Bozma: yol 4'e M02, yol 12'ye N01 /
  N02, yol 11'e Q01 / Q02, yol 8'e G18 yakalanır. Sınama bugün koşuyor (CAD çıktısı `taban-analiz.json` güncel geometriyle); üretimde
  yeniden koşar (§ 9 satır 2a).

### 11.4 Açık iş 1: kritik değerler yer tutucudan; kontrolün kaçan 20 bozması

- **Çözümleyici** `tasarim/freecad/rehber/rehber_deger.py` (yeni): `kablolar.json`, `pin-haritasi.md` § 9 JSON, `elektrik.md` (sigorta
  listesi, E9) → `{tür.anahtar}`. `rehber_metin` ham metni (`ADIM_HAM`, `KABLO_AD_HAM`, `SEMA_HAM`) saklar, canlı kopyaları çözer;
  çözülemeyen `COZUM_HATA`'ya (bugün boş). `ZORUNLU`, alan ve cümle sınamaları aynı yer tutucularla.
- **Yer tutucular (ham metinde 181):** `a` (sigorta akımı) 59 / 13 anahtar, `awg` 46 / 27, `bicak` (tip) 21 / 8, `gpio` 20 / 4,
  `saplama` 11 / 8, `ohm` 7 / 3, `ms` 7 / 3, `kopru` 3 / 3, `ara` 2, `yuva` 2, `s` 2, `yeniden` 1.
- **Çıplak kritik sayı sınaması** (ham metinde): GPIO N; N A + sigorta bağlamı; N AWG; N Ω / kΩ sürücü / ön şarj bağlamında; N ms / s ön
  şarj / röle bağlamında; "N. yuva" F bağlamında; elle bıçak tipi. Yük / sınır bağlamı muaf değil kural. **Muaf liste (1):** "24 AWG'den
  inceyse" (K04 kesit kuralının eşiği, bir kablonun kesiti değil). Bugün çıplak 0.
- **Kontrolün kaçan 20 bozması** (geçici kopya, her denemede kaynak yeniden yazıldı, `__pycache__` silindi, `--kaynak` ayrı süreçte `-B`;
  20'den 8'i iki biçimde: a çıplak sayı, b yanlış yer tutucu): **28 / 28 yakalandı**, temel ve geri yazılmış kaynak çıkış 0 (özet aynı).

| Kod | Bozma | Yakalayan |
| --- | --- | --- |
| M2 a / b | PC817 #1 → GPIO5 / `{gpio.BARA_DURUM}` | cümle sınaması (PC817 #1 pini); a ayrıca çıplak GPIO |
| M4 a / b | şarj 5 A mini / `{a.hat-C}` | elektrik: şarj hat sigortası tabloda 7,5 A |
| M5 a / b | çevre 5 A mini / `{a.hat-C}` | elektrik: çevre hat sigortası |
| M6 a / b | G22 7,5 A / `{a.hat-A}` | elektrik: G22 algı teli sigortası |
| M7 a / b | F6 "(mini" / `{bicak.hat-A}` | elektrik: kutu sigortası standart bıçak |
| M8 | F6 2. yuva | elektrik: F6 yuvası |
| M9 a / b | XL C 7,5 A / `{a.hat-A}` | elektrik: hat C 5 A |
| M10 | MOSFET + uzak "değil" | elektrik terim (istisna penceresi ± 30 karakter) |
| M11 | WAGO + uzak "yok" | elektrik terim (pencere − 30 / + 40) |
| M13 a / b | G22 16 AWG / `{awg.G16}` | elektrik AWG: G22 tabloda 22 AWG |
| M14 | kafa giriş köprüsü ≥ 22 AWG | elektrik AWG: köprü kesiti kümede değil |
| M15 | sürücü dirençleri yer değiştirmiş | elektrik direnç: seri 270 Ω |
| M17 | K2 1N4007 ters | cümle sınaması (katot bobin + ucunda) |
| M19 | 1N5819 ters (SEMA) | cümle sınaması (SEMA ESP32 USB) |
| M20 | F5'te G22 sigortası silinmiş | zorunlu (F5 G22 sigortası) |
| M21 | K52 kararlaştırılmış gibi | elektrik karar + zorunlu (K52 karar bekliyor) |
| M22 | K61 kararlaştırılmış gibi | elektrik karar (K61) |
| M24 a / b | en az 100 ms / `{ms.k1_sonra}` | elektrik E9: en az 300 ms |
| M27 | tünel kontrol maddesi silinmiş | alan sınaması (K2 kontrol) |
| M28 | Ö4 köprüsüz | zorunlu + cümle sınaması |

- **Yarım kalan / sınırı:** gerilimler (12 V, 6 V, 5 V; 86 yer) ve boylar / ölçüler yer tutucuya çevrilmedi (brief listesinde yok,
  sınaması yok). MOSFET / WAGO istisna penceresi sezgisel: öğeye yakın "değil" / "yok" hâlâ affeder. Cümle sınaması yalnız listelenen
  yön öğeleri için (diyot K1 / K2 / 1N5819, direnç sırası, Ö4, PC817 #1, E9 sırası, F5 K1 → K2).

### 11.5 Kontrolün 15 açık işi (`F10h-kontrol.md` § 2): ne yapıldı

| # | Madde | Ne yapıldı |
| --- | --- | --- |
| 1 | Denetim bağlama bakmıyor (20 / 28 kaçtı) | kritik değerler yer tutucudan, çıplak sayı, bağlam ve cümle kuralları; 28 / 28 (§ 11.4) |
| 2 | `ZORUNLU` sabit metin | desenler yer tutucuyla, çözümleyiciden (`_RDG.degerler().desen`, değerler kaçışlı) |
| 3 | `kaynak_metinler` dar, kaynakta yasak taraması yok | CAD ad / kod (893), `app.js` / `yazdir.html` / `rehber_veri.py` sabit metinleri (≈ 550) ve yasak taraması kaynak modunda |
| 4 | Kol türetilemezse yalnız uyarı | HATA, çıkış 1 (`arayuz` engellenince sınandı: "SONUÇ KALDI (1 hata)") |
| 5 | `CAD_ESLEME` elle | geometrik sınama (§ 11.3) |
| 6 | T8 E / E2 ve K04 kesit yazısı düşmüş | K1 teslim kontrolüne iki madde (K04 için `{yeniden.K04}` = 18 AWG + micro B); `ZORUNLU_ALAN` T8, K04 |
| 7 | KT3 rehberde yok | K1 kontrolüne KT3 süreklilik bakışı ve ayrı girişliyse `{awg.G01}` ara kablolar, yıldız; `ZORUNLU_ALAN` KT3 |
| 8 | F2 15 A yedek yok | F5 is_ ve alt adımda F2 ({a.F2} {bicak.F2}; hiçbir dalı beslemez); çözümleyici `elektrik.md` sigorta listesinden |
| 9 | F5 "uç yuvalar yedek" ↔ "F6 6. yuva" çelişkisi | 1 × 6'da uç iki yuva F2 ve F6'ya (nadiren değişenler), sık değişen F1, F3, F4, F5 ortada; 2 × 3'te altısı açıkta; `ZORUNLU` F5 uç yuvalar |
| 10 | K04 "900 mA" atlatması | "0,9 A varsayım" geri; `kablolar_denetim.py` §2-2 kuralı yük bağlamında (yük / çeker / tüketim / varsayım) sayıyı atlar; bozma `b_sayi_metin_15` (bağlamsız 0,9 A) ve `_16` yakalanır |
| 11 | Yarıçap ayırt edici değil | kademe tablosu (§ 11.6); kol 2,1 → 2,5'e döndü; taban CAD tüpleri geometri (2,5, değişmedi) |
| 12 | Karşıtlık zayıf | tema başına ton (`TEMA_TON`, veride `rt`; koyu temada siyah sınıf açık gri + koyu çekirdekli lejant karesi); tablo § 11.6 |
| 13 | K2'de hazır kablolar aynı gri | hazır kablo türü başına ton: USB, HDMI, CSI (lejantta ayrı girdi) |
| 14 | A04 kesin kaldı | `klemens:` teyit maddesi, durum teyit; sayılar 21 / 52 / 1 (ek kararla K01 de: 20 / 53 / 1, § 11.11) |
| 15 | `dongu-158.md` "62 kablo" | "74 kablo; 62 eski dökümün sayısıydı"; eski veri iddia sayısı kayıtlarda 54 (§ başı, `karar-kuyrugu.md`) |

### 11.6 Görünüm: kalınlık ve karşıtlık (renk kodlarından hesap; kare görülmedi)

- **Yarıçap kuralı** (`rehber_kablo.KESIT_YARICAP`): 22 AWG **2,5**, 18 AWG **3,1**, 16 AWG **3,6**, 12 AWG **4,6** mm. Denetim: en az dört
  kademe, en ince ≥ 2,5 (mevcut kol / şema çizimini inceltmez), komşu kademeler arası fark ≥ % 15. Tabloda olmayan kesit:
  max(2,5; 2,5 + 1,8 × (√mm² − √0,33)); hazır kablo: dış çap şartının yarısı, en az 2,5.
- **Karşıtlık** (WCAG, zeminler `stil.css`: açık sahne #eceae4 / lejant #ffffff, koyu sahne #1b1c20 / lejant #202226; eşik 3,0):

| Sınıf | Açık ton | sahne | lejant | Koyu ton | sahne | lejant |
| --- | --- | --- | --- | --- | --- | --- |
| kırmızı | #c0392b | 4,52 | 5,44 | #ef5a4c | 5,06 | 4,73 |
| turuncu | #b35a00 | 3,99 | 4,80 | #f0903a | 7,10 | 6,64 |
| sarı | #8a6d00 | 4,09 | 4,92 | #e8c020 | 9,72 | 9,10 |
| mavi | #1f6fb8 | 4,34 | 5,22 | #4a9fe8 | 6,01 | 5,63 |
| yeşil | #1e7a3c | 4,47 | 5,38 | #3dbb64 | 6,88 | 6,44 |
| mor | #7d3c98 | 5,87 | 7,07 | #b07fd0 | 5,51 | 5,15 |
| siyah | #222222 | 13,22 | 15,91 | #b9bec5 | 9,11 | 8,52 |
| beyaz | #4e6d7d | 4,58 | 5,52 | #f2f6f7 | 15,65 | 14,64 |
| hazır USB | #7c7c7c | 3,47 | 4,17 | #7d7d7d | 4,14 | 3,87 |
| hazır HDMI | #2f3f4f | 8,98 | 10,80 | #7f9bb5 | 5,88 | 5,51 |
| hazır CSI | #8a5a3c | 4,84 | 5,82 | #c0916c | 6,09 | 5,70 |

  En düşük 3,47 (önce 1,00: siyah koyu lejant; sarı / beyaz açık sahne 1,58). En yakın sınıf çifti ΔE76: açık 16,2 (beyaz / hazır USB),
  koyu 19,1 (siyah / hazır HDMI). Lejant metni: açık 5,74, koyu 5,66 (≥ 4,5). `rehber_kablo.py` kaynak denetimi her sınıfın iki tema
  tonunu ve eşiği sınar; `app.js` ve `yazdir.html` (basılı: açık ton) tonu okur, alan yoksa eski renge düşer.

### 11.7 Doğrulama (FreeCAD'siz; `-B`, `PYTHONDONTWRITEBYTECODE=1`, önbellek silinmiş)

| Komut | Sonuç |
| --- | --- |
| `kablolar_uret.py --kontrol` | güncel, çıkış 0 |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / toplam bozma 138 (ek kararla 139, açık işler turunda 145), GEÇER |
| `rehber_denetim.py --kaynak` | metin 530 (+ CAD 893, arayüz 552), ASCII 0, elektrik 0, zorunlu 0, yasak 0 (istisna 5), çıplak 0, yer tutucu 0; çıkış 0 |
| `rehber_denetim.py --bozma-denemesi` | 42 / 42; bozulmamış kaynakta 0 |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER, 51 / 23, geometri hata 0 / bilgi 5 / 17 / 17 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ, 38 bölüm, 35 s |
| kontrolün 20 bozması (geçici kopya) | 28 / 28 |
| `py_compile` (9 modül), `node --check` (`app.js`, `yazdir.html` betiği) | temiz; dosyalarda denetim karakteri yok |
| eski veri: `rehber_denetim.py` (veri) / `rehber_kablo.py --veri` | elektrik 55 / 64 hata (beklenen; üretimden sonra 0) |

### 11.8 Değişen dosyalar (bu tur)

`planlama/adim3/kablolar.json` (K04 notu, A04 teyit), `kablolar.md` ve `elektrik.md` bloğu (üretildi), `kablolar_denetim.py`;
`tasarim/freecad/rehber/rehber_deger.py` (yeni), `rehber_metin.py`, `rehber_denetim.py`, `rehber_kablo.py`, `rehber_veri.py`,
`rehber_uret.py`; `rehber/app.js`, `rehber/yazdir.html`; bu günlük, `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md`. Rehber
çıktıları üretilmedi, elle düzenlenmedi.

### 11.9 Orkestratöre

1. G13 yol 4'e eklendi (D1 kararında yoktu; geometri ve tablo destekliyor).
2. Yol 9 ve 12 `GEO_ISTISNA`: CAD yollarının bir kısmı eski tasarımı çiziyor; geometri P10.7b2'de düzelince istisnalar düşmeli.
3. U06 yol 12'den çıktı (yalnız "ESP32 USB" şemasında).
4. A04 teyite geçti; K01 (`klemens-508` + lehim) hâlâ kesin: aynı ölçüt uygulanmalı mı?
5. USB ses kartı CAD'de E4 adımında yerinde duruyor (rehberde "yedek, takılmaz" adıyla): adımdan çıkması isteniyor mu (CAD kaynağı
   değişir)?
6. MOSFET / WAGO istisna penceresi sezgisel (§ 11.4).
7. Geometrik sınama bugün CAD çıktısı `taban-analiz.json` ile koşuyor; taban yeniden üretilirse onunla.

### 11.10 Doğrulanamayanlar

Üretilmiş veride çeviri, ton, yarıçap ve geometri (eski veri ve benzetimle sınandı); iki temada 3B ışıklandırma altında karşıtlık ve
kesit kademelerinin gözle seçilmesi; F10f piksel ölçütü; PDF sayfa sayısı.

### 11.11 Ek kararlar (orkestratör, düzeltme turu 1 kabulünden sonra)

- **K01 teyite:** kural tek cümle (`kablolar_denetim.py` `s_klemens`): ucu `klemens-508` olan ve klemensin aldığı kesit belgeyle
  doğrulanmamış (`klemens_turleri.klemens-508.en_cok_mm2` boş) her kablo "kablajda teyit"; öbür ucun lehim olması bunu değiştirmez.
  Tablo tarandı: klemens-508 uçlu 11 kablo (SV1, SV2, SV3, G17, G19, A02, A03, A04, A05, K01, K02); K01 dışında
  hepsi zaten teyitteydi, başka geçen kablo yok. K01'e A04'teki gibi `klemens:` teyit maddesi; durum **20 / 53 / 1**. Bozma
  `b_klemens_19` (K01 elle "kesin", teyit boş) yakalanır; kural eklenince değişiklikten önceki tablo da K01'de hata verdi.
- **E4 metni:** is_ madde 1 ve "Masada: sol arka kabuk" alt adımı: "USB ses kartı bu adımda takılmaz: çizimde PAM8403'ün yanında
  görünen yeri boş kalır, kart yedek olarak kutuda durur (KT2 geçmezse Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5
  Ö1)." CAD kaynağı değişmedi; parçanın modelden / adımdan çıkması P10.7b2'de (`karar-kuyrugu.md`).
- **Yol 9 ve 12 istisnaları** kalır; geometri P10.7b2'de düzelince kalkar (`karar-kuyrugu.md`). G13 yol 4'te, U06 kabul: değişiklik yok.
- **Açık iş (kontrol sınayacak):** MOSFET / WAGO istisna penceresi sezgisel (öğenin ± 30 / − 30 … + 40 karakterindeki "değil" / "yok"
  affeder; § 11.4).
- **Koşular (14.11 10:21 sonrası, `-B`, önbellek temiz):** `kablolar_uret.py --kontrol` güncel; `kablolar_denetim.py` GEÇER, bozma 139 GEÇER;
  `rehber_denetim.py --kaynak` hepsi 0 (ASCII sözlüğüne "kutuda" eklendi), bozma 42 / 42; `rehber_kablo.py` GEÇER, 51 / 23, geometri
  hata 0. Değişen: `kablolar.json` (K01), `kablolar.md` / `elektrik.md` bloğu (üretildi), `kablolar_denetim.py`, `rehber_metin.py`
  (E4), `rehber_denetim.py` (ASCII), bu günlük, `dongu-158.md`, `karar-kuyrugu.md`.

## 12. Açık işler turu (14.11, ikinci bağımsız kontrol `F10h-kontrol-2.md` KAYNAK GEÇER, 20 açık iş)

Uygulama ajanı A, kaynak düzeyinde, orkestratörün D2 kararlarıyla. Bellek kısıtı sürdü: FreeCAD, `rehber_uret.py`, başsız tarayıcı
koşmadı; ölçülen kullanılabilir bellek 1587–1745 MB (1,2 GB eşiğine inmedi). Kontrol raporları, CAD kaynakları, kablo geometrisi,
`kablolar.json` devre değerleri, `pin-haritasi.md`, `kod/`, `main` değişmedi; rehber çıktı dosyalarına elle dokunulmadı.

### 12.1 Onaylı kritik metin kaydı (kalıcı korunma)

- **Dosya:** `tasarim/freecad/rehber/rehber_kritik_onay.json` (izlenir), modül `rehber_kritik.py` (yalnız standart kitaplık).
  Her girdi: yer (adım + alan / liste adı), ham metnin özeti (sha256, ilk 16 hane; boşluk normalleştirilmiş, yer tutucular
  çözülmeden), ilk 60 karakter, neden. Bugün **528 girdi**: metin **319** (yer tutucu geçen, bir ZORUNLU / ZORUNLU_ALAN /
  ZORUNLU_CUMLE deseniyle çakışan ya da `KRITIK_SOZ` taşıyan her cümle: sigorta, akü, gerilim, köprü, katot / anot, GPIO, röle,
  mantar, ölç-, "karar bekliyor" / "karar verilene", K5x / K6x, Ö4, MOSFET / WAGO / ses kartı, takılmaz …), liste **119** (ZORUNLU,
  ZORUNLU_ALAN, ZORUNLU_CUMLE, TERIM_ISTISNA, CIPLAK_MUAF, CIPLAK_KURAL, YASAK maddeleri tek tek; CIPLAK_YUK, CIPLAK_YUK_DEGIL,
  OLUMSUZLAMA, KRITIK_SOZ, CIPLAK_MUAF_SAYI), kablo **90** (`rehber_kablo.kritik_tablolar()`: CAD_ESLEME, GEO_DAL, GEO_ISTISNA,
  PARCA_CAD, MODELSIZ_KONUM, taban dışı bölgeler, KOL_ESLEME, KESIT_YARICAP, TEMA_TON, eşikler).
- **Sınama:** `rehber_denetim.py --kaynak` bugünkü kaynağı kayıtla karşılaştırır (yer başına sıra korunarak); değişen, silinen ya da
  eklenen kritik girdi HATA, satırı "KRITIK değişti / silindi / eklendi", eski hâlin ilk 60 karakteri ve yeni hâlin metni. Kayıt yoksa
  da HATA. `rehber_kablo.py` ana koşusu ve `--bozma-denemesi` aynı kaydın kablo bölümünü ayrı mekanizma olarak sınar.
- **Yenileme:** yalnız `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile`; önce farkı yazar, sonra
  kaydı yazar ve "bu değişiklik bağımsız kontrolden geçmeli" uyarısını basar. Olağan koşu kaydı asla yazmaz.
- **Ne kanıtlar, ne kanıtlamaz:** kayıt metnin doğru olduğunu kanıtlamaz (onu bağımsız kontrol yapar); kritik bir cümlenin,
  kuralın ya da eşleme tablosunun sessizce değişmesini imkânsız kılar. Bugünkü kayıt = ikinci kontrolün doğru bulduğu metin + bu
  turun aşağıdaki değişiklikleri (§ 12.4) + bu turun kural ve tablo değişiklikleri (§ 12.2, § 12.3, § 12.5). Bu yüzden bu tur da
  bağımsız kontrolden geçmeli.

### 12.2 Yer tutucu ve çıplak sayı kuralları

1. **Bozuk yer tutucu:** çözülmüş metinde `{`, `}`, `⟦`, `⟧` kalırsa HATA (`bozuk_yer_tutucu`; kaynak modunda ve veri modunda).
   Çözülemeyen yer tutucu `⟦?…⟧` olarak kaldığından o da buraya düşer.
2. **Anahtar ↔ bağlam (`baglam_denetle`, `rehber_deger.varlik_adlari`):** her yer tutucunun (grupsa her üyenin) gösterdiği varlığın
   adı aynı cümlede geçmeli; adlar tablodan türer (kablo kimliği; koruyucunun F etiketi / hat adı ve koruduğu kabloların kimlikleri;
   GPIO'nun pin haritasındaki ucu (K1 / K2, BC337-40 #n, PC817 #n) ve pin adının parçaları; `ohm` / `ms` / `s` / `kopru` /
   `saplama` için küçük ad tablosu). Kimlik aralıkları ("G01–G04") açılır; yer tutucunun kendi metni ad sayılmaz. Ölçüm: bugünkü
   kaynakta **184** yer tutucu (181 + bu turun grupları); kural ilk koşuda 14 cümlede alarm verdi, hepsi kablo / sigorta adının
   cümlede yazmamasıydı, anlam değiştirmeden düzeltildi (§ 12.4'teki K1 madde 1, Yerleşim saplamaları, K1 madde 3, madde 5,
   K1 kontrol ana hat, Teslimde, KT3, E3a K01, K2 kontrol uzatmalar, F5 / F1 G22, F5 not_ PC817 #2, F5 `ms.k1_sonra`). Bugün **0**.
   Sınır: iki varlığın birlikte geçtiği cümlede yer değiştirme (B09: `{gpio.BARA_DURUM}` ↔ `{gpio.ACIL_STOP_DURUM}`) bu kuralla
   yakalanmaz; onu onay kaydı yakalar.
3. **Türkçe duyarlı küçük harf** (`rehber_kritik.tr_kucuk`: İ → i, I → ı; büyük harf Latin kısaltma GPIO / I2C İngilizce kuralla).
   Çıplak sayı karşılaştırmaları küçük harf metinde.
4. **Birimler:** mA, kA, mΩ, kΩ, MΩ, "ohm"; ondalık virgül / nokta; sayı ile birim arasında boşluk, dar / bölünmez boşluk, satır
   sonu (`_bosluk`); sözle yazılmış değer (Türkçe sayı sözcüğü + amper / A / ohm / AWG) kritik bağlamda HATA. Yeni kural: bara
   saplamasının sırası ("(4.) saplama") çıplaksa HATA (B13).
5. **Yük muafiyeti daraltıldı:** sayı yalnız kendi yan cümlesinde yük / çeker / tüketim / varsayım geçiyor VE sigorta / F<n> / koruma
   / bıçak / mini / standart geçmiyorsa muaf. "sürekli", "anma", "ölç", "sınır" muafiyetten çıktı. Yan cümle bölmesi (`YAN_CUMLE`)
   ondalık virgülde bölmez ("0,9 A varsayım" bütün kalır).
6. **MOSFET / WAGO / ses kartı:** pencere ve sözcük affı kalktı; terim geçen cümle yalnız `TERIM_ISTISNA`'daki **12** tam cümleyle
   (boşluk normalleştirilmiş) geçer. Brief beş cümle bekliyordu; on iki oldu çünkü CAD ad / kod çevirileri ve `;` ile bölünen
   parçalar da ayrı cümle: "WAGO yok", K1 saplama cümlesi "(WAGO yok)", "Seçenek: kollu WAGO 221-413 …", E3a "USB ses kartı
   kablajdan çıktı: yedek, takılmaz;", E4 is_ "USB ses kartı takılmaz: çizimde ve animasyonda …;", E4 kontrol, E4 not, "Masada: sol
   arka kabuk + PAM8403 (USB ses kartı yedek, takılmaz)", "eski şema ses kartından çiziliyordu, kaldırıldı).", CAD köpük bant adı,
   CAD kart adı, CAD kart kodu. Liste onay kaydında.
7. **ZORUNLU tam sözcük:** desen tam sözcükle başlar ve biter (`(?<!\w)…(?!\w)`), olumsuzluk eki sözcüğü uzatınca tutmaz ("tak" ↔
   "takma"). F3 F6 deseni fiili de içerir ("yuvası) tak", B27); E3a deseni "kaynağıyla" oldu (tam sözcük); SEMA 12 V'ye ZORUNLU_CUMLE
   "regülatör yeri karar bekliyor, K52" (B28).
8. **K52 / Ö4:** iki kural onay kaydına bağlı (cümleleri ve kuralların kendisi kritik girdi). Ö4 kuralında "çekmez" affı kalktı.
9. **Muaf listesinin uzunluğu:** `CIPLAK_MUAF_SAYI = 1`; listede başka sayıda madde varsa `--kaynak` HATA (`muaf_denetle`, B33).

### 12.3 Kablo tablosu ve eşleme

- **Madde 10 (`kablolar_denetim.py` `s_sayi_metin`):** aynı dar yük kuralı (`YUK_SOZ`, `YUK_DEGIL`, `_yan_cumle`, Türkçe duyarlı küçük
  harf). Ek kural: muaf yük akımı kablonun zincirindeki en küçük koruyucuyu aşamaz (aşan yük sigortayı attırır). Kontrolün 8 denemesi
  (K1–K8) bellekte: **8 / 8** yakalandı (K3 "Şarj kolu 10 A (yük varsayımı)" bu ek kuralla: zincirde 7,5 A); `--bozma-denemesi`'ne
  `b_sayi_metin_17` … `_22` olarak girdi.
- **Madde 11 (`rehber_kablo.geometri_denetle`):**
  - Dal (yol 4) kendi noktalarıyla ve ana yolun yalnız ayrılma noktasına kadarki bölümüyle sınanır; ana yolun ayrılmadan sonraki kolu
    (BTS sol, sol motorlar) dala sayılmaz. Brief "yalnız kendi noktalarıyla" diyor; kelimesi kelimesine uygulanınca kontrolün doğru
    bulduğu G13 (bara → BTS sağ) düşüyor, çünkü baranın yerine geçen röle kutusu dalın değil ana yolun gövdesinde (yol 3 noktası
    (-112; 226; -130)). Bu yüzden "kendi yolu" = dal + gövde; ayrılmadan sonraki kol hariç.
  - **Taban dışı bölgeler** (`TABAN_DISI_BOLGE`; kaynak `montaj/montaj-analiz.json` parça merkezleri, ev pozu, global mm):

    | Bölge | x | y | Dayanak |
    | --- | --- | --- | --- |
    | kafa | −60 … 60 | 1200 … 1600 | kafa modülü x −134…134, y 1283…1578 (Govde grubu x −40…40, y 1283…1368); boyun geçişi eksende, yol 6 başı (0; 1215) |
    | sağ kol | 60 … 260 | 880 … 1320 | omuz_sag x 86…191, y 1165…1305; dirsek_sag x 162…228, y 899…1119 |
    | sol kol | −260 … −60 | 880 … 1320 | sağın x aynası |
    | gövde | −260 … 260 | 400 … 1280 | kabuk x −259…259, y 60…1268 (USB hub (48; 1121)) |

    Uç noktası sırayla ilk tutan bölgeye düşer; parça → bölge `TABAN_DISI_PARCA` ("Sağ kol …", "Sol kol …", "Kafa …" / "(kafa)",
    "USB hub"); bölgesiz taban dışı uç HATA.
  - **Modelsiz parça → nominal konum / yerine geçen parça** (`MODELSIZ_KONUM`; noktalar `taban_parcalar.py` YOL tanımlarından):

    | Parça (kutup) | Nominal nokta | Yerine geçen (yol ucu komşusu) | Gerekçe |
    | --- | --- | --- | --- |
    | XT60 akü / robot tarafı (+) | (−65,5; 133; −29) | akü kutusu | modeli yok, akü kablosunun ucunda; yol 1 başı "aku + -> XT60" |
    | XT60 akü / robot tarafı (−) | (65,5; 133; −29) | akü kutusu | yol 2 başı "aku - -> WAGO yildiz noktasi" |
    | Yıldız barası | (−20; 186; −90) | yok | güç panelindeki yıldız noktası; yol 2 sonu; yanında modelli parça yok |
    | Anahtarlı bara | yok | Röle K1 kutusu | modeli yok; CAD yolları "role -> WAGO"; röle ↔ bara ayırt edilmez |
    | Acil stop düğümü | yok | yok | pertinaks kart, CAD'de ne model ne nokta (yerleşim P10.7b2): sınanmaz, "elle bakıldı" bilgisi |

    Kutup ucun `nokta` alanından ("+" / "−"), iki damarlı uçta ilk damardan.
  - **Ayırt edilemeyen çiftler** (`ayirt_edilemeyen()`, ana koşu yazar): uç imzası (sınıf / desen, nominal nokta, bölge) aynı olup aynı
    yolda eşli olmayan çift bugün **1**: yol 10 A03 (Röle K1 → arayüz kartı) ↔ G22 (anahtarlı bara → PC817, çizilmeyen). Kontrolün G6'sı
    budur; geometri ayıramaz, `CAD_ESLEME` onay kaydı yakalar.
  - Kontrolün 18 G bozması (`geo_dok.py` kopyası, `geometri_denetle` doğrudan): **17 / 18** geometriyle (G1, G3 dal; G4 bölge; G7, G8
    nominal kutup), G6 yalnız onay kaydıyla (rehber_kablo `--bozma-denemesi` b23: "onaylı kablo tablosu değişti: CAD_ESLEME 10"). Temel
    koşu hata 0, bilgi 4 (yol 9 / 12 istisna; A04 / A06 acil stop düğümü elle bakıldı).
  - **Yapılamayan:** acil stop düğümünün nominal yeri (CAD'de yok); Röle K1 ↔ anahtarlı bara ayrımı (bara modeli yok); XT60 kutup
    noktaları CAD yolunun kendi baş noktalarından geldiği için yol 1 / 2'nin başını kayıt dışı biri değiştirirse noktalar da birlikte
    kayar (onay kaydı `MODELSIZ_KONUM` değişikliğini yakalar, `taban-analiz.json` değişikliğini değil); gövde bölgesi geniş (dikey her
    yol içinden geçer), USB hub uçlu kablo bugün eşli değil.
- **Madde 16 (grup yer tutucu):** `{tür.K1|K2|…}` her üyeyi çözer, değerler farklıysa çözülemez (`⟦?…⟧`, HATA). Gruplar: ana hat
  G01–G04, G01–G05, A01–A05, A01 / A02, G14–G16, hat-A / hat-B, G08 / G09, S01–S10 ve beş saplama grubu. Bozma (geçici kopya,
  `kablolar.json`): G15 18 AWG → "BOZUK YER TUTUCU … ⟦?awg.G14|G15|G16⟧", çıkış 1; A02 16 AWG → "⟦?awg.A01|A02|A03|A04…", çıkış 1.

### 12.4 Metin değişiklikleri (eski → yeni, `tasarim/freecad/rehber/rehber_metin.py`)

| Yer | Eski | Yeni |
| --- | --- | --- |
| :252 K1 madde 1 | "Ana hat ({awg.G01}; G01–G04)" | "{awg.G01\|G02\|G03\|G04}" (grup) |
| :261-262 Yerleşim | saplama başına ilk kablonun yer tutucusu | `{saplama.G12\|G14\|G15}`, `{saplama.G13\|G16}`, `{saplama.G05\|G06}`, `{saplama.G17\|G18}`, `{saplama.G20\|G22}` |
| :264-265 K1 madde 3 | "({a.hat-A}; G14, G15)", "{awg.G16}" | "({a.hat-A\|hat-B}; G14, G15)", "{awg.G14\|G15\|G16}" |
| :271 K1 madde 5 | "(yeşil, {awg.A01}; E3, E9)" | "(yeşil, A01–A05 {awg.A01\|A02\|A03\|A04\|A05}; E3, E9)" |
| :277-279 Ö4 (madde 15) | "… karar verilene kadar kısa bir tel köprüyle kapalı durur; köprü yoksa röle çekmez." | "… karar verilene kadar zincirin kendi teliyle (A01, A02) aynı kesitte ({awg.A01\|A02}) kısa bir tel köprüyle kapalı durur; köprü yoksa röle çekmez." |
| :286-288 madde 8 (madde 13) | "Mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez (tek köprü madde 5'teki Ö4 yerinde); akü XT60 ayrık kalır," | "Bu adımda köprü yalnız şu yerlerde takılır: Ö4 yerindeki kısa tel köprü (madde 5), acil stop düğüm kartındaki (A02, A04) {kopru.A02} tel köprü (madde 5), yıldız barasının saplamaları arasındaki {kopru.yildiz} köprü (madde 2) ve KT3 bakışında kutu ayrı girişli çıkarsa yuva girişlerine giden ara kablolar (kontrol listesi). Bunların dışında mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez; akü XT60 ayrık kalır," |
| :305 K1 kontrol Ö4 | "… kısa tel köprü takılı (köprü yoksa röle çekmez);" | "… kısa tel köprü takılı (A01 / A02 ile aynı kesit, {awg.A01\|A02}; köprü yoksa röle çekmez);" |
| :310 K1 kontrol | "{awg.G01} düğümler yalnız …" | "Ana hat ve toprak düğümleri (G01–G05, {awg.G01\|G02\|G03\|G04\|G05}) yalnız …" |
| :312-313 Teslimde | "({a.hat-cevre}, {a.hat-sarj})" … "{awg.G09}'ye eklendi" | "(çevre {a.hat-cevre}, şarj {a.hat-sarj})" … "G08 / G09'un {awg.G08\|G09} teline eklendi" |
| :322 KT3 | "… olabildiğince kısa {awg.G01} ara kablo" | "… olabildiğince kısa, kutunun giriş kablosuyla (G04) aynı kesitte {awg.G04} ara kablo" |
| :458 E3a | "{kopru.K01} tel köprüyle lehimli" | "{kopru.K01} tel köprüyle (K01 sonlandırması) lehimli" |
| :518-520 E4 is_ madde 1 ve :587-589 alt adım (madde 12) | "USB ses kartı bu adımda takılmaz: çizimde PAM8403'ün yanında görünen yeri boş kalır, kart yedek olarak kutuda durur (KT2 geçmezse …)" | "USB ses kartı takılmaz: çizimde ve animasyonda kart PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan görüntüdür, uygulanmaz. Kartın köpük bandı da yapıştırılmaz; kart yedek parçalarla birlikte saklanır (KT2 geçmezse Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1)." |
| :1582 `AD_CEVIRI` köpük bant | "… yedek USB ses kartının yeri; kart takılmaz" | "Köpük bant (yedek USB ses kartı için; kart takılmaz, bant yapıştırılmaz)" |
| :671 K2 kontrol | "Uzatma: … {awg.S01} … (silikon {awg.S01} sığmaz)" | "Uzatmalar (S01–S10): ince duvarlı PVC düz {awg.S01\|S02\|…\|S10}, damar ≤ 1,5 mm; kumpasla ölç (aynı kesitte silikon tel sığmaz)" |
| :721 F1 kontrol, :1352 F5 is_ | "PC817 #2 algı telinin {a.hat-G22} …" | "PC817 #2 algı telinin (G22) {a.hat-G22} …" |
| :1362-1363 F5 (madde 14) | "(K2 devreye almadan {ms.k1_sonra} sonra zaten bırakıldı)" | "(K2, devreye alma sırasında K1 çektikten {ms.k1_sonra} sonra zaten bırakılmıştı; E9 adım 5)" |
| :1389 F5 not_ | "{gpio.BARA_DURUM}'in LOW olması" | "PC817 #2'nin ({gpio.BARA_DURUM}) LOW olması" |

Köpük bandın başka işi yok: CAD'de "Köpük bant (USB ses kartı)" yalnız karta ait; PAM8403'ün kendi köpük bandı ayrı parça ("Köpük
bant (PAM8403)"), metni değişmedi. Metinle birlikte ZORUNLU desenleri, `TERIM_ISTISNA` ve ASCII sözlüğü güncellendi ("kutuda" çıktı;
8 yeni kelime: zincirin, teliyle, kesitte, yerlerde, kablosuyla, animasyonda, gidiyor, uygulanmaz).

### 12.5 Görünüm (madde 17, 18)

- **Renk farkı:** CIEDE2000 (ΔE00; sRGB → XYZ D65 → CIELAB, kL = kC = kH = 1; Sharma 2005 sınama çiftleriyle doğrulandı), lejantın her
  satırı aynı temadaki her satırla. **Eşik ΔE00 ≥ 15** (`RENK_FARK_ESIK`): ΔE00 ≈ 1 yan yana görülen en küçük fark, 2–10 "dikkatle
  bakınca", 10'un üstü "bir bakışta ayrı"; tel 3B sahnede ince (r 2,5–4,6 mm), gölgeli, yan yana değil; renk körlüğü payı yok. 15,
  ana sınıfların tonlarına dokunmadan ulaşılabilen en yüksek yuvarlak eşik. `kaynak_denetle` eşik altını HATA sayar.
- **En yakın 5 çift, önce → sonra:**

  | Tema | Önce (ΔE00) | Sonra (ΔE00) |
  | --- | --- | --- |
  | açık | mavi ↔ beyaz 11,8; turuncu ↔ CSI 12,4; siyah ↔ HDMI 12,9; beyaz ↔ USB 14,1; kırmızı ↔ CSI 15,7 | siyah ↔ HDMI 15,3; beyaz ↔ USB 15,9; kırmızı ↔ turuncu 17,1; mavi ↔ beyaz 17,4; kırmızı ↔ CSI 18,0 |
  | koyu | mavi ↔ HDMI 9,8; turuncu ↔ CSI 12,2; siyah ↔ beyaz 13,2; siyah ↔ HDMI 14,2; USB ↔ HDMI 15,7 | turuncu ↔ CSI 15,1; mavi ↔ HDMI 15,3; siyah ↔ beyaz 15,7; siyah ↔ USB 15,9; USB ↔ CSI 18,4 |

- **Değişen tonlar:** açık beyaz #4e6d7d → #4c7078, USB #7c7c7c → #828282, HDMI #2f3f4f → #1d3854, CSI #8a5a3c → #6f3312; koyu siyah
  #b9bec5 → #b3b3b3, USB #7d7d7d → #818181, HDMI #7f9bb5 → #5ba7b8, CSI #c0916c → #b2916b. Ana sınıflar (kırmızı, turuncu, sarı,
  mavi, yeşil, mor ve iki temada beyazın koyu tonu) değişmedi. **En düşük karşıtlık 3,19** (açık USB, sahneye; önce 3,47), eşik 3,0.
  Kontrolün ΔE76 sayıları ölçek farkıyla aynı sıralamayı veriyor.
- **18 ↔ 16 AWG:** kademe (3,1 / 3,6 mm, %16) olduğu gibi; § 9'a gözle bakış notu girdi. Renk tonları da üretimde bakılacaklarda kalır.

### 12.6 Bozmalar (geçici kopyada, depo dışında; `-B`, önbellek temiz; kontrolün klasörüne yazılmadı)

Kontrolün `bozma.py`'si kopyalandı, bu turda metni değişen 10 bozmanın (B02, B06, B08, B31, B32, B35, B36, B38, B38b, B41) "eski"
dizgesi aynı bozmayı bugünkü metne uygulayacak biçimde uyarlandı. İki koşu: (a) olağan (onay kaydı etkin); (b) "onaysız": kayıt her
bozmayla birlikte yenilenir, onay dışındaki mekanizma görünür. Sonuç: (a) **47 / 47**, (b) **44 / 47**.

| Kontrolün kaçan 24'ü | Onaysız yakalayan | | Kontrolün kaçan 24'ü | Onaysız yakalayan |
| --- | --- | --- | --- | --- |
| B06 A01 → A06 kesit | bağlam | | B24 Touch sırası ters | **yalnız onay** |
| B07 saplama G17 | bağlam | | B25 regülatör sırası ters | **yalnız onay** |
| B08 ms.onsarj_bos | bağlam | | B26 G22 "takma" | ZORUNLU tam sözcük |
| B09 BARA ↔ ACIL_STOP GPIO | **yalnız onay** | | B27 F6 "takma" | ZORUNLU (fiil desende) |
| B10 ohm.seri ↔ taban | bağlam | | B28 K52 silindi (SEMA) | ZORUNLU_CUMLE |
| B11 "Ön şarj (5,6 Ω)" | çıplak (Türkçe küçük harf) | | B29 MOSFET + "değil" | terim tam cümle listesi |
| B13 "(4.) saplama" | çıplak (saplama sırası) | | B30 WAGO + "yok" | terim tam cümle listesi |
| B15 5000 mA | çıplak (mA) | | B33 muafa madde | muaf sayısı |
| B16 0,005 kA | çıplak (kA) | | B34 "sürekli 7,5 A" | çıplak (dar yük) |
| B18 satır sonu + {a.F1} | bağlam | | B35 hat-sarj → hat-A | bağlam |
| B20 {A.F6} | bozuk yer tutucu | | B36 KT3 G01 → G06 | bağlam |
| B21 {a. F6} | bozuk yer tutucu | | B14b "dört buçuk A" | çıplak (sözle) |

Onaysız kaçan üçü: B09 (iki varlık aynı cümlede, bağlam kuralı yer değiştirmeyi görmez), B24 / B25 (sıra tersine çevrildi; cümle
ZORUNLU öğesi değil, anlamı okumadan sınanamaz). Üçünü de onay kaydı yakalar ("KRITIK değişti metin kaynak F5 is_ / E4 is_ / K2 is_").
B22 (kablolar.json'da `hat-G22` adı değişti) denetimin çökmesiyle (traceback, çıkış 1) yakalanıyor, ilk kontroldeki gibi; düzgün
hata iletisi yok (öneri, bu turda yapılmadı). Kontrolün 6 G bozması: G1, G3, G4, G7, G8 geometriyle, G6 onayla (§ 12.3). Kontrolün
5 K bozması: 5 / 5 (§ 12.3).

Kalıcı bozma sayıları: `rehber_denetim.py --bozma-denemesi` **65 / 65** (elektrik 34, çıplak 20, açık iş 11; yeni:
B29 / B30 / B38b terim ve Ö4, çıplak B11 / B13 / B15 / B16 / B14b / satır sonu / B34 / yük + sigorta / ondalık yük (yakalanmamalı),
bozuk yer tutucu B20 / B21, bağlam B01 / B05 / B07 / B08, grup, zorunlu tam sözcük F5 / F3, muaf sayısı, onay); `rehber_kablo.py
--bozma-denemesi` **27 / 27** (yeni b18–b27: G1, G3, G4, G7, G8, G6, üç eski ton, nominal nokta); `kablolar_denetim.py
--bozma-denemesi` toplam **145**, GEÇER (yeni `b_sayi_metin_17` … `_22`).

### 12.7 Kontrolün 20 açık işi: ne yapıldı / neden yapılmadı

| # | İş | Ne yapıldı |
| --- | --- | --- |
| 1 | Bozuk yer tutucu sessiz | çözülmüş metinde `{ } ⟦ ⟧` HATA (kaynak + veri modu); B20 / B21 yakalanıyor |
| 2 | Aynı türden yanlış anahtar | anahtar ↔ bağlam kuralı (184 yer tutucu, 14 alarm düzeltildi → 0) + onay kaydı; B09 yalnız onayla |
| 3 | Çıplak sayı büyük harf | Türkçe duyarlı küçük harf (`tr_kucuk`) |
| 4 | Birim / satır atlatma | mA, kA, mΩ, kΩ, MΩ, ohm, boşluk / satır sonu, sözle değer |
| 5 | Yük muafiyeti geniş | dar kural (§ 12.2-5); "sürekli", "anma", "ölç", "sınır" çıktı |
| 6 | MOSFET / WAGO pencereleri | pencere kalktı; 12 tam cümle listesi, onay kaydında |
| 7 | ZORUNLU ön ek eşleşmesi | tam sözcük + F3'te fiil desende |
| 8 | Açık karar / Ö4 sözcük affı | Ö4 "çekmez" affı kalktı; K52 / Ö4 onay kaydına bağlı; SEMA 12 V K52 ZORUNLU_CUMLE |
| 9 | Muaf listesini sınayan yok | `CIPLAK_MUAF_SAYI` sınaması + onay kaydı |
| 10 | Kablo tablosunda yük daraltması | aynı dar kural + "yük zincirin sigortasını aşamaz"; K1–K8 8 / 8 |
| 11 | Kaçan eşleme yanlışları | dal gövdesi, bölgeler, nominal konum tablosu, ayırt edilemeyen çiftler; G 17 / 18 geometri + G6 onay |
| 12 | E4 çizim ↔ metin | metin: animasyondaki yer eski tasarımdan, uygulanmaz; köpük bant yapıştırılmaz; "kutuda" kalktı. Kartın E4 deseninden çıkması CAD / sıra tarafı (P10.7b2, kuyrukta), bu turda yapılmadı (CAD kaynağı yasak) |
| 13 | "tek köprü" | bu adımda takılan köprülerin açık listesi + "bunların dışında … köprülenmez" |
| 14 | F5 parantezi | tek anlamlı cümle (E9 adım 5) |
| 15 | Ö4 köprü teli kesiti | zincirin teliyle aynı kesit, `{awg.A01\|A02}`; K60'a not; `kablolar.json` değişmedi |
| 16 | Tek anahtar çok kablo | grup yer tutucu, üyeler farklıysa HATA; bozma 2 / 2 |
| 17 | Renk uzaklığı ölçülmüyor | ΔE00 çift sınaması, eşik 15, 8 ton değişti, en düşük karşıtlık 3,19; üretimde gözle bakış kaldı |
| 18 | 18 ↔ 16 AWG adımı %16 | kademe aynı (orkestratör kararı); § 9'a gözle bakış notu |
| 19 | `dongu-158.md:190` bozma sayısı | gerçek tur sonu sayıları yazıldı (`dongu-158.md` § 4 P10.7 satırı ve § 5 günlük girdisi) |
| 20 | `kablolama-on-kararlar.md:92` | dokunulmadı (o günün anlatımı; aynı paragraf F6'yı 6. yuvaya koyuyor); not yalnız burada |

### 12.8 Doğrulama (14.11 11:00–11:25, `-B`, `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` silinmiş)

| Komut | Sonuç |
| --- | --- |
| `kablolar_uret.py --kontrol` | kablolar.md ve elektrik.md bloğu güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / toplam bozma 145, GEÇER |
| `rehber_denetim.py --kaynak` | metin 530 (+ CAD 893, arayüz 552); ASCII 0, elektrik 0, zorunlu 0, yasak 0 (istisna 5), çıplak 0, çözülemeyen 0, bozuk 0, bağlam 0, onay farkı 0 (kayıt metin 319, liste 119, kablo 90); çıkış 0 |
| `rehber_denetim.py --bozma-denemesi` | 65 / 65, bozulmamış kaynakta hata 0 |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER; çizilen 51 / çizilmeyen 23; geometri hata 0, bilgi 4; ayırt edilemeyen 1; onay tutuyor / 27 / 27 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ, 38 bölüm |
| sözdizimi (`ast`) + `\x08` / `\x01` / U+FFFD taraması | 6 dosya temiz; `node --check rehber/app.js` 0 |

Değişen dosyalar (bu tur): `tasarim/freecad/rehber/rehber_kritik.py` (yeni), `rehber_kritik_onay.json` (yeni, yenileme bayrağıyla
yazıldı), `rehber_deger.py`, `rehber_denetim.py`, `rehber_kablo.py`, `rehber_metin.py`, `planlama/adim3/kablolar_denetim.py`, bu
günlük, `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md` (K60 notu).

## 13. Düzeltme turu 2 (14.11, üçüncü bakış `F10h-kontrol-3.md` DÜZELTME GEREKLİ; son tur)

Üretimden önce tek madde: anahtarlı baranın köprüleri (kayıtta 3 × 12 AWG kırmızı) rehberde yoktu ve madde 8'deki "köprü yalnız şu
yerlerde takılır" cümlesi bu boşluğu yanlış bir talimata çeviriyordu. Kapsam dar tutuldu; devre değeri, `kablolar.json`, pin haritası,
CAD kaynağı ve kablo geometrisi değişmedi. FreeCAD, `rehber_uret.py` ve başsız tarayıcı koşmadı.

### 13.1 K1: iki bara, madde 8, kontrol maddesi (`tasarim/freecad/rehber/rehber_metin.py`)

- Yeni yer tutucular (`rehber_deger.py`, `bara-pabuc.kopruler`'den): `{kopru.bara}` (12 AWG), `{kopru_adet.yildiz|bara|toplam}`
  (4 / 3 / 7), `{kopru_renk.yildiz|bara}` (siyah / kırmızı), `{kopru_boy.yildiz|bara}` (50 mm), `{kopru_pabuc.toplam}` (14 = 2 × 7;
  `kopruler.pabuc` "her köprü ucu bir sarı … halka pabuç"). Adlar bağlam kuralına girdi (yıldız / anahtarlı bara / köprü / pabuç).
- Madde 2 (`:259–268`) iki bara ayrı cümlede: ortak kural (saplama başına en çok 4 pabuç, büyük akımlı pabuçlar yığının altında,
  üstte düz pul + yaylı pul; `bara-pabuc.not`), yıldız barası (5 saplama, 4 adet siyah 12 AWG köprü, ≈ 50 mm, yerleşim), anahtarlı
  bara (4 saplama, 3 adet kırmızı 12 AWG köprü, ≈ 50 mm, bütün saplamalar köprüyle bağlı).
- **Anahtarlı baranın yerleşimi uydurulmadı:** kayıtta `besleme_saplamasi: null`, `yerlesim` yok. Rehber: "Anahtarlı barada hangi
  ucun hangi saplamaya gideceği kayıtta yazılı değil: yerleşim serbest, yalnız saplama başına en çok 4 pabuç (besleme saplaması
  yazılı olmadığından baranın köprüleri koruyucunun tam akımıyla sınanır …)". Dayanak `kopruler.ilke`: "Besleme saplaması yazılı
  değilse köprü koruyanın tam akımıyla sınanır." Açık iş: yerleşimin kayda yazılması (§ 13.7).
- Madde 8 (`:293–297`): "yalnız" çıktı; "Bu adımda takılan köprüler: Ö4 …, acil stop düğüm kartı …, yıldız barası 4 adet 12 AWG …,
  anahtarlı bara 3 adet 12 AWG … ve KT3 ara kabloları. Bunların dışında mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman
  köprülenmez".
- Kontrol listesi (`:316–318`): "İki baranın köprüleri takılı: yıldız barasında 4 adet siyah 12 AWG, anahtarlı barada 3 adet
  kırmızı 12 AWG köprü, her ucu sarı halka pabuçla. Akü ayrıkken multimetrenin süreklilik kademesiyle her baranın ilk ve son
  saplaması arası öter (direnç sıfıra yakın); ötmezse köprü eksik ya da gevşek". ("≈ 0 Ω" çıplak direnç değeri kuralına takılacağı
  için sözle yazıldı.)
- Malzeme: rehberde ayrı malzeme / kesim listesi yok (kablo listesi `kablolar.md`'de, orada 7 köprü / 14 sarı pabuç geçiyor). K1
  "bağlantı" alanına (`:302–304`) eklendi: "Yıldız barası ve anahtarlı bara köprüleri: 7 adet 12 AWG köprü (yıldız 4 siyah,
  anahtarlı bara 3 kırmızı, her biri ≈ 50 mm) ve uçlarına 14 sarı halka pabuç."
- E4 (`:533`, `:602`): "çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür".
- Kural değişiklikleri: ZORUNLU K1 madde 8 deseni iki barayla; yeni ZORUNLU: madde 2 anahtarlı bara köprüsü, kontrol "İki baranın
  köprüleri takılı"; E4 ZORUNLU ve TERIM_ISTISNA yeni E4 cümlesiyle; TERIM_ISTISNA eski madde 2 cümlesi → "WAGO yok."; ASCII
  sözlüğüne 5 kelime (eksik, ilkesi, koruyucunun, saplamaya, zincir); YASAK "köprüleme talimatı" çoğul adı ("köprüler", "köprüleri",
  "köprülerin" …) artık tutmaz, fiil biçimleri tutar (bozma 5 / 5).

### 13.2 Kayıt → rehber tamlığı (`rehber_denetim.tamlik_denetle`, `--kaynak`'ta)

Kayıttaki her güvenlik öğesi rehber metninde yer tutucusuyla (koruyucu, köprü, saplama) ya da kimliği / adıyla (GPIO, anahtar, acil
stop zinciri) geçmeli; geçmeyen HATA. Eşlemesi olmayan yeni kayıt (bara, anahtar) da HATA. Muaf liste `TAMLIK_MUAF` (gerekçeli),
anahtar adları `TAMLIK_AD`; ikisi de onay kaydında. Muaf deseni hiçbir öğeyi tutmuyorsa ya da rehberde geçen öğeyi tutuyorsa HATA.

| Tür | Taranan | Ölçüt |
| --- | --- | --- |
| koruyucu (tür sigorta) | 12 | `{a.<koruyucu>}` |
| köprü (`bara-pabuc.kopruler`) | 2 | `{kopru.<b>}` ve `{kopru_adet.<b>}` |
| saplama düğümü | 13 | 2 bara (`{saplama.sayi}`, `{saplama.bara}`) + yıldız yerleşimindeki 11 iletken `{saplama.<kimlik>}` |
| GPIO rolü (pin haritası § 9) | 24 | `{gpio.<ad>}` ya da "GPIO<n>" |
| anahtar | 5 | `TAMLIK_AD` adı |
| acil stop zinciri | 9 | A01–A06 kimliğiyle; K1 / K2 kontağı ve mantar adıyla |
| **toplam** | **65** | |

**Düzeltmeden önceki kaynakta** (aynı denetim, eski `rehber_metin.py`): eksik **2**: "köprü Anahtarlı bara · +: kayıtta 3 × 12 AWG
kırmızı köprü var, rehberde {kopru.bara} / {kopru_adet.bara} yok" ve "köprü Yıldız barası · GND: kayıtta 4 × 12 AWG siyah köprü var,
rehberde {kopru_adet.yildiz} yok" (yıldız barasının köprü adedi de yazılı değildi). Başka eksik yok; ikisi § 13.1 ile kapandı.
Düzeltmeden sonra eksik 0.

Muaf (21 öğe, 4 desen): GPIO sinyal / ölçüm pinleri (enkoder, BTS, sonar, akü ölçümü; 16), veri yolu (I2C SDA / SCL, UART0 TX / RX;
4), kart üstü LED (1); anahtar `esp32-3v3` (ESP32 kartının kendi regülatörü, montajda ayrı parça değil). Gerekçe: güç ve acil stop
zincirinde değiller; pin numarası pin haritasında ve yazılımda, rehber yazmaz. Röle ve güvenlik pinleri (ROLE_K1, ROLE_K2_ONSARJ,
ACIL_STOP_DURUM, BARA_DURUM) muaf değil, geçiyor.

Kablo kimliği (bilgi, hata değil): 74 kablonun **68**'i rehberde kimliğiyle geçiyor; geçmeyen 6: I01, I02 (I2C), P01, P02, P03
(PCA9685 sinyal), C01 (kamera FPC). Kayıtta rehber adımları B6a / K2 / E4, tür "öneri" / "bugün".

### 13.3 Onay kaydı

- Kapsam: anahtar sözcük seçimi kalktı; 531 metnin **bütün cümleleri** kayda girer (metin **907**, liste **133**, kablo **90** =
  1130 girdi; önce 319 / 119 / 90). Neden etiketi yalnız bilgi ("metin" = etiketsiz).
- Kayıt tam metni de tutar (`metin` alanı; `bas` kalktı). Fark satırı eski ve yeni hâlin tamamını yazar; karar yine özetten (kayıttaki
  metin elle değişip özetle tutmazsa satırda "[UYARI: kayıttaki metin özetle tutmuyor]" görünür).
- Bozuk / boş JSON, `{}` ya da yapısı bozuk kayıt: `rehber_kritik.KayitHatasi` → `rehber_denetim.py` "HATA: onay kaydı okunamadı
  (rehber_kritik_onay.json): bozuk ya da boş JSON (…). Kayıt elle düzenlenmez; depodaki son hâline dön (git) ya da bilinçli olarak
  `rehber_denetim.py --kritik-onay-yenile` ile yenile", çıkış 1; `rehber_kablo.py` aynı iletiyi HATA satırı olarak yazar, KALDI,
  çıkış 1. Traceback yok.
- B22 (`kablolar.json`'da `hat-G22` adı değişti): "HATA: elektrik denetiminin kayıt girdisi okunamadı: 'hat-G22' anahtarı yok
  (kablolar.json koruyucular / kablolar ya da pin haritası değişti mi? …)", çıkış 1, traceback yok.
- `rehber_uret.py` `on_sinama()` (§ 9): üretimden önce kaynak denetimi + onay + tamlık; fark varsa çıkış 1. `py_compile` ile sınandı,
  koşulmadı.
- Kayıt bu turda bayrakla yenilendi: "onay kaydı yenilendi … (kablo 90, liste 133, metin 907); 611 fark yazıldı" (611'in çoğu yeni
  kapsamın ilk kez kayda giren cümleleri; içerik farkı aşağıda).

### 13.4 Farkın tamamı (eski kurallarla eski kayıt ↔ yeni; 29 girdi)

Metin (eski → yeni; yer tutucular ham):

| Yer | Eski | Yeni |
| --- | --- | --- |
| K1 is_ (madde 2) | Yıldız barası {saplama.sayi} M5 saplama, anahtarlı bara {saplama.bara} M5 saplama; uçlar halka pabuçla, saplama başına en çok {saplama.pabuc} pabuç, saplamalar arası {kopru.yildiz} köprü (WAGO yok). | İki bara da M5 saplama üstünde halka pabuç yığını: saplama başına en çok {saplama.pabuc} pabuç, büyük akımlı pabuçlar yığının altında, üstte düz pul + yaylı pul; WAGO yok. |
| K1 is_ (madde 2) | — | Yıldız barası (toprak) {saplama.sayi} M5 saplama: saplamalar {kopru_adet.yildiz} adet {kopru_renk.yildiz} {kopru.yildiz} köprüyle (≈ {kopru_boy.yildiz}, iki ucu sarı halka pabuç) birbirine zincir bağlanır. |
| K1 is_ (madde 2) | — | Anahtarlı bara (+) {saplama.bara} M5 saplama: saplamalar {kopru_adet.bara} adet {kopru_renk.bara} {kopru.bara} köprüyle (≈ {kopru_boy.bara}, iki ucu sarı halka pabuç) birbirine zincir bağlanır; bütün saplamalar köprüyle birbirine bağlı. |
| K1 is_ (madde 2) | — | Anahtarlı barada hangi ucun hangi saplamaya gideceği kayıtta yazılı değil: yerleşim serbest, yalnız saplama başına en çok {saplama.pabuc} pabuç (besleme saplaması yazılı olmadığından baranın köprüleri koruyucunun tam akımıyla sınanır: `planlama/adim3/kablolar.json`, saplama uç türünün köprü ilkesi). |
| K1 is_ (madde 8) | Bu adımda köprü yalnız şu yerlerde takılır: Ö4 yerindeki kısa tel köprü (madde 5), acil stop düğüm kartındaki (A02, A04) {kopru.A02} tel köprü (madde 5), yıldız barasının saplamaları arasındaki {kopru.yildiz} köprü (madde 2) ve KT3 bakışında kutu ayrı girişli çıkarsa yuva girişlerine giden ara kablolar (kontrol listesi). | Bu adımda takılan köprüler: Ö4 yerindeki kısa tel köprü (madde 5), acil stop düğüm kartındaki (A02, A04) {kopru.A02} tel köprü (madde 5), yıldız barasının saplamaları arasındaki {kopru_adet.yildiz} adet {kopru.yildiz} köprü (madde 2), anahtarlı baranın saplamaları arasındaki {kopru_adet.bara} adet {kopru.bara} köprü (madde 2) ve KT3 bakışında kutu ayrı girişli çıkarsa yuva girişlerine giden ara kablolar (kontrol listesi). |
| K1 kontrol | — | İki baranın köprüleri takılı: yıldız barasında {kopru_adet.yildiz} adet {kopru_renk.yildiz} {kopru.yildiz}, anahtarlı barada {kopru_adet.bara} adet {kopru_renk.bara} {kopru.bara} köprü, her ucu sarı halka pabuçla. |
| K1 kontrol | — | Akü ayrıkken multimetrenin süreklilik kademesiyle her baranın ilk ve son saplaması arası öter (direnç sıfıra yakın); ötmezse köprü eksik ya da gevşek |
| K1 baglanti_md | — | Yıldız barası ve anahtarlı bara köprüleri: {kopru_adet.toplam} adet {kopru.yildiz\|bara} köprü (yıldız {kopru_adet.yildiz} {kopru_renk.yildiz}, anahtarlı bara {kopru_adet.bara} {kopru_renk.bara}, her biri ≈ {kopru_boy.yildiz\|bara}) ve uçlarına {kopru_pabuc.toplam} sarı halka pabuç. |
| E4 is_ ve E4 alt adım 3 is_ (2 yer) | USB ses kartı takılmaz: çizimde ve animasyonda kart PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan görüntüdür, uygulanmaz. | USB ses kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan görüntüdür, uygulanmaz. |

Kural listeleri: ZORUNLU 2 değişti (K1 madde 8 deseni: "Bu adımda köprü yalnız şu yerlerde takılır … {kopru.yildiz} köprü" → "Bu
adımda takılan köprüler: … {kopru_adet.yildiz} adet {kopru.yildiz} köprü \(madde 2\), anahtarlı baranın saplamaları arasındaki
{kopru_adet.bara} adet {kopru.bara} köprü"; E4 deseni köpük bantla) ve 2 eklendi (madde 2 anahtarlı bara, kontrol "İki baranın
köprüleri takılı"); TERIM_ISTISNA 2 değişti ("uçlar halka pabuçla, … 12 AWG köprü (WAGO yok)." → "WAGO yok."; E4 cümlesi köpük
bantla); YASAK 1 değişti (`\bköprüle\w*` → `\bköprüle(?!r(?:i|in|e|de|den|le)?\b)\w*`); TAMLIK_AD 8 ve TAMLIK_MUAF 4 eklendi (§ 13.2).
Kablo bölümü değişmedi.

### 13.5 Bozmalar (geçici kopya, depo dışında; `-B`, önbellek temiz; kontrolün klasörüne yazılmadı)

Üçüncü bakışın kaçan / rastlantıyla yakalanan bozmaları, yeni kayıtla:

| Kod | Bozma | Sonuç | Mekanizma |
| --- | --- | --- | --- |
| N01b | F5 "uzatılmaz" → "uzatılabilir" | çıkış 1 | onay ("KRITIK değişti … F5 is_", eski / yeni tam cümle) |
| N01 | F5 "dönen tekeri elle durdurarak dene" | çıkış 1 | onay + ASCII |
| N03 | K1 "takılmadan önce" → "takıldıktan sonra" | çıkış 1 | onay |
| N04 / N04b / N04c | "Bu maddeyi şimdilik atla / yapma.", "Yukarıdaki listeye uyma." | çıkış 1 | onay ("eklendi") + ASCII |
| N05 | F5 "Bu adımdaki sıra kaynakta yok, doğrulanmadı." silindi | çıkış 1 | onay ("silindi") |
| N07 | K1 madde 7 ardına "Önce kabuğu kapat." | çıkış 1 | onay ("eklendi") |
| N11 | F5 "Mantarı bırak …" ↔ "Motor yön testi …" | çıkış 1 | onay (alan içi sıra) |
| D3a | madde 8'den anahtarlı bara köprüsü silindi | çıkış 1 | onay + zorunlu |
| D3b | madde 2'de `{kopru_adet.bara}` → `{kopru_adet.yildiz}` | çıkış 1 | onay + zorunlu + bağlam |
| D3c | madde 8'e "yalnız şu yerlerde" geri geldi | çıkış 1 | onay + zorunlu |

Kayıt: bozuk JSON, boş dosya, `{}`, yapısı bozuk kayıt → dördünde de `rehber_denetim.py` ve `rehber_kablo.py` çıkış 1, düzgün ileti,
traceback yok; B22 çıkış 1, düzgün ileti. İkinci kontrolün B01–B43'ü (47 biçim; B30'un çapası yeni madde 2 metnine uyarlandı): 47 / 47;
onaysız koşu 44 / 47 (B09, B24, B25 yalnız onayla, § 12.6 ile aynı). Kalıcı: `rehber_denetim.py --bozma-denemesi` **76 / 76** (65 + YASAK
5: üç fiil yakalanır, iki çoğul ad yakalanmaz; tamlık 6: anahtarlı bara köprüsü yer tutucusuz, kayda yeni sigorta / bara köprüsü /
saplama düğümü / zincir anahtarı / acil stop kablosu).

### 13.6 Doğrulama (14.11 11:40–11:56, `-B`, `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` silinmiş)

| Komut | Sonuç |
| --- | --- |
| `kablolar_uret.py --kontrol` | kablolar.md ve elektrik.md bloğu güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / toplam bozma 145, GEÇER |
| `rehber_denetim.py --kaynak` | metin 531 (+ CAD 893, arayüz 552); ASCII 0, elektrik 0, zorunlu 0, yasak 0 (istisna 5), çıplak 0, çözülemeyen 0, bozuk 0, bağlam 0, onay farkı 0 (kayıt metin 907, liste 133, kablo 90); tamlık 65 öğe, eksik 0, muaf 21, kablo kimliği 68 / 74; çıkış 0 |
| `rehber_denetim.py --bozma-denemesi` | 76 / 76, bozulmamış kaynakta hata 0 |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER; çizilen 51 / çizilmeyen 23; geometri hata 0, bilgi 4; ayırt edilemeyen 1; onay tutuyor / 27 / 27 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ, 38 bölüm |
| `py_compile` (derleme çıktısı depo dışına) | 10 dosya temiz (`rehber_uret.py` dahil); `\x08` / `\x01` / U+FFFD yok; `node --check rehber/app.js` 0 |
| olağan koşu kaydı yazmıyor | `--kaynak` ve `--bozma-denemesi` öncesi / sonrası `rehber_kritik_onay.json` SHA-256 aynı |

### 13.7 Açık işler (bu turda dokunulmadı)

- **Anahtarlı baranın saplama yerleşimi kayıtta yok** (`kopruler["Anahtarlı bara · +"].besleme_saplamasi: null`, `yerlesim` yok):
  rehber "yerleşim serbest" diyor (dayanak `ilke`). Yerleşim kayda yazılırsa `{saplama.<kimlik>}` yer tutucuları ve tamlık sınaması
  yıldız barasındaki gibi genişler.
- **G19, G20, G24, G26** (üçüncü bakış § 3.3-2): geometrinin kaçırdığı dört eşleme bozması yalnız onay kaydıyla tutuluyor (dal
  gövdesinin ana yolun ayrılma noktasına kadarki bölümü röle / bara uçlu kablolara da uyuyor; A03 ↔ G22 ayırt edilemiyor; eksik
  eşleme sınanmıyor). P10.7b2.
- `TABAN_DISI_BOLGE` gövde bölgesi geniş (üçüncü bakış § 3.3-3): P10.7b2.
- 21 GPIO / anahtar muafı (§ 13.2) ve kimliğiyle geçmeyen 6 kablo (I01, I02, P01–P03, C01): rehberin bunları anması P10.7b2'de
  karar.

Değişen dosyalar (bu tur): `tasarim/freecad/rehber/rehber_metin.py`, `rehber_deger.py`, `rehber_denetim.py`, `rehber_kritik.py`,
`rehber_kritik_onay.json` (bayrakla yenilendi), `rehber_kablo.py` (bozuk kayıt iletisi), `rehber_uret.py` (ön sınama; koşulmadı), bu
günlük, `planlama/dongu-158.md`.

## 14. Üretim ve zincir (14.11, üretim ajanı U)

14.11.2026 12:01–13:33 (saat okundu). Dal `lale-duzeltme`, HEAD `8134519`, kaynak çalışma ağacında. Yöntem F10g § 5: geçici
klasörde (depo dışında) `baslat.ps1` → `sarmal.ps1` (15 s bellek bekçisi) → yoklama, her koşunun `.durum` kaydı. Sarmalayıcıya
`-B` ve `PYTHONDONTWRITEBYTECODE=1` eklendi; bekçinin fiziksel bellek eşiği bu pakette 1,2 GB'a çekildi (art arda iki ölçüm). Kaynak
dosyalarına dokunulmadı; kod düzeltmesi yapılmadı. Aynı saatlerde dördüncü bağımsız kontrol (`F10h-kontrol-4.md`, KAYNAK GEÇER)
depoyu yalnız okuyarak çalıştı.

**FreeCAD kilidi:** 12:03 satır yazıldı ("P10.7b1 üretim (ajan U) rehber_uret.py"), FreeCAD aşaması (`freecadcmd`, veri 162 s) bitince
12:06'da "boş". Son hâli "boş". FreeCAD'in Python'u (3.11) `-B`'ye rağmen `tasarim/freecad/rehber/__pycache__` yazdı (6 dosya,
gitignore'da); iş sonunda silindi.

### 14.1 Ön sınama (FreeCAD'siz, 12:01–12:03)

| # | Komut | Çıkış | Süre | Beklenen ↔ ölçülen |
| --- | --- | --- | --- | --- |
| 1 | `kablolar_uret.py --kontrol` | 0 | < 1 s | "güncel" ↔ "kablolar.md ve elektrik.md bloğu güncel" |
| 2 | `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | 1 / 30 s | GEÇER, bozma 145 ↔ aynı |
| 3 | `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | < 1 / 2 s | GEÇER, 51 / 23, geometri hata 0 / bilgi 4, ayırt edilemeyen 1, onay tutuyor, 27 / 27 ↔ aynı |
| 4 | `rehber_denetim.py --kaynak` / `--bozma-denemesi` | 0 / 0 | 1 / < 1 s | metin 531, bütün sayılar 0, kayıt 907 / 133 / 90, tamlık 65 / 0 / 21, kablo kimliği 68 / 74, bozma 76 / 76 ↔ aynı |
| 5 | `rehber_kol_kablo.py --yazma` | 0 | 36 s | GEÇTİ, 38 bölüm ↔ aynı |
| 6 | kontrollerin bozmaları geçici kopyada | — | — | **koşulmadı** (brief 1–5'i istedi; araç kalıcı değil) |

Ön sınamadan sonra `git status` değişmedi.

### 14.2 Zincir

`rehber_uret.py` 12:03:31'de (boş bellek önce 4,05 GB), zincirin geri kalanı (`zincir.py`, sırayla) 12:42:04'te başladı (3,95 GB).

| Sıra | Komut | Başlangıç | Çıkış | Süre (s) | Beklenen | Ölçülen |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rehber_uret.py` | 12:03:31 | **2** | 2245 | çıkış 0 | **çıkış 2**: "ek kontrol sorunlu: ['denetim', 'perdelenme']" (§ 14.3 S1, S2); bütün çıktılar yazıldı |
| 1 | ön sınama satırı | | | | "on sinama: kaynak denetimi gecti, onay kaydi tutuyor (kablo 90, liste 133, metin 907)" | aynı satır, ilk satırda |
| 1 | parça / şema / alt adım | | | | 1192 / 49 / 71 | 1192 / 49 / 71 (71 geçti), tarayıcı 50 / 50, konsol hatası 0 |
| 1 | kablo eşleme | | | | GEÇTİ, 51 / 23, eşleşmeyen boş | "kablo esleme: GECTI"; `kontrol.json` `gecti` true, 51 / 23, `eslesmeyen` [] |
| 1 | denetim | | | | ELEKTRİK 0 | elektrik 0, yasak 0 (istisna 5), zorunlu eksik 0 / 71; **ASCII kalıntı 13** (S1) |
| 1 | uçuş | | | | 340 / 0 / 16 | 340 satır, çarpışan 0, istisna 16, `istisna_bos` 0, ölçüm kaydı 1 |
| 1 | sıra / giriş | | | | ulaşılamaz 0 | 565 bağlantı, ulaşılamaz 0; giriş yolu girilemez 0 |
| 1 | perdelenme | | | | gerekçesiz 0 | **gerekçesiz 1** (31.3 p0822), istisna 116 (F10g'de 117), toplam gizli 264 (S2) |
| 1 | PDF | | | | ≈ 75 sayfa | **77 sayfa** (adım 50 + devam 27), en küçük yazı 8,1 pt, 16079 kB, baskı karesi 121 / 121; neden § 14.3 S4 |
| 2 | `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 12:42:05 | 0 | 0 | hata 0 | GEÇER, hata 0, "veri: eşlemesiz çizim 0", onay tutuyor |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 12:42:05 | 0 | 1 | veri bozmaları yakalanır | 32 / 32 (27 + 5 veri bozması: şema rengi, yarıçap, CAD rengi, bilinmeyen kimlik, lejant tablosu) |
| 2a | geometrik eşleme (aynı koşu) | | | | hata 0, bilgi yalnız gerekçeli uçlar | hata 0, bilgi 4 (yol 9 ve 12 istisnalı uç, yol 10 A04 / A06 elle bakılan düğüm); `taban-analiz.json` yeniden yazılmadı |
| 3 | `rehber_denetim.py` (veri) | 12:42:06 | 0 | 0 | GEÇTİ, elektrik / yasak / çıplak 0 | ASCII 0, elektrik 0, yasak 0, zorunlu eksik 0 / 71, parça 1192, şema 49 |
| 4 | `F10f-dogrula.py` | 12:42:07 | 0 | 547 | GEÇTİ; `kablo_kare` izlenir | GEÇTİ; `kablo_kare` 76 / 76 (en düşük oran 0,483, en az fark 1135 px), `sonra` geçti; `gizli_piksel` 11 parça (F10g ile aynı liste başı) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 12:51:13 | **2** | 859 | renk_demo KALDI, gerisi geçti | renk_demo KALDI (bilinen); **`renk_sahne` KALDI: yanlış 11** (S3); renk_cad, karşıtlık, ev, işaret, görünürlük, arayüz geçti |
| 6 | `F10d-dogrula.py --goruntu-yok` | 13:05:32 | 0 | 719 | geçti; yabancı şema izlenir | GEÇTİ, masa yabancı şema 0, telefon taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 13:17:31 | 0 | 421 | geçti | GEÇTİ: seçim 6 / 6 (adım 17 panel 1 / 1), şema tıklaması geçti, ağsız dış istek 0, konsol 0 |
| 8 | `F9b-dogrula.py` | 13:24:32 | 0 | 5 | GEÇER, hata 0 | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 13:24:36 | 0 | 0 | 17 dosya aynı | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 10 | `regresyon.py --yazma` | 13:24:36 | 0 | 0 | GEÇER, aynı | GEÇER, 10 değerin hepsi aynı |

Zincirin `.durum` kaydı: "BITTI cikis 2 sure 2552 enaz 2.24" (çıkış 2 yalnız F10e'den; `zincir.py` ilk sıfırdan farklı kodu taşır).

**Bellek:** en düşük boş fiziksel bellek üretimde 2,42 GB, zincirde 2,24 GB (bekçinin 15 s'lik ölçümleri, 149 + 169 ölçüm); 1,2 GB
eşiğine yaklaşılmadı, bekçi hiç tetiklenmedi.

### 14.3 Sapmalar ve nedenleri (hiçbiri düzeltilmedi; kaynak / kural / ölçüt değişikliği gerektiriyor)

- **S1, ASCII kalıntı 13 (`rehber_uret.py` denetimi, tarayıcı metni):** "turuncu", "mor" (adım 0); "koruma", "enkoderle", "okunur",
  "kapatma", "Birden" (17); "besleyen", "VOUT" (31); "klemensi", "liste", "Analog", "beyaz" (32). Hepsi doğru yazılmış, Türkçe harfi
  olmayan kelimeler; kaynakları kablo tablosundan gelen panel metni (lejant adları "Anahtarlı bara, motor (turuncu)", "Sinyal (mor)",
  "Analog ses (beyaz)", `kb` satırları "koruma: …", "sigorta yok (… besleyen hattın koruması)", karışık yol notu "Birden çok devre
  sınıfı taşıyor"). `rehber_denetim.py --kaynak` ve veri modu bu metni taramıyor (ikisi de ASCII 0); yalnız tarayıcıdaki denetim
  görüyor. Çözüm `rehber_denetim.ASCII_TAMAM` listesine bu 13 kelimenin eklenmesi (kural listesi: bu pakette dokunulmadı).
- **S2, perdelenme gerekçesiz 1 (31.3, p0822 "Köpük bant (yedek USB ses kartı için; kart takılmaz, bant yapıştırılmaz)"):** E4 alt adım
  3'ün `gizli_ok` anahtarı `"Köpük bant (USB ses"`; parçanın adı `AD_CEVIRI` ile "Köpük bant (yedek USB ses kartı için …" oldu, anahtar
  artık tutmuyor (istisna 117 → 116, gerekçesiz 0 → 1). Parça F10g'deki gibi 3 mm vokselde tamamen gizli; yeni bir görünürlük sorunu
  değil, gerekçenin adla bağı koptu. Çözüm `rehber_metin.py` E4 alt adım 3 `gizli_ok` anahtarının yeni adın baş kısmına uyarlanması
  (ör. `"Köpük bant (yedek USB ses"`); bu pakette dokunulmadı.
- **S3, F10e `renk_sahne` yanlış 11:** adım 17'de p1180, p1182, p1183, p1188, p1189, p1190; adım 32'de p1184, p1185, p1186, p1187,
  p1191 (taban CAD kablo tüpleri). Sahnedeki renk açık temanın tonu (`kablo_sinif` light: kırmızı #c0392b, turuncu #b35a00, yeşil
  #1e7a3c, mor #7d3c98, sarı #8a6d00), F10e'nin beklediği veri `renk` alanı (taban rengi #d63031, #e67e22, #2e9e4f, #8e44ad, #e2b714).
  11'inin hepsi tema tonuna birebir eşit; yani sahne düzeltme turu 1'in tema tonu kuralını (§ 11.6) uyguluyor, F10e ölçütü bu kuralı
  bilmiyor. Ölçüt değişikliği (kablo parçasında beklenen = `rt[tema]`) orkestratöre bırakıldı.
- **S4, PDF 77 sayfa (≈ 75 beklenen):** `sayfa_esleme` farkı yalnız adım 29 (E3a, 1 → 2 sayfa) ve 33 (F1, 5 → 6 sayfa). Neden lejant
  satırı değil: E3a'nın `is_` 899 → 1464, `not_` 419 → 704 karakter; F1'in `is_` 1059 → 1225, `kontrol` 2135 → 2408, `kablo` 47 → 351
  karakter (HEAD verisi ↔ yeni veri). K1 (17) önceden de 2 sayfaydı.
- **Bilgi:** `kablo_kare` ölçütü kol yarıçapı 2,5 ile geçti (en düşük oran 0,483 ≥ 0,20); F10d yabancı şema 0; F10a "veri değişti
  (bilgi)".

### 14.4 Kare bakışı (iki tema)

Rehberin kendisinden 1400 × 900, kendi başsız Chrome'umla (F10a `Cdp`, profil geçici klasörümde, iş bitince kapandı; depoya yazmaz):
genel kare, kablo listesine kaydırılmış panel, listedeki ilk kabloya tıklanmış kare; ayrıca alt adımlar (31.3, 31.9, 35.4, 40.2, 41.2,
41.4, 48.2, 49.1), karışık sınıflı yollara tıklama (p1182 yol 3, p1184 yol 5, p1186 yol 7, p1181 toprak), K1 madde 2 / 8 / kontrol
metnine kaydırma ve yazdırılabilir sürümün (`yazdir.html`, PDF'in kaynağı) K1 / K2 sayfaları. Çekilen 93 kareden **35'ine baktım**
(33 sahne + 2 basılı sayfa; bazıları açık + koyu yan yana birleştirilerek, K2 ayrıca büyütülmüş kesitle). Bakmadıklarım: 40 / 41 / 48
genel bakışları, 41.2 koyu, 35.4, 40 / 41 / 48'in tıklanmış kareleri, 32 açık temanın tıklanmış karesi, basılı H1 sayfası. PDF'i doğrudan görüntü olarak açamadım (sayfa çizici yok); metnini `pypdf` ile
okudum, görünüşüne `yazdir.html` karesinden baktım.

| Kare | Tema | Gördüğüm |
| --- | --- | --- |
| K1 (17) genel | açık, koyu | Kırmızı, turuncu, yeşil, mor, siyah ayrı okunuyor. Açık temada toprak siyah, koyu temada açık gri (#b3b3b3) kısa parça seçiliyor; lejantta koyu temada toprak içi koyu, kenarı açık halka. Kırmızı ↔ turuncu iki temada ayrılıyor. Taban tüpleri aynı kalınlıkta (geometri 2,5; beklenen). |
| K1 madde 2 / 8 / kontrol | açık, koyu | Madde 2'de yıldız barası (4 siyah 12 AWG köprü) ve anahtarlı bara (3 kırmızı 12 AWG köprü, "yerleşim serbest") ayrı cümlelerde; madde 8 "Bu adımda takılan köprüler: … 4 adet … 3 adet 12 AWG köprü …"; kontrolün ilk maddesi "İki baranın köprüleri takılı …" + süreklilik cümlesi. Panelde kaydırarak okunuyor; basılı sayfada (18 / 77) madde 1–8 ve bağlantı alanı tek sayfaya sığıyor, kontrol listesi devam sayfasında (19). |
| K1 tıklama (yol 1, yol 3, toprak) | açık, koyu | Bilgi kartı dolu: başlık, "(gösterim) · taban · adım 17 (K1)", 4 `kb` satırı (kimlik, uçlar, kesit mm², sigorta / koruma, acil stopta enerjili / enerjisiz), "… ve 2 kablo daha (Kablo listesi)"; yol 3'te "Birden çok devre sınıfı taşıyor; renk ilk kablonun sınıfı". Seçim rengi parlak yeşil: açık temada acil stop koyu yeşilinin yanında ayrılıyor ama ikisi de yeşil (zor). Kart sahnenin sol üstünü örtüyor. |
| K2 (32) genel + büyütülmüş kesit | açık, koyu | Boyun demetinde açık temada HDMI lacivert (#1d3854) ↔ analog ses gri-mavi (#4c7078) ↔ 12 V kırmızı ayrılıyor; koyu temada HDMI camgöbeği ↔ ses beyaz ↔ kırmızı net. USB (gri) demette karede seçemedim (direğin arkasında). Açık temada lacivert HDMI siyaha yakın: tabandaki siyah toprakla aynı karede ayrı yerde, ince çizgide ayırmak zor. Sarı servo yolu (açık temada hardal #8a6d00) turuncudan ayrılıyor. 18 AWG (3,1) kırmızı ile 2,5'lik kablolar arasında kalınlık farkı bu ölçekte görünmüyor. |
| K2 tıklama (yol 5, yol 7) | açık, koyu | Kart dolu, karışık sınıf notu var. Koyu temada seçim yeşili (#7cfc00) ile sarı servo kablosu ince çizgide birbirine yakın (zor). |
| E4 (31) genel | açık, koyu | Kafa kapalı; lejantta USB / 5 V / HDMI var ama kablolar karede görünmüyor (yanıltıcı: lejant görünmeyen kabloları sayıyor). |
| E4.3 (31.3) | açık, koyu | Başlık "(USB ses kartı yedek, takılmaz)"; metin "USB ses kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; … uygulanmaz. Kartın köpük bandı da yapıştırılmaz". Karede iki yeşil kart kabuk duvarında takılı görünüyor, hangisinin takılmayan kart olduğu karede işaretli değil; metinle birlikte okunuyor, kare tek başına yanıltıcı. Köpük bant görünmüyor (S2). |
| E4.9 (31.9) | açık, koyu | Lejantta HDMI / USB / 5 V; kablolar kabuğun içinde, karede seçemedim (zor). Koyu temada lejantta 5 V mavisi ↔ HDMI camgöbeği ayrılıyor. |
| F3 (35) tıklama | açık, koyu | Göğüs dokunmatiği U05 kartı dolu (uçlar, "sigorta yok (hazır kablo / sinyal …)"); kablo seçimle yeşil görünüyor. |
| F5 (49) genel, 49.1 | açık, koyu | Metin hub bağlarını ve E9 ön şarj dizisini anlatıyor ("ESP32 ön şarj dizisi (E9): ön koşul …"); 49.1'de hub kutusu kapakta, kablo çizimi yok (beklenen: U03 / U05 / U06 şemaları K2 / F3'te). |
| G2 (39) | açık, koyu | Kablo çizimi yok (bu adımın kol kablo bölümü yok; kol bölümleri 36, 40, 41, 42, 44, 48'de). |
| G3 (40.2) | açık, koyu | Sarı uzatma demeti, beyaz kablo bağları. Açık temada hardal sarı gri zeminde okunuyor. "Kablo" ve "S2 lopu" lejantta aynı renk; lopun hangi bölüm olduğu karede renkle ayrılmıyor, yalnız şekilden (zor). |
| G4 (41.2, 41.4) | açık (41.2), açık + koyu (41.4) | U-lopu duvarda; 41.4'te bu uç duruş dolu, öbür uç duruş soluk: iki temada ayrılıyor. |
| H1 (48.2) | açık, koyu | Dirsek JR eki siyah, bilek lehim eki parlak sarı, ek noktaları beyaz halka; ekler 5,0 / 5,8 kalınlığıyla 2,5'lik kablodan ayrılıyor. Koyu temada lejantta JR eki kutusu boş çerçeve gibi görünüyor (koyu kutu koyu zeminde). |
| Basılı K2 (39 / 77) | — | "Karede:" satırı HDMI, USB, analog ses, 12 V'u sayıyor; aynı karedeki sarı servo ve mor sinyal taban kabloları satırda yok. |
| Basılı K1 (18 / 77) | — | **"Karede:" lejant satırı yok** (K1'in bütün kabloları CAD tüpü; `yazdir.html` `lejantMetin` yalnız şemaları sayıyor). Kâğıtta K1 karesindeki renklerin anlamı yazmıyor. |

**Zor okunan / yanıltıcı kareler: 9** — K1 seçim yeşili ↔ acil stop yeşili (açık); K2 lacivert HDMI ↔ siyah (açık, ince çizgi); K2 seçim
yeşili ↔ sarı (koyu); K2'de 18 AWG kalınlık farkı görünmüyor; E4 genel (lejant görünmeyen kabloları sayıyor); E4.3 (takılmayan kart
takılı görünüyor, metinle okunuyor); E4.9 (kablolar seçilemiyor); G3 40.2 (S2 lopu ↔ uzatma aynı renk); basılı K1 / K2 lejant satırı
eksik / CAD kabloları yok.

**Renk yargısı:** sınıflar iki temada ayrılıyor; koyu temada toprak (açık gri) ve açık temada sarı (hardal) / beyaz (gri-mavi) okunuyor.
En zayıf çift açık temada siyah ↔ HDMI lacivert (ölçü ΔE00 15,3; karede ince çizgide ayırt etmek zor). CSI kablo çizimi yok (C01
çizilmeyen), USB ↔ CSI ve turuncu ↔ CSI gözle bakılamadı. **Kalınlık yargısı:** verideki şema yarıçapları 2,5 / 3,0 (HDMI) / 3,1 (18
AWG) / 4,0–5,8 (kol eki, bağ); **3,6 (16 AWG) ve 4,6 (12 AWG) kademesinde çizilen şema yok** (16 / 12 AWG yolları CAD tüpü, 2,5). Bu
yüzden 18 ↔ 16 AWG farkına gözle bakılamadı; 18 AWG (3,1) ile 2,5 arasındaki fark genel karelerde görünmüyor, yalnız kol eklerinin
(5,0 / 5,8) kalınlığı seçiliyor.

### 14.5 Üretimin yazdığı dosyalar

`rehber/veri/rehber-veri.json` / `.js` (`robot.glb` / `robot-glb.js` değişmedi), `rehber/goruntu/*.png` (121), `planlama/rehber/goruntu/
*.png` (128, telefon kareleri dahil), `planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf`, `planlama/d158/F10{a,d,e,f}-dogrula.json`.
Paket dışı eski değişikler (`tasarim/freecad/kabuk/gorsel/*.png` 13, `tasarim/freecad/montaj/yerlesim-kontrol.json`) **yeniden
yazılmadı** (dosya zamanları 09.11 / 03.11, fark aynı). `carpisma-sonuc.json` ve `regresyon*.json` değişmedi. `git status` 36 → 294 satır
(+258: 249 kare, 2 veri, PDF, `kontrol.json`, 4 doğrulama JSON'u ve kontrol ajanının `F10h-kontrol-4.md`'si).

### 14.6 Doğrulanamayanlar

- 18 ↔ 16 AWG ve 12 AWG kademeleri gözle (çizilen şema yok, § 14.4).
- CSI kablosunun rengi (çizilmiyor).
- PDF'in görüntüsü doğrudan (sayfa çizici yok); basılı sayfa `yazdir.html` karesinden ve PDF metninden.
- Kontrollerin geçici kopyadaki bozmaları (§ 9 madde 6) koşulmadı.
- Renk ölçüsü 3B ışıklandırma altında değil, kare üstünde gözle; piksel ölçümü yalnız F10f `kablo_kare`.

## 15. Üretim uyum düzeltmesi (14.11, ajan U)

### 15.1 Birinci aşama: düzeltme + FreeCAD'siz sınama (13:37–13:43, saat okundu)

Orkestratörün hükmü: § 14.3'teki S1, S2, S3 içerik hatası değil, paketin araçlara yansımamış sonuçları. Bu aşamada FreeCAD ve
`rehber_uret.py` koşmadı. Rehber metni, kurallar, `kablolar.json`, onay kaydı, CAD ve geometri değişmedi.

**S1, ASCII kalıntı 13.** Neden: panelin kablo tablosundan gösterdiği metinleri (lejant adları, tıklama kartının `kb` satırları)
`rehber_denetim.py --kaynak` ve veri modu taramıyordu; kelimeler ancak üretimin tarayıcı denetiminde çıktı.

- `tasarim/freecad/rehber/rehber_denetim.py:488` yeni `tablo_metinleri(V=None)`: veri verilirse `kablo_sinif` adları ("Kablo: …") ve
  parça / şema `kb` satırları; verilmezse `rehber_kablo.Tablo()`'dan lejant adları ve 74 kablonun `bilgi_satiri`'ı. Yalnız ASCII
  sınamasına girer (elektrik, yasak ve tutarlılık sınamalarının girdisi değişmedi).
- `:1336` (`kaynak_denetle`) eski `asc = ascii_kalinti(m)` → yeni `asc = ascii_kalinti(m + tablo_metinleri())`.
- `:1314` (`denetle`, veri modu) eski `asc = ascii_kalinti(m + list(ek_metinler))` → yeni
  `asc = ascii_kalinti(m + tablo_metinleri(V) + list(ek_metinler))`.
- **Önce / sonra** (yalnız tarama eklenmiş, izinli liste eklenmemiş hâl ↔ son hâl): `--kaynak` ASCII **14 → 0** (Analog, beyaz, gri, mor,
  turuncu, besleyen, liste, koruma, klemensi, SDA, VOUT, enkoderle, okunur, kapatma), veri modu **13 → 0** (aynısı, SDA hariç: I01 / I02
  çizilmiyor). Üretimin bulduğu 13'ten 12'sini ön sınama artık yakalıyor; "Birden" yakalanmıyor, `app.js` sabit metni (karışık sınıf notu).
  `--kaynak`'ın 2 fazlası: "gri" (lejantın `hazir` satırı "Hazır kablo: USB, HDMI, CSI (gri)"; ekranda tür satırları gösterildiği için
  görünmüyor) ve "SDA" (I01 / I02 `kb` satırı; kablo çizilmiyor). Ön sınama bütün tabloyu taradığı için ekrandakinden geniş.
- İzinli liste: `:66` `ASCII_TAMAM`'a yeni satır "turuncu mor koruma enkoderle okunur kapatma birden besleyen klemensi liste analog
  beyaz gri" (11 + "birden" + "gri"); `:51` `KISALTMA`'ya "VOUT", "SDA"; `:48–49` açıklama satırı. İzinli listeler onay kaydında değil
  (kayıt farkı 0).
- Açık iş: `app.js` / `yazdir.html` sabit metinleri ASCII sınamasına girmiyor. Yalnız Türkçe harfli dizgilerle denendi, 64 kod kelimesi
  çıktı (`span`, `class`, `onerror` …), küçük değişiklik değil; "Birden" bu yüzden izinli listede, sınaması üretimde.

**S2, perdelenmede gerekçesiz 1.** Neden: E4 alt adım 3'ün `gizli_ok` anahtarı ad çevirisinden (`AD_CEVIRI`) önceki ada göreydi.

- `tasarim/freecad/rehber/rehber_metin.py:600` eski `gizli_ok={"Köpük bant (USB ses": voksel_ok(74), …}` → yeni
  `gizli_ok={"Köpük bant (yedek USB ses": voksel_ok(74), …}`. Gerekçe metni değişmedi; desen ("USB ses kartı") yeni adı zaten tutuyordu.
- Onay kaydı: `--kaynak` "onayli kritik girdi farki 0"; `gizli_ok` kayda girmiyor, yenileme gerekmedi, kayıt dokunulmadı.
- Başka kopan anahtar: eski (HEAD) ve yeni üretim verisinde bütün `sira_grup` ve adım `gizli_ok` / `ucus_ok` / `giris_ok` / `piksel_ok`
  anahtarları tarandı. Ad desenli olup hiçbir parça adına uymayan yalnız bu anahtar (yeni veride); iki verideki `giris_ok` "*"
  (34.8, 49.4) joker, eşleşme beklenmez. Kimlik anahtarlarının hepsi veride var.
- Bilgi satırı (ucuzdu): `tasarim/freecad/rehber/rehber_sira.py:1217–1220` `perdelenme()` sonucuna `eslesmeyen_anahtar` (ad desenli,
  hiçbir parçaya uymayan `gizli_ok` anahtarları; "*" ve kimlik hariç), `:1339–1340` özet satırı "perdelenme gerekce anahtari: parca
  adina uymayan N (bilgi)". Sınıra girmez.
- Sınama (FreeCAD'siz, depoya yazmadan): bugünkü veri bellekte `rehber_gorunum.alan_isle` ile tazelenip (değişen yalnız "E4.3 gizli_ok")
  adım 31'in perdelenmesi koştu: gerekçesiz **1 → 0**, 31.3'te p0822 gerekçeli (istisna adım 31'de 15). Bilgi satırı: düzeltmeden önce
  `['31.3 Köpük bant (USB ses']`, sonra `[]`.

**S3, F10e `renk_sahne` 11 yanlış.** Neden: ölçüt kablo parçasında taban rengini (`renk`) bekliyordu; uygulama tema tonunu çiziyor.

- `planlama/d158/F10e-dogrula.py:239` yeni `beklenen_renk(p, tema)`: kablo parçasında verideki `rt[tema]` (tek kaynak
  `rehber_kablo.TEMA_TON`; `rehber_kablo.py --veri` veriyi tablodan denetler), ton yoksa `renk`; öbür parçalarda `gr`. `:255` eski
  `bek = (PID[i].get("renk") or PID[i]["gr"]).lower()` → yeni `bek = beklenen_renk(PID[i], tema)`; `yontem` metni ve baş açıklaması
  (`:10`) buna göre. Beklenen sahneden okunmuyor. Ölçüm yine açık temada; öbür ölçütlere dokunulmadı.
- Sınama (yalnız ilgili bölüm; `rehber/`'in geçici kopyası, F10e'nin `sahne_tara` adres kalıbı, konum 17 ve 32, açık tema): bozulmamış
  kopyada 12 kablo parçası, **yanlış 0**. Bozma (kopyanın `rehber-veri.js`'inde p1180'in açık tonu turuncu sınıfın tonu #b35a00, p1190'ın
  açık tonu eski taban rengi #8e44ad): **yanlış 2** (p1180 sahne #b35a00 ↔ beklenen #c0392b; p1190 #8e44ad ↔ #7d3c98). Beklenen değerler
  depodaki `rehber-veri.json`'dan.
- Çıkış kodu: F10e `gecti` yalnız `ana` ölçütlerden (`renk_cad`, `renk_sahne`, `karsitlik`, `ev`, `ev_dogruluk`, `isaret`, `gorunurluk`,
  `arayuz`) ve konsol hatasından; `renk_demo` özette, çıkışa girmiyor. F10g zincirinde de "renk_demo KALDI (karar)" ile **çıkış 0** idi
  (§ 9 beklenen "renk_demo KALDI, gerisi geçti"). Düzeltmeden sonra beklenen **çıkış 0**; bu üretimdeki 2'nin tek nedeni `renk_sahne`.

**Sınama (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`, 13:41–13:43):**

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `kablolar_uret.py --kontrol` | 0 | güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 145, GEÇER |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, 51 / 23, geometri hata 0 / bilgi 4, ayırt edilemeyen 1 / 27 / 27 |
| `rehber_denetim.py --kaynak` | 0 | ASCII 0 (önce 14), öbür sayılar 0, kayıt 907 / 133 / 90, onay farkı 0, tamlık 65 / 0 / 21 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 76 / 76 |
| `rehber_kol_kablo.py --yazma` | 0 | GEÇTİ, 38 bölüm (35 s; "ilk 11": yeni veride ilk kol şeması 11, SEMA 13 → 11) |
| `rehber_denetim.py` (veri) | 0 | ASCII 0 (önce 13), elektrik 0, yasak 0 |
| `py_compile` (çıktı depo dışına) | — | `rehber_denetim.py`, `rehber_metin.py`, `rehber_sira.py`, `rehber_uret.py`, `F10e-dogrula.py` temiz |

JS değişmedi (`node --check` gerekmedi). Depoda `__pycache__` yok. `git status` 294 → 296 satır (`F10e-dogrula.py`, `rehber_sira.py`).

**İkinci aşama için yol:** düzeltmeler FreeCAD'in ürettiği veriyi (parça adları, `kb`, geometri, mesh) değiştirmiyor. `gizli_ok`
veriye `rehber_gorunum.alan_isle` ile işleniyor; bu da `rehber_uret.py`'nin FreeCAD'siz yolunda koşuyor. Bu yüzden projenin mevcut
`rehber_uret.py --veri-yok` kipi yeterli (baş açıklaması: "FreeCAD'i atla, yalnız tarayıcı kontrolü + görüntüler"; görünüm, kol kablo,
kontrol, PDF, denetim, sıra / perdelenme koşar). FreeCAD aşaması ≈ 160 s olduğundan kazanç küçük (≈ 35 dk kalır). Sonra zincirin 2–10'u;
F10e'de beklenen çıkış 0.

### 15.2 İkinci aşama: yeniden üretim (tam koşu) + zincir 2–10 (13:46–15:39, saat okundu)

Orkestratör kararı: tam koşu (`--veri-yok` değil), eşdeğerlik sorusu kalmasın. Yöntem § 14 ile aynı: kilit (13:46 yazıldı, 15:39
"boş"), sarmalayıcı + 15 s bellek bekçisi (eşik 1,2 GB) + durum dosyası, `-B`, `PYTHONDONTWRITEBYTECODE=1`. Üretimden önce boş bellek
3,92 GB, zincirden önce 4,21 GB. Bu sırada bağımsız kontrol (kontrol-5) depoyu yalnız okudu.

| Adım | Çıkış | Süre | İlk koşuyla (§ 14) fark |
| --- | --- | --- | --- |
| 1 `rehber_uret.py` (tam) | **0** (önce 2) | 2342 s (önce 2245) | ASCII **13 → 0**; perdelenme gerekçesiz **1 → 0**, gerekçeli istisna 116 → 117 (31.3 p0822); yeni bilgi satırı "parça adına uymayan 0"; ek kontrol sorunlu `['denetim', 'perdelenme']` → `-`. Aynı: parça 1192, şema 49, 50 / 50 adım, konsol hatası 0, uçuş 340 / 0 / 16, kablo eşleme GEÇTİ, elektrik 0, kol kablo 38 bölüm GEÇTİ, PDF **77** sayfa (adım 50, devam 27), 121 kare, 16079 kB |
| 2 `rehber_kablo.py --veri` / `--bozma-denemesi --veri` | 0 / 0 | 0 / 2 s | aynı (GEÇER; 32 / 32) |
| 3 `rehber_denetim.py` (veri) | 0 | 0 s | aynı (ASCII 0, parça 1192, şema 49) |
| 4 F10f | 0 | 573 s (546) | aynı (GEÇTİ) |
| 5 F10e `--goruntu-yok` | **0** (önce 2) | 894 s (859) | `renk_sahne` yanlış **11 → 0** (1192 / 1192 eşit); öbür ana ölçütler aynı (renk_cad 1192, ev 102, işaret 1284, görünürlük, arayüz); `renk_demo` KALDI (karar), çıkışa girmiyor |
| 6 F10d `--goruntu-yok` | 0 | 729 s (719) | aynı (GEÇTİ; perdelenme satırları bilgi) |
| 7 F10a `--kanit-yok` | 0 | 438 s (421) | aynı |
| 8 F9b | 0 | 5 s | aynı (hata 0) |
| 9 `carpisma_kos.py kontrol` | 0 | 0 s | aynı (17 dosya kayıtla aynı) |
| 10 `regresyon.py --yazma` | 0 | 0 s | aynı (kötüleşen yok) |

Zincir toplam 2641 s. En düşük boş bellek: üretimde 1,68 GB (bekçi eşiğinin üstünde, durdurma yok), zincirde 2,32 GB. FreeCAD
Python'unun (3.11) `-B`'ye karşın yazdığı dört `__pycache__` (`planlama/adim4`, `tasarim/freecad`, `tasarim/freecad/lale158`,
`tasarim/freecad/rehber`; hepsi bu iki üretimden, gitignore'da) silindi. `git status` 297 satır (296 + kontrolün `F10h-kontrol-5.md`'si).

**31.3 karesi (iki tema, 1400 × 900, normal kare):** sol arka kabuğun iç yüzünde iki yeşil kart üst üste (PAM8403 ve yanında yedek
USB ses kartı), altında pembe kenarlı raf / tutucu ve dört bağlantı yeri işareti. Köpük bant normal karede ayrı bir parça olarak
seçilmiyor (kartın arkasında, ince); § 14.4 ile aynı ve gerekçe metni (`voksel_ok(74)`, kimlik tamponunda görünür) bununla çelişmiyor.
Koyu temada aynı görünüm, kartlar ve pembe kenarlar okunuyor. Başlık ve metin "USB ses kartı yedek, takılmaz" iki temada aynı.

### 15.3 Kontrol-5 bulgusu ve düzeltmesi (15:39, zincir bittikten sonra)

**Bulgu (kontrol-5 S3-1):** F10e `beklenen_renk` ile sahne (`app.js` `kabloTon`) aynı `p.rt` alanını okuyor. § 15.1'de güvence diye
gösterilen `rehber_kablo.py --veri`, `rt`'yi yalnız şemalarda denetliyordu; parça döngüsü bakmıyordu. Düzeltmeden önce ölçüldü
(bugünkü veri, p1180): `rt.light` yanlış, `rt` silinmiş, `rt.dark` yanlış → `veri_denetle` hata **0 / 0 / 0** (üçü de kaçtı).

**Düzeltme (`tasarim/freecad/rehber/rehber_kablo.py`; F10e, metin, kural, onay kaydı değişmedi):**

- `:750–751` `veri_denetle` parça döngüsü, renk karşılaştırmasından sonra yeni:
  `if p.get("rt") != TB.ton(ids[0]): hata.append("parça %s: tema tonu %s, tablodan %s (%s)" …)`. Eksik `rt` de (`None`) hata verir.
  Eski: parça döngüsünde `rt` satırı yoktu (şemadaki `:765` karşılığı vardı).
- `bozma_denemesi` veri bozmaları (`v1–v5` sonrası) yeni: `v6` kablo parçasının `rt.light`'ı turuncu tonu #b35a00, `v7` parçanın
  `rt`'si silindi, `v8` kaynakta `TEMA_TON["yesil"]["light"]` değişti, veri eski (kontrol-5'in kaçan "kaynak değişti, veri eski"
  durumu; yeşil sınıfta yalnız CAD parçası var).

**Sınama (FreeCAD'siz, `-B`):**

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, onay kaydı tutuyor / **27 / 27** (kaynak bozmaları değişmedi) |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | GEÇER; 12 kablo parçasının 12'sinde `rt` = tablo tonu, hata 0 |
| `rehber_kablo.py --bozma-denemesi --veri …` | 0 | **35 / 35** (önce 32 / 32): v6 yakalandı (p1180 tema tonu #b35a00 ↔ tablodan #c0392b), v7 yakalandı (tema tonu None), v8 yakalandı (p1189 veri #1e7a3c ↔ tablodan #2e8b57; denetim + onay) |
| doğrudan `veri_denetle` (p1180) | — | `rt.light` yanlış 1, `rt` yok 1, `rt.dark` yanlış 1 (önce 0 / 0 / 0) |
| `rehber_denetim.py --kaynak` | 0 | ASCII 0, onaylı kritik girdi farkı **0** (kablo 90, liste 133, metin 907) |
| `py_compile rehber_kablo.py` (çıktı depo dışına) | — | temiz |

Bozma sayısına sabit bağlı kod yok: `rehber_uret.py` `veri_denetle`'yi çağırıp yalnız hata listesine bakıyor, zincir çıkış koduna
bakıyor; 27 / 27 ve 32 / 32 yalnız günlüklerde geçiyor. Bundan sonra beklenen: `rehber_kablo.py --bozma-denemesi` 27 / 27,
`--bozma-denemesi --veri` **35 / 35**. `rehber_uret.py` ve F10e bu yüzden yeniden koşulmadı (F10e kodu değişmedi; yeni satır bugünkü
veride hata vermiyor, yani üretimin kablo eşleme sonucu değişmezdi). § 15.1'deki ve F10e baş açıklamasındaki "`--veri` tablodan
denetler" cümlesi bu düzeltmeyle doğru. Açık (bilgi, kontrol-5 § 6.2): kol şemalarının `lejant` alanı ve `app.js` sabit metinleri ASCII
sınamasına girmiyor.

## 16. Kapanış (14.11, C adımı: kayıt + commit)

14.11.2026 15:45–15:55 (saat okundu). Dal `lale-duzeltme`, taban `8134519`. Kaynak, rehber metni, kurallar, onay kaydı,
`kablolar.json`, üretilmiş çıktılar ve kontrol raporları bu adımda değişmedi; yalnız kayıt belgeleri (bu günlük, `dongu-158.md`,
`karar-kuyrugu.md`, `README.md`). FreeCAD, `rehber_uret.py` ve doğrulayıcılar koşmadı. P10.7b1 bu commit'le kapandı.

### 16.1 Bağımsız bakışların hükümleri

| # | Rapor | Neye baktı | Hüküm | Sonra |
| --- | --- | --- | --- | --- |
| 1 | `F10h-kontrol.md` | A adımı, kaynak | **DÜZELTME GEREKLİ** (Ü1 CAD ad / kod, Ü2 Ö4 köprüsü, Ü3 eşleme; 15 açık iş) | düzeltme turu 1 (§ 11) |
| 2 | `F10h-kontrol-2.md` | düzeltme turu 1, kaynak | **KAYNAK GEÇER** (20 açık iş) | açık işler turu (§ 12) |
| 3 | `F10h-kontrol-3.md` | açık işler turu, kaynak | **DÜZELTME GEREKLİ** (anahtarlı bara köprüleri rehberde yok) | düzeltme turu 2 (§ 13) |
| 4 | `F10h-kontrol-4.md` | düzeltme turu 2, kaynak, kayıt → rehber tamlığı | **KAYNAK GEÇER** (G07 ve SV3 / dağıtım kartı C talimat boşluğu: montajdan önce kapanacak açık iş) | üretim + zincir (§ 14) |
| 5 | `F10h-kontrol-5.md` | üretim uyum düzeltmesi S1–S3 (§ 15.1) | önce **DÜZELTME GEREKLİ** (S3-1: `rt` parçalarda denetlenmiyordu), yeniden bakışta **UYUM DÜZELTMESİ GEÇER** | S3-1 düzeltmesi (§ 15.3) |

Döngü kuralı (`dongu-158.md` § 1 adım 4) en çok iki düzeltme turu der. Kaynakta iki düzeltme turu ve bir açık işler turu yapıldı,
dördüncü bakış geçti; ardından üretimde çıkan üç araç uyumsuzluğu (S1–S3) orkestratörce "üretim adımının uyum düzeltmesi" sayıldı ve
ayrı bir bağımsız kontrolle (kontrol-5) kapandı. Kuralın harfiyle bu üçüncü bir düzeltme turu sayılabilir: karar kuyruğunda K62
(Ahmet'in bilgisine / onayına).

**Zamanlama notu (kontrol-5 § 8):** zincirin `rehber_kablo.py --veri` adımı (14:54–15:39) S3-1 düzeltmesinden önceki kodla koştu
(`rehber_kablo.py`'nin zamanı 15:39). Yeni kod yeni veride ayrı koşularda sınandı: 15:39'daki yeniden koşular (§ 15.3: `--veri` hata 0,
veri bozması 35 / 35), kontrol-5'in yeniden bakışı (§ 8) ve bu adımın 15:47'deki koşusu (§ 16.2). Rehber verisi bu düzeltmeden sonra
yeniden üretilmedi; yeni satır bugünkü veride hata vermiyor.

### 16.2 Son sayılar

Kaynak: üretim kütüğü ve `planlama/rehber/kontrol.json` (§ 15.2), zincir (§ 15.2), S3-1 sonrası koşular (§ 15.3) ve bu adımın
FreeCAD'siz koşusu (15:47, `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`, yalnız okuyan komutlar; dördü de çıkış 0).

| Değer | Sayı | Kaynak |
| --- | --- | --- |
| Parça (rehber / mesh) | 1192 / 1192 | `kontrol.json` `ozet`; `rehber_denetim.py` (veri) |
| Adım / alt adım | 50 / 71 (geçen 50 / 71) | `kontrol.json` `ozet.adim`, `alt_adim` |
| Şema | 49 | `kontrol.json` `ozet.sema`, `denetim.sema` |
| PDF | 77 sayfa (devam 27), en küçük yazı 8,1 pt, 16079 kB | `kontrol.json` `yazdir` |
| Kablo eşleme | tablo 74, çizilen 51, çizilmeyen 23, eşleşmeyen 0, GEÇTİ | `kontrol.json` `kablo_esleme`; `rehber_kablo.py --veri` |
| Geometrik eşleme | hata 0, bilgi 4, ayırt edilemeyen çift 1 (A03 ↔ G22) | `rehber_kablo.py --veri` |
| Perdelenme | alt adımlarda gerekçesiz 0, istisna 117, toplam gizli 264 | `kontrol.json` `perdelenme` |
| Uçuş | 340 satır, çarpışan 0, istisna 16 | § 15.2 |
| Rehber denetimi (veri) | ASCII 0, elektrik 0, yasak 0 (istisna 5), zorunlu eksik 0 / 71 | `rehber_denetim.py` |
| Kaynak denetimi | metin 531, bütün sayılar 0, onay farkı 0 (kablo 90, liste 133, metin 907), tamlık 65 öğe / eksik 0 / muaf 21, kablo kimliği 68 / 74 | `rehber_denetim.py --kaynak` |
| Kablo tablosu | `kablolar_uret.py --kontrol` güncel; bozma 145 | bu adım; § 15.1 |
| Bozma sayıları | kablo denetimi 145; kaynak denetimi 76 / 76; `rehber_kablo` kaynak 27 / 27, veri 35 / 35 | § 15.1, § 15.3 |
| Zincir 2–10 | hepsi çıkış 0; F10e `renk_sahne` yanlış 0 (`renk_demo` bilinen karar, çıkışa girmiyor) | § 15.2 |

### 16.3 Doğrulanamayanlar

- 18 ↔ 16 AWG ve 12 AWG kalınlık kademeleri gözle (o kademelerde çizilen şema yok, § 14.4).
- CSI kablosunun rengi (C01 çizilmiyor); PDF'in görüntüsü doğrudan (yalnız metni ve `yazdir.html` karesi).
- Kontrollerin geçici kopyadaki bozmaları (§ 9 madde 6) üretim adımında koşulmadı.
- Zincirin `--veri` adımının yeni kodla koşmuş hâli (zamanlama notu, § 16.1).
- Sahnedeki renkler yalnız F10e kütüğü / JSON'u ve kare bakışıyla; bağımsız piksel ölçümü yalnız F10f `kablo_kare`.

### 16.4 Açık işler (karar kuyruğunda)

- **K62:** döngü kuralı ↔ bu paketteki tur sayısı (kayıt; Ahmet'in bilgisine / onayına).
- **K63:** montajdan önce kapanacak iki talimat boşluğu (kontrol-4 § 3.1-1 / -2: G07 + `R-aku-olcum`; SV3 + dağıtım kartı C): P10.7b2'nin ilk işi.
- "Karar değil, iş" bölümünde P10.7b1 maddeleri: kontrol-4'ün öbür açık işleri ve önceki turlardan kalanlar; üretimde görülenler
  (§ 14.4 kare bakışı); kontrol-5'in açık işi (kol şemalarının `lejant` alanı, `app.js` / `yazdir.html` sabit metinleri ASCII
  sınamasına girmiyor). Hepsi P10.7b2.

### 16.5 Commit öncesi

- Gizlilik taraması (gidecek farkın tamamı: izlenen dosyaların farkı, yeni dosyalar, `rehber-veri.json` / `.js`, PDF metni ve üst
  verisi, PNG / PDF / veri baytları): bu günlükteki dört geçici klasör anılışı sadeleştirildi (§ başı, § 4 tablosu, § 9, § 12.6
  başlığı). Öbür eşleşmeler yanlış alarm: sonar pin adı (`rehber_denetim.py`, onay kaydı), kontrol-4'ün gizlilik cümlesindeki bir
  sözcük, `rehber-veri.js`'te telefon kalıbına uyan ondalık sayılar. Rastgele dört kare açıldı; hepsi başsız tarayıcı karesi, ekran
  görüntüsü yok.
- Commit'e girmeyen paket dışı 14 dosya: `tasarim/freecad/kabuk/gorsel/*.png` (13), `tasarim/freecad/montaj/yerlesim-kontrol.json`.
  `__pycache__` yok.
