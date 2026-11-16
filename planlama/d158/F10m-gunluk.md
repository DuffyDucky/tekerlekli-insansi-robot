# F10m · P10.7b2e günlüğü: K52 a (göğüs regülatörü güç panelinde), bara tutucusu (K64), `is_ana` veri sınaması

Açılış 16.11.2026 05:13 (uygulama ajanı; FreeCAD'siz). Taban: `lale-duzeltme` = uzak = `84f1a4a` (P10.9a). Commit yok, üretim yok.
Sırada: kare düzeltmeleri (§ 8, sonra eklenecek) → bağımsız kontrol → üretim → commit / push.

## 1. Kapsam ve verilen karar

- **K52 → seçenek a** (orkestratör kararı (Echo), 16.11.2026): LM2577 + LM2596 kartı güç panelinde, rehber B5a'da takılır. Maliyet 0 TL.
- **Model değişmez** (`arayuz.py`, `taban_parcalar.py` ve öbür CAD dosyalarına dokunulmadı). Gerekçe: model değişikliği 9 bölümlük
  çakışma taramasını eskitir. Kart zarfı K51 ve K53 ile birlikte sonraki tam taramalı CAD paketinde girer.
- **K50 bu paketin dışında** (şarj girişi XT60E-M / F + şarj kablosu, Ahmet'in cevabı bekleniyor). K50'ye bağlı kayıt ve metin aynı kaldı.
- Ek işler: K58 başlığına "— KAPANDI"; bara tutucusu (F10l § 10.7 N3); veri modu `is_ana` hatası için kalıcı bozma sınaması (F10l § 10.3).

## 2. Hangi kablo kaydı hangi karara bağlı

| Kablo | Bağlı olduğu karar | Bu paketten önce | Sonra |
|---|---|---|---|
| G20 (F6 → regülatör girişi, 18 AWG) | K52 | `eksik` dolu → "karara bağlı" | `eksik` boş → "kablajda teyit edilecek" (iki ucu da güç panelinde; boy panelde ölçülür) |
| G21 (regülatör çıkışı → ekran jakı) | — (`eksik` zaten boş) | "kablajda teyit edilecek" | değişmedi |
| G06 (şarj kolu) | K50 (yalnız not ve rehber metni: XT60E-M) | "kablajda teyit edilecek" | değişmedi |

Kablo durumu: kesin 20 / teyit 53 → **54** / karara bağlı 1 → **0** (`kablolar.md` yeniden üretildi; taban (K1) demeti 17 / 0 / 17 / 0).

## 3. Değişen dosyalar ve satırlar (`git diff -U0` hunk başları, yeni dosyada)

| Dosya | Satırlar | Ne |
|---|---|---|
| `planlama/adim3/kablolar.json` | 3–4, 484 (silme), 3107–3147, 8727–8733 | tarih / kaynak; `orkestratore` listesinden K52 çıktı; G20 `eksik` [], `teyit`e K52 a satırı, `durum`, `boy_tahmin.vekil` notu (üst sınır korundu), `tarihce`; `kararlar`a K52 girdisi |
| `planlama/adim3/kablolar_uret.py` | 366 | "Orkestratör kararları (14.11, 15.11, 16.11)" başlığı |
| `planlama/adim3/kablolar.md` | üretilmiş | `kablolar_uret.py` çıktısı (elle düzenlenmedi) |
| `planlama/adim3/elektrik.md` | 17, 519 (düzyazı); 558 (üretilmiş blok, G20 satırı) | regülatörün yeri güç paneli, B5a, K52 a; kart ölçüsü ve panel üstündeki yeri modelde yok |
| `planlama/maliyet.json` | — | değişmedi: `:190` regülatör zaten listede; `:122-123` notları K11 düzeltmesiyle zaten güncel; gerçek değişiklik yok |
| `tasarim/freecad/rehber/rehber_metin.py` | 234–240, 242–243, 257–262, 422–424, 428–429, 459–460, 922–923, 953, 1238–1239, 1966–1967 | B5a is_ / kontrol / not_; K1 madde 4 ve 7; K2 madde 7 ve not_; F3 not_; şema 12 V |
| `tasarim/freecad/rehber/rehber_denetim.py` | 145–150, 319–324, 435–437, 478–479, 846, 1034–1036, 1048, 1741–1745, 2039–2105, 2288, 2407–2408 | ASCII izin listesi (9 kelime); ZORUNLU / SIRA / CUMLE; açık karar `K60\|K61\|K64`, kapalı karar `K(1\|10\|11\|14\|52)(?! a)`; M21 / M21b / M21c; `_veri_benzetimi`, `veri_is_ana_bozma_denemesi`; D6 bozmasının G20 metni |
| `tasarim/freecad/rehber/rehber_kablo.py` | 872–873, 887–889 | `SEMA_MODELSIZ` ve `SEMA_GEO_ISTISNA` ("12 V", "G20 a") gerekçesi K52 a'ya göre |
| `tasarim/freecad/rehber/rehber_kritik_onay.json` | yenilendi | `--kritik-onay-yenile` (§ 6) |
| `planlama/d158/F10l-birlesim.py` | 15, 109–156 | varsayılan taban `84f1a4a`; beklenen farklar tabana göre sözlükte (b2d listeleri kayıt olarak durur), b2e listeleri |
| `planlama/d158/karar-kuyrugu.md` | 67, 79–82, 960, 985–991, 1154, 1257–1277 | K52 satırı / başlığı / kapanış notu; K58 başlığı; K64 satırı ve gövdesi; sayaç |
| `planlama/dongu-158.md` | 43, 165, 185–190 | kilit satırı; P10.7 satırına b2e; § 5 günlük girdisi |

## 4. K52 için yazılanlar

**Kuyruk (K52 durumu):** "kapandı (16.11.2026; orkestratör kararı (Echo), seçenek a). Regülatör kartı (LM2577 + LM2596) güç panelinde;
rehber B5a'da, tezgâhta ekran bağlı değilken 12 V'a ayarlandıktan sonra panele takılır (T7 B). Maliyet 0 TL … Model bu kararla
değişmez: model değişikliği 9 bölümlük çakışma taramasını eskitir; kart zarfı K51 ve K53 ile birlikte sonraki tam taramalı CAD
paketinde girer. O zamana dek kart ölçüsü, panel üstündeki yeri ve bağlantı elemanı kayıtta yok."

**Rehber B5a, is_ (yeni paragraf):** "Göğüs ekranı regülatörü (LM2577 + LM2596; K52 a): ekrana ve panele bağlamadan, tezgâhta çıkışını
multimetreyle 12 V'a ayarla ve trimpotun konumunu boya noktasıyla işaretle (`planlama/d158/testler/T7-gogus-ekrani-12v.md` B). Sonra
kartı güç paneline tak; giriş (IN+ / IN−) ve çıkış (OUT+ / OUT−) klemensleri erişilebilir kalsın. Kart, ölçüsü ve panel üstündeki yeri
modelde yok; yeri ve bağlantı elemanı kaynakta yok, doğrulanmadı. Girişi (G20) K1'de, çıkışı (G21) K2'de bağlanır."

**B5a kontrol (2. madde):** "Göğüs ekranı regülatörü (LM2577 + LM2596) panelde; panele takılmadan önce tezgâhta, ekran bağlı değilken
çıkışı 12 V'a ayarlandı, trimpotu boya noktasıyla işaretli (T7 B)".

**B5a not_:** "Göğüs ekranı regülatörü (K52 a) modelde yok: karede görünmez, model sonraki tam taramalı CAD paketinde".

**K1 madde 4 (alt adım 17.7):** G20 "…: kutudan, B5a'da güç paneline takılan göğüs ekranı regülatörünün girişine (K52 a); G20'nin iki ucu
da panelde, göğüs regülatörünün direğe çıkan çıkışı K2'de." + "G20'nin regülatör ucunu regülatörün giriş klemensine bağla
({kutup.G20}; kart üstü IN+ / IN− yazısına göre)." (Eski: "uç bantlı, K2'de direğe çıkar" ve "Göğüs regülatörünün panel yeri karar
bekliyor (K52) …" kalktı.) **K1 madde 7:** "Kafa 12 V'un (G17) taban ucu ve panel içinde kalan göğüs ekranı dalı (G20) madde 4'te bağlandı".

**K2 madde 7:** "Regülatör B5a'da güç paneline takıldı (K52 a): panele takılmadan önce, ekrana bağlanmadan 12 V'a ayarlandı (kontrol);
girişi (G20) K1'de bağlandı." **K2 not_:** "LM2577 + LM2596 kartı güç panelinde (B5a, K52 a); kart ve panel üstündeki yeri modelde yok".
**F3 not_:** "Regülatör kartı güç panelinde (B5a, K52 a); kart ve panel üstündeki yeri modelde yok: bu adımda çıkış klemenslerine erişim
ölçülmedi, doğrulanmadı". **Şema 12 V:** "… (F6 {a.F6} → LM2577 + LM2596; regülatör güç panelinde, B5a, K52 a; modelde yok) → …".

Kaynak: ayar sırası `planlama/d158/testler/T7-gogus-ekrani-12v.md` B (regülatör tezgâhta, ekran bağlı değil, trimpot boya noktası);
kutup `kablolar.json` G20 `kutup`; panel `taban_parcalar.py:219` (5 mm huş kontrplak 270 × 274).

## 5. Bara tutucusu: sonuç ve dayanak

- **Kayıtta olan:** ne olduğu: basılmış yalıtkan tutucu, iki baranın M5 saplamalarını taşır (`planlama/adim3/kablolar.md` O-3 r;
  `planlama/maliyet.json:200` bara saplaması notu "Basılmış yalıtkan tutucu, CAD'i P10.7b"; `kablolar.json` bara-pabuc "Tutucunun CAD'i
  P10.7b iş maddesi"; `planlama/adim3/kablolama-on-kararlar.md:434`). Yaklaşık yeri: güç paneli (B5a kablo notu).
- **Kayıtta olmayan:** ölçüsü, CAD'i, baskı listesi satırı, panel üstündeki yeri, panele bağlantı elemanı.
- **Sonuç:** talimat yazılmadı (uydurmamak için). B5a not_'una "panelde yeri ve bağlantı elemanı karar bekliyor (K64)" yazıldı; kuyruğa
  **K64** açıldı. Seçenekler: a) basılmış yalıtkan tutucu, K51 / K52 / K53 ile aynı CAD paketinde (satın alma yok; gram doğrulanmadı);
  b) saplamalar doğrudan kontrplak panele (model değişikliği, ezilme / alt yüz erişim riski); c) hazır pirinç nötr barası (satın alma,
  fiyat doğrulanmadı, Ahmet onayı). Öneri a. Teknik seçim orkestratörün; c'de satın alma Ahmet'in.

