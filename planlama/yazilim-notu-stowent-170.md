# Yazılım notu: 1,70 m taslaktan çıkan sınırlar (stowent için)

25 Ekim 2026. Kaynak: `tasarim/freecad/taslak-170/` analizleri (`rapor.html`, `kol-analiz/rapor.html`,
`KOL125-KONTROL-NOTLAR.md`, `CATAL-KONTROL-NOTLAR.md`). Taslak henüz ana tasarım değil; sayılar onaylanınca
`kod/ortak/eklem_sinirlari.json` güncellenir (şu an 125 cm ve DS3218MG değerleri).

Bağlam: otonom hareket ve ROS 2 yok, kumanda telefondan; üst katman Gemini Robotics-ER (API).

## Zorunlu sınırlar

| # | Kural | Neden |
|---|---|---|
| 1 | **Omuz yana açma (S2) en az +5°**; 0°'a inme | 1,70 m'de kol ×1,25 ile S2 0°'de el yüz kabuğuna giriyor (125 cm'de 5° sınırının nedeni S1 kablo kaseti idi; şimdi iki neden var) |
| 2 | **İnsan ya da engel yakınında kol hızı omuzda ≤ ~1,5 rad/s (~85°/s)**; jest tepe hızı (5,2 rad/s) yalnız boş alanda | Sert bir engele tepe hızda çarpma dirsek çatalını ve servo millerini zorlar (darbe emniyeti 1,22, sınırda) |
| 3 | **Rampada (5°) teker ivmesi ≤ 0,1 m/s²**, kollar ev pozunda | Teker motoru 5° rampada 0,5 m/s²'de %104–106, 0,25'te %88–90; devrilme payı rampada en iyi seçenekte 1,49 (ölçüt 1,5) |
| 4 | Düz zeminde ivme ≤ 0,5 m/s² (mevcut kural sürer) | `planlama/yazilim-plani.md` Y1 |

## Takılma / aşırı yük koruması

Omuzdaki DS3235, dirsekteki MG996R'ı geri sürebilir (el bir yere takılırsa dirseğe MG996R'ın ~1,46 katı tork biner).
Öneri: bir eklem takılınca o hattın gücünü kesmek. **Dikkat:** DS3235 ve MG996R standart PWM servo; konumlarını geri
bildirmiyorlar. Bu yüzden "konum hatası izleme" doğrudan yapılamaz. Seçenekler (karar ekipte):

- Servo hattına akım ölçer (ör. INA219/INA226) ve eşik aşılınca PCA9685 çıkışını kapatmak
- Geri bildirimli servoya geçmek (maliyet ve CAD etkisi var)
- Yalnız yazılım: hız ve ivme profillerini yumuşak tutmak, jestleri boş alanda oynatmak (en ucuz, en zayıf)

## Elektrik notu (ölçüm gerekiyor)

Omuz servo hattı yoğun kullanımda ~5,4 A (XL4016'nın sürekli önerisi 5 A). Hat akımı ölçülmeden uzun jest dizisi
oynatılmamalı. Ölçüm sonucu ekip ile paylaşılmalı.
