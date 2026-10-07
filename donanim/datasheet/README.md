# Elimizdeki parçaların datasheet'leri

Sadece elde olan parçalar burada. Yeni parça gelince eklenir. İndirme tarihi: 7 Ekim 2026.

| Parça | Dosya | Kaynak |
|---|---|---|
| Raspberry Pi 5 8GB | `raspberry-pi-5-product-brief.pdf` (özellikler) | https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf |
| | `raspberry-pi-5-mechanical-drawing.pdf` (ölçü, delikler) | https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf |
| | `pi5-step/rpi-5b_no_graphics.step` (3B model, CAD için) | https://datasheets.raspberrypi.com/rpi5/RaspberryPi5-step.zip |
| | `rp1-peripherals.pdf` (GPIO/UART çipi RP1) | https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf |
| Nextion NX1060P101_011 (Intelligent, 10.1") | `NX1060P101-011C-I_dimension.pdf` (ölçü çizimi, R ve C sürümü ortak) | https://cdn.nextion.tech/wp-content/uploads/2022/03/NX1060P101-011C-I_dimension.pdf |
| | Elektrik özellikleri PDF değil, web sayfasında (aşağıda özet) | https://nextion.tech/datasheets/nx1060p101-011c-i/ |

Datasheet'i olmayanlar: 64 GB SD kart ve Pi adaptörü. Marka/model belli olunca eklenecek.

## Robot için önemli değerler

### Raspberry Pi 5
- Besleme: 5 V / 5 A, USB-C (Power Delivery destekli).
- Kart ölçüsü 85 × 56 mm, montaj delikleri 58 × 49 mm aralıklı, Ø2.7 (mekanik çizim).
- GPIO 3,3 V mantık seviyesinde. 5 V sinyal doğrudan bağlanmaz.
- Çalışma sıcaklığı 0–70 °C, kapalı kutuda havalandırma şart.

### Nextion NX1060P101_011
- Ekran 1024 × 600 IPS. Dış ölçü 258 × 152 mm, görünen alan 222,72 × 125,28 mm.
- Montaj delikleri 251,6 × 145,6 mm aralıklı. Kalınlık yaklaşık 9,8 mm + 1,6 mm PCB.
- Besleme: 5 V (4,75–6,5 V). %100 parlaklıkta 800 mA, uykuda 170 mA. Önerilen kaynak 5 V 2 A.
- Bağlantı: 4 pin 2,54 mm (GND, RX, TX, +5V). UART 2400–921600 baud.
- **Dikkat:** Datasheet TX çıkışını 3,0–5,0 V olarak veriyor. Pi'nin RX pini 3,3 V'tur, 5 V'a dayanıklı değildir.
  Nextion TX → Pi RX hattına gerilim bölücü (1 kΩ + 2 kΩ) ya da seviye dönüştürücü koy.
  Pi TX (3,3 V) → Nextion RX doğrudan bağlanabilir (RX giriş eşiği 3,0 V).
- Karttaki "ON TTL / OFF 232" seçicisi Pi için **TTL** konumunda olmalı.
- Arayüz Nextion Editor ile hazırlanır, microSD kartla ya da seri hattan yüklenir. USB yok.
- Dokunmatik tipi (C kapasitif / R dirençli) kutu etiketinden doğrulanacak.
