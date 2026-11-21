# P10.8f günlüğü: ufak dört iş (F9c, 17.10, 17.4, B5a düğüm kartı) (A ajanı)

Paket: P10.8f, A (uygulama). Başlangıç 21.11 14:26. Dal `lale-duzeltme`, yerel = uzak = `641bc6c`. Kilit tablosu satırı
`planlama/dongu-158.md` § Kilit tablosu (P10.8f). Commit / push başka ajanın işi; bu günlük adım adım yazıldı.
CAD geometrisi değişmedi (FreeCAD açılmadı, `FREECAD-KILIT.txt`'e dokunulmadı); dört işin hiçbiri geometri istemedi.

Kaynaklar: `planlama/dongu-158.md` (P10.8 hücresi), `planlama/d158/P108e-gunluk.md` (§ 11 doğrulanmayanlar), `planlama/d158/P108e-kontrol.md`
(B2 düğüm kartı etiketsiz, B3 17.10 kareden doğrulanamıyor), `planlama/d158/karar-kuyrugu.md` (K67; "Karar değil, iş" P10.8d / P10.8e bölümü),
`planlama/d158/P108d-gunluk.md` (kesik ve yol 11 / 12 B-rep ölçüsü).

## 1. Başlangıç durumu

| Ne | Değer |
| --- | --- |
| HEAD | `641bc6c` (yerel = uzak) |
| Eski kirli dosyalar | 21 (`P108f-olcum/git-status-bas.txt`; md5 `P108f-olcum/kir-bas.md5`) |
| `F9c-dogrula.py --tarayicisiz` | GEÇMEZ, **hata 60** (`P108f-olcum/once/F9c-tarayicisiz.log`). Görev özetindeki "59" yeniden üretilemedi; 1 farkın nedeni ölçülmedi |
| `F9c-uret.py` | yeniden üretilemiyor: `KeyError: 'K67'` (§ 2) |
| Önce kareleri | `P108f-olcum/once/kare/`: `rehber-adim-*.png` = yazdırma karesi (`rehber/goruntu/`, 1.200 × 720), `basili-adim-*.png` = etkileşimli kare (`planlama/rehber/goruntu/`, 1.400 × 900); ad ile anlam ters düştü, içerik bu |

## 2. İş 1: F9c 60 hata, gerçek neden

**Yöntem.** `F9c-dogrula.py` her commit'in ağacında (ikili dosyalar hariç `git archive`) ve o commit'e kadarki `git log` ile koşuldu
(geçici sarmalayıcı, depoya yazmaz). Arşivde PDF olmadığından her koşuda 1 yapay hata ("kırık bağlantı ../rehber/Lale-montaj-rehberi.pdf")
çıkar; aşağıdaki sayılar ondan arındırılmış.

| Commit | Ne | F9c hata |
| --- | --- | --- |
| `e3aaf94` (19.11 15:27) | P10.9c: sayfa son üretildi | 3 (sayfa kendi commit'ini taşıyamaz: commit sayısı, eşleşmeyen commit, konu öneki) |
| `1d7fb71` | P10.8a | 4 |
| `d8ade70` | P10.8b | 7 |
| `1fbe337` | P10.8c | 8 |
| `d2c6776` | P10.8d | 19 |
| `269e51b` | P10.8d kanca kaydı | 20 |
| `1db7a9c` | P10.8e | **25** |
| `641bc6c` | kayıt eşitlemesi (plan + kuyruk) | **60** (çalışma ağacında da 60) |

**60'ın dökümü** (`once/F9c-tarayicisiz.log`):
- 16 data-j: sayfadaki 19.11 değeri ↔ bugünkü JSON (montaj parça 1.225 → 1.251, kütle 25.835,06 → 25.876,13 g, ivme kütlesi, rehber
  parça 1.238 → 1.264, PDF 87 → 90 sayfa, demo bağlantı 937 → 953, tarama koşusu `20261119-075818` → `20261121-023529`).
- 13 K67 kaynaklı: karar sayıları (açık 26 → 27 × 7, toplam 66 → 67 × 3), F10 karar sayısı 1 → 2, F10 açık karar kimlikleri, "K67 tabloda 0 kez".
- 31 git kaynaklı: commit sayısı 108 → 116, eşleşmeyen 2 → 10, plan P10.8 hücresindeki hash'ler sayfanın commit hücresinde yok (21),
  konu öneki P10.8 olan commit hücrede yok (7), P10.9 `e3aaf94` (1).

**Önceki 25 ile yeni 35'in ayrımı.** `1db7a9c`'deki 25 = 16 data-j + 2 commit sayısı + 6 P10.8 konu öneki + 1 P10.9 `e3aaf94`.
`641bc6c` eşitlemesi 35 ekledi: 13 K67 + 21 plan hash'i (eşitleme P10.8 hücresine P10.8a–e hash'lerini yazdı) + 1 konu öneki (`641bc6c`).

**Gerçek neden ve önceki iddia.** "Sayfa 19.11'den kalma, yeniden üretilmedi" iddiası **doğru ama eksik**: 60 hatanın 60'ı sayfanın eski
değeriyle bugünkü kaynağın farkı; denetim hatalı değil. Eksik olan: sayfa **yeniden üretilemiyordu**. `641bc6c` K67'yi açık karar olarak
kuyruğa ekledi; `F9c-uret.py`'nin `GRUP` sözlüğünde K67 yok → `KeyError: 'K67'`. Ayrıca üreticideki elle yazılmış metinler (P10.8 satırı,
F10 tablosu, ön soru, başlık tarihi) 19.11 hâlindeydi; yalnız yeniden üretmek sayfaya kapanmış işleri "açık" diye yazdırırdı.

