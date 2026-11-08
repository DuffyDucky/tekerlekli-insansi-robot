# F1b brief: gövde tutarlılığı (P1.1, P1.4, P1.5) — 08.11.2026

Plan: `planlama/dongu-158.md` §3 F1. Karar kuyruğu: `planlama/d158/karar-kuyrugu.md`. Regresyon: `py -3 planlama/d158/regresyon.py`
(yalnız normal mod ya da `--yazma`; `--help` ya da tanımsız bayrak KULLANMA, betik onları tanımıyor ve taban çizgisini yeniden yazar).
FreeCAD 1.1 başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py` ("ü"lü yolda freecadcmd doğrudan çöker; başlatıcıyı kullan).
Önceki paket: F1a (kafa) bitti; `planlama/d158/F1a-gunluk.md` ve `F1a-kontrol.md` çakışma taramasını nasıl bölüm bölüm koştuğunu anlatır.

## P1.1 Akü 2,8 → 3,0 kg
Malzeme listesi v4'teki akü (Victron) 3,0 kg; model 2,8 kg ile hesaplıyor. Modeldeki akü kütlesini 3,0 kg yap (kaynak dosya ve
satırını günlüğe yaz; v4 listesinde kütle başka bir sayıysa onu kullan ve kaynağını göster). Kütle merkezi, devrilme
ve ivme/rampa analizlerini yeniden üret.
**Kabul:** rampa yüksüz payı ≥ 1,5 kalır (şu an 1,517). Altına inerse sonucu düzeltmeye çalışma: karar kuyruğuna yeni madde
(seçenekler + sayısal etki + varsayılan) yaz ve P1.4/P1.5'e geç. Toplam kütle, kütle merkezi yüksekliği, devrilme açıları
öncesi/sonrası tablo.
**Not (K23):** `planlama/y2/Y2b-ivme.json` 03.11'den commit'lenmemiş bir ara çıktı (K23 açık). Analiz hattın bu dosyayı yeniden
yazıyorsa yazmasına izin ver (güncel modelden üretilmiş çıktı eski ara çıktıdan iyidir); bunu günlüğe ve K23 maddesine
"P1.1 güncel modelle yeniden üretti" diye not düş. Hattın yazmadığı K23 dosyalarına (`montaj/yerlesim-kontrol.json`,
`kabuk/gorsel/*.png`) bilerek dokunma.

## P1.4 Göğüs kablo tüpleri
F0 kontrolünün bulgusu (`F0-kontrol.md` B2.5, `F0-gunluk.md:107-111`): plandaki "SY8205 249,7 mm³" sayısı eski, bugün 0
(`KY/uygulama-olcum.json`). Sorun şimdi başka yerde: `lale158-kontrol.json kablo_tup_cakisma`: HDMI × göğüs ekranı 897,1;
12 V × göğüs ekranı 617,3; USB dokunmatik × göğüs ekranı 167,6 mm³.
Önce **yeniden ölç**, sonra her birini ayır: (i) şema tüpünün ucu ekranın konnektörüne değiyor (beklenen temas: uç bölgesi
hariç tutulmalı, ölçüm yöntemi düzeltilir, gerekçesi yazılır) mı, (ii) tüp ekran gövdesinin içinden mi geçiyor (gerçek
çakışma: yol yeniden çizilir). Hangisi olduğunu her kablo için kanıtla (kesit görseli ya da uç mesafesi).
**Kabul:** gerçek çakışma 0; uç temasları ayrı bir alanda sayılır ve neden kabul edildiği yazılır; SY8205 × kafa kabloları 0 kalır.

## P1.5 Kabuk günlüğü ve rapor
`kabuk1.log` 16 × "Wire is not closed" uyarısının kaynağını bul ve düzelt (hangi parça/fonksiyon, neden açık tel).
Ek (F1a B): `kabuk_rapor.py` artık var olmayan `ekran_kontrol` anahtarını arıyor (KeyError), bu yüzden `kabuk/rapor.html`
yenilenemiyor ve eski MAX98357A satırını taşıyor. Düzelt ve raporu yeniden üret.
Ek (F1a B koşul 2): `kabuk_parcalar.py:733` yorumunda `72 x 10 kopru` yazıyor, doğrusu `70 x 10 kopru`. **Yalnız**
P1.5 için `kabuk_parcalar.py`'yi başka bir sebeple zaten değiştiriyorsan bu yorumu da düzelt; değiştirmiyorsan dokunma (P6.1'e kalır).
**Kabul:** temiz kabuk koşusunda "Wire is not closed" 0 satır; `kabuk_rapor.py` çıkış 0; `kabuk/rapor.html` 158 ve güncel ses düzeniyle.
Kabuk geometrisi değişmemeli; değişirse kabuk içi ve kabuk × iskelet çakışması 0 kaldığını ölç.

## Çakışma taraması
Değiştirdiğin modüllere bağlı bölümleri (`py -3 carpisma_kos.py kontrol` hangilerinin eskidiğini söyler) **tek tek** yeniden koş,
sonra `birlestir`. **Omuz bölümünü koşma** (~4,8 sa, P2.2/P6'ya ait). Ev pozu çakışması 0 kalmalı; eskimiş bölüm yalnız omuz olmalı.
Her FreeCAD koşusundan önce boş belleğe bak (`Get-CimInstance Win32_OperatingSystem` FreePhysicalMemory); 2 GB'ın altındaysa
başlatma, günlüğe yaz ve bekle/dur. Aynı anda tek FreeCAD süreci. Bellek koşu sırasında tükenirse yeniden başlatma: günlüğe yaz, dur.

## Korunan değerler
Her iş sonunda `regresyon.py` çıkış 0 olmalı (boy 1.580,0 ± 0,05; kafa içi, kabuk içi, kabuk × iskelet, ev pozu çakışmaları 0;
rampa ≥ 1,5; tilt ≥ 3,0; pan ≥ 2,0; mik–hoparlör ≥ 400; SY8205 × kafa kabloları 0). P1.1 rampayı bilerek değiştirir: değer
1,5 üstünde kalırsa "değişti" beklenen sonuçtur, günlüğe yaz; altına inerse karar kuyruğu. Regresyon "değişti" yüzünden
çıkış ≠ 0 verirse tabanı zorla güncelleme; durumu günlüğe yaz, kayıt ajanı karar verir.

## Kurallar
- Commit, push, dosya silme, checkout/reset/stash YOK (kayıt ajanı yapar).
- `tubitak-2209b/`, `kvkk/`, `rapor/`, `kafa-yerlesim/kaynak/` dokunulmaz. Efe'nin kodu (`kod/`) dokunulmaz.
- Kafa dosyalarına (F1a'nın alanı, commit'li) yalnız ölçüm için dokunabilirsin; değiştirme.
- Bu brief'te olmayan iş yapma; fark ettiğin sorunu günlüğe yaz.
- Belgelerde kişi adı gerekiyorsa "Ahmet Yorulmaz"; takma ad yazma (günlük ve kontrol dosyaları dahil, alıntı olarak bile).
- Günlük: `planlama/d158/F1b-gunluk.md` (dokunduğun her dosya, koştuğun her komut, ölçülen sayılar + JSON kaynağı, açıklar).
- Rapor: kayıt ajanı `planlama/d158/F1b-rapor.html`'i yazar; sen günlüğe öncesi/sonrası tablolarını ve görsel yollarını koy.
