**KAYNAK GEÇER** (üretim adımına geçilebilir; düzeltme turu 2 kapandı. Kayıttan rehbere tamlık okumasında iki yeni boşluk bulundu: G07 ile akü ölçüm direnci ve SV3 ile dağıtım kartı C. İkisi de güvenlik zincirini kesmiyor ya da yanlış bağlatmıyor. Fiziksel montajdan önce kapanması gereken açık iş olarak gidiyor, § 3.1)

# F10h dördüncü bağımsız kontrol: P10.7b1 düzeltme turu 2 (§ 13), kaynak düzeyi, kayıt → rehber tamlığı

- Tarih: 2026-11-14, 11:58–12:17 (saat okundu). Dal `lale-duzeltme`, HEAD `8134519`; değişiklikler çalışma ağacında.
- Yöntem: kaynağın taze kopyası geçici klasörümde (`planlama/adim3`, `tasarim/freecad/rehber`, `montaj-analiz.json`, `taban-analiz.json`,
  `rehber/app.js`, `yazdir.html`, `stil.css`). Komutlar `py -3 -B -X utf8` ve `PYTHONDONTWRITEBYTECODE=1` ile koştu. Çözülmüş metni
  `rehber_denetim.kaynak_metinler()` ile kopyadan ürettim: 531 alan, 1130 satır. Bozmaları bellekte ya da kopyada yaptım. Depoda yalnız
  okuyan koşular koştu. FreeCAD, `rehber_uret.py` ve başsız tarayıcıyı ben koşmadım. Boş bellek 3043–4174 MB arasındaydı.
- Ajanın § 13 iddialarını ve önceki üç kontrolün "doğru" dediklerini temel almadım. Her sayıyı yeniden ölçtüm.
- **Gözlem:** Bakış sırasında depoda `rehber_uret.py` koşuyordu. 12:03'te başlamış, ben başlatmadım. `rehber/veri` 12:06'da, FreeCAD
  kilidi 12:06'da, `planlama/rehber/goruntu/*.png` 12:10–12:11'de yeniden yazıldı. Bu yüzden "rehber çıktıları değişmedi" sınaması bugün
  anlamlı değil. Benim depo koşularımdan önce ve sonra onay kaydının, `kablolar.json`, `kablolar.md` ve `elektrik.md`'nin SHA-256 değeri
  aynı kaldı, `__pycache__` oluşmadı. Değişen tek şey o koşunun PNG'leri.

## 1. Kısa sonuç

Ajanın sayıları tutuyor: tamlık 65 öğe, eksik 0, muaf 21; onay kaydı 1130 girdi (907 / 133 / 90); bozma 76 / 76, 145, 27 / 27; çizilen
51, çizilmeyen 23; durum 20 / 53 / 1. K1 madde 2 ve 8 artık kayıtla birebir: anahtarlı baranın 3 adet kırmızı 12 AWG köprüsü yer
tutucudan geliyor, "yalnız" kalktı, yeni kontrol maddesi doğru. Onay kaydı artık her cümleyi tutuyor: önceki kontrolün tamamen kaçan 5
bozmasını ve benim 7 yeni bozmamı yakaladı. Bozuk, boş ya da eksik kayıtta düzgün ileti veriyor, traceback yok.

Asıl işte, yani kayıttan rehbere tamlık okumasında, sınamanın sayamadığı iki boşluk çıktı. Sınama ikisini "geçiyor" sayıyor:

1. **G07 akü ölçüm hattı ve kayıtlı koruyucusu `R-aku-olcum`** (kaynak ucundaki 100 kΩ): rehberde bağlama talimatı hiç yok. Kimlik yalnız
   "Teslimde bakılacaklar" notunda geçiyor.
2. **SV3 (XL4016 C → dağıtım kartı C) ve dağıtım kartı C'nin kendisi** (2200 µF dahil): rehberde yok. Kimlik yalnız aynı teslim notunda
   geçiyor. K1 madde 7 "servo … kafa hattının taban kısmını bağla", K2 madde 2 de "hat C" diyor, ama C hattının ne olduğu yazılı değil.

