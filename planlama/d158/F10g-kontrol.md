# F10g bağımsız kontrol (P10.5b, K56 + K57 uygulaması), 14.11.2026

Kontrolcü: ayrı ajan (B). Uygulama ajanının günlüğünü (`F10g-gunluk.md`) iddia olarak okudum; aşağıdaki sayılar kendi ölçümüm.
Başlangıç 14.11.2026 01:15 (saat `date` ile okundu), dal `lale-duzeltme`, HEAD `9145164`, çalışma ağacındaki commit edilmemiş
değişiklikler sınandı. Geçici betik ve çıktılar geçici klasörde; depoya yazdığım tek dosya bu rapor. FreeCAD ve `rehber_uret.py`
koşulmadı; doğrulama betikleri depo JSON'larını ezmeden, çıktısı geçici klasöre çevrilerek koşuldu (§ 4.7). Rehber `rehber/index.html`
üzerinden kendi başsız Chrome'umla (kendi profil klasörü) salt okuma açıldı; iş bitince yalnız o süreç kapandı.

## 1. Hüküm

**GEÇER.** Kabul ölçütlerinin hepsi kendi ölçümümle tutuyor; paketi durduran bulgu yok. Aşağıdaki bulguların hepsi okunurluk ya da
kayıt düzeyinde; commit'e kayıtlı açık iş olarak girebilir.

Özet:
- Adımı değişen parça yalnız iddia edilen sekizi; parça sayısı 1192, ad / adet aynı, başka parçada hiçbir alan değişmedi.
- Bağımsız nokta–üçgen ölçümünde 40.1 (kol çatalı + iki bilezik; ardından pul + M5×12) ve 44.1 (dirsek çatalı + iki bilezik;
  ardından horn merkez vidası) sağ ve sol temiz. Ölçüm körlemesine değil: eski sıra aynı betikle bilerek kurulunca engeller
  (1,67 / 2,48 mm ve 3,0 mm) yeniden çıkıyor.
- Silinen dört dar istisnanın yerine başka ad altında susturma gelmemiş.
- Perdelenmeye eklenen iki gerekçe gerçek bir durumu anlatıyor (iç bilezik yuvada, pul + cıvata başının altında).
- 39 ↔ 40.x ve 43 ↔ 44.x metinleri tek sıra; F10f üçüncü bakışın Y1'i kapandı.

## 2. Bulgular (önem sırasıyla)

### B1. 40.1 / 44.1 panel sırası metindeki sırayla tam örtüşmüyor (düşük-orta; kayıtlı açık iş)

