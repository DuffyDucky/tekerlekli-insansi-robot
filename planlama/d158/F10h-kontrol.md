**DÜZELTME GEREKLİ:** Rehber kaynağındaki elektrik değerleri kayıtlarla uyuşuyor. Üç sorun var: CAD'den gelen parça adları üretilen veride denetimi kıracak, Ö4 klemensinin köprüsü yazılmamış, yol 4 eşlemesinde yanlış motor var.

# P10.7b1: rehberin elektrik tarafı, bağımsız kaynak kontrolü (F10h B)

- Tarih: 2026-11-14 09:24 (saat ölçüldü). Dal `lale-duzeltme`, HEAD `8134519`. Ölçülen fark `git diff 8134519` ile alındı: 28 dosya. Çalışma ağacında 30 satır vardı; kontrol bitince bu rapor dışında yine 30 satır.
- Kapsam yalnız kaynak düzeyi. FreeCAD, `rehber_uret.py` ve başsız tarayıcı koşmadı. Rehber çıktılarına (`rehber/veri`, `rehber/goruntu`, `planlama/rehber`) bilerek eski oldukları için bakılmadı.
- Bozma denemelerinin hepsi geçici bir kopyada yapıldı. Kopya her denemeden sonra geri yazıldı ve özetiyle (hash) doğrulandı. Depoda değişen tek dosya bu rapor.
- Kullanılabilir bellek kontrol boyunca 2085–2155 MB arasında kaldı.

## 1. Üretimden önce düzelmeli

### Ü1. CAD parça adları ve kodları rehber verisinde elektrik denetimini kıracak

- **Bulgu:** Veri modundaki denetim CAD'den gelen parça adlarını ve kodlarını da tarıyor. `rehber_metin.py` bunların hiçbirini değiştirmiyor.
- **Etkilenen yerler:**
  - `tasarim/freecad/taban/taban_parcalar.py:453`: arayüz kartı kodu "MOSFET + 1N4007". `arayuz.py:663` aynı ifadeyi taşıyor ("role surucu MOSFET + diyot").
  - `tasarim/freecad/kafa/kafa_lib.py:81`: model adı "USB ses karti (PAM8403 girisi …)".
  - `yerlesim_lib.py:294`: "Kopuk bant (USB ses karti)".
  - Bu adlar E4 adımının parça satırına ve parça kartlarına olduğu gibi geçiyor.
- **Kural çakışması:** `rehber_denetim.py:559` (MOSFET, istisna "değil|eski|yerine") ve `:563` (ses kartı, istisna "yedek|takılmaz|çıktı|…") bu cümleleri yakalar.
- **Ölçüm:**
  - Eski üretilmiş veride `elektrik_denetle` koşturuldu ve 54 bulgu verdi.
  - Bunların 5'i parça adı ya da kodu: p0822, p0823 (ad ve kod), p1085 kodu ve E4 parça satırı. Bu metinler kaynakta yok, dolayısıyla yeni üretimde de değişmeyecek.
  - Sonuç: veri denetimi ELEKTRİK ≥ 5 verir ve `rehber_uret.py` "denetim" adımında sıfırdan farklı çıkış koduyla durur.
  - Ajanın "üretimden sonra 0" beklentisi tutmaz.
  - Asıl tehlike montajcıya giden mesaj: arayüz kartının kartında "MOSFET" okuyacak, oysa sürücü BC337-40.
- **Sayı tutarsızlığı:** Eski veride ajanın bulduğu sayı kayıtlar arasında farklı geçiyor. `F10h-gunluk.md` 30 diyor (ekrana basılan ilk satırlar), `dongu-158.md` ve `karar-kuyrugu.md` 49 diyor. Benim ölçümüm 54.
- **Öneri:**
  - CAD tarafına dokunmadan, rehberin görüntü adı ve kodu katmanında ad ve kod çevirisi eklenmeli (`rehber_metin` tr / TR_IFADE). Karşılıklar: "MOSFET + 1N4007" → "BC337-40 ×2 + 1N4007", "USB ses kartı" → "USB ses kartı (yedek, takılmaz)".
  - `kaynak_denetle` CAD parça adlarını ve kodlarını da taramalı. Böylece bu tür bulgu üretimden önce kaynak modunda görülür.

### Ü2. Ö4 klemensinin köprülü olduğu rehberde yazmıyor

