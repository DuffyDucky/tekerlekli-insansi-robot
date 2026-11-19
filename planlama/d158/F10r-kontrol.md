# F10r · P10.7b2i bağımsız kontrol: yol 9 kırpması, U06 şeması, kablo boyları

Kontrol 19.11.2026 (02:00 civarı), dal `lale-duzeltme`, HEAD `8bca2f5`, çalışma ağacındaki fark + `F10r-gunluk.md`. Fark önce kendi
başına okundu, günlük sonra. Kaynak düzeltilmedi; denemeler bellekte ya da yedekten geri yüklenerek yapıldı (aşağıda § 4).

## Karar: **DÜZELTMEYLE GEÇER**

Paketin üç iddiası tutuyor. Kesim geometrisi doğru, yol 12 değişmedi, kaldırılan her kural ya gereksiz hale gelmiş (şema düzeldi) ya da
daha sıkı bir kuralla değiştirilmiş. Sınamalar gerçekten yeşil, yeşile zorla çekilmiş değil. Kapanıştan önce iki küçük iş gerekiyor
(D1, D2). Kalan bulgular düşük önemde, kapanışı durdurmuyor.

## 1. Bulgular (önem sırasıyla)

### D1 · ORTA: sipariş belgesinde artık yanlış olan "1,5 m yeter" notu
- **Yer:** `planlama/d158/F8a-siparis.json:2174` (`S58.not2`) ve `planlama/d158/F8a-siparis.md:344`: "1,5 m (ESP32 yolu 1.360 mm, göğüs
  dokunmatik 640 mm: yeter)".
- **Ne yanlış:** U06'nın önerilen boyu 1.560 mm oldu. 1,5 m'lik alternatif kablo (Robotistan, url2) artık **yetmez**. Birincil ürün 2 m
  olduğu için bugünkü sipariş doğru, ama not hâlâ "yeter" diyor.
- **Senaryo:** Robocombo'da stok biter, biri alternatif sütundaki notu okuyup 1,5 m kablo alır. Kablo ESP32'ye ancak gergin ulaşır ya da
  hiç ulaşmaz. 150 mm kapak söküm payı da kalmaz.
- **Düzeltme:** not2'yi "1,5 m: ESP32 USB'ye yetmez (önerilen 1.560 mm, P10.7b2i); yalnız göğüs dokunmatiğine (640) yeter" yap, `.md`
  satırını aynı biçimde yeniden üret ya da düzenle. `maliyet.json` notu zaten "1,5 m yetmez, 2 m" diyor, değişmesi gerekmez.

### D2 · ORTA (commit engeli): günlükte yerel kullanıcı yolu
- **Yer:** `planlama/d158/F10r-gunluk.md:9`: paralel CAD ağacının tam Windows yolu, kullanıcı adıyla birlikte.
- **Ne yanlış:** Gizlilik. Günlük bunu § 7.e'de kendisi de not ediyor, ama düzeltilmeden commit tarifine giriyor.
- **Düzeltme:** commit'ten önce "paralel CAD ajanının ayrı worktree'si" gibi yolsuz bir ifadeye çevir. Farkın geri kalanında (kod,
  JSON, md) yerel yol, anahtar ya da kişisel bilgi yok (taranan: yerel kullanıcı / bulut klasörü yolları, e-posta, key, token, secret). Bu kontrol
  dosyasında da yok.

### D3 · DÜŞÜK: U06 boyunun eski değeri iki türetilmiş dosyada ve bir notta duruyor
- **Yer:** `tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json` `kablo_listesi["ESP32 USB"]` (971 / 1360; FreeCAD
  `uygulama_olc.py` yazar), `tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md:110` (971 / 1.360), `planlama/d158/kablo-kurali-notu.md:34`
  (971 / 1.360).
- **Ne yanlış:** Aynı boyun ikinci ve üçüncü kopyası. Hiçbir denetim bunları kaynağa bağlamıyor. Regresyon metriği
  (`sy8205_x_usb_mm3`) yalnız kafa içi kesişime bakıyor, taban değişikliğinden etkilenmiyor.
