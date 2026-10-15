# Lale: otomatik iş döngüsü (14 Ekim 2026 akşam başladı)

Duffy uzun süre yok; kullanım limiti (5 saatlik) dolup yenilenecek. Orkestratör (Echo, Claude Code) her saat
uyanır, bu dosyayı okur ve sıradaki işi yürütür. **Bu dosya döngünün tek doğru kaynağıdır;** her adım
bitince buradaki durum güncellenir. Kesinti/limit olursa bir sonraki uyanış kaldığı yerden devam eder.

Duffy'nin talimatı: "tasarım planlayıcı bitene kadar planlama ve aksiyon döngüleri kur ... şuan yaptığın ve
bundan sonraki adımları falan bitirince tasarım planlayıcıya geç onu da yap". "Tasarım planlayıcı" = 3B montaj
rehberi (Duffy seçti, 14 Ekim).

## Kurallar (her uyanışta geçerli)
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
| 2a | M1 kol kablo yolu (omuz, dirsek, kabuk) | ◐ dirsek + S2 ✅ `a158211`; **S1 🔄 Opus-4** (A′ döner U-lop kaseti, S2 alt sınır 5°, eski 'yana 0' kalıntıları, omuz kütle dolulukla) | `planlama/adim2/S1-kaset.md`; sonra bağımsız kontrol + commit |
| 2b | M4 omuz baskı analizi | ✅ `25de259` | 6/10 parça desteksiz basılamıyor (yuva, göbek, çatal). M1 omuzu değiştirirse betik yeniden koşulur. Açık: `omuz_parcalar.py` kütleyi %60 dolulukla hesaplıyor (kol başına 43–58 g eksik), FCStd'de 4 parça malzemesi PETG yazıyor (PETG-CF olmalı), yatay ısıl gömme kuponu yok → 2c/3–5. adımlarda ele alınacak; baskı listesi düzeltmeleri 5. adım (D6) |
| 2c | Opus-2: G + M1 bağımsız kontrol + S1 değerlendirme + tüp baskı | ✅ | `planlama/adim2/K-kontrol.md`; S1 bitince ikinci kontrol gerekecek |
| 3 | E0, E1–E4, E7 taban ve güç + K4 Pi 5 kafada | ✅ `7c87ff4` (Opus-5 kontrolü geçti); 🔄 Opus-6 takip düzeltmeleri | `adim3/K3-kontrol.md`, `T2-takip.md`: ESP32 USB metni, eski Pi metinleri, elektrik notları, kafa çıkış yarıkları üste, JGB37 9 kg·cm senaryosu. **Risk:** JGB37 durma torku etiketi belirsiz → ölçüm omniden önce |
| 4 | M6 montaj sırası ve erişim, M7 kupon | ⏳ | Rehbere girdi olur |
| 5 | B1, B2, E8, E9, D6 malzeme ve plan | ⏳ | |
| 6 | Bütün modüller yeniden üretilir → C7 tam tarama (C5 ile) → D4 regresyon → D5 | ⏳ | Makine ~1,5 sa |
| 7 | D1, D2 belgeler (isteğe bağlı D7, C8, M9, M10; D8 ve K5 Duffy'ye sorulur) | ⏳ | |
| 8 | **3B montaj rehberi** (A: FreeCAD'den adım verisi, B: 3B adım adım rehber + PDF; kabuk öncesi kablolama kapısı) | ⏳ | Plan 11 Ekim'de sunuldu: DuffyOS `Last-Session.md` 11 Ekim "montaj rehberi planı" kartı; ayrıntı 11 Ekim oturum dökümü (Claude oturumu 2892de2f). Önce planı oku, sonra başla |
| 9 | Sonuç `rapor.html` + Duffy'ye özet tablo | ⏳ | |

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
