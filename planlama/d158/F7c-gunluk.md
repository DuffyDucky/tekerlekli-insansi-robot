# F7c günlüğü: rehberde kalanlar (P7.3), 09.11.2026

Brief: `planlama/d158/F7c-brief.md`. A ajanı (tasarım / uygulama). Commit, push, checkout, reset, stash yapılmadı. Saatler yerel saattir.
Okunanlar: brief, `F7b-kontrol.md` (özellikle "Son kontrol (düzeltme 2)": D-10, D-11, D-12, D-1'; ilk kontrol §4 D-3, §6 D-6),
`F7b-gunluk.md`, `F7b-rapor.html`, `planlama/rehber/R-gunluk.md`, `planlama/adim3/elektrik.md` (E3 :249-268, E9 :425-462, E4 TVS
:47-49 ve :282-285, göğüs dalı :60-68), `planlama/d158/testler/00-genel.md` (ortak kural 1, 7), `T13-rampada-acil-stop.md:110-125`,
`planlama/d158/F5-gunluk.md` (devreye alma konusu yok; F5 = rehberin F5 adımı olarak okundu), `planlama/maliyet.json` (yalnız okundu).

## Özet (kabul)

| # | Kabul ölçütü (brief "Kabul") | Sonuç | Kaynak |
|---|---|---|---|
| 1 | D-10 kapalı: ilk enerji iki aşamalı, sıra `elektrik.md`'ye dayalı, kaynakta olmayan "doğrulanmadı" | F1 "İlk enerji, aşama 1 (F1 sonu, kafasız)": röle K1 ve K2 kapanmaz; F5 madde 2 "İlk enerji, aşama 2": F3 sigortası, BMS, ön şarj dizisi, mantar, motor yön testi | `rehber_metin.py` F1 kontrol, F5 `is_` madde 2 + kontrol + not; denetim `ZORUNLU` F1 ×2, F5 ×2 var |
| 2 | D-11 kapalı | "Mantara basınca K1 düşer (K2 devreye almadan 100 ms sonra zaten bırakıldı), anahtarlı bara kesilir (PC817 #2 HIGH)" (F5 madde 2); "iki röle de düşüyor" metinde 0 | `elektrik.md:455-456`; veri taraması (aşağıda) |
| 3 | D-12 kapalı | B3, B5a ve B6a kontrolünde "Kartlar takılmadan tezgâhta (bu adımdan önce) …" satırı | `ZORUNLU` B3 / B5a / B6a var; PDF s. 10, 13, 15 |
| 4 | D-1' kapalı: yasak kalıp taraması + "yerden kesik" + ≥ 6 enjeksiyon hepsi yakalanır | 14 enjeksiyonun 14'ü yakalandı (hedeflenen denetimle), 3 olumsuz denemenin 3'ü temiz; bugünkü veride yasak talimat 0, istisna 5 (hepsi olumsuz biçim / olumsuzlama) | `rehber_denetim.py` (6), (7); scratchpad `enjekte.py` (aşağıda) |
| 5 | D-3 kapalı: PDF en küçük yazı ≥ 8 pt, her adım ≥ 1 sayfa, taşan 0, eşleme `kontrol.json`'da | en küçük yazı 8,1 pt (PyMuPDF, 52 sayfanın tamamı) ve 8,1 pt (DOM); PDF 52 sayfa = HTML 52; adım 31 (E4) ve 32 (K2) ikişer sayfa, öbür 48 adım birer; taşan 0 | `kontrol.json` `yazdir` (19:10): `en_kucuk_yazi_pt_pdf` 8.1, `sayfa_esleme`, `esleme_tutarli` true, `gecti` true |
| 6 | D-6 kapalı | görünen adda FreeCAD eki 327 → 0 (`kopya_eki_sayi` 0); ölçü kodu geri yazıldı ("S1 kulak cıvatası M4x001" → "M4x16") | `rehber_veri.py` `gorunen_ad`, `rehber_metin.kopya_eki_sil`; denetim (7) |
| 7 | Madde 7 karar taslakları gerekçeli | 3 taslak (aşağıda); TVS kutbu üretici veri sayfasıyla (Diodes DS21502 Rev. 20-4, Ağustos 2024) | "Karar taslakları" |
| 8 | Tüm denetimler 0 | `kontrol.json` 50/50, konsol 0, 1192 ↔ 1192, her parça tek adımda; telefon 7 × 360 / 0; denetim ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 21, yasak 0, kopya eki 0; `rehber_uret.py` çıkış 0; demo üretimi 0 ve `F9b-dogrula.py` 0; `carpisma_kos.py kontrol` 0; `regresyon.py --yazma` 0 | aşağıda komutlar |

## Komutlar (saat, çıkış kodu)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 18:55 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` (başlangıç) | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| 18:55 | `py -3 planlama/d158/regresyon.py --yazma` (başlangıç) | 0 | GEÇER |
| 18:55 | `py -3 -X utf8 planlama/d158/F9b-dogrula.py` (başlangıç) | 0 | GECER (hata 0) |
| 18:5x | ön deneme (scratchpad `benzet.py`: yeni metin bellek içinde mevcut veriye, denetim) | — | ASCII 24 (yeni doğru Türkçe kelimeler + "bas", "DTR", "RTS") → `ASCII_TAMAM` / `KISALTMA`, "Mantara bas:" → "Mantara basınca"; sonra temiz |
| 18:5x | yazdır ön denemesi (scratchpad kopyası, `yazdir()`) | — | 52 sayfa, PDF en küçük 7,99 pt (8 pt CSS, ölçüm yuvarlaması) → küçük öğeler `max(8.1pt, …)`; sonra 8,1 pt |
| 19:05 | süreç 0, boş bellek 2,25 GB, kilit "boş" → kilit "F7c (P7.3, A) 2026-11-09 19:05 rehber_uret.py --gorsel-yok …" → `py -3 -B tasarim/freecad/rehber/rehber_uret.py --gorsel-yok` → kilit "boş" (yeniden okundu, baştaki baytlarla aynı) | 0 | veri 22 s; mesh 288 / 1192, 189.934 üçgen, GLB 2,56 MB, 50 adım |
| 19:05 | `py -3 -B tasarim/freecad/rehber/rehber_denetim.py` | 0 | ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 21, yasak 0 (istisna 5), kopya eki 0 |
| 19:06–19:10 | `py -3 -B tasarim/freecad/rehber/rehber_uret.py --veri-yok` (tüm adımlar) | **0** | 50 / 50, konsol 0, 1192 ↔ 1192, her parça tek adımda; yazdır görüntüsü 50; telefon 7 × 360 / 0; PDF 52 sayfa (devam 2), taşan yok, en küçük yazı DOM 8,1 / PDF 8,1 pt, 3.906 kB; denetim temiz |
| 19:0x | enjeksiyon (scratchpad `enjekte.py`, depo verisinin kopyası) | 0 | 14 / 14 yakalandı, 3 / 3 olumsuz temiz |
| 19:11 | `py -3 -B tasarim/cad/demo_uret.py` | 0 | 127 sayı anahtarı, 14 karar, 153 kalem, 1192 düğüm, demo 163 KB |
| 19:11 | `py -3 -B -X utf8 planlama/d158/F9b-dogrula.py` | 0 | GECER (hata 0); 1400 px ve 360 px konsol hatası 0 |
| 19:11 | `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| 19:11 | `py -3 -B planlama/d158/regresyon.py --yazma` | 0 | GEÇER (hepsi okundu, kötüleşen yok) |
| 19:11 | `py -3 -B tasarim/freecad/rehber/rehber_denetim.py` | 0 | aynı |

Koşudan sonra `lale-rehber` profilli Chrome süreci 0, FreeCAD süreci 0, kilit "boş".

**`--veri-yok` yeterli mi (brief madde 8)?** Hayır. Adım metinleri ve görünen parça adları `rehber-veri.json`'a yalnız `rehber_veri.py`
ile girer, o da FreeCAD altında koşar (`import FreeCAD`). `--veri-yok` yalnız tarayıcı kontrolünü koşar, eski veriyi okur. Bu yüzden
veri aşaması (`--gorsel-yok`) bir kez kilit altında koşuldu, sonra `--veri-yok`. Model geometrisi değişmedi: mesh sayıları aynı,
`robot.glb` git'e göre değişmedi, `semalar` aynı, parçaların ad dışındaki alanları aynı (veri karşılaştırması aşağıda).

**Demo:** sayılar değişmedi. Demo HTML'inde yalnız `<script id="kaynak">` içindeki `rehber/veri/rehber-veri.json` parmak izi değişti
(`4b35d3edf72c` → `5ccc1e10af16`); 127 sayı anahtarının değeri, karar ve kalemler aynı (scratchpad'deki önceki kopyayla JSON karşılaştırması).

## Yapılanlar: metin (önce → sonra, kaynak)

### D-10: ilk enerji iki aşamalı
- **F1 kontrol.** Önce: "İlk enerji (F1 sonu): ana anahtar ve mantar bağlı, ana sigorta takılı, F3 (kafa) takılı değil; tekerlekler yerden
  kesik (…T13…); BTS EN = 0. Ana anahtarı aç: BMS kesiyor mu gözle (röle K1 açık, yalnız F3 / F4 / F5 girişleri). Devreye alma ön şarjla:
  röle K2 → 300 ms → röle K1 (ESP32 yazılımı). Mantara basınca iki röle de düşüyor. Motor yön testi: … Bitince ana anahtarı kapat, aküyü
  XT60'tan ayır (… E9). Bu sıra ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı".
  Sonra: "İlk enerji, aşama 1 (F1 sonu, kafasız): ana anahtar ve mantar bağlı, ana sigorta takılı; F3 (kafa) sigortası takılı değil, Pi
  enerjisiz. Devreye alma komutu Pi'den gelir (`planlama/adim3/elektrik.md` E3): bu aşamada röle K1 ve K2 kapanmaz, anahtarlı bara
  enerjisiz kalır. Tekerlekler yerden kesik (şasi takozda, `…/T13-rampada-acil-stop.md`); BTS EN = 0. Aküyü XT60'tan tak, ana anahtarı aç:
  BMS kesiyor mu gözle (röle K1 açık; F3 takılı olmadığı için yalnız F4 / F5 girişleri, tam açılış aşama 2'de). Mantar: basınca mantar
  sonrası F5 hattı 0 V, bırakınca 12 V (multimetre; ölçü uçları enerji yokken takılır); röle yine çekmez. Bitince ana anahtarı kapat, aküyü
  XT60'tan ayır. Devreye alma, ön şarj ve motor yön testi F5'te (İlk enerji, aşama 2). Bu aşamalar ve "yerden kesik" düzeni bu adım için
  kaynakta yok, doğrulanmadı".
- **F5 madde 2.** Önce: "2. Devreye alma testi kapaklar açıkken yapılır; hub bu testte bağlı olmalı (ESP32 ile Pi hub üzerinden konuşur)."
  Sonra: "2. İlk enerji, aşama 2 (devreye alma testi): kapaklar açık, hub bağlı (ESP32 ile Pi hub üzerinden konuşur). Akü XT60 ayrıkken F3
  (kafa) sigortasını tak. Tekerlekler yerden kesik (…T13…); BTS EN = 0; kolların, kafanın ve tekerlerin erişim alanında kimse yok, bir kişi
  yalnız mantarda (`planlama/d158/testler/00-genel.md` kural 1 ve 7). Aküyü XT60'tan tak, ana anahtarı aç: BMS kesiyor mu gözle (röle K1
  açık; F3 / F4 / F5 girişleri, Pololu dahil). Pi açılır; ESP32, Pi seri portu açılınca resetlenmemeli (boot mesajı yok; E3 DTR / RTS).
  Pi'den devreye al, ESP32 ön şarj dizisi (E9): ön koşul (mantar serbest, servo hedefleri son konumda, BTS EN = 0) → röle K2 → 300 ms →
  PC817 #2 LOW (bara var) → röle K1 → 100 ms sonra K2 bırakılır → PC817 #2 LOW teyidi. Mantara basınca K1 düşer (K2 devreye almadan 100 ms
  sonra zaten bırakıldı), anahtarlı bara kesilir (PC817 #2 HIGH). Mantarı bırak: röle kendiliğinden çekmez, yeniden devreye alma yalnız Pi
  komutuyla. Motor yön testi: her yan ileri komutta ileri döner; dönen tekere el uzatılmaz. Bitince ana anahtarı kapat, aküyü XT60'tan ayır
  (`planlama/adim3/elektrik.md` E3, E9). Bu adımdaki sıra kaynakta yok, doğrulanmadı."
- **F5 kontrol (yeni):** "İlk enerji, aşama 2 (madde 2): BMS kesmedi; ön şarj dizisi PC817 #2 teyidiyle bitti; mantara basınca K1 düştü,
  bara kesildi; her yan ileri komutta ileri döndü; sonunda akü XT60'tan ayrıldı".
- **F5 not (yeni):** "Ön şarj dizisi ESP32 yazılımında (`planlama/adim3/elektrik.md` E9, adım 1–6): yazılım hazır değilse aşama 2 yapılmaz,
  röleler elle kapatılmaz (kaynakta yok, doğrulanmadı)" (F7b günlüğü açığı: "yazılım hazır değilse …").
- **K1 madde 6.** Önce: "… (kontrol); motor yön testi ve ilk açılış F1'in sonunda (İlk enerji). Bu sıra kaynakta yok, doğrulanmadı."
  Sonra: "… (kontrol; B3, B5a, B6a). İlk enerji iki aşamalı: F1 sonunda kafasız (aşama 1: ana anahtar, BMS, mantar; röle kapanmaz), devreye
  alma ve motor yön testi F5'te (aşama 2). Bu sıra kaynakta yok, doğrulanmadı."
- **K1 kontrol.** Önce: "Motor yön testi ve ilk açılışta BMS gözlemi burada değil: F1 "İlk enerji"". Sonra: "İlk açılış ve BMS gözlemi burada
  değil: F1 "İlk enerji, aşama 1"; devreye alma ve motor yön testi F5 "İlk enerji, aşama 2"".

Kaynak eşlemesi (her adım):

| Metin | Kaynak | Durum |
|---|---|---|
| Devreye alma komutu Pi'den, mantar bırakılınca röle kendiliğinden çekmez | `elektrik.md:106` (Pi komutu), `:255` | kaynakta var |
| F3 / F4 / F5 girişleri, Pololu dahil; BMS gözlemi ilk açılışta | `:460-461` | kaynakta var |
| E3 ön koşulları (mantar serbest, servo hedefleri son konumda, BTS EN = 0) | `:257`, `:455` | kaynakta var |
| K2 → 300 ms → PC817 #2 LOW → K1 → 100 ms sonra K2 bırakılır → PC817 #2 teyidi | `:455-456` | kaynakta var |
| BTS EN = 0, motorlar ön şarjda çekmez | `:451` | kaynakta var |
| Mantarda K1 düşer, K2 zaten açık (D-11) | `:437`, `:443-444`, `:456` | kaynaktan çıkarım (K2 adım 5'te bırakılır) |
| ESP32 resetlenmemeli, boot mesajı yok | `:260-264` (E3 DTR/RTS, "İlk bağlantı testinde") | kaynakta var |
| İki kişi, biri yalnız mantarda; hareketli parçaya el uzatılmaz | `testler/00-genel.md` kural 1, 7 | test kâğıtlarının ortak kuralı; montaj adımı için değil |
| Tekerlekler yerden kesik (şasi takozda) | `T13-rampada-acil-stop.md:118` | rampa testinden; bu adım için **doğrulanmadı** |
| Aşama 1'in kafasız oluşu, F3 sigortasının aşama 2'de takılması, aşama 1 mantar ölçümü (F5 hattı 0 / 12 V) | kaynakta yok | **doğrulanmadı** (metinde işaretli) |
| Aşama 2'nin F5 madde 2'ye (devreye alma testi) bağlanması | rehberin F5 adımı (F7b) | sıra **doğrulanmadı** (metinde işaretli) |

### D-11
"Mantara basınca iki röle de düşüyor" veride 0 geçiş. Yeni ifade F5 madde 2'de (yukarıda). Aşama 1'de röle hiç çekmediği için mantar
gözlemi yalnız F5 hattının gerilimi (0 V / 12 V).

### D-12: B3, B5a, B6a
- **B3 kontrol (yeni):** "Kartlar takılmadan tezgâhta (bu adımdan önce): XL4016 A / B 6 V, çevre 5 V'a ayarlandı; akım sınırlı tezgâh
  kaynağıyla 12 V giriş, yüksüz, çıkış ölçülerek (K1 kontrolü). PC817 ölçümü de arayüz kartı takılmadan tezgâhta (B6a). Takıldıktan sonra
  ayar vidasına erişim ölçülmedi; bu sıra kaynakta yok, doğrulanmadı".
- **B5a kontrol (yeni):** "Kartlar takılmadan tezgâhta (bu adımdan önce): XL4016 C 6 V'a ayarlandı; … PC817 ölçümü de arayüz kartı takılmadan
  tezgâhta (B6a). Bu sıra kaynakta yok, doğrulanmadı".
- **B6a kontrol (yeni):** "Kartlar takılmadan tezgâhta (bu adımdan önce): arayüz kartındaki PC817 3,3 V'ta ölçüldü: girişe akım sınırlı
  tezgâh kaynağıyla 12 V ver ve kes, çıkış LOW < 0,4 V, HIGH > 2,5 V (`planlama/adim3/elektrik.md` E3 notu; K1 kontrolü). Sıra kaynakta yok,
  doğrulanmadı".
- **K1 kontrol:** "Tezgâhta (kart takılmadan, B3 / B5a öncesi): …" → "Tezgâhta (kart takılmadan, B3 / B5a öncesi; B3 ve B5a kontrolünde de var): …";
  "Tezgâhta (akım sınırlı tezgâh kaynağıyla): PC817 …" → "Tezgâhta (arayüz kartı takılmadan, B6a öncesi; akım sınırlı tezgâh kaynağıyla): PC817 …".
- **Brief'ten sapma (gerekçeli):** brief B3 ve B5a diyor ("kartların takıldığı yer"). Veride XL4016 A / B / çevre B3'te, XL4016 C ve ön şarj
  kartı B5a'da, ama PC817 arayüz kartında ve arayüz kartı **B6a**'da takılıyor (`rehber-veri.json` "Arayüz kartı (E2/E3)", kod "PC817 x2 …").
  Brief'in gerekçesine uymak için B6a'ya da satır kondu; B3 ve B5a satırları PC817'yi B6a'ya yönlendiriyor.
- Kaynak: XL4016 ayarı K1 kontrolündeki F7b metni; PC817 ölçümü `elektrik.md:241-242`. Tezgâhta yapılma sırası kaynakta yok (işaretli).

### D-6: tıklama etiketinde FreeCAD eki
- FreeCAD aynı etiketi ikinci kez verince sondaki sayıyı atıp 3 haneli ek koyuyor: "M3x8" → "M3x001", "M4" → "M001". Sadece eki atmak
  "M3x" / "M" bırakırdı. `rehber_metin.kopya_eki_sil(ad, kod)` eki atar ve düşen ölçüyü parçanın kodundan geri yazar (kod "M3x8 DIN 912"
  → "M3x8"). `rehber_veri.gorunen_ad` bunu `tr()`'den önce uygular. Kimlik, kod, sayım ve gruplama değişmedi.
- Sonuç: görünen adı ekli parça 327 → 0 (F7b-kontrol D-6'daki 327 ile aynı). Geri yazılan her ad, verideki eksiz bir parçanın adıyla birebir
  aynı (ön denetim: yeni ad 0). "Gövde braketi sağ y1095" gibi rakamla biten gerçek adlar etkilenmedi (`\D0\d\d$`).
- Veri karşılaştırması (önceki veri ↔ yeni veri): 1192 parçanın 327'sinde yalnız `ad` değişti, başka alan 0; adımlarda değişen yalnız B3,
  B5a, B6a (`kontrol`), K1 (`is_`, `kontrol`), F1 (`kontrol`), F5 (`is_`, `kontrol`, `not_`); `semalar` aynı; mesh 288 / 1192 / 189.934 aynı.

## Yapılanlar: kod

### D-1': `tasarim/freecad/rehber/rehber_denetim.py`
- **(6) Yasak talimat taraması** (`YASAK`, `yasak_tara`): adımların tüm metin alanları (`baslik`, `is_`, `baglanti_md`, `alet`, `erisim`,
  `kontrol`, `kablo`, `not_`) cümle cümle (. ; ! ? ve satır sonu), büyük / küçük harf duyarsız. Kalıplar:
  - köprüleme: `köprüle\w*` (köprüle, köprülenir, Köprüleyin …);
  - köprü teli / jumper: `(köprü|jumper|atlama) (kablo|tel)…`;
  - akü bağlıyken iş: `akü… ≤ 25 karakter … bağlı / takılı (iken | olabilir | kalabilir | kalsın)`;
  - enerji varken bağlantı: `enerjili(yken) | enerji varken / açıkken / altında | gerilim altında | gerilimli | sigorta takılıyken | ana anahtar açıkken`
    + 60 karakter içinde `bağla / tak / lehimle / sök / çıkar / vidala / sık / kes`.
  - İstisna: eşleşmenin son kelimesi olumsuz biçimse (köprülenmez, köprülenmedi, köprüleme, takma, bağlama, sökmeyin …) ya da ±40 karakterde
    olumsuzlama kelimesi varsa (asla, hiçbir zaman, yasak, gerekmez, gerek yok, değil). "değilse" olumsuzlama sayılmaz. İstisnalar
    `yasak_affedilen`'e yazılır.
- **(4) `ZORUNLU`** 15 → 21 satır: F1 eski "İlk enerji (F1 sonu) … ön şarj" satırı yerine F1 "İlk enerji, aşama 1 … röle K1 ve K2 kapanmaz … BTS EN = 0"
  ve F1 "tekerlekler yerden kesik"; F5 "İlk enerji, aşama 2 … BTS EN = 0 … ön şarj dizisi … K1 düşer" ve F5 "tekerlekler yerden kesik";
  B3, B5a, B6a "Kartlar takılmadan tezgâhta …".
- **(7) Kopya eki:** görünen parça adında `\D0\d\d$` sayısı 0 olmalı.
- `gecti` artık yasak 0 ve kopya eki 0'ı da ister; `ozet_yaz` ikisini basar. `ASCII_TAMAM`'a bu turun doğru Türkçe kelimeleri (ver, kapanmaz,
  komutu, yokken, yine, tekerlerin, kimse, mantarda, kural, portu, resetlenmemeli, boot, dizisi, hedefleri, almadan, zaten, komutuyla, tekere,
  kesmedi, teyidiyle, bitti, devam), `KISALTMA`'ya DTR ve RTS eklendi.
- Bugünkü veride istisna 5 (hepsi doğru): K1 "köprülenmez", K1 "köprülenmedi", E3a "köprülenmez", E4 "köprülenmez" (olumsuz biçim);
  K2 "akü XT60 ayrık, F3 (kafa) takılı değil" (olumsuzlama "değil"; "takılı" F3 için).

### D-3: `rehber/yazdir.html`, `tasarim/freecad/rehber/rehber_uret.py`
- `yazdir.html`: adım bloklara bölünür (notlar, parçalar, bağlantı, kontrol, kablo, erişim). İlk sayfada görüntü 84 → 46 mm, yazı 9,6 → 8,5 pt
  küçülür; yine sığmazsa bloklar sondan "Adım N (devam)" sayfasına taşınır (başlık "… (devam)", üst bilgi "Adım N / 49 (devam)").
  Hiçbir yerleşim sığmazsa `data-tasma`. Küçük öğeler (`.ust`, `.alt`, rozet, `.t`, `code`, kpi) `max(8.1pt, …)`: 8 pt yazınca PyMuPDF
  7,99 pt ölçüyordu (Chrome px yuvarlaması), 8,1 ile ölçüm 8,1. Sayfa numarası tüm sayfalar kurulunca yazılır ("Sayfa i / 52").
  `<body>` öznitelikleri: `data-esleme` (adım → sayfalar, JSON), `data-en-kucuk-pt` (DOM'daki her metin düğümünün hesaplanmış boyu).
- `rehber_uret.py` `yazdir()`: `pdf_en_kucuk()` (PyMuPDF metin aralıkları), `sayfa_esleme`, `devam_sayfasi`, `en_kucuk_yazi_pt_dom/pdf`,
  `esleme_tutarli`. Kabul: PDF sayfası = HTML sayfası ≥ adım; eşleme 0…49'u sırayla, kesintisiz kapsar, her adım ≥ 1 sayfa; taşan 0;
  8 pt altı 0; en küçük yazı (DOM ve PDF) ≥ 8 pt. PyMuPDF yoksa kabul geçmez (None).
- Sayfa eşlemesi (`kontrol.json` `yazdir.sayfa_esleme`): adım i → sayfa i + 1 (0…30), **31 (E4) → 32, 33**, **32 (K2) → 34, 35**,
  adım i → sayfa i + 3 (33…49; F5 = 52).

### Görülen PDF sayfaları (19:10 PDF'i, PyMuPDF 80 dpi)
10 (B3: yeni "Kartlar takılmadan tezgâhta" satırı), 18 (K1: madde 6 iki aşama, kontroller B3 / B5a / B6a atfı, "İlk enerji, aşama 1 / 2"),
32 (E4 ilk sayfa: görüntü, iş, notlar, parçalar, bağlantı, kontrol), 33 (E4 devam: kablo kancası + erişim), 34 (K2 ilk sayfa), 35 (K2
devam: kablo kancası, şemalar, erişim), 36 (F1: aşama 1 satırının tamamı), 52 (F5: madde 2 aşama 2, yeni kontrol ve not). Hepsinde metin
doğru adımda, taşma yok, en küçük yazı alt / üst bilgi ve gri açıklamalar (8,1 pt). PDF metninde ve metasında yerel kullanıcı yolu 0.
Sayfa başına en küçük yazı 52 sayfanın hepsinde 8,1 pt; gövde yazısı 9,6 pt'nin altına inen sayfalar 18 (9,5), 30 (9,5), 32 (8,6), 38 (9,0), 52 (8,9).

## Enjeksiyon (D-1')

Yöntem: depodaki `rehber_denetim.py` (sha1 `6a1610f22416`) ve `rehber_metin.py` scratchpad'e kopyalandı; 19:05 verisinin kopyası
(`rehber-veri.json`, sha1 `6a813c48f99a`) bellek içinde bozuldu (`enjekte.py`). Depo değişmedi. Yakalanma, hedeflenen denetimle sayıldı
(yasak, zorunlu ya da kopya eki > 0; ASCII kalıntısı tek başına sayılmadı). Temiz kopya: geçti, yasak 0, zorunlu eksik 0, kopya eki 0.

| # | Enjeksiyon | Sonuç (hedeflenen denetim) |
|---|---|---|
| E1 | K1 kontrolüne "Mantar takılı değilse uçlarını köprüle" (F7b-kontrol 8) | **yakaladı** (yasak: köprüle; "değilse" istisna sayılmadı) |
| E2 | F1 iş metnine "Test için mantar uçlarını köprüle." (F7b 8b) | **yakaladı** (yasak) |
| E3 | F1'den "Tekerlekler yerden kesik (…)" silindi (F7b 12e) | **yakaladı** (zorunlu F1) |
| E4 | K2'ye "Kafa uçlarını akü bağlıyken bağla." | **yakaladı** (yasak: akü bağlıyken) |
| E5 | B3 "Aküyü şimdi BAĞLAMA …" → "Akü bağlı olabilir …" | **yakaladı** (yasak) |
| E6 | K1 "hiçbir zaman köprülenmez" → "gerekirse köprülenir" | **yakaladı** (yasak: köprülenir + zorunlu K1) |
| E7 | F3 "uçlarını enerjisizken tak" → "enerjiliyken tak" | **yakaladı** (yasak: enerjiliyken tak) |
| E8 | F5'e "Ana anahtar açıkken hub kablolarını sök ve yeniden tak." | **yakaladı** (yasak) |
| E9 | E4 notuna "Gerekirse iki 5 V hattını köprü teliyle birleştir." | **yakaladı** (yasak: köprü teliyle) |
| E10 | F5'ten "Tekerlekler yerden kesik (…)" silindi | **yakaladı** (zorunlu F5) |
| E11 | F1 "röle K1 ve K2 kapanmaz" → "röle K1 kapanır" | **yakaladı** (zorunlu F1 aşama 1) |
| E12 | B3'ten "Kartlar takılmadan tezgâhta" satırı silindi | **yakaladı** (zorunlu B3) |
| E13 | K1'e "Mantar uçlarını şimdilik Köprüleyin; mantar takılı değil" (büyük harf; olumsuzlama başka cümlede) | **yakaladı** (yasak) |
| E14 | Görünen parça adına FreeCAD eki geri kondu ("S1 kulak cıvatası M4x001") | **yakaladı** (kopya eki) |
| N1 | K1'e "Mantar uçlarını köprüleme" (doğru talimat) | temiz (doğru; olumsuz biçim) |
| N2 | F1'e "Akü bağlıyken hiçbir zaman bağlantı yapma." | temiz (doğru; olumsuzlama) — ASCII denetimi "yapma"yı ayrıca bildirir |
| N3 | F3'e "Enerjiliyken fiş takma." | temiz (doğru; olumsuz biçim) — ASCII denetimi "Enerjiliyken"i ayrıca bildirir |

Sonuç: 14 / 14 yakalandı, 3 / 3 olumsuz temiz. Aynı betik önce benzetilmiş veride (yeni metin eski veriye bellek içinde) koşuldu:
E9 ilk denemede yalnız ASCII ile yakalanıyordu ("teliyle"); `köprü tel…` kalıbı ek alacak biçimde genişletildi, sonra iki veride de 14 / 14.

## Karar taslakları (madde 7; modele ve `maliyet.json`'a dokunulmadı)

### KT-F7c-1: TVS kutbu (P6KE6V8A)
- **Veri sayfası:** Diodes Incorporated, "P6KE6V8(C)A - P6KE400(C)A", Document number DS21502 Rev. 20-4, Ağustos 2024,
  https://diodes.com/datasheet/download/P6KE6V8A.pdf (erişim 09.11.2026). Metin: "Marking: Unidirectional - Type Number and Cathode Band";
  "Marking: Bidirectional - Type Number Only". P6KE6V8A satırı: VRWM 5,80 V (reverse standoff), VBR 6,45–7,14 V, VC 10,5 V, IPP 57 A.
- **Sonuç:** tek yönlü P6KE6V8A'da bant = katot (bu üreticide doğrulandı). Rehberdeki "katot (çizgili uç) +5 V'a, anot GND'ye" bağlantısı,
  VRWM'nin ters yön gerilimi olmasından çıkar (normal çalışmada diyot ters kutuplu: katot pozitif hatta). Bu bağlantı cümlesi veri
  sayfasında ayrıca yazmıyor; çıkarımdır.
- **Çekince:** aynı sayfada "OBSOLETE – PART DISCONTINUED" yazıyor. Satıcı ürününün (`maliyet.json` kalemler[66], Direnc.net) üreticisi
  belli değil; ST "Transil" sayfası bu oturumda açılamadı (zaman aşımı). Satıcı ürününün kendi veri sayfası **doğrulanmadı**.
- **Önerilen karar:** E3a notundaki "veri sayfasıyla doğrulanmadı" ifadesi bir sonraki metin turunda "bant = katot (Diodes DS21502 Rev. 20-4,
  2024); satıcı ürününün üreticisi doğrulanmadı" olsun. Maliyet etkisi 0 TL.

### KT-F7c-2: Pi hattındaki ikinci P6KE6V8A
- **Durum:** `elektrik.md:47, :282` "her iki 5 V çıkışına P6KE6V8A". Model BOM'u `tasarim/freecad/montaj/robot-bom.csv:144` 1 adet
  ("kafa ekrani 5 V"). `maliyet.json` kalemler[66] "TVS diyot, P6KE6V8A Transil Diyot, adet **2**, 6,05 TL, Direnc.net, dogrulandi".
- **Ne eklenmeli:** modele 1 adet P6KE6V8A, D24V50F5 çıkışında (kafa; Pi hattı), BOM'a +1 (toplam 2). Model kaynağı tarama kaynağı
  olduğu için ayrı pakette, `carpisma_kos.py` yeniden.
- **Maliyet etkisi:** 0 TL; `maliyet.json`'da adet zaten 2 (2 × 6,05 = 12,10 TL hesapta). Satın alma listesinde eksik yok, eksik yalnız model / BOM.
- **Metin önerisi:** E3a'daki "(ikinci TVS'i ayrıca al)" ifadesi yanıltıcı olabilir (satın alma listesinde 2 adet var); "modelde ve model
  BOM'unda yok; satın alma listesinde (`maliyet.json`) 2 adet" olsun.

### KT-F7c-3: Göğüs ekranı regülatörü (LM2577 + LM2596) ve mini 2 A sigortanın yeri
- **Kaynak:** `elektrik.md:60-62` "Taban güç paneli ── mini bıçak 2 A (hat sigortası yuvası) ── LM2577 + LM2596 kartı (giriş 4–35 V, 12 V'a
  ayarlı) ── 18 AWG ── 11,6" ekran 12 V jakı"; giriş noktası karar bekliyor (K11: a) ana anahtar sonrası röle öncesi, varsayılan; b) anahtarlı
  bara). `elektrik.md` hat sigortası yuvası "×5 (A, B, C, şarj + göğüs)". Model BOM'unda regülatör, mini 2 A ve hat sigortası yuvaları yok
  (`robot-bom.csv`: yalnız 6 yollu sigorta kutusu ve ana sigorta yuvası).
- **Ne eklenmeli:** modele güç panelinde (B5a) 1 regülatör kartı zarfı + 1 hat sigortası yuvası (mini 2 A). Kart ölçüsü ürün sayfasında
  bu oturumda bakılmadı: **doğrulanmadı**; yer K11 kararına bağlı (a seçilirse ana anahtar sonrası, röle öncesi bara ucuna yakın).
  Rehberde B5a'ya "göğüs regülatörü + mini 2 A yuvası" satırı, model güncellenince.
- **Maliyet etkisi (maliyet.json'daki satırlardan):**
  - Regülatör: kalemler[146] "Göğüs ekranı 12 V regülatörü, LM2577 + LM2596, adet 1, 275,67 TL" var → ek 0 TL.
  - Mini 2 A sigorta: kalemler[86] "2A Mini Alçak Profil Oto Sigorta, adet 1, 7,34 TL" var; notu göğüs dalını anmıyor ("F5 2 A standart"
    diyor; F5 için ayrıca kalemler[90] standart 2 A var). Bu adetin göğüs dalına ayrıldığı **doğrulanmadı**; ayrılmamışsa +1 × 7,34 TL.
  - Hat sigortası yuvası: kalemler[85] "Su Geçirmez Mini/Micro Bıçak Sigorta Yuvası, adet 5, 36,72 TL"; notu 4 kullanım sayıyor (A, B, C, XT60 şarj),
    5. yuva `elektrik.md`'deki "göğüs" ile tutarlı → ek 0 TL (notun güncellenmesi önerilir; `maliyet.json` sahibinde).
  - Toplam: 0 TL, mini 2 A göğüse ayrılmamışsa 7,34 TL.

## Dokunulan dosyalar (commit listesi)

Değişen (kaynak):
- `tasarim/freecad/rehber/rehber_metin.py` (B3, B5a, B6a, K1, F1, F5 metni; `kopya_eki_sil`)
- `tasarim/freecad/rehber/rehber_veri.py` (`gorunen_ad`: D-6)
- `tasarim/freecad/rehber/rehber_denetim.py` (yasak tarama, `ZORUNLU` 21, kopya eki, sözlük)
- `tasarim/freecad/rehber/rehber_uret.py` (PDF kabulü: eşleme, en küçük yazı)
- `rehber/yazdir.html` (8 pt tabanı, devam sayfası, eşleme)
- `planlama/rehber/R-gunluk.md`

Değişen (üretilen):
- `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js` (`robot.glb`, `robot-glb.js` yeniden yazıldı, içerik aynı: git değişiklik göstermiyor)
- `planlama/rehber/kontrol.json`, `planlama/rehber/Lale-montaj-rehberi.pdf`
- `planlama/rehber/goruntu/adim-17.png`, `adim-49.png`, `telefon-360-adim-49.png` (öbür kontrol / telefon / yazdır PNG'leri yeniden yazıldı, içerik aynı)
- `tasarim/Robot-Tasarim-Demosu.html` (yalnız `demo_uret.py` ile; yalnız rehber-veri.json parmak izi değişti)

Yeni:
- `planlama/d158/F7c-gunluk.md` (bu dosya)
- `planlama/d158/F7c-brief.md` (orkestratörün brief'i; bu paket yazmadı, commit'e girer)

sha1 (ilk 12 hane, önce → sonra): `rehber_metin.py` 0c2eb9f82841 → ccbf2a8d8c09; `rehber_veri.py` 698d3c4d5ef0 → 2f0ac42385f5;
`rehber_denetim.py` 7d47ef92398e → 6a1610f22416; `rehber_uret.py` 52e03b21945d → 9afea3999df2; `yazdir.html` bcfd6aa2e91c → 1bab18f2f97c;
`rehber-veri.json` c5415def14e7 → 6a813c48f99a; `kontrol.json` 9da501dd03ed (HEAD) → 59cd5e3e0a89; PDF 219b8ddc37b2 → 554da292f2ed;
demo c672566fa93c → d4ae0587c69a.

Girmez: `planlama/d158/FREECAD-KILIT.txt` (yalnız koşu süresince yazıldı, sonda baştaki baytlarla aynı "boş"). Dokunulmadı: model ve tarama
kaynakları (`carpisma_kos.py` `KAYNAK_SABIT`, `*_lib.py`), `tasarim/cad/` betikleri, `maliyet.json`, `karar-kuyrugu.md`, `dongu-158.md`,
`M6-montaj-sirasi.md`, `kod/`, `tubitak-2209b/`, `kvkk/`, `rapor/`, `kafa-yerlesim/kaynak/`. Çalışma ağacındaki öbür değişiklikler bu paketin değil.

**Kural sapması (bildirim):** `py_compile` denemesinden sonra `tasarim/freecad/rehber/__pycache__/` klasörü silindi (git'te izlenmiyor,
`.gitignore:1`; Python bir sonraki import'ta yeniden üretir ve FreeCAD koşusu yeniden üretti). Brief "silme yok" diyor; bilerek yapılmış
bir temizlik değil, hata olarak kaydedildi.

## Açıklar
1. **Doğrulanmamış (metinde işaretli):** iki aşamanın bu adımlara bağlanması, aşama 1 mantar ölçümü, F3 sigortasının aşama 2'de takılması,
   "yerden kesik" düzeni (T13'ten), B3 / B5a / B6a tezgâh sırası ve takıldıktan sonra ayar vidasına erişim.
2. **Aşama 2 yazılıma bağlı:** ön şarj dizisi ESP32 yazılımında (E9 adım 1–6); yazılım hazır değilse aşama 2 yapılamaz (F5 notu).
3. **Aşama 1 BMS gözlemi kısmi:** F3 takılı olmadan Pololu / SY8205 girişleri devrede değil; tam açılış aşama 2'de.
4. **Kollar aşama 2'de takılı:** F5 son adım olduğu için devreye almada servolar güç alır; metin E3 ön koşulunu (servo hedefleri son konumda)
   ve erişim alanını yazıyor, ama kol hareketinin güvenli olduğu doğrulanmadı.
5. **Denetimin sınırı:** yasak tarama kalıp tabanlı; kalıp dışı bir anlatım ("mantarı devre dışı bırak", "sigortanın yerine tel koy") yakalanmaz.
   "akü … bağlı / takılı" kalıbı geniş: ileride olumsuzlamasız doğru bir cümle ("akü takılı, BMS'i gözle") yanlış bulgu verir, metin
   olumsuzlamayla ya da farklı fiille yazılmalı.
6. **TVS:** veri sayfası Diodes'un (üretimden kalkmış); satıcı ürününün üreticisi doğrulanmadı (KT-F7c-1).
7. **Model / BOM:** ikinci P6KE6V8A, göğüs regülatörü, mini 2 A ve hat sigortası yuvaları modelde yok (KT-F7c-2, -3; K11 açık).
8. **PDF 52 sayfa:** F7b raporundaki "PDF 50 sayfa" ifadesi artık eski; kabul "her adım ≥ 1 sayfa, taşan 0".
   (Düzeltme 1'den sonra 53 sayfa; aşağıda.)

---

# Düzeltme turu 1 (F7c-kontrol: O-1, O-2, D-3, D-1, D-2), 09.11.2026 19:30–19:55

Girdi: `planlama/d158/F7c-kontrol.md` (B: KOŞULLU, kritik 0, orta 2, düşük 4) ve orkestratörün düzeltme listesi. Commit, push, silme,
checkout, reset, stash yok. Bu turda hiçbir dosya ya da klasör silinmedi (`__pycache__` dahil; Python `-B` ve
`PYTHONDONTWRITEBYTECODE=1` ile koşuldu). Önceki hâllerin kopyası scratchpad `f7c/once-d1/`.

## Madde durumu

| # | Madde | Durum | Kaynak |
|---|---|---|---|
| O-1 | Aşama 1 sigorta durumu, "röle kapanmaz" gerekçesi, göğüs dalı, F5'te takılacaklar, zorunlu satır | yapıldı | `elektrik.md:91`, `:360-370` (sigorta listesi), `:338` (F4 → ESP32 VIN), `:441-445` (F1 → K1 ve K2 kontağı; F5 → bobinler), `:458` (GPIO2 = DevKit LED'i), `:62`, `:68` (göğüs dalı, K11) |
| O-2 | Mantar ölçü noktası, GND referansı, kıskaç uyarısı, uçların sökülme anı | yapıldı ("doğrulanmadı" kaldı) | `elektrik.md:235`, `:249-251` (PC817 #1 girişi mantar NC sonrası), `:341` (WAGO yıldız noktası, güç paneli) |
| D-3 | Kollar düşer, PWM = 0, ana anahtar kapalıyken XT60, takı kuralı | yapıldı (aşama 2; takı ve XT60 sırası aşama 1'e de) | `elektrik.md:257` (PWM = 0), `:262`, `:508` (reset → röle bırakır → kollar düşer); `00-genel.md:52` (kural 8) |
| D-1 | Yeni yasak kalıplar, olumsuzlama yalnız aynı yan cümlede, B'nin kaçanları | yapıldı: B'nin 20 denemesinin 20'si yakalanıyor | `rehber_denetim.py` (6) |
| D-2 | "akü … takılı" yanlış alarmı | yapıldı: P1, P2 temiz | `rehber_denetim.py` (6) |
| D-5 | F3 "ölçünce enerjiyi kes" belirsizliği | **yapılmadı** (listede yok; B "sonraki tur" dedi) | — |

## Kaynak doğrulaması (O-1)

`planlama/adim3/elektrik.md` "Sigorta listesi" (`:360-370`) ve "Sigorta dalları" (`:91`):
- Ana 30 A (akü + → her şey, XT60 sonrası); F1 20 A (röle K1 ve paralel ön şarj kolu K2 + 5,6 Ω → anahtarlı bara); F2 15 A yedek;
  F3 5 A kafa 12 V; F4 5 A XL4016 çevre 5 V (ESP32 VIN, sonar, enkoder; `:338`); F5 2 A acil stop / K1 + K2 bobinleri;
  hat sigortaları 7,5 A (XL4016 A), 7,5 A (XL4016 B), 5 A (XL4016 C), anahtarlı baradan; göğüs ekranı mini 2 A; şarj girişi mini 10 A.
- B'nin önerisindeki etiketler kaynakla aynı. "A / B / C" hat sigortaları kaynakta "hat 7,5 A → XL4016 A" biçiminde; metinde
  "XL4016 hat sigortaları (A 7,5 A, B 7,5 A, C 5 A)" yazıldı. F2 (yedek) ve şarj girişi 10 A aşama metnine yazılmadı: F2 bir yük
  beslemiyor, şarj girişi aküyü şarj cihazına bağlar, ilk enerjiyle ilgisi yok.

**"Röle kapanmaz" için seçilen yol: F1 takılı değil (donanım).** Gerekçe:
- K1 ve K2'nin kontaklarını F1 besler (`:441-442`), bobinlerini F5 (`:443-445`). Mantar ölçümü için F5 takılı olmalı (PC817 #1 girişi
  F5 → mantar NC sonrasında), ESP32 F4'le (XL4016 çevre) çalışır. Yani aşama 1'de bobin tarafı enerjili, ESP32 açık.
- ESP32'deki program bilinmiyor; K2'yi süren GPIO2 DevKit'in LED pini (`:458`). Hazır bir LED yakıp söndürme programı K2'yi açıp kapatır.
  "ESP32'de devreye alma yazılımı ya da boş program var" demek kaynağa dayanmaz (yazılımın durumu kaynakta yok, F5 notu "yazılım hazır
  değilse aşama 2 yapılmaz" diyor) ve okuyanın doğrulayamayacağı bir ön koşul olur.
- F1 takılı değilse röle hangi programla çekerse çeksin kontak tarafı enerjisiz: anahtarlı bara, BTS ve XL4016 A / B / C enerjisiz.
  Metin artık "röle kapanmaz" değil "röle K1 ve K2'nin kontakları enerjisiz" diyor ve K2'nin GPIO2 / LED üzerinden tıklayabileceğini yazıyor.
- Göğüs dalı: K11 varsayılanı (a) ana anahtar sonrası, röle öncesi (`:68`). Mini 2 A aşama 1'de takılı değil, boştaki 12 V ucu enerjisiz.
  F3'te ekran fişinden önce, akü ayrık ve ana anahtar kapalıyken takılır. K11 (b) seçilirse dal anahtarlı baraya bağlanır ve F3'teki
  regülatör ölçümü F5 aşama 2'ye kalır (metinde "doğrulanmadı" ile yazıldı).

## Önce / sonra metin

**F1 kontrol (aşama 1).**
- Önce: "İlk enerji, aşama 1 (F1 sonu, kafasız): ana anahtar ve mantar bağlı, ana sigorta takılı; F3 (kafa) sigortası takılı değil, Pi
  enerjisiz. Devreye alma komutu Pi'den gelir (`planlama/adim3/elektrik.md` E3): bu aşamada röle K1 ve K2 kapanmaz, anahtarlı bara
  enerjisiz kalır. Tekerlekler yerden kesik (…T13…); BTS EN = 0. Aküyü XT60'tan tak, ana anahtarı aç: BMS kesiyor mu gözle (röle K1 açık;
  F3 takılı olmadığı için yalnız F4 / F5 girişleri, tam açılış aşama 2'de). Mantar: basınca mantar sonrası F5 hattı 0 V, bırakınca 12 V
  (multimetre; ölçü uçları enerji yokken takılır); röle yine çekmez. Bitince ana anahtarı kapat, aküyü XT60'tan ayır. Devreye alma, ön
  şarj ve motor yön testi F5'te (İlk enerji, aşama 2). Bu aşamalar ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı"
- Sonra: "İlk enerji, aşama 1 (F1 sonu, kafasız): ana anahtar ve mantar bağlı. Saat, yüzük, bileklik çıkar (`planlama/d158/testler/00-genel.md`
  kural 8). Akü XT60 ayrık, ana anahtar kapalıyken ana sigortayı (30 A), F4 (5 A, XL4016 çevre 5 V: ESP32) ve F5 (2 A, acil stop: mantar,
  röle bobinleri) tak. F1 (20 A: röle K1 ve ön şarj kolu K2), F3 (5 A, kafa), XL4016 hat sigortaları (A 7,5 A, B 7,5 A, C 5 A) ve göğüs
  ekranı mini 2 A takılı değil (`planlama/adim3/elektrik.md` sigorta listesi): anahtarlı bara, kafa ve göğüs ekranı dalı enerjisiz, Pi
  enerjisiz. Devreye alma komutu Pi'den gelir (E3). ESP32'deki program bilinmiyor: K2'yi süren GPIO2 kartın LED pini (E9), LED yakıp
  söndüren hazır bir program K2'yi açıp kapatabilir. F1 takılı olmadığı için röle K1 ve K2'nin kontakları enerjisiz, anahtarlı bara
  enerjisiz kalır. Tekerlekler yerden kesik (…T13…); BTS EN = 0. Mantar ölçümü: akü ayrıkken multimetrenin kırmızı ucunu arayüz
  kartındaki PC817 #1 giriş klemensine (mantar sonrası düğüm, E3), siyah ucunu güç panelindeki WAGO GND yıldız noktasına bağla. Ölçü
  kıskacını mantar uçlarına takma. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: BMS kesiyor mu gözle (röle K1 açık;
  F3 takılı olmadığı için yalnız F4 / F5 girişleri, tam açılış aşama 2'de). Mantara basınca PC817 #1 girişi 0 V, bırakınca akü gerilimi
  (12,8–14,4 V). Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Devreye alma, ön şarj ve motor yön testi
  F5'te (İlk enerji, aşama 2). Bu aşamalar, sigorta sırası, ölçü noktası ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı"

**K1 madde 6.** "(aşama 1: ana anahtar, BMS, mantar; röle kapanmaz)" → "(aşama 1: ana anahtar, BMS, mantar; F1 takılı değil, anahtarlı
bara enerjisiz)".

**F3 madde 3.**
- Önce: "3. 11,6" ekranı (kasalı) cebe koy. 12 V fişini takmadan önce regülatör çıkışını yeniden ölç: 12 V (K2'de ayarlandı; ölçünce
  enerjiyi kes). …"
- Sonra: "3. 11,6" ekranı (kasalı) cebe koy. Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranı mini 2 A sigortasını tak (F1 aşama 1'de
  takılı değildi; dal girişi K11'in varsayılanı a: ana anahtar sonrası, röle öncesi; b seçilirse bu ölçüm F5 aşama 2'ye kalır,
  doğrulanmadı). 12 V fişini takmadan önce regülatör çıkışını yeniden ölç: 12 V (K2'de ayarlandı; ölçünce enerjiyi kes). …"

**F5 madde 2 (aşama 2).**
- Önce: "… Akü XT60 ayrıkken F3 (kafa) sigortasını tak. Tekerlekler yerden kesik (…T13…); BTS EN = 0; kolların, kafanın ve tekerlerin
  erişim alanında kimse yok, bir kişi yalnız mantarda (… kural 1 ve 7). Aküyü XT60'tan tak, ana anahtarı aç: BMS kesiyor mu gözle (röle
  K1 açık; F3 / F4 / F5 girişleri, Pololu dahil). … ön koşul (mantar serbest, servo hedefleri son konumda, BTS EN = 0) → … Mantara basınca
  K1 düşer (…), anahtarlı bara kesilir (PC817 #2 HIGH). Mantarı bırak: …"
- Sonra: "… Saat, yüzük, bileklik çıkar (`planlama/d158/testler/00-genel.md` kural 8). Akü XT60 ayrık, ana anahtar kapalıyken F1 (20 A),
  F3 (5 A, kafa) ve XL4016 hat sigortalarını (A 7,5 A, B 7,5 A, C 5 A) tak (`planlama/adim3/elektrik.md` sigorta listesi). Tekerlekler
  yerden kesik (…T13…); BTS EN = 0. Kollar aşağıda başlar: mantara basınca servo gücü de kesilir ve kollar düşer (E3 DTR / RTS notu).
  Kolların erişim alanında ve düşme hattında, kafanın ve tekerlerin erişim alanında kimse yok, bir kişi yalnız mantarda (kural 1 ve 7).
  Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: BMS kesiyor mu gözle (röle K1 açık; F3 / F4 / F5 girişleri, Pololu
  dahil; K11 a ise göğüs ekranı dalı da). … ön koşul (mantar serbest, servo hedefleri son konumda, BTS EN = 0 ve PWM = 0) → … Mantara
  basınca K1 düşer (…), anahtarlı bara kesilir (PC817 #2 HIGH), kollar düşer. Mantarı bırak: …"
- "Kollar aşağıda başlar" kaynakta yok; adımın sonundaki "Bu adımdaki sıra kaynakta yok, doğrulanmadı" kapsamında.

## Denetim (`rehber_denetim.py`) değişiklikleri
- `ZORUNLU` 21 → 23: F1 aşama 1 satırı "röle K1 ve K2 kapanmaz" yerine "röle K1 ve K2'nin kontakları enerjisiz … BTS EN = 0";
  yeni `F1 \(20 A[^)]*\)[^.]*takılı değil` (F1 ve dal sigortaları takılı değil) ve `PC817 #1 giriş klemensine.*WAGO GND.*mantar uçlarına takma`.
