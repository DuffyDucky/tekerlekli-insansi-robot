# Taşınma deneyi: tablolar (rapor.py üretir)

## Sınama kümesi (hüküm): tohum 1, 2 x 6 koridor

Taşıma (koşul başına n koşu). tepki = beynin davranış değiştirdiği ilk an (algi: "kayboldum"; v3 cok: yeniden plan / keşfe dönüş; v3 ab: tepki düzeneği yok); şüphe = konumlayıcının ilk `konum_kararsiz`'ı; bulma = taşımadan sonra poz hatası < 0,5 m ve yön < 30° olup sonuna dek öyle kalan dilimin başı. Süreler taşımadan sonra s (medyan / en çok).

| senaryo | tür | sürüm | başarı | tepki (med / maks s) | şüphe | bulma (med / maks s) | yanlış poza emin s (med / maks) | yanlış poza göre sürüş s (med / maks) | temas (koşu) | yanlış yerde "vardım" | yanlış koridora kesin sürüş: koşu (toplam s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ab | aynı koridor, uzak | v3 | 5/12 | 0/12 (None / None) | 12/12 (0.5) | 7/12 (6.7 / 84.2) | 3.9 / 71.3 | 5.2 / 83.3 | 0 (0) | 6 | 0 (0.0) |
| ab | aynı koridor, uzak | algi | 12/12 | 12/12 (0.8 / 0.8) | 12/12 (0.5) | 12/12 (5.5 / 63.6) | 0.6 / 26.8 | 0.8 / 27.2 | 0 (0) | 0 | 0 (0.0) |
| ab | 180° çevrilmiş | v3 | 8/12 | 0/12 (None / None) | 12/12 (2.8) | 8/12 (6.0 / 24.8) | 4.8 / 23.7 | 6.0 / 24.8 | 0 (0) | 4 | 0 (0.0) |
| ab | 180° çevrilmiş | algi | 12/12 | 11/12 (1.1 / 15.2) | 12/12 (1.5) | 12/12 (13.3 / 34.2) | 1.5 / 15.2 | 1.5 / 15.2 | 0 (0) | 0 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | v3 | 8/12 | 0/12 (None / None) | 12/12 (2.2) | 8/12 (11.1 / 48.0) | 7.0 / 44.2 | 7.2 / 47.7 | 0 (0) | 4 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | algi | 12/12 | 12/12 (1.4 / 13.2) | 12/12 (1.2) | 12/12 (10.1 / 37.6) | 1.2 / 12.7 | 1.4 / 13.1 | 0 (0) | 0 | 0 (0.0) |
| ab | başka koridor | v3 | 0/12 (güvenli durdu) | 0/12 (None / None) | 12/12 (0.5) | 0/12 (None / None) | 7.8 / 118.7 | 9.9 / 120.0 | 0 (0) | 6 | 12 (240.0) |
| ab | başka koridor | algi | 11/12 (güvenli durdu) | 12/12 (0.8 / 0.8) | 12/12 (0.5) | 0/12 (None / None) | 98.7 / 105.3 | 6.6 / 41.2 | 0 (0) | 1 | 12 (156.5) |
| cok | aynı koridor, uzak | v3 | 8/12 | 12/12 (0.7 / 4.6) | 12/12 (0.4) | 8/12 (8.9 / 48.0) | 7.0 / 45.3 | 8.8 / 47.6 | 0 (0) | 3 | 1 (12.0) |
| cok | aynı koridor, uzak | algi | 11/12 | 12/12 (0.8 / 0.8) | 12/12 (0.5) | 11/12 (6.9 / 121.3) | 0.4 / 0.8 | 0.7 / 0.8 | 0 (0) | 0 | 0 (0.0) |
| cok | 180° çevrilmiş | v3 | 10/12 | 11/12 (1.8 / 12.8) | 12/12 (1.4) | 9/12 (5.8 / 54.1) | 14.2 / 58.0 | 15.2 / 59.4 | 0 (0) | 2 | 2 (62.0) |
| cok | 180° çevrilmiş | algi | 10/12 | 12/12 (1.1 / 13.4) | 12/12 (0.9) | 12/12 (15.6 / 138.8) | 0.9 / 13.0 | 1.1 / 13.4 | 0 (0) | 0 | 0 (0.0) |
| cok | küçük kaydırma (1-3 m) | v3 | 11/12 | 12/12 (0.8 / 13.1) | 12/12 (0.6) | 12/12 (3.4 / 121.5) | 2.5 / 116.5 | 3.2 / 121.0 | 0 (0) | 0 | 0 (0.0) |
| cok | küçük kaydırma (1-3 m) | algi | 12/12 | 12/12 (0.8 / 13.4) | 12/12 (0.8) | 12/12 (7.4 / 56.6) | 0.8 / 12.7 | 0.8 / 13.4 | 0 (0) | 0 | 0 (0.0) |
| cok | başka koridor | v3 | 10/12 | 11/12 (0.5 / 1.0) | 11/12 (0.3) | 9/12 (8.9 / 70.9) | 6.0 / 123.1 | 8.8 / 70.3 | 0 (0) | 1 | 12 (155.0) |
| cok | başka koridor | algi | 11/12 | 12/12 (0.8 / 0.8) | 12/12 (0.4) | 11/12 (5.8 / 49.6) | 0.4 / 0.8 | 0.7 / 0.8 | 0 (0) | 0 | 12 (7.5) |

Yanlış alarm (taşıma yok). kayboldum = algi'nin boşuna "kayboldum" demesi; tepki (v3 cok) = boşuna yeniden plan / keşfe dönüş; süre farkı = algi - v3 (ikisi de vardıysa, eşli, s).

| senaryo | koşul | sürüm | başarı | kayboldum koşu (toplam) | tepki koşu | şüphe koşu | temas | yanlış koridora kesin sürüş: koşu (s) | süre farkı med / maks s |
|---|---|---|---|---|---|---|---|---|---|
| ab | taban | v3 | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| ab | taban | algi | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| ab | insan_2 | v3 | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| ab | insan_2 | algi | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| ab | esya_2 | v3 | 12/12 | 0 (0) | 0 | 1 | 0 | 0 (0.0) | - / - |
| ab | esya_2 | algi | 12/12 | 1 (2) | 1 | 1 | 0 | 0 (0.0) | 0.0 / 11.5 |
| ab | karma_2 | v3 | 11/12 | 0 (0) | 0 | 1 | 0 | 0 (0.0) | - / - |
| ab | karma_2 | algi | 12/12 | 1 (2) | 1 | 1 | 0 | 0 (0.0) | 0.0 / 0.0 |
| ab | karma_3 | v3 | 10/12 | 0 (0) | 0 | 2 | 0 | 0 (0.0) | - / - |
| ab | karma_3 | algi | 11/12 | 5 (10) | 5 | 5 | 0 | 0 (0.0) | 0.0 / 16.8 |
| cok | taban | v3 | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| cok | taban | algi | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| cok | insan_2 | v3 | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| cok | insan_2 | algi | 12/12 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| cok | esya_2 | v3 | 12/12 | 0 (0) | 4 | 4 | 0 | 3 (7.5) | - / - |
| cok | esya_2 | algi | 10/12 | 4 (11) | 4 | 4 | 0 | 2 (21.5) | 0.0 / 166.7 |
| cok | karma_2 | v3 | 10/12 | 0 (0) | 3 | 3 | 0 | 3 (34.5) | - / - |
| cok | karma_2 | algi | 12/12 | 3 (7) | 3 | 3 | 0 | 2 (6.5) | 0.0 / 9.4 |
| cok | karma_3 | v3 | 8/12 | 0 (0) | 8 | 8 | 0 | 6 (78.5) | - / - |
| cok | karma_3 | algi | 7/12 | 8 (24) | 8 | 8 | 0 | 5 (30.0) | 0.0 / 8.3 |

## Geliştirme kümesi (eşik ayarı): tohum 901-903 x koridor_2, 3, 5

Taşıma (koşul başına n koşu). tepki = beynin davranış değiştirdiği ilk an (algi: "kayboldum"; v3 cok: yeniden plan / keşfe dönüş; v3 ab: tepki düzeneği yok); şüphe = konumlayıcının ilk `konum_kararsiz`'ı; bulma = taşımadan sonra poz hatası < 0,5 m ve yön < 30° olup sonuna dek öyle kalan dilimin başı. Süreler taşımadan sonra s (medyan / en çok).

| senaryo | tür | sürüm | başarı | tepki (med / maks s) | şüphe | bulma (med / maks s) | yanlış poza emin s (med / maks) | yanlış poza göre sürüş s (med / maks) | temas (koşu) | yanlış yerde "vardım" | yanlış koridora kesin sürüş: koşu (toplam s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ab | aynı koridor, uzak | algi | 9/9 | 9/9 (0.8 / 0.8) | 9/9 (0.5) | 9/9 (5.8 / 13.2) | 0.4 / 0.8 | 0.8 / 0.8 | 0 (0) | 0 | 0 (0.0) |
| ab | 180° çevrilmiş | algi | 9/9 | 9/9 (2.6 / 12.6) | 9/9 (2.2) | 9/9 (7.8 / 46.9) | 2.2 / 12.5 | 2.6 / 12.5 | 0 (0) | 0 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | algi | 9/9 | 9/9 (0.8 / 5.8) | 9/9 (0.8) | 9/9 (6.0 / 32.4) | 0.8 / 5.4 | 0.8 / 5.8 | 0 (0) | 0 | 0 (0.0) |
| ab | başka koridor | algi | 9/9 (güvenli durdu) | 9/9 (0.8 / 0.8) | 9/9 (0.5) | 0/9 (None / None) | 104.4 / 107.5 | 3.4 / 60.1 | 0 (0) | 0 | 9 (110.5) |
| cok | aynı koridor, uzak | algi | 9/9 | 9/9 (0.8 / 0.8) | 9/9 (0.7) | 9/9 (5.7 / 55.7) | 0.6 / 0.8 | 0.8 / 0.8 | 0 (0) | 0 | 0 (0.0) |
| cok | 180° çevrilmiş | algi | 8/9 | 7/9 (1.9 / 7.0) | 9/9 (1.4) | 9/9 (8.8 / 148.1) | 1.4 / 7.0 | 1.8 / 7.0 | 0 (0) | 0 | 0 (0.0) |
| cok | küçük kaydırma (1-3 m) | algi | 9/9 | 9/9 (0.8 / 0.8) | 9/9 (0.8) | 9/9 (5.6 / 53.0) | 0.8 / 0.8 | 0.8 / 0.8 | 0 (0) | 0 | 0 (0.0) |
| cok | başka koridor | algi | 9/9 | 9/9 (0.8 / 0.8) | 9/9 (0.7) | 9/9 (6.8 / 61.8) | 0.6 / 0.8 | 0.7 / 0.8 | 0 (0) | 0 | 9 (7.5) |

Yanlış alarm (taşıma yok). kayboldum = algi'nin boşuna "kayboldum" demesi; tepki (v3 cok) = boşuna yeniden plan / keşfe dönüş; süre farkı = algi - v3 (ikisi de vardıysa, eşli, s).

| senaryo | koşul | sürüm | başarı | kayboldum koşu (toplam) | tepki koşu | şüphe koşu | temas | yanlış koridora kesin sürüş: koşu (s) | süre farkı med / maks s |
|---|---|---|---|---|---|---|---|---|---|
| ab | taban | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| ab | insan_2 | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| ab | esya_2 | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| ab | karma_2 | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| cok | taban | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| cok | insan_2 | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| cok | esya_2 | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |
| cok | karma_2 | algi | 9/9 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | None / None |

## Sınama, yalnız geliştirmede hiç kullanılmamış haritalar (koridor_1, 4, 6; 6 koşu / koşul)

Taşıma (koşul başına n koşu). tepki = beynin davranış değiştirdiği ilk an (algi: "kayboldum"; v3 cok: yeniden plan / keşfe dönüş; v3 ab: tepki düzeneği yok); şüphe = konumlayıcının ilk `konum_kararsiz`'ı; bulma = taşımadan sonra poz hatası < 0,5 m ve yön < 30° olup sonuna dek öyle kalan dilimin başı. Süreler taşımadan sonra s (medyan / en çok).

| senaryo | tür | sürüm | başarı | tepki (med / maks s) | şüphe | bulma (med / maks s) | yanlış poza emin s (med / maks) | yanlış poza göre sürüş s (med / maks) | temas (koşu) | yanlış yerde "vardım" | yanlış koridora kesin sürüş: koşu (toplam s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ab | aynı koridor, uzak | v3 | 4/6 | 0/6 (None / None) | 6/6 (0.4) | 5/6 (6.7 / 84.2) | 3.9 / 71.3 | 5.2 / 83.3 | 0 (0) | 1 | 0 (0.0) |
| ab | aynı koridor, uzak | algi | 6/6 | 6/6 (0.8 / 0.8) | 6/6 (0.4) | 6/6 (5.1 / 63.6) | 0.6 / 26.8 | 0.7 / 27.2 | 0 (0) | 0 | 0 (0.0) |
| ab | 180° çevrilmiş | v3 | 4/6 | 0/6 (None / None) | 6/6 (4.6) | 4/6 (8.8 / 24.8) | 7.5 / 23.7 | 8.7 / 24.8 | 0 (0) | 2 | 0 (0.0) |
| ab | 180° çevrilmiş | algi | 6/6 | 6/6 (4.0 / 9.6) | 6/6 (3.6) | 6/6 (14.4 / 16.9) | 3.6 / 9.1 | 4.0 / 9.5 | 0 (0) | 0 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | v3 | 6/6 | 0/6 (None / None) | 6/6 (1.8) | 6/6 (11.1 / 48.0) | 10.6 / 43.1 | 11.1 / 47.7 | 0 (0) | 0 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | algi | 6/6 | 6/6 (2.2 / 7.5) | 6/6 (1.8) | 6/6 (11.6 / 37.6) | 1.8 / 7.0 | 2.2 / 7.4 | 0 (0) | 0 | 0 (0.0) |
| ab | başka koridor | v3 | 0/6 (güvenli durdu) | 0/6 (None / None) | 6/6 (0.6) | 0/6 (None / None) | 62.3 / 118.7 | 9.1 / 45.8 | 0 (0) | 3 | 6 (75.5) |
| ab | başka koridor | algi | 6/6 (güvenli durdu) | 6/6 (0.8 / 0.8) | 6/6 (0.6) | 0/6 (None / None) | 95.3 / 103.7 | 4.3 / 41.1 | 0 (0) | 0 | 6 (63.5) |
| cok | aynı koridor, uzak | v3 | 5/6 | 6/6 (0.7 / 4.6) | 6/6 (0.5) | 5/6 (10.7 / 48.0) | 14.6 / 45.3 | 15.8 / 47.6 | 0 (0) | 1 | 1 (12.0) |
| cok | aynı koridor, uzak | algi | 6/6 | 6/6 (0.8 / 0.8) | 6/6 (0.5) | 6/6 (11.2 / 40.5) | 0.5 / 0.8 | 0.8 / 0.8 | 0 (0) | 0 | 0 (0.0) |
| cok | 180° çevrilmiş | v3 | 5/6 | 6/6 (1.5 / 12.8) | 6/6 (1.4) | 5/6 (17.7 / 54.1) | 24.0 / 58.0 | 25.4 / 58.1 | 0 (0) | 1 | 0 (0.0) |
| cok | 180° çevrilmiş | algi | 4/6 | 6/6 (1.4 / 13.4) | 6/6 (1.2) | 6/6 (18.5 / 138.8) | 1.2 / 13.0 | 1.4 / 13.4 | 0 (0) | 0 | 0 (0.0) |
| cok | küçük kaydırma (1-3 m) | v3 | 6/6 | 6/6 (1.5 / 2.5) | 6/6 (0.7) | 6/6 (7.6 / 58.5) | 6.6 / 52.7 | 7.5 / 58.2 | 0 (0) | 0 | 0 (0.0) |
| cok | küçük kaydırma (1-3 m) | algi | 6/6 | 6/6 (0.8 / 2.6) | 6/6 (0.8) | 6/6 (11.9 / 56.6) | 0.8 / 2.2 | 0.8 / 2.6 | 0 (0) | 0 | 0 (0.0) |
| cok | başka koridor | v3 | 4/6 | 5/6 (0.5 / 1.0) | 5/6 (0.3) | 3/6 (13.4 / 54.9) | 41.0 / 123.1 | 23.9 / 63.6 | 0 (0) | 1 | 6 (81.0) |
| cok | başka koridor | algi | 6/6 | 6/6 (0.6 / 0.8) | 6/6 (0.4) | 6/6 (5.7 / 10.5) | 0.4 / 0.8 | 0.6 / 0.8 | 0 (0) | 0 | 6 (4.0) |

Yanlış alarm (taşıma yok). kayboldum = algi'nin boşuna "kayboldum" demesi; tepki (v3 cok) = boşuna yeniden plan / keşfe dönüş; süre farkı = algi - v3 (ikisi de vardıysa, eşli, s).

| senaryo | koşul | sürüm | başarı | kayboldum koşu (toplam) | tepki koşu | şüphe koşu | temas | yanlış koridora kesin sürüş: koşu (s) | süre farkı med / maks s |
|---|---|---|---|---|---|---|---|---|---|
| ab | taban | v3 | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| ab | taban | algi | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| ab | insan_2 | v3 | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| ab | insan_2 | algi | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| ab | esya_2 | v3 | 6/6 | 0 (0) | 0 | 1 | 0 | 0 (0.0) | - / - |
| ab | esya_2 | algi | 6/6 | 1 (2) | 1 | 1 | 0 | 0 (0.0) | 0.0 / 11.5 |
| ab | karma_2 | v3 | 5/6 | 0 (0) | 0 | 1 | 0 | 0 (0.0) | - / - |
| ab | karma_2 | algi | 6/6 | 1 (2) | 1 | 1 | 0 | 0 (0.0) | 0.0 / 0.0 |
| ab | karma_3 | v3 | 4/6 | 0 (0) | 0 | 2 | 0 | 0 (0.0) | - / - |
| ab | karma_3 | algi | 5/6 | 4 (7) | 4 | 4 | 0 | 0 (0.0) | 4.1 / 16.8 |
| cok | taban | v3 | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| cok | taban | algi | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| cok | insan_2 | v3 | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| cok | insan_2 | algi | 6/6 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |
| cok | esya_2 | v3 | 6/6 | 0 (0) | 1 | 1 | 0 | 0 (0.0) | - / - |
| cok | esya_2 | algi | 6/6 | 1 (2) | 1 | 1 | 0 | 0 (0.0) | 0.0 / 166.7 |
| cok | karma_2 | v3 | 5/6 | 0 (0) | 1 | 1 | 0 | 1 (17.5) | - / - |
| cok | karma_2 | algi | 6/6 | 1 (3) | 1 | 1 | 0 | 0 (0.0) | 0.0 / 0.0 |
| cok | karma_3 | v3 | 4/6 | 0 (0) | 4 | 4 | 0 | 3 (36.0) | - / - |
| cok | karma_3 | algi | 3/6 | 4 (13) | 4 | 4 | 0 | 2 (15.0) | 0.0 / 5.3 |

## MuJoCo doğrulaması (A'dan B'ye, taban dünya)

Taşıma (koşul başına n koşu). tepki = beynin davranış değiştirdiği ilk an (algi: "kayboldum"; v3 cok: yeniden plan / keşfe dönüş; v3 ab: tepki düzeneği yok); şüphe = konumlayıcının ilk `konum_kararsiz`'ı; bulma = taşımadan sonra poz hatası < 0,5 m ve yön < 30° olup sonuna dek öyle kalan dilimin başı. Süreler taşımadan sonra s (medyan / en çok).

| senaryo | tür | sürüm | başarı | tepki (med / maks s) | şüphe | bulma (med / maks s) | yanlış poza emin s (med / maks) | yanlış poza göre sürüş s (med / maks) | temas (koşu) | yanlış yerde "vardım" | yanlış koridora kesin sürüş: koşu (toplam s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ab | aynı koridor, uzak | v3 | 3/5 | 0/5 (None / None) | 5/5 (0.5) | 3/5 (25.1 / 48.3) | 6.6 / 46.8 | 8.4 / 48.2 | 0 (0) | 2 | 0 (0.0) |
| ab | aynı koridor, uzak | algi | 5/5 | 5/5 (0.8 / 0.8) | 5/5 (0.7) | 5/5 (6.5 / 75.5) | 0.7 / 28.9 | 0.8 / 29.0 | 0 (0) | 0 | 0 (0.0) |
| ab | 180° çevrilmiş | v3 | 4/5 | 0/5 (None / None) | 5/5 (3.1) | 4/5 (15.8 / 43.0) | 20.1 / 41.0 | 20.4 / 42.8 | 0 (0) | 1 | 0 (0.0) |
| ab | 180° çevrilmiş | algi | 5/5 | 4/5 (6.5 / 20.5) | 5/5 (3.1) | 5/5 (17.9 / 26.6) | 3.0 / 20.1 | 3.4 / 20.5 | 0 (0) | 0 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | v3 | 1/5 | 0/5 (None / None) | 5/5 (2.7) | 1/5 (11.7 / 11.7) | 9.7 / 33.9 | 9.0 / 35.4 | 0 (0) | 4 | 0 (0.0) |
| ab | küçük kaydırma (1-3 m) | algi | 5/5 | 5/5 (3.4 / 11.7) | 5/5 (2.7) | 5/5 (13.0 / 26.1) | 2.6 / 11.7 | 3.3 / 11.7 | 0 (0) | 0 | 0 (0.0) |

Yanlış alarm (taşıma yok). kayboldum = algi'nin boşuna "kayboldum" demesi; tepki (v3 cok) = boşuna yeniden plan / keşfe dönüş; süre farkı = algi - v3 (ikisi de vardıysa, eşli, s).

| senaryo | koşul | sürüm | başarı | kayboldum koşu (toplam) | tepki koşu | şüphe koşu | temas | yanlış koridora kesin sürüş: koşu (s) | süre farkı med / maks s |
|---|---|---|---|---|---|---|---|---|---|
| ab | taban | v3 | 5/5 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | - / - |
| ab | taban | algi | 5/5 | 0 (0) | 0 | 0 | 0 | 0 (0.0) | 0.0 / 0.0 |

MuJoCo ile 2B aynı görev (aynı tohum, koridor, taşıma tohumu): 35 / 40 aynı sonuç.

| görev | MuJoCo | 2B |
|---|---|---|
| mj_ab_algi_ayni_uzak_koridor_1_2 | True | True |
| mj_ab_algi_ayni_uzak_koridor_3_1 | True | True |
| mj_ab_algi_ayni_uzak_koridor_4_2 | True | True |
| mj_ab_algi_ayni_uzak_koridor_5_1 | True | True |
| mj_ab_algi_ayni_uzak_koridor_6_2 | True | True |
| mj_ab_algi_kucuk_koridor_1_2 | True | True |
| mj_ab_algi_kucuk_koridor_3_1 | True | True |
| mj_ab_algi_kucuk_koridor_4_2 | True | True |
| mj_ab_algi_kucuk_koridor_5_1 | True | True |
| mj_ab_algi_kucuk_koridor_6_2 | True | True |
| mj_ab_algi_ters180_koridor_1_2 | True | True |
| mj_ab_algi_ters180_koridor_3_1 | True | True |
| mj_ab_algi_ters180_koridor_4_2 | True | True |
| mj_ab_algi_ters180_koridor_5_1 | True | True |
| mj_ab_algi_ters180_koridor_6_2 | True | True |
| mj_ab_algi_ya_taban_koridor_1_2 | True | True |
| mj_ab_algi_ya_taban_koridor_3_1 | True | True |
| mj_ab_algi_ya_taban_koridor_4_2 | True | True |
| mj_ab_algi_ya_taban_koridor_5_1 | True | True |
| mj_ab_algi_ya_taban_koridor_6_2 | True | True |
| mj_ab_v3_ayni_uzak_koridor_1_2 | True | True |
| mj_ab_v3_ayni_uzak_koridor_3_1 | False | False |
| mj_ab_v3_ayni_uzak_koridor_4_2 | True | True |
| mj_ab_v3_ayni_uzak_koridor_5_1 | False | False |
| mj_ab_v3_ayni_uzak_koridor_6_2 | True | True |
| mj_ab_v3_kucuk_koridor_1_2 | False | True |
| mj_ab_v3_kucuk_koridor_3_1 | False | True |
| mj_ab_v3_kucuk_koridor_4_2 | False | True |
| mj_ab_v3_kucuk_koridor_5_1 | False | False |
| mj_ab_v3_kucuk_koridor_6_2 | True | True |
| mj_ab_v3_ters180_koridor_1_2 | False | True |
| mj_ab_v3_ters180_koridor_3_1 | True | False |
| mj_ab_v3_ters180_koridor_4_2 | True | True |
| mj_ab_v3_ters180_koridor_5_1 | True | True |
| mj_ab_v3_ters180_koridor_6_2 | True | True |
| mj_ab_v3_ya_taban_koridor_1_2 | True | True |
| mj_ab_v3_ya_taban_koridor_3_1 | True | True |
| mj_ab_v3_ya_taban_koridor_4_2 | True | True |
| mj_ab_v3_ya_taban_koridor_5_1 | True | True |
| mj_ab_v3_ya_taban_koridor_6_2 | True | True |

