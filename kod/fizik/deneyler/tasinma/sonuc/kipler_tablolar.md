# Kip karşılaştırması: tablolar (kipler_rapor.py üretir)

## sinama (720 koşu; tohum 5, 6)

Hücre: doğru varış / sessiz hata (yanlış yerde "vardım") / güvenli durma ("yardım") / süre doldu; koşul başına 12 koşu (6 koridor x 2 tohum).

| Koşul | v3 | izleme | algi | izleme_algi | yanlış alarm (algi / izleme_algi) | fark etme (algi / izleme_algi) | temaslı koşu (v3 / izleme / algi / izleme_algi) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| taban | 12 / 0 / 0 / 0 | 12 / 0 / 0 / 0 | 12 / 0 / 0 / 0 | 12 / 0 / 0 / 0 | 0 / 0 | - / - | 0 / 0 / 0 / 0 |
| okul_hafif | 11 / 1 / 0 / 0 | 12 / 0 / 0 / 0 | 6 / 0 / 6 / 0 | 6 / 0 / 6 / 0 | 8 / 8 | - / - | 0 / 0 / 1 / 0 |
| okul_orta | 5 / 5 / 0 / 2 | 8 / 4 / 0 / 0 | 2 / 0 / 10 / 0 | 2 / 0 / 10 / 0 | 10 / 10 | - / - | 1 / 0 / 3 / 3 |
| taban+ayni_uzak | 2 / 8 / 0 / 2 | 0 / 0 / 0 / 12 | 12 / 0 / 0 / 0 | 12 / 0 / 0 / 0 | 0 / 0 | 12/12 (0.8 s) / 12/12 (0.8 s) | 0 / 0 / 0 / 0 |
| taban+kucuk | 3 / 7 / 0 / 2 | 1 / 6 / 0 / 5 | 12 / 0 / 0 / 0 | 11 / 1 / 0 / 0 | 0 / 0 | 12/12 (0.8 s) / 11/12 (5.9 s) | 0 / 0 / 0 / 0 |
| taban+ters180 | 8 / 4 / 0 / 0 | 0 / 3 / 0 / 9 | 12 / 0 / 0 / 0 | 10 / 2 / 0 / 0 | 0 / 0 | 10/12 (2.5 s) / 10/12 (4.6 s) | 0 / 0 / 0 / 0 |
| taban+baska_koridor | 0 / 9 / 0 / 3 | 0 / 2 / 0 / 10 | 0 / 1 / 11 / 0 | 0 / 1 / 11 / 0 | 0 / 0 | 12/12 (0.8 s) / 12/12 (0.8 s) | 0 / 0 / 0 / 0 |
| kapi_2 | 10 / 1 / 0 / 1 | 12 / 0 / 0 / 0 | 3 / 0 / 9 / 0 | 4 / 0 / 8 / 0 | 11 / 11 | - / - | 0 / 0 / 0 / 0 |
| cam_2 | 11 / 1 / 0 / 0 | 11 / 1 / 0 / 0 | 1 / 0 / 11 / 0 | 1 / 0 / 11 / 0 | 11 / 11 | - / - | 0 / 0 / 0 / 0 |
| donussuz_3 | 11 / 1 / 0 / 0 | 12 / 0 / 0 / 0 | 11 / 0 / 1 / 0 | 12 / 0 / 0 / 0 | 1 / 0 | - / - | 1 / 0 / 1 / 0 |
| kapi_2+kucuk | 4 / 7 / 0 / 1 | 1 / 7 / 0 / 4 | 2 / 0 / 10 / 0 | 2 / 0 / 10 / 0 | 8 / 8 | 11/11 (0.8 s) / 11/11 (0.8 s) | 0 / 0 / 0 / 0 |
| cam_2+kucuk | 5 / 7 / 0 / 0 | 1 / 8 / 0 / 3 | 1 / 0 / 11 / 0 | 1 / 0 / 11 / 0 | 9 / 9 | 7/7 (0.8 s) / 7/7 (0.8 s) | 0 / 0 / 0 / 0 |
| donussuz_3+kucuk | 8 / 4 / 0 / 0 | 2 / 9 / 0 / 1 | 8 / 0 / 2 / 2 | 8 / 2 / 1 / 1 | 0 / 0 | 12/12 (0.8 s) / 11/12 (0.8 s) | 0 / 0 / 3 / 2 |
| okul_agir | 1 / 7 / 0 / 4 | 2 / 8 / 0 / 2 | 1 / 1 / 10 / 0 | 1 / 1 / 10 / 0 | 12 / 12 | - / - | 3 / 1 / 3 / 1 |
| kapi_3 | 8 / 4 / 0 / 0 | 12 / 0 / 0 / 0 | 1 / 0 / 11 / 0 | 1 / 0 / 11 / 0 | 11 / 11 | - / - | 0 / 0 / 0 / 0 |

