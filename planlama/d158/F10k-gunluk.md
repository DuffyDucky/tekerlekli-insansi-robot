# F10k günlüğü · P10.7b2c (ilk yarı): taban kablolarının gösterim şemaları ve şema uç sınaması (kaynak düzeyinde)

15.11.2026, bitiş 12:26 (saat okundu; başlangıç saati okunmadı). Dal `lale-duzeltme`, HEAD = uzak = `b6022c3` (P10.7b2b). Kapsam: yolu
hiçbir çizimde olmayan 11 taban kablosu (T1: G07, G16, G22, SV3, G19; T2: M02; T3: B02, N01, N02, Q01, Q02), şemalara geometrik uç
sınaması (mevcut 11 şema dahil), F10j-kontrol-2 ön işi (A1–A5). Kapsam dışı: G06 (K50), G20 (K52), ikinci ajanın işi (elektronik katı kısa
telleri, kafa içi, ses kabloları), kablolar.json boy alanları. FreeCAD ve `rehber_uret.py` **koşmadı**; rehber çıktılarına
(`rehber/veri`, `planlama/rehber`) dokunulmadı. Commit, push, `git add` yok. İzlenen CAD kaynakları (`taban_parcalar.py`, `*_lib.py`,
`arayuz.py`, `kablo_yolu_ekran.py` ve öbür parça kaynakları), devre değerleri, kablo uçları, kesitler, sigortalar, `pin-haritasi.md`,
`maliyet.json`, `README.md`, `kod/`, kontrol raporları değişmedi. Paket dışı 14 dosya dokunulmadan duruyor. Başlangıç ölçümü (değişiklikten
önce koşu) bu pakette alınmadı; önceki sayılar `F10j-gunluk.md` § Üretim ve zincir'den.

## Ne yapıldı

