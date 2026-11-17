**DÜZELTME GEREKLİ** (tek madde, ucuz; üretimden önce). Kısım 1 ve kısım 2 içerik olarak doğru: uç etiketlerinin 57 kısa adını GLB
konumlarıyla tek tek eşledim, sağ / sol dahil hata yok; IS hesabını baştan yaptım, kayıtla aynı; K66 kayıtları birbiriyle ve kaynakla
tutarlı; onay farkı açıklanıyor, kritik değer farkı 0; kapsam temiz. Ama `kirp()` içindeki kesim denetimi FreeCAD'in gevşek
`BoundBox`'ına bakıyor ve yol 12'nin doğru kesilmiş tüpünde büyük olasılıkla sınırı aşmış görünüp üretimi `SystemExit` ile
durdurur (D1). Düzeltme tek satırlık.

# F10n kontrolü · P10.7b2f (kablo yolu kesimi, uç etiketleri, küçükler; pano kayıt düzeltmeleri, K66)

16.11.2026. Dal `lale-duzeltme`, HEAD = `b5fc255`; paket commit edilmemiş, farkı `git diff b5fc255` ile kendim okudum. Salt okuma:
depoda yalnız bu dosya yazıldı. Sınamalar depo dışında (oturum scratchpad'i `b2f-kontrol\`), bozma denemelerim bellekte ya da
scratchpad'de. FreeCAD ve `rehber_veri.py` / `rehber_uret.py` tam koşusu yok. Önizlemeyi (`onizle.py`'nin `KOK` değiştirilmiş kopyası)
güncel kaynakla `b2f-kontrol\onz2\`'ye yeniden ürettim, çünkü ajanın `b2f\onz\kare` kareleri (09:30–09:40) son veriden (09:52) ve
kısım 2'den eski. Bitişte `git status` başlangıçla aynı (artı bu dosya), depoda `__pycache__` yok.

## D bulguları (düzeltilmeli)

### D1 (engelleyici, üretim) `kirp()` kesim denetimi gevşek `BoundBox` ile; doğru geometride yanlış `SystemExit`

- **Yer:** `tasarim/freecad/rehber/rehber_veri.py:129-130` (`b = c.BoundBox`; `b.YMax > ky + 1e-6 or abs(b.YMin - y0) > 1e-3`),
  ayrıca `:126` (`y0 = s.BoundBox.YMin`).
- **Ne yanlış:** `Shape.BoundBox` eğri yüzlerde sıkı değil: silindir yüzü için parametre (UV) kutusunu, yani VMin / VMax'taki uç
  çemberlerini ve yüzün kesilmemiş eksen uzunluğunu alır. Yol 12'nin tüpü (`taban_parcalar.py:574-581` `tup()`, küre + silindir,
  r = 2,5) kesimde 2→3 parçasında kesiliyor; bu parça neredeyse yatay (dy = 0,24 mm, uzunluk ~ 140 mm). `common()` sonrası silindir
  yüzü kesim düzlemiyle sınırlanır ama yüzün V aralığı ~20 mm'lik kalan parçaya göre kalır; eğik silindirde uç çemberleri kesim
  düzleminin üstüne taşar. Kendi hesabım: kalan yüzün UV kutusu YMax ≈ 197,35, kesim `ky` = 192,5 → denetim "kesimi aşıyor" der.
  Geometri doğru, denetim yanlış.
- **Kanıt:** Aynı dosyanın kendisi bunu söylüyor: `rehber_veri.py:280-281` ("eğri yüzlü parçada BoundBox gevşek … sıkı kutudan
  (optimalBoundingBox)"); ayrıca `planlama/y2/Y2a-gunluk.md:112` ("kaba BoundBox 291,65 gevşek"), `carpisma.py:174`; lale158 /
  taslak-170 de `optimalBoundingBox` kullanıyor. FreeCAD koşturmadığım için "kesin" değil, "yüksek olasılık"; ama denetimin hata
  yönü tek taraflı (yalnız yanlış alarm üretir) ve sonuç 50 dakikalık koşunun boşa gitmesi.
- **Önerilen düzeltme:** `:129` `b = c.optimalBoundingBox()` (ve `:126` için `s.optimalBoundingBox().YMin`); toleransı 1e-6 yerine
  ~0,05 mm yap (üçgenleme payı). İstenirse alternatif: kesilen şeklin köşe noktalarının (`c.Vertexes`) en büyük y'si. Denetimin
  geri kalanı (boş kesim, hacim, `KIRPILAN == CAD_KIRP`) olduğu gibi kalsın. `:133`'teki log satırı gevşek kutuyla yazar, zararsız
  (istenirse aynı değişiklik).

## N notları (bilgi; engel değil)

1. **kirp() geri kalanı doğru.** Kesim yüksekliği kayıtlı noktadan + r (`cad_kirp_y` = 190 + 2,5); yalnız yol 12 etkileniyor
   (`KIRPILAN == CAD_KIRP` denetimi doğru); sonraki noktalar y ≥ 205 olduğundan kopuk parça kalmıyor; taban modül yerleşimi kimlik
   (`arayuz.py:693`), modül-konum denetimi doğru yerde; parça sayısı 1192, 68 / 5 / 1 değişmez; `kablo_kapisi` gevşek YMax ile bile
   K1'de kalır (eşik 300); ağ kodu (`s.Solids[0]`) bileşik sonucu kaldırır. Diğer kablo yolları dokunulmamış.
2. **Uç eşlemesi: 0 hata.** 47 `UC_ETIKET` + 10 `UC_MODELSIZ` adını GLB kutu merkezleriyle eşledim (`b2f-kontrol\uc_esle.py`):
   her "sağ" +X, her "sol" −X (motorlar, BTS'ler, sonarlar, kol servoları `omuz_sag/sol`, `dirsek_sag/sol` modülleriyle, XL4016
   işlev adları). "PC817 modülü → Arayüz kartı" `kablolar.json` `"PC817 modülü (arayüz kartı)"` ile tutarlı. `UC_ORTULU` 10 gerekçesi
   karelerde doğru (gerçekten başka parça / gövde arkasında); dürüst.
3. **Önizleme (onz2, güncel kaynak):** 24 konum, 48 etiket, 46 "yok"; iki kipte hepsi çizildi, çizilmeyen 0. 17.8'de etiket 2
   (Arayüz kartı / PC817) artık direğin üstünde değil, kartın üstünde (eski karede direkteydi). PDF 86 sayfa, en küçük yazı 8,1 pt,
   taşma yok. Sınıra yakın piksel alanları (PX_ESIK 30'un üstünde): 32.1 sol S1 36 px, sağ S1 72 px; 31.9 SY8205 97 px; Dağıtım A / B
   254 / 169 px; 32.4 ESP32 313 px. Gerçek GLB ile değişebilir; üretimden sonra bakılacaklar listesinde.
4. **"Beklenen KALDI" iki sonuç:** `rehber_denetim` depo verisinde 1 (B6a öğe geçmiyor) ve `rehber_kablo --veri` depo verisinde KALDI 2
   (GLB yol 12 YMax 1327,4; `uc_kaynak` yok) yalnız eski üretim verisinden. onz2 verisinde ikisi de GEÇER (zorunlu eksik 0; uç 24 konum
   hata 0; kırpma hata 0). GLB maddesinin gerçekten kapanması D1'in düzeltilip üretimin bitmesine bağlı.
5. **Onay farkı:** HEAD → şimdi 84 opcode, raporun 77 + 8'i (birleşik "değişti" sayımıyla) açıklıyor: kablo 165 → 222 (1 değişti
   `GEO_ISTISNA[12]` → `CAD_KIRP[12]`, +57 UC), liste 210 → 212, metin 1117 → 1121 (10 değişti, 9 eklendi, 5 silindi). Birimli değer
   kümeleri aynı, yalnız sayılar ("5 V", "12 V", "6 V" adlardan ve K66 cümlelerinden) arttı. **Kritik değer farkı 0** doğru.
6. **Birleşim:** GEÇER, 1095 → 1099; beklenen eklenen 15 / 15, silinen 11 / 11 gerçek farkla aynı.
7. **ASCII izin listesi gevşetilmemiş:** eklenen "sayfada karenin listesindeki" ve 14 kelimenin hepsi doğru Türkçe yazım; bozma
   denemem ("cevre", "Diyotun") yakalandı.
8. **ZORUNLU yalnız B6a `is_` cümlesini kapsıyor**, kontrol maddesindeki diyot yön cümlesini değil: kontrolü silmek / ters çevirmek
   yalnız onay kaydında yakalanıyor (zorunluda değil). Onay kaydı kapı olduğu için yeter; istenirse ZORUNLU'ya kontrol cümlesi de eklenir.
9. **K66 küçükleri:** metinde "VIN ≈ 4,5–4,6 V", hesabım 4,55–4,65 V (1N5819 düşümü 0,35–0,45 V, 5,0 V girişte); yuvarlama içinde.
   `elektrik.md:286` yeni K66 maddesi `## K4` başlığına boş satırsız bitişik (Markdown'da liste başlığa yapışır, görünüm sorunu yok
   ama düzen için bir boş satır iyi olur). Diyotun kart üzerindeki yeri kayıtlarda gerçekten açık; metin bunu açık söylüyor.