İkisi de güç yolunu ya da acil stop zincirini kesmiyor ve yanlış bağlatmıyor. G07 bir ölçüm hattı. SV3 için rehber genel bir talimat
veriyor ve ayrıntıda kablolar.md'ye gönderiyor; bu kontrolün kaydedilmiş bir çelişkisi yok. Montajcı yine de rehberden bu iki hattı
kuramaz. Bu yüzden ikisi açık işlerin başında (§ 3.1).

## 2. Üretimden önce düzelmeli

Yok. Gerekçe: bulduğum boşlukların hiçbiri montajcıya yanlış iş yaptırmıyor ve hiçbiri gerekli bir güç ya da güvenlik bağlantısını
yasaklamıyor ya da atlatmıyor. Önceki kontroldeki "yalnız" gibi, eksikliği yanlış bir talimata çeviren bir cümle yok. Üretimi kıracak kod
hatası ve gizlilik sorunu da yok. Tek tek gerekçeler § 3'te.

## 3. Kayıtlı açık iş

### 3.1 Tamlık okuması: kayıt → rehber (yeni boşluklar; montajdan önce kapanmalı)

1. **G07 / `R-aku-olcum`: akü ölçüm hattının bağlama talimatı yok.**
   - Kayıt: `planlama/adim3/kablolar.json` `koruyucular.R-aku-olcum` (tür `direnc`, giriş `ana-anahtar-cikis`), kablo G07
     (`kablolar.md:794`, sonlandırma "kaynak ucunda 100 kΩ telin başına lehim + makaron"), `dallar.aku-olcum`, pin haritası `AKU_ADC`
     (GPIO36).
   - Rehber: çözülmüş metnin 1130 satırında G07 tek yerde geçiyor, `rehber_metin.py:327-328` "Teslimde bakılacaklar … (A06 / G07 lehimli
     uçlarına yeniden bakılır)". "akü ölç", "100 kΩ", "GPIO36" hiçbir yerde yok. F1 ana anahtara yalnız "iki ana hat ucunu" bağlatıyor
     (`:721`); G07 de ana anahtarın çıkış saplamasına gider.
   - Montajcı ne yapar: hattı kurmadan geçer, ESP32'nin akü girişi yüzer. Kendi kafasına göre kurarsa 100 kΩ'u kart ucuna koyabilir; o
     zaman 22 AWG tel yalnız ana sigortanın (30 A) arkasında kalır. Zincir kesilmez: ölçüm kaybı olur, ama koruyucusu kayıtlı bir hat
     rehberde hiç yok.
   - Tamlık sınaması bunu neden görmüyor: koruyucu ölçütü yalnız tür "sigorta" olanlara bakıyor (`rehber_denetim.py:1019-1021`). Kablo
     kimliği ölçütü kimliğin herhangi bir cümlede geçmesini yeterli sayıyor (`:999`, `:1059`); teslim notu bunu karşılıyor.
   - Öneri: K1 madde 4'e bir cümle eklensin: "Akü ölçümü (G07, {awg.G07}): ana anahtarın çıkış saplamasından, 100 kΩ telin başında
     (kaynak ucu) lehim + makaron → arayüz kartı akü bölücüsü". F1'de "iki ana hat ucu"nun yanına G07 eklensin. Devre değeri değişmez.