- Yasak kalıplar (D-1): "devre dışı bırak", "kısa devre et / yap / oluştur / kur", "yerine tel / kablo / köprü / jumper (+ fiil)",
  enerji önekine "gerilim varken", "sigorta… takılıyken / takılı iken", "XT60… takılıyken / bağlıyken"; fiil listesine "değiştir",
  "bağlantı yap"; önek ile fiil arası 60 → 120 karakter (aşağıdaki J18).
- Olumsuzlama (D-1 a): yalnız eşleşme sonunun yan cümlesinde (virgül, iki nokta ve "ve, ama, fakat, ancak, sonra, ardından, veya,
  ya da, çünkü" ile bölünür) ve ±40 karakterde.
- "akü … takılı" (D-2): yalnız `akü(yü|nün|sü)? (XT60…)? bağlı / takılı …`; "Akü ön takozu … takılı", "Akü kayışları takılı" tutmaz.
- `ASCII_TAMAM`'a bu turun doğru kelimeleri: saat, bileklik, bobinleri, kolu, program, bilinmiyor, pini, kapatabilir, klemensine,
  siyah, panelindeki, dal, ise.
- Bugünkü veride istisna 5 → 4: K2 "akü XT60 ayrık, F3 (kafa) takılı değil" artık kalıba girmiyor; kalan 4 "köprülenmez / köprülenmedi".

## Enjeksiyon (scratchpad `enjekte_d1.py`)

Gerçek verinin (19:44, sha1 `09ca1380e7b3`) ve depodaki `rehber_denetim.py` (`2e9fb8230d9e`) ile `rehber_metin.py` (`96d9182310f8`)
kopyası scratchpad `f7c/denetim-d1-son/`'da; bozma bellek içinde, depo değişmedi. Yakalanma hedeflenen denetimle (yasak, zorunlu, kopya
eki > 0) sayıldı. Temiz kopya: geçti, yasak 0, istisna 4, zorunlu eksik 0 / 23, kopya eki 0. Çıkış 0.

