# F9d kontrolü: herkese açık depo temizliği (P9.4), 09.11.2026

Ajan B (bağımsız kontrol). Brief `planlama/d158/F9d-brief.md`, A çıktısı `F9d-gunluk.md`, `F9d-tarama.py` ve `git diff`.
A'nın günlüğüne dayanılmadı; her sayı aşağıdaki komutlarla yeniden ölçüldü. Kendi betiklerim depo dışında, "scratchpad" klasöründe
(`b_yol.py`, `b_fark.py`, `b_kos.py`, `b_ad.py`); kullanıcı adı ortam değişkeninden, takma ad `git remote` adresinden çalışma anında
okundu, hiçbir dosyaya yazılmadı. Kullanıcı adı `<K>` diye maskelendi. Git'te yalnız okuma; commit, silme, FreeCAD yok.
F7d'nin alanına (`rehber/`, `tasarim/freecad/rehber/`, `planlama/rehber/`, `tasarim/cad/viewer-template.html`, `F7d-*`) dokunulmadı.

## Karar: **KOŞULLU GEÇER**

34 dosyanın içeriği doğru: kayıt ajanı bu listeyi şimdi commit'leyebilir (commit'lenen ağaç kendi içinde tutarlı).
Koşullar, iki orta bulgu:
- **K1 (O-1):** F7d'nin yeniden ürettiği rehber şu an 54 sayfa. README'deki "53 sayfa" F7d commit'inden sonra eskiyecek.
  Son commit'i atan ajan `py -3 planlama/d158/F9d-tarama.py --ozet` çıkış 0 almalı; gerekirse README'de tek sayı değişir.
- **K2 (O-2):** README "Parça / kütle" satırındaki üç sayı kaynak JSON'lardan eski. Bu commit'e tek satır düzeltme olarak ya da
  P9.3 sonuç raporundan önce düzeltilmeli.

Bulgular: **kritik 0 · orta 2 · düşük 5.**

## Bulgular

### Orta
**O-1 · README PDF sayfa sayısı F7d ile kaydı.** README "(53 sayfa)" diyor. HEAD'deki `kontrol.json` `yazdir.pdf_sayfa` = 53 ve
HEAD PDF'i 53 sayfa, yani commit'lenen hâl tutarlı. Ancak F7d çalışma ağacında rehberi yeniden üretti (20:31):
`kontrol.json` `yazdir.pdf_sayfa` = **54**, `sayfa_esleme` en büyük sayfa 54, PDF 4.020.208 B / 54 sayfa. A'nın kendi betiği
`F9d-tarama.py --ozet` şimdi **çıkış 1** veriyor ("54 sayfa YOK", uyuşmazlık 1). A'nın günlüğündeki "README uyuşmazlığı 0"
ölçümü 20:23–20:25 arası, F7d üretiminden önce. README F7d'nin yazma alanında değil, bu yüzden son sayı kimin commit'inde
düzeltilecekse onun kayıt adımında `F9d-tarama.py` 0 şartı konmalı (K1). Betiğin bu kaymayı yakalaması doğru tasarım.