- **Yeni şema kaynağı** `tasarim/freecad/lale158/kablo_yolu_taban.py` (saf Python, `kablo_yolu_ekran.py` kalıbı). Yalnız `arayuz.TABAN`'ı
  okur; parça değil (GLB'ye ve parça sayısına girmez; 1192 kalır), `carpisma_kos` izlemez (adı `*_lib.py` değil). `yollar()` kablo
  kimliği → global nokta listesi; `gecis_denetle(pts, r)` levha geçiş denetimi (aşağıda).
- **Tek çözücü** `rehber_kablo.sema_noktalari(kaynak, ad)`: `yollar` (kablo_yolu_ekran), `kafa_ici_qled` (tilt ekseni çerçevesi →
  global, eski `rehber_veri._bas` ile aynı), `taban` (yeni). `rehber_veri.py` şemaları artık bununla çözer (eski `KYE` / `_bas` kodu
  kalktı). Eski 11 şemanın noktaları ve `boy_mm`'i, b6022c3 üretiminin `rehber-veri.json`'uyla 0,1 mm yuvarlamada birebir aynı (11 / 11;
  FreeCAD'siz karşılaştırma betiği, karalama klasöründe).
- **SEMA** (`rehber_metin.py`): 11 yeni girdi, kaynak `taban`, kaynak adı = kablo kimliği. Adlarda kesit `{awg.X}` yer tutucusuyla
  (M02'nin kesiti kayıtta yok: "motorun kendi kablosu"); sigorta değeri yazılmadı ("hat sigortası"). Modelsiz uçta "yeri yaklaşık".
- **Dürüst etiket** (adımın `kablo` listesi; ekranda `app.js:1221`, basılıda `yazdir.html:170` aynı alanı basar): K1'e dokuz hattın, B3'e
  M02'nin, B5a'ya SV3'ün "gösterim şemasıdır: çarpışma taramasından geçmedi, parça sayısına girmez, boy ölçümü değildir" notu; neyin
  modelden, neyin tahmin olduğu ve modelsiz ucun yeri yaklaşık olduğu aynı maddede.
- `KABLO_AD 4`: "Arka sol motor (M02) bu yolda değil, şeması yok" artık yanlıştı → "… bu yolda değil: kendi gösterim şeması B3'te".
- **Şema uç sınaması** `rehber_kablo.sema_geometri_denetle()` (ana koşuda ve bozma denemesinde; CAD sınaması `geometri_denetle` ve
  sonuçları değişmedi: yol 12, hata 0, bilgi 6). Ayrıntı § Şema sınaması.

## Kararlar (bu paketin; tartışmaya açık olanlar "açık"ta)

1. Adım bağı (kablolar.json `rehber` kodlarından): K1 → G07, G16, G22, G19, B02, N01, N02, Q01, Q02; B3 → M02 (kodları B2b / B3; motor
   uçları B3'te klemense bağlanır); B5a → SV3 (kodları B5a / K2; SV3 B5a tezgâhında bağlanır). G19 B3 / K1'den K1'e (kat üstündeki uç
   K1'de bağlanır). Kablolar.json'a dokunulmadı.
2. Şemanın tek ucu: Q01 / Q02'nin öbür ucu üç noktaya (çevre 5 V, PCA9685, arayüz bölücü) gider; şema arayüz kartında biter, adında
   "Trig teli PCA9685'e gider, o ucu çizilmedi". B02'nin "ESP32 / arayüz kartı" ucu ESP32 taşıyıcısında.
3. Anahtarlı bara modelde yok: G16 / G22 şeması `MODELSIZ_KONUM`'un vekil kuralıyla (Röle K1 kutusunun yanından) başlar; dağıtım kartı
   C modelde yok: SV3'ün b ucu "elle bakıldı" (MODELSIZ_KONUM, nominal noktası yok).
4. M02, yol 4'ün arka sağ bölümünün x aynası; ama BTS'den deliğe inişte yol 4'ün aynası XL4016 B kutusuna değiyordu (0 mm, tasarım
   bakışı) → x −88'den dışından geçirildi.
5. Renk kuralı değişmedi (devre sınıfı rengi, ana kablodan).

## Her yolun dayanağı ve tahminler

Koordinat global, ev pozu, mm. "Model" = `arayuz.TABAN` ölçüsü ya da `taban-analiz.json` kutusu. Uç kutu mesafeleri tasarım bakışından
(eksen çizgisi ↔ kutu; çarpışma taraması değil).

| Kablo | Adım | Uçlar (sınıf) | Dayanak (modelden) | Tahmin | Yol | Uç kutuya |
|---|---|---|---|---|---|---|
| G07 | K1 | ana anahtar (modelli) → arayüz kartı (modelli) | anahtar ve kart kutusu; x −56 hattı sigorta kutusu (x ≥ −52) ile ön şarj kartı (x ≤ −62) arası | anahtar çıkış saplaması yeri, kat üstü hat yüksekliği (y 184), kart kenarı uç | 281 mm | 2 / 4 |
| G16 | K1 | anahtarlı bara (nominal, vekil röle) → XL4016 C (modelli) | röle ve XL4016 C kutusu | bara yeri (modelde yok), hat sigortası yeri, XL C IN klemensi kenarda | 240 mm | 2 / 4 |
| G22 | K1 | anahtarlı bara (nominal, vekil röle) → PC817 / arayüz kartı (modelli) | röle ve kart kutusu | bara ve hat sigortası yeri, kart üstü uç | 240 mm | 2 / 4 |
| SV3 | B5a | XL4016 C (modelli) → dağıtım kartı C (modelsiz, elle) | XL4016 C kutusu | dağıtım kartı C'nin yeri (yaklaşık, XL C'nin −z yanı) | 39 mm | 4 / — |
| G19 | K1 | XL4016 çevre (modelli) → arayüz kartı (modelli) | ön kat kesiği (`kat_kesik_on`), ray üstü ile kat altı boşluğu | XL OUT klemensi yeri, kat altı hat (y 155) | 219 mm | 2,5 / 4 |
| M02 | B3 | BTS7960 sol (modelli) → JGB37 arka sol (modelli) | arka motor kablo deliği Ø16 (−80; 36), plaka altı hat (yol 4 ile aynı y 87) | BTS M+ / M− klemensinin yeri, motor kablosunun motordan çıkışı (yol 4 son noktasının aynası) | 384 mm | iç / iç |
| B02 | K1 | BTS7960 sağ (modelli) → ESP32 / arayüz kartı (modelli) | ön kat kesiği | BTS sinyal başlığı yeri, ESP taşıyıcı kenarı uç | 116 mm | 2,5 / 4 |
| N01 | K1 | JGB37 arka sol (modelli) → ESP32 DevKit (modelli) | arka kablo deliği (motor kablosunun 5 mm yanında), ön kat kesiği | enkoder kablosunun motordan çıkışı, motor kablosundan ayrılma (çizilmedi: iki ayrı hat) | 617 mm | iç / 4 |
| N02 | K1 | JGB37 arka sağ (modelli) → ESP32 DevKit (modelli) | arka kablo deliği, ön kat kesiği | N01 gibi | 553 mm | iç / 4 |
| Q01 | K1 | HC-SR04 sağ (modelli) → elektronik katı / arayüz kartı (modelli) | sonar konumu (`SONAR`, `sonar_on_z`), ön ara ray (z 210…250), ön kat kesiği | pin bloğundan çıkış (PCB üst kenarı y 127), kart kenarı uç | 305 mm | 2 (tutucu) / 4 |
| Q02 | K1 | HC-SR04 orta (modelli) → elektronik katı / arayüz kartı (modelli) | Q01 gibi | Q01 gibi | 228 mm | 2 (tutucu) / 4 |

Ortak tahminler: kart üstündeki klemens / pin başlığı yeri (uç noktaları kart kutusunun kenarında, 4 mm dışında alındı), kartların
arasındaki geçiş çizgisi, kat üstü (y 184) ve kat altı (y 155) hat yükseklikleri. Kablo çapı, büküm yarıçapı ve port yeri doğrulanmadı.
Yol uzunluğu boy ölçümü değildir; kablolar.json boy alanları bu dosyadan yazılmadı (ikinci ajanın işi).

## Şema sınaması (`rehber_kablo.sema_geometri_denetle`)

- Parça kutuları: taban-analiz.json (global) + kafa-analiz.json (kafa yereli + `yerlesim.konum` [0; 1290; 0]; montaj-analiz.json
  merkezleriyle Govde / Pan / Kafa aynı fark, doğrulandı; ev pozunda tilt 0 kabulü). Filtre `geometri_denetle` ile aynı.
- Yan kuralı `_yan_sina` ile ortak (şema için parça haritası parametre: `SEMA_PARCA`, `SEMA_PARCA_BOLGE`, `SEMA_MODELSIZ`; CAD'in varsayılanı
  değişmedi). Uç kuralı: uç noktasının ≤ 10 mm yanında modelli parça (taban ya da kafa) varsa eşlenen kabloların ucu olmalı; yoksa y ≥ 400
  için bölge, değilse nominal / elle.
- Göğüs ekranı ucu "göğüs ekranı portu" bölgesinde olmalı (`kablo_yolu_ekran.uc_bolgesi`, gp çerçevesinin tersi; lale158_kontrol ile
  aynı tanım). Gerekçe: `TABAN_DISI_BOLGE`'nin "sol kol" kutusu (x ≤ −60, y ≥ 880) göğsün sol yarısını da kapsıyor; ilk koşuda üç ekran
  ucu "sol kol bölgesinde" diye düştü (yanlış alarm, sınama hatası; geometri değil).
- Tek sınıf (bilinen karışım yok); eksik eşleme yalnız bilgi; y < 400 noktası olan şemada levha geçiş denetimi **hata**:
  `kablo_yolu_taban.gecis_denetle` (alt plakada Ø16 deliğin içinde, merkeze uzaklık + r ≤ 8; katta ön kat kesiğinin içinde, R 5 köşe
  dahil, ya da akü yarıklarında; levhanın içinde yatay giden bölüm de hata).
- Eşlemesiz şema: `kablo_yolu_taban.yollar()`'daki her kimliğin SEMA'da girdisi olmalı. Kullanılmayan `SEMA_GEO_ISTISNA` girdisi de hata.
- Sonuç: 22 şema (yollar 8, kafa_ici_qled 3, taban 11); hata 0, bilgi 14, istisnalı şema 5. 11 yeni şemanın 22 yanı ve 22 ucu tamam;
  levha geçişleri: alt plaka 3 (M02, N01, N02), kat 6 (G19, B02, N01, N02, Q01, Q02), hepsi bilinen geçişte.

### Mevcut 11 şemanın bulguları (geometri düzeltilmedi; gerekçeli istisna, `SEMA_GEO_ISTISNA`, onay kaydında)

| Şema | Bulgu | Neden (kayıttan) | İstisna anahtarı |
|---|---|---|---|
| HDMI (H02) | baş Pi kutusuna 13,2 mm; baş ucu kafada eşsiz | şema fişin arka ucundan başlar (`pi_hdmi`) | H02 a, baş |
| HDMI şerit (H01) | son Pi kutusuna 25,8 mm; son ucu eşsiz | şerit fişin arka ucunda biter (`hdmi0`) | H01 a, son |
| Dizi USB (U01) | baş ReSpeaker kutusuna 19,4 mm; kafa bölgesinin x ±60 sınırı dışında | `d_uc` = kart kenarı + 35 + fiş boyu 20 | U01 b, baş |
| 12 V (G20, G21) | G20 a sigorta kutusuna 13,0 mm | baş F6 çıkışında; regülatör yeri K52'de karar bekliyor | G20 a |
| **ESP32 USB (U06)** | **taban ucu (51,6; 190; −120) ESP32'ye 114,9 mm uzak**, yanında parça yok | ESP32 9 Ekim'den beri (80; 75)'te (`arayuz` TABAN esp, git `dfe0df3`); şema ucu 5 Kasım'da (`d26c7e7`) bu noktayla çizildi | U06 b, son |

ESP32 USB ayrıca bildirilir: şemanın taban ucu ESP32'de değil, güç panelinin üstünde; K2 / F5'te bu şemaya bakan montajcı ucu yanlış
yerde görür. Şema yeniden çizilmeli (açık iş; `kablo_yolu_ekran.py` izlenen kaynak, bu pakette düzeltilmedi). Fiş istisnaları (H01, H02,
U01) çizimin hatası değil, sınamanın fiş boyunu bilmemesi; fiş boyları TAHMİN (kablo gelince ölçülecek).

## Sayım (çizilen / çizilmeyen)

`cizilen_kimlikler` bir kimliği CAD_ESLEME, SEMA ya da KOL_ESLEME'de geçiyorsa "çizilen" sayar; yeni şemalar SEMA'ya girdiği için sayıma
**gösterim şeması olarak** girer (CAD yolu gibi çarpışma taramasından geçmiş sayılmaz; ayrımı adımın kablo notu ve bu günlük taşır, sayım
aracı ayırmaz: açık). 51 / 23 → **62 / 12**. Çizilmeyen 12: G06 (K50), I01, I02, P01, P02, P03, K01, K02, K03, C01, AU1, AU2.
Ayırt edilemeyen çift 0 (önceki 1, yol 10 A03 ↔ G22: P10.7b2b'nin sınıf kuralı; bu paket değiştirmedi).

## Ön iş (F10j-kontrol-2)

- **A1** (`rehber_metin.py` F1 kontrol madde 3): "Kusuru düzeltince ölçümü akü gerilimi maddesinden baştan yinele." → "Kusuru düzeltince
  ölçümü baştan, akünün kendi gerilimini okuduğun maddeden yinele." (kontrolün önerisi, harfiyen).
- **A2** (aynı madde): "bölücü düzelip okuma aralığa girene kadar ana anahtarı yeniden açma, …" → "bölücüdeki kusuru düzeltmeden ana
  anahtarı yeniden açma, ESP32'ye bu bölücüyle enerji verme, aşama 2'ye (F5) geçme." (önerisi, harfiyen). Değer, sıra ve güvenlik
  koşulu aynı: üç yasak yerinde, yeniden ölçüm baştan; `ZORUNLU_ALAN` deseni yeni metne çevrildi.
- **A4** kural kilitleri (`rehber_denetim.py`):
  - `ZORUNLU_ALAN` F1: "Kusuru düzeltince … yinele."; madde 1 "aralığına gelince bu maddeyi baştan yinele (…)" madde sonuna kadar; madde 2
    "bölücü geçer; ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök" madde sonuna kadar (bant gevşetmesi ve söküm
    sırası); "kusur bulunmazsa" deseni madde sonuna kadar uzatıldı (`(?=\n|$)`: arkasına eklenen gevşetme yakalanır).
  - `_DIKIS_SIK`: araya bir kelime ("dikiş vidalarını sık", "dikişleri iyice sık") ve büyük harf ("DİKİŞLERİ SIK"); 13 örnekte doğru
    (olumsuz / koşul biçimleri tutmuyor).
  - `ZORUNLU_SIRA`'ya "önce" alanı `None` olan yasak satır: K2 iş metninde, dört kablo cümlesi dışında "AU3 … kafa ucunda bağla" biçimi
    geçmez (`sira_denetle` yasak satırı da sınar).
  - `ZORUNLU_BOZMA`'ya 12 deneme: A1 / A2 eski biçimleri, F10j-kontrol-2'de kaçan F1 bozmaları (yinele silindi, kapıda gevşeme, madde 2
    sonunda söküm, bant gevşedi, kusur yoksa aşama 2, kusur cümlesinin arkasına gevşetme) ve K2 (AU3 yeniden bağlandı, üç dikiş biçimi).
    Hepsi yakalandı. F10j-kontrol-2'nin "orandan yeni ölçüt eklendi" bozması metni verilmediği için birebir denenmedi; madde sonuna
    eklenirse kilitler tutar (doğrulanmadı).
- **A5** izinli ASCII listesinden kullanılmayan altısı ("kayar", "gerilimine", "pimine", "kalibrasyonuyla", "belirgin", "gelene") ve A1 /
  A2 ile kullanımdan kalkan "maddesinden", "girene" çıktı; "maddeden" (A1) ve bu paketin 7 kelimesi (modelden, dokuz, yerlerdir,
  kartlara, bakarak, durumu, sinyali) girdi. ASCII kalıntı 0.
- **A3** ve kuyrukta karşılığı olmayan kontrol maddeleri `karar-kuyrugu.md`'ye yazıldı (kayıt).

## Onay kaydı farkı (`rehber_kritik_onay.json`, `--kritik-onay-yenile`; eski kopya karalama klasöründe, küme farkı)

Aracın sayımı 73 fark; küme farkıyla (yer, metin) 80 girdi. Kablo 100 → 143, liste 198 → 202, metin 1000 → 1019.

- **Kablo** (çıkan 0, giren 43): `SEMA_ESLEME` 22 (her şema: kaynak, ad, adım = kimlikler; eski 11 de, geometrinin ayırt edemediği şema
  eşlemesini kilitler), `SEMA_GEO_ISTISNA` 9, `SEMA_PARCA` 9, `SEMA_PARCA_BOLGE` 1, `SEMA_MODELSIZ` 1, `SEMA_KAYNAK` 1. Eski CAD tabloları
  aynı.
- **Liste** (çıkan 4, giren 8): `ZORUNLU_ALAN` F1 A2 deseni (eski → yeni), "kusur bulunmazsa" (madde sonuna kadar), yeni üç F1 deseni;
  `ZORUNLU_SIRA` K2 iki satırın `_DIKIS_SIK`'i (eski → yeni), yeni K2 yasak satırı.
- **Metin** (çıkan 3, giren 22): F1 madde 3'ün iki cümlesi (A1, A2: eski → yeni), KABLO_AD 4 (eski → yeni); K1 kablo notu 4 cümle, B3 2,
  B5a 2; 11 yeni SEMA adı.
- Kritik değer değişimi yok (yer tutucular aynı); silinen uyarı yok.

## Sınamalar (FreeCAD'siz, 12:26'ya kadar; hepsi çıkış 0)

| Koşu | Çıkış | Sayılar |
|---|---|---|
| `planlama/adim3/kablolar_uret.py --kontrol` | 0 | kablolar.md ve elektrik.md bloğu güncel |
| `planlama/adim3/kablolar_denetim.py` | 0 | GEÇER |
| `rehber_denetim.py --kaynak` (yenilemeden önce) | 1 | yalnız onay farkı 73; ASCII 0, zorunlu eksik 0, yasak 0, çıplak sayı 0 |
| `rehber_denetim.py --kaynak` (yenilemeden sonra) | 0 | metin 561; onay farkı 0 (kablo 143, liste 202, metin 1019); tamlık 172, eksik 0, muaf 21; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 243 / 243 (bu paketin 12'si dahil) |
| `rehber_kablo.py` | 0 | çizilen 62 / çizilmeyen 12; CAD geometri hata 0, bilgi 6; şema 22, hata 0, bilgi 14, istisnalı 5; ayırt edilemeyen 0; onay tutuyor |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | eşlemesiz çizim 0 (veri eski üretim: 49 şema) |
| `rehber_kablo.py --bozma-denemesi` | 0 | 54 / 54 (b45–b54 yeni) |
| `rehber_kablo.py --veri … --bozma-denemesi` | 0 | 62 / 62 |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, kaynak fark 0,0007 mm, GEÇTİ |
| `node --check rehber/app.js` | 0 | |

Yeni şema bozmaları (hepsi "denetim" mekanizmasıyla, onay kaydı olmadan): b45 N01 şemasına N02 (yanlış uca bağlı yol), b46 G19 sonu 30
mm kartın dışına (eşik dışı uç), b47 N01 SEMA'dan silindi (eşlemesiz şema), b48 Q01 B5a'da (yanlış adım), b49 N02 kat kesiği dışından,
b50 M02 alt plakayı deliksiz geçiyor, b51 ESP32 USB istisnası silindi, b52 SV3 + G16 iki sınıf, b53 PAM8403 `SEMA_PARCA`'dan çıktı, b54
Dizi USB'ye U03 (mevcut şema). Depoda `__pycache__` yok (`-B`, `PYTHONDONTWRITEBYTECODE`).

## Üretimde beklenecek sayılar ve bakılacak kareler

- Parça 1192 (değişmez), şema 49 → **60** (SEMA 22 + kol 38), çizilen **62 / 12**, alt adım 71 (K1, B3, B5a'da alt adım yok; şema alt
  adım uyarısı beklenmez), `rehber_veri` günlüğü "gosterim semasi: 22". `rehber_kol_kablo` kol şemalarının ilk sırası 11 → 22 olur.
- Kareler: **K1** (dokuz yeni şema; kat üstünde x 35–40, z 90–160 arası G19, B02, N01, N02 yan yana; kat kesiğinde altı hat), **B3**
  (M02, plaka altı ve arka delik), **B5a** (tezgâh adımı: SV3 şemasının panelin üstünde, XL4016 C'nin yanında durduğu; tezgâh görünümü
  şemayı global konumda çizer mi, bakılmadı). Basılı: K1'in kablo listesi bir madde uzadı (K1 P10.7b2a'da basılıda taşmıştı): PDF tamlık
  ve taşma; B3, B5a'nın kablo notu.

## Eski yollarla çelişkiler ve okunurluk

- G19 şeması ↔ CAD yol 9'un XL4016 sonrası eski kısmı (doğrudan ESP32'ye): ikisi aynı adımda görünür; yol 9 düzeltilmedi (GEO_ISTISNA 9
  yerinde, KABLO_AD 9 "bu şemada çizili değil" doğru kalıyor).
- M02 ↔ yol 4: M02 yol 4'ün arka sağ bölümünün aynası; KABLO_AD 4 metni güncellendi. N01 / N02 ↔ yol 12 (B01'in eski üst kısmı): çelişki
  yok, ayrı hat.
- Okunurluk: K1'de altı sinyal hattı (G07, B02, N01, N02, Q01, Q02) aynı mor renkte; ESP32 kenarında üç uç 12 mm arayla (z 66 / 78 /
  90); N02 plaka altında yol 4'ün arka sağ bölümüyle 5 mm aralıkla paralel (turuncu ↔ mor, ayrılır). Renk kuralı değiştirilmedi; ayrım
  tıklama kartındaki kimlikle.

