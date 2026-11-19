# F10u günlüğü: P10.7b2k, CAD'den bağımsız rehber uyumu (paralel CAD paketi P10.7b2j için)

DURUM: KAYNAK BİTTİ (19.11.2026 06:35), birleşme / üretim / zincir / commit YOK (brief gereği). Taban `lale-duzeltme` = `896c9a7`.

Brief: P10.7b2j (paralel CAD worktree'si, dal `lale-cad-b2j`, taban `8bca2f5`, bu günlük yazılırken `456b723`; tasarım
`F10s-gunluk.md`, kontrol `F10t-gunluk.md` SÜRÜYOR) birleşince rehber ve ölçü / kayıt zinciri üretilebilsin diye CAD'den bağımsız
kaynak değişiklikleri ana ağaçta hazırlanır. CAD model kaynağına (`tasarim/freecad/` altında taban, kafa, kabuk, `arayuz.py`,
`kafa10_lib.py`, `taban_parcalar.py` …) dokunulmadı; ses kartı yaması uygulanmadı; FreeCAD koşusu yok; worktree yalnız okundu
(dal nesneleri ana depodan `git show` / `git archive` ile okundu, worktree'de komut koşulmadı).

## 0. Başlangıç

- `git status --short`: 19 eski kir (13 kabuk PNG'si, `montaj/yerlesim-kontrol.json`, kökte `geometri2_cikar.py`, `geometri2_dogrula.py`,
  `geometri_cikar.py`, `gez.js`, `uc.js`); dokunulmadı.
- Temel sınamalar (06:00 dolayı): `rehber_denetim.py --kaynak` 0, `rehber_kablo.py` GEÇER, `F10l-birlesim.py` GECER,
  `kablolar_denetim.py` GEÇER. Boş bellek 5,6 GB (sonda 5,1 GB).
- Dal karşılaştırması: `git diff --name-only 8bca2f5 lale-cad-b2j` (75 dosya) ile `8bca2f5 896c9a7` (317 dosya) ortak dosya 0; bu
  paketin değiştirdiği 16 dosyanın hiçbiri b2j'de yok → **metin çakışması beklenmez** (§ 7.1).

## A. Rehberin CAD kalemlerine uyumu (F10s sonu, F10t § 6)

- **A1 B6 / K53 a (bitti):** B6 not_ "karar bekliyor" yerine çentik: "Elektronik katının arka kenarında (güç paneline bakan kenar), robota
  önden bakınca solda 1,5 mm derin çentik var (K53 a) …; iniş boyunca ortak hacim 0, en küçük boşluk 0,5 mm (`F10s-K53-olcum.json`; ölçüm
  düz yukarıdan inişle, eğik iniş ölçülmedi)". Yer `arayuz.TABAN["kat_on_centik"]` (x −136…−60,75; dalda). Kilit `ZORUNLU` "B6 K53 a çentik".
- **A2 E3a / K51 a (bitti):** "D24V50F5 → Pi hattındaki bugün modelde ve BOM'da yok …" → "SY8205 → QLED hattındaki ve D24V50F5 → Pi
  hattındaki, ikisi de modelde ve BOM'da var (K51 a)". not_: iki TVS'nin tabla yeri modelde; çeviricilerin çıkış ucunun kart üstündeki
  yeri modelde yok, lehim yeri kart yazısıyla teyit (F10t § 1.5: D24V50F5 çıkış ucu yönü doğrulanmadı). `ZORUNLU` adı ve K51 deseni
  yenilendi; BILESEN'deki "TVS P6KE6V8A" deseni iki parçaya da uyar.
- **A3 B5a / K1 17.1 / K64 a (bitti):** B5a is_'e montaj paragrafı (F10s § 4 + F10t § 1.2 sırası): ısıl gömme somunlar tezgâhta; 9
  saplama alttan altıgen cebe, somun elle; tutucular (yıldız önde, akü kablo yarıklarının arkasında; anahtarlı onun arkasında, röle
  hizasında) panel burçlara inmeden, altı açıkken, 2 × ISO 7380 M3×10 ile alttan; saplama numarası robota önden bakınca soldan sağa;
  saplama panele değmez. Kontrol satırı eklendi. not_ "henüz tasarlanmadı" → modele girdi + VARSAYIM'lar (altıgen baş, cep toleransı) +
  alımı teyit edilecek bağlantı elemanları. K1 17.1 "Karede görünmez: iki bara ve tutucuları modelde yok" → numara yönü, **sıkma ve
  yeniden sıkma**, U06 şeridi notu, "karede tutucular görünür; pabuç ve köprüler modelde yok". Kilitler: 5 yeni B5a, 2 yeni K1 `ZORUNLU`.
- **A4 bara vekili (bitti, Echo kararı 1–2):** şemalarda bara artık modelli tutucuyla sınanır; CAD yolları da (düzeltme turu 1, § 9).
  `UC_ETIKET` "Anahtarlı bara" / "Yıldız barası" → `^Bara tutucusu anahtarli bara` / `^Bara tutucusu yildiz barasi` (UC_MODELSIZ'den
  çıktı); `SEMA_KONUM` iki vekil; `sema_parcalari` "Bara tutucusu " parçalarını (tür Baski) modelli sayar; `SEMA_MODELLI_VEKIL`
  (şema adında "yeri yaklaşık" istenmez). G16 / G22 şeması anahtarlı baranın kendi saplamasından (`kablo_yolu_taban.BARA`,
  `bara_saplama`; kablolar.json yerleşimi: G16 2., G22 4.), panel üstünde y 195'te yatay, yıldızın saplamalarının arasından, U06
  şeridinin altından. Yeni sınama `bara_tutarlilik` (BARA ↔ `arayuz.TABAN["bara_tutucu"]`, numara ↔ yerleşim). SEMA adları ve K1 kablo
  notu güncellendi; `sema_boy` G16 240 → 160, G22 240 → 259 (`--sema-boy-yaz`; `kablolar_uret.py` ile `kablolar.md`). K1 17.1'e
  `odak=("Kablo yolu 2:", "Bara tutucusu")` (köprü uç etiketleri artık tutucunun kutusunda; kadraja sığsın).
- K64 alım fazlaları (9 M5 pul, 4 M3×10 ISO 7380, 4 M3 ısıl gömme somun, saplama baş tipi altıgen): yalnız "Ahmet'e sorulacak" notu
  (karar kuyruğu K64; rehber B5a not_ "satın alma listesinde ayrıca teyit edilir"); `maliyet.json`'a dokunulmadı.

## B. USB ses kartının CAD'den bağımsız bağımlılıkları (bitti)

Karar metni (karar kuyruğu 14.11 kaydı, `kablolama-on-kararlar.md` § 5 Ö1): kart kablajdan çıktı, yedek olarak siparişte kalır, takılmaz;
KT2 geçmezse Pi port 2'ye. Yamadan sonra çizimde de yok.

- `rehber_metin.py`: E4 is_ ve 31.3 alt adımı "USB ses kartı takılmaz, çizimde de yok: kart yedek parçalarla birlikte saklanır (KT2 …)";
  31.4'ün "ikinci kart" cümlesi kalktı; sira adı / `desen` / `saydam` / `gizli_ok`'tan kart çıktı; not_ "Modelde kart hâlâ çizili" →
  "P10.7b2j'de modelden çıkarıldı"; `AD_CEVIRI`'den üç kart çevirisi çıktı; SEMA ve E3a / E4 yorumları.
- `rehber_denetim.py`: `BILESEN`'den kart; `TERIM_ISTISNA`'dan beş ölü cümle (biri yeni cümleyle değişti); E4 `ZORUNLU` deseni; yeni
  `KALKAN_PARCA` (veride "USB ses kart" adlı parça varsa zorunlu eksik: yama uygulanmadan üretim yakalanır).
- `rehber_secici.py`: `_KAFA_KABUK`'tan "USB ses karti", "Kopuk bant (USB ses" (F10t § 6 madde 7).
- `kablo_yolu_ekran.py`: "Ses karti uzatmasi" ve "3,5 mm -> PAM" yolu, `KABLO` girdileri, Pi port 2 yorumu. Kafa içi kablo kütlesi
  6,5 + 0,5 = 7,0 g azalır (`kafa_ici_kablo_kutle`; `kafa_montaj` KABLO_EK, `hat_secenek` okur).
- `rehber_kablo.py`: `SEMA_ESLEMESIZ_MUAF` boş; bozma b66 "kaynakta olmayan yolun muafı" oldu.
- `uygulama_olc.py` (yalnız PAM ölçülür, Pi port 2 "bos (yedek)"), `uygulama_metin.py` (kart ölçüsü varsa yazılır, yoksa "modelde yok";
  K_YENI'den iki yol; LISTE_DISI, VARSAYIM), `uygulama_rapor.py` (K_BILGI, K_AD, PORT, GOR), `uygulama_gorsel.py` (kart etiketi).
- `kafa_rapor.py` (metin): kart "yedek, modelde yok"; ses ReSpeaker 3,5 mm → bölücü → PAM8403; iki TVS. `kafa_lib.py` / `kafa_parcalar.py`
  yorumları çarpışma taramasının izlediği kaynak olduğu için değiştirilmedi.

## C. P10.7b2i kontrolünden açık işler

- **D4 (bitti):** `geometri_denetle` kullanılan `GEO_ISTISNA`'yı izler, kullanılmayanı HATA sayar; bozma b99 (`CAD_KIRP[9]` dururken
  `GEO_ISTISNA[9]`).
- **D5 (bitti):** `u06_port_denetle`: `ESP_PORT` ESP32 DevKit kutusunun +x yüzünde (±0,5 mm, y / z kutuda), U06 son noktası port ağzının
  2,5 mm önünde (±0,05). Bozma b103. (Brief'teki "≤ 5 mm" eşiği yerine iki sıkı koşul: port yüzde ve şema portta.)
- **D7 (bitti):** onay girdisi `cad_kirp_metin` ile ("son 3 kesim (0, 0.7071, 0.7071) · p ≤ 143.92 · …"); onay kaydı yenilendi.
- **B1 (bitti):** B6a is_'e DevKit yönü (micro USB portu önden bakınca sağda, WROOM solda; ters takılırsa pinler yer değiştirir, U06 porta
  ulaşmaz) + kontrol satırı + `ZORUNLU`; K1 madde 7'deki ikinci "Yukarısı K2'de." kalktı. Yön `taban_lib.esp_local()`'dan (port +x ucunda).
- **Açık kaldı:** D3 (`uygulama-olcum.json` ESP32 USB 971 / 1360: FreeCAD `uygulama_olc` koşusu ister; § 7.2'de), D6 (`{boy.U06}` yer
  tutucusu: `rehber_deger`'e yeni tür + `elektrik.md`; bu pakette brief'in "zorlama" sınırıyla bırakıldı), 17.11 karesinde U06 (kare /
  sema_ok, üretim ister).

## D. Karar kuyruğu (bitti)

K2, K51, K53, K64'e "Uygulama (19.11.2026): P10.7b2j'de modele girdi (F10s § n, kontrol F10t § 1.x)" + rehber uyumu (bu günlük);
K52'ye "P10.7b2j'de de model hâlâ yok"; K64'e alım sorusu ve "CAD yolları eski noktada" açık işi; "P10.7b2'ye" bölümündeki USB ses kartı
maddesine yama durumu; son bölüme D4 / D5 / D7 / B1 yapıldı, D3 / D6 / 17.11 açık.

## Echo kararları (geri alınabilir)

1. ~~**CAD yolu sınaması eski vekilde kalır**~~ **Düzeltme turu 1'de geri alındı** (F10u-kontrol 1): yollar tutucuların ve
   saplamaların içinden geçiyordu ve hiçbir sınama yakalamıyordu. Yollar CAD dalında taşınıyor; `MODELSIZ_KONUM` iki bara için artık
   tutucu kutusu, girişim `bara_yol_denetle`'de (§ 9).
2. **Şemalar tutucuyla** (SEMA_KONUM vekili, `sema_parcalari` istisnası): şema bizim kaynağımız, model artık doğru yeri gösteriyor.
   Şema ölçüleri `kablo_yolu_taban.BARA`'da sabit (arayuz'da `bara_tutucu` olmadan da içe aktarılsın diye), `bara_tutarlilik` modelle eşitler.
