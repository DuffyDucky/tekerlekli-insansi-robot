# Omni günlüğü: ön iki teker omni + PETG göbek adaptörü, CAD (K75)

Karar K75 (Ahmet, 23.11.2026): ön iki teker omni, arka teker / motor / enkoder aynı. Bu dosya CAD işinin kaydı. Commit öneki `Lale omni`.
Dal `lale-duzeltme`. Ayrıntılı sayılar ve görseller: `tasarim/freecad/omni/rapor.html`.

## 1. 1. aşama (tasarım; commit `bc006c9`)

Özet commit mesajında: `arayuz.TABAN['omni']` (aktif; `TABAN_OMNI=0` lastik ön tekere döner), merkez tek değer `arayuz.OMNI_X` = 201,5
(lastik 216; ön iz 403, arka iz 432), `taban_lib.omni_local()` / `omni_adaptor_local()`, `taban_parcalar` ön köşeler + `TEKER_DONEN`,
`omni/omni_kontrol.py` (bağlantı 12 / 12, yeni parça × taban çakışma 0), `omni_gorsel.py`, `omni_rapor.py` → rapor taslağı.
Resmî tarama, taban ve ana montaj regresyonu 2. aşamaya bırakıldı.

## 2. 2. aşama (kontrol ajanı, 23.11.2026)

Başlangıç: HEAD `bc006c9`, yerel = uzak değil (iki commit push edilmemiş: `bf81903`, `bc006c9`). FreeCAD kilidi alındı, iş sonunda boşaltıldı.
Omni öncesi değerler `git 4bc73de` dosyalarından okundu.

### 2.1 Bağımsız doğrulama (ölçülen; `omni/omni_dogrula.py`)

- 1. aşama betiği yeniden koşuldu: `omni-kontrol.json` süre dışında birebir. Lastik geri dönüşü 427 parça (414 + 13), 148 bağlantı, 8.272,5 g;
  427 parçanın hepsi omni öncesi `taban-analiz.json` ile birebir (ad + sıra; hacim, kutu, kütle).
- Omni kipi: 453 parça (440 gerçek), 156 bağlantı hepsi tamam (omni 10 + kaplin-mil 2), taban 9.025,8 g (+753,3 g).
- x zinciri (sağ ön): braket 139–172,5, kaplin 174,5–204,5, adaptör 179–210,5, omni 187–216, merkez 201,5.
  **Düzeltilen iddia:** adaptör kaplini 17,5 değil **25,5 mm** kavrar (17,5 teker oturma yüzünün kaplin ucuna uzaklığı); `arayuz.py` yorumu düzeltildi.
- Dönen grup (`TEKER_DONEN`, kaplin hariç) 0–345° / 15°: ön köşe çakışma 0; en yakın motor M3 başları 3,5, alt plaka köşesi 6,08, braket 6,5 mm
  (motor gövdesi 3,05: mil ucu ↔ altıgen yuva, birlikte döner, gerçek açıklık değil). Ölçüt: projede yazılı kabul yok; kabul edilmiş arka
  lastik köşe emsali kaplin ↔ braket 2,0, M3 başı 3,79 mm. Ön köşe bu emsalin üstünde: geçer. `carpisma.py` 5 mm'si yakınlık eşiği, kabul değil.
