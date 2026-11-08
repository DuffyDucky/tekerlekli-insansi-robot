# Robot özeti (FreeCAD, 1,58 m; sayılar 09.11.2026)

Tekerlekli insansı robot Lale. Ana tasarım 1,58 m (01.11.2026 kararı, 03.11.2026 CAD); tüm modüller tek montajda (`montaj/robot-montaj.FCStd`).
Kaynak kısaltmaları: **MA** `montaj/montaj-analiz.json`, **BOM** `montaj/robot-bom.csv`, **LK** `lale158/lale158-kontrol.json`,
**UI** `lale158/kafa-yerlesim/uygulama-ivme.json`, **TA** `taban/taban-analiz.json`, **KA** `kafa/kafa-analiz.json`,
**RG** `planlama/d158/regresyon.json` (korunan değerler), **EK** `kod/ortak/eklem_sinirlari.json`. "Tahmini" / "varsayım" yazan değer ölçülmedi.
Koordinat: orijin zemin + robot merkezi, +X sağ, +Y yukarı, +Z ileri (mm). 9 Ekim 2026 tarihli 125 cm özeti aşağıda "Tarihçe" başlığında.

## Modüller (MA `moduller`; baskı adedi BOM "Baski" satırlarından, sol aynalar dahil)

| Modül | Parça | Baskı (adet) | Kütle | Not |
|---|---|---|---|---|
| İskelet | 59 | – | 6.410,8 g | şase + gövde direği 1.115,5 mm tek parça + omuz traversi, sigma 40 × 40 (BOM) |
| Omuz (sağ + sol) | 2 × 73 | 12 | 2 × 567,6 g | 2 eksen, omuz başına DS3235 × 2 |
| Kabuk | 357 | 34 | 7.170,4 g | gövde + etek + 11,6" göğüs ekranı (cep, çerçeve, VESA taşıyıcı) + hoparlör kabı + hub takozlu üst arka kapak |
| Dirsek + bilek + el (sağ + sol) | 2 × 57 | 8 | 2 × 400,5 g | kol başına MG996R × 2 |
| Kafa | 161 | 14 | 2.088,5 g | pan + tilt MG996R, 10,1" QLED, Pi 5 4 GB, Camera Module 3, ReSpeaker v2.0, USB ses kartı, PAM8403 |
| Taban | 342 | 4 | 8.109,8 g | 4 × JGB37, Victron LiFePO4 12,8 V 20 Ah **3,0 kg**, güç elektroniği, kartlar, 3 sonar, acil stop |
| **Toplam (ana montaj)** | **1.179** | **72** (62 kalem) | **25.715,6 g** | + kablo payı 400 g (tahmini) = **26.115,6 g** (UI `ev.kutle_g`) |

- Boy **1.580,0 mm** (LK `toplam_boy_mm`); omuz traversi merkezi y 1.270, gövde uzatması 315, taban 520 mm (MA `s3_mm`, `uzama_mm`, `taban_w_mm`).
- Ağırlık merkezi: montaj (−0,03; 528,46; −9,26) mm (MA `agirlik_merkezi`); ev pozu, kablo payıyla (−0,03; 522,71; −10,03) mm (UI `ev.am`).
- Baskı listesi (`planlama/baski-listesi.md:12`) 65 parça, 7,63–7,68 kg, 159–160 sa gösteriyor: 03.11 koşusu, kafa satırları 7" modelinden; BOM ile fark P4.3'te kapanacak.
- Servolar: 10 (BOM: DS3235 × 4, MG996R × 6); kanal önerisi `planlama/d158/servo-10-oneri.md`.

## Devrilme, motor, akü

