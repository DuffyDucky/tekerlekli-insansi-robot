# Makaralı omni modeli (ONERI-MAKARA) ve küre modeli (ONERI-ADAY) (Y0f, `kod/fizik/olcum_makara.py`)

**VARSAYIM**, bugünkü robot değil; aday teker (Nexus 14075) SEÇİLMEDİ. İkisi de öneri firmware (PI açık) ve aynı aday ölçüler (Ø127 × 29 mm, 480 g, merkez 14,5 mm içeri). Küre: ön teker tek küre + her adımda sıfırlanan x menteşesi (yanal direnç 0,05 × yük). Makara: göbek + 2 × 11 makara, her biri kendi ekseninde menteşe, temas makaralardan (`kod/fizik/omni_makara.py`, parametreler `kod/fizik/omni_teker.json`). Makara Ø 19 mm (ürün sayfası), boy 22 mm (TAHMİN), sıra eksen aralığı 10 mm (TAHMİN), makara 6 g (TAHMİN), yatak sürtünmesi makara başına 2 N (tek temas fazında yanal; pirinç boru, TAHMİN), enkoder arka (lastik) tekerde (pin planı), temas biçimi elipsoid (elipsoid a 24,9 mm). Etkin yarıçap sapması: elipsoid 0,005 mm, kapsül 0,357 mm; tur başına 22 makara geçişi.

Statik: ONERI-ADAY 26,882 kg, yük ön sol / arka sol / ön sağ / arka sağ 63,3 / 68,5 / 63,3 / 68,5 N, ön solda temas eden geom 1; ONERI-MAKARA 26,880 kg, yük ön sol / arka sol / ön sağ / arka sağ 63,8 / 69,6 / 62,9 / 67,5 N, ön solda temas eden geom 1

## Hız, kararlılık, zaman adımı ve çözücü (µ 0,8, 21 kg·cm)

Gerçek zaman oranı (RTF) = sanal s / duvar s, kayıtsız, tek iş parçacığı, bu makinede. Titreşim: v 0,25, 4 s.

| varyant | ayar | RTF düz / yerinde | yerinde w | pitch t-t ° | düşey ivme rms m/s² | 1,58 m ileri t-t mm | uyarı | nv / ngeom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | ana (dt 1 ms, eliptik koni, Newton) | 28,8 / 19,7 | 0,893 | 0,000 | 0,00 | 0,08 | 0 | 22 / 30 |
| ONERI-ADAY | dt 0,5 ms | 19,8 / 12,1 | 0,879 | 0,000 | 0,00 | 0,09 | 0 | 22 / 30 |
| ONERI-ADAY | ccd toleransı 1e-6 (MuJoCo varsayılanı) | 29,0 / 17,0 | 0,893 | 0,000 | 0,00 | 0,08 | 0 | 22 / 30 |
| ONERI-ADAY | dt 2 ms | 40,1 / 31,8 | 0,899 | 0,000 | 0,00 | 0,08 | 0 | 22 / 30 |
| ONERI-ADAY | piramit koni | 29,4 / 27,6 | 0,906 | 0,000 | 0,00 | 0,08 | 0 | 22 / 30 |
| ONERI-ADAY | impratio 10 | 29,4 / 17,4 | 0,887 | 0,000 | 0,00 | 0,09 | 0 | 22 / 30 |
| ONERI-ADAY | çözücü yinelemesi 20 | 29,4 / 19,3 | 0,893 | 0,000 | 0,00 | 0,08 | 0 | 22 / 30 |
| ONERI-ADAY | temas solref 0,002 | 22,1 / 23,4 | 0,907 | 0,000 | 0,00 | 0,08 | 0 | 22 / 30 |
| ONERI-ADAY | temas solref 0,008 | 30,7 / 19,0 | 0,874 | 0,000 | 0,00 | 0,09 | 0 | 22 / 30 |
| ONERI-MAKARA | ana (dt 1 ms, eliptik koni, Newton) | 13,3 / 9,4 | 0,904 | 0,003 | 0,05 | 0,10 | 0 | 64 / 208 |
| ONERI-MAKARA | dt 0,5 ms | 8,6 / 6,2 | 0,891 | 0,003 | 0,05 | 0,13 | 0 | 64 / 208 |
| ONERI-MAKARA | ccd toleransı 1e-6 (MuJoCo varsayılanı) | 13,1 / 11,0 | 0,904 | 0,003 | 0,05 | 0,10 | 0 | 64 / 208 |
| ONERI-MAKARA | dt 2 ms | 25,8 / 17,6 | 0,916 | 0,003 | 0,06 | 0,13 | 0 | 64 / 208 |
| ONERI-MAKARA | piramit koni | 15,4 / 11,2 | 0,918 | 0,001 | 0,04 | 0,11 | 0 | 64 / 208 |
| ONERI-MAKARA | impratio 10 | 14,5 / 10,8 | 0,902 | 0,003 | 0,05 | 0,13 | 0 | 64 / 208 |
| ONERI-MAKARA | çözücü yinelemesi 20 | 13,3 / 10,8 | 0,904 | 0,003 | 0,05 | 0,10 | 0 | 64 / 208 |
| ONERI-MAKARA | temas solref 0,002 | 16,6 / 11,7 | 0,919 | 0,001 | 0,05 | 0,09 | 0 | 64 / 208 |
| ONERI-MAKARA | temas solref 0,008 | 16,0 / 11,4 | 0,864 | 0,011 | 0,10 | 0,29 | 0 | 64 / 208 |

