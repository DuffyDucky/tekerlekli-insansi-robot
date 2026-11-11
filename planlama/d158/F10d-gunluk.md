# F10d günlüğü: alt adımlar, kabuk adımlarının bölünmesi, takma yönleri, görünürlük

Ajan A, dal `lale-duzeltme`, başlangıç `10b60d6`. Brief: `planlama/d158/F10d-brief.md`. Commit / push yok.
Geçici dosyalar: scratchpad `f10d/` (yön ölçüm betikleri ve JSON çıktıları).

## 1. Alt adım tasarımı

**Tek kaynak: F10c'nin `sira` grubu = alt adım.** `rehber_metin.py` adımında `alt=True` varsa her `sira` grubu bir alt adımdır;
ayrı bir alt adım listesi yok. Gerekçe: F10c sıra denetimi (`rehber_sira.py`), panel satır sırası ve sıralı takma zaten bu gruplardan
okunuyor; ikinci bir liste ikisinin ayrışmasına yol açardı. Grubun yeni alanları (hepsi isteğe bağlı):

| alan | anlamı |
| --- | --- |
| `ad`, `desen` | F10c'deki gibi (alt adım başlığı; görünen ada göre parça eşleşmesi, ilk eşleşen grup kazanır) |
| `is_` | alt adımın kendi metni |
| `masa` | masa birimi anahtarı: bu grup masada hazırlanır, aynı anahtarlı gruplar birikir (yalnız birimin parçaları görünür) |
| `bag` | o anahtarlı masa birimini robota bağlayan grup (birim bu alt adımda "alt montaj" olarak `ucus_bag` yönünden gelir) |
| `ucus` | `{desen: (x, y, z) \| "radyal", "*": varsayılan}`: grubun ana parçalarının geliş yönü (sağ için; adında "sol" geçen ya da sol modüldeki parçada x aynalanır) |
| `ucus_bag` | bağlanan birimin geliş yönü |
| `kamera` | `"arka"` ya da yön vektörü |
| `saydam` | bu alt adımda saydam çizilecek parçalar (desen; o ana kadar takılanlar) |
| `sema` | bu alt adımda gösterilen kablo şemaları (şema adında desen) |
| `konum` | `{desen: {"x" \| "y" \| "z": (alt, üst)}}`: aynı adlı bağlantı elemanlarını bant yüksekliğine / yana göre ayırır |
| `yan` | `"sag"` / `"sol"`: yalnız bu modül ekli parçalar (iki kollu adımlar) |
| `gizli_ok`, `ucus_ok` | `{desen: gerekçe}`: tamamen gizli yeni parça ya da çarpışan uçuş yolu için gerekçeli istisna |
| `giris_ok` | `{"*": gerekçe}`: birimin tek engeli dinlenmedeki model girişimiyse giriş denetiminde gerekçeli istisna |

Veri (`rehber-veri.json`): adımda `alt` (alt adım sayısı) ve `sira_grup[]` (`ad`, `tezgah` = masa anahtarı ya da "", `bag`, `satir`,
`is_`, `kamera`, `ub`, `saydam` kimlikleri, `sema` indeksleri, `ref` gösterim parçaları, `gizli_ok`, `ucus_ok`). Renk / braket
vurgusu / cıvata işareti (F10e) için grup kaydına alan eklemek yeter; şimdilik boş.

Isıl gömme somun: baskıdan sonra takılı (hazırlık). Ev sahibi parça (aynı adımın ana parçalarından sınır kutusu somun merkezini
içeren; birden çoksa en yakını) `h` alanında; somun ev sahibiyle birlikte uçar, adım içi sırada onun grubundadır. Panel / sıralı takma
satırı kalır (panel sırası = takma sırası), parçaları ev sahibinin satırıyla birlikte yerine gider.

Adresleme ve gezinme (`rehber/app.js`): ana adım sayısı 50, kimlikler aynı. Konum `[adım, alt adım]`; `?adim=31.3` ya da `#31.3`
doğrudan açılır, `31` ya da `31.0` genel bakış (adımın bütün yeni parçaları, eskisi gibi). ←/→ (ve düğmeler, kaydırma) genel bakıştan
alt adımlara, sonra bir sonraki adıma geçer. İlerleme çubuğu konum sırası üzerinden; sayaç "Adım 31 / 49 · alt adım 3 / 10". Alt
adımı olmayan adım bugünkü gibi. Panel: alt adım listesi (bağlantı), alt adımın başlığı / metni / satırları; genel bakışta tek tablo,
grup başlıklarıyla, takma sırasıyla. Yazdırma: genel bakış sayfasından sonra alt adım kartları (görüntü + metin + satırlar).

Patlatma mesafesi parça boyuyla orantılı: ana parça `max(40, 0,5 × sıkı köşegen)` (sıkı kutu: `optimalBoundingBox`; F10c'ye kadar
`1,1 × gevşek köşegen`, etek bantları 630–830 mm uzağa gidiyordu). Cıvata `max(25, 2,5 × boy)`, bağlanan birim `max(120, 0,8 × birim
köşegeni)`.

## 2. Ölçüm tanımları

- **Giriş yolu / uçuş yolu çarpışması** (`rehber_giris.py`, h 0,5 mm): hareketli küme yönde tam sayı adımlarla çekilir; üç eksenli
  ışınlarda ortak hacim boyu > **0,2 mm** olan çift çarpışma. Temas ve aynı düzlemdeki yüz çarpışma değil; dinlenmede (yerindeyken) zaten
  ortak hacmi olan çift (modeldeki girişim) sayılmaz, ayrıca listelenir. "Serbest" = sınır kutuları ayrılana kadar çarpışma yok.
- **Uçuş yolu** (`rehber_sira.py ucus_yolu`): alt adımlı adımlarda her satırın patlatılmış konumundan (taban + u·d) yerine giden düz yol,
  o satır takılmadan önce yerinde olanlarla. Yön en yakın küçük tam sayı yöne yuvarlanır (açı farkı kayıtta).
- **Perdelenme** (`rehber_sira.py perdelenme`): voksel 3 mm, 26 yönden dik izdüşüm; adımın (ve alt adımın) sonunda hiçbir yönden
  görünmeyen yeni parça "tamamen gizli". Alt adımlı adımlarda alt adım başına sınır 0 (gerekçeli istisna dışında).
- **Görünürlük** (`RehberTest.gorunurluk`, F10d-dogrula.py): kamera görüntüsünde kimlik tamponu piksel sayısı (güvenli alan; saydam
  çizilen eski parça örtmez) > 0 ve sınır kutusu köşeleri karede.

(Bölümler 3–10 ölçümlerden sonra yazıldı, aşağıda.)

## 3. Alt adım listeleri (son üretim, `rehber-veri.json`)

