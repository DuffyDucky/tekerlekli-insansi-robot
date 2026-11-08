# F0 bağımsız kontrol (ajan B) — 08.11.2026

Brief: `planlama/d158/F0-brief.md`. Plan: `planlama/dongu-158.md`. Dal `lale-duzeltme`, HEAD `d26c7e7`.
Ajan A'nın günlüğü (`F0-gunluk.md`) kanıt olarak kullanılmadı; her iddia kaynaktan, `git` çıktısından ve JSON'dan yeniden ölçüldü.
Proje dosyalarına yazılmadı: regresyon betiği depoda yalnız `--yazma` ile koşuldu (`regresyon.json` değişmedi, mtime 19:55:40),
kötüleştirme denemeleri scratchpad'teki kopyada yapıldı. Commit, silme, checkout/reset/stash yok.

| Paket | Karar |
|---|---|
| P0.1 Sınıflandırma | **KOŞULLU** |
| P0.2 Karar kuyruğu | **KOŞULLU** |
| P0.3 Regresyon betiği | **KOŞULLU** |

---

## P0.1 — KOŞULLU

### Doğrulananlar
- **Yol kapsamı tam.** `git status --porcelain=v1 -uall` şimdi 335 satır = 25 ` M` + 310 `??` (251'i `tubitak-2209b/`).
  A'nın işi 5 yeni dosya ekledi (`F0-gunluk.md`, `P0.1-siniflandirma.md`, `karar-kuyrugu.md`, `regresyon.py`, `regresyon.json`);
  çıkarınca belgedeki 330 = 25 + 305 (`P0.1-siniflandirma.md:6`) tutuyor. `planlama/d158/__pycache__/` `.gitignore:1` ile yok sayılıyor.
- **25 değişmiş dosyanın hepsi** tabloda (`P0.1-siniflandirma.md:31-46`); `git diff --numstat` sayıları belgeyle aynı
  (ör. `rehber_metin.py` 328/28, `elektrik.md` 106/67, `Robot-Tasarim-Demosu.html` 300/0).
- **`git add` listeleri:** G1–G9'daki 42 yolun 41'i `git status`'ta birebir var; 42.'si `.gitignore` (G9, bilinçli yeni değişiklik).
  **İki gruba düşen yol yok** (sıralı listede `uniq -d` boş). Hiçbir gruba girmeyen tüm yollar (`kvkk/` 16, `rapor/` 20,
  `KY/kaynak/` 5, `tasarim/solidworks/*.step` 2, `tubitak-2209b/` 251) G9'daki `.gitignore` satırlarıyla örtülüyor (`P0.1-siniflandirma.md:194-205`).
  `tubitak-2209b/` dökümü (kök 12 = 11 + kilit dosyası, `taslak/` 159, `ornekler/` 37, `resmi/` 25, `teslim/` 12, `malzeme-listesi/` 6) doğru.
- **Boyutlar:** `kvkk` 3,1 MB, `rapor` 11 MB, `tubitak-2209b` 102 MB, `KY/kaynak` 3,0 MB, `Lale-1650-duz.step` 28.301.537 bayt: belgeyle aynı.
- **G1–G5'e yasaklı yol sızmamış:** `tubitak-2209b/`, `kvkk/`, `rapor/`, `kafa-yerlesim/kaynak/`, `.step` ve büyük ikili yok.
  En büyük dosya `tasarim/Robot-Tasarim-Demosu.html` (898 KB; HEAD'de zaten 877 KB, izlenen dosya).
- **G1–G5 kişisel veri taraması** (14 dosyanın tamamı ve diff'te eklenen satırlar):
  - Ekip üyelerinin ve danışmanın soyadları (`rapor/Lale-tek-sayfa.html` "isimler" listesinden alındı): **0 eşleşme**.
  - E-posta: 0. Telefon: yalnız JSON/base64 içindeki sayılar (`Y2b-baski.json:1252`, demo `:268`), kişisel değil. TC kimlik deseni: 0.
  - Eklenen satırlarda geçen adlar: yalnız "Efe" (ad; HEAD'de 13 izlenen dosyada zaten var) ve takma ad (HEAD'de 72 dosyada; P4.5 kapsamı).
  - **Sonuç: G1–G5'te engelleyici gizlilik sorunu yok.** Küçük notlar aşağıda (madde 4, 5).
- **`rehber_metin.py` tespiti doğru.** `ADIM` sözlüğü (AST ile sayıldı): HEAD 29 anahtar, çalışma kopyası 49. C1 ve sonrası
  HEAD'de 12 (C1 D1 E1 E3 K2 F1 F2 F3 F4 G1 H1 F5), şimdi **32**: iddia doğru. 49 anahtar, `planlama/adim4/M6-montaj-sirasi.md:92-141`
  "Kod" sütunundaki 49 kodla sıra dahil aynı. `M6_BAYRAK_ACIK = False` `rehber_metin.py:471`, `kablo_kapisi` `:477` (belge 472/478 diyor, ±1).
  Dosya zamanları (04.11 01:19–01:26) ve `R-gunluk.md:13,15,17,22,26-31,86` alıntıları doğru. `tubitak-2209b/BAGLAM.md:223`
  alıntısı ("gece rapor, QLED CAD, montaj sırası ve rehber sürer") o satırda var.
- Sarkan atıflar doğru: `arayuz.py:328,347,531` → `raporlar/`; `arayuz.py:988,992`, `kafa10_lib.py:50,78` → `KY/kaynak/`.

### Bulgular
- **B1.1 Yanlış iddia:** `P0.1-siniflandirma.md:67` "izlenen dosyalarda bu adlar yok (`git ls-files` grep 0)". Ölçüm: "Ahmet Yorulmaz"
  HEAD'de 6 izlenen dosyada var (`KY/secenekler.md:8,332`, `KY/uygulama-notu.md:3,90,134`, `KY/uygulama_ivme.py:14`,
  `KY/uygulama_metin.py:89`, `KY/uygulama_rapor.py:192,202`, `KY/rapor.html:10`). Doğrusu: diğer üç öğrencinin soyadı ve danışmanın adı izlenen dosyalarda 0.
  K20'nin dışlama gerekçesi yine geçerli, yalnız cümle düzeltilmeli.
- **B1.2 Alıntı kaynağı:** `P0.1-siniflandirma.md:64` "iç dosya" için `saglayici-secimi.md:3` gösteriliyor; o satırda bu ifade yok
  ("Hazırlayan: ... asistan taslağı"). İfade yalnız `kvkk/fiyatlar.md:3`'te ("Bu dosya iç dosyadır").
- **B1.3 G1 commit mesajı eksik:** `rehber_metin.py` diff'i C1 öncesine de dokunuyor: `HAZIRLIK` (50 → 65 parça, perçin pensesi
  maddesi, kablo notu), `A3` (adım no 14 → 24), `B1a`, `B5a`, `K1` (AST karşılaştırması: değişen eski anahtarlar
  A3, B1a, B5a, K1, C1 … F5). Mesaj ve `P0.1-siniflandirma.md:21-22` yalnız "C1 sonrası 32 adım + K1" diyor.
  Ayrıca "31'i diff'te yeni `dict`" metinsel; anlamca **20 yeni anahtar** (D1a D1b D1c E1a E2a E2b E2c E2 E3a E4 G0 G2 G3 G4 H0a–H0f),
  11 tek satırlık eski kayıt yeniden yazılmış, K2 güncellenmiş.
- **B1.4 G2'de 2209-B dosya adları açık depoya giriyor:** `elektrik.md` diff'i `tubitak-2209b/BAGLAM.md` ve
  `tubitak-2209b/malzeme-listesi/...-v4.xlsx` adlarını iki yerde ekliyor (`elektrik.md:10` ve `:461`). İçerik değil, yalnız yol;
  P0.1 yalnız `:10`'u yazıyor (`P0.1-siniflandirma.md:79`). Engelleyici değil; `:461` de listeye eklenmeli.
- **B1.5 G4'te yerel hafıza yolları:** `raporlar/11-6-inc-gogus-ekrani-sigma.md:40,59` depo dışı kasanın arşiv dosya adlarını
  (`Arşiv/Threads-2026-10.md`, `Arşiv/Last-Session-2026-10.md`) ve takma adı içeriyor. Bu dosyalar açık depoya **ilk kez** giriyor;
  P4.5'te temizlense de geçmişte kalır. Engelleyici değil; Ahmet'e "commit öncesi temizle / sonra P4.5" seçeneği olarak sunulmalı.
- **B1.6 Satır atıfları kaymış:** `dongu-158.md` A'dan sonra (20:03:57) düzenlendi; atıflar bir satır geride:
  `P0.1-siniflandirma.md:72` `:38` → `:39`; `:229` `:53` → `:54`; `:231` `:34` → `:35`.
- G8 listesine `F0-kontrol.md` eklenmeli (belge bunu zaten söylüyor, `P0.1-siniflandirma.md:182`).

---

## P0.2 — KOŞULLU

### Doğrulananlar
- **Takma ad belgede 0 kez** (`grep -ci` 0); kişi adı "Ahmet" olarak yazılmış. `P0.1-siniflandirma.md` ve `regresyon.py/json`'da da 0.
- **Kapanan 5 madde kaynakta kapalı:**
  - **K8:** `planlama/y3/Y3-kontrol.md:109` "KARAR 29.10: (a) açıklık ±32 kalır; kutu alınınca ölçülür, uçtaki iki yuva yedek sigorta için
    ayrılır". Commit `f95f96b` mesajı "H1 uç yuvalar yedek". Doğru.
  - **K5:** soru `qled-cerceve-tasarim-notu.md:147`; Ahmet'in B + R1 seçimi `KY/uygulama-notu.md:3`, `KY/secenekler.md:1`; hub gövdede,
    7 cıvatalı kapak (`KY/secenekler.md:304`). Doğru. Not: ses kartı hâlâ kafada sol duvarda (`KY/secenekler.md:12,30`); servisi
    seçimle örtük kabul edilmiş sayılır, ayrı bir onay kaydı yok. Kapanış geçerli, belgede bu cümle eklenebilir.
  - **K15:** `dongu-158.md:43-44` "uzun taramalar (omuz, tam model) sırası gelince, saat fark etmeksizin koşar". Doğru (satır 44, bkz. B2.1).
  - **K16:** `KY/secenekler.md:8`; `kafa10_lib.py:402` "MAX98357A cikti"; `KY/uygulama-notu.md:57`. Doğru.
  - **K17:** `KY/secenekler.md:1` "Seçim: B + R1, 05.11.2026, uygulandı". Doğru.
- **Rastgele 20+ atıf kontrolü — doğru çıkanlar:** `Y3-kontrol.md:41-42,107-109,115`; `kararlar-2026-10-29.md:23-24`;
  `KY/uygulama-notu.md:9,26,58,59,64,98,106-112,114,131-134,146-155`; `KY/secenekler.md:16-19,240,243,253,275,281,286,299,304,330,332-341`;
  `elektrik.md:19,24,25,55,58,60,316`; `qled-cerceve-tasarim-notu.md:19,114-119,143-147`; `lale_dongu.FCMacro:216-226`;
  `Y2b-brief.md:15`, `Y3-brief.md:25`. JSON sayıları: K3'teki 9 sayı (`uygulama-ivme.json izgara_yuk_{0,100,500}g`), K23
  (`Y2b-ivme.json kutle_g` 25.467,9; HEAD 24.796,1; `ev.kutle_g` 25.910,6), K18–K22 boyutları: hepsi aynı.
- **Açık 18 maddenin hepsinde ≥ 2 seçenek ve varsayılan var.** Kaynaklarda kuyruğa girmesi gereken başka karar bulamadım
  (`uygulama-notu.md:146-155` 8 madde, `secenekler.md:332-341` 8 soru, `qled…:143-147` 3 soru, `Y3-kontrol.md:106-115`: hepsi K1–K23'te
  ya da "Karar değil, iş" bölümünde).

### Bulgular
- **B2.1 `dongu-158.md` atıfları bir satır kaymış** (dosya A'dan sonra düzenlendi; atıf bugünkü dosyada yanlış satırı gösteriyor):
  `karar-kuyrugu.md:3` `:33-34` → `:34-35`; `:51` `:24` → `:25`; `:52` `:135` → `:136`; `:53` `:87` → `:88`; `:54` `:135,147` → `:136,150`;
  `:58` `:63` → `:64`; `:62` `:136` → `:137`; `:74` `:137` → `:138`; `:83` `:138` → `:139`; `:100` `:139` → `:140`; `:107` `:23` → `:24`;
  `:108` `:141` → `:142`; `:109` `:38` → `:39`; `:124` `:143` → `:144`; `:133` `:62` → `:63`; `:176` `:43` → `:44`; `:194` `:38` → `:39`;
  `:195` `:53` → `:54`. Öneri: satır yerine bölüm + madde kodu da yaz (ör. "dongu-158.md §4 K1"), bir sonraki düzenlemede kırılmasın.
- **B2.2 K20 yanlış iddia** (`karar-kuyrugu.md:208-210`): "izlenen dosyalarda bu adlar yok" ve "adlar açık depoya ilk kez girer".
  "Ahmet Yorulmaz" zaten 6 izlenen dosyada (bkz. B1.1). Doğrusu: diğer üç öğrencinin soyadı ve danışmanın adı ilk kez girer.
- **B2.3 K19 alıntı kaynağı** (`karar-kuyrugu.md:200`): "iç dosya" yalnız `kvkk/fiyatlar.md:3`'te; `saglayici-secimi.md:3`'te yok (bkz. B1.2).
- **B2.4 K13 sayısal etki zayıf** (`karar-kuyrugu.md:158`): b seçeneği için yalnız "hesaplanmadı". Brief her maddede sayısal etki istiyor;
  uydurma olmasın diye en azından bilinen sayılar yazılabilir (12 LED, dizi kabuğun 2,5 mm altında: `KY/secenekler.md:299`;
  ReSpeaker Ø70: `yerlesim_lib.py:54`). Engelleyici değil.
- **B2.5 Yan bulgu (orkestratöre):** P1.4'ün sayısı eski. `dongu-158.md:65` "SY8205 kartından geçiyor (249,7 mm³)"; bugün 0
  (`KY/uygulama-notu.md:27` "249,7 | 0 | 0,00"; `uygulama-olcum.json kablo_sy8205."USB dokunmatik".sy8205_kesisim_mm3` = 0).
  P1.2 gibi P1.4 de B + R1 ile büyük ölçüde yapılmış. P1.4'ün kabul ölçütü `kablo_tup_cakisma 0` ise bugün hâlâ sıfır değil
  (`lale158-kontrol.json kablo_tup_cakisma`: HDMI × göğüs ekranı 897,1; 12 V × göğüs ekranı 617,3; USB dokunmatik × göğüs ekranı 167,6 mm³;
  şema uç temasları olabilir). P1.4 brief'i bu ikisini ayırmalı. A'nın hatası değil, bilgi.

---

## P0.3 — KOŞULLU

### Doğrulananlar
- **Koşu:** `py -3 planlama/d158/regresyon.py --yazma` → çıkış **0**, 10 değer "aynı", her satırda dosya : anahtar yolu yazıyor.
- **10 değer JSON'dan elle okundu, betikle aynı:**

| Değer | JSON'da | Kaynak (dosya : anahtar) | Not |
|---|---|---|---|
| Boy | 1580,0 | `lale158/lale158-kontrol.json : toplam_boy_mm` | |
| Kafa içi çakışma | `[]` → 0 | `kafa/kafa-analiz.json : statik` | `KY/uygulama-notu.md:38` aynı kaynağı gösteriyor |
| Kabuk içi | `[]` → 0 | `kabuk/kabuk-analiz.json : cakisma` | `KY/uygulama-notu.md:40` |
| Kabuk × iskelet | `[]` → 0 | `kabuk/kabuk-analiz.json : iskelet_cakisma` | |
| Ev pozu | `[]` → 0 | `carpisma-sonuc.json : ev_pozu_cakisma` | `tek_kosu: false` (bkz. B3.4) |
| Rampa yüksüz | 1,517 | `KY/uygulama-ivme.json : izgara_yuk_0g.a_sinir_pay15` | rampa5_ileri 1,689 / **geri 1,517** / yan 2,033 → en küçük doğru |
| Tilt | 3,64 | `kafa/kafa-analiz.json : tork.tilt.pay_tilt15` | `pay`/`pay_iki_hane` 3,65; ±15 için doğru anahtar `pay_tilt15` (`KY/uygulama-notu.md:21`) |
| Pan | 2,21 | `kafa/kafa-analiz.json : tork.pan.pay_iki_hane` | `pay` 2,2; plan 2,21 diyor (`KY/uygulama-notu.md:23`) |
| Mik-hoparlör | 574,3 | `KY/uygulama-olcum.json : mic_hoparlor.poz_min_mm` | `ev_min_mm` 595,7 ayrı; plan 574,3 (tüm pozlar) |
| SY8205 × USB | 0 | `KY/uygulama-olcum.json` | `kablo_sy8205` **10** + `kafa_ici_qled_kablo` **3** = **13 kablo**, hepsi 0,0 |

- **"Rampa en küçük" mantığı doğru:** `rampa5_*` anahtarlarının en küçüğü alınıyor; yön "büyük iyi", eşik 1,5. Denemede `rampa5_yan` 1,40
  yapılınca en küçük değişti ve çıkış 1 (aşağıda T3).
- **Kötüleştirme denemeleri** (scratchpad kopyası: 6 kaynak JSON + betik + `regresyon.json`, betiğin `KOK`'u kendi konumundan
  türediği için betik değiştirilmeden; `--yazma` ile):

| # | Değişiklik | Beklenen | Çıkış |
|---|---|---|---|
| T0 | yok | 0 | 0 |
| T1 | tilt 3,64 → 3,50 (eşik üstü) | 1 | **1** (KÖTÜLEŞTİ) |
| T2 | pan 2,21 → 1,9 | 1 | **1** (+ eşik) |
| T3 | `rampa5_yan` 2,033 → 1,40 | 1 | **1** (+ eşik) |
| T4 | `ev_pozu_cakisma` +1 çift | 1 | **1** |
| T5 | kafa `statik` +1 | 1 | **1** |
| T6 | SY8205 "Dizi USB" 0 → 0,5 | 1 | **1** |
| T7 | mik-hoparlör 574,3 → 450 | 1 | **1** |
| T8 | boy 1580 → 1590 | 1 | **1** |
| T9 | **boy 1580 → 1570** | 1 | **0 ("iyileşti")** |
| T10 | kabuk × iskelet +1 | 1 | **1** |
| T11 | `pay_tilt15` anahtarı silindi | 2 | **2** ("kaynak yok", uydurmuyor) |
| T12 | `carpisma-sonuc.json` yok | 2 | **2** |

- Yalnız standart kütüphane (`datetime, hashlib, json, os, sys`). Kaynak dosyaların sha256 ilk 12 hanesi kayda giriyor.

### Bulgular
- **B3.1 Boy tek yönlü kontrol ediliyor** (`regresyon.py:105-106` `yon="kucuk_iyi", esik=1580.0`). Korunan değer "boy 1.580,0 mm"
  (`dongu-158.md:24`), üst sınır değil sabit hedef; 1.570'e düşen boy "iyileşti" sayılıp çıkış 0 veriyor (T9). Boy için iki yönlü
  ("eşit", |Δ| ≤ tolerans) kontrol gerekli.
- **B3.2 Başarısız koşu taban çizgisini eziyor.** `--yazma` olmadan koşunca kötüleşen değer de `regresyon.json`'a "önceki" olarak
  yazılıyor (`regresyon.py:235-249`, çıkış koduna bakmadan). Deneme: tilt 3,50 ile 1. koşu çıkış 1, aynı veriyle 2. koşu **çıkış 0**
  ("aynı", 3,50 = 3,50). Eşik üstündeki bir kötüleşme ikinci koşuda kaybolur; döngüde C ajanı betiği iki kez koşarsa paket yanlışlıkla geçer.
  Öneri: karşılaştırma sabit bir "kabul edilmiş taban" ile yapılsın (ör. `taban` alanı yalnız çıkış 0'da ya da `--kabul` bayrağıyla
  güncellensin); çıkış ≠ 0 iken taban değişmesin.
- **B3.3 Satır atfı kaymış:** `regresyon.py:102-103` `dongu-158.md:22-24`, `:23-24` → bugün `:23-25` / `:24-25`.
- **B3.4 Bilgi (engelleyici değil):** `carpisma-sonuc.json` `tek_kosu: false`, `birlestirme_notu` "EKSIK / KARISIK birlestirme" (omuz bölümü
  03.11'den); ayrıca `ev_pozu_cakisma_s2_0` 4 çift içeriyor (S2 0° FCStd yerleşimi; `ev_pozu_poz.not_` "yazilim ev pozu (K6)").
  Betik doğru anahtarı okuyor, ama `tek_kosu` değerini kayda yazması P2.2/P6.1'de "ev pozu 0" sayısının hangi koşudan geldiğini gösterir.
- **B3.5 Ad:** "SY8205 × USB" 13 kablonun tamamını topluyor (HDMI, 12 V, hoparlör dahil). Üst küme olduğu için güvenli; etiket
  "SY8205 × kafa kabloları (USB dahil)" olabilir.

---

## Düzeltme listesi (ajan A'ya)

1. `P0.1-siniflandirma.md:67` ve `karar-kuyrugu.md:208-210` (K20): "izlenen dosyalarda bu adlar yok" cümlesini düzelt. "Ahmet Yorulmaz"
   6 izlenen dosyada var (`KY/secenekler.md:8`, `KY/uygulama-notu.md:3` …); ilk kez girecek olan diğer üç öğrencinin soyadı ve danışmanın adı.
   Varsayılan gerekçesini buna göre yaz. **Düzeltmeyi yazarken bu adları belgeye yazma.**
2. `P0.1-siniflandirma.md:64` ve `karar-kuyrugu.md:200` (K19): "iç dosya" kaynağı yalnız `kvkk/fiyatlar.md:3`; `saglayici-secimi.md:3` atfını kaldır ya da doğru ifadeyle değiştir.
3. G1 commit mesajı ve `P0.1-siniflandirma.md` §1: `rehber_metin.py` diff'inin C1 öncesini de değiştirdiğini yaz (HAZIRLIK 50 → 65 parça
   ve perçin pensesi; A3 adım no 14 → 24; B1a, B5a, K1). "31'i yeni dict" yerine "20 yeni adım, 11 adım yeniden yazıldı, K2 güncellendi".
   `rehber_metin.py:472,478` → `:471,477`.
4. `P0.1-siniflandirma.md:79`: `elektrik.md:461`'deki `tubitak-2209b/` atfını da listeye ekle; G2 mesajına "2209-B dosya adlarına atıf var,
   K18 a seçilirse temiz klonda boşa düşer" notu.
5. `raporlar/11-6-inc-gogus-ekrani-sigma.md:40,59` (yerel kasa arşiv yolları + takma ad, dosya açık depoya ilk kez giriyor): P0.1 §3'te
   bunu ayrı bir uyarı olarak yaz ve karar kuyruğuna "G4 öncesi bu iki satır temizlensin mi / P4.5'e mi kalsın" maddesi (K24) ekle
   (seçenekler + etki: temizlemezse satırlar git geçmişinde kalır).
6. `dongu-158.md` satır atıflarını güncelle: `P0.1-siniflandirma.md:72,229,231`, `karar-kuyrugu.md` 18 yer (liste B2.1'de),
   `regresyon.py:102-103`. Mümkünse satır yanına bölüm/kod yaz (ör. "§4 K1").
7. `regresyon.py` boy kontrolünü iki yönlü yap: 1.580,0'dan her sapma (tolerans içinde değilse) KÖTÜLEŞTİ ve eşik dışı, çıkış 1.
   T9 (1.570) ile dene.
8. `regresyon.py` taban çizgisi: çıkış ≠ 0 iken önceki kaydı (karşılaştırma tabanını) ezme; sabit "kabul edilmiş taban" tut. Deneme:
   kötüleşmiş veriyle iki ardışık yazmalı koşu, ikisi de çıkış 1 vermeli.
9. (İsteğe bağlı) `regresyon.py`: `carpisma-sonuc.json tek_kosu` değerini bilgi olarak kayda yaz; SY8205 etiketini netleştir.
10. (İsteğe bağlı) K13'e bilinen sayıları ekle; K5'e "ses kartı kafada sol duvarda kaldı, B seçimiyle kabul" cümlesi.
11. Düzeltmelerden sonra regresyonu yeniden koş ve `F0-gunluk.md`'ye çıkış kodunu yaz; G8 `git add` listesine `planlama/d158/F0-kontrol.md` ekle.

Orkestratöre bilgi (A'nın işi değil): `dongu-158.md:65` P1.4 sayısı eski (249,7 → bugün 0, `KY/uygulama-notu.md:27`); P1.4 brief'i
yazılmadan önce yeniden ölçülmeli (B2.5).

## G1–G5 gizlilik özeti
Engelleyici sorun **yok**: kişi soyadı (Ahmet Yorulmaz dışında), e-posta, telefon, `tubitak-2209b/`, `kvkk/`, `rapor/`, satıcı dosyası
ya da büyük ikili G1–G5'e girmiyor. Küçük notlar: G2 2209-B dosya **adlarına** atıf ekliyor (madde 4); G4'te iki satır yerel hafıza
yolu ve takma ad içeriyor (madde 5). G1–G5, madde 3'teki mesaj düzeltmesiyle commit'lenebilir; madde 5 Ahmet'e sorulursa G4 beklemeli.

## Genel karar: **KOŞULLU**
Üç paketin çıktısı büyük ölçüde doğru ve ölçülebilir: yol kapsamı tam, gruplar çakışmıyor, rehber sayısı doğru, kapanan 5 karar kaynakta
kapalı, 10 korunan değer JSON'la birebir, kötüleşme çıkış 1 veriyor. Düzeltme turu gerekli: iki yanlış olgu cümlesi (madde 1, 2),
eksik commit mesajı (3), kaymış atıflar (6) ve regresyon betiğinde iki mantık açığı (7: boy kısalması geçiyor; 8: ikinci koşu
kötüleşmeyi siliyor). Madde 7 ve 8 düzelmeden P0.3 sonraki paketlerin regresyon kapısı olarak kullanılmamalı.

---

# Yeniden kontrol 1 (ajan B, 08.11.2026, düzeltme turu 1 sonrası)

A'nın "Düzeltme turu 1" tablosuna (`F0-gunluk.md:71-112`) güvenilmedi; her madde dosyadan, `grep`/AST ile ve scratchpad kopyasında
koşarak yeniden ölçüldü. Depoda betik yalnız `--yazma` ile koşuldu; `regresyon.json` ve `lale158-kontrol.json` sha256 önce/sonra aynı.

| Paket | Yeni karar |
|---|---|
| P0.1 | **GEÇER** (commit adımına 1 not) |
| P0.2 | **GEÇER** (tek satırlık atıf düzeltmesiyle; yeni kontrol turu gerekmez) |
| P0.3 | **GEÇER** |

## Madde madde
1. **Ad iddiası — yapıldı.** `P0.1-siniflandirma.md:72`, `karar-kuyrugu.md:212-215` artık "Ahmet'in adı HEAD'de 6 izlenen dosyada; diğer
   üç öğrencinin soyadı ve danışmanın adı 0" diyor (ölçümle aynı). `planlama/d158/` altındaki bütün `.md/.py/.json` dosyalarında diğer
   öğrencilerin soyadı ya da danışmanın adı: **0 eşleşme**.
2. **"İç dosya" kaynağı — yapıldı** (`P0.1-siniflandirma.md:69`, `karar-kuyrugu.md:204`: yalnız `kvkk/fiyatlar.md:3`).
3. **G1 mesajı ve §1 — yapıldı.** 20 yeni adım / 11 yeniden yazılan / K2, HAZIRLIK, A3, B1a, B5a yazıldı (`P0.1-siniflandirma.md:22-25,109-117`).
   **Satır atfı: A haklı, ben yanılmışım.** `grep -n` ve Python `split('\n')` ikisi de `M6_BAYRAK_ACIK = False` → **472**,
   `def kablo_kapisi` → **478** veriyor (dosyada CR yok). İlk kontroldeki "471/477" düzeltmesi (B1.3, madde 3) geri alınır; 472/478 doğru.
4. **`elektrik.md:461` — yapıldı** (`P0.1-siniflandirma.md:84`, G2 mesajı `:129`).
5. **K24 — doğru açılmış** (`karar-kuyrugu.md:39` özet satırı, `:247-255`): soru, iki seçenek (a G4 öncesi temizle / b P4.5'e bırak),
   sayısal etki (1 dosya 2 satır; b'de geçmişte kalır, `dongu-158.md:36-37` geçmiş yeniden yazılmaz), varsayılan a, bloke G4, durum açık.
   G4 K24'e bağlandı (`P0.1-siniflandirma.md:91-93,146-147`). Sayım "Açık 19, kapandı 5, toplam 24" (`karar-kuyrugu.md:41`) tutuyor.
6. **`dongu-158.md` atıfları — 24 atfın 23'ü doğru satırı gösteriyor** (her biri satır içeriğiyle karşılaştırıldı). **Kalan 1:**
   `karar-kuyrugu.md:102` `dongu-158.md:140, §4 K6` → satır 140 K5; K6 **141**. Bu hata benim B2.1 listemden geldi (`:139 → :140`
   yazmışım, doğrusu `:141`). Bölüm/kod etiketi "§4 K6" doğru olduğu için okur yanılmaz; tek satır düzeltme.
7. **Boy iki yönlü — yapıldı ve doğrulandı.** `regresyon.py:114` `yon="esit", esik=1580.0, tol=0.05`; `_esik_icinde` (`:175-180`).
8. **Taban ezilmiyor — yapıldı ve doğrulandı.** Taban yalnız çıkış 0'da yazılıyor (`regresyon.py:276-291`); her koşu `regresyon-son-kosu.json`'a.
   Scratchpad kopyası (6 kaynak JSON + bugünkü betik + bugünkü taban), her senaryoda **art arda iki yazmalı koşu**:

   | Senaryo | Çıkış | Taban sha256 (önce → 1. → 2.) | Son koşu `boy_mm` |
   |---|---|---|---|
   | Değişiklik yok | 0, 0 | güncellendi (beklenen) | aynı |
   | **Boy 1.570** | **1, 1** | `834ce74e38cb` → aynı → aynı | KÖTÜLEŞTİ |
   | **Boy 1.590** | **1, 1** | aynı → aynı | KÖTÜLEŞTİ |
   | Boy 1.580,04 (tolerans içi) | 0, 0 | güncellendi | aynı |
   | Boy 1.579,94 (tolerans dışı) | 1, 1 | aynı → aynı | KÖTÜLEŞTİ |
   | Tilt 3,50 | 1, 1 | aynı → aynı | (tilt_payi kötüleşen) |
   | `carpisma-sonuc.json` yok | 2, 2 | aynı → aynı | — |

   Depoda `py -3 planlama/d158/regresyon.py --yazma`: çıkış **0**, 10 değer "aynı". Taban `regresyon.json` 20:15:20, `cikis_kodu` 0, boy `esit ± 0,05`.
9. **`tek_kosu` bilgisi — yapıldı.** `regresyon-son-kosu.json bilgi.carpisma_sonuc`: `tek_kosu` false, koşular 20261103-215611 ve 20261105-185759.
10. **K13 ve K5 — yapıldı** (`karar-kuyrugu.md:160-162`; K5 cümlesi).
11. **G8 listesi — `F0-kontrol.md` eklendi** (`P0.1-siniflandirma.md:194`).

## Uygulayıcının notu: `kablo_tup_cakisma`
Doğrulandı (`tasarim/freecad/lale158/lale158-kontrol.json`, sha `d8a141db0960`, değişmemiş): `HDMI` × göğüs ekranı **897,1**, `12 V` × göğüs
ekranı **617,3**, `USB dokunmatik` × göğüs ekranı **167,6** mm³ (HDMI'de ayrıca boyun mili 15,1, servo yuvası 1,7). SY8205 kesişimi ise 0.
Bilgi; F0 kararını etkilemez, P1.4 brief'ine girdi.

## Kalanlar
- **P0.2, 1 satır:** `karar-kuyrugu.md:102` `dongu-158.md:140` → `:141` (§4 K6). Benim hatalı düzeltme listemden; yeniden kontrol gerektirmez.
- **Commit adımı (C ajanı) için not, P0.1:** `planlama/d158/regresyon-son-kosu.json` izlenmiyor ve `.gitignore`'da yok; G8'de "isteğe bağlı"
  (`P0.1-siniflandirma.md:196`). Kabul ölçütü "git status yalnız bilinçli dışlananlar" için commit sırasında ya G8'e eklenmeli ya da G9'a
  `.gitignore` satırı olarak yazılmalı. Ayrıca `P0.1-siniflandirma.md:7` "5 yeni dosya" artık 7 (F0-kontrol, son-koşu).
- **Orkestratöre bilgi:** G8 ile açık depoya girecek `F0-brief.md:15,18` ve `dongu-158.md:40,92` takma adı içeriyor (orkestratör dosyaları,
  A'nın çıktısı değil); `dongu-158.md:41` kuralı ve P4.5 açısından commit öncesi bakılabilir.

## Genel karar (yeniden kontrol 1): **GEÇER**
Üç paketin düzeltmeleri kaynakta doğrulandı; regresyon kapısı artık boy sapmasını iki yönde yakalıyor ve kötüleşen koşu tabanı değiştirmiyor.
Kalan iki not (bir atıf satırı, son-koşu dosyasının commit/ignore kararı) kontrol turu gerektirmez.
