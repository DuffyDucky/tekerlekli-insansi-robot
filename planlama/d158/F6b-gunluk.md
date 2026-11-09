# F6b günlüğü: tek baskı analizi, tüm parçalar (P6.2), 09.11.2026

A ajanı. Brief `planlama/d158/F6b-brief.md`. Commit / push / silme yok (kayıt ajanı yapar).

## 0. Başlangıç denetimi (15:50)

| Komut | Çıkış | Not |
|---|---|---|
| `py -3 planlama/d158/regresyon.py --yazma` | 0 | GEÇER (hepsi okundu, kötüleşen yok) |
| `py -3 planlama/d158/F4c-dogrula.py` | 0 | 1–5b GEÇTİ |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |

Bellek 2,39 GB boş, FreeCAD süreci yok, kilit "boş".

### Kilit olayı (15:54, benim hatam)

15:54:14'te `dirsek omuz kafa kabuk` koşusunu, kilidi ve süreç listesini okuduğum aynı komutta başlattım. Çıktıda F7a'nın yeni yazdığı
kilidi ("F7a 2026-11-09 15:54 rehber_veri.py …") ve çalışan `freecadcmd` sürecini (PID 80628) gördüm ama koşu başlamıştı; betiğim kilidi
kendi metniyle ezdi. dirsek (3 s), omuz (4 s) ve kafa (25 s) F7a'nın süreciyle aynı anda koştu. kabuk başlarken (15:54:46) betiği ve
FreeCAD sürecimi durdurdum (15:55), kilide F7a'nın metnini aynen geri yazdım. F7a'nın süreci bu arada bitmişti; 15:59'da F7a kilidi
yeni koşusu için yeniden yazdı. O üç modülün çıktısı salt okumaydı (FCStd'leri yalnız açtım), sonradan hepsi yeniden koşuldu; F7a'nın
dosyalarına dokunulmadı. Sonraki dört koşu (16:03, 16:07, 16:11, 16:18) kilit "boş", süreç yok ve bellek ≥ 2 GB iken başladı
(2,26 / 2,68 / 3,96 / 3,43 GB); kilit bütün koşu boyunca "F6b (P6.2) baski_analiz_ortak (…) — saat" idi, bitince "boş" yapıldı.
Orkestratör sonradan bildirdi: OneDrive eşitlemesi kilidi eski içeriğe döndürebiliyor; F7a satırı varken süreç yoksa kilit bayat sayılır.

**Düzeltme turu 1 (D-3):** Kilidin 15:55:39'da eski içeriğe ("F7a 2026-11-09 15:54 …") dönmesi büyük olasılıkla benim geri yazmamdı.
F7a kilidi 15:54:34'te "boş" yapmıştı ve süreci bitmişti; benim yazdığım F7a satırı bayat kaldı. Doğrusu kilidi "boş" bırakmaktı. Bu geri
dönüşü OneDrive eşitlemesine bağlayan bir kanıt yok; yukarıdaki OneDrive gerekçesi **kanıtlanmadı**. B'nin 16:37:43'te "boş" yaptığı kilit
10 dakika sonra (16:47) hâlâ "boş"tu (`F6b-kontrol.md` madde 8, D-3). Bayat kilit kuralı ("satır var, süreç yok → bayat") zararsız
kalıyor. F7a çıktısına etkisi yok: commit'lenen çıktılar sonraki tam koşulardan geliyor.

## 1. Envanter: baskı alanlarını kim üretiyor

| Modül | Betik → işlev | JSON anahtarı | Yöntem |
|---|---|---|---|
| taban | `taban/taban_montaj.py` → `taban_lib.baski_analiz` (= `dirsek_lib.baski_analiz`, `taban_lib.py:17`) | `taban/taban-analiz.json` `baski[]` | Katman 1 mm, z = zmin + 0,5 + k; önceki katmanın 1 mm ofseti (45°) destek sayılır; açık bölge boyu > 15 mm ve 1 mm daraltınca alan kalırsa sorun; mesh 0,1. Destek filamenti sayılmaz; doluluk 0,8 |
| kabuk | `kabuk/kabuk_montaj.py:298` kendi `baski_analiz` | `kabuk/kabuk-analiz.json` `baski[]` | Aynı katman yöntemi, z = zmin + 0,5 + k, ofset kontrolsüz, mesh 0,25; F1b P1.5 açık tel kaydırması. Destek g yok; doluluk 0,9; filament tam sayıya yuvarlanır |
| kafa | `kafa/kafa_montaj.py:680` → `kafa_lib.baski_analiz` (`kafa_lib.py:225`, tarama kaynağı) | `kafa/kafa-analiz.json` `baski[]` (tarama kaynağı) | Aynı yöntem, z = zmin + **0,47** + k (eş düzlem kaçınması), ofset alanı büyümezse ofsetsiz; destek g yok; parça başına `doluluk_baski` |
| dirsek | `dirsek/dirsek_montaj.py:543` → `dirsek_lib.baski_analiz` (tarama kaynağı) | `dirsek/dirsek-analiz.json` `baski[]` | Kabukla aynı (z + 0,5); destek g yok; doluluk 0,8; sağ kol, Y2b ×2 |
| omuz | `omuz/omuz_baski.py` (FCStd'den) | `omuz/omuz-baski.json` `parcalar[]` | 6 eksen yönü; katman 0,5 mm (z0 0,23) + eğim yüzleri; köprü / konsol / ada; yön: sığma > yük uyumu > destek alanı; **destek g sayılır** (hacim × 0,15); doluluk CF 0,8–0,9 |
| omuz | `omuz/omuz_montaj.py:237` | `omuz/omuz-analiz.json` `baski[]` | Yalnız AABB ölçü (sıralı), `sigar` ≤ 230, kütle; destek yok. Y2b omuz ölçüsünü buradan alıyordu |
| kabuk (kapak, hoparlör, orta bant) | `lale158/kafa-yerlesim/uygulama_baski.py` → `yerlesim_olc.baski_mod` → `kafa_lib.baski_analiz` | `kafa-yerlesim/uygulama-baski.json` `parca{}` | kafa_lib (z + 0,47), doluluk 0,9; 05.11 |
| — | `lale158/lale158_kontrol.py:130`, `ikinci_kontrol.py:113` | `lale158-kontrol.json` `baski`, `ikinci-kontrol.json` `baski` | Analiz değil: modül JSON'undan `sigar` okuma / model duruşunda AABB |
| — | `taslak-170/taslak_montaj.py:272`, `test/m7_kuponlari.py:278` | taslak, kupon | Kapsam dışı (eski 170 cm taslağı, kuponlar) |

Zincir (F6a sonu): modül JSON'ları + omuz-baski → `planlama/y2/Y2b-baski.py` → `Y2b-baski.json` → `F4c-partiler.py` (kaynak anahtarı ve
X2D yine modül JSON'larından) → `F4c-liste.py` (+ `baski_listesi_guncelle.py`) → `baski-listesi.md`. Aynı parça için iki sonuç olan yerler:
üst arka kapak, hoparlör kabı, orta bant sağ (kabuk-analiz ↔ uygulama-baski); omuz (omuz-baski ↔ omuz-analiz ölçüsü).

## 2. Kapak uyuşmazlığının kök nedeni (19.667,7 ↔ 5,01 mm²)

Kanıt: `tasarim/freecad/lale158/baski-analiz.json` → `kapak_tani` (FreeCAD 1.1, 16:07 ve 16:18 koşuları; geometri `kabuk_parcalar.py`'den,
hacim 70.906,9 mm³ = FCStd nesnesi K… hacmi).

- **Aynı parça, aynı yön, aynı eşik.** İki sonuç da "Ust arka servis kapagi", yukarı = dış yüz normali × −1 (dış yüzü tablada), 45° / 1 mm
  katman. Fark yalnız kesit düzleminin yeri: `kabuk_montaj` z = zmin + 0,5 + k, `kafa_lib` (KY) z = zmin + 0,47 + k.
- **Yüz ölçümü (baskı çerçevesi, `kapak_tani.yatay_yuzler`):** tabla yüzü z 0 (25.059,7 mm², 7 delikli flanş), flanş üst yüzü **z 1,4988**
  (5.392,0 mm²), plaka üst (iç) yüzü z 2,9976 (17.891,3 mm²). Kapak baskı yönüne 2,27° eğik (kenar yüzleri n_z = 0,0397 = sin 2,27°),
  bu yüzden 1,5 mm'lik flanş baskı çerçevesinde 1,4988 mm. İnce kesit (0,05 mm adım): z < 1,5'te 8 tel / 25.059,7 mm², z 1,50–2,95'te 1 tel
  / 19.667,7 mm² (plaka), z ≥ 3,0'da takoz ve raylar.
- **Hata:** `kabuk_montaj`'ın z = 1,5 kesiti flanş üst yüzüne 1,2 µm yakın düşüyor. Bu kesitten çıkan yüz ters normalli (n_z −1,0) ve 1,2 µm
  eğik, kenar toleransı 0,00119 (`boolean_deneme["1.5-2.5"].alt`). Bir sonraki katman (z 2,5, n_z +1) ondan çıkarılınca `common` = 0,
  `cut` = 19.667,673 mm², yani katmanın tamamı "desteksiz" (`kabuk_montaj_yontemi.katman[2].acik` = [19.667,67, boy 156,1] = `kabuk-analiz.json`
  `baski[13].destek_sorun`). Oysa iki kesit aynı plaka: z 1,6 → 2,6 ve 1,9 → 2,9 denemelerinde `cut` = 5,011 mm², `common` = 19.662,66.
- **5,01 mm²:** aynı plakanın 1 mm arayla iki kesitinin gerçek XY farkı (eğik kenarlardan gelen şerit; `kafa_lib_yontemi.katman[2]`,
  `uygulama-tani.json`). 1 mm ofset (45° payı) bunu karşılıyor: destek gerekmez. KY'nin "hesap artığı" değerlendirmesi doğruydu.
- **Karşılaştırma (düzeltme turu 1, D-2):** Karşılaştırma parçası (düz arka servis kapağı) kontrol yerine geçmiyor. Bu parça
  BoundBox zmin'e göre kesildi (`baski_analiz_ortak.py:637`), eski yöntemin mesh zmin'ine göre değil. Ayrıca bir kenarı 0,45 mm toleranslı.
  `kapak_tani.karsilastirma_arka_servis_kapagi` verisinde z 1,5 kesiti hâlâ flanşta (8 tel, 30.242,9 mm²; flanş üstü 1,6 ile 1,9 arasında),
  z 0,5 kesiti bozuk (n_z −1). İlk metindeki "flanş üstü tam 1,5'te, kesit doğru yönde, `cut` 0" ifadesi bu veriyle tutmuyordu. Eski yöntem
  bu parçada 0 sorun buldu (`kabuk-analiz.json` `baski[12]`). Kök neden kanıtı karşılaştırmaya dayanmıyor: üst arka kapağın ölçümü,
  ince kesit ve boolean dökümü yeterli (B bağımsız ölçtü: `F6b-kontrol.md` madde 2).
- **Sonuç:** 3 mm plaka destek istemiyor; yön ve yüz seçimi doğru (dış yüz tablada, temas 25.060 mm²). 19.667,7 mm² kesit / boolean artığı.
  Tek analiz kapakta destek 0 (`baski-analiz.json` `parcalar[17]`).

## 3. Tek yöntem

Betik `tasarim/freecad/lale158/baski_analiz_ortak.py` (adı `*_lib.py` değil; tarama kaynaklarına dokunmuyor). Kipler:
FreeCAD (modül başına, `BASKI_MODUL=<modül>`, geometri o modülün `*_parcalar.py`'si ve `BASKI` tablosundan; FCStd'deki `Tur == "Baski"`
nesnesinin hacmiyle karşılaştırılır) ve birleştirme (`py -3 … birlestir <ara klasör>` → `baski-analiz.json`).

Yöntem (her parça, her aday yön için aynı `kolon_analizi`):
- Mesh 0,1 mm / 0,3 rad, `App.Rotation(yukari, Z)` ile baskı çerçevesine (eski analizlerle aynı dönüş).
- Dikey kolon taraması (0,5 mm ızgara): her kolonda mesh kesişimleri sıralı; alt yüzeyin altında hava varsa (> 0,3 mm) ve yüzey yataydan
  44°'den az eğimliyse (45° ± 1° mesh toleransı) destek; kolon boyu alttaki malzemeye ya da tablaya kadar. Kesit ve 2B boolean yok.
- Köprü / şerit kuralı eski dört yöntemle aynı sayılar: bölgeler (i, j, 1 mm z dilimi) komşuluğunda 3B ayrılır; XY boyu ≤ 15 mm ya da
  ~1 mm yarıçaplı diskle daraltınca kaybolan (≤ 2 mm şerit) bölge serbest.
- Destek g = hacim × 0,15 × 1,27 (omuz_baski ile aynı). Parça g = hacim × 1,27 × doluluk × 1,05 + destek. Süre = (hacim × doluluk + destek
  hacmi × 0,15) / 10 mm³/s. Doluluk modülün kendi değeri (değiştirilmedi).
- Yön kuralı: tasarım yönü (modül `BASKI.yukari`; omuzda omuz-baski `secilen_yon`, yük uyumu); X2D'ye sığmazsa sığan adaylardan en az destekli.
  Adaylar tasarım + 6 eksen; en az destekli aday `en_az_destek` diye yazılır (öneri). Bütün parçalar tasarım yönünde sığdı.

Ara sürümler (ilk koşu 16:03): (a) 1° tolerans yokken boyun milinin 45° konisi ve dirsek çatalı mesh yuvarlamasından destekli çıktı;
(b) bölgeler yalnız XY'de birleşince dik basılan bantlarda farklı yükseklikteki küçük çıkıntılar tek bölge sayıldı; (c) 4-komşu aşındırma
0,5 mm ızgarada çapraz yönde 2 mm halkayı geniş sandı. Üçü düzeltildi; sentetik denemeler (`kolon_analizi`: 40 × 40 askı 1.600 mm² /
16.000 mm³; 10 × 10 askı serbest; 2 mm şerit serbest, 3 mm destekli; üst üste iki küçük çıkıntı ayrı ve serbest) geçti.

Doğrulama: omuzda iki bağımsız yöntem yakın: destek alanı omuz yuvası 2.193,8 → 2.262,2 mm², göbek 2.352,7 → 2.434,8, tambur 769,2 → 860,0,
kol çatalı 2.023,2 → 2.044,0; destek g 11,1 / 5,7 / 0,8 / 11,4 → 11,5 / 5,9 / 0,8 / 12,7 (`baski-analiz.json` `fark`, omuz-baski satırları).
Tek-sayı kolonlar (kesişim sayısı tek) yalnız omuz bandı sağ ve solda, 100 / ~70.000 kolon (%0,14); ikisi de destek 0, sonuca etkisi yok.
Bütün 62 parçada FCStd hacmi eşit (`toplam.fcstd_hacim_esit_degil` = []), X2D'ye sığmayan yok.

Koşular (FreeCAD 1.1.4, yerel `.robot-cad\run_fc.py` başlatıcısı; çıkış hep 0): son koşu 16:18–16:24: taban 6,0 s, dirsek 4,4, omuz 7,3,
kafa 38,5, kabuk 280,0 s (`baski-analiz.json` `moduller`). Ara JSON'lar scratchpad'de (depoya girmedi).

### Tek JSON

`tasarim/freecad/lale158/baski-analiz.json`: 62 tür / 72 adet (`toplam.adet`), her parça bir kez (modül + ad). Her parçada: `yon`, `yukari`,
`olcu`, `x2d_sigar`, `destek_alan_mm2`, `destek_hacim_cm3`, `destek_g`, `parca_g`, `toplam_g`, `sure_sa` (alt / üst = doluluk aralığı),
`destek_bolge` (merkez parça koordinatında), `en_az_destek`, `adaylar`, `kaynak` (FCStd + nesne adı, STEP, `*_parcalar.py`, hacim eşitliği).
`fark`: eski modül JSON'larıyla (taban/kabuk/kafa/dirsek-analiz, omuz-baski, omuz-analiz, uygulama-baski) 72 karşılaştırma satırı.

### Büyük farklar (> %10 ya da destek var/yok değişimi; `fark[].buyuk`)

| Parça | Eski (kaynak) | Yeni | Açıklama |
|---|---|---|---|
| Üst arka servis kapağı | destekli, 85,0 g (`kabuk-analiz.json` `baski[13]`) | desteksiz, 85,1 g | §2: eski sonuç kesit / boolean artığı. KY (`uygulama-baski.json`) zaten desteksizdi |
| Göğüs ekranı VESA taşıyıcı | destekli, 113,0 g (`baski[26]`, 28 sorunlu katman, destek g sayılmıyordu) | destekli, 144,8 g (+%28,1) | Arka flanşın altı z 32–58 mm, 3.806,5 mm², 166,4 cm³ → 31,7 g destek. Yön aynı; fark destek filamentinin sayılması |

Ara koşularda görülüp düzeltilen var/yok değişimleri (boyun mili, yüz kabuğu sol, arka kafa kabuğu sol, dirsek çatalı, bantlar) son
sonuçta eski analizle aynı (desteksiz). %10'un altında ama not edilen: göğüs bandı sağ / sol +15,3 / +14,1 g (cep üst kenarı, köprü
159,5 / 147,5 mm, kolon 207 mm: destek g artık sayılıyor); kabuk satırları ±0,5 g (eski betik tam sayıya yuvarlıyordu); omuz ölçüsü artık
baskı yönündeki kutu (`omuz-analiz.json` AABB değil; örn. üst kol tüpü 130 × 56 × 56 → 56 × 56 × 130).

## 4. Zincir ve toplamlar

Uyarlanan: `planlama/y2/Y2b-baski.py` artık yalnız `baski-analiz.json`'u okuyor (destek g ve alanı satırda). `F4c-partiler.py` kaynak anahtarı,
yön ve X2D'yi `baski-analiz/parcalar[i]`'den alıyor; destek notu JSON'dan (alan + g) + kısa tarif. `F4c-dogrula.py` anahtarları yeni
JSON'dan; yeni kontrol 6 (her parça bir kez, Y2b ve BOM ile aynı). `F4c-liste.py` metni tek analize göre (kaynak zinciri, destekli liste
JSON'dan, kapak notu, F6b önce/sonra tablosu `git show 4d1898a:planlama/y2/Y2b-baski.json` ile). `baski_listesi_guncelle.py` değişmedi.

| Komut (PYTHONIOENCODING=utf-8) | Çıkış | Sonuç |
|---|---|---|
| `py -3 tasarim/freecad/lale158/baski_analiz_ortak.py birlestir <ara>` | 0 | 62 tür, 72 adet, 7.668,9–7.726,7 g, destek 124,5 g |
| `py -3 planlama/y2/Y2b-baski.py` | 0 | 72 adet, 7.669–7.727 g (PETG 6.475, CF 1.194–1.252; destek 124) |
| `py -3 planlama/d158/F4c-partiler.py` | 0 | kontrol hepsi True |
| `py -3 planlama/d158/F4c-liste.py` | 0 | 300 satır |
| `py -3 planlama/d158/F4c-dogrula.py` | **0** | 1, 2, 6, 3, 4a, 4b, 5a, 5b GEÇTİ |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | 17 dosyanın özeti kayıtla aynı |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** | GEÇER |

### Toplam önce / sonra (`4d1898a:planlama/y2/Y2b-baski.json` → `planlama/y2/Y2b-baski.json`)

| | Önce (F6a) | Sonra (F6b) | Fark |
|---|---|---|---|
| Adet | 72 | 72 | 0 |
| Filament | 7.604,8–7.662,4 g | 7.668,9–7.726,7 g | +64,1 / +64,3 g |
| PETG | 6.446,6 g | 6.474,9 g | +28,3 g |
| PETG-CF | 1.158,2–1.215,8 g | 1.194,0–1.251,8 g | +35,8 / +36,0 g |
| Destek (dahil) | yalnız omuz, 58,0 g | 124,5 g | +66,5 g |
| Süre | 158,22–159,42 sa | 159,90–161,08 sa | +1,68 / +1,66 sa |
| Destekli adet | 14 | 13 | −1 (üst arka kapak) |
| Parti 1 | 27 / 3,31 kg / 68,9–69,0 sa | 27 / 3,37 kg / 70,2–70,3 sa | +61 g (göğüs bantları, VESA) |
| Parti 2 | 25 / 1,33–1,38 kg / 27,7–28,8 sa | 25 / 1,33–1,39 kg / 27,9–29,0 sa | +3,4 g |
| Parti 3 | 9 / 0,75 kg / 15,7 sa | 9 / 0,76 kg / 15,7 sa | +1,3 g |
| Parti 4 | 11 / 2,21 kg / 45,9 sa | 11 / 2,21 kg / 46,1 sa | −1,7 g (yuvarlama) |

Listede yeni yuvarlanmış toplam: **72 parça, 7,67–7,73 kg, 160–161 sa** (önce 7,60–7,66 kg, 158–159 sa). PETG-CF + kupon: 1,37–1,55 kg;
1,5 kg'de pay +130 / −53 g (önce +166 / −17 g) → K42 etkileniyor (KT-F6b-1).

## 5. Destek azaltma önerileri (destek oranı en yüksek 5 parça; uygulanmadı)

Oran = destek g / toplam g (`baski-analiz.json`); "en az" = sığan 7 aday içinde en az destek hacimli yön.

| # | Parça | Oran | Destek (tasarım yönü) | En az destekli aday | Öneri |
|---|---|---|---|---|---|
| 1 | Göğüs ekranı VESA taşıyıcı (CF) | %21,9 | 31,7 g, 3.806 mm², arka flanş altı z 32–58 | −Y: 5,4 g, 1.476 mm², ama tabla teması 288 mm² (tasarımda 5.969) | Yön değişmesin (devrilme riski, VESA plakası katman düzleminde kalmalı). **Geometri:** arka flanşın altına 45° kaburga / pah (KT-F6b-3a) |
| 2 | Omuz yuvası (CF, ×2) | %14,1 | 11,5 g, manşon içi tavanı z 45 (1.201 mm², kolon 40) + S1 penceresi | Tasarım yönü zaten en az | Yön değişmez. **Geometri:** manşon içi tavanına damla / 45° kemer (KT-F6b-3b) |
| 3 | S1 kablo tamburu (×2) | %13,8 | 0,8 g, +x dudak altı (860 mm², kolon 5,4) | −Z: 0,4 g ama tabla teması 0 mm² | Değişiklik önerilmez (0,8 g); istenirse dudak altına 45° pah |
| 4 | Kol çatalı (CF, ×2) | %12,7 | 12,7 g, horn kulağı tavanı z 58,5 (1.100 mm², kolon 58,5) | −X: 2,2 g ama tabla teması 20 mm² | Yön değişmesin (omuz_baski yük uyumu; temas çok küçük). **Geometri:** horn kulağı altına 45° destek kaburgası / kulak tabanını pah (KT-F6b-3c) |
| 5 | Omuz göbeği (CF, ×2) | %9,3 | 5,9 g, flanş altı z 13 (1.521 mm²) + diş | −Y: 2,8 g, temas 1.070 mm² (tasarımda 1.153) | **Yön önerisi:** −Y destek yarıya iner, temas benzer; ama horn ekseni katman düzlemine yatar (omuz_baski +X'i yük uyumuyla seçti). Kupon / K39 ölçümünden sonra karar (KT-F6b-3d) |
| (6) | Göğüs bandı sağ / sol | %6,7 / %6,1 | 15,6 / 14,1 g, cep üst kenarı köprüsü 160 / 148 mm, kolon 207 mm | ±X (yatık): 1,6 g | Cep tavanı 148–160 mm açık uçlu bir açıklık: cep duvarı tam kesiyor (`kabuk_parcalar.py:98`), tavan 2,8 mm, altında 207 mm boşluk; pah işe yaramaz. **Destek kalsın** (dilimleyicide yalnız bu bölge) **ya da yatık baskı** (±X, 1,6 g; yüzey ve bant tutarlılığı bedeli) (KT-F6b-3e; düzeltme turu 1, O-1) |

## 6. Karar taslakları

**KT-F6b-1 · K42'ye ek (PETG-CF miktarı).** Tek analiz destek filamentini her parçada sayınca PETG-CF +35,8 / +36,0 g (VESA taşıyıcı +31,7,
omuz desteği +4). Parça + kupon 1,37–1,55 kg; 1,5 kg'de pay +130 / −53 g (önce +166 / −17). K42'nin önerdiği a (+1 makara, 2,0 kg) hâlâ
yeter (pay ≥ 446,8 g = 1.500 + 500 − 1.553,2). Seçenekler: a) K42 a değişmeden (öneri); b) VESA'ya kaburga (KT-F6b-3a) girerse ~26 g CF geri kazanılır, K42 yine a.
Ek senaryo: bütün PETG-CF parçalara 0,8–0,9 doluluk uygulanırsa (bugün yalnız omuz) üst sınır +66,1 g (kafa 5 parça, dirsek çatalı ve
bilek flanşı; `baski-analiz.json` `parca_g` × 0,125) → üst pay −119 g; K42 a yine yeter.

