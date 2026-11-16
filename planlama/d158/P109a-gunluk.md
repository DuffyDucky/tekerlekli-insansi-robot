# P10.9a günlüğü: faz sonu araçları iki basamaklı fazı (F10) tanısın (ön paket)

Ajan A, 16.11.2026 02:39–02:47 (sistem saati). Dal `lale-duzeltme`; commit, `git add`, stash yok (P10.7b2d ajanı aynı anda çalışıyor).
FreeCAD ve tarayıcı yok. Depodaki `sonuc-rapor.html` yeniden yazılmadı (ilk hâliyle bayt bayt aynı); deneme üretimi depo dışında.

## 1. Değişen dosyalar

- `planlama/d158/F9c-uret.py`
  - Kalıplar iki basamaklı: faz başlığı `F\d+`, plan satırı `P\d+\.\d+[a-z]?` (P10.4b, P10.5b paket), brief adı `F\d+[a-z]?`,
    commit etiketi `(F10a)`, konu satırındaki P kodu `P\d+\.\d+`, §5 tek başlıklı ✅ satırı, karar fazı `F(\d+)[a-z]?`.
  - Yeni `paket_kodu()`: harfli kod planda paket ise kalır (P10.4b), değilse harfsiz (P4.5a → P4.5 eskisi gibi, P10.7b2d → P10.7).
  - Karar fazı kuralına üçüncü adım: Durum ve Bloke'de faz yoksa Durum hücresindeki ilk P kodu (K62 "P10.7b1" → F10). F0–F9'da etkisi 0.
  - `GRUP`'a K53, K54, K55, K60, K61, K62 için TASLAK aciliyet önerisi (§ 3). Kapanan kararın grubu artık hata değil, bilgi
    (K1, K10, K11, K14 14.11'de kapandı; eskiden `main` 1 dönerdi).
  - `PAKET_SONUC`'a 11 F10 satırı, `FAZ_SONUC`'a F10 (§ 4); `raporlar()` P10.9'a da "bu rapor" bağlantısı.
  - `--cikti YOL`: sayfayı `sonuc-rapor.html` yerine YOL'a yazar.
- `planlama/d158/F9c-dogrula.py`
  - Aynı kalıplar (plan satırı, paket satırı, `data-satir` faz kodu, `KT-F\d+[a-z]?-\d+`, karar fazı); `range(10)` yerine plandaki faz
    başlıkları (`fazlar()`).
  - Kuyruk özeti `**Açık: 49.**` biçimini de okur (nokta bold içinde; eski kalıp `None` dönüyordu).
  - `hash_eksik` ve `komit_eslesmeyen` için kendi hesabı (F9 sonunda not sayfada yoktu, bu yüzden tanımsızdı).
  - `--sayfa YOL`: başka yoldaki sayfayı denetler (göreli bağlantılar yine `planlama/d158/`'ye göre).
- `planlama/d158/F9d-tarama.py`: değişmedi (faz kalıbı yok; yalnız modül olarak içe aktarılıyor).

## 2. Kanıt (çıktılar depo dışında, scratchpad `p109a/`)

- Önce: özgün `F9c-uret.py` kopyası, depo yolundaymış gibi; tek yama, `GRUP`'ta olmayan açık karar ("K53"…) için ("C", "?")
  (özgün kod bugünkü kuyrukta `KeyError: 'K53'` ile düşüyor; sayfa 14.11'den beri yeniden üretilemiyordu). → `once.html`.
- Sonra: `F9c-uret.py --cikti …/sonra.html`, çıkış 0: paket 47 (✅ 41, 🟡 1, ⛔ 2, 🔄 1, ⏳ 2), commit 95, bulunamayan hash 0,
  eşleşmeyen commit 2; karar 63, açık 49; faz F0 7, F10 6.
- F0–F9 karşılaştırması (`karsilastir.py`):
  - 36 F0–F9 paket satırından 35'i bayt bayt aynı (durum, sonuç, commit listesi, rapor); P9.3'te yalnız "Bu rapor: 36 → 47 paket".
  - Özet tablosunda F1–F9 satırları aynı; F0'ın açık kararı 13 → 7 (K53, K54, K55, K60, K61, K62 eski kodda F0'a düşüyordu, şimdi F10).
  - Açık K1–K52 karar satırları (43) aynı. Kalan farklar yalnız toplamlar (paket 36 → 47, grup A/B/C 19/11/19 → 21/14/14,
    eşleşmeyen commit 25 → 2).
- Denetim `F9c-dogrula.py --tarayicisiz --sayfa …/sonra.html`: hata 1, o da kaynakta (§ 5.1). Eski sayfa (`once.html`) 21 hata.
- Bozma: P10.4b satırı silinince "paket P10.4b tabloda 0 kez"; `faz_karar_F10` 6 → 5 yakalandı; P10.2 metninde 0,425 → 0,426
  "kaynakta yok" diye yakalandı.
- Koşmadı: `[9]` tarayıcı ölçümleri (1400 / 360 px yatay kaydırma, konsol hatası, taşan öğe) ve `--goruntu`. Bellek dar, Chrome açılmadı.

## 3. Karar aciliyet grupları: TASLAK (karar değil)

F9c'nin A / B / C kalıbıyla, gerekçe kuyruğun "Beklettiği" hücresinden. K53 A (elektronik katının lazer kesim dosyası; lazer teklifi
sipariş öncesi), K54 B (kafa iskeleti baskısı), K55 B (kabuk baskısı), K60 A (elde acil stop, elektrik güvenliği), K61 B (düğme
kablajı, Efe), K62 C (kayıt). P10.9'da orkestratör onaylasın ya da değiştirsin.

## 4. F10 paket özetlerinin kaynağı

- F0–F9 kalıbı: bir cümle, her sayı `dongu-158.md` (gerekirse günlük / rapor) içinde birebir geçer; `data-kaynak` denetimi bunu sınar.
- F10 için kaynak: `dongu-158.md` §3 F10 tablosunun Durum hücreleri (16.11 02:39 hâli). Ayrıntı için §5 günlüğü ve `F10*-gunluk.md`
  var, ama sayfaya plan hücresinde geçen sayılar alındı.
- Açık paketler "Açık" diye başlar: P10.2 (⛔ K53), P10.7 (🔄; kapalı alt paketler a, b1, b2a, b2b, b2c; b2d sürüyor), P10.8 (⏳),
  P10.9 (⏳). Faz satırı plandaki emojilerden 🔄 hesaplanır, kapanmış gibi görünmez.
- P10.9'da güncellenecek: P10.7 metni (b2d / b2e kapanınca), P10.9 metni, F10 faz cümlesi.

## 5. Sayaçlar: kaynak ve bugünkü değer

1. Açık / toplam karar: kuyruktan türüyor (`data-h karar_acik`, `karar_toplam`; üretici ve denetim Özet tablosunu ayrı ayrı sayar).
   Bugün 49 / 63, kapanan 14 (`karar-kuyrugu.md:80` ile aynı). Sayfadaki 47 / 52 sayfanın 09.11'den beri yeniden üretilmemesinden:
   P10.7a commit'i (`8134519`) sayfayı elle yamadı (maliyet, K52 metni), sayıya dokunmadı; K53'ten beri üretici `KeyError` ile düşüyordu.
   Elle yazılmış eski sayılar: `F9c-uret.py` `PAKET_SONUC["P0.2"]` "52 madde, 47 açık" (F9 sonu anlık görüntüsü, tarihî),
   `TUTARSIZ` 4. madde "açık 47 / 52", `dongu-158.md:167` P10.9 satırı "47 ↔ 48, 52 ↔ 53". Değiştirilmedi.
   - Kaynakta tutarsızlık (denetimin kalan tek hatası): `karar-kuyrugu.md` K58 Özet tablosunda "kapandı", ama başlığı
     `## K58 · ESP32 pin haritası (pano #8)` "— KAPANDI" taşımıyor. Kuyruk bu paketin alanı dışında.
2. F8a sipariş sayacı: elle / ajan yazımı, türemiyor. `F8a-siparis.json` `toplamlar.sayac` (136 satır, 86 + 7 = 93 doğrulandı),
   09.11'den beri aynı; aynı dosyada `guncelleme_14_11` "bu paket P10.7a'dan önceki listedir" diyor. Kalemlerden basit kuralla
   satır sayısı tutuyor (bölüm S + K + A = 136), doğrulanan tutmuyor (87 ↔ 86), ikinci satıcı tutmuyor (78 ↔ 73). Sayfa P8.1
   satırında ve "Sipariş paketi toplamı" / "Bütçe farkı" satırlarında bu eski listeyi gösteriyor; güncel sipariş `maliyet.json`
   (120.852,43 TL). Değiştirilmedi; P10.9'da "09.11 listesi" diye mi işaretlenecek, kaldırılacak mı orkestratörün kararı.

## 6. P10.9'a kalanlar

- Sayfa başlığı / altbilgi "(P9.3) · 09.11.2026", faz notu "F9'un 🔄'ı bu paketin kendisidir", Paket kartındaki "(bu paket)" elle;
  F10'a göre yazılmalı.
- Eşleşmeyen 2 commit (`9145164`, `f658f15`, 13.11 gizlilik denetimi): pakete bağlanacak mı, "paket dışı" diye mi gösterilecek.
- Commit eşlemesi F0–F9'daki sezgiyle: ör. `759bb28` (P10.4b) konu satırında "P10.7" geçtiği için P10.7'ye de bağlandı; B gözden geçirsin.
- K58 başlığı (§ 5.1), F8a sayacı kararı (§ 5.2), taslak aciliyet grupları (§ 3), tarayıcı ölçümleri.
- Son üretim (`F9c-uret.py`, `--cikti`'siz) ve `F9c-dogrula.py` (tarayıcılı) P10.7 kapandıktan sonra.

## 7. Plan için önerilen satır (orkestratör işletir; bu ajan `dongu-158.md`'ye yazmadı)

Günlük: `- 2026-11-16 02:47 **P10.9a (ön paket) A ✅ kaynak düzeyinde.** F9c-uret / F9c-dogrula iki basamaklı faz (F10, P10.4b), F10
paket özetleri taslak, --cikti / --sayfa; depo dışı üretim: F0–F9 paket satırları aynı (P9.3'te yalnız paket sayısı), denetim hata 1
(K58 başlığı, kuyruk); sayfa yeniden yazılmadı, commit yok; günlük planlama/d158/P109a-gunluk.md.`
P10.9 satırının Durum'una: `⏳ (ön paket P10.9a ✅ 16.11: araçlar F10'u tanıyor; sayılar ve üretim faz sonunda)`; iş hücresindeki
"47 ↔ 48, 52 ↔ 53" bugün 49 / 63.

## Düzeltme turu 1 (P109a-kontrol.md B1–B10)

Düzeltme ajanı, 16.11.2026 03:00–03:10 (sistem saati). Dal `lale-duzeltme`, HEAD `1c4e882`; commit, `git add`, stash yok. FreeCAD ve
tarayıcı yok. Yazılan dosyalar: `F9c-uret.py`, `F9c-dogrula.py`, bu bölüm. `sonuc-rapor.html`, `dongu-158.md`, `karar-kuyrugu.md`
değişmedi (md5 başta = sonda). Bütün koşular depo dışında, `1c4e882`'nin paylaşımlı klonuna çalışma ağacındaki metin dosyaları
(plan dahil, md5 `ae629afe…`) kopyalanarak (scratchpad `p109a-duzeltme/ayna/`); plan koşular boyunca değişmedi, canlı depodan
yapılan son üretim aynalı üretimle bayt bayt aynı.

### Uygulananlar
- **B1** `F9c-uret.py`: P kodu yalnız konu önekinden (`s.split(": ", 1)[0]`); §5 satırında "push A..B" sol ucu atlanır (`PUSH_SOL`,
  denetimde aynı kalıp). Düşen bağlar: P10.1 −`9d0c58a`, P10.3 −`ada0b87`, P10.4 −`10b60d6`, P10.7 −`759bb28`.
- **B2** `F9c-dogrula.py` [5]: her faz özet tablosunda bir kez, Durum = paketlerin en kötüsü; plan dışı faz satırı hata.
- **B3** denetim (F10 ve sonrası): "Açık" öneki ↔ plan durumu; "Kapalı alt paketler" / "Sürüyor" listeleri plandaki kalın alt paket
  başlıklarıyla (`**P10.7a ✅`, `**P10.7b2a (…) ✅ …, kapandı**`), planda geçen her alt paket listede; "Açık (Kxx)" ve "Kalan:"
  K kodları kuyrukta açık, "Kxx kapandı" kapalı; F10 faz cümlesinde "Kapalı:" / "Açık:" paketleri ve "P10.7'nin … alt paketleri",
  "(b2d sürüyor)" planla. İçerik: P10.7 "Kalan" planın "Sıradaki: P10.7b2" listesinden, b2a–b2c'nin kapattıkları (K63, 3B yollar)
  çıkarıldı: taban yollarının yeniden tasarımı, boyların ölçümü, düğüm tutucusu, boyun tüneli deneme parçası, G19 / G20 / G24 / G26
  (yalnız onayla; b2b "onaysız yakalanıyor" diyor, onay yok); K52, K60, K61 (kuyrukta açık); Efe'nin iki cevabı.
- **B4** K61 B → A (orkestratör kararı; kontrolün gerekçe metni, 76,24 kuyrukta geçiyor). Grup A/B/C 21/14/14 → 22/13/14.
- **B5** kart `… · N 🔄 · N ⏳` (`paket_⏳`); "(bu paket)" kalktı.
- **B6** kural notu kontrolün metniyle (⏳ sırası, Durum'daki P kodu adımı, "F10 açık").
- **B7** P9.3: "F9 sonu sayfası (09.11): 36 paket, 47 / 52 açık karar, 10 korunan değer; F10 yenilemesi P10.9." Kontrolün metni
  `data-kaynak` = yalnız plan ile koşturulunca "09.11 kaynakta yok" verdi (plan tarihi 2026-11-09 yazar); kaynağa `F9c-brief.md`
  eklendi (sayfa başlığının tarihi de oradan).
- **B8** §5 başlığı planda paket olmayan harfli kodsa harfsiz pakete iner (`**P10.7a ✅`, plan :165 → P10.7: `4a097fb`, `b6022c3`,
  `1c4e882`; :351'de hash yok). Bugün çıktı farkı 0 (üçü konu satırından zaten P10.7'de); ölçüldü.
- **Ek denetimler:** plan Durum hücresindeki her hash o paketin commit hücresinde (kontrolün önerisi; P6.1–P10.7, 15 paket);
  konu öneki yalnız P kodlarından oluşan döngü commit'i ("Lale P1.1:", "Lale P7.4/P9.4:", "Lale P2.1–P2.2:") o paketlerin
  hücresinde (Durum'unda hash olmayan F0–F5 paketleri için); faz satırındaki karar kimlikleri kuyruktan hesaplanan kümeyle aynı;
  her `*-rapor.html` (F9c-rapor hariç) en az bir paket satırında. F0–F9'da yanlış alarm 0.
- **B9** dokunulmadı (kuyruk alanı dışında); denetimin tek hatası o.
- **B10** (§ 2'deki ifadenin düzeltmesi; o satıra yazılmadı): "sayfa 14.11'den beri yeniden üretilemiyordu" yerine: özgün üretici
  K53'ün açıldığı 11.11'den (F10b) beri `KeyError` ile düşüyordu (14.11'de K1 / K10 / K11 / K14 kapanınca ayrıca "fazla grup" ile
  `return 1`); sayfa son kez 14.11'de `8134519` ile elle yamandı.

### Kanıt
- Önce (ilk ajanın çalışma ağacı betikleri) ↔ sonra, aynı donmuş planla: üretici çıkış 0 / 0; satır farkı 12 satır, 14 hücre / öğe,
  hepsi bilinçli: B1 4 commit hücresi (P10.1, P10.3, P10.4, P10.7); B3 P10.7 Sonuç; B4 6 (karar kartı; "Kararlar" maddesi 21 → 22,
  K61 eklendi; A ve B başlık sayıları; K61 satırı B'den silindi, A'ya eklendi); B5 kart; B6 not; B7 P9.3 Sonuç. 35 F0–F9 paket satırı, F0–F10
  faz satırları, öbür karar satırları, sayılar bölümü bayt bayt aynı. Açıklanamayan fark 0.
- Denetim (`--tarayicisiz`): yeni sayfa hata 1 (K58 başlığı); yeni denetim eski sayfada da yalnız K58; depodaki 09.11 sayfası 70 hata
  (bayat, beklenen).
- Bozma (depo dışı kopyada 25): yakalanan 22. Kontrolün kaçan türlerinden faz satırı silme (F10, F3), faz Durum (F10, F4), durum
  sözcüğü, faz notundan karar kimliği, commit taşıma (P10.1→P10.3, P7.1→P7.2, P1.1→P1.2), tek paketli rapor bağlantısı artık
  yakalanıyor; yeni: b2d sürüyor→kapalı, Kalan'a kapalı K56, F10 cümlesinde P10.2 / b2d kapalı, "K61 kapandı", "Açık:" önekini
  silme; plan tarafı (sayfa bayat): b2d kapandı, yeni alt paket b2e, P10.2 ✅, P10.7 ✅.
- Kaçan 3: yaygın sayı (P10.5 alt adım 71 → 72; `data-kaynak` alt dize sınırı, F9c-gunluk §12); Kalan'dan bir açık kararı silme
  (K61; liste eksiksizliği kuyruktan türetilemez, hangi açık kararın P10.7'ye ait olduğu bir yargı); birden çok paketin bağlandığı
  raporu yalnız bir satırdan silme (P1.2 F1a; ayırt etmek için brief eşlemesinin yeniden yazılması gerekir). Commit taşıma, konu
  öneki "Lale:" ya da faz etiketi olan commit'lerde hâlâ kaçar.
- Koşmadı: [9] tarayıcı ölçümleri ve `--goruntu`.

## Commit turu (78d160d sonrası yeniden koşu)

Ajan C, 16.11.2026 05:09 (sistem saati, +03:00). Dal `lale-duzeltme`, HEAD = `origin/lale-duzeltme` = `78d160d` (P10.7b2d;
plan P10.7 hücresi ve günlük satırı değişti). FreeCAD ve tarayıcı yok. Koşular canlı depodan, çıktı depo dışında (scratchpad
`p109a-commit/`); `sonuc-rapor.html`, `karar-kuyrugu.md` md5 başta = sonda.

- İlk koşu (düzeltme turu 1'in betikleriyle): üretici çıkış 0 (paket 47, commit 96, bulunamayan hash 0, eşleşmeyen 2: `9145164`,
  `f658f15`; karar 63, açık 49; `78d160d` P10.7 commit hücresinde). Denetim `--tarayicisiz` **hata 3**: K58 başlığı (bilinen) +
  "paket P10.7: P10.7b2d 'sürüyor' yazıyor, planda kapandı" + "faz F10: P10.7b2d 'sürüyor' yazıyor, planda kapandı". B3 denetimi
  tasarlandığı gibi yakaladı; neden `F9c-uret.py`'deki elle yazılmış iki metin.
- Düzeltme (`F9c-uret.py`, yalnız metin): `PAKET_SONUC["P10.7"]` "Sürüyor: P10.7b2d (…)" → kapalı alt paketlere
  "P10.7b2d (K1 / K2 demet alt adımları, PDF 84 sayfa)" (84 planın 05:10 günlük satırında); `FAZ_SONUC["F10"]` "P10.7'nin a, b1, b2a,
  b2b, b2c, b2d alt paketleri", "Açık: … P10.7, …" ("(b2d sürüyor)" kalktı).
- İkinci koşu: üretici çıkış 0 (aynı sayılar); denetim **hata 1**, yalnız K58 başlığı (kuyruk; sonraki paket). İlk ↔ ikinci sayfa
  farkı yalnız bu iki metin.
- Koşmadı: [9] tarayıcı ölçümleri ve `--goruntu`; depodaki `sonuc-rapor.html` yeniden üretilmedi.
