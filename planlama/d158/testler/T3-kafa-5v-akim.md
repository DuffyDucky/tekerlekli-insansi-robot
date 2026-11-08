# T3 · Kafa 5 V hatları: gerilim ve akım

Kâğıt T3 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Kafadaki iki 5 V hattını yük altında ölçmek: **Pi hattı** (Pololu D24V50F5 → Raspberry Pi 5 ve USB cihazları) ve **ekran hattı**
(SY8205 → 10,1" QLED Power). Ayrıca kafanın 12 V girişindeki toplam akımı ölçmek. İki hat ayrı ölçülür.

## Neden önemli

Kafa 5 V bütçesi tamamen hesap: Pi hattı 2,67 A, QLED 0,9 A **varsayım**, toplam 3,57 A; hiçbiri ölçülmedi, tepe değer
hesaplanmadı (`elektrik.md:22-25`). Pi hattı 5 A düşürücünün sınırına yaklaşırsa Pi düşük gerilim uyarısı verir, yeniden başlar.
Araştırma önerisi 4 saatlik yükte düşük gerilim uyarısının 0 olmasını şart koşuyor (`oneri-taslak-v8.md:68`).

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| D24V50F5: 5 V ±%4, 5 A sürekli, giriş en çok 38 V | `elektrik.md:16`, `07-gogus.md:47` | Satıcı sayfası; 12 V girişte sürekli akım üretici eğrisinden **doğrulanmadı** |
| Pi hattı (D24V50F5) normal 2,67 A, 5 A'nın %53'ü | `elektrik.md:24` | Hesap, ölçülmedi |
| SY8205: giriş 7–30 V, sürekli 3,7 A, koruma yazmıyor | `elektrik.md:18`, `07-gogus.md:51` | Satıcı sayfası |
| QLED (ekran hattı) 0,9 A | `elektrik.md:18`, `elektrik.md:25` | **Varsayım** |
| Kafa 5 V toplam normal 3,57 A (≈ 17,85 W) | `elektrik.md:22` | Hesap; tepe hesaplanmadı |
| Kafa 12 V girişi normal ≈ 1,55 A; sigorta F3 5 A | `elektrik.md:26`, `elektrik.md:334` | Hesap |
| Pi 5 USB çıkışları toplam 1,6 A (5 A kaynakta) | `07-gogus.md:47` | Satıcı/üretici notu (T5 ölçer) |
| Ayar: `PSU_MAX_CURRENT=5000`, `usb_max_current_enable=1` | `elektrik.md:247-248` | Tasarım |

## Gereken alet

- **DC akım pensi** (0,01 A çözünürlük): akım ölçümünde öncelikli alet. S2 (30 dk) yalnız pensle ölçülür.
- Pens yoksa seri **ölçüm köprüsü**: montajda D24V50F5 çıkışı ile USB-C ucu arasına ve SY8205 çıkışı ile Power kablosu arasına küçük bir
  klemens bırak; multimetre 10 A kademesi oraya seri girer. Bu yalnız S0 ve S1 için ve yalnız aletin 10 A süre sınırı S0/S1'in 5 dk'lık süresini karşılıyorsa kullanılır; karşılamıyorsa S0/S1'de de pens kullanılır.
- Multimetre ×2, laboratuvar güç kaynağı (12,8 V, akım sınırı 5 A) ya da akü + F3 5 A sigorta
- Pi'de terminal: `vcgencmd`, `stress-ng` (yoksa `sudo apt install stress-ng`)
- Kafadaki her şey takılı: QLED (HDMI + Power + Touch), kamera, ReSpeaker, USB ses kartı + PAM8403 + hoparlör, hub (dokunmatik + ESP32)

## Güvenlik

- **T2 GEÇER olmadan** QLED'in Touch kablosu Pi'ye takılmaz.
- 12 V girişini ters bağlama: D24V50F5'te ters gerilim koruması var, **SY8205'te koruma yazmıyor** (`elektrik.md:18`). İlk enerjiyi
  laboratuvar kaynağıyla, akım sınırı 1 A'de ver; Pi açıldıktan sonra sınırı 5 A'e çıkar (F3 ile aynı, `elektrik.md:334`).
- Akü kullanılıyorsa ana sigorta ve F3 5 A takılı; çıplak uçlar bantlı. Pens ya da prob takarken enerji kapalı.
- **Multimetreyle akım:** [00-genel.md](00-genel.md) "Multimetreyle akım ölçümü" kuralı. Kısaca: kırmızı uç 10 A soketine, yalnız seri,
  enerji kapalıyken bağla; iş bitince kırmızı uç V soketine geri; 10 A süre sınırına uy, dakikalarca süren ölçümde pens kullan.
- **Saat, yüzük, bileklik çıkar.**
- Düşürücüler ısınır: çalışırken elle tutma.
- Servo gücü bu testte gerekmez: anahtarlı bara kapalı (röle K1 çekmemiş), kafa servoları hareket etmez.

## Yöntem

1. Pi'de ayarları kontrol et ve yaz: `sudo rpi-eeprom-config` çıktısında `PSU_MAX_CURRENT=5000`; `vcgencmd get_config usb_max_current_enable`
   → `1` (`elektrik.md:247-248`). Değilse önce düzelt.
2. Ölçüm noktaları: **N1** kafa 12 V girişi (P6KE18A sonrası, + teli), **N2** D24V50F5 çıkışı (Pi hattı), **N3** SY8205 çıkışı (QLED Power).
   Her noktada gerilim (çıkış ucu ile GND arası) ve akım (önce pens; seri multimetre yalnız S0/S1'de ve süre sınırı 5 dk'yı karşılıyorsa).
   **Seri multimetre takılıysa** gerilimi multimetrenin **Pi (yük) tarafında** oku: multimetrenin iç direnci birkaç amperde onlarca–yüzlerce
   mV düşürür, düşürücü çıkışında okunan değer Pi'nin gördüğünü göstermez. Bu durumda tabloya "seri" yaz; aynı senaryoyu pensle
   tekrarlayabiliyorsan `get_throttled` sonucu için pensli koşu esas alınır.
3. Pi'nin kendi gördüğü gerilim için (Pi 5'e özgü komut): `vcgencmd pmic_read_adc EXT5V_V`.
4. Her senaryoda 5 dk bekle; süre boyunca **en düşük gerilimi** ve **en yüksek akımı** yaz. Senaryo sonunda
   `vcgencmd get_throttled` çıktısını yaz.
   - **S0 boşta:** masaüstü açık, QLED parlaklık %100, program çalışmıyor.
   - **S1 normal karşılama:** yüz animasyonu, kamera açık, ReSpeaker kaydediyor, hoparlörden orta seste konuşma çalıyor.
   - **S2 stres:** `stress-ng --cpu 4 --timeout 30m` + yüz animasyonu + hoparlörden yüksek ses (`elektrik.md:270` test şartı). 30 dk (varsayım; uzun 4 saatlik test H1 kapsamında ayrıdır).
     **Akım yalnız pensle**; pens yoksa S2'de akım ölçülmez (seri multimetre çıkarılır, köprü kısa tel ile kapatılır), yalnız gerilim ve `get_throttled` yazılır.