- **Senaryo:** Bir sonraki ajan boyu `uygulama-notu.md`'den okur ve 1.360 mm'yi yeniden belgeye taşır.
- **Düzeltme (kapanışta ya da kuyruğa):** `uygulama-notu.md:110` ve `kablo-kurali-notu.md:34` satırına "→ 19.11 P10.7b2i: 1.129 / 1.560"
  ekle. `uygulama-olcum.json`'u bir sonraki `uygulama_olc` koşusuna bırak ve bunu `karar-kuyrugu.md`'ye yaz.

### D4 · DÜŞÜK: `GEO_ISTISNA` için "kullanılmıyor" denetimi yok (paketten önce de yoktu)
- **Yer:** `tasarim/freecad/rehber/rehber_kablo.py:214` (`GEO_ISTISNA`). `SEMA_GEO_ISTISNA`'nın kullanılmayan istisna denetimi
  `:1272`'de var, `GEO_ISTISNA`'nınki yok.
- **Deneme (K6):** `CAD_KIRP[9]` dururken `GEO_ISTISNA[9]` geri eklendi. Sonuç: kaynak denetimi 0 hata, yalnız onay kaydı yakaladı.
- **Senaryo:** Bayat bir istisna yol 9'un uç hatalarını sessizce örter. Onay kaydı farkı gösterir, ama farkı onaylayan istisnanın
  gereksiz olduğunu göremez.
- **Düzeltme (sonraki paket):** yol, istisnasız da geometri sınamasından geçiyorsa "GEO_ISTISNA n: kullanılmıyor" hatası ver
  (`SEMA_GEO_ISTISNA` ile aynı kalıp), bozması da `GEO_ISTISNA[9]` geri eklensin.

### D5 · DÜŞÜK: U06'nın hangi porta takıldığı geometrik olarak kilitli değil
- **Deneme (K9):** şemanın son iki noktası ESP32'nin −x ucuna (port olmayan uca) taşındı. Şema geometrisi geçti, çünkü uç DevKit
  kutusuna 10 mm'den yakın. Yalnız `sema_boy` (kayıt 1.129, şema 1.177) yakaladı. `--sema-boy-yaz` ile kayıt yeniden yazılırsa bu da
  susar.
- Metin tarafı kilitli: `ZORUNLU` K1 deseni "önden bakınca sağ ucundaki portuna" ifadesini istiyor (sağ → sol bozması yakalandı).
  Şema ile metin arasında bağ yok.
- **Düzeltme (isteğe bağlı):** `ESP32 USB` son noktası için `ESP_PORT`'a ≤ 5 mm şartı, yani `SEMA_GEO`'ya port düzeyinde bir uç.

### D6 · DÜŞÜK: rehber K2 metnindeki boy (1.560) ve `elektrik.md` kaynağa yalnız onay kaydıyla bağlı
- **Deneme:** K2 kablo maddesinde "ESP32 USB 1.560" yeniden 1.360 yapıldı. `rehber_denetim --kaynak` çıkışı 1, ama yalnız "onaylı
  kritik girdi farkı 1" ile. Anlamsal bir kural (metin ↔ `lale158-kontrol.json`) yok.
- Yeni `boy_tazelik` `kablolar.json`'u koruyor (aşağıda). Rehber metni ve `elektrik.md` ise bir sonraki `lale158_kontrol` koşusunda
  eskiyebilir. Bu, b2h'deki 1.360'ın nasıl eskidiğiyle aynı yol.
- **Düzeltme (sonraki paket):** K2 "Önerilen boylar" sayılarını yer tutucuyla (`{boy.U06}` benzeri) kayıttan bas.

### D7 · KOZMETİK: onay kaydında kesimin yazımı yanıltıcı
- **Yer:** `tasarim/freecad/rehber/rehber_kablo.py:1294`. Kayıtta "son 3 kesim yön (0.0, 1.0, 1.0) ≤ 143.921" yazıyor: yön
  normalize edilmemiş, sınır normalize edilmiş yöne göre. Harfiyen okunursa (y + z ≤ 143,9) yanlış. Doğrusu (y + z)/√2 ≤ 143,92, yani
  y + z ≤ 203,5.
