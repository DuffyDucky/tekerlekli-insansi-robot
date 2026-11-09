# F4b günlüğü: takma ad temizliği, birinci kısım (P4.5a) + regresyon.py bayrak koruması — 09.11.2026

Ajan A. Brief: `planlama/d158/F4b-brief.md`. FreeCAD kullanılmadı; commit / push / silme / checkout / reset / stash yok.
Bu günlükte takma ad yazılmaz; "takma ad" denir. Takma adı içeren hesap adı ve not deposu adı da yazılmaz.

## 1. Yöntem

- Liste: `git grep -il <takma ad>` (başta 72 izlenen dosya) + izlenmeyen `F1a-kontrol.md`, `F5b-gunluk.md`.
- Değişim betiği (depo dışında, ajan scratchpad'inde): dosya bayt olarak okunur, UTF-8 çözülür, yalnız aşağıdaki dizgeler
  değiştirilir, satır sayısı ve satır sonları (LF / CRLF) korunur.
  - Kişiye atıf → **Ahmet** (ek uyumu: "-'nin" → "Ahmet'in", "-'ye" → "Ahmet'e", "-'de" → "Ahmet'te", HTML'de `&#x27;nin` → `&#x27;in`).
  - Belge başlığı / resmî tanıtım → **Ahmet Yorulmaz**: `Lale-Proje-Ozeti.txt:21` (proje lideri satırı), `README.md:59`
    (bölüm başlığı "Proje çerçevesi"), `planlama/kararlar-2026-10-29.md:1` (belge başlığı).
  - Takma adlı not deposu (vault) adı → "not deposu" / "kişisel not deposu (vault)" (6 satır: `README.md:107`, `dongu.md:28`,
    `kararlar-2026-10-29.md:87`, `siparis-farki-2026-10-29.md:11` ve `:85`, `Y2b-gunluk.md:21`; ayrıca `qled-cerceve-tasarim-notu.md:134`
    ve iki profil dosyasında yol içinde).
  - Kullanıcı adı: `kararlar-2026-10-29.md:87` ssh adresindeki kullanıcı → `<kullanıcı>@lale.local`.
  - Dosya yolu: geçici klasör yolunun takma adı içeren öneki (`C:\Users\...\Temp\claude\<oturum klasörü>\<oturum kimliği>`) → `...`
    (`...\scratchpad\...` kalır). İki profil `.txt` (29 satır) + `qled-cerceve-tasarim-notu.md:134`.
  - İzlenmeyen iki dosyada takma ad yalnız "arama terimi" olarak geçiyordu → "takma ad" (`F1a-kontrol.md:35`, `F5b-gunluk.md:63`).
- Doğrulama: değiştirilen dosyaların `git diff -U0` çıktısında silinen her satırda takma ad var (takma adsız silinen satır 0), eklenen
  satırlarda takma ad 0; her dosyada eklenen = silinen satır sayısı (yalnız ad / tanımlayıcı satırları değişti). Tarih, sayı, karar
  metni ve alıntı içeriği aynen.

## 2. Değişen dosyalar (dosya başına değişen satır)

İzlenen 60 dosya, `git diff --stat`: 195 ekleme, 195 silme. İzlenmeyen 2 dosya, 1'er satır. Toplam **62 dosya, 197 satır**.

| Satır | Dosya |
|---:|---|
| 1 | `Lale-Proje-Ozeti.txt` |
| 8 | `README.md` |
| 1 | `planlama/adim1/P-pi-kafada.md` |
| 1 | `planlama/adim2/M1-kablo-yolu.md` |
| 1 | `planlama/adim3/T-taban-guc-pi.md` |
| 6 | `planlama/adim3/elektrik.md` |
| 2 | `planlama/baski-listesi.md` |
| 18 | `planlama/dongu.md` |
| 6 | `planlama/duzeltme-plani.md` |
| 12 | `planlama/kararlar-2026-10-29.md` |
| 2 | `planlama/maliyet.json` |
| 6 | `planlama/siparis-farki-2026-10-29.md` |
| 1 | `planlama/y2/Y2a-brief.md` |
| 2 | `planlama/y2/Y2a-gunluk.md` |
| 3 | `planlama/y2/Y2a-kontrol.md` |
| 1 | `planlama/y2/Y2b-aku.json` |
| 2 | `planlama/y2/Y2b-aku.py` |
| 1 | `planlama/y2/Y2b-baski.py` |
| 1 | `planlama/y2/Y2b-gunluk.md` |
| 1 | `planlama/y2/Y2b-ivme.py` |
| 3 | `planlama/y2/Y2b-kontrol.md` |
| 1 | `planlama/y2/Y2b-maliyet.py` |
| 2 | `planlama/y3/Y3-brief.md` |
| 1 | `planlama/y3/Y3-gunluk.md` |
| 2 | `planlama/y3/Y3-kontrol.md` |
| 4 | `planlama/yazilim-notu-stowent-170.md` |
| 2 | `planlama/yazilim-plani.md` |
| 1 | `raporlar/aku-secimi/rapor.html` |
| 1 | `raporlar/kaynaklar/03-referans-finansman-destek.md` |
| 1 | `raporlar/kaynaklar/05-fiyat-arastirmasi.md` |
| 1 | `raporlar/kaynaklar/06-aku-secimi.md` |
| 2 | `tasarim/Robot-Tasarim-Demosu.html` |
| 1 | `tasarim/cad/robot_cad.py` |
| 1 | `tasarim/cad/viewer-template.html` |
| 1 | `tasarim/freecad/iskelet/iskelet_montaj.py` |
| 15 | `tasarim/freecad/lale158/ikinci/yavaslik/prof-head-kabuk.txt` |
| 14 | `tasarim/freecad/lale158/ikinci/yavaslik/prof-wt-kabuk.txt` |
| 1 | `tasarim/freecad/lale158/ikinci_ozet.py` |
| 2 | `tasarim/freecad/lale158/kablo_yolu_ekran.py` |
| 1 | `tasarim/freecad/lale158/lale158-regresyon.json` |
| 3 | `tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md` |
| 1 | `tasarim/freecad/lale158/rapor.html` |
| 1 | `tasarim/freecad/montaj/montaj_gorsel.py` |
| 1 | `tasarim/freecad/taslak-170/CATAL-KONTROL-NOTLAR.md` |
| 3 | `tasarim/freecad/taslak-170/CATAL-NOTLAR.md` |
| 1 | `tasarim/freecad/taslak-170/KOL125-NOTLAR.md` |
| 1 | `tasarim/freecad/taslak-170/analiz/hesap.json` |
| 1 | `tasarim/freecad/taslak-170/analiz/onceki-7mm/hesap.json` |
| 1 | `tasarim/freecad/taslak-170/kol-analiz/NOTLAR.md` |
| 1 | `tasarim/freecad/taslak-170/kol-analiz/kol_analiz.py` |
| 7 | `tasarim/freecad/taslak-170/kol-analiz/kol_rapor.py` |
| 5 | `tasarim/freecad/taslak-170/kol-analiz/rapor.html` |
| 2 | `tasarim/freecad/taslak-170/kutle.json` |
| 6 | `tasarim/freecad/taslak-170/rapor.html` |
| 3 | `tasarim/freecad/taslak-170/taslak-analiz.json` |
| 6 | `tasarim/freecad/taslak-170/taslak_ayar.py` |
| 2 | `tasarim/freecad/taslak-170/taslak_hesap.py` |
| 3 | `tasarim/freecad/taslak-170/taslak_parcalar.py` |
| 12 | `tasarim/freecad/taslak-170/taslak_rapor.py` |
| 2 | `tasarim/freecad/taslak-170/taslak_rapor_analiz.py` |
| 1 | `planlama/d158/F1a-kontrol.md` (izlenmiyor) |
| 1 | `planlama/d158/F5b-gunluk.md` (izlenmiyor) |

Örnekleme (`git diff --word-diff`): `(X, 26 Eylül 2026)` → `(Ahmet Yorulmaz, 26 Eylül 2026)`; `X: "pi 4 gb"` → `Ahmet: "pi 4 gb"`;
`X tarafından kabul edildi (29.10)` → `Ahmet tarafından kabul edildi (29.10)`; `ssh <takma ad>@lale.local` → `ssh <kullanıcı>@lale.local`;
profil satırı `...  100.217 C:\Users\...\scratchpad\head\...` → `...  100.217 ...\scratchpad\head\...` (sayı sütunları aynı).

## 3. Betik → çıktı ilişkisi

| Betik (değişen satır) | Çıktı (değişen satır) | FreeCAD? | Ne yapıldı |
|---|---|---|---|
| `planlama/y2/Y2b-aku.py:62,65` | `planlama/y2/Y2b-aku.json:160` | hayır | Betik düzeltildi, **yeniden üretildi**: çıktı elle düzeltilmiş hâliyle bayt bayt aynı (sayısal fark 0). |
| `taslak-170/kol-analiz/kol_rapor.py` (7) | `taslak-170/kol-analiz/rapor.html` (5) | hayır | Betik düzeltildi, **yeniden üretildi**: elle düzeltilmiş hâliyle bayt bayt aynı. |
| `taslak-170/taslak_rapor.py` (12), `taslak_rapor_analiz.py:844,846` | `taslak-170/rapor.html` (6) | hayır | Yeniden üretim denendi: **girdi kayması** (betik `arayuz.py`'yi okuyor; 1,58 m'ye geçişten beri boy zinciri vb. değişmiş, 24 satır sayısal fark, ör. omuz ekseni 955 → 1.270). Yedekten geri yüklendi, çıktı **elle** düzeltildi. taslak-170 arşiv (1,70 m); yeniden üretilmemeli. |
| `taslak-170/taslak_ayar.py:59` (`karar` dizgesi), `taslak_parcalar.py:184,334,343` | `taslak-170/kutle.json:589,608`, `taslak-analiz.json:1819,1829,1844` | **evet** (`taslak_parcalar.py`) | Betik düzeltildi, çıktı **elle**. Arşiv tasarım; P6.1'de yeniden üretilmez (gerekirse FreeCAD koşusunda betikle aynı metni verir). |
| `taslak_ayar.py:59` → `taslak_hesap.py` | `taslak-170/analiz/hesap.json:4000`, `analiz/onceki-7mm/hesap.json:4000` (eski kopya) | hayır (numpy) | Çıktı **elle**: yeniden hesap `arayuz.py` kayması nedeniyle sayıları değiştirir; yapılmadı. |
| `lale158/ikinci_ozet.py:117` | `lale158/lale158-regresyon.json:209` → (`lale158_rapor.py`) `lale158/rapor.html:22` | hayır | Yeniden üretim denendi: **girdi kayması** (F2'nin güncel `carpisma-sonuc.json`'u: tarama koşu kimliği ve aday sayısı değişiyor, 62 satır fark) + betik sonunda Windows konsolunda `UnicodeEncodeError` (print, `↔`). Yedekten geri yüklendi, iki çıktı **elle** düzeltildi. **P6.1'de yeniden üretilecek** (tam taramadan sonra). |
| `planlama/y2/Y2b-maliyet.py:101` | `planlama/maliyet.json` (beyaz notu) | hayır | Betik `maliyet.json`'u yerinde okuyup değiştiriyor (Y2b farkını uygular); yeniden koşmak sonraki elle düzeltmelerin üstüne eski farkı basar. Koşulmadı; çıktı **elle**. `maliyet.json`'daki Pi 4 GB notu betikten değil, elle yazılmış (Y2b/Y3 kararı). |
| `planlama/maliyet.json` + `tasarim/cad/viewer-template.html:245` → `tasarim/cad/demo_uret.py` | `tasarim/Robot-Tasarim-Demosu.html` (2) | hayır | Yeniden üretim denendi: **girdi kayması** (demo, şablon ve maliyetin eski hâlinden üretilmiş; 1.940 satır fark). Yedekten geri yüklendi, **elle** düzeltildi. Not: depo `CLAUDE.md`'si üretilmiş demonun elle düzenlenmemesini istiyor; bu iki satır yalnız ad değişimi. Demo bir sonraki `demo_uret.py` koşusunda aynı metni verir. |
| `tasarim/cad/robot_cad.py:111` | — | — | Yalnız yorum, çıktıya geçmiyor. |
| `planlama/y2/Y2b-ivme.py:14`, `Y2b-baski.py:5` | — | — | Yorum / docstring; `Y2b-ivme.json`, `Y2b-baski.json`'da takma ad yok. |
| (betik yok) cProfile çıktısı | `lale158/ikinci/yavaslik/prof-head-kabuk.txt`, `prof-wt-kabuk.txt` | — | Takma ad betikten değil, koşu ortamının geçici klasör yolundan geliyor; yol öneki elle `...` yapıldı, sayı sütunları aynı. Yeniden üretim gerekmez. |

Yeniden üretim yöntemi: çıktı scratchpad'e yedeklendi, betik koşuldu, `cmp` ile karşılaştırıldı; fark varsa yedek geri kopyalandı
(git checkout kullanılmadı). Yan etki: betiklerin `import`'u `__pycache__` dosyaları üretti (`.gitignore`'da, izlenmiyor).

## 4. Kapsam dışı kalanlar (`git grep -il <takma ad>` sonrası 12 dosya)

| Dosya:satır | Gerekçe |
|---|---|
| `CLAUDE.md:3,4,22` | Depo kökündeki ajan talimat dosyası; karar Ahmet'in (aşağıda karar taslağı). |
| `kod/ortak/eklem_sinirlari.json:111` | `kod/` Efe'nin alanı. Metin `arayuz.py:793`'ten `kod/ortak/eklem_sinirlari_uret.py` ile üretiliyor (FreeCAD gerekmez): P6.1'de `arayuz.py` temizlenip yeniden üretilince düzelir. |
| `tasarim/freecad/arayuz.py:18,22,24,29,73,186,289,333,343,425,491,497,538,552,631,793,963` | Tarama kaynağı (`KAYNAK_SABIT`) + F2'nin alanı (şu an değiştiriyor; satır numaraları 09.11 çalışma kopyası, kayabilir). P6.1. |
| `tasarim/freecad/kabuk/kabuk_lib.py:131` | Tarama kaynağı (`*/*_lib.py`) + F2 alanı (`kabuk/`). P6.1. |
| `tasarim/freecad/kabuk/kabuk_parcalar.py:219,298,729` | Tarama kaynağı (`KAYNAK_SABIT`) + F2 alanı. P6.1. |
| `tasarim/freecad/kafa/kafa10_lib.py:1,50,251,567` | Tarama kaynağı (`*/*_lib.py`). P6.1. |
| `tasarim/freecad/kafa/kafa_lib.py:166` | Tarama kaynağı (`*/*_lib.py`). P6.1. |
| `tasarim/freecad/kafa/kafa_parcalar.py:6` | Tarama kaynağı (`KAYNAK_SABIT`). P6.1. |
| `tasarim/freecad/lale158/kafa-yerlesim/yerlesim_lib.py:4` | Brief'in kapsam dışı listesinde. Not: `carpisma_kos.kaynak_listesi()` yalnız `*_lib.py` ve `*/*_lib.py` desenlerini izliyor; bu dosya iki klasör derinde, md5 listesine girmiyor olabilir. P6.1'de birlikte temizlenir. |
| `tasarim/freecad/omuz/omuz_parcalar.py:327` | Tarama kaynağı + F2 alanı. P6.1. |
| `tasarim/freecad/taban/taban_parcalar.py:34,559` | Tarama kaynağı (`KAYNAK_SABIT`). P6.1. |
| `tasarim/freecad/index.html:49,92` | **Brief dışı karar (aşağıda):** takma ad GitHub hesap adı olarak iki çalışan bağlantının içinde. Yer tutucu koymak bağlantıları kırar; dokunulmadı. |

Kapsam dışı izlenmeyen alanlar (`tubitak-2209b/`, `kvkk/`, `rapor/`, izlenmeyen `raporlar/` dosyaları) açılmadı, taranmadı.

## 5. Karar taslakları (Ahmet; `karar-kuyrugu.md`'ye yazılmadı)

### K-F4b-1: depo kökündeki `CLAUDE.md`

İçerik: yapay zekâ oturumları için bağlam dosyası. Takma ad 3 satırda: satır 3 (robot adının kimin kararı olduğu), satır 4 (proje
sahibinin tanıtımı: mekanik, montaj, kablaj, SolidWorks; yazılımı yapay zekâyla yazıyor), satır 22 (projenin takma adlı not deposu
oturumundan yönetildiği, tercih tarihi 26 Eylül 2026). Dosyanın geri kalanı çalışma kuralları (Türkçe, klasör düzeni, CAD ve maliyet
tek kaynakları, OneDrive uyarısı).

| Seçenek | Etki |
|---|---|
| **a) Olduğu gibi bırak** | Herkese açık depoda 3 satır takma ad kalır; P4.5 kabul ölçütü hiçbir zaman tam temiz olmaz. Ajan davranışı değişmez. |
| **b) Ad değişimi (önerilen)**: satır 3'te "adı Ahmet'in kararı", satır 4'te "Proje sahibi Ahmet Yorulmaz;", satır 22'de "kişisel not deposu (vault) oturumundan yönetiliyor (Ahmet'in tercihi, 26 Eylül 2026)" | Depo temizlenir. Bu klasörde açılan ajanlar sahibine "Ahmet" diye atıf yapar (resmî ad kuralıyla uyumlu). Not deposunun kendi talimatları ayrı dosyada olduğundan oradaki oturumlar etkilenmez. Risk: düşük. |
| c) Dosyayı izlemeden çıkar (`git rm --cached` + `.gitignore`), yerelde kalsın | Herkese açık son sürümde görünmez; ama ekip üyelerinin (Efe) ajanları bu bağlamı kaybeder. Silme sayıldığı için ayrıca onay ister. |

