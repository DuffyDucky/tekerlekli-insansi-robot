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

## v1 / v2 (MuJoCo)

v1 = ilk teslim (commit 461216f davranışı, `surum_ayari("v1")`), v2 = `surum_ayari("v2")`. Geliştirme kümesi: 11 labirent x tohum {0, 1, 2}; sınama kümesi: `labirent_13x13_t4..t8`, `labirent_17x17_t4..t8` x tohum {0, 1} (geliştirme boyunca bakılmadı). Karar kuralı: v2 sınama başarısı v1'den az değilse ve çarpma artmadıysa varsayılan olur.

| sürüm | küme | boy | n | başarı | ortanca süre (s, başarılı) | çarpma (toplam) | puan ort | en büyük poz hatası (m) | poz hatası maks ort (m) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 | gelistirme | 5x5 | 3 | 3/3 | 68 | 0 | 1462 | 0.06 | 0.05 |
| v1 | gelistirme | 7x7 | 3 | 3/3 | 243 | 0 | 1380 | 0.13 | 0.10 |
| v1 | gelistirme | 9x9 | 9 | 9/9 | 303 | 0 | 1346 | 0.35 | 0.24 |
| v1 | gelistirme | 13x13 | 9 | 7/9 | 384 | 0 | 998 | 0.81 | 0.50 |
| v1 | gelistirme | 17x17 | 9 | 6/9 | 534 | 0 | 932 | 1.10 | 0.74 |
| v1 | gelistirme | toplam | 33 | 28/33 | 347 | 0 | 1152 | 1.10 | 0.42 |
| v2 | gelistirme | 5x5 | 3 | 3/3 | 63 | 0 | 1465 | 0.13 | 0.09 |
| v2 | gelistirme | 7x7 | 3 | 3/3 | 222 | 0 | 1377 | 0.09 | 0.09 |
| v2 | gelistirme | 9x9 | 9 | 9/9 | 268 | 0 | 1358 | 0.34 | 0.22 |
| v2 | gelistirme | 13x13 | 9 | 7/9 | 346 | 0 | 1018 | 0.75 | 0.44 |
| v2 | gelistirme | 17x17 | 9 | 5/9 | 401 | 0 | 846 | 1.02 | 0.70 |
| v2 | gelistirme | toplam | 33 | 27/33 | 309 | 0 | 1137 | 1.02 | 0.39 |
| v1 | sinama | 13x13 | 10 | 10/10 | 702 | 0 | 1201 | 0.65 | 0.32 |
| v1 | sinama | 17x17 | 10 | 4/10 | 751 | 0 | 616 | 0.77 | 0.54 |
| v1 | sinama | toplam | 20 | 14/20 | 712 | 0 | 908 | 0.77 | 0.43 |
| v2 | sinama | 13x13 | 10 | 10/10 | 665 | 0 | 1216 | 0.34 | 0.25 |
| v2 | sinama | 17x17 | 10 | 4/10 | 716 | 0 | 627 | 0.86 | 0.53 |
| v2 | sinama | toplam | 20 | 14/20 | 699 | 0 | 921 | 0.86 | 0.39 |

Sınama kararı: v1 başarı 14/20, çarpma 0; v2 başarı 14/20, çarpma 0 -> varsayılan **v2**.

| sınama sahnesi | tohum | v1 durum | v1 süre | v2 durum | v2 süre |
| --- | --- | --- | --- | --- | --- |
| labirent_13x13_t4 | 0 | basari | 798.9 | basari | 736.2 |
| labirent_13x13_t4 | 1 | basari | 787.7 | basari | 718.4 |
| labirent_13x13_t5 | 0 | basari | 702.6 | basari | 741.3 |
| labirent_13x13_t5 | 1 | basari | 717.35 | basari | 699.85 |
| labirent_13x13_t6 | 0 | basari | 701.05 | basari | 696.0 |
| labirent_13x13_t6 | 1 | basari | 707.0 | basari | 633.8 |
| labirent_13x13_t7 | 0 | basari | 249.05 | basari | 215.3 |
| labirent_13x13_t7 | 1 | basari | 227.95 | basari | 223.35 |
| labirent_13x13_t8 | 0 | basari | 243.4 | basari | 230.65 |
| labirent_13x13_t8 | 1 | basari | 241.95 | basari | 222.1 |
| labirent_17x17_t4 | 0 | fail_sure | 900.0 | fail_sure | 900.05 |
| labirent_17x17_t4 | 1 | fail_sure | 900.0 | fail_sure | 900.05 |
| labirent_17x17_t5 | 0 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t5 | 1 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t6 | 0 | basari | 744.8 | basari | 697.4 |
| labirent_17x17_t6 | 1 | basari | 780.7 | basari | 728.2 |
| labirent_17x17_t7 | 0 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t7 | 1 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t8 | 0 | basari | 733.8 | basari | 750.0 |
| labirent_17x17_t8 | 1 | basari | 757.75 | basari | 703.35 |

### Hafızalı ek tur (v2, sınama kümesi, ilk koşu başarılıysa aynı tohum)

| sahne | tohum | ilk süre | hafızalı durum | hafızalı süre | kazanç | çarpma |
| --- | --- | --- | --- | --- | --- | --- |
| labirent_13x13_t4 | 0 | 736.2 | basari | 316.25 | 57% | 0 |
| labirent_13x13_t4 | 1 | 718.4 | basari | 338.95 | 53% | 0 |
| labirent_13x13_t5 | 0 | 741.3 | basari | 619.7 | 16% | 0 |
| labirent_13x13_t5 | 1 | 699.85 | basari | 628.45 | 10% | 0 |
| labirent_13x13_t6 | 0 | 696.0 | basari | 568.05 | 18% | 0 |
| labirent_13x13_t6 | 1 | 633.8 | basari | 578.25 | 9% | 0 |
| labirent_13x13_t7 | 0 | 215.3 | basari | 213.4 | 1% | 0 |
| labirent_13x13_t7 | 1 | 223.35 | basari | 210.35 | 6% | 0 |
| labirent_13x13_t8 | 0 | 230.65 | basari | 219.35 | 5% | 0 |
| labirent_13x13_t8 | 1 | 222.1 | basari | 228.4 | -3% | 0 |
| labirent_17x17_t6 | 0 | 697.4 | basari | 563.65 | 19% | 0 |
| labirent_17x17_t6 | 1 | 728.2 | basari | 581.85 | 20% | 0 |
| labirent_17x17_t8 | 0 | 750.0 | basari | 701.8 | 6% | 0 |
| labirent_17x17_t8 | 1 | 703.35 | basari | 675.8 | 4% | 0 |

### 2B benzetici: v1 (ilk.csv) / v2 (v2_2b.csv), aynı labirent ve tohumlar

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 13x13 | 15 | 14/15 | 480.2 | 765 | 104.0 | 0.07 | 1170 | 0.46 | 0.56 |
| v1 17x17 | 15 | 13/15 | 514.2 | 692 | 117.8 | 0.00 | 1104 | 0.74 | 0.48 |
| v1 5x5 | 5 | 5/5 | 63.2 | 68 | 12.1 | 0.00 | 1465 | 0.06 | 1.00 |
| v1 7x7 | 5 | 5/5 | 213.5 | 233 | 42.0 | 0.00 | 1381 | 0.09 | 0.99 |
| v1 9x9 | 15 | 15/15 | 243.7 | 319 | 50.8 | 0.07 | 1359 | 0.22 | 0.82 |

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v2 13x13 | 15 | 14/15 | 439.0 | 743 | 107.9 | 0.13 | 1188 | 0.45 | 0.55 |
| v2 17x17 | 15 | 13/15 | 469.0 | 608 | 120.3 | 0.00 | 1126 | 0.60 | 0.46 |
| v2 5x5 | 5 | 5/5 | 61.0 | 65 | 12.2 | 0.00 | 1466 | 0.07 | 1.00 |
| v2 7x7 | 5 | 5/5 | 175.7 | 209 | 37.9 | 0.00 | 1402 | 0.10 | 0.99 |
| v2 9x9 | 15 | 15/15 | 226.1 | 293 | 53.9 | 0.00 | 1374 | 0.22 | 0.81 |

