# F10v · P10.7b2j günlüğü (CAD tasarım turu 2; iki ajanlı CAD kuralının birinci yarısı)

DURUM: BİTTİ (19.11.2026). Push yok. Worktree `lale-cad-b2j` (depo dışı), taban `8bca2f5`, açılış ucu `d8f9c41`. Ana çalışma ağacına
yazılmadı (orada b2k rehber ajanı); ana ağaçtan yalnız okundu: `planlama/d158/F10u-gunluk.md` § 8 (CAD ajanına liste), `planlama/adim3/kablolar.json`
bara-pabuc yerleşimi, `lale158/kablo_yolu_taban.py`, `rehber/rehber_kablo.py` (`bara_yol_denetle`, `geometri_denetle`, `CAD_KIRP`). Rehber
kaynaklarına dokunulmadı. Her FreeCAD koşusundan önce ana ağaçtaki `FREECAD-KILIT.txt` "boş" okundu (yazılmadı), boş bellek ≥ 5,3 GB.

## 1. CAD kablo yolları bara tutucusu saplamalarına (BİTTİ, FreeCAD'de üretildi; commit `b308728`)

Atama: kendi çıkardığım atama F10u § 8 listesiyle birebir aynı (çelişki yok). Saplama numarası = `arayuz.TABAN["bara_tutucu"]` sırası
(x artan, önden bakınca soldan sağa). Kaynak `taban/taban_parcalar.py` § 8: `bara_uc(bara, no, yon)`, `bara_arasi`, `yarik_inis` yardımcıları
ölçüyü `BT`'den okur (tutucu taşınırsa yollar birlikte kayar).

**Echo kararları (geri alınabilir):**
- Bara ucu saplama ekseninden 10 mm (pabuç dili yönü), y 194 (tutucu üstü 189,5 + 4,5; tüp altı tutucuya 2 mm, somuna radyal ≈ 2,9 mm).
  F10u'nun şema önerisi (x; 191,9; z + 5) tüpü tutucuya 0,1 mm, kendi pul / somununa gömüyordu; benim ucum ona 5,4 mm (`GEO_ESIK` 10 içinde).
- Bara üstü yatay hat y 197 (somun üstü 195,7): tutucuyu yalnız iki saplamanın ortasından (eksenlere 12,5 mm) aşar.
- Panelden alt kata iniş akü kablo yariklarının ortasından, z −30 (yarık z −37…−23; akünün gövde ön yüzü z −38, kutuplar x ±65,5'te
  z −29'a çıkar): sol yarıkta x −57 (yol 1), −55 (3), −50 (7), −45 (5); sağda 46 (9), 54 (4), 62 (2).
- Yol 3 tek yol olarak röle → anahtarlı 3 (G09 / G11) → köprü boyunca 2 → 1 (G12+) → yıldız 1 (G12−) → sol yarık. Yol 4 (G13) dalı yol 3'ün
  anahtarlı 2 ucundan başlar (`GEO_DAL {4: 3}` korunur: dal başı ana yolun noktası).
- Yol 8 / 9: + damarı sigorta kutusundan (F3 / F4), yol yıldız 4'e uğrar (8 +z yanından, 9 −z yanından), anahtarlı tutucuyu 2–3 / 3–4 arasından aşar.
- Etiketler (parça adları) "WAGO" / "role -> WAGO" yerine bara + saplama yazıyor; `rehber_metin.KABLO_AD`'ın beklediği baş kısımlar aynı.
- Önceden kalan küçük kusurlar da (yalnız bu yollarda) düzeltildi: yol 3 ve 4'ün ön plaka deliğinden çıkışı plakaya değiyordu (y 87'ye
  indirildi; yol 4 ön motordan deliğe geri dönüp arka motora iner), yol 4 XL4016 çevrenin içinden geçiyordu (x 80 → 87), yol 7 BTS7960
  solun 0,85 mm içinden geçiyordu (ara nokta).