- **Devrilme** (TA `robot.pozlar[ev]`; teker hattı x ±216; AM'den devrilme kenarına öne 195, arkaya 175 mm: `dF`, `dR`): ev pozunda devrilme ivmesi ileri / geri / yana 3,66 / 3,28 / 4,05 m/s²,
  statik devrilme eğimi 20,5 / 18,5 / 22,5°; 5° rampada 2,79 / 2,42 / 3,18 m/s². Tüm yüksüz kol pozlarında (ızgara) en kötü pay: rampa 5° geri **1,519**
  (eşik 1,5), düz geri 2,097 (UI `izgara_yuk_0g.a_sinir_pay15`). Elde 100 g / 500 g ile rampa 1,479 / 1,329 (< 1,5): el yükü sınırı **karar bekliyor (K3, K9)**.
- **Tahrik** (TA `motor`): 4 × JGB37-520 12 V 60 dev/dk, teker 125 × 58. Düz zeminde 0,5 m/s² ile 3,31 kg·cm (sürekli 6,3'ün oranı 0,53);
  5° rampada 0,5 m/s² ile 6,86 kg·cm (1,09: sürekli değerin üstünde), 0,25 m/s² ile 5,82 (0,92). Hız ~0,39 m/s. JGB37 torku satıcı etiketi, doğrulanmadı
  (`planlama/adim3/elektrik.md` E0). Yazılımda rampada ivme ve fren ≤ 0,1 m/s² (EK `teker`).
- **Kafa servoları** (KA `tork`): kafa grubu 1.570,8 g; tilt payı (±15) 3,64, pan payı 2,21. Kol servo payları 3,0 kg akü sonrası P3.2'de
  hesaplandı (`planlama/d158/F3a-yuk.json`; AI HAT+ ana modelde yok, K2); el yükü önerisi düzde ≤ 100 g / el (K3, K9).
- **Akü** (TA `aku`): Victron SuperPack 12,8 V 20 Ah, 256 Wh, kullanılabilir × 0,8. Tahmini yüklerle (11,6" göğüs ekranı ve 10,1" QLED dahil) düşük / orta /
  yüksek 16,8 / 36,6 / 85,2 W → 12,2 / 5,6 / 2,4 sa. `elektrik.md` 04.11 kaba tahmini normal kullanımda ~3,8–4,4 sa (47–55 W); iki tahminin farkı
  çözülmedi, ikisi de ölçülmedi.

## Çakışma ve korunan değerler (RG, 09.11)

Kafa içi, kabuk içi, kabuk × iskelet ve ev pozu çakışması 0; mikrofon-hoparlör en az 574,3 mm; SY8205 × kafa kabloları 0 mm³. Eklem aralığında çakışma 0
(`carpisma-sonuc.json`; omuz bölümü 04.11 koşusundan, `tek_kosu` false, P2.2 / P6.1'de yeniden). Göğüs ekranı kablo tüpleri × kasa gerçek çakışma 0,
port girintisi varsayımıyla (LK `kablo_tup_uc_temas`; P1.4 🟡).

## Yazılım sınırları (EK; robot yazılımında uygulanmalı)

| Eklem | Sınır | Neden (EK) |
|---|---|---|
| Omuz öne-arka (S1) | −45…135° | DS3235 180°; horn kol aşağıdayken 45°'de |
| Omuz yana açma (S2) | +5…120° (S1 ≥ 120 iken ≤ 117) | +5: S1 kablo kaseti; S1 kaset kapağı flanşı |
| Dirsek | 0…105° | MG996R, çatal dayanağı |
| Bilek | −90…90° | MG996R |
| Kafa pan | −90…90° | kablo halkası ±90 |
| Kafa tilt | −13…13° | yazılım sınırı (29.10); KA serbest aralık |
| Teker | sınırsız | düzde ivme ≤ 0,5, fren ≤ 1,8 m/s²; rampada ≤ 0,1 m/s² ve kollar ev pozunda |

Kafa-kol yasak kutusu yok (EK `kafa_kol_yasak.aktif` false; P6 tam taramasında yeniden doğrulanacak). Sol kol servo komut işareti ters (tahmini).

## Açık kararlar ve işler

Karar kuyruğu `planlama/d158/karar-kuyrugu.md`: K1 (6. USB cihazı), K2 (AI HAT+ × boss), K3 / K9 (el yükü), K10 (PAM 5 V besleme), K11 (göğüs ekranı 12 V dalı),
K14 (boyun demeti, Efe teyidi) ve diğerleri. İş paketleri ve durum: `planlama/dongu-158.md`. Elektrik: `planlama/adim3/elektrik.md` "158 cm güncellemesi".

---

# Tarihçe: 9 Ekim 2026 özeti (125 cm, FreeCAD V3)

Aşağıdaki metin 125 cm tasarımın özetidir; sayıları güncel değildir.

Tekerlekli insansı robot, tüm modüller çizildi ve tek montajda (`montaj/robot-montaj.FCStd`). Kaynak: modül `*-analiz.json`'ları,
`carpisma-sonuc.json` (bölümlü tek koşu, 8 Ekim 22:17–23:44), `montaj/montaj-analiz.json`. "Tahmini" yazan değerler ölçülmedi.
Koordinat: orijin zemin + robot merkezi, +X sağ, +Y yukarı, +Z ileri (mm).

## Modüller (125 cm)

| Modül | Parça | Baskı (PETG) | Lazer / kesim | Kütle | Not |
|---|---|---|---|---|---|
| İskelet | 59 | – | 7 sigma 40×40 kesimi (3 × 1 m stok) | 5.793 g | şase + gövde direği + omuz traversi |
| Omuz (sağ + sol) | 2 × 68 | 2 × 5 (sol aynalı basılır) | – | 2 × 460 g | 2 eksen, DS3218MG × 2 |
| Kabuk | 202 | 15 | – | 4.901 g | gövde + taban eteği + Nextion 10,1" |
| Dirsek + bilek + el (sağ + sol) | 2 × 53 | 2 × 4 | – | 2 × 369 g | MG996R × 2 |
| Kafa | 98 | 7 | – | 1.363 g | pan + tilt MG996R, 7" LCD, Camera Module 3 |
| Taban | 306 | 4 | 3 (Al 3 mm plaka, 2 × 5 mm kontrplak) | 7.508 g | 4 × JGB37, LiFePO4, güç, kartlar, 3 sonar, acil stop |
| **Toplam (ana montaj)** | **907** | **44** | **3 lazer + 7 profil** | **21.224 g** | + kablo payı 400 g (tahmini) = **21,62 kg** |

Ağırlık merkezi (ev pozu, kollar aşağıda): montaj (−0,4; 374,2; −13,5) mm (11 Ekim tolerans güncellemesinden sonra); kablo payıyla (−0,4; 370,5; −14,4) mm, yerden 370 mm.
Montaj kütlesi + kablo payı = taban raporundaki 21.624,5 g (fark 0,0 g, AM 0,03 mm). `taban_montaj.py` ana montajdaki tabanı çıkarıp "tabansız" robotu buluyor (11 Ekim 2026 düzeltmesi; önceden yeniden koşunca taban iki kez sayılıyordu). Eklemler: 14 döner (2 kol × 4, kafa 2, teker 4) + 7 sabit + zemin.

## Devrilme, motor, akü (125 cm, taban raporu)

- **Devrilme** (temas teker merkez düzlemleri x ±178, z ±185; fren 1,5 m/s², tahmini): ev pozunda devrilme eşiği ileri / geri / yana
  5,3 / 4,5 / 4,7 m/s² (pay 3,5× / 3,0× / 3,1×), statik devrilme eğimi 28° / 25° / 26°. Tüm yüksüz kol pozlarında en küçük pay ~2,9×;
  5° rampada ev pozu payı 2,9× / 2,4× / 2,6×. 1 kg yükle kollar önde ileri pay 2,9×.
- **Tahrik:** 4 × JGB37-520 12 V 60 dev/dk enkoderli, teker 125 × 58. Düz zeminde 0,5 m/s² ile tork %44; 5° rampada 0,5 m/s² ile 5,7 kg·cm =
  sürekli değerin (6,3 kg·cm) **%90**'ı; rampada ivme ≤ 0,25 m/s² ile %77. Hız ~0,39 m/s.
- **Servolar:** omuz S1/S2 DS3218MG yüksüz pay 2,5×; dirsek MG996R 6,1×; kafa tilt 2,1×, pan 3,6×. Ana senaryo yüksüz jest; el ucu yükü ~50 g.
- **Akü:** LiFePO4 12,8 V 24 Ah (307 Wh; model 20 Ah Landport ölçüsüyle). Tahmini çalışma: düşük yük (11 W) ~22 saat, orta (33 W) ~7,5 saat,
  yüksek (81 W) ~3 saat.

## Yazılım sınırları (125 cm; robot yazılımında uygulanmalı; FreeCAD eklem sınırları yalnız fareyle sürüklemede tutuyor)

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

## Açık işler (9 Ekim 2026)

**Tolerans (11 Ekim 2026):** ısıl gömme somun deliği M3 Ø4,0 / M5 Ø6,4 (`arayuz.INSERT_DELIK`; önceden somun dış çapındaydı), üst kol tüpü ↔ pim
her yanda 0,25 mm (`arayuz.GECME`), kabuk dili ile komşunun dış yarısı arası 0,2 mm (`arayuz.KABUK_BINDIRME_BOSLUK`). Rulman yuvaları tam ölçüde;
`test/tolerans_kuponu.py` kuponlarıyla (Ø52, Ø16, Ø40 mil, somun delikleri) seçilecek. Ayrıntı `planlama/baski-listesi.md`.

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