- **Ne, nerede:** panel başlığı "Parçalar ve bağlantı elemanları (takma sırasıyla)" (web ve PDF s. 58, 66). Alt adımda önce
  parçalar, sonra bağlantı elemanları diziliyor (`rehber_veri.py` kuralı). Sonuç:
  - 40.1: horn → çatal → iç / dış bilezik → **üst kol tüpü** → ısıl gömme → **mafsal pulu → M5×12** → **S2 horn merkez vidası** →
    M3×8. Metin (40 madde 1–3, 40.1) ve kaynak (`omuz_rapor.py` SIRA 8–10): horn + merkez vidası → çatal → pul + M5×12 → tüp.
    - Tüp ↔ M5 farkı bu paketle geldi (M5 40.1'e taşındı).
    - Horn vidası ↔ çatal farkı önceden de vardı (HEAD verisinde de çataldan sonra).
  - 44.1: horn merkez vidası panelde M3×12 çatal–horn cıvatalarından **önce**. Metin "çatalı horna cıvatala; çatal yerindeyken …
    merkez vidası" diyor (sonra). Bu paketle geldi.
- **Ölçümüm:** bunlar montaj hatası değil. Panel sırasıyla da yol temiz:
  - M5×12 / pul tüp yerindeyken −z'den: temiz (sağ / sol, engel 1011–1013 parça, eşik üstü 0).
  - S2 horn merkez vidası p0120 / p0193 çatal yerindeyken +z'den: temiz.
  - Dirsek horn vidası yalnız çatal yerindeyken ölçüldü (M3×12'den önce): temiz.
  - Rehberin alet denetimi aynı sırayla "DUZ" diyor (günlük § 2.2; ben yeniden koşmadım, F10f-dogrula'nın sıra sınaması geçti, § 4.7).
  - Yani iki sıra da geometride mümkün. Okur yine de "takma sırasıyla" başlığı altında metinden farklı bir sıra görüyor.
- **Öneri:** ya alt adımda bağlantı satırlarını parçaların arasına alan bir sıra (ör. 40.1'de `b:pul, b:M5` tüpten önce; 44.1'de
  M3×12 horn vidasından önce), ya da panel başlığına / metne "liste parça önce, bağlantı sonra sıralıdır" notu.
  - Ajanın § 7'de bıraktığı not doğru; "gerçek sırada fark yaratmıyor" sözünü ölçümüm destekliyor.
- **Paketi durdurur mu:** hayır. Kayıtlı açık iş.

### B2. K57 başlığında yanlış ad: "S2 horn merkez vidası" (düşük; C adımında düzeltilsin)

- **Nerede:** `karar-kuyrugu.md` özet tablosu (K57 satırı) ve "## K57 · Dirsek çatalı ↔ S2 horn merkez vidası" başlığı.
- **Ölçümüm:** taşınan parça p0573 / p0630 "Dirsek horn merkez vidası M3". Dirsek servosu S2 değil, MG996R. S2 horn merkez vidası
  (p0120 / p0193) başka bir parça; adımı değişmedi (40).
- **Öneri:** C adımı "kapandı" yazarken başlığı "dirsek horn merkez vidası" yapsın.
  - K56'daki "Bugünkü rehber (düzeltme turu 2)" paragrafı artık F10g öncesini anlatıyor; "F10g öncesi" diye işaretlensin.
- **Paketi durdurur mu:** hayır.

### B3. Yeni perdelenme gerekçesinin kaynak atfı yanlış (düşük)

- **Nerede:** `rehber_metin.py` 40.1 `gizli_ok` p0116 / p0189. `gizli()` yardımcısı her gerekçeye sabit "… piksel ölçümü
  F10f-gunluk.md Düzeltme turu 1" ekliyor.
- **Sorun:** bu iki parçanın ölçümü F10g'de yapıldı (`F10g-gunluk.md` § 2.3), F10f düzeltme turu 1'de değil.
  - Gerekçe metni okur verisinde ve `kontrol.json`'da görünür. Okur metni değil, denetim gerekçesi.
- **Öneri:** `gizli()`'ye kaynak argümanı ya da bu iki parça için elle "F10g-gunluk.md § 2.3" atfı. Bir sonraki üretimde.
- **Paketi durdurur mu:** hayır.

### B4. `M6-montaj-sirasi.md` satır 132 ve 136 eski sırayı yazıyor (düşük; ölçüt 4'ü bozmuyor)

- **Ne:**
  - satır 132 (G2): "mafsal 625ZZ + M5 pim … 2 × M5×12 + pul";
  - satır 136 (H0b): "dirsek hornu + merkez vidası … **çataldan önce**".
- **Değerlendirmem:**
  - Kabul ölçütü 4 (A brief) tasarım kaynağı olarak `omuz_rapor.py` SIRA ve dirsek karşılığını sayıyor; ikisi de rehberle aynı (§ 3.5).
  - M6 tablosu F7a'dan beri 125 cm erişim analizinin kaydı olarak dondurulmuş (`rehber_secici.py` başlık notu). Rehber dört sütunu
    `rehber_metin.py`'den eziyor.
  - Okur verisini 39 / 40 / 43 / 44 için alan alan denetledim. M6'dan gelen tek hücreler 40 "erişim: düz" ve 44 "erişim: düz; pim
    robotta erişilemez"; ikisi de sırayla çelişmiyor. Rehberde görünen eski sıra kalıntısı yok.
  - Aynı belgenin § 1 maddesi "Dirsek tezgâhı: servolar → dirsek hornu → çatal → …" vidanın yerini söylemiyor; çelişmiyor.
- **Risk:** M6'yı okuyan biri 39 / 43 satırlarında eski sırayı görür. Rehber "M6 no 39" rozeti gösterdiği için bu belgeye yönlendirebilir.
- **Öneri:** tablo hücrelerine dokunmadan, tablonun üstüne tarihli tek satır not: "39 ve 43 satırlarındaki mafsal ve dirsek horn vidası
  sırası K56 / K57 (13.11.2026) ile değişti; geçerli sıra rehberde." Hücreyi değiştirmek `m6_tablo()` ayrıştırmasıyla rehberi
  etkileyebilir, not tablonun dışında kalmalı.
- **Paketi durdurur mu:** hayır. Kayıtlı açık iş.

### B5. `dirsek/rapor.html` elle düzeltmesi tutarlı; ama dosyanın geri kalanı zaten eski (bilgi; bu paketin dışı)

- **Ölçümüm:**
  - `dirsek_rapor.py` HEAD sürümü (değiştirilmemiş kopya) bu makinede çöküyor: "min() iterable argument is empty" (HEAD'de satır
    246, çalışma ağacında 248). İddia doğru.
  - Betiğin bir kopyasını yalnız iki değişiklikle koştum: boş listede `min()` yerine "–", çıktı geçici klasöre. Çalışma ağacı
    sürümünün ürettiği "Montaj sırası (öneri)" bölümü depodaki elle düzeltilmiş `rapor.html` bölümüyle **birebir aynı**.
  - HEAD sürümüyle çalışma ağacı sürümünün çıktıları yalnız bu satırda ayrılıyor.
- **Ek bulgu:** betik koşsaydı `rapor.html`'in başka yerleri de değişirdi. Depodaki dosya 8 Ekim 2026 görselleri ve o günün verisiyle duruyor:
  - 53 ↔ 57 parça,
  - dirsek ekseni −173 ↔ −203,
  - grup kütleleri,
  - gömülü görseller,
  - "çakışma taraması eskimiş olabilir" uyarısı.
  - Bu, bu paketten önce de böyleydi (betik çöktüğü için yenilenemiyor). Elle düzeltme yalnız sıra bölümünü yeniledi; doğru seçim.
- **Öneri:** `dirsek_rapor.py` satır 248'in boş liste korumasını ayrı bir pakette ekleyip raporu yeniden üretmek (ajanın § 7 notu).
- **Paketi durdurur mu:** hayır.

### B6. 43.x panelinde bağlantı elemanı yokken "takma sırasıyla yukarıdaki tabloda" cümlesi (düşük; bilgi)

- Karede gördüm (43.1 / 43.2, iki tema): "Bağlantı elemanları takma sırasıyla yukarıdaki tabloda." + "Kol başına yok (…)".
- Tabloda bağlantı satırı yok. Anlamı bozmuyor ama boş tabloyu işaret ediyor. Ajan § 7'de not etmiş.
- Kayıtlı açık iş.

## 3. Doğruladıklarım

### 3.1 Parça ataması (HEAD ↔ çalışma ağacı, `rehber-veri.json` `parcalar[]` bütün alanlar)

- 1192 ↔ 1192 parça, kimlik kümesi aynı, ad başına adet aynı. Alanı değişen parça **yalnız 8**:

  | Kimlik | Parça | Değişen alanlar |
  | --- | --- | --- |
  | p0116 / p0189 | 625ZZ iç bilezik (sağ / sol) | a, b 39 → 40; h yok → p0121 / p0194; u eğik → ±x; d 40 → 56,9 |
  | p0117 / p0190 | Mafsal pulu M5 | a, b 39 → 40 |
  | p0118 / p0191 | Mafsal cıvatası M5x12 | a, b 39 → 40 |
  | p0573 / p0630 | Dirsek horn merkez vidası M3 | a 43 → 44 (b 48 kaldı: tezgâh parçası H1'de robota girer) |

- Adım sayısı 50, alt adım grubu 74 ↔ 74 (rehberin "alt adım 71" sayısı `kontrol.json`'da 71 ↔ 71).
- Veride değişen öbür üst anahtarlar yalnız `uretim` (saat) ve `ev_kaynak` (bağlandığı yer sayıları; taşınan parçaların hedefi).
- BOM / adet etkilenmedi.

### 3.2 Uçuş yolları, bağımsız ölçüm

**Yöntem:**
- Ölçüm F10f B2 / B3'ün nokta–üçgen + genelleştirilmiş sargı sayısı yöntemi (betik kopyalanıp uyarlandı).
- Engel kümesini rehberin `durumlar()` fonksiyonunu kullanmadan, verinin `a` / `b` / `t` alanlarından ve satır sırasından kendim kurdum.
- Rehberden yalnız mesh okuyucu (`glb_oku`) alındı.
- 1 mm adım, eşik: duruş derinliği + 0,2 mm.

| Satır | Hareketli grup | Yön, boy | Engel | Eşik üstü | En derin temas |
| --- | --- | --- | --- | --- | --- |
| 40.1 p0121 | çatal + iç + dış bilezik + 2 ısıl gömme | +x, 56,9 | 999 | **0** | göbek 1,5 (duruşta 2,5) |
| 40.1 p0194 | aynası | −x, 56,9 | 999 | **0** | göbek 1,5 (duruşta 2,5) |
| 40.1 p0117 / p0190 | mafsal pulu | −z, 25 | 1011 | **0** | — |
| 40.1 p0118 / p0191 | M5×12 | −z, 42,5 | 1013 | **0** | iç bilezik / M5 ısıl gömme 0,0 (duruş teması) |
| 44.1 p0562 / p0619 | dirsek çatalı + iki bilezik | +y, 63,5 | 46 | **0** | horn / servo mili 0,0 |
| 44.1 p0573 / p0630 | horn merkez vidası (çatal yerinde) | ±x, 25 | 52 | **0** | servo mili 0,0 |
| 40.1 p0120 / p0193 | S2 horn merkez vidası (çatal yerinde; B1 için) | +z, 25 | 1015 | 0 | servo mili 0,0 |
| 40.1 p0127 | üst kol tüpü | −y, 76,1 | 1009 | 0 | tambur 1,1 (duruşta 1,1) |

Vidanın engel kümesine çatal grubu dahil (52 = 46 + iki çatal grubu). Vida çatalın içinden geçiyor ve çarpmıyor. Bu, kaynaktaki Ø9
erişim deliğiyle tutuyor (`dirsek_parcalar.py` satır 135, `cyl(4.5, …)` "horn merkez vidasi erisimi").

**Bilerek bozma** (aynı betik, eski sırayı taklit):

| Deneme | Ne kuruldu | Sonuç |
| --- | --- | --- |
| m1 | 40.1 sağ: iç bilezik çataldan ayrı, yerinde; pul + M5 yerinde (eski K56 sırası) | p0116 **1,67** mm, p0118 **2,48** mm (F10f üçüncü bakışın sayılarıyla aynı) |
| m2 | 44.1 sağ / sol: horn vidası yerinde (eski K57 sırası) | p0573 **3,0** mm, p0630 **3,0** mm (aynı) |

Yani ölçüm eski engelleri yakalıyor; yeni sıradaki "0" kör nokta değil.

**Rehberin kendi sonucu** (`planlama/rehber/kontrol.json`, HEAD ↔ çalışma ağacı):

| Ölçü | HEAD | Şimdi |
| --- | --- | --- |
| Uçuş satırı | 336 | 340 |
| Çarpışan / `sinir_carpisan` | 0 / 0 | 0 / 0 |
| Uçuş istisnası | 20 | 16 |
| `istisna_bos` | 0 | 0 |
| Ölçüm kaydı | 1 | 1 |
| `gecti` | true | true |

- HEAD'deki 20 istisnanın konumları: 31.6, 33.3–5, 35.1–3, 35.5, 36.1–2, 40.1 ×2, 41.6 ×4, 44.1 ×2. Şimdi 40.1 ve 44.1'dekiler
  yok, öbürleri aynı.
- 40.1 / 44.1'in bütün uçuş satırları `temiz: true`; HEAD'de çatal satırları `temiz: false` + istisna idi.
- +4 satır: 40.1'deki pul ×2 + M5×12 ×2.
- Giriş yolu istisnası 2 ↔ 2.

**Başka ad altında susturma yok:**
- `rehber_denetim.py` farkı yalnız `ASCII_TAMAM` sözlüğüne 4 kelime (preslenir, yerindeyken, koldan, kolundaki); denetim kuralı değişmedi.
- `rehber_metin.py` farkında `ucus_ok` / `giris_ok` / `piksel_ok` eklenmedi, yalnız silindi.
- Eklenenler:
  - `birlikte` için iç bilezik → çatal: C kararının kendisi, rulman çatala preslenmiş.
  - `gizli_ok` ×2: perdelenme, uçuş değil; § 3.3.
- `K1_KOL` / `K1_DIRSEK` sabitleri silinmiş, başka kullanan yok.

### 3.3 Perdelenme +2 (115 → 117, toplam gizli 262 → 264)

- **Gerçek durum mu:** evet.
  - p0116 / p0189 iç bilezik, rulmanın kendi dış bileziğinin içinde, çatalın arka kolundaki Ø16 yuvada.
  - Bir yanında mafsal pulu (M5 DIN 125, dış çap iç bilezikten büyük) ve cıvata başı, öbür yanında göbek var.
  - 44.1'deki dirsek 625ZZ bilezikleri (F10f'ten beri gerekçeli) aynı yapıda.
  - Görünmesi gereken bir parça susturulmuyor. Gerekçe uçuş sınamasını etkilemiyor (uçuşta çatalla birlikte ölçülüyor, § 3.2).
- **Okur ne görüyor:**
  - 40.1 takılı (iki tema): iç bilezik görünmüyor; parça listesinde "625ZZ rulman (iç bilezik) (sağ + sol) ×2" var.
  - Metin "625ZZ … tezgâhta önceden preslenir, iki bileziğiyle çatalla gelir" diyor. Kontrol listesinde "625ZZ yuvasından çıkmadı" var.
  - 40.1 patlatılmış (iki tema): rulman çatalın arka kolunda, çatalla birlikte duruyor; pul + cıvatanın yeri göbek tarafında işaretli.
  - Montajcı neyin takıldığını metinden ve listeden anlıyor.
- F10f-dogrula `gizli_piksel` (ajan zinciri ve benim tekrarım, § 4.7) p0116 / p0189'u "okurun göremediği yerde" listeliyor; bu tutarlı.

### 3.4 Metinler tek sıra (okur verisi + PDF metni)

- **39 (G2):**
  - Metin: "Servoyu göbeğe cıvatala. Göbeğin karşı tarafındaki mafsal (625ZZ, pul, M5×12) G3'te, kol çatalıyla gelir." Takma
    eylemi yok.
  - Liste: yalnız S2 servo + çıkış mili, M4×16 + kontra somun.
  - Alet "alyan 3 + 7 mm" (M5'in alyan 4'ü 40'a gitti). Doğru.
- **40 / 40.1 (G3):**
  - Rulman "tezgâhta önceden preslenir, iki bileziğiyle çatalla gelir"; pul + M5×12 "çatal yerindeyken"; iç bileziği göbeğe sıkar.
  - Bağlantı satırında "1 × M5×12 + pul mafsal (çataldan sonra)"; alet "PH1, alyan 2,5 / 4".
  - Parça listesi ve metin aynı parçaları anlatıyor. Panel sırası için B1.
- **43 / 43.x (H0b):**
  - "Dirsek hornunu servo miline geçir (merkez vidası bu adımda takılmaz: H0c'de, dirsek çatalından sonra)."
  - Bağlantı "Kol başına yok"; alet "el". Eski M6 erişim hücresi ("çataldan önce") okur verisinde yok.
- **44 / 44.1 (H0c):**
  - Vida "çatal yerindeyken …, çatalın dış kolundaki erişim deliğinden".
  - Başlık "Dirsek çatalı + horn merkez vidası + pim"; kontrol "Horn merkez vidası sıkı".
- **Aynı parça iki adımda takılıyor gibi okunan yer yok.** Taramam: 37–44 ve 48 adımlarının bütün metin alanlarında 625ZZ / mafsal
  / M5×12 / merkez vida / M5 pim. Kafadaki "625ZZ ve M5 pim bu adımda yok" (E2) ayrı bir adım, ilgisiz.
- **PDF** (75 sayfa; s. 57, 58, 59, 65, 66, 67 metni ve s. 58 / 66 görüntüsü) web verisiyle aynı metni taşıyor.

### 3.5 Tasarım kaynakları

- `omuz_rapor.py` SIRA (ve üretilmiş `omuz/rapor.md`) değişmemiş (git farkı yok):
  - SIRA 2 "625ZZ'yi çatalın arka koluna bastır";
  - SIRA 9 "Çatalı tak: … arka kol M5×12 + pulla göbekteki somuna".
  - K56 C'nin sırasının ta kendisi; "zaten uyumluydu" iddiası doğru.
- `dirsek_rapor.py` SIRA 5–6:
  - 5: "Horn'u … tak (merkez vidası 6. maddede, çataldan sonra)."
  - 6: "… Horn merkez vidasını çatalın dış kolundaki erişim deliğinden sık."
  - K57 a ile aynı. `rapor.html` için bkz. B5.
- `grep` taraması (md / py / html, `rehber/` ve F10 günlükleri dışında):
  - Eski sırayı hâlâ söyleyen tek belge `M6-montaj-sirasi.md` (B4) ve onun ham hâli `m6_tablo.md` / `M6_erisim.py` (125 cm kaydı).
  - `karar-kuyrugu.md` ve `dongu-158.md`'deki eşleşmeler eski durumu anlatan tarihsel satırlar.
- Geometri dosyalarına, korunan değerlere dokunulmamış:
  - Değişen kaynaklar yalnız `rehber_secici.py`, `rehber_metin.py`, `rehber_denetim.py`, `dirsek_rapor.py` (yalnız SIRA metni +
    yorum) ve `dirsek/rapor.html` (1 satır).
  - `robot.glb` değişmemiş.

### 3.6 Kareler (kendi başsız Chrome'um, 1400 × 900, iki tema)

- **Bakılan adresler:**
  - takılı: 39, 40, 40.1, 43, 43.1, 43.2, 44, 44.1;
  - patlatılmış: 40.1, 43.1, 43.2, 44.1.
  - 24 açılışın hepsinde `data-hazir=1`, `data-hata` boş, konsol hatası 0, uyarı 0.
- **39:** yalnız S2 servoları (siyah) ve M4 bağlantı yerleri; 625ZZ / pul / M5 yok. Koyu temada siyah servo koyu zeminde zor
  seçiliyor; önceden de böyleydi, bu paketin değil.
- **40.1 takılı:**
  - çatal turuncu, tüp mavi, göbek ve servo "bağlandığı yer" pembe;
  - 10 parça / 22 bağlantı;
  - iç bilezik görünmüyor (yuvada).
- **40.1 patlatılmış:** çatal +x / −x yönünde ayrık, rulman çatalın arka kolunda; tüp aşağıda (−y). Yön okunuyor, saydam / gri
  karışması yok.
- **43.1 / 43.2:**
  - yalnız horn (1 parça, 0 bağlantı), merkez vidası yok;
  - alet "el";
  - servo mili pembe. Açık temada horn ile gri servo yakın tonda; önceden de böyle (ajan § 7).
- **44.1:**
  - takılı (koyu): iki çatal turuncu, ön kol pembe, 6 parça / 22 bağlantı.
  - patlatılmış (açık): çatallar +y'de, vidalar ±x'te ayrı.
  - Hangi küçük vidanın merkez vidası olduğunu karede tek tek ayırt etmedim (yeri uçuş ölçümünde, § 3.2).
- **PDF** s. 58 (40) ve s. 66 (44) görüntüsü: kareler ve panel listeleri web'le aynı. PDF üstverisinde yerel bilgi yok (Creator
  "HeadlessChrome").

### 3.7 Zincir

**Ajanın kaydı:**
- `zin1.durum` "BITTI cikis 0 sure 5158 enaz 2.77". Sarmalayıcı zincirin çıkışını "herhangi biri ≠ 0 ise ≠ 0" diye topluyor (betiği okudum).
- Günlükteki her komutun "ZINCIR bitti … cikis 0" satırı log'da var:

| Komut | Başlangıç | Süre (s) | Çıkış |
| --- | --- | --- | --- |
| `rehber_uret.py` (FreeCAD'li tam üretim) | 23:42:18 | 2478 | 0 |
| F10f-dogrula | 00:23:36 | 623 | 0 |
| F10e-dogrula `--goruntu-yok` | 00:33:59 | 897 | 0 |
| F10d-dogrula `--goruntu-yok` | 00:48:56 | 719 | 0 |
| F10a-dogrula `--kanit-yok` | 01:00:56 | 434 | 0 |
| F9b-dogrula | 01:08:10 | 5 | 0 (GEÇER, hata 0) |
| `carpisma_kos.py kontrol` | 01:08:15 | 0 | 0 (17 dosya aynı) |
| `regresyon.py --yazma` | 01:08:15 | 0 | 0 (GEÇER) |

**Dosya saatleri:**
- Son kod yazımı `rehber_denetim.py` 13.11 23:41:49; öbür kaynaklar daha önce:
  - `rehber_secici.py` 23:33:14;
  - `rehber_metin.py` 23:41:22;
  - `dirsek_rapor.py` 23:34:55;
  - `rapor.html` 23:35:31.
- Zincir başlangıcı 23:42:17; bütün üretilen dosyalar ondan sonra:
  - veri 23:46:09;
  - kareler 23:52–23:55;
  - PDF 23:59:02;
  - `kontrol.json` 00:23:36;
  - F10f / F10e / F10d / F10a-dogrula.json 00:33:59 / 00:48:56 / 01:00:56 / 01:08:10.
- Zincirden sonra değişen depo dosyaları yalnız günlük, `dongu-158.md` ve `karar-kuyrugu.md` (23:44, belge).
- Eski 14 dosyanın saati 09.11; zincir onları yazmamış.

**Benim tekrarım** (FreeCAD'siz; depo JSON'u yazılmasın diye betikler modül olarak yüklenip `CIKTI` geçici klasöre çevrildi;
F10a `--json` ile; F9b `--goruntu`suz; regresyon `--yazma`; `carpisma_kos kontrol` salt okuma):

| Komut | Başlangıç | Boş bellek (GB) | Süre (s) | Çıkış | Sonuç |
| --- | --- | --- | --- | --- | --- |
| F10f-dogrula | 01:23:23 | 4,97 | 561 | 0 | GEÇTİ (veri, sınama, kablo kare, sağ / sol, mini etiket; `gizli_piksel` 11 parça, p0116 / p0189 dahil) |
| F10e-dogrula `--goruntu-yok` | 01:32:44 | 4,98 | 869 | 0 | GEÇTİ; renk_demo KALDI (karar) |
| F10d-dogrula `--goruntu-yok` | 01:47:13 | 5,07 | 728 | 0 | GEÇTİ (121 konum) |
| F10a-dogrula `--kanit-yok` | 01:59:21 | 5,03 | 444 | 0 | GEÇTİ (seçim 6/6, konsol 0, 360 px taşma 0) |
| F9b-dogrula | 02:06:45 | 4,95 | 5 | 0 | GEÇER, hata 0 |
| `carpisma_kos.py kontrol` | 02:06:50 | 4,94 | 0 | 0 | 17 dosya aynı |
| `regresyon.py --yazma` | 02:06:50 | 4,94 | 0 | 0 | GEÇER, kötüleşen yok |

Koşudan sonra dört `F10x-dogrula.json`, `regresyon-son-kosu.json` ve `carpisma-sonuc.json`'un git karması koşu öncesiyle aynı:
tekrarım depoya yazmadı. Kendi başsız Chrome süreçlerimden geride kalan yok (profil adıyla sayıldı: 0; kullanıcının Chrome'u 15
süreç, başlangıçtakiyle aynı).

**`renk_demo` KALDI:** HEAD'deki `F10e-dogrula.json`'da da `"renk_demo": false` (F10e'den beri bilinen karar); bu paketin getirdiği
bir şey değil.

### 3.8 Kayıt dosyaları

- `karar-kuyrugu.md` K56 / K57 "Durum": karar veren Ahmet, 13.11.2026 ≈ 23:28, alıntı "K56 ve K57 önerdiğin gibi olsun, devam",
  seçenek C / a.
  - "kapandı" ve açık sayısı (52) C adımına bırakılmış; brief'le uyumlu.
  - Özet tablo satırları da "Ahmet 13.11 … kararını verdi, uygulama F10g, kontrol bekliyor" diyor.
  - Eksik: K57 başlık adı (B2).
- `dongu-158.md`: P10.5b satırı (F10g; ölçüt ve durum) ve § 5'e başlangıç (23:29) + bitiş (01:13) girdileri var. Sayılar
  `kontrol.json`'la aynı.

### 3.9 Gizlilik

- Değişen ve yeni dosyaları yerel kullanıcı adı, makine adı, kullanıcı klasörü yolu, eşitleme klasörü, takma ad için taradım:
  `F10g-gunluk.md`, `karar-kuyrugu.md`, `dongu-158.md`, üç rehber betiği, `dirsek_rapor.py`, `rapor.html`, `rehber-veri.json` /
  `.js`, `kontrol.json`, dört `F10x-dogrula.json`, PDF metni (75 sayfa) ve üstverisi. **Bulgu 0.**
- `F10g-gunluk.md` geçici klasörü yalnız klasör adıyla anıyor (`k5657-a/`), yol yok.
- Kişi adı olarak yalnız "Ahmet" geçiyor.
- `karar-kuyrugu.md`'deki "OneDrive" eşleşmesi bu paketin farkında değil, eski bir maddede.

## 4. Ölçemediklerim / bakmadıklarım

- **Gerçek alet erişimi ve elle presleme** ölçülmedi; çatal takılıyken M5×12 ve horn merkez vidasının gerçek aletle sıkılması da
  ölçülmedi. Modelle ölçülemez; karar kuyruğundaki "Ölçülmedi" notu açık kalmalı.
- Rehberin alet / el modeli (`sira` denetimi) yeniden koşulmadı. F10f-dogrula'nın sıra sınaması tekrarımda geçti; ama 565 bağlantılı
  tam alet taraması `rehber_uret.py` içinde, onu koşmadım.
- Uçuş ölçümüm yalnız 40.1 ve 44.1'in değişen ve komşu satırları (14 satır + 3 bilerek bozma). Bütün rehberin 340 satırını
  bağımsız taramadım; öbür satırlar bu paketle değişmedi (istisna konumları HEAD ile aynı).
- Kareleri yalnız 12 adreste, iki temada, statik açtım. "Tak" animasyonunu adım adım izlemedim.
- Bu paketin dışındaki çalışma ağacı dosyalarına (`planlama/adim3/elektrik.md`, `pin-haritasi.md`, `pin-karari-*.md`, eski 14
  dosya) bakmadım; yalnız saatlerine baktım (pin dosyaları 14.11 00:32–01:12, ayrı iş).
- **Kontrol sırasında başka bir iş depoya yazdı.** Benim koşum değil; tekrarımın yazdığı dosyaların karması aynı.
  - Değişen dosyalar:
    - `dongu-158.md` 01:35;
    - `karar-kuyrugu.md` 01:49 (yeni madde K58, "Kapandı: 6", toplam 58);
    - `F4c-partiler.py` ve `planlama/baski-listesi.md` 01:35;
    - yeni `kablolama-*` dosyaları.
  - K56 / K57 satırları bu yazımdan sonra da yukarıda okuduğum gibi.
  - C adımı commit'te bu paketin dosyalarını o işinkilerden ayırmalı. `karar-kuyrugu.md` ve `dongu-158.md` iki işin değişikliğini
    birlikte taşıyor.