## Dönüş (küre / makara yan yana)

| varyant | durma | µ | yerinde w (komut 0,5 / 1 / 1,5) | tork / sürekli (w 1) | yay v 0,25 + w 0,5: w / yarıçap m | yay + w 1: w / yarıçap m | 90°: s / aşma ° | kolon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | 21kgcm | 0,5 | 0,459 / 0,926 / 0,926 | 1,1 | 0,420 / 0,57 | 0,650 / 0,30 | 2,0 / 5,7 | başarılı, 10,8 s |
| ONERI-ADAY | 21kgcm | 0,8 | 0,435 / 0,893 / 0,893 | 1,2 | 0,369 / 0,63 | 0,585 / 0,32 | 2,1 / 5,5 | başarılı, 10,9 s |
| ONERI-ADAY | 9kgcm | 0,5 | 0,456 / 0,861 / 0,861 | 2,3 | 0,139 / 1,24 | 0,302 / 0,45 | 2,4 / 6,8 | başarılı, 11,8 s |
| ONERI-ADAY | 9kgcm | 0,8 | 0,419 / 0,706 / 0,706 | 2,5 | 0,059 / 2,60 | 0,165 / 0,76 | 2,8 / 5,2 | başarılı, 13,8 s |
| ONERI-MAKARA | 21kgcm | 0,5 | 0,460 / 0,933 / 0,933 | 1,0 | 0,435 / 0,56 | 0,673 / 0,29 | 2,0 / 5,3 | başarılı, 10,7 s |
| ONERI-MAKARA | 21kgcm | 0,8 | 0,438 / 0,904 / 0,904 | 1,2 | 0,381 / 0,62 | 0,618 / 0,31 | 2,1 / 5,4 | başarılı, 11,1 s |
| ONERI-MAKARA | 9kgcm | 0,5 | 0,456 / 0,916 / 0,916 | 2,1 | 0,165 / 1,08 | 0,349 / 0,40 | 2,2 / 7,0 | başarılı, 12,4 s |
| ONERI-MAKARA | 9kgcm | 0,8 | 0,435 / 0,805 / 0,805 | 2,4 | 0,080 / 1,97 | 0,210 / 0,61 | 2,5 / 6,1 | başarılı, 13,1 s |

## Yan etkiler, rampa, eşik (µ 0,8, 21 kg·cm; eşik 9 kg·cm de)

| varyant | düz 6 s yol m | yanal itme 10 N: yan m / yön ° | dur m | acil stop m | 5° yan eğim duruş: yan m | 5° yan eğim düz 5 s: yan m / yön ° |
| --- | --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | 1,52 | 0,002 / 0,0 | 0,046 | 0,221 | -0,009 | -0,049 / -2,1 |
| ONERI-MAKARA | 1,52 | 0,002 / 0,1 | 0,046 | 0,220 | -0,006 | -0,031 / -1,4 |

| varyant | eğim | ortasına ulaştı | rampada hız m/s | `dur` sonrası 5 s geri kayma m | tutuyor |
| --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | 5° | evet | 0,327 | 0,175 | hayır |
| ONERI-ADAY | 10° | evet | 0,259 | 0,507 | hayır |
| ONERI-MAKARA | 5° | evet | 0,327 | 0,176 | hayır |
| ONERI-MAKARA | 10° | evet | 0,258 | 0,508 | hayır |

