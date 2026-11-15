**KAYNAK GEÇER** (üretimden önce düzelmesi zorunlu bulgu yok; aşağıda kayıtlı açık işler ve orkestratör kararları var)

# P10.7b2a ikinci bağımsız kontrol

- Kapsam: `lale-duzeltme`, HEAD `1328b60`, çalışma ağacındaki commit edilmemiş değişiklikler (ilk kontrol `F10i-kontrol.md`,
  düzeltme turu 1 `F10i-gunluk.md` "Düzeltme turu 1").
- Rapor saati: 2026-11-15 02:58 (sistem saati).
- Yöntem: gerçek depoda yalnız okuma ve brief'te izin verilen koşular; bütün bozmalar depo dışındaki geçici bir kopyada
  (planlama, rehber, tasarim/freecad, raporlar ve `origin/main`'den bayt bayt alınan `kanallar.yaml`).
  Bozma sürücüsü her bozmadan sonra dosyayı geri yazdı. Depoda yazılan tek dosya bu rapor.

## 1. Üretimden önce düzelmesi gerekenler

Yok. Mevcut metinde ve kayıtta montajda zarar verecek bir yanlış ya da eksik talimat bulmadım. Kayıtta yanlış değer, üretimi
kıracak kod hatası ya da gizlilik sorunu da yok. Güvenlik denetimlerinde bulduğum delikler (§4) onay kaydı kapısına takılıyor:
her metin değişikliği insan onayına geliyor. Bu yüzden onları "dişsiz" saymadım, açık iş ve karar konusu yaptım. Tek istisna B27
(§4): ona hiçbir kapı takılmıyor; orkestratör kararı.

## 2. Ü1–Ü7 ve öbür bulgular

| Bulgu | Durum | Nasıl ölçüldü |
| --- | --- | --- |
| Ü1 G22 uçları | Kapandı | Kayıtta damarlar ters çevrildi (B05): `ag` ve `donus` GEÇMEZ. Metinde elle ters (R9): satır bölünmesinden kopyada uygulanamadı, ajanın kendi bozması bunu kapsıyor ve yakalanıyor |
| Ü2 X01 beslemesi | Kapandı | Kayıtta VIN (B04): `ag` GEÇMEZ. Metinde "5V pinine" (R8) ve kontrolde öter ↔ ötmez (B25) yakalandı |
| Ü3 P03 köprüsü | Kapandı | "3 telli hazır kablo kullanabilirsin" (R10) yakalandı |
| Ü4 kablo talimat tamlığı | Kısmen | R1, B01–B03 yakalandı, ama gevşetilmiş ok kuralı AU3 ve H02'yi bir liste cümlesiyle geçiriyor (§3) |
| Ü5 K1 30 / 87 | Kapandı | Kayıtta K1 çıkışı NC (B07): GÜVENLİK. 30 ↔ 87 (B26): GÜVENLİK, uç–damar tutarlılığından; makul. Ajanın `elektrik.md:441` atfını reddi **haklı**: o satırda 30 / 87 numarası yok |
| Ü6 kutup ve kondansatör yönü | Kapandı | R2, R3 yakalandı. Yer tutucu kalıp yanına çelişen cümle eklenince (B09, B10) yalnız onay kaydı yakalıyor (§4) |
| Ü7 vurgu tonu okuyucusu | Kapandı | F10e `VURGU_TON`'u okuyor, bulamazsa hata veriyor. Ton ölçüsü `gecti`'ye girmiyor (ölçüm amaçlı). F10a ana ve kopya tonları iki temanın listesinden kabul ediyor, tema eşleşmesini denetlemiyor (§6) |
| A2 satır gönderimi | Kapandı | Ajanın düzeltmesi makul; ret haklı |
| A4 çıplak değer | Kısmen | R6 "4,23 V" yakalandı. **R5 kaçtı:** `rehber_metin.py` K1 `is_` içinde "100 kΩ'a yakın okunur" yakalanmıyor, çünkü "akü" bağlam sözcüğü `CIPLAK_KURAL`'ın (`rehber_denetim.py:1108–1121`) 40 karakterlik penceresinin dışında. B13 "100k" ve B14 "4,2 volt" de yalnız onay kaydına ve ASCII sözlüğüne takılıyor |
| A5 mantar "aynı klemens" | Kapandı | R7 yakalandı. Sözcük değişince (B16) kaçıyor (§4) |
| A7 A06 − ucu | Kapandı | R4 "sonra bağla" yakalandı |

## 3. Gevşetilmiş ok kuralı ve geçirdiği 15 kablo

Ok kuralının geçirdiği 15 kablo: A03, A04, A05, AU3, B01, B02, G01, G02, G05, G08, G09, H02, I01, I02, K03. Bunlara tek tek
baktım. Çoğu anlaşılır bir "kaynak → hedef" bağlama şeması. İki istisna var:

- **AU3 (kayıtlı açık iş, öne çıkar):** Yalnız K2 madde 5'teki "Boyun demeti, 5 kablo" liste cümlesinde geçiyor. PAM8403 L+ / L−
  ucuna lehim talimatı hiçbir adımda yok. Hoparlör ucu F2'de, kimliksiz anılıyor. PAM8403 BTL çıkışlı ve kısa devre korumalı;
  zarar olası değil, hoparlör sessiz kalır.
  - Ölçüm: çözülmüş metinde AU3 kimliği ve "L+" / "L−" araması, `talimat_kablolari` çıktısı.
  - Öneri: F2'ye "AU3'ün iki damarını PAM8403'ün L+ / L− çıkışına lehimle (AU3)" cümlesi. Ok kuralı liste cümlesini ("N kablo"
    kalıbı) talimat saymamalı.
