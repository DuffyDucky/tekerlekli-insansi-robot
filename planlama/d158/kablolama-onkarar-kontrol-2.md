# Kablolama ön kararları (P10.7): ikinci bağımsız kontrol, 14.11.2026 (02:39)

Kontrol edilen: `planlama/adim3/kablolama-on-kararlar.md` (**R**), `planlama/adim3/pin-haritasi.md` sürüm 4 (**PH**; `git diff b1c2a8d`),
`planlama/adim3/elektrik.md` (**EL**), `planlama/d158/karar-kuyrugu.md` (**KK**), `planlama/d158/kablolama-onkarar-gunluk.md` (**G**),
`planlama/d158/pin-karari-gunluk.md` (fark), Efe'ye pano taslağı (depo dışı). Karşılaştırma: `planlama/maliyet.json` (**MJ**), ilk kontrol
`planlama/d158/kablolama-onkarar-kontrol.md` (**K1R**), CAD kaynakları `tasarim/freecad/kafa/kafa7_parcalar.py` ve
`tasarim/freecad/lale158/kablo_yolu_ekran.py` (yalnız okundu, FreeCAD ve betik koşulmadı). Pano #8 mesaj #24'ün gönderilen gövdesi depo
dışı kopyasından okundu; panoya ne yazıldı ne "okundu" işaretlendi. Hesaplar elle ve depo dışı küçük bir hesap betiğiyle; hiçbir şey
ölçülmedi. Bu dosya dışında depoda hiçbir şey değişmedi.

