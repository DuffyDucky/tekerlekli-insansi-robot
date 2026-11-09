# F4c kontrol (P4.3 baskı listesi + P8.2 baskı partileri): ajan B, 09.11.2026

Brief: `planlama/d158/F4c-brief.md`. A'nın günlüğü: `planlama/d158/F4c-gunluk.md`. B, A'nın betiklerine dayanmadan saydı. Bağımsız sayım
betiği `planlama/d158/F4c-kontrol-sayim.py` (çıktısı `F4c-kontrol-sayim.json`), analiz JSON'larını, BOM'ları ve git'i okuyor. Yeniden üretim
denemesinden önce A'nın 4 çıktısı ve `baski_listesi_guncelle.py` scratchpad'e kopyalandı, sha256'ları alındı. Denemeden sonra 5 dosyanın da
sha256'sı aynı çıktı (`sha256sum -c`: hepsi OK), yani geri yazmak gerekmedi. FreeCAD kullanılmadı, git'e yazılmadı.

## Karar: **KOŞULLU GEÇER**

Sayılar, kaynak zinciri, "eski analiz" taraması, malzeme, parti toplamları ve yeniden üretim bağımsız sayımla doğrulandı. Commit'i engelleyen
bir hata yok. İki koşul var:
1. **KT-F4c-2'nin M5 gerekçesi yanlış** (B-1). M5 ısıl gömme somun yalnız PETG-CF parçalarda değil; ön kol gövdesi (PETG) de M5 alıyor. Bu
   yüzden M5 kuponunun iki malzemede de basılması gerekiyor ve önerilen adet **M5 13 değil 21** olmalı. Bu düzeltme K43 metnine girmeli; aşağıdaki
   K43 taslağı düzeltilmiş hâli. Günlük satır 156 ve 159–160 C'den önce düzeltilmeli ya da C bu kontrol dosyasıyla birlikte commit etmeli.
2. **Göğüs ekranı çerçeveleri ve VESA taşıyıcı da satın alınan parçaya bağlı** (B-2). VESA taşıyıcı Parti 1'de "hemen" basılacak gibi duruyor,
   ama 11,6" ekran kasasındaki VESA deliklerinin yeri doğrulanmadı. Üç parça, hub ve hoparlör parçaları gibi "parti içinde sona, ekran gelince"
   notunu almalı. Liste metnine (`baski-listesi.md:128-131`) ve `F4c-partiler.py` `META`'ya P6.1'de ya da C'den önce eklenmeli. Toplamları
   değiştirmiyor.

## İddia tablosu

