# F4b bağımsız kontrol (P4.5a takma ad temizliği, birinci kısım + `regresyon.py` bayrak koruması) — 09.11.2026

Ajan B (kontrol). Okunan: `dongu-158.md` §2 (kurallar, kilit tablosu), `F4b-brief.md`, `F4b-gunluk.md` (iddia olarak; kanıt sayılmadı),
78 dosyalık `git diff`, `carpisma_kos.py`, `regresyon.py`. Her kontrol depo dışında (scratchpad) yazılan betiklerle yapıldı.
FreeCAD kullanılmadı. Normal regresyon modu koşulmadı. Depoda bu dosya dışında hiçbir şey değişmedi (regresyon testinden sonra
`find -newer` ile değişen dosya: 0). Bu dosyada takma ad, hesap adı ve kişisel yol yazılmaz.

## Genel karar: **KOŞULLU GEÇER**

Temizliğin kendisi (60 izlenen + 2 izlenmeyen dosya) ve `regresyon.py` değişikliği **tam geçer**: yalnız ad / tanımlayıcı
satırları değişmiş, tek bir sayı, tarih ya da karar metni değişmemiş, JSON'lar geçerli ve yapısal olarak aynı, tarama
kaynaklarına, `kod/`'a ve `CLAUDE.md`'ye dokunulmamış, kalan 12 dosya günlükle birebir. Koşullar yalnız günlükteki iki karar
taslağının metninde (2 satır) ve commit anında bir önkoşul. A'ya yeni tur gerekmiyor; C birebir uygulayabilir.

## Madde tablosu