Veri sayfaları (bu kontrolde açıldı): Vishay *BC337 / BC338*, Doc. 85112 Rev. 1.2 (02-Nov-04); Meishuo *MAH3* otomotiv rölesi bobin tablosu
(MAH ailesinin 40 A kardeşi; MAH-112-C-4'ün kendi veri sayfası indirilemedi, satıcı listesi aynı 1,7 W bobini yazıyor); JQC-3FF 12 VDC
(Hongfa tabanlı tablolar, satıcı özetleri); ON Semi BC337 (300 mA'de hFE en az 60, arama özeti); satıcı sayfaları: sigorta kutusu (MJ:88) ve
direnç seti (MJ:115).

## Hüküm: **DÜZELTME GEREKLİ**

Tek durduran bulgu var ve küçük: röle sürücüsünün kapalı hâl gerekçesi yanlış ölçüte dayanıyor (sızıntı akımı rölenin **çekme** akımıyla
karşılaştırılmış; doğru ölçüt **bırakma gerilimi**). Röle verisiyle yeniden hesapta K2 için en kötü köşede garanti payı ≈ 0 çıkıyor. Çözüm
setteki 2,2 kΩ ile tek değer değişikliği (D1 aşağıda). BC337-40 seçimi, 270 Ω, pin tablosu, firmware kuralları, K10, K11 (F6) ve ses kararı
doğru; K14 fiş geçişi kurulabilir ama "alınacak kablo şartı + tanımlı yedek yol" olarak yazılmalı (bulgu 1, durdurmaz).

## Durduran bulgu

### D1 · Röle sürücüsünün kapalı hâli: ölçüt çekme akımı değil bırakma gerilimi; K2'de en kötü köşede pay yok (röle) — **durdurur**

- **Nerede:** PH:18 ("taban ≤ 0,49 V, transistör kesimde kalır"), PH:324-338 (D9 kapalı hâl; PH:334-336 "en kötü köşede bile ≈ 8 kat altında:
  **röle çekmez**"), PH:294 (D1 4,7 kΩ), PH:380 (T2), PH:426-427 (JSON `donanim`); R:249 ("K2 ≈ 22 mA'in ≈ 1/8'i"); EL:268, EL:444, EL:483-484;
  `pin-karari-gunluk.md` §11 son madde.
- **Röle verisi (kaynak):** K1 MAH-112-C-4 (MJ:107): Meishuo MAH3 bobin tablosu 12 V: **85 Ω ±%10, 1,7 W, çekme ≤ 8,4 V, bırakma ≥ 1,2 V**
  (23 °C). K2 JQC-3FF-12VDC (MJ:109): **400 Ω ±%10, çekme ≤ 9,0 V, bırakma ≥ 1,2 V**. Üreticiler yalnız iki sınır verir: "en geç 8,4 / 9 V'ta
  çeker" ve "en erken 1,2 V'ta bırakır". Belirli bir rölenin hangi gerilimde çekeceği bu ikisi arasında herhangi bir yer olabilir; "çekmez" ve
  "çekiliyse kesin bırakır" garantisi yalnız **bobin gerilimi < 1,2 V** iken var. PH'nin "%75 çekme" oranı çekmenin **en geç** noktası; çekmeme
  için ölçüt olamaz.
- **Kendi hesabım (PH'nin modeliyle aynı: IC = 1 mA·exp((VB − V₁)/VT), V₁ 0,60 / 0,55 V, −2 mV/K):** en kötü varsayım köşesi (dahili pull-up
  30 kΩ, VDD 3,6 V → taban 0,49 V; 70 °C) kollektör ≈ 0,5–2,5 mA (PH 0,5–2,8 mA; aynı mertebe).
  - K1: 2,8 mA × 85 Ω ≈ **0,24 V** < 1,2 V: pay ≈ 5×. Sorun yok.
  - K2: 2,8 mA × 360–440 Ω ≈ **1,0–1,23 V**: bırakma garantisinin (1,2 V) **tam sınırında**. Yani bu köşede K2'nin çekmeyeceği ya da çekiliyse
    bırakacağı veri sayfasıyla garanti edilmiyor. PH'nin "8 kat pay" cümlesi bu yüzden yanlış.
  - Gerçekçi köşe (VDD 3,35 V, pull-up 30 kΩ, 70 °C) ≈ 0,8 mA → K2 ≈ 0,3 V; tipik (45 kΩ) µA düzeyi. Risk düşük, ama güvenlik rölesinde
    belgelenen en kötü durumun payı sıfır olmamalı. K2 istemeden çekerse bara 5,6 Ω üstünden beslenir ve XL4016'lar servolara güç verir (EL E9).
  - T2 oda sıcaklığında yapılıyor. 70 °C köşesini ölçmez: "bobin akımı ≤ 1 mA" oda sıcaklığında kolayca geçer (hesap ≈ 0,01–0,09 mA), sıcak
    durum hakkında bilgi vermez. T2'nin "aşılırsa 2,2 kΩ" yedeği bu yüzden hiç tetiklenmeyebilir.
- **Önerilen düzeltme (en az değişiklik):** taban → GND direnci **4,7 kΩ → 2,2 kΩ** (direnç setinde var: satıcı sayfası "2,2KΩ", MJ:115),
  seri 270 Ω aynı kalır.
  - Boşta taban: tipik 3,3 × 2,2 / 47,2 = **0,15 V**, en kötü (30 kΩ, 3,6 V) **0,25 V**. Kollektör 70 °C'de bile < 1 µA (K2'de < 1 mV).
    Sıcaklık ve pull-up belirsizliği ortadan kalkar.
  - Sürülü hâlde: en kötü I_B = (2,64 − 1,2)/270 − 1,2/2200 = **4,79 mA**. Gerçekçi VBE 0,85 V ile 6,2 mA. GPIO akımı değişmez (≤ 9,8 / 10,9 mA).
  - Zorunlu β gerçek bobinle (bulgu 2): K1 0,19–0,21 A → **40–44** en kötü, gerçekçi ≈ 31. BC337-40'ın hFE'si 100 mA'de en az 250, 300 mA'de
    en az ≈ 170 (BC338-40 satırı) → ≈ 5× aşırı sürüş: doymuş. K2 ≈ 8.
  - İstenirse daha güçlü doyum için **220 Ω + 2,2 kΩ** (sette var): I_B en kötü 6,0 mA, β K1 32–35, GPIO en çok 12,0 / 13,4 mA. Espressif
    sınırının (VOH ≥ 2,64 V, 40 mA'e kadar) içinde, ama orkestratörün 10 mA hedefini aşar. Ben 270 Ω + 2,2 kΩ'u öneriyorum.
- **Değişecek yerler:** PH:18, PH:294 (D1), PH:304-312 (D1 hesabı), PH:324-338 (kapalı hâl tablosu ve "8 kat" cümlesi → "bobin gerilimi < 1,2 V
  bırakma sınırı, MAH3 / JQC-3FF veri sayfası"), PH:380 (T2: ölçüt "bobin gerilimi ≤ 0,12 V, yani bırakma sınırının ≤ %10'u". "2,2 kΩ'a in"
  yedeği kalkar; kontak kapanırsa D1 / D9 yeniden), PH:426-427 (`donanim` "2.2k taban -> GND"), R:237, R:249, R:255, EL:251, EL:259, EL:268,
  EL:444, EL:483-484, `pin-karari-gunluk.md` §11. Pin numaraları ve Y kuralları değişmez; JSON `surum` 4 kalabilir (yalnız donanım alanı) ya
  da 5 (karar sizin).
- **Neden durdurur:** brief'in sınıflamasıyla röleyi ilgilendiren her bulgu durdurur; hem de belgelenen gerekçe yanlış. Düzeltme tek değer ve metin.

## Öbür bulgular (kayıtlı açık iş olarak gidebilir)

1. **K14 fiş geçişi: CAD'de kanal yandan açık değil; listedeki USB 3.0 uzatması büyük ihtimalle geçmez. Kurulabilir, ama şart + yedek yol
   yazılmalı.** (R:119-130, R:320 KT4, MJ:137, MJ:191). Aşağıdaki "Madde 6" bölümünde ayrıntı. **Durdurmaz:** rota ve 5 kablo kararı doğru;
   her durumda çalışan, CAD'i değiştirmeyen bir yedek yol var (fişsiz geçirip yeniden sonlandırma). Ama MJ:137 sipariş edilmeden önce şart ona
   yazılmalı. Yoksa demet "yazıldığı gibi kurulamaz" durumuna teslimde düşülür.
2. **K1 bobin akımı 0,17 A değil, en kötü 0,19–0,21 A** (PH:314-316, R:244, EL:268). MAH bobini 85 Ω ±%10 (yukarıda). 14,6 V'ta 76,5 Ω ile
   0,191 A; soğuk bobinde (0 °C, bakır −%9) ≈ 0,21 A. 270 Ω / 4,7 kΩ ile zorunlu β K1 en kötü **37,6–41**, ajanın 33,5'i değil. Doyum yine yeterli
   (hFE en az ≈ 200 civarı; -40 şartıyla). Kayıp ≤ 0,21 A × 0,7 V ≈ 0,15 W, 0,45 W iznin içinde. Metindeki "~0,15 A, ölçülecek" yerine üretici
   değeri yazılsın. T2'deki "K1 ≈ 80 Ω" → 85 Ω ±%10. Röle verisi olmadığı için yazılan "yaygın oran" cümleleri (PH:334, R:249) üretici sınırlarıyla
   değişsin. Bırakma: MAH bobini 1,2 V altında, yani ≈ 13 mA altında kesin bırakır.
3. **"-40" kazanç sınıfı yük taşıyor; malzeme satırı ve teslim kontrolü buna göre olmalı** (PH:302 D9, R:253). Sınıfsız "BC337" (Direnc.net
   1,21 TL satırı) -16 olabilir: hFE 100 mA'de en az 100, 300 mA'de en az 60 (ON Semi, Vishay BC338-16). β ≈ 40'ta aşırı sürüş 1,5–2× kalır,
   VCE 0,3 V'u geçebilir. MJ satırına "yalnız BC337-40 (gövde yazısı 337-40)" yazılsın. Ayrıca **ayak sırası teslimde doğrulansın** (TO-92
   ayak dizilişi üreticiye göre değişebilir; Vishay çizimi E-B-C numaralı). C ve E ters lehimlenirse kapalı hâlde ters bağlı jonksiyon VEBO'yu
   (5 V) aşar, bobinden GPIO'ya ≈ 10–25 mA akım itilir (hesap). Kart bağlanmadan multimetrenin diyot kademesiyle B–E / B–C. PH §7'ye (T2'den
   önce) bir satır.
4. **T2'de "çekişte VCE ≤ 0,3 V" ölçütünün kalmazsa yolu yok** (PH:380). Yalnız "kontak kapanırsa" yolu var. Öneri: "VCE > 0,3 V ise seri
   direnç 220 Ω'a iner (D1), T2 yinelenir".
5. **F6 / K11: "korumasız ara kablo hiç kalmaz" yalnız kutunun ortak giriş baralı olduğu varsayımıyla doğru** (R:84-87, R:319 KT3, EL:68).
   MJ:88 satıcı sayfası (14.11 okundu): "6 Channel Auto Blade Fuse Box", 0–32 V DC, 115 × 53 × 42 mm, 6 kanal, montaj delikleri 103 mm arayla
   (tek sıra, 1 × 6), içinde 1 × 5, 1 × 10, 2 × 15, 2 × 20 A standart bıçak. **Ortak giriş yazmıyor.** Piyasada bu boyda hem ortak giriş saplamalı
   hem de her yuvası ayrı giriş-çıkış uçlu kutular var. Ayrı girişliyse F6'nın (ve F1–F5'in) girişine ana anahtardan köprü gerekir. Bu köprüleri
   yalnız ana 30 A korur: ilk kontrolün D2 sorunu, bu sefer altı yuvanın hepsinde ve K11'den bağımsız olarak (paketten eski). 6. yuvanın boş
   olduğu doğru: F1–F5 beşini kullanıyor (EL:91, :364-371). Girişi röle öncesi: kutu ana anahtardan sonra, F1 röleye gider (EL:323-339).
   **Öneri:** KT3'ün "kalmazsa" sütunu somut kural alsın: "Yuvalar ayrı girişliyse giriş köprüleri ana kablo kesitinde (12 AWG) ve kutunun
   üstünde, ≤ 10 cm, tek bir giriş klemensinden yıldız". Bu, F1–F5 için de EL Sigorta listesine bir satır. **Durdurmaz:** K11 kararı bu riski
   yaratmıyor ya da büyütmüyor; teyit zaten KT3'te.
6. **Mini / standart bıçak uyuşmazlığı gerçek, ve F5 (acil stop bobin sigortası) onun içinde** (R:96-98, G §6.5 madde 3, MJ:123-126,
   EL:374-377). MJ'deki ek sigortaların hepsi "Mini Alçak Profil" (2, 5, 7,5 × 2, 10 A). Hat yuvaları (MJ:122 "Mini/Micro") dört mini ister:
   7,5 × 2, 5 (C), 10 (şarj). MJ:124–126 bunu tam karşılar. Kutu ise standart (ATO) ister. Setinde olmayanlar: ikinci 5 A (F4), 2 A (F5), 3 A (F6).
   MJ:123 "2A Mini" kutuya girmez. Montajda F5 yuvasına setteki bir 5 / 10 A standardın takılma riski var (acil stop bobin hattı).
   **Öneri:** G §6.5'teki "sahibine soru" yerine kesin C maddesi: MJ:123 → **2 A standart**, **+5 A standart**, **+3 A standart**. 3 A standart
   bulunamazsa F6'ya 5 A standart da kabul edilebilir: 18 AWG korunur; ekranın en kötü girişi 1,5 A. Bu yedek R §3'e bir cümle. Paketten eski,
   durdurmaz.
7. **K10 masa testi ölçülebilir, iki ayrıntı eksik** (R:63-65, KT1).
   - Akım: "pens" yalnız DC (Hall) pens olabilir; AC pens okumaz. Multimetre seri bağlanırsa 10 A kademesi ve uçlar 4 A'de ≈ 0,1–0,2 V düşürür.
     Bu düşüm kendi başına düşük gerilim uyarısı doğurup testi yanlış düşürebilir. Öneri: akım GND dönüşündeki bilinen bir şöntle ya da
     DC pensle ölçülür. Ayrıca Pi 5'in kendi giriş gerilimi `vcgencmd pmic_read_adc` (EXT5V_V) ile okunur.
   - Uyarı: `vcgencmd get_throttled` sonucu 0x0 olmalı (bit 0 şimdi, bit 16 açılıştan beri düşük gerilim).
   - Kalemler doğru: 2,40 + 0,18 + 0,13 + 0,05 + 0,14 + 0,71 = 3,61 A. b'nin kablo etkisi doğru: tek kablo, uç SY8205 çıkışı, 1,61 A / 3,7 A = %44.
   - Küçük eskime: EL:29, EL:278 ve EL:511 (açık iş 8) hâlâ "tepe hesaplanmadı" diyor; artık Pi hattı tepesi var (EL:52). C'de bir kelime.
8. **Ses bölücüsü: hesap doğru; 2,7 kΩ sette yok, frekans / gürültü sorunu yok** (R:159-165).
   - Direnç seti sayfasında 2 kΩ, 2,2 kΩ, 3,3 kΩ var, **2,7 kΩ yok** (10 kΩ, 1 kΩ, 5,1 kΩ, 6,8 kΩ, 270 Ω, 4,7 kΩ var).
   - 10 kΩ / 2,2 kΩ ile oran 0,180 (yüksüz) – 0,164 (18 kΩ yük). 1 V rms varsayımıyla 1,7–2,0 W: başlangıç değeri olarak daha güvenli. Kesin
     değeri KT2'deki formül seçer; metin "masa denemesinde ayarlanır" demeli, şu an öyle diyor.
   - Bölücü çıkış empedansı ≈ 2,1 kΩ. PAM girişinin ≈ 18–20 kΩ'u ve modülün giriş kondansatörüyle (tipik 0,47–1 µF, doğrulanmadı) alt köşe
     ≈ 10–20 Hz: 40 mm hoparlörün bandını etkilemez. Bölücü sinyali ve kaynak gürültüsünü birlikte böler: SNR değişmez.
   - PAM8403 kazancı modüle göre değişebilir (kartta seri giriş direnci ya da potansiyometre varsa); KT2 ölçümü bunu da kapsar.
9. **Pano taslağı: Efe'nin bilmesi gereken iki şey eksik** (taslak madde 5; pano #8 mesaj #24'ün gönderilen gövdesi).
   - #24 Efe'ye "gate pull-down 4,7 kΩ … osiloskopla gate / röle ölçümü" ve "ör. AO3400A" dedi. Taslak sürücünün BC337'ye döndüğünü ve
     firmware'i etkilemediğini söylüyor, doğru. Eksik: **T2'nin ölçüm yöntemi değişti** (bobin gerilimi, bütün durumlar F5 takılı, bara yüksüz;
     Efe T2'ye katılacaksa bilmeli).
   - Eksik: **4 ve 19'un sürüş gücü düşürülmemeli.** BJT her pinden ≈ 6–10 mA çeker; `gpio_set_drive_capability` ile en düşük kademeye
     (≈ 5 mA) inilirse VOH düşer, taban akımı azalır. Varsayılan (kademe 2) ya da üstü kalmalı. MOSFET'te statik akım yoktu, bu yeni bir koşul.
     PH §5'e Y kuralı değilse D9'a not olarak.
   - Taslağın geri kalanı: kısa, kaynaklı, kişisel veri / takma ad yok, "karar verdik, bağımsız kontrol bekliyor" doğru.
10. **Kayıt tutarlılığı: `pin-karari-gunluk.md` değişti ama hiçbir yerde sayılmıyor** (R §16, G §6.1 "Röle sürücüsü" satırı "PH, EL, KK").
    `pin-karari-gunluk.md` §11 eklendi (14 satır). R §16 ve G §6.1'e eklensin. Ayrıca PH başlığı "Değişenler: D1, D9, §3.1 hesabı, T2, §9 donanım
    notu" diyor, ama §0 röle kuralı, §2 satır 4 / 19, §3.2, §4, Y2 ve kaynak satırları da değişti ("gate" → "taban"); başlıkta "bağlı sözcükler"
    ifadesi bunu karşılıyor, sorun değil.
11. **EL E9'da ana anahtar açılış darbesine F6 dalı eklenmeli** (EL:461 "yalnız F3/F4/F5 girişleri bağlanır, ≤ 0,6 mF"). K11 a ile
    LM2577 + LM2596 kartının giriş kondansatörleri de ana anahtarla bağlanır (değer bilinmiyor). Bilgi notu; KT3 zaten ilk açılışı izliyor.
12. **EL:446 eski K2 verisi** ("JQC-3F(T73) 7 A, 18,23 TL"); v4'te JQC-3FF 10 A (EL:93, MJ:109). Paketten eski; C'de tek kelime.

## Madde 1 · BC337 röle sürücüsü (baştan hesap)

| Büyüklük | Değer (kaynak) |
|---|---|
| BC337-40 hFE | 250 / 400 / 630 @ 100 mA, 1 V (Vishay 85112); 300 mA'de BC338-40 en az 170 (vekil); ON Semi: BC337 ailesi 300 mA'de en az 60 |
| VBE / VCE(sat) | VBE en çok 1,2 V @ 300 mA, 1 V; VCE(sat) en çok 0,7 V @ 500 mA / 50 mA; VBE(sat) yalnız eğri |
| Sınırlar | VCEO 45 V, VEBO 5 V, IC 800 mA, IB 100 mA, Ptot 625 mW, RθJA 200 °C/W, Tj 150 °C; ICES ≤ 100 nA (45 V) |
| ESP32 çıkışı | VOH ≥ 0,8 × VDD = 2,64 V, kaynak akımı 40 mA'e kadar (en yüksek sürüş kademesi; PH'nin DS Tablo 5-3 okuması). En kötü hesap 2,64 V ile, bu 10 mA'de ihtiyatlı |
| Bobinler | K1 MAH: 85 Ω ±%10, çekme ≤ 8,4 V, bırakma ≥ 1,2 V; K2 JQC-3FF: 400 Ω ±%10, ≤ 9,0 V / ≥ 1,2 V |