### Zaman dökümü (`kesif.tani`, MuJoCo geliştirme kayıtları; kesişen kalemler: tekrar, çıkmaz)

| sürüm | sahne | tohum | durum | süre | düz | dönüş | bekle | kurtarma | tekrar | çözüm dışı | yol / çözüm | çıkmaz kol girilen / uzaktan görülmüş | düz hız ort | poz hata %50 / son |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 | labirent_13x13_t1 | 0 | basari | 368.6 | 294.5 | 37.8 | 4.6 | 31.6 | 0.0 | 0.0 | 0.88 | 0 / 0 | 0.206 | 0.477 / 0.676 |
| v1 | labirent_13x13_t1 | 1 | basari | 384.1 | 300.4 | 46.7 | 6.0 | 31.0 | 19.0 | 0.0 | 0.89 | 0 / 0 | 0.204 | 0.157 / 0.196 |
| v1 | labirent_13x13_t1 | 2 | basari | 361.8 | 294.7 | 37.0 | 4.4 | 25.6 | 0.0 | 0.0 | 0.89 | 0 / 0 | 0.211 | 0.213 / 0.317 |
| v1 | labirent_13x13_t2 | 0 | fail_sure | 900.0 | 719.1 | 112.4 | 12.1 | 56.4 | 162.3 | 567.8 | 2.32 | 4 / 0 | 0.208 | 0.263 / 0.263 |
| v1 | labirent_13x13_t2 | 1 | basari | 360.8 | 294.9 | 42.2 | 4.3 | 19.4 | 13.8 | 13.4 | 0.96 | 2 / 0 | 0.212 | 0.308 / 0.575 |
| v1 | labirent_13x13_t2 | 2 | fail_sure | 900.0 | 723.5 | 114.8 | 9.3 | 52.3 | 168.7 | 576.3 | 2.28 | 4 / 1 | 0.202 | 0.335 / 0.335 |
| v1 | labirent_13x13_t3 | 0 | basari | 835.5 | 691.9 | 110.9 | 5.4 | 27.3 | 61.8 | 127.3 | 1.13 | 2 / 0 | 0.214 | 0.424 / 0.81 |
| v1 | labirent_13x13_t3 | 1 | basari | 868.4 | 719.7 | 106.0 | 8.4 | 34.3 | 88.2 | 110.9 | 1.12 | 1 / 0 | 0.204 | 0.31 / 0.569 |
| v1 | labirent_13x13_t3 | 2 | basari | 856.5 | 709.6 | 118.6 | 6.8 | 21.3 | 114.9 | 148.7 | 1.16 | 3 / 1 | 0.214 | 0.413 / 0.761 |
| v1 | labirent_17x17_t1 | 0 | basari | 424.0 | 345.5 | 43.0 | 5.0 | 30.5 | 0.0 | 0.0 | 0.88 | 0 / 0 | 0.214 | 0.557 / 1.103 |
| v1 | labirent_17x17_t1 | 1 | basari | 447.6 | 350.9 | 54.2 | 6.7 | 35.7 | 22.5 | 0.0 | 0.89 | 0 / 0 | 0.211 | 0.168 / 0.26 |
| v1 | labirent_17x17_t1 | 2 | basari | 423.9 | 350.0 | 41.8 | 4.6 | 27.4 | 0.0 | 0.0 | 0.87 | 0 / 0 | 0.21 | 0.234 / 0.462 |
| v1 | labirent_17x17_t2 | 0 | basari | 636.8 | 542.7 | 58.2 | 6.7 | 29.2 | 34.1 | 72.8 | 1.01 | 1 / 0 | 0.204 | 0.255 / 0.816 |
| v1 | labirent_17x17_t2 | 1 | basari | 639.9 | 534.6 | 55.9 | 6.0 | 43.3 | 44.3 | 82.8 | 1.01 | 1 / 0 | 0.206 | 0.36 / 0.87 |
| v1 | labirent_17x17_t2 | 2 | basari | 620.4 | 519.8 | 63.5 | 5.9 | 31.2 | 44.8 | 75.4 | 1.01 | 1 / 0 | 0.211 | 0.323 / 0.651 |
| v1 | labirent_17x17_t3 | 0 | fail_sure | 900.0 | 769.8 | 103.6 | 5.3 | 21.2 | 14.1 | 314.7 | 1.35 | 1 / 0 | 0.213 | 0.561 / 0.78 |
| v1 | labirent_17x17_t3 | 1 | fail_sure | 900.0 | 769.4 | 96.7 | 5.7 | 28.2 | 14.4 | 291.3 | 1.33 | 2 / 1 | 0.21 | 0.678 / 0.908 |
| v1 | labirent_17x17_t3 | 2 | fail_sure | 900.0 | 760.9 | 95.8 | 8.1 | 35.1 | 21.2 | 306.6 | 1.3 | 2 / 1 | 0.208 | 0.537 / 0.798 |
| v1 | labirent_5x5_t1 | 0 | basari | 68.5 | 51.8 | 7.2 | 1.0 | 8.5 | 0.0 | 0.0 | 0.85 | 0 / 0 | 0.211 | 0.023 / 0.06 |
| v1 | labirent_5x5_t1 | 1 | basari | 66.2 | 53.9 | 5.5 | 0.7 | 6.1 | 0.0 | 0.0 | 0.85 | 0 / 0 | 0.207 | 0.023 / 0.054 |
| v1 | labirent_5x5_t1 | 2 | basari | 71.8 | 58.8 | 7.9 | 0.8 | 4.3 | 0.0 | 0.0 | 0.84 | 0 / 0 | 0.186 | 0.028 / 0.028 |
| v1 | labirent_7x7_t1 | 0 | basari | 255.9 | 205.9 | 27.8 | 3.9 | 18.3 | 45.3 | 80.5 | 1.41 | 1 / 0 | 0.202 | 0.07 / 0.08 |
| v1 | labirent_7x7_t1 | 1 | basari | 150.2 | 119.2 | 18.2 | 1.4 | 11.5 | 0.0 | 0.0 | 0.85 | 0 / 0 | 0.208 | 0.029 / 0.104 |
| v1 | labirent_7x7_t1 | 2 | basari | 242.8 | 199.3 | 26.8 | 3.4 | 13.3 | 38.0 | 81.2 | 1.41 | 1 / 0 | 0.209 | 0.096 / 0.13 |
| v1 | labirent_9x9_t1 | 0 | basari | 303.0 | 260.1 | 27.8 | 2.0 | 13.2 | 54.0 | 104.3 | 1.45 | 1 / 0 | 0.21 | 0.074 / 0.157 |
| v1 | labirent_9x9_t1 | 1 | basari | 310.5 | 265.4 | 25.1 | 3.4 | 16.6 | 54.7 | 101.3 | 1.46 | 1 / 0 | 0.206 | 0.111 / 0.13 |
| v1 | labirent_9x9_t1 | 2 | basari | 296.0 | 253.5 | 31.2 | 2.4 | 8.9 | 57.7 | 104.1 | 1.44 | 1 / 0 | 0.212 | 0.157 / 0.173 |
| v1 | labirent_9x9_t2 | 0 | basari | 127.5 | 111.5 | 11.3 | 1.0 | 3.7 | 0.0 | 0.0 | 0.87 | 0 / 0 | 0.22 | 0.055 / 0.17 |
| v1 | labirent_9x9_t2 | 1 | basari | 286.8 | 230.5 | 32.9 | 3.9 | 19.4 | 77.0 | 146.9 | 1.81 | 0 / 0 | 0.212 | 0.109 / 0.223 |
| v1 | labirent_9x9_t2 | 2 | basari | 149.5 | 127.2 | 9.4 | 2.6 | 10.3 | 8.8 | 0.0 | 0.9 | 0 / 0 | 0.197 | 0.029 / 0.269 |
| v1 | labirent_9x9_t3 | 0 | basari | 325.3 | 277.9 | 41.2 | 1.8 | 4.4 | 38.2 | 67.4 | 1.2 | 0 / 0 | 0.223 | 0.15 / 0.299 |
| v1 | labirent_9x9_t3 | 1 | basari | 351.9 | 296.8 | 37.2 | 3.7 | 14.2 | 46.1 | 68.2 | 1.22 | 0 / 0 | 0.211 | 0.137 / 0.353 |
| v1 | labirent_9x9_t3 | 2 | basari | 341.9 | 281.3 | 46.4 | 2.2 | 11.9 | 50.6 | 68.8 | 1.22 | 0 / 0 | 0.221 | 0.174 / 0.351 |
| v2 | labirent_13x13_t1 | 0 | basari | 335.3 | 273.2 | 37.5 | 4.4 | 20.2 | 0.0 | 0.0 | 0.88 | 0 / 0 | 0.226 | 0.132 / 0.295 |
| v2 | labirent_13x13_t1 | 1 | basari | 338.5 | 276.1 | 40.2 | 2.9 | 19.3 | 7.0 | 0.0 | 0.86 | 0 / 0 | 0.219 | 0.23 / 0.27 |
| v2 | labirent_13x13_t1 | 2 | basari | 346.0 | 288.4 | 38.5 | 4.1 | 15.1 | 6.4 | 0.0 | 0.88 | 0 / 0 | 0.215 | 0.263 / 0.471 |
| v2 | labirent_13x13_t2 | 0 | fail_sure | 900.1 | 722.0 | 122.2 | 14.8 | 40.9 | 202.3 | 587.3 | 2.53 | 4 / 0 | 0.227 | 0.252 / 0.252 |
| v2 | labirent_13x13_t2 | 1 | fail_sure | 900.1 | 714.8 | 123.1 | 9.9 | 52.1 | 208.0 | 597.7 | 2.51 | 3 / 0 | 0.226 | 0.251 / 0.251 |
| v2 | labirent_13x13_t2 | 2 | basari | 323.1 | 269.7 | 39.0 | 3.9 | 10.5 | 10.3 | 13.2 | 0.95 | 1 / 0 | 0.233 | 0.075 / 0.33 |
| v2 | labirent_13x13_t3 | 0 | basari | 822.4 | 658.7 | 111.9 | 12.5 | 39.3 | 108.6 | 126.1 | 1.15 | 3 / 1 | 0.227 | 0.405 / 0.653 |
| v2 | labirent_13x13_t3 | 1 | basari | 758.7 | 628.2 | 95.2 | 4.9 | 30.3 | 46.3 | 104.3 | 1.06 | 1 / 0 | 0.223 | 0.398 / 0.672 |
| v2 | labirent_13x13_t3 | 2 | basari | 795.1 | 645.7 | 114.5 | 8.1 | 26.7 | 104.5 | 116.6 | 1.12 | 2 / 1 | 0.228 | 0.435 / 0.754 |
| v2 | labirent_17x17_t1 | 0 | basari | 401.1 | 322.4 | 42.1 | 5.6 | 31.0 | 0.0 | 0.0 | 0.87 | 0 / 0 | 0.229 | 0.282 / 0.401 |
| v2 | labirent_17x17_t1 | 1 | basari | 391.6 | 318.8 | 42.2 | 3.2 | 27.3 | 0.0 | 0.0 | 0.87 | 0 / 0 | 0.229 | 0.249 / 0.475 |
| v2 | labirent_17x17_t1 | 2 | basari | 400.3 | 325.1 | 41.4 | 3.2 | 30.6 | 0.0 | 0.0 | 0.87 | 0 / 0 | 0.226 | 0.257 / 0.356 |
| v2 | labirent_17x17_t2 | 0 | basari | 614.9 | 505.9 | 55.1 | 8.6 | 45.2 | 50.4 | 76.3 | 1.02 | 1 / 0 | 0.22 | 0.314 / 0.915 |
| v2 | labirent_17x17_t2 | 1 | fail_sure | 900.1 | 716.8 | 119.5 | 16.8 | 46.9 | 124.4 | 488.2 | 1.5 | 3 / 0 | 0.225 | 0.646 / 0.657 |
| v2 | labirent_17x17_t2 | 2 | basari | 583.5 | 487.9 | 55.8 | 5.6 | 34.2 | 47.7 | 77.6 | 1.01 | 1 / 0 | 0.225 | 0.405 / 1.019 |
| v2 | labirent_17x17_t3 | 0 | fail_sure | 900.1 | 748.3 | 112.5 | 9.0 | 30.2 | 109.1 | 344.2 | 1.39 | 2 / 0 | 0.224 | 0.554 / 0.674 |
| v2 | labirent_17x17_t3 | 1 | fail_sure | 900.1 | 771.2 | 91.2 | 8.8 | 28.9 | 78.6 | 297.0 | 1.36 | 1 / 0 | 0.214 | 0.62 / 0.883 |
| v2 | labirent_17x17_t3 | 2 | fail_sure | 900.1 | 759.7 | 110.7 | 5.7 | 23.9 | 101.0 | 333.1 | 1.42 | 4 / 1 | 0.227 | 0.616 / 0.924 |
| v2 | labirent_5x5_t1 | 0 | basari | 62.6 | 46.7 | 6.4 | 1.0 | 8.5 | 0.0 | 0.0 | 0.84 | 0 / 0 | 0.234 | 0.023 / 0.128 |
| v2 | labirent_5x5_t1 | 1 | basari | 60.8 | 47.6 | 6.3 | 0.8 | 6.1 | 0.0 | 0.0 | 0.85 | 0 / 0 | 0.234 | 0.023 / 0.049 |
| v2 | labirent_5x5_t1 | 2 | basari | 63.9 | 50.9 | 7.9 | 0.8 | 4.3 | 0.0 | 0.0 | 0.84 | 0 / 0 | 0.214 | 0.022 / 0.078 |
| v2 | labirent_7x7_t1 | 0 | basari | 222.4 | 179.1 | 30.2 | 2.0 | 11.1 | 39.9 | 76.6 | 1.4 | 1 / 0 | 0.231 | 0.066 / 0.086 |
| v2 | labirent_7x7_t1 | 1 | basari | 213.7 | 174.7 | 27.1 | 1.8 | 10.3 | 40.0 | 72.8 | 1.39 | 1 / 0 | 0.238 | 0.048 / 0.094 |
| v2 | labirent_7x7_t1 | 2 | basari | 230.2 | 177.1 | 41.3 | 2.0 | 9.8 | 51.1 | 80.6 | 1.43 | 1 / 0 | 0.232 | 0.086 / 0.086 |
| v2 | labirent_9x9_t1 | 0 | basari | 268.3 | 227.2 | 29.4 | 2.0 | 9.7 | 49.0 | 90.2 | 1.45 | 1 / 0 | 0.24 | 0.113 / 0.197 |
| v2 | labirent_9x9_t1 | 1 | basari | 173.3 | 149.5 | 14.3 | 1.2 | 8.4 | 0.0 | 0.0 | 0.87 | 0 / 0 | 0.22 | 0.072 / 0.218 |
| v2 | labirent_9x9_t1 | 2 | basari | 272.5 | 227.3 | 32.5 | 2.3 | 10.5 | 48.1 | 92.8 | 1.45 | 1 / 0 | 0.237 | 0.151 / 0.188 |
| v2 | labirent_9x9_t2 | 0 | basari | 125.3 | 104.6 | 11.5 | 1.2 | 8.1 | 0.0 | 0.0 | 0.91 | 0 / 0 | 0.242 | 0.086 / 0.196 |
| v2 | labirent_9x9_t2 | 1 | basari | 265.3 | 208.3 | 29.9 | 2.6 | 24.5 | 61.9 | 132.3 | 1.72 | 0 / 0 | 0.224 | 0.072 / 0.159 |
| v2 | labirent_9x9_t2 | 2 | basari | 255.8 | 206.5 | 32.2 | 2.4 | 14.8 | 67.9 | 129.8 | 1.76 | 0 / 0 | 0.232 | 0.073 / 0.167 |
| v2 | labirent_9x9_t3 | 0 | basari | 308.8 | 260.4 | 33.7 | 3.4 | 11.3 | 34.3 | 75.9 | 1.21 | 0 / 0 | 0.241 | 0.152 / 0.271 |
| v2 | labirent_9x9_t3 | 1 | basari | 331.1 | 275.2 | 39.5 | 3.7 | 12.6 | 34.7 | 69.9 | 1.21 | 0 / 0 | 0.226 | 0.091 / 0.292 |
| v2 | labirent_9x9_t3 | 2 | basari | 301.1 | 248.4 | 42.2 | 2.3 | 8.1 | 36.7 | 60.5 | 1.19 | 0 / 0 | 0.247 | 0.181 / 0.336 |