| Yol | Kablo (damar) | Uç(lar) (x; y; z) | En dar yabancı (gerçek geometri) | En dar bara (yabancı) |
|---|---|---|---|---|
| 1 | G01–G04 | baraya uğramaz; yıldızın önünden z −36, y 199 | 4,46 ön şarj kartı | 8,7 yıldız tutucusu |
| 2 | G05− | yıldız 3 (0; 194; −45) | 4,5 güç paneli (yarık kenarı) | 13,2 yıldız 4 pul |
| 3 | G09+/G11+, G12+, G12− | anahtarlı 3 (12,5; 194; −105), 2 (−12,5; 194; −105), 1 (−37,5; 194; −105), yıldız 1 (−50; 194; −45) | 2,26 alt plaka (delik kenarı) | 6,1 yıldız 2 somunu |
| 4 | G13+, G13− | anahtarlı 2 (−12,5; 194; −105) [dal başı], yıldız 2 (−25; 194; −45) | 0,89 akü kayışı (plaka altı, kutu ölçüsü) | 6,0 / 6,1 yıldız 3 civatası / somunu (19.11 düzeltme, kaynak `F10u-kontrol.md` yol doğrulaması; önceki yazım "> 15") |
| 5 | G14+, G14− | anahtarlı 1, yıldız 1 (yol 3 ile aynı uçlar) | 2,5 güç paneli (yarık kenarı) | 6,1 yıldız 2 somunu |
| 7 | G15+, G15− | anahtarlı 1, yıldız 1 | 4,5 güç paneli | 6,1 yıldız 2 somunu |
| 8 | G17− | yıldız 4 (25; 194; −45) | 5,0 anahtarlı tutucu | 5,0 anahtarlı tutucu |
| 9 | G18− | yıldız 4 (25; 194; −65) | rehber bölümü 3,5 güç paneli | 5,0 anahtarlı tutucu |

Ölçüm: `planlama/d158/F10v-yol-bosluk.py` (FreeCAD, `distToShape`, tüp r 2,5 × Referans olmayan her parça; kablonun bağlı olduğu /
içinden geçtiği parçalar ayrı) → `F10v-yol-bosluk.json`. U06 şeridi (x 14…40, z −40…−30, y ≥ 205): bu bölgede en yüksek tüp üstü y 201,5
(yol 1); şeride giren yol yok. Pabuç uçları y 194 (≤ 200).

**Yol 9 ve 12:** yol 12'ye dokunulmadı. Yol 9'un rehberde korunan bölümü **değişti**: noktalar[0..3] (4 nokta) → noktalar[0..12]
(13 nokta; F4 → anahtarlı 3–4 arası → yıldız 4 → yıldız 4–5 arası → sağ yarık → XL4016 çevre). Atılan eski bölüm (noktalar[13..15] =
eski [4..6]) koordinatça aynı. **Rehberde `CAD_KIRP[9]["son"]` 3 → 12** yapılmalı; kesim düzlemi aynı kalır (normal (0, 1, 1), en büyük
izdüşüm yine XL4016 ucu 141,42 → kesim 143,92; `cad_kirp_denetle` 0 hata). `son` 3 kalırsa `bara_yol_denetle` "yol 9 yıldız 4'e ulaşmıyor" verir.

**Rehber sınamaları bu dalın `taban-analiz.json`'u ile, ana ağacın güncel `rehber_kablo.py`'si (salt okunur içe aktarma, `-B`):**
`bara_yol_denetle` → `son` 3 ile 1 hata (yukarıdaki), `son` 12 ile **0**; `geometri_denetle` hata **0** (bilgi 4: yol 6 / 10 modelsiz uçlar);
`cad_kirp_denetle` 0. Kuralın kendisinde hata görmedim (not: izin bölgesi yatayda 12 mm, y ≥ 175; yol 3'ün köprü bölümü anahtarlı 2'nin
yanından 10 mm geçer, takım kutusunun 2,5 mm payının dışında, hata vermez).