- Teker ↔ etek önde 11,0 mm (hedef 12; 1 mm eksik, çakışma değil; Ahmet'in kararı).

### 2.2 Düzeltmeler (kod)

- `taban/taban_montaj.py`: devrilme yamuk destek çokgeniyle (ön x `OMNI_X`, arka x 216); duruş eğimi 0,155° yalnız geri yöne eklendi;
  `robot.destek`, `robot.zemin` alanları. Lastik kipinde hesap eskisiyle aynı.
- `montaj/moduller.py`: teker grubu `taban_parcalar.TEKER_DONEN`'den (ön grup 17 parça: omni, adaptör, 4× M3×35 / pul / ısıl gömme somun, kaplin, M4, pul);
  eklem ekseni ve beklenen poz `teker_merkez_x`.
- `taban/donus_hesap.py`: Model A "ÜST SINIR" etiketi; Model C (motor hız-tork eğrisi, yan başına aynı PWM, ω 0,90 rad/s) eklendi.
- `omni/omni_dogrula.py`, `omni/omni_rapor_asama2.py` (yeni), `omni/omni_rapor.py` 2. aşama bölümleri.

### 2.3 Taban ve ana montaj (ölçülen)

- `taban_montaj.py`: geçersiz 0, iç çakışma 0 (782 çift), taban × iskelet 0 çakışma / 36 temas, × kabuk 0 / 1, bölge ihlali 0; adaptör baskısı geçti.
- Robot ev pozu: 26.276,1 → 27.029,4 g, AM (0; 520,5; −10,5) → (0; 507,7; −5,0). Devrilme payı düz ileri / geri / yan 2,46 / 2,19 / 2,71 →
  2,45 / 2,30 / 2,69; rampa 5° 1,88 / 1,61 / 2,13 → 1,87 / 1,72 / 2,11. En düşük (kol önde + 0,5 kg, rampa ileri) 1,45 → 1,44 (eşik 1,5'in
  altında, omniden önce de; bilgi pozu). Motor rampa 5° 6,90 → 7,10 kg·cm (1,095 → 1,127×).
- Ana montaj: 1.277 parça (1.251 + 28 − 2), kütle 25.876,1 → 26.629,4 g, AM (0,03; 526,2; −9,7) → (0,03; 513,1; −4,2); taban dışı
  837 parça birebir. Eklem doğrulaması (kafa yön denetimi atlanmış kopya; `eklem_dogrulama.py` bu dalda `kafa_parcalar.Y_CAM` yok diye
  duruyor, omniden bağımsız): yön 12 / 12 doğru, teker eklemleri en büyük sapma 1,6e-10 mm, solve 0.
- Regresyon: omuz ve iskelet regresyonu birebir aynı.

### 2.4 Resmî çakışma taraması

`carpisma_kos.py` 9 bölüm, 23.11.2026 15:41 başladı. **Statik bölüm tamamlandı** (18,8 s): ev pozu çakışma 0 → 0, S2 0° 4 → 4 (bilgi),
kutusu kesişen aday çift 904 → 930, ayrılmış bölge ve arayüz uyumu birebir, toplam 26.629,4 g. Omuz bölümü sırasında (≈ 15:49) koşu sistem belleği
azaldığı için durduruldu, yeniden başlatılmadı. `carpisma-sonuc.json` ve `carpisma-bolum/` değiştirilmedi (karışık sonuç olmasın); özet
`tasarim/freecad/omni/carpisma-statik-asama2.json`. Koşulmayan: omuz, kol_sag, kol_sol, kolkol, kafa_sabit, kafa_sag, kafa_sol, taban.
**Açık iş:** tam koşu (≈ 4 saat, boş bellekle), ardından `taban_rapor.py`, `montaj_rapor.py`, `omni_rapor.py` yeniden.

### 2.5 Yerinde dönüş (madde 7)

1. aşamanın "ön motor 7,62 kg·cm (1,21×), arka fren" rakamı Model A'dandı (sonsuz sert, eşit çevre hızı): ÜST SINIR. Yeni kütleyle A
8,03 kg·cm (1,27×). Model C (µ 0,5): ön 3,62 kg·cm (0,58×, PWM 0,636), arka 2,90 sürüş; ön 216'da 3,24; 9 kg·cm motorla 3,27 (1,21×).
MuJoCo (dokunulmadı): ONERI-ADAY 1,08–1,24× (21 kg·cm), 2,28–2,53× (9 kg·cm); ONERI (216) 0,97–1,11× / 2,12–2,36×.
Sonuç: merkez kaymasının bedeli küçük (+0,4 kg·cm C'de, +0,1× MuJoCo'da); asıl konu motor payının TAHMİN'e (durma, sürekli = 0,3 × durma)
bağlı olması. Seçenekler (karar değil): motor ölçümü, ara parçayla ön omni 216 (yan etek açıklığı 41 → 26,5 mm, konsol uzar), yazılım sınırı.
Tasarım değiştirilmedi.

### 2.6 Dokunulmadan bildirilenler

Web demosu / `robot.glb` (merkez 216, adaptör Ø40, ürün 14075; yeniden üretilmedi), `kod/ortak/robot_parametreleri.json` iz 0,432,
`kod/fizik/omni_teker.json` göbek deliği 6 ve kütle +606 g (CAD +753), `maliyet.json` satır 133, `rehber_metin.py` ≈ 172 (x ±178),
`lale158/kafa-yerlesim/uygulama_ivme.py` (`XC = _X_WH`), `taban_gorsel.py` (omni kipinde lastik adı arıyor), taban M6 parça adları
yinelenmiş, `montaj_gui_kontrol.py` sürükleme hatası (GOBEK None), `eklem_dogrulama.py` `Y_CAM`.
