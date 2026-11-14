# Lale: kablolama paketinin (P10.7) elektrik ön kararları

Tarih: 14.11.2026 (ilk yazım, düzeltme turu 1 ve 2, C adımı). Karar: **orkestratör, Ahmet'in 13.11.2026 yetkilendirmesiyle** ("sormak zorunda
olmadığın şeyde sorma, inisiyatif al"). Durum: **karar verildi; K1, K10, K11, K14 kapandı** (ilk iki kontrol `planlama/d158/kablolama-onkarar-kontrol.md`
ve `kablolama-onkarar-kontrol-2.md` DÜZELTME GEREKLİ dedi, düzeltmeler işlendi; üçüncü bağımsız bakış `kablolama-onkarar-kontrol-3.md` **GEÇER**,
A1–A7 metin düzeltmeleri bu sürümde; değer ve kablaj değişmedi).
Kapsam: karar kuyruğu K1, K10, K11, K14; pano #6 / #7'den gelen dört öneri (ses yolu, hub beslemesi, Pi → ESP32 reset hattı, elde taşınan
acil stop); pin kararından gelen parça işleri (röle sürücüsü, dirençler). Kısaltmalar: **EL** = `planlama/adim3/elektrik.md` (satır sayısı
değişmedi, 522), **KK** = `planlama/d158/karar-kuyrugu.md`, **PH** = `planlama/adim3/pin-haritasi.md` (sürüm 4), **KY/** =
`tasarim/freecad/lale158/kafa-yerlesim/`, **LK** = `tasarim/freecad/lale158/lale158-kontrol.json` `kablo_ozet`, **MJ** = `planlama/maliyet.json`
(yalnız okundu). Pano mesajları veri olarak okundu (#5 mesaj #23, #6 mesaj #21, #7 mesaj #22).

## 0. Özet

| # | Konu | Karar | Varsayılandan sapma | Acil stopta |
|---|---|---|---|---|
| K1 | Altıncı USB cihazı | **Yok.** Ses kararıyla (§5) cihaz sayısı **4** | Varsayılan a (5 cihaz) tuttu; ses kararıyla 4'e iner | – |
| K10 | PAM8403 5 V | **a: D24V50F5 (Pi hattı), masa denemesine bağlı** (KT1); geçmezse b (SY8205) | Yok | Enerjili (F3, röle öncesi) |
| K11 | Göğüs ekranı 12 V girişi | **a: ana anahtar sonrası, röle öncesi; sigorta kutusunun 6. yuvası, F6 3 A** | Yok (sigorta yeri düzeltildi) | Enerjili, ekran açık |
| K14 | Boyun demeti | **a: CAD'deki 5 kablo**, şartlı (alınacak HDMI Ø ≤ 6, fiş geçiş sırası, masa denemesi, demet bağlanmadan Efe'nin reset cevabı) | Yok; demet büyümüyor | – |
| Ö1 | Ses: ReSpeaker çıkışı → PAM8403 | **Masa denemesine bağlı kabul** (KT2); yedek USB ses kartı siparişte | K16'daki 04.11 seçimini değiştirir | Enerjili (F3) |
| Ö2 | Hub harici beslemeli | **Hayır**, USB'den beslenmeye devam | Efe'nin önerisinden sapma | Enerjili (F3) |
| Ö3 | Pi → ESP32 reset hattı | **Yeni tel yok.** Bilinçli reset mevcut CP2102 DTR / RTS devresinden; demet bağlanmadan Efe'nin cevabı beklenir | Efe'nin önerisinden sapma (Efe'ye soru) | Reset = röleler bırakır (bilinen) |
| Ö4 | Elde taşınan acil stop | **Karar verilmedi** (Ahmet + Efe). Seçenekler ve kablaj etkisi §8 | – | – |
| PH | Röle sürücüsü | **BC337-40 + 270 Ω + 2,2 kΩ taban → GND + 1N4007** (PH sürüm 4 + 14.11 düzeltme; pinler değişmedi) | Sürüm 3'ün MOSFET şartı kalktı | – |

Kablo sayısı: **62 → 61** (ses kartı uzatması çıkar; göğüs 12 V'ta ara kablo yok), boyun demeti **değişmez** (5 kablo, 69,9 mm², en dar
kesit %44,8). Ayrıntı §11. Maliyet: genel toplamda **−83,80 TL + üç standart sigortanın fiyatı** (P10.7a: 3 × 4,33 TL, Motorobit; `planlama/maliyet.json`'da), koşullu toplamda
**−77,46 TL + USB 2.0 uzatma farkı**. Ayrıntı §10. 16.11 siparişinden önce değişen kalemler tek tabloda: §17.

## 1. K1 · Altıncı USB cihazı

- **Kaynak:** pano #5 mesaj #23 (Efe'nin tarafı, 13.11): "altıncı USB cihazı yok, sayıyı 5'e düzeltin"; yazılımda da plan yok, kafa düzeni (B) değişmez.
  Aynı mesaj: ses ReSpeaker çıkışından verilirse sayı 4'e iner. KK K1 notu bunu kaydetmişti.
- **Karar:** kapat. Cihazlar: ReSpeaker Mic Array v2.0, kafa ekranı dokunmatiği, göğüs ekranı dokunmatiği, ESP32 (CP2102). §5 kararıyla USB ses
  kartı çıkar: **4 cihaz**. Pi portları: 1 ReSpeaker, 2 **boş** (ses yolu denemeyi geçmezse yedek ses kartı buraya), 3 hub, 4 kafa dokunmatiği;
  hub: 1 göğüs dokunmatiği, 2 ESP32, 3–4 boş.
- **Sınama:** a ile c arasında 0 TL ve 0 kablo farkı vardı; cevap a'yı doğruladı. Kafa düzeni B ve boyun kanalı değişmez.
- **Etkilenen:** EL tablo "USB" satırı, "USB" paragrafı ve port tablosu, açık iş 17, blok şema; `KY/uygulama-notu.md:131-132` (C adımında yalnız not).

## 2. K10 · PAM8403'ün 5 V besleme noktası

- **Seçenekler:** a) D24V50F5 (Pi hattı); b) SY8205 (kafa ekranı hattı); c) ayrı küçük düşürücü (+61,20 TL, yer doğrulanmadı).
- **Pi hattı 5 V bütçesi, kalem kalem (hesap, ölçülmedi; D24V50F5 5 A sürekli, EL:23):**

  | Kalem | Akım @ 5 V | Kaynak |
  |---|---|---|
  | Pi 5 + Active Cooler, tam yük | 2,40 A (12 W) | EL E8 tablosu ("Pi 5 + Active Cooler", yoğun 12,0 W) |
  | ReSpeaker Mic Array v2.0 | 0,18 A | Seeed wiki ("5V, 180mA with led on") |
  | Hub: göğüs dokunmatiği ~0,08 + hub denetleyicisi ~0,05 | 0,13 A | EL:26 (dokunmatik); hub denetleyicisi **tahmin** |
  | Kafa ekranı Touch (QLED; besleme SY8205'ten, Touch yalnız veri) | ~0,05 A | **tahmin** |
  | Kamera Module 3 | 0,14 A (0,7 W) | EL E8 tablosu |
  | PAM8403 tepesi (3 W hoparlör, verim %85 varsayımı) | 0,71 A | `KY/uygulama-notu.md:98` (kontrol %83 ile 0,72 A buldu) |
  | **Toplam** | **≈ 3,61 A (5 A'in %72'si)** | hesap |
  | AI HAT+ (takılırsa) | +0,5 A (~2,5 W) → **4,11 A (%82)**; yükte +0,9 A (~4,5 W) → **4,51 A (%90)** | **güç değeri resmî değil** (üretici sayısı bulunmadı; tahmin) |

  `KY/uygulama-notu.md:98`'deki 3,28–3,38 A Pi tam yükünü içermiyordu (dosyanın kendi notu). PAM'ın 0,71 A'i 3 W sürekli sinüs ortalamasıdır;
  sinüs tepelerinde anlık ≈ 1,4 A'e çıkabilir (hesap), D24V50F5 çıkış kondansatörü ve Pi'nin girişi bunu süzer; ölçülmedi.
- **Neden a (şartlı):** (1) D24V50F5 kısa devre, aşırı akım, ısı korumalı (EL:23); SY8205 sayfası koruma yazmıyor (EL:25). (2) **Ses yolu
  toprağı:** §5 kararıyla ses ReSpeaker'dan çıkıyor; ReSpeaker Pi USB'sinden (yani D24V50F5 çıkışından) beslenir. PAM da aynı çıkıştan
  beslenince ses kaynağı ile yükselteç aynı düşürücünün çıkış toprağını paylaşır; b'de PAM akımı SY8205 toprağından girişteki ortak noktaya
  dolaşır (iki düşürücü de yalıtımsız, toprak yine ortak ama halka büyür). (3) Model zaten a ile çizildi (`KY/uygulama-notu.md:97, 113`).
  Bütçe AI HAT+'sız %72, AI HAT+'lı %82–90: pay kesin değil, bu yüzden karar **masa denemesine bağlı**.
- **Şart (KT1, masa denemesi):** Pi stres (ör. `stress-ng` dört çekirdek) + hoparlörde en yüksek ses (sınırlayıcı takılıyken, §5) + AI HAT+
  takılıysa onun yükü. Ölçüm (düzeltme turu 2):
  - **Akım:** D24V50F5 çıkış hattında **DC (Hall) pensle** ya da GND dönüşüne konan bilinen bir **şöntle** (gerilim düşümünden). Seri multimetre
    kullanılmaz: 10 A kademesi ve uçları 4 A'de ≈ 0,1–0,2 V düşürür, kendi başına yanlış düşük gerilim uyarısı doğurabilir (kontrol-2 bulgu 7).
    AC pens DC okumaz.
  - **Pi girişi:** `vcgencmd pmic_read_adc` çıktısındaki **EXT5V_V** (Pi 5'e özgü; Raspberry Pi belgeleri "supply voltage EXT5V_V").
  - **Uyarı:** `vcgencmd get_throttled`; belgeye göre bit 0 (0x1) "Undervoltage detected", bit 16 (0x10000) "Undervoltage has occurred".
    Deneme sonunda değer **0x0** olmalı (bit 16 açılıştan beri olanı gösterir).
  - **Geçme ölçütü:** `get_throttled` = 0x0 ve hat akımı ≲ 4 A.
- **Geçmezse: b (PAM SY8205'ten).** SY8205 yükü 0,9 A (QLED, varsayım) + 0,71 A ≈ **1,61 A (3,7 A'in %44'ü)**. Kablo etkisi: "PAM 5 V"
  yine tek kablo, yalnız kaynak ucu D24V50F5 çıkışından SY8205 çıkışına (P6KE6V8A sonrası) taşınır; boy CAD'den okunur (SY8205 ve PAM
  kafa içinde, yol ölçülmedi). SY8205'te koruma yazmadığı için PAM 5 V hattına küçük bir sigorta ya da PTC (≈ 1–1,5 A; değer o gün,
  satıcıyla) eklenir. ReSpeaker ve PAM ayrı düşürücülerde olur: KT2 uğultu denemesi b'de yinelenir. b de geçmezse c (+61,20 TL).
- **AI HAT+:** siparişi ya da takılması bu denemeye bağlıdır (AI HAT+ yokken geçen bir deneme AI HAT+'ı kapsamaz).
- **Acil stopta:** F3 dalı röleden önce (EL:91): PAM ve hoparlör enerjili kalır (a, b, c'de aynı). Robot acil stopta konuşabilir.
- **Kablo:** "PAM 5 V" D24V50F5 → PAM, yol 64 / önerilen 80 mm (LK `kablo."PAM 5 V"`); b'ye geçilirse uç değişir.

## 3. K11 · Göğüs ekranının 12 V dalı

- **Seçenekler:** a) ana anahtar sonrası, röle öncesi (acil stopta ekran açık); b) röle K1'in anahtarlı barası (acil stopta ekran kapanır).
- **Güvenlik sınaması:** acil stopun işi hareket enerjisini kesmek: anahtarlı bara (BTS7960 ×2 ve dört motor, XL4016 A / B / C ve on servo;
  EL:91, EL:325-331). Göğüs ekranı hareket üretmez; a'da ekran açık kalsa da hiçbir eklem ya da teker enerji almaz. Pi (F3) ve ESP32 (F4)
  acil stopta zaten açık; ekran acil stop durumunu gösterebilir. b'nin bedeli: ekran her acil stopta söner, regülatör kondansatörü ön şarj
  edilen bara kapasitesine eklenir (EL E9), ekran akımı F1 ve K1 kontağından geçer. Güvenlik kazancı yok. **Karar: a.**
- **Bağlantı noktası (düzeltme turu 1):** ilk yazımdaki "kutunun besleme ucundan ayrı hat yuvasına" bağlantı, yuvanın 16 AWG giriş kablosunu
  yalnız ana 30 A'ya bırakıyordu (kontrol D2). Seçenekler: (i) kutunun röle öncesi boş yuvası + bıçak sigorta; (ii) kontrolün öbür önerileri:
  F2 15 A çıkışından hat yuvası ya da "besleme ucundan ≤ 10 cm, bara kesitinde" şartı. **Seçilen (i): kutunun 6. yuvası = F6, standart bıçak.**
  Gerekçe: korumasız ara kablo hiç kalmaz (sigorta kutunun içinde, dal kablosu sigortanın çıkışından başlar); ayrı hat yuvası ve bir bağlantı
  noktası kalkar; F2'yi yük taşır hâle getirmez (F2 15 A yedek kalır, 18 AWG'yi 15 A korumazdı). Kutu 6 yollu, F1–F5 beşini kullanıyor
  (EL:323, :365-369): altıncısı boş / yedekti. Ürün sayfası (Motorobit, 14.11 okundu) yalnız "6 kanal", 0–32 V ve ölçü (115 × 53 × 42 mm)
  yazıyor; ortak giriş yazmıyor.
- **Kutu girişi kuralı (düzeltme turu 2, KT3):** "korumasız ara kablo yok" cümlesi **yalnız kutunun yuvaları ortak giriş barasındaysa** doğrudur.
  Teslimde bakılır (multimetre süreklilik: yuvaların giriş uçları birbirine bağlı mı). **Ayrı girişliyse** ana anahtardan yuvalara giriş
  köprüleri **12 AWG** (ana kablo kesiti), kutunun üstünde olabildiğince kısa, **tek bir giriş klemensinden yıldız** bağlanır. Bu köprüleri
  yalnız ana 30 A korur; bu durum F1–F6'nın hepsi için ve paketten eskidir, K11 onu büyütmez. EL Sigorta listesindeki H1 notuna yazıldı.
- **Ana anahtar kapalıyken:** kutunun girişi ana anahtardan sonra (EL:323): F6 dalı da kesilir.
- **Sigorta değeri (hesap):** ekranın gerçek en çoğu: Waveshare wiki tipik ~0,5 A, kutudaki adaptör **12 V / 1 A** (`raporlar/kaynaklar/07-gogus-ekrani-ve-5v.md:19`)
  → en çok 12 W kabul edildi. LM2577 + LM2596 verimi kaynakta yok, **%80 varsayımı**: giriş 15 W → 10 V'ta **1,50 A**, 12,8 V'ta 1,17 A,
  14,6 V'ta 1,03 A. Tipik ekranla 0,59 A (12,8 V) / 0,75 A (10 V).
  - 2 A: en kötüde %75 yük. Bıçak sigortalar sürekli akımda anma değerinin altında kullanılır ve sıcakta değerleri düşer (etek havası ölçüt
    sınırı 45 °C, EL E7); %75 + sıcak etek dar pay.
  - **3 A seçildi:** en kötüde %50. 18 AWG kablo (EL:62) 3 A ile korunur; regülatör kartı ve jak 1 A çıkış akımında. İlk açılışta regülatör giriş
    kondansatörünün dolum akımı bıçak sigortanın zaman eğrisinde kısa sürer (ölçülmedi, KT3).
  - **3 A standart bulunamazsa 5 A standart kabul:** en kötü 1,5 A = %30; 18 AWG 5 A ile de korunur (otomotiv kablajında 18 AWG'ye 7,5–10 A
    sigorta yaygın; genel bilgi). Bedeli: ekran dalındaki bir arıza daha geç keser; kablo yine korunur.
- **Sigorta türü (düzeltme turu 2):** kutu **standart (ATO)** bıçak alır (satıcı sayfasındaki set standart; EL:374). Listedeki ek sigortaların
  hepsi "Mini Alçak Profil" (MJ:123–126): mini olanlar hat yuvaları için doğru (7,5 × 2, 5 kafa servoları, 10 şarj; MJ:124–126; şarj P10.7a düzeltme turu 1'de 7,5 A), **kutu için
  yanlış tür**. Kutuya gereken ve sette olmayanlar: **F5 2 A standart** (MJ:123'ün "2 A mini"si yerine), **ikinci 5 A standart** (F4),
  **F6 3 A standart**. Montajda F5 yuvasına yanlışlıkla setteki 5 / 10 A'in takılma riski bu yüzden gerçek; malzeme listesi C'de düzelir.
- **Maliyet:** hat sigortası yuvası 5 → 4 (−36,72 TL, MJ:122; beşincisi göğüs içindi, EL:41). Standart 3 A (ya da 5 A), 2 A ve ikinci 5 A
  standart bıçak: bu yazımda fiyat okunamamıştı; P10.7a'da (14.11) Motorobit standart 2 / 3 / 5 A 4,33 TL bulundu, `planlama/maliyet.json`'a işlendi.
  MJ:123 (2 A mini, 7,34 TL) çıkar.
- **K8 notu (Ahmet'e bilgi):** 29.10 H1 kararı (EL:378-380): kutu 1 × 6 dizilişliyse uçtaki iki yuva kapak altında kalır ve yedek için ayrılır
  (F2 ve boş yuva). F6 bu boş yuvayı alır: göğüs ekranı sigortası kapak altında kalabilir. Seyrek atacak bir sigorta için kabul edilebilir
  (sık değişen F1, F3, F4, F5 ortada kalır); 2 × 3 dizilişte hepsi açıkta. Kutuda boş yedek yuva kalmaz.
- **Kablajda teyit edilecek:** kutunun ortak girişi; ilk açılışta F6'nın atmadığı; regülatör 12 V'a ayarlı; ekran jakı ölçüsü (EL açık iş 16).

## 4. K14 · Boyun kablo demeti

- **Kaynak:** pano #6 mesaj #21 (Efe'nin tarafı): boyun düzeni yazılım açısından kabul; tek çekince mekanik (≈ 950 mm HDMI'nin pan / tilt
  ekleminden geçmesi; ince / esnek kablo ve büküm payı bizde). Masada ≈ 1 m HDMI denemesi (soru f) cevapsız.
- **Demet (LK; çaplar tahmini, `kablo_yolu_ekran.py:20-36`):** 12 V çift 18 AWG 10,6 mm² + tilt servo 5,9 + göğüs HDMI Ø6 28,3 + hub
  uzatması Ø4 12,6 + hoparlör Ø4 12,6 = **69,9 mm²**. Yol (kafadan aşağı): tabla kablo geçişi → çatal tabanı → adaptör + mil Ø32 → mil arka
  penceresi 20 × 10 (175 mm², **%39,9**) → kablo odası → servo yuvası arka kanalı 20 × 7,8 (156 mm², **%44,8**) → alt çıkış 20 × 12
  (204 mm², **%34,3**) (`kablo_yolu_ekran.py:3-4, 37-38`).
- **Bu paketin kararları demeti değiştirmiyor:** ses (§5) kafa içinde; reset (§7) yeni tel eklemiyor (Efe "tel gerekir" derse aşağıdaki etki);
  hub (§6) gövdede.
- **Karar: a (CAD'deki gibi), şartlarla:**
  1. **Alınacak kablo şartı:** göğüs HDMI'si (micro HDMI → HDMI A) dış çapı **≤ 6 mm**, ince / esnek. Listedeki kablonun (MJ:191, "HDMI Erkek
     Mikro HDMI Erkek Altın Uçlu Kablo, 1,5 m", Robotistan 117,10 TL) çapı satır ve ürün adında yok: **bu şartı karşıladığı bilinmiyor.**
     Sipariş ya da teslimde çap ve fiş ölçüsü bakılır; karşılamazsa satır bu şartla değişir (maliyet sahibi, C adımı).
  2. Pan halkası ±90° için (`arayuz.py:579`), kodun pan sınırı ±45 bu aralıkta.
  3. **Fişlerin kanaldan geçişi (düzeltme turu 2; CAD okuması kontrol-2 Madde 6, `kafa7_parcalar.py:143-148, 243-244`):** servo yuvası arka
     kanalı **20 × 7,8 mm kapalı tünel** (≈ 34 mm boy; yandan açık değil), fiş iki yerde **dik döner** (mil içinden pencereye, tünelden alt
     çıkışa). Fiş ölçüsü depoda yok (`kablo_yolu_ekran.py:5`); tipik kalıp gövdeleri kontrol-2'nin tablosunda (ölçülmedi). **Karar değişmez**
     (5 kablo, CAD değişikliği yok), **alınacak kablo şartı kesinleşir:**
     - **Hub uzatması USB 2.0** (hub USB 2.0, EL:36; listedeki MJ:137 bir USB 3.0 uzatma: fişleri büyük ihtimalle geçmez, kablosu da Ø4 değil
       ≈ Ø5–5,5). **Erkek fiş gövdesi ≤ 13 × 7 mm.** Erkek uç aşağıdan yukarı (Pi port 3'e), **HDMI'den önce**, tünel boşken geçirilir.
     - **HDMI:** Ø ≤ 6 mm; **micro HDMI ucu** (fiş gövdesi ≤ 7 mm kalın, ≤ 18 mm geniş, boyu ≲ 30 mm: iki dik dönüş) aşağıdan yukarı → Pi HDMI1;
       **HDMI A ucu gövdede kalır** (ekran tarafı, 90° adaptörle, MJ:142).
     - **Sıra:** (1) hub uzatması, (2) HDMI, (3) tilt servo kablosu (3 pinli fiş küçük), (4) hoparlör ve (5) 12 V çifti **fişsiz**; uç kontakları
       / pabuçlar geçirdikten sonra takılır.
     - **Sipariş (16.11):** hub uzatması yeni şartla (USB 2.0, erkek fiş gövdesi ≤ 13 × 7 mm) ve HDMI Ø ≤ 6 mm şartıyla sipariş edilir;
       sipariş deneme için bekletilmez (kontrol-3 A2).
     - **Zorunlu adım: kablo demeti kurulmadan önce fiş geçirme denemesi.** Bunun için boyun tünelinin kısa bir **deneme parçası** basılır:
       yalnız kanal kesiti (20 × 7,8 mm, ≈ 34 mm boy), iki dik dönüş ve mil penceresi 20 × 10 (P10.7 / baskı listesine iş maddesi; CAD'e bu
       pakette dokunulmadı). Deneme kablolar teslim edilince yapılır; parça basılmadan önce evdeki herhangi bir USB 2.0 A erkek ve micro HDMI
       kabloyla da ön deneme yapılabilir. Kumpas ölçüsü tek başına yetmez (dik dönüşler).
     - **Fiş geçmezse sırasıyla:** (a) kablo fişsiz geçirilir ve yeniden sonlandırılır: USB 2.0'da dört damar, **lehimli (ya da sıkmalı) USB-A
       fiş**, D+ / D− bükümü ≤ 1 cm açılır; (b) HDMI için **şerit (FPC) HDMI + takılır uç adaptörleri** (kafa ekranında aynı düzen, EL:57); şerit
       düz geçer, adaptörler sonra takılır; 1080p'yi KT4'ün masa denemesi gösterir. CAD değişikliği (tüneli oluk olarak açmak) önerilmez.
     - Malzeme etkisi: MJ:137 ve MJ:191 "değişecek kalem" (günlük §7 C listesi).
  4. **Demet fiziksel olarak kapatılmadan** (kelepçe / kılıf) önce Efe'nin iki cevabı beklenir (§7). "Tel gerekir" derse bükümlü çift
     eklenir: ≈ 1–2 mm² (tahmin), servo kanalı 69,9 → ≈ 72 mm², **%44,8 → ≈ %46**; mil penceresi ≈ %41, alt çıkış ≈ %35 (hesap).
- **Kablajda teyit edilecek (KT4):** masa denemesi (pano #6 soru f): Pi 5 → aynı ince kabloyla 11,6" ekran, algılama ve 1080p; boyun içi dört
  geçiş elle (HDMI × mil, HDMI × servo yuvası, hub uzatması × mil, hoparlör × mil); pan ±90 ve tilt ±13'te kablo zorlanmıyor. Görüntü gelmezse
  ayrı karar (yedek yol modellenmedi).

**Ahmet'in bilmesi gereken risk (K14):** boyun demeti **yazıldığı gibi kurulamayabilir**. Servo kanalı kapalı ve dar (7,8 mm), fişler iki dik
dönüşten geçmek zorunda; listedeki hub uzatması (USB 3.0) büyük ihtimalle geçmez, HDMI'nin micro ucunun geçip geçmediği bilinmiyor. Kablo
demeti kurulmadan önce, kablolar gelince tünelin deneme parçasıyla yapılacak elle deneme belirleyecek; kablolar bu şartlarla 16.11'de
sipariş edilir, deneme siparişi bekletmez. Geçmezse yedek yollar (yeniden sonlandırma, şerit HDMI) CAD'i
değiştirmeden çalışır ama işçilik (lehim) ve şerit HDMI'de 1080p denemesi ister.

## 5. Öneri 1 · Ses ReSpeaker'ın kendi çıkışından PAM8403'e

- **Kaynak:** pano #7 mesaj #22 madde 1 (Efe'nin tarafı): ses ayrı USB karttan çıkarsa ReSpeaker'ın yankı gidermesi referans alamaz; öneri
  ReSpeaker 3,5 mm → PAM8403, USB ses kartı kalksın; elektrik itirazı (gürültü, toprak döngüsü, seviye) varsa yazın.
- **Üretici (Seeed wiki, ReSpeaker Mic Array v2.0, 14.11.2026 okundu):** "3.5mm Audio jack output socket"; "3.5mm Headphone jack: Output
  audio, We can plug active speakers or Headphones into this port"; codec WM8960; XVF-3000 işlevleri arasında "Acoustic Echo Cancellation
  (AEC)"; 6 kanallı firmware'de "Channel 5: merged playback"; "Max Sample Rate: 16Khz"; "5V, 180mA with led on and 170mA with led off".
- **Çıkarım (doğrulanmadı):** "Yankı giderme kartın kendi çalma akışını referans alır" üreticide açıkça yazmıyor; firmware tablosundaki
  "merged playback" kanalından çıkarım. Efe'nin tarafının söylediğiyle uyumlu.
- **PAM8403 (Diodes PAM8403 veri sayfası / uygulama notu, 14.11 arama sonucu):** kazanç en çok 24 dB (Rf en çok 142 kΩ, Ri en az 18 kΩ;
  elektriksel tablo "Gain = 24dB"); üretici ayrıca giriş sinyali büyük tutulursa çıkışın kırpılacağını uyarıyor. Giriş empedansı sayıyla
  bulunamadı; Ri en az 18 kΩ'dan en az ≈ 18 kΩ çıkarımı (doğrulanmadı). Kartta ses ayarı olup olmadığı satıcı sayfasında doğrulanmadı.
- **Elektrik sınaması:**
  - *Toprak döngüsü:* yeni döngü yok. Eski yolda da ses kaynağı (USB ses kartı) Pi USB'sinden besleniyordu; K10 a ile ReSpeaker ve PAM aynı
    düşürücünün çıkışını paylaşır (§2). Ses kablosu kalkan + iki damar, kalkan yalnız PAM girişi GND'sine.
  - *Kılıf gerçekten toprak mı:* WM8960 gibi kodekler kulaklık çıkışını kondansatörsüz, kılıfı ara gerilimde (toprak değil) sürerek de
    kullanabilir (genel bilgi; bu kartın düzeni belgede yok). Kılıf toprak değilse PAM GND'sine bağlamak o sürücüyü kısa devre eder. Bu
    yüzden KT2'nin ilk adımı süreklilik ölçümü (aşağıda).
  - *Gürültü:* dizi güç kablolarından 40,8 mm (SY8205) ile 129,8 mm (PAM 5 V) uzakta (`KY/uygulama-notu.md:61`); değişmez.
  - *Seviye ve ses tavanı (hesap):* hoparlör 4 Ω, 3 W (`robot-bom.csv:133`) → 3 W'ta çıkış √(3 × 4) = 3,46 V rms → 24 dB (× 15,85) ile girişte
    **≈ 0,22 V rms**. ReSpeaker kulaklık çıkışının tam ölçek seviyesi belgede yok; ≈ 1 V rms varsayıldı (doğrulanmadı). Tavan olmadan en yüksek
    seste PAM kırpar ve hoparlör 3 W'ı aşar.
  - **Ses tavanı seçimi: giriş bölücüsü** (kalıcı ALSA sınırı yerine). Gerekçe: donanım sınırı yazılım ayarı sıfırlansa, başka bir program ya da
    güncelleme ses düzeyini değiştirse de geçerli; ALSA sınırı yalnız ek katman. **Başlangıç değeri (düzeltme turu 2): ReSpeaker çıkışı →
    10 kΩ seri → PAM girişi; PAM girişi → 2,2 kΩ → GND** (ikisi de direnç setinde; 2,7 kΩ sette yok, kontrol-2 bulgu 8). Oran: PAM girişi
    sonsuz empedansta 2,2 / 12,2 = **0,180**; 18 kΩ'da (2,2 ∥ 18 = 1,96 kΩ) **0,164** (−15,7 dB). 1 V rms girişte PAM girişi 0,164–0,180 V rms
    → çıkış (× 15,85) 2,60–2,86 V rms → **1,7–2,0 W** (4 Ω; hesap, kırpma yok varsayımı): 3 W'ın altında. Bölücü çıkış empedansı ≈ 2 kΩ; PAM
    girişinin kondansatörüyle alt köşe hoparlör bandının altında (kontrol-2). ReSpeaker çıkışına yük ≈ 12 kΩ. 0 TL.
    **Son değer KT2 ölçümüyle:** ReSpeaker en yüksek seste 1 kHz sinüs çalarken jak ucunda AC rms ölçülür (V_çıkış); alt direnç
    R = 10 kΩ × 0,22 / (V_çıkış − 0,22) ile seçilir (18 kΩ yüklemesi pay bırakır; modülde seri giriş direnci ya da potansiyometre varsa
    ölçüm onu da kapsar).
  - *USB bütçesi:* Pi 5 USB çevre birimlerine 5 A kaynakla 1.600 mA, aksi hâlde 600 mA verir (raspberrypi.com belgeleri; bütçe fan girişiyle
    paylaşılır). Ses kartının kalkması bütçeyi yalnız rahatlatır. Ayar adları §6.
- **Karar: masa denemesine bağlı kabul.** Yol: Pi USB 1 → ReSpeaker → **ReSpeaker 3,5 mm jakı → 10 kΩ / 2,2 kΩ bölücü → PAM8403 sol girişi**
  (stereo kablo, bir kanal; hoparlör PAM'ın aynı kanalında). USB ses kartı, ~30 cm USB-A uzatma ve L USB-A dirsek kablajdan çıkar; Pi port 2 boş kalır.
- **Yedek (açık):** USB ses kartı (91,80 TL, MJ:78) **siparişte kalır, takılmaz**. KT2 geçmezse kart **Pi port 2'ye** takılır (port boş;
  uzatma ve L dirsek o zaman alınır) ve 04.11 düzeni (K16) geri gelir.
- **K16 notu:** bu karar Ahmet'in 04.11 seçimini (K16: "PAM8403 + USB ses kartı") değiştirir: ses kartı kısmı devreden çıkar, PAM8403 kalır.
  KK K16 girdisine ve EL:145'e "14.11: ses yolu değişti" notu yazıldı. Teknik karar yetkilendirme kapsamında sayıldı; Ahmet itiraz ederse eski
  yol olduğu gibi geri gelir (kart siparişte).
- **Efe'ye soru (taslak, gönderilmedi):** en yüksek örnekleme hızı 16 kHz; konuşma sesi (TTS) 16 kHz'te kabul mü, hangi firmware.
- **Kablajda teyit edilecek (KT2):** (1) **bağlamadan önce** multimetreyle 3,5 mm fişin kılıfı ↔ ReSpeaker USB GND (micro USB kılıfı ya da Pi
  GND) süreklilik: ≤ 1 Ω ve kılıfta DC gerilim yok olmalı; değilse kılıf PAM GND'sine bağlanmaz, yedek yola geçilir; (2) seviye ölçümü ve bölücü
  değeri (yukarıda); (3) en yüksek seste uğultu, bozulma; (4) jak yönü ve kabuk içinde fiş payı (dizi kabuğun 2,5 mm altında); kablo boyu CAD'den.

## 6. Öneri 2 · USB hub harici beslemeli olsun mu

- **Kaynak:** pano #6 mesaj #21 madde e.
- **Hub'daki yük:** göğüs dokunmatiği (~80 mA, EL:26) + hub denetleyicisi (~0,05 A, tahmin) + ESP32'nin VBUS akımı. ESP32 asıl beslemesini çevre
  5 V'tan VIN'e alır; VBUS seri 1N5819 ile ikinci kaynak (EL E4): VIN varken hub'dan kayda değer akım çekmez. Hub yükü **≈ 0,13 A** (hesap).
- **F4 atarsa (düzeltme turu 1):** çevre 5 V gider, ESP32 tamamen VBUS'tan beslenir: 0,24 A (EL:353) → hub ≈ 0,13 + 0,24 ≈ **0,37 A**. Pi'nin USB
  toplamı ≈ ReSpeaker 0,18 + hub 0,37 + QLED Touch ~0,05 ≈ **0,6 A**: Pi ayarı yapılmamışsa 600 mA sınırında, yapılmışsa 1,6 A içinde (hesap).
  Bu durumda röleler zaten bırakmıştır (F4 sonar / PCA9685 mantığını da besler); ESP32'nin hub'dan çalışması yalnız durum bildirimi içindir.
- **Pi USB akım ayarı (raspberrypi.com, "Raspberry Pi hardware" / "Power supply" ve EEPROM sayfaları):** Pi 5 USB çevre birimlerine 5 A kaynakla
  1.600 mA, aksi hâlde 600 mA verir; bütçe fan girişiyle paylaşılır. Kaynak 5 A'i USB-PD ile bildirmezse (D24V50F5 bildirmez) iki yol: EEPROM'da
  `PSU_MAX_CURRENT=5000` ("skip USB power-delivery negotiation and assume … given current rating") ya da `/boot/firmware/config.txt` içinde
  `usb_max_current_enable=1`. Ayar kurulumda yapılır (Efe'nin listesine).
- **Harici beslemenin bedeli:** göğüs üst arka kapağına yeni 5 V (≈ 1,4 m kablo ya da ikinci düşürücü); beslemeli hub'larda VBUS'un Pi'ye geri
  beslemesi "iki 5 V kaynağı köprülenmez" kuralını (EL:56) bozabilir (ürün seçilmedi); yeni sigorta / dal.
- **Karar: hayır**, hub USB'den beslenmeye devam eder (Efe'nin önerisinden sapma; Efe'ye bilgi taslakta).
- **Acil stopta:** hub F3 üzerinden (Pi) enerjili; değişiklik yok.
- **Kablajda teyit edilecek (KT5):** hub girişinde yükteki gerilim (EL açık iş 17); göğüs dokunmatiği ve ESP32 kopmuyor; F4 çıkarılmış hâlde
  ESP32'nin hub'dan çalıştığı ve Pi'nin USB aşırı akım uyarısı vermediği.

## 7. Öneri 3 · Pi'den ESP32 EN'e reset hattı

- **Kaynak:** pano #7 mesaj #22 madde 5: normal çalışmada otomatik reset kapalı kalsın; bilerek reset için Pi'nin bir GPIO'su transistörle EN'e.
- **Bugünkü donanım:** DevKit'teki otomatik reset devresi (CP2102 DTR / RTS → EN / GPIO0) **kartın üstünde ve yerinde**; plan onu sökmüyor, yalnız
  Pi tarafı portu DTR / RTS'yi oynatmadan açıyor (EL:261-264; `main` `kod/robot/seri.py:15-17, 92-106`: "Yine de reset olabilir (sürücüye
  göre)"). PH §8: "O gelene kadar reset yolu CP2102'nin DTR / RTS devresi".
- **Port açılışında istenmeyen reset riski (kontrolün yazdığı gibi):** Linux seri portu açarken DTR ve RTS'yi etkin yapar. pyserial açılıştan
  sonra önce DTR'yi, ardından RTS'yi bırakır; arada **DTR bırakık, RTS etkin** bir an kalır ve bu, DevKit devresinde EN'i LOW çeker: port
  açılışı ya da Pi servisinin yeniden başlaması ESP32'yi resetleyebilir (reset = röleler bırakır, kollar düşer). `ser.dtr = False; ser.rts = False`
  önce ayarlanıp sonra `open()` riski azaltır, sürücüye göre kaldırmaz (`seri.py` yorumu). Ayrı GPIO hattı bu riski kaldırmaz, yanına ikinci
  bir reset yolu ekler; riski yalnız otomatik reset devresinin donanımda kapatılması kaldırır.
- **Ayrı hattın bedeli:** Pi (kafa) → boyun → gövde → taban ESP32, ≈ 1,6 m yeni tel; boyun demetine bükümlü çift (≈ 1–2 mm², servo kanalı
  %44,8 → ≈ %46; tel çapı tahmini); transistör, iki direnç, filtre. Uzun tel HDMI ve servo hattıyla aynı demette: gürültüyle yanlış reset.
  Pi açılışında GPIO'nun varsayılan çekmesi pine göre değişir (raspberrypi.com "Most GPIOs have a default pull applied"; pin pin doğrulanmadı).
- **Karar (değişmedi): yeni tel yok.** Bilinçli reset mevcut DTR / RTS devresinden (Pi yazılımı reset dizisi uygular; esptool aynı devreyi kullanır).
- **Ek şart (düzeltme turu 1):** boyun demeti fiziksel olarak kapatılmadan (kelepçe / kılıf) önce **Efe'nin iki cevabı** beklenir: (1) bilinçli
  reset DTR / RTS ile yapılabiliyor mu; (2) otomatik reset donanımda (kartta iz kesme) kapatılacak mı. Cevap "tel gerekir" ise o zaman bükümlü
  çift eklenir: kesit etkisi §4 madde 4 (servo kanalı ≈ %46); pin, açılışta pull-down olan bir Pi GPIO'su, transistör ESP32 ucunda, tabanına
  pull-down ve RC filtre (değerler o gün).
- **Efe'nin önerisinden sapma:** soru taslağı hazır (gönderilmedi).
- **Kablajda teyit edilecek (KT6):** bilinçli reset dizisi ESP32'yi resetliyor; normal port açılışı resetlemiyor; **Pi servisinin yeniden başlatılması
  ve Pi'nin yeniden açılışı ESP32'yi resetlemiyor** (her biri ≥ 10 kez; ESP32 açılış yazısı ve PC817 #2 / bara izlenir).

## 8. Öneri 4 · Elde taşınan, kumandalı acil stop (karar verilmedi)

**Karar Ahmet + Efe'de** (para ve güvenlik mimarisi; pano #7 mesaj #22 madde 4). Burada yalnız seçenekler ve kablaj etkisi.

| Seçenek | Ne | Kablaja etkisi | Not |
|---|---|---|---|
| A | Yok; demoda mantarın yanında bir kişi (Efe'nin tarafının ara önerisi) | Yok | Bugünkü kablaj |
| B | Kumandalı, arıza-güvenli röle (kumanda, pil ya da alıcı giderse kontak açılır), kontağı K1 / K2 bobin hattında **mantar NC ile seri** (EL:249, EL:443) | F5 → mantar NC → **alıcı kontağı** → bobinler. +2 tel (taban içi), alıcının beslemesi (12 V, F5 ya da F4'ten; ≤ 2 A sigortalı), alıcı ve anten için yer. Yazılım değişmez: PC817 #1 mantar + alıcı sonrasını okursa ikisini birlikte "acil stop" görür | Ürün seçilmedi, fiyat yok. Arıza-güvenli olduğu üreticiden doğrulanmalı |
| C | Yalnız yazılım (telefon DUR düğmesi) | Yok | Gücü kesmez; acil stop sayılmaz |

- **Yer ayrılsın mı (öneri, karar değil):** mantar NC çıkışı ile bobinler arasına bugün **köprülü 2 pin klemens** konursa (köprü takılıyken
  devre bugünküyle aynı) B sonradan kablajı sökmeden eklenir. Maliyet klemens (MJ:117, 5,50 TL). Köprü unutulursa röle çekmez (güvenli yön).

## 9. Pin kararından gelen parçalar (malzeme listesine nasıl girer)

**Röle sürücüsü (düzeltme turu 1 ve 2):** iki röleye de **BC337-40 (TO-92) + 270 Ω seri taban direnci + 2,2 kΩ taban → GND + bobine ters
1N4007**. PH sürüm 4 (14.11 düzeltme notuyla) D1 / D9 / T2a / T2 ve §9 donanım notu buna göre; pinler ve firmware kuralları değişmedi (HIGH =
röle çeker). İlk yazımdaki "BC337 + 1 kΩ" yedeği K1'i doyurmuyordu (kontrol D3). İkinci kontrol (D1) kapalı hâlin yanlış ölçüte dayandığını
buldu: sızıntı akımı rölenin çekme akımıyla değil, **bırakma / çekmeme garantisi gerilimiyle (bobin < 1,2 V)** karşılaştırılır; 4,7 kΩ ile
K2'de en kötü köşe ≈ 1,0–1,2 V'tu (sınırda). Taban → GND **2,2 kΩ** oldu. Hesap (benim betiğim; kontrol-2 ile aynı sonuç; PH D1 / D9):

| Büyüklük | Değer |
|---|---|
| Röle verisi (üretici tabloları MAH3 / JQC-3FF, kontrol-3 doğruladı) | K1 MAH: 85 Ω ±%10, çekme ≤ 8,4 V, bırakma ≥ 1,2 V; K2 JQC-3FF: 400 Ω ±%10, ≤ 9,0 V / ≥ 1,2 V |
| Bobin akımı en kötü | K1 0,191 A (14,6 V, 76,5 Ω) – 0,21 A (soğuk); K2 0,041–0,045 A |
| Boşta taban (pull-up açık; 45 kΩ / 75 µA / 30 kΩ + 3,6 V) | 0,15 / 0,17 / **0,25 V** |
| 70 °C'de kollektör sızıntısı (0,25 V, iki model) | **0,13–0,72 µA** (ICES sınırı ≤ 10 µA @ 125 °C) |
| Bobin gerilimi (kapalı, en kötü) / garanti 1,2 V'a oranı | K1 ≤ 0,07 mV, K2 ≤ 0,32 mV (ICES ile ≤ 4,4 mV) / **≤ %0,4** |
| Taban akımı sürülü: en kötü (2,64 V, VBE 1,2 V) / VBE 0,85 V / tipik (3,3 V, 0,8 V) | **4,79** / 6,24 / 8,90 mA |
| Zorunlu β K1 (0,191 / 0,21 A), en kötü | **39,9 / 43,9**; K2 8,6 / 9,4. hFE en az 250 @ 100 mA (bütün üreticiler); 300 mA'de üreticiye göre 60 (onsemi, Lumimax) – 170 (Diotec). Belgeyle garanti pay 60 × 4,79 mA ≈ 287 mA → **≈ 1,37×** (VCE 1 V'ta; doyum değil) |
| GPIO akımının en çoğu (3,3 / 3,6 V, VBE 0,65 V) | 9,8 / 10,9 mA (seri direnç değişmedi) |
| VCE (sürülü) | belgede ≤ 0,7 V yalnız β = 10'da (500 / 50 mA); **≤ 0,3 V'u hiçbir üretici garanti etmez, belgeyle sınır 1,0 V**: K1 bobini besleme 11 V'ta ≥ 10,0 V, 10 V'ta ≥ 9,0 V (çekme garantisi ≤ 8,4 V); beklenen 0,1–0,3 V, **T2 (g)'de ölçülerek kabul** |
| K1 kaybı (0,21 A; VCE 0,2 / 0,3 / 1,0 V) | 42 / 63 / **210 mW** (+ taban 6 mW); en kötü ≈ 43 K ısınma, 60 °C ortamda **Tj ≈ 103 °C** < 150 °C; izin 0,45 W |
| Yedek seri 220 Ω (T2'de VCE > 0,3 V ise) | I_B en kötü 6,00 mA, β K1 32–35; GPIO 12,0 / 13,4 mA (DS Tablo 5-3'te IOH tipik 40 mA, en yüksek kademe; varsayılan kademe 2 ≈ 20 mA'in de altında). Doyumu o da belgeyle garanti etmez |

- **Parça şartı:** **BC337-40, kazanç sınıfı -40 zorunlu**; sınıfsız "BC337" kabul edilmez: -40 sınıfı 100 mA'de hFE ≥ 250 garanti
  eder ve tipik doyumu sağlar; 300 mA'deki en az değer sınıfa değil üreticiye bağlı (kontrol-3 A1). Gövde yazısı "337-40". Doyumu T2 (g) ölçer.
- **Ayak sırası (T2a, teslimde):** düz yüz önde, ayaklar aşağıda, soldan sağa **C-B-E** (Vishay, onsemi, Diotec, DC Components aynı;
  kontrol-3 A3). Multimetre diyot kademesi: kırmızı uç tabanda, siyah öbür iki ayakta ≈ 0,6–0,7 V; uçlar ters ve C–E arası açık; B–E düşümü
  B–C'den birkaç mV büyük. hFE soketi µA–mA düzeyinde ölçer (doğru yönde yüzler, ters yönde onlar); veri sayfasının 250–630'u 100 mA'de
  tanımlı, sokette ölçüt değil; sınıfı gövde yazısı belirler. **Ters takılırsa** (C ↔ E) kapalı hâlde E–B jonksiyonu bobin besleme gerilimini
  ters görür, VEBO 5 V aşılır, jonksiyon delinir; taban ≈ 0,6–0,7 V'ta kenetlenir, pine ≈ **2–3 mA** gider (hesap). Asıl risk bobin akımı
  (K1'de ≈ 70 mA, delinme gerilimi varsayımla): röle yarı çekebilir ya da sürülünce çekmeyebilir, transistör bozulur.
- **GPIO sürüş gücü:** BJT pinden ≈ 5–11 mA çeker (MOSFET'te statik akım yoktu). 4 ve 19'un sürüş gücü düşürülmez: ESP-IDF varsayılanı
  `GPIO_DRIVE_CAP_DEFAULT = 2` ("medium"; ESP-IDF v4.4.7 `hal/include/hal/gpio_types.h`); `gpio_set_drive_capability` ile 0 / 1'e inilmez.
  Kademeler ≈ 5 / 10 / 20 / 40 mA (ESP32 veri sayfası v5.3 IO_MUX not 8; kontrol-3 A7 okudu).

| Kalem | Adet | Satıcı / fiyat | Durum |
|---|---|---|---|
| **BC337-40** (TO-92), yalnız -40 | 2 + 1 yedek = **3** | Direnc.net BC337-40TA 3,02 TL (kontrol raporu, 14.11) → 9,06 TL | MJ:106 satırının yerine (C adımı) |
| Eski satır VBsemi IRLZ44NPBF-VB (MJ:106) | 2 → 0 | Robotistan 24,40 TL | Çıkar |
| 270 Ω ×2 (taban seri), **2,2 kΩ ×2** (taban → GND), IS bölücüsü 6,8 kΩ ×2 + 5,1 kΩ ×2, enkoder seri 1 kΩ ×2, ses bölücüsü 10 kΩ + 2,2 kΩ; yedek 220 Ω | — | Mevcut direnç seti (MJ:115, 90,50 TL) | Hepsi setin satıcı sayfasında (kontrol-2 okuması: 220 Ω, 270 Ω, 1 / 2,2 / 4,7 / 5,1 / 6,8 / 10 kΩ var; 2,7 kΩ yok); elde sayılmadı |
| 1N4007 ×2 | — | MJ:113 (2 adet) | Değişmedi |

- **Fark:** 3 × 3,02 − 2 × 24,40 = **−39,74 TL** (genel). SOT-23 adaptörü ve AO3400A / IRLML6344 satırları gereksiz.
- **MJ'ye yazılacak (C adımı, maliyet sahibi; MJ bu pakette değişmedi):** "C / P10.7'de girecek" listesi `planlama/d158/kablolama-onkarar-gunluk.md`'de.
  Sigortalar §3'te (kutu standart ister: 2 A, ikinci 5 A, 3 A standart); MJ:106 / 109 notlarındaki "GPIO2" → GPIO19.

## 10. Maliyet farkı

| Kalem | Fark (TL) | Toplam türü | Kaynak |
|---|---|---|---|
| K10 a (b'ye geçilirse küçük sigorta / PTC, fiyat o gün) | 0 | – | – |
| K11: hat sigortası yuvası 5 → 4 | **−36,72** | genel | MJ:122 |
| K11: standart 3 A bıçak sigorta +1 (F6; bulunamazsa 5 A standart) | +4,33 (P10.7a: Motorobit 3 A standart) | genel | MJ '3 Amper Oto Sigorta' |
| Sigorta türü (paketten eski): MJ:123 2 A mini → 2 A standart, +5 A standart | −7,34 + iki standart sigortanın fiyatı (P10.7a: 2 × 4,33) | genel | MJ:123 |
| K14 a: MJ:137 USB 3.0 uzatma → USB 2.0, fiş ≤ 13 × 7 mm; MJ:191 HDMI şartı | değişecek kalem; USB 2.0 uzatma P10.7a'da da fiyat bekliyor (şarta uyan bulunamadı); HDMI satırı şartıyla kaldı, teslimde ölçülür (O-11 b) | koşullu / genel | MJ:137, MJ:191 |
| Ses: USB-A uzatma 30 cm (Pi → ses kartı) çıkar | **−77,46** | koşullu (K4) | MJ:136 |
| Ses: L USB-A dirsek çıkar | 0 (fiyatsızdı) | – | MJ:138 |
| Ses: USB ses kartı | 0 (yedek olarak kalır) | genel | MJ:78 |
| Ses: 3,5 mm kablo (yeni boy) ve bölücü dirençleri | 3,5 mm kablo fiyat bekliyor (P10.7a: kısa erkek-erkek bulunamadı); dirençler setten | – | MJ:141, MJ:115 |
| Hub: harici besleme yok | 0 | – | – |
| Reset hattı: yeni tel yok (Efe "gerekir" derse bükümlü çift + transistör, o gün) | 0 | – | – |
| Acil stop: köprülü klemens (yalnız ayrılırsa) | ≤ 5,50 | koşullu | MJ:117 |
| Röle sürücüsü: IRLZ44N ×2 yerine BC337-40 ×3 | **−39,74** | genel | §9 |
| **Toplam** | **genel −83,80 + üç standart sigorta fiyatı (P10.7a: 12,99) (+ MJ:191 değişirse); koşullu −77,46 + USB 2.0 uzatma farkı** | | |

## 11. Kablo tablosunun girdi özeti (P10.7 için)

62 kablonun dökümü depoda tek dosya olarak bulunamadı (sayı 10.11 rehber dökümünden, `planlama/dongu-158.md:164, :259`); kontrol de
bulamadı. Liste P10.7'de yeniden kurulacak. Aşağıdaki fark listeden bağımsızdır.

| Kablo | Önce | Sonra | Sayıya etkisi |
|---|---|---|---|
| Ses kartı uzatması (Pi USB 2 → L dirsek → USB ses kartı; 217 / 270 mm) | var | **çıktı** | **−1** |
| Ses 3,5 mm | USB ses kartı L 3,5 mm → PAM girişi, 36 / 40 mm | **ReSpeaker 3,5 mm jakı → 10 kΩ / 2,2 kΩ bölücü → PAM girişi**, yol ölçülmedi (CAD'den) | 0 (uç değişti) |
| PAM 5 V | D24V50F5 → PAM, "varsayım" | D24V50F5 → PAM, **K10 a (denemeye bağlı)**, 64 / 80 mm; b'de kaynak ucu SY8205 çıkışı | 0 |
| Göğüs ekranı 12 V | "taban güç paneli" → mini 2 A (hat yuvası) → regülatör → ekran | **sigorta kutusu F6 3 A çıkışı** → LM2577 + LM2596 → ekran; GND yıldız noktasına (M5 saplama, O-3 r); 1.376 / 1.720 mm (regülatör → ekran); kutu → regülatör boyu CAD'den | 0 (ara kablo ve hat yuvası yok) |
| Boyun demeti | 5 kablo, 69,9 mm² | **aynı**; Efe "tel gerekir" derse + bükümlü çift | 0 (+1 koşullu) |
| Pi → ESP32 reset teli | öneri | **eklenmedi** (Efe'nin cevabına bağlı) | 0 |
| Hub harici besleme | öneri | **eklenmedi** | 0 |
| Acil stop alıcı kontağı / köprü | yok | **koşullu** (Ahmet + Efe) | 0 (seçilirse +1 köprü ya da +2) |
| ESP32 USB, göğüs dokunmatiği, dizi USB, hub uzatması, HDMI'ler, kafa içi QLED kabloları | – | değişmedi (HDMI'ye alınacak kablo şartı, §4) | 0 |

**Sonuç: 62 → 61** (yalnız ses kartı uzatması çıktı). Pi USB 2 ve hub 3–4 boş.

## 12. Acil stopa basıldığında enerjili kalanlar (bu kararlardan sonraki son liste)

Ana anahtar devrede (ON), mantar basılı (ya da F5 attı, ya da ESP32 resetlendi):

- **Enerjili:** akü → ana 30 A → ana anahtar → sigorta kutusu baraları; **F3 kafa dalı:** Pi 5, D24V50F5, SY8205, kafa ekranı (QLED),
  kamera, ReSpeaker, **PAM8403 ve hoparlör** (K10), kafa dokunmatiği, USB hub (gövde), göğüs dokunmatiği, ESP32'nin USB VBUS'u;
  **F6 göğüs ekranı dalı** (LM2577 + LM2596, 11,6" ekran; K11 a); **F4 çevre 5 V:** ESP32 (VIN), sonar ×3, enkoderler, PCA9685 ve BNO055
  mantığı, PC817 modülü; F1 çıkışından K1 / K2 kontak girişine kadarki hat; F5'ten mantar NC'ye kadarki hat; akü ölçüm bölücüsü; şarj girişi (ana anahtar öncesi). F2 15 A yedek (yük yok).
- **Enerjisiz:** röle K1 / K2 kontağından sonraki anahtarlı bara: BTS7960 ×2 ve dört JGB37, XL4016 A / B / C ve on servo (kollar düşer,
  kafa pan / tilt gevşer); mantar NC çıkışından sonraki hat: K1 ve K2 bobinleri, PC817 #1 girişi.
- **Bilinen, bu paketten eski:** XL4016 çıkışlarındaki servo kondansatörleri (5 × 2200 µF = 11 mF, 14.11'den beri dağıtım kartı C ile) acil stop anında ≈ ½ · 11 mF · 6² ≈ **0,20 J**
  tutar (EL E9 enerji satırı, düzeltme turu 1'de beş kondansatörle yeniden): kısa bir son servo hareketi olabilir; açık iş EL açık iş 12.
- Bu paketin kararları listeye yalnız **göğüs ekranını** (K11 a) açıkça ekledi; PAM8403 zaten F3'teydi. Hareket üreten hiçbir yük enerjili değil.

## 13. Kablajda teyit edilecek (kararlar bunlara bağlı)

| # | Ne | Kalmazsa |
|---|---|---|
| KT1 | Masa denemesi (K10): Pi stres + en yüksek ses (+ takılıysa AI HAT+); `vcgencmd get_throttled` = 0x0 ve D24V50F5 hattı ≲ 4 A (DC pens ya da şönt, seri multimetre değil); Pi girişi `pmic_read_adc` EXT5V_V | PAM SY8205'e (b, §2); o da olmazsa c (+61,20 TL). AI HAT+ siparişi bu sonuca bağlı |
| KT2 | Ses (Ö1): **bağlamadan önce** jak kılıfı ↔ USB GND sürekliliği (≤ 1 Ω, kılıfta DC yok); en yüksek seste jak çıkışı rms ölçümü ve bölücü değeri (§5); uğultu, bozulma; jak yönü ve fiş payı | Kılıf toprak değilse ya da uğultu çözülmezse USB ses kartı Pi port 2'ye (04.11 düzeni) |
| KT3 | Göğüs 12 V (K11): **teslimde kutunun yuvaları ortak giriş baralı mı** (süreklilik); ilk açılışta F6 3 A (standart) atmıyor; regülatör 12 V'a ayarlı; F5 yuvasında 2 A standart | Ayrı girişliyse giriş köprüleri 12 AWG, kutunun üstünde olabildiğince kısa, tek giriş klemensinden yıldız (§3); sigorta / regülatör yeniden |
| KT4 | Boyun (K14): **demet kurulmadan önce, teslimde, tünel deneme parçasında elle fiş geçirme** (USB 2.0 uzatma fişi ≤ 13 × 7 mm, HDMI'den önce; micro HDMI ≤ 7 mm kalın, ≤ 18 mm geniş, boy ≲ 30 mm); HDMI Ø ≤ 6; masa denemesi 1080p; dört geçiş elle; pan ±90 / tilt ±13'te kablo serbest | Fiş geçmezse: fişsiz geçirip yeniden sonlandırma (USB lehimli fiş); HDMI için şerit (FPC) + uç adaptörleri (§4) |
| KT5 | Hub (Ö2): girişte yükteki gerilim; dokunmatik ve ESP32 kopmuyor; F4 çıkarılmışken ESP32 hub'dan çalışıyor, Pi USB uyarısı yok | Harici besleme yeniden ele alınır |
| KT6 | Reset (Ö3): bilinçli reset dizisi ESP32'yi resetliyor; normal port açılışı, **Pi servis yeniden başlatma ve Pi'nin yeniden açılışı ESP32'yi resetlemiyor** | Ayrı hat / donanım iz kesme yeniden ele alınır |
| KT7 | PH §7 T1–T8 + T2a (kart gelince; T2a BC337-40 ayak sırası diyot testiyle; T2: kontak hiç kapanmıyor, **bobin gerilimi ≤ 0,12 V** (bırakma sınırı 1,2 V'un %10'u; oda sıcaklığında, sıcak köşe yalnız hesapla), çekişte VCE ≤ 0,3 V) | VCE > 0,3 V: seri 220 Ω, T2 yinelenir; PH |
| KT8 | Şarj cihazı (O-13): **ilk şarjda** kesme gerilimi multimetreyle akü uçlarında ölçülür (şarj hedefi 14,4 V = 4 × 3,6 V; 14,6 V yalnız en kötü durum hesap değeri, `elektrik.md:93`) | **14,4 V'u aşarsa** cihaz bu aküde kullanılmaz; LiFePO4 4S profili 14,4 V'a ayarlanabilen cihaz Ahmet'e |

## 14. Ahmet'e kalanlar

- **Elde taşınan acil stop** (Ö4): A / B / C ve "köprülü klemensle yer ayrılsın mı" (Ahmet + Efe).
- **Bilgi:** K16'daki 04.11 seçimi değişti: USB ses kartı kablajdan çıktı, yedek olarak siparişte (§5); denemeyi geçmezse geri gelir. İtiraz ederse eski yol.
- **Bilgi:** K8 (29.10 H1): kutunun boş yedek yuvası göğüs ekranının F6'sı oldu; 1 × 6 dizilişte kapak altında kalabilir (§3).
- **Bilgi:** AI HAT+ siparişi K10 masa denemesine bağlı (§2).
- **Risk (K14):** boyun demeti yazıldığı gibi kurulamayabilir; demet kurulmadan önce tünel deneme parçasıyla elle fiş denemesi belirleyecek (§4,
  "Ahmet'in bilmesi gereken risk").
- **Bilgi (sigorta türü):** kutu standart (ATO) bıçak alır; listedeki mini sigortalar girmez. 16.11 siparişinde 2 A (F5), ek 5 A ve 3 A (F6; yoksa
  5 A) standart; P10.7a'da Motorobit 4,33 TL'den bulundu, `planlama/maliyet.json`'a işlendi (§3, §10, §17).

## 15. Efe'ye sorulacaklar (taslak depo dışında, gönderilmedi)

1. Bilinçli reset için yeni tel yerine mevcut DTR / RTS devresi (§7): `esp32_reset()` bu diziyle yazılabilir mi? Otomatik reset donanımda
   (kartta iz kesme) kapatılacak mı? (Boyun demeti bu cevap gelmeden bağlanmaz.)
2. ReSpeaker çalma akışı 16 kHz (üretici): konuşma sesi için kabul mü, hangi firmware?
3. Bilgi: hub USB'den beslenmeye devam (§6); Pi USB akım ayarı (`PSU_MAX_CURRENT=5000` ya da `usb_max_current_enable=1`) kurulum listesine;
   röle sürücüsü BC337'ye döndü (firmware'i etkilemez, HIGH = çeker; taban → GND 2,2 kΩ); 4 / 19'un sürüş gücü varsayılanda kalmalı;
   T2 yöntemi değişti (bobin gerilimi); masa HDMI denemesi (f) hâlâ açık.

## 16. Etkilenen belgeler

- Bu pakette güncellendi: `planlama/adim3/elektrik.md` (satır sayısı 522, değişmedi), `planlama/adim3/pin-haritasi.md` (sürüm 4; pin tablosu
  HEAD ile ve üç yerde aynı, betikle sınandı), `planlama/d158/karar-kuyrugu.md` (K1, K10, K11, K14 Durum ve özet tablo durum metni; K16 notu; K52 notu; K58 donanım / açık kalan / not
  satırları; sondaki kayıt ve K58 iş maddesi), `planlama/d158/pin-karari-gunluk.md` (§11 sürüm 4 ve düzeltme notu).
- C adımında (14.11, üçüncü bakış GEÇER sonrası): KK'de K1, K10, K11, K14 kapandı, özet tablo ve sayım, dört önerinin kaydı, "karar değil,
  iş" maddeleri; `planlama/dongu-158.md` P10.7 satırı ve §5 girdisi; A1–A7 metin düzeltmeleri (PH D9 / T2a / T2, EL:37 / :268 / :518, bu
  rapor §4 / §9 / §13 / §17).
- P10.7'ye kalan: `planlama/d158/testler/T4-pam8403-ses-karti.md` (başlık ve yol: USB ses kartı → ReSpeaker
  çıkışı, KT1 / KT2 maddeleri), `planlama/maliyet.json` (günlükteki "C / P10.7'de girecek" listesi), `KY/uygulama-notu.md:98, :102-134`
  (tarihçe notu), `tasarim/freecad/arayuz.py` `SES_USB` ve `kablo_yolu_ekran.py` `KABLO` (ses kartı ve uzatması; göğüs 12 V kaynağı; model
  işi, P10.7), rehber şemaları 7 ve 8 (rehber işi, P10.7), `planlama/yazilim-plani.md` (ses ve reset satırları, Efe'nin dosyası değilse).

## 17. 16.11 siparişinden önce değişen kalemler

Bu bölüm tek başına okunur. Kararlar §2–§9'da; `planlama/maliyet.json` (MJ) bu pakette değişmedi, liste P10.7'de oraya işlenir. Fiyatlar
14.11'de okunan değerler; "bekliyor" olanların satıcısı ya da fiyatı doğrulanmadı. **P10.7a (14.11) notu:** liste MJ'ye işlendi; "Satıcı / fiyat" sütunu MJ'deki duruma eşitlendi, kablo tablosundan gelen ikinci tur kalemleri tablonun sonunda.

| Kalem | Eski → yeni | Adet | Satıcı / fiyat | Neden |
|---|---|---|---|---|
| Röle sürücüsü (MJ:106) | VBsemi IRLZ44NPBF-VB → **BC337-40** (TO-92; yalnız -40 sınıfı, gövde yazısı "337-40") | 2 → **3** (1 yedek) | Direnc.net BC337-40TA 3,02 TL (eski Robotistan 24,40 TL); fark −39,74 TL | Listedeki klonun veri sayfası yok, 3,3 V sürüşü doğrulanamadı; mantık seviyeli AO3400A onaylı satıcılarda bulunamadı; BC337-40 delikli, satıcısı belli (§9, PH D9) |
| Kutu sigortası F5 (MJ:123) | 2 A **mini** → 2 A **standart (ATO)** | 1 | Motorobit 4,33 TL (P10.7a; eski 7,34 TL mini çıktı) | Sigorta kutusu standart bıçak alır; mini girmez (§3) |
| Kutu sigortası F4 | + 5 A **standart (ATO)** (setteki tek 5 A'e ek) | 1 | Motorobit 4,33 TL (P10.7a) | F3 ve F4 iki 5 A ister (§3) |
| Kutu sigortası F6 (yeni) | + 3 A **standart (ATO)**; bulunamazsa 5 A standart | 1 | Motorobit 4,33 TL (P10.7a; 3 A bulundu) | Göğüs ekranı 12 V dalı kutunun 6. yuvasından (K11, §3) |
| Hat sigortası yuvası (MJ:122) | 5 → **4** | 4 | Motorobit; fark −36,72 TL | Göğüs ekranı dalı kutuya geçti (§3) |
| Hub uzatması (MJ:137) | USB 3.0 uzatma 1 m → **USB 2.0** A erkek-dişi ~1 m, **erkek fiş gövdesi ≤ 13 × 7 mm** | 1 | fiyat bekliyor (P10.7a: onaylı satıcılarda şarta uyan bulunamadı; eski Motorobit 214,20 TL çıktı) | Boyun tüneli 20 × 7,8 mm, iki dik dönüş; USB 3.0 fişi büyük ihtimalle geçmez (K14, §4) |
| Göğüs HDMI kablosu (MJ:191) | Şart eklenir: dış çap **Ø ≤ 6 mm**, ince / esnek; micro HDMI fişi ≤ 7 mm kalın, ≤ 18 mm geniş | 1 | Robotistan 117,59 TL (14.11; sayfa "Tükendi"; çapı bilinmiyor, teslimde ölçülür, O-11 b) | Boyun kanalı doluluğu ve fiş geçişi (K14, §4) |
| USB ses kartı uzatması (MJ:136) ve L USB-A dirsek (MJ:138) | **Çıkar** | 0 | −77,46 TL (koşullu) / fiyatsızdı | Ses ReSpeaker'ın 3,5 mm çıkışından (§5) |
| USB ses kartı (MJ:78) | Kalır, **yedek** olarak | 1 | değişmez | Masa denemesi geçmezse Pi port 2'ye takılır (§5) |
| 3,5 mm kablo (MJ:141) | Ses kartı → PAM yerine **ReSpeaker → PAM** (boy CAD'den) | 1 | fiyat bekliyor (P10.7a: kısa erkek-erkek bulunamadı) | Ses yolu (§5) |
| Dirençler (MJ:115) | Yeni kalem yok: 270 Ω ×2, 2,2 kΩ ×2, ses bölücüsü 10 kΩ + 2,2 kΩ, yedek 220 Ω **setten** | – | mevcut set 90,50 TL | Setin sayfasında var; elde sayılmadı (§9) |
| **P10.7a ikinci ve üçüncü tur (14.11, orkestratör kararları O-1 / O-3 / O-4 / O-8 / O-18):** kablo metreleri | 12 AWG kırmızı 2 → **5** m, siyah 2 → **3** m; 16 AWG kırmızı / siyah 1 → **5** m; 18 AWG kırmızı 7 → **11** m, siyah 7 → **9** m; 20 AWG kırmızı / siyah **+1** m (yeni) | – | Robocombo 118,00 / 60,50 (09.11 fiyatı, 14.11 okunamadı); Motorobit 43,26 / 24,72 | Kesitler kablo tablosundan (O-1 c), metre = CAD / liste boyu ya da kaba üst sınır tahmini (× 1,25; üçüncü turda 150 mm pay kaldırıldı) × 1,3 (`planlama/adim3/kablolar.md` §Malzeme özeti; boylar P10.7b'de ölçülecek) |
| Servo uzatma (MJ:19) | 19 → **23** | 23 | Robotistan 44,71 TL (sayfa "Tükendi", 14.11) | 10 uzatma 17,5 m × 1,3 |
| 2200 µF (MJ) | 4 → **5** | 5 | Motorobit 4,33 TL | Kafa dağıtım kartı C (O-8; EL:130 "önerilir, maliyette yok" idi) |
| Delikli pertinaks / 5,08 mm 2 pin klemens (MJ) | 5 → **6** / 4 → **12** | – | Direnc.net 24,20 / Robocombo 5,50 (09.11) | Dağıtım kartı C; dağıtım kartı ve arayüz kartı girişleri, Ö4 köprü yeri (O-6) |
| Halka pabuç (M5) | **+** sarı RV 5.5-5 (4–6 mm², 12 AWG) 10'lu × 4 (O-22 a köprüleri 14 uç); **+** mavi RV 2-5 (1,5–2,5 mm², 16 AWG) × 2; **+** kırmızı RV 1.25-5 (0,5–1,5 mm², 18–22 AWG) × 1 | 4 + 2 + 1 | Motorobit 49,44 / 24,10 / 19,78 TL | O-3 revize: düğümler M5 saplama üstünde pabuç yığını; 12 AWG sarı pabucun aralığının altında, teslimde denenir |
| Bara saplaması M5 | Hazır güç barası **alınmaz**; M5 × 25 cıvata + somun + yaylı pul takımı (saplama başına ≤ 4 pabuç, ABYC E-11; O-22 a, orkestratör kararı 14.11: yıldız 5, anahtarlı bara 4 saplama + 1 yedek; zincir köprü 4 + 3 adet 12 AWG; P10.7b'de şerit / pano tipi nötr barası bulunursa sadeleşir) | 10 takım (önce 6) | fiyat bekliyor | O-3 revize (üçüncü tur) + düzeltme turu 1; yalıtkan tutucu basılır, CAD'i P10.7b |
| Hat sigortası yuvası / 2 A mini | 4 → **5** / 2 A mini V3'e geri (+1); O-19 a ile 5 → **6** / 1 → **2** | 6 / 2 | Motorobit 37,08 / 7,42 TL | O-18 b: G22'nin bara ucunda 2 A (yuva mini bıçak alır); O-19 a: XL4016 çevre çıkışında 2 A (orkestratör kararı 14.11) |
| Sinyal teli ve uçlar | **+** 22 AWG çok telli 15 m rulo × 3 (fiyat bekliyor: onaylı satıcılarda stokta yok); Dupont kiti **çıktı** (pense yok); jumper dişi-dişi × 3 (uç olarak fabrika sıkılı dişi uçlar: tablodaki 89 dişi uç × 1,3 → 2 set + 1 masa), erkek-dişi × 1 | 3 / – / 3 / 1 | Motorobit 43,26 / 49,44 TL | O-4 revize: jumper ortadan kesilir, sinyal teline lehim + makaron |

Siparişle birlikte iş (malzeme değil): boyun tünelinin kısa **deneme parçası** basılır (P10.7 baskı listesi); fiş denemesi kablolar gelince,
demet kurulmadan önce (§4, KT4).

## 18. Orkestratör kararları (14.11)

P10.7a ikinci turda orkestratör O-1 … O-14'ü kararlaştırdı; karar metinleri, tabloda nasıl uygulandıkları ve açık kalanlar tek kaynakta:
`planlama/adim3/kablolar.json` (`kararlar`, `orkestratore`; okunur görünüm `planlama/adim3/kablolar.md`). Ayrıntılı kayıt
`planlama/d158/kablo-tablosu-gunluk.md` "Orkestratör kararları (14.11)". Bu belgeyi etkileyenler:

- **O-6 a / c:** acil stop düğümü güç panelinde çok çıkışlı klemens (2273-203 × 2, köprülü; P10.7a ek turunda, orkestratör kararı 14.11: WAGO 2273 yalnız tek telli alır, düğüm küçük pertinaks parçasında iki 2 pin 5,08 mm vidalı klemens, kart üstünde köprülü; kafa girişi de aynı biçimde, üç klemens); mantar ile düğüm arasında Ö4 için köprülü
  iki uçlu yer. Ö4'ün kendisi (§8) **açık**, Ahmet + Efe.
- **O-10 b / O-11 b:** K4 kalemleri koşullu kalır, sipariş yine verilir; şartlı hazır kablolar (§4, §17) mevcut satırlarıyla alınır,
  teslimde ölçülür; onaylı satıcı dışına çıkmak Ahmet'in kararı.
- **O-12:** bas-konuş düğmesi açık (Efe'ye sorulacak); tabloya kablo eklenmedi, kalem değişmedi.
- **O-13:** şarj hedefi 14,4 V (4 × 3,6 V); 14,6 V yalnız en kötü durum hesap değeri. Şarj cihazı kalır; ölçüt §13 KT8.
- **O-14 a:** bugünkü yazılım kuralı + watchdog kalır, kablaj değişmez; kendini tutma kontağı / Ö4 açık.
- **O-2 / O-3 / O-4:** kesit tablosu web kaynaklı (33 CFR 183.425 ve NFPA 79 Table 12.5.1, temkinli değer); 12 AWG baraya halka pabuçla;
  sinyal teli 22 AWG, uç olarak jumper'ın fabrika sıkılı dişi ucu (O-4 r; Dupont kiti çıktı), pense yok: lehim + makaron. Sipariş değişiklikleri §17'nin sonunda.
- **Üçüncü tur (orkestratör kararı, 14.11):** O-15 kayıtlı istisna `ana-hat-12awg` (12 AWG / 30 A değişmez; şart: ayrı döşeme, P10.7b'de
  gerilim düşümü; beklenen sürekli akım 25 A'in altında). O-16 kayıtlı istisna `motor-fabrika-kablosu` (uzatma gerekirse 12 AWG). O-17
  şarj kolu: + ana sigortanın yük tarafı / ana anahtarın akü tarafı, − yıldız; sigorta akü tarafındaki ucun dibinde (karar 10 A; düzeltme turu 1'de **7,5 A mini**). O-18 b: G22'nin
  bara ucunda 2 A hat sigortası. O-3 revize: hazır bara yok, M5 saplama üstünde pabuç yığını. O-4 revize: Dupont kiti yok, jumper uçları.
- **Açık kalan (orkestratöre):** K52 (göğüs regülatörünün yeri, G20); Ö4; O-12. Ayrıntı `planlama/adim3/kablolar.md` §Orkestratöre.
