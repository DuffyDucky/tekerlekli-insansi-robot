# Yazılım notu: 1,65 m tasarımdan çıkan sınırlar (stowent için)

25 Ekim 2026 (1,70 m taslak); **29 Ekim 2026 güncellemesi (Y2b): taslak ana tasarım oldu, boy 1,65 m, akü yerinde.** 29.10 ek: rampada fren ≤ 0,1, Pi 4 GB.
Kaynak: `planlama/y2/Y2a-kontrol.md` (bağımsız kontrol), `planlama/kararlar-2026-10-29.md` (Duffy kararları),
`planlama/y2/Y2b-ivme.json` (düz zemin ivme hesabı), taslak analizleri (`tasarim/freecad/taslak-170/`). Eklem sınırları
`kod/ortak/eklem_sinirlari.json`'da (CAD'den üretilir; omuz DS3235, S2 +5…120, kafa tilt ±13°). Dosya adı geçmiş için aynı kaldı.

Ana bilgisayar: **Raspberry Pi 5, 4 GB RAM** (eldeki kart; Duffy 29.10: "pi 4 gb"; eski listelerde 8 GB yazıyordu). Yazılımın bellek bütçesi 4 GB'a göre planlanmalı. İvme / fren sınırları makine okunur olarak `eklem_sinirlari.json` `teker.ivme_sinir_m_s2`'de (düz sürüş 0,5, düz fren 1,8, rampa sürüş 0,1, rampa fren 0,1).

Bağlam: otonom hareket ve ROS 2 yok, kumanda telefondan; üst katman Gemini Robotics-ER (API).

## Zorunlu sınırlar

| # | Kural | Neden |
|---|---|---|
| 1 | **Omuz yana açma (S2) en az +5°**; 0°'a inme | Uzun kolda S2 0°'de el yüz kabuğuna giriyor; S1 kablo kaseti de 5°'yi istiyor |
| 2 | **İnsan ya da engel yakınında kol hızı omuzda ≤ ~1,5 rad/s (~85°/s)**; jest tepe hızı (5,2 rad/s) yalnız boş alanda | Sert bir engele tepe hızda çarpma dirsek çatalını ve servo millerini zorlar (darbe emniyeti 1,22, sınırda) |
| 3 | **Rampada / eğimde (5°) teker ivmesi ≤ 0,1 m/s², yavaşlama ve fren de ≤ 0,1 m/s², kollar ev pozunda** (karar 29 Ekim 2026; fren kısmı Duffy 29.10) | Akü yerinde kaldı (75 mm öne geometrik olarak olmadı). Rampa 5°'de devrilme payı (Y2a'da 1,5 m/s² frenle hesaplandı; ölçüt 1,5): ev pozu **1,58** ✔, kollar geride / yukarıda-yanda 1,48–1,49 ✘, elde 0,5 kg ileri 1,44 ✘. Fren sınırı 1,8 (kural 4) rampada uygulansaydı ev pozunda pay 2,366 / 1,8 = **1,31** (< 1,5) olurdu: bu yüzden rampada yavaşlama / fren de ≤ 0,1 m/s² (karar, Duffy 29.10). Teker motoru rampada 0,5 m/s²'de sürekli torkun %103'ü, 0,1'de ≈ %78'i |
| 4 | **Düz zeminde ivme ≤ 0,5 m/s²** (sürer) | Motor sürekli torkunun ≈ %50'si. Devrilme düzde bağlayıcı değil: pay ≥ 1,5 için sınır ≈ **2,0 m/s²** (el yükü ≤ 100 g; yüksüz 2,06, elde 0,5 kg 1,85), 0,5'te en kötü pay 5,6. **Yazılım / acil stop freni düz zeminde ≤ 1,8 m/s²** (karar 29 Ekim 2026; rampada kural 3: ≤ 0,1): düzde en kötü pay 0,5 kg el yüküyle **1,54**, 100 g 1,68, yüksüz 1,72 (`Y2b-ivme.json` `fren_pay`) |
| 5 | **Kafa tilt ±13°** (önce ±15) | İlk çakışma +18° / −17°'de (kafa kabuğu ↔ rulman yuvası); ±13 ile pay 4–5° |
| 6 | **El yükü ≈ 100 g ile sınırlı** (açık konu, karar değil) | 0,5 kg el yükünde servo payı S1 / S2 0,97, dirsek 0,74 (< 1). 2× pay için ≈ 100 g ya da servo değişimi (Duffy kararı) |

## Takılma / aşırı yük koruması

Omuzdaki DS3235, dirsekteki MG996R'ı geri sürebilir (el bir yere takılırsa dirseğe MG996R'ın ~1,46 katı tork biner).
Öneri: bir eklem takılınca o hattın gücünü kesmek. **Dikkat:** DS3235 ve MG996R standart PWM servo; konumlarını geri
bildirmiyorlar. Bu yüzden "konum hatası izleme" doğrudan yapılamaz. Seçenekler (karar ekipte):

- Servo hattına akım ölçer (ör. INA219/INA226) ve eşik aşılınca PCA9685 çıkışını kapatmak
- Geri bildirimli servoya geçmek (maliyet ve CAD etkisi var)
- Yalnız yazılım: hız ve ivme profillerini yumuşak tutmak, jestleri boş alanda oynatmak (en ucuz, en zayıf)

## Elektrik notu (ölçüm gerekiyor)

Servo hattı (kol + bir kafa servosu) yoğun kullanımda ~5,45 A idi (XL4016'nın sürekli önerisi 5 A). **Karar 29 Ekim 2026:**
iki kol ayrı regülatörde, kafa servoları (pan + tilt) üçüncü bir XL4016'da: sağ kol / sol kol hattı yoğun ≈ 4,87 A (tepe ≈ 7,2 A),
kafa hattı yoğun ≈ 1,5 A (tepe ≈ 5,0 A); ayrıntı `planlama/adim3/elektrik.md` "1,65 m güncellemesi". PCA9685 kanal → hat
eşlemesi değişti (kafa servoları ayrı hatta). Hat akımı yine ölçülmeli; ölçülmeden uzun jest dizisi oynatılmamalı.
