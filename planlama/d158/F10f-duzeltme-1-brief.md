# F10f düzeltme turu 1 (P10.5), 12.11.2026

Bağımsız kontrol (B) hükmü: **DÜZELTME GEREKLİ**. Rapor: `planlama/d158/F10f-kontrol.md` (önce tamamını oku; ölçüm yöntemleri,
F10f-K1 sınıflama tablosu ve kare sınıflaması orada). Yolun geometrisi, katı içinden geçme, görünürlük pikseli ve kol dışı regresyon
doğrulandı; onlara dokunma. Düzeltilecekler aşağıda. `F10f-brief.md` **Kurallar bölümü bu turda da aynen geçerli** (yazılabilir
alanlar, dokunulmazlar, bellek / FreeCAD, uzun komut yöntemi, yapma listesi, yazım kuralları). B'nin ölçüm betikleri scratchpad
`f10f-b/` klasöründe (salt oku; 26 yönlü uçuş testi, ekran farkı, HEAD karşılaştırması).

## Düzeltilecekler

1. **Birim hatası (yüksek).** G4 metni (41.4 / 41.5) iç ve dış koşuyu "125,3 mm / 10,2 mm" ve "10,1 mm / 74,9 mm" yazıyor; kaynakta
   `s1_poz` `a_i` / `a_o` derece (`rehber_kol_kablo.py` `metin_sayilar`, "%s mm"). Metni kaynağın birimiyle düzelt (derece; okura
   ne açısı olduğu açık olsun). `metin_sayilar` denetimi birimi de sınasın: sayı doğru ama birim yanlışsa hata versin; öbür 24
   sayının birimini de bu gözle bir kez elden geçir. Sınama: birimi bilerek boz, yakalandığını göster.

2. **F10f-K1 (yüksek).** Orkestratör kararı: istisna bu hâliyle kalmaz.
   a. **İstisna anahtarını daralt:** parça + alt adım + çarpan parça + en çok derinlik (ölçülen değer + küçük pay; payı yaz). Bugün
      temiz olan 8 satır (S2 horn merkez vidası × 2, kaset cıvatası ψ 226 × 2, bilezik pulu baş × 4) muaf kalmasın. Aynı daraltma
      `gizli_ok` için de (parça kimliği + alt adım).
   b. **Rehberde düzelen 11 tür** (B tablosu 3.2 c): yönü / işareti / birlikte uçurmayı düzelt ve istisnadan çıkar: S2 horn (+z),
      üst kol tüpü (−y), S1 kaset gövdesi (ön radyal, +z; metin doğru, uçuş yanlış), dirsek servosu (−z), bilek servosu çıkış mili
      (servoyla birlikte), dirsek servo kontra somunu, 625ZZ iç bilezik (44.1), çatal-horn pulu (cıvatasıyla birlikte), bilezik pulu
      (somun tarafı; işaret ters), bilezik kontra somunu. B'nin önerdiği yön başlangıç noktasıdır; rehberin kendi sıra denetimiyle
      (uçuş yolu, perdelenme, el erişimi) yeniden ölç, daha iyisi varsa onu seç ve yaz. Sağ / sol ayna tutarlı olsun (B bulgu 10:
      sağ dirsek / bilek kulak cıvatası `d` 65, sol 100,7: nedenini bul, ayna tutsun).
   c. **Duruşa bağlı 2 tür** (kaset cıvatası ψ 200; kaset kapağı): tasarım bunları başka kol duruşunda takıyor (`S1-kaset.md` K5:
      cıvata S1 −45 / S2 90'da; kapak S2 ≥ 30 ve iki parçalı yol). Rehber kolu modeldeki duruşta çiziyor. Adım metni okura hangi
      duruşta takılacağını tasarımdaki değerle söylesin; istisna dar anahtarla ve gerçek gerekçeyle kalsın ("rehber kolu modeldeki
      duruşta çizer; tasarım bu parçayı … duruşunda takar"), "karar bekliyor" değil. Duruşu çizmek ucuzsa (uç duruş şemasındaki gibi)
      dene; değilse bırak ve yaz.
   d. **Tasarım / montaj sırası sorusu 2 kalem** (kol çatalı + 625ZZ dış bilezik, 40.1; dirsek çatalı ↔ horn merkez vidası, 44.1):
      **sırayı ya da parça ↔ adım atamasını değiştirme.** Dar anahtarlı istisna "karar bekliyor (karar kuyruğu)" etiketiyle kalsın.
      Günlüğe her biri için karar notu yaz: ölçüm, seçenekler (ör. B'nin ölçtüğü: iç bilezik + pul + mafsal cıvatası çataldan sonra
      takılırsa +x / −y açılıyor; horn merkez vidası çataldan sonra takılırsa ±z / +y açılıyor), her seçeneğin rehberde ve tasarım
      belgelerinde neyi değiştireceği, önerin. Seçenekleri B'nin 26 yönlü testiyle değil rehberin kendi denetimiyle de ölç (veriyi
      scratchpad kopyasında değiştirerek; depo verisinde sıra değişmez). Kuyruğa yazımı kayıt aşaması yapar; `karar-kuyrugu.md`'ye
      dokunma. Adım metni bu iki yerde okura yanlış bir şey söylemesin (olmayan bir takma yönünü tarif ediyorsa nötr yaz).
   e. Sonuç tablosu: 46 satır ve 9 gizli parçanın her biri için önce → sonra (düzeldi / dar istisna: gerekçe / dar istisna: karar).
      9 gizli parçanın 42 / 44 / 48 karelerinde okurca görülüp görülmediğini ölç (okurun pikseli, iki tema); görünmeyeni yaz.

3. **41.4 / 41.5 karşılaştırılamıyor (orta).** İki uç duruş karesi aynı kamera, aynı çerçeve yerleşimi ve aynı renkle çizilsin;
   okur iki kareyi art arda açınca U-lop'un nasıl kaydığını görsün (ör. öbür duruşun soluk izi, tambur üstünde açı işareti; yol
   sende). 41.2 / 41.3'te tambur ve kaset duvarı okunur olsun (B: "zor").

