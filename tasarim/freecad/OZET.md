# Robot özeti (FreeCAD V3, 9 Ekim 2026)

Tekerlekli insansı robot, tüm modüller çizildi ve tek montajda (`montaj/robot-montaj.FCStd`). Kaynak: modül `*-analiz.json`'ları,
`carpisma-sonuc.json` (bölümlü tek koşu, 8 Ekim 22:17–23:44), `montaj/montaj-analiz.json`. "Tahmini" yazan değerler ölçülmedi.
Koordinat: orijin zemin + robot merkezi, +X sağ, +Y yukarı, +Z ileri (mm).

## Modüller

| Modül | Parça | Baskı (PETG) | Lazer / kesim | Kütle | Not |
|---|---|---|---|---|---|
| İskelet | 59 | – | 7 sigma 40×40 kesimi (3 × 1 m stok) | 5.793 g | şase + gövde direği + omuz traversi |
| Omuz (sağ + sol) | 2 × 68 | 2 × 5 (sol aynalı basılır) | – | 2 × 464 g | 2 eksen, DS3218MG × 2 |
| Kabuk | 202 | 15 | – | 4.926 g | gövde + taban eteği + Nextion 10,1" |
| Dirsek + bilek + el (sağ + sol) | 2 × 53 | 2 × 4 | – | 2 × 370 g | MG996R × 2 |
| Kafa | 98 | 7 | – | 1.367 g | pan + tilt MG996R, 7" LCD, Camera Module 3 |
| Taban | 306 | 4 | 3 (Al 3 mm plaka, 2 × 5 mm kontrplak) | 7.508 g | 4 × JGB37, LiFePO4, güç, kartlar, 3 sonar, acil stop |
| **Toplam (ana montaj)** | **907** | **44** | **3 lazer + 7 profil** | **21.261 g** | + kablo payı 400 g (tahmini) = **21,66 kg** |

Ağırlık merkezi (ev pozu, kollar aşağıda): montaj (−0,4; 374,6; −13,5) mm; kablo payıyla (−0,4; 370,5; −14,4) mm, yerden 370 mm.
Montaj kütlesi + kablo payı = taban raporundaki 21.660,9 g (fark 0,0 g, AM 0,03 mm). Eklemler: 14 döner (2 kol × 4, kafa 2, teker 4) + 7 sabit + zemin.

## Devrilme, motor, akü (taban raporu)

- **Devrilme** (temas teker merkez düzlemleri x ±178, z ±185; fren 1,5 m/s², tahmini): ev pozunda devrilme eşiği ileri / geri / yana
  5,3 / 4,5 / 4,7 m/s² (pay 3,5× / 3,0× / 3,1×), statik devrilme eğimi 28° / 25° / 26°. Tüm yüksüz kol pozlarında en küçük pay ~2,9×;
  5° rampada ev pozu payı 2,9× / 2,4× / 2,6×. 1 kg yükle kollar önde ileri pay 2,9×.
- **Tahrik:** 4 × JGB37-520 12 V 60 dev/dk enkoderli, teker 125 × 58. Düz zeminde 0,5 m/s² ile tork %44; 5° rampada 0,5 m/s² ile 5,7 kg·cm =
  sürekli değerin (6,3 kg·cm) **%90**'ı; rampada ivme ≤ 0,25 m/s² ile %77. Hız ~0,39 m/s.
- **Servolar:** omuz S1/S2 DS3218MG yüksüz pay 2,5×; dirsek MG996R 6,1×; kafa tilt 2,1×, pan 3,6×. Ana senaryo yüksüz jest; el ucu yükü ~50 g.
- **Akü:** LiFePO4 12,8 V 24 Ah (307 Wh; model 20 Ah Landport ölçüsüyle). Tahmini çalışma: düşük yük (11 W) ~22 saat, orta (33 W) ~7,5 saat,
  yüksek (81 W) ~3 saat.

