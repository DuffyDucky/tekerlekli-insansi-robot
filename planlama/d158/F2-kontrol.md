# F2 kontrolü (P2.1 omuz mekanik durdurucu, P2.2 omuz çakışma taraması): bağımsız kontrol ajanı B, 09.11.2026

**Genel karar: KOŞULLU GEÇER.** Brief'in ölçülebilir kabul ölçütlerinin hepsi bağımsız olarak doğrulandı:
- temas açısı 4,300°
- kol ile kabuk arasında temas yok, en küçük boşluk 0,831 mm
- tek koşu, eskimiş bölüm 0, ev pozunda ve eklem aralığında çakışma 0
- `regresyon.py` çıkış 0
- kapsam, `kod/` ve takma ad temiz

Kritik bulgu yok. Üç orta bulgu, durdurucunun **yük ve dayanım anlatımıyla** ilgili; geometri ve tarama sonuçlarını etkilemiyor:
- "horn ve dişli yük almıyor" iddiası yarım doğru
- emniyet sayıları tek bir varsayım setine bağlı ve kök köşesindeki gerilme yığılmasını içermiyor
- `arayuz.py`'deki eski "−3°'te kabuk teması" tablosu `kod/` tarafına hâlâ akıyor

Koşullar kayıt ve rapor metniyle sınırlı. Kaynak dosyalara dokunulursa tarama eskir, bu yüzden kaynak düzeltmesi bu commit'te yapılmamalı (Koşul 1).

Kısaltmalar: `TF/` = `tasarim/freecad/`, `KY/` = `TF/lale158/kafa-yerlesim/`, `SP/` = A'nın scratchpad klasörü (günlükteki gibi). `SPB/` = B'nin klasörü
`%USERPROFILE%\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad\b-f2` (depo dışı). B depoya yalnız bu dosyayı yazdı.
B FreeCAD'i bir kez kısa ölçüm için tek süreç olarak koştu: `SPB/F2-kontrol-olc.py` → `SPB/F2-kontrol-olc.json`, 52 s, rc 0. Başlangıçta boş bellek 4,76 GB, çalışan FreeCAD süreci yoktu.
HEAD karşılaştırma kopyaları `SPB/HEAD_*.json` ve `SPB/HEAD_omuz_parcalar.py` (`git show HEAD:`). Darbe kontrolü: `SPB/F2-kontrol-darbe.py` → `.json`.

## İddia tablosu