4. **Metin tutarlılığı (orta).** 40.2 "uzatmaları tüp penceresinden çıkar" ↔ 48.2 "G3'te pencereden içeri girdi" çelişiyor;
   uzatma ucunun 40 ile 48 arasında nerede beklediği hiçbir metinde yok; 41.2 "F4'te dışarı alınan uçlar buraya bağlanır"
   yanıltıcı (kaynakta tek, kesintisiz 1856 mm uzatma); JR'nin pencere dışında takılıp sonra itileceği yalnız kod yorumunda.
   Kaynaktan (`S1-kaset.md`, `KOL_KABLO` açıklamaları, `dirsek_montaj.py` 8b) gerçek döşeme sırasını çıkar; 36.4 / 36.5, 40.2 / 40.3,
   41.2 / 41.3, 42.2 / 42.3, 44.2 / 44.3, 48.2 / 48.3 metinleri tek bir sırayı anlatsın: her kablo alt adımında kablonun iki ucunun
   o anda nerede olduğu yazsın. Bir bölüm, gerçekte döşendiği adımdan başka bir alt adıma bağlıysa bağı düzelt (ana adım sayısı ve
   kimlikleri değişmez). Kaynak sırayı tanımlamıyorsa uydurma: "tasarımda tanımlı değil" diye günlüğe ve karar notuna yaz, metinde
   yalnız tanımlı olanı söyle.

5. **S2 0° lopu (orta).** 40.2 / 40.3'te lop karede kıvrık kuyruk gibi (r_min 6,3 mm; sınır 11,2 mm; S2 0° kol aralığının dışında).
   Okur kabloyu bu kadar sıkı bükmesi gerektiğini sanmasın: karede görünen bir not / işaret ya da analiz edilmiş duruşun (S2 5°)
   çizimi; hangisi dürüst ve ucuzsa. Uçlar yine beklenen parçada bitsin; seçimini ve ölçümünü yaz.

