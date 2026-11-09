# F6a kontrolü (P6.1, P4.5 kalanı): bağımsız kontrol ajanı B, 09.11.2026

**Genel karar: DÜZELTME TURU GEREKİYOR (kısa, FreeCAD'siz kısım zorunlu, tarama kaynaklarına dokunmadan).**

Brief'in ölçülebilir kabul ölçütlerinin hepsi bağımsız olarak doğrulandı:
- tarama kaynaklarında takma ad 0
- `carpisma-sonuc.json`: `tek_kosu` true, koşu 20261109-084522, eskimiş 0, ev pozu 0, eklem aralığında 0
- diş kökü r 1,5 yay, temas yüzü ve temas açısı değişmedi (4,3002°, 5°'te 0,3436 mm; B'nin FreeCAD ölçümü)
- `regresyon.py --yazma` çıkış 0, 10/10 aynı
- kesit kaydırması 4 yerde, `eklem_sinirlari` önerisi üreticiyle bayt bayt aynı, sayısal sınır farkı 0

Kritik bulgu yok. İki orta bulgu var:
- **O-1.** F6a, `Y2b-baski.json`'u yeniden üretti (omuz göbeği 63,2 → 63,3 g). Ama F4c zincirini (`F4c-partiler.json/.md`, `baski-listesi.md` metinleri, `F4c-dogrula.py`) güncellemedi. Commit'li `F4c-dogrula.py` şu an iki yerde kalıyor: 4b (A raporlamadı) ve 5b (A raporladı). Y2b commit'e girer de F4c girmezse depo kendi denetimini geçmez.
- **O-2.** "≤ 59°/s yüksüz, ≤ 30°/s 500 g" sınırı yalnız F2'nin rijitlik varsayımında emniyet 2 veriyor. "Güç kesik düşme S2 ≤ 10,6°" sayısı da yanlış formülle hesaplanmış (servo torku düşülmüş; doğrusu ≈ 15,5°). K38'e gidecek metin aralıkla yazılmalı.

İkisi de tarama kaynağına dokunmadan düzelir. Tarama ve modül çıktıları geçerli kalır.

Kısaltmalar: `TF/` = `tasarim/freecad/`, `KY/` = `TF/lale158/kafa-yerlesim/`, `SP/` = A'nın scratchpad klasörü.
`SPB/` = B'nin klasörü (depo dışı): `%USERPROFILE%\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad\f6a-b`.

B'nin depoya yazdığı tek dosya bu dosya. Kaynaklara, modül çıktılarına, `kod/`'a ve git'e yazılmadı.

B FreeCAD'i bir kez, tek süreç olarak koştu: `SPB/F6a-kontrol-olc.py` → `SPB/F6a-kontrol-olc.json`.
- Süre 14:41:00–14:41:04, 4 s, rc 0.
- Önce boş bellek 2,08 GB, çalışan FreeCAD süreci 0; sonra 2,06 GB.
- Başlatıcı `%USERPROFILE%\.robot-cad\run_fc.py`, FreeCAD 1.1.4.
- Karşılaştırma için HEAD (F2) sürümü: `SPB/HEAD_omuz_parcalar.py` (`git show HEAD:`). A'nın `olc_dis.py`'si kullanılmadı.

Takma ad aramaları, takma ad komut satırına yazılmadan yapıldı: ad `git show HEAD:TF/kafa/kafa_parcalar.py` satır 6'dan çalışma anında türetildi (`SPB/ayikla_diff.py`). Arama büyük/küçük harf duyarsız ve alt dizge araması. HEAD'de geçen dört biçimin (5, 7, 9, 10 karakter; ekli ve hesap adı biçimleri) hepsi bu aramaya giriyor. A'nın günlüğü biçimleri açık yazmıyor, yalnız "`git grep -il <takma ad>`" diyor.

## Madde tablosu

| # | Madde | Kontrol yöntemi | Sonuç | Kanıt |
|---|---|---|---|---|
| 1a | Takma ad (P4.5 kalanı) | `SPB/ayikla_diff.py`: her `.py` farkında silinen ve eklenen satırları eşledi. Takma ad "Ahmet" ile değiştirilince satırın geri kalanı aynı mı, bakıldı. | **GEÇER.** 8 dosyada 30 satır, hepsi yalnız ad değişimi: `arayuz.py` 17, `kabuk_lib.py` 1, `kabuk_parcalar.py` 3, `kafa10_lib.py` 4, `kafa_lib.py` 1, `kafa_parcalar.py` 1, `omuz_parcalar.py` 1, `taban_parcalar.py` 2. A'nın tablosuyla aynı. Eklenen satırlarda takma ad 0. `KY/yerlesim_lib.py` HEAD'de zaten temiz: `git grep -il` HEAD'de 11 dosya veriyor, o dosya aralarında yok. | `git grep -il "$AD"` (çalışma kopyası) → `CLAUDE.md`, `kod/ortak/eklem_sinirlari.json`, `tasarim/freecad/index.html` (üçü de kapsam dışı: K25, `kod/`, K26) |
| 1b | `kabuk_parcalar.py:733` 72 → 70 | diff | **GEÇER**: tek satır, yalnız sayı. | `SPB/diff_ayik.txt` |
| 1c | Kesit kaydırması 4 yerde, P1.5 kalıbı | Kalıp `TF/kabuk/kabuk_montaj.py:332-359` (F1b P1.5, F1b-kontrol madde 14–15) ile satır satır karşılaştırıldı. Yeniden üretilen JSON'larda `kesit_kaydirma` ve "kapanmadi" sayıldı. | **GEÇER (not D-1).** `dirsek_lib.py:141-161` kalıbın birebir aynısı. `uygulama_tani.py:30-49` kalıbın aynısı, yalnız tanı betiği olduğu için hata kaydı yok, `kaydirma` alanı var. `kafa_lib.py:264-292` ve `omuz_baski.py:199-226` kalıbı genişletiyor: geçersiz yüzde de kaydırma deneniyor. Bu iki dosyada zaten `isValid` dalı vardı, gerekçe günlükte. Kaydırılan katman 0 / 0 / 0 / 0; "kesit teli kapanmadi" 0. | `kafa-analiz.json` `kesit_kaydirma` 15 kayıt, hepsi boş. `dirsek-analiz.json` 4 boş. `omuz-baski.json` 36 boş, `kesit_kaydirma_sayi` 36 × 0. `uygulama-tani.json` `kaydirma` 13 × 0/null. |
| 1d | Diş kökü r 1,5 | §2'deki ölçüm | **GEÇER** | `SPB/F6a-kontrol-olc.json` |
| 1e | "horn/dişli yük almaz" yorumları | diff ve `git grep` | **GEÇER (not D-3).** `omuz_parcalar.py:167-169` ve `arayuz.py:189-190` doğru anlamda. Başka bir yerde omuz S2'ye atıf kalmış (D-3). | `git grep -niE "yuk (almaz\|tasimaz)…"` |
| 1f | `yana_alt_bosluk_mm`, `eklem_sinirlari()` metni | diff; okuyanlar `git grep` ile arandı | **GEÇER (not D-2).** `arayuz.py:178-184`: yeni `{5.0: 0.34, 4.3: 0.0}` ve `yana_alt_temas`. `arayuz.py:782-787`: metin bu alanlardan üretiliyor. Okuyan tek yer `eklem_sinirlari()`. `kod/` içinde `bosluk_mm` okuyan betik yok. | `git grep -n "bosluk_mm\|yana_alt_bosluk\|temas_derece"` |
| 1g | `eklem_sinirlari` önerisi | §5 | **GEÇER** | |
| 1h | Port girintisi uygulanmadı | diff: `GOGUS_EKRAN` ve `lale158_kontrol.py` değişmemiş | **GEÇER** (doğru karar; ekran ölçülmedi) | `git status --porcelain -- '*.py'` (12 dosya, bunlar arasında yok) |
| 1i | `baski_listesi_guncelle.py` yaması | HEAD sürümüne `F4c-dogrula.py:28` `YAMA` (11 değişiklik) bellekte uygulandı, çalışma kopyasıyla karşılaştırıldı. | **GEÇER**: "HEAD + YAMA == çalışma kopyası: True". Ama yan etkisi O-1. | komut ve çıktı O-1'de |
| 1x | Brief dışı değişiklik | 12 `.py` farkının bütün parçaları 1a–1i'ye eşlendi | **GEÇER**: eşleşmeyen parça yok. | `SPB/diff_ayik.txt` |
| 2a | Kök dolgusu yalnız iç köşede mi | Göbek (F6a) − göbek (HEAD): eklenen ve çıkan hacim, kutu | **GEÇER.** Eklenen 27,715 mm³, tek katı. Kutu x 166,673…168,0; y −25,0…−23,0; z −8…21 (dişin genişliği). Çıkan 0. Kol çatalı aynı. Göbek tek katı, geçerli. Hacim 53.972,55 → 54.000,26 mm³. | `gobek_fark` |
| 2b | Profil (z 6,5 / 15 / −5) | `slice` kenarları | **GEÇER.** Üç kesitte de aynı: doğru (166,8233; −25) → (167,5; −34); **Circle r 1,5000**, merkez (168,3191; −24,8875), (166,8233; −25) → (167,2043; −23,884); doğru → (168; −23). B'nin teğetlik hesabı: T'de yarıçap · diş yönü = 0, U'da yarıçap · doğru yönü = 0. Yay 46,3°, U→K doğrusu x 168 yüzüne dışbükey köşeyle bağlanıyor, yeni iç köşe yok. A'nın `kt_fem.py` `geo_yeni` noktaları (T, O, U) CAD ile 4 hanede aynı. | `kesit.z6.5/z15/z-5` |
| 2c | Temas yüzü ve temas açısı | +x yüzü (normal (0,99719; 0,07498)) önce/sonra; ilk temas ikiye bölme ile (22 adım); ortak hacimler | **GEÇER.** Yüz y −34…−23 (319,9 mm²) → y −34…−25 (261,7 mm²). Yalnız kökteki 2 mm kısaldı; temas şeridi y −34…−29,42 içinde. İlk temas önce ve sonra **4,3002°**. Ortak hacim 4,29°'de 0,7047 / 0,7047, 4,2°'de 7,0917 / 7,0917. 4,31°'de boşluk 0,0049; 5°'te **0,3436 / 0,3436 mm**. 4,3°'teki temas noktaları (167,16; −29,42) ve (167,5; −34): kök dolgusundan uzakta. | `dis_yuzu_*`, `ilk_temas`, `aci`, `temas_noktalari_4_3` |
| 2d | Kol çatalı ↔ dolgu | En küçük mesafe, S2 −20…120 | **GEÇER.** S2 0 / 4,3 / 5 / 10 / 30 / ≥ 60: 3,00 / 4,43 / 4,69 / 6,53 / 11,17 / 13,38 mm. S2 −10'da 0,22 mm, −20'de 17,22 mm³ çakışma; ikisi de aralık dışı ve diş 4,3°'te zaten durduruyor. Bu 17,2 mm³, omuz regresyonundaki `kol_gobek` −20 farkıyla birebir aynı (2153,3 → 2170,5). A'nın −20'deki "59 mm³" değeri `KOK_DOLGU` gövdesine göre ölçülmüş (malzeme içi örtüşme dahil), net ekleme değil; çelişki yok. | `catal_x_dolgu` |
| 2e | K_t 1,45 ve darbe tablosu | Yöntem okundu (`SP/kt_fem.py`, `SP/darbe_f6a.py`). Aritmetik bağımsız yeniden yapıldı (`SPB/darbe_b.py` → `.json`). | **KOŞULLU (O-2).** Yöntem içinde sayılar doğru: stall 2,57, 1,5 rad/s yüksüz 1,54 vb. Hepsi F2 tablosu / 1,454. 59 / 30°/s yalnız F2 rijitliğinde emniyet 2. Düşme sınırı formülü hatalı. Sınırlar aşağıda. | `SPB/darbe_b.json` |
| 3 | Tarama | `py -3 TF/carpisma_kos.py kontrol` (FreeCAD'siz, okur). `carpisma-sonuc.json` alanları okundu. 17 kaynağın md5'i (ilk 10 hane, betikle aynı yöntem) bağımsız hesaplandı. Kaynak dosyaların zaman damgaları okundu. | **GEÇER.** Çıkış 0, "izlenen 17 dosyanin ozetleri kayitla ayni". `tek_kosu` true. 9 bölüm `kosu` = 20261109-084522; bölüm `kaynak` sözlükleri sonuçla birebir aynı. `ev_pozu_cakisma` []. `toplam.eklem_araliginda` 0 (kafa 0, taban 0). Bütün kaynakların değişme saati ≤ 08:54:41, taramanın başlangıcı 10:06:29. Uyuşmayan md5 0. | komutlar §Kanıtlar |
| 4a | `regresyon.py --yazma` | Koşudan önce ve sonra iki dosyanın sha1'i alındı | **GEÇER.** Çıkış 0, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)", 10/10 "aynı": boy 1580, çakışmalar 0, rampa 1,519, tilt 3,64, pan 2,21, mik–hoparlör 574,3, SY8205 0. Dosyalar değişmedi. A'nın normal koşusu tabanı yazmış; HEAD tabanıyla değerler aynı, fark yalnız tarih, sha ve koşu kimliği. | `SPB/regresyon_yazma.out`; `git diff planlama/d158/regresyon.json` |
| 4b | Regresyon referans önerileri | md5; HEAD'deki (F2) `sonra.json` ile alan alan; 14.10 / 08.10 referanslarıyla özet | **GEÇER.** `omuz-once.json` = `TF/omuz/regresyon/sonra.json` (md5 26c1e48c…), `iskelet-once.json` = `TF/iskelet/regresyon/sonra.json` (9b45698e…). Referanslar değişmedi (`git status` yalnız `omuz/regresyon/sonra.json`). F2 → F6a omuz farkı: göbek hacmi +27,715 mm³, kütle +0,0317 g, merkez ≤ 0,016 mm, `kol_gobek` −15 / −20; geri kalan 875 sayı ≤ 7,7e-5. İskelet F2 ile 0 fark. 14.10 → öneri: parça 70 → 75 (−3 / +6 adla, A'nın tablosuyla aynı); kütle 852,6 → 962,2 g; `kol_gobek` çakışan poz 8 → 11; `kol_govde` 94 → 94. **Eklem aralığında (S1 −45…135, S2 5…120) çakışan poz her ikisinde 0.** İskelet 08.10 → öneri: 59 parça; 43 aynı, 15 tanesi +315 mm kaymış (travers ve 14 bağlantı elemanı), direk +228.784 mm³ (= 315 mm uzama). Açıklanmamış fark yok. | §Kanıtlar |
| 5 | `eklem_sinirlari` önerisi | `kod/ortak/eklem_sinirlari_uret.py` modül olarak yüklendi (`main()` koşmaz); `uret()` metni öneriyle karşılaştırıldı; düzleştirilmiş fark. `--kontrol` koşuldu. `git status --porcelain kod/` | **GEÇER (not D-2).** Öneri = `uret()` çıktısı (6133 bayt, bayt bayt aynı); `kontrol_et` geçiyor. Fark yalnız şunlar: `r_s2` / `l_s2` `neden`, `bosluk_mm` {"0", "-2", "-3"} → {"5": 0.34, "4.3": 0.0}, yeni `temas_derece` {4.3, 3.65, 3.21}, `teker.not_` içinde takma ad → Ahmet. **Bu alanlar dışındaki sayısal fark: [] (yok).** `--kontrol`: "ESKI ya da yok", çıkış 1 (beklenen). `git status kod/` boş. | §Kanıtlar |
| 6a | Kütle değişimleri | HEAD ↔ çalışma kopyası, JSON alan alan | **GEÇER.** Göbek +27,715 mm³ × 1,27 × 0,9 = +0,0317 g/taraf. `montaj-analiz.json` `parcalar[91]` / `[164]` 61,691 → 61,722; robot 25.720,49 → 25.720,55. İskelet ve taban: +4,9 g F2'den kalma. `iskelet-analiz.json` son commit `bcaa6df` (04.11, F2'den önce); `taban-analiz.json` F2 commit'inde 26.115,6 g idi, yani F2 öncesi montaja göre üretilmişti (taban `montaj-analiz.json`'u okuyor, `taban_montaj.py:281`). Şimdi 26.120,5. Travers yükü +0,0243 N = 2,48 g/omuz (2,45 F2 + 0,03 F6a). `lale158-kontrol.json` `baski` omuz göbeği ölçüsü 66 → 77: son commit `fc8d7b5` (F2'den önce); 11 mm, dişin y −23 → −34 uzanması. Ayrıca `sure_s`. | `git log -1 -- …`; `SPB` farkları |
| 6b | 77 PNG, FCStd / STEP | `git status`, `git diff --numstat`, FCStd zip içeriği | **GEÇER (not D-5, D-6).** PNG'ler: iskelet 11, omuz 4, kabuk 13, dirsek 14, kafa 17, taban 18 = 77; montaj görselleri değişmedi. STEP: dirsek / iskelet / kabuk / kafa / taban 1 satır (zaman damgası); omuz +15.527 / −15.441, robot-montaj +558.714 / −558.542 (göbek geometrisi). Değişen STL yalnız `omuz-gobegi.stl`. FCStd içinde takma ad 0, kullanıcı yolu 0. 5 FCStd'ye GUI verisi eklendi (D-6). `yerlesim-kontrol.json` önceki kopyayla bayt aynı (`cmp`). | §Kanıtlar |
| 7a | `montaj_gorsel` | Kaynak okundu; `git log -S` | **KALIR (öneri, D-4).** Kök neden doğrulandı (D-4). | |
| 7b | F4c betikleri | B kopyayla denedi (depoya yazmadan) | **KALIR → düzeltme turu (O-1).** | |
| 7c | `baski-listesi.md` eski satırlar | `grep` ile kaynak arandı | **KALIR → düzeltme turu (O-1).** Satırlar elle değil, F4c betik şablonlarından geliyor. | |
| 8 | Commit listesi | §7 ↔ `git status --porcelain` | **KOŞULLU.** §7 ile durum birebir: eksik 0, fazla 0. Ama `Y2b-baski.json` ancak O-1 düzeltmesiyle birlikte girmeli. Ek dışlama: `tasarim/solidworks/`. Takma ad 0. Başka öğrenci ya da danışman soyadı 0. | §8 |

## Bulgular

**Kritik: yok.**

### O-1 (orta). F4c zinciri F6a ile tutarsız: commit'li `F4c-dogrula.py` iki denetimde kalıyor

**Neden.** F6a omuz göbeğini değiştirdi ve `planlama/y2/Y2b-baski.json`'u yeniden üretti:
- `satirlar[58]` g 63,2 → 63,3
- `toplam.g` 7604,6 → 7604,8
- `parti[2].g` 1330,6 → 1330,8

Ama `planlama/d158/F4c-partiler.json/.md` yeniden üretilmedi. Ayrıca `baski_listesi_guncelle.py` yaması kalıcı uygulandığı için `F4c-dogrula.py` 5b kırıldı.

**Kanıt** (B koştu, depoya yazmaz; `git status` önce ve sonra aynı):
```
$ py -3 planlama/d158/F4c-dogrula.py        → rc=1   (SPB/f4c_dogrula_orijinal.out)
GECTI 1 … GECTI 4a …
KALDI 4b F4c-partiler Parti 1-4 toplami = baski listesi …: 72 adet, 7604,6–7662,4 g, … (CF 1158,0–1215,8 g)
GECTI 5a …
yama/yonlendirme metni 0 kez bulundu (1 olmali): '    r = m.group(7).replace(\'**10,1" ekran + kamera delikleri**\' …
```
- **4b'yi A raporlamadı.** Açık A5 yalnız 5b'yi ve üç satırı söylüyor.
- `dongu-158.md:162` "F4c doğrulaması yeniden 0 vermeli" diyordu; bu sağlanmadı.

**Eski metinler** (`K39 kök yarıçapı (P6.1)` hâlâ "bekliyor" diyor; `63,2–70,4 g`): `planlama/baski-listesi.md:36`, `:134`, `:221`, `:239` ve `planlama/d158/F4c-partiler.md:49`, `:87`, `:105`, `:155`. A yalnız 36, 134 ve 239'u saydı. Bunlar elle yazılmış satırlar değil. F4c betiklerinin şablonlarından geliyorlar:
- `planlama/d158/F4c-liste.py:68` ("63,2–70,4 g", F2 satırı), `:143` (K39)
- `planlama/d158/F4c-partiler.py:88`, `:112`, `:244`, `:339` (K39)

`baski_listesi_guncelle.py` bu satırları yazmıyor. md dosyası elle düzeltilirse bir sonraki `F4c-liste.py` koşusu eski metni geri getirir.

**En küçük düzeltme, B'nin denemesi** (kopyalar `SPB/`'de, çıktı yolları scratchpad'e yönlendirildi, depoya yazılmadı):
1. `F4c-dogrula.py:28` `YAMA = [` → `YAMA = []` (eski liste yorum ya da `YAMA_F4C` adıyla dursun; gerekçe: "F6a 1i: Y1–Y7 kalıcı uygulandı"). `F4c-liste.py` `DG.guncelle(…, True)` (`:188-189`) değişmeden çalışır.
   - "Yama zaten uygulanmışsa atla" denetimi tek başına yetmiyor. B denedi: Y1'in eski metni yeni metnin öneki olduğu için yamalı kaynakta da 1 kez geçiyor (`SPB/kopya_dogrula.out`, 5b yine kaldı).
2. `F4c-partiler.py` yeniden koşulur. B'nin kopyası (`SPB/kopya_F4c-partiler.py`) 7 değer farkı verdi: `liste_toplam.g[0]` 7604,6 → 7604,8; `cf_g[0]` 1158,0 → 1158,2; `partiler.2.parcalar[14].g[0]` 63,2 → 63,3; `partiler.2.toplam.g[0]` 1330,6 → 1330,8 vb.
3. Bu iki değişiklikle `F4c-dogrula` kopyası: **rc 0, 1–5b hepsi GEÇTİ** (`SPB/kopya2_dogrula.out`).
4. Metin: şablonlardaki K39 ifadeleri "kök yarıçapı r 1,5 F6a'da uygulandı; DS3235 düşme ölçümü (K39) açık" olur, `F4c-liste.py:68`'e F6a payı (63,3–70,4 g) eklenir. Sonra `F4c-partiler.py` → `F4c-liste.py` (`baski-listesi.md`'yi yazar) → `F4c-dogrula.py` (0).

