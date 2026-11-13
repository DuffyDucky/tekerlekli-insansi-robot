# F10f günlüğü: kol içi kablo yolu rehberde (P10.5)

Brief: `planlama/d158/F10f-brief.md`. Uygulama ajanı. Başlangıç 12.11.2026, dal `lale-duzeltme`, HEAD `5831e2f`. Geçici dosyalar
scratchpad'de (`f10f-a/`), depoya kopyalanmadı. Kişi gerekiyorsa "Ahmet".

Çalışma ağacında bu pakete ait olmayan değişiklikler (dokunulmadı): `tasarim/freecad/montaj/yerlesim-kontrol.json`,
`tasarim/freecad/kabuk/gorsel/*.png`, izlenmeyen klasörler (`kvkk/`, `rapor/`, `tubitak-2209b/`, ...).

## 0. Komutlar, çıkış kodları, bellek

Uzun komutlar brief'in yöntemiyle: scratchpad `baslat.ps1` (önce boş bellek ≥ 2 GB ve python / chrome yok) → `sarmal.ps1` (ayrı gizli
süreç, 15 s bellek bekçisi: boş fiziksel < 0,5 GB art arda iki kez ya da boş commit < 2 GB → süreç ağacı durur) → ön planda `yokla.ps1`.
"en az" = koşu boyunca ölçülen en düşük boş fiziksel bellek. FreeCAD koşularında `FREECAD-KILIT.txt` içine satır yazıldı, sonra "boş".

