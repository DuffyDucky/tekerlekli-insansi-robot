# F9b kontrolü (P9.2: demo sayfası 1,58 m sayılarıyla): bağımsız kontrol ajanı B, 09.11.2026

**Genel karar: KOŞULLU GEÇER.** Kabul ölçütleri bağımsız olarak geçti:
- Sayfadaki sayılar kaynak JSON'larla aynı.
- `F9b-dogrula.py` gerçekten denetliyor; sahte geçiş yok.
- Konsol hatası 0. 360 px'te yatay kaydırma yok.
- Model kopyası `robot.glb` ile bayt bayt aynı.
- `demo_uret.py` kopyada sayfayı ve model dosyasını bayt bayt aynı üretiyor.
- Tarama ve regresyon 0.

Commit'ten önce A'nın iki sayfa düzeltmesi yapması gerekiyor (O-1, O-2). C'nin de bir sıralama kuralına uyması gerekiyor (O-3).

Kritik bulgu yok. Üç orta bulgu var:
- **O-1.** Maliyet tablosunda eski kafa ekranı ve Nextion / 7" iddiaları "eski" işareti taşımıyor. Kafa ekranı satırı KPI kartıyla çelişiyor.
- **O-2.** "Satın alınan 210", alım listesindeki 191 adetle uyuşmuyor; fark etiketlenmemiş.
- **O-3.** Model kopyası F7b'nin commit'lenmemiş `rehber-veri.json`'undan üretildi. F9b, F7b'den önce commit'lenirse o commit'te `F9b-dogrula.py` 1 döner.

Düşük bulgular D-1…D-7. Hiçbiri sayfadaki bir sayıyı yanlış yapmıyor.

Kısaltmalar: `SPB/` = B'nin klasörü (depo dışı), scratchpad `f9b-b`. `SPB/kopya/` = depodan alınmış 17 dosyalık kopya (sayfa, üretici, şablon, model, kaynak JSON'lar, GLB, kuyruk, doğrulama betiği). `TPL` = `tasarim/cad/viewer-template.html`.

B'nin depoya yazdığı tek dosya bu dosya. Git yazma, silme ve FreeCAD yok. Üretici ve bozma testleri yalnız `SPB/kopya/` içinde koşuldu. Depoda yalnız okuyan iki betik koşuldu: `carpisma_kos.py kontrol` ve `regresyon.py --yazma`. Koşudan önce ve sonra `git status --porcelain` aynı; `regresyon.json`, `regresyon-son-kosu.json` ve `carpisma-sonuc.json` sha1'i aynı.

## Madde tablosu