**Etki:** `Y2b-baski.json` F4c dosyaları olmadan commit'lenirse depo kendi denetimini geçmez. `Y2b-baski.json` hiç commit'lenmezse bu kez `F4c-dogrula` 1 kalır, çünkü Y2b-baski.py güncel `omuz-baski.json`'dan 63,3 üretiyor. Tek tutarlı yol düzeltme. FreeCAD gerekmez, tarama kaynağı değişmez.

### O-2 (orta). Darbe hız sınırı yalnız tek rijitlik varsayımında emniyet 2; düşme sınırı yanlış formülle

**Yöntem içinde doğru.** B'nin bağımsız aritmetiği (`SPB/darbe_b.py`, A'nın girdileri: r_F 30,296 mm, W 155,55 mm³, h 8,71 mm, I_kol 0,029412, I_500g 0,082784, K_t 1,4543):

| Durum | Sonuç |
|---|---|
| stall | emniyet 2,57 |
| emniyet 2 | F 280,6 N → yüksüz 58,9°/s, 500 g ile 30,2°/s |
| emniyet 1,5 | 89,2 / 45,6°/s |

A'nın `f6a.izinli` sonuçlarıyla aynı.

**Varsayıma duyarlılık.** Aynı K_t ile:

| Rijitlik (`darbe_f6a.py` üç durumu) | kθ (N·m/rad) | Emniyet 2 için hız (yüksüz / 500 g) | 59 / 30°/s'de emniyet |
|---|---|---|---|
| F2 varsayımı (k_diş/2, kol esnek) | 980 | 58,9 / 30,2°/s | 2,00 / 2,01 |
| Rijit (k_diş, kol rijit) | 4568 | **27,3 / 14,0°/s** | **1,14 / 1,15** |
| Esnek (k_diş/3, kol esnek) | 807 | 64,9 / 33,2°/s | 2,13 / 2,14 |