Her üç seçenekte de **git geçmişi** eski metni taşır (tüm 72 dosya için geçerli); geçmişten silmek geçmişi yeniden yazmayı gerektirir
(dongu-158 §2: onaysız yapılmaz). Ayrı karar konusu.

### K-F4b-2: `tasarim/freecad/index.html:49,92` (GitHub hesap adı)

İki bağlantı (`Tek sayfa özet`, `GitHub deposu`) deponun GitHub adresine gidiyor; adresin hesap kısmı takma adı içeriyor. Brief
"hesap adı → nötr yer tutucu" diyor ama yer tutucu bağlantıyı kırar. Deponun `origin` adresi ve Pages adresi de aynı hesap adını taşıyor;
yani bu iki satır, depo adresinin kendisinden fazlasını açığa çıkarmıyor. Bu dosyanın yayındaki hâli `main`'de (Pages); bu dalda
değiştirmek siteyi birleştirmeye kadar etkilemez.

| Seçenek | Etki |
|---|---|
| **a) Bırak (önerilen, şimdilik)** | Bağlantılar çalışır; hesap adı zaten depo/Pages adresinde. Kabul listesinde gerekçeli kapsam dışı. |
| b) Göreli bağlantı (`OZET.md`, `./`) | Hesap adı kalkar; ama Pages'te `.md` dosyası Jekyll ile işlenirse `OZET.md` bağlantısı 404 olabilir, "Kaynak dosyalar" bağlantısı GitHub kod görünümü yerine site klasörüne gider. Denenmeli. |
| c) Yer tutucu | Bağlantılar kırılır. Önerilmez. |
| d) Depoyu takma ad içermeyen bir hesaba / organizasyona taşı ya da hesap adını değiştir | Tek kalıcı çözüm; `origin`, Pages adresi ve paylaşılmış bağlantılar değişir (GitHub depo web / git bağlantılarını yönlendirir; Pages adresi yönlendirilmez, paylaşılmış site linkleri kırılır). Ahmet'in kararı. |