- **Düzeltme:** `cad_kirp_metin(n)` kullan ("(0, 0.7071, 0.7071) · p ≤ 143.92"). Onay kaydı bir kez daha yenilenir. İstenirse bu
  pakette yapılır, gerekmezse bırakılır.

### B1 · BİLGİ: ESP32'nin taşıyıcıdaki yönü rehberde yazılı değil
"Önden bakınca sağ ucundaki port" ifadesi, DevKit'in USB ucu +x'te takıldığını varsayıyor (`taban_lib.esp_local`: WROOM −x, port +x).
Rehberde ESP32'nin dişi başlığa hangi yönde takılacağı hiçbir adımda yazmıyor (bu paketten önce de böyleydi). 30 pinli kart 180°
ters de girer, o zaman pin eşlemesi de bozulur. Yeni cümle örtük olarak yönü veriyor. B6a / K1'de "USB ucu sağda (+x)" diye açıkça
yazmak ayrı bir iş.

## 2. İddia bazında doğrulama

**İddia 1: yol 9 kesimi**
- `taban-analiz.json` `kablo_yolu[8]` noktalarının (y + z)/√2 izdüşümü kendi hesabımla: korunan [0..3] 8,84 / 107,48 / 120,21 /
  **141,42**, atılan [4..6] 212,13 / 243,95 / **194,45**. Kesim 141,42 + 2,5 = 143,92 tutuyor. Atılan kürelerin en yakını düzlemin
  48 mm ötesinde.
- Kesilen tek bölüm [3]→[4] segmenti. Düzlemle kesiştiği yer [3]'ten yaklaşık 2,8 mm ötede, yani kalıntı yalnız tüp ucu kadar.
- `rehber_veri.kirp()` dönüş yönü doğru. `R = Rotation(e_y → yon)`. Kutu yerel `y ≤ d` olarak kurulup R ile dönünce
  `yon · (R p) = p_y` olur, yani bölge `yon · q ≤ d`. `_izd` şekli R⁻¹ ile döndürüyor: `(R⁻¹ q)_y = yon · q`, yani izdüşüm doğru.
  +y'de R birim, b2f davranışı aynen. FreeCAD'de yeniden koşmadım: günlükteki yol 12 hacmi ve kesim yüzü (3.944,49 mm³, 81,22 mm²)
  b2f ile aynı.
- Yol 12 değişmedi: `CAD_KIRP 12` onay girdisi farkta yok. Çıktı "yol 12 y ≤ 192.5".
- Bütün atılan noktaların dışarıda kalma şartı (`iceride`) eskisinden sıkı.
- Kendi bozmalarım, hepsi denetim tarafından yakalandı (onaydan ayrı sayıldı):
  - son = 6: 2 hata;
  - son = 5 ve yön +x (eski [4..5] kalır, `cad_kirp_denetle` geçer): `geometri_denetle` yakaladı ("son ucu [40, 185, 160]: parça yok");
  - son = 4 ve yön +x: 2 hata;
  - yön (0, −1, −1): 1 hata;
  - yön sıfır: `ValueError`, sessiz değil;
  - yol 12'de yön z: 1 hata.
- `glb_kutulari` üçlü dönüşü: depoda başka çağıran yok (`.py` taraması: yalnız `rehber_kablo.py` 2192 / 2194 / 2270).
  `rehber_gorunum.uc_isle` kendi `Mesh` kutularını (bmin, bmax) kullanıyor, etkilenmez.

**İddia 2: U06 şeması**
- Yol uzunluğunu kendim hesapladım (`kablo_yolu_ekran.yollar()`): **1.129,36 mm**. 1,25 × L + 150 = 1.561,7, kayıttaki 1.560 eskisi
  gibi 10'a yuvarlanmış (971 → 1.360 da öyleydi).
