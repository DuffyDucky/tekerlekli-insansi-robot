# F9b günlüğü: demo sayfası 1,58 m sayılarıyla (P9.2), 09.11.2026

Ajan A (tasarım/uygulama). Brief: `planlama/d158/F9b-brief.md`. FreeCAD kullanılmadı. Commit / push / merge yok.
Kural dışı tek silme: ilk turda bu işte üretilen iki takip dışı tam sayfa PNG'si (`F9b-goruntu-1400-tam.png`, `F9b-goruntu-360-tam.png`)
silindi (§6). Brief silmeyi yasaklıyordu; dosyalar takip dışıydı, kayıp yok. Düzeltme turu 1'de hiçbir dosya silinmedi (§10).
F7b alanına (`rehber/`, `tasarim/freecad/rehber/`, `planlama/rehber/`, `planlama/d158/F7b-*`) yazılmadı; `rehber/veri/robot.glb`,
`rehber/veri/robot-glb.js`, `rehber/veri/rehber-veri.json` ve `rehber/veri/rehber-veri.js` yalnız okundu.
**Düzeltme turu 1 (§10) sonrası geçerli olan:** model kopyası kaldırıldı, sayfa rehber dosyalarını göreli yükler (KT-F9b-2 = b).
§1–§9 ilk turun kaydıdır; turda değişen yerler o bölümlerde "→ §10" diye işaretli.

## 0. Özet

