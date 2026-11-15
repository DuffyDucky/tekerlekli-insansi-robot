# F10i günlüğü · P10.7b2a: K63 ve 74 kablonun bağlama talimatı

- **Paket:** P10.7b2a (A, uygulama; kaynak düzeyinde). Dal `lale-duzeltme`, başlangıç `1328b60` (P10.7b1). Commit / push yok:
  bağımsız kontrol ayrı.
- **Saat:** başlangıç orkestratörün kaydında 00:44 (bu ajan okumadı); günlük 2026-11-15 01:32–01:37 arasında yazıldı (saat 01:31:59, 01:35:06 ve
  01:36:39'da okundu).
- **Koşmayanlar (brief gereği):** FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları, başsız tarayıcı. Rehber çıktıları (`rehber/veri`,
  `rehber/goruntu`, `planlama/rehber`, PDF) elle düzenlenmedi: kaynak değişti, çıktılar üretime kadar kaynakla tutarsız (bilinen durum).
- **Dokunulmayanlar:** `kod/`, `main`, ekip panosu, paket dışı duran `tasarim/freecad/kabuk/gorsel/*.png` ve
  `tasarim/freecad/montaj/yerlesim-kontrol.json` (çalışma ağacında zaten değişikti, bu paket değiştirmedi). K52, K60, K61 açık kaldı.
  Devre değerleri (sigorta akımları, kesitler, direnç değerleri) değişmedi.

## 1. Özet

| Ölçüt | Önce (`1328b60`) | Sonra |
|---|---|---|
| Talimat maddesinde kimliği ve bağlama işaretiyle geçen kablo | 40 / 74 | **74 / 74** (muaf 0) |
| Tamlık sınamasının taradığı öğe | 65 (sigorta, köprü, saplama, GPIO, anahtar, acil stop) | 172 (+ kablo 74, cihaz korumaları, direnç, koruyucu yeri 7, kutuplu parça 4, kontak ucu 2, anahtarlı bara saplamaları) |
| `rehber_denetim.py --bozma-denemesi` | 76 / 76 | **104 / 104** |
| `kablolar_denetim.py --bozma-denemesi` | 145 | **156** (hepsi yakalandı) |
| `rehber_kablo.py --bozma-denemesi` | 27 / 27 | **32 / 32** |
| Onay kaydı (kablo / liste / metin) | 90 / 133 / 907 | 92 / 142 / 957; yenilemede **88 fark** (§ 8) |
| `kablolar.json` şeması | 3 | **4** (TVS, kontak uçları, koruyucu yeri, anahtarlı bara yerleşimi, kondansatör yönü) |

## 2. Kararlar (karar: orkestratör, 15.11)

1. **K2 / K1 kontak uçları.** K2: G10 → COM, NO → ön şarj direnci, NC boş. K1: 30 → 87. Kayıt: `anahtarlar.K1-kontak.uclar`,
   `anahtarlar.K2-kontak.uclar` (`giris`, `cikis`, `bos`, `teyit`, `kaynak`); `kararlar` P7b2a-1. Fiziksel pim yeri kablajda teyit.
2. **Hat sigortaları bara (kaynak) ucunda**, açık `yer` alanıyla: `koruyucular.hat-A / hat-B / hat-C / hat-G22 / hat-sarj /
   R-aku-olcum.yer` (P7b2a-2). `hat-cevre`'nin yeri P10.7b1'den beri yazılıydı.
3. **Anahtarlı bara yerleşimi:** seçenekler sayıldı (§ 4); hiçbiri öneriden iyi değil, öneri korundu (P7b2a-3).
4. **TVS ve kondansatör kutbu:** tek yönlü TVS'te katot (bantlı uç) artı hatta, anot GND'de; elektrolitikte eksi şeritli bacak GND'de
   (P7b2a-4). TVS kaynağı veri sayfası (§ 3); kondansatörün veri sayfası yok → kablajda teyit.
5. **G07 direnci pabuçta:** 100 kΩ'un öbür bacağı halka pabucun kovanına lehim; pabuç sayıma girdi (P7b2a-5). `planlama/maliyet.json`
   kayıttan üretilmiyor: dokunulmadı (sipariş farkı § 9).
6. **Dağıtım kartı C güç panelinde;** SV3 B5a'da tezgâhta, P03 K1'de (P7b2a-6).

## 3. Kayıt eklemeleri (`planlama/adim3/kablolar.json`, şema 3 → 4)

`kablolar_uret.py`, `kablolar_denetim.py` ve `kablolar.md` birlikte güncellendi; çıktı biçimi değişmedi (`indent=1`, UTF-8).

| Alan | Değer | Neden | Kaynak | Teyit |
|---|---|---|---|---|
| `tvs.P6KE18A` | kafa giriş kartında + / − arası; `yon` "katot (bantlı uç) +12 V ucuna, anot GND'ye"; sipariş kalemi 67 | kontrol-4 § 3.1-3: kutup yazılı değildi | Vishay P6KE6.8A–P6KE540A veri sayfası, belge 88369, rev. 27.09.2021: "for unidirectional types the color band denotes cathode end" (15.11 okundu) | satın alınan parçanın üreticisi bilinmiyor: bant teslimde okunur, yoksa takılmaz |
| `tvs.P6KE6V8A-pi`, `tvs.P6KE6V8A-ekran` | D24V50F5 VOUT / GND, SY8205 OUT+ / OUT−; `yon` "katot (bantlı uç) +5 V'a, anot GND'ye"; kalem 66 | rehberdeki "çizgili uç" ifadesi kayda bağlandı | aynı veri sayfası | aynı |
| `kondansatorler.yon / isaret / kaynak / teyit` | "− bacağı (gövdedeki eksi şeridinin olduğu yan) GND barasına, öbür bacak V+ barasına" | dağıtım kartı C talimatı (K63) | kalem 61'in satıcı sayfası üretici ve veri sayfası vermiyor (15.11 bakıldı): **doğrulanamadı** | şerit teslimde okunur; okunmazsa takılmaz (kablajda teyit edilecek) |
| `anahtarlar.K1-kontak.uclar` | giriş 30, çıkış 87 | karar 1 | `planlama/adim3/elektrik.md:441` | soket kuyruk numaraları teslimde |
| `anahtarlar.K2-kontak.uclar` | giriş COM, çıkış NO, boş NC | karar 1; enerjisizken ön şarj yolu açık | karar: orkestratör, 15.11 | JQC-3FF pim yeri elde parça olmadan doğrulanamaz: gövde şeması + süreklilik (bobin boşta COM–NC kısa, COM–NO açık) |
| `koruyucular.<hat>.yer` (6) | "anahtarlı bara ucunda (kaynak ucu): …" (A / B / C / G22), "ana anahtar girişindeki ucun dibinde (kaynak ucu): …" (şarj), "ana anahtar çıkış ucunda (kaynak ucu): …" (R-aku-olcum) | karar 2; kontrol-4 § 3.1-3 | kayıttaki `ara_uc` "a" (G14, G15, G16, G22, G06, G07) | — |
| `klemens_turleri.bara-pabuc.kopruler["Anahtarlı bara · +"]` | `besleme_saplamasi` 3, `yerlesim` 1: G12, G14, G15 / 2: G13, G16 / 3: G09, G11 / 4: G22, `gerekce` | karar 3; P10.7b1'de "yerleşim serbest" idi | § 4 sayımı | — |
| G07 damarı | `uc_turu.a` "pabuc", `uc_kuyrugu.a` {pabuc: kırmızı, ne: …}; `sonlandirma` ve `teyit` | karar 5 | karar: orkestratör, 15.11; değer `elektrik.md` (EL:234) | direnç bacağının kovanda tuttuğu ve çıkış saplamasının ölçüsü teslimde |
| G10 `sonlandirma` | "K2'nin COM kontak pimine doğrudan lehim (NO → ön şarj direnci, NC boş; pim yeri kablajda teyit)" | karar 1 | — | pim yeri |
| Kablo `rehber` alanları | G07 + F1 (K1 öneri → bugün), G22 + F5, B01 / B02 / N01 / N02 / U06 + K1, P03 K2 (öneri) → K1 | talimatın yeni yeri | rehber metni | — |
| `kararlar` P7b2a-1…6, `kaynak`, `alanlar` | şema 4 alan açıklamaları | — | — | — |

Denetim (`kablolar_denetim.py`): yeni sınama `yon_yer` (TVS alanları / düğümleri / kutup / kaynak URL'si / sipariş kalemi; kondansatör
"− … GND"; her `ara_koruyucu`'nun `yer`'i `ara_uc` parçasını anar; K1 / K2 uçları, K2 COM / NO / NC; bara saplama sırası kalın pabuç
altta); `kopru_akimlari` genelleşti (+ barada besleme b ucu düğüm olan damardan; iki yönde en küçük(besleme, yük)); pabuç sayımı
`uc_kuyrugu.pabuc`'u sayar; G07'nin pabuç kovanındaki 22 AWG ucu klemens alt sınırından muaf (`pabuc_kovan`). Yeni bozmalar 11
(`b_yon_yer` … `b_yon_yer_9`, `b_kesit_25`, `b_klemens_20`): 145 → 156, hepsi yakalandı.

## 4. Anahtarlı bara yerleşimi (karar 3)

Sayım (düzeltme turu 1'de depoya girdi: `planlama/d158/F10i-yerlesim-say.py`): 8 iletken (G09, G11, G12, G13, G14, G15, G16, G22),
4 saplama, saplama başına en çok 4 pabuç (köprü uçları dahil: uç saplamada 1, ortadakilerde 2), besleme saplaması serbest. **Geçerli
yerleşim 27.000** = iletken dağılışı × besleme hattını (G09, G11) taşıyan saplamanın besleme saplaması seçilişi; besleme saplaması
seçilmeden yalnız iletken dağılışı **14.840** (bağımsız kontrolün saydığı sayı, F10i-kontrol A10; iki sayı iki tanım). Köprü akımı modeli
`kablolar_denetim.kopru_akimlari` (bir köprünün iki yanındaki en küçük(besleme, yük); bütün + bara iletkenleri F1'den beslenir).

| | Köprü 1–2 | Köprü 2–3 | Köprü 3–4 | En kötü | 12 AWG etek sınırı | Pay |
|---|---|---|---|---|---|---|
| **Seçilen (öneri):** besleme 3; 1: G12, G14, G15 / 2: G13, G16 / 3: G09, G11 / 4: G22 | 20 A | 20 A | 2 A | **20 A** | 20,5 A | **0,5 A** |
| En iyi sıralı alternatif (40 yerleşim), ör. besleme 2; 1: G14, G16 / 2: G09, G11 / 3: G12, G13 / 4: G15, G22 | 12,5 A | 20 A | 9,5 A | 20 A | 20,5 A | 0,5 A |

27.000 yerleşimin **hepsinde** en kötü köprü akımı 20 A: F1'in (20 A) korumasıyla sınırlı, BTS7960B'nin biri hangi saplamada olursa
olsun bir köprü F1'in tamamını taşıyabilir. Karar ölçütü (en kötü köprü akımı) seçenekleri ayırmıyor; öneri korundu. Alternatif yalnız
ikinci ve üçüncü köprüyü rahatlatır, en kötüyü değil (bilgi; karar gerekmiyor). Pay 0,5 A dar: köprü kesiti ya da F1 değişirse yeniden
hesaplanır (`kablolar_denetim` her koşuda sınar).

## 5. Rehber metni: yeni talimatlar ve kaynakları (`tasarim/freecad/rehber/rehber_metin.py`)

Kaynak her kablo için `planlama/adim3/kablolar.json`'daki kaydı (uçlar, damarlar, sonlandırma); kritik değerler yer tutucudan
(`{awg.…}`, `{a.…}`, `{ohm.…}`, `{kontak.…}`, `{yer.…}`, `{yon.…}`, `{bsaplama.…}`; `rehber_deger.py`'ye 6 yeni tür).

- **K63 (1), G07** (`rehber_metin.py:302-307`, K1 madde 1): "Akü ölçüm teli (G07, {awg.G07}; akü ölçüm bölücüsünün {ohm.aku_olcum} üst
  direnci kaynak ucunda): arayüz kartı ucunu bölücünün orta noktası pedine lehimle, makaronla ört. Öbür uçta (G07'nin ana anahtar ucu)
  direnci telin ucuna lehimle, direncin öbür bacağını kırmızı M5 halka pabucun kovanına lehimle: direnç ile pabuç arasında tel kalmaz;
  direnci ve kovanı makaronla ört ({yer.R-aku-olcum}). Pabucu bantlı bırak: F1'de ana anahtarın çıkış saplamasına, G04'ün üstüne
  takılır. …" Kontroller: K1 `:394-396` (akü ayrık, direnç kademesi, pabuç ↔ bölücü orta noktası {ohm.aku_olcum}'a yakın), F1 aşama 1
  `:846-851` (DC V; değerler `elektrik.md` E2: 14,6 V'ta 2,23 V, 10,0 V'ta 1,53 V; 0 V ise pabuç / direnç / kart ucu kopmuş). F1
  madde 4 `:812-816`: giriş saplamasına G03 + G06, çıkışa G04 + G07, kalın pabuç altta; "G07 çıkışta olmalı: girişte olursa bölücü ana
  anahtar kapalıyken de akım çeker". K1 madde 1'de "dördü F1'de bağlanır" (G03, G04, G06, G07); F1 alt adım ve kablo listesi güncellendi.
- **K63 (2), SV3 + dağıtım kartı C** (`:227-231`, B5a): "Dağıtım kartı C, tezgâhta: kartın 2200 µF kondansatörünü V+ / GND barasına
  lehimle, yönü {yon.kondansator}. Gövdedeki eksi şeridi okunmuyorsa kondansatörü takma (kablajda teyit). Sonra SV3'ü ({awg.SV3})
  XL4016 C'nin OUT+ / OUT− klemensinden dağıtım kartı C'nin 2 pin 5,08 mm giriş klemensine bağla: OUT+ → V+, OUT− → GND. …" Kontrol
  `:233-235` (eksi şeritli bacak GND'de; SV3 kutbu; akü ayrıkken V+ ↔ GND kısa devre yok). K2 madde 2'de "hat C" tanımı (XL4016 C →
  SV3 → dağıtım kartı C, güç panelinde; B5a), S09 / S10 kartın pan / tilt çıkışına.
- **K1:** madde 1 G01 / G02 / G03 / G04 ayrı ayrı, `{yer.hat-sarj}`; madde 2 anahtarlı bara yerleşimi `{bsaplama.…}`; madde 3
  `{kontak.K1}`, G10 / G11 + `{kontak.K2}` (pim yeri kablajda teyit), hat sigortası yuvası `{yer.hat-A|hat-B|hat-C}` + kuyrukların
  yeri, `{yer.hat-G22}`; madde 5 A06'nın + ve − ucu; madde 5 son paragraf (kontrol-4 § 4 sözcük tuzağı) hedef listesi tam: G12, G13,
  G14, G15 + / −, G18, G19, SV1, SV2 (OUT+ → V+, OUT− → GND); madde 6 N01, N02, B01, B02, Q01–Q03, X01 kimlikle; madde 7 P03, G17, G20,
  U06. Kontrol: klemens tuzağı ("yalnız iki küçük kartta" → kafa giriş kartı, acil stop düğüm kartı ve arayüz kartının çevre 5 V
  düğümü); yeni maddeler G07, K2 kontağı, bara / hat sigortası yeri, A06 − ve sinyal uçları.
- **B3:** M01–M04 (motorların kendi kabloları, paralel çift), G12 / G13, G14 / G15 → SV1 / SV2, G18 / G19 (`{yer.hat-cevre}`).
- **B6a:** kondansatör A / B (`{yon.kondansator}`), X01, I01, I02 (OE → GND), P01, P02 (kanal numarası yazılmadı: pin haritasında).
- **E3a:** TVS'ler `{yon.P6KE6V8A-pi}`, `{yon.P6KE6V8A-ekran}`, `{yon.P6KE18A}` (`:548-552`); bant yoksa ya da çift yönlüyse takma
  (kablajda teyit); kontrol `:569-570` üç bandın yeri; not: veri sayfası ve üreticinin bilinmediği.
- **E4:** C01, H01, K04, U04 kimlikle (ana iş ve alt adım 9).
- **K2:** madde 1 S01–S08 tek tek; madde 2 hat C ve S09 / S10.
- **F1:** madde 3 A01 → NC giriş, A02 → NC çıkış (kontrol-4: "mantarın ikinci ucu" tekildi).

Rehber metnine yazılan ama yer tutucusu olmayan sayılar: F1 G07 kontrolündeki gerilimler (`elektrik.md` E2 tablosunun ölçü beklentisi;
çıplak sayı kuralı gerilimi kapsamıyor, P10.7b1'den beri açık iş "gerilimler yer tutucuda değil").

## 6. Denetim değişiklikleri

**`rehber_denetim.py`:**
- **Tamlık, talimat ölçütü** (`talimat_metinleri`, `talimat_kablolari`, `TALIMAT_FIIL`): talimat maddesi = adımın `is_` alanı ve alt
  adımların `is_` alanı (teslim notu, kontrol / kablo / not listesi, şema, KABLO_AD sayılmaz). Kablo kimliği açıkça (aralık "A01–A06"
  sayılmaz) ve aynı cümlede bağlama işaretiyle (→, bağla, tak, lehimle, vidala, geçir, uç, gider, gelir, iner, çıkar, pabuç). Sigorta
  `{a.<k>}`, direnç `{ohm.<TAMLIK_DIRENC>}`, cihaz koruması (BMS, çevirici, sürücü) koruduğu kabloların hepsi talimattaysa; köprü, saplama
  (yıldız `{saplama.<k>}`, anahtarlı bara `{bsaplama.<k>}`, besleme saplaması), TVS / kondansatör `{yon.…}`, kontak `{kontak.…}`,
  koruyucu yeri `{yer.…}` talimatta. Gerekçeli muaf `TAMLIK_MUAF` (tür "kablo" eklenebilir; bugün 0 kablo muaf). `TALIMAT_FIIL`,
  `TAMLIK_DIRENC`, `_KOD_DIZGE_ONU` onay kaydına girdi.
- **YASAK** (kontrol-4 § 3.5): yeni kural "köprüleme talimatı (nesneyle)": köprü sözcüğünün her biçimi aynı yan cümlede (virgül, iki
  nokta, ok, parantez keser) mantar / acil stop / NC / ana anahtar / sigorta / röle / kontak / artı / eksi ile geçerse bulgu; "köprü yoksa
  / yok / değil" ve olumsuz fiil affedilir. Nesnesiz çoğul ad ("Bu adımda takılan köprüler") sessiz.
- **ZORUNLU:** E3a "çizgili uç" → "bantlı uç" (yön kayıttan); yeni: P6KE18A kutbu, B5a kondansatör yönü, B5a SV3 kutbu, K1 G07 direnci
  pabuç kovanında, F1 G07 çıkış saplamasında.
- **ASCII kapsamı** (kontrol-5 § 6-2): `app.js` / `yazdir.html` görünen dizgeleri (JS belirteç ayırıcı: yorum ve düzenli ifade atlanır;
  HTML etiketi / özniteliği, dosya yolu, sınıf / seçici / olay adı alan çağrının dizgesi ayıklanır; görünen sayılan: Türkçe harfli ya da
  iki sözcüğünden biri sözlükte) ve kol şemalarının `lejant` alanı (`rehber_kol_kablo.py` LEJANT + `lejant=`, ast). 95 dizge girdi.
  Bilinen sınır: hiç Türkçe harfi ve bilinen sözcüğü olmayan dizge ("parca secili") görünmez sayılır.
- **ASCII izinli liste:** K63 metinlerinin 43 sözcüğü + app.js'in 10 sözcüğü (gözden geçirildi, doğru yazım); KISALTMA'ya SCL, COM, GLB.
  "kopuk" sözlükte "köpük"e çevriliyor: metinde "kopmuş" yazıldı.

**`rehber_kablo.py`:** seçim vurgusu (`app.js` `VURGU_TON`, tema başına "ana") karşıtlık (≥ 3,0) ve ΔE00 (≥ 15; her kablo tonu,
`EV_RENK`, `KONUM_RENK`) sınamasına girdi; yeni kural `SIYAH_L_FARK` 15 (açık temada siyah dışındaki ton siyahtan ≥ 15 L* açık); açık
HDMI #1d3854 → #193cff. `VURGU_TON` ve `SIYAH_L_FARK` onay kaydının kablo bölümünde.

### 6.1 Yeni sınamalar düzeltmeden önceki kaynakta (`1328b60`)

Eski `rehber_metin.py` ve eski `kablolar.json` geçici kopyada, yeni `tamlik_denetle` ile:
- eski metin + eski kayıt (şema 3): **46 eksik**: kablo 34 (G02, G07, M01–M04, SV1–SV3, A06, X01, B01, B02, N01, N02, I01, I02, P01–P03,
  Q02, S01–S09, K04, U04, H01, C01), koruyucu 11 (R-aku-olcum direnci; BTS7960 sol / sağ, D24V50F5, SY8205, XL4016 A / B / C / çevre,
  BMS: koruduğu kablolar talimatta değil), `{yer.hat-cevre}` 1, `{yon.kondansator}` 1. Eski ölçüt aynı kaynakta **0 eksik** buldu
  (68 / 74 kablo adıyla anılıyordu; I01, I02, P01, P02, P03, C01 anılmıyordu, yalnız bilgi). Düzeltme turu 1: ilk yazımdaki "2 eksik"
  yeniden üretilemedi (F10i-kontrol A15), 1328b60 kopyasında eski `rehber_denetim --kaynak` 0 verdi; doğrusu 0.
- eski metin + yeni kayıt (şema 4): **66 eksik** (+ TVS 3, kontak 2, koruyucu yeri 6, anahtarlı bara saplaması 9).
- YASAK: kontrol-4'ün üç cümlesi ve "mantarın iki ucu arasına bir köprü takılır" yeni kuralda 1'er bulgu; eski metinde yeni kural 0
  bulgu (7 istisna; yanlış alarm yok).

### 6.2 Bozma denemeleri

- `rehber_denetim.py --bozma-denemesi`: 104 / 104 (yeni 28): yasak 8 (5 yakalanmalı, 3 yakalanmamalı: "köprü yoksa röle çekmez",
  "köprülenmez", parantezli tel köprü → röle), talimat 10 (SV3 kimliği çıktı, G07 yalnız kontrolde, P03 bağlama işaretsiz,
  `{yon.P6KE18A}`, `{yon.kondansator}`, `{kontak.K2}`, `{yer.hat-A|hat-B|hat-C}`, `{bsaplama.G22}`, `{ohm.aku_olcum}`, `{a.hat-cevre}`
  çıktı), kayda öğe 5 (kablo, TVS, koruyucu yeri, kontak uçları, direnç), ASCII 5 (app.js dizge, şablon dizgesi, yazdir.html etiket dışı
  metin, kol lejantı; kod dizgesi yakalanmamalı). Bozmalar bellekte (dosya değişmez).
- `kablolar_denetim.py --bozma-denemesi`: 156, hepsi yakalandı.
- `rehber_kablo.py --bozma-denemesi`: 32 / 32 (yeni 5: eski açık yeşil vurgu karşıtlık 1,11; açık temada acil stop yeşiline yakın
  vurgu ΔE00 5,9; koyu temada servo sarısı vurgu 0,0; EV_RENK vurgu 0,0; eski açık HDMI L* farkı 9,5).

## 7. Küçük işler

- **Basılı lejant** (`rehber/yazdir.html`): "Karede:" satırı karedeki CAD kablo parçalarını da sayar (`parcalar[].renk`, devre sınıfı
  `kt` / `ks`; app.js lejantıyla aynı); alt adım kartında o alt adımın satırlarındaki CAD kablo parçaları. Bugünkü veriyle beklenen
  (üretimden önce taklit edildi, ölçülmedi): **K1** 0 → 5 satır (12 V doğrudan, toprak, anahtarlı bara / motor, acil stop, sinyal),
  **K2** 4 → 6 (+ servo gücü 6 V, sinyal); başka adımın lejantı değişmiyor.
- **E4 genel bakış lejantı:** değiştirilmedi. Neden: genel bakışta (alt adım yok) E4'ün beş şeması (U01, K05, H01, U04, K04) app.js'te
  "simdi" durumunda, çizilir ve sayılır; kafa kabukları onları örtebilir. Örtülme görünürlük ölçümü ister (başsız tarayıcı, bu pakette
  koşmaz). Açık iş: üretimde E4 karesine bakılır; örtülüyorsa lejant "çizilen ama örtülen" ayrımı yapmalı (kadraj / görünürlük ölçüsüyle).
- **Seçim vurgusu:** `app.js` `VURGU_TON` (açık: ana #a35ef2 menekşe, koyu: ana #00ffee camgöbeği; kopya ve ışıma tonları), tema
  değişince `sahneRengi()` malzemeleri günceller; `stil.css` `--vurgu` tema başına, işaret halkası `var(--vurgu)`. Ölçüm: açık vurgu
  zemine 3,21 / lejanta 3,86, en yakın ton mor ΔE00 17,9; koyu vurgu 13,41 / 12,55, en yakın beyaz 24,7. Kopya tonu (açık tint) eşik
  sınamasında değil (ana tonun açığı; açık temada zemine karşıtlığı düşük, eskisi gibi). `planlama/d158/F10a-dogrula.py` vurgu rengini
  malzeme renginden okuyordu: yeni tonlara uyarlandı (koşulmadı).
- **Açık HDMI:** #1d3854 → #193cff (L* 22,8 → ≈ 39; en yakın ton mor 17,8, mavi 18,2). Veri (`rt`) üretimde yenilenir.
- **`dongu-158.md` § 5:** P10.7b1 kapanış girdisinin saati için düzeltme girdisi (commit 15:50:47).
- Sözcük düzeltmesi `kablolar.json`: "G14'in" → "G14'ün", "G16'in" → "G16'nın" (hat sigortası yerleri).

## 8. Onay kaydı farkı (`rehber_denetim.py --kritik-onay-yenile`, 01:2x; tam liste)

1. **eklendi** · kablo · `ESIK`
   - eski: —
   - yeni: SIYAH_L_FARK 15.0
2. **değişti** · kablo · `TEMA_TON`
   - eski: hazir-hdmi = [('dark', '#5ba7b8'), ('light', '#1d3854')]
   - yeni: hazir-hdmi = [('dark', '#5ba7b8'), ('light', '#193cff')]
3. **eklendi** · kablo · `VURGU_TON`
   - eski: —
   - yeni: [('dark', '#00ffee'), ('light', '#a35ef2')] [('EV_RENK', '#ff3fa4'), ('KONUM_RENK', '#ffb000')]
4. **eklendi** · liste · `LISTE KOD_DIZGE_ONU`
   - eski: —
   - yeni: '(?:className\\s*\\+?=\|classList\\.\\w+\\(\|querySelector(?:All)?\\(\|getElementById\\(\|closest\\(\|matches\\(\|(?:set\|get\|has\|remove)Attribute\\(\|addEventListener\\(\|createElement\\(\|(?<![\\w.])(?:q\|qa\|\\$)\\()\\s*$'
5. **eklendi** · liste · `LISTE TALIMAT_FIIL`
   - eski: —
   - yeni: '→\|\\bbağla\\w*\|\\btak\\w*\|\\blehim\\w*\|\\bvidala\\w*\|\\bgeçir\\w*\|\\buc[uau]\\w*\|\\buç\\w*\|\\bgider\\b\|\\bgelir\\b\|\\biner\\b\|\\bçıkar\\b\|\\bpabuç\\w*'
6. **eklendi** · liste · `LISTE TAMLIK_DIRENC`
   - eski: —
   - yeni: [('R-aku-olcum', 'aku_olcum')]
7. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('köprüleme talimatı (nesneyle)', '\\b(?:mantar\\w*\|acil\\s+stop\\w*\|NC\|ana\\s+anahtar\\w*\|sigorta\\w*\|röle\\w*\|kontak\\w*\|(?:artı\|eksi)(?:sı\|si\|sını\|sini\|yı\|yi\|ya\|ye\|nın\|nin\|ları\|leri\|lar\|ler)?)(?![\\w])[^.;!?\\n,:→()]{0,60}?\\bköprü\\w*(?!\\w)(?!\\s+(?:yoksa\|yok\|değil)\\b)\|\\bköprü\\w*(?!\\w)(?!\\s+(?:yoksa\|yok\|değil)\\b)[^.;!?\\n,:→()]{0,60}?\\b(?:mantar\\w*\|acil\\s+stop\\w*\|NC\|ana\\s+anahtar\\w*\|sigorta\\w*\|röle\\w*\|kontak\\w*\|(?:artı\|eksi)(?:sı\|si\|sını\|sini\|yı\|yi\|ya\|ye\|nın\|nin\|ları\|leri\|lar\|ler)?)(?![\\w])', 'köprüle(?:n)?me(?:z\|di\|meli\|yin\|yiniz\|den)?\|köprülenemez')
8. **değişti** · liste · `LISTE ZORUNLU`
   - eski: ('E3a', 'katot \\(çizgili uç\\) \\+5 V', 'TVS kutbu')
   - yeni: ('E3a', 'katot \\(bantlı uç\\) \\+5 V', 'TVS kutbu')
9. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('E3a', "P6KE18A'yı kartın \\+ ve − uçları arasına lehimle, katot \\(bantlı uç\\) \\+12 V", 'P6KE18A kutbu (kafa giriş kartı)')
10. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('B5a', 'kondansatörünü V\\+ / GND barasına lehimle, yönü − bacağı', 'dağıtım kartı C kondansatör yönü')
11. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('B5a', "SV3'ü .{0,200}bağla: OUT\\+ → V\\+, OUT− → GND", 'SV3 kutbu (XL4016 C → dağıtım kartı C)')
12. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', 'direncin öbür bacağını kırmızı M5 halka pabucun kovanına lehimle', 'G07 direnci pabuç kovanında (K63)')
13. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('F1', "çıkış saplamasına G04'ü \\(sigorta kutusuna\\) ve akü ölçüm telinin pabucunu \\(G07", 'G07 ana anahtarın çıkışında (K63)')
14. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: Tezgâhta ayarlanan alt kat kartlarını (iki BTS7960B, XL4016 A / B / çevre) burçlara tak, klemenslerini kat gelmeden, üstü açıkken bağla; akü ayrık:
15. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: 1. Motor uçları (B2b'de plaka üstüne alındı): sol BTS7960B'nin M+ / M− klemensine ön sol motoru (M01) ve arka sol motoru (M02), sağ BTS7960B'ninkine ön sağ (M03) ve arka sağ motoru (M04) bağla.
16. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: Aynı yandaki iki motor aynı klemense paralel girer: iki motorun + ucu M+'ya, − ucu M−'ye.
17. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: 2. BTS7960B güç girişleri ({awg.G12\|G13}): sol kartın B+ / B− klemensine G12'yi, sağ kartınkine G13'ü bağla; + ve − karışmasın (kart üstü yazı).
18. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: 3. XL4016 A ve B: girişlerin IN+ / IN− klemensine G14 (A) ve G15'i (B), çıkışların OUT+ / OUT− klemensine SV1 (A) ve SV2'yi (B) bağla.
19. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: 4. XL4016 çevre: girişin IN+ / IN− klemensine G18'i, çıkışın OUT+ / OUT− klemensine G19'u bağla; G19'un hat sigortası yuvası {yer.hat-cevre}, sigortası takılmaz (F1 aşama 1'de takılır).
20. **eklendi** · metin · `kaynak B3 is_`
   - eski: —
   - yeni: Bu kabloların öbür uçları (bara, yıldız barası, sigorta kutusu, arayüz kartı, dağıtım kartları) K1'de bağlanır: aşağıdaki kablo notundaki gibi etiketle ve bantla.
21. **değişti** · metin · `kaynak B5a is_`
   - eski: XL4016 C ve ön şarj kartı da burada.
   - yeni: XL4016 C, ön şarj kartı ve dağıtım kartı C (kafa servolarının hattı C; XL4016 C'nin yanında) da burada.
22. **eklendi** · metin · `kaynak B5a is_`
   - eski: —
   - yeni: Dağıtım kartı C, tezgâhta: kartın 2200 µF kondansatörünü V+ / GND barasına lehimle, yönü {yon.kondansator}.
23. **eklendi** · metin · `kaynak B5a is_`
   - eski: —
   - yeni: Gövdedeki eksi şeridi okunmuyorsa kondansatörü takma (kablajda teyit).
24. **eklendi** · metin · `kaynak B5a is_`
   - eski: —
   - yeni: Sonra SV3'ü ({awg.SV3}) XL4016 C'nin OUT+ / OUT− klemensinden dağıtım kartı C'nin 2 pin 5,08 mm giriş klemensine bağla: OUT+ → V+, OUT− → GND.
25. **eklendi** · metin · `kaynak B5a is_`
   - eski: —
   - yeni: Bağlamadan önce telin iki ucunu etiketle, XL4016 C'nin ve kartın + / − yazısını karşılaştır: ters bağlanan kondansatör ısınır, kafa servoları zarar görür.
26. **eklendi** · metin · `kaynak B5a is_`
   - eski: —
   - yeni: Kafa servolarının sinyal köprüsü (P03) K1'de, uzatmaları (S09, S10) K2'de takılır.
27. **eklendi** · metin · `kaynak B5a kontrol`
   - eski: —
   - yeni: Dağıtım kartı C: kondansatörün eksi şeritli bacağı GND barasında; SV3 bağlandı (XL4016 C OUT+ → kartın V+, OUT− → GND).
28. **eklendi** · metin · `kaynak B5a kontrol`
   - eski: —
   - yeni: Akü ayrıkken multimetrenin direnç kademesinde kartın V+ ile GND arası sıfırda kalmıyor (kısa devre yok; kondansatör dolarken değer yükselir)
29. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: Tezgâhta, kat burçlara inmeden: kartları kata tak (arayüz kartı, dağıtım kartı A ve B, PCA9685, BNO055, ESP32 taşıyıcı), sonra kat üstündeki kartlar arası kabloları bağla.
30. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: Hepsi dişi uçlu sinyal teli (O-4 r); uçlar ve pinler `planlama/adim3/kablolar.md` tablolarında, kart üstü yazıya göre bağla:
31. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: 1. Dağıtım kartı A ve B: her kartın iki 2200 µF kondansatörünü V+ / GND barasına lehimle, yönü {yon.kondansator}; eksi şeridi okunmuyorsa takma (kablajda teyit).
32. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: 2. Arayüz kartı → ESP32 (X01): bölücü çıkışları, iki röle sürücüsünün taban girişi, PC817 çıkışları ve çıkış beslemesi, BTS EN düğümü, çevre 5 V → ESP32 VIN, GND → GND.
33. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: 3. I2C: ESP32 → PCA9685 giriş başlığı (I01: SDA, SCL, 3V3 → VCC, GND); PCA9685 çıkış başlığı → BNO055 (I02: SDA, SCL, VCC → VIN, GND).
34. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: PCA9685'in OE ucunu kart üstünde GND'ye bağla.
35. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: 4. Servo sinyalleri: PCA9685'in sağ kol kanalları → dağıtım kartı A'nın sinyal girişleri (P01), sol kol kanalları → dağıtım kartı B'ninkiler (P02); 3 pinli köprünün V+ ucu kartta bağlı değil, PCA9685'in V+ klemensi boş kalır.
36. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: Hangi kanalın hangi girişe gittiği kablolar.md'de (P01, P02).
37. **eklendi** · metin · `kaynak B6a kontrol`
   - eski: —
   - yeni: X01, I01, I02, P01 ve P02 bağlandı: her dişi uç kart üstü yazıyla kablolar.md'deki uca eşleşti; dağıtım kartı A ve B'de kondansatörlerin eksi şeritli bacağı GND barasında
38. **değişti** · metin · `kaynak E3a is_`
   - eski: TVS tek yönlü: katot (çizgili uç) +5 V'a, anot GND'ye.
   - yeni: TVS'ler tek yönlü; gövdedeki renkli bant katot ucudur (Vishay P6KE veri sayfası; `planlama/adim3/kablolar.json` tvs).
39. **değişti** · metin · `kaynak E3a is_`
   - eski: Kafa giriş kartı (P6KE18A üstünde küçük pertinaks parçası): üç adet 2 pin 5,08 mm vidalı klemens; + uçları ve − uçları kart üstünde {kopru.K01} tel köprüyle (K01 sonlandırması) lehimli (delikli plaket pedi F3 {a.F3} akım yolu değil).
   - yeni: Her P6KE6V8A'yı çeviricinin çıkış uçlarına lehimle: D24V50F5'te {yon.P6KE6V8A-pi}, SY8205'te {yon.P6KE6V8A-ekran}.
40. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: Bant yoksa ya da iki uçta da işaret varsa (çift yönlü) TVS'i takma (kablajda teyit).
41. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: Kafa giriş kartı (P6KE18A üstünde küçük pertinaks parçası): P6KE18A'yı kartın + ve − uçları arasına lehimle, {yon.P6KE18A}.
42. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: Üç adet 2 pin 5,08 mm vidalı klemens; + uçları ve − uçları kart üstünde {kopru.K01} tel köprüyle (K01 sonlandırması) lehimli (delikli plaket pedi F3 {a.F3} akım yolu değil).
43. **eklendi** · metin · `kaynak E3a kontrol`
   - eski: —
   - yeni: Üç TVS'in bantlı ucu (katot) artı hatta: P6KE18A kafa giriş kartının +12 V'unda, iki P6KE6V8A çeviricilerin +5 V çıkışında; anotlar GND'de
44. **değişti** · metin · `kaynak E3a not_`
   - eski: TVS kutup yönü (katot +5 V'a) tek yönlü TVS'in genel bağlanışı; depo kaynağında yazmıyor, veri sayfasıyla doğrulanmadı
   - yeni: TVS yönü kayıttan (`planlama/adim3/kablolar.json` tvs): Vishay P6KE serisi veri sayfası (belge 88369) tek yönlü tipte renkli bandın katot olduğunu yazıyor.
45. **eklendi** · metin · `kaynak E3a not_`
   - eski: —
   - yeni: Satın alınan parçaların üreticisi bilinmiyor: teslimde gövdedeki bant okunur (kablajda teyit)
46. **değişti** · metin · `kaynak E4 alt adım 9 is_`
   - eski: Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi → Pi; QLED HDMI (30 cm şerit, Pi micro HDMI 0), Power (SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (Pi USB 4).
   - yeni: Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi (C01) → Pi; QLED HDMI (H01; 30 cm şerit, Pi micro HDMI 0), Power (K04; SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (U04; Pi USB 4).
47. **değişti** · metin · `kaynak E4 is_`
   - eski: 4. Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi → Pi; QLED HDMI (30 cm şerit, Pi micro HDMI 0), Power (SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (Pi USB 4).
   - yeni: 4. Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi (C01) → Pi; QLED HDMI (H01; 30 cm şerit, Pi micro HDMI 0), Power (K04; SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (U04; Pi USB 4).
48. **değişti** · metin · `kaynak F1 alt adım 10 is_`
   - eski: z −88 sol bindirmesi 3 × M3×6, x −38 arka bindirmesi 3 × M3×6, z −105 braketine M3×14. K1'de bırakılan iki ana hat ucunu anahtara bağla.
   - yeni: z −88 sol bindirmesi 3 × M3×6, x −38 arka bindirmesi 3 × M3×6, z −105 braketine M3×14. K1'de bırakılan dört ucu anahtarın saplamalarına bağla: giriş saplamasına G03'ü ve şarj kolunun + pabucunu (G06), çıkış saplamasına G04'ü ve akü ölçüm telinin pabucunu (G07); kalın pabuç (G03, G04) altta.
49. **değişti** · metin · `kaynak F1 alt adım 7 is_`
   - eski: z −88 sağ bindirmesi 3 × M3×6, z −105 braketine M3×14. K1'de bırakılan acil stop ucunu kontağa bağla.
   - yeni: z −88 sağ bindirmesi 3 × M3×6, z −105 braketine M3×14. K1'de bırakılan iki acil stop ucunu mantarın NC kontağına bağla: A01'i NC girişine, A02'yi NC çıkışına.
50. **değişti** · metin · `kaynak F1 is_`
   - eski: Sonra K1'de bırakılan ucu bağla.
   - yeni: Sonra K1'de bırakılan iki ucu mantarın NC kontağına bağla: A01'i (F5 {a.F5} çıkışından gelen) NC girişine, A02'yi (acil stop düğümüne giden) NC çıkışına.
51. **silindi** · metin · `kaynak F1 is_`
   - eski: K1'de bırakılan iki ana hat ucunu bağla.
   - yeni: —
52. **eklendi** · metin · `kaynak F1 is_`
   - eski: —
   - yeni: K1'de bırakılan dört ucu anahtarın saplamalarına bağla: giriş saplamasına G03'ü (ana sigortadan) ve şarj kolunun + pabucunu (G06), çıkış saplamasına G04'ü (sigorta kutusuna) ve akü ölçüm telinin pabucunu (G07; {ohm.aku_olcum} akü ölçüm direnci pabucun kovanında).
53. **eklendi** · metin · `kaynak F1 is_`
   - eski: —
   - yeni: Kalın pabuç ({awg.G03\|G04}; G03, G04) altta, üstte düz pul + yaylı pul; giriş ile çıkışı anahtarın üstündeki işaretten oku (saplama ölçüsü teslimde).
54. **eklendi** · metin · `kaynak F1 is_`
   - eski: —
   - yeni: G07 çıkışta olmalı: girişte olursa bölücü ana anahtar kapalıyken de akım çeker.
55. **değişti** · metin · `kaynak F1 kablo`
   - eski: Burada bağlananlar: ana anahtar (G03, G04; {awg.G04}, halka pabuç), şarj girişi (G06, {awg.G06}), acil stop mantarı (A01 F5 {a.F5} girişi, A02 NC çıkışı; {awg.A02}).
   - yeni: Burada bağlananlar: ana anahtar (G03, G04; {awg.G04}, halka pabuç; G06'nın + pabucu girişte, G07'nin pabucu çıkışta), şarj girişi (G06, {awg.G06}), acil stop mantarı (A01 F5 {a.F5} girişi, A02 NC çıkışı; {awg.A02}).
56. **eklendi** · metin · `kaynak F1 kontrol`
   - eski: —
   - yeni: Akü ölçüm teli (G07), aşama 1'de mantar ölçümünden sonra: ana anahtar kapalı, akü XT60'tan ayrıkken multimetreyi DC V kademesinde bırak; kırmızı ucu arayüz kartındaki akü ölçüm bölücüsünün orta noktasına (G07'nin kart ucu), siyah ucu yıldız barasının akü dönüşü (G05) saplamasına bağla.
57. **eklendi** · metin · `kaynak F1 kontrol`
   - eski: —
   - yeni: Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin bölücü oranı kadar (`planlama/adim3/elektrik.md` E2: 14,6 V'ta 2,23 V, 10,0 V'ta 1,53 V); 0 V ise G07'nin pabucu, direnci ya da kart ucu kopmuş.
58. **eklendi** · metin · `kaynak F1 kontrol`
   - eski: —
   - yeni: Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök
59. **değişti** · metin · `kaynak K1 is_`
   - eski: 1. Ana hat ({awg.G01\|G02\|G03\|G04}; G01–G04): akü + → XT60 → ana sigorta {a.ana-sigorta} ({bicak.ana-sigorta} bıçak, kablolu yuva) → ana anahtar → sigorta kutusu.
   - yeni: 1. Ana hat ({awg.G01\|G02\|G03\|G04}): akü + → XT60 (G01, akü tarafı) → ana sigorta {a.ana-sigorta} ({bicak.ana-sigorta} bıçak, kablolu yuva; XT60'ın robot tarafından yuvanın girişine G02) → ana anahtar (yuvanın çıkışından G03) → sigorta kutusu (anahtarın çıkışından kutunun girişine G04).
60. **değişti** · metin · `kaynak K1 is_`
   - eski: Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır): ana anahtara gidecek iki uç bırakılır, F1'de bağlanır.
   - yeni: Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır): G03 ve G04'ün anahtar uçlarını halka pabuçlu ve bantlı bırak; şarj kolunun + ucu (G06) ve akü ölçüm teli (G07) de anahtara gider; dördü F1'de bağlanır.
61. **değişti** · metin · `kaynak K1 is_`
   - eski: Şarj kolu (G06, {awg.G06}): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına (G03 ile aynı saplama, mavi M5 halka pabuç); {a.hat-sarj} {bicak.hat-sarj} hat sigortasının kapaklı yuvası bu ucun dibinde, kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); − ucu yıldız barasına (mavi pabuç).
   - yeni: Şarj kolu (G06, {awg.G06}): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı saplama, mavi M5 halka pabuç; F1'de takılır); {a.hat-sarj} {bicak.hat-sarj} hat sigortasının kapaklı yuvası {yer.hat-sarj}, kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); − ucu yıldız barasına (mavi pabuç).
62. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Akü ölçüm teli (G07, {awg.G07}; akü ölçüm bölücüsünün {ohm.aku_olcum} üst direnci kaynak ucunda): arayüz kartı ucunu bölücünün orta noktası pedine lehimle, makaronla ört.
63. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Öbür uçta (G07'nin ana anahtar ucu) direnci telin ucuna lehimle, direncin öbür bacağını kırmızı M5 halka pabucun kovanına lehimle: direnç ile pabuç arasında tel kalmaz; direnci ve kovanı makaronla ört ({yer.R-aku-olcum}).
64. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Pabucu bantlı bırak: F1'de ana anahtarın çıkış saplamasına, G04'ün üstüne takılır.
65. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Pabuç saplamaya girmeden, akü ayrıkken multimetrenin direnç kademesiyle pabuç ile akü ölçüm bölücüsünün orta noktası arasını ölç: {ohm.aku_olcum}'a yakın okunur (kontrol).
66. **değişti** · metin · `kaynak K1 is_`
   - eski: Anahtarlı barada hangi ucun hangi saplamaya gideceği kayıtta yazılı değil: yerleşim serbest, yalnız saplama başına en çok {saplama.pabuc} pabuç (besleme saplaması yazılı olmadığından baranın köprüleri koruyucunun tam akımıyla sınanır: `planlama/adim3/kablolar.json`, saplama uç türünün köprü ilkesi).
   - yeni: Anahtarlı bara yerleşimi (kalın pabuç altta): saplama {bsaplama.G12\|G14\|G15} G12 / G14 / G15, {bsaplama.G13\|G16} G13 / G16, {bsaplama.G09\|G11} G09 / G11 (baraya gelen iki hat: röle K1 ve ön şarj kartı), {bsaplama.G22} G22; saplama başına en çok {saplama.pabuc} pabuç, köprü uçları dahil (`planlama/adim3/kablolar.json` yerleşim kaydı).
67. **değişti** · metin · `kaynak K1 is_`
   - eski: 3. F1 {a.F1} → röle K1 kontağı (30 → 87) → anahtarlı bara (G08, G09; {awg.G09}); F1 → ön şarj kartı (K2 kontağı + {ohm.onsarj}) → anahtarlı bara (G10, G11; {awg.G11}).
   - yeni: 3. F1 {a.F1} → röle K1 kontağı ({kontak.K1}: G08 sigorta kutusundan girişe, G09 çıkıştan anahtarlı baraya; {awg.G09}); F1 → ön şarj kartı → anahtarlı bara (G10, G11; {awg.G11}): G10'u K2 kontağının girişine lehimle, ön şarj direnci ({ohm.onsarj}) çıkış ucunda, G11 direncin öbür bacağından baraya; K2'nin uçları {kontak.K2} (röle pimlerinin yeri kablajda teyit: röle gövdesindeki şema).
68. **değişti** · metin · `kaynak K1 is_`
   - eski: Baradan: iki BTS7960B (G12, G13; {awg.G13}); mini hat sigortalarıyla XL4016 A ve B ({a.hat-A\|hat-B}; G14, G15), C ({a.hat-C}; G16), {awg.G14\|G15\|G16}; PC817 #2 algı teli (G22, {awg.G22}): bara ucunda {a.hat-G22} {bicak.hat-G22} hat sigortası, yıldız ucu 5 cm {ara.G22} siyah ara parçaya lehimli, ara parça kırmızı pabuçla.
   - yeni: Baradan: iki BTS7960B (G12, G13; {awg.G13}); mini hat sigortalarıyla XL4016 A ve B ({a.hat-A\|hat-B}; G14, G15), C ({a.hat-C}; G16, XL4016 C güç panelinde: IN+ / IN− klemensine), {awg.G14\|G15\|G16}; G14, G15 ve G16'nın hat sigortası yuvası {yer.hat-A\|hat-B\|hat-C}: yuvanın bir kuyruğu mavi M5 halka pabuçla bara saplamasına, öbür kuyruğu kablonun teline lehim + makaron; XL4016 ucunda sigorta yok.
69. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: PC817 #2 algı teli (G22, {awg.G22}): {yer.hat-G22} {a.hat-G22} {bicak.hat-G22} hat sigortası, yıldız ucu 5 cm {ara.G22} siyah ara parçaya lehimli, ara parça kırmızı pabuçla.
70. **değişti** · metin · `kaynak K1 is_`
   - eski: PC817 #1 girişi düğümden (A06, {awg.A06}; {gpio.ACIL_STOP_DURUM} okur).
   - yeni: PC817 #1 girişi düğümden (A06, {awg.A06}; {gpio.ACIL_STOP_DURUM} okur): A06'nın + ucunu acil stop düğüm kartında bir klemensin kuyruğuna (kart altı) lehimle, modülün IN1 + klemensine bağla; − ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle (makaron).
71. **değişti** · metin · `kaynak K1 is_`
   - eski: Alt kat kartlarının (iki BTS7960B, XL4016 A / B / çevre) klemens uçları B3'te, kat ve güç paneli gelmeden bağlandı: burada yalnız B3'te etiketli bırakılan öbür uçları bara, sigorta kutusu ve hat sigortalarına bağla.
   - yeni: Alt kat kartlarının (iki BTS7960B, XL4016 A / B / çevre) klemens uçları B3'te, kat ve güç paneli gelmeden bağlandı.
72. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Burada B3'te etiketli bırakılan öbür uçları yerlerine bağla: G12 ve G13'ün + uçlarını anahtarlı baraya, − uçlarını yıldız barasına; G14 ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baraya (madde 3), − uçlarını yıldız barasına; G18'in + ucunu sigorta kutusunun F4 çıkışına (madde 4), − ucunu yıldız barasına; G19'u arayüz kartının çevre 5 V / GND klemensine; SV1'i dağıtım kartı A'nın, SV2'yi dağıtım kartı B'nin V+ / GND giriş klemensine (OUT+ → V+, OUT− → GND).
73. **değişti** · metin · `kaynak K1 is_`
   - eski: 6. Enkoder ve sonarları bağla (motor uçları B3'te BTS7960B'ye bağlandı; sonarlar Q01–Q03).
   - yeni: 6. Enkoder, BTS sinyal ve sonar kabloları (dişi uçlu sinyal teli, O-4 r; pinler `planlama/adim3/kablolar.md`'de, kart üstü yazıya göre bağla): arka sol motorun enkoderi (N01) ve arka sağ motorun enkoderi (N02) → ESP32 taşıyıcı başlığı (VCC → 3V3, GND, A, B).
74. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Sol BTS7960B'nin sinyal başlığı (B01) ve sağınki (B02) → ESP32 (IN1, IN2) ve arayüz kartı (EN1 + EN2 → BTS EN düğümü, IS1 + IS2 → IS bölücüsü, VCC → çevre 5 V, GND).
75. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Sonarlar: sağ (Q01), orta (Q02) ve sol (Q03) sonarın VCC'sini arayüz kartının çevre 5 V'una, Trig'ini PCA9685'e, Echo'sunu arayüz kartındaki sonar bölücüsüne, GND'sini arayüz kartının GND'sine bağla.
76. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Motor uçları B3'te BTS7960B'ye bağlandı.
77. **değişti** · metin · `kaynak K1 is_`
   - eski: 7. Direğe çıkacak hatların taban kısmını da burada bağla (servo A / B / kafa, kafa 12 V, göğüs 12 V, ESP32 USB).
   - yeni: 7. Direğe çıkacak hatların taban kısmını da burada bağla: kafa servolarının sinyal köprüsü (P03): PCA9685'in kafa pan ve tilt kanallarından dağıtım kartı C'nin pan / tilt sinyal girişlerine 3 pinli köprü (köprünün V+ ucu kartta bağlı değil); kafa 12 V (G17), göğüs 12 V (G20) ve ESP32 USB'nin (U06) taban uçları.
78. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Servo uzatmaları (A / B / kafa) K2'de dağıtım kartlarının çıkışına takılır.
79. **değişti** · metin · `kaynak K1 kontrol`
   - eski: Ana hat ve toprak düğümleri (G01–G05, {awg.G01\|G02\|G03\|G04\|G05}) yalnız M5 saplama + halka pabuçta (saplama başına en çok {saplama.pabuc} pabuç); düğüm için vidalı klemens yalnız iki küçük kartta (kafa giriş kartı, acil stop düğüm kartı; 5,08 mm).
   - yeni: Ana hat ve toprak düğümleri (G01–G05, {awg.G01\|G02\|G03\|G04\|G05}) yalnız M5 saplama + halka pabuçta (saplama başına en çok {saplama.pabuc} pabuç).
80. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: Vidalı klemensli (5,08 mm) düğümler: kafa giriş kartı, acil stop düğüm kartı ve arayüz kartının çevre 5 V düğümü (`planlama/adim3/kablolar.json` klemens yerleri).
81. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: Akü ölçüm teli (G07): pabuç henüz saplamada değilken, akü ayrık, multimetrenin direnç kademesinde pabuç ile arayüz kartındaki akü ölçüm bölücüsünün orta noktası arası {ohm.aku_olcum}'a yakın; direnç ve pabuç kovanı makaronlu, pabuç bantlı (F1'de ana anahtarın çıkış saplamasına)
82. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: Ön şarj kartında K2'nin uçları {kontak.K2}: G10 girişte, ön şarj direnci çıkışta.
83. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: Pim yeri röle gövdesindeki şemayla ve akü ayrıkken multimetrenin süreklilik kademesiyle bakıldı (bobin boşta: G10'un pimi ile boş pim arası öter, G10'un pimi ile direncin pimi arası ötmez)
84. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: Anahtarlı bara: G14, G15, G16 ve G22'nin hat sigortası yuvaları bara ucunda, sigortaları takılı değil; saplamalardaki yerleşim madde 2'deki gibi (G09 ve G11 aynı saplamada), her saplamada en çok {saplama.pabuc} pabuç
85. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: A06'nın − ucu arayüz kartının GND pedinde; X01, B01, B02, N01, N02, Q01, Q02, Q03 ve P03'ün uçları kart üstü yazıyla kablolar.md'deki uca eşleşti
86. **değişti** · metin · `kaynak K2 is_`
   - eski: 1. Kol servo uzatmaları: dağıtım A / B → etek → direk arka yüzü (z −26) → travers altı (y ≈ 1215) arkası → omuz.
   - yeni: 1. Kol servo uzatmaları: kart ucunu dağıtım kartının 3 pinli çıkışına tak: sağ kol dağıtım kartı A'ya (S01 omuz öne-arka, S02 omuz yana, S03 dirsek, S04 bilek), sol kol dağıtım kartı B'ye (S05 omuz öne-arka, S06 omuz yana, S07 dirsek, S08 bilek); çıkış numaraları `planlama/adim3/kablolar.md`'de.
87. **değişti** · metin · `kaynak K2 is_`
   - eski: 2. Kafa servoları: hat C → direk üstü R62 halkası; tilt kablosu boyundan kafaya.
   - yeni: Yol: dağıtım A / B → etek → direk arka yüzü (z −26) → travers altı (y ≈ 1215) arkası → omuz.
88. **eklendi** · metin · `kaynak K2 is_`
   - eski: —
   - yeni: 2. Kafa servoları, hat C (XL4016 C → SV3 → dağıtım kartı C, güç panelinde; B5a): kafa pan uzatmasını (S09) dağıtım kartı C'nin pan çıkışına, kafa tilt uzatmasını (S10) tilt çıkışına tak → direk üstü R62 halkası; tilt kablosu boyundan kafaya.

Komutun özeti: `onay kaydı yenilendi: rehber_kritik_onay.json (kablo 92, liste 142, metin 957); 88 fark yazıldı`


## 9. Sipariş listesi farkı

**Yok.** G07'nin kırmızı M5 halka pabucu sayıma girdi (kırmızı pabuç 4 → 5; × 1,1 pay = 5,5 ≤ 10'lu paket): mevcut kalem 162'nin tek
paketi yetiyor. TVS (kalem 66, 67) ve kondansatör (kalem 61) adetleri değişmedi. `planlama/maliyet.json` kayıttan üretilmiyor:
dokunulmadı. Kontrol: `kablolar_denetim.py` `malzeme` sınaması GEÇER.

## 10. Üretimde beklenenler (üretim ayrı adım; bu pakette koşmadı)

- Parça 1192, şema 49, alt adım 71 değişmemeli (CAD ve şema geometrisi değişmedi). PDF sayfa sayısı metin uzadığı için artabilir
  (K1, B5a, B6a, E3a, F1 metni uzadı; 77'den fazla olabilir: ölçülmedi).
- K1 basılı sayfasında "Karede:" satırı (5 sınıf), K2'de 6 sınıf. Açık temada seçili parça fuşya (#e014ff; düzeltme turu 1'de
  menekşe #a35ef2'den değişti), koyu temada camgöbeği; HDMI şeması
  açık temada canlı mavi. `rehber_kablo.py --veri` yeni HDMI tonunu veride arar: veri yeniden üretilmeden "tema tonu" farkı verir.

## 11. Doğrulanamayanlar (kablajda teyit edilecek)

- TVS'lerin bandı (satın alınanın üreticisi bilinmiyor); kondansatörün eksi şeridi (veri sayfası yok).
- K2'nin (JQC-3FF) COM / NO / NC pim yeri; K1 soketinin 30 / 87 kuyruk numarası.
- G07: direnç bacağının pabuç kovanında lehimle tutması, çıkış saplamasının ölçüsü; G07 ölçümünde beklenen gerilimler `elektrik.md`
  E2'den, ölçülmedi.
- Anahtarlı bara: köprü payı 0,5 A (hesap, ölçüm değil).

## 12. Açık işler

- Yeni talimatların 3B şeması yok (G07, SV3, dağıtım kartı C, sinyal kabloları …): **şeması sonraki pakette** (çizilmeyen 23 kablo).
- E4 genel bakış lejantının örtülen şemaları (§ 7); vurgu kopya tonunun eşik dışı kalması.
- ASCII kapsamının bilinen sınırı (Türkçe harfsiz, sözlük dışı dizge); gerilimler yer tutucuda değil.
- Anahtarlı bara alternatifi (ikinci / üçüncü köprüyü rahatlatır): bilgi.
- Üretim + zincir: `rehber_uret.py`, F10* doğrulayıcıları, basılı sayfa ve vurgu renklerinin gözle bakışı.

## 13. Koşular (komut → çıkış kodu)

Hepsi `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`; son tur 01:2x.

| Komut | Çıkış | Not |
|---|---|---|
| `planlama/adim3/kablolar_uret.py` | 0 | `kablolar.md` 74 kablo (son koşu sözcük düzeltmesinden sonra) |
| `planlama/adim3/kablolar_uret.py --kontrol` | 0 | "kablolar.md ve elektrik.md bloğu güncel" |
| `planlama/adim3/kablolar_denetim.py` | 0 | 21 sınama GEÇER (yeni `yon_yer`) |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0 | 156 / 156 |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 1 → 0 | onay yenilemeden önce yalnız kritik fark; sonra 0 |
| `tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile` | 0 | 88 fark (§ 8) |
| `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0 | 104 / 104 |
| `tasarim/freecad/rehber/rehber_kablo.py` | 1 → 0 | yenilemeden önce yalnız onay kaydı (3 fark); sonra GEÇER |
| `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi` | 0 | 32 / 32 |
| `tasarim/freecad/rehber/rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GEÇTİ |
| `py_compile` (7 değişen .py; çıktı depo dışına) | 0 | |
| `node --check rehber/app.js`; `yazdir.html` betiği ayrı dosyada | 0; 0 | |
| geçici: yeni tamlık eski kaynakta (§ 6.1) | 0 | |
| Son tur, `kablolar.json` sözcük düzeltmesinden sonra (01:36:18'de bitti): `kablolar_uret.py --kontrol`, `kablolar_denetim.py`, `kablolar_denetim.py --bozma-denemesi`, `rehber_denetim.py --kaynak`, `rehber_kablo.py` | 0, 0, 0, 0, 0 | GEÇER; bozma 156; kritik fark 0; tamlık 172 / eksik 0; kablo talimat 74 / 74; onay tutuyor |

## Düzeltme turu 1 (15.11, 02:00–02:35; bağımsız kontrol `planlama/d158/F10i-kontrol.md` DÜZELTME GEREKLİ)

Kapsam: kontrolün yedi zorunlu bulgusu (Ü1–Ü7) ve küçük bulgulardan bu turda kapatılanlar (A1–A7, A9–A11, A13–A15). Devre değeri
(sigorta akımı, kesit, pin, direnç, süre) değişmedi; FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları ve başsız tarayıcı koşmadı; commit
yok. Her düzeltilen denetim için: kontrolün kaçan bozması yeniden üretildi (eski kodda kaçtı), şimdi yakalanıyor, kalıcı bozma
listesine girdi; bozulmamış kaynakta yanlış alarm 0.

### D1.1 Bulgu → yapılan → kanıt

| Bulgu | Yapılan | Kanıt (bozma, eski kodda → şimdi) |
|---|---|---|
| **Ü1** G22 kutbu | K1 madde 3: "G22'nin kutbu {kutup.G22}: + damarını … PC817 modülünün {uc.G22:+:b} klemensine, − damarını modülün {uc.G22:−:a} klemensinden yıldız barasına bağla"; ters bağlamanın sonucu ve "ters bağlıyken enerji verme"; K1 kontrolüne süreklilik maddesi. Uç ve kutup yer tutucudan (kayıt `G22` damarları). `kablolar.json` G22 teyit listesine kutup maddesi | ZORUNLU + ZORUNLU_ALAN + ZORUNLU_CUMLE; bozma "G22 uçları ters", "ters bağlama uyarısı silindi", "kutup kontrolü ters": kontrolde kaçtı → yakalandı (1'er) |
| **Ü2** X01 çıkış beslemesi | B6a madde 2: "PC817 modülünün çıkış besleme ucunu (çıkış VCC) ESP32'nin {uc.X01:PC817_çıkış_beslemesi:b} pinine bağla (X01): 5 V'a bağlama." + nedeni (pin haritası D3: girişler en çok 3,6 V); B6a kontrolüne süreklilik maddesi | ZORUNLU, ZORUNLU_ALAN, YASAK "PC817 çıkış beslemesi 5 V"; eski YASAK "PC817 … 5 V'a bağla" kaçtı → yakalandı; "5 V'a bağlama" yakalanmıyor (yanlış alarm 0) |
| **Ü3** P01–P03 V+ | B6a madde 4 ve K1 madde 7 emir kipinde: V+ teli takılmaz; 3 telli kabloda V+ damarı iki ucundan kesilip yalıtılır; neden (dönüştürücüler paralel); B6a ve K1 kontrolünde PCA9685 V+ ↔ dağıtım kartı V+ "ötmemeli". `kablolar.json` P01–P03 `not` | YASAK "PCA9685 V+ bağlama" (eski kodda kaçtı → yakalandı), ZORUNLU 4, ZORUNLU_ALAN 2; 5 zorunlu bozması yakalandı |
| **Ü4** tamlık ölçütü | `TALIMAT_FIIL` yalnız emir kipi; `TALIMAT_ERTELE` (bağlanır, takılır, takma, bağlanacak, gider …) yan cümlede talimatı düşürür; ok ("A → B") yalnız cümlede emir dışı fiil yokken talimat; kablo yalnız kaydının `rehber` alanında "bugün" yazan adımda aranır. Metin: G16, G21, K01, K02 emir kipine yazıldı | Bozma N01 / N02 "K2'de takılır", "bağlanacak", "takma", "bağlama", emri F5'te: eski kodda "K2'de takılır" ve "takma" **kaçtı** (0) → beşi de yakalandı (2'şer); emir kipinde bugünkü adımda 0 (yanlış alarm yok). Tamlık 74 / 74, eksik 0 |
| **Ü5** K1 87a / NC | `kablolar_denetim.py` `s_yon_yer`: K1 uçları 30 → 87, 87a boş değilse ya da G08 / G09 damarları uçlarla uyuşmazsa GÜVENLİK hatası; rehberde YASAK "K1 87a ucuna", "ana hat NC ucuna" | Ayna kopyada (düzeltme öncesi kayıt + denetim) K1 `cikis` 87a: `yon_yer` GEÇER, yalnız görünüm farkı (**kaçtı**) → şimdi `b_yon_yer_10`, `_11`, `_12` GÜVENLİK; YASAK bozması 4 + 2 yakalanmamalı |
| **Ü6** kutup ters | ZORUNLU desenleri yer tutucuyla: B5a ve B6a kondansatör `yönü {yon.kondansator}`, B5a `bağla: {kutup.SV3}`, K1 `({kutup.SV1|SV2})` | Eski kodda K1 SV1 / SV2 + / − yer değişimi kaçtı → "ters kutup", "kutbu silindi", B6a / B5a kondansatör ters, B5a SV3 ters: yakalandı |
| **Ü7** F10e vurgu | `F10e-dogrula.py` `appjs_vurgu_ton()`: `VURGU_TON`'u tema başına okur, yoksa hata verir; ton ölçüsü `secim_light`, `secim_dark` ve kopya tonları. Tarama: `F10a-dogrula.py` vurgu hex'lerini elle yazıyordu → `VURGU_TON`'dan; `F10d`, `F10f` vurgu okumuyor | Eski desen bugünkü app.js'te 0 eşleşme (None, sessiz düşüş); geçici test: `py_compile` 4 dosya, okuyucu iki temada doğru, üç bozuk app.js'te hata veriyor (doğrulayıcılar koşmadı) |
| **A1** G07 | Makaron lehimden önce, boyu direnç + iki bacak + kovan; açıkta bacak yok; gerginlik giderme (G04'e kablo bağı; bağın yeri kablajda teyit); F1 kontrolü bölücü oranı {oran.aku_olcum}, akü {v.aku_aralik} iken {v.aku_olcum} | ZORUNLU 3, ZORUNLU_ALAN 2; bozma "makaron lehimden sonra", "gerginlik silindi", "açıkta bacak kontrolü silindi", F1 aralığı elle, F1 koşulu değişti: yakalandı |
| **A2** K2 pim sırası | K1 madde 3: "Ön şarj kartında, lehimden önce K2'nin pimlerini bul …" G10 lehiminden önce; kontrol maddesi "G10 lehimlenmeden önce" | ZORUNLU; bozma "lehimden sonra": yakalandı. Satır gönderimi düzeltildi (aşağıda D1.2) |
| **A3** koruyucu yeri | Yerin başı (ilk ":" öncesi) kaynak ucundaki parçayı "… ucunda" diye anmalı, yük ucunun parçası başta geçmemeli | Kontrolün iki bozması: hat-B yük ucunda `b_yon_yer_13`, R-aku-olcum "arayüz kartında" `_14`: kaçtı → yakalandı |
| **A4** çıplak Ω / V | Direnç bağlamına "akü"; yeni kural "gerilim (akü ölçümü)" (akü ölçüm / bölücü oranı / orta noktası bağlamı); F1 değerleri yer tutucudan | Çıplak 100 kΩ, 4,23 V, F1 koşulu elle: eski kodda kaçtı → yakalandı; "PC817 3,3 V", ses bölücüsü 10 kΩ / 2,2 kΩ yakalanmıyor |
| **A5** aynı vida | YASAK "mantar / ana anahtar uçları aynı vidada" (çoğul uç: uçlar, iki uç, giriş ve çıkış) | "Mantarın NC uçlarını aynı vidaya bağla" eski kodda kaçtı → yakalandı; 3 yakalanmalı, "çıkış saplamasına G04 ve G07" yakalanmıyor |
| **A6** "(kablajda teyit)" | `teyit_denetle`: kaydı teyit işaretli yer tutucu (`yon`, `kontak`, `vida`) talimat satırında geçiyorsa aynı satırda "kablajda teyit" | E3a TVS, E3a P6KE18A, B5a ve B6a kondansatör ibaresi silindi: yakalandı (eskiden kaçıyordu) |
| **A7** A06 − ucu | ZORUNLU_CUMLE: A06'nın iki ucu aynı cümlede | "A06 − ucu silindi": yakalandı |
| **A9** vurgu ↔ sınıf | Açık ana #a35ef2 → **#e014ff** (fuşya), kopya #d9bffb → #f3b8ff, ışıma tonları; `stil.css --vurgu`, `SINIF.secili`; `rehber_kablo.py` kopya tonunu okur, ana ve kopya app.js `SINIF` renklerine (koyu temada önceki gri ayrı) karşı ΔE00 ≥ 15; SINIF onay kaydında | Yeni açık ana: zemine 3,06 / lejanta 3,68, en yakın lazer 16,6, EV_RENK 17,4; kopya en yakın ref 22,2. Bozma 4 (eski ton lazer 13,4, kopya lazer 4,3, profil koyu vurguya 5,5, koyu kopya önceki gri 0,0): yakalandı |
| **A10** 27.000 | `planlama/d158/F10i-yerlesim-say.py` depoda: dağılış 14.840, yerleşim (× besleme saplaması) 27.000, en kötü köprü 20 A hepsinde | İkisi de doğru, iki tanım (§ 4 düzeltildi) |
| **A11** kondansatör kaynağı | `kondansatorler.kaynak` = `planlama/adim3/elektrik.md:130`, kutup notu ayrı `kutup_kaynak`; denetim kaynak satırı ister | `b_yon_yer_15`: yakalandı |
| **A13** TVS çift yönlü | Kayıt ve rehber: gövde baskısı …A tek yönlü (bant katot), …CA çift yönlü (bant yok); CA baskılı ya da bantsız takılmaz | `b_yon_yer_16` (eski "iki uçta işaret" teyidi), ZORUNLU 2, bozma "CA cümlesi silindi", "eski ölçüt": yakalandı |
| **A14** saplama M5 | `anahtarlar.ana-anahtar.saplama` {M5, varsayım, kablajda teyit}; G03, G04, G06, G07 teyidine; rehberde `{vida.ana-anahtar}` + "kablajda teyit" (K1 madde 1, F1 madde 4) | `b_yon_yer_17`; `teyit_denetle` |
| **A15** "2 eksik" | 1328b60 kopyasında eski ölçüt 0 eksik (6 kablo yalnız bilgi) → § 6.1 düzeltildi | — |
| A8, A12, kondansatör yedeği | Açık iş: `karar-kuyrugu.md` "Karar değil, iş" | — |

### D1.2 Reddedilen ya da kısmen düzeltilen

- **Ü5 atfı:** kontrol "K1 uçlarını `elektrik.md:441` ile birebir karşılaştır" diyor; o satırda 30 / 87 numarası yok (kontağın işlevi var).
  Pin numaraları kaydın G08 (→ Röle K1 · 30) ve G09 (Röle K1 · 87 →) damarlarından; `K1-kontak.uclar.kaynak` bunu yazar, denetim uçları
  damarlarla karşılaştırır. Düzeltme yapıldı, atıf reddedildi.
- **A2 satırı:** gösterilen `rehber_metin.py:740-747` K2 adımının servo metni; 12 AWG lehiminden sonra pim bakışı K1 madde 3'teydi,
  düzeltme orada.
- **A10:** sayı yanlış değil (iki tanım); yalnız betik depoya alındı.
- **Tamlık ölçütündeki ok kuralı (bilinçli):** "Arayüz kartı → ESP32 (X01): …" gibi numaralı madde içindeki bağlama şemaları talimat
  sayılır; cümlede emir dışı bir fiil biçimi (takılır, gider, bağlanacak …) varsa sayılmaz. Bu yüzden 15 kablo yeniden yazılmadı; N01 /
  N02 bozmaları bu kuralla da yakalanıyor.

### D1.3 Kayda eklenenler (`planlama/adim3/kablolar.json`) ve dayanağı

- `kondansatorler.kaynak` `planlama/adim3/elektrik.md:130` (adet ve yer); `kutup_kaynak`: kalem 61'in satıcı sayfası üretici vermiyor.
- `tvs[*]`: `isaret` gövde baskısı …A / …CA; `teyit` "…CA soneki ya da bantsız parça takılmaz (kablajda teyit edilecek)"; kaynak Vishay
  P6KE veri sayfası (belge 88369, 27-Sep-2021): "for unidirectional types the color band denotes cathode end, no marking on
  bidirectional types", "For bidirectional types, use CA suffix" (15.11 yeniden okundu).
- `anahtarlar.ana-anahtar.saplama`: M5, varsayım; ölçü belgede yok (kablajda teyit); G03, G04, G06, G07 teyit listesinde.
- `anahtarlar.K1-kontak.uclar`: giriş 30, çıkış 87, boş 87a; kaynak G08 / G09 damarları + `elektrik.md:441` (işlev).
- G22 teyidi: modülün girişinde ters gerilim koruması belgede yok (kablajda teyit); ters bağlamada PC817 #2 LOW'a düşmez
  (`elektrik.md:258`).
- P01–P03 `not`: yalnız sinyal; kart girişindeki V+ bağlı değil (`elektrik.md:226`); 3 telli kabloda V+ kesilir; PCA9685'te kanal V+
  rayı ortak, V+ teli XL4016 A / B / C çıkışlarını paralel bağlar (kart içi ortak V+ kablajda teyit).
- `rehber` adım türü öneri → bugün: X01, I01, I02, P01, P02 (B6a), SV3 (B5a).
- Durum sayıları değişmedi: kesin 20, teyit 53, karara bağlı 1.

### D1.4 Kablajda teyit kalanlar

TVS gövde baskısı ve bandı; kondansatör eksi şeridi; K1 soketinin 30 / 87 kuyruk numarası; K2'nin COM / NO / NC pim yeri (lehimden
önce); PC817 modülünün IN2 girişinde ters gerilim koruması; PCA9685'te kanal V+ pinlerinin V+ klemensine ortaklığı; ana anahtarın
saplama ölçüsü (M5 varsayım); G07 gerginlik bağının yeri; F1'de G07 için beklenen 1,95–2,20 V (hesap, ölçülmedi).

### D1.5 Sipariş listesine etkisi

Adet değişmedi. Koşullu: ana anahtarın saplaması M5 çıkmazsa G03, G04, G06, G07'nin anahtar ucundaki halka pabuçlar o ölçüde alınır.
Kondansatörde yedek yok (5 / 5; açık iş, karar proje sahibinin).

### D1.6 Onay kaydı farkı (`rehber_denetim.py --kritik-onay-yenile`, 02:30:59; tam liste)

1. **eklendi** · kablo · `SINIF`
   - eski: —
   - yeni: light = [('baglanti', '#d4ac0d'), ('baski', '#f0932b'), ('cf', '#3d5a80'), ('imalat', '#d35400'), ('kablo', '#c0392b'), ('lazer', '#8e44ad'), ('onceki', '#b5b5b0'), ('profil', '#16a085'), ('ref', '#95a5a6'), ('satin', '#2f86d4')]
2. **eklendi** · kablo · `SINIF`
   - eski: —
   - yeni: dark = [('baglanti', '#d4ac0d'), ('baski', '#f0932b'), ('cf', '#3d5a80'), ('imalat', '#d35400'), ('kablo', '#c0392b'), ('lazer', '#8e44ad'), ('onceki', '#5d6168'), ('profil', '#16a085'), ('ref', '#95a5a6'), ('satin', '#2f86d4')]
3. **değişti** · kablo · `VURGU_TON`
   - eski: [('dark', '#00ffee'), ('light', '#a35ef2')] [('EV_RENK', '#ff3fa4'), ('KONUM_RENK', '#ffb000')]
   - yeni: [('dark', '#00ffee'), ('dark_kopya', '#9ffff6'), ('light', '#e014ff'), ('light_kopya', '#f3b8ff')] [('EV_RENK', '#ff3fa4'), ('KONUM_RENK', '#ffb000')]
4. **değişti** · liste · `LISTE CIPLAK_KURAL`
   - eski: ('direnç', '(?<![\\w{.,])\\d+(?:[.,]\\d+)? ?[mk]?(?:ω|ohm\\b)', 'bc337|sürücü|taban|\\bseri\\b|ön şarj')
   - yeni: ('direnç', '(?<![\\w{.,])\\d+(?:[.,]\\d+)? ?[mk]?(?:ω|ohm\\b)', 'bc337|sürücü|taban|\\bseri\\b|ön şarj|akü')
5. **değişti** · liste · `LISTE CIPLAK_KURAL`
   - eski: ('direnç (sözle)', '\\b(?:sıfır|bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan|yüz|bin|buçuk|yarım)(?: (?:sıfır|bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan|yüz|bin|buçuk|yarım))* (?:kilo|mili|mega)?(?:ohm\\w*|ω)', 'bc337|sürücü|taban|\\bseri\\b|ön şarj')
   - yeni: ('direnç (sözle)', '\\b(?:sıfır|bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan|yüz|bin|buçuk|yarım)(?: (?:sıfır|bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan|yüz|bin|buçuk|yarım))* (?:kilo|mili|mega)?(?:ohm\\w*|ω)', 'bc337|sürücü|taban|\\bseri\\b|ön şarj|akü')
6. **eklendi** · liste · `LISTE CIPLAK_KURAL`
   - eski: —
   - yeni: ('gerilim (akü ölçümü)', '(?<![\\w{.,])\\d+(?:[.,]\\d+)?(?: ?[–-] ?\\d+(?:[.,]\\d+)?)? ?m?v\\b', 'akü ölçüm|bölücü oran|bölücünün orta|bölücüsünün orta')
7. **eklendi** · liste · `LISTE TALIMAT_ERTELE`
   - eski: —
   - yeni: '(?<!\\w)(?!(?:bağla|tak|lehimle|vidala|geçir|sık|bağlayın|takın|lehimleyin|vidalayın|geçirin|sıkın)(?!\\w))(?!bağlantı)(?:bağla|tak|lehimle|vidala|geçir)\\w+|(?<!\\w)(?:gider|gelir|iner|girer|çıkar|gidecek|gelecek)(?!\\w)'
8. **değişti** · liste · `LISTE TALIMAT_FIIL`
   - eski: '→|\\bbağla\\w*|\\btak\\w*|\\blehim\\w*|\\bvidala\\w*|\\bgeçir\\w*|\\buc[uau]\\w*|\\buç\\w*|\\bgider\\b|\\bgelir\\b|\\biner\\b|\\bçıkar\\b|\\bpabuç\\w*'
   - yeni: '(?<!\\w)(?:bağla|tak|lehimle|vidala|geçir|sık|bağlayın|takın|lehimleyin|vidalayın|geçirin|sıkın)(?!\\w)'
9. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('PCA9685 V+ bağlama', '\\bPCA9685\\S*\\s+V\\+\\s*(?:klemens|pin|uc|ray)\\w*[^.;!?\\n]{0,60}?\\b(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\\s+yap)\\w*', '(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|yap)(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?|(?:bağla|tak|sök|çıkar|kes|değiştir|yap)(?:ıl|il|ul|ül)?(?:maz|mez)')
10. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('PC817 çıkış beslemesi 5 V', "\\b(?:PC817|çıkış\\s+(?:VCC|besleme))\\S*[^.;!?\\n]{0,120}?\\b5\\s*V['’](?:a|ya|e|ye)\\s+(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\\s+yap)\\w*", '(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|yap)(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?|(?:bağla|tak|sök|çıkar|kes|değiştir|yap)(?:ıl|il|ul|ül)?(?:maz|mez)')
11. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('K1 87a ucuna bağlama', "\\b87a(?:['’]\\w+)?\\b(?!\\s*\\)?\\s*boş)[^.;!?\\n]{0,60}?\\b(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\\s+yap)\\w*", '(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|yap)(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?|(?:bağla|tak|sök|çıkar|kes|değiştir|yap)(?:ıl|il|ul|ül)?(?:maz|mez)')
12. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('ana hat NC ucuna', "\\bG(?:08|09|10|11)\\b(?:['’]\\w+)?[^.;!?\\n]{0,80}?\\bNC\\b(?:['’]\\w+)?(?!\\s*\\)?\\s*boş)[^.;!?\\n]{0,30}?\\b(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\\s+yap)\\w*", '(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|yap)(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?|(?:bağla|tak|sök|çıkar|kes|değiştir|yap)(?:ıl|il|ul|ül)?(?:maz|mez)')
13. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('mantar / ana anahtar uçları aynı vidada', '\\b(?:mantar\\w*|ana\\s+anahtar\\w*)(?:\\s+\\w+){0,3}?\\s+(?:uç(?:lar|ları)\\w*|iki\\s+uc\\w*|giriş\\w*\\s+ve\\s+çıkış\\w*)[^.;!?\\n]{0,40}?\\baynı\\s+(?:vida|klemens|saplama|pabuç)\\w*[^.;!?\\n]{0,30}?\\b(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\\s+yap)\\w*|\\baynı\\s+(?:vida|klemens|saplama|pabuç)\\w*[^.;!?\\n]{0,30}?\\b(?:mantar\\w*|ana\\s+anahtar\\w*)(?:\\s+\\w+){0,3}?\\s+(?:uç(?:lar|ları)\\w*|iki\\s+uc\\w*|giriş\\w*\\s+ve\\s+çıkış\\w*)[^.;!?\\n]{0,30}?\\b(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\\s+yap)\\w*', '(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|yap)(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?|(?:bağla|tak|sök|çıkar|kes|değiştir|yap)(?:ıl|il|ul|ül)?(?:maz|mez)')
14. **değişti** · liste · `LISTE ZORUNLU`
   - eski: ('B5a', 'kondansatörünü V\\+ / GND barasına lehimle, yönü − bacağı', 'dağıtım kartı C kondansatör yönü')
   - yeni: ('B5a', 'kondansatörünü V\\+ / GND barasına lehimle, yönü {yon.kondansator}', 'dağıtım kartı C kondansatör yönü')
15. **değişti** · liste · `LISTE ZORUNLU`
   - eski: ('B5a', "SV3'ü .{0,200}bağla: OUT\\+ → V\\+, OUT− → GND", 'SV3 kutbu (XL4016 C → dağıtım kartı C)')
   - yeni: ('B5a', "SV3'ü .{0,200}bağla: {kutup.SV3}", 'SV3 kutbu (XL4016 C → dağıtım kartı C)')
16. **değişti** · liste · `LISTE ZORUNLU`
   - eski: ('K1', 'direncin öbür bacağını kırmızı M5 halka pabucun kovanına lehimle', 'G07 direnci pabuç kovanında (K63)')
   - yeni: ('B6a', 'her kartın iki 2200 .F kondansatörünü V\\+ / GND barasına lehimle, yönü {yon.kondansator}', 'dağıtım kartı A / B kondansatör yönü')
17. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', "SV2'yi dağıtım kartı B'nin V\\+ / GND giriş klemensine \\({kutup.SV1|SV2}\\)", 'SV1 / SV2 kutbu (XL4016 A / B → dağıtım kartı)')
18. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', 'direncin öbür bacağını kırmızı {vida.ana-anahtar} halka pabucun kovanına lehimle', 'G07 direnci pabuç kovanında (K63)')
19. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('B6a', "PC817 modülünün çıkış besleme ucunu \\(çıkış VCC\\) ESP32'nin {uc.X01:PC817_çıkış_beslemesi:b} pinine bağla \\(X01\\): 5 V'a bağlama", "X01: PC817 çıkış beslemesi ESP32 3V3'te, 5 V'a bağlanmaz")
20. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('B6a', "PCA9685'in V\\+ klemensine ve kanal başlıklarının V\\+ pinine tel takma", 'P01 / P02: PCA9685 V+ teli takılmaz')
21. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('B6a', '3 telli hazır servo kablosu kullanırsan V\\+ damarını iki ucundan kes, makaronla yalıt', 'P01 / P02: 3 telli kabloda V+ kesilir')
22. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('B6a', "V\\+ teli takılırsa üç dağıtım kartının V\\+'ı, yani XL4016 A, B ve C'nin çıkışları birbirine paralel girer", 'P01 / P02: V+ telinin nedeni (dönüştürücüler paralel)')
23. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', "PCA9685'in V\\+ pinine tel takma; 3 telli hazır kablo kullanırsan V\\+ damarını iki ucundan kes, makaronla yalıt", 'P03: PCA9685 V+ teli takılmaz, 3 telli kabloda V+ kesilir')
24. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', "Bağlamadan önce modülün üstündeki IN2 \\+ / IN2 − yazısını oku: ters bağlanan G22'de .{0,260}ters bağlıyken enerji verme", 'G22: kutup yazısı okunur, ters bağlıyken enerji verilmez')
25. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', "lehimden önce makaronu G07'nin teline geçir", 'G07: makaron lehimden önce geçirilir')
26. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', "Gerginlik giderme: G07'yi direncin tel tarafında, ana anahtara giden G04'e kablo bağıyla tuttur", 'G07: gerginlik giderme')
27. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('K1', "lehimden önce K2'nin pimlerini bul", 'K2 pim yeri 12 AWG lehiminden önce bulunur')
28. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('E3a', 'P6KE…A \\(sonu A\\) tek yönlüdür, renkli bandı katottur; P6KE…CA \\(sonu CA\\) çift yönlüdür, bandı yoktur', 'TVS: gövde baskısı (…A tek yönlü, …CA çift yönlü)')
29. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('E3a', "CA baskılı ya da bantsız TVS'i takma \\(kablajda teyit\\)", 'TVS: CA baskılı ya da bantsız takılmaz')
30. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('B6a', 'kontrol', 'çıkış VCC ile ESP32 {uc.X01:PC817_çıkış_beslemesi:b} pini arası öter, çıkış VCC ile çevre 5 V arası ötmez', "B6a kontrol: X01 çıkış VCC 3V3'te, 5 V'ta değil")
31. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('B6a', 'kontrol', "PCA9685'in V\\+ klemensi ile dağıtım kartı A'nın ve B'nin V\\+ barası arasında süreklilik yok", 'B6a kontrol: PCA9685 V+ ile dağıtım kartı A / B V+ arası ötmez')
32. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('K1', 'kontrol', '{uc.G22:−:a} ile yıldız barası arası öter, {uc.G22:+:b} ile yıldız barası arası ötmez', 'K1 kontrol: G22 kutbu')
33. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('K1', 'kontrol', "PCA9685'in V\\+ klemensi ile dağıtım kartı C'nin V\\+ barası arasında süreklilik yok", 'K1 kontrol: PCA9685 V+ ile dağıtım kartı C V+ arası ötmez (P03)')
34. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('K1', 'kontrol', 'direnç, iki bacağı ve pabuç kovanı makaronla tümüyle örtülü \\(açıkta bacak yok\\)', 'K1 kontrol: G07 direnci örtülü')
35. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('F1', 'kontrol', 'bölücü oranı \\({oran.aku_olcum}\\) katıdır: akü {v.aku_aralik} iken bölücünün orta noktasında {v.aku_olcum} okunur', 'F1 kontrol: G07 ölçüm aralığı (bölücü oranı, kayıttan)')
36. **eklendi** · liste · `LISTE ZORUNLU_CUMLE`
   - eski: —
   - yeni: ('K1', "A06'nın \\+ ucunu", 'IN1 \\+ klemensine bağla; − ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle', "K1 is_: A06'nın iki ucu (+ IN1 +, − IN1 − → GND)")
37. **eklendi** · liste · `LISTE ZORUNLU_CUMLE`
   - eski: —
   - yeni: ('K1', "G22'nin kutbu", '\\+ damarını \\(hat sigortasından gelen\\) arayüz kartındaki PC817 modülünün {uc.G22:+:b} klemensine, − damarını modülün {uc.G22:−:a} klemensinden yıldız barasına bağla', "K1 is_: G22'nin iki ucu ve kutbu")
38. **değişti** · metin · `kaynak B5a is_`
   - eski: Sonra SV3'ü ({awg.SV3}) XL4016 C'nin OUT+ / OUT− klemensinden dağıtım kartı C'nin 2 pin 5,08 mm giriş klemensine bağla: OUT+ → V+, OUT− → GND.
   - yeni: Sonra SV3'ü ({awg.SV3}) XL4016 C'nin OUT+ / OUT− klemensinden dağıtım kartı C'nin 2 pin 5,08 mm giriş klemensine bağla: {kutup.SV3}.
39. **değişti** · metin · `kaynak B6a is_`
   - eski: 2. Arayüz kartı → ESP32 (X01): bölücü çıkışları, iki röle sürücüsünün taban girişi, PC817 çıkışları ve çıkış beslemesi, BTS EN düğümü, çevre 5 V → ESP32 VIN, GND → GND.
   - yeni: 2. Arayüz kartı → ESP32 (X01): bölücü çıkışları, iki röle sürücüsünün taban girişi, PC817 çıkışları, BTS EN düğümü, çevre 5 V → ESP32 VIN, GND → GND.
40. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: PC817 modülünün çıkış besleme ucunu (çıkış VCC) ESP32'nin {uc.X01:PC817_çıkış_beslemesi:b} pinine bağla (X01): 5 V'a bağlama.
41. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: Modülün çıkışları PC817 #1 (acil stop, {gpio.ACIL_STOP_DURUM}) ve PC817 #2 (bara, {gpio.BARA_DURUM}) pinlerine gider; besleme 5 V olursa bu pinler 5 V görür, ESP32 girişleri en çok 3,6 V'a dayanır (pin haritası D3).
42. **değişti** · metin · `kaynak B6a is_`
   - eski: 4. Servo sinyalleri: PCA9685'in sağ kol kanalları → dağıtım kartı A'nın sinyal girişleri (P01), sol kol kanalları → dağıtım kartı B'ninkiler (P02); 3 pinli köprünün V+ ucu kartta bağlı değil, PCA9685'in V+ klemensi boş kalır.
   - yeni: 4. Servo sinyalleri, yalnız sinyal teli: PCA9685'in sağ kol kanallarının sinyal pinlerini dağıtım kartı A'nın sinyal girişlerine (P01), sol kol kanallarınınkini dağıtım kartı B'ninkilere (P02) tek telli dişi uçlarla bağla.
43. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: PCA9685'in V+ klemensine ve kanal başlıklarının V+ pinine tel takma; dağıtım kartının sinyal girişindeki V+ pini kartta bağlı değildir.
44. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: 3 telli hazır servo kablosu kullanırsan V+ damarını iki ucundan kes, makaronla yalıt.
45. **eklendi** · metin · `kaynak B6a is_`
   - eski: —
   - yeni: Neden: PCA9685'te kanal başlıklarının V+ pinleri V+ klemensine ortaktır; V+ teli takılırsa üç dağıtım kartının V+'ı, yani XL4016 A, B ve C'nin çıkışları birbirine paralel girer, dönüştürücüler zarar görebilir (kart içi ortak V+ sırası kablajda teyit).
46. **eklendi** · metin · `kaynak B6a kontrol`
   - eski: —
   - yeni: PC817 modülünün çıkış VCC ucu ESP32'nin {uc.X01:PC817_çıkış_beslemesi:b} pininde (X01), 5 V'ta değil: multimetrenin süreklilik kademesiyle çıkış VCC ile ESP32 {uc.X01:PC817_çıkış_beslemesi:b} pini arası öter, çıkış VCC ile çevre 5 V arası ötmez
47. **eklendi** · metin · `kaynak B6a kontrol`
   - eski: —
   - yeni: PCA9685 V+ boş: multimetrenin süreklilik kademesiyle PCA9685'in V+ klemensi ile dağıtım kartı A'nın ve B'nin V+ barası arasında süreklilik yok (ötmemeli).
48. **eklendi** · metin · `kaynak B6a kontrol`
   - eski: —
   - yeni: Öterse bir V+ teli takılı ya da kartın sinyal girişindeki V+ pini bağlı: o teli ya da bağı sök, ölçüm ötmeyene kadar devam etme
49. **değişti** · metin · `kaynak E3a is_`
   - eski: Bant yoksa ya da iki uçta da işaret varsa (çift yönlü) TVS'i takma (kablajda teyit).
   - yeni: Takmadan önce gövde baskısını oku: P6KE…A (sonu A) tek yönlüdür, renkli bandı katottur; P6KE…CA (sonu CA) çift yönlüdür, bandı yoktur (Vishay P6KE veri sayfası).
50. **değişti** · metin · `kaynak E3a is_`
   - eski: Kafa giriş kartı (P6KE18A üstünde küçük pertinaks parçası): P6KE18A'yı kartın + ve − uçları arasına lehimle, {yon.P6KE18A}.
   - yeni: CA baskılı ya da bantsız TVS'i takma (kablajda teyit).
51. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: Kafa giriş kartı (P6KE18A üstünde küçük pertinaks parçası): P6KE18A'yı kartın + ve − uçları arasına lehimle, {yon.P6KE18A}; baskısını ve bandını madde 2'deki gibi oku (kablajda teyit).
52. **değişti** · metin · `kaynak E3a is_`
   - eski: Girişe K2'de kafa 12 V çifti (G17) gelir, çıkışlar D24V50F5 (K01) ve SY8205'e (K02), {awg.K02}.
   - yeni: Girişe K2'de kafa 12 V çifti (G17) gelir.
53. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: Kartın çıkış klemenslerinden D24V50F5'in girişine (K01) ve SY8205'in girişine (K02) birer çift bağla, {awg.K02}.
54. **değişti** · metin · `kaynak E3a not_`
   - eski: TVS yönü kayıttan (`planlama/adim3/kablolar.json` tvs): Vishay P6KE serisi veri sayfası (belge 88369) tek yönlü tipte renkli bandın katot olduğunu yazıyor.
   - yeni: TVS yönü kayıttan (`planlama/adim3/kablolar.json` tvs): Vishay P6KE serisi veri sayfası (belge 88369) tek yönlü tipte renkli bandın katot olduğunu, çift yönlü tipte (CA soneki) işaret olmadığını yazıyor.
55. **değişti** · metin · `kaynak E3a not_`
   - eski: Satın alınan parçaların üreticisi bilinmiyor: teslimde gövdedeki bant okunur (kablajda teyit)
   - yeni: Satın alınan parçaların üreticisi bilinmiyor: teslimde gövde baskısı (…A / …CA) ve bant okunur (kablajda teyit)
56. **değişti** · metin · `kaynak F1 is_`
   - eski: Kalın pabuç ({awg.G03|G04}; G03, G04) altta, üstte düz pul + yaylı pul; giriş ile çıkışı anahtarın üstündeki işaretten oku (saplama ölçüsü teslimde).
   - yeni: Kalın pabuç ({awg.G03|G04}; G03, G04) altta, üstte düz pul + yaylı pul; giriş ile çıkışı anahtarın üstündeki işaretten oku (anahtarın saplama ölçüsü {vida.ana-anahtar} varsayım, kablajda teyit: başka çıkarsa pabuçları o ölçüde al).
57. **değişti** · metin · `kaynak F1 kontrol`
   - eski: Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin bölücü oranı kadar (`planlama/adim3/elektrik.md` E2: 14,6 V'ta 2,23 V, 10,0 V'ta 1,53 V); 0 V ise G07'nin pabucu, direnci ya da kart ucu kopmuş.
   - yeni: Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin bölücü oranı ({oran.aku_olcum}) katıdır: akü {v.aku_aralik} iken bölücünün orta noktasında {v.aku_olcum} okunur (`planlama/adim3/elektrik.md` E2).
58. **eklendi** · metin · `kaynak F1 kontrol`
   - eski: —
   - yeni: Hiç gerilim okunmuyorsa G07'nin pabucu, direnci ya da kart ucu kopmuş; aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış: ana anahtarı kapat, devam etme.
59. **değişti** · metin · `kaynak K1 is_`
   - eski: Şarj kolu (G06, {awg.G06}): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı saplama, mavi M5 halka pabuç; F1'de takılır); {a.hat-sarj} {bicak.hat-sarj} hat sigortasının kapaklı yuvası {yer.hat-sarj}, kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); − ucu yıldız barasına (mavi pabuç).
   - yeni: Şarj kolu (G06, {awg.G06}): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı saplama, mavi {vida.ana-anahtar} halka pabuç, ana anahtarın saplama ölçüsü kablajda teyit; F1'de takılır); {a.hat-sarj} {bicak.hat-sarj} hat sigortasının kapaklı yuvası {yer.hat-sarj}, kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); − ucu yıldız barasına (mavi pabuç).
60. **değişti** · metin · `kaynak K1 is_`
   - eski: Öbür uçta (G07'nin ana anahtar ucu) direnci telin ucuna lehimle, direncin öbür bacağını kırmızı M5 halka pabucun kovanına lehimle: direnç ile pabuç arasında tel kalmaz; direnci ve kovanı makaronla ört ({yer.R-aku-olcum}).
   - yeni: Öbür uçta (G07'nin ana anahtar ucu) lehimden önce makaronu G07'nin teline geçir: boyu direnci, iki bacağını ve pabucun kovanını birlikte örtecek kadar (lehimden sonra geçmez).
61. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Sonra direnci telin ucuna lehimle, direncin öbür bacağını kırmızı {vida.ana-anahtar} halka pabucun kovanına lehimle (ana anahtarın saplama ölçüsü kablajda teyit): direnç ile pabuç arasında tel kalmaz.
62. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Makaronu direncin üstüne çek ve ısıt: direnç, iki bacağı ve kovan tümüyle örtülü, açıkta bacak kalmaz (G07'nin direnci {yer.R-aku-olcum}).
63. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Gerginlik giderme: G07'yi direncin tel tarafında, ana anahtara giden G04'e kablo bağıyla tuttur; teli çekince yükü kablo bağı taşır, direncin gövdesi ve bacakları değil (bağın yeri kaynakta yok, kablajda teyit).
64. **değişti** · metin · `kaynak K1 is_`
   - eski: 3. F1 {a.F1} → röle K1 kontağı ({kontak.K1}: G08 sigorta kutusundan girişe, G09 çıkıştan anahtarlı baraya; {awg.G09}); F1 → ön şarj kartı → anahtarlı bara (G10, G11; {awg.G11}): G10'u K2 kontağının girişine lehimle, ön şarj direnci ({ohm.onsarj}) çıkış ucunda, G11 direncin öbür bacağından baraya; K2'nin uçları {kontak.K2} (röle pimlerinin yeri kablajda teyit: röle gövdesindeki şema).
   - yeni: 3. F1 {a.F1} → röle K1 kontağı ({kontak.K1}; soketin kuyruk numaraları kablajda teyit: G08 sigorta kutusundan girişe, G09 çıkıştan anahtarlı baraya; {awg.G09}); F1 → ön şarj kartı → anahtarlı bara (G10, G11; {awg.G11}).
65. **değişti** · metin · `kaynak K1 is_`
   - eski: Baradan: iki BTS7960B (G12, G13; {awg.G13}); mini hat sigortalarıyla XL4016 A ve B ({a.hat-A|hat-B}; G14, G15), C ({a.hat-C}; G16, XL4016 C güç panelinde: IN+ / IN− klemensine), {awg.G14|G15|G16}; G14, G15 ve G16'nın hat sigortası yuvası {yer.hat-A|hat-B|hat-C}: yuvanın bir kuyruğu mavi M5 halka pabuçla bara saplamasına, öbür kuyruğu kablonun teline lehim + makaron; XL4016 ucunda sigorta yok.
   - yeni: Ön şarj kartında, lehimden önce K2'nin pimlerini bul: akü ayrıkken röle gövdesindeki şemaya bak, multimetrenin süreklilik kademesinde (bobin boşta) COM ile NC arası öter, COM ile NO arası ötmez (pim yeri kablajda teyit).
66. **değişti** · metin · `kaynak K1 is_`
   - eski: PC817 #2 algı teli (G22, {awg.G22}): {yer.hat-G22} {a.hat-G22} {bicak.hat-G22} hat sigortası, yıldız ucu 5 cm {ara.G22} siyah ara parçaya lehimli, ara parça kırmızı pabuçla.
   - yeni: Sonra G10'u K2 kontağının girişine lehimle, ön şarj direnci ({ohm.onsarj}) çıkış ucunda, G11 direncin öbür bacağından baraya; K2'nin uçları {kontak.K2} (röle pimlerinin yeri kablajda teyit: röle gövdesindeki şema).
67. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Baradan: iki BTS7960B (G12, G13; {awg.G13}); mini hat sigortalarıyla XL4016 A ve B ({a.hat-A|hat-B}; G14, G15), {awg.G14|G15}.
68. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: XL4016 C'yi de mini hat sigortasıyla ({a.hat-C}) baradan güç panelindeki IN+ / IN− klemensine bağla (G16, {awg.G16}).
69. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: G14, G15 ve G16'nın hat sigortası yuvası {yer.hat-A|hat-B|hat-C}: yuvanın bir kuyruğu mavi M5 halka pabuçla bara saplamasına, öbür kuyruğu kablonun teline lehim + makaron; XL4016 ucunda sigorta yok.
70. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: PC817 #2 algı teli (G22, {awg.G22}): {yer.hat-G22} {a.hat-G22} {bicak.hat-G22} hat sigortası.
71. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: G22'nin kutbu {kutup.G22}: + damarını (hat sigortasından gelen) arayüz kartındaki PC817 modülünün {uc.G22:+:b} klemensine, − damarını modülün {uc.G22:−:a} klemensinden yıldız barasına bağla; − damarının yıldız ucu 5 cm {ara.G22} siyah ara parçaya lehimli, ara parça kırmızı pabuçla yıldız barasının {saplama.G22}.
72. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: saplamasına.
73. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Bağlamadan önce modülün üstündeki IN2 + / IN2 − yazısını oku: ters bağlanan G22'de giriş LED'i yanmaz, bara gerilimliyken PC817 #2 ({gpio.BARA_DURUM}) LOW'a düşmez ve ESP32 devreye almada hata verir; modülün girişinde ters gerilim koruması olup olmadığı belgede yok (kablajda teyit), ters bağlıyken enerji verme.
74. **değişti** · metin · `kaynak K1 is_`
   - eski: Burada B3'te etiketli bırakılan öbür uçları yerlerine bağla: G12 ve G13'ün + uçlarını anahtarlı baraya, − uçlarını yıldız barasına; G14 ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baraya (madde 3), − uçlarını yıldız barasına; G18'in + ucunu sigorta kutusunun F4 çıkışına (madde 4), − ucunu yıldız barasına; G19'u arayüz kartının çevre 5 V / GND klemensine; SV1'i dağıtım kartı A'nın, SV2'yi dağıtım kartı B'nin V+ / GND giriş klemensine (OUT+ → V+, OUT− → GND).
   - yeni: Burada B3'te etiketli bırakılan öbür uçları yerlerine bağla: G12 ve G13'ün + uçlarını anahtarlı baraya, − uçlarını yıldız barasına; G14 ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baraya (madde 3), − uçlarını yıldız barasına; G18'in + ucunu sigorta kutusunun F4 çıkışına (madde 4), − ucunu yıldız barasına; G19'u arayüz kartının çevre 5 V / GND klemensine; SV1'i dağıtım kartı A'nın, SV2'yi dağıtım kartı B'nin V+ / GND giriş klemensine ({kutup.SV1|SV2}).
75. **değişti** · metin · `kaynak K1 is_`
   - eski: 7. Direğe çıkacak hatların taban kısmını da burada bağla: kafa servolarının sinyal köprüsü (P03): PCA9685'in kafa pan ve tilt kanallarından dağıtım kartı C'nin pan / tilt sinyal girişlerine 3 pinli köprü (köprünün V+ ucu kartta bağlı değil); kafa 12 V (G17), göğüs 12 V (G20) ve ESP32 USB'nin (U06) taban uçları.
   - yeni: 7. Direğe çıkacak hatların taban kısmını da burada bağla.
76. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Kafa servolarının sinyal köprüsünü (P03), yalnız sinyal teliyle, PCA9685'in kafa pan ve tilt kanallarının sinyal pinlerinden dağıtım kartı C'nin pan / tilt sinyal girişlerine bağla.
77. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: PCA9685'in V+ pinine tel takma; 3 telli hazır kablo kullanırsan V+ damarını iki ucundan kes, makaronla yalıt (B6a madde 4: V+ teli XL4016 C'nin çıkışını A ve B'ninkilere paralel bağlar).
78. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Kafa 12 V (G17), göğüs 12 V (G20) ve ESP32 USB'nin (U06) taban uçlarını bağla.
79. **değişti** · metin · `kaynak K1 kontrol`
   - eski: Akü ölçüm teli (G07): pabuç henüz saplamada değilken, akü ayrık, multimetrenin direnç kademesinde pabuç ile arayüz kartındaki akü ölçüm bölücüsünün orta noktası arası {ohm.aku_olcum}'a yakın; direnç ve pabuç kovanı makaronlu, pabuç bantlı (F1'de ana anahtarın çıkış saplamasına)
   - yeni: Akü ölçüm teli (G07): pabuç henüz saplamada değilken, akü ayrık, multimetrenin direnç kademesinde pabuç ile arayüz kartındaki akü ölçüm bölücüsünün orta noktası arası {ohm.aku_olcum}'a yakın; direnç, iki bacağı ve pabuç kovanı makaronla tümüyle örtülü (açıkta bacak yok), tel direncin yanında G04'e kablo bağıyla tutturulu (çekince direnç gerilmiyor), pabuç bantlı (F1'de ana anahtarın çıkış saplamasına)
80. **değişti** · metin · `kaynak K1 kontrol`
   - eski: Pim yeri röle gövdesindeki şemayla ve akü ayrıkken multimetrenin süreklilik kademesiyle bakıldı (bobin boşta: G10'un pimi ile boş pim arası öter, G10'un pimi ile direncin pimi arası ötmez)
   - yeni: Pim yeri G10 lehimlenmeden önce (madde 3) röle gövdesindeki şemayla ve akü ayrıkken multimetrenin süreklilik kademesiyle bakıldı (bobin boşta: G10'un pimi ile boş pim arası öter, G10'un pimi ile direncin pimi arası ötmez)
81. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: G22'nin kutbu: + damarı (hat sigortası tarafı) PC817 modülünün {uc.G22:+:b} klemensinde, − damarı {uc.G22:−:a} klemensinden yıldız barasında; akü ayrıkken multimetrenin süreklilik kademesiyle {uc.G22:−:a} ile yıldız barası arası öter, {uc.G22:+:b} ile yıldız barası arası ötmez
82. **eklendi** · metin · `kaynak K1 kontrol`
   - eski: —
   - yeni: PCA9685 V+ boş (P03): akü ayrıkken multimetrenin süreklilik kademesiyle PCA9685'in V+ klemensi ile dağıtım kartı C'nin V+ barası arasında süreklilik yok (ötmemeli; B6a'da A ve B için de bakıldı)
83. **değişti** · metin · `kaynak K2 is_`
   - eski: 7. Göğüs ekranı 12 V boyundan geçmez: sigorta kutusunun F6 {a.F6} ({bicak.F6}) yuvasından ayrı dal (K11 a: ana anahtar sonrası, röle öncesi; acil stopta açık kalır) → LM2577 + LM2596 regülatörü (G20) → ekran 12 V jakı (G21), {awg.G21}; direk arka yüzünden çıkar, travers altında direğin soluna geçer, ekran arkasında bırakılır (F3).
   - yeni: 7. Göğüs ekranı 12 V boyundan geçmez: sigorta kutusunun F6 {a.F6} ({bicak.F6}) yuvasından ayrı dal (K11 a: ana anahtar sonrası, röle öncesi; acil stopta açık kalır) → LM2577 + LM2596 regülatörü (G20) → ekran 12 V jakı (G21), {awg.G21}.
84. **eklendi** · metin · `kaynak K2 is_`
   - eski: —
   - yeni: Regülatörün çıkışına ekran 12 V jak kablosunu bağla (G21); kabloyu direğin arka yüzünden, travers altından direğin soluna geçir ve jak ucunu ekran arkasında boşta bırak (ekrana F3'te takılır).

Komutun özeti: `onay kaydı yenilendi: rehber_kritik_onay.json (kablo 94, liste 170, metin 984); 84 fark yazıldı`

### D1.7 Koşular (son düzeltmeden sonra, 02:31–02:33; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Komut | Çıkış | Not |
|---|---|---|
| `planlama/adim3/kablolar_uret.py` | 0 | `kablolar.md` 74 kablo (kayıt düzeltmesinden sonra) |
| `planlama/adim3/kablolar_uret.py --kontrol` | 0 | "kablolar.md ve elektrik.md bloğu güncel" |
| `planlama/adim3/kablolar_denetim.py` | 0 | SONUÇ GEÇER |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0 | 164 / 164 (yeni 8: `b_yon_yer_10` … `_17`) |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 1 → 0 | yenilemeden önce yalnız onay kaydı farkı (84); sonra ASCII 0, elektrik 0, zorunlu eksik 0, yasak 0 (istisna 10: üçü yeni kuralların olumsuz biçimi "bağlama", "takma"), çıplak 0, bağlam 0, kritik fark 0, teyit ibaresi eksik 0; tamlık 172 öğe, eksik 0, kablo talimatta 74 / 74 |
| `tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile` | 0 | 84 fark (D1.6) |
| `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0 | 160 / 160; bozulmamış kaynakta hata 0 |
| `tasarim/freecad/rehber/rehber_kablo.py` | 1 → 0 | yenilemeden önce yalnız onay kaydı (3 fark: SINIF ×2, VURGU_TON); sonra GEÇER |
| `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi` | 0 | 36 / 36 (yeni 4, A9) |
| `tasarim/freecad/rehber/rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GEÇTİ |
| `planlama/d158/F10i-yerlesim-say.py` | 0 | dağılış 14.840, yerleşim 27.000, en kötü köprü 20 A: 27.000 |
| `py_compile` (9 değişen .py; çıktı depo dışına) | 0 | `kablolar_denetim`, `kablolar_uret`, `F10a-dogrula`, `F10e-dogrula`, `F10i-yerlesim-say`, `rehber_deger`, `rehber_denetim`, `rehber_kablo`, `rehber_metin` |
| `node --check rehber/app.js` | 0 | |
| geçici: F10a / F10e vurgu okuyucusu (ast ile, doğrulayıcı koşmadan) | 0 | iki tema doğru; VURGU_TON yok, ton dizge değil: hata veriyor |
| geçici: eski kodda kontrolün bozmaları (1328b60 kopyası, düzeltme öncesi ayna) | 0 | tamlık "K2'de takılır" / "takma", YASAK mantar aynı vida, PCA9685 V+, PC817 5 V, 87a, çıplak 100 kΩ / 4,23 V, K1 SV kutup, K1 87a kayıt: hepsi kaçıyordu |

Değişen dosyalar (bu tur): `planlama/adim3/kablolar.json`, `kablolar.md` (üretildi), `kablolar_denetim.py`, `kablolar_uret.py`;
`planlama/d158/F10a-dogrula.py`, `F10e-dogrula.py`, `F10i-yerlesim-say.py` (yeni), `F10i-gunluk.md`, `karar-kuyrugu.md`;
`planlama/dongu-158.md`; `rehber/app.js`, `rehber/stil.css`; `tasarim/freecad/rehber/rehber_deger.py`, `rehber_denetim.py`,
`rehber_kablo.py`, `rehber_kritik_onay.json`, `rehber_metin.py`.

## Düzeltme turu 2 (15.11, 03:00–03:20; ikinci bağımsız kontrol `planlama/d158/F10i-kontrol-2.md` KAYNAK GEÇER, açık bulgular)

Kapsam: ikinci kontrolün rehber metnini etkileyen açık bulguları, üretimden önce (üretim iki kez koşmasın). Devre değeri (sigorta
akımı, kesit, pin, direnç, süre) değişmedi; FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları ve başsız tarayıcı koşmadı; commit yok;
kontrol raporlarına dokunulmadı. Her koruyucu kural için: kontrolün bozması eski kodda yeniden üretildi (kaçtı), şimdi yakalanıyor,
kalıcı bozma listesine girdi; bozulmamış kaynakta yanlış alarm 0.

### D2.1 Bulgu → yapılan → kanıt

| # | Bulgu | Yapılan | Kanıt (eski kodda → şimdi) |
|---|---|---|---|
| 1 | **AU3 hoparlör talimatı** (§3: AU3 ve H02 yalnız liste cümlesinde) | K2 madde 5: "Hoparlör kablosunun (AU3) kafa ucunu PAM8403'ün sol kanal çıkışına lehimle: + damarını {uc.AU3:+:a} ucuna, − damarını {uc.AU3:−:a} ucuna" (L+ / L−); F2 madde 3 hoparlör ucu "{uc.AU3:+:b} / {uc.AU3:−:b}", kutbu {kutup.AU3} (L+ → +, L− → −; hoparlörün + işareti kablajda teyit); F3 madde 3 "HDMI (H02) ve 12 V (G21) uçlarını … ekrana tak" (`rehber_metin.py:825`, `:1007`, `:1105`). Uçlar kayıttan (`kablolar.json` AU3 damarları) | Tamlık bozması "AU3 / H02 yalnız liste cümlesinde": eski kodda kaçtı (liste cümlesi talimat sayılıyordu) → yakalandı; tamlık 74 / 74 |
| 2 | **Ok kuralı** liste / sayım cümlesini talimat sayıyordu | `TALIMAT_OK` ok iki yanında sözcük / uç ister; `TALIMAT_LISTE` ("N kablo / tel / hat / uç") varsa cümle talimat sayılmaz (`rehber_denetim.py:1289-1290`, `:1324`); ikisi onay kaydında | Aynı bozma (madde 1); emir kipindeki cümlelerde yanlış alarm 0 |
| 3 | **G07 lehim sırası** (yalıtımlı pabucun kovanına lehim PVC kılıfı eritir) ve F1'de aralık dışı okuma | K1: önce PVC kılıf çıkar, makaron tele geçer, direnç tele lehimlenir, bacak kovana sıkılır (pabuç pensesiyle), sonra lehim; makaron soğuyunca direncin ve kovanın üstüne (`rehber_metin.py:325-330`). F1 kontrol: okuma aralık dışında → ana anahtarı kapat, aküyü ayır, bölücüyü kontrol et; düzelene kadar ana anahtarı açma, ESP32'ye bu bölücüyle enerji verme, F5'e geçme (`:918`). Kayıt: G07 `uc_kuyrugu.a.ne`, `sonlandirma`, `koruyucular.R-aku-olcum.yer` | ZORUNLU sıra deseni + ZORUNLU_ALAN F1 kontrol; bozma "kılıf çıkarma silindi", "lehimden sonra sıkma", "makaron soğumadan", "aralık dışı talimatı silindi": eski kodda kaçtı → yakalandı |
| 4 | **P01–P03 V+ ölçü noktası**; P03'te "3 pinli köprü" | B6a ve K1 kontrol: "kanal başlığının V+ pini ile dağıtım kartı … V+ barası arasında süreklilik yok (… ölçü ucu V+ klemensine değil kanal başlığının V+ pinine: kartta klemens ile V+ rayı arasında ters kutup koruması olabilir)" (`:282`, `:450`); P01–P03 `not` ve P03 `sonlandirma` "yalnız sinyal teli … tek telli dişi uç" (`kablolar.json:4986`, `:5103`, `:5153`, `:5200`) | ZORUNLU_ALAN desenleri güncellendi; bozma "P01 / P02 ölçü noktası klemens", "P03 ölçü noktası klemens": eski kodda kaçtı → yakalandı |
| 5 | **TVS ifadesi** ("P6KE…A" "…CA"yı da kapsıyordu) | "sonu yalnız A (ör. P6KE18A) tek yönlüdür, renkli bandı katottur; sonu CA (ör. P6KE18CA) çift yönlüdür, bandı yoktur" (`rehber_metin.py:606`, not_ `:637`); kayıt `tvs[*].isaret`, `teyit` (`kablolar.json:10656-10682`) | ZORUNLU güncellendi; bozma "TVS muğlak ifade (P6KE…A)": yakalandı |
| 6 | **PC817 jumper** | Kayıtta yok: `elektrik.md:241` jumper konumunu yazmıyor, `pin-haritasi.md` ve `kablolama-on-kararlar` jumper anmıyor. Talimat yazılmadı; `karar-kuyrugu.md:1446` açık iş "kablajda teyit" | — |
| 7 | Günlük §10 "menekşe" | "fuşya (#e014ff; düzeltme turu 1'de menekşe #a35ef2'den değişti)" (`F10i-gunluk.md:462`) | — |
| 8 | **B16** mantarın iki ucu tek pabuçta / "aynı pabuca" | F1 iş ve alt adım: "A01'i NC girişine, A02'yi NC çıkışına" ayrı uçlar (ZORUNLU + ZORUNLU_ALAN); YASAK "aynı vidada" `(?:aynı\|tek\|ortak)\s+(?:vida\|klemens\|saplama\|pabu[çc])`; yeni YASAK "acil stop telleri tek uçta" (`rehber_denetim.py:481-490`) | Eski kodda zorunlu farkı 0, yasak 0 ("aynı pabuca" `pabuç\w*` ile tutmuyordu) → 2 zorunlu + 4 yasak bozması yakalandı, 2 yakalanmamalı yakalanmadı (`:1650-1654`) |
| 9 | **B18** A06 + ucu (F5 girişine yazılabiliyordu) | Yeni yer tutucu `{parca.A06:+:a}` (kayıttaki damar ucunun parçası: "acil stop düğümü (mantar NC çıkışı)", `rehber_deger.py:205`); K1: "A06'nın + ucunu {parca.A06:+:a} noktasına, yani acil stop düğüm kartında … lehimle" (`rehber_metin.py:378`); ZORUNLU_CUMLE | Eski kodda zorunlu farkı 0 → "F5 girişinde", "düğüm elle değişti": yakalandı (`rehber_denetim.py:1684-1686`) |
| 10 | **B23** K2 pim okuması ters yazılabiliyordu | `{kontak.K2:giris\|cikis\|bos}` (COM / NO / NC, kayıttan); K1: "(bobin boşta) {kontak.K2:giris} ile {kontak.K2:bos} arası öter, {kontak.K2:giris} ile {kontak.K2:cikis} arası ötmez" (`rehber_metin.py:351`); ZORUNLU_CUMLE | Eski kodda zorunlu farkı 0 → "okuma ters", "uçlar yer değişti": yakalandı (`rehber_denetim.py:1687-1689`) |
| 11 | **B27** bölücü değişince beklenen aralık ADC sınırını aşabiliyordu | `kablolar_denetim.py` `s_koruyucu` (`:833`): akü üst sınırı × oran ≤ "doğrusal bölge ≤ N V", satırdaki her "N V → M V" çifti oranla ±0,01 V, değer eksikse hata; `rehber_deger.py:252-258` aynı sınamayla KeyError | Eski kodda 18 → 33 kΩ hatasız çözüldü (oran 0,2481, 3,18–3,57 V) → `b_koruyucu_8` (18 → 33 kΩ), `_9` (10,0 V → 1,83 V), `_10` (sınır silindi) GÜVENLİK; rehber_deger bölücü denemesi 3 yakalandı, 18 → 15 kΩ (sınır içinde) yakalanmadı |
| 12 | **R5** çıplak 100 kΩ (bağlam sözcüğü 40 karakter dışında) | `CIPLAK_PENCERE` kural başına: direnç ve "gerilim (akü ölçümü)" 120, öbürleri 40 (`rehber_denetim.py:1156-1161`); onay kaydında | Eski kodda kaçtı → "R5 K1 G07 direnç ölçümü elle", "R5 K1 kontrol direnç ölçümü elle": yakalandı (`:1602-1605`); 120 her kurala uygulanınca F5 "0,5 s" yanlış alarm verdi, bu yüzden kural başına |

Açık işler (`karar-kuyrugu.md:1446-1456`, yoksa eklendi): PC817 jumper (yeni), F10e ton ölçüsü `gecti` dışında ve ΔE76 (yeni), F10a tema
eşlemesi (yeni), kopya ton karşıtlığı 1,33 / ΔE00 8,2 (yeni); ASCII kapsamı (A8), dağıtım kartı C yeri (A12) ve kondansatör yedeği zaten
kayıtlıydı.

### D2.2 Reddedilen ya da yorumlanan

- **F1 "ESP32'ye bağlama":** bölücünün orta noktası B6a'da (X01) ESP32'ye zaten bağlı; yeniden bağlanacak bir tel yok. Talimat "bölücü
  düzelip okuma aralığa girene kadar ana anahtarı yeniden açma, ESP32'ye bu bölücüyle enerji verme, aşama 2'ye (F5) geçme" diye yazıldı.
- **PC817 jumper:** kayıtta yok, talimat uydurulmadı (madde 6).
- **P7b2a-5 karar metni** (`kablolar.json`) tarih kaydı olduğu için değişmedi; geçerli metin G07 alanlarında.

### D2.3 Kayda eklenenler (`planlama/adim3/kablolar.json`, 13 alan) ve dayanağı

- G07 `uc_kuyrugu.a.ne`, `sonlandirma`; `koruyucular.R-aku-olcum.yer` "(PVC kılıfı çıkarılmış) sıkma + lehim": orkestratör kararı 15.11
  (yalıtımlı pabucun kovanına lehim kılıfı eritir).
- P01, P02, P03 `not` (Kontrol cümlesi kanal başlığının V+ pini); P03 `sonlandirma` yalnız sinyal teli, tek telli dişi uç (O-8).
- `tvs[*].isaret`, `teyit` (3 kayıt): "sonu yalnız A / sonu CA"; kaynak Vishay P6KE veri sayfası (belge 88369).
- Devre değeri, adet ve durum alanları değişmedi; `kablolar.md` `kablolar_uret.py` ile üretildi; `elektrik.md` değişmedi.

### D2.4 Kablajda teyit kalanlar

Hoparlörün + işareti; PC817 modülünün jumper konumu; direnç bacağının pabuç kovanında sıkılınca tutması (kovan çapı); PCA9685 kartında
kanal başlığı V+ rayı ile V+ klemensi arasındaki ters kutup koruması; D1.4'tekiler sürüyor.

### D2.5 Sipariş listesine etkisi

Yok: pabuç rengi, ölçüsü ve adedi aynı (PVC kılıf yalnız çıkarılıyor); yeni parça yok. `kablolar_denetim.py` malzeme sınaması GEÇER.

### D2.6 Onay kaydı farkı (`rehber_denetim.py --kritik-onay-yenile`, 03:15:03; tam liste)

1. **eklendi** · liste · `LISTE CIPLAK_PENCERE`
   - eski: —
   - yeni: [('direnç', 120), ('direnç (sözle)', 120), ('gerilim (akü ölçümü)', 120)]
2. **eklendi** · liste · `LISTE CIPLAK_PENCERE_VARSAYILAN`
   - eski: —
   - yeni: 40
3. **eklendi** · liste · `LISTE TALIMAT_LISTE`
   - eski: —
   - yeni: '(?<!\\w)\\d+\\s+(?:kablo\|tel\|hat\|uç)\\w*(?!\\w)'
4. **eklendi** · liste · `LISTE TALIMAT_OK`
   - eski: —
   - yeni: "[\\w)'’+−]\\s*→\\s*[\\w(+−]"
5. **değişti** · liste · `LISTE YASAK`
   - eski: ('mantar / ana anahtar uçları aynı vidada', '\\b(?:mantar\\w*\|ana\\s+anahtar\\w*)(?:\\s+\\w+){0,3}?\\s+(?:uç(?:lar\|ları)\\w*\|iki\\s+uc\\w*\|giriş\\w*\\s+ve\\s+çıkış\\w*)[^.;!?\\n]{0,40}?\\baynı\\s+(?:vida\|klemens\|saplama\|pabuç)\\w*[^.;!?\\n]{0,30}?\\b(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|bağlantı\\s+yap)\\w*\|\\baynı\\s+(?:vida\|klemens\|saplama\|pabuç)\\w*[^.;!?\\n]{0,30}?\\b(?:mantar\\w*\|ana\\s+anahtar\\w*)(?:\\s+\\w+){0,3}?\\s+(?:uç(?:lar\|ları)\\w*\|iki\\s+uc\\w*\|giriş\\w*\\s+ve\\s+çıkış\\w*)[^.;!?\\n]{0,30}?\\b(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|bağlantı\\s+yap)\\w*', '(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|yap)(?:ma\|me)(?:z\|dan\|den\|yın\|yin\|yınız\|yiniz\|malı\|meli)?\|(?:bağla\|tak\|sök\|çıkar\|kes\|değiştir\|yap)(?:ıl\|il\|ul\|ül)?(?:maz\|mez)')
   - yeni: ('mantar / ana anahtar uçları aynı vidada', '\\b(?:mantar\\w*\|ana\\s+anahtar\\w*)(?:\\s+\\w+){0,3}?\\s+(?:uç(?:lar\|ları)\\w*\|iki\\s+uc\\w*\|giriş\\w*\\s+ve\\s+çıkış\\w*)[^.;!?\\n]{0,40}?\\b(?:aynı\|tek\|ortak)\\s+(?:vida\|klemens\|saplama\|pabu[çc])\\w*[^.;!?\\n]{0,30}?\\b(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|bağlantı\\s+yap)\\w*\|\\b(?:aynı\|tek\|ortak)\\s+(?:vida\|klemens\|saplama\|pabu[çc])\\w*[^.;!?\\n]{0,30}?\\b(?:mantar\\w*\|ana\\s+anahtar\\w*)(?:\\s+\\w+){0,3}?\\s+(?:uç(?:lar\|ları)\\w*\|iki\\s+uc\\w*\|giriş\\w*\\s+ve\\s+çıkış\\w*)[^.;!?\\n]{0,30}?\\b(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|bağlantı\\s+yap)\\w*', '(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|yap)(?:ma\|me)(?:z\|dan\|den\|yın\|yin\|yınız\|yiniz\|malı\|meli)?\|(?:bağla\|tak\|sök\|çıkar\|kes\|değiştir\|yap)(?:ıl\|il\|ul\|ül)?(?:maz\|mez)')
6. **eklendi** · liste · `LISTE YASAK`
   - eski: —
   - yeni: ('acil stop telleri tek uçta', '\\bA0[12]\\b[^.;!?\\n]{0,40}?\\bA0[12]\\b[^.;!?\\n]{0,30}?\\b(?:aynı\|tek\|ortak\|bir)\\s+(?:vida\|klemens\|saplama\|pabu[çc]\|uç\|uca\|kontak)\\w*[^.;!?\\n]{0,30}?\\b(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|bağlantı\\s+yap)\\w*', '(?:bağla\|tak\|lehimle\|sök\|çıkar\|vidala\|sık\|kes\|değiştir\|yap)(?:ma\|me)(?:z\|dan\|den\|yın\|yin\|yınız\|yiniz\|malı\|meli)?\|(?:bağla\|tak\|sök\|çıkar\|kes\|değiştir\|yap)(?:ıl\|il\|ul\|ül)?(?:maz\|mez)')
7. **değişti** · liste · `LISTE ZORUNLU`
   - eski: ('K1', 'direncin öbür bacağını kırmızı {vida.ana-anahtar} halka pabucun kovanına lehimle', 'G07 direnci pabuç kovanında (K63)')
   - yeni: ('K1', "halka pabucun PVC kılıfını çıkar.{0,260}?makaronu G07'nin teline geçir.{0,300}?Direncin öbür bacağını pabucun kovanına sık \\(pabuç pensesiyle\\), sonra kovana lehimle.{0,120}?Soğuyunca makaronu direncin ve kovanın üstüne çek", 'G07 direnci pabuç kovanında: kılıf çıkar, makaron, sık, lehimle, makaron (K63)')
8. **değişti** · liste · `LISTE ZORUNLU`
   - eski: ('E3a', 'P6KE…A \\(sonu A\\) tek yönlüdür, renkli bandı katottur; P6KE…CA \\(sonu CA\\) çift yönlüdür, bandı yoktur', 'TVS: gövde baskısı (…A tek yönlü, …CA çift yönlü)')
   - yeni: ('E3a', 'sonu yalnız A \\(ör\\. P6KE18A\\) tek yönlüdür, renkli bandı katottur; sonu CA \\(ör\\. P6KE18CA\\) çift yönlüdür, bandı yoktur', 'TVS: gövde baskısı (sonu yalnız A tek yönlü, sonu CA çift yönlü)')
9. **eklendi** · liste · `LISTE ZORUNLU`
   - eski: —
   - yeni: ('F1', "iki acil stop ucunu mantarın NC kontağına bağla: A01'i NC girişine, A02'yi NC çıkışına", 'F1 alt adım: mantarın iki ucu ayrı (A01 NC girişi, A02 NC çıkışı)')
10. **değişti** · liste · `LISTE ZORUNLU_ALAN`
   - eski: ('B6a', 'kontrol', "PCA9685'in V\\+ klemensi ile dağıtım kartı A'nın ve B'nin V\\+ barası arasında süreklilik yok", 'B6a kontrol: PCA9685 V+ ile dağıtım kartı A / B V+ arası ötmez')
   - yeni: ('B6a', 'kontrol', "PCA9685'in kanal başlığının V\\+ pini ile dağıtım kartı A'nın ve B'nin V\\+ barası arasında süreklilik yok", 'B6a kontrol: PCA9685 kanal başlığı V+ ile dağıtım kartı A / B V+ arası ötmez')
11. **değişti** · liste · `LISTE ZORUNLU_ALAN`
   - eski: ('K1', 'kontrol', "PCA9685'in V\\+ klemensi ile dağıtım kartı C'nin V\\+ barası arasında süreklilik yok", 'K1 kontrol: PCA9685 V+ ile dağıtım kartı C V+ arası ötmez (P03)')
   - yeni: ('K1', 'kontrol', "PCA9685'in kanal başlığının V\\+ pini ile dağıtım kartı C'nin V\\+ barası arasında süreklilik yok", 'K1 kontrol: PCA9685 kanal başlığı V+ ile dağıtım kartı C V+ arası ötmez (P03)')
12. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('F1', 'is_', "A01'i \\(F5 {a.F5} çıkışından gelen\\) NC girişine, A02'yi \\(acil stop düğümüne giden\\) NC çıkışına", 'F1 iş: mantarın iki ucu ayrı (A01 NC girişi, A02 NC çıkışı)')
13. **eklendi** · liste · `LISTE ZORUNLU_ALAN`
   - eski: —
   - yeni: ('F1', 'kontrol', "Okuma {v.aku_olcum} aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır", 'F1 kontrol: G07 okuması aralık dışındaysa akü ayrılır')
14. **eklendi** · liste · `LISTE ZORUNLU_CUMLE`
   - eski: —
   - yeni: ('K1', "A06'nın \\+ ucunu", "A06'nın \\+ ucunu {parca.A06:+:a} noktasına, yani acil stop düğüm kartında bir klemensin kuyruğuna \\(kart altı\\) lehimle", "K1 is_: A06'nın + ucu kayıttaki düğümde (acil stop algısı)")
15. **eklendi** · liste · `LISTE ZORUNLU_CUMLE`
   - eski: —
   - yeni: ('K1', "lehimden önce K2'nin pimlerini bul", '\\(bobin boşta\\) {kontak.K2:giris} ile {kontak.K2:bos} arası öter, {kontak.K2:giris} ile {kontak.K2:cikis} arası ötmez', 'K1 is_: K2 pim okuması kayıttaki kontak uçlarıyla (COM ↔ NC öter, COM ↔ NO ötmez)')
16. **değişti** · metin · `kaynak B6a kontrol`
   - eski: PCA9685 V+ boş: multimetrenin süreklilik kademesiyle PCA9685'in V+ klemensi ile dağıtım kartı A'nın ve B'nin V+ barası arasında süreklilik yok (ötmemeli).
   - yeni: PCA9685 V+ boş: multimetrenin süreklilik kademesiyle PCA9685'in kanal başlığının V+ pini ile dağıtım kartı A'nın ve B'nin V+ barası arasında süreklilik yok (ötmemeli; ölçü ucu V+ klemensine değil kanal başlığının V+ pinine: kartta klemens ile V+ rayı arasında ters kutup koruması olabilir).
17. **değişti** · metin · `kaynak E3a is_`
   - eski: Takmadan önce gövde baskısını oku: P6KE…A (sonu A) tek yönlüdür, renkli bandı katottur; P6KE…CA (sonu CA) çift yönlüdür, bandı yoktur (Vishay P6KE veri sayfası).
   - yeni: Takmadan önce gövde baskısını oku: sonu yalnız A (ör.
18. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: P6KE18A) tek yönlüdür, renkli bandı katottur; sonu CA (ör.
19. **eklendi** · metin · `kaynak E3a is_`
   - eski: —
   - yeni: P6KE18CA) çift yönlüdür, bandı yoktur (Vishay P6KE veri sayfası).
20. **değişti** · metin · `kaynak E3a not_`
   - eski: Satın alınan parçaların üreticisi bilinmiyor: teslimde gövde baskısı (…A / …CA) ve bant okunur (kablajda teyit)
   - yeni: Satın alınan parçaların üreticisi bilinmiyor: teslimde gövde baskısı (sonu yalnız A ya da CA) ve bant okunur (kablajda teyit)
21. **değişti** · metin · `kaynak F1 kontrol`
   - eski: Hiç gerilim okunmuyorsa G07'nin pabucu, direnci ya da kart ucu kopmuş; aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış: ana anahtarı kapat, devam etme.
   - yeni: Hiç gerilim okunmuyorsa G07'nin pabucu, direnci ya da kart ucu kopmuş; aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış.
22. **eklendi** · metin · `kaynak F1 kontrol`
   - eski: —
   - yeni: Okuma {v.aku_olcum} aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök; akü ayrıkken bölücüyü kontrol et: G07'nin direnci (pabuç ile bölücünün orta noktası arası, K1 kontrolündeki direnç ölçümü), direncin ve G07'nin iki ucundaki lehim, bölücünün alt direnci (akü {v.aku_aralik} dışındaysa okuma da bölücü oranı kadar kayar).
23. **eklendi** · metin · `kaynak F1 kontrol`
   - eski: —
   - yeni: Bölücünün orta noktası ESP32'nin akü ölçüm pinine bağlı (B6a, X01): bölücü düzelip okuma aralığa girene kadar ana anahtarı yeniden açma, ESP32'ye bu bölücüyle enerji verme, aşama 2'ye (F5) geçme.
24. **değişti** · metin · `kaynak F2 alt adım 8 is_`
   - eski: Bandı takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (PAM8403'ten boyundan iner) hoparlöre bağla.
   - yeni: Bandı takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (AU3) hoparlöre lehimle, kutbu {kutup.AU3} (madde 3).
25. **değişti** · metin · `kaynak F2 is_`
   - eski: Orta bandı takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (PAM8403'ten boyundan iner) hoparlöre bağla.
   - yeni: Orta bandı takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (AU3; kafa ucu K2'den beri PAM8403'te) hoparlöre lehimle, kutbu {kutup.AU3}: + damarını hoparlörün {uc.AU3:+:b} ucuna, − damarını {uc.AU3:−:b} ucuna (hoparlörün + işareti kablajda teyit).
26. **değişti** · metin · `kaynak F3 is_`
   - eski: Sonra K2'de bırakılan HDMI ve 12 V uçlarını enerjisizken tak (90° fişler; ekranlı ilk açılışta F6 atmamalı, KT3: F5 aşama 2).
   - yeni: Sonra K2'de bırakılan HDMI (H02) ve 12 V (G21) uçlarını enerjisizken ekrana tak (90° fişler; ekranlı ilk açılışta F6 atmamalı, KT3: F5 aşama 2).
27. **değişti** · metin · `kaynak K1 is_`
   - eski: Öbür uçta (G07'nin ana anahtar ucu) lehimden önce makaronu G07'nin teline geçir: boyu direnci, iki bacağını ve pabucun kovanını birlikte örtecek kadar (lehimden sonra geçmez).
   - yeni: Öbür uçta (G07'nin ana anahtar ucu), lehimden önce: kırmızı {vida.ana-anahtar} halka pabucun PVC kılıfını çıkar (ana anahtarın saplama ölçüsü kablajda teyit); yalıtımlı pabucun kovanına lehim kılıfı eritir.
28. **değişti** · metin · `kaynak K1 is_`
   - eski: Sonra direnci telin ucuna lehimle, direncin öbür bacağını kırmızı {vida.ana-anahtar} halka pabucun kovanına lehimle (ana anahtarın saplama ölçüsü kablajda teyit): direnç ile pabuç arasında tel kalmaz.
   - yeni: Sonra lehimden önce makaronu G07'nin teline geçir: boyu direnci, iki bacağını ve pabucun kovanını birlikte örtecek kadar (lehimden sonra geçmez).
29. **değişti** · metin · `kaynak K1 is_`
   - eski: Makaronu direncin üstüne çek ve ısıt: direnç, iki bacağı ve kovan tümüyle örtülü, açıkta bacak kalmaz (G07'nin direnci {yer.R-aku-olcum}).
   - yeni: Direnci telin ucuna lehimle.
30. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Direncin öbür bacağını pabucun kovanına sık (pabuç pensesiyle), sonra kovana lehimle: direnç ile pabuç arasında tel kalmaz.
31. **eklendi** · metin · `kaynak K1 is_`
   - eski: —
   - yeni: Soğuyunca makaronu direncin ve kovanın üstüne çek ve ısıtarak büz: direnç, iki bacağı ve kovan tümüyle örtülü, açıkta bacak kalmaz (G07'nin direnci {yer.R-aku-olcum}).
32. **değişti** · metin · `kaynak K1 is_`
   - eski: Ön şarj kartında, lehimden önce K2'nin pimlerini bul: akü ayrıkken röle gövdesindeki şemaya bak, multimetrenin süreklilik kademesinde (bobin boşta) COM ile NC arası öter, COM ile NO arası ötmez (pim yeri kablajda teyit).
   - yeni: Ön şarj kartında, lehimden önce K2'nin pimlerini bul: akü ayrıkken röle gövdesindeki şemaya bak, multimetrenin süreklilik kademesinde (bobin boşta) {kontak.K2:giris} ile {kontak.K2:bos} arası öter, {kontak.K2:giris} ile {kontak.K2:cikis} arası ötmez (pim yeri kablajda teyit).
33. **değişti** · metin · `kaynak K1 is_`
   - eski: PC817 #1 girişi düğümden (A06, {awg.A06}; {gpio.ACIL_STOP_DURUM} okur): A06'nın + ucunu acil stop düğüm kartında bir klemensin kuyruğuna (kart altı) lehimle, modülün IN1 + klemensine bağla; − ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle (makaron).
   - yeni: PC817 #1 girişi düğümden (A06, {awg.A06}; {gpio.ACIL_STOP_DURUM} okur): A06'nın + ucunu {parca.A06:+:a} noktasına, yani acil stop düğüm kartında bir klemensin kuyruğuna (kart altı) lehimle, modülün IN1 + klemensine bağla; − ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle (makaron).
34. **değişti** · metin · `kaynak K1 kontrol`
   - eski: PCA9685 V+ boş (P03): akü ayrıkken multimetrenin süreklilik kademesiyle PCA9685'in V+ klemensi ile dağıtım kartı C'nin V+ barası arasında süreklilik yok (ötmemeli; B6a'da A ve B için de bakıldı)
   - yeni: PCA9685 V+ boş (P03): akü ayrıkken multimetrenin süreklilik kademesiyle PCA9685'in kanal başlığının V+ pini ile dağıtım kartı C'nin V+ barası arasında süreklilik yok (ötmemeli; ölçü ucu klemense değil kanal başlığının V+ pinine; B6a'da A ve B için de bakıldı)
35. **eklendi** · metin · `kaynak K2 is_`
   - eski: —
   - yeni: Hoparlör kablosunun (AU3) kafa ucunu PAM8403'ün sol kanal çıkışına lehimle: + damarını {uc.AU3:+:a} ucuna, − damarını {uc.AU3:−:a} ucuna; gövde ucunu fişsiz bırak (madde 6), F2'de hoparlöre lehimlenir.

Komutun özeti: `onay kaydı yenilendi: rehber_kritik_onay.json (kablo 94, liste 180, metin 991); 35 fark yazıldı`

### D2.7 Koşular (son düzeltmeden sonra, 03:17:37–03:18:59; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Komut | Çıkış | Not |
|---|---|---|
| `planlama/adim3/kablolar_uret.py --kontrol` | 0 | "kablolar.md ve elektrik.md bloğu güncel" |
| `planlama/adim3/kablolar_denetim.py` | 0 | SONUÇ GEÇER (koruyucu, malzeme dahil) |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0 | 167 / 167 (önce 164; yeni `b_koruyucu_8`, `_9`, `_10`) |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 1 → 0 | yenilemeden önce yalnız onay kaydı farkı (35); sonra ASCII 0, elektrik 0, zorunlu eksik 0, yasak 0 (istisna 10), çıplak 0, çözülemeyen yer tutucu 0, bağlam 0, kritik fark 0, teyit ibaresi eksik 0; tamlık 172 öğe, eksik 0, kablo talimatta 74 / 74 |
| `tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile` | 0 | 35 fark (D2.6) |
| `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0 | 185 / 185 (önce 160; yeni 25: zorunlu 13, yasak 6, çıplak 2, bölücü 3, tamlık 1); bozulmamış kaynakta hata 0 |
| `tasarim/freecad/rehber/rehber_kablo.py` | 0 | GEÇER; onay kaydı (kablo bölümü) tutuyor |
| `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi` | 0 | 36 / 36 |
| `tasarim/freecad/rehber/rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GEÇTİ |
| `py_compile` (4 değişen .py; çıktı depo dışına) | 0 | `rehber_deger`, `rehber_denetim`, `rehber_metin`, `kablolar_denetim` |
| `node --check rehber/app.js` | 0 | |
| geçici: eski kodda kontrolün bozmaları (düzeltme öncesi) | 0 | AU3 / H02 liste cümlesi, B16 tek / aynı pabuç, B18, B23, R5, B27 (18 → 33 kΩ): hepsi kaçıyordu |

Değişen dosyalar (bu tur): `planlama/adim3/kablolar.json`, `kablolar.md` (üretildi), `kablolar_denetim.py`;
`planlama/d158/F10i-gunluk.md`, `karar-kuyrugu.md`; `planlama/dongu-158.md`; `tasarim/freecad/rehber/rehber_deger.py`,
`rehber_denetim.py`, `rehber_kritik_onay.json`, `rehber_metin.py`.

## Üretim ve zincir (15.11, üretim ajanı U)

15.11.2026 03:24–05:03 (saat okundu). Dal `lale-duzeltme`, HEAD `1328b60`, kaynak çalışma ağacında. Yöntem F10g § 5 / F10h § 14:
depo dışındaki geçici klasörde `baslat.ps1` → `sarmal.ps1` (15 s bellek bekçisi, eşik 1,2 GB art arda iki ölçüm) → yoklama, her
koşunun `.durum` kaydı; her koşu `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`. **Kaynağa dokunulmadı, kod düzeltmesi yapılmadı.**
Aynı saatlerde üçüncü dar bakış (`F10i-kontrol-3.md`, SON TUR GEÇER) depoyu yalnız okudu; kaynak dosyalarının son yazımı 03:15:03
(onay kaydı), üretimden (03:25:31) önce.

**FreeCAD kilidi:** 03:25 satır yazıldı ("P10.7b2a üretim (ajan U) rehber_uret.py"), FreeCAD aşaması (veri 178 s) bitip `freecadcmd`
kapandıktan sonra 03:31'de "boş". Son hâli "boş". FreeCAD'in Python'u `-B`'ye karşın dört `__pycache__` yazdı (`planlama/adim4`,
`tasarim/freecad`, `tasarim/freecad/lale158`, `tasarim/freecad/rehber`; gitignore'da, üretimden önce yoktu); iş sonunda silindi.

### Ön sınama (FreeCAD'siz, 03:24:27–03:25:09)

| Komut | Çıkış | Süre | Beklenen ↔ ölçülen |
| --- | --- | --- | --- |
| `kablolar_uret.py --kontrol` | 0 | < 1 s | "güncel" ↔ "kablolar.md ve elektrik.md bloğu güncel" |
| `kablolar_denetim.py` | 0 | 1 s | GEÇER ↔ SONUÇ GEÇER (`yon_yer` dahil) |
| `rehber_denetim.py --kaynak` | 0 | 1 s | D2.7 ↔ aynı: metin 545, bütün sayılar 0 (yasak istisna 10), onay farkı 0 (kayıt kablo 94 / liste 180 / metin 991), tamlık 172 / eksik 0 / muaf 21, kablo talimatta 74 / 74 |
| `rehber_kablo.py` | 0 | 1 s | GEÇER, 51 / 23, geometri hata 0 / bilgi 4, onay tutuyor ↔ aynı |
| `rehber_kol_kablo.py --yazma` | 0 | 39 s | GEÇTİ, 38 bölüm ↔ aynı |
| `node --check rehber/app.js` | 0 | — | 0 |

### Zincir

| Sıra | Komut | Başlangıç | Çıkış | Süre (s) | Beklenen | Ölçülen |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rehber_uret.py` (tam) | 03:25:31 | **2** | 2527 | çıkış 0 | **çıkış 2**: "ek kontrol sorunlu: ['yazdir']" (S1); bütün çıktılar yazıldı |
| 1 | ön sınama satırı | | | | kayıt tutuyor | "on sinama: kaynak denetimi gecti, onay kaydi tutuyor (kablo 94, liste 180, metin 991)" |
| 1 | parça / şema / alt adım | | | | 1192 / 49 / 71 | 1192 / 49 / 71 (71 geçti); tarayıcı 50 / 50, konsol hatası 0 |
| 1 | kablo eşleme | | | | GEÇTİ, 51 / 23 | "kablo esleme: GECTI"; `kontrol.json` `gecti` true, 51 / 23, `eslesmeyen` [] |
| 1 | denetim | | | | elektrik 0 | ASCII 0, elektrik 0, zorunlu uyarı eksik 0 / 98, yasak 0 (istisna 10) |
| 1 | uçuş / sıra / giriş / perdelenme | | | | 340 / 0 / 16; 0; 0; gerekçesiz 0 | 340 satır, çarpışan 0, istisna 16; 565 bağlantı ulaşılamaz 0; girilemez 0; gerekçesiz 0, istisna 117, toplam gizli 264 |
| 1 | PDF | | | | ≥ 77 sayfa, taşan 0 | **79 sayfa** (adım 50 + devam 29), en küçük yazı 8,1 pt, 16141 kB, baskı karesi 121 / 121; **taşan ['17']**, `yazdir.gecti` false (S1, S2) |
| 2 | `rehber_kablo.py --veri …` | 04:10:17 | 0 | 0 | hata 0 | GEÇER, "veri: eşlemesiz çizim 0", onay tutuyor; en yakın ton light vurgu ↔ lazer 16,6 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 04:10:17 | 0 | 2 | yakalanır | 44 / 44 (36 kaynak + 8 veri) |
| 2a | geometrik eşleme (aynı koşu) | | | | hata 0 | hata 0, bilgi 4 (yol 9, 12 istisnalı; yol 10 A04 / A06 elle) |
| 3 | `rehber_denetim.py` (veri) | 04:10:20 | 0 | 1 | elektrik / yasak 0 | ASCII 0, elektrik 0, yasak 0, zorunlu eksik 0 / 98, parça 1192, şema 49 |
| 4 | `F10f-dogrula.py` | 04:10:20 | 0 | 572 | GEÇTİ | GEÇTİ; `kablo_kare` 76 / 76 (en düşük oran 0,483, en az fark 1135 px), `sonra` geçti |
| 5 | `F10e-dogrula.py --goruntu-yok` | 04:19:52 | 0 | 883 | çıkış 0, renk_demo KALDI | GEÇTİ; renk_sahne yanlış 0 (1192 / 1192); renk_demo KALDI (karar). **İlk gerçek koşu:** `VURGU_TON` okundu: `secim_light` #e014ff (zemin 3,06), `secim_dark` #00ffee (13,41), kopya açık #f3b8ff (zemine 1,33), kopya koyu #9ffff6 (14,68) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 04:34:35 | 0 | 725 | geçti | GEÇTİ; masa yabancı şema 0, telefon taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 04:46:40 | 0 | 428 | geçti | GEÇTİ (**ilk gerçek koşu**, vurgu tonları `VURGU_TON`'dan): seçim 6 / 6 (adım 17 parça 1 / 1, panel 1 / 1), şema tıklaması geçti, ağsız dış istek 0, konsol 0 |
| 8 | `F9b-dogrula.py` | 04:53:49 | 0 | 5 | GEÇER | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 04:53:53 | 0 | 0 | 17 dosya aynı | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 10 | `regresyon.py --yazma` | 04:53:54 | 0 | 0 | aynı | GEÇER, 10 değerin hepsi aynı |

Zincir 2–10 `.durum`: "BITTI cikis 0 sure 2617 enaz 2.78". **Bellek:** en düşük boş fiziksel bellek üretimde 2,81 GB (168 ölçüm),
zincirde 2,78 GB (173 ölçüm); bekçi tetiklenmedi.

### Sapmalar ve nedenleri (hiçbiri düzeltilmedi: metin / yerleşim, kod hatası değil)

- **S1, basılı K1'in ilk sayfası taşıyor; `rehber_uret.py` çıkış 2.** `yazdir.html` K1'in ilk sayfasına (başlık, kare, lejant, `is_`)
  hiç blok koymadan da sığdıramıyor (`tasma` "17"); yazı 8,5 pt alt sınırına inmiş. Neden: K1 `is_` 5414 → **10029** karakter
  (HEAD verisi ↔ yeni veri). **Sonuç PDF'te ölçüldü:** sayfa 19 madde 5'in ortasında ("… K1'de soketin 86 / 85 kuyruklarının")
  kesiliyor; `is_`'in son **3645 karakteri** (≈ % 36) PDF'in hiçbir sayfasında yok (40 karakterlik 19 örnek parçadan 1'i PDF metninde,
  o da genel bir ifade): madde 5'in ikinci yarısı (A06'nın + ucu, PC817 #1 girişi), **madde 6** (N01, N02, B01, B02, Q01–Q03, X01),
  **madde 7** (P03, G17, G20, U06) ve **madde 8** (köprü listesi). Ekranda (panel) metin tam. Devam sayfaları (20, 21) parça /
  bağlantı / kontrol listesini taşıyor. Çözüm yerleşim ya da metin kararı ister (ör. `is_`'i madde başına blok yapmak ya da K1 metnini
  kısaltmak): ölçüt / kaynak değişikliği, bu pakette yapılmadı.
- **S2, PDF 77 → 79 sayfa:** `sayfa_esleme` farkı B6a (14) 1 → 2 sayfa (`is_` 99 → 1900 karakter) ve K1 (17) 2 → 3 sayfa. Öbür adımlar
  aynı sayfa sayısında (kaymalar bu ikisinden).
- **Bilgi:** `--bozma-denemesi --veri` 44 / 44 (F10h § 15.3'te 35; kaynak bozmaları 27 → 36, D1.7).

### Kare bakışı (iki tema)

Rehberin kendisinden 1400 × 900, kendi başsız Chrome'umla (F10a `Cdp`, profil geçici klasörümde, iş bitince kapandı; depoya yazmaz),
04:55–04:57: adımlar 12 (B5a), 14 (B6a), 17 (K1), 29 (E3a), 31 (E4), 32 (K2), 33 (F1), 33.7, 33.9, 33.10, 34 (F2), 34.8; her biri iki
temada genel kare + panel sayfa sayfa (kaydırarak) + panel metni (DOM); seçim: K1 p1180 / p1189 / p1190, K2 p1184 / şema 0 (H02) /
şema 3 (AU3); kopya: 12, 14, 4 adımlarında çok kopyalı burca 3B tıklama (gerçek ve sınıf renk kipi). PDF sayfaları PyMuPDF ile görüntüye
çevrildi. Çekilen 225 kareden **42 ekran karesine ve 5 PDF sayfasına baktım** (11'i koyu tema; panel sayfaları dörder yan yana,
HDMI ve kopya kareleri büyütülmüş kesitle). Bakmadıklarım: K1 p1189 / p1190 ve K2 şema 3 tıklama kareleri, panel sayfalarının çoğu
koyu tema, 33.7 / 33.9 / 33.10 panel sayfaları, B5a panelinin alt sayfaları, K1 panelinin son ≈ 1370 px'i (14 sayfa sınırı; parça /
kontrol listesi, metni DOM'dan okundu), 14 adımının kopya karesi.

| Kare | Tema | Gördüğüm |
| --- | --- | --- |
| Panel metni (12 konum, DOM) | açık, koyu | Ekranda çözülmemiş yer tutucu **0** (`{…}`, `⟦`, `⟧` yok; veride de 0); panel dışına taşan / kesilen öğe 0 |
| K1 (17) panel, 8 sayfa | açık (4 + 4), koyu (4) | G07 + 100 kΩ (kılıf, makaron, sıkma + lehim sırası), anahtarlı bara yerleşimi ("saplama 1 G12 / G14 / G15, 2 G13 / G16, 3 G09 / G11, 4 G22"), K2 kontağı ("COM ile NC arası öter, COM ile NO arası ötmez"), madde 5–8 tam okunuyor, kesik yok. Zor: madde 1 ve 3 tek paragraf, kırk satır civarı; kontrol maddeleri de uzun paragraf |
| B6a (14) panel | açık | X01, I01, I02, P01, P02 maddeleri ve kontrolleri (PCA9685 V+ boş, ölçü ucu kanal başlığının V+ pininde) okunuyor |
| B5a (12) panel üstü | açık | Dağıtım kartı C, kondansatör yönü, SV3 OUT+ → V+, OUT− → GND okunuyor |
| E3a (29) panel | açık | Üç TVS'in yönü ("katot (bantlı uç) +5 V'a", P6KE18A +12 V), "sonu yalnız A / sonu CA" okunuyor |
| F1 (33) kontrol | açık | Ölçüm maddeleri (G07: DC V, 1,95–2,20 V, aralık dışında ana anahtarı kapat, aküyü ayır) okunuyor; madde çok uzun tek paragraf (zor) |
| F2.8 (34.8) | açık | "AU3 … kutbu L+ → +, L− → −" ve kontrol maddesi okunuyor |
| K2 / AU3 basılı (sayfa 41) | — | Madde 5 AU3 "+ damarını L+ ucuna, − damarını L− ucuna" tam; sayfa sığıyor |
| Seçim K1 p1180 | açık, koyu | Açık temada fuşya #e014ff zeminden, kırmızıdan, turuncudan, morundan ve acil stop yeşilinden net ayrılıyor; koyu temada camgöbeği #00ffee yeşilden ve kırmızıdan net ayrı |
| Seçim K2 p1184 | açık, koyu | Açık temada fuşya hardal sarıdan net, direkteki mor sinyal telinden ayrılıyor (fuşya açık, mor koyu; ince çizgide ikisi aynı renk ailesi); koyu temada camgöbeği sarıdan net ayrı (F10h § 14.4'teki yeşil ↔ sarı sorunu yok) |
| Seçim K2 şema 0 (H02) | açık, koyu | Seçili HDMI açıkta fuşya, koyuda camgöbeği. Koyu temada seçilmemiş HDMI tonu (#5ba7b8, soluk camgöbeği) ile seçim camgöbeği yan yana konunca ayrılıyor; tek başına bakınca aynı renk ailesi (zor) |
| HDMI açık tema (K2, büyütülmüş) | açık | #193cff canlı mavi, ince çizgide siyahtan ve analog ses gri-mavisinden (#4c7078) net ayrı. Siyah kablo aynı karede HDMI'nin yanında değil (siyah toprak tabanda); ton olarak ayrımı bariz |
| Kopya (12, 4) | açık, koyu; gerçek ve sınıf | Seçilen burç ve 7 / 19 kopyası **aynı tonda görünüyor**: burçlar plakanın arkasında, x-ray silueti (`VURGU.xray`, ana ton, %30) hepsinin üstüne çiziliyor; **kopya tonu #f3b8ff karede seçilemedi**, ana ↔ kopya ayrılmıyor. Sınıf kipinde açık temada fuşya burçlar mor lazer plakadan (#8e44ad) ayrılıyor ama aynı renk ailesi (zor); koyu temada camgöbeği net |
| E4 (31) genel | açık, koyu | Kafa kapalı; lejant "Hazır kablo: USB / 5 V (mavi) / Hazır kablo: HDMI" sayıyor, karede hiçbir kablo görünmüyor (açık iş; değişmedi, yalnız gördüğüm) |
| Basılı K1 (sayfa 19) | — | "Karede:" satırı **5 sınıf** (12 V kırmızı, toprak, anahtarlı bara / motor, acil stop, sinyal); metin madde 5'te kesik (S1) |
| Basılı K2 (sayfa 41) | — | "Karede:" satırı **6 sınıf** (HDMI, USB, analog ses, 12 V, servo 6 V, sinyal). Başka adımın lejant satırı HEAD PDF'iyle aynı (17 ve 32 dışında fark 0) |
| Basılı B6a (15), E3a (33), F1 (43) | — | Sığıyor, okunuyor |

**Zor okunan / yanıltıcı kareler: 7** — basılı K1 (talimatın % 36'sı yok, S1); K1 panel madde 1 / 3 ve F1 kontrol maddeleri tek uzun
paragraf; kopya vurgusu (ana ↔ kopya ayrılmıyor, kopya tonu görünmüyor); açık temada fuşya ↔ mor sinyal ve fuşya ↔ mor lazer aynı renk
ailesi (ayrılıyor, pay ince); koyu temada seçili ↔ seçilmemiş HDMI aynı renk ailesi; E4 genel (lejant görünmeyen kabloları sayıyor).

**Renk yargısı:** seçim vurgusu iki temada zeminden ve komşu kablo sınıflarından ayrılıyor; açık temada lazer / mor ile ayrım en zayıf
yer (ölçü ΔE00 16,6). Açık HDMI #193cff siyahtan bariz ayrı.

### Üretimin ve zincirin yazdığı dosyalar

`rehber/veri/rehber-veri.json` / `.js` (`robot.glb` / `robot-glb.js` içerikçe aynı), `rehber/goruntu/*.png` (değişen 25),
`planlama/rehber/goruntu/*.png` (değişen 39), `planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf`,
`planlama/d158/F10{a,d,e,f}-dogrula.json`. Paket dışı eski değişikler (`tasarim/freecad/kabuk/gorsel/*.png` 13,
`tasarim/freecad/montaj/yerlesim-kontrol.json`) **yeniden yazılmadı** (SHA-1 önce / sonra aynı). `git status` 34 → 107 satır (+73: 64
kare, 2 veri, PDF, `kontrol.json`, 4 doğrulama JSON'u ve üçüncü bakışın `F10i-kontrol-3.md`'si).

### Doğrulanamayanlar

- PDF'in görünüşü PyMuPDF görüntüsünden (Chrome'un yazdırdığı dosya); kâğıda basılmadı.
- Kopya tonu, öndeki (örtülmemiş) bir kopyada denenmedi: baktığım üç örnekte kopyalar plakanın arkasında.
- Renk yargıları kare üstünde gözle; piksel ölçümü yalnız F10e / F10f'in kendi ölçütleri.
- Kontrollerin geçici kopyadaki bozmaları koşulmadı (brief istemedi).

## Basılı sayfa düzeltmesi ve yeniden üretim (15.11, ajan Y)

15.11.2026 05:05–06:48 (saat okundu). Dal `lale-duzeltme`, HEAD `1328b60`. **Talimat metnine dokunulmadı** (`rehber_metin.py`,
`rehber_deger.py`, onay kaydı, `kablolar.json` SHA-256 önce / sonra aynı); düzeltme yalnız basılı sayfanın yerleşiminde.

### Tanı

`yazdir.html` adımı bloklara bölüp sığmayanları sondan "devam" sayfasına taşıyordu; ama iş metni (`is_`) blok değildi: ilk sayfaya
başlık, kare, lejant ve KPI ile **tek parça** basılıyordu. Sayfa kutusu `.ic` sabit yükseklikte ve `overflow:hidden`; `sigdir()` kareyi
84 → 46 mm, yazıyı 9,6 → 8,5 pt küçültüp yine sığdıramayınca sayfayı `data-tasma`'ya yazıyor, taşan kısım kutunun dışında kalıp
**basılmıyordu**. K1'in `is_`'i 10029 karakter; ilk sayfa blok koyulmadan da taşıyordu. Metin DOM'da tam olduğu için `rehber_denetim`
(zorunlu uyarı / ASCII, tarayıcının DOM metnine bakar) eksikliği göremezdi; yalnız taşma sayacı yakaladı. Ölçüm (aşağıdaki tamlık
denetimiyle, 05:03 PDF'i): K1 `is_`'inin işaretsiz metninde son **3644 karakter** (boşluksuz 3066) PDF'te yok; kesik sayfa 19'da
"… K1'de soketin 86 / 85 kuyruklarının | üstünde lehim + makaron …": üretim ajanının ≈ 3645'i doğrulandı (fark bir karakter: `**`
işaretleri düşülerek sayıldı). Öbür 49 adımda eksik 0.

### Düzeltme (genel, K1'e özel değil)

`rehber/yazdir.html`:

- `bloklar()`: eski `var b = [];` → yeni `var b = isBloklari(st);` — `is_` satır (paragraf / madde) başına `{tur: "is"}` blok, öbür
  blokların önünde. Sondan taşıma döngüsü aynı kaldı; iş metni blokları en son taşınır.
- `sayfa()`: eski `h.push("<div class='is'>" + md(st.is_) + "</div>")` → yeni `h.push(isMetin)`; `isMetin` = sayfadaki iş blokları
  `"\n"` ile birleşip tek `md()`'den geçer (bütün paragraflar sığınca HTML eskisiyle bayt bayt aynı). Devam sayfası iş metniyle
  başlıyorsa başlığın altında "← K1 iş metni: önceki sayfa ile devam" (paragraf ortasından sürüyorsa "… önceki sayfa sonunda yarım
  kalan yer burada sürüyor"); iş metni sonraki sayfada sürüyorsa sayfanın sonunda "İş metni sürüyor / İş metni yarım kaldı: devamı
  sonraki sayfa (K1, adım 17) →". Yeni stil `.isdevam` (soluk, eğik, ≥ 8,1 pt).
- Yerleşim döngüsü: sığan en çok blok seçildikten sonra sıradaki blok iş metni paragrafıysa `bol()` onu **sözcük sınırında** böler
  (ikili arama; sığan en uzun baş bu sayfada, kalanı sonraki sayfada; `**` / `` ` `` çiftinin içinden bölmez; iki yanda en az 6
  sözcük). Tek paragraf boş bir devam sayfasına sığmasa bile aynı yolla sayfalara akar. Yalnız bölünen boşluk düşer, karakter düşmez.
  Bölünemeyen blok (tablo, kontrol listesi, alt adım kartı) eskisi gibi `data-tasma`'ya yazılır.

`tasarim/freecad/rehber/rehber_uret.py`: yeni `pdf_tamlik()` (+ `_tam_norm`, `_tam_md`, `_tam_eslesen`, `TAM_EN_AZ = 20`) ve
`yazdir()`'da eski kabul `… and not d["kucuk_yazi"] and kucuk_ok)` → yeni `… and kucuk_ok and d["tamlik"]["gecti"])`; özet satırı
"yazdir tamlik: …" ve eksik başına "EKSIK adim … sayfa … sonunda kesik: …" satırı; `kontrol.json` `yazdir.tamlik`. Eşikler (taşma,
8 / 8,1 / 8,5 pt, kare 46 mm) değişmedi.

**Tamlık denetimi:** her adımın `is_`'i, alt adım `is_`'leri, notları ve kontrol maddeleri o adımın PDF sayfalarında (DOM'un
`sayfa_esleme`'si) aranır; PyMuPDF metni ve kaynak NFKC, boşluk / satır sonu / yumuşak tire ayıklanır, satır sonu tiresi silinmiş ikinci
okuma da denenir, `md()` işaretleri düşülür. `is_` sayfa sayfa en uzun bitişik parça olarak eşlenir (atlama yok; 20 karakterden kısa
rastlantısal eşleşme sayılmaz); maddeler adımın sayfalarında bütün aranır. Önceden böyle bir denetim yoktu (taşma sayacı dışında).

### Bozma denemeleri (geçici kopya, `<base>` depodaki `rehber/`'e; PDF geçici klasöre)

| Deneme | Beklenen | Sonuç |
| --- | --- | --- |
| Temiz `yazdir.html` | geçer | geçti, eksik 0 (yanlış alarm yok) |
| Eski `yazdir.html` (düzeltme öncesi) | kalır | kaldı: taşan 17, K1 `is_` 3066 (boşluksuz) eksik, kesik "… kuyruklarının \| üstünde lehim …" |
| Devam sayfasında iş metninin son paragrafı gizli | kalır | kaldı: K1 794 eksik, "8. K1'de enerji verilmez …" |
| Kısaltılmış sayfa (yalnız baskıda `.ic` 200 mm) | kalır | kaldı: `is_` 5388, madde 68 eksik (**taşma sayacı 0**: yalnız tamlık yakalar) |
| Bir kontrol maddesi gizli (baskıda) | kalır | kaldı: madde 18 eksik |
| Alt adım iş metni görünmez (baskıda) | kalır | kaldı: madde 67 eksik |
| Bir not maddesi gizli (baskıda) | kalır | kaldı: madde 8 eksik |

7 / 7. Ek sınama (genel çözüm): adım 9'un `is_`'ine tarayıcıda 71 bin karakterlik **tek paragraf** eklendi (yalnız geçici kopyada):
10 sayfaya aktı (sayfa başına ≈ 7100 karakter), taşan yok, eksik 0.

### Yeniden üretim kararı

FreeCAD aşaması **koşmadı**: girdileri (CAD kaynakları, `rehber_veri.py`, `rehber_metin.py`) değişmedi; çıktısı `robot.glb` /
`robot-glb.js` SHA-256 önce / sonra aynı. Yalnız PDF aşamasını koşturan bir kip yok (`--ek-yok` PDF'i de atlıyor; `kontrol.json`'u
elle yazmak olmaz), bu yüzden `rehber_uret.py --veri-yok` (FreeCAD dışında bütün aşamalar) ve ardından **zincirin tamamı baştan**
koştu. Kilit gerekmedi, dokunulmadı ("boş"). Sarmalayıcı + bekçi (15 s, 1,2 GB) F10g § 5 yöntemiyle, geçici klasörde.

**SHA-256 (332 dosya, önce ↔ üretim ↔ zincir sonu):** `rehber/goruntu` 121 / 121 aynı (baskı kareleri); `planlama/rehber/goruntu`
125 / 128 aynı; `robot.glb`, `robot-glb.js`, `planlama/adim3/*`, `rehber/index.html`, `app.js`, `stil.css` aynı; paket dışı
`tasarim/freecad/kabuk/gorsel/*.png` (13) ve `yerlesim-kontrol.json` yeniden yazılmadı. Değişen: `yazdir.html`, `rehber_uret.py`
(kaynak), PDF, `kontrol.json`, `rehber-veri.json` / `.js`, kontrol kareleri `adim-31-01`, `adim-36-02`, `adim-41-06` (üretim) ve
`F10{a,d,e,f}-dogrula.json` (zincir).

- **Kontrol kareleri** (ekran, `index.html`; ekran kodu değişmedi): 31-01 ve 41-06'nın öncekisi HEAD'dekiyle aynıydı, piksel farkı
  40 / 27 piksel, en çok 2 / 5 gri düzeyi (yazılımsal çizimin gürültüsü). 36-02'nin öncekinin kopyası yok (yalnız SHA'sı).
- **Veri:** `rehber-veri.json` / `.js` baytça farklı. `--veri-yok` geçişi (`rehber_gorunum.isle` + `rehber_kol_kablo.isle`) verinin
  geçici kopyasında bir kez daha koşturuldu: içerik ve anahtar sırası aynı, yalnız iki geçen süre alanı (`ev_kaynak.sure_s`,
  `sure_baglanti_s`) farklı. Önceki dosyada bu iki alana 0–300 s aralığında her değer denendi, SHA tutmadı: 05:03 dosyasıyla fark
  süre alanlarından büyük, ama kopyası saklanmadığı için **ne olduğu ölçülemedi**. Kareler, PDF'in öbür adımları ve zincirin bütün
  sayıları aynı çıktı.

### PDF

**79 → 80 sayfa** (adım 50 + devam 30), en küçük yazı DOM / PDF 8,1 pt, 16163 kB, taşan 0, eşleme tutarlı, `yazdir.gecti` true.
Tamlık: 50 adım, `is_` 31525 karakter (boşluksuz), **eksik 0**; madde 260 (not, kontrol, alt adım `is_`), eksik 0. K1 (17) 3 → 4
sayfa: 19 (kare, lejant, madde 1–5'in başı; "yarım kaldı" işareti), 20 ("önceki sayfa sonunda yarım kalan yer burada sürüyor", madde 5
sonu–8, parçalar, bağlantı), 21 (kontrol listesi), 22 (kablo kancası, erişim). Eski ↔ yeni PDF adım adım (sözcükler ve konumları 0,1
pt'ye yuvarlı, görüntü dikdörtgenleri): **düzeni değişen tek adım 17**; 18–49'un sayfa numarası bir kaydı, içerik ve konum aynı
(24 ve 36'da yalnız yazı kenarı piksel farkı, sözcük konumları aynı); 0–16 aynı.

### Zincir

| Sıra | Komut | Başlangıç | Çıkış | Süre (s) | Ölçülen |
| --- | --- | --- | --- | --- | --- |
| 1 | `rehber_uret.py --veri-yok` | 05:21:34 | 0 | 2361 | 50 / 50 adım, konsol 0; alt adım 71 / 71; PDF yukarıda; denetim ASCII 0, elektrik 0, zorunlu eksik 0 / 98, yasak 0; sıra / uçuş / giriş geçti; kablo eşleme GEÇTİ; "ek kontrol sorunlu: -" |
| 2 | `rehber_kablo.py --veri …` | 06:01:15 | 0 | 0 | SONUÇ GEÇER, geometri hata 0 / bilgi 4 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 06:01:15 | 0 | 2 | 44 / 44 yakalandı |
| 3 | `rehber_denetim.py` (veri) | 06:01:18 | 0 | 0 | ASCII 0, elektrik 0, zorunlu eksik 0 / 98, yasak 0, parça 1192, şema 49 |
| 4 | `F10f-dogrula.py` | 06:01:18 | 0 | 602 | GEÇTİ |
| 5 | `F10e-dogrula.py --goruntu-yok` | 06:11:21 | 0 | 938 | GEÇTİ; renk_demo KALDI (karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 06:26:59 | 0 | 724 | GEÇTİ; masa yabancı şema 0, telefon taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 06:39:03 | 0 | 431 | GEÇTİ; yazdırma kareleri 50 / 50, PDF görüntü 121, boş sayfa yok; seçim 6 / 6 |
| 8 | `F9b-dogrula.py` | 06:46:13 | 0 | 5 | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 06:46:18 | 0 | 0 | 17 dosya kayıtla aynı |
| 10 | `regresyon.py --yazma` | 06:46:18 | 0 | 0 | GEÇER, 10 değer aynı |

Ön sınama: `rehber_denetim.py --kaynak` çıkış 0 (ASCII'ye giren arayüz dizgesi 102; yeni basılı işaret dizgeleri ASCII kalıntısız).
Koşmayan zincir adımı yok. **Bellek:** en düşük boş fiziksel bellek üretimde 3,10 GB (157 ölçüm), zincirde 2,36 GB (179 ölçüm; veri
geçişinin kopyada yeniden koşturulduğu dakika); bekçi tetiklenmedi.

### Baktığım sayfalar (PDF'ten PyMuPDF ile 110 dpi)

| Sayfa | Adım | Gördüğüm |
| --- | --- | --- |
| 19 | K1 (17) | Başlık, rozetler, kare, "Karede:" satırı 5 sınıf yerinde; madde 1–4 tam, madde 5 "… ön şarj kartındaki K2" ile biter; altında "İş metni yarım kaldı: devamı sonraki sayfa (K1, adım 17) →"; kesik / üst üste binme yok |
| 20 | K1 | "← K1 iş metni: önceki sayfa sonunda yarım kalan yer burada sürüyor", sonra "bobini (+; A04) …" (sıra doğru, sözcük bölünmemiş); madde 5 sonu, alt kat paragrafı, madde 6, 7, 8 tam; parçalar / bağlantı sütunları |
| 21 | K1 | Kontrol listesi iki sütun, maddeler bütün (kontrol kutuları yerinde) |
| 22 | K1 | Kablo kancası (kablo yolu 1–4, 9–11; veride 5–8 yok) ve erişim notu |
| 15, 16 | B6a (14) | Eskisiyle aynı: iş metni madde 1–4, parça tablosu, kontrol; devam sayfasında kablo kancası ve erişim |
| 7, 17, 73 | B2a (6), B6 (15), H0d (45) | Rastgele seçim (`random.Random(158)`): sığıyor, okunuyor, alt adım kartları (45.1 / 45.2) yerinde |
| 29 | E1 (24) | Piksel farkı çıkan sayfa: içerik ve yerleşim aynı |

### Açık kalanlar

- `README.md` "(77 sayfa)" yazıyor; PDF artık 80 sayfa (05:03'te 79'du). `F9d-tarama.py` bu uyuşmazlığı sayar; README bu paketin
  dokunabileceği dosyalardan değil.
- Bölünemeyen bloklar (kontrol listesi, tablo, alt adım kartı) bir sayfadan uzun olursa yine taşar; artık sessiz değil: taşma sayacı
  ve tamlık denetimi ikisi de üretimi düşürür.
- Kâğıda basılmadı; görünüş PyMuPDF görüntüsünden.
