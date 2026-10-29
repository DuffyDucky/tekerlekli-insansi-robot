# Y3 — M6 CAD erişim düzeltmeleri (tasarım ajanı günlüğü)

Brief: `planlama/y3/Y3-brief.md`. **Önce bu günlüğü oku, yapılanı tekrarlama.**

## Günlük
- 2026-10-29: Adım 0 bitti, `59367ab` (rampa freni ≤ 0,1; Pi 5 4 GB, maliyet genel 103.166,51). Y3 brief + günlük açıldı.
- `Y3_erisim.py` (yeni; M6_erisim.py ölçüm fonksiyonlarını kullanır, modül FCStd'lerini salt okur) önce koşusu (`Y3-erisim-once.json`):
  C1 göbek–horn 2 YOK (serbest 7,0, göbek plakası), S2 somun 2 YOK (y 34,75), dirsek 2 cıvata YOK (13,6, ön kol alt yan duvarı) +
  3 somun YOK, tilt 1 somun YOK → 125 cm M6 bulguları 1,65 m'de aynen geçerli.
- **C1 + C3 (omuz) bitti:** `arayuz.M6` (yeni dict) `gobek_horn_kanal` Ø5 x 168,5…200,5 (z +6 iki cıvata) ve `s2_somun_cep` (plaka altı
  blok x 174…196, y 32…39, z −2,5…2,5; DIN 985 altıgen cep s 7,2). `omuz_montaj` yeniden: 75 parça, statik 0, M6 pay aynı, göbek
  175,2 → 175,3 g. `Y3_erisim` sonra: göbek–horn 4/4 DÜZ, S2 somun 2 CEP + 2 açık ağız.
- **C2 (dirsek) bitti:** `arayuz.M6` `dirsek_kulak_erisim` (ön kol alt yan duvarında alt iki kulak cıvatası ekseninde Ø8) +
  `dirsek_somun_cep` (plaka −x yüzünde 4 altıgen cep bloğu, x 193,4…198,6, servo gövdesine 0,5 mm; üst bloklar R_KAFA zarfına kırpılı).
  İlk koşuda cep plakaya 0,05 mm oyuyordu ("somun plakaya dayalı" HATA) → cep derinliği plaka yüzünde bitirildi. `dirsek_montaj`:
  57 parça, ev pozu 0, bağlantı 22/22, ön kol desteksiz (çıkıntı 0,009), 399,7 → **400,5 g**, kablo OK; `dirsek-analiz.json` S2 satırı artık
  DS3235 1.770 mm (Y2b'nin Y4'e bıraktığı JSON yenilendi). `Y3_erisim`: dirsek 8 cıvata DÜZ, 8 somun CEP (önce 2 + 3 YOK).
- **C3 (kafa) bitti:** `arayuz.M6` `tilt_somun_cep`; `kafa/kafa7_parcalar.py` eğme çatalında ön kulak iki somunu için ön ağın üstünde cep
  bloğu (plaka −x yüzü, servo ön ucundan 0,5). `kafa_montaj`: 147 parça, ev pozu 0, bağlantı 29/29, tilt serbest −15…15 (arayüz artık
  ±13: kafa FCStd'si ilk kez ±13 ile üretildi), çatal desteksiz, 2.043,0 → **2.043,5 g**. `Y3_erisim`: tilt 2 CEP + 2 açık ağız (önce 1 YOK).
  Kafa'da Pi parça adı artık "Raspberry Pi 5 4GB + Active Cooler" (Adım 0 kaynağı).
- **C1–C3 özeti:** 125 cm'deki erişilemez bağlantılar modülde 10 / robotta 19 (`M6-montaj-sirasi.md:38`; modülde göbek–horn 2, S2
  somun 2, dirsek 2 + 3, tilt 1; iki kolla 19, hepsi C1–C3'e düşer; önceki "12" aritmetik hataydı, Y3 kontrolü a) → 0 YOK
  (`Y3-erisim-once.json` / `Y3-erisim-sonra.json`).
- 29.10 (oturum sınırından sonra devam; durum doğrulandı: `59367ab` var, C1–C3 dosyaları çalışma ağacında). **Kabuk (sürüyor):** `arayuz.M6`
  K1 `govde_braket_m5` (ISO 7380 M5×16 dışarıdan + M5 perçin somun, ısıl gömme M5 + DIN 912 + pul kalkar), K2 `etek_braket_m3` (M3×14 ISO 7380
  + M3 perçin somun, boss r 5,5), K3 `s1_ped_yarik_r_ic` 41,5, K5 `etek_kapak_h1`, K6 `etek_kapak_h2`, K7 `ana_anahtar_delik_d` 30 (tahmini),
  K4 `arka_kapak_ust` (henüz uygulanmadı). `kabuk_lib.percin_somun`, `kabuk_parcalar` (boss / delik / elemanlar / kapak parçaları),
  `kabuk_montaj` braket kontrolü perçin somuna göre + kapak cıvatası kontrolü. Koşu sırada.
- **Taban (kod hazır, koşu sırada):** `arayuz.TABAN` `xl_kafa` (XL4016 C, güç paneli üstü (97,5; 0), akünün önünde) + `on_sarj_karti`
  (K2 JQC-3F + 5,6 Ω 11 W + 1N4007, pertinaks 70 × 50, (−97,5; −1)) + iki yeni bölge; XL4016 / dağıtım kartı adları A sağ kol / B sol kol
  (pan / tilt kol hatlarından çıktı); `taban_parcalar` panel delikleri + `kart_burclu` ile iki kart. `elektrik.md` CAD cümleleri güncellendi.
- **K4 kodu yazıldı** (ilk kabuk koşusu K4'süz başlamıştı): `KAPAK2` (x ±75, y 1100…1268, üst kenar 1268 dikişinde alın), 1268 dikişi arka
  bindirme ±93 / ±120, göğüs arkası x0 cıvataları (1130 / 1215) kaldırıldı, kapak çevresine 7 bindirme adayı. Kabuk yeniden koşulacak.
- Kabuk 1. koşu (K4'süz): 301 parça, braket 14/14, kapak cıvatası 8/8, bindirme 79/79, baskı hepsi desteksiz; **2 sorun:** (a) H1 deliği
  x ±44 etek dolgu şeridini (x ±38) ikiye bölüyordu → delik x ±32; (b) M5 ISO 7380 başı eğik duvarda (y 400 / 1165) kabuğa 2,4–3,5 mm³
  giriyordu → dış yüzde Ø(dk + 1) × 0,3 mm oturma (`arayuz.M6 oturma_derin`), baş oturmada. 2. koşu (K4 dahil) sürüyor.
- **Taban bitti:** `taban_montaj` 355 parça, iç çakışma 0, bağlantı **127/127** (önce 119; +8 burç bağlantısı), taban × kabuk 0, bölge 48 / 0
  ihlal, **7.909,8 g** (önce 7.795,7; XL4016 C + ön şarj kartı + burç / vida). Devrilme ev: ileri 3,74 / geri 3,24 / yan 4,07, rampa 5° geri 2,38.
- **Kabuk bitti (2. koşu, K1–K7 hepsi):** 312 parça (baskı 28: +üst arka servis kapağı, etek kapağı H1 / H2), geçersiz 0, çoklu katı 0,
  kabuk içi çakışma 0 (767 çift), iskelet 0, bölge 51 / 0 ihlal, braket 14/14 (perçin somun kontrolleri), kapak cıvatası 8/8, bindirme
  **84/84** (önce 79; üst kapak çevresi + 1268 ±93), bindirme boşluğu en az 0,188 (≥ 0,15), 28 baskı parçasının hepsi desteksiz ve tablaya
  sığıyor, **6.116,6 g** (önce 6.074,6). Ana montaj (BOM) sırada.
- **Ana montaj bitti:** `ana_montaj` 1.120 parça (önce 1.073), 22 eklem, solve 0, STEP 1.120 katı, **24.554,3 g** (önce 24.396,1),
  AM (−0,08; 525,81; −12,49); `robot-bom.csv` 144 kalem (bağlantı 856, baskı 66, satın 175). BOM farkı: + M5×16 ISO 7380 8, M5 perçin
  somun 8, M3×14 ISO 7380 6, M3 perçin somun 6, XL4016 3 → 4, ön şarj kartı 1, 3 kapak, naylon burç +8, M3 ısıl gömme +7, M3×6 ISO 7380 +13;
  − M5×10 8, M5 pul 8, M5 ısıl gömme 8. `yerlesim_kontrol`: ev pozu S2 5 çakışma 0, kol kaba 40 poz 0, kafa 15 poz 0.
- **Maliyet:** `maliyet.json` adetleri yeni BOM'dan (+ pay); M6 koşullu satırlarından perçin somun, perçin aleti, M5×16 artık toplama giriyor,
  M3×8 (K2) satırı ISO 7380 M3 satırına (×14) birleşti, "servis kapakları bağlantısı" ve "M4 ısıl gömme" (altıgen cep seçildi) silindi.
  `maliyet_toplam.py`: 99 kalem, ara 90.232,68, **genel 103.767,58 TL** (Adım 0 sonrası 103.166,51; +601,07), koşullularla 109.056,64.
  `demo_uret.py` koştu. README, proje planı, sipariş farkı notu, `duzeltme-plani` M6, `M6-montaj-sirasi.md` notu güncellendi.
- **Y4'e kalan:** tam çakışma taraması (`carpisma_kos.py`), `M6_erisim.py` / `M6_ek.py` 1,65 m'e uyarlanıp yeniden koşusu (adım
  seçicileri 125 cm y eşikleri içeriyor), `dirsek_montaj` kabuktan sonra yeniden (S1 kontrolü K3 öncesi kabuğa karşı koştu; yarık yalnız
  malzeme kaldırır), `baski-listesi.md` (66 parça), `kabuk_rapor.py`, görseller / rapor.html, `taban_montaj` tüketim tablosundaki "A sağ kol
  + pan / B sol kol + tilt" etiketleri (sayılar E8'de Y2b-aku.py'den). Y4 / Y6: OZET.md, taban_rapor.py, Lale-Proje-Ozeti.txt, 05-fiyat.
- 29.10: Y3 tasarım işi bitti → tek commit (bağımsız kontrol sırada).
- **29.10 kontrol düzeltmeleri** (`Y3-kontrol.md` "Düzeltilecek" 1–5; Duffy kararı bekleyenlere dokunulmadı):
  1. C1: `arayuz.M6 gobek_horn_kanal` d 5,0 → **6,0** (M3 DIN 912 başı Ø5,5 + 0,25 radyal pay). Komşu geometri: kanal ekseni z 6,01, plaka
     z 2,5…7,5 → kanal altında plaka eti 0,51 mm (Ø5'te 1,01; x 168,5…174,5 ve 195,5…199); iki kanal arası (y ±3) 6 mm, S2 kulak
     deliklerine 3,5 mm, havşa Ø6,6 ile örtüşme aynı. Göbek +X basılıyor: 0,51 mm et dikey ince duvar, dilimleyici atarsa kanal alttan açık
     yarık olur; taşıyıcı değil (plaka şeridi y −3…3 ve dışında tam), işlev değişmez → z −6 seçeneği gerekmedi. Takma taraması (kontrol
     betiği, scratch): dört cıvata baş yönünde 0…45 mm kaydırıldı, göbekle ortak hacim **0 mm³** (önce z +6 ikisi 7,5 mm'de değiyordu,
     8–14 mm'de 8,56 mm³). Yeniden: `omuz_montaj` (75 parça, statik 0, göbek 175,3 → **175,1 g**), `iskelet_montaj`, `dirsek_montaj`
     (göbek kütlesi / AM), `ana_montaj` (1.120 parça, solve 0, STEP 1.120, **24.554,1 g**, AM (−0,08; 525,80; −12,49); BOM yalnız göbek
     118,7 → 118,5 g, maliyet etkilenmez), `taban_montaj` (bağlantı 127/127, çakışma 0, bölge 48 / 0; robot satırı artık 1.120 parçalık
     montaj-analiz'den: tabansız 778 parça, ev devrilme ileri / geri / yan 3,74 / 3,24 / **4,08**, rampa 5° geri **2,37**),
     `yerlesim_kontrol` (ev S2 5 0, kol 40 poz 0, kafa 15 poz 0), `Y3_erisim` sonra (göbek–horn 4 DÜZ; sayaçlar aynı).
     README AM satırı 525,80. Not: `iskelet-analiz.json` Y3 öncesinden kalmıştı (bölge 55 → 57; ihlal 0); `taban-analiz.json` robot
     satırı Y3 commit'inde 1.073 parçalık eski montaj-analiz'e dayanıyordu (tabansız 757), şimdi güncel.
  2. `elektrik.md:24` S2 cümlesi: JSON Y3'te yeniden üretildi, 1.770 mm.
  3. "12 YOK" → modülde 10 / robotta 19: `dongu.md` Y3 satırı ve bu günlükteki C1–C3 özeti.
  4. `adim4/M6_erisim.py` `ISO7380_S` + `"M5x": 3.0` (ISO 7380-1 M5 altıgen yuva 3 mm). Kısa koşu (scratch): `alet()` BOM'daki ISO 7380
     kodlarında önce M5×16 × 8 atlanıyordu, şimdi alyan 3; kabuk FCStd'de 8 M5×16 → 8 DÜZ (alyan 3,0). Tam koşu Y4'te.
  5. `elektrik.md` sigorta seti paragrafı: hat yuvaları 7,5 A × 2 + 5 A (C) + şarj 10 A, yuva × 4, ek bıçak sigorta 6 (`maliyet.json` ile aynı).