| # | İddia (A) | Yöntem (B) | Sonuç | Kaynak |
|---|---|---|---|---|
| 1 | 72 parça (03.11'de 65); PETG 6,45 kg; PETG-CF 1,16–1,22 kg; toplam 7,60–7,66 kg; 158,2–159,4 sa; +7 parça: 2 hoparlör kabı, hoparlör kelepçesi, 4 QLED tırnağı; `robot-bom.csv` 62 kalem / 72 adet birebir | Kendi betiği: 4 modül analizi (`baski`) + `omuz-baski.json`, adet `robot-bom.csv`'den (dirsek analizi sağ kolu sayıyor; BOM ×2). PETG-CF kümesi model (`malzeme="PETG-CF"`) + 03.11 listesinin işaretli 11 türü. 03.11 değerleri `git show fa49caa` | **DOĞRU.** 62 tür, **72 adet**, 7.604,6–7.662,4 g, 158,22–159,42 sa, PETG 6.446,6 g, PETG-CF 1.158,0–1.215,8 g (12 tür, 18 adet), 14 destekli. BOM ile ad kümesi aynı, adet farkı yalnız dirsek ×2. Yeni 7 parça tam olarak iddia edilenler; kalkan parça yok. 03.11: 65 / 7.627,2–7.684,4 g / 158,70–159,88 sa, fark −22,6 / −22,0 g ve −0,48 / −0,46 sa. 72 parçanın hepsi X2D'ye sığıyor (en büyüğü 235 mm, göğüs bandı) | `F4c-kontrol-sayim.json` `toplam`, `yeni_parcalar`, `adet_fark_analiz_bom`, `x2d_disi` |
| 2 | "Eski analiz" satırı yok; her analiz geometri kaynağından yeni (kafa 05.11; F1a'ya göre geometri değişmedi) | Dosya zamanı + `git log -1` (analiz ↔ `*_parcalar.py`, `*_lib.py`, `arayuz.py`). Kafa için `git diff d26c7e7 HEAD` (kafa10_lib, kafa7_parcalar, kafa_lib, arayuz). Ayrıca 09.11 03:32'de güncel kaynaktan kurulan `robot-bom.csv`'deki kafa kütleleri ile 05.11 kafa analizinin `kutle_g` değerleri karşılaştırıldı (`montaj/moduller.py:190-191` kafayı `kafa_parcalar`'dan kuruyor) | **DOĞRU.** **Kabuk:** analiz 09.11 01:18, `kabuk_parcalar.py` 08.11 20:34. `kabuk_montaj.py` 02:17'de değişmiş, ama analizdeki `kesit_kaydirma` alanı düzeltilmiş kodun çıktısı (`409d521`). `arayuz.py` 02:38 farkı yalnız OMUZ `durdurucu` ve akü kütlesi. **Kafa:** analiz 05.11 17:01, kaynaklar 08.11. Fark yalnız yorum, ad ve `SECENEK` (varsayılanı eski sabitlerle aynı). 14 kafa parçasında BOM kütlesi − analiz kütlesi = **0,0 g**. **Omuz:** `omuz-baski.json` 03:25 (girdi FCStd 03:20:54) > `omuz_parcalar.py` / `arayuz.py` 02:38. `omuz-analiz.json` 07:31 hacimleri `omuz-baski` ile aynı. **Taban, dirsek:** analiz 09.11 03:29–03:31 > kaynak | `git log`, `date -r`, `F4c-kontrol-sayim.json` `kafa_kutle_fark_bom_eksi_analiz_g` |
| 3 | VESA taşıyıcı modelde PETG-CF; eski Renk tablosu beyaz PETG diyordu | Kaynak okundu, `git log -S` | **Modelde DOĞRU:** `kabuk_parcalar.py:375-376` `malzeme="PETG-CF"` (`bcaa6df`, 04.11). **F1b kararı yok:** F1b günlüğünde/kontrolünde ve karar kuyruğunda VESA malzemesi geçmiyor. A bunu doğru yazmış. Tutarsızlık daha önce `F0-gunluk.md:61`, `P0.1-siniflandirma.md:95` ve `qled-cerceve-tasarim-notu.md:140`'ta not edilmiş. Malzeme Ahmet'in kararı değil, modelcinin seçimi (B-5) | `kabuk_parcalar.py:374-376`, `Y2b-baski.py:11-12` |
| 4 | Parti toplamları = liste (72); her parçanın bir partisi var; atama `proje-plani.md` ve M6 ile tutarlı | `F4c-dogrula.py` 4a/4b koşuldu. B toplamları kendi sayımıyla karşılaştırdı. Atamalar `proje-plani.md:40-66` ve `M6-montaj-sirasi.md` §2 (adım 4, 16, 19, 20, 23, 26, 27, 29, 31, 33–37, 40–47) ile okundu | **DOĞRU, iki not var.** 27 + 25 + 9 + 11 = 72; kg ve sa Y2b `toplam.parti` ile aynı. Parti 2: servo/horn parçaları; Parti 3: QLED kabukları, iskelet ve 4 tırnak; Parti 4: etek ve H1/H2, akü takozu Parti 1 arasında. Bunlar plana uyuyor. Yanlış partide parça yok. Ama Parti 1'de satın alınan parçaya bağlı olup "sona bırak" notu almayan 3 parça var: göğüs çerçeveleri ve VESA (B-2). Parti 2'de ise servo/horn'a bağlı olmayan 4 tür var: El, boyun adaptörü, rulman yuvası, S1 kaset kapağı (B-7, yanlış değil) | `F4c-partiler.json`, `proje-plani.md:44-66`, `M6-montaj-sirasi.md:97-140` |
| 5 | Parti 0 ≈ 7,3 sa (plan ≈ 3 sa); K31 A/B/C doğru yansımış | STL hacimleri B'nin kendi kodu (binary STL, işaretli hacim) ile hesaplandı. `m7-kupon-sonuc.json` okundu. Süre `test/README.md` yöntemiyle hesaplandı. K31 metni `karar-kuyrugu.md`'den | **DOĞRU.** A 20,46 cm³ → 26,0 g; B 69,21 → 87,9 g; C/D1/D2/E JSON ile aynı. Toplam 257,6–420,6 g, **7,32–11,96 sa**. Plandaki 3 sa = C bir kez + D1 + D2 + E = 104,1 g → 2,96 sa (`m7` `toplam` 178 dk). K31 tablosunda A (Ø3,8–3,9 → kupon değişmez), B (Ø4,8–4,9 → kupon uymaz, FreeCAD), C (ruthex Ø4,0–4,2 → uyar, tedarik yetişmez) ve M5 (Ø6,7–6,8 ↔ kupon Ø6,2–6,6 uymaz) K31 ile aynı. Kupon listesi makul. Alt değerde yöntem karışık (B-6) | `F4c-partiler.json` `partiler.0`, `karar-kuyrugu.md` K31 |
| 6 | KT-F4c-1: ihtiyaç 1,33–1,52 kg ↔ 1,5 kg; +0,5 kg makara `kalemler[109]` fiyatıyla +1.114,03 TL (×1,15 = 1.281,13) | `maliyet.json` okundu; `tl` alanının birim fiyat olduğu `adim5/maliyet_toplam.py:19` (`adet × tl`) ile doğrulandı | **DOĞRU.** `kalemler[109]` = PETG-CF, adet 3, `tl` 1.114,03 (birim), `secenek` "yazici"; `pay` 0,15 → 1.281,13. Parça + kupon CF 1.333,8–1.517,2 g; 1,5 kg'de pay +166,2 … −17,2 g; D2'siz +69,0 … +207,6; 2,0 kg'de +482,8 … +666,2. Çelişki de doğru not edilmiş: `F8a-siparis.md:78` "filament satın alınmaz", `maliyet.json` ise sayıyor | `maliyet.json` `kalemler[109]`, `pay` |
| 7 | KT-F4c-2: M3 177, M5 13 (21) gerekli ↔ plan M3 168, M5 6 | Modül BOM'ları (taban 2, kabuk 106, kafa 29, dirsek 2 × 2, omuz `omuz-analiz.json` `bom` 9 × 2 = 18 → M3 159; M5: kafa 1, dirsek 2, omuz 2 = 5). Kupon delikleri `tolerans_kuponu.py:8-9` ve `m7` `kupon_c_delikler`. M5'in hangi parçada olduğu model kaynağından okundu | **M3 DOĞRU, M5 gerekçesi YANLIŞ.** M3: 159 + 2 × (4 + 5) = **177** ✓. M5: dirsek M5'i **ön kol gövdesinde** (`dirsek_parcalar.py:235` `g.cut(insert_hole(5…))` → `:242` "On kol govdesi" **PETG**; M6 adım 44 "M5 pim (yanaktaki ısıl gömmeye)"). Kafa M5'i eğme çatalında (CF), omuz M5'i göbekte (CF). 5 M5'in 2'si PETG'de. A'nın "M5 yalnız PETG-CF parçalarda" cümlesi (`F4c-gunluk.md:156`) tutmuyor. M5 kuponu iki malzemede gerekli: **5 + 2 × (3 + 5) = 21** (B-1) | `F4c-kontrol-sayim.json` `isil_gomme` |
| 8 | `baski_listesi_guncelle.py` yamasız 19 metin satırı farklı; Y1–Y7 yamasıyla aynı; betik değiştirilmedi | B'nin kendi koşturucusu, scratchpad'de ayrı ağaç kurup betiği alt süreçte çalıştırdı: yamasız ve YAMA'lı, her biri iki kez. `git status`, `git log` ve sha256 | **DOĞRU.** Yamasız: 19 +/− satır; parça satırı farkı 0. Farklar başlık tarihi, üst bölüm ("kafada 7\" ekran", boş tablo), "3,31–3,31 kg / ≈ 69–69 sa" ve Parti 3 etiketi "7\"". YAMA (11 değişiklik, her eski metin tam bir kez): fark 0. İki koşu arasında da fark 0 (sabit nokta; yamasız da şu an sabit). Betik `git status`'ta temiz, son commit `bcaa6df`; sha önce ve sonra aynı | scratchpad `betik_dene.py` çıktısı |
| 9 | A yalnız `baski-listesi.md` ve `Y2b-baski.json`'u değiştirdi, `F4c-*` ekledi; takma ad yok; `tasarim/freecad/` ve `kod/` değişmedi | `git status`, `git diff --stat`. Brief'ten (07:49:53) yeni dosyalar `find -newer` ile bulundu. Eklenen satırlarda ve `F4c-*`'te takma ad ve büyük harfli özel ad taraması yapıldı | **DOĞRU.** Brief'ten sonra değişenler: A'nın 2 M + 6 yeni dosyası; ayrıca `dongu-158.md` (08:15, döngü yöneticisi), `F2-gunluk.md`, `F2-rapor.html`, `karar-kuyrugu.md` (F2 C) ve `F6a-brief.md` (yeni, A'nın değil). `tasarim/` ve `kod/` altında brief'ten yeni dosya yok. Önceden değişik olanlar: `kabuk/gorsel/*.png` (03.11 21:35), `montaj/yerlesim-kontrol.json` (03.11 21:23), `lale_dongu.*` (30.10). Takma ad: eklenen satırlarda 0, `F4c-*`'te 0. Başka öğrenci ya da danışman soyadı 0. Kişi olarak yalnız "Ahmet" geçiyor; "hoca" sözcüğü ad olmadan geçiyor | `git status`, `find -newer` |
| 10 | `F4c-dogrula.py` çıkış 0; zincir (Y2b → partiler → liste → doğrula) idempotent | B zinciri iki kez koştu ve her koşudan sonra 5 dosyanın sha256'sını önceki değerlerle karşılaştırdı | **DOĞRU, bir notla.** `F4c-dogrula.py`: 7 kontrolün 7'si GEÇTİ, çıkış 0. Zincir `PYTHONIOENCODING=utf-8` ile iki koşuda rc 0 0 0 0; 4 çıktının ve betiğin sha256'sı ilk değerle aynı (yalnız dosya zamanı değişti). **Ama** stdout yönlendirilince (cp1254) `Y2b-baski.py` `print`'te `☐` karakterinde `UnicodeEncodeError` ile **rc 1** veriyor ve JSON'u yazamadan duruyor (B-3) | scratchpad `sha-*.txt` |