### Gruplar (ölçüt: [('uyum', 0.75), ('std', 0.05)])

| Koşul grubu (koşu / kip) | Kip | Doğru davranış | Sessiz hata | Güvenli durma | Süre doldu | Yanlış alarm | Temaslı koşu | Ölçütle önlenen sessiz hata | Ölçütle gereksiz durma |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz harita (12) | v3 | 12 / 12 | 0 | 0 | 0 | - | 0 | 0 / 0 | 0 / 12 |
|  | izleme | 12 / 12 | 0 | 0 | 0 | - | 0 | 0 / 0 | 0 / 12 |
|  | algi | 12 / 12 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 / 12 |
|  | izleme_algi | 12 / 12 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 / 12 |
| okul günü hafif (12) | v3 | 11 / 12 | 1 | 0 | 0 | - | 0 | 0 / 1 | 0 / 11 |
|  | izleme | 12 / 12 | 0 | 0 | 0 | - | 0 | 0 / 0 | 0 / 12 |
|  | algi | 6 / 12 | 0 | 6 | 0 | 8 | 1 | 0 / 0 | 0 / 6 |
|  | izleme_algi | 6 / 12 | 0 | 6 | 0 | 8 | 0 | 0 / 0 | 0 / 6 |
| okul günü orta (12) | v3 | 5 / 12 | 5 | 0 | 2 | - | 1 | 4 / 5 | 1 / 5 |
|  | izleme | 8 / 12 | 4 | 0 | 0 | - | 0 | 3 / 4 | 0 / 8 |
|  | algi | 2 / 12 | 0 | 10 | 0 | 10 | 3 | 0 / 0 | 0 / 2 |
|  | izleme_algi | 2 / 12 | 0 | 10 | 0 | 10 | 3 | 0 / 0 | 0 / 2 |
| okul günü ağır (12) | v3 | 1 / 12 | 7 | 0 | 4 | - | 3 | 5 / 7 | 0 / 1 |
|  | izleme | 2 / 12 | 8 | 0 | 2 | - | 1 | 8 / 8 | 0 / 2 |
|  | algi | 1 / 12 | 1 | 10 | 0 | 12 | 3 | 1 / 1 | 0 / 1 |
|  | izleme_algi | 1 / 12 | 1 | 10 | 0 | 12 | 1 | 1 / 1 | 1 / 1 |
| tek etken 2. kademe: kapı %25, cam %50 (24) | v3 | 21 / 24 | 2 | 0 | 1 | - | 0 | 0 / 2 | 0 / 21 |
|  | izleme | 23 / 24 | 1 | 0 | 0 | - | 0 | 0 / 1 | 0 / 23 |
|  | algi | 4 / 24 | 0 | 20 | 0 | 22 | 0 | 0 / 0 | 0 / 4 |
|  | izleme_algi | 5 / 24 | 0 | 19 | 0 | 22 | 0 | 0 / 0 | 0 / 5 |
| tek etken 3. kademe: kapı %50, dönüşsüz %50 (24) | v3 | 19 / 24 | 5 | 0 | 0 | - | 1 | 0 / 5 | 3 / 19 |
|  | izleme | 24 / 24 | 0 | 0 | 0 | - | 0 | 0 / 0 | 4 / 24 |
|  | algi | 12 / 24 | 0 | 12 | 0 | 12 | 1 | 0 / 0 | 3 / 12 |
|  | izleme_algi | 13 / 24 | 0 | 11 | 0 | 11 | 0 | 0 / 0 | 3 / 13 |
| taşınma, temiz harita (4 tür) (48) | v3 | 13 / 48 | 28 | 0 | 7 | - | 0 | 17 / 28 | 0 / 13 |
|  | izleme | 1 / 48 | 11 | 0 | 36 | - | 0 | 8 / 11 | 0 / 1 |
|  | algi | 47 / 48 | 1 | 11 | 0 | 0 | 0 | 0 / 1 | 1 / 36 |
|  | izleme_algi | 44 / 48 | 4 | 11 | 0 | 0 | 0 | 2 / 4 | 0 / 33 |
| taşınma (küçük) + eskime (kapı / cam / dönüşsüz) (36) | v3 | 17 / 36 | 18 | 0 | 1 | - | 0 | 7 / 18 | 1 / 17 |
|  | izleme | 4 / 36 | 24 | 0 | 8 | - | 0 | 22 / 24 | 1 / 4 |
|  | algi | 11 / 36 | 0 | 23 | 2 | 17 | 3 | 0 / 0 | 2 / 11 |
|  | izleme_algi | 11 / 36 | 2 | 22 | 1 | 17 | 2 | 1 / 2 | 1 / 11 |

