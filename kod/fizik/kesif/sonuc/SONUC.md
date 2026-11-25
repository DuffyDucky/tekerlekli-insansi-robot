# Keşif beyni: ölçüm sonuçları

Bu dosya `py -3 -m kesif.kos rapor` ile CSV'lerden üretilir; elle düzeltilmez. Benzetici: `benzet2b.py` (2B, dönen tarama çarpıklığı açık, %14 dönüş fazlası + gürültü varsayılan). Hakem: `labirent.hakem`.

## İlk tur: strateji x labirent boyu (5 tohum, %14 dönüş hatası)

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kesif 13x13 | 15 | 14/15 | 480.2 | 765 | 104.0 | 0.07 | 1170 | 0.46 | 0.56 |
| kesif 17x17 | 15 | 13/15 | 514.2 | 692 | 117.8 | 0.00 | 1104 | 0.74 | 0.48 |
| kesif 5x5 | 5 | 5/5 | 63.2 | 68 | 12.1 | 0.00 | 1465 | 0.06 | 1.00 |
| kesif 7x7 | 5 | 5/5 | 213.5 | 233 | 42.0 | 0.00 | 1381 | 0.09 | 0.99 |
| kesif 9x9 | 15 | 15/15 | 243.7 | 319 | 50.8 | 0.07 | 1359 | 0.22 | 0.82 |
| rastgele 13x13 | 15 | 0/15 | - | - | 72.0 | 0.93 | -362 | 0.05 | - |
| rastgele 17x17 | 15 | 0/15 | - | - | 72.0 | 0.93 | -369 | 0.05 | - |
| rastgele 5x5 | 5 | 2/5 | 359.5 | 365 | 54.9 | 0.40 | 396 | 0.03 | - |
| rastgele 7x7 | 5 | 0/5 | - | - | 37.7 | 0.80 | -471 | 0.02 | - |
| rastgele 9x9 | 15 | 0/15 | - | - | 71.8 | 0.80 | -340 | 0.05 | - |
| sag_duvar 13x13 | 15 | 3/15 | 675.5 | 707 | 114.2 | 0.00 | 295 | 0.19 | - |
| sag_duvar 17x17 | 15 | 0/15 | - | - | 118.0 | 0.00 | 80 | 0.28 | - |
| sag_duvar 5x5 | 5 | 5/5 | 189.2 | 205 | 31.8 | 0.00 | 1395 | 0.05 | - |
| sag_duvar 7x7 | 5 | 4/5 | 449.2 | 578 | 76.0 | 0.00 | 1014 | 0.11 | - |
| sag_duvar 9x9 | 15 | 5/15 | 550.3 | 767 | 103.7 | 0.00 | 512 | 0.11 | - |

### Labirent bazında (kesif)

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| labirent_13x13_t1 | 5 | 5/5 | 326.6 | 338 | 66.2 | 0.00 | 1319 | 0.49 | 0.61 |
| labirent_13x13_t2 | 5 | 4/5 | 328.4 | 337 | 89.2 | 0.20 | 1111 | 0.26 | 0.61 |
| labirent_13x13_t3 | 5 | 5/5 | 755.4 | 765 | 156.5 | 0.00 | 1080 | 0.64 | 0.46 |
| labirent_17x17_t1 | 5 | 5/5 | 391.1 | 408 | 80.3 | 0.00 | 1283 | 0.72 | 0.48 |
| labirent_17x17_t2 | 5 | 5/5 | 568.9 | 580 | 118.4 | 0.00 | 1184 | 0.63 | 0.54 |
| labirent_17x17_t3 | 5 | 3/5 | 628.1 | 692 | 154.6 | 0.00 | 845 | 0.86 | 0.41 |
| labirent_5x5_t1 | 5 | 5/5 | 63.2 | 68 | 12.1 | 0.00 | 1465 | 0.06 | 1.00 |
| labirent_7x7_t1 | 5 | 5/5 | 213.5 | 233 | 42.0 | 0.00 | 1381 | 0.09 | 0.99 |
| labirent_9x9_t1 | 5 | 5/5 | 265.6 | 318 | 54.0 | 0.20 | 1337 | 0.18 | 0.85 |
| labirent_9x9_t2 | 5 | 5/5 | 151.5 | 259 | 31.9 | 0.00 | 1416 | 0.21 | 0.87 |
| labirent_9x9_t3 | 5 | 5/5 | 314.0 | 319 | 66.6 | 0.00 | 1326 | 0.28 | 0.74 |

