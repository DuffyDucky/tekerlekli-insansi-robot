# F10t · P10.7b2j kontrol günlüğü (CAD analiz / kontrol ajanı; iki ajanlı CAD kuralının ikinci yarısı)

DURUM: KESİLDİ (19.11.2026 06:52; orkestratörün plan değişikliği: yeni CAD tasarım turu). Tasarım incelemesi, ana montaj, baskı zinciri,
regresyonlar ve görseller bitti; çakışma taraması statik bölümünden sonra omuz bölümünde durduruldu (§ 5). Push yok.

Açılış 19.11.2026 02:09 (saat okundu). F10s ile aynı depo dışı worktree (yerel yol yazılmadı), dal `lale-cad-b2j`, taban `8bca2f5`,
incelenen uç `184ba51` (6 commit). Ana çalışma ağacına yazılmadı. Push yok.

## 0. Koşu düzeni

- FreeCAD kilidi: ana ağaçtaki `planlama/d158/FREECAD-KILIT.txt` **yalnız okundu** (ana ağaca yazma yasağı; kilide satır yazılmadı).
  Her FreeCAD koşusundan önce kilit "boş" ve boş bellek ≥ 2,5 GB beklendi. Çakışma taraması için depo dışı sürücü
  (kontrol ajanının çalışma dizininde, commit'e girmez): `carpisma_kos.kos()` ile aynı (tek koşu kimliği, 9 bölüm sırayla, sonunda
  `birlestir()`), ek olarak her bölümden önce kilit + bellek beklemesi ve `.durum` dosyasına satır.
- Koşu günlükleri depo dışında; freecadcmd çıkış koduna güvenilmedi, her koşunun günlüğü okundu.

## 1. Tasarımın eleştirel okunması (`git diff 8bca2f5..184ba51`, sonra F10s günlüğü)

### 1.1 Yeniden üretilebilirlik ve "çıkış 0 ama hata" sorusu

- `taban_montaj.py` (02:10–02:12, 110 s) ve `kafa_montaj.py` (02:10–02:15, 288 s) worktree'de, değişikliksiz kaynakla yeniden koşuldu; günlükler
  satır satır okundu. Taban: geçersiz 0, iç çakışma 0 (660 çift), bağlantı 140 / 140, taban × iskelet 0 (temas 36), taban × kabuk 0
  (temas 1), bölge ihlali 0, iki tutucu "sigar, çıkıntı 0, destek sorunu 0". Kafa: geçersiz 0, ev pozu çakışma 0 (502 çift), bağlantı
  29 / 29, kütle 2.089,5 g, tilt payı 3,7 / pan 2,2. Traceback / Error / KeyError yok; kafa günlüğünde 11 satır OCC uyarısı
  "makeElementFace: resulting face is invalid" (kafa × gövde süpürme aşaması; parça geçerliliği 0 hata, F10s'den önceki kafa koşularının
  bilinen uyarısı, sonuca etkisi görülmedi).
- Fark: üretilen dosyalarda yalnız `sure_s` ve STEP zaman damgası (taban-analiz.json 1 satır, kafa-analiz.json 1 satır). Yani commit'li
  çıktılar commit'li kaynağın çıktısı; "Celik A2" hatası kaynakta yok (`grep` 0), RHO sözlüklerinde yalnız tanımlı malzemeler. O hata
  ara bir denemede kalmış, commit'li sonuçları etkilememiş. Üretilenler geri alındı.
- Küçük kayıt hatası: F10s § 4 "taban içi çakışma 0 (669 çift)" yazıyor; commit'li `taban-analiz.json` `cift_sayisi` 660, koşum da 660.

### 1.2 K64 bara tutucuları