3. **Saplama numarası = modeldeki sıra (x artan) = robota önden bakınca soldan sağa** (F10t de böyle numaralıyor); B5a'da tanım, K1'de anma,
   `bara_tutarlilik` artan sırayı sınar.
4. **Yama uygulanmadan üretim durur** (sessiz geçiş yok): `AD_CEVIRI` / `TERIM_ISTISNA` girdileri kalktığı için kartın CAD adı terim
   kuralına takılır; `KALKAN_PARCA` veride ikinci kez yakalar.
5. **D5 eşiği** "≤ 5 mm" yerine yüz + 2,5 mm koşulu (C).
6. **Tork** "≈ 2–2,5 N·m (tahmin, ölçülmedi)" F10t § 1.2'den; metin "yaylı pul düzleşene kadar" ölçütünü öne koyar.
7. `kafa_rapor.py` metni değişti (kafa/ altında ama model kaynağı değil, taramanın izlediği listede yok).

## Güvenlik / enerji sırası (ayrıca işaretli)

Düzeltme turu 1'de düzeltildi (F10u-kontrol 3, 4). İlk yazımdaki "F5 'enerjiden önce' listesine" önerisi yanlıştı: ilk enerji F1'de
("İlk enerji, aşama 1", kafasız), F5 aşama 2.

