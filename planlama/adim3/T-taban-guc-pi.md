# T: 3. adım tasarım ajanı (taban, güç, Pi kafada)

Başlangıç: 2026-10-15. Durum: **TAMAMLANDI (tasarım)**; kontrol/regresyon/ana montaj ayrı ajanın ve 6. adımın işi. Kararlar: `elektrik.md`.

## Durum
- [x] Okuma (CLAUDE.md, README, düzeltme planı, döngü, P, B, betikler, maliyet, akü raporu)
- [x] E0 dönüş yükü hesabı (taban/donus_hesap.py, arayuz.TABAN['donus']) — omni CAD bayrağı hazır (TABAN_OMNI=1 / arayuz.TABAN['omni']['aktif'], varsayılan kapalı)
- [x] E1 servo beslemesi bölme + taban CAD (XL B = eski Pi XL'i, dağıtım kartı A/B; montaj koşusu bekliyor)
- [x] E2 sensör / ADC / acil stop okuma
- [x] E3 acil stop yeniden başlatma
- [x] E4 Pi 5 beslemesi (kafada 5 V/5 A)
- [x] K4 Pi kafada CAD (kafa modülü) + taban Pi yeri boşaltma (kafa_montaj koştu)
- [x] E7 etek içi ısı
- [x] elektrik.md
- [x] maliyet.json kalemleri
- [x] Taban ve kafa üretimi + kontroller + görseller + raporlar

## Günlük
- 2026-10-15: dosya açıldı.
- 2026-10-15: okuma bitti. Kararlar (taslak): E0 iki modelle (Coulomb sürtünme dairesi = ana, 'yan tam μN + Wong μt(R)' = üst sınır), sabitler arayuz.TABAN['donus']'a; ayrı saf Python modül taban/donus_hesap.py. Pi'nin XL4016'sı servo B (sol kol) olur (XL sayısı 3 kalır). Sonar: 4,7k/10k bölücü. Acil stop durumu: PC817 optokuplör. Kafa: Pi P raporundaki konum (köşe x -34, z +1, alt y 189), 5 V çevirici tabla sol-önde.
- 2026-10-15: E0 hesap modülü bitti (`tasarim/freecad/taban/donus_hesap.py`, saf Python). Yerinde dönüş (Coulomb + lastik kayma c 0,05, ev pozu 21,61 kg, AM z -14,4): μ 0,4/0,5/0,6 → en çok 12,1/14,9/17,7 kg·cm (arka teker), sürekli 6,3'ün ×1,91/×2,36/×2,81, durma 21'in %57/71/84; akım 1,7–2,4 A/motor (tahmini). Üst sınır (yanal tam μN, Wong): 17,5/21,6/25,6 (μ 0,5–0,6'da durmayı aşar). Yay (R ≈ 1,1 m) yalnız %10–15 düşürür. Ön omni (teker düzlemi aynı x 178): 2,6–3,2 kg·cm (×0,41–0,51), dönme merkezi arka aks ortası. Omni Ø127 / teker Ø125: düz giderken önler %1,6 hızlı, ön motorlara +~1,3 kg·cm çekişme. Omni farklı x'te (163,5) olursa ön/arka birbirine karşı çalışır → omni aynı düzlemde, göbek adaptörüyle.
- 2026-10-15: taban CAD düzenlendi (arayuz.TABAN: xl görevleri, arayuz_karti, servo_dagitim, donus, omni; BOLGELER: Pi fan payı kalktı, dağıtım + E7 fan yeri eklendi). taban_lib: omni_local, arayuz_karti_local, servo_dagitim_local. taban_parcalar: Pi + amfi çıktı, arayüz kartı + 2 dağıtım kartı, omni bayrağı, kablo yolları. taban_montaj: donus (E0), kafa kütle düzeltmesi (montaj-analiz eski), TUKETIM hatları. Import testi: 316 gerçek parça, 7.529,4 g (önce 292 / 7.493,4), geçersiz 0; omni açık: 8.209,4 g (+680 g), geçersiz 0. Omni Ø127 aks aynı → zeminden 1 mm aşağı (gerçekte ön 1 mm yükselir, 0,15° eğim).
- 2026-10-15: kafa CAD + kafa_montaj koştu (140 s). Parça 98 → 115, kütle 1.363,1 → 1.431,3 g (+68,2), AM (0,6; 133,6; 21,1) → (0,9; 136,4; 19,4). Bağlantı 44/44 (4 yeni burc_kart kontrolü), ev pozu çakışma 0, bağıl boşluk hata 0, tilt serbest −25…40 ve pan ±180 aynı, çarpan poz kümesi (aralık dışı) birebir aynı. Tilt: 926,6 g (25 g kafa içi kablo payı dahil), 4,64 kg·cm, pay 2,03 (önce 2,11; P tahmini 1,96). Pan pay 3,6. Isı: kapalı 39/45/49 °C (boşta/tipik/en kötü, 30 °C ortam), yarıklı (1,0–1,55 L/s) 34–42 °C. Yarık: giriş 1.200, çıkış 1.440 mm². Pi ↔ kafa iskeleti 6,6, ↔ arka kabuk 7,5 mm; tilt taramasında Pan/Gövde'ye en az 31,6 mm. Arka kabuk baskı desteksiz (0 sorun), 263,1 g.
- 2026-10-15: servo hatları dengelendi: A = sağ kol + pan (yoğun 4,4 A), B = sol kol + tilt (4,7 A); fan yeri üç XL'in ortasına (z 85–135). taban_montaj yeniden koştu (96 s): 316 parça, 7.529,4 g, bağlantı 119/119, çakışma 0, iskelet/kabuk 0, bölge ihlali 0. Omni varyantı da koşuldu (8.209,4 g, çakışma 0, teker–etek 10,55 mm < 12) ve varsayılan geri üretildi.
- 2026-10-15: `planlama/adim3/elektrik.md` yazıldı (E0–E4, E7, K4, blok şema, akım bütçesi, sigorta, pin taslağı). maliyet.json: 13 yeni + 2 değişen kalem (`adim: "3"`), V3 +2.767,28 TL (pay hariç); koşullu omni + fan 4.547 TL toplam dışı. demo_uret.py koşulmadı (kapsam dışı).
- 2026-10-15: görseller (kafa_gorsel, taban_gorsel; GUI) ve raporlar (kafa/rapor.html: "Raspberry Pi 5 kafada" bölümü; taban/rapor.html: "Dönüş yükü (E0)", yeni sigorta planı, yerleşim satırları) yeniden üretildi. Bitti.

## Sonuç

| Modül | Önce | Sonra |
|---|---|---|
| Taban | 292 parça, 7.493,4 g | 316 parça, 7.529,4 g (Pi + amfi −; arayüz kartı + 2 dağıtım kartı +); omni açıkken 8.209,4 g |
| Kafa | 98 parça, 1.363,1 g | 115 parça, 1.431,3 g |
| Robot ev pozu (taban_montaj hesabı) | 21,61 kg, AM y 370,2 | 21,71 kg, AM (−0,2; 372,4; −13,8); devrilme payı en az 3,0× aynı düzeyde |

Kontroller: kafa bağlantı 44/44, ev pozu çakışma 0, bağıl boşluk hatası 0, tilt −25…40 serbest (değişmedi), baskı 7/7 desteksiz; taban bağlantı 119/119, taban içi / iskelet / kabuk çakışma 0, bölge ihlali 0, teker–etek 12,0 (omni 10,55).
Koşulmayan: tam çakışma taraması (`carpisma_kos.py`), ana montaj, regresyonlar (6. adım). `carpisma-sonuc.json` taban ve kafa bölümleri eskidi.
Dokunulmayan: omuz, dirsek, kabuk, iskelet, montaj; `tasarim/cad/demo_uret.py` (maliyet sayfası) koşulmadı.

## Açık sorunlar
1. K1 ölçümü (μ, JGB37 durma torku/akımı) → `arayuz.TABAN['donus']`.
2. Omni açılırsa: etek ön teker boşluğu 10,55 mm (kabuk), `montaj/moduller.py` teker adı, göbek adaptörü teyidi, Ø127/Ø125 %1,6 hız farkı.
3. Etek arka bandına havalandırma yarıkları (kabuk), E7 ölçümü sonrası fan.
4. Hoparlör yeri (Duffy), mikrofon yeri CAD'de yok.
5. Pololu D36V50F5 TR'de yok (ithal) — eşdeğer arama.
6. Pin planı: ön enkoderlere pin yok (E5).
7. Röle bobini gerçek gücü (~1,8 W) akü hesabında 0,3 W (E8, 5. adım).
