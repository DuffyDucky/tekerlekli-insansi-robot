> Kaynak: Efe'nin vault'undaki rapor (27 Ekim 2026). Karar: şimdilik modem alınmıyor, gezdiren kişinin hotspot'u kullanılacak (bkz. planlama/kararlar-2026-10-27.md); bu rapor ilerde gerekirse diye duruyor.

# Lale için Wi-Fi yayan 4G modem: 3 seçenek (2026-10-27)

Gerek: beyin bulut API'de; robot bahçede de internete ulaşmalı; telefon kumandası için telefon ve Pi aynı Wi-Fi'da olmalı → modem hem internet verir hem robotun kendi Wi-Fi ağını yayar. Veri ayda 1-3 GB.

| Seçenek | Model | Fiyat (27.10.2026) | Artı | Eksi |
|---|---|---|---|---|
| Öneri | TP-Link M7200 (pilli MiFi) | MediaMarkt 2.429 TL (indirimli), Vatan 3.929 TL | B1/B3/B7/B8/B20 (TR operatörleriyle uyumlu görünüyor), 10 cihaz, 94×57×20 mm, micro-USB 5 V/1 A, 24 ay TR garanti, çok satıcı | Pilli (2000 mAh): robot içinde ısı/şişme riski, USB'de sürekli çalışma doğrulanmadı; dış anten çıkışı yok; yalnız 2,4 GHz |
| Pi için en rahat | Huawei E8372h-320 (Wi-Fi'lı USB dongle) | TR fiyatı doğrulanamadı (Amazon.com.tr stok yok; Trendyol "4G Mobile WiFi 5" 2.458 TL, model teyitsiz) | Pilsiz, USB'den beslenir, 94×30×14 mm ~45 g, 2 harici anten girişi, HiLink modunda Pi'de USB-Ethernet olarak görünür (sürücü yok) | Güvenilir stoklu satıcı yok; kilit/bant listesi satıcıya göre çelişiyor; bazı Huawei dongle'lar Pi'de güç sorunu çıkarmış |
| Operatör cihazı | Turkcell Superbox Go MW63VC | Pasaj 2.299 TL (164 TL/ay taksit) | Operatörden tek elden | Operatöre kilitli mi, bant, besleme doğrulanmadı; puanı düşük |

Hat (güz 2026): Vodafone faturasız 3 ay 50 GB 875 TL (~292 TL/ay, +27 TL telsiz); Turkcell faturasız aylık 4 GB 386,80 TL; Türk Telekom faturasız (yalnız arama özeti) 28 gün 10 GB 200 TL / 25 GB 300 TL → en ucuz görünen, hat alırken teyit. M2M/IoT SIM gerekmez (çıkarım). Öğrenci tarifesi araştırılmadı.

Alternatifler: telefon hotspot (bedava; telefon robota bağlı kalır, hem kumanda hem kaynak olamaz); eduroam'a Pi (PEAP ile mümkün ama kişisel hesap robota gömülür, bahçede kapsama yok, istemci izolasyonu olabilir).

Pi kurulumu (öneri): SIM PIN'ini kapat, modemi telefonla kur (APN, otomatik bağlan); Pi: `nmcli dev wifi connect <SSID> password <şifre>`; telefon aynı ağa, modem arayüzünden Pi'ye DHCP rezervasyonu; dongle alınırsa `lsusb` + `nmcli device` ile `usb0`/`enx…` Ethernet, yönetim 192.168.8.1; ilk gün masada USB'den 1 saat sürekli çalışma testi.

Toplam ilk maliyet ≈ 2.429 + 875 + 27 + SIM bedeli ≈ 3.400 TL; aylık ~200-300 TL. TÜBİTAK tablosu 16.000'de dolu; bu kalem sanayi ortağı/üniversite ya da ekip. Kaynaklar: MediaMarkt https://www.mediamarkt.com.tr/tr/product/_tp-link-m7200-4g-lte-300-mbps-mobil-kablosuz-router-1194544.html · Vatan https://www.vatanbilgisayar.com/tp-link-m7200-150mbps-4g-lte-tasinabilir-kablosuz-n-router.html · TP-Link datasheet https://static.tp-link.com/upload/product-overview/2024/202404/20240402/M7200_datasheet.pdf · Amazon.com.tr E8372h https://www.amazon.com.tr/dp/B08CY7VF3S · Turkcell Pasaj https://www.turkcell.com.tr/pasaj/bilgisayar-tablet/modem-ve-network-urunleri/modemler · Vodafone faturasız https://www.vodafone.com.tr/tarifeler/faturasiz-kolay-paketler · Turkcell 4 GB https://www.turkcell.com.tr/paket-ve-tarifeler/konusma/aylik-4-gb-internet-paketi-hazirkart · TT faturasız https://bireysel.turktelekom.com.tr/mobil/yeni-musteri-tarife-ve-paketleri/faturasiz-paketler · Pi dongle rehberi (08.10.2026) https://raspberry.tips/en/raspberrypi-tutorials/raspberry-pi-usb-mobile-dongle-4g-lte
