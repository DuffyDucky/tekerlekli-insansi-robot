# F10n · P10.7b2f günlüğü: Kablo yolu 12 gerilemesi, uç etiketleri, küçük kare işleri

Açılış 16.11.2026 09:10 (uygulama ajanı; FreeCAD'siz). Taban: `lale-duzeltme` = uzak = `b5fc255` (P10.7b2e). Kaynak düzeyinde kapanış
16.11.2026 10:02 (saat okundu). Commit yok, push yok, FreeCAD ve tam üretim koşmadı. Sırada: bağımsız kontrol → üretim + zincir →
commit / push. Girdi: `planlama/d158/F10m-kare-inceleme.md` § 4, § 6; `planlama/d158/F10m-gunluk.md` § 14.

Dokunulmayanlar: CAD model dosyaları (`arayuz.py`, `taban_parcalar.py`, `kafa_*`, `taslak_*` …); K50 ile ilgili metin ve kayıt;
üretilmiş çıktı (`rehber/veri/`, `rehber/goruntu/`, `planlama/rehber/`, PDF); `sonuc-rapor.html` yeniden üretilmedi; eski kir
(`tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json`, depo kökündeki 0 baytlık `geometri_cikar.py`,
`geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`) olduğu gibi.

## 1. Tasarım kararları

1. **Kablo yolu 12 (p1191) kalıcı çözümü rehber tarafında kırpma.** `taban-analiz.json` `kablo_yolu[11]`'in 0–2 noktaları B01'in
   tabandaki yoludur (sol BTS7960B → ESP32 taşıyıcısı); 3. noktadan sonrası 05.11 öncesi ESP32 → kafa USB yoludur (artık U06, hub'dan).
   Modeli değiştirmek yerine (yasak: model dosyası) rehber verisi üretilirken parça `y ≤ 2. noktanın y'si + tüp yarıçapı`
   (190 + 2,5 = **192,5**) yarım uzayıyla kesişir. Kaynak tek yerde: `rehber_kablo.CAD_KIRP = {12: dict(son=2, gerekce=...)}`,
   `CAD_TUP_R = 2.5`, `cad_noktalar()` / `cad_kirp_y()`. Uydurma geometri yok: kesim düzlemi kayıttaki noktadan ve modeldeki tüp
   yarıçapından.
   - FreeCAD'li yol: `rehber_veri.py`, belgeler kapandıktan sonra `kirp()`; modül yerleşimi birim olmalı, kesişim boş, y en büyüğü
     kesimi aşan ya da y en küçüğü değişen sonuç `SystemExit`. Kırpılan yol kümesi `CAD_KIRP` ile birebir olmalı.
   - Geometri denetimi (`geometri_denetle`, `demet_yol_adimlari`) artık kırpılmış noktaları kullanır; `GEO_ISTISNA[12]` kalktı.
   - Veri denetimi (`rehber_kablo --veri`): `kirp_veri_denetle` GLB'deki mesh sınırlarına bakar (y en büyük ≤ kesim + 0,5;
     y en küçük ≤ başlangıç − 2,5 + 0,5; tam bir parça).
   - Metin: 17.10'un ve şema adının "eski çizim" cümleleri kalktı, K2 kablo listesindeki "Taban şeması 12" maddesi (N4) kalktı.
2. **Uç etiketleri: ad kayıttan, yer modelden.** `kablolar.json` damar uç adları kısa ada indirilir (`uc_kisa`); kısa ad
   `rehber_kablo.UC_ETIKET` ile tam bir CAD parçasına (regex + gerekirse modül; kol servoları `omuz_sag/omuz_sol/dirsek_sag/dirsek_sol`
   modülüyle) ya da `UC_MODELSIZ`'e (nedenli) bağlanır; 47 modelde, 10 modelsiz. Her damar öneki sınıflı, iki tabloda birden olan ad
   yok, bayat ad yok, her regex tam bir parça (`uc_etiket_denetle`).
   - `rehber_gorunum.uc_isle` her konum (adım ya da alt adım) için metinde adı geçen ve karede çizilen kabloların uçlarını toplar;
     aynı parçaya düşen adlar " / " ile birleşir; nokta GLB parça kutusunun merkezi; konum başına en çok 10 (`UC_EN_COK`) etiket karede.
   - Karede görünmeyen uç numara almaz, "Uç karede görünmez: ad (neden)" listesine gider. Nedenler: modelde yok, bu adımda takılı
     değil (`durum == gizli`) ya da `rehber_metin.UC_ORTULU` (10 kayıt; "bu bakışta başka parçaların arkasında" /
     "bu kadrajın dışında"). `UC_ORTULU` önizlemede görünürlük ölçümüyle (F10d U4) bulundu, her kayıt kullanılmalı (U6).
   - `app.js`: numara yuvarlağı parça noktasında; çakışırsa 8 yönde artan uzaklıkta yer aranır, kılavuz çizgisiyle bağlanır; kutular
     birbirine, işaret kümelerine ve öbür çapalara binmez, güvenli alanın içinde kalır. Yazdırma karesinde (`?sahne=1`) yalnız numara,
     etkileşimli kipte numara + ad. `u` tuşu ve `?uc=0` kapatır (localStorage "uc").
   - `yazdir.html`: karenin altında "Uçlar: [n] ad (kablolar)" ve "Uç karede görünmez: …" satırları (lejantla aynı punto, ≥ 8 pt).
3. **Adım 0 tanımı kutuda.** `is_` paragrafı `**…:**` ile başlıyorsa `yazdir.html` onu mavi kenarlı `.is.tanim` kutusuna koyar;
   HAZIRLIK paragrafı "**Sağ / sol tanımı:** …" ile başlar. Adım 0'ın "bakış" etiketi: `kareBaslik` yalnız etkileşimli kipte gizli değil,
   artık her kipte görünür (`!SAHNE` koşulu).
4. **Kurulum testi K1 → F5.** Test devreye alma ve yön testinden sonra yapılabildiği için tam metni F5 "İlk enerji, aşama 2" kontrol
   listesinin sonuna taşındı; K1 kontrolünde tek satırlık gösterge kaldı. F5 `is_` "kontrol listesindeki sağ / sol kurulum testini yap".
5. **Yapılmayan FreeCAD'li bölmeler.** Kablo yolu 5 / 7'nin bölünmesi CAD parçasını bölmeyi gerektirir (model dosyası; veri parça
   sayısı CAD ile tutmaz, `renk_isle` durur). 17.10'un bölünmesi alt adım numaralarını kaydırır (16 gönderme, kare incelemesi);
   uç etiketleri 17.10'daki karışıklığı (hangi kart hangisi) zaten karede çözer. İkisi de bu pakette yapılmadı.

## 2. Madde madde

| Madde | Durum | Nerede | Not |
|---|---|---|---|
| 1 Kablo yolu 12 gerilemesi (K1 ana karesi kadrajı, hayalet çizgi) | yapıldı (kaynak) | `rehber_kablo.py`, `rehber_veri.py`, `rehber_denetim.py`, `rehber_metin.py` | önizlemede K1 ana karesi (17) tabana odaklı, 32.4'te soluk mor çizgi yok; gerçek kesim FreeCAD'li üretimde |
| 2 Uç etiketleri (`app.js`, `yazdir.html`) | yapıldı | `rehber_kablo.py`, `rehber_gorunum.py`, `rehber_metin.py` (`UC_ORTULU`), `app.js`, `index.html`, `stil.css`, `yazdir.html` | önizleme: 24 konum, 48 etiket karede, 46 "karede görünmez"; 20 konumda çizilen etiket var |
| 3a 31.4 yedek USB ses kartı | yapıldı | `rehber_metin.py` 31.4 `is_` | "Karede PAM8403'ün yanındaki ikinci kart yedek USB ses kartıdır: takılmaz (önceki alt adım)." |
| 3b K2 ana karesi lejantında "Sinyal (mor)" | yapıldı | `app.js` (`onceki` dalında kablolama ana karesinde sınıf sayımı), `yazdir.html` (ana lejantta `p.a < s` kabloları) | önizlemede 32 görüldü |
| 3c Adım 0 tanımı kutuda + "bakış" etiketi | yapıldı | `rehber_metin.py` HAZIRLIK, `yazdir.html` `.is.tanim`, `app.js` `kareBaslik` | önizleme PDF sayfa 1'de kutu görüldü |
| 3d 32.4 USB kablosu karşıtlığı | kısmen | kırpmayla | karşıtlığı düşüren hayalet çizgi kalktı; ton değiştirilmedi (ΔE00 en düşük beyaz ↔ hazir-usb 15,9 ≥ 15 eşiği). Üretim karesinde yeniden bakılacak |
| 3e B6a tablolarında "(yazılım adı)" | yapıldı | `rehber_deger.py` | "PCA9685 kanal N sinyali (yazılım adı `…`)" |
| 3f Kurulum testi K1 → F5 | yapıldı | `rehber_metin.py` | § 1.4 |
| 4a Kablo yolu 5 / 7 bölünmesi | yapılmadı | — | § 1.5 (model dosyası gerekir) |
| 4b 17.10 bölünmesi | yapılmadı | — | § 1.5 (numara kayması; etiketlerle örtüldü) |
| 4c Bara gösterim parçası, F1 ölçü noktaları karesi | kapsam dışı | — | sonraki CAD paketi |
| 5a F9c-uret P10.7 / F10 özetleri b2e'ye | yapıldı | `F9c-uret.py` | depo dışı üretim + `F9c-dogrula --sayfa`: hata 2 → 0 |
| 5b `dongu-158.md` b2d kare incelemesi kilit satırı | yapıldı | plan | yerine b2f kilit satırı |
| 5c N bulguları | N4, N9 yapıldı; N7, N13 b2e'de zaten yapılmış | `rehber_metin.py` (N4), `app.js` `miniGuncelle` (N9) | açık: § 6 |

## 3. Onay kaydı ve birleşim

- `rehber_kritik_onay.json` yenilendi (`rehber_denetim.py --kritik-onay-yenile`; önceki kopya depo dışında). Yeni: kablo 222 /
  liste 211 / metin 1118. **77 fark:** kablo +`CAD_KIRP`, −`GEO_ISTISNA[12]`, +47 `UC_ETIKET`, +10 `UC_MODELSIZ`; liste +1
  `TERIM_ISTISNA` (31.4 cümlesi "ses kart" kuralına takılıyordu); metin 11 silinen, 12 eklenen. **Kritik (birimli) değer farkı 0.**
  Birimsiz sayı belirteçleri: silinen 12, 32, 01, 05.11 (kalkan "eski çizim" cümleleri), eklenen 7960, 8403 (parça adları).
- `F10l-birlesim.py`: varsayılan taban `b5fc255`; `BEKLENEN["b5fc255"]` b2f'nin 8 eklenen / 7 silinen cümlesi, her biri gerekçeli.
  Sonuç GECER (eski 1095, yeni 1096 cümle). b2e'nin listeleri `84f1a4a` tabanında kayıt olarak kaldı (o tabanla koşu artık b2f
  farklarını da gösterir).

