# V: bağımsız doğrulama (düzeltme planı 1. adım)

Başlangıç: 14 Ekim 2026. Ajan: bağımsız kontrol. Kaynak/tasarım değiştirilmez, git commit yok, tam çakışma taraması ve ana montaj koşulmaz.

## Durum
- [x] 1 Değişen dosyalar / günlükte olmayan değişiklik
- [x] 2 Modüllerin yeniden üretimi (sırayla: iskelet, omuz, dirsek, kabuk, taban)
- [x] 3 İddia / ölçüm tablosu
- [x] 4 eklem_sinirlari_uret --kontrol, carpisma_kos kontrol
- [x] 5 Sabit grep (eski değeri kullanan kod)
- [x] 6 Regresyon

## Günlük
- 15:40 Başladı. Günlüklerin (A1, A2, B, F) hepsi okundu. Çıktı ön-kopyası (karşılaştırma tabanı): scratchpad `onceki/` (analiz JSON, BOM, regresyon dosyaları, carpisma-sonuc.json).
- Adım 1 (git diff, HEAD=daccdbd; çalışma ağacında 11 Ekim değişiklikleri de var): günlüklerde SÖYLENMEYEN kaynak değişiklikler:
  - `taban_montaj.py`: ana montajda taban varsa tabansız robot kütlesi/AM/parça sayısı hesabı (`_MT`, `N_r0`) değişti; B günlüğünde yok (devrilme hesabının girdisi).
  - `omuz_rapor.py` ~ ok (A2 yazmış); `kafa_rapor.py`/`montaj_rapor.py`: yalnız C6 uyarı kutusu satırı (A1 yazmış).
  - `montaj/eklem-dogrulama.json` yalnız `sure_s` değişti (kuru koşu yan etkisi; A1 GIF yan etkisini yazmış, bunu yazmamış).
  - `ortak_lib.py insert()`/`INSERT_DELIK`, `maliyet.json` (beyaz PETG, PETG-CF): 11 Ekim işi, 1. adımın değil.
- `python -I kod/ortak/eklem_sinirlari_uret.py --kontrol` -> "guncel", rc 0. `eklem_sinirlari.json`: S2 3…120, S1 -45…135, kutu pan 25…60 (sol -60…-25), tilt 20…30, kol koşulu öne 120…135 / yana 3…5 / dirsek 65…105.
- `python carpisma_kos.py kontrol` -> ESKİ, rc 1 (beklenen): değişen arayuz, carpisma, dirsek/kabuk/omuz/taban _parcalar, ortak_lib; kayıtta yok: dirsek/kabuk/kafa/omuz _lib, sigma_profil, kafa-analiz.json; 9 bölümün 9'u eski.
- Üretim: omuz_regresyon (54 s) -> fark.json önceki ile AYNI; yalnız beklenen 3 fark (parça 70->66, adlar, BOM 17->16). omuz-analiz.json önceki ile aynı. iskelet_montaj (23 s), iskelet_regresyon: BİREBİR AYNI; iskelet-analiz.json yalnız eğilme sayıları değişti (omuz kütlesi -4 pul; önceki iskelet koşusu omuzdan önceydi), geometri/kesim aynı. dirsek_montaj (47 s): analiz önceki ile aynı, tek fark `tork.omuz_eski.S1` 5,61 -> 5,59 (A2'nin `lim` süzgeci yana 0 -> 3; A1 koşusu A2'den önceydi: kasıtlı C1 sonucu).
- Bağımsız ölçüm (v_olcum.py, günlüklerden bağımsız geometri okuması): tüp iç/dış r 25,65/28,0; çatal pim r 25,4, bilezik iç r 28,25 -> pim 0,25, bilezik 0,25; tüp×çatal ortak hacim 0. Omuz M6 uç-somun payı 1,7 (4/4), omuz kütle 848,49 g/66 parça, M6 pulu yok. İskelet köşe M6 payı 0,6 (8/8), sigma mesafesi 1,9.
- 16:05 Üretim bitti: kabuk_montaj (488 s) ve taban_montaj (94 s) dahil tüm modüller yeniden üretildi; ayrıca omuz/iskelet/dirsek/kabuk/taban `*_rapor.py` yeniden koşuldu (rapor.html). Ana montaj, carpisma tam koşu, kafa ve GUI görselleri koşulmadı.
  Tekrarlanabilirlik: kabuk, taban ve omuz analiz JSON'ları ve BOM'lar ajan çıktılarıyla birebir aynı (yalnız `sure_s`); iskelet ve dirsek farkları regresyon bölümünde.

