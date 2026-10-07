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
| `iskelet/` | Şase çerçevesi + gövde direği + omuz traversi + bağlantılar: `iskelet_parcalar.py`, `iskelet_montaj.py`, `iskelet_gorsel.py`, `iskelet_rapor.py` → `rapor.html` |
| `montaj/` | **Ana montaj** (FreeCAD Assembly): iskelet + sağ omuz + aynalı sol omuz tek dosyada, eklemler, eklem doğrulaması → `robot-montaj.FCStd`, `rapor.html` |
| `carpisma.py` | Modüller arası çakışma: modülleri `arayuz.MODULLER` ile yerleştirir, ev pozunu, hareketli modüllerin tüm tarama pozlarını ve henüz çizilmemiş modüllerin ayrılmış bölgelerini tarar → `carpisma-sonuc.json` |

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
FC_SCRIPT=$R/carpisma.py "$FC" $L                     # modüller arası tarama (~1 dk)
python $R/iskelet/iskelet_rapor.py                     # iskelet/rapor.html

# omuz: montaj + tarama + tork (~40 s), görseller, rapor
FC_SCRIPT=$R/omuz/omuz_montaj.py "$FC" $L
FC_SCRIPT=$R/omuz/omuz_gorsel.py "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecad.exe" $L
python $R/omuz/omuz_rapor.py

# omuz regresyonu: ortak dosyalar (arayuz, ortak_lib, sigma_profil) değişince omuzun aynı kaldığını kanıtlar
FC_SCRIPT=$R/omuz/omuz_regresyon.py REG_ETIKET=sonra "$FC" $L   # omuz/regresyon/once.json ile karşılaştırır -> fark.json
```

PowerShell'de: `$env:FC_SCRIPT="<betik>"; & "$env:LOCALAPPDATA\Programs\FreeCAD 1.1\bin\freecadcmd.exe" C:\Users\Victus\.robot-cad\run_fc.py`

Sıra: `arayuz.py` veya `ortak_lib.py` değişirse → omuz regresyonu → iskelet montajı → `carpisma.py` → ana montaj → raporlar.

## Ana montaj (`montaj/`)

Tüm modüller tek FreeCAD Assembly dosyasında: `robot-montaj.FCStd` (+ `robot-montaj.step`). Modül listesi ve yükleyiciler
`montaj/moduller.py`'de (`SIRA` + `MODUL_YUKLE`); yerleşim yalnız `arayuz.MODULLER`'den okunur, sol omuz şekil aynalanarak
(gerçek aynalı geometri, parça adları "(sol)") kurulur. Eklemler: iskelet zemine sabit, her omuz gövdesi iskelete sabit, her omuzda
öne-arka (S1, −45…135°) ve yana açma (S2, 0…120°) döner eklemi. Eksen ve sınırlar `omuz/omuz-montaj.FCStd`'den okunur.

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
- Yeni modül (kabuk, kafa, taban, dirsek): `arayuz.MODULLER`'e yerleşim, `moduller.py`'ye yükleyici (parçalar, gruplar, bağlantı,
  eklemler, beklenen poz) ve `SIRA`'ya ad. Hareketli modülün beklenen pozu `eklem_dogrulama.py`'de karşılaştırılır.

## Kontroller

| Kontrol | Nerede | Ölçüt |
|---|---|---|
| Parça geçerliliği | her `*_montaj.py` | `isValid()` ve tek katı |
| Modül içi çakışma | her `*_montaj.py` | tüm çiftler, `common().Volume > 0,5 mm³` çakışma |
| Bağlantı oturması | `iskelet_montaj.py` | köşe bağlantı ve kama profile dayalı, çekiç somun dudak altında, cıvata ucu somunu geçip kanal tabanına değmiyor, set vida tabana dayalı |
| Ayrılmış bölgeler | `iskelet_montaj.py`, `carpisma.py` | henüz çizilmemiş modüllerin bölgelerine taşma yok |
| Modüller arası | `carpisma.py` | ev pozu + her hareketli modülün tüm tarama pozları |
| Ana montaj | `montaj/ana_montaj.py`, `montaj/eklem_dogrulama.py` | parça sayısı/kütle/AM = modül toplamı; simülasyonla sürülen eklemlerde çözücü konumu = modül kinematiği |
| Regresyon | `omuz/omuz_regresyon.py` | parça sayısı, hacim, sınır kutusu, kütle, çakışma, tarama, tork birebir |

## Yeni modül eklemek (taban, kabuk, kafa, dirsek)

1. Ölçüleri ve yerleşimi `arayuz.py`'ye yaz (`MODULLER`'e yerel orijin; kendi ayrılmış bölgelerini `BOLGELER`'e).
2. Klasörü `iskelet/` gibi kur: `<modul>_parcalar.py` (import edilebilir, `P` listesi) + `<modul>_montaj.py` (kontroller + kayıt).
   Genel elemanları `ortak_lib.py`'den al; modüle özgü parçalar `<modul>_lib.py`'de kalsın.
3. `carpisma.py` içinde `MODUL_YUKLE`'ye bir yükleyici ekle ve adı `KONTROL` listesine koy. Hareketli modülde
   `hareket` (pozlar + grup yerleşimi) ver; başka modülün parçası olan parçaları `haric` listesine yaz. Modül çizilince
   o modülün `BOLGELER` kutuları otomatik olarak kontrol dışı kalır, yerine gerçek geometrisi taranır.