## 4. Sınamalar

| Sınama | Sonuç |
|---|---|
| `kablolar_uret.py --kontrol` | 0 (güncel) |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / 172 bozma, GEÇER |
| `rehber_denetim.py --kaynak` | 0; ascii 0, elektrik 0, D1–D8 hata 0, onay farkı 0 |
| `rehber_denetim.py --bozma-denemesi` | 302 / 302 (b2e 299) |
| `rehber_denetim.py` (depodaki eski veri) | 0 |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER; uç etiketi 47 / 10 hata 0 / **93 / 93** (yeni b87–b93: kırpma ve uç tabloları) |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` (depodaki eski veri) | **beklenen KALDI (2)**: GLB'de yol 12 y en büyük 1327,4 > 192,5 ve `uc_kaynak` yok; ikisi de üretimle kalkar |
| `rehber_kablo.py --bozma-denemesi --veri` depodaki veri | 105 / 105 (`uc_kaynak` gerektiren v13–v15 atlandı) |
| `rehber_kablo.py --veri` önizleme verisi | GEÇER; kırpma hata 0, veri uç etiketi 24 konum hata 0 |
| `rehber_kablo.py --bozma-denemesi --veri` önizleme verisi | **108 / 108** (yeni v10–v15) |
| `rehber_kol_kablo.py --yazma` | GEÇTİ |
| `F10l-birlesim.py` | GECER (eklenen 8 / 8, silinen 7 / 7) |
| `F10d-dogrula.py --bozma-denemesi` | şema karede 5 / 5, uç etiketi **9 / 9** (U1–U6) |
| `F10d-dogrula.py --yalniz-uc --rehber <önizleme>` | GECTI, hata 0 (24 konum, iki kip) |
| Gerçek tarayıcıda bozma (önizleme verisi bozularak, depo dışı) | 4 hata yakalandı (U4, U1 × 2, U5) |
| `F9c-uret.py --cikti <geçici>` + `F9c-dogrula.py --tarayicisiz --sayfa` | 0 hata (önce 2) |
| `node --check rehber/app.js` | 0 |
| Önizleme PDF (depo dışı, `yazdir.html`) | 86 sayfa, en küçük 8,1 pt, taşma yok; "Uçlar:" 16 sayfada, "Uç karede görünmez" 11 sayfada |
| `__pycache__` | depoda 0 |

Koşulmayan: FreeCAD (`rehber_veri.py` kırpması), tam üretim (`rehber_uret`), zincir 2–10, F10d tam koşu (gezinme / görünürlük /
telefon üretilmiş veriyle), koyu tema.

## 5. Önizleme ve FreeCAD'li yolda bakılacaklar

Önizleme (depo dışı): depodaki `rehber/` kaynakları kopyalandı; GLB'de p1191'in y > 192,5 üçgenleri düşürüldü (622 üçgenin 383'ü;
y en büyük 1327,4 → 192,4; gerçek kesimde kapak yüzü olur, burada yok); veriye `alan_isle` + `uc_isle` uygulandı; kareler
`rehber_uret` ile aynı (1200 × 720, `?sahne=1&tema=light`) ve etkileşimli 1400 × 900.

- Gözle görülen kareler (açık tema): 0, 14 (B6a), 17, 17.2, 17.10 (iki kip), 32, 32.4.
- Ölçülen ama gözle bakılmayan: 9, 12, 17.3–17.9, 17.11, 29, 31.4, 31.9, 32.1–32.7 (ölçüm F10d U1–U5 ile geçti).
- **Üretimden sonra bakılacak:** 17.12 (kadraj; önizlemede etiket yok), 17.1, 17.3–17.9, 17.11, 29, 31.4, 31.9, 32.1–32.3, 32.5–32.7;
  koyu tema; PDF'te kareye basılı numaralar (önizleme PDF'i depodaki eski kare görüntülerini kullandı); 32.4'te U06 karşıtlığı.

FreeCAD'li yolda:
1. `rehber_veri.py` `kirp()`: taban modülü yerleşimi birim mi (değilse durur), `common` sonucu boş değil, y en büyük ≤ 192,5.
   `KIRPILAN == CAD_KIRP` sınaması.
2. Kesim yüzeyi: gerçek kesimde tüpün ucu düz kapak; 17.10 ve K1 ana karesinde B01'in ESP32 taşıyıcısına vardığı yer doğal mı.
3. `kablo_kapisi` ataması: yol 12 kırpılınca alan eşiğiyle K1'de kalmalı (önizlemede `alan_isle` 12 değişiklik, b2e ile aynı).
4. `rehber_kablo --veri` yeni satırları: "kırpılan CAD yolları … hata 0", "veri uç etiketi: 24 konum, hata 0".
5. F10d tam koşu `uc_etiket` bölümü: GLB kutuları gerçek kesimle değişirse etiket noktaları kayar; U4 eşiğine bakılmalı.

## 6. Beklenen üretim sayıları ve açık işler

Beklenen: alt adım **91**, şema **65**, parça **1192**, çizim sınıfı 68 / 5 / 1 (değişmemeli); uç etiketi 24 konum / 48 etiket /
46 görünmez (önizlemeyle aynı olmalı); PDF önizlemede **86** sayfa (uç listeleri ve tanım kutusu sayfa eklemedi; gerçek karelerle
yeniden bakılır), en küçük 8,1 pt, taşan 0.

Açık:
- N1 / N2: `kablolar.json` kayıt verisi (bu paketin alanı değil).
- N3: `karar-kuyrugu.md`'deki bayat paragraf; ucuz ama dokunulmadı (kuyruk bu paketin kilit alanında değil).
- N5: cümlenin kaynağı yok; kaynaksız yazılmadı.
- N6: kural sınırı; değiştirilmedi.
- N8: kapsam dışı.
- N10: w'nin artırılması için kaynak yok.
- Kablo yolu 5 / 7 ve 17.10 bölünmesi (§ 1.5), bara gösterim parçası, F1 ölçü noktaları karesi: sonraki CAD paketi.

## 7. Bağımsız kontrolün bakacağı yerler

1. `rehber_kablo.UC_ETIKET` regex'lerinin doğru parçayı seçtiği (özellikle kol servoları modül süzgeci, "PC817 modülü → Arayüz kartı").
2. `rehber_metin.UC_ORTULU` nedenlerinin karelerle tutarlılığı (10 kayıt; ölçümle bulundu, gözle yalnız 17.10 ve 17.2 görüldü).
3. `uc_isle`'nin hangi kabloları "bu konumda" saydığı (metinde geçen ∩ çizilen + `BAGLANTI_TABLOSU`); alt adımı olmayan adımlar.
4. `rehber_veri.py` `kirp()` FreeCAD'siz sınanamadı: kod okuması.
5. Onay kaydı farkının 77 satırı (`--kritik-onay-yenile` çıktısı) ve birimli değer farkının 0 olduğu.
6. Kurulum testinin F5'teki yeri ve K1'deki gösterge cümlesi.

## 8. Kısım 2: kayıt düzeltmeleri (pano #7 mesaj #32, #8 mesaj #33)

Açılış 16.11.2026 10:11, kaynak düzeyinde kapanış 10:26 (saat okundu; uygulama ajanı, FreeCAD'siz). Taban aynı (`b5fc255`); kısım 1'in
çalışma ağacı değişiklikleri geri alınmadı, üstüne yazıldı. Commit yok, push yok, FreeCAD ve tam üretim koşmadı. Dayanak: 16.11'de panoya
gönderilen iki cevap (#32 konu #7, #33 konu #8; Efe'nin #27–#30 mesajları) ve onların depo dışı araştırması. Dokunulmayanlar: K60, K61,
K50 kayıtları ve sipariş kalemleri; CAD model dosyaları; `kod/`; üretilmiş çıktı (`rehber/veri/`, `rehber/goruntu/`, `planlama/rehber/`);
`sonuc-rapor.html` (git karması HEAD ile aynı, `44c02d35…`); eski kir dosyaları.

**Satır numaraları korundu.** `kablolar.json` kaynakları `elektrik.md:NNN` ve `kablolama-on-kararlar.md:NNN` göndermeleriyle denetleniyor
(`kablolar_denetim` "kaynak" sınaması); bu yüzden `elektrik.md` (592), `pin-haritasi.md` (465) ve `kablolama-on-kararlar.md` satır sayısı
HEAD ile aynı: yeni metin var olan satırlara eklendi (uzun satır), E4'teki yeni madde `## K4` başlığından önceki boş satırın yerinde (286).