## 6. `planlama/d158/regresyon.py` bayrak koruması

Değişiklik (+14 / −0 satır): `main()` başında, ölçümden ve dosya okumadan önce bayrak denetimi.
- `--help` / `-h` → modül docstring'i (kullanım metni) basılır, çıkış **0**, hiçbir dosyaya yazılmaz.
- `--yazma` dışındaki her argüman (tanımsız bayrak ya da konumsal argüman) → stderr'e "Hata: tanımsız argüman: ..." , çıkış **2**,
  ölçülmez, yazılmaz. (`--yazma --xyz` de hata.)
- Bayraksız normal mod ve `--yazma` mantığı değişmedi. Docstring'e iki satır kullanım eklendi; stderr de UTF-8'e ayarlandı.

Test (normal mod koşulmadı):

| Komut | Çıkış | regresyon.json sha256 | regresyon-son-kosu.json sha256 |
|---|---:|---|---|
| (önce) | — | `e6f288ff5b7ba0a1320fe5defdaa215e500ddb356799988a092c1931b9b71969` | `ced8869015652586a3cda90b6ce68fde8b2a2c4c1141c9a33f14d517acc7abda` |
| `--help` | 0 | aynı | aynı |
| `-h` | 0 | aynı | aynı |
| `--xyz` | 2 | aynı | aynı |
| `--yazma --xyz` | 2 | aynı | aynı |
| `x` (konumsal) | 2 | aynı | aynı |
| `--yazma` | 0 (GEÇER, ölçtü, yazmadı) | aynı | aynı |