### Adım süresi (kesif, bu makinede, tek iş parçacığı, düşük öncelik)

- tarama işleme (SLAM + gerekiyorsa plan) ort 9.1 ms, p95 ort 16.1 ms, en kötü 101 ms
- planlama ort 21.9 ms, en kötü 89 ms

### Başvuru (sahne JSON'undan; beyin görmez): alt sınırlar, 0,25 m/s, dönüşsüz

| sahne | çözüm (m) | çözüm süresi (s) | sağ el hücre | ideal sağ el (s) | sol el hücre |
| --- | --- | --- | --- | --- | --- |
| labirent_5x5_t1 | 14.3 | 57 | 11 | 57 | 25 |
| labirent_7x7_t1 | 32.5 | 130 | 53 | 276 | 45 |
| labirent_9x9_t1 | 40.3 | 161 | 35 | 182 | 63 |
| labirent_9x9_t2 | 29.9 | 120 | 23 | 120 | 61 |
| labirent_9x9_t3 | 55.9 | 224 | 77 | 400 | 51 |
| labirent_13x13_t1 | 76.7 | 307 | 229 | 1191 | 109 |
| labirent_13x13_t2 | 71.5 | 286 | 217 | 1128 | 111 |
| labirent_13x13_t3 | 144.3 | 577 | 159 | 827 | 161 |
| labirent_17x17_t1 | 92.3 | 369 | 381 | 1981 | 197 |
| labirent_17x17_t2 | 118.3 | 473 | 281 | 1461 | 137 |
| labirent_17x17_t3 | 131.3 | 525 | 153 | 796 | 413 |

## Odometri duyarlılığı (kesif; dönüş fazlası 0 / %14 / %25)

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.00 13x13 | 15 | 11/15 | 523.2 | 806 | 128.2 | 0.27 | 964 | 0.48 | 0.59 |
| 0.00 17x17 | 15 | 11/15 | 504.0 | 745 | 126.2 | 0.07 | 992 | 0.67 | 0.46 |
| 0.00 5x5 | 5 | 5/5 | 61.9 | 68 | 12.1 | 0.00 | 1466 | 0.06 | 0.99 |
| 0.00 7x7 | 5 | 5/5 | 209.7 | 242 | 42.0 | 0.00 | 1383 | 0.13 | 0.94 |
| 0.00 9x9 | 15 | 15/15 | 253.3 | 340 | 52.7 | 0.07 | 1354 | 0.22 | 0.80 |
| 0.14 13x13 | 15 | 14/15 | 480.2 | 765 | 104.0 | 0.07 | 1170 | 0.46 | 0.56 |
| 0.14 17x17 | 15 | 13/15 | 514.2 | 692 | 117.8 | 0.00 | 1104 | 0.74 | 0.48 |
| 0.14 5x5 | 5 | 5/5 | 63.2 | 68 | 12.1 | 0.00 | 1465 | 0.06 | 1.00 |
| 0.14 7x7 | 5 | 5/5 | 213.5 | 233 | 42.0 | 0.00 | 1381 | 0.09 | 0.99 |
| 0.14 9x9 | 15 | 15/15 | 243.7 | 319 | 50.8 | 0.07 | 1359 | 0.22 | 0.82 |
| 0.25 13x13 | 15 | 12/15 | 514.8 | 840 | 120.5 | 0.27 | 1022 | 0.48 | 0.55 |
| 0.25 17x17 | 15 | 12/15 | 518.4 | 702 | 122.5 | 0.07 | 1041 | 0.64 | 0.49 |
| 0.25 5x5 | 5 | 5/5 | 62.8 | 68 | 12.1 | 0.00 | 1465 | 0.07 | 1.00 |
| 0.25 7x7 | 5 | 5/5 | 208.2 | 229 | 41.6 | 0.00 | 1384 | 0.11 | 0.97 |
| 0.25 9x9 | 15 | 15/15 | 241.1 | 317 | 50.3 | 0.07 | 1362 | 0.20 | 0.82 |

## Hafızalı koşu (aynı labirent, ilk koşunun haritası ve çıkış pozu)