Yükün temas şeridindeki yeri de etkili. Eğilme kolu orta noktada 8,71 mm, uçta (y −34) 11,0 mm (× 1,263), üst kenarda 6,42 mm (× 0,737). Yük uca kayarsa, F2 rijitliğinde emniyet 2 için 40,0 / 20,5°/s gerekir.

A'nın günlüğü (`F6a-gunluk.md:118-119`, `:288-290`) ve `dongu-158.md:161` yalnız ilk satırı veriyor ve "K38 ile örtüşüyor" diyor. Doğru ifade şu: K38'in 60 / 30°/s sınırı F2 varsayımında emniyet ≈ 2, rijit alt sınırda ≈ 1,15.

**Düşme sınırı hatası.** `SP/darbe_f6a.py:175` `izinli_kt()` güç kesik düşme için de `tau = F * r_F - tau_stall` kullanıyor, yani servo torkunu düşüyor. Güç kesikken servo torku yok. Tablodaki düşme senaryoları (`servo=False`, `:150-152`) doğru, ama `dusme_S2_derece` (`:180`) yanlış formülle hesaplanmış.

Doğrusu (`SPB/darbe_b.json` `dusme_S2_deg_servosuz`):

| Rijitlik | Emniyet 2 | Emniyet 1,5 |
|---|---|---|
| F2 varsayımı | **15,5°** (A: 10,6) | 20,4° (A: 15,3) |
| Rijit | 8,1° | 10,2° |

Hata tutucu yönde, ama karar metnine yanlış sayı gidiyor (`F6a-gunluk.md:119`, `:290`).

**K_t'nin değerlendirmesi:**
- Yöntem: 2B düzlem gerilme, CST, h 0,02 mm. Ağ yakınsamış (0,08 / 0,04 / 0,02 → 1,461 / 1,460 / 1,454), CAD geometrisi doğru (madde 2b).
- K_t,etkin = FE tepe gerilmesi / F2 nominali. Nominal y −23'te, t 5,673, kol 8,71. Yani emniyet = izin / FE tepe gerilmesi. "Etkin" çarpan kısa kiriş payını da içeriyor; A'nın günlüğüne göre kökten uzakta FE / kiriş oranı 1,10–1,15, bu karşılaştırma JSON'da yok.
- Tepe noktası (166,86; −24,52), yay içinde. O kesitin yerel nominaline göre (kol 7,19 mm, t ≈ 5,80) yerel çarpan ≈ 1,84 ediyor. El kitabındaki omuz yarıçapı eğilme eğrileri (r/d ≈ 0,26, D/d ≈ 1,2–1,5) yaklaşık 1,3–1,4 verir; kısa kiriş payıyla bu ≈ 1,45–1,6 olur. FE bundan biraz yüksek, yani tutucu tarafta. Bu yalnız mertebe karşılaştırması; B ayrı bir FE koşmadı.
- Modelin kapsamadıkları:
  - z boyunca düzgün yük varsayılıyor; kol burulursa uca yığılır.
  - Yük şerit üzerinde düzgün yayılı; uca kayma payı yukarıda verildi.
  - Ankastre sınır y −10'da. Genel tepe gerilmesi (0,113 MPa/N) bu sınırın köşesinde çıkıyor; bu bir sınır koşulu yapaylığı, A doğru şekilde kök bölgesiyle sınırlamış.
  - Baskıda yay katman basamaklarıyla oluşur. Göbek +X yönünde basılıyor ve yayın düzlemi baskı yönünü içeriyor; r 1,5 yaklaşık 7 katmanla çiziliyor (A6). Tepe noktasındaki asal gerilme hemen hemen y yönünde, yani katman düzleminde. XY dayanımı kullanmak doğru, ama yüzey basamakları ek yerel çentik getirir.
  - Malzemenin darbe davranışı ve tekrarlı yük hesapta yok.

**F2 tablosundan farkı.**
- F2 tablosu K_t'siz nominal gerilmeyle hesaplanmıştı. F6a sayıları aynı modelin F2 / 1,454'ü: stall 3,73 → 2,57, yüksüz 2,24 → 1,54 vb.
- Bu bir **kötüleşme değil**. F2'nin keskin köşeli gerçek geometrisi aynı FE ile K_t 2,73…3,64 veriyor; yani F2'nin gerçek emniyeti stall'da 1,37…1,03, yüksüzde 0,82…0,62'ydi. F6a kökü bunu 1,9–2,5 kat iyileştiriyor.
- Rapor metninde "emniyet 3,73 → 2,57 düştü" diye yazılmamalı; "K_t'li karşılaştırmada 1,0–1,4 → 2,57" yazılmalı.

### D-1 (düşük). Kesit kalıbının iki dosyada genişletilmesi ve kalıptan gelen kenar durumu
- `kafa_lib.py:264-292` ve `omuz_baski.py:199-226`, P1.5 kalıbına "geçersiz yüzde de kaydır" adımını ekliyor. Brief "aynısı" diyordu. Ama iki dosyada eski `isValid` dalı vardı ve sonuç 0 kaydırma; davranış farkı bu modelde tetiklenmiyor.
- Kenar durumu: dz 0'da tel açık ya da yüz geçersiz, kaydırılmış düzlemde kesit boşsa (`if not ws: break`, `kafa_lib.py:274-275`, `dirsek_lib.py:149-150`, kalıbın kendisi `kabuk_montaj.py:348-349`), katman ne `sorun`'a ne `atla`'ya yazılır. Sessiz atlama yalnız parçanın en üst ya da en alt katmanında olabilir.
- `omuz_baski.kesit_k` (`:210`) bu durumu "acik" olarak döndürüyor; daha iyi.
- Bilgi olarak; düzeltme gerekmez.

### D-2 (düşük). `bosluk_mm` anahtarının anlamı değişti
- Eski anlam: kol ↔ kabuk boşluğu (S2 0 / −2 / −3).
- Yeni anlam: kol çatalı ↔ en yakın engel, yani durdurucu dişi (S2 5 / 4,3).
- Aynı anahtar adı korunuyor. `arayuz.py:783` metnindeki "1,36 mm" ve "0,83 mm" alanlardan değil, sabit yazılmış.
- `kod/` içinde okuyan yok, ama Efe'ye gidecek pano notunda (KT-F6a-1) anlam değişikliği açıkça yazılmalı.

### D-3 (düşük). Omuz S2'ye atıf yapan bir ifade kalmış
- `TF/dirsek/dirsek_rapor.py:197` ve onun ürettiği `TF/dirsek/rapor.html:59` şöyle diyor: "servo mili yanal yük taşımaz (omuz S2 ile aynı çözüm)".
- F2-kontrol B-1 ve F6a 1e'ye göre omuz S2'de darbe kuvvetinin ~%88'i mafsala radyal gider ve horn + servo mili bunu 625ZZ + M5 ile paylaşır. Parantez içi atıf yanlış.
- A'nın araması bu biçimi yakalamamış (`F6a-gunluk.md:130`).
- Tarama kaynağı değil. Sonraki rapor güncellemesinde "(omuz S2'de radyal yük horn/servo mili ile 625ZZ arasında paylaşılır)" olmalı.

### D-4 (düşük, önceden var). `montaj_gorsel.py` 29.10'dan beri koşmuyor
- Kök neden doğrulandı: `TF/arayuz.py:759-763` `KAFA_KOL_YASAK`, `_YS_AKTIF` false iken `kutu_sag_kol`, `kutu_sol_kol` ve `kol_kosulu` değerlerini None yapıyor. Bu değişiklik `b1f9547`'de geldi (29.10; `git log -S"_YS_AKTIF"`).
- `TF/montaj/montaj_gorsel.py:98` bu None değerleri döngüye alıyor, `:101` `Y["kol_kosulu"][k]` "'NoneType' object is not subscriptable" ile düşüyor (`SP/gui_montaj_gorsel.log`).
- Montaj görsellerinin son commit'i `c531c59` (14.10).
- F6a'dan bağımsız.

### D-5 (düşük, bilgi). K23'ün kabuk görselleri artık F6a çıktısı
- 13 kabuk PNG'si 14:28'de F6a tarafından yeniden üretildi; 03.11 ara çıktıları üstüne yazıldı.
- K23 seçenek a "P6.1 yeniden üretir" diyordu; kabuk geometrisi F6a'da değişmedi (yalnız yorum).
- Bu turda bu dosyalar talimat gereği commit dışı. Orkestratör K23'ü "P6.1 yeniden üretti" diye kapatırsa 13 PNG F6a ile girebilir.
- `TF/montaj/yerlesim-kontrol.json` hâlâ 03.11 hâlinde (önceki kopyayla `cmp` aynı); P6.1 brief'inde üretimi yoktu.