v1 toplam süre payı: düz 83%, dönüş 11%, bekle 1%, kurtarma 5%; tekrar 9%, çözüm dışı 23%; düz hız ort 0.209 m/s.

v2 toplam süre payı: düz 82%, dönüş 12%, bekle 1%, kurtarma 5%; tekrar 11%, çözüm dışı 28%; düz hız ort 0.228 m/s.

## Uzatılmış süre (KURAL DIŞI: hakem süre sınırı 1800 s; v2, MuJoCo, tohum 0)

Soru: 15 dk sınırı olmasaydı çözer miydi, ne kadar sürerdi. Bu satırlar yukarıdaki 15 dakikalık tabloların hiçbirinde yok. Gereken hız = yürünen yol / 900 s (aynı yolu 900 s'de bitirmek için ortalama hız).

| sahne | durum | süre (s) | çözüm (m) | yürünen (m) | yol / çözüm | çarpma | poz hatası maks (m) | poz hatası %25 / %50 / son (m) | düz hız ort (m/s) | gereken hız (m/s) | gereken / 0,39 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| labirent_13x13_t2 | fail_sikisma | 1077.75 | 71.5 | 214.9 | 3.01 | 0 | 0.252 | 0.204 / 0.252 / 0.252 | 0.226 | 0.239 | 0.61 |
| labirent_17x17_t1 | basari | 401.1 | 92.3 | 80.7 | 0.87 | 0 | 0.401 | 0.069 / 0.282 / 0.401 | 0.229 | 0.090 | 0.23 |
| labirent_17x17_t2 | basari | 614.9 | 118.3 | 121.2 | 1.02 | 0 | 0.915 | 0.112 / 0.314 / 0.915 | 0.22 | 0.135 | 0.35 |
| labirent_17x17_t3 | fail_sikisma | 1737.95 | 131.3 | 335.4 | 2.55 | 0 | 0.674 | 0.554 / 0.674 / 0.674 | 0.218 | 0.373 | 0.96 |
| labirent_17x17_t4 | basari | 1689.9 | 183.3 | 345.3 | 1.88 | 0 | 0.668 | 0.337 / 0.432 / 0.668 | 0.227 | 0.384 | 0.98 |
| labirent_17x17_t5 | fail_sikisma | 1700.0 | 152.1 | 336.5 | 2.21 | 0 | 0.446 | 0.16 / 0.392 / 0.446 | 0.222 | 0.374 | 0.96 |
| labirent_17x17_t6 | basari | 697.4 | 133.9 | 143.3 | 1.07 | 0 | 0.856 | 0.086 / 0.297 / 0.856 | 0.228 | 0.159 | 0.41 |
| labirent_17x17_t7 | basari | 930.5 | 183.3 | 181.9 | 0.99 | 0 | 0.517 | 0.198 / 0.387 / 0.517 | 0.217 | 0.202 | 0.52 |
| labirent_17x17_t8 | basari | 750.0 | 162.5 | 146.0 | 0.90 | 0 | 0.621 | 0.167 / 0.271 / 0.621 | 0.218 | 0.162 | 0.42 |
**Hüküm** (17x17, tohum 0): 30 dakikada 6/8 çözülüyor (15 dakikada 4). 900 s'yi aşanların 17x17_t7 yürünen yol / çözüm < 1,3 ile yalnız hızdan aşıyor; 17x17_t4, 17x17_t3, 17x17_t5 yol / çözüm >= 1,5 ile keşif dolaşıyor (hakemin 300 s yeni hücresiz kuralına takılan ya da geç biten). Harita kayması süreyle büyüyor ama kaçmıyor: en büyük poz hatası 0.40–0.92 m, çarpma toplam 0.

## v2 / v3 (MuJoCo): dışa açık sınır önceliği

Tanı: `sonuc/tani_dolanma.md`. v3 = v2 + dışa açık sınırın (dönüşsüz ışın oranı >= 0,3) maliyeti 25 m düşük, yeri hatırlanır. Geliştirme: eski 11 labirent x 3 tohum + görülmüş 17x17_t4, t5 x 2 tohum. Sınama2: `labirent_13x13_t9..t13`, `labirent_17x17_t9..t13` x tohum {0, 1}.

| sürüm | küme | boy | n | başarı | ortanca süre (s, başarılı) | çarpma (toplam) | puan ort | en büyük poz hatası (m) | poz hatası maks ort (m) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v2 | gelistirme | 5x5 | 3 | 3/3 | 63 | 0 | 1465 | 0.13 | 0.09 |
| v2 | gelistirme | 7x7 | 3 | 3/3 | 222 | 0 | 1377 | 0.09 | 0.09 |
| v2 | gelistirme | 9x9 | 9 | 9/9 | 268 | 0 | 1358 | 0.34 | 0.22 |
| v2 | gelistirme | 13x13 | 9 | 7/9 | 346 | 0 | 1018 | 0.75 | 0.44 |
| v2 | gelistirme | 17x17 | 13 | 5/13 | 401 | 0 | 669 | 1.02 | 0.60 |
| v2 | gelistirme | toplam | 37 | 27/37 | 309 | 0 | 1044 | 1.02 | 0.39 |
| v3 | gelistirme | 5x5 | 3 | 3/3 | 62 | 0 | 1466 | 0.12 | 0.08 |
| v3 | gelistirme | 7x7 | 3 | 3/3 | 222 | 0 | 1377 | 0.09 | 0.09 |
| v3 | gelistirme | 9x9 | 9 | 9/9 | 268 | 0 | 1358 | 0.34 | 0.22 |
| v3 | gelistirme | 13x13 | 9 | 7/9 | 346 | 0 | 1018 | 0.75 | 0.44 |
| v3 | gelistirme | 17x17 | 13 | 8/13 | 519 | 0 | 846 | 1.10 | 0.64 |
| v3 | gelistirme | toplam | 37 | 30/37 | 327 | 0 | 1105 | 1.10 | 0.40 |
| v2 | sinama2 | 13x13 | 10 | 10/10 | 724 | 0 | 1181 | 0.62 | 0.38 |
| v2 | sinama2 | 17x17 | 10 | 5/10 | 797 | 0 | 736 | 0.68 | 0.40 |
| v2 | sinama2 | toplam | 20 | 15/20 | 731 | 0 | 958 | 0.68 | 0.39 |
| v3 | sinama2 | 13x13 | 10 | 10/10 | 724 | 0 | 1181 | 0.62 | 0.38 |
| v3 | sinama2 | 17x17 | 10 | 5/10 | 797 | 0 | 735 | 0.69 | 0.40 |
| v3 | sinama2 | toplam | 20 | 15/20 | 731 | 0 | 958 | 0.69 | 0.39 |

Sınama2 kararı: v2 başarı 15/20, çarpma 0; v3 başarı 15/20, çarpma 0 -> varsayılan **v3**.

Not: v3 sınama2'de kazanç getirmedi (15/20 = 15/20). Geliştirmedeki kazanç (27 → 30 / 37) düzeltmenin üzerinde tasarlandığı labirentten, 17x17_t3'ten geliyor; genel iyileşme kanıtı sayılmaz.

| sınama2 sahnesi | tohum | v2 durum | v2 süre | v3 durum | v3 süre |
| --- | --- | --- | --- | --- | --- |
| labirent_13x13_t10 | 0 | basari | 202.25 | basari | 199.45 |
| labirent_13x13_t10 | 1 | basari | 208.8 | basari | 208.8 |
| labirent_13x13_t11 | 0 | basari | 731.15 | basari | 731.15 |
| labirent_13x13_t11 | 1 | basari | 717.7 | basari | 717.7 |
| labirent_13x13_t12 | 0 | basari | 867.95 | basari | 867.95 |
| labirent_13x13_t12 | 1 | basari | 736.85 | basari | 736.85 |
| labirent_13x13_t13 | 0 | basari | 869.4 | basari | 869.4 |
| labirent_13x13_t13 | 1 | basari | 743.05 | basari | 743.05 |
| labirent_13x13_t9 | 0 | basari | 328.1 | basari | 328.1 |
| labirent_13x13_t9 | 1 | basari | 336.55 | basari | 336.55 |
| labirent_17x17_t10 | 0 | basari | 305.7 | basari | 305.7 |
| labirent_17x17_t10 | 1 | basari | 318.4 | basari | 318.4 |
| labirent_17x17_t11 | 0 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t11 | 1 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t12 | 0 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t12 | 1 | fail_sure | 900.05 | fail_sure | 900.05 |
| labirent_17x17_t13 | 0 | basari | 864.1 | basari | 861.25 |
| labirent_17x17_t13 | 1 | basari | 797.35 | basari | 797.4 |
| labirent_17x17_t9 | 0 | basari | 885.55 | basari | 894.55 |
| labirent_17x17_t9 | 1 | fail_sure | 900.05 | fail_sure | 900.05 |

| geliştirme sahnesi | tohum | v2 durum | v2 süre | v3 durum | v3 süre |
| --- | --- | --- | --- | --- | --- |
| labirent_17x17_t2 | 0 | basari | 614.9 | basari | 533.5 |
| labirent_17x17_t2 | 2 | basari | 583.5 | basari | 504.7 |
| labirent_17x17_t3 | 0 | fail_sure | 900.05 | basari | 668.5 |
| labirent_17x17_t3 | 1 | fail_sure | 900.05 | basari | 710.35 |
| labirent_17x17_t3 | 2 | fail_sure | 900.05 | basari | 677.7 |
| labirent_5x5_t1 | 2 | basari | 63.9 | basari | 62.4 |

(yalnız farklı sonuçlanan geliştirme koşuları)

### Uzatılmış (KURAL DIŞI 1800 s, tohum 0): dolanma kayboldu mu

| sürüm | başarı | fail_sikisma | ort yol / çözüm | süre (başarılı, s) |
| --- | --- | --- | --- | --- |
| v2 | 6/9 | 3 | 1.61 | 17x17_t1 401, 17x17_t2 615, 17x17_t6 697, 17x17_t4 1690, 17x17_t7 930, 17x17_t8 750 |
| v3 | 7/9 | 2 | 1.43 | 17x17_t1 401, 17x17_t2 534, 17x17_t3 668, 17x17_t6 697, 17x17_t7 930, 17x17_t4 1690, 17x17_t8 747 |

### 2B v2 / v3 (21 geliştirme labirenti x tohum {0, 1}, `sonuc/v3_2b.csv`)

| grup | n | başarı | süre ort (s, başarılı) | süre maks | yol (m) | çarpma ort | puan ort | poz hata maks ort (m) | doğru duvar ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v2 13x13 | 16 | 15/16 | 441.6 | 698 | 108.2 | 0.06 | 1194 | 0.37 | 0.64 |
| v2 17x17 | 16 | 13/16 | 607.2 | 853 | 151.8 | 0.06 | 992 | 0.59 | 0.49 |
| v2 5x5 | 2 | 2/2 | 60.5 | 64 | 12.2 | 0.00 | 1466 | 0.06 | 1.00 |
| v2 7x7 | 2 | 2/2 | 167.2 | 205 | 36.2 | 0.00 | 1407 | 0.10 | 0.99 |
| v2 9x9 | 6 | 6/6 | 227.9 | 276 | 54.5 | 0.00 | 1373 | 0.22 | 0.82 |
| v3 13x13 | 16 | 15/16 | 405.2 | 698 | 99.9 | 0.06 | 1213 | 0.37 | 0.64 |
| v3 17x17 | 16 | 13/16 | 597.0 | 853 | 150.0 | 0.06 | 997 | 0.59 | 0.49 |
| v3 5x5 | 2 | 2/2 | 55.4 | 56 | 12.0 | 0.00 | 1469 | 0.06 | 1.00 |
| v3 7x7 | 2 | 2/2 | 167.2 | 205 | 36.2 | 0.00 | 1407 | 0.10 | 0.99 |
| v3 9x9 | 6 | 6/6 | 227.9 | 276 | 54.5 | 0.00 | 1373 | 0.22 | 0.82 |

## Deneme zinciri (HAFIZALI sınıf): başarısız denemenin haritası sonraki denemeye taşınır

**Bu bölüm "ilk girişte, hiç bilgi olmadan" KPI'sı değildir.** 2. ve sonraki denemelerde beyin önceki denemelerin haritasını bilir. İlk giriş KPI'sı (v3, ön bilgisiz) değişmedi: yukarıdaki "v2 / v3" bölümü. CSV: `sonuc/deneme_gelistirme.csv`, `sonuc/deneme_sinama2.csv` (sütunlar `sinif` = hafizali, `kume`, `deneme_no`; her deneme ayrı satır). Kurulum: `kesif.kos_deneme`, `kesif.deneme`. Robot her yeni denemede START pozuna + yerleştirme hatasına (std 3 cm, 2°; kırpma 6 cm, 4°) konur; beyin pozunu harita çerçevesinde START'a sıfırlar, ilk iki taramayı geniş aramayla eski haritaya oturtur. En çok 4 deneme, her biri 900 s.

| küme | zincir | 1. denemede | 2. | 3. | 4. | 4 denemede çözülmedi | toplam süre ortanca (s, çözülen) | deneme sayısı | çarpma (toplam) | fail_start | START kesme | hata satırı |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gelistirme | 7 | 0 | 2 | 5 | 0 | 0 | 2502 | 19 | 0 | 0 | 0 | 0 |
| sinama2 | 20 | 15 | 1 | 0 | 0 | 4 | 734 | 33 | 1 | 0 | 0 | 0 |

1. deneme = eski ilk giriş koşusu (gelistirme, `mujoco_v3.csv`): 7/7 aynı sonuç ve süre (±1 s).
1. deneme = eski ilk giriş koşusu (sinama2, `mujoco_sinama2_v3.csv`): 20/20 aynı sonuç ve süre (±1 s).

| küme | deneme no | n | başarı | harita büyümesi ort (m²) | yeni hücre ort (birleşik artışı) | poz hatası maks ort (m) | kurtarma ort |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gelistirme | 1 | 7 | 0 | 256.4 | 122.3 | 0.39 | 2.4 |
| gelistirme | 2 | 7 | 2 | 95.3 | 38.7 | 0.33 | 2.0 |
| gelistirme | 3 | 5 | 5 | 108.3 | 24.0 | 0.53 | 1.6 |
| sinama2 | 1 | 20 | 15 | 268.5 | 99.0 | 0.39 | 1.8 |
| sinama2 | 2 | 5 | 1 | 64.3 | 26.4 | 0.35 | 2.6 |
| sinama2 | 3 | 4 | 0 | 23.1 | 11.8 | 0.36 | 3.2 |
| sinama2 | 4 | 4 | 0 | 30.6 | 12.5 | 0.36 | 4.8 |

### Zincirler: gelistirme

| sahne | tohum | çözüm (m) | deneme: durum / süre (s) | çözüldüğü deneme | toplam süre (s) | bilinen alan sonda (m²), deneme başına | birleşik hücre (deneme sonu) | poz hatası maks (m) | START hatası 0,5 s (m / °) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| labirent_13x13_t2 | 0 | 72 | 1 fail_sure 900; 2 basari 491 | 2 | 1391.2 | 245 → 352 | 118 → 140 | 0.252 / 0.252 | 0.0057 0.108 |
| labirent_13x13_t2 | 1 | 72 | 1 fail_sure 900; 2 basari 491 | 2 | 1391.35 | 244 → 354 | 115 → 138 | 0.251 / 0.235 | 0.0011 0.308 |
| labirent_17x17_t2 | 1 | 118 | 1 fail_sure 900; 2 fail_sikisma 359; 3 basari 523 | 3 | 1782.1 | 277 → 308 → 423 | 130 → 143 → 168 | 0.657 / 0.182 / 0.783 | 0.0026 0.141 / 0.005 0.31 |
| labirent_17x17_t4 | 0 | 183 | 1 fail_sure 900; 2 fail_sure 900; 3 basari 812 | 3 | 2612.15 | 253 → 369 → 512 | 114 → 176 → 217 | 0.432 / 0.549 / 0.621 | 0.0039 0.089 / 0.0046 0.111 |
| labirent_17x17_t4 | 1 | 183 | 1 fail_sure 900; 2 fail_sure 900; 3 basari 782 | 3 | 2582.5 | 252 → 368 → 512 | 118 → 178 → 220 | 0.404 / 0.38 / 0.412 | 0.0159 0.059 / 0.0032 0.118 |
| labirent_17x17_t5 | 0 | 152 | 1 fail_sure 900; 2 fail_sure 900; 3 basari 702 | 3 | 2501.6 | 269 → 366 → 436 | 132 → 179 → 185 | 0.446 / 0.45 / 0.546 | 0.0206 0.114 / 0.0305 0.108 |
| labirent_17x17_t5 | 1 | 152 | 1 fail_sure 900; 2 fail_sure 900; 3 basari 738 | 3 | 2538.15 | 259 → 349 → 418 | 129 → 173 → 179 | 0.255 / 0.248 / 0.306 | 0.029 0.065 / 0.0104 0.09 |

### Zincirler: sinama2

| sahne | tohum | çözüm (m) | deneme: durum / süre (s) | çözüldüğü deneme | toplam süre (s) | bilinen alan sonda (m²), deneme başına | birleşik hücre (deneme sonu) | poz hatası maks (m) | START hatası 0,5 s (m / °) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| labirent_13x13_t10 | 0 | 46 | 1 basari 199 | 1 | 199.45 | 147 | 35 | 0.161 | - |
| labirent_13x13_t10 | 1 | 46 | 1 basari 209 | 1 | 208.8 | 149 | 35 | 0.264 | - |
| labirent_13x13_t11 | 0 | 90 | 1 basari 731 | 1 | 731.15 | 285 | 98 | 0.621 | - |
| labirent_13x13_t11 | 1 | 90 | 1 basari 718 | 1 | 717.7 | 285 | 96 | 0.6 | - |
| labirent_13x13_t12 | 0 | 155 | 1 basari 868 | 1 | 867.95 | 353 | 125 | 0.376 | - |
| labirent_13x13_t12 | 1 | 155 | 1 basari 737 | 1 | 736.85 | 337 | 119 | 0.308 | - |
| labirent_13x13_t13 | 0 | 113 | 1 basari 869 | 1 | 869.4 | 305 | 112 | 0.365 | - |
| labirent_13x13_t13 | 1 | 113 | 1 basari 743 | 1 | 743.05 | 305 | 112 | 0.44 | - |
| labirent_13x13_t9 | 0 | 56 | 1 basari 328 | 1 | 328.1 | 189 | 51 | 0.403 | - |
| labirent_13x13_t9 | 1 | 56 | 1 basari 337 | 1 | 336.55 | 189 | 50 | 0.276 | - |
| labirent_17x17_t10 | 0 | 69 | 1 basari 306 | 1 | 305.7 | 186 | 53 | 0.163 | - |
| labirent_17x17_t10 | 1 | 69 | 1 basari 318 | 1 | 318.4 | 187 | 53 | 0.429 | - |
| labirent_17x17_t11 | 0 | 165 | 1 fail_sure 900; 2 fail_sure 900; 3 fail_sure 900; 4 fail_sure 900 | yok | 3600.2 | 301 → 401 → 437 → 491 | 136 → 184 → 203 → 224 | 0.467 / 0.391 / 0.428 / 0.418 | 0.0095 0.589 / 0.0008 0.258 / 0.0048 0.29 |
| labirent_17x17_t11 | 1 | 165 | 1 fail_sure 900; 2 fail_sure 900; 3 fail_sure 900; 4 fail_sure 900 | yok | 3600.2 | 280 → 402 → 439 → 493 | 126 → 186 → 205 → 228 | 0.271 / 0.328 / 0.288 / 0.286 | 0.0007 0.039 / 0.0017 0.222 / 0.0064 0.428 |
| labirent_17x17_t12 | 0 | 207 | 1 fail_sure 900; 2 fail_sure 900; 3 fail_sure 900; 4 fail_sure 900 | yok | 3600.2 | 319 → 321 → 340 → 342 | 150 → 154 → 163 → 163 | 0.585 / 0.546 / 0.581 / 0.493 | 0.0054 0.171 / 0.0042 0.076 / 0.0057 0.096 |
| labirent_17x17_t12 | 1 | 207 | 1 fail_sure 900; 2 fail_sure 900; 3 fail_sure 900; 4 fail_sure 900 | yok | 3600.2 | 315 → 323 → 323 → 335 | 147 → 152 → 152 → 158 | 0.137 / 0.13 / 0.126 / 0.253 | 0.0048 0.664 / 0.007 0.35 / 0.0004 0.058 |
| labirent_17x17_t13 | 0 | 178 | 1 basari 861 | 1 | 861.25 | 368 | 138 | 0.379 | - |
| labirent_17x17_t13 | 1 | 178 | 1 basari 797 | 1 | 797.4 | 368 | 137 | 0.685 | - |
| labirent_17x17_t9 | 0 | 82 | 1 basari 895 | 1 | 894.55 | 302 | 111 | 0.631 | - |
| labirent_17x17_t9 | 1 | 82 | 1 fail_sure 900; 2 basari 369 | 2 | 1268.85 | 213 → 303 | 96 → 111 | 0.254 / 0.351 | 0.0025 0.128 |

### START'ta yeniden hizalama (gelistirme; aynı beyin kopyası, aynı yerleştirme, 10 s sonda)

| hizalama | n | yerleştirme hatası ort (m / °) | START hatası 0,5 s ort / maks (m) | yön 0,5 s ort / maks (°) | 10 s ort / maks (m) | yön 10 s ort / maks (°) |
| --- | --- | --- | --- | --- | --- | --- |
| açık | 12 | 0.035 / 1.99 | 0.011 / 0.030 | 0.135 / 0.310 | 0.045 / 0.182 | 0.331 / 1.149 |
| kapalı | 12 | 0.035 / 1.99 | 0.012 / 0.042 | 0.185 / 0.471 | 0.070 / 0.460 | 0.384 / 1.129 |

### START'ta yeniden hizalama (sinama2; aynı beyin kopyası, aynı yerleştirme, 10 s sonda)

| hizalama | n | yerleştirme hatası ort (m / °) | START hatası 0,5 s ort / maks (m) | yön 0,5 s ort / maks (°) | 10 s ort / maks (m) | yön 10 s ort / maks (°) |
| --- | --- | --- | --- | --- | --- | --- |
| açık | 13 | 0.030 / 1.90 | 0.004 / 0.009 | 0.259 / 0.664 | 0.007 / 0.017 | 0.756 / 2.269 |
| kapalı | 13 | 0.030 / 1.90 | 0.008 / 0.020 | 0.507 / 0.965 | 0.007 / 0.019 | 0.678 / 2.262 |

### Hız sınırı: harita tam bilinse 900 s'ye sığar mı

Bilinen haritada ölçülen tempo (çözüm metresi başına süre, 14 hafızalı koşu): en iyi 3.86, ortanca 4.23, en kötü 4.75 s/m (yalnız düz sürüş + köşelerde dur–dön–kalk; ölçülen düz hız ~0,23 m/s).

| sahne | çözüm (m) | alt sınır çözüm / 0,39 m/s (s) | tam haritayla beklenen süre en iyi / ortanca / en kötü (s) | 900 s'ye sığar mı | zincir sonucu (tohum: çözüldüğü deneme) |
| --- | --- | --- | --- | --- | --- |
| labirent_17x17_t12 | 207 | 530 | 798 / 874 / 982 | sınırda: ortanca tempoda +26 s pay, en kötüde -82 s; keşfe yer yok | t0: yok (4 deneme), t1: yok (4 deneme) |
| labirent_17x17_t4 | 183 | 470 | 708 / 775 / 870 | evet | t0: 3, t1: 3 |
| labirent_17x17_t13 | 178 | 457 | 688 / 753 / 846 | evet | t0: 1, t1: 1 |
| labirent_17x17_t11 | 165 | 423 | 638 / 698 / 784 | evet | t0: yok (4 deneme), t1: yok (4 deneme) |
| labirent_13x13_t12 | 155 | 397 | 597 / 654 / 735 | evet | t0: 1, t1: 1 |
| labirent_17x17_t5 | 152 | 390 | 587 / 643 / 722 | evet | t0: 3, t1: 3 |

## v4: hız zarfı (fren zarfı, ölçüye dayalı hızlanma izni, yay süpürme denetimi)

### Tanı (v3 MuJoCo kayıtları, geliştirme + sınama2, 57 koşu; `sonuc/hiz_tani_v3.csv`)

- Düz sürüş toplam sürenin %81'i; ölçülen düz hız (düz süre ağırlıklı) 0.225 m/s.
- Hızlı kip (v_komut > 0,26) düz sürenin %22'inde açık. Koşulların tek başına engellediği pay: 1,0 m ön şerit %71, |w| <= 0,12 %53, 1,5 s bekleme %19. Yalnız ön şerit %24, yalnız w %5, yalnız bekleme %0.3.
- Düz sürenin hız dağılımı: < 0,10 m/s %12, 0,10–0,20 %20, 0,20–0,24 %9, 0,24–0,26 %38, 0,26–0,33 %5, >= 0,33 %17.
- Düz parça 3471 (ortalama 1.64 m). 1,5 m'den kısa 2074 parça 7459 s sürdü; ideal dur-kalk süresi 5142 s. Parça sonunda 0,10 m/s altında geçen kuyruk toplam 3098 s (toplam sürenin %10.0'i): izleyicinin doğrusal yumuşak varışı (v <= 0,8 x kalan) köşeye üstel yaklaşıyor.
- Üst sınır: her düz parça 0,39 m/s tavan ve 0,5 m/s² hızlanma / yavaşlamayla (yay ve eğrilik yok sayılarak) 25082 s yerine 16952 s sürerdi; kazanç en çok 8131 s, toplam sürenin %26'i. Yerinde dönüş, plan ve kurtarma değişmez sayıldı.