| sahne | n (ilk başarılı) | ilk süre ort | hafızalı süre ort | hafızalı başarı | kazanç |
| --- | --- | --- | --- | --- | --- |
| labirent_13x13_t1 | 3/3 | 328.4 | 306.7 | 3/3 | 7% |
| labirent_13x13_t2 | 2/3 | 324.2 | 288.7 | 2/2 | 11% |
| labirent_13x13_t3 | 3/3 | 751.7 | 594.5 | 3/3 | 21% |
| labirent_17x17_t1 | 3/3 | 394.2 | 369.4 | 3/3 | 6% |
| labirent_17x17_t2 | 3/3 | 566.9 | 487.0 | 3/3 | 14% |
| labirent_17x17_t3 | 2/3 | 661.5 | 537.5 | 2/2 | 19% |
| labirent_5x5_t1 | 3/3 | 66.0 | 57.3 | 3/3 | 13% |
| labirent_7x7_t1 | 3/3 | 229.4 | 131.2 | 3/3 | 43% |
| labirent_9x9_t1 | 3/3 | 257.6 | 162.4 | 3/3 | 37% |
| labirent_9x9_t2 | 3/3 | 168.9 | 121.2 | 3/3 | 28% |
| labirent_9x9_t3 | 3/3 | 314.9 | 231.9 | 3/3 | 26% |

## Ayar: sınama kümesinde sonra (önce = ilk turun kesif satırları; arama eğitim labirentlerinde)

- önce: başarı 52/55, puan ort 1249.6; sonra: başarı 52/55, puan ort 1265.4

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aday03 13x13 | 15 | 15/15 | 509.4 | 879 | 126.9 | 0.07 | 1212 | 0.43 | 0.57 |
| aday03 17x17 | 15 | 12/15 | 420.8 | 543 | 130.3 | 0.00 | 1090 | 0.54 | 0.47 |
| aday03 5x5 | 5 | 5/5 | 55.2 | 60 | 12.3 | 0.00 | 1469 | 0.08 | 1.00 |
| aday03 7x7 | 5 | 5/5 | 175.6 | 194 | 41.6 | 0.20 | 1387 | 0.13 | 0.94 |
| aday03 9x9 | 15 | 15/15 | 205.2 | 261 | 52.9 | 0.00 | 1386 | 0.19 | 0.82 |

## MuJoCo (gezinme.duzenek) ile 2B benzetici: aynı labirent ve tohum (kesif)

MuJoCo'da tohum LiDAR gürültüsünü değiştirir; odometri hatası düzeneğin fiziğinden gelir (beynin öğrendiği dönüş ölçeği k_don ort 0.875). Beyin ön bilgisiz kurulur (`KesifBeyni()`).