### D-6 (düşük, bilgi). FCStd'lere GUI verisi girdi
- dirsek, iskelet, kabuk, omuz ve taban `*-montaj.FCStd` artık `GuiDocument.xml`, `LineColorArray*` ve küçük resim içeriyor; boyutlar +%5…+%25.
- Nedeni modül görsel betiklerinin kasıtlı `doc.save()` çağrısı (`omuz_gorsel.py:118`, `taban_gorsel.py:69` "renk ve gorunurluk dosyaya").
- Son 4 commit'teki sürümlerde GUI verisi yoktu, çünkü görseller montajdan önce koşmuştu.
- Zararsız, bilgi olarak.

### D-7 (düşük, önceden var). Çakışma kaynak özeti satır sonuna duyarlı
- `carpisma_kos.kaynak_ozeti()` çalışma kopyası baytlarının md5'ini alıyor. İzlenen 17 dosyanın 11'i çalışma kopyasında LF: F6a'nın düzenlediği 9 tarama kaynağı ile daha önce düzenlenmiş `dirsek_parcalar.py` ve `iskelet_parcalar.py`. Kalan 6'sı CRLF: `carpisma.py`, `kafa-analiz.json`, `omuz_lib.py`, `ortak_lib.py`, `sigma_profil.py`, `taban_lib.py` (`git ls-files --eol`; `core.autocrlf=true`).
- HEAD (F2) kaydında da karışıktı: `carpisma.py`, `ortak_lib.py` vb. CRLF; `arayuz.py`, `iskelet_parcalar.py` vb. LF. Yani yeni değil.
- `git add` / `commit` çalışma kopyasına dokunmaz, `kontrol` 0 kalır. Ama `checkout`, `stash` ya da temiz bir klon dosyaları CRLF'ye çevirir ve `kontrol` "eski" der.
- C commit'ten önce bu dosyalara checkout, reset ya da stash uygulamamalı. İleride özetin satır sonundan bağımsız alınması (CRLF → LF normalize) düşünülmeli; `carpisma_kos.py` tarama kaynağı değil.

## Açık maddeler için öneriler

**`montaj_gorsel` (A3, KT-F6a-5).** En küçük düzeltme tek koşul. `montaj_gorsel.py:98`:
```python
for taraf, kutu in ((("Sag", Y["kutu_sag_kol"]), ("Sol", Y["kutu_sol_kol"])) if Y.get("aktif") else ()):
```
Böylece yasak kutu yokken kutu denetimi atlanır; eklem sınırı denetimi (`:94-96`) kalır.
- `montaj_gorsel.py` tarama kaynağı değil (`KAYNAK_SABIT` ve `*_lib.py` desenlerinde yok); `kontrol` etkilenmez.
- Sonra `gui:montaj_gorsel` bir kez koşulur. Bu, `TF/montaj/gorsel/*.png` ve GUI'li `robot-montaj.FCStd` yazar.
- Risk: betik 29.10'dan beri koşmadığı için kutu denetiminden sonra başka eski bağımlılıklar çıkabilir. Koşu durursa yeniden başlatılmaz, günlüğe yazılır.
- **Öneri: F6a düzeltme turuna alınsın** (P6.1 satırında var, tarama gerektirmez). Makine ya da zaman yoksa F6a kabulünü bloke etmez; ayrı küçük paket (P6.1 kalanı) olur.

**F4c betikleri (A5, KT-F6a-4).** O-1'deki 1–3. adımlar. `F4c-dogrula.py` `YAMA = []`, `F4c-partiler.py` yeniden koşu; `F4c-liste.py` kodu değişmez, yalnız metin şablonları. B kopyada rc 0 gördü. **Düzeltme turu, zorunlu.**

**`baski-listesi.md` eski satırları.** Elle düzeltilmez; satırlar betik şablonlarından geliyor (O-1 4. adım). Kapsam :36, :134, :221, :239 ve `F4c-partiler.md` :49, :87, :105, :155.

## Kanıtlar (komut → çıktı, özet)

```
$ git grep -il "$AD"                       # AD çalışma anında türetildi, yazılmadı
CLAUDE.md
kod/ortak/eklem_sinirlari.json
tasarim/freecad/index.html
$ git grep -il "$AD" HEAD | wc -l          → 11 (= 3 kapsam dışı + 8 tarama kaynağı)
$ grep -aic "$AD" planlama/d158/F6a-*  F6a-regresyon-oneri/*.json   → hepsi 0
FCStd (zip içi) ve omuz-gobegi.stl         → takma ad 0, "X:\Users\…" yolu 0
$ py -3 tasarim/freecad/carpisma_kos.py kontrol
carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni.   rc=0
md5[:10] bağımsız: uyusmayan [] toplam 17; bolum kaynaklari sonuc ile ayni: True
$ py -3 planlama/d158/regresyon.py --yazma   → rc=0, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)", sha1 önce = sonra
$ py -3 kod/ortak/eklem_sinirlari_uret.py --kontrol   → "eklem_sinirlari.json ESKI ya da yok", rc=1
oneri == uret() metni (bayt): True 6133 6133; bosluk_mm/temas_derece disi sayisal fark: []
$ git status --porcelain kod/              → (boş)
FreeCAD (SPB/F6a-kontrol-olc.json): ilk_temas once 4.3002 / sonra 4.3002; aci "5": [0.3436, 0] / [0.3436, 0];
  gobek_fark eklenen 27.715 mm3, cikan 0.0, kutu [166.673, 168.0, -25.0, -23.0, -8.0, 21.0]; kesit z6.5 Circle r 1.5 merkez [168.3191, -24.8875]
omuz sonra HEAD(F2) -> simdi: |fark|>1e-3 7 alan (göbek hacim/kütle/merkez, kol_gobek -15/-20); kucuk 875, en buyuk 7.70e-05
omuz once(14.10) / oneri: kol_gobek 8 / 11, kol_govde 94 / 94, eklem araliginda [] / []
iskelet once(08.10) -> oneri: ayni 43, kayma315 15, Govde diregi merkez +157.5, hacim +228784
$ py -3 planlama/d158/F4c-dogrula.py       → rc=1 (KALDI 4b; 5b "0 kez bulundu")       [O-1]
SPB kopya (YAMA=[] + F4c-partiler yeniden): rc=0, "SONUC: GECTI"
```

## Genel karar

**DÜZELTME TURU GEREKİYOR.** Tasarım, tarama, regresyon ve `eklem_sinirlari` önerisi GEÇER. Tur kısa ve FreeCAD gerektirmeyen bir zorunlu kısımdan oluşuyor; tarama kaynaklarına dokunulmaz, tarama geçerli kalır. Kritik 0, orta 2, düşük 7.

Madde etiketleri:

| # | Madde | Etiket |
|---|---|---|
| 1 | Kaynak değişiklikleri | GEÇER |
| 2 | Diş geometrisi | GEÇER |
| 2 | K_t / darbe metni | KOŞULLU |
| 3 | Tarama | GEÇER |
| 4 | Regresyon | GEÇER |
| 5 | `eklem_sinirlari` | GEÇER |
| 6 | Yeniden üretilen çıktılar | GEÇER |
| 7 | `montaj_gorsel` | KALIR |
| 7 | F4c | KALIR |
| 7 | `baski-listesi` | KALIR |
| 8 | Commit listesi | KOŞULLU |

## A için düzeltme listesi (tarama kaynaklarına — `arayuz.py`, `*_parcalar.py`, `*_lib.py`, `carpisma.py`, `kafa-analiz.json` — dokunma)

1. **F4c (zorunlu, O-1):**
   - `planlama/d158/F4c-dogrula.py:28` `YAMA = []`; eski liste `YAMA_F4C` adıyla ya da yorum olarak kalsın, gerekçe satırıyla. Docstring 5. madde buna göre düzeltilsin.
   - K39 metinleri "kök yarıçapı r 1,5 F6a'da uygulandı; DS3235 düşme ölçümü (K39) açık" olsun: `F4c-partiler.py:88`, `:112`, `:244`, `:339` ve `F4c-liste.py:143`.
   - `F4c-liste.py:68`'e F6a payı (63,3–70,4 g; +0,03 g) eklensin.
   - Sonra sırayla koşulsun: `py -3 planlama/d158/F4c-partiler.py` → `py -3 planlama/d158/F4c-liste.py` → `py -3 planlama/d158/F4c-dogrula.py`. Sonuncunun çıkışı 0 olmalı.
   - `baski-listesi.md` :36, :134, :221, :239 ve `F4c-partiler.md` :49, :87, :105, :155 güncellenmiş mi, bakılsın.
2. **Darbe metni (zorunlu, O-2):**
   - `F6a-gunluk.md:118-121`, `:288-290`: düşme sınırı servo torkusuz yeniden verilsin. Emniyet 2'de 15,5°, emniyet 1,5'te 20,4° (F2 rijitliği); rijitte 8,1 / 10,2°.
   - 59 / 30°/s yanına rijitlik aralığı yazılsın: rijitte emniyet 2 için 27 / 14°/s, 59 / 30°/s'de emniyet 1,14–2,13; yük ucu kayarsa 40 / 20°/s.
   - "K38 ile örtüşüyor" ifadesi "F2 varsayımında" diye daraltılsın.
   - `SP/darbe_f6a.py:175` için düzeltilmiş `izinli` değerleri JSON'a yazılsın (betik depo dışı).
   - `dongu-158.md:161` satırının düzeltmesi orkestratörde.
3. **`montaj_gorsel` (önerilir, D-4):**
   - `TF/montaj/montaj_gorsel.py:98`'e `if Y.get("aktif")` koşulu eklensin; bu dosya tarama kaynağı değil.
   - `gui:montaj_gorsel` bir kez koşulsun; öncesinde boş bellek ≥ 2 GB, tek süreç. Durursa yeniden başlatılmasın, günlüğe yazılsın.
   - Sonra `py -3 TF/carpisma_kos.py kontrol` 0 ve `regresyon.py --yazma` 0 olmalı.
4. Günlük §7'ye eklenecek dosyalar: `F4c-dogrula.py`, `F4c-liste.py`, `F4c-partiler.py`, `F4c-partiler.json`, `F4c-partiler.md`, `planlama/baski-listesi.md`; 3. madde yapıldıysa `montaj_gorsel.py`, `TF/montaj/gorsel/*.png`, `robot-montaj.FCStd`. D-3 (dirsek rapor ifadesi) bu turda değil, plana iş olarak.

## C için onaylı `git add` listesi