2. **SV3 ve dağıtım kartı C: kafa servo hattı C'nin rehberde karşılığı yok.**
   - Kayıt: `kablolar.json` SV3 (`kablolar.md:641`; XL4016 C OUT → dağıtım kartı C girişi, 16 AWG, koruma XL4016-C), `kondansatorler`
     (dağıtım kartı C'de 1 × 2200 µF), `pertinaks_parcalari` ("dağıtım kartı C"), `klemens_yerleri` (dağıtım kartı C · SV3 girişi),
     `kablolar.md:658`.
   - Rehber: "dağıtım kartı C" hiçbir yerde yok. B6a "2 dağıtım kartı" diyor. SV3 yalnız `:327-329` teslim notunda (T8 E denemesi) geçiyor.
     XL4016 C'nin çıkışı hiçbir yerde bağlanmıyor: B5a `:209` yalnız yerini, K1 madde 3 `:272` yalnız girişini veriyor. K2 madde 2 `:657`
     "Kafa servoları: hat C → direk üstü R62". Sinyal tarafı P03 zaten bilinen eksikler arasında.
   - Montajcı ne yapar: K1 madde 7 ("servo … kafa" taban kısmı) ile kablolar.md'ye bakarsa kurar. Yalnız rehberle kuramaz ve baş servoları
     beslemesiz kalır. Güvenlik zinciri etkilenmez; S09 / S10'u A ya da B kartına takarsa yük hat sigortalı bir hatta kayar.
   - Öneri: B5a ya da K1 madde 3'e şu eklensin: "XL4016 C çıkışı → dağıtım kartı C (SV3, {awg.SV3}; kartta 2200 µF, kutbuna dikkat; S09 /
     S10 buradan)". Gerekirse dağıtım kartı C B5a parça listesine de girer.
3. **Tamlık sınamasının ölçütü "anılış", "talimat" değil.** Kopyada, bellekte denedim (§ 5.1):
   - T13: K1 madde 3'teki hat sigortası talimatı silindi, F1 / F5'teki "tak" anılışı kaldı. Sınama sessiz kaldı.
   - T14: G07'nin tek anılışı silindi. Sınama sessiz kaldı; sonuç yalnız bilgi satırında görünüyor.
   - T5: A04'ün bütün tekil anılışları silindi. Sınama sessiz kaldı, çünkü "A01–A05" / "A01–A06" aralıkları A04'ü sayıyor
     (`rehber_deger.py:232-238`).
   - T11: kayda tür `direnc` yeni bir koruyucu eklendi. Sınama sessiz kaldı.
   - T12: kayda anahtarlı baraya bağlı yeni bir güç kablosu eklendi. Sınama sessiz kaldı; kablo yalnız bilgi listesine düşüyor.

   Bugün metin değişikliklerini onay kaydı tutuyor (T13 / T14 / T5 onay farkı verir). Kayda yeni öğe eklenmesi ise (T11 / T12) yalnız
   "sigorta / köprü / saplama / GPIO / anahtar / acil stop kablosu" türlerinde hata veriyor. Öneri:
   - koruyucu ölçütü `tur != "bms"` olacak biçimde genişlesin (dönüştürücü / sürücü için ad, direnç için kablo kimliği);
   - güç sınıfı kabloların (devre ≠ sinyal) kimliği bilgi değil hata sayılsın;
   - teslim / not alanlarındaki anılış sayılmasın;
   - acil stop kablosu aralıkla değil tekil kimlikle aransın.
