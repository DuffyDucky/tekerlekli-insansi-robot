# F9d günlüğü: herkese açık depo temizliği (P9.4), 09.11.2026

Brief: `planlama/d158/F9d-brief.md`. Plan: `planlama/dongu-158.md` §3 F9 (P9.4). Dal `lale-duzeltme`. Ajan A.
Bu günlükte takma ad ve yerel kullanıcı adı yazılmaz: kullanıcı adı `<kullanıcı>`, takma ad "takma ad" diye geçer.
Geçici dosyalar depo dışında, "scratchpad" klasöründe. Git'te yalnız okuma komutları; commit, push, silme, `.gitignore` değişikliği, FreeCAD yok.
Paralel paket F7c C bu sırada `00a2f56` ve `4c7e2ec` commit'lerini attı; alanına (rehber, demo, `F7c-*`, `dongu-158.md`) yazılmadı.

## 0. Başlangıç (20:11)

| Komut | Çıkış |
|---|---|
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 ("izlenen 17 dosyanın özetleri kayıtla aynı") |
| `py -3 planlama/d158/regresyon.py --yazma` | 0 (GEÇER, hepsi okundu, kötüleşen yok) |

## 1. Yerel kullanıcı yolu taraması

### 1a. Yöntem
Yeni betik **`planlama/d158/F9d-tarama.py`** (yalnız okur):
- `git grep -n -I -i -F -e users`: geniş ön süzgeç, "Users" geçen her izlenen satır.
- Kesin eşleşme Python deseniyle: sürücü harfi (`C:`) ya da POSIX sürücü biçimi (`/c`) + ters ya da düz eğik çizgi + `Users` + ayraç +
  harfle başlayan kullanıcı adı. JSON kaçışlı `\\` biçimi de yakalanır. Kullanıcı adı desende sabit değil; çıktıda `<kullanıcı>` diye maskelenir.
  Zaten kısaltılmış `C:\Users\...` biçimi (F4b'nin yazdığı) ad taşımadığı için eşleşmez.
- Alan sınıflaması: dokunulmaz (brief listesi), paralel alan, tarama kaynağı (`carpisma_kos.kaynak_listesi()` doğrudan çağrılır),
  üretici betik, üretilmiş JSON / çıktı, yazılabilir (kök `README.md`, `planlama/d158/`, tarama kaynağı olmayan betikler), brief listesinde yok.
- Ayrıca `planlama/d158/F9d-*` dosyaları (henüz izlenmiyor, commit'e girecek) taranır.
- Yazılabilir alanda eşleşme varsa ya da README sayıları JSON'la uyuşmazsa çıkış 1.

Not: Git Bash içinde `git grep -E` ile `/[a-z]` içeren desen MSYS yol dönüştürmesine takılıp düz eğik çizgili satırları kaçırdı (ilk elle
sayımda 28 dosya). Betik `git`'i doğrudan `subprocess` ile çağırıyor; sayılar betikten.

### 1b. Önce / sonra

| Alan | Önce satır / dosya | Sonra satır / dosya |
|---|---|---|
| **yazılabilir** | **35 / 30** | **0 / 0** |
| brief listesinde yok | 9 / 5 | 9 / 5 |
| üretici betik | 1 / 1 | 1 / 1 |
| üretilmiş çıktı | 2 / 2 | 2 / 2 |
| üretilmiş JSON | 1 / 1 | 1 / 1 |
| **toplam** | **48 / 39** | **13 / 9** |

Yazılabilir 35 satır: `planlama/d158/` eski paket belgelerinde 19 satır (14 dosya), tarama kaynağı olmayan betiklerde 16 satır (16 dosya:
15 yorum satırı + `carpisma_kos.py:47` sabiti).

### 1c. Düzeltilenler (35 satır, 30 dosya)
Kural: yalnız yol öneki değişti, yolun geri kalanı aynı.
`C:\Users\<kullanıcı>` → `%USERPROFILE%`; `C:/Users/<kullanıcı>` → `~` (satırda `%LOCALAPPDATA%` varsa `%USERPROFILE%`, aynı kabuk biçimi kalsın diye).
Her dosyada eklenen = silinen satır (`git diff --numstat`); satır sayısı aynı.

| Dosya:satır | Tür | Önce (maskeli) | Sonra |
|---|---|---|---|
| `planlama/d158/F0-brief.md:3` | belge | `C:\Users\<kullanıcı>\OneDrive\Masaüstü\Robot` | `%USERPROFILE%\OneDrive\Masaüstü\Robot` |
| `planlama/d158/F1a-brief.md:4`, `F1b-brief.md:5`, `F2-brief.md:5`, `F6a-brief.md:8` | belge | `C:\Users\<kullanıcı>\.robot-cad\run_fc.py` | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `planlama/d158/F1a-gunluk.md:5`, `F1b-gunluk.md:5`, `F2-gunluk.md:5`, `F6a-gunluk.md:5` | belge | `C:\Users\<kullanıcı>\AppData\Local\Temp\claude\…\scratchpad…` | `%USERPROFILE%\AppData\Local\Temp\claude\…` |
| `planlama/d158/F1a-gunluk.md:6`, `F1b-gunluk.md:6`, `F2-gunluk.md:6`, `F6a-gunluk.md:7` | belge | başlatıcı yolu (yukarıdaki gibi) | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `planlama/d158/F1b-kontrol.md:9`, `F2-kontrol.md:18`, `F3a-kontrol.md:113`, `F6a-kontrol.md:19`, `F7a-kontrol.md:20` | belge | scratchpad yolu | `%USERPROFILE%\AppData\Local\Temp\claude\…` |
| `planlama/d158/F6a-kontrol.md:26` | belge | başlatıcı yolu | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `planlama/adim1/pi_kafada_olcum.py:2`, `pi_kafada_tabla.py:2`, `planlama/adim3/K3_cad_olcum.py:3`, `tasarim/freecad/kafa/kafa_gorsel.py:2` | betik (yorum) | `C:\Users\<kullanıcı>\.robot-cad\run_fc.py` | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `planlama/adim2/K-olcum.py:4`, `K2-dudak.py:4`, `K2-geo.py:3`, `K2-kablo.py:4`, `tasarim/freecad/omuz/omuz_baski.py:11`, `tasarim/freecad/taslak-170/taslak_analiz.py:5` | betik (yorum) | `C:/Users/<kullanıcı>/.robot-cad/run_fc.py` | `~/.robot-cad/run_fc.py` |
| `planlama/adim2/S1-duzeltme-kontrol.py:9`, `planlama/adim4/M6_erisim.py:3`, `planlama/y3/Y3_erisim.py:4`, `tasarim/freecad/taslak-170/taslak_gorsel.py:2`, `taslak_montaj.py:3` | betik (yorum, `%LOCALAPPDATA%` satırı) | `C:/Users/<kullanıcı>/.robot-cad/run_fc.py` | `%USERPROFILE%/.robot-cad/run_fc.py` |
| `tasarim/freecad/carpisma_kos.py:47` | betik (sabit) | `BASLATICI = r"C:\Users\<kullanıcı>\.robot-cad\run_fc.py"` | `BASLATICI = os.path.join(os.path.expanduser("~"), ".robot-cad", "run_fc.py")` + yorum `%USERPROFILE%\.robot-cad\run_fc.py` |

**Betiklerin tarama kaynağı kontrolü:** `carpisma_kos.kaynak_listesi()` 17 dosya döndürüyor (`KAYNAK_SABIT` 11 + `*_lib.py`, `*/*_lib.py`).
Düzeltilen 16 betiğin hiçbiri bu listede değil (betik bunu her koşuda yeniden denetliyor; `carpisma_kos.py` kendisi listede değil, `carpisma.py` var).
Hiçbir betik başka bir betiğin başlık yorumunu okumuyor (`git grep` ile ad atıfları tek tek bakıldı: yalnız metin atfı).

**Aynı çıktı kanıtı:** 15 betik FreeCAD betiği; FreeCAD bu pakette yasak, o yüzden koşturmak yerine kod ağacı karşılaştırıldı:
`ast.dump(ast.parse(HEAD))` = `ast.dump(ast.parse(çalışma kopyası))` → **15 / 15 aynı** (yalnız yorum değişti, derlenen kod bayt bayt aynı;
`compile()` geçti). `carpisma_kos.py` kodu değişti (16. dosya, AST farklı, beklenen); kanıt:
- `BASLATICI` değeri önce / sonra (`import carpisma_kos; print(BASLATICI)`, scratchpad'e yazıldı, ekrana basılmadı): `cmp` → **aynı**; dosya var (`os.path.isfile` True).
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` çıktısı önce / sonra: `cmp` → **aynı**, çıkış 0.
- `BASLATICI` yalnız `kos()` içinde system Python'da kullanılıyor (`subprocess.call([FC, BASLATICI])`); Windows'ta `expanduser("~")` = `%USERPROFILE%`.

### 1d. Ele alınmayan kalanlar (13 satır, 9 dosya; her biri gerekçeli)

| Dosya:satır | Tür | Alan | Neden |
|---|---|---|---|
| `planlama/y2/Y2a-brief.md:19` | belge | brief listesinde yok | Brief yalnız `planlama/d158/` eski paket belgelerine izin veriyor; `planlama/y2/` dışarıda. Aynı dönüşüm sonraki pakette (1 satır). |
| `planlama/y2/Y2b-brief.md:13` | belge | brief listesinde yok | Aynı neden (depo yolu, 1 satır). |
| `planlama/y3/Y3-brief.md:23`, `:28` | belge | brief listesinde yok | Aynı neden (depo yolu + başlatıcı, 2 satır). |
| `tasarim/freecad/README.md:43`, `:47`, `:48`, `:92` | belge | brief listesinde yok | Brief README iznini yalnız kök `README.md` madde 3 için veriyor. `:47`/`:48` kabuk örneğinde `R=` / `L=` değişkenleri (4 satır). |
| `tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md:37` | belge | brief listesinde yok | Yedek klasörü yolu; brief listesinde değil (1 satır). |
| `tasarim/freecad/taslak-170/taslak_rapor.py:458` | betik | üretici betik | Yol, ürettiği `rapor.html`'e giden metnin içinde; değiştirmek çıktıyı değiştirir (brief: "çıktıyı değiştirmiyorsa düzelt"). Tarama kaynağı değil. |
| `tasarim/freecad/taslak-170/rapor.html:154` | belge | üretilmiş çıktı | `taslak_rapor.py` çıktısı; elle değil yeniden üretimle değişir. |
| `tasarim/freecad/lale158/2209b-cad-sonuclar.json:6` | JSON (kaçışlı) | üretilmiş JSON | Dokunulmaz (üretilmiş JSON). Anahtar `png_tam_yol`; üreten betik izlenen dosyalarda bulunamadı (`git grep png_tam_yol`: yalnız bu JSON). |
| `tasarim/freecad/lale158/ikinci/yavaslik/prof-head-kabuk.txt:72` | üretilmiş çıktı | üretilmiş çıktı | cProfile çıktısı; yol FreeCAD kurulumunun `site-packages` yolu (F4b de bu dosyada yalnız kendi önekini kısaltmıştı). |

Dokunulmaz izlenmeyen alanda da yol var (izlenmediği için toplamda yok): `tubitak-2209b/` 5 dosyada 14 satır (K18).
Tarama kaynaklarında, `kod/`, paralel alanda (rehber, demo, `tasarim/cad/`, `F7c-*`, `dongu-158.md`) ve `CLAUDE.md`'de eşleşme 0.

**Geçmiş:** geçmiş yeniden yazılmadı. `git log --all -G '<sürücü>:<ayraç>Users<ayraç><ad>'`: **125 commit'in 29'unda** yerel yol geçiyor;
eski commit'lerde (ve GitHub'daki geçmişte) yol kalır. Rapor için not: "HEAD'de yazılabilir alanda 0; eski commit'lerde yol kalır."

## 2. Takma ad taraması
Biçim F6a / F4b'deki gibi: `git grep -il <takma ad>` (harf duyarsız; hesap adı ve not deposu adı içindeki geçişler de yakalanır).
Ad bu günlüğe ve betiğe yazılmadı: `TAKMA_AD` ortam değişkeniyle verildi, değer `git remote` adresinden kabukta türetildi; betik yalnız sayı ve dosya basar.

| Küme | Satır | Dosya | Liste |
|---|---|---|---|
| İzlenen, **hafıza** | 3 | 1 | `CLAUDE.md` (K25, dokunulmadı) |
| İzlenen, diğer | 3 | 2 | `kod/ortak/eklem_sinirlari.json` (1; `kod/` dokunulmaz, KT-F6a-1 önerisi bekliyor), `tasarim/freecad/index.html` (2; K26, GitHub hesap adı iki bağlantının içinde) |
| **İzlenen toplam** | **6** | **3** | |
| İzlenmeyen, hafıza | 27 | 1 | `tubitak-2209b/BAGLAM.md` |
| İzlenmeyen, tarihçe (değişiklik / karar / denetim / hakem notları) | 129 | 24 | hepsi `tubitak-2209b/taslak/` altında |
| İzlenmeyen, diğer | 76 | 23 | 21'i `tubitak-2209b/`, ayrıca `raporlar/11-6-inc-gogus-ekrani-sigma.md` (2; K24), `tasarim/solidworks/renkler.md` (1; K22) |
| **İzlenmeyen toplam** | **232** | **48** | 46'sı `tubitak-2209b/` (K18) |
| **Git tarihçesi** | — | — | içerikte (`git log --all -i -G`) **48 / 125 commit**; commit mesajında 3; yazar / committer alanında 0 |

Ayrıca depo adresinin kendisi (GitHub hesap adı) takma adı taşıyor: K26.
Düzeltilen dosyaların eklenen satırlarında ve `F9d-*` dosyalarında takma ad 0, kullanıcı adı 0 (Python ile sayıldı).

## 3. README (yalnız madde 3)
Karşılaştırma ve kaynak anahtarları (`F9d-tarama.py` her koşuda yeniden denetler):

| README metni | Kaynak | Anahtar | Değer | Önce README'de |
|---|---|---|---|---|
| "50 adım" | `planlama/rehber/kontrol.json` | `ozet.adim` (= `yazdir.adim`) | 50 | yoktu |
| "1.192 parça" | `planlama/rehber/kontrol.json` | `ozet.parca_rehber` (= `ozet.parca_mesh`, `denetim.parca`) | 1192 | yoktu |
| "53 sayfa" | `planlama/rehber/kontrol.json` | `yazdir.pdf_sayfa`; `yazdir.sayfa_esleme` en büyük sayfa 53 (adım 49 → 52, 53), `esleme_tutarli` true | 53 | yoktu |
| "127 JSON anahtarından" | `tasarim/Robot-Tasarim-Demosu.html` | `<script id="kaynak">` `anahtarlar` sayısı (F9b `demo_uret.py`) | 127 | yoktu |
| "boy 1.580 mm" / "**1.580,0 mm**" | `tasarim/freecad/lale158/lale158-kontrol.json` | `toplam_boy_mm` (demoda `boy` anahtarı aynı yol) | 1580.0 | tablo satırı doğruydu |
| 3B model, 1.192 parça | demo `kaynak.model` | `script` = `../rehber/veri/rehber-veri.js`, `../rehber/veri/robot-glb.js`; `dugum` 1192 | — | "3B modeli mevcut demodan alır" (eski) |

Değişen README satırları (11 eklenen, 10 silinen; Pages bağlantısı yok, dokunulmadı; `main`'e birleştirme iddiası yok):
- Klasör tablosu, rehber satırı: 1,58 m, 50 adım, 1.192 parça, PDF 53 sayfa ve kaynak anahtarları eklendi.
- Demo satırı: "Eski CadQuery 3B montajı (V1 / V2 / V3, 125 cm)…" eskiydi → "Lale tasarım demosu, 1,58 m (P9.2, F9b)…; bu sürüm `lale-duzeltme` dalında"
  (`main` ve `origin/main`'deki demo eski başlıklı sürüm; README yalnız bu dalı anlatıyor).
- `robot_cad.py` satırı: "Modeli üreten kod (STEP + CSV + demo)" → eski CadQuery modeli, demoda kullanılmaz (`demo_uret.py:16-17`).
- `demo_uret.py` satırı: "şablon + model + maliyet" → "şablon + kaynak JSON'lar + maliyet; FreeCAD / CadQuery gerekmez; denetim `F9b-dogrula.py`".
- "Montaj rehberini üretme": "adım seçicileri 1,58 m'e uyarlanmadı" eskiydi (`R-gunluk.md:41`: seçiciler `rehber_secici.py`'de, F7a) → düzeltildi.
- "CAD'i yeniden üretme": bölümün eski CadQuery modeline ait olduğu ve modelin demoya girmediği yazıldı; son paragraf demo yenilemeyi
  göreli model bağlantısıyla anlatıyor.
Değişmedi: "Demodaki 3B görünüm için internet gerekir" doğru (demo three.js'i CDN'den yüklüyor). 1.179 parça satırı (MA `parca_sayisi`, ana montaj)
rehberin 1.192'siyle çelişmiyor, ayrı sayımlar.

## 4. Karar taslakları (karar-kuyrugu.md'ye yazılmadı)

### KT-F9d-1 · D-9: `planlama/rehber/goruntu/adim-*.png` depoda nasıl tutulsun
**Ölçüm:**
- `git count-objects -vH`: gevşek 2.975 nesne **439,65 MiB**, paket 267 nesne 474,60 KiB, `prune-packable` 2; `.git` klasörü 461.680.698 B.
- Çalışma ağacı: `planlama/rehber/goruntu/` 57 PNG 7.101.641 B, bunun `adim-*.png` 50 dosyası **6.482.146 B**, `telefon-360-*` 7 dosya.
  Yanında üretilen: `rehber/goruntu/` 50 PNG 3.261.137 B, `Lale-montaj-rehberi.pdf` 4.008.893 B.
- Rehber üretim commit'leri (yeni blob bayt):

| Commit | adım PNG | telefon PNG | `rehber/goruntu` | PDF | Toplam |
|---|---|---|---|---|---|
| `887bcfe` (P7.1) | 50 / 6.465.071 | — | — | — | 6,47 MB (+ `rehber/veri` 6,71 MB) |
| `649885f` (P7.2) | 50 / 6.451.048 | 7 / 609.971 | 50 / 3.261.137 | 3.987.397 | **14,31 MB** (adım + rehber/goruntu + PDF = 13,70 MB) |
| `e448eab` (P7.3) | 3 / 570.321 | 2 / 209.719 | — | 4.008.893 | 4,79 MB |

- Geçmişte yalnız `adim-*.png`: **111 blob, ham 14.845.781 B, diskte 14.489.931 B** (%97,6; PNG sıkışmıyor); `telefon-360-adim-*` 9 blob'uyla
  birlikte 120 / 15.665.471 / 15.287.573 (düzeltme turu 1, D-2: ilk sürümde etiket 120'yi yalnız adım PNG'si diye veriyordu). Tüm geçmiş blob'ları diskte ≈ 461 MB;
  en büyükler `.step` 172 MB, `.FCStd` 135 MB, `.html` 67 MB, `.png` 48,7 MB.
- Görüntüler belirlenimci: `e448eab`'de 50 adımdan yalnız 3'ü değişti; görüntüsü değişmeyen adım 0 B ekliyor. "≈ 13 MB" yalnız tam görsel değişimde.
- 14 izlenen dosya `rehber/goruntu/adim-` yollarına bağlantı veriyor (`kontrol.json` `sonuc[].goruntu`, F7a/F7b/F7c günlük / kontrol / raporları, `R-gunluk.md`, `rehber_uret.py`).

**Seçenekler:**
- a) `.gitignore` + izlemeden çıkarma (`git rm --cached`, kayıt ajanı): sonraki üretimler 0 B; geçmişteki 14,5 MB (telefon dahil 15,3 MB) kalır; görüntüye bağlanan
  dosyaların (en çok 14) bağlantıları GitHub'da kırılır, rehber kanıtı yalnız yerelde kalır.
- b) **Yalnız sürüm commit'i:** PNG'ler yalnız paket kayıt commit'inde (ya da Ahmet'in "sürüm" dediği commit'te) girer, ara düzeltme
  turlarında `git add` listesine alınmaz. Bugünkü 3 üretim commit'i 25,6 MB ekledi; b'de aynı gün tek commit'le ≈ 6,5 MB (adım PNG) + değişen
  PDF / `rehber/goruntu`. Araç değişmez; ara turlarda `git status` kirli kalır (K23'e benzer).
- c) Git LFS (yerelde `git-lfs/3.7.1` kurulu): depo geçmişine PNG başına ~130 B işaretçi; LFS deposuna yine ≈ 6,5 MB / tam üretim;
  mevcut 14,5 MB geçmişte kalır (geçmiş yeniden yazılmaz); 4 kişilik ekipte herkes `git lfs install` yapmalı; GitHub Pages LFS dosyalarını
  sunmaz, bu yüzden yalnız `planlama/rehber/goruntu/` için uygun (Pages'ten açılabilecek `rehber/goruntu/` için değil); ücretsiz LFS kotası hesap
  planına bağlı, bu pakette doğrulanmadı.

**Önerilen varsayılan: b.** Kanıt bağlantıları korunur, araç ve `.gitignore` değişmez; belirlenimci üretim yüzünden gerçek artış yalnız görsel
değiştiğinde. Ek not (karar değil): gevşek nesneler 439,65 MiB; bu yerel bakım işi (`git gc`) depo boyunu GitHub'da değiştirmez.

### KT-F9d-2 · `tasarim/cad/lale158-model.js` (izlenmeyen artık dosya)
- **Üreten:** `tasarim/cad/demo_uret.py`, F9b ilk turu (dosya başlığı: "Ureten: tasarim/cad/demo_uret.py"; tarih 09.11 17:30). KT-F9b-2 = b
  (orkestratör) ile sayfa göreli bağlantıya geçti; betik artık üretmiyor (`demo_uret.py:20` "Eski kopya … artik uretilmez").
- **Demo kullanıyor mu: hayır.** `Robot-Tasarim-Demosu.html`'de "lale158-model" 0 geçiş; `<script src>` yalnız `../rehber/veri/rehber-veri.js`,
  `../rehber/veri/robot-glb.js` ve three.js CDN. `F9b-dogrula.py:522` sayfa bu dosyaya bağlanırsa hata veriyor.
- 3.495.365 B; git geçmişinde 0 commit; içerdiği GLB sha256 `760bf1ff5955` bugünkü `rehber/veri/robot.glb` ile aynı (yinelenen kopya).
  `rapor/` altındaki aynı adlı dosya (K20, 2,0 MB) ayrı bir dosya, bu karar onu kapsamaz.
- **Seçenekler:** a) sil: disk −3,5 MB, `git status` −1 satır, depo etkisi 0; kaynağı `rehber/veri/`'de, yeniden üretmeye gerek yok.
  b) `.gitignore`'a ekle: `git status` −1 satır, `.gitignore` +1 satır, 3,5 MB OneDrive'da kalır. c) bırak: 1 `??` satırı kalır; açık
  listesiz bir `git add` 3,5 MB'ı herkese açık depoya sokabilir.
- **Önerilen varsayılan: a (sil; Ahmet ya da kayıt ajanı).**

### KT-F9d-3 · Kalıcı izlenmeyenler ve K23 (`git status --porcelain`, 20:23)

| Girdi | Boyut | Bağlı karar | Öneri | Neden |
|---|---|---|---|---|
| ` M` `tasarim/freecad/kabuk/gorsel/*.png` (13) + ` M` `tasarim/freecad/montaj/yerlesim-kontrol.json` (+45 −45) | 787.293 B + 9.048 B | K23 (açık) | **bekle** | 03.11 ara çıktısı, karar Ahmet'te (varsayılan a "ara çıktı" commit'i); regresyon bu dosyalardan değer okumuyor. |
| ` M` `planlama/dongu-158.md` | — | — | **bekle** | Orkestratör / F7c alanı; bu paketin değil. |
| `kvkk/` | 16 dosya, 3.142.451 B | K19 | **`.gitignore`** | İç dosya / kişisel veri; K19 varsayılanı dışla. |
| `rapor/` | 20 dosya, 11.087.000 B | K20 | **`.gitignore`** | Ekip üyelerinin ve danışmanın adları; onayları kayıtta yok (K20 varsayılanı a). |
| `tubitak-2209b/` | 267 dosya, 110.862.910 B | K18 | **`.gitignore`** | Takma ad 229 satır / 46 dosya, yerel yol 14 satır / 5 dosya; 111 MB. |
| `tasarim/freecad/lale158/kafa-yerlesim/kaynak/` | 5 dosya, 3.047.767 B | K21 | **`.gitignore`** | Satıcı dosyaları (STP, JPG, PNG), dokunulmaz; K21 varsayılanı. |
| `tasarim/solidworks/` | 6 dosya (+ `__pycache__`), 28.676.311 B | K22 | **bekle → kısmi commit** | K22 varsayılanı: `step_renkli.py`, `step_duz.py`, `renkler.md` commit, 2 STEP (28,6 MB) dışla; önce `renkler.md:63` takma adı temizlenmeli. |
| `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat` | 17.760 + 1.421 B | K22 / G6 | **bekle → commit** | Hareket makrosu; takma ad 0, yerel yol 0; `step_renkli.py`'yi içe aktarıyor, K22 ile birlikte girmeli. |
| `raporlar/11-6-inc-gogus-ekrani-sigma.md` | 9.546 B | K24 / G4 | **bekle** | 2 satırda takma ad + depo dışı hafıza dosya adı; K24 varsayılanı: önce temizle sonra commit. |
| `raporlar/kaynaklar/06-onayli-satici-A.md`, `-B.md`, `07-gogus-ekrani-ve-5v.md` | 40.862 B | G4 | **commit** | İzlenen `arayuz.py:347,531` ve `elektrik.md:16` bunlara atıf yapıyor (sarkan atıf); takma ad 0, yerel yol 0. |
| `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt` | 1.862 + 2.310 B | — | **commit** | Öncül: `F3a-pano-govde.txt` `9cca013`'te commit'lendi; panoya giden mesaj metni, takma ad 0, yerel yol 0, yalnız ilk ad. |
| `planlama/d158/FREECAD-KILIT.txt` | 6 B ("boş") | — | **`.gitignore`** | Koşu kilidi (çalışma zamanı durumu); izlenirse her FreeCAD koşusu diff üretir. Silinmez (F6b brief'i). |
| `planlama/d158/F7d-brief.md` | — | — | **bekle** | F7d paketinin brief'i; F7d kaydı alır. |
| `tasarim/cad/lale158-model.js` | 3.495.365 B | KT-F9d-2 | **sil** (yukarıda) | Kullanılmayan yinelenen kopya. |
| `planlama/d158/F9d-brief.md`, `F9d-tarama.py`, `F9d-gunluk.md` | — | — | **commit** | Bu paketin dosyaları (aşağıdaki liste). |

`.gitignore` önerisi alan 5 girdinin sayısal etkisi: `git status`'ta −5 satır, 128,1 MB izlenmeyen veri dışarıda kalır. `.gitignore` değiştirilmedi.

## 5. Son kontrol, ilk tur (20:23 – 20:25; güncel sonuçlar §7.6)

| Komut | Çıkış |
|---|---|
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** (çıktı başlangıçla bayt bayt aynı) |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** (GEÇER) |
| `TAKMA_AD=<takma ad> py -3 planlama/d158/F9d-tarama.py --ozet` | **0**: yazılabilir alanda yerel yol **0**; toplam 13 satır / 9 dosya (yukarıdaki §1d); takma ad izlenen 6 satır / 3 dosya; README sayı uyuşmazlığı **0** |
| AST karşılaştırması (HEAD ↔ çalışma kopyası, 16 betik) | 15 aynı, 1 beklenen fark (`carpisma_kos.py`, değer aynı) |
| Eklenen satırlarda takma ad / kullanıcı adı (Python) | 0 / 0 (`F9d-*` dahil) |

## 6. Dokunulan dosyalar (kayıt ajanı için açık `git add` listesi, düzeltme turu 1 sonrası **40 dosya**)

Değişen (36; düzeltme turu 1 ile +5):
```
README.md
planlama/adim1/pi_kafada_olcum.py
planlama/adim1/pi_kafada_tabla.py
planlama/adim2/K-olcum.py
planlama/adim2/K2-dudak.py
planlama/adim2/K2-geo.py
planlama/adim2/K2-kablo.py
planlama/adim2/S1-duzeltme-kontrol.py
planlama/adim3/K3_cad_olcum.py
planlama/adim4/M6_erisim.py
planlama/y3/Y3_erisim.py
planlama/y2/Y2a-brief.md
planlama/y2/Y2b-brief.md
planlama/y3/Y3-brief.md
planlama/d158/F0-brief.md
planlama/d158/F1a-brief.md
planlama/d158/F1a-gunluk.md
planlama/d158/F1b-brief.md
planlama/d158/F1b-gunluk.md
planlama/d158/F1b-kontrol.md
planlama/d158/F2-brief.md
planlama/d158/F2-gunluk.md
planlama/d158/F2-kontrol.md
planlama/d158/F3a-kontrol.md
planlama/d158/F6a-brief.md
planlama/d158/F6a-gunluk.md
planlama/d158/F6a-kontrol.md
planlama/d158/F7a-kontrol.md
tasarim/freecad/carpisma_kos.py
tasarim/freecad/kafa/kafa_gorsel.py
tasarim/freecad/omuz/omuz_baski.py
tasarim/freecad/taslak-170/taslak_analiz.py
tasarim/freecad/taslak-170/taslak_gorsel.py
tasarim/freecad/taslak-170/taslak_montaj.py
tasarim/freecad/README.md
tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md
```
Yeni (4):
```
planlama/d158/F9d-brief.md
planlama/d158/F9d-tarama.py
planlama/d158/F9d-gunluk.md
planlama/d158/F9d-kontrol.md
```
Listeye girmeyenler: `planlama/dongu-158.md`, K23 dosyaları (13 kabuk PNG, `yerlesim-kontrol.json`), F7d'nin bütün dosyaları (`F7d-*`, `rehber/`,
`planlama/rehber/`, `tasarim/freecad/rehber/`, `tasarim/cad/viewer-template.html`) ve §4'teki izlenmeyenler.
**Sıra:** önce F7d commit'i, sonra F9d: README "54 sayfa" F7d'nin `kontrol.json`'uyla tutarlı (HEAD'deki 53 ile değil).
`regresyon-son-kosu.json` yazılmadı (`--yazma`).

## 7. Düzeltme turu 1 (B kontrolü `planlama/d158/F9d-kontrol.md`: KOŞULLU; 20:35 – 20:47)
Kapsam orkestratörden: O-1, O-2, D-1; D-2…D-5 yalnız günlükte yanıt. F7d alanına yazılmadı; commit, push, silme, `.gitignore`, FreeCAD yok.

### 7.1 O-2: README kütle satırı ve öteki sayılar
README:40 (`git diff --numstat` README toplam +14 −13):

| README önce | README sonra | Kaynak · anahtar |
|---|---|---|
| ana montaj 25.715,6 g | **25.720,55 g** | `tasarim/freecad/montaj/montaj-analiz.json` · `kutle_g` |
| ev pozu **26.115,6 g** | **26.120,6 g** | `tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json` · `ev.kutle_g` |
| AM (−0,03; 522,71; −10,03) | **(−0,03; 522,84; −10,03)** | aynı dosya · `ev.am` |
| 400 g kablo payı | aynı (anahtar eklendi) | aynı dosya · `kablo_payi.kutle_g` |

Aynı karşılaştırmayla iki eski satır daha bulundu ve düzeltildi:
- **Baskı satırı (README:49):** "65 parça, 7,63–7,68 kg, 159–160 sa (03.11, P4.3'te yenilenecek)" → "72 parça (13'ü destekli), destek dahil
  7.668,9–7.726,7 g, 159,9–161,08 sa". Kaynak `tasarim/freecad/lale158/baski-analiz.json` `toplam.adet`, `toplam.destekli_adet`,
  `toplam.toplam_g.0/.1`, `toplam.sure_sa.0/.1` (F6b tek analiz, `0f8e1ad`; `planlama/baski-listesi.md` ve demonun `b_*` anahtarları da bunu kullanıyor).
- **Klasör tablosu baskı listesi (README:16):** "65 parça; 03.11, kafa satırları 7" modelinden" → "72 parça; 09.11, tek analiz `baski-analiz.json`".

`F9d-tarama.py` README denetimi 6 satırdan **38 satıra** çıktı; her satır README metnini JSON'dan biçimleyip README'de arar:

| README metni | Kaynak | Anahtar |
|---|---|---|
| 50 adım · 1.192 parça · (54 sayfa) | `planlama/rehber/kontrol.json` | `ozet.adim` · `ozet.parca_rehber` · `yazdir.pdf_sayfa` (+ `sayfa_esleme` en büyük) |
| 127 JSON anahtarından | `tasarim/Robot-Tasarim-Demosu.html` | `script#kaynak` `anahtarlar` sayısı |
| boy 1.580 mm · **1.580,0 mm** | `tasarim/freecad/lale158/lale158-kontrol.json` | `toplam_boy_mm` (MA `boy_mm` 1580,0 aynı) |
| gövde direği 1.115,5 mm | `tasarim/freecad/montaj/robot-bom.csv` | Kalem "Sigma 40x40 agir kanal 10, 1115.5 mm" |
| merkezi y 1.270 mm · uzatması 315 mm | `montaj-analiz.json` | `s3_mm` · `uzama_mm` |
| 1.179 parça · ana montaj 25.720,55 g · 520 mm | `montaj-analiz.json` | `parca_sayisi` · `kutle_g` · `taban_w_mm` |
| 400 g kablo payı · **26.120,6 g** · AM (−0,03; 522,84; −10,03) | `uygulama-ivme.json` | `kablo_payi.kutle_g` · `ev.kutle_g` · `ev.am` |
| pay **1,519** · düz zeminde 2,097 | `uygulama-ivme.json` | `izgara_yuk_0g.a_sinir_pay15.rampa5_geri` · `.duz_geri` |
| teker izi 432 mm (x ±216 | `planlama/y2/Y2b-ivme.json` | `teker_hatti.iz_genisligi` · `teker_hatti.x` |
| akü **3,0 kg** | `robot-bom.csv` | Kalem "LiFePO4 12,8 V 20 Ah Victron …" toplam kütle 3000 |
| DS3235 × 4, MG996R × 6 · **toplam 10 servo** | `robot-bom.csv` | Kalem "DS3235 servo" / "MG996R servo" adet |
| Kafa grubu 1.570,8 g · tilt payı 3,64 · pan payı 2,21 | `tasarim/freecad/kafa/kafa-analiz.json` | `tork.tilt.kutle_g` · `tork.tilt.pay_tilt15` · `tork.pan.pay_iki_hane` |
| tilt sınırı ±13° · S2 ≥ +5° | `kod/ortak/eklem_sinirlari.json` (yalnız okundu) | `eklemler.tilt.min/max` · `eklemler.r_s2.min` (= `l_s2.min`) |
| ivme ve fren ≤ 0,1 · ivme ≤ 0,5, fren ≤ 1,8 m/s² | aynı | `teker.ivme_sinir_m_s2.rampa_surus/rampa_fren` · `.duz_surus/.duz_fren` |
| mikrofon-hoparlör en az 574,3 mm | `tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json` | `mic_hoparlor.poz_min_mm` |
| baskı 72 parça (13'ü destekli) · 7.668,9–7.726,7 g · 159,9–161,08 sa · klasör tablosu 72 parça | `tasarim/freecad/lale158/baski-analiz.json` | `toplam.adet`, `.destekli_adet`, `.toplam_g`, `.sure_sa` |
| maliyet ≈ 118.700 TL · koşullularla ≈ 124.600 · elde düşülürse ≈ 93.800 | `planlama/maliyet.json` | JSON anahtarı değil, hesap: `planlama/adim5/maliyet_toplam.py` ve sayfa kuralı (V3, yazıcı, yedek, %15): genel 118.666,22; koşullu 124.573,11; elde (Pi 5, kart, yüz ekranı) düşülmüş 93.770,47. `maliyet_toplam.py` çıkış 0; `F9b-dogrula.py --tarayicisiz` [3] "genel 118.666,22 TL", çıkış 0 |
| QLED satın alınırsa ≈ 102.100 | `planlama/d158/F8a-siparis.json` + `maliyet.json` | hesap: (ara − elde + `kalemler[id=S76].birincil.fiyat` 7.217,95) × 1,15 = 102.071,11 |
| sipariş paketi ≈ 107.600 TL | `planlama/d158/F8a-siparis.json` | `toplamlar.okul_butcesi_dahil_pay15` 107.569,14 |

Karşılaştırılmayan README sayıları (anahtarı yok ya da karar / metin): K-numaraları, "E0–E9", "≤ 100 g / el" (K9 önerisi), "6. USB cihazı"
(K1), "1280 × 720", "11,6" 1080p", "Pi 5 4 GB" (BOM kalem adlarıyla aynı metin), tarihler; "Aşağıdaki bölümler projenin geçmişidir"
satırından sonraki Eylül–Ekim bölümleri (README onları kendisi tarihli diye işaretliyor).

### 7.2 O-1: PDF sayfa sayısı
F7d rehberi çalışma ağacında yeniden üretti: `planlama/rehber/kontrol.json` `yazdir.pdf_sayfa` = **54**, `sayfa_esleme` en büyük sayfa 54
(HEAD'de 53). README "(53 sayfa)" → **"(54 sayfa)"**. `F9d-tarama.py` dosyaları diskten (`open(os.path.join(KOK, …))`) okur, yani
**çalışma ağacına göre** denetler, HEAD'e göre değil: `git show HEAD:planlama/rehber/kontrol.json` → 53, betik 54 basıyor. Kayıtta önce F7d,
sonra F9d commit'lenirse commit'lenen README ile `kontrol.json` aynı (54). F9d, F7d'den önce commit'lenirse HEAD'de README 54 /
`kontrol.json` 53 olur; bu yüzden sıra şart.

### 7.3 D-1: ek yol temizliği (yalnız önek, 9 satır / 5 dosya)

| Dosya:satır | Önce (maskeli) | Sonra |
|---|---|---|
| `planlama/y2/Y2a-brief.md:19` | `C:\Users\<kullanıcı>\.robot-cad\run_fc.py` | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `planlama/y2/Y2b-brief.md:13` | `C:\Users\<kullanıcı>\OneDrive\Masaüstü\Robot` | `%USERPROFILE%\OneDrive\Masaüstü\Robot` |
| `planlama/y3/Y3-brief.md:23` | depo yolu (aynı) | `%USERPROFILE%\OneDrive\Masaüstü\Robot` |
| `planlama/y3/Y3-brief.md:28` | başlatıcı yolu | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `tasarim/freecad/README.md:43` | başlatıcı yolu (metin) | `%USERPROFILE%\.robot-cad\run_fc.py` |
| `tasarim/freecad/README.md:47` | `R="C:/Users/<kullanıcı>/OneDrive/Masaüstü/Robot/tasarim/freecad"` (bash) | `R="$USERPROFILE/OneDrive/Masaüstü/Robot/tasarim/freecad"` |
| `tasarim/freecad/README.md:48` | `L=C:/Users/<kullanıcı>/.robot-cad/run_fc.py` (bash) | `L=$USERPROFILE/.robot-cad/run_fc.py` |
| `tasarim/freecad/README.md:92` | PowerShell komutunda başlatıcı yolu | `$env:USERPROFILE\.robot-cad\run_fc.py` |
| `tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md:37` | `C:\Users\<kullanıcı>\.robot-cad\yedek-qled-oncesi\` | `%USERPROFILE%\.robot-cad\yedek-qled-oncesi\` |

Kuraldan sapma ve nedeni: `tasarim/freecad/README.md:47`, `:48` ve `:92` çalıştırılan komutlar. `%USERPROFILE%` bash'te ve PowerShell'de
açılmaz; `~` ise çift tırnak içinde açılmaz. Komutlar bozulmasın diye aynı değişkenin kabuk yazımı kullanıldı (bash `$USERPROFILE`,
PowerShell `$env:USERPROFILE`; satırlarda zaten `$LOCALAPPDATA` / `$env:LOCALAPPDATA` var). Git Bash'te `$USERPROFILE` Windows biçiminde
açılır, yani eski `C:/…` gibi doğrudan freecadcmd'ye gider. Deneme: `USERPROFILE` ters eğik çizgili bir deneme değeri `<profil>` alınca `R` ve `L`'nin açılımı
`<profil>/OneDrive/…` ve `<profil>/.robot-cad/run_fc.py`. Her dosyada eklenen = silinen satır; `git diff --check` 0.

**Önce / sonra (betik, `--ozet`):**

| Alan | Tur 1 öncesi | Tur 1 sonrası |
|---|---|---|
| yazılabilir | 0 / 0 | 0 / 0 |
| brief listesinde yok (D-1 dosyaları) | 9 / 5 | **0 / 0** |
| üretici betik (`taslak_rapor.py:458`) | 1 / 1 | 1 / 1 |
| üretilmiş çıktı (`taslak-170/rapor.html:154`, `prof-head-kabuk.txt:72`) | 2 / 2 | 2 / 2 |
| üretilmiş JSON (`2209b-cad-sonuclar.json:6`) | 1 / 1 | 1 / 1 |
| **toplam** | **13 / 9** | **4 / 4** |

Paketin başından: 48 / 39 → 4 / 4. Kalan 4 satırın gerekçesi §1d'deki gibi: üretici betik ile çıktısı birlikte düzeltilmeli, JSON'un üreticisi bulunmalı.

### 7.4 Düşük bulgular
- **D-2 (kabul, düzeltildi):** §4 KT-F9d-1'de etiket artık 111 adım blob'u / 14.845.781 / 14.489.931 B; telefon dahil 120 ayrıca yazıldı. Öneri (b) değişmedi.
- **D-3 (bilgi):** `pi_kafada_olcum.py` çalışma kopyası `w/mixed` (`git ls-files --eol`). Değiştirme betiği satırları `\n`'de bölüp aynı
  baytlarla birleştiriyor, yalnız 2. satırın içeriği değişti; karışık satır sonu önceden vardı. Index `i/lf`, commit'lenen blob LF olur; işlem gerekmez.
- **D-4 (kabul):** demo satırındaki "Bu sürüm `lale-duzeltme` dalında" ifadesi `main`'e birleştirme commit'inde kaldırılmalı. Birleştirme
  Ahmet onayında olduğu için şimdi değiştirilmedi.
- **D-5 (bilgi):** `expanduser("~")` başka bir kullanıcıda o kullanıcının profilini gösterir; amaç bu (taşınabilirlik). Bu makinede değer aynı.

### 7.5 Takma ad / kullanıcı adı
Bu turda değişen satırlarda ve dört `F9d-*` dosyasında (`F9d-kontrol.md` dahil) takma ad 0, kullanıcı adı 0 (Python ile sayıldı).
İzlenen takma ad sayımı değişmedi: 6 satır / 3 dosya.

### 7.6 Son kontrol (20:46 – 20:49)
Not: ilk son koşuda betik bu günlükte 2 satır yakaladı (§7.3'teki açılım denemesi tek harfli örnek adla yazılmıştı; çıkış 1). Örnek ad
`<profil>` yer tutucusuyla değiştirildi, koşu yinelendi; aşağıdaki sonuçlar ikinci koşudan.

| Komut | Çıkış |
|---|---|
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** ("izlenen 17 dosyanin ozetleri kayitla ayni") |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** (GEÇER, hepsi okundu, kötüleşen yok) |
| `TAKMA_AD=<takma ad> py -3 planlama/d158/F9d-tarama.py --ozet` | **0**: yazılabilir alanda yerel yol 0; toplam 4 / 4; takma ad izlenen 6 / 3; README 38 satırın 38'i var, uyuşmazlık **0** |
| `py -3 planlama/adim5/maliyet_toplam.py` | 0 (genel 118.666,22; koşullu 124.573,11) |
| `py -3 planlama/d158/F9b-dogrula.py --tarayicisiz` | 0 (SONUC: GECER; dosya yazmaz) |
| `git diff --check` (bu turun 6 dosyası) | 0 |
