# Sipariş listesi farkı: hocaya iletilen liste ↔ güncel 1,65 m tasarım (29 Ekim 2026)

**Durum (Duffy, 29.10):** sipariş verilmedi; sipariş listesi hocaya iletildi. Eski kalemlerde ekleme / çıkarma yapılabilir.
Bu dosya yalnız fark çıkarır; hocaya gönderilmedi.

## Hangi liste "hocaya iletilen" sayıldı

- **Liste:** demo sayfasının maliyet düğmesinden indirilen iki Excel, 17 Ekim 2026:
  `robot-maliyet-V3-2026-10-17.xlsx` (tam liste) ve `robot-maliyet-V3-elimizdekiler-dusuldu-2026-10-17.xlsx` (Duffy'nin
  İndirilenler klasörü; depoda yok). 15:25'teki ilk indirme ile 15:38'deki "(1)" kopyası bayt bayt aynı (md5 aynı).
- **Gerekçe:** DuffyOS kaydı (17.10, 15:40): sorumlu hocaya "Lale Robot Maliyet Listesi" e-postası hazırlandı, 2 Excel eki (tam liste
  + elimizdekiler düşülmüş), Duffy kendisi gönderecekti; 29.10'da "sipariş listesi hocaya iletildi" dedi. Dosya adındaki "sipariş" / "hoca" araması depoda (üç dal) bir liste
  bulmadı. Excel'in içeriği `planlama/maliyet.json` `b27fd80` sürümü (17 Ekim, "fiyat ve stok güncellemesi"; `2b07779`'a kadar
  değişmedi): 97 kalem, ara 86.672,21 TL, genel **99.673,04 TL** (`maliyet_toplam.py` ile aynı). Elimizdekiler düşülmüş: genel 72.696,96 TL
  (Pi 5, microSD, Nextion düşülmüş). Bu tek aday; sonraki maliyet sürümü (`d823435`, 29.10) hocaya gönderilmedi.
- **Güncel:** `planlama/maliyet.json` (29.10, Y2b + bu günün servo hattı kararı), V3 satırları, yazıcıyla, yedek ve %15 pay dahil;
  adetler `tasarim/freecad/montaj/robot-bom.csv` (1.650 mm, 1.073 parça) bağlantı / satın alma satırlarından + %5–15 pay
  (Y2b kontrolünde BOM ile birebir doğrulandı). 96 kalem, ara 89.710,01 TL, genel **103.166,51 TL** (29.10 Pi 4 GB düzeltmesiyle; önce 94.783,78 / 109.001,35).

Fiyat farkı = (güncel adet × güncel birim) − (listedeki adet × listedeki birim), KDV dahil, pay hariç. "Tahmini" yazan fiyat satıcı
sayfasından doğrulanmadı.

## Eklenecekler (3 kalem, +7.540,00 TL)

| Kalem | Adet | Fark TL | Neden |
|---|---|---|---|
| Mikrofon dizisi: Seeed reSpeaker XVF3800 USB 4 mik, kasalı | 1 | +5.500,00 (tahmini) | ReSpeaker Lite'ın yerine (Efe, 26.10; `raporlar/mikrofon-secimi.md`, main): AEC, gürültü bastırma, yön; fuar gürültüsü |
| Yönlü mikrofon kolu (kardioid shotgun + USB ses kartı + kürk kılıf) | 1 | +2.000,00 (tahmini) | XVF3800'e ek, konuşan kişiye yönlü alım (aynı rapor) |
| Saplama M3 DIN 976 (4 × 73 mm kesilir) | 1 | +40,00 (tahmini) | CAD kafada 4 saplama (`robot-bom.csv`; Y2b), listede yoktu |

## Çıkarılacaklar (4 kalem, −12.058,53 TL)

| Kalem | Adet | Fark TL | Neden |
|---|---|---|---|
| Göğüs ekranı Nextion NX1060P101 10,1" | 1 | −9.159,71 | Göğüs ekranı kaldırıldı (25.10; kumanda telefondan). Eldeydi: "elimizdekiler düşülmüş" listesinde zaten toplamda değildi |
| Mikrofon ReSpeaker Lite | 1 | −2.617,54 | XVF3800 + yönlü mikrofonla değişti |
| Yüz paneli, 3 mm akrilik 190 × 115 | 1 | −250,00 | 10,1" kafada panel yok, CAD'de yok |
| Tırtıllı somun M4 (kanal 10) | 8 | −31,28 | 1,65 m CAD'de yok (Y2b'de silindi) |

## Adet veya model değişenler (22 kalem, +7.556,33 TL)