## Yazılım sınırları (robot yazılımında uygulanmalı; FreeCAD eklem sınırları yalnız fareyle sürüklemede tutuyor)

| Eklem | Sınır | Neden |
|---|---|---|
| Omuz öne-arka (S1) | −45…135° | DS3218MG 180°, horn kol aşağıdayken 45°'de; geometri −60…180° izin verir |
| Omuz yana açma (S2) | 0…120° | 0°'nin altında kol / el kabuğa çarpar (yana −10°'de el kabuğa giriyor) |
| Dirsek | 0…105° | MG996R, çatal dayanağı |
| Bilek | −90…90° | MG996R |
| Kafa pan | −90…90° | `arayuz.KAFA` (serbest aralık ±180) |
| Kafa tilt | −25…30° | `arayuz.KAFA` (serbest −25…40) |
| Teker | sınırsız | hız / ivme sınırı: rampada ≤ 0,25 m/s² önerilir |
| **Kafa-kol yasak bölgesi** | kol öne 125…135°, yana 0°, dirsek 70…105° iken kafa o kola doğru pan 30…55° (sol kol −55…−30°) **ve** tilt 25…30° birlikte verilmemeli | el ön yüz kabuğuna girer; sınır 5° kesinlikte (yakınsadı), yazılımda +1 adım pay; satır satır tablo `kafa/rapor.html` |

Sol kol servoları aynalı: aynı eklem açısı için sol servo komut işareti ters (tahmini; montajda doğrulanmalı).
Diğer tüm modül çiftlerinde eklem aralığında çakışma 0 (omuz, kol zinciri, kol ↔ kol en az 290 mm, kafa × sabit, taban). En dar yerler:
kol ↔ kabuk ~3,8 mm (kol aşağıda), sabit boyun ↔ kabuk R62 halkası 8,4 mm, kafa ↔ ön kol 25,7 mm, kol ↔ taban/etek ~365 mm.

## Açık işler

**Satın alınacak / BOM'a eklenecek:** 12 V 40 A röle + soket; ESP32 taşıyıcı (pertinaks + 2 × 15'li dişi header); M2,5 pirinç burç + vida
(Pi, PCA9685, BNO055); M4 ve M5 çekiç somun; M5×16 set vida; 25 mm cırt kayış (2); köpük bant; XT60 şarj girişi; 37 mm L motor braketi;
kamera için ~1 m FPC (elimizdeki 200 mm yetmez; Pi tabanda, kamera kafada); kafaya HDMI kablosu (taban → kafa yolu).

**Ölçülecek / doğrulanacak (kumpas, tartı, datasheet):** Limacell 24 Ah akünün ölçüsü, kütlesi ve kutup yeri (yuva 181 × 77 × 167); sigorta
kutusu, röle, ana anahtar ASW-A01, ana sigorta yuvası (tahmini zarflar); BTS7960 delik aralığı; eldeki BNO055 muadili; HC-SR04 pin bloğu;
motor braketi delik düzeni (flanş x 115 hizası); servo horn delik dizilimi (omuz, dirsek); köşe bağlantı ve çekiç somun ölçüleri (iskelet);
Nextion ölçüleri; ısıl gömme somun ölçüleri; LCD kütlesi ve kamera delikleri; 6808-2RS / 625ZZ yük değerleri.

**Tasarım kararları bekleyen:** kabuk etek üst plakasına ana anahtar deliği ve XT60 şarj girişi; etekte ısı (Pi 5 + 3 × XL4016 + 2 × BTS7960)
ölçülüp gerekirse havalandırma; rampada motor torku (%90) için yazılım ivme sınırı ya da daha güçlü motor; 270° servo alınırsa omuz sınırları
genişletilebilir; tilt servosunda radyal yük (ikinci rulman seçeneği).

Ayrıntı: `montaj/rapor.html` (tam robot), modül raporları `iskelet/ omuz/ kabuk/ dirsek/ kafa/ taban/rapor.html`; çalıştırma `README.md`.
