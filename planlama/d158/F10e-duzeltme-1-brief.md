# F10e düzeltme turu 1 (P10.4b), 12.11.2026

Bağımsız kontrol (B) hükmü: **DÜZELTME GEREKLİ**. Rapor: `planlama/d158/F10e-kontrol.md` (önce tamamını oku; ölçüm yöntemleri ve
kanıt kareleri orada). Rehberde engelleyici bozulma yok; düzeltilecekler aşağıda. Paket çalışma ağacında, commit edilmedi
(dal `lale-duzeltme`, HEAD `90c270a`). Paketi yapan uygulama ajanı artık yok; sen onun yerine devam ediyorsun.

Önce oku: `F10e-kontrol.md`, `F10e-brief.md` (iş, kabul, **Kurallar bölümü bu turda da aynen geçerli**: yazılabilir alanlar,
dokunulmazlar, bellek / FreeCAD, yapma listesi, yazım kuralları), `F10e-gunluk.md` (özellikle §0 komut tablosu, §5, §6, §8).
B'nin ham ölçüm betikleri scratchpad'de `f10e-b/` ve `f10e-b2/` klasörlerinde (salt oku; yöntemini kendi doğrulamana alabilirsin).

## Düzeltilecekler

1. **Koyu temada görünürlük (kontrol bulgu 1).** "Okurun pikseli" ölçümü yalnız açık temada koşuyor (`F10e-dogrula.py`,
   `tema=light`). Koyu temada kabuk alt adımlarının 212 yeni parçasından 20'si eşik altında, 6 bindirme cıvatası 0–3 px
   (34.3 p0244, 34.4 p0242, 34.5 p0256, 34.6 p0254, 35.1 p0280, 35.2 p0282). İstenen: (a) ölçüm iki temada koşsun ve geçme şartına
   girsin; (b) koyu temada bu parçalar görünür olsun (eşik: ≥ 30 px ve tek başına çizilişin ≥ %20'si; gerekçeli istisna yalnız
   gerçekten başka parçanın içinde / arkasında kalan için, parça kimliği ve nedeniyle). Kök nedeni bul (kenar kuralı mı, renk ↔ zemin
   mi, saydamlık sırası mı); gerçek rengi değiştirmeden çöz (kenar çizgisi, zemin, ışık gibi).
2. **31.3 `p0762` (bulgu 2).** Günlük "40 / 142 px, geçti" diyor; gerçek ekran görüntüsünde parçayı gizlemek eşiği aşan 0 piksel
   değiştiriyor. Önce senin ölçüm fonksiyonunun neden ekran görüntüsünden farklı verdiğini bul (B bunu çözemedi); fonksiyon
   yanlışsa onu düzelt ve bütün kabuk alt adımlarını düzeltilmiş ölçümle yeniden koş (başka gizli parça çıkabilir). Sonra parçayı
   karede görünür yap.