**KT-F6b-2 · Modül analizlerindeki eski `baski` alanı.** `kabuk_montaj.py`, `kafa_lib.py`, `dirsek_lib.py` (taban dahil) her koşuda eski katman
yöntemini çalıştırıp modül JSON'una yazıyor; zincir artık okumuyor ama iki sonuç dosyalarda duruyor (kapaktaki hata `kabuk-analiz.json`'da
kalıyor). Seçenekler: a) sonraki geometri döngüsünde modül betiklerinden baskı analizini kaldırıp `baski_analiz_ortak.py`'ye yönlendirmek
(`kafa_lib` / `dirsek_lib` tarama kaynağı → tarama yeniden koşar); b) dokunmamak, belgelerde "eski, zincir dışı" demek; c) yalnız
`kabuk_montaj`'ın z başlangıcını 0,47'ye almak. Önerilen varsayılan: b şimdi, a P6'nın sonraki geometri işinde. F6b dosyalara dokunmadı.

Düzeltme turu 1 ekleri (D-4):
- (a) **c seçeneği bu kapağı yalnız rastlantıyla düzeltir**, kalıcı düzeltme değil: 0,47 başka bir parçada başka bir yüze teğet düşebilir.
  P1.5 açık tel kaydırması kapalı telli ters normalli yüzü yakalamaz. Eski yöntem kalacaksa kesit yüzünün normali ve düzlemselliği
  (dz > 1e-6) denetlenmeli.