| sahne | tohum | MuJoCo durum | süre | çarpma | poz hata maks | doğru duvar | 2B durum | 2B süre | 2B poz hata maks | 2B doğru duvar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| labirent_13x13_t1 | 0 | basari | 368.55 | 0 | 0.676 | 0.5538 | basari | 328.2 | 0.441 | 0.5951 |
| labirent_13x13_t1 | 1 | basari | 384.1 | 0 | 0.196 | 0.7754 | basari | 326.35 | 0.328 | 0.6416 |
| labirent_13x13_t1 | 2 | basari | 361.8 | 0 | 0.317 | 0.6949 | basari | 330.8 | 0.359 | 0.6334 |
| labirent_13x13_t2 | 0 | fail_sure | 900.0 | 0 | 0.263 | 0.7793 | fail_sure | 900.0 | 0.194 | 0.7929 |
| labirent_13x13_t2 | 1 | basari | 360.8 | 0 | 0.575 | 0.4499 | basari | 334.55 | 0.292 | 0.4993 |
| labirent_13x13_t2 | 2 | fail_sure | 900.0 | 0 | 0.335 | 0.7559 | basari | 313.8 | 0.331 | 0.5001 |
| labirent_13x13_t3 | 0 | basari | 835.5 | 0 | 0.81 | 0.4144 | basari | 735.3 | 0.698 | 0.4445 |
| labirent_13x13_t3 | 1 | basari | 868.35 | 0 | 0.569 | 0.5018 | basari | 764.1 | 0.699 | 0.4314 |
| labirent_13x13_t3 | 2 | basari | 856.45 | 0 | 0.761 | 0.4176 | basari | 755.6 | 0.562 | 0.491 |
| labirent_17x17_t1 | 0 | basari | 424.0 | 0 | 1.103 | 0.4054 | basari | 389.75 | 0.659 | 0.5053 |
| labirent_17x17_t1 | 1 | basari | 447.55 | 0 | 0.26 | 0.6487 | basari | 384.3 | 0.578 | 0.5023 |
| labirent_17x17_t1 | 2 | basari | 423.9 | 0 | 0.462 | 0.5616 | basari | 408.5 | 0.57 | 0.4769 |
| labirent_17x17_t2 | 0 | basari | 636.8 | 0 | 0.816 | 0.4762 | basari | 572.55 | 0.496 | 0.7375 |
| labirent_17x17_t2 | 1 | basari | 639.9 | 0 | 0.87 | 0.4398 | basari | 564.65 | 0.543 | 0.5199 |
| labirent_17x17_t2 | 2 | basari | 620.4 | 0 | 0.651 | 0.4682 | basari | 563.55 | 0.821 | 0.4306 |
| labirent_17x17_t3 | 0 | fail_sure | 900.0 | 0 | 0.78 | 0.3388 | fail_sure | 900.0 | 1.03 | 0.3321 |
| labirent_17x17_t3 | 1 | fail_sure | 900.0 | 0 | 0.908 | 0.3107 | basari | 630.75 | 0.838 | 0.4404 |
| labirent_17x17_t3 | 2 | fail_sure | 900.0 | 0 | 0.798 | 0.3233 | basari | 692.15 | 0.968 | 0.4525 |
| labirent_5x5_t1 | 0 | basari | 68.5 | 0 | 0.06 | 1.0 | basari | 67.85 | 0.08 | 1.0 |
| labirent_5x5_t1 | 1 | basari | 66.2 | 0 | 0.054 | 1.0 | basari | 62.4 | 0.023 | 1.0 |
| labirent_5x5_t1 | 2 | basari | 71.8 | 0 | 0.028 | 1.0 | basari | 67.65 | 0.088 | 0.988 |
| labirent_7x7_t1 | 0 | basari | 255.8 | 0 | 0.08 | 1.0 | basari | 230.4 | 0.092 | 0.9923 |
| labirent_7x7_t1 | 1 | basari | 150.15 | 0 | 0.104 | 0.9887 | basari | 228.7 | 0.091 | 0.9985 |
| labirent_7x7_t1 | 2 | basari | 242.7 | 0 | 0.13 | 0.9772 | basari | 229.1 | 0.089 | 0.9911 |
| labirent_9x9_t1 | 0 | basari | 302.95 | 0 | 0.157 | 0.9689 | basari | 178.5 | 0.156 | 0.8271 |
| labirent_9x9_t1 | 1 | basari | 310.5 | 0 | 0.13 | 0.9553 | basari | 276.5 | 0.185 | 0.8409 |
| labirent_9x9_t1 | 2 | basari | 295.95 | 0 | 0.173 | 0.7965 | basari | 317.95 | 0.2 | 0.8413 |
| labirent_9x9_t2 | 0 | basari | 127.45 | 0 | 0.17 | 0.9423 | basari | 259.4 | 0.201 | 0.8785 |
| labirent_9x9_t2 | 1 | basari | 286.7 | 0 | 0.223 | 0.8816 | basari | 126.0 | 0.224 | 0.8214 |
| labirent_9x9_t2 | 2 | basari | 149.4 | 0 | 0.269 | 0.8312 | basari | 121.45 | 0.194 | 0.8896 |
| labirent_9x9_t3 | 0 | basari | 325.3 | 0 | 0.299 | 0.7352 | basari | 312.6 | 0.309 | 0.7168 |
| labirent_9x9_t3 | 1 | basari | 351.85 | 0 | 0.353 | 0.6818 | basari | 318.55 | 0.269 | 0.7631 |
| labirent_9x9_t3 | 2 | basari | 341.85 | 0 | 0.351 | 0.6705 | basari | 313.55 | 0.281 | 0.7205 |

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mujoco 13x13 | 9 | 7/9 | 576.5 | 868 | 121.3 | 0.00 | 998 | 0.50 | 0.59 |
| mujoco 17x17 | 9 | 6/9 | 532.1 | 640 | 124.9 | 0.00 | 932 | 0.74 | 0.44 |
| mujoco 5x5 | 3 | 3/3 | 68.8 | 72 | 12.1 | 0.00 | 1462 | 0.05 | 1.00 |
| mujoco 7x7 | 3 | 3/3 | 216.2 | 256 | 39.7 | 0.00 | 1380 | 0.10 | 0.99 |
| mujoco 9x9 | 9 | 9/9 | 276.9 | 352 | 54.0 | 0.00 | 1346 | 0.24 | 0.83 |

