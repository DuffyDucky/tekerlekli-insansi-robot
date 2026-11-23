# Öneri firmware + ön omni (Y0f, `kod/fizik/olcum_oneri.py`)

**VARSAYIM**, bugünkü robot değil (V0 hariç). ONERI = öneri firmware (dal `oneri/donus-omni`, `motorlar.cpp`: PI kp 4, ki 20, integral sınırı 0,6, w girişi 1,0, 20 ms döngü, enkoder tik farkından hız, enkoder arızası koruması; masada PI açıldıktan sonraki durum: dalda PI ilk yüklemede kapalı) + ön iki teker omni (makara yanal sürtünmesi 0,05, TAHMİN). ONERI-T = öneri firmware + bugünkü lastikler. ONERI-ADAY = ONERI, ön teker aday omni ölçüleriyle (Ø127 x 29, 480 g; seçilmedi). Öneri varyantlarında enkoder arka (lastik) tekerde (pin planı); ön enkoder en altta duyarlılık. Başsız, protokol üzerinden; 3 s sonra 1,5 s ortalaması. Tork / sürekli: en yüklü tekerin ortalama torku / (durma x 0,3, TAHMİN).

## Dönüş

| varyant | durma | µ | yerinde w (komut 0,5 / 1 / 1,5) | tork / sürekli (w 1) | yay v 0,25 + w 0,5: w / yarıçap m | yay + w 1: w / yarıçap m | 90°: s / aşma ° / tepe oranı | kolon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