- **F1 (yeni kontrol maddesi, "İlk enerji, aşama 1"in hemen önünde):** akü XT60'tan ayrık, ana anahtar kapalıyken iki baranın dokuz M5
  somunu yeniden sıkılır; saat / yüzük çıkar, anahtar iki baraya birden değmesin (anahtarlı (+) ile yıldız eksenleri 60 mm arayla:
  lokma anahtar köprü kurabilir). İlk hafta sonu aynı koşullarla bir kez daha. K1 17.1 bu maddeye gönderir. Kabuk ve etek takılıyken
  panele üstten erişim **ölçülmedi** (metinde çekince, karar kuyruğu K64'te açık iş).
- **F1 (yeni kontrol maddesi):** enerjiden önce ESP32 DevKit yönüne bakılır. B6a'nın sonucu düzeltildi: ters takılınca taşıyıcının 5 V
  hattı bir GPIO pinine gelir ve F4 takılınca (F1 aşama 1) kart zarar görür; eski "USB fişi porta ulaşmaz" güvencesi kalktı.
- B5a montaj sırası (tutucu panel altı açıkken) enerji sırasını değiştirmez.

## 5. Sınamalar (PYTHONIOENCODING=utf-8, `py -3 -B -X utf8`; ana ağaçta ve depo dışı birleşim benzetiminde)

Benzetim: karalama klasöründe `git archive 896c9a7` (tasarim/freecad, planlama, rehber) + bu paketin 16 dosyası + `git archive
lale-cad-b2j` ile dalın değiştirdiği tasarim / planlama dosyaları. Yama uygulanmadı (FCStd yeniden üretilmedi).

| Sınama | Ana ağaç | Benzetim (birleşmiş) |
|---|---|---|
| `rehber_denetim.py --kaynak` | çıkış 1: yalnız 3 terim (kartın CAD adı / kodu; beklenen, Karar 4); onay farkı 0, ASCII 0, zorunlu eksik 0 | aynı 3 terim (yama + üretimle kalkar) |
| `rehber_denetim.py --bozma-denemesi` | 305 / 305, bozulmamış kaynakta hata 0 | — |
| `rehber_kablo.py` | KALDI 9: bara tutucusu yok (`bara_tutarlilik`, G16 / G22 vekil ve uç, 2 uç etiketi) | **GEÇER** (G16 / G22 iki yan + iki uç tamam, uç etiketi hata 0) |
| `rehber_kablo.py --bozma-denemesi` | 103 / 103 (temel kırmızı olduğu için anlamsız) | **103 / 103**, yeni beşi kendi iletisiyle (b66, b99–b103) |
| `F10l-birlesim.py` (taban 896c9a7, yeni liste) | GECER | — (git ister) |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / GEÇER | — (git ister) |

Birleşmeye kadar kırmızı kalması beklenenler: `rehber_kablo.py` (9 hata, hepsi "bara tutucusu modelde yok" kökenli) ve
`rehber_denetim.py --kaynak` (3 terim, yama + FreeCAD üretimi gerekir). Beklenmeyen kırmızı yok.

Ek gözlem (benzetim): b2j modelinde `rehber_gorunum.cad_parcalar()` 1240 parça (ana ağaçta 1192; +46 taban, +2 TVS); yamayla kart ve
bandı çıkınca **1238** beklenir. Kafa parça kimlikleri yama sonrası değişmez (TVS kartın hemen önüne girer, kart + bant çıkar):
F10a / F10e'deki sabit kimlikler (p0750, p0762, p0781, p0440) yerinde. Tutucu, saplama, pul, somun, M3 vida ve ısıl gömme somunlarının
grubu FCStd'de `Guc_aku_surucu_panel` ve y_min ≥ 172,85 olacağı için B5a'nın ilk kuralına düşer (benzetimde analiz grubu "Guc" ile
denendi; gerçek grup üretimde doğrulanır).

## 6. Dokunulan dosyalar (16)

`planlama/adim3/kablolar.json` (yalnız G16 / G22 `sema_boy`), `planlama/adim3/kablolar.md` (üretilen), `planlama/d158/F10l-birlesim.py`
(`BEKLENEN["896c9a7"]`, varsayılan taban), `planlama/d158/karar-kuyrugu.md`, `planlama/d158/F10u-gunluk.md` (bu),
`tasarim/freecad/kafa/kafa_rapor.py`, `tasarim/freecad/lale158/kablo_yolu_ekran.py`, `kablo_yolu_taban.py`,
`tasarim/freecad/lale158/kafa-yerlesim/uygulama_gorsel.py`, `uygulama_metin.py`, `uygulama_olc.py`, `uygulama_rapor.py`,
`tasarim/freecad/rehber/rehber_denetim.py`, `rehber_kablo.py`, `rehber_kritik_onay.json` (yenilendi, 62 fark), `rehber_metin.py`,
`rehber_secici.py`.

## Birleştirme ve kapanış tarifi

Düzeltme turu 2'de güncellendi (19.11.2026). Temel `F10r-gunluk.md` § 7–8 (arka plan kalıbı, `.durum`, sık okuma, FreeCAD kilidi
`FREECAD-KILIT.txt`, bellek ≥ 2,5 GB). Her adımın geçme ölçütü yazılı; bir adım kırmızıysa sonrakine geçilmez (7.9).

