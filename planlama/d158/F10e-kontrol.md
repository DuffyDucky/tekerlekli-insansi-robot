# F10e bağımsız kontrol (B)

Kontrol: 12.11.2026, dal `lale-duzeltme`, HEAD `90c270a`, paket çalışma ağacında (commit edilmedi). Brief: scratchpad'deki
`F10e-B-brief.md`. Bu kontrol, yarıda kalan önceki kontrol ajanının (B1, 00:31–01:10) ham ölçümlerini devralıp tamamlıyor. Her
sayının kaynağı yanında yazılı:
- **[B1]**: B1'in betiği ve ham çıktısı (scratchpad `f10e-b/`). Betiği okundu, ne ölçtüğü ve eşiği aşağıda yazılı. Rehber dosyaları o
  koşudan beri değişmedi: `rehber/` son yazım 11.11 23:36, `planlama/rehber/` son yazım 11.11 23:56; B1 koşuları 00:34–01:05.
- **[B2]**: bu kontrolde yeniden ölçüldü, yeniden hesaplandı ya da gözle bakıldı.
- **[A]**: uygulama ajanının iddiası (`F10e-gunluk.md`, `F10e-dogrula.json`). Burada yalnız karşılaştırma için geçiyor.

## 1. Hüküm

**DÜZELTME GEREKLİ.** Asıl düzeltilmesi gereken kayıt: rehberin kendisinde engelleyici bir bozulma yok, kabul eşikleri (zor ≤ 2,
anlaşılmıyor 0, renk 1192 / 1192, F10d görünürlüğü) tutuyor. Ama günlükteki dört iddia ölçümle çürüdü ya da eksik çıktı; bunlar
düzeltilmeden günlük kayda girmemeli.

En önemli bulgular:
1. **Okurun pikseli koyu temada ölçülmemiş.** A'nın görünürlük ölçümü yalnız açık temada koşuyor (`F10e-dogrula.py` satır 405).
   Koyu temada kabuk alt adımlarındaki 20 yeni parça eşiğin altında kalıyor; bunların 6'sı 0–3 px, yani okur için görünmüyor
   (bindirme cıvataları 34.3 p0244, 34.4 p0242, 34.5 p0256, 34.6 p0254, 35.1 p0280, 35.2 p0282). Ölçüm [B1]; sayfanın gerçek ekran
   görüntüsüyle ayrıca doğrulandı [B1 çekti, B2 yeniden hesapladı]. Halkalar yerlerini gösteriyor; parçanın kendisi görünmüyor.
2. **31.3 `p0762` görünmüyor.** A'nın kaydı "40 / 142 px, geçti" diyor. Gerçek ekran görüntüsünde parçayı gizlemek eşiği
   (Σ|ΔRGB| > 24) aşan 0 piksel değiştiriyor; eşiğin altında değişen 164 piksel var [B1 çekti, B2 yeniden hesapladı]. Brief'in
   F10d'den devrettiği "soluk iki parça" sorunu bu parçada çözülmemiş.
