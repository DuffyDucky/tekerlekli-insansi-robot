# P10.8d günlüğü · parça beklemeyen CAD açıkları (A ajanı: tasarım / uygulama)

DURUM (21.11 06:35, B2): **KONTROL BİTTİ, GEÇER** (`P108d-kontrol.md`; tam tarama `20261121-023529` tek koşu, 364 / eklem aralığında 0).
**C BEKLİYOR: Kapanış tarifi § 14.** Commit / push yok.
(Önceki durum: A işi bitti, açılış 20.11.2026 11:15, bitiş 11:45; saat okundu. Dal `lale-duzeltme`, HEAD `1fbe337`. B 20.11 11:42–12:44,
tarama Windows Update yeniden başlatmasıyla kesildi; B2 § 13.)
Başlangıçta: FreeCAD kilidi "boş", çalışan FreeCAD yok, boş bellek ≈ 4 GB. Çalışma ağacında 19 eski kir + orkestratörün
`planlama/dongu-158.md` değişikliği (kilit satırı ve § 5 satırı; bu ajan yazmaz).

## 1. Kapsam ve kabul ölçütleri (değişiklikten önce yazıldı)

Ortak ölçüm aracı: `planlama/d158/P108d-olcum.py` (FreeCAD 1.1, `run_fc.py` ile; `taban_parcalar.py`'yi içe aktarır, iskelet /
kabuk / kafa / kol parçalarını `montaj/robot-montaj.FCStd`'den (Modul ≠ taban) alır; yalnız `planlama/d158/P108d-olcum/` altına
yazar). Aynı betik değişiklikten önce (HEAD, `P108d-olcum/once.json`) ve sonra (`sonra.json`) koşar. "Yabancı parça" = kablonun
bağlı olmadığı / içinden geçmediği her gerçek (Referans olmayan) parça; izinli liste F10v-yol-bosluk.py `IZIN` ile aynı, yeni
kartlar adıyla eklenir. Mesafe `distToShape` (tüp r 2,5, `taban_parcalar.tup`), ortak hacim `common().Volume`.