| Grup | Sonuç |
|---|---|
| A'nın E1–E14'ü (E11 yeni metne: "röle K1 ve K2'nin kontakları enerjisiz" → "röle K1 kapanır") | 14 / 14 yakalandı |
| B'nin J1–J20'si (J15, J17, J18 yeni metne uyarlandı) | **20 / 20** yakalandı (ilk turda 12 / 20) |
| D1–D4: yeni zorunlu satırlar (F1 "takılı değil" silindi; F1 (20 A) listeden çıktı; kıskaç uyarısı silindi; "WAGO GND" → "bir GND") | 4 / 4 |
| D5–D9: ek biçimler ("Mantar takılı değil, sigortanın yerine kablo koy", "XT60 bağlıyken kafa fişini değiştir", "kısa devre yap ve …", "Sigortalar takılı iken klemensleri sık", "… devre dışı bırakın, değil mi?") | 5 / 5 |
| Olumsuz: N1–N3, B'nin P1–P4, N4–N8 ("asla devre dışı bırakma", "yerine tel koyma", "kısa devre yapma", "XT60 takılıyken hiçbir fişi sökme", "takılı değil, uçlarını köprüleme") | 12 / 12 temiz |

B'nin kaçanları ayrıntılı: J1 devre dışı bırak, J2 kısa devre et, J3 yerine tel koy, J7 "XT60 takılıyken … sök", J8 "… değiştir",
J10 "takılı değil, uçlarını köprüle" (yan cümle), J11 "sigortası takılıyken … tak", J12 "Gerilim varken … sık": hepsi yasak bulgu.
J18 ön denemede kaçtı: yeni F5 metninde "Ana anahtar açıkken" ile "tak" arasında sigorta listesi var (≈ 85 karakter), 60'lık pencere
yetmedi; pencere 120'ye çıkarıldı, sonra yakalandı. Toplam 43 / 43 yakalandı, 12 / 12 temiz (benzetilmiş ön veride ve gerçek veride aynı).

