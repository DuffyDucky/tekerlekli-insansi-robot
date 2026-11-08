# F1a brief: kafa tutarlılığı (P1.2, P1.3, P1.6, P1.7) — 08.11.2026

Plan: `planlama/dongu-158.md` §3 F1. Karar kuyruğu: `planlama/d158/karar-kuyrugu.md`. Regresyon: `py -3 planlama/d158/regresyon.py`.
FreeCAD 1.1 başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py` ("ü"lü yolda freecadcmd doğrudan çöker; başlatıcıyı kullan).
Kafa yerleşim bağlamı: `tasarim/freecad/lale158/kafa-yerlesim/` (`uygulama-notu.md`, `secenekler.md`, `rapor.html`).

## P1.2 Eski ses yükseltici kalıntıları
F0 bulgusu: MAX98357A modelde ve BOM'da yok; yorumlarda, `kafa_rapor.py`'de ve eski 7" kodunda kalmış. Kalıntıları
PAM8403 + USB ses kartı düzenine göre düzelt (yalnız metin/yorum/rapor kodu; geometri değişmez).
**Kabul:** `git grep -n MAX98357` yalnız tarihçe belgelerinde (planlama günlükleri, raporlar/kaynaklar) kalır.

## P1.3 AI HAT+ 26T
Ölçü 65 × 56,5 mm, yığın 16 mm, 30 g (varsayım; üretici çizimi bulunursa onu kullan, kaynağını yaz). Pi 5 üstüne yığın.
Arka üst cıvata boss'u ile çakışma (77,69 mm³, `Arka kafa kabugu sag`) için **iki seçenek** üret: (a) boss'u taşı,
(b) HAT yönünü/yığını değiştir. Karar K2 Ahmet'te: **ana modele uygulama**; seçenekleri ayrı betik/parametre bayrağıyla
üret (`kafa-yerlesim/` altında `hat_secenek_a.py` / `_b.py` ya da bayrak), ana model bugünkü gibi kalsın.
**Kabul:** her seçenekte kafa içi çakışma 0, HAT–dizi/hava yolu açıklığı, vida erişimi (mm), kafa kütlesi ve tilt payı
(kafa-analiz yöntemiyle) tablo; seçenek görselleri (Opus ile üret). Karar kuyruğunda K2'ye sayıları ekle.

## P1.6 Eski betikler ve metinler
`ikinci_ozet.py:142` ve `lale158_rapor.py` içinde "kasa↔çerçeve" ifadesi; `kafa_rapor.py`, `kafa_gorsel.py` 125 cm
içerikli ve StopIteration ile düşüyor. 158 modeline göre düzelt.
**Kabul:** iki betik hatasız koşar; rapor 158 sayılarını (kafa grubu 1.570,8 g, tilt 3,64, pan 2,21) verir.

## P1.7 Hoparlör kabı arka tutucu
`uygulama-notu.md` "Kap varsayım: arka tüp açık çizimde, hoparlörü arkadan tutan yüzey ve kelepçe modelde yok".
Hoparlörü arkadan tutan yüzey + kelepçe/sıkıştırma tasarla (ana modele girer, K kararına bağlı değil).
**Kabul:** kafa içi çakışma 0; baskı analizi (`KL.baski_analiz` yöntemi) 0 destek sorunu; mikrofon-hoparlör ≥ 400 mm korunur.

## Korunan değerler
Her iş sonunda `regresyon.py` çıkış 0 olmalı (boy 1.580,0; çakışmalar 0; rampa ≥ 1,5; tilt ≥ 3,0; pan ≥ 2,0;
mik-hoparlör ≥ 400; SY8205 × kafa kabloları 0). Ana modelde kütle değişirse yeni değeri yaz.

## Kurallar
- Commit, push, dosya silme, checkout/reset/stash YOK (kayıt ajanı yapar).
- `tubitak-2209b/`, `kvkk/`, `rapor/` dokunulmaz. Efe'nin kodu (`kod/`) dokunulmaz.
- Bu brief'te olmayan iş yapma; fark ettiğin sorunu günlüğe yaz.
- Belgelerde kişi adı gerekiyorsa "Ahmet"; takma ad yazma.
- Günlük: `planlama/d158/F1a-gunluk.md` (dokunduğun her dosya, koştuğun her komut, ölçülen sayılar + JSON kaynağı, açıklar).
- Rapor taslağı: `tasarim/freecad/lale158/kafa-yerlesim/F1a-rapor.html` (özet kartları, görseller, açık işler).
