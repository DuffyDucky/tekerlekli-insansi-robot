# Dönüş varyantları (Y0f, `kod/fizik/olcum_varyantlar.py`)

V0 bugünkü robot; öbürleri **VARSAYIM** (`kod/fizik/varyantlar.py`, modelleme yöntemi orada). Başsız, protokol üzerinden; 3 s sonra 1,5 s ortalaması. w komutu varyantın tavanı (V1: 3, öbürleri 1). Tork oranı: yerinde dönüşte en yüklü tekerin ortalama torku / sürekli tork (durmanın %30'u, TAHMİN); > 1 ısınma, ≈ 3,3 durma.

- **V0**: firmware 0.5.0 + dört lastik teker (varsayılan)
- **V1**: w girişi 3'e dek; yerinde dönüşte PWM ±1 (açık çevrim)
- **V2**: enkoderden teker hızı PI (kp 2, ki 10; TAHMİN), PWM doyuma dek
- **V3**: ön iki teker yanal serbest, tahrikli
- **V4**: ön iki teker serbest (bilyalı sarhoş), yalnız arka iki teker tahrikli
- **V1+V3**: V1 ve V3 birlikte
- **V2+V3**: V2 ve V3 birlikte

| varyant | durma | µ | yerinde w rad/s | 90° s | tork / sürekli | yay (v 0,25) v / w | yarıçap m | kolon dolaşma |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V0 | 21kgcm | 0,5 | 0,001 | - | 2,0 | 0,199 / 0,001 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V0 | 21kgcm | 0,8 | 0,001 | - | 2,0 | 0,199 / 0,001 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V0 | 9kgcm | 0,5 | 0,001 | - | 2,0 | 0,155 / 0,000 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V0 | 9kgcm | 0,8 | 0,001 | - | 2,0 | 0,155 / 0,000 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V1 | 21kgcm | 0,5 | 0,118 | 13,3 | 2,3 | 0,105 / 0,065 | 1,61 | başarılı, 34,6 s |
| V1 | 21kgcm | 0,8 | 0,126 | 12,5 | 2,3 | 0,088 / 0,002 | - | başarılı, 43,8 s |
| V1 | 9kgcm | 0,5 | 0,001 | - | 3,6 | 0,045 / 0,001 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V1 | 9kgcm | 0,8 | 0,001 | - | 3,6 | 0,045 / 0,001 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V2 | 21kgcm | 0,5 | 0,088 | 17,9 | 2,1 | 0,105 / 0,054 | 1,95 | başarılı, 44,1 s |
| V2 | 21kgcm | 0,8 | 0,086 | 18,2 | 2,3 | 0,032 / 0,002 | - | başarılı, 53,3 s |
| V2 | 9kgcm | 0,5 | 0,001 | - | 3,6 | 0,032 / 0,001 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V2 | 9kgcm | 0,8 | 0,001 | - | 3,6 | 0,032 / 0,001 | - | başarısız (0 / 3 ara nokta, 60 s) |
| V3 | 21kgcm | 0,5 | 0,793 | 2,0 | 0,6 | 0,209 / 0,728 | 0,29 | başarılı, 11,5 s |
| V3 | 21kgcm | 0,8 | 0,711 | 2,2 | 0,8 | 0,208 / 0,649 | 0,32 | başarılı, 11,8 s |
| V3 | 9kgcm | 0,5 | 0,431 | 3,6 | 1,3 | 0,167 / 0,546 | 0,31 | başarılı, 15,3 s |
| V3 | 9kgcm | 0,8 | 0,253 | 6,2 | 1,6 | 0,163 / 0,388 | 0,42 | başarılı, 18,1 s |
| V4 | 21kgcm | 0,5 | 0,519 | 3,0 | 1,0 | 0,186 / 0,549 | 0,34 | başarılı, 13,6 s |
| V4 | 21kgcm | 0,8 | 0,382 | 4,1 | 1,2 | 0,182 / 0,399 | 0,45 | başarılı, 14,8 s |
| V4 | 9kgcm | 0,5 | 0,010 | - | 2,0 | 0,108 / 0,271 | 0,40 | başarısız (0 / 3 ara nokta, 60 s) |
| V4 | 9kgcm | 0,8 | 0,010 | - | 2,0 | 0,102 / 0,021 | 4,96 | başarısız (0 / 3 ara nokta, 60 s) |
| V1+V3 | 21kgcm | 0,5 | 1,664 | 0,9 | 1,0 | 0,141 / 1,086 | 0,13 | başarılı, 10,8 s |
| V1+V3 | 21kgcm | 0,8 | 1,579 | 1,0 | 1,1 | 0,138 / 1,012 | 0,14 | başarılı, 10,8 s |
| V1+V3 | 9kgcm | 0,5 | 1,278 | 1,2 | 1,8 | 0,134 / 0,736 | 0,18 | başarılı, 13,1 s |
| V1+V3 | 9kgcm | 0,8 | 1,112 | 1,4 | 2,0 | 0,119 / 0,620 | 0,19 | başarılı, 13,6 s |
| V2+V3 | 21kgcm | 0,5 | 0,982 | 1,6 | 0,7 | 0,199 / 0,777 | 0,26 | başarılı, 10,5 s |
| V2+V3 | 21kgcm | 0,8 | 0,975 | 1,6 | 0,8 | 0,191 / 0,737 | 0,26 | başarılı, 10,6 s |
| V2+V3 | 9kgcm | 0,5 | 0,983 | 1,6 | 1,5 | 0,159 / 0,592 | 0,27 | başarılı, 11,1 s |
| V2+V3 | 9kgcm | 0,8 | 0,974 | 1,6 | 1,8 | 0,141 / 0,504 | 0,28 | başarılı, 11,1 s |

## Yan etkiler (µ 0,8, 21 kg·cm)

Model sol-sağ simetrik: düz gidiş, dur ve acil stopta yön sapması bozucu olmadan 0 çıkar (gerçek robotta motor ve zemin farkı sapma yaratır). Yön kararlılığını yanal itme sütunu gösterir. Yan eğim: yerçekimi robotun sağına eğik.

| varyant | düz 6 s: yan sapma m / yön ° | yanal itme 10 N 0,3 s, 3 s sonra: yan m / yön ° | dur (0,39'dan): yol m / yön ° | acil stop: yol m / yön ° | 5° yan eğim duruş 5 s: yan kayma m / yön ° | 5° yan eğim düz 5 s: yan kayma m / yön ° |
| --- | --- | --- | --- | --- | --- | --- |
| V0 | 0,000 / 0,0 | 0,000 / 0,0 | 0,070 / -0,0 | 0,228 / -0,0 | -0,000 / 0,0 | -0,000 / 0,0 |
| V1 | 0,000 / 0,0 | 0,000 / 0,0 | 0,070 / -0,0 | 0,228 / -0,0 | -0,000 / 0,0 | -0,000 / 0,0 |
| V2 | 0,000 / 0,0 | 0,000 / 0,0 | 0,055 / -0,0 | 0,228 / -0,0 | -0,000 / 0,0 | -0,000 / 0,0 |
| V3 | 0,000 / 0,0 | 0,006 / 0,3 | 0,070 / -0,0 | 0,228 / -0,0 | -0,010 / -2,8 | -0,239 / -16,5 |
| V4 | 0,000 / 0,0 | 0,006 / 0,4 | 0,083 / -0,0 | 0,218 / -0,0 | -0,013 / -3,6 | -0,430 / -29,2 |
| V1+V3 | 0,000 / 0,0 | 0,006 / 0,3 | 0,070 / -0,0 | 0,228 / -0,0 | -0,010 / -2,8 | -0,239 / -16,5 |
| V2+V3 | 0,000 / 0,0 | 0,003 / 0,1 | 0,055 / -0,0 | 0,228 / -0,0 | -0,010 / -2,8 | -0,061 / -2,9 |
