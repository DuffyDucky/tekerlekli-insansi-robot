# Renkli STEP renk tablosu (Lale)

`step_renkli.py` her parçanın FreeCAD'deki `Renk` özelliğini (anahtar) aşağıdaki RGB'ye çevirir. Renkler uydurma değil,
projedeki FreeCAD görsel betiklerinden alındı. Tablo `step_renkli.py` içindeki `RENK` ve `RENK_TABAN` sözlükleridir; birini değiştirirsen
diğerini de güncelle.

## Kaynaklar

- Birincil: `tasarim/freecad/taslak-170/taslak_gorsel.py` (`RENK`). `taslak_montaj.py` aynı anahtarlarla parçaları işaretler.
  Aynı tablo `iskelet_gorsel.py`, `kabuk_gorsel.py` ve diğer modül görsel betiklerinde de var; `kabuk` değeri farklı (0,90/0,91/0,93, modül
  görselinde) ama taslak tablosu esas alındı.
- İkincil: `tasarim/freecad/taban/taban_gorsel.py` (`RENK`), yalnız taslak tablosunda olmayan anahtarlar için (`pcb_y`, `k_*`).
- Kullanılmadı: `tasarim/cad/robot_cad.py` `COL` ve demo (`Robot-Tasarim-Demosu.html`). O eski V1-V3 modelin paletidir, anahtar adları farklı
  (`rim_blue`, `pcb_green` vb.) ve taslak-170 parçalarıyla eşleşmez.
- Taslak tablosu ile taban tablosu çelişen anahtarlar (`pcb_k`: taslakta yeşil, tabanda kırmızı; `aku`, `motor`, `alu2` tonları): taslak tablosu geçerli.

## Parça grubu - renk (taslak-170, 1064 parça)