**Şimdi onaylı.** 122 dosya: 52 değişik dosya + 64 PNG + 6 yeni dosya (bu dosya, `F6a-kontrol.md`, dahil). `Y2b-baski.json` bu listede yok; ikinci bloğa bakın. PNG globları değişmemiş PNG'leri de kapsıyor, bunun bir etkisi yok. B, değişen her dosyanın bu listede ya da dışlama listesinde olduğunu `comm` ile denetledi; listede olmayan tek dosya `Y2b-baski.json`.
```
git add tasarim/freecad/arayuz.py tasarim/freecad/dirsek/dirsek_lib.py tasarim/freecad/kabuk/kabuk_lib.py \
  tasarim/freecad/kabuk/kabuk_parcalar.py tasarim/freecad/kafa/kafa10_lib.py tasarim/freecad/kafa/kafa_lib.py \
  tasarim/freecad/kafa/kafa_parcalar.py tasarim/freecad/lale158/baski_listesi_guncelle.py \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama_tani.py tasarim/freecad/omuz/omuz_baski.py \
  tasarim/freecad/omuz/omuz_parcalar.py tasarim/freecad/taban/taban_parcalar.py \
  tasarim/freecad/carpisma-sonuc.json tasarim/freecad/carpisma-bolum/statik.json tasarim/freecad/carpisma-bolum/omuz.json \
  tasarim/freecad/carpisma-bolum/kol_sag.json tasarim/freecad/carpisma-bolum/kol_sol.json tasarim/freecad/carpisma-bolum/kolkol.json \
  tasarim/freecad/carpisma-bolum/kafa_sabit.json tasarim/freecad/carpisma-bolum/kafa_sag.json tasarim/freecad/carpisma-bolum/kafa_sol.json \
  tasarim/freecad/carpisma-bolum/taban.json \
  tasarim/freecad/dirsek/dirsek-analiz.json tasarim/freecad/dirsek/dirsek-montaj.FCStd tasarim/freecad/dirsek/dirsek-montaj.step \
  tasarim/freecad/iskelet/iskelet-analiz.json tasarim/freecad/iskelet/iskelet-montaj.FCStd tasarim/freecad/iskelet/iskelet-montaj.step \
  tasarim/freecad/kabuk/kabuk-analiz.json tasarim/freecad/kabuk/kabuk-montaj.FCStd tasarim/freecad/kabuk/kabuk-montaj.step \
  tasarim/freecad/kafa/kafa-analiz.json tasarim/freecad/kafa/kafa-montaj.FCStd tasarim/freecad/kafa/kafa-montaj.step \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-tani.json tasarim/freecad/lale158/lale158-kontrol.json \
  tasarim/freecad/montaj/montaj-analiz.json tasarim/freecad/montaj/robot-montaj.FCStd tasarim/freecad/montaj/robot-montaj.step \
  tasarim/freecad/omuz/omuz-analiz.json tasarim/freecad/omuz/omuz-baski.json tasarim/freecad/omuz/omuz-montaj.FCStd \
  tasarim/freecad/omuz/omuz-montaj.step tasarim/freecad/omuz/regresyon/sonra.json tasarim/freecad/omuz/stl/omuz-gobegi.stl \
  tasarim/freecad/taban/taban-analiz.json tasarim/freecad/taban/taban-montaj.FCStd tasarim/freecad/taban/taban-montaj.step \
  planlama/d158/regresyon.json planlama/d158/regresyon-son-kosu.json \
  tasarim/freecad/iskelet/gorsel/*.png tasarim/freecad/omuz/gorsel/*.png tasarim/freecad/dirsek/gorsel/*.png \
  tasarim/freecad/kafa/gorsel/*.png tasarim/freecad/taban/gorsel/*.png \
  planlama/d158/F6a-gunluk.md planlama/d158/F6a-eklem_sinirlari-oneri.json planlama/d158/F6a-dis-kok.png \
  planlama/d158/F6a-regresyon-oneri/omuz-once.json planlama/d158/F6a-regresyon-oneri/iskelet-once.json \
  planlama/d158/F6a-kontrol.md
```

**Düzeltme turundan sonra, B'nin yeniden kontrolüyle** (`F4c-dogrula.py` 0):
```
git add planlama/y2/Y2b-baski.json planlama/d158/F4c-dogrula.py planlama/d158/F4c-liste.py planlama/d158/F4c-partiler.py \
  planlama/d158/F4c-partiler.json planlama/d158/F4c-partiler.md planlama/baski-listesi.md
# 3. madde yapıldıysa: tasarim/freecad/montaj/montaj_gorsel.py tasarim/freecad/montaj/gorsel/*.png (robot-montaj.FCStd yukarıda)
```