## 6. Onay kaydı

`rehber_denetim.py --kritik-onay-yenile`: **25 fark** (yer başına). Girdi düzeyinde: kablo 165 → 165 (1 değişti: `SEMA_GEO_ISTISNA`
12 V / G20 a gerekçesi), liste 206 → 210 (3 silindi: K1 / K2 "karar bekliyor (K52)", şema 12 V ZORUNLU_CUMLE; 7 eklendi: B5a × 2, K1 × 2,
K2 × 1 ZORUNLU, şema 12 V ZORUNLU_CUMLE, B5a ZORUNLU_SIRA), metin 1064 → 1071 (8 silindi, 15 eklendi; § 4'teki cümleler).
**Kritik değer farkı 0:** değişen cümlelerde yer tutucular aynı değerleri çözer ({a.F6} 3 A, {awg.G20} / {awg.G21} 18 AWG); tek yeni
yer tutucu {kutup.G20} kayıttaki değişmemiş G20 kutbunu ("F6 çıkışı → IN+, IN− → GND") okur. Devre değeri ve sipariş farkı yok.
Önceki kaydın kopyası (ajan geçici alanı) `b2e/onay-once.json`.

## 7. Sınamalar (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Sınama | Önce (84f1a4a ağacı) | Sonra |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | 0 (güncel) |
| `kablolar_denetim.py` | GEÇER | GEÇER |
| `kablolar_denetim.py --bozma-denemesi` | 172 | 172 |
| `rehber_denetim.py --kaynak` | 0; metin 615; onay kablo 165 / liste 206 / metin 1064 | 0; metin 618; onay kablo 165 / liste 210 / metin 1071; tamlık 172, eksik 0; D1–D7 hata 0 |
| `rehber_denetim.py --bozma-denemesi` | 289 / 289 | **296 / 296** (M21 değişti; + M21b, M21c, veri `is_ana` 5) |
| `rehber_denetim.py` (veri, eski üretim) | 0; zorunlu eksik 0 / 115 | **1, beklenen**: zorunlu eksik 5 / 118 (yeni 5 ZORUNLU eski veride yok) + elektrik 5 ("karar bekliyor (K52)" eski veride; K52 kapandı). Üretimle kalkar |
| `rehber_kablo.py` | GEÇER | GEÇER (onay kablo bölümü tutuyor) |
| `rehber_kablo.py --bozma-denemesi` | 86 / 86 | 86 / 86 |
| `rehber_kablo.py --veri` | GEÇER | GEÇER |
| `rehber_kablo.py --bozma-denemesi --veri` | 95 / 95 | 95 / 95 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ (38) | GEÇTİ (38) |
| `F10l-birlesim.py` | GEÇER (taban 1c4e882) | GEÇER (taban 84f1a4a; eklenen 15 / 15, silinen 8 / 8; gönderme 16, çözülemeyen 0) |
| `node --check rehber/app.js` | 0 | 0 |
| `F9c-dogrula.py` (depodaki bayat `sonuc-rapor.html`) | koşulmadı | 1 (hata 101; sayfa 09.11'den bayat; kuyruk başlık sayımı tutarlı: açık 49, kapanan başlık 15) |
| `F9c-uret.py --cikti <geçici>` | koşulmadı | 1: `KeyError: 'K64'` (`GRUP` sözlüğünde K64 yok; § 9) |

**Koşulmayan:** FreeCAD, `rehber_uret.py` (tam üretim), zincir 2–10, PDF, kare görüntüleri. `__pycache__` bırakılmadı.

`is_ana` sınaması (`veri_is_ana_bozma_denemesi`): kaynaktan veri benzetimi (`_veri_benzetimi`: `adimlar[*].is_` + `sira_grup[*].is_`)
üstünde `tutarlilik`: temel eksik 0 ve `is_ana` kuralı ≥ 2; K1 "Bağlarken akü ayrık (XT60 açık)." silinmesi, K2 "F3 (kafa) takılı değil"
silinmesi, K1 uyarısının ilk alt adıma taşınması ve uyarıların yalnız veride olmayan `is_ana` anahtarına yazılması yakalanır. Çıktıdaki
temel satırı "YAKALANDI (0)" diye görünür (temel denetim geçti anlamında; biçim kusuru, işlev doğru).

## 8. Kare düzeltmeleri (kısım 2; FreeCAD'siz önizleme, sayılar `onizle.py` benzetimi)

Kaynak: bağımsız kare incelemesi `planlama/d158/F10l-kare-inceleme.md` (dokunulmadı). Alan: `rehber_metin.py` DEMET_ALT / E4.

| Kare | İnceleme bulgusu | Yapılan | Önizleme |
|---|---|---|---|
| 32.4 | yanlış bilgi: B01'in eski yolu (Kablo yolu 12) U06 diye okunuyor | `kablo_sec` yalnız U06; Kablo yolu 12 17.10'a (`KABLO_KAPI_ISTISNA`) | U06 2623 px |
| 31.4 | yanlış bilgi: AU1 / K05 "karede görünmez" | kamera (0.55, 0.5, 1.25); `sema_ortulu` kalktı | K05 1801, AU1 7898 px; PAM8403 0 → 0.94 |
| 31.2 | şema karede yok | kamera (-0.3, -0.3, 1.25) | U01 1473 px; ReSpeaker 0 → 0.98 |
| 17.7 | yanlış bilgi: Kablo yolu 9'un XL4016 sonrası eski çizim | kartta uyarı; G19 → 17.9, A01 → 17.8, G17 → 32.3 göndermesi | yalnız metin |
| 17.4 | bağlam yok | `odak` kalktı, kamera (-0.85, 0.9, 0.5) | bağlam geri geldi |
| 17.5 / 17.9 | hat başka karede | göndermeler (G14 / G15 ve SV1 / SV2 → 32.1) | Sema 12 2856 px (17.5) |
| 17.10 | hat görünmüyor | kamera (-0.6, 0.9, 0.5), elektronik katı saydam; Kablo yolu 12 burada | şema 1860+ px; oran 0.196 → 0.68 / 0.79 |
| 17.11 | vurgulu kablo yok | kamera / odak; kartta neden yazıyor | gözle |
| 32.1 / 32.2 / 32.7 | kadraj | kamera / saydam / odak | 32.7 3188 px |
| 32.5 | lejant "beyaz", hat koyu cyan | `sema=("(H02)", "(U03,")`; lejant adı "açık temada koyu çizilir" | H02 4266, U03 622 px |
| 32.6 | AU3 başka karede | `sema=("(AU3)",)` | AU3 4817 px |
| 17.1 / F1 | modelde yok | "Karede görünmez" + yer tarifi | yalnız metin |
| 17.2, 17.3, 17.6, 17.8, B6a | yer tarifi yok | kart metnine yer tarifi | yalnız metin |

Yeni kurallar: D8 (desensiz, şemasız iki alt adımın kamera / saydam / odak üçlüsü aynı olamaz; 2 bozma), F10d `sema_karede`
(lejanttaki şema karede çizilmeli; `--bozma-denemesi` 5 / 5). Eski veride yalnız 31.2 / 31.4'ü yakalardı, ikisi düzeldi.

## 9. Açık maddeler

1. **K64 kapandı (a, kısım 2):** tutucu sonraki CAD paketinde tasarlanıp basılır; B5a not_'u buna göre. Takılma talimatı o pakette.
2. **Regülatör kartının ölçüsü, panel üstündeki yeri ve bağlantı elemanı** kaynakta yok (rehber "doğrulanmadı" der); kart zarfı sonraki
   tam taramalı CAD paketinde (K51, K52, K53).
3. **F3'te regülatör çıkış klemensine erişim** (kapsam dışı bulgu): regülatör artık güç panelinde; F3 (etekten sonra) çıkış klemensine
   erişim ölçülmedi. F3 not_'una yazıldı; CAD paketinde bakılmalı.
4. **G20 boyu:** `boy_tahmin.vekil` üst sınırı (eski "direğe çıkar" yoluna göre) korundu, notu gerçek boyun çok daha kısa olduğunu
   söyler; boy panelde ölçülür. Kesim listesi bu üst sınırla fazla tel gösterir.
5. **K50 dokunulmadı:** G06 notu (XT60E-M), `rehber_kablo.py:152` / `:186`, `rehber_metin.py` K1 / F1 / F5'teki XT60E-M metinleri K50
   kararına bağlı, aynı kaldı.
6. **`F9c-uret.py` `GRUP`** kısım 2'de K64 / K65 eklendi; depo dışı koşu çıkış 0. Depodaki `sonuc-rapor.html` yeniden üretilmedi.
7. **Eski üretim verisi** (`rehber/veri/`) K52 "karar bekliyor" metnini taşır; veri denetimi üretime kadar 1 çıkar (beklenen).
8. **Yazılım sağ / sol düzeltmesi Efe'de** (`planlama/d158/sag-sol-karari.md` § 3): motor, enkoder, sonar, kol kanalı adları robotun kendi
   sağına göre; CAD önden bakanın sağına göre. Düzeltilene dek K1 kurulum testi ters çıkabilir.
9. **CAD yorumlarında eski sağ / sol tanımı** (kapsam dışı, dokunulmadı): `arayuz.py:7`, kopyaları `taban_parcalar.py:8`,
   `taslak_ayar.py:166`, `kutle.json:3`; pan yorumları `arayuz.py:593`, `kafa_parcalar.py:195`, `kafa7_parcalar.py:570`,
   `kafa_montaj.py:861`, `eklem_dogrulama.py:299`.
10. **`arayuz.py:359` göğüs ekranı port notu:** gerçek üründe portların hangi tarafta olduğu Ahmet'te.
11. **HAZIRLIK (adım 0) `kaynak_metinler` taramasında yok** (kapsam dışı): adım 0'daki sağ / sol cümlesini YASAK / ASCII denetimi görmüyor.
12. **32.4'te direk üstünde soluk eski Kablo yolu 12 çizgisi** kalabilir (bağlam çizimi); üretimde gözle bakılmalı.
13. **17.11 mini haritasında halka yok** (odak parçası halka almıyor); kapsam dışı, kayıt.

## 10. Beklenen üretim sayıları (üretim koşulmadı; tahmin)

| | b2d üretimi | b2e beklenen | Neden |
|---|---|---|---|
| Alt adım | 91 | 91 | yeni kart yok; K1 12, K2 8 aynı (birleşim A) |
| Şema | 65 | 65 | şema eklenmedi; yalnız 12 V şema metni |
| Parça | 1192 | 1192 | model değişmedi |
| Kablo | 74; 68 / 5 / 1 | 74; 68 / 5 / 1 | çizim sınıfı değişmedi |
| Kablo durumu | 20 / 53 / 1 | 20 / 54 / 0 | G20 |
| PDF | 84 sayfa | 84–85 | B5a'ya bir paragraf, bir kontrol, iki not (≈ 8 satır) |
| Kare | — | değişmez | model ve kamera aynı; regülatör karede görünmez (B5a not_) |

## 11. Kısım 2 özeti (16.11; FreeCAD'siz, commit yok)

**Değişen dosyalar (kısım 2):** `tasarim/freecad/rehber/rehber_metin.py` (adım 0, B5a, B6a, K1, F1, E4, DEMET_ALT), `rehber_denetim.py`
(K64 kapalı, D8, bozmalar, ASCII listesi), `rehber_kablo.py` (beyaz lejant), `rehber_veri.py` (`koordinat`, odak, Kablo yolu 12 istisnası),
`rehber_gorunum.py` (odak), `rehber_kritik_onay.json` (yenilendi); `rehber/app.js` (yorumlar, mini görünüm ipucu, odak kadrajı);
`planlama/adim3/kablolar_uret.py` + üretilmiş `kablolar.md`, `pin-haritasi.md` (§ 2, § 9 satır sonları; satır kaymadı);
`planlama/d158/F10d-dogrula.py`, `F10l-birlesim.py`, `F9c-uret.py`, `karar-kuyrugu.md` (K64 kapandı, K65 eklendi), `sag-sol-karari.md` (yeni).

**Sağ / sol tanımı (K65, Echo kararı 16.11):** "Bu rehberde ve kablo tablosunda sağ / sol, robota önden bakan kişinin sağı / soludur;
robotun kendi sağı / solu değildir." Yeri: rehber adım 0 (HAZIRLIK `is_`), `kablolar.md` sürüm satırının altı, pin haritası § 2 ve § 9,
`rehber_veri.py` `koordinat`, app.js mini görünüm ipucu. K1 kontrolüne kurulum testi (`sur` v = 0, w = 0,2; `odo_sifirla` + elle tekerlek;
`kod/esp32/OKU_BENI.md`, kartta denenmedi). Ön sınama: +X = robotun kendi solu, 528 konumlu adla tutuyor.

**Sınamalar (kısım 2 sonu):** `kablolar_uret --kontrol` 0; `kablolar_denetim` PASS, bozma 172; `rehber_denetim --kaynak` 0 (D1–D8 hata 0;
K1 39 kablo / 17 madde, K2 18 / 9), bozma 299 / 299; veri denetimi 1 (beklenen: zorunlu eksik 5 / 118 + K52 elektrik 5, eski üretim verisi);
`rehber_kablo` PASS, bozma 86 / 86, `--veri` PASS, bozma 95 / 95; `rehber_kol_kablo` PASSED; `F10l-birlesim` PASS (eklenen 43 / 43,
silinen 9 / 9); `node --check app.js` 0; `F10d --bozma-denemesi` 5 / 5; `F9c-uret` depo dışı 0. Koşulmayan: FreeCAD, tam üretim, PDF.

**Onay kaydı:** `--kritik-onay-yenile` 30 fark (kablo 165, liste 210, metin 1071 → 1098): 1 liste (ZORUNLU K64), 2 metin değişimi
(B5a not_, F1 kontrol), gerisi yeni cümle; kritik değer farkı 0.

**Beklenen üretim:** alt adım 91 (K1 12, K2 8), şema 65, parça 1192 aynı; kareler değişir: 17.4, 17.5, 17.10, 17.11, 31.2, 31.4, 32.1,
32.2, 32.4, 32.5, 32.6, 32.7; PDF biraz uzar (≈ 85–86 sayfa). Üretimde gözle bakılacak: yalnız metin kartları, gerçek şema ataması
(32.5 / 32.6 AU3, 17.10 B01), koyu tema, PDF.

## 12. Düzeltme turu 1 (16.11.2026 06:35–06:56; kontrol `planlama/d158/F10m-kontrol.md` DÜZELTME GEREKLİ, küçük)

Üretim ajanı; HEAD = uzak = `84f1a4a`, commit yok. Geçici dosyalar oturum scratchpad'inde (`…\scratchpad\b2e-uretim\`).

- **D1 (yapıldı):** `rehber_denetim.py` `kaynak_metinler` artık adım 0'ı (HAZIRLIK `baslik`, `is_`, `kontrol`, `kablo`) da dolaşır
  (`getattr(R, "HAZIRLIK")`; HAZIRLIK yer tutucu taşımaz, ham = çözülmüş). Sınandı: beş kelime izin listesinden bellekte çıkarılınca
  kaynak modu tam olarak `rehberde`, `tablosunda`, `bakan`, `soludur`, `adlar`'ı "kaynak 0 is_" yerinde yakalar (önce görmüyordu). Beş
  kelime `ASCII_TAMAM`'a eklendi (Türkçe harfi olmayan doğru yazım; TR sözlüğünde ASCII karşılıkları yok). Adım 0'ı okutunca başka
  kalıntı çıkmadı (ascii 0, yasak 0, çıplak sayı 0, zorunlu 0). Kontrolün `veri_benzet.py`'si (eski veri + `alan_isle` + `denetle`)
  bugünkü kaynakla: ascii **5 → 0**, zorunlu eksik 0; kalan elektrik 1 eski verideki şema 4 metni (kaynak düzeltilmiş, üretimle kalkar).
- **D2 (yapıldı):** K1 kontrol, sağ / sol kurulum testi: "F5 … devreye aldıktan **ve motor / enkoder yön testinden (`*_MOTOR_TERS`,
  `*_ENKODER_TERS`; `kod/esp32/OKU_BENI.md`) sonra** yapılır"; sayaç cümlesi "soldaki arka teker `odo` satırında **yalnız `sag`
  sayacını değiştirmeli (`sol` sabit kalır)**, sağdaki yalnız `sol` sayacını; sayacın artıp azalması bu testin konusu değil, yön
  testinin konusudur" ("elle ileri çevir" → "elle çevir"). F5 aşama 2'ye tek cümle gönderme: "Yön testinden sonra K1 kontrolündeki
  sağ / sol kurulum testini yap." `sag-sol-karari.md`: § 2 madde 4 ve § 5 başlığı / sırası (taraf testi, yön testinden sonra; ölçüt
  hangi sayacın değiştiği); § 3'e iki madde: BTS IS girişleri (`guc.*` `is_sol` / `is_sag`, GPIO32 / 33) takası ve `*_TERS`
  bayraklarının taraflarıyla taşınması ya da F5'te yeniden kalibrasyonu (bugünkü değerler `git show origin/main:kod/esp32/src/motorlar.cpp`
  ile okundu: SOL / SAG MOTOR false / true, ENKODER false / true, "hepsi TAHMİNİ").
