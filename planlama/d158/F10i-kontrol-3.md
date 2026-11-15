**SON TUR GEÇER**

# F10i kontrol 3 · P10.7b2a düzeltme turu 2'ye dar bakış (kaynak düzeyi)

15.11, 03:22–03:35. Dal `lale-duzeltme`, HEAD `1328b60`, değişiklikler commit edilmemiş çalışma ağacında. Kapsam yalnız
`F10i-gunluk.md` "Düzeltme turu 2" (12 madde) ile değişenler. FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları, başsız tarayıcı ve
`rehber_kol_kablo.py --yazma` koşmadı. Denetimler ve bozmalar depo dışındaki geçici bir kopyada koştu (`kablolar_denetim.py`
yalnız okuyan bir betik olduğu için depoda da koştu). Kaynak dosyalara dokunulmadı; depoda yazılan tek dosya bu rapor.

Montajda zarar verecek bir yanlış ya da eksik talimat, kayıtta yanlış değer, üretimi kıracak bir kod hatası ya da gizlilik sorunu
bulunmadı. Aşağıdaki bulguların hepsi kayıtlı açık iş sınıfında.

## 1. Talimatlar (çözülmüş metin `rehber_metin` içe aktarılarak okundu; `COZUM_HATA` boş, metinde `{…}` / `⟦?⟧` kalmadı)

| Konu | Sonuç | Nasıl ölçüldü |
|---|---|---|
| AU3 kafa ucu (`rehber_metin.py:825-826`) | Doğru: "+ damarını L+ ucuna, − damarını L− ucuna"; kayıtta `AU3` damarları `PAM8403 · L+ / L−` | Çözülmüş metin ↔ `kablolar.json` AU3 |
| AU3 gövde ucu (`:1007-1009`, `:1079-1080`) | Doğru: "kutbu L+ → +, L− → −: + damarını hoparlörün + ucuna, − damarını − ucuna"; işaret kablajda teyit | Aynı |
| H02 / G21 (`:1105-1106`) | Doğru: enerjisizken, ölçümden ve akü ayrıldıktan sonra takılıyor | Okuma |
| AU3 enerji durumu | K2 "enerjisiz çalış, F3 takılı değil"; F2'de F3 hâlâ takılı değil (F1 aşama 1 listesi): PAM8403 lehim sırasında beslemesiz | K2, F1 kontrol, F3 |
| G07 sırası (`:325-330`) | Uygulanabilir: kılıf çıkar → makaron tele → direnç tele lehim → bacak kovana sık → kovana lehim → soğuyunca makaronu çek ve büz. Direnç iki kez lehimlenmiyor (bir bacak tele, öbür bacak kovana); cümleler çelişmiyor; K1 kontrolü (`:439-442`) ve kayıt (`G07 uc_kuyrugu.a.ne`, `sonlandirma`, `R-aku-olcum.yer`) aynı sırayı söylüyor | Okuma, kayıt |
| F1 aralık dışı okuma (`:918-923`) | Güvenli ve anlaşılır. Çözülmüş metin "Okuma 1,95–2,20 V aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır …" (100 kΩ / 18 kΩ, oran 0,1525, akü 12,8–14,4 V). ESP32'yi F4 besler, F4 ana anahtardan sonra geldiği için "ana anahtarı yeniden açma" yasağı ESP32'yi de kapsıyor | Çözülmüş metin, F1 aşama 1 listesi |
| P01–P03 (`:282-285`, `:450-452`) | Doğru (servoların beslemesi aşağıda). Kayıttaki P01 / P02 / P03 `not` ile P03 `sonlandirma` ("yalnız sinyal teli … tek telli dişi uç") rehberle uyumlu; P03'te "3 pinli köprü" kalmamış | Kayıt |
| TVS (`:606-607`, `:637`) | Doğru: "sonu yalnız A (ör. P6KE18A) tek yönlüdür … sonu CA (ör. P6KE18CA) çift yönlüdür"; kayıtta `tvs[*].isaret` ve `teyit` aynı | Okuma |
| K2 pim okuması (`:351`) | "COM ile NC arası öter, COM ile NO arası ötmez": bobin boştayken doğru; kayıtta `K2-kontak.uclar` COM / NO / NC; K1 kontrolü (`:443-445`) uyumlu | Çözülmüş metin |
| A06 + ucu (`:378`) | "acil stop düğümü (mantar NC çıkışı) noktasına, yani acil stop düğüm kartında …": kayıtla aynı | Çözülmüş metin |