**O-2 · README kütle satırı eski (brief madde 3 "sayı satırları").** README:40 (A dokunmadı, A'nın karşılaştırma listesinde yok):

| README | Kaynak | Bugünkü değer |
|---|---|---|
| ana montaj 25.715,6 g (MA `kutle_g`) | `tasarim/freecad/montaj/montaj-analiz.json` `kutle_g` | **25.720,55** (F2 `ff1c2e9` 25.720,49 → F6a `a051281` 25.720,55) |
| ev pozu **26.115,6 g** | `uygulama-ivme.json` `ev.kutle_g` | **26.120,6** |
| AM (−0,03; 522,71; −10,03) | `uygulama-ivme.json` `ev.am` | **(−0,03; 522,84; −10,03)** |

Aynı tablonun öteki sayıları tutuyor: 1.179 (`parca_sayisi`), boy 1.580,0 (`toplam_boy_mm`, `boy_mm`), taban 520, pay 1,519 / 2,097,
tilt 3,64 / pan 2,21, kafa grubu 1.570,8 (`kafa-analiz.json` `tork.tilt.kutle_g`), mikrofon-hoparlör 574,3.
Bölüm başlığı "sayılar 09.11.2026" dediği için herkese açık README'de yanlış sayı kalıyor. Düzeltme tek satır (K2).

### Düşük
**D-1 · HEAD'de kullanıcı adlı 13 satır kalıyor (9 dosya).** Hepsi brief'in yazma izni dışında, A'nın gerekçeleri doğru (aşağıda §1b).
Ancak 5 belgedeki 9 satır (`planlama/y2/Y2a-brief.md`, `Y2b-brief.md`, `planlama/y3/Y3-brief.md`, `tasarim/freecad/README.md`,
`qled-cerceve-tasarim-notu.md`) aynı önek dönüşümüyle kolayca temizlenebilir. Sonraki pakete öneri: bu 5 belge, ardından
`taslak_rapor.py` ile `rapor.html` birlikte (üretici + çıktı), sonra `prof-head-kabuk.txt`. `2209b-cad-sonuclar.json` için
üretici bulunmalı (izlenen dosyalarda `png_tam_yol` yalnız bu JSON'da geçiyor). Geçmişte 29 commit'te yol var
(`git log --all -G`); yazar ve committer alanlarında 0.

**D-2 · KT-F9d-1'de "120 `adim-*.png` blob'u" etiketi.** 120 sayısı `telefon-360-adim-*.png` dosyalarının 9 blob'unu da içeriyor.
Yalnız `adim-*.png`: **111 blob, ham 14.845.781 B, diskte 14.489.931 B** (%97,6). Telefon dahil 120 / 15.665.471 / 15.287.573 (A ile aynı).
Öneriyi değiştirmiyor.

**D-3 · `planlama/adim1/pi_kafada_olcum.py` çalışma kopyası karışık satır sonu** (`git ls-files --eol`: `w/mixed`; 194. satırdan
sonrası LF). A'nın değiştirdiği satır 2'de değil. `core.autocrlf=true` ve index LF olduğu için commit'lenen blob LF olur:
`git diff --numstat` 1/1, `--ignore-cr-at-eol` ile aynı (30 dosya, +35 −35). Etkisi yok. 7 dosya `w/crlf`, 23 dosya `w/lf`;
hepsi `i/lf`.

**D-4 · README demo satırında "Bu sürüm `lale-duzeltme` dalında".** Bu bir `main` birleştirme iddiası değil, doğru. Ama dal `main`'e
birleşince eskir; birleştirme commit'inde kaldırılmalı.

**D-5 · `carpisma_kos.py` `expanduser("~")` başka makinede başka profili gösterir.** Bu makinede değer bayt bayt aynı (aşağıda §2).
Davranış farkı yalnız başka bir kullanıcıda ortaya çıkar ve istenen yönde (taşınabilirlik). Bir kusur değil, not olarak düşüldü.

## 1. Yerel yol (madde 1)

### 1a. Bağımsız tarama
`scratchpad/b_yol.py`: `git ls-files` ile izlenen tüm dosyalar ve 3 `F9d-*` dosyası, çalışma ağacından okundu. Üç desen var:
1. sürücü (`X:`, `/x/`, `/mnt/x/`) + ayraç + `Users` + ayraç;
2. `Users` + ayraç + herhangi bir ad;
3. kullanıcı adının kendisi (büyük/küçük harf duyarsız, desenden bağımsız).

Ayraç olarak tek `\`, JSON kaçışlı `\\`, `/`, `%5C` ve `%2F` kabul edildi. İkili dosyalarda (NUL içeren) ad bayt düzeyinde arandı.
A'nın deseninden farklı olarak ad harfle başlamak zorunda değil; adın kendisi de ayrıca aranıyor.

| Ölçüm | Komut | Çıkış | Sonuç |
|---|---|---|---|
| HEAD, ad geçen satır / dosya | `git grep -I -i -F -n -e <K> HEAD \| wc -l` (ve `-l`) | 0 | **48 / 39** |
| Çalışma ağacı, izlenen | `git grep -I -i -F -n -e <K>` (ve `-l`) | 0 | **13 / 9** |
| İkili izlenen dosyada ad | `git grep -i -F -l -e <K>` (`-I` yok) | 0 | 9 (aynı 9 metin dosyası; ikili 0) |
| Bağımsız desen taraması | `B_KULL=<K> py -3 scratchpad/b_yol.py .` | 0 | 27 satır / 14 dosya, bunun **13'ü adlı** (9 dosya); kalan 14 satır adı taşımayan, önceden kısaltılmış `X:\Users\...` / `<kullanıcı>` anlatımı (F4b günlüğü / raporu, F6a-kontrol:218, F9d günlüğü ve betiği) |
| **Yazılabilir alanda adlı satır** | aynı | 0 | **0** (README, `planlama/d158/`, 16 betik ve `F9d-*` içinde 0) |
| A'nın betiği | `TAKMA_AD=… py -3 planlama/d158/F9d-tarama.py --ozet` | **1** | yol: 13 / 9, yazılabilir 0 (A ile aynı); çıkış 1 nedeni README (O-1) |

Önce / sonra: 48 / 39 → 13 / 9. A'nın düzelttiği 35 satır / 30 dosya ile A'nın sayıları tutuyor.

### 1b. Kalan 13 satırın gerekçesi (tek tek)

| Dosya:satır | Tür | B denetimi | Gerekçe geçerli mi |
|---|---|---|---|
| `planlama/y2/Y2a-brief.md:19` | belge | yazma izni yalnız `planlama/d158/` eski belgeleri | evet (D-1) |
| `planlama/y2/Y2b-brief.md:13` | belge | aynı | evet (D-1) |
| `planlama/y3/Y3-brief.md:23`, `:28` | belge | aynı (aynı klasördeki `Y3_erisim.py` betik olduğu için izinliydi, düzeltilmiş) | evet (D-1) |
| `tasarim/freecad/README.md:43`, `:47`, `:48`, `:92` | belge | README izni yalnız kök `README.md` madde 3 | evet (D-1) |
| `tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md:37` | belge | yazma listesinde yok | evet (D-1) |
| `tasarim/freecad/taslak-170/taslak_rapor.py:458` | betik | yol, ürettiği HTML'in metninde; değiştirmek çıktıyı değiştirir (brief: "çıktıyı değiştirmiyorsa") | evet |
| `tasarim/freecad/taslak-170/rapor.html:154` | üretilmiş çıktı | yukarıdakinin çıktısı, aynı metin | evet |
| `tasarim/freecad/lale158/2209b-cad-sonuclar.json:6` | JSON (kaçışlı `\\`) | üretilmiş JSON dokunulmaz; `git grep png_tam_yol` yalnız bu dosya | evet |
| `tasarim/freecad/lale158/ikinci/yavaslik/prof-head-kabuk.txt:72` | üretilmiş çıktı (cProfile) | FreeCAD `site-packages` yolu | evet (zayıf: dokunulmaz listesinde açıkça yok, ama ölçüm çıktısı) |

Tarama kaynaklarında, `kod/`, F7d / F7c alanında ve `CLAUDE.md`'de adlı satır 0.
Geçmiş: `git log --all --format=%h -i -G "<sürücü>:<ayraç>Users<ayraç><K>" | wc -l` → **29** (125 commit içinde; A ile aynı).
Yazar / committer alanında ad: 0.

## 2. Betik değişiklikleri (madde 2)

| Ölçüm | Komut | Çıkış | Sonuç |
|---|---|---|---|
| AST HEAD ↔ çalışma ağacı (16 betik) ve satır çifti denetimi (30 dosya) | `B_KULL=<K> py -3 scratchpad/b_fark.py . liste30.txt` | 0 | **AST 15 / 15 aynı**, farklı yalnız `carpisma_kos.py`; 16 betiğin hepsi `compile()` geçti |
| FreeCAD'siz betikler | her betikte `import FreeCAD/Part/…` sayımı | 0 | 15'i FreeCAD betiği; yalnız `carpisma_kos.py` FreeCAD'siz (aşağıda koşuldu) |
| Kaynak özetine giren dosya mı | `carpisma_kos.kaynak_listesi()` + `KAYNAK_SABIT` | 0 | 17 = 11 sabit + 6 `*_lib.py`; değişen 16 betiğin hiçbiri listede değil |
| Başka izleyici | `git grep` `md5/sha256` + `getmtime/st_mtime` | 0 | Değişen betiklerin özetini ya da saatini izleyen kod yok. `demo_uret.py` `KAYNAK` 10 JSON / GLB, değişen dosya yok. `omuz-baski.json` yalnız betik adını yazıyor |

**`carpisma_kos.py`** (`scratchpad/b_kos.py`): HEAD kaynağı `git show` ile okundu ve gerçek dosya yolu `__file__` alınarak bellekte
çalıştırıldı (depoya yazılmadı).
- `BASLATICI` HEAD ↔ çalışma ağacı: **eşit (dize eşitliği)**, dosya var. `os.path.expanduser` Windows'ta `HOME`'u değil `USERPROFILE`'ı
  kullanır; Git Bash altında da (HOME tanımlı) eşit çıktı.
- `kaynak_listesi()` ve `KAYNAK_SABIT` HEAD ile aynı (17). `FC` aynı. Fonksiyon dışındaki üst düzey değerlerde fark yok (`[]`).
- `kontrol` çıktısı HEAD kodu ↔ çalışma ağacı kodu: **bayt bayt aynı**, ikisi de çıkış 0, sha256 `e7f821b8094b`.
  Metin: "carpisma-sonuc.json guncel: izlenen 17 dosyanin ozetleri kayitla ayni."
- `BASLATICI` yalnız `kos()` içinde `subprocess.call([FC, BASLATICI])` olarak kullanılıyor (`git grep BASLATICI`: 2 satır).
- `carpisma_kos.py` kendisi tarama kaynağı değil.

**`omuz_baski.py` tarama kaynağı değil (kesin).** `kaynak_listesi()` içinde yok. `KAYNAK_SABIT`'te `omuz/omuz_parcalar.py` var,
`omuz_baski.py` yok. `omuz/` altında `*_lib.py` yalnız `omuz_lib.py`. Daha önceki anılışı `F4b-kontrol.md:31`'de: orada bir
*izleyici* olarak geçiyor (kendisi `omuz_parcalar.py`'nin sha256 / mtime değerini sonuca yazar), kaynak olarak değil. Değişikliği
yalnız 11. satırdaki yorum (AST aynı).

## 3. Anlam (madde 3)
`git diff --word-diff=porcelain --word-diff-regex='[^[:space:]]+'` 30 dosyada çalıştırıldı. Değişen her sözcük çifti yol öneki
(`X:\Users\<K>` → `%USERPROFILE%`, `X:/Users/<K>` → `~` ya da `%USERPROFILE%/`), tek istisna `carpisma_kos.py:47` (§2).
`b_fark.py` satır çifti denetimi: 35 değişen satır çifti; önek normalize edildikten sonra 34 çift birebir aynı, 1 çift beklenen
kod farkı (`carpisma_kos.py`). Yapısal fark (satır ekleme / silme) 0. Yeni satırlarda ad 0. `git diff --numstat` her dosyada
eklenen = silinen, toplam +35 −35. `git diff --check` → 0.

## 4. README (madde 4)
`git diff -- README.md`: +11 −10, değişen satırlar yalnız klasör tablosundaki rehber, demo, `robot_cad.py` ve `demo_uret.py` satırları
ile "Montaj rehberini üretme" ve "CAD'i yeniden üretme" paragrafları.

| İddia | Kaynak / komut | Ölçülen | Sonuç |
|---|---|---|---|
| 50 adım | `kontrol.json` `ozet.adim` (= `yazdir.adim`) | 50 | ✅ |
| 1.192 parça | `ozet.parca_rehber` = `parca_mesh` = `denetim.parca`; `rehber-veri.json` `parcalar` 1192 (HEAD ve çalışma ağacı) | 1192 | ✅ |
| PDF 53 sayfa | HEAD `kontrol.json` `yazdir.pdf_sayfa` 53, eşleme en büyük 53, HEAD PDF 53 sayfa; **çalışma ağacı 54** | 53 / 54 | ⚠ O-1 |
| 127 JSON anahtarı | demo `<script id="kaynak">` `anahtarlar` (sözlük) | 127 | ✅ |
| boy 1.580 mm, `toplam_boy_mm` | `lale158-kontrol.json` 1580.0; demo `anahtarlar.boy` aynı yol | 1580.0 | ✅ |
| 3B model `robot-glb.js` + `rehber-veri.js`, göreli, 1.192 | demo `kaynak.model.script`, `dugum` 1192; `<script src>` yalnız bu ikisi ve three.js CDN | aynı | ✅ |
| açık kararlar "karar bekliyor" | demoda 36 geçiş | var | ✅ |
| maliyet `planlama/maliyet.json` | `demo_uret.py` `KAYNAK.maliyet` | var | ✅ |
| `robot_cad.py` eski, demoya girmez; "sonunda demo da yeniden üretilir" | `demo_uret.py:16-20`; `robot_cad.py:1046-1047` `demo_uret.build(MODEL_JSON)` | aynı | ✅ |
| `demo_uret.py` FreeCAD / CadQuery gerekmez | yalnız standart kütüphane import'ları (satır 24-31) | aynı | ✅ |
| denetim `F9b-dogrula.py` | izleniyor | var | ✅ |
| seçiciler `rehber_secici.py` (1,58 m) | dosya başlığı "parça → adım seçicileri, 1,58 m modeli (F7a)"; `R-gunluk.md:46` "seçiciler `rehber_secici.py`'de" | aynı | ✅ |
| "3B görünüm için internet gerekir" | three.js cdnjs'ten | aynı | ✅ |
| demo eskiden "125 cm CadQuery" idi | `main` / `origin/main` başlık "Robot Tasarım Demosu", `kaynak` bloğu yok; HEAD "Lale Tasarım Demosu" | doğru | ✅ |

**Pages ve `main`:** README'de `http`, `github.io` ya da Pages bağlantısı HEAD'de de çalışma ağacında da yok (0). `http|pages|main|birleş`
geçen satırlar HEAD ile birebir aynı (`diff` boş). Tek `main` geçişi (README:44, "main'deki kod ±20") A'dan önce de vardı. Yeni
birleştirme iddiası yok (D-4). Dokunulmayan tablo satırı için O-2.

## 5. Takma ad ve soyad (madde 5)
Biçim F6a'daki gibi: harf duyarsız, alt dize. Ad `git remote` adresinden çalışma anında türetildi. Soyadlar `tubitak-2209b/BAGLAM.md`
ekip ve danışman tablosundan çalışma anında okundu (6 kişi, 9 aday sözcük). Sözcük sınırıyla, büyük harfli arandı (`scratchpad/b_ad.py`).

| Küme | Komut | Çıkış | Takma ad | Başka öğrenci / danışman soyadı |
|---|---|---|---|---|
| Commit listesi 34 dosya | `py -3 scratchpad/b_ad.py . liste34.txt` | 0 | **0** | **0** |
| İzlenen tüm depo | `F9d-tarama.py --ozet` | 1 (O-1) | 6 satır / 3 dosya (`CLAUDE.md` K25, `kod/…/eklem_sinirlari.json`, `tasarim/freecad/index.html` K26; A ile aynı) | — |
| KT-F9d-3'te "commit" önerilen 7 izlenmeyen dosya | `b_ad.py` + `grep -c <K>` | 0 | 0 | 0; yerel yol 0 |

Not: commit listesindeki 3 dosyada (`README.md:59`, `F1b-brief.md:55`, `F2-brief.md:48`) yalnız **Ahmet'in kendi soyadı** geçiyor.
Bu satırlar HEAD'de de var, A eklemedi ve brief'in "kişi gerekiyorsa Ahmet" kuralıyla çelişmiyor.

## 6. Karar taslakları (madde 6)

**KT-F9d-1 (D-9 PNG):** seçenek 3 (a / b / c), önerilen varsayılan b, etkisi bayt olarak verilmiş. ✅ Ölçümler:
- `git count-objects -vH`: gevşek 2975 nesne / 439,65 MiB, paket 267 / 474,60 KiB, `prune-packable` 2; `du -sb .git` 461.680.698 B.
  A ile aynı.
- HEAD `planlama/rehber/goruntu/`: 57 PNG / 7.101.641 B; `adim-*.png` 50 / 6.482.146 B; `rehber/goruntu/` 50 / 3.261.137 B;
  HEAD PDF 4.008.893 B. A ile aynı.
- Commit başına yeni blob (`git diff-tree` + `cat-file -s`):
  - `887bcfe`: adım 50 / 6.465.071, `rehber/veri` 4 / 6.712.795.
  - `649885f`: adım 50 / 6.451.048, telefon 7 / 609.971, `rehber/goruntu` 50 / 3.261.137, PDF 3.987.397. Toplam 14,31 MB;
    adım + `rehber/goruntu` + PDF 13,70 MB.
  - `e448eab`: adım 3 / 570.321, telefon 2 / 209.719, PDF 4.008.893 (4,79 MB).
  - Üçü birlikte 25,6 MB (`rehber/veri` hariç). A ile aynı.
- Geçmiş blob'ları diskte 461.054.615 B; `.step` 172,4 MB, `.FCStd` 135,1 MB, `.html` 67,1 MB, `.png` 48,7 MB. `git-lfs/3.7.1` kurulu.
  A ile aynı. Etiket farkı için D-2.
- Çalışma ağacında F7d'nin yeniden üretimi şu an `adim-*.png` toplamını 6.509.113 B yapıyor (4 adım + 2 telefon değişmiş).
  Öneriyi değiştirmez; F7d'nin konusu.

**KT-F9d-2 (`tasarim/cad/lale158-model.js`):** seçenek 3 (sil / `.gitignore` / bırak), etki verilmiş, öneri sil. ✅ Ölçümler:
- 3.495.365 B, tarih 09.11 17:30. Başlıkta "Ureten: tasarim/cad/demo_uret.py".
- `git log --all` 0 commit. İçindeki `glb_sha256` (`760bf1ff5955…`) bugünkü `rehber/veri/robot.glb` sha256 ile aynı;
  `robot.glb` değişmemiş.
- Demoda ve `viewer-template.html`'de "lale158-model" 0 geçiyor. `demo_uret.py:20` "artik uretilmez".
  `F9b-dogrula.py:522-523` sayfa bu dosyaya bağlanırsa hata veriyor.
- `rapor/lale158-model.js` (1.978.949 B) ayrı bir dosya; A da öyle ayırmış.

**KT-F9d-3 (izlenmeyenler):** girdi başına öneri, neden ve bağlı karar verilmiş, toplu sayısal etki var
(`.gitignore` 5 girdi, 128.140.134 B ≈ 128,1 MB, `git status` −5 satır). ✅ Ölçümler:
- `kvkk/` 16 / 3.142.451, `rapor/` 20 / 11.087.000, `tubitak-2209b/` 267 / 110.862.910, `kafa-yerlesim/kaynak/` 5 / 3.047.767,
  `tasarim/solidworks/` 6 / 28.676.311.
- `F5-pano-govde.txt` 1.862, `F5b-pano-govde.txt` 2.310, `FREECAD-KILIT.txt` 6, `lale_dongu.FCMacro` 17.760,
  `lale_dongu_ac.bat` 1.421, `11-6-inc-…sigma.md` 9.546, `raporlar/kaynaklar/` üç dosya 40.862 B.
- Hepsi A ile aynı. Seçenekler satır başına tek öneri olarak yazılmış; seçenek kümesi ortak (commit / `.gitignore` / bekle), yeterli.
- Not: A'nın tablosundan sonra `planlama/d158/F7d-gunluk.md` (F7d, bekle) eklendi.

## 7. Bütünlük (madde 7)

| Komut | Çıkış | Sonuç |
|---|---|---|
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** | "GEÇER (hepsi okundu, kötüleşen yok)" |
| `carpisma_kos.py kontrol` HEAD kodu ↔ çalışma ağacı kodu (`b_kos.py`) | 0 / 0 | çıktı bayt bayt aynı (§2) |
| `git diff --check` (31 değişen dosya) | 0 | boşluk hatası yok |
| `ast.parse(F9d-tarama.py)` | 0 | geçti |

Değişen betiklerden FreeCAD'siz ve hızlı koşan tek betik `carpisma_kos.py`; çıktısının değişmediği yukarıda gösterildi.
Öteki 15 betik FreeCAD gerektiriyor ve AST'leri HEAD ile aynı.

## 8. Commit listesi (madde 8)
`git status --porcelain` ile karşılaştırıldı:
- A'nın 31 değiştirilmiş dosyasının her birinde yalnız F9d değişikliği var (README dışındakiler 35 önek satırı, README +11 −10).
  F7d'nin hiçbir hunk'ı bu dosyalara karışmamış.
- Değiştirilmiş olup listede olmayanlar başka paketlerin:
  - `planlama/dongu-158.md`: orkestratör.
  - F7d: `rehber/veri/rehber-veri.js` / `.json`, `tasarim/cad/viewer-template.html`, `tasarim/freecad/rehber/rehber_denetim.py`
    ve `rehber_metin.py`, `planlama/rehber/` (PDF, `kontrol.json`, 4 `adim-*.png`, 2 `telefon-*.png`).
  - K23: 13 kabuk PNG ve `yerlesim-kontrol.json`.
- Eksik dosya yok; fazla dosya yok. Listeye bu kontrol dosyası eklenmeli. Kesin liste **35 dosya**.

### Kesin `git add` listesi (35)
```
git add -- README.md \
  planlama/adim1/pi_kafada_olcum.py planlama/adim1/pi_kafada_tabla.py \
  planlama/adim2/K-olcum.py planlama/adim2/K2-dudak.py planlama/adim2/K2-geo.py planlama/adim2/K2-kablo.py \
  planlama/adim2/S1-duzeltme-kontrol.py planlama/adim3/K3_cad_olcum.py planlama/adim4/M6_erisim.py planlama/y3/Y3_erisim.py \
  planlama/d158/F0-brief.md planlama/d158/F1a-brief.md planlama/d158/F1a-gunluk.md \
  planlama/d158/F1b-brief.md planlama/d158/F1b-gunluk.md planlama/d158/F1b-kontrol.md \
  planlama/d158/F2-brief.md planlama/d158/F2-gunluk.md planlama/d158/F2-kontrol.md planlama/d158/F3a-kontrol.md \
  planlama/d158/F6a-brief.md planlama/d158/F6a-gunluk.md planlama/d158/F6a-kontrol.md planlama/d158/F7a-kontrol.md \
  tasarim/freecad/carpisma_kos.py tasarim/freecad/kafa/kafa_gorsel.py tasarim/freecad/omuz/omuz_baski.py \
  tasarim/freecad/taslak-170/taslak_analiz.py tasarim/freecad/taslak-170/taslak_gorsel.py tasarim/freecad/taslak-170/taslak_montaj.py \
  planlama/d158/F9d-brief.md planlama/d158/F9d-tarama.py planlama/d158/F9d-gunluk.md planlama/d158/F9d-kontrol.md
```
Commit'ten sonra `git show --stat HEAD` 35 dosya göstermeli. `git add -A` ya da `git add .` kullanılmamalı.

### Commit mesajı önerisi
```
Lale P9.4: herkese açık depo temizliği: yazılabilir alanda yerel yol 35 → 0 (F9d)

- 14 eski paket belgesi ve 16 betikte yalnız yol öneki %USERPROFILE% / ~ oldu; 15 betikte AST aynı,
  carpisma_kos.py BASLATICI expanduser("~") ile (değer ve kontrol çıktısı aynı)
- Depoda kalan 13 satır gerekçeli (yazma listesi dışı belgeler, üretici / üretilmiş çıktı); geçmiş yeniden yazılmadı
- README: rehber (50 adım, 1.192 parça, PDF), demo (1,58 m, F9b, 127 anahtar), robot_cad / demo_uret satırları kaynak JSON'larla
- Karar taslakları KT-F9d-1…3 (D-9 PNG, lale158-model.js, izlenmeyenler) günlükte; kontrol B: KOŞULLU (O-1 PDF sayfa F7d ile, O-2 README kütle satırı)
- kontrol 0, regresyon 0
```

## Yeniden kontrol (düzeltme 1), 09.11.2026

Dar yeniden kontrol: A'nın günlüğü §7, `git diff` ve çalışma ağacı. Ölçümler yine bağımsız (scratchpad betikleri
`b_maliyet.py`, `b_fark.py`, `b_yol.py`, `b_ad.py`). F7d çalışma ağacında rehberi ve demoyu yeniden üretmiş durumda; o dosyalara
dokunulmadı.

### Karar: **GEÇER** (kayıt sırası şartıyla)
O-1, O-2 ve D-1 kapandı. D-2 düzeltildi; D-3, D-4 ve D-5 yanıtlandı. Yeni bulgu: kritik 0, orta 0, düşük 1 (D-6).
**Kayıt şartı (K1'):** README "(54 sayfa)" yalnız çalışma ağacındaki F7d `kontrol.json`'uyla tutarlı; HEAD'de hâlâ 53 var.
Bu yüzden şu sıra izlenmeli:
1. Önce F7d commit'lenir.
2. F9d `git add`'inden hemen önce `git diff --quiet HEAD -- planlama/rehber/kontrol.json` 0 dönmeli (F7d'nin son hâli commit'te).
3. Aynı anda `F9d-tarama.py --ozet` de 0 dönmeli.

F7d yeniden üretirse ve sayfa sayısı değişirse README'deki tek sayı ona uyar. F9d, F7d'den önce commit'lenmemeli.

### 1. README: sayılar JSON ile
Bütün sayılar kaynak dosyalardan yeniden okundu ve README:36–51 satırlarıyla karşılaştırıldı. **Uyuşmazlık 0.**

| README | Kaynak · anahtar | Ölçülen |
|---|---|---|
| 1.580,0 mm; boy 1.580 | LK `toplam_boy_mm`; MA `boy_mm` | 1580.0 / 1580.0 |
| gövde direği 1.115,5 mm | BOM "Sigma 40x40 agir kanal 10, 1115.5 mm" × 1 | ✅ |
| merkezi y 1.270; uzatma 315 | MA `s3_mm`; `uzama_mm` | 1270.0; 315.0 |
| 1.179 parça; ana montaj 25.720,55 g; taban 520 | MA `parca_sayisi`; `kutle_g`; `taban_w_mm` | 1179; 25720.55; 520.0 |
| 400 g; **26.120,6 g**; AM (−0,03; 522,84; −10,03) | UI `kablo_payi.kutle_g`; `ev.kutle_g`; `ev.am` | 400.0; 26120.6; [−0.03, 522.84, −10.03] |
| teker izi 432, x ±216 | `Y2b-ivme.json` `teker_hatti.iz_genisligi`, `.x` | 432.0; 216.0 |
| akü 3,0 kg | BOM LiFePO4 kalemi, toplam kütle | 3000.0 g |
| pay 1,519; düz 2,097 | UI `izgara_yuk_0g.a_sinir_pay15.rampa5_geri` / `.duz_geri` | 1.519; 2.097 |
| DS3235 × 4; MG996R × 6; toplam 10 | BOM adet | 4; 6 |
| kafa grubu 1.570,8; tilt 3,64; pan 2,21 | KA `tork.tilt.kutle_g`, `.pay_tilt15`, `tork.pan.pay_iki_hane` | 1570.8; 3.64; 2.21 |
| tilt ±13°; S2 ≥ +5° | `eklem_sinirlari.json` `eklemler.tilt.min/max`; `r_s2.min` (= `l_s2.min`) | −13/13; 5.0 |
| ≤ 0,1 rampa; düz ivme ≤ 0,5, fren ≤ 1,8 | `teker.ivme_sinir_m_s2` | rampa 0.1/0.1; düz 0.5/1.8 |
| mikrofon-hoparlör 574,3 | `uygulama-olcum.json` `mic_hoparlor.poz_min_mm` | 574.3 |
| baskı 72 (13'ü destekli); 7.668,9–7.726,7 g; 159,9–161,08 sa; klasör tablosu 72 | `baski-analiz.json` `toplam.adet`, `.destekli_adet`, `.toplam_g`, `.sure_sa` | 72; 13; [7668.9, 7726.7]; [159.9, 161.08]. `baski-listesi.md:11-12` da 72 |
| rehber 50 adım; 1.192 parça; (54 sayfa) | `kontrol.json` `ozet.adim`, `ozet.parca_rehber`, `yazdir.pdf_sayfa` (eşleme en büyük 54) | 50; 1192; 54 (çalışma ağacı; HEAD 53, K1') |
| demo 127 anahtar; 1.192 düğüm; `lale158-model` 0 | demo `script#kaynak` (çalışma ağacı ve HEAD) | 127 (HEAD 127); 1192; 0 |

**Maliyet satırı** (A değiştirmedi; `scratchpad/b_maliyet.py` hesabı, `viewer-template.html` `on()` / `calc()` kuralıyla).
Kural: V3, yazıcı, yedek dahil, pay 0,15. Betik `maliyet_toplam.py`'yi kullanmadı.

| README | Hesap | Sonuç |
|---|---|---|
| ≈ 118.700 TL | ara 103.188,02 × 1,15 | **118.666,22** ✅ |
| koşullularla ≈ 124.600 | `secenek: kosullu` dahil | **124.573,11** ✅ |
| elimizdekiler düşülürse ≈ 93.800 | `elde` bayraklı 3 kalem (ana bilgisayar, hafıza kartı, yüz ekranı; 21.648,48 TL) çıkar | **93.770,47** ✅ |
| QLED alınırsa ≈ 102.100 | (elde düşülmüş ara + `F8a-siparis.json` S76 `birincil.fiyat` 7.217,95) × 1,15 | **102.071,11** ✅ |
| sipariş paketi ≈ 107.600 | `F8a-siparis.json` `toplamlar.okul_butcesi_dahil_pay15` | **107.569,14** ✅ |
| bulunamayan 2 kablo fiyatsız, toplama girmiyor | `tl` boş kalem 2; V3 görünen fiyatsız 0 | ✅ |

Pages ve `main`: README'de bağlantı yine 0. `main` geçen tek satır (README:44) değişmedi. README +14 −13; yeni değişiklikler
yalnız satır 15 (54), 16 (baskı listesi) ve tablodaki kütle ile baskı satırları.

### 2. Yol ve ad
- **5 yeni dosya** (Y2a, Y2b, Y3 brief'leri, `tasarim/freecad/README.md`, `qled-cerceve-tasarim-notu.md`):
  - `git diff --numstat` her dosyada eklenen = silinen, toplam 9 satır.
  - `git diff --word-diff=porcelain`'de değişen sözcükler yalnız yol öneki: `X:\Users\<K>` → `%USERPROFILE%`; bash `X:/Users/<K>` →
    `$USERPROFILE`; PowerShell → `$env:USERPROFILE`. Kalanı aynı.
  - `b_fark.py`'nin 3 "fark" işareti yalnız bu kabuk değişkeni biçimleri; yapısal fark 0.
- **Önceki 30 dosya** yeniden ölçüldü:
  - +35 −35, değişmemiş.
  - AST 15 / 15 aynı; `carpisma_kos.py` beklenen fark.
- **İzlenen depoda kullanıcı adı:** `git grep -I -i -F -n -e <K>` → **4 satır / 4 dosya**:
  - `taslak_rapor.py:458` ve `rapor.html:154` (üretici ve çıktısı);
  - `2209b-cad-sonuclar.json:6`;
  - `prof-head-kabuk.txt:72`.

  Hepsi gerekçeli (§1b). Yazılabilir alanda 0. `F9d-*` dört dosyada 0. İkili dosyada 0.
- **Takma ad ve soyad** (`b_ad.py`, 40 dosya):
  - takma ad **0**;
  - başka öğrenci ya da danışman soyadı **0**;
  - yalnız Ahmet'in kendi soyadı, HEAD'de var olan 3 satırda.

  İzlenen depo genelinde takma ad 6 satır / 3 dosya, değişmedi (K25, K26, `kod/`).

### 3. `tasarim/freecad/README.md` komutları (echo, FreeCAD koşulmadı)

| Kabuk | Komut | Açılım (maskeli) | Denetim |
|---|---|---|---|
| Git Bash | `R="$USERPROFILE/OneDrive/Masaüstü/Robot/tasarim/freecad"` | `X:\Users\<K>/OneDrive/Masaüstü/Robot/tasarim/freecad` | klasör var; `normcase(normpath)` eski değerle **aynı** |
| Git Bash | `L=$USERPROFILE/.robot-cad/run_fc.py` | `X:\Users\<K>/.robot-cad/run_fc.py` | dosya var; eski değerle **aynı**; tırnaksız kullanımda 1 sözcük |
| Git Bash | `FC_SCRIPT=$R/iskelet/iskelet_montaj.py` | `…/tasarim/freecad/iskelet/iskelet_montaj.py` | hedef betik var |
| PowerShell 5.1 | argüman `$env:USERPROFILE\.robot-cad\run_fc.py` (komut kipinde tırnaksız) | `X:\Users\<K>\.robot-cad\run_fc.py` | `Test-Path` True; eski literal ile `-eq` **True**; `freecadcmd.exe` yolu var |

Metin satırı (`:43`) `%USERPROFILE%` biçiminde ve yalnız açıklama. Anlam korunuyor; komutlar ilgili kabukta çalışır biçimde.

**D-6 (düşük, yeni):** `L=$USERPROFILE/...` ve `"$FC" $L` tırnaksız. Profil yolunda boşluk olan başka bir makinede sözcük bölünür.
Bu makinede 1 sözcük, eski literal de tırnaksızdı. Taşınabilirlik için ileride `L="$USERPROFILE/.robot-cad/run_fc.py"` ve `"$L"`
önerilir. Bu commit'i engellemez.

### 4. Komutlar

| Komut | Çıkış | Sonuç |
|---|---|---|
| `TAKMA_AD=… py -3 planlama/d158/F9d-tarama.py --ozet` | **0** | yol 4 / 4, yazılabilir 0; takma ad 6 / 3; README uyuşmazlığı 0 |
| `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| `py -3 planlama/d158/regresyon.py --yazma` | **0** | GEÇER (hepsi okundu, kötüleşen yok) |
| `py -3 scratchpad/b_maliyet.py` | 0 | yukarıdaki maliyet tablosu |
| `git diff --check` (36 izlenen dosya) | 0 | — |
| `ast.parse(F9d-tarama.py)` | 0 | — |

### 5. Liste
`git status --porcelain` listeden çıkarıldığında kalanların hepsi başka paketin ya da izlenmeyen:
- orkestratör: `planlama/dongu-158.md`;
- F7d: `planlama/rehber/` (PDF, `kontrol.json`, `R-gunluk.md`, 4 `adim-*.png`, 2 `telefon-*.png`), `rehber/veri/rehber-veri.js` / `.json`,
  `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/viewer-template.html`, `tasarim/freecad/rehber/rehber_denetim.py` / `rehber_metin.py`,
  `F7d-brief.md`, `F7d-gunluk.md`;
- K23: 13 kabuk PNG ve `yerlesim-kontrol.json`;
- KT-F9d-3'teki izlenmeyenler.

Listede F7d dosyası yok, eksik dosya yok. **40 dosya, tam.**

### Kesin `git add` listesi (40; F7d commit'inden sonra, K1' denetimleri 0 iken)
```
git add -- README.md \
  planlama/adim1/pi_kafada_olcum.py planlama/adim1/pi_kafada_tabla.py \
  planlama/adim2/K-olcum.py planlama/adim2/K2-dudak.py planlama/adim2/K2-geo.py planlama/adim2/K2-kablo.py \
  planlama/adim2/S1-duzeltme-kontrol.py planlama/adim3/K3_cad_olcum.py planlama/adim4/M6_erisim.py \
  planlama/y2/Y2a-brief.md planlama/y2/Y2b-brief.md planlama/y3/Y3-brief.md planlama/y3/Y3_erisim.py \
  planlama/d158/F0-brief.md planlama/d158/F1a-brief.md planlama/d158/F1a-gunluk.md \
  planlama/d158/F1b-brief.md planlama/d158/F1b-gunluk.md planlama/d158/F1b-kontrol.md \
  planlama/d158/F2-brief.md planlama/d158/F2-gunluk.md planlama/d158/F2-kontrol.md planlama/d158/F3a-kontrol.md \
  planlama/d158/F6a-brief.md planlama/d158/F6a-gunluk.md planlama/d158/F6a-kontrol.md planlama/d158/F7a-kontrol.md \
  tasarim/freecad/README.md tasarim/freecad/carpisma_kos.py tasarim/freecad/kafa/kafa_gorsel.py \
  tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md tasarim/freecad/omuz/omuz_baski.py \
  tasarim/freecad/taslak-170/taslak_analiz.py tasarim/freecad/taslak-170/taslak_gorsel.py tasarim/freecad/taslak-170/taslak_montaj.py \
  planlama/d158/F9d-brief.md planlama/d158/F9d-tarama.py planlama/d158/F9d-gunluk.md planlama/d158/F9d-kontrol.md
```
Commit'ten sonra `git show --stat HEAD` 40 dosya göstermeli. `git add -A` ya da `git add .` kullanılmamalı.

### Commit mesajı önerisi
```
Lale P9.4: herkese açık depo temizliği: yerel kullanıcı yolu 48 → 4 satır, yazılabilir alanda 0 (F9d)

- 19 belge ve 16 betikte yalnız yol öneki değişti (%USERPROFILE% / ~; tasarim/freecad/README.md komutlarında
  $USERPROFILE / $env:USERPROFILE); 15 betikte AST aynı, carpisma_kos.py BASLATICI expanduser("~") (değer ve kontrol çıktısı aynı)
- Kalan 4 satır gerekçeli: taslak_rapor.py + rapor.html (üretici ve çıktısı), 2209b-cad-sonuclar.json, prof-head-kabuk.txt;
  geçmiş yeniden yazılmadı
- README sayıları JSON'la: rehber 50 adım / 1.192 parça / PDF 54 sayfa, demo 1,58 m (F9b, 127 anahtar), kütle 25.720,55 g /
  ev pozu 26.120,6 g, baskı 72 parça; F9d-tarama.py README'yi 38 satırda denetler
- Karar taslakları KT-F9d-1…3 (D-9 PNG, lale158-model.js, izlenmeyenler) günlükte
- B kontrolü: KOŞULLU, düzeltme 1 sonrası GEÇER; kontrol 0, regresyon 0, tarama 0
```