90°: yön 10 ms'de bir denetlenir, 90°'yi geçince `dur`; aşma = `dur` sonrası fren (+ en çok bir 10 ms dilim). 200 ms denetimle aşmaya ortalama ≈ 6° daha eklenir (ilk sürümün 8–15°'si buydu).
| V0 | 21kgcm | 0,5 | 0,001 / 0,001 / 0,001 | 2,0 | 0,001 / - | 0,001 / - | ulaşmadı (20 s) | başarısız (0 / 3) |
| V0 | 21kgcm | 0,8 | 0,001 / 0,001 / 0,001 | 2,0 | 0,001 / - | 0,001 / - | ulaşmadı (20 s) | başarısız (0 / 3) |
| V0 | 9kgcm | 0,5 | 0,000 / 0,001 / 0,001 | 2,0 | 0,000 / - | 0,000 / - | ulaşmadı (20 s) | başarısız (0 / 3) |
| V0 | 9kgcm | 0,8 | 0,000 / 0,001 / 0,001 | 2,0 | 0,000 / - | 0,000 / - | ulaşmadı (20 s) | başarısız (0 / 3) |
| ONERI | 21kgcm | 0,5 | 0,459 / 0,923 / 0,923 | 1,0 | 0,422 / 0,57 | 0,648 / 0,29 | 2,0 / 5,3 / 1,02 | başarılı, 10,8 s |
| ONERI | 21kgcm | 0,8 | 0,436 / 0,892 / 0,892 | 1,1 | 0,373 / 0,62 | 0,589 / 0,32 | 2,1 / 5,5 / 1,04 | başarılı, 11,0 s |
| ONERI | 9kgcm | 0,5 | 0,458 / 0,880 / 0,880 | 2,1 | 0,156 / 1,13 | 0,327 / 0,42 | 2,3 / 6,1 / 1,02 | başarılı, 11,6 s |
| ONERI | 9kgcm | 0,8 | 0,432 / 0,742 / 0,742 | 2,4 | 0,114 / 1,47 | 0,199 / 0,64 | 2,6 / 5,1 / 1,02 | başarılı, 12,6 s |
| ONERI-T | 21kgcm | 0,5 | 0,060 / 0,095 / 0,095 | 2,0 | 0,001 / - | 0,018 / 8,55 | 17,9 / 0,5 / 2,64 | başarılı, 43,9 s |
| ONERI-T | 21kgcm | 0,8 | 0,001 / 0,085 / 0,085 | 2,3 | 0,001 / - | 0,001 / - | 18,7 / 0,4 / 2,37 | başarılı, 56,7 s |
| ONERI-T | 9kgcm | 0,5 | 0,000 / 0,001 / 0,001 | 2,0 | 0,001 / - | 0,001 / - | ulaşmadı (20 s) | başarısız (0 / 3) |
| ONERI-T | 9kgcm | 0,8 | 0,000 / 0,001 / 0,001 | 2,0 | 0,001 / - | 0,001 / - | ulaşmadı (20 s) | başarısız (0 / 3) |
| ONERI-ADAY | 21kgcm | 0,5 | 0,459 / 0,926 / 0,926 | 1,1 | 0,420 / 0,57 | 0,650 / 0,30 | 2,0 / 5,7 / 1,02 | başarılı, 10,8 s |
| ONERI-ADAY | 21kgcm | 0,8 | 0,435 / 0,893 / 0,893 | 1,2 | 0,369 / 0,63 | 0,585 / 0,32 | 2,1 / 5,5 / 1,03 | başarılı, 10,9 s |
| ONERI-ADAY | 9kgcm | 0,5 | 0,456 / 0,861 / 0,861 | 2,3 | 0,139 / 1,24 | 0,302 / 0,45 | 2,4 / 6,8 / 1,02 | başarılı, 11,8 s |
| ONERI-ADAY | 9kgcm | 0,8 | 0,419 / 0,706 / 0,706 | 2,5 | 0,059 / 2,60 | 0,165 / 0,76 | 2,8 / 5,2 / 1,03 | başarılı, 13,8 s |

## Yan etkiler (µ 0,8, 21 kg·cm)

Model sol-sağ simetrik: düz gidiş ve frende yön sapması bozucu olmadan 0; yön kararlılığını yanal itme gösterir.

| varyant | düz 6 s yol m | yanal itme 10 N 0,3 s: yan m / yön ° | dur (0,39'dan) m | acil stop m | 5° yan eğim duruş: yan m / yön ° | 5° yan eğim düz 5 s: yan m / yön ° |
| --- | --- | --- | --- | --- | --- | --- |
| V0 | 1,45 | 0,000 / 0,0 | 0,070 | 0,228 | -0,000 / 0,0 | -0,000 / 0,0 |
| ONERI | 1,52 | 0,002 / 0,0 | 0,046 | 0,222 | -0,009 / -2,7 | -0,050 / -2,1 |
| ONERI-T | 1,52 | 0,000 / 0,0 | 0,046 | 0,222 | -0,000 / 0,0 | -0,000 / 0,0 |
| ONERI-ADAY | 1,52 | 0,002 / 0,0 | 0,046 | 0,221 | -0,009 / -2,6 | -0,049 / -2,1 |

## Rampa (rampa kipi, sonar kapalı, µ 0,8, 21 kg·cm): `dur` sonrası süzülme bittikten sonra 5 s

| varyant | eğim | ortasına ulaştı | rampada hız m/s | 5 s geri kayma m | tutuyor |
| --- | --- | --- | --- | --- | --- |
| V0 | 5° | evet | 0,329 | 0,168 | hayır |
| V0 | 10° | evet | 0,263 | 0,488 | hayır |
| ONERI | 5° | evet | 0,328 | 0,169 | hayır |
| ONERI | 10° | evet | 0,261 | 0,488 | hayır |
| ONERI-T | 5° | evet | 0,329 | 0,168 | hayır |
| ONERI-T | 10° | evet | 0,263 | 0,488 | hayır |
| ONERI-ADAY | 5° | evet | 0,327 | 0,175 | hayır |
| ONERI-ADAY | 10° | evet | 0,259 | 0,507 | hayır |

## Eşik (sonar kapalı, µ 0,8)

Düşük hızda eşik kazancı PI'dan (lastikli ONERI-T de geçiyor). Ön omni küre olarak modellendi (sürekli çember): omni makaralarıyla eşik geçişi modellenmedi, masada denenmeli.

| varyant | durma | v komutu | 5 mm | 10 mm | 15 mm |
| --- | --- | --- | --- | --- | --- |
| V0 | 21 kg·cm | 0,20 | geçti | ön çıktı | geçmedi |
| V0 | 21 kg·cm | 0,39 | geçti | geçti | geçti |
| V0 | 9 kg·cm | 0,20 | geçmedi | geçmedi | geçmedi |
| V0 | 9 kg·cm | 0,39 | geçti | ön çıktı | geçmedi |
| ONERI | 21 kg·cm | 0,20 | geçti | geçti | geçti |
| ONERI | 21 kg·cm | 0,39 | geçti | geçti | geçti |
| ONERI | 9 kg·cm | 0,20 | geçti | geçmedi | geçmedi |
| ONERI | 9 kg·cm | 0,39 | geçti | ön çıktı | geçmedi |
| ONERI-T | 21 kg·cm | 0,20 | geçti | geçti | geçti |
| ONERI-T | 21 kg·cm | 0,39 | geçti | geçti | geçti |
| ONERI-T | 9 kg·cm | 0,20 | geçti | geçmedi | geçmedi |
| ONERI-T | 9 kg·cm | 0,39 | geçti | ön çıktı | geçmedi |
| ONERI-ADAY | 21 kg·cm | 0,20 | geçti | geçti | geçti |
| ONERI-ADAY | 21 kg·cm | 0,39 | geçti | geçti | geçti |
| ONERI-ADAY | 9 kg·cm | 0,20 | geçti | geçmedi | geçmedi |
| ONERI-ADAY | 9 kg·cm | 0,39 | geçti | ön çıktı | geçmedi |

## Enkoder arızası koruması: yanlış alarm

Koruma (PI düzeltme payı + makullük denetimi, `motorlar.cpp` DUZELTME_* / KUSKU_*) bu dosyadaki bütün ölçümlerde (kalkış, dönüş, 9 kg·cm doyum, rampa, eşik, yan eğim, duyarlılık, makara taraması) izlendi. Tetiklenme: 54.

- ONERI eşik: sol teker, 4200 ms
- ONERI eşik: sag teker, 4200 ms
- ONERI eşik: sol teker, 4000 ms
- ONERI eşik: sag teker, 4000 ms
- ONERI eşik: sol teker, 3680 ms
- ONERI eşik: sag teker, 3700 ms
- ONERI eşik: sol teker, 3440 ms
- ONERI eşik: sag teker, 3440 ms
- ONERI-T 21kgcm µ 0.8 dönüş / yay / 90° / kolon: sol teker, 1540 ms
- ONERI-T 21kgcm µ 0.8 dönüş / yay / 90° / kolon: sag teker, 1540 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sol teker, 1380 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sag teker, 1380 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.5 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sol teker, 1380 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sag teker, 1380 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sol teker, 1520 ms
- ONERI-T 9kgcm µ 0.8 dönüş / yay / 90° / kolon: sag teker, 1520 ms
- ONERI-T eşik: sol teker, 4220 ms
- ONERI-T eşik: sag teker, 4220 ms
- ONERI-T eşik: sol teker, 4000 ms
- ONERI-T eşik: sag teker, 4000 ms
- ONERI-T eşik: sol teker, 3860 ms
- ONERI-T eşik: sag teker, 3860 ms
- ONERI-T eşik: sol teker, 3400 ms
- ONERI-T eşik: sag teker, 3400 ms
- ONERI-ADAY eşik: sol teker, 4220 ms
- ONERI-ADAY eşik: sag teker, 4220 ms
- ONERI-ADAY eşik: sol teker, 4020 ms
- ONERI-ADAY eşik: sag teker, 4020 ms
- ONERI-ADAY eşik: sol teker, 3800 ms
- ONERI-ADAY eşik: sag teker, 3800 ms
- ONERI-ADAY eşik: sol teker, 3460 ms
- ONERI-ADAY eşik: sag teker, 3460 ms
- duyarlılık: enkoder önde olsaydı: sol teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sag teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sol teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sag teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sol teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sag teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sol teker, 1520 ms
- duyarlılık: enkoder önde olsaydı: sag teker, 1520 ms

## Düz gidiş, aks uyumu (v 0,25, µ 0,8, 21 kg·cm; 4 s sonra 2 s)

Aday omni Ø127, arka lastik Ø125; bir yandaki iki motor aynı PWM'i alır (aynı BTS7960), firmware iki aksı ayrı süremez. Çevre oranı = teker çevre hızı / gövde hızı (1 = kaymasız).

| durum | v m/s | ön aks |tork| N·m | arka aks |tork| N·m | ön çevre oranı | arka çevre oranı | 6 s'de yön ° |
| --- | --- | --- | --- | --- | --- | --- |
| V0 | 0,242 | 0,171 | 0,171 | 1,000 | 1,000 | 0,00 |
| ONERI | 0,250 | 0,171 | 0,171 | 1,000 | 1,000 | 0,00 |
| ONERI-ADAY | 0,250 | 0,185 | 0,165 | 1,000 | 1,000 | -0,00 |
| acik cevrim + aday omni | 0,243 | 0,186 | 0,166 | 1,000 | 1,000 | -0,00 |

## Statik devrilme payı (geometri: temas noktaları ve AM; karşılaştırma için)

| varyant | kütle kg | AM x / y / z mm | ön temas y mm | ileri ° | geri ° | yana ° |
| --- | --- | --- | --- | --- | --- | --- |
| V0 | 26,28 | -10,5 / 0,0 / 520,5 | 245,0 | 20,6 | 18,5 | 25,2 |
| ONERI | 26,28 | -10,4 / 0,0 / 520,5 | 216,0 | 20,6 | 18,5 | 23,9 |
| ONERI-ADAY | 26,88 | -7,4 / 0,0 / 510,6 | 201,5 | 20,6 | 19,2 | 23,5 |

## Makara yanal sürtünmesi taraması (ONERI-ADAY, yerinde w komutu 1)

Üretici değeri yok (rulmanlı / pirinç borulu sürüm). Yanal kuvvet = katsayı x ortalama teker yükü (eklemde sabit Coulomb; masada yüklü tekeri yana çekme ölçümüyle karşılaştırılacak sayı).

| katsayı | yanal kuvvet N / teker | 21 kg·cm µ 0,5 | 21 kg·cm µ 0,8 | 9 kg·cm µ 0,5 | 9 kg·cm µ 0,8 |
| --- | --- | --- | --- | --- | --- |
| 0,00 | 0,0 | 0,97 (0,8) | 0,94 (0,9) | 0,96 (1,6) | 0,93 (2,0) |
| 0,05 | 3,3 | 0,93 (1,1) | 0,89 (1,2) | 0,86 (2,3) | 0,71 (2,5) |
| 0,10 | 6,6 | 0,90 (1,4) | 0,86 (1,5) | 0,53 (2,8) | 0,40 (3,0) |
| 0,15 | 9,9 | 0,87 (1,6) | 0,83 (1,7) | 0,21 (3,3) | 0,17 (3,3) |
| 0,20 | 13,2 | 0,85 (1,8) | 0,80 (2,0) | 0,19 (3,3) | 0,17 (3,3) |
| 0,30 | 19,8 | 0,79 (2,2) | 0,68 (2,4) | 0,19 (3,3) | 0,17 (3,3) |
| 0,40 | 26,4 | 0,65 (2,3) | 0,50 (2,7) | 0,19 (3,3) | 0,17 (3,3) |
| 0,60 | 39,6 | 0,57 (2,3) | 0,46 (2,7) | 0,19 (3,3) | 0,17 (3,3) |

Hücre: gerçekleşen w rad/s (tork / sürekli).

## Duyarlılık (ONERI, µ 0,8, 21 kg·cm; yerinde w komutu 1 ve 5° yan eğimde 5 s düz gidiş)

| ayar | yerinde w | w std | tork / sürekli | yan eğim kayma m / yön ° |
| --- | --- | --- | --- | --- |
| ana (makara 0,05, kp 4, ki 20) | 0,892 | 0,009 | 1,1 | -0,050 / -2,1 |
| makara yanal sürtünmesi 0 (ideal) | 0,934 | 0,008 | 0,8 | -0,052 / -2,2 |
| makara yanal sürtünmesi 0,15 | 0,829 | 0,012 | 1,6 | -0,050 / -2,1 |
| makara yanal sürtünmesi 0,30 | 0,769 | 0,012 | 2,0 | -0,050 / -2,1 |
| kp 2, ki 10 | 0,890 | 0,009 | 1,1 | -0,065 / -3,2 |
| kp 8, ki 40 | 0,894 | 0,013 | 1,1 | -0,036 / -1,3 |
| kp 4, ki 0 (yalnız P) | 0,767 | 0,008 | 1,1 | -0,095 / -6,0 |
| integral sınırı 0,3 (0.5.0 değeri) | 0,892 | 0,009 | 1,1 | -0,050 / -2,1 |
| enkoder arızası koruması yok | 0,892 | 0,009 | 1,1 | -0,050 / -2,1 |
| enkoder önde olsaydı (omni teker) | 0,968 | 0,008 | 1,1 | -0,050 / -2,2 |
| enkoder çözünürlüğü yarı (990 tik/tur) | 0,892 | 0,010 | 1,1 | - |
| dt 0,5 ms | 0,878 | 0,007 | 1,1 | -0,050 / -2,1 |
| temas solref 0,002 | 0,916 | 0,014 | 1,0 | -0,037 / -1,7 |
| temas solref 0,008 | 0,873 | 0,007 | 1,1 | -0,066 / -2,5 |
| piramit koni | 0,907 | 0,015 | 1,0 | - |
| noslip 5 | 0,894 | 0,009 | 1,1 | - |
| impratio 10 | 0,891 | 0,009 | 1,1 | - |
| ADAY, firmware TEKER_CAPI_M 0,125 (ana) | 0,893 | 0,009 | 1,2 | -0,049 / -2,1 |
| ADAY, firmware TEKER_CAPI_M 0,127 | 0,879 | 0,009 | 1,2 | - |
| ADAY, enkoder önde olsaydı (omni teker) | 1,048 | 0,009 | 1,3 | -0,052 / -2,3 |

## Duyarlılık: enkoder önde olsaydı (yerinde w komutu 1, 90°)

Bu dosyanın öbür bütün sayıları öneri varyantlarında enkoder ARKA (lastik) tekerde (pin planı: `planlama/adim3/pin-haritasi.md` 100–103; ön motorlarda enkoder yok). Ön (omni) enkoder bugünkü pin planında geçerli değil; 23.11'e dek bu dosyanın ana tablosu bu kabulle alınmıştı.

| varyant | durma | µ | yerinde w (enkoder ön) | tork / sürekli | 90°: s / aşma ° |
| --- | --- | --- | --- | --- | --- |
| ONERI | 21kgcm | 0,5 | 0,977 | 1,0 | 1,9 / 5,7 |
| ONERI | 21kgcm | 0,8 | 0,968 | 1,1 | 2,0 / 5,0 |
| ONERI | 9kgcm | 0,5 | 0,860 | 2,1 | 2,3 / 6,0 |
| ONERI | 9kgcm | 0,8 | 0,720 | 2,4 | 2,6 / 4,4 |
| ONERI-T | 21kgcm | 0,5 | 0,091 | 2,0 | 18,5 / 0,3 |
| ONERI-T | 21kgcm | 0,8 | 0,081 | 2,3 | 19,9 / 0,4 |
| ONERI-T | 9kgcm | 0,5 | 0,001 | 2,0 | - |
| ONERI-T | 9kgcm | 0,8 | 0,001 | 2,0 | - |
| ONERI-ADAY | 21kgcm | 0,5 | 1,058 | 1,1 | 1,8 / 5,9 |
| ONERI-ADAY | 21kgcm | 0,8 | 1,048 | 1,3 | 1,9 / 6,3 |
| ONERI-ADAY | 9kgcm | 0,5 | 0,843 | 2,3 | 2,4 / 6,1 |
| ONERI-ADAY | 9kgcm | 0,8 | 0,689 | 2,5 | 2,8 / 4,7 |