- Sayfa (`tasarim/Robot-Tasarim-Demosu.html`) baştan üretildi: 1,58 m FreeCAD montajının GLB modeli (rehber GLB'nin kopyası), sayı kartları,
  korunan değerler, modüller, eklem aralıkları, baskı, maliyet, takvim, açık kararlar. Eski V1–V3 CadQuery modeli, kaydırıcılı devrilme
  hesabı ve 1,65 m "Gövde ekranı" denemesi **kaldırıldı** (git geçmişinde: 680b965, c7f9af4).
- Sayılar betikle: `tasarim/cad/demo_uret.py` `SAYILAR` tablosu (anahtar, kaynak, JSON yolu, biçim) → sayfada `<span data-k>`; maliyet
  bölümü JS'de `planlama/maliyet.json`'dan, her sayı `data-mk` ile işaretli.
- Kontrol: `planlama/d158/F9b-dogrula.py` çıkış **0** (statik + DevTools ile 1400 ve 360 px DOM), konsol hatası 0, 360 px'te yatay kaydırma yok.
- Bütünlük: `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0 (10/10 aynı).

## 1. Envanter (F9b öncesi sayfa, HEAD = c7f9af4 içeriği; son içerik değişikliği 680b965)

Sayım `py -3 planlama/d158/F9b-envanter.py` (çıkış 0): HTML metninde 37 sayı (üst 7, gövde ekranı 7, maliyet + "hakkında" 23),
satır içi betik metin sabitlerinde 195 sayı (ana betik 96, gövde ekranı 21, maliyet betiği 78; maliyet betiğindekilerin çoğu Excel XML
kodu, görünür değil) → **232 ham sayı**. Bunlara JS'in hesapladığı değerler eklenir (kartlar, özet, parça listesi, maliyet tablosu).
Gömülü veri: CadQuery model JSON'u (54 parça, V1 17,75 / V2 18,90 / V3 18,57 kg) ve 29.10 tarihli maliyet JSON'u (119 kalem;
`planlama/maliyet.json` ile **aynı değildi**).

| # | Sayfadaki sayı / iddia (eski) | Eski değer | Eski kaynak | Güncel kaynak anahtarı | Yeni değer (sayfada) | Durum |
|---|---|---|---|---|---|---|
| 1 | Boy (V3 deneme / kaydırıcı) | 125 cm (V1 115) | `model JSON C.V3.H`, `C.H0` | `lale158-kontrol.json toplam_boy_mm` | 1.580 mm (1,58 m) | değişti |
| 2 | Kütle (özet, alt bilgi) | V3 18,57 kg (V1 17,75, V2 18,90) | `model JSON check.v3.mass` | `montaj-analiz.json kutle_g` | 25,72 kg (25.720,55 g) | değişti |
| 3 | Ağırlık merkezi yüksekliği | V3 337 mm | `check.v3.com[1]` | `montaj-analiz.json agirlik_merkezi.1` | 528,6 mm | değişti |
| 4 | Parça sayısı / parça listesi | 54 CadQuery parçası (V2 CSV) | model JSON, `parca-listesi-V2.csv` | `montaj-analiz.json parca_sayisi`, `parcalar[tur=…]#say` | 1.179 (baskı 72, satın 210, bağlantı 893, lazer 3, imalat 1) | değişti |
| 5 | Servolar | DS3218 omuz, MG996R dirsek/kafa (seçici: DS3218 / MG996R / STS3215) | `SERVOS` sabiti | `F6a-eklem_sinirlari-oneri.json eklemler#say`; `montaj-analiz.json parcalar[kod=DS3235 servo]#say`, `[kod=MG996R servo]#say` | 10 = 4 DS3235 + 6 MG996R | değişti |
| 6 | Kafa ekranı | V1 7" kafada; V2 iki GC9A01 göz; V3 7" yüz | `VER_DEK`, `STAGE_*` | `montaj-analiz.json parcalar[ad=Yuz ekrani WaveShare 10,1in QLED HDMI].kod` | 10,1" QLED 1280 × 720 | değişti |
| 7 | Göğüs ekranı | V2/V3 10,1" (V3'te 15° eğik) | `VER_DEK`, `ver-list` | `montaj-analiz.json parcalar[ad=Gogus ekrani 11,6 in HDMI 1920x1080 kasali]` | 11,6" 1920 × 1080 | değişti |
| 8 | Gövde ekranı denemesi: boyutlar 5–13,3", y 263–1062, bant 476–861, 669, derinlik 60–98, 1,65 m gövde | 1,65 m | `arayuz.py:306-356` (sayfaya elle) | — | bölüm kaldırıldı | kaldırıldı |
| 9 | Kaydırıcı aralıkları (boy 950–1600, şase 260–500 / 340–700, kol 250–500, rampa 0–10°) ve ön ayarlar (H0 1150, W0 340, L0 500; riskli 1500/280/360/820/480/90°) | — | `SL`, `PRESETS`, `C` | — | kaldırıldı (eski modelin parametrik hesabı) | kaldırıldı |
| 10 | Devrilme kartları (m/s², pay ×, rampa °), acil stop 1,5 m/s² | V3 modelinden hesap | JS `calc()` | `regresyon-son-kosu.json degerler.rampa_yuksuz.deger`; `F6a-…oneri.json teker.ivme_sinir_m_s2.*` | rampa payı 1,519 (≥ 1,5); düz fren ≤ 1,8, sürüş ≤ 0,5, rampa ≤ 0,1 m/s² | değişti |
| 11 | Motor kartı: JGB37 21 kg·cm, sürekli 6,3 kg·cm, teker yarıçapı 62,5 mm, F formülü | sabit | `calc()`, "hakkında" | — (158 kaynağında yok) | kaldırıldı | kaldırıldı |
| 12 | Omuz/dirsek servo kartı: DS3218 20, MG996R 10, STS3215 19,5 kg·cm; dirsek sınırı 5,0 | sabit | `SERVOS`, `calc()` | — | kaldırıldı; tilt 3,64 / pan 2,21 payı eklendi (`regresyon-son-kosu.json`) | değişti |
| 13 | Özet: hız 0,39 m/s; ölçü G × D × Y | sabit / hesap | `render()` | — (kaynak yok) | kaldırıldı | kaldırıldı |
| 14 | "Ne yapmalı" önerileri: akü 2,8 kg, şase 50 cm, boy 115 cm, %15–20 doluluk | sabit | `render()` | — | kaldırıldı (akü artık 3,0 kg, F1b) | kaldırıldı |
| 15 | V1→V2, V2→V3 listesi: 21×18×15 → 18×15×14 cm, 36 cm, 35 mm, 23 cm, 115→125 cm, 65→82 cm, 15°, 34→27 cm, 30 cm | tarihçe | `verList*` | — | kaldırıldı | kaldırıldı |
| 16 | Yapım adımları: 15 kg yük, 7" ekran | sabit | `STAGE_NOTE` | montaj sırası artık rehberde (`rehber-veri.json adimlar#say`) | "montaj rehberi (50 adım)" bağlantısı | değişti |
| 17 | 3B baskı: okul yazıcısı 25 × 25 × 25 cm, ≤ 23 cm parçalar, PETG 2,5 mm duvar | sabit | "hakkında" | `baski-analiz.json yontem.x2d.*`, `toplam.*`; `Y2b-baski.json toplam.cf_g/petg_g` | X2D 246 × 246 × 250 mm, sığmayan 0; 72 parça; 7.668,9–7.726,7 g; 159,90–161,08 sa; destek 124,5 g; 13 destekli (9 tür); PETG 6.474,9 g; PETG-CF 1.194,0–1.251,8 g | değişti |
| 18 | Vida/kablo payı 0,6 kg | sabit | `C.EXTRA` | — (montaj kütlesi bağlantı elemanlarını sayıyor) | kaldırıldı | kaldırıldı |
| 19 | Modül kütleleri | yok | — | `montaj-analiz.json moduller[ad=…].parca / .kutle_g` | 8 modül tablosu | yeni |
| 20 | Korunan değerler (çakışma 0 ×4, SY8205 × USB 0, mik–hoparlör) | yok | — | `regresyon-son-kosu.json degerler.*` | 0, 0, 0, 0, 0 mm³, 574,3 mm | yeni |
| 21 | Eklem aralıkları | yok | — | `F6a-…oneri.json eklemler.{r_s1,r_s2,r_dirsek,r_bilek,pan,tilt}.min/max/servo`, `bagimli.0` | S1 −45…135, S2 5…120, dirsek 0…105, bilek −90…90, pan −90…90, tilt −13…13; S1 ≥ 120'de S2 ≤ 117 | yeni |
| 22 | Maliyet: genel toplam (V3, %15, yedek dahil) | 103.767,58 TL (29.10, 119 kalem, 99 görünür) | gömülü eski JSON | `planlama/maliyet.json` (09.11; JS hesabı, `data-mk`) | 118.666,22 TL (121 kalem), ara 103.188,02 | değişti |
| 23 | Maliyet: kur, kur kaynağı, tarih | 49,4463, TCMB 16.10, 29 Ekim 2026 | gömülü eski JSON | `maliyet.json kur`, `kur_kaynak`, `tarih` | 49,4463; 16.10.2026; 9 Kasım 2026 | tarih değişti |
| 24 | Maliyet satırları, gruplar, notlar (978 `data-mk` sayısı) | 29.10 | gömülü eski JSON | `maliyet.json kalemler.*`, `gruplar`, `notlar` | 09.11 değerleri | değişti |
| 25 | Maliyet "V3 yapısı" etiketi, V1/V2 geçişi | V1/V2/V3 | `O.ver` | aynı kural (`ver` boş ya da `v3`) | "güncel liste"; sürüm seçici kaldırıldı | değişti |
| 26 | Takvim | "2 Ekim 2026" (hoca geri bildirimi), yapım adımları | `VER_DEK` | `planlama/proje-plani.md` (JSON değil) | takvime tarih yazılmaz; S ↔ K28/K29 "karar bekliyor" | değişti |
| 27 | İndirmeler: STEP V1/V2/V3, `parca-listesi*.csv` | CadQuery | `cad/` | `freecad/montaj/robot-montaj.step`, `robot-bom.csv` | ana montaj STEP + BOM | değişti |
| 28 | Alt bilgi "Model: cad/robot_cad.py (CadQuery)" + V1/V2/V3 kütle/AM | — | `stamp` | — | "üretici demo_uret.py, şablon viewer-template.html" | değişti |
| 29 | Açık kararlar | yok | — | `karar-kuyrugu.md` özet tablosu (durum) | 14 karar "karar bekliyor": K2, K3, K9, K11, K28, K29, K32, K34, K38, K41, K42, K44, K45, K46 | yeni |

**Özet:** eski sayfanın metinde 232 ham sayısı ve JS'le hesaplanan bütün model sayıları ana tasarıma ait değildi. Hiçbiri aynen kalmadı:
model / boy / kütle / parça / servo / ekran / yapım / devrilme sayıları (satır 1–18) değişti ya da kaldırıldı; maliyet bölümünün sayıları
(satır 22–24) aynı kuralla güncel `maliyet.json`'dan yeniden hesaplandı (aynı kalan: kur 49,4463 ve kur kaynağı). Yeni sayfada
**128 `data-k` elemanı (125 anahtar)** + **978 `data-mk` maliyet sayısı**; DOM'daki 1.635 sayının tamamı bağlı, 5 muaf (pay seçenekleri
%0–%25, `data-ui="secenek"`), bağsız 0.