3. **34.7 (bulgu 3).** Hoparlör grubu karede ≈ 80 px, katmanlar ayırt edilmiyor. Kamera / kadraj / saydamlık ile iyileştirmeyi
   dene. Olmuyorsa "zor" olarak bırak ve günlükte öyle yaz (kabul eşiği zor ≤ 2; sayım dürüst olsun: B'ye göre açık 40, zor 2).
   Günlükteki "hoparlör kara" ifadesini karede görülene göre düzelt.
4. **Benzer kare çiftleri (bulgu 4).** 34.3 / 34.5, 34.4 / 34.6, 49.3 / 49.4: okur hangi alt adımda olduğunu 3B kareden
   anlayamıyor. Kareye, sahneyi küçültmeyen bir ayırt edici ekle (ör. sahnenin üstüne bindirilmiş küçük taraf / konum etiketi,
   küçük görünümde belirgin vurgu, kamera farkı; yol sende). Dikkat: önceki denemede kare başlığı sahneyi ≈ %10 küçültüp F10d
   görünürlüğünü bozmuştu; çözümün sahne boyutunu değiştirmesin. Etkileşimli sayfada ve basılı karede ayrı ayrı sına.
5. **Kayıt düzeltmeleri (günlük ve varsa sayfa metni):**
   - "1188 bağlantı elemanı" → veride 893 benzersiz bağlantı elemanı; 1188 konum başına işaret toplamı (bulgu 6 / tablo satırı 4).
   - "Tek kaynak CAD": kablo yolu 12 parçası (p1180–p1191) sahnede rehberin kablo paletiyle çiziliyor (paket öncesinden; p1187 CAD
     kırmızı ↔ rehber mavi). **Orkestratör kararı:** bu pakette değiştirme; günlüğe istisna olarak yaz ve "P10.7'ye devredildi
     (kablo içeriği)" diye not düş.
   - 9a "etek ön bandı için iki parçalı yol yok": denenen yönleri sayarak yaz ("denenen N ötelemede bulunmadı; dönme denenmedi").
   - Adım 41 "+x'ten kaydırarak takılmaz" uyarısı: ya metnin söylediği kol duruşunda ölç, ya metni ölçülenle sınırla
     (hangisi daha az iş ve daha doğruysa; seçimini yaz).
   - Anlaşılırlık sayımı, görünürlük tablosu ve "geçti" yazan yerler yeni ölçümle güncellensin.
   Günlükte eski iddiayı silme: yeni bir "§ Düzeltme turu 1" bölümü aç, hangi iddianın neyle değiştiğini yaz, eski satırın yanına
   "düzeltildi, bkz. §…" notu koy.

## Sonra
- Rehberi yeniden üret (`rehber_uret.py --veri-yok` yeterliyse o; veri değişiyorsa gerekeni koş ve nedenini yaz), ardından zincir:
  `F10d-dogrula.py --goruntu-yok`, `F10a-dogrula.py --kanit-yok`, `F9b-dogrula.py`, `carpisma_kos.py kontrol`,
  `regresyon.py --yazma`, `F10e-dogrula.py` (tam). Hepsi çıkış 0 olmalı; çıkış kodlarını yakala.
- Değişen karelere (en az: 31.3, 34.3–34.7, 35.1–35.3, 36.1, 49.3, 49.4; açık ve koyu) kendin bak; önce / sonra
  `planlama/d158/F10e-goruntu-d1-*.png`.
- B'nin "ölçülmedi" dediği PDF en küçük yazı ve sayfa sayısını önce / sonra yaz.

## Kabul
- Kabuk alt adımlarında okurun pikseli iki temada ölçülü; eşik altı yeni parça 0 ya da gerekçeli istisna listesi (ısıl gömmeler
  ayrı sayılır, önceki kuralla). 31.3 `p0762` ekran görüntüsü farkıyla görünür.
- Benzer üç çift kareden ayırt ediliyor (yazısız 3B kareye bakan biri hangisi olduğunu söyleyebilmeli); sahne boyutu değişmedi.
- Günlükteki dört iddia düzeltildi; sayılar yeni ölçümle aynı.
- 50 / 50 + alt 50 / 50, konsol 0, 1192 ↔ 1192, yazdırma kareleri boş 0, zincir çıkış 0, regresyon 10 / 10; model geometrisi ve
  kablolama içeriği değişmedi.

## Çalışma
- Bellek dar (≈ 3 GB boş): her ağır komuttan önce ölç (≥ 2 GB), aynı anda tek ağır süreç, **hiçbir komutu arka plana atma**,
  uzun işi parçala ve ara sonucu diske yaz. Tam üretim ≈ 35–50 dk sürer; araç komutu kendiliğinden arka plana alırsa ön planda
  yoklayarak bitmesini bekle, başka ağır iş başlatma.
- Geçici dosyaların: bu oturumun scratchpad'inde `f10e-d1/` klasörü (orkestratör yolunu prompt'ta verir).
- `F10e-kontrol.md`'ye yazma (B'nin dosyası). Günlüğü erken aç, bölüm bölüm doldur.
- Dönüş: yalnız iş bitince ya da gerçekten ilerleyemeyince; arkada süreç bırakma. Dönüş mesajı kısa: her madde için ne yapıldı,
  ölçüm sayıları, zincir çıkış kodları, yapamadıkların, dokunduğun dosyalar.
