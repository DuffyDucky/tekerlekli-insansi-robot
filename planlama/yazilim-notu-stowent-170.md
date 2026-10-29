# Yazılım notu: 1,65 m tasarımdan çıkan sınırlar (stowent için)

25 Ekim 2026 (1,70 m taslak); **29 Ekim 2026 güncellemesi (Y2b): taslak ana tasarım oldu, boy 1,65 m, akü yerinde.**
Kaynak: `planlama/y2/Y2a-kontrol.md` (bağımsız kontrol), `planlama/kararlar-2026-10-29.md` (Duffy kararları),
`planlama/y2/Y2b-ivme.json` (düz zemin ivme hesabı), taslak analizleri (`tasarim/freecad/taslak-170/`). Eklem sınırları
`kod/ortak/eklem_sinirlari.json`'da (CAD'den üretilir; omuz DS3235, S2 +5…120, kafa tilt ±13°). Dosya adı geçmiş için aynı kaldı.

Bağlam: otonom hareket ve ROS 2 yok, kumanda telefondan; üst katman Gemini Robotics-ER (API).

## Zorunlu sınırlar

| # | Kural | Neden |
|---|---|---|
| 1 | **Omuz yana açma (S2) en az +5°**; 0°'a inme | Uzun kolda S2 0°'de el yüz kabuğuna giriyor; S1 kablo kaseti de 5°'yi istiyor |
| 2 | **İnsan ya da engel yakınında kol hızı omuzda ≤ ~1,5 rad/s (~85°/s)**; jest tepe hızı (5,2 rad/s) yalnız boş alanda | Sert bir engele tepe hızda çarpma dirsek çatalını ve servo millerini zorlar (darbe emniyeti 1,22, sınırda) |
| 3 | **Rampada / eğimde (5°) teker ivmesi ≤ 0,1 m/s² ve kollar ev pozunda** (karar 29 Ekim 2026) | Akü yerinde kaldı (75 mm öne geometrik olarak olmadı). Rampa 5°'de devrilme payı (acil stop freni 1,5 m/s², tahmini; ölçüt 1,5): ev pozu **1,58** ✔, kollar geride / yukarıda-yanda 1,48–1,49 ✘, elde 0,5 kg ileri 1,44 ✘. Teker motoru rampada 0,5 m/s²'de sürekli torkun %103'ü, 0,1'de ≈ %78'i |
| 4 | **Düz zeminde ivme ≤ 0,5 m/s²** (sürer) | Motor sürekli torkunun ≈ %50'si. Devrilme düzde bağlayıcı değil: pay ≥ 1,5 için sınır ≈ **2,0 m/s²** (el yükü ≤ 100 g; yüksüz 2,06, elde 0,5 kg 1,85), 0,5'te en kötü pay 5,6. Yazılım freni de ≤ 2 m/s² kalmalı (el yükü ≤ 100 g iken pay ≥ 1,5) |
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

Omuz servo hattı yoğun kullanımda ~5,4 A (XL4016'nın sürekli önerisi 5 A). Hat akımı ölçülmeden uzun jest dizisi
oynatılmamalı. Ölçüm sonucu ekip ile paylaşılmalı.
