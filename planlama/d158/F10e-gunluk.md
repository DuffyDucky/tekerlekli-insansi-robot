# F10e günlüğü: gerçek renk, bağlandığı yer, cıvata işaretleri, zor alt adımlar

## DURAKLAMA (saat ölçülerek) — kapandı: devam edildi 11.11.2026 23:07, iş 12.11.2026 00:27'de bitti

Aşağıdaki duraklama kaydı tarihçe olarak kalıyor; kalan işlerin hepsi yapıldı (§8). Duraklamadaki "çıkış kodu yakalanmadı" maddesi
kapandı: bir düzeltme sayfa kodunu değiştirdiği için (§8, F10d) üretim çıkış kodu yakalanarak yeniden koşuldu, **çıkış 0**. Önceki
koşunun (20:55) çıkış kodu yakalanmadı, öyle kalıyor.

Orkestratörün isteğiyle 11.11.2026 21:44'te duraklatıldı (bellek Ahmet'e lazım). Koşan üretim öldürülmedi, bitmesi beklendi:
`rehber_uret.py --veri-yok` 20:55:45'te başladı, 21:43:4x'te bitti (≈ 48 dk). Sonra yeni ağır komut başlatılmadı. Bu pakete ait
arkada süreç yok (python / başsız Chrome yok; denetlendi). `FREECAD-KILIT.txt` "boş"; FreeCAD bu pakette hiç koşulmadı. Duraklamada
kullanılabilir bellek 3,92 GB.

**Bitenler (brief "İş" maddelerine göre):**

1. Gerçek renk: bitti. Veri ↔ CAD 1192 / 1192, GuiDocument 1031 / 1031; varsayılan gerçek renk, sınıf kipi (düğme, `C`, `?renk=`);
   kenar kuralları; panel ve yazdırma örnekleri. Demo ↔ rehber renk farkı karar maddesi (§11).
2. Bağlandığı yer: bitti. 95 / 99 konum (boş 4'ün gerekçesi §3); doğruluk 201 çift, ölçülen 186, doğru 186 (son ölçüm, kodu bu
   hâliyle); bütün koşu henüz yok.
3. Cıvata işaretleri: bitti. İlk koşuda işaret 1188 = bağlantı elemanı 1188, kabuk 277 / 277, kare dışı 0. *(düzeltildi, bkz. §12.6)*
4. Zor 8 alt adım: kamera düzeltmeleri bitti (§4); karelere bakıldı (§5: 7 açık, 31.9 zor). Önce / sonra kareleri
   (`F10e-goruntu-*.png`) **henüz çekilmedi**.
5. Devredilen 3 ölçüm: bitti (§7).
6. Doğrulama betiği: yazıldı; ilk koşudan sonra iki bölümü yeniden kuruldu (§6). Düzeltilmiş hâliyle **bütün koşu yok**.
   Depodaki `F10e-dogrula.json` (19:39) eski koşunun; şu anki kodu temsil etmez.
7. Üretim: bitti (aşağıda). Zincirin geri kalanı koşulmadı.
8. Karelere bakma: kabuk 42 alt adım açık + koyu ve 15 başka adım bakıldı (§5). Son üretimden sonra yeniden bakılmadı (son üretim
   veri ↔ kod değiştirmedi, yalnız ASCII denetim listesi değişti).

**Son üretim (`rehber_uret.py --veri-yok`):** çıkış kodu yakalanmadı (süreç `Start-Process` ile, `-PassThru` / bekleme olmadan
başlatılmıştı); stderr boş, çıktıda "ek kontrol sorunlu: -", `kontrol.json` içinde bütün `gecti` alanları doğru, üretimin çıkış koşulu
(`ek_kotu` boş, piksel denetimi tam) 0 demek. Kesin çıkış kodu için yeniden koşmak gerekmez; zincirdeki F10a / F10d bunu yeniden okur.

| denetim | sonuç |
| --- | --- |
| tarayıcı kontrolü | 50 adım, 50 geçti, konsol hatası 0, her parça tek adımda |
| alt adım | 50 / 50 geçti, her parça tek alt adımda |
| yazdırma kareleri | 100 kare, piksel denetimi 100 / 100, boş 0, en düşük çizim oranı 0,0606 |
| telefon 360 px | 7 adımda taşma 0 |
| PDF | 69 sayfa (önce 69), en küçük yazı 8,1 pt dom / pdf (önce 8,1), 12576 kB, eşleme tutarlı |
| metin denetimi | ASCII kalıntı 0, gruplama yanlış 0, kafa / hoparlör / hub çelişki 0, zorunlu uyarı eksik 0 / 40, yasak talimat 0 |
| sıra | 565 bağlantı, ulaşılamaz 0 (sınır 0), bilinen kapalı sınama geçti |
| perdelenme | alt adımlarda gerekçesiz gizli 0 (sınır 0), gerekçeli istisna 102 |
| görünüm (rehber_gorunum) | renk 1192 eşleşti, GuiDocument 1031 / 1031, metin alanı değişen 0, bağlandığı yer 95 / 99 |

**Kalan işler, tam sırayla** (her biri ayrı süreç, öncesinde bellek ölçümü ≥ 2 GB, ön planda yoklama, aynı anda tek ağır süreç;
çalışma klasörü depo kökü):

1. `py -3 -u -X utf8 planlama/d158/F10d-dogrula.py --goruntu-yok` (F10d eşiği hâlâ geçiyor mu; gerekirse yalnız yeni görünüme uydur).
2. `py -3 -u -X utf8 planlama/d158/F10a-dogrula.py --kanit-yok`
3. `py -3 -u -X utf8 planlama/d158/F9b-dogrula.py` (veri karması değişti; F9b bunu "bilgi" sayar)
4. `py -3 -u -X utf8 tasarim/freecad/carpisma_kos.py kontrol` (FreeCAD gerekiyorsa kilit kuralı)
5. `py -3 -u -X utf8 planlama/d158/regresyon.py --yazma`
6. `py -3 -u -X utf8 planlama/d158/F10e-dogrula.py` (tam, kareli: `F10e-dogrula.json` + `F10e-goruntu-*.png`; ≈ 10–12 dk)
7. Önce / sonra karelerine bak; §5'i ve PDF önce / sonra satırını kesinleştir.
8. Bu günlükte "ZİNCİR" yazan bölümleri (§3 sonuç, §6, §8–§11) doldur; dönüş raporu.

Tahmini kalan süre: zincir 1–5 ≈ 25–35 dk (en uzunu F10d ve F10a, tarayıcıyla), F10e tam koşu ≈ 12 dk, kare bakma ve günlük
≈ 20 dk; toplam ≈ 1–1,5 saat.

**Yarım kalan ya da henüz doğrulanmamış değişiklikler:**

- `planlama/d158/F10e-dogrula.py`: görünürlük ve ev doğruluğu bölümleri ilk koşudan sonra değişti; parça parça koşuldu, bütün koşu yok.
- `planlama/d158/F10e-dogrula.json`: eski (ilk koşu, KALDI); 6. adımda üzerine yazılacak.
- `rehber/app.js` (20:13, son kenar kuralı: saydam yeni parça, önceki grisine yakın parça), `rehber/stil.css`, `rehber/yazdir.html`,
  `rehber/index.html`: son üretimden önce değişti, üretimin tarayıcı / yazdırma / telefon denetimlerinden geçti; F10a / F10d / F10e
  arayüz denetimleri bu son hâlde koşulmadı.
- `tasarim/freecad/rehber/rehber_metin.py` (kamera alanları), `rehber_gorunum.py` (yeni), `rehber_uret.py`, `rehber_denetim.py`
  (`ASCII_TAMAM`'a "renk"): üretimden geçti; F10d / F10a ile doğrulanmadı.
- `F10d-dogrula.py` / `F10a-dogrula.py`: bu pakette değiştirilmedi.
- Bu günlükte "ZİNCİR" yazan yerler boş.

**Çalışma ağacı tutarlı mı:** evet, açılabilir. `rehber/veri/rehber-veri.js` / `.json` (20:56), kod ve `planlama/rehber/kontrol.json`
(21:43) aynı üretimden: üretim veriyi şimdiki `rehber_metin.py` ve `rehber_gorunum.py` ile yazdı ("değişen 0"), sonra bu veri ve
şimdiki sayfa koduyla bütün kareleri, PDF'yi ve `kontrol.json`'u üretti. `rehber/veri/robot.glb` değişmedi (git'e göre). Tutarsız tek
çıktı yukarıdaki eski `F10e-dogrula.json`.

**Pakete ait olmayan, dikkat:** `planlama/dongu-158.md` çalışma ağacında değişmiş görünüyor (dosya saati 18:51, 4 ekleme / 3 silme);
bu paket o dosyaya yazmadı (dokunulmaz listesinde). Önceki paketlerin scratchpad'inden kalan üç `tail -f` süreci açık (f10c-b,
f10c-c, f10d-b günlüklerini izliyor; bu paketin değil, dokunulmadı).

Uygulama ajanı (A). Brief: `planlama/d158/F10e-brief.md`. Başlangıç: dal `lale-duzeltme`, HEAD `90c270a` (F10d). Geçici dosyalar
scratchpad'de; depoya kopyalanmadı. FreeCAD **koşulmadı** (gerekmedi: renk CAD kaynağından FreeCAD'siz okunuyor, §1); kilit baştan
sona "boş".