### 7.1 Yapıldı: birleştirme ve montajlar (`F10w-gunluk.md`)

CAD dalı (uç `06b2ed9`: yollar bara saplamalarına taşındı, ses kartı yaması) ana ağaca `git merge --squash` ile alındı, **commit'siz**
(dalın ara commit'leri taşınmadı). Kafa / taban / ana montaj, baskı zinciri ve görseller birleşik ağaçta yeniden üretildi. CAD
değişikliği index'te (staged), b2k değişikliği çalışma ağacında (unstaged); üretimin yeniden yazdığı dosyaların bir kısmı ikisinde de
("MM").

### 7.2 Sürüyor: tam çakışma taraması (`F10x-gunluk.md`)

Tarama ajanı önce `lale158_kontrol` ve `uygulama_olc` → `uygulama_rapor` koşar (D3: ESP32 USB 1.129 / 1.560 gelmeli), sonra
`carpisma_kos.py` tam koşu (≈ 4 sa), sonra `carpisma_kos.py kontrol` → 0. Koşarken izlenen dosyalara (`arayuz.py`, `*_lib.py`,
`*_parcalar.py`, `*-analiz.json`, montaj çıktıları) dokunulmaz, başka FreeCAD koşturulmaz. Geçme: F10x DURUM "BİTTİ", kontrol 0.
Sonra D3: `uygulama-olcum.json` / `uygulama-notu.md` yeni değerlerle kayıt ve notlarla (karar kuyruğu D3) tutarlı mı bak, kapat.

### 7.3 Tarama sonucu

Kontrol 0 değilse: çakışan çiftler F10x'te; kaynak düzeltmesi CAD işi (yeni tur), rehber kapanışı durur.

### 7.4 FreeCAD veri adımlı tam üretim

- Ön sınama (saniyeler): `rehber_denetim.py --kaynak` **çıkış 0** (onay farkı 0), `rehber_kablo.py` **GEÇER**, `F10l-birlesim.py`
  GECER, `kablolar_denetim.py` GEÇER. (Düzeltme turu 2'de dördü de böyle; değiştiyse önce sebep.)
- Üretim: `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` (veri adımlı, `--veri-yok` yok; arka planda `AD=uret`, ≈ 45–50 dk).
  Geçme: "BITTI cikis 0"; parça sayısı `rehber_gorunum.cad_parcalar()` ile aynı (benzetimdeki tahmin 1238; F10w montajından sonra
  gerçek sayı oradan okunur); "UYARI atanamadi" yok (tutucu takımı B5a'ya düşmeli); `odak` boş desen uyarısı yok; veride "USB ses
  kart" adlı parça yok (`KALKAN_PARCA`); PDF taşan 0.

### 7.5 Yeterlilik kanıtı

`rehber_kablo.py --veri rehber/veri/rehber-veri.json` GEÇER (uç etiketi: köprü etiketleri tutucularda); `rehber_denetim.py` (veri)
zorunlu eksik 0; `F10d-gizli-piksel.json`'daki "Köpük bant (USB ses kartı)" kaydı için F10d `--gizli` yeniden (31.3 `gizli_ok`'ta yalnız
PAM bandı).

### 7.6 Zincir 2–10

`F10r-gunluk.md` § 7.c tablosu aynen (2a, 2b, 3, 4 F10f, 5 F10e `--goruntu-yok`, 6 F10d `--goruntu-yok`, 7 F10a `--kanit-yok`, 8 F9b,
9 `carpisma_kos.py kontrol`, 10 `regresyon.py --yazma`; **`regresyon.py` argümansız koşulmaz**). 2b'de kaynak bozmaları 111
(`rehber_kablo --bozma-denemesi`), elektrik bozmaları 311.

### 7.7 Kare bakışı (gözle)

- 17.1 (iki tutucu ve köprü etiketleri kadrajda, saplama sırası, Kablo yolu 2 yıldız 3'te), B5a (tutucular, M3 vidalar), B6 (çentik),
  E3a (iki TVS), E4 / 31.3–31.4 (kart yok), 17.7 (Kablo yolu 9 yıldız 4'ten geçiyor).
- **Şema / tüp üst üste binmesi (F10u-kontrol T3):** 17.1, 17.4, 17.6 ve K2 32.1 karelerinde G16 / G22 şemaları CAD tüpleriyle aynı
  şeritte (merkezler arası 0,2–2,0 mm, tüp yarıçapı 2,5). Şemanın okunup okunmadığına bak; okunmuyorsa şema rengi / vurgu ya da
  kamera değişikliği önerisi günlüğe (model değil, gösterim sorunu).

### 7.8 Commit'ler, tarama, push (dosyalar adıyla, `git add -A` yok; 19 eski kir girmez)

- **Commit'ten önce (kapanış ajanı):** `F10v-gunluk.md` yol tablosunda yol 4'ün yabancı saplama uzaklığı "> 15 mm" → "6,0 / 6,1 mm
  (yıldız 3 civata / somunu)" (`F10u-kontrol.md` tur 2; karar kuyruğu K64 notu). Tarama sürerken bu dosyaya dokunulmaz.
- **`git add` yalnız tarama bittikten sonra**, dosyalar adıyla: ikinci commit'te `git add -A` / `git add .` kullanma (19 eski kir dosyası
  girer: 13 PNG `tasarim/freecad/kabuk/gorsel/`, `montaj/yerlesim-kontrol.json`, kökteki beş betik).
- **İki commit ayrılabilir:** CAD squash'ı index'te, b2k çalışma ağacında. Sıra: (1) index olduğu gibi → "Lale P10.7b2j: K2 boss,
  K53 çentik, K51 TVS, K64 bara tutucuları, CAD yolları saplamalara, ses kartı modelden çıktı (CAD)"; (2) b2k kaynakları (§ 6 ve § 9
  / § 10 dosyaları + bu günlük + kontrol dosyası) ve üretim / zincir çıktıları (`F10r` § 7.e listesi, "MM" dosyalarının çalışma ağacı
  hâli, F10w / F10x günlükleri) → "Lale P10.7b2k: rehber CAD paketine uyumlandı, bara yolu kilidi; P10.7b2j kapanışı (tam tarama,
  rehber yeniden üretildi)". (1) için önce `git diff --cached --stat` ile index'te b2k dosyası olmadığına bak; varsa (ya da "MM"
  dosyaları ayrılamıyorsa) tek commit, ileti ikisini birden söyler.
