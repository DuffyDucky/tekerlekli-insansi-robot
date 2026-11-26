# Dayanıklılık tamamlama turu: rotada ölçülen etiketten seçilen eksik / yanlış yer (üretildi: dayaniklilik.py rapor_rota)

Sınama koridorları koridor_2/4/5/6, orta hedef, kafa sabit, dönüş fazlası %25, tohum 1-6 (tohum 1-3 ilk turla aynı başlangıç sapması ve kusur çekilişi). Aday etiketler: aynı koridor / tohumun kusursuz koşusunda süzgecin en az bir ölçümünü kabul ettiği etiketler (deney tasarımı; Beyin bunu görmez, hep nominal planı kullanır). "etkisiz" = koşu temiz koşuyla birebir aynı (varis_hatasi_m, etiket_olcum, etiket_ret, sure_s, en_yanal_sapma_m).

Denetim (sayaç takılı kusursuz koşu, tohum 1-3, ilk turla birebir aynı): 12/12

| koşul | düzey | tohum | başarı | etkisiz | varış ort / en (m) | yanal ham en (m) | yanal ilk 2 m sonrası ort / en (m) | konum hatası en (m) | temas olay / süre (s) | seçilen etiketin temiz koşudaki kabul payı ort |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz | - | 1-3 | 12/12 | - | 0,118 / 0,136 | 0,121 | 0,021 / 0,073 | 0,122 | 0 / 0,0 | - |
| temiz | - | 1-6 | 24/24 | - | 0,118 / 0,136 | 0,121 | 0,021 / 0,075 | 0,133 | 0 / 0,0 | - |
| kayip1_rota | 1 etiket yok (rotada ölçülenlerden, rastgele) | 1-3 | 12/12 | 0 | 0,133 / 0,207 | 0,249 | 0,027 / 0,249 | 0,277 | 0 / 0,0 | 0,41 |
| kayip1_rota | 1 etiket yok (rotada ölçülenlerden, rastgele) | 1-6 | 24/24 | 0 | 0,121 / 0,207 | 0,249 | 0,029 / 0,249 | 0,277 | 0 / 0,0 | 0,40 |
| kayip1_kritik | 1 etiket yok (en çok ölçülen) | 1-3 | 12/12 | 0 | 0,119 / 0,186 | 0,249 | 0,031 / 0,249 | 0,277 | 0 / 0,0 | 0,50 |
| kayip1_kritik | 1 etiket yok (en çok ölçülen) | 1-6 | 24/24 | 0 | 0,124 / 0,204 | 0,249 | 0,031 / 0,249 | 0,277 | 0 / 0,0 | 0,50 |
| yanlis1_rota | 1 etiket 1 m kaymış (rotada ölçülenlerden, rastgele) | 1-3 | 5/12 | 0 | 0,949 / 5,754 | 1,210 | 0,153 / 1,210 | 1,163 | 1 / 101,8 | 0,41 |
| yanlis1_rota | 1 etiket 1 m kaymış (rotada ölçülenlerden, rastgele) | 1-6 | 15/24 | 0 | 0,756 / 5,762 | 1,225 | 0,142 / 1,225 | 1,200 | 2 / 206,0 | 0,40 |
| yanlis1_kritik | 1 etiket 1 m kaymış (en çok ölçülen) | 1-3 | 8/12 | 0 | 0,276 / 0,957 | 0,957 | 0,051 / 0,957 | 1,142 | 0 / 0,0 | 0,49 |
| yanlis1_kritik | 1 etiket 1 m kaymış (en çok ölçülen) | 1-6 | 15/24 | 0 | 0,332 / 1,040 | 0,957 | 0,051 / 0,957 | 1,142 | 0 / 0,0 | 0,49 |
| yanlis05_rota | 1 etiket 0,5 m kaymış (rotada ölçülenlerden, rastgele) | 1-3 | 9/12 | 0 | 0,233 / 0,460 | 0,622 | 0,069 / 0,622 | 0,840 | 0 / 0,0 | 0,41 |
| yanlis05_rota | 1 etiket 0,5 m kaymış (rotada ölçülenlerden, rastgele) | 1-6 | 20/24 | 0 | 0,235 / 1,652 | 0,622 | 0,079 / 0,622 | 6,405 | 0 / 0,0 | 0,40 |
| yanlis025_rota | 1 etiket 0,25 m kaymış (rotada ölçülenlerden, rastgele) | 1-3 | 12/12 | 0 | 0,099 / 0,229 | 0,249 | 0,037 / 0,249 | 0,304 | 0 / 0,0 | 0,41 |
| yanlis025_rota | 1 etiket 0,25 m kaymış (rotada ölçülenlerden, rastgele) | 1-6 | 24/24 | 0 | 0,095 / 0,229 | 0,249 | 0,035 / 0,249 | 0,304 | 0 / 0,0 | 0,40 |

## Başarısız koşular

