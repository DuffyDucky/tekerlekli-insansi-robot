# P10.8f bağımsız kontrol (B ajanı)

B ajanı, 21.11.2026 (açılış ≈ 17:28, rapor 17:45; saat okundu). Dal `lale-duzeltme`, HEAD = `origin/lale-duzeltme` = `641bc6c`; A'nın işi
çalışma ağacında, commit yok. A'nın günlüğü (`P108f-gunluk.md`) iddia sayıldı; aşağıdaki sayılar B'nin kendi koşularından ve kendi açıp
baktığı karelerden. FreeCAD açılmadı (`FREECAD-KILIT.txt`'e dokunulmadı); rehber yeniden üretilmedi; kaynak, çıktı, plan ve A'nın
günlüğü değişmedi: B'nin koşularından önce ve sonra 138 kirli / yeni dosyanın md5'i birebir aynı, `git status` (B'nin klasörü hariç) aynı,
başlangıçtan sonra depo içinde (`.git` hariç) B'nin klasörü dışında değişen dosya yok (`find -newer`). Commit benzetimi ve geçmiş
commit'lerdeki F9c ölçümü depo dışında, geçici `git clone --shared` kopyasında yapıldı (depodaki `.git`'e yazılmadı). B'nin logları ve
bozma betiği `planlama/d158/P108f-kontrol-olcum/`.

**Karar: GEÇER**

Gerekçe: (1) F9c'nin 60 hatası denetim gevşetilmeden, muafiyetsiz kapandı: `F9c-dogrula.py` HEAD ile aynı, `F9c-uret.py` farkında
mantık değişikliği yok (yalnız K67 grubu, metinler, kaynak listeleri); elle yazılmış her yeni iddia kaynağında bulundu (§ 1). B'nin
koşusu 0 / 0 (iki kip), B'nin yeniden ürettiği sayfa depodakiyle bayt bayt aynı. (2) Üç kare açığı karede kapandı; dokuz numara doğru
saplamada, B5a yazısı doğru kartta (§ 3; PDF sayfaları dahil). (3) Yan etki yok: değişen kareler beklenen 6 + iki gürültü karesi, uç
etiketi yeri yalnız 17.4'te değişti (§ 4). (4) CAD geometrisi ve çarpışma kayıtları HEAD ile aynı (§ 5). (5) Zincir son kaynak ve
çıktılarla koştu; B'nin yeniden koştuğu 17 denetim A'nın değerini verdi (§ 6). Bulgular bilgi düzeyinde (§ 10).

## 1. F9c (madde 1)

**Denetim değişmedi.** `git diff --quiet HEAD -- planlama/d158/F9c-dogrula.py` → aynı (son değişiklik `84f1a4a`, P10.9a).

**60'ın yeniden üretimi.** `641bc6c` ağacının tam kopyasında (PDF dahil, yapay hata yok) `F9c-dogrula.py --tarayicisiz`: **hata 60**;
hata listesi A'nın `P108f-olcum/once/F9c-tarayicisiz.log`'uyla satır satır aynı (`diff` boş). Dağılım: data-j 16 (kütle 5, rehber parça 4,
tarama koşusu 3, ivme kütlesi 2, demo bağlantı 2), K67 kaynaklı 13 (açık karar 7, toplam 3, F10 karar sayısı 1, F10 kimlikleri 1, "K67
tabloda 0 kez" 1), git kaynaklı 31 (P10.8 konu öneki / plan hash'i 28, P10.9 `e3aaf94` 1, commit sayısı 1, eşleşmeyen 1). A'nın
16 / 13 / 31 dökümü doğru. Aynı yöntemle `1db7a9c`: **25**, `e3aaf94`: **3** (A'nın tablosuyla aynı; `F9c-1db7a9c-tarayicisiz.log`,
`F9c-e3aaf94-tarayicisiz.log`). Görev özetindeki "59" B tarafından da üretilemedi.

**`F9c-uret.py` farkı satır satır (her yeni / değişen iddia kaynağına karşı):**

| Fark | Kaynak | Sonuç |
|---|---|---|
| `GRUP["K67"]` = A, metin "Sipariş listesindeki kart burcu adedi (48; CAD 52) … verildiyse eksik burçlar ayrı alınır" | `karar-kuyrugu.md:82` (Özet), `:1500–1517` (K67 gövdesi: liste 48, CAD 52, seçenek c, 16.11 siparişi) | örtüşüyor; grup § 2 |
| P10.2: "burç 2 … (P10.8 satırında; P10.8d'de kapandı)" | plan P10.8 hücresi "burç 2 … **kapandı: P10.8d `d2c6776`**" | örtüşüyor |
| P10.8 "Parça beklemeyen işler (19.–21.11)": P10.8a kupon dosyaları (hazır, basılmadı); P10.8b–e: yol 10 / 11 / 12, burç 2, iki kart modelde, 16 şema, dikiş ölçümü, 17.11 ve 32.1 kareleri; P10.8f bu sayfa ve 17.4 / 17.10 / B5a | plan P10.8 hücresi (`dongu-158.md:165`) kapandı işaretleri; P10.8f bu paket | örtüşüyor (P10.8f kısmı bu paketin kendi iddiası, kayıtta henüz açık: § 10 N1) |
| P10.8 "Devralınan (19.11) … iki yeni kartın gerçek ölçüsü ve burç / vida boyu" | kuyruk `:2007` "Kartlar gelince"; plan hücresi "(açık)" | içerik doğru; madde 21.11'de (P10.8d) doğdu, "Devralınan (19.11)" başlığı altında (§ 10 N2) |
| P10.8 "sonraki tam taramalı CAD paketinde": K52 zarfı, K31, yol 6 → kart C, kafa giriş kartı (TAHMİN), `TABAN_DISI_BOLGE`, tam tarama yeniden | plan hücresinde "(açık)" yazılı 7 maddeden 6'sı; 7.'si (iki kart ölçüsü) üst listede | örtüşüyor ("açık 7" sayımı tutuyor) |
| P10.8 eski "rehber: 17.4, 32.1, 17.10, 17.11 U06, `--kaynak` CAD adı, D6, kafa-yerlesim" çıktı | plan: 32.1, U06, `--kaynak`, D6 rehber tarafı, kafa-yerlesim **kapandı**; 17.4 / 17.10 / B5a bu paket | örtüşüyor (bu paket commit'lenince) |
| Rehber satırı: "P10.8b–e: K55 bant metni, ESP32 yön denetimi, `--kaynak` CAD adları, D6, iki kart modelli uç, 17.11 U06 taban bölümü, 32.1 taban bakışı. P10.8f: …" | plan P10.8b ve P10.8e kapanış metinleri | örtüşüyor |
| Rehber açık: ölçülmeyen yollar (göğüs bandı sol yanal, F2 ve etek arka dikişleri), `--kaynak` malzeme adları, `elektrik.md` boyları, kart zarfı TAHMİN | kuyruk `:1975–1984`, `:2007` | örtüşüyor |
| CAD satırı: "P10.8d (21.11): yol 10, 11, 12 düzeltildi, burç 2 yarıktan çıktı, iki kart modelde, 16 şema tarandı" | plan P10.8d metni | örtüşüyor |
| CAD açık: K52, K31, yol 6 (S09 / S10 "elle bakıldı"), iki kart ölçüsü (TAHMİN), kafa giriş kartı, `TABAN_DISI_BOLGE`, tam tarama; "kafa-yerlesim yeniden üretilmeli" çıktı | plan "(açık)" maddeleri; kuyruk `:2004–2006`; kafa-yerlesim plan "**kapandı: P10.8c `1fbe337`**" | örtüşüyor |
| Sipariş satırı "K67 kart burcu adedi (CAD 52, liste 48)" | K67 | örtüşüyor |
| F10 sırası: madde 1 "(yapıldı: P10.8a, basılmadı)"; madde 6'da P10.8d'de yapılanlar ayrıldı | plan P10.8a ve P10.8d | örtüşüyor |
| Depo satırı: "P10.8a–e commit'leri ve kayıt eşitlemesi push edildi; P10.8d'den sonra kancaya STEP koordinatı istisnası eklendi (21.11)"; açıkta yalnız gömülü görsel istisnası | `origin/lale-duzeltme` = `641bc6c` (yerel izleme dalı; uzak ayrıca sorgulanmadı); `269e51b` commit mesajı; `dongu-158.md:186`; kuyruk `:2019–2020` "STEP … yapıldı … `data:image` … açık" | örtüşüyor |
| Ortak ön soruya K67 | K67 gövdesi "16.11 siparişinin verilip verilmediği kayıtta yok (K27–K37'nin ortak ön sorusu)" | örtüşüyor |
| Tutarsızlık notu: F10 kararları K62 (C) ve K67 (A, taslak) | kuyruk Özet (açık F10 kararı iki) | örtüşüyor |
| Tutarsızlık notu: demo P10.9c'de üretilmedi, P10.8e'de P10.8d montajıyla üretildi (F9b 0) | plan P10.8e "demo sayfası P10.8d sayılarıyla (F9b 0)" | örtüşüyor |
| Yeni tutarsızlık notu: 60 hata, P10.8e commit'inde 25, kategoriler, commit'ten sonra 3 | B'nin ölçümü: 60, 25; benzetim 3 (§ 8) | örtüşüyor |
| Başlık "19.11.2026; yenileme P10.8f, 21.11.2026" | bu paket | örtüşüyor |

Sayfaya uydurulmuş değer bulunmadı. Sayılar (`data-j`, `data-h`) üreticide hesaplanıyor, elle yazılmadı.

**B'nin koşuları (çalışma ağacı):** `F9c-dogrula.py --tarayicisiz` → **GEÇER (hata 0)** (`k7-F9c-tarayicisiz.log`); `F9c-dogrula.py`
(tarayıcılı, görüntü yazmadan) → **GEÇER (hata 0)**; 1400 px ve 360 px'te konsol hatası 0, taşan öğe 0, yatay kaydırma yok
(`F9c-tarayicili.log`). `--goruntu` kipi koşulmadı (izlenen 10 PNG'yi yeniden yazardı; tarayıcı denetimi görüntüsüz kipte aynı).
`F9c-uret.py --cikti <depo dışı>` → çıkış 0, "toplam 67, açık 27", 154.009 bayt, **depodaki `sonuc-rapor.html` ile bayt bayt aynı**
(`F9c-uret-B.log`); yani sayfa elle yamanmadı ve kilit satırı (17:26) sayfayı etkilemiyor.

## 2. K67 aciliyet grubu (madde 2): A tutarlı

Tanım (`F9c-uret.py` `GRUP_AD`): A "Sipariş ya da elektrik güvenliği öncesi", B "Montaj öncesi", C "Sonra karar verilebilir".
Emsal ölçüt P10.9a kontrolü B4'te konmuş (`P109a-kontrol.md:74–83`): seçeneği sipariş satırını değiştiren karar A (K12 "fan seçilirse
sipariş satırı eklenir", K32, K61 B → A). Adet soruları da A: K43 (insert adedi), K31, K33. K67'nin a / b seçenekleri sipariş listesindeki
adedi değiştiriyor (+4 / +8 burç), kuyruk "Bloke ettiği" hücresi "Taban güç paneli kartları (B5a), sipariş listesi". Bu ölçütle **A
doğru**. Karşı gerekçe (yazılsın): 16.11 siparişi verildiyse soru pratikte B'ye (B5a montajından önce ayrı alım) iner ve seçenek c
zaten bunu öneriyor; ama aynı ön soruya bağlı K27–K37 / K42 / K43 / K50 / K61 de A'da duruyor, K67'yi ayrı tutmak tutarsız olur. Öneri:
A kalsın; orkestratör onaylasın.

## 3. Üç kare (madde 3; B dosyaları açıp baktı)

Önce: `P108f-olcum/once/kare/` (`rehber-adim-*` = yazdırma 1.200 × 720, `basili-adim-*` = etkileşimli 1.400 × 900; boyutlar B'nin
ölçümü, A'nın "ad ile anlam ters" notu doğru; 6 / 6 HEAD'deki dosyayla md5 aynı). Sonra: depodaki üretilmiş kareler (A'nın
`sonra/kare/` kopyalarıyla md5 aynı). PDF: `planlama/rehber/Lale-montaj-rehberi.pdf` 90 sayfa, B sayfa 13 (B5a) ve 24 (17.4) açtı
(110 ve 300 dpi).

| Kare | Kapandı mı | B'nin gördüğü |
|---|---|---|
| 17.10 (iki kip) | **Evet** | Saydam katın dış kenarı ve ortadaki yarık ince siyah çizgiyle çiziliyor. Koyu mor hatlar (katın üstünde) yarığın çerçevesinin içine giriyor; yarığın altından sonarlara (5, 7, 8) ve BTS'lere inen bölümler soluk mor (katın altında, saydam katın ardında). Geçiş artık kareden okunuyor: yalnız bir çizgi eklenmedi, renk koyu → soluk tam yarığın kenarında değişiyor. Uç etiketleri (8) yerinde; piksel farkı yalnız kat kenarı çizgisinin kutusunda (yazdırma 10.761 px, kutu 123…895 × 52…579). |
| 17.4 (iki kip + PDF s. 24) | **Evet** | Arka sırada dört saplamada A1–A4, ön sırada beşinde Y1–Y5, soldan sağa. Veri: anahtarlı x −37,5 / −12,5 / 12,5 / 37,5 (z −115, arka), yıldız x −50…50 (z −55, ön); kamera önden-üstten, +x ekranın sağı, K65 "+X önden bakanın sağı" ile numaralama kuralı (B5a metni) aynı. Yazılar birbiriyle ve uç etiketleriyle çakışmıyor; lejantta anlamı ("A1–A4: anahtarlı baranın, Y1–Y5: yıldız barasının … soldan sağa"), PDF'te kare altında "Karedeki yazılar: …" satırı var. Ayrıntı § 10 N6. |
| B5a (iki kip + PDF s. 13) | **Evet** | "Acil stop düğüm kartı" yazısı arkadaki küçük yeşil kartın (p1071, x −118, z −90, 30 × 30) üstünde, ince çizgiyle karta bağlı; öndeki büyük yeşil kart ön şarj kartı (p1058, x −130…−65, z −23,5…21,5), yazı ona değil. Metindeki "röle K1 ile ön şarj kartının arasında" ile aynı yer. Uç etiketleri (XL4016 C, Dağıtım kartı C) yerinde; piksel farkı yalnız yazının kutusunda (yazdırma 3.766 px, kutu 183…339 × 165…198; etkileşimli 2.736 px). |

PDF'te iki karedeki yazılar okunuyor ama küçük (§ 10 N3).

## 4. Yan etki (madde 4)

- **Değişen kare listesi** (`git status`): `rehber/goruntu/adim-12, -17-04, -17-10` ve `planlama/rehber/goruntu/` aynı üçü + `adim-33-04`,
  `adim-33-07`. Üretimin yeniden yazdığı 289 kare PNG'sinin öbür 281'i bayt bayt aynı (`find -newer` listesinde var, `git status`'ta yok). Beklenen
  dışında içerik değişen kare yok.
- **33-04 / 33-07:** HEAD'e göre farklı piksel 60 / 68, kanal farkı toplamı > 24 olan **0**, fark kutusu (893…936 × 743…810) "Robotun
  neresi" mini görünümünde. Gürültü; A'nın ölçümüyle aynı.
- **17.4 kamera:** üretim logunda tek fark `alt adim 17.4 kadraj D 336 → 349` (P10.8e `uretim2.log` ile P10.8f `uretim2.log` karşılaştırması;
  öbür bütün adım / alt adım satırları aynı; PDF 19.485 → 19.496 kB, sayfa 90 aynı).
- **Uç etiketleri:** B'nin `F10d-dogrula.py --yalniz-uc` koşusu: 23 konum, 59 etiket, hata 0, GECTI (223 s). HEAD'deki
  `F10d-dogrula.json`'la konum konum karşılaştırma: farklı olan **yalnız 17.4** (yazdırma en çok 1,6 px, etkileşimli en çok 21,1 px; A
  "≤ 2 / ≤ 21 px" dedi); B5a dahil öbür 22 konum × 2 kip aynı.
- **Kod okuması (`app.js`):** `ia` yedeği ("üst nokta güvenli alanın dışındaysa kutu merkezi") yalnız `ETK.liste` (parça etiketi)
  döngüsünde; uç etiketi (`UC.liste`) yerleşiminde yedek yok. `ETK.liste` yalnız `etiket` alanı olan konumlarda dolu (veri: 2 konum,
  17.4 ve B5a); boşken `eNokta` / `eKutu` boş, uç etiketi kodu eski davranışta. Lejant notu ve `yazdir.html` satırı yalnız
  `etiket_not` + `etiket` varsa (yalnız 17.4). `stil.css` `.ep` / `.et` yalnız `g.etk` içinde. Başka adıma etki yolu yok.

## 5. Geometri (madde 5)

`git status -- tasarim/`: rehber dışı değişenler yalnız 21 eski kirin 14'ü (13 kabuk PNG + `yerlesim-kontrol.json`, md5 başlangıçla
aynı). `git diff --quiet HEAD -- tasarim/freecad/carpisma-sonuc.json tasarim/freecad/carpisma-bolum/` → **aynı**. FCStd / STEP / STL /
GLB farkı yok. `tasarim/` altında başlangıçtan (14:26) sonra değişen dosya yalnız `rehber_metin.py` ve `rehber_gorunum.py` (izlenmeyen
ya da yok sayılan dosyalar dahil, `find -newer`). `carpisma_kos.py kontrol` (B iki kez): "izlenen 17 dosyanın özetleri kayıtla aynı".

## 6. Zincir (madde 6)

**Tazelik.** Dosya saatleri: kaynaklar en geç 15:35:32 (`P108f-etiket-olc.py`; `app.js` / `rehber_gorunum.py` 15:32); üretim 2
15:39:17–16:21:57 (çıktılar 15:40:00–16:21:57); F9c sayfası 16:22:46, `F9c-goruntu-*` 16:22:55; **zincir 16:22:59 başladı**,
17:25:58 bitti (15 / 15 çıkış 0, `zincir.durum`). Zincirden sonra değişen izlenen dosya yalnız `dongu-158.md` (17:26:36, kilit satırı)
ve A'nın günlüğü. Zincirde `dongu-158.md`'yi okuyan tek adım `regresyon.py` (korunan değerler §1); B yeniden koştu, GEÇER. Bu yüzden
57 dakikalık tam zincir yeniden koşulmadı. Zincir logları okundu: 15 logda Traceback 0; F10d "23 konum, 59 etiket, hata 0", F10e
"GECTI; renk_demo KALDI (karar)", 6g "103 / 116" (P10.8e ile aynı), regresyon "kötüleşen yok". Zincirin yazdığı F10 JSON farkları tarih,
süre ve 17.4 / 17.10 ölçümleri.

**B'nin yeniden koştukları** (hepsi çıkış 0, A'nın değeri):

| # | Komut | B'nin sonucu |
|---|---|---|
| k1 / 2c | `rehber_denetim.py --kaynak` | ascii 0, onay farkı 0 (219 / 258 / 1201), CAD ad/kod 973 |
| 3 | `rehber_denetim.py` | ascii 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0 |
| k2 / 2a | `rehber_kablo.py`, `--veri rehber/veri/rehber-veri.json` | GEÇER / GEÇER |
| k3 | `F10l-birlesim.py` | GECER |
| k4 | `P108f-etiket-bozma.py` | sağlam 10 yazı; 8 / 8 YAKALANDI |
| k5 | `P108f-etiket-olc.py` | 2 konum, 10 yazı, hata 0, GECTI; DevTools kareleri A'nınkiyle md5 aynı (belirlenimci) |
| — | `F10d-dogrula.py --yalniz-uc` | 23 konum, 59 etiket, hata 0 (§ 4) |
| — | `F10d-dogrula.py --bozma-denemesi` | şema 5 / 5, uç etiketi 9 / 9 |
| k6 | `node --check rehber/app.js` | tamam |
| k7 | `F9c-dogrula.py --tarayicisiz` / tarayıcılı | 0 / 0 (§ 1) |
| k8 | `md5sum -c P108f-olcum/kir-bas.md5` | 21 / 21 OK |
| 0a, 9 | `carpisma_kos.py kontrol` | kayıtla aynı |
| t1 / t2 | `kupon_tazelik.py` / `--bozma-denemesi` | TAZE (16) / 4 / 4 |
| 8 | `F9b-dogrula.py` | GECER (hata 0) |
| 10 | `regresyon.py --yazma` | GEÇER, kötüleşen yok |

Koşulmayanlar: 2b (`rehber_kablo --bozma-denemesi`, 75 s; kablo kodu değişmedi), F10f / F10e / F10d tam / F10a (uzun; girdileri
zincirden sonra değişmedi), rehber üretimi.

**A'nın yeni ölçüm betikleri hatayı yakalıyor mu.**
- `P108f-etiket-bozma.py` (Python tarafı, `etiket_isle`): 8 bozmanın her biri ayrı bir durdurma kuralına dokunuyor (desen boş, yazı
  çakışması iki yoldan, x sırası takası, alt adım yok, alt adım numarası yok, parça o adımda takılı değil, adım yok). Anlamlı.
- `P108f-etiket-olc.py` (tarayıcı tarafı): kendi bozma sınaması yoktu; B yazdı (`P108f-kontrol-olcum/B-etiket-olc-bozma.py`, B'nin
  ölçüm JSON'unun bellek kopyasını bozar): **7 / 7 kapsamdaki bozma YAKALANDI** (A4 düşmesi, üretim 1'deki gerçek hata; kutu güvenli
  alan dışında; iki yazı üst üste; yazı uç etiketinin üstünde; DOM 0; yanlış yazı; konum ölçülmemiş). Kapsam dışı iki bozma beklendiği
  gibi KAÇTI: yazının yanlış saplamaya bağlanması ve kutunun parçadan uzak düşmesi; araç yazının parçasına yakınlığına bakmıyor (§ 10 N5).

## 7. Eski kirli dosyalar ve muafiyet (madde 7)

- Başlangıç kaydı `P108f-olcum/git-status-bas.txt`: 14 M + 7 ?? = 21 (artı A'nın `P108f-olcum/`). Şimdiki `git status`'ta aynı 21 yol;
  `md5sum -c` 21 / 21 OK.
- Farkta yeni muafiyet / istisna / atlama yok: `git diff` eklenen satırlarında `muaf`, `istisna`, `atla`, `skip`, `ignore`, `UC_ORTULU`,
  `GEO_YAN_ELLE`, `_DISARIDA`, eşik / tolerans araması yalnız sayfa metnini (kancanın STEP istisnası, "toleransı" sözcüğü) ve
  `PARCA_ETIKET` yorumundaki "UC_ORTULU gibi" benzetmesini buldu. `rehber_metin.py` farkı yalnız `kenar=("Elektronik katı",)` ve yeni
  `PARCA_ETIKET`; `UC_ORTULU` / `GEO_YAN_ELLE` değişmedi. `F9c-dogrula.py` değişmedi. `P108f-zincir.sh`, `P108e-zincir.sh`'den yalnız
  log yolu ve başlık yorumunda ayrılıyor (`diff`).

## 8. Commit sonrası F9c (madde 8): tahmin doğru, ölçüldü

Mekanizma (`F9c-dogrula.py`): `komit_sayisi` F0 tabanından HEAD'e `git log` sayısı, sayfaya üretimde yazılır; `komit_eslesmeyen`
sayfanın hiçbir commit hücresinde geçmeyen döngü commit'leri; "konu öneki" kuralı, konusu `Lale P10.8…` olan her commit'in P10.8
satırının commit hücresinde geçmesini ister. Sayfa kendi commit'inin hash'ini içeremez → yeni commit üçünü de bozar.

Benzetim (depo dışı klon, `641bc6c` + A'nın `git add` listesindeki 116 dosya, A'nın önerdiği mesajla tek commit):
`F9c-dogrula --tarayicisiz` → **hata 3**: `komit_sayisi: sayfa '116', hesap 117`; `komit_eslesmeyen: sayfa '2', hesap 3`;
`paket P10.8: konu öneki bu pakette olan <hash> commit hücresinde yok` (`F9c-benzetim-commit-sonrasi.log`). Emsal `e3aaf94` aynı 3
(B ölçtü). Sınır: iki ayrı commit atılırsa 6 olur; sonraki kayıt eşitlemesi P10.8f hash'ini plan P10.8 hücresine yazarsa o commit
ayrıca "plan hash'i sayfada yok" hatası ekler (641bc6c'deki 21'in mekanizması).

## 9. Kapanış tarifi (madde 9)

- **`git add` listesi eksiksiz ve doğru.** Listedeki yolların kapsadığı değişiklik 116 dosya; `git status`'ta listede olmayan yalnız
  21 eski kir ve B'nin dosyaları. Benzetimde listenin `git add`'i sonrası klonda kalan değişiklik 0.
- **Girmemesi gereken dosya yok:** 21 eski kir listede değil; `FREECAD-KILIT.txt` `.git/info/exclude:19`'da ve listede değil;
  geçici çıktı yok (önizleme betiği sistem geçici klasörüne yazıyor). `P108f-olcum/` metin dosyalarında kullanıcı yolu, e-posta,
  anahtar / jeton, IBAN kalıbı aranıp bulunmadı (`grep`); PNG'ler tarayıcı çekimi. Satır sonu: LF depoya LF girer (`core.autocrlf=true`,
  `app.js` çalışma ağacında CRLF, depoda LF).
- **Listede olmayan, eklenmesi gereken:** B'nin `planlama/d158/P108f-kontrol.md` ve `planlama/d158/P108f-kontrol-olcum/` (emsal:
  `P108d-kontrol-olcum/` izleniyor). B'nin klasöründe kullanıcı yolu yok (bir log satırı B tarafından maskelendi).
- **Kanıt klasörü boyutu:** diskte 10,5 MB (77 dosya), ama depoya giren yeni içerik benzetimde **5,85 MB** (ham blob): `once/kare/` 6 PNG
  HEAD'deki dosyalarla aynı, `sonra/kare/` 6 PNG ve `devtools/` 17.4 kareleri üretilen karelerle aynı, `devtools/12-*` =
  `onizleme/cekim-kaynak/12-*`; git aynı içeriği bir kez tutar. Asıl yük `onizleme/` aday kareleri (≈ 4,9 MB tekil). Emsal: `P108e-olcum/`
  tamamı (76 dosya, 2,8 MB, `onizleme/` dahil) izleniyor. Tamamının girmesi emsale uygun, şart değil; aday karelerden yalnız seçilen
  (`k1_10_kenar`) ve reddedilenlerden birer tane tutmak ≈ 3 MB kazandırır (orkestratörün kararı). Bütün commit'in yeni nesnesi diskte
  ≈ 26,5 MB, çoğu her rehber üretiminde yenilenen PDF (K47 b: kontrol görüntüleri paket kayıt commit'inde girer).
- Commit mesajında kişisel bilgi yok.

## 10. Bulgular (hepsi bilgi; geçmez nedeni değil)

- **N1 (kayıt):** Sayfa 17.4 / 17.10 / B5a'yı P10.8f'te yapılmış yazıyor; plan P10.8 hücresi ve kuyruğun "Rehber" maddesi bunları hâlâ
  açık yazıyor (A'nın alanı dışında). Commit'ten sonraki kayıt eşitlemesinde kapatılmalı; o eşitleme F9c'ye yeni hata ekler (§ 8).
- **N2 (metin):** P10.8 satırında "iki yeni kartın gerçek ölçüsü ve burç / vida boyu" "Devralınan (19.11)" listesinde; madde P10.8d'de
  (21.11) doğdu. Sonraki yenilemede başlık "Devralınan (19.11) ve P10.8d'den" gibi düzeltilebilir.
- **N3 (PDF ölçeği):** Yazdırma karesi PDF'te 73–76 mm genişlikte basılıyor; 14 px yazı ≈ 0,86 mm, yani ≈ 2,4 pt (uç numaralarıyla aynı
  ölçek). 300 dpi'de okunuyor, kâğıtta çok küçük. Uç numaraları da öyle olduğu için yeni bir kusur değil; kâğıtta okunurluk isteniyorsa
  rehber aracı işi.
- **N4 (ölçüm kapsamı):** `P108f-etiket-olc.py` ve F10d uç etiketi ölçümü DevTools çekimini (`cekim=1`) ölçüyor. 17.4'te (alt adım) bu
  çekim teslim edilen karelerle piksel piksel aynı (fark 0). B5a gibi alt adımsız adımlarda teslim edilen kare üretimin `--screenshot`
  çekimi ve kadrajı farklı (fark 212.870 / 335.870 px). B5a'nın teslim edilen iki karesi yalnız gözle doğrulandı (B baktı, § 3).
  F10d için de geçerli, P10.8f'ten önceki durum.
- **N5 (araç):** `P108f-etiket-olc.py` yazının kendi parçasının yanında olup olmadığına bakmıyor (§ 6 bozma: kapsam dışı iki bozma
  kaçtı). Bağlantı noktası veriden geldiği ve numaralama Python'da denetlendiği için bu paket için yeterli.
- **N6 (17.4 etkileşimli):** A4 yazısı (yedek `ia` noktası) saplamanın gövdesinin önünde, saplamanın ucu yazının üstünde görünüyor;
  hangi saplama olduğu belli. Y4 / Y5 saplamaları yarı saydam direğin arkasında, Y5 soluk. "4 Yıldız barası" uç etiketi Y3 saplamasının
  somununa değiyor. Okunurluğu bozmuyor.
- **N7 (A'nın sayıları):** A'nın günlüğündeki ölçülebilir sayıların hepsi B'nin ölçümüyle aynı çıktı (60 / 25 / 3, dökümü, 0 / 0, 21 / 21,
  8 / 8, 10 yazı, 23 / 59, 17.4 kayması, 33-04 / 33-07 gürültüsü, D 336 → 349). Uyuşmayan sayı yok.

## 11. Commit'ten önce

**Şart (A'nın işinde düzeltme yok):** `git add` listesine B'nin `planlama/d158/P108f-kontrol.md` ve `planlama/d158/P108f-kontrol-olcum/`
eklensin. Commit'ten hemen önce `F9c-dogrula.py --tarayicisiz` yine 0 olmalı (B'nin son koşusu 17:41, 0).

**Şart değil, not:** K67 grubu A (orkestratör onayı, § 2); `onizleme/` aday karelerinin kırpılması (≈ 3 MB, § 9); N1 kayıt eşitlemesi;
N2 metin; commit'ten sonra F9c 3 hata (yapısal, § 8).

## 12. Bakılmayanlar / doğrulanamayanlar

- `F9c-dogrula.py --goruntu` koşulmadı (izlenen PNG'leri yeniden yazardı); A'nın 10 PNG'si açılıp bakılmadı. Tarayıcı denetimi görüntüsüz
  kipte koşuldu (0).
- Zincirin uzun adımları (F10f, F10e, F10d tam, F10a) ve 2b, rehber üretimi B tarafından koşulmadı (§ 6 gerekçesi).
- Koyu temada kareler açılmadı (kareler ve ölçüm açık temada; parça etiketi CSS'te iki temada sabit beyaz kutu).
- `origin`'in uzak hâli sorgulanmadı (`git fetch` yok); push durumu yerel izleme dalından.
- 17.10'daki geçişin B-rep doğruluğu (yol 11 / 12 kesikten) yeniden ölçülmedi; dayanak P10.8d ölçümü, B yalnız karenin bunu gösterdiğine baktı.
