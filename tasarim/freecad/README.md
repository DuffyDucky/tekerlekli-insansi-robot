# FreeCAD modelleri (V3)

Robotun FreeCAD 1.1 modeli modül modül kuruluyor. Her modül kendi klasöründe, Python betikleriyle üretiliyor.
Üretilmiş dosyaları (FCStd, STEP, JSON, görseller, rapor.html) elle düzenleme; betiği değiştirip yeniden çalıştır.
Eski CadQuery modeli `tasarim/cad/robot_cad.py` yalnız ölçü kaynağı olarak okunuyor.

## Klasör düzeni

| Dosya / klasör | Rol |
|---|---|
| `arayuz.py` | **Tek ölçü ve arayüz kaynağı** (saf Python, FreeCAD'siz import edilir): global koordinat, V3 ana ölçüleri (robot_cad satırıyla), sigma profil özellikleri, cıvata/pul/somun/çekiç somun tabloları, köşe bağlantı ölçüleri, modül yerleşimleri (`MODULLER`), ayrılmış bölgeler (`BOLGELER`) |
| `ortak_lib.py` | Ortak parça kütüphanesi: `box/cyl/hexprism`, DIN 912/913/934/985/125, ısıl gömme somun, çekiç somun, rulman, sigma (X/Y/Z), 40×40 geniş köşe bağlantı, iç köşe bağlantı, `yerlestir()` |
| `sigma_profil.py` | 40×40 ağır sigma kesiti (kesit alanı üreticiye göre doğrulandı); doğrudan çalışınca test parçası üretir |
| `omuz/` | Sağ omuz (2 eksen): `omuz_parcalar.py` parçalar + kinematik, `omuz_montaj.py` kontroller + kayıt, `omuz_gorsel.py`, `omuz_rapor.py`, `omuz_regresyon.py` |
| `iskelet/` | Şase çerçevesi + gövde direği + omuz traversi + bağlantılar: `iskelet_parcalar.py`, `iskelet_montaj.py`, `iskelet_gorsel.py`, `iskelet_rapor.py` → `rapor.html`, `iskelet_regresyon.py` |
| `kabuk/` | Gövde kabuğu + taban eteği + Nextion göğüs ekranı + iskelete bağlantı braketleri: `kabuk_lib.py`, `kabuk_parcalar.py`, `kabuk_montaj.py` (kontroller, baskı analizi), `kabuk_gorsel.py`, `kabuk_rapor.py` → `rapor.html` |
| `dirsek/` | Sağ dirsek + ön kol + bilek + el (sol = X aynası): `dirsek_lib.py` (MG996R, horn, baskı analizi), `dirsek_parcalar.py`, `dirsek_montaj.py` (kontroller, dirsek içi tarama, tork, baskı), `dirsek_gorsel.py`, `dirsek_rapor.py` → `rapor.html`, `dirsek-analiz.json`. Arayüz `arayuz.DIRSEK`; modüller arası tarama `carpisma.py` (kol zinciri), ana montajda `dirsek_sag` / `dirsek_sol` |
| `kafa/` | Boyun + pan + tilt + kafa: `kafa_lib.py` (6808-2RS, 7" LCD, Camera Module 3, baskı analizi), `kafa_parcalar.py`, `kafa_montaj.py` (kontroller, pan × tilt tarama, R62 uyumu, tork, baskı), `kafa_gorsel.py`, `kafa_rapor.py` → `rapor.html`, `kafa-analiz.json`. Arayüz `arayuz.KAFA`, `MODULLER['kafa']`; modüller arası tarama `carpisma.py` bölüm 4b, ana montajda `kafa` (pan + tilt) |
| `taban/` | Alt plaka + elektronik katı (ön) + güç paneli (arka) + 4 motorlu tahrik + akü + güç elektroniği + kartlar + sonar + acil stop: `taban_lib.py`, `taban_parcalar.py`, `taban_montaj.py` (kontroller, iskelet/kabuk statik tarama, devrilme/motor/akü hesabı, DXF, baskı) → `taban-analiz.json`, `dxf/`; `taban_gorsel.py`, `taban_rapor.py` → `rapor.html`. Arayüz `arayuz.TABAN`, `MODULLER['taban']`; modüller arası tarama `carpisma.py` bölüm 4c, ana montajda `taban` (4 teker eklemi) |
| `montaj/` | **Ana montaj** (FreeCAD Assembly): iskelet + sağ/sol omuz + kabuk + sağ/sol dirsek + kafa + taban (tam robot) tek dosyada (sol = gerçek aynalı geometri), eklemler, eklem doğrulaması → `robot-montaj.FCStd`, `rapor.html` |
| `carpisma.py` | Modüller arası çakışma: modülleri `arayuz.MODULLER` ile yerleştirir, ev pozunu, hareketli modüllerin tüm tarama pozlarını, kol zincirini (omuz × dirsek × bilek; iki kol birbirine karşı), kafayı (pan × tilt × iki kolun pozları), tabanı (ev pozu, iki kolun tüm pozları, kafa) ve henüz çizilmemiş modüllerin ayrılmış bölgelerini (artık yok) tarar. **Bölümlü:** `CARPISMA_BOLUM` ile bölüm seçilir, her bölüm `carpisma-bolum/<bolum>.json`'a yazar |
| `carpisma_kos.py` | Bölümlü koşu sürücüsü (sistem Python'u): bölümleri sırayla ayrı `freecadcmd` süreçlerinde koşar (bellek her bölümden sonra boşalır), sonunda birleştirir → `carpisma-sonuc.json` (`bolumler`: süre, tepe bellek; `birlestirme_notu`, `tek_kosu`) |
| `OZET.md` | Tüm robotun tek sayfalık özeti: modüller, sayılar, kütle/AM, devrilme, motor, akü, yazılım sınırları, açık işler |

Koordinat (global): orijin zemin + robot merkezi, +X robotun sağı, +Y yukarı, +Z ileri (yüz), mm.
Her modülün yerel orijini `arayuz.MODULLER`'de (sağ omuz = travers merkezi (0, 955, 0); sol omuz = sağın X aynası).

## Çalıştırma

`freecadcmd`, yolunda "ü" (Masaüstü) olan betiği doğrudan alınca çöküyor. Betikler ASCII yoldaki başlatıcıyla çalışır
(`C:\Users\Victus\.robot-cad\run_fc.py`, hedef betik `FC_SCRIPT` ortam değişkeninde). Konsol çıktısı ASCII.

```bash
FC="$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe"   # GUI gerektirenler için freecad.exe
R="C:/Users/Victus/OneDrive/Masaüstü/Robot/tasarim/freecad"
L=C:/Users/Victus/.robot-cad/run_fc.py

# iskelet: montaj + kontroller + eğilme + STEP/BOM/JSON (~15 s), görseller (GUI), rapor (sistem Python'u)
FC_SCRIPT=$R/iskelet/iskelet_montaj.py "$FC" $L
FC_SCRIPT=$R/iskelet/iskelet_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/carpisma_kos.py                             # modüller arası tarama: 9 bölüm sırayla, ayrı süreçlerde (~1,5 saat) -> carpisma-sonuc.json
python $R/carpisma_kos.py kafa_sag kafa_sol           # yalnız seçilen bölümler + birleştirme (diğerleri eski dosyalarından; not 'tek_kosu: false')
python $R/carpisma_kos.py birlestir                   # yalnız birleştirme (carpisma-bolum/*.json -> carpisma-sonuc.json)
FC_SCRIPT=$R/carpisma.py CARPISMA_BOLUM=taban "$FC" $L   # tek bölüm elle (statik|omuz|kol_sag|kol_sol|kolkol|kafa_sabit|kafa_sag|kafa_sol|taban;
                                                         # kol, kafa, hepsi kısaltmaları); günlükler %TEMP%/carpisma-<bolum>.log
# CARPISMA_KISA=1: kafa x kol taramasını yasak bölge çevresine daraltan geliştirme testi (carpisma-bolum/<bolum>-kisa.json, birleştirmeye girmez)
python $R/iskelet/iskelet_rapor.py                     # iskelet/rapor.html

# omuz: montaj + tarama + tork (~40 s), görseller, rapor
FC_SCRIPT=$R/omuz/omuz_montaj.py "$FC" $L
FC_SCRIPT=$R/omuz/omuz_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/omuz/omuz_rapor.py

# omuz regresyonu: ortak dosyalar (arayuz, ortak_lib, sigma_profil) değişince omuzun aynı kaldığını kanıtlar
FC_SCRIPT=$R/omuz/omuz_regresyon.py REG_ETIKET=sonra "$FC" $L   # omuz/regresyon/once.json ile karşılaştırır -> fark.json
# iskelet regresyonu (dosya yazmaz, yalnız iskelet_parcalar'ı import eder): değişiklikten önce once, sonra sonra
FC_SCRIPT=$R/iskelet/iskelet_regresyon.py REG_ETIKET=sonra "$FC" $L   # iskelet/regresyon/fark.json

# kabuk: parçalar + kontroller + baskı analizi + STEP/BOM/JSON (~6 dk), görseller (GUI), rapor
FC_SCRIPT=$R/kabuk/kabuk_montaj.py "$FC" $L
FC_SCRIPT=$R/kabuk/kabuk_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/kabuk/kabuk_rapor.py                 # carpisma.py ve ana montajdan sonra (onların sonuçlarını da okur)
# dirsek: montaj + kontroller + tarama + tork + baski (~30 s), gorseller (GUI), rapor
FC_SCRIPT=$R/dirsek/dirsek_montaj.py "$FC" $L
FC_SCRIPT=$R/dirsek/dirsek_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/dirsek/dirsek_rapor.py
# kafa: montaj + kontroller + pan x tilt tarama + tork + baski (~2 dk), gorseller (GUI), rapor
FC_SCRIPT=$R/kafa/kafa_montaj.py "$FC" $L
FC_SCRIPT=$R/kafa/kafa_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/kafa/kafa_rapor.py
# taban: parcalar + kontroller + iskelet/kabuk statik tarama + hesaplar + DXF + baski (~2 dk), gorseller (GUI), rapor
FC_SCRIPT=$R/taban/taban_montaj.py "$FC" $L
FC_SCRIPT=$R/taban/taban_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/taban/taban_rapor.py
```

Not: `omuz_regresyon.py` `omuz_montaj.py`'yi çalıştırıp omuz çıktılarını yeniden yazar (FCStd GUI durumu kaybolur). Sonuç birebir
aynıysa üretilmiş omuz dosyaları `git checkout` ile geri alınabilir.

PowerShell'de: `$env:FC_SCRIPT="<betik>"; & "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\freecadcmd.exe" C:\Users\Victus\.robot-cad\run_fc.py`

Sıra: `arayuz.py` veya `ortak_lib.py` değişirse → omuz ve iskelet regresyonu → iskelet montajı → kabuk montajı → dirsek montajı → `carpisma.py` →
`carpisma_kos.py` → ana montaj (`ana_montaj.py` + `montaj_gorsel.py` + `montaj_gui_kontrol.py` + `eklem_dogrulama.py`) → görseller → raporlar
(`montaj_rapor.py`, `taban_rapor.py`, `kafa_rapor.py`, `kabuk_rapor.py`, `dirsek_rapor.py`; hepsi `carpisma-sonuc.json` ve montaj çıktılarını okur).

## Ana montaj (`montaj/`)

Tüm modüller tek FreeCAD Assembly dosyasında: `robot-montaj.FCStd` (+ `robot-montaj.step`). Modül listesi ve yükleyiciler
`montaj/moduller.py`'de (`SIRA` + `MODUL_YUKLE`); yerleşim yalnız `arayuz.MODULLER`'den okunur, sol omuz şekil aynalanarak
(gerçek aynalı geometri, parça adları "(sol)") kurulur; sol dirsek de aynı yolla. Eklemler: iskelet zemine sabit, her omuz gövdesi ve kabuk iskelete sabit, her omuzda
öne-arka (S1, −45…135°) ve yana açma (S2, 0…120°) döner eklemi. Her dirsek çatalı omuzun Kol grubuna sabit
(üst kol tüpü ucu), her kolda dirsek (0…105°) ve bilek (−90…90°) döner eklemi; eksen ve sınırlar `dirsek/dirsek-montaj.FCStd`'den okunup
`arayuz.DIRSEK` ile karşılaştırılır. Kafanın sabit boynu (Kafa_Govde) traverse sabit; pan (Kafa_Govde → Kafa_Boyun, −90…90°) ve tilt
(Kafa_Boyun → Kafa_Bas, −25…30°) döner eklemleri `kafa/kafa-montaj.FCStd`'den (etiketle: dosyada pan eklemi "Pan001") okunup `arayuz.KAFA` ile
karşılaştırılır; kablo demeti gösterimi ana montajda yok. Dirsek yükleyicisinde `ust_kol` (zincir: beklenen poz omuz açılarını da alır) ve `analiz` (analiz JSON yolu) var. Eksen ve sınırlar `omuz/omuz-montaj.FCStd`'den okunur.

```bash
M=$R/montaj
FC_SCRIPT=$M/ana_montaj.py "$FC" $L          # montaj + STEP + montaj-analiz.json (parça/kütle/AM modül toplamıyla karşılaştırılır)
FC_SCRIPT=$M/montaj_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L   # eklem görünümleri + Kollari_oynat simülasyonu, dosyayı GUI'den kaydeder; görseller; GIF kareleri %TEMP%/robot-montaj-kare
FC_SCRIPT=$M/montaj_gui_kontrol.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L   # taze açılış: eklem görünür/seçilebilir, fareyle sürükleme -> gui-kontrol.json
FC_SCRIPT=$M/eklem_dogrulama.py "$FC" $L      # eklemleri simülasyonla sürer, omuz kinematiğiyle karşılaştırır -> eklem-dogrulama.json
python $M/montaj_rapor.py                      # GIF + montaj/rapor.html
```

- `ana_montaj.py` tek başına çalışırsa dosyada eklem görünüm nesneleri olmaz; ardından `montaj_gorsel.py` şart.
- FreeCAD 1.1'de eklem sınırları yalnız fareyle sürüklemede uygulanır; simülasyon ve `solve()` sınır dışı açıyı kabul eder.
- Ana montajda bir parçanın şekli kendi Placement'ını taşıyabilir (kafa parçaları): dosyadan AM hesabında yalnız üst grubun yerleşimi uygulanır.
- Taban: gövde grubu (`Taban_Govde`) uzun raya sabit; 4 teker grubu (`Taban_OnSagTeker` …: teker + kaplin + M4 eksenel vida + pul)
  gövdeye **sınırsız** döner eklemle (`Taban_TekerOnSag` …; eksen motor mili +X, teker merkezi x ±178, y 62,5, z ±185; pozitif = ileri
  yuvarlanma). `taban-montaj.FCStd`'de eklem yok; eksen `taban_parcalar` (X_WH, Z_WH, arayuz.AX) ile `moduller.yukle_taban`'da kurulur.
  Grup adları eklem adlarıyla çakışmamalı (FreeCAD aynı adlı nesneye "001" ekler).
- Yeni modül: `arayuz.MODULLER`'e yerleşim, `moduller.py`'ye yükleyici (parçalar, gruplar, bağlantı, eklemler (sınır `None` = sınırsız),
  beklenen poz) ve `SIRA`'ya ad. Hareketli modülün beklenen pozu `eklem_dogrulama.py`'de karşılaştırılır.

## Kontroller

| Kontrol | Nerede | Ölçüt |
|---|---|---|
| Parça geçerliliği | her `*_montaj.py` | `isValid()` ve tek katı |
| Modül içi çakışma | her `*_montaj.py` | tüm çiftler, `common().Volume > 0,5 mm³` çakışma |
| Bağlantı oturması | `iskelet_montaj.py` | köşe bağlantı ve kama profile dayalı, çekiç somun dudak altında, cıvata ucu somunu geçip kanal tabanına değmiyor, set vida tabana dayalı |
| Ayrılmış bölgeler | `iskelet_montaj.py`, `carpisma.py` | henüz çizilmemiş modüllerin bölgelerine taşma yok |
| Modüller arası | `carpisma.py` (bölümlü, `carpisma_kos.py`) | ev pozu + her hareketli modülün tüm tarama pozları; kol zinciri (omuz −45…135 / 0…120 × dirsek 0…105 × bilek ±90, kaba 15° + 5 mm altında ince 5°, aralık dışı halka ayrı) iskelet, kabuk, bölgeler, omuz gövde/göbeğine karşı; iki kol birbirine karşı (simetrik, zıt, birlikte öne); kafa (pan −180…165 × tilt −25…40, kaba 15°) sabit modüllere ve iki kolun 1770'er pozuna karşı (sıkı tessellation kutusu ön elemesi, 5 mm altı / çakışma çevresi 5° ince; yasak bölge sınırı çakışan çiftlerin eksen komşularıyla yakınsayana dek); taban: ev pozunda tüm modüllere (çakışma, temas, en küçük boşluk), iki kolun tüm pozlarına (acil stop, sonar, ana anahtar, etek), kafaya (sınır kutusu) |
| Ana montaj | `montaj/ana_montaj.py`, `montaj/eklem_dogrulama.py` | parça sayısı/kütle/AM = modül toplamı; simülasyonla sürülen eklemlerde çözücü konumu = modül kinematiği |
| Regresyon | `omuz/omuz_regresyon.py`, `iskelet/iskelet_regresyon.py` (+ `taban/regresyon/moduller.json`: kabuk/dirsek/kafa çıktıları önceki ve güncel `arayuz.py` ile) | parça sayısı, hacim, sınır kutusu, kütle, AM, çakışma, tarama/tork (omuz), bağlantılar (iskelet) birebir |
| Kabuk bağlantıları | `kabuk/kabuk_montaj.py` | braket profile ve boss'a dayalı, çekiç somun dudak altında, M6 ucu somunu geçip kanal tabanına değmiyor, eksen hizası; M5/M3 kavrama ≥ d ve ≤ ısıl gömme somun deliği, dış yüzeye ≥ 1 mm et; bindirme cıvatası başı dudağa, ısıl gömme somun boss'a oturmuş |
| Baskı | `kabuk/kabuk_montaj.py` | her baskı parçası `arayuz.YAZICI` kullanılabilir hacmine sığar; 45° üstü çıkıntı oranı; 1 mm katmanlarla desteksiz basılabilirlik (2 mm'den dar şerit ve 15 mm'den kısa açıklık serbest) |

## Yeni modül eklemek (taban, kabuk, kafa, dirsek)

1. Ölçüleri ve yerleşimi `arayuz.py`'ye yaz (`MODULLER`'e yerel orijin; kendi ayrılmış bölgelerini `BOLGELER`'e).
2. Klasörü `iskelet/` gibi kur: `<modul>_parcalar.py` (import edilebilir, `P` listesi) + `<modul>_montaj.py` (kontroller + kayıt).
   Genel elemanları `ortak_lib.py`'den al; modüle özgü parçalar `<modul>_lib.py`'de kalsın.
3. `carpisma.py` içinde `MODUL_YUKLE`'ye bir yükleyici ekle ve adı `KONTROL` listesine koy. Hareketli modülde
   `hareket` (pozlar + grup yerleşimi) ver; başka modülün parçası olan parçaları `haric` listesine yaz. Modül çizilince
   o modülün `BOLGELER` kutuları otomatik olarak kontrol dışı kalır, yerine gerçek geometrisi taranır.

## Kabuk modülü (`kabuk/`)

Gövde kabuğu (4 yatay bant × sağ/sol + arka servis kapağı) ve taban eteği (3 bant × sağ/sol): 15 PETG baskı parçası, 3 mm duvar,
Bambu Lab X2D'ye (`arayuz.YAZICI`, kullanılabilir 246 × 246 × 250) sığacak şekilde bölünmüş. Biçim V3 `torso_shell3` / `base_cover3`
ölçüleriyle (`arayuz.GOVDE_KESIT`, `ETEK_KESIT`): yuvarlatılmış dikdörtgen kesitler, omuzda x = 147…152 düz yan duvar ve Ø84 delik
(omuz modülündeki referansla aynı), göğüste 15° eğik ön duvar ve Nextion NX1060P101_011 penceresi (`arayuz.NEXTION`, datasheet).

- **Bölme:** dış ve iç zarfın arasındaki orta zarf duvarı iki yarıya ayırır; iç yarının hücre sınırı dikişten 12 mm kaydırılınca bindirme
  dili oluşur (`kabuk_parcalar.py` baş notu). Dilde damla boss + M3 ısıl gömme somun, dudaktan M3×6 ISO 7380. Yatay plakalarda alın birleşim.
- **İskelete bağlantı:** 4 gövde braketi (3 mm Al U, direk ±X kanalına 2× M6 + çekiç somun, kabuğa M5 + ısıl gömme somun), 6 etek
  braketi (2 mm Al L, uzun ray üst kanalına M6, eteğe M3). Ölçüler `arayuz.KABUK_GOVDE_BRAKET` / `KABUK_ETEK_BRAKET`.
- **Ayrılmış bölgeler:** etek braketleri artık kabuk bölgesi; taban için sonar (3) ve acil stop (gövde, mantar) bölgeleri; Nextion konnektör
  ve kablo boşluğu (kabuk).
- **Baskı yönü** parça başına `kabuk_parcalar.BASKI`; boss'lar ve omuz deliği o yöne göre 45° damla şekilli.
- **Montajda:** `moduller.py`'de `kabuk` (tek grup, direğe sabit eklem); `carpisma.py`'de `KONTROL` listesinde. Tarama çıktısında hedef modül
  başına eklem aralığındaki en küçük boşluk (`modul_bosluk_eklem_araliginda`) ve çakışan pozlar (`modul_cakisan_poz`) var.

## Dirsek modülü (`dirsek/`)

Sağ kol: dirsek çatalı (üst kol tüpüne pim + sıkma bileziği) + ön kol (dirsek ve bilek MG996R) + bilek flanşı + sabit kancalı el; sol kol X aynası.
Ayrıntı ve sonuçlar `dirsek/rapor.html`'de.

- **Kol zinciri taraması** (`carpisma.py` bölüm 4): dirsek parçaları omuzla birlikte sürülür (çatal = Pp·Pr, ön kol ·Pe, el ·Pb). Sınır kutusu
  ön elemesi (köşeleri poz matrisiyle taşınan tutucu kutu, numpy), 5 mm altındaki her aday tam ölçülür, hedef başına en küçük boşluk dal-sınırla;
  5 mm altında kalan alt pozların çevresi 5° adımla yeniden taranır. Kol başına 1755 poz + 279 aralık dışı, iki kol ~10 dk.
- **Sonuç (8 Ekim 2026):** eklem aralığında çakışma 0, yasak poz bölgesi yok; kabuğa en az ~3,8 mm (kol aşağıda, çatal bileziği ↔ göğüs bandı),
  iskelete ~103 mm, iki kol arası ≥ 290 mm. Aralık dışı: yana −10°'de el kabuğa giriyor (omuz yana sınırı 0° engelliyor).
- **Tork kararı:** ana senaryo yüksüz jest (1. dönem kapsamı); mevcut servolar yeterli, 0,5 kg yük bilgi amaçlı, el ucu yükü ~50 g ile sınırlı.

## Kafa modülü (`kafa/`)

Boyun (traverse sabit: boyun plakası, servo yuvası, iki 6808-2RS, pan MG996R) + pan grubu (boyun mili, eğme çatalı, tilt MG996R) + kafa (iskelet,
ön/arka kabuk, 7" LCD, Camera Module 3). Ayrıntı ve sonuçlar `kafa/rapor.html`'de.

- **Modüller arası tarama** (`carpisma.py` bölüm 4b, 8 Ekim 2026): kafa × sabit modüller çakışma 0; en küçük boşluk sabit boyun ↔ kabuk R62 halkası
  8,4 mm, hareketli kafa ↔ iskelet 43 mm, ↔ omuz gövdesi 52 mm, ↔ kabuk 54 mm. Kafa × kollar: ön kola en az 25,7 mm, dirsek çatalına 55 mm, omuza 59 mm.
- **Yasak poz bölgesi (yazılım, 9 Ekim 2026 kesin sınır):** kol öne 125…135°, yana 0°, dirsek 70…105° (el yüzün önünde) iken kafa o kola
  doğru pan 30…55° (sol kolda −55…−30°) ve tilt 25…30° birlikte verilmemeli: el ön yüz kabuğuna giriyor (kol başına 198 yasak el alt pozu,
  603 çakışan poz çifti). Sınır, çakışan her çiftin eksen komşuları 5° (bilek 15°) adımla yeni çakışma kalmayana dek tarandı (8 turda
  yakınsadı); önceki ±5° belirsizlik giderildi (bölge önceki tahminden geniş: öne 125°, dirsek 70°, pan 55° de yasak). Satır satır tablo
  `kafa/rapor.html`'de (`yasak_kural`). Geometri değiştirilmedi.
- **Ana montaj:** 98 parça, 1.366,8 g (robot toplamı aşağıda, `## Taban modülü`). Eklem doğrulaması pan/tilt en büyük sapma
  2·10⁻¹⁰ mm. GUI: tilt kafadan sürükleniyor (30°'de duruyor), pan yalnız boyun milinden ve zor (−14…+3°).

## Taban modülü (`taban/`)

Alt plaka + ön elektronik katı + arka güç paneli + 4 JGB37 tahrik + LiFePO4 akü + güç elektroniği + kartlar + 3 sonar + acil stop: 306 parça
(3 lazer, 4 baskı) + 13 Referans (kablo yolu şemaları, ana anahtar düğmesi gösterimi), 7.508 g. Ayrıntı `taban/rapor.html`.

- **Modüller arası tarama** (`carpisma.py` bölüm 4c, 8 Ekim 2026): ev pozunda taban ↔ tüm modüller çakışma 0 (iskelet 44 temas: plaka/raylar,
  kabuk 1 temas: acil stop bileziği ↔ etek). Kollar × taban (her kol 1755 + 279 aralık dışı + 15 jest pozu, tüm alt pozlar, ana anahtar düğmesi
  ve etek dahil): çakışma 0, en küçük boşluk ~365 mm (el ↔ etek üstü), acil stop mantarına ~367 mm, sonara ~544 mm; kolun en alt noktası
  y ≈ 626 mm, tabanın en üstü y 290 mm. Kafa × taban: kafa en alt y 965 mm, taban en üst 290 mm (675 mm; ölçüm gerekmedi). Taban için yazılım
  sınırı ya da geometri değişikliği gerekmedi.
- **Ana montaj:** tam robot 907 parça, 22 grup, 22 eklem (14 döner: 2 × 4 kol, 2 kafa, 4 teker), **21.260,9 g**, AM (−0,4; 374,6; −13,5) mm.
  Kablo payı 400 g (tahmini, parça listesinde yok) eklenince 21.660,9 g, AM (−0,4; 370,5; −14,4): taban raporunun devrilme hesabıyla aynı
  (fark 0,0 g, 0,03 mm). Teker eklemleri sınırsız; eklem doğrulaması (400°, −720° dahil) en büyük sapma 1·10⁻¹⁰ mm, yön doğru (+90° → alt
  nokta geri = ileri yuvarlanma). GUI: 907/907 parça, 22 eklem görünür ve seçilebilir.
- **Bölümlü tam koşu (8 Ekim 2026, 22:17–23:44, tek koşu):** statik 55 s, omuz 1.733 s, kol sağ/sol 341/332 s, kol-kol 34 s, kafa × sabit 53 s,
  kafa × sağ/sol kol 1.104/1.474 s, taban 104 s; tepe bellek en çok 647 MB (kafa bölümleri), bellek sorunu yok. Eklem aralığında toplam 1.206
  çakışma, hepsi kafa-kol yasak bölgesi (603 + 603 poz çifti); diğer tüm bölümlerde eklem aralığında 0.
- **Regresyon:** `arayuz.py`'ye taban eklendi (yalnız ekleme) → omuz ve iskelet regresyonu fark 0; kabuk/dirsek/kafa parça adları, hacim, sınır
  kutusu ve kütlesi git HEAD arayüzüyle birebir aynı (`taban/regresyon/moduller.json`).