**Düzeltme (kaynakta, `F9c-uret.py`).** Muafiyet eklenmedi, denetim değişmedi.
1. `GRUP["K67"] = ("A", …)`: grup **TASLAK** (alım sorusu; `GRUP_AD["A"]` tanımı), orkestratör onaylar ya da değiştirir.
2. Elle yazılmış metinler bugünkü kayda göre: P10.8 satırı (P10.8a kupon dosyaları hazır, basılmadı; P10.8b–e kapananlar; parça bekleyenler
   ve sonraki CAD paketine kalanlar plan P10.8 hücresinden ve kuyruktan), F10 tablosunda montaj rehberi / CAD / depo satırları ve önerilen
   sıra (madde 1 yapıldı, madde 6'da P10.8d'de yapılanlar), ortak ön soruya ve sipariş satırına K67 (CAD 52, liste 48), tutarsızlık
   notlarına K67 ve demo, yenileme notu, başlıkta "yenileme P10.8f, 21.11.2026". "Kapalı alt paketler:" kalıbı kullanılmadı (P10.8a planda
   kapalı yazılmıyor; kalıp denetimi onu "Sürüyor" ister).
3. Sayfa `F9c-uret.py` ile yeniden üretildi (§ 8).

**Commit'ten sonra kalacak 3 hata (yapısal, muaf tutulmadı).** Sayfa kendi commit'inin hash'ini içeremez; P10.8f commit'inden sonra
`F9c-dogrula` beklenen 3 hata verir: commit sayısı (+1), eşleşmeyen commit (+1), "konu öneki bu pakette olan <yeni hash> commit hücresinde
yok". Emsal `e3aaf94` (aynı 3). Bu TAHMİN (commit yapılmadan ölçülemez); bir sonraki yenilemede kapanır.

## 3. İş 2: kare 17.10 (K1 alt adım 10), kesikten geçiş

**Önce.** Kamera üstten-önden (0; 1; 0,45), elektronik katı yarı saydam. Katın ortasındaki yarık (P108d: x −60…60, z 150…175) saydam
yüzeyde seçilmiyor; panel "karedeki Kablo yolu 11 ve 12 de kesikten geçer" diyor ama kareden doğrulanamıyordu (P108e-kontrol B3).

**Adaylar** (`planlama/d158/P108f-onizleme.py`, depodaki `rehber/` değişmeden geçici kopyada; kareler `P108f-olcum/onizleme/`):

| Aday | Sonuç |
| --- | --- |
| `k1_10_kenar` (saydam + kat kenar çizgisi) | yarığın sınırı siyah çizgi, mor hatlar yarığa giriyor; 8 uç etiketi yerinde → **seçildi** |
| `k1_10_opak_kenar` (opak kat) | geçiş çok net ama BTS7960 sol / sağ (uç 2, 4) katın altında kalıyor (U4 riski) |
| `k1_10_on_alcak`, `k1_10_on_orta` (öne alçak / orta kamera) | yarık BTS kartlarının ardında, daha az seçiliyor |

