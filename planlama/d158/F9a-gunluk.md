# P9.1 (F9a) günlüğü — takvim ve kritik yol, ajan A, 08.11.2026

Brief: `planlama/d158/F9a-brief.md`. Yazılan dosyalar yalnız `planlama/proje-plani.md` ve bu günlük. CAD koşturulmadı, commit yok.

## Okunan kaynaklar (salt okuma)

| Kaynak | Ne alındı |
|---|---|
| `planlama/dongu-158.md` §3 F9, §2 | P9.1 kabulü ("her hafta satırı bir bağımlılığa bağlı"), yapılmayacaklar (onaysız satın alma yok) |
| `planlama/siparis-farki-2026-10-29.md:3` | Sipariş verilmedi, liste hocada |
| `planlama/baski-listesi.md` (03.11) | Parti 1–4: 65 parça (+ Parti 0 kuponları), 7,63–7,68 kg, 159–160 sa; paylaşımlı yazıcıda 4–5 hafta (tahmini, satır 84); kuponlar ~3 sa; filament firma + ekip (satır 37); STL dışa aktarma açık iş |
| `planlama/adim4/M6-montaj-sirasi.md` §2 | 48 adım + F5; sıra kuralları (elektrik testi kabuktan önce, kafa kabuktan önce, kollar kabuktan sonra) |
| `planlama/rehber/R-gunluk.md` | Rehber yarım: seçiciler 125 cm'den, göğüs ve kafa ekranı adımları yazılmadı |
| `planlama/yazilim-plani.md` | Y0–Y12 paketleri, H16 = 11–17 Oca, ilk sürüş tanımı |
| `planlama/maliyet.json` (tarih 2026-10-29) | Satıcı, stok, durum alanları; stoksuz / ithal / tahmini kalemler; 6808 ve ısıl gömme birim fiyatı |
| `raporlar/kaynaklar/05-fiyat-arastirmasi.md:578–579` | Robotsepeti "tedarik süresi yaklaşık 7–12 iş günü" (tek kaynaklı teslim süresi) |
| `raporlar/kaynaklar/06-aku-secimi.md:121` | Limacell "özel üretim, ort. 3 iş günü" |
| `raporlar/kaynaklar/06-onayli-satici-B.md`, `07-gogus-ekrani-ve-5v.md` | 10,1" QLED Robotistan stokta, 11,6" Robotistan stokta, D24V50F5 stokta (01.11) |
| `tasarim/freecad/lale158/lale158-kontrol.json` | `toplam_boy_mm` 1580.0, `parca` 1177 |
| `tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md` + `uygulama-ivme.json` | `ev.kutle_g` 25.910,6 g (400 g kablo payı dahil), yüksüz rampa payı 1,517 |
| `planlama/d158/servo-10-oneri.md` | 10 servo: DS3235 × 4 (S1, S2), MG996R × 6 (dirsek, bilek, pan, tilt) |

## Bulgular

1. **Teslim süresi kaynağı neredeyse yok.** Kaynaklar stok durumunu yazıyor (29.10 – 01.11), kargo süresini yazmıyor. Kaynaklı tek süreler:
   Robotsepeti 7–12 iş günü ve Limacell 3 iş günü üretim. Geri kalan teslim süreleri "varsayım" diye işaretlendi.