Önceden olan ve bu turun kapsamı dışında kalan (dokunulmadı): yol 10 ön şarj kartının üstüne 0,1 mm değiyor; yol 11 ve 12 elektronik katını
kesik dışında deliyor ve ESP32 taşıyıcısının burç / vidasına giriyor; yol 11 alt plakaya değiyor; yol 9'un atılan eski bölümü PCA9685'ten
geçiyor (rehberde çizilmez). Hepsi Referans (taramaya / kütleye girmez).

G22 şeması (b2k, yatay kısım z −80): CAD yolu değil (CAD_ESLEME'de G22 yok). CAD yolları tutucular arası koridoru z −95'te (yol 3) ve iki
saplamanın ortasından boyuna geçişlerle (x −37,5 / −12,5 / 0 / 25 / 37,5) kullanıyor; şemayla kesişme yalnız gösterimde, çakışma yok.

`taban_montaj.py` (FreeCAD): geçersiz 0, iç çakışma 0 (660 çift), bağlantı 140 / 140, taban × iskelet 0 (temas 36), × kabuk 0 (temas 1),
bölge ihlali 0, baskı 6 parça sorun 0; kütle 8.231,4 g (değişmedi; yollar Referans). DXF'ler ve `taban-bom.csv` değişmedi.

## 2. USB ses kartı yaması (BİTTİ, FreeCAD'de üretildi; commit `7127456`)

`git apply planlama/d158/F10s-ses-karti-cikar.patch` (yalnız `kafa/kafa10_lib.py`). `kafa_montaj.py` (258 s, çıkış 0; günlük okundu,
Traceback yok, bilinen 12 satır OCC "makeElementFace" uyarısı): geçersiz 0, ev pozu çakışma 0 (502 → 499 çift), bağlantı 29 / 29, kütle
2.089,5 → **2.081,4 g**, tilt payı 3,7 → **3,8**, pan payı 2,2 → **2,3**, STEP katı 163 → 161; `kafa-bom.csv`'de kart satırı yok, köpük bant
10 → 9. F10s § 5 denemesiyle aynı. Kafa içi kablo kütlesi (`lale158/kablo_yolu_ekran.py` KABLO_EK) bu dalda eski dosyadan: b2k'nın −7,0 g'lık
değişikliği birleşmeden sonra kafa_montaj yeniden koşulunca girer. `taban_montaj` kafa kütlesini okuduğu için yeniden koşuldu
(`kafa_duzeltme` −8,1 g; ana montaj bekliyor).

## 3. Küçükler

- **D24V50F5 pin yönü (doğrulanamadı, model değişmedi):** Pololu ürün sayfası (pololu.com/product/2851): 17,8 × 20,3 × 8,8 mm, 0,1"
  aralıklı **tek sıra 5 pin** (EN, VIN, GND, GND, VOUT), iki M2 deliği karşı köşelerde; hangi kenarda olduğu ve sıra yönü sayfada yazmıyor.
  Modelde kart pinsiz düz blok (`kafa_lib.cevirici_local`), yönü yok. Sonuç: giriş ve çıkış aynı kenarda; TVS'nin (−80; 20) "çıkışın
  yanında" olması pin kenarının +z'ye (TVS'ye) bakmasına bağlı → montajda kart pin kenarı +z'ye gelecek şekilde yapıştırılmalı (rehber notu
  önerisi; kart yazısıyla teyit).
