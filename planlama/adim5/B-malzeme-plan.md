# 5. adım: malzeme listesi ve plan (B1, B2, B3, E8, E9, D6) — Opus-9 / Opus-10 günlüğü

Başlangıç: 2026-10-15 ~14:35. CAD dosyalarına (`tasarim/freecad/`) dokunulmadı (S1 kontrolü ve M6 CAD sürüyor). Sipariş yok, commit yok.
Kesinti olursa bu günlükten devam edilir.

## Durum
| İş | Durum | Not |
|---|---|---|
| Okuma | ✅ | CAD BOM toplamı `bom_say.py` → `bom_toplam.json` (iskelet + taban + kabuk + kafa + 2 × omuz − travers + dirsek iki kol) |
| B1 eksik kalemler | ✅ | `maliyet_duzelt.py`; kanıt `raporlar/kaynaklar/05-fiyat-arastirmasi.md` bölüm 6 |
| B2 adet/sürüm | ✅ | aynı betik |
| B3 öneri | ✅ | aşağıda (yalnız öneri, maliyete girmedi) |
| E8 akü süreleri | ✅ | `e8_aku.py` → `e8-aku.json`; `adim3/elektrik.md` E8 bölümü |
| E9 sigorta + ön şarj | ✅ | `adim3/elektrik.md` sigorta listesi + E9 bölümü |
| M6 koşullu kalemler | ✅ | 6 kalem, `secenek: kosullu`, `kosullu: "M6 CAD"` |
| D6 belgeler | ✅ (OZET hariç) | proje-plani, yazilim-plani, baski-listesi. `tasarim/freecad/OZET.md` ekran kararı satırı: yazma alanı dışında, açık |
| Maliyet sayfası üretimi | ✅ | `tasarim/cad/demo_uret.py` → `tasarim/Robot-Tasarim-Demosu.html` (yalnız maliyet JSON satırı değişti) |

## Sonuç

### Maliyet (V3, yazıcı, yedek dahil, %15 pay; `maliyet_toplam.py` sayfanın `calc()` hesabını tekrarlar)