## İddia / ölçüm tablosu
| İddia (günlük) | Ölçülen (kendi çıktım) | Uyuyor |
|---|---|---|
| Tüp–bilezik radyal boşluk 0,25 (A1) | bağımsız dilim: tüp dış r 28,0; bilezik iç r 28,25 -> 0,25; modül kontrolü 0,25 | evet |
| Pim–tüp 0,25; tüp iç r 25,65 (A1) | tüp iç r 25,65 (omuz geometrisinden), pim r 25,4 -> 0,25; tüp × çatal ortak hacim 0 | evet |
| Kabul sınırı 0,3 (A1) | `dirsek_montaj.py`: `0 < b <= GECME["kabul_max"]` ve `abs(b - GECME[...]) < 1e-6`; 22/22 bağlantı | evet |
| Omuz M6 payı: somun 1,7 / kanal tabanı 0,8, 4/4 (A2) | modül kontrolü 1,7 / 0,8 (4/4); bağımsız somun payı 1,7 (4/4); pul yok; 66 parça, 848,49 g | evet |
| Taban plaka M6: 1,7 / 0,8, 14 bağlantı (B) | analiz `somun_gecme_pay` 1,7, `uc_taban_pay` 0,8 (18 M6 kanal bağlantısı; 8 M4: 1,4 / 1,1); bağımsız somun payı 1,7 (14/14), sigma mesafesi 0,8 (12/14; 2'sinde bbox süzgeci olmayan OCC distToShape sahte 0,0 verdi, arka rayla 0,8) | evet |
| Kabuk gövde braketi M6×14 pulsuz: uç 11,0, 1,7 / 0,8, 8 delik (F) | analiz 8× (11,0; 1,7; 0,8; pulsuz); bağımsız 1,7 / 0,8 | evet |
| Etek braketi M6×14 + pul: uç 10,4, 1,1 / 1,4, 6 delik (F) | analiz 6× (10,4; 1,1; 1,4; pullu); bağımsız 1,1 / 1,4 | evet |
| İskelet köşe M6 payı (≥0,5 her yerde, M3) | 8× uç 9,9: somun payı 0,6, tabana 1,9 (bağımsız ölçüm aynı); kontrolde 0,5 şartı YOK (yalnız `somun_alti <= uc < taban`) | değer evet, kontrol zayıf |
| En küçük bindirme boşluğu 0,1881; 21 çift, ihlal 0 (F) | 0,1881 (orta bant ↔ göğüs bandı sağ/sol), 21 çift, ihlal 0; diğerleri 0,2019 … 0,25 (etek 0,2153 / 0,2475 dahil) | evet |
| Çubuk artıkları 194,5 / 99,0 / 109,0 (B) | analiz aynı; elle: 1000-2-(800,5+3)=194,5; 1000-2-(500+200+190+9)=99; 1000-2-(500+190+190+9)=109; `kesim_hatasi` boş | evet |
| S2 alt sınırı 3° (A2) | `arayuz.OMUZ`, `omuz-montaj.FCStd` AngleMin=3 / Max=120, S1 -45 / 135, `eklem_sinirlari.json` min 3 (sağ + sol); `--kontrol` güncel | evet |
| Kol ↔ kabuk 3°'de en az 7,17; 0°'de 3,76 (öne 40); -2°'de temas (A2) | bağımsız (kabuk FCStd'den): (40,0,0): -3: 0, -2: 0, 0: 3,76, 3: 7,17, 5: 8,56; (0,0,0): -2: 0,63, 0: 4,67, 3: 8,18; ek pozlar 3°'de 7,15 (90,60,0 ve 135,0,0) | evet; 3°'de en az 7,15 (0,02 mm sapma, A2 yalnız 6 poz taradı) |
| Kafa-kol kutusu pan 25…60 / tilt 20…30, sol aynası (A2) | JSON aynı; 198 + 198 yasak kol pozundaki 603 + 603 kafa pozunun hepsi kutunun içinde (kutu dışı 0) | evet |
| Parça/kütle: omuz 70/852,56 -> 66/848,49; taban 306/7507,6 -> 292/7493,4; kabuk 202/4901,2 -> 194/4886,3; dirsek 369,3 -> 368,7 | omuz 66 / 848,49 (595,2+147,2+106,1); taban 292 / 7493,4; kabuk 194 / 4886,3, AM (-0,08; 466,68; 8,57); iskelet 59 / 5793,1; dirsek 53 / 368,7. Pul kütlesi elle: 4×1,017=4,07; 14×1,017=14,2 | evet |
| Robot toplamı: A2 "907 -> 899", B "907 -> 893" | ikisi kısmi. Birleşik beklenen: 907 - 8 (omuz) - 14 (taban) - 8 (kabuk) = 877 parça; kütle 21.224,45 -> ≈ 21.185,9 g (omuz -8,14, taban -14,23, kabuk -14,95, dirsek -1,28). Ana montaj koşulmadı, hesap | günlükler tek başına eksik |
| Kabuk `bosluk.cam_duvar_mm` ile rapor "0,1 mm" (A1, D3) | `kabuk_montaj.py`: `round(0.106 * cos(15°), 3)` = 0,102; ölçüm değil, elle yazılı 0,106 sabitinden | metin "değişkenden" ama değişken de sabit |

