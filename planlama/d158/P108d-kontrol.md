# P10.8d bağımsız kontrol (B ajanı: kontrol + tam çakışma taraması + regresyon)

B ajanı, 20.11.2026 (açılış 11:42; tam tarama 12:44'te Windows Update yeniden başlatmasıyla kesildi); **B2 ajanı** 21.11.2026
(açılış 02:30, bitiş 06:35; saat okundu) kontrolü bitirdi: § 1, § 2, § 3.1'in 12:02'ye kadarki satırları ve § 5 B'nin, geri kalanı
B2'nin. Dal `lale-duzeltme`, HEAD `1fbe337`; A'nın işi çalışma ağacında, commit yok. A'nın günlüğü (`P108d-gunluk.md`) okundu; § 1'deki
hedefler ölçüt, "sonuç" satırları iddia sayıldı. Sayıların hepsi B / B2'nin kendi koşularından; A'nın betikleri koşulmadı. B'nin
ölçüm betikleri ve çıktıları geçici klasörden `planlama/d158/P108d-kontrol-olcum/`'a kurtarıldı (B2'ninkiler de orada). Kaynak
dosyaya ve rehbere dokunulmadı, commit / push yok.

**Karar: GEÇER**

Gerekçe: (1) Yedi maddenin hedefleri B'nin bağımsız ölçümüyle sağlanıyor (§ 2; tek sapma bulgu B1, yolun kendi ucunda, ortak hacim 0,
geçmez nedeni değil, § 4). (2) Tam çakışma taraması tek koşu kimliğiyle (`20261121-023529`) 9 / 9 bölüm baştan sona koştu, hepsi
rc 0, istisna 0, aynı kaynak özeti; `birlestir()` `tek_kosu: true`; sonuç bölüm bölüm HEAD'deki 19.11 koşusuyla **aynı**: toplam 364,
eklem aralığında **0**, ev pozu çakışması **0**, taban taraması 0 (§ 3.2). (3) `carpisma_kos.py kontrol` **0**, `regresyon.py --yazma`
**0, GEÇER, kötüleşen yok** (rampa 1,519 → 1,523; § 3.3). (4) B'nin 20.11 zincir sonuçları (taban / ana montaj / boy / kafa-yerleşim /
ivme) hâlâ geçerli: 12:02'den sonra kaynak ya da üretilmiş dosya değişmedi (§ 3.1 notu). Açık kalanlar rehber tarafında ve bilinen
(§ 5, P10.8e'ye devir): `sema_geometri_denetle` 1 hata, `--kaynak` ascii kalıntı 5; bunlar CAD paketinin geçme ölçütü değil, A'nın
§ 9 risk listesinde ve devir listesinde.

## 1. Başlangıç ve kapsam

- 11:44: çalışan FreeCAD yok, `FREECAD-KILIT.txt` "boş", boş bellek ≈ 4,0 GB.
- `git diff --stat` (HEAD'e göre): kaynak olarak yalnız `tasarim/freecad/taban/taban_parcalar.py` (+64 / −7, `--numstat` ile).
  Üretilmiş: `taban-analiz.json`, `taban-bom.csv`, `taban-montaj.FCStd`, `taban-montaj.step`, `dxf/guc-paneli-arka-5mm-kontrplak.dxf`.
  İzlenmeyen: `planlama/d158/P108d-*` (günlük, 5 betik, `P108d-olcum/` 7 JSON). `planlama/dongu-158.md` değişikliği orkestratörün
  (kilit satırı + § 5 iki satır).
- Kapsam dışı dosyalar: `git diff HEAD -- tasarim/freecad/arayuz.py tasarim/freecad/rehber planlama/d158/karar-kuyrugu.md
  tasarim/freecad/lale158 planlama/adim3 planlama/maliyet.json` **boş** (B'nin koşularından önce). `taban_lib.py`, `kablolar.json`
  dokunulmamış (md5 tarama kaydındakiyle aynı).
- 19 eski kir (13 kabuk PNG'si, `montaj/yerlesim-kontrol.json`, kökte `geometri_cikar.py`, `geometri2_cikar.py`,
  `geometri2_dogrula.py`, `gez.js`, `uc.js`): md5'leri başta ve sonda 19.11 yedeğiyle (`lale-birlestirme-yedek/kir-yedek-md5.txt`)
  **birebir aynı**. A da B de bunları yeniden yazmadı.
- Yol 1'in yeniden çizilmesi (brief'te yoktu): eski çapraz bölüm (88; 199; −60) → (112; 192; −100), y 192…199'da kart C'nin yerinden
  (x 94…130, z −92…−62, zarf üstü y 199,1) geçiyordu; kart orada kalacaksa gerekliydi. Bozduğu bir şey bulunmadı: yol 1'in temas
  listesi HEAD ile aynı dört uç parça (akü, ana anahtar, ana sigorta yuvası, sigorta kutusu; yalnız yuvanın içindeki tüp hacmi
  1.247 → 1.364 mm³, uç), 3 mm içinde yabancı parça yok, rehber `bara_yol_denetle` / `geometri_denetle` hata 0. Yol 2…9'un tüp
  hacmi HEAD ile birebir aynı (geometri değişmedi).

## 2. Madde başına ölçüm (A'nın sayısı ↔ B'nin sayısı)

Yöntem (A'dan farklı): taban parçaları üretilmiş `taban-montaj.FCStd`'den (B'nin yeniden ürettiği; A'nınkiyle aynı, § 4), öbür
modüller `montaj/robot-montaj.FCStd`'den; HEAD için `git show HEAD:…/taban-montaj.FCStd`. **İzin listesi kullanılmadı**: her tüp ×
her gerçek parça için 3 mm içindeki her parça ve temasta `common().Volume` listelendi, sınıflama elle. Oturma: burç taban yüzü / vida
başı üst yüzü ile panel yüzünün `Face.common` alanı (A dilim hacmiyle ölçtü). Şema noktaları `rehber_kablo.sema_noktalari`'ndan
B'nin kendi betiğiyle yeniden alındı (A'nın `sema-girdi.json`'u ile en büyük fark 3,5·10⁻⁵ mm, yuvarlama).

| # | Ölçüt (hedef) | A | B | Sonuç |
|---|---|---|---|---|
| 1 | Yol 10 × ön şarj kartı, önce | 0,354 mm³ | 0,354 mm³ | aynı |
| 1 | Yol 10 sonra: yabancıya en dar (≥ 1,0), ortak hacim (0) | 2,90 / 0 | **2,90** (ön şarj kartı) / 0; temaslar yalnız yolun kendi parçaları (sigorta kutusu, röle, acil stop kontağı, düğüm kartı, arayüz kartı) | ✅ |
| 2 | Yol 11 önce (yabancı ortak hacim) | 871,6 | 871,6 (alt plaka 158,3 + kat 265,4 + ara ray 419,6 + ESP32 taşıyıcı vida 28,3) | aynı |
| 2 | Yol 11 sonra: ortak hacim / en dar yabancı | 0 / 1,95 (etek ön sol) | 0 / **0,50 mm sonar tutucu sol** (A'nın izin listesinde `^Sonar`), sonra 1,954 etek ön sol, 2,50 ara ray | ✅ / **bulgu B1** |
| 2 | Yol 11 kat / alt plaka geçişi | kesikte, kata 3,95 | tüp × kat 3,952 mm, × alt plaka 30,38 mm (temas yok: kesiğin içinden, kenara ≥ 6,45 mm eksen) | ✅ |
| 2 | Yol 12 rehber bölümü (noktalar 0..2) önce | 522,1 | 522,1 (kat 464,5; burç 43,0; vida alt 13,1; vida üst 1,6) | aynı |
| 2 | Yol 12 rehber bölümü sonra: ortak hacim / en dar | 0 / 2,46 (taşıyıcı vida 1 üst) | 0 / **2,458**; PCA9685 3,317; kat 5,632; temas yalnız uç (ESP32 taşıyıcı, DevKit). BTS7960 sol (baş ucu) 1,793 | ✅ |
| 2 | Yol 12 `CAD_KIRP` | geçerli | `cad_kirp_denetle`: "yol 12 y ≤ 192,5; hata 0" | ✅ |
| 2 | Yol 12 tam yol (bilgi, kapsam dışı) | 2.825,4 → 2.303,3 | 2.825,4 → 2.303,3 (boyun plakası, pan servosu, servo yuvası, VESA taşıyıcı) | aynı |
| 3 | Burç 2 oturma (hedef = engelsiz burç) | 0,391 → 0,895 | yüz alanı 7,484 → **17,118** / 19,129 mm² (0,391 → 0,895; engelsiz burç 0 ile aynı) | ✅ |
| 3 | Burç 2 alt vida başı | 0,264 → 0,618 | panelde desteklenen 6,280 → **14,679** mm² (engelsiz vida 0 ile aynı; oran B'nin paydasıyla 0,376 → 0,880, A'nınkiyle 0,264 → 0,618) | ✅ |
| 3 | Burç 1 / 3 (K53 çentiği) | 0,817 | 0,817; vida 0,815 | değişmedi |
| 4–5 | Yeni burçlar / alt vida başları | 0,895 / 0,618 | 8 / 8 burç 17,118 mm² (0,895), 8 / 8 vida 14,679 mm² | ✅ |
| 4 | Düğüm kartı zarfı | x −133…−103, z −105…−75, y 187,5…199,1 | aynı (bb); 10 mm içinde yalnız güç paneli (8,0); grup (burç / vida) × başka parça 3 mm içinde yok | ✅ |
| 4 | Düğüm kartı × kablo yolları (kendi yolu hariç) | yol 3'e 9,65; yol 10'a ≥ 7,29 | yol 3 9,648; yol 10 (kendi) 0 / 7,291 | ✅ |
| 5 | Kart C zarfı | x 94…130, z −92…−62 | aynı; 10 mm içinde ana sigorta yuvası 8,0, panel 8,0 | ✅ |
| 5 | Kart C × yol 1 | 6,01 (kart), vida 6,31 | 6,009 / 6,309 | ✅ |
| 5 | Kart C alt vida başı × akü kayışı (≥ 1,0) | 1,25 | **1,25** (vida 0), 2,25 (vida 1) | ✅ |
| 5 | DAGITIM_C (100; 192; −60) → kart C (≤ 5) | 3,0 | 3,000 | ✅ |
| 4–5 | M5 kat cıvatalarının üstü | açık | kart / burç / vida kutusu × M5x12 (±115; −40) xz örtüşme yok; en yakın 30,8 (düğüm) / 17,9 mm (kart C) | ✅ |
| 4–5 | TAHMİN işareti | – | parça adlarında "nominal zarf TAHMIN", BOM satırlarında "(TAHMIN)", kaynakta `ESD` / `DGC` yorumu "nominal zarf TAHMIN", "Olcu ve kutle TAHMIN" | ✅ |
| – | `taban_montaj` | 414 parça, bağlantı 148 / 148, iç / × iskelet / × kabuk 0 | 414 (13 Referans), çift 708, geçersiz 0, iç çakışma 0, bağlantı 148 / 148 tamam, × iskelet 0 (81 çift, temas 36), × kabuk 0 (509, temas 1), bölge 48 / ihlal 0, STEP 414, eklem tamam | ✅ |
| – | Taban kütlesi | 8.231,4 → 8.272,5 g | 8.272,5 g (+41,1), AM (−0,639; 121,634; −46,122) | aynı |
| – | DXF | 8 yeni + taşınan delik | daire 18 → 27: 8 yeni Ø3,4 + (−65; 18,5); kaldırılan daire yok (eski delik yarığın çizgisindeydi) | ✅ |
| 6 | 16 şema | 16 / 16, 14 temiz, G07 / G16 ara çakışma | 16 / 16; eksen parçanın içinde: G07 yıldız bara tutucusu (uca 118 mm), G16 gövde direği (uca 44,8 mm); M02 / N01 / N02 motor (uçta, ≤ 9,4 mm). Çizim yarıçapı içinde ara: G07 anahtarlı tutucu 0,5, ısıl gömme 2,0, M5x25 2,1. SV3 ucu kart C vida 2,95 / kart 3,0 (önce temiz). HEAD ile fark yalnız SV3 | ✅ aynı |
| 7 | E4 geometri | yarım bindirme, 1,25 + 1,25 | sağ bb x −16…136,65, sol −136,65…0; yerinde ortak 0, mesafe 0; kesit (orta y): sol dış katman z −64,89…−63,64 x 0'a kadar, sağ iç katman −63,64…−62,39 x −16'ya kadar | ✅ |
| 7 | E4 süpürme (B: adım 1 mm, −z / +z 0,25 mm, eşik 0,5 mm³) | sol yerinde → sağ serbest +x, −y, +z, +x+z; −z 0,25'te 18,9 | sağ serbest +x (17 mm'de ayrışır), −y, +z, +x+z; kapalı −z (**0,25 mm'de 18,85 mm³**), −x, +y, −x−z, +y−z | ✅ |
| 7 | | sağ yerinde → sol serbest −x, +y, −z, −x−z, +y−z | aynı beş yön serbest; +x, −y, +z (0,25'te 18,85), +x+z kapalı | ✅ |

## 3. Tam model, tam tarama, regresyon

### 3.1 Zincir (sırayla, tek FreeCAD; her koşuda kilitte B satırı, sonunda "boş")

| Saat | Komut | Süre | Çıkış | Sonuç |
|---|---|---|---|---|
| 11:46 | `taban/taban_montaj.py` | 88 s | 0 | § 2 satırı; `taban-analiz.json` A'nınkiyle `sure_s` dışında aynı, BOM ve DXF md5 aynı |
| 11:49 | B ölçümü (HEAD ve şimdi, depo dışı) | 20 / 32 s | 0 | § 2 |
| 11:52 | `montaj/ana_montaj.py` | 89 s | 0 | **1.251 gerçek parça** (1.225 → 1.251; Referans dahil 1.264), geçersiz 0, solve 0, STEP 1.251, kütle 25.835,1 → 25.876,1 g, AM (0,013; 526,719; −9,594) → (0,034; 526,183; −9,71); `robot-bom.csv` +2 kart satırı, M3x6 80 → 88, M3x8 68 → 76, naylon burç 44 → 52 |
| 11:53 | `lale158/lale158_kontrol.py` | 10 s | 0 | boy **1.580,0** (boy_tamam), parça 1.251; JSON farkı yalnız `parca` |
| 11:53 | `lale158/kafa-yerlesim/uygulama_olc.py` | 438 s | 0 | mikrofon–hoparlör 574,3, SY8205 × kablo 0 mm³; JSON farkı yalnız `sure_s` |
| 12:01 | `lale158/kafa-yerlesim/uygulama_ivme.py` | 60 s | 0 | yüksüz rampa 5° en küçük `rampa5_geri` **1,519 → 1,523** |
| 12:02 | B E4 + vida başı ölçümü (depo dışı) | 41 s | 0 | § 2 |
| 12:03 | tam tarama, koşu `20261120-120318` (B, depo dışı sürücü `b_tarama.py`) | kesildi | sürücü `rc=4` | `statik` bitti (73 s); `omuz` 250 / 875'te 12:44:08 Windows Update yeniden başlatmasıyla öldü; kalan 7 bölüm koşmadı. **Geçersiz, kullanılmadı** |
| 21.11 02:35 | tam tarama, koşu **`20261121-023529`** (B2, `P108d-kontrol-olcum/b2_tarama.py`, baştan 9 bölüm) | 14.085 s (02:35:29–06:30:14) | **0** | § 3.2 |
| 21.11 06:31 | `cd tasarim/freecad && py -3 -B -X utf8 carpisma_kos.py kontrol` | 1 s | **0** | "carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni." |
| 21.11 06:31 | `py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` | 1 s | **0** | GEÇER, kötüleşen yok (§ 3.3); `regresyon.json` / `regresyon-son-kosu.json` md5 önce / sonra aynı, `git status` aynı |
| 21.11 06:31 | B1 ölçümü (B2, salt okuma, `P108d-kontrol-olcum/b2-b1/b1_olc.py`; `taban-montaj.FCStd` md5 önce / sonra aynı) | süre ölçülmedi | 0 (istisna 0) | § 4 B1 |

**B'nin zincir sonuçlarının geçerliliği (B2, 21.11 02:32):** depoda 20.11 12:02:30'dan sonra değişen dosya (`find -newermt`) yalnız
`FREECAD-KILIT.txt`, bu rapor ve eski taramanın `carpisma-bolum/statik.json`'u. Zincir çıktılarının zamanları 11:47:52 … 12:02:06
(`uygulama-ivme.json` son). İzlenen 17 dosyanın md5 özeti B'nin 12:03 kaydıyla (`P108d-kontrol-olcum/kaynak-bas.json`) birebir aynı;
B'nin 11:45 md5 listesiyle (`md5-bas.txt`) 39 dosyanın 36'sı aynı, farklı üçü B'nin kendi yeniden ürettiği `taban-analiz.json`
(`sure_s`), `taban-montaj.FCStd`, `taban-montaj.step`. Bu yüzden zincir yeniden koşulmadı; yukarıdaki 11:46–12:02 satırları geçerli.

Notlar: `freecadcmd` betik istisnasında da 0 döndürüyor (B'nin ilk zincir denemesi yol hatasıyla 4 betiği açamadı, çıkış 0 verdi; hiçbir
dosya yazılmadı, `git status` aynı). Bu yüzden her koşunun günlüğünde "Exception while processing" sayıldı: hepsinde 0. Günlüklerdeki
`QtCore` Traceback'leri bilinen Assembly modülü gürültüsü. Komutlar depo kökünden, `FC_SCRIPT=<betik> freecadcmd run_fc.py`.

### 3.2 Tam tarama (koşu `20261121-023529`, B2)

B'nin koşusu `20261120-120318` kesildi (12:44:08 olay 1074, `MoUsoCoreWorker.exe` "Hizmet paketi (Planlı)"; Kernel-Power 41 / 6008 /
BugCheck / Resource-Exhaustion yok; neden tarama değil, bellek izi yok; ayrıntı `P108d-gunluk.md` § 13.2). Tek koşu şartı yüzünden
`statik` dahil baştan koşuldu.

Sürücü `planlama/d158/P108d-kontrol-olcum/b2_tarama.py`: `carpisma_kos.kos()` ile aynı mantık (modülü içe aktarır; tek koşu kimliği,
9 bölüm ayrı `freecadcmd` süreçlerinde sırayla, sonda `birlestir()`); ek: her bölümden önce boş bellek ≥ 2,5 GB (hiç beklemedi),
kilitte bölüm satırı, günlükler depoda (`b2-log/`), bölüm başı / bitişi saat damgalı `b2-tarama.durum`, 60 s'de bir nabız. Bash arka plan
koşusu. Başta boş bellek 7,57 GB; bölüm başlarında en düşük 7,35 GB.

| Bölüm | Başlangıç → bitiş (21.11) | Süre (sürücü; içinde yükleme) | rc / istisna | Tepe bellek | Çakışma (bu koşu) | HEAD (19.11, `20261119-075818`) |
|---|---|---|---|---|---|---|
| statik | 02:35:29 → 02:36:52 | 83 s (13,7 + 65,6) | 0 / 0 | 751 MB | ev pozu **0** | 0 |
| omuz | 02:36:52 → 06:03:48 | 12.416 s (12.353,9 + 61,4) | 0 / 0 | 732 MB | sağ 116, sol 116 poz; eklem aralığında **0** | 116 / 116; 0 |
| kol_sag | 06:03:48 → 06:07:31 | 223 s | 0 / 0 | 733 MB | tam poz aralıkta 0 / dışı 63; alt poz aralıkta 0 / dışı 53 | aynı |
| kol_sol | 06:07:31 → 06:11:13 | 222 s | 0 / 0 | 748 MB | 0 / 63; 0 / 53 | aynı |
| kolkol | 06:11:13 → 06:12:06 | 53 s | 0 / 0 | 197 MB | 0 / 227 poz çifti | aynı |
| kafa_sabit | 06:12:06 → 06:14:40 | 154 s | 0 / 0 | 743 MB | aralıkta 0 / dışı 0 | aynı |
| kafa_sag | 06:14:40 → 06:21:45 | 425 s | 0 / 0 | 619 MB | çift aralıkta 0 / dışı 3 | aynı |
| kafa_sol | 06:21:45 → 06:28:43 | 418 s | 0 / 0 | 621 MB | 0 / 3 | aynı |
| taban | 06:28:43 → 06:30:14 | 90 s | 0 / 0 | 795 MB | çakışma 0, eklem aralığında 0, statik 0 | aynı |
| **toplam** | 02:35:29 → 06:30:14 | 14.085 s sürücü; `sure_s` 14.075 | sürücü 0 | | **364 / eklem aralığında 0** | 364 / 0 |

Tek koşu doğrulaması: `carpisma-sonuc.json` `tek_kosu: true`, 9 bölümün `kosu` alanı `20261121-023529`, birleştirme notu "Tum bolumler
ayni kaynak dosyalarla … kostu; onceki kosulardan veri alinmadi" (UYARI yok). Her bölümün `kaynak` kaydı sürücünün başta aldığı özetle aynı
(`kaynak_ayni True` × 9). `arayuz_uyumu`, `ayrilmis_bolge`, `ev_pozu_cakisma_s2_0` (4, bilgi) HEAD ile aynı. Değişen yalnız beklenenler:
taban modülü 401 → 427 parça (+26), taban kütlesi 8.231,4 → 8.272,5 g, toplam 25.835,1 → 25.876,1 g, AM (0,01; 526,72; −9,59) →
(0,03; 526,18; −9,71), `ev_pozu_kesisen_cift` (modüller arası sınır kutusu kesişen aday çift sayısı, hacim değil) 868 → 904.
Kablo yolları Referans grubu olduğu için taramaya girmiyor (`moduller.taban.haric`); B1 ayrıca ölçüldü (§ 4).

### 3.3 Korunan değerler (taze ölçüm)

`py -3 -B -X utf8 planlama/d158/regresyon.py --yazma` (21.11 06:31, çıkış 0; taban `regresyon.json` 09.11):

| Değer | Taban | Şimdi | Eşik | Durum |
|---|---|---|---|---|
| Boy, mm | 1.580 | 1.580 | 1.580 ± 0,05 | aynı |
| Çakışma kafa içi / kabuk içi / kabuk × iskelet | 0 / 0 / 0 | 0 / 0 / 0 | 0 | aynı |
| Çakışma ev pozu (tam model, `carpisma-sonuc.json`) | 0 | **0** | 0 | aynı |
| Devrilme payı yüksüz rampa 5° | 1,519 | **1,523** | 1,5 | iyileşti |
| Tilt payı | 3,64 | 3,78 | 3,0 | iyileşti (kafa-analiz.json P10.8d'de değişmedi; fark 09.11 tabanından sonraki paketlerden) |
| Pan payı | 2,21 | 2,26 | 2,0 | iyileşti (aynı not) |
| Mikrofon–hoparlör, mm | 574,3 | 574,3 | 400 | aynı |
| SY8205 × kafa kabloları, mm³ | 0 | 0 | 0 | aynı |

Sonuç: **GEÇER (hepsi okundu, kötüleşen yok)**. `--yazma`: `regresyon.json` ve `regresyon-son-kosu.json` md5'i önce / sonra aynı.
Taban (rampa 1,519) güncellenmedi; argümansız koşu C / orkestratörün işi.

### 3.4 İzlenen dosyalar

`carpisma_kos.kaynak_listesi()` 17 dosya; md5 (10 hane) taramanın başında (`P108d-kontrol-olcum/b2-kaynak-bas.json`, 02:35:29) ve
sonunda (`b2-kaynak-son.json`, 06:30:14) **aynı**, B'nin 20.11 12:03 kaydıyla (`kaynak-bas.json`) da aynı:

| Dosya | md5 | Dosya | md5 |
|---|---|---|---|
| carpisma.py | c688d738c3 | kafa/kafa_parcalar.py | 2421681738 |
| arayuz.py | 288cc20c6e | taban/taban_parcalar.py | **5f6f3d9e81** (P10.8d) |
| ortak_lib.py | a668036c1b | kafa/kafa-analiz.json | 682d561278 |
| sigma_profil.py | 7db14eb8d5 | dirsek/dirsek_lib.py | 51238e19bd |
| iskelet/iskelet_parcalar.py | da1de9d063 | kabuk/kabuk_lib.py | ec1c00a7bd |
| omuz/omuz_parcalar.py | 2093a4ebd4 | kafa/kafa10_lib.py | 32479026d5 |
| kabuk/kabuk_parcalar.py | cb2d75a334 | kafa/kafa_lib.py | a0240ebf6f |
| dirsek/dirsek_parcalar.py | 7182c29899 | omuz/omuz_lib.py | b5c14c4ed2 |
| | | taban/taban_lib.py | 638881cefc |

`carpisma_kos.py kontrol` 0 (yukarıdaki özetler sonuç dosyasının `kaynak` kaydıyla aynı). 19 eski kir ile `taban_parcalar.py`,
`taban-bom.csv`, DXF: 22 / 22 md5 B'nin 20.11 11:45 listesiyle aynı (21.11 06:31).

## 4. Bulgular

**B1: kablo yolu 11 × "Sonar tutucu sol" 0,50 mm (yolun başlangıç ucunda; geçmez nedeni değil).** B'nin izin listesiz ölçümü (§ 2)
yol 11'e en yakın gerçek parçayı 0,50 mm'de buldu; A'nın 1,95 mm'si `IZIN[11] = ^(Sonar|Arayuz karti|ESP32)` ile sonar parçalarını
yolun kendi parçası saydığı için. B2 yeri ölçtü (`P108d-kontrol-olcum/b2-b1/b1.json`, `taban-montaj.FCStd`): en yakın noktalar tüpün
**başlangıç uç kapağı** (−79,41; 124,5; 255) ↔ tutucunun ön yüzü (−79,41; 124,0; 255); ortak hacim **0 mm³**. Yolun ilk noktası
(−79,41; 127; 255) sonar sol pin bloğu (TAHMİN, Q01 / Q02 ile aynı varsayım), tüp yarıçapı 2,5: boşluk tam o ucun önünde, yol boyunca
değil (A'nın § 4 "uç ≤ 10 mm" tanımıyla **uç teması**). Aynı uçta "Sonar_acil_stop" 0,50, "Sonar HC-SR04 (sol)" 4,5 mm. Tam tarama
kablo yollarını (Referans) içermediği için bu değeri değiştirmez; taban × kabuk / iskelet 0. Değerlendirme: yabancı parçaya ≥ 1,0 mm
ölçütü ihlal edilmiyor (tutucu, kablonun bağlandığı sonarın kendi taşıyıcısı ve temas ucunda); gerçek pin / konnektör yeri
doğrulanmadı. Öneri (kuyruk, CAD değil): sonar pin bloğu gerçek ölçüsü gelince yol 11 başlangıcı yeniden ölçülsün.

**B2: `rehber_denetim.py --kaynak` ascii kalıntı 5** (yeni parça adlarındaki `nominal`, `vidali`, `dort`, `kopru`, `giris`; § 5). CAD
geçme ölçütü değil; rehber üretilince veri kipi de düşer. P10.8e'ye devredildi (TR sözlüğü / `ASCII_TAMAM` ya da ad değişikliği).

**B3: `sema_geometri_denetle` 1 hata** (SV3 ucu × dağıtım kartı C, A § 9.1). Bilinen, P10.8e.

**B4 (bilgi):** `regresyon.json` tabanı 09.11'den; tilt / pan "iyileşti" farkı P10.8d'den değil (`kafa-analiz.json` HEAD ile aynı).
Yeni rampa değeri 1,523 tabana yazılmadı.

**B5 (bilgi):** `ev_pozu_kesisen_cift` 868 → 904: 26 yeni taban parçasının (2 kart, 8 burç, 16 vida) modüller arası sınır kutusu
adayları; hacim kesişimi 0 (ev pozu çakışma listesi boş).

## 5. Rehber tarafı (salt okunur; P10.8e'ye devir listesi)

Koşulanlar (sistem Python'u, hiçbiri dosya yazmadı: `git status` önce / sonra aynı):

| Denetim | Çıkış | Sonuç |
|---|---|---|
| `tasarim/freecad/rehber/rehber_kablo.py` | 1 | **SONUÇ KALDI (1 hata)**: şema SV3 son ucu (100; 192; −60) yanındaki parça "Dagitim karti C" eşlenen kabloların ucu değil. Kırpma kesimi hata 0 (yol 9, yol 12 y ≤ 192,5), bara yolu hata 0, geometri hata 0 / bilgi 4, şema geometrisi 27 şema hata 1 |
| `rehber_denetim.py --kaynak` | 1 | **ascii kalıntı 5**, öbür hepsi 0: yeni parça adı / kodundaki `nominal`, `vidali`, `dort`, `kopru`, `giris` (düğüm kartı etiketi ve iki BOM kodu). Beşi de P10.8d adlarından; A'nın günlüğünde yok |
| `rehber_denetim.py` (veri, zincir 3) | 0 | ascii 0, zorunlu eksik 0 / 165, parça **1.238** (rehber verisi P10.8c'den; model artık 1.264) |
| `planlama/adim3/kablolar_denetim.py` | 0 | GEÇER |
| `planlama/d158/F10l-birlesim.py` | 0 | GECER |

P10.8e'ye devredilecekler:
1. `sema_geometri_denetle` 1 hata (SV3 ↔ kart C). A'nın § 6 bellekte denemesine göre `PARCA_CAD` kart C'ye bağlanınca yol 6 karta
   ulaşmıyor (S09 / S10): yol 6'nın karta uzatılması ya da dal yolu.
2. `rehber_denetim --kaynak` ascii kalıntı 5: rehber üretilince bu adlar veriye girer ve zincir 3 (veri kipi) de düşer. Ya
   `rehber_metin` TR sözlüğüne / `ASCII_TAMAM`'a girer (rehber kodu), ya da A adları değiştirir (§ 4 B2).
3. `UC_MODELSIZ` ("düğüm kartı modelde yok", "kafa dağıtım kartı modelde yok"), `PARCA_CAD` iki MODELSIZ satırı, `MODELSIZ_KONUM`.
4. `rehber_metin.py:569`, `:2198` ("Kablo yolu 11 ve 12 kesiğin dışında"), `rehber_denetim.py:420` ZORUNLU kuralı.
5. G07 (bara tutucularının içinden) ve G16 (gövde direğinin içinden) şema düzeltmesi.
6. Rehber verisi parça 1.238 → 1.264: tam rehber üretimi; `uygulama_ivme` raporu / notu (değer bu kontrolde 1,523).
7. Bilgi (maliyet / alım): CAD'de M3x8 naylon burç 52; `maliyet.json` "Kart burcu seti" adet 48 → 4 eksik.

## 6. B / B2'nin yeniden yazdığı üretilmiş dosyalar

- **B (20.11 11:46–12:02, zincir):** `tasarim/freecad/taban/{taban-analiz.json, taban-bom.csv, taban-montaj.FCStd, taban-montaj.step}`,
  `taban/dxf/guc-paneli-arka-5mm-kontrplak.dxf` (BOM ve DXF md5 A'nınkiyle aynı), `montaj/{robot-montaj.FCStd, robot-montaj.step,
  montaj-analiz.json, robot-bom.csv}`, `lale158/lale158-kontrol.json`, `lale158/kafa-yerlesim/uygulama-olcum.json`,
  `lale158/kafa-yerlesim/uygulama-ivme.json`. 12:04: `carpisma-bolum/statik.json` (kesilen koşu; B2 üzerine yazdı).
- **B2 (21.11 02:35–06:30, tarama):** `tasarim/freecad/carpisma-bolum/{statik, omuz, kol_sag, kol_sol, kolkol, kafa_sabit, kafa_sag,
  kafa_sol, taban}.json`, `tasarim/freecad/carpisma-sonuc.json` (git farkı 10 dosya, +189 / −189).
- **Kayıt dosyaları:** bu rapor, `P108d-gunluk.md` § 13–14, `planlama/d158/P108d-kontrol-olcum/` (B'den kurtarılanlar + B2'nin
  sürücüsü, durum, günlükleri, B1 ölçümü), `planlama/dongu-158.md` kilit satırı; `FREECAD-KILIT.txt` (git dışı) "boş".
- Yazılmayan: `regresyon.json`, `regresyon-son-kosu.json` (`--yazma`), kaynak dosyalar, rehber, 19 eski kir (md5 aynı).

## 7. Bakılmayanlar

- Görüntü üretilmedi, kartlar / yollar ekranda görülmedi (taban / montaj / kafa görselleri, `montaj_gorsel`, rehber kareleri koşmadı).
- Rapor betikleri (`taban_rapor.py`, `montaj_rapor.py`, `kafa_rapor.py`, `uygulama_rapor.py`) ve modül regresyonları
  (`iskelet_regresyon`, `omuz_regresyon`; kaynakları değişmedi) koşulmadı; `kafa_montaj.py` koşulmadı (tarama kaynağı
  `kafa-analiz.json`'u eskitirdi).
- Güç panelinin kartlarla birlikte akü üstünden yerine sokulması; düğüm kartına ve kart C'ye giden kabloların (A02…A06, SV3, S09 / S10)
  CAD yolu; kartların gerçek ölçüsü (kart yok, TAHMİN).
- E4'te yalnız 9 yön (A 12 yön) ve yalnız iki kabuk; tam bağlam yeniden ölçülmedi.
- `regresyon.py` argümansız koşulmadı: `regresyon.json` tabanı (rampa 1,519) yazılmadı; yeni değer 1,523 ile tabanı C / orkestratör
  günceller.