## İkinci ajan için altyapı (elektronik katı kısa telleri, kafa içi, ses)

1. Kaynak: `tasarim/freecad/lale158/kablo_yolu_<ad>.py`, `yollar()` → {kimlik: [(x, y, z), …]} (global, ev pozu, mm; saf Python, yalnız
   `arayuz` okur). Taban için `kablo_yolu_taban.py`'ye eklemek de olur (kaynak `taban`).
2. Yeni kaynak adı: `rehber_kablo.SEMA_KAYNAK`'a ve `sema_noktalari()`'na bir dal (rehber_veri.py otomatik kullanır). Kafa yerelinde
   tanımlanan yol için `kafa_ici_qled` dalındaki dönüşüm örnek.
3. `rehber_metin.SEMA`'ya `(kaynak, ad, adım, görünen ad, (kimlik, …))`; adım kablonun kablolar.json `rehber` kodlarından biri; adda kesit
   `{awg.X}`, değer yer tutucusuz yazılmaz; modelsiz uçta "yeri yaklaşık". Şema tek devre sınıfı taşır.
4. Uç parçası `PARCA_CAD`'de yoksa `SEMA_PARCA`'ya: kafa / taban model adı deseni, ya da `TABAN_DISI` + `SEMA_PARCA_BOLGE`, ya da
   `MODELSIZ` + `SEMA_MODELSIZ` (gerekçe). Kafa parçaları zaten listede (kafa-analiz.json; Pi, QLED, D24V50F5, SY8205, PAM8403, ReSpeaker).
5. `rehber_kablo.py` koş: yan / uç hatası çıkarsa önce çizimi düzelt; gerçekten düzeltilemezse `SEMA_GEO_ISTISNA[(ad, "baş" | "son" |
   "<kimlik> <yan>")]` gerekçesiyle. Taban altına inen yol levha geçişinden otomatik sınanır. "Eşlemesiz şema" denetimi bugün yalnız
   `taban` kaynağının bütün kimliklerini arar: yeni tam kaynak eklenirse `sema_geometri_denetle`'nin sonundaki döngüye eklenmeli (açık).
6. Adımın `kablo` listesine "gösterim şemasıdır: çarpışma taramasından geçmedi, parça sayısına girmez, boy ölçümü değildir" notu.
7. `rehber_denetim.py --kaynak` → ASCII kelimeleri; `--kritik-onay-yenile` (eski kaydı önce kopyala, küme farkını günlüğe yaz).
8. Boy: yol uzunluğu `kablo_yolu_taban.uzunluk()` ile okunur, boy ölçümü değildir.

## Doğrulanamayanlar / açık

- Yeni şemalar çarpışma taramasından geçmedi (FreeCAD yok); tasarım bakışında uçlar dışında kutu teması: M02 ve N01 / N02'nin akü
  kayışlarına 2,6–3 mm, Q01 / Q02 sonar tutucusuna 2 mm (eksen ↔ kutu; tüp yarıçapı 2,5).
- Kart üstü klemens / başlık yerleri, bara ve dağıtım kartı C'nin yeri, sonar pin bloğu çıkışı, motor kablosu çıkışı: tahmin.
- Kafa-analiz kutularının ev pozunda tilt 0 kabulü (montaj-analiz merkezleriyle fark aynı; tilt açısı ayrıca okunmadı).
- Tezgâh adımında (B5a) şemanın görünümü, K1 / B3 / B5a kareleri ve basılı sayfalar: üretim koşmadı, bakılmadı.
- Sayım aracı gösterim şemasını CAD yolundan ayırmıyor (62'nin 11'i taranmamış şema): ayrı sayım istenirse araç işi.
- ESP32 USB şemasının taban ucu (mevcut şema, yukarıda): yeniden çizilmedi.

## İkinci yarı (ajan B)

15.11.2026, 12:30–13:01 (saat sistemden). Ajan A'nın altyapısı kullanıldı; A'nın yaptığı hiçbir şey geri alınmadı. FreeCAD ve rehber
üretimi koşmadı; commit yok.

### Yapılanlar

| Kablo | Adım | Gösterim | Uç sınıfları | Sınama |
|---|---|---|---|---|
| I01, I02, P01, P02 | B6a | bağlantı tablosu (`{bag.<kimlik>}`) | kayıttaki iki uç, kart / başlık adı | GPIO ve PCA kanal adı pin-haritası JSON'una çapraz sınandı, geçer |
| P03 | K1 | bağlantı tablosu | PCA9685 ↔ dağıtım kartı C | geçer |
| K01 | E3a | kafa içi şema | giriş kartı (NOMINAL) → D24V50F5 | yan / uç geçer |
| K02 | E3a | kafa içi şema | giriş kartı (NOMINAL) → SY8205 | yan / uç geçer |
| K03 | E3a | kafa içi şema | D24V50F5 → Pi 5 USB-C | yan / uç geçer |
| C01 | E4 | kafa içi şema | Pi 5 CSI → Kamera | yan / uç geçer |
| AU1, AU2 | E4 | ortak kafa içi şema, etiketli | ReSpeaker jakı → ses bölücüsü (NOMINAL) → PAM8403 | yan / uç geçer |

- Yeni dosya `tasarim/freecad/lale158/kablo_yolu_kafa.py`: noktalar kafa-analiz yerelinde; global = (x, Y0 + y, z), Y0 = 1290
  (arayüz S3 + SG / 2). Dayanak: `kafa-analiz.json` kutuları (Pi 5, D24V50F5, SY8205, PAM8403, ReSpeaker, QLED, kafa iskeleti tablası).
  TAHMİN noktaları dosya başında işaretli: kafa giriş kartı (−58, 224, 30), Pi USB-C (−31,3, 231, 3), Pi CSI (9,5, 236, 1), D24 sağ
  kenar −69, SY8205 girişi (12, 225, 39), ReSpeaker jakı (82, 280, −9), PAM giriş pedi (−121, 262, 8).
