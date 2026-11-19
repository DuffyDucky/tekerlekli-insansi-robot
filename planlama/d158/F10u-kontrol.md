# F10u-kontrol: P10.7b2k bağımsız kontrolü (CAD'den bağımsız rehber uyumu)

Tarih 19.11.2026. Taban `lale-duzeltme` = `896c9a7` (uzak ile aynı), paket commit'siz: `git diff 896c9a7` (16 dosya) + `F10u-gunluk.md`.
Paralel CAD dalı `lale-cad-b2j` (`456b723`) yalnız okundu (dal nesneleri `git show` / `git archive`, worktree'deki izlenmeyen
`F10t-gunluk.md` dosyadan okundu); worktree'de komut koşulmadı. FreeCAD koşulmadı. Kaynaklara yazılmadı; tek yazılan bu dosya.

## Karar: DÜZELTMEYLE GEÇER

Birleştirme kendisi güvenli: iki dalın ortak dosyası 0, birleşik benzetimde `rehber_kablo.py` GEÇER, `rehber_denetim.py --kaynak`'ta
yalnız beklenen 3 terim kalıyor. Denetleyici değişikliklerinin hepsi bir metin / şema değişikliğine karşılık geliyor (bir istisna:
bulgu 5). Ama üretimden (rehber yeniden üretimi) önce kapanması gereken iki kare / metin çelişkisi (bulgu 1, 2) ve enerji sırasına
bağlanmamış bir güvenlik cümlesi (bulgu 3) var; push'tan önce b2j dalındaki takma ad (bulgu 9).

## Bulgular (önem sırasıyla)

