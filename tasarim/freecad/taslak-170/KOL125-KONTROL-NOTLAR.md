# Kol ×1,25 + DS3235: CAD kontrol/analiz ajanı notları (ara kayıt)

Durum: başladı (24 Ekim 2026). Görev: tasarım ajanının ×1,25 + DS3235 işini bağımsız doğrula; taslak_hesap.py ve kol_analiz.py'yi
gerçek geometriyle (ek 32,4 mm ön kolda) yeniden koş; tam çarpışma; devrilme/motor; raporlar. Onaylanmamış öneriler uygulanmaz.

## Okunan bağlam
- analiz/*.json 21 Ekim tarihli (×1,15 taslak). taslak_hesap.py girdi-*.json okur -> ×1,25 için taslak_analiz.py 'kutle' yeniden koşulmalı.
- taslak_hesap.py satır 72: tasarım ajanı el ucu ofsetini KOL_BOY_YENI - KOL_BOY_ESKI yaptı; eski girdilerle (×1,15 geometrisi) tutarsız.
- Önceki koşu süreleri: kafa-yeni 2841 s, kol_sag/sol-yeni ~2225 s, kafakol ~200 s, kolkol 21 s.
- Önceki analiz/*.json (×1,15) git HEAD'de; ayrıca scratchpad kopyası. kol-analiz önceki sonuç git e8697ac'de.
- Ön kol kesit uzatması = ONKOL_ALT profili (3 mm U, 339 mm²: kol_analiz ONKOL_ALT ile aynı alan) -> ön kolun kritik kesiti artık
  alt U'nun başı (s_e + 42,75), önceki analiz alt kesiti s_e + 60'ta ölçüyordu.

## Koşular (24 Ekim, ~02:00 başladı)
- FreeCAD paralel: A (kutle, dogrula, statik, kolkol, kafakol_sag/sol), B kol_sag, C kol_sol, D kafa; E: kutle 444 (yeniden: girdi'ye
  `alt_kume` bilek servosu alt kümesi + `kol` meta eklendi) + 480/500/520 kutle+statik.
- taslak_analiz.py değişikliği: b_kutle çıktısına `alt_kume` (OnKol içindeki bilek servosu + mil + 4 M4 + 4 somun) ve `kol` (seçim) eklendi.

## 1) Bağımsız doğrulama (dogrula bölümü + scratch kontrol_geo.py, 24 Ekim ~01:35)
- taslak_parcalar yeniden kurulum 1052 parça 24.496,25 g AM (−0,105; 566,916; −10,718) = kutle.json (fark −0,05 g, sıra/ad/kütle aynı).
- FCStd: 1052 nesne, aynı kütle, şekil merkezleriyle AM birebir. STEP: 1052 katı, 1052/1052 eşleşme (en kötü ölçüt 0,02), STEP geometrisi + kütleyle AM (−0,11; 566,92; −10,72).
- Paylı 24.941,25 g (400 + 45 kablo payı) = tasarım ajanının 24.941,3.
- Eksen kaymaları (125 cm'e göre): omuz/pan 435, dirsek 405, bilek 372,6 (= 405 − 32,4), tilt 493,26. Bilek y 1071,5 ✓, dirsek 1187 ✓.
- El ucu (sağ El en alt nokta, FCStd) y 983,1 ✓ (= 1390 − 406,9).
- Ön kol gövdesi 42,18 → 53,35 g (+11,17 g, 0,345 g/mm), 1 katı, geçerli; bbox 63,1 × 133,5 × 33,5 mm (tabla 250 ✓, hedef 230 ✓). El 40 × 84,6 × 58; tüp 56 × 130 × 56.
- Ön kol CAD kesitleri: s 30 (dirsek servosu penceresi, üst): A 324,1 mm², Wx 1.465, Wz 1.073 mm³ (kol_analiz idealize ONKOL_UST: 444 / 2.119 / 3.959 -> Wz 3,7× iyimserdi);
  s 42–92 (alt U, uzatma dahil): A 339,3, Wx 1.199, Wz 6.288 (kol_analiz ONKOL_ALT ile aynı).
- Statik (ev pozu, tüm çiftler): 3285 aday, 6 çakışma, hepsi 125 cm'den (S1 tamburu ↔ kol çatalı 97,9 / tüp 65,0; tüp ↔ S1 kaset kapağı 7,6; iki yan). Yeni 0.
- Kol ↔ kol: 227 poz çifti, çakışma 0, en az 290 mm (×1,15 ile aynı).
- Kafa × kol (sağ/sol): çakışma 0; en az 10,98 mm (El ↔ yüz kabuğu, kol 135/5/105/−90, kafa pan ±30 tilt 15). ×1,15'te 17,99 mm. -> ince yerel tarama yapılacak (pan 15° adımı arası).

## 2) taslak_hesap.py
- Değişiklik: OMUZ_SERVO_VERI (DS3218MG 20 sabit; DS3235 29/32/35 @5/6/7,4 V, stall servo geriliminde: kol-analiz HAT modeli), omuz_stall(),
  kol_gruplari() (eski tüp:yaka yolu aynen + yeni on_kol yolu), on_kol_uygula() (bilek alt kümesi + El + bilek ekseni kayar, U bölüm nokta kütle, atalet paralel eksen),
  kol_servo(omuz=...), robot_on_kol(), kol_orani_on_kol(); Robot girdi/TASLAK_KOL tutarlılık assert'i; TASLAK_HESAP_AN ortam değişkeni.
- Regresyon: TASLAK_KOL=115 TASLAK_OMUZ_SERVO=DS3218MG + eski girdi -> hesap.json eski dosyayla BAYT BAYT aynı (6,5 dk).

## Ara bulgular (24 Ekim ~02:05)
- İlk ×1,25 hesabında ×1,15 geri-alma kontrolü S1 9,92 vs gerçek ×1,15 9,87 kg·cm verdi: ön kol gövdesinin uzatma altı bölümü (alt U + bilek
  servosu plakası) bilek servosuyla birlikte kaymıyordu. Düzeltme: taslak_analiz kutle `alt_kume`'ye `on_kol_alt` (gövdenin uzatma altı, CAD common)
  eklendi; taslak_hesap.on_kol_uygula ve kol_analiz.kutle_noktalari bunu da kaydırıyor. kutle 444/520/480/500 yeniden koşuluyor (G).
- Hesap (ilk koşu, düzeltme öncesi; değerler değişebilir): ×1,25 + DS3235 S1 statik 10,72 kg·cm, stall 30,4 @5,48 V -> pay 2,84, ivmeli 1,66,
  elde 111 g; S2 2,79; dirsek 2,39 kg·cm pay 3,94 (×1,15: 5,18). Devrilme izgara düz 444 1,94 / rampa 1,36; 520 1,97 / 1,40; 520 + akü 75 öne
  düz min 2,07 / rampa min 1,49. Motor 5° rampa 0,5 m/s² %104, 0,25'te %88 (444).
- Rapor betikleri: taslak_rapor_analiz (servo/kol_orani/devrilme karar/çarpışma notu/sonuç kutusu/açık işler veriye bağlandı, kafakol_ince okunur),
  taslak_rapor (yeniden hesap satırı yalnız analiz eskiyse; kol-analiz bağlantı metni), kol_rapor (başlık, sonuç, KPI, bölüm 2, bölüm 8 önceki fark).

## Tarama sonuçları (24 Ekim ~02:15)
- kol_sag/sol (tam zincir, 43.043 tam ölçüm): eklem aralığında çakışma 0; en küçük boşluklar ×1,15 ile aynı (kabuk 0,5 S1 tamburu↔kaset kapağı, mevcut).
- kol_sag dirsek-only: çakışma 0; kabuğa 17,95 (dirsek çatalı↔göğüs bandı), aynı.
- kafakol S2=0 (aralık DIŞI): 357 çakışma (×1,15'te 0, en az 1,81 mm): El ↔ yüz kabuğu / arka kafa kabuğu, kol öne 125–135, yana 0, dirsek 80–105,
  pan −45…40, tilt ±15, ≤ 480 mm³. Aralıkta (S2 ≥ 5°) çakışma yok -> S2 ≥ 5° sınırı artık ön kol uzunluğu için de gerekli (açık iş).

## Hesap (düzeltilmiş ön kol modeli, 24 Ekim ~02:20) — analiz/hesap.json
- Yöntem kontrolü: ×1,25'ten ön kol uzatması geri alınınca S1 9,87 / dirsek 1,77 kg·cm = gerçek ×1,15 geometrisi (9,87 / 1,77) ✓.
- ×1,25 + DS3235 (stall 30,4 kg·cm @5,48 V): S1 10,72 kg·cm statik pay 2,84, ivmeli 1,66, elde 111 g; S2 10,91 -> 2,79 / 1,64, 106 g;
  dirsek 2,39 kg·cm pay 3,94 (×1,15: 5,32); kafa tilt 3,85, pan 2,20.
  Önceki ×1,15 + DS3218MG (20): S1 9,87 pay 2,03, ivmeli 1,22, elde ~0. ×1,36 (ek ön kola): S1 2,60 / 1,47.
- Devrilme (ızgara en kötü, düz / 5° rampa): 125 cm 2,83/2,25; 444 1,94/1,36; 520 1,97/1,40; 520 + akü 75 öne min 2,07/1,49.
  Ev pozu 444 düz 2,29/2,02/2,08 (ileri/geri/yan), rampa 1,71/1,45/1,50; 520 düz 2,33/2,06/2,56, rampa 1,75/1,48/1,98.
- Motor (444): düz 0,5 m/s² %50, 5° rampa 0,5 %104, 0,25 %88; 520: %51 / %106 / %90; yerinde dönüş μ0,5 ×2,66 (444).
- Kalan: kol_analiz koşuyor; kafakol_ince (H) ve kafa (D) FreeCAD'de; sonra kol_rapor + taslak_rapor + 115 regresyon tekrarı.

## Son durum (24 Ekim ~02:45)
- kafa (pan ±90 × tilt ±15, 259 poz): çakışma 0; kafa ↔ kabuk 34,7, iskelet 43,1, omuz 43,0 mm.
- kafakol_ince (taslak_analiz yeni bölümü, iki kol): 3.402 kol × 279 kafa pozu, çakışma 0, en az 7,71 mm (El ↔ yüz kabuğu, kol 132,5/5/95/−45, pan ±34 tilt 15). Kaba 10,98.
- kol_analiz (×1,25 + DS3235): S1 2,84 / 1,66, 111 g; hat yoğun 5,43 A, tepe 7,84 A, servo 5,48 V; dirsek geri sürme 1,46× (önceki 1,32);
  baskı L3 en düşük dirsek çatalı dış kolu 1,86 (önceki 2,07), L4 0,77; ön kol üst kesiti (CAD) L3 5,67 / L4 3,10, alt U 8,38 / 3,75.
  Zayıf halkalar (tahmini kapasiteli): S2 mili radyal L3 0,54, bilek MG996R mili L3 0,74, dirsek MG996R mili L3 0,78, 25T horn L3 1,30.
- Raporlar üretildi: rapor.html, kol-analiz/rapor.html ("yeniden hesaplanacak" notu yok). Statik 480'de bilinen 16 braket M4 ↔ uzun ray (taslak, önceden de).
