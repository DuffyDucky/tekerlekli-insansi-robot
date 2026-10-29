# Y2a — 1,65 m taslağını ana tasarıma taşıma (CAD tasarım ajanı günlüğü)

Görev (orkestratör, 26 Ekim 2026; 29 Ekim'de boy 1,65 m oldu): `tasarim/freecad/taslak-170/` varyantındaki 1,70 m geometrisini modüllere (`arayuz.py`, `iskelet/
kabuk/ omuz/ dirsek/ kafa/ taban/`) ve ana montaja (`montaj/`) işlemek; ek kararlar: göğüs Nextion kaldırılır, taban 520 + akü 75 mm öne,
gövde direği 1.235,5 mm (1,65 m'de **1.185,5 mm**) tek parça 2 m stoktan, S1 kaseti KZ1 / KZ2 + `S1-kaset.md` belge düzeltmeleri. Commit/push yok.
Bu dosya kesintide kaldığı yerden devam için: her alt iş bitince buraya yazılır. **Önce bu günlüğü oku, yapılanı tekrarlama.**

## Plan (sıra)
| # | İş | Durum |
|---|---|---|
| 0 | Okuma + taslak referans dökümü (modüllere dokunmadan önce; 444 ve 520) | ✅ |
| 1 | `arayuz.py` (29 Ekim: BOY 1650, S3 1340, UZAMA 385): boy 1700, S3 1390, gövde kesiti uzatma bandı, dikişler, braketler, Nextion kaldır, taban 520 (ETEK_A), DIRSEK (tüp 130, ön kol +32,4, el +19, çatal 8), KAFA (10", tilt ekseni), KZ1, KZ2, stok 2 m | ✅ |
| 2 | iskelet: direk 1.185,5 (1650; 1700de 1.235,5) (2 m stok kesim planı) → `iskelet_montaj.py` | ✅ |
| 3 | kabuk (1650'de koştu, geçti): 6 gövde bandı (2 uzatma), Nextion + pencere + konnektör bölgesi yok, etek 520 (orta dolgu şeridi), braketler, KZ1 → `kabuk_montaj.py` | ✅ |
| 4 | omuz: tüp 130, DS3235 adı, KZ2 → `omuz_montaj.py` | ✅ |
| 5 | dirsek: tüp ucu −170, ön kol +32,4, el yakası +19, çatal dış kol 8 + M3x12 + 2 pul + 45° destek, kablo yolu → `dirsek_montaj.py` | ✅ |
| 6 | kafa: 10" kafa (kafa10) + boyun adaptörü modüle → `kafa_montaj.py` | ✅ |
| 7 | taban: 520 (tahrik + plaka yanlara, braket M4 → DIN 985), akü yerleşimi → `taban_montaj.py` | ✅ |
| 8 | ana montaj: `ana_montaj.py` (+ kısa yerleşim: ev pozu S2 5°, kol kaba, kafa süpürmesi), taslakla parça parça fark tablosu | ✅ |
| 9 | README (taslak arşiv notu), S1-kaset.md düzeltmeleri, rapor | ✅ |

## Günlük
- 2026-10-26: başladı. Okundu: CLAUDE.md, dongu.md, freecad README/OZET, arayuz, taslak_ayar/parcalar, kafa10, KOL125/CATAL notları
  (+ kontrol notları), K3 raporu, moduller.py, ana_montaj.py, iskelet/omuz/dirsek/kabuk/taban parçaları. Çalışma ağacı temiz (HEAD 6594c63).
- Taslak referans dökümü (scratch `taslak_dok.py` → `taslak444.json`, `taslak520.json`): modüller değişmeden önce koşturuldu.
- Döküm sonucu: taslak 520 → 1.076 parça, 25.027,2 g, AM (−0,20; 558,45; −10,50); taslak 444 → 1.064 parça, 24.511,3 g (= kutle.json).
  Kafa dengesi dy −13,255, zb −89,893 (tilt ekseni kafa yereli y 188,255; adaptör 58,255).
- **1 arayuz.py (bitti):** BOY 1700, HEAD_UP 290, S3 1390, UZAMA 435; GOVDE_KESIT uzatma (476,5…911,5 sabit kesit = 125 cm loft'unun
  476,5 kesiti a 125 / bf 85 / bb 85 / r 38; taslakta 488,5 kesiti → 0,7 mm basamak yoktu artık), GOVDE_DIKIS 476,5/694/911,5/1125/1318,
  ARKA_KAPAK +435, KABUK_GOVDE_BRAKET y 400/560,25/777,75/1215; NEXTION + konnektör bölgesi + ekran_noktasi silindi (GOGUS_* yalnız
  eğik duvar biçimi); TABAN_W 520, TABAN_DX 38 (bölüm 1'de), ETEK_A 260, etek üst kesiti a 188, ETEK_DIKIS_X ±38, ETEK_ACIKLIK
  genişletilmedi (taslakta 276 × 140 olup gövdenin yanında 26 mm boşluk açıyordu), ACIL_STOP / ana anahtar ±38, etek braketi x_ic 252,
  taban bölgeleri _X_BR 171 / _X_WH 216; TABAN plaka x 173, braket cıvatası x 153 (plakaya DIN 985); OMUZ servo DS3235 (+ kod,
  kütle, stall 30,4); DIRSEK tüp ucu −170, eksen −203, eksen_x 156…227,9, bilek −318,5, el ucu −406,9, tup/on_kol/el uzama, çatal 8 +
  M3x12 + 2 pul; KAFA yeni (KAFA7 = eski ölçüler, KAFA_EKRAN10, denge dy/zb sabit, tilt (26,9; 188,255; 25), ±15, adaptor_h 58,255);
  KAFA_KOL_YASAK aktif=False (125 cm ölçümü tilt 25…30 yeni ±15 aralığın dışında); KOL_KABLO dirsek/çatal noktaları −30, bilek
  servo noktaları −62,4, bilek_ek (lehim), govde_dikey ilk nokta S3 − 55; **KZ1** pim bosluk 1,0; **KZ2** ip delik_eksenel 0,8;
  DIREK_STOK 2000; YAZICI_OKUL 250³. `kod/ortak/eklem_sinirlari_uret.py` kontrolüne "aktif=False" koruması (2 satır).
- **Akü 75 mm öne: GEOMETRİK OLARAK UYGULANAMAZ** (arayuz TABAN notu). Akü (181 × 77 × 167, yatık) orta ara ray (z −20…20,
  y 94,5…134,5) ile arka ara ray arasındaki bölmede; 75 mm önde ön yüzü z +37: orta ara ray, direk dibi köşe bağlantıları
  (y 134,5…171,5) ve gövde direği akünün içinde kalır. Kutuplar ön yüzde 9 mm çıkıntılı, takoz aralığından kablolanıyor. Akü yerinde
  bırakıldı (aku_one_uygulanan_mm 0); seçenekler rapora (a: orta ara rayı akünün üstüne yükseltilmiş travers + 2 dikme, direk ~80 mm
  kısalır; b: akü ön bölmeye (~+240 mm), elektronik arkaya; c: akü yerinde + yazılım ivme sınırı / balast).
- **2 iskelet (bitti):** kesim planı 2 m (direk + sol uzun ray + ön ara ray, artık 63,5) + 1 m (sağ uzun + travers + arka ara, 99) +
  1 m (orta ara, 805 yedek). `iskelet_montaj.py`: 59 parça, çakışma 0, bağlantı 12/12, bölge 0 ihlal, **6.646,1 g** (taslak 6.646,1),
  AM (0; 460,9; 0); eğilme direk 0,92 MPa / 0,398 mm (omuz ALT_KOL tahminiyle; Y4'te kol kütleleriyle).
- 2026-10-26 (limit öncesi, ek): **kabuk** (1700) koştu: 291 parça (25 baskı), kabuk içi çakışma 0, iskelet 0, bölge 0, braket 14/14, M6 pay
  1,10/0,80, bindirme cıvatası 79/79, tüm baskı parçaları X2D'ye sığıyor, desteksiz; 6.205,5 g. **omuz** koştu: 75 parça, S2 5 statik 0,
  Kol 159,0 g (taslak 159,0). **dirsek_parcalar** (sağ) taslak 520 dökümüyle 57/57 parça birebir (merkez < 0,01 mm, kütle < 0,01 g).
  Kafa: `kafa/kafa7_parcalar.py` (eski kafa_parcalar, KAFA7 ölçüleri), `kafa/kafa10_lib.py` (taslak kafa10), yeni `kafa/kafa_parcalar.py`
  (Govde/Pan + adaptör + 10" Bas; BAG yeniden eşlendi; saplama DIN 985'i +1 mm geçecek boyda — taslakta somuna 3 mm giriyordu).
  dirsek_montaj: horn cıvatası pul kontrolü, S1/S2 stall DS3235, kablo boyu bilek lehimli ek, y literalleri tüp ucuna bağlı.
- **2026-10-29 devam — BOY DEĞİŞİKLİĞİ (Duffy, 29 Ekim): 1650 mm.** `arayuz.BOY` tek parametre: S3 1340, UZAMA 385, direk 1.185,5
  (2 m stok), uzatma 2 bant × 192,5 (+12 dil = 204,5 ≤ 250; tek bant 397 sığmaz), dikişler 476,5 / 669 / 861,5 / 1075 / 1268, gövde
  braketleri 400 / 547,75 / 740,25 / 1165, arka kapak 885…1075, kafa tabanı 1360. Kabukta göğüs önü x0 cıvatası 1270 → 835 + UZAMA (gövde
  bandına bağlı). Yorumlarda "1,70 m" → "1,65 m". 1700 çıktıları (iskelet, kabuk, omuz) geçersiz → hepsi yeniden koşulacak.
  `eklem_sinirlari.json` üretildi (yasak kutu aktif=False, tilt ±15, DS3235 metni).
- **2026-10-29 02:12 (yeni ajan devraldı; önceki oturum temizlendi).** Okundu: brief, bu günlük, CLAUDE.md, dongu.md 1,70 m planı, arayuz.py
  (BOY 1650, S3 1340, UZAMA 385, DIREK_L 1.185,5). Çalışma ağacında önceki ajanın 27 dosyası duruyor (dokunulmadı, üzerine devam).
  Önceki ajan 29 Ekim 01:54–02:07'de iskelet, omuz, kabuk'u **1650 ile yeniden koşmuş** ama günlüğe yazamamış; çıktılar okundu:
  - iskelet (01:54): 59 parça, çakışma 0, bağlantı 12/12, bölge 0 ihlal (55 bölge), **6.548,1 g**, AM (0; 443,12; 0); kesim planı 2 m
    (direk 1.185,5 + sol uzun 500 + ön ara 190, artık 113,5) + 1 m (sağ uzun + travers + arka ara, 99) + 1 m (orta ara, 805);
    direk σ en kötü 0,93 MPa (o pozda sehim 0,336 mm; emniyet 118,8), **en büyük tepe sehimi 0,370 mm** (ızgara, iki kol S1 90 / S2 5;
    adlı poz "iki kol öne + 0,5 kg" 0,371) — `iskelet-analiz.json` `egilme.en_kotu`; Y2b düzeltmesi (omuz ALT_KOL tahmini, Y4'te gerçek kol kütlesiyle).
  - omuz (01:55): 75 parça, S2 5 statik 0 (S2 0'da tambur ↔ çatal/tüp, aralık dışı, bilinen), M6 pay 1,7 / 0,8, kütle Gövde 625,7 /
    Göbek 175,2 / Kol 159,0 g.
  - kabuk (02:07): 291 parça (25 baskı), kabuk içi çakışma 0, iskelet 0, bölge 0 ihlal (49), braket 14/14, M6 22/22 (pay 1,1 / 0,8),
    vida 79/79, kaset 4/4, **6.074,6 g**, AM (−0,05; 588,39; 0,64); bantlar 204,5 (uzatma), tümü X2D + okul 250'ye sığıyor.
    **Tek bulgu:** "Govde orta bandi sag" desteksiz=False, ama sorun bir *hesap hatası* (z 220,5'te `makeOffset2D: result is null`),
    gerçek çıkıntı değil (1700'de aynı geometri geçmişti). → kabuk_montaj destek kontrolüne yeniden deneme eklenecek, kabuk yeniden koşulacak.
- 2026-10-29 02:17 **5 dirsek (koştu, 1650):** `dirsek_montaj` 57 parça, ev pozu çakışma 0, omuz arayüzü 0, bağlantı 22/22, dirsek serbest
  −40…110 (arayüz 0…105), kablo kontrolü OK (S1 U R_min 12,91; bilek servosu lehimli ek artan 0,5 mm), 397,1 g, AM (190,1; −255,2; −1,3)
  (omuz yereli). Tork: S1 yüklü 31,12 / stall 30,4 → pay 0,98; S2 31,40 → 0,97; dirsek yüklü 12,58 / 9,4 → 0,75 (el ucunda 0,5 kg;
  2× pay için yük ≤ ~100 g) — tahmini, Y2a kontrolüne. **Bulgu:** El baskısı destek kontrolüne takıldı (z 70,5, O22 yaka boşluğunun düz
  tavanı 24 mm köprü > 15). Düzeltme: `dirsek_parcalar` yaka boşluğunun üst (baskıda yukarı) ucu 45° koni (10,5 mm) + 5,5 mm silindir;
  El ~+2–3 g (tahmini; yeniden koşuda ölçülecek). Taslakla El artık birebir değil.
- 2026-10-29 02:17 **7 taban (bitti):** `taban_parcalar`: X_BR 171 / X_WH 216 (TABAN_DX), alt plaka 346 × 500 (kat ve güç paneli 270
  kalır), braket M4'leri plaka üstünde DIN 985 (`somun` bağlantı tipi; ray dışında x 153), kablo şeması y'leri S3'e bağlı, Nextion 5 V
  hattı kaldırıldı. `taban_montaj`: devrilme teker hattı XC 178 → A._X_WH (216), Nextion güç satırı kaldırıldı, 10,1" ekran satırı (7"
  değerleri, tahmini, Y2b), DS3235 adları. `donus_hesap.X_W` 0,178 → A._X_WH. `kafa7_parcalar` assert KY1 == HEAD_UP → 275 (HEAD_UP 290).
  Sonuç: 316 parça (+13 referans), iç çakışma 0, bağlantı 119/119, iskelet 0, kabuk 0 (291 parça, 1650), teker–etek 4 × 12,0 mm,
  bölge 46 / 0 ihlal, baskı 4/4 desteksiz, **7.795,7 g** (+400 kablo payı = 8.195,7), AM (−0,9; 120,4; −44,9). Robot satırları (devrilme,
  motor, dönüş) hâlâ eski 125 cm `montaj-analiz.json`'dan → ana montajdan sonra taban_montaj yeniden koşulacak.
- 2026-10-29 02:24 **6 kafa (sürüyor):** `kafa7_parcalar` assert düzeltildi (yukarıda); `kafa_parcalar` 147 parça (Gövde/Pan 61, adaptör 13,
  Baş 73), 2.038,2 g. `kafa_montaj` 10,1" kafaya uyarlandı: saplama kontrolü (alt uç ısıl gömmede ≥ d, DIN 985'i ≥ 0,5 geçer, dayanmalar),
  kafa10 bağlantı temasları (`KP.BAG_METIN`; Pi burçları / köpük bant ara parça; tilt pimi çifti bağıl boşluk ≥ 0,3) + her kafa10
  cıvatası ↔ en yakın ısıl gömme somun, eski 7"/vizör oturmaları çıkarıldı, "eğme çatalı → mil" yerine çatal → adaptör → mil, ısı hesabı
  yeni yarıklarla (giriş 630 / çıkış 840 mm², H 39,5; 10,1" ekran 4 W TAHMİNİ), kablo payı merkezi tilt ekseninin 20 mm altı (tahmini).
  İlk koşu: ev pozu çakışma 0, bağlantı 28/29 (eksik olan yalnız ara parçalı temaslardı → kontrol düzeltildi, yeniden koşulacak).
- 2026-10-29 02:24 **8 ana montaj (hazırlık):** `ana_montaj.py` → `robot-bom.csv` (tür + kod, modül sütunu) + boy/S3/uzama/taban alanları,
  çarpışma karşılaştırmasına "carpisma-sonuc.json eski (Y4)" notu; `moduller.py` açıklama metinleri (8 gövde braketi, braket DIN 985,
  10,1" kafa, adaptör). Yeni `montaj/yerlesim_kontrol.py` (kısa kontrol: ev pozu S2 5 tüm modül çiftleri; sağ kol kaba ızgara S1 5 × S2 4
  × dirsek 2, S1 ≥ 120 → S2 ≤ 117; kafa pan 5 × tilt 3 + en küçük boşluk) → `yerlesim-kontrol.json`. README: taslak-170 ARŞİV notu + 1,65 m notu.
- 2026-10-29 02:28 kafa ilk koşu sonuçları: tilt serbest −15…15 (arayüz ±15 tam sınırda; +20'de ekran ↔ boyun mili, −20'de arka kabuk ↔
  rulman yuvası), pan serbest ±180, tork tilt 2,39 kg·cm (pay 3,9) / pan 4,27 (pay 2,2), R62 sabit parçalar ≥ 8,41 mm, kafa 2.038,2 g.
  **Baskı bulguları:** (a) boyun yükseltme adaptörü üst flanşı 9 mm yatay çıkıntı (destek 4 katman) → `kafa10_lib.adaptor` flanş altına
  45° koni (r 21 → 30); (b) **kafa kabuğu SAĞ parçaları (ön + arka) x = 0 dikiş dili** (16 mm şerit, iç yarı duvar) yüzü-tablada baskıda
  ~1,25 mm yükseklikte konsol → destek gerekir (ön sağ 2 bölge, arka sağ 1 bölge, z 2,5). Yarım-bindirme dikişin bu baskı yönünde doğal
  sonucu; düzeltme tasarım kararı (destekli baskı / dikiş biçimi) → AÇIK SORU (rapor). `kafa_montaj` json sonu eski K7 sabitlerine
  (Y_TABLA, LCD, YOL) bakıyordu → düzeltildi. S1-kaset.md belge düzeltmeleri (K3 listesi: ESKİ işareti, görünüm 28,4, duvar ipi −x notu,
  u_pay 7,0 satırları → KZ1) yapıldı; KZ1 ölçümü bekliyor.
- 2026-10-29 02:40 dirsek yeniden (El konisi + `dirsek_lib` baskı kontrolünde ofset kurulamayan yüz ofsetsiz, kafa_lib ile aynı): 57 parça,
  çakışma 0, bağlantı 22/22, **El desteksiz** (çıkıntı 0,022 → 0,009), kablo OK, **399,7 g** (El +2,6 g), AM (190,1; −255,8; −1,3);
  tork S1 yüklü 31,21 / 30,4 (pay 0,97), S2 31,49 (0,97), dirsek 12,62 / 9,4 (0,74) — 0,5 kg el yükünde servolar yetmiyor, 2× pay için
  el yükü ≤ ~100 g (tahmini; Y2a kontrolüne). kafa ikinci koşu: bağlantı 29/29, ama adaptör koni füzyonu OCC'de sessizce bozuldu
  (adaptör 4 cm³'e düştü, kütle 1.980,7) → adaptör gövdesi tek döner profil (revolve) olarak yeniden yazıldı (65,3 cm³, test edildi);
  kafa + kabuk (destek kontrolü düzeltmesi) yeniden koşuyor.
- 2026-10-29 02:50 **6 kafa (bitti):** 147 parça, ev pozu çakışma 0, bağlantı 29/29 (125 cm Gövde/Pan + 4 saplama + kafa10 temasları),
  bağıl boşluk ≥ 1,0, tilt serbest −15…15 (+20 / −20'de çakışma: sınır payı < 5°), pan ±180 serbest, kafa × gövde en az 3,21 mm,
  R62 sabit ≥ 8,41; tork tilt 2,39 kg·cm (pay 3,9; AM eksenden 0,4 mm), pan 4,27 (pay 2,2); adaptör artık desteksiz; **2.043,0 g**,
  AM yerel (1,4; 154,3; 19,5). Isı (tahmini, ekran 4 W): tipik 42 °C kapalı-çekiş, en kötü 45 °C. **Boy ölçümü:** kafa kabuğu tepesi
  yerel y 290,000 (optimalBoundingBox; kaba BoundBox 291,65 gevşek) → global **1.650,0 mm** = BOY. Açık: kafa kabuğu sağ parçaları dikiş
  dili desteği (yukarıda).
- 2026-10-29 03:05 **KZ1 ölçümü:** K3-olcum.py `cep` adımı scratch kopyasıyla (K2-ortak kök yolu yamalı, çıktı scratch) güncel FCStd'lerde:
  U ucu eşiği **L +3,73 / S1 +5,19°** (hedef ≥ +3 / +4 ✔), pim dikmesi S1 135'te 3,75. S1-kaset.md'ye Y2a bölümü eklendi.
- 2026-10-29 03:05 **8 ana montaj (koştu):** 1.073 parça, 22 grup, 22 eklem, solve 0, ev pozu çözücü sapması 0, STEP 1.073 katı, geçersiz 0,
  **24.396,1 g**, AM (−0,20; 527,43; −12,38); modül analizleriyle fark −0,117 g (yuvarlama), parça 1.073/1.073. `robot-bom.csv` 137 kalem
  (bağlantı 822 adet 1.372,7 g, baskı 63 adet 7.349,3 g, satın 165 adet 13.754,4 g, lazer 3 / 1.800,0 g, imalat 1). Karşılaştırmadaki
  çarpışma farkı (3.135 g / 152,8 mm) eski 125 cm carpisma-sonuc.json'dan, anlamsız (Y4). Sırada: kabuk (destek kontrolü yüz başına
  ofset), taban (robot satırları yeni montajla), yerleşim kontrolü.
- 2026-10-29 03:10 **Taslakla fark** (taslak 520 dökümü 1.076 parça / 25.027,2 g / AM y 558,45 ↔ ana montaj 1.073 / 24.396,0 / 527,43; scratch
  `fark.py`, montaj-analiz.json `parcalar`): toplam **−631,2 g**. (a) **50 mm boy farkı:** gövde direği −98,0 (1.235,5 → 1.185,5), 4 uzatma
  bandı −136,4 (bant 217,5 → 192,5) → ≈ −234 g; parça sayısı aynı (bindirme/braket adları yükseklikle değişti). (b) **Nextion kaldırıldı:**
  ekran −535,0 + 4 ekran cıvatası + 4 ısıl gömme −4,4; göğüs bandı kapalı +98,9 (sağ +52,8 / sol +46,1). (c) diğer: etek orta yarıları
  +36,4 (taslakta 520 geçişi orta bantta farklı kesilmişti), boyun adaptörü +4,8 (45° koni), El ×2 +5,2 (koni), saplama M3×71 → ×73
  (DIN 985'i +1 mm geçer), alt plaka +0,9, omuz bandı −4,6. Modül AM y farkları −50 (omuz/dirsek/kafa) = boy farkı. Taban parça/kütle aynı.
- 2026-10-29 03:35 **kabuk (son koşu):** destek kontrolünde yüz başına ofset (kurulamayan yüz ofsetsiz) → 25/25 baskı desteksiz; 291 parça,
  çakışma 0, iskelet 0, bölge 0, 6.074,6 g, AM (−0,1; 588,4; 0,6). **taban (robot satırları yeni montajla):** robot **24,80 kg**
  (kablo payı 0,4 dahil), ev AM (−0,2; 521,3; −13,2); devrilme ivmesi düz ileri 3,73 / geri 3,23 / yan 4,06, rampa 5° geri **2,37**
  (en kötü: kollar geride 2,23; fren 1,5 varsayımı); yerinde dönüş sürekli torkun %249'u (omniyle %47) — E0 kararı aynı, ölçüm bekliyor.
  **Yerleşim kontrolü** (`montaj/yerlesim-kontrol.json`, 127 s): (1) ev pozu S2 5: 28 modül çifti, 2.394 bb çifti, **çakışma 0**;
  (2) sağ kol kaba 40 poz: **çakışan 0**; (3) kafa pan ±90 × tilt ±15 (15 poz): çakışma 0, 15 mm içinde komşu parça yok. Poz uygulaması
  ayrıca doğrulandı (El/bilek ve yüz kabuğu bb'leri pozla değişiyor).
- 2026-10-29 03:35 **Y2a tasarım işi bitti → kontrol ajanına.** Kalan / açık: (1) akü 75 mm öne UYGULANAMADI (Duffy kararı a/b/c);
  (2) kafa kabuğu sağ parçaları dikiş dili baskı desteği; (3) servo payları 0,5 kg el yükünde < 1 (S1/S2 0,97, dirsek 0,74; ≤ ~100 g
  için 2×); (4) 10,1" ekran gücü / ısı tahmini; (5) tam çarpışma taraması + devrilme/motor kontrolü (Y4 / kontrol ajanı).
  **Kapsam dışı notlar:** `kabuk_rapor.py` `A.NEXTION`'a bakıyor (çalışmaz), tüm `rapor.html` / görseller / `OZET.md` / `carpisma-sonuc.json`
  eski (125 cm); README modül metinleri (Nextion, 7" LCD, 955/975) Y2b; uzatma kablosu boyu `dirsek_montaj` S1 boy satırı 1.926 mm (S2 1.490)
  — maliyet Y2b'de yeniden; `tasarim/solidworks/` izlenmeyen klasör bu işin değil.