| | Önce | Sonra |
|---|---|---|
| Kalem (dosyada / V3'te görünen) | 70 / 70 | 118 / 97 |
| Ara toplam | 74.193,69 TL | 86.215,20 TL |
| **Genel toplam (koşullular hariç)** | **85.322,75 TL** | **99.147,48 TL** |
| **Koşullular dahil** (omni, fan, M6 CAD) | **90.551,80 TL** | **105.053,19 TL** |

- 48 yeni kalem (42 normal, bunların 3'ü sürüm değişimi: Nextion, Victron, V3 baskı hizmeti; 6 M6 koşullu) + 14 mevcut kalem düzeltildi
  (`"adim": "5"`; 3. adım kalemleri değiştiyse `"3+5"`).
- Farkın büyüğü: Victron (K3) +7.967; Nextion (K2) −3.172; PETG-CF 1 → 1,5 kg +1.106; PETG +1 makara +389; kargo 7 → 12 sipariş +600;
  geri kalan B1 (vida, ısıl gömme, rulman, horn, servo uzatma, röle, ön şarj vb.) ≈ +5.100.
- B2: sigma 2,7 → 3 m (kesim planı), T-somun 40 → 50, M6×16 40 → 18 (+ M6×14 30, M6×20 2), M5×40 burç 4 → 8, servo braketleri ve
  YSB vida setleri `ver: v1,v2`, Waveshare 10,1" `v2` → Nextion `v3`, Limacell `v1,v2` → Victron `v3`, baskı hizmeti V3 6,0 kg,
  lazer plaka 340×500 → 270×500, kontrplak 2 parça, HDMI adedi 1 (Nextion UART; değişmedi, not eklendi), acil stop modeli uyuşmazlığı not.

### E8 (Victron 256 Wh × 0,81)
Boşta 19,0 W → 10,9 sa · normal 36,3 W → 5,7 sa · **yoğun 104,4 W → 2,0 sa** (omni ile 2,3) · ders karışımı 5,7 sa · fuar karışımı 5,1 sa.
Planın "≈ 2,5 sa"i 307 Wh içindi (24 Ah ile 2,4 sa). 8 saat fuar 400 Wh (31 Ah) ister: öğle şarjı ya da 2. akü.

### E9
İkinci 5 A (F4) + 2 A (F5) standart bıçak, şarj girişi 10 A mini + 3. kapaklı yuva. Ön şarj: **K2 rölesi (12 V 7 A) + 5,6 Ω 11 W taş direnç,
K1'e paralel kol, F1 sonrası**; bobin mantar NC sonrasından, ikinci IRLZ44N, GPIO2; 300 ms ön şarj, tepe 2,6 A, τ 11 ms (bara ≈ 2 mF tahmini,
ölçülecek), hata durumunda ≤ 1 s. Kalıcı paralel direnç (acil stopu deler) ve NTC (ısı, hızlı yeniden devreye almada etkisiz) reddedildi.

### B3: ucuz eşdeğerler (yalnız öneri)

| Kalem | Şimdi | Eşdeğer | Fark | Bedel / risk |
|---|---|---|---|---|
| Akü | Victron 12.680,70 | Limacell 24 Ah 4.746,02 | −7.935 | Akü raporu kuralı: ≤ 186 × 79 × 172 mm ve M5/M6 kutup yazılı teyit edilirse. Özel üretim, iade yok |
| Amfi | Adafruit MAX98357A 728,81 | Amazon muadil 227,23 | −502 | Kart ölçüsü/delikleri farklı olabilir (kafa içi, köpük bantla) |
| Isıl gömme M3 | 125 × 5,22 = 652,50 | Hobi Mekatronik M3 × 5,3 × 6, 100'lü 350 TL (+25'li) | ≈ −215 | Dış çap 5,3: CAD deliği Ø4,0 değişir, kupon C ile seçilmeli |
| Ana röle | Elo mini 40 A 166,32 | Kartal mikro 40 A 56,70 | −110 | Mikro ISO gövde/soket farklı; stok "gelince haber ver" |
| Servo horn | Robiz 10 × 82,32 | AliExpress 10'lu ~2–4 USD | ≈ −700 | Teslim 2–4 hafta, Parti 2 horn ölçüsünü geciktirir |
| M3 imbus | adet 1,30 | cabacivata 250'li paket (M3×8 191,84 + KDV) | küçük | Paket fazlası |
| Pololu D36V50F5 | 1.952,68 (ithal) | Türkiye'de ≥ 5 A, ≥ 24 V girişli korumalı 5 V modül | olası −1.000 | Ters gerilim / aşırı akım koruması aranmalı (elektrik.md açık iş 8) |
| Göğüs ekranı | Nextion 9.154,91 | Waveshare 10,1" (E) 6.607,48 | −2.547 | K2 kararı Nextion; seçilirse göğüs bandı yeniden çizilir, HDMI + Pi USB gerekir. Önerilmez |

### CAD adet / tutarlılık bulguları (yalnız liste; `tasarim/freecad/` değişmedi)
1. `taban-bom.csv` akü "LiFePO4 12,8 V 24 Ah" → Victron 12,8/20 (K3); `arayuz` akü kütlesi 2,8 → 3,0 kg.
2. `taban-analiz.json` `aku`: 307 Wh, × 0,80, röle 0,3 W (E8 tablosuyla değiştirilmeli; OZET süreleri de).
3. `taban-bom.csv` acil stop Emas **B200E60 (60 mm)** + kontak bloğu; maliyette B200E-E 40 mm (satır korunup not düşüldü).
4. Ön şarj K2 + 5,6 Ω direnç ve ikinci IRLZ44N taban CAD'inde/BOM'da yok (güç paneli, 6. adımda eklenmeli).
5. `taban-bom.csv` "(BOM'da yok)" notları (röle + soket, pertinaks) artık maliyette: metin eskidi.
6. FCStd `Malzeme`: omuz 4 parça (M4 açık 2) ve dirsek çatalı (M7 kupon README "şu an PETG") PETG yazıyor, PETG-CF olmalı.
7. `omuz_parcalar.RHO` %60 doluluk (M4 açık 1): omuz kütlesi kol başına 43–58 g eksik.
8. Düzeltme planının "T-somun 40 → 18" maddesi eskiydi: CAD 50 (iskelet 8, taban 18, kabuk 14, omuz 8, kafa 2).
9. CAD 25T horn **disk** tipi, Türkiye'de yalnız kol tipi bulundu; delik dizilimi horn gelince ölçülmeli (zaten Parti 2 şartı).
10. CAD ısıl gömme deliği Ø4,0 ruthex M3 × 5,7 (OD 4,6) için; Türkiye'de bulunan insertler OD 4 / 5 / 5,3.

