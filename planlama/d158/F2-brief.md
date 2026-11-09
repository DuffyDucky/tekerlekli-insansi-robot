# F2 brief: omuz (P2.1 durdurucu, P2.2 omuz taraması) — 09.11.2026

Plan: `planlama/dongu-158.md` §3 F2. Karar kuyruğu: `planlama/d158/karar-kuyrugu.md`. Regresyon: `py -3 planlama/d158/regresyon.py`
(yalnız normal mod ya da `--yazma`; `--help` ya da tanımsız bayrak KULLANMA, betik onları tanımıyor ve tabanı yeniden yazar).
FreeCAD 1.1 başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py` ("ü"lü yolda freecadcmd doğrudan çöker; başlatıcıyı kullan).
Önceki paketler: F1a, F1b (commit'li). Çakışma taramasının bölüm bölüm nasıl koşulduğu: `planlama/d158/F1b-gunluk.md`.
Paralel koşan paketler: F4a (yalnız belgeler: `elektrik.md`, `maliyet.json`, README/OZET; FreeCAD yok) ve F3a kontrolü
(`planlama/d158/F3a-*`). Onların dosyalarına dokunma. **FreeCAD makinesi yalnız sende.**

## P2.1 Omuz mekanik durdurucu
Amaç: S2 (kolu yana açan DS3235) servosu bozulur, gücü kesilir ya da yazılım sınırı aşılırsa kol kabuğa vurmasın. Güncel alt
sınır **S2 +5°** (`tasarim/freecad/arayuz.py:176`, `yana_aralik=(5.0, 120.0)`; 15.10 S1 kablo kaseti; C1 kararındaki +3° eski).
Kabuğa temas −3°'te (`yana_alt_bosluk_mm`, `planlama/adim2/S1-kaset.md`). Durdurucu, kolu kabuktan önce mekanik olarak
durdurmalı: temas açısını seç ve gerekçesini yaz (yazılım sınırı +5° ile kabuk teması −3° arasında; ör. 0…+2°). S1 (öne-arka,
−45…135) için de benzer bir risk var mı bak; varsa yalnız ölç ve günlüğe yaz (tasarım bu pakette değil, karar taslağı).
F5 bulgusu: kod omuz için 160° kullanıyor, CAD 135° (`planlama/d158/servo-10-oneri.md`); durdurucu CAD sınırına göre tasarlanır,
kod farkını günlüğe not et.
Durdurucu yeri (omuz yuvası, S2 flanşı, kabuk iç duvarı …) ve malzeme (PETG-CF baskı) senin tasarımın; servo horn'una ya da
dişliye yük bindirmeyen, darbeyi gövdeye aktaran bir çözüm tercih et. Durdurucuya çarpma anındaki yükü (kol kütlesi ve ataleti, S2
stall torku 30,4 kg·cm) kaba hesapla ve baskı parçasının dayanımını değerlendir.
**Kabul:** durdurucu açısında kol–durdurucu teması var, kol–kabuk 0 (çakışma ölçümüyle); baskı analizi (`omuz_baski.py` yöntemi)
destek sorunu 0 ya da gerekçeli; omuz kütle/tork payları (S1, S2) değişimi tablo; eklem aralığında yeni çakışma 0.

## P2.2 Omuz bölümü çakışma taraması
P2.1 bittikten sonra: `py -3 tasarim/freecad/carpisma_kos.py omuz` (~4,8 sa; QLED + çerçeve + kabuk değişikliklerinden sonra hiç
koşmadı), ardından `birlestir`, sonra `omuz_regresyon.py` ve `iskelet_regresyon` (yerini bul). Uzun koşu Ahmet'in onayıyla
(08.11, K15 kapandı): saat fark etmeksizin koşar.
P2.1 kabuk ya da iskelet kaynak dosyasını değiştirirse diğer bölümler de eskir: `carpisma_kos.py kontrol` ile bak ve eskiyenleri
tek tek yeniden koş (omuz en son, en uzun).
**Kabul:** `carpisma-sonuc.json` `tek_kosu: true` (ya da eşdeğeri: tüm bölümler aynı kaynakla), eskimiş bölüm 0, ev pozu
çakışması 0, eklem aralığında çakışma 0; omuz ve iskelet regresyonları geçer.
Bellek: her FreeCAD koşusundan önce boş bellek (`Get-CimInstance Win32_OperatingSystem` FreePhysicalMemory) ≥ 2 GB olmalı;
koşu sırasında 5 dakikada bir boş belleği günlüğe yaz. Bellek tükenir ya da süreç ölürse **yeniden başlatma**: günlüğe yaz, dur.
Aynı anda tek FreeCAD süreci.

## Korunan değerler
Her iş sonunda `regresyon.py` çıkış 0 (boy 1.580,0 ± 0,05; kafa içi, kabuk içi, kabuk × iskelet, ev pozu çakışmaları 0;
rampa ≥ 1,5 (şimdi 1,519); tilt ≥ 3,0; pan ≥ 2,0; mik–hoparlör ≥ 400; SY8205 × kafa kabloları 0). Durdurucu kütlesi rampayı
değiştirebilir: 1,5 üstündeyse beklenen değişim; altına inerse karar kuyruğu taslağı. Regresyon "değişti" yüzünden ≠ 0 verirse
tabanı zorla güncelleme; günlüğe yaz.

## Kurallar
- Commit, push, dosya silme, checkout/reset/stash YOK (kayıt ajanı yapar).
- `tubitak-2209b/`, `kvkk/`, `rapor/`, `kafa-yerlesim/kaynak/`, Efe'nin kodu `kod/` dokunulmaz (`kod/ortak/eklem_sinirlari.json`
  arayuz.py'den üretiliyorsa ve üretici betik onu yeniden yazıyorsa durma, günlüğe yaz: Efe'nin alanı).
- `karar-kuyrugu.md`'ye yazma; karar taslaklarını `F2-gunluk.md` içinde "karar taslağı" başlığıyla yaz (paralel paketler var).
- Bu brief'te olmayan iş yapma; fark ettiğin sorunu günlüğe yaz. `kabuk_parcalar.py:733` yorumu P6.1'in işi.
- Takma ad yazma (alıntı olarak bile); gerekiyorsa "Ahmet Yorulmaz".
- Günlük: `planlama/d158/F2-gunluk.md` (dokunduğun her dosya, her komut, sayılar + JSON kaynağı, görsel yolları, açıklar).
  Durdurucu için en az iki görsel (yakın plan temas anı, kesit) üret.