6. **Kare okunurluğu.** B'nin sınıflaması: 14 benzersiz karenin 4'ü açık, 10'u zor, 41.4 ↔ 41.5 karşılaştırması anlaşılmıyor.
   Nedenler tabloda (B §4): 36.4 / 36.5 yeşil yol ↔ camgöbeği K2 çizgileri (rengi ayır, renk farkını ölç); 40.2 / 40.3 üç bölüm tek
   renk, kablo bağı ve tambur bağı karede işaretli değil; 48.2 / 48.3 iki ek işareti tek çizgi üstünde (tek kabloda seri iki ek gibi
   okunuyor: hangi ek hangi kabloya ait, ayırt edilsin), tüp soluk. Lejantta kol kabloları kendi renkleriyle görünsün ("Kablo yolu"
   kırmızı kare ↔ çizilen turuncu / yeşil). Okur metninde "voksel" iç terimi kalmasın. Hedef: anlaşılmıyor 0, zor ≤ 4 / 14;
   tutmayan kareyi nedeniyle "zor" yaz.

7. **Kayıt.** Günlükte eski iddiayı silme: yeni "§ Düzeltme turu 1" bölümü aç, hangi iddianın neyle değiştiğini yaz, eski satırın
   yanına "düzeltildi, bkz. §…" notu koy (özellikle: "metin sayıları eksik 0", "F10f-K1 hepsi F10f öncesinden" → doğru ama istisna
   genişti, kabul satırı "uçuş yolu çarpışan 0 (istisna 58)").

## Sonra
- Rehberi yeniden üret (uçuş yönü veride değişiyorsa FreeCAD'li veri koşusu gerekir: kilit ve bellek kuralıyla; gerekmiyorsa
  `--veri-yok`; hangisini neden koştuğunu yaz), ardından zincir: `F10f-dogrula.py`, `F10e-dogrula.py --goruntu-yok`,
  `F10d-dogrula.py --goruntu-yok`, `F10a-dogrula.py --kanit-yok`, `F9b-dogrula.py`, `carpisma_kos.py kontrol`,
  `regresyon.py --yazma`. Hepsi çıkış 0; çıkış kodlarını yakala.
- Değişen bütün kablo karelerine (14 benzersiz kare × 2 tema) ve uçuşu değişen parça alt adımlarının (40.1, 41.1, 41.6, 42.1,
  44.1, 48.4) karelerine kendin bak; önce / sonra `planlama/d158/F10f-goruntu-d1-*.png`.
- PDF sayfa sayısı ve en küçük yazı önce / sonra.

## Kabul
- G4 açıları doğru birimde; birim denetimi kalıcı ve sınanmış.
- Uçuş istisnası: 11 tür istisnasız 0 çarpışma; kalan istisnaların hepsi dar anahtarlı ve iki sınıftan biri (gerekçeli: duruş /
  karar bekliyor: 2 kalem); önceden muaf tutulan temiz satır 0. Model geometrisi değişmedi (GLB karması aynı); parça ↔ adım ataması
  değişmedi.
- 41.4 / 41.5 aynı kamera / yerleşim / renk; kablo metinleri birbiriyle çelişmiyor, her kablo alt adımında iki ucun yeri yazılı.
- Kablo kareleri: anlaşılmıyor 0, zor ≤ 4 / 14 (kendi gözünle, dürüst sayım); görünürlük 56 / 56 korunur.
- 50 / 50, konsol 0, 1192 ↔ 1192, alt adım sayısı değişmedi (71; değişirse nedenini yaz), denetim 0, ulaşılamaz 0, girilemez 0,
  yazdırma kareleri boş 0, zincir çıkış 0, regresyon 10 / 10; pin / konnektör içeriği yok.

## Çalışma
- Bellek dar (boş ≈ 2,9 GB): her ağır komuttan önce ölç (≥ 2 GB), aynı anda tek ağır süreç, uzun komutlar sarmalayıcı + ön planda
  yoklama + bellek bekçisi (izlenen arka plan görevi yok), ara sonucu diske yaz.
- Geçici dosyaların: scratchpad `f10f-d1/` (yoksa oluştur); `f10f-a/` araçlarını kopyalayıp kullanabilirsin.
- `F10f-kontrol.md`'ye yazma (B'nin dosyası). Depo kökündeki boş `rehber_metin.py`'ye dokunma (Ahmet'e soruldu).
- Dönüş: yalnız iş bitince ya da gerçekten ilerleyemeyince; arkada süreç bırakma. Dönüş mesajı kısa: her madde için ne yapıldı,
  ölçüm sayıları, F10f-K1 sonuç tablosu özeti, iki karar notunun özeti, zincir çıkış kodları, yapamadıkların, dokunduğun dosyalar.
