# F0 günlüğü (P0.1, P0.2, P0.3) — tasarım ajanı A, 08.11.2026

Brief: `planlama/d158/F0-brief.md`. Plan: `planlama/dongu-158.md`. Dal `lale-duzeltme`, HEAD `d26c7e7`.

## Dokunulan dosyalar
Yalnız yeni dosyalar, hepsi `planlama/d158/` altında:
- `P0.1-siniflandirma.md` (P0.1)
- `karar-kuyrugu.md` (P0.2)
- `regresyon.py`, `regresyon.json` (taban), `regresyon-son-kosu.json` (son koşu; düzeltme turu 1'de eklendi) (P0.3)
- `F0-gunluk.md` (bu dosya)

Başka dosya değiştirilmedi. Commit, silme, checkout/reset/stash yok. `tubitak-2209b/` yalnız okundu (`BAGLAM.md`).
Depo dışından salt okunan: Echo hafıza kasasının `daily/v3/` günlükleri ve `Threads.md` (dosyaların kaynağını bulmak için).
Geçici test betiği oturumun scratchpad klasöründe, depoda değil.

## P0.1 Sınıflandırma
- `git status`: 25 değişmiş + 305 izlenmeyen (251'i `tubitak-2209b/`). Tablo ve gerekçe `P0.1-siniflandirma.md`.
- `rehber_metin.py` +328 −28 (356 değişen satır): 03→04.11 gecesi Echo'nun rehber/belge ajanı; Ahmet'in 04.11 talimatına dayanıyor
  (`tubitak-2209b/BAGLAM.md:223`). `R-gunluk.md` ile tutarlı: C1 sonrası 32 adım (sayıldı), K1 baştan, `kablo_kapisi` ve
  `M6_BAYRAK_ACIK` kodda var, iki dosya `ast.parse` ile ayrışıyor. Ajanın adı/oturumu kayıtta yok: **doğrulanmadı**.
- **9 commit grubu** önerildi (G1–G9), her biri için tam `git add` listesi ve mesaj. Karara bağlı olmayan: G1 rehber, G2 elektrik,
  G3 baskı listesi, G5 demo; G8 (döngü + F0) kontrolden sonra. G4 K24'e, G6 K22'ye, G7 K23'e, G9 K18–K22'ye bağlı (düzeltme turu 1).
- Dışlanması önerilen: `tubitak-2209b/` (2209-B kuralı), `kvkk/` (iç dosya, kişi adı), `rapor/` (ekip üyelerinin ve danışmanın adları),
  `KY/kaynak/` (satıcı/üretici dosyası), `tasarim/solidworks/*.step` (28,3 MB üretilmiş STEP). Depo açık (`gh repo view`: PUBLIC).
- Kaynağı tamamen bilinmeyen yol yok. Kısmen belirsiz: rehber/belge ajanının kimliği; demo değişikliği yalnız hafıza günlüğünde
  (`daily/v3/2026-10-30.md:19`); Word kilit dosyası `tubitak-2209b/~$le-2209B-oneri-v14-final.docx` (07.11 11:35).

## P0.2 Karar kuyruğu
- 24 madde: K1–K9 (bölüm 4) + K10–K17 (kaynak belgelerden) + K18–K23 (P0.1'den) + K24 (F0 kontrolünden, düzeltme turu 1).
- **Açık 19** (K14 Efe'nin teyidi), **kapandı 5**: K5 (B + R1 ile aşıldı), K8 (29.10 karar a, `Y3-kontrol.md:109`),
  K15 (08.11 onayı, `dongu-158.md:43-44, §2 "Açık onaylar"`), K16 (04.11 PAM8403, `secenekler.md:8`), K17 (05.11 B + R1, `secenekler.md:1`).
- Plan K8'i açık sayıyordu; kaynakta 29.10'da kapanmış. K5'in sorusu 05.11 yerleşim seçimiyle eski düzene ait kaldı.

## P0.3 Regresyon
Betik `py -3 planlama/d158/regresyon.py` iki kez koşuldu (19:55:31 ilk kayıt, 19:55:40 karşılaştırma). İkinci koşu çıkış kodu 0,
10 değerin hepsi "aynı":

| Değer | Bugün | Eşik | Kaynak (dosya : anahtar) |
|---|---|---|---|
| Boy, mm | 1.580,0 | ≤ 1.580,0 | `tasarim/freecad/lale158/lale158-kontrol.json` : `toplam_boy_mm` |
| Çakışma, kafa içi | 0 | 0 | `tasarim/freecad/kafa/kafa-analiz.json` : `statik` (liste uzunluğu) |
| Çakışma, kabuk içi | 0 | 0 | `tasarim/freecad/kabuk/kabuk-analiz.json` : `cakisma` |
| Çakışma, kabuk × iskelet | 0 | 0 | `tasarim/freecad/kabuk/kabuk-analiz.json` : `iskelet_cakisma` |
| Çakışma, ev pozu | 0 | 0 | `tasarim/freecad/carpisma-sonuc.json` : `ev_pozu_cakisma` |
| Rampa 5°, yüksüz devrilme payı | 1,517 | ≥ 1,5 | `KY/uygulama-ivme.json` : `izgara_yuk_0g.a_sinir_pay15.rampa5_geri` (rampa5_* en küçüğü) |
| Tilt payı ±15 | 3,64 | ≥ 3,0 | `tasarim/freecad/kafa/kafa-analiz.json` : `tork.tilt.pay_tilt15` |
| Pan payı | 2,21 | ≥ 2,0 | `tasarim/freecad/kafa/kafa-analiz.json` : `tork.pan.pay_iki_hane` |
| Mikrofon-hoparlör, mm | 574,3 | ≥ 400 | `KY/uygulama-olcum.json` : `mic_hoparlor.poz_min_mm` |
| SY8205 × USB, mm³ | 0 | 0 | `KY/uygulama-olcum.json` : `kablo_sy8205.*` + `kafa_ici_qled_kablo.*` `.sy8205_kesisim_mm3` (13 kablo toplamı) |

(`KY/` = `tasarim/freecad/lale158/kafa-yerlesim/`.) Brief'teki beklenen değerlerin altısı da aynen bulundu. **Bulunamayan değer yok.**
Kaynak JSON'ların hepsi `d26c7e7`'de commit'li ve çalışma kopyasında değişmemiş; `regresyon.json` her dosyanın sha256 ilk 12 hanesini tutuyor.

Betik davranışı (scratchpad'te geçici kopyayla denendi, depodaki `regresyon.json`'a dokunmadan): önceki tilt 3,70 iken 3,64 → "KÖTÜLEŞTİ",
çıkış 1; bir dosya yokken "kaynak yok", çıkış 2. `--yazma` ile dosyaya yazmadan karşılaştırır.

## Yan bulgular
- **P1.2'nin model kısmı yapılmış görünüyor:** MAX98357A modelde 0 parça (`KY/uygulama-notu.md:57`, `kafa10_lib.py:402`); `kafa-bom.csv`
  ve `robot-bom.csv`'de yok. Kalan: yorumlar, `kafa_rapor.py:604`, eski 7" kodu (`kafa7_parcalar.py:489`). P1.2 brief'i bunu ölçmeli.
- `elektrik.md` (çalışma kopyası) hâlâ hub'ı kafada açık sayıyor (`elektrik.md:58`); model 05.11'de hub'ı gövdeye aldı. P4.1.
- `baski-listesi.md:43` VESA taşıyıcıyı Beyaz PETG'de sayıyor, `Y2b-baski.py:11-12` PETG-CF. P4.3.
- Commit'lenecek yeni dosyalarda takma ad geçen yerler P0.1 §3'te listelendi (P4.5).
- `carpisma-sonuc.json` `tek_kosu` false (omuz bölümü 03.11'den): regresyon "ev pozu" değerini bu dosyadan okuyor; P2.2 sonrası dosya değişince
  karşılaştırma yine çalışır.

## Açık kalanlar
- K18–K24 Ahmet'te; G4, G6, G7, G9 bunlara bağlı. G1, G2, G3, G5 kararsız commit'lenebilir (orkestratör, adım 7).
- `regresyon.json` (taban) yalnız çıkış 0 olan koşuda yeniden yazılıyor (tarih ve geçmiş değişir); `regresyon-son-kosu.json` her koşuda.
- Rehber ajanının kimliği ve Word kilit dosyasının durumu doğrulanmadı.

## Düzeltme turu 1 (08.11.2026, `F0-kontrol.md` 11 madde)

Dokunulan: `P0.1-siniflandirma.md`, `karar-kuyrugu.md`, `regresyon.py`, `regresyon.json` (taban, çıkış 0 koşusuyla), yeni
`regresyon-son-kosu.json`, bu günlük. Başka dosya yok; commit, silme, checkout/reset/stash yok. Denemeler scratchpad kopyasında.

| # | Madde | Durum | Ne yapıldı |
|---|---|---|---|
| 1 | Ad iddiası (P0.1 §3, K20) | yapıldı | "İzlenen dosyalarda bu adlar yok" kaldırıldı. Ölçüm: Ahmet'in adı HEAD'de 6 izlenen dosyada (`git grep -l HEAD`); diğer üç öğrencinin soyadı ve danışmanın adı 0. Varsayılan gerekçesi buna göre yazıldı. Adlar hiçbir belgeye yazılmadı (d158 altında grep 0). |
| 2 | "İç dosya" kaynağı (P0.1, K19) | yapıldı | Kaynak yalnız `kvkk/fiyatlar.md:3`; `saglayici-secimi.md:3` "asistan taslağı" diye anıldı. |
| 3 | G1 mesajı ve §1 | yapıldı | AST ölçümü yeniden yapıldı: 20 yeni adım, 11 kısa kayıt yeniden yazıldı, K2 güncellendi, K1 baştan; C1 öncesi HAZIRLIK (50 → 65 parça, perçin pensesi, servo kablosu), A3 (14 → 24. adım), B1a (M7 kupon C), B5a (XL4016 C). Satır atfı **değiştirilmedi**: `grep -n` `M6_BAYRAK_ACIK` için 472, `def kablo_kapisi` için 478 veriyor (1 tabanlı); kontrolün 471/477'si bir eksik. Belgeye "(grep -n, 1 tabanlı)" notu eklendi. |
| 4 | `elektrik.md:461` 2209-B atfı | yapıldı | P0.1 §3 sarkan atıflara `:461` eklendi; G2 mesajına "K18 a seçilirse temiz klonda boşa düşer" notu. |
| 5 | 11,6" raporundaki iki satır | yapıldı | P0.1 §3'e ayrı uyarı; karar kuyruğuna **K24** (a: G4'ten önce temizle, varsayılan; b: P4.5'e bırak; etki: b'de iki satır git geçmişinde kalır). G4 "K24 kararına bağlı" işaretlendi. Kuyruk: 24 madde, açık 19, kapandı 5. |
| 6 | `dongu-158.md` satır atıfları | yapıldı | `karar-kuyrugu.md` 18 yer, `P0.1-siniflandirma.md` 3 yer, `regresyon.py` 2 yer, bu günlük 1 yer güncellendi; her atfın yanına bölüm ve kod yazıldı (ör. `dongu-158.md:136, §4 K1`). |
| 7 | Boy iki yönlü | yapıldı | `yon="esit"`, hedef 1.580,0, tolerans 0,05 mm; dışı hem "KÖTÜLEŞTİ" hem eşik dışı, çıkış 1. |
| 8 | Taban ezilmesin | yapıldı | `regresyon.json` artık kabul edilmiş taban: yalnız çıkış 0 olan koşu yazar. Her koşunun sonucu `regresyon-son-kosu.json`'a. |
| 9 | (isteğe bağlı) `tek_kosu`, SY8205 etiketi | yapıldı | Kayda `bilgi.carpisma_sonuc` (tek_kosu false, birleştirme notu, koşu kimlikleri 20261103-215611 ve 20261105-185759). Etiket "SY8205 × kafa kabloları (USB dahil, 13 kablo)"; anahtar adı `sy8205_x_usb_mm3` aynı kaldı (taban sürekliliği). |
| 10 | (isteğe bağlı) K13 sayıları, K5 cümlesi | yapıldı | K13: 12 LED, dizi kabuğun 2,5 mm altında, Ø70 (`KY/yerlesim_lib.py:54`). K5: ses kartı ve PAM kafada sol duvarda kaldı, B seçimiyle kabul, ayrı onay kaydı yok. |
| 11 | Regresyon yeniden + G8 listesi | yapıldı | Aşağıda; G8 `git add` listesine `planlama/d158/F0-kontrol.md` eklendi. |

**Kötüleştirme denemesi** (scratchpad'te 6 kaynak JSON + betik + taban kopyası; depodaki JSON'lara yazılmadı, sha256 önce/sonra aynı:
taban `df0368ee119f`, `lale158-kontrol.json` `d8a141db0960`). Her senaryo ardışık **iki** yazmalı koşu:

| Senaryo | Çıkış kodları | Taban |
|---|---|---|
| Değişiklik yok | 0, 0 | güncellendi |
| Boy 1.580 → 1.570 (T9) | 1, 1 | aynı kaldı |
| Boy 1.580 → 1.590 (T8) | 1, 1 | aynı kaldı |
| Boy 1.580 → 1.580,04 (tolerans içi) | 0, 0 | güncellendi |
| Boy 1.580 → 1.579,94 (tolerans dışı) | 1, 1 | aynı kaldı |
| Tilt 3,64 → 3,50 (T1) | 1, 1 | aynı kaldı |
| `carpisma-sonuc.json` yok (T12) | 2, 2 | aynı kaldı |

**Regresyon son çıktı** (`py -3 planlama/d158/regresyon.py`, 08.11.2026 20:15:20, taban 19:55:40): **çıkış 0**, 10 değer "aynı".
boy 1.580 (eşik 1.580 ± 0,05) · kafa içi 0 · kabuk içi 0 · kabuk × iskelet 0 · ev pozu 0 · rampa yüksüz 1,517 · tilt 3,64 · pan 2,21 ·
mikrofon-hoparlör 574,3 · SY8205 × kafa kabloları 0. Kaynaklar yukarıdaki P0.3 tablosuyla aynı. Taban bu koşuyla güncellendi.

**Orkestratöre not (kontrol ajanının bulgusu, B2.5):** P1.4'teki 249,7 mm³ bugün 0. `dongu-158.md:65, §3 P1.4` "USB dokunmatik kablo yolu
SY8205 kartından geçiyor (249,7 mm³)"; güncel ölçüm `KY/uygulama-notu.md:27` (önceki 249,7, ölçülen 0,00) ve
`KY/uygulama-olcum.json kablo_sy8205."USB dokunmatik".sy8205_kesisim_mm3` = 0. P1.4'ün kabul ölçütü `kablo_tup_cakisma 0` ise
`lale158-kontrol.json kablo_tup_cakisma` hâlâ sıfır değil (kontrol: HDMI × göğüs ekranı 897,1; 12 V × göğüs ekranı 617,3; USB dokunmatik ×
göğüs ekranı 167,6 mm³; şema uç teması olabilir). P1.4 brief'i yazılmadan önce yeniden ölçülmeli; P1.2 gibi P1.4 de B + R1 ile büyük
ölçüde yapılmış olabilir.
