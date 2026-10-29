# Lale: otomatik iş döngüsü (14 Ekim 2026 akşam başladı)

Duffy uzun süre yok; kullanım limiti (5 saatlik) dolup yenilenecek. Orkestratör (Echo, Claude Code) her saat
uyanır, bu dosyayı okur ve sıradaki işi yürütür. **Bu dosya döngünün tek doğru kaynağıdır;** her adım
bitince buradaki durum güncellenir. Kesinti/limit olursa bir sonraki uyanış kaldığı yerden devam eder.

Duffy'nin talimatı: "tasarım planlayıcı bitene kadar planlama ve aksiyon döngüleri kur ... şuan yaptığın ve
bundan sonraki adımları falan bitirince tasarım planlayıcıya geç onu da yap". "Tasarım planlayıcı" = 3B montaj
rehberi (Duffy seçti, 14 Ekim).


> **DURAKLATILDI (15 Ekim 2026 akşam, Duffy):** "kablo makarasını yapanın işi bitince başka iş açma montaj rehberini de tamamen bitirme %50 bitince önemli bir checkpointte dur". Saatlik zamanlayıcı kapatıldı. S1 kontrolü bitince (geçerse) yalnız commit; yeni ajan yok. Rehber ~%50 checkpoint'te durur (`planlama/rehber/R-gunluk.md`). Devam için Duffy'nin yeni "başla"sı gerekir.

## Kurallar (her uyanışta geçerli)
- Oturum yeniden başlarsa eski ajanlar SendMessage ile devam ettirilemez ("No transcript found"): aynı brief + "önce günlüğü oku, yapılanı tekrarlama" ile yeni Opus ajanı başlat.
- Ajan düzeni: iki Opus ajanı (`model: opus`, general-purpose). Biri tasarım, biri analiz + bağımsız kontrol.
  Aynı dosyaya iki ajan aynı anda dokunmaz. Ana oturum iş yapmaz; brief yazar, sonucu doğrular, kritik değeri kendisi ölçer.