- **H02:** Aynı liste cümlesiyle geçiyor. Gerçek talimatı F3'te ama kimliksiz ("HDMI ve 12 V uçlarını ... tak"). Öneri: F3
  cümlesine "(H02)" eklensin.

Bu iki durum Ü4 sınıfının bir kısmını yeniden açıyor. Montajda zarar yok.

## 4. Denetimlerin dişi: kendi bozmalarım (B01–B27, R1–R10)

Gerçek depoda ajanın bozmaları tam yakalanıyor: `kablolar_denetim` 164 / 164, `rehber_denetim` 160 / 160, `rehber_kablo` 36 / 36.
Ben 37 bozma yazdım (B01–B27, R1–R10). Uygulanamayan 1 (R9; ajanınki kapsıyor).

**Anlamsal denetimin yakaladıkları (9 + R'ler):**

- B04 X01 VIN (`ag`), B05 G22 damarları ters (`ag`, `donus`), B06 K2 G10 NC'de (`yon_yer`), B07 K1 çıkış NC (GÜVENLİK).
- B11 hat-G22 yeri "PC817 modülü ucunda", B17 F1 teyit ibaresi silindi (teyit), B21 G22 3. saplamada, 5 pabuç (`kesit`).
- B22 P6KE18A yönü ters (ZORUNLU ve `yon_yer`), B25 X01 kontrolü ters, B26 K1 30 ↔ 87 (GÜVENLİK).
- R1–R4, R6–R8, R10.

**Yalnız onay kaydının yakaladıkları (17):**

Bunlar `kritik_fark` kapısına takılıyor. Bazılarına ASCII sözlüğü de tesadüfen takılıyor, çünkü "dinlenmede", "volt", "noktada",
"pabuca", "Gerekirse" gibi sözlük dışı ama doğru Türkçe sözcükler içeriyorlar.

- B01, B02, B03 (tamlık, ok ve ertele kalıpları), B08 G09 "dinlenmede kapalı ucuna", B09, B10 (yer tutucu yanında çelişen cümle).
- B12 hat-G22 yeri (yalnız `gorunum` farkı), B13, B14, B15 (çıplak değer), B19 PCA9685 V+ klemensine XL4016 A, B20 X01 VIN.
- B24 G07 giriş saplamasına.
- **B16 (öne çıkar):** F1'de "A01'i ve A02'yi tek pabuca sıkıp NC girişine tak". Mantar köprülenir, acil stop delinir.
  - F1'de mantarın giriş ve çıkış bağlantısını koruyan pozitif ZORUNLU yok. YASAK yalnız "aynı klemens" kalıbını arıyor
    (`rehber_denetim.py:421–459`).
  - Öneri: ZORUNLU_CUMLE'ye F1 için "A01 … NC girişine" ve "A02 … NC çıkışına" eklensin.
- **B18 (öne çıkar):** A06'nın + ucu "sigorta kutusunun F5 girişinde". PC817 #1 mantarı algılamaz; mantar bırakılınca röle komutsuz
  yeniden çekebilir. Öneri: A06'nın kaynak düğümü ("acil stop düğüm kartı") ZORUNLU_CUMLE'ye girsin.
- **B23 (öne çıkar):** K2 pim bakışında "COM ile NO arası öter" (ters). Kullanıcıyı G10'u NC'ye lehimlemeye götürür; ön şarj
  baypas edilir ya da hiç kapanmaz. Öneri: K2 pim cümlesi için ZORUNLU (beklenen okuma sırası).

**Hiçbir şeyin yakalamadığı (1, orkestratör kararı):**

- **B27:** `elektrik.md` bölücü tablosunda 18 kΩ → 33 kΩ.
  - Değer yer tutucudan çözüldüğü için onay kaydı bile görmüyor. Rehber 3,18–3,57 V'u "beklenen" diye basar.
  - ESP32 ADC 11 dB doğrusal sınırı yaklaşık 2,45 V; bölücü çıkışı 3,3 V'u da aşar.
  - Öneri: `kablolar_denetim` ya da `rehber_deger` içinde "akü üst sınırı × oran ≤ 2,45 V" sınaması, ya da bölücü oranının
    onay kaydına kablo değeri olarak girmesi.
  - Montajda zarar ancak bu dosya yanlış düzenlenirse doğar; bugünkü değer doğru.

## 5. Yeni talimatların elektriksel doğruluğu

- **G22:** + damar → IN2 +, IN2 − → yıldız barası 5. saplama. Ters bağlama uyarısı ve süreklilik kontrolü doğru ve ayırt edici.
  Koruyucu anahtarlı bara ucunda. Doğru.
- **X01:** PC817 çıkış VCC → ESP32 3V3; "≤ 3,6 V" `pin-haritasi.md:296` D3 ile uyumlu. Doğru.
  - Açık iş (önceden de vardı): modülün yüksek / düşük seviye jumper'ı (`elektrik.md:241`) rehberde yok. Öneri: B6a'ya
    "jumper'ı … konumuna al" cümlesi.
- **P01–P03:** Servo beslemesi SV1–SV3 → dağıtım kartları → uzatmalar (K2) yolundan geliyor. PCA9685 V+ klemensi boş; servo
  beslemesiz kalmıyor. Doğru.
  - Açık iş: V+ süreklilik ölçümü PCA'nın V+ klemensinde yapılıyor. Adafruit tipi kartlarda klemens ile ray arasında ters kutup
    FET'i olabilir; ölçüm kanal başlığının V+ pininde daha sağlam.
  - Açık iş: kayıttaki P03 sonlandırması hâlâ "3 pinli köprü" diyor (`kablolar.json` P03 `not`). Metinle tutarsız ama zararsız.
- **G07:** Oran 18 / 118 = 0,1525. 12,8 V → 1,95 V; 14,4 V → 2,20 V; 14,6 V → 2,23 V. Hepsi 2,45 V altında. Makaron sırası ve
  gerginlik giderme var. Doğru.
  - Açık iş: yalıtımlı kırmızı pabucun kovanına lehim PVC'yi eritebilir. Öneri: yalıtımsız pabuç ya da lehimden sonra makaron.
  - Açık iş: aralığın altında okuma için talimat yok. Öneri: "akünün kendi gerilimini de ölç, oranla karşılaştır".
  - Kırılgan bağ: `v.aku_aralik` dizgesi `elektrik.md:67`'deki göğüs regülatörü bağlamından alınıyor. Bugün doğru, satır
    değişirse sessizce kayar.
- **K1 madde 3 (K2 pim bakışı):** Lehimden önce, akü ayrıkken yapılıyor; iki yanlış yönü de ayırt ediyor. Doğru. Dişi için B23'e bak.
- **TVS (E3a):** Yön ve "CA ya da bantsız takma" kuralı doğru.
  - Açık iş: "P6KE…A (sonu A) tek yönlü" ifadesi muğlak. CA da A ile biter; A soneki aslında %5 toleransı gösterir. Öneri:
    "…CA değil, …A".

**Onay kaydı farkı:** 84 fark (57 eklendi, 27 değişti; metin 47, liste 34, kablo 3). Değişen 27'nin karakter farkını tek tek okudum.

- İstenmeyen kritik değer değişimi yok.
- Silinen tek uyarı F1'deki "0 V ise … kopmuş" cümlesi; yerini "Hiç gerilim okunmuyorsa" aldı, anlam korunuyor.
- K52, K60 ve K61 hâlâ "karar bekliyor" (ZORUNLU geçiyor; bilinen durum).

**Devre değerleri:** `1328b60` ile karşılaştırıldı. Uçlar, koruma, kesit, damarlar, besleme zinciri ve koruyucu akımları aynı.
Durum sayıları 20 / 53 / 1. Yalnız rehber adım türünde "öneri → bugün" değişiklikleri var.

## 6. Renk (kendi WCAG ve CIEDE2000 hesabım; sistemin değerleriyle aynı)

| Ton | Sahneye | Lejanta | En yakın (ΔE00) |
| --- | --- | --- | --- |
| Açık ana #e014ff | 3,06 | 3,68 | lazer 16,6, EV_RENK 17,4 |
| Açık kopya #f3b8ff | 1,33 | 1,60 | ref 22,2 |
| Koyu ana #00ffee | 13,41 | 12,55 | profil 24,3 |
| Koyu kopya #9ffff6 | — | — | koyu ana 8,2; beyaz 20,6 |

- CAD gerçek renklerine (varsayılan "gerçek" kipi) en az ΔE00 19,1. Bu sınama `rehber_kablo.py`'de yok.
- Açık ana 3,06 ile eşiğin (3,0) hemen üstünde. Düz renkte ölçülüyor; ışıklandırma ve emissive ile sapabilir. Üretimde F10e'nin
  ölçümüne bakılmalı.
- Kopya tonlarına karşıtlık sınaması yok; ana ↔ kopya ayrımı sınanmıyor (koyu 8,2). Açık iş.

## 7. Doğrulayıcılar ve sayım betiği

- **F10e** (`planlama/d158/F10e-dogrula.py:102–121`, `329–343`): `VURGU_TON`'u okuyor, bulamazsa hata. Karşıtlık ölçüsü
  `gecti`'nin dışında; ölçüm de76 ile yapılıyor, de00 ile değil. Açık iş.
- **F10a** (`planlama/d158/F10a-dogrula.py:228–258`): ana ve kopya tonları iki temanın birleşik listesinden kabul ediliyor; hangi
  temada olduğu denetlenmiyor. Hafif gevşeme. Açık iş.
- **F10i-yerlesim-say.py:** Okudum, yöntem doğru. Kendi bağımsız sayımım da 14840 / 27000 verdi. En kötü köprü akımı her
  yerleşimde 20 A. Açık iş: `kablolar.json` anahtarlı bara gerekçesi hâlâ "sayım: F10i-gunluk.md" diyor; betiğe işaret etmeli.

## 8. Koşular (gerçek depoda; hepsi çıkış 0)

| Koşu | Sonuç |
| --- | --- |
| `kablolar_uret.py --kontrol` | güncel, 0 |
| `kablolar_denetim.py` | GEÇER, bozma 164 / 164, 0 |
| `rehber_denetim.py --kaynak` | tamlık eksik 0, teyit 0, bozma 160 / 160, 0 |
| `rehber_kablo.py` | GEÇER, bozma 36 / 36, 0 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ, 38 bölüm, 0 |
| `F10i-yerlesim-say.py` | 14840 / 27000, 0 |
| `py_compile` (değişen ve yeni 9 .py) | hepsi OK, 0 |
| `node --check rehber/app.js` | 0 |

Koşulardan sonra `git status` değişmedi. Bellek koşu boyunca 1,2 GB'ın üstünde kaldı (son ölçüm 4,8 GB).

## 9. Sınırlar ve gizlilik

- Korunan yollarda fark yok: `kod/`, `pin-haritasi.md`, `elektrik.md`, `maliyet.json`, `rehber/veri`, `rehber/goruntu`,
  `planlama/rehber`.
- PNG'ler ve `yerlesim-kontrol.json` bu paketten önceki tarihli. `F10i-kontrol.md` ilk kontrolden sonra değişmemiş görünüyor.
- Kökte artık dosya yok. Yok sayılan listede paketten kalan dosya yok.
- Gizlilik: `1328b60`'a göre eklenen 3360 satır ile `F10i-gunluk.md` ve `F10i-yerlesim-say.py` tarandı. Aranan: yerel yol, makine
  adı, takma ad, e-posta, parola / anahtar. Temiz.
  - Tek eşleşme "Echo"; HC-SR04 pin adı, takma ad değil.
  - "Ahmet" ve "Efe" ikişer kez, izin verilen roller olarak geçiyor.

## 10. Üretim adımı

- **Açık iş:** `F10i-gunluk.md:462` §10 hâlâ "açık temada seçili parça menekşe" diyor. Düzeltme turundan sonra ton fuşya
  (#e014ff). Öneri: §10 güncellensin; üretimde göze bakan yanlış tonu arar.
- **Beklenen kırılmalar ve bakılacaklar:**
  - `rehber_kablo.py --veri` veri yeniden üretilmeden "tema tonu" farkı verir (günlük bunu biliyor).
  - F10e ton ölçüsü `gecti`'nin dışında. Üretimde 3,06 payı bu ölçüyle elle okunmalı.
  - PDF sayfa sayısı metin uzadığı için 77'yi aşabilir.
  - Parça 1192, şema 49, alt adım 71 değişmemeli.

## 11. Orkestratörün karar vermesi gerekenler

1. B16, B18, B23: acil stop, PC817 algısı ve K2 pim okumasını koruyan pozitif ZORUNLU_CUMLE'ler bu pakette mi eklensin, yoksa açık
   işte mi kalsın? Bugün yalnız onay kaydı ve insan gözü koruyor.
2. B27: bölücü oranı için ADC sınırı sınaması (hiçbir kapı yok).
3. AU3 talimatı ve ok kuralının liste cümlesini geçirmesi (Ü4'ün kalıntısı).
4. R5 çıplak "100 kΩ" kaçağı: bağlam penceresi genişlesin mi?

## 12. Bakılmadı

- FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları ve başsız tarayıcı (brief gereği koşulmadı). Render edilmiş renk ve kare içeriği
  bakılmadı.
- TVS, kondansatör ve JQC-3FF veri sayfaları: satın alınan parçanın üreticisi bilinmiyor; web'den bakılmadı.
- PDF sayfa sayısı.