### 2B geliştirme (21 labirent x tohum {0, 1}; `sonuc/v3_2b.csv` v3 satırları, `sonuc/v4_2b.csv`)

| sürüm | başarı | çarpma olayı | temas (s) | süre ortanca (başarılı) |
| --- | --- | --- | --- | --- |
| v3 | 38/42 | 2 | 5.80 | 360 |
| v4 | 37/42 | 1 | 2.90 | 306 |

v4/v3 süre oranı (ikisi de başarılı, 36 çift): ortanca 0.889, ortalama 0.927.

### MuJoCo v3 / v4 (900 s, ön bilgisiz)

Geliştirme ve sınama3 ayrı satırda. Sınama3 (13x13 / 17x17 t14..t18) bu aşamada üretildi; v4'ün sınama3 sonuçlarına geliştirme bitene kadar bakılmadı. Sınama2 görülmüş kümedir, yalnız gerileme denetimi.

| küme | sürüm | başarı | süre ortanca (başarılı, s) | v4/v3 süre ortanca (ort; çift) | puan ort | düz hız ort (m/s) | hızlı kip payı (düz süre) | 0,10 m/s altı kuyruk (s) | çarpma olayı | temas (s) | en küçük duvar payı (m; koşu p01 ortancası) | payı < 5 mm koşu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme | v3 | 30/37 | 327 |  | 1105 | 0.227 | 0.23 | 1771 | 0 | 0.00 | 0.014 (0.099) | 0/37 |
| geliştirme | v4 | 33/37 | 292 | 0.883 (0.909; 30) | 1199 | 0.275 | 0.70 | 357 | 0 | 0.00 | -0.001 (0.111) | 4/37 |
| sınama3 | v3 | 14/20 | 635 |  | 914 | 0.223 | 0.21 | 1306 | 1 | 0.05 | -0.001 (0.102) | 2/20 |
| sınama3 | v4 | 17/20 | 594 | 0.884 (0.906; 14) | 1042 | 0.269 | 0.68 | 314 | 0 | 0.00 | -0.001 (0.097) | 3/20 |