- ab_yanlis05_rota_koridor_5_k5_kapi_6_sabit_t1: beyin bitti dedi, hedefe 0.46 m; seçilen [203] (temiz koşuda 67 / 199 kabul)
- ab_yanlis05_rota_koridor_5_k5_kapi_6_sabit_t2: beyin bitti dedi, hedefe 0.46 m; seçilen [203] (temiz koşuda 60 / 166 kabul)
- ab_yanlis05_rota_koridor_5_k5_kapi_6_sabit_t4: beyin bitti dedi, hedefe 1.65 m; seçilen [202] (temiz koşuda 62 / 198 kabul)
- ab_yanlis05_rota_koridor_6_k6_kapi_6_sabit_t2: beyin bitti dedi, hedefe 0.46 m; seçilen [253] (temiz koşuda 58 / 184 kabul)
- ab_yanlis1_kritik_koridor_4_k4_kapi_9_sabit_t1: beyin bitti dedi, hedefe 0.74 m; seçilen [157] (temiz koşuda 267 / 529 kabul)
- ab_yanlis1_kritik_koridor_4_k4_kapi_9_sabit_t2: beyin bitti dedi, hedefe 0.61 m; seçilen [157] (temiz koşuda 268 / 517 kabul)
- ab_yanlis1_kritik_koridor_4_k4_kapi_9_sabit_t3: beyin bitti dedi, hedefe 0.50 m; seçilen [157] (temiz koşuda 273 / 530 kabul)
- ab_yanlis1_kritik_koridor_4_k4_kapi_9_sabit_t4: beyin bitti dedi, hedefe 0.69 m; seçilen [157] (temiz koşuda 270 / 524 kabul)
- ab_yanlis1_kritik_koridor_4_k4_kapi_9_sabit_t5: beyin bitti dedi, hedefe 0.70 m; seçilen [157] (temiz koşuda 270 / 523 kabul)
- ab_yanlis1_kritik_koridor_4_k4_kapi_9_sabit_t6: beyin bitti dedi, hedefe 0.70 m; seçilen [157] (temiz koşuda 253 / 502 kabul)
- ab_yanlis1_kritik_koridor_5_k5_kapi_6_sabit_t1: beyin bitti dedi, hedefe 0.96 m; seçilen [203] (temiz koşuda 67 / 199 kabul)
- ab_yanlis1_kritik_koridor_5_k5_kapi_6_sabit_t4: beyin bitti dedi, hedefe 1.04 m; seçilen [203] (temiz koşuda 64 / 198 kabul)
- ab_yanlis1_kritik_koridor_5_k5_kapi_6_sabit_t6: beyin bitti dedi, hedefe 1.04 m; seçilen [203] (temiz koşuda 61 / 177 kabul)
- ab_yanlis1_rota_koridor_4_k4_kapi_9_sabit_t1: beyin bitti dedi, hedefe 0.74 m; seçilen [157] (temiz koşuda 267 / 529 kabul)
- ab_yanlis1_rota_koridor_4_k4_kapi_9_sabit_t2: sure doldu (hedefe 5.75 m); temas 1; seçilen [152] (temiz koşuda 66 / 517 kabul)
- ab_yanlis1_rota_koridor_4_k4_kapi_9_sabit_t3: beyin bitti dedi, hedefe 0.50 m; seçilen [157] (temiz koşuda 273 / 530 kabul)
- ab_yanlis1_rota_koridor_4_k4_kapi_9_sabit_t4: sure doldu (hedefe 5.76 m); temas 1; seçilen [152] (temiz koşuda 74 / 524 kabul)
- ab_yanlis1_rota_koridor_4_k4_kapi_9_sabit_t6: beyin bitti dedi, hedefe 0.30 m; seçilen [152] (temiz koşuda 68 / 502 kabul)
- ab_yanlis1_rota_koridor_5_k5_kapi_6_sabit_t1: beyin bitti dedi, hedefe 0.96 m; seçilen [203] (temiz koşuda 67 / 199 kabul)
- ab_yanlis1_rota_koridor_5_k5_kapi_6_sabit_t2: beyin bitti dedi, hedefe 0.96 m; seçilen [203] (temiz koşuda 60 / 166 kabul)
- ab_yanlis1_rota_koridor_6_k6_kapi_6_sabit_t1: beyin bitti dedi, hedefe 1.04 m; seçilen [253] (temiz koşuda 56 / 183 kabul)
- ab_yanlis1_rota_koridor_6_k6_kapi_6_sabit_t2: beyin bitti dedi, hedefe 0.96 m; seçilen [253] (temiz koşuda 58 / 184 kabul)

## İlk turun tek etiketlik koşulları: etkili / etkisiz (yeniden sayım, ilk turun ham kayıtları)

| koşul | başarı (12) | etkisiz | etkili koşularda başarı |
| --- | --- | --- | --- |
| kayip1 | 12/12 | 6 | 6/6 |
| yanlis1 | 9/12 | 6 | 3/6 |
| yirtik_hafif | 12/12 | 3 | 9/9 |
