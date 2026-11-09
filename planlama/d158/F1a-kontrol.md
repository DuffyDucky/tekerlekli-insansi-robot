# F1a kontrol (P1.2, P1.3, P1.6, P1.7): ajan B, 08.11.2026

**Genel karar: KOŞULLU.** Geometri, çakışma ve regresyon tarafında sorun yok (10/10 aynı, ev pozu 0, ana model K2'den etkilenmemiş).
Koşullar küçük: P1.2'nin kabul cümlesi harfiyen sağlanmadı (MAX98357A başka paketlerin dosyalarında kalıyor, sahipleri yazılmalı), raporda bir
ölçü yanlış (70 yerine 72) ve commit listesinden çıkarılması gereken dosyalar var. A'nın yeniden çalışması gerekmiyor.

Yöntem: A'nın günlüğü kanıt sayılmadı. Diff'ler okundu, JSON'lar HEAD ile karşılaştırıldı. `kafa_rapor.py`, `lale158_rapor.py` ve
`ikinci_ozet.py` B tarafından çıktı yolu scratchpad'e yönlendirilerek koşuldu (depoya yazılmadı). `regresyon.py --yazma` ve
`carpisma_kos.py kontrol` koşuldu. FreeCAD açılmadı.

## Madde tablosu

| Madde | Karar | Kanıt |
|---|---|---|
| **P1.2** model/betiklerde MAX98357A | KOŞULLU | Diff: yalnız yorum/metin/rapor kodu (`arayuz.py:274-275, 654, 984`; `kafa10_lib.py:14-15, 304, 395, 407`; `kafa_lib.py:178-179`; `kafa7_parcalar.py:25-26, 490-491`; `qled_gorsel.py:124`; `taban_lib.py:4`; `taban_parcalar.py:5, 476`; `taban_rapor.py:158, 179, 194`). Geometri değişmedi. `kafa`, `taban` ve `iskelet/rapor.html` içinde `MAX98357` 0. **Ama** `git grep -i max98357` tarihçe dışında da sonuç veriyor: `Lale-Proje-Ozeti.txt:68`, `planlama/maliyet.json:75`, `planlama/yazilim-plani.md:23,114`, `planlama/adim3/elektrik.md:12,21,266`, `rehber/veri/rehber-veri.json` (4 yer), `tasarim/freecad/rehber/rehber_metin.py:276`, `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/freecad/kabuk/rapor.html:60`. A bunları başka paketlere bıraktı ve günlüğe yazdı; bu, brief'teki "kapsam dışına çıkma" kuralına uygun. Yine de kabul cümlesi harfiyen sağlanmıyor (bkz. Koşul 1). `KY/yerlesim_*.py`, `uygulama_*.py`, `secenekler.md`, `uygulama-notu.md` 05.11 seçim çalışmasının tarihçesi; `uygulama_olc.py:105` amfinin modelde 0 parça olduğunu sayan bekçi satırı, kabul edilir. |
| P1.2 ses yükselticisi tek | GEÇER | `kafa-bom.csv`, `robot-bom.csv` ve `montaj-analiz.json` içinde MAX 0. `kafa7_parcalar` "I2S amfi (125 cm)" parçası 1,58 m kafasına girmiyor (`kafa_parcalar.py:8, 25`: yalnız Govde/Pan grubu alınıyor). |
| P1.2 kafa içi çakışma | GEÇER | `kafa-analiz.json` `statik` 0 (regresyon). |
| P1.2 `elektrik.md` PAM besleme notu | GEÇER, koşula bağlı | Brief bu işi istemedi; plan satırı (`dongu-158.md:74`) istiyor. Besleme noktası K10 kararına bağlı ve karar açık (`karar-kuyrugu.md:25, 165`; bağlı paketler P1.2, P4.1, P8.3). `elektrik.md:21` hâlâ "doğrulanmadı" diyor. A günlükte "P4.1/K10" yazdı ama P4.1'in satırında (`dongu-158.md:99`) bu iş geçmiyor. Bkz. Koşul 1. |
| **P1.3** a/b çakışma 0 | GEÇER | `hat-secenek-a.json` ve `-b.json`: `cakisma_hatli` [], `cakisma_hatsiz` [], `eski_zarf_cakisma` [], `gecersiz` [], `log_uyari` []. Seçenek 0 F0'daki 77,69 / 7,97 / 3,18 sayısını yeniden üretiyor, yani yöntem doğrulanmış. |
| P1.3 ana model değişmedi | GEÇER | `kafa10_lib.SECENEK` varsayılanı eski sabitlerle birebir: `(-DIL_W/2, 60.0)`, `pi_dz=0` (`kafa10_lib.py:62, 179, 304, 462`). `kafa-analiz.json`, `kafa-montaj.FCStd` (05.11 17:01) ve `kafa-bom.csv` değişmedi. Robot BOM'u, `montaj-analiz.json`, `kabuk-analiz.json` ve `lale158-kontrol.json` içinde "AI HAT" 0. |
| P1.3 tilt payları 3,30 / 3,37 | GEÇER | `hat_secenek.py:143-219` `tork()`, `kafa_montaj.py` §6'nın kopyası. Seçenek 0'ın HAT'sız sonucu `kafa-analiz.json` ile birebir aynı (1.570,8 g; 2,583 kg·cm; 3,64; pan 2,21), yani hesap doğrulanmış. HAT'lı: a 3,30 (2,846 kg·cm), b 3,37 (2,785 kg·cm); kafa grubu 1.598,9 g. İkisi de ≥ 3,0. |
| P1.3 K2 maddesi | GEÇER | `karar-kuyrugu.md:63-97`: iki seçenek, varsayılan (a), 17 satırlık sayı tablosu, kaynak anahtarları ve varsayımlar yazılmış. JSON'la karşılaştırıldı: en yakın parça (a 3,0 / 6,3; b 2,05 / 3,55), fan zarfı (98,2 / 19,61), erişim, kütle ve paylar aynı. |
| **P1.6** `kafa_rapor.py` | GEÇER | B koştu, çıkış 0. Çıktı depodaki `kafa/rapor.html` ile **bayt bayt aynı** (1.515.396 B). İçinde 1.570,8 ×4, 3,64 ×3, 2,21 ×3 geçiyor; `MAX98357`, takma ad, vizör ve D36V50F5 0. "125 cm" 5 kez geçiyor, hepsi tarihçe/karşılaştırma bağlamında. |
| P1.6 `lale158_rapor.py` | GEÇER | B koştu, çıkış 0. Çıktı depodaki `lale158/rapor.html` ile bayt bayt aynı. "Kasa ↔ çerçeve" ölçütü 0,2 (`:67`). |
| P1.6 `ikinci_ozet.py:142` | GEÇER | Dosyada "kasa↔çerçeve" yok, A'nın tespiti doğru. Betik çıkış 0 veriyor, ama yalnız `PYTHONIOENCODING=utf-8` ile: varsayılan cp1254 konsolda `print` satırı `↔` karakterinde `UnicodeEncodeError` ile düşüyor. Bu sorun daha önce de vardı. Çıktısı, yeni tarama kimlikleri yüzünden depodaki 04.11 tarihli `lale158-regresyon.json`'dan farklı; A bu dosyaya dokunmadı. |
| P1.6 `kafa_gorsel.py` | GEÇER (dolaylı) | B koşmadı, çünkü betik depodaki görsellerin üstüne yazıyor. AST temiz; `next(` yok, yani StopIteration kaynağı gitmiş. `doc.save` kaldırılmış (`:8, 223`) ve `kafa-montaj.FCStd` değişmemiş. 17 görselin tarihi 08.11. `kafa-izometrik.png` açılıp bakıldı: 158 kafası. 125 cm'den kalan 3 eski poz görseli klasörde duruyor, rapor onları göstermiyor. |
| **P1.7** çakışma | GEÇER | `kabuk-analiz.json`: `cakisma` [], `iskelet_cakisma` [], `gecersiz` [], `coklu_kati` []; parça 357. Kafa içi 0, ev pozu 0. `uygulama-olcum.json`: hoparlör ↔ köpük ped 0,0 (tasarım gereği temas), kelepçe ↔ ön halka 4,243. |
| P1.7 baskı | GEÇER | `kabuk-analiz.json` baski "Hoparlor kelepcesi": 56,6 × 56,6 × 14,3, `destek_sorun_sayi` 0, `desteksiz` true. Arka kap (13,3) ve ön halka da 0. Destek sorunu olan parçalar HEAD ile aynı (göğüs bandı sağ/sol 1, servis kapağı 1, VESA 28). |
| P1.7 kütle | GEÇER | Kütle 4,0 g (baskı analizi), 4,3 g (BOM), 5,0 g (`lale158-kontrol` baski). Fark yöntemden geliyor; ön halka ve kap için de aynı fark var. Elle hesap: hacim ≈ 3.760 mm³ (70 × 10 × 3 köprü + 2 × 9 × 10 × 11,3 bacak, delikler düşülmüş); %80–90 dolulukla PETG'de ≈ 4,0–4,3 g. Makul. Kabuk 7.165,4 → 7.170,4 g; montaj 25.515,59 g. |
| P1.7 mikrofon–hoparlör | GEÇER | `uygulama-olcum.json` `mic_hoparlor.poz_min_mm` 574,3 (HEAD de 574,3). Hoparlörün yeri değişmedi. |
| P1.7 kablo ucu | GEÇER | `kablo_yolu_ekran.py:100-104` değişti. `lale158-kontrol.json` `kablo_tup_cakisma.Hoparlor` = [Boyun mili 1,2], HEAD ile aynı. Kafa torkuna etkisi yok: `kafa_ici_kablo_kutle()` (`:152-171`) yalnız kafa tabanının üstündeki parçaları sayıyor; değişen uç gövdede (y ≈ 1003). |
| **Çakışma taraması** | GEÇER | `carpisma_kos.py kontrol`: "kaynagi eskimis bolumler: omuz" (rc 1; başka uyarı yok). `carpisma-sonuc.json`: `ev_pozu_cakisma` [], kesişen çift 819, toplam 364, eklem aralığında 0 (HEAD ile aynı). 9 bölüm "tamam": 8'i 08.11 koşusu (221801, 230636, 231459), omuz 20261103. `kutle_toplam_g` 25.515,6. |
| **Regresyon** | GEÇER | `py -3 planlama\d158\regresyon.py --yazma` (23:23:36): "GEÇER", 10/10 aynı (boy 1.580; dört çakışma 0; rampa 1,517; tilt 3,64; pan 2,21; mik–hop 574,3; SY8205 0). Taban dosyalarının md5'i koşudan önce ve sonra aynı. `regresyon.json` diff'inde yalnız tarih ve sha değişmiş, değerler aynı. |
| **Yan etkiler** | KOŞULLU | `Y2b-ivme.json` (03.11 22:09), `montaj/yerlesim-kontrol.json` (03.11 21:23) ve 13 kabuk görseli (03.11 21:35) **A'nın değil**. Bunlar K23'teki ara çıktılar (`karar-kuyrugu.md:38, 272-280`; dosya tarihleri F1a'dan önce). Yeniden üretilen `iskelet/` ve `taban/rapor.html` eski veriden bugünkü JSON'a güncellendi (ör. iskelet KPI 1590 → 364, eskime uyarısı yalnız "omuz"). Bu kapsam içinde, sorun yok. `dongu-158.md` diff'i orkestratörün (kilit tablosu, günlük). |
| Takma ad / soyad | GEÇER | `git diff` içinde eklenen satırlarda takma ad 0. A, 3 satırdaki takma adı kaldırdı: ikisinde "Ahmet" yazdı (`arayuz.py:984`, `kafa10_lib.py:407`), birinde nötr metin koydu (`kafa7_parcalar.py:491`). A'nın yeni dosyalarında (`hat_*.py`, `hoparlor_gorsel.py`, `f1a_rapor.py`, `F1a-rapor.html`, `F1a-gunluk.md`) takma ad 0. Başka öğrenci ya da hoca soyadı yok. Daha önceden kalanlar (P4.5'in işi, HEAD'de zaten var): `arayuz.py` 17, `kafa10_lib.py` 4, `kabuk_parcalar.py` 3, `kablo_yolu_ekran.py` 2, `taban_parcalar.py` 2, `kafa_lib.py` 1, `lale158/rapor.html` 1 (`lale158-regresyon.json:209`'dan geliyor). |

## Koşullar

1. **P1.2'nin kalan satırlarını sahip paketlere yaz** (orkestratör, `dongu-158.md`). Şu an P4.2 ve P4.4 dışında hiçbir paket satırı bu
   dosyaları adıyla anmıyor; P1.2'nin `elektrik.md` kısmı da K10'a bağlı ve sahipsiz.
   - `dongu-158.md:99` (P4.1 iş hücresi), eski: `USB cihaz listesi (6. cihaz Efe cevabına göre)` → yeni: `USB cihaz listesi (6. cihaz Efe cevabına göre); ses: PAM8403 + USB ses kartı, MAX98357A satırları :12, 21, 266 ve PAM besleme noktası (K10)`
   - §5 günlüğe bir satır: `F1a B: P1.2 kalanları → P4.2 maliyet.json:75 · P4.4 Lale-Proje-Ozeti.txt:68 · P5.2 yazilim-plani.md:23,114 · P7.1 rehber_metin.py:276 + rehber/veri · P9.2 Robot-Tasarim-Demosu.html · kabuk/rapor.html (kabuk_rapor.py KeyError, aşağıda)`
2. **Kelepçe köprüsünün boyu 70 mm, 72 değil.** Kodda köprü `kopru_e1=35`, yani ±35 (`kabuk_parcalar.py:774, 782`); baskı kutusu 56,6 = (70 + 10)/√2.
   - `tasarim/freecad/lale158/kafa-yerlesim/f1a_rapor.py:216`, eski: `(72 × 10 köprü + 2 bacak)` → yeni: `(70 × 10 köprü + 2 bacak)`. Ardından `py -3 f1a_rapor.py` ile `F1a-rapor.html`'i yeniden üret.
   - Aynı hata `kabuk_parcalar.py:733` yorumunda da var (`72 x 10 kopru`). **Şimdi düzeltme:** `kabuk_parcalar.py` tarama kaynak listesinde (`carpisma_kos.py:30`); tek bir yorum değişikliği bile 8 bölümün hepsini "eskimiş" yapar. P6.1 tam taramasından önce düzelt.
3. **Commit'e girmeyecek dosyalar** (kayıt ajanı C açık `git add` listesi kullanmalı):
   - `kvkk/`, `rapor/`, `tubitak-2209b/`, `tasarim/freecad/lale158/kafa-yerlesim/kaynak/` (satıcı dosyaları).
   - K23 açık, F1a'nın değil: `planlama/y2/Y2b-ivme.json`, `tasarim/freecad/montaj/yerlesim-kontrol.json`, `tasarim/freecad/kabuk/gorsel/*.png` (13 dosya).
   - Başka paketlerin dosyaları: `planlama/d158/F5-pano-govde.txt`, `F5b-gunluk.md` (içinde takma ad var, bkz. §5), `F5b-pano-govde.txt`, `raporlar/11-6-inc-gogus-ekrani-sigma.md`, `raporlar/kaynaklar/06-onayli-satici-A.md`, `-B.md`, `07-gogus-ekrani-ve-5v.md`, `tasarim/solidworks/`, `tasarim/freecad/montaj/lale_dongu.FCMacro`, `lale_dongu_ac.bat`.
   - `planlama/dongu-158.md`: orkestratörün dosyası; F1a commit'ine girip girmeyeceğine orkestratör karar verir.

## Daha büyük düzeltmeler (F1a dışı, ayrı pakete)

- `kabuk/kabuk_rapor.py:130, 331, 376` `d["ekran_kontrol"]` anahtarını okuyor. Bu anahtar `kabuk-analiz.json`'da 15.10'dan beri yok (Nextion döneminden kalma).
  Bu yüzden `kabuk/rapor.html` yenilenemiyor; içinde 1 MAX98357 satırı ve eski kabuk duruyor. P1.5 ile aynı modül, oraya eklenebilir.
- `ikinci_ozet.py:153-157`'deki `print` satırları cp1254 konsolda düşüyor. Düzeltme: betiğin başına `sys.stdout.reconfigure(encoding="utf-8")` ya da koşuda `PYTHONIOENCODING=utf-8`. Tarihçe betiği, acil değil.
- `montaj-analiz.json` `karsilastirma.kutle.fark_carpisma` 4,989 g ve `am.fark_carpisma_mm` 0,088. Sebep: `ana_montaj` taramadan önce koştu; `carpisma-sonuc.json` artık 25.515,6 g. Sonraki `ana_montaj` koşusu bu farkı kendiliğinden kapatır.
- K2 uygulanınca (P6.1) tilt payı 3,64'ten 3,30'a (a) ya da 3,37'ye (b) iner. Korunan değer tablosundaki "tilt 3,64" o zaman güncellenmeli; eşik 3,0 hâlâ sağlanıyor.
- K2 için Ahmet'e iki not. (a) seçeneğinde boss, havalandırma yarığına 1 mm uzakta ve dikiş cıvatası x −5'te, yani dikişe 2,15 mm. Kenar mesafesi ve duvar dayanımı ölçülmedi. (b) seçeneğinde kablo boyları yeniden hesaplanmadı. İkisi de K2 notlarında açıkça yazılı ya da varsayım olarak işaretli.
- İsteğe bağlı: `KY/uygulama_olc.py:105`'teki bekçi satırı yalnız "MAX98357" arıyor. 125 cm arşivindeki parçanın adı artık "I2S amfi (125 cm)"; bekçi `("MAX98357", "I2S amfi")` arasın. Satır ölçüm betiğinde, acil değil.