- (b) Eski `baski` alanını okuyan yalnız `lale158_kontrol.py` değil, dört betik daha var: `tasarim/freecad/kabuk/kabuk_rapor.py:128`
  (yeniden koşulursa kapağı yine "destekli" gösterir), `tasarim/freecad/dirsek/dirsek_rapor.py:93`, `planlama/adim5/baski_toplam.py:16`,
  `planlama/d158/F4c-kontrol-sayim.py:37`. a ya da b uygulanırken bunlar da ele alınmalı.

**KT-F6b-3 · Geometri önerileri (uygulanmadı).** a) VESA taşıyıcı arka flanş altına 45° kaburga; b) omuz yuvası manşon içi tavanına damla
/ 45° kemer; c) kol çatalı horn kulağı altına 45° kaburga; d) omuz göbeği −Y baskı yönü (kupon / K39 sonrası); e) göğüs bandı cep tavanı
(düzeltme turu 1, O-1): geometri önerisi yok. Tavan 2,8 mm, altında 207 mm boşluk, 148–160 mm açık uçlu açıklık; 45° pah ya da kemer bu
açıklığı taşımaz. Seçenekler: (i) **destek kalsın** (15,6 / 14,1 g PETG; dilimleyicide yalnız bu bölgeye boyalı destek); (ii) **yatık baskı**
(±X, 1,6 g; yüzey ve bant tutarlılığı bozulur). a–d tarama kaynağı ya da geometri değişikliği; destek g düşüşü tahmini: a ≈ 26, b ≈ 2 × 9,
c ≈ 2 × 10 g (toplam ≈ 64 g). e için tasarruf tahmini yok.