2. **Baskı, S'den önce başlarsa kritik yolda değil; başlamazsa kritik yola girer.** Parti 1 kupon sonucuna bağlı, kupon değerlendirmesi
   6808 rulmanı ve ısıl gömme somunu ister (kuponlar A, B, C). Bunlar siparişle gelirse baskı ≈ S+1,5'te başlar; 159–160 sa,
   paylaşımlı yazıcıda haftada ≈ 32–40 sa (4–5 hafta tahmininden türetildi) → kabuk montajı ≈ 1,5–2 hafta gecikir.
   Erken alım (6808 × 4 + M3 × 168 + M5 × 6 ısıl gömme, `maliyet.json` birim fiyatlarıyla ≈ 1.340 TL; düzeltme turu 1'de 625ZZ ve kupon D eklendi → ≈ 1.490 TL; tur 2: kupon D fiyatıyla ≈ 1.496 TL) Ahmet'in kararı; plana öneri olarak yazıldı.
3. **Taban, lazer kesime bağlı.** Alt plaka 346 × 500, 14 bükme braket ve kontrplak atölyeden; süre ve fiyat tahmini, DXF gerekli.
4. **Stoksuz kalemler kritik yolda:** mesafe burcu M5 × 40 (`maliyet.json` `stok: belirsiz`, Türkiye'de bulunamadı; taban adım 10); ön şarj rölesi K2, optokuplör, IMU,
   kart burcu seti, servo uzatma kablosu, geniş köşe bağlantı (`maliyet.json` 29.10 `stok: yok`). XVF3800 ithal, ön sipariş (kritik yolda değil).
5. ~~Kritik yol nominal 8 hafta; iyimser ≈ 6,5, kötümser ≈ 12~~ → düzeltme turu 1: durum A 7,5 / 8 / 13, durum B ≈ 10–10,5 hafta; düzeltme turu 2: B ≈ 9,5–10 hafta (aşağıda).

## Senaryolar (ilk tur; düzeltme turu 1'de değişti, aşağıya bakın)

| | S = 16.11 (H8) | S = 30.11 (H10) |
|---|---|---|
| İlk sürüş (S+3) | 6.12 (H10) | 20.12 (H12) |
| Konuşan + jest yapan robot (S+7) | 3.01 (H14) | 17.01 (H16) |
| Demo hazır (S+8) | 10.01 (H15) | 24.01 (dönem sonrası) |
| H15–16'ya sığıyor mu | Evet, H16 tampon | Hayır, ≈ 1 hafta açık. Kesintiyle (jest 8 → 4, kabuğun bir kısmı sonraya, 2 senaryo × 10 deneme) ≈ 10–14.01'de sığar, tampon yok; ya da teslimi 1–2 hafta kaydırma (karar) |

Kötümser sürelerle (+4 hafta) iki senaryo da sığmaz.

## proje-plani.md'de değişenler

- Giriş paragrafı: 1,58 m sayıları (boy 1.580,0 mm, 1.177 parça, 25.910,6 g, 10 servo, 10,1" QLED kafa, 11,6" göğüs ekranı); 1,65 m ve 125 cm tarihçe olarak.
- "Tek takvim" paragrafı: H9 ilk sürüş hedefinin geçersiz olduğu, takvimin S'ye göre yazıldığı.
- Yeni bölümler: "Kritik yol", "Takvim (sipariş gününe göre)", "İki örnek", "Kesinti sırası", "S'yi beklemeden yapılabilecekler", "Dış tarihler".
- Eski takvim tablosu "Tarihçe: 15 Ekim takvimi" başlığıyla aynen kaldı. "1,65 m geçişi" paragrafı tarihçe başlığına alındı, 1,58 m cümlesi eklendi.
- Riskler: "Sipariş gecikmesi" ve "Baskı kapasitesi" satırları eklendi; "Parça stoğu / kargo" ve devrilme satırı 1,58 m'ye göre güncellendi.
- Kapasite paragrafına kalan haftaların kişi-saati eklendi; "İlk iki hafta" 4. maddede 1,65 m → 1,58 m.
- Takma ad dosyadan çıkarıldı, yerine "Ahmet" yazıldı (depo herkese açık; `dongu-158.md` §2 kuralı).

## Açık kalanlar (karar ya da doğrulama)

- Erken alım (≈ 1.496 TL) ve lazer DXF teklifi: Ahmet'in kararı.
- Kabuğun bir kısmını kollardan sonraya bırakmak M6 kural 4'e aykırı olabilir (F2–F3 → F4 sırası); rehberde doğrulanmadı.
- ESP32 Y1/Y3/Y4'ün masada hazır olduğu varsayıldı; durum belgesi okunmadı (kod `main` dalında, yazılım sorumlusunun alanı).
- Final sınav haftaları ve demo günü kaynaklarda yok.

## Düzeltme turu 1 (08.11.2026; kontrol `F9a-kontrol.md` KOŞULLU, 10 madde)

| # | Kontrol maddesi | Yapılan |
|---|---|---|
| 1 | S = 16.11 "Evet" koşulsuz yazılmış | İki durum ayrıldı. **A:** erken kupon alımı + Parti 0–1 S+3'ten önce + lazer ≤ 1 hf → 8 hf. **B:** koşullar yok → ≈ 10–10,5 hf. İki örnek tablosu 4 sütun (S × durum); son güvenli gün tablosu ve "Sipariş gecikmesi" riski koşulla yazıldı |
| 2 | Lazer yalnız adım 4–5'e bağlı yazılmış | 2a → M6 adım 4–15 ve 18; nominal 1 hf, koşul "DXF ve teklif S'den önce, atölye ≤ 1 hf" açık yazıldı (koşul yoksa 1,5 → durum B). Aşama 5'e 2b (akü, adım 9) eklendi. Sigma kesimi 2a'dan 2'ye alındı |
| 3 | Kesinti 4 M6 ile çelişiyor | Kesinti listesinden çıkarıldı; "gövde kabuğu F2–F4 tamamen dışarıda" karar maddesine çevrildi (bedeli kol başına ≈ 25 cıvata söküm, göğüs ekranı ertelenir; tarihlere katılmadı). Kesinti 2 + 3 kazancı ≈ 1 hf; S = 30.11 (A) → 17.01, tampon yok. "≈ 4.12" son günü → 30.11 (A) / 16.11 (B) |
| 4 | İyimser / kötümser tablodan çıkmıyor | Tablodan türetildi: 7,5 / 8 / 13 hf (aşama sırasıyla yazıldı); "+4 hf" → "+5 hf" |
| 5 | Erken alım listesi eksik | 625ZZ × 5 (148,35 TL) ve kupon D bağlantı elemanları eklendi; toplam ≈ 1.490 TL (M5 fiyatı tahmini, M3×20 seti fiyatsız) |
| 6 | Robotsepeti genellemesi | "MAX98357A ve ReSpeaker Lite sayfalarında", ≈ 1,5–2,5 hf |
| 7 | "Tamponsuz" belirsiz | "demo H16'nın son günü 17.01'deyse" eklendi |
| 8 | 2209-B tarihi kaynaksız, hafta yanlış | Kaynak: Ahmet'in bildirimi (P9.1 brief'i), depoda belge yok; "(H8 – H9 pazartesi)" |
| 9 | M6 tablosu 125 cm | Not eklendi: 1,58 m'de göğüs ve kafa ekranı adımları yazılmadı, adım numaraları kayabilir (`R-gunluk.md`) |
| 10 | Günlük | Kişi adı → "yazılım sorumlusu"; "Parti 1–4: 65 parça (+ Parti 0)"; mesafe burcu `stok: belirsiz` |

### Tur 1 sonucu (tur 2 ile geçersiz; aşağıdaki tur 2 tablosuna bakın)

| | S = 16.11, A | S = 30.11, A | S = 16.11, B | S = 30.11, B |
|---|---|---|---|---|
| İlk sürüş | 6.12 (H10) | 20.12 (H12) | 9.12 (H11) | 23.12 (H13) |
| Konuşan + jest yapan robot | 3.01 (H14) | 17.01 (H16) | 17.01 (H16) | 31.01 |
| Demo hazır | 10.01 (H15) | 24.01 | 24–28.01 | 7–11.02 |
| H15–16'ya sığar mı | Evet, H16 tampon | Hayır; kesinti 2 + 3 ile 17.01, tampon yok | Hayır; kesinti 2 + 3 ile 17–21.01 | Hayır, kesintiyle de |

Son güvenli sipariş günü: A'da 16.11 (bir hafta tampon), 23.11 (tamponsuz, demo 17.01'deyse), 30.11 (kesinti 2 + 3 ile);
B'de 2.11 / 9.11 (geçti), kesintiyle 16.11. Belirleyici olan bu hafta (H7): erken kupon alımı ve DXF/teklif.