## Bulgular

### Kritik
Yok.

### Orta
- **B-1 · K43 (KT-F4c-2) M5 adedi 13 değil 21 olmalı.** Gerekçe yukarıda, iddia 7'de. Plan M5 6 → 21 = +15 × 6,35 = **+95,25 TL** (A'nın hesabı +44,45 TL idi; taban
  fiyat `F8a-siparis.md:147`). Gerekirse en azından C kuponu PETG'de M5 ile basılır: 5 + 8 + 5 = 18. M3 177 doğru. Düzeltilecek yer
  `F4c-gunluk.md:156, 159-160`. Liste ve parti dosyalarında insert adedi geçmiyor.
- **B-2 · Göğüs ekranı çerçevesi sağ/sol ve VESA taşıyıcı (Parti 1) satın alınan 11,6" ekrana bağlı.** VESA deliklerinin kasadaki yeri ve
  derinliği doğrulanmadı (`arayuz.py:342`; tasarımda bunun için ±8 mm X yarığı ve kanal ayarı bırakılmış). Çerçeve kasa ölçüsüne
  (284,65 × 182,25) göre çizilmiş. Ekran S siparişinde (`maliyet.json` `kalemler[145]`, P8.1), Parti 1 ise S−0,5'te başlıyor. Hub ve hoparlör
  parçaları gibi bu üçü de Parti 1'in sonuna bırakılmalı (≈ 3,6 sa; VESA 113 g PETG-CF). Yanlış basılırsa VESA, KT-F4c-1'deki dar CF payını yer.
  Parti numarası değişmez, yalnız not ekleniyor: `baski-listesi.md:128-131` "Sıralama mantığı" ve `F4c-partiler.py` `META`/`PARTI[1]`.