## 2. Tasarım kararları (gerekçeli)

- **Üretici:** `demo_uret.py` yeniden yazıldı (giriş noktası korunsun: `maliyet.json` dipnotu ve `CLAUDE.md` bu adı veriyor;
  `robot_cad.py:1046-1047` `demo_uret.build(MODEL_JSON)` çağrısı bozulmasın diye imza aynı, argüman yok sayılıp not basılıyor).
  Şablon `viewer-template.html` 1,58 m şablonu oldu (eski hâli git'te).
- **Model: kopya** (→ §10: orkestratör kararı b ile kaldırıldı, sayfa artık göreli bağlantı kullanıyor) (`tasarim/cad/lale158-model.js`, base64 GLB + 1.192 satırlık parça tablosu {id, ad, modül, sınıf}). Gerekçe:
  sayfa `file://` altında açılmalı, `fetch` ile `.glb` okunamaz; göreli bağlantı (`../rehber/veri/robot-glb.js`) F7b'nin çıktı biçimine
  (global ad, dosya adı) ve çalışırken değişen `rehber-veri.json`'a bağlanırdı. Kopyanın güncelliğini `F9b-dogrula.py` denetler
  (GLB bayt bayt + sha256, tablo `rehber-veri.json` ile); F7b `robot.glb`'yi yeniden üretirse doğrulama 1 döner, `demo_uret.py` yeniden
  koşulur. Bedeli: depoya +3,4 MB (eski gömülü CadQuery modeli 0,76 MB çıktı). GLB okuyucu sayfada (yalnız POSITION + indices + matrix);
  three.js r128 (cdnjs) dışında kütüphane yok.
- **Açık kararlar:** değer yerine `{{K:Kxx}}` → "karar bekliyor · Kxx"; etiket metinlerini kendim yazdım (sayısız), durum kuyruktan okunur.
  K44 / K45 / K42 brief'teki örneklerin hepsi sayfada. Önerilen varsayılanlar (ör. K3 "≤ 100 g", K45 "59 / 30°/s", K42 "+1 makara")
  sayfada yok.
- **maliyet.json dokunulmaz** olduğu için eski metinler aynen gösterilir; önceki tasarıma ait notlar sayfada `eski tasarım notu` diye
  işaretlenir (desen `1[,.]65 ?m|125 ?cm`), `notlar[0]`'daki "Demodaki 3B model eski CadQuery V3" cümlesinin altına F9b uyarısı eklenir.

## 3. Komutlar ve çıkış kodları

| Komut | Çıkış | Not |
|---|---|---|
| `py -3 tasarim/cad/demo_uret.py` | 0 | 125 anahtar, 14 karar, 153 kalem; model 1.192 düğüm, 3.413 KB; demo 161 KB |
| `py -3 planlama/d158/F9b-dogrula.py --goruntu` | **0** | "SONUC: GECER (hata 0)" |
| `py -3 planlama/d158/F9b-envanter.py` | 0 | §1 sayımı |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | "carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni." |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** | 10/10 "aynı", "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)" |

`F9b-dogrula.py` çıktısının özeti (tam tablo betikte, her anahtar için dosya · yol · metin basılır):

```
[1] data-k: 125 anahtar, sayfada 128 bagli eleman (her biri kaynak dosyadan yeniden okundu, bicimlendi, karsilastirildi)
[2] sayi taramasi (statik HTML): 117 bagli, 5 muaf {'secenek': 5}, 0 bagsiz
[3] maliyet: gomulu JSON = planlama/maliyet.json (153 kalem); sayfa kurali 121 kalem, ara 103.188,02, genel 118.666,22 TL
[4] model kopyasi: GLB 2559336 bayt, sha256 760bf1ff5955, 1192 dugum; tablo 1192 satir (rehber-veri.json ile ayni)
[5] kararlar: 14 karar, 33 etiket; hepsi kuyrukta "açık"
[6] eklem sinirlari kod/ ile sayisal ayni (10 eklem, bagimli, teker ivmesi); servo 10 = 4 DS3235 + 6 MG996R; kafa 10,1" QLED; gogus 11,6"
    brief sayilari: boy 1580, rampa 1,519, tilt 3,64, pan 2,21, mik-hoparlor 574,3 (kaynakla ayni)
[8] 1400 px: innerWidth 1400, scrollWidth 1400, data-hazir=1, data-hata='', konsol hatasi 0; data-k 128, data-mk 978, 1635 bagli, 0 bagsiz
    360 px:  innerWidth 360,  scrollWidth 360,  data-hazir=1, data-hata='', konsol hatasi 0; data-k 128, data-mk 978, 1635 bagli, 0 bagsiz
SONUC: GECER (hata 0)
```

Tarayıcı: Chrome headless, DevTools protokolü (`websockets`). Masaüstü Chrome penceresi ~500 px'in altına inmiyor (`--window-size=360`
ile innerWidth 504 ölçüldü), bu yüzden 360 px `Emulation.setDeviceMetricsOverride` ile verildi. Konsol hatası olaylardan sayılır
(`Runtime.exceptionThrown`, `console.error/assert`, `Log.entryAdded` error) + sayfanın kendi sayacı `<html data-hata>`.