| # | İddia (A) | Kontrol yöntemi | Sonuç | Kaynak |
|---|---|---|---|---|
| 1a | Diş, kol çatalının çapraz kirişini S2 = 4,3002°'de durduruyor | B kendi betiğiyle şunları yükledi: güncel `omuz_parcalar.py` ve HEAD sürümü. Çatal `O.Pr(θ)` ile döndürüldü. İlk temas ikiye bölme ile bulundu (ortak hacim > 0,01 mm³ ya da mesafe ≤ 1e-4). | **GEÇER.** İlk temas 4,3003…4,3004° (A'nın 4,3002'si eşik farkı içinde). Ortak hacim 4,29°'de 0,705, 4,299°'da 0,070, 4,30°'de 0 mm³. Temas noktaları (167,5; −34) ile (167,156; −29,421) arasında, z −8…21: yüz yüze temas, 4,58 × 29 = 133 mm². | `SPB/F2-kontrol-olc.json` `catal`, `ilk_temas_gobek_yeni`, `temas_noktalari_4_3` |
| 1b | S2 5°'te boşluk 0,344 mm | Aynı betik | **GEÇER**: 0,3436 mm. 4,31°'de 0,0049; 4,4°'de 0,0489 (A ile aynı). | ″ |
| 1c | 4,3°'de kol–kabuk teması 0, en küçük boşluk 0,831 mm | `kabuk_parcalar` yüklendi, global koordinatlar omuz yereline taşındı (y − S3). Omuz Kol grubu `Pp(S1)·Pr(S2)` ile, S1 0 / 20 / 90 / 140, S2 4,3 ve 5 | **GEÇER**: çakışma 0. En küçük boşluk S2 4,3°'te 0,8309 mm (S1 20 / 90 / 140; tüp ↔ S1 kaset kapağı sağ), S1 0'da 2,195. S2 5°'te 1,358. 4,3 ile 5° arasındaki eğimden geriye doğru uzatılınca kaset kapağıyla temas ≈ 3,20° çıkıyor, A'nın 3,207'siyle tutarlı. | ″ `kol_x_kabuk` |
| 1d | Durdurucusuz modelde ilk temas S1 tamburuyla 3,65°'te, S1 kaset kapağıyla 3,21°'de. Eski "kabuk −3°" değeri geçersiz | Tambur ikiye bölme ile ölçüldü. Kaset için 1c'ye bakın. | **GEÇER**: tambur 3,6471°. 4,3°'de tambura 0,4002 mm, 5°'te 0,825 mm. "−3°" C1 (14.10) ölçümüne ait. Kaset 15.10'da geldi. Ancak bu eski değer `arayuz.py:178` ve `kod/` dosyasında hâlâ duruyor (B-3). | ″ `catal.*.tambur`, `ilk_temas_tambur` |
| 2 | Yük yolu kiriş → diş → göbek duvarı; horn ve dişli yük almıyor | Rijit kol + sabit mafsal denge denklemi. Rotor eylemsizliği için mertebe hesabı (dişli oranı 373, `taslak-170/kol-analiz/kol_analiz.py:50`). | **KISMEN.** Tork yolu doğru: durdurucu torku dişliden önce karşılıyor, statik stall'da dişli yalnız kendi stall torkunu taşıyor. Ama (a) durdurucu S2 eksenine 30,3 mm uzakta, kolun vurma merkezi 263,6 mm'de. Bu yüzden darbe kuvvetinin %88,5'i S2 mafsalına (üstte horn + servo mili, altta 625ZZ + M5) **radyal** yük olarak gidiyor. (b) Rotorun dişliler üzerinden yansıyan eylemsizliği, J_rotor 0,3…1,0 g·cm² kabulüyle kol eylemsizliğinin %14…47'si. 1,5 rad/s çarpmada dişli stall torkunun 1,4…2,1 katını taşır. Ayrıntı B-1'de. | `SPB/F2-kontrol-darbe.json` `mafsal`, `rotor` |
| 3a | Darbe sayıları: stall 98 N ve emniyet 3,73; yüksüz 1,5 rad/s 2,24; 500 g 1,32; kaçak servo 0,54; S2 30°'den düşme 1,48 | Aynı yöntemle bağımsız yeniden hesap. B'nin kök kesiti FreeCAD'den: y −23,5'te x 161…166,711, t 5,71 mm (A 5,673, y −23'te). | **GEÇER (yöntem içinde).** B: stall 98,4 N, 5,44 MPa, emniyet 3,79. 1,5 rad/s yüksüz 365 N / 2,27; 500 g 619 N / 1,34; kaçak 1532 N / 0,54; 30°'den düşme 556 N / 1,49. Fark ≤ %2, kaynağı t farkı. | `SPB/F2-kontrol-darbe.json`, A: `SP/f2/darbe.json` |
| 3b | Yöntem ve girdiler | Kol kütlesi ve eylemsizliği kontrol edildi: dirsek zinciri 400,5 g, ağırlık merkezi 255,7 mm. m·r² 0,0262, I 0,0286; fark 0,0024, yaklaşık 30 cm'lik gövdenin kendi eylemsizliği, makul. Malzeme `kol_analiz.py:204-214`: Polymaker Fiberon PETG-rCF08 TDS V1.0, XY 59,8 MPa, E 3.710 MPa, K_T 0,85, sürünme 0,45. Katman yönü de kontrol edildi: +X yukarı basılıyor, kökteki eğilme gerilmesi y yönünde, yani katman düzleminde, XY değeri doğru. | **GEÇER, iki çekinceyle**: (1) sonuç kol eğilme rijitliğine (`kth_kol` 1715, taslak-170 modelinden) ve "temas + kiriş + duvar = diş kadar esneklik" tahminine bağlı. Kol esnekliği ihmal edilir ya da diş rijitliği tam alınırsa 1,5 rad/s yüksüz emniyet 1,22…2,57 aralığına yayılıyor. (2) Kökte çekme tarafında keskin iç köşe var, gerilme yığılması hesapta yok. İkisi B-2'de. | `SPB/F2-kontrol-darbe.json` `duyarlilik`; `SPB/F2-kontrol-olc.json` `dis_kesit` |
| 4 | Baskı: diş iç duvarın destek bölgesiyle birleşti, destek 5,2 → 5,7 g; `omuz-baski.json`'daki 4 eğik yüz F2 öncesinde de vardı | `git show HEAD:` `omuz-baski.json` ile alan alan karşılaştırma. Eski ve yeni göbekte FreeCAD ile eğik yüz araması. `git log -S`. | **GEÇER, açıklama B'den.** HEAD'deki `omuz-baski.json` 29.10 12:24 tarihli. C1–C3 (Y3 M6, `87473ae`, 29.10 17:35, ve `872cb9c`) ondan **sonra** geldi, yani "önce" sütunu HEAD geometrisini değil daha eskisini gösteriyor. 4 eğik yüz C3'ün M4 altıgen somun cepleri (x 180/190, y 34,75): normal (∓0,866, ±0,5), 15,9 / 20,8 mm². Eski ve yeni göbekte aynılar, F2 kaynaklı değiller. Yeni 4. destek bölgesi (174,2; 35,3; 29,3 mm²) de C3'ten. Diş bölgesi 270 → 673 mm², 2,76 → 7,27 cm³. Bu, A'nın "birleşti" demesiyle uyumlu. 5,2 → 5,7 g'ın yaklaşık +0,56 g'ı F2'den, yaklaşık −0,15 g'ı Y3'ten. Açık kalan 6 kapanabilir. | `SPB/omuz-baski.HEAD.json`; `SPB/F2-kontrol-olc.json` `egik_yuz_once/sonra` (8 = 8 aynı); `git log -S s2_somun_cep` |
| 5 | Göbek 175,1 → 177,6 g; robot +4,9 g; S1 payı 2,78 → 2,77, S2 2,72 → 2,72; 500 g'da 0,97 | HEAD ile güncel JSON'lar karşılaştırıldı. Eklenen hacim FreeCAD'de ölçüldü. | **GEÇER.** Eklenen 2142,82 mm³, çıkan 0. Kutu x 161…167,5, y −34…−10, z −8…21. Göbek tek katı, geçerli. ×1,27 × 0,9 = 2,45 g/omuz. `kutle.Gobek` 175,1 → 177,6. Montaj 25.715,59 → 25.720,49 g, ağırlık merkezi y 528,457 → 528,593. `tork.sonuc`: S1 10,95 → 10,96 (pay 2,78 → 2,77), S2 11,16 (2,72), 500 g'da 0,97 / 0,97. `kablo` bloğu birebir aynı. Rampa 1,519. BOM'daki 118,5 → 123,4 iki adedin toplamı (61,7 × 2). | `SPB/HEAD_*_omuz-analiz.json`, `…dirsek-analiz.json`, `…montaj-analiz.json`, `…uygulama-ivme.json` |
| 6 | Tarama: `tek_kosu` true (20261109-033441), 9 bölüm; `kontrol` çıkışı 0; ev pozunda çakışma yok, eklem aralığında 0 | B `py -3 TF/carpisma_kos.py kontrol` koştu. JSON HEAD ile karşılaştırıldı. | **GEÇER.** Çıkış 0: "izlenen 17 dosyanin ozetleri kayitla ayni". 9 bölümün hepsi "tamam" ve aynı koşu kimliğini taşıyor. `ev_pozu_cakisma` [], `toplam` 364 ve aralıkta 0, HEAD ile aynı. `ev_pozu_cakisma_s2_0` aynı 4 kayıt. `carpisma-sonuc.json` B'nin koşusundan önce ve sonra bayt bayt aynı (`cmp`). | `TF/carpisma-sonuc.json`; `SPB/carpisma-sonuc.HEAD.json` |
| 7 | `regresyon.py --yazma` çıkış 0, 10 değer aynı (rampa 1,519) | B yalnız `--yazma` ile koştu (07:38:46, taban 07:32:32). | **GEÇER.** Çıkış 0, "GEÇER", 10/10 "aynı". `regresyon.json` ve `regresyon-son-kosu.json` önce ve sonra bayt bayt aynı. | çıktı bu tabloda |
| 8 | Omuz ve iskelet regresyonları "FARK VAR" diyor ama farklar F2 kaynaklı değil | `omuz-analiz.json` HEAD ile anahtar anahtar karşılaştırıldı. Regresyonların HEAD'deki `fark.json` ve `sonra.json`'ları okundu. `UZAMA` ve iskeletin OMUZ kullanımı grep ile tarandı. | **GEÇER.** Omuzda HEAD ile güncel arasında yalnız `statik_s2_0` (+ çatal ↔ göbek 395,8 mm³), `kol_gobek` (yalnız S2 ≤ 0 anahtarları), `tork` (±0,01), `kutle`, `baski` ve `sure_s` farklı. `parca_sayisi` 75, `bosluk` Kol-Gövde 6,29 ve `kol_govde` HEAD'de de aynı. Yani regresyonun 70 → 75, 4,0 → 6,29, 8 → 11 ve 0,394 farkları, 14.10 tarihli referansla F2 öncesi model arasındaki fark. İskelette `Govde diregi` farkı 315 mm, bu `arayuz.UZAMA` (:28) ile aynı. HEAD'deki iskelet `sonra.json` 08.10'dan, uzatma öncesinden kalma. `iskelet/*.py` `OMUZ["durdurucu"]`'yu kullanmıyor. | `SPB/HEAD_*regresyon*.json`; `TF/arayuz.py:28` |
| 9 | Elle değişen dosyalar yalnız `arayuz.py` (OMUZ bloğu) ve `omuz_parcalar.py`; gerisi betik çıktısı | `git status`, `git diff --stat`, dosya zaman damgaları | **GEÇER.** 49 M dosyası var. Bunların 13'ü PNG, ayrıca `yerlesim-kontrol.json` (03.11 21:23–21:35) ve `dongu-158.md`. Kalan 34 dosya A'nın listesiyle birebir aynı. Zaman damgaları 02:38–07:32 arasında, koşu sırasıyla tutarlı. `arayuz.py` farkı +6 satır, hepsi OMUZ bloğunda (`durdurucu` ve yorumu). `omuz_parcalar.py` farkı +13 / −1 satır, yalnız diş bölümünde. STL'lerden yalnız `omuz-gobegi.stl` değişti. `kod/` değişmedi (`git status kod` boş). Eklenen satırlarda takma ad 0, başka öğrenci ya da danışman soyadı 0. `arayuz.py` farkının bağlam satırında takma ad geçiyor (`arayuz.py:186`), ama bu satır HEAD'den kalma ve A eklemedi. `F2-gunluk.md` ve `F2-brief.md`'de takma ad 0. Günlükte `kod/` sahibinin yalnız adı geçiyor (`F2-gunluk.md:181,192,301`; soyad değil, F0-kontrol uygulamasıyla aynı). | `git diff`, `date -r` |
| 9b | F2 dışı oldukları söylenen dosyalar | Zaman damgası ve diff içeriği | **GEÇER.** 13 kabuk PNG'si ve `yerlesim-kontrol.json` 03.11 tarihli, K23 kapsamında. `dongu-158.md`'nin 07:34:53 tarihli farkı orkestratörün satırlarından oluşuyor: F2 tablo satırı, F2 ve F8a günlük satırları, P8.1 durumu. A bu dosyaya yazmadı (A'nın son çıktısı 07:32:32). Eklenen satırlarda takma ad yok. | ″ |
| 10 | Brief'e uyum: S1 için yalnız ölçüm ve karar taslağı var, `kabuk_parcalar.py:733`'e dokunulmamış, görseller iddiayı gösteriyor | diff; görseller açıldı | **GEÇER.** S1 için tasarım yok, yalnız ölçüm ve KT-F2-4 var. `TF/kabuk/*.py` değişmedi. `F2-durdurucu-kesit.png` şunları gösteriyor: z 6,5 ve −1,25 kesitlerinde diş, çatal 4,3° / 5° / 0°, tambur ve tüp. Sayılar ölçümle aynı. `F2-durdurucu-yakin.png` temas anını gösteriyor ama kalabalık; başlık eksen etiketlerinin (150 / −30) üstüne biniyor. | iki PNG |

## Bulgular

**Kritik: yok.**

**B-1 (orta). "Horn ve dişli yük almıyor" ifadesi yarım doğru.** Durdurucu torku servodan önce karşılıyor, bu doğru. Ama:
- **Mafsalın radyal yükü.** Rijit kolu sabit bir mafsal etrafında döndürüp R = F·(1 − m·r_am·r_F / I) dengesini kurunca, durdurucu eksene yakın (30,3 mm) ve kolun vurma merkezi uzak (263,6 mm) olduğu için R ≈ 0,885·F çıkıyor. Örnekler:
  - 1,5 rad/s yüksüz çarpmada yaklaşık 320 N
  - 500 g ile yaklaşık 550 N
  - statik stall'da 98 N

  Bu yük üst çatal plakası → M3 cıvatalar → alüminyum horn → 25T mil ile alttaki 625ZZ + M5 pim arasında paylaşılıyor. Kuvvetin z konumuna (z ≈ 6,5) bakılırsa yarısından fazlası servo miline düşüyor.
- **Rotorun yansıyan eylemsizliği.** Oran 373, J_rotor 0,3…1,0 g·cm² (ölçülmedi, küçük coreless motor için tipik aralık) kabulüyle 0,004…0,014 kg·m² ediyor. Bu kol eylemsizliğinin %14…47'si. Servo sürerken çarpmada rotoru durduran tork dişlilerden geçiyor: 1,5 rad/s'de stall torkunun yaklaşık 1,4…2,1 katı.
- A da açık kalan 1'de bunu "aleyhte" diye not etmiş, ama tablo ve yorumlar ters sonucu söylüyor.

**Etki:** iddia 2 ve KT-F2-1'in hız sınırı. Düzeltme Koşul 1'de.

**B-2 (orta). Emniyet sayıları tek bir varsayım setine bağlı ve kök köşesini içermiyor.** A'nın sayıları yöntem içinde doğru (iddia 3a), ama iki konu var:
- **Rijitlik varsayımı.** Kol eğilmesi seri yay olarak alınıyor (taslak-170'ten 1715 N·m/rad). Ayrıca "temas + kiriş + duvar = diş kadar esneklik" diye bir tahmin var. Diş tam rijitlikte alınıp kol esnekliği çıkarılırsa 1,5 rad/s yüksüz emniyet 1,22'ye düşüyor. Bu varsayımlarla yayılım şöyle:

  | Durum | Emniyet aralığı |
  |---|---|
  | 1,5 rad/s yüksüz | 1,22…2,57 |
  | 1,5 rad/s, 500 g | 0,67…1,55 |
  | 30°'den düşme | 0,69…1,78 |

- **Kök köşesi.** Çekme tarafında (+x yüzü) dişin eğik yüzü (x 166,7) göbek duvarının alt yüzüne (y −23, x 166,7…168) 90°'lik keskin iç köşeyle bağlanıyor. Bu köşe B'nin kesitinde ve `F2-durdurucu-kesit.png`'de görünüyor. PETG-CF'nin kopma uzaması düşük, darbe ve sürekli stall yüklemesi var. Gerilme yığılması 1,5…2 kat olursa 1,5 rad/s yüksüz emniyet yaklaşık 1,1…1,5 olur. A'nın "≤ 1,5 rad/s yüksüz çarpmayı güvenle karşılar" sonucu bu yüzden sağlam değil.
- **Duyarlılık (bilgi).** Servo yanı sıcaklık katsayısı (K_T 0,75, `kol_analiz.py:212`) alınırsa bütün emniyetler × 0,88 olur. Diş servo gövdesine 7,5 mm uzakta olduğundan 0,85 savunulabilir.

**Öneri:** bir sonraki tasarım paketinde (P6.1 ya da ayrı paket) kökün +x köşesine ≥ 1,5 mm yarıçap ya da pah eklenmeli. Kiriş 4,3°'de y ≈ −29'un altında, köşe y −23'te, arada ≈ 4 mm var. KT-F2-1'in hız sınırı ölçüm gelene kadar daha temkinli olmalı (aşağıda).

**B-3 (orta). Eski "kabuk teması −3°" tablosu `kod/` dosyasına akıyor.**
- `TF/arayuz.py:178` hâlâ `yana_alt_bosluk_mm={0: 4.7, -2: 0.6, -3: 0.0}` diyor.
- `eklem_sinirlari()` (`arayuz.py:772-774`) bu değeri, "5'te 0,77 mm; kabuk boşluğu 0'da 4,7 mm, −3'te temas" metniyle birlikte `kod/ortak/eklem_sinirlari.json`'a yazıyor (`:20`, `:61`).
- F2 ölçümüne göre bugün durum şu: S1 kaset kapağıyla temas 3,21°, tamburla 3,65°, mekanik durdurucu 4,3°, 5°'te dişe boşluk 0,344 mm.
- Yazılım tarafı "5°'in altında 8° pay var" diye okuyabilir.
- A'nın brief'i `kod/`'a dokunmayı yasaklıyor; bu yüzden kusur değil, ama karar taslaklarında yok. KT-F2-3'e eklenmeli (aşağıda).

**B-4 (düşük). Baskı tablosunun "önce" sütunu eski.** "Önce" sütunu 29.10 12:24 koşusundan; C1–C3 geometrisi ondan sonra geldi (iddia 4). Bu yüzden:
- "Destek bölgesi 3 → 4" F2'den değil.
- 5,2 → 5,7 g'ın yaklaşık 0,56 g'ı F2'den.

A'nın açık kalan 6'sının nedeni bulundu: C3'ün somun cepleri. Rapor metninde bu ayrım verilmeli.

**B-5 (düşük). Tambur ve yazılım sınırı payı dar.** Durdurucu penceresi tambur (3,647°) ile 5° arasında. Diş 4,3°'de, tambura 0,40 mm, 5°'te dişe 0,344 mm boşluk var. Tolerans payı şöyle tüketiliyor:
- Baskı toleransı ±0,2 mm, 30 mm kolda ≈ ±0,38°.
- 500 g ile 1,5 rad/s çarpmada çatal sapması 0,47°. Toplamı 0,85°, tambur payı 0,65°'yi aşabiliyor.
- Servo sıfır hatası > 0,7° olursa kol S2 5'te dişe dayanıp sürekli stall'da kalır (KT-F2-3 bunu söylüyor).

İlk montajda sentil kontrolü (S2 5'te 0,3 mm geçer, 0,4 geçmez) ve gerekirse dişin zımparalanması montaj talimatına girmeli.

**B-6 (düşük). Omuz ve iskelet regresyonlarının referansları eski.** Omuz referansı 14.10'dan, iskeletinki 08.10'dan. Betikler "FARK VAR" dediği sürece bu iki regresyon gerçek bir değişikliği yakalayamaz. Referans yenileme (`REG_ETIKET=once`) ayrı ve küçük bir adım olarak, gerekçesi yazılarak yapılmalı. Karar yürütücüde. Bu paketin kabulünü bloke etmez: F2 kaynaklı fark yok (iddia 8).

**B-7 (düşük, bilgi).** `F2-durdurucu-yakin.png` başlığı eksen etiketlerinin üstüne biniyor. Raporda kesit görseli öne alınmalı.

## Koşullar (C / kayıt ajanı)

1. **Kaynak dosyalara bu commit'te dokunulmamalı.** `arayuz.py` ve `omuz_parcalar.py` çakışma özetinde izleniyor (17 dosya). Yalnız bir yorum değişse bile `carpisma_kos.py kontrol` bütün bölümleri eskimiş gösterir. Bu yüzden iki yorum satırı
   (`TF/omuz/omuz_parcalar.py:167` "servo horn'u ve dislisi yuk yolunda degil", `TF/arayuz.py:179-184` durdurucu yorumu)
   bir sonraki taramalı pakette (P6.1) şu anlamla düzeltilmeli: "tork yolu dişliden önce; S2 mafsalı (horn/servo mili + 625ZZ) darbede kuvvetin ~%88'ini radyal taşır; rotor eylemsizliği dişlide (F2-kontrol B-1)". Plana iş olarak yazılmalı.
2. **`F2-gunluk.md` "Açık kalanlar"ın sonuna kayıt ajanı şu satırları eklemeli** (günlük izlenen kaynak değil):
   `10. B kontrolü (F2-kontrol.md): "horn/dişli yük almıyor" yalnız tork için geçerli; darbede kuvvetin ~%88'i S2 mafsalına radyal gider, rotor eylemsizliği dişliden geçer (B-1). Emniyetler kol esnekliği ve rijitlik varsayımına bağlı (1,5 rad/s yüksüz 1,22…2,57) ve kök +x iç köşesinin gerilme yığılması hesapta yok (B-2): kök yarıçapı/pahı sonraki pakette. Açık kalan 6 kapandı: eğik yüzler C3 somun cepleri; "önce" baskı JSON'u 29.10 C1–C3 öncesi (B-4).`
3. **`F2-rapor.html` metninde** "durdurucu ≤ 1,5 rad/s yüksüz çarpmayı güvenle karşılar" yazılmamalı. Yerine şu yazılmalı: "stall'da emniyet 3,7; 1,5 rad/s yüksüz 2,2 (varsayıma göre 1,2…2,6; kök köşesi hesapta yok)". Baskı satırında da destek artışının F2 payı (≈ +0,56 g) ayrı verilmeli.

## C için: commit listesi

```
git add tasarim/freecad/arayuz.py tasarim/freecad/omuz/omuz_parcalar.py \
  tasarim/freecad/omuz/omuz-analiz.json tasarim/freecad/omuz/omuz-baski.json tasarim/freecad/omuz/omuz-montaj.FCStd \
  tasarim/freecad/omuz/omuz-montaj.step tasarim/freecad/omuz/stl/omuz-gobegi.stl \
  tasarim/freecad/omuz/regresyon/sonra.json tasarim/freecad/omuz/regresyon/fark.json \
  tasarim/freecad/dirsek/dirsek-analiz.json tasarim/freecad/dirsek/dirsek-montaj.FCStd tasarim/freecad/dirsek/dirsek-montaj.step \
  tasarim/freecad/taban/taban-analiz.json tasarim/freecad/taban/taban-montaj.FCStd tasarim/freecad/taban/taban-montaj.step \
  tasarim/freecad/montaj/montaj-analiz.json tasarim/freecad/montaj/robot-montaj.FCStd tasarim/freecad/montaj/robot-montaj.step \
  tasarim/freecad/montaj/robot-bom.csv tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json \
  tasarim/freecad/carpisma-bolum/statik.json tasarim/freecad/carpisma-bolum/omuz.json tasarim/freecad/carpisma-bolum/kol_sag.json \
  tasarim/freecad/carpisma-bolum/kol_sol.json tasarim/freecad/carpisma-bolum/kolkol.json tasarim/freecad/carpisma-bolum/kafa_sabit.json \
  tasarim/freecad/carpisma-bolum/kafa_sag.json tasarim/freecad/carpisma-bolum/kafa_sol.json tasarim/freecad/carpisma-bolum/taban.json \
  tasarim/freecad/carpisma-sonuc.json \
  tasarim/freecad/iskelet/regresyon/sonra.json tasarim/freecad/iskelet/regresyon/fark.json \
  planlama/d158/regresyon.json planlama/d158/regresyon-son-kosu.json \
  planlama/d158/F2-brief.md planlama/d158/F2-gunluk.md planlama/d158/F2-durdurucu-yakin.png planlama/d158/F2-durdurucu-kesit.png \
  planlama/d158/F2-kontrol.md
```
- `planlama/dongu-158.md`: orkestratörün dosyası. Eklenen satırlarda takma ad yok. Commit'e girip girmeyeceği C'nin kararı; girerse F8a satırları da birlikte gider.
- **Commit'e girmemeli:**
  - K23: `TF/kabuk/gorsel/*.png` (13 dosya) ve `TF/montaj/yerlesim-kontrol.json`
  - `kvkk/`, `rapor/`, `tubitak-2209b/`, `tasarim/solidworks/`, `KY/kaynak/`
  - `TF/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`
  - `raporlar/` altındaki 4 izlenmeyen dosya
  - `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`
- Commit'ten **önce** `py -3 TF/carpisma_kos.py kontrol` çıkışı 0 olmalı. B'nin koşusu 0 verdi; `arayuz.py` ve `omuz_parcalar.py` B'nin kontrolünden sonra değişmemeli.

**`rapor.html` için öne çıkacak sayılar:**
- **Durdurucusuz ilk temaslar:** S1 tamburu 3,65°, S1 kaset kapağı 3,21°; eski "kabuk −3°" geçersiz.
- **Diş:** temas 4,300° (B: 4,3003), yüz yüze 133 mm².
- **Boşluklar:**
  - S2 5°'te dişe 0,344 mm, tambura 0,825 mm
  - 4,3°'de kol–kabuk en az 0,831 mm, kabuk teması 0
- **Kütle:** göbek +2,45 g (2142,8 mm³), robot +4,9 g; pay değişimi ≤ 0,01; rampa 1,519.
- **Darbe:**

  | Durum | Kuvvet | Emniyet |
  |---|---|---|
  | Stall | 98 N | 3,7 |
  | 1,5 rad/s yüksüz | 364 N | 2,2 (aralık 1,2…2,6) |
  | 1,5 rad/s, 500 g | – | 1,3 |
  | Kaçak servo | – | 0,54 |
  | 30°'den düşme | – | 1,5 |

  Mafsal radyal yükü ≈ 0,88·F.
- **Tarama:** tek koşu 20261109-033441, 9 bölüm, omuz 3 sa 25 dk; ev pozu 0, aralıkta 0, toplam 364; en düşük boş bellek 4,51 GB.
- **Regresyon:** `regresyon.py` 0 ve 10/10 aynı. Omuz ve iskelet regresyonları "FARK VAR" diyor; referanslar eski (14.10 / 08.10), F2 kaynaklı fark yok.

## Karar taslaklarına yorum (karar kuyruğuna önerilen metin; numara C'nin, sıradaki K38…)

**KT-F2-1 (S2 alt bölgede hız sınırı ve kapanma sırası): kabul, sınır daha temkinli.** B-2 yüzünden A'nın "emniyet 2 için 100°/s" sınırı sağlam değil. Önerilen metin:
"K38 · S2 alt bölge hız sınırı: S2 < 20° bölgesinde açısal hız ölçüm gelene kadar ≤ 60°/s (elde yük varsa ≤ 30°/s). Güç kesilmeden önce iki kol S2 ≤ 15°'ye indirilir. Acil durdurmada kolun yüksekten düşebileceği kabul edilir; diş kırılırsa kol tambura ve kaset kapağına (3,65° / 3,21°) dayanır. Sahibi `kod/`; CAD değişmez. Gerekçe: F2-gunluk darbe tablosu ve F2-kontrol B-1/B-2."

**KT-F2-2 (daha dayanıklı ya da esnek durdurucu): kabul; önce en ucuz adım.** Seçenekler (a) TPU ped, (b) alt sınırı 8°'ye çıkarmak, (c) alüminyum diş. Bunlardan önce kök yarıçapı ya da pahı (B-2) ve servo geri sürme ölçümü gelmeli. Önerilen metin:
"K39 · Durdurucu güçlendirme: (1) dişin kök +x iç köşesine ≥ 1,5 mm yarıçap/pah (sonraki taramalı pakette, P6.1). (2) Bir DS3235 ile ölçüm: güç kesikken S2 30 / 60 / 90°'den bırakılıp düşme süresi ölçülür. Bu ölçüm geri sürme sürtünmesini ve gerçek darbe enerjisini verir. Mümkünse rotor eylemsizliği de tahmin edilir. (3) Ölçüm emniyet < 1,5 gösterirse (b) S2 alt sınırı 5 → 8° ve TPU ped, ya da (c) metal diş. (b) seçilirse `eklem_sinirlari.json` ve ev pozu değişir."

**KT-F2-3 (S2 sıfır kalibrasyonu durdurucuya göre): kabul, B-3 ve B-5 eklensin.** Önerilen metin:
"K40 · S2 kalibrasyonu ve sınır metni: Horn kol dişe dayalıyken (S2 = 4,3°) takılır. S2 5 komutunda dişle 0,3 mm sentil geçmeli, 0,4 geçmemeli; geçmiyorsa diş yüzü zımparalanır. Aynı adımda `arayuz.OMUZ['yana_alt_bosluk_mm']` ve `eklem_sinirlari()` 'neden' metni F2 ölçümüyle güncellenir (kaset 3,21°, tambur 3,65°, durdurucu 4,3°, 5°'te dişe 0,344 mm). `kod/ortak/eklem_sinirlari.json` sahibi yeniden üretir. `arayuz.py` değiştiği için bu, taramalı bir pakette yapılır."

**KT-F2-4 (S1 kod aralığı 160 ↔ CAD 135): kabul, metin aynı kalabilir.** F5 bulgusuyla tek karar olarak girmeli. Önerilen metin:
"K41 · S1 yazılım aralığı: kod 0…160 → −45…135 (`eklem_sinirlari.json` zaten −45…135). Omuz parçaları hiçbir S1 açısında çarpışmıyor; sınırı yalnız kablo U lopu belirliyor (≈ 140,2°'de kasete sıkışır). S1 için mekanik durdurucu istenirse ayrı tasarım paketi açılır. Sahibi `kod/`."