### Düşük
- **B-3 · `Y2b-baski.py` yönlendirilmiş stdout'ta düşüyor.** Betik `print` satırında `☐` basıyor, cp1254'te bu `UnicodeEncodeError` veriyor ve JSON'u
  yazmadan rc 1 dönüyor. Günlükteki "Çıkış 0" (`F4c-gunluk.md:13`) UTF-8 konsolda doğru. `F4c-dogrula.py` stdout'u yakaladığı için etkilenmiyor.
  Sorun daha önce de vardı, F4c'den gelmiyor. Öneri: günlükteki yeniden üretim komutlarına `PYTHONIOENCODING=utf-8` notu; betiğe
  `sys.stdout.reconfigure(encoding="utf-8")` (P6.1 ya da `planlama/y2` sahibi).
- **B-4 · P4.3 kabulü yalnız yamayla sağlanıyor.** Yamasız betik 19 metin satırını eski hâle çeviriyor. Brief'in kuralı gereği yama uygulanmadı.
  A bunu "Geçti, koşullu" diye açıkça yazmış. Yama `tasarim/freecad/` sahibine (P6.1); uygulanana kadar `baski_listesi_guncelle.py`'yi tek başına
  koşmak listeyi bozuyor. `F4c-liste.py` ile yeniden üretmek güvenli.