## 4. Kabul ölçütleri

| Ölçüt | Sonuç | Kanıt |
|---|---|---|
| Sayfa yerelde (`file://`) açılıyor, konsol hatası 0 | ✅ 1400 ve 360 px'te 0 | `F9b-dogrula.py` [8]; `data-hazir=1` (3B model çizildi) |
| `F9b-dogrula.py` 0, her sayı bir JSON anahtarına bağlı | ✅ çıkış 0; bağsız sayı 0 (statik 117, DOM 1.635 bağlı; 5 muaf pay seçeneği) | [1]–[3], [8] |
| Eski 1,65 sayısı kalmamış, kalan eşleşmelerin gerekçesi var | ✅ şablon, üretici, model tablosu 0 eşleşme; sayfada 12 (gömülü `maliyet.json` metni) + DOM'da 11 (8 kalem notu, 3 genel not), hepsi `maliyet.json` metni | §5 |
| Açık kararlar "karar bekliyor" | ✅ 14 karar, 33 etiket, hepsi kuyrukta açık | [5] |
| 360 px'te yatay kaydırma yok | ✅ scrollWidth 360 = innerWidth 360 | [8]; `F9b-goruntu-360-*.png` |
| Kafa QLED 10,1", 10 servo, göğüs 11,6", model 1,58 m | ✅ | [6]; KPI kartları; GLB 1.192 düğüm |
| Bütünlük: `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0 | ✅ 0 / 0 | §3 |
| Görüntü ≥ 4, biri 360 px, Read ile bakıldı | ✅ 10 görüntü, 4'ü 360 px | §6 |

## 5. 1,65 araması (betikle: `1650`, `1.650`, `1,65`, `1.65`, `165 cm`, `165 mm`)

| Yer | Eşleşme | Gerekçe |
|---|---|---|
| `tasarim/cad/viewer-template.html`, `tasarim/cad/demo_uret.py`, `tasarim/cad/lale158-model.js` (base64 dışı; → §10: artık aranmıyor, sayfa kullanmıyor) | 0 | — |
| `tasarim/Robot-Tasarim-Demosu.html` | 12 | Hepsi `<script id="cost">` içinde: `planlama/maliyet.json`'un birebir kopyası (brief'e göre dokunulmaz; [3] eşitliği denetliyor) |
| DOM (görünür metin) | 11 | `maliyet.json` metni: `kalemler.{5, 8, 14, 19, 33, 92, 107, 139}.not` ve `notlar.0.b`, `notlar.0.t`, `notlar.1.b`. Hepsi "eski tasarım notu" etiketli |

## 6. Görüntüler (Read ile bakıldı)

`planlama/d158/` altında: `F9b-goruntu-1400-ust.png` (KPI + 3B izometrik), `F9b-goruntu-1400-yan-seffaf.png` (yan, şeffaf kabuk),
`F9b-goruntu-1400-modul-on.png` (ön, modül renkleri, kabuk gizli), `F9b-goruntu-1400-korunan-eklem.png`, `F9b-goruntu-1400-baski-maliyet.png`,
`F9b-goruntu-1400-kararlar.png`, `F9b-goruntu-360-ust.png`, `F9b-goruntu-360-model.png`, `F9b-goruntu-360-eklem.png`, `F9b-goruntu-360-maliyet.png`.
Bakarken bulunan ve düzeltilen: "3B model yükleniyor" yazısı kalıyordu (CSS `display:flex`, `hidden`'ı eziyordu → `[hidden]{display:none!important}`);
renkler soluktu (sRGB → doğrusal dönüşüm eklendi); 360 px'te eklem tablosunun servo sütunu harf harf kırılıyordu (`td` için `overflow-wrap:normal`,
tablo kendi kabında kayar); ipucu yazısı 360 px'te modelin üstüne biniyordu (gizlendi). Tam sayfa görüntüsü denendi; `captureBeyondViewport`
sayfanın başını sonda tekrarladı, okunamadığı için bölüm bölüm görüntüye geçildi (tam sayfa dosyaları silindi; ikisi de bu işte üretilmişti).

## 7. Dokunulan dosyalar (commit listesi; commit C'de) (→ §10: güncel liste orada)

Değişen: `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/demo_uret.py`, `tasarim/cad/viewer-template.html`.
Yeni: `planlama/d158/F9b-brief.md` (brief; izlenmiyordu, brief gereği girer), `tasarim/cad/lale158-model.js` (→ §10: artık commit'e girmez), `planlama/d158/F9b-dogrula.py`, `planlama/d158/F9b-envanter.py`, `planlama/d158/F9b-gunluk.md`,
`planlama/d158/F9b-goruntu-1400-ust.png`, `F9b-goruntu-1400-yan-seffaf.png`, `F9b-goruntu-1400-modul-on.png`, `F9b-goruntu-1400-korunan-eklem.png`,
`F9b-goruntu-1400-baski-maliyet.png`, `F9b-goruntu-1400-kararlar.png`, `F9b-goruntu-360-ust.png`, `F9b-goruntu-360-model.png`,
`F9b-goruntu-360-eklem.png`, `F9b-goruntu-360-maliyet.png` (hepsi `planlama/d158/`).
Okunan (yazılmayan): brief'teki kaynaklar, `rehber/veri/robot.glb`, `rehber/veri/rehber-veri.json`, `kod/ortak/eklem_sinirlari.json`,
`planlama/y2/Y2b-baski.json`, `planlama/proje-plani.md`, `tasarim/cad/robot_cad.py`, `tasarim/freecad/rehber/rehber_uret.py` (CDP yöntemi).
Takma ad ve yerel kullanıcı klasörü yolu: yeni/değişen dosyalarda 0 (doğrulama [6] yol desenini denetler; takma ad kabukta arandı, 0).

## 8. Karar taslakları

- **KT-F9b-1 · `main`'e birleştirme:** `main`'e birleştirme (GitHub Pages; kök `index.html` bu sayfaya yönlendiriyor) **Ahmet onayına bağlı**.
  Seçenekler: a) onaydan sonra birleştir; b) P9.3 sonuç raporuyla birlikte birleştir. Önerilen: b. Yalnız öneri.
- **KT-F9b-2 · Model kopyası depoya girsin mi:** `tasarim/cad/lale158-model.js` 3,4 MB (herkese açık depo). a) gir (sayfa kendi başına açılır;
  güncellik doğrulamada); b) kopya yerine `../rehber/veri/robot-glb.js`'e göreli bağlantı (çift kayıt yok; F7b biçimine bağımlı).
  Önerilen: a. Yalnız öneri. **Karar (düzeltme turu 1, orkestratör): b.** Uygulama §10.
- **KT-F9b-3 · `maliyet.json` eski metinleri (iş, karar değil):** `notlar[0].t` "Demodaki 3B model eski CadQuery V3 (125 cm)" artık yanlış;
  8 kalem notu (`kalemler` 5, 8, 14, 19, 33, 92, 107, 139) 1,65 m ölçülerine dayanıyor (ör. 8: kabuk braket adedi "1,65 m CAD", 19: kablo
  boyları). `maliyet.json` sahibi (P8 izi) gözden geçirsin; değişince `demo_uret.py` koşulur.
  Düzeltme turu 1 ile genişletildi:
  - Kafa ekranı ve Nextion kalemleri: `kalemler[33]` (Yüz ekranı, Waveshare 10.1" HDMI LCD (B), "CAD'deki tahmini model") CAD'deki QLED ile
    çelişiyor; `kalemler[36]` (Ekran kablosu: "Nextion UART olduğu için HDMI adedi 1 (yalnız 7" yüz ekranı)") ve `kalemler[78]` (Direnç seti:
    "Nextion RX") Nextion'a dayanıyor, `notlar[1]` ise "Nextion kaldırıldı" diyor. Sayfa üçünü işaretliyor (§10); metnin düzeltilmesi
    `maliyet.json` sahibinde, kalem 33'ün alınıp alınmayacağı K32'ye bağlı.
  - K numaralama çakışması: `maliyet.json` K3'ü eski numaralamayla akü için kullanıyor (`notlar[4]` "Akü Victron SuperPack 12,8/20 (K3)";
    akü kaleminin notu "K3 (14 Ekim 2026), akü raporunun 1. tercihi"). Karar kuyruğunda K3 "Düz zeminde elde yük sınırı". `maliyet.json`'daki
    K numaraları kuyrukla çakışıyor; sayfada iki ayrı "K3" görünüyor. Sahibi eski numaraları ayırt edilir biçimde yazsın (ör. önek).
- **KT-F9b-4 · Depodaki `CLAUDE.md` (iş):** 12–13. satırlar "demo `robot_cad.py`'den üretilir, arayüz `viewer-template.html`" diyor; artık demo
  `demo_uret.py` + 1,58 m kaynaklardan üretiliyor. Aynı dosyada K25 (takma ad) açık; ikisi birlikte düzeltilebilir. Bu pakette dokunulmadı.
  Düzeltme turu 1 ile genişletildi; aynı eski demo tarifi iki yerde daha var (F9b'nin yazma alanı dışında, dokunulmadı):
  - `README.md:21`: "Eski CadQuery 3B montajı (V1 / V2 / V3, 125 cm); devrilme, motor ve servo hesabı canlı".
  - `planlama/proje-plani.md:235`: "`demo_uret.py` yalnız maliyet sayfasını üretir".
  Üçü birlikte güncellenmeli: demo 1,58 m FreeCAD montajını rehber dosyalarından gösterir, sayıları `demo_uret.py` kaynak JSON'lardan alır.

## 9. Açıklar

- 3B görünüm three.js r128'i CDN'den yükler; çevrimdışı açılışta model görünmez (sayılar ve maliyet görünür, "3B görünüm açılamadı" yazar).
- Maliyet toplamı açık kararlara bağlı (K28, K32, K34, K42); sayfa bunu yazıyor, toplam bugünkü satırlarla.
- `F9a` brief'i kütleyi 25.910,6 g diye anıyordu; güncel `montaj-analiz.json kutle_g` 25.720,55 g (çarpışma taraması 25.720,6). Sayfa güncel olanı gösterir.
- ~~`montaj-analiz.json bom_ozet.Satin.adet` 191, `parcalar[tur=Satin]` 210; sayfa parça listesinden sayar (toplam 1.179 tutuyor). Fark BOM
  gruplamasından olabilir; incelenmedi.~~ **Kapandı (düzeltme turu 1, O-2):** B'nin incelemesine göre fark 19 katı: `ana_montaj.py`
  "(" ile başlayan adları alım listesine (BOM) yazmıyor; bunlar 10 servo çıkış mili ve 9 rulman bileziği, satın alınan bir parçanın parçası
  olarak ayrı katı modellenmiş. Sayfa artık "satın alınan 210 katı (alım listesinde 191 adet; fark servo çıkış milleri ve rulman
  bilezikleri)" diyor; 191 `bom_ozet.Satin.adet`'e bağlı `p_satin_bom` anahtarından gelir. Kırılım 1.179'a tutsun diye 210 kaldı.
- Regresyon etiketi "Tilt servo payı, ±15" JSON'daki gibi gösterilir; eklem aralığı ±13 (pay ±15'te hesaplanmış, tutucu taraf).
- Parça renkleri `rehber-veri.json`'un `r` sınıfından; F6b C notundaki `baski-analiz.json` malzeme alanı sorunu bu sayfayı etkilemez.
- `rehber/veri/robot.glb` F7b'de yeniden üretilirse `F9b-dogrula.py` [4] 1 döner → `py -3 tasarim/cad/demo_uret.py` yeniden koşulmalı (C, F7b
  bittikten sonra bir kez daha koşsun). (→ §10: model artık göreli bağlantı; GLB değişimi kopya eskitmez. Yine de `glb_dugum`, `glb_ref`,
  `rehber_adim` gibi sayılar rehber dosyalarından gelir; F7b'den sonra `demo_uret.py` ve doğrulama bir kez koşulmalı.)
- Eski kaydırıcılı devrilme/motor/servo hesabı (eski modelin parametrik oyuncağı) 1,58 m için yeniden kurulmadı; kaynak JSON'larda karşılığı yok.

## 10. Düzeltme turu 1 (B kontrolü `planlama/d158/F9b-kontrol.md`: KOŞULLU GEÇER, kritik 0, orta 3, düşük 7)

Kurallar aynı: commit / push / merge yok, F7b alanına yazılmadı, FreeCAD yok. **Bu turda hiçbir dosya silinmedi.**

| Madde | Yapılan | Yer |
|---|---|---|
| O-1 (zorunlu) | Maliyet satırlarına sayfa katmanında işaret: kalem 33 (Yüz ekranı, Waveshare 10.1" LCD (B)) altına "F9b notu: K32'ye bağlı; CAD'deki kafa ekranı QLED 10,1"" (metinde elle rakam yok; 10,1 `kafa_in` anahtarından `data-k` span'i olarak gelir); kalem 36 (Ekran kablosu) ve 78 (Direnç seti) Nextion notlarına "eski tasarım notu". `maliyet.json`'a dokunulmadı. Üretici her işaret için kalem adını ve notta aranan metni ("LCD (B)", "Nextion") denetler; `maliyet.json` kayarsa üretim durur. | `demo_uret.py` `KALEM_ISARET`, `kalem_isaret()`; şablon `eski(t,i)`, `duz(i)`; doğrulama `ISARET` |
| O-1 denetimi | `F9b-dogrula.py` [6]: gömülü listede üç işaret ve kalem adları; [8]: 1400 ve 360 px DOM'da kalem 33'ün F9b notu metni (sayı `data-k`'ya bağlı) ve 36 / 78'in `eski tasarım notu` etiketi. | [6], [8] |
| O-2 (zorunlu) | Parça kartı: "satın alınan 210 katı (alım listesinde 191 adet; fark servo çıkış milleri ve rulman bilezikleri)". 191 yeni `p_satin_bom` ← `montaj-analiz.json bom_ozet.Satin.adet`. §9'daki açık kapatıldı. | şablon KPI; `SAYILAR` |
| KT-F9b-2 = b | Sayfa modeli `../rehber/veri/rehber-veri.js` ve `../rehber/veri/robot-glb.js`'ten `<script>` ile yükler (`window.REHBER_VERI`, `window.REHBER_GLB`; `file://`'da çalışır). Parça bilgisi düğüm adıyla `parcalar`'dan eşlenir. Üretici artık `lale158-model.js` üretmez; yalnız dosyaların varlığını ve her GLB düğümünün `parcalar`'da olduğunu denetler. | şablon; `demo_uret.py` `model_bilgi()` |
| KT-F9b-2 doğrulama | [4] dosyaların o anki hâlini okur, sabit sha yok: sayfa iki `<script src>`'yi yüklüyor; `robot-glb.js` içindeki GLB = `robot.glb` (bayt bayt); `rehber-veri.js` = `rehber-veri.json`; 1.192 düğümün hepsi `parcalar`'da; gömülü düğüm sayısı = GLB. Sayfa eski kopyaya bağlıysa hata. | [4] |
| Artık dosya | `tasarim/cad/lale158-model.js` (3,4 MB, ilk turda üretildi) **silinmedi**, diskte artık olarak duruyor. Takip dışı; commit'e girmez, sayfa ve doğrulama onu kullanmaz. Silinmesini C ya da Ahmet değerlendirir. | — |
| D-2 | "{{glb_ref}} gösterim parçası ({{glb_kablo}} kablo yolu ve ana anahtar düğmesi)" → sayfada "13 gösterim parçası (12 kablo yolu ve ana anahtar düğmesi)". 12 yeni `glb_kablo` ← `rehber-veri.json parcalar[tur=Referans][r=kablo]#say`. | şablon model notu |
| D-4 | Günlüğün 3. satırı düzeltildi: silme olayı kural dışı tek silme olarak anlatıldı. | baş kısım |
| D-3 | §7 listesine `planlama/d158/F9b-brief.md` eklendi. | §7, aşağıdaki liste |
| D-5 | KT-F9b-4'e `README.md:21` ve `planlama/proje-plani.md:235` eklendi (dosyalara dokunulmadı). | §8 |
| D-7 | KT-F9b-3'e kalem 33 / 36 / 78 ve `maliyet.json`'daki K3 numaralama çakışması eklendi. | §8 |
| D-1 (önerilen) | Brief sayıları farklıysa artık hata (önceden "BILGI"). Ek olarak `data-ui` muafiyeti daraltıldı: yalnız `secenek` ve `secim` içinde bağsız sayı olabilir; `eski` / `duzeltme` içindeki sayı `data-k`'ya bağlı olmalı (yeni F9b notunun 10,1'i bağsız kalmasın diye). | [6], [2] |
| D-6 (önerilen) | `main()` başında `sys.stdout.reconfigure(encoding="utf-8")`; çıktı dosyaya yönlendirildiğinde çökme yok (bu turun koşuları dosyaya yönlendirildi, rc 0). | `F9b-dogrula.py` |