4. **Sinyal ve kart içleri (bilinen muafiyetle aynı sınıf).** X01 (arayüz kartı ↔ ESP32: röle sürücü girişleri, PC817 çıkışları, 5 V),
   B01, B02 yalnız şema yazısında (KABLO_AD 11 / 12) geçiyor. N01, N02, Q01–Q03 için yalnız "Enkoder ve sonarları bağla" (`:290`) var.
   Kart içleri (arayüz kartının bölücüleri, BTS EN 10 kΩ → GND, ön şarj kartının iç bağı, dağıtım kartlarının 2200 µF'ı) rehberde yapım
   talimatı olarak yok. Hepsinde hata güvenli yöne düşer: K1 çekmez ya da motor dönmez. Bunlar P10.7b2'deki "21 muaf ve 6 kablo" kararına
   eklensin.

### 3.2 Montajcı okumasındaki öbür ayrıntılar (düşük)

1. **P6KE18A'nın kutbu yazılı değil.** `rehber_metin.py:470-471`: P6KE6V8A için "katot (çizgili uç) +5 V'a" var, kafa giriş kartındaki
   P6KE18A için yok (`elektrik.md:282` de yazmıyor). Ters takılırsa F3 5 A ilk enerjide atar. Öneri: aynı cümle "+12 V'a" diye eklensin.
2. **K2'nin hangi kontağı (COM–NO) kullanılacağı yazılı değil.** JQC-3FF'te NC ucu da var. `elektrik.md:437-446` davranışı tarif ediyor
   ("yalnız devreye alma anında kapalı"), pini adlandırmıyor; rehber yalnız "K2 kontağı" diyor (`:270`). NC'ye bağlanırsa bara 5,6 Ω
   üzerinden acil stoptan bağımsız beslenir. F5 dizisi (GPIO5 teyidi) ve "mantara basınca bara kesildi" kontrolü bunu yakalar. Öneri:
   kayda ve rehbere "COM → NO" yazılsın (orkestratör kararı; devre değişmez).
3. **Hat sigortası A / B / C'nin kablo üstündeki yeri** kayıtta yazılı değil (`koruyucular.hat-A` adı "XL4016 A girişi"; G22 için "bara
   ucunda", çevre için "OUT+ dibinde" yazıyor). Kesit sınaması 16 AWG'nin bütün boyunu 7,5 A'le korunmuş sayıyor; sigorta XL ucuna
   konursa baradan sigortaya kadarki parça F1 20 A'in arkasında kalır. Rehber kaydı izliyor, uydurmuyor. Öneri: kayda "bara ucunda"
   yazılsın (orkestratör kararı).
4. **F1'de mantarın ikinci ucu ve G06'nın anahtar ucu.** F1 madde 3 (`:719`) ve alt adım 7 (`:802`) "K1'de bırakılan ucu" diyor, tekil.
   Mantara iki uç gider (A01 giriş, A02 çıkış); F1 kablo satırı ikisini de sayıyor. K1 madde 1 G06'nın + ucunu "ana anahtarın giriş
   saplamasına (G03 ile aynı)" diyor, ama anahtar F1'de takılıyor ve F1 yalnız "iki ana hat ucu"nu bağlatıyor (`:721`). Hata güvenli
   yönde: A02 eksikse K1 çekmez; G06 eksikse şarj olmaz. Öneri: F1'de "A01 ve A02'yi NC uçlarına", "G03 ile G06'nın + pabucu giriş
   saplamasına, G04 (ve G07) çıkış saplamasına" yazılsın.
5. **A06'nın − ucu** (PC817 #1 girişi − → arayüz kartı GND pedi; `kablolar.json` A06 sonlandırma) rehberde yok (`:283`). Hata güvenli
   yönde: GPIO23 sürekli "mantar basılı" okur ve devreye alma ön koşulu geçmez.
6. **Aynı yandaki iki motorun aynı M+ / M− klemensine paralel bağlanması** (M01–M04 sonlandırma) rehberde yazılı değil. B3 yalnız "motor
   çıkışı" diyor. F5 yön testi yakalar.

### 3.3 Düzeltme turu 2'nin kendisi

1. **K1 madde 2 ve 8 tabloyla birebir.** `rehber_metin.py:259-269` ve `:293-297` ham metinde yer tutucuyla yazılı. Çözülmüş hâlinde iki
   bara ayrı ayrı yazılı:
   - yıldız barası: 5 saplama, 4 adet siyah 12 AWG köprü, ≈ 50 mm;
   - anahtarlı bara: 4 saplama, 3 adet kırmızı 12 AWG köprü, ≈ 50 mm.

   Kayıt `klemens_turleri.bara-pabuc.kopruler` ile aynı. Bağlantı satırı (`:302-304`) 7 köprü ve 14 sarı pabuç diyor (14 = 2 × 7, kayıttaki
   `pabuc` notuyla aynı). "yalnız" kalktı. Madde 8 artık bir yasak değil, liste ("Bu adımda takılan köprüler …"). Ardındaki "Bunların
   dışında mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez" cümlesi listeyi kapatmıyor, yalnız iki şeyi yasaklıyor.
   Doğru.
2. **Yeni kontrol maddesi** (`:316-318`): adet ve renk yer tutucudan geliyor; "ilk ve son saplama arası öter" zincirdeki her köprüyü seri
   sınar. Doğru (gevşek bir köprüyü ayırt etmez, beklenen).
3. **Anahtarlı baranın yerleşimi uydurulmamış.** Kayıtta `besleme_saplamasi: null`, `yerlesim` yok. Rehber bunu söylüyor ve "serbest"
   sonucunu `ilke` cümlesine dayandırıyor. Benim hesabım:
   - 4 saplamalı zincirde köprü pabuçları 1 / 2 / 2 / 1, boş yer 3 / 2 / 2 / 3 = 10. Baraya giden iletken 8: G09, G11, G12, G13, G14, G15,
     G16, G22. K1 madde 3 sekizini de "→ anahtarlı bara / Baradan" diye sayıyor.
   - Saplama başına en çok 4 pabuç kuralına uyan her dağılım sığar.
   - En kötü dağılımda köprüden F1 akımı (20 A) geçer; aynı sigortanın arkasındaki 12 AWG G08–G13 kesit sınamasından geçiyor.

   Kural yetiyor. "Serbest" bir çıkarım; kayıtta açıkça yazılırsa daha iyi olur (açık iş, ajan da bildirmiş).
4. **Sözcük tuzağı taraması** (çözülmüş metinde "yalnız / tek / sadece / hiçbir / ancak / dışında": 41 geçiş, hepsini okudum). Yeni bir
   yasak + eksik liste yok. Düşük öneme sahip iki tane var:
   - K1 madde 5 son paragraf (`:287-289`): "burada yalnız B3'te etiketli bırakılan öbür uçları bara, sigorta kutusu ve hat sigortalarına
     bağla". Hedef listesinde yıldız barası, dağıtım kartları A / B ve arayüz kartı (G19) yok. "Yalnız" burada "alt kata uzanma"
     anlamında, K1 kontrolü de "boşta uç kalmadı" diyor. Öneri: liste tamamlansın ya da "yerlerine (kablolar.md)" yazılsın.
   - K1 kontrol (`:324-325`): "düğüm için vidalı klemens yalnız iki küçük kartta". Kayıtta arayüz kartının çevre 5 V düğümü de klemensle
     giriyor (`klemens_yerleri`). Bağlam ana hat ve toprak düğümleri olduğu için yanlış iş yaptırmıyor.
5. **YASAK daraltması gerçek talimatı kaçırıyor** (`rehber_denetim.py:358`). Kopyada denedim:
   - Kaçanlar (3): "mantarın iki ucunu kısa bir telle **köprüler**" (Türkçede geniş zaman fiili, ad değil), "ana anahtarın iki ucunu
     baradaki **köprülere** bağla", "ana anahtarın uçlarına **köprüler takılır**". Eski kural üçünü de yakalıyordu.
   - Daraltmadan önce de kaçan: "mantarın iki ucu arasına bir köprü takılır".
   - Eski kural bugünkü metinde 4 yanlış alarm veriyordu, daraltmanın nedeni bu.

   Bugün bu biçimleri onay kaydı yakalıyor (her cümle kayıtta). Öneri: çoğul ad yalnız aynı yan cümlede `_KOPRU_NESNE` (mantar, NC, ana
   anahtar, sigorta, röle, kontak) yoksa affedilsin.
6. **Kayıtta köprü adedi değişirse** (anahtarlı bara 3 → 4, kopyada) `--kaynak` çıkışı 0 oluyor. Bu tasarım gereği: metin yer tutucudan
   kendiliğinden güncelleniyor, onay kaydı ham metni tutuyor. Adedin saplama sayısıyla tutarlılığı (n − 1) kablo tablosunun işi. Ona
   bakmadım.

### 3.4 Onay kaydı ve `rehber_uret.py` ön sınaması

1. Kapsam bütün metin: 907 metin girdisi, 531 alanın bütün cümleleri. Yalnız boşluk değişikliğini (Y8) bilerek tutmuyor (`normal()`).
   Zararsız.
2. `on_sinama()` (`rehber_uret.py:525-547`, çağrı `:562`): argümanlar okunduktan sonra, `veri()`, FreeCAD ve tarayıcıdan önce çalışıyor.
   - `kaynak_denetle()`'nin `gecti` alanı onay farkını ve tamlığı içeriyor (`rehber_denetim.py:1352-1353`).
   - Her istisna "URETIM DURDU" iletisi ve çıkış 1 veriyor; `KayitHatasi` da buna dahil. Kullandığı anahtarların hepsi dönüş sözlüğünde
     var.
   - İçe aktardıkları yalnız standart kitaplık ve depo modülleri: `rehber_denetim`, `rehber_metin`, `rehber_deger`, `rehber_kritik`,
     `rehber_kablo`.
   - Bu sekiz dosya Python 3.11 sözdizimiyle ayrıştırılıyor (`ast.parse(feature_version=(3, 11))`): `rehber_uret.py`, `rehber_veri.py`
     (FreeCAD altında koşan), `rehber_metin.py`, `rehber_deger.py`, `rehber_kritik.py`, `rehber_kablo.py`, `rehber_denetim.py`,
     `rehber_kol_kablo.py`.
   - `rehber_uret.py` sistem Python'uyla koşuyor; FreeCAD yalnız `rehber_veri.py`'yi alt süreçte açıyor (`:57`).
   - Mantık doğru. Koşulduğunu görmedim (§ 6).

## 4. Üretim adımında bakılacaklar

1. Şu anda koşan `rehber_uret.py`'nin ilk satırı "on sinama: kaynak denetimi gecti, onay kaydi tutuyor (kablo 90, liste 133, metin
   907)" olmalı; koşunun günlüğüne bakılsın.
