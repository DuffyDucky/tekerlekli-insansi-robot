# F6b kontrolü (P6.2: tek baskı analizi, tüm parçalar): bağımsız kontrol ajanı B, 09.11.2026

**Genel karar: KOŞULLU GEÇER.** Commit'ten önce A'nın `F6b-gunluk.md`'de kısa bir metin düzeltmesi yapması gerekiyor (O-1). Zincir, JSON ve FreeCAD yeniden koşusu gerekmiyor.

Brief'in kabul ölçütlerinin hepsi bağımsız olarak doğrulandı:
- Tek JSON'da 62 tür / 72 adet var, her parça bir kez geçiyor. Liste, JSON ve BOM aynı.
- Kapak uyuşmazlığının kök nedeni FCStd geometrisinde yeniden ölçüldü.
- `baski-listesi.md` betikle bu JSON'dan üretiliyor. Kopyada zincir bayt bayt aynı çıktı verdi.
- `F4c-dogrula.py` 0, `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0.
- A'nın kolon yöntemi, B'nin FCStd mesh'lerinde 12/12 parçada aynı sayıları verdi. Ayrıca B'nin BRep yöntemiyle (A'nınkinden bağımsız) VESA, omuz yuvası ve kol çatalında %0,2 içinde tuttu.

Kritik bulgu yok. Bir orta bulgu var:
- **O-1.** KT-F6b-3e'nin "göğüs bandı cep üst kenarına 45° pah / kemer" önerisi geometriyle tutarsız. Cep duvarı tam kesiyor. Tavanın altı 207 mm boyunca tablaya kadar boş ve 160 / 148 mm açık uçlu açıklık kalıyor. 2,8 mm kalınlık yönünde pah bu açıklığı taşımaz. "≈ 2 × 13 g" tasarrufu dayanaksız.

Düşük bulgular D-1…D-8. Hiçbiri sayıyı ya da zinciri değiştirmiyor.

Kısaltmalar: `TF/` = `tasarim/freecad/`, `SPB/` = B'nin klasörü (depo dışı): scratchpad `f6b-b`.

B'nin depoya yazdığı tek dosya bu dosya. Kilit dosyasına yalnız kilit kuralı için yazıldı. Git yazma, silme ve kaynak değişikliği yok. Zincir betikleri depoda değil, `SPB/kopya/` içinde koşuldu. `git status` ve `git diff --stat` koşu öncesi ve sonrası, F6b dosyaları için aynı. Arada F7a'nın C commit'leri 887bcfe (16:40:53) ve 3946ad5 girdi; bunlar yalnız F7a dosyalarını içeriyor, F6b dosyası yok.

**B'nin FreeCAD koşusu (tek, kısa):** `SPB/f6b_b_olc.py` → `SPB/f6b_b_olc.json` (+ 12 mesh `SPB/mesh_*.npz`).
- Süre 16:37:21–16:37:43, 22 s, rc 0.
- Önce: çalışan FreeCAD süreci 0, boş bellek 2,48 GB, kilit "boş".
- Koşu boyunca kilitte "F6b-B (P6.2 kontrol) f6b_b_olc.py 2026-11-09 16:37" satırı vardı; bitince "boş" yapıldı. 16:47'de yeniden okundu: hâlâ "boş", değişme saati 16:37:43. 10 dakikada geri dönmedi.
- Sonra boş bellek 2,65 GB.
- FreeCAD 1.1.4, yerel `.robot-cad\run_fc.py` başlatıcısı.
- FCStd'ler yalnız açıldı, kaydedilmedi. Değişme saatleri F6a'dakiyle aynı: 14:27–14:29, kafa 08:54.

Takma ad taraması: ad, F6a B'nin yöntemiyle `git show 647cafc^:TF/kafa/kafa_parcalar.py` satır 6'dan çalışma anında türetildi (`SPB/ad_tara.py`). Ekrana ve dosyaya yazılmadı; arama deseni geçici dosyadan okundu ve dosya silindi.

## Madde tablosu

| # | Madde | Kontrol yöntemi | Sonuç | Kanıt |
|---|---|---|---|---|
| 1a | `baski_analiz_ortak.py` yöntemi | 772 satır okundu. Çekirdek `kolon_analizi` (`:188-332`), bölgeleme (`:285-297`), kütle (`:335-339`), yön kuralı (`parca_analiz` `:428-452`) incelendi. | **GEÇER (not D-1).** Çıkıntı eşiği 45° − 1° tolerans: `n_z < −cos 44°` (`:274-275`), yani 44–45° arası yüz serbest. Belgelenmiş. Yön kuralı tek: tasarım yönü; X2D'ye sığmazsa sığan adaylardan en az destekli. Bütün parçalar sığdığı için seçim hep tasarım yönü. Destek alanı = destek isteyen kolon × 0,25 mm². Hacim = kolon boyu (alttaki üst yüzeye ya da tablaya) × 0,25. Köprü / şerit kuralı eski yöntemle aynı: ≤ 15 mm serbest; 1,25 mm yarıçaplı diskle aşındırma, yani ≤ 2 mm şerit serbest, 2,5 mm destekli. Kütle formülü 62 parçanın hepsinde JSON'la tutuyor; `toplam` satırlardan yeniden üretiliyor. | B'nin yeniden hesabı: formül uyuşmazlığı 0, toplam 7.668,9–7.726,7 g |
| 1b | Sessiz katman hatası bu betikte olabilir mi; P1.5 kalıbı | Kod ve duyarlılık koşusu (`SPB/duyarlilik.py`: 5 ızgara kaydırması + H 0,25) | **GEÇER (not D-1).** Ana yöntemde kesit ve 2B boolean yok; mesh'e dikey ışın atılıyor. Bu yüzden "yüze teğet kesit" hatası burada oluşmaz, P1.5 kaydırması da gerekmez. Kesit yalnız `kapak_tani` içinde, eski hatayı bilerek yeniden üretmek için kullanılıyor (`:497-546`, kaydırmasız; doğru). Benzer risk ızgara fazı: eşiğe yakın şeritlerde sonuç ızgaraya bağlı (D-1). Kesişim sayısı tek olan kolonlar `parite_hatasi` olarak sayılıyor ama sonucu etkilemiyor; yalnız omuz bandı sağ/sol 100'er kolon, ikisinde de destek 0. | `SPB/duyarlilik.json` |
| 1c | `Y2b-baski.py` ve F4c betiklerinin farkı | `git diff`, parça parça | **GEÇER (not D-6).** `Y2b-baski.py` (+17/−22) yalnız `baski-analiz.json` okuyor ve destek g'yi topluyor; ayrıca docstring 1,65 → 1,58 m, CF 11 → 12 tür. `F4c-partiler.py`: kaynak anahtarı, yön ve X2D tek analizden; destek notu = JSON alan + g + elle tarif. `F4c-dogrula.py`: anahtarlar tek analizden, yeni kontrol 6, yön denetimi birleşti. `F4c-liste.py`: kaynak zinciri metni, F6b önce/sonra bölümü (`git show 4d1898a`), kapak ve kafa notları. Brief dışı değişiklik yok. | `git diff` |
| 1d | Tarama kaynakları; yeni betik adı | `carpisma_kos.py kontrol`; `kaynak_listesi()` | **GEÇER.** rc 0, "izlenen 17 dosyanin ozetleri kayitla ayni". `kaynak_listesi()` 17 dosya; yeni betik aralarında yok, adı `*_lib.py` değil. Modül analizleri ve FCStd'ler değişmedi (`git status`). | `SPB/carpisma_kontrol.out` |
| 1e | Regresyon | `regresyon.py --yazma`; önce/sonra sha1 | **GEÇER.** rc 0, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)". `regresyon.json` ve `regresyon-son-kosu.json` değişmedi. | `SPB/regresyon.out` |
| 2 | Kapak kök nedeni | B'nin FreeCAD koşusu, FCStd geometrisi (`kabuk-montaj.FCStd` K013). Çerçeve JSON'daki 4 haneli `yukari` ile kuruldu (bkz. not). | **GEÇER (not D-2).** **Eğim:** kenar yüzleri n_z ±0,0397, asin = **2,2753°**. **Flanş üstü:** yüz 14'ün en alt köşesi **1,498817** = 1,5 · cos 2,2753°. Plaka üstü 2,997635 = 3 · cos. **Kaydırılmış kesitler:** 1,55/2,55, 1,7/2,7, 1,8/2,8, 1,95/2,95 → cut **5,006 mm²**, common 19.662,64; dördü aynı, z'den bağımsız geometrik sabit. A'nın çerçevesinde 5,011; fark %0,1. **Flanş düzlemi yakınında kesit bozuluyor:** B'nin çerçevesinde z 1,499 / 1,5 / 1,5005 → "result shape is null" / "Wire is not closed" ×2. A'nın tam çerçevesinde aynı düzlem sessiz biçimde ters normalli yüz veriyor (`kapak_tani.boolean_deneme["1.5-2.5"].alt`: n_z −1, dz 1,19 µm, tolerans 0,00119, tel kapalı); B bu dökümü okudu ve sayılar kendi içinde tutarlı. **Gerçek destek 0:** B'nin iki bağımsız yöntemi de 0 verdi; BRep'te z > 0,3'te aşağı bakan düz yüz yok, kolon yöntemi 6 ızgarada 0. P1.5 kalıbı bu hatayı yakalamazdı: teller kapalı, kalıp yalnız açık telde kaydırıyor (`TF/kabuk/kabuk_montaj.py:332-359`). Not: kapağın `yukari`sı eğri yüzey normalinden geliyor (`TF/kabuk/kabuk_parcalar.py:263`). 4 haneye yuvarlanınca çerçeve ≤ 0,003° döndü (tabla yüzü 0…0,0065 mm). Bu µm farkı hata kipini değiştirdi (sessiz ters yüz → istisna), kök nedeni değiştirmedi. | `SPB/f6b_b_olc.json` `kapak` |
| 3a | 72 adet ↔ JSON ↔ BOM, her parça bir kez | `SPB` betiği: listenin `baski-analiz/parcalar[i]` satırları; BOM `Baski` satırları; JSON (modül, ad) sayımı | **GEÇER.** Liste 62 satır / 72 adet, 62 farklı indeks, çift 0, eksik 0. BOM 62 satır. JSON 62 tür / 72 adet, çift 0. `F4c-dogrula` 2, 3, 6 da geçiyor. | komut çıktısı |
| 3b | Büyük farkların açıklaması | `fark[]` (72 satır) tarandı; `buyuk` = 2 satır | **GEÇER (not D-7).** Üst arka kapak: destekli → desteksiz, 85,0 → 85,1 g (madde 2). VESA: +%28,1. B'nin hesabı: yeni `parca_g` 113,1 = eski 113,0; fark tam destek 31,7 g. B'nin bağımsız BRep ölçümü de bunu doğruluyor: tek yüz (yüz 28), 15° eğik, z 31,75–57,63, izdüşüm 3.809,2 mm² (A 3.806,5), hava hacmi 166,7 cm³ (A 166,4). Eşik sınırında (%10,0 / %9,9) iki küçük satır işaretlenmemiş (D-7). | `SPB/f6b_b_olc.json` `brep` |
| 3c | En az 5 parçayı B ölçtü | BRep (aşağı bakan düz yüzü aşağı uzat, parçadan çıkar, yüze değen hava hacmi): 7 parça. A'nın kolon yöntemi B'nin FCStd mesh'lerinde: 12 parça. | **GEÇER (not D-1).** Kolon yöntemi FCStd mesh'lerinde 12/12 parçada A'nın sayılarını birebir verdi; FCStd geometrisi analiz geometrisiyle aynı. BRep ↔ A: **VESA** 3.809 ↔ 3.807 mm², 166,7 ↔ 166,4 cm³. **Omuz yuvası** 2.259 ↔ 2.262 mm², 60,2 ↔ 60,4 cm³ (5 bölge birebir). **Kol çatalı** düz yüz 1.097 ↔ 1.100 mm², 58,8 ↔ 59,0 cm³; A'nın öteki iki bölgesi silindir altı, BRep düz yüz ölçüyor. **Arka kafa sağ** dikiş dili yüz 134: 2.942 ↔ 3.056 mm², 4,41 ↔ 4,58 cm³ (yüz eni 16 mm = `Y2b-baski.py` `DESTEK_NOT`). **Göğüs bandı sağ / sol** cep tavanı şeridi (15° eğik, en 2,8 mm): 426 / 396 ↔ 381 / 357 mm², 88,2 / 81,8 ↔ 78,8 / 73,8 cm³. A %10–11 düşük (D-1). **Üst arka kapak** 0 ↔ 0. | `SPB/f6b_b_olc.json`, `SPB/duyarlilik.json` |
| 3d | FCStd hacmi = analiz hacmi | B: 5 FCStd'deki bütün `Tur == "Baski"` nesneleri; örneklem yerine tamamı | **GEÇER.** FCStd'de tam 62 baskı nesnesi var (taban 4, kabuk 34, kafa 14, dirsek 4, omuz 6). JSON dışı nesne 0, tekrar eden etiket 0, Placement hep birim, hepsi geçerli. A'nın `fcstd_hacim_mm3` ile en büyük fark 0,05 mm³ (yuvarlama). | `SPB/f6b_b_olc.json` `hacim` |
| 4 | Zincir | `SPB/kopya/` (planlama/, TF/test/, baskı JSON + betikler, BOM); git okuması `GIT_DIR` ile gerçek depodan, yalnız okuma. Sırayla Y2b → partiler → liste → dogrula. Ayrıca depoda `F4c-dogrula.py` (yalnız okur). | **GEÇER.** 4/4 rc 0. Dört çıktının (`Y2b-baski.json`, `F4c-partiler.json/.md`, `baski-listesi.md`) sha1'i depodakiyle **bayt bayt aynı**. `F4c-dogrula.py` kopyada ve depoda rc 0, "SONUC: GECTI" (1, 2, 6, 3, 4a, 4b, 5a, 5b). **Kontrol 6 anlamlı:** her (modül, ad) tam bir kez; satır sayısı = Y2b; adet toplamı = Y2b = BOM; her satırda g / sa / desteksiz / destek g / ölçü / yön JSON'la aynı. Sınırı: JSON'un FCStd'ye bağlılığını denetlemiyor; o JSON içindeki `hacim_esit`'te ve madde 3d'de. | `SPB/zincir_*.out`, `SPB/f4c_dogrula_depo.out` |
| 5a | Önce/sonra tablosu | `git show 4d1898a:planlama/y2/Y2b-baski.json` ↔ şimdiki | **GEÇER.** Değerler B'nin hesabıyla aynı: filament 7.604,8–7.662,4 → 7.668,9–7.726,7 g (+64,1 / +64,3); PETG +28,3; CF +35,8 / +36,0; süre +1,68 / +1,66 sa; destekli 14 → 13. Partiler: P1 +61,1, P2 +3,4, P3 +1,3, P4 −1,7 g. | komut çıktısı |
| 5b | +64 g destek filamentinden mi | Satır satır ayrıştırma | **GEÇER (not D-8).** +64,1 g = yeni destek 124,5 − eski omuz desteği 58,0 (`omuz-baski.json` `destek_filament_g` × adet) = **+66,5 g** net destek, artı −2,4 g yuvarlama (kabuk satırları eskiden tam sayıydı). PETG +28,3 ≈ göğüs bantları +29,4 + kafa sağ 1,3 − yuvarlama. CF +35,8 ≈ VESA +31,8 + omuz +4. | |
| 5c | × 0,15 makul mü; 30° eşik | A'nın `kolon_analizi` B'nin mesh'lerinde `ACI = 30` ile (destekli 9 tür + 3 karşılaştırma) | **GEÇER (not D-8).** 0,15 omuz_baski ile aynı. İnce, uzun destekte (göğüs bandı: 207 mm yüksek, 2,8 mm kalın) alt sınıra yakın; büyük hacimde (VESA 166 cm³) ağaç destekte üst sınıra yakın. Belirsizliği ±%50 almak doğru olur; A bunu açık 1'de yazmış. **30° sonucu neredeyse değiştirmiyor:** destekli yüzler 0° ya da 15° eğimli. Değişen yalnız kol çatalı 66,65 → 63,83 cm³ ve göğüs bandı sağ 81,78 → 81,66. Toplam destek ≈ −1,1 g (124,5 → ≈ 123,4). 45°'de desteksiz olan hiçbir parça 30°'de destekli olamaz (destek kümesi küçülür). A'nın açık 2'deki "daha az destek verir" sözü niceliksiz; etkisi %1. | `SPB/duyarlilik.json` `B30` |
| 5d | PETG-CF payı ve KT-F6b-1 | `F4c-partiler.json` | **GEÇER (not D-8).** CF parça + kupon 1.369,8–1.553,2 g → 1,37–1,55 kg. 1,5 kg'de pay +130,2 / −53,2 g (önce +166 / −17). 2,0 kg'de üst durum payı **446,8 g** (A "≥ 447"). 0,8 → 0,9 senaryosu: CF parçaların `parca_g` toplamı 528,6 g × 0,125 = 66,1 g (A ile aynı). K42 a (2,0 kg) yine yeter; destek ±%50 olsa bile CF desteği 91,9 g ± 46 g, pay ≥ 400 g kalır. | |
| 6a | KT-F6b-2 | Metin ve eski alanı okuyanlar (`git grep`) | **KOŞULLU (D-4).** Öneri tutarlı (şimdi b, sonra a). Eksikleri: (1) c seçeneği (z 0,47) bu kapağı rastlantıyla düzeltir, kalıcı düzeltme değil. P1.5 kaydırması kapalı telli ters yüzü yakalamaz; eski yöntem kalacaksa kesit yüzünün normali ve düzlemselliği (dz > 1e-6) denetlenmeli. (2) Eski `baski` alanını okuyan yerler yalnız `lale158_kontrol.py` değil: `TF/kabuk/kabuk_rapor.py:128-129` (kapağı "destekli" sayar), `TF/dirsek/dirsek_rapor.py:93-95`, `planlama/adim5/baski_toplam.py:16`, `planlama/d158/F4c-kontrol-sayim.py:37`. | `git grep` |
| 6b | KT-F6b-3 | Bölgeler, BRep ve kaynak geometri | **KALIR (O-1)** yalnız e için. a, b, c, d tutarlı: VESA 15° flanş altı tek yüz; omuz yuvası manşon tavanı z 45,2 (40 × 30 mm, 48,4 cm³ → ≈ 9 g); kol çatalı horn kulağı z 58,5 (44 × 32 mm, 58,8 cm³ → ≈ 11 g); göbek −Y 14,5 cm³ → 2,8 g, temas 1.070 mm². Tasarruf tahminleri a ≈ 26, b 2 × 9, c 2 × 10 makul. **e tutarsız (O-1).** | `SPB/f6b_b_olc.json` `brep` |
| 7 | Commit listesi | §8 ↔ `git status --porcelain`; `comm` | **KOŞULLU (D-5).** A'nın listesindeki 11 dosyanın hepsi durumda var, fazla yok. Eksik: `planlama/d158/F6b-brief.md` (izlenmeyen; brief gereği girmeli). Dışlamalar doğru: F7a dosyaları zaten commit'li (887bcfe, 3946ad5), `dongu-158.md`, kabuk görselleri (K23, 14:28), `FREECAD-KILIT.txt`, `montaj/yerlesim-kontrol.json` (F6b değil), yeni `F7b-brief.md`. Takma ad: F6b'nin 12 dosyasında 0. Depo genelinde (`git grep -il`, izlenen) yalnız kapsam dışı 3 dosya: `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html` (F6a ile aynı). Başka öğrenci ya da danışman soyadı 0. F6b dosyalarındaki büyük harfli sözcükler tek tek tarandı; kişi adı olarak yalnız "Ahmet" var. Kullanıcı yolu yalnız `F6b-gunluk.md:93`'te başlatıcı yolu; aynı yol commit'li F0/F1 brief ve günlüklerinde de geçiyor. | `SPB/ad_tara.py`, `SPB/st.txt`, `SPB/ekle.txt` |
| 8 | Kilit olayı (dongu: "F7a çıktısı etkilenmedi mi → B bakar") | F6b ve F7a günlükleri, FCStd zaman damgaları, depo | **GEÇER (not D-3).** A'nın 15:54 koşuları F7a'nın 15:54:09–15:54:34 veri koşusuyla çakıştı. Ama F7a'nın commit'lenen çıktıları sonraki tam koşulardan geliyor (15:59:50–16:02:45 ve düzeltme turu 16:28–16:30; `F7a-gunluk.md:28`, `:133-134`). FCStd'ler kaydedilmedi; depoda `_ara` gibi bir artık yok. Etki yok. | `F7a-gunluk.md` |

## Bulgular

**Kritik: yok.**

### O-1 (orta). KT-F6b-3e: "cep üst kenarına 45° pah / kemer" önerisi geometriyle tutarsız

Yer: `planlama/d158/F6b-gunluk.md:162` (§5 satır 6) ve `:178-180` (KT-F6b-3 e, "e ≈ 2 × 13 g").

Kanıt:
- **Cep duvarı tam kesiyor.** `TF/kabuk/kabuk_parcalar.py:98` `S.cut(gogus_yer(box(..., -GE_T - 1.0, 6.0)))`; duvarın normal kalınlığı `GE_T` 2,9 mm (`:81`).
- **Destek yüzü dar bir şerit.** BRep'te yüz 61 (sağ) / 112 (sol): 15° eğik şerit, XY eni 2,8 mm (duvar kalınlığı), boyu 159,3 / 147,3 mm, z 206,5–207,3.
- **Altı tablaya kadar boş.** Altındaki hava 207,3 mm yüksek. Bant içinde tavanın altında malzeme yok: cep bandın alt kenarından açık.
- **Bir ucu boşta.** Sağdaki bölge x ≈ −8,5…151 aralığında (`merkez_parca` x 71,2, boy 159,5). Bir ucu dikiş tarafında; orada öbür yarı ayrı bir parça.

Yani bu bir konsol ya da kenar çıkıntısı değil, 148–160 mm'lik açıklığın tavanı:
- Kalınlık yönündeki 2,8 mm'yi 45° pahlamak açıklığı taşımaz.
- Açıklığı 45° kemerle kapatmak 80–160 mm yükseklik ister; cebin görünür kenarını da değiştirir.
- "≈ 2 × 13 g" tasarrufunun dayanağı yok.

Bu metin yalnız günlükte. `baski-listesi.md` ve F4c çıktılarına geçmemiş; `F4c-partiler.py:95` TARIF metni ("cep üst kenarı (köprü 160 mm)") doğru.

Düzeltme: KT-F6b-3 e'yi şu seçeneklerle yeniden yaz:
- (i) Destek kalsın: 15,6 / 14,1 g PETG; dilimleyicide yalnız bu bölgeye, boyalı destek.
- (ii) Yatık baskı (±X): 1,6 g. A'nın kendi notu geçerli: yüzey ve bant tutarlılığı bozulur.
- (iii) Geometri seçeneği istenirse: cebin alt kenarına kırılabilir kurban köprü ya da ince destek duvarı. Bu bile 160 mm'lik bir köprü bırakır; PETG için uzun.

Tasarruf tahmininden e'yi çıkar. KT-F6b-3'ün toplam tasarrufu buna göre a + b + c ≈ 26 + 18 + 20 g olur.

### D-1 (düşük). Eşiğe yakın şeritlerde sonuç ızgara fazına bağlı (göğüs bantları)

A'nın `kolon_analizi`'si (`baski_analiz_ortak.py:42` `JIT`, `:41` `H`) B'nin mesh'lerinde 5 ayrı ızgara kaydırması ve H 0,25 ile koşuldu (`SPB/duyarlilik.json`):

| Parça | A (JIT 0,4865/0,3172) | 5 kaydırma aralığı | H 0,25 | BRep (kesin, düz yüz) |
|---|---|---|---|---|
| Göğüs bandı sağ | 81,8 cm³ | 81,2–98,4 | 97,4 | 93,7 |
| Göğüs bandı sol | 73,8 cm³ | 72,6–87,8 | 87,7 | 82 (şerit) + 5,1 (z 12 yüzü, A'da serbest) |
| Yüz kabuğu sağ | 1.228 mm² / 1,85 cm³ | 1.227–1.992 / 1,85–2,40 | 1.957 / 2,36 | – |
| VESA, omuz yuvası, göbek, tambur, kol çatalı, arka kafa sağ | – | ≤ %1 | ≤ %1 | %0,2 |

A'nın seçtiği faz göğüs bantlarında alt uçta kalıyor. Gerçek değer ≈ +%15: sağ +2,9 g, sol +2,6 g, toplam ≈ +5,5 g. Bu filament PETG; K42'ye etkisi yok, toplam 7,67–7,73 kg yuvarlamasını da değiştirmiyor.

Sağdaki z 12 yüzü (alt kenar çıkıntısı) A'da destekli (686,5 mm²), soldaki benzeri serbest (BRep 623,5 mm²). Bu ayrım 6 ızgarada da aynı kaldı, yani yalnız faz değil, gerçek bir genişlik farkı (≈ 2 mm şerit eşiği). Etkisi ≈ 0,6–1 g.

Öneri: `F6b-gunluk.md` §7'ye açık olarak ekle ("göğüs bantlarının desteği ızgaraya duyarlı, ≈ +%15; dilimleyicide bakılmalı"). Yöntem değişikliği gerekmiyor.

### D-2 (düşük). Kapak tanısındaki "karşılaştırma" kontrol parçası iddiayı göstermiyor

Yer: `F6b-gunluk.md:61`. İddia: "3 mm düz arka servis kapağında flanş üstü tam 1,5'te, kesit doğru yönde (n_z +1), `cut` 0".

`kapak_tani.karsilastirma_arka_servis_kapagi` verisi bunu desteklemiyor:
- z 1,5 kesiti hâlâ flanşta: 8 tel, 30.242,9 mm² = flanş alanı. z 1,6'da da 8 tel, z 1,9'da 1 tel. Yani flanş üstü 1,6 ile 1,9 arasında.
- z 0,5 kesiti bozuk: n_z −1, dz 0,289, tolerans 0,281.
- Bu kesitler `BoundBox.ZMin`'e göre alınmış (`baski_analiz_ortak.py:637`), eski yöntemin mesh zmin'ine göre değil.
- B'nin ölçümünde bu parçada 0,449 mm toleranslı bir kenar var. Kesit, kutu ve bu parçanın tabana yakın dilimleri güvenilmez (B'nin çerçevesinde de z 0,5 / 1,5 kesitleri bozuldu).

Kök neden kanıtı bundan etkilenmiyor: üst arka kapak ölçümü, ince kesit ve boolean dökümü yeterli. Öneri: `:61` satırını "karşılaştırma parçası (düz arka kapak) BoundBox zmin'e göre kesildiği ve bir kenarı 0,45 mm toleranslı olduğu için kontrol yerine geçmiyor; eski yöntem bu parçada 0 sorun buldu (`kabuk-analiz.json` `baski[12]`)" diye yaz.

### D-3 (düşük, süreç). Kilidin "OneDrive ile geri dönmesi" kanıtlanmadı; geri dönüşü büyük olasılıkla A yaptı

`F7a-gunluk.md:35-36`: F7a kilidi 15:54:34'te "boş" yaptı. Kilit 15:55:39'da eski içeriğe ("F7a 2026-11-09 15:54 …") döndü; F7a bunu OneDrive'a bağladı.

`F6b-gunluk.md:19-20`'ye göre ise A 15:55'te "kilide F7a'nın metnini aynen geri yazdı". O sırada F7a'nın süreci bitmişti (`:20`). Yani 15:55:39'daki geri dönüş büyük olasılıkla A'nın geri yazmasıydı; F7a'nın gördüğü bayat satır buradan geliyor. Bu geri dönüş için OneDrive'ı gösteren başka bir kanıt yok. B'nin 16:37:43'te "boş" yaptığı kilit 10 dakika sonra hâlâ "boş"tu.

Bayat kilit kuralı ("satır var, süreç yok → bayat") yine zararsız. Ama gerekçesi (`F6b-gunluk.md:24`, `dongu-158.md` günlük satırı) düzeltilmeli. Öneri: `F6b-gunluk.md` §0'a bir satır ekle: "15:55:39'daki geri dönüş benim geri yazmamdı; F7a o sırada kilidi bırakmıştı. Doğrusu kilidi 'boş' bırakmaktı." F7a çıktısına etki yok (madde 8).

### D-4 (düşük). KT-F6b-2 iki noktada eksik

Madde 6a'da ayrıntılı. Özet: c seçeneği rastlantısal; P1.5 kalıbı kapalı telli ters yüzü yakalamaz. Eski alanı okuyan dört betik daha var: `kabuk_rapor.py:128-129`, `dirsek_rapor.py:93-95`, `adim5/baski_toplam.py:16`, `F4c-kontrol-sayim.py:37`. KT-F6b-2'ye eklenmeli. `kabuk_rapor` yeniden koşulursa kapağı yine "destekli" gösterir.

### D-5 (düşük). Commit listesinde `F6b-brief.md` yok

`F6b-gunluk.md` §8 yeni dosyalarda `F6b-brief.md`'yi saymıyor. Dosya izlenmiyor; brief gereği girmeli. Aşağıdaki C listesinde var.

### D-6 (düşük). `F4c-liste.py` metninde JSON'dan gelmeyen sabit sayılar

Yer: `planlama/d158/F4c-liste.py:164-167`. Sabit yazılmış sayılar:
- yüz sağ 12,3 cm², arka sağ 30,6 cm², ≈ 1,3 g, "1,2–2,3 mm";
- kapak için 2,27°, 1,4988 mm, 1,2 µm, 5,01 mm².

Bugün doğrular; B'nin hesabı: 1.228,2 / 3.056,0 mm², 0,4 + 0,9 g. Ama `baski-analiz.json` değişirse sessizce eskir; `F4c-dogrula.py` bunları denetlemiyor. Şimdilik değiştirme: değişirse `baski-listesi.md` baytları da değişir. Sonraki F4c işinde JSON'dan üretilsin.

### D-7 (düşük, bilgi). Eşik sınırındaki iki küçük fark

`fark[]` içinde iki satır işaretlenmemiş:
- Hoparlör kelepçesi 5,0 → 4,5 g (−%10,0, eşik `> 10`). Eski kabuk değeri tam sayıya yuvarlanmış; neden yuvarlama.
- Hoparlör kabı arka, KY 8,1 → 7,3 g (−%9,9). KY 05.11 geometrisi ve kütle × 1,05.

İkisi de eşiğin hemen altında ve açıklanabilir; ayrıca yazılması gerekmiyor.

### D-8 (düşük, metin). Küçük sayı ve ifade düzeltmeleri

- `F6b-gunluk.md:168`: "pay ≥ 447 g" → "≥ 446,8 g" (1.500 + 500 − 1.553,2).
- §4 / §6: "+64 g destek filamenti" için kesin ayrışım +66,5 g net destek (124,5 − 58,0 eski omuz desteği) − 2,4 g yuvarlama.
- `:185` açık 2: "30° daha az destek verir" → "30° ile toplam destek ≈ −1,1 g (%1); destekli yüzler 0° ya da 15°" (B ölçümü).
- `:184` açık 1'e ekle: CF desteği 91,9 g; ±%50 belirsizlikte K42 a payı ≥ 400 g kalır.

## Genel karar

**KOŞULLU GEÇER.** Kabul ölçütleri bağımsız olarak geçti. Sayılar, zincir, JSON, kapak kök nedeni ve tarama / regresyon bütünlüğü için düzeltme gerekmiyor.

Commit'ten önce yalnız `F6b-gunluk.md`'de metin düzeltmesi gerekiyor:
- O-1 zorunlu.
- D-2, D-3, D-4, D-8 aynı turda önerilir; dakikalar sürer.

Düzeltmede `F6b-gunluk.md` dışında dosyaya dokunulmamalı. Özellikle betikler, JSON ve `baski-listesi.md` aynı kalmalı. O zaman zincir yeniden koşulmaz; B'nin dar yeniden kontrolü (diff okuması + `F4c-dogrula` 0) yeterli.

KT-F6b-1 (K42 a değişmez) ve KT-F6b-2 (b şimdi) sayısal olarak doğru. KT-F6b-3 a–d karar kuyruğuna gidebilir; e, O-1 düzeltmesinden sonra gitmeli.

## A için düzeltme listesi (yalnız `planlama/d158/F6b-gunluk.md`; betik, JSON, liste, tarama kaynağı ve FreeCAD yok)

1. **O-1 (zorunlu).**
   - `:162` (§5 satır 6) öneri sütunu: "geometri: cep üst kenarını 45° pah ya da üst kenara kemer" → "cep tavanı 148–160 mm açık uçlu açıklık (cep duvarı tam kesiyor, `kabuk_parcalar.py:98`); pah işe yaramaz. Destek kalsın (dilimleyicide yalnız bu bölge) ya da yatık baskı (±X, 1,6 g; yüzey bedeli)".
   - `:178-180` KT-F6b-3: e'yi buna göre yeniden yaz, "e ≈ 2 × 13 g" tahminini çıkar.
2. **D-2.** `:61` "Karşılaştırma" maddesini D-2'deki gibi düzelt.
3. **D-3.** §0'a kilit geri dönüşünün nedenini ekle; `:24`'teki OneDrive gerekçesini "kanıtlanmadı" diye işaretle.
4. **D-4.** KT-F6b-2'ye (`:172-176`) iki ek: (a) c seçeneği rastlantısal, P1.5 kapalı telde kaydırmaz, eski yöntem kalacaksa yüz normali / düzlemsellik denetimi; (b) eski alanı okuyan dört betik.
5. **D-8.** `:168` "≥ 446,8 g"; `:184-185` açık 1–2'ye B'nin sayıları; §7'ye D-1 (göğüs bantları ızgara duyarlılığı ≈ +%15, ≈ +5,5 g PETG).
6. Bitince: `py -3 planlama/d158/F4c-dogrula.py` → 0. Öteki 11 F6b dosyasının sha1'i düzeltmeden önce ve sonra aynı olmalı. `F6b-gunluk.md` izlenmediği için `git diff`'te görünmez; B onu doğrudan okur.

## C için onaylı `git add` listesi

**O-1 düzeltmesinden ve B'nin dar yeniden kontrolünden sonra.** 13 dosya: 8 değişik + 5 yeni (bu dosya dahil). B, durumda olup bu listede olmayan her yolun aşağıdaki dışlama listesinde olduğunu `comm` ile denetledi (`SPB/st.txt` ↔ `SPB/ekle.txt`; eksik 0, fazla 0).

```
git add tasarim/freecad/lale158/baski_analiz_ortak.py tasarim/freecad/lale158/baski-analiz.json \
  planlama/y2/Y2b-baski.py planlama/y2/Y2b-baski.json \
  planlama/d158/F4c-partiler.py planlama/d158/F4c-partiler.json planlama/d158/F4c-partiler.md \
  planlama/d158/F4c-liste.py planlama/d158/F4c-dogrula.py planlama/baski-listesi.md \
  planlama/d158/F6b-brief.md planlama/d158/F6b-gunluk.md planlama/d158/F6b-kontrol.md