- Çalışan ajan varsa yenisini başlatma, aynı işi tekrar verme. Önce `planlama/adim*/` günlüklerine bak.
- **Git (Duffy, 14 Ekim: "githuba paralel git adım adım ilerledikçe push at büyük bir hata falan ile karşılaşırsak
  geri alması kolay olsun"):** çalışma dalı `lale-duzeltme`. Her adım (ya da alt iş) doğrulanınca orkestratör o işin
  dosyalarını commit'ler ve `git push` atar; mesaj `Lale: <adım> ...` + ne doğrulandı. Commit yalnız hiçbir ajan o
  dosyaları düzenlemiyorken atılır; ajanlar commit atmaz. Geri alma: `git revert <commit>` (gönderilmiş geçmiş yeniden
  yazılmaz). `main` (GitHub Pages sitesi) değişmez; dal sonunda Duffy onaylarsa squash-merge edilir (büyük dosyalar
  main'e bir kez girer). K5 Release taşıması ve D8 depo temizliği yine Duffy'ye sorulur.
- Sipariş, satın alma, dışarı mesaj yok. Ölçüm gerektiren iş (JGB37 durma torku, zemin sürtünmesi) ekibin; varsayımla
  ilerle, varsayımı açıkça yaz.
- Tam çakışma taraması ve ana montaj yalnız 6. adımda, bir kez.
- Her adımın sonunda: kritik değerleri yeniden ölç, bu dosyayı güncelle, DuffyOS `Last-Session.md` kartını güncelle.

## Durum

| Sıra | İş | Durum | Not |
|---|---|---|---|
| 1 | 1. adım (M2, M3, M5, M8, C1–C3, C6, D3) | ✅ V kontrolü geçti | `planlama/adim1/` |
| 1b | G takip (kelepçe yarığı, eski sınır kodu, ≥0,5 kontrolleri, kabuk cam) | ✅ `a158211` | Opus-2 kontrolü geçti |
| 2a | M1 kol kablo yolu | dirsek + S2 ✅ `a158211`; **S1 tasarım bitti (Opus-4), 🔄 Opus-8 bağımsız kontrol** | `adim2/S1-kaset.md`, `K2-s1-kontrol.md`. Kaset kabuk modülünde, omuz üstünden 26,4 mm taşıyor; S1 R_min 12,91 (7,5×d geçer, 10×d geçmez); uzatma kablosu iki kol ≈ 8,4 m (maliyete) |
| 2b | M4 omuz baskı analizi | ✅ `25de259` | 6/10 parça desteksiz basılamıyor (yuva, göbek, çatal). M1 omuzu değiştirirse betik yeniden koşulur. Açık: `omuz_parcalar.py` kütleyi %60 dolulukla hesaplıyor (kol başına 43–58 g eksik), FCStd'de 4 parça malzemesi PETG yazıyor (PETG-CF olmalı), yatay ısıl gömme kuponu yok → 2c/3–5. adımlarda ele alınacak; baskı listesi düzeltmeleri 5. adım (D6) |
| 2c | Opus-2: G + M1 bağımsız kontrol + S1 değerlendirme + tüp baskı | ✅ | `planlama/adim2/K-kontrol.md`; S1 bitince ikinci kontrol gerekecek |
| 3 | E0, E1–E4, E7 taban ve güç + K4 Pi 5 kafada | ✅ `7c87ff4` + takip `c299754` | **Risk:** JGB37 9 kg·cm ise standart tekerle dönemez, omniyle sınırda → ölçüm omni siparişinden önce. Açık: arayuz ESP32/PCA9685 bölgeleri eski V3 yerinde; Pololu 12 V akımı grafikten; perde/fan testi |
| 4 | M6 montaj sırası ve erişim, M7 kupon | ✅ analiz + kupon `6bb1eff`; ⏳ **M6 CAD** (C1 göbek-horn cıvatası, C2 dirsek servo kulağı, C3 kontra somun cepleri, K1/K2 dışarıdan vida + perçin somun, K3 ped yarığı + Ø84, K4 göğüs servis kapağı, K5 etek kapağı, K6 ana sigorta, K7 ana anahtar deliği) | S1 kontrolü bitince tasarım + kontrol ajanı; sonra `M6_erisim.py` yeniden |
| 5 | B1, B2, E8, E9, D6 malzeme ve plan | ✅ `15a4444` | Genel 99.147,48 TL (koşullular dahil 105.053,19). Yoğun kullanım 2,0 sa. Ön şarj K2 rölesi + 5,6 Ω (CAD'de yok → M6 CAD ile). CAD'e kalan bulgular `adim5/B-malzeme-plan.md` |
| 6 | Bütün modüller yeniden üretilir → C7 tam tarama (C5 ile) → D4 regresyon → D5 | ⏳ | Makine ~1,5 sa |
| 7 | D1, D2 belgeler (isteğe bağlı D7, C8, M9, M10; D8 ve K5 Duffy'ye sorulur) | ⏳ | |
| 8 | **3B montaj rehberi** (A: adım verisi, B: 3B sayfa + yazdırılabilir) | 🔄 Opus-10 altyapı + taslak (şimdiki CAD'den; 6. adımdan sonra tek komutla yeniden üretilecek) | `planlama/rehber/R-gunluk.md`, `rehber/`, `tasarim/freecad/rehber/`. İskelet: `adim4/M6-montaj-sirasi.md` (48 adım) |
| 9 | Sonuç `rapor.html` + Duffy'ye özet tablo | ⏳ | |

## 1,70 m planı (25 Ekim 2026, Duffy: "ana projeye 170den devam edeceğiz", "tamam onaylıyorum go brr")

Ana tasarım artık `tasarim/freecad/taslak-170/` (kol ×1,25 + omuz DS3235, dirsek çatalı dış kol 8 mm). Duffy'nin onayladığı
ek kararlar: **göğüs Nextion kaldırılır**, **taban 520 mm + akü 75 mm öne**, **gövde direği 2 m boydan tek parça**. Ölçüm
bekleyenler (varsayımla ilerlenir, açıkça yazılır): JGB37 durma torku, kafa 5 V akımı (Pi 5 + 10" ekran), omuz servo hattı akımı.
Push yok (Duffy: "şimdilik yerelde kalsın"); her doğrulanan adım yerel commit. Kurallar yukarıdakiyle aynı (iki Opus ajanı).

| Sıra | İş | Durum |
|---|---|---|
| Y1 | S1 kablo kaseti bağımsız kontrolünü bitir (`adim2/K2-s1-kontrol.md`, WIP `834b386`) | ✅ KOŞULLU GEÇTİ (125 + 170); K1–K6 düzeltmeleri Y1b |
| Y1b | S1 düzeltmeleri K1–K6 + ikinci pim + S2 kablosu göbekte | ✅ KOŞULLU GEÇTİ (`adim2/K3-s1-duzeltme-kontrol.md`); kalan KZ1 `duvar.pim.bosluk` 0,5→1,0, KZ2 tambur ip deliği ≥0,8 mm, S1-kaset.md belge düzeltmeleri → Y2a'ya |
| Y2a | CAD: taslağı ana montaja taşı (arayuz + modüller + montaj; Nextion yok, taban 520 + akü 75 öne, direk 2 m stok) + KZ1/KZ2 | ✅ KOŞULLU GEÇTİ (`planlama/y2/Y2a-kontrol.md`; KZ1 akü yeri/devrilme, KZ2 servo el yükü, KZ3 tilt payı, KZ4 kafa kabuğu desteği → Duffy kararı / Y2b). **Kararlar 29.10** (`planlama/kararlar-2026-10-29.md`): KZ1 akü yerinde + rampada kollar ev pozu + ivme ≤ 0,1 m/s²; KZ3 tilt ±13; KZ4 dikiş aynı, destekli baskı; KZ2 açık |
| Y2b | Veri/belge: eklem_sinirlari, maliyet.json, baskı listesi, elektrik/akü, README, proje planı, demodan lidar/otonomi | ✅ **KOŞULLU GEÇTİ** (`planlama/y2/Y2b-kontrol.md`, `ee6c0a1`); **kararlar alındı 29.10** (`planlama/kararlar-2026-10-29.md` 5–9: fren ≤ 1,8 m/s², kollar ayrı + kafa servoları üçüncü XL4016 (genel 109.001,35 TL), akü gereksinimi 2 sa (yoğun 1,83 kabul), sipariş verilmedi / liste hocada → `planlama/siparis-farki-2026-10-29.md`). Tasarım (`planlama/y2/Y2b-gunluk.md`): maliyet genel **108.670,84 TL** (önce 99.673,04; koşullularla 114.636,55), baskı 63 parça 7,71–7,77 kg, düz zemin devrilme sınırı ≈ 2,0 m/s² (kural ≤ 0,5 sürer; rampada ≤ 0,1), elektrik 1,65 m tablosu + E8 (yoğun 1,8 sa), demodan lidar kaldırıldı. `kabuk_rapor.py` (Nextion) → Y4 |
| Y3 | M6 CAD (erişim düzeltmeleri, eski 4. adımdaki liste) | ✅ **KOŞULLU GEÇTİ (kontrol düzeltmeleri yapıldı)** (`planlama/y3/Y3-kontrol.md`, `planlama/y3/Y3-gunluk.md`, brief `Y3-brief.md`). Önce 29.10 kararları `59367ab` (rampada fren ≤ 0,1; Pi 5 4 GB). C1 göbek–horn Ø6 kanal (kontrolden sonra Ø5 → Ø6: cıvata başı Ø5,5 geçer), C2 ön kol Ø8 erişim + 4 somun cebi, C3 S2 ve tilt somun cepleri → 125 cm'deki YOK bağlantılar (modülde 10 / robotta 19, `adim4/M6-montaj-sirasi.md:38`) 0 (`Y3_erisim.py`); K1 / K2 braketler dışarıdan ISO 7380 + perçin somun, K3 ped yarığı Ø84'e, K4 üst arka servis kapağı (y 1100…1268), K5 / K6 etek kapakları H1 (sigorta kutusu) / H2 (ana sigorta), K7 ana anahtar deliği Ø30 (tahmini); taban: XL4016 C (kafa hattı) + ön şarj kartı (K2 + 5,6 Ω) güç panelinde. Modüller (omuz, dirsek, kafa, kabuk, taban) + ana montaj yeniden: 1.120 parça, 24.554 g, AM (−0,08; 525,80; −12,49), modül çakışmaları 0, yerleşim kontrolü 0; maliyet genel 103.767,58 TL. Duffy kararı bekleyen: H1 sigorta açıklığı, K1 M5×16 boyu (`Y3-kontrol.md`). Tam tarama ve M6_erisim yeniden koşusu (`ISO7380_S` M5 eklendi) → Y4 |
| Y4 | Tüm modüller yeniden üretilir → tam çakışma taraması → regresyon (eski 6. adım) | ⏳ |
| Y5 | 3B montaj rehberi 1,70 m'den yeniden üretilir ve tamamlanır (eski 8. adım) | ⏳ |
| Y6 | Belgeler + sonuç `rapor.html` (eski 7. ve 9. adım) | ⏳ |

## Günlük
- 2026-10-14 22:45 Döngü kuruldu. Opus-1 (G + M1) ve Opus-2 (M4) çalışıyor. K4 = Pi kafada.
- 2026-10-14 22:55 `lale-duzeltme` dalı açıldı, `c531c59` gönderildi (11 Ekim planları + 1. adımın ajan dışı kısmı).
  Ajanların dosyaları (arayuz, dirsek, omuz, kabuk, iskelet_montaj, eklem_dogrulama, montaj_gorsel, adim2, G-takip)
  2. adım kaydına girecek. 11 Ekim'den kalmış boş `.git/index.lock` silindi.
- 2026-10-14 23:05 M4 bitti, `25de259`. G'nin dört maddesi Opus-1 günlüğünde tamam (doğrulanmadı).
- 2026-10-14 ~23:50 Opus-1 M1 ortasında oturum limitine takıldı (yenilenme 03:30).
- 2026-10-15 03:31 Opus-1 SendMessage ile devam ettirildi (aynı ajan, günlüğünden).
- 2026-10-15 03:40 Opus-1 bitti (G tamam, M1 dirsek+S2 tamam, S1 açık). Opus-2 kontrol + S1 değerlendirme; Opus-3 (yeni, taze bağlam) 3. adım. S1 tasarımı Opus-2 önerisinden sonra.
- 2026-10-15 ~04:20 Opus-2 kontrolü geçti → `a158211` (arayuz.py'den yalnız 1./2. adım parçaları; 3. adımın taban/elektrik parçaları dışarıda). S1 kararı (orkestratör): A′ döner U-lop kaseti (bedeli: yay duvarı omuz üstünden ~40 mm görünür). Opus-4 S1'i uyguluyor; Opus-3 3. adımda.
- 2026-10-15 ~04:45 Opus-3 bitti (taban 316 parça 7.529 g, kafa 115 parça 1.431 g, robot 21,71 kg, maliyet +2.767 TL). Opus-5 3. adımı kontrol ediyor; Opus-4 S1'de.
- 2026-10-15 ~05:00 Opus-4 ve Opus-5 oturum limitine takıldı (yenilenme 08:30). 08:31 ikisi de SendMessage ile devam ettirildi.
- 2026-10-15 ~08:50 Opus-5 kontrolü geçti → `7c87ff4` (arayuz.py'den yalnız 3. adım parçaları). Opus-6 takip düzeltmeleri; Opus-4 S1'de.
- 2026-10-15 ~09:20 Opus-6 bitti, orkestratör kontrolü (VBUS metni yok, kafa 44/44, taban aynı) → `c299754`. Opus-7 4. adım (M7 + M6 analizi); Opus-4 S1'de.
- 2026-10-15 ~09:40 Opus-4 ve Opus-7 oturum limitine takıldı (yenilenme 13:30). 13:31 ikisi de devam ettirildi.
- 2026-10-15 ~14:00 Opus-4 S1'i bitirdi (omuz 73, kabuk 206 parça). Opus-8 S1 kontrolü; Opus-7 M6 analizinde.
- 2026-10-15 ~14:30 Opus-7 bitti → `6bb1eff` (M7 kupon + M6 analizi; D1 kuponu FCStd ile fark 0). Opus-9 5. adım; Opus-8 S1 kontrolü. M6 CAD, S1 kontrolünden sonra.
- 2026-10-15 ~14:40 Opus-8 ve Opus-9 limite takıldı (yenilenme 18:30). Oturum yeniden başlamış, eski ajanlar devam ettirilemedi → 18:35 yeni Opus-8b (S1 kontrolü, K2-*.json'dan devam) ve Opus-9b (5. adım, günlükten devam). Uyanık tutma süreçleri (17020, 24440) hâlâ çalışıyor.
- 2026-10-15 ~19:15 Opus-9b bitti → `15a4444` (toplam betikle doğrulandı). Opus-10 montaj rehberi altyapısı (CAD'i yalnız okur); Opus-8b S1 kontrolünde. M6 CAD, S1 kontrolünden sonra.
- 2026-10-15 ~19:30 Duffy duraklattı (yukarıdaki not). Zamanlayıcı silindi; Opus-10'a %50 checkpoint talimatı gönderildi.
- 2026-10-15 ~23:30 PC reset: Opus-8b (S1 kontrolü) yarıda kaldı, `K2-s1-kontrol.md` kapanmadı (son tarama 22:16). Duffy: limit %82, sonra devam. Devamda yeni ajan günlükten başlar.
- 2026-10-25 1,70 m planı kuruldu (yukarıda). Y1: S1 kontrolü yeni Opus ajanıyla, `K2-s1-kontrol.md` günlüğünden devam.
- 2026-10-25 Y1 bitti: KOŞULLU GEÇTİ. 6 ev pozu çakışması modelleme artığı (S2 0°, kol 3,6°'de dayanıyor). Uzatma kablosu taslakta ~12,3 m. Y1b tasarım ajanı başlıyor.
- 2026-10-26 Y1b kontrol: KOŞULLU GEÇTİ (K4 sınırlayanı pim dikmesi; u_pay 7,0 işe yaramaz, pim boşluğu 1,0 önerildi). Y2 ikiye bölündü (Y2a CAD, Y2b veri/belge).
- 2026-10-29 Y2b (veri/belge) tasarım işi bitti, tek yerel commit; bağımsız kontrol sırada. Ayrıntı `planlama/y2/Y2b-gunluk.md`.
- 2026-10-29 Y2b kontrolü KOŞULLU GEÇTİ (`ee6c0a1`); Duffy kararları işlendi (kararlar 5–9), sipariş farkı çıkarıldı; push (Duffy: "önerdiğin gibi yap, pushla").
- 2026-10-29 29.10 kararları (rampada fren ≤ 0,1, Pi 5 4 GB) `59367ab`; Y3 (M6 CAD) tasarım işi bitti, tek yerel commit; bağımsız kontrol sırada. Ayrıntı `planlama/y3/Y3-gunluk.md`.