- `taban-analiz.json` sınır kutularıyla (tüp r = 2) yaptığım bağımsız yakınlık kontrolü:
  - ESP32 DevKit 0,5 mm (port ağzı);
  - XL4016 C 11,5 mm;
  - taşıyıcı vidası 13,4 mm, burç 16,9 mm, kat M5 cıvatası 17,5 mm;
  - taşıyıcı kutusu 1,1 mm. Bu kutu dişi başlıkları da içeriyor; başlıklar z 62 / 87'de, fiş ise z 75 ± 2'de. Günlükteki kesin
    şekilden çıkan 9,6 mm ile çelişmiyor.
  - Fişin arkasında (+x, x 127–160) parça yok, yani büküm için yer var.
  - Kutu taramasında öbür "Kablo yolu" tüpleriyle örtüşme görünüyor. Bunlar gösterim tüpleri; kablolar arası temas taranmıyor, sorun
    değil.
- 18 mm fiş boyu (tahmin): yalnız son segment boyu. ±10 mm hata önerilen boyda ±12,5 mm eder. 2 m kabloyla pay 440 mm, sonucu
  değiştirmez. Gerçek micro B fiş kabartması (yaklaşık 10,5 × 7 mm) z 69,8–80,3 / y 197,2–204,2 aralığına düşer. Başlıklar bu
  aralığın dışında, kart port ucunda bitiyor. Fiş sığıyor (kutu düzeyinde).
- `lale158-kontrol.json` farkı yalnız U06 (`kablo_ozet`, `kablo_tup_hacim`) ve `sure_s`. `kablo_tup_cakisma` eşiği 0,5 mm³, eski
  yanlış uçta da [] idi. Bu yüzden çakışma alanı tek başına konumu kanıtlamıyor; yakınlık ölçümü kanıtlıyor.
- Metin:
  - "Önden bakınca sağ" = +x (adım 0 tanımı, `rehber_metin.py:98-104`). Port +x ucunda, "direğin sağı" x = 40 > 20, yani tutarlı.
  - 17.10 ve 17.11 de ESP32'yi "önden bakınca sağda" diyor.
  - Sıra: fiş K1'de takılıyor, 1N5819 K2 madde 4'te, hub ucu F5'te. Enerji F1 / F5'te, enerji / güvenlik sırası bozulmuyor (eski
    metin de taban ucunu K1'de bağlatıyordu).
  - K2 maddesinin kaldırılması karar kuyruğunun istediği gibi (`karar-kuyrugu.md:1759-1760`: cümle, `ZORUNLU_ALAN` ve dört bozma
    birlikte kalkar). Yerine K1 `ZORUNLU` ve üç bozma geldi.
  - Küçük tekrar: 17.11'de "(yukarısı K2'de, direk arka yüzü)" ve iki cümle sonra "Yukarısı K2'de." (kozmetik).
- Metin bozmalarım: sağ → sol, "güç panelinin altından", direğin sağı → solu. Üçü de "zorunlu uyarı eksik 1" ile yakalandı.

**İddia 3: kablo boyları**
- `kablolar.json` / `kablolar.md` / `elektrik.md:39, :83` yalnız U06. `boy_tazelik` mantığı doğru: kaynak çözülmüşse çalışıyor,
  liste dizinini ve tek sayıyı destekliyor.
