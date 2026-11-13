# F10f düzeltme turu 2 (P10.5), 12.11.2026

İkinci bağımsız bakış (B2) hükmü: **DÜZELTME GEREKLİ**. Rapor: `planlama/d158/F10f-kontrol-2.md` (önce tamamını oku). İlk kontrolün
iki yüksek bulgusu (birim, geniş istisna), metin çelişkisi ve ayna farkı kapandı; onlara dokunma. Bu, döngünün izin verdiği **son**
düzeltme turu: kapsamı aşağıdakiyle sınırlı tut, yeni iş açma. `F10f-brief.md` Kurallar bölümü ve `F10f-duzeltme-1-brief.md`
"Çalışma" bölümü aynen geçerli. B2'nin ölçüm betikleri scratchpad `f10f-b2/` klasöründe (salt oku: `geo_ucus`, `diag571`,
`geo_karar`, `b2_parca`, `b2_kare`, `b2_fark`, `b2_reg`, `metin_dok`, `ucus2`).

## Düzeltilecekler

1. **625ZZ uçuşu yuvadan geçiyor, 44.1 (orta-yüksek; B2 3.1).** p0571 ↔ p0583 ve p0628 ↔ p0640: rulman −x / +x uçarken dirsek
   çatalının yuva omzundan 1,55 mm derinlikte geçiyor (t 0,5–10 mm). Rehberin denetimi görmüyor: duruşta örtüşen çift (burada
   0,06 mm sıkı geçme) yolun tamamında dışarıda bırakılıyor.
   a. **Uçuş:** rulmanı çatalla birlikte uçur (B2 ölçümü: p0562 + p0571 + p0583, +y, d 63,5, horn merkez vidası dışında temiz;
      sol kol aynası). Bu, aynı alt adım (44.1) içinde gösterim grubudur; parça ↔ adım ataması değişmez. Adım metni rulmanın
      çatala önceden takıldığını söylesin (kaynakta böyle mi, `dirsek_montaj.py` / tasarım notundan doğrula; kaynak başka sıra
      diyorsa uydurma, karar notuna yaz). K1-b karar notuna bu ölçümü ekle.
   b. **Denetimdeki kör nokta:** duruşta örtüşen çifti tümden dışarıda bırakma; çift başına eşik = duruş derinliği + pay (payı
      yaz). Düzeltilmiş denetimi **bütün rehberde** koş. Kol adımlarında (36, 39–48) çıkan her yeni satır düzelsin ya da dar
      anahtarlı, sınıfı yazılı istisnaya girsin. Kol dışı adımlarda çıkan yeni satırları **düzeltme** (kapsam dışı): tam listesini
      (alt adım, parça, engel, derinlik) günlüğe ve `kontrol.json`'a yaz; dar anahtarlı istisna, sınıfı "ölçüm kaydı: F10f
      düzeltme 2'de ilk kez ölçüldü, ayrı iş". Hiçbir satır sessizce atlanmasın; önce / sonra sayıları yaz.
   c. Sınama: 625ZZ'nin eski yönünü scratchpad kopyasında geri koy, düzeltilmiş denetimin yakaladığını göster; `F10f-dogrula.py`
      sınamasına kalıcı ekle.

2. **42.1 ve adım 42 patlatma görünümünde iki ön kol da gizli (orta; B2 3.2).** Sol ön kol ayna düzeltmesiyle "yerinde" (d 0)
   oldu; patlatma d 0 parçaları çizmiyor, servolar ve somunlar referanssız havada. Patlatmada d 0 olan yeni parçalar yerinde
   çizilsin (ayna düzeltmesi bozulmadan). Bu kural başka adımları da etkiler: değişen konumları say (HEAD rehberi ve tur 1
   kareleriyle ekran farkı), en az 8'ine bak, bozulan varsa yaz. `tak()` değişikliğinin adım 0'daki 47 / 58 px farkının nedenini
   bul (B2 3.7); adım 0 sıra canlandırmasına bak.

