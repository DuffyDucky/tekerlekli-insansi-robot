# Lale fizik modeli: kütle ve ağırlık merkezi karşılaştırması (üretilir: `kod/fizik/model_uret.py`)

Robot çerçevesi: x ileri, y robotun kendi solu, z yukarı; orijin zemin + robot merkezi; ev pozu. AM mm.

| Kaynak | Kütle (g) | AM x | AM y | AM z | Fark kütle (g) | Fark AM (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| **Model** (`lale.xml` gövdeleri toplamı) | 26276.1 | -10.48 | 0.03 | 520.46 | | |
| montaj-analiz.json kutle_g / agirlik_merkezi (kablosuz) + kablo payi 400 g (taban-analiz.json, TAHMIN) | 26276.1 | -10.48 | 0.03 | 520.46 | +0.01 | +0.00 / +0.00 / -0.00 |
| montaj-analiz.json (kablosuz, yalniz CAD parcalari) | 25876.1 | -9.71 | 0.03 | 526.18 | +400.01 | -0.77 / -0.00 / -5.73 |
| taban-analiz.json robot.pozlar[ev] (kablo payli; tarih farkli montajdan) | 26276.1 | -10.50 | 0.00 | 520.50 | +0.04 | +0.02 / +0.03 / -0.04 |

Model toplam atalet tensörü (AM'de, kg·m²): Ixx 6.8724, Iyy 6.9518, Izz 0.6939, Ixy -0.00150, Ixz -0.24337, Iyz -0.00481.
Atalet kaynağı: FreeCAD Solid.MatrixOfInertia (AM'de, birim yogunluk) x Kutle_g / hacim; parca ici yogunluk tekduze varsayimi; grup = paralel eksen toplami. Karşılaştırılacak CAD atalet değeri yok (montaj-analiz.json ataleti yazmıyor).

| Gövde | Montaj grupları | Kütle (g) | AM x / y / z (mm) | Ixx / Iyy / Izz (kg·m²) |
| --- | --- | --- | --- | --- |
| taban | Taban_Govde | 7960.7 | -50.9 / -0.7 / 128.3 | 0.07192 / 0.16147 / 0.20516 |
| govde | Iskelet, Kabuk, OmuzSag_Govde, OmuzSol_Govde, Kafa_Govde | 14381.7 | 6.5 / 0.3 / 583.2 | 3.13602 / 3.16957 / 0.34843 |
| kafa_boyun | Kafa_Boyun | 278.6 | 6.9 / 0.5 / 1423.8 | 0.00071 / 0.00074 / 0.00015 |
| kafa_bas | Kafa_Bas | 1469.3 | 25.0 / 1.0 / 1479.8 | 0.01458 / 0.00892 / 0.01282 |
| sag_omuz_gobek | OmuzSol_Gobek | 177.6 | -2.3 / -174.0 / 1277.6 | 0.00009 / 0.00009 / 0.00007 |
| sag_ust_kol | OmuzSol_Kol, DirsekSol_UstKol | 269.6 | -1.6 / -187.3 / 1164.3 | 0.00131 / 0.00130 / 0.00018 |
| sag_on_kol | DirsekSol_OnKol | 200.9 | -0.2 / -193.0 / 1017.5 | 0.00043 / 0.00038 / 0.00006 |
| sag_el | DirsekSol_El | 89.0 | -0.8 / -182.8 / 906.4 | 0.00008 / 0.00009 / 0.00002 |
| sol_omuz_gobek | OmuzSag_Gobek | 177.6 | -2.3 / 174.0 / 1277.6 | 0.00009 / 0.00009 / 0.00007 |
| sol_ust_kol | OmuzSag_Kol, DirsekSag_UstKol | 269.6 | -1.6 / 187.3 / 1164.3 | 0.00131 / 0.00130 / 0.00018 |
| sol_on_kol | DirsekSag_OnKol | 200.9 | -0.2 / 193.0 / 1017.5 | 0.00043 / 0.00038 / 0.00006 |
| sol_el | DirsekSag_El | 89.0 | -0.8 / 182.8 / 906.4 | 0.00008 / 0.00009 / 0.00002 |
| teker_on_sol | Taban_OnSagTeker | 177.9 | 185.0 / 210.3 / 62.5 | 0.00023 / 0.00035 / 0.00023 |
| teker_arka_sol | Taban_ArkaSagTeker | 177.9 | -185.0 / 210.3 / 62.5 | 0.00023 / 0.00035 / 0.00023 |
| teker_on_sag | Taban_OnSolTeker | 177.9 | 185.0 / -210.3 / 62.5 | 0.00023 / 0.00035 / 0.00023 |
| teker_arka_sag | Taban_ArkaSolTeker | 177.9 | -185.0 / -210.3 / 62.5 | 0.00023 / 0.00035 / 0.00023 |
