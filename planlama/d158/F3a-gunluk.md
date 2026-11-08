# F3a günlüğü: elde yük tablosu ve servo payları (P3.1, P3.2), 09.11.2026

Ajan A (tasarım/analiz). Brief: `planlama/d158/F3a-brief.md`. FreeCAD kullanılmadı; mevcut dosyaların hiçbiri değişmedi.
Yazılan dosyalar: `planlama/d158/F3a-yuk.py` (hesap betiği), `planlama/d158/F3a-yuk.json` (bütün sayılar), bu günlük.
Koşu: `python planlama/d158/F3a-yuk.py` (≈ 40 s, saf Python, yalnız okur). Regresyon: `regresyon.py --yazma` → **GEÇER**
(10 değer aynı; rampa yüksüz 1,519, tilt 3,64, pan 2,21).

## 1. Girdiler (F1b sonrası çalışma kopyası, commit'lenmemiş hâliyle okundu)

| Kısa | Dosya | Kullanılan |
|---|---|---|
| MA | `tasarim/freecad/montaj/montaj-analiz.json` | `parcalar[]` (modül, grup, kütle, global merkez, sıfır eklem açısı); toplam 25.715,59 g (akü 3,0 kg F1b'de) |
| UI | `tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json` | `izgara_yuk_{0,100,500}g` (doğrulama ve hücre kaynağı), `kablo_payi` |
| DA | `tasarim/freecad/dirsek/dirsek-analiz.json` | `arayuz` (eksen noktaları, `el_ucu`), `tork.sonuc[]` (doğrulama ve hücre kaynağı) |
| KA | `tasarim/freecad/kafa/kafa-analiz.json` | `tork.tilt`, `tork.pan` |
| HS | `tasarim/freecad/lale158/kafa-yerlesim/hat-secenek-{0,a,b}.json` | `tork_hatli`, `tork_hatsiz` |
| AY | `tasarim/freecad/arayuz.py` | S1 −45…135 (175), S2 5…120 (176), DS3235 stall 30,4 (184), tilt ±13 (582), pan ±90 (579) |
| SO | `planlama/d158/servo-10-oneri.md` | kod sınırları (§1 tablo, Ç2–Ç5): omuz 0…160, dirsek 0…110, tilt ±20, pan ±45; S2 ve bilek kodda yok |

## 2. Yöntem (değiştirilmedi, FreeCAD'siz yeniden yazıldı ve doğrulandı)

- **Devrilme / fren / rampa:** `uygulama_ivme.py` (Y2b-ivme kopyası) aynen: a_dev = g (d cos θ − h sin θ) / h, teker hattı z ±185, x ±216;
  ızgara S1 −45…135 / 15 × S2 5, 30, 60, 90, 120 × dirsek 0, 35, 70, 105 (bilek 0), kip "simetrik" ve "sağ" (sol kol ev pozunda);
  +400 g kablo payı; **yük her iki elin ucunda** (`arayuz.DIRSEK.el_ucu`), yani "100 g" satırı = elde 100 g, robota toplam 200 g.
  "Devrilme payı" K3 ve `regresyon.py` ile aynı anahtar: `a_sinir_pay15` = a_dev_min / 1,5 (ölçüt ≥ 1,5; sayı aynı zamanda 1,5 m/s²
  referans ivmedeki pay). Fren payı = a_dev_min / 1,8 (`fren_pay.duz_min`). Betikteki tek fark: FreeCAD Placement'ları (Pp, Pr, Pe, Pb,
  `moduller.global_poz` aynası) Rodrigues dönüşümüyle saf Python'da; parça merkezleri MA'dan.
- **Kol servo torku:** `dirsek_montaj.py` bölüm 5 `tork(phi, th, al, be)` aynen: statik yerçekimi torku; S1 = Σ m·z, S2 / dirsek / bilek
  kendi ekseni etrafında (r × F)·a; ızgara S1 ve S2 5° adım (uç sınırlar dahil), dirsek 5°, bilek −90 / 0 / 90; yük el ucunda (bilek için kanca
  noktasında). Pay = stall / en kötü tork. Stall: DS3235 30,4 kg·cm (AY:184, 5,48 V hat modeli), MG996R 9,4 kg·cm (4,8 V datasheet).