## Düzeltme turu 2 (08.11.2026; "Yeniden kontrol 1" KOŞULLU, Y1–Y4)

| # | Kontrol maddesi | Yapılan |
|---|---|---|
| Y1 | B iki gecikmeyi üst üste topluyordu (8 + 0,5 + 1,5–2) | B ≈ **9,5–10 hf**: lazerin yarım haftası aşama 8'in baskı beklemesinin içinde kalır. B sütunları: gövde S+6,5–7, kollar S+7,5–8, jest S+8,5–9, demo S+9,5–10. Kesinti satırı, son güvenli günler, risk satırı güncellendi |
| Y2 | A'nın baskı koşulu tek yazıcıda yetmiyordu | A koşulu (a): Parti 1 ≈ S−0,5'te başlar, ≈ S+1,5'te biter; Parti 2 ≈ S+1,5 → 2,3; Parti 3 → 2,8; Parti 4 → S+4–4,5. S = 16.11 hazırlık takvimi (≈ 12.11'e kadar) yazıldı. Takvim tablosunda parti sütunu tek yazıcıya göre sıralandı. Aşama 8'e omuz yuvası (adım 19) ve kafa servo yuvası (adım 23) → Parti 2 bağımlılığı eklendi |
| Y3 | M3×20 "fiyatsız" yanlış | `maliyet.json:136` M3 imbus 1,30 TL; kupon D 2 × 1,30 + 4 × 0,40 (pul) + 2 × 1,02 (DIN 985) = 6,24 TL → toplam ≈ 1.496 TL |
| Y4 | "9.11 fiilen geçti" | "9.11 yarın; hoca onayı ve ödeme birkaç günde beklenmediği için fiilen kaçırıldı (varsayım)" |

