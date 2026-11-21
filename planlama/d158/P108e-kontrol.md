# P10.8e bağımsız kontrol (B ajanı: kontrol + kapanış)

B ajanı, 21.11.2026 (açılış ≈ 10:44, rapor 10:58; saat okundu). Dal `lale-duzeltme`, HEAD = origin = `269e51b`; A'nın işi çalışma
ağacında, commit yok. A'nın günlüğü (`P108e-gunluk.md`) okundu; "önce / sonra" ve "sonuç" satırları iddia sayıldı. Aşağıdaki sayılar
B'nin kendi koşularından ve kendi baktığı karelerden. FreeCAD açılmadı (kilit "boş" kaldı); rehber yeniden üretilmedi; kaynak ve
üretilmiş dosyalara dokunulmadı (B'nin koşularından önce ve sonra 396 + 21 kirli dosyanın md5'i birebir aynı). B'nin geçici betikleri ve
logları depo dışında kaldı.

**Karar: GEÇER**

Gerekçe: (1) Muafiyetlerin dördü de (iki `UC_ORTULU` kaydı, iki `GEO_YAN_ELLE` kaydı, `app.js` arama uzaklığı) gerekçesi kareye /
modele bakılarak doğrulandı ve dar: her biri tek alt adımda ya da tek kablonun tek yanında, kullanılmazsa ya da koşul bozulursa denetim
HATA veriyor (§ 2). (2) CAD geometrisi değişmedi: farkta FCStd / STEP yok, `tasarim/freecad/` altında değişen kaynak yalnız rehber
kaynakları, rehber şeması (`kablo_yolu_taban.py`, parça değil) ve kafa-yerleşim not üreticisi; `carpisma_kos.py kontrol` 0 (§ 3).
(3) A'nın zincir tur 2 sonuçları geçerli: tur 2 başlangıcından (09:47:01) sonra kaynak ya da rehber çıktısı değişmedi; B'nin koştuğu 17
hızlı denetimin hepsi A'nın değerini verdi (§ 4). (4) Kareler anlatılanı gösteriyor; değişen 289 karenin piksel farkı yalnız paketin
dokunduğu adımlarda (§ 5). Bulgular bilgi düzeyinde (§ 7), geçmez nedeni yok.

## 1. Kapsam

- Değişen izlenen dosyalar (eski kir hariç): rehber kaynakları `tasarim/freecad/rehber/{rehber_kablo, rehber_metin, rehber_veri,
  rehber_gorunum, rehber_denetim}.py` + `rehber_kritik_onay.json`, `rehber/app.js`, `tasarim/freecad/lale158/kablo_yolu_taban.py`,
  `kafa-yerlesim/{uygulama_metin.py, uygulama-notu.md, rapor.html}`, `planlama/adim3/kablolar.{json,md}`, `planlama/d158/F10l-birlesim.py`,
  `F10{a,d,e,f}-dogrula.json`, `planlama/dongu-158.md`, `tasarim/Robot-Tasarim-Demosu.html`, üretilmiş rehber (`rehber/veri/` 4 dosya,
  `rehber/goruntu/` 141, `planlama/rehber/goruntu/` 148, PDF, `kontrol.json`). İzlenmeyen yeni: `P108e-gunluk.md`, `P108e-onizleme.py`,
  `P108e-sema-girdi.py`, `P108e-sema-olcum.py`, `P108e-zincir.sh`, `P108e-olcum/` (76 dosya, 2,8 MB).
- 21 eski kir: 20'si A'nın başlangıç özetiyle (`P108e-olcum/kir-bas.md5`, 07:01) aynı (`md5sum -c` 20 / 20 OK); 19'u ayrıca 19.11 yedeğiyle
  (`lale-birlestirme-yedek/kir-yedek-md5.txt`) aynı (19 / 19 OK). `b2-tarama.nabiz` son değişme 06:29:30 (paketten önce),
  `FREECAD-KILIT.txt` `.git/info/exclude`'da, içerik "boş".
- Brief'teki "`demo_uret.py` (yeni betik)" doğru değil: betik P10.7b2g'den (`d542472`) beri depoda ve değişmedi; A yalnız koştu (günlük
  § 9 doğru yazıyor: "P10.8c'deki gibi").