- Kendi bozmalarım:
  - önerilen 1.360: yakalandı (kaynak);
  - önerilen 1.560,4: yakalandı (tam eşitlik);
  - kaynak başka kablonun anahtarına: yakalandı;
  - `sema_boy` 971: `kablolar_denetim`'de yalnız `gorunum` (md eski) yakaladı. `rehber_kablo` `sema_boy_denetle` bunu ayrıca
    yakalıyor (K9'da görüldü);
  - `onerilen_mm` alanı silindi: yalnız `gorunum` yakaladı (önemsiz).
- Sınır: kaynak tek sayıyken kayıtta iki `_mm` alanı varsa sessiz geçer (`kablolar_denetim.py:1989`). Bugün böyle bir kayıt yok.

**Denetleyici gevşetmesi (tek tek)**

| Kaldırılan / değişen | Yerine | Değerlendirme |
|---|---|---|
| `GEO_ISTISNA[9]` | `CAD_KIRP[9]` + `cad_kirp_denetle` + `kirp()` içinde bütün atılan noktaların dışarıda kalması + GLB izdüşüm sınaması | Daha sıkı |
| `SEMA_GEO_ISTISNA` U06 b / son | Yok (şema istisnasız geçiyor; geri eklenirse "kullanılmıyor", b98) | Gerekçeli |
| `ZORUNLU_ALAN` K2 "yanlış yerde" + 4 D2 bozması | `ZORUNLU` K1 17.11 + 3 bozma | Kuyruğun istediği; kapsam eşdeğer |
| b51 (U06 istisnası silindi) | b51 HDMI baş istisnası silindi | Aynı mekanizma sınanıyor |
| `DEMET_ALT` ESP32 USB `kablo_sec` | Yok (seçtiği madde kalktı) | Gerekçeli |
| v10 / v11 y kutusu | İzdüşüm; + v16 / v17 / v18 | Eşdeğer + yeni |
| `ASCII_TAMAM` + "portuna" | — | Doğru yazım |

`rehber_kritik_onay.json`: 11 farkın hepsi bu paketin (GEO_ISTISNA 9 → CAD_KIRP 9, SEMA ×2, ZORUNLU +1, ZORUNLU_ALAN −1, K1 alt
adım 7 / 11, K2 kablo ×2, KABLO_AD 9). `CAD_KIRP 12` ve öbür girdiler değişmemiş.

## 3. Koştuğum sınamalar (`PYTHONIOENCODING=utf-8`, `PYTHONDONTWRITEBYTECODE=1`, `py -3 -B -X utf8`, depo kökünden)

| Sınama | Sonuç |
|---|---|
| `rehber_kablo.py` | SONUÇ GEÇER, çıkış 0; "kırpma kesimi: yol 9 (0, 0.7071, 0.7071) · p ≤ 143.92, yol 12 y ≤ 192.5; hata 0"; geometri hata 0; şema geometrisi hata 0, istisnalı 4; onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 98 / 98 (b94–b98 hepsi denetimle yakalandı, yalnız onayla değil) |
| `rehber_denetim.py --kaynak` | çıkış 0; ASCII 0, zorunlu eksik 0, yasak 0, çıplak 0, onay farkı 0 (kablo 220, liste 226, metin 1142) |
| `rehber_denetim.py --bozma-denemesi` | 305 / 305, bozulmamışta hata 0 |
| `kablolar_denetim.py` | GEÇER |
| `kablolar_denetim.py --bozma-denemesi` | 174, GEÇER (b_boy_tazelik, b_boy_tazelik_2 YAKALADI) |
| `F10l-birlesim.py` | GECER |
| Kendi bozmalarım | `rehber_kablo` 9 (K1–K9, bellekte), `kablolar_denetim` 5 (bellekte kopya), metin 4 (`rehber_metin.py` yedekten geri yüklendi, SHA-1 önce / sonra aynı `019c3088…`) |
| `git status` | Başlangıçtaki listeyle aynı: paketin 13 değişen + 1 yeni dosyası, 19 eski kir. `regresyon.json` / `-son-kosu.json` değişmemiş. Bu kontrolün tek yeni dosyası bu belge |

## 4. Bakmadığım / bakamadığım

- FreeCAD koşmadım: `kirp()`'in gerçek şekil üzerindeki sonucu, `lale158_kontrol` ve kesin şekil yakınlıkları için günlüğe ve
  koddan çıkardığım dönüşüm kanıtına güvendim.
- Tam üretim ve zincir koşulmadı (görev dışı): GLB'de yol 9'un kesilmiş çizimi, U06'nın `rehber-veri.json`'daki noktaları, kareler
  (17.7, 17.11, 32.4), uç etiketi sayıları ve PDF kapanış ajanına kalıyor (günlük § 7.b doğru sınamaları tarif ediyor).
- K64 bara tutucusunun U06 şeridine düşüp düşmeyeceği CAD ajanının işi. Günlükteki bağımlılık notu yerinde.
- `uygulama_olc.py` yeniden koşulmadı (D3).
