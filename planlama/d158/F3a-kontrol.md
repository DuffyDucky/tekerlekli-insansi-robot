# F3a kontrolü: elde yük tablosu ve servo payları (P3.1, P3.2), 09.11.2026

Ajan B (bağımsız kontrol). Girdi: `dongu-158.md` §1–§2, §3 F3, §4 K3/K9; `F3a-brief.md`; A'nın çıktıları `F3a-gunluk.md`, `F3a-yuk.py`,
`F3a-yuk.json`. Karşılaştırma: `karar-kuyrugu.md` K2/K3/K9, `KY/uygulama-ivme.json` + `uygulama_ivme.py`, `dirsek_montaj.py` §5 +
`dirsek-analiz.json`, `kafa_montaj.py` §6 + `kafa-analiz.json`, `KY/hat-secenek-{0,a,b}.json` + `hat_secenek.py`, `montaj-analiz.json`, `arayuz.py`,
`servo-10-oneri.md`, `y2/Y2a-kontrol.md`, `kararlar-2026-10-29.md`, `taslak-170/kol-analiz/kol-analiz.json`. FreeCAD kullanılmadı; bu dosya dışında
hiçbir dosya yazılmadı. `KY/` = `tasarim/freecad/lale158/kafa-yerlesim/`.

## Genel karar: **KOŞULLU**

Yöntem ve sayılar doğru: betik scratchpad kopyasında yeniden koşuldu ve depodaki `F3a-yuk.json` ile **bayt bayt aynı** çıktı verdi
(md5 `a960878b…`); 0 / 100 / 500 g'ın 18 devrilme anahtarı ve 4 servo sonucu kaynak JSON'larla tarafımdan ayrıca karşılaştırıldı, fark 0.
Öneri tabloyla tutarlı. Koşullar küçük: iki yerde "2×" ifadesi sayıyla çelişiyor (S2 1,996), tilt ilk temas açısı eski modelin ölçümü
olarak işaretlenmemiş, HAT kütlesinin varsayım olduğu ve kolun mevcut ivmeli payı yazılmamış, K3 eki "varsayılan" satırı birebir aktarılabilir değil.
Hepsi ≤ 2 satır; A'ya ayrı düzeltme turu **gerekmez**, kayıt ajanı (C) uygular.

## Madde tablosu