### Doğrulanamayan fiyatlar (tahmini, notta "fiyat doğrulanmadı")
İç köşe bağlantı (45×45 fiyatı), Al bükme braket, 25T horn (kol fiyatı), servo uzatma (sayfa tükendi), JR seti, röle soketi, XT60 tutucu,
M5 pabuç, M2,5 distans seti, cırt kayış, kablo bağı + taban, bıçak sigortalar ve yuvaları, Bluetooth gamepad, M5 ısıl gömme (ölçü),
vida kalemleri (kategori taban fiyatı, boya göre ayrılmıyor), M6 koşullu perçin somun + alet + M4 ısıl gömme.

## Dosyalar
- `planlama/maliyet.json`, `tasarim/Robot-Tasarim-Demosu.html` (üretildi), `raporlar/kaynaklar/05-fiyat-arastirmasi.md` (bölüm 6)
- `planlama/adim3/elektrik.md` (sigorta listesi, E8, E9), `planlama/baski-listesi.md`, `planlama/proje-plani.md`, `planlama/yazilim-plani.md`
- `planlama/adim5/`: `bom_say.py` + `bom_toplam.json`, `baski_toplam.py` + `baski_toplam.json`, `e8_aku.py` + `e8-aku.json`,
  `maliyet_duzelt.py` (bir kez koşar), `maliyet_toplam.py`

## Günlük
- 14:35 Dosya açıldı.
- ~15:00 Okuma bitti. Önce toplam (V3, yazıcı, yedek dahil, %15 pay): ara 74.193,69 → genel **85.322,75 TL**;
  koşullular dahil 90.551,80. Bulgular:
  - maliyet hâlâ **Limacell 24 Ah** (K3 Victron) ve **Waveshare 10,1"** (K2 Nextion) diyor → B2'de uygulanacak.
  - Vida setleri Robolink **YSB** (yıldız başlı); CAD DIN 912 imbus + ISO 7380 + DIN 913 + DIN 985 + ısıl gömme kullanıyor.
    CAD sayımı: M3 DIN 912 178, M3 ISO 7380 63, M2,5 24, M4×16 51, M5 17, M6 46 + set 16+8, ısıl gömme M3 109 / M5 9,
    M6 çekiç somun 50, M4/M5 çekiç 8+8, kontra somun M3 4 / M4 36(+3 naylon).
  - T-somun: plan "40 → 18" diyordu; güncel CAD M6 çekiç somun **50** (iskelet 8, taban 18, kabuk 14, omuz 8, kafa 2).
  - Servo braketleri (çok amaçlı ×2, uzun U ×1) V3 CAD'de yok → `ver: v1,v2`.
  - Kontrplak V3'te 2 parça 270×226 + 270×274 (5 mm huş); Al: alt plaka 270×500 + boyun plakası.
- 2026-10-15 (devam, Opus-10) Önceki ajan limitte kesildi; günlükten devam. `bom_say.py` yok, `planlama/adim5/` altına yeniden yazıldı.
- (Opus-10) `bom_say.py` → `bom_toplam.json`; sayılar önceki günlükle birebir. Ek CAD bulguları: röle K1 + soket, ESP32 taşıyıcı pertinaks
  (4. kart), M2,5 pirinç burç 8 + kafa burcu 4, cırt kayış 2, Al bükme braket 6 + 4, 6808 ×4, 625ZZ ×5, horn ×10, iç köşe 8 + M6×10 set 16,
  M5×16 set 8. Sigma CAD 2.570,5 mm, 3 × 1 m çubuk.
- (Opus-10) Fiyat araştırması (05-fiyat bölüm 6). Baskı toplamı (`baski_toplam.py`): 50 parça, 5,96–6,02 kg (PETG 5,01, CF 0,96–1,02), 124–125 sa.
- (Opus-10) `maliyet_duzelt.py` uygulandı (yedek: %TEMP%/maliyet-once.json); 3. adım kalemlerinde `adim` "3+5" yapıldı. Toplamlar yukarıda.
- (Opus-10) elektrik.md sigorta + E8 + E9; 05-fiyat bölüm 6; demo_uret; proje-plani (tek takvim H1 = 28 Eyl, SolidWorks/V1 izi temizlendi);
  yazilim-plani (+2 hafta, Y8, 3. adım kuralları, Nextion, `arm`/`reset` mesajları); baskı listesi (M4, S1 kaset + tambur, eğme çatalı
  notu, Nextion/Victron, 50 parça). Bitti.