- **Tilt / pan:** `kafa_montaj.py` bölüm 6 aynen: tilt = yerçekimi torku (sınır açısında) + I·α (α 26,2 rad/s²); pan = I_max·α + rulman + kablo.
  Tilt yerçekimi KA / HS'deki kafa grubu kütlesi ve AM'sinden (0,01 mm yuvarlanmış) yeniden hesaplandı.

**Doğrulama** (`F3a-yuk.json` → `dogrulama`):
- UI'nin 0 / 100 / 500 g için 18 anahtarı: a_dev farkı **0,000** (en büyük 0,0001 m/s²), en kötü poz ve kip 18/18 aynı, AM farkı ≤ 0,01 mm.
  Ev pozu kütle 26.115,5 / AM (−0,03; 522,71; −10,03) = UI `ev`.
- DA `tork.sonuc`: S1, S2, dirsek, bilek yüksüz ve 500 g torku 4/4 aynı (0,01 kg·cm), `izinli_yuk_2x_g` 105 / 99 / 112 / 3.600 aynı.
  Dirsek en kötü pozu farklı yazıldı ([90,100,0,−90] ↔ DA [90,30,0,90]): S1 90'da S2 ekseni düşey olur, S2 ve bilek açısı dirsek torkunu
  değiştirmez; aynı torklu pozlar arasında bağ (tie), sayı aynı.
- Tilt: KA `pay_tilt15` 3,64 aynı; `egri` 6 noktada fark ≤ 0,001 kg·cm; HS 0 / a / b HAT'lı-HAT'sız `pay_tilt15` 6'nın 5'i aynı,
  b HAT'lı 3,38 ↔ 3,37 (AM 0,01 mm yuvarlaması).
- Sonuç: 1,58 m kol servo sayıları (S1 / S2 0,97, dirsek 0,74 @ 500 g) bugünkü montaj parçalarıyla **yeniden hesaplandı ve aynı çıktı**
  (kol geometrisi 1,58'de değişmedi; K9'daki "1,65 m'den, yeniden ölçülmedi" notu artık kapanabilir).

## 3. P3.1: düz zeminde elde yük tablosu

Yük her iki elde (toplam = 2 ×). Kalın: ölçütün altında (devrilme / fren / rampa ≥ 1,5; servo ≥ 1).

| Elde yük (toplam) | Düz devrilme, en kötü yön | Fren 1,8 m/s² | Rampa 5° (ızgara) | Rampa 5°, kollar ev pozunda (bilgi) | S1 | S2 | Dirsek | Bilek |
|---|---|---|---|---|---|---|---|---|
| 0 g (0) | 2,097 (geri) | 1,748 | 1,519 | 1,611 | 2,78 | 2,72 | 3,88 | 463 |
| 50 g (100) | 2,077 (geri) | 1,731 | **1,499** | 1,606 | 2,34 | 2,30 | 2,73 | 111 |
| 100 g (200) | 2,057 (geri) | 1,714 | **1,479** | 1,601 | 2,03 | 2,00 (1,996) | 2,11 | 62,7 |
| 200 g (400) | 2,017 (geri) | 1,681 | **1,440** | 1,591 | 1,59 | 1,58 | 1,45 | 33,6 |
| 500 g (1.000) | 1,907 (geri) | 1,589 | **1,329** | 1,563 | **0,97** | **0,97** | **0,74** | 14,0 |

Servo torkları (kg·cm, aynı sırayla 0 / 50 / 100 / 200 / 500 g): S1 10,95 / 12,98 / 15,01 / 19,06 / 31,22; S2 11,16 / 13,19 / 15,23 / 19,29 / 31,50;
dirsek 2,42 / 3,44 / 4,46 / 6,50 / 12,62; bilek 0,02 / 0,08 / 0,15 / 0,28 / 0,67.

