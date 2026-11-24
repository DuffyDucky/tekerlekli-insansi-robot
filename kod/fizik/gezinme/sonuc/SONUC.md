# Gezinme ölçümleri: A'dan B'ye ve kayıp robot (2026-11-25)

Kaynak: `senaryo_ab.py --olcum`, `senaryo_kayip.py --olcum` (koşu başına ham JSON `ham/`, depoya girmez; özet
`senaryo_ab.csv`, `senaryo_kayip.csv`). Fizik MuJoCo 4.0.1, varyant **ONERI** (öneri firmware PI + ön omni küre modeli,
koridor deneyinin varyantı; bugünkü robot DEĞİL), sanal LiDAR 500 ışın/10 Hz gürültülü, denetim 20 Hz, Pi istemci →
sahte ESP32 yolu (sonar kuralı açık). Başarı: Beyin `bitti` dedi ve gövde merkezi hedefe ≤ 0,30 m (yer gerçeği).

**Özet:** A→B 36/36, kayıp robot 30/30 başarılı; 66 koşuda **sıfır temas**. Başarısız koşu yok, bu yüzden "başarısızlık ve
nedeni" listesi boş; zayıf noktalar aşağıda ölçümle birlikte.

## Senaryo 1: A'dan B'ye (6 koridor × 3 hedef × 2 tohum = 36)