- Her commit'ten önce kancanın kalıplarıyla tarama (yalnız eklenen satırlar; kalıplar kancanın kendisinden okunur):
  `K=$(sed -n "s/^ *ara \"\(takma ad\|yerel yol\)\" \"-aEio\" '\(.*\)'$/\2/p" .git/hooks/pre-push | paste -sd'|'); git diff --cached -U0 | grep -aE '^\+[^+]' | grep -aEin "$K"`
  → boş olmalı. Çıktı varsa satırı düzelt (sahip "Ahmet", orkestratör "Echo"), `git add`, yeniden tara.
- Push'tan önce kancanın kendisiyle kuru koşu (push etmeden; kanca stdin'den aralık okur):
  `echo "refs/heads/lale-duzeltme $(git rev-parse HEAD) refs/heads/lale-duzeltme $(git rev-parse origin/lale-duzeltme)" | bash .git/hooks/pre-push; echo $?`
  → 0. Yalnız `robot-glb.js` base64 dizisine takılırsa F10r § 8'deki değerlendirme; başka bulgu varsa push yok: bulgulu yerel commit
  yeniden kurulur (`git commit --amend`; üstüne düzeltme commit'i yetmez, kanca geçmişteki eklenen satırı görür).
- Sonra push.

### 7.9 Bir adım kırmızıysa

Commit / push yok; log'un son 60 satırı + `.durum` bu günlüğe "Kapanış: KALDI" başlığıyla. `bara_tutarlilik` HATA verirse
`arayuz.TABAN["bara_tutucu"]` değişmiştir → `kablo_yolu_taban.BARA` aynı değerlere çekilir, `--sema-boy-yaz` + `kablolar_uret.py` +
onay yenileme + F10l listesi.

## Kontrol ajanının özellikle bakması gerekenler

1. G16 / G22 şemasının yolu (y 195, x −12,5 ve −37,5'ten yıldız saplamalarının arasından): pabuç ve somun zarfı ölçülmedi; şema
   gösterim, ama karede saplamaların içinden geçiyor gibi görünebilir.
2. B5a sırası: tutucuyu alttan M3 ile sıkmak için panelin altı açık olmalı; metin "panel burçlara inmeden" diyor, panelin B5a'da
   tezgâhta olduğu F10t § 1.2 ile tutarlı mı.
3. K1 17.1 "U06 yıldız barasının sağ yarısının önünden" ve "{saplama.G17} numaralı saplama" (4.) ifadesi şerit (x 14…40, z −40…−30) ile.
4. `KALKAN_PARCA` + `AD_CEVIRI` silinmesi: yama uygulanmadan üretim bilinçli olarak durur.
5. `SEMA_MODELLI_VEKIL` muafiyetinin genişliği (yalnız iki bara).
6. Güvenlik işaretli iki metin (yeniden sıkma, ESP32 yönü).

## 8. CAD tasarım ajanına: hangi yol hangi saplamada bitmeli

Kaynak: hedefler `planlama/adim3/kablolar.json` bara-pabuc `yerlesim` (rehber metnindeki `{saplama.X}` / `{bsaplama.X}` ile aynı kayıt),
yolların kabloları `rehber_kablo.CAD_ESLEME`, saplama eksenleri paralel CAD worktree'sindeki model (`arayuz.TABAN["bara_tutucu"]`,
`taban-analiz.json` "Bara civatasi M5x25 DIN 933 (…)" kutuları). Numara = x artan = robota önden bakınca soldan sağa.

Saplama eksenleri (x; z), y 179,8…208,3 (civata), pul + yaylı pul üstü y 191,7, somun üstü 195,7, tutucu gövdesi y 179,5…189,5:
yıldız (z −55) 1 (−50), 2 (−25), 3 (0), 4 (25), 5 (50); anahtarlı (z −115) 1 (−37,5), 2 (−12,5), 3 (12,5), 4 (37,5).
Şemalardaki uç noktası (saplamada biten yol için öneri): (x; 191,9; z + 5).

| Yol | Kablo (damar) | Bara | Saplama | Eksen (x; z) | Uç önerisi (x; y; z) | Bugünkü durum (benzetim) |
|---|---|---|---|---|---|---|
| 1 | G01–G04 (ana + hattı) | — | — | — | baraya uğramaz | noktalar[2→3] yıldız tutucusundan ve 3., 4. saplama takımından geçiyor |
| 2 | G05 (−, akü dönüşü) | yıldız | 3 | (0; −55) | (0; 191,9; −50) | tutucudan ve 4. takımdan geçiyor, (−20; 186; −90)'da bitiyor |
| 3 | G12 (+) | anahtarlı | 1 | (−37,5; −115) | (−37,5; 191,9; −110) | yıldız tutucusundan geçiyor, hiçbir saplamaya ulaşmıyor |
| 3 | G12 (−) | yıldız | 1 | (−50; −55) | (−50; 191,9; −50) | 〃 |
| 3 | G09 (+), G11 (+) | anahtarlı | 3 | (12,5; −115) | (12,5; 191,9; −110) | 〃 (yol bugün röleden çıkıyor) |
| 4 | G13 (+) | anahtarlı | 2 | (−12,5; −115) | (−12,5; 191,9; −110) | baraya ulaşmıyor (kontrol listesinde yoktu; sınama ister) |
| 4 | G13 (−) | yıldız | 2 | (−25; −55) | (−25; 191,9; −50) | 〃 |
| 5 | G14 (+) | anahtarlı | 1 | (−37,5; −115) | (−37,5; 191,9; −110) | röleden başlıyor, yıldız tutucusundan geçiyor |
| 5 | G14 (−) | yıldız | 1 | (−50; −55) | (−50; 191,9; −50) | 〃 |
| 7 | G15 (+) | anahtarlı | 1 | (−37,5; −115) | (−37,5; 191,9; −110) | röleden başlıyor, yıldız tutucusundan geçiyor |
| 7 | G15 (−) | yıldız | 1 | (−50; −55) | (−50; 191,9; −50) | 〃 |
| 8 | G17 (−; + damarı F3'ten) | yıldız | 4 | (25; −55) | yol 4. saplamanın ±12 mm'sinden geçer | anahtarlı 1 ve yıldız 1 takımından, tutucudan geçiyor |
| 9 | G18 (−; + damarı F4'ten) | yıldız | 4 | (25; −55) | 〃 | anahtarlı 4, yıldız 5 takımından, tutucudan geçiyor |

Sınamanın kuralı (`rehber_kablo.bara_yol_denetle`, 1 mm adım, tüp yarıçapı 2,5 mm): bir yolun noktası tutucu ya da saplama takımı
(civata, pul, yaylı pul, somun) kutusunun 2,5 mm içindeyse HATA; tek izin, yolun kendi bara damarının saplama ekseninin yatayda 12 mm
yakınında ve tutucu üst yüzünün üstünde (y ≥ 189,5; düzeltme turu 2, T2). Her bara damarının saplamasına yol bu bölgeden en az bir kez girmeli. Pratikte: tutucu üstünde yatay giden kısım
y ≥ 192,5 (y 195 önerilir, şemalar gibi), saplamalar arasından geçen kısım yabancı saplama ekseninden yatayda ≥ 6,5 mm. Yol 3'ün
tek bir yol olarak üç saplamaya (anahtarlı 1 ve 3, yıldız 1) uğraması gerekir; yol 5 ve 7'nin başı röle yerine anahtarlı 1'e taşınır
(`geometri_denetle` de G14 / G15'in a ucunu anahtarlı bara tutucusunda arar). Yol 8 ve 9'un + ucu sigorta kutusunda kalır.

## 9. Düzeltme turu 1 (F10u-kontrol: DÜZELTMEYLE GEÇER)

- **Bulgu 1 (YÜKSEK).** (a) `bara_yol_denetle` + `bara_yol_hedefleri` (`rehber_kablo.py`), ana koşuda ve `dene()`'de; `MODELSIZ_KONUM`
  iki bara için tutucu kutusu (Karar 1 geri alındı), `geometri_denetle`'nin modelli listesine tutucular (Baski) girdi. Bozma:
  `bara_yol_bozma` beş diferansiyel deneme (doğru çizilmiş yol 2 önkoşul; izin 0, yanlış saplama hedefi, yabancı takımdan geçiş,
  tutucu gövdesinden geçiş, saplamaya ulaşmama). Temel kırmızıyken `dene()`'nin "hata var" ölçütü dişsiz olduğu için ayrı.
  Birleşmeye (ve yolların taşınmasına) kadar kırmızı: ana ağaçta "tutucu yok" (1), benzetimde 26 bara yolu + 9 geometri.
  (b) K1 17.1 (Kablo yolu 2 yıldızın `{saplama.G05}` numaralı saplamasında biter), 17.4 (Kablo yolu 3 anahtarlının
  `{bsaplama.G09|G11}` ve `{bsaplama.G12}` numaralı saplaması), 17.6 (G22 şeması `{bsaplama.G22}`'den): yer tutucular kablolar.json
  yerleşiminden, sınama aynı kayıttan. `ZORUNLU`: 17.1 yol 2 cümlesi. (c) § 8.
- **Bulgu 2.** 17.6 "anahtarlı bara karede görünmez (modelde yok…)", F1 aşama 1 "(arka kat; bara modelde yok)", 17.4 "Kablo yolu 3'ün
  baradan …" değişti. Tarama: başka "bara … modelde yok / karede görünmez" cümlesi yok. Kilit: `YASAK` "bara modelde yok" + iki
  yakalanan, bir yakalanmaması gereken ("pabuçlar ve köprüler modelde yok") bozma.
- **Bulgu 3 (güvenlik).** Yukarıdaki Güvenlik bölümü. `ZORUNLU` K1 ×3 (F1'e bağ, koşul, erişim çekincesi), F1 ×1 (sıkma maddesi).
- **Bulgu 5 (güvenlik).** B6a sonucu + F1 yön maddesi; `ZORUNLU` B6a ×1, F1 ×2.
- **Bulgu 6.** `rehber_metin.py:403` `{bsaplama.G13|G16}`'ya geri döndü: gerekçe yoktu, SEMA G16 adı için yazılan sed'in yan etkisiydi.
  Çözücü `|` birleşimini destekliyor (`--kaynak` çözülemeyen 0; 403 "2" verir). SEMA G16 adı `{bsaplama.G16}` kalır.
- **Bulgu 7.** G22 şemasının yatay kısmı z −95 → **−80** (Echo kararı, geri alınabilir): iki bara ekseninin arası (−115 / −55), eksenlere
  30 / 25 mm, tutucu kutularına 24 / 14 mm (eskisi anahtarlı somunlarına 10,4 mm). `sema_boy` G22 258 (`--sema-boy-yaz`), kablolar.md
  üretildi. G16 / G22 şemaları `bara_yol_denetle` kuralıyla elle sınandı: girişim 0. K1 U06 notuna G05 eklendi ("G05: akü yarığından
  yıldızın 3 numaralı saplamasına; G17 ve G18: 4").
- **Bulgu 8.** `kalkan_parca_bozma_denemesi` (`rehber_denetim --bozma-denemesi`, 3 satır: temel 0, kart veride yakalanır, ReSpeaker
  yakalanmaz). `u06_port_denetle` 180° DevKit'i yakalamaz: analizdeki DevKit kutusu taşıyıcıya simetrik (x 54…107), yön yalnız
  `taban_lib.esp_local`'da (FreeCAD ister) → ucuz kilit yok; docstring'e sınır, karar kuyruğuna açık iş.
- **Bulgu 9.** E4: KT2 geçmezse ~30 cm USB-A uzatma ve L dirsek de gerekir (`kablolama-on-kararlar.md` § 5 satır 202, § 17 satır 425);
  `ZORUNLU` E4 ×1; karar kuyruğunda "Ahmet'e sorulacak". Sipariş listesine dokunulmadı.
- **Tarif:** 7.1 squash + tarama, 7.5 kancayla kuru koşu.
- **Diğer:** `F10l-birlesim.py` B2K listeleri boş liste koşusundan yeniden üretildi (etiketler `dt1`); onay kaydı yenilendi (29 fark);
  ASCII listesine 6 kelime.

Sınamalar (düzeltme turu 1 sonrası):

| Sınama | Ana ağaç | Benzetim |
|---|---|---|
| `rehber_denetim.py --kaynak` | çıkış 1: yalnız 3 terim (beklenen); onay farkı 0, ASCII 0, zorunlu eksik 0, yasak 0 | aynı |
| `rehber_denetim.py --bozma-denemesi` | **311 / 311** | 311 / 311 |
| `rehber_kablo.py` | KALDI 27 (tutucu yok kökenli + yol 5 / 7 röle başı + bara yolu "tutucu yok") | KALDI 35: 26 bara yolu + 9 geometri, hepsi CAD yolları (yollar taşınınca 0); şema, uç etiketi, `bara_tutarlilik` 0 |
| `rehber_kablo.py --bozma-denemesi` | 103 / 103 (bara yolu bozmaları atlandı: tutucu yok) | **108 / 108** (beş bara yolu bozması kendi iletisiyle) |
| `F10l-birlesim.py` | GECER | — |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / GEÇER | — |

Beklenmeyen kırmızı yok. Not: temel kırmızıyken `rehber_kablo --bozma-denemesi`'nin eski 103 satırı "yakalandı" der ama ayırt etmez
(ilk turda da böyleydi); anlamlı sayım yollar taşındıktan sonraki benzetim / birleşik ağaç koşusudur.

Dokunulan dosyalar (bu tur): `rehber_metin.py`, `rehber_denetim.py`, `rehber_kablo.py`, `rehber_kritik_onay.json`,
`lale158/kablo_yolu_taban.py`, `planlama/adim3/kablolar.json` (G22 `sema_boy`), `kablolar.md`, `planlama/d158/F10l-birlesim.py`,
`karar-kuyrugu.md`, bu günlük.

## 10. Düzeltme turu 2 (CAD dalı birleşik ağaçta, F10u-kontrol "Tur 1 kontrolü": DÜZELTMEYLE GEÇER)

Sınamalar artık ana ağaçta gerçek modelle (benzetim yok). FreeCAD koşulmadı; taramanın izlediği dosyalara dokunulmadı.

- **T1.** `CAD_KIRP[9]["son"]` 3 → 12, gerekçe "noktalar[13..]" / "[12]" / "[0..12]". Yol 9 artık 16 nokta (sigorta kutusu → yıldız 4
  (25; 194; −65) noktalar[5] → … → XL4016 çevre (49,2; 125; 75) noktalar[12] → eski ESP32 kolu [13..15]). Kesim aynı:
  `(0; 0,7071; 0,7071) · p ≤ 143,92`. Korunan [0..12] izdüşümü 8,84…141,42 (en büyük [12] 141,42), atılan [13..15] 212,13 / 243,95 /
  194,45: sınır ikisinin arasında, `cad_kirp_denetle` hata 0, kırpılmış yol [12]'de bitiyor.
- **T2.** İzin bölgesi `y ≥ BARA_IZIN_Y` (189,5, tutucu üst yüzü). Üç bozma eklendi: dikey gövdeye (y 182), gövde içinde eksen
  boyunca (y 185), panelin altından (y 176); üçü eski 175 kuralıyla 0 hata verir (kaçak), yenisiyle 2 / 2 / 2. Gerçek yollar temiz.
  Bara yolu bozmaları ana ağaçta koştu (atlanmadı): 8 / 8.
- **T3.** Kapanış 7.7'ye kare bakışı maddesi.
- **T4.** K1 17.1 ve F1'de alet "lokma anahtarı" (iki `ZORUNLU`). **T5.** F1 ESP32 yön maddesine "kabuk ve etek takılıyken üstten
  görülebildiği ölçülmedi; asıl denetim B6a" (`ZORUNLU`).
- **CAD turu 2'den (F10v § 5).** Yol adları (yol 2–9, "WAGO" yok): `KABLO_AD` baş kısımları yeni adların başıyla aynı (kaynak sınaması
  hata 0), uzun adlar yeni geometriyle çelişmiyor (yol 4 "anahtarlı bara → BTS7960 sağ"). Bu adlara bakan kurallar: `rehber_kablo`
  satır 172'deki XT60 − gerekçesi ve MODELSIZ_KONUM yorumu eski WAGO adını anıyordu, düzeltildi; desenler ("Kablo yolu N:") ada
  bağlı değil. Onay kaydı ad tutmuyor (fark yalnız CAD_KIRP 9). CAD uçları (x; 194; z ± 10) ile şema uçları (x; 191,9; z + 5) farkı
  sınamayı etkilemiyor (ikisi de izin bölgesinde). 17.7'ye "Kablo yolu 9 yıldızın {saplama.G18} numaralı saplamasından geçer, −
  damarı orada ayrılır" (`ZORUNLU`). E3a: "D24V50F5'i pin kenarı +z'ye (modelde TVS'nin yanına) bakacak şekilde tak; ürün gelince
  kart yazısıyla doğrula" (`ZORUNLU`), kuyrukta K51 açık iş. K52: iki boş alan (37 × 77, 33 × 77 mm) kuyrukta not.
  `_G10_YAKIN` gerekçesi değişmedi (geometri hata 0; F10v'nin "yol 3 ön şarj kartının ≈ 8,6 mm yanından" notu muafın konusu olan
  yol 1 / 8'i değiştirmiyor).
- **D3.** 07:50'de `uygulama-olcum.json` 09.11 tarihli, `lale158-kontrol.json` 07:49 (08:00'den önce): F10x koşusu henüz yok. Açık
  bırakıldı, kuyrukta not; kapanış 7.2'de.
- **Diğer.** ASCII listesine "bakacak"; onay kaydı yenilendi; F10l B2K listeleri yeniden üretildi (etiket `dt2`).

| Sınama (ana ağaç, birleşik model) | Sonuç | Beklenen |
|---|---|---|
| `rehber_kablo.py` | **SONUÇ GEÇER** | GEÇER |
| `rehber_kablo.py --bozma-denemesi` | **111 / 111** (bara yolu 8 satır koştu) | 109: fark T2'de bir yerine üç kaçak bozması |
| `rehber_denetim.py --kaynak` | **çıkış 0** (terim 0: kart modelde yok; onay 0, ASCII 0, zorunlu 0, yasak 0) | 0 |
| `rehber_denetim.py --bozma-denemesi` | 311 / 311 (kalkan parça 3 dahil) | — |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / GEÇER | — |
| `F10l-birlesim.py` | GECER (yeni liste) | — |
| `F10v-yol-bosluk.py` | koşulmadı (FreeCAD ister: `import Part`) | — |

Dokunulan (bu tur): `rehber_kablo.py`, `rehber_metin.py`, `rehber_denetim.py`, `rehber_kritik_onay.json`, `F10l-birlesim.py`,
`karar-kuyrugu.md`, bu günlük.

## 11. Düzeltme turu 3 (küçükler; F10u-kontrol "Tur 2 kontrolü ve yol doğrulaması": GEÇER)

Tarama sürerken: FreeCAD yok, izlenen dosyalara ve index'e yazılmadı, `git add` yok.

1. `rehber_kablo.py` CAD_KIRP yorumu yeni indislerle (yol 9: [0..12] korunur, yıldız 4 [5], XL4016 çevre [12], atılan [13..15]);
   § 8'deki izin kuralı "y ≥ 189,5".
2. E3a: "D24V50F5'i pin kenarı TVS'ye bakacak şekilde tak; … kart üstündeki yazıyla doğrula" (eksen adı kalktı; `ZORUNLU` güncellendi).
3. Pabuç yelpazesi (K1 "Toprak ve iki bara"): yeni yer tutucu `{coklu_pabuc.yildiz|bara}` (`rehber_deger.py`): kablolar.json
   yerleşimindeki kablolar + zincir köprü uçları (uç saplamada 1, arada 2; köprü adedi saplama − 1 değilse hata) ≥ 2 olan saplamalar →
   "1, 2, 3, 4 ve 5" / "1, 2, 3 ve 4". Talimat: "pabuçları yelpaze gibi açarak diz, üst üste aynı yöne bindirme; somunu taktıktan sonra
   dişin tam kavradığına bak" (sayı yok). Bağlam adları `_OZEL`'e; iki `ZORUNLU`.
4. B3 kablo maddesi: "Plaka altından geçen motor kablolarını (Kablo yolu 4) akü kayışıyla plaka arasına sıkıştırma, kayışa bağlama"
   (`ZORUNLU`).
5. K1 17.10 metni ve `KABLO_AD[11]` / `[12]`: "kablo ön kat kesiğinden geçer; çizimdeki yol kesiğin dışında görünür"; CAD düzeltmesi
   karar kuyruğunda (K64 notu altında) açık iş.
6. **D3 kapandı.** F10x adım 0'da `uygulama-olcum.json` (07:56) ve `lale158-kontrol.json` (07:49) yenilendi: ESP32 USB 1.129 / 1.560,
   ses kartı ölçümleri kalktı. `uygulama-notu.md` ESP32 satırı ve `kablo-kurali-notu.md` yeni değere çekildi (`elektrik.md` zaten
   doğruydu; `F4a-gunluk.md` geçmiş kaydı, dokunulmadı). `uygulama_rapor.py`'nin F10x'te düştüğü IndexError (`uygulama_metin.py:58`,
   HEAD'de de vardı) `_yak_tr` ile giderildi; rapor yeniden koşturuldu ama **beklenmedik farklar** verdiği için çıktı geri alındı
   (`uygulama-notu.md` / `rapor.html` HEAD hâli + yalnız ESP32 satırı elle):
   (a) kafa kütlesi 1.570,8 → 1.542,7 g, toplam 25.910,6 → 26.120,6 g, tilt payı 3,64 → 3,78, pan 2,21 → 2,26, ızgara 1,517 → 1,519
   (F10w montajından; ses kartı + U06 dışı); (b) 12 V satırı elle yazılmış "tabandan, boyundan geçmez" düzeltmesini kaybedip
   "(boyundan) … Değişmedi" yazıyor (üreticide eski metin); (c) "Listede olmayan 6 kalem" dört kalem sayıyor ve L USB-A dirseği
   anıyor. Düzeltilmedi, kuyrukta açık iş (üretici düzeltilip not yeniden üretilmeli).
7. Kuyruğa F10v yol 4 "> 15 mm" → 6,0 / 6,1 mm notu (F10v'ye dokunulmadı); § 7.8'e iki madde (F10v düzeltmesi commit öncesi;
   `git add -A` yok, `git add` taramadan sonra, dosyalar adıyla).
8. Onay kaydı yenilendi (13 fark); F10l listeleri yeniden üretildi (`dt3`); ASCII listesine "ezer", "yelpaze".

| Sınama (ana ağaç) | Sonuç |
|---|---|
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER / 111 / 111 |
| `rehber_denetim.py --kaynak` / `--bozma-denemesi` | çıkış 0 (onay 0, ASCII 0, zorunlu 0, bağlam 0) / 311 / 311 |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / GEÇER |
| `F10l-birlesim.py` | GECER |

Dokunulan (bu tur): `rehber_kablo.py`, `rehber_metin.py`, `rehber_denetim.py`, `rehber_deger.py`, `rehber_kritik_onay.json`,
`lale158/kafa-yerlesim/uygulama_metin.py`, `uygulama-notu.md` (ESP32 satırı), `planlama/d158/kablo-kurali-notu.md`,
`F10l-birlesim.py`, `karar-kuyrugu.md`, bu günlük.

## Ahmet'e sorulacaklar

- K64 alım: 9 M5 düz pul (DIN 125), 4 M3×10 ISO 7380, 4 M3 ısıl gömme somun; bara saplaması altıgen başlı (DIN 933) mı gelecek?
- K52: göğüs regülatörü kartının ölçüsü / ürünü (model hâlâ yok).
- KT2 geçmezse gereken ~30 cm USB-A uzatma (MJ:136) ve L USB-A dirsek (MJ:138): yedek olarak şimdi mi alınsın, KT2 sonucuna mı kalsın?