## Komutlar (saat, çıkış kodu)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 19:3x | `benzet.py` (yeni metin bellek içinde önceki veriye) + `rehber_denetim` | — | önce ASCII 13 (doğru Türkçe kelimeler) → `ASCII_TAMAM`; sonra temiz, zorunlu 0 / 23 |
| 19:3x | `enjekte_d1.py` (benzetilmiş veri) | 1 → 0 | J18 kaçtı → pencere 120; sonra 43 / 43, 12 / 12 |
| 19:44 | süreç 0, boş bellek 2,19 GB, kilit "boş" → kilit "F7c düzeltme 1 (P7.3, A) 2026-11-09 19:44 rehber_uret.py --gorsel-yok …" → `py -3 -B tasarim/freecad/rehber/rehber_uret.py --gorsel-yok` → kilit "boş" (6 bayt, baştakiyle aynı) | 0 | veri 34 s; mesh 288 / 1192, 189.934 üçgen, GLB 2,56 MB, 50 adım |
| 19:45 | `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py` | 0 | ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 23, yasak 0 (istisna 4), kopya eki 0 |
| 19:45 | veri karşılaştırması (scratchpad `karsilastir_d1.py`, önceki veri ↔ yeni) | — | parça farkı 0 / 1192; değişen adım alanları yalnız K1 `is_`, F1 `kontrol`, F3 `is_`, F5 `is_`; üst anahtarlar aynı; `robot.glb` sha1 aynı (`9458b9e67135`) |
| 19:45–19:49 | `py -3 -B tasarim/freecad/rehber/rehber_uret.py --veri-yok` | **0** | 50 / 50, konsol 0, 1192 ↔ 1192, her parça tek adımda; yazdır görüntüsü 50; telefon 7 × 360 / 0; PDF **53** sayfa (devam 3), HTML 53, eşleme tutarlı, taşan yok, en küçük yazı DOM 8,1 / PDF 8,1 pt, 3.915 kB; denetim temiz |
| 19:50 | `py -3 -B -X utf8 tasarim/cad/demo_uret.py` | 0 | 127 sayı anahtarı, 14 karar, 153 kalem, 1192 düğüm, 163 KB |
| 19:50 | `py -3 -B -X utf8 planlama/d158/F9b-dogrula.py` | 0 | GECER (hata 0) |
| 19:50 | `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| 19:50 | `py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` | 0 | GEÇER (hepsi okundu, kötüleşen yok) |
| 19:50 | `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py` | 0 | aynı |
| 19:5x | `enjekte_d1.py` (gerçek veri kopyası) | 0 | 43 / 43, 12 / 12 |

Koşudan sonra FreeCAD süreci 0, `lale-rehber` profilli Chrome süreci 0, kilit "boş".

**Demo:** düzeltme öncesi demo (scratchpad kopyası) ile yeni demo arasındaki tek fark `<script id="kaynak">` içindeki
`rehber/veri/rehber-veri.json` parmak izi (`5ccc1e10af16` → `85a3cc196adb`). Sayı anahtarları, kararlar, kalemler aynı.

**PDF.** 53 sayfa; eşleme: adım i → sayfa i + 1 (0…30), 31 (E4) → 32, 33; 32 (K2) → 34, 35; adım i → i + 3 (33…48); **49 (F5) → 52, 53**.
F5'in yeni aşama 2 metni ilk sayfayı doldurdu, "Erişim notu" bloğu devam sayfasına (53) geçti. En küçük yazı 8,1 pt (PyMuPDF, 53 sayfa),
PDF metninde ve metasında yerel yol 0. Görülen sayfalar (90 dpi): 36 (F1: aşama 1'in tam metni, sigorta listesi, ölçü noktası, kıskaç
uyarısı, uçların sökülmesi), 38 (F3: göğüs 2 A satırı madde 3'te), 52 (F5: aşama 2, sigortalar, kollar düşer, PWM = 0), 53 (F5 devam:
yalnız erişim notu). Sayfa 18 (K1) çizildi, bakılmadı (değişen yalnız madde 6'nın bir yan cümlesi).

**Değişen PNG'ler (bu tur, sha1 karşılaştırması):** `planlama/rehber/goruntu/adim-17.png` (K1), `adim-35.png` (F3), `adim-49.png` (F5),
`telefon-360-adim-35.png`, `telefon-360-adim-49.png`. Öbür PNG'ler (`rehber/goruntu/` dahil) bayt bayt aynı. `adim-35.png` ve
`telefon-360-adim-35.png` ilk turun commit listesinde yoktu, eklendi.

**sha1 (ilk 12, düzeltme öncesi → sonrası):** `rehber_metin.py` ccbf2a8d8c09 → 96d9182310f8; `rehber_denetim.py` 6a1610f22416 → 2e9fb8230d9e;
`rehber-veri.json` 6a813c48f99a → 09ca1380e7b3; `rehber-veri.js` 036bfec75a58 → c3997f7b74a8; `kontrol.json` 59cd5e3e0a89 → 78a767f30e1c;
PDF 554da292f2ed → 0fd7c550afa2; demo d4ae0587c69a → d3f8fcd89029. Değişmeyen: `rehber_veri.py`, `rehber_uret.py`, `yazdir.html`, `robot.glb`, `robot-glb.js`.

## Dokunulan dosyalar (bu tur)
`tasarim/freecad/rehber/rehber_metin.py`, `tasarim/freecad/rehber/rehber_denetim.py`, `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js`,
`planlama/rehber/kontrol.json`, `planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-17.png`, `adim-35.png`, `adim-49.png`,
`telefon-360-adim-35.png`, `telefon-360-adim-49.png`, `tasarim/Robot-Tasarim-Demosu.html` (yalnız `demo_uret.py`), `planlama/rehber/R-gunluk.md`,
`planlama/d158/F7c-gunluk.md`; `planlama/d158/FREECAD-KILIT.txt` (koşu süresince, sonda "boş"; commit'e girmez).

**Güncel commit listesi (paketin tamamı):** ilk turdaki liste + `planlama/rehber/goruntu/adim-35.png` + `planlama/rehber/goruntu/telefon-360-adim-35.png`
(+ B'nin `planlama/d158/F7c-kontrol.md`'si).

## Açıklar (düzeltme 1)
1. D-5 yapılmadı: F3 "ölçünce enerjiyi kes" hâlâ belirsiz (ana anahtar mı, akü mü); bir sonraki metin turuna.
2. "Kollar aşağıda başlar" ve sigortaların takılma sırası kaynakta yok (metinde "doğrulanmadı" kapsamında). Aşama 1'de bobin tarafı
   enerjili olduğu için K2 tıklayabilir; bu bir tehlike değil (kontak tarafı enerjisiz) ama okuyanı şaşırtmasın diye metinde yazıyor.
3. PC817 #1 "giriş klemensi" adı modülün gerçek klemens etiketine göre ölçülmedi (modül gelince bakılacak); ölçü noktası "doğrulanmadı".
4. K11 açık: (b) seçilirse göğüs regülatörü ölçümü F3'ten F5 aşama 2'ye kayar; metin bunu yazıyor, rehber sırası değişmedi.
5. Denetim yine kalıp tabanlı: sözcük seçimi farklı bir talimat ("mantar NC uçlarını birleştir") yakalanmaz; 120 karakterlik pencere
   uzun bir cümlede ilgisiz bir fiili yakalayabilir (bugünkü veride yanlış bulgu 0).
6. PDF 53 sayfa: F5'in devam sayfasında yalnız erişim notu var (taşma değil, kabul "her adım ≥ 1 sayfa").