Duvar payı gerçek pozdan ölçülür: ayak izi kutusu (±0,264 x ±0,262 m) ile 2B duvar çizgileri arası, her 2. adım (`kesif.hiz_tani`). -0,001 = kutu çizgiye değdi. MuJoCo temas bayrağı bu anların çoğunda 0 kaldı (temas sütunu); çarpışma geometrisinin kutudan birkaç mm farkı olabilir. Yine de bu, payın tükendiği andır.

Sonradan bakıldı (sınama2, görülmüş küme; v4 koşulan satırlar):

| küme | sürüm | başarı | süre ortanca (başarılı, s) | v4/v3 süre ortanca (ort; çift) | puan ort | düz hız ort (m/s) | hızlı kip payı (düz süre) | 0,10 m/s altı kuyruk (s) | çarpma olayı | temas (s) | en küçük duvar payı (m; koşu p01 ortancası) | payı < 5 mm koşu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sınama2 (sonradan bakıldı) | v3 | 15/20 | 731 |  | 958 | 0.221 | 0.21 | 1327 | 0 | 0.00 | -0.001 (0.099) | 2/20 |
| sınama2 (sonradan bakıldı) | v4 | 17/20 | 648 | 0.842 (0.821; 15) | 1062 | 0.272 | 0.69 | 273 | 2 | 6.15 | -0.001 (0.109) | 3/20 |