### 8.1 Madde madde

| # | Ne | Nerede | Kritik cümle / değer |
|---|---|---|---|
| 1 | IS arıza cümlesi | `pin-haritasi.md` Y7 (276–277), D7 (351), başlık 16.11 notu (8) | "tek kanal arızasında pin 0,82–1,44 V (tipik 0,93 V), iki kanal birden 2,88 V … 16.11'e dek burada yazan "hata akımında pin ≥ 1,4 V" yalnız 7 mA için doğruydu. Yazılıma önerilen eşik: pin ≥ 500 mV (`analogReadMilliVolts`, ham değer değil; 3 örnek aynı) … Hesap, ölçüm değil; kesin eşik T6 ölçümünden sonra yazılır" |
| 2 | T6'ya 4 mA adımı | `pin-haritasi.md` § 7 T6 (387) | "Ek adım (16.11): aynı kurulumla 4 mA … pin gerilimi hem multimetreyle hem firmware'in `analogReadMilliVolts` okumasıyla yazılır"; ölçüt "4 mA'de pin yazılımın arıza eşiğinin (öneri 500 mV, Y7) açıkça üstünde (hesap 0,82 V …)". Not: brief "`planlama/d158/testler/` altında" diyordu; oradaki T6 akustik testi, BTS IS testi yalnız pin haritası § 7'de (testler/ altında IS / BTS geçen kâğıt yok) |
| 3 | VIN'e seri Schottky (K66) | `karar-kuyrugu.md` K66 (özet + gövde, sayım 48 / 18 / 66); `elektrik.md` E4 tablosu (144), E4 yeni madde (286), blok şema (338), açık işler 6 (509); `kablolar.json` X01 "5 V" damarı (not, teyit, kaynak `elektrik.md:286`) ve `kararlar` K66 → `kablolar.md`; `maliyet.json` 1N5819; rehber B6a madde 2 + kontrol, K2 alt adım 4; `rehber_denetim.ZORUNLU_CUMLE` B6a yön kuralı | "çevre 5 V → 1N5819 anodu, katot → ESP32 VIN"; sigorta atınca "düşenler 5 V'tan beslenen üç HC-SR04 ve iki BTS7960B kartının mantık VCC'si. Ayakta kalanlar: ESP32 (USB'den …) ve ESP32 kartının 3V3 regülatöründen beslenenler: PCA9685 mantığı, BNO055, iki enkoder, PC817 modülünün çıkış tarafı"; risk "VIN ≈ 4,5–4,6 V … hesap, ölçülmedi"; tezgâh denemesi üç madde, "geçmezse diyot geri alınır ve panoya yazılır" |
| 4 | Reset ve ReSpeaker | `elektrik.md` E3 (264); `kablolama-on-kararlar.md` §4 madde 4 (157), §5 (208), §7 (250), §15 (393); kuyruk "Karar değil, iş" maddesi (Yapıldı); rehber K2 alt adım 5, K2 kontrol, E4 not_ | "Efe'nin iki cevabı geldi (pano #7 mesaj #28, 14.11; kayıt 16.11) … İki açıdan da boyun demeti kapatılabilir; bükümlü çift eklenmez" |
| 5 | K65 ek notu | `sag-sol-karari.md` § 3 (madde zaten vardı; ad taşınması açık yazıldı), kuyruk K65'e ek not | "Pi'ye giden arıza satırındaki `is_sol` / `is_sag` adları da girişleriyle birlikte taşınır; takastan sonra `is_sol` GPIO33'ün, `is_sag` GPIO32'nin arızasıdır" |
| 6 | Sonuç raporu aracı | `F9c-uret.py` GRUP K66 (A), P10.7 özeti (Sürüyor: "kısım 2: kayıt düzeltmeleri, VIN'e seri Schottky K66"; "Kalan"dan "Efe'nin iki cevabı" çıktı) | depo dışı `--cikti`: karar toplam 66, açık 48, çıkış 0; `F9c-dogrula --tarayicisiz --sayfa`: hata 0 (kapanan başlık 18) |
| 7 | Sınamalar, onay, birleşim, plan | § 8.3; `F10l-birlesim.py` `B2F_*`; plan b2f satırı ve günlük | — |