| # | Madde | Şu anki durum (kaynak) | Hedef (sayı) | Doğrulama | Dokunulacak |
|---|---|---|---|---|---|
| 1 | Kablo yolu 10 × ön şarj kartı | 0,1 mm değiyor (`F10v-gunluk.md` § 1 "önceden olan"); HEAD'de yeniden ölçülür | Yol 10'un yabancı parçalara en dar boşluğu **≥ 1,0 mm**, ortak hacim **0 mm³** (taban + iskelet + kabuk parçaları) | `P108d-olcum.py` → `yol["10"]` | `taban/taban_parcalar.py` YOL[9] |
| 2 | Kablo yolu 11 ve 12 × elektronik katı | Katı ön kesiğin (x −60…60, z 150…175) dışından deliyor, ESP32 taşıyıcısının burç / vidasına giriyor, yol 11 alt plakaya değiyor (`F10v-gunluk.md` § 1; kuyruk K64 notu "Açık, CAD") | (a) Elektronik katı × tüp ortak hacim **0 mm³**; (b) kat orta düzlemini geçiş noktası kesiğin içinde, kesik kenarına **≥ 2,5 mm** (tüp yarıçapı; `kablo_yolu_taban.gecis_denetle` kuralı); (c) yabancı parçaya en dar **≥ 1,0 mm** (iskelet ve kabuk dahil). (d) Rehberin kırpma sabiti değişmeden geçerli kalır: yol 12'nin noktalar[0..2]'si BTS7960 sol → ESP32 taşıyıcısı, en büyük y ≤ 190 (`rehber_kablo.CAD_KIRP[12]` son 2, kesim y 192,5) | `P108d-olcum.py` → `yol["11"]`, `yol["12"]`, `gecis` | `taban_parcalar.py` YOL[10], YOL[11] |
| 3 | Burç 2'nin akü kablo yarığı üstünde oturması | Burç 2 (x −65, z −23,5) panele **%39** oturuyor (7,484 / 19,129 mm²), alt vida başı **%26** (6,28 / 23,758 mm²), delik yarığa açık (`F10b-olcum.json` `on_sarj_oturma`; kuyruk K53 "İlgili not") | Burç 2 ve alt vida başı panele **%100** (oran 1,000), burç tabanı yarık kenarına **≥ 1,0 mm**; öbür üç burç %100 kalır; K53 çentiği / kat inişi etkilenmez (yalnız arka burç değişir) | `P108d-olcum.py` → `oturma` | `taban_parcalar.py` (ön şarj kartı delikleri; güç paneli deliği) |
| 4 | Acil stop düğüm kartı CAD modeli | Modelde yok, nominal konum yok (`rehber_kablo.MODELSIZ_KONUM` "sınanmaz, elle bakıldı"; kuyruk P10.7b2a açık işi) | Modelde **1** kart: güç panelinde, nominal konum + **nominal zarf (TAHMİN)** (içerik kayıttan: iki adet 2 pin 5,08 mm vidalı klemens, `kablolar.json` A02 sonlandırması); taban içi çakışma **0**, bağlantı kontrolü **hepsi tamam**, taban × iskelet / kabuk **0**, burçlar panelde **%100**, alt vida başı akü / kayışa **≥ 1,0 mm**, kablo yollarına (Referans) **≥ 1,0 mm** | `taban_montaj.py` + `P108d-olcum.py` → `yeni_kart` | `taban_parcalar.py` |
| 5 | Dağıtım kartı C'nin yeri ve bağlantı elemanı (A12) | Kart modelde yok; yer kararı "güç panelinde, XL4016 C'nin yanında" (`kablolar.json` P7b2a-6); şema ucu `kablo_yolu_taban.DAGITIM_C` (100; 192; −60), "yeri yaklaşık" | Modelde **1** kart (nominal zarf, TAHMİN; içerik `kablolar.json` SV3 notu: 16 AWG giriş klemensi, 2200 µF, iki 3 pinli çıkış), 4 × M3 × 8 naylon burç + üst / alt vida (öbür panel kartlarıyla aynı); madde 4'ün ölçütlerinin aynısı + şema ucu DAGITIM_C kartın kutusuna **≤ 5 mm** (rehber `SEMA_KONUM` ve şema dosyası değişmeden tutarlı kalır) | aynı | `taban_parcalar.py` |
| 6 | 11 taban + 5 kafa içi / ses şemasının çarpışma taraması | Hiç taranmadı (`kablo_yolu_taban.py`, `kablo_yolu_kafa.py` başlık yorumları; kuyruk P10.7b2c açık işi) | **16 / 16** şema taranmış: her şema için yabancı parçalara en dar uzaklık (eksen çizgisi) ve çizim yarıçapı (`rehber_kablo.KESIT_YARICAP`, rehberin çizdiği tüp) içinde kalan parçalar, uçta / arada ayrımıyla JSON'da. TAHMİN uçlar (kafa giriş kartı, kart üstü konnektör yerleri) TAHMİN kalır, ölçü uydurulmaz. Şema geometrisi bu pakette değişmez (şema `kablolar.json` `sema_boy` ve rehber onay kaydının kaynağı; düzeltme rehber paketinde, liste kuyruğa) | `P108d-olcum.py` → `sema` | yok (yalnız ölçüm) |
| 7 | E4 dikey dikiş bindirmesi ölçümü | Ölçülmedi; F10c "sol takılıyken sağ girmez", F10y "+x 129 mm serbest" (mesh, tam bağlam); kuyruk "Açık (c)" | B-rep ölçümü: (a) bindirmenin geometrisi (dilin x / y / z genişliği, iki kabuk arası boşluk); (b) iki kabuk yalnızken iki sırada 10 yönde süpürme (ortak hacim > 0,01 mm³ ilk mesafe, 150 mm'ye kadar). Sonuç: "dikiş sırayı zorluyor mu" evet / hayır, sayıyla. **Model değişmez** | `planlama/d158/P108d-e4.py` → `P108d-olcum/e4.json` | yok (yalnız ölçüm) |

**Korunan değerler (kötüleşemez):** boy 1.580,0 (taban değişikliği y < 262'de; boy etkilenmez, ölçüm B / C); taban içi çakışma 0,
taban × iskelet 0, taban × kabuk 0 (`taban_montaj.py`); tam tarama B'de; devrilme: `taban_montaj` robot bölümü bilgi olarak önce /
sonra (eklenen kütle ≈ 0,1 kg, taban katında); `uygulama-ivme.json` bu pakette koşmaz (P10.8e). Tilt / pan / mikrofon-hoparlör /
SY8205 × USB: kafa dosyalarına dokunulmaz, değişmez.

**Dokunulacak dosyalar (tam liste, kilit tablosu için):** kaynak yalnız `tasarim/freecad/taban/taban_parcalar.py`;
`taban_montaj.py`'nin ürettikleri `tasarim/freecad/taban/{taban-analiz.json, taban-bom.csv, taban-montaj.FCStd, taban-montaj.step}`,
`tasarim/freecad/taban/dxf/guc-paneli-arka-5mm-kontrplak.dxf` (yeni delikler); `planlama/d158/P108d-*` (günlük, ölçüm betikleri,
`P108d-olcum/`). `arayuz.py`, `taban_lib.py`, şema dosyaları, rehber kaynakları, `kablolar.json`, `maliyet.json`: dokunulmaz.
İzlenen `taban_parcalar.py` değiştiği için `carpisma_kos.py kontrol` 1 verir (beklenen; tam tarama B'de).

**Paketten çıkarma kuralı:** bir madde parça ölçüsü ya da Ahmet'in kararını isterse uydurulmaz; gerekçesi ve kuyruk metni § sonuna.

### 1.1 Başlangıç ölçümü (HEAD, değişiklikten önce; `P108d-olcum/once.json`, 11:18, 32,7 s, çıkış 0) ve hedef düzeltmeleri

| Madde | HEAD'de ölçülen | Hedefin kesinleşmesi |
|---|---|---|
| 1 | Yol 10 × ön şarj kartı **ortak hacim 0,354 mm³** (değme değil, 0,1 mm giriyor: tüp altı 197,5, kartın header zarfı üstü 197,6). Sonraki yabancı: M5x12 kat civatası 12,25 mm | değişmedi: ≥ 1,0 mm, 0 mm³ |
| 2 | Yol 11: yabancı ortak hacim **871,6 mm³** (alt plaka 158,3; elektronik katı 265,4; şase ara rayı ön 419,6 (iskelet); ESP32 taşıyıcı vida 1 üst 28,3); arayüz kartı vida 3 üst **0,80 mm**. Geçiş: alt plakayı 2 yerde deliksiz geçiyor + plaka içinde yatay bölüm, katı (−93,6; 132,5)'te kesiksiz. Yol 12 rehber bölümü: **522,1 mm³** (kat 464,5; ESP32 taşıyıcı burç 1 43,0; vida 1 alt 13,1; vida 1 üst 1,6); katı (32,3; 111,8)'de kesiksiz | (c) yol 12 için **rehberin çizdiği bölümde** (noktalar 0..2; tam yolun direk / boyun bölümü yol 6 / 8 ile aynı eski sorun, kapsam dışı, § 7). Yol 11 için tüm yol |
| 3 | Burç 2: **7,484 / 19,129 mm² (0,391)**, alt vida başı **6,280 / 23,758 (0,264)**. Kıyas: engelsiz delikli burç 17,118 (0,895), vida başı 14,679 (0,618); fark Ø3,4 panel deliği | Hedef "%100" = engelsiz delikle aynı: burç **0,895**, vida başı **0,618** (ön şarj burç 1 / 3'ün 0,817'si K53 çentiği, bu paketin değil) |
| 4–5 | `yeni` boş (kart yok). Panel altı vida başları: bara tutucusu ISO 7380'ler aküye 1,35 mm (en dar) | Alt vida başı akü / kayışa ≥ 1,0 mm, yeni kartlar M5 kat civatalarının (x ±115, z −40) üstünü örtmez (panel sökümü için anahtar erişimi). Kart C'nin yeri yol 1'in (88; 199; −60) → (112; 192; −100) çaprazını kesiyor: **yol 1 bu bölümde yeniden çizilir** (uçlar aynı) |
| 6 | 16 / 16 şema ölçüldü; eksen çizgisi parçanın içinde: G07 (bara tutucusu), G16 (gövde direği), M02 / N01 / N02 (motor, uç) — ayrıntı § 4 | ölçüm, değişiklik yok |
| rehber | `P108d-rehber-denetim.py once`: tüm denetimler hata 0; geometri bilgi 4 (A04 / A06 acil stop düğümü, S09 / S10 dağıtım C "modelsiz, elle") | sonra da hata 0 (rehber kaynağına dokunulmadan) |

## 2. Yapılan değişiklik (tek kaynak dosya: `tasarim/freecad/taban/taban_parcalar.py`, +64 / −7 satır)

- **Madde 3 (burç 2):** `OS_DEL[2]` (ön şarj kartının arka sağ deliği) z −23,5 → **−18,5** (`OS_DEL2_Z = −23 + 3,175 + 1,325`; altıgen
  burcun köşesi yarık kenarına 1,325 mm). Güç paneli deliği aynı listeden kesildiği için birlikte taşındı. Kart şekli `on_sarj_local()`:
  `perf_local()` (zarf değişmedi) + yeni Ø3 delik; eski köşe deliği kartta boş kalır (kendi yapımı pertinaks). Öbür üç burç ve K53
  çentiği değişmedi.
- **Madde 4:** "Acil stop dugum karti (pertinaks, nominal zarf TAHMIN)": merkez (−118; −90), 30 × 30 × 1,6 + tek bileşen zarfı 10 mm
  (A / B dağıtım kartlarındaki 16 AWG klemensin yüksekliği), kütle 10 g (TAHMİN). 4 × M3x8 naylon burç, üstte M3x6, alttan M3x8 DIN 912
  (ön şarj kartıyla aynı `kart_burclu`). Kart x −133…−103, z −105…−75, y 187,5…199,1: röle K1'in (z ≤ −115) ve ön şarj kartının
  (z ≥ −26) arasında, akü ve kayışın dışında (alt vida başı x ≤ −102,75; kayış x ≥ −92,5).
- **Madde 5:** "Dagitim karti C (kafa pan + tilt; pertinaks, nominal zarf TAHMIN)": merkez (112; −77), 36 × 30 × 1,6 + zarf 10 mm,
  16 g (TAHMİN), bağlantı elemanı madde 4 ile aynı. Kart x 94…130, z −92…−62: XL4016 C'nin arkasında (karar P7b2a-6 "XL4016 C'nin
  yanında"), SV3 şemasının ucu (100; 192; −60) karta 3,0 mm. Alt vida başları akü kayışına 1,25 mm (x 96,5). M5 kat civatalarının
  (±115; −40) üstü açık (panel sökümünde anahtar girer). Ana sigorta yuvasına 8 mm.
- **Yol 1 (madde 5'in gereği):** (88; 199; −60) → (112; 192; −100) çaprazı kart C'nin yerinden geçiyordu; araya (88; 199; −100) eklendi
  (x 88'den sigorta yuvasının +z ucuna iner). Uçlar aynı.
- **Madde 1, yol 10:** röleden sonra düğüm kartına (−118; 197; −90) uğrar; ön şarj kartının üstündeki iki nokta y 200 → **203**.
  Uçlar aynı.
- **Madde 2, yol 11:** baştan çizildi (Q01 / Q02 şemasının yolu): sonar sol pin bloğu (−79,41; 127; 255; PCB üst kenarı, TAHMİN, şemayla
  aynı varsayım) → ara ray üstü y 140 → kat altı y 155 → ön kesik (x −28, z 162,5) → kat üstü y 184 → arayüz kartı (−90,5; 195; 95)
  → (0; 195; 90) → ESP32 (80; 195; 85). Kesik geçişi önce x −45'teydi: BTS7960 sol kutusuna 9,5 mm kalıyordu ve rehber
  `geometri_denetle` "B01 bu yola ulaşıyor, eşlenmemiş" hatası verdi (ara koşu, § 6); x −28'de 14,5 mm, hata 0.
- **Madde 2, yol 12:** yalnız `noktalar[1]` (−30; 160; 160) → **(−10; 190; 168)**: kat orta düzlemini kesiğin içinde (−25,0; 160,7)
  geçer, ESP32 taşıyıcısının köşe vidalarından ve PCA9685'ten uzak. Nokta sayısı ve `noktalar[2]` = ESP32 taşıyıcı merkezi aynı, en büyük
  y 190: `rehber_kablo.CAD_KIRP[12]` geçerli (`cad_kirp_denetle` hata 0). İlk deneme (−3; 190; 170) PCA9685'e 0,998 mm verdi, bırakıldı.
- Ölçü sabitleri `ESD`, `DGC` `taban_parcalar.py`'de (arayüze girmedi); `arayuz.py`, `taban_lib.py` değişmedi.

## 3. Sonuçlar: önce → sonra (`P108d-olcum/once.json` → `sonra.json`; `taban_montaj.py` son koşusu)

| # | Ölçüt | Önce | Sonra | Hedef |
|---|---|---|---|---|
| 1 | Yol 10 yabancı ortak hacim / en dar | 0,354 mm³ / 0 (ön şarj kartı) | **0 / 2,90 mm** (ön şarj kartı) | ≥ 1,0; 0 ✅ |
| 2 | Yol 11 yabancı ortak hacim / en dar | 871,6 mm³ / 0 (alt plaka, kat, ara ray, ESP32 vida) | **0 / 1,95 mm** (etek ön sol, kabuk); ara ray 2,5; kat 3,95 | ✅ |
| 2 | Yol 11 geçiş | plakada 2 deliksiz geçiş + plaka içinde yatay; kat (−93,6; 132,5) kesiksiz | **kat (−28; 162,5) kesikte, başka geçiş yok** | ✅ |
| 2 | Yol 12 rehber bölümü ortak hacim / en dar | 522,1 mm³ / 0 (kat, ESP32 taşıyıcı burç ve vidaları) | **0 / 2,46 mm** (ESP32 taşıyıcı vida 1 üst); PCA9685 3,32; kat 5,63 | ✅ |
| 2 | Yol 12 geçiş | kat (32,3; 111,8) kesiksiz | **kat (−25,0; 160,7) kesikte** | ✅ |
| 2 | Yol 12 tam yol | 2.825,4 mm³ | 2.303,3 mm³ (yalnız direk / boyun bölümü: boyun plakası, pan servosu, göğüs VESA taşıyıcısı) | kapsam dışı, § 7 |
| 3 | Burç 2 panel oturması / alt vida başı | 0,391 / 0,264 | **0,895 / 0,618** (engelsiz delikle aynı) | ✅ |
| 4–5 | Yeni kart × kablo yolları (en dar, kendi yolu hariç) | – | düğüm kartı: yol 3'e 9,65; burç / vida yol 10'a ≥ 7,29. Kart C: yol 1'e 6,01 (kart), vida 6,31 | ≥ 1,0 ✅ |
| 4–5 | Yeni burçlar panelde / alt vida başı | – | 8 burç 0,895, 8 vida başı 0,618; en dar alt baş → akü kayışı 1,25 (kart C vida 0) | ✅ |
| 5 | DAGITIM_C (100; 192; −60) → kart C | – | 3,0 mm | ≤ 5 ✅ |
| – | `taban_montaj.py` | 388 parça (13 referans), çift 660, bağlantı 140 / 140, iç çakışma 0, × iskelet 0 (81 çift), × kabuk 0 (473), bölge ihlali 0 | **414 parça** (+26: 2 kart, 8 burç, 16 vida), çift 708, **bağlantı 148 / 148**, iç çakışma 0, × iskelet 0 (81), × kabuk 0 (509), bölge 48 / ihlal 0, STEP katı 414, eklem tamam | ✅ |
| – | Taban kütlesi / AM | 8.231,4 g; (−0,711; 121,299; −45,942) | 8.272,5 g (+41,1); (−0,639; 121,634; −46,122) | bilgi |
| – | Devrilme (`taban_montaj` robot bölümü, bilgi) | en küçük düz 2,02, rampa 5° 1,44 (one_yuk ileri) | 2,02 / **1,45**; değişen 9 değer +0,01, kötüleşen yok | bilgi |
| – | Korunan devrilme 1,519 (`uygulama-ivme.json` ızgara) | 1,519 | **koşulmadı (P10.8e)**; eklenen 41 g kat düzeyinde, AM 0,5 mm iniyor → kötüleşme beklenmez, **doğrulanmadı** | B / C |
| – | Rehber denetimleri (`P108d-rehber-denetim.py`) | hepsi hata 0 | geometri hata 0; **`sema_geometri_denetle` hata 1** (§ 9.1, P10.8e) | bilinen |

BOM (`taban-bom.csv`): M3x6 DIN 912 80 → 88, M3x8 DIN 912 26 → 34, M3x8 naylon burç 44 → 52; iki yeni "Delikli pertinaks … (TAHMIN)"
satırı; güç paneli 239,9 → 239,7 g (8 yeni delik). DXF: yalnız `guc-paneli-arka-5mm-kontrplak.dxf` değişti (8 yeni delik + taşınan
delik); öbür iki DXF git'e göre aynı.

## 4. Madde 6: 16 şemanın taraması (`P108d-olcum/sonra.json` `sema`; eksen çizgisi × 1.251 gerçek parça)

Yöntem: şema noktaları rehberin tek çözücüsünden (`rehber_kablo.sema_noktalari`, `P108d-sema-girdi.py`), çizgi `Part.makePolygon`;
parçalar taban kaynaktan, öbür modüller `montaj/robot-montaj.FCStd`'den. "Uç": en yakın nokta şemanın bir ucuna ≤ 10 mm. Gerçek dış
çap kayıtta yok; çizim yarıçapı (`KESIT_YARICAP`, okunur ölçek) yalnız eşik olarak kullanıldı.

| Şema | r çizim | Eksen parçanın içinde | Çizim yarıçapı içinde (uçta kendi ucu / arada) | Yorum |
|---|---|---|---|---|
| G07 | 2,5 | **yıldız bara tutucusu (arada)** | uç: ana anahtar 2,0 (kendi ucu); **ara: anahtarlı tutucu 0,5, yıldız tutucu M3 ısıl gömmesi 2,0, yıldız 1 M5 civatası 2,1** | şema y 184'te (x −56; z −123…−55) bara tutucularının içinden: **gerçek ara çakışma** |
| G16 | 3,6 | **gövde direği, iskelet (arada, uca 44,8 mm)** | uç: anahtarlı 2 somun / pul / civata / tutucu ≤ 2,5 (kendi ucu) | (20; 195; −18) direğin içinde: **gerçek ara çakışma** |
| G22 | 2,5 | – | uç: anahtarlı 4 somun 0,38 … tutucu 2,4 (kendi ucu) | temiz |
| SV3 | 3,6 | – | uç: **kart C vida 1 üst 2,95, kart C 3,0** (kendi ucu) | önce temizdi (en dar panel 4,5); kart modele girince uç kartın yanında |
| G19 | 3,6 | – | – (en dar kat 6,53) | temiz |
| M02 | 2,5 | motor arka sol (uçta, 9,4 mm) | kendi ucu | temiz |
| B02 | 2,5 | – | – (BTS sağ 2,5, uç) | temiz |
| N01, N02 | 2,5 | motor arka sol / sağ (uçta, 5 mm) | kendi ucu (enkoder) | temiz |
| Q01, Q02 | 2,5 | – | – (sonar tutucu 3,0) | temiz |
| K01 | 3,1 | – | – (kafa iskeleti 3,12) | temiz; kafa giriş klemensi TAHMİN uç, modelde yok |
| K02 | 3,1 | – | uç: SY8205 2,25 (kendi ucu) | temiz |
| K03 | 3,1 | – | – (Pololu 3,6) | temiz |
| C01 | 2,5 | – | – (kamera 2,75) | temiz |
| AU1 | 2,5 | – | – (PAM8403 5,5) | temiz |

Sonuç: **16 / 16 tarandı; 14 temiz, 2 şemada gerçek ara çakışma (G07, G16).** Şema dosyalarına dokunulmadı (kapsam yalnız ölçüm;
şema `kablolar.json` `sema_boy` ve rehber onayının kaynağı). Kafa giriş kartı ve kart üstü konnektör yerleri TAHMİN kaldı.

## 5. Madde 7: E4 dikey dikiş bindirmesi (`P108d-e4.py` → `P108d-olcum/e4.json`, son koşu 21 s, çıkış 0)

Yalnız iki arka kafa kabuğu (ev pozu, global; öbür kafa parçaları yok). **Model değişmedi.**

- **Geometri:** iki kabuk x −16…0 bandında, y 203 mm boyunca **yarım bindirme**: arka duvar 2,5 mm (z −64,89…−62,39) iki katmana
  bölünmüş. Sol kabuğun **dış** katmanı (z −64,89…−63,64, 1,25 mm) x 0'a kadar, sağ kabuğun **iç** katmanı (z −63,64…−62,39)
  x −16'ya kadar uzanıyor. Üst bölümde (yerel y ≥ ~240) bindirme 10 mm (x −10…0). Yerinde ortak hacim 0, boşluk 0 (yüzler değiyor).
  Kesit haritası `e4.json` `geometri.kesit_haritasi`.
- **Süpürme (12 yön, adım 2 mm, ilk çarpışma 0,25 mm'ye inceltilir, eşik 0,5 mm³):**
  - Sol yerindeyken sağ: serbest **+x, −y, +z, (+x+z)**; kapalı −z (0,25 mm'de 18,9 mm³), −x, +y, (+x−z), (−x−z), (−x+z), (+y−z), (+x+y).
  - Sağ yerindeyken sol: serbest **−x, +y, −z, (−x−z), (+y−z)**.
- **Sonuç: bindirme sırayı geometriyle zorlamıyor (zorluyor: hayır)**, ama yönü kısıtlıyor: sol önce takılırsa sağ kabuk **arkadan (−z)
  giremez** (iç dili solun dış dudağının önünde kalır); yalnız yandan (+x) kaydırılarak girer (−y ve +z kafanın içinden geçer, gerçek
  bağlamda yok). Sağ önce takılırsa sol arkadan da yandan da girer. F10y'nin tam bağlam ölçümüyle (+x 129 mm serbest) uyumlu;
  "önce sağ, sonra sol" kolaylık önerisi olarak doğru. Tam bağlamda bu pakette yeniden ölçülmedi.

## 6. Komutlar ve çıkış kodları (depo kökünden; FreeCAD tek koşu, sırayla; `freecadcmd run_fc.py` = `%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecadcmd.exe` + `.robot-cad\run_fc.py`)

| Komut | Çıkış | Not |
|---|---|---|
| `py -3 -B -X utf8 planlama/d158/P108d-sema-girdi.py` | 0 | 16 şema |
| `FC_SCRIPT=planlama/d158/P108d-olcum.py P108D_ETIKET=once freecadcmd run_fc.py` | 0 | HEAD, 32,7 s |
| `py -3 -B -X utf8 planlama/d158/P108d-rehber-denetim.py once` | 0 | hepsi hata 0 |
| aynı ölçüm, `P108D_ETIKET=ara1` | 0 | ara (yol 12 → PCA 0,998 mm; `ara1.json` commit dışı) |
| `FC_SCRIPT=tasarim/freecad/taban/taban_montaj.py freecadcmd run_fc.py` | 0 | 1. koşu, 88 s |
| ölçüm `sonra` + `P108d-rehber-denetim.py sonra` | 0 / 0 | geometri hata 1 (yol 11 ↔ B01) → yol 11 x −28 |
| `taban_montaj.py` (2. koşu, son hâl) | 0 | 83 s; § 3 |
| ölçüm `sonra` (son) + `P108d-rehber-denetim.py sonra` (son) | 0 / 0 | § 3 |
| `py -3 -B -X utf8 planlama/d158/P108d-analiz-fark.py` | 0 | HEAD ↔ şimdi `taban-analiz.json` özeti |
| `FC_SCRIPT=planlama/d158/P108d-e4.py freecadcmd run_fc.py` | 0 | 3 koşu (1: bant kutusu y'de yanlış, geometri boş; 2: düzeltildi; 3: kesit haritası eklendi) |
| `cd tasarim/freecad && py -3 -B -X utf8 carpisma_kos.py kontrol` | **1** | beklenen: `taban/taban_parcalar.py` değişti, tüm bölümler eski |
| `md5sum -c` (başta alınan `montaj/yerlesim-kontrol.json` özeti) | OK | **eski kir dosyası koşularımla yeniden yazılmadı** |

Bellekte deneme (dosya yazmadan): rehber `PARCA_CAD`'de "Dağıtım kartı C" → `^Dagitim karti C`, "Acil stop düğümü" →
`^Acil stop dugum karti` yapılırsa `geometri_denetle` 2 hata verir: **yol 6: S09 / S10 a yanı (Dağıtım kartı C) yola ulaşmıyor**
(yol 6 direk üstünden başlıyor, karta inmiyor; rehberin mutasyon sınaması b44 de bunu bekliyor). Düğüm kartı için hata yok.

## 7. Fark edilen, dokunulmayan (kapsam dışı)

- Yol 12'nin rehberde kırpılan eski bölümü (ESP32 → direk → kafa USB) ve yol 6 / 8 boyun plakası, pan servosu, servo yuvası, göğüs VESA
  taşıyıcısının içinden geçiyor; yol 3 / 4 / 5 / 7 köşe bağlantısına (direk-ray) ve omuz yuvasına giriyor; yol 9'un atılan bölümü
  PCA9685'ten geçiyor; yol 4 akü kayışına 0,89 mm. Hepsi HEAD'de de aynı (`once.json`); Referans tüpler, taramaya girmez.
- G07 ve G16 şemalarında gerçek ara çakışma (§ 4).
- `taban_montaj.py` "Acil stop" önekli parçaları kabuk yakınlık bilgi listesine alır: düğüm kartı da o listeye girdi (yalnız bilgi).
- `taban-montaj.FCStd` 1,45 → 1,31 MB (yeniden yazım; 414 parça, STEP 414 katı). Nedeni incelenmedi.
- Rehber metni / verisi artık eski: `UC_MODELSIZ` "düğüm kartı modelde yok", "kafa dağıtım kartı modelde yok"; `rehber_metin.py:569`
  ve `:2198` ("Kablo yolu 11 ve 12 kesiğin dışında"), `rehber_denetim.py:420` ZORUNLU kuralı; `PARCA_CAD` iki satır MODELSIZ.
- Naylon burç: taban 44 → 52 adet; `maliyet.json` "M3 kart burcu seti 48" yetiyor mu bakılmadı (başka modüllerin burcu sayılmadı).

## 8. Gözle bakılan / bakılmayan

- Bakılan (sayıyla): § 3 ve § 4 tabloları JSON'dan; BOM farkı; kart yerleri parça kutularıyla (`robot-montaj.FCStd` kutu dökümü,
  geçici); E4 kesit haritası.
- **Bakılmayan:** hiçbir görüntü üretilmedi, kartlar ve yollar ekranda görülmedi (taban görselleri, `ana_montaj`, rehber kareleri koşmadı);
  güç paneli kartlarıyla birlikte panelin yerine sokulması (akü üstünden) ölçülmedi; düğüm kartına ve kart C'ye giden kabloların
  (A02…A06, SV3, S09 / S10) CAD yolu çizilmedi; tam çakışma taraması (B'nin işi); DXF'in kendisi açılıp bakılmadı.

## 9. B için riskli yerler (taramadan önce)

1. **`sema_geometri_denetle` 1 hata** (SV3 son ucu kart C'nin yanında; rehber kartı "modelsiz" sayıyor). Rehber üretimi bu denetimde
   durursa P10.8e'de çözülür; çözüm tek satır değil (yol 6 karta inmiyor, § 6). Rehber kaynağına bu pakette dokunulmadı.
2. Parça sayısı değişir: `robot-montaj` 1.238 → **1.264** (gerçek 1.225 → 1.251) olmalı; `ana_montaj`, `robot-bom`, `montaj-analiz`,
   `carpisma-sonuc.json` yeniden üretilecek. `ana_montaj` koşmadım; ölçüm betiğim taban parçalarını kaynaktan aldı.
3. Kart zarfları ve kütleleri **TAHMİN** (kart yok): 30 × 30 ve 36 × 30, zarf 10 mm, 10 g ve 16 g. Zarf üst vida başlarına 0,75 mm.
4. En dar yeni boşluklar: kart C alt vida başı → akü kayışı **1,25 mm**; kart C → yol 1 6,0. Burç 2 → yarık kenarı 1,325 mm (hesap;
   ayrı mesafe ölçülmedi, oturma 0,895 dolaylı kanıt).
5. Yol 11'in başı sonar sol pin bloğu varsayımına (PCB üst kenarı, Q01 / Q02 ile aynı TAHMİN) taşındı; eski baş PCB'nin altındaydı.
   Rehber uç sınaması geçti (hata 0); gerçek pin yeri doğrulanmadı.
6. `taban_parcalar.py` izlenen dosya: `carpisma_kos.py kontrol` tam taramaya kadar 1 verir. Taban × iskelet / kabuk bu pakette yalnız
   `taban_montaj.py` içinde (ev pozu, statik) ölçüldü: 0.
7. Korunan devrilme 1,519 (`uygulama-ivme`) koşulmadı: doğrulanmadı. Boy, tilt / pan, mikrofon-hoparlör, SY8205 × USB: kafa / iskelet
   dosyalarına dokunulmadı, ölçülmedi.

## 10. Commit'e girecek dosyalar (her biri bir yol)

```
tasarim/freecad/taban/taban_parcalar.py
tasarim/freecad/taban/taban-analiz.json
tasarim/freecad/taban/taban-bom.csv
tasarim/freecad/taban/taban-montaj.FCStd
tasarim/freecad/taban/taban-montaj.step
tasarim/freecad/taban/dxf/guc-paneli-arka-5mm-kontrplak.dxf
planlama/d158/P108d-gunluk.md
planlama/d158/P108d-olcum.py
planlama/d158/P108d-sema-girdi.py
planlama/d158/P108d-rehber-denetim.py
planlama/d158/P108d-analiz-fark.py
planlama/d158/P108d-e4.py
planlama/d158/P108d-olcum/once.json
planlama/d158/P108d-olcum/sonra.json
planlama/d158/P108d-olcum/sema-girdi.json
planlama/d158/P108d-olcum/rehber-once.json
planlama/d158/P108d-olcum/rehber-sonra.json
planlama/d158/P108d-olcum/e4.json
```

(B / C'nin kontrol zincirinde yeniden üretilecekler, örn. `ana_montaj` çıktıları ve `carpisma-sonuc.json`, onların listesine.)

**Yasak / dışarıda kalacak:** `planlama/d158/P108d-olcum/ara1.json` (ara ölçüm); 13 kabuk PNG'si (`tasarim/freecad/kabuk/gorsel/*.png`),
`tasarim/freecad/montaj/yerlesim-kontrol.json`, kökte `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`
(19 eski kir); `planlama/dongu-158.md` ve `planlama/d158/karar-kuyrugu.md` (orkestratör yazar); `tasarim/freecad/arayuz.py`;
`tubitak-2209b/`; Efe'nin kod dosyaları.

## 11. Kopyalanmaya hazır metinler

**Plan, P10.8 hücresi ("Sonraki tam taramalı CAD paketinde" listesinin yerine / sonuna):**

> **P10.8d (20.11, `planlama/d158/P108d-gunluk.md`):** CAD kablo yolu 10 ön şarj kartından 2,9 mm (0,354 mm³ → 0); yol 11 baştan
> (sonar pin bloğu → ara ray üstü → ön kesik → arayüz kartı → ESP32; 871,6 mm³ → 0, en dar 1,95) ve yol 12'nin rehber bölümü kesikten
> (522,1 mm³ → 0, en dar 2,46; CAD_KIRP aynı); burç 2 yarıktan çıktı (oturma 0,391 → 0,895, engelsiz delikle aynı); acil stop düğüm
> kartı ve dağıtım kartı C güç panelinde (nominal zarf TAHMİN, M3x8 naylon burç + DIN 912; yol 1 kart C'nin yanından yeniden çizildi);
> 16 şema tarandı (14 temiz; G07 bara tutucularından, G16 gövde direğinden geçiyor); E4 dikişi yarım bindirme, sırayı zorlamıyor (sol
> önceyse sağ yalnız +x'ten). Taban 388 → 414 parça, bağlantı 148 / 148, çakışma 0. Kalan: rehber `PARCA_CAD` ve yol 6 → kart C
> (P10.8e), G07 / G16 şema düzeltmesi; göğüs regülatörü kartı (K52), K31 insert boyu, `TABAN_DISI_BOLGE` bu pakette değil.

**Karar kuyruğu, K53 "İlgili not" sonuna:**

> P10.8d (20.11): burç 2 deliği z −23,5 → −18,5 taşındı; panel oturması 0,391 → 0,895, alt vida başı 0,264 → 0,618 (engelsiz delikle
> aynı). K53'ün kendisi (ön burçlar, çentik) değişmedi.

**Karar kuyruğu, A12 (dağıtım kartı C) satırı:**

> P10.8d (20.11): dağıtım kartı C modelde: güç panelinde XL4016 C'nin arkasında, x 94…130, z −92…−62 (36 × 30, zarf ve kütle TAHMİN),
> 4 × M3x8 naylon burç, M3x6 üst / M3x8 alt DIN 912. SV3 şemasının ucu karta 3,0 mm. Açık: rehber `PARCA_CAD` modele bağlanınca yol 6
> karta ulaşmıyor (S09 / S10); yol 6'nın karta uzatılması ya da dal yolu rehber paketinde (P10.8e).

**Karar kuyruğu, "yol 11 / 12 Açık, CAD" satırı:**

> P10.8d (20.11): CAD tarafı kapandı: yol 11 ve 12 katı ön kesikten geçiyor, yabancı parçaya ortak hacim 0. Rehber metni
> (`rehber_metin.py:569`, `:2198`) ve `rehber_denetim.py:420` kuralı P10.8e'de güncellenecek.

**Karar kuyruğu, "şemalar taranmadı" satırları:**

> P10.8d (20.11): 16 / 16 şema tarandı (`P108d-gunluk.md` § 4): 14 temiz; G07 (y 184'te bara tutucularının içinden) ve G16 (gövde
> direğinin içinden) şema düzeltmesi ister (rehber paketi). Kafa giriş kartı / konnektör yerleri TAHMİN.

**Karar kuyruğu, E4 "Açık (c)":**

> P10.8d (20.11): ölçüldü (B-rep, yalnız iki kabuk): x −16…0 yarım bindirme (sol dış, sağ iç katman, 1,25 + 1,25 mm). Sıra zorlanmıyor;
> sol önceyse sağ yalnız +x'ten girer (−z kapalı), sağ önceyse sol −x / −z'den. Kapandı; "önce sağ" kolaylık önerisi olarak kalır.

**Karar kuyruğu, acil stop düğüm kartı (P10.7b2a açık işi):**

> P10.8d (20.11): acil stop düğüm kartı modelde: güç panelinde (−118; −90), 30 × 30 (zarf, kütle TAHMİN), röle K1 ile ön şarj kartı
> arasında; CAD yol 10 kartın içinden geçer. Rehber `PARCA_CAD` / `UC_MODELSIZ` P10.8e'de modele bağlanır (bellekte denendi: hata yok).
> Alım sorusu (Ahmet): taban naylon burcu 44 → 52; "M3 kart burcu seti 48" yeter mi?

## 12. Paketten çıkarılan maddeler

Yok. Yedi maddenin hepsi yapıldı (6 ve 7 yalnız ölçüm). İki maddenin rehber tarafı (madde 5'in yol 6 bağlantısı, madde 6'nın G07 / G16
şema düzeltmesi) kapsam gereği P10.8e'ye bırakıldı.

## 13. B2 ajanı: kesilen kontrolün bitirilmesi (21.11.2026, açılış 02:30; saat okundu)

### 13.1 Durum (başta okundu)

- HEAD `1fbe337`, dal `lale-duzeltme`; P10.8d commit'siz. Çalışan FreeCAD / python yok. `FREECAD-KILIT.txt` "P10.8d B …, bolum omuz,
  kosu 20261120-120318, 20.11 12:04" (bayat), `dongu-158.md` kilit satırı eski B.
- Eski B (20.11 11:42–12:44): § 1, § 2, § 3.1 yazılmış; tam tarama koşusu `20261120-120318`: `statik` 12:04:32'de bitti (73 s),
  `omuz` 250/875 pozisyonda (günlükte son satır 12:34:22, 1.790 s); sürücü `rc=4`, kalan yedi bölüm koşmadı.

### 13.2 Yeniden başlatmanın nedeni (Windows Olay Günlüğü, System, 20.11 12:20–12:55)

- **12:44:08 olay 1074 (User32):** `C:\WINDOWS\uus\AMD64\MoUsoCoreWorker.exe` NT AUTHORITY\SYSTEM adına yeniden başlattı,
  neden "İşletim Sistemi: Hizmet paketi (Planlı)", 0x80020010. 12:46:21 açılış, 12:47:19 ikinci 1074 (`TrustedInstaller.exe`,
  "Yükseltme (Planlanmış)", 0x80020003), 12:47:34 açılış. 12:50:12 olay 19: KB5132057 (2026-11 Preview Update, 26300.10075) ve
  KB5137006 (.NET) kuruldu.
- **Yok:** Kernel-Power 41, 6008 (beklenmeyen kapanma), BugCheck, Resource-Exhaustion (2004). Kernel-Boot 20: "last shutdown's
  success status was true". Yani **neden taramanın kendisi değil**; bellek tükenmesi izi yok (statik tepe 735 MB, omuz başında boş
  4,18 GB). Omuz günlüğü ≈ 18 dk'da bir satır yazıyor; 12:34:22'den sonraki satır ≈ 12:52'de gelecekti, süreç 12:44'teki kapanışla öldü.
- Windows Update etkin saatleri **18:00 → 12:00** (`HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings`); 12:44 bu aralığın dışında
  kaldığı için otomatik yeniden başlatma oldu. 12:50'den sonra yalnız Defender tanım güncellemeleri (yeniden başlatmasız).
- **Bekleyen yeniden başlatma (21.11 02:32):** WU `RebootRequired` yok, CBS `RebootPending` yok; `PendingFileRenameOperations` 28 girdi
  (yazıcı sürücüsü / gaming services DLL'leri; WU işareti değil). Güç planı Dengeli, uyku AC / DC "hiç", AC'de, pil %100.
- Önlem: tarama etkin saatler içinde (≈ 02:35 → ≈ 06:30) koşar; bellek nedeni olmadığı için ek önlem yalnız eski B'nin bölüm başı
  ≥ 2,5 GB boş bellek beklemesi; günlükler bu kez depoda kalıcı klasörde (§ 13.4).

### 13.3 Eski B'nin dosyaları kurtarıldı (geçici klasörden depoya, `cp -p`, md5 / `cmp` ile birebir)

Kaynak: eski B'nin geçici oturum klasörü (yol commit öncesi kaldırıldı, C). Hedef: **`planlama/d158/P108d-kontrol-olcum/`** (P108b-olcum gibi
betik + JSON düzeni):
- betikler: `b_tarama.py` (tarama sürücüsü), `b_olcum.py`, `b_sema.py`, `b_e4_vida.py`, `zincir.sh`, `yokla.sh`;
- ölçümler: `b-once.json`, `b-sonra.json`, `b-sema.json`, `b-sema16.json`, `b-e4-vida.json`; kayıtlar: `kaynak-bas.json` (12:03 izlenen
  17 dosya özeti), `md5-bas.txt` (11:45), `kir-bas.txt` / `kir-simdi.txt`, `tarama.durum`;
- günlükler `b1-log/` (18 dosya: zincir, ölçüm, rehber denetimleri, `tarama-surucu.log`, `carpisma-statik.log`, `carpisma-omuz.log`).
  18 günlükte "Exception while processing" 0.
- Rapora geçmemiş ölçüm: yok. `b-e4-vida.json` (vida başı alanları 14,679 / 13,604 / 6,28 mm², oran 0,88 / 0,815 / 0,376) ve E4
  değerleri kontrol raporu § 2'de; `b-sema16.json` § 2 madde 6 satırında.

### 13.4 Eski B'nin zincir sonuçları hâlâ geçerli mi: **geçerli** (yeniden koşulmadı)

- Depoda 20.11 12:02:30'dan sonra değişen dosya (`find -newermt`, `.git` hariç) yalnız üç: `FREECAD-KILIT.txt`, `P108d-kontrol.md`
  (12:39) ve `carpisma-bolum/statik.json` (12:04:31, eski taramanın çıktısı; B2 taramasında yeniden yazılır).
- Zincir çıktılarının zamanları: `taban-*` 11:47:52–58, `montaj/*` 11:53:17–37, `lale158-kontrol.json` 11:53:48,
  `uygulama-olcum.json` 12:01:05, `uygulama-ivme.json` 12:02:06; `taban_parcalar.py` 11:31:48 (md5 `5f6f3d9e8162`).
- İzlenen 17 dosyanın md5 özeti 21.11 02:32'de eski B'nin 12:03 kaydıyla (`kaynak-bas.json`) **birebir aynı**.
- `md5-bas.txt` (11:45, B'nin zincirinden önce) ile bugün: 39 dosyanın 36'sı aynı; farklı üçü B'nin yeniden ürettiği
  `taban-analiz.json` (`sure_s`), `taban-montaj.FCStd`, `taban-montaj.step` (raporda yazıldığı gibi). 19 eski kir: `kir-bas` = `kir-simdi`.
- `git status` listesi eski B'nin 12:04 kaydıyla (`st3.txt`) aynı, ek olarak yalnız `carpisma-bolum/statik.json`.

### 13.5 Tam tarama (B2)

- Kilit 02:34'te B2 adına alındı (`FREECAD-KILIT.txt`, `dongu-158.md` kilit satırı).
- Sürücü: `planlama/d158/P108d-kontrol-olcum/b2_tarama.py` (eski `b_tarama.py` mantığı: `carpisma_kos` içe aktarılır, tek koşu kimliği,
  9 bölüm ayrı `freecadcmd` süreçlerinde sırayla, sonda `birlestir()`; ek: günlükler `b2-log/`, bölüm başı / bitişi saat damgalı
  `b2-tarama.durum`, 60 s'de bir `b2-tarama.nabiz`, izlenen 17 dosyanın özeti başta / sonda `b2-kaynak-bas.json` / `b2-kaynak-son.json`,
  özet `b2-tarama-ozet.json`). Bash arka plan koşusu; çıkış kodu sarmalayıcıyla `.durum`'a.
- 02:35:09 ilk başlatma denemesi boş geçti: `b2-log/` klasörü kabuk yönlendirmesinden önce yoktu, Python hiç başlamadı (çıkış 1, hiçbir
  dosya yazılmadı). Klasör açılıp 02:35:29'da başlatıldı: **koşu `20261121-023529`**.

- Bekleme: Bash ön plan yoklaması en çok ≈ 170 s (araç 180 s'de arka plana alıyor; 9 dk'lık ilk deneme böyle oldu), her uyanışta
  `.durum` son satırı, nabız yaşı (hep ≤ 60 s), `python.exe` / `freecadcmd.exe` süreci ve `freecadcmd` CPU süresi (sürekli arttı).
  Süreç hiç ölmedi; yeniden başlatma gerekmedi.
- Bölüm bitişleri (`b2-tarama.durum`, hepsi rc 0, sonuç yazıldı, kaynak aynı, istisna 0): statik 02:36:52 (83 s), **omuz 06:03:48
  (12.416 s)**, kol_sag 06:07:31 (223), kol_sol 06:11:13 (222), kolkol 06:12:06 (53), kafa_sabit 06:14:40 (154), kafa_sag 06:21:45 (425),
  kafa_sol 06:28:43 (418), taban 06:30:14 (90). 06:30:14 `BIRLESTIRILDI tek_kosu True toplam cakisma 364 eklem_araliginda 0`,
  `KAYNAK bas=son True`, `SURUCU_CIKIS 0`. Toplam 14.085 s (≈ 3 sa 55 dk; tahmin 3,8 sa idi). Boş bellek bölüm başlarında
  7,35–7,70 GB, nabızda en düşük 5,42 GB (02:56, kullanıcı uygulaması; tarama süreci ≈ 450 MB çalışma kümesi).
- Sonuç bölüm bölüm HEAD'deki 19.11 koşusuyla (`20261119-075818`) **aynı**: ev pozu 0; omuz 116 + 116 poz (eklem aralığında 0); kol sağ /
  sol tam 0 / 63, alt 0 / 53; kolkol 0 / 227; kafa sabit 0 / 0; kafa sağ / sol 0 / 3; taban 0. Toplam 364, eklem aralığında 0.
  Değişen yalnız taban 401 → 427 parça, kütle / AM ve sınır kutusu aday sayısı 868 → 904 (kontrol § 3.2).
- 06:31 `carpisma_kos.py kontrol` **0**; `regresyon.py --yazma` **0, GEÇER** (rampa 1,519 → 1,523 iyileşti; tilt / pan 09.11 tabanına göre
  iyileşti, P10.8d'den değil; öbürleri aynı); regresyon dosyalarının md5'i ve `git status` önce / sonra aynı.
- 06:31 B1 ölçümü (salt okuma, `b2-b1/`): yol 11 × "Sonar tutucu sol" 0,50 mm yolun **başlangıç uç kapağında**, ortak hacim 0 → uç
  teması, geçmez nedeni değil (kontrol § 4).
- 06:31 kilit "boş" (`FREECAD-KILIT.txt`); `dongu-158.md` kilit satırı "B2 bitti, C bekliyor".
- **Karar: GEÇER** (`P108d-kontrol.md`). Kontrol raporu doldu, yer tutucu yok.
- Teslim md5 listesi: `planlama/d158/P108d-kontrol-olcum/b2-teslim-md5.txt` (commit'e girecek 34 üretilmiş / kaynak / ölçüm dosyası;
  günlük, kontrol, `dongu-158.md`, `karar-kuyrugu.md` hariç, çünkü sonradan yazılabilir). 06:34'te `md5sum -c` hepsi OK.

## 14. Kapanış tarifi (C ajanı için; tek başına okunur)

Bu tarif **§ 10'un yerine** geçer (§ 10 B / B2'nin dosyalarından önce yazıldı). Komutlar depo kökünden, Git Bash. Python
`py -3 -B -X utf8`. FreeCAD **koşulmaz** (tarama ve zincir bitti; yeniden koşmak tarama kaydını eskitebilir). İşaret: **[sınandı]** B2
21.11'de aynı komutu koştu; **[DENENMEDİ]** B2 koşmadı.

### 14.1 Ölçüm (commit'ten önce, hepsi geçmeli; biri tutmazsa dur ve raporla)

| # | Komut | Beklenen |
|---|---|---|
| 1 | `git rev-parse --short HEAD; git branch --show-current` [sınandı] | `1fbe337`, `lale-duzeltme` |
| 2 | `cat planlama/d158/FREECAD-KILIT.txt; tasklist \| grep -i freecad` [sınandı] | "boş", süreç yok |
| 3 | `md5sum -c --quiet planlama/d158/P108d-kontrol-olcum/b2-teslim-md5.txt && echo OK` [sınandı, 06:34] | `OK` (34 dosya B2'nin bıraktığı gibi) |
| 4 | `cd tasarim/freecad && py -3 -B -X utf8 carpisma_kos.py kontrol; echo $?; cd ../..` [sınandı] | "carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni.", `0` |
| 5 | `py -3 -B -X utf8 -c "import json;d=json.load(open('tasarim/freecad/carpisma-sonuc.json',encoding='utf-8'));print(d['tek_kosu'],sorted({v['kosu'] for v in d['bolumler'].values()}),d['toplam']['cakisma'],d['toplam']['eklem_araliginda'],len(d['ev_pozu_cakisma']))"` [sınandı] | `True ['20261121-023529'] 364 0 0` |
| 6 | `PYTHONIOENCODING=utf-8 py -3 -B -X utf8 planlama/d158/regresyon.py --yazma; echo $?` [sınandı] | "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)", `0` |
| 7 | `grep -cE "@@[A-Z]" planlama/d158/P108d-kontrol.md planlama/d158/P108d-gunluk.md` [sınandı] | ikisi de `0` (yer tutucu yok) |
| 8 | `git status --porcelain` [sınandı] | yalnız § 14.2 ve § 14.3'teki yollar (§ 11 kuyruk metinleri uygulandıysa `planlama/d158/karar-kuyrugu.md` de) |

### 14.2 Commit'e girer (açık `git add` listesi)

```
git add -- \
  tasarim/freecad/taban/taban_parcalar.py \
  tasarim/freecad/taban/taban-analiz.json tasarim/freecad/taban/taban-bom.csv \
  tasarim/freecad/taban/taban-montaj.FCStd tasarim/freecad/taban/taban-montaj.step \
  tasarim/freecad/taban/dxf/guc-paneli-arka-5mm-kontrplak.dxf \
  tasarim/freecad/montaj/robot-montaj.FCStd tasarim/freecad/montaj/robot-montaj.step \
  tasarim/freecad/montaj/montaj-analiz.json tasarim/freecad/montaj/robot-bom.csv \
  tasarim/freecad/lale158/lale158-kontrol.json \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json \
  tasarim/freecad/carpisma-sonuc.json tasarim/freecad/carpisma-bolum \
  planlama/d158/P108d-gunluk.md planlama/d158/P108d-kontrol.md \
  planlama/d158/P108d-olcum.py planlama/d158/P108d-sema-girdi.py planlama/d158/P108d-rehber-denetim.py \
  planlama/d158/P108d-analiz-fark.py planlama/d158/P108d-e4.py \
  planlama/d158/P108d-olcum ':!planlama/d158/P108d-olcum/ara1.json' \
  planlama/d158/P108d-kontrol-olcum ':!planlama/d158/P108d-kontrol-olcum/b2-tarama.nabiz' \
  planlama/dongu-158.md
```

[DENENMEDİ: `git add`; iki dışlama yol belirteci `git ls-files --others --exclude-standard -- <aynı belirteç>` ile sınandı: `P108d-olcum`
6 JSON (ara1 hariç), `P108d-kontrol-olcum` 52 dosya (nabız hariç; 53 − 1).] `carpisma-bolum` 9 JSON'un hepsi değişti. `dongu-158.md`:
orkestratörün kilit satırı + § 5 satırları; commit'ten önce kilit tablosundaki P10.8d satırı **silinir** (§ 2 "paket bitince kilit satırı
silinir") ve plan P10.8 hücresi § 11 metniyle güncellenir: bunlar orkestratörün / C'nin kararı, B2 yazmadı. `karar-kuyrugu.md` yalnız § 11
kuyruk metinleri uygulandıysa eklenir.

Eklendikten sonra: `git diff --cached --stat | tail -1` ve `git diff --cached --name-only | grep -E "gorsel/|yerlesim-kontrol|geometri|gez.js|uc.js|ara1|nabiz|KILIT"`
**boş** olmalı [DENENMEDİ].

### 14.3 Commit'e girmez

- 19 eski kir (19.11'den, P10.8d'ye ait değil; md5 A / B / B2 boyunca aynı): `tasarim/freecad/kabuk/gorsel/*.png` (13),
  `tasarim/freecad/montaj/yerlesim-kontrol.json`, kökteki `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`,
  `uc.js` (kökteki beşi 0 bayt).
- `planlama/d158/P108d-olcum/ara1.json` (A'nın ara ölçümü), `planlama/d158/P108d-kontrol-olcum/b2-tarama.nabiz` (anlık nabız).
- `planlama/d158/FREECAD-KILIT.txt` (`.git/info/exclude`'da), `planlama/d158/regresyon.json` ve `regresyon-son-kosu.json` (değişmedi;
  taban güncellemesi ayrı karar), `planlama/maliyet.json`, `tubitak-2209b/`, Efe'nin kod dosyaları.

### 14.4 Commit mesajı önerisi [DENENMEDİ]

```
Lale P10.8d: kablo yolu 10 / 11 / 12, burç 2, acil stop düğüm kartı ve dağıtım kartı C modelde; 16 şema ve E4 ölçüldü; tam çakışma taraması

- Kablo yolu 10 ön şarj kartından 2,9 mm (0,354 mm³ → 0); yol 11 baştan (ön kesikten, 871,6 → 0 mm³); yol 12 rehber bölümü kesikten (522,1 → 0; CAD_KIRP aynı); yol 1 kart C'nin yanından
- Burç 2 akü kablo yarığından çıktı (panel oturması 0,391 → 0,895, engelsiz delikle aynı)
- Acil stop düğüm kartı ve dağıtım kartı C güç panelinde (nominal zarf ve kütle TAHMİN; M3x8 naylon burç + DIN 912); taban 388 → 414 parça, bağlantı 148 / 148, çakışma 0
- 16 şema tarandı (14 temiz; G07 / G16 ara çakışma, rehber paketine); E4 dikişi yarım bindirme, sırayı zorlamıyor
- Ana montaj 1.251 gerçek parça, boy 1.580,0, rampa 1,519 → 1,523; tam çakışma taraması tek koşu 20261121-023529: 364 / eklem aralığında 0 (HEAD ile bölüm bölüm aynı), carpisma_kos kontrol 0, regresyon GEÇER
- Rehber tarafı P10.8e'ye: sema_geometri 1 hata (SV3 × kart C), --kaynak ascii kalıntı 5, PARCA_CAD / UC_MODELSIZ, G07 / G16
- Günlük planlama/d158/P108d-gunluk.md, bağımsız kontrol P108d-kontrol.md (GEÇER; tarama 20.11'de Windows Update yeniden başlatmasıyla kesildi, 21.11'de baştan koşuldu)
```

(Önceki commit'lerdeki gibi `Co-Authored-By` satırı C'nin kendi atıf kuralına göre eklenir.)

### 14.5 Commit ve push [DENENMEDİ]

```
git commit -F <mesaj dosyası>          # mesaj dosyası depo dışında (örn. C'nin geçici klasörü)
git show --stat --format='%h %s' HEAD | tail -3
git fetch origin && git status -sb     # "## lale-duzeltme...origin/lale-duzeltme [ahead 1]" olmalı; behind varsa DUR
git push origin lale-duzeltme
git status -sb                         # "## lale-duzeltme...origin/lale-duzeltme" (ahead / behind yok)
```

`main`'e birleştirme yok. Push'tan sonra `git status --porcelain` yalnız § 14.3'teki yolları göstermeli.

## 15. C ajanı: kapanış (21.11.2026, açılış ≈ 06:36; saat okundu)

### 15.1 Kanıtın yoklanması (tarife geçmeden)

- `carpisma-sonuc.json`: `tek_kosu` True, 9 bölümün `kosu` alanı `20261121-023529`, `toplam` 364 / eklem aralığında 0, ev pozu
  çakışması 0, birleştirme notunda UYARI yok. Bölüm süreleri kontrol § 3.2 tablosuyla aynı (ör. omuz 12.353,9 + 61,4 s).
- HEAD'e göre fark (`carpisma-sonuc.json` + 9 bölüm dosyası, +189 / −189), zaman / pid alanları dışında yalnız: `taban_parcalar.py`
  özeti `d00e2075e9` → `5f6f3d9e81` (dosyanın bugünkü md5'i), taban parça 401 → 427, taban kütlesi 8.231,4 → 8.272,5, toplam kütle
  25.835,1 → 25.876,1, AM, `ev_pozu_kesisen_cift` 868 → 904, taban taramasında `hedef_sayisi` 405 → 431, `kutu_kesisen` 469 → 505,
  `tam_olcum` 143 → 159. Hiçbir çakışma sayısı değişmedi: rapor ile dosyalar uyumlu.
- B2'den sonra değişen dosya (`find -newermt "2026-11-21 06:30:15"`, `.git` hariç): yalnız kilit dosyası, bu günlük, kontrol raporu,
  `dongu-158.md`, `P108d-kontrol-olcum/b2-b1/*` ve `b2-teslim-md5.txt`. Kaynak / üretilmiş dosya değişmedi.

### 15.2 Ölçüm (§ 14.1; FreeCAD koşulmadı, kilit alınmadı)

| # | Sonuç |
|---|---|
| 1 | `1fbe337`, `lale-duzeltme`; yerel = uzak (0 / 0) |
| 2 | kilit "boş", FreeCAD / python süreci yok |
| 3 | `md5sum -c` 34 / 34 **OK** |
| 4 | `carpisma_kos.py kontrol` "guncel: izlenen 17 dosyanin ozetleri kayitla ayni.", **0** |
| 5 | `True ['20261121-023529'] 364 0 0` |
| 6 | `regresyon.py --yazma` **0**, "GEÇER (hepsi okundu, kötüleşen yok)" (rampa 1,523, tilt 3,78, pan 2,26); `git status` ve değişik / izlenmeyen dosyaların + `regresyon*.json`'un md5'i önce / sonra **aynı** |
| 7 | `@@[A-Z]` yer tutucu: iki dosyada 0 |
| 8 | `git status` yalnız § 14.2 / § 14.3 yolları |

### 15.3 Gizlilik taraması (commit öncesi; kanca `pre-push` kalıpları + geçici klasör / ev dizini / bilgisayar adı)

- Anahtar / parola / belirteç, e-posta, telefon, IBAN, ekip soyadı, takma ad: **0**. Sayı kalıbına takılan `05…` dizileri ondalık
  sayıların içinde (yanlış alarm). Resmî / başkasına ait belge, ofis belgesi yok.
- **Makine yolları:** `P108d-kontrol-olcum/` altındaki 13 kopya dosyada (B'nin JSON / günlük / betikleri ve B2'nin günlükleri) 56 yer:
  depo kökünün mutlak yolu, eski B'nin ve B2'nin geçici oturum klasörü, FreeCAD kurulum yolu, ev dizini. Betikle (dosya zamanları
  korunarak) göreli yapıldı: depo kökü → göreli yol (yalnız kök → `.`), geçici klasör → `<gecici>`, FreeCAD →
  `%LOCALAPPDATA%\Programs\…`, ev dizini → `$HOME` / `~`. `zincir.sh` / `yokla.sh`'ta `SS="${SS:-<gecici>}"` (sözdizimi `bash -n`
  geçti); JSON'lar geçerli, `b1_olc.py` ayrıştırılıyor. Sayı / ölçüm içeriği değişmedi. Bu dosyalar teslim md5 listesinde değil.
- Bu günlükte § 13.3'teki geçici klasör yolu genel ifadeyle değiştirildi. Kontrol raporu ve `dongu-158.md` farkı temiz.
- İkili dosyalar: STEP başlıkları ve iki FCStd'nin `Document.xml`'i yol / kullanıcı adı içermiyor (`FileName` / `TransientDir` boş).
  En büyük dosya `montaj/robot-montaj.step` 31,2 MB (HEAD'de 30,7 MB; izlenen dosya, P10.8d'de yeniden üretildi); başka > 10 MB yok.

### 15.4 Plan

- `dongu-158.md`: kilit tablosundan P10.8d satırı silindi; P10.8 hücresinin sonuna P10.8d kaydı (§ 11 metni + P10.8e'de açık
  kalanlar: `sema_geometri_denetle` 1 hata SV3 ↔ kart C, `--kaynak` ascii kalıntı 5, `PARCA_CAD` / `UC_MODELSIZ` / `MODELSIZ_KONUM`,
  rehber metni ve ZORUNLU kural, G07 / G16, tam rehber üretimi); § 5'e "P10.8d kapandı" girişi.
- `karar-kuyrugu.md` (§ 11 kuyruk metinleri) **uygulanmadı**: kapanış görevinde yok, § 10 orkestratörün dosyası diyor.
- `regresyon.json` tabanı (rampa 1,519) güncellenmedi (ayrı karar).

### 15.5 Commit ve push

Commit tek, açık `git add` listesiyle (§ 14.2; `P108d-kontrol-olcum` 53 dosya, nabız hariç; § 14.2'deki "52" ile fark
büyük olasılıkla en son (06:34) yazılan `b2-teslim-md5.txt`; çıkarım, doğrulanmadı). Hash ve push sonucu bu commit'in içine yazılamaz; ajan raporunda ve `git log`'da.