```

**Dışlama (F6b değil):**
- `planlama/dongu-158.md`. Bu kontrolün brief'i gereği dışarıda. Not: `dongu-158.md` günlüğünde "`dongu-158.md` F6b C ile commit'lenecek" yazıyor; çelişkiyi orkestratör çözmeli.
- `tasarim/freecad/kabuk/gorsel/*.png` (13 dosya, 14:28, K23).
- `planlama/d158/FREECAD-KILIT.txt`.
- `tasarim/freecad/montaj/yerlesim-kontrol.json`.
- `planlama/d158/F7b-brief.md`, `planlama/d158/F5-pano-govde.txt`, `planlama/d158/F5b-pano-govde.txt`.
- `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `tasarim/freecad/montaj/lale_dongu_ac.bat`.
- `kvkk/`, `rapor/`, `raporlar/` (4 dosya), `tubitak-2209b/`, `tasarim/solidworks/`.
- F7a dosyaları 887bcfe ve 3946ad5'te zaten commit'li.

C'ye not: bu dosyalarda "LF → CRLF" uyarısı var. `git add` çalışma kopyasını değiştirmez. C commit'ten önce checkout, reset ya da stash uygulamamalı (F6a-kontrol D-7 ile aynı uyarı; bu dosyalar tarama kaynağı değil).

## Kanıtlar (komut → çıktı, özet)

```
FreeCAD (tek koşu) 16:37:21–16:37:43, rc 0, süreç 0, bellek 2,48 → 2,65 GB      → SPB/f6b_b_olc.out, .json
  hacim: 62/62 eşit (max |Δ| 0,05 mm³), FCStd'de 62 baskı nesnesi, JSON dışı 0
  kapak: eğim 2,2753°, flanş üstü 1,498817 (=1,5·cos), cut 5,006 ×4 çift; z 1,499/1,5/1,5005 kesit hatası
  brep: VESA 3809,2 mm² / 166723 mm³; omuz yuvası 2259,0 / 60232; kol çatalı 1109,7 / 58821;
        göğüs sağ 1082,9 / 93673, sol 1019,1 / 86952; arka kafa sağ 3728,8 / 66744 (fazlası yüz 4: z 99,9, 653 mm²; A'nın yönteminde serbest bölgede, köprü/şerit kuralı)
py -3 SPB/duyarlilik.py (A'nın kolon_analizi, FCStd mesh'leri)                     → 12/12 A ile aynı; 30°: −1,1 g; JIT/H duyarlılığı yalnız göğüs bantları
SPB/kopya: Y2b-baski.py → F4c-partiler.py → F4c-liste.py → F4c-dogrula.py         → rc 0/0/0/0; 4 çıktı sha1 = depo; SONUC: GECTI
py -3 planlama/d158/F4c-dogrula.py (depo, yalnız okur)                               → rc 0, SONUC: GECTI
py -3 tasarim/freecad/carpisma_kos.py kontrol                                         → rc 0, 17 özet aynı
py -3 planlama/d158/regresyon.py --yazma                                              → rc 0, GEÇER; regresyon dosyaları sha1 aynı
SPB/ad_tara.py                                                                        → F6b 12 dosyada takma ad 0; git grep -il: kapsam dışı 3 dosya
git status --porcelain ↔ SPB/ekle.txt (comm)                                          → eksik 0, fazla 0
```

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

**Karar: GEÇER.** O-1 kapandı. D-1, D-2, D-3, D-4, D-5 ve D-8 günlükte doğru işlendi. D-6 (`F4c-liste.py` sabit sayıları) ve D-7 (eşik sınırındaki iki satır) bilerek bırakıldı; öneriye uygun, engel değil. Yeni bulgu: kritik 0, orta 0, düşük 1 (D-9). FreeCAD kullanılmadı.

## Madde sonuçları

| # | Madde | Yöntem | Sonuç |
|---|---|---|---|
| 1 | `F6b-gunluk.md` farkı | Dosya izlenmediği için `git diff` boş. Fark, ilk kontrolde alınan kopyayla (`SPB/kopya/planlama/d158/F6b-gunluk.md`) `diff` ile çıkarıldı. | **GEÇER.** Değişen yerler yalnız şunlar: §0 D-3 paragrafı; §2 karşılaştırma (D-2); §3 başlatıcı yolu kısaltıldı; §5 satır (6) ve KT-F6b-3 e (O-1); KT-F6b-1 "≥ 446,8 g" (D-8); KT-F6b-2 ekleri (D-4); §7 açık 1, 2 ve yeni 7 (D-8, D-1); §8 `F6b-brief.md` (D-5); yeni §9. Başka satır değişmedi. Metinler B'nin sayılarıyla aynı: 2,8 mm / 207 mm / 148–160 mm; a–c ≈ 26 + 18 + 20 = 64 g; 91,9 g ± 46; −1,1 g (124,5 → 123,4); 81,2–98,4 / 72,6–87,8 cm³; dört betik ve satırları. "e için tasarruf tahmini yok" doğru. `:24`'teki OneDrive cümlesi yerinde duruyor ama hemen altındaki paragraf onu "kanıtlanmadı" diye işaretliyor; yeterli. |
| 2 | 11 dosyanın sha1'i | B kendi aldı; A'nın §9 tablosuyla ve B'nin ilk kontrol kopyasıyla karşılaştırdı | **GEÇER.** 11/11 A ile aynı ve ilk kontroldeki kopyayla aynı. Yani ilk kontrolden beri F6b'nin betik, JSON ve liste dosyaları değişmedi. |
| 3 | Denetimler | Depoda | **GEÇER.** `F4c-dogrula.py` rc 0 "SONUC: GECTI"; `carpisma_kos.py kontrol` rc 0 (17 özet aynı); `regresyon.py --yazma` rc 0 "GEÇER". (`SPB/t1_*.out`) |
| 4 | Yerel kullanıcı klasörü yolu; takma ad | Commit'e girecek 14 dosyada `Users\`, kullanıcı adı, `AppData` arandı. Takma ad `SPB/ad_tara.py` yöntemiyle (çalışma anında türetilir) arandı. | **GEÇER (not D-9).** `F6b-gunluk.md` 0. Bu dosyada 2 yol vardı: `SPB` tanımı ve başlatıcı; "scratchpad `f6b-b`" ve "yerel `.robot-cad\run_fc.py`" diye kısaltıldı, şimdi 0. Kalan tek yer `planlama/d158/F6b-brief.md:9` (D-9). Takma ad 14 dosyada 0. |
| 5 | Kesin `git add` listesi | `git status --porcelain` ↔ liste (`comm`) | Aşağıda. 14 dosya. Durumda olup listede olmayanların hepsi dışlamada. Yeni: `tasarim/freecad/rehber/rehber_metin.py` değişik (F7b alanı) ve `F7b-brief.md`; ikisi de dışarıda. |

### D-9 (düşük). `F6b-brief.md:9`'da başlatıcının yerel kullanıcı klasörü yolu

Brief orkestratörün dosyası; B'nin yazma alanı dışında, düzeltilmedi. Aynı yol daha önce commit'lenmiş F0/F1 brief ve günlüklerinde de geçiyor. Orkestratör ya commit'ten önce `F6b-brief.md:9`'u "yerel `.robot-cad\run_fc.py` başlatıcısı" diye kısaltır ya da yolu proje alışkanlığı olarak kabul eder. Bu sha1'i değiştirir ama başka hiçbir dosyayı etkilemez.

## C için kesin `git add` listesi (tek blok, 14 dosya)

```
git add tasarim/freecad/lale158/baski_analiz_ortak.py tasarim/freecad/lale158/baski-analiz.json \
  planlama/y2/Y2b-baski.py planlama/y2/Y2b-baski.json \
  planlama/d158/F4c-partiler.py planlama/d158/F4c-partiler.json planlama/d158/F4c-partiler.md \
  planlama/d158/F4c-liste.py planlama/d158/F4c-dogrula.py planlama/baski-listesi.md \
  planlama/d158/F6b-brief.md planlama/d158/F6b-gunluk.md planlama/d158/F6b-kontrol.md \
  planlama/dongu-158.md
```

Commit dışı:
- `planlama/d158/F7a-*` (commit'li) ve `planlama/d158/F7b-*` (F7b paralel çalışıyor).
- `tasarim/freecad/rehber/` (F7b), `tasarim/freecad/kabuk/gorsel/*.png` (13 dosya, K23), `tasarim/freecad/montaj/yerlesim-kontrol.json`.
- `planlama/d158/FREECAD-KILIT.txt`, `planlama/d158/F5-pano-govde.txt`, `planlama/d158/F5b-pano-govde.txt`.
- `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `tasarim/freecad/montaj/lale_dongu_ac.bat`.
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`.

C'ye not:
- `dongu-158.md` orkestratör tarafından yazılmaya devam ediyor. C, `git add` anındaki hâlini alır.
- Checkout, reset ya da stash yapılmamalı (LF/CRLF).
- Commit'ten sonra `py -3 planlama/d158/F4c-dogrula.py` ve `carpisma_kos.py kontrol` → 0 olmalı.

**Commit mesajı önerisi (tek satır):**
`Lale P6.2: tek baskı analizi (baski_analiz_ortak.py → baski-analiz.json, 62 tür / 72 adet, destek dahil 7,67–7,73 kg); üst arka kapak desteksiz (kesit hatası), F4c zinciri tek analizden (F6b)`