### Yanlış alarmlar (taşıma yokken / taşımadan önce)

| Koşul | Kip | yanlış alarmlı koşu | ilk alarm nedeni: poz sıçraması / uyum (10 taramanın 8'i kötü) / bitti ama şüpheli | alarm taramasında geçiş > 0,10 / uyum < 0,60 | yanlış alarmlı koşuların sonucu (doğru / sessiz / güvenli / süre) |
| --- | --- | --- | --- | --- | --- |
| okul_hafif | algi | 8 | 0 / 8 / 0 | 8 / 0 | 2 / 0 / 6 / 0 |
| okul_hafif | izleme_algi | 8 | 0 / 8 / 0 | 8 / 0 | 2 / 0 / 6 / 0 |
| okul_orta | algi | 10 | 1 / 9 / 0 | 8 / 0 | 0 / 0 / 10 / 0 |
| okul_orta | izleme_algi | 10 | 0 / 10 / 0 | 9 / 1 | 0 / 0 / 10 / 0 |
| kapi_2 | algi | 11 | 0 / 11 / 0 | 11 / 0 | 2 / 0 / 9 / 0 |
| kapi_2 | izleme_algi | 11 | 0 / 11 / 0 | 11 / 0 | 3 / 0 / 8 / 0 |
| cam_2 | algi | 11 | 0 / 11 / 0 | 11 / 0 | 0 / 0 / 11 / 0 |
| cam_2 | izleme_algi | 11 | 0 / 11 / 0 | 11 / 0 | 0 / 0 / 11 / 0 |
| donussuz_3 | algi | 1 | 0 / 1 / 0 | 0 / 0 | 0 / 0 / 1 / 0 |
| kapi_2+kucuk | algi | 8 | 0 / 8 / 0 | 8 / 0 | 1 / 0 / 7 / 0 |
| kapi_2+kucuk | izleme_algi | 8 | 0 / 8 / 0 | 8 / 0 | 1 / 0 / 7 / 0 |
| cam_2+kucuk | algi | 9 | 0 / 9 / 0 | 9 / 0 | 0 / 0 / 9 / 0 |
| cam_2+kucuk | izleme_algi | 9 | 0 / 9 / 0 | 9 / 0 | 0 / 0 / 9 / 0 |
| okul_agir | algi | 12 | 2 / 10 / 0 | 10 / 0 | 1 / 1 / 10 / 0 |
| okul_agir | izleme_algi | 12 | 0 / 12 / 0 | 11 / 1 | 1 / 1 / 10 / 0 |
| kapi_3 | algi | 11 | 0 / 11 / 0 | 11 / 0 | 0 / 0 / 11 / 0 |
| kapi_3 | izleme_algi | 11 | 0 / 11 / 0 | 11 / 0 | 0 / 0 / 11 / 0 |

Ölçütün kip başına etkisi (sinama): v3 önlenen 33 / 66 sessiz hata, gereksiz durma 5 / 99 doğru varış; izleme önlenen 41 / 48 sessiz hata, gereksiz durma 5 / 86 doğru varış; algi önlenen 1 / 2 sessiz hata, gereksiz durma 6 / 84 doğru varış; izleme_algi önlenen 4 / 7 sessiz hata, gereksiz durma 5 / 83 doğru varış

İkincil (seçilmedi; geliştirmenin en iyi tek adaylı kuralı [('uyum', 0.75)]): v3 önlenen 29 / 66, gereksiz 0 / 99; izleme önlenen 25 / 48, gereksiz 0 / 86; algi önlenen 0 / 2, gereksiz 0 / 84; izleme_algi önlenen 1 / 7, gereksiz 1 / 83

## gelistirme (168 koşu; tohum 7, 8)

Hücre: doğru varış / sessiz hata (yanlış yerde "vardım") / güvenli durma ("yardım") / süre doldu; koşul başına 12 koşu (6 koridor x 2 tohum).

| Koşul | v3 | izleme | yanlış alarm (algi / izleme_algi) | fark etme (algi / izleme_algi) | temaslı koşu (v3 / izleme) |
| --- | --- | --- | --- | --- | --- |
| taban | 12 / 0 / 0 / 0 | 12 / 0 / 0 / 0 | - | - | 0 / 0 |
| okul_hafif | 8 / 1 / 0 / 3 | 11 / 1 / 0 / 0 | - | - | 0 / 0 |
| okul_orta | 5 / 5 / 0 / 2 | 9 / 3 / 0 / 0 | - | - | 0 / 0 |
| kapi_3 | 8 / 3 / 0 / 1 | 12 / 0 / 0 / 0 | - | - | 0 / 0 |
| cam_3 | 9 / 3 / 0 / 0 | 12 / 0 / 0 / 0 | - | - | 0 / 0 |
| taban+kucuk | 8 / 4 / 0 / 0 | 2 / 9 / 0 / 1 | - | - | 0 / 0 |
| taban+ayni_uzak | 4 / 6 / 0 / 2 | 0 / 3 / 0 / 9 | - | - | 0 / 0 |

### Gruplar (ölçüt: [('uyum', 0.75), ('std', 0.05)])

| Koşul grubu (koşu / kip) | Kip | Doğru davranış | Sessiz hata | Güvenli durma | Süre doldu | Yanlış alarm | Temaslı koşu | Ölçütle önlenen sessiz hata | Ölçütle gereksiz durma |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz harita (12) | v3 | 12 / 12 | 0 | 0 | 0 | - | 0 | 0 / 0 | 0 / 12 |
|  | izleme | 12 / 12 | 0 | 0 | 0 | - | 0 | 0 / 0 | 0 / 12 |
| okul günü hafif (12) | v3 | 8 / 12 | 1 | 0 | 3 | - | 0 | 0 / 1 | 0 / 8 |
|  | izleme | 11 / 12 | 1 | 0 | 0 | - | 0 | 1 / 1 | 0 / 11 |
| okul günü orta (12) | v3 | 5 / 12 | 5 | 0 | 2 | - | 0 | 4 / 5 | 0 / 5 |
|  | izleme | 9 / 12 | 3 | 0 | 0 | - | 0 | 2 / 3 | 1 / 9 |
| tek etken 3. kademe: kapı %50, dönüşsüz %50 (24) | v3 | 17 / 24 | 6 | 0 | 1 | - | 0 | 3 / 6 | 0 / 17 |
|  | izleme | 24 / 24 | 0 | 0 | 0 | - | 0 | 0 / 0 | 1 / 24 |
| taşınma, temiz harita (4 tür) (24) | v3 | 12 / 24 | 10 | 0 | 2 | - | 0 | 8 / 10 | 0 / 12 |
|  | izleme | 2 / 24 | 12 | 0 | 10 | - | 0 | 8 / 12 | 0 / 2 |

Ölçütün kip başına etkisi (gelistirme): v3 önlenen 15 / 22 sessiz hata, gereksiz durma 0 / 54 doğru varış; izleme önlenen 11 / 16 sessiz hata, gereksiz durma 2 / 58 doğru varış

İkincil (seçilmedi; geliştirmenin en iyi tek adaylı kuralı [('uyum', 0.75)]): v3 önlenen 13 / 22, gereksiz 0 / 54; izleme önlenen 7 / 16, gereksiz 1 / 58