- **B-5 · 6 PETG-CF türü model kaynağında "PETG" diye tanımlı.** `kafa7_parcalar.py:158` (Servo yuvası), `:177` (Rulman yuvası), `:248` (Boyun mili),
  `:285` (Eğme çatalı); `dirsek_parcalar.py:140` (Dirsek çatalı), `:303` (Bilek flanşı). CF bilgisi listenin "tasarım kararı" kümesinden
  (`Y2b-baski.py:11-12`) geliyor. Liste bunu doğru yazmış (`baski-listesi.md:180` "Malzeme `Y2b-baski.py` CF kümesinden"). Ama günlükteki
  "modele göre düzeltildi" (`F4c-gunluk.md:70`) yalnız VESA için doğru. Yoğunluk ikisinde de 1,27, kütle etkilenmiyor. Model malzemesi P6.1'de
  hizalanmalı. VESA'nın PETG-CF olması da bir Ahmet kararına dayanmıyor; K42 ile birlikte teyit edilebilir.
- **B-6 · Parti 0 alt değerinde yöntem karışık.** Kupon A iki uçta da %100 dolu (26,0 g). Kupon B'nin alt değeri 60 g ve kaynağı yok. C–E ise
  "4 çevre + %25" tahmini. Toplama etkisi birkaç gram ve birkaç dakika; dilimleyici değeri esas alınacak (A da öyle yazmış).
- **B-7 · Parti 2 ihtiyatlı.** El (2 × 1,64 sa), boyun yükseltme adaptörü (1,46), rulman yuvası (0,56; yalnız kupon A'ya bağlı) ve S1 kaset kapakları
  servo ya da horn beklemiyor. Bunlar Parti 1'e alınabilir (≈ 5,5 sa, Parti 2'yi kısaltır). Yanlış değil, yalnız öneri. `Y2b-baski.py` `parti()`'ye dokunmayı
  gerektirir.
