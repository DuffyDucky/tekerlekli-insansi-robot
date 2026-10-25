# 1,70 m taslak: maliyet farkı (V3'e göre)

25 Ekim 2026. Bu dosya `planlama/maliyet.json`'ı (V3, 125 cm) **değiştirmez**; taslak ana tasarım olunca
kalemler oraya işlenir. Fiyatlar KDV dahil. "Tahmini" yazanlar satıcı sayfasından doğrulanmadı.

## Kararlaşmış farklar

| Kalem | V3 | 1,70 m taslak | Adet | Fark (TL) | Durum |
|---|---|---|---|---|---|
| Omuz servosu | DS3218MG, 964,50 (Robocombo) | **DS3235**, 1.171,50 indirimli / 1.255 liste (Robocombo, stok 134, 24 Ekim 2026) | 4 + 1 yedek | **+1.035** (liste fiyatıyla +1.453) | doğrulandı; ürün açıklamasında "RDS3235" geçiyor, satıcıya model ve kulak deliği (49,5 × 10) sorulacak |
| Dirsek çatalı horn cıvatası | M3x8 | **M3x12** + başın altında 2× DIN 125-A M3 pul | 8 cıvata + 16 pul | ~+30 | tahmini |
| PETG filament (Microzey HS PETG beyaz, 389 TL/kg) | 6 kg (parçalar ≈ 4,94 kg) | ~8 kg (taslakta PETG parçalar ≈ 6,65 kg; uzatma bantları 1,15 kg + 10" kafa) | +2 kg | ~+778 | tahmini (fire payı V3 ile aynı oranda) |

## Fiyatlanmamış / karar bekleyen farklar

| Kalem | Not |
|---|---|
| Gövde direği (sigma 40×40) | 800,5 → 1.235,5 mm; 1 m stok yetmez. 1,5–2 m boy, özel kesim ya da iki parça + ek plakası. Fiyat araştırılmadı |
| Yüz ekranı | 7" (2.790,25) → 10" HDMI. **Hoca verecek** (21 Ekim); verilmezse Waveshare 10.1" (B) 12.424,50 (Robotsepeti, V2 kaydı) → +9.634 |
| Kablolar | Gövde içi hatlar +435 mm, kol tüpü +30 mm, bilek servosu +32,4 mm; S1/S2 için 20 AWG önerisi onaysız |
| Taban 520 mm + akü 75 mm öne | Devrilme önerisi, onaysız; plaka ve etek dolgu şeridi değişir |
| Servo hattı düşürücüsü | Akım ölçümünde XL4016 yetmezse 20 A düşürücü (~400–600 TL, tahmini) |
| Onaysız mekanik öneriler | 6806 S2 destek rulmanı, ikinci 6808, kelepçeli horn |

## Kararlaşmış farkların toplamı

≈ **+1.843 TL** (indirimli servo fiyatıyla; liste fiyatıyla ≈ +2.261 TL). Ekran hocadan gelirse fiyatlanmamış
kalemler içinde en büyüğü direk profilidir.

Kaynaklar: `kol-analiz/NOTLAR.md` (DS3235 fiyat ve stok), `CATAL-NOTLAR.md` (cıvata ve pul), `kutle.json` (PETG kütlesi),
`planlama/maliyet.json` (V3 fiyatları).