**Değişiklik.** `rehber_metin.py` `DEMET_ALT["K1"]` alt adım 10: `kenar=("Elektronik katı",)` (kamera, saydamlık, odak aynı). Panel metni
değişmedi (cümle artık kareden doğrulanabilir). Kare `kaynak-17-10-*.png` (önizleme) ve üretimden sonra `sonra/kare/` (§ 7).

## 4. İş 3: kare 17.4 (K1 alt adım 4), saplama numaraları

**Önce.** Karede dokuz M5 saplama görünüyor, numarası yok; panel "anahtarlı baranın 3 numaralı saplaması" gibi numara veriyor
(numaralama B5a'da: "robota önden bakınca soldan sağa").

**Çözüm: genel parça etiketi** (kablo ucu olmayan parçaya karede yazı).
- `rehber_metin.py` `PARCA_ETIKET`: konum → desen listesi (parça görünen adı düzenli ifadesi → yazı) ve isteğe bağlı not. 17.4:
  `Bara cıvatası M5x25 DIN 933 (anahtarlı N)` → `AN`, `(yıldız N)` → `YN`; not "A1–A4: anahtarlı baranın, Y1–Y5: yıldız barasının saplama
  numarası (robota önden bakınca soldan sağa)".
- `rehber_gorunum.py` `etiket_isle` (üretimin görünüm adımında, `uc_isle`'den sonra): yalnız o konumda görünen (`durum != gizli`) parçayı
  eşler; numaralı yazılarda parçaları kutu merkezinin x'ine göre sıralar ve numaraların 1..N sırasıyla geldiğini **denetler** (adla
  numara çelişirse üretim durur); aynı yazı iki parçaya düşerse, desen boş kalırsa, adım / alt adım yoksa durur. Veriye
  `sira_grup[].etiket` / `adimlar[].etiket` (yazı, parça, `ip` = kutu üstü merkezi, `ia` = kutu merkezi, yedek nokta; § 7),
  `etiket_not` ve `etiket_kaynak` yazar.
- Ölçüm: anahtarlı 1–4 x −37,5 / −12,5 / 12,5 / 37,5, yıldız 1–5 x −50…50 (+x = önden bakanın sağı); numaralama adla aynı (denetim geçti).
- `rehber/app.js`: `ETK` durumu, `ucCiz` içinde parça etiketleri uç etiketlerinden **önce** yerleşir (önce parçanın hemen üstü, sonra
  çevresi; güvenli alan içinde; işaret kümeleri, birbirleri ve parça noktalarıyla çakışmadan); kutuları uç etiketlerine engel. Çizim
  `g.etk` (beyaz kutu, koyu yazı, ince çizgi); F10d'nin saydığı `g.uc` değişmedi. Uç etiketleriyle aynı aç / kapa. `RehberTest.etiket()`
  sınama arayüzü; lejantta not (uç etiketi açıkken). `rehber/stil.css` `.ep` / `.et`. `rehber/yazdir.html` lejantta "Karedeki yazılar: …".

## 5. İş 4: kare B5a (adım 12), acil stop düğüm kartı

Aynı özellik: `PARCA_ETIKET[("B5a", 0)]`, desen `^Acil stop düğüm kartı` → "Acil stop düğüm kartı" (not yok). Kare `kaynak-12-*.png`:
kartın üstünde yazı, ince çizgiyle karta bağlı; iki uç etiketi (XL4016 C, dağıtım kartı C) yerinde.

## 6. Ön sınamalar (üretimden önce)

| Sınama | Sonuç |
| --- | --- |
| `node --check rehber/app.js`; `yazdir.html` iç betiği `node --check` | tamam / tamam |
| `rehber_denetim.py --kaynak` | 0; ascii kalıntı 0, onay farkı 0 (219 / 258 / 1201); CAD ad/kod 973 (P10.8e zinciriyle aynı) (`P108f-olcum/ara/kaynak.log`) |
| `rehber_kablo.py` | 0; GEÇER (`ara/kablo.log`) |
| `F10l-birlesim.py` | 0; GEÇER (rehber metninde cümle değişmedi; `ara/birlesim.log`) |
| `P108f-etiket-bozma.py` (yeni; `etiket_isle` bozma sınaması) | 0; sağlam koşu 10 yazı; **8 / 8 bozma yakalandı** (`ara/etiket-bozma.log`) |
| `F10d-dogrula.py --yalniz-uc` önizleme kopyasında | 0; 23 konum, 59 etiket, hata 0 |
| Aynı ölçüm `HEAD` rehberinde, karşılaştırma | uç etiketi yeri değişen tek konum 17.4 (parça etiketlerinden kaçtı): yazdırma karesinde 4 etiket ≤ 2 px, etkileşimli kipte ≤ 21 px; öbür 22 konum × 2 kip aynı |

## 7. Rehber üretimi ve bir düzeltme

**Üretim 1** `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (FreeCAD'siz; GLB ve parça verisi P10.8e'den): 14:48:28–15:30:45,
çıkış 0, Traceback 0 (log `P108f-olcum/uretim.log`, `uretim.durum`). "parca etiketi 2 konumda 10 yazi", "rehber_metin alanlari, degisen 1:
K1.10 kenar"; tarayıcı 50 / 50, konsol 0, "ek kontrol sorunlu: -"; PDF 90 sayfa; alt adım satırlarının hepsi GECTI. P10.8e üretim 2
logundan tek anlamlı fark: 17.4 kadraj D 336 → 349 (etkileşimli kipte lejant notu ikinci satıra iniyor, güvenli alan küçülüyor, kamera
≈ % 4 uzakta).

**Kare bakışında bulunan hata.** Yazdırma karesi `rehber/goruntu/adim-17-04.png`'de A4 yazısı yoktu (8 / 9). Önizleme aracı kareyi
Chrome `--screenshot` ile çekiyordu, üretim ve F10d DevTools ile (`cekim=1`); iki çekimin kadrajı 17.4'te birkaç piksel farklı, önizlemede
A4 sığıyordu. Yeni ölçüm aracı `planlama/d158/P108f-etiket-olc.py` (F10d uç etiketi ölçümüyle aynı çekim; kural: verideki her yazı iki
kipte çizilir, DOM sayısı eşit, kutu güvenli alanda, kutular birbiriyle ve uç etiketleriyle çakışmaz) üretim 1 çıktısında **KALDI**: 17.4
sahne ve etkileşimli kipte A4 "güvenli alanın dışında" (saplama ucu ekran y 45 / 51 px, başlık şeridinin altında).
**Düzeltme:** `etiket_isle` her yazıya yedek nokta `ia` (kutu merkezi) yazar; `app.js` üst nokta güvenli alan dışındaysa onu dener.
Önizleme kopyasında: `P108f-etiket-olc.py` 2 konum, 10 yazı, hata 0, GECTI (DevTools kareleri `onizleme/cekim-kaynak/`: A4 saplamanın
üstünde, A3'ün yanında); `F10d-dogrula.py --yalniz-uc` 23 konum, 59 etiket, hata 0; bozma sınaması yine 8 / 8; `--kaynak` 0 (ascii 0,
onay farkı 0), `rehber_kablo.py` 0, `F10l-birlesim.py` GEÇER, `node --check` tamam. `P108f-onizleme.py`'ye `cekim=1` eklendi (aynı
çekim değil, yine `--screenshot`; kesin ölçüm `P108f-etiket-olc.py --png`).

**Üretim 2** (aynı komut, log `P108f-olcum/uretim2.log`, `uretim2.durum`): 15:39:17–16:21:57, **çıkış 0**, Traceback 0. Parça etiketi 2
konum 10 yazı; uç etiketi 24 konum 59 etiket (üretimin sayımı; F10d'nin sayımıyla 23 konum, P10.8e ile aynı); tarayıcı 50 / 50, konsol 0,
"ek kontrol sorunlu: -"; PDF 90 sayfa (adım 50, devam 40), en küçük yazı 8,1 pt.
Sonra `py -3 -B -X utf8 planlama/d158/P108f-etiket-olc.py --json P108f-olcum/sonra/etiket-olc.json --png P108f-olcum/sonra/kare`: çıkış 0,
**2 konum, 10 yazı, hata 0, GECTI** (17.4 iki kipte 9 / 9, B5a iki kipte 1 / 1; log `sonra/etiket-olc.log`, DevTools kareleri
`sonra/kare/devtools/`).

**Sonra kareleri** `P108f-olcum/sonra/kare/` (`yazdirma-adim-*.png` = `rehber/goruntu/`, `etkilesimli-adim-*.png` = `planlama/rehber/goruntu/`;
üretim 2'den). Önce ↔ sonra: 17.10 yarığın sınırı siyah çizgi, mor hatlar yarığa giriyor (önce yarık seçilmiyordu); 17.4 dokuz saplamada
A1–A4 / Y1–Y5 ve lejantta anlamı (önce numara yok); B5a "Acil stop düğüm kartı" yazısı kartın üstünde (önce etiketsiz).

**Değişen öbür kareler.** `planlama/rehber/goruntu/adim-33-04.png`, `adim-33-07.png` (üretim 1'de `adim-33-04`, `adim-47`, `adim-49-05`):
HEAD ile Σ|ΔRGB| > 24 olan piksel **0** (fark kutusu küçük görünüm köşesinde, kenar yumuşatma gürültüsü). Kaynak değişikliği değil;
`planlama/rehber` toptan eklenirse commit'e girer, zararsız.

## 8. F9c yenileme

Üretimden sonra (sayfa `planlama/rehber/kontrol.json`'u okur): `py -3 -B -X utf8 planlama/d158/F9c-uret.py` çıkış 0, "karar: toplam 67,
açık 27", `sonuc-rapor.html` 154.009 bayt. `F9c-dogrula.py --tarayicisiz`: **GEÇER (hata 0)** (`sonra/F9c-tarayicisiz.log`).
`F9c-dogrula.py --goruntu`: **GEÇER (hata 0)**; 1400 ve 360 px'te konsol hatası 0, taşan öğe 0; 10 `F9c-goruntu-*.png` yeniden yazıldı
(`sonra/F9c-goruntu.log`). Önce 60 → sonra 0. Önceki 25'in 25'i ve yeni 35'in 35'i kapandı; kalan yok (commit'ten sonra beklenen 3, § 2).

## 9. Zincir

`bash planlama/d158/P108f-zincir.sh` (P108e-zincir.sh'nin kopyası, yalnız log yolu `P108f-olcum/`), üretim 2'den ve F9c yenilemesinden
sonra: 16:22:59–17:25:58, loglar `P108f-olcum/zincir/`, ilerleme `P108f-olcum/zincir.durum`. **15 adımın 15'i çıkış 0.**

| # | Komut | Çıkış | Sonuç |
| --- | --- | --- | --- |
| 0a | `carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |
| t1 / t2 | `kupon_tazelik.py` / `--bozma-denemesi` | 0 / 0 | TAZE (16) / 4 / 4 |
| 2a | `rehber_kablo.py --veri …` | 0 | GEÇER |
| 2b | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 136 / 136 |
| 2c | `rehber_denetim.py --kaynak` | 0 | ascii 0, onay farkı 0 (219 / 258 / 1201) |
| 3 | `rehber_denetim.py` | 0 | ascii 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0, elektrik 0 |
| 4 | `F10f-dogrula.py` | 0 | GECTI (587 s) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | GECTI (1.013 s); `renk_demo` KALDI (bilinen karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 0 | GECTI (1.150 s); uç etiketi 23 konum, 59 etiket, hata 0 |
| 6g | `F10d-dogrula.py --gizli …` | 0 | bilgi: 103 / 116 (P10.8e ile aynı) |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | GECTI (772 s) |
| 8 | `F9b-dogrula.py` | 0 | GECER (hata 0); demo yeniden üretilmedi (GLB ve montaj değişmedi) |
| 9 | `carpisma_kos.py kontrol` | 0 | kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | GEÇER, kötüleşen yok |

Zincir `planlama/d158/F10a-dogrula.json`, `F10d-dogrula.json`, `F10e-dogrula.json`, `F10f-dogrula.json`'u yeniden yazdı.
Zincirden sonra `F9c-dogrula.py --tarayicisiz` yine **0** (`sonra/F9c-tarayicisiz-zincirden-sonra.log`); eski kirli dosyalar
`md5sum -c P108f-olcum/kir-bas.md5` 21 / 21 aynı. Kilit satırı ve bu günlük güncellendikten sonra son koşu: F9c 0
(`sonra/F9c-tarayicisiz-son.log`), `--kaynak` 0. Kanıt klasörü `P108f-olcum/` ≈ 11 MB (önizleme kareleri dahil).

## 10. Kapanış tarifi (commit ajanı için)

Depo kökünden, `export PYTHONIOENCODING=utf-8`; Python komutları `py -3 -B -X utf8 …`. Uzun adımlar Bash arka planında `.durum` kalıbıyla.

**Elle düzenlenen kaynaklar**
- `planlama/d158/F9c-uret.py` (GRUP K67 TASLAK; P10.8 satırı, F10 tablosu, ön soru, tutarsızlık notları, başlık tarihi; § 2)
- `tasarim/freecad/rehber/rehber_metin.py` (`DEMET_ALT["K1"]` alt adım 10 `kenar`; yeni `PARCA_ETIKET`; panel metni değişmedi)
- `tasarim/freecad/rehber/rehber_gorunum.py` (yeni `etiket_isle`, `isle()` çağrısı)
- `rehber/app.js` (`ETK`, `ucCiz` parça etiketi yerleşimi ve çizimi, lejant notu, `RehberTest.etiket`), `rehber/stil.css` (`.ep`, `.et`),
  `rehber/yazdir.html` (lejantta "Karedeki yazılar")
- `planlama/dongu-158.md` (yalnız kilit tablosundaki P10.8f satırı)
- Yeni: `planlama/d158/P108f-gunluk.md`, `P108f-onizleme.py`, `P108f-etiket-bozma.py`, `P108f-etiket-olc.py`, `P108f-zincir.sh`

**Üretilen çıktılar** (elle dokunulmadı): `rehber/veri/rehber-veri.js`, `rehber-veri.json`; `rehber/goruntu/adim-12.png`, `adim-17-04.png`,
`adim-17-10.png`; `planlama/rehber/` (`kontrol.json`, `Lale-montaj-rehberi.pdf`, `goruntu/adim-12.png`, `adim-17-04.png`, `adim-17-10.png`,
gürültü `adim-33-04.png`, `adim-33-07.png`); `planlama/d158/sonuc-rapor.html`, `planlama/d158/F9c-goruntu-*.png` (10); zincirin yazdığı
F10 JSON'ları (§ 9); kanıt klasörü `planlama/d158/P108f-olcum/`.

**Commit'ten önce bakılacaklar**
1. `F9c-dogrula.py --tarayicisiz` commit'ten hemen önce 0 olmalı (A'nın son koşusu § 9 sonunda). Commit'ten sonra 3 hata beklenir (§ 2);
   muaf tutulmadı.
2. `GRUP["K67"]` grubu TASLAK (A); orkestratör onaylamalı.
3. Kareler: `P108f-olcum/once/kare/` ↔ `sonra/kare/` (17.10, 17.4, B5a).
4. `P108f-etiket-olc.py` 0 (parça etiketi iki kipte tam) ve `F10d` uç etiketi 59, hata 0 (§ 9).

**Kontrol komutları** (A'nın sonucu beklenen):

| # | Komut | Beklenen |
| --- | --- | --- |
| k1 | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0; ascii 0, onay farkı 0 (219 / 258 / 1201) |
| k2 | `tasarim/freecad/rehber/rehber_kablo.py` | 0; GEÇER |
| k3 | `planlama/d158/F10l-birlesim.py` | 0; GEÇER |
| k4 | `planlama/d158/P108f-etiket-bozma.py` | 0; 8 / 8 |
| k5 | `planlama/d158/P108f-etiket-olc.py` (≈ 1 dk; tarayıcı) | 0; 2 konum, 10 yazı, hata 0 |
| k6 | `node --check rehber/app.js` | tamam |
| k7 | `planlama/d158/F9c-dogrula.py --tarayicisiz` | 0; GEÇER (hata 0) |
| k8 | `md5sum -c planlama/d158/P108f-olcum/kir-bas.md5` | 21 / 21 OK (eski kirli dosyalar değişmedi) |
| k9 | `bash planlama/d158/P108f-zincir.sh` (≈ 55 dk; arka planda) | 15 / 15 çıkış 0 (§ 9) |
| k10 | `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (isteğe bağlı, ≈ 43 dk) | 0; parça etiketi 10, uç etiketi 59, PDF 90 |

**Denenmemiş:** k10'dan sonra F9c'nin yeniden üretilmesi gerekip gerekmediği (A'da üretimden sonra F9c üretildi; k10 `kontrol.json`'u
yeniden yazar, değerler aynı kalmalı); `P108f-zincir.sh`'nin argümanlı çağrısı.

**`git add` listesi**
```
git add planlama/dongu-158.md planlama/d158/F9c-uret.py planlama/d158/sonuc-rapor.html planlama/d158/F9c-goruntu-*.png \
  planlama/d158/P108f-gunluk.md planlama/d158/P108f-onizleme.py planlama/d158/P108f-etiket-bozma.py \
  planlama/d158/P108f-etiket-olc.py planlama/d158/P108f-zincir.sh planlama/d158/P108f-olcum \
  planlama/d158/F10a-dogrula.json planlama/d158/F10d-dogrula.json planlama/d158/F10e-dogrula.json planlama/d158/F10f-dogrula.json \
  planlama/rehber rehber/app.js rehber/stil.css rehber/yazdir.html rehber/veri rehber/goruntu \
  tasarim/freecad/rehber/rehber_gorunum.py tasarim/freecad/rehber/rehber_metin.py
```
Zincirin değiştirmediği F10 JSON'unu `git add` sessizce atlar. Eklemeden önce `git status --short` ile listede olmayan değişiklik
kalmadığına bak (aşağıdakiler hariç).

**Dışarıda kalanlar (eklenmez, dokunulmaz):** `tasarim/freecad/kabuk/gorsel/` 13 PNG, `tasarim/freecad/montaj/yerlesim-kontrol.json`,
kökteki `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`, `planlama/d158/P108d-olcum/ara1.json`,
`planlama/d158/P108d-kontrol-olcum/b2-tarama.nabiz` (21 eski kirli dosya; md5 `P108f-olcum/kir-bas.md5`), `planlama/d158/FREECAD-KILIT.txt`.

**Commit mesajı önerisi**
```
Lale P10.8f: ufak dört: F9c sayfası yeniden üretildi (60 → 0; K67 üreticide yoktu), 17.10 kat kesiği kenar çizgisiyle, 17.4 saplama numaraları (A1–A4, Y1–Y5) ve B5a acil stop düğüm kartı karede yazılı (parça etiketi)
```

## 11. Durum

| İş | Durum | Önce → sonra |
| --- | --- | --- |
| 1 F9c | yapıldı (kaynakta: üretici) | 60 → 0 hata; K67 `KeyError` → üretiliyor; muafiyet 0 |
| 2 kare 17.10 | yapıldı (veri alanı `kenar`) | yarık seçilmiyor → kat kenar çizgisiyle yarık ve içine giren hatlar görünüyor |
| 3 kare 17.4 | yapıldı (parça etiketi) | numara 0 / 9 → 9 / 9 iki kipte; lejantta anlamı |
| 4 kare B5a | yapıldı (parça etiketi) | düğüm kartı etiketsiz → "Acil stop düğüm kartı" iki kipte |

CAD geometrisi değişmedi; FreeCAD açılmadı.

**Doğrulanmayanlar:** commit'ten sonra F9c'nin tam 3 hata vereceği (emsalden TAHMİN, § 2); görev özetindeki "59"un kaynağı (A 60 ölçtü);
K67 grubu (TASLAK); kare görünüşü bir insan gözüyle değerlendirilmedi (A'nın bakışı ve ölçüm araçları); yazdırılabilir PDF'teki 17.4 / B5a
sayfaları ayrıca açılıp bakılmadı (üretim "esleme tutarli, tasan -" dedi).

## 12. Fark edilen, dokunulmayan

- 17.1 ve 17.5 panelleri de saplama numarası veriyor, B5a metni numaralama kuralını veriyor; bu karelerde numara yazısı yok. `PARCA_ETIKET`'e konum eklemek tek satır, ama kapsam dışı.
- Basılı sayfa lejantı `sema_on` (17.11, P10.8e) notunu yazmıyor; etkileşimli lejant yazıyor.
- `F9c` sayfası yapısı gereği kendi commit'ini taşıyamaz (§ 2); her commit'ten sonra 3 hata. Denetimde "son commit sayfanın commit'i ise
  muaf" gibi bir kural yok; eklenmedi (görev: denetimi gevşetme).
- K67'nin grubu taslak (A); orkestratör onayı gerekir.
