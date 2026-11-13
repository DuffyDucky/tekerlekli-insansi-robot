# F10f ikinci bağımsız bakış (düzeltme turu 1'in kontrolü), 12.11.2026

Kontrolcü: ayrı ajan (B2). Düzeltme ajanının günlüğünü (`F10f-gunluk.md` § Düzeltme turu 1) iddia olarak okudum; aşağıdaki sayılar
kendi ölçümüm. Geçici dosyalar scratchpad `f10f-b2/` içinde. Depoda yazdığım tek dosya bu rapor. Üretici, depodaki doğrulama
betikleri ve FreeCAD koşulmadı. İlk kontrolcünün (B) scratchpad betikleri yalnız kopyalanarak kullanıldı.

## 1. Hüküm

**DÜZELTME GEREKLİ.** İlk kontrolün iki yüksek bulgusu (birim, geniş istisna) kapandı. Metin çelişkisi ve ayna farkı da kapandı.
Paket yine de geçmiyor. Nedenler önem sırasıyla:

1. **625ZZ rulmanı (44.1) yuvasının omzundan geçiyor (orta-yüksek, yeni).** p0571 ↔ p0583 ve p0628 ↔ p0640, −x / +x uçuşta dirsek
   çatalının içinde 1,55 mm derinlikte. t 0,5–10 mm boyunca süreklilik var. Rehber "temiz" diyor; bunun tek nedeni dinlenme kör
   noktası: duruşta 0,06 mm örtüşen çift yol boyunca dışarıda bırakılıyor. Ölçüm `geo_ucus` / `diag571`.
2. **Okurluk hedefi tutmuyor: zor 5 / 14 (hedef ≤ 4).** 41.4 / 41.5'te tambur ve duvar kenar çizgisi yok. −45 tambur ucu 31 / 39 px.
   48.2 / 48.3'te iki ek tek çizgide hâlâ seri okunuyor. Ölçüm `b2_kare` ve bölüm 5.
3. **42.1 ve 42 patlatma / sıra görünümü iki ön kolu da gizliyor (orta, yeni).** HEAD'de yalnız sağ ön kol gizliydi. Şimdi servo ve
   somunlar referanssız havada duruyor. Ölçüm `b2_parca`: HEAD ↔ şimdi kare farkı.
4. Küçükler (düşük):
   - 40.2 / 41.2'de S2 uzatma ucunun yeri yanlış.
   - Eski tür dize anahtarlı istisna sessizce kabul ediliyor (M8).
   - F4'te iç terim "F10f sıra denetimi".
   - PDF'te kare içi lejant yaklaşık 2,5 pt.
   - Metin denetimi iç ↔ dış takasını yakalamıyor (T4, T9).

Devir a (gizli parçalar): ayrı iş. Bu pakette kötüleşmedi, paketi durdurmaz (bölüm 4).

## 2. İlk kontrolün bulguları