## 0. Komutlar, çıkış kodları, bellek

Bellek: kullanılabilir fiziksel bellek (`Win32_OperatingSystem.FreePhysicalMemory`), her ağır komuttan önce ölçüldü. Uzun komutlar ayrı
süreç olarak başlatıldı, çıktı dosyaya yazıldı, ön planda kısa aralıklarla yoklandı; aynı anda iki ağır süreç koşulmadı.

| komut | bellek önce (GB) | çıkış | not |
| --- | --- | --- | --- |
| `rehber_gorunum.py --yazma` (keşif, birkaç kez) | 1,13 → 3,57 | 0 | veri yazmadan ölçüm |
| `rehber_gorunum.py` (veri yazımı; rehber_metin değiştikçe 6 kez) | 3,7–4,9 | 0 | her koşu ≈ 26–30 s |
| scratchpad kare / ölçüm betikleri (tek alt adım, CDP) | 3,9–4,9 | 0 | geliştirme |
| `F10e-dogrula.py --goruntu-yok` (ilk koşu) | 3,88 | 2 | 585 s; KALDI: görünürlük ve ev doğruluğu ölçütü yeniden kuruldu (§6) |
| devredilen ölçümler (scratchpad, `rehber_giris` + nokta–üçgen) | 4,44 | 0 | ≈ 6 dk |
| `rehber_uret.py --veri-yok` (1. koşu) | 3,16 | durduruldu | denetim "ascii kalıntı 1" (yeni düğme metnindeki "renk"); düzeltilip baştan koşuldu |
| `rehber_uret.py --veri-yok` (2. koşu, 20:55) | 2,2 | yakalanmadı | çıktı ve `kontrol.json`'da her denetim geçti |
| `F10d-dogrula.py --goruntu-yok` (23:08) | 3,47 | **2** | 648 s; KALDI: kabuk görünürlüğü 4 parça (§8) |
| tek alt adım ölçümleri (scratchpad, CDP; kök neden) | 2,37–2,40 | 0 | |
| `rehber_uret.py --veri-yok` (3. koşu, 23:22) | 2,55 | **0** | 2057 s |
| `F10d-dogrula.py --goruntu-yok` (23:57) | 3,93 | **0** | 519 s, GEÇTİ |
| `F10a-dogrula.py --kanit-yok` (00:06) | 3,96 | **0** | 396 s, GEÇTİ |
| `F9b-dogrula.py` (00:12) | 3,91 | **0** | 6 s, GEÇER (hata 0) |
| `tasarim/freecad/carpisma_kos.py kontrol` (FreeCAD'siz) | 3,91 | **0** | 0,5 s, sonuç güncel (17 izlenen dosya aynı) |
| `planlama/d158/regresyon.py --yazma` | 3,85 | **0** | 0,2 s, 10 / 10 aynı |
| `F10e-dogrula.py` (tam, kareli; 00:13) | 3,89 | **0** | 772 s, GEÇTİ; `renk_demo` karar (geçme şartına girmez) |

Çıkış kodları scratchpad'deki küçük bir sarmalayıcıyla (alt süreç dönüş kodu dosyaya) yakalandı.

## 1. Gerçek renk: kaynak ve yöntem

- **Kaynak:** tek kaynak CAD. Parçanın modül FCStd'sindeki `Renk` özelliği (Document.xml) × o modülü boyayan gorsel betiğinin *(düzeltildi, bkz. §12.6)*
  `RENK` tablosu (`tasarim/freecad/<modül>/<modül>_gorsel.py`, ast ile okunur; float → `int(x*255+0.5)`), kural betiklerdeki
  `RENK.get(o.Renk, RENK["gri"])`. Rehberde ayrı renk tablosu yok. *(düzeltildi, bkz. §12.6)*
- **FreeCAD'siz:** FCStd zip; Document.xml'den nesne sırası ve String özellikleri. Parça sırası `rehber_veri.py` ile aynı
  (`m6_yukle.DOSYA` sırası × nesne sırası, `Tur` özellikli `Part::Feature`, `HARIC` önekleri). Her parçada modül, tür ve kod veriyle
  eşleşmezse betik durur.
- **Bağımsız denetim:** FCStd'nin GuiDocument.xml'inde kayıtlı ShapeAppearance yayınık rengi (gorsel betiği `doc.save()` ile yazmış).
  Kafa dosyasında GuiDocument yok (161 parça).
- **Ölçüm:** veri ↔ CAD 1192 / 1192 aynı; GuiDocument kayıtlı 1031, aynı 1031, farklı 0. Tabloda olmayan ad: `kabuk:pcb` (1 parça,
  kural gereği gri `#999999`).
- **Yeni dosya:** `tasarim/freecad/rehber/rehber_gorunum.py` (veriye `parcalar[].gr`, `renk_kaynak`, `ev`, `ev_kaynak`, `ip` ve
  rehber_metin görünüm alanları). `rehber_uret.py` her üretimde (FreeCAD'li ya da `--veri-yok`) veri adımından sonra çağırır
  (`--cikti` ile çağırmaz: depodaki veriye yazmasın).

Renk tablosu özeti (ad, renk, parça):

| ad | renk | parça | ad | renk | parça |
| --- | --- | --- | --- | --- | --- |
| celik | `#80858f` | 723 | pirinc | `#dba838` | 188 |
| siyah | `#212124` | 61 | naylon | `#f2f2e6` | 44 |
| kabuk | `#e6e8ed` | 37 | petg | `#f58c21` | 19 |
| alu | `#c7ccd4` | 18 | alu2 | `#8c99ad` / `#9ea6b3` | 18 / 1 |
| petg2 | `#2e85db` | 15 | pcb_m | `#1a4da6` | 11 |
| celik2 | `#dba838` | 8 | pcb / pcb_y | `#1a7333` | 8 / 3 |
| öbür 17 ad (kırmızı, lastik, motor, kablo renkleri, …) | | 41 | | | |

## 2. Tasarım seçimleri

- **Varsayılan kip: gerçek renk.** Gerekçe: okur masadaki parçayı karedekiyle eşleştirir (beyaz kabuk, kara CF taşıyıcı, pirinç ısıl
  gömme); sınıf renkleri parçanın türünü söyler ama gerçekte öyle görünmez. Sınıf kipi düğme (`◑ gerçek renk` / `◑ sınıf rengi`),
  `C` tuşu ve `?renk=sinif|gercek` ile; seçim yerel kayıtta tutulur. Sınıf paleti değişmedi.
- **Önceki parçalar:** bugünkü gri (açık `#b5b5b0`, koyu `#5d6168`), değişmedi.
- **Bağlandığı yer tonu:** `#ff3fa4` (pembe). Verideki her gerçek renkle en küçük ΔE76 57,7 (en yakın `#b31f1f`); seçim yeşili
  `#7cfc00` ve kehribar `#ffb000` ile de ayrık. Önceki parça bu tonda çizilir (öncekiler "saydam" kipteyse saydam; "gizli" kipte bile
  görünür). Masada ilk alt adımda önceki parça yoksa bağlandığı yer birimin tabanıdır (bu alt adımda yeni): gerçek renginde, pembe
  kenar çizgisiyle.
- **Zeminle karışan renk:** yeni parçanın rengi ile zemin (`--sahne`) arasındaki WCAG karşıtlık oranı 3,0'ın altındaysa kenar çizgisi
  (EdgesGeometry 30°, açık temada `#26282c`, koyuda `#e8e8e8`). Ek iki kural (karelerden): saydam çizilen yeni parça her zaman kenar
  alır, rengi parçanın kendi rengiyle karşıtlığı yüksek olan tema rengi (35.3'te kara taşıyıcı açık temada bulanıktı); önceki grisiyle
  karşıtlığı 1,5'in altında kalan yeni parça da kenar alır (alüminyum horn, çelik cıvata tezgâh karelerinde öncekilerden ayrılsın).
  Panel ve yazdırma satır örneklerine ince kenar (açık gri / kara örnek zeminde kaybolmasın).
- **Seçim yeşili ve kehribar:** değişmedi. Seçim yeşili `#7cfc00` ↔ en yakın gerçek renk ΔE 78,5; kehribar `#ffb000` ↔ petg
  `#f58c21` ΔE 21,9, ama kehribar yalnız küçük görünümde, orada gerçek renk yok (soluk gri robot).
- **Cıvata yeri işaretleri:** SVG katmanı, ekranda sabit boyutlu halka (yarıçap 9 px; dış koyu 4 px, iç beyaz 1,8 px, iki temada da
  okunur). Noktası veride (`parcalar[].ip`: cıvata başının üst merkezi, öbürleri sınır kutusu merkezi), parça uçarken onunla gider.
  22 px'ten yakın işaretler tek halkada kümelenir, yanında "×n". Panel satırı ya da parça seçilince ilgili halkalar seçim yeşilinde.
  Aç / kapa: düğme `⊚ işaret`, `I` tuşu, `?isaret=0|1`. Yazdırma karelerinde de görünür.
- **Kare başlığı:** yazdırma / PDF karesinin (`?sahne=1`) sol üstünde "31.5 <alt adım adı> · bakış: ön-üstten" (bakış kamera *(düzeltildi, bkz. §12.5)*
  vektöründen). Benzer kare çiftleri (34.3 / 34.5, 34.4 / 34.6, 49.3 / 49.4) basılı karede başlıktan, etkileşimli sayfada sahnenin
  yanındaki panel başlığından ve alt adım listesinin işaretli satırından ayırt edilir; küçük görünümdeki kehribar yer de farklı
  yükseklikte. İlk sürümde başlık etkileşimli sayfada da vardı; araç çubuğunun altında bant açıp güvenli alanı daralttığı için yeni
  parçalar ≈ %10 küçüldü ve F10d görünürlüğü düştü (§8). Bu yüzden etkileşimli sayfadan kaldırıldı.
- **Lejant:** "Bu adımın parçaları (gerçek renk)", "Bağlandığı yer", "Önceki adımlar", halka "Bağlantı elemanı yeri (×n: küme)".
- **Kadraj:** konumun yeni parçalarının hepsi bağlantı elemanıysa (31.5, 31.10, 36.3) kadraj bağlandığı parçaları da kapsar.

## 3. Bağlandığı yer: yöntem ve sonuç

- Veriden: konumun yeni bağlantı elemanlarının çevresinde halka noktaları (cıvata r + 0,8 / r + 2,5 mm, 6 yükseklik × 8 açı; somun
  dış yüzün 0,8 mm dışı), noktanın en az 3'ünü içeren önceki parça (eğik ışın paritesi, `robot.glb`). Bulunmazsa yeni ana parçaların
  yüzeyinden 0,6 mm (sonra 1,5, 3) dışarıdaki noktaların en az 6'sını içeren önceki parça (temas). Masada ilk alt adımda taban.
- Sonuç: 99 konumun 95'inde (bağlantı elemanı 73, masa tabanı 15, temas 0,6 mm 7). Boş 4: adım 1 (önceki parça yok), 17, 32, 49.2
  (yeni parça yok). Kabuk alt adımlarında: yeni parçalı 41 / 41 alt adımda vurgu var, sahnede de 95 / 95 (veri = sahne).
- Doğruluk (ikinci, bağımsız yöntem, `F10e-dogrula.py`): her (konum, ev) çiftinde konumun yeni parçalarının köşelerinden ev parçasının
  üçgenlerine en kısa nokta–üçgen uzaklığı ≤ 1 mm. Sonuç: 201 çift; 15'i masa tabanı (taban bu alt adımda yeni, uzaklık anlamsız,
  ölçülmedi); ölçülen 186, doğru 186 (hepsi doğrudan ≤ 1 mm).
- Vurgu olmayan 4 konum, tek tek:
  - **Adım 1 (A1 şase çerçevesi):** robotun ilk adımı; önceki parça yok, bağlanacak yer yok.
  - **Adım 17 (K1 kablolama kapısı 1: taban):** yeni parça yok (yalnız kablo şemaları); "bağlandığı yer" yeni parçaya göre tanımlı.
  - **Adım 32 (K2 kablolama kapısı 2: gövde içi):** aynı gerekçe, yalnız kablo.
  - **49.2 (ilk enerji, aşama 2, kapaklar açık):** test alt adımı; yeni parça yok.
  Dördünde de vurgu verilecek yeni parça yok; uydurulmuş vurgu yerine boş bırakıldı.

## 4. Zor alt adımlar ve kare düzeltmeleri

Değişen `rehber_metin.py` alanları (yalnız kamera; kablolama içeriği değişmedi):

| alt adım | önce | sonra | gerekçe (ölçüm) |
| --- | --- | --- | --- |
| 31.9 | ön-sağ-üst, kabuklar saydam değil | (1, 0,55, 0,6), kafa kabukları + yüz ekranı saydam | iç kablolar görünsün |
| 34.2 | (-0,85, 0,62, 1,25) | (-1, 0,2, 0) | bindirme cıvatası p0322 gizle-fark 2 px |
| 34.4 | (-1, 0,35, -0,5) | (-1, 0,3, -0,3) | p0306 41 / 225 px (oran 0,18) |
| 34.6 | (-1, 0,35, -0,5) | (-1, 0,3, -0,3) | p0308 / p0310 34 / 31 px (oran < 0,2) |
| 34.7 | (-1, 0,45, 0,6) | (-1, 0,45, 0,2) | kelepçe cıvatası p0440 hoparlörün arkasında: 0 px → 127 px |
| 34.8 | varsayılan | (-1, 0,35, -0,5) | p0268 17 px |
| 34.9 | (-0,85, 0,62, 1,25) | (1, 0,35, -0,5) | p0270 22 px |
| 35.1 | varsayılan | (0,6, 0,45, 1,25) | p0280 29 px |
| 35.4 | (0,85, 0,62, 1,25) | (0, 0,4, 1) (tam önden) | VESA pulları p0424 / p0426 48 / 27 px, oran < 0,2 |
| 49.4 | adım "arka" | (-0,85, 0,62, -1,25) | 49.3 ile aynı bakıştan kare neredeyse aynıydı |

Kamera adayları scratchpad'de tarandı (alt adım başına 9–16 yön, her yönde bütün yeni parçalar için gizle-fark ve yalnız piksel);
en az değişiklikle hepsini geçiren yön seçildi.

## 5. Anlaşılırlık tablosu (kabuk alt adımları, F10d ile yan yana)

Bakılan kareler: 42 kabuk alt adımının hepsi açık ve koyu temada (1400 × 900, `?cekim=1`), kamera değişen 12 alt adım yeniden. Ölçüt
F10d'ninki: "açık" = yeni parça, nereye bağlandığı ve bağlantı elemanlarının yeri kareden okunuyor.

| alt adım | F10d | F10e | gözlem (F10e) |
| --- | --- | --- | --- |
| 31.1–31.4 | açık | açık | kabuk açık gri, kenarlı; bağlandığı braket / iskelet pembe |
| 31.5 | zor | **açık** | arka kabuk rafı pembe, 4 halka; kadraj rafı kapsıyor (eski: 4 sarı cıvata, raf seçilmiyor) |
| 31.6–31.8 | açık | açık | yüz kabuğu taban (pembe kenarlı), kamera / QLED / tırnaklar gerçek renkte |
| 31.9 | zor | **zor** | yüz grubu kafada belli, kabuklar saydam; metindeki kablo bağlantıları küçük, CSI şeması karede yok (kablolama içeriği değişmez) |
| 31.10 | zor | **açık** | kafa kabukları pembe, 9 dikiş halkası; cıvataların yeri halkalardan okunuyor |
| 33.1–33.10 | açık | açık | bantlar açık gri + kenar, braketler pembe, perçin / cıvata halkaları |
| 34.1–34.3, 34.5 | açık | açık | |
| 34.4 | zor | **açık** | braket pembe, x 0 dikişinin cıvataları halkalı; bakış soldan |
| 34.6 | zor | **açık** | 34.4 ile aynı düzen ve bakış; 3B kare neredeyse aynı (son kare çiftinde de). Ayıran: panel başlığı, alt adım listesindeki işaretli satır, basılı karede kare başlığı, küçük görünümde biraz farklı yükseklik | *(düzeltildi, bkz. §12.5)*
| 34.7 | zor | **açık** | bant (masa tabanı) pembe kenarlı, hoparlör kara, iki kelepçe cıvatası görünür (127 / ≥ 30 px) | *(düzeltildi, bkz. §12.4)*
| 34.8, 34.9 | açık | açık | |
| 35.1, 35.2 | açık | açık | |
| 35.3 | zor | **açık** | direk pembe, taşıyıcı kenarlı (açık temada da), 6 halka (cıvata, pul, çekiç somun) |
| 35.4, 35.5 | açık | açık | 35.4 tam önden: ekran saydam, 4 VESA halkası |
| 36.1, 36.2 | açık | açık | |
| 36.3 | zor | **açık** | omuz bandı pembe, 3 halka; kadraj bantları kapsıyor |
| 49.1–49.5 | açık | açık | 49.3 / 49.4 artık farklı bakıştan |

- F10d: açık 34, zor 8, anlaşılmıyor 0. **F10e: açık 41, zor 1 (31.9), anlaşılmıyor 0.** *(düzeltildi, bkz. §12.4)*
- **Zor kalan 31.9, gerekçe:** alt adımın işi beş ayrı bağlantı (CSI şeridi → Pi, QLED HDMI, SY8205 çıkışı, Touch USB ve yüz kabuğunu
  takmak). Son karede (açık + koyu, F10e-goruntu-31-9) yüz grubu kafada belli; kafa kabukları ve yüz ekranı saydam, iç kartlar ve
  kablolar görünüyor. Ama kabloların hangi konnektöre girdiği küçük ve saydam katmanların arkasında; CSI şeridi karede ayrı çizgi
  olarak okunmuyor. Bunu düzeltmek için kablo şeması eklemek ya da metni bölmek gerekiyor; brief kablolama içeriğini değiştirmeyi
  yasaklıyor. Önceki F10d karesine göre iyileşme var (kafanın içi görünüyor, bağlandığı kafa pembe), ama tek bakışta okunmuyor.
- Kabuk dışı 15 adım (2, 5, 8, 12, 15, 17, 21, 25, 28, 30, 39, 41, 43, 45, 48), açık + koyu: 14 açık; **21 zor** (tezgâh: iki S1
  hornu küçük, gri; horn halkası ve kenarı yeri gösteriyor ama iki birim karede uzak). 43 / 45 hornları da küçük, pembe bağlandığı yer
  ve halka okunuyor. Gerçek renkte metal parçalar (horn, cıvata) sınıf kipindeki kadar parlak değil; bunun için §2'deki "önceki
  grisine yakın → kenar" kuralı eklendi.

## 6. Doğrulama betiği

`planlama/d158/F10e-dogrula.py` → `F10e-dogrula.json` (+ `F10e-goruntu-*.png`). Bölümleri ve ilk koşudan sonraki değişiklikler:

- Görünürlük (gizle-fark) ilk koşuda bütün yeni parçaları (bağlanan birimin iç parçaları dahil) saydı: F10d'nin ayrımına (alt adımın
  kendi satırları; birim: en büyük parça + iç parçalar masadaki alt adımında) getirildi. Geçme şartı: F10d'nin soluk bulduğu iki parça
  okurun gördüğü pikselle ölçütü geçer; bütün kabuk alt adımlarındaki sonuç ayrıca yazılır (`tam_gecti`, `tam_kalan`). Isıl gömmeler
  (hazırlıkta takılı) ayrı sayılır.
- Bağlandığı yer doğruluğu: kaynak yalnız yeni bağlantı elemanlarıydı; veri halka bulunmayınca yüzey temasına düştüğü için (adım 8
  teker → motor, 48 bilezik → üst kol tüpü) yeni ana parçalar da eklendi.
- Kare başlığı denetimi `?sahne=1` karesine taşındı (başlık artık yalnız orada, §2).

Son tam koşu (00:13, çıkış 0, 772 s), eşikler parantezde:

| bölüm | sonuç | geçti |
| --- | --- | --- |
| renk veri ↔ CAD | 1192 / 1192 eşit; GuiDocument 1031 / 1031 | evet |
| renk sahnede (100 konum × 2 tema) | yeni görülen 1192 / 1192, yanlış 0 | evet |
| karşıtlık (kenar eşiği 3,0; önceki grisi 1,5) | açık: eşik altı 677, kenarsız 0; önceki grisine yakın 507, kenarsız 0. koyu: 164 / 0; 65 / 0; saydam kenarsız 0 | evet |
| tonlar (ΔE76 en yakın gerçek renk) | ev `#ff3fa4` 57,7; seçim `#7cfc00` 78,5; kehribar `#ffb000` 21,9 (yalnız küçük görünümde) | bilgi |
| bağlandığı yer | veride 95, sahnede 95; kabuk yeni parçalı 41 / 41 | evet |
| bağlandığı yer doğruluğu (≤ 1 mm) | 186 / 186 (+ 15 masa tabanı) | evet |
| işaretler | işaret 1188 = bağlantı elemanı 1188; kabuk 277 / 277 (265 küme); kare dışı / yanlış 0 | evet | *(düzeltildi, bkz. §12.6)*
| görünürlük, soluk iki parça (≥ 30 px ve ≥ 0,20 × yalnız) | 31.3 p0762 40 / 142; 34.7 p0440 137 / 314 | evet | *(düzeltildi, bkz. §12.2)*
| görünürlük, bütün kabuk (bilgi) | 42 alt adım, yeni 335; okurun pikseliyle eşik altı 2: 35.3 p0432 taşıyıcı pulu M6 141 / 750 (oran 0,188), 36.1 p0288 bindirme cıvatası 29 / 154; ısıl gömme 4 (33.3 p0367 29, 33.6 p0381 23, 34.1 p0321 29, 34.7 p0439 1) | bilgi | *(düzeltildi, bkz. §12.2)*
| arayüz | renk kipi, `C`, `I`, satır seçimi → halka seçili, `?renk=sinif&isaret=0`, kare başlığı çiftlerde farklı | evet |
| renk demo (40 örnek) | gerçek = demo 0, sınıf = demo 0 | **hayır, karar (§11)** |

## 7. Devredilen ölçümler

FreeCAD'siz: `rehber_giris.Giris` (ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, dinlenmedeki temas sayılmaz, adım 0,5 / 2 mm),
nokta–üçgen uzaklığı ve parite (`robot.glb`). Betik ve ham çıktı scratchpad'de.

1. **Etek ön bandı, iki parçalı yol (K55 c).** Etek ön sağ (33.3, ısıl gömmeleriyle) ve sol (33.5):
   - Düz +z: 0,5 mm'de braket z+105'in perçin somunu (0,8 mm ortak hacim). Bacak 1 (dışa / içe x, ±y, −z, dışa-yukarı; 1, 2, 3, 5, 8,
     12 mm) sonra bacak 2 +z: **hiçbiri serbest değil**, hepsi bacak 1'in ilk 0,5–1 mm'sinde çarpıyor (perçin somunu 0,45–2,14 mm,
     sonar 3 mm, komşu etek bantları). Tersi (önce +z 0,5 / 1 mm, sonra dışa / ±y): perçin somunu 0,8 mm.
   - Perçin somunu engelden çıkarılınca düz +z **serbest** (181,5 mm'de ayrılıyor); dışa x ve +y'de sonar 3 mm.
   - Sonuç: iki bacaklı bir yol yok; bandı tutan, braket z+105'teki perçin somunu. Uygulanabilir aday sıra değişikliği (perçin somunu *(düzeltildi, bkz. §12.6)*
     bant yerindeyken bandın deliğinden takılır) ya da K55'in a / b seçenekleri. **Karar Ahmet'te; rehberde uygulanmadı.**
2. **Arka servis kapağı ↔ orta bant gerçek derinliği** (49.3; ışın ölçümü dinlenmede 1,5 mm "kiriş" diyordu): kapağın köşelerinden
   orta bant sağın içinde kalan 26 / 533, en çok 0,231 mm, medyan 0; orta bant solun içinde 14, en çok 0,059 mm. Bantların köşelerinden
   kapağın içinde kalanların derinliği 0. Giriş −z: 6,5 mm'de kutular ayrılıyor, çarpışma yok. **Temas (≤ 0,23 mm), çarpışma değil.**
3. **Adım 41 (G4) "+x'ten kaydırarak takılmaz".** S1 kaset gövdesi sağ (p0232) ve sol (p0234), CAD duruşunda, kapak ve cıvatalar
   hariç: sağ +x 0,5 mm'de üst kol tüpü (5,34 mm), −x'te omuz bandı sağ (93 mm) ve göğüs bandı; sol aynalı. Önden radyal (+z)
   **serbest** (122,5 mm). **Uyarı tutuyor** (iki x yönü de kapalı, radyal açık); metin değişmedi. Not: ölçüm CAD duruşunda; metindeki *(düzeltildi, bkz. §12.6)*
   kol duruşunda (S1 −45 / −20 / 0) ölçülmedi.

## 8. Zincir ve kabul

**F10d ilk koşuda düştü (23:08, çıkış 2).** Kabuk görünürlüğünde (kimlik tamponu, ≥ 30 px ve ≥ 0,20 × yalnız) 4 parça kaldı: 33.5
p0396 29 / 54, p0398 29 / 57; 33.7 p0530 26 / 94; 36.1 p0462 17 / 133. HEAD'deki F10d sonucunda aynı parçalar 31 / 60, 32 / 62, 33 / 106,
31 / 145 idi.
- Kök neden ölçüldü: hem görünen hem "yalnız" piksel aynı oranda düşmüştü (≈ 0,9), yani örtülme değil, parçalar küçülmüş. Kimlik
  tamponu renkten bağımsız, bağlandığı yer parçaları önceki parçalarla aynı opaklıkta, kamera alanları bu alt adımlarda değişmedi.
  Kalan fark F10e'nin kare başlığıydı: araç çubuğunun altında (tuvalde y 92–116) bant açıp güvenli alanın üstünü 30 px aşağı itiyordu.
- Düzeltme: kare başlığı yalnız `?sahne=1` (yazdırma / PDF) karesinde (`rehber/app.js`, `kareBaslik`); F10e betiğindeki başlık
  denetimi o kareye taşındı. Ölçüm (tek alt adım): 33.5 31 / 60, 32 / 62; 33.7 33 / 106; 36.1 31 / 145 (HEAD değerleriyle aynı).
- Sonra üretim (`--veri-yok`, çıkış 0) ve zincir baştan, sırayla koşuldu (§0). F10d ikinci koşuda: kabuk 42 alt adım, yeni 335,
  görünmeyen 0, istisna 0, masa yabancı şema 0, gezinme 100 / 100, panel = takma 100 / 100, 360 px taşma 0 → GEÇTİ.

Kabul ölçütleri (brief):

| ölçüt | hedef | sonuç | durum |
| --- | --- | --- | --- |
| renk veri ↔ CAD | 1192 / 1192 | 1192 / 1192; GuiDocument bağımsız denetim 1031 / 1031 | geçti |
| rehber = demo (≥ 30 parça) | eşit | 40 örnek, eşit 0 (demo sınıf paleti; ne gerçek ne rehber sınıf rengi) | **kaldı, karar (§11)** |
| karşıtlık (iki tema) | eşik üstü | eşik altı rengin hepsi kenarlı (açık 677, koyu 164; kenarsız 0) | geçti |
| kabuk anlaşılmıyor | 0 | 0 | geçti |
| kabuk zor | ≤ 2, gerekçeli | 1 (31.9, gerekçe §5) | geçti | *(düzeltildi, bkz. §12.4)*
| vurgu ve işaret, bütün kabuk alt adımları | var | vurgu 41 / 41 (yeni parçalı), işaret 277 / 277 | geçti |
| işaret sayısı = bağlantı elemanı sayısı | eşit | 1188 = 1188 | geçti | *(düzeltildi, bkz. §12.6)*
| alt adım / konsol | 50 / 50, 0 | 50 / 50, konsol 0 (üretim, F10a, F10e) | geçti |
| parça | 1192 ↔ 1192 | 1192 ↔ 1192, her parça tek alt adımda | geçti |
| denetim | 0 | ASCII 0, gruplama 0, çelişki 0, zorunlu uyarı eksik 0 / 40 | geçti |
| ulaşılamaz / giremez | 0 / 0 | sıra: ulaşılamaz 0 / 565; F10a / F10d giriş denetimleri geçti | geçti |
| görünmeyen yeni parça | 0 | F10d ölçüsüyle (kimlik tamponu) 0 / 335. Okurun pikseliyle (F10e gizle-fark) 2 parça eşik altında (§6), ikisi de karede görünüyor (141 ve 29 px) | geçti (F10d ölçüsü); okur pikseli bilgi | *(düzeltildi, bkz. §12.2)*
| boş yazdırma karesi | 0 | 100 / 100 kare çizili, boş 0, en düşük çizim oranı 0,0606 | geçti |
| arayüz: seçim, patlat / tak, küçük görünüm, gezinme, ağsız açılış, 360 px | geçer | F10a: seçim 6 / 6, ağsız dış istek 0, küçük görünüm 50 / 50, 360 px taşma 0, CDN 0; F10d: gezinme ileri / geri 100 / 100; F10e: `C`, `I`, satır → halka | geçti |
| PDF önce / sonra | sayfa ve en küçük yazı | 69 → 69 sayfa; 8,1 → 8,1 pt (dom ve pdf); 12576 kB | geçti |
| F9b | 0 | hata 0 (veri karması değişti: bilgi) | geçti |
| çarpışma kontrol | 0 | çıkış 0, sonuç güncel | geçti |
| regresyon | 10 / 10 | 10 / 10 aynı | geçti |
| model geometrisi | değişmedi | `rehber/veri/robot.glb` git'e göre değişmedi; CAD dosyalarına dokunulmadı | geçti |

## 9. Önce / sonra kareleri

`F10e-dogrula.py` 19 kare yazdı (1400 × 900 iki sayfa yan yana; "önce" = HEAD rehberi ve verisi, "sonra" = şimdiki):
`F10e-goruntu-<alt adım>-once-sonra-{acik,koyu}.png` (zor 8 alt adım × 2 tema = 16) ve `F10e-goruntu-cift-{34-3-34-5,34-4-34-6,49-3-49-4}.png`.

Son koşudan sonra kendim baktıklarım:
- 35.3 açık temada: önce mavi saydam taşıyıcı, cıvatalar sarı, direk seçilmiyor. Sonra kara taşıyıcı kenarlı, direk pembe, 6 halka.
  **Açık.**
- 31.9 koyu temada: önce turuncu kabuk, içi görünmüyor. Sonra kafa pembe, kabuklar saydam, kartlar ve kablolar görünüyor ama
  konnektörler küçük. **Zor** (§5).
- 34.7 açık temada: önce turuncu saydam bant, sarı cıvatalar. Sonra açık gri bant pembe kenarlı, hoparlör kara, 11 halka. **Açık.** *(düzeltildi, bkz. §12.4)*
- Çift 34.4 / 34.6: 3B kare neredeyse aynı. Ayıran: panel başlığı, alt adım listesi, küçük görünümde hafif yükseklik farkı. *(düzeltildi, bkz. §12.5)*
- Çift 49.3 / 49.4: bakış farklı, kapak ve halka düzeni farklı. **Ayırt ediliyor.** *(düzeltildi, bkz. §12.5)*

Son koşuda üretilen ama bu turda bakılmayan kareler: 31.5, 31.10, 34.4, 34.6, 36.3 (iki tema), 35.3 / 34.7 koyu, 31.9 açık, çift
34.3 / 34.5. Bu alt adımlara §5'te (kare başlığı kaldırılmadan önce, scratchpad karelerinde) bakılmıştı. Kadraj o zamandan beri
yalnız ≈ %5 büyüdü, düzen aynı. Bu turdaki hükümleri o bakışa dayanıyor; bu tur karelerine bakılmadı.

Soluk iki parça: 31.3 p0762 40 / 142 px, 34.7 p0440 137 / 314 px (ölçüm). 34.7'de kelepçe cıvataları kendi karesinde halkalı ve *(düzeltildi, bkz. §12.2)*
görünür. 31.3'ün son karesine bu turda bakılmadı; yalnız ölçüm var.

## 10. Dokunulan dosyalar

Elle değiştirilen:
- `rehber/app.js`: gerçek renk kipi, bağlandığı yer tonu, kenar kuralları, işaret katmanı, kare başlığı (yalnız `?sahne=1`),
  `C` / `I` tuşları, RehberTest ölçümleri.
- `rehber/index.html`, `rehber/stil.css`, `rehber/yazdir.html`
- `tasarim/freecad/rehber/rehber_gorunum.py` (yeni), `rehber_uret.py` (görünüm adımı), `rehber_denetim.py` (`ASCII_TAMAM`: "renk"),
  `rehber_metin.py` (yalnız kamera / saydam alanları, §4)
- `planlama/d158/F10e-dogrula.py` (yeni), `planlama/d158/F10e-gunluk.md` (bu dosya)

Üreticilerin yazdığı:
- `rehber/veri/rehber-veri.js` / `.json`, `rehber/goruntu/*.png`
- `planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/*.png`, `planlama/rehber/kontrol.json`
- `planlama/d158/F10e-dogrula.json`, `planlama/d158/F10e-goruntu-*.png` (19)
- `planlama/d158/F10d-dogrula.json`, `planlama/d158/F10a-dogrula.json` (yeniden koşu sonucu; betikleri değişmedi)

Dokunulmayan: `F10d-dogrula.py`, `F10a-dogrula.py`, `FREECAD-KILIT.txt` (hep "boş"), dokunulmazlar listesi. Çalışma ağacında
önceden değişik görünen kullanıcı dosyaları (kabuk `gorsel/*.png`, `yerlesim-kontrol.json`, `dongu-158.md` …) bu paketin değil.

## 11. Açık kalanlar ve karar gerektirenler

1. **Demo renkleri (karar).** `tasarim/Robot-Tasarim-Demosu.html` kendi sınıf paletini (TUR) kullanıyor; 40 örnekte rehberin ne
   gerçek ne sınıf rengiyle eşit (ör. bağlantı `#c9a227` ↔ `#d4ac0d`, satın alınan `#2f6fb3` ↔ `#2f86d4`, profil `#8d99a6` ↔
   `#16a085`). Demo `demo_uret.py` ile üretiliyor ve bu pakette yasak. Seçenekler: (a) demo üreticisi verideki `gr` alanını okusun
   (gerçek renk); (b) iki palet ayrı kalsın, kabul ölçütü "demo = rehber sınıf kipi" olarak yeniden yazılsın. Öneri: (a), tek kaynak CAD.
2. **K55 etek ön bandı (karar).** İki bacaklı yol yok (§7.1). Bandı braket z+105'teki perçin somunu tutuyor. Aday: perçin somununu *(düzeltildi, bkz. §12.6)*
   bant yerindeyken takmak (sıra değişikliği) ya da K55 a / b. Rehberde uygulanmadı.
3. **Okurun pikseliyle eşik altı iki parça (bilgi, ölçüt adayı).** 35.3 p0432 taşıyıcı pulu M6: 141 px, oran 0,188 (eşik 0,20). *(düzeltildi, bkz. §12.2)*
   36.1 p0288 bindirme cıvatası: 29 px (eşik 30). F10d ölçüsüyle ikisi de geçiyor. İkisi için kamera taranmadı. Okurun pikseli kabul
   ölçütü olacaksa iki alt adımda kamera taraması gerekir, sonra üretim ve zincir yeniden (≈ 1,5 saat).
4. **Isıl gömmeler, okurun pikseli (bilgi).** 33.3 p0367 29, 33.6 p0381 23, 34.1 p0321 29, 34.7 p0439 1 px. Hepsi hazırlıkta takılı *(düzeltildi, bkz. §12.2)*
   (adım 0), bantla gelir. 34.7'de p0439 bandın iç yüzünde, hoparlörün arkasında.
5. **31.9 zor** (§5): kablo şeması ya da metin bölme gerekir; kablolama içeriği yasak. Karar Ahmet'te.
6. **21 zor** (kabuk dışı, §5): iki S1 hornu küçük; bu pakette kamera değiştirilmedi.
7. **Adım 41 ölçümü** CAD duruşunda yapıldı; metindeki kol duruşunda (S1 −45 / −20 / 0) ölçülmedi. *(düzeltildi, bkz. §12.6)*
8. Paket dışı: `planlama/dongu-158.md` çalışma ağacında değişik (18:51; bu paket yazmadı). Önceki paketlerden / oturumlardan kalan beş
   `tail -f` süreci açık (9–11 Kasım'da başlamış; f2, f10c-b, f10c-c, f10d-b günlüklerini izliyor). Bu paketin değil, dokunulmadı.
   Bu pakete ait arkada süreç yok (python, başsız tarayıcı yok; denetlendi).

## 12. Düzeltme turu 1 (12.11.2026)

Brief: `planlama/d158/F10e-duzeltme-1-brief.md`; kontrol: `F10e-kontrol.md` (B, DÜZELTME GEREKLİ). Uygulama ajanı (D1), A'nın
yerine. Geçici dosyalar (betik, kare, ara sonuç) scratchpad'de (`f10e-d1/`), depoya kopyalanmadı. FreeCAD koşulmadı (gerekmedi);
`planlama/d158/FREECAD-KILIT.txt` baştan sona "boş". Eski iddialar silinmedi; değişen satırların sonunda "düzeltildi, bkz. §12.x".

### 12.1 Ölçüm fonksiyonu neden ekran görüntüsünden farklıydı (bulgu 2)

- **Kök neden:** `RehberTest.gorunurlukFark` sahneyi sahne dışı bir `WebGLRenderTarget`'a (4 örnek, `colorSpace: SRGB`) çizip
  okuyordu. three r160 XR olmayan render target'a shader çıktısını **doğrusal** (LinearSRGB) yazar; hedefin `colorSpace` seçeneği
  çıktıyı değiştirmez (vendor paketinde `outputColorSpace: w===null ? renderer.outputColorSpace : w.isXRRenderTarget ? … : Linear`).
  Ekrandaki tuval sRGB'ye kodlanır. Doğrusal değerlerde saydam katmanların arkasındaki farklar büyük çıkıyordu.
- **Ölçüm (31.3 p0762, açık tema, aynı sahne ve kamera, Σ|ΔRGB| > 24):** render target 4 örnek 40 px (en büyük Σ 45), render target
  örneksiz 35 px (51), tuval kenar yumuşatmalı 0 px (19), tuval yumuşatmasız 0 px (19). B'nin ekran görüntüsü farkı 0 px. Yani
  fark örneklemeden değil, render target yolundan.
- **Düzeltme:** `gorunurlukFark` artık sayfanın kendi tuvaline (ekrana giden `renderer.render(sahne, kamera)` yolu) çizip
  `gl.readPixels` ile okuyor, sonunda sayfayı yeniden çiziyor (`rehber/app.js`). Sınama: 31.3 p0762 açık 0 (B 0); 34.5 p0256 koyu 0
  (B 0), açık 56 (B 56). B'nin 11 parçalık ekran / renderer eşleşmesiyle aynı sonucu veriyor.
- `F10e-dogrula.py` görünürlüğü artık **iki temada** koşuyor ve ikisi de geçme şartında (§12.2).

### 12.2 Düzeltilmiş ölçümle bütün kabuk alt adımları (bulgu 1, 2)

Ölçüt değişmedi: ≥ 30 px ve ≥ 0,20 × yalnız (kimlik tamponu); ısıl gömmeler ayrı sayılır. "Önce" koşusu düzeltilmiş ölçüm
fonksiyonuyla ama A'nın çizimiyle (`?ustte=0`: §12.3'teki çizim değişikliği kapalı), "sonra" bu turun çizimiyle. 42 alt adım, tema
başına 335 yeni parça (F10d'nin sayımı: alt adımın satırları + bağlanan birim; B'nin "simdi" sayımı 212).

| tema | önce: eşik altı (ısıl gömme hariç) | önce: ısıl gömme eşik altı | sonra | sonra: ısıl gömme |
| --- | --- | --- | --- | --- |
| açık | 1: 35.3 p0434 111 / 2082 | 2: 31.3 p0762 0 / 142, 34.7 p0439 1 / 93 | **0** | **0** |
| koyu | 18 (aşağıda) | 3: 31.3 p0762 0 / 142, 33.3 p0367 29 / 48, 34.7 p0439 0 / 93 | **0** | **0** |

Koyu "önce" 18 (fark / yalnız px): 34.2 p0300 31 / 165, p0302 26 / 174, p0324 27 / 191; 34.3 p0244 3 / 218; 34.4 p0242 2 / 265,
p0304 28 / 228, p0306 28 / 266; 34.5 p0256 0 / 222; 34.6 p0254 2 / 266, p0308 34 / 227, p0310 27 / 265; 34.8 p0272 29 / 77; 34.9 p0266
11 / 94, p0312 14 / 108, p0314 12 / 118; 35.1 p0280 0 / 105; 35.2 p0282 0 / 110; 35.3 p0434 111 / 2082. B'nin 20'sinden 36.1 p0288
(31 / 154) ve p0290 (35 / 157) bu ölçümde eşiği geçiyor (B kendi siluetini "yalnız" aldı; burada F10d'nin kimlik tamponu). Bu ölçümde
başka gizli parça çıkmadı: düzeltilmiş fonksiyonun bulduğu eşik altı parçaların hepsi B'nin listesinde.

"Sonra" (iki tema): eşik altı 0, ısıl gömme eşik altı 0, istisna 0, birim 0. Soluk iki parça: 31.3 p0762 açık 156 / 142, koyu 155 / 142;
34.7 p0440 açık 239 / 314, koyu 233 / 314. En küçük değerler: oran 0,230 (35.3 p0437, 741 / 3223, iki tema), piksel 33 açık / 37 koyu
(33.7 p0392, yalnız 59). Önceki "eşik altı 2: 35.3 p0432 141 / 750, 36.1 p0288 29 / 154" (§6) render target ölçümüydü; düzeltilmiş
ölçümle önce 167 / 750 ve 35 / 154 (geçiyor), sonra 273 / 750 ve 81 / 154. Ham sonuç: scratchpad `gor-once-light.json`,
`gor-once-dark.json`, `gor-sonra-1.json`; tam koşu `F10e-dogrula.json` (§12.7).

### 12.3 Koyu temada kök neden ve çözüm (bulgu 1)

- **Kök neden: saydamlık sırası (+ renk ↔ zemin).** Kenar kuralı değil: bu cıvatalar kenar istemiyor (çelik `#80858f` koyu zemin
  `#1b1c20` ile karşıtlık 4,3). Kameradan parçanın köşelerine ışın (34.5 p0256, 228 örnek): hepsinin önünde bu alt adımın bandı
  (p0209, opaklık 0,4) ve bağlandığı braket (p0207, 0,25) var; ikisi de çift yüzlü, derinlik yazmaz, cıvatanın üstüne her yüzde
  karışır. Kalan geçirgenlik küçük (gizlerken değişen en büyük Σ: koyu 22, açık 45). Açık temada koyu çelik açık zeminden yine
  ayrılıyordu; koyu temada arkasındaki koyu zemine / griye karışıyor. 35.1 p0280 aynı (p0213 0,4 + p0211 0,25). 31.3 p0762 üç saydam
  yeni parçanın (p0753, p0822, p0823; 0,4) arkasında, iki temada 0.
- **Çözüm (gerçek renk değişmedi):** saydam listesi olan alt adımda, saydam olmayan yeni bağlantı elemanı aynı renkte, opaklık 1,
  derinlik yazarak saydam geçişte saydam katmanlardan **sonra** çizilir (`renderOrder` 10; kenarı 11). Opak parçaların arkasındaki
  yeri gizli kalır (derinlik testi açık); saydam katmanın arkasındaki yeri tam renginde görünür. Küçük görünümdeki vurgunun yöntemi.
  `rehber/app.js` (`ustteKoy`; `?ustte=0` yalnız önce / sonra ölçümü için kapatır). Renk denetimi (`RehberTest.renkler`) aynı rengi
  ve opaklık 1 okur.
- Gerekçeli istisna: gerekmedi (0).

### 12.4 34.7 (bulgu 3)

- Denenen: (1) kadraj yalnız hoparlör grubuna (yeni alan `kadraj`, veri + sayfa). Grubun ekran kutusu bugünkü karede ≈ 110 × 135 px
  (köşe izdüşümü; B gözle ≈ 80 px); kadrajla kareyi dolduruyordu, kelepçe, iki cıvata, ısıl gömmeler ve kara hoparlör okunuyordu.
  Ama masa tabanı olan bant kareden taştı ve 13 halkanın 8'i kare dışına çıktı (kare gözle, açık + koyu). F10d'nin geçme şartı her yeni parçanın sınır kutusunun karede olmasını istiyor ve F10e işaret denetimi her
  işaretin karede olmasını; ikisini gevşetmek ölçtükleri şeyi değiştirirdi. **Geri alındı** (veri ve kod).
  (2) Saydamlık (yalnız tarayıcıda, depo değişmedi): hoparlör, ön halka, ped opak; kap ve kelepçe 0,4; bir de kelepçe opak. Grup aynı
  boyutta (≈ 110 × 130 px), katman sırası yine ayrılmıyor, bir varyantta boss'taki ısıl gömme hoparlörün arkasında kaldı. Daha iyi değil.
  (3) Kamera: bu turda taranmadı.
- **Sonuç: 34.7 "zor" kalıyor.** Gerekçe: hoparlör grubu (ön halka, ped, kap, kelepçe) karede küçük, 0,4 opaklıklı katmanlar üst üste,
  sıra ayırt edilmiyor. Kelepçe cıvataları ve ısıl gömmeler artık tam renkte (§12.3).
- "Hoparlör kara" ifadesi (§5, §9) yanlıştı: kara hoparlör beyaz saydam kabın ve kelepçenin arkasında **koyu gri** görünüyor (kare
  gözle, açık + koyu).
- Anlaşılırlık sayımı (§12.8): açık 40, zor 2 (31.9, 34.7), anlaşılmıyor 0. Eşik (zor ≤ 2) tutuyor.

### 12.5 Benzer kare çiftleri (bulgu 4)

- **Ayırt edici:** küçük görünümün alt kenarında, kutunun içinde, yeni parçaların yeri: taraf (vurgulu kutunun ortası: sağ / sol /
  orta, ön / arka) ve yükseklik aralığı (y, mm). Örnek: 34.3 "sağ · y 470–660", 34.5 "sağ · y 620–810"; 34.4 "sol · y 480–650", 34.6
  "sol · y 630–800"; 49.3 "orta-arka · y 810–1010", 49.4 "orta-arka · y 1030–1200" (kareden okundu). Küçük görünüm etkileşimli sayfada
  ve basılı karede (`?sahne=1`) var; etiket ikisinde de görünüyor (gözle: 34.4 basılı kare, 34.4 telefon 360 px).
- **Sahne boyutu değişmedi:** etiket küçük görünüm kutusunun içinde; güvenli alan (`guvenliAlanlar`) küçük görünümün kutusunu zaten
  dışarıda tutuyor, etiketi okumuyor. Kamera ve kadraj kodu değişmedi. F10d görünürlük koşusu (etiketle) GEÇTİ: görünmeyen 0 (§12.7).
- `rehber/index.html` (`#mini-yer`), `rehber/stil.css` (`.mini-yer`, dar ekranda 9,5 px), `rehber/app.js` (`miniYer`).
- Not: yazı etiketi. 3B sahnenin kendisi (kamera, kompozisyon) 34.3 / 34.5 ve 34.4 / 34.6'da hâlâ aynı; ayrım etiketten ve küçük
  görünümdeki kehribarın yüksekliğinden.

### 12.6 Kayıt düzeltmeleri

| eski iddia | yer | düzeltme |
| --- | --- | --- |
| "işaret 1188 = bağlantı elemanı 1188" | DURAKLAMA 3, §6, §8 | Veride **893 benzersiz** bağlantı elemanı. 1188 = konum başına yeni bağlantı elemanı işaretlerinin toplamı (adım genel bakışı + alt adım; alt adımlı adımların elemanları iki kez sayılır). Yani "işaret 1188 = konum başına yeni bağlantı elemanı 1188 (benzersiz 893)". Sayı B ile aynı. |
| "tek kaynak CAD; rehberde ayrı renk tablosu yok" | §1 | **İstisna:** kablo yolu 12 parçası (p1180–p1191) sahnede verinin `renk` alanıyla, yani rehberin kablo paletiyle çiziliyor (`app.js` `parcaRengi`: `p.renk || …`, paketten önce de böyleydi). Örnek: p1187 CAD `#f20d0d` (kırmızı) ↔ rehber `#2f86d4` (mavi). Orkestratör kararı: bu pakette değiştirilmedi. **P10.7'ye devredildi (kablo içeriği).** |
| "iki bacaklı bir yol yok" (9a) | §7.1, §11.2 | Günlükteki yönteme göre (betik bu turda yeniden koşulmadı): bacak 1 için 6 öteleme yönü (dışa / içe x, ±y, −z, dışa-yukarı) × 6 uzunluk (1, 2, 3, 5, 8, 12 mm) = 36, ardından +z; ters sıra (önce +z 0,5 / 1 mm, sonra dışa / ±y) 2 × 3 = 6. **Denenen 42 iki bacaklı öteleme yolunda bulunmadı; dönme ve ara açılar denenmedi.** "Perçin somunu tutuyor" somun çıkarılınca düz +z'nin serbest olmasıyla destekleniyor. |
| "+x'ten kaydırarak takılmaz", "uyarı tutuyor, metin değişmedi" (adım 41) | §7.3, §11.7 | **Metin ölçülene indirildi** (kol duruşunda ölçmek FreeCAD'siz poz kurmayı gerektirir; daha çok iş ve bu turda doğrulanamaz). `rehber_metin.py` G4 `is_`: "Sırayı bozma. CAD duruşunda yandan kaydırılamaz (+x'te üst kol tüpüne, −x'te omuz bandına değer); önden radyal tak." Kol duruşunda: ölçülmedi. |
| görünürlük satırları ve "geçti" | §6, §8, §9, §11.3, §11.4 | §12.2 ve §12.7 |
| anlaşılırlık "açık 41, zor 1", 34.7 açık, "hoparlör kara" | §5, §8, §9 | §12.4, §12.8 |
| benzer çiftler "ayırt ediliyor" | §2, §5, §9 | O zaman yalnız yazıyla (panel / kare başlığı); şimdi küçük görünüm etiketiyle de, §12.5 |

Sayfa metni: rehberde 1188 / 893 ve "tek kaynak" ifadesi geçmiyor (yalnız günlükte); değişen sayfa metni yalnız adım 41.

### 12.7 Üretim ve zincir (12.11.2026 07:00–08:08, tek üretim koşusu)

**İlk deneme (02:04, durduruldu):** `rehber_uret.py --veri-yok` araç tarafından arka plana alındı; oturum boştayken sistem belleği
kritik düşünce Claude Code süreci öldürdü (komutun kendi hatası değil). Talimat gereği kendiliğinden yeniden başlatılmadı. Ahmet'in
kararıyla ("yeniden başlatmadan yine koş") 07:00'da aşağıdaki yöntemle baştan koşuldu; 02:04 koşusunun yarım çıktılarının hepsinin
üzerine 07:00 koşusu yazdı (tutarlılık tablosu aşağıda).

**Yöntem:** her komut scratchpad'deki bir sarmalayıcıyla ayrı, gizli pencereli süreç olarak başlatıldı (`Start-Process`); çıktı
dosyaya, çıkış kodu ve süre durum dosyasına. Sarmalayıcı 15 s'de bir boş fiziksel belleği ve boş commit'i ölçtü; art arda iki ölçümde
fiziksel < 0,5 GB ya da commit < 2 GB olsa süreç ağacını durduracaktı (hiç tetiklenmedi). Her komuttan önce boş bellek ≥ 2 GB ve
arkada python / Chrome olmadığı denetlendi; aynı anda tek komut. Yoklama ön planda, kısa aralıklarla.

| komut | başlangıç | boş bellek önce (GB) | çıkış | süre | koşu boyunca en düşük boş fiziksel bellek (GB) | sonuç |
| --- | --- | --- | --- | --- | --- | --- |
| sarmalayıcı denemesi (scratchpad, 20 s bekleyip bilerek 3 döner) | 07:00:20 | kayıtta yok | 3 (beklenen) | 21 s | 2,43 | çıkış kodu dosyaya düştü |
| `rehber_uret.py --veri-yok` | 07:00:54 | ≈ 2,5 (elle, sarmalayıcı kaydı dışında) | 0 | 1862 s | 1,59 | aşağıda |
| `F10d-dogrula.py --goruntu-yok` | 07:34:33 | 3,28 | 0 | 522 s | 1,81 | GEÇTİ |
| `F10a-dogrula.py --kanit-yok` | 07:43:28 | 3,19 | 0 | 402 s | 2,10 | GEÇTİ |
| `F9b-dogrula.py` | 07:50:25 | 3,21 | 0 | 6 s | 3,15 | GEÇER, hata 0 |
| `carpisma_kos.py kontrol` | 07:50:40 | 3,21 | 0 | 1 s | 3,13 | 17 dosyanın özetleri kayıtla aynı |
| `regresyon.py --yazma` | 07:50:45 | 3,25 | 0 | 1 s | 3,19 | GEÇER (hepsi okundu, kötüleşen yok; 10 satırın 10'u "aynı") |
| `F10e-dogrula.py` (tam) | 07:50:55 | 3,23 | 0 | 879 s | 1,73 | GEÇTİ; `renk_demo` KALDI (karar, geçme koşulunda değil); kare 19 |
| önce / sonra kareleri (scratchpad `p_d1kare.py`) | 08:07:26 | 3,19 | 0 | 44 s | 2,51 | 24 kare yazıldı |

Hiçbir komut sıfırdan farklı çıkmadı; yeniden koşulan komut yok. Bütün koşu boyunca ölçülen en düşük boş fiziksel bellek **1,59 GB**
(üretim sırasında); en düşük boş commit 8,97 GB (üretim sırasında; F10e 9,91). Bitişte arkada python / Chrome süreci yok
(denetlendi), `FREECAD-KILIT.txt` "boş".

**Üretim (`rehber_uret.py`) özeti (kendi günlüğünden):** tarayıcı kontrolü 50 adım, 50 geçti, konsol hatası 0, her parça tek adımda;
alt adım 50 / 50; yazdırma 100 / 100 kare, piksel denetimi 100 / 100, boş 0, en düşük çizim oranı 0,0606; PDF 69 sayfa (50 adım + 19
devam), en küçük yazı DOM 8,1 / PDF 8,1 pt, 12 632 kB; metin denetimi ASCII 0, zorunlu uyarı eksik 0 / 40; perdelenme alt adımlarda
gerekçesiz gizli 0, gerekçeli istisna 102; ek kontrol sorunlu "-".

**F10d:** kabuk alt adım 42, yeni parça 335, görünmeyen 0, istisna 0, birim içi 39, masa yabancı şema 0, eşik 30 px / 0,20; telefon 360
px taşma 0. **F10a:** seçim 6 / 6, ağsız dış istek 0, konsol 0, kadraj ortanca 0,1733 → 0,4013 taşan 0, küçük görünüm 50 / 50
(masaüstü 50 / 50, 360 px taşma 0), cdn 0, yazdırma kareleri çizili 50 / 50, PDF görüntü 100, boş sayfa yok.

**F10e (tam):** renk veri ↔ CAD 1192 / 1192 (GuiDocument 1031 / 1031); bağlandığı yer çift 201, ölçülen 186, doğru 186, masa tabanı
15; sahnede yeni görülen 1192 / 1192, yanlış 0; bağlandığı yer kabuk alt adım 41 / 41 (yeni parçasız 49.2); işaret beklenen 1188,
işaret 1188 (konum başına; benzersiz 893, §12.6), kabuk 277 / 277, kötü 0; görünürlük (gizle-fark, yeni ölçüm) **açık: 42 alt adım,
yeni 335, görünmeyen 0, gömme 0, istisna 0; koyu: aynı, 0 / 0**; soluk 31.3 p0762 açık 156 / 142, koyu 155 / 142; 34.7 p0440 açık
239 / 314, koyu 233 / 314 (fark pikseli / yalnız pikseli) → geçti; arayüz denetimleri (renk kipi, işaret tuşu, satır seçimi, adres,
kare başlığı) geçti. §12.2'nin scratchpad sayılarıyla aynı.

**Çalışma ağacının tutarlılığı (dosya saatleri, 12.11):** bütün üretim çıktıları 07:00 koşusundan, bütün doğrulama çıktıları onun
ardından.

| çıktı | saat | kaynak |
| --- | --- | --- |
| `rehber/app.js`, `index.html`, `stil.css` | 01:47–01:52 | bu turun kodu (elle), üretimden önce |
| `rehber/veri/rehber-veri.{json,js}` | 07:01 | 07:00 koşusu (G4 metni var, kadraj alanı yok) |
| `planlama/rehber/goruntu/adim-NN.png` (50) | 07:01–07:06 | 07:00 koşusu |
| `planlama/rehber/goruntu/adim-NN-JJ.png` (50), `rehber/goruntu/adim-NN-JJ.png` (50) | 07:06–07:09 | 07:00 koşusu |
| `rehber/goruntu/adim-NN.png` (50) | 07:09–07:11 | 07:00 koşusu |
| `planlama/rehber/goruntu/telefon-360-*.png` (7) | 07:11 | 07:00 koşusu |
| `planlama/rehber/Lale-montaj-rehberi.pdf` | 07:12 | 07:00 koşusu |
| `planlama/rehber/kontrol.json` | 07:31 | 07:00 koşusu |
| `F10d-dogrula.json` / `F10a-dogrula.json` / `F10e-dogrula.json` | 07:43 / 07:50 / 08:05 | bu zincir |
| `F10e-goruntu-*.png` (F10e karesi 19 + d1 24) | 08:04–08:08 | bu zincir |

Böylece 02:04 koşusundan kalan karışık durum (yarısı yeni, yarısı eski kareler; eski PDF ve `kontrol.json`) artık yok.

**PDF önce / sonra (PyMuPDF, boş olmayan metin parçaları):** önce (A'nın PDF'i, 11.11 23:36) 69 sayfa, en küçük yazı 8,1 pt; sonra
(07:12) 69 sayfa, en küçük yazı 8,1 pt (8,1 pt 1226 parça, 8,18 pt 4, 8,46 pt 1; önce de aynı dağılım).

### 12.8 Bakılan kareler ve kabul

**Önce / sonra kareleri:** `planlama/d158/F10e-goruntu-d1-<adres>-<acik|koyu>.png`, 24 dosya: 31.3, 34.3, 34.4, 34.5, 34.6, 34.7,
35.1, 35.2, 35.3, 36.1, 49.3, 49.4, her biri açık + koyu. Sol yarı "önce" = B1'in bu turdan önce çektiği kare (1400 × 900,
`?cekim=1`); sağ yarı "sonra" = 07:00 üretiminden sonraki sayfa, aynı adres ve tema.

Gözle bakılan d1 dosyaları (depodaki hâliyle): **31.3 koyu, 34.3 açık, 34.7 koyu, 49.3 açık.** Gözlem: 31.3 koyu, sonra yarısında
halkaların içi pirinç / altın dolu (önce boş görünüyordu), etiket "sol · y 1350–1590"; 34.3 açık, sonra yarısında bindirme cıvataları
saydam bantların önünde tam renkte, etiket "sağ · y 470–660"; 34.7 koyu, kelepçe cıvataları ve ısıl gömmeler halka içinde renkli,
hoparlör grubu yine saydam bant arkasında (zor, §12.4), etiket "sağ · y 720–1100"; 49.3 açık, sahne önce / sonra aynı, yalnız etiket
"orta-arka · y 810–1010" eklenmiş. Bozulma görülmedi. Öbür 20 d1 dosyasına depodaki hâliyle bakılmadı; aynı adres ve temaların bu turdaki
scratchpad kareleri (yeni kodla, üretimden önce) §12.8'in önceki sürümündeki gibi gözle bakılmıştı (34.5 koyu, 34.7 açık, 34.4 / 34.6,
49.4 açık, 35.1–35.3 ve 36.1 açık + koyu, 34.x koyu).

Anlaşılırlık (kabuk): bu turda 42 alt adımın hepsine bakılmadı. B'nin sayımı (açık 40, zor 2: 31.9, 34.7) bu turda değişen 34.7 için
gözle doğrulandı (zor); öbürleri B'nin hükmü, bu turda yeniden bakılmadı.

**Kabul ölçütleri (bu koşuyla):**

| ölçüt | sonuç |
| --- | --- |
| rehber üretimi 50 / 50 adım + 50 / 50 alt adım, konsol 0 | tuttu |
| renk 1192 ↔ 1192 (veri ↔ CAD ve sahnede) | tuttu |
| bağlandığı yer 41 / 41, doğruluk 186 / 186 | tuttu |
| işaret 1188 / 1188 (konum başına), kötü 0 | tuttu |
| görünürlük iki temada eşik altı 0 (gömme 0), soluk iki parça görünür | tuttu (açık 0 / 0, koyu 0 / 0) |
| anlaşılırlık zor ≤ 2 | tuttu (açık 40, zor 2; B'nin sayımı + 34.7 bu turda) |
| yazdırma boş 0, PDF en küçük yazı ≥ 8 pt | tuttu (boş 0; 8,1 pt; 69 sayfa) |
| F10d / F10a / F9b | GEÇTİ / GEÇTİ / GEÇER |
| çarpışma özetleri, regresyon 10 / 10 | aynı / GEÇER |
| model geometrisi, CAD renkleri, kablolama içeriği | değişmedi (bu tur dokunmadı; çarpışma ve regresyon "aynı") |
| `renk_demo` | KALDI (karar; geçme koşulunda değil, A'dan beri aynı) |
| kablo yolu 12 parçasının rehber paletiyle çizilmesi | değişmedi, P10.7'ye devredildi (§12.6) |