### 1. YÜKSEK (üretimden önce): CAD kablo yolları yeni bara tutucularının ve saplamaların içinden geçiyor
- Yer: `taban/taban-analiz.json` `kablo_yolu` (b2j'de değişmedi) ↔ b2j tutucuları; rehber tarafında `rehber_kablo.py:178–185`
  (`MODELSIZ_KONUM`, Echo kararı 1: "CAD yolu sınaması eski vekilde kalır"), `rehber_metin.py:413` ("Karede iki bara tutucusu
  saplamaları ve somunlarıyla görünür").
- Ölçtüğüm (birleşik benzetim, merkez çizgisi ile parça kutusu arası; tüp yarıçapı 2,5 eklenmeden): yol 1 (G01–G04, ana + hattı)
  yıldız 3. saplamasından ve pulundan **0,0 mm**; yol 2 (G05) yıldız tutucusunun gövdesinden (nokta (30; 186; −60) tutucu kutusunun
  içinde) geçip tutucunun 24 mm arkasında (−20; 186; −90), iki bara arasında boşlukta bitiyor; yol 3 ve 5 yıldız tutucusundan 0,0;
  yol 7 1,0; yol 8 (G17) anahtarlı 1. ve yıldız 1. saplamasından 0,0 / 0,9; yol 9 (G18) yıldız 5. ve anahtarlı 4. saplamasından 0,0 / 0,6.
- Senaryo: K1 17.1 "Toprak ve iki bara" (desen "Kablo yolu 2:", yeni `odak` tutuculara) karesinde vurgulu toprak kablosu tutucunun
  içinden geçip boşlukta biter, uç etiketi "G05/−" ise tutucunun kutusunda; ana + hattı (yol 1) karede GND barasının 3. saplamasına
  saplanmış görünür. Önceki metin bunu "iki bara ve tutucuları modelde yok" diye açıklıyordu; yeni metin tersini söylüyor.
  `geometri_denetle` yalnız uçlara baktığı, kablo yolları da çakışma sayımına girmediği için hiçbir sınama yakalamıyor.
- Öneri: CAD yollarını (`taban_parcalar.py` YOL 1, 2, 3, 5, 7, 8, 9) tutucu saplamalarına taşımak. Ses kartı yaması zaten
  birleşmeden sonra tam çakışma taraması istiyor (F10u § 7.2.3); YOL taşıması aynı CAD turuna girerse ek tarama maliyeti yok, ayrı
  yapılırsa (`taban_parcalar.py` `KAYNAK_SABIT`'te) bir tam tarama daha gerekir: karar şimdi verilmeli. Taşınmayacaksa en azından
  bu yolları gösteren K1 alt adımlarının ("Toprak ve iki bara", "Ana hat ve şarj kolu", "Röle K1 ve ön şarj kartı") ve yol 5 / 7 /
  8 / 9'u gösteren K1 / K2 karelerinin metnine "CAD kablo yolları eski WAGO noktasında / röleden çizili; bara ucu
  tutucudadır" notu ve bu yolların bara çevresinde `CAD_KIRP` ile kırpılması, sonra kare bakışı.

### 2. ORTA (üretimden önce): "bara modelde yok" diyen iki cümle güncellenmemiş
- `rehber_metin.py:490–491` (K1 17.6, G22): "anahtarlı bara karede görünmez (modelde yok, güç panelinde)". Aynı karede G22 şeması artık
  anahtarlı baranın 4. saplamasından çiziliyor: metin ile kare çelişir.
- `rehber_metin.py:1130–1132` (F1 "İlk enerji, aşama 1" kontrolü): "yıldız barası güç panelinde (arka kat; bara modelde yok)".
- Daha hafif: `rehber_metin.py:460–461` "Karede Kablo yolu 3'ün baradan sol BTS7960B'ye giden kısmı" — yol 3 röleden çıkıyor, bara artık
  başka yerde görünür (bulgu 1 ile birlikte çözülür).
- Öneri: üç cümleyi tutucu modelde diye düzelt; F10l `B2K_*` listesi ve onay kaydı yenilenir.

### 3. ORTA (üretimden önce): bara somunlarını yeniden sıkma cümlesi enerji sırasına bağlı değil
- `rehber_metin.py:408–410`: "ilk enerjiden önce ve ilk haftanın sonunda yeniden sık". Cümle yalnız K1'de. Rehberde ilk enerji
  F1 "İlk enerji, aşama 1"dir (`rehber_metin.py:1110`; F4 ve F5 burada takılıyor), F5 aşama 2'dir. F10u "Güvenlik" bölümü (satır 102)
  sonraki paket için **F5**'i öneriyor: yanlış adım, F5 ilk enerjiden sonradır.
- "İlk haftanın sonunda" sıkma için koşul yok: ana anahtar kapalı, akü XT60'tan ayrık, takı çıkar (K1'in "akü ayrık" kuralı bu
  noktada geçerli değil; robot o zaman çalışır durumda). Lokma anahtarı anahtarlı bara (+) ile 60 mm arkadaki yıldız barası arasında
  köprü kurabilir. Panele kabuk / etek takılıyken üstten erişim de rehberde ölçülmemiş (F10t § 1.2 "her zaman erişilir" yalnız taban
  modeli için).
- Öneri: F1 aşama 1 kontrol listesinin başına "akü XT60 ayrıkken bara somunlarını yeniden sık" maddesi + ZORUNLU; K1 cümlesine
  "ilk hafta sonundaki sıkma da ana anahtar kapalı, akü XT60'tan ayrıkken" eklenmesi; erişim F-adımlarında doğrulanmadı diye etiket.

### 4. ORTA-DÜŞÜK: ESP32 ters takma cümlesi asıl sonucu söylemiyor
- `rehber_metin.py:303–305` (B6a): "ters takılırsa bütün pinler yer değiştirir ve ESP32 USB fişi (U06, K1) porta ulaşmaz". Yön
  doğru (`taban_lib.esp_local`: WROOM −x, port +x; `ESP_PORT` x 107 = DevKit kutusunun +x yüzü). Ama 30 pinli DevKit 180° dönünce
  taşıyıcının 5 V / GND hattı GPIO pinlerine gelir ve F1 aşama 1'de F4 (XL4016 çevre 5 V → ESP32) takılınca kart enerjilenir; hasar
  ilk enerjide olur. "Porta ulaşmaz" da garanti değil (kablo esnek, port −x'te de erişilebilir). F1 aşama 1 öncesinde yön denetimi yok.
- Öneri: "ters takılı kartla enerji verme: 5 V bir GPIO pinine gelir" ve F1 aşama 1 enerji öncesi listesine yön bakışı.

### 5. DÜŞÜK: gerekçesiz yer tutucu daraltması
- `rehber_metin.py:403`: `{bsaplama.G13|G16} G13 / G16` → `{bsaplama.G16} G13 / G16`. Günlükte yok, F10l listesinde yok (çıktı metni
  aynı olduğu için), onay kaydında bir fark olarak var. Eski hâliyle de bütün sınamalar geçiyor (benzetimde geri aldım: tek fark "onaylı
  kritik girdi farkı 1"). G13 saplaması değişirse "G13 / G16" yanlış numara basar. Öneri: geri al (onayı yeniden yenile) ya da gerekçele.

### 6. DÜŞÜK: G16 / G22 şemasının pabuç alanıyla ilişkisi
- `kablo_yolu_taban.py:389–394`. Modelli parçalara en yakın: başlangıç saplamasının somun / pul kutusuna 0,4 mm (beklenen, uç),
  yıldız saplamalarına ≥ 6 mm, tutucu üstüne 5,5 mm; U06'ya G16 16,9 mm, G22 59,6 mm (U06 kendi en alçak yeri y 205, x 40, z −30…37).
  Sorun yok. Ancak G22 z −95'te x 37,5 → −37,5 boyunca anahtarlı baranın dört saplamasının 15 mm önünden, y 195'te geçiyor: pabuçlar
  +z'ye bakarsa (şema "pabuç dili +z" varsayıyor) dilleri ve kovanları bu çizginin altında kalır (zarf ölçülmedi); karede G22 başka
  saplamalara değiyor gibi okunabilir. Öneri: köşeyi z −80'e almak (iki tutucu arası, ikisine de ≥ 14 mm).
- U06 notu (`rehber_metin.py:410–411`) G17 / G18'i anıyor, F10t § 1.3'ün saydığı G05'i (akü yarığından yıldız 3'e, şeridin x / z
  izdüşümünden geçer) anmıyor. "Bara kablolarını … yatay götür" genel cümlesi kapsıyor; "(G05, G17, G18)" daha açık olur.

### 7. DÜŞÜK: denetleyici sınırları
- `rehber_kablo.u06_port_denetle` portu kutunun +x yüzüne sabitliyor; DevKit CAD'de 180° dönerse kutu aynı kalır, sınama geçer
  (yön yalnız `esp_local`'da). Sınırlama olarak yorum satırına yazılmalı.
- `KALKAN_PARCA` için `rehber_denetim --bozma-denemesi`'nde bozma yok; elle denedim (eski `rehber-veri.json` ile: kart ve bandı
  "kalkan parça veride" olarak yakalandı). Bir bozma eklenmesi önerilir.

### 8. BİLGİ: USB ses kartı kararı ile metin uyumlu
- Karar (`kablolama-on-kararlar.md` § 5 Ö1, karar kuyruğu K16 notu, 14.11): kart kablajdan çıktı, yedek olarak siparişte, **robota
  takılmaz**; KT2 geçmezse Pi port 2'ye. E4 "takılmaz, çizimde de yok: kart yedek parçalarla birlikte saklanır" bununla birebir; kart
  yalnız çizimden değil robottan da çıkıyor. Ses yolu rehberde tam: ReSpeaker 3,5 mm → 10 kΩ / 2,2 kΩ bölücü → PAM8403 (AU1, AU2, E4),
  PAM 5 V → D24V50F5 (K05), PAM → hoparlör ("Hoparlor" şeması, K2), ReSpeaker → Pi USB 1 (U01). `kafa_rapor.py` ve `uygulama_*`
  aynı. Önceden de var olan boşluk: KT2 geçmezse kartla birlikte siparişten çıkarılan ~30 cm USB-A uzatma ve L dirsek de gerekir
  (`kablolama-on-kararlar.md` satır 202, 425); E4 bunu söylemiyor.
- `uygulama_metin.py`, `uygulama_olc` yeniden koşulana dek (D3) eski kart ölçüsünü basar; tarif bunu kapsıyor.

### 9. BİRLEŞME NOTU (b2k dışı, push'tan önce)
- `lale-cad-b2j`'deki `planlama/d158/F10s-gunluk.md` 2 yerde, worktree'deki izlenmeyen `F10t-gunluk.md:42` 1 yerde takma adı
  kullanıyor. `.git/hooks/pre-push` "takma ad" kalıbı birleşme sonrası push'u durdurur; F10u § 7.5 yalnız `robot-glb.js` uyarısını
  anıyor. Depoda proje sahibi "Ahmet", orkestratör "Echo" diye geçiyor (pre-push başlığı dahil); b2k bu düzene uyuyor ("Ahmet'e
  sorulacak", K64). Önerilen: b2j günlüklerinde aynı düzene çevrilmesi.
- b2k farkında ve `F10u-gunluk.md`'de yerel yol, anahtar, e-posta, ekip soyadı yok (pre-push kalıplarıyla tarandı).

### 10. Doğrulananlar (sorun yok)
- **Ortak dosya:** `8bca2f5..lale-cad-b2j` 75 dosya, `8bca2f5..896c9a7` + paket 339 dosya, kesişim 0; worktree'nin commit'siz
  `carpisma-bolum/statik.json`'u da ana dalda yok.
- **Ana ağaçtaki kırmızılar:** `rehber_kablo.py` 9 hata (bara_tutarlilik 1, G16 / G22 vekil + yan + baş ucu 6, uç etiketi 2), hepsi
  `Bara tutucusu` parçası / `TABAN["bara_tutucu"]` yokluğundan; benzetimde 0. `rehber_denetim --kaynak` 3 terim, hepsi kafa modelindeki
  kartın / bandının CAD adı ve kodu; benzetimde de 3 (yama + `kafa_montaj` ister). Başka kökenli hata yok.
- **K64 montajı:** B5a sırası (ısıl gömme → saplama alttan, somun elle → tutucu panele → M3 alttan), panel B5a'da tezgâhta ve B5'ten
  önce: F10t § 1.2 ile aynı. Model: cep alttan açık, saplama başı y 179,8 (panelden 0,3 mm), M3 × 10 başı y 172,8 → panel 5 + insert
  5,7 mm; yıldız z −66…−44 akü yarıklarının (z −37…−23) arkasında, anahtarlı z −126…−104 röle (z −155…−115) hizasında. Saplama
  numarası = x artan = önden bakınca soldan sağa (K65): CAD adları "(yildiz 1)" x −54…−46 … "(yildiz 5)" x 46…54. kablolar.json
  yerleşimi: G16 anahtarlı 2, G22 anahtarlı 4, G17 / G18 yıldız 4 (x 25), G05 yıldız 3 (x 0): metin ve şemalar tutuyor. Akü takılıyken
  gereken bir vida yok (M3'ler bir daha gerekmez, saplama değişimi panel sökümüyle, metin bunu söylüyor). Saplama başı panel
  kontrplak olduğu ve 0,3 mm aralık bulunduğu için yalıtım iddiası doğru.
- **`sema_boy`:** G16 160,2, G22 258,6 mm (elle hesap) = kayıt 160 / 259; `kablolar_denetim` GEÇER.
- **B6 / K53, E3a / K51, K2 notları** F10t § 1.4–1.6 ve b2j commit'leriyle aynı.
- **Onay kaydı:** 896c9a7 ↔ çalışma ağacı karşılaştırmasında (yer × metin satırı) 85 satır (günlüğün "62"si girdi sayımı; sayım
  biçimi farkı): CAD_KIRP 9 yazımı (D7), iki ses muafı, iki SEMA_KONUM / UC_ETIKET, iki UC_MODELSIZ, 7 TERIM_ISTISNA, 15 ZORUNLU,
  geri kalanı B5a / B6 / B6a / E3a / E4 / K1 / SEMA metinleri. Hepsi farktaki gerçek bir değişikliğe karşılık geliyor; gerekçesiz tek
  satır bulgu 5. Kaldırılan / yumuşatılan kurallar (BILESEN kartı, TERIM_ISTISNA ölü cümleleri, E4 / E3a / B5a ZORUNLU desenleri,
  SEMA_ESLEMESIZ_MUAF, b66'nın yeni anlamı, `sema_not_denetle`'nin iki bara muafiyeti, `sema_parcalari`'nın "Bara tutucusu" istisnası)
  her biri metnin / modelin değişmesine bağlı ve dar; yerine yeni kilitler (KALKAN_PARCA, 9 ZORUNLU, bara_tutarlilik, u06_port_denetle,
  kullanılmayan GEO_ISTISNA) geldi. Yumuşatma yok.

## Koşulan sınamalar (`PYTHONIOENCODING=utf-8`, `py -3 -B -X utf8`; `regresyon.py` koşulmadı)

| Sınama | Ana ağaç | Birleşik benzetim (depo dışı) |
|---|---|---|
| `rehber_kablo.py` | KALDI 9 (yukarıda) | GEÇER |
| `rehber_kablo.py --bozma-denemesi` | — | 103 / 103 (b66, b99–b103 kendi iletisiyle) |
| `rehber_denetim.py --kaynak` | çıkış 1, yalnız 3 terim; onay farkı 0, zorunlu eksik 0 | aynı 3 terim |
| `rehber_denetim.py --bozma-denemesi` | — | 305 / 305, bozulmamış kaynakta hata 0 |
| `rehber_denetim.py rehber/veri/rehber-veri.json` (eski veri) | — | KALKAN_PARCA kartı ve bandı yakaladı |
| `F10l-birlesim.py` | GECER (eklenen 30 / 30, silinen 20 / 20) | — |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / GEÇER (174) | — |

Benzetim: karalama klasöründe `git archive lale-cad-b2j` + `8bca2f5..896c9a7` dosyaları `git archive 896c9a7`'den + paketin 16
dosyası ve günlük. Yama uygulanmadı.

Kendi bozmalarım (benzetimde, her biri geri alındı): (a) E4'e "USB ses kartını PAM8403'ün yanına köpük bantla yapıştır" →
`--kaynak` terim kuralı yakaladı; (b) kablolar.json'da G22'yi anahtarlı 4 → 3 → `bara_tutarlilik` yakaladı; (c) `ESP_PORT`'u
DevKit'in −x yüzüne (x 54) taşıdım, şema da birlikte kaydı → `u06_port_denetle` + `sema_boy` yakaladı; (d) kullanılmayan
`GEO_ISTISNA[5]` → "kullanılmıyor" + onay farkı yakaladı; (e) `{bsaplama.G13|G16}`'yı geri koydum → yalnız onay farkı (bulgu 5).
Ana ağacın `git status`'u koşulardan önce ve sonra aynı (md5 karşılaştırması); bu dosya dışında yazılan yok.

## Bakamadıklarım

- Üretilmiş kareler (17.1, 17.6, B5a, B6, E3a, E4 31.3–31.4): FreeCAD / rehber üretimi istiyor; bulgu 1 ve 6 koordinat hesabıyla.
- Yama sonrası `kafa_montaj` / BOM / parça sayısı (1238), seçicinin tutucu takımını B5a'ya düşürmesi, `odak` boş desen uyarısı.
- Pabuç zarfı, kablo bükülme yarıçapı, PETG sünmesi ve tork değeri (kaynakta ölçüm yok).
- Güç paneline kabuk / etek takılıyken üstten erişim (bulgu 3).
- F10t henüz "SÜRÜYOR": b2j'deki tutucu ölçüleri değişirse `bara_tutarlilik` yakalar (F10u § 7.6).

---

## Tur 1 kontrolü (düzeltme turu 1, F10u-gunluk § 8–9)

Yalnız bu turun farkı okundu (önceki onayın satır listesiyle karşılaştırılarak). Benzetim iki CAD ucunda kuruldu (depo dışı, sonra
silindi): `d8f9c41` (uygulama ajanının benzetimi) ve **`b308728`** (dalın şimdiki ucu: "CAD kablo yolları bara tutucusu
saplamalarına taşındı", F10v). İki uçta da ana dal + paketle ortak dosya 0. Worktree'de commit'siz `kafa10_lib.py` ve `F10s-gunluk.md`
değişikliği var (CAD ajanı çalışıyor); okunmadı, benzetime girmedi.

### Karar: DÜZELTMEYLE GEÇER

Önceki bulguların hepsi işlenmiş; güvenlik metinleri adım sırasıyla tutarlı. Kalan tek zorunlu iş: CAD yolları taşınmış uçla
(b308728) birleşince `rehber_kablo.py` GEÇMİYOR (T1), tarif bunu söylemiyor.

### Kalan bulgular

**T1. ORTA, birleşmeden hemen sonra / üretimden önce şart: `CAD_KIRP[9]` CAD tarafındaki yol 9 değişikliğine uyarlanmamış.**
`b308728` benzetiminde `rehber_kablo.py` KALDI (4): "yol 9 G18 b yanı (XL4016 çevre) yola ulaşmıyor", "yol 9 son ucu
(25; 197; −130) … eşlenen kabloların ucu değil", "bara yolu: yol 9 yıldız barasının 4. saplamasına ulaşmıyor", onaylı tablo farkı
CAD_KIRP 9. Neden: yol 9 artık 16 nokta (yıldız 4 → XL4016 çevre (49,2; 125; 75) noktalar[12]), rehber hâlâ `son=3` tutuyor. CAD
commit'i bunu söylüyor ("CAD_KIRP[9] son 3 -> 12, kesim 143,92 aynı"; `F10v-yol-bosluk.py` `KIRP = {9: 12, …}`), ama
`rehber_kablo.py` ana dalda. Benzetimde yalnız `son=12` yapınca kalan tek satır onay farkı. Gerekli: `CAD_KIRP[9]` `son` 12,
gerekçe metnindeki "noktalar[4..]" / "noktalar[3]" → "[13..]" / "[12]", onay yenileme, F10u § 7.1'deki "SONUÇ GEÇER" ölçütüne bu
ön adımın eklenmesi.

**T2. DÜŞÜK-ORTA: `bara_yol_denetle` izin bölgesi aşağı doğru açık.** Kural (`rehber_kablo.py:1226–1229`): kendi saplama ekseninin
yatayda ≤ 12 mm'sinde ve **y ≥ 175** olan nokta hiçbir kutuyla sınanmaz. Komşu saplama aralığı 25 mm, yabancı takım kutusu + tüp
yarıçapı eksenden 7,1 mm'ye uzanıyor; 12 mm izin komşuya taşmıyor, yani yatayda gevşek değil. Ama y ≥ 175 tutucu gövdesini
(179,5…189,5), saplama başını ve paneli (174,5…179,5) de kapsıyor. Benzetimde üç kaçak denedim, üçü de TEMİZ geçti: yol 2'nin sonu
tutucu gövdesine dikey (0; 182; −50); gövde içinde y 185'te saplama 3 ekseni boyunca; panelin altından (0; 176; −55). Bozma "tutucu
gövdesinden (y 185)" yalnız izin bölgesinin dışında kalan ucu (z −42,4) yakaladığı için geçiyor. Öneri: koşulu `q[1] >= 189.5`
(tutucu üstü, pabuç yığını) yapmak. Benzetimde denedim: taşınmış yollar ve bozmanın doğru yolu temiz kalıyor, üç kaçak yakalanıyor
(2 / 2 / 1 hata). Bozmaya bir "dikey, kendi saplamasında gövdeye" satırı eklenmeli.

**T3. DÜŞÜK (kare bakışında): G16 / G22 şemaları taşınmış CAD yollarıyla üst üste.** b308728'de bara üstü hat y 197'de, iki saplama
ortasında; şemalar y 195'te aynı şeritlerde. Şema merkezi ile CAD tüpü merkezi arası: G16 × yol 4 0,2, × yol 8 0,7, × yol 3 1,1 mm;
G22 × yol 9 1,3, × yol 3 / 4 / 5 / 7 / 8 2,0 mm (tüp yarıçapı 2,5). Karede G22, 12 AWG demetin içinde çizilir. Gerçek kablolar da
aynı koridordan geçtiği için yanlış değil; 17.x kare bakışında okunabilirliğe bakılmalı. Modelli parçalara en yakın uzaklık değişmedi
(başlangıç somununa 0,4 mm); G22 boyu 258,5 mm (kayıt 258).

**T4. DÜŞÜK: "anahtar" iki anlamda.** F1 maddesi (`rehber_metin.py:1129–1131`) ve K1 cümlesi aynı cümlede "ana anahtar kapalı" ve
"anahtar iki baraya birden değmesin" diyor; ikincisi lokma anahtarı. "Lokma / alet bir baradan öbürüne değmesin" daha açık.

**T5. DÜŞÜK: F1'deki ESP32 yön bakışı için erişim çekincesi yok.** Bara sıkma maddesinde "kabuk ve etek takılıyken erişim ölçülmedi"
var, yön bakışında yok. ESP32'nin F1'de üstten görünüp görünmediği ölçülmedi. Asıl denetim olarak B6a kontrol satırı kalıyor.

### Doğrulananlar

- **Bulgu 1:** `bara_yol_hedefleri` hedefleri `CAD_ESLEME` × kablolar.json bara-pabuc `yerlesim`'den okuyor (rehber metnindeki
  numaralarla aynı kayıt). § 8 tablosu kayıtla ve modelle tutuyor: yol 2 G05 yıldız 3; yol 3 G12 anahtarlı 1 / yıldız 1, G09 / G11
  anahtarlı 3; yol 4 G13 anahtarlı 2 / yıldız 2; yol 5 / 7 G14 / G15 anahtarlı 1 / yıldız 1; yol 8 / 9 yıldız 4; eksenler
  `arayuz.TABAN["bara_tutucu"]` ile aynı. b308728'de yol uçları bu saplamalarda (y 194, eksenden 10 mm). Saplama başına pabuç
  (kayıt + köprü uçları): yıldız 4 / 4 / 4 / 4 / 3, anahtarlı 4 / 4 / 4 / 2; sınır (4) aşılmıyor. Beş diferansiyel bozma gerçekten
  koşuyor: iki benzetimde de 5 / 5 kendi iletisiyle, toplam **108 / 108**; ana ağaçta "tutucu yok, atlandı" (103).
- **27 / 35 hata:** ana ağacın 27'si tutucu yokluğundan (vekil, uç etiketi, `bara_tutarlilik`, "bara yolu: tutucu yok") ve eski
  CAD yollarından (yol 2 / 3 / 4 / 5 / 7 uç ve yan satırları). d8f9c41 benzetimindeki 35'in hepsi eski CAD yolları (9 geometri +
  26 bara yolu). Başka kökenli kalem yok. b308728'de 4 (T1).
- **Güvenlik metinleri (bulgu 3, 4):** F1'deki iki yeni madde "İlk enerji, aşama 1"in önünde. İkisi de akü ayrık ve ana anahtar
  kapalıyken yapılabilen işler (sıkma, göz). F4'ün aşama 1'de takıldığı ve ESP32'yi beslediği doğru. K1 cümlesi F1'e bağlı; ilk hafta
  sonu koşulu ve erişim çekincesi yazılı; B6a'da "porta ulaşmaz" kalktı. Sıra hatası ya da akü ayrıkken yapılamayan bir kontrol yok.
- **Bulgu 2:** 17.4 / 17.6 / F1 cümleleri düzeldi. `YASAK` "bara modelde yok" kalıbı ";"de durduğu için 17.1'deki "pabuçlar ve
  köprüler modelde yok" ifadesine takılmıyor. Bozmalar (17.6 / F1 eski metni yakalanır) geçiyor.
- **Bulgu 5, 6, 8, 9:** `{bsaplama.G13|G16}` geri döndü. G22 z −80. `kalkan_parca_bozma_denemesi` 3 satır (temel 0, kart yakalanır,
  ReSpeaker yakalanmaz). E4 eki `kablolama-on-kararlar.md` satır 202 / 425 ile aynı. `u06_port_denetle` sınırı docstring'de.
- **Onay kaydı:** önceki turun satır listesine göre 32 eklenen / 6 çıkan satır (günlüğün "29"u girdi sayımı). Hepsi bu turun
  değişikliği: MODELSIZ_KONUM iki bara (Karar 1 geri alındı), YASAK 1, ZORUNLU 10 (K1 ×5, F1 ×3, B6a ×1, E4 ×1; eski K1 sıkma deseni
  çıktı), K1 17.1 / 17.4 / 17.6, F1, B6a, E4 metinleri, G13|G16 geri dönüşü. Fazla ya da açıklanmayan satır yok.
- **ASCII 6 kelime** (`ikisinde biter saplamadan tutucusuyla kartla sorulacak`): hepsi yeni metinlerde geçen, Türkçe harfi olmayan
  doğru yazım; gerekçe yorumu var (`rehber_denetim.py:66`).
- **Tarif:** `--squash` ara commit'leri taşımıyor. Takma ad eklenmiş satır olarak yalnız `7d3f7f1` ve `3c20e11`'de var (birer satır).
  `896c9a7..lale-cad-b2j` farkında kancanın "takma ad" ve "yerel yol" kalıplarına uyan eklenmiş satır 0. Dal ucundaki `git grep`
  eşleşmeleri (`CLAUDE.md`, `index.html`, `eklem_sinirlari.json`) ana dalda zaten bulunan, kancanın taramadığı eski satırlar. b2k
  farkında ve iki F10u dosyasında 0. Kalıbı kancadan okuyan `sed` komutu doğru ifadeyi çıkarıyor; kuru koşu komutu kancanın stdin
  biçimine uygun. Uygulanabilir.

### Sınamalar (bu tur; `PYTHONIOENCODING=utf-8`, `regresyon.py` koşulmadı)

| Sınama | Ana ağaç | Benzetim d8f9c41 | Benzetim b308728 |
|---|---|---|---|
| `rehber_kablo.py` | KALDI 27 | KALDI 35 | KALDI 4 (T1); `CAD_KIRP[9] son=12` ile 1 (yalnız onay) |
| `rehber_kablo.py --bozma-denemesi` | — | 108 / 108 | 108 / 108 |
| `rehber_denetim.py --kaynak` | 3 terim; onay 0, zorunlu 0, yasak 0 | — | — |
| `rehber_denetim.py --bozma-denemesi` | — | 311 / 311 | — |
| `F10l-birlesim.py` / `kablolar_denetim.py` (+ bozma) | GECER / GEÇER / GEÇER | — | — |
| Kendi denemelerim (`bara_yol_denetle`) | — | — | 3 kaçak TEMİZ geçti; `y ≥ 189.5` ile 3 / 3 yakalandı, gerçek yollar temiz (T2) |

Ana ağacın `git status`'u koşulardan önce ve sonra aynı; benzetimler silindi.

Ek (kontrol sürerken dal ilerledi, `06b2ed9`: ses kartı yaması uygulandı, kafa yeniden üretildi): aynı benzetimde ortak dosya 0;
`rehber_kablo.py` yine 4 (T1, aynı satırlar); `rehber_denetim --kaynak` yine 3 terim. Terimler `montaj/montaj-analiz.json`'dan
okunuyor (`rehber_denetim.cad_ad_metinleri`), dalda ana montaj henüz yeniden koşulmadı: beklenen, tarif § 7.2.2 kapsıyor.

### CAD yolları taşındıktan sonra kapanış ajanının mutlaka koşacakları

1. `CAD_KIRP[9]` (T1) ve önerilirse T2 düzeltmesinden sonra, birleşik ağaçta `rehber_kablo.py` → **GEÇER** (bara yolu 0, yol 9
   uçları 0); `rehber_kablo.py --bozma-denemesi` → 108 / 108 (beş bara yolu bozması "atlandı" demeden, kendi iletisiyle; T2
   yapıldıysa 109). Onay yenilemesi bağımsız kontrolden geçer.
2. `rehber_denetim.py --kaynak` (3 terim yalnız yama + `kafa_montaj` öncesi), `--bozma-denemesi` 311 / 311; `F10l-birlesim.py`,
   `kablolar_denetim.py` (+ bozma).
3. `planlama/d158/F10v-yol-bosluk.py` (CAD tarafının gerçek geometri boşluğu) ve `taban_montaj` iç çakışma 0, tutucu × yol teması.
4. Üretimden sonra: `rehber_kablo.py --veri rehber/veri/rehber-veri.json` GEÇER, `rehber_denetim.py` (veri) zorunlu eksik 0,
   `KALKAN_PARCA` 0. Kare bakışı: 17.1 (yol 2 yıldız 3'te biter), 17.4 (yol 3 anahtarlı 3 / 1, yıldız 1), 17.6 (G22 anahtarlı 4'ten),
   K2 32.1 (yol 5 / 7 anahtarlı 1'den), şema / CAD tüpü üst üste binmesi (T3).

---

## Tur 2 kontrolü ve yol doğrulaması (F10u-gunluk § 10; CAD dalı `06b2ed9` dizinde, F10w)

Sınamalar ana ağaçta, birleşik gerçek modelle koşuldu. Tam çakışma taraması (F10x) sürerken FreeCAD koşulmadı. İzlenen dosyalara ve
dizine yazılmadı. Kendi bozma denemelerim yalnız bellekte yapıldı (`RK.BARA_IZIN_Y` modül içinde değiştirildi, kaynak dosyalara
dokunulmadı). Yol doğrulaması `taban/taban-analiz.json` nokta ve kutu verisiyle, FreeCAD'siz kendi hesabımla yapıldı.

### Karar: GEÇER

Tur 1 bulgularının hepsi doğru işlenmiş. Üretimden önce şart olan bir bulgu yok. Aşağıdakiler düşük önemli; kapanışta ya da kuyrukta
ele alınabilir.

### Tur 2 farkı

- **T1:** Hesabı kendim yaptım. Yol 9 16 nokta; normal (0; 1; 1)/√2 üzerindeki izdüşümler: korunan [0..12] 8,84 … 141,42 (en büyüğü
  [12], XL4016 çevre (49,2; 125; 75)); atılan [13..15] 212,13 / 243,95 / 194,45. Kesim 141,42 + 2,5 = 143,92; atılan bölümün en
  küçük değeriyle arasında 50,5 mm pay, kalıntı yok. Kırpılmış yol yıldız 4'e uğruyor ([5] (25; 194; −65), eksenden 10 mm) ve
  XL4016'da bitiyor. Onay farkı yalnız CAD_KIRP 9.
  Kalan küçük iş: `rehber_kablo.py:228–232`'deki açıklama yorumu hâlâ eski indisleri yazıyor ("noktalar[0..3]", "[4..6]", korunan
  y 125…215,5; yeni değer 125…219). Sayılar (141,42 / 194,45) doğru. Ayrıca F10u-gunluk § 8 satır 258 hâlâ "y ≥ 175" diyor.
- **T2:** `BARA_IZIN_Y = 189,5`.
  - Ayrımı kendim denedim: bellekte eski 175 değerine dönünce üç yeni bozma 0 hata veriyor (kaçak), 189,5 ile 2 / 2 / 2.
  - Ana ağaçta sekiz bara yolu bozması gerçekten koşuyor, "atlandı" yok; toplam **111 / 111**.
  - Gerçek yollarda bara yolu hatası 0.
- **T4 / T5:** Yeni metinler yerinde: "lokma anahtarı" K1'de ve F1'de; F1'deki ESP32 erişim çekincesi.
- **17.7 cümlesi:** Yer tutucu "4 numaralı" diye çözülüyor (kablolar.json yıldız yerleşimi `"4": ["G17/−", "G18/−"]`). CAD'de yol 9
  gerçekten yıldız 4'e gidiyor (yatayda tam 10 mm).
- **E3a:** D24V50F5 notu Pololu sayfasıyla tutarlı. Sayfa 5 pini (EN, VIN, 2 × GND, VOUT) ve 0,1" aralığı yazıyor; fiziksel sırayı
  metinde vermiyor, "PCB üstünde yazılı" diyor. Bu yüzden "kart yazısıyla doğrula" doğru. Küçük not: "+z'ye" rehberdeki tek eksen adı;
  montajcı için "TVS'ye bakacak" tek başına yeter.
- **ZORUNLU kilitleri ve onay:** 6 yeni ZORUNLU deseni var: E3a ×1, F1 ×2, K1 ×2, K1 17.7 ×1. Tur 1'e göre onay kaydına 12 satır
  eklendi, 5 satır çıktı. Hepsi bu turun değişikliği: CAD_KIRP 9, yukarıdaki desenler, K1 17.1 / 17.7, F1 ve E3a metinleri. Yeni
  ASCII kelimesi "bakacak" doğru yazım. Yer tutucuların hepsi çözülüyor (`COZUM_HATA` boş).

### CAD kablo yollarının bağımsız doğrulaması (yollar 1–5, 7–9; nokta ve kutu düzeyinde, tüp r 2,5)

| İddia (F10v § 1) | Sonuç |
|---|---|
| Atamalar F10u § 8 ile birebir | **Tutuyor.** Saplama ziyaretleri (eksenden ≤ 12 mm, y ≥ 189,5) kablolar.json hedefleriyle aynı. Tek fazla ziyaret yol 3 × anahtarlı 2: yolun anahtarlı 3 → 2 → 1 parçası köprüleri gösteriyor ve köprü uçları zaten o saplamada. |
| Bara ucu eksenden 10 mm, y 194 | **Tutuyor.** 13 bara ucunun hepsi tam 10,0 mm ve y 194 (yıldız uçları z −45, yalnız yol 9 z −65; anahtarlı uçları z −105). |
| Yatay hat y 197, saplamaların ortasından geçiyor | **Tutuyor** (yol 2 y 194'te kendi ucuna iniyor, yol 1 y 199). Bara üstünde yabancı saplamaya en dar yatay uzaklık 12,5 mm; tek istisna yukarıdaki köprü. |
| Yabancı saplama / tutucuya en dar 5,0 (yol 8, 9) ve 6,1 (yol 3, 5, 7) | **Yol 8 / 9 tutuyor** (anahtarlı tutucuya 5,0; yol 8 için yıldız 3 takımına kutu düzeyinde 5,1). **Yol 5 / 7 tutuyor** (yıldız 2 somununa 6,1). Yol 3 için köprüyü yabancı saymazsak 6,1. Tablodaki küçük yanlış: yol 4 "> 15" değil; yıldız 3 civata / somununa **6,0 / 6,1** (yine eşiğin üstünde). |
| Başka parçaya en dar 0,89 (yol 4 × akü kayışı) | **Kutu düzeyinde aynı çıkıyor** (kayış z −80 kutusuna 0,89). Yol plakanın altında y 85,5…88'de, kayışın plakanın altından dönen kısmının (y 90) hemen altından geçiyor. Gerçek bir temas riski değil: kayış yumuşak, kabloyu sıkıştıracak bir parça yok. Tek dikkat noktası kablo bağlanırken: kayışla plaka arasına girerse kayış gerginliği kabloyu ezer. |
| U06 şeridine (x 14…40, z −40…−30, y ≥ 205) giren yol yok | **Tutuyor** (tüp payıyla, hiçbir yolda nokta yok). |
| Yol 3 / 4 ön plaka deliği, yol 4 × XL4016 çevre, yol 7 × BTS7960 sol temasları giderildi | **Tutuyor.** Delikler: `arayuz.motor_kablo_delik` (±80; 200) / (80; 36), çap 16. Tüp deliğin kenarına 5,1 ve 3,9 mm uzakta. Plaka altındaki çıkış y 87 (tüp üstü 89,5 < 91,5). XL4016 çevre: önceki uçta tüp içindeydi, şimdi 2,76 mm. BTS sol: 0,85 mm içerideydi, şimdi 5,28 mm. |
| Yol 12 değişmedi | **Tutuyor** (yol 10, 11, 12'nin noktaları önceki analizle aynı). |
| Gerçek geometriyle boşluk değerleri (4,5 / 2,26 / 2,5 vb.; panel yarığı, plaka deliği kenarı) | **Bakılamadı** (FreeCAD `distToShape` ister; kutu değerleri delik içinden geçen yolda anlamsız). |

**Fiziksel takılabilirlik:** Takılamayacak ya da pabucu dönemeyecek bir uç yok. Bütün uçlar tutucunun üstünde, kendi saplamasının
yanında. Bir uyarı: yıldız 1 (G12−, G14−, G15−) ve anahtarlı 1'de (G12+, G14+, G15+) üç kablo aynı noktaya aynı yönden geliyor.
Üç 12 AWG pabucun boğumu aynı yöne bakarsa üst üste düz oturmaz; pabuçlar yelpaze gibi açılmalı. Rehberde bunu söyleyen bir talimat
yok (yalnız "kalın pabuç altta"). Pabuç ve köprüler modelde yok. Bu yüzden y 197'deki yatay hattın köprülerin (y ≈ 191–196) üstünden
geçtiği ve 4 pabuçlu yığının somunu ≈ 4–5 mm yükselttiği hesaba girmiyor. Bunlar da bakılamayanlara giriyor; civata y 208,3'e kadar
uzandığı için diş boyu yetiyor.

**"Dokunulmadı" denen eski kusurlar:**
- **Yol 10 × ön şarj kartı (0,1 mm):** Talimat doğurmuyor. Karede çizgi kartın üstüne değer gibi görünüyor, zararsız.
- **Yol 11 (Q03) ve kırpılmış yol 12 (B01):** 17.10 karesinde elektronik katını **ön kat kesiğinin dışından** deliyor (yol 11
  (−93,6; 177; 132), yol 12 (32,4; 177; 112); kesik x −60…60, z 150…175). Aynı karedeki kardeş şemalar (B02, N01, N02, Q01, Q02)
  açıkça "→ ön kat kesiği →" diyor; Q03 ve B01'in etiketinde (`KABLO_AD` 11 / 12) geçiş yeri yok. Yanlış bir talimat değil, ama
  yanıltıcı bir kare: montajcı katta delik varmış gibi görebilir. Öneri: iki etikete "ön kat kesiğinden" ve "CAD çizgisi katı
  temsilî olarak keser" notu eklenmesi (metin değişir, onay yenilenir).
- **Yol 12'nin ESP32 taşıyıcısının burç / vidasına girmesi:** Yol taşıyıcının merkezinde bitiyor, kare yalnız uç yerini gösteriyor.
  Talimat etkilenmiyor.

### Paket bütünü

- **Dizin:** 80 dosya. Liste `8bca2f5..06b2ed9` ile birebir, her blob `06b2ed9`'dakiyle aynı. b2k dosyası dizinde **yok**: iki
  commit'e ayrılabilir. 1. commit dizinin olduğu hâli (CAD); 2. commit b2k kaynakları, yeniden üretilmiş 61 MM çıktı ve F10u / F10w /
  F10x günlükleri. İkinci commit'te `git add -A` kullanılmamalı, yoksa 19 eski kir dosyası da girer. `git add` dizine yazdığı için
  taramanın bitmesi beklenmeli.
- **Çalışma ağacı:**
  - 61 MM dosya: yeniden üretilmiş montaj ve görseller, baskı ve F4c listeleri.
  - 11 "M " dosya: dal kaynakları, çalışma ağacı dizinle aynı.
  - 8 A dosya: dal günlükleri.
  - 16 yalnız-çalışma-ağacı değişikliği: b2k kaynakları (rehber ×5, kablolar ×2, F10l, karar-kuyrugu, `kablo_yolu_*`, `uygulama_*`,
    `kafa_rapor`) ve `lale158-kontrol.json` (F10x adım 0).
  - 9 izlenmeyen dosya.
  - 19 eski kir (14 M + 5 ??) olduğu gibi; F10w § 6 ile uyumlu.
- **Gizlilik:** Gidecek farkı kancanın bütün kalıplarıyla taradım: `git diff 896c9a7` eklenen satırları (FCStd / STEP / PNG / BREP
  ve 19 kir hariç, 21.964 satır) ve dört izlenmeyen F10 günlüğü. Anahtar, e-posta, IBAN / telefon, yerel yol, takma ad, ekip adı:
  hepsi **0**.

### Sınamalar (ana ağaç, birleşik model; `git status` md5'i koşulardan önce ve sonra aynı)

| Sınama | Sonuç |
|---|---|
| `rehber_kablo.py` | **SONUÇ GEÇER** |
| `rehber_kablo.py --bozma-denemesi` | **111 / 111** (8 bara yolu satırı kendi iletisiyle) |
| `rehber_denetim.py --kaynak` | çıkış 0: elektrik 0, zorunlu eksik 0, yasak 0, onay farkı 0, çözülemeyen yer tutucu 0 |
| `rehber_denetim.py --bozma-denemesi` | 311 / 311 |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / GEÇER |
| `F10l-birlesim.py` | GECER |
| Bellekte T2 ayrımı (175 ↔ 189,5) | 0 / 0 / 0 ↔ 2 / 2 / 2 |

### Kapanış ajanının üretimden sonra karede bakması gerekenler

1. **17.1:** Yol 2 yıldız 3'te, tutucunun üstünde biter.
2. **17.4:** Yol 3 anahtarlı 3 → 2 → 1 → yıldız 1, yol 4'ün dalı anahtarlı 2'den.
3. **17.6:** G22 şeması anahtarlı 4'ten, z −80.
4. **17.7:** Yol 9 F4 → yıldız 4 → XL4016'da biter; eski ESP32 kolu ve kesim kalıntısı görünmez.
5. **K2 32.1:** Yol 5 / 7 anahtarlı 1'den başlar.
6. **17.10:** Yol 11 / 12'nin katı kesik dışından deldiği görüntü; etiket notu eklenmediyse not düşülmeli.
7. **Şema / tüp üst üste binmesi (T3):** G16, G22 ve y 197 hattı.
8. **Veri modu:** `rehber_kablo.py --veri` GEÇER, `rehber_denetim` veri modu zorunlu eksik 0 ve `KALKAN_PARCA` 0.
