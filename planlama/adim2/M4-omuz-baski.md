# M4: Omuz baskı analizi (düzeltme planı 2. adım)

Ajan: analiz ve bağımsız kontrol (geometri değiştirmez). Başlangıç: 14 Ekim 2026.
Yazılan dosyalar: `tasarim/freecad/omuz/omuz_baski.py`, `tasarim/freecad/omuz/omuz-baski.json`, bu günlük.

## İlerleme
- [x] Günlük açıldı
- [x] Kaynaklar okundu (README, duzeltme-plani M4, baski-listesi, omuz betikleri)
- [x] Betik yazıldı (`tasarim/freecad/omuz/omuz_baski.py`, ilk koşu başladı)
- [x] Betik koşuldu, JSON üretildi (4 koşu; son koşu 268 s)
- [x] Sonuç tablosu ve öneriler

## Notlar (okuma)
- Omuzun baskı parçaları 5 tür × 2 (sağ + sol, sol = X aynası) = 10 adet: Omuz yuvası, Rulman kapağı, Omuz göbeği, Kol çatalı
  (PETG-CF) ve Üst kol tüpü (beyaz PETG). `omuz-montaj.FCStd` içinde `Tur == "Baski"` olan 5 Part::Feature; hepsinin
  `Malzeme` alanı hâlâ "PETG" (baskı listesi 4'ünü PETG-CF sayıyor).
- `omuz-analiz.json` `baski` alanında yön, çıkıntı, destek, süre yok; yalnız `sigar` (≤ 230 mm) ve kütle var.
  Kütle `omuz_parcalar.RHO["PETG"] = 1,27 × 0,6` (%60 doluluk) ile; M4 0,8–0,9 istiyor.
- Diğer modüllerin yöntemi (`kafa_lib.baski_analiz`): 1 mm katman dilimleri, önceki katmanın 1 mm ofseti (45°),
  2 mm'den dar şerit serbest, 15 mm'den uzun desteksiz bölge = destek. Bu betik aynı kuralları 0,5 mm katmanla
  uygular ve bölgeyi köprü / konsol / ada diye ayırıp açıklığı ölçer.
- Girdi: `omuz-montaj.FCStd` (diğer ajan yeniden üretebilir; betik dosyanın 5 s durgun olmasını bekleyip geçici kopyadan açar,
  zaman damgası ve sha256 JSON'a yazılır). İlk okumada FCStd 14.10.2026 15:48:40.

## Yöntem (`omuz_baski.py`)
- **Girdi:** `omuz/omuz-montaj.FCStd` içindeki `Tur == "Baski"` parçaları. Betik dosya son 5 s içinde yazıldıysa bekler,
  geçici kopyadan açar, zip bütünlüğünü denetler; JSON'a dosya, değiştirilme zamanı, sha256 yazılır. `omuz_parcalar.py`
  FCStd'den yeniyse uyarı düşer. `OMUZ_BASKI_KAYNAK=parcalar` ile doğrudan parça betiğinden okur. Omuz yeniden üretilmez.
- **Bu koşunun girdisi:** `omuz-montaj.FCStd`, 14.10.2026 15:48:40, 175.187 bayt, sha256 `bc6e54004f81ae08`
  (`omuz_parcalar.py` 14:59:48, yani FCStd güncel).
- Her parça 6 eksen yönünde (±X, ±Y, ±Z yukarı) denenir:
  - tablaya sığma (Z etrafında en dar kutu, X2D 246 × 246 × 250) ve iki adedin yan yana sığması,
  - ilk katman alanı (z = 0,1 kesiti) ve yükseklik / √taban oranı,
  - 45° üstü çıkıntı alanı (mesh) ve yatay tavan alanı,
  - **katman analizi:** 0,5 mm kesitler, önceki katman 0,5 mm ofsetle (45°) destek sayılır, 2 mm'den dar şerit serbest. Kalan her bölgenin
    tutunma kenarı bulunur, içinden nokta örneklenir: iki karşı kenardan tutunan **köprü** (açıklık = karşı tutunmalar arası),
    tek kenardan **konsol** (boy = tutunmaya uzaklık), altında hiç malzeme olmayan **ada**. Destek gerekir: ada, konsol > 1 mm ya da
    köprü > 15 mm. Destek kolonunun boyu ve tablaya mı parçaya mı bastığı ölçülür (destek hacmi = alan × kolon, tahmini).
  - **eğimli yüzler:** sürekli dik eğim her katmanda dar şerit ürettiği için katman analizinden kaçar; yüz yüz 45° üstü eğim alanı
    ayrıca ölçülür. Yatay eksenli Ø10'a kadar delikler serbest (yaygın uygulama, tahmini).
  - **yük eksenleri:** rulman yuvası / mili, horn delikleri, servo kulak delikleri, ısıl gömme somunlar geometriden (silindir yarıçapı)
    bulunur. Ağırlıklı "yük uyumu" hesaplanır: horn ve rulman ekseni tablaya dik olmalı (katmanlar yükü kesmez, delik yuvarlak basılır),
    yuva manşonunun eğilme ekseni yatay olmalı. Isıl gömme deliklerinin yönü ve ağız tarafı da yazılır.
  - Seçim sırası: sığma > yük uyumu > destek alanı > çıkıntı > ilk katman. En az destekli yön ayrıca yazılır.
- **Kütle / süre:** ρ 1,27 g/cm³ (PETG-CF 1,25–1,30, tahmini), etkin doluluk 0,8 / 0,9 (PETG tüp 0,8); filament = kütle × 1,05 + destek
  (%15 dolu destek, tahmini). Süre 10 mm³/s ile (diğer modüllerle aynı, tahmini); PETG-CF için ayrıca 7 mm³/s yavaş senaryo.
- Elle doğrulama: yuva servo penceresi 21 mm → ölçülen köprü 20,0 (21 − 2 × 0,5 pay). Göbek penceresi 41 → 40,0. Göbek plakası köşesi
  (42; −27) için beklenen konsol ≈ 26,9 → ölçülen 26,5. Çatal alt kulağı duvardan 44 mm → 42,9. Rulman kapağı +X ve tüp ±Y tamamen temiz.
- Koşu sırasında iki hata düzeltildi. `makeOffset2D` döndürülmüş kesitte ofseti ters yöne veriyordu (artık iki işaret denenir). İnce halka
  ofseti kurulamayınca "dar" sayılıyordu (artık genişlik 2·alan/çevre ile tahmin ediliyor). İkisi de 2,0–2,6 mm basamakları gizliyordu.
  Sonra eğimli yüz ölçümü eklendi: yatay yatan tüp önce yalnız 454 mm² destek gösteriyordu, eğim ölçümüyle 6.174 mm² oldu.

## Sonuç (10 parça = 5 tür × sağ/sol; sol X aynası, sonuç aynı)

| Parça | Malzeme | Yön (tablada) | Ölçü (mm) | İlk katman | Desteksiz? | Destek alanı / hacmi | En büyük köprü / konsol (mm) | Kütle (0,8 / 0,9) | Süre sa (10 mm³/s; 7 mm³/s) |
|---|---|---|---|---|---|---|---|---|---|
| Omuz yuvası | PETG-CF | −Y: y = 25 üst yüzü tablada, manşon yatay | 76 × 76 × 67 | 1.616 mm² | **Hayır** (5 bölge) | 2.194 mm² / ≈ 58 cm³ | 41,1 / 34,6 | 66,6 / 75,0 g | 1,70–1,88; 2,43–2,69 |
| Rulman kapağı | PETG-CF | +X: x = 146 yüzü tablada, Ø52 yuva yukarı açık | 76 × 60 × 14 | 1.405 mm² | **Evet** | 0 | 0 / 0 | 14,6 / 16,4 g | 0,32–0,36; 0,46–0,51 |
| Omuz göbeği | PETG-CF | +X: Ø40 mil ucu x = 150 tablada | 66 × 51 × 49 | 1.157 mm² | **Hayır** (3 bölge) | 2.058 mm² / ≈ 28 cm³ | 40,0 / 26,5 | 52,9 / 59,5 g | 1,27–1,42; 1,82–2,03 |
| Kol çatalı | PETG-CF | −Z: üst (horn) kulağı z = 30,5 tablada | 76 × 56 × 63,5 | 1.438 mm² | **Hayır** (3 bölge + 2 eğim yüzü) | 2.023 mm² / ≈ 60 cm³ | 3,3 / 42,9 | 83,2 / 93,6 g | 2,07–2,30; 2,95–3,28 |
| Üst kol tüpü | PETG | +Y: tüp ucu tablada, eksen dik | 56 × 56 × 100 | 396 mm² | **Evet** | 0 | 0 / 0 | 40,2 g (0,8) | 0,88 |

- **"Desteksiz" iddiası 10 parçanın 6'sında tutmuyor** (omuz yuvası, omuz göbeği ve kol çatalı, ikişer adet). Bu üç türün **hiçbir eksen
  yönü desteksiz değil**. En az destekli yönleri de destek istiyor: yuva −Y 2.194 mm², göbek −Y 688 mm², çatal +Y 861 mm².
- Toplam (10 adet): kütle **515–569 g**, süre **12,5–13,7 sa** (10 mm³/s). PETG-CF yavaş senaryoyla ≈ 17–19 sa. Baskı listesindeki omuz
  değerleri düşük: %60 doluluklu model kütlesiyle 386 g, 48 g/sa ile 8,6 sa.
- Isıl gömme somunlar:
  - yuva M3 × 4: seçili yönde **yatay**, ağız yanda;
  - göbek M5 (625ZZ mafsalı): **yatay**, delik boydan boya açık;
  - çatal tüp M3 × 2: seçili yönde dikey. Biri yukarı, biri aşağı açılıyor; aşağı açılan pimin altındaki destekli bölgeye bakıyor.
  - Rulman kapağında ve tüpte somun yok.

### Parça parça destek bölgeleri ve öneriler (geometri değiştirilmedi; karar tasarım ajanının)

**Omuz yuvası (−Y).** Manşon yatay, böylece kol momenti katman düzleminde kalıyor (seçimin sebebi). S1 kulak delikleri ve kapak
somunları yatay.
1. Manşon tavanı (y = −20,2 iç yüzü): 40,4 mm köprü, 1.148 mm². Destek manşonun içinde, alt duvarın iç yüzüne (sigma oturma yüzü) basıyor.
   Bu yönde kaçınılmaz. Öneri: yalnız manşon içine destek (enforcer) ve arayüz katmanı; oturma yüzü sonra temizlenir. +X yönünde manşon dik
   olur ama uç duvarı ve plaka için destek 3.905 mm²'ye çıkıyor.
2. Kollar ve servo plakası y = 22'de bitiyor, yani tabladan 3 mm yukarıda başlıyor: 485 mm², 34,6 mm konsol. **Öneri: kolları ve plakayı
   y = 25'e uzat** (3 mm). Parça tablaya oturur, destek kalkar. Çakışma kontrolü tasarım ajanında.
3. Kapak kulakları (x 127–146, z ±26…38, y ±12) tabladan 13 mm yukarıda başlıyor: 2 × 231 mm², 18,7 mm konsol. **Öneri: kulakları
   y = 25'e kadar uzat** ya da altına 45° takviye koy.
4. S1 servo penceresi tavanı: 20 mm köprü (100 mm²), 15 mm kuralını az aşıyor. Öneri: pencere üstüne 45° damla tepe ya da küçük destek.
   Plakada damla için ~11 mm yer var, sınırda.
   2 ve 3 yapılırsa kalan destek yalnız manşon içi ve pencere olur.

**Rulman kapağı (+X).** İddia tutuyor. Ø52 yuvanın ekseni dik, yuva yukarı açık (fil ayağı yuvaya denk gelmiyor). Değişiklik gerekmez.

**Omuz göbeği (+X).** Ø40 mil ve S1 horn delikleri dik; kolun tüm momenti bu yoldan geçiyor. S2 kulak delikleri ve M5 somunu yatay.
1. Flanş plakası (x = 163) Ø45 omzun dışına 26,5 mm konsol: 1.588 mm². Destek tabladan 13 mm kolonla geliyor. Alt yüz geçme yüzü değil,
   kapağa 3 mm boşluğu var. Öneri: tablaya basan ağaç destek. Plaka altına 45° takviye kapakla çakışır, önermiyorum.
2. Ø40 → Ø45 basamağı: 2,0 mm konsol (270 mm², sınırda). Bu yüz 6808 iç bileziğinin dayanma yüzü, sarkarsa geçme bozulur. Öneri: baskıdan
   sonra ölç, gerekirse düzle; ya da basamağa 0,5 mm pah ver.
3. S2 servo penceresinin üst kenarı (x = 195,5): 41 mm köprü, 3,5 mm et. **Öneri: pencereyi x = 199'a kadar aç (U kanal).** S2 kulak
   delikleri (y −14,75 / 34,75) yan raylarda kalır, köprü kalkar. Servo tutuşu tasarım ajanında kontrol edilmeli.
4. M5 ısıl gömme deliği (Ø6,4) yatay basılıyor; üstü sarkar, somun eğik oturabilir. Öneri: deliği damla biçimli yap ya da kuponun M5
   deliğini yatay olarak da bas.
   Alternatif yön −Y (arka duvar tablada) 688 mm² destek ister, ama Ø40 mil ve horn delikleri yatay kalır. Rulman geçmesi yüzünden
   önermiyorum.

**Kol çatalı (−Z).** Horn delikleri, Ø16 625ZZ yuvası ve tüp somunları dik.
1. Alt kulak (z −28…−33) duvardan 42,9 mm konsol: 1.081 mm². Destek 54 mm kolonla **üst kulağın iç yüzüne (S2 horn oturma yüzü, z = 25,5)**
   basıyor, horn yüzünde destek izi kalır.
2. Ø50,8 pim ve Ø56 bileziğin yatay silindir alt yüzü: 836 mm² eğim (en dik 79°) ve 19,4 mm konsol; destek tabladan.
   - Alternatif +Y (pim ucu tablada): 861 mm², ≈ 19 cm³ destek, hepsi tablaya basıyor. Kalanlar: duvar uçları Ø56 bileziğin dışına
     8,9 mm taşıyor (2 × 232 mm²), bilezik basamağı 2,1 mm. Ama horn delikleri ve Ø16 yuva yatay olur: yuva ovalleşir, katmanlar flanşı
     boyuna keser.
   - **Öneri:**
     - (a) Çatalı ikiye böl: alt kulak ayrı parça olur, duvara vidalanır. İki parça da flanşı tablada, desteksiz ve yük yönü doğru basılır.
     - (b) Bölmeden −Z yönünde destek arayüzüyle bas, horn yüzünü sonra düzle.
     - Duvar uçları Ø56 içine çekilirse +Y neredeyse desteksiz olur, ama yuva yatay kalır.

**Üst kol tüpü (+Y).** İddia tutuyor. Yükseklik / √taban oranı 5,0 (100 mm boy, 396 mm² halka), bu yüzden 5 mm brim öneriyorum. M3
delikleri Ø3,4, yatay ve küçük. Katmanlar tüpün eğilmesini keser, ama gerilme ≈ 0,05 MPa (0,26 kg × 100 mm, tahmini), ihmal edilebilir.

## Baskı listesine girecek (sonraki adım; bu adımda `baski-listesi.md`'ye dokunulmadı)
- Satır 6–7'deki "44 parçanın hepsi … desteksiz basılıyor" cümlesi yanlış. Omuzda 6 adet destekli: yuva, göbek, çatal (ikişer).
  Kaynak `omuz/omuz-baski.json`.
- Omuz satırlarının "Tabla yönü" sütunu ("—") doldurulacak:
  - yuva: "y = 25 üst yüzü tablada, manşon yatay, destekli"
  - kapak: "x = 146 yüzü tablada, yuva yukarı"
  - göbek: "mil ucu tablada, destekli"
  - çatal: "horn kulağı tablada, destekli (ya da bölünmüş)"
  - tüp: "uç tablada, brim"
- Omuz filamenti ve süresi (adet başına, doluluk 0,8–0,9):

  | Parça | Filament | Süre | Eski filament |
  |---|---|---|---|
  | Yuva | 81–90 g | 1,7–1,9 sa | 52 g |
  | Kapak | 15–17 g | 0,3–0,4 sa | 12 g |
  | Göbek | 61–68 g | 1,3–1,4 sa | 42 g |
  | Çatal | 99–110 g | 2,1–2,3 sa | 66 g |
  | Tüp | 42 g | 0,9 sa | 32 g |

  Eski süreler 48 g/sa tahminiyle hesaplanmıştı. "Omuz analizinde süre yok" notu kalkar.
- **PETG-CF toplamı** 0,79 kg'dan ≈ 0,96–1,02 kg'a çıkıyor (omuzun payı 344 g'dan 512–569 g'a). Önerilen "1 kg siyah PETG-CF" (2 × 0,5 kg)
  artık pay bırakmıyor. %20–25 payla ≈ 1,25 kg gerekir, yani 3 × 0,5 kg (`maliyet.json` da değişir, tahmini).
- Toplam baskı süresi ≈ 120 sa'ye omuz farkıyla ≈ 4–5 sa eklenir.
- Sol omuzun STL'si yok (`stl/` yalnız sağ). Sağ STL dilimleyicide X'e göre aynalanır.

## Açık sorunlar (tasarım ajanına / sonraki adıma)
1. `omuz_parcalar.RHO["PETG"] = 1,27 × 0,6`. Bu yüzden omuz baskı kütlesi M4'ün 0,8–0,9 doluluğuna göre %33–50 düşük kalıyor: kol başına
   +43–58 g (Göbek grubu +13–20 g, Kol grubu +31–42 g). `omuz-analiz.json` tork tablosu ve ana montaj kütlesi bununla yeniden hesaplanmalı.
2. FCStd'de 5 parçanın `Malzeme` alanı "PETG". 4'ü PETG-CF olmalı.
3. Yatay ısıl gömme delikleri (yuva M3 × 4, göbek M5) için kupon yok; kupon B'nin delikleri dik basılıyor.
4. `omuz_montaj.py` `sigar` ölçütü 230 mm, `arayuz.YAZICI` 246 mm. Sonucu değiştirmiyor ama tutarsız.
5. Yöntem sınırları: 45° kuralı, 15 mm köprü ve 1 mm konsol sınırı, 0,5 mm analiz katmanı, Ø10'a kadar yatay delik serbest. Destek hacmi
   ve süreler tahmini. Sonuç dilimleyici (Bambu Studio) önizlemesiyle karşılaştırılmadı.
6. Analiz FCStd 15:48:40'a dayanıyor. M1 kablo yolu değişikliğinden sonra betik aynen yeniden koşulmalı (~4,5 dk):
   `FC_SCRIPT=$R/omuz/omuz_baski.py "$FC" $L`