- Tablolar yalnız kayıttan (kablolar.json uçları, pin-haritasi.md JSON bloğu `pinler`, `pca9685_kanallar`); kayıtta olmayan pin sırası /
  dağıtım kartı C giriş pini "kayıtta yok" yazılıyor, uydurulmuyor.
- AU1 / AU2 şeması görünen etiket taşıyor: bölücünün yeri ve varlığı KT2'ye bağlı, jak yeri tahmin. E4 alt adımı "Sol arka kabuk → kafa"
  metnindeki eski "şeması yok" cümlesi güncellendi (aşağıda eski / yeni).
- `rehber_kablo.py`: kaynak `kafa_ici`, `SEMA_KONUM` (giriş kartı nominal noktası `kablo_yolu_kafa.giris_karti_global()` ile sınanır;
  bölücü PAM8403 kutusuna bağlı), nominal uç dalı, eşlemesiz şema denetimi bütün kaynaklarda (muaf: `yollar` içindeki iki eski ses yolu,
  "Ses karti uzatmasi" ve "3,5 mm -> PAM"; muaf kullanımda değilse ya da kaynakta yoksa hata), üç sınıflı sayım, `BAGLANTI_TABLOSU`,
  `sema_boy` alanı (yazıcı `--sema-boy-yaz`, biçim gidiş-dönüş sınamalı).
- `rehber_deger.py`: yer tutucu `{bag.<kimlik>}`; `rehber_uret.py` kontrol.json `kablo_esleme`'ye yol_cizimi / yol_kaynak /
  baglanti_tablosu / hicbiri ve şema-geometri / bağlantı / şema boyu hatalarını yazar (koşmadı).
- `planlama/adim3/kablolar.json` sürüm 5: 27 kabloya `sema_boy` (boy / boy_tahmin ve `maliyet.json` dokunulmadı); kablolar_uret.py
  kablolar.md'de "şema N mm (gösterim şeması yolu; ölçüm değil)" ekler; kablolar_denetim.py `s_sema_boy` sınaması ve 5 bozma.

### Sayım (üç sınıf)

yol çizimi 68 (kaynağa göre, örtüşmeli: CAD 39, şema 29, kol 6) / bağlantı tablosu 5 (I01, I02, P01, P02, P03) / hiçbiri 1 (G06).
Hedef tuttu. Kaynak örtüşmesi: bir kablo hem CAD yolunda hem şemada olabilir, sınıf sayısı tekildir (68 + 5 + 1 = 74).

### Şema boyu

Şema 27 (yollar 8, kafa_ici_qled 3, taban 11, kafa_ici 5); hata 0. Şemadan uzun kayıt yok: risk tablosu boş. En dar paylar: K05 −16,
U01 −25, H01 −46, N02 −47 mm.

| Kablo | Kayıt (mm) | Şema (mm) | | Kablo | Kayıt (mm) | Şema (mm) |
|---|---|---|---|---|---|---|
| K01 | 200 (tahmin) | 14 | | H02 | 950 | 757 |
| K02 | 200 | 71 | | K04 | 300 | 114 |
| K03 | 200 | 47 | | K05 | 80 | 64 |
| C01 | 300 | 70 | | M02 | 600 | 384 |
| AU1 (AU2 ortak) | 300 | 219 | | N01 | 800 | 617 |
| AU3 | 1030 | 824 | | N02 | 600 | 553 |
| B02 | 400 | 116 | | Q01 | 550 | 305 |
| G07 | 450 | 281 | | Q02 | 450 | 228 |
| G16 | 400 | 240 | | SV3 | 300 | 39 |
| G19 | 300 | 219 | | U01 | 110 | 85 |
| G21 (G20 ortak) | 1720 | 1376 | | U03 | 920 | 617 |
| G22 | 500 | 240 | | U04 | 350 | 217 |
| H01 | 300 | 254 | | U05 | 640 | 395 |
| | | | | U06 | 1360 | 971 |

Kafa içi şema boyu gerçek döşemeden kısadır (K01 14 mm): kayıt boyunun yerine geçmez.

### Kafa içi kesişim ölçümü

Yöntem (FreeCAD'siz, betik çalışma dizini dışında): şema ekseni 0,5 mm adımla örneklenir, her örneğin `kafa-analiz.json` kutusuna en
kısa uzaklığı alınır, açıklık = uzaklık − tüp yarıçapı. Sonuç: kablonun kendi ucu olmayan modelli parçaya giren şema yok. SY8205: yalnız
K02'nin kendi ucu (−0,9 mm, klemens ucu); öbürleri ≥ 11,2 mm (C01 11,2, K03 47,9, AU1 49,6, K01 69,2). K01 / K02 kafa iskeleti tablasına
oturuyor (0,0). C01 QLED'e 2,6 mm; AU1 kendi uç parçaları PAM / ReSpeaker'a 3,0 / 3,9 mm. Kabuk (Baskı) kutuları içi boş olduğundan bu
yöntemle değerlendirilemez. Tilt 0 kabul edildi.

### U06 kararı

U06 şeması değiştirilmedi, istisna yerinde. (a) Taşımak çarpışma taramasının izlediği dosyayı değiştirmez (`kablo_yolu_ekran.py`
`carpisma_kos.py` KAYNAK_SABIT listesinde değil). (b) Ama U06'nın boy kaynağı `lale158-kontrol.json#kablo_ozet` (FreeCAD `KY.ozet()`)
ve aynı dosyanın tüp çarpışma sonucu eskir: düzeltme FreeCAD koşusuyla birlikte yapılmalı (açık, karar-kuyrugu).

### Ajan A'nın işine dokunulanlar (eski / yeni)

- `rehber_denetim.TAMLIK_MUAF` GPIO deseni: eski `I2C_SDA|I2C_SCL|UART0_TX|UART0_RX`, yeni `UART0_TX|UART0_RX`. Neden: bağlantı tabloları
  I2C pinlerini rehbere getirdi, denetim "muaf ama rehberde geçiyor" diyordu. Eski değer kodda yorum olarak duruyor.
- E4 alt adım 4 `is_`: eski "Ses kablosunun şeması yok (ReSpeaker sağ kabukta; eski şema ses kartından çiziliyordu, kaldırıldı).",
  yeni "Ses kablosunun çizimi gösterim şemasıdır: bölücünün yeri ve varlığı KT2'ye bağlı, ReSpeaker jakının yeri tahmin." Talimatın
  değeri, sırası, güvenlik koşulu değişmedi; yalnız şema durumu cümlesi.

### Onay kaydı farkı (40 madde)

Kablo 143 → 161, liste 202 (1 değişti), metin 1019 → 1038.

- Kablo eklendi: BAGLANTI_TABLOSU 5, SEMA_BOY_ETIKET 1, SEMA_ESLEME 5, SEMA_ESLEMESIZ_MUAF 2, SEMA_KONUM 2, SEMA_PARCA 3.
- Değişti: SEMA_KAYNAK (kafa_ici eklendi); LISTE TAMLIK_MUAF (I2C çıktı); E4 alt adım 4 `is_` (yukarıda).
- Metin eklendi: B6a kablo 6, E3a kablo 3, E4 kablo 2, K1 kablo 2, SEMA AU1 2, C01 1, K01 1, K02 1, K03 1.

### Sınamalar (hepsi çıkış 0)

| Koşu | Sonuç |
|---|---|
| kablolar_uret --kontrol | güncel |
| kablolar_denetim | GEÇER, 21 sınama |
| kablolar_denetim --bozma-denemesi | 172 / 172 (A'da 167) |
| rehber_denetim --kaynak | yenilemeden önce çıkış 1 (40 fark), sonra 0: metin 574, ASCII 0, elektrik 0, onay farkı 0, tamlık 172 / eksik 0 / muaf 19, kablo 74 / 74 |
| rehber_denetim --bozma-denemesi | 243 / 243 |
| rehber_kablo | GEÇER, onay tutuyor |
| rehber_kablo --veri | GEÇER, eşlemesiz çizim 0 |
| rehber_kablo --bozma-denemesi | 70 / 70 (b55–b70 yeni; yalnız onayla yakalanan yok) |
| rehber_kablo --bozma-denemesi --veri | 78 / 78 |
| rehber_kol_kablo --yazma | 38 bölüm, GEÇTİ |
| node --check rehber/app.js | 0 |

### Beklenen üretim

Parça 1192 (değişmez); SEMA 22 → 27; şemalar 60 → 65 (kol ilk dizini 27); alt adım 71. PDF büyük olasılıkla ≥ 80 sayfa (B6a, K1, E3a, E4
kablo listeleri uzadı). Bakılacak kareler: E3a tezgâh (K01–K03), E4 "Sol arka kabuk → kafa" (AU1) ve "Kablolar + yüz grubu → kafa"
(C01), basılı B6a / K1 kablo listelerinde taşma.

### Okunurluk kaygıları

- Uygulama şema tıklamasında `boy_mm`'den "~N mm" gösterir: K01 "~14 mm" yanıltıcı olabilir (uygulama değiştirilmedi).
- Kayıt adı "Dağıtım kartı C (kafa)", kart güç panelinde: tablo adı aynen gösteriyor.
- Bağlantı tablosu satırları uzun; ses ve K hatlarında TAHMİN noktaları var.

### Doğrulanamayanlar / açık

- Jak, Pi CSI ve kamera konnektörü, SY8205 girişi, D24 pini, Pi USB-C yerleri ve kafa giriş kartının yeri tahmin.
- Kafa içi şemalar çarpışma taramasından geçmedi; kareler ve basılı sayfa görülmedi (üretim koşmadı); tilt 0 kabulü.
- Sayım günlüğü: `yol_kaynak` örtüşmeli sayılır (bir kablo CAD ve şemada); sınıf sayımı tekildir.
- AU1 / AU2: KT2 sonucu gelince şema ve kayıt birlikte güncellenmeli.

## Düzeltme turu 1

15.11.2026, 13:24–13:36 (saat sistemden). Girdi: bağımsız kontrol `planlama/d158/F10k-kontrol.md` (DÜZELTME GEREKLİ, 3 kalem) ve
orkestratörün kararları (D1–D3, dar ekler, kuyruk). FreeCAD ve rehber üretimi koşmadı; rehber çıktılarına (`rehber/veri`,
`planlama/rehber`) dokunulmadı; commit, push, `git add` yok. Devre değerleri, kablo uçları, kesitler, sigortalar, boylar (`boy`,
`boy_tahmin`, `sema_boy`), `kablolar.json`, `pin-haritasi.md`, izlenen CAD dosyaları, `maliyet.json`, `README.md`, `kod/`, kontrol
raporları ve paket dışı 14 dosya değişmedi. Talimat metninde yalnız D2 ve D3'ün eklediği bilgi; mevcut cümlelerin değeri, sırası ve
güvenlik koşulu aynı.

### D1 · Tıklama kartındaki "~N mm" kesim boyu sanılmasın

- Yer: `rehber/app.js` `semaSec`. Eski: `Kablo şeması · adım N (KOD) · ~39 mm`. Yeni (gösterim şeması): `Kablo şeması · adım N (KOD) ·
  çizim yolu ~39 mm (kesim boyu değil)`. Basılı sayfa (`yazdir.html`) sayıyı göstermiyor ("(şema)"), değişmedi; `stil.css` değişmedi.
- Dokunulan: rehber_metin.SEMA'dan gelen 27 gösterim şemasının hepsi (yollar 8, kafa_ici_qled 3, taban 11, kafa_ici 5; eski K04, U03,
  U04 dahil). Eski "yollar" / "kafa_ici_qled" şemalarında sayı kayıttaki `yol_mm` ile aynı, ama kesim boyu `onerilen_mm` / `liste_mm`
  (ör. K04 114 / 300): bu yüzden onlar da etiketli.
- Dokunulmayan: taranmış CAD yolları (12 "Kablo yolu N" parçası: tıklama kartı sayı göstermiyor, değişecek bir şey yok) ve 38 kol içi
  bölüm (veride `kol` alanı olanlar; "~N mm" aynı kaldı). Kol bölümünün sayısı bölümün kendi uzunluğu (ör. 23 mm): kayıttaki boy (S02–S08
  `gereken_mm`, dirsek-analiz) değil, onunla aynı da değil; kesim boyu sanılma riski düşük ama sıfır değil: kuyrukta.
- `boy_mm` alanı silinmedi.
- Kilit: `rehber_kablo.sema_boy_etiketi_denetle` app.js'in `semaSec`'ini okur, etiket ifadesini (`SEMA_BOY_APP`, onay kaydında) arar ve
  `boy_mm`'in başka yerde gösterilmesini HATA sayar; `veri_denetle` kol bölümü olmayan şemada `kol` alanını HATA sayar (etiket `kol`a
  bakar). Ana koşuda ve `rehber_uret.py`'nin kontrol.json `kablo_esleme` hatalarında (koşmadı). Bozmalar: b71 etiketsiz "~N mm", b72
  "(kesim boyu değil)" silindi, b73 etiket kol bölümüne kaydı, b74 boy başka yerde etiketsiz; v9 gösterim şemasında `kol` alanı. Hepsi
  "denetim" mekanizmasıyla yakalandı.

