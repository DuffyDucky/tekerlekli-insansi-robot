# T2: 3. adım takip düzeltmesi (tasarım ajanı)

Başlangıç: 2026-10-15. HEAD `7c87ff4`. Kaynak: `K3-kontrol.md` "Hatalar" (bölüm 2 E-1/E-2, 3 kalıntı, 4 ısı, 6 belge).
Durum: **TAMAMLANDI** (15 Ekim 2026). Commit yok; tam çakışma taraması ve ana montaj koşulmadı (kapsam dışı).

## Durum
- [x] 1. ESP32 USB kablosu tek tarif (VBUS'ta seri 1N5819)
- [x] 2. Eski Pi metinleri (taban_rapor.py, arayuz.py Pi/MAX98357A bölgeleri)
- [x] 3. elektrik.md notları (Pololu, diyotlu VEYA, DTR/RTS, ön şarj, PC817 3,3 V)
- [x] 4. Kafa ısısı (çıkış yarıkları üst/arka üst, perde, tahmin yeniden)
- [x] 5. JGB37 riski (9 kg·cm senaryosu) riski (9 kg·cm senaryosu)
- [x] Kafa ve taban yeniden üretim + kontroller + rapor

## Günlük
- 2026-10-15: dosya açıldı.
- 2026-10-15: G1 betik metinleri: `kafa_montaj.py` pi.boyun_kablolari, `kafa_parcalar.py` kablo demeti notu, `kafa_rapor.py` kablo yolu notu, `taban_parcalar.py` kablo yolu 12 adı → "VBUS hattında seri 1N5819". JSON/rapor yeniden üretimde düzelir.
- 2026-10-15: G2 `taban_rapor.py` 158/178/220/222/349 güncellendi (Pi + amfi kafada; arayüz/dağıtım kartları bağlantı satırı eklendi, MAX98357A satırı çıktı). `arayuz.py` BOLGELER: Pi 5 ve MAX98357A (elektronik kati) kaldırıldı. Okuyanlar: `taban_montaj.py` (taban bölgeleri ↔ iskelet/kabuk, ihlal sayımı; 48 → 46 bölge), `kabuk_montaj.py` (bölge ↔ kabuk; yalnız raporlama), `iskelet_rapor.py` (tablo), `carpisma.py` (taban KONTROL'de olduğu için taban bölgeleri zaten hariç). Kaldırmak kontrol bozmuyor. ESP32/PCA9685 bölgeleri de eski V3 yerinde (kapsam dışı, açık iş).
- 2026-10-15: G5 `T2_donus_9kg.py` (donus_hesap import, arayuz değişmez): 9 kg·cm'de yerinde dönüş 12,1/14,9/17,7 kg·cm = durmanın %134/165/197'si (motor durur, dönemez); üst sınır %194–285; ön omni 2,6–2,9 kg·cm = sürekli 2,7'nin ×0,95–1,08 (sınırda); omni ile düz gidiş çekişmesi ×0,68–1,08.
- 2026-10-15: G4 CAD: giriş arka alt bant y 185–220 (önce 192–227), çıkış arka üst bant y 234–261 (8 yarık) + yan duvar en üst 2'şer (y 234–246), toplam alanlar aynı (1.200 / 1.440). Emiş perdesi (arka kabukla tek parça, x −45…48, y 221–223, z −63…−5). Isı modeli: doğal çekiş (baca) + duvar kaybı ve iyimser fan sınırı; kafa_rapor tablo güncellendi. Yeniden üretim bekliyor.
- 2026-10-15: G3 elektrik.md: Pololu (5,5 A 36 V'ta; 3,5–8 A tüm giriş aralığı, 12 V eğrisi teyit), ESP32 diyotlu VEYA (özet + E4), PC817 3,3 V notu + doğrudan PC817 2,2 kΩ yedeği, E3'e DTR/RTS ve ön şarj (E9) maddeleri, açık işler 9–13. G5 uyarısı E0'a ve T-taban-guc-pi.md açık sorun 1'e.
- 2026-10-15: Üretim: kafa_montaj (145 s), kafa_gorsel (GUI), kafa_rapor; taban_montaj (68 s), taban_rapor. taban_gorsel koşulmadı (taban geometrisi değişmedi).

## Sonuç

| Kontrol | HEAD | Şimdi |
|---|---|---|
| Kafa parça / kütle | 115 / 1.431,3 g | 115 / 1.443,5 g (arka kabuk 263,1 → 275,3: perde) |
| Kafa bağlantı, ev pozu çakışma, bağıl boşluk | 44/44, 0, hata 0 | aynı (JSON `baglanti_kontrol`, `bagil_bosluk`, `tarama`, `r62`, `statik` HEAD ile birebir) |
| Tilt / pan serbest, çarpan poz kümesi | −25…40 / ±180 | aynı |
| Tilt torku, pay | 4,64 kg·cm, 2,03 | 4,67 kg·cm, 2,01 |
| Arka kabuk baskı | desteksiz 0 sorun | aynı |
| Taban parça, bağlantı, çakışma, iskelet/kabuk | 316, 119/119, 0, 0/0 | aynı (tek parça farkı: kablo yolu 12 adı) |
| Taban bölgeleri | 48, ihlal 0 | 46, ihlal 0 |
| Robot ev pozu | 21,71 kg, AM y 372,4 | 21,73 kg, AM y 372,9; E0 tablosu aynı |
| Kafa ısısı (tipik, 30 °C) | yarıklı 36–40 (iyimser) | doğal çekiş 43,6 → 42,8; dürüst aralık 34–43 °C |

## Açık sorunlar
1. `arayuz.py` BOLGELER: ESP32 ve PCA9685 (elektronik kati) bölgeleri de eski V3 yerinde (akü üstü); bu işin kapsamı dışında bırakıldı. Taban çizili olduğu için çakışma taramasına girmiyor; yalnız `taban_montaj` bölge ↔ iskelet/kabuk kontrolünde (ihlal 0).
2. `kabuk-analiz.json` Pi/MAX98357A bölge satırları kabuk_montaj yeniden koşunca düşer (kabuk başka ajanda).
3. Perde ve yarıkların ısı etkisi ölçülmeli (tahmin aralığı geniş); Active Cooler hava yönü kafada test edilmeli.
4. JGB37: ölçüm omni siparişinden önce; 9 kg·cm çıkarsa omni de sınırda.
5. `carpisma-sonuc.json` taban ve kafa bölümleri eskidi (tam tarama 6. adımda).
