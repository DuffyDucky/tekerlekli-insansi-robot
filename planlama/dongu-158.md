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
| P0.1 | Commitlenmemiş 25 dosya + izlenmeyen klasörleri sınıflandır (rehber_metin.py +356 satır kimden?, `kvkk/`, `rapor/`, `raporlar/07-*`, `solidworks/`, `lale_dongu.FCMacro`). Projeye ait olanları konu başına ayrı commit; kaynağı belirsiz olanı karar kuyruğuna | `git status` yalnız bilinçli dışlananlar; her commit tek konu | – | ⏳ |
| P0.2 | Karar kuyruğunu aç: aşağıdaki "Bilinen kararlar" listesini seçenek + varsayılan + etkiyle yaz | Her maddede en az 2 seçenek ve sayısal etki | P0.1 | ⏳ |
| P0.3 | Regresyon betiği `d158/regresyon.py`: korunan değerleri JSON'lardan toplar, öncekiyle karşılaştırır | Bugünkü değerlerle koşar, hepsi "aynı" | P0.1 | ⏳ |

### Faz F1: 158 modelini tutarlı yap (kafa ve gövde)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P1.1 | Akü 2,8 → 3,0 kg (Victron, malzeme listesi v4) modele; devrilme ve ivme yeniden | Rampa payı ≥ 1,5 kalır ya da sonuç karar kuyruğuna | – | ⏳ |
| P1.2 | Modelde kalan MAX98357A'yı çıkar (04.11 karar: PAM8403 + USB ses kartı); `elektrik.md`'de PAM 5 V besleme noktası D24V50F5 olarak | Modelde ses yükseltici tek; kafa içi çakışma 0 | P1.1 | ⏳ |
| P1.3 | AI HAT+ 26T'yi modele ekle (65 × 56,5, yığın 16, 30 g); arka üst cıvata boss'u çakışmasına (77,69 mm³) **iki çözüm** üret: boss taşı / HAT yönünü çevir | İki seçenek de çakışma 0; seçim karar kuyruğuna, varsayılan "boss taşı" | P1.1 | ⏳ |
| P1.4 | USB dokunmatik kablo yolu SY8205 kartından geçiyor (249,7 mm³): şema yolunu kartın yanından geçir | kablo_tup_cakisma 0 | P1.3 | ⏳ |
| P1.5 | `kabuk1.log` 16 × "Wire is not closed" kaynağını bul ve düzelt | Temiz koşuda 0 satır | P1.1 | ⏳ |
| P1.6 | Eski metin ve betikler: `ikinci_ozet.py:142`, `lale158_rapor.py` "kasa↔çerçeve"; `kafa_rapor.py`, `kafa_gorsel.py` (125 cm, StopIteration) 158'e | İki betik hatasız koşar, rapor 158 sayılarıyla | P1.5 | ⏳ |
| P1.7 | Hoparlör kabı arka tutucu + kelepçe (modelde yok) | Çakışma 0, baskı analizi 0 destek sorunu | P1.3 | ⏳ |

### Faz F2: Omuz

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P2.1 | Omuz mekanik durdurucu (S2 alt sınır +3°, C1 kararı): servo bozulsa kol kabuğa vurmasın | Durdurucuda temas, kabukta 0; baskı analizi geçer | F1 ile | ⏳ |
| P2.2 | Omuz bölümü çakışma taraması (QLED + çerçeve sonrası hiç koşmadı, ~4,8 sa makine) + `omuz_regresyon`, `iskelet_regresyon` | `tek_kosu: true`, çakışma 0 | – (makine dolu) | ⏳ |

### Faz F3: Yük ve hareket sınırları

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P3.1 | Düz zeminde elde yük sınırı: 0 / 50 / 100 / 200 / 500 g için devrilme payı ve servo payı tablosu | Tablo + önerilen sınır karar kuyruğuna | F2 ile | ⏳ |
| P3.2 | Servo payları 3,0 kg akü ve AI HAT+ sonrası yeniden (S1, S2, dirsek, bilek, pan, tilt) | Hepsi ≥ 1 ya da madde karar kuyruğuna | P3.1 | ⏳ |