| R_seri / R_taban-GND | I_B en kötü (2,64 V, VBE 1,2 V) | I_B gerçekçi (VBE 0,85 V) | β K1 en kötü (0,191 / 0,21 A) | GPIO en çok (3,3 / 3,6 V) | Boşta taban en kötü | K2 bobini en kötü köşe |
|---|---|---|---|---|---|---|
| 270 Ω / 4,7 kΩ (sürüm 4) | 5,08 mA | 6,45 mA | 37,6 / 41 | 9,8 / 10,9 mA | 0,49 V | ≈ 1,0–1,2 V (sınırda) |
| **270 Ω / 2,2 kΩ (öneri)** | 4,79 mA | 6,24 mA | 40 / 44 | 9,8 / 10,9 mA | 0,25 V | < 1 mV |
| 220 Ω / 2,2 kΩ | 6,00 mA | 7,75 mA | 32 / 35 | 12,0 / 13,4 mA | 0,25 V | < 1 mV |

- **270 Ω doğru mu:** evet. "Zorunlu β 33,5" gerçek bobinle 38–44'e çıkıyor (bulgu 2), -40 sınıfında hâlâ ≈ 5× aşırı sürüş. 220 Ω daha
  güvenli doyum verir, bedeli ≈ 12–13 mA GPIO akımı (Espressif sınırı içinde). İkisi de kabul edilebilir; asıl değişmesi gereken taban-GND
  direnci (D1).