## 7. Açıklar

1. Destek g tahmini (hacim × 0,15); ağaç destek daha az, ızgara daha çok verir. Dilimleyicide parça başına bakılmalı (Parti 0 sonrası STL).
   CF desteği 91,9 g; ±%50 belirsizlikte (± 46 g) K42 a payı ≥ 400 g kalır (B, `F6b-kontrol.md` madde 5d).
2. 45° eşik Cura gibi tutucu; Bambu Studio varsayılanı 30°. B'nin ölçümünde 30° ile toplam destek ≈ −1,1 g (%1; 124,5 → ≈ 123,4 g),
   çünkü destekli yüzler 0° ya da 15° eğimli (madde 5c). Eşik değişirse betikte tek sabit (`ACI`).
3. Doluluk modülden geldi; PETG-CF 0,8–0,9 aralığı yalnız omuzda (KT-F6b-1 senaryosu).
4. Eski `baski` alanları modül JSON'larında duruyor (KT-F6b-2); `lale158_kontrol.py` hâlâ modül JSON'undan `sigar` okuyor.
5. Omuz bandı sağ / sol'da %0,14 tek-sayı kolon (mesh); destek 0 olduğu için etkisiz, kaynağı incelenmedi.
6. Kilit olayı (§0).
7. (Düzeltme turu 1, D-1) Göğüs bantlarının desteği ızgara fazına duyarlı. Seçilen faz (JIT 0,4865 / 0,3172) alt uçta kalıyor: 5 kaydırma
   81,2–98,4 / 72,6–87,8 cm³, BRep 93,7 / ≈ 87 cm³. Gerçek değer yaklaşık +%15, ≈ +5,5 g PETG (sağ +2,9, sol +2,6). K42'ye etkisi yok,
   7,67–7,73 kg yuvarlamasını değiştirmiyor; dilimleyicide bakılmalı. Yöntem değişikliği gerekmiyor.