**Servolar beslemeyi nereden alıyor:** dağıtım kartlarından. XL4016 A → SV1 → dağıtım kartı A (sağ kol S01–S04), XL4016 B → SV2 → B
(sol kol S05–S08), XL4016 C → SV3 → C (kafa S09 / S10); servo uzatmaları kartın 3 pinli çıkışlarına takılıyor (kayıtta S09 / S10
V+ damarı `Dağıtım kartı C · pan / tilt V+`). PCA9685'in V+ hattı hiçbir servoyu beslemiyor (`parca_beslemesi` PCA9685: 3v3). P01–P03'te
V+ damarını kesmek servoyu beslemesiz bırakmıyor, yalnız üç XL4016 çıkışının PCA9685'in ortak V+ rayı üstünden birbirine paralel
bağlanmasını önlüyor. Sinyalin dönüş yolu ortak toprak (XL4016'nın giriş ve çıkış eksisi ortak, yıldız barasında).

## 2. Onay kaydı farkı (günlük D2.6, 35 girdi; hepsi okundu)

İstenmeyen kritik değer değişimi yok. Silinen bir uyarı yok: F1 kontrolde "ana anahtarı kapat, devam etme" çıkmış, yerine daha geniş
iki cümle girmiş (girdi 21–23). Değişen ZORUNLU / ZORUNLU_ALAN girdileri (7, 8, 10, 11) eski korumayı daraltmıyor, yenisi eskisini
kapsıyor. K52, K60, K61 metinlerine dokunulmamış. Tur 1'in G22 ve X01 metinleri listede yok (değişmemiş); P01–P03'te yalnız ölçü
noktası değişmiş. Temiz kaynakta `onayli kritik girdi farki 0 (kablo 94, liste 180, metin 991)`.

## 3. Koruyucu kurallar: kendi bozmalarım (geçici kopyada; her denemeden sonra geri yüklendi, son temiz koşu çıkış 0)

| Kural | Bozma (ajanınkinden farklı) | Sonuç |
|---|---|---|
| B16 | F1 alt adımına ek cümle: "Sonra A01 ile A02'yi mantarın NC girişinde birleştirip bağla" | Yakalandı (yasak 1 + onay farkı 1) |
| B16 | F1 iş metnine ek: "Mantarın iki ucunu tek kontak vidasına sık" | **Yalnız onay kaydı yakaladı** (yasak 0): açık iş A1 |
| B18 | Metne ek: "A06'nın + ucunu sigorta kutusunun F5 girişine de bağla" | Yakalandı (zorunlu 1 + onay 1) |
| B18 | Kayıtta A06 + damarı `Sigorta kutusu (F5 çıkışı) · +` | `rehber_denetim` 0 (kayda güvenir), `kablolar_denetim` 1 (düğüm yok, koruma, zincir): yakalandı |
| B23 | Yer tutucular yerinde, "öter" ↔ "ötmez" yer değişti | Yakalandı (zorunlu 1 + onay 1) |
| B23 | Kayıtta `K2-kontak.uclar` NO ↔ NC | `kablolar_denetim` 1 (karar G10 → COM, NO → direnç): yakalandı |
| B27 | Üst direnç 100 → 68 kΩ; satırdaki gerilimler ve `akim_a` tutarlı güncellendi | `kablolar_denetim` 1 GÜVENLİK (3,06 V > 2,45 V), `rehber_denetim` 1 (çözülemeyen yer tutucu 5): yakalandı |
| B27 | Alt direnç 18 → 22 kΩ, gerilimler eski | İkisi de yakaladı (2,63 V GÜVENLİK, gerilim çiftleri tutmuyor) |
| R5 | F1 madde 4'te `{ohm.aku_olcum}` → "100 kΩ" | Yakalandı (çıplak 1) |
| R5 | F1 kontrolde `{v.aku_olcum}` → "1,95–2,20 V" (cümle başında) | **Yalnız onay kaydı yakaladı** (çıplak 0): açık iş A2 |
| Ok kuralı | E3a "D24V50F5 → Pi USB-C (K03 …)" okunu "ve" yaptım | Yakalandı: 73 / 74, eksik K03. Ok kuralı gerçek talimatı hâlâ sayıyor; 74 / 74 gerçek |
| Ok kuralı | Aynı cümleye "; 2 tel" eklendi (talimat gerçek) | K03 sayılmadı (73 / 74): yanlış alarm yönünde, sessiz geçiş değil. Açık iş A3 |
| G07 | Kılıf çıkarma lehimden sonraya taşındı | Yakalandı (zorunlu 1 + onay 2) |
| AU3 | Kayıtta hoparlör + / − ters | `kablolar_denetim` 1 (ağlar tutmuyor): yakalandı |

Temiz kaynakta yanlış alarm 0 (bütün denetimler çıkış 0).

## 4. Koşular (çıkış kodu)

| Komut | Çıkış | Not |
|---|---|---|
| `kablolar_uret.py --kontrol` (kopya) | 0 | güncel |
| `kablolar_denetim.py` (depo, salt okuma) | 0 | SONUÇ: GEÇER |
| `kablolar_denetim.py --bozma-denemesi` (depo, salt okuma) | 0 | 167 YAKALADI / 167 (`b_koruyucu_8`, `_9`, `_10` dahil) |
| `rehber_denetim.py --kaynak` (kopya) | 0 | hepsi 0; tamlık 172 öğe, eksik 0; kablo talimatta 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` (kopya) | 0 | 185 / 185; bozulmamış kaynakta hata 0 |
| `rehber_kablo.py` (kopya) | 0 | GEÇER; onay kaydı (kablo) tutuyor |
| `rehber_kablo.py --bozma-denemesi` (kopya) | 0 | 36 / 36 |
| `py_compile` (6 dosya, çıktı depo dışına) | 0 | `rehber_deger`, `rehber_denetim`, `rehber_metin`, `rehber_kablo`, `kablolar_denetim`, `kablolar_uret` |
| `node --check rehber/app.js` | 0 | |

## 5. Sınırlar ve gizlilik

- `kablolar.json` (`1328b60` ile): 74 kablonun hepsinde `kesit`, `koruma`, `uc_a`, `uc_b`, damar uçları ve PCA kanalları aynı.
  Koruyucularda yalnız `yer`, anahtarlarda `uclar` / `saplama` alanları değişmiş; `tvs` ve `kondansatorler` paketin eklediği bölümler.
  Akım, direnç (`R-aku-olcum.ad`, `akim_a`) ve sigorta değerleri aynı.
- `pin-haritasi.md`, `elektrik.md`, `planlama/maliyet.json`, `kod/`: `1328b60`'a göre fark yok. `F10i-kontrol.md` ve
  `F10i-kontrol-2.md` turdan önce yazılmış (02:59), sonra dokunulmamış.
- `1328b60`'a göre eklenen 2.781 satırda yerel yol, makine adı, takma ad, e-posta, parola / anahtar kalıbı yok ("Echo" yalnız
  HC-SR04'ün pin adı). Kişi adı olarak yalnız "Ahmet" ve "Efe" geçiyor.
- PC817 jumper: `elektrik.md:241` yalnız "jumper'la yüksek/düşük seçiliyor" diyor, konum yazmıyor; öbür iki kayıt anmıyor. Talimatın
  yazılmaması doğru; `karar-kuyrugu.md:1448` açık işi var.

## 6. Kayıtlı açık işler (montajda zarar yok)

- **A1 · B16 yasak kalıbı** (`rehber_denetim.py:481-490`): ilk desen "mantar … iki ucu … tek **kontak** vidası" biçimini tutmuyor
  ("kontak" yalnız A01 / A02 deseninde var). Bu bozmayı onay kaydı yakalıyor. Öneri: ilk desenin isim listesine `kontak` ekle.
- **A2 · R5 cümle başı**: "Okuma 1,95–2,20 V aralığının altında …" gibi bağlam sözcüğü sayıdan sonra gelen çıplak gerilim, sayıdan
  önceki pencerede bağlam olmadığı için kaçıyor (`:1189-1190`, sonrası yalnız 20 karakter). Onay kaydı yakalıyor. Öneri: gerilim
  kuralında sonraki pencereyi de genişlet ya da "aralığ" sözcüğünü bağlama al.
- **A3 · TALIMAT_LISTE** (`:1290`): "N tel / kablo" geçen gerçek bir "A → B" talimatı artık sayılmıyor. Sonucu yanlış alarm (eksik),
  sessiz geçiş değil; bugün böyle bir cümle yok (74 / 74).
- **A4 · K2 madde 5 cümle sırası** (`rehber_metin.py:823-826`): "Kafa ucunda bağla …, sonra dikişleri sık." cümlesinden **sonra**
  "Hoparlör kablosunun (AU3) kafa ucunu … lehimle" geliyor. Kelimesi kelimesine izleyen biri dikişleri sıkıp kafayı yeniden açmak
  zorunda kalabilir (9 cıvata). Öneri: AU3 cümlesini "sonra dikişleri sık"tan önceye al.
- **A5 · G07 makaronunun yeri** (`:326-328`): makaron tele geçtikten sonra direnç telin ucuna lehimleniyor. Makaronun lehim yerinden
  uzağa itileceği yazmıyor; yakında kalırsa ısıdan erken büzülür ve yeniden yapmak gerekir. Öneri: "makaronu lehim yerinden
  uzağa, telin geri tarafına it".
- **A6 · F1 aralık dışı ölçütü**: aralık akünün 12,8–14,4 V olduğunu varsayıyor; akü bu aralığın dışındaysa sağlam bölücü de
  "aralık dışı" okunur. Talimatın sonucu temkinli (durup bölücüye bakmak); parantez bunu açıklıyor. Öneri: aynı anda akü
  uçlarındaki gerilimi de oku.
- **A7 · Cümle bölücü "ör."de bölüyor** (`_CUMLE_GENIS`, `:357`): TVS cümlesi onay kaydında üç parçaya ayrılmış (D2.6 girdi 17–19).
  Koruma bozulmuyor (ZORUNLU tüm alana bakıyor); kayıt okunurluğu düşüyor.
- **Bilgi, tur dışı:** F1 ölçümünde bölücünün orta noktası ESP32'ye zaten bağlı. Alt direnç eksikse ADC pini akü gerilimini 100 kΩ
  üzerinden görür (≈ 0,13 mA). Akımı üst direnç sınırlıyor; tasarım kararı, bu turun değişikliği değil.

## 7. Bakılmadı

Üretim çıktıları (`rehber/veri`, `rehber/goruntu`, `planlama/rehber`) ve rehberin tarayıcıdaki görünümü; `rehber_kol_kablo.py
--yazma`; onay kaydı JSON'unun tur 1 hâliyle bayt bayt farkı (tur 1 commit edilmemiş; günlükteki 35 girdi ve temiz koşudaki
"kritik fark 0" ile bakıldı); PAM8403 modülünün ve hoparlörün gerçek uç etiketleri (elde parça yok, kayıtta kablajda teyit).