- **Bırakma:** firmware LOW yazınca taban ≈ 0 V, kollektör nA düzeyinde: iki röle de kesin bırakır. Çekili bir rölenin düşük akımda tutunması
  ancak pin "çıkış HIGH"tan reset görmeden "pull-up'lı giriş"e geçerse söz konusu. Bunu yapan bir yol bulamadım: resette çıkış kapanır, 4 wpd,
  19 yüzer; `SPI.begin()` 19'u pull-up'sız giriş yapar. 2,2 kΩ ile bu senaryo da kapanır.
- **Geri tepme:** her bobine ters 1N4007 (EL:443, MJ:113 adet 2). Kollektör en çok ≈ 14,6 + 1 V < VCEO 45 V. Düz diyot bırakma süresini uzatır
  (MAH3 bırakma ≤ 5 ms diyotsuz; diyotla on ms mertebesi, ölçülmedi). Acil stop mantarın kendisi bobini kestiği için güvenlik açısından önemsiz;
  E9 dizisinde 100 ms beklemeler var.
- **MOSFET'e göre gözden kaçan sakınca:** depolama süresi µs mertebesi, röle için önemsiz. Sıcakta ICES kaçağı (125 °C'de ≤ 10 µA) önemsiz.
  Asıl sıcaklık etkisi VBE'nin düşmesi; o da D1'de. Yeni olan üç koşul: kazanç sınıfı (bulgu 3), ayak sırası (bulgu 3), GPIO sürüş gücü (bulgu 9).