| varyant | durma | v komutu | 5 mm | 10 mm | 15 mm |
| --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | 21 kg·cm | 0,20 | geçti | geçti | geçti |
| ONERI-ADAY | 21 kg·cm | 0,39 | geçti | geçti | geçti |
| ONERI-ADAY | 9 kg·cm | 0,20 | geçti | geçmedi | geçmedi |
| ONERI-ADAY | 9 kg·cm | 0,39 | geçti | ön çıktı | geçmedi |
| ONERI-MAKARA | 21 kg·cm | 0,20 | geçti | geçti | geçti |
| ONERI-MAKARA | 21 kg·cm | 0,39 | geçti | geçti | geçti |
| ONERI-MAKARA | 9 kg·cm | 0,20 | geçti | geçmedi | geçmedi |
| ONERI-MAKARA | 9 kg·cm | 0,39 | geçti | ön çıktı | geçmedi |

## Titreşim (düz gidiş, µ 0,8, 21 kg·cm, 4 s; eğilim çıkarılmış)

t-t = tepeden tepeye. 1,58 m: tabana rijit bağlı, tabandan 1,58 m yukarıdaki nokta (gövde salınımının kafa yüksekliğindeki karşılığı); kafa: `kafa_bas` gövdesi (boyun / gövde servolarının esnekliği dahil). Makara geçiş frekansı = v / (2πR) × 22.

| durum | v m/s | gövde z t-t mm | düşey ivme rms / tepe m/s² | pitch t-t ° (baskın Hz) | roll t-t ° (Hz) | makara geçişi Hz | 1,58 m ileri / yan / düşey t-t mm | kafa ileri / yan t-t mm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V0 (lastik) | 0,10 | 0,000 | 0,00 / 0,0 | 0,000 (135,8) | 0,000 (135,8) | 4,3 | 0,00 / 0,00 / 0,00 | 0,00 / 0,00 |
| V0 (lastik) | 0,25 | 0,000 | 0,00 / 0,0 | 0,000 (135,8) | 0,000 (135,8) | 13,6 | 0,00 / 0,00 / 0,00 | 0,00 / 0,00 |
| V0 (lastik) | 0,39 | 0,000 | 0,00 / 0,0 | 0,000 (135,8) | 0,000 (135,8) | 22,2 | 0,00 / 0,00 / 0,00 | 0,00 / 0,00 |
| küre (ONERI-ADAY) | 0,10 | 0,000 | 0,00 / 0,0 | 0,000 (12,5) | 0,000 (16,7) | 5,5 | 0,11 / 0,01 / 0,00 | 0,11 / 0,01 |
| küre (ONERI-ADAY) | 0,25 | 0,000 | 0,00 / 0,0 | 0,000 (10,6) | 0,000 (10,6) | 13,8 | 0,08 / 0,00 / 0,00 | 0,08 / 0,00 |
| küre (ONERI-ADAY) | 0,39 | 0,000 | 0,00 / 0,0 | 0,000 (16,5) | 0,000 (19,6) | 21,5 | 0,08 / 0,01 / 0,00 | 0,07 / 0,01 |
| makara elipsoid | 0,10 | 0,009 | 0,01 / 0,1 | 0,003 (5,4) | 0,000 (2,8) | 5,5 | 0,15 / 0,00 / 0,01 | 0,15 / 0,00 |
| makara elipsoid | 0,25 | 0,009 | 0,05 / 0,3 | 0,003 (13,7) | 0,000 (6,8) | 13,8 | 0,10 / 0,02 / 0,01 | 0,09 / 0,02 |
| makara elipsoid | 0,39 | 0,009 | 0,10 / 0,5 | 0,003 (21,5) | 0,000 (10,8) | 21,5 | 0,13 / 0,00 / 0,01 | 0,12 / 0,00 |
| makara 5 küre | 0,10 | 0,010 | 0,10 / 0,5 | 0,003 (27,6) | 0,000 (2,8) | 5,5 | 0,16 / 0,01 / 0,01 | 0,16 / 0,01 |
| makara 5 küre | 0,25 | 0,012 | 0,51 / 1,6 | 0,004 (68,9) | 0,000 (6,8) | 13,8 | 0,12 / 0,01 / 0,01 | 0,11 / 0,01 |
| makara 5 küre | 0,39 | 0,014 | 0,95 / 2,8 | 0,005 (21,5) | 0,001 (10,6) | 21,4 | 0,15 / 0,03 / 0,01 | 0,14 / 0,03 |
| makara kapsül | 0,10 | 0,178 | 0,51 / 4,8 | 0,057 (5,7) | 0,002 (11,1) | 5,6 | 1,65 / 0,07 / 0,17 | 1,55 / 0,07 |
| makara kapsül | 0,25 | 0,033 | 0,98 / 5,5 | 0,015 (27,8) | 0,029 (13,9) | 13,6 | 0,75 / 1,17 / 0,03 | 0,76 / 1,12 |
| makara kapsül | 0,39 | 0,038 | 1,56 / 8,7 | 0,012 (42,2) | 0,024 (21,2) | 21,0 | 1,53 / 1,78 / 0,04 | 1,50 / 1,74 |