**Hücre kaynakları**
- 0, 100, 500 g devrilme / fren / rampa: UI `izgara_yuk_{0,100,500}g.a_sinir_pay15.duz_geri`, `.fren_pay.duz_min`,
  `.a_sinir_pay15.rampa5_geri` (F3a betiği aynı sayıyı üretti). 50, 200 g: `F3a-yuk.json` `P3_1.izgara.{50,200}` aynı anahtarlar.
- Rampa, kollar ev pozunda: `F3a-yuk.json` `P3_1.izgara.<yük>.ev_pozu_rampa5.pay15_min` (aynı formül, poz S1 0 / S2 5 / dirsek 0, yük elde; ızgara değil).
- Servo 0 ve 500 g: DA `tork.sonuc[S1|S2|Dirsek|Bilek].yuksuz_kgcm` / `.yuklu_kgcm`, pay `yuksuz_pay` / `yuklu_pay`;
  50, 100, 200 g: `F3a-yuk.json` `P3_1.tablo[i].servo.<eklem>.pay` (DA yöntemi, `tork()` aynen).

**En kötü pozlar ve neden**
- Düz / rampa "geri" (arkaya devrilme, ileri hızlanmada): iki kol simetrik, S2 120 (kollar yana tam açık) + S1 75 (0–50 g) → 90 / dirsek 35
  (100–200 g, rampa 100 g'dan) → 105 / dirsek 35 (500 g). Kollar yukarı-geriye kalkınca AM hem yükselir (h 532 → 561 mm) hem geri kayar
  (z −14,3 → −21,6 mm); d küçülüp h büyüdüğü için a_dev en küçük. Yük arttıkça en kötü poz elin daha yukarıda olduğu S1'e kayıyor.
- S1 (DS3235): S1 90 / S2 5 / dirsek 0, kol dümdüz öne yatay; el ucu yükünün S1 eksenine yatay kaldıracı en büyük (405,4 mm).
- S2 (DS3235): S1 0 / S2 90 / dirsek 0, kol dümdüz yana yatay; kaldıraç 406,9 mm (el ucu omuz eksenine 406,9 mm).
- Dirsek (MG996R): S1 90, dirsek 0: üst kol öne yatay, ön kol da yatay; yükün dirsek eksenine kaldıracı 203,9 mm (en büyük).
  S1 90'da S2 ekseni düşey olduğundan S2 ve bilek açısı torku değiştirmez (aynı torklu poz ailesi).
- Bilek (MG996R): yük bilek ekseninde, kanca ofseti ~13 mm; tork küçük, pay her yükte ≫ 1.

**Sınır taraması** (her elde, `F3a-yuk.json` `P3_1.sinir_her_elde_g`; 10 g adım, servo ikiye bölme):

| Ölçüt | Geçtiği en büyük yük (her elde) |
|---|---|
| Düz devrilme ≥ 1,5 | ≥ 1.000 g (tarama sonu; bağlayıcı değil) |
| Fren 1,8 m/s² ≥ 1,5 | 810 g |
| Rampa 5° ızgara ≥ 1,5 | 40 g (50 g'da 1,499) |
| Rampa 5° kollar ev pozunda ≥ 1,5 | ≥ 1.000 g |
| Servo pay ≥ 1 | dirsek **342 g**, S2 473 g, S1 480 g, bilek > 5.000 g |
| Servo pay ≥ 2 (DA `izinli_yuk_2x_g` ölçütü) | S2 **99 g**, S1 105 g, dirsek 112 g |

**Önerilen sınır: elde ≤ 100 g (her el; iki elde toplam ≤ 200 g), düz zeminde; rampada yüksüz.**
Gerekçe:
1. Brief ölçütü (devrilme ≥ 1,5, servo ≥ 1) tek başına ≈ 340 g'a izin veriyor; bağlayan **dirsek servosu** (342 g), devrilme değil.
2. Ama pay 1 stall torkuna göre: stall servonun durduğu tork (DS3235 için 5,48 V hat modeli, MG996R için 4,8 V datasheet); hesap statik,
   kolun ivme torku ve gerilim düşümü yok. Projenin önceki hedefi 2× pay (DA `izinli_yuk_2x_g`, K9 "2× pay için ~100 g"): 100 g'da
   S1 2,03, S2 2,00 (1,996, 2×'in hemen altında), dirsek 2,11. 100 g, 2× referansına en yakın yuvarlak değer (kesin 2× sınırı 99 g, S2).
3. Devrilme 100 g'da düzde 2,057, frende 1,714: ikisi de ≥ 1,5, yük artışıyla yavaş düşüyor (500 g'da bile 1,907 / 1,589).
4. Rampa ızgara payı 50 g'da bile 1,499 < 1,5: kollar her pozda serbestken rampada yük taşınamaz. Mevcut kural (rampada kollar ev pozunda,
   karar 29.10, Y2a KZ1) uygulanırsa 100 g ile 1,601 (500 g ile 1,563) ≥ 1,5; yani "rampada yüksüz" yerine "rampada yük varsa kollar ev pozunda"
   da savunulabilir, ama bu yazılımın ev pozunu zorlamasına bağlı (SO Ç7: boşta pozu ev pozu değil). Varsayılan önerim temkinli olan: rampada yüksüz.

## 4. K3 eki taslağı

(Kayıt ajanı K3 maddesine ekler; `karar-kuyrugu.md`'ye bu paket yazmadı.)

- **P3.1 tablosu (F3a, 09.11.2026; `planlama/d158/F3a-yuk.json`, betik `F3a-yuk.py`, FreeCAD'siz, `uygulama_ivme.py` ve `dirsek_montaj.py`
  yöntemi aynen; 0 / 100 / 500 g UI ve DA sayılarını birebir üretti):** yük her iki elde.

  | Elde yük | Düz devrilme | Fren 1,8 | Rampa 5° | S1 | S2 | Dirsek |
  |---|---|---|---|---|---|---|
  | 0 g | 2,097 | 1,748 | 1,519 | 2,78 | 2,72 | 3,88 |
  | 50 g | 2,077 | 1,731 | 1,499 | 2,34 | 2,30 | 2,73 |
  | 100 g | 2,057 | 1,714 | 1,479 | 2,03 | 2,00 | 2,11 |
  | 200 g | 2,017 | 1,681 | 1,440 | 1,59 | 1,58 | 1,45 |
  | 500 g | 1,907 | 1,589 | 1,329 | 0,97 | 0,97 | 0,74 |

  Kaynak anahtarlar: `izgara_yuk_*.a_sinir_pay15.duz_geri`, `.fren_pay.duz_min`, `.a_sinir_pay15.rampa5_geri` (0 / 100 / 500 UI, 50 / 200
  `F3a-yuk.json P3_1.izgara`); servo DA `tork.sonuc` (0 / 500) ve `F3a-yuk.json P3_1.tablo` (50 / 100 / 200). Bilek her yükte ≥ 14.
- Bağlayan ölçüt servo: pay ≥ 1 için ≤ 342 g (dirsek), pay ≥ 2 için ≤ 99 g (S2). Düz devrilme ≥ 1,5 1.000 g'a kadar, fren ≥ 1,5 810 g'a kadar tutuyor.
- Rampa ızgara payı 50 g'da 1,499 (< 1,5); kollar ev pozunda 100 g ile 1,601, 500 g ile 1,563.
- AI HAT+ (K2; 30 g varsayım, Pi'nin 4 üst vidası çıkınca net 28,1 g: HS `kafa_grubu_g` farkı) eklenince yüksüz rampa 1,519 → 1,515, düz 2,097 → 2,093
  (a ve b aynı; 30 g ile de 1,515); sonuç değişmiyor.
- **Varsayılan (K3 "Varsayılan" satırının yerine):** b, her elde ≤ 100 g (iki elde toplam ≤ 200 g), yalnız düz zeminde; rampada yüksüz. c (500 g) ancak
  K9 b ile (500 g'da S1 / S2 0,97, dirsek 0,74). Seçenek b metnine "her elde" eklenir. Alternatif: rampada kollar ev pozunda zorlanırsa ≤ 100 g (1,601; SO Ç7'ye bağlı).

## 5. P3.2: servo payları (3,0 kg akü sonrası, AI HAT+ ana modelde yok)

Akü kol ve kafa servolarının torkuna girmiyor (taban gövdesinde); kol servoları için 3,0 kg akü öncesi ve sonrası aynı.

**Kol servoları** (`F3a-yuk.json` `P3_2.<eklem>.{cad,kod}_{0,100,500}g`):

| Servo | Model / stall | Yüksüz, CAD sınırı | Yüksüz, kod sınırı | 100 g (CAD = kod) | 500 g (CAD = kod) | En kötü poz (S1, S2, dirsek, bilek) |
|---|---|---|---|---|---|---|
| S1 | DS3235 / 30,4 | 2,78 | 2,78 | 2,03 | **0,97** | 90, 5, 0, 0 |
| S2 | DS3235 / 30,4 | 2,72 | 2,72 (kodda S2 yok; öneri = CAD) | 2,00 | **0,97** | 0, 90, 0, −90 |
| Dirsek | MG996R / 9,4 | 3,88 | 3,88 | 2,11 | **0,74** | 90, *, 0, * |
| Bilek | MG996R / 9,4 | 463 | 463 (kodda yok) | 62,7 | 14,0 | yük bilek ekseninde |

Kod sınırı (S1 0…160, dirsek 0…110) kol servolarında **kötüleştirmiyor**: en kötü poz kolun yatay olduğu S1 90 / dirsek 0, iki aralığın da içinde
(160'a kalkan kol yataydan uzaklaşır, tork azalır). Horn kayması (SO Ç6) ile kod 0…160 → CAD −45…115 olsa da S1 90 içeride; sonuç aynı.
Yan bilgi: S1 150 / 160 ızgaraya eklenince devrilme de değişmedi (0 g düz 2,097 / rampa 1,519; 100 g 2,057 / 1,479; `not_kod_s1_160_devrilme`).

**Pan / tilt** (`F3a-yuk.json` `P3_2.kafa`; tilt = yerçekimi + I·α, stall 9,4):

| Model | Tilt CAD ±13 | Tilt ±15 (korunan değer metriği) | Tilt kod ±20 | Pan CAD | Pan kod (tilt ±20, pan ±45) |
|---|---|---|---|---|---|
| Bugünkü model (HAT yok) | 3,65 | 3,64 | 3,61 | 2,21 | 2,17* |
| K2 a, boss taşı (HAT'lı) | 3,32 | 3,30 | 3,27 | 2,20 | 2,16* |
| K2 b, yığın 5 mm önde (HAT'lı) | 3,39 | 3,38 (HS 3,37) | 3,34 | 2,20 | 2,17* |

Kaynak: CAD ±13 = KA / HS `pay_iki_hane` ile aynı (3,65 / 3,32 / 3,39); ±15 = `pay_tilt15`; ±20 bu betik (aynı formül, açı 20).
Pan CAD = KA `tork.pan.pay_iki_hane` / HS `pan_pay_iki_hane`.
\* Pan kod: pan torku pan açısından bağımsız (kodun ±45'i etkisiz); yalnız tilt ±20'ye çıkınca I_max büyür. KA `I_kgm2` yalnız −13 / 0 / +13'te;
I(θ) = A + B cos 2θ + C sin 2θ üç noktadan uydurulup ±20'ye uzatıldı (0,014681 → 0,014936 kg·m²): **tahmini (ekstrapolasyon)**.

**Kod sınırı daha kötü:** tilt (±20) ve pan (tilt ±20 üzerinden), ama hepsi korunan eşiklerin üstünde (tilt ≥ 3,0, pan ≥ 2,0): en düşük K2 a
tilt 3,27, pan 2,16. Tilt ±20'nin asıl sorunu tork değil, çakışma: güncel model `kafa-analiz.json` `tarama.ilk_carpan` ±20'de çakışıyor
(327,4 / 654,9 mm³; ±15 serbest, 5° adım); +18° / −17° 29.10 ölçümü (`y2/Y2a-kontrol.md:54`, QLED öncesi kafa, 0,5° adım).

**1'in altına düşen:** yalnız 500 g elde S1 0,97, S2 0,97, dirsek 0,74 (K9). Yüksüz ve ≤ 100 g'da bütün servolar ≈ 2 ve üstü (en düşük S2 1,996); kafa ≥ 2,16.

## 6. Karar taslağı (P3.2 → K9 güncellemesi)

- **K9 sayısal etki güncellemesi:** 1,58 m modelinde yeniden hesaplandı (F3a, `F3a-yuk.json P3_2`): 500 g elde S1 0,97, S2 0,97, dirsek 0,74;
  1,65 m sayılarıyla aynı (kol geometrisi ve kütlesi değişmedi, DA 400,5 g). "1,65 m modelinden; 1,58 m'de yeniden ölçülmedi" cümlesi düşebilir.
- **Seçenek b'nin servo gereksinimi** (aynı statik yöntem, el ucunda 500 g): pay ≥ 1 için S1 ≥ 31,2, S2 ≥ 31,5, dirsek ≥ 12,6 kg·cm stall;
  pay ≥ 2 için S1 ≥ 62,4, S2 ≥ 63,0, dirsek ≥ 25,2 kg·cm. Daha ağır dirsek servosu S1 / S2 torkunu da büyütür; bu etki ve maliyet **hesaplanmadı**.
- b seçilse de rampada 500 g ızgara payı 1,329 < 1,5 (yalnız kollar ev pozunda 1,563).
- **Varsayılan önerisi değişmedi:** a (≤ 100 g; K3 b ile aynı sınır). Pan / tilt için karar gerekmiyor (K2 a ve b'de de eşik üstü).

## 7. Açık kalanlar ve fark edilen sorunlar (iş yapılmadı, not)

1. Kol servo payı **statik** (yerçekimi); kol ivme torku bu pakette yok. Mevcut ivmeli pay (yüksüz, ×1,25 taslak): `taslak-170/kol-analiz/kol-analiz.json` S1 1,64, S2 1,62, dirsek 3,18;
   yüklü ivmeli hesaplanmadı (B kaba tahmini: 100 g'da S1 ≈ 1,1, 200 g'da < 1, `F3a-kontrol.md`). Stall ölçütü servonun tutma sınırı değil; 2× referansı bu yüzden anlamlı.
2. Devrilme ızgarası bilek 0'da ve 15° adımda (UI ile aynı); "sağ" kipinde de yük iki elde (sol kol ev pozunda yük tutuyor): tek elde yük için temkinli.
3. Pan kod değeri ekstrapolasyon (yukarıda *). Kesin değer için `kafa_montaj` I_pan'ı ±20'de hesaplamalı (FreeCAD, bu pakette yok).
4. AI HAT+ duyarlılığı nokta kütleyle (HS `tork_hatli` − `tork_hatsiz` kütle/AM farkı, kafa konumu MA `moduller[kafa].konum`; b'de Pi'nin 5 mm kayması
   da farka giriyor): yüksüz rampa 1,515, eşiğe 0,015 pay kalıyor. HAT ana modele girince korunan "yüksüz rampa ≥ 1,5" yine tutar ama dar.
5. Rampa kuralındaki "ev pozu" CAD ev pozu mu, kodun boşta pozu (omuz 10, dirsek 15) mu netleşmeli (SO Ç7); 4. maddedeki 1,60 CAD ev pozuyla.
6. Kodun tilt ±20 ve omuz 160 sınırları: tork açısından sorun yok, çakışma açısından var (F5 Ç2, Ç4); P5.1 / Efe tarafında.
7. DA `tork.yuklu_poz` dirsek için [90,120,0,0] yazıyor, bu betik [90,115,0,90] buldu: eşit torklu poz bağı (S1 90'da S2 / bilek etkisiz), sayı aynı.