## 8. Dokunulan dosyalar (commit listesi için)

- Yeni: `tasarim/freecad/lale158/baski_analiz_ortak.py`, `tasarim/freecad/lale158/baski-analiz.json`, `planlama/d158/F6b-gunluk.md`,
  `planlama/d158/F6b-brief.md` (izlenmeyen; brief gereği girer, F6b yazmadı; D-5).
- Değişti: `planlama/y2/Y2b-baski.py`, `planlama/y2/Y2b-baski.json` (betikle), `planlama/d158/F4c-partiler.py`, `F4c-partiler.json`, `F4c-partiler.md`
  (betikle), `planlama/d158/F4c-liste.py`, `planlama/d158/F4c-dogrula.py`, `planlama/baski-listesi.md` (betikle).
- Yalnız içerik: `planlama/d158/FREECAD-KILIT.txt` (F6b son koşudan sonra "boş" yaptı; 16:27'de F7a düzeltme turu kendi satırını yazdı,
  dokunulmadı).
- Çalışma ağacında olup F6b'nin olmayan değişiklikler: `planlama/dongu-158.md` (16:24, başkası), `tasarim/freecad/kabuk/gorsel/*.png` (14:28,
  F6b başlamadan önce), `rehber/`, `planlama/rehber/`, `tasarim/freecad/rehber/`, `montaj/yerlesim-kontrol.json` (F7a / başka paket).