| # | Madde | Sonuç | Kanıt |
|---|---|---|---|
| 1 | F4b dosya listesi = HEAD'deki takma ad listesi − kalan 12 | ✅ | `git grep -il` HEAD: 72 dosya. Günlük §2 tablosu: 60 izlenen + 2 izlenmeyen. HEAD listesi − günlük listesi = tam olarak kalan 12 dosya; günlük listesinde olup HEAD'de olmayan yalnız izlenmeyen 2 dosya. |
| 2 | Dosya başına satır sayısı | ✅ | 60 dosyada `git diff --numstat` günlük §2 tablosuyla birebir (60/60 eşleşti); toplam +195 / −195. Her dosyada eklenen = silinen. |
| 3 | Yalnız ad satırı mı (hunk düzeyinde betik) | ✅ | `git diff -U0`, hunk hunk: her hunk'ta − ve + satır sayısı eşit (eşitsiz hunk 0); silinen 195 satırın hepsinde takma ad var (takma adsız silinen 0); eklenen 195 satırda takma ad 0. Satır çiftlerinde karakter düzeyinde fark (difflib) yalnız şu kümeden: takma ad → `Ahmet` (177), Türkçe ek uyumu (`'nin`→`'in` 18, `'ye`→`'e` 4, `'de`→`'te` 1), takma ad → `Ahmet Yorulmaz` (3), takma adlı not deposu adı → "not deposu" / "kişisel not deposu (vault)" (6), ssh kullanıcısı → `<kullanıcı>` (1), geçici klasör yolunun takma adlı öneki → `...` (30). Başka hiçbir fark yok. |
| 4 | Sayı / tarih değişti mi | ✅ | Her satır çiftinde rakam dizileri karşılaştırıldı: farklı çıkan 30 satırın tamamı yol önekindeki oturum kimliği rakamları (2 profil `.txt` 29 satır + `qled-cerceve-tasarim-notu.md:134`); kalan sayı sütunları (ör. `100.217`, `8293.832`) birebir aynı. Diğer 165 satırda rakam dizisi aynı. |
| 5 | Elle düzeltilen makine çıktıları | ✅ | `taslak-170/rapor.html` 6, `lale158-regresyon.json` 1, `lale158/rapor.html` 1, `Robot-Tasarim-Demosu.html` 2, `kutle.json` 2, `taslak-analiz.json` 3, `hesap.json` 1 + `onceki-7mm/hesap.json` 1, `Y2b-aku.json` 1, `maliyet.json` 2 satır; hepsi madde 3 ve 4'ten geçti. Betik dizgeleriyle çıktı dizgeleri eşleşiyor (`taslak_ayar.py:59` ↔ `kutle.json:589,608` ↔ `hesap.json:4000`; `taslak_parcalar.py:184,334,343` ↔ `taslak-analiz.json:1819,1829,1844`; `ikinci_ozet.py:117` ↔ `lale158-regresyon.json:209` ↔ `lale158/rapor.html:22`; `Y2b-aku.py:65` ↔ `Y2b-aku.json:160`; `Y2b-maliyet.py:101` ↔ `maliyet.json:135`; `kol_rapor.py:60,125,318,396,492,493` ↔ `kol-analiz/rapor.html:30,39,72,80,95`). A'nın "yeniden üretildi, bayt bayt aynı" iddiaları koşulmadı (betikler dosya yazar). |
| 6 | JSON geçerli ve içerik aynı | ✅ | 7 JSON (`maliyet.json`, `Y2b-aku.json`, `lale158-regresyon.json`, `kutle.json`, `taslak-analiz.json`, 2 × `hesap.json`) `json.load` geçti. HEAD ile yapısal ağaç karşılaştırması: anahtar sırası, liste uzunluğu, tüm sayı / bool değerleri aynı; farklı 11 dizgenin hepsi "takma ad → Ahmet (+ ek uyumu)". |
| 7 | Satır sonları | ✅ | Değişen satırların sonu korunmuş; `Robot-Tasarim-Demosu.html` "mixed" ama CRLF satırları 763–765 (değişen 289, 967 değil; önceden var). `core.autocrlf=true`, commit LF'ye normalleştirir. |
| 8 | Anlam ve "Ahmet" / "Ahmet Yorulmaz" ayrımı | ✅ | 195 satırın tamamı okundu. Alıntılar aynen ("pi 4 gb", "tamam onaylıyorum go brr", "absürd gözükmez ..."). "Ahmet Yorulmaz" yalnız resmî tanıtım / belge başlığında: `Lale-Proje-Ozeti.txt:21` (proje lideri), `README.md:59` (bölüm başlığı), `kararlar-2026-10-29.md:1`. Kişiye atıflar "Ahmet". Not deposu adı ve ssh kullanıcısı nötr yer tutucuya dönmüş (`kararlar-2026-10-29.md:87` `ssh <kullanıcı>@lale.local`), yol önekleri `...` (`...\scratchpad\...` kalıyor, anlamlı). Öneri (bloklamaz): aynı dosyadaki öteki üç tur başlığı `kararlar-2026-10-29.md:28,74,97` "(Ahmet, ...)"; tutarlılık istenirse onlar da "Ahmet Yorulmaz" olabilir. |
| 9 | İzlenmeyen 2 dosya | ✅ (kısmi) | `F1a-kontrol.md`, `F5b-gunluk.md`: takma ad 0. `F1a-kontrol.md:35` ve `F5b-gunluk.md:63` "takma ad" diyor, anlam (arama terimi listesi) korunuyor. Önceki hâl git'te olmadığı için tek satır değiştiği doğrulanamaz. |
| 10 | Tarama kaynaklarına dokunuldu mu | ✅ | `KAYNAK_SABIT` (`carpisma_kos.py:29-31`) + `kaynak_listesi()` glob'u (`*_lib.py`, `*/*_lib.py`) import etmeden kopyalandı → 17 dosya. F4b listesi ∩ bu liste = **boş**. Çalışma ağacı diff'i ∩ liste = `arayuz.py`, `omuz/omuz_parcalar.py`: ikisi de F2'nin; ikisinde de takma adlı silinen / eklenen satır 0, takma ad sayısı HEAD ile aynı (17 ve 1). |
| 11 | `kod/`, `CLAUDE.md`, izlenmeyen `raporlar/` | ✅ | `git status kod/ CLAUDE.md`: temiz. `kod/` altında bugün değişen dosya 0; `CLAUDE.md` mtime 11.10. `raporlar/` altında bugün değişen 4 dosya, hepsi F4b'nin izlenen dosyaları; izlenmeyen `raporlar/11-6-inc-gogus-ekrani-sigma.md` takma adı hâlâ taşıyor (dokunulmamış). `kvkk/`, `rapor/`, `tubitak-2209b/`: bugün değişen 0. |
| 12 | Kalan 12 dosya | ✅ | Çalışma ağacında `git grep -il`: 12 dosya, günlük §4 ile birebir. Gerekçeler doğru: 8'i gerçek tarama kaynağı (`arayuz.py`, `kabuk_lib.py`, `kabuk_parcalar.py`, `kafa10_lib.py`, `kafa_lib.py`, `kafa_parcalar.py`, `omuz_parcalar.py`, `taban_parcalar.py`; 3'ü ayrıca F2 alanı), `yerlesim_lib.py` brief'in kapsam dışı listesinde, `kod/ortak/eklem_sinirlari.json:111` `arayuz.py:793`'ten `kod/ortak/eklem_sinirlari_uret.py` ile üretiliyor (doğrulandı: aynı metin, betik `import arayuz`), `CLAUDE.md` karar, `index.html` karar. |
| 13 | `yerlesim_lib.py` tarama listesinde mi | ✅ (A haklı) | İki klasör derinde (`lale158/kafa-yerlesim/`); glob yalnız kök ve tek alt klasöre bakıyor → `kaynak_listesi()`'nde **yok**. Başka izleyici de yok: `regresyon.py` yalnız okuduğu JSON'ların sha256'sını alıyor; `omuz_baski.py` yalnız `omuz_parcalar.py`'yi, `rehber_veri.py` / `bom_say.py` FCStd / BOM mtime'ını izliyor. `yerlesim_lib` yalnız `yerlesim_olc.py`, `yerlesim_koridor.py`, `yerlesim_gorsel.py` tarafından import ediliyor (seçenek betikleri; hiçbir tarama kaynağı onu import etmiyor). Satır 4 bir yorum. **Sonuç: şimdi temizlemek güvenli** (hiçbir taramayı / regresyonu eskitmez); brief kapsam dışı saydığı için A dokunmamakta haklı. Bkz. "Ayrı / isteğe bağlı" 1. |
| 14 | `index.html:49,92` gerekçesi | ✅ | İki `href` de `https://github.com/<hesap>/tekerlekli-insansi-robot/...`; hesap adı takma adı içeriyor. `origin` aynı hesap. `main`'deki aynı dosyada da 2 geçiş var (Pages). Yer tutucu bağlantıyı kırar: gerekçe doğru. |
| 15 | `regresyon.py` diff | ✅ | +14 / −0. `main()` başında, `CIKTI` okunmadan ve `olc()` çağrılmadan önce: `--help`/`-h` → `print(__doc__)`, `return 0`; `--yazma` dışındaki her argüman → stderr'e hata, `return 2`. `yazma_yok` satırından sonrası değişmemiş (normal mod ve `--yazma` mantığı aynı). Docstring'e kullanım satırları, stderr UTF-8. Not: `--help --xyz` → 0 (yardım öncelikli; argparse ile aynı davranış, sorun değil). |
| 16 | `regresyon.py` testi (yeniden koşuldu) | ✅ | sha256 önce: `regresyon.json` `e6f288ff5b7ba0a1…`, `regresyon-son-kosu.json` `ced8869015652586…` (A'nınkiyle aynı). `--help` 0, `-h` 0, `--xyz` 2 (stderr mesajı), `--yazma --xyz` 2, `x` 2, `--help --xyz` 0, `--yazma` 0 ("GEÇER", yazmadı). Her komuttan sonra iki sha aynı; depoda değişen dosya 0. Normal mod koşulmadı. |
| 17 | Başka soyad | ✅ | Eklenen 195 satırdaki büyük harfli sözcükler tarandı: kişi soyadı yalnız "Yorulmaz" (3). Öteki adlar satıcı / marka (Kartal Otomasyon, Atakale, Emas, Elo, Merter, Tenlacum, Robotistan …) ya da ekip içi ad ("Efe"). "Hoca" geçen satırlarda isim yok. |
| 18 | Karar taslağı K-F4b-1 (`CLAUDE.md`) | 🟡 | Biçim doğru (3 seçenek + etki + önerilen = b). İçerik doğru: takma ad `CLAUDE.md:3,4,22`'de (okundu); git geçmişi uyarısı doğru. Belirsizlik: "satır 3 ve 4'te 'Ahmet Yorulmaz' / 'Ahmet'" hangisinin nereye gideceğini söylemiyor → Koşul 2. |
| 19 | Karar taslağı K-F4b-2 (hesap adı) | 🟡 | Biçim doğru (4 seçenek + etki + önerilen = a). Seçenek d'nin etkisinde hata: "GitHub yönlendirme verir" yalnız depo (web + git) bağlantıları için doğru; GitHub, taşınan / adı değişen hesabın **Pages adresini yönlendirmez** (GitHub belgesi, "Transferring a repository": "we don't redirect GitHub Pages associated with the repository"). Paylaşılmış site linkleri kırılır → Koşul 1. Seçenek b'nin "Jekyll ile 404 olabilir, denenmeli" çekincesi yerinde. |
| 20 | Kapsam dışı ek bulgu | ℹ️ | İzlenmeyen `tasarim/solidworks/renkler.md:63` takma adı içeriyor; brief'in iki listesinde de yok. İzlenmediği için şu an herkese açık değil; bu klasör depoya eklenirse önce temizlenmeli. |

## Koşullar (birebir, C uygular)

1. `planlama/d158/F4b-gunluk.md:166` (K-F4b-2, seçenek d, etki sütunu)
   eski: `(GitHub yönlendirme verir)`
   yeni: `(GitHub depo web / git bağlantılarını yönlendirir; Pages adresi yönlendirilmez, paylaşılmış site linkleri kırılır)`
2. `planlama/d158/F4b-gunluk.md:148` (K-F4b-1, seçenek b)
   eski: `satır 3 ve 4'te "Ahmet Yorulmaz" / "Ahmet"`
   yeni: `satır 3'te "adı Ahmet'in kararı", satır 4'te "Proje sahibi Ahmet Yorulmaz;"`

**Commit önkoşulu (C):** F2 açık, `lale158-regresyon.json` / `lale158/rapor.html` gibi çıktıları yeniden üretebilir. `git add`'den
hemen önce F4b'nin 60 izlenen dosyasında `git diff --numstat`'ı günlük §2 tablosuyla karşılaştır (toplam +195 / −195, her dosyada
eklenen = silinen). Farklı çıkan dosya varsa o dosyayı ekleme, orkestratöre bildir.

## Ayrı / isteğe bağlı (bloklamaz, orkestratör kararı)

1. `tasarim/freecad/lale158/kafa-yerlesim/yerlesim_lib.py:4`: tarama dışı olduğu doğrulandı (madde 13); orkestratör isterse
   ayrı küçük işte (ya da P4.5b'nin başında) satır başındaki takma ad `Ahmet` yapılabilir; hiçbir tarama bölümünü eskitmez.
2. `kararlar-2026-10-29.md:28,74,97` tur başlıklarında "Ahmet" → "Ahmet Yorulmaz" (madde 8, yalnız tutarlılık).
3. Sayım notu: günlük §8.1 "tarama kaynakları ... 10 dosya" ve `dongu-158.md` günlüğündeki "9 tarama kaynağı": gerçek tarama
   kaynağı 8; `yerlesim_lib.py` tarama dışı, `eklem_sinirlari.json` üretilmiş çıktı. P6.1 iş listesi için doğru sayı: 8 + 1 + 1.

## F4b için `git add` listesi (açık)

```
Lale-Proje-Ozeti.txt
README.md
planlama/adim1/P-pi-kafada.md
planlama/adim2/M1-kablo-yolu.md
planlama/adim3/T-taban-guc-pi.md
planlama/adim3/elektrik.md
planlama/baski-listesi.md
planlama/dongu.md
planlama/duzeltme-plani.md
planlama/kararlar-2026-10-29.md
planlama/maliyet.json
planlama/siparis-farki-2026-10-29.md
planlama/y2/Y2a-brief.md
planlama/y2/Y2a-gunluk.md
planlama/y2/Y2a-kontrol.md
planlama/y2/Y2b-aku.json
planlama/y2/Y2b-aku.py
planlama/y2/Y2b-baski.py
planlama/y2/Y2b-gunluk.md
planlama/y2/Y2b-ivme.py
planlama/y2/Y2b-kontrol.md
planlama/y2/Y2b-maliyet.py
planlama/y3/Y3-brief.md
planlama/y3/Y3-gunluk.md
planlama/y3/Y3-kontrol.md
planlama/yazilim-notu-stowent-170.md
planlama/yazilim-plani.md
raporlar/aku-secimi/rapor.html
raporlar/kaynaklar/03-referans-finansman-destek.md
raporlar/kaynaklar/05-fiyat-arastirmasi.md
raporlar/kaynaklar/06-aku-secimi.md
tasarim/Robot-Tasarim-Demosu.html
tasarim/cad/robot_cad.py
tasarim/cad/viewer-template.html
tasarim/freecad/iskelet/iskelet_montaj.py
tasarim/freecad/lale158/ikinci/yavaslik/prof-head-kabuk.txt
tasarim/freecad/lale158/ikinci/yavaslik/prof-wt-kabuk.txt
tasarim/freecad/lale158/ikinci_ozet.py
tasarim/freecad/lale158/kablo_yolu_ekran.py
tasarim/freecad/lale158/lale158-regresyon.json
tasarim/freecad/lale158/qled-cerceve-tasarim-notu.md
tasarim/freecad/lale158/rapor.html
tasarim/freecad/montaj/montaj_gorsel.py
tasarim/freecad/taslak-170/CATAL-KONTROL-NOTLAR.md
tasarim/freecad/taslak-170/CATAL-NOTLAR.md
tasarim/freecad/taslak-170/KOL125-NOTLAR.md
tasarim/freecad/taslak-170/analiz/hesap.json
tasarim/freecad/taslak-170/analiz/onceki-7mm/hesap.json
tasarim/freecad/taslak-170/kol-analiz/NOTLAR.md
tasarim/freecad/taslak-170/kol-analiz/kol_analiz.py
tasarim/freecad/taslak-170/kol-analiz/kol_rapor.py
tasarim/freecad/taslak-170/kol-analiz/rapor.html
tasarim/freecad/taslak-170/kutle.json
tasarim/freecad/taslak-170/rapor.html
tasarim/freecad/taslak-170/taslak-analiz.json
tasarim/freecad/taslak-170/taslak_ayar.py
tasarim/freecad/taslak-170/taslak_hesap.py
tasarim/freecad/taslak-170/taslak_parcalar.py
tasarim/freecad/taslak-170/taslak_rapor.py
tasarim/freecad/taslak-170/taslak_rapor_analiz.py
planlama/d158/F1a-kontrol.md
planlama/d158/F5b-gunluk.md
planlama/d158/regresyon.py
planlama/d158/F4b-brief.md
planlama/d158/F4b-gunluk.md
planlama/d158/F4b-kontrol.md
```

(60 izlenen temizlik dosyası + 2 izlenmeyen temizlik dosyası + `regresyon.py` + F4b'nin 3 belgesi = 66.)
`planlama/dongu-158.md` orkestratörün dosyası (F4a ✅, F4b kilit satırı, günlük): F2 alanıyla çakışmıyor, F4b commit'ine eklenmesi
orkestratörün kararı; eklenecekse kendi satırı olarak.

## Commit'e girmemesi gerekenler

- **F2 (koşuyor):** `tasarim/freecad/arayuz.py`, `tasarim/freecad/omuz/omuz_parcalar.py`, `planlama/d158/F2-brief.md`,
  `planlama/d158/F2-gunluk.md`, ve F2'nin üreteceği tarama / rapor çıktıları (`carpisma-*`, `kabuk/`).
- **F4b öncesinden kalan (K23, 03.11; F2 günlüğü satır 13):** `tasarim/freecad/kabuk/gorsel/*.png` (13 dosya),
  `tasarim/freecad/montaj/yerlesim-kontrol.json`.
- Kalan 12 takma adlı dosyanın hiçbiri (zaten değişmedi; `arayuz.py` / `omuz_parcalar.py` yalnız F2 değişikliği taşıyor).
- `regresyon.json`, `regresyon-son-kosu.json` (değişmedi; sha aynı).
- İzlenmeyen ve kapsam dışı: `kvkk/`, `rapor/`, `tubitak-2209b/`, `raporlar/11-6-inc-gogus-ekrani-sigma.md`,
  `raporlar/kaynaklar/06-onayli-satici-A.md`, `06-onayli-satici-B.md`, `07-gogus-ekrani-ve-5v.md`, `tasarim/solidworks/`,
  `tasarim/freecad/lale158/kafa-yerlesim/kaynak/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`,
  `planlama/d158/F5-pano-govde.txt`, `F5b-pano-govde.txt`, `__pycache__/` (`.gitignore`'da).