## 7. Başka soyad bulgusu

Değiştirilen 197 satırda başka öğrenci / danışman soyadı yok ("hoca", "danışman", "Dr.", "Prof." geçen satırlarda isim yok). Ayrı bir
depo geneli soyad taraması yapılmadı (brief kapsamı değil).

## 8. Açık kalanlar

1. P6.1: tarama kaynaklarındaki takma ad satırları (bölüm 4 tablosu, 10 dosya), ardından `eklem_sinirlari_uret.py` ve
   `ikinci_ozet.py` + `lale158_rapor.py` yeniden üretimi.
2. K-F4b-1 (`CLAUDE.md`) ve K-F4b-2 (hesap adı) Ahmet'in kararı; git geçmişindeki eski metin ayrı karar.
3. `ikinci_ozet.py` sonunda Windows konsolunda `UnicodeEncodeError` (print, `↔`); JSON yazımından sonra olduğu için çıktıyı etkilemiyor.
   `PYTHONIOENCODING=utf-8` ile koşulmalı ya da `stdout.reconfigure` eklenmeli (brief dışı, dokunulmadı).
4. `tasarim/Robot-Tasarim-Demosu.html` şablon ve maliyetin güncel hâlinden yeniden üretilmemiş (1.940 satır kayma); ayrı iş.
5. `yerlesim_lib.py` çakışma md5 listesine girmiyor olabilir (bölüm 4); P6.1 öncesi kontrol edilmeli.