3. **34.7 hâlâ "zor".** Hoparlör grubu karede ≈ 80 × 80 px. Ön halka, ped, kap ve kelepçe 0,4 opaklıkla üst üste çiziliyor, katman
   sırası ayırt edilmiyor (F10d'nin zor gerekçesi aynen duruyor). Günlükteki "hoparlör kara" ifadesi de karede görülmüyor: kara
   hoparlör beyaz saydam kabın içinde, gri görünüyor [B2 gözle, `zoom-34.7`].
   Benim sayımım: açık 40, zor 2 (31.9, 34.7), anlaşılmıyor 0. Eşik (zor ≤ 2) yine tutuyor ama A'nın "açık 41, zor 1" iddiası tutmuyor.
4. **Benzer kare çiftleri 3B karede ayrılmıyor.** 34.3 / 34.5 ve 34.4 / 34.6 kareleri piksel düzeyinde neredeyse aynı (yalnız küçük
   görünümdeki kehribar ≈ 9 px kayıyor). 49.3 / 49.4'te kamera farklı ama iki kare de "pembe çerçevede gri dikdörtgen kapak, 7 halka"
   görünümünde. Okur hangi alt adımda olduğunu ancak yazıdan anlıyor: etkileşimli sayfada panel başlığı, basılı karede kare başlığı.
   Brief'in "kareden anlayabilmeli" ölçütü yalnız yazıyla karşılanıyor [B2 gözle].
5. **"Tek kaynak CAD" 12 parçada tutmuyor.** Kablo yolu parçaları (p1180–p1191) sahnede verinin `renk` alanıyla, yani rehberin kendi
   kablo paletiyle çiziliyor (`app.js` 279 / 422, HEAD'den kalma). `gr` (CAD rengi) bunlar için kullanılmıyor. Ton farkı çoğunda küçük,
   ama p1187 (kafa 12 V) CAD'de kırmızı `#f20d0d`, rehberde mavi `#2f86d4` [B2].

## 2. Kabul ölçütleri

| ölçüt (brief) | iddia [A] | bu kontrolün ölçümü | sonuç |
| --- | --- | --- | --- |
| 1. Renk veri ↔ CAD | 1192 / 1192 | Bağımsız okuma (FCStd Document.xml `Renk` × modül `_gorsel.py` RENK tablosu, ast ile) [B1]: 1191 / 1191 aynı, fark 0. Eşleşmeyen tek parça p0781 (ad eşlemesi "10,1\"" ↔ "10,1in"); elle bakıldı: CAD `K105` Renk `siyah` → kafa RENK `#212124` = veri `#212124` [B2]. Toplam **1192 / 1192**. GuiDocument kayıtlı renk 1031 / 1031 aynı [B1]. | doğrulandı |
| 1. Rehberde ayrı renk tablosu yok | yok | Gerçek renk için yok. Kablo yolu 12 parçası sahnede `p.renk` (rehber kablo paleti) ile çiziliyor; p1187 CAD kırmızı ↔ rehber mavi [B2] | **kısmen çürütüldü** (bulgu 5) |
| 2. Yeni parçalar gerçek renkte, öncekiler gri | yanlış 0 | 66 konum × 2 tema (42 kabuk alt adımı + 24 başka konum): renk yanlış 0, önceki gri yanlış 0 [B1] | doğrulandı |
| 2. Sınıf kipi düğme / `C` / `?renk=` | çalışıyor | Düğme 12 / 12 sınıf rengine geçiyor, `C` geri alıyor, `I` halkaları 11 → 0 → 11, `?renk=sinif&isaret=0` geçiyor [B1 `ui.json`] | doğrulandı |
| 2. Seçim yeşili / kehribar gerçek renkle karışmıyor | ΔE 78,5 / 21,9 | Karede seçili taşıyıcı yeşil, halkalar yeşil, karışma görülmedi [B2 gözle `ui-secim-35.3`, `ui-satir-34.3-b5`]. ΔE sayıları ölçülmedi (A'nın) | doğrulandı (gözle) |
| 2. Kenar çizgisi karede gerçekten çiziliyor | kenarsız 0 | Kenar çizgileri açıkken ve kapalıyken çekilmiş kare çiftleri, Σ|ΔRGB| > 24 değişen piksel: 31.7 koyu 10285, 33.1 açık 11761 / koyu 9203, 35.3 açık 14187 / koyu 15481; 31.7 açık 0 (kara QLED açık zeminde kenar istemiyor) [B1 çekti, B2 hesapladı]. 132 karede kenar gereken (WCAG < 3,0) yeni parça 984, kenarsız 0 [B1] | doğrulandı |
| 3. Bağlandığı yer, 42 kabuk alt adımının hepsinde | 41 / 41 yeni parçalı | 41 / 41 (49.2'de yeni parça yok); sahnedeki pembe parça = veri `ev` 132 / 132 karede [B1] | doğrulandı |
| 3. Vurgulanan parça gerçekten bağlandığı parça mı (≥ 20 alt adım) | 186 / 186 | 41 alt adımda 74 (konum, ev) çifti, nokta–üçgen uzaklığı, `robot.glb`, eşik 0,5 mm: doğrudan temas (bağlantı elemanı köşelerinin ≥ %10'u) 49; önceki bağlantı elemanı (perçin somun / ısıl gömme) üzerinden 14; yalnız ana parça teması 3; ev bu alt adımda yeni (masa tabanı) 7; temassız 1 [B1]. Temassız olan 35.3 p0005 (direk): çekiç somunlar p0434 / p0437 direğe 0,0 mm (köşelerin %6,7'si 0,5 mm içinde, B1 eşiğinin altında) [B2]. Vurgulanmayan aday ana parça 0 [B1] | doğrulandı (kabukta 67 / 67 ölçülen; 7 masa tabanı ölçülmedi) |
| 4. İşaret sayısı = bağlantı elemanı sayısı | 1188 = 1188; kabuk 277 / 277 | Veride 893 benzersiz bağlantı elemanı. 1188, konum başına toplam (adım genel bakışı + alt adım; alt adımlı 10 adımın 295 elemanı iki kez sayılıyor) [B2]. Kabuk 277 [B2]; 42 alt adımda 265 halka, ×n toplamı 277 [B1] | sayı doğrulandı; **"1188 bağlantı elemanı" ifadesi yanıltıcı** |
| 4. Kümeleme açık | ×n | Karelerde "×2 / ×3 / ×6" etiketleri ve lejantta "(×n: küme)" var [B2 gözle] | doğrulandı |
| 4. İşaret karede ve doğru yerde (≥ 10 alt adım) | kare dışı 0 | 66 konum × 2 tema, kendi izdüşümüm (yeni bağlantı elemanının köşe noktalarından ekran kutusu): yeni = karede = halka ×n toplamı = 1292; elemandan en yakın halkaya > 22 px olan 0; halkadan en yakın eleman kutusuna en çok 2 px [B1]. Patlatılmış 35.3'te 6 halkanın 6'sı uçan elemanın kutusunun içinde [B1 `ui.json`] | doğrulandı (66 / 100 konum) |
| 4. Panel satırı → halkalar vurgulanıyor | çalışıyor | 4 alt adımda 7 satır: satırın elemanı = yeşil halka, yanlış 0, eksik 0 [B1]; karede yeşil [B2 gözle] | doğrulandı |
| 5. Kabuk anlaşılmıyor 0, zor ≤ 2 | açık 41, zor 1 | açık 40, zor 2 (31.9, 34.7), anlaşılmıyor 0 [B2 gözle, 84 kare] | eşik tutuyor; **iddia çürütüldü** (34.7) |
| 5. Benzer çiftler kareden ayırt ediliyor | ayırt ediliyor | Yalnız panel başlığından ve basılı karedeki kare başlığından; 3B kare 34.3 / 34.5 ve 34.4 / 34.6'da neredeyse aynı [B2 gözle] | **kısmen** (bulgu 4) |
| 5. ≥ 15 kabuk dışı adım | 14 açık, 21 zor | 21 konuma baktım (0, 2, 5, 8, 12, 15, 17, 19, 21.1, 21.2, 25, 28, 30, 32, 38, 41, 43.1, 44, 45.2, 46.1, 48) ve ayrıca 31 / 33 / 34 genel bakışa. Renk ya da işaret hiçbirini bozmamış; 21.1 / 21.2'de horn kenarlı ve halkalı, bence açık [B2 gözle] | doğrulandı |
| 6. Okurun pikseli, kabuk alt adımları (≥ 30 px ve ≥ 0,20 × yalnız) | eşik altı 2 (35.3 p0432, 36.1 p0288) + ısıl gömme 4 | B1'in renderer'ı sayfanın sahnesi ve kamerasıyla, gerçek malzemeyle, parçayı tek tek gizleyerek ölçtü. 11 parçada sayfanın ekran görüntüsüyle birebir aynı sonucu verdi. "simdi" (alt adımın yeni parçası, ısıl gömme hariç): **açık temada 212'nin 1'i** eşik altında (35.3 p0434 çekiç somun 111 / 2143, oran 0,052, kanalın içinde), **koyu temada 212'nin 20'si** (6'sı 0–3 px). A'nın iki parçası B1'de eşiği geçiyor: 35.3 p0432 167 / 798 (0,209), 36.1 p0288 35 / 173 (0,202); ikisi de sınırda. Isıl gömme: açık 24 / 162, koyu 26 / 162 eşik altında; 34.7 p0439 1 px (A ile aynı) [B1, özeti B2 çıkardı] | **çürütüldü** (eksik: koyu tema ölçülmemiş) |
| 6. 31.3 p0762 ve 34.7 p0440 (F10d'de soluk) | 40 / 142 ve 137 / 314, ikisi geçti | p0762: ekran görüntüsünde > 24 değişen 0 px, B1 renderer'ında 0 / 165. p0440: 141 / 350 (0,403), geçiyor [B1; ekran farkı B2 yeniden hesapladı] | p0762 **çürütüldü**, p0440 doğrulandı |
| 7. Kare başlığı yalnız yazdırmada | etkileşimlide yok | Etkileşimli 132 karede `#kare-baslik` görünür 0 [B1]. `?sahne=1` 100 konumun 99'unda başlık var; adım 0'da yok [B1 `baslik.json`]. Basılı karede başlık okunuyor ("34.3 Uzatma bandı 1 sağ + y 530 braketi · bakış: sağ-önden") [B2 gözle `baski-c1`, `baski-c3`] | doğrulandı |
| 7. Kaldırma başka şeyi bozmuş mu | F10d geçti | Bozulma görülmedi (132 kare, konsol 0) [B1]. F10d görünürlük koşusu bu kontrolde koşulmadı | doğrulandı (gözle); F10d ölçülmedi |
| 8. 50 / 50, 50 alt adım, konsol 0, ağ 0 | geçti | 100 konum açıldı, hazır 100, konum doğru 100, konsol 0, ağ isteği 0 [B1 `ui.json`] | doğrulandı |
| 8. 1192 parça ↔ `robot.glb` 1192; glb = HEAD | geçti | Veri 1192 parça [B2]; `robot.glb` git blob özeti çalışma ağacında ve HEAD'de aynı (`c7d9901…`) [B2]. Düğüm sayısı ölçülmedi (demo sayfasının kaynağı 1192 diyor) | doğrulandı (düğüm: ölçülmedi) |
| 8. `tasarim/freecad/` içinde `rehber/` dışına dokunulmuş mu | hayır | F10e brief'inden (11.11 18:51) yeni, `rehber/` dışında dosya 0. `kabuk/gorsel/*.png`, `yerlesim-kontrol.json` (3.11), `lale_dongu*` (30.10), `kafa-yerlesim/kaynak/` (4.11) daha eski [B2] | doğrulandı |
| 8. PDF sayfa / en küçük yazı | 69 → 69; 8,1 → 8,1 pt | 69 sayfa; önceki sürümün PDF'i (B1'in HEAD'den çektiği `once.pdf`) de 69 [B2]. En küçük yazı ölçülmedi | sayfa doğrulandı |
| 8. 360 px, seçim, patlat / tak, küçük görünüm, ←→ | geçti | 360 px: 7 konumda genişlik 360 = 360, taşma yok. Seçim yeşil. Patlatmada halkalar parçayla gidiyor. Tak sırası ilerliyor. ←→ 31.5 → 31.6 → 31.5, son alt adımdan → 32 [B1]. Küçük görünüm 84 kabuk karesinin hepsinde var, kehribar yerinde [B2 gözle] | doğrulandı |
| 9a. Etek ön bandı iki parçalı yol | yol yok; bandı perçin somunu tutuyor | **Ölçülmedi** (B1'in süpürmesi `devir.py a` çıktı yazmadan sona erdi, yeniden başlatılmadı). Metin okuması: bulgu 8 | ölçülmedi |
| 9b. Arka servis kapağı ↔ orta bant | en çok 0,23 mm, temas | Kapağın köşelerinden orta bant sağın içinde 26 / 533, en derin 0,2306 mm; solun içinde 14, en derin 0,0587 mm; tersi ≈ 0 [B1 `devir_b.json`, köşe paritesi + nokta–üçgen, A'dan ayrı kod] | doğrulandı |
| 9c. Adım 41 "+x'ten kaydırarak takılmaz" | tutuyor (CAD duruşunda) | Metin ölçülenden fazlasını söylüyor (bulgu 7). Kol duruşunda ölçülmedi | **abartılı** |
| 10. Demo rengi | demo kendi sınıf paletini kullanıyor; 40 örnekte eşit 0 | Okuma [B2]: demo sayfası paleti sabit `TUR` (Robot-Tasarim-Demosu.html satır 309–310) ve modül paleti `MOD` (311); `gr` alanını okumuyor; `demo_uret.py` renk üretmiyor. Olgu düzeltmesi: dokuz sınıf renginden üçü rehberin sınıf paletiyle **aynı** (cf `#3d5a80`, lazer `#8e44ad`, gösterim `#95a5a6`), altısı farklı (ör. baskı `#e8913a` ↔ `#f0932b`, profil `#8d99a6` ↔ `#16a085`, bağlantı `#c9a227` ↔ `#d4ac0d`) | gerçek ↔ demo farkı doğrulandı; "sınıf = demo 0" yalnız örneklem için doğru |
| 11. Kural ihlalleri | yok | Değişen ve yeni dosyalarda yerel kullanıcı klasörü yolu 0 (tek eşleşme `rehber_uret.py` 237'deki "Masaüstü Chrome" sözcüğü, yol değil). Günlükte kişi olarak yalnız "Ahmet" geçiyor (baştan sona okundu). Kablolama: `semalar` ve `kablo_ad_uyari` HEAD ile aynı; adımlarda değişen alanlar yalnız `ev`, `sira_grup.{ev, kamera, saydam}`; parçalarda yalnız `gr`, `ip`; `is_` / `kablo` / `kablolama` / `not_` / `kontrol` değişen 0 [B2] | doğrulandı (soyad listesi elimde yok; yalnız bu okuma) |

## 3. Bulgular

### Engelleyici

Yok (rehberde). Hüküm, günlükteki iddialar yüzünden "düzeltme gerekli".

### Önemli

1. **Koyu temada görünmeyen yeni parçalar.** Kabuk alt adımlarında "simdi" parçalardan eşik altı: açık 1 / 212, koyu 20 / 212.
   Koyu temada 0–3 px kalanlar: 34.3 p0244 3 / 243, 34.4 p0242 2 / 290, 34.5 p0256 0 / 244, 34.6 p0254 2 / 291, 35.1 p0280 0 / 123,
   35.2 p0282 0 / 124. Öbür 14'ü 11–35 px ya da oranı < 0,20: 34.2 p0300 / p0302 / p0324, 34.4 p0304 / p0306, 34.6 p0308 / p0310,
   34.8 p0272, 34.9 p0266 / p0312 / p0314, 35.3 p0434, 36.1 p0288 / p0290. Hepsi bindirme cıvatası; 35.3 p0434 çekiç somun.
   - Nasıl ölçüldü: B1'in betiği (`b_gor.py`) sayfanın sahnesini ve kamerasını kendi WebGLRenderer'ıyla çiziyor (sRGB, kenar
     yumuşatma, gerçek malzeme, saydamlık, kenar çizgileri, zemin). Her yeni parçayı tek tek gizleyip güvenli alanda
     Σ|ΔRGB| > 24 pikselleri sayıyor. "Yalnız" değeri, parçanın kara zeminde tek başına beyaz silueti.
   - Gerçek ekran görüntüsüyle karşılaştırma (`b_ekran.py`): 11 parçada iki ölçüm aynı sayıyı verdi. Örnekler: 34.5 koyu p0256
     0 = 0, açık 56 = 56; 35.1 koyu p0280 0 = 0, açık 34 = 34. Ekran görüntülerinden farkı yeniden hesapladım: 34.5 koyu p0256'yı
     gizlemek 133 pikseli değiştiriyor, hepsi Σ ≤ 24.
   - Önemi: A'nın geçme şartı F10d'nin kimlik tamponu ölçüsü; o ölçü temadan bağımsız ve hâlâ geçiyor. Halkalar cıvatanın yerini
     koyu temada da gösteriyor. Ama "okurun gördüğü piksel" iddiası yalnız açık tema için geçerli.
   - Öneri: görünürlük ölçümünü iki temada koş. Koyu temada ya bu cıvatalara kenar ver (saydam bandın arkasındaki çelik koyu zeminde
     kayboluyor) ya da günlüğe "koyu temada halkayla gösteriliyor" diye tek tek yaz.
2. **31.3 p0762 görünmüyor** (A: 40 / 142). Ekran görüntüsünde > 24 değişen 0 px, B1 renderer'ında 0 / 165; 31.4'te de 0 / 238.
   A'nın `gorunurlukFark` ölçümü (sahne dışı render target, 4 örnek) bu parçada ekrandakinden farklı sonuç veriyor. Neden farklı
   olduğu ölçülmedi. Öneri: günlükteki "soluk iki parça geçti" satırını düzelt. p0762 hazırlıkta takılı bir ısıl gömme; halka yerini
   gösteriyor ama parça görünmüyor. Ya kamera / saydamlık düzeltilmeli ya da gerekçeli istisna olarak yazılmalı.
3. **34.7 zor** (A: açık). Hoparlör grubu (p0236 ön halka, p0237 kap, p0238 kelepçe `#e6e8ed`; p0438 hoparlör, p0443 ped `#212124`;
   hepsi opaklık 0,4) karede ≈ 80 × 80 px. 13 halkanın 4'ü üstünde, katmanlar ayırt edilmiyor [B1 sahne verisi, B2 gözle `34.7-acik`,
   `zoom-34.7`]. Ayrıca 13 halkanın 11'i hazırlıkta (adım 0) takılı ısıl gömmelerde; bu alt adımın asıl işi olan 2 kelepçe cıvatası
   kalabalıkta kayboluyor. Öneri: hoparlör grubuna yakın kadraj ya da patlatma; günlükte "hoparlör kara" ifadesini düzelt.
4. **Benzer çiftler.** 34.3 / 34.5 ve 34.4 / 34.6'nın 3B kareleri aynı (aynı kamera, tekrarlayan bant geometrisi). Ayıran tek görsel
   ipucu küçük görünümdeki kehribarın ≈ 9 px kayması. 49.3 / 49.4'te kamera farklı ama kompozisyon aynı. Etkileşimli sayfada panel
   başlığı ve alt adım listesi, basılı karede kare başlığı ayırıyor. Öneri: 3B karede seviye ipucu (ör. alttaki bandı numarasıyla
   ya da etiketle göstermek, ya da farklı yükseklikte kamera); en azından günlükte "ayırt ediliyor" yerine "yalnız yazıyla" yazılmalı.
5. **Kablo yolu renkleri CAD'den değil.** `app.js` 279: `p.renk || (gercek ? p.gr : sınıf)`. 12 kablo yolu parçası iki kipte de
   rehberin kendi kablo paletiyle çiziliyor: p1187 `#2f86d4` ↔ CAD `#f20d0d`, p1180 `#d63031` ↔ `#f20d0d`, p1188 `#2f86d4` ↔ `#1a73ff`
   … Bu HEAD'den kalma; kablolama içeriği bu pakette yasaktı. Öneri: günlükte "tek kaynak CAD (kablo yolları hariç, gerekçe)" diye yaz.
   p1187'deki kırmızı ↔ mavi farkı karar maddesi olarak açılmalı.
6. **"Bağlantı elemanı 1188" ifadesi.** Veride 893 bağlantı elemanı var; 1188, genel bakış ve alt adım konumlarındaki işaretlerin
   toplamı. Öneri: "işaret 1188 = konum başına yeni bağlantı elemanı 1188 (benzersiz 893)".

### Küçük

7. **Adım 41 metni ölçülenden fazlasını söylüyor.** Metin "+x'ten kaydırarak takılmaz" diyor ve hemen ardından kol duruşunu veriyor
   (S1 −45 / −20 / 0). +x yönündeki engel A'nın ölçümünde **üst kol tüpü** (5,34 mm); bu bir kol parçası, kol duruşunda yeri değişir.
   −x yönündeki engel (omuz bandı) gövdede. Yani "iki x yönü de kapalı" yalnız CAD duruşu için ölçüldü. Öneri: kol duruşunda ölç ya da
   metni "CAD duruşunda +x'te üst kol tüpüne değiyor" düzeyine indir.
8. **9a sonuç dili.** Günlük §7.1 "iki bacaklı bir yol yok" diyor. Anlatılan yöntemde birinci bacak 6 öteleme yönü × 1–12 mm, ikinci
   bacak +z; dönme ve ara açılar denenmemiş. Ölçülen şey "denenen iki bacaklı yolların hiçbiri serbest değil". "Perçin somunu tutuyor"
   sonucu, somun çıkarılınca düz +z'nin serbest olmasıyla destekleniyor. Bu kontrol 9a'yı ölçemedi.
9. **Isıl gömme halkaları.** Masada yapılan alt adımlarda (31.1, 31.3, 33.6, 34.7 …) hazırlıkta takılı ısıl gömmeler de bu adımın
   bağlantı elemanı gibi halka alıyor. Panel satırı "burada yalnız sayılır" diyor; karede ayrım yok. Öneri: bu halkaları farklı biçimde
   (ör. kesik çizgi) göster.
10. **Kenar çizgisi olup piksele yansımayan iki kare:** 31.4 koyu (4 kenar çocuğu, değişen 0 px) ve 49.4 koyu (1, 0 px) [B1]. Kenarlar
    opak parçanın arkasında; okura etkisi yok, bilgi.
11. **Adım 0'ın basılı karesinde başlık yok** (99 / 100) [B1]. Kapak / genel görünüm için kasıtlı olabilir; günlükte yazmıyor.

## 4. Kabuk alt adımları (42)

Bakılan: 42 alt adımın açık ve koyu karesi (`?cekim=1`, 1400 × 900, B1'in çektiği; çizelge `sheet/kab-00…20`). Seçilenlerin tam karesi
de açıldı: 31.5, 31.10, 34.7, 36.3 ve yakınlaştırmalar. Ölçüt F10d'ninki: "açık" = yeni parça, nereye bağlandığı ve bağlantı
elemanlarının yeri kareden okunuyor.

| alt adım | F10d | A (F10e) | B (bu kontrol) | gerekçe (B) |
| --- | --- | --- | --- | --- |
| 31.1 | açık | açık | açık | ReSpeaker yeşil, kabuk saydam pembe kenarlı taban, 10 halka |
| 31.2 | açık | açık | açık | beyaz kabuk pembe brakete; bağlantı elemanı yok |
| 31.3 | açık | açık | açık | kartlar ve 4 halka okunuyor; p0762 görünmüyor, halkası yerini gösteriyor |
| 31.4 | açık | açık | açık | sol kabuk pembe sağ kabuğa |
| 31.5 | zor | açık | açık | tabla opak pembe, 4 halka tablada; cıvatanın kendisi yalnız halka içinde |
| 31.6 | açık | açık | açık | kamera kartı yeşil, 10 halka |
| 31.7 | açık | açık | açık | kara QLED pembe yüz kabuğunda; koyu temada kenarlı |
| 31.8 | açık | açık | açık | 4 mavi tırnak, halkalı |
| 31.9 | zor | zor | zor | konnektörler küçük ve saydam katmanların arkasında; CSI şeridi seçilmiyor (A ile aynı) |
| 31.10 | zor | açık | açık (sınırda) | 9 halka dikişleri izliyor; 4 kafa kabuğu tek pembe saydam kütle, bazı halkaların ön / arka yüzde olduğu belirsiz |
| 33.1–33.10 | açık | açık | açık | bant saydam kenarlı, braket / komşu bant pembe, halkalar kenarda |
| 34.1, 34.2 | açık | açık | açık | braket pembe, bant saydam, halkalar |
| 34.3 | açık | açık | açık | tek başına okunuyor; 34.5 ile aynı kare (bulgu 4) |
| 34.4 | zor | açık | açık (sınırda) | içten soldan bakış, bant hâlâ kareyi dolduruyor; x 0 dikiş halkaları üst ortada okunuyor |
| 34.5 | açık | açık | açık | 34.3 ile aynı kare |
| 34.6 | zor | açık | açık (sınırda) | 34.4 ile aynı kare ve aynı gerekçe |
| 34.7 | zor | açık | **zor** | hoparlör grubu küçük, katmanlar ayrılmıyor, 11 / 13 halka hazırlık ısıl gömmesinde (bulgu 3) |
| 34.8, 34.9 | açık | açık | açık | |
| 35.1, 35.2 | açık | açık | açık | braket pembe, halkalar; koyu temada p0280 / p0282 görünmüyor (halka var) |
| 35.3 | zor | açık | açık | direk pembe, taşıyıcı kara saydam kenarlı, 6 halka; çekiç somun kanalın içinde (halkayla) |
| 35.4 | açık | açık | açık | ekran saydam, 4 × 2 VESA halkası |
| 35.5 | açık | açık | açık | çerçeve 8 × 2 halka |
| 36.1, 36.2 | açık | açık | açık | |
| 36.3 | zor | açık | açık (sınırda) | 3 halka dikiş yerini veriyor; dikiş çizgisi ve cıvatalar pembe saydam kütlede seçilmiyor |
| 49.1 | açık | açık | açık | kapak taban pembe kenarlı, hub kutusu |
| 49.2 | açık | açık | açık | test adımı, yeni parça yok, robotun tamamı |
| 49.3 | açık | açık | açık | kapak gri, bant pembe, 7 halka; 49.4'e çok benziyor (bulgu 4) |
| 49.4 | açık | açık | açık | aynı; hub karede görünmüyor (kapağın içinde) |
| 49.5 | açık | açık | açık | iki servis kapağı saydam, 4'er halka |

Toplam: F10d açık 34 / zor 8; A açık 41 / zor 1; **B açık 40 / zor 2 / anlaşılmıyor 0** ("sınırda" 4: 31.10, 34.4, 34.6, 36.3).

## 5. Ölçülemeyenler

- **9a etek ön bandı süpürmesi:** B1'in `devir.py a` süreci (PID 45440) bu kontrol başladığında (01:15) koşuyordu, 01:20 yoklamasında
  yoktu ve `devir_a.json` yazmamıştı. Brief gereği yeniden başlatılmadı. Yalnız günlüğün metni okundu (bulgu 8).
- **Adım 41, kol duruşunda süpürme:** ölçülmedi (FreeCAD'siz kol duruşu kurulmadı).
- **PDF en küçük yazı boyutu:** ölçülmedi; yalnız sayfa sayısı (69 / 69).
- **`robot.glb` düğüm sayısı:** ölçülmedi (blob özeti HEAD ile aynı olduğu için değişmedi).
- **İşaret konumu ve renk, kalan 34 konum:** B1 66 / 100 konumu ölçtü (42 kabuk + 24 başka). Kalan konumlarda ölçülmedi.
- **Okurun pikseli, kabuk dışı adımlar:** ölçülmedi (yalnız kabuk alt adımları, iki tema).
- **F10d / F10a / F9b / çarpışma / regresyon zinciri:** bu kontrolde koşulmadı (brief: depoya yazan betik koşulmaz). A'nın çıkış kodları
  ölçülmedi, yalnız günlükte okundu.
- **Bağlandığı yer, kabuk dışı (186 çiftin kabuk dışındakiler) ve 7 masa tabanı:** ölçülmedi.
- **A'nın `gorunurlukFark`'ı ile ekran görüntüsünün neden farklı sonuç verdiği** (31.3 p0762'de 40 ↔ 0): ölçülmedi.
- **Seçim yeşili / kehribar ΔE değerleri:** hesaplanmadı (yalnız gözle).
- **Soyad / takma ad taraması:** kişi listesi elimde yok; yalnız günlük okundu ve yerel yol tarandı.