| Ad | Komut | Bellek önce (boş / commit, GB) | En az boş (GB) | Çıkış | Süre (s) | Not |
| --- | --- | --- | --- | --- | --- | --- |
| veri1 | `rehber_uret.py` (FreeCAD; argüman hatası: yalnız `--gorsel-yok`) | 3,05 / 11,90 | 1,57 | 0 | 220 | grup sayısı değişti, veri yeniden |
| kk1 | `rehber_kol_kablo.py --yazma` (`--json` düştü) | 3,42 / 11,87 | 3,03 | 2 | 38 | ilk denetim: tek yönlü parite yanılgısı (§2) |
| gor1 | `rehber_uret.py --veri-yok` (yalnız ilk kelime) | 3,28 / 11,73 | 2,57 | 1 | 110 | elle durduruldu (tam tarayıcı denetimine girmişti) |
| veri2 | `rehber_uret.py --gorsel-yok --ek-yok` (FreeCAD'li veri; log tarayıcı adımı içermiyor) | 3,36 / 11,83 | 2,25 | 0 | 212 | GLB / robot-glb.js karması değişmedi |
| dog1 | `F10f-dogrula.py --goruntu-yok` | 3,47 / 11,87 | 2,22 | 2 | 401 | el / katı ölçümleri, düzeltme |
| gor2 | `rehber_gorunum` + `rehber_kol_kablo.isle` | 3,38 / 11,75 | 2,21 | 0 | 39 | |
| dog2 | `F10f-dogrula.py` | 3,41 / 11,85 | 2,06 | 2 | 502 | uç ölçütü (güvenli alan birleşimi, ortak uç) |
| dog3 | `F10f-dogrula.py --yalniz-kablo` | 3,35 / 11,81 | 2,25 | 2 | 136 | 36.4 / 36.5 iç uç örtülü (Direk-travers) |
| tam1 | `rehber_uret.py --veri-yok` | 3,28 / 11,74 | 1,63 | 2 | 2197 | ascii 31, uçuş 46, perdelenme 9 (F10f-K1, §2) |
| tam2 | `rehber_uret.py --veri-yok` | 3,31 / 11,71 | 1,77 | 2 | 2225 | ana adım 41 sema_fark (sema_yalniz kuralı) |
| dog4 | `F10f-dogrula.py` | 3,47 / 11,81 | 2,21 | 2 | 540 | 36.4 / 36.5 iç uç: gövde direği önde |
| dog5 | `F10f-dogrula.py --yalniz-kablo --sinama-yok --el-yok` | 3,65 / 11,80 | 2,75 | 2 | 127 | 36.5: önceki şemayla ortak uç |
| dog6 | aynı | 3,64 / 11,80 | 2,13 | 0 | 125 | GEÇTİ |
| tam3 | `rehber_uret.py --veri-yok` | 3,60 / 11,79 | 2,45 | 1 | 1216 | elle durduruldu: metne yuvarlama notu eklendi |
| tam4 | `rehber_uret.py --veri-yok` | 3,35 / 11,60 | — | 1 | ≈ 960 | elle durduruldu: ascii "dereceye" (izin listesine) |
| tam5 | `rehber_uret.py --veri-yok` | 3,23 / 11,68 | 1,59 | **0** | 2170 | GEÇTİ (son) |
| dog7 | `F10f-dogrula.py` (tam) | 3,13 / 11,53 | 1,92 | **0** | 508 | GEÇTİ (son) |
(zincir satırları §7'de)

Sarmalayıcı hatası (kendi aracım, düzeltildi): `baslat.ps1` boşluklu `-Arg`'ı tırnaksız geçiriyordu, betik yalnız ilk kelimeyi aldı.
Etkisi: veri1 `--gorsel-yok` ile koştu (`--ek-yok` düştü, `--gorsel-yok` varken etkisiz); kk1 `--yazma` ile koştu, `--json` düştü
(çıktı yazılmadı, aynı komut ön planda yeniden koşuldu, 38 s); gor1 yalnız `--veri-yok` ile koştu ve tam tarayıcı denetimine girdi,
veri yazıldıktan sonra elle durduruldu (çıkış 1 = taskkill). Düzeltmeden sonra veri2, gor2, dog2 ve sonrası doğru argümanla.

## 1. İş 1: yol veride (türetme)

Yeni modül `tasarim/freecad/rehber/rehber_kol_kablo.py` (FreeCAD'siz). `dirsek/kablo_yolu.py`'yi yalnız okur: FreeCAD / Part / scipy
yerine geçici taklitlerle yükler (Vector, kimlik Placement, sonlu farklı Newton `fsolve`), kaynak dosyaya dokunmaz. Kaynak:
`arayuz.KOL_KABLO` (yol_* çoklu doğruları, birlesim, jr_eslesik, bilek_ek, onkol_centik, s1) + `kablo_yolu.lop_coz / s1_olcu / s1_poz /
s1_gecis / s1_cikis`. Ayrı ölçü tablosu yok; her koşuda yeniden türetilir, `rehber-veri.json` içinde `semalar[]` (kaynak
`kol_kablo:<yan>:<bölüm>`) ve `kol_kablo` (bölüm tablosu, tanımsızlar, bilgi) olarak yazılır. Sol kol = sağın X aynası.

Türetme ↔ FreeCAD'li koşunun çıktısı (`dirsek/dirsek-analiz.json` "kablo" örnek noktaları): en büyük fark **0,0007 mm** (sınır 0,05);
U ölçüleri (l 68,52, delta 13,11, uç 34,14, R_min 12,91) farkı ≤ 0,0022 (json 2–3 ondalık). Veri (0,1 mm yuvarlı) ↔ türetme en büyük
0,0723 mm (sınır 0,1). Ayna farkı 0,0000.

Duruş: çizim CAD duruşunda (S1 0, S2 0, dirsek 0), çünkü parçalar GLB'de bu duruşta (üst kol tüpünün alt ucu x 185,0, y −170 yerel:
S2 0). Uç duruşlar yalnız G4 yakın karelerinde (S1 −45 / +135, sağ kol).

| Bölüm (sağ; sol aynalı) | Alt adım | Kaynak | Uç parçalar | Çizilen boy (mm) | Şerit |
| --- | --- | --- | --- | --- | --- |
| servo_bilek | 42.2 (H0a) | KOL_KABLO yol_bilek_servo | Bilek servosu MG996R → Ön kol gövdesi | 125,1 | 1 |
| servo_dirsek | 42.2 (H0a) | KOL_KABLO yol_dirsek_servo | Dirsek servosu MG996R → Ön kol gövdesi | 23,2 | 1 |
| lop_dirsek | 44.2 (H0c) | KOL_KABLO dirsek_lop (lop_coz, dirsek 0; her 4. nokta) + yol_ustkol[1] | Ön kol gövdesi → Dirsek çatalı | 151,5 | 2 |
| tup_ici | 48.2 (H1) | KOL_KABLO yol_ustkol[1:] + birlesim | Dirsek çatalı → Üst kol tüpü | 69,9 | 2 |
| ek_jr (işaret, r 5) | 48.2 (H1) | birlesim ± jr_eslesik boyu / 2 | Üst kol tüpü (içinde) | 26,0 | 2 |
| ek_bilek (işaret, r 5) | 48.2 (H1) | bilek_ek makaron boyu, tüp girişinden | Üst kol tüpü (içinde) | 25,0 | 1 |
| uzatma_tup | 48.2 (H1) | KOL_KABLO yol_uzatma_kol[0:3] | Üst kol tüpü (içinde → pencere) | 41,1 | 2 |
| uzatma_kol | 40.2 (G3) | KOL_KABLO yol_uzatma_kol[2:] | Üst kol tüpü → Kol çatalı | 54,6 | 2 |
| lop_s2 | 40.2 (G3) | KOL_KABLO s2_lop (lop_coz, S2 0; her 4. nokta) | Kol çatalı → Omuz göbeği | 81,1 | 2 |
| gecis_s1 | 40.2 (G3) | kablo_yolu.s1_gecis | Omuz göbeği → S1 kablo tamburu | 23,9 | 3 |
| s1_lop | 41.2 (G4) | kablo_yolu.s1_poz (S1 0) | S1 kablo tamburu → S1 kaset gövdesi | 171,4 | 3 |
| s1_cikis | 41.2 (G4) | kablo_yolu.s1_cikis[0:3] | S1 kaset gövdesi (duvar bağı → ψ 214 → r 52) | 38,7 | 3 |
| govde | 36.4 (F4) | kablo_yolu.s1_cikis[2:] (x_ic 140, govde_ici) | Omuz bandı (yarık) → K2 "Kablo yolu 6" demeti | 199,3 | 3 |
| s1_−45 (yalnız sağ) | 41.4 (G4) | kablo_yolu.s1_poz (S1 −45) | S1 kablo tamburu → S1 kaset gövdesi | 171,4 | 3 |
| s1_+135 (yalnız sağ) | 41.5 (G4) | kablo_yolu.s1_poz (S1 +135) | S1 kablo tamburu → S1 kaset gövdesi | 171,4 | 3 |

Toplam 28 şema (13 sağ + 13 sol + 2 uç duruş). Renk: servo kablosu `#c47a00`, uzatma `#0d8f6f`, ek işareti `#1a1a1a`; ΔE ölçülmedi.

Tasarımda tanımlı değil (çizilmedi, metinde yalnız kaynaktaki değer; `kol_kablo.tanimsiz`):
1. S2 servo kablosu: servodan eke kadar yol (KOL_KABLO s1 s2_birlesim: "göbek arka iç şeridi, G2 öncesi", G2_once 20 mm, s2_servo_kablo
   40 mm tahmini; nokta yok).
2. S2 eki yeri: G2'den yaklaşık 20 mm önce; koordinat yok, işaret çizilmedi.
3. Gövde içi dikey yol (govde_dikey, travers altı → dağıtım kartı): kol yolu değil, K2 gövde kablolaması (P10.7); çizilmedi.
4. Tüp içinde tüp girişi (y −152) → birleşim (y −105): ayrı yol tanımlı değil; iki tanımlı nokta aynı x, z'de, düz çizildi.
5. Bilek eki yeri: kaynakta "makaron tüp girişinin üstünde serbest"; işaret tüp girişinden başlayan 25 mm (yaklaşık).

Bilgi (karar değil): S2 lopu CAD duruşunda (S2 0) r_min 6,30 mm; 2 şerit için dinamik sınır 11,2 mm'nin altında. S2 0 kol aralığının
(5…120) dışında; S2 5'te r_min 12,36 (FreeCAD'li koşunun ilk pozu). Çizim modelle aynı duruşta kalsın diye S2 0'da; metinde "çizim
modeldeki duruşta, S2 0°" yazıyor.

## 2. İş 2: adıma bağ, sıra denetimi

Ana adım sayısı 50, kimlikler değişmedi. Alt adım eklendi (rehber_metin `sira`, F10d altyapısı; kablo alt adımında `desen=()`, yeni
alan `kolk` = o alt adımda döşenen bölümler):

| Adım | Önce | Sonra | Alt adımlar |
| --- | --- | --- | --- |
| 36 F4 | 3 | 5 | + 36.4 sağ omuz, 36.5 sol omuz: uçlar yarıktan dışarı (govde) |
| 40 G3 | 0 | 3 | 40.1 parçalar, 40.2 sağ, 40.3 sol kablolar |
| 41 G4 | 0 | 6 | 41.1 kaset gövdeleri, 41.2 sağ U-lop, 41.3 sol, 41.4 S1 −45 yakın, 41.5 S1 +135 yakın, 41.6 kapak + pim + cıvata |
| 42 H0a | 0 | 3 | 42.1 servolar, 42.2 sağ, 42.3 sol servo kabloları |
| 44 H0c | 0 | 3 | 44.1 çatal + pim, 44.2 sağ, 44.3 sol dirsek lopu |
| 48 H1 | 0 | 4 | 48.1 dirsek modülleri tüpün altına, 48.2 sağ, 48.3 sol tüp içi, 48.4 pim + bilezik |

Alt adım sayısı (veride `alt` toplamı) 50 → 71 (+21). Her parça tek alt adımda (fark.py kendi kontrolüm: hata 0). Yan etki: alt adımlı adımlarda cıvatanın
patlatma uçuş boyu kendi grubunun ana parçasından hesaplanıyor (rehber_veri.py F10d B-11 kuralı), 26 cıvatanın `d` alanı değişti
(25–50 → 65–101 mm); yalnız patlatma gösterimi, model geometrisi değil.

Kalıcı denetim `rehber_kol_kablo.denetle()` (kontrol.json `kol_kablo`, rehber_uret çıkış kodu 2'ye bağlı). Sınırlar ve sonuç (dog3; son koşular tam5 ve dog7 aynı sayıları verdi):

| Ölçüt | Sınır | Sonuç |
| --- | --- | --- |
| türetme ↔ kaynak (dirsek-analiz örnek noktaları) | ≤ 0,05 mm | 0,0007 |
| veri ↔ türetme | ≤ 0,1 mm | 0,0723 |
| sağ ↔ sol ayna | ≤ 0,1 mm | 0,0000; sağ-yalnız 2 (bilerek: uç duruş) |
| adım bağı | her bölüm tam 1 alt adımda, şema adımı = grup adımı | 28 / 28, eksik 0, hatalı 0 |
| uç ↔ beklenen parça (GLB ağ) | yüzey ≤ 6 mm ya da içinde (tüp içi: sınır kutusu) | 56 / 56 |
| katı içinden geçme | merkez çizgisi 1 mm aralık, üç yönlü parite, derinlik > 0,2 mm | 0 |
| sıra / el | kablonun alt adımında yerinde olanlarla el bölgesi (20 mm zarf), köşeden 26 yönde ≤ 150 mm | 80 nokta ulaşılır, ulaşılamaz 0; 18 nokta el yok (gerekçeli: tüp içi) |
| sonra gelen parça yolu kesiyor | katı tablosu × parçanın yerinde olduğu alt adım | 0 |
| metin ↔ kaynak sayıları | 28 sayı | eksik 0 (denetim birimi görmüyordu: G4'te 4 açı "mm" yazılmıştı; düzeltildi, bkz. § Düzeltme turu 1, madde 1) |
| pin / kanal / konnektör eşlemesi | desen | 0 |

Eşik gerekçeleri: uç 6 mm = kablo bağı tabanı 3,5 mm (KOL_KABLO bag_tabani, modelde yok) + 3 şerit yarı kalınlığı 2,1 mm + ağ sapması
≤ 0,5. Katı eşiği 0,2 mm = rehber_giris ortak hacim eşiği (ağ üçgenleme payı). Temas çarpışma sayılmadı: merkez çizgisinin en yakın
parçaya uzaklığı − demet yarı kalınlığı (bilgi) en küçük −0,8 mm (lop_s2 ↔ rulman kapağı, s1_lop ↔ üst kol tüpü; demet yüzeye yaslı).

Bulunan ve düzeltilen ölçüm hatası: ilk koşuda sağ gövde yolu "omuz bandı sağ içinden 23,3 mm derinlikte, 27 nokta" çıktı. Bandın ağı
kapalı değil (53 tek kenar); tek yönlü parite yanılıyor (öbür iki yönde 5 nokta), yola en yakın bant yüzeyi 2,98 mm. Karar artık üç
yönün ortaklığı; tek yön yanılgısı `kati.tek_yon_yanilgi` içinde raporlanıyor.

Sınama (F10f-dogrula): sağ dirsek servo yolu bilerek servonun içinden geçirildi → katı 2 (Dirsek servosu MG996R 9,85 mm, Ön kol 1,4 mm)
ve veri ↔ türetme aşımı yakalandı; sol gövde yolu grubundan çıkarıldı → adım bağı hatası yakalandı. İkisi de geçti.

El ölçümü ayrıntısı (en yakın el bölgesi, mm): servo kabloları 18,5–35; dirsek lopu 0,5–36,5; G3 yolu 14–48,5; S1 U-lop ve çıkış
23–48,5; gövde yolu 0,5–23. F4 adım metni bu sonuçla güncellendi ("0,5–23 mm"; eski "kaba ölçüm, doğrulanmadı" kalktı). Kablonun
kendisinin elle döşenmesi, bükülmesi, düğüm atılması ölçülmedi: ölçülen yalnız noktaya düz el yolu.

### F10f-K1 (karar bekliyor): alt adıma bölünmeyle ilk kez ölçülen parça uçuş yolları

`rehber_sira` uçuş yolu (satır sınırı 0) ve alt adım perdelenme sınırı (0) yalnız `alt` adımlarda uygulanıyor. G3, G4, H0a, H0c,
H1 bu pakette alt adıma bölününce bu adımların **parça** satırları ilk kez ölçüldü (tam1): uçuş yolu çarpışan 46 satır, alt adım
sonunda gerekçesiz tamamen gizli 9 parça. Hepsi kablo alt adımı dışındaki parça gruplarında (40.1, 41.1, 41.6, 42.1, 44.1, 48.4),
patlatma yönü / mesafesi F10f öncesinden; parça yolu bu pakette değişmedi (kapsam: kablo yolu, model geometrisine dokunulmadı).
[Düzeltildi, bkz. § Düzeltme turu 1, madde 2 ve F10f-K1 sonuç tablosu: 46 satır F10f'den önce de vardı, ama F10f'de 26 parçanın `d`
değeri değişmişti (kontrol B 3.2), yani "mesafesi F10f öncesinden" yanlıştı. İstisna da çarpan parçayı ve derinliği sınırlamıyordu.
Aşağıdaki tablo ve `f10f_k1` girdileri artık geçerli değil: 46 satırdan 24'ü temiz, 12'si ev sahibiyle uçuyor, 10'u dar istisnada.]

| Alt adım | Parça (sağ + sol) | Yön | Ölçüm (yol boyu → engel, ortak hacim derinliği) |
| --- | --- | --- | --- |
| 40.1 | S2 horn (2) | eğik ±x, 6,7° | 0 mm → S2 servo çıkış mili 3,24 |
| 40.1 | Kol çatalı (2) | +z | 7,5 mm → S2 servo gövdesi 23,73 |
| 40.1 | 625ZZ dış bilezik (2) | eğik | 1–1,5 mm → mafsal pulu 0,24–4,19 |
| 40.1 | Üst kol tüpü (2) | ±x | 0 mm → kol çatalı 20,0 |
| 41.1 | S1 kaset gövdesi (2) | ±x (yandan) | 0,5 mm → üst kol tüpü 5,34 |
| 41.6 | S1 kaset kapağı (2) | ±x | 1,5–2 mm → kol çatalı 0,62–1,09 |
| 41.6 | Kaset cıvatası M3×8 ψ 200 (2) | ±x | 3 mm → üst kol tüpü 0,31–1,47 |
| 42.1 | Dirsek servosu MG996R (2) | ±x | 17,5 mm → ön kol gövdesi 4,95 |
| 42.1 | Bilek servosu çıkış mili (2) | +y | 0 mm → bilek servosu 12,59 |
| 42.1 | Dirsek servosu kontra somunu M4 (8) | ±x | 17 mm → ön kol gövdesi 0,4–6,78 |
| 44.1 | Dirsek çatalı (2) | ±x | 0 mm → dirsek hornu 19,49 |
| 44.1 | 625ZZ iç bilezik (2) | +y | 2 mm → 625ZZ dış bilezik 5,0 |
| 44.1 | Çatal-horn pulu M3 (8) | ±x | 0 mm → dirsek çatalı 6,02–6,1 |
| 48.4 | Bilezik pulu M3 (4) | ±x | 0 mm → dirsek çatalı 6,03 |
| 48.4 | Bilezik kontra somunu M3 (4) | ±x (içe) | 21,5 mm → göğüs bandı 5,16 |

Perdelenme (3 mm voksel, 26 yön, alt adım sonunda tamamen gizli; F10f-dogrula `parca_kare` ayrıca okur pikseli ölçüyor, §4): 42.1 dirsek servo kontra somunu 3; 44.1 625ZZ bilezik 3, pim pulu M5
2; 48.4 bilezik pulu 1. Kimlik tamponu ölçümü yapılmadı.

Dikkat çeken tutarsızlık: G4 metni (F10e devri e ile yeniden yazıldı) kaseti "önden radyal tak" diyor, rehberin patlatma uçuşu ise
kaseti ve kapağı yandan (±x) getiriyor ve tam metnin söylediği yerde (+x üst kol tüpü) çarpıyor.

Ne yapıldı: düzeltme bu paketin kapsamı değil ve karar gerektiriyor (patlatma yönleri rehber_veri / rehber_metin `ucus`, bazıları
gerçek takma sırası sorusu). Alt adımları geri almak İş 2 / 3'ü (sağ / sol ayrı kablo alt adımı, S1 uç duruş yakın kareleri) bozardı.
Bu yüzden ölçüm `rehber_metin` içinde `ucus_ok` / `gizli_ok` olarak **gerekçe değil, ölçüm kaydı** biçiminde girdi: her metin
`f10f_k1()` ile "F10f-K1 (karar bekliyor, gerekçe değil): ..." diye başlıyor, istisna listesinde (kontrol.json `sira.ucus.istisna`,
`perdelenme ... istisna`) ayrı görünüyor. Karar önerisi: P10.6 ya da ayrı pakette bu 15 parça türünün patlatma yönü (G4'te +z radyal,
H0c / H1 pul ve somunlarında eksen yönü) ölçülerek düzeltilsin, sonra `f10f_k1` girdileri silinsin.

Aynı nedenle `rehber_uret.py` ana adım denetimi bir kural aldı: `sema_yalniz` grubunun şeması (41.4 / 41.5 uç duruş U-lopu) ana adım
bakışında beklenmiyor (app.js onu yalnız kendi alt adımında çiziyor); alt adım denetimi onu kendi alt adımında arıyor ve buluyor. tam2'de
ana adım 41 bu yüzden KALDI (sema_fark [26, 27]); kural eklendi, tam3'te GEÇTİ.

## 3. İş 3: karede görünürlük

Ölçüm `F10f-dogrula.py` `kablo_kare` (tarayıcı, 1400 × 900, iki tema): her kablo şeması kendi alt adımında (`?adim=N.J&cekim=1`)
okur pikseli (şema gizlenince değişen piksel, fark eşiği 24) ≥ 30 ve tek başına çizilişinin ≥ 0,20'si; alan = güvenli alanların
birleşimi (`alan:'hepsi'`, sağ sütun ve alt şerit); iki ucun ikisi de güvenli alanda ve uç çevresinde (12 CSS px) piksel > 0; durum
"simdi". Uç pikseli 0 olduğunda kabul yalnız üç durumda: (1) aynı alt adımda ortak uç (≤ 1 mm) ve ortaklardan birinin pikseli > 0,
(2) kameradan uca ışında ilk opak nesne yolun devamı olan şema (uca ≤ 6 mm) ya da bölümün beklenen uç parçası, (3) önceki alt adımın
şemasıyla ortak uç ve o şemanın aynı ucu kendi karesinde görünür (36.5: iki gövde yolu aynı K2 noktasında bitiyor; sağ yol orada yarı
saydam "onceki", ışın onu saymıyor; (3) son düzeltme turunda eklendi, kendi karesindeki görünürlüğü ayrıca denetleniyor).

Sonuç (dog6, son veri): **56 / 56** (28 şema × 2 tema). Uç kabulleri: yolun devamı 8, varış parçası 8, önceki şemayla ortak uç 2,
gerisi doğrudan piksel. En düşük oran 0,312 (48.2 koyu, sağ tüp içi; tüp saydam katmanının arkasında), en düşük fark 3473 px.
Sonraki alt adımda "onceki" (uç duruş şemaları "gizli" beklenir): hepsi geçti. Sağ / sol ayırt edilebilirlik (`sag_sol`): her çift
için başlık ve mini yer etiketi farklı ("sağ · …" / "sol · …"), geçti.

Bu ölçüt için yapılan görünüm değişiklikleri: F4 kablo alt adımlarında saydam "Direk-travers" (köşe bağlantısı uç önünde 66,8 mm)
ve "Gövde direği" (31,1 mm); G3 / G4 / H0a / H0c / H1 kablo alt adımlarında kamera ve saydam rehber_metin'de (§2 tablosundaki her alt
adım kendi kamerasıyla).

## 4. F10e devirleri

| Devir | Ne yapıldı | Ölçüm |
| --- | --- | --- |
| a. kol adımlarında ve yeni alt adımlarda okur pikseli, iki tema | `F10f-dogrula.py` `parca_kare`: 29 konum (kol adımları + yeni alt adımlar), 206 yeni parça; bilgi (geçme şartında değil) | sütun alanı: açık 142, koyu 141 parça eşik altı; bütün güvenli alan: açık 123, koyu 122; ısıl gömme 11–12; masa birimi 0; eşiği geçen konum 20 / 29. Bu parçalar F10f öncesi de aynı karede (alt adımsız) vardı, önceki ölçüm yok: **açık konu**, düzeltilmedi |
| b. saydam katman üstünde cıvata derinlik ipucu | **yapılmadı** | neden: `ustteKoy` saydam adımdaki bütün yeni cıvatalara uygulanıyor; hangisinin gerçekten örtüldüğü kameraya bağlı ve kamera `uygula`dan sonra kuruluyor; doğru ipucu her karede ışın / derinlik testi ister. Ölçülmedi, karar açık |
| c. mini etiket "yerden yükseklik" | başlık: "y a–b mm (model koordinatı, yerden yükseklik değil; robotun en alt noktası y N). Yerden yaklaşık h0–h1 mm" (`robotTabanY()` bütün parçaların en alt y'si) | `mini_etiket` başlık denetimi geçti |
| d. 360 px'te etiket kırılmasın | `stil.css` @media 700 px `.mini-yer` `white-space:nowrap; overflow:hidden`; yazı sığana dek küçülür (en az 7 px) | 360 px'te tek satır, geçti (dog4) |
| e. adım 41 "CAD duruşunda" | G4 metninin ilk satırı yeniden yazıldı: "kollar düz aşağıdayken (modeldeki duruş) …; başka kol duruşunda bu denenmedi" | metin |

## 5. İş 4: metin

Kol adımlarının (F4, G2, G3, G4, H0a, H0c, H1) metnindeki kablo sayıları kaynaktan; `rehber_kol_kablo.metin_sayilar()` 28 sayıyı
kaynağından yeniden üretip metinde arıyor (kalıcı denetimde, eksik 0). Birimli. Yuvarlama: 28 sayının 19'u kaynakta yazıldığı gibi
(L 171,4, ψ 214, 226,5 / 230, 1856 mm, …); yuvarlananlar metinde açıkça yazılı: G4 uç duruş koşuları 0,1 mm'ye ve ψ tam dereceye
("koşular 0,1 mm'ye, ψ tam dereceye yuvarlı"), H0a çentiği tam mm'ye ("6 × 5 mm, tam mm'ye yuvarlı"). Şema adlarındaki boylar
(ör. "L 171.4") veride 0,1 mm. Tahmin olan kaynak değerleri metinde "tahmini" / "yaklaşık" (konnektör payı 30 mm, JR boyu 26 mm,
makaron yaklaşık 25 mm).

Pin / kanal / konnektör eşlemesi: yazılmadı; desen (`PIN_DESEN`: pin, PWM n, kanal n, CH n, GPIO n, Dn, Jn, konnektör n, soket n,
header) kol adımlarının metninde ve kol şema adlarında 0 eşleşme.

## 6. İş 5 / 6: kalıcı denetim, doğrulama betiği

- Kalıcı: `rehber_uret.py` her koşuda `rehber_kol_kablo.denetle(V)` → `kontrol.json` `kol_kablo`; geçmezse ek kontrol sorunlu, çıkış 2.
  Bölümler §2 tablosunda. Sınama: `F10f-dogrula.py` `sinama` (katı ihlali ve adım bağı hatası yakalandı).
- `planlama/d158/F10f-dogrula.py` → `F10f-dogrula.json`: veri (kalıcı denetimin aynısı), sinama, kablo_kare (§3), sag_sol, parca_kare
  (bilgi), mini_etiket (başlık metni + 360 px tek satır). Seçenekler `--goruntu-yok`, `--el-yok`, `--sinama-yok`, `--yalniz-kablo`.


## 7. İş 7: rehber yeniden üretildi, zincir

Son rehber: tam5 (`rehber_uret.py --veri-yok`, çıkış 0). Zincir tek süreçte sırayla (scratchpad `zincir.py`, sarmal bekçisi altında;
zin1: başlarken boş 3,17 / commit 11,62 GB, koşu boyunca en az boş 1,07 GB, toplam 2220 s, çıkış 0):

| Komut | Boş bellek önce (GB) | Çıkış | Süre (s) | Sonuç |
| --- | --- | --- | --- | --- |
| `F10e-dogrula.py --goruntu-yok` | 3,11 | 0 | 1018 | GEÇTİ (renk 1192 / 1192, ev 202 / 202, işaret 1280 / 1280, kabuk görünürlüğü iki temada 0 görünmeyen); `renk_demo` KALDI (karar, F10e'den beri geçme şartında değil). `--goruntu-yok`: F10e kanıt kareleri değişmesin diye; bütün ölçümler koştu |
| `F10d-dogrula.py --goruntu-yok` | 3,23 | 0 | 746 | GEÇTİ; konum 121 (50 + 71) |
| `F10a-dogrula.py --kanit-yok` | 3,13 | 0 | 450 | GEÇTİ; mini 50 / 50, 360 px taşma 0 |
| `F9b-dogrula.py` | 3,19 | 0 | 5 | GEÇER, hata 0 |
| `carpisma_kos.py kontrol` | 3,19 | 0 | 0 | 17 dosyanın özeti kayıtla aynı |
| `regresyon.py --yazma` | 3,18 | 0 | 0 | GEÇER, 10 / 10 aynı |

Kabul ölçütleri (tam5 + dog7): ana adım 50 / 50, konsol 0, parça 1192 ↔ 1192, alt adım 71 / 71, her parça tek alt adımda; denetim
0 (ascii 0); ulaşılamaz 0; girilemez 0; uçuş yolu çarpışan 0 (istisna 58 = F10d'den 12 + F10f-K1 46) [düzeltildi, bkz.
§ Düzeltme turu 1: 46'lık geniş istisna "çarpışan 0"ı istisnayla sağlıyordu; şimdi 340 satır, çarpışan 0, istisna 22 = 12 + dar 10,
`istisna_bos` 0]; alt adım gerekçesiz gizli 0 (istisna 115 = 106 + F10f-K1 9) [9'u artık kimlik anahtarlı gerekçe, okur pikseli
§ Düzeltme turu 1'de]; yazdırma karesi 121, boş 0 (en düşük çizim oranı 0,0606, ana adım; alt adımlarda 0,1102);
telefon 360 px 0; kol_kablo GEÇTİ. Geometri: robot.glb ve robot-glb.js karması değişmedi (veri2 sonrası), parça kayıtlarında yalnız
26 cıvatanın `d` alanı (§2).

PDF önce / sonra: **69 → 74 sayfa** (devam sayfası 19 → 24), en küçük yazı **8,1 → 8,1 pt** (DOM ve PDF; alt sınır 8,0), boyut
12632 → 15941 kB.

## 8. İş 8: karelere bakış

Kendi gözümle baktığım son kareler (1400 × 900, `?adim=N.J&cekim=1`): 36.4 koyu, 36.5 açık, 40.3 açık, 41.4 koyu, 42.2 açık,
44.3 koyu, 48.2 koyu ve birleşik `F10f-goruntu-41.png` (açık + koyu, 41.2 / 41.4 / 41.5). Bunlarda yol baştan sona karede, uçlar
beklenen parçada, mini etiket "sağ · …" / "sol · …". Öbür 21 kare (son-*.png) çekildi ve birleşik görüntülere girdi, ama tek tek
bakılmadı; görünürlükleri yalnız `kablo_kare` ölçümüyle (§3) doğrulandı.

Önce / sonra: `planlama/d158/F10f-goruntu-{36,40,41,42,44,48}.png`. Satırlar açık ve koyu tema. İlk sütun önce: HEAD rehberinde ana
adım (o adımlarda kol kablosu yoktu). Öbür sütunlar sonra: yeni kablo alt adımları.

Bakarken gördüğüm, düzeltmediğim iki şey:
1. Lejantta "Kablo yolu" kırmızı kare, kol kabloları ise turuncu (servo) ve yeşil (uzatma) çiziliyor.
2. 36.4'te uzatma yeşili (`#0d8f6f`) yanındaki K2 demet şemasının camgöbeğine yakın. ΔE ölçülmedi.

[İkisi de düzeltildi, bkz. § Düzeltme turu 1, madde 6: lejantta kol şemaları kendi renk ve adıyla; uzatma `#dd00ff`, eski yeşil ↔
camgöbeği ΔE76 21 idi, yeni 141.]

## 9. Açık konular, karar bekleyenler

- **F10f-K1** (§2): 15 parça türünde parça uçuş yolu çarpışması ve 9 gizli parça. Ölçüm kaydı olarak istisnaya alındılar. Karar ve
  düzeltme gerekiyor; G4'te metin "önden radyal" diyor, uçuş yandan geliyor. [Düzeltildi, bkz. § Düzeltme turu 1: 11 tür rehberde
  düzeldi (G4 gövde ve kapak artık +z); 2 duruş türü ve 2 karar türü dar istisnada; 9 gizli parça kimlikli gerekçeyle.]
- Devir a: kol konumlarında okur pikseli eşiğin altında kalan parçalar. Açık temada 123, koyu temada 122 (bütün güvenli alanlar).
  Bilgi olarak raporlandı, düzeltilmedi.
- Devir b: derinlik ipucu yapılmadı (§4).
- Tasarımda tanımlı olmayan 5 yol parçası (§1); S2 lopu r_min bilgisi (§1).
- Lejant rengi ve renk yakınlığı (§8); ΔE ölçülmedi.
- Kendi hatam, bırakıldı: depo kökünde boş `rehber_metin.py` (0 bayt, 09:22). Bir yol hatasıyla oluştu, içerik yok, içe aktarmayı
  etkilemiyor. Brief silmeye izin vermediği için durdu; silinmesini öneriyorum.

## 10. Dokunulan dosyalar

- Yeni: `tasarim/freecad/rehber/rehber_kol_kablo.py`, `planlama/d158/F10f-dogrula.py`, `F10f-dogrula.json`, `F10f-gunluk.md`,
  `F10f-goruntu-{36,40,41,42,44,48}.png`.
- Değişen kod: `tasarim/freecad/rehber/rehber_metin.py`, `rehber_gorunum.py` (GRUP_ALAN `sema_yalniz`), `rehber_uret.py` (kol_kablo
  denetimi, sema_yalniz ana adım kuralı), `rehber_denetim.py` (ASCII izin listesi +32 kelime), `rehber/app.js`, `rehber/stil.css`.
- Üretilen: `rehber/veri/rehber-veri.json` / `.js`, `planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/*`
  (yeni alt adım kareleri dahil), `F10a-dogrula.json`, `F10d-dogrula.json`, `F10e-dogrula.json` (betikleri değişmedi).
- `FREECAD-KILIT.txt`: veri koşularında satır yazıldı, şimdi "boş".
- Dokunulmayan: model geometrisi, `arayuz.py`, `dirsek/`, `omuz/`, `F10a-goruntu-*.png`, F10e kanıt kareleri, dokunulmazlar listesi.
  `tasarim/freecad/kabuk/gorsel/*.png` ve `montaj/yerlesim-kontrol.json` önceden değişikti.

## § Düzeltme turu 1 (12.11)

Brief: `F10f-duzeltme-1-brief.md`, kontrol: `F10f-kontrol.md`. Tur iki parçada yapıldı. Ahmet'in isteğiyle ≈ 14:44'te en yakın
güvenli noktada durduruldu (o anki durum aşağıdaki "Durdurma notu"nda). Ahmet "devam" dedi, 18:18'de çalışma ağacı aynı bulunarak
devam edildi (18:27 başlangıç). Bu bölüm turun tamamını anlatır. Aşağıdaki sayılar, aksi yazılmadıkça, depodaki üretimden (uret1:
FreeCAD'li tam koşu, uret2: `--veri-yok`) ve zincirden (zin2) gelir. Durdurmadan önceki ölçümler veri kopyasında yapılmıştı; onlar
üretimle yeniden ölçüldü ve farkları yazıldı.

### Koşular

| Koşu | Komut | Boş bellek önce (GB) | Çıkış | Süre (s) | Sonuç |
| --- | --- | --- | --- | --- | --- |
| kk2 | `rehber_kol_kablo.py --yazma` (eski veride) | 2,56 | 2 | 39 | bağ işaretleri: uç 64 / 64, katı 0; metin eksik 8 / birim hatası 4, çünkü depodaki veri eski metni taşıyordu (beklenen) |
| uret1 | `rehber_uret.py` (FreeCAD veri; kilit satırı yazıldı, sonra "boş") | 2,57 | 2 | 2767 | yalnız `denetim` kaldı: ASCII kalıntı 19 (yeni metnin Türkçe harfi olmayan doğru kelimeleri; `rehber_denetim.ASCII_TAMAM`'a eklendi). Öbür her şey geçti |
| uret2 | `rehber_uret.py --veri-yok` | 3,39 | 0 | 2716 | ek kontrol sorunlu yok |
| zin2 | zincir | 2,75 | (durduruldu) | 581 + | F10f-dogrula çıkış 2: 41.4'te −45° yolunun tambur bağı ucu ortak kamerada 625ZZ dış bileziğin (p0122, 39,3 mm önde) arkasında, uç pikseli 0. Zincir F10e'deyken durduruldu (veri değişecekti) |
| hizli1 | `rehber_gorunum.py` + `F10f-dogrula.py --yalniz-kablo --el-yok` | 2,58 | 0 | 193 | 41.4 / 41.5 saydam listesine "625ZZ rulman" eklendi; kablo kare GEÇTİ |
| zin3 | `rehber_uret.py --veri-yok` + zincir, tek süreçte | 3,30 | 0 | 5476 | üretim çıkış 0 (2639 s), zincirin hepsi çıkış 0; koşu boyunca en az boş 1,00 GB |

Son üretim (zin3, uret2 ile aynı sayılar) kabul sayıları: ana adım 50 / 50, konsol 0, alt adım 71 / 71, her parça tek alt adımda; denetim ASCII 0, gruplama 0;
ulaşılamaz 0 (565 bağlantı); girilemez 0; **uçuş yolu 340 satır, çarpışan 0, istisna 22 (F10d'den 12 + dar 10), `istisna_bos` 0**;
perdelenme alt adım gerekçesiz gizli 0, istisna 115 (106 + kimlikli gerekçe 9); yazdırma karesi 121, boş 0; telefon 360 px 0;
PDF 74 sayfa, en küçük yazı 8,1 pt (DOM ve PDF), 16076 kB (önce 74 / 8,1 / 15941 kB); kol_kablo GEÇTİ (bölüm 32, uç 64 / 64, katı 0,
ulaşılamaz 0, metin 28 sayı, eksik 0, birim hatası 0, pin 0).

### Zincir (zin3)

| Komut | Boş bellek önce (GB) | Çıkış | Süre (s) | Sonuç |
| --- | --- | --- | --- | --- |
| `rehber_uret.py --veri-yok` | 3,23 | 0 | 2639 | ek kontrol sorunlu yok; uçuş 340 / çarpışan 0 / istisna 22; ulaşılamaz 0; gizli 0 (istisna 115) |
| `F10f-dogrula.py` | 2,70 | 0 | 581 | GEÇTİ: veri, sınama (katı, adım bağı, birim), kablo kare, sağ / sol, mini etiket; parça kare bilgi; gizli piksel 9 / 9 görünmüyor (bilgi) |
| `F10e-dogrula.py --goruntu-yok` | 2,64 | 0 | 990 | GEÇTİ (renk, ev, işaret 1280 / 1280); `renk_demo` KALDI (karar, F10e'den beri geçme şartında değil) |
| `F10d-dogrula.py --goruntu-yok` | 2,41 | 0 | 776 | GEÇTİ |
| `F10a-dogrula.py --kanit-yok` | 2,47 | 0 | 483 | GEÇTİ; mini 50 / 50, 360 px taşma 0 |
| `F9b-dogrula.py` | 2,33 | 0 | 6 | GEÇER, hata 0 |
| `carpisma_kos.py kontrol` | 2,31 | 0 | 0 | 17 dosyanın özeti kayıtla aynı |
| `regresyon.py --yazma` | 2,31 | 0 | 1 | GEÇER, kötüleşen yok |

### Madde durumu

| # | Madde | Durum |
| --- | --- | --- |
| 1 | Birim hatası | **Yapıldı, üretimle doğrulandı.** `metin_sayilar` (adım, sayı, birim, kaynak) döndürüyor; `metin_denetle` sayıyı kendi birimiyle arıyor, başka birimle (mm / ° / cm / derece) geçerse `birim_hata`, denetim kalır. G4 41.4 / 41.5 derece: "iç koşu (tamburdaki yay, tambur bağından U'ya) 125,3°", "dış koşu (duvar boyunca yay, U'dan duvar bağına) 10,2°", +135: 10,1° / 74,9°. Öbür sayılara birim: L 80 / 120 mm, 0…105°, 5…120°, −45…135°, S1 ≥ 120° iken S2 ≤ 117°, 6 × 5 mm, 12 × 6 mm, y −105 mm (ψ önekli sayılar açı, birimsiz). uret2: 28 sayı, eksik 0, birim hatası 0. Sınama `F10f-dogrula.py` `sinama()` "birim": 125,3° yerine "125,3 mm" yazılınca birim hatası yakalanıyor (değişen 1 sayı, birim hatası 1, denetim kaldı; sınama GEÇTİ). |
| 2 | F10f-K1 | **Yapıldı, üretimle doğrulandı.** (a) Dar istisna: `ucus_ok` parça kimliği anahtarlı `{id: {sinif, gerekce, engel: {engel id: derinlik + 0,5}}}`; yolun tamamı süpürülüyor (`rehber_giris.yon(tum=True)`, kayıtta `carpan_hepsi`); listede olmayan engel ya da daha derin çarpışma çarpışan sayılır; kullanılmayan anahtar `istisna_bos`, denetim kalır. Pay 0,5 mm (ışın aralığı h). (b) 11 tür rehberde düzeldi (yön, mesafe, birlikte uçma, yerinde); (c) 2 duruş türü dar istisnada, tasarım duruşu metinde; (d) 2 karar türü dar istisnada, karar notları aşağıda. (e) Sonuç tablosu ve 9 gizli parçanın okur pikseli aşağıda. |
| 3 | 41.4 / 41.5 | **Yapıldı.** İki uç duruş karesi aynı kamera ve yerleşimde (kadraj D 197, sağ sütun, ikisinde aynı), aynı renkte (`poz_a` = `poz_b` = uzatma menekşesi `#dd00ff`); öbür duruşun yolu soluk iz (grup `iz` alanı, app.js "iz": saydamlık 0,3, kadraja dahil; lejantta "(soluk: öbür uç duruş)"). Metindeki "Soluk iz … kamera ve renk iki karede aynı" cümlesi artık çizimle tutarlı (karelere baktım, iki tema). Ortak kamerada −45° yolunun tambur bağı ucu 625ZZ dış bileziğin arkasında kalıyordu (F10f-dogrula kablo kare, zin2); 41.4 / 41.5'te rulman da saydam çiziliyor, uç görünüyor. 41.2 / 41.3: S1 kablo tamburu ve kaset gövdesi kenar çizgisiyle (grup `kenar`, app.js `kenarKoy`), iki temada okunuyor. |
| 4 | Kablo metinleri tek sıra | **Yapıldı.** Metin döşeme sırası (F4 → G3 → G4 → H0a / H0c → H1) önceki parçadaki gibi; bölüm ↔ alt adım bağları bu sıraya göre gözden geçirildi, değişiklik gerekmedi: F4.4 / F4.5 gövde içi yol; G3.2 / G3.3 G2 → tambur bağı, S2 lopu, pencere → K, iki bağ işareti; G4.2 / G4.3 U-lopu + duvar → yarık (G3'te gevşek kalan parça); G4.4 / G4.5 uç duruşlar; H0a / H0c servo kabloları; H1.2 / H1.3 tüp içi, iki ek, birleşim → pencere. Alt adım başlıkları yolu pencereden tambura doğru adlandırıyor, metin tamburdan pencereye döşüyor; ikisi aynı yol, başlıklar değiştirilmedi. `rehber_kol_kablo.EL_YOK` kod metni artık yalnız kaynakta olanı söylüyor ("eşleşik JR çifti tüp içinde; takıldığı yer tasarımda tanımlı değil"; bilek lehimi için aynı); eski "JR pencerenin dışında takılır" kalktı. |
| 5 | S2 0° lopu | **Seçim: işaret + not (S2 5° çizimi değil).** S2 lopu kendi rengiyle (`uzatma_b` `#8a2be2`) ve kendi lejantıyla çiziliyor: "S2 lopu: çizim S2 0°, aralık dışı (tasarım S2 5…120°)"; şema adında "; çizim S2 0°, aralık dışı"; 40.2 metninde not. Gerekçe: S2 5° çizimi kaynaktaki `kablo_yolu.lop_coz`'u başka duruşta çözmek ve K / G2 uçlarını o duruşa taşımak demek; uçlar modeldeki (S2 0°) parçalara bağlı, karede parçalarla çelişirdi. Ölçüm: S2 5°'de r_min 12,73 mm (kaynak 12,36), sınır 11,2; S2 0°'de 6,3. |
| 6 | Kare okunurluğu | **Yapıldı.** Renk (ΔE76, CIE Lab D65): uzatma `#0d8f6f` → `#dd00ff`. Eski uzatma ↔ K2 camgöbeği `#00a3a3` 21; yeni uzatma ↔ camgöbeği 141, ↔ EV pembesi 62, ↔ rehberdeki en yakın renk (`#6c5ce7`) 51, ↔ iki zemin 121 / 125. Kol renkleri arası: uzatma ↔ S2 lopu `#8a2be2` 27, servo `#c47a00` ↔ bilek eki `#ffd400` 42, dirsek eki `#1a1a1a` ↔ bilek eki 116, kablo bağı `#ffffff` ↔ uzatma 125; öbür çiftler ≥ 80. 40.2 / 40.3: S2 lopu ayrı renk, K noktası ve tambur bağı beyaz bağ işareti (4 mm, kablonun üstünde). 48.2 / 48.3: dirsek eki siyah, bilek eki sarı, üst kol tüpü kenar çizgili. Lejant: kol şemaları kendi renk ve adıyla ("Kablo yolu" kırmızı kare kalktı), kutular ince gri çerçeveli (beyaz / sarı açık zeminde de görünsün). Okurluk (kendi gözümle, 14 kablo karesi × 2 tema): anlaşılmıyor 0, zor 3 / 14. |
| 7 | Günlük | Bu bölüm; eski iddiaların yanına "düzeltildi, bkz. § Düzeltme turu 1" notları düşüldü (§1 metin denetimi, F10f-K1 bölümü, kabul satırı). |

### F10f-K1 sonuç tablosu (46 satır)

Önce: F10f ilk tur verisi (5831e2f), kopya ölçümü `rehber_sira.ucus_yolu` (tam süpürme). Sonra: uret2 (340 satırlık ölçüm,
çarpışan 0; istisna listesinde olmayan satır temizdir). "Ev sahibiyle": parça artık kendi satırında uçmuyor (veride `h`), ev sahibinin
satırı temiz. Derinlikler mm (ortak hacim, h 0,5).

**Özet: 46 → temiz 24, ev sahibiyle 12, dar istisna 10 (karar 6, duruş 4).**

| Alt adım | Parça | Önce (u, d) | Önce engel / derinlik | Sonra |
| --- | --- | --- | --- | --- |
| 40.1 | p0119 S2 horn 25T alüminyum disk | u [0.992, 0, 0.128], d 40.0 | p0106 4.91 | temiz: u [0, 0, 1.0], d 40.0 |
| 40.1 | p0192 S2 horn 25T alüminyum disk | u [-0.992, 0, 0.128], d 40.0 | p0179 4.91 | temiz: u [-0, 0, 1.0], d 40.0 |
| 40.1 | p0121 Kol çatalı | u [0, 0, 1.0], d 56.9 | p0105 30.98, p0119 19.09, p0108 7, p0110 7, p0107 6.98, p0109 6.98 | dar istisna (karar): yön [1, 0, 0], 625ZZ rulman (iç bilezik) [p0116] 5.0 |
| 40.1 | p0194 Kol çatalı | u [0, 0, 1.0], d 56.9 | p0178 30.98, p0192 19.09, p0181 7, p0183 7, p0180 6.98, p0182 6.98 | dar istisna (karar): yön [-1, 0, 0], 625ZZ rulman (iç bilezik) [p0189] 5.0 |
| 40.1 | p0122 625ZZ rulman (dış bilezik) | u [0.987, 0, -0.163], d 40.0 | p0118 8.44, p0117 7.97, p0116 6.42 | dar istisna (karar): yön [4, 0, -1], Mafsal pulu M5 [p0117] 4.19 |
| 40.1 | p0195 625ZZ rulman (dış bilezik) | u [-0.987, 0, -0.163], d 40.0 | p0191 8.44, p0190 7.97, p0189 6.42 | dar istisna (karar): yön [-4, 0, -1], Mafsal pulu M5 [p0190] 0.24 |
| 40.1 | p0127 Üst kol tüpü | u [1, 0, -0.007], d 76.1 | p0121 22.4, p0130 2.83, p0128 2.83 | temiz: u [0, -1, 0.0], d 76.1 |
| 40.1 | p0200 Üst kol tüpü | u [-1, 0, -0.007], d 76.1 | p0194 22.51, p0203 2.83, p0201 2.83 | temiz: u [-0, -1, 0.0], d 76.1 |
| 41.1 | p0232 S1 kaset gövdesi sağ | u [1, 0, 0.0], d 75.7 | p0127 34.57, p0121 22.56, p0129 11, p0128 5.7 | temiz: u [0, 0, 1.0], d 75.7 |
| 41.1 | p0234 S1 kaset gövdesi sol | u [-1, 0, 0.0], d 75.7 | p0200 34.57, p0194 22.56, p0202 11, p0201 5.7 | temiz: u [-0, 0, 1.0], d 75.7 |
| 41.6 | p0233 S1 kaset kapağı sağ | u [1, 0, 0.0], d 75.7 | p0121 22.34, p0129 9.19, p0128 3.8 | dar istisna (duruş): yön [0, 0, 1], S1 kaset gövdesi sağ [p0232] 3.01 |
| 41.6 | p0235 S1 kaset kapağı sol | u [-1, 0, 0.0], d 75.7 | p0194 22.3, p0202 9.19, p0201 3.8 | dar istisna (duruş): yön [0, 0, 1], S1 kaset gövdesi sol [p0234] 3.01 |
| 41.6 | p0463 Kaset cıvatası M3x8 (sağ ψ 200) | u [1, -0, -0.0], d 100.7 | p0121 11, p0127 5.46, p0129 2.98, p0128 2.6 | dar istisna (duruş): yön [1, 0, 0], Üst kol tüpü [p0127] 1.47 |
| 41.6 | p0467 Kaset cıvatası M3x8 (sol ψ 200) | u [-1, -0, -0.0], d 100.7 | p0194 11, p0200 5.46, p0202 2.98, p0201 2.6 | dar istisna (duruş): yön [-1, 0, 0], Üst kol tüpü [p0200] 0.31 |
| 42.1 | p0587 Dirsek servosu MG996R | u [1, 0, 0.0], d 40.0 | p0582 4.95 | temiz: u [0, 0, -1.0], d 40.0 |
| 42.1 | p0644 Dirsek servosu MG996R | u [-1, 0, 0.0], d 40.0 | p0639 4.95 | temiz: u [-0, 0, -1.0], d 40.0 |
| 42.1 | p0598 Bilek servosu çıkış mili | u [0, 1, 0.0], d 40.0 | p0597 12.59 | ev sahibiyle uçar (p0597, Bilek servosu MG996R) |
| 42.1 | p0655 Bilek servosu çıkış mili | u [0, 1, 0.0], d 40.0 | p0654 12.59 | ev sahibiyle uçar (p0654, Bilek servosu MG996R) |
| 42.1 | p0590 Dirsek servosu kontra somunu M4 | u [-1, 0, 0.0], d 25.0 | p0582 6.78 | temiz: u [-1, 0, 0.0], d 15.0 |
| 42.1 | p0592 Dirsek servosu kontra somunu M4 | u [-1, 0, 0.0], d 25.0 | p0582 6.78 | temiz: u [-1, 0, 0.0], d 15.0 |
| 42.1 | p0594 Dirsek servosu kontra somunu M4 | u [-1, 0, 0.0], d 25.0 | p0582 6.78 | temiz: u [-1, 0, 0.0], d 15.0 |
| 42.1 | p0596 Dirsek servosu kontra somunu M4 | u [-1, 0, 0.0], d 25.0 | p0582 6.78 | temiz: u [-1, 0, 0.0], d 15.0 |
| 42.1 | p0647 Dirsek servosu kontra somunu M4 | u [1, 0, 0.0], d 25.0 | p0639 6.78 | temiz: u [1, 0, 0.0], d 15.0 |
| 42.1 | p0649 Dirsek servosu kontra somunu M4 | u [1, 0, 0.0], d 25.0 | p0639 6.78 | temiz: u [1, 0, 0.0], d 15.0 |
| 42.1 | p0651 Dirsek servosu kontra somunu M4 | u [1, 0, 0.0], d 25.0 | p0639 6.78 | temiz: u [1, 0, 0.0], d 15.0 |
| 42.1 | p0653 Dirsek servosu kontra somunu M4 | u [1, 0, 0.0], d 25.0 | p0639 6.78 | temiz: u [1, 0, 0.0], d 15.0 |
| 44.1 | p0562 Dirsek çatalı | u [-1, 0, 0.0], d 63.5 | p0582 33.38, p0587 30.53, p0572 19.49, p0588 8.93, p0595 8, p0593 8, p0596 6.78, p0594 6.78 | dar istisna (karar): yön [0, 1, 0], Dirsek horn merkez vidası M3 [p0573] 3.0 |
| 44.1 | p0619 Dirsek çatalı | u [1, 0, 0.0], d 63.5 | p0639 33.38, p0644 30.53, p0629 19.49, p0645 8.93, p0652 8, p0650 8, p0651 6.78, p0653 6.78 | dar istisna (karar): yön [0, 1, 0], Dirsek horn merkez vidası M3 [p0630] 3.0 |
| 44.1 | p0583 625ZZ rulman (iç bilezik) | u [0, 1, 0.0], d 40.0 | p0571 6.18, p0562 6.18 | ev sahibiyle uçar (p0571, 625ZZ rulman (dış bilezik)) |
| 44.1 | p0640 625ZZ rulman (iç bilezik) | u [0, 1, 0.0], d 40.0 | p0628 6.18, p0619 6.18 | ev sahibiyle uçar (p0628, 625ZZ rulman (dış bilezik)) |
| 44.1 | p0575 Çatal-horn pulu M3 (2x DIN 125-A) | u [-1, 0, 0.0], d 25.0 | p0572 6.13, p0587 6.13, p0562 6.02, p0588 1.93 | ev sahibiyle uçar (p0574, Çatal-horn cıvatası M3x12) |
| 44.1 | p0577 Çatal-horn pulu M3 (2x DIN 125-A) | u [-1, 0, 0.0], d 25.0 | p0572 6.13, p0587 6.13, p0562 6.04, p0588 1.92 | ev sahibiyle uçar (p0576, Çatal-horn cıvatası M3x12) |
| 44.1 | p0579 Çatal-horn pulu M3 (2x DIN 125-A) | u [-1, 0, 0.0], d 25.0 | p0562 6.1, p0572 6.1, p0587 6.1, p0588 1.92 | ev sahibiyle uçar (p0578, Çatal-horn cıvatası M3x12) |
| 44.1 | p0581 Çatal-horn pulu M3 (2x DIN 125-A) | u [-1, 0, 0.0], d 25.0 | p0562 6.1, p0572 6.1, p0587 6.1, p0588 1.94 | ev sahibiyle uçar (p0580, Çatal-horn cıvatası M3x12) |
| 44.1 | p0632 Çatal-horn pulu M3 (2x DIN 125-A) | u [1, 0, 0.0], d 25.0 | p0629 6.13, p0644 6.13, p0619 6.02, p0645 1.93 | ev sahibiyle uçar (p0631, Çatal-horn cıvatası M3x12) |
| 44.1 | p0634 Çatal-horn pulu M3 (2x DIN 125-A) | u [1, 0, 0.0], d 25.0 | p0629 6.13, p0644 6.13, p0619 6.04, p0645 1.92 | ev sahibiyle uçar (p0633, Çatal-horn cıvatası M3x12) |
| 44.1 | p0636 Çatal-horn pulu M3 (2x DIN 125-A) | u [1, 0, 0.0], d 25.0 | p0619 6.1, p0629 6.1, p0644 6.1, p0645 1.92 | ev sahibiyle uçar (p0635, Çatal-horn cıvatası M3x12) |
| 44.1 | p0638 Çatal-horn pulu M3 (2x DIN 125-A) | u [1, 0, 0.0], d 25.0 | p0619 6.1, p0629 6.1, p0644 6.1, p0645 1.94 | ev sahibiyle uçar (p0637, Çatal-horn cıvatası M3x12) |
| 48.4 | p0565 Bilezik pulu M3 (somun) | u [1, -0, -0.0], d 25.0 | p0562 6.03 | temiz: u [-1, 0, 0.0], d 25.0 |
| 48.4 | p0569 Bilezik pulu M3 (somun) | u [1, -0, -0.0], d 25.0 | p0562 6.03 | temiz: u [-1, 0, 0.0], d 25.0 |
| 48.4 | p0622 Bilezik pulu M3 (somun) | u [-1, -0, -0.0], d 25.0 | p0619 6.03 | temiz: u [1, 0, 0.0], d 25.0 |
| 48.4 | p0626 Bilezik pulu M3 (somun) | u [-1, -0, -0.0], d 25.0 | p0619 6.03 | temiz: u [1, 0, 0.0], d 25.0 |
| 48.4 | p0566 Bilezik kontra somunu M3 | u [-1, 0, 0.0], d 25.0 | p0213 5.16 | temiz: u [-1, 0, 0.0], d 20.0 |
| 48.4 | p0570 Bilezik kontra somunu M3 | u [-1, 0, 0.0], d 25.0 | p0213 5.16 | temiz: u [-1, 0, 0.0], d 20.0 |
| 48.4 | p0623 Bilezik kontra somunu M3 | u [1, 0, 0.0], d 25.0 | p0214 5.16 | temiz: u [1, 0, 0.0], d 20.0 |
| 48.4 | p0627 Bilezik kontra somunu M3 | u [1, 0, 0.0], d 25.0 | p0214 5.16 | temiz: u [1, 0, 0.0], d 20.0 |

Dar istisnaların izin verdiği engel ve derinlikler (+0,5 pay ayrıca): p0121 / p0194 iç bilezik 6,42, mafsal cıvatası 5,0; p0122 /
p0195 mafsal cıvatası 8,44, pul 7,97, iç bilezik 6,42; p0233 / p0235 kaset gövdesi 4,2; p0463 / p0467 kol çatalı 11,0, tüp 5,46,
tüp cıvatası 2,98, ısıl gömme 2,6; p0562 / p0619 horn merkez vidası 5,46. Kaset cıvatasının gerçek d'si üretimde 27,5 mm (kopyadaki
varsayım tuttu); `istisna_bos` 0.

Duruş (madde 2c): kapak ve ψ 200 cıvatası rehberde modeldeki duruşta (S1 0°, S2 0°) çiziliyor; tasarımdaki takma duruşu metinde
(41.1 / 41.6 / G4 d): cıvata S1 −45 / −20 / 0 × S2 90'da düz +x yolu temiz; kapak iki parçalı yol (önden x +3,3 havada, sonra −x 3,3)
S2 30'da temiz (S1 0 ve −45), S2 0'da itme kol çatalına değiyor (16,2 / 12,9). Duruşu çizmek denenmedi.

### 9 gizli parça (perdelenme, kimlik anahtarlı gerekçe)

Gizli kalmalarının nedeni yerleri (ön kol / çatal / bilezik içinde), uçuş değil: kopyada ve üretimde aynı 9 parça. Okur pikseli
(`F10f-dogrula.py gizli_piksel`, iki tema, parçanın kendi alt adımında; görünürlük = boyanınca değişen piksel, fark = parça yokken
karşılaştırma):

| Alt adım | Parça | Açık: fark / yalnız (px) | Koyu: fark / yalnız (px) |
| --- | --- | --- | --- |
| 42.1 | p0590 Dirsek servosu kontra somunu M4 | 0 / 361 | 0 / 361 |
| 42.1 | p0647 Dirsek servosu kontra somunu M4 | 0 / 205 | 0 / 205 |
| 42.1 | p0649 Dirsek servosu kontra somunu M4 | 0 / 201 | 0 / 201 |
| 44.1 | p0583 625ZZ rulman (iç bilezik) | 0 / 373 | 0 / 373 |
| 44.1 | p0628 625ZZ rulman (dış bilezik) | 16 / 561 | 22 / 561 |
| 44.1 | p0640 625ZZ rulman (iç bilezik) | 0 / 246 | 0 / 246 |
| 44.1 | p0584 Pim pulu M5 | 0 / 218 | 0 / 218 |
| 44.1 | p0641 Pim pulu M5 | 6 / 189 | 9 / 189 |
| 48.4 | p0569 Bilezik pulu M3 (somun) | 0 / 96 | 0 / 96 |

"Yalnız": parça tek başına çizilince kaplayacağı piksel; "fark": karede parça varken / yokken değişen piksel (alan "hepsi"; "sütun"
alanı aynı). Ölçüt ≥ 30 px ve ≥ 0,20 × yalnız: 9'unun 9'u iki temada da okura görünmüyor (en çok 22 px, p0628 koyu). Gerekçeleri
`rehber_metin` `gizli()` ile kimlik anahtarlı yazıldı (26 yönde dik izdüşümde yerindeyken görünmez; nerede olduğu yazılı; okur onu
sıralı takmada yerine giderken görür). Bu ölçüm bilgi amaçlı, `gecti` alanı yok (None).

### Karar notları

Sıra ve parça ↔ adım ataması değişmedi; karar-kuyrugu.md'ye dokunulmadı. İki tür dar istisnada ("karar bekliyor").

- **K1-a (40.1 kol çatalı + 625ZZ dış bilezik).**
  - Durum: iç bilezik, mafsal pulu ve mafsal cıvatası G2'de takılı (adım 39). Kol çatalı 26 tam sayı yönün hiçbirinden gelemiyor
    (kontrol B); +x'te yalnız iç bilezik (6,42) ve mafsal cıvatası (5,0) engel. Rehber şimdi +x (sağ) / −x (sol) kullanıyor.
  - Seçenek A (B'nin önerisi; iç bilezik + pul + cıvata aynı alt adımda çataldan sonra): iç bilezik bu kez dış bileziğe 6,38, çatala
    6,33 çarpıyor.
  - Seçenek A' (A + rulman tek parça, iç bilezik dış bilezikle birlikte): dış bilezik çatala 6,3–6,4 çarpıyor (eğik, +x ve −x yolların
    hepsinde).
  - Seçenek C (rulman çatala önceden preslenir, iki bilezik çatalla birlikte uçar; pul + mafsal cıvatası 40.1'de çataldan sonra):
    **temiz** (çatal +x ya da −y).
  - C'nin değiştirdikleri: rehberde parça ataması 39 → 40 (iç bilezik, pul, cıvata) ve G2 / G3 metni; tasarım belgelerinde montaj
    sırası (G2 "karşı tarafa 625ZZ ve M5 pim").
  - Öneri: C. Ölçümler veri kopyasında (scratchpad, depoya yazmayan betik).
- **K1-b (44.1 dirsek çatalı ↔ horn merkez vidası).**
  - Durum: vida H0b'de takılı (adım 43); çatal +y ve ±z yollarında vida başına 5,46 çarpıyor. Rehber şimdi +y.
  - Seçenek: vida 44.1'e, çataldan sonraya. Çatal temiz, vidanın +x yolu da temiz.
  - Değiştirdikleri: H0b metni ("Çataldan önce"), parça ataması 43 → 44, dirsek montaj sırası.
  - Öneri: bu seçenek. Çatal takılıyken vidanın horna erişimi yalnız düz yolla ölçüldü; alet erişimi ölçülmedi.

### Karelere bakış

Önce: `scratchpad f10f-d1/kare/once-*` (durdurmadan önce, eski veri + eski app.js). Sonra: uret2 verisi + son app.js, 1400 × 900,
`?adim=N.J&cekim=1`, iki tema. Kendi gözümle baktıklarım: 14 kablo karesinin 28'i (36.4, 36.5, 40.2, 40.3, 41.2–41.5, 42.2, 42.3,
44.2, 44.3, 48.2, 48.3; tam boy ya da altılı paftada) ve 40.1, 41.1, 41.6, 42.1, 44.1, 48.4 iki temada (paftada): hepsi çiziliyor, boş
ya da kayık yok.

| Kare | Kontrol B (önce) | Sonra (açık / koyu) | Not |
| --- | --- | --- | --- |
| 36.4, 36.5 | zor | anlaşılır / anlaşılır | menekşe uzatma opak; K2 demeti saydam ve ayrı renkte |
| 40.2, 40.3 | zor | anlaşılır / anlaşılır | S2 lopu ayrı renk ve lejant notu; K ve tambur bağı beyaz işaret |
| 41.2 | zor | anlaşılır / anlaşılır | tambur ve kaset duvarı kenar çizgili |
| 41.3 | zor | zor / anlaşılır | açık temada duvar kenarı soluk |
| 41.4, 41.5 | zor; kıyas anlaşılmıyor | anlaşılır / anlaşılır; kıyas anlaşılır | aynı kamera ve renk, öbür duruş soluk iz; ortak kısımda iz yolun altında kalıyor |
| 42.2, 42.3, 44.2, 44.3 | (bulgu yok) | anlaşılır / anlaşılır | değişmedi (servo turuncusu) |
| 48.2, 48.3 | zor | anlaşılır / zor | iki ek iki renk; koyu temada siyah JR koyu zeminde zayıf |

Sayım (karenin iki temasından kötüsü): anlaşılmıyor 0, zor 3 / 14 (41.3, 48.2, 48.3), hedef ≤ 4. Kontrol B'de: zor 10, kıyas
anlaşılmıyor 1. Bu değerlendirme benim gözümle; bağımsız bakış değil.
> **Not (düzeltme turu 2):** B2 aynı kareleri zor 5 / 14 saydı (41.3 açık, 41.4, 41.5, 48.2, 48.3); bu "zor 3" tutmadı. Tur 2 sonrası
> yeniden sınıflama aşağıda, § Düzeltme turu 2 → Madde 3.

Önce / sonra görüntüleri: `planlama/d158/F10f-goruntu-d1-{36,40,41,48}.png` (sütunlar alt adım × önce / sonra, satırlar açık / koyu; 41: 41.2, 41.4, 41.5).

### Değişen dosyalar (bu tur)

| Dosya | Değişiklik |
| --- | --- |
| `tasarim/freecad/rehber/rehber_giris.py` | yolun tamamını süpürme (`tum`) |
| `rehber_sira.py` | dar istisna, `istisna_bos`, gizli_ok kimlikle eşleşme |
| `rehber_veri.py` | yerinde / `ucus_d` / `ucus_ters` / `birlikte`; grup `kenar` |
| `rehber_gorunum.py` | `alan_isle` grup `kenar` |
| `rehber_metin.py` | `f10f_k1` yerine `dar()` / `gizli()`; grup yönleri; metin, birimler, bağ / iz / kenar alanları; 41.4 / 41.5 saydam + 625ZZ |
| `rehber_kol_kablo.py` | birimli metin denetimi; renkler, lejant, bağ işaretleri, `iz`; EL_YOK metni |
| `rehber_denetim.py` | ASCII izin listesi +19 kelime (gözden geçirildi) |
| `rehber/app.js` | `tak()` birlikte uçan parça; `iz` (soluk öbür duruş), `kenar`, kol şeması lejantı |
| `planlama/d158/F10f-dogrula.py` | birim sınaması, `gizli_piksel`, "sonra" kontrolü öbür duruş karesinde "iz" kabul |
| üretilenler | `rehber/veri/rehber-veri.json` / `.js` (`robot.glb` / `robot-glb.js` FreeCAD koşusundan sonra HEAD ile bayt bayt aynı: git karması eşit), `planlama/rehber/kontrol.json`, kareler, PDF, `F10*-dogrula.json`, `F10f-goruntu-d1-*.png` |

`FREECAD-KILIT.txt`: uret1'de satır yazıldı, FreeCAD aşaması bitince "boş". Dokunulmayan: model geometrisi, `arayuz.py`, `dirsek/`,
`omuz/`, dokunulmazlar listesi, depo kökündeki boş `rehber_metin.py`.

### Yapılamayan / açık kalan

- K1-a ve K1-b karar bekliyor (dar istisnada); duruş iki türü çizilmedi, metinde.
- 41.3 (açık tema) ve 48.2 / 48.3 (koyu tema, siyah JR) kendi değerlendirmemde "zor"; bağımsız bakış yapılmadı.
  (Not, tur 2: B2 ayrıca 41.4 / 41.5'i zor saydı; tur 2 sınıflaması § Düzeltme turu 2 → Madde 3.)
- Okurluk değerlendirmesi ve 41.2–41.5 duvar / tambur okunurluğu yalnız göz; ölçülmedi.
- Kablonun elle döşenmesi, alet erişimi (K1-b vidası) ölçülmedi.

### Durdurma notu (14:44, değiştirilmeden özet)

Durdurulduğunda madde 1, 2 (a–d) kod ve metin olarak bitmiş, üretim ve zincir koşulmamıştı; madde 3'te yalnız metin vardı (çizimle
tutarsız), madde 6 başlanmamıştı, eski iddialara not düşülmemişti. Ölçümler veri kopyasındaydı. Devamda bu eksikler yukarıdaki gibi
kapandı.

## § Düzeltme turu 2 (brief `F10f-duzeltme-2-brief.md`, B2 raporu `F10f-kontrol-2.md`)

### Bellek nedeniyle durma notu (12.11.2026 22:52)

Ağır komut öncesi boş bellek 1,90 GB idi; kurala göre arayla üç kez daha ölçüldü: 1,92 / 1,91 / 1,69 GB (hepsi 2 GB altı). Bu
yüzden simülasyon, FreeCAD veri koşusu, tam üretim, zincir ve kare çekimi **başlatılmadı**. Arkada süreç yok. Bu turdaki ölçüm
sayılarının hepsi (1b önce / sonra, etkilenen konumlar, okunurluk sınıflaması, PDF) **ölçülmedi**.

Kodda biten (py_compile / node --check geçti, üretimle denenmedi):
- 1a: H0c.1'de 625ZZ dış / iç bilezik çatalla birlikte uçuyor (`birlikte`); metin rulmanın tezgâhta çatala önceden bastırıldığını
  söylüyor. Kaynak: `dirsek_rapor` SIRA adım 2 (rulman, çatal ön kola katılmadan yuvaya bastırılır). K1-b notuna ölçüm eklenmedi
  (simülasyon koşulmadı).
- 1b: `rehber_giris.yon / yon_gercek` duruşta örtüşen çifti artık dışarıda bırakmıyor; eşik = duruş derinliği + `DINLENME_PAY`
  0,5 mm (`rehber_sira.py`). `KOL_ADIM` = {36, 39–48}. "ölçüm kaydı" sınıflı istisnalar `olcum_kaydi` alanında listelenir.
  Bütün rehber koşusu yapılmadı: yeni satır listesi yok.
- 1c: yapılmadı (sınama koşusu ağır).
- 2: `app.js` patlatmada d ≤ 0 yeni parçalar (renkli vurgu değilse) yerinde çiziliyor (`x.yerinde`); ev sahibinin bayrağı konuklara
  geçer. Etkilenebilecek adımlar (d ≤ 0 parçası olan): 4 B1a, 12 B5a, 14 B6a, 19 D1a, 23 E1a, 29 E3a, 37 G0, 42 H0a ve alt adımları.
  Ekran farkı sayımı ve adım 0 47 / 58 px nedeni: yapılmadı.
- 3: 41.4 / 41.5 tambur + kaset kenarı, p0118 mafsal cıvatası saydam; 48.2 / 48.3 iki ek arası bilek uzatma parçası (`tup_ara`,
  uzatma rengi) ve lehim / JR ek işaretleri (`nokta_lehim`, `nokta_jr`, beyaz); grup kenarı açık temada siyah (41.3). Sınıflama
  yapılmadı; "zor 3" iddiasına düzeltme notu kare bakışından sonra düşülecek.
- 4: 40.2 / 41.2 S2 uzatma ucu metni düzeltildi; F4 madde 2 okur diline çevrildi; dize istisna anahtarı (M8) kullanılmazsa ya da kol
  adımındaysa `bos`'a giriyor; metin denetimi: G4 iç / dış koşu etiket eşlemesi (T4, `etiket_hata`), "m" / "rad" birim sayılıyor
  (T9), "L 171,4 mm (−5…0 mm)" ve denetimde L_tol girdisi. Scratchpad bozma sınaması (eski veri, G4 metni değiştirilerek): T4 takası
  iki uçta da 2 etiket_hata, T9 "125,3 m" ve "74,9 rad" 1'er birim_hata; eski metinde tolerans birimsiz olduğu için 1 eksik
  (yeni metinle 0). PDF lejantı: yapılmadı.

### Devam (13.11.2026, yeniden başlatma sonrası)

Yukarıdaki durma notu değiştirilmedi; "ölçülmedi" dediği sayılar aşağıda ölçüldü. Önceki ajanın kodu okunarak gözden geçirildi
(`rehber_giris._dinlenme_suz`, `rehber_sira` M8 / `olcum_kaydi`, `rehber_kol_kablo`, `app.js` `yerinde` / `grupKenar`, H0c metni:
`dirsek_rapor` SIRA 2 ile karşılaştırıldı, doğru).

#### Koşular

Hepsi scratchpad sarmalayıcısıyla (`baslat` belleği ölçer, < 2 GB ya da arkada chrome / ≥ 300 MB python varsa başlatmaz; bekçi 15 s'de
bir ölçer). Aynı anda tek ağır süreç.

| Koşu | Ne | Başlarken boş bellek | Süre | Çıkış |
| --- | --- | --- | --- | --- |
| simE | bütün rehber uçuş denetimi, **eski** kural (`DINLENME_PAY` yok), tur 1 verisi (kopya) | 7,10 GB | 1012 s | 0 |
| simY | aynı, yeni kural + 44.1 rulman düzeltmesi (kopya) | 6,96 GB | 1005 s | 0 |
| simK40 | adım 40 ve 44, 40.1 düzeltmesi (kopya) | — | 6 s | 0 |
| simS | adım 31, 36, 40, 44, son metin (kopya) | — | 116 s | 0 |
| sin1 | `F10f-dogrula` sınaması (madde 1c dahil) | 7,44 GB | 18 s | 0 |
| uret1 | `rehber_uret` FreeCAD'li veri + tam üretim | 6,78 GB | 2554 s (veri 173 s) | 2 (yalnız ASCII kalıntı 8) |
| zin1 | `rehber_uret --veri-yok` + 7 komut | 7,41 GB | 4990 s | hepsi 0 |
| pf1 | patlatma ekran farkı, 120 konum × 2 tema | 7,32 GB | 861 s | 0 |
| pf2 | aynı, 9 değişen konum, saydam düzeltmeden sonra | (tarayıcı, kısa) | ≈ 1 dk | 0 |
| zin2 | `app.js` saydam düzeltmesinden sonra zincirin tekrarı | 6,99 GB | 4983 s | hepsi 0 |

FreeCAD kilidi: uret1'de 02:53'te yazıldı, veri bitince 02:57'de "boş". Başka koşuda FreeCAD yok.

#### Madde 1a (44.1 rulman) ve K1 notları

- H0c.1: 625ZZ dış / iç bilezik dirsek çatalıyla birlikte uçuyor (önceki ajan; doğrulandı). Eski yönle (dış bilezik sağ −x / sol +x,
  d 40, ayrı) yeni kural iki bileziği dirsek çatalıyla **8,67 mm** ortak hacimde çarpışan sayıyor; birlikte uçunca 0.
- **K1-b notuna ölçüm:** üretimde p0562 (çatal + iki bilezik, +y, d 63,5) yalnız p0573 horn merkez vidasına değiyor: ortak hacim
  derinliği 5,46 mm (ilk temas 3,0 mm'de). Rulman çatala eklenince yeni engel çıkmadı. Dar istisna (karar) sürüyor.
- **K1-a notuna ekleme:** yeni kural 40.1'de de bir sorun çıkardı: dış bilezik (p0122 / p0195) kol çatalıyla 9,27 / 9,19 mm örtüşüyor
  (eski kural bu duruş çiftini sayımdan atıyordu). Düzeltme: dış bilezik kol çatalıyla `birlikte` (kaynak `omuz_rapor` SIRA 2 "625ZZ'yi
  çatalın arka koluna bastır"); metin "tezgâhta önceden bastırılır, çatalla birlikte gelir". Bu, K1-a seçenek C'nin rulman kısmıdır;
  iç bilezik / pul / cıvatanın adım ataması **değişmedi** (39'da). Çatal satırının engelleri değişmedi (iç bilezik 6,42, cıvata 5,0;
  K1-a dar izni içinde). p0122 / p0195'in artık kullanılmayan dar anahtarları kaldırıldı.

#### Madde 1b: bütün rehber, önce / sonra

| Durum | Satır | Çarpışan | İstisna | istisna_bos | Ölçüm kaydı |
| --- | --- | --- | --- | --- | --- |
| Önce: eski kural, tur 1 verisi (simE) | 340 | 0 | 22 | 2 (\*) | 0 |
| Sonra: son üretim (zin1, `kontrol.json`) | 336 | 0 | 20 | 0 | 1 |

(\*) Eski kural + yeni M8 kuralı: 36.1 / 36.2'deki dize anahtarlar ("Omuz bandı sağ / sol") kol adımında olduğu için `bos`'a girdi.
Satır sayısı 340 → 336: 40.1 ve 44.1'de birlikte uçan 4 parça kendi satırını kaybetti (ev sahibinin satırında uçuyor).

Yeni kuralın düzeltmesiz ortaya çıkardığı satırlar (simE ↔ simY / simK40 karşılaştırması):
- Kol adımlarında **4**: 44.1 p0571 / p0628 (625ZZ dış bilezik, dirsek çatalı 8,67 mm; önce temizdi), 40.1 p0122 / p0195 (kol çatalı
  9,27 / 9,19 mm; önce K1-a dar istisnasındaydı, yeni engel izni aştı). Dördü de `birlikte` ile düzeldi; kol adımında yeni istisna **0**.
- Kol dışında **1**: 31.6 p0798 kamera, yeni engel yüz kabuğu (ön) sağ p0750 7,95 mm (eski engel p0763 2,91 mm). Satır zaten F10d dize
  istisnasındaydı; düzeltilmedi, "ölçüm kaydı" sınıflı dar anahtara çevrildi. `kontrol.json` → `sira.ucus.olcum_kaydi` içinde listeli.
- Son istisna dağılımı (20): dize 9 (kol dışı, F10d), karar 4, duruş 4, yol 2, ölçüm kaydı 1. Kol adımlarında istisna 10
  (36.1–2 yol, 40.1 karar × 2, 41.6 duruş × 4, 44.1 karar × 2); kol adımında dize anahtar 0.
- 36.1 / 36.2 "Omuz bandı" dize anahtarları dar ve "yol" sınıfına çevrildi (gerekçe aynı F10d giriş yolu ölçümü; engeller: sağ
  p0213 75,0, p0078 25,25, p0070 10,0, p0287 / p0289 2,57; sol p0214 63,0, p0151 25,25, p0143 10,0, p0291 / p0293 2,57; izin +0,5).
- Ölçülmedi: B2'nin nokta–üçgen ölçümü (44.1 için 1,55 mm) ile bu denetimin ışın derinliği (8,67 mm) arasındaki farkın ayrıntısı;
  iki yöntem aynı çifti çarpışan buluyor, derinlik tanımları farklı.

#### Madde 1c: sınama

`F10f-dogrula.py` → `sinama()` içine kalıcı `dinlenme` alt sınaması (`sinama_dinlenme`): veri kopyasında 44.1'e eski 625ZZ yönü geri
konur (dış bilezik sağ −x / sol +x, d 40, ayrı uçar; iç bilezik onunla), `ucus_yolu([44])` yeni pay ile ve `DINLENME_PAY = None` ile
koşulur. Geçme şartı: yeni kural iki bileziği dirsek çatalıyla çarpışan sayar, eski kural saymaz. sin1: yeni kural 2 bilezik / 8,67 mm,
eski kural 0 → **geçti**. Aynı koşuda: etiket takası (125,3° ↔ 10,2°) 2 `etiket_hata`, "125,3° (125,3 m)" 1 `birim_hata` (ikisi de yeni
alt sınama, geçti). `gecti` artık altı alt sınamanın hepsi.

#### Madde 2: patlatma kuralının etkisi

- Sayım (pf1; aynı veri, iki `app.js`: depo ↔ `yerinde` kapalı kopya; Σ|ΔRGB| > 24 piksel): 120 konum × 2 tema; değişen **9 konum**,
  ikisi de iki temada: 4, 12, 14, 19, 23, 29, 37, 42, 42.1. Kalan 111 konumda fark 0.
- Bakış (9'u, açık tema tam; koyu tema paftada): 42 / 42.1 iki ön kol yerinde, iyi (amaçlanan). 12, 14, 19, 23, 37 taban / gövde yerinde,
  parçalar referanslı. **Bozulma: 4 (B1a)** opak alt plaka alttan gelen 20 naylon burcu ve akü ön takozunu örtüyordu; 29'da kart
  altından gelen cıvatalar kısmen örtülüyordu.
- Düzeltme (`app.js` `siraKonum`): yerinde çizilen, henüz takılmamış parça saydam (0,35); takılınca opak. Sonra (pf2) aynı 9 konum
  değişiyor (fark 11 028–210 828 px); 9'una iki temada baktım: 4'te burçlar ve takoz plakanın içinden görünüyor, 29'da cıvatalar
  görünüyor, 12 / 14 / 19 / 23 / 37 / 42 / 42.1'de örtülen parça yok. **Bozulan 0** (kendi gözüm).
- Görüntü: `F10f-goruntu-d2-patlat.png` (4, 29, 42, 42.1 patlatma; önce = tur 1 davranışı, sonra = saydam yerinde).
- Adım 0'daki 47 / 58 px fark: farklı piksellerin rengi önce gri / camgöbeği, sonra mor / magenta. Neden (çıkarım): tur 1'deki uzatma
  rengi değişikliği (`#0d8f6f` → `#dd00ff`); kol şemaları gövde boşluklarından görünüyor. `tak()` değil: `patlat()` / `tak()` adım 0'da
  (`su === 0`) hemen dönüyor (koddan). Şemaları gizleyip farkın kaybolduğu tarayıcıda **doğrulanmadı**.

#### Madde 3: kablo kareleri (tur 2 sonrası)

Kendi gözümle, 1400 × 900, `?adim=N.J&cekim=1`, iki tema; sınıf = iki temanın kötüsü. Önce = tur 1 durumu (kopya), sonra = depo.

| Kare | B2 | Sonra (açık / koyu) | Kötüsü | Not |
| --- | --- | --- | --- | --- |
| 36.4 | — | anlaşılır / anlaşılır | anlaşılır | menekşe uzatma opak, demet saydam |
| 36.5 | — | anlaşılır / anlaşılır | anlaşılır | |
| 40.2 | — | anlaşılır / anlaşılır | anlaşılır | S2 lopu ve bağ beyaz |
| 40.3 | — | anlaşılır / anlaşılır | anlaşılır | |
| 41.2 | — | anlaşılır / anlaşılır | anlaşılır | |
| 41.3 | zor | anlaşılır / anlaşılır | anlaşılır | açık temada grup kenarı artık siyah, kaset duvarı seçiliyor |
| 41.4 | zor | zor / anlaşılır | **zor** | tambur ve kaset kenarı artık çizili, mafsal cıvatası saydam; açık temada soluk öbür duruş izi gri zeminde zayıf, kare yoğun; −45 uç piksel boyu ölçülmedi |
| 41.5 | zor | zor / anlaşılır | **zor** | aynı |
| 42.2 | — | anlaşılır / anlaşılır | anlaşılır | servo kablosu |
| 42.3 | — | anlaşılır / anlaşılır | anlaşılır | |
| 44.2 | — | anlaşılır / anlaşılır | anlaşılır | |
| 44.3 | — | anlaşılır / anlaşılır | anlaşılır | |
| 48.2 | zor | anlaşılır / anlaşılır | anlaşılır | iki ek arasında uzatma rengi parça; lehim ve JR ek noktası beyaz bant; koyu temada siyah JR koyu gri zeminde seçiliyor |
| 48.3 | zor | anlaşılır / anlaşılır | anlaşılır | aynı |

Sayım: anlaşılmıyor **0**, zor **2 / 14** (41.4, 41.5), hedef ≤ 4. Bu benim gözüm; bağımsız bakış değil, okunurluk ölçülmedi.
44.1 (çekim ve patlatma) iki temada da bakıldı: rulman çatalla birlikte, kare değişmedi gibi görünüyor (çekimde rulman çatalın içinde).
Görüntüler: `F10f-goruntu-d2-41.png` (41.3–41.5), `-48.png`, `-44.png` (44.1 çekim + patlatma), `-patlat.png`.

#### Madde 4: PDF lejantı

`rehber/yazdir.html`: her alt kartın görselinin altında ve ana karenin altında (şema yalnız olanlar hariç) "Karede: …" lejantı (renk
kutucuğu + şema lejantı, öbür uç duruş için "(soluk: öbür uç duruş)"), 8,1 pt. Ölçüm (zin1 PDF, PyMuPDF): tur 1'de 74 sayfa / en küçük
yazı 8,1 pt / 16 076 kB; şimdi **75 sayfa**, en küçük yazı DOM ve PDF'te **8,1 pt**, 16 193 kB; "Karede:" satırı 20 (14 alt kart + 6 ana
kare). Sayfa 61 ve 72 gözle görüldü (lejant görselin altında, taşma yok).

#### Zincir

zin1 (uret1 sonrası, saydam düzeltmeden önce): hepsi çıkış 0; bekçinin gördüğü en az boş bellek 5,38 GB.

| Komut | Başlangıç | Boş bellek | Süre | Çıkış |
| --- | --- | --- | --- | --- |
| rehber_uret --veri-yok | 03:37:44 | 7,34 GB | 2377 s | 0 |
| F10f-dogrula | 04:17:21 | 7,28 GB | 551 s | 0 |
| F10e-dogrula --goruntu-yok | 04:26:32 | 7,27 GB | 890 s | 0 (renk_demo KALDI: karar, F10e'den beri) |
| F10d-dogrula --goruntu-yok | 04:41:22 | 7,20 GB | 730 s | 0 |
| F10a-dogrula --kanit-yok | 04:53:32 | 7,20 GB | 437 s | 0 (mini 50 / 50, 360 px taşma 0) |
| F9b-dogrula | 05:00:48 | 7,30 GB | 5 s | 0 |
| carpisma_kos kontrol | 05:00:54 | 7,29 GB | 0 s | 0 (17 dosya aynı) |
| regresyon --yazma | 05:00:54 | 7,28 GB | 0 s | 0 (10 / 10 aynı) |

Üretim sonuçları (zin1): 50 / 50, konsol 0, 1192 ↔ 1192, alt adım 71 / 71, her parça tek adımda; denetim ASCII 0, ulaşılamaz 0 (565
bağlantı), girilemez 0, perdelenme gerekçesiz gizli 0 (istisna 115); yazdırma karesi 121, boş 0; telefon 360 px 0; kol_kablo GEÇTİ
(bölüm 38, uç 76, katı 0, metin 29 sayı, eksik / birim / etiket / pin 0, el yok gerekçeli 28); F10f kablo kare / sağ-sol / mini etiket
GEÇTİ; devir a parça kare görünmeyen 123 / 206 açık, 122 / 206 koyu (değişmedi); gizli 9 / 9. GLB karması HEAD ile aynı; parça ↔ adım
ataması HEAD ile aynı (0 fark); HEAD'e göre değişen giriş alanları u 36, d 36, h 16.

zin2 (`app.js` saydam düzeltmesinden sonra; son durum budur): hepsi çıkış 0; toplam 4983 s, bekçinin gördüğü en az boş bellek 5,07 GB.

| Komut | Başlangıç | Boş bellek | Süre | Çıkış |
| --- | --- | --- | --- | --- |
| rehber_uret --veri-yok | 05:28:49 | 6,89 GB | 2378 s | 0 |
| F10f-dogrula | 06:08:27 | 7,12 GB | 554 s | 0 |
| F10e-dogrula --goruntu-yok | 06:17:41 | 7,11 GB | 886 s | 0 (renk_demo KALDI: karar, F10e'den beri) |
| F10d-dogrula --goruntu-yok | 06:32:27 | 7,05 GB | 726 s | 0 (360 px taşma 0) |
| F10a-dogrula --kanit-yok | 06:44:32 | 7,11 GB | 434 s | 0 (mini 50 / 50, 360 px taşma 0, konsol 0) |
| F9b-dogrula | 06:51:47 | 7,11 GB | 5 s | 0 |
| carpisma_kos kontrol | 06:51:51 | 7,08 GB | 0 s | 0 (17 dosya aynı) |
| regresyon --yazma | 06:51:51 | 7,09 GB | 0 s | 0 (hepsi aynı) |

zin2 sonrası ölçtüklerim: `kontrol.json` uçuş satır 336, çarpışan 0, istisna 20, `istisna_bos` 0, ölçüm kaydı 1 (31.6 p0798); denetim
ASCII 0, ulaşılamaz 0 (565), girilemez 0; kol_kablo GEÇTİ (aynı sayılar); 1192 ↔ 1192; PDF 75 sayfa, en küçük yazı 8,1 pt, 16 193 kB,
"Karede:" 20. zin1'deki sayılarla aynı.

#### Önceki ajanın kodunda düzeltilenler

- M8 kuralı (kol adımında dize anahtar → `bos`) 36.1 / 36.2'deki F10d dize anahtarlarını kırıyordu (`istisna_bos` 2): dar + "yol".
- Yeni duruş kuralı 40.1 dış bileziği çarpışan yaptı; 44.1 için yapılan `birlikte` 40.1'e de uygulandı, kullanılmayan anahtarlar silindi.
- `dar()` "ölçüm kaydı" sınıfını bilmiyordu (`SINIF_ONEK` yoktu): sınıf önekleri tek yerde; 31.6 kamera dize anahtarı ölçüm kaydına.
- `ozet_yaz` yeni pay, `istisna_bos` ve ölçüm kaydı satırlarını basmıyordu: eklendi.
- Yeni metin 8 ASCII kalıntısı verdi (uret1 çıkış 2): kelimeler `ASCII_TAMAM`'a (gözden geçirildi).
- `app.js` `yerinde` kuralı adım 4 / 29'da örtme yapıyordu: saydam (madde 2).

#### Dokunulan dosyalar (tur 2, iki ajan)

`tasarim/freecad/rehber/`: `rehber_giris.py`, `rehber_sira.py`, `rehber_metin.py`, `rehber_kol_kablo.py`, `rehber_denetim.py`;
`rehber/app.js`, `rehber/yazdir.html`; `planlama/d158/F10f-dogrula.py`, `F10f-gunluk.md`, `F10f-goruntu-d2-{41,44,48,patlat}.png`,
`FREECAD-KILIT.txt`; üretilenler (`rehber/veri/*`, `planlama/rehber/kontrol.json`, kareler, PDF, `F10*-dogrula.json`). Model geometrisi,
parça ↔ adım ataması, dokunulmazlar listesi değişmedi.

#### Ölçülmeyenler

- Kablo karelerinde okunurluk yalnız göz (benim); bağımsız bakış yok; 41.4 −45 uç piksel boyu ölçülmedi.
- Adım 0 farkının nedeni tarayıcıda doğrulanmadı (koddan ve renkten çıkarım).
- Nokta–üçgen ile ışın derinliği farkı; alet erişimi (K1-b vidası), kablonun elle döşenmesi.
- 121 konumda patlatma görünümünde konsol taraması yapılmadı (yalnız ekran farkı).
- pf2'de koyu temaya paftada (küçük) bakıldı, tam boy değil.