10. **B6a'da X01 (Arayüz kartı ucu) etiketlenmiyor**, çünkü X01 K1'de çiziliyor; kural (yerin metni ∩ orada çizilen) gereği doğru,
    bilgi olarak.
11. **32.4 `DEMET_ALT` ESP32 USB'ye `saydam=("Gövde direği",)`** eklenmiş, `F10n-gunluk.md`'de yazmıyor. Değişiklik doğru (kare
    okunur oldu), yalnız günlüğe bir satır.
12. **Tarihsel / bilinen eskiler:** `F9c-uret.py` P10.7 özeti 120.852,43 gösteriyor (o anın değeri, tarihsel); demo sayfası ve depo
    `sonuc-rapor.html` eski (bilinen, üretim sonrası).
13. **IS eşiği ve kILIS yayılımı:** 500 mV ↔ 2,43 mA ↔ nominal kILIS 8500'de ~20,7 A. kILIS'in parça parça yayılımı (veri sayfasında
    geniş) metinde anılmıyor; eşik "hesap, ölçüm değil" diye işaretli olduğu için kabul edilebilir, tezgâhta bakılacak.

## Kısım 2 ayrıntı (bağımsız yeniden hesap ve okuma)

- **IS hesabı (kendi sonucum):** kart IS direnci birleşik 500 Ω (varsayım) ∥ bölücü (6,8k + 5,1k = 11,9k) → 479,8 Ω; bölücü oranı
  5,1 / 11,9 = 0,4286; pin = 205,6 Ω × I_IS. 4 mA → 0,822 V; 4,5 mA → 0,925 V; 7 mA → 1,439 V; normal 5,6 A (kILIS 8500) → 0,135 V.
  Rb 1 kΩ + R2 2,2 kΩ durumu → 220 Ω (4 mA'de 0,88 V); 470 Ω durumu → 193,8 Ω (0,775 V). `pin-haritasi.md:8`, `:276-277`, `:351`,
  `:387` ile birebir. Varsayımlar varsayım diye yazılmış; 4 / 4,5 / 7 mA hatırladığım veri sayfası değerleri, `pin-haritasi.md:36`
  bunu ikinci el diye işaretliyor.
- **K66:** diyot yönü (anot 5 V hattı, katot VIN) doğru; `elektrik.md`, `kablolar.json` (X01 "5 V" damarı not / teyit / kaynak
  `elektrik.md:286`, satır doğru), `kablolar.md` (üretilmiş, `--kontrol` güncel), `maliyet.json` (yalnız 1N5819 adet 1 → 2), kuyruk
  (K66 satırı, bölümü, sayım 48 / 18 / 66) ve rehber B6a birbiriyle tutarlı. "Düşenler / ayakta kalanlar" listesi `kablolar.json`
  `yuk_butcesi` ve `parca_beslemesi` (PCA9685 3V3) ile aynı. Toplamlar: ara 105.089,07 → 105.090,29; genel 120.852,43 → 120.853,83;
  koşullu 126.423,90 → 126.425,31; 125 kalem.
- **Reset / ReSpeaker cevapları** (`elektrik.md` E3 :264, `kablolama-on-kararlar.md`) pano #32 / #33 ve `cevap-konu7.md` /
  `cevap-konu8.md` ile aynı. **`is_sol` / `is_sag` notu** (`sag-sol-karari.md`) yönü doğru (donanım "sol" = −X).
- **Satır sayıları korunmuş** (`elektrik.md` 592 / `pin-haritasi.md` 465 / 460 göndermeleri), `kablolar.json` satır göndermeleri
  doğru satırı gösteriyor.

## Koşturulan sınamalar (hepsi depo dışı çıktıyla)

| Sınama | Sonuç |
| --- | --- |
| `kablolar_uret --kontrol` | 0 |
| `kablolar_denetim` / bozma | GEÇER / 172 yakalandı |
| `rehber_denetim --kaynak` / bozma | 0 / 302 / 302 |
| `rehber_denetim` veri (depo verisi / onz2) | 1 beklenen (B6a) / 0 |
| `rehber_kablo` / bozma | GEÇER / 93 / 93 |
| `rehber_kablo --veri` depo verisi / bozma | KALDI 2 beklenen / 105 / 105 |
| `rehber_kablo --veri` onz ve onz2 / bozma | GEÇER / 108 / 108 |
| `kol --yazma` | GEÇTİ |
| `F10l-birlesim.py` | GEÇER (1095 → 1099, 15 / 15, 11 / 11) |
| `F10d-dogrula.py --yalniz-uc` bozma | 5 / 5, 9 / 9 |
| `F9c-uret --cikti` (dışarı) / `F9c-dogrula` | 0 / 0 |
| `node --check` (`app.js`) | 0 |
| Onay kaydı farkı (kendi difflib'im, `onay_fark2.py`) | 84 opcode, kritik değer farkı 0 |
| Önizleme yeniden üretimi (onz2) + PDF | 24 konum, 48 etiket, 86 sayfa, taşma yok |

**Kendi bozma denemelerim** (bellekte; `ADIM` ve `ADIM_HAM` birlikte değiştirildi): B6a yön ters, B6a cümlesi silindi, 1N5819 →
1N4007 (zorunlu + onay); B6a kontrolü silindi / ters (yalnız onay, N8); F5 ve K1 kontrolü silindi (onay); ASCII "cevre", "Diyotun"
(ascii + onay); `UC_ETIKET` BTS takası, XL4016 A → B (onay); `UC_MODELSIZ` değişikliği (onay); `CAD_KIRP` son = 3 (geo + onay);
`CAD_TUP_R` 30 (onay). Hepsi yakalandı. K2 alt adım değişiklikleri içe aktarmada türetildiği için bellek bozması geçersizdi; o durum
için onay kaydına dayandım.

**Kapsam:** K50 / K60 / K61 dokunulmamış; CAD model dosyaları ve `kod/` değişmemiş; `rehber/veri`, `goruntu`, `planlama/rehber`
elle düzenlenmemiş; eski kirli dosyalar (09.11 / 03.11 tarihli) ve kökteki 5 sıfır baytlık dosya yerinde; farkta sahip takma adı yok;
`git status` paket dosya listesiyle aynı.

## Bakılamayanlar

- FreeCAD koşusu: gerçek `kirp()` (D1 hesapla gösterildi, koşturulmadı), gerçek GLB, `.brp` içindeki üçgenleme, tam üretim ve zincir.
- Koyu tema; gerçek tarayıcıda etkileşim (`u` tuşu, `?uc=0`) yalnız `RehberTest.ucEtiket` üzerinden önizlemede.
- BTS7960 veri sayfasının kendisi (değerler hatırlanan / ikinci el); tezgâh davranışı (diyot düşümü, IS gerilimi).

## Üretimden sonra gözle bakılacaklar

1. Log'da `CAD_KIRP: … y … -> ~192,5` satırı; GLB'de yol 12'nin YMax'ı ~192,5 (1327,4 değil); K1 ana karesinde hayalet çizgi yok.
2. `rehber_kablo --veri` gerçek veride GEÇER, `rehber_denetim` veri modunda 0.
3. Sınıra yakın uç etiketleri: 32.1 (S1 sol / sağ), 31.9 (SY8205), 32.4 (ESP32), Dağıtım A / B; etiket parçanın üstünde mi.
4. 17.8 etiket 2 kartın üstünde (direkte değil); 17.10, 14, 17.12 ve adım 0 tanım kutusu; yazdırma sayfalarında "Uçlar:" /
   "Uç karede görünmez:" satırları ve K2 ana kare lejantı.