**Bozma sınaması** (scratchpad betiği; sayfa bellekte değiştirildi, depoya yazılmadı; `--tarayicisiz`): değişiklik yok → rc 0; kalem 36
işareti yok → rc 1; kalem 33 türü "eski" → rc 1; `data-ui="eski"` içinde "1.590 mm" → rc 1; `data-ui="duzeltme"` içinde "7 inç" → rc 1;
`<script src>` eski kopyaya çevrildi → rc 1; gömülü düğüm sayısı 1.191 → rc 1.

**Komutlar ve çıkışlar**

```
py -3 tasarim/cad/demo_uret.py                       → 0 (127 anahtar, 14 karar, 153 kalem; model göreli, 1.192 düğüm)
py -3 planlama/d158/F9b-dogrula.py --goruntu         → 0, "SONUC: GECER (hata 0)"
    [1] 127 anahtar, sayfada 130 bağlı eleman   [2] statik 119 bağlı, 5 muaf (secenek), 0 bağsız
    [3] maliyet aynı (153 kalem); sayfa kuralı 121 kalem, ara 103.188,02, genel 118.666,22 TL
    [4] robot-glb.js GLB 2.559.336 bayt = robot.glb (o anki sha256 760bf1ff5955); rehber-veri.js 1.192 parça = rehber-veri.json
    [5] 14 karar, 33 etiket, hepsi açık   [6] eklem = kod/; brief sayıları aynı; işaretler kalem 33 / 36 / 78
    [8] 1400 ve 360 px: konsol hatası 0, data-hazir=1, scrollWidth = innerWidth; data-k 131, data-mk 978, 1.638 bağlı, 5 muaf, 0 bağsız;
        maliyet işaretleri kalem 33 F9b notu, 36 ve 78 eski tasarım notu; 1,65 eşleşmesi 23 (hepsi maliyet.json metni, ilk turla aynı)
py -3 tasarim/freecad/carpisma_kos.py kontrol        → 0 ("izlenen 17 dosyanin ozetleri kayitla ayni")
py -3 planlama/d158/regresyon.py --yazma             → 0 (GEÇER, kötüleşen yok)
```