- **N6 (yapıldı):** D8 kamera üçlüsünü 3 ondalığa yuvarlar, saydam / odak sırasız küme; iki yeni bozma (32.8'e 1e-6 kaydırılmış kamera,
  ters sıralı saydam / odak) yakalanır.
- **N7 (yapıldı):** kapalı karar düzenli ifadesine K65 (`\bK(1|10|11|14|52|64|65)\b(?! a)`); bozma M21d ("Sağ / sol tanımı karar bekliyor
  (K65)") yakalanır.
- **N3 (yapıldı):** `karar-kuyrugu.md` K64 "Kayıtta olmayan" paragrafına "(Açılıştaki durum; kapanıştan sonra B5a not_'u ve 17.1 değişti,
  bkz. aşağıda "Durum".)" (sayımlar aynı: açık 48 / kapandı 17 / toplam 65).
- **N8 (yapıldı):** `sag-sol-karari.md` § 9: `tubitak-2209b/` depoda izlenmiyor (`.git/info/exclude`; kontrol `.gitignore` demişti,
  `git check-ignore -v` ile düzeltildi).
- **N13 (yapıldı):** adım 0 sağ / sol paragrafının sonuna "Robotun arkasından çalışırken önden bakanın sağı senin solunda kalır."
- **Kaza notu (yapıldı):** `F9c-uret.py` `--help` / `-h` kullanım metnini basıp çıkış 0 ile durur; tanınmayan bayrak ya da değersiz
  `--cikti` yazmadan çıkış 2. Sınandı: `--help`, `-h`, `--yardim`, `--cikti`, `--kuru --fazla`; her birinden sonra depodaki
  `sonuc-rapor.html` git karması `44c02d35…` = HEAD'deki (yeniden üretilmedi). `--kuru` 0, `--cikti <geçici>` 0.
