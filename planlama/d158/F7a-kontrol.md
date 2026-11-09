# F7a kontrolü (P7.1, 3B montaj rehberi 1,58 m): bağımsız kontrol ajanı B, 09.11.2026

**Genel karar: DÜZELTME TURU GEREKİYOR (kısa: 2 seçici satırı + 3 metin satırı + yeniden üretim).**

Kabulün ölçülebilir ölçütlerinin hepsi bağımsız olarak doğrulandı:
- 50 adım (hazırlık + M6'nın 48 satırı + F5);
- model 1192 ↔ rehber 1192, sıra, modül, ad ve kod bire bir aynı;
- B'nin kendi Chrome koşusunda 50/50 adım geçti, konsol hatası 0;
- veri F6a FCStd'lerinden, GLB boyu 1580,0 mm;
- `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0.

Ama iki parça montaj mantığına aykırı adımda görünüyor; ikisi de B'nin "havada parça" taramasında çıktı:
- **O-1.** Kafadaki 625ZZ iç bileziği, eğme çatalından önce E2b'de havada.
- **O-2.** Ana anahtar ASW-A01 gövdesi B5a güç paneli tezgâhında havada. Model onu etek plakasının altına koyuyor.

İkisi de 125 cm seçicilerinden kalma, ama brief seçicilerin 1,58 m modeline göre yeniden yazılmasını istiyordu. Düzeltmeleri küçük. Tarama kaynaklarına dokunulmaz, ama düzeltme bir FreeCAD veri koşusu (~22 s) ister.

Kritik 0, orta 2, düşük 6.

Kısaltmalar: `TF/` = `tasarim/freecad/`, `SPB/` = B'nin klasörü (depo dışı): `C:\Users\Victus\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad\f7a-b`.

B'nin depoya yazdığı tek dosya bu dosya. B FreeCAD koşmadı: parça listesi FCStd içindeki `Document.xml`'den, konumlar `.brp` köşe noktalarından, analiz JSON'larından ve GLB'den alındı. Kilit dosyasına yazılmadı; 16:13'te F6b satırı vardı. Git'e yazılmadı. `git status --porcelain` B'nin koşularından önce ve sonra aynı.

## Madde tablosu

| # | Madde | Kontrol yöntemi | Sonuç | Kanıt |
|---|---|---|---|---|
| 1a | Diff, brief dışı değişiklik | `git diff` 4 `.py` + 3 web dosyası; yeni `rehber_secici.py` satır satır okundu; durum listesindeki her dosyanın değişme saati alındı | **GEÇER.** A'nın değişiklikleri yalnız brief'in izin verdiği alanlarda: `rehber/`, `TF/rehber/`, `planlama/rehber/`, `F7a-*`, kilit. `M6_erisim.py`, `M6_ek.py`, `M6_erisim_sonuc.json`, `m6_yukle.py`, `M6-montaj-sirasi.md` değişmedi (`git status planlama/adim4` boş). Durumdaki öbür değişiklikler başkalarının: F6b alanı (`F4c-dogrula.py`, `F4c-partiler.py`, `Y2b-baski.py`, `baski_*`, `F6b-*`, 16:01–16:11), orkestratör (`dongu-158.md` 16:07; içinde "F7a … B" satırı), K23 / F6a (13 kabuk PNG'si 14:28, `yerlesim-kontrol.json` 03.11). | §Kanıtlar 1 |
| 1b | Tarama kaynakları | `py -3 TF/carpisma_kos.py kontrol`, `py -3 planlama/d158/regresyon.py --yazma` | **GEÇER.** Birincisi rc 0: "izlenen 17 dosyanin ozetleri kayitla ayni". İkincisi rc 0: "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)". Koşulardan önce ve sonra `git status` aynı. | `SPB/regresyon.out` |
| 2a | Parça sayımı (model ↔ rehber) | `SPB/fcstd_parca.py` 7 FCStd'nin `Document.xml`'ini okudu. `m6_yukle` kuralı: `Part::Feature`, `Tur` özelliği var, omuzda `HARIC`. `SPB/eslestir.py` bu listeyi `rehber-veri.json` ile karşılaştırdı. | **GEÇER.** Model 1192: iskelet 59, omuz 73 + 73, kabuk 357, dirsek 57 + 57, kafa 161, taban 355. Tür: Bağlantı 893, Satın 210, Baskı 72, Referans 13, Lazer 3, İmalat 1; A'nınkiyle aynı. Rehber ile karşılaştırma: sıra + modül + kod 1192/1192 aynı, ad (ASCII'ye indirgenmiş) 1192/1192 aynı, çoklu küme farkı 0 / 0, `id` tekil, `a` alanı boş 0. Yani her parçanın tam bir adımı var. | `SPB/model_parca.json` |
| 2b | Hariç tutulan 4 nesne | FCStd XML | **GEÇER.** Omuz dosyasındaki "Omuz traversi (sigma 40x40 agir, 200 mm)" (Satın, kod "Sigma 40x40 agir kanal 10, 200 mm") iskeletteki "Omuz traversi" ile aynı kodlu bir kopya (asıl A3'te). "Govde kabugu yan yuzu (referans)", `Tur = Referans`, kabuğun yerine konmuş bir gösterim (`TF/omuz/omuz_parcalar.py:115`). Sağ + sol = 4. | |
| 2c | Brief 1 listesi tek tek | `SPB/adim_dokum.txt` (adım → model etiketleri) | **GEÇER.** Liste aşağıda §2c. | |
| 2d | Montaj mantığı, erişim | Adım adım okuma. Kabuk dikiş elemanlarının y değerleri `.brp`'den (`SPB/x0_kontrol.py`), taban güç grubu `taban-analiz.json` kutularından. Ek olarak **havada parça taraması** (`SPB/yuzen.py`): her adımda yeni görünen parçanın GLB köşe kutusu, o adımda görünen başka bir parçaya 1,5 mm payla değiyor mu? | **KOŞULLU (O-1, O-2).** Tarama tüm modelde tam 2 parça buldu: E2b'de 625ZZ iç bilezik (kafa), B5a'da ASW-A01 gövdesi. Başka havada parça yok. Dikiş eşikleri doğru: x = 0 dikişi y 328…953 F2, 1021 / 1222 F3, 1255 F4; y1005 F3, y1198 F4; arka kapak bindirmesi y 820…967, üst arka kapak y 1035…1158 F5. B5a eşiği (y > 170) doğru: XL4016 C y 188…211 ve ön şarj kartı panelde, alt kat kartları y 102…146. | O-1, O-2 |
| 3 | Veri tazeliği | `kaynak.cad` ↔ `ls --full-time`; `git log -1 --format=%ci`; `git show --stat a051281`; GLB ayrıştırıldı (`SPB/glb_kontrol.py`) | **GEÇER.** `kaynak.cad`: iskelet / omuz 14:27, kabuk / dirsek 14:28, taban 14:29, kafa 08:54. FCStd değişme saatleriyle dakikası dakikasına aynı (14:27:40 / 14:27:58 / 14:28:08 / 14:28:30 / 14:29:10 / 08:54:37). FCStd'lerin son commit'i a051281 (15:36:49; commit dosyadan sonra, beklenen) ve hepsi temiz: boyutlar commit'tekiyle bayt bayt aynı. GLB: 1192 düğüm (`p0000…p1191`, rehber id'leriyle aynı küme), 288 mesh. Köşe noktalarından kutu (referanslar hariç): **y 0,0…1580,0 (boy 1580,0)**, x ±261,7, z −264,2…268,0. `robot-glb.js` base64 = `robot.glb`; `rehber-veri.js` = `.json`. | §Kanıtlar 3 |
| 4 | Tarayıcı | B'nin kendi koşusu `SPB/tarayici_b.py`: Chrome başsız, ayrı profil `SPB/chrome-profil`, 50 adımda `--dump-dom`. Ayrıca `--enable-logging=stderr` ile Chrome'un konsol satırları sayıldı; bu kanal test sayfasıyla denendi ve `console.error` yakalıyor. Beklenen küme B'nin kendi koduyla veriden üretildi. Görüntüler `SPB/goruntu/b-adim-NN.png`'ye. | **GEÇER.** 50/50 geçti. `data-hata` 0. Chrome konsol satırı 0: 50 adımda hiç konsol çıktısı yok. `data-hazir` 50/50. Her adımda görünen yeni ve alt montaj kümeleri beklenenle aynı (fark 0), mesh eksiği 0. Adım 0'da hedef 1192. Toplam yeni = 1192, birden çok adımda yeni 0, hiç yeni olmayan 0 (`SPB/kontrol-b.json`, 16:15). Depodaki `kontrol.json` (16:02) da 50/50 ve aynı özet. Gözle bakılanlar: 15 görüntü (§4). | §4 |
| 5 | Uygulama düzeltmeleri | `git diff rehber/` | **GEÇER (not D-6).** "M6 tablosu:" → "Bağlantı:" (`app.js:289`). `#m6-uyari`, `SINIF.m6`, `tr.m6` ve `.uyari` kaldırıldı; lejant boşsa `hidden` (`app.js:315`). `not_` "Notlar" kutusunda (`app.js:265-268`; F3 görüntüsünde 6 madde görünüyor). "Erişim notu (M6)" → "Erişim notu". Veride `m6` bayrağı 0 parça, 0 adım. Kalan: D-6. | `SPB/goruntu/b-adim-35.png` |
| 6 | Göğüs ekranı F3'te | Brief iş 3 + kabul; R-gunluk 3; M6 F3 satırı; kaynak satırlarıyla karşılaştırma | **GEÇER (yorum kabul edilebilir).** Kabul "48 + F5 adım (+ hazırlık)" diyor; ayrı adım 51 adım ederdi ve kabulle çelişirdi. M6 F3 satırı zaten "Göğüs bantları + Nextion" (göğüs ekranının yeri). Parçaların hepsi F3'te: ekran, taşıyıcı, çerçeve 2, çerçeve cıvatası 8 + ısıl gömme 8, taşıyıcı M6×18 2 + pul 2 + direk ön kanalı çekiç somunu 2, VESA M4×12 4 + pul 4 = 34 parça. Metindeki sayılar ve sıra notları kaynakla aynı: `TF/lale158/lale158_rapor.py:76-79`, `kablo_yolu_ekran.py:2,6,19` ("Pi HDMI1", 90° fiş), `elektrik.md:26,62,68`. Doğrulanmamış bilgiler işaretli: F3 `not_` 6 madde (sıra, VESA deliği / vida derinliği, K2 12 V çakışması, port yeri, HDMI / USB yolu, K11), F3 metninin son cümlesi, K2 madde 6 "(doğrulanmadı)". Orkestratöre bilgi: R-gunluk 3 "F3'ten sonra ayrı adım" diyordu; A'nın yorumu kararlar bölümüne yazıldı (`R-gunluk.md:110`). | |
| 7 | Commit listesi, ad taraması | A'nın listesi ↔ `git status --porcelain`; takma ad çalışma anında türetildi, yazılmadı | **KOŞULLU.** A'nın listesinde eksik: `planlama/d158/F7a-brief.md` (önceki paketlerin brief'leri commit'li, ör. `F6a-brief.md`). Fazla: `FREECAD-KILIT.txt` (koordinasyon dosyası; şu an F6b satırını taşıyor) commit'e girmemeli. Takma ad 0 (§7). Başka öğrenci ya da danışman soyadı 0; F7a dosyalarında kişi adı hiç yok. | §7 |

### §2c Brief 1 listesindeki parçaların adımı

| Brief parçası | Model etiketi (adet) | Adım |
|---|---|---|
| 8 braket | Govde braketi sağ / sol y400 / y530 / y688 / y1095 (8) + 16 M6×14 + 16 çekiç somun + 8 M5 perçin somun | **C1** (18), 48 parça |
| Etek M3×14 | Civata M3x14 ISO 7380 (Etek braketi … z−105 / 0 / +105) (6); M3 perçin somunlar braketle C0'da | **F1** (33) |
| Gövde uzatma bandı | Govde uzatma bandi 1 / 2 sağ + sol (4) | **F2** (34) |
| H1 / H2 | Etek servis kapagi H1 (sigorta kutusu), H2 (ana sigorta) + 8 kapak cıvatası + 8 ısıl gömme | **F5** (49) |
| Üst arka kapak (hub takozlu) | Ust arka servis kapagi (takoz kapakla tek baskı, `kabuk_parcalar.py:798`) + 7 bindirme + 7 ısıl gömme + USB Hub 4'lü + köpük bant | **F5** (49) |
| Dolgu şeritleri | Etek dolgu seridi ön, arka (2) | **F1** (33) |
| Göğüs çerçevesi, VESA taşıyıcı | yukarıda madde 6 (34 parça) | **F3** (35) |
| Adaptör / saplamalar | Boyun yukseltme adaptoru + Saplama M3x73 DIN 976 (4) + Pul M3 (4) + Somun M3 DIN 985 (4). Kafada çatalla birlikte, mil flanşı ile çatal arasına giriyor (`kafa10_lib.py:10-11`). Modelde VESA adaptörü diye bir parça yok. | **E2c** (27) |
| Omuz göbeği dişi | Ayrı parça değil: `omuz_parcalar.py:212-214` `DURDURUCU` ve `KOK_DOLGU`, `hub.fuse` ile "Omuz gobegi"ne katılmış. Model parça listesinde diş / durdurucu adında nesne yok. | **G0** (37), göbekle |
| QLED kafa parçaları | Yuz ekrani WaveShare 10,1in QLED HDMI + 4 ekran tırnağı + 4 tırnak cıvatası + 4 ısıl gömme (tırnak boss) + 4 köpük bant | **E4** (31) |

## Bulgular

**Kritik: yok.**

### O-1 (orta). Kafadaki 625ZZ iç bileziği E2b'de, eğme çatalından önce havada görünüyor
- **Kanıt.** E2b seçicisi `TF/rehber/rehber_secici.py:138` şöyle: `_ve(_KF, _g("Pan"), _ad("Boyun mili", "ic bilezik", "Mil-horn"))`. "ic bilezik" yalnız 6808'leri değil, Pan grubundaki "625ZZ rulman (ic bilezik)"i de yakalıyor.
- Parçanın yeri (`TF/kafa/kafa-analiz.json`, kafa yereli): y 185…193, z 21…29. Bu, tilt pimi M5 (y 185…193) ve çatal sol duvarı. Boyun mili y 48…96'da.
- Tam modelde değdiği parçalar: eğme çatalı (E2c), pim cıvatası / pul / M5 ısıl gömme (E2), 625ZZ dış bilezik ve kafa iskeleti (E3a). E2b'de hiçbiri yok.
- Görüntü `SPB/goruntu/b-adim-26.png`: halka sol üstte boşlukta duruyor ve kamera kadrajı da bu yüzden yukarı kaçıyor. Parça listesinde "625ZZ rulman (iç bilezik) ×1" var.
- Çelişki: E2 metni "Karşı yanağa 625ZZ ve M5 pimi tak" (M6 E2: "Tilt servosu + 625ZZ + M5 pim"), ama E2 listesinde 625ZZ yok.
- Kaynak: 15.10 verisinde de E2b'deydi (`git show ef5a978:rehber/veri/rehber-veri.json`; `M6_erisim.py:108-109` aynı seçici). A seçiciyi taşırken düzeltmemiş. Omuz (G2 / G3) ve dirsek (H0c) 625ZZ'leri doğru.

### O-2 (orta). Ana anahtar ASW-A01 gövdesi B5a güç paneli tezgâhında, panelle teması yok
- **Kanıt.** `rehber_secici.py:121`'deki ikinci B5a satırı "Ana anahtar ASW"yi yakalıyor.
- Model gövdeyi etek üst plakasının altına, acil stobun aynası olarak koyuyor:
  - `TF/taban/taban_parcalar.py:10` "acil stop / ana anahtar etekle (arayuz)";
  - `:392` "ana anahtar (etek plakasi alti)";
  - `:444` not "oneri: etek ust plakasinin altinda, acil stobun aynasi";
  - `TF/arayuz.py:723` "Ana anahtar govdesi (etek plakasi alti, oneri)".
- Gövde y 216…256'da. Güç paneli ve kartları y 170…224'te, ama gövde x −142…−92 / z −225…−175 kutusunda hiçbirine değmiyor. Tam modelde yalnız "Etek arka sol"a (F1) ve üç kablo şemasına değiyor.
- B5a tezgâhında (yalnız güç paneli görünürken) havada kalıyor.
- A acil stobu bu yüzden F1'e almış (`rehber_secici.py:149`), aynası ana anahtarı almamış.
- Metin de eski: B5a `is_` (M6 tablosundan) "ana anahtar" diyor. `rehber_metin.py:132` kontrolü "… ve ana anahtar panele (M4 + naylon somun)" diyor, ama modelde ana anahtar için M4 yok (B5a'daki 3 M4: röle 1, sigorta kutusu 2).
- 15.10'da da B5a'daydı.

### D-1 (düşük, bilgi). Isıl gömme somunlar cıvatalarının adımında listeleniyor
- M6 tablosu (`M6-montaj-sirasi.md:91`) ve hazırlık adımı "ısıl gömme somunlar baskıdan hemen sonra takılır" diyor.
- Rehberde ise "yeni" olarak cıvatalarıyla birlikte geliyorlar:
  - F5'te arka kapak 7 + üst arka kapak 7. Fiziksel olarak gövde bantlarında (y 820…1158).
  - F5'te H1 / H2 8. A'ya göre etek plakasında.
  - E4'te kafa dikişleri.
- A bunu açıkça karar olarak yazdı (`R-gunluk.md:111-113`, `F7a-gunluk.md:161-163`). Görsel ve sayım açısından tutarlı, ama kullanıcı "bu adımda ısıl gömme takılacak" diye okuyabilir.
- P7.2: parça listesinde "önceden takılı" etiketi ya da adım notu.

### D-2 (düşük). Günlük ifadeleri
- `F7a-gunluk.md:130-131`: "Diğer görüntüler 15:56 koşusundan; son koşuda (16:02) yalnız F5'in kamera alanı değişti." Doğru değil.
  - Depodaki 50 PNG'nin hepsi son koşudan: değişme saatleri 16:00:16…16:02:45.
  - Veri de 16:00'da yeniden üretildi.
  - A'nın gözle baktığı görüntülerin çoğu ise 15:56 koşusundandı.
  - B'nin 16:15 koşusu güncel veride 50/50 verdi; sonuç değişmiyor, yalnız ifade düzeltilmeli.
- `R-gunluk.md:33` "12 görüntüye gözle bakıldı" diyor; `F7a-gunluk.md:126` "16 adım". İkisinden biri düzeltilmeli.

### D-3 (düşük, P7.2'de zaten var). Parça listesi gruplama yanıltıcı
- B'nin görüntülerinde:
  - C0 "Etek braketi sağ z− ×6";
  - B3 "XL4016 servo 6 V B ×3" (çevre + A + B);
  - E2b "6808-2RS alt rulman ×2" (alt + üst);
  - G4 "S1 kaset gövdesi sağ ×4" (gövde + kapak).
- `F7a-gunluk.md:152-153` madde 6 ile aynı sorun.

### D-4 (düşük, P7.2'de zaten var). Kadraj
- E1 (24) çok yakın; parça listesi "0 parça".
- O-1 düzelince E2b kadrajı da düzelir.
- F3 (35) kadrajı göğüs bandını kesmeden gösteriyor, makul.

### D-5 (düşük, bilgi). `rehber_uret.py` çıktı yolları sabit
- `kontrol()` her zaman `planlama/rehber/goruntu/` ve `planlama/rehber/kontrol.json`'a yazıyor (`rehber_uret.py:17`, `:116`).
- Bağımsız kontrol, depoyu değiştirmeden bu betikle yapılamıyor. B kendi sürücüsünü yazdı.
- İleride `--cikti <klasör>` seçeneği eklenebilir.

### D-6 (düşük). Eski M6 atfı
- `rehber/app.js:294`'te boş kontrol listesi metni hâlâ "(M6 erişim notuna bak)" diyor. Başlık artık "Erişim notu".
- "M6 no NN" rozeti (`app.js:261`) M6 tablosundaki sıra numarası; doğru, kalabilir.

## §4 Gözle bakılan görüntüler (B'nin koşusu, `SPB/goruntu/`; A'nınkilerden yalnız 35 ortak)

| Adım | Görünen | Yargı |
|---|---|---|
| 4 B1a | alttan alt plaka, 20 burç, takoz; 22 parça + 24 bağlantı = 46 | doğru, alttan kamera |
| 9 B3 | 2 BTS7960 + 3 XL4016 + akü + 2 kayış; 20 × M3×6 | doğru (XL4016 C artık B5a'da) |
| 11 C0 | 6 etek braketi uzun rayda, M3 perçin somunlar brakette | doğru; ad gruplaması D-3 |
| 14 B6a | elektronik katı tezgâhı, 6 kart + burçlar | doğru |
| 19 D1a | iki omuz yuvası + S1 servo, tezgâhta | doğru |
| 24 E1 | boyun → travers, 6 bağlantı | parçalar doğru, kadraj çok yakın (D-4) |
| 26 E2b | boyun mili + 6808 iç bilezikleri + **havada 625ZZ iç bileziği** | **O-1** |
| 28 E2 | tilt servosu + M5 pim + M5 ısıl gömme | parçalar doğru; 625ZZ eksik (O-1) |
| 30 E3 | kafa alt montajı (tabla, Pi, D24V50F5, SY8205) tilt hornunda | doğru |
| 35 F3 | göğüs bandı + ekran + çerçeve; Notlar kutusu 6 madde | doğru |
| 38 G1 | göbek + tambur alt montajı omuzda | doğru |
| 40 G3 | S2 hornu, kol çatalı, üst kol tüpü | doğru |
| 41 G4 | S1 kaseti iki yanda | doğru; ad gruplaması D-3 |
| 44 H0c | dirsek çatalı tezgâhta | doğru |
| 47 H0f | el, flanş üzerinde | doğru |

## §7 Commit listesi ve ad taraması
- A'nın listesi (`F7a-gunluk.md:167-178`) ile durum karşılaştırıldı. F7a'ya ait bütün değişiklikler listede: 4 `.py` (biri yeni), 3 web dosyası, 4 veri dosyası, `kontrol.json`, 50 PNG (8 değişik + 42 yeni), `R-gunluk.md`, `F7a-gunluk.md`.
  - Eksik: `F7a-brief.md`.
  - Çıkarılmalı: `FREECAD-KILIT.txt`.
  - `TF/rehber/__pycache__/` `.gitignore:1` ile dışarıda.
- **Takma ad.** Ad çalışma anında türetildi: `git show 647cafc^:TF/kafa/kafa_parcalar.py` satır 6 ile `647cafc` sürümü arasında değişen tek kelime. `SPB/ad_tara2.py` bu adı yazmıyor; büyük / küçük harf duyarsız alt dizge araması yapıyor. Sonuçlar:
  - F7a'nın 15 dosyasında 0. `robot.glb` ve `robot-glb.js` base64 çözülmüş hâliyle dahil.
  - 50 PNG'de 0.
  - Diff'in eklenen 184 satırında 0.
  - `git grep -il` (izlenen): yalnız `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `TF/index.html`. Bunlar F6a'da bilinen, kapsam dışı üç dosya.
  - İzlenmeyenlerde de yalnız commit dışı alanlar: `raporlar/`, `tasarim/solidworks/`, `tubitak-2209b/`.
- **Soyad.** F7a dosyalarında kişi adı hiç geçmiyor: "Ahmet" 0, başka ad 0. Ad + büyük harfli kelime kalıbı 0.

## Kanıtlar (komut → çıktı, özet)

```
1  git status --porcelain   → önce = sonra (SPB/status_once.txt)
   değişme saatleri: TF/rehber/* 15:50–15:59, rehber/* 15:52–16:00, kontrol.json 16:02:45, R-gunluk 16:04:45, F7a-gunluk 16:06:34
1b py -3 TF/carpisma_kos.py kontrol        → "carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni."  rc=0
   py -3 planlama/d158/regresyon.py --yazma → "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)"  rc=0
2a SPB/fcstd_parca.py → kabuk 357, taban 355, kafa 161, omuz 73+73, iskelet 59, dirsek 57+57 = 1192; haric 4
   SPB/eslestir.py    → sira+modul+kod esit 1192/1192; ad uyusmayan 0; model-rehber 0, rehber-model 0; a None 0
2d SPB/yuzen.py       → HAVADA adim 12 B5a: Ana anahtar ASW-A01 govdesi;  HAVADA adim 26 E2b: 625ZZ rulman (iç bilezik) [kafa]
3  SPB/glb_kontrol.py → nodes 1192, meshes 288; kose (referans haric) y 0.0 … 1580.0, boy 1580.0
   robot-glb.js base64 == robot.glb: True; rehber-veri.js == json: True
4  SPB/tarayici_b.py  → {'adim': 50, 'gecen': 50, 'konsol_hata': 0, 'parca': 1192, 'simdi_toplam': 1192, 'birden_cok': 0, 'hic': 0}
   Chrome stderr CONSOLE satırı: 50 adımda 0 (kanal test sayfasıyla doğrulandı)
```

## Genel karar

**DÜZELTME TURU GEREKİYOR (kısa).** Sayım, tazelik, tarayıcı, uygulama düzeltmeleri, göğüs ekranı yorumu ve tarama bütünlüğü GEÇER. İki parçanın adımı yanlış (O-1, O-2). Düzeltme seçicide birer satır, metinde birkaç satır ve bir yeniden üretim. Tarama kaynaklarına dokunulmaz.

| # | Madde | Etiket |
|---|---|---|
| 1 | Diff, tarama kaynakları, regresyon | GEÇER |
| 2 | Parça ataması | KOŞULLU (O-1, O-2) |
| 3 | Veri tazeliği, GLB | GEÇER |
| 4 | Tarayıcı | GEÇER |
| 5 | Uygulama düzeltmeleri | GEÇER (D-6) |
| 6 | Göğüs ekranı F3'te | GEÇER |
| 7 | Commit listesi, ad | KOŞULLU (brief eksik, kilit fazla) |

## A için düzeltme listesi (tarama kaynaklarına, `M6_*`'ya ve `M6-montaj-sirasi.md`'ye dokunma)

1. **O-1.** `TF/rehber/rehber_secici.py:138` E2b'de "ic bilezik" yalnız 6808'leri tutsun. Örnek: `_ad("Boyun mili", "6808-2RS alt rulman (ic", "6808-2RS ust rulman (ic", "Mil-horn")`, ya da satıra `_degil(_ad("625ZZ"))` ekle.
   - Beklenen: E2b 8 → 7, E2 13 → 14.
   - E2 metni ("625ZZ ve M5 pimi") değişmez.
2. **O-2.** Ana anahtarı B5a'dan F1'e taşı.
   - `rehber_secici.py:121`'den "Ana anahtar ASW"yi çıkar.
   - `:149` F1 satırı: `_ve(_T, _ad("Acil stop", "Ana anahtar ASW"))`.
   - Beklenen: B5a 40 → 39, F1 61 → 62.
   - Metin (`rehber_metin.py`):
     - B5a `is_`'yi ez: ana anahtarsız; XL4016 C ve ön şarj kartı dahil.
     - `:132` kontroldeki "ve ana anahtar" kalksın.
     - F1 madde 4: "Ana anahtar (ASW-A01) gövdesi etek üst plakasının altına, acil stobun aynası; ölçü ve delik Ø30 tahmini (doğrulanmadı)".
     - K1 madde 1'e "ana anahtar gövdesi F1'de etekle takılır, uçlar bırakılır" notu (acil stopla aynı kural).
3. **Yeniden üret:** `python tasarim/freecad/rehber/rehber_uret.py`. Kilit kuralı geçerli: 16:13'te kilitte F6b satırı vardı, bitmesini bekle.
   - Beklenen: `kontrol.json` 50/50, `her_parca_tek_adimda` true, konsol 0.
   - Görüntülere bak: 12 (B5a), 26 (E2b), 28 (E2), 33 (F1).
   - Sonra `py -3 TF/carpisma_kos.py kontrol` 0 ve `py -3 planlama/d158/regresyon.py --yazma` 0.
4. **Günlük (D-2):**
   - `F7a-gunluk.md:130-131` görüntülerin kaynağını düzelt.
   - `R-gunluk.md:33` "12" ile günlükteki "16"yı eşitle.
   - Commit listesine `planlama/d158/F7a-brief.md` ekle; `FREECAD-KILIT.txt`'yi "commit dışı (koordinasyon)" olarak işaretle.
   - Düzeltme turunu ve yeni sayıları yaz.
5. **İsteğe bağlı (D-6):** `rehber/app.js:294` "(M6 erişim notuna bak)" → "(erişim notuna bak)".
6. D-1, D-3, D-4 P7.2 listesinde kalır; D-1'i P7.2 listesine ekle.

## C için `git add` listesi

**Şimdi commit önerilmez.** Düzeltme turu, burada sayılan üretilmiş dosyaların hepsini yeniden yazar. Aşağıdaki liste düzeltme turundan ve B'nin dar yeniden kontrolünden sonra geçerli: 66 dosya.
```
git add tasarim/freecad/rehber/rehber_secici.py tasarim/freecad/rehber/rehber_veri.py \
  tasarim/freecad/rehber/rehber_metin.py tasarim/freecad/rehber/rehber_uret.py \
  rehber/app.js rehber/index.html rehber/stil.css \
  rehber/veri/rehber-veri.json rehber/veri/rehber-veri.js rehber/veri/robot.glb rehber/veri/robot-glb.js \
  planlama/rehber/kontrol.json planlama/rehber/goruntu/adim-*.png planlama/rehber/R-gunluk.md \
  planlama/d158/F7a-brief.md planlama/d158/F7a-gunluk.md planlama/d158/F7a-kontrol.md
```
Orkestratör O-1 ve O-2'yi P7.2'ye bırakmaya karar verirse aynı liste bugünkü hâliyle de commit edilebilir. Bu durumda iki atama P7.2 listesine yazılmalı.

**Commit'e girmemeli:**
- `planlama/d158/FREECAD-KILIT.txt` (koordinasyon dosyası)
- F6b alanı: `planlama/d158/F4c-dogrula.py`, `F4c-partiler.py`, `planlama/y2/Y2b-baski.py`, `planlama/d158/F6b-*`, `tasarim/freecad/lale158/baski_analiz_ortak.py`, `baski-analiz.json`
- `planlama/dongu-158.md` (orkestratör)
- K23: `tasarim/freecad/kabuk/gorsel/*.png` (13) ve `tasarim/freecad/montaj/yerlesim-kontrol.json`
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/solidworks/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`, `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`

**Commit'ten önce:**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` 0 olmalı.
- Tarama kaynaklarına checkout, reset ya da stash uygulanmamalı (F6a D-7).

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026 16:35–16:40

Kapsam: A'nın düzeltme turu 1 (`F7a-gunluk.md` "Düzeltme turu 1", :189-226). Kısaltmalar yukarıdaki gibi. B'nin bu turdaki çıktıları `SPB/tur1/`, görüntüler `SPB/goruntu/b-adim-{12,13,26,28,33}.png`.

B FreeCAD koşmadı; kilide yazmadı (16:35'te içerik "boş"). Git'e yazmadı. `git status --porcelain` koşulardan önce ve sonra aynı.

## Madde sonuçları

| # | Madde | Etiket | Kanıt |
|---|---|---|---|
| 1 | Diff'ler, kapsam | GEÇER | aşağıda 1 |
| 2 | Parça → adım dökümü, havada parça | GEÇER | aşağıda 2 |
| 3 | Tarayıcı, görüntüler | GEÇER | aşağıda 3 |
| 4 | `kontrol` 0, regresyon 0 | GEÇER | aşağıda 4 |
| 5 | Commit listesi, ad | GEÇER | aşağıda 5 |

**1. Diff'ler.**

Dosya saatleri:
- Bu turda değişen kaynaklar yalnız şunlar: `rehber_secici.py` 16:26:36, `rehber_metin.py` 16:27:06, `rehber/app.js` 16:27:13.
- `rehber_veri.py`, `rehber_uret.py`, `index.html` ve `stil.css` ilk turdaki hâlinde: saatler 15:52–15:59, `git diff --stat` satır sayıları aynı.
- Üretilenler: veri 16:28:01, PNG'ler 16:28:06–16:30:57, `kontrol.json` 16:30:57.
- Günlükler: `R-gunluk.md` 16:32:41, `F7a-gunluk.md` 16:33:18.

`rehber_secici.py` (182 → 184 satır; +2 satır yorum):
- `:111` ilk B5a satırı (Guc_aku, y > 170) + `_degil(_ad("Ana anahtar"))`.
- `:138-139` E2b: `_veya(_ad("Boyun mili", "Mil-horn"), _ve(_ad("6808"), _ad("ic bilezik")))`.
- `:121` ikinci B5a satırından "Ana anahtar ASW" çıktı.
- `:150-151` F1: `_ad("Acil stop", "Ana anahtar ASW")`.
- Başka satır değişmedi.
- A'nın y > 170 notu doğru: gövdenin y'si 216…256, yani ilk satır da onu yakalıyordu.
- Yeni dışlama yalnız adında "Ana anahtar" geçen Guc_aku parçalarını etkiliyor; modelde bu tek parça. Düğme gösterimi Referans, seçiciye girmiyor. Başka bir parçayı itmedi: madde 2'deki döküm farkı tam 2 parça.

`rehber_metin.py` (ilk tura göre farklar):
- B5a: yeni `is_` (ana anahtar yok, F1'e yönlendiriyor) ve kontroldeki ana anahtar çıkarıldı.
- K1 madde 1: "ana anahtara gidecek iki uç bırakılır, F1'de bağlanır".
- F1 madde 4: gövde etek üst plakasının altına; "model yeri öneri, ölçü tahmini zarf; bağlantı elemanı modelde yok, doğrulanmadı".
- Başka fark yok.

`rehber/app.js`: ilk tura göre tek satır, `:294` "(erişim notuna bak)". CRLF korundu (357/357).

**2. Parça → adım, havada parça.**
- `SPB/eslestir.py` yeniden koşuldu: model 1192 ↔ rehber 1192; sıra, modül, kod ve ad 1192/1192; çoklu küme farkı 0 / 0; atanmamış 0.
- B'nin ilk tur dökümüne (`SPB/adim_dokum_ilk.txt`) göre `diff`, tam olarak şu iki taşıma:
  - "625ZZ rulman (ic bilezik)" [kafa]: E2b → E2;
  - "Ana anahtar ASW-A01 govdesi (tahmini zarf)" [taban]: B5a → F1.
- Adım sayıları: B5a 40 → 39, B5 alt montajı 40 → 39, E2b 8 → 7, E2 13 → 14, F1 61 → 62. A'nın tablosuyla aynı.
- Başka hiçbir parçanın adımı değişmedi.
- `SPB/yuzen.py` (havada parça taraması): **0**.
- Veri: `uretim` 16:28; `kaynak.cad` değişmedi (14:27 / 14:27 / 14:28 / 14:28 / 08:54 / 14:29).
- GLB: 1192 düğüm, 288 mesh, köşe kutusu y 0,0…1580,0. `robot-glb.js` = `robot.glb`, `rehber-veri.js` = `.json`.

**3. Tarayıcı.**
- `SPB/tarayici_b.py` 16:36'da: **50/50**. `data-hata` 0, Chrome konsol satırı 0, mesh eksiği 0, fark 0.
- Toplam yeni görünen 1192; birden çok adımda 0; hiç görünmeyen 0.
- Gözle bakılanlar:
  - **12 B5a:** panel, XL4016 C, ön şarj kartı, sigorta kutusu, röle, ana sigorta yuvası; 14 parça + 25 bağlantı = 39. Ana anahtar yok, metin F1'e yönlendiriyor.
  - **26 E2b:** boyun mili + 6808 iç bilezikleri + 4 M3×8; havada halka yok, kadraj mile oturdu.
  - **28 E2:** listede "625ZZ rulman (iç bilezik) ×1". Metin "625ZZ ve M5 pimi" ile tutarlı.
  - **33 F1:** listede "Ana anahtar ASW-A01 govdesi ×1"; madde 4 yeni metin, doğrulanmadı işaretli. Gövde etek altında olduğu için dışarıdan görünmüyor; bu beklenen.

**4. Bütünlük.**
- `py -3 TF/carpisma_kos.py kontrol` → rc 0, "izlenen 17 dosyanin ozetleri kayitla ayni".
- `py -3 planlama/d158/regresyon.py --yazma` → rc 0, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)" (`SPB/tur1/regresyon.out`).

**5. Commit listesi, ad.**
- A'nın listesi (`F7a-gunluk.md:170-184`) artık `F7a-brief.md`'yi içeriyor, `FREECAD-KILIT.txt`'yi "commit dışı" diyor.
- Durumda F7a'ya ait olup listede olmayan dosya yok.
- İlk kontrolden sonra durum listesine giren yeni değişiklikler F6b'nin: `planlama/baski-listesi.md`, `F4c-liste.py`, `F4c-partiler.json/.md`, `planlama/y2/Y2b-baski.json`. F7a'ya sayılmadı.
- Takma ad (çalışma anında türetildi, yazılmadı): F7a'nın 15 dosyası, 50 PNG, diff'in eklenen 194 satırı ve bu dosya: 0. `git grep -il` izlenenlerde yine yalnız kapsam dışı üç dosya.
- Kişi adı ve soyad: F7a dosyalarında 0.
- D-2 kapandı:
  - `F7a-gunluk.md:133-134` görüntü saatleri doğru (16:28:06–16:30:57, B ölçtü);
  - `R-gunluk.md:33` "16 görüntü".

## Bulgular (bu tur)

Yeni bulgu yok. O-1, O-2, D-2 ve D-6 kapandı. D-1, D-3, D-4 ve D-5 bilgi ya da P7.2 olarak kalıyor:
- D-1 ve D-3: `F7a-gunluk.md` "P7.2'ye kalanlar" ve "Açıklar" bölümlerinde var.
- D-4: P7.2 madde 8.
- D-5: araç önerisi.

## Genel karar (düzeltme 1 sonrası)

**GEÇER.** Kabul ölçütlerinin hepsi sağlanıyor:
- 50 adım;
- her model parçası tam bir adımda (1192 ↔ 1192), havada parça 0;
- konsol 0; `kontrol.json` 50/50 (A'nın 16:30 koşusu ve B'nin 16:36 koşusu);
- veri 1,58 m modelinden;
- `kontrol` 0, regresyon 0.

Kritik 0, orta 0 (ikisi de kapandı), açık düşük 4 (bilgi / P7.2).

| # | Madde | Etiket |
|---|---|---|
| 1 | Diff, tarama kaynakları, regresyon | GEÇER |
| 2 | Parça ataması | GEÇER |
| 3 | Veri tazeliği, GLB | GEÇER |
| 4 | Tarayıcı | GEÇER |
| 5 | Uygulama düzeltmeleri | GEÇER |
| 6 | Göğüs ekranı F3'te | GEÇER |
| 7 | Commit listesi, ad | GEÇER |

## C için kesin `git add` listesi (66 dosya)

```
git add tasarim/freecad/rehber/rehber_secici.py tasarim/freecad/rehber/rehber_veri.py \
  tasarim/freecad/rehber/rehber_metin.py tasarim/freecad/rehber/rehber_uret.py \
  rehber/app.js rehber/index.html rehber/stil.css \
  rehber/veri/rehber-veri.json rehber/veri/rehber-veri.js rehber/veri/robot.glb rehber/veri/robot-glb.js \
  planlama/rehber/kontrol.json planlama/rehber/goruntu/adim-*.png planlama/rehber/R-gunluk.md \
  planlama/d158/F7a-brief.md planlama/d158/F7a-gunluk.md planlama/d158/F7a-kontrol.md
```
Sayım: 4 betik + 3 web + 4 veri + `kontrol.json` + 50 PNG + `R-gunluk.md` + 3 F7a belgesi = 66.

**Commit'e girmemeli:**
- `planlama/d158/FREECAD-KILIT.txt` (koordinasyon dosyası)
- F6b alanı (paralel çalışıyor):
  - `planlama/y2/` (`Y2b-baski.py`, `Y2b-baski.json`);
  - `planlama/baski-listesi.md`;
  - `planlama/d158/F4c-*` (`F4c-dogrula.py`, `F4c-liste.py`, `F4c-partiler.py/.json/.md`);
  - `planlama/d158/F6b-*`;
  - `tasarim/freecad/lale158/baski_*` ve `baski-analiz.json`.
- `planlama/dongu-158.md` (orkestratör)
- K23: `tasarim/freecad/kabuk/gorsel/*.png` (13) ve `tasarim/freecad/montaj/yerlesim-kontrol.json`
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/solidworks/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`, `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`
- `tasarim/freecad/rehber/__pycache__/` zaten `.gitignore`'da.

**Commit'ten önce:**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` 0 olmalı.
- Tarama kaynaklarına checkout, reset ya da stash uygulanmamalı (F6a D-7).
- `git add` yalnız yukarıdaki yolları almalı. `git add -A` ya da `git add planlama/` kullanılmamalı; F6b dosyaları aynı klasörlerde.

**Commit mesajı önerisi:**
```
Lale P7.1: 3B montaj rehberi 1,58 m modelinden yeniden üretildi; 50 adım, 1192 parça tek adımda, rehber_secici.py, göğüs ekranı F3 (F7a)
```