2. § 3.1-1 ve -2 kapatılırsa onay kaydı yenilenir; yalnız K1 madde 3 / 4, F1 ve B5a cümleleri değişmeli. Fark bağımsız kontrole gider,
   rehber yeniden üretilir.
3. K1 karesinde iki bara ve 7 köprü cümlesi panelde ve basılı sayfada sığıyor mu bakılsın.

## 5. Kendi ölçümlerim

### 5.1 Tamlık okuması tablosu (kayıt → rehber; kendi okumam, sınamanın sayımı değil)

| Öğe türü | Kayıtta | Rehberde açık talimat | Eksik |
| --- | --- | --- | --- |
| Koruyucu, tür sigorta (ana, F1, F3–F6, hat A / B / C / G22 / şarj / çevre) | 12 | 12 (bağla + tak; hat A / B / C'de kablo üstündeki yeri yok, kayıtta da yok) | 0 |
| Koruyucu, öbür türler (BMS 1, dönüştürücü 6, BTS 2, direnç 1) | 10 | 9 | 1: `R-aku-olcum` (G07) |
| Köprü (bara köprüleri 2 takım / 7 adet, kart üstü tel köprü 2 kart, Ö4, KT3 ara kabloları) | 6 | 6 | 0 |
| Saplama düğümü (yıldız 11 iletken, anahtarlı bara 8 iletken) | 19 | 19 (anahtarlı barada yerleşim kayıtta yok, rehber "serbest") | 0 |
| Saplama: ana anahtar giriş (G03 + G06) / çıkış (G04 + G07) | 4 | 2 (F1: "iki ana hat ucu") | 2: G06'nın + ucu (K1'de yazılı, F1'de yok), G07 |
| Röle (K1 30 → 87, 86 / 85; K2 bobin + kontak) | 2 | 2 (K2'de COM–NO yazılı değil, kayıtta da yok) | 0 |
| Sürücü BC337-40 + 270 Ω / 2,2 kΩ | 2 | 2 | 0 |
| Diyot / TVS (1N4007 × 2, 1N5819, P6KE6V8A × 2, P6KE18A) | 6 | 6; kutup 5'inde yazılı | 0 (P6KE18A kutbu yok) |
| PC817 girişleri (#1 A06, #2 G22) | 2 | 2 (A06'nın − ucu yok) | 0 |
| Anahtar ve acil stop zinciri (ana anahtar, mantar NC, A01–A06, Ö4, düğüm kartı) | 10 | 10 (F1'de mantar ucu tekil) | 0 |
| Ön şarj (K2 + 5,6 Ω, G10 / G11, yükseklik, E9 dizisi) | 1 | 1 | 0 |
| Şarj kolu (G06, hat sigortası, XT60E-M, takılmaz) | 1 | 1 | 0 |
| İki bara, kafa giriş kartı, acil stop düğüm kartı | 4 | 4 | 0 |
| Dağıtım kartları (A, B, C) | 3 | 2 (A / B yalnız yer olarak) | 1: dağıtım kartı C |
| Kondansatör 2200 µF (A 2, B 2, C 1) | 5 | 0 | 5 (kart içi, § 3.1-4) |

Tamlık sınamasının sayımı (depoda ve kopyada aynı): taranan 65 (koruyucu 12, köprü 2, saplama düğümü 13, GPIO rolü 24, anahtar 5, acil
stop zinciri 9), eksik 0, muaf 21. Sayım doğru; eksik 0 sonucu ise sınamanın baktığı türlerle sınırlı.

### 5.2 Kablolar: rehberde bağlanacağı yer belli mi (74)

| Sınıf | Adet | Kablolar |
| --- | --- | --- |
| Kimliğiyle ya da iki ucuyla bağlama talimatı var | 59 | G01–G06, G08–G22, A01–A06, M01–M04 (B3), SV1, SV2 (B3 + şema), S01–S10, K01–K05, U01, U03–U06, H01, H02, C01 (E4: "CSI şeridi → Pi"), AU1–AU3 |
| Yalnız şema yazısı ya da genel "bağla" | 8 | X01, B01, B02, N01, N02, Q01, Q02, Q03 |
| Hiç talimat yok | 7 | **G07, SV3 (yeni)**; I01, I02, P01, P02, P03 (bilinen, § 8 / § 13.2) |

- Sınamanın "kimliğiyle geçmeyen 6" listesinde C01 var, ama E4 madde 4 onu iki ucuyla bağlatıyor. G07 ve SV3 listede yok, çünkü teslim
  notunda anılıyorlar. Gerçek boşluk 7.
- Çizilmeyen 23 kablonun listesi (`rehber_kablo.cizim_tablosu`) G07 ve SV3'ü içeriyor. Orada bilinen eksik şema; metin eksikliği ise
  yeni.

### 5.3 Denemeler (kopya, bellekte ya da kopya dosyada; her dosya denemesinden sonra SHA-256 değeri geri doğrulandı)

| Takım | Deneme | Sonuç |
| --- | --- | --- |
| Tamlık, beklenen hata | 11 (T1–T4, T5c, T6–T10, T5b) | 11 / 11 hata: anahtarlı bara köprüsünün bütün anılışları silindi; `{a.hat-G22}` yok; `{saplama.G17\|G18}` yok; ROLE_K2_ONSARJ yok; A04 aralıklar dahil yok; kayda hat-D sigortası; yeni köprü takımı; pin haritasına ROLE_K3; yeni anahtar; yıldız yerleşimine G23; "K2 bobini (+; A04)" silindi |
| Tamlık, kör nokta | 5 (T5, T11–T14) | 5'i de sessiz (§ 3.1-3) |
| Onay kaydı: önceki kontrolün kaçan 5'i | N01b, N03, N05, N07, N11 | 5 / 5 fark (1, 1, 1, 1, 2) |
| Onay kaydı: yeni | 8 | 7 / 7 fark. Y1 F1 "kapalıyken" → "açıkken"; Y2 F3 güvenlik cümlesi silindi; Y3 E3a'ya cümle eklendi; Y4 K1 kontrol sırası; Y5 F5 kontrol maddesi silindi; Y6 cümle iş metninden nota taşındı; Y7 "kısa devre yok" → "var". Y8 (yalnız boşluk) 0, bilerek |
| Kayıt dosyası (`--kaynak` / `rehber_kablo.py`) | 9 durum × 2 | Dosya yok, bozuk JSON, boş, `{}`, bölümler boş, metin bölümü yok, girdide `ozet` yok, bölümler liste, UTF-16: hepsinde çıkış 1, traceback yok, düzgün ileti ya da fark sayısı. Kopyada `rehber_kablo.py` kol modülü olmadığı için zaten 1 çıkıyor; onay satırı "1 fark / 90 fark", traceback yok |
| Kablo tablosu | 3 | B22 (hat-G22 adı): çıkış 1, düzgün ileti. Anahtarlı bara köprü kaydı silindi: çıkış 1 (çözülemeyen 15). Adet 3 → 4: çıkış 0 (§ 3.3-6) |
| YASAK | 9 | Fiil biçimleri ve "köprülerse" / "köprülerle birleştir" / "köprülendi" yakalanıyor; iki meşru cümle sessiz; 3 gerçek talimat kaçıyor (§ 3.3-5) |

Toplam 58 deneme. Temiz kaynakta yanlış alarm 0 (tamlık 0, onay 0).

### 5.4 Koşular (depoda, yalnız okuyan, 12:10–12:11)

| Koşu | Çıkış | Sonuç (ajanın iddiasıyla) |
| --- | --- | --- |
| `kablolar_uret.py --kontrol` | 0 | "kablolar.md ve elektrik.md bloğu güncel": aynı |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / toplam bozma 145, GEÇER: aynı |
| `rehber_denetim.py --kaynak` | 0 | metin 531 (+ CAD 893, arayüz 552), bütün kalemler 0, onay farkı 0 (kablo 90, liste 133, metin 907); tamlık 65 / eksik 0 / muaf 21; kimlik 68 / 74 (I01, I02, P01, P02, P03, C01): aynı |
| `rehber_denetim.py --bozma-denemesi` | 0 | 76 / 76, bozulmamış kaynakta 0: aynı |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER; 74 / 51 / 23; geometri hata 0, bilgi 4; ayırt edilemeyen 1 (A03 ↔ G22); onay tutuyor / 27 / 27: aynı |
| `node --check rehber/app.js` | 0 | aynı |

Durum sayıları (`kablolar.json`): kesin 20, teyit 53, karara bağlı 1. Ajanın iddiasıyla aynı.

### 5.5 Sınırlar ve gizlilik

- `kablolar.json` HEAD'e göre: 74 kimlik aynı. Kablo alanlarında yalnız `teyit` 23, `durum` 11, `sonlandirma` 5 değişmiş. `uc_a`, `uc_b`,
  `kesit`, `koruma`, `acil_stopta_enerjili`, `devre`, `damarlar`, `renk`, `besleme_zinciri` değişmemiş. `koruyucular`, `anahtarlar`,
  `klemens_turleri` (köprü kayıtları dahil), `aglar`, `dugumler`, `ic_baglar`, `zinciri_kesen_turler`, `dallar`, `kondansatorler`
  değişmemiş. Yalnız metin değişiklikleri var: `klemens_yerleri.yerler[0].not` ("köprülü" → "≥ 18 AWG tel köprülü") ve
  `renk_kurali.ilke` (palet kaynağının adı).
- `pin-haritasi.md`, `kod/`, `tasarim/freecad/taban`, `kafa`, kabuk ve montaj Python kaynakları, `*.FCStd`: HEAD'e göre fark yok.
  Önceki üç kontrol raporunun son değişiklik zamanı 09:26, 10:45 ve 11:36. Rehber çıktıları için § başındaki gözleme bakın.
- Paketin eklediği 1908 satırda ve yeni dosyalarda (günlük, `rehber_deger.py`, `rehber_kablo.py`, `rehber_kritik.py`, onay kaydı; 8940
  satır) şunların hiçbiri yok: yerel kullanıcı yolu, makine adı, e-posta, parola, anahtar, soyad.

## 6. Bakılmadı

- `rehber_uret.py`'nin `on_sinama()`'sının gerçek koşudaki çıktısı. O sırada koşan üretimin günlüğünü okumadım.
- `rehber_kol_kablo.py --yazma`. Yazan bir koşu, bu bakışın sınırı dışında.
- Kopyada `rehber_kablo.py` ana koşusunun kol bölümü (kol modülleri kopyada yok).
- Üretilmiş veri, kareler, PDF.
- Kart içi devrelerin (arayüz kartı, ön şarj kartı, dağıtım kartları) `elektrik.md` ile tam karşılaştırması. Yalnız rehberde yer alıp
  almadıklarına baktım.
- Köprü adedinin saplama sayısıyla tutarlılığını kablo tablosu denetiminin tutup tutmadığı.