- **F10s "669 çift"** → 660 (F10s § 4 satırı düzeltildi, not eklendi).
- **K52 regülatör için güç panelinde boş alan (modellenmedi):** panel üstüne çıkan parçalar + direk cebi + iki akü yarığı, 3 mm pay, ≥ 20 mm
  dikdörtgenler (parça kutularıyla; kablo yolları hariç tutulmadı):
  1. x −94…94 (188) × z −170…−129 (41): anahtarlı tutucu ile sigorta kutusu arası. CAD yolları 1 (z −165), 3 (röle çıkışı), 8, 9 (x 0 / 25) geçer.
  2. x −132…132 (264) × z −97…−69 (28): iki tutucu arası koridor; bara kablolarının yolu (yol 3 z −95, 3 / 4 / 5 / 7 / 8 / 9 boyuna) → uygun değil.
  3. x 56…93 (37) × z −247…−170 (77): sigorta kutusunun sağı (yol 10 F5 çıkışı üstünden geçer; acil stop gövdesi y ≥ 214).
  4. x −89…−56 (33) × z −247…−170 (77): sigorta kutusunun solu (ana anahtar y ≥ 216 üstte; yol 1 z −210'da geçer).
  5. x 25…62 (37) × z −20…20 (40) ve x −59…−25 (34) × z −20…20 (40): direk cebinin iki yanı (yarıkların önü; yol 1 / 2 yarıktan çıkar).
  LM2577 + LM2596 kart ölçüsü bilinmeden seçilmedi; 1 en büyüğü ama kablo geçidi.

## 4. Tarama / analiz ajanına (taze ajan) eskiyen çıktılar

- Değişen izlenen kaynaklar: `taban/taban_parcalar.py`, `kafa/kafa10_lib.py` → `carpisma_kos` tazelik kaydı 9 bölümün hepsi için eski
  (F10t § 5 tarifi; tam koşu ≈ 3 sa 50 dk, koşarken izlenen dosyaya dokunma).
- Yeniden üretilecek: `montaj/ana_montaj.py` (+ `robot-bom.csv`; kafa −8,1 g, kart satırı çıkar, taban parça adları değişti), görseller
  (`taban_gorsel.py`: taban FCStd GUI durumu yine yok; `kafa_gorsel.py`; `montaj_gorsel.py`), baskı zinciri (`baski_analiz_ortak.py` → … →
  `F4c-dogrula.py`; baskı parçası değişmedi, 74 beklenir), `kafa_rapor.py`, `taban_rapor.py`, `montaj_rapor.py`, regresyonlar.
- Dikkat: kablo yolu tüpleri Referans; tarama onları saymaz. Yolların sınaması `F10v-yol-bosluk.py` (FreeCAD, ≈ 15 s) ve rehberin
  `bara_yol_denetle` / `geometri_denetle`'si (birleşmeden sonra, `CAD_KIRP[9]["son"] = 12` ile).

## 5. Rehber (b2k) tarafına

1. `rehber_kablo.CAD_KIRP[9]["son"]` 3 → 12 (gerekçe metni "noktalar[4..]" → "noktalar[13..]"; `cad_kirp_metin` aynı: `(0, 0.7071, 0.7071) · p ≤ 143.92`).
2. Taban kablo yolu parça adları değişti (yol 2, 3, 4, 5, 7, 8, 9; baş kısımlar `KABLO_AD` ile uyumlu, "WAGO" yok). Onay kaydında tam ad
   tutuluyorsa yenilenmeli; `KABLO_AD[3]` metni "röle K1 ∥ ön şarj kolu → anahtarlı bara" yol geometrisiyle uyumlu.
3. CAD uçları (x; 194; z ± 10) şema uçlarından (x; 191,9; z + 5) farklı (yukarıda gerekçe); yıldız 4'te yol 9 −z yanından (25; 194; −65).
4. Yol 4 artık panelden başlıyor (dal başı = yol 3'ün anahtarlı 2 ucu); yol 3'te anahtarlı 2 ucu köprü gösterimi.
5. `MODELSIZ_KONUM` / `_G10_YAKIN` gerekçeleri: yol 3 sigorta kutusunun yanından değil, ön şarj kartının ≈ 8,6 mm yanından iner (G10 / G11 yanı
   bu yakınlıkla sağlanıyor; geometri_denetle hata 0).
6. D24V50F5 pin kenarı +z notu (§ 3) E3a'ya eklenebilir.

## Commit'ler

`b308728` kablo yolları (+ `F10v-yol-bosluk.{py,json}`), `7127456` ses kartı yaması, sonraki: bu günlük + F10s düzeltmesi.