- Son denetim (16:3x): F4c-dogrula 0, carpisma_kos kontrol 0, regresyon --yazma 0; dokunulan dosyalarda takma ad yok (grep 1).
- Dokunulmadı: tarama kaynakları (`carpisma_kos.kaynak_listesi()`; kontrol 0), modül analizleri ve FCStd'ler (yalnız okundu),
  `baski_listesi_guncelle.py`, `kod/`, `karar-kuyrugu.md`, `dongu-158.md`, `maliyet.json`, F7a alanı.

## 9. Düzeltme turu 1 (16:52–16:55)

B'nin kontrolü `planlama/d158/F6b-kontrol.md`: KOŞULLU GEÇER (kritik 0, orta 1, düşük 8). Bu turda yalnız bu günlük değişti; betik, JSON,
liste ve FreeCAD koşusu yok.

| Madde | Yer | Yapılan |
|---|---|---|
| O-1 | §5 satır (6), KT-F6b-3 e | "Cep üst kenarına 45° pah / kemer" kaldırıldı. Yeni metin: tavan 2,8 mm, altında 207 mm boşluk, 148–160 mm açık uçlu açıklık; seçenek destek kalsın ya da yatık baskı (±X, 1,6 g). "e ≈ 2 × 13 g" tahmini çıkarıldı; a–c toplamı ≈ 64 g |
| D-2 | §2 "Karşılaştırma" | Düz arka kapak karşılaştırması kontrol yerine geçmiyor (BoundBox zmin, 0,45 mm toleranslı kenar, z 1,5 hâlâ flanşta) |
| D-3 | §0 | 15:55:39 geri dönüşü büyük olasılıkla benim geri yazmam; OneDrive gerekçesi kanıtlanmadı; B'nin kilidi 16:37:43 → 16:47 "boş" kaldı |
| D-4 | §6 KT-F6b-2 | (a) c seçeneği (z 0,47) rastlantısal, normal / düzlemsellik denetimi; (b) eski alanı okuyan dört betik eklendi |
| D-8 | §6 KT-F6b-1, §7 açık 1–2 | "≥ 447" → "≥ 446,8 g"; CF desteği 91,9 g ± %50 → pay ≥ 400 g; 30° ile ≈ −1,1 g |
| D-1 | §7 açık 7 | Göğüs bantları ızgaraya duyarlı, gerçek ≈ +%15, ≈ +5,5 g PETG |
| D-5 | §8 | `planlama/d158/F6b-brief.md` commit listesine eklendi |
| — | §3 | Başlatıcının yerel kullanıcı klasörü yolu kısaltıldı (`.robot-cad\run_fc.py`) |