- **Alınmayan (açık madde):** N1 (G20 `rehber` alanı), N2 (G20 boy üst sınırı), N4 (K2 "Taban şeması 12'nin direkten kafaya çıkan kısmı
  eski" cümlesi; üretimden sonra 32.4'e bakılacak), N5 (32.5 AU3 / S10 / G17 göndermesi), N9 (17.11 mini harita halkası), N10 (w = 0,2
  ile dönmezse ne yapılacağı: değer kaynakta yok), N11 / N12 / N14 (bilgi).

**Onay kaydı:** `--kritik-onay-yenile` iki kez (D1 + D2, sonra N13): toplam **21 fark** (metin 1098 → 1117; kablo 165, liste 210 aynı).
Eklenen 21: adım 0'ın 17 cümlesi (D1'in kapsam genişlemesi; kısım 2'nin 3 sağ / sol cümlesi + HEAD'de zaten var olan 14 cümle), N13
cümlesi, F5 göndermesi, K1 testinin değişen 2 cümlesi (2 silindi). Girdi düzeyi karşılaştırma (`…\b2e-uretim\onayfark.py`): silinende
olup eklenende olmayan değer **yok**; eklenende fazla olanlar adım 0'ın HEAD'deki değişmemiş sayıları (72 parça, M3 / M5 / M7, alyan
ölçüleri, Ø7,1 / Ø5,1 …) ve yol adlarındaki "158", "32" (`d158`, `esp32`). **Kritik değer farkı 0.**

