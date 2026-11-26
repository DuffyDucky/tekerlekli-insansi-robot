# Bağımsız hüküm 3: düzen x tehlike sınıfı

Kaynak: `sonuc/hukum3.csv` (hüküm koşusu), `sonuc/hukum3_fiz.csv` (hakemin düşme saydığı görevler, koşu sürdürülerek).
Ön kayıt: `sonuc/on_kayit_3.md`. Tohum 211-220, bütün sahneler yeni (`h3_*`). Üretici: `py -3 hukum3.py tablo`.

Hücre (uçurum sınıfları): `hakem düşme / koşu · fiziksel düşme / sürdürülen · en küçük pay cm`. Yanlış alarm: `durma / koşu`. Hata varsa ayrıca yazılır.

| sınıf | 6 (4OD+2AD (SECIM_2)) | 10 (6OD+4AD (SECIM_3)) | 14 (8WRD+4AD+2YR40 (önceki secim.json, t2_hukum)) | 3A (8WRaD+4AD+2YR40 (SECIM_3A)) | 3B (6OD+4AD + kural (SECIM_3B)) |
| --- | --- | --- | --- | --- | --- |
| Merdiven başı / sahanlık kenarı, ileri | 0 / 162 · 0 · 4,3 | 0 / 162 · 0 · 4,9 | 0 / 162 · 0 · 6,2 | 0 / 162 · 0 · 6,2 | 0 / 162 · 0 · 6,3 |
| Sahanlık köşesi, ileri | **2 / 108** · 1 / 2 · -6,3 | 0 / 108 · 0 · 4,9 | 0 / 108 · 0 · 6,2 | 0 / 108 · 0 · 6,2 | 0 / 108 · 0 · 5,8 |
| Kuyu, ileri | 0 / 96 · 0 · 5,6 | 0 / 96 · 0 · 6,2 | 0 / 96 · 0 · 7,5 | 0 / 96 · 0 · 7,5 | 0 / 96 · 0 · 6,2 |
| Dar açıklık 0,48-0,85 m, ileri | 0 / 360 · 0 · 3,3 | 0 / 360 · 0 · 5,7 | 0 / 360 · 0 · 5,7 | 0 / 360 · 0 · 5,7 | 0 / 360 · 0 · 5,7 |
| Dar açıklığa geri gidiş | **21 / 288** · 19 / 21 · -9,2 | 0 / 288 · 0 · 5,1 | 0 / 288 · 0 · 4,9 | 0 / 288 · 0 · 4,9 | 0 / 288 · 0 · 6,5 |
| Geniş kenara geri gidiş | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 7,5 | 0 / 72 · 0 · 9,8 |
| Yerinde dönüş, geniş kenar | 0 / 72 · 0 · 3,9 | 0 / 72 · 0 · 3,9 | 0 / 72 · 0 · 4,4 | 0 / 72 · 0 · 4,4 | 0 / 72 · 0 · 7,9 |
| Yerinde dönüş, dar açıklık yanında | **109 / 384** · 0 / 109 · -9,5 | **110 / 384** · 0 / 110 · -9,3 | 0 / 384 · 0 · 0,4 | 0 / 384 · 0 · 0,4 | 0 / 384 · 0 · 3,8 |
| Dar yarık 8,5-16 cm | **238 / 840** · 118 / 238 · -7,6 | **68 / 840** · 17 / 68 · -5,1 | **2 / 840** · 0 / 2 · -0,4 | 0 / 840 · 0 · 0,3 | **61 / 840** · 27 / 61 · -4,5 |
| Eğik yarık 15-45° | **83 / 288** · 26 / 83 · -7,2 | **11 / 288** · 1 / 11 · -4,7 | 0 / 288 · 0 · 4,1 | 0 / 288 · 0 · 4,6 | **5 / 288** · 1 / 5 · -1,5 |
| İniş rampasının ucunda düşüş | 0 / 72 · 0 · 2,7 | 0 / 72 · 0 · 3,4 | 0 / 72 · 0 · 3,8 | 0 / 72 · 0 · 3,8 | 0 / 72 · 0 · 3,5 |
| Yanlış alarm | 0 / 585 | 0 / 585 | 0 / 585 | 0 / 585 | 0 / 585 |
| **Uçurum toplamı** | **453 / 2742** · 164 / 453 · -9,5 | **189 / 2742** · 18 / 189 · -9,3 | **2 / 2742** · 0 / 2 · -0,4 | **0 / 2742** · 0 / 0 · 0,3 | **66 / 2742** · 28 / 66 · -4,5 |
| **Yanlış durma toplamı** | **0 / 585** | **0 / 585** | **0 / 585** | **0 / 585** | **0 / 585** |