**Görüntüler:** 10 PNG bir kez yenilendi (`planlama/d158/F9b-goruntu-*.png`, 4'ü 360 px); `1400-ust`, `360-ust`, `360-model` Read ile bakıldı:
parça kartında yeni etiket, model notunda "13 gösterim parçası (12 kablo yolu ve ana anahtar düğmesi)", 3B model göreli dosyalardan çizildi.
Maliyet satırları ayrıca scratchpad'e çekildi (kalem 33 / 36 / 78, 1400 ve 360 px; depoya girmez): kalem 33'te turuncu F9b notu,
36 ve 78'de "eski tasarım notu" etiketi görünüyor; 360 px'te taşma yok.

**Commit listesi (güncel; commit C'de):**
- Değişen: `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/demo_uret.py`, `tasarim/cad/viewer-template.html`.
- Yeni: `planlama/d158/F9b-brief.md`, `planlama/d158/F9b-dogrula.py`, `planlama/d158/F9b-envanter.py`, `planlama/d158/F9b-gunluk.md`,
  `planlama/d158/F9b-kontrol.md` (B), 10 × `planlama/d158/F9b-goruntu-*.png`.
- Girmez: `tasarim/cad/lale158-model.js` (artık).
- Sıra (B'nin O-3'ü, model artık göreli olduğu için daha da gerekli): F7b'nin `rehber/veri/` commit'i önce ya da aynı anda; ardından
  `py -3 tasarim/cad/demo_uret.py` ve `py -3 planlama/d158/F9b-dogrula.py` → 0.

**sha256 (ilk 12, bu turun sonunda):** `Robot-Tasarim-Demosu.html` 9613ce541bb3, `demo_uret.py` a600852640c9,
`viewer-template.html` eed41f6bec3d, `F9b-dogrula.py` 12c608a40019.