- **B-8 · Satır sonu.** Git `baski-listesi.md` için "LF will be replaced by CRLF" uyarısı veriyor. Betik LF yazıyor. Commit'te zararsız, ama C bilsin.

## C için `git add` listesi (tam)

```
git add planlama/baski-listesi.md planlama/y2/Y2b-baski.json \
        planlama/d158/F4c-brief.md planlama/d158/F4c-gunluk.md \
        planlama/d158/F4c-partiler.md planlama/d158/F4c-partiler.json \
        planlama/d158/F4c-partiler.py planlama/d158/F4c-liste.py planlama/d158/F4c-dogrula.py \
        planlama/d158/F4c-kontrol.md planlama/d158/F4c-kontrol-sayim.py planlama/d158/F4c-kontrol-sayim.json
```

**Ekleme:** `planlama/dongu-158.md` (döngü yöneticisinin), `tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json`,
`tasarim/freecad/montaj/lale_dongu.*`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`,
`F6a-brief.md`, `planlama/d158/__pycache__/` (ignore'da), `kvkk/`, `rapor/`, `raporlar/…`, `tasarim/solidworks/`, `tubitak-2209b/`.
C, B-1'i günlükte düzeltirse (satır 156, 159–160) bu dosyayla birlikte commit etmeli; düzeltmezse K43 metni bu dosyadaki hâliyle girmeli.

## Rapor için öne çıkacak sayılar

- **72 baskı parçası** (03.11: 65; +7: hoparlör kabı ön/arka, hoparlör kelepçesi, 4 QLED tırnağı). 62 tür; ana montaj BOM'u ile birebir.
- **7,60–7,66 kg** filament: **PETG 6,45 kg** + **PETG-CF 1,16–1,22 kg** (12 tür, 18 adet). 03.11'e göre −22 g.
- **158,2–159,4 sa** baskı (durmadan ≈ 6,6 gün; haftada 32–40 sa ile ≈ 4,0–5,0 hafta). **14 adet destekli.** Hepsi X2D'ye (246 × 246 × 250) sığıyor.
- Partiler: **Parti 1 27 parça / 3,31 kg / ≈ 69 sa**, **Parti 2 25 / 1,33–1,38 kg / ≈ 28–29 sa**, **Parti 3 9 / 0,75 kg / ≈ 16 sa**,
  **Parti 4 11 / 2,21 kg / ≈ 46 sa**. Parti 0: 8 kupon baskısı, 0,26–0,42 kg, **≈ 7,3 sa** (plan ≈ 3 sa yalnız M7 kuponlarını sayıyordu).
- PETG-CF ihtiyacı (parça + kupon) **1,33–1,52 kg ↔ alım 1,5 kg** (pay +166 … −17 g).
- Isıl gömme somun ihtiyacı (pay hariç): **M3 177, M5 21** ↔ plan M3 168, M5 6.
- Takvim (40 sa/hf): baskı ≈ S+3,5'te biter; 32 sa/hf'de ≈ S+4,5 (plan S+4–4,5).

## Karar kuyruğuna girecek metin (döngü yöneticisi taşır; B `karar-kuyrugu.md`'ye yazmadı)

Özet tablosu satırları:

```
| K42 | PETG-CF miktarı: 1,5 kg yetmiyor | **açık** (F4c) | a: +1 makara (4 × 0,5 = 2,0 kg), +1.114,03 TL | S siparişi filament satırı, K34, Parti 0/2 |
| K43 | Isıl gömme somun adedi: M3 177, M5 21 (plan 168 / 6) | **açık** (F4c) | Erken alımda M3 177 + pay, M5 21 + pay | K29, K31, Parti 0 kuponları |
```

```
## K42 · PETG-CF miktarı: 1,5 kg yetmiyor (KT-F4c-1)
- **Soru:** PETG-CF 3 × 0,5 kg (1,5 kg; `planlama/maliyet.json` `kalemler[109]`) parçalara ve kuponlara yetiyor mu, kaç makara alınsın?
- **Sayılar:** parçalar 1.158,0–1.215,8 g (`planlama/y2/Y2b-baski.json` `toplam.cf_g`; 12 tür, 18 adet, VESA taşıyıcı 113 g dahil). Parti 0
  CF kuponları 175,8–301,4 g (`planlama/d158/F4c-partiler.json` `partiler.0.toplam.cf_g`). Toplam 1.333,8–1.517,2 g. 1,5 kg'de pay +166 … −17 g;
  D2 kuponu basılmazsa +69 … +208 g. En büyük CF parçası kafa servo yuvası 151,5 g: tek başarısız baskı alt durumdaki payı bitiriyor. VESA
  taşıyıcının destek malzemesi (28 katman) sayılmadı.