Hız sınıfı (sınama2'de v3'ün süreye sığmadığı 17x17_t11 ve t12; sonradan bakıldı):

| sahne | tohum | v3 durum / süre | v4 durum / süre | v4 p_en | v4 yol (m) |
| --- | --- | --- | --- | --- | --- |
| labirent_17x17_t11 | 0 | fail_sure / 900.05 | fail_sure / 900.05 | 0.6006 | 203.017 |
| labirent_17x17_t11 | 1 | fail_sure / 900.05 | fail_sure / 900.05 | 0.6007 | 205.067 |
| labirent_17x17_t12 | 0 | fail_sure / 900.05 | fail_sure / 900.05 | 0.8451 | 211.966 |
| labirent_17x17_t12 | 1 | fail_sure / 900.05 | basari / 837.85 | 1.0 | 196.045 |

**Karar kuralı** (sınama3): v4 başarısı v3'ten az değil (14 / 17) ve çarpma artmadı (1 / 0) -> sağlandı, `VARSAYILAN_SURUM = "v4"` (sonra v3'e döndü: v5 bölümü).

Kalan başarısızlıklar (v4):

| küme | sahne | tohum | durum | süre | p_en | yol (m) | çarpma | son olaylar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme | labirent_13x13_t2 | 0 | fail_sure | 900.05 | 0.9074 | 200.254 | 0 | 12.7:kurtarma; 251.7:kurtarma; 430.2:kurtarma |
| geliştirme | labirent_17x17_t4 | 0 | fail_sure | 900.05 | 0.5073 | 206.634 | 0 | 366.0:kurtarma; 698.7:kurtarma |
| geliştirme | labirent_17x17_t4 | 1 | fail_sure | 900.05 | 0.5375 | 210.31 | 0 | 375.6:kurtarma |
| geliştirme | labirent_17x17_t5 | 1 | fail_sure | 900.05 | 0.944 | 214.968 | 0 | 838.6:kurtarma |
| sınama3 | labirent_13x13_t15 | 1 | fail_sure | 900.05 | 0.9679 | 205.004 | 0 | 849.0:kurtarma; 876.8:kurtarma |
| sınama3 | labirent_17x17_t18 | 0 | fail_sure | 900.05 | 0.6887 | 202.101 | 0 | 149.9:kurtarma; 671.9:kurtarma |
| sınama3 | labirent_17x17_t18 | 1 | fail_sure | 900.05 | 0.6891 | 200.495 | 0 | 60.0:kurtarma; 104.3:kurtarma |
| sınama2 | labirent_17x17_t11 | 0 | fail_sure | 900.05 | 0.6006 | 203.017 | 0 | 676.1:kurtarma |
| sınama2 | labirent_17x17_t11 | 1 | fail_sure | 900.05 | 0.6007 | 205.067 | 1 | 720.8:kurtarma; 725.6:kurtarma |
| sınama2 | labirent_17x17_t12 | 0 | fail_sure | 900.05 | 0.8451 | 211.966 | 0 |  |