**Birleşim** (`F10l-birlesim.py`, taban `84f1a4a`): beklenen eklenen 43 → **48** (K1 testinin iki cümlesi yeni metinle; + F5 göndermesi,
adım 0'ın üç K65 cümlesi, N13), silinen 9 / 9. GEÇER.

**Sınamalar (FreeCAD'siz, 06:50–06:55):**

| Sınama | Kısım 2 sonu | Düzeltme turu 1 sonrası |
|---|---|---|
| `kablolar_uret --kontrol` / `kablolar_denetim` / bozma | 0 / GEÇER / 172 | 0 / GEÇER / 172 |
| `rehber_denetim --kaynak` | 0; metin 618 (adım 0 yok) | 0; metin **630** (adım 0 dahil); ascii 0, onay farkı 0 (yenilemeden sonra); D1–D8 hata 0 |
| `rehber_denetim --bozma-denemesi` | 299 / 299 | **302 / 302** (+ D8 × 2, M21d) |
| `rehber_denetim` (veri, eski üretim) | 1 (beklenen) | 1 (beklenen: zorunlu eksik 5 / 118 + K52 elektrik 5, eski veri) |
| `rehber_kablo` / bozma / `--veri` / bozma `--veri` | GEÇER / 86 / GEÇER / 95 | aynı |
| `rehber_kol_kablo --yazma` | 38 GEÇTİ | 38 GEÇTİ |
| `F10l-birlesim.py` | GEÇER (43 / 9) | GEÇER (48 / 9) |
| `F10d-dogrula.py --bozma-denemesi` | 5 / 5 | 5 / 5 |
| `node --check rehber/app.js` | 0 | 0 |
| `F9c-uret.py --cikti <geçici>` | 0 | 0 (GRUP'ta kapanmış karar bilgi satırı) |

Değişen dosyalar (bu tur): `tasarim/freecad/rehber/rehber_denetim.py`, `rehber_metin.py`, `rehber_kritik_onay.json`;
`planlama/d158/F10l-birlesim.py`, `F9c-uret.py`, `sag-sol-karari.md`, `karar-kuyrugu.md`, bu günlük. K50 ve CAD model dosyalarına
dokunulmadı. Depoda `__pycache__` yok.

## 13. Üretim ve zincir (16.11.2026 06:56–08:43; saatler sistemden)

Yöntem F10l § 10 ile aynı (scratchpad `b2e-uretim\`: `baslat.ps1` → `sarmal.ps1` 15 s bellek bekçisi, eşik 1,2 GB art arda iki ölçüm ya
da boş commit < 2 GB → `.durum`; arka planda `bekci.ps1`, üretimde 110 dk, zincirde 100 / 60 dk). Kaynağa üretimden sonra dokunulmadı
(yalnız bu günlük ve `dongu-158.md`; ikisini üretim okumaz).

### 13.1 Üretim: tek koşu, çıkış 0 (06:56:02–07:40:02)

`rehber_uret.py` tam koşu: **çıkış 0, 2640 s** (b2d ikinci koşu 2606 s). Bellek önce 3,52 GB, en düşük 1,81 GB; bekçi tetiklenmedi.
FreeCAD kilidi 06:56 "P10.7b2e üretim ajanı: rehber_uret.py tam üretim", veri aşaması (168 s) bitince 06:59:07 "boş"; son hâli "boş".
FreeCAD'in Python'u `-B`'ye karşın dört `__pycache__` yazdı (`planlama/adim4`, `tasarim/freecad`, `tasarim/freecad/lale158`,
`tasarim/freecad/rehber`; hepsi 06:56–06:58'de oluşmuş); zincirden önce silindi, sonda depoda `__pycache__` yok.

| Ölçü | Beklenen (brief) | Ölçülen |
| --- | --- | --- |
| ön sınama | geçer | "kaynak denetimi gecti, onay kaydi tutuyor (kablo 165, liste 210, metin 1117)" |
| alt adım | 91 | **91**, geçti 91; her parça / her şema tek alt adımda (60 şema, birden çok 0, hiç 0) |
| şema / parça | 65 / 1192 | **65 / 1192** (renk 1192, CAD sırası eşleşme 1192) |
| kablo | 68 / 5 / 1 | **68 / 5 / 1** (zincir 2: yol çizimi 68 = CAD 39, kol 6, şema 29; bağlantı tablosu 5; hiçbiri 1 G06); eşlemesiz 0 |
| denetim (veri) | — | ASCII 0, elektrik 0, **zorunlu eksik 0 / 118**, yasak 0 (istisna 10) |
| sıra / giriş / uçuş / ısıl / perdelenme | hata 0 | ulaşılamaz 0 / 565; girilemez 0; uçuş 340, çarpışan 0, istisna 16; ısıl hata 0; gerekçesiz gizli 0, istisna 117 |
| kol kablo | — | 38 bölüm GEÇTİ |
| yazdırma kareleri | — | 50 + 91 = 141 kare, piksel denetimi 141 / 141, boş yok; en düşük çizim oranı 0,0606 |
| PDF taşan / tamlık | taşan 0, eksik 0 | **86 sayfa** (adım 50 + devam 36), eşleme tutarlı, **taşan yok**; tamlık: `is_` 21557 karakter, eksik 0; madde 440, eksik 0; yineleme 0; 18941 kB |
| en küçük yazı | ≥ 8,0 pt | DOM / PDF **8,1 pt** |
| tarayıcı / 360 px | — | 50 / 50, konsol 0; 7 adreste 360 / 0 |
| PDF sayfa | ≈ 85–86 | 86 (b2d 84; K1 kontrolündeki uzun test cümlesi ve B5a / K1 / K2 kart metinleri) |

PDF'te çözülmemiş yer tutucu 0. Adım 0 sağ / sol paragrafı (N13 cümlesi dahil) s. 1'de tam; K1 kurulum testi s. 21'de tam (D2'nin
yeni metniyle); F5 göndermesi s. 84'te. Veri `koordinat`: "mm; +X robota önden bakanın sağı (robotun kendi solu), +Y yukarı, +Z ileri
(yüz); eksenler sağ elli" (N14 kapandı).

### 13.2 Zincir (F10h § 9 2–10, F10l § 10.5'teki komutlar)

- **Birinci koşu `zin1` (07:40:34–08:20:57): bellek bekçisi durdurdu** (`BITTI bellek sure 2423 enaz 0.79`). 2–5 bitti, hepsi çıkış 0;
  F10d "telefon" aşamasındayken boş bellek 08:19:26'dan sonra 2,06 → 0,79 GB'a düştü, iki ölçüm < 1,2 GB → süreç ağacı durduruldu.
  Artık süreç kalmadı (python / chrome / FreeCAD 0), bellek hemen 3,67 GB'a döndü. Kod hatası değil, makine belleği; b2d'de aynı
  aşamanın en düşüğü 1,42 GB'tı. F10d-dogrula.json yazılmamıştı.
- **İkinci koşu `zin2` (08:21:35–08:43:38): 6–10, çıkış 0, 1323 s**, en düşük boş bellek 1,39 GB (bekçi tetiklenmedi).

| Sıra | Komut | Çıkış | Süre (s) | Ölçülen |
| --- | --- | --- | --- | --- |
| 2 | `rehber_kablo.py --veri …` | 0 | 2 | SONUÇ GEÇER; 68 / 5 / 1; ayırt edilemeyen 0; onay tutuyor; eşlemesiz 0 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 24 | 95 / 95 |
| 3 | `rehber_denetim.py` (veri) | 0 | 1 | ASCII 0, elektrik 0, zorunlu eksik 0 / 118, yasak 0 |
| 4 | `F10f-dogrula.py` | 0 | 580 | GEÇTİ (veri, sınama, kablo kare, sağ / sol, parça kare, gizli piksel, mini etiket) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | 974 | GEÇTİ; `renk_demo` KALDI (bilinen karar); işaret 1284 / 1284 |
| 6 | `F10d-dogrula.py --goruntu-yok` (zin2) | 0 | 873 | GEÇTİ; 141 / 141 konum eşit; masa yabancı şema 0; **`sema_tek` 60 şema, birden çok 0, hiç 0**; **lejantta geçen şema karede çizilmiyor 0**; 360 px taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | 444 | GEÇTİ; seçim 6 / 6, yazdırma kareleri 50 / 50, PDF görüntü 141, boş sayfa yok, dış istek 0, konsol 0, 360 px taşma 0 ("veri değişti", bilgi) |
| 8 | `F9b-dogrula.py` | 0 | 5 | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 0 | 0 | izlenen 17 dosya kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | 0 | GEÇER, kötüleşen yok |

Zincir PDF'i, `kontrol.json`'u ve veriyi değiştirmedi (SHA-256 zincirden önce / sonra aynı). Zincirin yazdığı:
`planlama/d158/F10{a,d,e,f}-dogrula.json`.

**Beklenen ↔ ölçülen:** alt adım 91 ↔ 91; şema 65 ↔ 65; parça 1192 ↔ 1192; kablo 68 / 5 / 1 ↔ 68 / 5 / 1; taşan 0 ↔ 0; tamlık eksik 0 ↔ 0;
en küçük yazı ≥ 8,0 ↔ 8,1 pt; `sema_tek` GEÇTİ ↔ GEÇTİ; zincir adımları çıkış 0 ↔ 0 (birinci zincir koşusu bellek bekçisiyle durdu,
6–10 yeniden koştu); PDF ≈ 85–86 ↔ 86. `renk_demo` KALDI bilinen.

### 13.3 Üretimde sınanan varsayımlar (§ 9 madde 12, § 11)

| Varsayım | Sonuç | Dayanak |
| --- | --- | --- |
| Kablo yolu 12 (B01) 17.10'a düştü | **evet** | veri K1 `sira_grup[9]` `ref` = p1190 (Kablo yolu 11) + **p1191 (Kablo yolu 12)**; başka alt adımda yok (her parça tek alt adımda); karede vurgulu mor |
| U06 32.4'e düştü | **evet** | K2 `sira_grup[3]` `ref` 0, `sema` yalnız "ESP32 USB (U06) …"; lejant "Kablo: Hazır kablo: USB" |
| AU3 şeması 32.6'ya düştü | **evet** | `sira_grup[5]` `sema` yalnız "Hoparlör (AU3) …"; 32.5'te H02 + U03; 32.6 lejantı "Analog ses (beyaz; açık temada koyu çizilir)" |
| 32.4'te direkte eski çizgi kaldı mı | **kaldı** (soluk) | 32.4 karesinde direğin sol kenarında ince soluk mor çizgi: Kablo yolu 12'nin direk kısmı, önceki adımlar bağlamı olarak çiziliyor. Kart metni (17.10) bu kısmın eski çizim olduğunu söylüyor; 32.4 kartı söylemiyor (N4 açık) |
| Yeni denetim: aynı kare (D8) | hata 0 | kaynak D8 0; ek ölçüm: 91 alt adım karesinden aynı adımdaki her çiftin 3B alanı karşılaştırıldı (eşik 24, 2000 px altı "neredeyse aynı"): ekran 0 çift, basılı 0 çift |
| Yeni denetim: lejant (F10d `sema_karede`) | 0 | "lejantta geçen şema karede çizilmiyor (sema_ortulu dışı, px < 30): 0" |

### 13.4 Değişen kareler ve kendi bakışım (hüküm bağımsız incelemenin)

Piksel karşılaştırması (HEAD ↔ yeni, eşik 24): değişen 60 PNG (ekran `rehber/goruntu` 23, basılı `planlama/rehber/goruntu` 37). Beklenen
12 kare (17.4, 17.5, 17.10, 17.11, 31.2, 31.4, 32.1, 32.2, 32.4, 32.5, 32.6, 32.7) iki yerde de büyük farkla değişti (≈ 80 k – 700 k px).
Beklenen listenin dışında değişenler:

- Basılı karede yalnız sağ metin sütununda (x 1019–1382) fark: 0, 12, 17.1, 17.6, 17.7, 17.9 (kart metni değişti: adım 0 sağ / sol,
  B5a, yer tarifleri); 35.3 / 35.5 yalnız alt şeritte (1159 px).
- 3B alanda büyük fark: 17 (K1 ana kare, ≈ 400 k px) ve 17.12 (≈ 30 k px): büyük olasılıkla Kablo yolu 12'nin K1'e geçmesi (K1'in genel
  bakışı ve son kontrolü artık onu K1 kablosu olarak çiziyor); doğrulanmadı.
- Küçük fark: 22 (≈ 9,8 k px, dar dikey şerit), 31 (ekranda alt şerit 4 k, basılıda 95 k: E4 ana karesi), 32 (≈ 3,5–5,7 k), 32.3 (≈ 1,5–1,9 k),
  24, 31.5, 31.9 (< 900 px); 18, 25, 31.1, 49.5 eşik altı (0 px > 24). Telefon 360 px karesi: 0, 24, 31, 32. Nedenini tek tek açmadım.

Kendi baktıklarım (ekran / basılı açık tema; koyu tema bakılmadı): 17.4, 17.5, 17.10, 17.11, 31.2, 31.4, 32.1, 32.2, 32.4, 32.5, 32.6,
32.7 ve PDF s. 1 (adım 0), s. 21 (K1 testi). **Açıkça bozuk kare bulmadım** (boş kare yok, alt adım numaraları doğru, metinle çelişki
görmedim). Gözlemler: 32.2'de sarı servo kablosu artık görünüyor (b2d'deki "anlaşılmıyor" karesi); 17.11 yakın kare, vurgu yok (kart
nedenini söylüyor), mini haritada halka yok (N9); 32.6'da AU3 koyu çizgisi yarı saydam kabuğun arkasında, seçilebilir ama soluk; 31.2'de
USB (U01) gri çizgisi kabuğun iç kenarında ince.

### 13.5 Açık maddeler (üretimden sonra)

1. **N4:** 32.4'te direk boyunca soluk eski Kablo yolu 12 çizgisi duruyor; 32.4 kartı bunu söylemiyor (17.10 kartı söylüyor). Bağımsız
   kare incelemesi karar versin (kart cümlesi ya da bağlam çiziminden çıkarma).
2. **N1, N2, N5, N9, N10** (§ 12): dokunulmadı.
3. **Bellek:** zincirin F10d "telefon" aşaması bu makinede 0,8 GB'a kadar indi (birinci zincir koşusu bekçiyle durdu). Sonraki paketlerde
   F10d tek başına koşulabilir.
4. Beklenen listenin dışında değişen kareler (§ 13.4) bağımsız incelemede bir kez görülmeli; koyu tema bu turda bakılmadı.
5. Önceki paketten süren: zor kareler, E3a K01, K1 mor hatlar, SV3 ucu, "20 V aralığı" kaynağı, A4 basılı boşluklar; § 9'daki 2–5, 8–10.

### 13.6 Commit hazırlığı (commit yok; ayrı ajan)

Commit'e girecek 89 dosya (git status'tan, eski kir dışında hepsi): kaynak 15 (`tasarim/freecad/rehber/` 6, `planlama/adim3/` 5
(`kablolar.md` üretilmiş), `rehber/app.js`, `planlama/d158/F10d-dogrula.py`, `F10l-birlesim.py`, `F9c-uret.py`), kayıt 6
(`planlama/d158/F10m-gunluk.md`, `F10m-kontrol.md`, `F10l-kare-inceleme.md`, `sag-sol-karari.md`, `karar-kuyrugu.md`,
`planlama/dongu-158.md`), üretilmiş 68 (`rehber/veri/rehber-veri.js`, `.json`; `rehber/goruntu/` 23 PNG; `planlama/rehber/goruntu/` 37 PNG;
`planlama/rehber/Lale-montaj-rehberi.pdf`, `kontrol.json`; `planlama/d158/F10{a,d,e,f}-dogrula.json`). Liste:
`…\scratchpad\b2e-uretim\commit-liste.txt`.

Girmeyecek eski kir (dokunulmadı): `tasarim/freecad/kabuk/gorsel/*.png` (13), `tasarim/freecad/montaj/yerlesim-kontrol.json`, kökteki 0
baytlık `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`. Bu 19 dosyanın SHA-1'i düzeltme turundan
önceki anlık görüntüyle (06:35) üretim ve zincirden sonra aynı (fark 0). `planlama/d158/sonuc-rapor.html` git karması `44c02d35…` = HEAD.
`git status`'ta bu 89 + 19 dışında satır yok.

## 14. Kare incelemesi ve commit (16.11.2026 09:00; saat sistemden)

Bağımsız kare incelemesi `planlama/d158/F10m-kare-inceleme.md` (salt okunur; üretimden sonra, commit öncesi): **commit'e engel yok**
(yanlış bağlatan çelişki, yanlış taraf, yanlış alt adım ya da boş kare bulunmadı; taraf etiketleri ve "önden bakınca" yer tarifleri
bakılan her karede tutuyor). Kayıt ve commit ajanı; kaynak ve üretilmiş çıktıya dokunulmadı, FreeCAD koşmadı.

**Hüküm dağılımı (aynı 23 kare):** F10l açık 3 / zor 12 / anlaşılmıyor 8 → F10m açık **5** / zor **17** / anlaşılmıyor **1** (17.1).

**Bulgular (inceleme § 2):**
- **Giderildi (4):** 32.4 çelişkisi (vurgulu çizgi artık U06), 31.4 (ses kablosu ve K05 görünür, "Karede: 5 V" doğru), 32.1 ve 32.7
  (arka kamera). Ayrıca F10l § 3.1'deki sağ / sol tanım eksiği giderildi (adım 0, K65); 17.11 artık 17.12'nin kopyası değil.
- **Kısmen giderildi (7):** 17.4, 17.5, 17.10, 17.11, 32.2, 32.5, 32.6 (doğru taraf / saydam kat / yakın kamera; kutular etiketsiz,
  17.10'da yedi mor hat ayrılmıyor, 32.6'da gövdeye inen yollar kadraj dışında).
- **Yalnız metinle örtüldü (9):** 17.1, 17.2, 17.3, 17.6, 17.7, 17.8, 17.9, F1 kontrol, B6a (kare aynı; kartta yer tarifi, "karede
  görünmez" ya da göndermeler).
- **Bulgu yoktu (3):** 17.12, 32.3, 32.8 (17.12 ve 32.3'te yeni küçük sorun, aşağıda; 32.8'de yalnız ölçüt farkı).

**Bilinen gerileme (commit'e bilerek girdi):** B01'in çizgisi (Kablo yolu 12) K1'e geçince (`rehber_veri.py` `kablo_kapisi` istisnası,
inceleme § 1a) K1 ana karesinin (adım 17) kadrajı direğin tepesine açıldı, taban yaklaşık dörtte bir boyuta indi, kablolar okunmuyor;
eski dikey kısım 17.12, 18, 22, 24, 25, basılı 31, 32.1, 32.3, 32.4, 32.7'de kartın anmadığı soluk mor "hayalet çizgi" olarak görünüyor
(32.3'te G17'nin hemen yanında). Yanlış bağlatmıyor (o adımlarda sinyal kablosu döşenmiyor; K2 kablo listesi "eski" diyor). § 13.5
madde 1'deki N4 bununla birlikte açık.

**Açık maddeler (P10.7b2f'nin girdisi):**
1. FreeCAD'siz: 32.3 / 32.4 kartlarına eski çizim cümlesi (N4); 17.12 kadrajı (`odak` ile tabana); K1 ana karesinin kadrajı (adım düzeyi
   kamera / odak; FreeCAD'siz olduğu doğrulanmadı); 31.4'te yedek (takılmayan) USB ses kartı notu; K2 ana karesi (32) lejantına
   "Sinyal (mor)" geri; adım 0 sağ / sol tanımının kutuya alınması (ve adım 0 karesinde bakış etiketi); uç bileşenlerine etiket koyan
   yeni `app.js` özelliği (17.2, 17.3, 17.4, 17.5, 17.6, 17.8, 17.10, 32.2; incelemenin "asıl kaldıraç" dediği); 32.4 USB karşıtlığı.
2. FreeCAD'li: bara gösterim parçası (17.1); Kablo yolu 5 / 7'nin taban ve direk kısmına bölünmesi (17.5, 17.9) ve 17.10'un bölünmesi;
   F1 ölçü noktaları karesi (yeni alt adım); Kablo yolu 12'nin eski dikey kısmının şemadan kaldırılması (kalıcı çözüm; gerilemeyi kapatır).
3. Bakılmayanlar: koyu tema, etkileşimli davranış (tıklama, döndürme, mini harita balonu), PDF'in çoğu sayfası (yalnız s. 1, 21, 24,
   48 çizdirildi), telefon 360 px kareleri ve küçük farklı kareler (31.5, 31.9, 35.3, 35.5, 49.5).
4. Süren: § 12 N1, N2, N5, N9, N10; § 13.5 madde 3–5; § 9 madde 2–5, 8–10.

**Commit:** "Lale P10.7b2e: …" (`lale-duzeltme`), açık `git add` listesiyle 90 dosya: § 13.6'daki 89 + `F10m-kare-inceleme.md`.
Eski kir (§ 13.6'daki 19 dosya) commit'e girmedi, dokunulmadı. Push öncesi gizli / özel veri taramasında § 9 madde 10'daki takma ad,
depo kuralına göre (`planlama/dongu-158.md` § 2, paylaşılan çıktıda takma ad yazılmaz) "Ahmet" yapıldı; başka bulgu yok. Bu dosya commit'in içinde olduğu için karmayı taşımaz; karma
commit geçmişinde.

