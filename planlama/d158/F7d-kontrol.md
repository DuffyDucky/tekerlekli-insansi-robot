# F7d kontrolü (P7.4, rehberde son düşükler + demo metni): bağımsız kontrol ajanı B, 09.11.2026

**Kapsam.** Brief `planlama/d158/F7d-brief.md`; A'nın çıktısı `planlama/d158/F7d-gunluk.md`, `planlama/rehber/R-gunluk.md` ve rehber
dosyalarındaki `git diff`. F7c bulgularının kaynağı `planlama/d158/F7c-kontrol.md` (D-5, D-6', D-7, D-8, D-9, D-10). Elektrik kaynağı
`planlama/adim3/elektrik.md`. A'nın günlüğüne dayanılmadı; her sayı aşağıdaki komutlarla yeniden ölçüldü.

**B'nin çalışma koşulları.**
- Çalışma klasörü scratchpad `f7d_B/` (A'nın `f7d/` klasörü kullanılmadı). Betikler: `enjekte_b.py`, `n_a.py`, `oneri_yama.py`,
  `pdf_olc_b.py`, `ad_tara_b.py`; kopyalar `denetim/`, `denetim_head/`, `denetim_oneri/`, `demo_kopya/`, `uret/`, `sayfa/`.
- FreeCAD koşulmadı, kilide yazılmadı (kilit "boş", 6 bayt; FreeCAD süreci 0).
- Git'e yazılmadı; commit, push, silme, checkout, reset, stash yok. Python `-B` ve `PYTHONDONTWRITEBYTECODE=1`.
- Depoya yazma yok: kontrol başı ve sonu `git status --porcelain -uall` ve sha1 listeleri karşılaştırıldı. Aradaki farkların hepsi F9d ya
  da orkestratörün (`README.md`, `planlama/dongu-158.md`, `planlama/y2/Y2a-brief.md`, `Y2b-brief.md`, `planlama/y3/Y3-brief.md`,
  `tasarim/freecad/README.md`, `qled-cerceve-tasarim-notu.md`, `F9d-gunluk.md`, `F9d-tarama.py`). F7d'nin 17 dosyası kontrol boyunca
  değişmedi. Bu dosya tek istisna.

## Genel karar

**KOŞULLU.** Kritik bulgu yok. Rehber metni kaynağa dayanıyor; "doğrulanmadı" işaretleri doğru yerde. Üretim, PDF, demo, tarama,
regresyon, ad ve yol kontrollerinin hepsi 0. İki orta bulgu var, ikisi de küçük düzeltme:
- **O-1:** D-7 düzeltmesi denetime yeni bir kaçak açtı. "Ana anahtar açıkken birkaç saniye sonra F1 sigortasını tak" artık yakalanmıyor;
  HEAD'deki denetim yakalıyordu.
- **O-2:** Şarj girişi rehbere girdi, ama iki eksik var:
  - kolun akü XT60'ının hangi tarafından alınacağı yazmıyor. Rehberdeki "akü ayrık = enerjisiz" güvencesi buna dayanıyor;
  - F5 notu sigortayı "ilk şarjdan önce" taktırıyor. Bundan sonra XT60E-M **erkek** panel konnektörün pimleri akü bağlı olduğu sürece
    gerilimli; ana anahtar da mantar da bunu kesmiyor. Rehberde bu konuda uyarı yok.
  - Konnektörün cinsi karar adayı (KT-F7d-1, aşağıda).

| Önem | Sayı | Bulgular |
|---|---|---|
| kritik | 0 | — |
| orta | 2 | O-1, O-2 |
| düşük | 7 | D-1 … D-7 |

**Koşul.** O-1 için `_SINIR` yaması (aşağıda; B kopyada denedi) uygulanmalı. O-2 için K1, F1 ve F5 metnine iki cümle eklenmeli. Bunlarla
rehber ve denetim yeniden üretilir. Düşük bulgular engelleyici değil.

Orkestratör O-1 ve O-2'yi sonraki tura bırakmayı seçebilir. Gerekçe:
- gerçek veride yasak 0;
- rehber şarj sigortasını hiçbir adımda taktırmıyor, yani rehberin kapsadığı sürede şarj pimleri enerjisiz.

Bu durumda commit bugünkü hâliyle de güvenli. Ancak O-2'nin F5 notu rehberden sonraki ilk şarja talimat veriyor; uyarısız kalmamalı.

## Madde sonuçları

| # | Madde | Sonuç |
|---|---|---|
| 1 | D-5, D-6', D-7, D-8, D-9, D-10 | D-5, D-8 ve D-9 **kapalı**. D-6' **kısmen** (S3 hâlâ kaçıyor, D-1). D-7 **kapalı**, ama yeni bir kaçak açtı (O-1). D-10 **kısmen** (O-2) |
| 2 | Şarj girişi | rehberin kapsadığı sürede pimler enerjisiz (sigorta iki aşamada da takılı değil). Kol yeri ve sigorta takıldıktan sonraki uyarı eksik (O-2). Karar adayı: KT-F7d-1 |
| 3 | Denetim | gerçek veride yasak 0, zorunlu 0 / 35. B'nin yeni denemeleri: 20 enjeksiyondan 11'i yakalandı. Kaçanlardan 3'ü gerileme (O-1), 6'sı bilinen sınır (D-3). Olumsuz denemeler: 6 / 6 temiz. Nesne listesi sınırını yoklayan 4 cümlede yanlış alarm çıktı (D-2). F7c regresyonu: J1–J20 ve K1–K11 31 / 31 yakalandı, P1–P8 8 / 8 temiz, S1–S3'te 2 / 3 |
| 4 | PDF | 54 sayfa (PyMuPDF ve pypdf). En küçük yazı 8,10 pt; 8 pt altı 0; taşan 0; alt bilgi 54 / 54 doğru. Eşleme `kontrol.json` ile aynı. B'nin üretimiyle metin 54 / 54 aynı. 6 sayfa görüldü |
| 5 | Rehber bütünlüğü | 50 / 50, konsol 0, 1192 ↔ 1192, 360 px 7 × 0. Görüntüler 20:28–20:31'de üretilmiş, veriden (20:26) sonra; içerikleri yeni metni gösteriyor. B'nin `--veri-yok --cikti` üretimi 0 |
| 6 | Demo | şablon farkı yalnız "Bu sayfa hakkında"; `demo_uret.py` kopyada bayt bayt aynı; `F9b-dogrula.py` 0. 8 denetim betikle uyuşuyor; bir ifade biraz fazla iddialı (D-5) |
| 7 | README | F9d'nin alanı; çalışma ağacında "(54 sayfa)" yazıyor. Commit sırası bulgusu (D-6) |
| 8 | Bütünlük | tarama 0, regresyon 0. 17 dosyada takma ad 0, soyad 0, yerel yol 0. Liste tam, F9d dosyası karışmamış |

## 1. D-bulguları tek tek

Kaynakları B kendisi açtı:
- `elektrik.md`: `:41`, `:59-68` (göğüs ekranı dalı), `:91`, `:229-269` (E2, E3), `:323-341` (blok şema), `:360-380` (sigorta listesi);
- `testler/00-genel.md` (kural 1, 7, 8, multimetre kuralı, alet listesi) ve `T7-gogus-ekrani-12v.md`;
- `maliyet.json` `:85`, `:86`, `:92`, `:93`, `:111`, `:122`;
- `raporlar/kaynaklar/06-aku-secimi.md:163-165`, `tasarim/freecad/taban/rapor.html` "Servis erişimi".

Adım metinleri `rehber_metin.ADIM` ile `rehber-veri.json` arasında 49 adımda alan alan karşılaştırıldı: fark 0.

### D-5 + D-9 (F3, göğüs regülatörü): **kapalı**

**Sıra.** Akü ayrıkken uçlar bağlanır → ana anahtar kapalıyken akü XT60'tan takılır → ana anahtar açılır → çıkış okunur → ana anahtar
kapatılır → akü XT60'tan ayrılır → ölçü uçları sökülür → HDMI ve 12 V fişi enerjisizken takılır.
- Veride "enerjiyi kes" 0 kez geçiyor.
- Sıra `00-genel.md` kural 7 ile ("ölçü ucu enerji yokken bağlanır") tutarlı.
- Kaynakta adım sırası yok; metin bunu "Ölçüm sırası ve ölçü noktası kaynakta yok, doğrulanmadı" diye yazıyor. **Doğru.**

**Ölçüm anında enerjili dallar** (K11 a). F1 aşama 1'den sonra takılı olanlar ana 30 A, F4 ve F5; F3'te göğüs 2 A eklenir. Ana anahtar
açılınca yalnız F4, F5 ve göğüs dalı enerjilenir.
- F1 takılı değil: K2 tıklasa da bara enerjisiz (`:440-445`).
- F3 takılı değil: Pi enerjisiz.
- Bu durumda hareketli parça yok; sıra güvenli.

**K11 b.** 12 V fişi F3'te takılmaz, ucu bantlı kalır.
- F5 aşama 2'de ölçü ucu akü ayrıkken bağlanır, tel erişim alanının dışına çıkarılır, değer dışarıdan okunur.
- Fiş, akü ayrıldıktan sonra takılır.
- D-9'daki "ölçümsüz fiş" kapandı; T7'deki "ekrana bağlamadan" kuralına uyuyor.

`ZORUNLU` F3 ×5 satırı var; B9 (sıra bozma) ve B10 ("DC A") ile denendi, ikisi de yakalandı.

### D-8 (multimetre kademesi ve uç): **kapalı**

- "DC V, kırmızı uç V soketinde" doğru. `00-genel.md` multimetre kuralı 2 ve 4'e dayanıyor.
- "10 A soketinde kalırsa bu noktayı GND'ye bağlar ve F5 2 A atar" fiziksel olarak doğru (E3: F5 → mantar NC → PC817 #1 düğümü).
- "20 V aralığı (akü en çok 14,6 V)": 14,6 V `:234`'te geçiyor. Aralığın kendisi çıkarım ve metinde "doğrulanmadı" yazıyor.
- "PC817 #1 giriş klemensinin + ucu" ve "regülatör çıkışının + / − klemensi (kart üstü yazıya göre)" metinde "doğrulanmadı" olarak
  işaretli. Doğru.

**F1 madde 3, mantar NC süreklilik denemesi:** güvenli.
- Deneme mantar bağlanmadan önce yapılıyor ("Bağlamadan önce … Sonra K1'de bırakılan ucu bağla"), yani mantar devreden yalıtık.
- Adım başlığı "Bağlarken akü ayrık" diyor, metin de "(akü ayrık …)" diyor.
- Süreklilik kademesi alet listesinde var (`00-genel.md:73`). Denemenin kendisi kaynakta yok; metinde "doğrulanmadı" yazıyor.

### D-10 (şarj girişi): **kısmen**, O-2'ye bak

**Kaynağa uyan kısım.** Kol K1 madde 1'de kablolanıyor, konnektör F1 madde 5'te takılıyor. Şarj 10 A iki listede de "takılı değil":
F1 aşama 1 ve F5 aşama 2. Dayanaklar:
- `:372`: "XT60 şarj girişi → akü + (ana anahtar öncesi)", "dördüncü kapaklı yuva";
- `:41`, `:91`;
- `taban/rapor.html`: "Şarj: akü yerinde, ayrı XT60 şarj girişinden (konum önerisi: etek üst plakası arka; kabukta delik gerekir, açık iş)".

Yer, bağlantı noktası ve takılma sırası metinde "doğrulanmadı" olarak işaretli. Rehberin hiçbir adımı şarj sigortasını taktırmıyor, bu
yüzden rehberin kapsadığı sürede pimler enerjisiz. Güvenli.

**Eksikler:** O-2.

### D-6' (denetim boşlukları): **kısmen**

- K1 "birleştir", K3 "birbirine bağla", K5 "açtıktan sonra … tak", K6 "röleyi elle kapat": yakalanıyor.
- S1, S2 ve K11 (sökme sırası) için `ZORUNLU` satırları eklendi.
- **S3 hâlâ kaçıyor (D-1).**

### D-7 (120 karakterlik pencere): **kapalı**, yeni kaçak O-1'de

Eski P5 temiz; A'nın N1–N4'ü de B'nin NB1–NB3'ü de temiz. Ancak çıplak sıra bağlacında kesmek yeni bir kaçak açtı (O-1).

## 2. Orta bulgular

### O-1 · Pencere sınırı yeni kaçak açtı (D-7 düzeltmesinin yan etkisi)

`_SINIR` iki ifade türünde pencereyi kesiyor: sıra bağlacında ("sonra", "bitince", "ardından", "sonunda", "en son") ve enerjiyi bitiren
ifadenin kökünde ("aküyü ayır", "enerjiyi kes"). Bu iki yoldan iki kaçak açılıyor:
- Tehlikeli talimatın ortasındaki bir zaman ifadesi fiili pencerenin dışında bırakıyor.
- Kök olumsuz eki de tutuyor: "ayırmadan" "ayır" ile, "kesmeden" "kes" ile eşleşiyor.

| # | Cümle | HEAD denetimi | F7d denetimi |
|---|---|---|---|
| B19 | F5: "Ana anahtar açıkken birkaç saniye sonra F1 sigortasını tak" | yakaladı | **kaçtı** |
| B20 | F3: "Enerji varken ölçüm bitince göğüs 12 V fişini tak" | yakaladı | **kaçtı** |
| B13 | F3: "Ana anahtar açıkken aküyü ayırmadan 12 V fişini tak." | yakaladı | **kaçtı** |

B19 doğal bir cümle ve K5'in ("açtıktan sonra … tak") eş anlamlısı. Gerçek veride bugün 0, bu yüzden orta.

**Öneri** (B scratchpad kopyasında denedi; `oneri_yama.py`). Çıplak bağlaç kesmesin. Yalnız enerjiyi bitiren ifade kessin, o da olumsuz
ekli değilse:
```
_SINIR = (r"(?:\bana\s+anahtar\w*\s+kapat|\bakü\w*\s+(?:XT60\S*\s+)?ayır|\bXT60\S*\s+ayır|\benerjiyi\s+kes)(?!ma|me)")
```
Yamalı kopyanın sonuçları:
- gerçek veride yasak 0, zorunlu 0 / 35;
- B13, B19 ve B20 yakalandı;
- J/K 31 / 31, P1–P8 8 / 8 (P5 dahil), NB1–NB6 6 / 6 ve A'nın N1–N4'ü 4 / 4 temiz kaldı.

Kısacası D-7'nin istediği doğru cümleler yine geçiyor. B14 ("enerjiyi kesmeden … değiştir") yamada da kaçıyor; bu HEAD'den kalma bir
sınır (D-3).

### O-2 · Şarj girişi: kol yeri ve sigorta takıldıktan sonra gerilimli erkek pimler

1. **Kolun yeri.** K1 madde 1 "Şarj girişi: akü + hattından, ana anahtardan önce" diyor ve iki biçimde okunabilir:
   - akü XT60'ının robot tarafından (ana hat): akü XT60 ayrılınca kol enerjisiz;
   - akünün kendi tarafından (M5 kutup ile XT60 arası): kol ve sigorta yuvasının giriş ucu her zaman gerilimli.

   Rehberin bütün güvenlik düzeni "akü XT60 ayrık = enerjisiz" varsayımına dayanıyor: K1 "Bağlarken akü ayrık", F1 madde 5 "akü ayrıkken
   bağla", F5 notu. Kaynak tarafı belirtmiyor (`:372` yalnız "akü +"). Metin iki şey demeli:
   - "akü XT60'ının robot tarafından, ana hattan (XT60 ayrılınca enerjisiz)";
   - "yer kaynakta yok, doğrulanmadı".
2. **Sigorta takıldıktan sonra.** F5 notu "Sigorta ilk şarjdan önce, akü XT60 ayrıkken takılır" diyor. Şarj akü yerindeyken, akü XT60
   bağlıyken yapılıyor (`taban/rapor.html`). Sigorta bir kez takılınca:
   - `maliyet.json:111`'deki **XT60E-M panel erkek** konnektörün pimleri akü bağlı olduğu sürece gerilimli kalır;
   - ana anahtar ve mantar bu kolu kesmez (`:372` "ana anahtar öncesi").

   F1 aşama 1'deki "sigortası takılı olsaydı … gerilimli olurdu" cümlesi doğru, ama rehberden sonraki kalıcı durumu anlatmıyor. Notta
   şu uyarı olmalı: "takıldıktan sonra şarj pimleri akü bağlı oldukça gerilimli; ana anahtar ve mantar kesmez; konnektör kapağı / cins:
   karar bekliyor".

   Akü 12,8 V LFP, bu yüzden çarpma tehlikesi düşük. Asıl risk pimler arasında kısa devre: akım 10 A sigorta atana kadar akar, kıvılcım
   ve yanık yapabilir (genel bilgi).
3. **Küçük eksik.** Konnektörün − ucunun nereye bağlanacağı (akü − mi, WAGO yıldız noktası mı) ve kutup işareti yazmıyor. Metin yalnız
   "+ hattı → şarj girişi ucu" diyor. Kaynakta da yok; "doğrulanmadı" diye eklenmeli.

Rehberin kapsadığı sürede pimler enerjisiz olduğu için orta, kritik değil.

## 3. Düşük bulgular

**D-1 · S3 hâlâ kaçıyor (D-6' kısmen).**
- F5'teki "Kollar aşağıda başlar: … kollar düşer (E3 DTR / RTS notu)." cümlesi tümden silinince denetim geçiyor. Sebebi: `ZORUNLU`
  satırı yalnız "kollar düşer" arıyor ve bu ifade ön şarj dizisinden sonraki cümlede de var.
- Korunması gereken asıl talimat "Kollar aşağıda başlar".
- A'nın günlüğündeki "S1–S3 … için `ZORUNLU` satırları" iddiası S3 için tutmuyor. A'nın Y16'sı iki yeri birden siliyordu, o yüzden
  yakaladı.
- Öneri: F5 `Kollar aşağıda başlar`.

**D-2 · Yeni köprüleme kalıbında yanlış alarm.** `_KOPRU_NESNE` iki şekilde fazla tutuyor:
- `artı\w*` "artık"ı, `eksi\w*` "eksik"i tutuyor;
- "sigorta" ve "12 V" nesneleri kablo ekleme cümlelerini de tutuyor.

Olası doğru cümlelerde yanlış alarm (NB7–NB10):

| # | Cümle | Neden tuttu |
|---|---|---|
| NB7 | "Artık S2 uzatmasının iki ucunu lehimle birleştir" | "artık" |
| NB8 | "Eksik kalan servo uzatmasını ek kabloyla birleştir" | "eksik" |
| NB9 | "Sigorta kutusunun GND uçlarını WAGO yıldız noktasında birleştir" | "sigorta" |
| NB10 | "12 V çift kablonun uzatmasını lehimle birleştir" | "12 V" |

- Gerçek veride 0.
- `elektrik.md` "adaptör kablosu kesilebilir" diyor; ileride bir "12 V … birleştir" cümlesi yazılırsa yanlış alarm verir.
- Öneri: `artı(?!k)\w*`, `eksi(?!k)\w*`; bu biçimlerin olumsuz deneme olarak eklenmesi.

**D-3 · Bilinen denetim sınırları** (engelleyici değil; kayıt için). Kaçanlar:
- B8: F1 aşama 1'de "Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç" → "Aküyü XT60'tan tak, ana anahtarı aç". F3'te bu
  satır korunuyor, F1'de korunmuyor.
- B14: "enerjiyi kesmeden … değiştir", olumsuz ekli fiil istisna sayılıyor. HEAD'den kalma.
- B15: F1 madde 5'te "Şarj 10 A sigortası takılmaz" → "sigortasını tak".
- B18: K1'de "Uç bantlı … sigortası takılmaz" → "Uç açık … takılır". B15 ve B18'de aşama 1 listesi değişmediği için çelişki fark
  edilmiyor.
- B16: "iki telini aynı klemense bağla". A'nın açığı 4.
- B17: "birleştirme işini … yap" (ad biçimi).

**D-4 · F3'teki akülü ölçümde iki eksik** (K11 a).
- `00-genel.md` kural 8 ("Saat, yüzük, bileklik çıkar") F1 ve F5'te yazıyor, F3'te yazmıyor.
- Ölçüm sırasında K2'den gelen 12 V kablosunun ekran ucundaki fişi gerilimli (regülatör çıkışı). "Ucu bantlı / metal parçaya değmesin"
  yazmıyor; K11 b'de yazıyor.
- Dal 2 A sigortalı; risk düşük.

**D-5 · Demo metninde bir ifade biraz fazla iddialı.**
- Metin: "sayfanın modeli kopya tutmadan … okuduğu".
- `F9b-dogrula.py` [4] gerçekte şunlara bakıyor:
  - sayfa iki dosyayı `<script src>` ile yüklüyor mu;
  - eski kopya `lale158-model.js`'e bağlı mı;
  - `robot-glb.js` = `robot.glb` mi;
  - `rehber-veri.js` = `.json` mı;
  - düğümler parça listesinde mi.
- Sayfaya gömülü bir model kopyası olup olmadığına bakmıyor. B baktı: bugün yok, `REHBER_GLB=` 0 kez geçiyor.
- Öneri: "… göreli bağlantıyla okuduğu (eski kopya `lale158-model.js`'e bağlı olmadığı)".
- Öbür 7 iddia betikle uyuşuyor:
  - [1] ve [2]: sayılar kaynak JSON'la aynı, bağsız sayı yok;
  - [3]: maliyet aynı hesapla;
  - [5]: kararlar kuyrukta açık;
  - [6]: eklem öneri dosyası ↔ `kod/` sayısal aynı; servo, ekran ve işaretler;
  - [7]: 1,65;
  - [8]: konsol 0, `data-hazir` = 1 (model yüklendi), 360 px'de yatay kaydırma yok.

**D-6 · README ile commit sırası.**
- README F9d'nin alanında. Çalışma ağacındaki README F9d tarafından "(54 sayfa)" diye güncellenmiş; F7d'nin PDF'i de 54 sayfa, yani tutarlı.
- F9d, F7d'den önce ya da F7d olmadan commit'lenirse README 54, HEAD PDF'i 53 der.
- İkisi aynı anda ya da F7d önce commit'lenmeli. README'ye dokunulmadı.

**D-7 · A'nın günlüğündeki küçük yanlışlar** (metne yansımıyor).
- "S1–S3 için ZORUNLU" (bkz. D-1).
- "kablo kesiti kaynakta yok": `elektrik.md`'de gerçekten yok, ama `maliyet.json:122`'deki yuva "16AWG" kuyruklu. Kesit için ipucu var.

## 4. Karar taslağı

**KT-F7d-1 · Şarj girişi konnektörü: gerilimli erkek pimler** (karar: Ahmet / tasarım; `karar-kuyrugu.md`'ye B yazmadı).

Durum:
- `maliyet.json:111`: XT60E-M panel **erkek**, 61,20 TL, Motorobit.
- `elektrik.md:372`: kol ana anahtar öncesinde, 10 A mini sigortalı.
- Şarj akü yerindeyken yapılıyor. Sigorta takılı olduğu sürece pimler gerilimli; ana anahtar ve mantar kesmiyor.

| Seçenek | Ne | Etki |
|---|---|---|
| a | XT60E-M kalır; şarj sigortası **yalnız şarj sırasında** takılır, bitince çıkarılır | Parça ve maliyet aynı. Pimler yalnız şarjda gerilimli. Her şarjda sigorta yuvasına erişim gerekir; yuvanın yeri modelde yok, H1 / H2'den erişim doğrulanmadı. Unutulursa d'ye döner. Rehberde F5 notu ve kullanım notu değişir |
| b | **XT60E-F (dişi) panel konnektöre** geçilir | Gerilimli taraf gömük soket olur; XT60'ta kaynak tarafında dişi kullanma alışkanlığı genel bilgi, kaynakta yok. Şarj kablosunun ucu erkek XT60 olmalı; `maliyet.json:93`'te XT60H-M × 5 var. `maliyet.json:111` satırı değişir: **fiyat ve stok doğrulanmadı**, yeni bakım gerekir. Panel deliği yeni parçayla ölçülmeli. Rehberde K1 ve F1 metni değişir |
| c | Kol **ana anahtar sonrasına** alınır | Ana anahtar kapalıyken pimler enerjisiz. Ama şarj ancak ana anahtar açıkken olur: F4 / F5 dalları, ESP32, akü ADC bölücüsü ve K11 a'da göğüs ekranı dalı da enerjilenir. Ana anahtar şarj akımını da taşır. `elektrik.md:372` ve akü raporu önerisiyle çelişir; E3 / E9 yeniden okunmalı |
| d | Bugünkü gibi: XT60E-M, sigorta kalıcı takılı; konnektöre **kapak** ve uyarı etiketi | Parça değişmez. Kapak `maliyet.json`'a fiyatsız aday olarak girer. 12,8 V'ta çarpma tehlikesi düşük, ama açık pimler arasında kısa devre 10 A sigorta atana kadar akım çeker (genel bilgi). Rehberde F5 notuna uyarı girer |

**B'nin görüşü:** b, olmazsa a. Gerekçe:
- gerilimli tarafı dokunmaya kapalı yapan tek seçenek b;
- a parça değiştirmez ama kullanıcının her seferinde hatırlamasına dayanır;
- c güvenlik düzenini (E3, ana anahtar) şarj için değiştirir; d riski kabul eder.

Karar ne olursa olsun, O-2'deki iki metin düzeltmesi (kolun yeri ve sigorta takıldıktan sonraki uyarı) bu karardan bağımsız.

## 5. Denetim ayrıntısı

**Yöntem.**
- Depodaki `rehber_denetim.py`, `rehber_metin.py` ve `rehber-veri.json` scratchpad `f7d_B/denetim/`'e kopyalandı. sha1 (ilk 12):
  `158d2c8f097a`, `64c5df86198c`, `da04cf4af2b0`; A'nın günlüğüyle aynı.
- Bozma `enjekte_b.py` ile bellek içinde yapıldı. Yakalanma yalnız hedeflenen denetimle sayıldı: yasak + zorunlu + kopya eki > 0. ASCII
  sayılmadı, çünkü eklenen kelimeler `ASCII_TAMAM`'da yok.
- Karşılaştırma için HEAD'deki `rehber_denetim.py` aynı veriyle ayrıca koşuldu (`denetim_head/`). O veride zaten 1 zorunlu eksik var
  (F1 "+ ucuna" deseni değişti). Bu yüzden HEAD sütunu yalnız yasak bulgusuna bakar.

**Temiz kopya.** Geçti. Yasak 0, istisna 5:
- K1 ×2, E3a ve E4: "köprülenmez / köprülenmedi";
- F5: "röleler elle kapatılmaz".

Hepsi doğru olumsuz biçim. Zorunlu eksik 0 / 35, kopya eki 0, ASCII 0.

**B'nin yeni enjeksiyonları (A'nın Y1–Y23'ünden farklı cümleler):**

| # | Enjeksiyon | Sonuç |
|---|---|---|
| B1 | F3: "Ana anahtar açıkken HDMI ve 12 V fişlerini tak, sonra çıkışı oku." | yakaladı (enerji varken) |
| B2 | E3a: "Pi'nin 5 V hattını SY8205 çıkışıyla birleştir." | yakaladı (birleştir) |
| B3 | K1: "Röle K1'in kontak uçlarını kısa bir telle birbirine bağla" | yakaladı |
| B4 | F5: "Ön şarj tıklamazsa röleyi tornavidayla elle bastır" | yakaladı |
| B5 | F1: "Aküyü bağlayınca acil stop klemensini sık." | yakaladı |
| B6 | F5: "Enerji verince servo konnektörünü değiştir" | yakaladı |
| B7 | F5 notu: "akü XT60 ayrıkken takılır" → "akü bağlıyken takılır" | yakaladı |
| B9 | F3 K11 a sökme sırası bozuldu | yakaladı (zorunlu) |
| B10 | F3 "DC V kademesine" → "DC A kademesine" | yakaladı (zorunlu) |
| B11 | F5 "Şarj girişi mini 10 A bu aşamada da takılı değil" silindi | yakaladı (zorunlu) |
| B12 | F1 madde 3 "(akü ayrık;" → "(akü bağlı;" | yakaladı (akü bağlı) |
| B8 | F1 aşama 1 "Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç" → "Aküyü XT60'tan tak, ana anahtarı aç" | **kaçtı** (D-3) |
| B13 | F3: "Ana anahtar açıkken aküyü ayırmadan 12 V fişini tak." | **kaçtı** (O-1; HEAD yakalıyordu) |
| B14 | F5: "XT60 takılıyken enerjiyi kesmeden F1 sigortasını değiştir" | **kaçtı** (D-3; HEAD'de de istisna) |
| B15 | F1 madde 5 "Şarj 10 A sigortası takılmaz" → "sigortasını tak" | **kaçtı** (D-3) |
| B16 | F1: "Acil stop düğmesinin iki telini aynı klemense bağla" | **kaçtı** (D-3, A'nın açığı 4) |
| B17 | F1: "Mantar uçlarını birleştirme işini ölçümden önce yap" | **kaçtı** (D-3, ad biçimi istisna sayıldı) |
| B18 | K1 "Uç bantlı … sigortası takılmaz" → "Uç açık … takılır" | **kaçtı** (D-3) |
| B19 | F5: "Ana anahtar açıkken birkaç saniye sonra F1 sigortasını tak" | **kaçtı** (O-1; HEAD yakalıyordu) |
| B20 | F3: "Enerji varken ölçüm bitince göğüs 12 V fişini tak" | **kaçtı** (O-1; HEAD yakalıyordu) |

Brief'in istediği "en az 8 enjeksiyon" B1–B7, B9–B12'de karşılanıyor: 11 / 11 yakalandı. B8 ve B13–B20 bilinçli sınır denemeleri.

**Olumsuz denemeler (doğru metin):**

| # | Cümle | Sonuç |
|---|---|---|
| NB1 | F3: "Ana anahtar açıkken yalnız multimetreyi oku, ardından ana anahtarı kapat ve ölçü uçlarını sök." | temiz |
| NB2 | F1 (D-7 kalıbı): "Enerji varken yalnız PC817 ışığına bak, en son aküyü XT60'tan ayır ve kıskaçları sök" | temiz |
| NB3 | F5 (D-7 kalıbı): "XT60 takılıyken yalnız ekrandaki gerilimi izle, sonunda ana anahtarı kapat, uçları sök" | temiz |
| NB4 | F1: "Sigorta uçlarını asla birbirine bağlama" | temiz (olumsuz biçim) |
| NB5 | F3: "Ana anahtar açıkken hiçbir fişi takma" | temiz (olumsuz biçim) |
| NB6 | G2: "Uzatmanın iki parçasını lehimle birleştir, makaron geçir" | temiz |
| NB7–NB10 | nesne listesi sınırı ("artık", "eksik", "sigorta kutusu GND", "12 V kablo uzatması") | **yanlış alarm** (D-2) |

Brief'in istediği "en az 4 olumsuz deneme" karşılanıyor: NB1–NB6 6 / 6 temiz, üçü D-7 kalıbında.

**F7c regresyonu.** Önceki B'nin setleri yeni metne uyarlanarak koşuldu:
- J1–J20 ve K1–K11: **31 / 31 yakalandı.** İlk turda kaçan K1, K3, K5, K6, K10 ve K11 artık yakalanıyor. K8 ve K10'un metni yeni cümleye
  uyarlandı.
- P1–P8: **8 / 8 temiz.** P5 artık temiz.
- S1 ve S2 yakalandı; **S3 kaçtı** (D-1).

Gerileme yok. HEAD'e göre B13, B19 ve B20'deki gerileme O-1'de.

**Gerçek veri.** Depodaki `rehber_denetim.py` → çıkış 0; zorunlu eksik 0 / 35, yasak 0 (istisna 5), ASCII 0, kopya eki 0.

## 6. PDF

`pdf_olc_b.py` (PyMuPDF 1.27, pypdf 6.19), depo PDF'i (sha1 `65f35923dcb2`) üzerinde:
- **54 sayfa** (PyMuPDF ve pypdf);
- en küçük yazı **8,10 pt**, 8 pt altı span olan sayfa 0;
- sayfa dışına taşan span 0;
- "Sayfa i / 54" alt bilgisi 54 / 54 doğru;
- "(devam)" sayfaları 33, 35, 39, 54.

**Eşleme.** Başlıktan ("Adım i / 49") kurulan eşleme `kontrol.json` `yazdir.sayfa_esleme` ile **aynı** (50 adım). İki sayfalı adımlar:
31 → 32, 33; 32 → 34, 35; **35 → 38, 39**; **49 → 53, 54**. `kontrol.json`: `pdf_sayfa` 54, `html_sayfa` 54, `devam_sayfasi` 4,
`tasan` [], `kucuk_yazi` [], DOM 8,1 ve PDF 8,1 pt.

**B'nin üretimi.** `uret/Lale-montaj-rehberi.pdf` 54 sayfa. Saat maskelenince metni depo PDF'iyle **54 / 54 sayfada aynı**; eşleme aynı.

**PDF'de yerel yol izi** (metin + meta) 0.

**Bakılan sayfalar** (110 dpi, scratchpad `f7d_B/sayfa/`):

| Sayfa | Adım | Görülen |
|---|---|---|
| 18 | 17 K1 | Madde 1 sonunda şarj girişi cümlesi; madde 6 "K1'de enerji verilmez … akü XT60 ayrık kalır". Kablo yolu 2 "Toprak: akü − → WAGO". Tek sayfa |
| 36 | 33 F1 | Madde 3 süreklilik denemesi, madde 5 şarj girişi. Aşama 1 metni tam: şarj 10 A takılı değil, "gerilimli olurdu", DC V, V soketi, "+ ucuna", sökme sırası. Tek sayfa, okunaklı |
| 38 | 35 F3 | Madde 3'te K11 a / K11 b metni tam, kontrol listesinde yeni satır. Kural 8 yok (D-4) |
| 39 | 35 F3 (devam) | Yalnız "Erişim notu"; taşma değil (kabul "her adım ≥ 1 sayfa") |
| 53 | 49 F5 | Aşama 2 tam: şarj 10 A, K11 b uçları, dışarıdan okuma, fiş sırası. Notlarda şarj notu |
| 54 | 49 F5 (devam) | Kontrol listesi (K11 b satırı dahil), kablo, erişim |

## 7. Rehber bütünlüğü ve üretim

**`kontrol.json`** (20:31):
- 50 / 50 geçti, konsol hatası 0;
- `parca_rehber` 1192 ↔ `parca_mesh` 1192, her parça tek adımda;
- telefon 360 px'te 7 adım × taşma 0;
- `yazdir_goruntu` 50, eksik 0; `denetim.gecti` true.

**Görüntüler.**
- 6 değişen PNG'nin zamanı 20:28:02–20:31:20; veri 20:26:31'de üretilmiş.
- Öbür PNG'ler de aynı koşuda yazılmış, ama içerikleri HEAD ile aynı (git yalnız 6 dosyayı değişmiş gösteriyor).
- `adim-35.png` açıldı: panelde K11 a / b metni yeni hâliyle var.

**B'nin üretimi.** `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok --cikti <scratchpad f7d_B/uret>` → **0**
(20:46:59–20:51:18). Sonuçlar:
- 50 adım, 50 geçti, 0 sorunlu, konsol 0, her parça tek adımda;
- telefon 7 × 360 / 0;
- PDF 54 (devam 4), HTML 54, eşleme tutarlı, taşan yok, en küçük 8,1 / 8,1 pt, 3.926 kB;
- denetim temiz (zorunlu 0 / 35, yasak 0, istisna 5).

**HEAD ile aynı kalanlar.** `rehber/veri/robot.glb`, `robot-glb.js`, `rehber/yazdir.html`, `rehber_veri.py`, `rehber_uret.py`
(`git diff --quiet HEAD` → aynı).

## 8. Demo

- **Şablon.** `git diff tasarim/cad/viewer-template.html`: tek satır, "Bu sayfa hakkında" bölümündeki `<li>`.
- **Demo.** `git diff --word-diff` iki yeri gösteriyor: aynı `<li>` ve `kaynak` bloğundaki `rehber-veri.json` parmak izi
  (`85a3cc196adb` → `74137332d78e`). Başka fark yok.
- **Kopyada üretim** (scratchpad `f7d_B/demo_kopya/`, 13 kaynak dosya + iki model .js): `py -3 -B -X utf8 tasarim/cad/demo_uret.py` →
  **0**; 127 sayı anahtarı, 14 karar, 153 kalem, 1192 düğüm. Çıktı depodaki demoyla **bayt bayt aynı** (sha1 `53e6b4c89ff6`).
- **`py -3 -B -X utf8 planlama/d158/F9b-dogrula.py`** → **0**, "GECER (hata 0)". Tarayıcı denetimi koştu:
  - 1400 ve 360 px'te `data-hazir` = 1, konsol 0, yatay kaydırma yok;
  - 1.638 bağlı sayı, 0 bağsız.
- **8 iddia ↔ betik:** D-5'e bak. Yedisi birebir, biri ("kopya tutmadan") biraz fazla iddialı.
- **Başka "kopya" iddiası.** Şablonda ve demoda "kopya" yalnız bu `<li>` içinde geçiyor.

## 9. Bütünlük, ad, yol, liste

| Komut | Çıkış | Sonuç |
|---|---|---|
| `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | **0** | izlenen 17 dosyanın özetleri kayıtla aynı |
| `py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` | **0** | "GEÇER (hepsi okundu, kötüleşen yok)" |
| `ad_tara_b.py` (17 dosya; PDF metni ve metası, PNG baytları dahil) | 0 | takma ad 0, soyad 0, "ad + büyük harf" 0, yerel yol 0 |

Takma ad depodaki kaynaktan türetildi ve hiçbir yere yazılmadı.

**Liste.** `git status`'ta F7d'ye ait değişiklik tam 17 dosya; A'nın listesiyle aynı. Bu dosya (`F7d-kontrol.md`) eklenince 18 olur.
- Rehber betiklerinde başka ajanın değişikliği yok: `git diff`'te yalnız F7d hunk'ları görünüyor.
- F9d dosyaları listeye karışmamış: `README.md`, eski d158 belgeleri, `carpisma_kos.py`, `kafa_gorsel.py`, `omuz_baski.py`,
  `taslak-170/*`, `planlama/adim*`, `y2` / `y3`, `F9d-*`.

**Girmez:**
- `planlama/d158/FREECAD-KILIT.txt`: izlenmiyor, "boş";
- `planlama/dongu-158.md`: orkestratörün;
- `tasarim/freecad/kabuk/gorsel/*.png` ve `tasarim/freecad/montaj/yerlesim-kontrol.json`: başka paketlerin;
- `__pycache__/`: izlenmiyor;
- F9d alanı.

## C için kesin `git add` listesi (18 dosya)

O-1 ve O-2 düzeltilince yeniden üretilen dosyalar aynı yollarda kalır; liste değişmez. A'nın yeni bir dosyaya ihtiyacı olursa B yeniden
bakar.

```
git add tasarim/freecad/rehber/rehber_metin.py \
        tasarim/freecad/rehber/rehber_denetim.py \
        tasarim/cad/viewer-template.html \
        rehber/veri/rehber-veri.json \
        rehber/veri/rehber-veri.js \
        planlama/rehber/R-gunluk.md \
        planlama/rehber/kontrol.json \
        planlama/rehber/Lale-montaj-rehberi.pdf \
        planlama/rehber/goruntu/adim-17.png \
        planlama/rehber/goruntu/adim-33.png \
        planlama/rehber/goruntu/adim-35.png \
        planlama/rehber/goruntu/adim-49.png \
        planlama/rehber/goruntu/telefon-360-adim-35.png \
        planlama/rehber/goruntu/telefon-360-adim-49.png \
        tasarim/Robot-Tasarim-Demosu.html \
        planlama/d158/F7d-brief.md \
        planlama/d158/F7d-gunluk.md \
        planlama/d158/F7d-kontrol.md
```

Commit sırası: F9d'nin README'si "(54 sayfa)" diyor. F7d, F9d ile aynı anda ya da ondan önce commit'lenmeli (D-6).

## Commit mesajı önerisi

```
Lale P7.4: rehberde son düşükler: F3 göğüs regülatörü ölçüm sırası açık (ana anahtar kapalıyken akü tak → aç → oku → kapat → akü ayır → uçları sök; K11 b'de 12 V fişi F5 aşama 2'de ölçümden sonra), mantar ve regülatör ölçümünde DC V / V soketi / klemensin + ucu, F1 mantar NC süreklilik denemesi (akü ayrık), şarj girişi 10 A (K1 kablo, F1 etek, aşama 1 / 2 takılı değil), denetimde köprüleme eş anlamlıları + röleyi elle kapatma + "açtıktan sonra tak", pencere sınırı, ZORUNLU 35, PDF 54 sayfa ≥ 8,1 pt; demo "Bu sayfa hakkında" F9b denetimlerine göre (F7d)
```

O-1 ve O-2 bu turda düzeltilirse mesaja eklenmeli: "pencere yalnız enerjiyi bitiren ifadede kesilir; şarj kolu akü XT60'ının robot
tarafında, sigorta takılınca pimler gerilimli uyarısı".

## Kanıtlar (komut → çıkış)

```
git status --porcelain -uall + sha1 (başta / sonda)                       → F7d'nin 17 dosyası aynı; farklar F9d / orkestratör
FREECAD-KILIT.txt                                                         → "boş" (6 bayt); FreeCAD süreci 0
rehber_denetim.py (depo, gerçek veri)                                     → 0; zorunlu 0/35, yasak 0, istisna 5, ascii 0, kopya 0
f7d_B/denetim kopya sha1                                                  → 158d2c8f097a / 64c5df86198c / da04cf4af2b0
rehber_metin.ADIM ↔ rehber-veri.json (49 adım, 8 alan)                    → fark 0
enjekte_b.py f7d_B/denetim                                                → 0; B 11/20 (zorunlu 11/11), NB 6/10 (NB1–6 temiz), J/K 31/31, S 2/3, P 8/8
enjekte_b.py f7d_B/denetim_head (HEAD denetimi)                           → 0; B13, B19, B20 yasakla yakalanıyor (O-1 gerilemesi)
oneri_yama.py + enjekte_b.py f7d_B/denetim_oneri                          → 0; B 14/20, B13/B19/B20 yakalandı, J/K 31/31, P 8/8, NB1–6 temiz, gerçek veri 0
n_a.py (A'nın N1–N4) depo denetimi / yamalı kopya                         → 0 / 0 yasak
rehber_uret.py --veri-yok --cikti f7d_B/uret                              → 0; 50/50, konsol 0, 1192 ↔ 1192, 360 px 7/0, PDF 54, denetim temiz
pdf_olc_b.py depo PDF                                                     → 54/54; en küçük 8,10 pt; <8 pt 0; taşan 0; alt bilgi 54/54; eşleme = kontrol.json; yerel yol 0
B PDF ↔ depo PDF (saat maskeli metin)                                     → 54/54 aynı; eşleme aynı
f7d_B/demo_kopya: demo_uret.py                                            → 0; bayt bayt aynı (53e6b4c89ff6)
F9b-dogrula.py                                                            → 0 (GECER, tarayıcı dahil)
carpisma_kos.py kontrol / regresyon.py --yazma                           → 0 / 0
ad_tara_b.py (17 dosya)                                                   → TOPLAM 0
```

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

**Kapsam.** A'nın "Düzeltme turu 1" kaydı (`planlama/d158/F7d-gunluk.md:272-`): O-1, O-2, D-1, D-2, D-4, D-5 ve FreeCAD'siz veri yazımı.
Bu tur dar bir kontrol.

**B'nin çalışma koşulları.**
- Çalışma klasörü scratchpad `f7d_B/d1/`.
- FreeCAD koşulmadı, kilide yazılmadı (kilit "boş", 6 bayt). Git'e yazılmadı, hiçbir şey silinmedi. Python `-B` ve
  `PYTHONDONTWRITEBYTECODE=1`.
- Kontrol başında ve sonunda `git status --porcelain -uall` ve sha1 listeleri **aynı**. Bu bölümün eklenmesi tek istisna.
- Arka planda iş ya da headless Chrome kalmadı.

**Bu turda değişen dosyalar.** sha1 (ilk 12), A'nın günlüğüyle aynı:
- `rehber_metin.py` `9026b9c27853`, `rehber_denetim.py` `8eac1a079098`, `viewer-template.html` `3bb82018db85`;
- `rehber-veri.json` `84d4b6744e81`, `.js` `c0bd83d928fe`;
- `kontrol.json` `a00f1ef8b58f`, PDF `2d50a7393bfa`, demo `e6537a6bce81`;
- 6 PNG (21:09–21:13'te yazılmış, yani veriden, 21:08'den sonra);
- `R-gunluk.md`, `F7d-gunluk.md`.

`robot.glb`, `robot-glb.js`, `yazdir.html`, `rehber_veri.py` ve `rehber_uret.py` HEAD ile aynı.

## Karar (düzeltme 1 sonrası)

**GEÇER. F7d commit edilebilir.**
- **O-1 kapandı:** B13, B19 ve B20 yakalanıyor; D-7'nin doğru cümleleri temiz.
- **O-2 kapandı:** kolun tarafı, − ucu, kutup ve sigortadan sonraki gerilimli pim uyarısı metinde; kaynakta olmayanlar "doğrulanmadı".
- **D-1, D-2 ("artık / eksik"), D-4 ve D-5 kapandı.**
- **FreeCAD'siz veri yazımı güvenli** (§ 1). FreeCAD'li tam veri koşusu commit için **gerekmiyor**.
- Üretim, PDF, demo, tarama, regresyon, ad ve yol kontrolleri 0.

| Önem | Sayı | Açık bulgular |
|---|---|---|
| kritik | 0 | — |
| orta | 0 | — |
| düşük | 4 | D-8 (üretim damgası), D-9 ("kuyruğa girmedi" ifadesi), D-2' (NB9 / NB10), D-3 (bilinen denetim sınırları) |

Hiçbiri commit'i engellemiyor. D-6 (commit sırası) geçerli.

## 1. Veri bütünlüğü (FreeCAD'siz yazım)

B'nin betiği `f7d_B/veri_fark.py`. A'nın `veri_metin_yaz.py`'si koşulmadı; sonuç bağımsız olarak çıkarıldı.

| Soru | Ölçüm | Sonuç |
|---|---|---|
| İlk tura göre fark yalnız üç alanda mı? | ilk turun FreeCAD verisi (`da04cf4af2b0`, B'nin kopyası) ↔ şimdi: derin karşılaştırma, bütün anahtarlar | **evet**: 3 fark yolu, `K1.is_`, `F3.is_`, `F5.not_` |
| Adımların parça, bağlantı, kontrol, kablo, alet listeleri HEAD ve ilk turla aynı mı? | 50 adımda alan alan: `parcalar`, `baglantilar`, `m6`, `sure_dk`, `kamera`, `tezgah`, `baglanir`, `kablolama`, `faz`, `no`, `baslik`, `baglanti_md`, `alet`, `erisim`, `kablo` | **ilk turla hepsi aynı; HEAD ile de hepsi aynı.** `kontrol` alanı HEAD'e göre yalnız F1, F3 ve F5'te farklı; bu ilk turun beklenen değişikliği, bu turda değişmedi. Adım 0: `kontrol` 8, `kablo` 1, `not_` 0 (ilk turla aynı; A'nın ilk denemedeki boşalması geri alınmış) |
| Üst alanlar | `parcalar`, `semalar`, `mesh`, `atanmamis`, `tur_ad`, `modul_ad`, `kaynak` | ilk turla ve HEAD ile **aynı**. `uretim` ilk turla aynı (20:26), HEAD'den farklı |
| js = json mu? | `window.REHBER_VERI=` + JSON + `;\r\n` | **eşdeğer**. Gövde `json.dumps(…, separators=(",", ":"))` ile bayt bayt aynı |
| Yazım biçimi FreeCAD'inkiyle aynı mı? | `json.dumps(indent=0, ensure_ascii=False)` + metin kipi (CRLF) | şimdiki dosya **birebir**. İlk turun FreeCAD dosyası da aynı biçimde birebir; yani biçim `rehber_veri.py:625-627` ile aynı |
| `rehber_metin.py`'deki metin veriye birebir girdi mi? | `rehber_veri.py:533-586` kuralıyla (adım 0 `HAZIRLIK`, öbürleri `ADIM`; dolu metin alanı ve üç liste) 50 adım | **fark 0** |
| FreeCAD koşusu başka bir şeyi değiştirir miydi? | `rehber_metin.py` ilk tur ↔ şimdi `diff` | değişen yalnız `ADIM` içinde K1 `is_`, F3 `is_`, F5 `not_` dizgileri. `TR`, `TR_EK`, `M6_CAD_NOT`, `FAZ`, `TUR_AD`, `MODUL_AD` ve `HAZIRLIK` aynı. `rehber_veri.py` ve CAD kaynakları değişmedi |

**Hüküm.** Yöntem bu tur için güvenli. Bugünkü metinle FreeCAD'li bir koşunun üreteceği verinin içeriği, depodaki veriyle aynı olurdu.
Fark yalnız iki yerde çıkardı: `uretim` saati ve buna bağlı PDF alt bilgisi ile `kontrol.json` `ozet.veri_uretim`.

Gerekçe:
- Metin dışı her alan FreeCAD'in 20:26 çıktısıyla aynı;
- metin alanları kaynağa birebir;
- yazım biçimi FreeCAD yazıcısıyla aynı;
- metin dışında `rehber_metin.py`'de değişen bir şey yok.

**Bu yüzden FreeCAD'li tam veri koşusu commit için gerekmiyor.** İstenirse bir sonraki FreeCAD'li paket kilit kuralıyla koşar ve yalnız saati
düzeltir.

Yöntemin sınırı: betik scratchpad'de ve depoda yok, yani bir sonraki ajan aynı adımı tekrarlayamaz. Bu tur için engel değil. Tekrar
gerekirse `rehber_veri.py`'ye bir metin modu eklenmesi ayrı bir iş olarak önerilir.

## 2. Önceki açıklar

**O-1: kapandı.** Yeni `_SINIR`, B'nin önerisiyle aynı: çıplak sıra bağlacı kesmiyor, enerjiyi bitiren dört ifade `(?!ma|me)` ile kesiyor.
`enjekte_b.py` yeni denetim ve yeni veri kopyasında (`f7d_B/d1/denetim/`):
- B13, B19 ve B20 **yakalandı**; B toplamı 14 / 20;
- D-7'nin doğru cümleleri temiz: NB1–NB3 ve P5; A'nın N1–N4'ü (`n_a.py`) 4 / 4 temiz.

**O-2: kapandı.** Metin `rehber_metin.py` ve PDF s. 18 / 53'te okundu.
- **K1:**
  - "Kolu akü XT60'ının robot tarafından, ana hattan al: akü XT60'tan ayrılınca kol da enerjisiz kalır …";
  - "XT60'ın hangi tarafı olduğu doğrulanmadı";
  - − ucu ve kutup işareti "doğrulanmadı"; genel toprak `elektrik.md:341` ile tutarlı ("akü − ── WAGO yıldız noktası");
  - kesit için `maliyet.json:122` (16AWG yuva), "doğrulanmadı".

  Talimat, rehberin "akü ayrık = enerjisiz" düzenini kuran güvenli taraf; kaynakta olmadığı açıkça yazıyor. Doğru.
- **F5 notu:**
  - "sigorta takıldıktan sonra … XT60E-M panel erkek … pimleri, akü XT60'tan ayrılmadıkça gerilimlidir: ana anahtar da mantar da bu kolu
    kesmez";
  - "Pimlere metal değdirme";
  - "KT-F7d-1 … karar verilene kadar geçerli".

  `elektrik.md:372` ve `maliyet.json:111` ile tutarlı.
- **Yeni tehlike: yok.** Hiçbir adım şarj sigortasını taktırmıyor. Sigortanın takılma anı yine akü XT60 ayrıkken.
- **Korunuyor:** yeni `ZORUNLU` satırları K1 kol tarafı ve F5 pim uyarısı. B'nin R1 ve R2'si yakalandı.

**D-1 (S3): kapandı.** F5'te `Kollar aşağıda başlar` için ayrı satır var; S3 yakalandı (S 3 / 3).

**D-2: "artık / eksik" kapandı.** NB7 ve NB8 temiz. B'nin RN2'si ("Artık şarj ucunu bantla, eksik etiketi tamamla") temiz. R5 ("Akünün
artısıyla eksisini tek telle birleştir") ve R6 ("Artıyı eksiye kısa bir kabloyla birbirine bağla") yakalandı. Yani çekim ekli biçimler
hâlâ tutuluyor.

**D-2' (düşük, açık): NB9 / NB10.** "Sigorta kutusunun GND uçlarını WAGO'da birleştir" ve "12 V çift kablonun uzatmasını lehimle
birleştir" yanlış alarm veriyor. **Engelleyici değil:**
- gerçek veride 0;
- hata güvenli yönde: denetim kaçırmıyor, fazladan uyarıyor;
- yazar cümleyi değiştirir ya da `ASCII_TAMAM` gibi bir istisna eklenir.

Sonraki denetim turuna öneri: nesne ile "birleştir" arasında "GND / uzatma / ek" geçiyorsa istisna, olumsuz deneme olarak NB9 ve NB10.

**D-4: kapandı.** F3 K11 a'da:
- "Ölçümden önce saat, yüzük, bileklik çıkar (`00-genel.md` kural 8)";
- "fişin metal ucunu bantla yalıt, ekran kasasına ve metal parçalara değmesin (genel güvenlik, kaynakta yok)".

İkisi de `ZORUNLU`'da; B'nin R3 ve R4'ü yakalandı. Yeni tehlike yok. Fiş sonra "enerjisizken tak" adımında takılıyor; bandın çıkarılması
söylenmemiş ama açık, bulgu değil.

**D-5: kapandı.** Demo metni artık şöyle: "göreli bağlantıyla (`<script src>`) yüklediği ve eski model kopyasının dosyasına bağlı olmadığı
(sayfaya gömülü bir kopya ayrıca aranmaz)".
- Bu `F9b-dogrula.py` [4] ile birebir (`:519-523`).
- Eski dosyanın adı şablonda ve demoda 0 kez geçiyor; F9b o adı görse hata verirdi.
- `git diff`: şablonda yalnız "Bu sayfa hakkında" `<li>`'si; demoda aynı `<li>` ve `kaynak` bloğundaki `rehber-veri.json` parmak izi
  (`85a3cc196adb` → `38d5d32bc0b3`).

**D-3 (düşük, bilinen sınırlar): sürüyor.** B8, B14, B15, B16, B17 ve B18 kaçıyor; A'nın açıkları 4'te kayıtlı. Engelleyici değil.

**B'nin tur 1'e yönelik ek denemeleri** (`f7d_B/d1/enjekte_d1.py`):

| # | Deneme | Sonuç |
|---|---|---|
| R1 | K1 "Kolu akü XT60'ının robot tarafından, ana hattan al" → "Kolu doğrudan akü kutbundan al" | yakaladı (zorunlu) |
| R2 | F5 notu "ana anahtar da mantar da bu kolu kesmez" → "ana anahtar bu kolu da keser" | yakaladı (zorunlu) |
| R3 | F3 "fişin metal ucunu bantla yalıt, " → "fiş açıkta kalabilir, " | yakaladı (zorunlu) |
| R4 | F3 "Ölçümden önce saat, yüzük, bileklik çıkar" → "Ölçüm sırasında takılar kalabilir" | yakaladı (zorunlu) |
| R5 | K1 "Akünün artısıyla eksisini tek telle birleştir" | yakaladı (köprüleme) |
| R6 | F1 "Artıyı eksiye kısa bir kabloyla birbirine bağla" | yakaladı (köprüleme) |
| R7 | F5 "Ana anahtar açıkken, sonra da ardından şarj sigortasını tak" | yakaladı (enerji varken) |
| R8 | F5 "XT60 takılıyken ana anahtarı kapatmadan şarj girişini bağla" | yakaladı (enerji varken) |
| RN1 | F5 "Akü XT60 ayrıkken şarj sigortasını tak, sonra kapağı kapat" | temiz |
| RN2 | K1 "Artık şarj ucunu bantla, eksik etiketi tamamla" | temiz |
| RN3 | F3 "Ana anahtar açıkken yalnız oku, bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra fişi tak" | temiz |

**`enjekte_b.py` toplamı** (yeni denetim + yeni veri): B 14 / 20, NB 8 / 10 (NB9 ve NB10 D-2'), J/K 31 / 31, S 3 / 3, P 8 / 8. Temiz
kopyada geçti: yasak 0, istisna 5, zorunlu 0 / 40.

## 3. Yeni düşük bulgular

**D-8 · Üretim damgası eski.**
- `rehber-veri.json` `uretim`, `kontrol.json` `ozet.veri_uretim` ve PDF / rehber alt bilgisi "üretim 2026-11-09 20:26" diyor. Metin ise
  21:08'de yazıldı.
- İçerik doğru (§ 1). A bunu günlüğünde ve `R-gunluk.md`'de açıkça yazmış.
- Commit mesajında da belirtilsin (aşağıda). Bir sonraki FreeCAD'li koşu saati düzeltir.

**D-9 · F5 notunda "kuyruğa girmedi".**
- F5 notu "(KT-F7d-1, `planlama/d158/F7d-kontrol.md`; kuyruğa girmedi)" diyor.
- Kayıt ajanı KT-F7d-1'i `karar-kuyrugu.md`'ye taşıyınca bu ifade eskir.
- Engelleyici değil. Sonraki rehber turunda "kuyruğa girmedi" yerine kuyruk satırına bağlanmalı. Kayıt ajanı kuyruğa yazarken bunu notunda
  belirtebilir.

## 4. Kontroller

| Komut | Çıkış | Sonuç |
|---|---|---|
| `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py` (depo) | **0** | zorunlu eksik 0 / 40, yasak 0 (istisna 5), ASCII 0, kopya eki 0, bağlamla affedilen 6 |
| `veri_fark.py` | 0 | § 1 |
| `enjekte_b.py f7d_B/d1/denetim` | 0 | § 2 |
| `d1/enjekte_d1.py` / `n_a.py` | 0 / 0 | R1–R8 yakalandı, RN1–RN3 temiz / N1–N4 temiz |
| `rehber_uret.py --veri-yok --cikti <scratchpad f7d_B/d1/uret>` (21:21:10–21:25:26) | **0** | 50 / 50, konsol 0, her parça tek adımda, telefon 7 × 360 / 0, PDF 54 (devam 4), HTML 54, eşleme tutarlı, taşan yok, en küçük 8,1 / 8,1 pt, denetim zorunlu 0 / 40 |
| B PDF ↔ depo PDF (saat maskeli metin) | — | **54 / 54 aynı**; eşleme aynı |
| `pdf_olc_b.py` depo PDF | 0 | PyMuPDF ve pypdf **54**; en küçük **8,10 pt**; 8 pt altı 0; taşan 0; alt bilgi 54 / 54; eşleme = `kontrol.json`; devam 33, 35, 39, 54; yerel yol 0 |
| Sayfa görüntüleri (110 dpi, `f7d_B/d1/sayfa/`) | — | s. 18 (K1 kol tarafı, − ucu, kesit), s. 38 (F3 takı ve fiş yalıtımı, sıra tam), s. 53 (F5 aşama 2, pim uyarısı). Kesik satır yok, metin doğru adımda |
| `f7d_B/d1/demo_kopya`: `py -3 -B -X utf8 tasarim/cad/demo_uret.py` | **0** | 127 anahtar, 14 karar, 153 kalem; depodaki demoyla **bayt bayt aynı** (`e6537a6bce81`) |
| `py -3 -B -X utf8 planlama/d158/F9b-dogrula.py` | **0** | GECER (hata 0); 1400 ve 360 px'te `data-hazir` = 1, konsol 0, yatay kaydırma yok |
| `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | **0** | izlenen 17 dosya kayıtla aynı |
| `py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` | **0** | GEÇER |
| `ad_tara_b.py` (18 dosya, PDF metni ve metası, PNG baytları dahil) | 0 | takma ad 0, soyad 0, "ad + büyük harf" 0, yerel yol 0 |

**Liste.** F7d'ye ait değişiklik yine 17 dosya + bu dosya = 18. F9d dosyaları karışmamış. Rehber betiklerinde `git diff` yalnız F7d hunk'larını
gösteriyor.

## KT-F7d-1 (son hâl; kayıt ajanı karar kuyruğuna taşır)

**KT-F7d-1 · Şarj girişi konnektörü: sigortadan sonra gerilimli erkek pimler.** Karar: Ahmet / tasarım.

Durum:
- `maliyet.json:111`: şarj girişi XT60E-M panel **erkek** (61,20 TL, Motorobit, 09.11).
- `elektrik.md:372`: kol ana anahtar öncesinde, 10 A mini sigortalı.
- Şarj akü yerindeyken, akü XT60 bağlıyken yapılıyor (`tasarim/freecad/taban/rapor.html` "Servis erişimi").
- Sigorta takılı olduğu sürece pimler gerilimli; ana anahtar ve mantar kesmiyor.
- Rehber sigortayı hiçbir adımda taktırmıyor. F5 notunda geçici uyarı var: pimlere metal değdirme, bu uyarı karar verilene kadar geçerli.
- Kolun akü XT60'ının robot tarafından alınması rehberin önerisi, kaynakta yok.

| Seçenek | Ne | Etki |
|---|---|---|
| a | XT60E-M kalır; şarj sigortası **yalnız şarj sırasında** takılır, bitince çıkarılır | Parça ve maliyet aynı; pimler yalnız şarjda gerilimli. Her şarjda sigorta yuvasına erişim gerekir; yuvanın yeri modelde yok, H1 / H2'den erişim doğrulanmadı. Unutulursa d'ye döner. Rehberde F5 notu ve kullanım notu değişir |
| b | **XT60E-F (dişi) panel konnektöre** geçilir | Gerilimli taraf gömük soket olur; kaynak tarafında dişi kullanma alışkanlığı genel bilgi, kaynakta yok. Şarj kablosunun ucu erkek XT60 olur (`maliyet.json:93`'te XT60H-M × 5 var). `maliyet.json:111` satırı değişir: **fiyat ve stok doğrulanmadı**, yeni bakım gerekir. Panel deliği yeni parçayla ölçülür. Rehberde K1, F1 ve F5 metni değişir |
| c | Kol **ana anahtar sonrasına** alınır | Ana anahtar kapalıyken pimler enerjisiz. Şarj ancak ana anahtar açıkken olur: F4 / F5 dalları, ESP32, akü ADC bölücüsü ve K11 a'da göğüs dalı da enerjilenir. Ana anahtar şarj akımını da taşır. `elektrik.md:372` ve akü raporu önerisiyle çelişir; E3 / E9 yeniden okunmalı |
| d | Bugünkü gibi: XT60E-M, sigorta kalıcı takılı; konnektöre **kapak** ve uyarı etiketi | Parça değişmez; kapak `maliyet.json`'a fiyatsız aday olarak girer. 12,8 V'ta çarpma tehlikesi düşük, açık pimler arasında kısa devre 10 A sigorta atana kadar akım çeker (genel bilgi). Rehberdeki geçici uyarı kalıcı olur |

**B'nin görüşü:** b, olmazsa a. Gerilimli tarafı dokunmaya kapalı yapan tek seçenek b; a parça değiştirmez ama her seferinde hatırlamaya
dayanır; c güvenlik düzenini şarj için değiştirir; d riski kabul eder.

Karar ne olursa olsun, rehberdeki F5 notu ("kuyruğa girmedi", D-9) ve gerekirse K1 / F1 metni sonraki rehber turunda karara göre
güncellenir.

## C için kesin `git add` listesi (18 dosya)

```
git add tasarim/freecad/rehber/rehber_metin.py \
        tasarim/freecad/rehber/rehber_denetim.py \
        tasarim/cad/viewer-template.html \
        rehber/veri/rehber-veri.json \
        rehber/veri/rehber-veri.js \
        planlama/rehber/R-gunluk.md \
        planlama/rehber/kontrol.json \
        planlama/rehber/Lale-montaj-rehberi.pdf \
        planlama/rehber/goruntu/adim-17.png \
        planlama/rehber/goruntu/adim-33.png \
        planlama/rehber/goruntu/adim-35.png \
        planlama/rehber/goruntu/adim-49.png \
        planlama/rehber/goruntu/telefon-360-adim-35.png \
        planlama/rehber/goruntu/telefon-360-adim-49.png \
        tasarim/Robot-Tasarim-Demosu.html \
        planlama/d158/F7d-brief.md \
        planlama/d158/F7d-gunluk.md \
        planlama/d158/F7d-kontrol.md
```

**Girmez:**
- `planlama/d158/FREECAD-KILIT.txt` (izlenmiyor, "boş");
- `planlama/dongu-158.md`;
- `tasarim/cad/lale158-model.js` (izlenmiyor, bu paketin değil);
- `__pycache__/`;
- F9d alanı ve başka paketlerin dosyaları;
- `rehber/veri/robot.glb` ve `robot-glb.js` (HEAD ile aynı).

**Commit sırası (D-6):** F9d'nin README'si "(54 sayfa)" diyor. F7d, F9d ile aynı anda ya da ondan önce commit'lenmeli.

## Commit mesajı (güncel)

```
Lale P7.4: rehberde son düşükler: F3 göğüs regülatörü ölçüm sırası açık (ana anahtar kapalıyken akü tak → aç → oku → kapat → akü ayır → uçları sök; ölçümden önce takı çıkar, 12 V fiş ucu yalıtılır; K11 b'de 12 V fişi F5 aşama 2'de ölçümden sonra), mantar ve regülatör ölçümünde DC V / V soketi / klemensin + ucu, F1 mantar NC süreklilik denemesi (akü ayrık), şarj girişi 10 A (kol akü XT60'ının robot tarafında, aşama 1 / 2 takılı değil, sigortadan sonra gerilimli pim uyarısı; konnektör KT-F7d-1), denetimde köprüleme eş anlamlıları + röleyi elle kapatma + "açtıktan sonra tak", pencere yalnız enerjiyi bitiren ifadede kesilir, ZORUNLU 40, PDF 54 sayfa ≥ 8,1 pt; demo "Bu sayfa hakkında" F9b denetimlerine göre; düzeltme 1'de veri metni FreeCAD'siz rehber_veri.py kuralıyla yazıldı, üretim damgası 20:26 (F7d)
```

## Kanıtlar (bu tur)

```
git status --porcelain -uall + sha1 (başta / sonda)                       → aynı; kilit "boş"; headless Chrome 0
veri_fark.py (ilk tur da04cf4af2b0 ↔ şimdi; HEAD ↔ şimdi)                  → 3 fark yolu (K1.is_, F3.is_, F5.not_); listeler aynı; js = json; biçim birebir; metin → veri fark 0
rehber_denetim.py (depo)                                                  → 0; zorunlu 0/40, yasak 0, istisna 5
enjekte_b.py f7d_B/d1/denetim                                             → 0; B 14/20 (B13/B19/B20 yakalandı), NB 8/10, J/K 31/31, S 3/3, P 8/8
d1/enjekte_d1.py / n_a.py                                                 → R 8/8 yakalandı, RN 3/3 temiz / N1–N4 temiz
rehber_uret.py --veri-yok --cikti f7d_B/d1/uret                           → 0; 50/50, konsol 0, 1192 ↔ 1192, 360 px 7/0, PDF 54, denetim 0/40
B PDF ↔ depo PDF (saat maskeli metin); pdf_olc_b.py                       → 54/54 aynı; 54 sayfa, en küçük 8,10 pt, taşan 0, eşleme = kontrol.json
f7d_B/d1/demo_kopya: demo_uret.py                                         → 0; bayt bayt aynı (e6537a6bce81)
F9b-dogrula.py / carpisma_kos.py kontrol / regresyon.py --yazma           → 0 / 0 / 0
ad_tara_b.py (18 dosya)                                                   → TOPLAM 0
```