### 8.2 IS hesabı (yeniden yapıldı) ve malzeme

- Rload = 500 ∥ (6,8 k + 5,1 k) = 500 × 11.900 / 12.400 = **479,8 Ω**; k = 5,1 / 11,9 = **0,4286**; pin = I_IS × **205,6 Ω**. 4 mA → **0,822 V**,
  4,5 mA → 0,925 V, 7 mA → **1,439 V**, 14 mA → **2,879 V**; iki teker durmada kart 5,6 A → I_IS = 5,6 / 8500 = 0,659 mA → 0,135 V.
  500 mV ↔ I_IS 2,43 mA ↔ kart başına 20,7 A; 0,5 / 0,822 = 0,61; 0,5 / 0,135 = 3,7. Rb 1 kΩ + R2 2,2 kΩ: 900 Ω × 0,2444 = 220 Ω
  (4 mA → 0,88 V); kartta direnç yok + 470 Ω: 452,1 Ω × 0,4286 = 193,8 Ω (4 mA → 0,775 V). **Taslaktaki sayılarla birebir tutuyor.**
  Varsayımlar: kart IS direnci birleşik 500 Ω (ölçülmedi), IIS(lim) 4 / 4,5 / 7 mA ve kILIS 8500 ikinci elden, doyma 0,95–1,1 V doğrulanmadı.