### D2 · U06 şemasının yanlış çizilen taban ucu

- Yer: `rehber_metin.py` K2 `kablo` listesi, "Taban şeması 12'nin …" maddesinden sonra yeni madde (şema yeniden çizilmedi):
  `"ESP32 USB" şemasının (U06) taban ucu yanlış yerde, güç panelinin üstünde çizili (şema yeniden çizilecek): kablonun taban ucu
  elektronik katındaki ESP32 taşıyıcısında ESP32'nin USB girişine takılır`
- Dayanak: `SEMA_GEO_ISTISNA` ("ESP32 USB", "U06 b" / "son"; uç (51,6; 190; −120), ESP32'ye 114,9 mm); ESP32'nin rehberdeki yeri B6a
  ("kartları kata tak (… ESP32 taşıyıcı)"), şema adlarında "ESP32 taşıyıcısı". Kablonun taban ucu K1 madde 7'de bağlanır.
- Kilit: `ZORUNLU_ALAN` ("K2", "kablo"; madde sonuna kadar). Bozmalar (`ZORUNLU_BOZMA`): cümle silindi, uç "şemadaki yere" bırakıldı,
  "yanlış yerde" silindi, arkasına "şüphede şemaya uy" eklendi: 4 / 4 yakalandı. ASCII listesine "panelinin" girdi (Türkçe harfi olmayan
  doğru yazım).

### D3 · P03 tablosunda dağıtım kartı C'nin yeri

- Yer: `rehber_metin.py` K1 `kablo`, P03 satırı. Eski: `… → Dağıtım kartı C (kafa) tilt sinyal girişi. Dağıtım kartı C modelde yok,
  yeri çizilmez; …`. Yeni: `… → Dağıtım kartı C (kafa) tilt sinyal girişi. Dağıtım kartı C (kafa): kart güç panelinde, XL4016 C'nin
  yanında; adındaki "kafa" beslediği pan / tilt servolarıdır. Dağıtım kartı C modelde yok, yeri çizilmez; …`. Kayıttaki ad
  (`kablolar.json`) değişmedi; `{bag.P03}` kayıttan aynen kalıyor.
- Dayanak: `kablolar.json` karar P7b2a-6 ("Dağıtım kartı C güç panelinde, XL4016 C'nin yanında"); B5a iş metni ("dağıtım kartı C (kafa
  servolarının hattı C; XL4016 C'nin yanında) da burada").
- Aynı adın montajcıya "kafa" diye göründüğü öbür yerler (rehber metinlerinde başka yok; hepsi kayıttan gelen kb satırı): B5a'da SV3
  şemasının tıklama kartı ve kablo listesi satırı; K2'de CAD "Kablo yolu 6"nın (S09, S10) kartı ve kablo listesi satırı; P03'ün kb
  satırı (çizimi yok, bugün gösterilmiyor). Aynı ek `rehber_kablo.UC_YER_EK` ile kb satırına girer (`bilgi_satiri`): `SV3: XL4016 C ·
  OUT+ → Dağıtım kartı C (kafa) (kart güç panelinde, XL4016 C'nin yanında; adındaki "kafa" beslediği pan / tilt servolarıdır) · V+ ·
  16 AWG …`. `kablolar.md` (kayıt görünümü) değişmedi. B5a iş metnindeki "dağıtım kartı C (kafa servolarının …)" zaten yerini yazıyor.
- Kilit: `ZORUNLU_ALAN` ("K1", "kablo") ve yapısal kural `rehber_kablo.uc_yer_eki_denetle` (adı geçen her görünen metinde ek: adım
  metinleri, şema adları, KABLO_AD, 74 kb satırı; ad hiç geçmezse de HATA). Bozmalar: `ZORUNLU_BOZMA` 2 (ek silindi, "kart kafada");
  `rehber_kablo` b82 K1 eki silindi, b83 kb satırında ek yok, b84 yeni metinde ad eksiz: hepsi yakalandı.

### Dar ekler

- **KABLO_AD 9, 11, 12** (`rehber_metin.py`; yalnız doğru olduğu kimlikler, hepsinin şeması K1'de): 9 "… bu şemada çizili değil" →
  "… bu şemada çizili değil: kendi gösterim şeması K1'de" (G19); 11 "Orta ve sağ sonar (Q01, Q02) bu şemada değil" → "…: kendi gösterim
  şemaları K1'de"; 12 "Enkoderler (N01, N02) ve BTS sağ (B02) bu şemada değil." → "…: kendi gösterim şemaları K1'de." (ESP32 USB
  cümlesi aynı).
- **E3a notu**: "çarpışma taramasından geçmedi, boy ölçümü değildir" → "çarpışma taramasından geçmedi, parça sayısına girmez, boy
  ölçümü değildir". (E4 notunda da bu ifade yok; kapsam dışı, kuyrukta.)
- **SV3 kart ucu nominal nokta**: `rehber_kablo.SEMA_KONUM[("Dağıtım kartı C", "*")]` = (100; 192; −60), kaynak
  `kablo_yolu_taban.DAGITIM_C` (SV3'ün son noktası; değer aynı, şema boyu 39 mm değişmedi). Dayanak: kart modelde yok; kayıtta güç
  panelinde, XL4016 C'nin yanında (P7b2a-6; SV3 `boy_tahmin` "XL4016 C klemensinin yanında"); nokta XL4016 C'nin −z yanında,
  kutusundan 36,5 mm: TAHMİN, yeri yaklaşık. Şema sınaması iki noktanın aynı olduğunu sınar (kafa giriş kartıyla aynı kalıp). SV3'ün b
  yanı artık "elle bakıldı" değil, nominal noktayla sınanıyor (şema bilgisi 16 → 15). CAD yolu 6'nın kart yanı `MODELSIZ_KONUM`'da
  "elle" kaldı (o yol kartı çizmiyor). Bozmalar: b75 uç panelin öbür köşesinde (x −100; kontrolün denemesi), b76 uç 30 mm öteye, b77
  nominal kaynaktan ayrıldı: hepsi geometri / tutarlılık sınamasıyla ("denetim"), `sema_boy` tazeliğine kalmadan. "Yeri yaklaşık" SEMA
  adında duruyor ve aşağıdaki kuralla zorunlu.
- **Gösterim şeması notu yapısal kural** `rehber_kablo.sema_not_denetle` (onay kaydından bağımsız; kural tablosu `SEMA_NOT` onay
  kaydında): çarpışma taramasından geçmeyen kaynakların (`taban`, `kafa_ici`; 16 şema) her şeması için adımın kablo listesinde
  "gösterim şemasıdır", kaynak dosyası, "çarpışma taramasından geçmedi", "boy ölçümü değildir" geçen not; notun "gösterim şemasıdır"dan
  önceki kısmı şemanın bütün kimliklerini anmalı; modelsiz / nominal uçlu şemanın adında "yeri yaklaşık" (ses bölücüsünde "yeri ve
  varlığı kesin değil"). Bozmalar: b78 B5a notu silindi, b79 SV3 adından "yeri yaklaşık" silindi, b81 E3a notunda K02 anılmıyor.
  Kapsam dışı: eski `yollar` ve `kafa_ici_qled` şemaları (E4'te H01, U04, K04, U01, K05; F3'te U05 için adımda not yok; K2'deki not
  başka biçimde). Not eklemek talimat metni işi: kuyrukta.
- **Yanlış adıma taşınan şema (G19 → B3)**: aynı kural yakalıyor (b80: B3'ün notu yalnız M02'yi anıyor). Dar düzeltmeyle oldu, ayrı
  sınama gerekmedi. Sınır: hem şema taşınır hem not elle değiştirilirse yalnız onay kaydı yakalar (not metni kayıtta).

### Ek (orkestratör kararı, 13:40–13:47): kol bölümünün "~N mm" etiketi

- Yer: `rehber/app.js` `semaSec`, kol dalı. Eski: `Kablo şeması · adım N (KOD) · ~23 mm`. Yeni: `Kablo şeması · adım N (KOD) · bölüm
  uzunluğu ~23 mm (kesim boyu değil)`. 38 kol bölümünün hepsi; `boy_mm` ve `kol` alanları aynı. Yukarıdaki D1 maddesinde "kol
  bölümlerinde ~N mm aynı kaldı" yazanlar bu ekle geçersiz.
- Kilit: aynı `sema_boy_etiketi_denetle` (`SEMA_BOY_APP` iki dalı da arar). Bozmalar: b85 kol bölümünde etiketsiz "~N mm", b86 kol
  bölümünde "(kesim boyu değil)" silindi (yeni); b72 artık yalnız gösterim şemasının etiketini bozar; b73 "iki etiket yer değiştirdi".
  v9'un hata iletisi ("kartta çizim yolu yerine bölüm uzunluğu diye gösterilir") güncellendi.
- Montajcıya mm cinsinden uzunluk gösteren başka yer (dokunulmadı, liste): `app.js` adım parçalarının y aralığı ipucu (model
  koordinatı ve yerden yükseklik, uzunluk değil); `yazdir.html` yalnız sayfa üstünde "ölçüler mm" (sayı yok); kb satırları boy
  taşımıyor. Kart ve basılı sayfanın gösterdiği iş metinlerinde (`rehber_metin.py`) K2'nin "Önerilen boylar (yol × 1,25 …; tahmin):
  HDMI 950, hub uzatması 920, ESP32 USB 1.360, hoparlör 1.030, göğüs 12 V 1.720 mm" cümlesi kayıttaki `onerilen_mm` ile aynı (H02,
  U03, U06, AU3, G21); öbür mm sayıları parça ölçüsü ya da tarama mesafesi (ör. JR çifti 26 mm, giriş yolu 138 mm), kablo boyu değil.
- Onay kaydı: kablo bölümünde 1 değişen girdi (`SEMA_BOY_APP`; 165 → 165, liste 204, metin 1040 aynı).
- Sınamalar 13:48'de yeniden (aşağıdaki 11 koşunun hepsi, çıkış 0): sayılar aynı, yalnız `rehber_kablo --bozma-denemesi` 86 / 86 ve
  `--veri … --bozma-denemesi` 95 / 95 (b85, b86 her iki kipte); `rehber_denetim --kaynak` onay farkı 0.

### Onay kaydı farkı (`rehber_kritik_onay.json`, `--kritik-onay-yenile`; eski kopya karalama klasöründe, küme farkı)

18 girdi (ek öncesi; ek 1 girdiyi daha değiştirdi, yukarıda): kablo 161 → 165, liste 202 → 204, metin 1038 → 1040.

- Kablo (çıkan 0, giren 4): `SEMA_KONUM` Dağıtım kartı C (100,0; 192,0; −60,0); `SEMA_BOY_APP` (app.js etiket ifadesi); `SEMA_NOT`
  (kural tablosu); `UC_YER_EK`.
- Liste (çıkan 0, giren 2): `ZORUNLU_ALAN` K2 kablo (D2), K1 kablo (D3).
- Metin (çıkan 4, giren 6): değişen 4 (E3a kablo notu; KABLO_AD 9, 11, 12, eski → yeni yukarıda); eklenen 2 (K1 kablo D3 cümlesi, K2
  kablo D2 cümlesi).
- Kritik değer değişimi yok (yer tutucular aynı); silinen uyarı yok.

### Sınamalar (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`; hepsi çıkış 0)

| Koşu | Çıkış | Sayılar |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | kablolar.md ve elektrik.md bloğu güncel |
| `kablolar_denetim.py` | 0 | GEÇER (21 sınama, sema_boy dahil) |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 172 bozma |
| `rehber_denetim.py --kaynak` (yenilemeden önce) | 1 | yalnız onay farkı 12 satır (+ ilk koşuda ASCII 1: "panelinin", listeye girdi) |
| `rehber_denetim.py --kaynak` (yenilemeden sonra) | 0 | metin 575; ASCII 0; elektrik 0; zorunlu eksik 0; onay farkı 0 (kablo 165, liste 204, metin 1040); tamlık 172, eksik 0, muaf 19; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 249 / 249 (bu turun 6'sı dahil) |
| `rehber_kablo.py` | 0 | 68 / 5 / 1; CAD geometri hata 0, bilgi 6; şema 27, hata 0, bilgi 15, istisnalı 5; tablo hata 0; şema boyu hata 0, şema > kayıt 0; kart etiketi hata 0, gösterim notu 16 şema hata 0, yer eki hata 0; onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 0 | 84 / 84 (b71–b84 yeni) |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0 | eşlemesiz çizim 0 (veri eski üretimden) |
| `rehber_kablo.py --veri … --bozma-denemesi` | 0 | 93 / 93 (v9 yeni) |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, kaynak fark 0,0007 mm, GEÇTİ |
| `node --check rehber/app.js` | 0 | |

`rehber_uret.py`'ye üç yeni denetim eklendi (kontrol.json `kablo_esleme` hata listesi); dosya yalnız sözdizimiyle sınandı, koşmadı.
Depoda `__pycache__` yok (sözdizimi sınamasının bıraktığı bir dosya silindi).

### Üretimde beklenen sayılar

Parça 1192, SEMA 27, şemalar 65, alt adım 71, gösterim şeması 27 (değişmedi). `rehber_kablo --veri` (yeni veriyle): eşlemesiz 0, `kol`
alanı hatası 0. Tıklama kartı: 27 gösterim şemasında "çizim yolu ~N mm (kesim boyu değil)", 38 kol bölümünde "bölüm uzunluğu ~N mm (kesim boyu değil)". kb satırları SV3,
S09, S10 (ve P03) için ekli. Basılı: K2 kablo listesi bir madde, K1'in P03 satırı bir cümle uzadı (K1 daha önce taşmıştı): PDF tamlık
ve taşma.

### Üretimden sonra karede bakılacaklar (kontrolün listesi + bu tur)

- K1: 9 yeni şema eski CAD yollarıyla aynı karede; kat kesiğindeki altı mor hat ayırt ediliyor mu; G07'nin ana anahtar ucu boşlukta
  (anahtar F1'de); XL4016 çevreden iki hat (yol 9 ve G19). Yol 9 / 11 / 12'nin kartında "kendi gösterim şeması K1'de".
- B3 (M02, plaka altı ve delik) ve B5a (tezgâh görünümünde SV3 doğru yerde mi; kartında "çizim yolu ~39 mm (kesim boyu değil)" ve kb
  satırında dağıtım kartı C'nin yeri).
- E3a: kafa giriş kartının çizildiği yer D24'e 13 mm (kart sığıyor mu, boyun geçişini x −50…−37, z −25…−1 kapatıyor mu); K01'in kartı
  "çizim yolu ~14 mm (kesim boyu değil)".
- E4: "Kablolar + yüz grubu → kafa" (C01) ve "Sol arka kabuk → kafa" (AU1).
- K2: U06 cümlesi kablo listesinde; "Kablo yolu 6" kartında dağıtım kartı C'nin yeri.
- Basılı: B6a'ya beş uzun tablo satırı, K1'e iki madde (P03 satırı bu turda uzadı), K2'ye bir madde: PDF taşma ve tamlık.
- `rehber_veri` günlüğü: gösterim şeması 27, şemalar 65, "UYARI sema alt adimi yok" çıkmamalı.

### Doğrulanamayanlar

- Kartlar, kb satırlarının uzunluğu ve basılı sayfa görülmedi (üretim koşmadı). app.js değişikliği yalnız `node --check` ve kaynak
  kuralıyla sınandı, tarayıcıda açılmadı.
- Dağıtım kartı C'nin nominal noktası TAHMİN (kart modelde yok); "XL4016 C'nin yanında" kaydı kesin, mesafe değil.
- U06 cümlesindeki "USB girişi" ESP32 DevKit'in kart üstü USB soketidir; soket tipi rehberde yazmıyor.

## Üretim ve zincir (15.11.2026; ajan U)

Dal `lale-duzeltme`, HEAD = uzak = `b6022c3`, paketin kaynağı çalışma ağacında (düzeltme turu 1 ve 13:40–13:47 eki sonrası). Yöntem F10g
§ 5 / F10j "Üretim ve zincir": depo dışı geçici klasörde sarmalayıcı (15 s bellek bekçisi, eşik 1,2 GB art arda iki ölçüm ya da boş commit
< 2 GB), her koşunun `.durum` kaydı; her koşu `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`. **Kaynağa dokunulmadı, kod düzeltmesi
yapılmadı.** Aynı saatlerde ikinci dar bakış (`F10k-kontrol-2.md`, KAYNAK GEÇER, 14:01) depoyu yalnız okudu; metin düzeltmesi istemedi.
Paketin kaynaklarının son yazımı üretim başlangıcından önce (en geç `rehber_kablo.py` 13:45:29, `rehber_kritik_onay.json` 13:41:21,
`rehber/app.js` 13:40:14); çıktılar bugünkü kaynaktan.

**Bellek bekleme (üretimden önce):** 13:50 boş fiziksel bellek 1,76 GB (kullanıcının tarayıcısı açık, 16 süreç; dokunulmadı). 60 sn'de
bir ölçüldü: 1,94 / 1,40 / 1,91 / 2,30 / 1,89 / **3,01 GB** (13:55:29, eşik 2,8 tuttu). Ön sınama bu sırada yapıldı.

**FreeCAD kilidi:** 13:55'te "boş"tu, satır yazıldı; FreeCAD veri aşaması (208 s) bitince 13:59:14'te "boş"a döndürüldü. Son hâli "boş".

### Ön sınama (FreeCAD'siz, 13:50–13:51)

`kablolar_uret.py --kontrol` (güncel), `kablolar_denetim.py` (GEÇER), `rehber_denetim.py --kaynak`, `rehber_kablo.py` (GEÇER, onay
tutuyor), `rehber_kol_kablo.py --yazma` (38 bölüm, GEÇTİ), `node --check rehber/app.js`: hepsi çıkış 0.

### Üretim (13:55:39–14:42:39)

`rehber_uret.py` tam koşu: **çıkış 0, 2820 s** (önceki paket 2562 s). Bellek: önce 3,02 GB; bekçinin en düşük ölçümü **1,27 GB**
(14:29:16, 187 ölçüm; 1,5 GB altı 8 ölçüm, art arda iki 1,2 GB altı yok, bekçi tetiklenmedi).

| Ölçü | Beklenen | Ölçülen |
| --- | --- | --- |
| ön sınama | geçer | "kaynak denetimi gecti, onay kaydi tutuyor (kablo 165, liste 204, metin 1040)" |
| parça / şema / alt adım | 1192 / 65 / 71 | 1192 / **65** / 71 (71 geçti); veri: gösterim şeması 27 (taban 11, kafa_ici 5, yollar 8, kafa_ici_qled 3), kol 38 |
| kol kablo | ilk dizin 27 | "38 bölüm (38 şema, ilk 27)", denetim GEÇTİ |
| kablo eşleme (kontrol.json) | 68 / 5 / 1, hata 0 | GEÇTİ; yol çizimi 68 (CAD 39, şema 29, kol 6), bağlantı tablosu 5 (I01, I02, P01, P02, P03), hiçbiri 1 (G06); hata 0, eşleşmeyen 0 |
| denetim | elektrik 0 | ASCII 0, elektrik 0, zorunlu uyarı eksik 0 / 113, yasak 0 (istisna 10) |
| uçuş / sıra / giriş / perdelenme | hata 0 | 340 satır, çarpışan 0, istisna 16; 565 bağlantı ulaşılamaz 0; girilemez 0; gerekçesiz 0, istisna 117 |
| PDF | 80 ya da birkaç fazlası, taşan yok, ≥ 8,0 pt | **80 sayfa** (adım 50 + devam 30), taşan yok, en küçük yazı DOM / PDF 8,1 pt, 16326 kB, eşleme tutarlı |
| PDF tamlık | eksik 0, yineleme 0 | 50 adım, `is_` 32017 karakter, eksik 0; madde 416 (önceki 404), eksik 0; yineleme 0 |
| tarayıcı | 50 / 50 | 50 geçti, konsol hatası 0, ek kontrol sorunlu "-" |

`rehber_veri` günlüğünde "UYARI sema alt adimi yok" yok. Üretimin yazdığı dosyalar: `rehber/veri/rehber-veri.json` / `.js`,
`planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf` ve **bütün** adım görüntüleri (`rehber/goruntu/` ve `planlama/rehber/goruntu/`,
248 PNG; önceki pakette 4). Piksel karşılaştırması (`b6022c3` ↔ yeni): görünür fark (eşik 24) B3, B5a, B5, K1, E3a, E3, E4 alt 4 / 5 / 9 /
10, F1 ve birkaç komşu adımda; öbürlerinde fark yalnız sağ alttaki küçük bir bölgede ve eşiğin altında (kenar yumuşatma düzeyi; nedeni
bakılmadı). Paket dışı 14 dosyanın SHA-1'i üretimden önceki kayıtla aynı (yeniden yazılmadı). FreeCAD'in Python'u `-B`'ye karşın dört
`__pycache__` yazdı (önceki paketteki gibi; iş sonunda silinecek).

### Zincir (14:44:17–15:31:54)

F10h § 9 tablosunun 2–10'u, önceki paketteki komutların aynısı, tek sarmalayıcı altında sırayla (`.durum`: "BITTI cikis 0 sure 2858 enaz
1.71"; 189 ölçüm, bekçi tetiklenmedi).

| Sıra | Komut | Başlangıç | Çıkış | Süre (s) | Beklenen | Ölçülen |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rehber_uret.py` (tam) | 13:55:39 | 0 | 2820 | çıkış 0 | yukarıdaki tablo |
| 2 | `rehber_kablo.py --veri …` | 14:44:17 | 0 | 1 | GEÇER, eşlemesiz 0 | SONUÇ GEÇER; CAD geometri hata 0, bilgi 6; şema 27, hata 0, bilgi 15, istisnalı 5; ayırt edilemeyen 0; onay tutuyor; eşlemesiz çizim 0 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 14:44:17 | 0 | 24 | 95 / 95 | **95 / 95** yakalandı |
| 3 | `rehber_denetim.py` (veri) | 14:44:42 | 0 | 1 | elektrik / yasak 0 | ASCII 0, elektrik 0, zorunlu eksik 0 / 113, yasak 0 (istisna 10) |
| 4 | `F10f-dogrula.py` | 14:44:42 | 0 | 628 | GEÇTİ | GEÇTİ (veri, sınama, kablo kare, sağ / sol, mini etiket; parça kare "None" önceki gibi) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 14:55:10 | 0 | 978 | çıkış 0, `renk_demo` önceki gibi | GEÇTİ; `renk_demo` KALDI (karar; önceki paketle aynı, bilinen kayıt) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 15:11:28 | 0 | 756 | GEÇTİ | GEÇTİ; konum 121 (50 + 71), masa yabancı şema 0, 360 px taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 15:24:04 | 0 | 465 | GEÇTİ | GEÇTİ; seçim 6 / 6, yazdırma kareleri 50 / 50, PDF görüntü 121, boş sayfa yok, dış istek 0, konsol 0 ("veri değişti", bilgi) |
| 8 | `F9b-dogrula.py` | 15:31:49 | 0 | 5 | GEÇER | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 15:31:54 | 0 | 0 | 17 dosya aynı | "izlenen 17 dosyanin ozetleri kayitla ayni" (izlenen CAD dosyası değişmedi) |
| 10 | `regresyon.py --yazma` | 15:31:54 | 0 | 0 | aynı | GEÇER, 10 değer aynı, kötüleşen yok |

Zincir PDF'i, `kontrol.json`'u ve veriyi değiştirmedi (SHA-256 önce / sonra aynı). Zincirin yazdığı: `planlama/d158/F10{a,d,e,f}-dogrula.json`.
En düşük boş bellek zincirde 1,71 GB (14:53:53).

### Sapmalar ve nedenleri

- **Sayılarda sapma yok:** parça 1192, şema 65, alt adım 71, gösterim şeması 27, kol ilk dizini 27, 68 / 5 / 1, PDF 80 sayfa (adım 50 +
  devam 30), taşan yok, en küçük yazı 8,1 pt, tamlık eksik 0 / yineleme 0, `rehber_kablo` veri bozması 95 / 95, çarpışma 17 dosya aynı,
  regresyon 10 / 10 aynı, F10e `renk_demo` önceki gibi.
- **Bilgi, PDF sayfa eşlemesi:** `b6022c3` PDF'iyle adım adım aynı (kayan adım yok, sayfa sayısı değişen adım yok). Uzayan metinler
  (B6a, K1, K2, E3a, E4) mevcut sayfalarına sığdı; tamlık madde sayısı 404 → 416.
- **Bilgi, üretim süresi:** 2820 s (önceki 2562 s); sıra denetimi 1464 s, uçuş yolu 945 s. Boş bellek önceki koşudan çok daha düşüktü
  (en az 1,27 GB, önceki 2,86); neden olarak bellek baskısı tahmin, ölçülmedi.
- **Bilgi, görüntüler:** üretim 248 adım görüntüsünün hepsini yeniden yazdı (önceki pakette 4). Görünür fark yalnız şeması değişen ve
  komşu adımlarda; öbürlerinde sağ alttaki küçük bölgede eşik altı fark (yukarıda).
- **Bilgi:** F10a "veri değişti" (bilgi satırı; veri bu üretimde değişti). F10f'te "parça kare None" önceki gibi.
- Basılı yazı boyları (hedef sayfalar): K1 s. 19 gövde 8,5 pt (önceki gibi), s. 20–22 9,6; B6a s. 15 8,7, s. 16 9,6; B3 s. 10 9,1; B5a s. 13
  9,3; E3a s. 34 8,6, s. 35 9,6; E4 s. 37 9,6, s. 38 9,0, s. 39 9,1, s. 40–41 9,6; K2 s. 42 8,5, s. 43 9,6; her sayfada en küçük 8,1 pt
  (resim altı ve rozetler). Bütün PDF'te çözülmemiş yer tutucu (`{…}`, `⟦`, `⟧`) 0.

### Kare bakışı (15:33–15:38; kendi başsız Chrome'um, 1400 × 900, profil geçici klasörde)

Ekran: K1, B3, B5a, B6a, E3a, E4, E4 alt 4 ve alt 9, K2, H0a (kol bölümü), iki temada genel kare + kablo kancasına kaydırılmış panel; her
gösterim şeması ve kablo yolu satırı tek tek seçildi (kare + etiket kartı metni DOM'dan, iki tema; açık temada 54, koyu temada 39
seçim). Basılı: PyMuPDF ile 110 / 160 dpi. Rastgele üç değişmemiş adım `random.Random(1583)` ile, metni `b6022c3` verisine göre değişmeyen
adımlardan: adım 7 B2b s. 8, adım 15 B6 s. 17, adım 35 F3 s. 55. **Gözle baktığım: 18 ekran karesi, 20 PDF sayfası** (K1 s. 19–22,
B3 s. 10, B5a s. 13, B6a s. 15–16, E3a s. 34–35, E4 s. 37–41, K2 s. 42–43, rastgele s. 8, 17, 55). Öbür seçim karelerine gözle
bakılmadı; onların etiket metni DOM'dan okundu.

| Kare | Tema | Gördüğüm |
| --- | --- | --- |
| Panel metni (10 adres, DOM) | açık, koyu | Çözülmemiş yer tutucu 0; panel dışına taşan / kesilen öğe 0 |
| Şema kartı etiketi (DOM, bütün seçimler) | açık, koyu | 27 gösterim şemasının hepsinde "Kablo şeması · adım N (KOD) · çizim yolu ~N mm (kesim boyu değil)" (ör. K01 ~14, SV3 ~39, M02 ~384, G07 ~281, eski K04 ~114, U06 ~971); kol bölümünde (H0a) "bölüm uzunluğu ~125 mm (kesim boyu değil)"; CAD "Kablo yolu N" kartında sayı yok ("(gösterim) · taban") |
| K1 genel (ekran) | açık, koyu | Dokuz yeni şema eski CAD yollarıyla aynı karede; kat kesiği çevresinde mor sinyal hatları iç içe |
| K1 seçim: G07, G19, B02, N01, Q01 (koyu), yol 9 | açık, koyu | Seçilen hat vurgu renginde tek başına izlenebiliyor; G19 mavi (5 V) hat, yol 9 ayrı hat (XL4016 çevreden iki hat ayrı görünüyor); G07'nin ana anahtar ucu direğin yanında, parçasız noktada bitiyor |
| K1 yol 9 / 11 / 12 kartı (DOM) | açık, koyu | "kendi gösterim şeması K1'de" / "kendi gösterim şemaları K1'de" var |
| B3 M02 seçimi | açık | Sol BTS7960'tan plaka üstünden arkaya giden tek hat; kablo kancasında not "çarpışma taramasından geçmedi, parça sayısına girmez, boy ölçümü değildir" |
| B5a (tezgâh) SV3 seçimi | açık | Şema güç panelinde mavi XL4016 C kartının üstünde (tezgâh görünümünde doğru kartta); öbür ucu (dağıtım kartı C, modelde yok) boşlukta; kb satırında kartın yeri ("kart güç panelinde, XL4016 C'nin yanında; …") |
| B6a kablo kancası | açık, koyu | I01, I02, P01, P02 satırları okunuyor (kod biçimli kanal adları); "bağlantı tablosudur, 3B çizim değil" notu dört satırın arkasında |
| E3a K01 seçimi, genel | açık, koyu | K01 (14 mm) seçilince etiket kartının altında kalıyor; K02 kırmızı, K03 mavi ayrı görünüyor; kafa giriş kartı modelde yok |
| E4 alt 4 AU1 seçimi | açık | Masa denemesi etiketi kartta ("Bölücü masa denemesine (KT2) bağlı: yeri ve varlığı kesin değil"); şema opak sol kabuğun arkasında, yalnız küçük bir parçası görünüyor |
| E4 alt 9 C01 seçimi | açık | C01 saydam yüz kabuğunun ardında, Pi ile kamera arasında görünüyor |
| K2 U06 seçimi + kablo kancası | açık | U06 kartı "çizim yolu ~971 mm (kesim boyu değil)"; U06 uyarı cümlesi kablo kancasında ayrı madde; "Kablo yolu 6" kartında S09 / S10 satırında dağıtım kartı C'nin yeri |
| H0a kol bölümü | koyu | "bölüm uzunluğu ~125 mm (kesim boyu değil)" |
| Gösterim şeması notu (ekran) | açık, koyu | K1, B3, B5a, E3a, E4 kablo kancasında "çarpışma taramasından geçmedi" ve "yeri yaklaşık" var; E4 notunda "parça sayısına girmez" yok; K2 notunda (eski `kablo_yolu_ekran` şemaları) "çarpışma taramasından geçmedi" yok (ikisi de kuyrukta, kapsam dışı) |
| Basılı K1 s. 19–22 | — | s. 19 gövde 8,5 pt, sonda "İş metni yarım kaldı: devamı sonraki sayfa (K1, adım 17) →"; s. 20 "← K1 iş metni: önceki sayfa sonunda yarım kalan yer burada sürüyor", madde 5 sonu–8 tam, madde 7'de P03; s. 21 kontrol listesi iki sütun, P03 maddesi var, sığıyor; s. 22 kablo kancası: gösterim şeması notu, P03 satırı (yer cümlesiyle), yol 9 / 11 "kendi gösterim şeması K1'de", dokuz şema satırı "(şema)"; taşma / kesilme yok |
| Basılı B6a s. 15–16 | — | s. 15 iş metni madde 3–4 (I01, I02, P01, P02), kontrol listesi sığıyor; s. 16 kablo kancasında dört bağlantı tablosu satırı tam, sonra açıklama notu; taşma yok |
| Basılı B3 s. 10, B5a s. 13 | — | Karede M02 / SV3 görünüyor; notlar ve şema satırları tam |
| Basılı E3a s. 34–35 | — | s. 34 iş metni + notlar; s. 35 kontrol listesi ("Tabla geçişi (x −50…−37) boş"), K01–K03 notu ve üç şema satırı |
| Basılı E4 s. 37–41 | — | s. 38 kablo kancası: C01 / AU1 notu ve yedi şema satırı; s. 40 alt 4 kartı "Ses kablosunun çizimi gösterim şemasıdır …"; s. 41 alt 9 karesinde C01 görünüyor |
| Basılı K2 s. 42–43 | — | s. 42 gövde 8,5 pt, madde 1–8 tam; s. 43 kablo kancasında U06 cümlesi, yol 6 satırı, beş şema satırı |
| Basılı rastgele s. 8, 17, 55 | — | Sığıyor, okunuyor, değişiklik izi yok |

**Zor okunan / yanıltıcı kareler**

1. **K1 genel kare (ekran ve basılı s. 19):** kat kesiği çevresinde altı mor sinyal hattı (G07, B02, N01, N02, Q01, Q02) ve yol 11 / 12
   iç içe. Ekranda tek tek seçilince ayırt ediliyor; basılıda seçim yok, montajcı hangi mor hattın hangi kablo olduğunu yalnız kablo
   listesindeki kimlikten çıkarır.
2. **K1 G07:** şemanın ana anahtar ucu direğin yanında parçasız bir noktada bitiyor (anahtar F1'de takılıyor); kart "ana anahtar çıkışı"
   diyor. Montajcı ucu karede arar, anahtarı bulamaz; iş metni anahtarın F1'de geldiğini söylüyor.
3. **E3a K01:** 14 mm'lik şema seçilince etiket kartının altında kalıyor (karede neredeyse görünmüyor). Kafa giriş kartı modelde yok:
   kartın D24'e sığıp sığmadığı ve "tabla geçişi (x −50…−37) boş" kontrol maddesiyle çakışıp çakışmadığı kareden anlaşılmıyor.
4. **E4 alt 4 (Sol arka kabuk → kafa):** AU1 / AU2 şeması opak sol kabuğun arkasında; ekranda küçük bir parçası, basılı alt adım
   karesinde (s. 40) hiç görünmüyor, ama karenin altında "Karede: Kablo: Analog ses (beyaz)" yazıyor. Montajcı karede ses kablosunu arar.
5. **B5a SV3:** dağıtım kartı C modelde olmadığından şemanın kart ucu boşlukta; not "yeri yaklaşık" diyor (yanıltıcı değil, düşük).
6. **B6a bağlantı tabloları:** tablo değil uzun satır içi dizi; okunuyor, ama "3B çizim değil" açıklaması dört satırdan sonra geliyor (düşük).

Paket öncesinden bilinen ve bu bakışta değişmeyenler (K1 madde 1–3 uzun paragraf vb.) yeniden sayılmadı.

### Doğrulanamayanlar

- PDF'in görünüşü PyMuPDF görüntüsünden; kâğıda basılmadı.
- Seçim karelerinin çoğuna gözle bakılmadı (18 kare gözle; etiketler DOM'dan). B5a'daki mavi kartın XL4016 C olduğu parça listesinin
  rengiyle eşleştirildi, kart adı karede okunmadı.
- Kafa giriş kartının sığması ve boyun geçişini kapatıp kapatmadığı (kart modelde yok); yeni şemaların çarpışma durumu (taranmadı).
- PNG'lerin hepsinin yeniden yazılma nedeni ve eşik altı farkın kaynağı bakılmadı.

### Üretimin ve zincirin yazdığı dosyalar

Üretim: `rehber/veri/rehber-veri.json` / `.js`, `planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf`, `rehber/goruntu/` ve
`planlama/rehber/goruntu/` altındaki 248 PNG. Zincir: `planlama/d158/F10{a,d,e,f}-dogrula.json`. Paket dışı 14 dosya yeniden yazılmadı
(SHA-1 başta ve sonda aynı). FreeCAD'in yazdığı dört `__pycache__` (13:55–13:59, içlerinde yalnız `.pyc`) silindi. `git status`: başta 32,
sonda 289 satır (üretim çıktıları + 4 doğrulama JSON'u + paralel bakışın `F10k-kontrol-2.md`'si). Kilit "boş". Commit, push, `git add` yok.
