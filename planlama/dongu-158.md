# Lale 1,58 m: otonom iş döngüsü (8 Kasım 2026)

Ahmet Yorulmaz, 08.11: "iş planlaması yapalım, her iş aşamasında geri bildirim döngüsü oluştur, full otonom olsun".
**Bu dosya döngünün tek doğru kaynağıdır.** Orkestratör (Echo, Claude Code) her uyanışta bunu okur, sıradaki işi
yürütür, bitince durum tablosunu ve günlüğü günceller. Eski döngü `dongu.md` (Y1–Y6, 1,65 m) tarihçedir; Y4–Y6 buraya
taşındı.

## 1. Her iş paketinin geri bildirim döngüsü

Her paket aynı sekiz adımdan geçer. Bir adım geçmeden sonrakine geçilmez.

| # | Adım | Kim | Çıktı |
|---|---|---|---|
| 1 | **Brief**: amaç, dokunulacak dosyalar, kabul ölçütleri (sayıyla), korunacak değerler | Orkestratör | `planlama/d158/<paket>-brief.md` |
| 2 | **Uygulama** | Opus ajanı A (tasarım) | Değişen dosyalar + `<paket>-gunluk.md` |
| 3 | **Bağımsız kontrol**: yalnız brief + çıktıyı görür, A'nın günlüğüne güvenmez, ölçer | Opus ajanı B (kontrol) | `<paket>-kontrol.md`: GEÇER / KOŞULLU / GEÇMEZ |
| 4 | **Düzeltme turu**: GEÇMEZ ya da KOŞULLU maddeler A'ya geri döner, B yeniden bakar | A → B | En çok 2 tur. 3. turda hâlâ geçmezse paket **karar kuyruğuna** gider, döngü sonraki bağımsız pakete geçer |
| 5 | **Ölçüm**: kritik değerleri JSON'dan okur (A ve B'nin raporuna güvenmez) | Opus ajanı C (kayıt) | Günlükte sayılar |
| 6 | **Regresyon**: önceki paketlerin korunan değerleri bozulmadı mı (aşağıdaki tablo) | Ajan C (`regresyon.py`) | `d158/regresyon.json` |
| 7 | **Kayıt**: commit + push `lale-duzeltme`, paket `rapor.html` | Ajan C | Commit kimliği |
| 8 | **Karar**: C'nin sayılarını A/B raporlarıyla karşılaştırır, bu dosyayı ve Ahmet'in hafıza kasasını günceller, sonraki paketi başlatır | Orkestratör | Durum tablosu |

**Korunan değerler** (her paketten sonra yeniden ölçülür; biri kötüleşirse paket GEÇMEZ):
boy 1.580,0 mm; çakışma (kafa içi, kabuk içi, kabuk × iskelet, ev pozu) 0; yüksüz rampa devrilme payı ≥ 1,5 (şimdi 1,517);
tilt payı ≥ 3,0 (3,64); pan payı ≥ 2,0 (2,21); mikrofon-hoparlör ≥ 400 mm (574,3); SY8205 × USB 0 mm³.

## 2. Otonomi kuralları

- **Uyanış:** saatlik zamanlayıcı. Uyanınca: çalışan ajan var mı bak → yoksa sıradaki paket. Limit dolarsa bir sonraki
  uyanış günlükten devam eder; eski ajan devam ettirilemezse aynı brief + "önce günlüğü oku" ile yeni ajan.
- **Ajan düzeni:** üç Opus ajanı (A tasarım, B kontrol, C ölçüm + kayıt); görsel üreten ajan da Opus.
- **Orkestratör:** ana oturum **hiç iş yapmaz** (Ahmet, 08.11: "asla bu oturum iş yapmasın sadece alt agentlar iş yapsın"): yalnız brief yazar, ajan başlatır, rapor okur, bu dosyayı ve hafızayı günceller. Ölçüm, commit ve push da ajanda. Aynı dosyaya iki ajan aynı anda dokunmaz. Bağımsız iki paket paralel koşabilir (aşağıda "paralel" sütunu).
- **Paralel çalışma (Ahmet, 08.11: "birbiri ile çakışmıyorsa paralel agent çalıştırmanı istiyorum"):** dosya alanları
  çakışmayan paketler aynı anda koşar. Başlatmadan önce aşağıdaki kilit tablosuna paketin yazacağı alanı yaz; alanı
  başka bir koşan paketle kesişen iş başlatılmaz. Aynı anda en çok bir FreeCAD koşusu (makine). Commit yalnız ajan C'de
  ve açık `git add` listesiyle; iki C aynı anda commit atmaz. Paket bitince kilit satırı silinir.

### Kilit tablosu (koşan paketler)