| # | Denetim | Sonuç | Kanıt |
|---|---|---|---|
| 1 | Betik yeniden koşu | ✔ | `F3a-yuk.py` kopyası (yalnız `ROOT` satırı ortam değişkenine çevrildi; çıktı scratchpad'e) → `F3a-yuk.json` depodakiyle bayt bayt aynı; depodaki JSON'un md5'i koşudan önce ve sonra aynı |
| 2 | 0 / 100 / 500 g, 18 anahtar | ✔ | Kendi karşılaştırmam: `uygulama-ivme.json izgara_yuk_{0,100,500}g.en_kotu` × `F3a-yuk.json P3_1.izgara`: a_dev farkı 0,000 (18/18), poz + kip 18/18 aynı, AM ≤ 0,01 mm; `a_sinir_pay15` ve `fren_pay.duz_min` 3/3 aynı. Ev pozu 26.115,5 ↔ 26.115,6 g (yuvarlama), AM aynı |
| 3 | Kol servo, DA ile | ✔ | `dirsek-analiz.json tork.sonuc`: yüksüz / 500 g torku S1 10,95 / 31,22, S2 11,16 / 31,50, dirsek 2,42 / 12,62, bilek 0,02 / 0,67; `izinli_yuk_2x_g` 105 / 99 / 112 / 3.600: hepsi aynı. Dirsek poz farkı gerçekten bağ: S1 90'da [90,30,0,90], [90,100,0,−90], [90,115,0,90], [90,120,0,0] dördünde dirsek torku 12,618 (500 g), S2 torku 0 (S2 ekseni düşey) |
| 4 | 50 ve 200 g aynı yöntem mi | ✔ | Aynı `izgara()` ve `tork()` fonksiyonu, yalnız `yuk` argümanı farklı (`F3a-yuk.py:324-326`, `377`). Kaynak betikle (`uygulama_ivme.py:32-80`, `dirsek_montaj.py:437-526`) satır satır karşılaştırdım: formül, ızgara, S2 117 kırpması, kablo payı 400 g, kip, 2× ikiye bölme aynı |
| 5 | Elle sağlama | ✔ | S2 yüksüz: Σ m·\|y\| = 159·57,6 + 110,7·174,7 + 200,9·252,5 + 89·363,6 = 111.584 g·mm = 11,16 kg·cm (DA 11,16). S1 90/5: ≈ 10,96 (DA 10,95; göbek −1,42, S2 5° −0,02). Kaldıraçlar 405,4 / 406,9 / 203,9 mm (`el_ucu` y −406,9, dirsek ekseni y −203) |
| 6 | "Yük her iki elde" | ✔ | K3'teki sayılar zaten `uygulama_ivme.py:41-46` yönteminden: yük **her iki** elin ucunda `yuk_g`. Servo torku tek kol, yük o elde (`dirsek_montaj.py:466-468`). Yani "100 g" her iki hesapta da "her elde 100 g". A bunu açık yazmış (günlük :24, :47, :88) |
| 7 | En kötü pozlar | ✔ | S1: kol öne yatay (S1 90, S2 alt sınır 5, dirsek 0); S2: kol yana yatay (S1 0, S2 90); dirsek: ön kol yatay (S1 90 + dirsek 0; S1 0 + dirsek 90 de 12,57 ile neredeyse eşit). Yatay kaldıraç bu pozlarda en büyük; ızgara 5° ve sınırlar dahil. Devrilme: düz ve rampada en kötü yön her yükte "geri" (S2 120, S1 75→90→105) |
| 8 | Servo paydası | ✔ (not) | Stall: DS3235 30,4 kg·cm = 29 / 32 kg·cm @ 5 / 6 V'tan 5,48 V hat gerilimine ara değer (`arayuz.py:183-184`); MG996R 9,4 kg·cm @ 4,8 V (11 @ 6 V) üretici sayfası (`dirsek_montaj.py:494`). İkisi de DA ile aynı, A gerilimleri yazmış (:30, :91). Not: gerilim tabanı karışık; MG996R için hat geriliminde 10,29 (`kol-analiz.json` `stall_eff`) alınsa dirsek pay ≥ 1 sınırı 342 → ≈ 386 g, 2× sınırı 112 → ≈ 134 g olur; bağlayan 2× ölçütü yine S2 99 g, öneri değişmez. DS3235 değerlerinin kaynağı zayıf (`taslak-170/kol-analiz/NOTLAR.md:15`: "PDF indirilemedi", arama özeti) — A'nın değil, proje genelinin açığı |
| 9 | Bilek 463 | ✔ (not) | 9,4 / 0,0203 = 463 (DA `yuksuz_pay` 462,87). Bilek ekseni ön kol ekseni (`bilek_yon` 0,1,0), yük kancada 13 mm kaçık: tork çok küçük, oran yuvarlamaya duyarlı. Sayı doğru, yorumu "≫ 1" yeterli; yük elde eksenden kaçık tutulursa (ör. 50 mm) bilek torku 4× büyür, yine ≫ 1 |
| 10 | Statik sınırın yazılması | ✔ / koşul 3 | Açık yazılmış (:91-92, :167). Eksik: projede kol için **ivmeli** pay zaten var: `taslak-170/kol-analiz/kol-analiz.json` `ozet.varyant.1.25.servo.DS3235.eklem` yüksüz `pay_ivmeli` S1 1,64, S2 1,62, dirsek 3,18 (α 26,2 rad/s², kafa ile aynı profil). Bkz. aşağıda B tahmini |
| 11 | Öneri ↔ tablo | ✔ / koşul 1 | ≤ 100 g/el düzde: düz 2,057, fren 1,714 (≥ 1,5), servo S1 2,03 / S2 1,996 / dirsek 2,11. Rampa 100 g 1,479 < 1,5 → "rampada yüksüz" doğru. 50 g rampa 1,499: öneri bunu "rampada hiç yük yok" ile doğru ele alıyor; kendi taramam: 48 g 1,500, 50 g 1,499 (eşik ≈ 48 g, 15° ızgarada; sık ızgara sınırı ancak düşürür). Çelişki yalnız sözde: "100 g 2× hedefini tutan en büyük değer" (:93) ve "≤ 100 g'da bütün servolar ≥ 2,0" (:154), oysa S2 1,996 ve kesin 2× sınırı 99 g |
| 12 | 2× gerekçesinin kaynağı | ✔ (zayıf) | "2×" bir karar değil, 21.10'dan beri hesaplanan referans: `dirsek_montaj.py:511` (`izinli_yuk_2x_g`), `kararlar-2026-10-29.md:24` ("2× pay için el yükü ~100 g"), `taslak-170 yuk_2x_g`, `yazilim-notu-stowent-170.md:21`. A "projenin önceki hedefi" diyor; doğru ifade "projede kullanılan referans". Gerekçeyi asıl güçlendiren ivmeli pay (madde 10) |
| 13 | P3.2 kol, CAD ↔ kod | ✔ | `F3a-yuk.json P3_2.<eklem>.kod_*` = `cad_*` (S1 0…160, dirsek 0…110 en kötü pozu değiştirmiyor; S1 90 ve dirsek 0 iki aralıkta da). Horn kayması (Ç6) notu doğru |
| 14 | Pan kod = ekstrapolasyon | ✔ | Açık işaretli (:142 yıldız, :148-149, :169). I(θ) = A + B cos 2θ + C sin 2θ, 3 noktadan tam uydurma. Benim değerlendirmem: tilt ekseni pan ekseninden z 25 mm kaçık olduğu için gerçek eğride cos θ / sin θ terimleri de var; bunların ±20'ye taşıdığı hata ≈ 0,012 × b₁ ≈ 2·10⁻⁶ kg·m² (b₁ ≈ 1,5·10⁻⁴), payda < 0,01 etki. 2,17 sağlam |
| 15 | Tilt ±20 ilk temas +18 / −17 | ⚠ koşul 2 | Kaynak **ölçüm** ama **eski model**: `y2/Y2a-kontrol.md:54-56` (29.10, 0,5° adım, QLED kafa 04.11'den önce); `arayuz.py:582`, `servo-10-oneri.md:83`, `kararlar-2026-10-29.md:20` hep bunu tekrarlıyor. Güncel model ölçümü: `kafa-analiz.json` (05.11) `tarama.serbest_tilt` [−15, 15], `tarama.ilk_carpan` +20'de "Yüz kabuğu (ön) sağ × Rulman yuvası" 327,4 mm³, −20'de "Arka kafa kabuğu sağ × Rulman yuvası" 654,9 mm³ (5° adım). Sonuç değişmiyor: **kodun ±20'si güncel CAD'de çakışıyor**; güncel modelde ilk temas 15° ile 20° arasında, kesin açı ölçülmedi |
| 16 | AI HAT+ ile rampa 1,515 | ✔ / koşul 4 | Kütle 28,1 g = HS `tork_hatli.kafa_grubu_g` 1.598,9 − `tork_hatsiz` 1.570,8; bu, `hat_secenek.py:87-94` HAT takımı 30 g (kart 22 + başlık 4 + FFC 1 + 4 × (ayak 0,5 + vida 0,25); **varsayım**, `hat_secenek.py:12`) eksi kaldırılan 4 Pi üst vidası. Nokta global (−12,2; 1.538,8; −35,8). Hesap: aynı ızgara + nokta kütle. Kendi koşum: 28,1 g ve 30 g ikisi de rampa 1,515, düz 2,093 (40 g'da bile 1,513). Elle: h 532,19 → 533,27 mm, rampa 2,279 → 2,272 m/s² → 1,515 ✔ |
| 17 | K3 eki taslağı | ⚠ koşul 5 | Sayılar doğru, kaynak anahtarlar var. Eksik: "Öneri" satırı K3'ün `Varsayılan:` satırının yerine geçeceğini, "her elde" tanımının b seçeneğine gireceğini ve c'nin (500 g) servo nedeniyle ancak K9 b ile mümkün olduğunu söylemiyor. Düzeltilmiş metin aşağıda |
| 18 | K9 karar taslağı | ✔ | Seçenek (a / b), sayısal etki (500 g'da 0,97 / 0,97 / 0,74; b için gereken stall 31,2 / 31,5 / 12,6, 2× için 62,4 / 63,0 / 25,2 kg·cm), varsayılan (a) var; "1,65 m'den, yeniden ölçülmedi" cümlesinin yerine geçecek metin net. DA zaten 1,58 commit'inde (`bcaa6df`, 04.11) üretilmiş; A'nın bugünkü `montaj-analiz.json` parçalarıyla birebir üretmesi bunu doğruluyor. Küçük not: "DA 400,5 g" (:159) — gruplar 110,7 + 200,9 + 89,0 = 400,6 g; yuvarlama, düzeltme gerekmez |
| 19 | Mevcut dosya değişmedi | ✔ | F3a brief'inden (02:00:59) sonra değişen dosyalar: yalnız `F3a-gunluk.md`, `F3a-yuk.py`, `F3a-yuk.json` (A), `F1b-kontrol.md` (paralel B), `dongu-158.md` (orkestratör). `git status`'taki öteki "M" dosyalar `F1b-gunluk.md` "Değişen dosyalar" listesinde ya da K23 (03.11 tarihli kabuk görselleri, `yerlesim-kontrol.json`; F1b günlüğü :38, :186). `karar-kuyrugu.md` 08.11 23:48 (F3a'dan önce). F3a `__pycache__` bırakmadı |
| 20 | Takma ad | ✔ | F3a dosyalarında arama: 0 eşleşme; "Ahmet" kullanılmış |
| 21 | Regresyon `--yazma` | ✔ | `py -3 planlama\d158\regresyon.py --yazma` → GEÇER, 10/10 "aynı" (rampa 1,519, tilt 3,64, pan 2,21, boy 1.580, çakışmalar 0, mik-hop 574,3, SY8205 0); `regresyon.json` ve `regresyon-son-kosu.json` md5'leri koşudan (02:15) önce ve sonra aynı. İkisi 02:17:55'te F1b hattınca (aynı dakikada `kabuk_montaj.py`, `F1b-rapor.html`) yeniden yazıldı; F3a / B ile ilgisi yok |

## B tahmini: ivme torkuyla kol payı (karar için bilgi, A'nın işi değil)

Proje yöntemi (`taslak-170/taslak_hesap.py` `kol_servo`: en kötü statik pozdaki atalet × α 26,2 rad/s²) ve oradaki kol ivme torku
(×1,25 kol, DS3235: S1 7,69, dirsek 0,85 kg·cm) + yükün nokta kütle ataleti (m r² α; r = 405,4 / 203,9 mm), statik tork F3a'dan.
Kol ataleti 1,70 taslağından (bugünkü S1 statik torku ondan %1 farklı: 10,95 ↔ 10,85); **kaba tahmin, doğrulanmadı**:

| Her elde | S1 statik + ivme → pay (stall 30,4) | Dirsek statik + ivme → pay (stall 9,4) |
|---|---|---|
| 0 g | 10,95 + 7,69 → 1,63 (kaynak 1,64) | 2,42 + 0,85 → 2,87 |
| 50 g | 12,98 + 7,69 + 2,19 → 1,33 | 3,44 + 0,85 + 0,55 → 1,94 |
| 100 g | 15,01 + 7,69 + 4,39 → **1,12** | 4,46 + 0,85 + 1,11 → 1,46 |
| 200 g | 19,06 + 7,69 + 8,77 → **0,86** | 6,50 + 0,85 + 2,22 → **0,98** |

Yorum: statik "2×" ile ivmeli "≥ 1" aşağı yukarı aynı yükte (~100 g) buluşuyor; 200 g ivmeli hareketle (60° / 0,4 s) S1 ve dirsekte 1'in altına
iniyor. Bu, A'nın ≤ 100 g önerisini destekliyor ve "brief ölçütü tek başına ≈ 340 g'a izin veriyor" cümlesinin yalnız statik için geçerli olduğunu
gösteriyor. Karar kuyruğuna yazılırsa "B tahmini, taslak-170 kol ataleti" diye işaretlenmeli.

## Koşullar (≤ 2 satır, birebir; kayıt ajanı C uygular)

Hepsi `planlama/d158/F3a-gunluk.md`.

1. **:93** eski → yeni
   - eski: `   S1 2,03, S2 2,00 (1,996, 2×'in hemen altında), dirsek 2,11. 100 g, 2× hedefini yuvarlak sayıyla tutan en büyük değer.`
   - yeni: `   S1 2,03, S2 2,00 (1,996, 2×'in hemen altında), dirsek 2,11. 100 g, 2× referansına en yakın yuvarlak değer (kesin 2× sınırı 99 g, S2).`
   
   **:154** eski → yeni
   - eski: `Yüksüz ve ≤ 100 g'da bütün servolar ≥ 2,0 (S2 1,996); kafa ≥ 2,16.`
   - yeni: `Yüksüz ve ≤ 100 g'da bütün servolar ≈ 2 ve üstü (en düşük S2 1,996); kafa ≥ 2,16.`
2. **:152** eski → yeni
   - eski: `tilt 3,27, pan 2,16. Tilt ±20'nin asıl sorunu tork değil, çakışma: ilk temas +18° / −17° (F5 Ç4, `kararlar-2026-10-29.md` KZ3).`
   - yeni: `tilt 3,27, pan 2,16. Tilt ±20'nin asıl sorunu tork değil, çakışma: güncel model `kafa-analiz.json` `tarama.ilk_carpan` ±20'de çakışıyor`
     `(327,4 / 654,9 mm³; ±15 serbest, 5° adım); +18° / −17° 29.10 ölçümü (`y2/Y2a-kontrol.md:54`, QLED öncesi kafa, 0,5° adım).`
3. **:167** eski → yeni
   - eski: `1. Kol servo payı **statik** (yerçekimi); kol hareketinin ivme torku yok (kafada var). Stall ölçütü servonun tutma sınırı değil; 2× hedefi bu yüzden anlamlı.`
   - yeni: `1. Kol servo payı **statik** (yerçekimi); kol ivme torku bu pakette yok. Mevcut ivmeli pay (yüksüz, ×1,25 taslak): `taslak-170/kol-analiz/kol-analiz.json` S1 1,64, S2 1,62, dirsek 3,18;`
     `yüklü ivmeli hesaplanmadı (B kaba tahmini: 100 g'da S1 ≈ 1,1, 200 g'da < 1, `F3a-kontrol.md`). Stall ölçütü servonun tutma sınırı değil; 2× referansı bu yüzden anlamlı.`
4. **:118** eski → yeni
   - eski: `- AI HAT+ (K2, 28,1 g net) eklenince yüksüz rampa 1,519 → 1,515, düz 2,097 → 2,093 (a ve b aynı); sonuç değişmiyor.`
   - yeni: `- AI HAT+ (K2; 30 g varsayım, Pi'nin 4 üst vidası çıkınca net 28,1 g: HS `kafa_grubu_g` farkı) eklenince yüksüz rampa 1,519 → 1,515, düz 2,097 → 2,093`
     `(a ve b aynı; 30 g ile de 1,515); sonuç değişmiyor.`
5. **:119** eski → yeni
   - eski: `- **Öneri:** b, elde ≤ 100 g (her el), düz zeminde; rampada yüksüz (ya da rampada kollar ev pozunda zorlanırsa ≤ 100 g).`
   - yeni: `- **Varsayılan (K3 "Varsayılan" satırının yerine):** b, her elde ≤ 100 g (iki elde toplam ≤ 200 g), yalnız düz zeminde; rampada yüksüz. c (500 g) ancak`
     `K9 b ile (500 g'da S1 / S2 0,97, dirsek 0,74). Seçenek b metnine "her elde" eklenir. Alternatif: rampada kollar ev pozunda zorlanırsa ≤ 100 g (1,601; SO Ç7'ye bağlı).`

Büyük düzeltme yok; A'ya tur gerekmez. Koşullar uygulanmazsa paket yine de doğru sayı taşır, ama K3'e giden metin ve tilt kaynağı yanıltıcı kalır.

## Karar kuyruğuna aktarılacak metinler

- **K3 eki** (`F3a-gunluk.md` §4): **onaylı, koşul 4 ve 5 ile.** Tablo, kaynak anahtarlar, "bağlayan ölçüt servo", rampa ve HAT satırları birebir aktarılabilir.
  Kayıt ajanı ayrıca K3 "Seçenekler" b'yi "≤ 100 g her elde" yapar ve `Varsayılan:` satırını koşul 5'teki metinle değiştirir. İsteğe bağlı bir satır
  (öneririm): "İvme torkuyla (60° / 0,4 s) S1 payı 100 g'da ≈ 1,1, 200 g'da < 1 (B kaba tahmini, `F3a-kontrol.md`; taslak-170 kol ataleti)."
- **K9 güncellemesi** (`F3a-gunluk.md` §6): **onaylı, değişiklik yok.** K9 "Sayısal etki" maddesindeki "Bu sayılar 1,65 m modelinden; 1,58 m'de
  yeniden ölçülmedi (P3.2)." cümlesi §6'nın ilk maddesiyle, "b seçilse de 500 g ile rampa payı 1,327" → 1,329 ile değiştirilir; "b'nin servo
  gereksinimi" maddesi eklenir. Varsayılan a kalır.
- Pan / tilt için karar maddesi gerekmez: en düşük K2 a, kod sınırında tilt 3,27 ≥ 3,0, pan 2,16 ≥ 2,0 (ekstrapolasyon, hata < 0,01).

## F5 / Efe'ye iletilecek bilgi (güvenlik; karar değil, pano bilgisi)

- **Kodun tilt sınırı ±20 (70…110) güncel CAD'de çakışma bölgesinde:** `kafa-analiz.json` (05.11, QLED kafa) `tarama.ilk_carpan` +20'de yüz kabuğu
  (ön) sağ × rulman yuvası 327,4 mm³, −20'de arka kafa kabuğu sağ × rulman yuvası 654,9 mm³; serbest aralık ±15 (5° adım). CAD sınırı ±13.
  Pano #6 bu farkı "Tilt 70…110 (±20), CAD ±13" diye yazıyor ama **±20'de kabuğun rulman yuvasına çarptığını söylemiyor** (`F5-pano-govde.txt:6`).
  Orkestratör F5 hattına bilgi olarak eklemeli. Aynı aileden: omuz kod 160 ↔ CAD 135 (Ç2), dirsek kod 110 ↔ CAD 105, 110'da boşluk 1,6 mm, 115 çarpar
  (`arayuz.py:504`, Ç3). Tork açısından üçü de sorunsuz (F3a).
- Orkestratörün `dongu-158.md:162` günlük satırındaki "Tilt kod ±20 ilk temas +18/−17°" de koşul 2'ye göre "±20 güncel CAD'de çakışıyor (+18/−17 29.10 ölçümü)" olmalı.

## Kontrolün sınırı

- Devrilme ızgarası 15° adım ve bilek 0'da (UI ile aynı); daha sık ızgara payları yalnız düşürebilir. Rampa 50 g'daki 0,001'lik fark bu çözünürlüğün içinde.
- Kafa ataleti (`I_kgm2` 3 nokta) ve kablo kütleleri kaynak JSON'lardan; FreeCAD ile yeniden ölçülmedi. Kol ivme tablosu B'nin kaba tahminidir.
- Scratchpad: betik kopyası, çıktı ve koşu günlüğü `C:\Users\Victus\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad\f3a\`
  (depoya girmez).