## Eşik duyarlılığı (makara, v 0,2, sonar kapalı)

| durum | durma | 5 mm | 10 mm | 15 mm | 20 mm | 25 mm | 30 mm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| makara Ø15 | 21 kg·cm | geçti | geçti | geçti | geçti | geçti | ön çıktı |
| makara Ø15 | 9 kg·cm | geçti | geçmedi | geçmedi | geçmedi | geçmedi | geçmedi |
| makara Ø19 (ana) | 21 kg·cm | geçti | geçti | geçti | geçti | geçti | ön çıktı |
| makara Ø19 (ana) | 9 kg·cm | geçti | geçmedi | geçmedi | geçmedi | geçmedi | geçmedi |
| makara Ø23 | 21 kg·cm | geçti | geçti | geçti | geçti | geçti | ön çıktı |
| makara Ø23 | 9 kg·cm | geçti | geçmedi | geçmedi | geçmedi | geçmedi | geçmedi |
| 5 küre Ø19 | 21 kg·cm | geçti | geçti | geçti | geçti | geçti | ön çıktı |
| 5 küre Ø19 | 9 kg·cm | geçti | geçmedi | geçmedi | geçmedi | geçmedi | geçmedi |
| kapsül Ø19 | 21 kg·cm | geçti | geçti | geçti | geçti | ön çıktı | ön çıktı |
| kapsül Ø19 | 9 kg·cm | geçti | geçmedi | geçmedi | geçmedi | geçmedi | geçmedi |
| küre modeli (ONERI-ADAY) | 21 kg·cm | geçti | geçti | geçti | geçti | geçti | ön çıktı |
| küre modeli (ONERI-ADAY) | 9 kg·cm | geçti | geçmedi | geçmedi | geçmedi | geçmedi | geçmedi |

## Makara yatağı sürtünmesi (makara başına; yerinde w komutu 1; enkoder arka)

Her makara ekleminde sabit Coulomb momenti = kuvvet × makara yarıçapı (yükle değişmez). Parametre, tek makara temasta iken tekerin yanal direncidir; iki sıra birden yere değerken model direnci ≈ 2,1 katına çıkar (B, Y0f-kontrol § 14.2: yerinde dönüşte zamanın ≈ %10'u, düz gidişte ≈ %30'u). Gerçekte pim sürtünmesi yükle bölünür, iki temasta toplam aynı kalır. Teker seçimi ölçütü: masada teker gerçek yükte (≈ 62 N) yavaşça yana çekilirken ölçülen sürekli kuvvet bu tablonun ilk sütunuyla (tek temas değeri) karşılaştırılır. TAHMİN'e bağlı, mertebe, sınır değil (2 N, pim µ 0,2 TAHMİN'inden).