- Diyot: VIN ≈ 5,0 − (0,35…0,45) ≈ 4,55–4,65 V → kayıtta "≈ 4,5–4,6 V" (taslağın sayısı; düşüm tahmini, veri sayfası bu turda açılmadı).
  5,2 V × 10 / 14,7 = 3,537 V (echo bölücüsü).
- `maliyet.json` "Diyot 1N5819" adet 1 → **2** (yedek yok), not satırına 16.11 gerekçesi. `planlama/adim5/maliyet_toplam.py`: ara toplam
  105.089,07 → 105.090,29 (**+1,22 TL**), genel (%15 pay) 120.852,43 → **120.853,83** (**+1,40 TL**), koşullularla 126.423,90 → 126.425,31.
  Kalem sayısı 125 (değişmedi). Satın alma listesindeki başka kalem değişmedi (K61 bas-konuş, K60 klemens, K50 olduğu gibi).

### 8.3 Onay kaydı, birleşim, sınamalar (`py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

- Onay kaydı yenilendi (`rehber_denetim.py --kritik-onay-yenile`; kısım 1'in kaydı depo dışında): kablo 222 / liste **212** / metin **1121**;
  **8 fark**: liste +1 (`ZORUNLU_CUMLE` B6a VIN 1N5819 yönü), metin eklenen 3 (B6a is_ × 2, B6a kontrol), değişen 4 (E4 not_, K2 alt adım
  4 ve 5 is_, K2 kontrol). **Kritik (birimli) değer farkı 0:** bütün kayıtta birimli değer kümesi 88 → 88, yalnız eskide / yalnız yenide
  yok. Değişen girdilerde silinen {16 kHz × 3, 1 A}, eklenen {16 kHz × 3, 1 A, 5 V × 4}; "5 V" yeni değer değil, çevre 5 V ağının adı
  (eski kayıtta 49 kez). Diyot rehbere yeni kritik değer getirmedi (VIN ≈ 4,5–4,6 V rehbere yazılmadı, yalnız kayıtlarda). Birimsiz yeni
  belirteç: 14.11 (tarih).
- `ASCII_TAMAM`'a 14 kelime (gerekçeli satır, `rehber_denetim.py`): beslenmesin, diye, diyodun, belirlenir, iletir, iletmez, etti, pano, demete,
  beslenmesini, keser, mevcut, devresiyle, kapatabilirsin.
- `F10l-birlesim.py` (taban `b5fc255`): `B2F_SILINEN` +4, `B2F_EKLENEN` +7, her biri gerekçeli; GECER, cümle 1095 → 1099, eklenen 15 / 15,
  silinen 11 / 11.

| Sınama | Sonuç |
|---|---|
| `kablolar_uret.py` / `--kontrol` | yazıldı (74 kablo) / 0 güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER (19 sınama; kaynak, sayi_metin, gorunum dahil) / 172 bozma, GEÇER |
| `rehber_denetim.py --kaynak` | onay yenilemeden önce 1 (yalnız onay farkı 8; ASCII 14 → izin listesi), sonra **0** |
| `rehber_denetim.py --bozma-denemesi` | 302 / 302 |
| `rehber_denetim.py` (depodaki eski veri) | **beklenen KALDI (1)**: yeni B6a yön kuralı eski veride öğeyi bulamıyor ("öğe geçmiyor"); üretimle kalkar |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER / 93 / 93 |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` / `+ --bozma-denemesi` | beklenen KALDI (2, kısım 1'deki iki madde) / 105 / 105 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ (38 bölüm) |
| `F10d-dogrula.py --bozma-denemesi` | uç etiketi 9 / 9 |
| `F10l-birlesim.py` | GECER (15 / 11) |
| `F9c-uret.py --cikti <geçici>` + `F9c-dogrula.py --tarayicisiz --sayfa` | 0 / 0 hata (karar 66, açık 48, kapanan 18) |
| `node --check rehber/app.js` | 0 (bu kısımda değişmedi) |
| `__pycache__` | depoda 0 |

Koşulmayan: FreeCAD, tam üretim (`rehber_uret`), zincir, önizleme verisiyle `rehber_kablo --veri` / F10d (rehber metni değişti, kare ve
uç etiketi kodu değişmedi), `tasarim/cad/demo_uret.py`.

### 8.4 Açık maddeler

1. **Diyodun fiziksel yeri ve bağlantı biçimi** (arayüz kartı üstü mü, X01'in 5 V damarında hat içi mi) kayıtta yok: rehber yalnız yönü ve
   adımı (B6a) söylüyor, "kablajda belirlenir"; `kablolar.json` X01 teyit maddesi.
2. Tezgâh denemesinin hangi test kâğıdına gireceği açık (aday `kablolama-on-kararlar.md` KT5, aynı kurulum).
3. **Demo sayfası** (`tasarim/Robot-Tasarim-Demosu.html`) `maliyet.json`'dan üretilir; yeniden üretilmedi, 1N5819'u hâlâ adet 1 gösteriyor
   (+1,40 TL fark). Üretim / commit adımında `demo_uret.py` (depoya yazar).
4. Sipariş günü 16.11: diyodun bu siparişe girip girmediği kayıtta yok.
5. Yazılım tarafı (Efe): `guc.cpp`'deki "≥ 1,4 V" yorumu ve ham 4000 eşiği, sonar zaman aşımıyla çevre 5 V arızası, `is_sol` / `is_sag`
   takası; kod bu pakette değişmedi.

### 8.5 Bağımsız kontrolün bakacağı yerler

1. IS sayıları (§ 8.2) ve Y7 cümlesinin varsayımları ayrı ayrı söylediği (ikinci elden, ölçülmedi, hesap).
2. K66'nın "sigorta atınca düşen / ayakta kalan" listesi: `kablolar.json` `koruyucular.hat-cevre.yuk_butcesi` ve `parca_beslemesi` ile
   (BTS VCC ve sonarlar 5 V, PCA9685 / BNO055 / enkoder / PC817 çıkışı 3V3).
3. Blok şemadaki "ESP32 VIN (önünde seri 1N5819 …)" öğesinin `kablolar_denetim` `DIYAGRAM` `hat-cevre` kuralıyla uyumu (geçti) ve anlamı.
4. Satır numarası korunması: `elektrik.md` 286'nın `## K4` başlığına bitişik olması (boş satır yok) görünümü bozuyor mu.
5. Rehber B6a / K2 metinleri ve yeni `ZORUNLU_CUMLE` kuralı; veri kipindeki beklenen KALDI (1) üretimden sonra 0 olmalı.
6. Kuyruk sayımı (açık 48, kapandı 18, toplam 66) ve K66'nın "kapandı (tezgâh denemesine bağlı kabul)" sınıflaması.

## 9. Düzeltme turu 1 (16.11.2026 10:45–11:00; kontrol `planlama/d158/F10n-kontrol.md` DÜZELTME GEREKLİ, tek bulgu D1)

Üretim ajanı; HEAD = uzak = `b5fc255`, commit yok. Geçici dosyalar oturum scratchpad'inde (`…\scratchpad\b2f-uretim\`).

- **D1 (yapıldı, FreeCAD'de sınandı):** `rehber_veri.py` `kirp()` sınırları artık sıkı kutudan okur (`optimalBoundingBox(False, False)`,
  üçgenlemesiz, kesin geometri); pay `KIRP_PAY = 0,05 mm`. Denetimin amacı korundu ve iki madde eklendi: (a) yolun sıkı y en büyüğü
  kesimin altındaysa "kesecek bir şey yok: kayıt bayat" ile durur; (b) `rehber_kablo.cad_noktalar(n)`'in korunan noktaları (tüp
  ekseni) kesilmiş katının içinde, ilk atılan nokta dışında olmalı (çok alçak kesim B01'in tabandaki kısmını keserse durur). Boş kesim,
  hacmi küçültmeyen kesim, y en küçüğün değişmesi, `KIRPILAN == CAD_KIRP` olduğu gibi. Log satırı sıkı kutuyla.
  - **Üretimden önce deneme** (depo dışı `kirp_deneme.py`, kilit alınarak 10:52, bitince "boş"; `freecadcmd` + `run_fc.py`, yalnız taban
    modülü, 10 s ve 2 s): betik `rehber_veri.py`'deki gerçek `kirp()` kaynağını okuyup çalıştırır. Kablo yolu 12: kesim 192,5; kesilmiş
    katı 1, hacim 27.255,63 → 3.944,49 mm³. **Eski denetim gevşek kutuyla y en büyük 197,41 > 192,5 görüp üretimi durdururdu** (kontrolün
    hesabı 197,35 ile uyumlu); sıkı kutu (kesin ve üçgenlemeli ikisi de) 137,50…192,50, köşe noktaları en büyük y 192,50. **Yeni
    `kirp()` geçti.** Kesim yüzü: y = 192,5 düzleminde tek düz yüz, alan 81,22 mm² (tüp 2→3 parçası düzleme eğik girdiği için kesit
    elips; πr² / cos = 19,63 / 0,2417 = 81,2). Bozma (gerçek kodla): kesim 1400 (bayat), 100 (boş), 150 (B01'in iki noktası dışarıda),
    189 (ESP32 ucu dışarıda) dördü de `SystemExit` ile yakalandı. Nokta denetimi eklenmeden önce 150 yakalanmıyordu.
- **N8 (yapıldı):** `rehber_denetim.ZORUNLU_CUMLE`'ye B6a kontrol maddesinin ölçüm yönü cümlesi ("çevre 5 V → ESP32 VIN yönünde iletir,
  ters yönde iletmez (bantlı uç, katot, VIN tarafında)"). Bellekte bozma: yön ters çevrilince "yön ifadesi yok", madde silinince "öğe
  geçmiyor" yakalandı (`n8_boz.py`).
- **N11 (yapıldı, yalnız günlük):** 32.4 `DEMET_ALT` ESP32 USB alt adımına `saydam=("Gövde direği",)` eklendi (kısım 1'de, günlükte
  yazmıyordu): direk saydam çizilince USB kablosu okunur oldu.
- **Alınmayan (açık):** N3 (sınıra yakın uç etiketi alanları: önizleme ölçümü; elle yer ya da `UC_ORTULU` kaydı kanıtsız olur, üretimden
  sonra gerçek GLB ile ölçülür, § 10); N9 (`elektrik.md:286` ile `## K4` arasına boş satır: satır numaraları `kablolar.json` kaynak
  göndermeleriyle denetleniyor, bir satır eklemek 287 sonrası göndermeleri kaydırır; risksiz değil); N13 (kILIS yayılımı cümlesi:
  kaynak açılmadan yazılmaz); N1, N2, N10, N12 bilgi.
- **Onay kaydı** yenilendi (önceki kopya depo dışında): kablo 222 / liste **213** / metin 1121; **1 fark** (liste +1: yeni
  `ZORUNLU_CUMLE`). Metin değişmedi; **kritik değer farkı 0** (yeni girdideki "5 V" ağ adı, "1N5819" parça adı, metinde zaten var).
- **Birleşim:** rehber metni değişmediği için `F10l-birlesim.py` beklenen listeleri değişmedi; GECER (1095 → 1099, 15 / 15, 11 / 11).

| Sınama (FreeCAD'siz, 10:55–11:00) | Sonuç |
| --- | --- |
| `kablolar_uret --kontrol` / `kablolar_denetim` / bozma | 0 / GEÇER / 172 |
| `rehber_denetim --kaynak` | onay yenilemeden önce 1 (yalnız onay farkı 1), sonra **0** |
| `rehber_denetim --bozma-denemesi` | 302 / 302 |
| `rehber_denetim` (depodaki eski veri) | beklenen KALDI: B6a is_ ve **yeni B6a kontrol** "öğe geçmiyor" (eski veri; üretimle kalkar) |
| `rehber_kablo` / bozma | GEÇER / 93 / 93 |
| `rehber_kablo --veri` depodaki veri / bozma | beklenen KALDI (2, § 4) / 105 / 105 |
| `rehber_kol_kablo --yazma` | GEÇTİ (38) |
| `F10l-birlesim.py` | GECER |
| `F10d-dogrula.py --bozma-denemesi` | 5 / 5, uç 9 / 9 |
| `node --check rehber/app.js` | 0 |
| `__pycache__` | depoda 0 |

Değişen dosyalar (bu tur): `tasarim/freecad/rehber/rehber_veri.py`, `rehber_denetim.py`, `rehber_kritik_onay.json`, bu günlük.

## 10. Üretim: başlatılmadı (16.11.2026 11:00–11:34; bellek)

Tam üretim (`rehber_uret.py`) başlatılmadı; kaynağa düzeltme turundan sonra dokunulmadı. Neden makine belleği: b2e üretimi 3,43 GB boş
bellekle başlayıp en düşük 1,81 GB'a indi (≈ 1,6 GB düşüş, en düşüğü görüntü / uçuş aşamasında 07:22), bellek bekçisi 1,2 GB'ta art arda
iki ölçümde durdurur; güvenli başlangıç ≈ 2,9 GB. Bu turda makinede kullanıcının kendi Chrome'u açık (10:48'den beri, ≈ 3–3,6 GB, yeni
sekmeler); boş bellek 10:52 2,14 → 11:07 1,17 → 11:34 2,05 GB, 34 dakikalık yoklamada 2,3 GB'ı geçmedi. Kullanıcı süreçlerine
dokunulmadı. Bekçiyi gevşetmek ya da < 2 GB'la başlatmak (`baslat.ps1` kuralı) yerine durup bildirildi. Kilit "boş".

Üretim açılınca yapılacak: `…\scratchpad\b2f-uretim\` (`baslat.ps1`, `sarmal.ps1`, `bekci.ps1`, `zincir.py` b2e'den kopya); F10m § 13
yöntemi, F10d tek başına; ölçülecekler bu günlüğün § 5, kontrolün "Üretimden sonra gözle bakılacaklar" listesi.

## 11. Üretim, zincir, kare incelemesi, commit (17.11.2026 02:36–05:50; saatler sistemden)

Üretim / commit ajanı; HEAD = uzak = `b5fc255`. Yöntem F10m § 13 ile aynı (oturum scratchpad'i `b2f-uretim\`: `baslat.ps1` →
`sarmal.ps1` 15 s bellek bekçisi, eşik 1,2 GB art arda iki ölçüm ya da boş commit < 2 GB). Başlangıçta ağaç § 9–10 ile tutarlı: 44 dosya,
kilit "boş", `.durum` artığı yok, `__pycache__` yok, eski kirin (19 dosya) SHA-1'i 16.11 anlık görüntüsüyle aynı. Kaynağa üretimden sonra
dokunulmadı (yalnız bu günlük ve `dongu-158.md`).

### 11.1 Üretim: tek koşu, çıkış 0 (02:38:58–03:24:20)

`rehber_uret.py` tam koşu: **çıkış 0, 2722 s**. Bellek önce 3,27 GB, en düşük 1,31 GB; bekçi tetiklenmedi. Kilit 02:38 "P10.7b2f üretim
ajanı", veri aşaması bitince 02:42:04 "boş"; son hâli "boş". FreeCAD'in Python'u dört `__pycache__` yazdı, zincirden önce silindi.

| Ölçü | Beklenen (§ 6) | Ölçülen |
| --- | --- | --- |
| ön sınama | geçer | "kaynak denetimi gecti, onay kaydi tutuyor (kablo 222, liste 213, metin 1121)" |
| veri | — | 176 s; mesh 288 benzersiz / 1192 parça |
| uç etiketi | 24 konum / 48 / 46 | **24 konum, 48 etiket, karede görünmez 46** |
| alt adım / şema / parça | 91 / 65 / 1192 | **91 / 65 / 1192**; her şema tek alt adımda (60, birden çok 0, hiç 0) |
| denetim (veri) | 0 | ASCII 0, zorunlu eksik 0 / 118, yasak 0; § 9'daki "beklenen KALDI" (B6a öğe) kalktı |
| sıra / uçuş / ısıl / perdelenme | hata 0 | ulaşılamaz 0 / 565; uçuş 340, çarpışan 0, istisna 16; ısıl 0; gerekçesiz gizli 0, istisna 117 |
| yazdırma kareleri | — | 141 kare, piksel denetimi 141 / 141, boş yok |
| PDF | 86 sayfa, taşan 0, ≥ 8,0 pt | **86 sayfa**, eşleme tutarlı, taşan yok, en küçük **8,1 pt**, 19011 kB; yer tutucu 0 |
| tarayıcı / 360 px | — | 50 / 50, konsol 0; 7 adreste 360 / 0 |

Kırpma (§ 5 FreeCAD'li yol 1–4): `rehber_kablo --veri` gerçek veride "kırpılan CAD yolları (yol 12 y ≤ 192.5): robot.glb okundu; hata 0",
"veri uç etiketi: 24 konum, hata 0", SONUÇ GEÇER; `kirp()` `SystemExit` vermedi.

### 11.2 Zincir 2–10 (F10m § 13.2 komutları; F10d tek başına)

| Sıra | Komut | Çıkış | Süre (s) | Ölçülen |
| --- | --- | --- | --- | --- |
| 2 | `rehber_kablo.py --veri …` | 0 | 1 | GEÇER; kırpma hata 0, uç 24 konum hata 0 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 29 | **108 / 108** |
| 3 | `rehber_denetim.py` (veri) | 0 | 1 | ASCII 0, zorunlu eksik 0 / 118, yasak 0 |
| 4 | `F10f-dogrula.py` | 0 | 600 | GEÇTİ |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | 1015 | GEÇTİ; işaret 1284 / 1284; `renk_demo` KALDI (bilinen karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` (tek başına) | 0 | 1008 | GEÇTİ; 141 / 141 konum; `sema_tek` 60 / 0 / 0; **uç etiketi 20 konum, 48 etiket, görünmez 35, hata 0**; 360 px taşma 0; en düşük boş bellek 1,17 GB (tek ölçüm, bekçi tetiklenmedi) |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | 459 | GEÇTİ; seçim 6 / 6, mini 50 / 50, dış istek 0, konsol 0, 360 taşma 0 ("veri değişti", bilgi) |
| 8 | `F9b-dogrula.py` | 0 | 5 | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 0 | 0 | izlenen 17 dosya kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | 0 | GEÇER, kötüleşen yok (`regresyon.json` değişmedi) |

Koşu düzeni: `zin1` 2–5 (03:24–03:52, çıkış 0); `zin2` F10d (05:13–05:30); `zin3` 7–10 **bellek bekçisiyle durdu** (F10a "mini 1400"
aşamasında boş bellek 3,19 → 0,62 GB, 137 s; başka ağır süreç yoktu) → `zin4` 7–10 yeniden (05:33–05:41, çıkış 0, en düşük 1,52 GB).
03:52–05:13 arası boşluk: `zin1`'in bitiş bildirimi oturum boştayken ajana ulaşmadı; iş durmadı, sonraki adım geç başladı.
Veri, GLB, PDF ve `kontrol.json`'un SHA-256'sı zincirden önce / sonra aynı. Zincirin yazdığı: `planlama/d158/F10{a,d,e,f}-dogrula.json`.

**Demo sayfası (§ 8.4 madde 3):** `maliyet.json` (1N5819 1 → 2) değiştiği için `tasarim/cad/demo_uret.py` zincirin 8. adımından önce koşuldu
(çıkış 0; `tasarim/Robot-Tasarim-Demosu.html` 2 satır: kaynak karmaları ve maliyet verisi). F9b bunu sayı sayı doğruladı.

### 11.3 Kare incelemesi (açık tema; ekran `rehber/goruntu` ve etkileşimli `planlama/rehber/goruntu`)

Piksel farkı (HEAD ↔ yeni): git'in değişti dediği 289 PNG'nin hepsinde fark var; çoğu yalnız "Robotun neresi" mini haritasında (eşik 24'ün
altında, eski dikey çizginin mini haritadan kalkması). Büyük farklar beklenen yerlerde: 17 (≈ 370–400 k px), 0, 14, 31.4, 32, 17.10–17.12, 32.4.

- **Kablo yolu 12 kesimi:** 17 (K1 ana karesi) yeniden tabana odaklı, kablolar okunuyor, direkte mor çizgi yok. 32.3 (G17'nin yanı), 32.4,
  34.3 (HEAD ile yan yana: direk boyunca giden soluk mor çizgi kalktı) temiz; 33–35 alt adımlarındaki 2–10 k px fark bundan.
- **Uç etiketleri:** 17.10 (8 numara; basılıda numara, etkileşimlide numara + ad; sağ / sol adlar doğru tarafta), 17.8 (2 numara kartın
  üstünde, direkte değil), 32.1 (S1 sol / sağ ve omuz uçları), 31.9 (SY8205 ve kafa kartları), 32.4 (ESP32): etiketler parçanın
  üstünde, birbirine, lejanta ve mini haritaya binmiyor. PDF'te "Uçlar:" 16 sayfada, "Uç karede görünmez" 11 sayfada (önizlemeyle aynı);
  s. 26 (17.10–17.12) okunur, taşma yok.
- **Adım 0:** PDF s. 1'de "Sağ / sol tanımı:" mavi kenarlı kutuda; karede "bakış: sağ-önden" etiketi görünüyor.
- **32.4 karşıtlığı:** USB (U06) koyu gri çizgi direk boyunca seçiliyor.
- Bozuk / boş kare, yanlış taraf ya da yanlış alt adım görmedim; **düzeltme turu kullanılmadı.**

Kapsam dışı gözlemler (dokunulmadı): 17.12 bütün robotu kadrajlıyor (taban küçük); b2d'de (`78d160d`) de aynı, b2f gerilemesi değil
(F10m § 14 açık maddesi). PDF s. 25'te (17.9) Kablo yolu 9 (G18) için "eski çizimdir" cümlesi duruyor: yol 12'den ayrı, bilinen durum
(Kablo yolu 5 / 7 / 9 bölünmesi sonraki CAD paketinde). F10d 17.1'de "GÖRÜNMEZ p1181 Kablo yolu 2" bilgi satırı (çıkışa girmiyor).
Bakılmayan: koyu tema kareleri (üretim yalnız açık tema basıyor; F10e koyu temada görünürlük 0 sorun), telefon kareleri gözle.

### 11.4 Commit

Tek commit "Lale P10.7b2f: …" (`lale-duzeltme`), açık `git add` listesiyle 325 dosya: kaynak / kayıt 25 (§ 1–9'un dosyaları, bu günlük,
`F10n-kontrol.md`, `dongu-158.md`), üretilmiş: `rehber/veri/` 4, `rehber/goruntu/` 141, `planlama/rehber/goruntu/` 148,
`planlama/rehber/Lale-montaj-rehberi.pdf`, `kontrol.json`, `planlama/d158/F10{a,d,e,f}-dogrula.json`, `tasarim/Robot-Tasarim-Demosu.html`.
Kontrol görüntüleri (`planlama/rehber/goruntu/`) K47 açık olduğu için b2d / b2e'deki gibi commit'e girdi. Eski kir (19 dosya) girmedi,
SHA-1'i başlangıçla aynı.
