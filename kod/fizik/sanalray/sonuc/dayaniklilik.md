# Dayanıklılık tabloları (üretildi: dayaniklilik.py rapor)

## A'dan B'ye (sınama koridorları; her koşul, temiz ve birleşik dahil: orta hedef x 4 koridor x 3 tohum = 12), kafa sabit, dönüş fazlası %25
| koşul | etken | düzey | başarı | varış hatası ort / en (m) | yanal sapma ham en (m) | yanal, ilk 2 m'den sonra ort / en (m) | temas olayı | temas süresi (s) | konum hatası en (m) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz | temiz | - | 12/12 | 0,118 / 0,136 | 0,121 | 0,021 / 0,073 | 0 | 0,0 | 0,122 |
| konum5 | harita konum | ±5 cm | 12/12 | 0,115 / 0,142 | 0,126 | 0,021 / 0,093 | 0 | 0,0 | 0,128 |
| konum20 | harita konum | ±20 cm | 12/12 | 0,114 / 0,170 | 0,194 | 0,034 / 0,194 | 0 | 0,0 | 0,257 |
| aci5 | harita açı | ±5° | 12/12 | 0,119 / 0,141 | 0,121 | 0,022 / 0,072 | 0 | 0,0 | 0,122 |
| odak2 | odak | %2 | 12/12 | 0,129 / 0,177 | 0,121 | 0,022 / 0,115 | 0 | 0,0 | 0,165 |
| egim2 | montaj eğimi | ±2° | 12/12 | 0,121 / 0,146 | 0,106 | 0,021 / 0,074 | 0 | 0,0 | 0,119 |
| gecikme200 | gecikme | 200 ms | 12/12 | 0,076 / 0,107 | 0,130 | 0,021 / 0,130 | 0 | 0,0 | 0,142 |
| dusme50 | kare düşmesi | %50 | 12/12 | 0,136 / 0,159 | 0,124 | 0,021 / 0,061 | 0 | 0,0 | 0,125 |
| ortulme50 | örtülme | %50 zaman | 12/12 | 0,135 / 0,196 | 0,121 | 0,021 / 0,092 | 0 | 0,0 | 0,185 |
| parlama_agir | parlama | %50 zaman, genlik 230 | 12/12 | 0,131 / 0,185 | 0,121 | 0,024 / 0,100 | 0 | 0,0 | 0,154 |
| bulanik_agir | bulanıklık | 33 ms, titreşim 0,6 rad/s | 12/12 | 0,182 / 0,228 | 0,186 | 0,031 / 0,186 | 0 | 0,0 | 0,219 |
| yirtik_hafif | yırtık | etiketlerin 1/3'ü, köşe %15 | 12/12 | 0,145 / 0,258 | 0,121 | 0,019 / 0,070 | 0 | 0,0 | 0,211 |
| yirtik_agir | yırtık | hepsi, köşe %25 | 2/12 | 0,804 / 1,983 | 1,076 | 0,324 / 1,076 | 6 | 242,7 | 1,904 |
| kayip1 | eksik etiket | 1 etiket yok | 12/12 | 0,130 / 0,207 | 0,121 | 0,019 / 0,073 | 0 | 0,0 | 0,182 |
| yanlis1 | yanlış yer | 1 etiket 1 m kaymış | 9/12 | 0,291 / 0,957 | 0,957 | 0,056 / 0,957 | 0 | 0,0 | 1,142 |
| hafif | birleşik | hafif | 12/12 | 0,116 / 0,140 | 0,105 | 0,020 / 0,087 | 0 | 0,0 | 0,119 |
| orta | birleşik | orta | 11/12 | 0,176 / 0,317 | 0,185 | 0,028 / 0,185 | 0 | 0,0 | 0,272 |
| agir | birleşik | ağır | 2/12 | 0,809 / 1,983 | 1,076 | 0,328 / 1,076 | 6 | 242,7 | 1,904 |

## Rastgele bırakılma, birleşik kurulumlar (sınama koridorları, bırakma = tohum - 1; ilk sürüm "tek" ve doğrulamalı başlatma)
| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en (s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agir, tek, kafa sabit | 0/12 | - | - / - | 0 | - / - | 300,4 | 0 | 0 | 0 | 18 | 3140,2 |
| hafif, tek, kafa sabit | 12/12 | 0,100 | 0,049 / 0,202 | 0 | 2,9 / 13,1 | 41,9 | 0 | 0 | 0 | 0 | 0,0 |
| orta, dogrulamali, kafa sabit | 6/12 | 0,176 | 0,072 / 0,154 | 0 | 33,3 / 110,3 | 218,1 | 27 | 5 | 15 | 22 | 804,5 |
| orta, tek, kafa sabit | 5/12 | 0,144 | 0,320 / 1,381 | 2 | 6,0 / 19,4 | 134,5 | 0 | 0 | 0 | 5 | 1219,0 |

## Doğrulamalı başlatma, GELİŞTİRME (koridor_1, koridor_3, bırakma 0-3)
| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en (s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz, dogrulamali, kafa sabit | 8/8 | 0,115 | 0,023 / 0,083 | 0 | 4,0 / 8,4 | 48,5 | 0 | 1 | 0 | 4 | 1,6 |
| temiz, tek, kafa sabit | 7/8 | 0,106 | 0,035 / 0,140 | 0 | 2,7 / 7,4 | 73,0 | 0 | 0 | 0 | 1 | 276,4 |

## Doğrulamalı başlatma, SINAMA (ayrı tohumlar: sınama koridorları, bırakma 10-13)
| koşul | başarı | varış hatası ort (m) | başlatma hatası ort / en (m) | başlatma > 0,5 m | konumlanma ort / en (s) | toplam süre ort (s) | doğrulama reddi | konum bırakma | takılma | temas olayı | temas süresi (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temiz, dogrulamali, kafa sabit | 16/16 | 0,102 | 0,019 / 0,201 | 0 | 5,5 / 14,2 | 35,3 | 0 | 0 | 0 | 0 | 0,0 |
| temiz, tek, kafa sabit | 15/16 | 0,092 | 0,027 / 0,179 | 0 | 4,4 / 13,1 | 48,6 | 0 | 0 | 0 | 2 | 274,9 |