- **Bulgu:** `rehber_metin.py:276` (K1 is_) yalnız "iki uçlu yer (2 pin 5,08 mm klemens) elde taşınan acil stop (Ö4) için ayrıldı: Ö4 karar bekliyor (K60)" diyor.
- **Kayıtlar köprüyü şart koşuyor:**
  - `kablolama-on-kararlar.md` §8 Ö4: köprülü klemens, "Köprü unutulursa röle çekmez".
  - O-6 a/c ve `kablolar.json` A02 sonlandırması: "Ö4 için iki uçlu yer (2 pin 5,08 klemens, köprülü)".
- **Bu iki satırın etkisi:**
  - Rehber aynı adımın 284-285. satırlarında "Mantar ve ana anahtar uçları hiçbir zaman köprülenmez" diyor. İlk kez kuran biri Ö4 klemensini köprüsüz bırakmaya yönelir.
  - Köprüsüz bırakılırsa acil stop zinciri açık kalır: K1 hiç çekmez, F1'deki PC817 #1 ölçümü hep "basılı" okur. Arıza aranırken yanlış yere bakılır.
  - Benim M28 bozmam ("köprüsüz bırakılır" ekledim) denetimden geçti, yani denetim bunu yakalamıyor.
- **Öneri:**
  - 276'ya şu cümle eklenmeli: "klemensin iki ucu kısa tel köprüyle takılı gelir; Ö4 gelene kadar köprü sökülmez (köprüsüz röle çekmez)".
  - K1 kontrol listesine şu madde eklenmeli: "Ö4 klemensinde köprü takılı".
  - `ZORUNLU`'ya "K1: Ö4 … köprü" uyarısı eklenmeli.

### Ü3. Kablo eşlemesi: yol 4'te M02 yanlış; N01 / N02 ve S01 / S05 yanlış sınıfta

- **Bulgu:** `rehber_kablo.py:32` `CAD_ESLEME[4] = ("M03", "M04", "M02")`.
- **Ölçüm:** `taban_parcalar.py` 533-587'deki YOL geometrisi ve `taban-analiz.json` konumları karşılaştırıldı.
  - Motorların konumu: arka sol (-140, ·, -185), ön sol (-140, ·, 185), sağ motorlar x = +140.
  - Yol 4'ün sınır kutusu x -52,5…140,5. Yani yalnız sağ ön ve sağ arka motora ulaşıyor.
  - M02 (sol motor demeti) bu yolda çizili değil. Yol 3 de yalnız ön sol motora ulaşıyor.
- **Öbür eşleme hataları:**
  - Yol 12'nin sınır kutusu z 17,5…162,5. Arka motor enkoderlerine (N01 / N02) ulaşmıyor, ama ikisi "çizilen" sayılmış.
  - Yol 5 ve 7 dağıtım kartından direk boyunca omuza çıkıyor, yani S01–S04 / S05–S08 uzatma demetini çiziyor. S01 ve S05 "çizilmeyen" sayılmış.
- **Yeniden sayım:** yaklaşık 54 çizilen / 20 çizilmeyen. Ajanın ve denetimin sayısı 55 / 19.
- **Denetim neden yakalamıyor:** Denetim yalnız "kimlik tabloda var mı" sorusuna bakıyor. Geometriyle karşılaştırma yapmadığı için bu tür kaymayı göremez.
- **Montajcıya etkisi:** Sahnede yol 4'e tıklayan biri sol motor demetini sağ tarafta arar.
- **Öneri:**
  - `CAD_ESLEME[4]` = ("M03", "M04") olmalı. M02 için yol 3 eşlemesine bakılmalı.
  - N01 / N02 çizilmeyenlere, S01 / S05 çizilenlere (yol 5 / 7) taşınmalı.
  - İsteğe bağlı: `veri_denetle`'ye uç konumu ↔ yol sınır kutusu kaba kontrolü eklenmeli.

## 2. Kayıtlı açık iş olarak gidebilir

Her bulguda yer, ölçüm ve öneri birer satır.

1. **`rehber_denetim.py` zayıf.** Benim 28 gerçek kaynak bozmamdan 20'si kaçtı (§4). Değerleri tablodan okuyor, ama:
   - Kurallar "değer listede var mı" diye bakıyor, "bu bağlamda doğru değer mi" diye bakmıyor.
   - Örnekler: PC817 #1 → GPIO5, şarj 5 A, G22 7,5 A / 16 AWG, XL C 7,5 A.
   - Sıra ve yön ifadelerini hiç sınamıyor: diyot ters, dirençler yer değiştirmiş, "en az 100 ms".
   - **Öneri:** kimlik bağlamlı kurallar eklenmeli (kablo kimliği / sigorta kimliği → tablo değeri).