**Commit'e girmemeli:**
- `planlama/dongu-158.md` (orkestratörün dosyası; C'nin kararı)
- K23: `tasarim/freecad/kabuk/gorsel/*.png` (13 dosya, D-5'e bakın) ve `tasarim/freecad/montaj/yerlesim-kontrol.json`
- `kvkk/`, `rapor/`, `tubitak-2209b/`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`
- `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`
- izlenmeyen `raporlar/` (4 dosya)
- `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`
- **ek olarak** `tasarim/solidworks/` (izlenmiyor, listede yoktu)

**Commit'ten önce:**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` çıkışı 0 olmalı.
- Tarama kaynaklarına checkout, reset ya da stash uygulanmamalı (D-7).

**Takma ad ve soyad:** commit'e girecek bütün metin dosyalarında (eklenen satırlar ve yeni dosyalar, 2474 satır), FCStd içlerinde ve PNG'lerde takma ad 0. Başka öğrenci ya da danışman soyadı 0. Yalnız `kod/` sahibinin adı geçiyor (`F6a-gunluk.md:285`), soyadı geçmiyor; önceki paketlerle aynı uygulama.

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

Kapsam: A'nın düzeltme turu 1 (`F6a-gunluk.md` §9 "Düzeltme turu 1" ve "3. madde devamı", :365-435). Kısaltmalar yukarıdaki gibi: `TF` = `tasarim/freecad`, `SP` = A'nın scratchpad'i (`…\scratchpad\f6a`), `SPB` = B'nin scratchpad'i (`…\scratchpad\f6a-b`).

## Madde sonuçları

| # | Madde | Etiket | Kanıt |
|---|---|---|---|
| 1 | Üç düzeltmenin diff'i, kapsam | GEÇER | aşağıda 1 |
| 2 | F4c zinciri | GEÇER | aşağıda 2 |
| 3 | Darbe sayıları | GEÇER | aşağıda 3 |
| 4a | 11 montaj PNG'si | **KALIR** | O-3, D-8 |
| 4b | `robot-montaj.FCStd` | GEÇER | aşağıda 4b |
| 4c | 84 `AttributeError`, poz tilt'i | GEÇER (düşük bulgu, engel değil) | D-8, D-9 |
| 5 | Bütünlük (`kontrol`, `regresyon`, kaynak özetleri) | GEÇER | aşağıda 5 |
| 6 | C `git add` listesi | KOŞULLU (montaj grubu tur 2'ye bağlı) | aşağıda 6 |

**1. Düzeltmeler, kapsam.** `git diff --stat`: 7 dosya, +40/−36. Hepsi O-1 düzeltme listesinde ya da orkestratör onayında (15:00) var; başka dosya yok. Turdan önceki `git status` (`SPB/status.txt`, 14:45) ile şimdiki arasındaki fark tam olarak şu: 6 F4c/baskı dosyası, `montaj_gorsel.py`, 11 montaj PNG'si ve bu dosya.
- `planlama/d158/F4c-dogrula.py`: `YAMA = []`. Eski liste `YAMA_F4C` adıyla gerekçesiyle duruyor, docstring güncel.
- `F4c-partiler.py:88`, `:112`, `:244`, `:339` ve `F4c-liste.py:143` K39 metni ("kök yarıçapı r 1,5 F6a'da uygulandı; DS3235 düşme ölçümü (K39) açık"). `F4c-liste.py:68` göbek satırı, `:70` fark toplamı.
- `TF/montaj/montaj_gorsel.py` (+6/−5; diff satır satır okundu):
  - `:33` yorum;
  - `:40-41` `%.6f` → `%.9f`;
  - `:47` `Kafa_Tilt` 0,25 → 0,22;
  - `:98-99` `if Y.get("aktif")` koruması.
  - B'nin hesabı: `degrees(0.087266463)` = 5,0000000229 ≥ 5 (sınır içinde); `degrees(0.22)` = 12,605 < 13.
  - `arayuz.py` ve tasarım sınırları değişmedi. Dosya tarama kaynağı değil.
- `TF/montaj/montaj_gorsel.py:54-66` (`POZ_GORSEL`) ve kamera satırları (`:192-210`, `:259`) bu turda değişmedi. Brief açısından doğru, ama O-3'ün kaynağı bu satırlar.

**2. F4c zinciri.**
- `py -3 planlama/d158/F4c-dogrula.py` → **rc 0**, "SONUC: GECTI" (`SPB/f4c_dogrula_tur1.out`; bu raporu yazmadan önce yeniden koşuldu, yine rc 0).
- Eski metinlerin sayımı 0: "K39 kök yarıçapı (P6.1)", "ayrıca K39", "63,2–70,4", "−22,6", "69–208". Sayılan dosyalar: `planlama/baski-listesi.md`, `F4c-partiler.md`, `F4c-partiler.json`, `F4c-liste.py`, `F4c-partiler.py`.
- Tutarlılık:
  - `Y2b-baski.json` `satirlar[58]`: `g` [63.3, 70.4], `adet` 2.
  - `baski-listesi.md:36` ve `F4c-liste.py:68`: "63,3–70,4 g", "+5,4–5,8 g".
  - `baski-listesi.md:38` ve `F4c-liste.py:70`: "−22,4 / −22,0 g". Bu, eski −22,6'ya 2 adet × alt uçta +0,1 g eklenmesiyle tutarlı.
  - `baski-listesi.md` diff'i +6/−6. Kapsamı `:36`, `:38`, `:134`, `:221`, `:239` ve D2 kupon payı 69–208 → 69–207 (betik hesabı).

**3. Darbe sayıları.** `F6a-gunluk.md:119-124`, `:293-297` ve §9 tablosu (`:385-393`) B'nin bağımsız hesabıyla (`SPB/darbe_b.json`) birebir aynı:
- düşme sınırı: 15,5° / 20,4° (F2 rijitliği), 8,1° / 10,2° (rijit);
- rijitte emniyet 2 için hız: 27 / 14°/s;
- 59 / 30°/s'de emniyet: 1,14 / 1,15 (rijit), 2,00 / 2,01 (F2), 2,13 / 2,14 (esnek);
- yük ucu kayarsa: 40 / 20°/s.

"K38 ile örtüşüyor" ifadesi "F2 rijitlik varsayımında" diye daraltılmış (`:124`, `:294`). O-2 kapandı. `dongu-158.md:161` orkestratörde.

**4b. `robot-montaj.FCStd` (5.766.891 bayt, 14:59:54).**
- zip testi hatasız. HEAD'e göre: nesne 1409 → 1425, `JointType` 21 / 21. Yeni olanlar: `Hareket*` 14 nesne, `Kollari_oynat`, `GuiDocument.xml`, küçük resim.
- Kısa FreeCAD okuma koşusu (bu turdaki tek FreeCAD koşusu):
  - Ön koşul: boş bellek 2,68 GB, çalışan FreeCAD 0. Süre 15:03:24–15:03:38 (13 s), rc 0. Betik `SPB/F6a-kontrol-fcstd.py`, sonuç `SPB/F6a-kontrol-fcstd.json`, günlük `SPB/fcstd.log`.
  - Geçersiz şekil 0. Yerleşim farkı 0; gruplar HEAD gibi birim dönüşümde.
  - Hacim farkı yalnız `OmuzSag/Sol_P034` (göbek) 53972,549 → 54000,264 mm³ (+27,715, F6a kök yayı). Toplam hacim 17811137,8 → 17811193,2.
  - Günlükte 4 `QtCore` `NameError` var: FreeCAD'in `Mod\Assembly\CommandCreateSimulation.py:772` dosyası GUI'siz modda hata veriyor. Zararsız; D-9'a bakın.
- GUI verisi taşıyan FCStd bu depoda olağan: `c531c59`, `dfe0df3` ve `1312001` commit'lerinde de `GuiDocument.xml` ve `Kollari_oynat` vardı. Başsız okuyucular (`eklem_dogrulama.py:33` `JointType == "Revolute"` süzgeci, `lale158_kontrol.py`, `uygulama_olc.py`) bundan etkilenmez.
- Sonuç: bozuk kaydedilmemiş; içerik beklenen içerik (F6a geometrisi + GUI kurulumu). `doc.save()` pozlardan önce olduğu için ev pozunda kayıtlı.

**5. Bütünlük.**
- `py -3 TF/carpisma_kos.py kontrol` → **rc 0**, "izlenen 17 dosyanin ozetleri kayitla ayni" (`SPB/carpisma_kontrol_tur1.out`). Önceki turun bağımsız md5[:10] karşılaştırması da 17/17 aynıydı. Bu turda tarama kaynaklarının hiçbirinde diff yok.
- `py -3 planlama/d158/regresyon.py --yazma` → **rc 0**, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)" (`SPB/regresyon_tur1.out`). Koşudan önce ve sonra alınan `git status --porcelain` aynı; koşudan sonra yeni ya da değişen dosya yok (`find -newer`).
- Takma ad (çalışma anında türetildi, yazılmadı): sayım 0. Bakılan yerler:
  - bu turda değişen 10 metin dosyası;
  - bütün diff'in eklenen satırları;
  - `robot-montaj.FCStd` içindeki XML'ler.
  - İzlenmeyen dosyalarda geçtiği yerler yalnız commit dışı alanlarda: `tubitak-2209b/`, `raporlar/`, `tasarim/solidworks/`.
- Başka öğrenci ya da danışman soyadı yok.

## Bulgular (bu tur)

### O-3 (orta). Montaj görsellerinin kadrajı eski boy için; kafa ve omuzlar kadraj dışında
- **Kanıt (gözle bakıldı: `on`, `yan`, `izometrik`, `kafa`, `omuzlar`, `dirsek`, `poz-selam`, `poz-one`, `poz-kafa`, `taban-ic`):**
  - `montaj-on.png`, `montaj-yan.png` ve `montaj-izometrik.png` gövde kabuğunun üst kısmında kesiliyor; kafa yok. Yan görünüşte omuz da kesik.
  - `montaj-kafa.png` ile `montaj-poz-kafa.png` kafayı değil göğüs/omuz bölgesini gösteriyor.
  - `montaj-omuzlar.png` omuzları göstermiyor.
  - `montaj-poz-one.png` ve `montaj-poz-selam.png` boyunda kesiliyor.
  - `montaj-dirsek.png` dirseğin yalnız alt kısmını gösteriyor.
  - Yalnız `montaj-taban.png` ve `montaj-taban-ic.png` doğru.
- **Neden:** kamera merkezleri ve görünür yükseklikler 14.10 modelinden kalma.
  - Satırlar: `TF/montaj/montaj_gorsel.py:192` (0,640,0) h 1000; `:194`/`:196` (0,635,0) h 790; `:198` kafa (0,1080,20) h 520; `:200` omuzlar (0,900,20) h 360; `:202` dirsek (150,790,0) h 420; `POZ_GORSEL` `:58`/`:62`/`:65` merkez y 820 / 860 / 1090; `:259` hareket kareleri (0,650,40) h 1340.
  - Model 1,58 m'de 476,5 dikişinden yukarısı `arayuz.UZAMA` = 315 mm daha yüksek (`TF/arayuz.py:24`, `:28`).
  - HEAD'deki `montaj-kafa.png` (`SPB/head_gorsel/`) eski modelde kafayı tam gösteriyordu.
- **Etki:** commit'lenirse kadrajı doğru olan 14.10 görsellerinin yerine kafası kesik görseller girer. Tasarımı ve taramayı etkilemez.
- **Düzeltme:** tur 2, aşağıda.

### D-8 (düşük). Poz görsellerinde kafa tilt'i ±13 sınırının dışında
- `TF/montaj/montaj_gorsel.py:61` `poz-one` için `tilt=25.0`, `:63` `poz-kafa` için `tilt=20.0`. Sınır `arayuz.KAFA["tilt_aralik"]` ±13 (Y2a, 29.10).
- `POZ_GORSEL` animasyon denetiminden geçmiyor (A da not etmiş, `F6a-gunluk.md:430`). Görseller robotun alamayacağı bir pozu gösteriyor.
- Diğer poz açıları (pan 30 / 45, omuz yana 100 / 20, dirsek 95 / 60, bilek −60 / 45) animasyon denetiminin geçtiği aralıklar içinde.
- O-3 ile aynı koşuda düzeltilir.

### D-9 (düşük, engel değil). GUI günlüğünde 84 traceback, GUI'siz açışta 4 `NameError`
- `SP/gui_montaj_gorsel.log` 84 traceback içeriyor; hepsi FreeCAD 1.1 `Mod\Assembly\JointObject.py` dosyasından:
  - `:1126` `getIcon` ve `:1164` `getOverlayIcons` → `app_obj` 42 adet;
  - `:1075` `updateData` → `switch_JCS1` 21 adet;
  - `:1078` `updateData` → `switch_JCS2` 21 adet.
  - Toplam 21 eklem × 4. `ViewProviderJoint` bağlanmadan önce çağrılan geri çağrılar bunlar; proje kodu değil.
- Koşu rc 0; iç günlük "eklem 21 simulasyon Kollari_oynat hareket 14"; FCStd geçerli (4b).
- GUI'siz açışta da 4 `QtCore` `NameError` var: `CommandCreateSimulation.py:772`. Zararsız, rc 0.
- Açık kalan tek şey A9: FCStd'nin GUI'de açılıp eklem görünümünün gözle doğrulanması. Bu Ahmet'in ya da sonraki bir GUI oturumunun işi; commit'i bloke etmez.

### D-10 (düşük, bilgi). Yenilenmeyen montaj görselleri
- `montaj-hareket.gif` (14.10) ve `montaj-gui-*.png` (5 adet, 09.10) eski modelde kalıyor.
- GIF'i `montaj_rapor.py` üretiyor, koşulmadı. GUI ekranları elle alınmış.
- F6a kapsamı dışı; plana iş olarak yazılmalı.

### Kapananlar
- O-1 (F4c) kapandı.
- O-2 (darbe metni) kapandı.
- D-4 (`montaj_gorsel` koşmuyor) kapandı: betik rc 0.
- D-1, D-2, D-3, D-5, D-6, D-7 olduğu gibi duruyor (düşük, bilgi; bu turun konusu değil).

## Düzeltme turu 2 (son tur): yalnız `TF/montaj/montaj_gorsel.py` + bir GUI koşusu

Tarama kaynaklarına, `arayuz.py`'ye ve öteki betiklere dokunulmaz.

1. **Kamera (O-3).** Kafa, omuz ve dirsek odaklı görünümlerin merkez y'sine `A.UZAMA` eklensin: `:198`, `:200`, `:202` ve `POZ_GORSEL` `:58`, `:62`, `:65`.
   - Tam boy görünümlerde (`:192`, `:194`, `:196`, `:259`) merkez y yaklaşık `A.BOY / 2` olsun. Görünür yükseklik `A.BOY / (A.BOY − A.UZAMA)` ≈ 1,25 oranında büyütülsün.
   - Ya da hepsi `Shape.BoundBox` ile hesaplansın; hangisi daha kısaysa. Sayılar sabit yazılmasın, `A.` sabitlerinden türetilsin.
   - Taban görünümleri (`:205`, `:210`) değişmez.
2. **Poz tilt'i (D-8).** `:61` `tilt=25.0` ve `:63` `tilt=20.0` en çok 13 olsun (öneri 12,0). Varsa açıklama metni de buna göre değişsin.
3. **Ön denetim (FreeCAD'siz).** `POZ_GORSEL` açıları `arayuz` sınırlarına göre denetlensin (betiğin `animasyon_kontrol()` sınırlarıyla aynı). İhlal 0 olmalı; sonuç günlüğe yazılsın.
4. **Tek GUI koşusu.** `gui:montaj_gorsel`; öncesinde boş bellek ≥ 2 GB, çalışan FreeCAD 0. Durursa yeniden başlatılmaz, günlüğe yazılır.
5. **Kabul ölçütleri:**
   - rc 0;
   - `on`, `yan` ve `izometrik` görünümlerinde robotun tamamı (teker → kafa tepesi) kadrajda;
   - `kafa` ve `poz-kafa` görünümlerinde kafa, `omuzlar` görünümünde iki omuz, `dirsek` görünümünde dirsek tam görünüyor;
   - `poz-*` görsellerinde kafa kesilmiyor.
   - Günlüğe her görselin gözle bakıldığı yazılsın.
6. **Sonra:** `py -3 TF/carpisma_kos.py kontrol` → 0 ve `py -3 planlama/d158/regresyon.py --yazma` → 0. `F6a-gunluk.md` §9'a "düzeltme turu 2" girişi.

**Tur 2 yapılamazsa (geri çekilme):**
- Montaj grubundan yalnız 11 PNG commit dışında kalır; çalışma kopyasında değişik görünürler. `montaj_gorsel.py` ve `robot-montaj.FCStd` şimdiki hâlleriyle kabul edilebilir (1 ve 4b).
- O-3 ve D-8 plana iş olarak yazılır. Bu durumda F6a kararı **GEÇER (montaj PNG'leri hariç)** olur.

## Genel karar

**DÜZELTME TURU 2 GEREKİYOR (son tur, yalnız montaj görselleri).**
- Düzeltme turu 1'in üç maddesi GEÇER. F4c zinciri, darbe sayıları, FCStd, tarama, regresyon ve takma ad denetimi temiz.
- Tek engel O-3: 11 montaj PNG'si commit'lenirse kafası kesik görseller girer. Tur 2 FreeCAD'li tek kısa GUI koşusu (≈ 1 dk) ve tarama dışı tek bir betik değişikliği.
- Montaj grubu dışındaki dört grup **şimdi commit'lenebilir**; tur 2'yi beklemez. `F6a-gunluk.md` ile bu dosya tur 2'de yeniden değişeceği için `planlama/d158` grubu en son commit'lenmeli.
- Bulgu sayıları:
  - bu turda yeni: kritik 0, orta 1 (O-3), düşük 3 (D-8, D-9, D-10);
  - toplam açık: kritik 0, orta 1, düşük 9 (D-1, D-2, D-3, D-5, D-6, D-7, D-8, D-9, D-10).

## C için kesin `git add` listesi (tek blok)

- 150 yol, glob açılınca. Bunların 141'i değişik ya da yeni (135 `M`, 6 `??`).
- Kalan 9'u değişmemiş PNG; globlar bunları da kapsıyor, bir etkisi yok: `kafa/gorsel` 3, `omuz/gorsel` 1, `montaj-gui-*` 5.
- `comm` ile denetlendi (`SPB/final_exp.txt` ↔ `git status --porcelain -uall`). Değişen her dosya ya bu listede ya da aşağıdaki dışlama listesinde.
- Montaj grubu (4) tur 2 kabulünden sonra eklenir. Geri çekilmede 4. grubun son satırı (`montaj-*.png`) atlanır.

```
# 1) kaynak + tarama (tarama kaynakları ile carpisma-sonuc.json aynı commit'te olmalı)
git add tasarim/freecad/arayuz.py tasarim/freecad/dirsek/dirsek_lib.py tasarim/freecad/kabuk/kabuk_lib.py \
  tasarim/freecad/kabuk/kabuk_parcalar.py tasarim/freecad/kafa/kafa10_lib.py tasarim/freecad/kafa/kafa_lib.py \
  tasarim/freecad/kafa/kafa_parcalar.py tasarim/freecad/omuz/omuz_parcalar.py tasarim/freecad/taban/taban_parcalar.py \
  tasarim/freecad/lale158/baski_listesi_guncelle.py tasarim/freecad/lale158/kafa-yerlesim/uygulama_tani.py \
  tasarim/freecad/omuz/omuz_baski.py \
  tasarim/freecad/carpisma-sonuc.json tasarim/freecad/carpisma-bolum/statik.json tasarim/freecad/carpisma-bolum/omuz.json \
  tasarim/freecad/carpisma-bolum/kol_sag.json tasarim/freecad/carpisma-bolum/kol_sol.json tasarim/freecad/carpisma-bolum/kolkol.json \
  tasarim/freecad/carpisma-bolum/kafa_sabit.json tasarim/freecad/carpisma-bolum/kafa_sag.json tasarim/freecad/carpisma-bolum/kafa_sol.json \
  tasarim/freecad/carpisma-bolum/taban.json
# 2) modul ciktilari
git add tasarim/freecad/dirsek/dirsek-analiz.json tasarim/freecad/dirsek/dirsek-montaj.FCStd tasarim/freecad/dirsek/dirsek-montaj.step \
  tasarim/freecad/iskelet/iskelet-analiz.json tasarim/freecad/iskelet/iskelet-montaj.FCStd tasarim/freecad/iskelet/iskelet-montaj.step \
  tasarim/freecad/kabuk/kabuk-analiz.json tasarim/freecad/kabuk/kabuk-montaj.FCStd tasarim/freecad/kabuk/kabuk-montaj.step \
  tasarim/freecad/kafa/kafa-analiz.json tasarim/freecad/kafa/kafa-montaj.FCStd tasarim/freecad/kafa/kafa-montaj.step \
  tasarim/freecad/omuz/omuz-analiz.json tasarim/freecad/omuz/omuz-baski.json tasarim/freecad/omuz/omuz-montaj.FCStd \
  tasarim/freecad/omuz/omuz-montaj.step tasarim/freecad/omuz/regresyon/sonra.json tasarim/freecad/omuz/stl/omuz-gobegi.stl \
  tasarim/freecad/taban/taban-analiz.json tasarim/freecad/taban/taban-montaj.FCStd tasarim/freecad/taban/taban-montaj.step \
  tasarim/freecad/montaj/montaj-analiz.json tasarim/freecad/montaj/robot-montaj.step \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-tani.json tasarim/freecad/lale158/lale158-kontrol.json \
  tasarim/freecad/iskelet/gorsel/*.png tasarim/freecad/omuz/gorsel/*.png tasarim/freecad/dirsek/gorsel/*.png \
  tasarim/freecad/kafa/gorsel/*.png tasarim/freecad/taban/gorsel/*.png
# 3) F4c / baski
git add planlama/y2/Y2b-baski.json planlama/baski-listesi.md planlama/d158/F4c-dogrula.py planlama/d158/F4c-liste.py \
  planlama/d158/F4c-partiler.py planlama/d158/F4c-partiler.json planlama/d158/F4c-partiler.md
# 4) montaj (tur 2 kabulunden sonra; geri cekilmede son satir atlanir)
git add tasarim/freecad/montaj/montaj_gorsel.py tasarim/freecad/montaj/robot-montaj.FCStd \
  tasarim/freecad/montaj/gorsel/montaj-*.png
# 5) planlama/d158 (en son; tur 2 gunlugu ve bu dosya dahil)
git add planlama/d158/regresyon.json planlama/d158/regresyon-son-kosu.json planlama/d158/F6a-gunluk.md \
  planlama/d158/F6a-eklem_sinirlari-oneri.json planlama/d158/F6a-dis-kok.png \
  planlama/d158/F6a-regresyon-oneri/omuz-once.json planlama/d158/F6a-regresyon-oneri/iskelet-once.json \
  planlama/d158/F6a-kontrol.md
```

**Önerilen commit grupları:**
1. **Kaynak + tarama:** F6a kök yayı, kesit kaydırma, `arayuz`, `carpisma-sonuc` ve 10 bölüm.
2. **Modül çıktıları:** analiz/montaj/STEP/STL, `uygulama-*`, `lale158-kontrol` ve modül görselleri.
3. **F4c / baskı listesi:** K39 metni, göbek 63,3–70,4 g, fark toplamı −22,4 g.
4. **Montaj:** `montaj_gorsel` koruması ve kadraj, GUI'li `robot-montaj.FCStd`, 11 montaj görseli.
5. **`planlama/d158`:** F6a günlüğü, öneriler, regresyon, kontrol.

1 ve 2 ayrı commit olabilir ama aynı push'ta gitmeli: 2'deki çıktılar 1'deki kaynaklardan üretildi.

**K23 notu (korunuyor):** 13 kabuk PNG'si ve `montaj/yerlesim-kontrol.json` şimdilik commit dışında; K23 Ahmet'in kararı.

**`git status --porcelain` içinde olup listede olmayanlar ve nedeni:**
- `planlama/dongu-158.md`: orkestratörün dosyası; B'nin yazma ve onay alanı dışında, C'nin kararı.
- `tasarim/freecad/kabuk/gorsel/*.png` (13) ve `tasarim/freecad/montaj/yerlesim-kontrol.json`: K23, yukarıdaki not.
- `tasarim/freecad/lale158/kafa-yerlesim/kaynak/` (5): F6a çıktısı değil, önceden var.
- `tasarim/freecad/montaj/lale_dongu.FCMacro` ve `lale_dongu_ac.bat`: döngü altyapısı, F6a'nın değil.
- `planlama/d158/F5-pano-govde.txt` ve `F5b-pano-govde.txt`: F5 paketinin pano metinleri, F6a dışı.
- `kvkk/`, `rapor/`, `raporlar/` (4), `tubitak-2209b/` ve `tasarim/solidworks/`: proje dışı ya da başka iş. Takma ad geçen izlenmeyen dosyalar yalnız bunların içinde, bu yüzden commit dışı kalmaları gerekiyor.

**Commit'ten önce (değişmedi):**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` → 0 olmalı.
- Tarama kaynaklarına checkout, reset ya da stash uygulanmamalı (D-7).
- Geri çekilmede 11 montaj PNG'sinin HEAD'e döndürülüp döndürülmeyeceğine C ya da Ahmet karar verir. Bunlar tarama kaynağı değil.

---

# Son kontrol (düzeltme 2): B, 09.11.2026

Kapsam dar: A'nın düzeltme turu 2 (`F6a-gunluk.md` §10). Bakılanlar: `montaj_gorsel.py` diff'i, 11 montaj PNG'si, `robot-montaj.FCStd` (15:25 kaydı) ve sınır denetimleri. Kısaltmalar yukarıdaki gibi.

## Madde sonuçları

| # | Madde | Etiket |
|---|---|---|
| 1 | `montaj_gorsel.py` diff'i | GEÇER |
| 2 | 11 montaj PNG'si | GEÇER |
| 3 | `robot-montaj.FCStd` | GEÇER |
| 4 | `carpisma_kos.py kontrol`, `regresyon.py --yazma` | GEÇER |

**1. `TF/montaj/montaj_gorsel.py` diff'i.**
- `git diff --stat`: +21/−17 (tur 1 + tur 2). Satırları tek tek okudum. Tur 1'in onaylı satırları dışında yalnız O-3 ve D-8 satırları değişmiş, başka değişiklik yok:
  - `:37-39`: iki yorum satırı ve `TAM = A.BOY / (A.BOY - A.UZAMA) * 1.03`. Değeri 1580 / 1265 × 1,03 = 1,2865.
  - Tam boy görünümler merkez `(0, A.BOY / 2, ·)` ve yükseklik `× TAM` aldı:
    - `:195` izometrik `1080 * TAM`;
    - `:197` ön ve `:199` yan `790 * TAM`;
    - `:262` hareket kareleri `1340 * TAM`.
  - Odaklı görünümlerin merkez y'sine `+ A.UZAMA` eklendi; yükseklikleri değişmedi:
    - `:201` kafa;
    - `:203` omuzlar;
    - `:205` dirsek;
    - `POZ_GORSEL` `:61` selam, `:65` one, `:68` kafa.
  - Taban görünümleri değişmedi.
  - D-8: `:64` poz-one `tilt=12.0` (önce 25), `:66` poz-kafa `tilt=12.0` (önce 20).
    - Sınır `TF/arayuz.py:597` `tilt_aralik=(-13.0, 13.0)`.
    - Pan değerleri 30 / 0 / 45; sınır `:594` ±90.
- Satır sonları: 289 CRLF, yalın LF 0 (bayt sayımı). Dosya karışık satır sonuna dönmemiş.
- Kamera değerleri modelden hesaplanıyor: ölçek ve kaydırma `A.BOY` ile `A.UZAMA` üzerinden. İki taban değeri koşu 1'den sonra elle ayarlanmış: izometrik 1000 → 1080 ve poz-one merkezi 860 → 900, yani `900 + A.UZAMA` (D-11).
- Tarama kaynağı değil. `arayuz.py` diff'i turdan önceki F6a diff'iyle aynı (+34/−21).

**2. 11 montaj PNG'si.** Hepsi 15:25:30–15:25:52 tarihli; her birine Read ile baktım.

| Görsel | Kafa | Omuzlar | Dirsek | Not |
|---|---|---|---|---|
| `montaj-on.png` | tam | tam | tam | tekerden kafa tepesine kadar robotun tamamı |
| `montaj-yan.png` | tam | tam | tam | tekerler alt kenarda, kesik değil |
| `montaj-izometrik.png` | tam | tam | tam | alt teker kadrajda |
| `montaj-kafa.png` | tam | iki omuz başı | — | |
| `montaj-omuzlar.png` | alt kısmı | iki omuz eklemi tam | — | konu omuz, beklenen kadraj |
| `montaj-dirsek.png` | — | sağ omuz tam | tam | bilek ucu alt kenarda kesiliyor (D-11) |
| `montaj-taban.png` | — | — | — | taban, acil stop, tekerler |
| `montaj-taban-ic.png` | — | — | — | aynı kadraj HEAD'de de var; havada görünen vidalar gizlenen etek panellerinin vidaları |
| `montaj-poz-selam.png` | tam | tam | tam | sağ kol kalkık |
| `montaj-poz-one.png` | tam | tam | tam | kafa öne hafif eğik |
| `montaj-poz-kafa.png` | tam | iki omuz | — | pan 45 |

- Poz-one ve poz-kafa'da kafa eğimi küçük ve ±13 içinde görünüyor. Kaynakta değer 12,0 (`:64`, `:66`); açıyı görselden ölçmedim, kaynak değerine dayanıyorum.
- O-3 ve D-8 kapandı.

**3. `robot-montaj.FCStd` (15:25:29, 5.766.556 bayt).**
- zip `testzip` hatasız: 5501 girdi, `GuiDocument.xml` var.
- Kısa FreeCAD okuma koşusu, tek seferlik:
  - Ön koşul: boş bellek 2,44 GB, çalışan FreeCAD 0.
  - Süre 15:29:35–15:29:57 (21 s), rc 0. Koşudan sonra çalışan FreeCAD 0.
  - Betik `SPB/F6a-kontrol-fcstd.py` (tur 1'deki betik), sonuç `SPB/F6a-kontrol-fcstd.json`, günlük `SPB/fcstd2.log`. Tur 1 sonucu `SPB/F6a-kontrol-fcstd-tur1.json`.
- Sonuç tur 1 ile birebir aynı:
  - nesne 1425 (HEAD'de 1409), şekilli nesne 1179;
  - geçersiz şekil 0, hatalı nesne 0;
  - yerleşim farkı 0; gruplar birim dönüşümde ve HEAD ile aynı;
  - hacim farkı yalnız `OmuzSag/Sol_P034` 53972,549 → 54000,264; toplam 17811137,8 → 17811193,2.
- **Düzeltme (B'nin kendi hatası):** önceki bölümde (4b ve D-9) "4 `QtCore` `NameError`" yazdım. Doğrusu iki günlükte de 15 traceback, hepsi aynı satırdan: `CommandCreateSimulation.py:772`. Zararsız, rc 0; değerlendirme değişmiyor.

**4. Sınır denetimleri.**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` → **rc 0**, "izlenen 17 dosyanin ozetleri kayitla ayni" (`SPB/carpisma_kontrol_tur2.out`).
- `py -3 planlama/d158/regresyon.py --yazma` → **rc 0**, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)" (`SPB/regresyon_tur2.out`).
  - Koşudan önce ve sonra alınan `git status --porcelain -uall` bayt bayt aynı (`cmp`).
  - Koşudan sonra yeni ya da değişen dosya yok.
- Takma ad 0: `montaj_gorsel.py`, `F6a-gunluk.md` ve `robot-montaj.FCStd` içindeki XML'lerde.
- Bir önceki kontrolden bu yana `git status`'a tek yeni dosya girdi: `tubitak-2209b/teslim/TYBS-proje-bilgileri-v14.md`. Başka bir işin dosyası; `tubitak-2209b/` zaten commit dışı.

## Bulgular (bu tur)

### D-11 (düşük, bilgi). Kamera tabanlarının ikisi elle ayarlı; dirsek görünümünde bilek ucu kenarda
- **İki elle ayarlı değer.** `:195` izometrik tabanı 1000 → 1080 ve `:65` poz-one merkezi 860 → 900. A bunları koşu 1'in görsellerine bakarak ayarlamış (§10).
  - Ölçek ve kaydırma yine modelden geliyor (`TAM`, `A.UZAMA`). Model bir daha uzarsa bu iki pay da kendiliğinden ölçeklenir.
  - Kadraj payının bir kısmının elle verildiği bilinsin.
- **Dirsek görünümü.** `montaj-dirsek.png`'de dirsek eklemi tam, ama bilek ucu alt kenarda kesiliyor. Görünümün konusu dirsek olduğu için kabul.
- **Koşu sayısı.** A iki GUI koşusu yaptı (§10: "izin verilen tek ek koşu"). B bu izni görmedi, orkestratörün bildiği varsayılıyor.
  - Bellek ön koşulu uygulanmış: 1,98 GB'ta deneme kendiliğinden durmuş, koşu sayılmamış.

### Kapananlar ve açıklar
- O-3 ve D-8 kapandı.
- Açık kalanlar (düşük, bilgi; F6a kabulünü bloke etmez): D-1, D-2, D-3, D-5, D-6, D-7, D-9, D-10, D-11.
- D-9'daki A9 (FCStd'nin GUI'de açılıp eklem görünümünün gözle doğrulanması) Ahmet'te ya da sonraki bir GUI oturumunda.

## Genel karar

**GEÇER.**
- F6a ve iki düzeltme turu kabul. Montaj görselleri de commit'e girer.
- Bulgu sayıları:
  - bu turda yeni: kritik 0, orta 0, düşük 1 (D-11);
  - toplam açık: kritik 0, orta 0, düşük 9.

## C için kesin `git add` listesi (son hâl, 5 grup, montaj dahil)

- 150 yol, glob açılınca. Bunların 141'i değişik ya da yeni (135 `M`, 6 `??`).
- Kalan 9'u değişmemiş PNG; globlar bunları da kapsıyor, bir etkisi yok.
- `comm` ile yeniden denetlendi (`SPB/final_exp.txt` ↔ `SPB/status_all2.txt`). Listede olmayan değişiklikler önceki bölümdeki dışlama listesiyle aynı, artı yukarıdaki `tubitak-2209b/` dosyası.
- Gruplar sırayla commit'lenebilir. 1 ve 2 aynı push'ta gitmeli.

```
# 1) kaynak + tarama (tarama kaynakları ile carpisma-sonuc.json aynı commit'te olmalı)
git add tasarim/freecad/arayuz.py tasarim/freecad/dirsek/dirsek_lib.py tasarim/freecad/kabuk/kabuk_lib.py \
  tasarim/freecad/kabuk/kabuk_parcalar.py tasarim/freecad/kafa/kafa10_lib.py tasarim/freecad/kafa/kafa_lib.py \
  tasarim/freecad/kafa/kafa_parcalar.py tasarim/freecad/omuz/omuz_parcalar.py tasarim/freecad/taban/taban_parcalar.py \
  tasarim/freecad/lale158/baski_listesi_guncelle.py tasarim/freecad/lale158/kafa-yerlesim/uygulama_tani.py \
  tasarim/freecad/omuz/omuz_baski.py \
  tasarim/freecad/carpisma-sonuc.json tasarim/freecad/carpisma-bolum/statik.json tasarim/freecad/carpisma-bolum/omuz.json \
  tasarim/freecad/carpisma-bolum/kol_sag.json tasarim/freecad/carpisma-bolum/kol_sol.json tasarim/freecad/carpisma-bolum/kolkol.json \
  tasarim/freecad/carpisma-bolum/kafa_sabit.json tasarim/freecad/carpisma-bolum/kafa_sag.json tasarim/freecad/carpisma-bolum/kafa_sol.json \
  tasarim/freecad/carpisma-bolum/taban.json
# 2) modul ciktilari
git add tasarim/freecad/dirsek/dirsek-analiz.json tasarim/freecad/dirsek/dirsek-montaj.FCStd tasarim/freecad/dirsek/dirsek-montaj.step \
  tasarim/freecad/iskelet/iskelet-analiz.json tasarim/freecad/iskelet/iskelet-montaj.FCStd tasarim/freecad/iskelet/iskelet-montaj.step \
  tasarim/freecad/kabuk/kabuk-analiz.json tasarim/freecad/kabuk/kabuk-montaj.FCStd tasarim/freecad/kabuk/kabuk-montaj.step \
  tasarim/freecad/kafa/kafa-analiz.json tasarim/freecad/kafa/kafa-montaj.FCStd tasarim/freecad/kafa/kafa-montaj.step \
  tasarim/freecad/omuz/omuz-analiz.json tasarim/freecad/omuz/omuz-baski.json tasarim/freecad/omuz/omuz-montaj.FCStd \
  tasarim/freecad/omuz/omuz-montaj.step tasarim/freecad/omuz/regresyon/sonra.json tasarim/freecad/omuz/stl/omuz-gobegi.stl \
  tasarim/freecad/taban/taban-analiz.json tasarim/freecad/taban/taban-montaj.FCStd tasarim/freecad/taban/taban-montaj.step \
  tasarim/freecad/montaj/montaj-analiz.json tasarim/freecad/montaj/robot-montaj.step \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama-tani.json tasarim/freecad/lale158/lale158-kontrol.json \
  tasarim/freecad/iskelet/gorsel/*.png tasarim/freecad/omuz/gorsel/*.png tasarim/freecad/dirsek/gorsel/*.png \
  tasarim/freecad/kafa/gorsel/*.png tasarim/freecad/taban/gorsel/*.png
# 3) F4c / baski
git add planlama/y2/Y2b-baski.json planlama/baski-listesi.md planlama/d158/F4c-dogrula.py planlama/d158/F4c-liste.py \
  planlama/d158/F4c-partiler.py planlama/d158/F4c-partiler.json planlama/d158/F4c-partiler.md
# 4) montaj
git add tasarim/freecad/montaj/montaj_gorsel.py tasarim/freecad/montaj/robot-montaj.FCStd \
  tasarim/freecad/montaj/gorsel/montaj-*.png
# 5) planlama/d158
git add planlama/d158/regresyon.json planlama/d158/regresyon-son-kosu.json planlama/d158/F6a-gunluk.md \
  planlama/d158/F6a-eklem_sinirlari-oneri.json planlama/d158/F6a-dis-kok.png \
  planlama/d158/F6a-regresyon-oneri/omuz-once.json planlama/d158/F6a-regresyon-oneri/iskelet-once.json \
  planlama/d158/F6a-kontrol.md
```

**K23 notu (korunuyor):** 13 kabuk PNG'si ve `montaj/yerlesim-kontrol.json` şimdilik commit dışında; K23 Ahmet'in kararı.

**Commit'ten önce (değişmedi):**
- `py -3 tasarim/freecad/carpisma_kos.py kontrol` → 0 olmalı.
- Tarama kaynaklarına checkout, reset ya da stash uygulanmamalı (D-7).

## Commit mesajı önerisi (grup başına tek satır)

1. `F6a: omuz göbeği diş kökü r 1,5 yay ve kesit kaydırma; tarama sonucu (17 kaynak özeti, 10 bölüm)`
2. `F6a: modül çıktıları yeniden üretildi (analiz, FCStd, STEP, göbek STL, uygulama ölçümleri, modül görselleri)`
3. `F6a: F4c ve baskı listesi güncellendi (K39 kök yayı uygulandı, göbek 63,3–70,4 g, fark −22,4 g)`
4. `F6a: montaj_gorsel 1,58 m modele uyarlandı (yasak kutu koruması, kamera BOY/UZAMA'dan, tilt ≤ 13); montaj görselleri ve GUI kaydı`
5. `F6a: tasarım günlüğü, eklem sınırları ve regresyon önerileri, B kontrol raporu`
