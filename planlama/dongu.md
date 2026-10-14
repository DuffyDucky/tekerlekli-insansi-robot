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
- Git commit yok, GitHub'a gönderme yok (K5 Release taşıması ve D8 depo temizliği Duffy'ye sorulacak; dışarı gönderim).
- Sipariş, satın alma, dışarı mesaj yok. Ölçüm gerektiren iş (JGB37 durma torku, zemin sürtünmesi) ekibin; varsayımla
  ilerle, varsayımı açıkça yaz.
- Tam çakışma taraması ve ana montaj yalnız 6. adımda, bir kez.
- Her adımın sonunda: kritik değerleri yeniden ölç, bu dosyayı güncelle, DuffyOS `Last-Session.md` kartını güncelle.

## Durum

| Sıra | İş | Durum | Not |
|---|---|---|---|
| 1 | 1. adım (M2, M3, M5, M8, C1–C3, C6, D3) | ✅ V kontrolü geçti | `planlama/adim1/` |
| 1b | G takip (kelepçe yarığı, eski sınır kodu, ≥0,5 kontrolleri, kabuk cam) | 🔄 Opus-1 | Windows güncellemesiyle kesilmişti |
| 2a | M1 kol kablo yolu (omuz, dirsek, kabuk) | 🔄 Opus-1 (G'den sonra) | `planlama/adim2/M1-kablo-yolu.md` |
| 2b | M4 omuz baskı analizi | 🔄 Opus-2 | `planlama/adim2/M4-omuz-baski.md`; M1 omuzu değiştirirse yeniden koşulur |
| 2c | Opus-2: G + M1 bağımsız kontrol | ⏳ | Opus-1 bitince |
| 3 | E0 (+K1 varsayımla), E1–E4, E7 taban ve güç **+ K4: Pi 5 kafaya** (kafa CAD, havalandırma, boyun kabloları, 12→5 V) | ⏳ | K4 kararı 14 Ekim: evet |
| 4 | M6 montaj sırası ve erişim, M7 kupon | ⏳ | Rehbere girdi olur |
| 5 | B1, B2, E8, E9, D6 malzeme ve plan | ⏳ | |
| 6 | Bütün modüller yeniden üretilir → C7 tam tarama (C5 ile) → D4 regresyon → D5 | ⏳ | Makine ~1,5 sa |
| 7 | D1, D2 belgeler (isteğe bağlı D7, C8, M9, M10; D8 ve K5 Duffy'ye sorulur) | ⏳ | |
| 8 | **3B montaj rehberi** (A: FreeCAD'den adım verisi, B: 3B adım adım rehber + PDF; kabuk öncesi kablolama kapısı) | ⏳ | Plan 11 Ekim'de sunuldu: DuffyOS `Last-Session.md` 11 Ekim "montaj rehberi planı" kartı; ayrıntı 11 Ekim oturum dökümü (Claude oturumu 2892de2f). Önce planı oku, sonra başla |
| 9 | Sonuç `rapor.html` + Duffy'ye özet tablo | ⏳ | |

## Günlük
- 2026-10-14 22:45 Döngü kuruldu. Opus-1 (G + M1) ve Opus-2 (M4) çalışıyor. K4 = Pi kafada.