- **Isı:** en kötü 0,21 A × 0,7 V + taban ≈ 0,155 W → ≈ 31 K ısınma; 60 °C'de izin 0,45 W. Beklenen VCE 0,1–0,3 V'ta < 0,07 W.

## Madde 2 · Pin raporu sürüm 4

- `git diff b1c2a8d -- planlama/adim3/pin-haritasi.md`: yalnız başlık, röle kuralı cümlesi (PH:18), BJT kaynak satırı (yeni) ve MOS satırına
  "sürüm 3" etiketi, MJ satırı, §2 satır 4 ve 19 (bağlı donanım ve donanım şartı sütunları), §3.1 tablo ve "eski firmware" K1 / K2 yolu,
  §3.2 bir kelime, §4 iki satır ve röle kilidi cümlesi, Y2'de "gate" → "taban", D1, D9 ve hesapları, T2, JSON `surum` ve ROLE_K1 / K2
  `uc` / `donanim`, §10 iki madde değişmiş. **Pin numaraları, işlevler, öbür 23 pinin satırları, Y1–Y13'ün anlamı, D2–D8 ve T1, T3–T8
  değişmemiş.** JSON'da yalnız `surum` ve iki satırın `uc` / `donanim` alanı değişmiş; `gpio`, `yon`, `acilis`, `en_cok_ms` aynı.