- **"Somun sıkılmış hal" denetleyiciyi geçmek için mi?** Hayır, gerçek montajı yansıtıyor. Altıgen cep alttan açık (YD1 − 1'den kesiliyor),
  derinlik k + 0,3 = 3,8 mm. Somun sıkılınca çekme kuvveti başı cep tavanına (PETG) bastırır; panel başı yalnız tutucu sökülünce düşmesin
  diye yakalar (0,3 mm aralık). İlk koşudaki "baş panelde" modeli gevşek hali gösteriyordu ve kuvvet zincirinde (somun → yaylı pul → pul →
  pabuçlar → tutucu üstü … cep tavanı → baş) yanlış yüzeyi temas sayıyordu. Denetleyiciye (`taban_montaj.py:85–91`) dokunulmamış
  (fark yok). Temas listesi (baş–tutucu, pul–tutucu, yaylı–pul, somun–yaylı) gerçek yük yolu.
- Pabuç yığını: `kablolar.json` bara-pabuc "saplama başına en çok 4 pabuç", yerleşim 4 / 4 / 4 / 2 ve 3 / 2 / 2 / 2 / 2 (+ köprü uçları);
  4 × 1,2 = 4,8 mm sarı RV 5.5 için ihtiyatlı (dil kalınlığı ölçülmedi, VARSAYIM doğru etiketli). Uç payı 7,5 mm: M5 × 20 de yeterdi,
  değiştirmeye gerek yok.
- Altıgen baş (DIN 933) VARSAYIMI tasarımı belirliyor: sipariş başka baş tipiyle gelirse (ör. DIN 912 silindir baş) cep dönmeyi tutmaz.
  Ahmet'in alım kalemi (aşağıda). Cep anahtar ağzı 8,4 (baş 8,0): FDM'de altıgen cep çoğu zaman 0,1–0,2 mm daralır; baş sıkı girer
  (tutsak kalması için iyi), girmezse cep ısıyla oturtulur. İlk baskıda deneme önerisi, model değişikliği değil.
- **Montaj sırası ve erişim:** saplama yalnız alttan girer (delik Ø5,5 başı geçirmez); M3 × 10 vidalar panelin altından. Rehber sırası B3
  (akü) → B5a (tezgâh: güç paneli) → B5 (panel burçlara) olduğu için tutucular tezgâhta, panelin altı açıkken takılır: mümkün. Sıra:
  ısıl gömme somunlar → saplamaları alttan cebe, üstten somunu elle tak (saplama düşmesin) → tutucuyu panele koy → M3'ler panel
  altından. Panel yerine indikten sonra M3 başları akü üstünün 1,35 mm üstünde, erişilmez (gerekmez). Panel dikey iner (direk cebi
  önden açık ama panel direk boyunca iniyor; vida başları kayış üstlerinin z dışında: kayış z −152,5…−127,5 / −92,5…−67,5, vida başları
  z −57,85…−52,15 ve −117,85…−112,15). Pabuç ve somunlar üstten, 8 mm lokma ile her zaman erişilir. Akü sökme: panel kalkmadan akü
  çıkmıyor (bu paketten önce de böyleydi); tutucu buna yeni engel eklemiyor, saplamalar panelle birlikte kalkar. Saplama değiştirmek
  tutucuyu (dolayısıyla paneli) sökmeyi gerektirir: yalnız arıza halinde.
- Seçici: yeni parçaların hepsi FCStd grubu `Guc_aku_surucu_panel` ve YMin > 170 (en düşük M3 başı 172,85) → `rehber_secici.py:111`
  kuralıyla B5a (kod okundu; `rehber_uret` atanmamış listesi bu dalda koşulmadı, rehber paketinde doğrulanacak).
- Yük ve sünme notu (rehber metnine): akım pabuçtan pabuca geçer, ama sıkma kuvveti 6,2 mm PETG'den geçiyor; PETG sıkma altında
  zamanla gevşer. Yaylı pul var; rehbere "somunu 2–2,5 N·m, ilk enerji öncesi ve ilk haftadan sonra yeniden sık" notu önerilir
  (tork değeri M5 / PETG için mühendislik tahmini, ölçülmedi).

### 1.3 U06 şeridi (b2i: güç paneli x 14…40 / z −40…−30 / y 205…262)

- Modelli parçalar: tutucu y ≤ 189,5 ve z ≤ −44; saplama ucu y 208,3 ama z ≤ −50,4 (somun köşesi): şeritle kesişmiyor (z'de 4 mm /
  9,6 mm). Bu doğru.
- Modelsiz pabuçlar: yığın tutucu üstünde y 189,5…195,3 (+ pul / somun 200,5'e kadar). Şerit y 205'ten başladığı için pabuç hangi
  yöne bakarsa baksın şeride giremez; F10s'in "yıldız pabuçları −z'ye baksın" koşulu gereksiz ve G05'te uygulanamaz: akü − (G05) akü
  kablo yarığından (x 40…80 ya da −80…−40, z −37…−23) +z yanından gelir, pabucu −z'ye çevirmek 12 AWG'de U dönüşü ister.
- Gerçek risk kabloların kendisi: yıldız 4. saplamasındaki (x 25) G17 / G18 ve G05'in yarıktan saplama 3'e giden kablosu şeridin
  x / z izdüşümünden geçebilir; y 205'in altında kalırlarsa şeritle kesişmezler. Rehber notu önerisi: "bara kablolarını panel üstünde
  pabuç seviyesinde (y ≤ 200, panelden ≈ 20 mm) yatay götür; U06 şeridinin (x 14…40, z −40…−30) üstünden yukarı kaldırma". U06 şeması
  değişmez. Kablo boyları / bükülme yarıçapı ölçülmedi.

### 1.4 K53 çentik

- 75,25 × 1,5 mm, yana açık (köşede ince şerit yok). En yakın delik ön kat burcu (x −115, z 40, Ø5,5): çentikle arasında 11,5 mm et.
  Kat 5 mm huş kontrplak, 270 × 226; kesitten 1,5 mm kenar kaybı dayanımı anlamlı etkilemez (hesap yapılmadı, geometri okundu).
  Çentiğin x ucu −60,75, ön şarj kartının x −65 burcuna 4,25 mm (burç yarıçapı dahil pay ≈ 1,25 mm; F10s-K53-olcum.json: iniş boyunca
  ortak hacim 0, en küçük boşluk 0,5 mm kat ↔ güç paneli tasarım aralığı).

### 1.5 K51 TVS

- (−80; 20) tablada D24V50F5'in (−80; 6) önünde, ev pozu çakışma 0, tilt / pan payları aynı. Doğrulanmayan: D24V50F5'in çıkış
  pinlerinin modeldeki yönü (kart zarf olarak modelli, pin yok); "çıkış ucunun yanında" iddiası kart veri sayfasıyla montajda teyit.
  Seçici: "TVS P6KE6V8A Pi hatti" ve "Kopuk bant (TVS Pi hatti)" `_KAFA_KABUK` desenlerine uymuyor → E3a (Kafa_tilt) doğru.

### 1.6 K2 boss

- Dikiş cıvatası arka duvarın dışından (−z) takılıyor (n = (0, 0, −1), baş dış yüzde): 2 mm alyan düz eksenden, arkada engel yok;
  baş kenarı x = 0 dikişine 2,15 mm (baş tamamen sol kabukta). F1a-kontrol'ün açık notu sürüyor: boss havalandırma yarığına 1 mm,
  duvar dayanımı ölçülmedi (K2 a kararıyla kabul). Baskı: arka kabuk sağ destek sorunu 1 (önceki de 1, alan +4 mm²).

### 1.7 Gizlilik

- Fark (STEP / FCStd hariç) ve commit mesajları tarandı: yerel kullanıcı yolu, anahtar, parola yok. FCStd'lerin `Document.xml`'inde
  sürücü yolu yok; STEP'lerde kullanıcı adı 0. Commit yazarı deponun önceki commit'leriyle aynı kimlik. F10s günlüğü başlatıcıyı
  `%USERPROFILE%` ile yazıyor.

### 1.8 Sonuç

Düzeltilmesi gereken tasarım hatası bulunmadı; değişiklik yapılmadı. Notlar rehber iş listesine ve alım kalemlerine (§ 6, § 7).

Kapsam boşluğu (hata değil): K52 kararı (`karar-kuyrugu.md` K52 Durum) göğüs ekranı regülatörü (LM2577 + LM2596) zarfının "K51 ve K53
ile birlikte sonraki tam taramalı CAD paketinde" modele gireceğini yazıyor; P10.7b2j kapsamına (F10q § 5'in beş kalemi) alınmamış, modelde
yok. K64 tutucuları güç panelinin ortasındaki geniş boş alanı aldı; K52 kartının panelde yeri artık daha dar (kart ölçüsü kayıtta
doğrulanmamış). Sonraki CAD paketine kesin iş.

## 2. Koşular (hepsi kilit "boş" ve boş bellek ≥ 2,5 GB bekleyerek; günlükler depo dışında, satır satır okundu)

Ana ağaçtaki b2i kapanış ajanı kilidi 02:13'te aldı; bu ajanın bütün FreeCAD işleri kilit 02:56'da "boş" olana dek bekledi.

| Saat | Komut | Süre | Çıkış | Sonuç |
|---|---|---|---|---|
| 02:10 | `taban_montaj.py` (doğrulama, geri alındı) | 110 s | 0 | § 1.1 |
| 02:10 | `kafa_montaj.py` (doğrulama, geri alındı) | 288 s | 0 | § 1.1 |
| 02:56 | `montaj/ana_montaj.py` | 140 s | 0 | 1227 parça (taban 342 → 388, kafa 161 → 163), geçersiz 0, eklem 22 solve 0, kütle 25.720,6 → 25.843,2 g, AM y 528,6 → 527,0 |
| 02:58 | `montaj/montaj_gorsel.py` (GUI) | 103 s | 0 | GUI kurulumu kaydedildi (eklem 21, simülasyon), 11 görsel + 81 hareket karesi |
| 03:00 | `taban/taban_gorsel.py` (GUI) | 53 s | 0 | 18 görsel; FCStd GUI durumuyla kaydedildi |
| 03:01 | `kafa/kafa_gorsel.py` (GUI) | 43 s | 0 | 17 görsel (FCStd kaydetmez) |
| 03:02–03:09 | `lale158/baski_analiz_ortak.py` × 5 modül | 13 / 318 / 57 / 8 / 12 s | 0 | iki tutucu desteksiz, sığar; § 3 |
| 03:11 | `iskelet_regresyon.py`, `omuz_regresyon.py` `REG_ETIKET=sonra` | 5 / 107 s | 0 | ikisi de **SONUÇ: BİREBİR AYNI**; yan ürünler (regresyon/*.json, omuz-montaj.*, omuz-analiz.json) geri alındı |
| 02:56–06:52 | çakışma taraması (§ 5) | statik 99 s, omuz durduruldu (3 sa 54 dk koşmuştu) | – | § 5 |

Kir: `montaj_gorsel.py` / `kafa_gorsel.py` / `taban_gorsel.py` günlük ve kopyalarını depo dışı TEMP'e yazdı (TEMP koşu için çalışma
dizinine yönlendirildi). Regresyon betiklerinin yazdığı izlenen dosyalar geri alındı (paketle ilgisiz). GUI koşusunda FreeCAD Assembly'nin
bilinen `ViewProviderJoint ... app_obj` uyarısı (FreeCAD 1.1.4 iç hatası, çıktıyı etkilemedi).

Gözle bakılan görseller: `taban-guc-paneli.png`, `taban-elektronik-kati.png` (iki tutucu panelin ortasında, saplama + somun, akü
kablo yarıkları yıldız tutucusunun +z yanında), `kafa-arka.png` (üst dikiş cıvatası arka duvarın dışında, yarık sütunlarının arasında,
dikişin sağında), `kafa-yerlesim-ust.png`.

## 3. Baskı zinciri (72 → 74)

`baski_analiz_ortak.py birlestir` → `Y2b-baski.py` → `F4c-partiler.py` → `F4c-liste.py` → `F4c-dogrula.py`: **SONUÇ: GEÇTİ** (1, 2, 3, 4a,
4b, 5a, 5b, 6). 64 tür / 74 adet, 7.722,7–7.780,5 g (+53,8 g), 161,0–162,2 sa, destekli adet 13 (değişmedi). Tutucular: yıldız 29,6 g /
0,62 sa, anahtarlı 24,2 g / 0,50 sa (baskı analizi; BOM'daki 28,2 / 23,0 g baskı katsayısız kütle). Y2b iki tutucuyu Parti 4'e koydu
(taban kuralı); bağımlılığı yalnız saplama baş tipi, Parti 1'e alınabilir (öneri, değiştirilmedi).
Betik düzeltmeleri (küçük, net; kaynak/denetim gevşetme yok):
- `F4c-partiler.py` `META`: iki tutucu satırı yoktu → KeyError. Eklendi (bağlı kalem: saplama baş tipi teyidi; adım B5a).
- `F4c-liste.py`: F6b fark tablosu her satırı F6a listesinde arıyordu → KeyError. Yeni parça "— (yoktu)" satırıyla, toplam etiketi
  sayıdan; "F6b'den sonra eklenen parçalar" bölümü. **Ayrıca:** betik `baski-listesi.md`'yi baştan yazdığı için P10.7b2g'de (17.11) elle
  eklenen "Kablo deneme parçası" bölümünü siliyordu (ilk koşuda görüldü, dosya geri alındı); bölüm artık mevcut dosyadan aynen korunuyor.
  İki koşu aynı çıktıyı veriyor.

## 4. USB ses kartı yaması

`git apply --check planlama/d158/F10s-ses-karti-cikar.patch` bu dalın ucunda geçiyor. **Uygulanmadı** (orkestratörün koşullu isteği,
≈ 05:57, değerlendirildi): şart (a) tutmuyor. Yama `kafa/kafa10_lib.py`'yi değiştiriyor; bu dosya `carpisma_kos.kaynak_listesi()`'nde
(`*_lib.py`) ve her bölüm kaynak özetini **bölüm bitince** yazıyor (`carpisma.py:1645`). Koşan omuz bölümü (≈ 3,4 sa, 02:58'de başladı)
yama sonrası biterse eski geometriyi tarayıp yeni özeti kaydederdi (yanıltıcı tazelik); önce biterse statik + omuz eski, kalan yedi bölüm
yeni özetle kalır → `tek_kosu` bozulur, omuzun yeniden koşusu (≈ 3,4 sa) gerekir. Ucuz değil; tarama durdurulmayacağı için yama
birleştirmeden sonra (kafa_montaj + ana montaj / BOM + kafa içeren bölümler: statik, kafa_sabit, kafa_sag, kafa_sol, taban; kafa10_lib
bütün bölümlerin özetinde olduğu için tazelik kaydı ancak tam koşuyla temizlenir) uygulanır. Şart (b) ayrıca sınanmadı (gerek kalmadı);
F10s § 5'e göre bu daldaki zincirde (kafa_montaj, ana montaj, baskı, F4c, görseller) `uygulama_olc` bağımlılığı yok, kırılan taraf rehber.

## 5. Çakışma taraması (kesildi; tazelik düzeni ve yeniden koşu tarifi)

- Sürücü: depo dışı `carpisma_surucu.py` (kontrol ajanının çalışma dizininde; içeriği `carpisma_kos.kos()` ile aynı + bölüm başına kilit /
  bellek beklemesi + `.durum` satırı). Koşu kimliği `20261119-021529`; 02:15–02:56 kilit bekledi.
- **statik** (02:56–02:58, 99 s, tepe 718 MB, çıkış 0): ev pozu (S1 0, S2 5) çakışma **0** (868 sınır kutusu kesişen çift; 09.11'de
  821, yeni tutucu / saplama çiftleri); S2 0 mekanik sıfır bilgisi 4 çakışma (09.11 ile aynı dört: üst kol tüpü × S1 kaset kapağı
  6,42 mm³ × 2, gövde braketi M5x18 × dirsek çatalı 20,53 mm³ × 2; yalnız bilgi, K6); arayüz uyumu omuz sağ / sol aynı.
- **omuz** 02:58'de başladı, 06:52'de orkestratörün isteğiyle durduruldu (süreç ve sürücü sonlandırıldı, sonuç yazılmadı). 09.11'de
  bu bölüm 12.232 s (3 sa 24 dk) sürmüştü; bu gece 3 sa 54 dk'da bitmemişti (02:58–03:13 arası aynı anda montaj / baskı / regresyon
  koştu, CPU paylaşıldı). Kalan yedi bölüm koşmadı.
- Üretilen `carpisma-bolum/statik.json` geri alındı (yarım koşu; tasarım turundan sonra zaten eski olur). `carpisma-sonuc.json` değişmedi.
- **Tazelik düzeni:** `carpisma_kos.kaynak_listesi()` = sabit liste (carpisma.py, arayuz.py, ortak_lib.py, sigma_profil.py, beş modülün
  `*_parcalar.py`'si, `kafa/kafa-analiz.json`) + bütün `*_lib.py`. Her bölüm bittiğinde **bütün listenin** md5 özetini kendi JSON'una
  yazar (`carpisma.py:1645`). `eskime()` her bölümün kaydını bugünkü özetlerle karşılaştırır; `birlestir()` `tek_kosu` için 9 bölümün
  aynı koşu kimliği ve aynı özetle bitmesini ister. Yani **herhangi bir izlenen dosya değişince 9 bölümün hepsi eskir**; bölüm başına
  ayrı tazelik yok. `taban_parcalar.py` (kablo yolları) ya da `kafa10_lib.py` (ses kartı yaması) değişince statik dahil hepsi yeniden.
  Tuzak: kaynak dosya bir bölüm koşarken değişirse o bölüm eski geometriyi tarayıp yeni özeti yazar (yanıltıcı tazelik).
- **Yeniden koşu tarifi (tasarım turundan sonra, taze ajan):** tasarım commit'lerinden sonra worktree temiz; kilit "boş", boş bellek
  ≥ 2,5 GB. Ya `python tasarim/freecad/carpisma_kos.py` (9 bölüm sırayla + birleştirme; günlük `%TEMP%/carpisma-<bölüm>.log`), ya da
  kilit beklemeli sürücü (aynı mantık, tek koşu kimliği). Bash `run_in_background` ile başlat, `.durum` dosyasını ≤ 170 s'lik ön plan
  döngüleriyle yokla (180 s'yi geçen ön plan komutu arka plana atılıyor). Sıra: statik, omuz, kol_sag, kol_sol, kolkol, kafa_sabit,
  kafa_sag, kafa_sol, taban. Süreler (09.11 tarama + yükleme): statik 12 + 61 s (bu gece 99 s), omuz 12.232 + 61 s, kol_sag 170 + 59,
  kol_sol 170 + 60, kolkol 45 + 11, kafa_sabit 96 + 63, kafa_sag 468 + 12, kafa_sol 459 + 12, taban 24 + 61 s → ≈ 3 sa 50 dk; tepe
  bellek ≈ 750 MB. Koşu sırasında başka FreeCAD işi koşturma (omuz CPU'ya bağlı) ve izlenen hiçbir dosyayı değiştirme. Sonra
  `carpisma_kos.py kontrol` (çıkış 0), `regresyon.py` (`cakisma_ev_pozu`), `kafa_rapor.py`, `taban_rapor.py`, `montaj_rapor.py`
  (raporlar eskime uyarısını taramadan okur; tarama bitmeden üretme). Taban / kafa kaynağı değiştiği için önce `taban_montaj.py`,
  `kafa_montaj.py`, `ana_montaj.py`, görseller ve baskı zinciri (§ 2–3 sırası) yeniden.

## 7. Ahmet'in alım kararına gidecek kalemler (`maliyet.json` değiştirilmedi)

- "Bara saplaması M5" (kalem 156, 10 takım, fiyat bekliyor): sipariş **altıgen başlı (DIN 933 / ISO 4017, A2, anahtar ağzı 8)** olmalı;
  tutucunun cebi buna göre. Başka baş tipi gelirse cep değişir.
- M5 DIN 125 pul: CAD toplamı 13 → 22 (+9); Pul satırında M5 × 14 → en az 22.
- ISO 7380 M3 × 10: 4 adet, satırda (kalem 121) bu boy yok.
- M3 ısıl gömme somun: CAD 159 → 163; satır 168, pay içinde.
- P6KE6V8A: 2 adet zaten satırda (kalem 66); değişiklik yok.

## 6. Sonraki rehber paketine düzeltme listesi (F10s § 2–§ 5 doğrulandı ve tamamlandı)

Satır numaraları bu dalın tabanındaki (`8bca2f5`) kaynağa göre; ana ağaçtaki b2i bunları kaydırmış olabilir, desenle aranmalı.

1. `rehber_metin.py` B6 `not_` (:350–352) "K53, karar bekliyor … Çözüm seçilmedi" → F10s § 2'deki öneri metni (doğru: çentik ön katın
   arka kenarında, x −136…−60,75, 1,5 mm; kanıt `F10s-K53-olcum.json`).
2. `rehber_metin.py` E3a (:737–738) "D24V50F5 → Pi hattındaki bugün modelde ve BOM'da yok, sonraki CAD paketinde eklenecek (K51 a)" →
   "iki hatta da modelde ve BOM'da var". **Eklenen:** `rehber_denetim.py:365` ZORUNLU deseni `sonraki CAD paketinde eklenecek \(K51 a\)`
   bu metinle birlikte değişmeli (yoksa denetim "zorunlu eksik" verir); :218 ZORUNLU adı "(Pi hattındaki modelde yok)" eskidi.
3. `rehber_metin.py` B5a `not_` (:271–274) "henüz tasarlanmadı …" → gerçek talimat. **Eklenen:** `rehber_denetim.py:370` ZORUNLU deseni
   `CAD paketinde tasarlanıp basılacak, satın alınmayacak \(K64 a\)` birlikte değişmeli. Önerilen B5a alt adımı (tezgâhta, panel altı
   açıkken, B5'ten önce): (a) iki tutucuya alttan 2'şer M3 ısıl gömme somun; (b) 9 M5 × 25 altıgen başlı saplamayı alttan altıgen cebe
   sok, üstten somunu elle tak (saplama düşmesin); (c) tutucuyu panele koy (yıldız z −55 akü kablo yarıklarına yakın olan, anahtarlı
   z −115 röle hizasında), panelin altından 2'şer ISO 7380 M3 × 10; (d) K1'de pabuçlar: büyük akımlı altta, üstte DIN 125 pul + DIN 127
   yaylı pul + somun; somun 2–2,5 N·m (tahmin), ilk enerji öncesi ve ilk haftadan sonra yeniden sık (PETG sünmesi); (e) bara kablolarını
   panel üstünde pabuç seviyesinde (y ≤ 200) yatay götür, U06 şeridinin (x 14…40, z −40…−30) üstünden yukarı kaldırma.
4. `rehber_metin.py` K1 17.1 (:383–385) "Karede görünmez: iki bara ve tutucuları modelde yok" → artık karede görünür (tutucu + saplama;
   pabuçlar modelde yok).
5. `rehber_kablo.py` **(eklenen)** `MODELSIZ_KONUM` (:175 ve düzeltme `b26` :1791) yıldız barası (−20 / 20; 186; −90 / −60) → gerçek
   saplama 3 (0; ≈ 192; −55); anahtarlı bara (:177) Röle K1 vekili → "Bara tutucusu anahtarli bara" parçası (saplama 3: x 12,5, z −115);
   `UC_MODELSIZ` (:269–270) "bara modelde yok (bara tutucusu CAD paketinde, K64)" eskidi. `lale158/kablo_yolu_taban.py` (:13, :78, :81)
   vekil röle notları aynı. Yol değişirse rehber kablo onay kayıtları yeniden.
6. Seçici: yeni taban parçaları B5a'ya, TVS + köpük bandı E3a'ya düşüyor (kod okundu, § 1.2 / § 1.5); `rehber_uret` "atanmamış" listesi
   üretimde bakılmalı.
7. USB ses kartı (F10s § 5): yama `planlama/d158/F10s-ses-karti-cikar.patch` bu dalın ucuna `git apply --check` ile uyuyor (aşağıda § 4);
   bağımlılık listesi (uygulama_olc / uygulama_metin, rehber_denetim / rehber_metin E4 / rehber_secici:101–102, kablo_yolu_ekran,
   rehber_kablo:960, kafa_rapor metinleri) okundu. **Eklenen:** `rehber_secici.py:101–102` `_KAFA_KABUK` içindeki "USB ses karti" ve
   "Kopuk bant (USB ses" desenleri parça kalkınca ölü desen olur (zararsız, temizlik).
8. `karar-kuyrugu.md` K2 / K51 / K53 / K64 satırlarına "P10.7b2j'de modele girdi (F10s § n, kontrol F10t)" notu; K52 "model hâlâ yok".

## 8. Tasarım turuna devir (orkestratör, 06:5x)

Ana ağaçtaki b2k kontrolü (YÜKSEK): `taban_parcalar.py` CAD kablo yolları 1, 2, 3, 5, 7, 8, 9 eski WAGO / röle noktalarında kalmış, yeni
bara tutucularının / saplamaların içinden geçiyor. Bu kontrol yolları bara–pabuç geometrisine karşı denetlemedi (§ 1'de pabuç zarfı
ve U06 şeridi incelendi, yolların uç noktaları incelenmedi); bulgu bu günlüğün kararını değiştirir: tasarım **düzeltmeyle geçer**.
Tasarım turunda yapılacaklar (bu ajan dokunmadı): yolları tutucu saplamalarına taşı (her saplamada en çok 4 pabuç, `kablolar.json`
bara-pabuç yerleşimi), USB ses kartı yamasını uygula (`F10s-ses-karti-cikar.patch`, `--check` geçiyor), sonra § 2–3 zinciri ve § 5
taraması baştan. Ayrıca bu turda: F10s ve bu günlükte proje sahibinin takma adı geçen üç satır "Ahmet" yapıldı (depo herkese açık).