| # | Bulgu | Durum | Ölçümüm |
| --- | --- | --- | --- |
| 1 | G4 açıları mm yazılmış | **kapandı** | G4 metni artık derece: 125,3° / 10,2° ve 10,1° / 74,9°. Kaynak `s1_poz`: a_i 125.349 / 10.130, a_o 10.159 / 74.940; `kablo_yolu` belgesi a_i / a_o'yu derece diye tanımlıyor. Güncel veride `metin_denetle`: 28 sayı, eksik 0, birim_hata 0. 12'den fazla sayıyı elle kaynakla karşılaştırdım, doğru. Bozma sınaması (`metin_dok`, 12 deneme): mm / cm / ° takası birim_hata verdi (T1, T6, T10, T11, T12). "m", "rad" ve birimsiz yazım eksik verdi (T2, T3, T5, T7, T8); bu durumda da denetim kalıyor. **Yakalanmayan:** iç ↔ dış değer takası (T4) ve doğru sayının yanına yanlış birimli fazladan bir geçiş (T9). Küçük boşluk: "L 171,4 mm (−5…0)" toleransında birim yok (kaynak L_tol mm). |
| 2 | F10f-K1 istisnası geniş | **kapandı** (yeni bulgu 3.1 ayrı) | 40, 41, 42, 44 ve 48. adımlarda 100 satır: çarpışan 0, istisna 10, istisna_bos 0. Önceden temiz olup istisnada duran 8 satır (horn vidası 2, ψ226 2, bilezik pulu baş 4) artık istisnada değil, temiz. Rehberin kendi fonksiyonuyla mutasyon (`ucus2`): M1 (S2 horn eski yön) yakalandı, M2 (çatal eski yön) "asan", M3 (somun d 25) yakalandı, M4 (kullanılmayan anahtar) istisna_bos, M5 (pay 1 mm daraltıldı) "asan", M6 (kaset yana) yakalandı, M7 (pul ters) yakalandı. **M8:** eski tür dize anahtar ("Kaset cıvatası") sessizce kabul ediliyor, istisna_bos'a girmiyor. Kol adımlarında eski tür anahtar sayısı 0, bu yüzden düşük. Bağımsız denetçim (köşe + yüz ağırlık merkezi, sargı sayısı içerde testi, 1 mm adım, eşik dinlenme + 0,2): yeni yönlerin hepsi temiz. Bunlar S2 horn +z, üst kol tüpü −y 76,1, kaset gövdesi +z 75,7, dirsek servosu −z, bilek servosu (mil −y), dirsek kontra somunu iki yan, çatal-horn cıvatası (pulla), bilezik pulu somunu iki yan, bilezik kontra somunu iki yan. Aynı denetçi eski yönleri yakaladı: 4,23 / 1,8 / 1,64 mm (`kk1`). İstisnada kalan 2 karar türünün notları (K1-a, K1-b) açık: seçenekler, ölçüm, öneri, ölçülmeyen. Bağımsız ölçümüm (`geo_karar`) notlarla uyuşuyor. K1-a mevcut: p0116 1,67 ve p0118 2,48 mm engel; C seçeneği (+x ve −y) temiz. K1-b mevcut: p0573 3,0 mm; vida sonra takılırsa temiz. |
| 3 | 41.4 / 41.5 kıyaslanamıyor | **kısmen** | Aynı kamera ve aynı renk; öbür duruş iki temada da soluk iz. Lejant sırası biraz farklı; mini-yer y 1220–1260 ↔ 1220–1320. Tambur ve duvar kenar çizgisiyle çizilmemiş (grup `kenar` bu iki karede yok). −45 tambur ucu ekranda 31 px (açık) / 39 px (koyu). `ucOrtu`: p0118 mafsal cıvatası ucun 32,6 mm önünde. Rulmanın saydam olması yanıltmıyor ama ucu tam açmıyor. Kare başına zor; kıyas "anlaşılmıyor"dan "zor"a çıktı. |
| 4 | 40.2 ↔ 48.2 çelişkisi, uç nerede bekliyor | **kapandı** (küçük kalıntı 3.4) | Tek döşeme sırası var; 40.2 ↔ 48.2 tutarlı. "F4'te dışarı alınan uçlar" kalktı, yerine "uzatma kesintisiz, ek yok" geldi. JR'nin yeri kaynakta tanımlı (y −122…−62); 48.2 bunu doğru veriyor. |
| 5 | S2 0° lopu pigtail | **kısmen** | Ayrı menekşe renk (`#8a2be2`) ve lejant notu "çizim S2 0°, aralık dışı". Karede hâlâ sıkı kıvrım görünüyor. Uyarı artık görünür; şeklin kendisi düzelmedi (seçilen yol buydu). |
| 6 | Demet kalınlığı S2 0° çakışması | ölçülmedi | Tasarım dışı duruş (5'e bağlı). Yeniden ölçmedim. |
| 7 | "voksel" okur metninde | **kapandı** | Okur metninde yok. Yerine yeni bir iç terim girdi: F4 madde 2'de "F10f sıra denetimi … el zarfı" (3.5). |
| 8 | Lejant kırmızı kare | **kapandı** | Kol şemaları lejantta kendi renk ve adıyla. Kırmızı "Kablo yolu" karesi yok (kareler, iki tema). |
| 9 | 36.5 sol ucu | **kısmen** | Uzatma rengi değişti (ΔE76 uzatma ↔ K2 camgöbeği 141,3). İç uç ekranda hâlâ 0 px; `ucOrtu` null (ekran dışı / kadraj kenarı). Kare açık sayıldı. |
| 10 | Ayna asimetrisi | **kapandı** | Bilek / dirsek kulak cıvatası iki yanda d 65 (HEAD: sol 100,7 / 50). Sol ön kol artık sağ gibi "yerinde", d 0 (`ayna`). |
| 11 | Kökte boş `rehber_metin.py` | **kapanmadı** (bilerek) | Dosya duruyor (0 bayt, 09:22, dokunulmamış). Günlük bırakıldığını söylüyor. Silme kararı Ahmet'in. |
| 12 | "icinde" testi yalnız kutu | **kısmen**, ölçülmedi | Kod okuması: `rehber_kol_kablo.py` 612–641'de artık `M.icinde` + `_icinde3` (üç yön ortak parite) var. Sınamasını koşmadım. |

## 3. Yeni bulgular

### 3.1 Orta-yüksek: 625ZZ uçuşu yuvadan geçiyor (44.1), dinlenme kör noktası

- **Ölçüm:** p0571 (sağ 625ZZ) ↔ p0583, p0628 (sol) ↔ p0640. −x / +x uçuşta dirsek çatalının rulman yuvası omzunda 1,55 mm derinlik,
  t 0,5–10 mm boyunca. Ters yön (+x) ön kola 4,17 ve servoya 9,75 mm giriyor. +y (HEAD yönü) çatala 7,25 mm giriyor.
- **Neden rehber görmüyor:** `Giris.yon` / `yon_gercek` duruşta örtüşen çifti (burada 0,06 mm, yuva sıkı geçme) yolun tamamında
  dışarıda bırakıyor. Daha derin girişler de bu yüzden sayılmıyor. Diğer bulgular dışında kalan aynı türden çiftleri taramadım.
- **Öneri:**
  1. Rulmanı çatala önceden pres et ve çatalla birlikte +y uçur. Horn vidası hariç bu temiz (`geo_karar` "625-44.1-catalla+y":
     hareketli p0562 + p0571 + p0583, d 63,5, asan {}).
  2. Bunu K1-b notuna, K1-a C seçeneği gibi ekle.
  3. Kör nokta için: dinlenme derinliğini çift başına eşik olarak al (derinlik > dinlenme + pay ise çarpışma). Çifti tümden dışarıda
     bırakma.

### 3.2 Orta: 42.1 ve 42 patlatma / sıra görünümünde iki ön kol da gizli

- **Ölçüm (`b2_parca`, HEAD ↔ şimdi):** HEAD'de yalnız sağ ön kol gizliydi, sol çiziliyordu. Şimdi ikisi de gizli; dirsek servoları ve
  kontra somunlar referanssız havada.
- **Neden:** Sol ön kol artık "yerinde" (u 0, d 0). Patlatma d 0 parçaları çizmiyor. Uçuş denetimi de d ≤ 0'ı atladığı için uyarı
  çıkmıyor.
- **Öneri:** Patlatmada d 0 taban parçalarını yerinde çiz. Ayna düzeltmesi bunu açığa çıkardı; bulgu 10'u bozmadan çözülmeli.

### 3.3 Orta: okurluk zor 5 / 14, hedef ≤ 4 (ayrıntı bölüm 5)

- **41.4 / 41.5:**
  - Tambur ve duvara `kenar` ekle; 41.2 / 41.3'te iş görüyor.
  - −45 ucunu örten p0118 mafsal cıvatasını (32,6 mm önde) bu iki karede saydam çiz.
- **48.2 / 48.3:**
  - İki ek arasındaki bilek uzatma parçası servo turuncusuyla çiziliyor; uzatma rengine al.
  - JR ve lehim noktasına 40.x'teki gibi bağ işareti koy. Ekler o zaman seri değil, iki ayrı nokta okunur.
- **41.3 açık tema:** kenar çizgileri soluk. Kenar rengini açık temada koyulaştır.

### 3.4 Düşük: S2 uzatma ucunun yeri

40.2 / 41.2'de "kol ucu tüp penceresinde" S2 uzatması için yanlış. S2 uzatması G2'de göbekte ekleniyor. Öneri: S2 için "göbekteki G2
ekinde" yaz.

### 3.5 Düşük: okur metninde iç terim

F4 madde 2'de "F10f sıra denetimi … el zarfı" geçiyor. Öneri: "elle ulaşılabilirlik ölçüldü" gibi okur diline çevir.

### 3.6 Düşük: istisna anahtarı ve metin denetimi açıkları

- **M8:** eski tür dize anahtar sessizce geçiyor. Öneri: dize anahtarı hata say ya da istisna_bos sayımına kat.
- **T4 / T9:** metin denetimi sayıyı ve birimini arıyor, sıra / konum eşlemiyor. Öneri: G4'te değeri etiketiyle ("iç koşu … X°") eşle.
  Bir sayının metindeki her geçişini birimiyle denetle.
- "L 171,4 mm (−5…0)" toleransına "mm" ekle.

### 3.7 Düşük: `tak()` değişikliği

- **Değişiklik:** `app.js` `tak()` artık yalnız `onceden` olanları değil, barındırılan her parçayı atlıyor.
- **Ölçüm (`b2_reg`, kol dışı 14 adres × 2 tema, ilk turun kareleriyle):**
  - 13 adres 0–1 px.
  - Adım 0'da 47 / 58 px fark var, kutu x 324–468, y 237–282 (ısıl gömme somun bölgesi).
- **Değerlendirme:** Durağan karede küçük. Nedeni (sıra canlandırması mı, başka bir şey mi) ölçülmedi. Öneri: adım 0 sıra
  canlandırmasına bakılsın.

## 4. PDF ve devir a

**PDF (`pdf`, `pdf2`):**
- 74 sayfa, 16076 kB. En küçük metin 8,1 pt.
- 121 görüntü, boş 0.
- Yeni alt adım kareleri var: sayfa 59 (40.x), 61 (41.2–41.6), 71 (48.x).
- Kareler 1200 × 720 px, sayfada 215,2 × 129 pt basılıyor. Kare içi lejant (1000 px tuvalde CSS 12 px) bu ölçekte yaklaşık 2,5 pt, yani
  okunmuyor (düşük-orta). Renkler ve yollar seçiliyor.
- Öneri: PDF'te lejantı karenin dışına metin olarak bas, ya da kablo karelerini tam genişlikte koy.

**Devir a (`parca_kare`, görünmeyen parça):**
- Açık temada 123 / 206, koyuda 122 / 206. İlk üretimle aynı.
- En kötü konumlar: 42.1 36 / 44, 39 20 / 26, 48.4 16 / 16, 44.1 15 / 26, 38 14 / 14, 40.1 14 / 26.
- Nedenler yapısal:
  - (sağ + sol) alt adımlarda tek kamera var, sol parçalar gövdenin arkasında kalıyor (p0194 kol çatalı sol 0 px, p0200 tüp sol 0).
  - 42.1'de servolar opak ön kolun içinde (p0597 0, p0654 0).
  - Rulman ve pimler çatalın içinde.
  - Küçük bağlantı elemanları yalnız işaretle görünüyor.
- HEAD ↔ şimdi, ana adımlar, 15 parça × 2 tema: kötüleşen parça yok.
  - p0644 471 → 434 px (açık), 178 → 168 (koyu).
  - p0562 yaklaşık −%1,3.
  - p0127 48. adımda iyileşti.
- **Hüküm: ayrı iş, paketi durdurmaz.**
- Öneriler: 42.1'de ön kolu saydam çiz; sağ / sol alt adımları ayır ya da sola ayrı kamera ver; işaretleri açık tut.

## 5. Kare sınıflaması

İki temanın kötüsü sayıldı. Yöntem: `b2_kare` ile 1400 × 900 çekim, gözle okuma. Şema görünürlüğü `b2_fark` ile ölçüldü (gizle /
yeniden çiz, Σ|ΔRGB| > 24, mini / lejant / mini-yer hariç, `isaret=0`).
- 32 şema × 2 tema = 64 ölçüm. Hepsi görünür; en az 1135 px (sema40, açık).
- 64'ün 64'ünde fonksiyon = ekran.
- ΔE76: uzatma ↔ S2 lopu 26,9, ↔ K2 camgöbeği 141,3, ↔ `#6c5ce7` 50,7. Beyaz bağ ↔ uzatma 125,3.

| Kare | Açık | Koyu | Sonuç | Not |
| --- | --- | --- | --- | --- |
| 36.4 | açık | açık | açık | |
| 36.5 | açık | açık | açık | iç uç 0 px |
| 40.2 | açık | açık | açık | çekince: sıkı kıvrım; menekşe ↔ magenta yakın (ΔE 26,9) |
| 40.3 | açık | açık | açık | aynı çekince |
| 41.2 | açık | açık | açık | tambur / duvar kenarı okunuyor |
| 41.3 | zor | açık | zor | açık temada kenar çizgisi soluk |
| 41.4 | zor | zor | zor | tambur / duvar kenarı yok, −45 ucu 31 / 39 px, p0118 önde |
| 41.5 | zor | zor | zor | tambur / duvar kenarı yok |
| 42.2 | açık | açık | açık | |
| 42.3 | açık | açık | açık | |
| 44.2 | açık | açık | açık | |
| 44.3 | açık | açık | açık | |
| 48.2 | zor | zor | zor | iki ek tek çizgide seri okunuyor; bilek uzatma parçası servo turuncusu |
| 48.3 | zor | zor | zor | aynı |

**Toplam:** zor 5 / 14 (hedef ≤ 4), anlaşılmıyor 0. Günlükteki "zor 3 / 1" ile uyuşmuyor; fark 41.3 açık ve 48.x.

Gizli parçalar (`b2_fark`, isaret = 0, açık / koyu px):

| Parça | Açık / koyu px |
| --- | --- |
| p0590 | 0 / 0 |
| p0569 | 0 / 0 |
| p0584 | 0 / 0 |
| p0583 | 0 / 0 |
| p0628 | 16 / 22 |
| p0641 | 6 / 9 |

Günlükteki iddiayla uyuşuyor. İşaretler açıkken halka ve "×2" etiketi konumu gösteriyor (610–682 px değişim).

**Zincir ve regresyon:**
- **Durum dosyaları günlükle uyuşuyor:** kk2 2, uret1 2, uret2 0, hizli1 0, zin3 0 (tüm adımlar 0). zin2'de bitiş satırı yok; günlük
  durdurulduğunu söylüyor.
- **Sıra:**
  - Son kod değişikliği 20:19 (rehber_metin), app.js 19:18, denetim 18:50.
  - zin3 başlangıcı 20:22:47.
  - Çıktılar: veri 20:23, kareler 20:23–20:39, PDF 20:39, kontrol.json 21:06, F10f-dogrula.json 21:16, F10e 21:32, F10d 21:45,
    F10a 21:53.
- **HEAD ile aynı olanlar:**
  - `robot.glb` / `robot-glb.js` özetleri.
  - F10a, F10d, F10e, F9b, regresyon, carpisma_kos ve arayüz sonuçları.
- **Diğer:**
  - 19 ASCII sözcüğün hepsi doğru Türkçe; hiçbiri bir denetimi boşa çıkarmıyor.
  - Korunan dosyalar (kabuk png, yerlesim-kontrol.json) paketten eski.
  - Veri ↔ HEAD: 1192 parça. Değişen alanlar u 38, d 30, h 12; a / b değişmedi.
  - Kol dışı 14 adres × 2 tema ilk turun kareleriyle: 13 adres 0–1 px, adım 0 47 / 58 px (3.7).
- **Kural taraması:** değişen F10f dosyalarında (rehber betikleri, app.js, F10f-*.md / py / json) yerel kullanıcı klasörü yolu ve
  takma ad geçmiyor. Depodaki eşleşmeler pakete ait olmayan eski dosyalarda.

## 6. Ölçülemeyenler

- **121 konumun konsol (hata / uyarı) taraması.** Bellek dar olduğu için (yaklaşık 2 GB boş) ayrı tarayıcı turu açmadım.
- **Adım 0 sıra canlandırmasında `tak()` değişikliğinin etkisi.** Yalnız durağan kare kıyaslandı (3.7).
- **İlk kontrolün bulgu 6'sı (demet kalınlığı, S2 0°) ve bulgu 12'nin sınaması.** Kod okundu, koşulmadı.
- **3.1 dışında, dinlenme kör noktasına düşen başka çiftler.** Tüm rehberde taranmadı; yalnız 40–48 kol adımları denetlendi.
- **K1-a / K1-b önerilerinde alet erişimi** (tornavida / anahtar yolu). Notlar da bunu ölçülmedi diye yazıyor.
- **PDF'in basılı kopyada okunması.** Yalnız pt hesabı yapıldı.
- **FreeCAD tarafı (kaynak model) ve üretici yeniden koşusu.** Kısıt gereği koşulmadı.