3. **Kare okunurluğu: zor 5 / 14, hedef ≤ 4 (orta; B2 3.3 ve §5).**
   - 41.4 / 41.5: tambur ve kaset duvarına kenar çizgisi (41.2 / 41.3'teki gibi); −45 ucunu örten p0118 mafsal cıvatası bu iki
     karede saydam.
   - 48.2 / 48.3: iki ek arasındaki bilek uzatma parçası uzatma renginde; JR ve lehim noktasına bağ işareti; ekler seri değil
     iki ayrı nokta okunsun.
   - 41.3 açık tema: kenar çizgisi koyulaşsın.
   Şema görünürlüğü (ekran farkı) korunur; sınıflamayı B2'nin ölçeğiyle (iki temanın kötüsü) kendin yap ve günlükteki "zor 3"
   iddiasının yanına düzeltme notu düş.

4. **Küçükler (düşük; B2 3.4–3.6, §4).**
   - 40.2 / 41.2: S2 uzatma ucunun yeri ("kol ucu tüp penceresinde" S2 için yanlış; S2 uzatması G2'de göbekte ekleniyor).
   - F4 madde 2: iç terim "F10f sıra denetimi … el zarfı" okur diline.
   - İstisna anahtarı: eski tür dize anahtar hata versin ya da `istisna_bos` sayımına girsin (M8).
   - Metin denetimi: G4'te değeri etiketiyle eşle (iç ↔ dış takası yakalansın, T4); bir sayının metindeki her geçişi birimiyle
     denetlensin (T9); "L 171,4 mm (−5…0)" toleransına birim.
   - PDF: kare içi lejant basılı ölçekte ≈ 2,5 pt, okunmuyor. Yazdırma karelerinde kol kablo lejantını okunur yap (karenin
     dışına metin olarak ya da basılı ölçekte ≥ 8 pt); PDF sayfa sayısı ve en küçük yazıyı önce / sonra yaz.

## Bu turda yapılmayacaklar (kayıtta açık iş olarak kalır)
Devir a (kol konumlarında eşik altı parçalar: B2 hükmü "ayrı iş"), S2 0° lopunun şekli (not ve renk seçildi), 36.5 iç ucunun 0 px
olması, demet kalınlığı (ilk kontrol bulgu 6), kol dışı adımlarda madde 1b ile çıkacak yeni satırların düzeltilmesi, iki karar
kalemi (K1-a, K1-b: sıra değişmez).

## Sonra
- Uçuş verisi değiştiği için FreeCAD'li veri koşusu (kilit + bellek kuralı), tam üretim, zincir: `F10f-dogrula.py`,
  `F10e-dogrula.py --goruntu-yok`, `F10d-dogrula.py --goruntu-yok`, `F10a-dogrula.py --kanit-yok`, `F9b-dogrula.py`,
  `carpisma_kos.py kontrol`, `regresyon.py --yazma`. Hepsi çıkış 0.
- Değişen karelere iki temada kendin bak (41.3–41.5, 48.2 / 48.3, 42 ve 42.1 patlatma, 44.1, madde 2'nin etkilediği konumlardan
  en az 8); önce / sonra `planlama/d158/F10f-goruntu-d2-*.png`.
- Günlükte yeni "§ Düzeltme turu 2" bölümü; eski iddiayı silme, yanına not düş.

## Kabul
- 44.1'de 625ZZ uçuşu çatalla birlikte; düzeltilmiş denetim (duruş derinliği + pay) bütün rehberde koşuyor, kol adımlarında
  istisna dışı çarpışan 0, kol dışı yeni satırlar listeli; sınama eski yönü yakalıyor.
- 42 / 42.1 patlatmada ön kollar görünüyor; etkilenen öbür konumlar sayılı, bozulan 0 ya da yazılı.
- Kablo kareleri: anlaşılmıyor 0, zor ≤ 4 / 14 (iki temanın kötüsü); görünürlük korunur.
- Küçükler kapandı ya da nedeniyle "yapılmadı".
- 50 / 50, konsol 0, 1192 ↔ 1192, alt adım 71, denetim 0, ulaşılamaz 0, girilemez 0, yazdırma kareleri boş 0, zincir çıkış 0,
  regresyon 10 / 10; GLB karması aynı; parça ↔ adım ataması HEAD ile aynı; pin / konnektör içeriği yok.

## Çalışma
- Bellek çok dar (22:43'te boş 1,97 GB; tur 1 zincirinde en düşük 1,00 GB). Her ağır komuttan önce ölç; 2 GB altındaysa
  birkaç dakika arayla en çok 3 kez daha ölç, yine düşükse **başlatma**, nerede kaldığını yazıp dön. Aynı anda tek ağır süreç;
  uzun komutlar sarmalayıcı + ön planda yoklama + bellek bekçisi.
- Geçici dosyaların: scratchpad `f10f-d2/` (yoksa oluştur).
- `F10f-kontrol.md` ve `F10f-kontrol-2.md`'ye yazma. Depo kökündeki boş `rehber_metin.py`'ye, `karar-kuyrugu.md`, `dongu-158.md`,
  `README.md`'ye dokunma. Commit, push, silme, checkout, reset, stash yok.
- "DUR" mesajı gelirse en yakın güvenli noktada bırak (önceki gibi).
- Dönüş: yalnız iş bitince ya da gerçekten ilerleyemeyince; arkada süreç bırakma. Dönüş mesajı kısa: madde madde ne yapıldı,
  ölçüm sayıları (özellikle 1b: kol adımları / kol dışı yeni satır sayısı), zincir çıkış kodları, yapamadıkların, dokunduğun
  dosyalar.
