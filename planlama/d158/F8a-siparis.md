# F8a: 158 sipariş paketi (P8.1)

Kontrol tarihi: **09.11.2026**. Fiyatlar satıcı sayfasında görülen KDV dahil fiyattır, kargo hariç. **Sipariş verilmedi**, sepete ürün eklenmedi, satıcıya yazılmadı.
Brief: `planlama/d158/F8a-brief.md`. Yöntem, bakılan sayfalar ve öneriler: `planlama/d158/F8a-gunluk.md`. Makine okunur veri: `planlama/d158/F8a-siparis.json`.

**158 güncel liste** burada şu demek: malzeme listesi v4 (03.11) + K4 kabloları ve F1b 90° fişleri (F4a, `maliyet.json` `fiyat_bekliyor`). `maliyet.json` 29.10 (1,65 m) listesi + F4a'nın 09.11 kısmi eklemeleri (MAX98357A V3'ten çıktı, 11 `fiyat_bekliyor` satırı); 11,6" göğüs ekranı, QLED, ReSpeaker v2.0 ve D24V50F5 onda yok (köprü §7).
Düzeltme turu 1 (09.11.2026): bağımsız kontrol `F8a-kontrol.md` (KOŞULLU) uygulandı; değişiklik listesi günlük §9.

## 1. Özet

| | Değer |
|---|---|
| Sipariş satırı (onaylı site + K4/F1b + bulunamayanlar + kamera) | 136 |
| Fiyatı bugün sayfada görülen, onaylı satıcı | 86 satır, 68.455,64 TL |
| Fiyatı bugün sayfada görülen, onaylı olmayan satıcı (rulman, sigma profil, T-somun, köşe bağlantı) | 7 satır, 4.100,80 TL |
| Kısmen: sayfa taban fiyatı, boy/varyant seçilmeden (paslanmaz vida, M6×16 dahil; insert) | 27 satır, 1.962,31 TL |
| Doğrulanmadı (v4 yaklaşık fiyatı kullanıldı) + stok yok | 9 + 1 satır, 4.629,63 TL |
| Bulunamadı / fiyat yok (toplama girmez) | 6 satır |
| Hizmet (3B baskı, lazer, bükme; tahmini, teklif yok) | 4 satır, 14.390,00 TL |
| **Parça toplamı, doğrulanmamış dahil** | **79.148,38 TL** |
| Parça toplamı, doğrulanmamış hariç (doğrulanmış + kısmen) | 74.518,75 TL |
| **Okul bütçesi (parça + hizmet), doğrulanmamış ve K4 dahil** | **93.538,38 TL** |
| Okul bütçesi, doğrulanmamış hariç | 88.908,75 TL |
| Okul bütçesi, kararsız kalemler hariç (K4 çıkar; K1, K9, K10, K11, K12 varsayılanla 0 TL) | 93.147,10 TL |
| Okul bütçesi (93.538,38) × 1,15 | 107.569,14 TL; kararsız hariç × 1,15: 107.119,16. Kıyas: `maliyet.json` elimizdekiler düşülmüş 78.023,96 → +29.545,18 (§7) |
| PAKET A (TÜBİTAK önerisi, ayrı bütçe; okul toplamına girmez) | 13 satır, 14.215,11 TL |
| Koşullu (etek fanı, omni teker; toplama girmez) | 4.587,68 TL |
| Erken alım (proje-plani §, 1.496 TL) bugün | 1.515,90 TL (+19,53); Rhino kargosuyla 1.654,90 TL (§4) |