2. **`ZORUNLU` sabit metin taşıyor** (`rehber_denetim.py:140-`). "7,5 A", "F6 3 A", "GPIO19 sürer" gibi ifadeler doğrudan yazılı. Tablo değişince bayatlar, ve M1'i yalnız bu sabit metin yakaladı. **Öneri:** desenler `kablolar.json` ve pin JSON'undan üretilmeli.
3. **`kaynak_metinler` dar** (`rehber_denetim.py:583-598`). Şunları taramıyor: parça adları ve kodları (Ü1), `rehber_veri.py` / `app.js` / `yazdir.html` metinleri. Yasak taraması kaynak modunda hiç yok. **Öneri:** kapsam genişletilmeli.
4. **`rehber_kablo.py:365`: kol bölümleri türetilemezse yalnız UYARI verip GEÇER diyor.** Kopyada `arayuz` modülü yokken bunu gördüm, eşleme sınaması sessizce dişsizleşebiliyor. **Öneri:** bu durumda çıkış kodu sıfırdan farklı olmalı.
5. **`CAD_ESLEME` elle yazılmış** (`rehber_kablo.py:28`). Ü3 bunun sonucu. Kalıcı çözüm uç konumundan türetmek ya da geometriyle sınamak.
6. **Rehber, §16.7'den iki maddeyi düşürmüş.** `rehber_metin.py:306` "§16.7, §17.7" diye anıyor, ama şunlar yok:
   - §16.7-3: T8 E / E2 tezgâh kısa devre denemeleri (`T8-servo-hatlari.md` 147-184).
   - §16.7-4: K04 kesit yazısı.
   - **Öneri:** iki madde teslim kontrolüne eklenmeli.
7. **KT3 rehberde yok.** Sigorta kutusu yuvalarının ortak baralı mı ayrı mı olduğu teslimde bakılacak; ayrıysa 12 AWG giriş köprüleri gerekir (`elektrik.md` 360-381, `kablolama-on-kararlar.md` KT3). **Öneri:** K1 teslim maddesine eklenmeli.
8. **F2 15 A yedek sigorta rehberde hiç geçmiyor** (`elektrik.md` 360-381). Küçük; sigorta takma adımında "yedek 15 A kutuda" diye anılabilir.
9. **F5 metni kendiyle çelişiyor** (`rehber_metin.py:1349-1350`). "Uç yuvalar yedek … F6 kutunun 6. yuvasında" deniyor, ama 1×6 dizilişte 6. yuva bir uç yuva. Küçük. **Öneri:** "6. uç yuva artık F6'nın" diye yazılmalı.
10. **K04 "0,9 A" yerine "900 mA" yazılmış.** Kuralı karşılamak yerine kuralı atlatan bir çözüm, mA ifadeleri denetimden kaçıyor. **Öneri:** kural daraltılmalı (QLED akımı varsayımı istisna), değer "0,9 A" kalmalı.
11. **Kablo yarıçapı fiilen ayırt edici değil.**
    - Taban CAD tüpleri 2,5 mm sabit kaldı (12 AWG ile 22 AWG aynı görünüyor).
    - Şema tüpleri 2,5–3,0, kol 2,1. Kol eskiden 2,5'ti; incelme var, şişirme yok.
    - Kesite göre okunur bir fark yok. F10f piksel ölçütü kol telinde risk taşıyor (bakılmadı).