- **Seçenekler:** a) +1 makara (2,0 kg; pay 483–666 g). b) 1,5 kg'de kal; D2 basılmaz, başarısızlıkta yeniden sipariş (gecikme riski).
  c) K34 (baskı hizmeti) netleşince karar ver.
- **Sayısal etki:** a: +1.114,03 TL (`kalemler[109]` birim fiyatı, 11 Ekim; stok yeniden doğrulanmadı); %15 payla +1.281,13 TL. b: 0 TL.
- **Ayrıca netleşmeli:** `F8a-siparis.md:78` "filament firma ve ekipten, satın alınmaz", ama `maliyet.json` filamenti V3 toplamında sayıyor
  (`secenek` "yazici"). VESA taşıyıcının PETG-CF olması modelde (`kabuk_parcalar.py:375-376`), Ahmet'in kararına dayanmıyor (F4c-kontrol B-5).
- **Önerilen varsayılan:** a. Yalnız öneri.
- **Bloke:** S siparişindeki filament satırı; Parti 0 CF kuponları ve Parti 2.
- **Durum:** açık.

## K43 · Isıl gömme somun adedi (KT-F4c-2, F4c-kontrol B-1 düzeltmesiyle)
- **Soru:** Erken alımda (K29) kaç M3 ve M5 ısıl gömme somun alınsın?
- **Sayılar:** model (`tasarim/freecad/montaj/robot-bom.csv`, 09.11) **M3 159, M5 5**. M5'lerin yeri: ön kol gövdesi ×2 (**PETG**,
  `dirsek_parcalar.py:235, 253`), eğme çatalı ×1 (PETG-CF), omuz göbeği ×2 (PETG-CF). Kuponlar iki malzemede basılıyor: B (M3 4, M5 3) ve C
  (M3 5, M5 5) → M3 18, M5 16 (`tasarim/freecad/test/tolerans_kuponu.py:8-9`, `m7-kupon-sonuc.json` `kupon_c_delikler`). Gereken (pay hariç):
  **M3 177, M5 21**. M5 yalnız C kuponu PETG'de denenirse 18.
- **Plan:** M3 168 (`maliyet.json`) / 176 (v4), M5 6. M3 kupona yetmiyor (−9); M5 modele ve kupona yetmiyor (−15).
- **Sayısal etki (taban fiyat, `F8a-siparis.md` §4.1):** M3 168 → 177: +9 × 5,29 = +47,61 TL. M5 6 → 21: +15 × 6,35 = +95,25 TL.
- **Önerilen varsayılan:** erken alımda M3 177 + pay, M5 21 + pay (pay oranı Ahmet'in). K31'in M3 varyantı (A/B/C) adedi değiştirmez; K31 M5 ürünü
  seçilmeden M5 alınmamalı (kupon delikleri Rhino M5 için küçük). Yalnız öneri.
- **Bloke:** K29 (erken alım), K31, Parti 0 kupon B/C.
- **Durum:** açık.
```