| yanal N (tek temas) | 21 kg·cm µ 0,5 | 21 kg·cm µ 0,8 | 9 kg·cm µ 0,5 | 9 kg·cm µ 0,8 | 5° yan eğim 5 s: yan m / yön ° |
| --- | --- | --- | --- | --- | --- |
| 0,00 | 0,962 (0,8) | 0,937 (0,9) | 0,953 (1,6) | 0,919 (2,0) | -0,056 / -2,4 |
| 0,05 | 0,961 (0,8) | 0,931 (0,9) | 0,951 (1,6) | 0,929 (2,0) | -0,055 / -2,3 |
| 1,00 | 0,947 (0,9) | 0,920 (1,0) | 0,940 (1,9) | 0,892 (2,2) | -0,043 / -1,8 |
| 2,00 | 0,933 (1,0) | 0,904 (1,2) | 0,916 (2,1) | 0,805 (2,4) | -0,031 / -1,4 |
| 3,00 | 0,919 (1,1) | 0,886 (1,3) | 0,824 (2,3) | 0,666 (2,6) | -0,022 / -1,0 |
| 5,00 | 0,893 (1,3) | 0,858 (1,5) | 0,530 (2,8) | 0,367 (3,0) | -0,016 / -0,8 |
| 7,00 | 0,870 (1,5) | 0,831 (1,6) | 0,239 (3,2) | 0,004 (2,0) | -0,016 / -0,8 |
| 13,00 | 0,831 (2,0) | 0,765 (2,2) | 0,004 (2,0) | 0,004 (2,0) | -0,016 / -0,8 |
| 20,00 | 0,699 (2,3) | 0,376 (2,8) | 0,004 (2,0) | 0,004 (2,0) | -0,016 / -0,8 |

Hücre: gerçekleşen w rad/s (tork / sürekli).

## Rampa çıkışı ve temas biçimi (rampa_parkuru boyutları, rampa kipi, sonar kapalı, v 0,25, µ 0,8, 21 kg·cm, enkoder arka; "enkoder ön" satırları önceki ölçümün kurgusu)

Ön temassız = ön tekerin zemine değmediği fizik adımlarının oranı (sıçrama). Yük her fizik adımında ortalanır.

| durum | eğim | çıktı | rampada v m/s | ön çevre oranı | ön / arka yük N | ön temassız % | arka tork / durma |
| --- | --- | --- | --- | --- | --- | --- | --- |
| küre modeli ONERI (Ø125, teşhisteki) | 10° | evet | 0,250 | 1,00 | 28 / 99 | 0 | 0,42 |
| küre modeli ONERI (Ø125, teşhisteki) | 15° | evet | 0,109 | 2,64 | 12 / 113 | 92 | 0,81 |
| küre modeli ONERI-ADAY | 10° | evet | 0,250 | 1,00 | 31 / 99 | 0 | 0,43 |
| küre modeli ONERI-ADAY | 15° | evet | 0,121 | 2,23 | 14 / 113 | 90 | 0,78 |
| makara elipsoid (ana) | 10° | evet | 0,250 | 1,00 | 31 / 99 | 0 | 0,43 |
| makara elipsoid (ana) | 15° | evet | 0,120 | 2,25 | 14 / 113 | 89 | 0,78 |
| makara 5 küre | 10° | evet | 0,250 | 1,03 | 31 / 99 | 19 | 0,44 |
| makara 5 küre | 15° | evet | 0,119 | 2,25 | 14 / 113 | 88 | 0,78 |
| makara kapsül | 10° | evet | 0,230 | 1,20 | 31 / 99 | 46 | 0,49 |
| makara kapsül | 15° | evet | 0,096 | 2,87 | 14 / 113 | 78 | 0,84 |
| makara elipsoid, ccd 1e-6 (hatalı normal) | 10° | evet | 0,250 | 1,00 | 31 / 99 | 0 | 0,43 |
| makara elipsoid, ccd 1e-6 (hatalı normal) | 15° | evet | 0,177 | 1,16 | 23 / 113 | 35 | 0,63 |
| makara elipsoid, enkoder ön | 10° | evet | 0,253 | 1,00 | 31 / 99 | 0 | 0,43 |
| makara elipsoid, enkoder ön | 15° | evet | 0,088 | 2,65 | 14 / 113 | 89 | 0,77 |
| makara elipsoid, ccd 1e-6 (hatalı normal), enkoder ön | 10° | evet | 0,253 | 1,00 | 31 / 99 | 0 | 0,43 |
| makara elipsoid, ccd 1e-6 (hatalı normal), enkoder ön | 15° | evet | 0,166 | 1,16 | 24 / 113 | 34 | 0,63 |

## Enkoder arka (lastik; asıl) / ön (omni; duyarlılık: enkoder önde olsaydı) (µ 0,8)

Depoda enkoderler arka motorlarda (`planlama/adim3/pin-haritasi.md` 100–103: GPIO 18 / 17 sol arka JGB37, 16 / 15 sağ arka; 398 ve `elektrik.md` 495: ön motorlarda enkoder yok; firmware `pinler.h` aynı pinler). Bu dosyanın öbür bütün sayıları arka enkoderle; 23.11 ilk sürümü ön enkoder kabulüyle alınmıştı.