### Faz F4: Elektrik ve belgeler 158 ile aynı dili konuşsun

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P4.1 | `elektrik.md`: hub yeri, boyun demeti (göğüs HDMI + USB dokunmatik), USB cihaz listesi (6. cihaz Efe cevabına göre) | Belgedeki her sayı bir JSON'a ya da kaynağa bağlı | F1 sonrası | ⏳ |
| P4.2 | Listede olmayan 6 kablo kalemini aday olarak `maliyet.json`'a "koşullu" işaretle ekle (satıcı sayfası doğrulanmadan fiyat yazılmaz) | Genel toplam ve koşullu toplam ayrı | P4.1 | ⏳ |
| P4.3 | Baskı listesi: hub takozlu kapak, 2 yeni kap parçası, VESA taşıyıcı malzemesi (PETG-CF) | `baski_listesi_guncelle.py` ile model aynı | P4.1 | ⏳ |
| P4.4 | README 1,65 → 1,58 m, `OZET.md`, `planlama/y2/Y2b-*.json` eski sayılar, `proje-plani.md` başlık sayıları | Depoda "1,65 m ana tasarım" ifadesi yalnız tarihçede | P4.1 | ⏳ |
| P4.5 | Takma ad temizliği: kodda ~43 dosya (GitHub'a gidiyor) → "Ahmet Yorulmaz" ya da nötr | `git grep -i <takma ad>` yalnız tarihçe/hafıza dosyalarında | P4.4 | ⏳ |

### Faz F5: Yazılım hizası (Efe'nin alanı; biz yalnız hazırlarız)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P5.1 | 10 servoluk kanal tablosu önerisi: ad, PCA9685 kanalı, açı sınırı (`eklem_sinirlari`), ev pozu, servo modeli (main'de 6: bilek ve omuz yana açma yok) | Her satır CAD sınırlarıyla aynı; `d158/servo-10-oneri.md` | F1 ile | ⏳ |
| P5.2 | Kablo kuralı farkı: `yazilim-plani.md:64` "HDMI ve CSI boyundan geçmez" ↔ göğüs HDMI + dokunmatik boyundan geçiyor; Efe için tek sayfa not | Not hazır, pano mesajı taslağı | P5.1 | ⏳ |
| P5.3 | Panoya bilgi + soru olarak gönder (karar yok) | Pano konusu açıldı | Onaya bağlı | ⏳ |

### Faz F6: Tam model (eski Y4)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P6.1 | Bütün modüller yeniden üretilir → tam çakışma taraması (tek koşu) → `eklem_dogrulama`, `montaj_gorsel`, modül görselleri | Çakışma 0, `tek_kosu: true`, korunan değerler aynı | – (makine ~2–6 sa) | ⏳ |
| P6.2 | Baskı analizi tüm parçalar; kapakta iki analizin uyuşmazlığı (19.667,7 mm² ↔ 5,01 mm²) çözülür | Tek analiz, tek sonuç | P6.1 sonrası | ⏳ |

### Faz F7: Montaj rehberi (eski Y5)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P7.1 | 3B rehber 158 modelinden yeniden üretilir (şu an ~%50, 1,65 m'den) | 48 + F5 adım, her adımda parça görünürlüğü doğru | P6 sonrası | ⏳ |
| P7.2 | Yazdırılabilir sürüm + kafa (QLED, ses, hub) adımları | PDF/HTML, konsol temiz, ekran görüntüleri | P7.1 | ⏳ |

### Faz F8: Sipariş ve üretim hazırlığı (sipariş verilmez)

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P8.1 | 158 için güncel sipariş paketi: hocadaki listeyle fark, satıcı sayfası ve stok doğrulaması, her kalem için ikinci satıcı | Fark tablosu + toplam; doğrulanmayan kalem işaretli | F4 sonrası | ⏳ |
| P8.2 | Baskı partileri (Parti 0–4): sıra, filament kg, süre, önce basılacak test kuponları | Partilerin toplamı baskı listesine eşit | P8.1 | ⏳ |
| P8.3 | Ölçüm ve test kâğıtları (ekip yapacak): JGB37 durma torku, QLED Power–Touch VBUS (Pi'ye takmadan), kafa 5 V akımı, PAM akımı, hub girişi gerilimi, akustik (Ø3 delik, yankı, servo gürültüsü) | Her test: amaç, malzeme, adım, kayıt tablosu, geçer sınırı | F1 ile | ⏳ |

### Faz F9: Takvim ve teslim

| Kod | İş | Kabul ölçütü | Paralel | Durum |
|---|---|---|---|---|
| P9.1 | `proje-plani.md` takvimi: H9 (23–29 Kas) ilk sürüş sipariş verilmeden gerçekçi değil → sipariş tarihine bağlı yeni takvim + kritik yol | Her hafta satırı bir bağımlılığa bağlı | F8 ile | ⏳ |
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

- 2026-11-08 ~21:00 F0 ajan A bitti: 9 commit grubu (G1–G5 kararsız), karar kuyruğu 23 madde (18 açık, K8 ve K5 kapanmış), regresyon 10/10 aynı. Bulgu: P1.2 model kısmı zaten yapılmış; depo herkese açık → kvkk/, rapor/, tubitak-2209b/, satıcı dosyaları dışlanacak. Ajan B kontrolde.
- 2026-11-08 Ahmet: orkestratör iş yapmaz (ölçüm/commit ajana); PC kapanmaz (uyku zaten kapalı + uyku engelleyici süreç). 
- 2026-11-08 Plan yazıldı. Pano #5 (6. USB) Efe'de. Başlatma onayı bekleniyor.