5. S2'nin sonunda düşürücülerin üstüne elle değmeden yaklaş: koku, ses (ıslık), kararma var mı, not al.
6. Pi test sırasında kendiliğinden yeniden başladıysa bir önceki açılışın günlüğüne bak (kalıcı günlük açıksa):
   `journalctl -b -1 | grep -i voltage`. Yeniden başlama tek başına KALIR sebebidir.

## Kayıt tablosu

Ayarlar: `PSU_MAX_CURRENT` = ______  `usb_max_current_enable` = ______

Tablo 1: 12 V girişi ve Pi hattı

| Senaryo | Ölçer (pens / seri) | N1 12 V (V) | N1 akım (A) | N2 Pi hattı en düşük (V) | N2 akım en yüksek (A) |
|---|---|---|---|---|---|
| S0 boşta | | | | | |
| S1 normal | | | | | |
| S2 stres | | | | | |
| S2 tekrar | | | | | |

Tablo 2: ekran hattı ve Pi'nin kendi okuması

| Senaryo | N3 ekran hattı en düşük (V) | N3 akım en yüksek (A) | EXT5V_V (V) | get_throttled |
|---|---|---|---|---|
| S0 boşta | | | | |
| S1 normal | | | | |
| S2 stres | | | | |
| S2 tekrar | | | | |

Gözlem (koku, ses, ekran titremesi, yeniden başlama): ________________________________________________

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| N2 Pi hattı gerilimi, her senaryoda en düşük | **4,80–5,20 V** (5 V ±%4) | `elektrik.md:16` |
| N2 Pi hattı akımı, en yüksek | **< 5,0 A** | `elektrik.md:16` |
| N3 ekran hattı gerilimi | **4,75–5,25 V** | USB 2.0 belirtimi, Tablo 7-7 (dış kaynak; SY8205 toleransı sayfada yok) |
| N3 ekran hattı akımı, en yüksek | **< 3,7 A** | `elektrik.md:18` |
| N1 kafa 12 V akımı, en yüksek | **< 5,0 A** (F3) | `elektrik.md:334` |
| `get_throttled` her senaryoda | **0x0** (düşük gerilim ve yavaşlama yok) | `oneri-taslak-v8.md:68` |

Bunlar geçse de şu farklar kaydedilir ve belgeye işlenir (kalır sayılmaz): S1'de N2 > 2,67 A ya da N3 > 0,9 A çıkarsa hesap varsayımı
yanlıştır; `elektrik.md:22-25` ve akım bütçesi (`elektrik.md:315`) güncellenir.

## Sınır aşılırsa

- Pi hattı 5 A'e dayanıyor ya da gerilim 4,80 V'un altına iniyorsa: `elektrik.md` E4 (`elektrik.md:243-245`) ve açık iş 8
  (`elektrik.md:472`). Kaynakta geçen daha büyük seçenek D24V150F5 (`07-gogus.md:48`); seçim **Ahmet Yorulmaz**'ın.
- Ekran hattı aşarsa ya da QLED titriyorsa: `elektrik.md:18` ve açık iş 14 (`elektrik.md:478`), karar Ahmet Yorulmaz.
- `get_throttled` 0x0 değilse: ölçümü tekrarla, kablo boyunu ve kesitini (D24V50F5 → USB-C ucu 20 AWG ~10 cm, `elektrik.md:246`) kontrol
  et, sonucu tasarım ajanına ver. PAM8403'ün besleme noktası da etkiler: bkz. [T4](T4-pam8403-ses-karti.md) ve `karar-kuyrugu.md` K10.

## Sonuç

☐ GEÇER  ☐ KALIR    Pi hattı en yüksek: ______ A   Ekran hattı en yüksek: ______ A   12 V en yüksek: ______ A

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