## v5: dönüş / yay güvenliği (durunca dönüş denetimi, körlemesine dönmeme, yay kaçınma)

Geliştirme: MuJoCo geliştirme kümesi ve sınama2 (v4'ün iki çarpmasının tanısı sınama2 kayıtlarında yapıldı; bu yüzden sınama2 artık geliştirme sayılır). Sınama4 (13x13 / 17x17 t19..t23 x 2) bu aşamada üretildi; v5 kodu dondurulduktan sonra koşuldu, karar yalnız ona göre. v3 sınama4 koşuları v5 öncesi kod kopyasından, v4 sınama4 koşuları (yalnız karşılaştırma, karardan sonra) v4_kod kopyasından.

| küme | sürüm | başarı | çarpma olayı (koşu) | temas (s) | süre ortanca (başarılı, s) | süre oranı / v4 (ortanca; çift) | süre oranı / v3 | puan ort | kurtarma | duvar payı < 5 mm koşu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme | v3 | 30/37 | 0 (0) | 0.00 | 327 |  |  | 1105 | 39 | 0/37 |
| geliştirme | v4 | 33/37 | 0 (0) | 0.00 | 292 |  | 0.883; 30 | 1199 | 17 | 4/37 |
| geliştirme | v5 | 32/37 | 1 (1) | 0.25 | 286 | 0.999; 32 | 0.893; 29 | 1172 | 14 | 1/37 |
| sınama2 (görülmüş, tanı) | v3 | 15/20 | 0 (0) | 0.00 | 731 |  |  | 958 | 35 | 2/20 |
| sınama2 (görülmüş, tanı) | v4 | 17/20 | 2 (2) | 6.15 | 648 |  | 0.842; 15 | 1062 | 12 | 3/20 |
| sınama2 (görülmüş, tanı) | v5 | 17/20 | 0 (0) | 0.00 | 606 | 0.981; 16 | 0.833; 15 | 1078 | 16 | 2/20 |
| **sınama4** (YENİ) | v3 | 12/20 | 0 (0) | 0.00 | 464 |  |  | 856 | 30 | 0/20 |
| **sınama4** (YENİ) | v4 | 12/20 | 0 (0) | 0.00 | 426 |  | 0.877; 12 | 877 | 13 | 5/20 |
| **sınama4** (YENİ) | v5 | 12/20 | 0 (0) | 0.00 | 389 | 0.964; 12 | 0.845; 12 | 886 | 19 | 0/20 |

**Karar kuralı** (sınama4): v5 başarısı v3'ten az değil (12 / 12) ve çarpma artmadı (0 / 0) -> sağlandı.

Bütün kümelerde çarpma olayı (koşu sayısı): v3 0 (77), v4 2 (77), v5 1 (77). "Çarpma sıfır" hedefi yalnız v3'te tutuyor; bu yüzden `VARSAYILAN_SURUM` v3'e döndü (sınama4 kuralı v5 için sağlansa da). v5 seçmeli: `surum_ayari("v5")`.

Çarpmalı ya da başarısız v5 koşuları:

| küme | sahne | tohum | durum | süre | p_en | çarpma | temas (s) | son olaylar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geliştirme | labirent_13x13_t2 | 0 | fail_sure | 900.05 | 0.908 | 0 | 0.0 | 12.7:kurtarma |
| geliştirme | labirent_13x13_t2 | 2 | fail_sure | 900.05 | 0.9062 | 0 | 0.0 | 475.1:kurtarma |
| geliştirme | labirent_17x17_t1 | 1 | basari | 349.95 | 1.0 | 1 | 0.25 | 335.4:disa_acik_sinir; 339.8:disa_acik_sinir; 340.8:cikis_goruldu |
| geliştirme | labirent_17x17_t4 | 0 | fail_sure | 900.05 | 0.5482 | 0 | 0.0 |  |
| geliştirme | labirent_17x17_t4 | 1 | fail_sure | 900.05 | 0.5402 | 0 | 0.0 | 729.5:kurtarma |
| geliştirme | labirent_17x17_t5 | 1 | fail_sure | 900.05 | 0.9429 | 0 | 0.0 | 221.1:kurtarma |
| sınama2 | labirent_17x17_t11 | 0 | fail_sure | 900.05 | 0.6005 | 0 | 0.0 | 266.2:kurtarma |
| sınama2 | labirent_17x17_t12 | 0 | fail_sure | 900.05 | 0.8448 | 0 | 0.0 |  |
| sınama2 | labirent_17x17_t12 | 1 | fail_sure | 900.05 | 0.8545 | 0 | 0.0 | 76.6:kurtarma |
| sınama4 | labirent_17x17_t19 | 0 | fail_sure | 900.05 | 0.7881 | 0 | 0.0 | 221.5:kurtarma |
| sınama4 | labirent_17x17_t19 | 1 | fail_sure | 900.05 | 0.788 | 0 | 0.0 | 524.2:kurtarma |
| sınama4 | labirent_17x17_t20 | 0 | fail_sure | 900.05 | 0.7211 | 0 | 0.0 | 716.2:kurtarma; 723.9:kurtarma; 731.7:kurtarma; 739.6:kurtarma; 746.2:kurtarma; 753.9:kurtarma; 760.5:kurtarma |
| sınama4 | labirent_17x17_t20 | 1 | fail_sure | 900.05 | 0.7436 | 0 | 0.0 |  |
| sınama4 | labirent_17x17_t21 | 0 | fail_sure | 900.05 | 0.8141 | 0 | 0.0 | 185.6:kurtarma; 525.8:kurtarma |
| sınama4 | labirent_17x17_t21 | 1 | fail_sure | 900.05 | 0.8132 | 0 | 0.0 | 48.1:kurtarma; 574.3:kurtarma |
| sınama4 | labirent_17x17_t23 | 0 | fail_sure | 900.05 | 0.941 | 0 | 0.0 | 735.1:disa_acik_sinir |
| sınama4 | labirent_17x17_t23 | 1 | fail_sure | 900.05 | 0.9387 | 0 | 0.0 | 223.6:kurtarma; 234.9:kurtarma |

## Başarısızlıklar (129)

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
| v2_2b.csv | kesif | labirent_17x17_t3 | 3 | 0.14 | fail_sure | 900.0 | - / kesif | 863.2:kurtarma/on_engel |
| v2_2b.csv | kesif | labirent_17x17_t3 | 4 | 0.14 | fail_sure | 900.0 | - / kesif | 639.8:kurtarma/on_engel |
| v2_2b.csv | kesif | labirent_13x13_t2 | 1 | 0.14 | fail_sure | 900.0 | - / kesif | 206.2:kurtarma/on_engel |
| v3_2b.csv | kesif | labirent_17x17_t4 | 0 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v3_2b.csv | kesif | labirent_17x17_t4 | 1 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v3_2b.csv | kesif | labirent_17x17_t5 | 1 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v3_2b.csv | kesif | labirent_17x17_t4 | 0 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v3_2b.csv | kesif | labirent_17x17_t4 | 1 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v3_2b.csv | kesif | labirent_17x17_t5 | 1 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v3_2b.csv | kesif | labirent_13x13_t2 | 1 | 0.14 | fail_sure | 900.0 | - / kesif | 206.2:kurtarma/on_engel |
| v3_2b.csv | kesif | labirent_13x13_t2 | 1 | 0.14 | fail_sure | 900.0 | - / kesif | 206.2:kurtarma/on_engel |
| v4_2b.csv | kesif | labirent_17x17_t2 | 0 | 0.14 | fail_sure | 900.0 | - / kesif | 58.9:kurtarma/on_engel; 288.2:kurtarma/sikisma; 293.1:kurtarma/on_engel; 537.5:kurtarma/sikisma; 687.4:kurtarma/on_engel |
| v4_2b.csv | kesif | labirent_17x17_t4 | 0 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v4_2b.csv | kesif | labirent_17x17_t4 | 1 | 0.14 | fail_sure | 900.0 | - / kesif |  |
| v4_2b.csv | kesif | labirent_17x17_t5 | 0 | 0.14 | fail_sure | 900.0 | - / kesif | 196.2:kurtarma/on_engel |
| v4_2b.csv | kesif | labirent_17x17_t5 | 1 | 0.14 | fail_sure | 900.0 | - / kesif | 765.8:kurtarma/on_engel |