## 2. Muafiyetler (her biri ayrı)

| Muafiyet | Gerekçe gerçek mi (B'nin bakışı) | Kapsam | Önce → sonra |
|---|---|---|---|
| `UC_ORTULU[("K2", 2)]` "Dağıtım kartı C (kafa)" = bu kadrajın dışında | **Evet.** 32.2 karesinin konum kutusu "orta · y 1210–1330" (iki kare de bakıldı); kartın kutusu y 187,5…199,1 (`taban-analiz.json`): ≈ 1.010 mm aşağıda. Aynı alt adımda "kafa tilt servosu" emsali. Basılı sayfa (PDF s. 49) "Uç karede görünmez: Dağıtım kartı C (kafa) (bu kadrajın dışında)" diyor | Tek alt adım, tek uç. F10d U6 kullanılmayan kaydı HATA sayar | F10d tur 1: 32.2'de U1 × 2 + U4 = 3 hata → 0; uç etiketi 60 → 59; 32.2'nin tek etiketi 2 → 1 numara (B'nin F10d `--yalniz-uc` koşusu) |
| `UC_ORTULU[("K2", 1)]` sağ S1 / sol S1 = bu kadrajın dışında (brief'te yok; A § 5) | **Evet.** 32.1'in yeni bakışı tabana arkadan-üstten; iki karede de omuz / kol yok, direk kadrajın üst kenarından çıkıyor. Metin ve PDF s. 48 bunu açıkça söylüyor ("omuz uçları kadrajın dışında") | Tek alt adım, iki uç; U6 korur | Bakış değişikliğinin sonucu (eski "arka" bakışında omuzlar karedeydi, bara çıkışı seçilmiyordu); etiketlenen: dağıtım kartı A (1), B (2) |
| `GEO_YAN_ELLE` {(6, S09, a), (6, S10, a)} | **Evet.** CAD yolu 6'nın kutusu y 1.212,5…1.327,5, x ±2,5 (`taban-analiz.json`): yalnız boyun → kafa; kart C y ≤ 199,1. Yol karta ≈ 1.013 mm yaklaşmıyor. S09 / S10'un a ucu kayıtta "Dağıtım kartı C (kafa)" (`kablolar.json`) | Anahtar (yol, kablo, yan): yalnız bu iki yan. Kod: yan yola ulaşırsa HATA ("kaydı kaldır"), kayıt kullanılmazsa HATA; bozma b107–b110 bunları yakalıyor (B'nin koşusu 118 / 118, veri kipinde 136 / 136). Onay kaydına girer (`GEO_YAN_ELLE 6 S09 a` / `S10 a`) | P10.8c'de aynı yanlar `MODELSIZ_KONUM` ile "elle bakıldı" idi: kapsam daralmadı. `rehber_kablo.py` 1 hata → 0, BİLGİ 2 satır ("yola ulaşmıyor, elle bakıldı") |
| `app.js` `ucCiz` uzaklık listesine 11 R, 14 R | **Evet.** Döngü ilk uyan yerde duruyor (kod okundu): ≤ 8,5 R'de yer bulan etiket değişmez. B'nin F10d `--yalniz-uc` koşusu (124 s, GECTI, 23 konum, 59 etiket, hata 0), A'nın değişiklik öncesi ölçümüyle (`zincir-tur1/uc-1.json`) karşılaştırıldı: 23 konum × 2 kipte fark yalnız B5a etkileşimli etiket 2 (önce çizilmiyordu; şimdi nokta (770; 307) → kutu (770; 167), 140 px) ve 32.2'nin numarası (yukarıda) | Yalnız yakında yer bulamayan etikete uygulanır; bugün tek etiket | B5a etkileşimli kipte "yer bulunamadı (çakışma)" → çiziliyor |

B5a etkileşimli etiketin görünüşü (A doğrulayamadı): F10d'nin durumu CDP ile yeniden kurulup ekran alındı (açık ve koyu tema, 1.400 ×
900). Etiket "Dağıtım kartı C (kafa)" sigorta kutusunun üst kenarında, ince dikey çizgi kartın üst yüzündeki noktaya iniyor; yazı
okunuyor, çizgi siyah kutunun üstünde de seçiliyor; XL4016 C etiketiyle çakışma yok. Koyu temada ad kutusu siyah kutuyla aynı tonda
(yazı okunur, kutunun kenarı zor seçilir; bilgi). Statik Chrome ekranında (`--virtual-time-budget`, üretimin `planlama/rehber/goruntu/
adim-12.png`'si de) kamera çerçevesi biraz farklı ve etiket kartın hemen yanında kısa çizgiyle duruyor: 140 px'lik yer yalnız F10d /
CDP çerçevesinde.

## 3. CAD geometrisi

- `git status`: FCStd / STEP değişikliği yok. `git diff --stat HEAD -- tasarim/freecad`: rehber kaynakları, `kablo_yolu_taban.py`,
  kafa-yerleşim (not, rapor, üretici) ve 14 eski kir dosyası; parça / montaj kaynağı (`*_parcalar.py`, `*_lib.py`, `arayuz.py`,
  `carpisma.py`) yok.
- `kablo_yolu_taban.py` parça değil: yalnız `rehber_kablo` / `rehber_veri` / `rehber_metin` okuyor (dosya başlığı "PARÇA DEĞİL"
  kalıbında; CAD tarafında içe aktaran yok). Tam taramanın izlediği 17 dosyada değil.
- `cd tasarim/freecad && py -3 -B -X utf8 carpisma_kos.py kontrol`: 10:45 ve 10:49 iki kez **0**, "izlenen 17 dosyanin ozetleri kayitla
  ayni". `20261121-023529` taraması geçerli.
- G07 / G16 ölçüm girdisi güncel: `P108e-olcum/sema-girdi-sonra.json`'un 16 şemasının noktaları bugünkü `rehber_kablo.sema_noktalari`
  ile aynı (en büyük fark < 0,001 mm; 16 / 16), `kablo_yolu_taban.py`'nin 07:08'deki son değişikliği yalnız yorum. Ölçüm logları
  önce / sonra: G07 eksen içinde 1 → 0, çizim içinde ara 4 → 0, en dar ara 0,0 → 4,0 (M5 somun, yıldız 1); G16 eksen içinde 1 → 0, ara 1 →
  0, en dar ara 0,0 → 5,5 (yıldız tutucusu). A'nın tablosuyla aynı.

## 4. Zincir geçerliliği ve B'nin koşuları

Tur 2'nin geçerliliği: `find -newermt "2026-11-21 09:47:00"` (depo, `.git` hariç) yalnız zincirin kendi çıktılarını (`F10{a,d,e,f}-dogrula.json`,
`F10d-gizli-piksel.json` (içerik HEAD ile aynı), `P108e-olcum/zincir/`, `zincir.durum`) ve tur 2'den sonra yazılan günlük (10:42:24), plan
(10:42:54), iki şema logu (`sema-once.log`, `sema-sonra.log`, 10:42:42; zincir girdisi değil) buldu. Son kaynak değişiklikleri
`rehber_metin.py` 09:04:24, `app.js` 09:04:16; ikinci üretim 09:04:40'ta başladı, 09:46:49'da bitti; demo 09:46:55. Zincir baştan koşulmadı.

B'nin koşuları (depo kökü, `py -3 -B -X utf8`, 10:45:47–10:49:13; hepsi çıkış 0):

| Komut | B | A (§ 7 / § 9 tur 2) |
|---|---|---|
| `carpisma_kos.py kontrol` (başta / sonda) | 0 / 0, 17 dosya aynı | aynı |
| `rehber_kablo.py` | GEÇER; uç etiketi 51 modelde / 6 modelsiz, hata 0; BİLGİ: yol 6 S09 a / S10 a "elle bakıldı (GEO_YAN_ELLE)" | GEÇER; 51 / 6 |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | GEÇER; veri uç etiketi 24 konum, hata 0; kırpma hata 0 | GEÇER |
| `rehber_kablo.py --bozma-denemesi` / `--veri …` | 118 / 118 / 136 / 136 | 118 / 118 / 136 / 136 |
| `rehber_denetim.py --kaynak` | ascii 0, elektrik 0, zorunlu eksik 0, yasak 0; onay farkı 0 (kablo 219, liste 258, metin 1201); CAD etiket / kod 975, eskime HATA 0 / bilgi 2 | aynı |
| `rehber_denetim.py` (veri) | ascii 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0; parça 1264, şema 65 | aynı |
| `rehber_denetim.py --bozma-denemesi` | 347 / 347 | 347 / 347 |
| `planlama/adim3/kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / 174 bozma, GEÇER | aynı |
| `planlama/d158/F10l-birlesim.py` | GECER; eski 1177 / yeni 1179 cümle, eklenen 13, silinen 11 (beklenen 13 / 11) | aynı |
| `tasarim/freecad/test/kupon_tazelik.py` / `--bozma-denemesi` | TAZE (16) / 4 / 4 | aynı |
| `planlama/d158/F4c-dogrula.py` | GECTI | GEÇTİ |
| `planlama/d158/F9b-dogrula.py` | GECER (hata 0); 1264 GLB düğümü, konsol 0 (1400 / 360 px) | GECER |
| `planlama/d158/regresyon.py --yazma` | GEÇER, kötüleşen yok (rampa 1,519 → 1,523 "iyileşti") | aynı |
| `F10d-dogrula.py --yalniz-uc <depo dışı JSON>` | GECTI: 23 konum, 59 etiket, karede görünmez uç 35, hata 0 | tur 2 F10d: 23 konum, 59, hata 0 |

Koşulmayanlar (tur 2'den geçerli sayıldı): F10f, F10e, F10d tam, F10d `--gizli`, F10a, rehber üretimi, `uygulama_rapor.py`, `demo_uret.py`.

## 5. Kareler (B dosyayı açıp baktı)

| Kare | Gördüğü |
|---|---|
| 17.11 (`rehber/goruntu/adim-17-11.png`, `planlama/rehber/goruntu/adim-17-11.png`) | Gri U06 çizgisi direk dibinden elektronik katına inip ESP32 taşıyıcısında bitiyor; etiketler 1 PCA9685, 2 Dağıtım kartı C (kafa) (kart ve burçları görünüyor), 3 ESP32, okunuyor, üst üste değil. Lejantta "Kablo: Hazır kablo: USB" ve "ESP32 USB (U06): yalnız taban bölümü (…); tamamı K2 madde 4'ün karesinde". Metin ("Karede vurgulu çizgi U06'nın taban bölümüdür") kareyle uyumlu |
| 32.1 (iki kare) | Arkadan-üstten taban: anahtarlı baranın 4 saplaması önde, sarı hat saplamadan çıkıp direğe gidiyor, etiket 1 dağıtım kartı A, 2 dağıtım kartı B (direğin iki yanında); konum "orta · y 100–1290". Etiket 1 işareti basılı karede direğin kenarına biniyor ama okunuyor. Omuz / kol karede yok |
| 32.2 (iki kare) | Boyun / kafa altı, sarı S09 / S10 hattı; tek etiket 1 kafa pan servosu; kart C etiketi yok (doğru, kadraj dışı) |
| B5a (adım 12; basılı, üretim etkileşimli, B'nin statik ve CDP ekranları) | Etiket 1 XL4016 C, 2 Dağıtım kartı C (dört burçlu küçük mavi kutu, XL4016 C'nin arkasında, kırmızı kutunun yanında). Sarı SV3 ikisinin arasında |
| Acil stop düğüm kartı, B5a | Karede görünüyor ama **etiketsiz**: sol tarafta siyah röle kutusu ile büyük yeşil ön şarj kartı arasındaki küçük yeşil kart (dört burç). Yeri `taban-analiz.json` ile tutuyor (düğüm z −105…−75; ön şarj −26…24; x ikisinde de −133…−62 aralığında). Metindeki "röle K1 ile ön şarj kartının arasında" tarifiyle seçilebilir; karede adı yazmıyor (B5a'da etiket yalnız kablo uçlarına; bu kart SV3'ün ucu değil) |
| 17.10 (basılı + B'nin etkileşimli ekranı) | Mor sinyal hatları, 8 etiket okunuyor. Kat yarı saydam, tepeden bakış: Kablo yolu 11 / 12 ile şemalar aynı renkte ve kesiğin kenarı karede seçilmiyor. "Yol 11 / 12 kesikten geçer" **kareden doğrulanamadı**; dayanağı P10.8d'nin B-rep ölçümü (P108d-kontrol § 2: yol 11 tüp × kat 3,95 mm, kesiğin içinden; yol 12 rehber bölümü ortak hacim 0) ve CAD o günden beri aynı (§ 3) |
| 13 (B5), 33.1 / 33.2 (F1) | Piksel farkı yalnız güç paneli bölgesinde: yeni kartlar (13'te kart C burçlarıyla) |

Değişen kare sayısı: 289 PNG'nin (141 + 148) hepsinin baytı değişti; HEAD ile piksel karşılaştırması (kanal farkı > 24): **190 kare
piksel piksel aynı** (yalnız kodlama), 27 karede 1–5 piksel (gürültü), 36 karede 6–1.613 piksel (bütün robotun ya da tabanın göründüğü
sonraki adımlar: 00, 17.12, 18, 31.5, 32.x, 33.x, 34.x, 49.2, iki telefon karesi), **36 karede ≥ 2.000 piksel** (iki klasörde aynı 18 kare:
12, 13, 15, 17, 17.1–17.11, 32.1, 33.1, 33.2). Büyük farkların hepsi paketin dokunduğu yerlerde (yeni kartlar, G07 / G16, 17.11, 32.1);
beklenmedik değişen kare yok.

## 6. Yeni kod ve metin

- **`sema_on` (adım ötesi şema).** `rehber_veri.py`: desen tam bir şemaya uymalı, şema sonraki adımın olmalı, y ≤ sınır noktaları bir uçta
  bitişik ve ≥ 2; uymazsa üretim durur. Veride yalnız K1 alt adım 11 (U06). `app.js`: `tupGeo` eski `semaKur` kodunun birebir taşınması
  (davranış aynı), `ON_OBJ` yalnız `sema_on` olan alt adımda görünür, öbür adımlarda gizli; `userData.d = "on"` F10d `sema_karede`
  sayımına girmiyor. `rehber_gorunum.uc_isle`: `sema_on` kabloları uç etiketi kümesine. Yan etki: 190 kare piksel olarak aynı, değişen
  kareler yukarıda; F10d / F10e / F10f / F10a tur 2'de geçti.
- **`uygulama_metin.py`**: fark < 1 g ise "koşu güncel montajla aynı kütleyi veriyor … bu montajla hesaplandı", karar listesinde
  `uygulama_ivme` sorusu yok. Notun farkı: 1,519 → 1,523 (4 yer), elde 1,483 / 1,333, fren 1,751, kütle 26.276,1 g, parça 1.251, koşu
  `20261121-023529`, fark 0,0 g; notun "Seçim:" satırındaki kişi adı HEAD'de de var (yalnız tarih değişti).
- **Demo** (`git diff --word-diff`): yalnız gömülü sayılar (kütle 25,84 → 25,88 kg, 25.835,06 → 25.876,13 g, AM y 526,7 → 526,2, parça
  1.225 → 1.251, satın alınan 210 → 220, GLB düğümü 1.238 → 1.264, taban 388 → 414 parça / 8,23 → 8,27 kg) ve kaynak blokundaki özetler.
- **Yeni betikler**: `P108e-onizleme.py` (rehber kopyası sistemin geçici klasöründe, yalnız `P108e-olcum/onizleme/` PNG yazar),
  `P108e-sema-girdi.py` (düz Python, yalnız `sema-girdi-<etiket>.json`), `P108e-sema-olcum.py` (FreeCAD'de FCStd'yi açar, kaydetmez,
  yalnız `sema-<etiket>.json`), `P108e-zincir.sh` (zincir; regresyon `--yazma`). Depo kaynağına yazan yok.
- **Onay kaydının 25 farkı** (`rehber_kritik_onay.json`) tek tek okundu: kablo −7 / +6 (MODELSIZ_KONUM, PARCA_CAD MODELSIZ, SEMA_KONUM,
  UC_MODELSIZ kalktı; PARCA_CAD / UC_ETIKET desenleri, iki GEO_YAN_ELLE geldi), liste 1 (ZORUNLU 17.10), metin −11 / +13. Yeni metinlerin
  yer iddiaları `taban-analiz.json` ile tutuyor: kart C x 94…130, z −92…−62, XL4016 C z −23,5…23,5 → "XL4016 C'nin arka yanında" (−z);
  `DAGITIM_C` z −60, kartın +z kenarı −62 → "şema kartın ön (+z) kenarının yanında biter"; düğüm kartı z −105…−75 ön şarj (−26…24) ile
  röle arasında, x ön şarjla aynı yan.
- **Dil**: yeni / değişen cümlelerin hepsi tam Türkçe karakterli (ASCII kalıntı 0, B'nin `--kaynak` ve veri koşusu), düz. Ölçülmemiş değer
  ölçülmüş gibi yazılmamış: kart ölçüsü ve zarfı "TAHMİN: kart yapılınca ölçülecek", K1 17.8 / K1 kablo / SV3 adında "zarfı TAHMİN".

## 7. Bulgular (hepsi bilgi; geçmez nedeni değil)

- **B1:** B5a'daki "dörder M3×8 naylon burçla (üstte M3×6, altta M3×8 vida)" modelin seçimi (ön şarj kartıyla aynı takım, P10.8d), ölçü
  değil; cümle TAHMİN demiyor. Üst vidanın boyu kart kalınlığına bağlı ve kart kalınlığı TAHMİN; "ölçüsü TAHMİN" cümlesi bunu dolaylı
  kapsıyor. Kart gelince vida boyu da kartla birlikte teyit edilmeli (A'nın "doğrulanmayanlar" satırında zaten var).
- **B2:** Acil stop düğüm kartı B5a karesinde etiketsiz; yalnız metindeki yer tarifiyle seçiliyor (§ 5). Kuyruk için öneri: B5a'ya
  `odak` / ad etiketi (rehber aracı işi, karar değil).
- **B3:** 17.10'da "yol 11 / 12 de kesikten geçer" cümlesi kareyle değil P10.8d'nin B-rep ölçümüyle dayanaklı; kare (tepeden, aynı mor
  renk) kesiği göstermiyor.
- **B4:** B5a etkileşimli etiketin yeri tarayıcı çerçevesine göre değişiyor: F10d / CDP çerçevesinde 140 px yukarıda, statik ekranda
  kartın yanında. İkisinde de okunur; koyu temada ad kutusu siyah sigorta kutusunun üstünde düşük karşıtlıklı.
- **B5:** `kablolar.json` S09 / S10 `boy_tahmin` hâlâ "dağıtım kartı C → XL4016 C vekil" ile hesaplı (kart artık modelde). Boy kuralı
  kablolar paketinin işi; bu pakette değişmedi.

## 8. CAD paketine devredilenler (açık)

- **CAD kablo yolu 6 kart C'ye inmiyor** (`taban_parcalar.py` YOL[5]: (0; 1215; −26) → (0; 1290; −30) → (0; 1325; −10); kart C x 94…130,
  y 187,5…199,1, z −92…−62). Yol çizilince `GEO_YAN_ELLE` iki kaydı "yan yola ulaşıyor" HATA'sıyla kendini gösterir, kaldırılır.
- P10.8d'den süren (değişmedi): acil stop düğüm kartı ve dağıtım kartı C'nin gerçek ölçüsü / zarfı / kütlesi ve burç / vida boyu (kart
  yapılınca); göğüs regülatörü kartı (K52), K31 insert boyu, `TABAN_DISI_BOLGE` (bu pakette değildi).

## 9. Bakılmayanlar / doğrulanamayanlar

- Uzun zincir adımları (F10f, F10e, F10d tam, F10a) ve rehber üretimi B tarafından koşulmadı (tur 2 geçerli, § 4).
- 17.10'da yol 11 / 12'nin kesikten geçtiği kareden doğrulanamadı (§ 5).
- Kart zarfları, burç / vida boyları TAHMİN (kart yok).
- `--kritik-onay-yenile`'nin ürettiği 25 farkın dışında onay kaydı mantığı yeniden incelenmedi.
