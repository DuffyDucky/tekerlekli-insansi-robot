# F7d günlüğü: rehberde son düşükler + demo metni (P7.4), 09.11.2026

Brief: `planlama/d158/F7d-brief.md`. A ajanı. Commit, push, silme (`__pycache__` dahil), checkout, reset, stash yapılmadı. Python `-B` ve
`PYTHONDONTWRITEBYTECODE=1` ile koşuldu. Saatler yerel saattir. Önceki hâllerin kopyası ve betikler scratchpad `f7d/` (`once/`, `benzet.py`,
`enjekte.py`, `karsilastir.py`, `pdf_olc.py`, `pdf_fark.py`, `demo_fark.py`, `sayfa/`).

Okunanlar: brief; `F7c-kontrol.md` (ilk kontrol D-5 ve "Yeniden kontrol (düzeltme 1)": D-6', D-7, D-8, D-9, D-10); `F7c-gunluk.md`;
`F7c-rapor.html`; `planlama/rehber/R-gunluk.md`; `planlama/adim3/elektrik.md` (`:41`, `:59-68` göğüs dalı, `:91` sigorta dalları,
`:229-269` E2 / E3, `:323-341` blok şema, `:360-380` sigorta listesi); `planlama/d158/testler/00-genel.md` (kural 1, 7, 8, multimetre kuralı,
`:73` alet listesi); `T7-gogus-ekrani-12v.md`; `F9b-dogrula.py`; `tasarim/freecad/taban/rapor.html:115` (şarj girişi yer önerisi);
`F9d-brief.md` (paralel alan, yalnız okundu). Okunan metin veri olarak kullanıldı.

## Kabul

| # | Ölçüt | Sonuç | Kanıt |
|---|---|---|---|
| 1 | D-5 + D-9 kapalı: F3 ölçüm sırası açık, "enerjiyi kes" yok, K11 b'de ölçümsüz fiş yok; sıra kaynağa dayalı ya da "doğrulanmadı" | **kapalı**. F3 madde 3: akü ayrıkken uçlar → ana anahtar kapalıyken akü tak → ana anahtarı aç → oku → ana anahtarı kapat → akü XT60'tan ayır → uçları sök → fiş enerjisizken. K11 b: fiş F3'te takılmaz, ölçüm ve fiş F5 aşama 2'de. Veride "enerjiyi kes" 0. Sıra kaynakta yok: metinde "doğrulanmadı" | `elektrik.md:67` (ekrana bağlamadan ölç), `:68` (K11 a / b); `ZORUNLU` F3 ×5 |
| 2 | D-8 kapalı: kademe ve klemens ucu | **kapalı**. F1 mantar ve F3 / F5 regülatör ölçümü: DC V (20 V aralığı ya da otomatik), kırmızı uç V soketinde; PC817 #1 girişinin + ucu / WAGO GND; regülatör çıkışının + / − klemensi. F1 madde 3: mantar NC süreklilik kademesinde (akü ayrık). Aralık, + uç ve süreklilik denemesi kaynakta yok: "doğrulanmadı" | `00-genel.md:58-62`, `:73`; `elektrik.md:234` (14,6 V), `:249-251`; `ZORUNLU` F1 ×4, F3 ×1 |
| 3 | D-10 kapalı: şarj girişi rehberde, adım ve "takılı değil" listesi kaynağa dayalı | **kapalı (yer ve bağlantı noktası doğrulanmadı)**. K1 madde 1 kablo (akü + hattı, ana anahtar öncesi, şarj 10 A yuvası); F1 madde 5 etek konnektörü (delik modelde yok); F1 aşama 1 listesinde "şarj girişi mini 10 A takılı değil"; F5 aşama 2'de de takılı değil, F5 notu | `elektrik.md:41`, `:91`, `:372`; `taban/rapor.html:115`; `ZORUNLU` F1, F5 |
| 4 | D-6' kapalı | **kapalı**. "birleştir", "birbirine bağla / lehimle / değdir / tuttur / kıskaçla" (anahtarlama / besleme nesnesi bağlamında), "röleyi elle kapat", "açtıktan / taktıktan / verdikten sonra … tak" kalıpları; S1–S3 ve sökme sırası için `ZORUNLU` satırları | enjeksiyon Y1–Y17 |
| 5 | D-7 kapalı: pencere cümle / bağlaç sınırında | **kapalı**. Pencere sıra bağlacında (sonra, bitince, ardından, sonunda, en son) ve enerjiyi bitiren ifadede (ana anahtarı kapat, aküyü ayır, XT60'tan ayır, enerjiyi kes) kesilir; virgül ve "ve" kesmez | N1–N4 temiz; Y12 (liste içi "ve") yakalandı |
| 6 | Yeni enjeksiyonların hepsi yakalanır, olumsuzların hepsi geçer, gerçek veride 0 | **23 / 23** yakalandı; **10 / 10** olumsuz temiz (D-7 cümlesiyle 4); gerçek veride yasak 0 (istisna 5), zorunlu eksik 0 / 35. Regresyon: B'nin J 14 / 14, P1–P8 8 / 8 | aşağıda |
| 7 | Demo metni gerçeğe uygun | "model kopyasının güncelliği" kalktı; `F9b-dogrula.py`'nin gerçek denetimleri yazıldı. Sayfada başka "kopya" iddiası yok (şablon ve demo taraması: 1 / 1) | `viewer-template.html:260` |
| 8 | Tüm kontroller 0 | `rehber_uret.py --veri-yok` 0 (50/50, konsol 0, 1192 ↔ 1192, 360 px 7 × 0, PDF 54 sayfa, her adım ≥ 1, taşan 0, en küçük 8,1 pt, eşleme güncel); denetim 0; `demo_uret.py` 0; `F9b-dogrula.py` 0; `carpisma_kos.py kontrol` 0; `regresyon.py --yazma` 0 | komutlar |

## Komutlar (saat, çıkış kodu)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 20:20 | `rehber_denetim.py` (başlangıç) | 0 | zorunlu 0 / 23, yasak 0 (istisna 4) |
| 20:20 | `carpisma_kos.py kontrol` / `regresyon.py --yazma` (başlangıç) | 0 / 0 | izlenen 17 dosya aynı / GEÇER |
| 20:2x | scratchpad `benzet.py` (yeni metin bellek içinde mevcut veriye + yeni denetim) | 1 → 0 | önce ASCII 21 (doğru Türkçe kelimeler: kademesine, soketine, klemensinin …) → `ASCII_TAMAM`; sonra zorunlu 0 / 35, yasak 0, istisna 5 |
| 20:2x | scratchpad `enjekte.py` (benzetilmiş veri) | 0 | 23 / 23, 10 / 10, J 14 / 14, P 8 / 8 |
| 20:26 | FreeCAD süreci 0, boş bellek 3,43 GB, kilit "boş" (6 bayt) → kilit "F7d (P7.4, A) 2026-11-09 20:26 rehber_uret.py --gorsel-yok (veri + mesh)" → `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_uret.py --gorsel-yok` → kilit "boş" (baştaki 6 baytla aynı) | 0 | veri 22 s; mesh 288 / 1192, 189.934 üçgen, GLB 2,56 MB, 50 adım |
| 20:26 | `karsilastir.py` (önceki veri ↔ yeni veri ↔ benzetilmiş veri) | — | parça farkı 0 / 1192; değişen adım alanları yalnız K1 `is_`, F1 `is_` / `kontrol`, F3 `is_` / `kontrol`, F5 `is_` / `kontrol` / `not_`; benzetilmişle fark 0; `robot.glb` sha1 aynı (`9458b9e67135`) |
| 20:26 | `rehber_denetim.py` + `enjekte.py` (gerçek veri) | 0 / 0 | zorunlu 0 / 35, yasak 0 (istisna 5); 23 / 23, 10 / 10, 14 / 14, 8 / 8 |
| 20:27–20:31 | `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` | **0** | 50 / 50, konsol 0, her parça tek adımda; yazdır görüntüsü 50; telefon 7 × 360 / 0; PDF **54** sayfa (devam 4), HTML 54, eşleme tutarlı, taşan yok, en küçük DOM 8,1 / PDF 8,1 pt, 3.926 kB; denetim temiz |
| 20:3x | `pdf_olc.py` (PyMuPDF) | — | 54 sayfa; en küçük 8,1 pt; 8 pt altı 0; "Sayfa i / 54" 54 sayfada doğru; üst bilgiden eşleme = `kontrol.json` `yazdir.sayfa_esleme` |
| 20:3x | `py -3 -B -X utf8 tasarim/cad/demo_uret.py` | 0 | 127 sayı anahtarı, 14 karar, 153 kalem, 1192 düğüm, 163 KB |
| 20:3x | `demo_fark.py` (önceki demo ↔ yeni) | — | 127 anahtarın hiçbiri değişmedi; kaynak bloğunda yalnız `rehber-veri.json` parmak izi (`85a3cc196adb` → `74137332d78e`); blok dışında yalnız "Bu sayfa hakkında" satırı |
| 20:3x | `py -3 -B -X utf8 planlama/d158/F9b-dogrula.py` | **0** | GECER (hata 0), tarayıcı denetimi dahil |
| 20:3x | `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | **0** | izlenen 17 dosyanın özetleri kayıtla aynı |
| 20:3x | `py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` | **0** | GEÇER (hepsi okundu, kötüleşen yok) |
| 20:3x | `rehber_denetim.py` (son) | 0 | aynı |

Koşulardan sonra FreeCAD süreci 0, `lale-rehber` / `f9b-chrome` profilli Chrome süreci 0, kilit "boş".

**`--veri-yok` yeterli mi?** Hayır (F7c'deki tespit geçerli): adım metni `rehber-veri.json`'a yalnız FreeCAD altında koşan `rehber_veri.py` ile
girer. Veri aşaması bir kez kilit altında koşuldu; geometri değişmedi (parça farkı 0, GLB aynı).

## Kaynak eşlemesi

| Metin | Kaynak | Durum |
|---|---|---|
| Göğüs regülatörü ekrana bağlanmadan ölçülür | `elektrik.md:67`; T7 "Ekranı regülatör ayarlanmadan bağlama" | kaynakta var |
| K11 a: ana anahtar sonrası, röle öncesi (F3'te ana anahtarla enerjilenir); b: anahtarlı bara (F1 takılıp devreye alınana kadar enerjisiz) | `elektrik.md:68`, `:91`, `:252`, `:365` | kaynaktan çıkarım |
| Ölçüm sırası (akü ayrıkken uç, ana anahtar kapalıyken akü, aç, oku, kapat, ayır, uçları sök) | yok (F1 aşama 1'deki rehber sırası; kural 7: ölçü ucu enerji yokken) | **doğrulanmadı** (metinde) |
| DC V; akım kademesindeki multimetre iki nokta arasına değmez; kırmızı uç V soketine | `00-genel.md:58-62` | kaynakta var |
| 20 V aralığı (akü en çok 14,6 V) | `elektrik.md:234` | aralık çıkarım, **doğrulanmadı** |
| PC817 #1 girişinin + ucu = mantar sonrası düğüm | `elektrik.md:235`, `:249-251` | + uç etiketi **doğrulanmadı** |
| Mantar NC sürekliliği (akü ayrık) | alet listesinde süreklilik var (`00-genel.md:73`), deneme kaynakta yok | **doğrulanmadı** |
| Şarj girişi: XT60 → akü + (ana anahtar öncesi), mini 10 A, kapaklı yuva | `elektrik.md:372`, `:41`, `:91` | kaynakta var |
| Şarj girişinin kablolandığı adım K1 (ana hat burada), konnektör F1 (etek) | `taban/rapor.html:115` (yer önerisi etek üst plakası arka, delik açık iş); modelde parça ve delik yok | **doğrulanmadı** |
| Ana sigortadan önce mi sonra mı | yok | **doğrulanmadı** |
| Aşama 1 ve 2'de şarj 10 A takılı değil | `:372` (ana anahtar öncesi: ana anahtar kesmez) | kaynaktan çıkarım; takılma sırası **doğrulanmadı** |

## Önce / sonra metin

**K1 madde 1** (sonuna eklendi): "Şarj girişi: akü + hattından, ana anahtardan önce, kapaklı mini sigorta yuvası (şarj 10 A) → XT60 şarj
girişi ucu (`planlama/adim3/elektrik.md` sigorta listesi). Uç bantlı bırakılır, F1'de etekteki şarj girişine bağlanır; sigortası takılmaz
(F1 aşama 1). Ana sigortadan önce mi sonra mı bağlanacağı ve kablo kesiti kaynakta yok, doğrulanmadı."

**F1 madde 3.** Önce: "Acil stop mantarını panel somunuyla tak, K1'de bırakılan ucu bağla." Sonra: "Acil stop mantarını panel somunuyla tak.
Bağlamadan önce mantarı multimetrenin süreklilik kademesinde dene: NC uçları arasında mantar serbestken bip var, basılıyken yok (akü ayrık;
kaynakta yok, doğrulanmadı). Sonra K1'de bırakılan ucu bağla."

**F1 madde 5 (yeni):** "XT60 şarj girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok
(`tasarim/freecad/taban/rapor.html` şarj notu; doğrulanmadı). Delik açıldıysa konnektörü tak, K1'de bırakılan şarj ucunu akü ayrıkken bağla;
açılmadıysa uç bantlı kalır. Şarj 10 A sigortası takılmaz (aşama 1 listesi)."

**F1 kontrol, aşama 1.**
- Önce: "… XL4016 hat sigortaları (A 7,5 A, B 7,5 A, C 5 A) ve göğüs ekranı mini 2 A takılı değil (…): anahtarlı bara, kafa ve göğüs ekranı
  dalı enerjisiz, Pi enerjisiz. …"
- Sonra: "… XL4016 hat sigortaları (A 7,5 A, B 7,5 A, C 5 A), göğüs ekranı mini 2 A ve şarj girişi mini 10 A takılı değil (…): anahtarlı bara,
  kafa ve göğüs ekranı dalı enerjisiz, Pi enerjisiz. Şarj girişi ana anahtardan önce akü + hattında: sigortası takılı olsaydı ana anahtar
  kapalıyken de gerilimli olurdu. …"
- Önce: "Mantar ölçümü: akü ayrıkken multimetrenin kırmızı ucunu arayüz kartındaki PC817 #1 giriş klemensine (mantar sonrası düğüm, E3),
  siyah ucunu …"
- Sonra: "Mantar ölçümü: akü ayrıkken multimetreyi DC V kademesine al (20 V aralığı ya da otomatik; akü en çok 14,6 V), kırmızı ucu V soketine
  tak: 10 A soketinde kalırsa multimetre bu noktayı GND'ye bağlar ve F5 2 A atar (`planlama/d158/testler/00-genel.md` multimetre kuralı).
  Kırmızı ucu arayüz kartındaki PC817 #1 giriş klemensinin + ucuna (mantar sonrası düğüm, E3), siyah ucunu …"
- Son cümle: "Bu aşamalar, sigorta sırası, ölçü noktası ve "yerden kesik" düzeni …" → "Bu aşamalar, sigorta sırası, ölçü noktası, klemensin
  + ucu, multimetre aralığı ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı".

**F3 madde 3 (D-5, D-9).**
- Önce: "3. 11,6" ekranı (kasalı) cebe koy. Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranı mini 2 A sigortasını tak (F1 aşama 1'de
  takılı değildi; dal girişi K11'in varsayılanı a: ana anahtar sonrası, röle öncesi; b seçilirse bu ölçüm F5 aşama 2'ye kalır,
  doğrulanmadı). 12 V fişini takmadan önce regülatör çıkışını yeniden ölç: 12 V (K2'de ayarlandı; ölçünce enerjiyi kes). Sonra K2'de
  bırakılan HDMI ve 12 V uçlarını enerjisizken tak (90° fişler)."
- Sonra: "3. 11,6" ekranı (kasalı) cebe koy. Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranı mini 2 A sigortasını tak (F1 aşama 1'de
  takılı değildi). Dalın girişi K11'e bağlı (`planlama/adim3/elektrik.md` göğüs ekranı dalı). K11 a (varsayılan; ana anahtar sonrası, röle
  öncesi): 12 V fişini takmadan önce regülatör çıkışını yeniden ölç. Akü ayrıkken multimetreyi DC V kademesine al (20 V aralığı ya da
  otomatik), kırmızı ucu V soketine tak; kırmızı ucu regülatör çıkışının + klemensine, siyah ucunu çıkışın − klemensine bağla (kart üstü
  yazıya göre). Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç, çıkışı oku: 12 V (K2'de ayarlandı). Bitince ana anahtarı
  kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Sonra K2'de bırakılan HDMI ve 12 V uçlarını enerjisizken tak (90° fişler). K11 b
  (anahtarlı bara): dal F5 aşama 2'de devreye alınana kadar enerjisiz, burada ölçülemez. 12 V fişini bu adımda takma, ucu bantlı kalsın;
  yalnız HDMI'yi enerjisizken tak. Ölçüm ve 12 V fişi F5 aşama 2'de. Ölçüm sırası ve ölçü noktası kaynakta yok, doğrulanmadı."
- **F3 kontrol (yeni):** "K11 a: regülatör çıkışı 12 V okundu, 12 V fişi akü XT60'tan ayrıldıktan sonra takıldı. K11 b: 12 V fişi takılmadı,
  ucu bantlı (F5 aşama 2)".

**F5 madde 2 (aşama 2).** Eklenenler (yerinde):
- sigortalardan sonra: "Şarj girişi mini 10 A bu aşamada da takılı değil. K11 b ise (göğüs dalı anahtarlı barada; F3 madde 3): akü ayrıkken
  multimetreyi F3'teki gibi göğüs regülatörü çıkışına bağla (DC V; 12 V fişi takılı değil), teli kolların ve tekerlerin erişim alanının
  dışına çıkar.";
- ön şarj dizisinden sonra: "K11 b ise regülatör çıkışını erişim alanının dışından oku: 12 V.";
- sonda: "Bitince ana anahtarı kapat, aküyü XT60'tan ayır (… E3, E9)." → "… (… E3, E9). K11 b ise sonra ölçü uçlarını sök ve göğüs 12 V
  fişini enerjisizken tak (üst arka servis kapağı açıkken; fişe bu sırada erişim ölçülmedi)."
- **F5 kontrol (yeni):** "K11 b ise: göğüs regülatörü çıkışı 12 V okundu, 12 V fişi akü XT60'tan ayrıldıktan sonra takıldı".
- **F5 not (yeni):** "Şarj girişi mini 10 A iki aşamada da takılı değil: şarj girişi ana anahtardan önce akü + hattında (… sigorta listesi).
  Sigorta ilk şarjdan önce, akü XT60 ayrıkken takılır; bu sıra kaynakta yok, doğrulanmadı".

## Denetim (`rehber_denetim.py`) değişiklikleri

- **Yasak kalıplar (D-6'):**
  - "köprüleme (birleştir)" ve "köprüleme (birbirine bağla)": nesne (mantar, acil stop, NC, ana anahtar, sigorta, röle, kontak, "N V",
    artı, eksi) + 60 karakter içinde "birleştir…" ya da "birbirine bağla / değdir / lehimle / tuttur / kıskaçla…". Olumsuz biçim
    ("birleştirme", "bağlamayın", "bağlanmaz") istisna. "GND uçlarını WAGO yıldız noktasında birleştir" ve "S2 kablosunu uzatmayla
    birleştir" tutmaz (nesne yok).
  - "röleyi elle kapat / çek / bastır": gerçek verideki F5 notu "röleler elle kapatılmaz" olumsuz biçim istisnası (istisna 4 → 5).
  - Enerji önekine: "ana anahtarı açtıktan sonra / açınca / açıldıktan sonra", "aküyü (XT60'tan) taktıktan sonra / takınca / bağladıktan
    sonra", "enerji verdikten sonra / verince / verildikten sonra".
- **Pencere (D-7):** `[^.;!?\n]{0,120}?` → aynı karakter sınıfı, ama sıra bağlacında (sonra, bitince, ardından, sonunda, en son) ya da
  enerjiyi bitiren ifadede (ana anahtarı kapat, aküyü (XT60'tan) ayır, XT60'tan ayır, enerjiyi kes) durur. Virgül ve "ve" kesmez:
  F7c'deki J18 gerekçesi (liste içi "F1 (20 A), F3 (5 A, kafa) ve … tak") korunur (Y12).
- **`ZORUNLU` 23 → 35:** F1 mantar ölçü noktası deseni "+ ucuna" ile; F1 "akü ayrıkken multimetreyi DC V kademesine al … V soketine",
  "XT60'tan ayır, sonra ölçü uçlarını sök", "şarj girişi mini 10 A takılı değil", "süreklilik kademesinde"; F5 "Akü XT60 ayrık, ana anahtar
  kapalıyken F1 (20 A) … tak", "kollar düşer", "Şarj girişi mini 10 A bu aşamada da takılı değil"; F3 "Akü XT60 ayrık, ana anahtar
  kapalıyken göğüs ekranı mini 2 A", "Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç", "Bitince ana anahtarı kapat,
  aküyü XT60'tan ayır, sonra ölçü uçlarını sök", "K11 b … ölçülemez. 12 V fişini bu adımda takma", "DC V kademesine".
- `ASCII_TAMAM`'a bu turun doğru kelimeleri: anahtardan, etekteki, sigortadan, kesiti, kademesinde, serbestken, bip, gerilimli, olurdu,
  multimetreyi, kademesine, otomatik, soketine, soketinde, atar, klemensinin, ucuna, klemensin, okundu, barada, teli.
- Gerçek veride: yasak 0; istisna 5 (K1 ×2, E3a, E4 "köprülenmez / köprülenmedi"; F5 "röleler elle kapatılmaz"), hepsi doğru olumsuz biçim.
  Gerçek veride enerji öneki isabeti: yalnız F1 "gerilimli olurdu" (fiil yok, bulgu değil).

## Enjeksiyon (scratchpad `enjekte.py`)

Yöntem: depodaki `rehber_denetim.py` ve `rehber_metin.py`; veri önce benzetilmiş kopyada, sonra 20:26 gerçek verisinde (`rehber-veri.json`)
bellek içinde bozuldu. Depo değişmedi. Yakalanma yalnız hedeflenen denetimle (yasak, zorunlu, kopya eki > 0) sayıldı. Temiz kopya: geçti,
yasak 0, istisna 5, zorunlu eksik 0 / 35, kopya eki 0, ASCII 0. İki veride sonuç aynı.

| # | Enjeksiyon | Sonuç |
|---|---|---|
| Y1 | F1'e "Ölçüm için mantar NC uçlarını birleştir." (F7c-kontrol K1) | yakaladı (yasak: birleştir) |
| Y2 | F1'e "Ölçerken mantarın iki ucunu kıskaçla birbirine bağla." (K3) | yakaladı (birbirine bağla) |
| Y3 | F5'e "Ana anahtarı açtıktan sonra F1'i tak." (K5) | yakaladı (enerji öneki) |
| Y4 | F5'e "Yazılım hazır değilse röleyi elle kapat." (K6) | yakaladı (röleyi elle kapatma) |
| Y5 | K1'e "Ana anahtar uçlarını tek tel ile birleştir." | yakaladı |
| Y6 | E3a'ya "Gerekirse iki 5 V çıkışını birbirine lehimle." | yakaladı |
| Y7 | F3'e "Sigorta yuvasının iki ucunu birbirine bağla." | yakaladı |
| Y8 | F1'e "Acil stop kontaklarını birbirine değdir." | yakaladı |
| Y9 | F1'e "Mantar takılı değil, NC uçlarını birleştir." (olumsuzlama başka yan cümlede) | yakaladı |
| Y10 | F5'e "Aküyü XT60'tan taktıktan sonra servo konnektörünü sök." | yakaladı |
| Y11 | F3'e "Enerji verdikten sonra 12 V fişini tak." | yakaladı |
| Y12 | F5 "Akü XT60 ayrık, ana anahtar kapalıyken F1 (20 A)" → "Ana anahtar açıkken F1 (20 A)" (liste içi virgül ve "ve") | yakaladı (yasak + zorunlu) |
| Y13 | F1'e "Ana anahtar açıkken mantar klemensini sık, bitince aküyü ayır." (sınırdan önceki fiil) | yakaladı |
| Y14 | F3 göğüs 2 A cümlesi silindi (F7c-kontrol S1) | yakaladı (zorunlu) |
| Y15 | F5 sigorta cümlesi silindi (S2) | yakaladı (zorunlu) |
| Y16 | F5 "kollar düşer" iki yerde silindi (S3) | yakaladı (zorunlu) |
| Y17 | F1 sökme sırası bozuldu: "ölçü uçlarını sök, ana anahtarı kapat, aküyü ayır" (K11) | yakaladı (zorunlu) |
| Y18 | F1 "akü ayrıkken multimetreyi" → "enerji varken multimetreyi" (K10) | yakaladı (zorunlu) |
| Y19 | F1 "DC V kademesine" → "akım kademesine" (D-8) | yakaladı (zorunlu) |
| Y20 | F1 "şarj girişi mini 10 A takılı değil" silindi (D-10) | yakaladı (zorunlu) |
| Y21 | F3 "aküyü XT60'tan ayır" silindi (D-5) | yakaladı (zorunlu) |
| Y22 | F3 K11 b "fişini bu adımda takma" → "tak" (D-9) | yakaladı (zorunlu) |
| Y23 | F3 "Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç" → "Aküyü tak, ana anahtarı aç" (D-5) | yakaladı (zorunlu) |

**Sonuç: 23 / 23 yakalandı.**

| # | Olumsuz deneme (doğru metin) | Sonuç |
|---|---|---|
| N1 | F1'e D-7 cümlesi (P5): "Ana anahtar açıkken yalnız BMS ışığını gözle, bitince ana anahtarı kapat, aküyü ayır ve ölçü uçlarını sök" | temiz |
| N2 | F1'e aynı cümle "sonra" ile: "… gözle, sonra ana anahtarı kapat, aküyü XT60'tan ayır ve ölçü uçlarını sök" | temiz |
| N3 | F5'e bağlaçsız: "XT60 takılıyken yalnız gerilimi oku, ana anahtarı kapatınca aküyü ayır ve uçları sök" | temiz |
| N4 | F5'e "Enerji varken yalnız ekranı izle, ardından enerjiyi kes ve hub kablosunu tak" | temiz |
| N5 | F1'e "Mantar NC uçlarını birleştirme." | temiz (olumsuz biçim) |
| N6 | E3a'ya "İki 5 V hattını birbirine bağlamayın." | temiz (olumsuz biçim) |
| N7 | K1'e "GND uçlarını WAGO yıldız noktasında birleştir." | temiz (köprüleme nesnesi yok) |
| N8 | G2'ye "S2 kablosunu uzatmayla birleştir." | temiz |
| N9 | F5'e "Röleler hiçbir zaman elle kapatılmaz." | temiz |
| N10 | F5'e "Ana anahtarı açtıktan sonra yalnız BMS ışığını gözle." | temiz (fiil yok) |

**Sonuç: 10 / 10 temiz** (D-7 cümlesiyle 4 deneme). F7c regresyonu: B'nin J1–J12, J17, J20'si (yasak türü; J17 yeni metne uyarlandı)
**14 / 14** yakalandı; P1–P8 **8 / 8** temiz (P5 artık temiz).

## PDF

- 54 sayfa (PyMuPDF; `kontrol.json` `pdf_sayfa` 54, `html_sayfa` 54); en küçük yazı **8,1 pt** (PyMuPDF, 54 sayfanın
  hepsinde; DOM 8,1); 8 pt altı sayfa 0; "Sayfa i / 54" 54 sayfada doğru.
- Eşleme (`kontrol.json` `yazdir.sayfa_esleme`, üst bilgiden kurulanla aynı): adım i → i + 1 (0…30); 31 (E4) → 32, 33; 32 (K2) → 34, 35;
  i → i + 3 (33, 34); **35 (F3) → 38, 39**; i → i + 4 (36…48); **49 (F5) → 53, 54**. Devam sayfası 4.
- Metni değişen sayfalar (önceki PDF ile saat maskeli karşılaştırma, `pdf_fark.py`): adım 17 (s. 18), 33 (s. 36), 35 (s. 38 + yeni devam
  s. 39), 49 (s. 53, 54). **Bakılan sayfalar (90 dpi, scratchpad `f7d/sayfa/`):**
  - 18 (K1): madde 1'de şarj girişi cümlesi; tek sayfa, taşma yok.
  - 36 (F1): madde 3 süreklilik, madde 5 şarj girişi; kontrol listesinde aşama 1 tam (şarj 10 A takılı değil, DC V, V soketi, + ucu);
    tek sayfa.
  - 38 (F3): madde 3'te K11 a / b metni tam, kontrol listesinde yeni satır; 39: devam, yalnız "Erişim notu".
  - 53 (F5): aşama 2 tam (şarj 10 A, K11 b uçları, okuma, fiş), notlarda şarj notu; 54: devam, kontrol listesi, kablo, erişim.
- Hepsinde metin doğru adımda, kesik satır yok; en küçük yazı alt / üst bilgi. PDF metninde ve metasında yerel kullanıcı yolu 0.

## Demo (madde 5)

- `tasarim/cad/viewer-template.html:260`, önce: "Doğrulama: `planlama/d158/F9b-dogrula.py` (her sayının kaynak JSON'la aynı olduğunu,
  model kopyasının güncelliğini ve açık kararların durumunu denetler)."
- Sonra: "Doğrulama: `planlama/d158/F9b-dogrula.py`. Denetledikleri: sayfadaki her sayının kaynak JSON'la aynı olduğu ve kaynağa
  bağlanmamış sayı kalmadığı; maliyetin `planlama/maliyet.json`'dan aynı hesapla çıktığı; sayfanın modeli kopya tutmadan, montaj
  rehberinin dosyalarından göreli bağlantıyla okuduğu ve bu dosyaların o anki hallerinin birbiriyle tutarlı olduğu (`robot-glb.js`
  içindeki model = `robot.glb`, `rehber-veri.js` = `rehber-veri.json`, her model düğümü parça listesinde); "karar bekliyor" görünen her
  kararın kuyrukta açık olduğu; sayfadaki eklem sınırlarının (öneri dosyası) `kod/ortak/eklem_sinirlari.json` ile sayısal aynı olduğu;
  servo sayısı, ekran boyları ve maliyet notu işaretleri gibi sayfa iddiaları; eski boy sayısının gerekçesiz geçmediği. Tarayıcıyla da
  açar: konsol hatası yok, model yüklendi, telefon genişliğinde yatay kaydırma yok."
- Dayanak: `F9b-dogrula.py` başlık açıklaması 1–8 ve `main()` ([1] data-k, [2] sayı taraması, [3] maliyet, [4] model göreli bağlantı
  KT-F9b-2, sabit sha yok, [5] kararlar, [6] eklem / servo / ekran / işaret iddiaları, [7] eski 1,65 araması, [8] tarayıcı: konsol,
  `data-hazir`, 360 px).
- Başka "kopya" iddiası: şablon ve demo HTML'inde "kopya" geçen tek yer bu satırdı (1 / 1). `demo_uret.py`'deki "kopya değil" yorumu
  doğru, dokunulmaz.
- Yeni metinde rakam yok (F9b sayı taraması bağsız sayı saymaz), "1,65" yok.
- Demo yalnız `demo_uret.py` ile üretildi; 127 sayı anahtarının hiçbiri değişmedi.

## Dokunulan dosyalar (commit listesi)

Değişen (kaynak): `tasarim/freecad/rehber/rehber_metin.py`, `tasarim/freecad/rehber/rehber_denetim.py`, `tasarim/cad/viewer-template.html`,
`planlama/rehber/R-gunluk.md`.

Değişen (üretilen): `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js`, `planlama/rehber/kontrol.json`,
`planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-17.png`, `adim-33.png`, `adim-35.png`, `adim-49.png`,
`telefon-360-adim-35.png`, `telefon-360-adim-49.png`, `tasarim/Robot-Tasarim-Demosu.html` (yalnız `demo_uret.py`). Öbür PNG'ler,
`robot.glb`, `robot-glb.js`, `rehber_veri.py`, `rehber_uret.py`, `yazdir.html` bayt bayt aynı (sha1 karşılaştırması).

Yeni: `planlama/d158/F7d-gunluk.md` (bu dosya); `planlama/d158/F7d-brief.md` (orkestratörün, bu paket yazmadı).

Girmez: `planlama/d158/FREECAD-KILIT.txt` (yalnız koşu süresince yazıldı, sonda baştaki 6 baytla aynı "boş"); `__pycache__/` (izlenmiyor;
FreeCAD koşusu yazdı, silinmedi). Çalışma ağacındaki öbür değişiklikler (`carpisma_kos.py`, `kafa_gorsel.py`, `omuz_baski.py`,
`taslak-170/*`, `kabuk/gorsel/*.png`, `yerlesim-kontrol.json`, `dongu-158.md`, F9d dosyaları) bu paketin değil. Rehber betiklerinde başka
ajanın değişikliği yoktu (`git diff` yalnız bu paketin parçalarını gösteriyor).

sha1 (ilk 12, önce → sonra): `rehber_metin.py` 96d9182310f8 → 64c5df86198c; `rehber_denetim.py` 2e9fb8230d9e → 158d2c8f097a;
`viewer-template.html` 6e6f03d9a091 → a6427ed1a360; `rehber-veri.json` 09ca1380e7b3 → da04cf4af2b0; `kontrol.json` 78a767f30e1c →
7c755a6fe092; PDF 0fd7c550afa2 → 65f35923dcb2; demo d3f8fcd89029 → 53e6b4c89ff6.

Ad / yol: yerel kullanıcı yolu taraması (bu paketin yazdığı metin dosyaları, `kontrol.json`, demo, PDF metni ve metası) 0. Takma ad ve soyad
yazılmadı.

## Açıklar

1. **Şarj girişinin yeri ve bağlantı noktası doğrulanmadı:** modelde konnektör ve etek deliği yok (`OZET.md` "tasarım kararları bekleyen");
   ana sigortadan önce mi sonra mı bağlanacağı kaynakta yok. Konnektör `maliyet.json`'da panel **erkek** (XT60E-M): şarj sigortası takılı ve
   akü bağlıyken açıkta duran pimler gerilimli olur (ana anahtar kesmez). Cins seçimi ve kapak ayrı karar (Ahmet / tasarım); rehber bu turda
   sigortayı hiç taktırmıyor.
2. **Ölçüm sırası, 20 V aralığı, PC817 #1 "+ ucu", regülatör "+ / − klemensi" ve mantar süreklilik denemesi** kaynakta yok; metinde
   "doğrulanmadı". Klemens etiketleri modül / kart gelince bakılmalı.
3. **K11 b'de fişe F5'te erişim ölçülmedi:** ekran ve çerçeve takılıyken 12 V fişine üst arka servis kapağından ulaşılabildiği doğrulanmadı.
   K11 karar bekliyor.
4. **Denetim yine kalıp tabanlı:** köprüleme eş anlamlıları yalnız belirli nesnelerle aranıyor (ör. "iki ucu aynı klemense bağla" ya da nesne
   adı geçmeyen "uçlarını birleştir" yakalanmaz); bu, "GND uçlarını WAGO'da birleştir" gibi doğru cümlelerin yanlış alarm vermemesi için
   seçildi. Pencere virgülde ve "ve"de kesmiyor: "Ana anahtar açıkken yalnız gözle, aküyü ayır ve uçları sök" temiz (enerjiyi bitiren ifade),
   ama "ana anahtar açıkken X'i gözle, Y'yi sök" gibi sınırsız bir doğru cümle hâlâ bulgu verir (bugünkü veride 0).
5. **K1 kontrolündeki "artı ile eksi arasında kısa devre yok"** satırına kademe yazılmadı (brief D-8 mantar ve gerilim ölçümü diyor); bara
   kondansatörleri yüzünden süreklilik kademesinde kısa bip görülebilir, ileride "direnç kademesi" diye netleştirilebilir.
6. **PDF 54 sayfa:** F3'ün devam sayfasında yalnız "Erişim notu" var (taşma değil; kabul "her adım ≥ 1 sayfa"). README'deki sayfa sayısı F9d'nin
   alanında; F9d README'yi `kontrol.json`'dan okuyorsa bu turdan sonra 54 olmalı.

## Düzeltme turu 1 (F7d-kontrol KOŞULLU; 09.11 21:0x–21:2x)

Okunan: `planlama/d158/F7d-kontrol.md` (O-1, O-2, D-1 … D-7, KT-F7d-1); B'nin scratchpad `f7d_B/oneri_yama.py` ve `enjekte_b.py`
(yalnız okundu ve kopyada koşuldu). Koordinatör kuralı bu turda: FreeCAD yok, commit / push / silme yok, F9d alanına yazma yok.

### Kabul (tur 1)

| # | İstenen | Sonuç | Kanıt |
|---|---|---|---|
| 1 | O-1: pencere yalnız enerjiyi bitiren ifadede kesilir; B19, B20, B13 yakalanır; D-7 doğru cümleleri, N1–N10 temiz; gerçek veri 0 | **kapalı**. `_SINIR` = "ana anahtarı kapat / aküyü (XT60'tan) ayır / XT60'tan ayır / enerjiyi kes", ardından `(?!ma\|me)` (B'nin önerisi, A'nın denemesiyle doğrulandı). Sıra bağlacı kesmez | Y24 (B19), Y25 (B20), Y26 (B13) yakalandı; A'nın Y27–Y29'u ("sonra", "ana anahtarı kapatmadan", "ardından") yakalandı; N1–N10, N14, N15 ve B'nin NB1–NB3'ü, P5 temiz; gerçek veride yasak 0 |
| 2 | O-2: K1'de kolun XT60'ın hangi tarafından alındığı; F5 notunda gerilimli pim uyarısı; − ucu ve kutup | **kapalı (kaynakta olmayanlar "doğrulanmadı")**. K1: kol akü XT60'ının robot tarafından, ana hattan; kaynak yalnız "akü +, ana anahtar öncesi" diyor, taraf doğrulanmadı. − ucu ve kutup işareti doğrulanmadı (genel toprak `elektrik.md` blok şema). F5 notu: sigortadan sonra XT60E-M pimleri, akü XT60'tan ayrılmadıkça gerilimli; ana anahtar ve mantar kesmez; KT-F7d-1'e kadar geçerli. Konnektör seçimi değişmedi | `elektrik.md:341` (toprak), `:372` (şarj kolu); `maliyet.json` XT60E-M ve 16AWG yuva satırları; `ZORUNLU` K1 ×1, F5 ×1; Y33, Y34 |
| 3 | D-1: S3 için ayrı `ZORUNLU` | **kapalı**. F5 `Kollar aşağıda başlar` | Y30 (yalnız o cümle silindi) → yalnız "F5 kollar aşağıda başlar" eksik; B'nin S3'ü de yakalandı |
| 4 | D-2: "artık" / "eksik" yanlış alarm vermez | **kapalı**. `artı` / `eksi` yalnız ad çekim ekleriyle (sı, si, sını, sini, yı, yi, ya, ye, nın, nin, lar, ler, ları, leri) ve kelime sınırıyla | N11 (NB7), N12 (NB8), N13 temiz; Y35 "Akü artısını eksisiyle birleştir", Y36 "Eksi ucu artı uçla birbirine değdir" hâlâ yakalanıyor |
| 5 | D-4: F3'te ölçümden önce takı ve gerilimli fiş ucu | **kapalı**. "Ölçümden önce saat, yüzük, bileklik çıkar (`00-genel.md` kural 8)"; "fişin metal ucunu bantla yalıt, ekran kasasına ve metal parçalara değmesin (genel güvenlik, kaynakta yok)" | `00-genel.md:52`; `ZORUNLU` F3 ×2; Y31, Y32 |
| 6 | D-5: demo "kopya tutmadan" iddiası F9b'nin baktığıyla sınırlı | **kapalı**. "… göreli bağlantıyla (`<script src>`) yüklediği ve eski model kopyasının dosyasına bağlı olmadığı (sayfaya gömülü bir kopya ayrıca aranmaz)". Eski dosyanın adı yazılmadı: F9b [4] sayfada o adı görürse hata verir (`F9b-dogrula.py:522`). Rakam yok | `demo_fark.py`: 127 sayı anahtarının hiçbiri değişmedi |
| 7 | Yeniden üret ve doğrula | **0**: `rehber_uret.py --veri-yok` 50/50, konsol 0, 1192 ↔ 1192, 360 px 7 × 0, taşan 0, en küçük 8,1 pt, PDF **54** sayfa (değişmedi; README'nin "(54 sayfa)" ifadesiyle tutarlı, README'ye dokunulmadı); `demo_uret.py` 0; `F9b-dogrula.py` 0; `carpisma_kos.py kontrol` 0; `regresyon.py --yazma` 0; denetim 0 (zorunlu 0 / 40, yasak 0, istisna 5) | komutlar |

### Sapma: veri FreeCAD'siz güncellendi

`--veri-yok` adım metnini veriye almaz (bkz. yukarı): metin `rehber-veri.json`'a yalnız `rehber_veri.py` ile girer, o da FreeCAD ister. Bu
turda FreeCAD yasak olduğu için metin alanları scratchpad `f7d/veri_metin_yaz.py` ile yazıldı:
- kural `rehber_veri.py:533-586` ile aynı: adım "0" için `RM.HAZIRLIK`, öbürleri için `RM.ADIM`; `baslik`, `is_`, `baglanti_md`, `alet`,
  `erisim` = metin varsa metin, yoksa eski değer; `kontrol`, `kablo`, `not_` = metindeki liste;
- yazma biçimi `rehber_veri.py:625-627` ile aynı (json `indent=0`, `ensure_ascii=False`; js `window.REHBER_VERI=` + kompakt JSON + `;\n`;
  metin kipi).
- Sınama: değişiklik uygulanmadan yeniden yazılan dosyalar FreeCAD çıktısıyla **bayt bayt aynı** (json `da04cf4af2b0`, js `d93390ba5578`).
  Değişiklikle fark yalnız K1 `is_`, F3 `is_`, F5 `not_` (parça, GLB, şema, öbür adımlar aynı); `benzet.py` çıktısıyla veri eşit; js = json.
- İlk denemede adım "0" `RM.ADIM`'dan okunduğu için `kontrol` / `kablo` boşaldı; hemen yedekten geri yazıldı (sha1 baştakiyle aynı), betik
  düzeltildi, sonra yeniden uygulandı (yedek: scratchpad `f7d/d1/once_veri/`).
- `uretim` alanı **20:26'da kaldı** (FreeCAD koşusunun saati): rehber ve PDF alt bilgisi "üretim 2026-11-09 20:26" der, metin 21:0x'te
  güncellendi. Bir sonraki FreeCAD koşusu (`rehber_uret.py` ya da `--gorsel-yok`) aynı metni yazar ve saati düzeltir; içerik değişmez.

### Önce / sonra (tur 1)

- **K1 madde 1**, önce: "… Uç bantlı bırakılır, F1'de etekteki şarj girişine bağlanır; sigortası takılmaz (F1 aşama 1). Ana sigortadan önce
  mi sonra mı bağlanacağı ve kablo kesiti kaynakta yok, doğrulanmadı." Sonra: "… → XT60 şarj girişi ucu (`elektrik.md` sigorta listesi).
  Kolu akü XT60'ının robot tarafından, ana hattan al: akü XT60'tan ayrılınca kol da enerjisiz kalır (rehberdeki "akü ayrık = enerjisiz"
  düzeni buna dayanır). Kaynak yalnız "akü +, ana anahtar öncesi" diyor; XT60'ın hangi tarafı olduğu doğrulanmadı. Şarj girişinin − ucunun
  bağlanacağı nokta ve kutup işareti kaynakta yok, doğrulanmadı (genel toprak: akü − → WAGO yıldız noktası, `elektrik.md` blok şema). Uç
  bantlı bırakılır, … sigortası takılmaz (F1 aşama 1). Ana sigortadan önce mi sonra mı bağlanacağı kaynakta yok, doğrulanmadı. Kablo kesiti
  `elektrik.md`'de yok; sigorta yuvası 16AWG kuyruklu (`planlama/maliyet.json` hat sigortası yuvası), doğrulanmadı." (D-7'deki kesit
  düzeltmesi de burada.)
- **F3 madde 3**, "12 V fişini takmadan önce regülatör çıkışını yeniden ölç." ile "Akü ayrıkken multimetreyi …" arasına: "Ölçümden önce saat,
  yüzük, bileklik çıkar (`planlama/d158/testler/00-genel.md` kural 8). K2'den gelen 12 V kablosunun ekran ucundaki fiş ölçüm boyunca
  regülatör çıkışının 12 V'unu taşır: fişin metal ucunu bantla yalıt, ekran kasasına ve metal parçalara değmesin (genel güvenlik, kaynakta
  yok)."
- **F5 notu (şarj)**, "… bu sıra kaynakta yok, doğrulanmadı" sonrasına: "Uyarı: sigorta takıldıktan sonra etekteki şarj girişinin (XT60E-M
  panel erkek, `planlama/maliyet.json`) pimleri, akü XT60'tan ayrılmadıkça gerilimlidir: ana anahtar da mantar da bu kolu kesmez. Pimlere
  metal değdirme. Konnektörün cinsi ve kapağı karar taslağında (KT-F7d-1, `planlama/d158/F7d-kontrol.md`; kuyruğa girmedi); bu uyarı karar
  verilene kadar geçerli".
- **Demo** (`viewer-template.html:260`), önce: "sayfanın modeli kopya tutmadan, montaj rehberinin dosyalarından göreli bağlantıyla okuduğu ve
  bu dosyaların …"; sonra: "sayfanın modeli montaj rehberinin dosyalarından göreli bağlantıyla (`<script src>`) yüklediği ve eski model
  kopyasının dosyasına bağlı olmadığı (sayfaya gömülü bir kopya ayrıca aranmaz); bu dosyaların …".

### Denetim değişiklikleri (tur 1)

- `_SINIR`: çıplak sıra bağlacı ("sonra", "bitince", "ardından", "sonunda", "en son") çıktı; enerjiyi bitiren dört ifade `(?!ma|me)` ile.
- `_KOPRU_NESNE`: `artı\w*` / `eksi\w*` → `(?:artı|eksi)(?:sı|si|sını|sini|yı|yi|ya|ye|nın|nin|ları|leri|lar|ler)?` + kelime sınırı.
- `ZORUNLU` 35 → **40**: F5 `Kollar aşağıda başlar`; F5 şarj pimi uyarısı; F3 `Ölçümden önce saat, yüzük, bileklik çıkar`; F3
  `fişin metal ucunu bantla yalıt`; K1 `Kolu akü XT60'ının robot tarafından, ana hattan al`.
- `ASCII_TAMAM` + 13 doğru Türkçe kelime (hattan, rehberdeki, buna, hangi, kuyruklu, ucundaki, metal, pimleri, gerilimlidir, kesmez,
  pimlere, cinsi, verilene).
- Bağlamla affedilen 6 (önceki veriyle aynı 6 satır), yasak istisnası 5 (aynı).

### Enjeksiyon (tur 1)

A'nın `enjekte.py`'si (benzetilmiş veri ve gerçek veri): YENI **36 / 36** yakalandı (Y1–Y23 + Y24–Y36), OLUMSUZ **15 / 15** temiz
(N1–N10 + N11–N15), ESKI 14 / 14, ESKI_OLUMSUZ 8 / 8; çıkış 0.

| # | Deneme | Beklenen | Sonuç |
|---|---|---|---|
| Y24 | F5 "Ana anahtar açıkken birkaç saniye sonra F1 sigortasını tak" (B19) | yakala | yasak: enerji varken bağlantı |
| Y25 | F3 "Enerji varken ölçüm bitince göğüs 12 V fişini tak" (B20) | yakala | yasak |
| Y26 | F3 "Ana anahtar açıkken aküyü ayırmadan 12 V fişini tak." (B13) | yakala | yasak |
| Y27 | F1 "XT60 takılıyken ölçümden sonra mantar klemensini sık" | yakala | yasak |
| Y28 | F5 "Ana anahtar açıkken ana anahtarı kapatmadan hub kablosunu tak" | yakala | yasak |
| Y29 | F1 "Enerji varken ardından PC817 klemensini vidala" | yakala | yasak |
| Y30 | F5 "Kollar aşağıda başlar: … (E3 DTR / RTS notu)." tümden silindi (S3) | yakala | zorunlu: yalnız "F5 kollar aşağıda başlar" |
| Y31 | F3 "Ölçümden önce saat, yüzük, bileklik çıkar (…)" silindi | yakala | zorunlu |
| Y32 | F3 "fişin metal ucunu bantla yalıt, " silindi | yakala | zorunlu |
| Y33 | F5 notu "ana anahtar da mantar da bu kolu kesmez" → "ana anahtar bu kolu keser" | yakala | zorunlu |
| Y34 | K1 "Kolu akü XT60'ının robot tarafından, ana hattan al" → "Kolu akünün kendi tarafından al" | yakala | zorunlu |
| Y35 | K1 "Akü artısını eksisiyle birleştir" | yakala | yasak: köprüleme (birleştir) |
| Y36 | K1 "Eksi ucu artı uçla birbirine değdir" | yakala | yasak: köprüleme (birbirine bağla) |
| N11 | K2 "Artık S2 uzatmasının iki ucunu lehimle birleştir" (NB7) | temiz | temiz |
| N12 | K2 "Eksik kalan servo uzatmasını ek kabloyla birleştir" (NB8) | temiz | temiz |
| N13 | K2 "Eksikse ek kabloyu lehimle birleştir, artıkları kes" | temiz | temiz |
| N14 | F1 "Ana anahtar açıkken yalnız gerilimi oku, birkaç saniye sonra ana anahtarı kapat, aküyü XT60'tan ayır ve uçları sök" | temiz | temiz |
| N15 | F3 "XT60 takılıyken yalnız BMS ışığına bak, bitince enerjiyi kes ve 12 V fişini tak" | temiz | temiz |

B'nin `enjekte_b.py`'si (yeni denetim + yeni veri kopyasında): B 14 / 20 (B13, B19, B20 artık yakalanıyor; kaçan 6'sı D-3'ün bilinen
sınırları: B8, B14, B15, B16, B17, B18), NB **8 / 10** (NB7, NB8 temiz; NB9 "Sigorta kutusunun GND uçlarını … birleştir" ve NB10 "12 V çift
kablonun uzatmasını lehimle birleştir" hâlâ yanlış alarm, açık 5), J/K 31 / 31, S **3 / 3**, P 8 / 8.

### Komutlar (tur 1)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 21:0x | scratchpad `benzet.py` (yeni metin + yeni denetim, bellek içinde) | 1 → 0 | ASCII 13 → `ASCII_TAMAM` (bir kelime büyük harfle yazılmıştı, küçültüldü); sonra zorunlu 0 / 40, yasak 0, istisna 5 |
| 21:0x | `enjekte.py` / `enjekte_b.py` | 0 / 0 | yukarıda |
| 21:0x | scratchpad `veri_metin_yaz.py --sinama` | 0 | FreeCAD çıktısıyla bayt bayt aynı |
| 21:0x | `veri_metin_yaz.py` → `rehber/veri/rehber-veri.json` / `.js` | 0 | fark yalnız K1 `is_`, F3 `is_`, F5 `not_`; js = json |
| 21:0x | `rehber_denetim.py` | 0 | zorunlu 0 / 40, yasak 0 (istisna 5) |
| 21:0x–21:13 | `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` | **0** | 50 / 50, konsol 0, her parça tek adımda (1192 ↔ 1192), telefon 7 × 360 / 0, PDF **54** (devam 4: 31 → 32, 33; 32 → 34, 35; 35 → 38, 39; 49 → 53, 54), HTML 54, eşleme tutarlı, taşan yok, en küçük DOM 8,1 / PDF 8,1 pt, 3.932 kB |
| 21:1x | `pdf_olc.py` | 0 | 54 sayfa, en küçük 8,1 pt, 8 pt altı 0, eşleme = `kontrol.json` |
| 21:1x | `py -3 -B -X utf8 tasarim/cad/demo_uret.py` + `demo_fark.py` | 0 | 127 anahtar değişmedi; parmak izi `rehber-veri.json` `74137332d78e` → `38d5d32bc0b3`; blok dışında yalnız "Bu sayfa hakkında" satırı |
| 21:1x | `py -3 -B -X utf8 planlama/d158/F9b-dogrula.py` | **0** | GECER (hata 0); 1400 ve 360 px konsol 0, `data-hazir` = 1 |
| 21:1x | `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | **0** | izlenen 17 dosya aynı |
| 21:1x | `py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` | **0** | GEÇER |
| 21:1x | `rehber_denetim.py` (son) | 0 | aynı |

FreeCAD koşulmadı, kilit dosyasına yazılmadı ("boş"). Koşulardan sonra FreeCAD ve `lale-rehber` / `f9b-chrome` profilli Chrome süreci 0.

**Bakılan PDF sayfaları** (90 dpi, scratchpad `f7d/d1/sayfa/`): 18 (K1: madde 1'de kol tarafı, − ucu, kesit; tek sayfa), 38 (F3: madde
3'te takı ve fiş yalıtımı, ölçüm sırası tam), 39 (F3 devam), 53 (F5: aşama 2 tam; notta pim uyarısı ve KT-F7d-1), 54 (F5 devam). Kesik
satır yok, metin doğru adımda.

### Dosyalar ve sha1 (tur 1, ilk 12)

`rehber_metin.py` 64c5df86198c → 9026b9c27853; `rehber_denetim.py` 158d2c8f097a → 8eac1a079098; `viewer-template.html` a6427ed1a360 →
3bb82018db85; `rehber-veri.json` da04cf4af2b0 → 84d4b6744e81; `rehber-veri.js` d93390ba5578 → c0bd83d928fe; `kontrol.json` → a00f1ef8b58f;
PDF 65f35923dcb2 → 2d50a7393bfa; demo 53e6b4c89ff6 → e6537a6bce81; PNG adim-17 db70fdcb5603, adim-33 85734c0f8bfb, adim-35 9007fefc320a,
adim-49 70b10e53378c, telefon-360-adim-35 20cbd31c733e, telefon-360-adim-49 b0e049f19c52. Değişen dosya kümesi önceki turla aynı;
`planlama/d158/F7d-kontrol.md` (B'nin) commit listesine eklendi. `tasarim/cad/lale158-model.js` (izlenmiyor) bu paketin değil.

Yerel kullanıcı yolu ve takma ad taraması (bu paketin metin dosyaları, veri, `kontrol.json`, demo, PDF metni ve metası): 0.

### Günlükteki eski yanlışların düzeltmesi (F7d-kontrol D-7)

- Kabul satırı 4'teki "S1–S3 … için `ZORUNLU` satırları" S3 için doğru değildi (Y16 iki yeri birden siliyordu); S3 bu turda ayrı satırla
  korunuyor (Y30).
- Açık 1'deki "kablo kesiti kaynakta yok" yalnız `elektrik.md` için doğru; `maliyet.json` yuvası 16AWG kuyruklu. K1 metni buna göre
  düzeltildi.
- Kabul satırı 5 ve açık 4'teki "sıra bağlacında kesilir" bu turda geçersiz: pencere yalnız enerjiyi bitiren ifadede kesilir.

### Açıklar (tur 1 sonrası)

1. Şarj kolunun XT60'ın robot tarafından alınması rehberin önerisi, kaynakta yok; − ucu, kutup işareti, ana sigortaya göre yeri ve kesit
   doğrulanmadı. Konnektör cinsi / kapağı KT-F7d-1'de (Ahmet / tasarım; `karar-kuyrugu.md`'ye bu paket yazmadı, yazma alanı değil).
2. F3 fiş yalıtımı "genel güvenlik": kaynakta yok.
3. Veri FreeCAD'siz güncellendi; `uretim` alanı ve PDF alt bilgisi 20:26 der. Bir sonraki FreeCAD koşusu saati düzeltir.
4. D-3 sınırları sürüyor: B8 (F1'de "ana anahtar kapalıyken" sırası korunmuyor), B14 ("enerjiyi kesmeden … değiştir": tembel pencere ilk
   fiil olan olumsuz "kesmeden"de durur), B15 / B18 (şarj sigortası "takılmaz" → "tak" çelişkisi), B16 ("aynı klemense bağla"), B17
   (ad biçimi "birleştirme işini yap").
5. NB9 / NB10: "sigorta" ve "12 V" nesneleri kablo ekleme cümlesinde yanlış alarm verir (gerçek veride 0). Bu turun kapsamı yalnız "artık" /
   "eksik" idi; dokunulmadı.
6. Önceki açıklar 2, 3, 5 ve 6 geçerli (PDF yine 54 sayfa).