Ana bulgular:
- **Akü (Victron, Atakale) stok 1 ve özel sipariş:** sayfa '7 gün içinde üreticiden/ithalatçıdan tedarik edilerek özel sipariş' diyor. S'de (16.11) sipariş → varış ≈ 24–28.11; taban adım 9 (akü) ≈ 25–26.11: **sınırda**. Planın yedeği Limacell 24 Ah (onaylı değil) bugün 4.814,86, 'ortalama hazırlanma süresi 3 iş günü' → S'de sipariş ≈ 20–24.11. Takvim §3.1.
- **M6×16 fosfat (taban, 18 adet): CNC Marketi'de 2 adet.** İkinci satıcı paslanmaz DIN 912 A2 M6×16 (paslanmazcivata.ist, taban 3,89); muadil CNC M6×16 fosfat bombe başlı 4,80, stok 235. Toplama paslanmaz girdi (+5,22).
- **Erken alım insertinde CAD'in L 5,7'si Rhino sayfasında yok.** Üç seçenek §4.1; karar Ahmet'in.
- **QLED 10,1" stok 2** (v4'te 4). İkinci satıcı Motorobit 15.300,00 (2,1×), Direnc 8.523,08 tükendi.
- **Tırtıllı somun M5 (Robotistan) tükendi.** İkinci: CNC Marketi kanal 10 M5 3,96 (onaylı değil), 8 adet 31,68 TL.
- **11 fiyatsız adaydan 9'u fiyatlandı.** L USB-A dirsek ve L 3,5 mm kısa kablo onaylı sitelerde bulunamadı. 90° micro USB adaptörü yok; muadil 90° USB-A → micro B kablo (boyu sayfada yok).
- Planın 'stoksuz kritik' dört kaleminden üçü artık stokta: ön şarj rölesi (Direnc, stokta), optokuplör (Robotistan stok 33), kart burcu (Robotistan stok 2.457). **Mesafe burcu M5×40 hâlâ bulunamadı.**
- Kamera Module 3 tükendi (Robotistan iki sayfa, Robocombo v4'te). 8 Ω hoparlör (PAKET A) stok 1 < 3, fiyat sayfada görünmüyor.

## 2. Fark tablosu: hocadaki liste ↔ 158 güncel liste

**Hangi liste hocada?** Brief'in kaynağı `siparis-farki-2026-10-29.md`: 17.10 Excel (= `maliyet.json` `b27fd80`, 97 satır, ara 86.672,21, genel 99.673,04). Ama `tubitak-2209b/` notları (salt okundu) 03.11 v4 listesinin hocanın öğrencisine gönderildiğini yazıyor (`BAGLAM.md:221-222`; `malzeme-listesi/rapor.md:4` ise 'Liste gönderilmedi' diyor, çelişki). Bu yüzden iki fark veriyorum: 2.1 17.10 Excel'e göre (brief), 2.2 v4'e göre. Hangisinin hocada olduğunu Ahmet teyit etmeli (§9 madde 1).

### 2.1 17.10 Excel → 158

**Eklenen: 15 satır grubu (44 satır)** · **Çıkan: 8 satır grubu (10 satır)** · **Model, satıcı ya da adet değişen: 37 grup**

Eklenenler

| Kalem | Adet | Neden (karar / paket) |
|---|---|---|
| Göğüs ekranı 11,6" 1080p (Robotistan) | 1 | Göğüs ekranı geri geldi, 11,6" (dongu-158; F1b kablo yolu) |
| Göğüs ekranı 12 V regülatörü, HDMI 1,5 m, 90° HDMI adaptör | 1+1+1 | 11,6" ekranın beslemesi ve kablosu (03.11 kararı: regülatörlü 12 V; F1b 90° fiş) |
| 90° micro USB (dokunmatik) + 90° DC jak (12 V) | 1+1 | F1b kontrolü: üç fişin üçü de 90° olmalı (`F1b-kontrol.md:56`) |
| Kafa ekranı 5 V düşürücü SY8205 + micro USB 30 cm besleme | 1+1 | QLED Power girişi Pi hattından ayrı (v4 notu) |
| PAM8403 amfi + USB ses kartı | 1+1 | K16 kapandı (04.11): MAX98357A yerine |
| USB hub 4 port | 1 | K5/K17 (05.11, B + R1): hub gövdede; robotta 6 USB cihazı, Pi'de 4 port |
| Yönlü mikrofon kolu (kardioid) | 1 | Efe 26.10 mikrofon raporu; onaylı sitede yok, (a) satırı, 2.000 tahmini |
| Perçin somun M3 ×7, M5 ×9 + ISO 7380 M5×18 ×9 | 3 satır | Y3 M6 CAD bağlantıları (17.10'da koşullu satırdı, artık kesin) |
| Dişli çubuk M3 (kafa saplama 4 parça) | 1 | Y2b CAD kafada 4 saplama |
| M4×12 ×4 (göğüs VESA), M6×18 ×2 (göğüs taşıyıcı) | 2 satır | Göğüs ekranı montajı |
| M2,5×5, M2,5×8 imbus, M2×8 PT, köpük bant 1 mm, mumlu ip | 5 satır | Model çıktısı (v4); fiyatların çoğu yok |
| Kablo bağı tabanı 10 paket | 1 | 17.10'da kablo bağıyla tek satırdı; v4'te ayrı satır |
| K4 kabloları: USB-A uzatma 30 cm ve 1 m, L USB-A dirsek, kısa micro USB, hoparlör kablosu, L 3,5 mm | 6 | K4 açık (varsayılan a: koşullu kalem); kafa kablo listesi `uygulama-notu.md` |
| PAKET A: 13 kalem (AI HAT+ dahil) | 13 | TÜBİTAK 2209-B önerisi, ayrı bütçe; AI HAT+ yerleşimi K2 açık |
| 3B baskı hizmeti (anlaşmalı firma, 7,7 kg) | 1 | Filament satırlarının yerine (03.11: firma ve ekip basar) |

Çıkanlar

| Kalem | Neden |
|---|---|
| Göğüs ekranı Nextion 10,1" (elde) | 25.10 kaldırıldı; yerine 11,6" (yeni satır). Eldeydi, toplamda değildi |
| Mikrofon ReSpeaker Lite | Dizi değişti: 29.10 XVF3800, v4'te ReSpeaker Mic Array v2.0 (XVF3800 Türk satıcıda yok) |
| Ses amfisi Adafruit MAX98357A | K16 (04.11): PAM8403 + USB ses kartı |
| Yüz paneli 3 mm akrilik | 10,1" kafada panel yok |
| Tırtıllı somun M4 ×8 | 1,65 m CAD'de silindi (Y2b) |
| Bluetooth gamepad | Ahmet'in 03.11 kararı: oyun kolu yok (v4 raporu) |
| PETG ×7 + PETG-CF ×3 filament (3 satır) | 03.11: filament firma ve ekipten; satın alınmaz, yerine baskı hizmeti |
| Eşik altı kargo satırı (12 × 120) | v4 kargo hariç; satıcı eşikleri §8 |

Değişenler

| Kalem | 17.10 | 158 | Neden |
|---|---|---|---|
| Omuz servosu | DS3218MG ×4 + yedek 1 (964,50) | DS3235 ×5, Robocombo 1.809 (liste 1.930) | Kol ×1,25, omuz torku; DS3218 yetmiyor (29.10) |
| Yüz ekranı | Waveshare 7" (C) 2.790,25 | 10,1" QLED Robotistan 7.217,95 | Hoca 10" istedi (21.10); v4'te QLED (03.11) |
| Ana bilgisayar (elde) | Pi 5 8 GB | Pi 5 4 GB (elde) | 29.10: eldeki kart 4 GB |
| Kafa 5 V düşürücü | Pololu D36V50F5 (ithal) 1.975,38 | Pololu D24V50F5 Robotistan 2.266,93 | Onaylı satıcıda bulunan Pololu |
| Akü şarj cihazı | LiFePO4 4S 6 A (UserPil) 1.661,40 | IMAX B6 80 W Robocombo 1.809 | Onaylı satıcı; LiFe modu var, 50 W → 4S'te ≈ 3,4 A (v4 notu) |
| Acil stop | Emas B200E 40 mm (Elektrix) | NP2-BE102 NC metal (Motorobit) 306 | Onaylı satıcı |
| Röle K1 | Elo mini oto röle 40 A | MAH-112-C-4 30/40 A (Motorobit) 183,60 | Onaylı satıcı |
| Hızlı klemens | WAGO 221-413 10'lu (Trendyol) | WAGO 2273-203 ×10 (Motorobit) | Onaylı satıcı; farklı seri |
| XT60 | Çift ×5 (Robotsepeti) | XT60H dişi ×5 + erkek ×5 (Robocombo) | Onaylı satıcı |
| XT60 şarj girişi tutucusu | Panel tutucu (tahmin) | XT60E-M panel erkek (Motorobit) | Model |
| Ana sigorta yuvası | Hepsiburada 550 | Robotistan standart boy 48,18 | Onaylı satıcı |
| Kamera kablosu | Adafruit 5819 (ithal) | Direnc Pi 5 FPC 300 mm 175,43 | Onaylı satıcı |
| Mikro HDMI kafa kablosu | Mikro HDMI → HDMI 25–30 cm | DIY HDMI şerit 30 cm + 2 fiş (3 satır) | Kafa içi kısa set (03.11) |
| ESP32 – Pi USB kablosu | 1,5 m ×1 | 2 m ×2 (ESP32 + göğüs dokunmatik) | Göğüs dokunmatiği eklendi |
| Motor montaj braketi | Robotzade 37 mm ×4 | Robotistan L tipi 37D ×2 paket (4 adet) | Onaylı satıcı |
| Motor sürücü | BTS7960B ×2 + yedek (Makermarketim) | BTS7960B ×3 (Robotistan) | Onaylı satıcı |
| Kart burcu | Direnc 200 parça set | Robotistan M3×8 ×48 | Onaylı satıcı, adet |
| M2,5 distans | Pirinç set (Amazon) | YP-600 plastik ×20 (Direnc) | Onaylı satıcı |
| Servo horn 25T | Robiz alüminyum ×10 | Motorobit 25T gri ×10 | Onaylı satıcı |
| Servo uzatma 1 m | 14 | 19 | Uzun kol + gövde (29.10) |
| XL4016 | 3 | 4 | 29.10 servo hattı kararı |
| Hat sigortası yuvası (mini) | 3 | 5 | XL4016 4. girişi + göğüs 12 V dalı |
| Bıçak sigorta (ek) | 5 (tek satır) | 7 (mini 2/5/7,5×2/10 A + standart 2/5 A) | 29.10 kararı + göğüs 2 A |
| TVS | 2 (tahmin) | P6KE6V8A ×2 + P6KE18A ×1 | Kafa ekranı ayrı 5 V dalı |
| Silikon kablo 18 AWG | 10 m | 14 m (7+7) | v4 model boyları |
| Silikon kablo 12 / 16 AWG | Motorobit / tahmin | Robocombo 2+2 / 1+1 | Onaylı satıcı |
| Delikli pertinaks | 4 (70×50) | 5 (6×13 cm, kesilir) | Muadil ölçü |
| Diyot, direnç seti, klemens + header | Tahmin satırları | Ayrı satırlar, onaylı satıcı | v4 |
| Cırt kayış, kablo bağı | Tahmin | Motorobit 20×400 ×4; Direnc 100'lü | v4 |
| Optokuplör, MOSFET | Direnc | Robotistan | Onaylı satıcı (Direnc'te tükendi) |
| Sigma profil | 3 × 1 m çubuk 908,33 | 3 m ölçüye kesim 934,08 (1.115,5 + 2×500 + 200 + 3×190) | 158 direği tek parça |
| T-somun M6 (kanal 10) | 50 | 62 | Model 60 + 2 |
| Tırtıllı somun M5 | CNC Marketi | v4 Robotistan; bugün tükendi → CNC Marketi | Stok |
| Alüminyum bükme braket | 10 | 14 | Gövde U braketi 4 → 8 |
| Alüminyum lazer alt plaka | 270 × 500 | 346 × 500 | Taban 520 |
| Vida adetleri | M3 DIN912 198, ISO7380 M3 70, M4 56, M5 20, M6 32, fiberli 48, pul 70 | 206, 138, 60, 15, 44, 62, 90 | 158 model çıktısı (v4) |
| Isıl gömme somun | M3 125, M5 12 | M3 176 (plan/maliyet 168), M5 6 | 158 model; 168/176 farkı günlükte |

Aynı kalanlar: enkoderli motor, arazi tekerleği, kaplin, akü (Victron 20 Ah, Atakale), rulmanlar, mesafe burcu, JR konnektör, soğutucu, ESP32, PCA9685, BNO055, HC-SR04 (satıcıların bir kısmı değişti), kamera, hoparlör, bas-konuş, sigorta kutusu, ana sigorta, ana anahtar, kondansatör, makaron, ön şarj rölesi ve direnci, akü pabucu, röle soketi, gizli ve geniş köşe, M6×16 fosfat, set vidalar, MG996R (6 + 2 yedek), servo sayısı 10 (4 omuz + 6).

Tutar: 17.10 genel 99.673,04 (pay dahil, elde ve kargo dahil) → bugünkü 158 okul bütçesi 93.538,38 TL (pay yok, elde ve kargo yok), %15 payla 107.569,14. Kalem kalem köprü `maliyet.json` üzerinden §7'de.

### 2.2 v4 (03.11) → 158 bugün

| Değişiklik | Satır | Etki |
|---|---|---|
| Eklenen: K4 kabloları (6) + F1b 90° micro USB ve DC jak (2); 90° HDMI v4'te zaten var | 8 | +491,34 TL (2 satır fiyatsız) |
| Çıkan | 0 | — |
| Satıcı değişen: tırtıllı somun M5 Robotistan (tükendi) → CNC Marketi | 1 | 297,20 → 31,68 TL |
| Model değişen: 625ZZ Rulmanal sayfası artık 'BGR (Karbon)', KWC değil | 1 | 29,67 → 30,04 |
| Fiyat değişen (onaylı satıcı, aynı ürün) | 24 | Robotistan satırları %0,1–0,3 yukarı; P6KE6V8A 9,07 → 6,05; site satırları toplamı 68.219,82 → 67.995,98 (M5 somun dahil) |
| Stok düşen: QLED 4 → 2, motor 32 → 25, arazi tekerleği → 7, motor tutucu → 5 paket, kamera 0 | 5 | §3 |

## 3. Kritik yol ve erken alım kalemleri: stok ve kargo

Kritik yol (`proje-plani.md`): 1 → max(2, 2a lazer) → 5 → 6 → 7 → … ; akü dalı 2b. S = 16.11 yalnız erken kupon alımıyla tutuyor. Kargo süresi: sayfadaki 'kargoya veriliş' yazısı; taşıma süresi sayfalarda yok (**varsayım: 1–3 iş günü**).

| Adım | Kalem | Adet | Satıcı · fiyat · stok | Kargoya veriliş (sayfa) | İkinci satıcı |
|---|---|---|---|---|---|
| kupon + erken alım (kritik yol 1) | Rulman 6808-2RS, 40×52×7 mm | 4 | [Rulmanal](https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman) · 108,16 · stok 51 | 'Aynı Gün Kargo Saat 16:00'a kadar olan siparişler'; 2.500 TL üzeri ücretsiz; ücret sayfada yok | [Rulmanal](https://www.rulmanal.com.tr/urun/6808-2rs-nsk-40x52x7-rulman) · 1.061,02 · stok 5 |
| kupon + erken alım (kritik yol 1) | Rulman 625ZZ, 5×16×5 mm | 5 | [Rulmanal](https://www.rulmanal.com.tr/urun/625-zz-kwc-5-16-5-rulman) · 30,04 · stok 8398 | 'Aynı Gün Kargo Saat 16:00'a kadar olan siparişler'; 2.500 TL üzeri ücretsiz; ücret sayfada yok | yok |
| kupon + erken alım (kritik yol 1) | Isıl gömme somun M3, pirinç, delik Ø4,0, boy 5,7 mm | 176 | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3) · 5,29 · stokta (adet yok) | 'saat 16:00 ve öncesi ise siparişiniz aynı gün kargoya verilir', sonrası stoktaysa ertesi iş günü; 'Yurtiçi Kargo 139TL', 2.500 TL üzeri ücretsiz | yok |
| kupon + erken alım (kritik yol 1) | Isıl gömme somun M5, pirinç | 6 | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5) · 6,35 · stokta (adet yok) | 'saat 16:00 ve öncesi ise siparişiniz aynı gün kargoya verilir', sonrası stoktaysa ertesi iş günü; 'Yurtiçi Kargo 139TL', 2.500 TL üzeri ücretsiz | yok |
| kupon D (erken alım) | İmbus cıvata DIN 912 A2 M3×20 | 5 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) · 1,30 · ürün stoğu 77.199 (boy ayrımı yok) | 'Stoktan teslim 15:00'e kadar aynı gün kargo'; 2.000 TL üzeri ücretsiz; ücret sayfada yok | yok |
| kupon D (erken alım) | Düz pul DIN 125 A2 M3 | 36 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125) · 0,40 · stok görünmedi | 'Stoktan teslim 15:00'e kadar aynı gün kargo'; 2.000 TL üzeri ücretsiz; ücret sayfada yok | [Robotistan](https://www.robotistan.com/m3-pul-50-adet) · 1,03 · stok 469 |
| kupon D (erken alım) | Fiberli somun DIN 985 A2 M3 | 10 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-fiberli-somun-cesitleri-din985) · 1,02 · stok görünmedi | 'Stoktan teslim 15:00'e kadar aynı gün kargo'; 2.000 TL üzeri ücretsiz; ücret sayfada yok | [Robotistan](https://www.robotistan.com/m3-fiberli-somun-10-adet) · 2,61 · stok 686 |
| 2 tahrik (kritik yol) | Enkoderli DC motor | 4 | [Direnc.net](https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor) · 665,41 · stok 25 | 'Saat 15:00'e kadar ... aynı gün kargoda'; 1.500 TL üzeri ücretsiz | İkinci onaylı satıcı yok: Robotistan'da JGB37-520 yalnız 1000 dev/dk |
| 2 tahrik (kritik yol) | Motor montaj braketi (4 adet = 2 paket) | 2 | [Robotistan](https://www.robotistan.com/aluminyum-l-tipi-37d-motor-tutucu) · 764,79 · stok 5 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Motorobit](https://www.motorobit.com/37-mm-motor-tutucu) · 107,10 · tükendi |
| 2 tahrik (kritik yol) | Altıgen kaplin (6 mm mil → 12 mm) | 4 | [Motorobit](https://www.motorobit.com/6mm-motor-safti-ile-uyumlu-hex-tekerlek-kaplini) · 122,40 · stok 384 | 'Saat 15.00'a kadar verilen siparişler aynı gün kargoda'; 2.500 TL üzeri ücretsiz (MNG-DHL) | [Robotistan](https://www.robotistan.com/robot-araba-tekerlek-altigen-kaplin-6mm-30mm) · 79,89 · stok 294 |
| 2 tahrik (kritik yol) | Arazi tekerleği | 4 | [Robotistan](https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi) · 362,27 · stok 7 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Motorobit](https://www.motorobit.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi) · 612,00 · stok 22 |
| 5 taban (kritik yol) | Sigma profil 40×40 ağır tip, kanal 10, ölçüye kesim: 1.115,5 | 3 | [CNC Marketi](https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip) · 934,08 · stok 120,9 | 'Stoktan hızlı gönderim'; 'Kargo 132,00 TL (KDV dahil)', 2.400 TL üzeri ücretsiz | [Otomasyoncu](https://www.otomasyoncu.net/urun/sigma-profil-40x40-agir-kanal-10) · 1.097,46 · stok görünmedi |
| 5 taban (kritik yol) | Tırtıllı (T) somun M6, kanal 10 | 62 | [CNC Marketi](https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu-m6) · 3,90 · stok 36790 | 'Stoktan hızlı gönderim'; 'Kargo 132,00 TL (KDV dahil)', 2.400 TL üzeri ücretsiz | yok |
| 5 taban (kritik yol) | Gizli iç köşe bağlantı, 40×40 kanal 10, set vidalı | 8 | [CNC Marketi](https://www.cnc-marketi.com/urun/45x45-gizli-kose-baglanti-90-k10) · 39,60 · stok 989 | 'Stoktan hızlı gönderim'; 'Kargo 132,00 TL (KDV dahil)', 2.400 TL üzeri ücretsiz | yok |
| 5 taban (kritik yol) | Geniş köşe bağlantı, 40×40 kanal 10 | 4 | [Otomasyoncu](https://www.otomasyoncu.net/urun/40x40-kose-baglanti-genis) · 31,36 · stok görünmedi | Kargo ve stok sayfada yok (fiyat '0,52 USD + KDV') | [CNC Marketi](https://www.cnc-marketi.com/urun/genis-kose-baglanti-40x40-k10) · 25,38 · tükendi |
| 5 taban (kritik yol) | Tırtıllı (T) somun M5, kanal 10 | 8 | [CNC Marketi](https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu10-kanal-profil-tirtilli-somunu) · 3,96 · stok 42761 | 'Stoktan hızlı gönderim'; 'Kargo 132,00 TL (KDV dahil)', 2.400 TL üzeri ücretsiz | [Robotistan](https://www.robotistan.com/40-serisi-m5-t-somun) · 37,20 · tükendi (v4 birincili) |
| 5 taban (kritik yol) | İmbus cıvata DIN 912 M6×16, fosfat | 18 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912) · 3,89 · ürün stoğu 322.514 (boy ayrımı yok) | 'Stoktan teslim 15:00'e kadar aynı gün kargo'; 2.000 TL üzeri ücretsiz; ücret sayfada yok | [CNC Marketi](https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata) · 3,60 · stok 2 |
| 2a lazer (kritik yol) | Alüminyum lazer + abkant: gövde U braketi 3 mm × 8, etek taş | 14 | teklif yok (tahmini 60,00) | teklif bekleniyor | yok |
| 2a lazer (kritik yol) | Alüminyum lazer kesim: alt plaka 346×500×3 mm Al 5754 + boyu | 1 | teklif yok (tahmini 1.500,00) | teklif bekleniyor | yok |
| 2a lazer (kritik yol) | Kontrplak lazer kesim: 5 mm huş, 270×226 mm + 270×274 mm | 1 | teklif yok (tahmini 500,00) | teklif bekleniyor | yok |
| 2b akü (kritik yol dalı) | Akü 12,8 V LiFePO4 20 Ah | 1 | [Atakale](https://atakale.com/index.php?product_id=438&route=product%2Fproduct) · 12.680,70 · stok 1 | 'Ürün sipariş edildiğinde sizin için 7 gün içinde üreticiden/ithalatçıdan tedarik edilerek özel sipariş olarak gönderilecektir'; koli kargo mesafeye göre 1/2/3/5 gün | [Geçersun Enerji](https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya) · 4.814,86 · stokta (adet yok) |
| 6 elektrik (kritik yol) | Motor sürücü (2 + 1 yedek) | 3 | [Robotistan](https://www.robotistan.com/bts7960b-20-amper-motor-surucu-karti) · 265,30 · stok 140 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Robocombo](https://robocombo.com/bts7960b-dc-43a-cift-motor-surucu-2867) · 271,50 · stok 1 |
| plan: stoksuz kritik (ön şarj rölesi K2) | Ön şarj rölesi K2 | 1 | [Direnc.net](https://www.direnc.net/12v-minyonpot-qianji-role--jqc-3ff-12vdc-10a) · 19,36 · stokta (adet yok) | 'Saat 15:00'e kadar ... aynı gün kargoda'; 1.500 TL üzeri ücretsiz | [Motorobit](https://www.motorobit.com/jqc-3ff-m-12v-15a-role-5-pin) · 30,60 · stok 42 |
| plan: stoksuz kritik (optokuplör) | Optokuplör modülü | 1 | [Robotistan](https://www.robotistan.com/pc817-2-kanal-optokuplor-izolasyon-modulu) · 74,10 · stok 33 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Motorobit](https://www.motorobit.com/pc817-2-kanal-optokuplor-izolasyon-modulu) · 76,50 · tükendi |
| plan: stoksuz kritik (kart burcu) | Kart burcu (M3×8) | 48 | [Robotistan](https://www.robotistan.com/8mm-m3-disidisi-plastik-aralayici) · 1,83 · stok 2457 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Motorobit](https://www.motorobit.com/m3-10mm-plastik-disi-disi-aralayici-standoff) · 1,84 · stok 4771 |
| plan: stoksuz kritik (mesafe burcu) | Mesafe burcu M5×40, dişi-dişi (yoksa M5 uzatma somunu) | 8 | bulunamadı | — | yok |
| Parti 2 servo | Omuz servosu DS3235 (4 + 1 yedek) | 5 | [Robocombo](https://robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4534) · 1.809,00 · stok 85 | '15:00'e kadar verilen siparişler aynı gün kargoda'; 2.000 TL üzeri ücretsiz, altı 150 TL | [Motorobit](https://www.motorobit.com/rds3235-35kg-dijital-servo-motor-180-u-servo-braket-dahil) · 2.631,60 · stok 46 |
| Parti 2 servo | Dirsek, bilek, kafa servosu (6 + 2 yedek) | 8 | [Robocombo](https://robocombo.com/tower-pro-mg996r-metal-disli-dijital-servo-motor-180-derece) · 202,50 · stok 393 | '15:00'e kadar verilen siparişler aynı gün kargoda'; 2.000 TL üzeri ücretsiz, altı 150 TL | [Robotistan](https://www.robotistan.com/mg996-13-kg-servo-motor) · 236,63 · stok 524 |
| Parti 2 servo kolu | Servo horn 25T | 10 | [Motorobit](https://www.motorobit.com/25t-servo-motor-kolu-gri) · 76,50 · stok 184 | 'Saat 15.00'a kadar verilen siparişler aynı gün kargoda'; 2.500 TL üzeri ücretsiz (MNG-DHL) | [Robiz](https://robiz.net/servoarm25t) · 83,16 · stokta (adet yok) |
| Parti 3 kafa ekranı | Kafa ekranı 10,1" QLED | 1 | [Robotistan](https://www.robotistan.com/101-inc-qled-ekran-modulu) · 7.217,95 · stok 2 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Motorobit](https://www.motorobit.com/waveshare-101-1280720-qled-kapasitif-dokunmatik-hdmi-ekran) · 15.300,00 · stok 10 |
| Parti 3 göğüs ekranı | Göğüs ekranı 11,6" 1080p (gömülü) | 1 | [Robotistan](https://www.robotistan.com/116-inc-lcd-ekran-modulu) · 9.367,79 · stok 10 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo | [Direnc.net](https://www.direnc.net/116inch-hdmi-lcd-ekran-raspberry-pi-uyumlu-1920x1080-ips-teknik-ozellikleri) · 12.695,09 · stok 4 |

Notlar: insert, rulman, vida, sigma profil ve T-somun satıcılarının hiçbiri onaylı listede değil; bunlar onaylı sitelerde bulunamayan (a) satırları. Kargo ücreti ve eşikleri §8. Lazer ve bükme için teklif yok (DXF ile alınacak). M6×16: CNC'de 2 adet, gereken 18; tutar paslanmaz ikinci satıcıyla (taban fiyat; 'Stoktan teslim 15:00'e kadar aynı gün kargo'); CNC'den tek kargo istenirse bombe başlı 4,80 (stok 235, baş şekli CAD'le kontrol edilmedi).

### 3.1 Akü takvimi

Taban + iskelet (aşama 5) S+1 → S+2 = 23–29.11; akü adım 9'da, ≈ S+1,5 = **25–26.11** (`proje-plani.md` aşama 5, 2b). Taşıma süresi sayfalarda yok: Limacell için **varsayım 1–3 iş günü**; Atakale için sayfadaki koli süresi 1–5 gün (mesafeye göre).

| Seçenek | Sipariş | Kargoya veriliş (sayfa) | Varış | Adım 9'a (≈ 25–26.11) | Not |
|---|---|---|---|---|---|
| Atakale Victron 20 Ah, S'de | 16.11 | ≤ 23.11 ('7 gün içinde … tedarik') | ≈ 24–28.11 | **Sınırda / geç** (0–3 gün bekleme) | Onaylı satıcı, stok 1, 12.680,70 |
| Atakale Victron 20 Ah, erken alımla | 10–12.11 | ≤ 17–19.11 | ≈ 18–24.11 | Yetişir | Stok 1: o güne kadar satılmazsa |
| Limacell 12 V 24 Ah, S'de | 16.11 | ≈ 19.11 ('ortalama hazırlanma süresi 3 iş günü') | ≈ 20–24.11 (varsayım) | Yetişir | Onaylı değil; 4.814,86 (havale 4.622,27); 3.000 TL üzeri kargo ücretsiz |
| Limacell, bu hafta | 09–12.11 | Sayfa: 09.11 siparişi 'en geç 12 Kasım 2026 Perşembe günü kargoda' | ≈ 13–17.11 (varsayım) | Yetişir | Aynı |

Limacell sayfası: 12,8 V, 307 Wh; 'Max. Sürekli Deşarj Akımı 30 A', anlık 45 A; 6 ay garanti; özel üretim olduğu için iade yok. **Ölçü ve kütle sayfada yok, CAD akü yuvasıyla kontrol edilmedi**; 30 A sürekli sınırının motor tepe akımı ve ana sigortayla uyumu doğrulanmadı. Seçim Ahmet'in (§9 madde 4).

## 4. Erken alım listesi (P9.1, ≈ 1.496 TL)

| Kalem | Adet | Satıcı | Plan fiyatı (tutar) | Bugün birim | Bugün tutar | Stok | Not |
|---|---|---|---|---|---|---|---|
| Rulman 6808-2RS | 4 | [Rulmanal](https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman) | 427,20 | 108,16 | 432,64 | stok 51 | İkinci aynı satıcı NSK |
| Rulman 625ZZ | 5 | [Rulmanal](https://www.rulmanal.com.tr/urun/625-zz-kwc-5-16-5-rulman) | 148,35 | 30,04 | 150,20 | stok 8398 | Sayfa adı artık '625 ZZ BGR 5x16x5 (Karbon)': marka değişti. Motorobit 625ZZ 'plastik kaplı', muadil değil |
| Isıl gömme somun M3 | 168 | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3) | 876,96 | 5,29 | 888,72 | stokta (adet yok) | Sayfada L 5,7 varyantı yok (ID3 OD4 L4; ID3 OD5 L4–8); CAD deliği Ø4,0 / L 5,7 ile uyum doğrulanmadı. Fiyat taban (varyant seçilmeden). Seçenekler sipariş §4.1. Direnc 'İnsert Somun M3' 12,70 tükendi (dış çap 6 mm) |
| Isıl gömme somun M5 | 6 | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5) | 37,62 | 6,35 | 38,10 | stokta (adet yok) | Varyantlı ürün |
| Kupon D: 2 × M3×20 DIN 912 + 4 × pul M3 + 2 × DIN 985 M3 | 8 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) | 6,24 | taban fiyat | 6,24 | vida: ürün stoğu 77.199; pul ve somun: görünmedi | Boy seçilmeden taban fiyat |
| **Toplam** | | | **1.496,37** | | **1.515,90** | | Fark +19,53 TL |
| Kargo: Rhino3DPrinter (926,82 < 2.500) | | | | | +139,00 | | Rulmanal (582,84 < 2.500) ve paslanmazcivata.ist (< 2.000) eşik altı, ücret sayfada yok |
| **Toplam, bilinen kargoyla** | | | | | **1.654,90** | | |

- **Hâlâ geçerli, küçük farkla:** 1.515,90 TL (+19,53), Rhino kargosuyla 1.654,90. Rulman (Rulmanal stok 51 / 8.398) ve insert (Rhino, stokta) stokta; M3 vida sayfası ürün stoğu 77.199 (boy ayrımı yok); pul ve fiberli somun sayfalarında stok görünmedi.
- Isıl gömme M3 adedi: plan ve `maliyet.json` 168, v4 176. Öneri: plan takvimine göre **168 bu hafta** alınsın (erken alım H7'de: `proje-plani.md:71, 119`); 176 ile fark 8 adet P4.3 BOM'uyla netleşir ve S siparişine eklenir (+42,32; 176 bugün alınırsa 1.558,22 TL).
- 625ZZ: Rulmanal sayfasının adı artık '625 ZZ BGR 5x16x5 (Karbon)'; plandaki KWC marka değil. Ölçü aynı.
- Insert: Sayfada L 5,7 varyantı yok (ID3 OD4 L4; ID3 OD5 L4–8); CAD deliği Ø4,0 / L 5,7 ile uyum doğrulanmadı. Fiyat taban 5,29; varyant fiyatı sepete eklemeden görünmedi. Seçenekler §4.1.
- Vida fiyatları boy seçilmeden taban fiyat; sayfada adet kademesi var (21 adet üstü %10, 51 üstü %15, 101 üstü %20 indirim), toplamlar taban fiyatla, yani üst sınır.
- Üç satıcı da onaylı listede değil.

### 4.1 M3 insert: CAD'deki 5,7 mm boy için seçenekler (karar Ahmet'in)

CAD: `arayuz.INSERT` boy 5,7; kupon delikleri Ø3,8 / 3,9 / 4,0 / 4,1, derinlik 6,2 (`tasarim/freecad/test/tolerans_kuponu.py`, salt okundu). Rhino sayfasının kuralı: delik M3 insert dış çapından 0,1–0,2 mm, M5'te 0,2–0,3 mm dar.

| Seçenek | Ürün · satıcı | Uygun delik | Boy | Etki |
|---|---|---|---|---|
| A | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3) ID3 OD4 L4 · taban 5,29, varyant fiyatı görünmedi · stokta | Ø3,8–3,9 (kural); kupondaki Ø3,8 ve 3,9 delikleri bunu dener | 4 (CAD 5,7) | Kupon değişmez, erken alım bu hafta yapılabilir. Diş boyu 1,7 mm kısa: CAD boyu P4.3'te 4'e çekilir |
| B | Rhino3DPrinter ID3 OD5 L6 · taban 5,29, varyant fiyatı görünmedi · stokta | Ø4,8–4,9 (kural); kupon delikleri (Ø3,8–4,1) uymaz | 6 (≈ 5,7) | Kupon ve CAD deliği büyütülmeli (FreeCAD işi, F8a dışında); kupon basımı gecikir |
| C | ruthex RX-M3x5.7 (dış çap 4,6; üretici önerisi delik 4,0–4,2) | CAD Ø4,0 ile uyumlu | 5,7 | Türkiye'de satıcı bulunamadı (3 WebSearch); yalnız yurt dışı satıcılar (3DJAKE, galaxus, 3dprima). Fiyat, teslim süresi ve gümrük doğrulanmadı; erken alım takvimine (11–12.11) yetişmesi beklenmez |

Direnc 'İnsert Somun M3' 12,70 tükendi ve dış çapı 6 mm (uymaz); Rhino'nun RhinoLab 'İnsert Somun M3' 4,23 tükendi. M5: CAD delikleri Ø6,2 / 6,4 / 6,6, derinlik 7,5; Rhino'da ID5 OD7 L7 var, kurala göre delik Ø6,7–6,8 (kupondakilerden büyük); M5 için de aynı karar gerekir.

## 5. Kalem tablosu

Durum: **doğrulandı** = fiyat ve stok bugün sayfada görüldü; **kısmen** = ürünün taban fiyatı görüldü, boy/varyant fiyatı görülmedi; **doğrulanmadı** = bugün fiyat görülmedi, tutar v4 (03.11) yaklaşık fiyatı; **karara bağlı** = açık karar. 'Tutar' sütunu, birincil stokta değilse ikinci satıcının fiyatıyla hesaplandı (işaretli).

### 5.1 Onaylı sitelerden (v4 satırları)

**Atakale** (1 satır, 12.680,70 TL)

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| S5 | Akü 12,8 V LiFePO4 20 Ah: Victron Energy 12.8V 20AH LifePo4 Superpack 256Wh BAT512020705 | 1 | [Atakale](https://atakale.com/index.php?product_id=438&route=product%2Fproduct) · 12.680,70 · stok 1 | 12.680,70 | [Geçersun Enerji](https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya) · 4.814,86 · stokta (adet yok) · Planın akü yedeği (onaylı değil): Limacell 12 V 24 Ah, 307 Wh; sayfa: 'özel üretim, ortalama hazırlanma süresi 3 iş günü', 'en geç 12 Kasım 2026 Perşembe günü kargoda' (09.11 siparişi için), 3.000 TL üzeri kargo ücretsiz; sürekli 30 A, anlık 45 A; ölçü ve kütle sayfada yok, CAD yuvasıyla kontrol edilmedi. Onaylı 4 sitede LiFePO4 paket yok; Hepsiburada Victron 403 (doğrulanmadı) | doğrulandı |

**Direnç.net** (9 satır, 3.274,26 TL)

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| S8 | Delikli pertinaks: 6x13 Delikli Plaket | 5 | [Direnc.net](https://www.direnc.net/6x13-delikli-plaket) · 24,20 · stok 1695 | 121,00 | [Motorobit](https://www.motorobit.com/5x7cm-epoxy-cift-tarafli-delikli-plaket) · 31,82 · stok 392 · 5×7 cm epoksi (70×50 hedefi tam karşılar) | doğrulandı |
| S9 | Enkoderli DC motor: JGB37-520 - 12V 60RPM Enkoderli Motor | 4 | [Direnc.net](https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor) · 665,41 · stok 25 | 2.661,64 | — · İkinci onaylı satıcı yok: Robotistan'da JGB37-520 yalnız 1000 dev/dk | doğrulandı |
| S10 | Kablo bağı: 2.5mm x 100mm Kablo Bağı (100 Adet) Siyah | 1 | [Direnc.net](https://www.direnc.net/25mm-x-100mm-kablo-bagi-100-adet-siyah) · 27,95 · stokta (adet yok) | 27,95 | [Robotistan](https://www.robotistan.com/36mm-genislik-15cm-uzunluk-kablo-bagi-beyaz-100-adet) · 49,40 · stok 51 · 3,6 × 150 mm beyaz | doğrulandı |
| S11 | Kamera kablosu (Pi 5, 300 mm): Raspberry Pi 5 Kamera FPC Kablosu - 300mm | 1 | [Direnc.net](https://www.direnc.net/raspberry-pi-5-kamera-fpc-kablosu-300mm) · 175,43 · stokta (adet yok) | 175,43 | [Robotistan](https://www.robotistan.com/raspberry-pi-kamera-kablosu-standard-mini-500mm) · 231,15 · stok 298 · Pi 5 tipi (standart-mini) 500 mm; 300 mm Robotistan'da yok | doğrulandı |
| S12 | M2,5 distans: YP-600 6mm Plastik Distans - M2.5 - 20 Adet | 1 | [Direnc.net](https://www.direnc.net/yp-600-6mm-plastik-distans-m25-vidaya-uygun-20-adet) · 65,33 · stokta (adet yok) | 65,33 | — · Onaylı diğer sitelerde M2,5 plastik distans bulunamadı | doğrulandı |
| S13 | Ön şarj direnci: 5.6R 11W Taş Direnç | 1 | [Direnc.net](https://www.direnc.net/022r-11w-tas-direnc-11664) · 9,98 · stok 4 | 9,98 | — · Diğer sitelerde 5,6 Ω yok (Robotistan'da 5 W taş direnç, 4,7/10 Ω) | doğrulandı |
| S14 | Ön şarj rölesi K2: 12V Minyonpot Qianji Röle JQC-3FF-12VDC 10A | 1 | [Direnc.net](https://www.direnc.net/12v-minyonpot-qianji-role--jqc-3ff-12vdc-10a) · 19,36 · stokta (adet yok) | 19,36 | [Motorobit](https://www.motorobit.com/jqc-3ff-m-12v-15a-role-5-pin) · 30,60 · stok 42 · JQC-3FF-M 15 A, 5 pin: ayak düzeni kartla kontrol edilmeli | doğrulandı |
| S15 | TVS diyot (kafa 5 V): P6KE6V8A Transil Diyot | 2 | [Direnc.net](https://www.direnc.net/p6ke6v8a) · 6,05 · stok 1210 | 12,10 | [Motorobit](https://www.motorobit.com/p6ke6v8a-transil-diyot) · 16,52 · stok 10000 | doğrulandı |
| S16 | Ultrasonik mesafe sensörü: HC-SR04 Arduino Ultrasonik Mesafe Sensörü | 3 | [Direnc.net](https://www.direnc.net/arduino-ultrasonic-sensor-hc-sr04) · 60,49 · stok 805 | 181,47 | [Robotistan](https://www.robotistan.com/hc-sr04-ultrasonik-mesafe-sensoru) · 64,04 · stok 464 | doğrulandı |

**Motorobit** (31 satır, 4.593,56 TL)

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| S19 | Acil stop butonu: NP2 BE102 NC Metal Acil Stop Butonu | 1 | [Motorobit](https://www.motorobit.com/np2-be102-nc-metal-acil-stop-butonu) · 306,00 · stok 28 | 306,00 | [Direnc.net](https://www.direnc.net/drn956-16mm-acil-stop-dugmesi-kafa-27mm) · 217,77 · stok görünmedi · Zayıf muadil: 16 mm delik, kafa 27 mm | doğrulandı |
| S20 | Altıgen kaplin (6 mm mil → 12 mm): 6mm Motor Şaftı ile Uyumlu Hex Tekerlek Kaplini | 4 | [Motorobit](https://www.motorobit.com/6mm-motor-safti-ile-uyumlu-hex-tekerlek-kaplini) · 122,40 · stok 384 | 489,60 | [Robotistan](https://www.robotistan.com/robot-araba-tekerlek-altigen-kaplin-6mm-30mm) · 79,89 · stok 294 · Tekerleğin 12 mm altıgen göbeğine uyumu sayfada yok | doğrulandı |
| S21 | Ana güç anahtarı: ASW-A01 100A ON-OFF Battery Disconnect Switch | 1 | [Motorobit](https://www.motorobit.com/asw-a01-100a-on-off-battery-disconnect-switch) · 281,52 · stok 92 | 281,52 | — · Onaylı diğer sitelerde 100 A akü ayırıcı bulunamadı | doğrulandı |
| S22 | Ana sigorta 30 A: 30 Amper Oto Sigorta - Bıçak Sigorta | 2 | [Motorobit](https://www.motorobit.com/30a-maksi-oto-sigorta-bicak-sigorta) · 4,28 · stok 743 | 8,56 | — · Onaylı diğer sitelerde 30 A bıçak sigorta bulunamadı | doğrulandı |
| S23 | Cırt kayış (akü bağı): Lipo Pil Tutucu Cırt Bant 20x400mm - Siyah | 4 | [Motorobit](https://www.motorobit.com/lipo-pil-tutucu-cirt-bant-20x400mm-siyah) · 52,02 · stok 742 | 208,08 | [Robotistan](https://www.robotistan.com/cirt-bant-seti-30-cm-x-2-cm5-adet) · 153,69 · stok 60 · 5 × 300 mm set (400 mm değil) | doğrulandı |
| S24 | Diyot 1N4007: 1N4007 - 1000V 1A Diyot | 2 | [Motorobit](https://www.motorobit.com/1n4007-1000v-1a-diyot) · 0,61 · stok 23592 | 1,22 | [Direnc.net](https://www.direnc.net/1n4007-diyot-mic) · 0,73 · stok 4092 | doğrulandı |
| S25 | Diyot 1N5819: 1N5819 - 1A 40V Diyot | 1 | [Motorobit](https://www.motorobit.com/1n5819-1a-40v-diyot) · 1,22 · stok 9697 | 1,22 | [Direnc.net](https://www.direnc.net/1n5819-1a-40v-schottky-rectifier-mic) · 1,57 · stok görünmedi | doğrulandı |
| S26 | Erkek pin header 1×40: 1x40 Erkek Header 40 Pin 2.54mm 180 Derece - Beyaz | 2 | [Motorobit](https://www.motorobit.com/1x40-erkek-header-40-pin-254mm-180-derece-beyaz) · 4,28 · stok 472 | 8,56 | — · Diğer sitelerde 1×40 erkek header bakılmadı | doğrulandı |
| S27 | Hat sigortası yuvası: Su Geçirmez Mini/Micro Bıçak Sigorta Yuvası - 16AWG | 5 | [Motorobit](https://www.motorobit.com/su-gecirmez-minimicro-bicak-sigorta-yuvasi-16awg) · 36,72 · stok 742 | 183,60 | [Robotistan](https://www.robotistan.com/kablolu-bicak-sigorta-yuvasi-mini-boy) · 29,27 · stok 73 · Mini boy, su geçirmez olduğu yazmıyor | doğrulandı |
| S28 | HDMI açılı adaptör (göğüs ekranı ucu): HDMI Dişi Erkek Çevirici Konnektör - 90 Derece | 1 | [Motorobit](https://www.motorobit.com/hdmi-disi-erkek-cevirici-konnektor-90-derece) · 45,90 · stok 104 | 45,90 | [Direnc.net](https://www.direnc.net/hdmi-disi-erkek-cevirici-90-derece-dirsek) · 87,71 · tükendi · Tükendi | doğrulandı |
| S29 | Hızlı klemens (10 adet): 2273-203 3 Pin Buat Klemensi (Wago) | 10 | [Motorobit](https://www.motorobit.com/2273-203-3-pin-buat-klemensi) · 12,24 · stok 18 | 122,40 | — · Onaylı diğer sitelerde Wago 2273 bulunamadı | doğrulandı |
| S30 | Hoparlör: Speaker 4 ohm 3W 40mm | 1 | [Motorobit](https://www.motorobit.com/speaker-4-ohm-3w-40mm) · 107,10 · stok 1680 | 107,10 | — · Onaylı diğer sitelerde 4 Ω 3 W 40 mm yok (Motorobit 8 Ω 0,5 W var, yetmez) | doğrulandı |
| S31 | Kafa ekranı 5 V düşürücü: SY8205 7-30V'tan 5V'a 5A Voltaj Düşürücü - Servo Sürücü Güç Kartı | 1 | [Motorobit](https://www.motorobit.com/sy8205-7-30vtan-5va-5a-voltaj-dusurucu-servo-surucu-guc-karti) · 146,88 · stok 81 | 146,88 | [Motorobit](https://www.motorobit.com/hcw-p715-9-36vtan-5va-5a-voltaj-dusurucu-regulator-karti) · 168,30 · stok 52 · Muadil HCW-P715 9–36 V → 5 V 5 A | doğrulandı |
| S32 | Kablo bağı tabanı (10 paket = 100 adet): IYPK-30X30 28x28mm Yapışkanlı Kroşe - 10 Adet | 10 | [Motorobit](https://www.motorobit.com/iypk-30x30-10-adet-yapiskanli-kroseler) · 31,82 · stok 1000 | 318,20 | — · Robotistan 28×28 yapışkan köşe 100'lü tükendi | doğrulandı |
| S33 | Kondansatör 2200 µF 16 V: 2200uF 16V Electrolytic Capacitor 10x20mm | 4 | [Motorobit](https://www.motorobit.com/2200uf-16v-electrolytic-capacitor-10x20mm) · 4,28 · stok 1575 | 17,12 | [Robotistan](https://www.robotistan.com/2200uf-16v-elektrolit-kondansator) · 6,83 · stok 182 | doğrulandı |
| S34 | Makaron seti: 328 Parça Renkli Makaron Seti | 1 | [Motorobit](https://www.motorobit.com/328-parca-renkli-makaron-seti) · 116,28 · stok 49 | 116,28 | [Robotistan](https://www.robotistan.com/328-adet-renkli-makaron) · 125,03 · tükendi | doğrulandı |
| S35 | Mini bıçak sigorta 2 A: 2A Mini Alçak Profil Oto Sigorta - Bıçak Sigorta | 1 | [Motorobit](https://www.motorobit.com/2a-mikro-oto-sigorta-bicak-sigorta) · 7,34 · stok 381 | 7,34 | — · Mini alçak profil sigorta başka onaylı sitede bulunamadı | doğrulandı |
| S36 | Mini bıçak sigorta 5 A: 5A Mini Alçak Profil Oto Sigorta | 1 | [Motorobit](https://www.motorobit.com/5a-mikro-oto-sigorta-bicak-sigorta) · 7,34 · stok 154 | 7,34 | — · Aynı | doğrulandı |
| S37 | Mini bıçak sigorta 7,5 A: 7.5A Mini Alçak Profil Oto Sigorta | 2 | [Motorobit](https://www.motorobit.com/75a-mikro-oto-sigorta-bicak-sigorta) · 7,34 · stok 571 | 14,68 | — · Aynı | doğrulandı |
| S38 | Mini bıçak sigorta 10 A: 10A Mini Alçak Profil Oto Sigorta | 1 | [Motorobit](https://www.motorobit.com/10a-mikro-oto-sigorta-bicak-sigorta) · 7,34 · stok 913 | 7,34 | — · Aynı | doğrulandı |
| S39 | Röle K1: MAH-112-C-4 12V 30/40A Otomotiv Rölesi 5-Pin | 1 | [Motorobit](https://www.motorobit.com/mah-112-c-4-12v-30/40a-otomotiv-rolesi-5-pin) · 183,60 · stok 94 | 183,60 | [Kartal Otomasyon](https://www.kartalotomasyon.com.tr/urun/12v-40a-mikro-role-5-fisli) · 56,70 · stok görünmedi · Onaylı değil; 12 V 40 A mikro röle 5 fişli | doğrulandı |
| S40 | Servo horn 25T: 25T Servo Motor Kolu - Gri | 10 | [Motorobit](https://www.motorobit.com/25t-servo-motor-kolu-gri) · 76,50 · stok 184 | 765,00 | [Robiz](https://robiz.net/servoarm25t) · 83,16 · stokta (adet yok) · Onaylı değil (Robiz); 25T metal kol | doğrulandı |
| S41 | Sigorta kutusu (6 yollu, sigortalar dahil): 6 Channel Auto Blade Fuse Box | 1 | [Motorobit](https://www.motorobit.com/6-channel-auto-blade-fuse-box) · 315,18 · stok 117 | 315,18 | — · Onaylı diğer sitelerde 6 yollu sigorta kutusu bulunamadı | doğrulandı |
| S42 | Silikon kablo 18 AWG kırmızı (m): 18 AWG Silicone Cable Red - 1 Meter | 7 | [Motorobit](https://www.motorobit.com/18-awg-silicone-cable-red-1-meter) · 42,84 · stok 1277 | 299,88 | [Robotistan](https://www.robotistan.com/18-awg-1-metre-siyah-ve-kirmizi-silikon-kablo) · 58,55 · tükendi · Tükendi | doğrulandı |
| S43 | Silikon kablo 18 AWG siyah (m): 18 AWG Silicone Cable Black - 1 Meter | 7 | [Motorobit](https://www.motorobit.com/18-awg-silicone-cable-black-1-meter) · 42,84 · stok 1277 | 299,88 | [Robotistan](https://www.robotistan.com/18-awg-1-metre-siyah-ve-kirmizi-silikon-kablo) · 58,55 · tükendi · Tükendi | doğrulandı |
| S44 | Standart bıçak sigorta 2 A: 2 Amper Oto Sigorta - Bıçak Sigorta | 1 | [Motorobit](https://www.motorobit.com/2a-maksi-oto-sigorta-bicak-sigorta) · 4,28 · stok 445 | 4,28 | — · Bakılmadı (Motorobit'te 2 A/5 A standart bıçak var) | doğrulandı |
| S45 | Standart bıçak sigorta 5 A: 5 Amper Oto Sigorta - Bıçak Sigorta | 1 | [Motorobit](https://www.motorobit.com/5-amper-oto-sigorta-bicak-sigorta) · 4,28 · stok 1549 | 4,28 | — · Aynı | doğrulandı |
| S46 | TVS diyot (kafa 12 V): P6KE18A Transil Diyot | 1 | [Motorobit](https://www.motorobit.com/p6ke18a-transil-diyot) · 16,52 · stok 27 | 16,52 | — · Direnc/Robotistan'da P6KE18A bulunamadı | doğrulandı |
| S47 | USB ses kartı (amfi çıkışı): USB 7.1 Kanal Kulaklık + Mikrofon Ses Kartı | 1 | [Motorobit](https://www.motorobit.com/usb-71-kanal-kulaklik-mikrofon-ses-karti) · 91,80 · stok 42 | 91,80 | [Motorobit](https://www.motorobit.com/harici-ses-karti-cm108-hoparlor-mikrofon-girisi) · 367,20 · stok 28 · Aynı satıcı CM108 (PAKET A'daki kartın aynısı); başka onaylı sitede USB ses kartı bulunamadı | doğrulandı |
| S48 | USB-C güç ucu: USB Type-C Erkek 24-Pin Test Kartı | 1 | [Motorobit](https://www.motorobit.com/usb-type-c-erkek-24-pin-test-karti) · 153,00 · stok 96 | 153,00 | — · Onaylı diğer sitelerde bulunamadı | doğrulandı |
| S49 | XT60 panel konnektör (şarj girişi): XT60E-M Panel Tipi Erkek Konnektör - XT60 | 1 | [Motorobit](https://www.motorobit.com/xt60e-m-panel-tipi-erkek-konnektor-xt60) · 61,20 · stok 960 | 61,20 | [Direnc.net](https://www.direnc.net/xt60e-panel-montaj-disi-konnektor) · 51,42 · stok 188 · Yanlış cins (panel dişi); onaylı sitelerde başka panel erkek yok | doğrulandı |

**Robocombo** (16 satır, 14.596,50 TL)

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| S52 | Akü şarj cihazı: IMAX B6 Şarj Cihazı 80W Adaptörlü | 1 | [Robocombo](https://robocombo.com/imax-b6-sarj-cihazi-80w-adaptorlu-3245) · 1.809,00 · stok 245 | 1.809,00 | [Motorobit](https://www.motorobit.com/imax-b6ac-dahili-adaptorlu-lixx-nixx-pb-sarj-aleti) · 2.754,00 · stok 41 · B6AC dahili adaptörlü, 1,5× fiyat | doğrulandı |
| S53 | Alt kontrolcü: ESP32 Wi-fi + Bluetooth Geliştirme Kartı (30 pin, CP2102) | 1 | [Robocombo](https://robocombo.com/esp32-wi-fi-bluetooth-gelistirme-karti) · 289,50 · stok 438 | 289,50 | [Robotistan](https://www.robotistan.com/esp32-esp-32s-wifi-bluetooth-dual-mode-gelistirme-karti) · 396,42 · stok 959 | doğrulandı |
| S54 | DC-DC düşürücü (servo A, B, C + çevre 5 V): XL4016 8A DC-DC Step Down Voltaj Regülatörü | 4 | [Robocombo](https://robocombo.com/xl4016-8a-dc-dc-step-down-voltaj-regulatoru-2991) · 121,00 · stok 320 | 484,00 | [Motorobit](https://www.motorobit.com/xl4016-8a-dc-dc-step-down-voltaj-regulatoru) · 244,80 · stok 77 | doğrulandı |
| S55 | Direnç seti: 300 Parça 30 Çeşit Direnç Seti - 1/4W | 1 | [Robocombo](https://robocombo.com/300-parca-30-cesit-direnc-seti-14w-3923) · 90,50 · stok 644 | 90,50 | [Motorobit](https://www.motorobit.com/direnc-seti-30-cesit-20ser-adet-600-adet-14w) · 198,90 · stok 237 · 600 adet | doğrulandı |
| S56 | Dirsek, bilek, kafa servosu (6 + 2 yedek): Tower Pro MG996R Metal Dişli Dijital Servo Motor 180 Derece | 8 | [Robocombo](https://robocombo.com/tower-pro-mg996r-metal-disli-dijital-servo-motor-180-derece) · 202,50 · stok 393 | 1.620,00 | [Robotistan](https://www.robotistan.com/mg996-13-kg-servo-motor) · 236,63 · stok 524 | doğrulandı |
| S57 | Dişi pin header 40 pin: 40 pin Dişi Header (180 Derece) | 1 | [Robocombo](https://robocombo.com/40-pin-disi-header-180-derece) · 6,50 · stok 1587 | 6,50 | [Motorobit](https://www.motorobit.com/1x40-disi-header-40-pin-180-derece) · 6,73 · stok 33 | doğrulandı |
| S58 | ESP32 – Pi ve göğüs dokunmatik USB kablosu (USB-A → micro B): 2 Metre Micro USB 2.0 Kablo | 2 | [Robocombo](https://robocombo.com/2-metre-micro-usb-2-0-kablo-sarj-kablosu-4143) · 75,50 · stok 282 | 151,00 | [Robotistan](https://www.robotistan.com/mikro-usb-kablo-1) · 76,24 · stok 90 · 1,5 m (ESP32 yolu 1.360 mm, göğüs dokunmatik 640 mm: yeter) | doğrulandı |
| S59 | Klemens 5,08 mm 2 pin: 2 Pin 1 No 5.08mm Klemens | 4 | [Robocombo](https://robocombo.com/2-pin-1-no-508mm-klemens-2511201001) · 5,50 · stok 672 | 22,00 | [Direnc.net](https://www.direnc.net/0-numara-2li-klemens-1) · 3,45 · stok görünmedi | doğrulandı |
| S60 | Omuz servosu DS3235 (4 + 1 yedek): DSSERVO DS3235 35kg Servo Motor - 180 Derece - Su Geçirmez (Coreless) | 5 | [Robocombo](https://robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4534) · 1.809,00 · stok 85 | 9.045,00 | [Motorobit](https://www.motorobit.com/rds3235-35kg-dijital-servo-motor-180-u-servo-braket-dahil) · 2.631,60 · stok 46 · Farklı marka (RDS3235), braket dahil | doğrulandı |
| S61 | Servo sürücü: PCA9685 16 Kanal 12 Bit PWM Sürücü Lehimli | 1 | [Robocombo](https://robocombo.com/pca9685-16-kanal-12-bit-pwm-surucu-lehimli-4603) · 181,00 · stok 87 | 181,00 | [Robotistan](https://www.robotistan.com/pca9685-16-kanal-i2c-pwmservo-surucu-karti-klon) · 247,61 · stok 493 | doğrulandı |
| S62 | Silikon kablo 12 AWG kırmızı (m): 12AWG Kırmızı Silikon Kablo 1m | 2 | [Robocombo](https://robocombo.com/12awg-kirmizi-silikon-kablo-1m) · 118,00 · stok 386 | 236,00 | [Motorobit](https://www.motorobit.com/12-awg-silikon-kablo-kirmizi-1-metre) · 128,52 · stok 414 | doğrulandı |
| S63 | Silikon kablo 12 AWG siyah (m): 12AWG Siyah Silikon Kablo 1m | 2 | [Robocombo](https://robocombo.com/12awg-siyah-silikon-kablo-1m) · 118,00 · stok 425 | 236,00 | [Motorobit](https://www.motorobit.com/12-awg-silikon-kablo-siyah-1-metre) · 128,52 · tükendi | doğrulandı |
| S64 | Silikon kablo 16 AWG kırmızı (m): 16AWG Kırmızı Silikon Kablo 1m | 1 | [Robocombo](https://robocombo.com/16awg-kirmizi-silikon-kablo-1m) · 60,50 · stok 564 | 60,50 | [Motorobit](https://www.motorobit.com/16-awg-silikon-kablo-kirmizi-1-metre) · 52,02 · stok 225 | doğrulandı |
| S65 | Silikon kablo 16 AWG siyah (m): 16AWG Siyah Silikon Kablo 1m | 1 | [Robocombo](https://robocombo.com/16awg-siyah-silikon-kablo-1m) · 60,50 · stok 403 | 60,50 | [Motorobit](https://www.motorobit.com/16-awg-silikon-kablo-siyah-1-metre) · 52,02 · tükendi | doğrulandı |
| S66 | XT60 konnektör dişi: Amass XT60H-F Dişi Lipo Batarya Güç Konnektör | 5 | [Robocombo](https://robocombo.com/amass-xt60h-f-disi-lipo-batarya-guc-konnektor-4912) · 30,50 · stok 1984 | 152,50 | [Direnc.net](https://www.direnc.net/xt60-plug-60a-li-po-konnektor) · 18,87 · stok 1702 · Takım (erkek + dişi); 5 takım iki satırı karşılar | doğrulandı |
| S67 | XT60 konnektör erkek: Amass XT60H-M Erkek Lipo Batarya Güç Konnektör | 5 | [Robocombo](https://robocombo.com/amass-xt60h-m-erkek-lipo-batarya-guc-konnektor-4913) · 30,50 · stok 1003 | 152,50 | [Direnc.net](https://www.direnc.net/xt60-plug-60a-li-po-konnektor) · 18,87 · stok 1702 · Takım; satır 66 ile birlikte | doğrulandı |

**Robotistan** (24 satır, 32.850,96 TL)

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| S70 | 5 V düşürücü (Pi 5): Pololu 5 V, 5 A Step-Down Regülatör D24V50F5 - PL-2851 | 1 | [Robotistan](https://www.robotistan.com/pololu-5v-5a-step-down-voltaj-regulator-d24v50f5-pl-2851) · 2.266,93 · stok 14 | 2.266,93 | [Motorobit](https://www.motorobit.com/hcw-p715-9-36vtan-5va-5a-voltaj-dusurucu-regulator-karti) · 168,30 · stok 52 · Zayıf muadil: Pololu'nun koruma özellikleri sayfada yok | doğrulandı |
| S71 | Ana sigorta yuvası: Kablolu Bıçak Sigorta Yuvası Standart Boy (F114-C) | 1 | [Robotistan](https://www.robotistan.com/kablolu-bicak-sigorta-yuvasi-standart-boy) · 48,18 · stok 41 | 48,18 | [Robotistan](https://www.robotistan.com/kablolu-bicak-sigorta-yuvasi-mini-boy) · 29,27 · stok 73 · Mini boy; standart boy başka onaylı sitede yok | doğrulandı |
| S72 | Arazi tekerleği: Büyük Arazi Tekerleği 125 mm x 58 mm - Mavi | 4 | [Robotistan](https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi) · 362,27 · stok 7 | 1.449,08 | [Motorobit](https://www.motorobit.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi) · 612,00 · stok 22 · Aynı tekerlek | doğrulandı |
| S73 | Bas-konuş düğmesi: 43mm LED Arcade Basmalı Buton Kırmızı | 1 | [Robotistan](https://www.robotistan.com/43mm-led-arcade-basmali-buton-kirmizi) · 76,24 · stok 13 | 76,24 | — · Onaylı diğer sitelerde 43 mm LED arcade buton bulunamadı | doğrulandı |
| S74 | Göğüs ekranı 11,6" 1080p (gömülü): 11.6inç Kapasitif Dokunmatik LCD Ekran Modülü - 1920×1080, HDMI, IPS | 1 | [Robotistan](https://www.robotistan.com/116-inc-lcd-ekran-modulu) · 9.367,79 · stok 10 | 9.367,79 | [Direnc.net](https://www.direnc.net/116inch-hdmi-lcd-ekran-raspberry-pi-uyumlu-1920x1080-ips-teknik-ozellikleri) · 12.695,09 · stok 4 · Muhafazalı 11,6" 1080p; dokunmatik ve dış ölçü sayfada kontrol edilmedi | doğrulandı |
| S75 | Göğüs ekranı 12 V regülatörü: DC-DC Ayarlı Voltaj Yükseltici-Düşürücü Kartı (LM2577 + LM2596) | 1 | [Robotistan](https://www.robotistan.com/dc-dc-ayarli-voltaj-yukseltici-dusurucu-karti-lm2577lm2596) · 275,67 · stok 68 | 275,67 | [Robotistan](https://www.robotistan.com/5v-3a-voltaj-regulator-karti-lm2596-5v) · 163,45 · stok 361 · Yalnız düşürücü, 12 V çıkış ayarlanamaz: muadil değil, bilgi için | doğrulandı |
| S76 | Kafa ekranı 10,1" QLED: 10.1inç Kapasitif Dokunmatik QLED Quantum Dot Ekran Modülü - 1280×720 Piksel - G+G Sertleştirilmiş Cam Panel (WaveShare, kod 20789) | 1 | [Robotistan](https://www.robotistan.com/101-inc-qled-ekran-modulu) · 7.217,95 · stok 2 | 7.217,95 | [Motorobit](https://www.motorobit.com/waveshare-101-1280720-qled-kapasitif-dokunmatik-hdmi-ekran) · 15.300,00 · stok 10 · Aynı Waveshare ürünü; Direnc 8.523,08 tükendi | doğrulandı |
| S77 | Göğüs ekranı HDMI kablosu (Pi 5 micro HDMI → HDMI A): HDMI Erkek Mikro HDMI Erkek Altın Uçlu Kablo, 1,5 m | 1 | [Robotistan](https://www.robotistan.com/hdmi-erkek-mikro-hdmi-erkek-altin-uclu-kablo-1) · 117,10 · stok 208 | 117,10 | [Direnc.net](https://www.direnc.net/hdmiden-mikro-hdmi-cevirici-adaptor-kablo) · 216,56 · stok görünmedi | doğrulandı |
| S78 | Kafa içi kısa mikro HDMI kablosu, 30 cm, 1/3: DIY HDMI Kablo - 30 cm HDMI Şerit Kablo | 1 | [Robotistan](https://www.robotistan.com/diy-hdmi-kablo-30-cm-hdmi-serit-kablo) · 105,51 · stok 93 | 105,51 | — · DIY HDMI şerit seti yalnız Robotistan'da | doğrulandı |
| S79 | Kafa içi kısa mikro HDMI kablosu, 2/3: Micro HDMI Plug (DIY HDMI Kablo ile Birlikte Kullanılabilir) | 1 | [Robotistan](https://www.robotistan.com/micro-hdmi-plug-diy-hdmi-kablo-ile-birlikte-kullanilabilir) · 247,61 · stok 92 | 247,61 | — · Aynı | doğrulandı |
| S80 | Kafa içi kısa mikro HDMI kablosu, 3/3: HDMI Plug (DIY HDMI Kablo ile Birlikte Kullanılabilir) | 1 | [Robotistan](https://www.robotistan.com/hdmi-plug-diy-hdmi-kablo-ile-birlikte-kullanilabilir) · 247,61 · stok 38 | 247,61 | — · Aynı | doğrulandı |
| S81 | Kafa ekranı 5 V besleme kablosu (USB-A → micro B, 30 cm): Mikro USB Kablo | 1 | [Robotistan](https://www.robotistan.com/mikro-usb-kablo-30) · 34,76 · stok 4689 | 34,76 | [Robotistan](https://www.robotistan.com/micro-usb-15cm-data-kablosu-siyah) · 38,42 · stok 89 · Aynı satıcı, 15 cm | doğrulandı |
| S82 | Kart burcu (M3×8): 8mm M3 Dişi-Dişi Plastik Aralayıcı | 48 | [Robotistan](https://www.robotistan.com/8mm-m3-disidisi-plastik-aralayici) · 1,83 · stok 2457 | 87,84 | [Motorobit](https://www.motorobit.com/m3-10mm-plastik-disi-disi-aralayici-standoff) · 1,84 · stok 4771 · 10 mm (8 mm yok) | doğrulandı |
| S83 | Mikrofon dizisi (4 mikrofon, USB): ReSpeaker Mic Array v2.0 | 1 | [Robotistan](https://www.robotistan.com/respeaker-mic-array-v20) · 6.680,04 · stok 9 | 6.680,04 | — · Onaylı diğer sitelerde ReSpeaker v2.0 bulunamadı | doğrulandı |
| S84 | Motor montaj braketi (4 adet = 2 paket): Aluminyum L tipi 37D Motor Tutucu (İkili) - PL-1084 | 2 | [Robotistan](https://www.robotistan.com/aluminyum-l-tipi-37d-motor-tutucu) · 764,79 · stok 5 | 1.529,58 | [Motorobit](https://www.motorobit.com/37-mm-motor-tutucu) · 107,10 · tükendi · Tükendi (Robotzade 37 mm de stok 0) | doğrulandı |
| S85 | Motor sürücü (2 + 1 yedek): BTS7960B 40 Amper Motor Sürücü Kartı | 3 | [Robotistan](https://www.robotistan.com/bts7960b-20-amper-motor-surucu-karti) · 265,30 · stok 140 | 795,90 | [Robocombo](https://robocombo.com/bts7960b-dc-43a-cift-motor-surucu-2867) · 271,50 · stok 1 · Stok 1 | doğrulandı |
| S86 | Optokuplör modülü: PC817 2 Kanal Optokuplör İzolasyon Modülü | 1 | [Robotistan](https://www.robotistan.com/pc817-2-kanal-optokuplor-izolasyon-modulu) · 74,10 · stok 33 | 74,10 | [Motorobit](https://www.motorobit.com/pc817-2-kanal-optokuplor-izolasyon-modulu) · 76,50 · tükendi · Tükendi (Direnc de tükendi) | doğrulandı |
| S87 | Röle sürücü MOSFET: VBsemi Elec IRLZ44NPBF-VB (TO-220) | 2 | [Robotistan](https://www.robotistan.com/vbsemi-elec-irlz44npbf-vb) · 24,40 · stok 752 | 48,80 | [Direnc.net](https://www.direnc.net/irlz44n-d2pak-smd-n-kanal-mosfet) · 30,25 · tükendi · SMD D2PAK (TO-220 değil) | doğrulandı |
| S88 | Servo uzatma kablosu (1 m): 22AWG Servo Uzatma Kablosu, 100 cm | 19 | [Robotistan](https://www.robotistan.com/60-cekirdek-22awg-servo-kablosu) · 44,52 · stok 71 | 845,88 | [Motorobit](https://www.motorobit.com/servo-uzatma-kablosu-60-cm-disi-erkek) · 61,20 · stok 1832 · 60 cm (boy farklı) | doğrulandı |
| S89 | Ses amfisi: 2*3 W Mini Amfi Devresi - PAM8403 | 1 | [Robotistan](https://www.robotistan.com/23w-mini-amfi-devresi-pam8403) · 21,96 · stok 78 | 21,96 | [Motorobit](https://www.motorobit.com/pam8403-ses-kontrollu-ses-amplifikatoru) · 91,80 · stok 129 · Potlu farklı kart; ölçü kontrol | doğrulandı |
| S90 | Soğutucu: Raspberry Pi Active Cooler | 1 | [Robotistan](https://www.robotistan.com/raspberry-pi-active-cooler-en) · 322,02 · stokta (adet yok) | 322,02 | [Motorobit](https://www.motorobit.com/raspberry-pi-5-aktif-sogutucu-gumus) · 306,00 · stok 19 | doğrulandı |
| S91 | Tırtıllı (T) somun M5, kanal 10: 40 Serisi M5 T Somun | 8 | [Robotistan](https://www.robotistan.com/40-serisi-m5-t-somun) · 37,20 · tükendi | 31,68 (ikinci satıcıyla) | [CNC Marketi](https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu10-kanal-profil-tirtilli-somunu) · 3,96 · stok 42761 · Onaylı değil; kanal 10 M5 (kanal ölçüsü yazan tek sayfa) | doğrulandı (onaylı olmayan satıcı) |
| S92 | USB hub: USB Hub - 4lü - USB (Dahili Güç Anahtarı) | 1 | [Robotistan](https://www.robotistan.com/usb-hub-3lu-mini-usb-a-dahili-guc-anahtari) · 187,23 · stok 38 | 187,23 | [Direnc.net](https://www.direnc.net/usb-coklayici-hub-4-x-usb-20) · 1.157,15 · stok 15 · 6,2× fiyat | doğrulandı |
| S93 | Yönelim sensörü (IMU): BNO055 9DOF Sensör Modül | 1 | [Robotistan](https://www.robotistan.com/bno055-9dof-sensor-modul) · 771,50 · stok 7 | 771,50 | [Motorobit](https://www.motorobit.com/gravity-bno055-bmp280-akilli-10dof-ahrs-imu-sensoru-sen0253) · 4.896,00 · stok 30 · Farklı kart (BNO055 + BMP280), 6,4× fiyat | doğrulandı |

### 5.2 F1b 90° fişleri

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| F1a | 90° HDMI adaptör (göğüs ekranı ucu) | 1 | [Motorobit](https://www.motorobit.com/hdmi-disi-erkek-cevirici-konnektor-90-derece) · 45,90 · stok 104 | 45,90 | [Direnc.net](https://www.direnc.net/hdmi-disi-erkek-cevirici-90-derece-dirsek) · 87,71 · tükendi | doğrulandı · v4 satır 28'de zaten var (aynı ürün): toplama ikinci kez girmez |
| F1b | 90° micro USB (göğüs dokunmatiği, ekran ucu) | 1 | [Robotistan](https://www.robotistan.com/raspberry-pi-usb-kablo-a-micro-b-dik-usb-kablo-donusturucu) · 87,82 · stok 138 | 87,82 | [Robotistan](https://www.robotistan.com/4-pin-cikisli-30cm-micro-usb-kablo-90-derece) · 45,74 · tükendi | doğrulandı · Adaptör bulunamadı; muadil: ekran ucu 90° USB-A → micro B kablo. Boyu sayfada yok (gereken 640 mm). Boy yeterse v4 satır 58'deki 2 m kablolardan biri düşer. İkinci: 30 cm 90° kablo, tükendi ve kısa |
| F1c | 90° DC jak fişi (göğüs ekranı 12 V) | 1 | [Motorobit](https://www.motorobit.com/55x21mm-90-derece-erkek-dc-barrel-jak) · 12,24 · stok 264 | 12,24 | [Motorobit](https://www.motorobit.com/55x25mm-90-derece-erkek-dc-barrel-jak) · 14,08 · tükendi | doğrulandı · Ekranın jak ölçüsü doğrulanmadı; 5,5×2,1 varsayıldı. İkinci aynı mağaza 5,5×2,5 (tükendi); 4,0×1,7 de var |

### 5.3 K4 kabloları (açık karar K4; varsayılan a: koşullu kalem)

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| K4a | USB-A uzatma ~30 cm (Pi port 2 → ses kartı) | 1 | [Robotistan](https://www.robotistan.com/usb-erkek-disi-donusturucu-30cm) · 77,46 · stok 26 | 77,46 | [Robotistan](https://www.robotistan.com/usb-uzatma-kablo-40-cm-seffaf) · 45,13 · stok 53 | doğrulandı · Sipariş boyu 270 mm (kafa-yerlesim/uygulama-notu.md). İkinci: aynı mağaza PM-8608 50 cm (Motorobit 30 cm anahtarlı kablonun veri hattı sayfada yazmıyor) |
| K4b | USB-A uzatma ~1 m (Pi port 3 → hub) | 1 | [Motorobit](https://www.motorobit.com/usb-30-disi-erkek-siyah-uzatma-kablosu-1-metre) · 214,20 · stok 176 | 214,20 | [Robotistan](https://www.robotistan.com/usb-uzatma-kablosu-15-m-seffaf) · 60,99 · stok 29 | doğrulandı · Sipariş boyu 920 mm. Birincil USB 3.0 (kablo çapı boyun kanalına göre ölçülmedi); ikinci USB 2.0 1,5 m (fazla boy sarılır) |
| K4c | L USB-A dirsek, 90° (Pi port 2 ağzı) | 1 | bulunamadı | — | — | bulunamadı / fiyat yok · Onaylı sitelerde bulunamadı (arama: usb 90 derece / dirsek / l tipi / açılı + web araması). Motorobit'te yalnız 50 cm açılı erkek-erkek kablo var (işe yaramaz) |
| K4d | Kısa micro USB kablo ~11 cm (Pi port 1 → ReSpeaker) | 1 | [Robotistan](https://www.robotistan.com/micro-usb-15cm-data-kablosu-siyah) · 38,42 · stok 89 | 38,42 | [Robotistan](https://www.robotistan.com/mikro-usb-kablo-30) · 34,76 · stok 4689 | doğrulandı · Sipariş boyu 110 mm; 15 cm veri kablosu. İkinci aynı mağaza 30 cm |
| K4e | Hoparlör kablosu ~1,1 m (PAM8403 → hoparlör) | 2 | [Motorobit](https://www.motorobit.com/2x050-kordon-kablo-1-metre) · 30,60 · stok 265 | 61,20 | [Direnc.net](https://www.direnc.net/2x050-kordon-kablo) · 21,78 · stokta (adet yok) | doğrulandı · Sipariş boyu 1.030 mm → 2 m (tek parça gelip gelmediği sayfada yok); 2×0,50 mm² |
| K4f | L 3,5 mm fişli kısa kablo ~4 cm (ses kartı → PAM8403) | 1 | bulunamadı | — | — | bulunamadı / fiyat yok · Onaylı sitelerde L (90°) 3,5 mm fiş/kablo bulunamadı. Geçici yol: düz lehimli fiş Motorobit '3.5mm Stereo Jak - Erkek' 9,18 TL (L değil) |

### 5.4 Onaylı sitelerde bulunamayanlar (v4 (a) satırları)

Bu satırlar onaylı beş sitede yok; hocanın öğrencisine URL'siz verilecek grup (`BAGLAM.md:221`). Fiyatı bugün görülenler onaylı olmayan satıcı sayfasından.

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| A119 | Akü kutup pabucu: M5 halka pabuç, 12 AWG kablo için × 2 + M5 yaylı pul | 1 | bulunamadı | 40,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı |
| A120 | Bombe başlı imbus ISO 7380 A2 M3×5 | 3 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380) · 1,15 · stok görünmedi | 3,45 | — | kısmen (taban/varyant fiyatı) · Taban fiyat (boy seçilmeden) |
| A121 | Bombe başlı imbus ISO 7380 A2 M3×6 | 128 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380) · 1,15 · stok görünmedi | 147,20 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A122 | Bombe başlı imbus ISO 7380 A2 M3×14 | 7 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380) · 1,15 · stok görünmedi | 8,05 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A123 | Bombe başlı imbus ISO 7380 A2 M5×18 | 9 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m5-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380) · 2,95 · stok görünmedi | 26,55 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A124 | Bombe başlı imbus ISO 7380 A2 M6×14 | 4 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m6-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380) · 3,89 · stok görünmedi | 15,56 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A125 | Çift taraflı köpük bant, 1 mm (VHB tipi) | 1 | bulunamadı | 44,50 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı (Robocombo VHB tükendi) |
| A126 | Dişli çubuk M3 DIN 976 A2: 4 parça × 77 mm kesilecek | 1 | bulunamadı | 40,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı (plan 4 × 73 mm; v4 4 × 77 mm) |
| A127 | Düz pul DIN 125 A2 M3 | 36 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125) · 0,40 · stok görünmedi | 14,40 | [Robotistan](https://www.robotistan.com/m3-pul-50-adet) · 1,03 · stok 469 | kısmen (taban/varyant fiyatı) · Taban fiyat; ikinci onaylı Robotistan M3 pul (A2 olduğu yazmıyor) |
| A128 | Düz pul DIN 125 A2 M4 | 20 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125) · 0,40 · stok görünmedi | 8,00 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A129 | Düz pul DIN 125 A2 M5 | 14 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125) · 0,40 · stok görünmedi | 5,60 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A130 | Düz pul DIN 125 A2 M6 | 20 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125) · 0,40 · stok görünmedi | 8,00 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A131 | Fiberli somun DIN 985 A2 M3 | 10 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-fiberli-somun-cesitleri-din985) · 1,02 · stok görünmedi | 10,20 | [Robotistan](https://www.robotistan.com/m3-fiberli-somun-10-adet) · 2,61 · stok 686 | kısmen (taban/varyant fiyatı) · Taban fiyat; ikinci onaylı Robotistan |
| A132 | Fiberli somun DIN 985 A2 M4 | 52 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/paslanmaz-fiberli-somun-cesitleri-din985) · 1,02 · stok görünmedi | 53,04 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A133 | Geniş köşe bağlantı, 40×40 kanal 10 | 4 | [CNC Marketi](https://www.cnc-marketi.com/urun/genis-kose-baglanti-40x40-k10) · 25,38 · tükendi | 125,44 (ikinci satıcıyla) | [Otomasyoncu](https://www.otomasyoncu.net/urun/40x40-kose-baglanti-genis) · 31,36 · stok görünmedi | doğrulandı (onaylı olmayan satıcı) · CNC Marketi tükendi; Otomasyoncu (onaylı değil) |
| A134 | Gizli iç köşe bağlantı, 40×40 kanal 10, set vidalı | 8 | [CNC Marketi](https://www.cnc-marketi.com/urun/45x45-gizli-kose-baglanti-90-k10) · 39,60 · stok 989 | 316,80 | — | doğrulandı (onaylı olmayan satıcı) · Sayfa 45×45 K10 (40×40 uyumu doğrulanmadı) |
| A135 | Isıl gömme somun M3, pirinç, delik Ø4,0, boy 5,7 mm | 176 | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3) · 5,29 · stokta (adet yok) | 931,04 | — | kısmen (taban/varyant fiyatı) · Sayfada L 5,7 varyantı yok (ID3 OD4 L4; ID3 OD5 L4–8); CAD deliği Ø4,0 / L 5,7 ile uyum doğrulanmadı. Fiyat taban (varyant seçilmeden). Seçenekler sipariş §4.1. Direnc 'İnsert Somun M3' 12,70 tükendi (dış çap 6 mm) |
| A136 | Isıl gömme somun M5, pirinç | 6 | [Rhino3DPrinter](https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5) · 6,35 · stokta (adet yok) | 38,10 | — | kısmen (taban/varyant fiyatı) · Varyantlı ürün |
| A137 | ISO mini oto röle soketi, 5 fişli, kablolu | 1 | bulunamadı | 120,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı |
| A138 | İmbus cıvata DIN 912 A2 M3×6 | 89 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) · 1,30 · ürün stoğu 77.199 (boy ayrımı yok) | 115,70 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A139 | İmbus cıvata DIN 912 A2 M3×8 | 76 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) · 1,30 · ürün stoğu 77.199 (boy ayrımı yok) | 98,80 | [Robotistan](https://www.robotistan.com/m3-8mm-imbus-civata) · 4,73 · stok 5350 | kısmen (taban/varyant fiyatı) · Taban fiyat; ikinci onaylı Robotistan M3×8 (paslanmaz yazmıyor) |
| A140 | İmbus cıvata DIN 912 A2 M3×10 | 10 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) · 1,30 · ürün stoğu 77.199 (boy ayrımı yok) | 13,00 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A141 | İmbus cıvata DIN 912 A2 M3×12 | 26 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) · 1,30 · ürün stoğu 77.199 (boy ayrımı yok) | 33,80 | [Robotistan](https://www.robotistan.com/m3-12mm-imbus-civata) · 3,77 · stok 581 | kısmen (taban/varyant fiyatı) · Taban fiyat; ikinci onaylı Robotistan M3×12 |
| A142 | İmbus cıvata DIN 912 A2 M3×20 | 5 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912) · 1,30 · ürün stoğu 77.199 (boy ayrımı yok) | 6,50 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A143 | İmbus cıvata DIN 912 A2 M4×12 | 4 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m4-paslanmaz-imbus-civata-cesitleri-din912) · 2,02 · stok görünmedi | 8,08 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A144 | İmbus cıvata DIN 912 A2 M4×16 | 56 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m4-paslanmaz-imbus-civata-cesitleri-din912) · 2,02 · stok görünmedi | 113,12 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A145 | İmbus cıvata DIN 912 A2 M5×12 | 15 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m5-paslanmaz-imbus-civata-cesitleri-din912) · 2,66 · stok görünmedi | 39,90 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A146 | İmbus cıvata DIN 912 A2 M6×14 | 40 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912) · 3,89 · ürün stoğu 322.514 (boy ayrımı yok) | 155,60 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A147 | İmbus cıvata DIN 912 A2 M6×18 | 2 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912) · 3,89 · ürün stoğu 322.514 (boy ayrımı yok) | 7,78 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A148 | İmbus cıvata DIN 912 A2 M6×20 | 2 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912) · 3,89 · ürün stoğu 322.514 (boy ayrımı yok) | 7,78 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A149 | İmbus cıvata DIN 912 M2,5×5 | 12 | bulunamadı | — | — | bulunamadı / fiyat yok · Fiyat yok |
| A150 | İmbus cıvata DIN 912 M2,5×8 | 12 | bulunamadı | — | — | bulunamadı / fiyat yok · Fiyat yok |
| A151 | İmbus cıvata DIN 912 M6×16, fosfat | 18 | [CNC Marketi](https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata) · 3,60 · stok 2 (gereken 18) | 70,02 (ikinci satıcıyla) | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912) · 3,89 · ürün stoğu 322.514 (boy ayrımı yok) | kısmen (taban/varyant fiyatı) · Stok yetmez: ikinci satıcı gerekli · CNC sayfası: 'Son 2 Adet'. İkinci: paslanmaz DIN 912 A2 M6×16 (boy tablosunda 6x16 var; taban fiyat, ürün stoğu 322.514, 'Stoktan teslim 15:00'e kadar aynı gün kargo'); A2 malzemesi fosfat çeliğin yerine (fosfat şartı kaynakta yok: maliyet.json notu yalnız 'CAD M6×16 = 16 + 2 yedek'). CNC'de muadil: M6×16 fosfat bombe başlı 4,80, stok 235 (baş şekli farklı, CAD boşluğu kontrol edilmedi) |
| A152 | JR konnektör seti: erkek + dişi gövde 12'şer adet + krimp pin | 1 | bulunamadı | 150,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı |
| A153 | Mesafe burcu M5×40, dişi-dişi (yoksa M5 uzatma somunu) | 8 | bulunamadı | 320,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı (plan: baskılı burç + uzun cıvata seçeneği) |
| A154 | Mumlu polyester bağlama ipi, Ø0,4 mm | 1 | bulunamadı | — | — | bulunamadı / fiyat yok · Fiyat yok |
| A155 | Perçin somun M3×7, düz flanşlı çelik (2 mm Al için) | 7 | bulunamadı | 35,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı |
| A156 | Perçin somun M5×9, düz flanşlı çelik (3 mm Al için) | 9 | bulunamadı | 45,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı |
| A157 | Plastik için vida M2×8 PT | 4 | bulunamadı | — | — | bulunamadı / fiyat yok · Fiyat yok |
| A158 | Rulman 625ZZ, 5×16×5 mm | 5 | [Rulmanal](https://www.rulmanal.com.tr/urun/625-zz-kwc-5-16-5-rulman) · 30,04 · stok 8398 | 150,20 | — | doğrulandı (onaylı olmayan satıcı) · Sayfa adı artık '625 ZZ BGR 5x16x5 (Karbon)': marka değişti. Motorobit 625ZZ 'plastik kaplı', muadil değil |
| A159 | Rulman 6808-2RS, 40×52×7 mm | 4 | [Rulmanal](https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman) · 108,16 · stok 51 | 432,64 | [Rulmanal](https://www.rulmanal.com.tr/urun/6808-2rs-nsk-40x52x7-rulman) · 1.061,02 · stok 5 | doğrulandı (onaylı olmayan satıcı) · İkinci aynı satıcı NSK |
| A160 | Set vida DIN 913/916 A2 M5×16 | 8 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/5mm-paslanmaz-setskur-cesitleri-kafasiz-alyan-din916) · 0,84 · stok görünmedi | 6,72 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A161 | Set vida DIN 913/916 A2 M6×10 | 16 | [paslanmazcivata.ist](https://www.paslanmazcivata.ist/urun/6mm-paslanmaz-setskur-cesitleri-kafasiz-alyan-din916) · 1,02 · stok görünmedi | 16,32 | — | kısmen (taban/varyant fiyatı) · Taban fiyat |
| A162 | Sigma profil 40×40 ağır tip, kanal 10, ölçüye kesim: 1.115,5 mm × 1; 500 mm × 2; 200 mm × 1; 190 mm × 3 (toplam 2.885,5 mm) | 3 | [CNC Marketi](https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip) · 934,08 · stok 120,9 | 2.802,24 | [Otomasyoncu](https://www.otomasyoncu.net/urun/sigma-profil-40x40-agir-kanal-10) · 1.097,46 · stok görünmedi | doğrulandı (onaylı olmayan satıcı) · TL/m; 3 m alınır, ölçüye kesim ayrıca sorulur |
| A163 | Tırtıllı (T) somun M6, kanal 10 | 62 | [CNC Marketi](https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu-m6) · 3,90 · stok 36790 | 241,80 | — | doğrulandı (onaylı olmayan satıcı) |
| A164 | Yönlü (kardioid/shotgun) mikrofon + USB ses kartı + rüzgâr kılıfı | 1 | bulunamadı | 2.000,00 (v4 yaklaşık) | — | doğrulanmadı · Bulunamadı (onaylı sitelerde kardioid yok) |

### 5.5 Stokta olmayan

| # | Kalem | Adet | Birincil satıcı · fiyat (TL, KDV dahil) · stok | Tutar | İkinci satıcı · fiyat · stok | Durum / not |
|---|---|---|---|---|---|---|
| C170 | Kamera: Raspberry Pi Camera Module 3 | 1 | [Robotistan](https://www.robotistan.com/raspberrypi-camera-module) · 1.835,13 · tükendi | 1.835,13 | [Robotistan](https://www.robotistan.com/raspberry-pi-kamera-modulu-3) · 1.835,13 · tükendi | stok yok · Tükendi; ikinci Robotistan sayfası da 0. Direnc/Motorobit'te Module 3 yok; Robocombo v4'te tükendi. Esnek hedef, kritik yolda değil |

### 5.6 Hizmetler (anlaşmalı firma; tahmini, teklif yok)

| # | Kalem | Adet | Birim (tahmini) | Tutar | Not |
|---|---|---|---|---|---|
| H173 | 3B baskı: PETG 6,47 kg + PETG-CF 1,16–1,21 kg, 65 parça (246×246×250 mm tablaya sığar), beyaz + siyah | 7,7 | 1.500,00 | 11.550,00 | baskı partileri |
| H174 | Alüminyum lazer + abkant: gövde U braketi 3 mm × 8, etek taşıyıcı L braketi 2 mm × 6 | 14 | 60,00 | 840,00 | 2a lazer (kritik yol) |
| H175 | Alüminyum lazer kesim: alt plaka 346×500×3 mm Al 5754 + boyun plakası 3 mm | 1 | 1.500,00 | 1.500,00 | 2a lazer (kritik yol) |
| H176 | Kontrplak lazer kesim: 5 mm huş, 270×226 mm + 270×274 mm | 1 | 500,00 | 500,00 | 2a lazer (kritik yol) |

### 5.7 PAKET A (TÜBİTAK önerisi; okul toplamına girmez)

| # | Kalem | Adet | Satıcı · bugün fiyat · stok | v4 fiyatı | Durum |
|---|---|---|---|---|---|
| P102 | Dijital ses seviyesi ölçer: Uni-T UT-353 Mini Ses ve Seviye Ölçer | 1 | [Direnc.net](https://www.direnc.net/ut-353-mini-ses-ve-seviye-olcer) · 1.512,30 · stokta (adet yok) | 1.512,30 | doğrulandı |
| P103 | I2S MEMS mikrofon modülü: INMP441 Mems I2S Çok Yönlü Mikrofon Modülü | 2 | [Direnc.net](https://www.direnc.net/inmp441-mems-i2s-cok-yonlu-mikrofon-modulu) · 151,23 · stok 497 | 151,23 | doğrulandı |
| P104 | Zemin işaretleme bandı (30 mm × 30 m): 30mmX30M 3D Yazıcı İçin Mavi Baskı Maskeleme Bandı | 2 | [Direnc.net](https://www.direnc.net/30-mm-x-30-m-mavi-bant-ressamlar-baski-maskeleme-araci-reprap-3d-yazici) · 84,69 · stok 11 | 84,69 | doğrulandı |
| P105 | Hoparlör kablosu (2×0,75 mm²): 2x0,75 TSE'li Kordon Kablo - 1 metre | 15 | [Motorobit](https://www.motorobit.com/2x075-tseli-kordon-kablo-1-metre) · 40,39 · stok 273 | 40,39 | doğrulandı |
| P106 | İki kanallı ses yükselteci (2×50 W): TPA3116 D-Class 5.0 HiFi 2x50W 2 Kanal Stereo Amfi Modülü | 1 | [Motorobit](https://www.motorobit.com/tpa3116-d-class-50-hifi-2x50w-2-kanal-stereo-amfi-modulu) · 2.692,80 · stok 30 | 2.692,80 | doğrulandı |
| P107 | Şerit metre (3 m): 3M Şerit Metre 16mm | 1 | [Motorobit](https://www.motorobit.com/3m-serit-metre-16mm) · 107,10 · stok 22 | 107,10 | doğrulandı |
| P108 | USB ses kartı (mikrofon/hat girişli): Harici Ses Kartı CM108 Hoparlör Mikrofon Girişi | 1 | [Motorobit](https://www.motorobit.com/harici-ses-karti-cm108-hoparlor-mikrofon-girisi) · 367,20 · stok 28 | 367,20 | doğrulandı |
| P109 | Yükselteç adaptörü (24 V, 2 A): Gepro UM-0224 24V 2A Adaptör | 1 | [Motorobit](https://www.motorobit.com/gepro-um-0224-24v-2a-adaptor) · 306,00 · stok 253 | 306,00 | doğrulandı |
| P110 | 3,5 mm stereo ses kablosu (1,5 m): 3.5 MM Erkek Erkek 1.5 Mt Stereo AUX Kablo | 2 | [Robotistan](https://www.robotistan.com/35-mm-erkek-erkek-15-mt-stereo-aux-kablo) · 31,10 · stok 19 | 30,97 | doğrulandı |
| P111 | Deney hafıza kartı (32 GB): Micro SD Kart 32GB | 1 | [Robotistan](https://www.robotistan.com/micro-sd-kart-32gb) · 554,38 · stok 53 | 552,08 | doğrulandı |
| P112 | Dişi-dişi bağlantı kablosu (30 cm, 40'lı): 30 cm 40 Pin Ayrılabilen Dişi-Dişi F-F Jumper Kablo | 1 | [Robotistan](https://www.robotistan.com/30cm-40-pin-ayrilabilen-disi-disi-f-f-jumper-kablo-300-mm) · 57,33 · stok 2329 | 57,09 | doğrulandı |
| P113 | Kutulu pasif hoparlör (8 Ω, 5 W): 8 Ohm 5W Hoparlör | 3 | [Robotistan](https://www.robotistan.com/8-ohm-5w-hoparlor) · görünmüyor · stok 1 | 166,41 | doğrulanmadı; stok 1 < gereken 3; fiyat sayfada görünmüyor |
| P114 | Yapay zekâ hızlandırıcı kartı (26 TOPS, PCIe): Raspberry Pi AI HAT+ (26T) | 1 | [Robotistan](https://www.robotistan.com/raspberry-pi-ai-hat) · 6.978,88 · stok 23 | 6.949,89 | doğrulandı |
| | **Toplam (bugün; hoparlör v4 fiyatıyla)** | | | 14.183,32 | **14.215,11** |

### 5.8 Koşullu ve elde (toplama girmez)

| # | Kalem | Adet | Satıcı · fiyat · stok | Not |
|---|---|---|---|---|
| E179 | Etek fanı 12 V 40×40×10 (E7 ısı ölçümüne bağlı) | 1 | [Robocombo](https://robocombo.com/12v-fan-40x40x10mm) · 48,50 · stok 156 | Koşullu; onaylı diğer sitelerde 12 V 40×40×10 bulunamadı |
| E180 | Omni teker Ø127 × 2 (K1 sürüş ölçümüne bağlı) | 2 | eski ithal fiyat 2.269,59 (doğrulanmadı) | Onaylı sitelerde yok; eski ithal fiyat, doğrulanmadı |
| L98 | Raspberry Pi 5 4 GB (ELDE) | 1 | [Robotistan](https://www.robotistan.com/raspberry-pi-5-4-gb) · 7.071,58 · tükendi | Elde; sayfada tükendi |
| L99 | microSD 64 GB Sandisk Ultra (ELDE) | 1 | [Robocombo](https://robocombo.com/sandisk-ultra-64gb-micro-sd-2910) · 995,00 · stok 11 | Elde |

## 6. Açık karara bağlı kalemler

Varsayılanlar `karar-kuyrugu.md`'deki önerilerdir; karar Ahmet'in. Okul bütçesi (93.538,38) K4'ü satın alınacak gibi sayar; 'kararsız kalemler hariç toplam' = varsayılanlar + K4 satırları çıkarılmış: **93.147,10 TL**.

| Karar | Seçenek | Ek maliyet (TL) | Kaynak sayfa · stok | Not |
|---|---|---|---|---|
| K1 6. USB cihazı | a: 5 cihaz (varsayılan) | 0 | — | Hub'da 2 boş port |
| | c: gövdede, hub portuna | 0 – 76,24 | [Robotistan micro USB 1,5 m](https://www.robotistan.com/mikro-usb-kablo-1) · 76,24 · stok 90 | Cihaz bilinmiyor; kablo tipi doğrulanmadı |
| | b: kafada | doğrulanmadı | — | Yeni kablo ve yerleşim |
| K2 AI HAT+ yerleşimi | a: boss taşı / b: HAT yönü | 0 | — | Yalnız baskı geometrisi |
| | Kart (PAKET A'da) | 0 okul / 6.978,88 TÜBİTAK | [Robotistan](https://www.robotistan.com/raspberry-pi-ai-hat) · 6.978,88 · stok 23 | Destek gelmezse okul bütçesine +6.978,88 |
| K4 6 kablo | a: koşullu kalem (varsayılan) | 0 (koşullu = genel toplam dışı); satın alınırsa +391,28 | §5.3 | 2 satır bulunamadı (L USB-A dirsek, L 3,5 mm) |
| | b: ekip karşılar | 0 | — | |
| | c: v4'e kesin kalem | +391,28 | — | |
| K9 el yükü | a: her elde ≤ 100 g (varsayılan) | 0 | — | |
| | b, pay ≥ 1: dirsek 2 MG996R → DS3218MG (2 + 1 yedek) | +2.332,50 | [Robocombo](https://www.robocombo.com/dsservo-ds3218-20kg-servo-motor-180-derece-su--4151) · 980,00 · stok 4; ikinci [Motorobit](https://www.motorobit.com/ds3218mg-20kg-su-gecirmez-dijital-servo-motor) 1.315,80 · stok 101 (+3.339,90) | Dirsek ≥ 12,6 kg·cm; omuz DS3235 6 V'ta 32 ≥ 31,2/31,5 sınırda. CAD/kütle etkisi hesaplanmadı |
| | b, pay ≥ 2 | 6–8,4 V'ta stoklu servo yok (80/150 kg tükendi, 220 kg 24 V) | DS5160 60 kg·cm: [Motorobit](https://www.motorobit.com/ds5160-hv-60kg-dijital-servo-motor) 2.448 · stok 6; [Direnc.net](https://www.direnc.net/ds5160mg-su-gecirmez-servo-motor) 2.419,68 · stok 5 | Gereken ≥ 62,4/63,0 kg·cm: 60 yetmez. Bilgi: 5 × DS5160 = +3.195,00. Dirsek ≥ 25,2 için DS3235: +4.819,50. Motorobit RDS5180 80 kg 2.876,40 ve RDS51150 150 kg 3.672,00 tükendi; Robocombo DES220 220 kg 24 V 15.075,00 stok 5 (24 V hat gerekir). |
| K10 PAM8403 5 V | a: D24V50F5 (varsayılan) / b: SY8205 | 0 | — | |
| | c: ayrı düşürücü | +61,20 | [Motorobit](https://www.motorobit.com/dc-5-30v-to-5v-3a-voltaj-dusurucu-modulu) · 61,20 · stok 459; ikinci [Robotistan](https://www.robotistan.com/5v-3a-voltaj-regulator-karti-lm2596-5v) 163,45 · stok 361 | Yer ve ölçü doğrulanmadı |
| K11 göğüs 12 V dalı | a (varsayılan) / b | ≈ 0 | — | Parçalar aynı (regülatör, mini yuva, 2 A sigorta v4'te); kablo boyu farkı ölçülmedi |
| K12 kafa havası | a: yarıklar (varsayılan) | 0 | — | |
| | b: 30 mm fan 12 V | +66,07 | [Motorobit](https://www.motorobit.com/30x30x10mm-12v-010a-fan-2-kablolu) · 66,07 · stok 526; ikinci [Robotistan](https://www.robotistan.com/sogutma-fan-12v-kablo-28cm) 90,87 · stok 97 | Fan yeri HAT zarfıyla kesişiyor (K2) |
| F2 omuz durdurucu | — | **F2 bekliyor** | — | Baskı parçası (filament, satın alınmaz) + belki vida/somun; P4.3/P8.2 ekler |

## 7. Toplamlar ve `maliyet.json` ile fark

| Toplam | TL |
|---|---|
| Onaylı site satırları (v4, 81 satır; M5 somun CNC ile) | 67.995,98 |
| F1b yeni 2 satır | 100,06 |
| K4 (4 fiyatlı satır) | 391,28 |
| Onaylı sitelerde bulunamayanlar (46 satır; 4'ü fiyatsız) | 8.825,93 |
| Kamera (stok yok, son sayfa fiyatı) | 1.835,13 |
| **Parça toplamı** | **79.148,38** |
| · doğrulanmış (onaylı + onaylı olmayan satıcı) | 72.556,44 |
| · kısmen (taban/varyant fiyatı) | 1.962,31 |
| · doğrulanmamış (v4 yaklaşık + kamera) | 4.629,63 |
| Hizmetler (tahmini) | 14.390,00 |
| **Okul bütçesi, doğrulanmamış ve K4 dahil** | **93.538,38** |
| Okul bütçesi, doğrulanmamış hariç | 88.908,75 |
| Okul bütçesi, kararsız hariç (K4 çıkar) | 93.147,10 |
| Okul bütçesi × 1,15 (maliyet.json yöntemi) | 107.569,14 |
| Okul bütçesi, kararsız hariç × 1,15 | 107.119,16 |
| Koşullu dahil × 1,15 (maliyet.json koşullu 108.208,77 ile kıyas) | 112.844,97 |
| Elde dahil × 1,15: (okul bütçesi + elde 8.066,58) × 1,15 | 116.845,70 |
| PAKET A (ayrı) | 14.215,11 |

**Köprü: `maliyet.json` genel 102.919,71 → F8a okul bütçesi 93.538,38**

| Adım | TL | Neden |
|---|---|---|
| `maliyet.json` genel (29.10 + F4a 09.11 kısmi eklemeleri, 1,65 m) | 102.919,71 | ara 89.495,40 × 1,15 |
| − %15 pay | −13.424,31 | F8a sayfa fiyatı veriyor, pay eklemiyor |
| − elde kalemler | −21.648,48 | Pi 5 4 GB 7.031,58 + microSD 2.192,40 + Waveshare 10,1" 12.424,50 (maliyet.json bunları toplama katıyor; v4 katmıyor) |
| − kargo satırı | −1.440,00 | v4 kargo hariç |
| − filament | −6.843,09 | 03.11: filament firma/ekipten; baskı hizmeti aşağıda hizmetlerle eklenir |
| − lazer + bükme hizmeti | −2.840,00 | İkisinde de 2.840,00; aşağıda hizmetlerle geri eklenir |
| = 29.10 listesinin parça tutarı | 56.723,83 | |
| + Göğüs ekranı 11,6" (yeni; 29.10 listesinde göğüs ekranı yok) | +9.367,79 |  |
| + Kafa ekranı 10,1" QLED (29.10'da Waveshare 10,1" 'elde'; yukarıda elde kalemlerle düşüldü) | +7.217,95 |  |
| + Göğüs ekranı yan parçaları: 12 V regülatör, HDMI 1,5 m, 90° HDMI, F1b 90° micro USB ve DC jak | +538,73 |  |
| + Kafa içi HDMI şerit seti (3 satır) − 29.10 'ekran kablosu' 114,30 | +486,43 |  |
| + Omuz servosu DS3235 5 adet: 1.809 − 1.171,50 (29.10 fiyatı) | +3.187,50 |  |
| + Mikrofon dizisi: ReSpeaker v2.0 6.680,04 − XVF3800 5.500 (tahmini) | +1.180,04 |  |
| + Pi 5 V düşürücü: D24V50F5 − Pololu D36V50F5 1.975,38 (ithal) | +291,55 |  |
| + Kafa sesi ve USB (K16, K5): PAM8403, USB ses kartı, USB hub, SY8205, micro USB 30 cm | +482,63 |  |
| + K4 kabloları (açık karar, 4 fiyatlı satır) | +391,28 |  |
| − Çıkanlar (03.11 kararı): oyun kolu 750 + perçin somun aleti 400 | −1.150,00 |  |
| + Diğer: ~90 satırda satıcı, fiyat ve adet değişiklikleri (v4 satıcıları, adet bölünmesi, vida adetleri, kamera fiyatı vb.) | +430,65 | Kalıntı: köprü toplamından geri hesaplandı, kalem kalem ayrıştırılmadı. |
| = F8a parça toplamı | 79.148,38 | |
| + hizmetler (baskı 11.550 + lazer/bükme 2.840) | 14.390,00 | |
| = **F8a okul bütçesi** | **93.538,38** | |

Kısaca: `maliyet.json` 1,65 m listesinde kafa ekranı 'elde' sayılıyordu ve göğüs ekranı yoktu; 158 listesinde iki ekran satın alınacak (+16.586). Aynı esasla (pay dahil, kargo hariç): alınacaklar 107.569,14 ↔ `maliyet.json` elimizdekiler düşülmüş 78.023,96 → +29.545,18; elde dahil 116.845,70 ↔ 102.919,71 → +13.925,99.

78.023,96: `F4a-gunluk.md:74` (V3, yazıcılı, elimizdekiler düşülmüş). Elde dahil = (okul bütçesi + elde 8.066,58: Pi 5 4 GB ve microSD bugünkü fiyatla) × 1,15. Kontrol turundaki 107.563,13 / +29.539,17 / +13.919,99 değerlerinden fark +6,01: M6×16 artık ikinci satıcıyla (18 × 3,89).

### En pahalı 15 sipariş satırı (doğrulama önceliği c)

| # | Kalem | Tutar | Durum |
|---|---|---|---|
| S5 | Akü 12,8 V LiFePO4 20 Ah | 12.680,70 | doğrulandı |
| S74 | Göğüs ekranı 11,6" 1080p (gömülü) | 9.367,79 | doğrulandı |
| S60 | Omuz servosu DS3235 (4 + 1 yedek) | 9.045,00 | doğrulandı |
| S76 | Kafa ekranı 10,1" QLED | 7.217,95 | doğrulandı |
| S83 | Mikrofon dizisi (4 mikrofon, USB) | 6.680,04 | doğrulandı |
| A162 | Sigma profil 40×40 ağır tip, kanal 10, ölçüye kesim: 1. | 2.802,24 | doğrulandı (onaylı olmayan satıcı) |
| S9 | Enkoderli DC motor | 2.661,64 | doğrulandı |
| S70 | 5 V düşürücü (Pi 5) | 2.266,93 | doğrulandı |
| A164 | Yönlü (kardioid/shotgun) mikrofon + USB ses kartı + rüz | 2.000,00 | doğrulanmadı |
| C170 | Kamera: Raspberry Pi Camera Module 3 | 1.835,13 | stok yok |
| S52 | Akü şarj cihazı | 1.809,00 | doğrulandı |
| S56 | Dirsek, bilek, kafa servosu (6 + 2 yedek) | 1.620,00 | doğrulandı |
| S84 | Motor montaj braketi (4 adet = 2 paket) | 1.529,58 | doğrulandı |
| S72 | Arazi tekerleği | 1.449,08 | doğrulandı |
| A135 | Isıl gömme somun M3, pirinç, delik Ø4,0, boy 5,7 mm | 931,04 | kısmen (taban/varyant fiyatı) |

## 8. Satıcı toplamları ve kargo

| Satıcı | Satır | Tutar (bugün) | Ücretsiz kargo eşiği | Kargo ücreti | Kargoya veriliş (sayfa) |
|---|---|---|---|---|---|
| Robotistan | 26 | 33.022,98 | 1.500 (geçiyor) | 0,00 | '48 saat içerisinde kargoya'; 1.500 TL üzeri ücretsiz kargo |
| Robocombo | 16 | 14.596,50 | 2.000 (geçiyor) | 0,00 | '15:00'e kadar verilen siparişler aynı gün kargoda'; 2.000 TL üzeri ücretsiz, altı 150 TL |
| Atakale | 1 | 12.680,70 | sayfada görülmedi | sayfada yok | 'Ürün sipariş edildiğinde sizin için 7 gün içinde üreticiden/ithalatçıdan tedarik edilerek özel sipariş olarak gönderilecektir'; koli kargo mesafeye göre 1/2/3/5 gün |
| Motorobit | 34 | 4.881,20 | 2.500 (geçiyor) | 0,00 | 'Saat 15.00'a kadar verilen siparişler aynı gün kargoda'; 2.500 TL üzeri ücretsiz (MNG-DHL) |
| CNC Marketi | 4 | 3.392,52 | 2.400 (geçiyor) | 0,00 | 'Stoktan hızlı gönderim'; 'Kargo 132,00 TL (KDV dahil)', 2.400 TL üzeri ücretsiz |
| Direnc.net | 9 | 3.274,26 | 1.500 (geçiyor) | 0,00 | 'Saat 15:00'e kadar ... aynı gün kargoda'; 1.500 TL üzeri ücretsiz |
| paslanmazcivata.ist | 25 | 993,17 | 2.000 (altında) | sayfada yok | 'Stoktan teslim 15:00'e kadar aynı gün kargo'; 2.000 TL üzeri ücretsiz; ücret sayfada yok |
| Rhino3DPrinter | 2 | 969,14 | 2.500 (altında) | 139,00 | 'saat 16:00 ve öncesi ise siparişiniz aynı gün kargoya verilir', sonrası stoktaysa ertesi iş günü; 'Yurtiçi Kargo 139TL', 2.500 TL üzeri ücretsiz |
| Rulmanal | 2 | 582,84 | 2.500 (altında) | sayfada yok | 'Aynı Gün Kargo Saat 16:00'a kadar olan siparişler'; 2.500 TL üzeri ücretsiz; ücret sayfada yok |
| Otomasyoncu | 1 | 125,44 | sayfada görülmedi | sayfada yok | Kargo ve stok sayfada yok (fiyat '0,52 USD + KDV') |

Sayfada görülen kargo ücretiyle eşik altı kalan: Rhino3DPrinter 139 TL. Eşik altı ya da eşiği bilinmeyen, ücreti sayfada olmayan: paslanmazcivata.ist, Rulmanal, Otomasyoncu. Atakale'nin kargo ücreti sayfada yok. CNC Marketi (3.392,52) 2.400 eşiğini geçiyor (M6×16 paslanmazcivata.ist'e geçtiği için 64,80 düştü). Kargo toplamlara eklenmedi; bilinen ücretler toplamı 139,00 TL. Onaylı olmayan satıcıların sipariş tutarı: 6.063,11 TL.

Akü yedeği Limacell (Geçersun Enerji) siparişe girmedi; seçilirse 3.000 TL eşiğini geçer (kargo ücretsiz).

## 9. Ahmet'e gidecek sorular ve öneriler

Kontrol raporunun (`F8a-kontrol.md` §5) 12 maddesi ve F8a karar taslakları (KT1–KT9) birleştirildi. Hepsi öneri; karar Ahmet'in, panoya yazılmadı.

1. **Hocadaki liste:** 17.10 Excel mi, 03.11 v4 mü (`BAGLAM.md:222` 'beğendi' ↔ `malzeme-listesi/rapor.md:4` 'gönderilmedi')? Öneri: v4 hocada sayılsın, §2.2 farkı iletilsin; değilse §2.1.
2. **Bütçe farkı:** 158 alınacaklar (pay dahil, kargo hariç) 107.569,14 TL; `maliyet.json` elimizdekiler düşülmüş 78.023,96'dan (README ≈ 78.000) +29.545,18; elde dahil kıyasla +13.925,99. Öneri: fark sipariş öncesi hocaya bildirilsin.
3. **Erken alım:** 1.515,90 TL + Rhino kargosu 139 = 1.654,90. Öneri: bu hafta (H7), insert 168 (fark 8 P4.3'te). Satıcılar onaylı değil: okul siparişi mi kişisel alım mı? Insert varyantı §4.1: öneri A (OD4 L4; kupon değişmeden Ø3,8/3,9 delikleri dener, CAD boyu P4.3'te 4'e çekilir); B kupon ve CAD değişikliği ister, C takvime yetişmez. M5 için de aynı karar: kupon delikleri Ø6,2–6,6, Rhino OD 7 kuralıyla Ø6,7–6,8 gerekir (§4.1).
4. **Akü:** Atakale Victron stok 1, '7 gün içinde tedarik': S'de sipariş adım 9 için sınırda (§3.1). Öneri: Atakale aküsü erken alımla bu hafta sipariş edilsin (12.680,70 TL; S'den önce ödeme ve hoca onayı gerekir); olmazsa S'de Limacell 24 Ah (4.814,86, onaylı değil; ölçü ve 30 A sürekli akım kontrolüyle).
5. **Kafa ekranı:** Hocadan mı gelecek, alınacak mı (README ve `maliyet.json` notu 'hocadan gelirse' ↔ v4 satın alma satırı)? Alınacaksa QLED Robotistan stok 2, indirimli 7.217,95 (liste 8.124,85; Motorobit 15.300). Öneri: alınacaksa S'nin ilk partisinde; stok 1'e düşerse öne alınsın.
6. **K4 (6 kablo):** a seçilirse genel toplam dışı (0), satın alınırsa +391,28; L USB-A dirsek ve L 3,5 mm kısa kablo onaylı sitelerde yok. Öneri: bu iki kablo P4.2'de kablo yarıçapıyla yeniden değerlendirilsin.
7. **K9 el yükü:** a (≤ 100 g) 0 TL, varsayılan; b pay ≥ 1 dirsek DS3218MG +2.332,50 (Robocombo stok 4; ikinci satıcıyla +3.339,90); b pay ≥ 2: 6–8,4 V'ta stoklu servo yok (80/150 kg tükendi, 220 kg 24 V).
8. **K1, K10, K11, K12:** Etkileri 0–76,24 TL; bütçe açısından önemsiz, tasarım kararı.
9. **K2 / AI HAT+:** PAKET A'da (6.978,88); TÜBİTAK desteği gelmezse okul bütçesine mi eklenecek?
10. **3B baskı hizmeti:** 11.550 TL tahmini (7,7 kg × 1.500): anlaşmalı firma ücretli mi, teklif alınacak mı? Öneri: teklif S'den önce istensin; gelene kadar `maliyet.json`'a fiyatlı satır yazılmasın.
11. **M6×16 (18 adet, CNC'de 2):** Fosfat şartının kaynağı bulunamadı (`maliyet.json` notu yalnız 'CAD M6×16 = 16 + 2 yedek'). Seçenekler: paslanmaz DIN 912 A2 M6×16 (paslanmazcivata.ist, taban 3,89, ürün stoğu 322.514; F8a tutarı bununla) ya da CNC M6×16 fosfat bombe başlı 4,80, stok 235 (sigma ile tek kargo; baş şekli CAD'le kontrol edilmeli). Öneri: paslanmaz DIN 912 (baş şekli aynı). Dayanım sınıfı farkı (A2-70 ↔ fosfat; sınıf sayfada yok) sigma bağlantısı için kontrol edilmedi.
12. **Onaylı olmayan satıcılar:** CNC Marketi, Rulmanal, Rhino3DPrinter, paslanmazcivata.ist, Otomasyoncu: 6.063,11 TL. Hocanın öğrencisine URL'siz (a) grubu olarak mı gidecek? Tırtıllı somun M5 Robotistan'da tükendi; öneri CNC Marketi (M6 somun ve sigmayla aynı sipariş).
13. **8 Ω hoparlör (PAKET A):** Robotistan stok 1 < 3, fiyat sayfada görünmüyor. Öneri: PAKET A için ikinci satıcı ya da adet düşürme (bu paketin kapsamı dışında).
14. **Kamera:** Module 3 ve NoIR Module 3 tükendi (v4 notu 'gelmezse NoIR'). Kritik yolda değil; öneri: S'de yeniden bakılsın.