- Kalıntı taraması (MOSFET, gate, AO3400A, IRLML, IRLZ, drain, 220 Ω): yalnız bilerek bırakılmış tarihçe satırlarında (PH:4, :36 "sürüm 3;
  kullanılmıyor", :41, :45, :340-342 "neden MOSFET değil", :456). Kendi içinde çelişki yok; D1'deki "8 kat" cümlesi yanlış (D1 yukarıda).
- Pano #8 #24 ile çelişki: bulgu 9.

## Madde 3 · F6 / K11

- Yapı ve konum doğru: kutu ana anahtar sonrası, röle öncesi; F1–F5 beş yuvayı kullanıyor, 6. yuva boştu (H1 notunda yedek). Ana anahtar
  kapalıyken F6 da kesilir.
- Akım: ekran en çok 12 W (12 V / 1 A adaptör), regülatör verimi %80 varsayımı → 10 V'ta 1,50 A = 3 A'in %50'si (hesabım aynı). 18 AWG 3 A ile
  korunur. LM2577 + LM2596 kartı bu girişte çalışma bölgesinde (anahtar akımı ≈ 3 A sınırının altında; ölçülmedi).
- Açık kalan: ortak giriş (bulgu 5), standart 3 A (bulgu 6), ana anahtar açılış darbesi (bulgu 11). Mini / standart uyuşmazlığı gerçek (bulgu 6).

## Madde 4 · K10

Kalemler ve kaynakları tutuyor (3,61 A; AI HAT+ ile 4,11–4,51 A, resmî değer yok). "≲ 4 A" ölçütü AI HAT+ tahmininin tam altında: deneme
gerçekten ayırt edici. Ölçüm yöntemi bulgu 7. b'nin kablo etkisi doğru.

## Madde 5 · Ses bölücüsü

Bulgu 8. "Masa denemesinde ayarlanır" ifadesi R:164-165'te var ve doğru sınıf. Önerim: başlangıç değeri 10 kΩ / 2,2 kΩ (sette olan), son
değer KT2'deki ölçümle.

## Madde 6 · K14 fiş geçişi

**CAD'den okunan geçiş (yukarıdan aşağı; `kafa7_parcalar.py`, `kablo_yolu_ekran.py:34-39`):**

| Geçiş | Ölçü | Kaynak |
|---|---|---|
| Tabla kablo geçişi | 13 × 24 mm, R4 | `kafa7_parcalar.py:349` |
| Eğme çatalı deliği / boyun mili | Ø28 / Ø32 | `:267`, `:239` |
| Mil arka penceresi | altta 20 geniş × 5, üstte 45° ile 10'a daralır (10 yüksek), duvar 4 mm | `:243-244` |
| Kablo odası | halka, r < 27,5 | `:170` |
| Servo yuvası arka kanalı | **20 × 7,8 mm kapalı tünel**, ≈ 34 mm boy (y 6–40); arka duvarı 3 mm; üstte 20 × 12,6'ya açılır | `:143-145` |
| Alt çıkış | arka duvarda 20 × 12 pencere (üstü 45°), tünelin dibinde **90° dönüş** | `:147-148` |

**Kanal yandan açık değil** (servo yuvası tek baskı parçası, kanal içinde kapalı bir boşluk); CAD'de bunun bir seçeneği de yok. Fiş iki yerde
**dik açı döner**: mil içinden pencereye, tünelden alt çıkışa. Bu yüzden yalnız kesit değil fiş boyu da önemli; kumpas ölçüsü tek başına
yetmez.

**Fişler (tipik ürün ölçüleri; standart yalnız metal kılıfı belirler, kalıp gövdesi ürüne göre değişir, ölçülmedi):**

| Fiş | Metal kılıf (standart) | Tipik kalıp gövdesi | 20 × 7,8 tünel (boşken / HDMI Ø6 yanındayken 14 × 7,8) | Mil penceresi |
|---|---|---|---|---|
| micro HDMI (Pi ucu) | 6,4 × 2,3 | ≈ 10–12 × 5–8 | ince kalıplıysa geçer; ≥ 7,5 mm kalınsa geçmez | geçer |
| HDMI A (ekran ucu) | 14 × 4,5 | ≈ 20–22 × 9–11 | geçmez (gövdede kalır, R'nin yazdığı gibi) | – |
| USB-A erkek (USB 2.0) | 12 × 4,5 | ≈ 14–16 × 7–8; ince ürünler ≈ 12–13 × 6 | yalnız ince ürün, boş tünelde | 16 × 8 sığmaz, 13 × 6,5 sığar |
| USB-A erkek (USB 3.0, MJ:137) | 12 × 4,5 | ≈ 16–18 × 8–9 | **geçmez** | sığmaz |
| USB-A dişi (uzatmanın öbür ucu) | 13,1 × 5,7 | ≈ 18–20 × 10–11 | geçmez | sığmaz |
| 3 pinli servo fişi | – | ≈ 8 × 4 × 14 | geçer | geçer |

**Sonuç:**
- HDMI: R'nin yolu (micro HDMI ucu aşağıdan yukarı, A ucu gövdede) doğru. Şart "micro HDMI kalıp gövdesi ≤ 7 mm kalın, ≤ 18 mm geniş" yeterli.
  Ek olarak **boy ≲ 30 mm** (iki dik dönüş) gerekir; en iyisi baskı parçalarıyla elde denemek.
- Hub uzatması: MJ:137 bir **USB 3.0** uzatma. İki ucu da tünelden geçmeyecek kalınlıkta olması çok olası. Kablosu da Ø4 değil ≈ Ø5–5,5
  (9 damar): demet ≈ 77 mm², servo kanalı ≈ %49 (+ olası reset çifti ≈ %51). Hub USB 2.0 (EL:36), USB 3.0 gereksiz.
- **Kararı durdurmuyor; "alınacak kablo şartı + tanımlı yedek yol" olarak gider:**
  1. Hub uzatması **USB 2.0**, erkek ucu kalıp gövdesi **≤ 13 × 7 mm** (teslimde ölçülür). Erkek uç aşağıdan yukarı, HDMI'den **önce**
     (tünel boşken) geçirilir.
  2. **Yedek (her durumda çalışır, CAD değişmez):** fiş geçmiyorsa kablo fişsiz geçirilir ve yeniden sonlandırılır. USB 2.0'da dört damar:
     kesip lehim + makaron ya da lehimli / sıkmalı USB-A fiş; D+ / D− bükümü ≤ 1 cm açılır. HDMI için yedek **şerit (FPC) HDMI + takılır uç
     adaptörleri**: kafa ekranında zaten bu düzen var (EL:57). Şerit düz geçer, adaptörler sonra takılır. 1 m şeritte 1080p'yi KT4'ün masa
     denemesi gösterir.
  3. CAD değişikliği (tüneli arkadan oluk olarak açmak) önerilmez: mil penceresi USB-A fişini yine geçirmez, baskı parçası değişir.
  4. KT4'e: "kablolar alınmadan önce baskı parçalarında (servo yuvası, mil) fişlerin elle geçirilmesi" eklenir. R:129-130'daki "ayrı karar"
     yerine yukarıdaki yedek yazılır. MJ:137 ve MJ:191 notlarına şart.

## Madde 7 · İlk kontrolün bulguları

| Bulgu | Durum |
|---|---|
| D1 K10 payı | **Kapandı** (R §2 tablo, EL:52-54, KK K10). Küçük eskime: bulgu 7 |
| D2 K11 sigorta yeri | **Kapandı** (F6). Ortak giriş varsayımına bağlı: bulgu 5 |
| D3 BC337 + 1 kΩ | **Kapandı** (270 Ω). Yeni: D1 (4,7 kΩ → 2,2 kΩ), bulgu 2–4 |
| 1 jak kılıfı | Kapandı (KT2 adım 1) |
| 2 ses seviyesi | Kapandı (bölücü); 2,7 kΩ sette yok, bulgu 8 |
| 3 "masa denemesine bağlı" | Kapandı (R, EL:28, KK kayıt); uzatmanın yeniden alımı R:171'de yazılı |
| 4 K16 kaydı | Kapandı (KK K16 notu, EL:145). Özet tablo KK:31 C adımında |
| 5 K14 HDMI çapı / fiş | Kısmen: şart yazıldı; fiş geçişi bulgu 1 / Madde 6 |
| 6 reset / demet | Kapandı (R §7, KT6, demet Efe'nin cevabından önce bağlanmaz) |
| 7 hub F4 senaryosu | Kapandı (R §6, EL:88, KT5) |
| 8 taslak "kapattık" | Kapandı; yeni eksik bulgu 9 |
| 9 servo kondansatörü | Kapandı (EL açık iş 12, R §12) |
| 10 62 kablo dökümü | Açık iş olarak kayıtlı (R §11) |

## Madde 8 · Tutarlılık, farklar, gizlilik ve C listesi

- R = EL = KK = G: K1, K10, K11, K14, ses, hub, reset aynı şeyi söylüyor. Röle sürücüsü dört yerde aynı (D1 düzeltmesi dördüne de girecek).
- EL farkı yalnız bu kararların ve sürücünün gerektirdiği satırlarda; satır sayısı 522 → 522 (`git show HEAD:` ile sayıldı). Pin tablosu
  (EL:472-492) yalnız 4 ve 19'un not / işlev sütununda değişti. PH 435 → 462 satır.
- KK farkı (`b1c2a8d`'ye göre): K10, K11, K14 Durum, K16 notu, K58 tek satır, "yeni sorular" kaydı. K56, K57, P10.5b'ye dokunulmamış.
  `b1c2a8d`'nin commit mesajı da kuyruktaki ara durumu belirtiyor.
- Gizlilik: R, G, PH / EL / KK / `pin-karari-gunluk.md` farkı ve taslakta yerel yol, makine adı, takma ad, e-posta, parola / anahtar, ağ adı
  yok (tarandı; "Echo" yalnız AEC alıntısında ve sonar "echo"da).

**C adımında düzeltilecek satırlar (kuyruk ve bağlı belgeler; commit edilmiş eski satırlar çalışma ağacında zaten yeni):**
1. KK özet tablosu: :16 (K1), :25 (K10 "masa denemesine bağlı"), :26 (K11), :29 (K14), :31 (K16 "14.11: ses yolu değişti" notu); sayım :75.
2. KK K58: :1121 ("gate pull-down 4,7 kΩ, mantık seviyeli röle MOSFET'i" → BC337-40, D1 düzeltmesiyle taban değeri), :1127 ("MOSFET satıcı /
   stok" → BC337-40 satıcısı belli), :1215-1216 ("IRLZ44N → AO3400A ×2 + SOT-23 adaptör" iş maddesi → BC337-40 ×3, adaptör yok).
3. KK K52 (:67, :924-946): "mini 2 A ve hat sigortası yuvası" → regülatör + kutunun F6 3 A yuvası; hat yuvası yok. K11 notu :299 tarihçe
   olarak kalabilir.
4. MJ: :106 (BC337-40 ×3, "yalnız -40"), :115 notu (taban 270 Ω + 2,2 kΩ; ses 10 kΩ + 2,2 kΩ ya da ölçüme göre), :122 adet 5 → 4,
   :123 2 A mini → **2 A standart**, **+5 A standart**, **+3 A standart** (bulgu 6), :137 USB 2.0 ve fiş şartı (Madde 6), :191 fiş şartı.
5. EL: D1 düzeltmesinin satırları (D1'de liste), :29 / :278 / :511 "tepe hesaplanmadı", :446 JQC-3FF, :461 F6 dalı, Sigorta listesine
   "ayrı girişli kutu" kuralı (bulgu 5).
6. R §9 / §13 KT4 / KT7 ve PH T2 (D1 ve bulgu 1–4); R §16 ve G §6.1'e `pin-karari-gunluk.md`.
7. Pano taslağı madde 5'e T2 yöntemi ve sürüş gücü notu (bulgu 9).

## Doğruladıklarım

- BC337-40 veri sayfası değerleri PH'deki BJT satırıyla aynı (hFE 250 / 400 / 630, BC338-40 170 @ 300 mA, VCE(sat) 0,7 V @ 500 / 50 mA,
  VBE 1,2 V @ 300 mA, VEBO 5 V, Ptot 625 mW, RθJA 200 °C/W).
- PH'nin taban akımı, GPIO akımı, boşta taban gerilimi ve sızıntı modeli hesapları (kendi betiğimle aynı sonuç; fark yalnız bobin akımı ve ölçüt).
- 270 Ω, 220 Ω, 2,2 kΩ, 4,7 kΩ, 10 kΩ, 1 kΩ, 5,1 kΩ, 6,8 kΩ direnç setinde (satıcı sayfası); 2,7 kΩ yok.
- K10 bütçesi kalem kalem; K11 akımları; F6'nın konumu ve 6. yuvanın boşluğu; ana anahtar kapalıyken kesilme.
- Sigorta kutusunun satıcı sayfası: 6 kanal, 0–32 V, 115 × 53 × 42 mm, delik arası 103 mm, setteki sigortalar EL:374 ile aynı.
- Boyun kesitleri CAD kaynağıyla aynı (20 × 7,8 = 156, pencere 175, alt çıkış 204 mm²); kanal kapalı.
- Pin tablosu, JSON ve EL pin planında pin numaraları ve işlevler değişmemiş (diff satır satır okundu; betik koşulmadı).

## Bakamadıklarım

- MAH-112-C-4'ün kendi veri sayfası (indirilemedi; MAH3 kardeşi ve satıcının "1,7 W" bilgisi kullanıldı). JQC-3FF için satıcıdaki Qianji
  ürününün kendi sayfası (Hongfa tabanlı tablolar ve satıcı özetleri kullanıldı; 0,45 W / 320 Ω türüyse bırakma akımı sınırı 3,75 mA).
- BC337-40'ın 1 mA'deki VBE'si ve 170–210 mA'deki VCE(sat)'ı (veri sayfasında sayı yok; yalnız eğri). Satıcıdaki BC337-40TA'nın üreticisi
  ve ayak sırası; Direnc.net fiyatı yeniden okunmadı.
- Sigorta kutusunun ortak girişli olup olmadığı (sayfada yok; fotoğraf okunmadı).
- Fiş ölçüleri: MJ:137 ve MJ:191 ürünlerinin kalıp gövdeleri (sayfalarda yok); tablo tipik ürün ölçüsüdür. Dik dönüşlerde geçebilecek en
  uzun fiş boyu hesaplanmadı, elde deneme önerildi.
- PAM8403 modülünün giriş devresi (seri direnç / potansiyometre / kondansatör değeri); ReSpeaker çıkış seviyesi.
- Pano #8 #24'ün sunucudaki hâli (yalnız depo dışındaki gönderim kopyası okundu; `oku` komutu "okundu" yazdığı için kullanılmadı).