| # | Madde | Kontrol yöntemi | Sonuç | Kanıt |
|---|---|---|---|---|
| 1a | `F9b-dogrula.py` gerçekten denetliyor mu | 684 satır okundu. Doğrulama, `SPB/kopya/` içinde değiştirilmemiş sayfayla koşuldu. Ardından 18 bozma testi yapıldı (`SPB/b_bozma.py`). Her testten sonra kopya sayfa geri yüklendi; sha256 ilk hâliyle aynı (`c39a7f76…`). | **GEÇER (not D-1).** Kopyada rc 0 ve A'nın özetiyle aynı: 125 anahtar / 128 eleman, statik 117 bağlı, DOM 1.635 bağlı / 5 muaf / 0 bağsız, 23 adet 1,65 eşleşmesi. Betik kendi ürettiği değerle karşılaştırmıyor. Gömülü tablodan yalnız dosya, yol ve biçimi alıyor; değeri kaynak dosyadan yeniden okuyor (`:219-233`). Gömülü `deger` ve `metin` de kaynakla karşılaştırılıyor. Maliyeti Python'da yeniden hesaplıyor. GLB'yi bayt bayt karşılaştırıyor. **Yakalanan bozmalar:** boy 1.580 → 1.590 (yalnız span; span + gömülü değer birlikte). Düz metinde bağsız "1.590 mm". Karar etiketinin yanında "1.590". Kaynak JSON'da 1590 (sayfa bayat kalınca 6 hata). Kapanmış K16 için "karar bekliyor". Gömülü maliyet fiyatı. Sahte `data-mk` (yalnız tarayıcılı koşuda). "1,65 m" ve "165cm" düz metinde. **Yakalanmayanlar (D-1):** harfe bitişik sayı ("1590mm", "7inç", "6xServo"); `data-ui="eski"` kabı içindeki sayı; `title` özniteliğinde "1.590"; sayı anahtarının başka bir JSON yoluna bağlanması (`boy` → `montaj-analiz.json s3_mm` 1.270 → yalnız "BILGI: farkli"). Bugünkü sayfada bu açıklardan yararlanan bir sayı yok. Bağlı elemanların dışındaki rakamlı sözcükler yalnız şunlar: S1/S2, DS3235/MG996R, X2D, V1–V3, 3B/3D, commit kimliği ve dosya adları; pay seçenekleri %0–%25 muaf. | `SPB/bozma_sonuc.json`, `SPB/dogrula_kopya_tam.out` |
| 1b | Muafiyet ne kadar geniş | `:57-58`, `:202-208` | **GEÇER (not D-1).** Muafiyet adla değil, ata öğedeki `data-ui` ile veriliyor. İçerik denetlenmiyor. Sayfada kullanılan tek muafiyet `secenek` ×5 (pay seçenekleri). `eski` ve `duzeltme` öğelerinde sayı yok. | DOM dökümü |
| 2a | Sayılar bağımsız | B'nin kendi okuması (A'nın kodu kullanılmadan); `SPB/cdp/` DOM ve görünen metin dökümü | **GEÇER.** Hepsi kaynakla ve sayfayla aynı: boy 1.580 mm (`lale158-kontrol.json`, `zemin_y` 0; `montaj-analiz.json boy_mm` ve regresyon da 1.580). Kütle 25.720,55 g / 25,72 kg; modüller toplamı 25.720,54; çarpışma taraması 25.720,6. AM yerden 528,6. Parça 1.179 = modüller 59+342+357+161+73+73+57+57. GLB 1.192 düğüm. Rampa 1,519 ≥ 1,5. Tilt 3,64. Pan 2,21. Mik–hoparlör 574,3 ≥ 400. Çakışma 0 ×4; SY8205 × USB 0. Eklem aralığında çakışma 0. Servo 10 = 4 DS3235 + 6 MG996R; montajdaki adet ve eklem dosyasındaki servo alanı (DS3235 ×4, MG996R ×6) aynı. Kafa 10,1" QLED 1280 × 720 (`WaveShare 10.1HP-CAPQLED`). Göğüs 11,6" 1920 × 1080. Eklem: S1 −45…135, S2 5…120, dirsek 0…105, bilek −90…90, pan −90…90, tilt −13…13; bağımlı sınır S1 ≥ 120 → S2 ≤ 117; teker 0,5 / 1,8 / 0,1 / 0,1 m/s². Bu sayılar `kod/ortak/eklem_sinirlari.json` ile de aynı. Baskı: 72 parça; 7.668,9–7.726,7 g; 159,90–161,08 sa; destek 124,5 g; 13 destekli (9 tür); X2D 246 × 246 × 250, sığmayan 0; PETG 6.474,9 g; CF 1.194,0–1.251,8 g. `baski-listesi.md`'deki "72, 7,67–7,73 kg, 160–161 sa" ile de tutarlı. | `SPB/cdp/metin_1400.txt` |
| 2b | Maliyet | Üç bağımsız hesap: B'nin kendi kuralı, depodaki `planlama/adim5/maliyet_toplam.py` ve sayfa DOM'u | **GEÇER.** 121 kalem, ara toplam 103.188,02, %15 pay 15.478,20, genel toplam **118.666,22 TL** (≈ 2.400 USD; ara ≈ 2.087). Doğrulanan 98 / 121. Stokta yok 2 (Geniş köşe bağlantı, Kamera). Grup tutarları `maliyet_toplam.py` ile aynı ("Üretim ve sarf" 11.508 = üretim 4.665,13 + yazıcı 6.843,09). Gömülü JSON = `planlama/maliyet.json` (B'nin `json` karşılaştırması). | `SPB/cdp/metin_1400.txt` |
| 2c | 191 ↔ 210 | `montaj-analiz.json` `bom_ozet`, `parcalar`; `tasarim/freecad/montaj/ana_montaj.py:245-247` | **KALIR (O-2).** İki sayı da doğru, ama farklı şeyleri sayıyor. 210, montajdaki `tur=Satin` katı sayısı. 191, BOM'daki satın alma adedi. BOM, kodu "(" ile başlayan 19 katıyı dışarıda bırakıyor: 10 servo çıkış mili `(servo ile)`, 5 625ZZ bileziği `(625ZZ ile)`, 4 6808 bileziği `(6808 ile)`. Bunlar satın alınan parçanın içindeki ayrı katılar (76,8 g). Sayfa 210'u kullanıyor, çünkü kırılım (72+210+893+3+1) 1.179'a tutsun diye parça listesinden sayıyor. Ama aynı kartın yanında "⬇ Parça listesi (CSV)" bağlantısı var ve o dosyada satın alınanlar 191. "Satın alınan parça" için doğru sayı 191; 210 "katı" diye etiketlenmeli. | komut çıktısı |
| 3 | Açık kararlar | Kuyruk özet tablosu ve K28, K32, K34, K41, K42, K44, K45 ayrıntıları; DOM'da önerilen değerleri arama ("≤ 100 g", "59", "30°/s", "60°/s", "+1 makara", "2,0 kg", "7.217,95", "29.545", "112.678", "Boss taşı", "insert 168", "M3 177" …) | **GEÇER (O-1'e bağlı not).** 14 karar ve 33 etiketin hepsi kuyrukta "açık". Önerilen değerlerin hiçbiri sayfada yok. **K42:** sayfa bugünkü 3 × 0,5 kg makarayı ve CF ihtiyacını gösteriyor, önerilen +1 makarayı göstermiyor. **K44 / K45 / K38:** aralıklar sınır dosyasının değerleri; hız sınırı yok. **K28 / K34:** toplamın yanında etiketli; yazıcı kipi `maliyet.json` `baski` alanından geliyor. **K32:** toplam, kafa ekranını satın alınmış sayıyor (12.424,50 TL, `elde` düşülmemiş). K32'nin iki seçeneği de 118.666,22'yi değiştiriyor (a: elde düşülür, b: 112.678,69). Sayfa toplamın yanında K32'yi ve "karar değildir" notunu yazıyor; yeterli. Ama satırın modeli eski ekran (O-1). **K41:** S1 −45…135 sınır dosyasının değeri; koddaki 0…160 sayfada yok. "Yazılım aralığı karar bekliyor" etiketi var. Sütun başlığı "Aralık (°)" yerine "sınır dosyası" dese belirsizlik kalkar (öneri, bulgu değil). Bilgi: maliyet bölümü K33 ve K43'ü listelemiyor (küçük tutarlar; satırlar bugünkü değerle). | `SPB/cdp/metin_1400.txt`, `karar-kuyrugu.md:16-61, 493-503, 618-725` |
| 4a | 1,65 / 1650 / 165 cm / 170 | B'nin görünen metin ve DOM araması | **GEÇER.** Görünen metinde: "1,65" 11 kez, hepsi `maliyet.json` metni (kalem 5, 8, 14, 19, 33, 92, 107, 139 notu; `notlar[0].b`, `[0].t`, `[1].b`). 11'inin de yanında "eski tasarım notu" etiketi var (B'nin DOM denetimi: 8/8 kalem notu, 3/3 not). "1650", "1.650", "165 cm/mm" 0. "125 cm" 3 kez, hepsi aynı etiketli notlarda. "170" 3 kez: ikisi klasör adı "taslak-170" (etiketli notlar 14 ve 139), biri kamera FPC boyu "~170–190 mm" (boy değil). Gömülü maliyet JSON'unda 12 eşleşme, dokunulmaz kaynağın birebir kopyası. Şablonda, üreticide ve model tablosunda 0. | `SPB/cdp/metin_1400.txt` |
| 4b | Öteki eski iddialar | 7", Nextion, 6 servo, MAX98357A, DS3218/STS3215, GC9A01, 1280 × 800, V3, CadQuery, eski takvim | **KALIR (O-1).** Temiz olanlar: 6 servo, DS3218, STS3215, GC9A01 0. "MAX98357A" yalnız `notlar[0]`'daki doğru tarihçe cümlesinde ("MAX98357A → PAM8403", K16). CadQuery ve V1–V3 yalnız "eski" diye anılıyor. Takvim tarihsiz; "2 Ekim" hoca notu kaldırılmış; "Ekim 2026" geçenler fiyat tarihi. **İşaretsiz eski iddialar:** (1) `kalemler[33]` "Yüz ekranı · Waveshare 10.1" HDMI LCD (B) kasalı, 1280 × 800 IPS (CAD'deki tahmini model)": model sütunu işaretsiz ve KPI kartındaki QLED 1280 × 720 ile çelişiyor; notu 1,65 içerdiği için etiketli. (2) `kalemler[36]` notu "Nextion UART olduğu için HDMI adedi 1 (yalnız 7" yüz ekranı)". (3) `kalemler[78]` notu "Nextion RX". | `SPB/cdp2/b-1400-yuz-ekrani.png` |
| 5 | Tarayıcı | B'nin kendi CDP betiği (`SPB/b_cdp.py`; A'nın kodu kullanılmadı). Headless Chrome, `file://`, `Emulation.setDeviceMetricsOverride` ile 1400, 360 ve 390 px. Konsol: istisna, `console.error/assert/warning`, `Log` error/warning, ağ hatası. Taşma: `body` altında sağ kenarı görüntü alanını aşan ve kaydırılabilir kabı olmayan öğeler. | **GEÇER.** Üç genişlikte de: konsol (uyarı dahil) 0, ağ hatası 0, `data-hazir=1` (three.js CDN'den yüklendi, model çizildi), `data-hata` yok. 360 px: scrollWidth 360 = innerWidth, `scrollTo(5000)` sonrası scrollX 0, taşan öğe 0. 390 px de aynı. 12 görüntü alındı ve Read ile bakıldı (1400: üst, korunan, modüller, baskı, maliyet, maliyet tablosu, kararlar, yüz ekranı satırı, kablo satırı; 360: üst, model, eklem, maliyet, kararlar). Model 360 px'te de görünüyor. 360 px eklem tablosunda servo sütunu sözcük sözcük kırılıyor, harf harf değil. A'nın 10 görüntüsünden 360-maliyet ayrıca açıldı; B'ninkiyle aynı içerik. | `SPB/cdp/cdp_rapor.json`, `SPB/cdp/*.png`, `SPB/cdp2/*.png` |
| 6a | Üretici yeniden koşusu | `SPB/kopya/` içinde `py -3 -I -X utf8 tasarim/cad/demo_uret.py` | **GEÇER.** rc 0: "125 anahtar · 14 karar · 153 kalem", model 1.192 düğüm. Sayfa sha256 `c39a7f76…` ve `lale158-model.js` sha256 `58419733…`, depodakilerle **bayt bayt aynı** (`cmp`). Depodaki sayfanın üzerine yazılmadı. | `SPB/sha_once.txt` |
| 6b | Brief dışı değişiklik | `git diff --stat` (3 dosya, +996 / −1.539); `git grep` ile üretici ve şablonun kullanıcıları | **GEÇER (not D-5).** Değişiklik brief'in yazma alanında. Kaldırılanlar brief'le uyumlu: eski CadQuery modeli, kaydırıcılı devrilme / motor / servo hesabı (kaynakta karşılığı yok, sayı elle yazılı), 1,65 m gövde ekranı denemesi, V1/V2 seçicisi. `robot_cad.py:1046-1047` `demo_uret.build(MODEL_JSON)` çağrısı bozulmamış (imza aynı). Üreticiyi içe aktaran başka betik yok. Sayfadaki bağlantıların hedefleri izlenen dosyalar: `rehber/index.html`, `freecad/montaj/robot-montaj.step`, `robot-bom.csv`, `freecad/index.html`. Kapsam dışında kalıp artık eskiyen metinler: `README.md:21` ve `planlama/proje-plani.md:235` (D-5). | `git grep` |
| 6c | Model kopyası | B'nin kendi base64 çözümü | **GEÇER.** GLB 2.559.336 bayt, sha256 `760bf1ff5955…`, `rehber/veri/robot.glb` ile aynı; `robot.glb` HEAD ile de aynı. Dosya 3.495.365 bayt; metin kısmında kullanıcı yolu 0. | |
| 6d | Bütünlük | Depoda | **GEÇER.** `carpisma_kos.py kontrol` rc 0 ("izlenen 17 dosyanin ozetleri kayitla ayni"). `regresyon.py --yazma` rc 0 (10/10 aynı, "GEÇER"). Dosyalar ve `git status` öncesi ve sonrası aynı. | `SPB/carpisma.out`, `SPB/regresyon.out` |
| 7a | Takma ad ve soyad | `SPB/ad_tara.py`: ad çalışma anında `git show 647cafc^` ↔ `647cafc` `kafa_parcalar.py` 6. satırındaki tek değişen sözcükten türetildi. Ekrana ve dosyaya yazılmadı. 4 harflik gövde ve tam biçim, büyük/küçük harf duyarsız arandı. Bakılan yerler: sayfa, gömülü JSON ve JS, model dosyası (metin + çözülmüş GLB), üretici, şablon, F9b betikleri, günlük ve brief, `maliyet.json`, `rehber-veri.json`, B'nin DOM / metin / öznitelik dökümü. | **GEÇER.** Tam ad her yerde 0. Gövde yalnız 1 kez eşleşti: model dosyasındaki base64 dizisinin içinde, rastgele 4 harf (`SPB/ad_yer.py`: base64 içinde; çözülmüş GLB'de 0). "Efe" / "Ahmet" / hoca / unvan + büyük harfli sözcük kalıbı 0; başka öğrenci ya da danışman soyadı yok. Sayfada kişi olarak yalnız "Ahmet" var; "Efe" adı `maliyet.json` notlarından geliyor (zaten commit'li). | `SPB/ad_tara.py` |
| 7b | Yerel kullanıcı yolu | Aranan desenler: Windows ve Unix kullanıcı klasörü kalıpları, uygulama verisi klasörü, yerel kullanıcı adı ve bulut klasörü adı. Taranan dosyalar: commit'e girecek bütün metin dosyaları, model dosyasının metin kısmı ve GLB'si, 10 PNG'nin baytları. | **GEÇER.** 0. `F9b-gunluk.md:105`'teki tek eşleşme "masaüstü Chrome penceresi" ifadesi (yol değil). | |
| 7c | KT-F9b-2 (3,4 MB kopya) | `rehber/veri/` izlenen dosyalar; F7b'nin `robot-glb.js` biçimi | **Öneri.** A'nın gerekçesi ("kopya sayfayı F7b'den bağımsız tutar") zayıf. `F9b-dogrula.py` [4] kopyayı zaten `robot.glb` ve `rehber-veri.json`'a bağlıyor; F7b'nin her yeniden üretimi demo_uret'i yeniden koşturuyor (O-3 bunun örneği). F7b'nin `rehber/veri/robot-glb.js` (`window.REHBER_GLB`, aynı GLB) ve `rehber-veri.js` (`window.REHBER_VERI`) dosyaları ef5a978 / 887bcfe'den beri izleniyor. `file://` altında `<script src>` ile okunur; `fetch` gerekmez. Kopya ise herkese açık depoya **üçüncü** bir 3,4 MB base64 kopya ekliyor ve her GLB değişiminde geçmiş 3,4 MB daha büyüyor. **B'nin önerisi: b** (göreli bağlantı + doğrulamada global adların varlık denetimi), F7b kapandıktan sonra. a da kabul edilebilir; depo bugün ≈ 421 MiB, bunun yanında %1'in altında. Karar Ahmet'in. | `git ls-files rehber/` |
| 7d | Silinen iki dosya | `git log --all -- 'planlama/d158/F9b-*'`, `git ls-files`, `git stash list`, `git status` | **KOŞULLU (D-4).** F9b dosyası git geçmişinde hiç yok; stash yok; izlenen dosyalarda silme 0. Silinen iki tam sayfa görüntüsü takip dışıydı ve bu işte üretilmişti. Kayıp yok: `goruntu(tam=True)` yolu betikte duruyor, yeniden üretilebilir. Ama brief silmeyi yasaklıyor ve günlüğün başı (`:3`) "silme yok" diyor; `:138` ise silmeyi yazıyor. Çelişki düzeltilmeli. | |
| 8 | Commit listesi | §7 ↔ `git status --porcelain -uall`; `comm` (`SPB/st_all.txt` ↔ `SPB/ekle.txt`) | **KOŞULLU (D-3).** A'nın 16 dosyasının hepsi durumda var. Eksik: `planlama/d158/F9b-brief.md` (izlenmiyor; brief gereği girmeli) ve bu dosya. Durumda olup listede olmayanların hepsi dışlamada: F7b (`rehber/`, `planlama/rehber/`, `tasarim/freecad/rehber/`, `F7b-*`), `dongu-158.md`, `FREECAD-KILIT.txt`, öteki kapsam dışı yollar. **PNG'ler:** 10 dosya 1,1 MB. Hepsinin girmesini öneririm. Günlük §6 onları kanıt olarak anıyor; dışarıda kalırlarsa çalışma kopyasında takip dışı artık olarak dururlar. Silmek de bu pakette yasak. Boyut, model kopyasının üçte biri. Koşul: O-1 / O-2 düzeltmesinden sonra `--goruntu` bir kez yeniden koşulsun, çünkü `1400-ust`, `360-ust` ve maliyet görüntüleri değişen kartları gösteriyor. Sonra bir daha koşulmasın; her koşu yeni bloblar üretir. | `SPB/st_all.txt`, `SPB/ekle.txt` |

## Bulgular

**Kritik: yok.**

### O-1 (orta). Maliyet tablosunda işaretsiz eski kafa ekranı ve Nextion / 7" iddiaları; kafa ekranı KPI ile çelişiyor

Yer: `planlama/maliyet.json:69` (`kalemler[33]`), `:72` (`[36]`), `:115` (`[78]`). Sayfada işaretleme `tasarim/cad/demo_uret.py:157-163` (`NOT_DUZELTME` yalnız `notlar`'a, `ESKI_DESEN` `1[,.]65 ?m|125 ?cm`) ve `TPL:424-427, 436`.

Kanıt (`SPB/cdp2/b-1400-yuz-ekrani.png`, `SPB/cdp/metin_1400.txt:309, 313, 456`):
- KPI kartı (`TPL:130`): "10,1" QLED · 1280 × 720 · WaveShare 10.1HP-CAPQLED".
- Maliyet tablosu, aynı sayfa: "Yüz ekranı · Waveshare 10.1" HDMI LCD (B) kasalı, 1280 × 800 IPS, kapasitif (CAD'deki tahmini model) · 12.424,50 TL". Bu satır genel toplama giriyor. Model sütununda işaret yok; yalnız 1,65 içeren notunda "eski tasarım notu" var.
- "Ekran kablosu" notu: "Nextion UART olduğu için HDMI adedi 1 (yalnız 7" yüz ekranı)". İşaret yok.
- "Direnç seti" notu: "… Nextion RX …". İşaret yok.
- Sayfanın kendi notu (`notlar[1]`) "Nextion kaldırıldı" diyor. Yani sayfa kendi içinde çelişiyor.

Brief "kafa QLED 10,1"" ve "eski bilgi işaretli" istiyor. `maliyet.json` dokunulmaz, ama işaretleme sayfanın işi; A bunu 1,65 notlarında zaten yapıyor.

Düzeltme (yalnız `demo_uret.py` + `TPL`):
- Kalem düzeyinde düzeltme notu ekle (`NOT_DUZELTME`'nin kalem karşılığı). Metin sayısız olsun. Örnek: `kalemler[33]` "F9b notu: bu satır 29.10 listesinin ekranı; CAD'deki yüz ekranı yukarıdaki karttaki QLED. Hangi satırın alınacağı K32'ye bağlı."
- `kalemler[36]` ve `[78]` notlarını "eski tasarım notu" diye işaretle. Örneğin `ESKI_DESEN`'e `Nextion|7"` eklenebilir: `notlar[1]`'deki doğru "Nextion kaldırıldı" cümlesi de etiket alır, ama bu zararsız. Ya da kalem numarasıyla liste kullanılabilir.
- `F9b-dogrula.py`'ye denetim ekle: bu üç kalemde işaretin var olduğunu denetlesin (D-1'deki `data-ui` içerik denetimiyle birlikte).
- KT-F9b-3'e (`F9b-gunluk.md:158-160`) bu üç kalemi ve D-7'yi ekle.

### O-2 (orta). "Satın alınan 210", alım listesindeki 191 ile uyuşmuyor

Yer: `TPL:128`, `demo_uret.py:73` (`p_satin` = `parcalar[tur=Satin]#say`), `F9b-gunluk.md:169-170` ("incelenmedi").

Kanıt (madde 2c):
- `montaj-analiz.json` `bom_ozet.Satin.adet` 191.
- `parcalar[tur=Satin]` 210.
- Fark 19 katı. `ana_montaj.py:246` kodu "(" ile başlayanları BOM'a yazmıyor: 10 servo çıkış mili, 9 rulman bileziği. Bunlar satın alınan bir parçanın parçası.
- Aynı kartın üstündeki "⬇ Parça listesi (CSV)" bağlantısı 191 gösteriyor.

Düzeltme:
- Kırılım 1.179'a tutsun diye 210 kalabilir, ama etiket "satın alınan 210 katı" olmalı.
- Yanına bağlı bir anahtar ekle: `p_satin_bom` ← `montaj-analiz.json bom_ozet.Satin.adet`. Metin: "(alım listesinde {{p_satin_bom}} adet; fark servo çıkış milleri ve rulman bilezikleri, ayrı katı olarak modellendi)".
- "19" yazılacaksa o da bir anahtara bağlanmalı; yazılmasa da olur.
- `F9b-gunluk.md` §9'daki açığı bu açıklamayla kapat.

### O-3 (orta, süreç). Model kopyası F7b'nin commit'lenmemiş `rehber-veri.json`'una bağlı

Kanıt:
- `rehber/veri/rehber-veri.json` çalışma kopyasında değişik (F7b, 17:21).
- HEAD ile `parcalar` (id, ad, modül, r) arasında 147 ad farkı var (Türkçe karakter düzeltmesi). Ayrıca yeni `modul_ad` alanı var.
- `lale158-model.js` bu çalışma kopyasından üretildi.
- `SPB/kopya/`'da `rehber-veri.json` HEAD hâline çevrildi: `F9b-dogrula.py` → rc 1, "model parca tablosu rehber-veri.json ile ayni degil".

Yani F9b commit'i F7b'den önce girerse o commit'in kendi doğrulaması geçmez. F7b kontrolde ve `rehber-veri.json` / `robot.glb`'yi yeniden üretebilir.

Düzeltme (C için, A'nın işi değil):
- F7b commit'i F9b'den önce (ya da aynı anda) girsin.
- F7b'nin son hâliyle `py -3 tasarim/cad/demo_uret.py` koşulsun.
- `F9b-dogrula.py` → 0 olsun. Sayfa ve model dosyası değiştiyse yeni hâlleri commit'lensin.

### D-1 (düşük). Doğrulama betiğinin dört açığı (bugünkü sayfayı etkilemiyor)

Yer: `planlama/d158/F9b-dogrula.py:194`, `:202-208`, `:571-573`; öznitelikler hiç taranmıyor.

Kanıt (`SPB/bozma_sonuc.json`):
1. `SAYI` deseni harfe bitişik sayıyı ad sayıyor. "1590mm", "7inç", "6xServo" geçti (rc 0).
2. `data-ui` muafiyeti ata öğeye bakıyor, içeriği denetlemiyor. `<em data-ui="eski">boy 1.590 mm</em>` geçti.
3. `title` / `aria-label` öznitelikleri sayı taramasına girmiyor. `title="boy 1.590 mm"` geçti; "1.650" ise 1,65 aramasına takıldı.
4. Anahtar → JSON yolu eşlemesinin anlamı denetlenmiyor. Brief sayıları (`:571-573`) yalnız "BILGI: farkli" basıyor. `boy` `s3_mm`'e (1.270) bağlandığında rc 0.

Öneri (bu turda zorunlu değil):
- (4) için brief sayılarını hataya çevir: boy 1580, rampa 1,519, tilt 3,64, pan 2,21, mik–hoparlör 574,3, servo 10.
- (2) için `data-ui="eski"` ve `"duzeltme"` öğelerinin metni sabit metne eşit olsun.
- (1) için birim bitişik (`\d+(mm|cm|kg|V|A|in|inç)`) deseni de bağsız sayılsın.

### D-2 (düşük). "13 kablo yolu gösterimi" yanlış: 12 kablo yolu + 1 gösterim parçası

Yer: `TPL:153`. `glb_ref` = `rehber-veri.json parcalar[tur=Referans]#say` = 13. Bunların 12'si "Kablo yolu 1…12", biri "Ana anahtar düğmesi (gösterim, kabuk deliği gerekir)" (r `ref`).

Düzeltme: "… ve {{glb_ref}} gösterim parçası (kablo yolları ve ana anahtar düğmesi)".

### D-3 (düşük). Commit listesinde `F9b-brief.md` yok

`F9b-gunluk.md:143-146`. Dosya izlenmiyor; brief gereği girmeli. Aşağıdaki C listesinde var.

### D-4 (düşük, süreç). Silme yasağı ve günlükte çelişki

`F9b-gunluk.md:3` "silme yok" diyor, `:138` iki tam sayfa görüntüsünün silindiğini yazıyor. Brief silmeyi yasaklıyor. Dosyalar takip dışıydı (madde 7d), kayıp yok.

Düzeltme: `:3`'ü "Commit / push / merge yok. Kural dışı tek silme: bu işte üretilen iki takip dışı tam sayfa PNG'si (§6)" diye yaz.

### D-5 (düşük). Kapsam dışı belgelerde eski demo tarifi

Yerler:
- `README.md:21`: "Eski CadQuery 3B montajı (V1 / V2 / V3, 125 cm); devrilme, motor ve servo hesabı canlı".
- `planlama/proje-plani.md:235`: "`demo_uret.py` yalnız maliyet sayfasını üretir".

İkisi de F9b'nin yazma alanı dışında. KT-F9b-4'e (`F9b-gunluk.md:161-162`, şimdi yalnız `CLAUDE.md`) eklenmeli.

### D-6 (düşük). Doğrulama, Windows'ta çıktı yönlendirilince çöküyor

`F9b-dogrula.py:482`, `print`. Çıktı dosyaya ya da boruya yönlendirilince (cp1254) "−" / "·" karakterinde `UnicodeEncodeError` veriyor ve rc 1 dönüyor. Hata güvenli yönde (geçirmiyor), ama C'nin günlüğe yönlendirerek koşusu yanlış "GEÇMEZ" verir. B `-X utf8` ile koştu.

Düzeltme: `main()` başına `sys.stdout.reconfigure(encoding="utf-8")` ya da docstring'e `-X utf8`.

### D-7 (düşük, bilgi). Sayfada iki ayrı "K3"

Karar tablosundaki K3 "Düz zeminde elde yük sınırı". `maliyet.json` notları ise eski numaralamayla K3'ü akü için kullanıyor:
- `notlar[4]` "Akü Victron SuperPack 12,8/20 (K3)" (`maliyet.json:24`);
- akü kaleminin notu "K3 (14 Ekim 2026), akü raporunun 1. tercihi".

Okuyan karıştırabilir. KT-F9b-3'e "maliyet.json'daki K-numaraları kuyrukla çakışıyor" diye eklenmeli. Sayfada düzeltme gerekmiyor.

## Genel karar

**KOŞULLU GEÇER.** Sayılar, maliyet, model kopyası, kararlar, 1,65 temizliği, tarayıcı, üretici tekrarlanabilirliği ve tarama / regresyon bütünlüğü bağımsız olarak doğrulandı.

Commit'ten önce:
- A: O-1, O-2 (zorunlu); D-2, D-4 (aynı turda, dakikalar); D-3, D-5, D-7 (yalnız günlük metni).
- C: O-3 sırası.

D-1 ve D-6 önerilir, zorunlu değil.

Düzeltme yalnız `demo_uret.py`, `viewer-template.html`, (D-1 / D-6 yapılırsa) `F9b-dogrula.py` ve `F9b-gunluk.md`'de olmalı. `maliyet.json`, `kod/`, F7b alanı ve tarama kaynakları değişmemeli. B'nin dar yeniden kontrolü şunlardan oluşur: diff okuması, kopyada üretici bayt eşitliği, `F9b-dogrula.py` 0, görünen metinde O-1 / O-2 / D-2 kontrolü.

## A için düzeltme listesi

1. **O-1 (zorunlu).** `demo_uret.py` + `TPL`:
   - `kalemler[33]` satırına sayısız F9b düzeltme notu ekle (K32'ye bağlı, CAD'deki ekran QLED).
   - `kalemler[36]` ve `[78]` notlarını "eski tasarım notu" diye işaretle.
   - `F9b-dogrula.py`'ye bu üç işaretin varlık denetimini ekle.
2. **O-2 (zorunlu).**
   - `TPL:128`'de "satın alınan {{p_satin}} katı (alım listesinde {{p_satin_bom}} adet; fark servo çıkış milleri ve rulman bilezikleri)".
   - `SAYILAR`'a `("p_satin_bom", "montaj", "bom_ozet.Satin.adet", 0)` ekle.
   - Günlük §9'daki 191 ↔ 210 açığını kapat.
3. **D-2.** `TPL:153` "{{glb_ref}} gösterim parçası (kablo yolları ve ana anahtar düğmesi)".
4. **D-4.** `F9b-gunluk.md:3` silme cümlesini düzelt.
5. **D-3, D-5, D-7.** Günlük §7'ye `F9b-brief.md` ekle. KT-F9b-4'e `README.md:21` ve `proje-plani.md:235`, KT-F9b-3'e O-1'in üç kalemini ve K3 çakışmasını ekle.
6. (Önerilir) **D-1, D-6.** Brief sayılarını hataya çevir; `data-ui` içerik denetimi; birim bitişik sayılar; stdout UTF-8.
7. Bitince:
   - `py -3 tasarim/cad/demo_uret.py`.
   - `py -3 -X utf8 planlama/d158/F9b-dogrula.py --goruntu` → 0 (10 PNG bir kez yenilenir).
   - Görüntülere Read ile bak.
   - `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0.
   - Değişen dosyaların sha256'sını günlüğe yaz.

## C için onaylı `git add` listesi

**Koşul:** O-1 / O-2 düzeltmesinden ve B'nin dar yeniden kontrolünden sonra. **O-3:** F7b commit'i önce girer. Ardından `py -3 tasarim/cad/demo_uret.py` ve `py -3 -X utf8 planlama/d158/F9b-dogrula.py` → 0. Sayfa ya da model dosyası değişirse yeni hâli alınır.

19 dosya: 3 değişik + 16 yeni (bu dosya dahil). Liste KT-F9b-2 = a varsayımıyla yazıldı (A'nın önerisi). Ahmet b'yi seçerse `tasarim/cad/lale158-model.js` çıkar ve A şablonu `../rehber/veri/robot-glb.js` + `rehber-veri.js`'e bağlar; B yeniden bakar. B, durumdaki her yolun ya bu listede ya da dışlamada olduğunu `comm` ile denetledi (`SPB/st_all.txt` ↔ `SPB/ekle.txt`: eksik 0, fazla 0; bu dosya ve brief hariç).

```
git add tasarim/Robot-Tasarim-Demosu.html tasarim/cad/demo_uret.py tasarim/cad/viewer-template.html \
  tasarim/cad/lale158-model.js \
  planlama/d158/F9b-brief.md planlama/d158/F9b-gunluk.md planlama/d158/F9b-kontrol.md \
  planlama/d158/F9b-dogrula.py planlama/d158/F9b-envanter.py \
  planlama/d158/F9b-goruntu-1400-ust.png planlama/d158/F9b-goruntu-1400-yan-seffaf.png \
  planlama/d158/F9b-goruntu-1400-modul-on.png planlama/d158/F9b-goruntu-1400-korunan-eklem.png \
  planlama/d158/F9b-goruntu-1400-baski-maliyet.png planlama/d158/F9b-goruntu-1400-kararlar.png \
  planlama/d158/F9b-goruntu-360-ust.png planlama/d158/F9b-goruntu-360-model.png \
  planlama/d158/F9b-goruntu-360-eklem.png planlama/d158/F9b-goruntu-360-maliyet.png
```

**Dışlama (F9b değil):**
- F7b: `rehber/` (app.js, stil.css, yazdir.html, goruntu/, veri/rehber-veri.js / .json), `planlama/rehber/`, `tasarim/freecad/rehber/`, `planlama/d158/F7b-brief.md`, `planlama/d158/F7b-gunluk.md`.
- `planlama/dongu-158.md`, `planlama/d158/FREECAD-KILIT.txt`.
- `planlama/d158/F5-pano-govde.txt`, `planlama/d158/F5b-pano-govde.txt`.
- `tasarim/freecad/kabuk/gorsel/*.png` (13, K23), `tasarim/freecad/montaj/yerlesim-kontrol.json`.
- `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`.
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`.

C'ye not:
- Üç dosyada "LF → CRLF" uyarısı var. Checkout, reset ya da stash yapılmamalı.
- Commit'ten sonra `F9b-dogrula.py` (`-X utf8`) ve `carpisma_kos.py kontrol` → 0.
- `main`'e birleştirme yok (KT-F9b-1, Ahmet onayı).

**Commit mesajı önerisi (tek satır):**
`Lale P9.2: demo sayfası 1,58 m sayılarıyla (demo_uret.py → 125 JSON anahtarı, rehber GLB kopyası, 14 açık karar "karar bekliyor", maliyet 118.666,22 TL); F9b-dogrula.py (F9b)`

## Kanıtlar (komut → çıktı, özet)

```
SPB/kopya: py -3 -I -X utf8 tasarim/cad/demo_uret.py              → rc 0; sayfa c39a7f76…, model 58419733… = depo (cmp, bayt bayt)
SPB/kopya: py -3 -I -X utf8 planlama/d158/F9b-dogrula.py          → rc 0, "SONUC: GECER (hata 0)" (A ile aynı sayımlar)
SPB/kopya: aynı betik, -X utf8 olmadan, çıktı dosyaya               → UnicodeEncodeError, rc 1 (D-6)
SPB/b_bozma.py (16 bozma) + 2 ek (s3_mm eşlemesi, title "1.590")    → 11 yakalandı, 7 geçti: 6'sı D-1, biri tarayıcısız koşuda sahte data-mk (tarayıcılı koşu yakalıyor); kopya sayfa geri yüklendi (sha aynı)
SPB/kopya: rehber-veri.json = HEAD hâli → F9b-dogrula.py            → rc 1, model tablosu farklı (O-3); geri yüklendi
SPB/b_cdp.py (B'nin CDP'si) 1400 / 360 / 390 px                     → konsol 0, ağ hatası 0, data-hazir 1, scrollWidth = innerWidth, taşan öğe 0
B'nin JSON okuması + planlama/adim5/maliyet_toplam.py               → 121 kalem, 103.188,02, 118.666,22 TL; 98/121; stok yok 2
montaj-analiz.json: Satin 210 katı, bom_ozet 191; "(" kodlu 19 katı → O-2
py -3 tasarim/freecad/carpisma_kos.py kontrol (depo)                → rc 0, 17 özet aynı
py -3 planlama/d158/regresyon.py --yazma (depo)                     → rc 0, 10/10 aynı, GEÇER; sha1 ve git status aynı
SPB/ad_tara.py, SPB/ad_yer.py                                       → tam ad 0; tek gövde eşleşmesi base64 içinde rastgele (GLB'de 0)
git log --all -- 'planlama/d158/F9b-*'                              → boş (silinenler takip dışıydı)
git status --porcelain -uall ↔ SPB/ekle.txt (comm)                   → eksik 0, fazla 0
```

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

**Karar: GEÇER.**
- O-1 ve O-2 kapandı.
- O-3 göreli bağlantıyla (KT-F9b-2 = b) çözüldü. Sıra yine önerilir (aşağıda).
- D-2…D-7 doğru işlendi. D-1 kısmen işlendi; önerilen bir maddeydi, engel değil.

Yeni bulgular: kritik 0, orta 0, düşük 2 (D-8, D-9). FreeCAD, silme ve git yazma yok.

Bu turda B'nin kopyası `SPB/kopya2/`: depodan 18 dosya, F7b'nin 17:54 tarihli `rehber/veri/` dosyaları dahil. A'nın §10'daki sha256'ları (sayfa `9613ce541bb3`, üretici `a600852640c9`, şablon `eed41f6bec3d`, doğrulama `12c608a40019`) B'nin aldıklarıyla aynı.

## Madde sonuçları

| # | Madde | Yöntem | Sonuç |
|---|---|---|---|
| 1a | `demo_uret.py` diff'i | İlk kontrol kopyası ↔ şimdiki (`diff -u`) | **GEÇER.** Yalnız istenenler var. (1) Model kopyası kaldırıldı: `model_kopyasi()` → `model_bilgi()`. Dosya yazmıyor; yalnız göreli dosyaların varlığını ve her GLB düğümünün `parcalar`'da olduğunu denetliyor. (2) `p_satin_bom` ← `bom_ozet.Satin.adet` (O-2). (3) `glb_kablo` ← `parcalar[tur=Referans][r=kablo]#say` (D-2). (4) `KALEM_ISARET` + `kalem_isaret()` (O-1). Kalem adı ve aranan metin korunuyor; `maliyet.json` kayarsa üretim duruyor. Ek metninde bağsız rakam varsa üretim duruyor; 10,1 `kafa_in` anahtarından `data-k` olarak geliyor. Başka değişiklik yok. |
| 1b | `viewer-template.html` diff'i | Aynı yöntem | **GEÇER.** Değişenler: Parça KPI etiketi (O-2); model notu (D-2 ve göreli dosyalar); iki `<script src>` (`../rehber/veri/rehber-veri.js`, `robot-glb.js`); okuyucu `window.REHBER_GLB` / `REHBER_VERI`, parçalar düğüm adıyla eşleniyor; `eski(t,i)`, `duz(i)`, bir CSS satırı. GLB okuyucusu, kamera ve maliyet hesabı aynı. |
| 1c | `F9b-dogrula.py` diff'i ve muafiyet daraltması | Aynı yöntem ve bozma | **GEÇER.** [4] göreli dosyaları o anki hâlleriyle denetliyor: `robot-glb.js` GLB'si `robot.glb` ile bayt bayt aynı, `rehber-veri.js` = `.json`, düğümlerin hepsi kapsanıyor, eski kopyaya bağlantı hata. [6] brief sayıları artık hata; gömülü işaret listesi bağımsız `ISARET` ile karşılaştırılıyor. [8] DOM'da kalem 33'ün not metni ve içindeki `data-k`; kalem 36 ve 78'in etiketi. D-6: `stdout.reconfigure`; B dosyaya yönlendirilmiş çıktıyla `-X utf8` olmadan koştu, rc 0. **Muafiyet daraltması doğru, sahte geçiş açmıyor.** Bağsız sayıya yalnız `secenek` ve `secim` izin veriyor. `eski` / `duzeltme` içindeki sayı ancak bir `data-k` atası varsa bağlı sayılıyor, o `data-k`'nın metni de DOM'da kaynakla karşılaştırılıyor. Bir `data-ui` öğesine `data-k` eklemek de açık değil: `data-k` metni değerin tam kendisi olmak zorunda. |
| 2 | Doğrulama ve bozma | `SPB/kopya2/`'de tam koşu (Chrome dahil) ve `SPB/b_bozma2.py` (16 bozma; 2'si Chrome'lu). Her bozmadan sonra sayfa, `robot-glb.js`, `rehber-veri.js` ve `maliyet.json` geri yüklendi; sha256'ları ilk hâliyle aynı. | **GEÇER (not D-9).** Değiştirilmemiş kopya: rc 0. 127 anahtar / 130 eleman; statik 119 bağlı, 5 muaf, 0 bağsız. DOM 1400 / 360: konsol 0, 1.638 bağlı, 0 bağsız. İşaretler: kalem 33 F9b notu, 36 ve 78 "eski tasarım notu". 1,65 eşleşmesi 23 (ilk turla aynı yerler). **Yakalanan 12 bozma:** gömülü işaretten kalem 36'yı silme; kalem 33 türünü "eski" yapma; 33'ün not metninde QLED → LCD (DOM); sayfa JS'inde `duz()` boş (DOM); `p_satin_bom` 191 → 190; `p_satin_bom` span'i yerine düz "191"; `data-ui="eski"` içinde "1.590"; `boy` → `s3_mm` (artık brief hatası); `<script src>` eski kopyaya; `robot-glb.js` bir bayt; `rehber-veri.js` ≠ `.json`; `maliyet.json` kalem adı. **Geçen 4 bozma (D-9):** `p_satin_bom` → `bom_ozet.Baski.adet` (72, gömülü değer tutarlı); `data-ui="secim"` içinde "1.590"; "1590mm"; `title` özniteliğinde "1.590". |
| 3a | `file://` göreli yükleme | B'nin CDP'si (`SPB/b_cdp.py`), `SPB/kopya2/tasarim/` altından 1400 / 360 / 390 px | **GEÇER.** İki `<script src>` yüklendi, `data-hazir=1`, model çizildi. Konsolda istisna, error, warning ve ağ hatası 0. 360 ve 390 px'te scrollWidth = innerWidth; taşan öğe 0; scrollX 0. |
| 3b | Başka klasörde açan kullanıcı | Yalnız HTML dosyası ayrı bir klasöre kopyalandı (`SPB/yalniz/`) | **KOŞULLU (D-8).** Sayılar, kararlar ve maliyet çalışıyor; yatay taşma yok. Model yüklenmiyor (`data-hazir="model-yok"`). Konsolda 3 hata: iki dosya yüklenemedi ve bir `console.error`. Görünen yedek metin "3B görünüm açılamadı (three.js için internet bağlantısı ve WebGL gerekiyor)" diyor; asıl neden yanlış söyleniyor. Göreli yol depo yapısına bağlı: `tasarim/` ve `rehber/` yan yana olmalı. GitHub Pages ve depo içi açılış sorunsuz. Sayfanın notu dosyaları adıyla anıyor ama "depo içinden açılmalı" demiyor. İlk turdaki kopya da `cad/` alt klasörüne bağlıydı; bağımlılık türü yeni değil, yalnız klasör değişti. |
| 3c | Kalem 33 / 36 / 78 görüntüleri | `SPB/cdp3/b-1400-k33.png`, `b-1400-k78.png`, `b-360-k33.png`, `b-360-k36.png`, `b-360-k78.png`; ayrıca `b-1400-ust.png` | **GEÇER.** Kalem 33: notun yanında "eski tasarım notu" ve altında turuncu "F9b notu: K32'ye bağlı; CAD'deki kafa ekranı QLED 10,1"" var; 10,1 noktalı çizgili `data-k`. Kalem 36 ("Nextion UART … yalnız 7" yüz ekranı") ve kalem 78 ("Nextion RX") "eski tasarım notu" etiketli. 360 px'te satırlar kırılıyor, taşma yok. Parça kartında "satın alınan 210 katı (alım listesinde 191 adet; fark servo çıkış milleri ve rulman bilezikleri)". Model notunda "13 gösterim parçası (12 kablo yolu ve ana anahtar düğmesi)". Model göreli dosyalardan çizildi. |
| 4 | Üretici ve eski kalıntı | `SPB/kopya2/`'de (içinde `lale158-model.js` yok) `py -3 -I -X utf8 tasarim/cad/demo_uret.py` | **GEÇER.** rc 0: "127 anahtar · 14 karar · 153 kalem; model göreli … 1192 düğüm". Sayfa depodakiyle **bayt bayt aynı** (`cmp`, sha256 `9613ce541bb3…`). Kopyada `lale158-model.js` oluşmadı (`find` → 0; `tasarim/cad/` yalnız üretici ve şablon). Depodaki `tasarim/cad/lale158-model.js` (3,4 MB, 17:30) takip dışı artık olarak duruyor. Sayfa ve doğrulama onu kullanmıyor. Silme kararı C'nin ya da Ahmet'in; bu pakette silme yasak. |
| 5 | O-3 yeniden | `SPB/kopya2/`'de `rehber-veri.js` ve `.json` HEAD hâline çevrildi | **GEÇER.** `F9b-dogrula.py --tarayicisiz` → rc 0. Göreli bağlantıda doğrulama dosyaların o anki hâlini okuyor; F9b commit'i hangi `rehber/veri/` hâliyle girerse girsin kendi içinde tutarlı. Sıra yine önerilir: gömülü `dosyalar` sha'sı ve `modul_ad` adları F7b'nin son hâliyle uyuşsun. Geri yükleme sonrası sha aynı. |
| 6 | Bütünlük, güvenlik | Depoda `carpisma_kos.py kontrol`, `regresyon.py --yazma`; `SPB/ad_tara.py`; yol deseni | **GEÇER.** Çarpışma rc 0 (17 özet aynı). Regresyon rc 0, GEÇER. `git status` öncesi ve sonrası aynı; silinen izlenen dosya 0. Takma ad 0 (sayfa, üretici, şablon, doğrulama, günlük, `rehber-veri.js`, B'nin DOM dökümü). Yerel kullanıcı yolu 0. |
| 7 | Günlük | §3 baş kısmı, §7, §8, §10 okundu | **GEÇER.** D-4: 3. satır kural dışı silmeyi doğru anlatıyor. D-3: brief listede. D-5: KT-F9b-4'te `README.md:21`, `proje-plani.md:235`. D-7: KT-F9b-3'te K3 çakışması ve kalem 33 / 36 / 78. §10'daki komut çıktıları B'nin koşularıyla aynı. |

### D-8 (düşük). Sayfa depo dışında açılınca yedek metin yanlış nedeni söylüyor

Yer: `TPL:141` (`.fallback` metni) ve `TPL:293` (`model-yok` dalı aynı `nogl` görünümünü kullanıyor).

Kanıt: `SPB/cdp_yalniz/b-360-model.png`, `SPB/cdp_yalniz/cdp_rapor.json`. HTML tek başına açıldığında `data-hazir="model-yok"` oluyor ve konsolda 3 hata çıkıyor. Görünen metin internet ve WebGL'i suçluyor.

Öneri (engel değil):
- `model-yok` durumunda ayrı metin göster: "Model dosyaları bulunamadı: sayfa depo içinden açılmalı (`tasarim/` ile `rehber/` yan yana)."
- Model notuna da "sayfa depo yapısı içinde açılır" ekle.

Kabul ölçütü (depo içinde `file://`, konsol 0) sağlanıyor.

### D-9 (düşük, bilgi). D-1'in kalanı

Yer: `F9b-dogrula.py:201` (`SAYI`), `:211-219`, `:63` (`UI_SAYILI`). Brief sayıları hataya çevrildi, `eski` / `duzeltme` muafiyeti kapandı. Hâlâ geçen dört durum var:
- harfe bitişik sayı;
- `title` özniteliği;
- `data-ui="secim"` (statik sayfada herhangi bir öğeye eklenebilir);
- brief listesinde olmayan anahtarın başka yola bağlanması (`p_satin_bom` → `Baski.adet`).

Bugünkü sayfada bunlardan yararlanan sayı yok (B'nin DOM taraması). İsteğe bağlı iyileştirmeler:
- `secim` muafiyetini yalnız `#info` öğesine sınırla;
- `p_satin_bom` için `p_satin − p_satin_bom` = "(" kodlu katı sayısı denetimi ekle.

## C için kesin `git add` listesi (tek blok, 18 dosya)

`lale158-model.js` listeye girmez. B, durumdaki her yolun ya bu listede ya da dışlamada olduğunu `comm` ile denetledi (`SPB/st2_all.txt` ↔ `SPB/ekle2.txt`; eksik 0). F9b ile ilgili dışarıda kalan tek yol `tasarim/cad/lale158-model.js` (artık).

```
git add tasarim/Robot-Tasarim-Demosu.html tasarim/cad/demo_uret.py tasarim/cad/viewer-template.html \
  planlama/d158/F9b-brief.md planlama/d158/F9b-gunluk.md planlama/d158/F9b-kontrol.md \
  planlama/d158/F9b-dogrula.py planlama/d158/F9b-envanter.py \
  planlama/d158/F9b-goruntu-1400-ust.png planlama/d158/F9b-goruntu-1400-yan-seffaf.png \
  planlama/d158/F9b-goruntu-1400-modul-on.png planlama/d158/F9b-goruntu-1400-korunan-eklem.png \
  planlama/d158/F9b-goruntu-1400-baski-maliyet.png planlama/d158/F9b-goruntu-1400-kararlar.png \
  planlama/d158/F9b-goruntu-360-ust.png planlama/d158/F9b-goruntu-360-model.png \
  planlama/d158/F9b-goruntu-360-eklem.png planlama/d158/F9b-goruntu-360-maliyet.png
```

**Sıra:**
1. F7b'nin C commit'i önce girer (`rehber/veri/robot.glb`, `robot-glb.js`, `rehber-veri.js`, `rehber-veri.json` dahil).
2. Ardından F9b'nin C'si `py -3 tasarim/cad/demo_uret.py` ve `py -3 planlama/d158/F9b-dogrula.py` koşar → 0.
3. F7b'nin son hâli 17:54'ten farklıysa sayfa baytları değişir; çünkü gömülü `dosyalar` sha'sı ve `glb_ref` / `glb_kablo` / `rehber_adim` değerleri oradan geliyor. O zaman yeni sayfa eklenir ve `--goruntu` gerekmez. Sayı değerleri değiştiyse B'ye haber verilir.

**Dışlama:**
- `tasarim/cad/lale158-model.js`: artık. Silinmesi ya da `.gitignore`'a alınması C'nin ya da Ahmet'in kararı.
- F7b: `rehber/`, `planlama/rehber/`, `tasarim/freecad/rehber/`, `planlama/d158/F7b-*`.
- `planlama/dongu-158.md`, `planlama/d158/FREECAD-KILIT.txt`, `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`.
- `tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`.
- `kvkk/`, `rapor/`, `raporlar/`, `tubitak-2209b/`, `tasarim/solidworks/`.

C'ye not:
- Checkout, reset ya da stash yapılmamalı (LF/CRLF).
- Commit'ten sonra `F9b-dogrula.py` ve `carpisma_kos.py kontrol` → 0.
- `main`'e birleştirme yok (KT-F9b-1).

**Commit mesajı önerisi (tek satır, b seçeneğine göre):**
`Lale P9.2: demo sayfası 1,58 m sayılarıyla (demo_uret.py → 127 JSON anahtarı, 3B model rehber GLB'sinden göreli bağlantıyla, 14 açık karar "karar bekliyor", maliyet 118.666,22 TL); F9b-dogrula.py (F9b)`

## Kanıtlar (yeniden kontrol)

```
diff -u SPB/kopya ↔ SPB/kopya2 (üretici, şablon, doğrulama)          → yalnız O-1, O-2, D-2, D-1/D-6 ve göreli model değişiklikleri
SPB/kopya2: demo_uret.py                                            → rc 0; sayfa = depo (cmp, 9613ce541bb3); lale158-model.js oluşmadı
SPB/kopya2: F9b-dogrula.py (Chrome, -X utf8 yok, çıktı dosyaya)      → rc 0, GECER; 127 / 130; DOM 1.638 bağlı, 0 bağsız; işaretler 33 / 36 / 78
SPB/b_bozma2.py (16)                                                → 12 yakalandı, 4 geçti (D-9); geri yükleme sha'ları aynı
SPB/kopya2 + HEAD rehber-veri.js/.json → F9b-dogrula.py --tarayicisiz → rc 0 (O-3 kapandı); geri yüklendi
SPB/b_cdp3.py 1400 / 360 / 390 px (depo yapısında)                   → konsol 0, data-hazir 1, taşma 0; kalem 33 / 36 / 78 görüntüleri
SPB/b_cdp.py, yalnız HTML ayrı klasörde                              → model-yok, konsol 3 hata, yedek metin yanlış neden (D-8)
py -3 tasarim/freecad/carpisma_kos.py kontrol (depo)                → rc 0
py -3 planlama/d158/regresyon.py --yazma (depo)                     → rc 0, GEÇER; git status aynı
SPB/ad_tara.py                                                      → takma ad 0; yerel yol 0
```