Sayılar ölçüme göre: E4 10 (denetim notu 7), F1 9 (6), F2 6 (5), F3 5, F4 2, F5 5; ayrıca iki kollu tezgâh adımları D1c (21), H0b (43),
H0d (45) ve H0e (46) kol başına birer alt adım, 2'şer (madde 5: sağ / sol kadraj; 45 / 46 ilk F10d-dogrula koşusundan sonra eklendi,
bölüm 7). Toplam 45 alt adım; ana adım 50. "masa X": parça masada X birimine eklenir
(robotta görünmez); "bağla X": X birimi robota `ub` yönünden gelir. E4 sırası F10c'deki gibi: sağ arka → sol arka → tabla
cıvataları → yüz grubu (masada: kamera, QLED, tırnaklar) → kablolar + yüz grubu → dikişler. Başka ana adıma taşınan parça yok
(E4 dikiş grubunu K2'ye taşıma denenmedi: sıra denetimi E4 içinde ulaşılabilir buluyor, gerek görülmedi). Satır içi sıra
alt adımlı adımlarda grubun `desen` sırası; ısıl gömme (hazırlık) satırları cıvatalardan önce.

**21 D1c** (Tezgâh: S1 ortaya, horn), 2 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 21.1 | Sağ omuz: horn + merkez vidası |  | S1 horn 25T alüminyum disk sağ ×1; M3x5 horn vidası (servo ile) ×1 | (1.0, 0.35, 0.45) | 4 | 0 |
| 21.2 | Sol omuz: horn + merkez vidası |  | S1 horn 25T alüminyum disk sol ×1; M3x5 horn vidası (servo ile) ×1 | (-1.0, 0.35, 0.45) | 4 | 0 |

**31 E4** (Kafa kabukları + yüz ekranı, kamera, ses), 10 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 31.1 | Masada: sağ arka kabuk + ReSpeaker | masa arka_sag | Arka kafa kabuğu sağ ×1; ReSpeaker Mic Array v2.0 ×1; M3 ısıl gömme somun ×7; M2x8 PT vida (plastik için) ×3 | (0.55, -0.75, 1.0) | 0 | 0 |
| 31.2 | Sağ arka kabuk → kafa | bağla arka_sag ub (0.0, 0.0, -1.0) | (satır yok; birim gelir) | arka | 0 | 1 |
| 31.3 | Masada: sol arka kabuk + USB ses kartı, PAM8403 | masa arka_sol | Arka kafa kabuğu sol ×1; Köpük bant ×2; USB ses kartı ×1; PAM8403 amfi ×1; M3 ısıl gömme somun ×4 | (1.0, 0.35, 0.5) | 0 | 0 |
| 31.4 | Sol arka kabuk → kafa | bağla arka_sol ub (0.0, 0.0, -1.0) | (satır yok; birim gelir) | (-0.85, 0.62, -1.25) | 0 | 3 |
| 31.5 | Tabla → arka kabuk rafı cıvataları |  | M3x10 DIN 912 ×4 | (0.35, 0.45, 1.25) | 2 | 0 |
| 31.6 | Masada: yüz kabuğu + kamera | masa yuz | Yüz kabuğu (ön) (sağ + sol) ×2; Kamera Raspberry Pi Camera Module 3 ×1; M3 ısıl gömme somun ×6; M2x8 PT vida (plastik için) ×4 | (0.6, 0.45, -1.25) | 0 | 0 |
| 31.7 | Masada: QLED → yüz kabuğu | masa yuz | Yüz ekranı WaveShare 10,1" QLED HDMI ×1 | (0.6, 0.45, -1.25) | 0 | 0 |
| 31.8 | Masada: ekran tırnakları | masa yuz | Köpük bant ×4; Ekran tırnağı üst (sağ + sol) ×2; Ekran tırnağı alt (sağ + sol) ×2; M3x6 ISO 7380 ×4 | (0.6, 0.45, -1.25) | 0 | 0 |
| 31.9 | Kablolar + yüz grubu → kafa | bağla yuz ub (0.0, 0.0, 1.0) | (satır yok; birim gelir) | ön sağ üst | 0 | 3 |
| 31.10 | Kabuk dikişi |  | M3x5 ISO 7380 ×2; M3x6 ISO 7380 ×7 | ön sağ üst | 0 | 0 |

**33 F1** (Taban eteği), 9 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 33.1 | Orta bantlar + orta braketler |  | Etek orta (sağ + sol) ×2; M3 ısıl gömme somun ×12; M3x14 ISO 7380 ×2 | ön sağ üst | 0 | 0 |
| 33.2 | Ön sağ bant |  | Etek ön sağ ×1; M3 ısıl gömme somun ×2; M3x6 ISO 7380 ×3; M3x14 ISO 7380 ×1 | ön sağ üst | 0 | 0 |
| 33.3 | Ön dolgu şeridi |  | Etek dolgu şeridi ön ×1; M3 ısıl gömme somun ×2; M3x6 ISO 7380 ×2 | ön sağ üst | 0 | 0 |
| 33.4 | Ön sol bant |  | Etek ön sol ×1; M3x6 ISO 7380 ×5; M3x14 ISO 7380 ×1 | (-0.85, 0.62, 1.25) | 0 | 0 |
| 33.5 | Masada: arka sağ bant + acil stop | masa arka_sag | Etek arka sağ ×1; Acil stop mantarı + bilezik ×1; Acil stop kontak gövdesi (1NC) ×1; M3 ısıl gömme somun ×3 | (0.85, 0.62, 1.25) | 0 | 0 |
| 33.6 | Arka sağ birimi → robot | bağla arka_sag ub (1.0, 0.0, 0.0) | M3x6 ISO 7380 ×3; M3x14 ISO 7380 ×1 | arka | 0 | 0 |
| 33.7 | Arka dolgu şeridi |  | Etek dolgu şeridi arka ×1; M3 ısıl gömme somun ×3; M3x6 ISO 7380 ×3 | arka | 0 | 0 |
| 33.8 | Masada: arka sol bant + ana anahtar | masa arka_sol | Etek arka sol ×1; Ana anahtar ASW-A01 gövdesi (tahmini zarf) ×1 | (-0.85, 0.62, 1.25) | 0 | 0 |
| 33.9 | Arka sol birimi → robot | bağla arka_sol ub (-1.0, 0.0, 0.0) | M3x6 ISO 7380 ×6; M3x14 ISO 7380 ×1 | (-0.85, 0.62, -1.25) | 0 | 0 |

**34 F2** (Gövde alt ve orta bantları), 6 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 34.1 | Alt bantlar + y 400 braketi |  | Gövde alt bandı (sağ + sol) ×2; M3 ısıl gömme somun ×10; M3x6 ISO 7380 ×4; M5x18 ISO 7380 ×2 | ön sağ üst | 0 | 0 |
| 34.2 | Uzatma bandı 1 + y 530 braketi |  | Gövde uzatma bandı 1 (sağ + sol) ×2; M3 ısıl gömme somun ×10; M3x6 ISO 7380 ×10; M5x18 ISO 7380 ×2 | ön sağ üst | 0 | 0 |
| 34.3 | Uzatma bandı 2 + y 688 braketi |  | Gövde uzatma bandı 2 (sağ + sol) ×2; M3 ısıl gömme somun ×10; M3x6 ISO 7380 ×10; M5x18 ISO 7380 ×2 | ön sağ üst | 0 | 0 |
| 34.4 | Masada: orta bant sağ + hoparlör | masa orta_sag | Gövde orta bandı sağ ×1; Hoparlör kabı ön halka ×1; Hoparlör 40 x 20 ×1; Hoparlör kabı arka (flanşlı) ×1; Köpük ped (hoparlör kelepçesi) ×1; Hoparlör kelepçesi ×1; M3 ısıl gömme somun ×4; M3x20 DIN 912 ×2 | (-1.0, 0.45, 0.6) | 0 | 0 |
| 34.5 | Orta bant sağ → gövde | bağla orta_sag ub (1.0, 0.0, 0.0) | M3x6 ISO 7380 ×3 | ön sağ üst | 0 | 0 |
| 34.6 | Orta bant sol |  | Gövde orta bandı sol ×1; M3x6 ISO 7380 ×5 | (-0.85, 0.62, 1.25) | 0 | 0 |

**35 F3** (Göğüs bantları + göğüs ekranı), 5 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 35.1 | Göğüs bandı sağ + y 1095 braketi |  | Göğüs bandı sağ ×1; M3 ısıl gömme somun ×5; M3x6 ISO 7380 ×3; M5x18 ISO 7380 ×1 | ön sağ üst | 0 | 0 |
| 35.2 | Göğüs bandı sol + y 1095 braketi |  | Göğüs bandı sol ×1; M3 ısıl gömme somun ×3; M3x6 ISO 7380 ×5; M5x18 ISO 7380 ×1 | (-0.85, 0.62, 1.25) | 0 | 0 |
| 35.3 | VESA taşıyıcı → direk ön kanalı |  | Göğüs ekranı VESA taşıyıcı ×1; M6 DIN 125 pul ×2; M6x18 DIN 912 ×2; M6 çekiç somun, kanal 10 ×2 | (0.45, 0.35, 1.25) | 0 | 0 |
| 35.4 | Göğüs ekranı → taşıyıcı (VESA) |  | Göğüs ekranı 11,6" HDMI 1920x1080 kasalı ×1; M4 DIN 125 pul ×4; M4x12 DIN 912 ×4 | (0.85, 0.62, -1.25) | 0 | 1 |
| 35.5 | Göğüs ekranı çerçevesi |  | Göğüs ekranı çerçevesi (sağ + sol) ×2; M3 ısıl gömme somun ×8; M3x6 ISO 7380 ×8 | ön sağ üst | 0 | 0 |

**36 F4** (Omuz bantları), 2 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 36.1 | Omuz bandı sağ |  | Omuz bandı sağ ×1; M3 ısıl gömme somun ×5; M3x6 ISO 7380 ×3 | ön sağ üst | 0 | 0 |
| 36.2 | Omuz bandı sol |  | Omuz bandı sol ×1; M3 ısıl gömme somun ×3; M3x6 ISO 7380 ×5 | (-0.85, 0.62, 1.25) | 0 | 0 |

**43 H0b** (Tezgâh: dirsek hornu), 2 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 43.1 | Sağ kol: dirsek hornu + merkez vidası |  | Dirsek horn 25T alüminyum disk sağ ×1; M3x5 horn vidası (servo ile) ×1 | (1.0, 0.4, 0.5) | 0 | 0 |
| 43.2 | Sol kol: dirsek hornu + merkez vidası |  | Dirsek horn 25T alüminyum disk sol ×1; M3x5 horn vidası (servo ile) ×1 | (-1.0, 0.4, 0.5) | 0 | 0 |

**45 H0d** (Tezgâh: bilek hornu), 2 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 45.1 | Sağ kol: bilek hornu + merkez vidası |  | Bilek horn 25T alüminyum disk sağ ×1; M3x5 horn vidası (servo ile) ×1 | (1.0, -0.6, 0.5) | 0 | 0 |
| 45.2 | Sol kol: bilek hornu + merkez vidası |  | Bilek horn 25T alüminyum disk sol ×1; M3x5 horn vidası (servo ile) ×1 | (-1.0, -0.6, 0.5) | 0 | 0 |

**46 H0e** (Tezgâh: bilek flanşı), 2 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 46.1 | Sağ kol: bilek flanşı + 4 cıvata |  | Bilek flanşı sağ ×1; M3x8 DIN 912 ×4 | (1.0, -0.6, 0.5) | 0 | 0 |
| 46.2 | Sol kol: bilek flanşı + 4 cıvata |  | Bilek flanşı sol ×1; M3x8 DIN 912 ×4 | (-1.0, -0.6, 0.5) | 0 | 0 |

**49 F5** (Servis kapakları (test sonrası)), 5 alt adım:

| alt | başlık | masa / bağla | satırlar (takma sırası) | kamera | saydam | şema |
| --- | --- | --- | --- | --- | --- | --- |
| 49.1 | Masada: üst arka kapak + hub | masa ust_kapak | Üst arka servis kapağı ×1; Köpük bant (USB Hub kapak içi) ×1; USB Hub 4'lü (kapak içi) ×1; M3 ısıl gömme somun ×7 | (0.6, 0.45, 1.25) | 0 | 0 |
| 49.2 | İlk enerji, aşama 2 (kapaklar açık) |  | (satır yok; birim gelir) | ön sağ üst | 0 | 0 |
| 49.3 | Arka servis kapağı |  | Arka servis kapağı ×1; M3 ısıl gömme somun ×7; M3x6 ISO 7380 ×7 | ön sağ üst | 0 | 0 |
| 49.4 | Üst arka kapak (hub'la) → gövde | bağla ust_kapak ub (0.0, 0.0, -1.0) | M3x6 ISO 7380 ×7 | ön sağ üst | 0 | 0 |
| 49.5 | Etek servis kapakları H1 + H2 |  | Etek servis kapağı H1 (sigorta kutusu) ×1; Etek servis kapağı H2 (ana sigorta) ×1; M3 ısıl gömme somun ×8; M3x6 ISO 7380 ×8 | (0.7, 1.0, -1.0) | 0 | 0 |


## 4. Takma yönü düzeltmeleri (önce HEAD / sonra; giriş yolu ölçümü)

Ölçüm betikleri scratchpad `f10d/` (`yon_olc.py`, `yon_ince.py`, `yon_ince2.py`, `yon_horn.py`, `yon_ters.py`, `yon_ekran.py`,
`yon_cer.py`; `rehber_giris.Giris`, h 0,5 mm, eşik 0,2 mm, temas çarpışma değil). "Serbest" = sınır kutuları ayrılana kadar ortak
hacim > 0,2 mm yok. "Dinlenme" = parça yerindeyken zaten ortak hacmi olan çift (model girişimi; çarpışma sayılmaz, ayrıca yazılır).
u = parçanın geldiği yön (patlatılmış konum = yer + u·d), d = patlatma mesafesi (mm). Sol parçada x aynalı.

| adım | parça | önce u, d | sonra u, d | ölçüm (gerekçe) |
| --- | --- | --- | --- | --- |
| E4 31 | Yüz ekranı QLED | (0, 0, 1), 319 | (0, 0, −1), 145 | masada yüz kabuğuna (kamera takılı): yalnız −z serbest (arkadan / içeriden). Önce duvarın içinden geliyordu |
| E4 31 | Yüz kabuğu sağ / sol | (0,36, 0,18, −0,91), 296 | (0, 0, 1), 133 (masa tabanı) → birim +z | yüz grubu birimi kafaya: yalnız +z serbest (rehber_sira giriş) |
| E4 31 | Arka kafa kabuğu sağ / sol | (0,71, 0, −0,71), 316 | birim −z | sağ birim: yalnız −z; sol birim: −x, −z serbest (giriş) |
| E4 31 | ReSpeaker | (0, −1, 0), 112 | (0, −0,71, 0,71), 50 | masada: (−1, −1, 0), (0, −1, 1) serbest; (0, −1, 0) kapalı |
| E4 31 | USB ses kartı, PAM8403, köpükleri | (−1, 0, ±0,05), 40–60 | (1, 0, 0), 40 | masada sol arka kabuğa: (1, 0, 0), (1, 0, 1) serbest |
| E4 31 | Tırnak köpükleri | (0,78, 0, 0,62), 40 | (0, 0, −1), 40 | masada: (0, 0, −1), (±1, 0, −1) serbest; panelde köpük tırnaktan önce (önce tırnak önce geliyordu: 24 mm çarpışma) |
| E4 31 | Kamera | (yönü yok, radyal) | (0, 0, −1), 40 | hiçbir yön serbest değil: istisna (bölüm 5) |
| E2 28 | Tilt hornu | (0,75, 0, 0,66), 40 | (1, 0, 0), 40 | servo takılıyken yalnız +x serbest (servo ekseni) |
| E2 28 | Tilt servosu çıkış mili | (0,73, 0, 0,68), 40 | (1, 0, 0), 40 | horn ile aynı eksen |
| D1c 21 | S1 hornu sağ / sol | (0, 1, 0), 40 | (±1, 0, 0), 40 | (0, 1, 0): çıkış miline 3,3 mm; ±x serbest (14 mm) |
| H0b 43 | Dirsek hornu sağ / sol | (0, 1, 0), 40 | (±1, 0, 0), 40 | (0, 1, 0): çıkış miline 3,3 mm; ±x serbest (11 mm) |
| H0d 45 | Bilek hornu sağ / sol | (0, 1, 0), 40 | (0, −1, 0), 40 | (0, 1, 0): 1 mm sonra çıkış miline 11,48 mm; −y serbest (4 mm) |
| H0e 46 | Bilek flanşı | (0, −1, 0), 44 | (0, −1, 0), 40 | −y serbest (değişmedi; mesafe) |
| E2a 25 | Pan hornu | (0, 1, 0) | (0, 1, 0) | +y serbest (38 mm); değişmedi; görünürlük için kamera + saydam (bölüm 6) |
| F1 33 | Etek orta sağ / sol | (±1, 0, 0), 647 | (±1, 0, 0), 187 | yalnız ±x serbest |
| F1 33 | Etek ön sağ / sol | (±0,71, 0, 0,71), 828 | (±0,71, 0, 0,71), 185 | hiçbir düz yön serbest değil (h 0,25'te de): istisna, karar F10d-K1 |
| F1 33 | Etek arka sağ / sol | (±0,71, 0, −0,71), 828 | birim ±x | arka sağ birimi yalnız +x, arka sol birimi yalnız −x serbest |
| F1 33 | Dolgu şeridi ön | (0, 0, 1), 631 | (0, 1, 0), 155 | düz yol yok; iki parçalı yol serbest (önce +z 10 mm, sonra +y): istisna |
| F1 33 | Dolgu şeridi arka | (0, 0, −1), 631 | (0, 1, 0), 155 | arka sağ takılıyken yalnız +y serbest |
| F1 33 | Acil stop kontak | (0,51, 0, −0,86), 78 | (0, −1, 0), 40 | masada (mantar takılı): yalnız −y (alttan) serbest |
| F1 33 | Ana anahtar | (−0,51, 0, −0,86), 89 | (0, −1, 0), 41 | masada: (0, −1, 0) ve dört yön daha serbest |
| F2 34 | Gövde alt / uzatma 1 / uzatma 2 bandı | (1, 0, 0), 304–483 | (±1, 0, 0), 138–157 | her biri (alttakiler takılı) yalnız kendi tarafına ±x serbest |
| F2 34 | Gövde orta bandı sağ / sol | (0,06, 0, 1), 476 | (±1, 0, 0), 176 (sağ: birim) | sol: yalnız −x serbest; sağ + hoparlör birimi: +x'te çarpışma yok, dinlenmede uzatma 2 sağ ile 5,53 mm (istisna) |
| F2 34 | Hoparlör kabı, hoparlör, kelepçe, köpük ped | (0,42–0,47, 0, 0,89), 40–100 | (0, 0,56, −0,83) = (0, 2, −3), 40–46 | eksenel (0, 2, −3) beşi için serbest (90–101 mm); (0, 1, −1) ve (0, 1, −2) hoparlörde kapalı. Panel sırası kab ön → hoparlör → kab arka → köpük → kelepçe (önce kelepçe hoparlörden önceydi: 39,9 mm çarpışma) |
| F3 35 | Göğüs bandı sağ / sol | (0,1, 0, 0,99), 521 | (±1, 0, 0), 180 | hiçbir yön serbest değil (orta bant dudağı 12 mm, ilk adımda): istisna, karar F10d-K1 |
| F3 35 | Göğüs ekranı 11,6" | (0, 0, 1), 382 | (0, 0,24, 0,97) = (0, 1, 4), 174 | bantlar + taşıyıcı takılı: 22 yönden yalnız (0, 1, 4) serbest (84,5 mm); düz +z 19,5 mm sonra bant |
| F3 35 | Çerçeve sağ / sol | (0, 0, 1), 407 | (0, 0, 1), 129 | 6 eğik yön dahil hiçbiri serbest değil (bant 34 mm, ilk adımda): istisna |
| F4 36 | Omuz bandı sağ / sol | (0,11, 0, 0,99), 510 | (±1, 0, 0), 124 | 18 + 7 eğik yön, iki parçalı yol (+y 4,5 mm sonra ±x / +z): hiçbiri serbest değil: istisna, karar F10d-K1 |
| F5 49 | Etek servis kapağı H1 / H2 | (0, 0, −1), 99–141 | (0, 1, 0), 45–64 | yalnız +y (üstten) serbest |
| F5 49 | Üst arka servis kapağı + hub | (0, 0, −1), 248 | birim −z; masada hub, köpük (0, 0, 1) | birim −z: kapağın ısıl gömmeleri ilk adımda bantla 0,5 mm (istisna); masada hub ve köpük +z serbest |
| F5 49 | Arka servis kapağı | (0, 0, −1), 382 | (0, 0, −1), 124 | −z'de çarpışma yok; dinlenmede orta bant sağ ile 1,5 mm |
| F5 49 | H1 / H2 ısıl gömmeleri (8) | (0, −1, 0), 25 | uçmaz (d 0) | ev sahibi F5'te yok; somun etek arka bandının deliğinde (sınır kutusu içinde); −y'de bant malzemesine 2,6 mm |

Patlatma mesafesi: etek bantları 630–830 mm → 155–187 mm; F2–F4 bantları 304–521 → 124–180 mm (madde 3, mesafe kuralı bölüm 1).
Bütün yön farkı listesi (134 satır): scratchpad `f10d/yon_tablo.txt`.

## 5. Uçuş ve giriş istisnaları (gerekçeli)

Kalıcı denetim `rehber_sira.py`: `giris` (alt adım birimi ya da satırı yerine girebiliyor mu) ve `ucus_yolu` (her alt adım satırı
patlatılmış konumundan yerine giden düz yol). İkisinin de sınırı 0; aşağıdakiler grubun `giris_ok` / `ucus_ok` alanında gerekçeyle
yazılı, `kontrol.json`'da `istisna` listesinde. Uçuşta cıvatanın kendi eş somunu / ısıl gömmesi (dinlenmede sınır kutusu ortak) engel
sayılmaz (`es_dis`, 0,5 mm pay; cıvata deliğe somunla birlikte girer); 133 satır böyle.

| sınıf | adet | satırlar | ölçüm |
| --- | --- | --- | --- |
| Bindirme dudağı (K1) | 8 | 33.2 / 33.4 etek ön sağ / sol; 35.1 / 35.2 göğüs bandı; 35.5 çerçeve sağ / sol; 36.1 / 36.2 omuz bandı | hiçbir düz yönden serbest değil; engel bir önceki bandın 12 mm bindirme dudağı (çerçevede 34 mm); iki sıra da ölçüldü: kilitli |
| İki parçalı yol | 1 | 33.3 ön dolgu şeridi | önce +z 10 mm, sonra +y serbest; tek düz yol yok (sonar 3 mm) |
| Yön yuvarlama | 12 | F1 bindirme cıvataları ×4 (5,87°); F2 kelepçe cıvatası ×2 (1,33°), y792 yan ×2 (4,42°); F3 VESA cıvatası ×4 (0,97°) | tam sayı yöne yuvarlanınca 0,32–0,65 mm sürtme; gerçek eksende serbest |
| Model girişimi (K3) | 2 uçuş + 2 giriş | uçuş: 31.6 kamera (yüz kabuğu ısıl gömmesine 2,91 mm, dinlenmede 3,91 mm), 49.4 üst arka kapak (ısıl gömmeleri 0,5 mm; dinlenmede 1,5 mm); giriş: 34.5 orta bant sağ birimi (+x'te çarpışma yok, dinlenmede uzatma 2 sağ ile 5,53 mm), 49.4 üst arka kapak birimi | çarpışma dinlenmedeki ortak hacimden; geometri değişikliği kapsam dışı |
| Çekiç somun M6 | 2 | 35.3 | −z'de 1 mm sonra kanal dudağı 10 mm: somun kanala ucundan kaydırılır ya da döndürülerek oturtulur (düz z yolu yok) |

Uçuş: 240 satır, çarpışan 0 (sınır 0), gerekçeli istisna 25, eşik 0,2 mm (513 s). Giriş: girilemez 0 (sınır 0), gerekçeli istisna 2, E3 kafa girişi serbest (272 s); sıra denetimi ulaşılamaz 0 / 565 bağlantı.

## 6. Perdelenme (madde 6)

Ölçüm: voksel 3 mm, 26 yön, adım sonunda (alt adımlı adımlarda ayrıca her alt adım sonunda) hiçbir yönden görünmeyen yeni parça.
Toplam (adım sonunda, bütün adımlar): **önce 291 / sonra 291**. Adım sonu toplamı değişmez (adımın parçaları ve son
konumları aynı; alt adım yalnız ara durum ekler). Alt adımlarda gerekçesiz gizli 0 (sınır 0), gerekçeli
107.

| adım | yeni | önce gizli (HEAD) | sonra gizli (adım sonu) | alt adım başına gizli (alt adım sonu); gerekçe |
| --- | --- | --- | --- | --- |
| 1 A1 | 29 | 8 | 8 (0 parça + 8 bağlantı) |  |
| 2 A2 | 15 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 3 A3 | 15 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 4 B1a | 46 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 5 B1 | 28 | 10 | 10 (0 parça + 10 bağlantı) |  |
| 8 B2 | 16 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 10 B4 | 24 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 11 C0 | 30 | 6 | 6 (0 parça + 6 bağlantı) |  |
| 16 B7 | 14 | 4 | 4 (0 parça + 4 bağlantı) |  |
| 18 C1 | 48 | 9 | 9 (0 parça + 9 bağlantı) |  |
| 20 D1b | 20 | 8 | 8 (0 parça + 8 bağlantı) |  |
| 21 D1c | 4 | 0 | 0 (0 parça + 0 bağlantı) | 0/0; gerekçesiz 0, gerekçeli 0 |
| 22 D1 | 16 | 8 | 8 (0 parça + 8 bağlantı) |  |
| 23 E1a | 27 | 10 | 10 (0 parça + 10 bağlantı) |  |
| 27 E2c | 18 | 8 | 8 (0 parça + 8 bağlantı) |  |
| 28 E2 | 12 | 1 | 1 (1 parça + 0 bağlantı) |  |
| 29 E3a | 22 | 3 | 3 (3 parça + 0 bağlantı) |  |
| 30 E3 | 7 | 1 | 1 (0 parça + 1 bağlantı) | 0/0/1; gerekçesiz 0, gerekçeli 0 |
| 31 E4 | 60 | 46 | 46 (13 parça + 33 bağlantı) | 4/0/4/0/1/4/0/2/0/0; gerekçesiz 0, gerekçeli 15 |
| 33 F1 | 61 | 21 | 21 (0 parça + 21 bağlantı) | 11/2/0/0/0/0/0/0/0; gerekçesiz 0, gerekçeli 13 |
| 34 F2 | 87 | 30 | 30 (0 parça + 30 bağlantı) | 4/11/17/2/0/1; gerekçesiz 0, gerekçeli 35 |
| 35 F3 | 54 | 23 | 23 (0 parça + 23 bağlantı) | 2/2/2/0/6; gerekçesiz 0, gerekçeli 12 |
| 36 F4 | 18 | 11 | 11 (0 parça + 11 bağlantı) | 5/6; gerekçesiz 0, gerekçeli 11 |
| 37 G0 | 16 | 3 | 3 (0 parça + 3 bağlantı) |  |
| 38 G1 | 14 | 10 | 10 (0 parça + 10 bağlantı) |  |
| 39 G2 | 28 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 40 G3 | 26 | 4 | 4 (0 parça + 4 bağlantı) |  |
| 41 G4 | 12 | 2 | 2 (0 parça + 2 bağlantı) |  |
| 42 H0a | 42 | 3 | 3 (0 parça + 3 bağlantı) |  |
| 43 H0b | 4 | 0 | 0 (0 parça + 0 bağlantı) | 0/0; gerekçesiz 0, gerekçeli 0 |
| 44 H0c | 28 | 7 | 7 (3 parça + 4 bağlantı) |  |
| 45 H0d | 4 | 0 | 0 (0 parça + 0 bağlantı) | 0/0; gerekçesiz 0, gerekçeli 0 |
| 46 H0e | 10 | 0 | 0 (0 parça + 0 bağlantı) | 0/0; gerekçesiz 0, gerekçeli 0 |
| 47 H0f | 10 | 6 | 6 (0 parça + 6 bağlantı) |  |
| 48 H1 | 16 | 1 | 1 (0 parça + 1 bağlantı) |  |
| 49 F5 | 50 | 36 | 36 (2 parça + 34 bağlantı) | 1/0/11/0/9; gerekçesiz 0, gerekçeli 21 |
| **toplam** | | **291** | **291** | |

Gerekçe sınıfları (alt adım istisnaları):
- **Isıl gömme somun** (kategorik): baskıya gömülü, boss içinde; görünmesi beklenmez. İstisnaların çoğu bu.
- **Voksel yanlış pozitifi**: 3 mm voksel ince parçayı (köpük bant, kapak cıvatası, kamera vidası, tabla cıvatası, bant bindirme
  cıvatası) arkasındaki kabukla birleştiriyor. Bağımsız ölçüm (`F10d-dogrula.py --gizli`, piksel kimlik tamponu, alt adım kamerası
  + 9 ek yön): 33 voksel-gizli parçanın 31'i en az bir kamerada görünüyor (4–466 piksel); gerekçe metninde piksel sayısı ve kamera
  yazılı. Çıktı `planlama/d158/F10d-gizli-piksel.json`.
- **Gerçekten gizli**: çekiç somun M6 ×2 (35.3), direk kanalının içinde; takma anında elde, yerinde görünmez.

## 7. Görünürlük (madde 5) ve arayüz sınamaları

`F10d-dogrula.py` (görünürlük kimlik tamponundan, sınır kutusu köşeleri karede):

| konum | yeni | görünmeyen | karede değil | sonuç |
| --- | --- | --- | --- | --- |
| 21.1 / 21.2 D1c | 2 / 2 | 0 | 0 | GEÇTİ |
| 25 E2a (pan hornu) | 2 | 0 | 0 | GEÇTİ |
| 43.1 / 43.2 H0b | 2 / 2 | 0 | 0 | GEÇTİ |
| 45.1 / 45.2 H0d | 2 / 2 | 0 | 0 | GEÇTİ |
| 46.1 / 46.2 H0e | 5 / 5 | 0 | 0 | GEÇTİ |

Genel bakış kareleri (21, 43, 45, 46; iki kol tek karede) ve kabuk alt adımları yalnız bilgi olarak ölçüldü (sınır yok): kabukta
görünmeyenlerin hemen hepsi ısıl gömme somun ve ince bağlantı elemanı (bölüm 6'nın piksel ölçümü). **[Düzeltme turu 1 notu
(kontrol B-6): bu cümle yanlış. Aynı ölçümde 34.4'te hoparlör, kabın ön halkası ve köpük ped (ana parçalar), 35.4'te 4 VESA
cıvatası ve 4 pulu 0 piksel. Yeni ölçüm ve düzeltme: bölüm 11.]** Bilgi satırlarında dikkat
çekenler: 33.6 acil stop kontak gövdesi ve 33.9 ana anahtar gövdesi birim bağlanırken etek altında kalıyor (kamerada 0 piksel; voksel
ölçümünde alttan görünür, gizli sayılmıyor); 49.2 yeni parçası olmayan iş adımı.
Gezinme: konum 95 (ana 50 + alt 45), ileri / geri / doğrudan adres (20 örnek) GEÇTİ. Panel = takma: 95/95 konumda panel satır
sırası takma sırasıyla aynı. Telefon 360 px taşma 0. `F10d-dogrula`: GEÇTİ, 116 kare, 706 s.
`F10a-dogrula --kanit-yok` (alt adımlı gezinmeye uyarlandı): seçim 6/6, ağsız dış istek 0, konsol 0, mini görünüm 50/50 masaüstü +
360, yazdırma kareleri çizili 50/50 (boş 0), PDF görüntü 95, boş sayfa yok, tak kadrajı, CDN 0: GEÇTİ.

İlk koşuda 45 H0d ve 46 H0e kaldı: tek alttan kamerada (0,85, −0,62, 1,25) sağ kolun bilek hornu / flanşı + 4 cıvatası karede
değildi (iki kol x ekseninde 2 × ≈ 300 mm aralıklı). Düzeltme: D1c / H0b gibi sağ / sol alt adım (`yan`), kendi yanından alttan
kamera (±1,0, −0,6, 0,5). Alt adım sayısı 41 → 45.

## 8. Komutlar ve çıkış kodları

| komut | çıkış | süre / not |
| --- | --- | --- |
| `py -3 tasarim/freecad/rehber/rehber_uret.py` (tam, 1.) | 1 | ozet_yaz cp1254 konsolda "→" basamadı; `kontrol.json` yazılmadı → `rehber_uret.py` başında `stdout.reconfigure(errors="replace")` |
| `py -3 tasarim/freecad/rehber/rehber_uret.py` (tam, 2.) | 0 | 41 alt adım; `uret_tam2.log` |
| `py -3 planlama/d158/F10a-dogrula.py --kanit-yok` | 2 → 0 | ilk koşu: `app.js` sözdizimi (yorum satırı kodu yutmuş) ve `takili` tanımsız; ikisi düzeltildi |
| `py -3 planlama/d158/F10d-dogrula.py --gizli …` | 0 | piksel ölçümü, `F10d-gizli-piksel.json` |
| `py -3 planlama/d158/F10d-dogrula.py` (1.) | 2 | 45 / 46 görünürlük (bölüm 7) |
| `py -3 tasarim/freecad/rehber/rehber_uret.py` (tam, 3.) | 0 | H0d / H0e sağ / sol alt adım |
| `py -3 planlama/d158/F10a-dogrula.py --kanit-yok` | 0 | |
| `py -3 planlama/d158/F10d-dogrula.py` (2.) | 0 | |
| `py -3 planlama/d158/F9b-dogrula.py` | 0 (hata 0) | |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 (17 dosya özeti kayıtla aynı) | |
| `py -3 tasarim/freecad/regresyon.py --yazma` | 0 (10/10 aynı, kötüleşen yok) | |

Her FreeCAD koşusunda kilit satırı "F10d ajan A: rehber_uret.py tam üretim (tarih)", bitince "boş". Ağır ölçümler tek tek,
ara sonuçlar scratchpad `f10d/` altında.

## 9. Bakılan kareler

`planlama/d158/F10d-goruntu-<adım>-<alt>-<acik|koyu>.png` (00 = genel bakış) ve 31 / 33 için `-once-sonra-` (solda HEAD tek kare,
sağda alt adım kareleri). Kendim baktıklarım ve gördüğüm:

Her alt adım ve genel bakış karesi, açık ve koyu (116 kare; scratchpad `f10d/sheet/` altında adım başına temaya göre
birleştirilmiş sayfalar olarak), ayrıca 31 / 33 önce-sonra (açık + koyu). Ayrıca birkaçını tam boy (25, 21.1, 31.6, 34.4, 35.4,
36.1, 43.2, 49.5).
- 21.1 / 21.2, 43.1 / 43.2, 45.1 / 45.2, 46.1 / 46.2: horn / flanş + vidalar karenin ortasında, iki temada da seçik. Genel bakışta
  (xx.0) iki kol uzak; sağ kol parçaları kenarda ya da dışarıda (bilgi, alt adımlar bunu çözüyor).
- 25: pan hornu ve merkez vidası boyun yatağı saydam çizilerek tam görünüyor.
- 31: 31.1 / 31.3 masada kabuk + ReSpeaker / ses kartı, 31.2 / 31.4 birim kafada, 31.5 tabla cıvataları içeriden (sarı, küçük),
  31.6–31.8 masada yüz grubu (kamera, QLED arkadan, tırnaklar), 31.9 yüz grubu kafada, 31.10 dikiş cıvataları. Önce tek karede
  yalnız dış kabuk görünüyordu; sonra iç parçalar kabuktan önce, kendi karelerinde.
- 33: bantlar sırayla; 33.5 / 33.8 masada acil stop / ana anahtar. 33.6 / 33.9 karelerinde kontak gövdesi / anahtar etek altında
  görünmüyor (bilgi).
- 34: bantlar alttan üste; 34.4 masada hoparlör grubu. Masa karesinde gövde içi kablo yolları birimle birlikte havada çiziliyor
  (gözlem, aşağıda).
- 35: 35.3 taşıyıcı + çekiç somun (somun kanalda görünmüyor, istisna), 35.4 ekran (kamera alttan-arkadan, ekran + VESA cıvataları
  görünür), 35.5 çerçeve. **[Düzeltme turu 1 notu (kontrol B-6): "VESA cıvataları görünür" yanlış. Kendi `F10d-dogrula.json`
  ölçümüm de 4 cıvata + 4 pul için 0 piksel veriyordu; karede görünen ekran ve kablolardı. Yeni ölçüm ve düzeltme: bölüm 11.]**
- 36: sağ / sol bant ayrı karelerde; genel bakış yalnız sağ tarafı gösteriyor (bilgi).
- 49: 49.1 masada kapak + hub, 49.2 robot bütün (iş adımı), 49.3 arka kapak, 49.4 üst kapak birimi, 49.5 H1 / H2 kapakları.
Boş ya da bozuk kare görmedim. Bazı karelerde alt çubuk ve "Robotun neresi" kutusu görünüyor (ekran görüntüsü boyu farkı), içerik
aynı.

## 10. Dokunulan dosyalar, karar / açık maddeler, brief dışı gözlemler

**Dokunulan:**
- `tasarim/freecad/rehber/`: `rehber_metin.py`, `rehber_veri.py`, `rehber_sira.py`, `rehber_denetim.py`, `rehber_uret.py`
- `rehber/`: `app.js`, `index.html`, `stil.css`, `yazdir.html`, `veri/rehber-veri.js`, `veri/rehber-veri.json`, `goruntu/*`
  (`veri/robot.glb` ve `robot-glb.js` HEAD ile aynı bayt)
- `planlama/rehber/`: `Lale-montaj-rehberi.pdf`, `kontrol.json`, `goruntu/*`
- `planlama/d158/`: `F10d-gunluk.md`, `F10d-dogrula.py`, `F10d-dogrula.json`, `F10d-gizli-piksel.json`, `F10d-goruntu-*.png`,
  `F10a-dogrula.py` / `.json` (madde 7: alt adımlı gezinmeye uyarlama, ölçtüğü şey aynı), `FREECAD-KILIT.txt`

**Karar (uygulanmadı):**
- **F10d-K1 bindirme dudakları:** F1 ön bantları, F3 göğüs bantları ve çerçeve, F4 omuz bantları hiçbir düz yoldan girmiyor (12 mm
  dudak; çerçevede 34 mm). Seçenekler: (a) bugünkü gibi "esneterek / eğerek takılır" istisnası; (b) CAD'de bindirme yönünü
  değiştirmek (geometri, bu paketin dışında); (c) rehberde iki parçalı yol (önce eğik, sonra yerine). Öneri: (b) bir sonraki
  geometri paketinde ölçülsün; o zamana kadar (a).
- **F10d-K2 F5 ısıl gömmeleri:** H1 / H2 kapaklarının ve arka kapağın ısıl gömmeleri bant malzemesinde; ev sahibi bandın hazırlığına
  (F1 / F2) taşınmalı. Şimdilik F5'te "uçmaz" (d 0). Öneri: taşı (sayı değişmez, adım değişir; sıra ölçümü gerekli).
  **[Düzeltme turu 1 notu: K2 karar değil, veri düzeltmesi; kapsamı da buradakinden geniş (kontrol B-2). Bütün ısıl gömmeler için
  ev sahibi geometriyle bulundu ve somunlar ev sahibinin adımına taşındı: bölüm 11.]**
- **F10d-K3 model girişimleri:** orta bant sağ ↔ uzatma 2 sağ 5,53 mm; üst arka kapak ↔ göğüs bandı sağ 1,5 mm; arka servis kapağı
  ↔ orta bant 1,5 mm; kamera ↔ yüz kabuğu 3,91 mm. Öneri: kabuk modelinde düzeltilsin (tam tarama gerektirir).
  **[Düzeltme turu 1'de geri çekildi, bkz. kontrol B-4: bu sayılar eksen ışınının yüzeye teğet geçtiği yerdeki kiriş boyu, derinlik
  değil. Gerçek derinlik 0,057–0,28 mm; ayrıntı bölüm 11.]**

**Açık:** - Karar maddeleri F10d-K1, K2, K3 (yukarıda) kuyruğa yazılmadı (`karar-kuyrugu.md` dokunulmaz); koordinatöre.
- 33.6 / 33.9 kamerada görünmeyen birim parçaları (acil stop kontağı, ana anahtar): voksel ölçümü geçiyor, piksel ölçümü 0; F10e
  kamera / saydam ayarıyla bakılabilir.
- Görünürlük sınırı (madde 5) yalnız 21, 25, 43, 45, 46 için; kabuk alt adımlarında piksel görünürlüğü yalnız bilgi.

**Brief dışı gözlemler (dokunulmadı):**
- 3 mm voksel perdelenme ince parçalarda yanlış pozitif veriyor (bölüm 6); piksel ölçümü kalıcı denetime alınabilir.
- 34.4 "masada" karesinde kablo yolları (gövde içi) masa birimiyle birlikte havada görünüyor; masa kipinde kablo gizlenmesi F10e'ye
  not.
- Benden önce var olan değişiklikler: `tasarim/freecad/kabuk/gorsel/*.png` (9 Kasım), `tasarim/freecad/montaj/yerlesim-kontrol.json`
  (3 Kasım); `planlama/dongu-158.md` bu oturumda koordinatör tarafından değişti (P10.4 satırı). Hiçbirine dokunmadım.

## 11. Düzeltme turu 1 (kontrol `F10d-kontrol.md` B-1 … B-12)

**Durum: tamamlandı, FreeCAD'siz yoldan** (11.9, 11.13).
- İlk tam üretim çıkış 2 ile bitti (`denetim`, `perdelenme`). İkisi düzeltildi.
- İkinci tam üretim veriyi (`rehber-veri.*`, `robot.glb`) ve PDF'i yazdı, sonra sistem belleği azaldığı için dışarıdan durduruldu.
- Makinede kullanılabilir bellek 1–3,5 GB arasındaydı. Nedeni çekirdek havuzuydu, süreç kapatarak düzelmiyordu. Bu yüzden FreeCAD
  yeniden koşulmadı.
- Veri ikinci üretimden ve son kod hâlinden:
  - kod dosyalarının hepsi ikinci üretimin başlangıcından önce değişmiş;
  - veride 1192 parça ve taşınan 59 somun var;
  - veride 34.5 / 34.7 `gizli_ok` metinleri ve 7 K1 metni var;
  - sha256 `rehber-veri.json` 6aaaf339feed058a…, `robot.glb` 760bf1ff5955ce03….
- Bu veriyle FreeCAD'siz üretim (`rehber_uret.py --veri-yok`) koşuldu: çıkış 0, sorunlu kalem yok. `kontrol.json`, kareler ve PDF
  artık aynı veriden.
- Sonra doğrulama zincirinin beşi koşuldu, beşi de geçti.

Aşağıdaki sayılar son veriyle ölçüldü. Farklıysa koşunun adı yazılı.

### 11.1 Isıl gömme ev sahibi (B-2, K2)

- Yöntem (`rehber_veri.py`): somunun 0,8 mm dışındaki 24 halka noktasından en çoğunu malzemesinin içinde tutan ana parça (Part
  isInside; bütün ana parçalar aday, sınır kutusu merkezine 8 mm'den yakın kutulu olanlar). Somun ev sahibinin adımına ve alt
  montajına taşınır. Sonuç `rehber-veri.json` → `isil_gomme`.
- 164 somun, 164 ev sahipli, ev sahipsiz 0. En düşük skor 24 / 24 (isInside). Sıra denetiminin ağ (mesh) yöntemiyle bağımsız
  denetimi (ilk tam üretim): hata 0, en düşük skor 9 / 24.
- Taşınan 59:

| eski adım | yeni adım | ev sahibi | adet |
| --- | --- | --- | --- |
| 20 D1b | 19 D1a | Omuz yuvası | 8 |
| 27 E2c | 26 E2b | Boyun mili | 4 |
| 28 E2 | 27 E2c | Eğme çatalı | 1 |
| 35 F3 | 34 F2 | Gövde orta bandı sağ / sol | 3 / 3 |
| 36 F4 | 35 F3 | Göğüs bandı sağ / sol | 3 / 3 |
| 39 G2 | 37 G0 | Omuz göbeği | 2 |
| 41 G4 | 36 F4 | Omuz bandı sağ / sol | 2 / 2 |
| 44 H0c | 42 H0a | Ön kol gövdesi | 2 |
| 47 H0f | 46 H0e | Bilek flanşı | 4 |
| 49 F5 | 33 F1 | Etek arka sağ / sol | 6 / 2 |
| 49 F5 | 34 F2 | Gövde orta bandı sağ / sol | 4 / 3 |
| 49 F5 | 35 F3 | Göğüs bandı sağ / sol | 4 / 3 |

- K2 bu yüzden karar değil, veri düzeltmesi. 49.1 metni ve F5 `baglanti_md` buna göre (somunlar bantlarda, F1 / F2 / F3).
- Denetim kalıcı: üreticinin `isil_gomme` adımı (hata sınırı 0) ve sıra denetimindeki ağ denetimi.

### 11.2 Kendi karesinde görünürlük (B-1, B-7, B-8)

- Ölçüt (`F10d-dogrula.py`, `app.js` `RehberTest.gorunurluk()`): yeni parça, alt adımın kendi kamerasında **≥ 30 piksel ve tek
  başına çizilişinin ≥ %20'si**, sınır kutusunun köşeleri güvenli alanda. Saydam (opaklık < 0,5) çizilen parça arkasını örtmez.
  Saydam yeni parça tek tek ölçülür: opak parçalarla birlikte yalnız o çizilir.
- Eşik gerekçesi: 30 piksel kontrolün önerisi (B-7). 31.8 köpük bandı eski ölçütle 4–5 pikselle geçiyordu. %20 oranı, büyük bir
  parçanın çoğu örtülüyken birkaç yüz pikselle geçmesini önler.
- Isıl gömmeler de ölçüme girdi (B-8): `gizli_piksel` istisna listesini de ölçüyor. Isıl gömmenin ev sahibi o karede saydam (0,25;
  yeni parça 0,4).
- Sonuç (veri: ikinci hızlı veri üretimi `--gorsel-yok --ek-yok`, kamera / saydam ayarları ve B-11 düzeltmesiyle):

| ölçüm | konum | yeni parça | görünmeyen | istisna |
| --- | --- | --- | --- | --- |
| önce (bu turun başı) | 46 sınırlı | 363 | 171 (100'ü ısıl gömme) | (piksel istisnası yok, ölçüt yoktu) |
| ara | 46 | — | 16 | 0 |
| sonra | 61 sınırlı (kabuk alt adımı 42) | kabuk 335 | **0** | **0** |

  Masada bağlanan birimlerin iç parçaları 58; hepsi masada yeni oldukları alt adımda görünür. Masa alt adımında yabancı şema 0.
- Son veriyle yeniden ölçüldü (`F10d-dogrula.py`, 11.9):
  - kabuk alt adımı 42, yeni parça 335, görünmeyen 0, istisna 0;
  - birim içi parça 58; masada yabancı şema 0.
- Gizli piksel (`--gizli kontrol.json`): perdelenmede gerekçeli gizli 102 parçanın 102'si kendi alt adım karesinde pikselli. En
  düşüğü 31 px (36.1, x 0 dikişindeki ısıl gömme); 30'un altında 0. Bunların 77'si ısıl gömme.
- Genel bakış kareleri (21, 43, 45, 46; iki kol uzak) sınır dışı, bilgi olarak "KALDI (bilgi)". F10d'nin ilk turundaki gibi; alt
  adımları geçiyor.
- Kamera ve saydam taraması: her alt adım için 14 kamera yönü × saydam kümeleri (S1: alt adımın saydamı + ev sahipleri + yeni baskı
  parçaları; S2: + o ana kadarki kabuk / kafa baskıları; S3: + kendi baskı dışı parçaları). İlk geçen seçilip elle sadeleştirildi.
- Alt adım bölmeleri (kabuk alt adımı 37 → 42; bütün alt adım 45 → 50; konum 95 → 100):
  - 33 F1: orta bant sağ / sol ayrı; ön sağ, dolgu ön, ön sol; masada arka sağ + acil stop, bağ, arka dolgu, masada arka sol + ana
    anahtar, bağ (10).
  - 34 F2: alt, uzatma 1, uzatma 2 bantları sağ / sol ayrı; masada orta bant sağ + hoparlör, bağ, orta bant sol (9). Eski 34.4
    (hoparlör) şimdi 34.7, eski 34.5 (bağ) 34.8.
  - 36 F4: omuz bandı sağ; sol ön dikiş; arka dikiş (3).
  - 31, 35, 49 bölünmedi; kamera ve saydam değişti (`rehber_metin.py` E4, F3, F5).

### 11.3 Masada yabancı kablo (B-3)

`app.js` `semaDurum`: masa alt adımında, başka adımın şeması "gizli". Ölçüm: masa alt adımlarında görünen yabancı şema 0 (11.2
ile aynı koşu).

### 11.4 Uçuş ve giriş istisnaları (B-5, B-12; ölçülmemiş 10)

- B-5: yön yuvarlama istisnaları (12) kaldırıldı. `ucus_yolu` eksen ya da köşegen yönde tam sayı yönle, değilse gerçek yönle ölçüyor.
  Son veri (`--veri-yok`): 240 uçuş satırı, istisnasız çarpışan 0, gerekçeli istisna 12 (ilk tam üretimle aynı). Hepsi aşağıda ve
  ölçülü.
- 35.4 göğüs ekranı (0, 1, 4): gerçek yön (0, 0,243, 0,97), h 0,5 mm, d 173,6 mm, **serbest** (istisna değil).
- B-11 düzeltmesi 35.4'ün VESA cıvatalarını ekranın d'siyle uzatıyordu (ters yöne uçan cıvata 160 mm'de göğüs bandına 4,73 mm). Yön
  koşulu eklendi. İlk tam üretimde 35.4'te istisna da çarpışma da yok.
- Kalan 12 istisna (ilk tam üretim) ve gerekçe türü:

| alt adım | parça | gerekçe türü |
| --- | --- | --- |
| 31.6 | Kamera | dinlenmede temas. −z'de ışın 2,91 mm kiriş; gerçek derinlik 3–8 mm'de yüz kabuğu sağ ile en çok 1,0 mm, ısıl gömmeyle 0,24 mm, 10 mm'den sonra 0. Elde denenmedi |
| 33.3 / 33.5 | Etek ön sağ / sol | K1 bindirme (11.5) |
| 33.4 | Etek dolgu şeridi ön | iki parçalı yol ölçüldü: +z 10 mm sonra +y 170 mm serbest. Düz +y'de sonar 1–82 mm |
| 35.1 / 35.2 | Göğüs bandı sağ / sol | K1 bindirme |
| 35.3 ×2 | Çekiç somun M6 | düz yol yok. −z'de direk kanalı 2–25 mm; −y'de 400 mm boyunca yalnız kendi cıvatası 2–6 mm; +y'de kendi cıvatası 2–66 mm, sonra travers. Somun kanalın içinde, takılırken elde |
| 35.5 ×2 | Göğüs ekranı çerçevesi sağ / sol | K1 bindirme |
| 36.1 / 36.2 | Omuz bandı sağ / sol | K1 bindirme |

- Giriş istisnası 2 (K3; 11.7): 34.8 orta bant sağ, 49.4 üst arka kapak.
- B-12: "travers ucundan kaydırarak sok" (D1) ölçülmemişti. Metin "omuz gövdesini travers ucuna oturt (giriş yolu ölçülmedi)" oldu.
- Bütün adım metinlerinde "kaydır" taraması (son veri) iki yer buldu:
  - adım 30 "çapraz ya da kaydırmalı yol ölçülmedi" (zaten ölçülmedi diyor);
  - adım 41 G4 "+x'ten kaydırarak takılmaz" (F10d öncesi olumsuz uyarı). Bu ölçülmedi, metne dokunulmadı.

### 11.5 F10d-K1 ölçümü ve karar önerisi

Yöntem (bu turda): `rehber_giris` ışın ölçümü, h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım. "a–b mm" parçanın o yolda a'dan b
mm'ye kadar o engelle ortak hacmi. Dinlenmedeki temas sayılmaz. Isıl gömmeler ev sahibine taşındıktan (11.1) sonraki veriyle.

| bant | yön | ilk engel ve aralık | ayrılma |
| --- | --- | --- | --- |
| Etek ön sağ | (1, 0, 1) çizilen | sonar 1–12 mm | — |
| | +x | sonar 1–73 mm | 235 mm |
| | +y | braket perçin somunu 1–7, sonar 1–81, M6 45–63 mm | — |
| | +z | yalnız braket perçin somunu 1–7 mm | 183 mm |
| | −z | orta bant boyunca | — |
| Etek ön sol | (−1, 0, 1) | sonar 1–11 mm | — |
| | −x | sonar 1–61 mm | 223 mm |
| | +y | perçin somunu 1–7, sonar 1–81 mm | 229 mm |
| | +z | yalnız perçin somunu 1–7 mm | 183 mm |
| Göğüs bandı sağ | +x | orta bant sağ 1–159 mm, ısıl gömme 17–111 mm | 173 mm |
| | +y | orta bant 1–13 mm | — |
| | ±z | orta bant 1–213 mm | 215 / 219 mm |
| Göğüs bandı sol | −x | orta bant sol 1–135 mm | 161 mm |
| | +y | orta bant sol 1–13, göğüs bandı sağ 1–19 mm | — |
| | ±z | orta bant sol 1–213, göğüs bandı sağ 1–215 mm | 219 mm |
| Çerçeve sağ | +z | göğüs bandı 1–9, ekran 3–7 mm | 65 mm |
| | +x (yana, dışa) | göğüs bandı 2–150, orta bant 4–108 mm | — |
| | +x 20 sonra +z 150 | göğüs bandı 2–30 mm | — |
| | +y / −z | göğüs bandı 1–51 / ekran 1–31, direk 49–145 mm | — |
| Çerçeve sol | +z | göğüs bandı sol 1–9, göğüs bandı sağ 3–7, ekran 3–7 mm | 67 mm |
| | −x | göğüs bandı sol 1–151 mm | 153 mm |
| Omuz bandı sağ | +x | göğüs bandı 1–161, rulman kapağı 3–99, yuva bağlantı cıvatası M6 3–29 mm | 173 mm |
| | +y | 7 mm'den: rulman kapağı 7–101, kapak cıvatası 19–79, omuz yuvası 21–53 mm | — |
| | +z / −z | göğüs bandı 1–161 / 1–19, M6 3–105 mm | — / 165 mm |
| Omuz bandı sol | −x | göğüs bandı sol 1–137, rulman kapağı 3–99, M6 3–29 mm | 161 mm |
| | +y | rulman kapağı 7–101 mm | — |
| | ±z | göğüs bandı sol 1–161 / 1–19, omuz bandı sağ 1–151 / 1–153 mm | — / 165 mm |

Belgeler: `tasarim/freecad/kabuk/kabuk_parcalar.py` (baş) ve `kabuk_rapor.py` (≈ 211) bindirme dilini tarif ediyor, bantların
takma biçimini tarif etmiyor. Çerçeve için `kabuk_parcalar.py` (≈ 297): "Yarım C yana çekilince kasadan ayrılır: bant + çerçeve ekran
takılıyken sokulabilir". Bu kasaya göre; ölçümde yana yol göğüs bandıyla 2–150 mm ortak hacimli.

> **F10d-K1 · Kabuk bindirme dilleri: bantlar düz yoldan girmiyor (ölçüldü)**
> - **Soru:** Etek ön, göğüs, omuz bantları ve göğüs ekranı çerçevesi hiçbir düz yoldan yerine girmiyor. Okura nasıl tarif edilsin,
>   geometri mi değişsin?
> - **Ölçüler** (F10d düzeltme turu 1, ışın h 0,5 mm, eşik 0,2 mm):
>   - Göğüs ve omuz bantları: yana yolda bir alttaki bandın dili 1–135 / 1–161 mm boyunca ortak hacimli, 161–173 mm'de ayrılıyor.
>     Omuzda ayrıca rulman kapağı 3–99 mm.
>   - Etek ön: +z'de yalnız braket perçin somunu 1–7 mm, sonra serbest. Öbür yönlerde sonar 1–81 mm.
>   - Çerçeve: +z'de göğüs bandı 1–9 mm ve ekran 3–7 mm; yana 1–151 mm.
>   - Kabuk belgeleri dili tarif ediyor, takma biçimini tarif etmiyor.
> - **Seçenekler:**
>   a) Metin: "bandı hafifçe esneterek dili alttaki bandın arkasına sok" (geometri değişmez; baskı kuponunda denenmeli);
>   b) geometri: dilde pah ya da ön / arka yarıda ters bindirme; kabuk çakışma taraması gerekir;
>   c) rehberde iki parçalı yol. Etek ön için aday: +z 7 mm'den sonra serbest, ama ölçülmedi. Bantlar için düz iki bacak bulunmadı;
>      çerçevede +x 20 sonra +z 150 çarpıyor.
> - **Öneri:**
>   - Etek ön için (c), iki bacaklı yol ölçülsün.
>   - Göğüs, omuz ve çerçeve için (a) geçici olsun, kuponda denensin; (b) bir sonraki geometri paketinde.
>   - Karar Ahmet'te.

Rehber metinleri (`rehber_metin.py` F1 / F3 / F4 `ucus_ok`) bu ölçülerle yeniden yazıldı. 33.3'teki ölçülmemiş "sonarı ve perçin somunu
deliklerine oturtarak yerine yatır" kaldırıldı. Göğüs bandındaki "esneterek oturt" de kaldırıldı.

### 11.6 F10d-K2

Veri düzeltmesi olarak uygulandı (11.1).

### 11.7 F10d-K3 geri çekildi (B-4)

Eski sayılar eksen ışınının yüzeye teğet geçtiği yerdeki kiriş boyuydu. Gerçek derinlik, dinlenmede yüzey örnek noktalarının katı
içindeki nokta–üçgen uzaklığıyla ölçüldü:

| çift | eski | gerçek derinlik en çok / medyan |
| --- | --- | --- |
| orta bant sağ ↔ uzatma bandı 2 sağ | 5,53 mm | 0,28 mm / 0 (bir ölçümde 0,082) |
| üst arka kapak ↔ göğüs bandı sağ | 1,5 mm | 0,057 mm / 0 |
| kamera ↔ yüz kabuğu (dinlenme) | 3,91 mm | 0,000 (temas) |

Arka servis kapağı ↔ orta bant **yeniden ölçülmedi**. 34.8 ve 49.4 `giris_ok` metinleri "temas, çarpışma değil" diye yeniden yazıldı.
49.4'teki eski 0,5 mm uçuş çarpışması, kapakla uçan yanlış ev sahipli ısıl gömmelerdendi (11.1). İlk tam üretimde 49.4 temiz.

### 11.8 B-6, B-9, B-10, B-11

- **B-6:** bölüm 7 ve 9'daki iki cümleye not düşüldü; eski metin duruyor.
- **B-9:** `rehber_uret.py` yazdırma piksel denetimi ana + alt adım karelerini sayıyor. Son veri (`--veri-yok`):
  - 100 kare, piksel denetimi 100 / 100, boş 0, en düşük çizim oranı 0,060;
  - F10a: PDF görüntü 100, boş sayfa yok.
- **B-10:** `app.js` gezinmede `replaceState` ile sorgudaki `adim`'i de güncelliyor. Tarayıcıda sınandı (geçici betik, depoya
  yazmaz). 3 / 3 geçti:
  - `?adim=30` + 6 ok → `?adim=31.5#31.5`;
  - `?adim=33.2` + 3 ok → 33.5;
  - `?adim=0` + 2 ok → 2.

  Her birinde yenilemeden sonra konum aynı.
- **B-11:** `rehber_veri.py` `CIV_UZAT`. Cıvatanın başı aynı alt adımda gelen ve aynı yöne uçan ana parçanın kutusundaysa d =
  max(kendi d, parçanın d + 25).

### 11.9 Komutlar

Her ağır komuttan önce kullanılabilir bellek ölçüldü (sütun "bellek"). Komutlar tek tek koşuldu, aynı anda iki ağır süreç yoktu.

| komut | bellek | çıkış | not |
| --- | --- | --- | --- |
| `rehber_uret.py --gorsel-yok --ek-yok` ×3 | — | 0 | hızlı veri (FreeCAD); tarama ve ara görünürlük ölçümleri bunlarla |
| `rehber_uret.py` (tam, 1.) | — | 2 | sorunlu iki kalem, aşağıda. Öbür sonuçlar son koşuyla aynı |
| `rehber_uret.py` (tam, 2.) | — | — | veri ve PDF yazıldı; sonra sistem belleği azaldığı için dışarıdan durduruldu. Kilit elle "boş" yapıldı |
| `rehber_uret.py --veri-yok` (FreeCAD'siz) | 1,22 GB | 0 | ayrıntı aşağıda |
| `F10d-dogrula.py` | 3,12 GB | 0 | GEÇTİ, 830 s, kare 126. Konum 100 (ana 50 + alt 50); ileri / geri / doğrudan 20 eşit; panel = takma 100 / 100; kabuk görünmeyen 0; 360 px taşma 0 |
| `F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | 3,40 GB | 0 | 102 / 102 pikselli, en düşük 31 px |
| `F10a-dogrula.py --kanit-yok` | 3,48 GB | 0 | GEÇTİ. Seçim 6 / 6, ağsız dış istek 0, konsol 0, kadraj ortanca 0,173 → 0,401, taşan 0, mini görünüm 50 / 50 masaüstü + 50 / 50 360 px, PDF görüntü 100, boş sayfa yok, CDN 0 |
| `py -3 -X utf8 planlama/d158/F9b-dogrula.py` | 2,64 GB | 0 | GEÇER (hata 0) |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 2,61 GB | 0 | izlenen 17 dosyanın özeti kayıtla aynı |
| `py -3 planlama/d158/regresyon.py --yazma` | 2,46 GB | 0 | GEÇER, hepsi okundu, kötüleşen yok |
| B-10 tarayıcı sınaması (geçici betik) | — | 0 | 3 / 3 |

Birinci tam üretimin sorunlu iki kalemi:
- **`denetim`:** ASCII kalıntı 9. Bunlar bu turun metinlerindeki doğru Türkçe kelimeler: braketin, brakete, saydam, yerinden, yolda,
  karede, arkada, kapaklarda, bantta. `rehber_denetim.py` `ASCII_TAMAM` listesine eklendi.
- **`perdelenme`:** alt adımda gerekçesiz voksel-gizli 2 parça: 34.5 bindirme cıvatası y634 arka ve 34.7 köpük ped. Piksel ölçümünde
  kendi karelerinde görünüyorlar (122 / 222 ve 315 / 315 px). `gizli_ok` eklendi.

`--veri-yok` neyi koştu, neyi koşmadı:

| denetim | durum (son veri) |
| --- | --- |
| tarayıcı kontrolü, ana adım | 50 / 50, konsol hatası 0, her parça tek adımda: evet |
| alt adım kontrolü | 50 / 50, her parça tek alt adımda: evet |
| yazdırma görüntüsü (ana + alt) | 100 kare, piksel denetimi 100 / 100, boş 0, en düşük çizim oranı 0,060 |
| telefon 360 px | 7 örnek adım, taşma 0 |
| yazdırılabilir / PDF | 69 sayfa (adım 50, devam 19), HTML 69, eşleme tutarlı, taşan yok, en küçük yazı DOM 8,1 / PDF 8,1 pt, 11 119 kB |
| metin denetimi | ASCII kalıntı 0, gruplama yanlış 0, çelişki 0, zorunlu uyarı eksik 0 / 40, yasak 0, kopya eki 0; parça 1192, şema 13 |
| sıra | 565 bağlantı, ulaşılamaz 0, sınama geçti (2016 s) |
| giriş | girilemez 0, E3 kafa girişi serbest, sınama geçti; istisna 2 (34.8, 49.4; temas) |
| uçuş | 240 satır, istisnasız çarpışan 0, gerekçeli istisna 12 |
| ısıl gömme (ağ denetimi) | 164 somun, hata 0, en düşük skor 9 / 24 |
| perdelenme | alt adımda gerekçesiz gizli 0, gerekçeli 102 |
| **koşmayan:** veri üretimi (FreeCAD) | geometri, ağ / GLB ve ısıl gömmenin katı (isInside) atanması. Son geçerli sonuç ikinci tam üretimden (veri sha yukarıda): 164 / 164 ev sahipli, taşınan 59, en düşük skor 24 / 24 |

### 11.10 Anlaşılırlık (kabuk alt adımları, son veri, açık + koyu)

42 alt adımın açık ve koyu karelerinin hepsine baktım (`F10d-goruntu-<adım>-<alt>-<acik|koyu>.png`). Koyu temaya özgü sorun yok;
iki temada da hüküm aynı. PDF'in değişen sayfalarına da baktım (41, 44, 46, 48: adım 33 / 34 alt adım kareleri ve parça listeleri).
Hepsi düzgün, taşma yok.

| alt adım (şimdi) | kontrol (önce) | şimdi | gerekçe |
| --- | --- | --- | --- |
| 31.1–31.4 | açık | açık | masada kabuk + ReSpeaker / ses kartı, sonra kabuk kafada |
| 31.5 | zor | **zor** | tabla → raf cıvataları: 4 sarı cıvata görünür, ama saydam kabuklar ve kablolar arasında raf ayırt edilmiyor |
| 31.6–31.8 | açık | açık | kamera, QLED, tırnaklar yüz kabuğunda |
| 31.9 | zor | **zor** | yüz grubu kafada belli; metindeki 4 kablo bağlantısı karede yok (değişmedi) |
| 31.10 | zor | **zor** | arka kameradan 9 dikiş cıvatası görünür, ama saydam kafanın içi kablo yoğun, cıvatalar küçük |
| 33.1, 33.2 | (yoktu; eski 33.1) | açık | orta bant sağ / sol ayrı; bant saydam, braket ve cıvatalar görünür |
| 33.3–33.5 | açık | açık | ön sağ, dolgu, ön sol sırayla |
| 33.6 (masada acil stop) | zor (eski 33.5) | açık | mantar ve kontak gövdesi görünür, havada yabancı kablo yok |
| 33.7, 33.8 | açık | açık | |
| 33.9 (masada ana anahtar) | zor (eski 33.8) | açık | anahtar gövdesi görünür, havada yabancı kablo yok |
| 33.10 | açık | açık | |
| 34.1, 34.2 | açık (eski 34.1) | açık | alt bant sağ / sol ayrı |
| 34.3, 34.5 | açık | açık | uzatma bandı turuncu, alttaki gri; braket + cıvata ortada |
| 34.4, 34.6 | açık | **zor** | sol bantlar: arka-içten kamera, bant kareyi dolduruyor; x 0 dikişinin cıvataları kenarda, küçük |
| 34.7 (masada hoparlör) | **anlaşılmıyor** (eski 34.4) | **zor** | grup ızgara duvarının iç yüzünde, hoparlör ve kelepçe cıvataları görünür; ön halka / ped / kab sırası karede ayırt edilmiyor, metinde (sıra kaynakta yok) |
| 34.8, 34.9 | açık | açık | bant gövdede, hoparlör içinde görünür |
| 35.1, 35.2 | açık | açık | |
| 35.3 | açık | **zor** | taşıyıcı ve cıvatası görünür, ama kadraj yakın, kablolar önde, kanal ve çekiç somun seçilmiyor |
| 35.4 | **anlaşılmıyor** | açık | ekran saydam; arkasındaki 4 VESA cıvatası taşıyıcıda görünür |
| 35.5 | açık | açık | |
| 36.1, 36.2 | açık | açık | |
| 36.3 | (yoktu) | **zor** | arka dikişin 3 cıvatası görünür, ama kadraj yakın ve kablolar önde; yer yalnız küçük görünümden okunuyor |
| 49.1 | zor | açık | masada kapak + hub; ısıl gömmeler artık kapakta değil, yabancı kablo yok |
| 49.2–49.5 | açık | açık | 49.3 / 49.4 kadrajı yine benzer |

Toplam:
- önce (kontrol, 37 alt adım): açık 29, zor 6, anlaşılmıyor 2;
- sonra (42 alt adım): **açık 34, zor 8, anlaşılmıyor 0.**

Zor kalanların gerekçesi:
- kadraj yakın ya da içten bakış (34.4, 34.6, 35.3, 36.3);
- kablo / saydam kalabalığı (31.5, 31.10);
- karede olmayan kablo bağlantısı (31.9);
- grubun iç sırası karede ayırt edilmiyor (34.7).

Bunların hiçbirinde parça 0 piksel değil (11.2). Düzeltme kamera / kadraj işi; bu turda yapılmadı.

### 11.11 Dokunulan dosyalar (bu tur)

- `tasarim/freecad/rehber/`: `rehber_metin.py`, `rehber_veri.py`, `rehber_sira.py`, `rehber_denetim.py`, `rehber_uret.py`,
  `rehber_giris.py`
- `rehber/`: `app.js`, `veri/rehber-veri.js`, `veri/rehber-veri.json` (`robot.glb` yeniden yazıldı, HEAD ile aynı bayt)
- `planlama/rehber/`: `Lale-montaj-rehberi.pdf`, `kontrol.json`, `goruntu/*` (FreeCAD'siz üretimden)
- `planlama/d158/`:
  - `F10d-gunluk.md`, `F10d-dogrula.py`, `F10d-dogrula.json`, `F10d-gizli-piksel.json`, `F10d-goruntu-*.png`;
  - `F10a-dogrula.json` (koşu sonucu);
  - `FREECAD-KILIT.txt` ("boş").

### 11.12 Kabul tablosu (son veri)

| ölçüt | sonuç |
| --- | --- |
| anlaşılmıyor 0 | 0 (önce 2) |
| zor kalanlar gerekçeli | 8, gerekçeli (11.10) |
| kendi karesinde görünmeyen yeni parça 0 | 0 / 335 (eşik ≥ 30 px ve ≥ %20) |
| ısıl gömme denetimi 0 hata | 0 (ağ denetimi; katı ataması ikinci tam üretimden 164 / 164) |
| masada yabancı kablo 0 | 0 |
| yazdırma tamamı | 100 / 100 (ana 50 + alt 50; önce 95 hedefti, alt adım 45 → 50) |
| uçuş istisnalarının hepsi ölçülmüş | 12 / 12 |
| taşınanlar listeli | 59 (11.1) |
| 1192 ↔ 1192 | 1192 parça (metin denetimi ve veri) |
| her parça tek ana adım ve tek alt adımda | evet / evet |
| ulaşılamaz 0, girilemez 0 | 0 / 0 |
| gezinme, panel = takma | 100 konum, 100 / 100 |
| F10d, F10a, F9b, çakışma, regresyon | beşi de geçti |
| PDF | 69 sayfa, en küçük yazı 8,1 pt |

### 11.13 Bellek kısıtı ve açık kalanlar

**Bellek kısıtı.** Kullanılabilir bellek 1–3,5 GB arasında gidip geldi. Neden çekirdek havuzu; düzelmesi için makinenin yeniden
başlatılması gerekir, karar Ahmet'te. FreeCAD kuralı ≥ 2 GB istediği için tam üretim yeniden koşulmadı.

FreeCAD'siz tamamlama şunları **kapsamıyor**: veri / ağ üretimi ve ısıl gömmenin katı ataması. Bunlar ikinci tam üretimin çıktısı.
Kesintiden etkilenmediği nasıl görüldü: veri ve GLB 15:34'te yazılmış, kesinti sonraki tarayıcı aşamasında. JSON tam okunuyor,
1192 parça var, tarayıcı ve sıra denetimleri bu veriyle geçti. Denetimi 11'in başında.

**Açık kalanlar:**
1. Bellek düzelince bayraksız tam üretim bir kez daha koşulabilir. Beklenen fark yok, aynı veri üretilmeli.
2. Zor kalan 8 alt adımın kamera / kadraj düzeltmesi (11.10).
3. Ölçülmeyenler:
   - etek ön iki bacaklı yolu (K1 önerisinin (c) seçeneği);
   - arka servis kapağı ↔ orta bant derinliği;
   - adım 41 "kaydırarak takılmaz" uyarısı.
4. F10d-K1 karar kuyruğuna yazılmadı (`karar-kuyrugu.md` dokunulmaz); metin 11.5'te.