D-6 (F4c-liste sabit sayıları) ve D-7 (eşik sınırı iki satır) B'nin önerisiyle değiştirilmedi.

sha1, düzeltmeden önce (16:52) ve sonra (16:53), öteki 11 F6b dosyası:

| Dosya | Önce | Sonra |
|---|---|---|
| `tasarim/freecad/lale158/baski_analiz_ortak.py` | b7ffe9f7d9a2adefaa4be99d890af654214243b9 | aynı |
| `tasarim/freecad/lale158/baski-analiz.json` | d4220099574d470b7e3836b0c27bf1c7d049406a | aynı |
| `planlama/y2/Y2b-baski.py` | ef9a4bb73c58ad4bca32f0bbd7222068ce1ec2c4 | aynı |
| `planlama/y2/Y2b-baski.json` | cda8de9015339db82a729c706f3fcb3ebc332ae3 | aynı |
| `planlama/d158/F4c-partiler.py` | 6282f562b8487e5f1117832bd705bfd538b8caf8 | aynı |
| `planlama/d158/F4c-partiler.json` | 432b270ba90db1530b81e1cdb1ab94f05e0a3d75 | aynı |
| `planlama/d158/F4c-partiler.md` | bab3e7e1d706675e84f0b66a3b041e3c65c1bdb5 | aynı |
| `planlama/d158/F4c-liste.py` | 1939a087f7e642f2acc93364e0a1d7d24a1b49ae | aynı |
| `planlama/d158/F4c-dogrula.py` | cb1f5d93ab87a9e2da3127925ae32efc0005c6ba | aynı |
| `planlama/baski-listesi.md` | 9a9ec9049981dbbb6289eb12fac68399fec81e77 | aynı |
| `planlama/d158/F6b-brief.md` | 767df5c2231ef4c2e958051dc99e7291d9009eac (değişme saati 15:42) | aynı (önce-sha1 düzeltmeden sonra alındı; dosyaya bu turda yazılmadı) |

Denetim: `py -3 planlama/d158/F4c-dogrula.py` → **0** (SONUC: GECTI). Kilit "boş"; bu turda yazılmadı. Takma ad taraması 0.