| Paket | Ajan | Yazdığı alan |
|---|---|---|
| F2 (P2.1, P2.2) | C (commit + push + `F2-rapor.html` + karar kuyruğu K38–K41; kaynak dosyalara dokunmaz) |
| F4c (P4.3, P8.2) | A | `planlama/baski-listesi.md`, `planlama/y2/Y2b-baski.json` (betikle), `planlama/d158/F4c-*`; FreeCAD yok, git yazma yok | `tasarim/freecad/omuz/`, `arayuz.py` (yalnız omuz bloğu), `kabuk/` (durdurucu kabukta ise), `carpisma-bolum/omuz.json` + `carpisma-sonuc.json`, `planlama/d158/F2-*`, **FreeCAD makinesi** |

- **Tasarım sırası:** her adım öncekini bozmamalı; tam çakışma taraması yalnız P6'da, bir kez.
- **Karar gereken yerde durma:** Ahmet'in kararını isteyen madde `planlama/d158/karar-kuyrugu.md`'ye yazılır
  (seçenekler + önerilen varsayılan + etkisi). Döngü varsayılanla ilerlemez; o maddeye bağlı olmayan işe geçer.
- **Yapılmayacaklar (Ahmet'in onayı olmadan):** sipariş/satın alma; `main`'e birleştirme (Pages sitesi); dosya silme;
  geçmişi yeniden yazma; Efe'nin kod dosyalarını değiştirme; panoya **karar** yazma; e-posta/WhatsApp.
  Panoya yalnız soru ve bilgi yazılabilir (bkz. "Açık onaylar").
- **2209-B dosyalarına dokunulmaz** (`tubitak-2209b/`, v14 nihai; 08.11 Ahmet: "hiçbir değişiklik yapmanı istemiyorum").
- **Resmî/paylaşılan çıktıda** takma ad yazılmaz, Ahmet Yorulmaz yazılır.
- **Durma noktası:** her faz sonunda (F1, F2, …) Ahmet'e tek tablo özet; faz içinde soru sorulmaz.

**Açık onaylar (Ahmet, 08.11):** faz sonunda özet verilir, döngü beklemeden devam eder; panoya Efe için soru ve bilgi
mesajı döngü kendisi gönderebilir (karar asla); uzun taramalar (omuz, tam model) sırası gelince, saat fark etmeksizin koşar.

## 3. İş paketleri

Durum: ⏳ sırada · 🔄 çalışıyor · ✅ geçti · 🟡 koşullu geçti · ⛔ karar bekliyor

### Faz F0: Zemin (makine yükü düşük)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P0.1 | Commitlenmemiş 25 dosya + izlenmeyen klasörleri sınıflandır (rehber_metin.py +356 satır kimden?, `kvkk/`, `rapor/`, `raporlar/07-*`, `solidworks/`, `lale_dongu.FCMacro`). Projeye ait olanları konu başına ayrı commit; kaynağı belirsiz olanı karar kuyruğuna | `git status` yalnız bilinçli dışlananlar; her commit tek konu | – | ✅ |
| P0.2 | Karar kuyruğunu aç: aşağıdaki "Bilinen kararlar" listesini seçenek + varsayılan + etkiyle yaz | Her maddede en az 2 seçenek ve sayısal etki | P0.1 | ✅ |
| P0.3 | Regresyon betiği `d158/regresyon.py`: korunan değerleri JSON'lardan toplar, öncekiyle karşılaştırır | Bugünkü değerlerle koşar, hepsi "aynı" | P0.1 | ✅ |

### Faz F1: 158 modelini tutarlı yap (kafa ve gövde)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P1.1 | Akü 2,8 → 3,0 kg (Victron, malzeme listesi v4) modele; devrilme ve ivme yeniden | Rampa payı ≥ 1,5 kalır ya da sonuç karar kuyruğuna | – | ✅ |
| P1.2 | Modelde kalan MAX98357A'yı çıkar (04.11 karar: PAM8403 + USB ses kartı); `elektrik.md`'de PAM 5 V besleme noktası D24V50F5 olarak | Modelde ses yükseltici tek; kafa içi çakışma 0 | P1.1 | ✅ |
| P1.3 | AI HAT+ 26T'yi modele ekle (65 × 56,5, yığın 16, 30 g); arka üst cıvata boss'u çakışmasına (77,69 mm³) **iki çözüm** üret: boss taşı / HAT yönünü çevir | İki seçenek de çakışma 0; seçim karar kuyruğuna, varsayılan "boss taşı" | P1.1 | ✅ |
| P1.4 | Göğüs kablo tüpleri × göğüs ekranı (F0: SY8205 kesişimi zaten 0; HDMI 897,1 / 12 V 617,3 / USB 391,5 mm³ port ucunda): gerçek çakışmayı uç temasından ayır | kablo_tup_cakisma 0 | P1.3 | 🟡 girinti varsayımıyla 0 (HDMI 416,4 / 12 V 280,2 / USB 173,6 mm³ kasaya 12 mm iniş, port girintisi modelde yok); ekran gelince yeniden ölçülecek |
| P1.5 | `kabuk1.log` 16 × "Wire is not closed" kaynağını bul ve düzelt; `kabuk_rapor.py` `ekran_kontrol` KeyError → `kabuk/rapor.html` yenilensin (eski MAX satırı gider) | Temiz koşuda 0 satır | P1.1 | ✅ (kök neden: kesit düzlemi deliğe teğet; 0,05 mm kaydırma) |
| P1.6 | Eski metin ve betikler: `ikinci_ozet.py:142`, `lale158_rapor.py` "kasa↔çerçeve"; `kafa_rapor.py`, `kafa_gorsel.py` (125 cm, StopIteration) 158'e | İki betik hatasız koşar, rapor 158 sayılarıyla | P1.5 | ✅ |
| P1.7 | Hoparlör kabı arka tutucu + kelepçe (modelde yok) | Çakışma 0, baskı analizi 0 destek sorunu | P1.3 | ✅ |

### Faz F2: Omuz

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P2.1 | Omuz mekanik durdurucu (S2 alt sınır +5° (`arayuz.py:176`, 18.10; C1 kararındaki +3° eski)): servo bozulsa kol kabuğa vurmasın | Durdurucuda temas, kabukta 0; baskı analizi geçer | F1 ile | ✅ (diş 4,30°; kök yarıçapı P6.1'de) |
| P2.2 | Omuz bölümü çakışma taraması (QLED + çerçeve sonrası hiç koşmadı, ~4,8 sa makine) + `omuz_regresyon`, `iskelet_regresyon` | `tek_kosu: true`, çakışma 0 | – (makine dolu) | ✅ (20261109-033441; omuz/iskelet referansları eski, P6.1) |

### Faz F3: Yük ve hareket sınırları

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P3.1 | Düz zeminde elde yük sınırı: 0 / 50 / 100 / 200 / 500 g için devrilme payı ve servo payı tablosu | Tablo + önerilen sınır karar kuyruğuna | F2 ile | ✅ (karar K3/K9 Ahmet'te) |
| P3.2 | Servo payları 3,0 kg akü ve AI HAT+ sonrası yeniden (S1, S2, dirsek, bilek, pan, tilt) | Hepsi ≥ 1 ya da madde karar kuyruğuna | P3.1 | ✅ (karar K3/K9 Ahmet'te) |

### Faz F4: Elektrik ve belgeler 158 ile aynı dili konuşsun

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P4.1 | `elektrik.md`: hub yeri (gövde, üst arka göğüs servis kapağı içi; K5), boyun demeti (5 kablo: kafa 12 V, tilt servo, göğüs HDMI, hub uzatması, hoparlör; dokunmatik ve ESP32 USB gövdedeki hub'dan, göğüs 12 V tabandan — F4a A düzeltmesi), USB cihaz listesi (6. cihaz Efe cevabına göre); ses: PAM8403 + USB ses kartı, MAX98357A satırları :12, 21, 266 ve PAM besleme noktası (K10) | Belgedeki her sayı bir JSON'a ya da kaynağa bağlı | F1 sonrası | ✅ |
| P4.2 | Listede olmayan 6 kablo kalemini (USB dokunmatik ve 12 V için de 90° fiş, F1b B) aday olarak `maliyet.json`'a "koşullu" işaretle ekle (satıcı sayfası doğrulanmadan fiyat yazılmaz) | Genel toplam ve koşullu toplam ayrı | P4.1 | ✅ |
| P4.3 | Baskı listesi: hub takozlu kapak, 2 yeni kap parçası, VESA taşıyıcı malzemesi (PETG-CF) | `baski_listesi_guncelle.py` ile model aynı | P4.1 | ⏳ |
| P4.4 | README 1,65 → 1,58 m, `OZET.md`, `planlama/y2/Y2b-*.json` eski sayılar, `proje-plani.md` başlık sayıları | Depoda "1,65 m ana tasarım" ifadesi yalnız tarihçede | P4.1 | ✅ |
| P4.5 | Takma ad temizliği: kodda ~43 dosya (GitHub'a gidiyor) → "Ahmet Yorulmaz" ya da nötr | `git grep -i <takma ad>` yalnız tarihçe/hafıza dosyalarında | P4.4 | 🔄 (P4.5a: tarama kaynakları, `kod/`, `CLAUDE.md` hariç; onlar P6.1 öncesi) |

### Faz F5: Yazılım hizası (Efe'nin alanı; biz yalnız hazırlarız)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P5.1 | 10 servoluk kanal tablosu önerisi: ad, PCA9685 kanalı, açı sınırı (`eklem_sinirlari`), ev pozu, servo modeli (main'de 6: bilek ve omuz yana açma yok) | Her satır CAD sınırlarıyla aynı; `d158/servo-10-oneri.md` | F1 ile | ✅ |
| P5.2 | Kablo kuralı farkı: `yazilim-plani.md:64` "HDMI ve CSI boyundan geçmez" ↔ göğüs HDMI + dokunmatik boyundan geçiyor; Efe için tek sayfa not | Not hazır, pano mesajı taslağı | P5.1 | ✅ |
| P5.3 | Panoya bilgi + soru olarak gönder (karar yok) | Pano konusu açıldı | Onaya bağlı | ✅ |

### Faz F6: Tam model (eski Y4)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P6.1 | Önce `kabuk_parcalar.py:733` yorumu `72 x 10 kopru` → `70 x 10 kopru` (F1a B; tarama kaynağı olduğu için burada); `kafa_lib.py:265`, `dirsek_lib.py:141`, `omuz_baski.py:201`, `uygulama_tani.py:30` sessiz katman atlama kalıbına P1.5 kesit kaydırması (F1b B); göğüs ekranı port girintisini kasa modeline geometri olarak ekle (ekran ölçülünce, hariç tutma kutusu kalkar); F2 B: omuz durdurucu dişinin kök iç köşesine ≥ 1,5 mm yarıçap/pah (`omuz_parcalar.py`), "horn/dişli yük almaz" yorumlarını "tork almaz, radyal yük S2 mafsalında" diye düzelt, `arayuz.py:178` `yana_alt_bosluk_mm` eski "−3° kabuk" değerini 158 modeline (tambur 3,65°, diş 4,30°) güncelle ve `eklem_sinirlari.json`'u yeniden üret (Efe'ye bilgi); omuz ve iskelet regresyon referanslarını yenile (karar sonrası); sonra bütün modüller yeniden üretilir → tam çakışma taraması (tek koşu) → `eklem_dogrulama`, `montaj_gorsel`, modül görselleri | Çakışma 0, `tek_kosu: true`, korunan değerler aynı | – (makine ~2–6 sa) | ⏳ |
| P6.2 | Baskı analizi tüm parçalar; kapakta iki analizin uyuşmazlığı (19.667,7 mm² ↔ 5,01 mm²) çözülür | Tek analiz, tek sonuç | P6.1 sonrası | ⏳ |

### Faz F7: Montaj rehberi (eski Y5)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P7.1 | 3B rehber 158 modelinden yeniden üretilir (şu an ~%50, 1,65 m'den) | 48 + F5 adım, her adımda parça görünürlüğü doğru | P6 sonrası | ⏳ |
| P7.2 | Yazdırılabilir sürüm + kafa (QLED, ses, hub) adımları | PDF/HTML, konsol temiz, ekran görüntüleri | P7.1 | ⏳ |

### Faz F8: Sipariş ve üretim hazırlığı (sipariş verilmez)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P8.1 | 158 için güncel sipariş paketi (`maliyet.json` 11 fiyatsız aday; 90° HDMI/micro USB adaptörleri yanlışlıkla "ses" grubunda): hocadaki listeyle fark, satıcı sayfası ve stok doğrulaması, her kalem için ikinci satıcı | Fark tablosu + toplam; doğrulanmayan kalem işaretli | F4 sonrası | ✅ (kararlar K27–K37 Ahmet'te) |
| P8.2 | Baskı partileri (Parti 0–4): sıra, filament kg, süre, önce basılacak test kuponları | Partilerin toplamı baskı listesine eşit | P8.1 | ⏳ |
| P8.3 | Ölçüm ve test kâğıtları (ekip yapacak): JGB37 durma torku, QLED Power–Touch VBUS (Pi'ye takmadan), kafa 5 V akımı, PAM akımı, hub girişi gerilimi, akustik (Ø3 delik, yankı, servo gürültüsü) | Her test: amaç, malzeme, adım, kayıt tablosu, geçer sınırı | F1 ile | ✅ |

| P8.4 | Ek test kâğıtları (P8.3'ten çıkan; `00-genel.md:3` "kontrol bekliyor" satırı da güncellenir): K12 kafa ısı testi, H1 sigorta açıklığı ölçümü, perçin delik/somun ölçüsü, rampada acil stop (motor boşa düşünce yuvarlanma, `kararlar-2026-10-29.md:83`); P8.3 kontrol önerileri: T4 ilk dinlemede acil stop basılı, T1 seri multimetreyi çıkarmayı zorunlu yap | P8.3 biçiminde, sayısal geçer sınırı | P8.3 sonrası | ✅ |

### Faz F9: Takvim ve teslim

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P9.1 | `proje-plani.md` takvimi: H9 (23–29 Kas) ilk sürüş sipariş verilmeden gerçekçi değil → sipariş tarihine bağlı yeni takvim + kritik yol | Her hafta satırı bir bağımlılığa bağlı | F8 ile | ✅ |
| P9.2 | Demo sayfası 158 sayılarıyla (lale-duzeltme'de); `main`'e birleştirme yalnız onayla | Sayfa yerelde açılır, sayılar JSON ile aynı | P6 sonrası | ⏳ |
| P9.3 | Sonuç `rapor.html` + Ahmet'e özet tablo | Tüm paketlerin durumu, açık kararlar | En son | ⏳ |

## 4. Bilinen kararlar (P0.2 kuyruğa yazar)

| # | Karar | Önerilen varsayılan |
|---|---|---|
| K1 | Altıncı USB cihazı (Efe'ye soruldu, pano #5) | Cevap gelene kadar 5 cihaz + 2 boş hub portu |
| K2 | AI HAT+ çakışması: boss taşı / HAT yönü | Boss taşı |
| K3 | Düz zeminde elde yük sınırı | P3.1 tablosuna göre |
| K4 | 6 kablo kalemi listeye girsin mi | Koşullu kalem olarak gir |
| K5 | Hub ve ses kartı arka kabuk yan duvarında, servis için kabul mü | Kabul |
| K6 | Hoparlör duvara paralel / yatay eksene kama | Paralel (ölçüm sonrası yeniden) |
| K7 | Mikrofon dizisi kabuğun altında ("kafanın üstü" böyle kabul mü) | Kabul (boy 1.580 sınırı) |
| K8 | H1 sigorta açıklığı (Y3-kontrol) | Y3 notundaki öneri |
| K9 | El yükü 0,5 kg için servo değişimi mi, 100 g sınırı mı | 100 g sınırı |

## 5. Günlük

- 2026-11-09 F2 B: KOŞULLU GEÇER, kritik yok. Ölçüm bağımsız (temas 4,3003°, 5°'te 0,3436 mm, kol–kabuk en küçük 0,8309 mm), kontrol 0, regresyon --yazma 0, 34 dosya listesi birebir; "FARK VAR" eski referanslardan. Orta: (1) darbenin ~%88'i S2 mafsalına radyal (horn/rulman), yansıyan rotor ataleti dişliye stall'ın 1,4–2,1 katı; (2) emniyet varsayıma duyarlı (1,5 rad/s yüksüz 1,22–2,57), diş kökünde keskin iç köşe; (3) `arayuz.py:178` eski −3° değeri `eklem_sinirlari.json`'a gidiyor. **Orkestratör kararı:** düzeltme turu yok (kök yarıçapı omuz kaynağını değiştirir → 3,5 sa yeniden tarama); kök yarıçapı, yorumlar ve `yana_alt_bosluk_mm` P6.1'e eklendi (zaten tam tarama yapacak). C başladı: kaynak dosyalara dokunmadan commit, rapor emniyet ifadesi aralıkla, K38–K41.

- 2026-11-09 F2 A bitti (P2.1 + P2.2): omuz göbeğine PETG-CF diş, temas S2 4,30° (S2 5°'te 0,344 mm boşluk; kol–kabuk 0, en küçük 0,831 mm). Durdurucusuz ilk temas kabuk değil S1 tamburu (3,65°). Darbe emniyeti: stall 3,73, yüksüz 1,5 rad/s 2,24, 500 g 1,32, kaçak tam hız 0,54, 30°'den düşme 1,48 (KT-F2-1/2). Tarama 20261109-033441 tek koşu, 9 bölüm rc 0, eskimiş 0, ev pozu 0, aralıkta 0; omuz 3 sa 25 dk, bellek en düşük 4,51 GB. regresyon.py 0 (rampa 1,519). Omuz/iskelet regresyon "FARK VAR" (eski referanslar, F2 kaynaklı değil iddiası). Karar taslakları KT-F2-1…4. B kontrolde.

- 2026-11-09 **F8a ✅ (P8.1)** C: a35cab1, 76fd4b2 (maliyet.json V3 102.919,71 → 118.666,22; koşullu 124.573,11; elde düşülmüş 93.770,47), fbaa7ab, rapor 2879c86 push. Karar kuyruğu K27–K37 (açık 32 / 37). Sipariş verilmedi. P8.2 P4.3'ü, P4.3 F2'yi bekliyor.

- 2026-11-09 F8a B yeniden kontrol: KOŞULLU → 6 kısa metin (T1-1…T1-6) C'de, sonra GEÇER. Toplamlar ve 6 sayfa bağımsız tutuyor. maliyet.json'a 18 öneri (8 koşullu: kafa ekranı Ahmet'e bağlı; 10 ret). C başladı.

- 2026-11-09 F8a düzeltme 1 bitti: kıyas aynı esasla (+29.545 alınacaklar); M6×16 ikinci satıcı; insert 5,7 mm yok → A/B/C (Ahmet); akü: Atakale 16.11'de sınırda, bu hafta ya da Limacell (4.814,86, 3 gün) yetişir; maliyet.json önerileri uygulanabilir hâle. Ahmet listesi 14 madde. B yeniden kontrolde.

- 2026-11-09 F8a B: KOŞULLU. Toplamlar kuruşu kuruşuna, kritik fiyatlar tutuyor; ama maliyet.json kıyası yanlış esasta (doğrusu satın alınacaklarda +29.539, elde dahil +13.920; README ≈ 78.000'den ~29.500 fazla), M6×16 stok 2/18, insert 5,7 mm varyantı yok, akü yedeği Limacell atlanmış. Düzeltme 1 A'da. Ahmet'e 12 karar (hocadaki liste, bütçe farkı hocaya, erken alım, kafa ekranı hocadan mı).

- 2026-11-09 F8a A bitti: 136 satır, 94 tam doğrulandı; okul bütçesi 93.533,16 TL (%15 payla 107.563,13; maliyet.json'dan +4.643,42: iki ekran satın alınıyor, DS3235). Erken alım 1.515,90 TL (hâlâ geçerli). Kritik: akü stok 1 + 7 gün tedarik, ikinci satıcı yok; QLED stok 2; Kamera Module 3 tükendi; M5 mesafe burcu yok. Ahmet'e: hocadaki liste 17.10 mı v4 mü; erken alım okul mu kişisel mi. B kontrolde.

- 2026-11-09 F8a A (P8.1 sipariş paketi: fark tablosu, satıcı/stok doğrulaması, ikinci satıcı) başladı; 16.11 sipariş günü için öne alındı. Yalnız yeni dosyalar.

- 2026-11-09 **F4b ✅ (P4.5a)** C: c7f9af4 (63 dosya), 34d0cc0, rapor 0979d70 push; kalan 11 dosya (8 tarama kaynağı + `kod/` üretimi → P6.1; K25 `CLAUDE.md`; K26 hesap adı). **Orkestratör hatası:** `F4b-brief.md:5` takma adı harf harf yazıyordu, 34d0cc0 ile herkese açık dala girdi; satır düzeltildi (commit bekliyor: sonraki C), geçmişte kalır. regresyon.py artık --help/tanımsız bayrakta yazmıyor.

- 2026-11-09 F4b B: KOŞULLU GEÇER (195 satırın hepsi yalnız ad; tarama kaynaklarıyla kesişim boş; regresyon.py testleri tekrarlandı). Koşullar: 2 günlük cümlesi + commit öncesi numstat karşılaştırması (F2 çıktı yeniden üretebilir). `yerlesim_lib.py` tarama kaynağı değil → şimdi temizlenebilir. Ek: izlenmeyen `tasarim/solidworks/renkler.md:63` takma ad (K22 notu).

- 2026-11-09 F4b A bitti: 62 dosya / 197 satır (yalnız ad satırları); kalan 12 dosya: `CLAUDE.md` (karar), `kod/…eklem_sinirlari.json` (P6.1 üretim), 9 tarama kaynağı (P6.1), `tasarim/freecad/index.html` (GitHub hesap adı bağlantıda; karar). regresyon.py: --help/-h 0, tanımsız bayrak 2, dosyaya yazmıyor (sha aynı). B kontrolde. F2 omuz taraması sürüyor.

- 2026-11-09 **F4a ✅** C: 79fb383 (13 dosya), rapor 233ce00 push; maliyet 102.919,71 / koşullu 108.208,77. F4b A (P4.5a takma ad temizliği, tarama kaynakları hariç + regresyon.py --help koruması) başladı. P4.3 F2'yi bekliyor (durdurucu yeni baskı parçası).

- 2026-11-09 F4a B: KOŞULLU GEÇER (tüm sayılar kaynakla birebir; hub/boyun A haklı; 6 metin koşulu C'de: tilt ±13 tasarım / kod ±20 çerçevesi, F3 bitti, K2 açık listede, K14 işareti, 78.000 TL koşulu). K10 "sınırda değil" ölçülmeden yazılmaz.

- 2026-11-09 F4a A bitti: 7 belge 1,58'e; maliyet genel 103.767,58 → 102.919,71 (MAX çıktı), koşullu dahil 108.208,77; 11 fiyatsız aday (`fiyat_bekliyor`, toplam dışı). Orkestratör brief hatası: hub yeri ve boyun demeti kaynaklarla çelişiyordu, A kaynağa uydu; P4.1 satırı düzeltildi. Takma ad kalıntıları (17) P4.5'e. B kontrolde.

- 2026-11-09 **F3 ✅** C: 9cca013 (K3/K9 kuyruğa, öneri ≤ 100 g/el), rapor 1a319f2 push; pano #6 mesaj 17 (tilt ±20 çakışması bilgi + "±13 mümkün mü" sorusu). Koşan: F2 A, F4a A.

- 2026-11-09 F3a B: KOŞULLU (6 küçük metin koşulu, C'de). Yöntem ve sayılar bağımsız doğrulandı. Ek: ivmeli kol payı kaba tahmini 100 g/el S1 ≈ 1,1, 200 g/el < 1 → ≤ 100 g önerisini destekler. Tilt ±20 çakışması pano #6'ya bilgi olarak eklenecek.

- 2026-11-09 **F1 ✅** (P1.4 🟡: port girintisi varsayımı). **F1b ✅** C: regresyon 10/10 (rampa 1,519); f567ac2, fc8d7b5, 409d521, da17f1d, rapor 74cf048 push. F2 (omuz durdurucu + omuz taraması) ve F4a (elektrik, kablo kalemleri, README/OZET 1,58) A başladı; F3a B kontrolde.

- 2026-11-09 F1b B: KOŞULLU GEÇER. P1.1 ve P1.5 temiz (B kök nedeni buldu: kesit düzlemi yatay deliğe teğet). P1.4 ölçüm doğru ama 0, modelde olmayan port girintisi varsayımına bağlı → 🟡. `Y2b-ivme` farkının −0,047'si 03.11 ara çıktısının eski modelinden. Koşul 1 plana yazıldı; koşul 2 (`kabuk_montaj.py:338` yorumu + günlük açık 9) C'de.

- 2026-11-09 F3a A bitti (FreeCAD'siz, mevcut yöntemler saf Python; 0/100/500 g 18 anahtar birebir). Her elde: 50 g rampa 1,499 (< 1,5); 500 g S1/S2 0,97, dirsek 0,74. Öneri ≤ 100 g/el düzde, rampada yüksüz (servo 2× hedefi). Tilt kod ±20 güncel kafada çakışıyor (kafa-analiz 05.11: ±20'de 327,4 / 654,9 mm³, ±15 serbest; +18/−17° eski 29.10 modelinden). AI HAT+ ile yüksüz rampa 1,515. B kontrolde.

- 2026-11-09 F1b A bitti: akü 3,0 kg (rampa 1,517 → 1,519, devrilme açıları ≈ aynı); göğüs kablo hacimleri port ucu teması olarak ayrı alana (`kablo_tup_uc_temas`; USB 167,6 eksik ölçülmüş, doğrusu 391,5), gerçek çakışma 0; kabuk "Wire is not closed" 16 → 0 (0,05 mm kaydırma, geçici çare), kabuk_rapor çalışıyor. 8 bölüm yeniden tarandı, ev pozu 0. Regresyon 10/10 (A normal modda koştu, taban rampa 1,519). B kontrolde. Paralel: F3a A (P3.1 + P3.2, FreeCAD'siz).

- 2026-11-08 **F1a ✅** (B: KOŞULLU → koşul 1 plana, koşul 2 C'de). C: regresyon 10/10; 76a5701 (62 dosya), d37a671, 93089df, rapor 24a703d push. `F1a-kontrol.md:35` takma adı içerdiği için commit dışı → P4.5. P1.3 K2 kararı Ahmet'te. F1b A başladı.

- 2026-11-08 F1a B: KOŞULLU (geometri, çakışma, regresyon temiz). P1.2 kalanları → P4.2 maliyet.json:75 · P4.4 Lale-Proje-Ozeti.txt:68 · P5.2 yazilim-plani.md:23,114 · P7.1 rehber_metin.py:276 + rehber/veri · P9.2 Robot-Tasarim-Demosu.html · kabuk/rapor.html (kabuk_rapor.py KeyError → P1.5). K2 uygulanınca korunan tilt 3,64 → 3,30 (a) / 3,37 (b); regresyon tabanı o an güncellenir. Koşul 2 (f1a_rapor.py:216 72→70) C'de.

- 2026-11-08 F1a A bitti: P1.2 (MAX98357 kalıntıları), P1.3 (K2 seçenek a/b, ikisi çakışma 0, ana modele uygulanmadı), P1.6, P1.7 (hoparlör kelepçesi 4 g, desteksiz, çakışma 0). Bellek yüzünden yarım kalan kafa_sol + taban taraması tamamlandı: ev pozu 0, eskimiş bölüm yalnız omuz (P6). Regresyon 10/10. B kontrolde.

- 2026-11-08 **F5b ✅** (B: 1 tur → GEÇER; fren sorusu düzeltildi: sur'da 0,5 m/s² rampa var, dur/bekçi/yön bırakma rampasız). C: 5cc17c4 push; **pano #7** (soru, bekleyen efe). `F5b-gunluk.md` 63. satırdaki tarama notu yüzünden commit dışı → P4.5 ad temizliğinde. Efe'de açık: #5 (6. USB), #6 (10 servo), #7 (güvenlik/ses).

- 2026-11-08 **P8.4 ✅** C: K1/K2 uygulandı, f747bb0 + rapor 7e78b45 push. Küçük açık: 00-genel kural 1 "yandan uzanılır" ↔ T13 adım 4 ana yol "üst taraftan, arka köşeden" (sonraki test düzeltmesinde hizala). F5b A çalışıyor.

- 2026-11-08 P8.4 B: GEÇMEZ (T13 C) → 2 tur → GEÇER + K1/K2 (iki satır; B: ayrı tur gerekmez, diff yeter) → C uygular + kayıt. Kural notu: 2 tur sınırından sonra yalnız kontrolün metnini birebir verdiği ≤2 satırlık koşullar C'de uygulanabilir; daha fazlası karar kuyruğuna.

- 2026-11-08 P8.4 A bitti (T10–T13 + T1/T4 ekleri). B kontrolde. **Efe'ye toplu soru listesi (pano, P8.4 sonrası):** (1) ReSpeaker yankı giderme ayrı USB ses kartıyla referans alır mı; (2) yazılımda "devreden çıkar" (röle bırakma) komutu var mı; (3) elde taşınan uzaktan acil stop yok — donanım karşılığı tanımsız (T6, T8, T9, T13). Karar kuyruğu: K7 ana anahtar deliği ve perçin somun ayrı maddeler (`karar-kuyrugu.md:298`).

- 2026-11-08 **P9.1 ✅** C: 979b995, 92efdb0 (rapor), e700636 push.

- 2026-11-08 P9.1 B: 2 düzeltme turu → GEÇER. Sonuç: S=16.11 + erken alım (≈1.496 TL, 9.11 karar) + Parti 1 12.11 → demo 10.01; yoksa 20–24.01. C kayıtta.

- 2026-11-08 **P8.3 ✅** C: regresyon 10/10, fc9c651 + rapor 15b0a30 push. Not: remote sahibinin hesap adı takma ad (URL.de görünüyor; kapsam dışı, Ahmet.e bilgi verildi). regresyon.py `--help` tanımıyor, normal koşu yapıyor (C kazası, geri kuruldu) → P4 sırasında düzelt.

- 2026-11-08 P8.3 B: GEÇMEZ (T8/T9 güvenlik, multimetre) → 2 düzeltme turu → GEÇER (10/10 kâğıt). C kayıtta. P9.1 B: KOŞULLU (16.11 'Evet' erken alıma bağlı; lazer kritik yolda; kesinti 4 M6 ile çelişiyor; son sipariş ≈30.11) → düzeltme 1.

- 2026-11-08 **F5 ✅** (B: 2 düzeltme turu → GEÇER). C: regresyon 10/10, commit 4d242eb + rapor 3159125 push; pano #6 açıldı (soru, bekleyen efe). P9.1 A başladı.

- 2026-11-08 P8.3 A bitti: 9 kâğıt + testler.html (123 atıf). Bulgular: ReSpeaker yankı giderme ayrı ses kartıyla referans alamayabilir → Efe'ye soru (F5 sonrası pano); fan 3 dB çelişkisi; P8.4 eklendi. B kontrolde. F5 yeniden kontrolde. F1a A kabuk koşusunda.

- 2026-11-08 F5 A bitti: 10 servo tablosu (yeni kanallar 6–9), kod↔CAD 11 çelişki (en kritik: horn sıfır kayması kodda yok; tilt ±20↔±13; omuz 160↔135), kablo notu 4 soru, pano taslağı 1.563 kr. **P2.1 notu:** S2 alt sınırı güncel kaynakta +5° (`arayuz.py:176`), plandaki +3° eski olabilir → B doğruluyor. F1a A kabuk koşusunu bekliyor. P8.3 A çalışıyor.

- 2026-11-08 ~21:50 **F0 ✅** (B: 1. turda 3 KOŞULLU → düzeltme → GEÇER). C: regresyon 10/10 aynı; commit 8dcc4eb, 0b8a245, fa49caa, 680b965, 93da9af, c1bb4ed push. Bekleyen gruplar G4 (K24), G6 (K22), G7 (K23), G9 (K18–K22). Bulgu: göğüs kablo_tup_cakisma HDMI 897,1 / 12 V 617,3 / USB 167,6 mm³ → P1.4. F1a (kafa) A ajanı başladı.

- 2026-11-08 ~21:00 F0 ajan A bitti: 9 commit grubu (G1–G5 kararsız), karar kuyruğu 23 madde (18 açık, K8 ve K5 kapanmış), regresyon 10/10 aynı. Bulgu: P1.2 model kısmı zaten yapılmış; depo herkese açık → kvkk/, rapor/, tubitak-2209b/, satıcı dosyaları dışlanacak. Ajan B kontrolde.
- 2026-11-08 Ahmet: orkestratör iş yapmaz (ölçüm/commit ajana); PC kapanmaz (uyku zaten kapalı + uyku engelleyici süreç). 
- 2026-11-08 Plan yazıldı. Pano #5 (6. USB) Efe'de. Başlatma onayı bekleniyor.
