# QLED kafa ekranı ve göğüs çerçevesi: tasarım notu

**Durum (04.11.2026, 18:50): kabuk → taban → ana montaj → taban zinciri son modelde temiz bitti.** Commit durumu dal geçmişinde. Açıklar: tarama omuz bölümü ve iskelet/omuz regresyonu QLED sonrası yeniden koşulmadı.

## Koşular

| Adım | Süre | Sonuç |
| --- | --- | --- |
| `kabuk/kabuk_montaj.py` | 4.250,8 s | Traceback 0; geçersiz 0, kabuk içi 0, kabuk × iskelet 0, bölge ihlali 0 |
| `taban/taban_montaj.py` → `montaj/ana_montaj.py` → `taban/taban_montaj.py` | ~80–170 s her biri | Traceback 0; iki kez daha yinelendi (akü 20 Ah, tarama sonrası karşılaştırma) |
| `lale158/qled_gorsel.py`, `lale158_gorsel.py`, `sekil4_gorsel.py` | 17–154 s | PNG'ler `lale158/gorsel/`, gözle bakıldı |
| `lale158/lale158_kontrol.py` | 246–474 s | Boy 1.580,0; ekran çakışması 0; sığmayan 0 |
| `lale158/ikinci_kontrol.py` model / kol / kafa,tilt / catal | 50 s / ~14.000 s uyanık / 1.877 s / 691 s | Traceback 0; kol koşusu 12:25–16:31 arası bilgisayar ~2 sa 06 dk beklemedeydi |
| `carpisma_kos.py` omuz hariç 8 bölüm, tek tek | 17:43–18:33 | Eklem aralığında 0, toplam 364 (aralık dışı) |
| `Y2b-ivme.py`, `Y2b-baski.py` geçici kopya | 112 s | `ikinci/ivme-qled.json`, `ikinci/baski-qled.json`; `planlama/` yenilenmedi |

**`Wire is not closed`:** yeni kabuk logunda 16 satır, 3 Kasım çerçeve öncesi logda da 16 ve aynı yerde. Parçaları yükleyen taban ve ana montaj loglarında 0. Kaynak çerçeve kodu değil, kabuk_montaj baskı analizindeki ofset; düzeltilmedi, göğüs bandı desteksizlik sonucu temkinli okunmalı.

**Eski kalan çıktılar:** `kabuk/gorsel/`, `kafa/rapor.html`, `kabuk/rapor.html`, `taban/rapor.html`, `montaj/rapor.html`, `montaj/yerlesim-kontrol.json`, `OZET.md`, `planlama/y2/Y2b-*.json`. `taban_rapor.py` 20 Ah'a göre düzeltildi, rapor yeniden üretilmedi. `OZET.md` akü süreleri eski (22 / 7,5 / 3 sa).

## Değişen dosyalar (`tasarim/freecad/`)

| Dosya | Değişiklik |
| --- | --- |
| `arayuz.py` | `KAFA_EKRAN_QLED`, `KAFA["ekran"]` ataması, `_KAFA_DENGE`, `kablo_payi`, `GOGUS_EKRAN` çerçeve parametreleri |
| `kafa/kafa_lib.py` | `qled_local()`, `tvs_local()`, `SY8205`, `TVS`, `HUB`, `SES`, `PAM` |
| `kafa/kafa10_lib.py` | Pencere, cam cebi, tırnaklar, kart yerleri, `ZARF` yer ayırma hacimleri; 7" kodu `else` dalında duruyor |
| `kafa/kafa_parcalar.py` | Başlık yorumları, `ZARF` (parça listesi dışında) |
| `kafa/kafa_montaj.py` | `qled` ölçümleri, `fan_yarik` senaryoları, `kafa-zarf.brep` |
| `kafa/kafa_gorsel.py`, `kafa/kafa_rapor.py`, `montaj/moduller.py`, `README.md` | Etiket ve metin |
| `kabuk/kabuk_parcalar.py` | Köşe takozu ve köşe flanşı, parametreli renk/kod |
| `kabuk/kabuk_montaj.py` | `cerceve_on` ve `baski` ölçümleri (JSON anahtarı `gogus_ekrani`) |
| `lale158/kablo_yolu_ekran.py` | `cam_geri` farkı, `kafa_ici_qled()` |
| `lale158/lale158_rapor.py` | QLED metinleri (`rapor.html` üretilmedi) |
| `lale158/qled_gorsel.py` | Yeni, koşulmadı |