| Grup | Anahtar | RGB 0-1 | Hex | Parça | İçerik |
| --- | --- | --- | --- | --- | --- |
| Kabuk panelleri (PETG) | `kabuk` | 0,85 0,87 0,90 | `#D9DEE6` | 27 | yüz/arka kafa kabuğu, gövde bantları, servis kapağı, etek |
| İskelet, alüminyum profil/ray/direk | `alu` | 0,78 0,80 0,83 | `#C7CCD4` | 18 | şase rayları, gövde direği, omuz traversi, boyun plakası, 25T alüminyum horn diskleri |
| İskelet, alüminyum braket/köşe | `alu2` | 0,55 0,60 0,68 | `#8C99AD` | 19 | köşe bağlantı 40x40, gövde/etek braketleri |
| İskelet, iç köşe kanalı | `celik2` | 0,86 0,66 0,22 | `#DBA838` | 8 | iç köşe bağlantı kanal 10 (pirinçle aynı değer, projede böyle) |
| Yapısal baskı (PETG-CF) | `petg2` | 0,18 0,52 0,86 | `#2E85DB` | 11 | omuz göbeği, üst kol tüpü, ön kol, el, boyun mili, kafa iskeleti |
| Baskı bağlantı parçaları (PETG) | `petg` | 0,96 0,55 0,13 | `#F58C21` | 23 | tutucular, yuvalar, çatallar, flanş, tambur |
| Servolar (gövde + çıkış mili) | `siyah` | 0,13 0,13 0,14 | `#212124` | 50 | DS3235, MG996R servoları ve milleri; ayrıca set vida, saplama, köpük bant, kayış, yüz ekranı (LCD) |
| Tekerler | `lastik` | 0,10 0,10 0,10 | `#1A1A1A` | 4 | Teker 125x58 |
| Tahrik motorları | `motor` | 0,62 0,64 0,68 | `#9EA3AD` | 4 | JGB37-520 |
| Akü | `aku` | 0,25 0,30 0,35 | `#404C59` | 1 | LiFePO4 12,8 V |
| Elektronik, yeşil kart | `pcb` / `pcb_k` | 0,10 0,45 0,25 | `#1A7340` | 4 + 3 | Pi 5, kamera, Pololu, MAX98357A / BTS7960, ESP32 |
| Elektronik, mavi kart | `pcb_m` | 0,15 0,30 0,60 | `#264C99` | 10 | sonar, XL4016, servo dağıtım, PCA9685, BNO055 |
| Elektronik, arayüz kartı | `pcb_y` | 0,10 0,45 0,20 | `#1A7333` | 2 | arayüz kartı, ESP32 taşıyıcı (taban_gorsel'den) |
| Röle, sigorta, acil stop kontak gövdeleri | `koyu` | 0,25 0,25 0,28 | `#404047` | 3 | plastik gövdeler |
| Ana sigorta yuvası, anahtar, acil stop mantarı | `kirmizi` | 0,85 0,15 0,12 | `#D9261F` | 3 | |
| Kontrplak katları | `ahsap` | 0,80 0,65 0,45 | `#CCA673` | 2 | elektronik katı, güç paneli |
| Bağlantı elemanları (çelik) | `celik` | 0,50 0,52 0,56 | `#80858F` | 657 | vida, cıvata, pul, çekiç somun |
| Pirinç somun/burç/kaplin | `pirinc` | 0,86 0,66 0,22 | `#DBA838` | 175 | ısıl gömme somun, burç, 12 mm kaplin |
| Naylon burç | `naylon` | 0,92 0,92 0,88 | `#EBEBE0` | 36 | M3x8 burç |
| İp | `gri` | 0,60 0,60 0,60 | `#999999` | 4 | S1 tambur bağlama ipi |

Toplam 21 anahtar, birbirinden farklı 19 RGB (`celik2` = `pirinc`, `pcb` = `pcb_k`).

## Varsayılan (projede rengi olmayan) durumlar

- taslak-170'te varsayılana düşen parça yok (21 anahtarın hepsi bir tabloda tanımlı).
- Bir parçanın `Renk` anahtarı iki tabloda da yoksa (Y2a'da yeni anahtar çıkabilir) `gri` (`#999999`) verilir ve betik çıktısı
  "varsayılana düşen anahtarlar" satırında listeler. O zaman anahtarı bu tabloya ve betiğe ekle.
- Tabloda `vizor` (ekran siyahı) ve `kablo` anahtarları tanımlı ama taslak-170'te kullanılmıyor.

## Not: "SolidWorks'te geometri gorunmuyor" incelemesi (29 Ekim)

- Supheli neden saydamlik/alfa tersligiydi; **yanlis cikti**: `Lale-1650-renkli.step` icinde `SURFACE_STYLE_TRANSPARENT` 0 adet, 1073 `STYLED_ITEM` hepsi
  opak `FILL_AREA_STYLE_COLOUR`. Geometri tam: 1073 `ADVANCED_BREP_SHAPE_REPRESENTATION` (1069 `MANIFOLD_SOLID_BREP` + 4 `BREP_WITH_VOIDS`), birim mm,
  her stil dogru katiya ve dogru baglama bagli, FreeCAD'e geri alinca 1073 kati ve sinir kutusu (-261,7..261,7 / -5,1..1651,7 / -264,2..268 mm) ayni.
- Betige yine de iki sigorta eklendi: renk ve gorunum nesnesi acikca opak (`Transparency=0`), dogrulama STEP metninde saydam stil sayisinin 0 olmasini sart kosar.
  Eklenen `--grup <metin>` secenegi yalniz etiketi eslesen alt gruplari yazar (kucuk deneme dosyasi: `Lale-test-teker.step`).
- `-v2` dosyalari eskisiyle govde olarak ayni (yalniz zaman damgasi farkli). Gorunmeme dosyadan degil SolidWorks tarafindan (Large Assembly / hafif yukleme) geliyorsa
  kucuk `Lale-test-teker.step` once acilarak ayirt edilir.

- Duz alternatif (29 Ekim): `step_duz.py` montaj/alt montaj olmadan tek urun, 1073 kati dunya koordinatinda, yuz basina renk (opak); `Lale-1650-duz.step`, `Lale-test-teker-duz.step`. Renkli montaj STEP SolidWorks'te gorunmezse bunlari dene.

- Silindi (29 Ekim, Ahmet): `Lale-1650-renkli.step`, `-v2`, `Lale-taslak-170-renkli.step`, `-v2` ve `Lale-test-teker.step` SolidWorks'te geometrisiz acildigi icin silindi. Calisan surum `*-duz.step`; `step_duz.py` ile uretilir. Yukaridaki incelemedeki dosya adlari tarihsel kayittir.