Yuvarlama notu: S+8,5 = 59,5 gün → 16.11 için ≈ 14.01 (kontroldeki ≈ 13.01 ile yarım gün farkı); 30.11 için ≈ 28.01.

### Son sonuç

| | S = 16.11, A | S = 30.11, A | S = 16.11, B | S = 30.11, B |
|---|---|---|---|---|
| İlk sürüş | 6.12 (H10) | 20.12 (H12) | 9.12 (H11) | 23.12 (H13) |
| Gövde + kabuk | 20.12 (H12) | 3.01 (H14) | 31.12 – 3.01 (H14) | 14–17.01 (H16) |
| Konuşan + jest yapan robot | 3.01 (H14) | 17.01 (H16) | 14–17.01 (H16) | 28–31.01 |
| Demo hazır | 10.01 (H15) | 24.01 | 20–24.01 | 3–7.02 |
| H15–16'ya sığar mı | Evet, H16 tampon | Hayır; kesinti 2 + 3 ile 17.01, tampon yok | Hayır; kesinti 2 + 3 ile ≈ 14–17.01, tampon yok | Hayır; kesintiyle ≈ 28–31.01 |

Son güvenli sipariş günü: A 16.11 (tamponlu) / 23.11 (tamponsuz) / 30.11 (kesintiyle); B 2–6.11 (geçti) / 9–13.11 (fiilen kaçırıldı) / 16–19.11 (kesintiyle).

A'nın hazırlık takvimi (S = 16.11): 9.11 erken alım kararı + sipariş · 9–10.11 Parti 0 · 11–12.11 parçalar gelir (varsayım), kupon
değerlendirmesi, CAD/STL · **12.11 Parti 1 başlar** → 25.11 · Parti 2 → 1.12 · Parti 3 → 5.12 · Parti 4 → 17.12. S = 30.11 için son gün ≈ 26.11.

## Kayıt ajanı notu (08.11.2026, ajan C; "Yeniden kontrol 2" GEÇER sonrası)

Kontrolün iki küçük notu yalnız `planlama/proje-plani.md`'de uygulandı:

1. **Yarım haftalı B tarihleri bir gün ileri** (iki örnek tablosu): ilk sürüş 9.12 → **10.12** (H11) ve 23.12 → **24.12** (H13);
   kolların alt ucu 6.01 → **7.01** (16.11-B, "7–10.01") ve 20.01 → **21.01** (30.11-B, "21–24.01"); demonun alt ucu 20.01 → **21.01**
   (16.11-B, "21–24.01") ve 3.02 → **4.02** (30.11-B, "4–7.02"). Tablonun altındaki "Durum B'de demo hazır ≈ 20–24.01" cümlesi de
   aynı tarih olduğu için "≈ 21–24.01" yapıldı. H numaraları ve "sığar mı" sonuçları değişmedi; başka tarih değiştirilmedi.
   Yukarıdaki "Son sonuç" tablosu tur 2 kaydı olarak olduğu gibi bırakıldı; geçerli tarihler plandadır.
2. **A hazırlık takvimi:** 11–12.11'e sıkıştırılan kupon değerlendirmesi + CAD + STL dışa aktarma "varsayım (plandaki 0,5 haftalık
   aşama bir güne indirildi)" diye işaretlendi.