| Kalem | Listede (17.10) | Güncel (29.10) | Fark TL | Neden |
|---|---|---|---|---|
| Yüz ekranı | Waveshare 7" HDMI (C), 2.790,25 | Waveshare 10,1" HDMI (B), 12.424,50 | +9.634,25 | Hoca 10" kafa istedi (21.10). Hoca verecek: "elde" işaretli; verirse fark 0 |
| Omuz servosu | DS3218MG × 4, 964,50 | **DS3235** × 4, 1.171,50 | +828,00 | Kol ×1,25 (1,65 m), omuz torku; DS3218 yetmiyor |
| Yedek omuz servosu | DS3218MG × 1 | DS3235 × 1 | +207,00 | Aynı servo |
| PETG filament (1 kg) | 6 | 8 | +778,00 | Baskı 63 parça, 7,71–7,77 kg (`baski-listesi.md`) |
| Servo uzatma kablosu 1 m | 14 | 19 | +219,70 | Uzun kol + gövde: iki kol 11,2 m + S1 / pan / tilt 5,8 m, ×1,1 |
| **DC-DC düşürücü XL4016** | 3 | **4** | +242,40 | **Karar 29.10:** kol + kafa servosu bir hatta ≈ 5,45 A > 5 A → sağ kol, sol kol, kafa (pan + tilt) ayrı regülatör |
| **Hat sigortası yuvası (mini)** | 3 | **4** | +40,00 | Karar 29.10: dördüncü XL4016'nın girişi (5 A) |
| **Bıçak sigorta (ek)** | 5 | **6** | +5,00 | Karar 29.10: kafa servo hattı 5 A mini sigorta |
| Sigma profil 40 × 40 ağır | 3 × 1 m çubuk, 908,33 | 3,0 m, satıcı ölçüye keser, 934,08 | +77,25 | 1,65 m direk tek parça 1.185,5 + 2 × 500 + 200 + 3 × 190 = 2.955,5 mm (BOM); 1 m çubuktan direk çıkmaz |
| Alüminyum bükme braket | 10 | 14 | +240,00 | Gövde U braketi 4 → 8 (1,65 m gövdede dört seviye, iki yan; BOM 8 + 6) |
| Alüminyum lazer kesim | alt plaka 270 × 500 | 346 × 500 (taban 520) | 0,00 | Taban 520 mm; fiyat aynı varsayıldı, teklif yenilenmeli |
| ESP32 – Pi USB kablosu | 1,5 m | 2 m | 0,00 | Gereken 1,64 m (Pi kafada, gövde uzadı); fiyat aynı varsayıldı |
| Isıl gömme somun M3 | 125 | 160 | +182,70 | BOM 142 + pay |
| Isıl gömme somun M5 | 12 | 16 | +25,08 | BOM 13 + pay |
| Bombe başlı imbus M3 (ISO 7380) | 70 | 108 | +43,70 | BOM 96 + pay |
| İmbus civata M3 (DIN 912) | 198 | 195 | −3,90 | BOM 174 + pay |
| İmbus civata M5 | 20 | 24 | +10,64 | BOM 21 + pay |
| İmbus civata M6 (14 / 20) | 32 | 42 | +38,90 | BOM 36 + 2 + pay |
| Fiberli somun M3 / M4 | 48 | 62 | +14,28 | BOM 8 + 47 + pay |
| Pul (DIN 125) | 70 | 93 | +9,20 | BOM 32 / 15 / 21 / 16 + pay |
| T-somun M6 (kanal 10) | 50 | 60 | +37,90 | BOM 56 + 2 + pay |
| **Ana bilgisayar (elde)** | Raspberry Pi 5, 8 GB, 12.105,35 | **Raspberry Pi 5, 4 GB RAM**, 7.031,58 | −5.073,77 | **Karar 29.10 (Duffy: "pi 4 gb"):** eldeki kart 4 GB (Pi kurulumu 17.10). Fiyat Robotistan 4 GB sayfası (29.10). Eldeki kalem: satın alma yok, elimizdekiler düşülmüş toplam değişmez |

Aynı adda karşılığı olan diğer 71 kalem adet, model ve fiyatta aynı.

## Net fark

| | Hocadaki liste (17.10) | Güncel (29.10) | Fark |
|---|---|---|---|
| Kalem sayısı | 97 | 96 | +3 / −4 / 22 değişen |
| Parçalar + kargo (ara) | 86.672,21 | 89.710,01 | **+3.037,80 TL** |
| Genel (%15 pay dahil) | 99.673,04 | 103.166,51 | **+3.493,47 TL** |
| Elimizdekiler düşülmüş, genel | 72.696,96 (Pi, SD, Nextion düşülmüş) | 78.270,76 (Pi, SD, 10,1" yüz ekranı düşülmüş) | +5.573,80 TL |

Farkın büyüğü: yüz ekranı +9.634 (hoca verirse 0), mikrofon değişimi +4.882 (XVF3800 + yönlü − ReSpeaker; ikisi tahmini fiyat),
Nextion −9.160 (eldeydi), Pi 8 → 4 GB −5.074 (eldeki; 29.10), DS3235 +1.035, PETG +778. 29.10 servo hattı kararı (XL4016 + yuva + sigorta): +287,40 ara, +330,51 genel.
Koşullu kalemler (omni teker, fan, M6 CAD bağlantıları) iki listede de toplama girmiyor; koşullularla güncel genel 109.132,23 TL (Pi 4 GB ile; önce 114.967,06).

## Notlar
- XL4016 dördüncü adedi henüz CAD'de yok (`robot-bom.csv` 3 adet; etek yerleşimi Y3 / Y4'te).
- XVF3800 ve yönlü mikrofon fiyatları tahmini, stok belirsiz: listeye eklemeden önce satıcı fiyatı alınmalı.
- Listede "Raspberry Pi 5, 8 GB" (eldeki kalem) vardı; DuffyOS kurulum kaydı (17.10) eldeki Pi'nin 4 GB çıktığını yazıyor, Duffy 29.10'da
  "pi 4 gb" dedi → `maliyet.json` "Raspberry Pi 5, 4 GB RAM", 7.031,58 TL (yukarıdaki tabloda). Satın alma toplamını etkilemiyor (eldeki kalem).
- **Y3 (29.10, M6 CAD) sonrası:** güncel genel **103.767,58 TL** (+601,07: dışarıdan ISO 7380 + perçin somun + perçin aleti artık toplama giriyor, M5 ısıl gömme / M5×10 / pul düştü; `maliyet.json`). Yukarıdaki tablolar Y3 öncesi (103.166,51); fark Y6'da yeniden çıkarılır.
- Kaynak dosyalar: Excel'ler (yukarıda), `git show b27fd80:planlama/maliyet.json`, `planlama/maliyet.json`, `planlama/adim5/maliyet_toplam.py`.