Bilinen koridor ve bilinen başlangıç (`baslangic` ± 0,10 m, ± 3° sapma, tohuma göre); konumlayıcı `CokHaritaliMCL`
tek harita, 1500 parçacık; rota `rota.py` (koridor çizgesi, Dijkstra), izleyici `izleyici.py`. Süre sınırı
rota/0,25 × 1,8 + 40 s. Hedefler: koridorun ≈ %30, ≈ %65 kapısı ve son kapı (koridor_4'te orta hedef kol kapısı).

| koridor | hedef | rota m | başarı (t1, t2) | süre s (t1/t2) | varış hatası m (t1/t2) | tahmin hatası m (en çok) | temas |
|---|---|---|---|---|---|---|---|
| koridor_1 | k1_kapi_5 | 7.28 | evet, evet | 31.8 / 31.8 | 0.048 / 0.048 | 0.0023 | 0 |
| koridor_1 | k1_kapi_12 | 17.77 | evet, evet | 73.8 / 73.8 | 0.048 / 0.049 | 0.0022 | 0 |
| koridor_1 | k1_kapi_18 | 26.77 | evet, evet | 109.8 / 109.8 | 0.048 / 0.046 | 0.0022 | 0 |
| koridor_2 | k2_kapi_1 | 1.48 | evet, evet | 8.7 / 8.7 | 0.045 / 0.049 | 0.0019 | 0 |
| koridor_2 | k2_kapi_2 | 6.67 | evet, evet | 29.4 / 29.4 | 0.049 / 0.049 | 0.0022 | 0 |
| koridor_2 | k2_kapi_3 | 9.28 | evet, evet | 39.9 / 39.9 | 0.049 / 0.044 | 0.0031 | 0 |
| koridor_3 | k3_kapi_2 | 4.28 | evet, evet | 19.9 / 19.8 | 0.047 / 0.054 | 0.0074 | 0 |
| koridor_3 | k3_kapi_5 | 10.68 | evet, evet | 45.5 / 45.5 | 0.049 / 0.046 | 0.0027 | 0 |
| koridor_3 | k3_kapi_8 | 21.48 | evet, evet | 93.4 / 93.4 | 0.049 / 0.050 | 0.0029 | 0 |
| koridor_4 | k4_kapi_3 | 5.17 | evet, evet | 23.4 / 23.4 | 0.055 / 0.057 | 0.0096 | 0 |
| koridor_4 | k4_kapi_9 | 16.18 | evet, evet | 72.1 / 72.1 | 0.049 / 0.048 | 0.0022 | 0 |
| koridor_4 | k4_kapi_11 | 19.18 | evet, evet | 79.4 / 79.4 | 0.049 / 0.049 | 0.0017 | 0 |
| koridor_5 | k5_kapi_3 | 6.17 | evet, evet | 27.5 / 27.5 | 0.039 / 0.041 | 0.0090 | 0 |
| koridor_5 | k5_kapi_6 | 12.18 | evet, evet | 51.5 / 51.5 | 0.051 / 0.049 | 0.0031 | 0 |
| koridor_5 | k5_kapi_10 | 20.18 | evet, evet | 83.4 / 83.5 | 0.050 / 0.047 | 0.0029 | 0 |
| koridor_6 | k6_kapi_3 | 6.17 | evet, evet | 27.5 / 27.5 | 0.042 / 0.044 | 0.0048 | 0 |
| koridor_6 | k6_kapi_6 | 12.18 | evet, evet | 51.5 / 51.5 | 0.051 / 0.044 | 0.0038 | 0 |
| koridor_6 | k6_kapi_10 | 20.18 | evet, evet | 83.4 / 83.5 | 0.048 / 0.047 | 0.0018 | 0 |

Ortalama varış hatası 0,048 m (en çok 0,057), konum tahmini hatası en çok 0,010 m; ortalama hız rota/süre 0,23 m/s
(seyir 0,25). Yol / rota oranı 0,97–1,01. RTF en az 5,8 (2 ağır süreç paralel, tek iş parçacığı).

**Engel demosu** (`senaryo_ab.py --engel`, `ham/ab_engel.json`, kayıt `../kayit/ab_engel.npz`): koridor_5 → kapi_6 yolunda
(6,0; 6,2)'de r 0,2 m silindir "insan". Robot 17,6 s'de durdu, 8,2 s bekledi, insan 25,7 s'de çekilince devam etti;
başarı, varış hatası 0,051 m, temas 0.

## Senaryo 2: kayıp robot (6 koridor × 5 bırakma = 30)

Robot koridorda rastgele bir yere ve yöne bırakılır (arka dingil yüzeylerden ≥ 0,60 m, gövde ≥ 0,05 m); hangi koridorda
olduğunu bilmez: `CokHaritaliMCL` 6 harita, 3000 parçacık. Karar kuralı: en olası koridorun olasılığı ≥ 0,90 ve konum
kararlı, 10 tarama üst üste. Kararsızken tepkisel keşif (boşluk yönü, ortalama, önü kapalıysa yerinde dönüş); karardan
sonra hedef kapıya (göreli `kapi_1..3`, ilgili koridorun durağı) rota. Süre sınırı 300 s.

| koridor | bırakma | başlangıç (x, y, yön°) | hedef | başarı | karar yolu m | karar anı s | karar | süre s | yol m | varış hatası m | temas |
|---|---|---|---|---|---|---|---|---|---|---|---|
| koridor_1 | b0 | 14.21, 5.81, 129 | k1_kapi_2 | evet | 0.57 | 3.5 | koridor_1 ✓ | 42.5 | 9.61 | 0.047 | 0 |
| koridor_1 | b1 | 10.91, 5.94, -1 | k1_kapi_3 | evet | 8.44 | 42.9 | koridor_1 ✓ | 102.3 | 22.01 | 0.050 | 0 |
| koridor_1 | b2 | 10.66, 6.42, -12 | k1_kapi_2 | evet | 8.66 | 44.2 | koridor_1 ✓ | 109.5 | 23.74 | 0.047 | 0 |
| koridor_1 | b3 | 23.13, 5.65, -159 | k1_kapi_1 | evet | 4.82 | 24.6 | koridor_1 ✓ | 88.4 | 20.05 | 0.047 | 0 |
| koridor_1 | b4 | 26.84, 5.57, -110 | k1_kapi_3 | evet | 0.18 | 2.4 | koridor_1 ✓ | 92.2 | 21.31 | 0.050 | 0 |
| koridor_2 | b0 | 11.78, 6.88, -56 | k2_kapi_2 | evet | 0.55 | 3.4 | koridor_2 ✓ | 21.9 | 4.05 | 0.050 | 0 |
| koridor_2 | b1 | 7.37, 7.15, 106 | k2_kapi_3 | evet | 0.30 | 2.7 | koridor_2 ✓ | 25.0 | 4.77 | 0.047 | 0 |
| koridor_2 | b2 | 6.48, 6.76, -45 | k2_kapi_3 | evet | 0.47 | 2.9 | koridor_2 ✓ | 22.0 | 4.55 | 0.049 | 0 |
| koridor_2 | b3 | 3.67, 6.32, 6 | k2_kapi_2 | evet | 0.49 | 3.1 | koridor_2 ✓ | 23.2 | 4.85 | 0.045 | 0 |
| koridor_2 | b4 | 7.02, 6.93, -122 | k2_kapi_2 | evet | 0.37 | 2.6 | koridor_2 ✓ | 15.7 | 2.40 | 0.048 | 0 |
| koridor_3 | b0 | 14.17, 2.54, -91 | k3_kapi_1 | evet | 0.40 | 3.8 | koridor_3 ✓ | 50.2 | 10.99 | 0.049 | 0 |
| koridor_3 | b1 | 2.89, 2.16, -57 | k3_kapi_2 | evet | 1.28 | 7.2 | koridor_3 ✓ | 17.3 | 3.15 | 0.047 | 0 |
| koridor_3 | b2 | 16.01, 4.09, 164 | k3_kapi_1 | evet | 0.42 | 4.1 | koridor_3 ✓ | 70.4 | 14.82 | 0.049 | 0 |
| koridor_3 | b3 | 8.06, 2.16, -57 | k3_kapi_3 | evet | 0.35 | 2.7 | koridor_3 ✓ | 7.3 | 0.80 | 0.057 | 0 |
| koridor_3 | b4 | 8.49, 2.31, 46 | k3_kapi_1 | evet | 0.57 | 3.8 | koridor_3 ✓ | 31.6 | 6.30 | 0.050 | 0 |
| koridor_4 | b0 | 19.46, 6.55, 26 | k4_kapi_3 | evet | 0.49 | 3.1 | koridor_4 ✓ | 60.8 | 13.73 | 0.046 | 0 |
| koridor_4 | b1 | 20.93, 6.26, -26 | k4_kapi_1 | evet | 0.49 | 3.0 | koridor_4 ✓ | 81.0 | 18.66 | 0.050 | 0 |
| koridor_4 | b2 | 4.15, 6.58, 18 | k4_kapi_2 | evet | 0.60 | 3.7 | koridor_4 ✓ | 9.3 | 0.95 | 0.121 | 0 |
| koridor_4 | b3 | 11.26, 9.51, 44 | k4_kapi_3 | evet | 0.36 | 2.8 | koridor_4 ✓ | 45.6 | 8.80 | 0.048 | 0 |
| koridor_4 | b4 | 2.50, 6.14, 122 | k4_kapi_3 | evet | 0.51 | 4.4 | koridor_4 ✓ | 27.7 | 5.20 | 0.052 | 0 |
| koridor_5 | b0 | 18.72, 5.93, 153 | k5_kapi_3 | evet | 25.66 | 133.8 | koridor_5 ✓ | 150.4 | 28.57 | 0.051 | 0 |
| koridor_5 | b1 | 10.46, 6.53, 132 | k5_kapi_1 | evet | 19.72 | 104.4 | koridor_5 ✓ | 146.3 | 28.97 | 0.049 | 0 |
| koridor_5 | b2 | 20.09, 6.02, -99 | k5_kapi_3 | evet | 0.33 | 4.1 | koridor_5 ✓ | 58.9 | 12.72 | 0.052 | 0 |
| koridor_5 | b3 | 21.29, 6.49, -176 | k5_kapi_1 | evet | 4.34 | 22.3 | koridor_5 ✓ | 76.9 | 17.31 | 0.047 | 0 |
| koridor_5 | b4 | 5.86, 6.00, 76 | k5_kapi_3 | evet | 6.53 | 33.9 | koridor_5 ✓ | 56.7 | 10.92 | 0.052 | 0 |
| koridor_6 | b0 | 6.23, 6.32, 167 | k6_kapi_3 | evet | 12.28 | 66.6 | koridor_6 ✓ | 80.1 | 14.32 | 0.053 | 0 |
| koridor_6 | b1 | 22.90, 5.77, -134 | k6_kapi_3 | evet | 1.38 | 8.2 | koridor_6 ✓ | 65.2 | 14.97 | 0.049 | 0 |
| koridor_6 | b2 | 15.92, 6.47, -73 | k6_kapi_2 | evet | 0.58 | 4.5 | koridor_6 ✓ | 51.3 | 10.99 | 0.048 | 0 |
| koridor_6 | b3 | 6.30, 6.40, -138 | k6_kapi_3 | evet | 14.08 | 75.9 | koridor_6 ✓ | 96.5 | 17.98 | 0.051 | 0 |
| koridor_6 | b4 | 3.18, 5.98, -9 | k6_kapi_3 | evet | 8.66 | 44.2 | koridor_6 ✓ | 66.0 | 12.89 | 0.052 | 0 |

| koridor | başarı | karar yolu m (ortanca / en çok) | karar anı s (en çok) | süre s (ortanca) |
|---|---|---|---|---|
| koridor_1 | 5/5 | 4.82 / 8.66 | 44.2 | 92.2 |
| koridor_2 | 5/5 | 0.47 / 0.55 | 3.4 | 22.0 |
| koridor_3 | 5/5 | 0.42 / 1.28 | 7.2 | 31.6 |
| koridor_4 | 5/5 | 0.49 / 0.60 | 4.4 | 45.6 |
| koridor_5 | 5/5 | 6.53 / 25.66 | 133.8 | 76.9 |
| koridor_6 | 5/5 | 8.66 / 14.08 | 75.9 | 66.0 |


Yanlış koridor kararı 0, yeniden planlama 0, keşfe geri dönüş 0.

## Zayıf noktalar (ölçülen)

- **Simetrik / tekrarlı koridorlar yavaş karar veriyor.** koridor_5'te iki bırakmada karar 20–26 m yol ve 104–134 s
  sürdü (p 0,91–0,94'te ancak eşiği geçti); koridor_1 ve koridor_6'da 5–14 m. Kapı dizileri benzer olan bölümlerde
  parçacıklar birkaç aday arasında kalıyor. Kural 0,90 eşiğini korudu, yanlış karar vermedi; bedeli süre.
- **Konum hatası iyimser.** Sahne haritası ile MCL haritası aynı dosyadan; gerçek koridorda harita farkı, insanlar ve
  yansıyan yüzeyler olacak. A→B tahmin hatası (≤ 0,01 m) gerçek donanımda beklenecek değer değil.
- **Varış hatası ≈ 0,05 m sabit** (izleyici `varis_payi_m` 0,05): yumuşak varış; daha sıkı park gerekirse ayar.
- **Engel bekleme yalnız durur**, etrafından dolaşmaz (2,0 m koridorda dönme çapı 1,04 m; dolaşma ayrı iş).
- **İlk küresel güncelleme ≈ 2 s** (6 harita × 3000 parçacık): kayıp senaryosunda 3B pencere açılışta bir kez donuyor.
- Bu ölçümlerin çoğu Normal öncelikte koştu (öncelik düzeltmesi koşu sırasında yapıldı, süreçler elle BelowNormal'a alındı);
  sonuçları etkilemez, yalnız RTF'yi.