## Ön kayıtlı ölçüte göre

Ölçüt (SONUC.md'den aynen): uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma. Izgaradaki bütün hızlar (0,10 / 0,20 / 0,25 / 0,39 m/s) sayılır. Hatalı koşu geçti sayılmaz.

| düzen | sensör | hakem düşme | yanlış durma | hata | hüküm |
| --- | --- | --- | --- | --- | --- |
| 4OD+2AD (SECIM_2) | 6 | 453 / 2742 | 0 / 585 | 0 | **GEÇMEDİ** |
| 6OD+4AD (SECIM_3) | 10 | 189 / 2742 | 0 / 585 | 0 | **GEÇMEDİ** |
| 8WRD+4AD+2YR40 (önceki secim.json, t2_hukum) | 14 | 2 / 2742 | 0 / 585 | 0 | **GEÇMEDİ** |
| 8WRaD+4AD+2YR40 (SECIM_3A) | 14 | 0 / 2742 | 0 / 585 | 0 | **GEÇTİ** |
| 6OD+4AD + kural (SECIM_3B) | 10 | 66 / 2742 | 0 / 585 | 0 | **GEÇMEDİ** |

## Hıza göre hakem düşmesi (ikincil)

Yerinde dönüş koşuları (dar ve geniş, 456 / düzen) ilerleme hızı taşımaz, bu tabloda yoktur (w ±1 rad/s; 3B'de kural geri yaya çevirir).

| düzen | 0.10 m/s | 0.20 m/s | 0.25 m/s | 0.39 m/s |
| --- | --- | --- | --- | --- |
| 6 | 118 / 816 | 0 / 18 | 118 / 816 | 108 / 636 |
| 10 | 22 / 816 | 0 / 18 | 20 / 816 | 37 / 636 |
| 14 | 1 / 816 | 0 / 18 | 1 / 816 | 0 / 636 |
| 3A | 0 / 816 | 0 / 18 | 0 / 816 | 0 / 636 |
| 3B | 22 / 816 | 0 / 18 | 17 / 816 | 27 / 636 |

## Ayrıntı: dar yarık, genişliğe göre (mm)

Hücre: `hakem düşme / koşu · en küçük pay cm`.

| düzen | 85 | 95 | 105 | 115 | 125 | 145 | 160 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 31 / 120 · -4,2 | 37 / 120 · -4,7 | 33 / 120 · -5,2 | 38 / 120 · -5,7 | 34 / 120 · -6,1 | 37 / 120 · -7,2 | 28 / 120 · -7,6 |
| 10 | 12 / 120 · -4,2 | 13 / 120 · -4,2 | 11 / 120 · -4,5 | 14 / 120 · -5,1 | 7 / 120 · -4,2 | 9 / 120 · -4,6 | 2 / 120 · -4,5 |
| 14 | 0 / 120 · 0,5 | 0 / 120 · 0,1 | 1 / 120 · -0,4 | 1 / 120 · -0,1 | 0 / 120 · 0,7 | 0 / 120 · 4,5 | 0 / 120 · 4,6 |
| 3A | 0 / 120 · 0,5 | 0 / 120 · 0,3 | 0 / 120 · 0,4 | 0 / 120 · 0,5 | 0 / 120 · 0,7 | 0 / 120 · 4,5 | 0 / 120 · 4,6 |
| 3B | 12 / 120 · -4,2 | 12 / 120 · -4,2 | 11 / 120 · -4,5 | 12 / 120 · -3,7 | 7 / 120 · -1,8 | 7 / 120 · -1,8 | 0 / 120 · 0,9 |

## Ayrıntı: dar yarık, açıya göre (°)

Hücre: `hakem düşme / koşu · en küçük pay cm`.

| düzen | -12 | -7 | 3 | 8 | 12 |
| --- | --- | --- | --- | --- | --- |
| 6 | 33 / 168 · -7,2 | 44 / 168 · -7,1 | 91 / 168 · -7,6 | 38 / 168 · -6,4 | 32 / 168 · -7,6 |
| 10 | 12 / 168 · -4,6 | 10 / 168 · -4,5 | 29 / 168 · -4,4 | 8 / 168 · -5,1 | 9 / 168 · -4,5 |
| 14 | 1 / 168 · -0,4 | 0 / 168 · 0,1 | 0 / 168 · 1,1 | 0 / 168 · 0,4 | 1 / 168 · -0,1 |
| 3A | 0 / 168 · 0,5 | 0 / 168 · 0,3 | 0 / 168 · 1,1 | 0 / 168 · 0,4 | 0 / 168 · 0,8 |
| 3B | 12 / 168 · -4,1 | 9 / 168 · -4,5 | 25 / 168 · -3,9 | 8 / 168 · -4,2 | 7 / 168 · -4,2 |

## Ayrıntı: eğik yarık, eksen açısına göre (°)

Hücre: `hakem düşme / koşu · en küçük pay cm`.

| düzen | 15 | 25 | 35 | 45 |
| --- | --- | --- | --- | --- |
| 6 | 27 / 72 · -6,6 | 21 / 72 · -5,6 | 22 / 72 · -7,2 | 13 / 72 · -4,7 |
| 10 | 7 / 72 · -4,7 | 4 / 72 · -1,1 | 0 / 72 · 1,6 | 0 / 72 · 2,0 |
| 14 | 0 / 72 · 4,1 | 0 / 72 · 4,2 | 0 / 72 · 4,8 | 0 / 72 · 5,4 |
| 3A | 0 / 72 · 4,6 | 0 / 72 · 4,9 | 0 / 72 · 4,8 | 0 / 72 · 5,8 |
| 3B | 5 / 72 · -1,5 | 0 / 72 · 1,4 | 0 / 72 · 4,0 | 0 / 72 · 6,2 |

## Ayrıntı: dar açıklık yanında dönüş, d'ye göre (m)

Hücre: `hakem düşme / koşu · en küçük pay cm`.

| düzen | 0.33 | 0.38 | 0.43 | 0.48 |
| --- | --- | --- | --- | --- |
| 6 | 65 / 96 · -9,5 | 44 / 96 · -4,5 | 0 / 96 · 0,5 | 0 / 96 · 5,7 |
| 10 | 65 / 96 · -9,3 | 45 / 96 · -4,5 | 0 / 96 · 0,5 | 0 / 96 · 5,7 |
| 14 | 0 / 96 · 7,3 | 0 / 96 · 0,4 | 0 / 96 · 2,0 | 0 / 96 · 5,7 |
| 3A | 0 / 96 · 7,3 | 0 / 96 · 0,4 | 0 / 96 · 2,0 | 0 / 96 · 5,7 |
| 3B | 0 / 96 · 4,6 | 0 / 96 · 3,8 | 0 / 96 · 7,0 | 0 / 96 · 12,1 |

## Ayrıntı: dar açıklığa geri, genişliğe göre (cm)

Hücre: `hakem düşme / koşu · en küçük pay cm`.

| düzen | 48 | 52 | 58 | 62 | 68 | 72 | 78 | 85 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 11 / 36 · -9,2 | 5 / 36 · -8,2 | 4 / 36 · -4,1 | 1 / 36 · -5,2 | 0 / 36 · 1,8 | 0 / 36 · 3,1 | 0 / 36 · 2,5 | 0 / 36 · 4,4 |
| 10 | 0 / 36 · 5,2 | 0 / 36 · 5,1 | 0 / 36 · 6,9 | 0 / 36 · 8,5 | 0 / 36 · 8,1 | 0 / 36 · 8,4 | 0 / 36 · 8,4 | 0 / 36 · 8,2 |
| 14 | 0 / 36 · 4,9 | 0 / 36 · 5,4 | 0 / 36 · 6,8 | 0 / 36 · 8,4 | 0 / 36 · 8,4 | 0 / 36 · 8,6 | 0 / 36 · 8,4 | 0 / 36 · 8,4 |
| 3A | 0 / 36 · 4,9 | 0 / 36 · 5,4 | 0 / 36 · 6,8 | 0 / 36 · 8,4 | 0 / 36 · 8,4 | 0 / 36 · 8,6 | 0 / 36 · 8,4 | 0 / 36 · 8,4 |
| 3B | 0 / 36 · 6,5 | 0 / 36 · 6,8 | 0 / 36 · 7,7 | 0 / 36 · 9,3 | 0 / 36 · 9,3 | 0 / 36 · 9,3 | 0 / 36 · 9,6 | 0 / 36 · 9,3 |

## Hakemin düşme saydığı koşular (en çok 60)

| kimlik | sınıf | sahne | açı | v | yanal | d | pay cm | tetik sensörü | neden | fiziksel (teker dz mm, eğim °, gövde) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hukum3-10-01159 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.33 | -4.28 | on_sag | yok | düşmedi (-1.2, 0.25, yok) |
| hukum3-10-01160 | donus_dar | h3_acik_48 | None | None | 0.26 | 0.33 | -9.28 | on_sag | yok | düşmedi (-0.9, 0.19, yok) |
| hukum3-10-01162 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.33 | -7.92 | on_sol | yok | düşmedi (-1.3, 0.27, yok) |
| hukum3-10-01163 | donus_dar | h3_acik_48 | None | None | 0.26 | 0.33 | -4.15 | on_sol | yok | düşmedi (-1.4, 0.29, yok) |
| hukum3-10-01166 | donus_dar | h3_acik_48 | None | None | 0.26 | 0.38 | -4.55 | on_sag | yok | düşmedi (-1.0, 0.22, yok) |
| hukum3-10-01168 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.38 | -3.06 | on_sol | yok | düşmedi (-1.3, 0.26, yok) |
| hukum3-10-01183 | donus_dar | h3_acik_52 | None | None | 0.04 | 0.33 | -4.26 | on_sag | yok | düşmedi (-1.2, 0.24, yok) |
| hukum3-10-01184 | donus_dar | h3_acik_52 | None | None | 0.26 | 0.33 | -8.94 | on_sag | yok | düşmedi (-0.8, 0.18, yok) |
| hukum3-10-01185 | donus_dar | h3_acik_52 | None | None | -0.25 | 0.33 | -0.06 | on_sol | yok | düşmedi (-0.0, 0.01, yok) |
| hukum3-10-01186 | donus_dar | h3_acik_52 | None | None | 0.04 | 0.33 | -8.02 | on_sol | yok | düşmedi (-1.4, 0.3, yok) |
| hukum3-10-01187 | donus_dar | h3_acik_52 | None | None | 0.26 | 0.33 | -3.95 | on_sol | yok | düşmedi (-1.4, 0.29, yok) |
| hukum3-10-01190 | donus_dar | h3_acik_52 | None | None | 0.26 | 0.38 | -3.85 | on_sag | yok | düşmedi (-0.9, 0.19, yok) |
| hukum3-10-01192 | donus_dar | h3_acik_52 | None | None | 0.04 | 0.38 | -2.87 | on_sol | yok | düşmedi (-1.2, 0.25, yok) |
| hukum3-10-01207 | donus_dar | h3_acik_58 | None | None | 0.04 | 0.33 | -3.01 | on_sag | yok | düşmedi (-2.0, 0.41, yok) |
| hukum3-10-01208 | donus_dar | h3_acik_58 | None | None | 0.26 | 0.33 | -8.34 | on_sag | yok | düşmedi (-0.7, 0.16, yok) |
| hukum3-10-01209 | donus_dar | h3_acik_58 | None | None | -0.25 | 0.33 | -1.65 | on_sol | yok | düşmedi (-0.9, 0.2, yok) |
| hukum3-10-01210 | donus_dar | h3_acik_58 | None | None | 0.04 | 0.33 | -7.7 | on_sol | yok | düşmedi (-1.2, 0.24, yok) |
| hukum3-10-01211 | donus_dar | h3_acik_58 | None | None | 0.26 | 0.33 | -3.79 | on_sol | yok | düşmedi (-1.3, 0.28, yok) |
| hukum3-10-01214 | donus_dar | h3_acik_58 | None | None | 0.26 | 0.38 | -3.75 | on_sag | yok | düşmedi (-0.9, 0.19, yok) |
| hukum3-10-01215 | donus_dar | h3_acik_58 | None | None | -0.25 | 0.38 | -0.3 | on_sol | yok | düşmedi (-0.1, 0.02, yok) |
| hukum3-10-01216 | donus_dar | h3_acik_58 | None | None | 0.04 | 0.38 | -2.59 | on_sol | yok | düşmedi (-1.2, 0.25, yok) |
| hukum3-10-01231 | donus_dar | h3_acik_62 | None | None | 0.04 | 0.33 | -0.67 | on_sag | yok | düşmedi (-0.2, 0.05, yok) |
| hukum3-10-01232 | donus_dar | h3_acik_62 | None | None | 0.26 | 0.33 | -8.41 | on_sag | yok | düşmedi (-0.8, 0.16, yok) |
| hukum3-10-01233 | donus_dar | h3_acik_62 | None | None | -0.25 | 0.33 | -2.98 | on_sol | yok | düşmedi (-1.5, 0.31, yok) |
| hukum3-10-01234 | donus_dar | h3_acik_62 | None | None | 0.04 | 0.33 | -7.64 | on_sol | yok | düşmedi (-1.3, 0.27, yok) |
| hukum3-10-01235 | donus_dar | h3_acik_62 | None | None | 0.26 | 0.33 | -2.4 | on_sol | yok | düşmedi (-1.9, 0.41, yok) |
| hukum3-10-01238 | donus_dar | h3_acik_62 | None | None | 0.26 | 0.38 | -3.52 | on_sag | yok | düşmedi (-1.1, 0.24, yok) |
| hukum3-10-01239 | donus_dar | h3_acik_62 | None | None | -0.25 | 0.38 | -0.84 | on_sol | yok | düşmedi (-0.3, 0.07, yok) |
| hukum3-10-01240 | donus_dar | h3_acik_62 | None | None | 0.04 | 0.38 | -2.69 | on_sol | yok | düşmedi (-1.4, 0.3, yok) |
| hukum3-10-01256 | donus_dar | h3_acik_68 | None | None | 0.26 | 0.33 | -6.37 | None | None | düşmedi (-0.6, 0.12, yok) |
| hukum3-10-01257 | donus_dar | h3_acik_68 | None | None | -0.25 | 0.33 | -3.76 | on_sol | yok | düşmedi (-2.6, 0.54, yok) |
| hukum3-10-01258 | donus_dar | h3_acik_68 | None | None | 0.04 | 0.33 | -6.83 | on_sol | yok | düşmedi (-0.8, 0.17, yok) |
| hukum3-10-01259 | donus_dar | h3_acik_68 | None | None | 0.26 | 0.33 | -0.25 | on_sol | yok | düşmedi (-0.0, 0.01, yok) |
| hukum3-10-01262 | donus_dar | h3_acik_68 | None | None | 0.26 | 0.38 | -3.32 | on_sag | yok | düşmedi (-1.1, 0.23, yok) |
| hukum3-10-01263 | donus_dar | h3_acik_68 | None | None | -0.25 | 0.38 | -2.09 | on_sol | yok | düşmedi (-1.9, 0.4, yok) |
| hukum3-10-01264 | donus_dar | h3_acik_68 | None | None | 0.04 | 0.38 | -2.34 | on_sol | yok | düşmedi (-1.2, 0.25, yok) |
| hukum3-10-01280 | donus_dar | h3_acik_72 | None | None | 0.26 | 0.33 | -6.15 | on_sag | yok | düşmedi (-0.7, 0.15, yok) |
| hukum3-10-01281 | donus_dar | h3_acik_72 | None | None | -0.25 | 0.33 | -4.19 | on_sol | yok | düşmedi (-2.8, 0.59, yok) |
| hukum3-10-01282 | donus_dar | h3_acik_72 | None | None | 0.04 | 0.33 | -5.5 | None | None | düşmedi (-0.8, 0.16, yok) |
| hukum3-10-01286 | donus_dar | h3_acik_72 | None | None | 0.26 | 0.38 | -2.75 | on_sag | yok | düşmedi (-1.6, 0.33, yok) |
| hukum3-10-01287 | donus_dar | h3_acik_72 | None | None | -0.25 | 0.38 | -2.54 | on_sol | yok | düşmedi (-2.2, 0.47, yok) |
| hukum3-10-01288 | donus_dar | h3_acik_72 | None | None | 0.04 | 0.38 | -2.21 | on_sol | yok | düşmedi (-1.4, 0.29, yok) |
| hukum3-10-01304 | donus_dar | h3_acik_78 | None | None | 0.26 | 0.33 | -5.94 | on_sag | yok | düşmedi (-0.7, 0.15, yok) |
| hukum3-10-01305 | donus_dar | h3_acik_78 | None | None | -0.25 | 0.33 | -4.98 | on_sol | yok | düşmedi (-2.3, 0.48, yok) |
| hukum3-10-01306 | donus_dar | h3_acik_78 | None | None | 0.04 | 0.33 | -5.53 | on_sol | yok | düşmedi (-0.8, 0.16, yok) |
| hukum3-10-01310 | donus_dar | h3_acik_78 | None | None | 0.26 | 0.38 | -1.12 | on_sag | yok | düşmedi (-0.8, 0.17, yok) |
| hukum3-10-01311 | donus_dar | h3_acik_78 | None | None | -0.25 | 0.38 | -2.55 | on_sol | yok | düşmedi (-3.0, 0.63, yok) |
| hukum3-10-01312 | donus_dar | h3_acik_78 | None | None | 0.04 | 0.38 | -1.0 | on_sol | yok | düşmedi (-0.6, 0.13, yok) |
| hukum3-10-01328 | donus_dar | h3_acik_85 | None | None | 0.26 | 0.33 | -5.5 | on_sag | yok | düşmedi (-0.8, 0.17, yok) |
| hukum3-10-01329 | donus_dar | h3_acik_85 | None | None | -0.25 | 0.33 | -5.49 | on_sol | yok | düşmedi (-2.2, 0.47, yok) |
| hukum3-10-01330 | donus_dar | h3_acik_85 | None | None | 0.04 | 0.33 | -5.28 | on_sol | yok | düşmedi (-0.9, 0.19, yok) |
| hukum3-10-01334 | donus_dar | h3_acik_85 | None | None | 0.26 | 0.38 | -0.13 | on_sag | yok | düşmedi (-0.0, 0.0, yok) |
| hukum3-10-01335 | donus_dar | h3_acik_85 | None | None | -0.25 | 0.38 | -2.96 | on_sol | yok | düşmedi (-1.8, 0.37, yok) |
| hukum3-10-01351 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.33 | -4.53 | on_sag | yok | düşmedi (-1.1, 0.23, yok) |
| hukum3-10-01352 | donus_dar | h3_acik_48 | None | None | 0.26 | 0.33 | -9.22 | on_sag | yok | düşmedi (-1.2, 0.26, yok) |
| hukum3-10-01354 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.33 | -8.12 | on_sol | yok | düşmedi (-1.4, 0.29, yok) |
| hukum3-10-01355 | donus_dar | h3_acik_48 | None | None | 0.26 | 0.33 | -4.58 | on_sol | yok | düşmedi (-1.3, 0.26, yok) |
| hukum3-10-01357 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.38 | -0.19 | on_sag | yok | düşmedi (-0.0, 0.0, yok) |
| hukum3-10-01358 | donus_dar | h3_acik_48 | None | None | 0.26 | 0.38 | -4.25 | on_sag | yok | düşmedi (-0.9, 0.2, yok) |
| hukum3-10-01360 | donus_dar | h3_acik_48 | None | None | 0.04 | 0.38 | -3.18 | on_sol | yok | düşmedi (-1.3, 0.27, yok) |

(650 koşu daha; hepsi `hukum3.csv`'de `dustu` = True)