12. **Renk karşıtlığı zayıf** (WCAG oranı, `karsitlik` hesabı):
    - Siyah (#222): koyu lejantta 1,00, koyu sahnede 1,07. Toprak teli koyu temada görünmez.
    - Sarı ve beyaz: açık lejantta ≈ 1,9, açık sahnede ≈ 1,58.
    - Turuncu: açık lejantta 2,85.
    - `#808080` inset çerçeve beyaza karşı 3,95, siyaha karşı 4,03. Lejant karesini kurtarıyor, ama sahnedeki tel çerçevesiz.
    - En yakın sınıf çifti beyaz / hazır, ΔE76 19,1.
13. **K2'de renk ayrımı kayboldu.** H02, U03 ve U06 aynı griye düştü; eskiden ayrı renklerdi. Kol tellerinin hepsi sarı. Okunurluk kaybı var, renk = devre sınıfı kuralına uygun. Kare bakışında değerlendirilmeli.
14. **A04 kesin kaldı, yalnız klemens-508 uçlu.** Öbür klemens-508 uçluların durumu teyite çekildi, tutarlılık için bakılmalı. Küçük.
15. **`dongu-158.md` P10.7 satırında "62 kablo" yazıyor**, tablo 74. Bayat sayı.

## 3. Üretim adımında bakılacaklar

`F10h-gunluk.md` §9 komut listesinin yanında şunlara bakılmalı:

1. `rehber_denetim.py` veri modu Ü1 düzelmeden ELEKTRİK ≥ 5 verir, `rehber_uret.py` sıfırdan farklı çıkış koduyla durur. Ü1 önce yapılmalı, sonra üretim.
2. Ü3 düzeltmesi sonrası `rehber_kablo.py` sayısı yaklaşık 54 / 20 olmalı. 55 / 19 görülürse eşleme düzelmemiştir.
3. SEMA dizini kaydı (eski 13 → 11 şema): kare adları ve yazdırma sayfası şema numaraları elle kontrol edilmeli.
4. Koyu temada siyah toprak teli ve açık temada sarı / beyaz teller: iki temada gözle bakılmalı (§2-12).
5. Kol tel yarıçapı 2,1 ile F10f piksel ölçütü yeniden koşulmalı.
6. K2 karelerinde gri tellerin (H02, U03, U06) ayırt edilip edilmediğine bakılmalı.
7. Arayüz kartı ve E4 kafa parçaları kartlarında "MOSFET" ve "USB ses kartı" ifadeleri kalmamalı (Ü1).
8. `rehber_kol_kablo.py --yazma` kaynakta 38 bölüm, yaklaşık 35 s; üretimde aynı sayı beklenir.

## 4. Kendi ölçümlerim

### Denetim koşumları (hepsi çıkış 0)

- `rehber_denetim.py --kaynak`: metin 528, ASCII 0 / elektrik 0 / zorunlu 0.
- `--bozma-denemesi`: 16 / 16.
- `rehber_kablo.py`: GEÇER, 55 / 19 (19 kimlik ajanınkiyle aynı), karışık yollar 3, 5, 7, 9; bozma 9 / 9.
- `kablolar_denetim.py`: GEÇER, bozma 136. Depoda koşuldu, salt okunur; kopyada `origin/main` ve `maliyet.json` yoktu.
- `kablolar_uret.py --kontrol`: güncel.
- `rehber_kol_kablo.py --yazma`: GEÇTİ, 38 bölüm. Koşumdan sonra git durumu değişmedi.
- py_compile: 6 rehber modülü ve `kablolar_denetim.py` geçti. İçe aktarma tamam (SEMA 11, KABLO_AD 12).
- `node --check`: `app.js` ve `yazdir.html` içindeki betik temiz.

### Rehber metni ↔ kayıtlar

- `rehber_metin.py` farkı baştan sona okundu.
- Anahtar kelimeli elektrik cümlesi sayısı 464 (kendi bağımsız listemle). Dağılım: K1 90, F5 66, K2 55, F1 51, E4 50, E3a 28, F3 27, KABLO_AD 17, SEMA 15, öbürleri az.
- Kayıtlarla uyuşanlar:
  - sigorta değerleri ve tipleri (F1 20 A, F3 5 A, F4 5 A, F5 2 A, F6 3 A standart 6. yuva, şarj 7,5 A mini, çevre / G22 2 A mini, XL C 5 A)
  - G kimlikleri ve yıldız yerleşimi (1: G12 / G14 / G15, 2: G13 / G16, 3: G05 / G06, 4: G17 / G18, 5: G20 / G22)
  - diyot yönleri (K1 katot 86, K2 katot bobin +, 1N5819 anot hub tarafı)
  - BC337-40 + 270 Ω seri + 2,2 kΩ taban → GND
  - pinler (K1 GPIO4, K2 GPIO19, PC817 #1 GPIO23, #2 GPIO5)
  - E9 dizisi (en az 300 ms, 500 ms önerilir, K2 en çok 1 s)
  - K52 / K60 / K61 "karar bekliyor"
- Uyumsuzluklar: Ü2 ve §2-6…9.

### Kablo tablosu

- Ölçüm: 8134519 ↔ çalışma ağacı arasında alan alan fark.
- 74 kimlik aynı.
- Değişen alanlar yalnız şunlar: teyit (21), durum (9), sonlandırma (5: G17, A02, A04, K01, K02; köprü ifadesi), K04 notu, `klemens_yerleri` notu, `renk_kurali.ilke`.
- Uç, GPIO, koruma, kesit ve acil stop alanları değişmedi.
- Durum sayısı 22 / 51 / 1 doğru. Durumu değişen 9 kablo (SV1–3, G18, G19, G22, A01, A02, K02) hepsi `BELGESIZ_UC` (modul-vidali / sigorta-kutusu) gerekçeli.

### Eşleme

- 20'den fazla eşleme elle geometriyle karşılaştırıldı: taban yolları 1–12, 11 SEMA eşlemesi, kol bölüm örnekleri.
- SEMA ve kol eşlemeleri doğru. Taban sonucu Ü3.

### Bozma denemeleri

- Yöntem: geçici kopyada `rehber_metin.py` gerçek kaynak metni değiştirildi, her denemede `rehber_denetim.py --kaynak` ayrı süreçte koşuldu.
- Sonuç: 28 deneme, 8 yakalandı, 20 kaçtı.
- **Yakalanan:**
  - M1 BC337-40 #2 GPIO13: yalnız `ZORUNLU` sabit metniyle.
  - M3 "GPIO2 (K2)".
  - M12 ses kartı yolu geri: `;` bölmesi sayesinde.
  - M16 ön şarj 10 Ω.
  - M18 K1 diyotu ters: zorunlu.
  - M23 "kalaylanarak": yalnız ASCII sözlüğüyle, rastlantı.
  - M25 sigortalar ana anahtar açıkken: zorunlu.
  - M26 ana sigorta 40 A.
- **Kaçan:**
  - M2 PC817 #1 → GPIO5
  - M4 şarj 5 A mini
  - M5 çevre 5 A mini
  - M6 G22 7,5 A
  - M7 F6 "(mini"
  - M8 F6 2. yuva
  - M9 XL C 7,5 A
  - M10 MOSFET + ilgisiz "değil"
  - M11 WAGO + ilgisiz "yok"
  - M13 G22 16 AWG
  - M14 kafa giriş köprüsü ≥ 22 AWG
  - M15 dirençler yer değiştirmiş
  - M17 K2 diyotu ters
  - M19 1N5819 ters (SEMA)
  - M20 F5'te G22 sigortası silinmiş
  - M21 K52 kararlaştırılmış gibi
  - M22 K61 kararlaştırılmış gibi
  - M24 "en az 100 ms"
  - M27 tünel kontrol maddesi silinmiş
  - M28 Ö4 "köprüsüz bırakılır"
- **Yöntem notu:** İlk koşumda M3 "kaçtı" göründü. Nedeni şuydu: dosya aynı saniye içinde aynı boyda yeniden yazılınca Python önbelleğe alınmış eski derlemeyi kullandı. Denemeler `-B` ile, önbellek silinerek yeniden koşuldu; yukarıdaki sonuç o koşumun. Gerçek kaynak dosyasını değiştirip ayrı süreçte koşan her bozma aracı aynı tuzağa düşebilir.

### Sınırlar ve gizlilik

- `git diff 8134519 --stat -- kod planlama/adim3/pin-haritasi.md rehber/veri rehber/goruntu planlama/rehber` boş. `main`'e dokunulmadı, kontrol raporları değişmedi.
- Paketin eklediği satırlarda yerel yol, e-posta ve kişisel veri taraması temiz. Yalnız "masa" sözcüğü eşleşti. Rehberde "Ahmet" adı izinli kullanımda.
- Çalışma ağacındaki 13 `kabuk/gorsel/*.png` ve `montaj/yerlesim-kontrol.json` bu paketten değil (brief'te belirtildiği gibi).

## 5. Bakılmadı

- Üretilmiş rehber verisi ve kareler (yeni üretim yok). Ü1 eski veriden ve kaynaktan çıkarıldı, yeni üretimde koşmadı.
- İki temada gözle bakış, PDF, yazdırma sayfası çıktısı.
- F10f piksel ölçütü.
- Tıklayınca tablo bilgisinin (`kabloBilgi`) tarayıcıda çalışması. Yalnız kaynak ve `node --check` ile bakıldı.
- T8 / KT denemelerinin gerçekte koşması.
- `rehber_kablo` için geçerli ama yanlış kimlik, renk ya da çap elle değiştirilmiş veri bozmaları: benzetilmiş veri yok, yalnız kaynaktan değerlendirildi (§2-4, §2-5).