## Modül kontrolleri (yeniden üretimden)
| Modül | Geçersiz | Çoklu katı | Modül içi çakışma | Komşu arayüz | Bağlantı | Yeni kontrol |
|---|---|---|---|---|---|---|
| iskelet (59 parça) | 0 | 0 | 0 | bölge ihlali 0 (57 bölge) | 12/12 | kesim artığı ≥10 mm: geçti |
| omuz (66) | 0 | 0 | statik 0; tarama kol×göbek 8, göbek×gövde 0, kol×gövde 94 (önceki ile aynı) | tork farkı 0 (5,722 kg·cm) | eklem testi True | M6 payı 4/4; S2 3…120 |
| dirsek (53) | 0 | 0 | ev pozu 0 | omuz arayüzü 0, 5/5 geçti | 22/22 | tüp-bilezik 0,25 / kabul 0,3 |
| kabuk (194) | 0 | 0 | 0 (485 çift) | iskelet 0 (116), bölge ihlali 0 (51) | braket 10/10, bindirme cıvatası 51/51, ekran 4/4 | M6 payı 14/14, bindirme 21 çift 0 ihlal, baskı 15/15 sığar |
| taban (292) | 0 | 0 | 0 (469 çift) | iskelet 0 (44 temas), kabuk 0 (1 temas) | 111/111 | M6 uç somun payı ≥0,5: geçti |