| varyant | enkoder | durma | yerinde w | yay v 0,25 + w 0,5: v / w | 90° s / aşma ° |
| --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | arka | 21kgcm | 0,893 | 0,232 / 0,369 | 2,1 / 5,5 |
| ONERI-ADAY | arka | 9kgcm | 0,706 | 0,153 / 0,059 | 2,8 / 5,2 |
| ONERI-ADAY | ön (duyarlılık) | 21kgcm | 1,048 | 0,223 / 0,410 | 1,9 / 6,3 |
| ONERI-ADAY | ön (duyarlılık) | 9kgcm | 0,689 | 0,154 / 0,059 | 2,8 / 4,7 |
| ONERI-MAKARA | arka | 21kgcm | 0,904 | 0,235 / 0,381 | 2,1 / 5,4 |
| ONERI-MAKARA | arka | 9kgcm | 0,805 | 0,158 / 0,080 | 2,5 / 6,1 |
| ONERI-MAKARA | ön (duyarlılık) | 21kgcm | 1,062 | 0,226 / 0,426 | 1,8 / 6,8 |
| ONERI-MAKARA | ön (duyarlılık) | 9kgcm | 0,776 | 0,158 / 0,081 | 2,5 / 5,3 |

Rampa çıkışı (rampa_parkuru boyutları: 2 m yatay + 1 m platform; rampa kipi, sonar kapalı, v 0,25, en çok 30 s; son 3 s'nin ortalaması; çevre oranı = teker çevre hızı / gövde hızı, 1 = kaymasız).

| varyant | enkoder | durma | eğim | çıktı (son x) | rampada v m/s | ön / arka çevre oranı | ön / arka tork / durma | ön / arka yük N (ön temassız adım %) | enkoder kilidi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ONERI-ADAY | arka | 21kgcm | 10° | evet (14,41) | 0,250 | 1,00 / 1,00 | 0,44 / 0,43 | 31 / 99 (0) | hayır/hayır |
| ONERI-ADAY | arka | 21kgcm | 15° | evet (14,43) | 0,121 | 2,23 / 1,00 | 0,41 / 0,78 | 14 / 113 (90) | hayır/hayır |
| ONERI-ADAY | arka | 9kgcm | 10° | hayır (12,91) | 0,030 | 1,01 / 1,00 | 1,02 / 1,02 | 31 / 99 (0) | hayır/hayır |
| ONERI-ADAY | arka | 9kgcm | 15° | hayır (12,19) | - | - / - | - / - | - / - (-) | evet/evet |
| ONERI-ADAY | ön (duyarlılık) | 21kgcm | 10° | evet (14,41) | 0,254 | 1,00 / 1,00 | 0,44 / 0,43 | 31 / 99 (0) | hayır/hayır |
| ONERI-ADAY | ön (duyarlılık) | 21kgcm | 15° | evet (14,44) | 0,103 | 2,45 / 1,00 | 0,41 / 0,78 | 14 / 113 (90) | hayır/hayır |
| ONERI-ADAY | ön (duyarlılık) | 9kgcm | 10° | hayır (12,91) | 0,030 | 1,01 / 1,00 | 1,02 / 1,02 | 31 / 99 (0) | hayır/hayır |
| ONERI-ADAY | ön (duyarlılık) | 9kgcm | 15° | hayır (12,19) | - | - / - | - / - | - / - (-) | hayır/hayır |
| ONERI-MAKARA | arka | 21kgcm | 10° | evet (14,42) | 0,250 | 1,00 / 1,00 | 0,44 / 0,43 | 31 / 99 (0) | hayır/hayır |
| ONERI-MAKARA | arka | 21kgcm | 15° | evet (14,42) | 0,120 | 2,25 / 1,00 | 0,41 / 0,78 | 14 / 113 (89) | hayır/hayır |
| ONERI-MAKARA | arka | 9kgcm | 10° | hayır (12,91) | 0,030 | 1,02 / 1,00 | 1,02 / 1,02 | 31 / 99 (0) | hayır/hayır |
| ONERI-MAKARA | arka | 9kgcm | 15° | hayır (12,19) | - | - / - | - / - | - / - (-) | evet/evet |
| ONERI-MAKARA | ön (duyarlılık) | 21kgcm | 10° | evet (14,41) | 0,253 | 1,00 / 1,00 | 0,44 / 0,43 | 31 / 99 (0) | hayır/hayır |
| ONERI-MAKARA | ön (duyarlılık) | 21kgcm | 15° | evet (14,41) | 0,088 | 2,65 / 1,00 | 0,42 / 0,77 | 14 / 113 (89) | hayır/hayır |
| ONERI-MAKARA | ön (duyarlılık) | 9kgcm | 10° | hayır (12,91) | 0,030 | 1,02 / 1,00 | 1,02 / 1,02 | 31 / 99 (0) | hayır/hayır |
| ONERI-MAKARA | ön (duyarlılık) | 9kgcm | 15° | hayır (12,19) | - | - / - | - / - | - / - (-) | hayır/hayır |

Enkoder arızası (ONERI-MAKARA, korumalı; test_enkoder_ariza.py kurgusu: v 0,10, 1 s sonra arıza, 3 s):

| enkoder | arıza (sol / sağ) | son 1 s m | açı ° | kilit | tespit ms |
| --- | --- | --- | --- | --- | --- |
| arka | - / - | 0,106 | -0,0 | hayır/hayır | - / - |
| arka | takili / takili | 0,082 | -0,0 | evet/evet | 550 / 550 |
| arka | ters / ters | 0,082 | 0,0 | evet/evet | 510 / 510 |
| arka | takili / - | 0,105 | -6,5 | evet/hayır | 550 / - |
| ön (duyarlılık) | - / - | 0,108 | 0,0 | hayır/hayır | - / - |
| ön (duyarlılık) | takili / takili | 0,082 | -0,0 | evet/evet | 550 / 550 |
| ön (duyarlılık) | ters / ters | 0,082 | 0,0 | evet/evet | 510 / 510 |
| ön (duyarlılık) | takili / - | 0,107 | -7,1 | evet/hayır | 550 / - |

## Enkoder arızası koruması: yanlış alarm

Tetiklenme: 114; bunların 10'i KASITLI arıza denemesi (beklenen tespit), öbürleri ölçümün adıyla.

- ONERI-ADAY eşik: sol teker, 4220 ms
- ONERI-ADAY eşik: sag teker, 4220 ms
- ONERI-ADAY eşik: sol teker, 4020 ms
- ONERI-ADAY eşik: sag teker, 4020 ms
- ONERI-ADAY eşik: sol teker, 3800 ms
- ONERI-ADAY eşik: sag teker, 3800 ms
- ONERI-ADAY eşik: sol teker, 3460 ms
- ONERI-ADAY eşik: sag teker, 3460 ms
- ONERI-MAKARA eşik: sol teker, 4200 ms
- ONERI-MAKARA eşik: sag teker, 4200 ms
- ONERI-MAKARA eşik: sol teker, 3980 ms
- ONERI-MAKARA eşik: sag teker, 3980 ms
- ONERI-MAKARA eşik: sol teker, 3640 ms
- ONERI-MAKARA eşik: sag teker, 3640 ms
- ONERI-MAKARA eşik: sol teker, 3400 ms
- ONERI-MAKARA eşik: sag teker, 3400 ms
- eşik duyarlılığı: sag teker, 5980 ms
- eşik duyarlılığı: sol teker, 6000 ms
- eşik duyarlılığı: sol teker, 4200 ms
- eşik duyarlılığı: sag teker, 4200 ms
- eşik duyarlılığı: sol teker, 3980 ms
- eşik duyarlılığı: sag teker, 3980 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4000 ms
- eşik duyarlılığı: sag teker, 4000 ms
- eşik duyarlılığı: sol teker, 3980 ms
- eşik duyarlılığı: sag teker, 4060 ms
- eşik duyarlılığı: sol teker, 5980 ms
- eşik duyarlılığı: sag teker, 6680 ms
- eşik duyarlılığı: sol teker, 4200 ms
- eşik duyarlılığı: sag teker, 4200 ms
- eşik duyarlılığı: sol teker, 3980 ms
- eşik duyarlılığı: sag teker, 3980 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4000 ms
- eşik duyarlılığı: sag teker, 4000 ms
- eşik duyarlılığı: sol teker, 4060 ms
- eşik duyarlılığı: sag teker, 4060 ms
- eşik duyarlılığı: sol teker, 6440 ms
- eşik duyarlılığı: sag teker, 6440 ms
- eşik duyarlılığı: sol teker, 4200 ms
- eşik duyarlılığı: sag teker, 4200 ms
- eşik duyarlılığı: sol teker, 4040 ms
- eşik duyarlılığı: sag teker, 4040 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4000 ms
- eşik duyarlılığı: sag teker, 4000 ms
- eşik duyarlılığı: sol teker, 4060 ms
- eşik duyarlılığı: sag teker, 4060 ms
- eşik duyarlılığı: sol teker, 5980 ms
- eşik duyarlılığı: sag teker, 5980 ms
- eşik duyarlılığı: sol teker, 4180 ms
- eşik duyarlılığı: sag teker, 4180 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4000 ms
- eşik duyarlılığı: sag teker, 4000 ms
- eşik duyarlılığı: sol teker, 3980 ms
- eşik duyarlılığı: sag teker, 3980 ms
- eşik duyarlılığı: sol teker, 6560 ms
- eşik duyarlılığı: sag teker, 6580 ms
- eşik duyarlılığı: sag teker, 6340 ms
- eşik duyarlılığı: sol teker, 6360 ms
- eşik duyarlılığı: sol teker, 4060 ms
- eşik duyarlılığı: sag teker, 4060 ms
- eşik duyarlılığı: sol teker, 4140 ms
- eşik duyarlılığı: sag teker, 4180 ms
- eşik duyarlılığı: sol teker, 4140 ms
- eşik duyarlılığı: sag teker, 4140 ms
- eşik duyarlılığı: sol teker, 3940 ms
- eşik duyarlılığı: sag teker, 3940 ms
- eşik duyarlılığı: sag teker, 3900 ms
- eşik duyarlılığı: sol teker, 3920 ms
- eşik duyarlılığı: sag teker, 5960 ms
- eşik duyarlılığı: sol teker, 6420 ms
- eşik duyarlılığı: sol teker, 4220 ms
- eşik duyarlılığı: sag teker, 4220 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4020 ms
- eşik duyarlılığı: sag teker, 4020 ms
- eşik duyarlılığı: sol teker, 4000 ms
- eşik duyarlılığı: sag teker, 4000 ms
- eşik duyarlılığı: sol teker, 4060 ms
- eşik duyarlılığı: sag teker, 4060 ms
- makara yatağı sürtünmesi: sol teker, 1640 ms
- makara yatağı sürtünmesi: sag teker, 1680 ms
- makara yatağı sürtünmesi: sol teker, 1520 ms
- makara yatağı sürtünmesi: sag teker, 1520 ms
- makara yatağı sürtünmesi: sol teker, 1520 ms
- makara yatağı sürtünmesi: sag teker, 1520 ms
- makara yatağı sürtünmesi: sol teker, 1520 ms
- makara yatağı sürtünmesi: sag teker, 1520 ms
- makara yatağı sürtünmesi: sol teker, 1520 ms
- makara yatağı sürtünmesi: sag teker, 1520 ms
- enkoder ONERI-ADAY arka 9kgcm 15° rampa: sol teker, 10700 ms
- enkoder ONERI-ADAY arka 9kgcm 15° rampa: sag teker, 10700 ms
- enkoder ONERI-MAKARA arka 9kgcm 15° rampa: sag teker, 10160 ms
- enkoder ONERI-MAKARA arka 9kgcm 15° rampa: sol teker, 10680 ms
- KASITLI enkoder arızası (beklenen tespit) arka takili/takili: sol teker, 2220 ms
- KASITLI enkoder arızası (beklenen tespit) arka takili/takili: sag teker, 2220 ms
- KASITLI enkoder arızası (beklenen tespit) arka ters/ters: sol teker, 2180 ms
- KASITLI enkoder arızası (beklenen tespit) arka ters/ters: sag teker, 2180 ms
- KASITLI enkoder arızası (beklenen tespit) arka takili/-: sol teker, 2220 ms
- KASITLI enkoder arızası (beklenen tespit) ön (duyarlılık) takili/takili: sol teker, 2220 ms
- KASITLI enkoder arızası (beklenen tespit) ön (duyarlılık) takili/takili: sag teker, 2220 ms
- KASITLI enkoder arızası (beklenen tespit) ön (duyarlılık) ters/ters: sol teker, 2180 ms
- KASITLI enkoder arızası (beklenen tespit) ön (duyarlılık) ters/ters: sag teker, 2180 ms
- KASITLI enkoder arızası (beklenen tespit) ön (duyarlılık) takili/-: sol teker, 2220 ms