MuJoCo tarama işleme ort 7.5 ms; gerçek zaman oranı ort 3.3 (aynı anda 3 MuJoCo + 2 benzetici süreci).

## Başarısızlıklar (113)

| dosya | strateji | sahne | tohum | odo | durum | süre | sebep / son mod | son olaylar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ayar_sonra.csv | kesif | labirent_17x17_t3 | 1 | 0.14 | fail_sure | 900.0 | - / kesif | 875.1:kurtarma/on_engel; 882.5:kurtarma/on_engel |
| ayar_sonra.csv | kesif | labirent_17x17_t3 | 2 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| ayar_sonra.csv | kesif | labirent_17x17_t3 | 3 | 0.14 | fail_sure | 900.0 | - / kesif | 186.9:kurtarma/on_engel |
| hafiza.csv | kesif | labirent_17x17_t3 | 0 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| hafiza.csv | kesif | labirent_13x13_t2 | 0 | 0.14 | fail_sure | 900.0 | - / konumlan | 229.6:kurtarma/on_engel; 397.9:kurtarma/on_engel; 766.5:kurtarma/on_engel |
| ilk.csv | sag_duvar | labirent_17x17_t1 | 1 | 0.14 | fail_sikisma | 381.25 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t1 | 2 | 0.14 | fail_sikisma | 381.0 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t1 | 0 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_17x17_t1 | 3 | 0.14 | fail_sikisma | 380.9 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t1 | 4 | 0.14 | fail_sikisma | 778.2 | ilerlemesiz / gir | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t2 | 0 | 0.14 | fail_sikisma | 890.35 | ilerlemesiz / ilerle | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t2 | 1 | 0.14 | fail_sikisma | 679.3 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t2 | 3 | 0.14 | fail_sikisma | 387.05 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t2 | 2 | 0.14 | fail_sure | 900.0 | - / ilerle | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_17x17_t3 | 0 | 0.14 | fail_sikisma | 569.45 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t2 | 4 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_17x17_t3 | 1 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_17x17_t3 | 2 | 0.14 | fail_sure | 900.0 | - / gir | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_17x17_t3 | 3 | 0.14 | fail_sikisma | 351.35 | ilerlemesiz / saga_don | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_17x17_t3 | 4 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | kesif | labirent_17x17_t3 | 0 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| ilk.csv | kesif | labirent_17x17_t3 | 4 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| ilk.csv | kesif | labirent_13x13_t2 | 0 | 0.14 | fail_sure | 900.0 | - / konumlan | 229.6:kurtarma/on_engel; 397.9:kurtarma/on_engel; 766.5:kurtarma/on_engel |
| ilk.csv | sag_duvar | labirent_13x13_t1 | 1 | 0.14 | fail_sikisma | 381.25 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_13x13_t1 | 2 | 0.14 | fail_sikisma | 381.0 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_13x13_t1 | 3 | 0.14 | fail_sikisma | 380.9 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_13x13_t2 | 0 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_13x13_t2 | 1 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_13x13_t2 | 3 | 0.14 | fail_sikisma | 387.05 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_13x13_t3 | 0 | 0.14 | fail_sikisma | 569.45 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_13x13_t2 | 4 | 0.14 | fail_sure | 900.0 | - / saga_don | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_13x13_t3 | 1 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_13x13_t3 | 2 | 0.14 | fail_sure | 900.0 | - / gir | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_13x13_t3 | 3 | 0.14 | fail_sikisma | 351.35 | ilerlemesiz / saga_don | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_13x13_t3 | 4 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_9x9_t1 | 1 | 0.14 | fail_sure | 900.0 | - / sola_don | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_9x9_t1 | 3 | 0.14 | fail_sikisma | 380.9 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t2 | 1 | 0.14 | fail_sikisma | 387.15 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t2 | 2 | 0.14 | fail_sikisma | 387.35 | ilerlemesiz / gir | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t2 | 3 | 0.14 | fail_sikisma | 387.05 | ilerlemesiz / gir | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t3 | 0 | 0.14 | fail_sikisma | 733.35 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t2 | 4 | 0.14 | fail_sikisma | 894.4 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t3 | 2 | 0.14 | fail_sure | 900.0 | - / gir | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_9x9_t3 | 3 | 0.14 | fail_sikisma | 351.35 | ilerlemesiz / saga_don | baslangic:1 fail_sikisma:1 |
| ilk.csv | sag_duvar | labirent_9x9_t3 | 4 | 0.14 | fail_sure | 900.0 | - / takip | baslangic:1 fail_sure:1 |
| ilk.csv | sag_duvar | labirent_7x7_t1 | 0 | 0.14 | fail_sikisma | 381.05 | ilerlemesiz / takip | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t1 | 0 | 0.14 | fail_sikisma | 90.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t1 | 1 | 0.14 | fail_sikisma | 441.8 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t1 | 2 | 0.14 | fail_sikisma | 378.25 | ilerlemesiz / don | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t1 | 3 | 0.14 | fail_sikisma | 185.5 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t1 | 4 | 0.14 | fail_sikisma | 551.4 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t2 | 1 | 0.14 | fail_sikisma | 140.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t2 | 0 | 0.14 | fail_sure | 900.0 | - / ileri | baslangic:1 fail_sure:1 |
| ilk.csv | rastgele | labirent_17x17_t2 | 2 | 0.14 | fail_sikisma | 347.05 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t2 | 3 | 0.14 | fail_sikisma | 162.75 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t2 | 4 | 0.14 | fail_sikisma | 494.35 | ilerlemesiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t3 | 0 | 0.14 | fail_sikisma | 347.8 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t3 | 1 | 0.14 | fail_sikisma | 358.35 | ilerlemesiz / ileri | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t3 | 2 | 0.14 | fail_sikisma | 749.1 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t3 | 3 | 0.14 | fail_sikisma | 470.0 | ilerlemesiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t1 | 0 | 0.14 | fail_sikisma | 90.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_17x17_t3 | 4 | 0.14 | fail_sikisma | 593.8 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t1 | 1 | 0.14 | fail_sikisma | 441.8 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t1 | 3 | 0.14 | fail_sikisma | 185.5 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t1 | 2 | 0.14 | fail_sikisma | 378.25 | ilerlemesiz / don | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t1 | 4 | 0.14 | fail_sikisma | 551.4 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t2 | 1 | 0.14 | fail_sikisma | 140.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t2 | 2 | 0.14 | fail_sikisma | 347.05 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t2 | 0 | 0.14 | fail_sure | 900.0 | - / ileri | baslangic:1 fail_sure:1 |
| ilk.csv | rastgele | labirent_13x13_t2 | 3 | 0.14 | fail_sikisma | 162.75 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t3 | 0 | 0.14 | fail_sikisma | 347.8 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t2 | 4 | 0.14 | fail_sikisma | 494.35 | ilerlemesiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t3 | 1 | 0.14 | fail_sikisma | 358.35 | ilerlemesiz / ileri | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t3 | 2 | 0.14 | fail_sikisma | 749.1 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t3 | 3 | 0.14 | fail_sikisma | 470.0 | ilerlemesiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t1 | 0 | 0.14 | fail_sikisma | 90.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_13x13_t3 | 4 | 0.14 | fail_sikisma | 593.8 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t1 | 1 | 0.14 | fail_sikisma | 613.55 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t1 | 2 | 0.14 | fail_sikisma | 378.25 | ilerlemesiz / don | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t1 | 3 | 0.14 | fail_sikisma | 185.5 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t1 | 4 | 0.14 | fail_sikisma | 551.4 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t2 | 1 | 0.14 | fail_sikisma | 140.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t2 | 0 | 0.14 | fail_sure | 900.0 | - / don | baslangic:1 fail_sure:1 |
| ilk.csv | rastgele | labirent_9x9_t2 | 3 | 0.14 | fail_sikisma | 162.75 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t2 | 2 | 0.14 | fail_sikisma | 347.05 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t3 | 0 | 0.14 | fail_sikisma | 347.8 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t2 | 4 | 0.14 | fail_sikisma | 494.35 | ilerlemesiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t3 | 1 | 0.14 | fail_sikisma | 358.35 | ilerlemesiz / don | baslangic:1 carpma:2 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t3 | 3 | 0.14 | fail_sikisma | 317.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t3 | 2 | 0.14 | fail_sikisma | 749.1 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_7x7_t1 | 0 | 0.14 | fail_sikisma | 90.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_9x9_t3 | 4 | 0.14 | fail_sikisma | 593.8 | ilerlemesiz / ileri | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_7x7_t1 | 1 | 0.14 | fail_sikisma | 438.85 | ilerlemesiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_7x7_t1 | 2 | 0.14 | fail_sikisma | 378.25 | ilerlemesiz / don | baslangic:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_7x7_t1 | 3 | 0.14 | fail_sikisma | 185.5 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_5x5_t1 | 0 | 0.14 | fail_sikisma | 90.0 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_7x7_t1 | 4 | 0.14 | fail_sikisma | 201.25 | hareketsiz / don | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_5x5_t1 | 1 | 0.14 | fail_sikisma | 438.3 | ilerlemesiz / ileri | baslangic:1 carpma:1 fail_sikisma:1 |
| ilk.csv | rastgele | labirent_5x5_t1 | 2 | 0.14 | fail_sikisma | 378.25 | ilerlemesiz / don | baslangic:1 fail_sikisma:1 |
| odometri.csv | kesif | labirent_17x17_t3 | 0 | 0.0 | fail_sure | 900.0 | - / kesif |  |
| odometri.csv | kesif | labirent_17x17_t3 | 1 | 0.0 | fail_sure | 900.0 | - / kesif | 349.1:kurtarma/on_engel |
| odometri.csv | kesif | labirent_17x17_t3 | 2 | 0.0 | fail_sure | 900.0 | - / kesif |  |
| odometri.csv | kesif | labirent_17x17_t3 | 4 | 0.0 | fail_sure | 900.0 | - / kesif | 251.7:kurtarma/on_engel; 553.9:kurtarma/on_engel |
| odometri.csv | kesif | labirent_17x17_t3 | 1 | 0.25 | fail_sure | 900.0 | - / kesif | 462.6:kurtarma/on_engel |
| odometri.csv | kesif | labirent_17x17_t3 | 2 | 0.25 | fail_sure | 900.0 | - / kesif | 366.4:kurtarma/on_engel; 799.2:kurtarma/on_engel |
| odometri.csv | kesif | labirent_17x17_t3 | 4 | 0.25 | fail_sure | 900.0 | - / kesif | 478.4:kurtarma/on_engel; 759.9:kurtarma/on_engel |
| odometri.csv | kesif | labirent_13x13_t2 | 0 | 0.0 | fail_sure | 900.0 | - / kesif | 464.4:kurtarma/on_engel; 744.4:kurtarma/on_engel |
| odometri.csv | kesif | labirent_13x13_t2 | 1 | 0.0 | fail_sure | 900.0 | - / kesif | 590.8:kurtarma/on_engel; 868.6:kurtarma/sikisma; 873.5:kurtarma/on_engel |
| odometri.csv | kesif | labirent_13x13_t2 | 2 | 0.0 | fail_sure | 900.0 | - / kesif | 459.1:kurtarma/on_engel |
| odometri.csv | kesif | labirent_13x13_t2 | 3 | 0.0 | fail_sure | 900.0 | - / kesif | 233.8:kurtarma/on_engel; 792.5:kurtarma/sikisma; 797.4:kurtarma/on_engel; 859.8:kurtarma/sikisma |
| odometri.csv | kesif | labirent_13x13_t2 | 0 | 0.25 | fail_sure | 900.0 | - / kesif | 814.5:kurtarma/sikisma; 817.8:tukendi/gevset; 835.0:kurtarma/sikisma; 839.9:kurtarma/on_engel; 849.6:kurtarma/sikisma; 852.9:tukendi/unut:336; 852.9:tukendi/duv |
| odometri.csv | kesif | labirent_13x13_t2 | 3 | 0.25 | fail_sure | 900.0 | - / konumlan | 233.4:kurtarma/on_engel; 407.6:kurtarma/on_engel |
| odometri.csv | kesif | labirent_13x13_t2 | 4 | 0.25 | fail_sure | 900.0 | - / kesif | 227.0:kurtarma/on_engel; 329.4:kurtarma/on_engel; 415.4:kurtarma/on_engel |