Yedekler: `%USERPROFILE%\.robot-cad\yedek-qled-oncesi\` ve `yedek-cerceve-oncesi\`. İkincisi kafa işinin ilk düzenlemesinden sonra alındı; sonraki bir düzenleme hem kafa ölçümlerini hem çerçeveyi içerdiği için iki iş arasındaki ayrım tam değil. Yedekler CRLF, çalışma kopyaları LF; karşılaştırmada `diff --strip-trailing-cr` kullanılmalı.

## Yeni parametreler

- **`KAFA_EKRAN_QLED`:** `cam_t` 0,9, `cam_panel_t` 6,3, `panel_x` (-116,6; 118,4), `panel_y` (-71,59; 71,41), `kart_x` (-54,1; 55,9), `kart_y` (-44,59; 15,41), `kutle_g` 600 (varsayım), `guc_W` 4,5 (varsayım), `kenar` 0, `pencere_pay` 1, `cep_bosluk` 0,25, `cep_duvar` 1,6, `cep_h` 3, `tirnak`, `port`, `fis`. Kaynak URL'leri kodda yorum olarak duruyor.
- **`_KAFA_DENGE`:** dy −13,878, zb −89,893. **`kablo_payi`:** 59 g, eksene göre (30; −5; 15).
- **`GOGUS_EKRAN`:** `cam_geri` 2,0; `cerceve`: `renk="kabuk"`, `kod=None`, `kose=dict(r=14, on_bosluk=0.2, flans_x=(129, 145))`.
- **Geri dönüş:** `cam_geri=0.5`, `renk="siyah"`, `kod="PETG baski (siyah)"`, `kose=None`. Bu geri dönüş koşularak denenmedi.

## Ölçümler (kafa, `kafa_montaj.py` koşusu)

| Ölçüm | Değer |
| --- | --- |
| Baş parça kütlesi / kablo payı dahil | 1.472,3 g / 1.531,3 g |
| Statik tilt momenti (önce 1,314) | 0,08 kg·cm |
| Tilt toplam / pay (önce pay 2,9), stall 9,4 | 2,42 kg·cm / 3,89 |
| Pan momenti / pay | 4,26 kg·cm / 2,2 |
| Geçersiz, çoklu katı, ev pozu çakışması (500 çift) | 0, 0, 0 |
| Bağlantı | 29/29 |
| Tilt serbest aralığı | −15…+15 (ilk çarpma +20/−20) |
| Cam ↔ kabuk iç yan / üst / alt | 9,6 / 35,71 / 20,71 mm |
| Pencere; görünen alanı örtme | 227,64×129,36; 0 mm³, kabuk payı 1,0 mm |
| Ekran ↔ iskelet / kamera / Pi / arka kabuk | 10,2 / 11,296 / 64,393 / 22,521 mm |
| Ekran ↔ Pan (−13 / +13 derece) | 13,93 / 7,55 mm |
| Kafa ↔ pan en küçük (iskelet ↔ çatal) | 1,0 mm |
| HDMI yolu / şerit | 254 / 300 mm |
| Touch, Power yolu / kablo | 180/350, 114/300 mm |

**Safra gerekmiyor:** statik moment 0,08 kg·cm, ağırlık merkezi eksene 0,5 mm.

## Ölçümler (tam model, 04.11.2026)

| Ölçüm | Değer | Kaynak |
| --- | --- | --- |
| Boy (`optimalBoundingBox`, tüm parçalar) | 1.580,0 mm | `ikinci-kontrol.json` model, `lale158-kontrol.json` |
| Parça, grup | 1.168, 22 | `montaj-analiz.json` |
| Kütle / kablo payı dahil | 25.436,9 g / 25.836,9 g; AM y 524,0 | `montaj-analiz.json`, `taban-analiz.json` |
| Ekran × tam model | 0 çakışma, 68 çift; temaslar hacim 0 | `ikinci-kontrol.json` model.ekran |
| Kasa ↔ direk (şart ≥ 20) | 28,27 mm | `kabuk-analiz.json`, model.ekran 28,268 |
| Kasa ↔ göğüs bandı / çerçeve | 5,0 mm / 0,2 mm | `kabuk-analiz.json` |
| Aktif alan ↔ çerçeve payı | 14,175 mm; aktif alana giren parça yok; cam 2,0 mm geride | `kabuk-analiz.json` cerceve_on |
| Takoz, köşe flanşı ↔ boss | Kabuk içi 0 çakışma, 915 çift; flanş ↔ bant temas, hacim 0 (boss'lar bant gövdesinde) | `kabuk-analiz.json`, model.ekran.temas |
| Takoz kalınlığı, R | 1,8 mm, R14 | `kabuk-analiz.json` |
| Çerçeve (2 yarı) | 207,2 × 147 × 10; 31 g filament, 30 g, 0,6 sa; sığar, destek sorunu 0 | `kabuk-analiz.json` baski |
| Taşıyıcı | 106,2 × 100 × 63,4; 113 g, 108 g, 2,4 sa; sığar, destek sorunu 28 (destekli) | `kabuk-analiz.json` baski |
| Baskı toplamı | 69 adet, 7.579–7.636 g, 157,6–158,8 sa; sığmayan 0 | `ikinci/baski-qled.json` |
| Devrilme, ev pozu rampa 5° | ileri 1,85, geri 1,62, yan 2,11 | `taban-analiz.json` |
| Devrilme, yüksüz en kötü rampa | 1,523 | `ikinci/ivme-qled.json` |
| Devrilme, elde 100 g / 500 g en kötü rampa | **1,482 / 1,331, eşik 1,5 altı** | `ikinci/ivme-qled.json` |
| İki kol önde + 0,5 kg, rampa ileri | 1,41 | `taban-analiz.json` |
| Fren 1,8 düz, yüksüz / 100 g / 500 g | 1,751 / 1,717 / 1,590 | `ikinci/ivme-qled.json` |
| Kol tarama | Eklem aralığında 0; aralık dışı 63'er tam poz | `carpisma-sonuc.json` |
| Kol ızgara, sağ / sol | 684 / 684 çakışma, hepsi S2 0–3; S2 4 0,604 mm, S2 5 1,358 mm | `ikinci-kontrol.json` kol |
| Çatal ↔ çerçeve, S2 5 | 19,685 mm | `ikinci-kontrol.json` catal |
| Kafa × kol, tilt ±13, ±15 | 0 çakışma, en küçük 11,046 mm | `ikinci-kontrol.json` kafa |
| Tilt ilk çakışma | −17° ve +18°, pan −90 | `ikinci-kontrol.json` tilt |
| Akü (20 Ah, 256 Wh, %80; tahmini tüketim) | düşük 12,2, orta 5,6, yüksek 2,4 sa; 16,8 / 36,6 / 85,2 W | `taban-analiz.json` aku |

S2 < 5 çakışmaları (üst kol tüpü ↔ S1 kaseti, çatal ↔ M5 cıvata, el ↔ göğüs bandı) gerçek geometri. Sınır yalnız yazılımda; mekanik durdurucu yok. Ana montaj dosyası kolları S2 0'da taşır, Şekil 4 görseli de bu pozdadır.

## Ölçülmeyenler

- Tarama omuz bölümü (17.394 s sürmüştü) QLED ve çerçeve sonrası koşulmadı; `carpisma-sonuc.json` `tek_kosu: false`. Kol + dirsek × kabuk kendi ızgarada ölçüldü; omuz göbeği hareketi × yeni çerçeve ölçülmedi.
- `omuz_regresyon`, `iskelet_regresyon` QLED sonrası koşulmadı (son koşu 03:03).
- `montaj_gorsel.py`, `eklem_dogrulama.py`, modül görselleri ve raporları koşulmadı.
- Geri dönüş parametreleri (`cam_geri=0.5`, siyah çerçeve, `kose=None`) koşularak denenmedi.

## Varsayımlar

- Kafa ekranı kütlesi 600 g ve güç 4,5 W varsayım.
- Toplam kalınlık: üretici STEP'i 14,38 mm, görev 15,03 mm veriyor; zarf 15,03 alındı.
- Fiş ölçüleri (`fis`), ses kartı ve PAM8403 ölçüleri, kütleleri tahmin. Dahili kablo yolları model üzerinden kaba yol.
- Fan debisi (1,0–1,6) tahmin.
- Göğüs aktif alanı kasa merkezinde kabul edildi, kasa köşe yarıçapı doğrulanmadı.

## Fan ve yarık karar notu

| Senaryo | Kapalı | Mevcut yarıklar | 30 mm fan |
| --- | --- | --- | --- |
| Normal, 19,8 W | 49,7 °C | 48,2 °C | 36,9–39,1 °C |
| Yük altında, 22,9 W | 52,8 °C | 50,9 °C | 38,0–40,5 °C |

Öneri: mevcut arka yarıklar kalsın. Fan yeri ayrıldı (30×30×10), parça olarak eklenmedi ve listede yok. Stres testinde tilt servo gövdesi 50 °C'yi geçerse 30 mm egzoz fanı eklenir. Hesapta servonun kendi ısısı, alt bölme ve boyun açıklığı girişi yok; bu yüzden yarıklı sonuç normalde yalnız 1,8 K pay, yükte 0,9 K aşım veriyor. Bu sayılar kesin sınır değil, karşılaştırma içindir.

## Kontrol ajanının bakması gerekenler

1. maddenin sonucu yukarıda (Koşular). 2. madde: kabuk_montaj temiz bitti. 3. madde: çakışma yok, yatağa sığıyor. 4–6 fiziksel deneme ister, 7–8 hâlâ açık.

**Yeni bulgular (04.11):**

- USB dokunmatik şema yolu kafada `SY8205 kafa ekrani 5 V` kartından geçiyor, 249,7 mm³ (`lale158-kontrol.json` kablo_tup_cakisma). Boyun mili 15,1 ve 1,2 mm³, servo yuvası 1,7 mm³ eski tür şema temasları. Yol şeması düzeltilmedi; kart yeri tasarım kararı değil, kablo elle yanından geçirilir, kontrol edilmeli.
- Elde 100 g ile rampa payı 1,482'ye indi (7" modelde 1,521 geçiyordu). Elde yük sınırı Ahmet'in kararı.
- Akü modelde 2,8 kg, malzeme listesi v4'teki Victron 3,0 kg. Devrilme ve kütle 2,8 kg ile; modele işlenmedi.
- `taban_montaj.py` 24 Ah kullanıyordu; malzeme listesi v4 (satır 5) ve K3 kararı 20 Ah. Kapasite, BOM etiketi ve `arayuz` notu düzeltildi. Seçim değişmedi.

**Önceki maddeler:**

1. **`kabuk1.log` içinde 16 satır `<Exception> Wire is not closed.`** var. Kafa logunda yok. Kaynağı belirlenmedi; eski bir kabuk logu olmadığından yeni olup olmadığı bilinmiyor. `Exception while` aramasına **takılmaz**, ayrıca aranmalı. Yarım log: `...\scratchpad\kabuk1.log`
2. `kabuk_parcalar.py` denenmemiş kodla `carpisma.py` ve `moduller.py` içine import edilir. Taramadan önce `kabuk_montaj.py` temiz bitmeli.
3. Köşe flanşı (`flans_x` 129–145) boss'a çarpabilir, flanş çerçeveyi yatak sınırına yaklaştırabilir.
4. Panel dışında cam şeridi yalnız 0,9 mm ve tırnak buraya baskı yapabilir; sıkma riski fiziksel denemeyle kontrol edilmeli.
5. Kalıplı fişler panele değebilir: pay 0,3 mm, fiş ölçüsü tahmin.
6. Ağırlık merkezi x, kablo dahil 2,8 mm (önce 0,74). Kablo payı merkezi tahmin.
7. Eski metinler: `ikinci_ozet.py:142` ve `lale158_rapor.py` içinde "kasa↔çerçeve". `baski-listesi` Beyaz PETG altında VESA taşıyıcı yazıyor, model ve Y2b PETG-CF diyor; dokunulmadı.
8. `kafa_rapor.py` ve `kafa_gorsel.py` eski içerikli (125 cm, StopIteration), koşulmadı. Planlama belgeleri (`elektrik.md`) güncellenmedi.

## Ahmet'e sorular

- MAX98357A modelde kaldı, malzeme listesi PAM8403 ve ses kartı diyor; ikisi de modelde. Hangisi kalacak?
- ReSpeaker kafada olacak mı? Yeri modellenmedi.
- Hub ve ses kartı arka kabuk yan duvarına kondu; servis için bu yer kabul mü?