## Regresyon
- Kasıtlı (1. adım): omuz parça 70->66, adlar, BOM 17->16; taban 306->292; kabuk 202->194; dirsek çatal/bilezik -0,64 g; kabuk dili 0,05 mm incelme (-3,2 g); iskelet kesim planı (geometri aynı); `tork.omuz_eski.S1` 5,61 -> 5,59 (S2 süzgeci 0 -> 3).
- İskelet regresyonu (8 Ekim tabanı): BİREBİR AYNI. Omuz regresyonu: `fark.json` ajan çıktısıyla aynı.
- Beklenmeyen fark: yok. Not: `iskelet-analiz.json` eğilme sayıları değişti (F 11,9717 -> 11,9318 N vb.), çünkü önceki iskelet koşusu omuzun pulsuz kütlesinden önceydi; zararsız.
- `taban/regresyon/moduller.json` 8 Ekim tarihli; üreten betik depoda yok (D4'te yeniden yapılacak).

## Bulgular (kesin / şüpheli)
- KESİN: `dirsek_montaj.py:413-414` tork taraması hâlâ elle `range(-45,136,5)` / `range(0,121,5)` (S2 3° yok; muhafazakâr ama C3 hedefine aykırı). `iskelet_montaj.py:243` en kötü durum ızgarası yana 0…120 / öne 0…180 elle (muhafazakâr).
- KESİN: `montaj/eklem_dogrulama.py:194` POZ ve `montaj_gorsel.py` (poz-önü yana=0, Kollari_oynat yana 0…69) S2 3°'nin altına iniyor; ana montaj koşusunda `sinir_ici=False` ("SINIR DIŞI") çıkacak.
- KESİN: `omuz_montaj.py` M6 kontrolü kanal tabanı tarafında `taban_pay > 0` (diğer modüllerde ≥0,5); iskelet köşe M6 kontrolünde hiç 0,5 şartı yok. Değerler (0,8 / 0,6) şu an geçiyor.
- ŞÜPHELİ: dirsek bilezik kelepçesi: yarık 2 mm kapanınca çevre 2 mm kısalır, yarıçap ≈ 0,32 mm iner; toplam radyal boşluk artık 0,25 + 0,25 = 0,5 mm (eskiden 0,2). Tüp pime tam bastırılamayabilir (bilezik–tüp arası ancak ≈ 0,07 mm sıkışma). Baskı kuponuyla doğrulanmadı (A1 de işaretlemişti).
- ŞÜPHELİ: kafa-kol kutusunun dayanağı olan 198 çakışma pozunun hepsi yana = 0 (artık erişilemez). Yana 3°'de çakışma var mı taranmadı; kutu C7'ye kadar kanıtsız muhafazakâr kural.
- ŞÜPHELİ: `omuz_parcalar.py:175,180,189` pim yarıçapı 25,4 ve tüp dış r 28 elle yazılı (`A.TUP_PIM_R` / `D["tup_ro"]` kullanmıyor); dirsek kontrolünün bilezik tarafı tüp dışını arayüzden okuyor (bağımsız ölçüm 28,0 çıktı, tutarlı).
- Not: `distToShape` bbox süzgeci olmadan sahte 0,0 verebildi (taban M6 vida ↔ uzak sigma). Depodaki taramalar bbox süzgeci kullanıyor, zarar yok.

## Eski değer taşıyan belge/rapor metinleri (düzeltilmedi)
OZET.md (202/306 parça, 4.901/7.508 g, S2 0…120, eski yasak tablosu, dil 0,2 mm); tasarim/freecad/README.md (S2 0…120, pan 30…55 / tilt 25…30, 306 parça/7.508 g, 907 parça/21.260,9 g); planlama/baski-listesi.md:103 (bindirme 0,2 mm); iskelet/rapor.html + `iskelet_rapor.py` (omuz "4× M6×16 + 4× M6 pul"); dirsek/rapor.html (yana 0…120, 907 parça/21,22 kg, 202/202 8 Ekim regresyonu, "0° konumu kabuğa kaçmamalı"); kabuk/rapor.html (yana 0…120, 21.260,9 g/907); taban/rapor.html (306 parça/7.507,6 g, 907 parça, yana 0…120; `taban_rapor.py:272` varsayılan 601, `:388` "306"); kafa/rapor.html ve montaj/rapor.html (yeniden üretilmedi: eski yasak bölge, C6 uyarı kutusu yok).

## Sonuç
Geçti. Bağımsız ölçüm günlük iddialarının hepsini doğruladı; beklenmeyen regresyon yok. Açık işler yukarıdaki bulgular ve 6. adım (carpisma tam koşu, ana montaj 877 parça beklenir).
