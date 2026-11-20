# P10.8c bağımsız kontrol

Kontrol ajanı, 19.11.2026. Dal `lale-duzeltme`, HEAD = uzak = `d8ade70`. Uygulama günlüğü (`P108c-gunluk.md`) okundu, iddialar
kaynaktan yeniden ölçüldü. FreeCAD açılmadı: FCStd'ler zip içindeki `Document.xml` ve `.brp` dosyalarından, STL'ler doğrudan okundu.
Bozma denemeleri depo dışı kopyalarda yapıldı. Depoya yazılan tek dosya bu dosya; koşulardan önce ve sonra `git status` aynı (38 satır:
19 eski kir + paketin 19 satırı).

**Karar: DÜZELTMEYLE GEÇER.** Standart numarası düzeltmesi doğru, sınırlı ve korumalı. M7 D / E onarımı tasarımla aynı ölçülüyor.
Commit'ten önce düzeltilmesi gereken bir şey var: yeniden üretilen kafa notu artık kendi kaynağıyla çelişiyor (O1). Ayrıca okura dönük
birkaç cümle eskidi (O2), etek kuponunun deneme yöntemi yazılmamış (O3).

## 1. Bulgular

### ORTA

**O1. Kafa notunun omuz anlatısı bu paketle çelişkili hâle geldi.**
- Yer: `tasarim/freecad/lale158/kafa-yerlesim/uygulama_metin.py` (`OZET_MD` satır 22, `ATLANAN` satır 97–99, `KARAR` ilk madde) ve
  bunlardan üretilen `uygulama-notu.md` ile `rapor.html`.
- Kanıt: `carpisma-sonuc.json` `bolumler.omuz` bölümünde durum "tamam". Koşu 20261119-075818, 08:00–11:11 (11.489 s), bütün modüller,
  `tek_kosu` true. Yeni not ise "zincir omuz bölümü hariç koştu", "omuz bölümü eski kayıttan" ve "omuz bölümü ve omuz regresyonu
  koşmadı" diyor. Ayrıca "omuz sonucu koşu 20261119-075818'ten, yeni kabuktan önce; dosyada `tek_kosu` true" diyor. Karar listesinin
  ilk maddesi "omuz bölümü (~4,8 saat) koşulsun mu?" diye soruyor. HEAD'deki not tutarlıydı (koşu 20261103, `tek_kosu` false).
  Çelişkiyi yeniden üretim getirdi: üreticideki sabit metin yeni veriyle birleşti.
- Etki: okur yapılmış 3,2 saatlik bir koşuyu açık karar sanır. "Yeni kabuktan önce" ifadesi de yanlış.
- Öneri: commit'ten önce bu üç metni `CRP["tek_kosu"]` ve omuz koşusunun tarihine bağlayın (ya da cümleleri kaldırın), not ile raporu
  birlikte yeniden üretin. Bu yapılmadan § 10.2'deki "kafa-yerleşim … kapandı" kaydı yazılmamalı.

**O2. Okura dönük eski cümleler (paketin konusu, paket dokunmadı).**
- `tasarim/freecad/test/README.md` satır 253: "Etek ön için … kuponu yok … Açık iş olarak kuyrukta." Kupon artık var.
- `planlama/baski-listesi.md`, "Yanak ve bant kuponları" bölümü: "etek önün 'somun takılıyken' kuponu yok". Bu bölüm elle yazılmış;
  `F4c-liste.py` onu olduğu gibi korur, yani F4c yenilense de düzelmez.
- `planlama/baski-listesi.md` satır 208, `F4c-partiler.md` satır 40 ve `F4c-partiler.json` `m7_uyari` hâlâ "D / E bölümü bugünkü
  dirsekle koşmuyor … yeniden üretilmeli" diyor. Bu artık yanlış. Uyarıyı üreten `m7_eski_uyari()` `yalniz_c` alanına bakıyor; alan
  silindiği için F4c yeniden koşunca uyarı kendiliğinden kalkar.
- `karar-kuyrugu.md` satır 1893 hâlâ "BİLİNEN ESKİ" çıktısına atıf yapıyor. Bu çıktı artık yok.
- Öneri: README ve baskı listesi cümleleri kapanışta tek satırla düzeltilsin. M7 uyarısı ve kuyruk satırı soru (b) ile birlikte ele
  alınsın.

**O3. Etek kuponunun deneme yöntemi ve kabul ölçütü yazılmamış.**
- Kanıt: M7, yanak ve bant kuponlarının README'de "Test" ve kabul bölümü var. Etek kuponunun yok; elde yalnız JSON'daki `gerekenler`
  listesi var.
- Mantık açığı: günlük ve betik başlığı "kupon zorlamadan geçerse gerçek bant da geçer" diyor. Gerekçe yalnız sertlik: dilim gerçek
  banttan sert. Ama üst parça elde serbest tutulan 8 × 42,5 × 29,5 mm'lik bir dilim. Flanşın üstünden eğilip döndürülerek geçirilebilir;
  gerçek bant (234 × 175 mm, z +88 dikişine bağlı) bunu yapamaz. Yöntem hareketi kısıtlamazsa kuponun "geçti" sonucu gerçek bant için
  kanıt olmaz. Ters yönde de sorun var: kısa ve sert dilim, en çok 10 mm³ ortak hacimle büyük ihtimalle takılır. O zaman sonuç
  "belirsiz" olur (betik başlığı da bunu söylüyor).
- Öneri: README'ye kısa bir bölüm. (1) Önce yalnız +x, sonra yalnız −z. (2) Dudak yüzü dile paralel kalır, üst parça döndürülmez (alt
  parça mengenede, üst parça düz bir takozla itilir). (3) Geçti: elle itişle oturur, flanş ya da boss'ta beyaz iz ya da çatlak yok.
  Kaldı: belirsiz, K55 b. Sonuç kaydının nereye yazılacağı da belirtilsin.
- Günlükteki "Sınır (JSON'da da yazılı)" ifadesi doğru değil. `etek-kuponu.json`'da sınır ya da kısıt metni yok, yalnız betik
  başlığında var. JSON'a `sinir_` alanı eklenebilir.

**O4. M7 D1 / D2 kütleleri baskı listesinde ve F4c'de eski kaldı. Doğrulayıcı bunu görmüyor.**
Değerler F4c'nin kendi formülüyle hesaplandı (`sure_sa`: g ÷ 1,27 ÷ 10 mm³/s × 1,3). Betik koşulmadı.

| Satır | Bugün (F4c / baskı listesi) | Yeni `m7-kupon-sonuc.json` ile |
|---|---|---|
| D1 g (tahmini / %100) | 40,9–87,9 | 41,8–90,3 |
| D1 sa | 1,16–2,50 | 1,19–2,57 |
| D2 g | 41,4–86,2 | 42,3–88,6 |
| D2 sa | 1,18–2,45 | 1,20–2,52 |
| E | 14,3–17,9 g | aynı (STL baytı HEAD ile aynı) |
| Parti 0 toplam g | 257,4–420,0 | ≈ 259,2–424,8 |
| Parti 0 PETG-CF g | 175,7–301,1 (0,18–0,30 kg) | ≈ 177,5–305,9 (0,18–0,31 kg) |
| Parti 0 sa | 7,32–11,94 | ≈ 7,37–12,08 |
| D2'siz sa | 6,14–9,49 | ≈ 6,17–9,56 |

Etkilenen satırlar: `baski-listesi.md` 97, 103, 194, 204, 205, 208; `F4c-partiler.md` 12, 33, 34, 38, 40; `F4c-partiler.json`
`partiler.0`. README'deki ölçü (73,9 mm) baskı listesinde yok; orada ölçü sütunu da yok. `F4c-dogrula.py` GEÇER veriyor, ama
kupon kütlelerini `m7-kupon-sonuc.json` ile karşılaştırmıyor. Bu eskimeyi hiçbir doğrulayıcı yakalamıyor (bkz. soru b).

### DÜŞÜK

**D1. `artirma_eki_sil` kodu otorite sayıyor. Kardeş kuralı olmasa bazı uyumsuzlukları sessizce "düzeltirdi".**
- Depo dışında denendi: ("Civata M3x16", kod "M3x6") "Civata M3x6" oluyor. ("Rulman 626", "625") "Rulman 625" oluyor. ("Kablo 12",
  "Kablo 1") "Kablo 1" oluyor. ("X 0010", "X 9") "X 9" oluyor.
- Bunları `artirma_denetle`'nin kardeşsiz kuralı `--kaynak`'ta HATA yapar. Üretim de başlamadan `kaynak_denetle`'yi koşup düşerse
  durur (`rehber_uret.py` 758–769).
- Kalan risk: aradaki bütün etiketler aynı belgede varsa (ör. "Kablo 1" … "Kablo 11" ve "Kablo 12", kod "Kablo 1") ad sessizce
  değişir. Bugünkü 1238 parçada böyle bir durum yok.
- Öneri: bozma listesine bir negatif ekleyin: etiket "Civata M3x16", kod "M3x6"; beklenen "kardeşsiz HATA".

**D2. Etek alt parçasında desteksiz düz çıkıntı.**
- STL'den ölçüldü: baskı yönünde z 3,0'da 120 mm² aşağı bakan düz yüz var, x −10…−6, y −13,75…16,25 (baskı koordinatı). Bu, braketin
  dilimde kalan x 240–244 kısmı. Taşıyıcı plakası x 244'ten başladığı için tablanın 3 mm üstünde, 4 mm genişliğinde, desteksiz 90°
  bir çıkıntı oluyor.
- Öneri: `TAS["plaka_x"]` 240'tan başlasın ya da kutu x 244'ten kesilsin.
- Üst parçanın tablaya teması 3 × ≈ 36 mm (110 mm²), boyu 29,5 mm. Brim önerilir.

**D3. Gerçek perçin somunu PETG ayağa takılacak.**
- `gerekenler`'de "M3 perçin somunu (2 mm Al için) + perçin aleti" yazıyor. Kuponda ayak 2 mm Al 5754 değil, PETG. Sıkıştırınca
  ezilebilir ya da çatlayabilir, flanş yüksekliği gerçekteki gibi olmayabilir.
- Kumpasla flanş ölçümü listede var, ama ayağın PETG olduğu JSON'da ve notta yazmıyor (betik başlığında P10.8a O2'ye atıf var).
- Öneri: bir cümle ekleyin; flanşlı biçimi ilk deneme olarak önerin (alet istemez).

**D4. Kupon tazelik denetiminde iki küçük boşluk.**
- (1) Bugünkü `arayuz.py`'de kaybolan anahtar sessizce atlanıyor (`kk in bug`, `bug is not None`).
- (2) E kuponu omuz FCStd'sine md5 ile bağlı değil. Tüp yarıçapları `arayuz.DIRSEK` `tup_ri` / `tup_ro` üzerinden dolaylı izleniyor;
  bu, bugünkü geometri için yeterli.
- `--kati` artık etkisiz. Depoda bu bayrağı kullanan betik yok, yalnız belgelerde geçiyor. Gerileme değil.
- Önceki turun "yeni eskimeyi gizleme" hatası geri gelmedi: istisna listesi tamamen kalktı.

**D5. `m7_kuponlari.py` için "sabit sayı kalmadı" iddiası tam doğru değil.**
- Kulaklar 178 / 192, TZ − 41 / − 30, destek x 213, `R_BIL_DIS` 31 ve `PIM_BOY` 25 hâlâ sabit. Bunlar `dirsek_parcalar.py`'de de sabit.
- D1 ile FCStd dilimi arasındaki doğrulama (fark 1 mm³'ü aşarsa betik durur) sapmayı yakalar. Kabul edilebilir; günlükteki ifade
  düzeltilsin.

**D6. Kafa notundaki kütle ve devrilme sayıları 09.11 tarihli kaynaktan geliyor.**
- Not, toplam kütleyi ve ızgara paylarını `uygulama-ivme.json`'dan okuyor (son commit 09.11). Değer 26.120,6 g, yani model 25.720,6
  + 400 g kablo payı.
- Güncel montaj (`montaj-analiz.json`, `carpisma-sonuc.json`) 25.835,1 g diyor; payla 26.235,1 g. Fark ≈ 115 g.
- Not "1.225 parça" (19.11) ile 09.11 kütlesini aynı cümlede veriyor. Günlükteki "F10w montajından gelen sayılar" ifadesi kütle ve
  devrilme için geçerli değil.
- Etki küçük. Not bir sonraki `uygulama_ivme` koşusuna kadar böyle kalabilir; günlükte doğru yazılsın.

**D7. Kalıcı sızıntı ve okur yerleri.**
- `ISO 738[1-9]` izlenen dosyalarda (satır sayısı, bilgi): `ikinci-kontrol.json` 28, `robot-montaj.step` 21, `F10d-dogrula.json` 18,
  `planlama/rehber/kontrol.json` 17, `uygulama-ikinci.json` 14, `F10e-dogrula.json` 14, `M6_erisim_sonuc.json` 10,
  `rehber-veri.json` 9 (`.js` tek satırda), `F10f-dogrula.json` 2. Kuyruk, P108b günlüğü ve denetim kodundaki geçişler hatayı
  anlatıyor.
- Git dışı: `tasarim/cad/lale158-model.js` ve `rapor/lale158-model.js` (`.git/info/exclude`).
- Okura dönük temiz yerler: PDF 89 sayfa, metninde 0 (parça adı hiç geçmiyor), `robot.glb` 0, demo HTML 0, `robot-bom.csv` ve modül
  BOM'ları 0, baskı listesi 0.
- Tam üretime kadar rehber sayfası 9 yanlış adı gösterir. Kalıcı kalan: `robot-montaj.step` ürün adları (CAD'de açan görür).

**D8. Standart numarası denetimi her ISO / DIN numarasına bakar, yalnız bağlantı elemanlarına değil.**
Depoda rehber dışında ISO 273 (geçiş deliği), ISO 2936 (alyan), ISO 4762 ve ISO 4017 geçiyor. Rehber metni bunlardan birini anarsa
`--kaynak` HATA verir. Bu bilinçli bir seçim, sorun değil; yalnız bilinsin.

## 2. Standart numarası (görev 1)

**Kök neden, FCStd XML'inden bağımsız olarak doğrulandı.**
- Altı FCStd'nin hepsi FreeCAD 1.1R20260928 ile kaydedilmiş, hiçbirinde yinelenen etiket yok.
- Kabukta "Cerceve civatasi M3x6 ISO 7380…7387" zinciri 8 nesne (K204–K218, ikişer artan nesne adı). Yanlış numaralı olanlar 7 nesne
  (K206–K218). Sekizinin de `Kod` değeri "M3x6 ISO 7380".
- Dirsekte "Yaka civatasi M3x6 ISO 7380 / 7381" zinciri 2 nesne (D054 / D056); yanlış numaralı olan 1 nesne. Dirsek belgesi rehberde
  sağ ve sol olarak iki kez kullanılıyor, bu yüzden rehberde 2 ad.
- Rehber verisinde yanlış ad 9 (p0411–p0423 arası 7, p0618, p0675). Günlükle aynı.
- 0NN dışındaki artırma adayları için tarama yapıldı: her belgede "sondaki sayı − 1 de etiket olarak var mı" diye bakıldı. Origin /
  eksen / düzlem nesneleri dışında yalnız bu 8 nesne çıktı.
- 2 haneli sayıyla biten etiketlerde (M4x16 gibi) FreeCAD 1.1 eski biçimi, yani 0NN ekini kullanmış. Bunları `kopya_eki_sil` zaten
  tanıyor.

**1238 parçada önce / sonra karşılaştırması.**
- Eski ve yeni `kopya_eki_sil` yalnız bu 9 parçada farklı sonuç veriyor; hepsi "… ISO 7380" oluyor.
- Yeni kuralla CAD'den kurulan adlar commit'li veriyle karşılaştırıldı: 21 fark var. 9'u bu düzeltme. Kalan 12'si taban kablo yolu
  adları; bunları üretim ayrı bir yoldan (`kablo_ad`) kuruyor ve kural onlara dokunmuyor.
- Yeni adlarda 0NN kalıntısı yok. Ad ile kod arasında standart çelişkisi 0.
- Standart kalıbı taşıyan görünen adlar ve sayıları: ISO 7380 47, DIN 985 12, DIN 933 9, DIN 125 8, DIN 913 8, DIN 976 4.

**Ölçütün sınır durumları (depo dışında denendi).** Aşağıdakiler değişmiyor:
- "Civata M3x6" (kodlu ya da kodsuz), "DIN 912", "Rulman 625ZZ".
- "Parca (2)", kodu boş ya da sayıyla bitmeyen "Parca 2", "Sonar 8", "Servo 13".
- "… ISO 7381" + kod "… ISO 7381" (gerçekten 7381 olan parça).
- "… ISO 7380" + kod "… 7381" (ad küçük, kod büyük).
- "… ISO 7380 (sag)".

Değişenler: "… ISO 7381" + kod 7380 (doğru). DIN 913 → 912, DIN 935 → 934 ve DIN 126 → 125 kaymaları kodla düzeliyor. Kod ile adın
gerçekten çeliştiği durumlar D1'de; bugün bunları kardeş kuralı korur.

Gerçek 7380 ve 7381 parçaları yan yana olursa: kod otorite olduğu için ikisi de doğru gösterilir. Ama 7381 bilinen kümede yok, `--kaynak`
HATA verir; numara kümeye bilinçli olarak eklenmeli.

**Bilinen standart kümesi doğru ve tam.**
- CAD kodlarında: DIN 125, 127, 912, 913, 933, 934, 976, 985 ve ISO 7380.
- `planlama/maliyet.json`'da: ISO 7380, DIN 912, 913, 916, 985, 976, 127, 125.
- Birleşimleri tam olarak bu 10 numara. Eksik ya da fazla yok. DIN 933 / 934 yalnız CAD'de (taban bara saplaması takımı); DIN 916
  yalnız maliyet listesinde.
- Küme bu iki kaynaktan çalışma anında kurulabilirdi. Ama kodu kendi kendini doğrulayan bir kayıt olurdu. Elle yazılmış izin listesi
  ve kümede olmayan CAD kodunun `--kaynak`'ta HATA vermesi daha güvenli; kabul ediyorum.

**Veride bozma (depo dışı kopya, `denetle`).**
- Commit'li veri: GEÇMEZ, standart hatası 18. Beklenen.
- 9 adı yeni kuralla kurulmuş benzetim verisi: GEÇER, standart hatası 0.
- Parça adına ISO 7389 sokulunca 2 hata (bilinmeyen numara ve ad ↔ kod).
- DIN 912 kodlu bir parçanın adına DIN 913 eklenince 1 hata (ad ↔ kod).
- Adım metnine ISO 7381 ya da ISO 4762 eklenince 1'er hata.
- 16 yeni bozma denemesinin hepsi yakalandı; doğru 9 ad değişmedi.

**Veri kipinin bugün çıkış 1 vermesi beklenen durum.** Üretim aynı yolu kullanıyor: `rehber_veri.py` 394, 788 ve 847
`RM.kopya_eki_sil` çağırıyor; ad FreeCAD `o.Label`'ından, kod `o.Kod`'dan geliyor (`m6_yukle.py` 44). Bu yüzden tam üretimden sonra
standart hatasının 0'a ineceği kanıtlanmış sayılır.

Adların tekleşmesi parça listesini değiştirmez: bağlantı elemanı satırları `(grup, kod)` anahtarıyla toplanıyor (`rehber_veri.py`
856–862). Satır sayısı ve "liste 257" onay sayısı etkilenmez.

## 3. Kuponlar (görev 2 ve 3): kendi doğrulama tablom

| Arayüz | Tasarım | Bağımsız ölçüm | Kaynak |
|---|---|---|---|
| Pim r / bilezik iç r / bilezik dış r | 25,4 / 28,25 / 31,0 | D1 ve D2 STL, y = TUC + 12 kesiti: 25,4 / 28,25 / 31,0 | STL'de ışın-kesit, FreeCAD'siz |
| Dış kol | 8 mm (`catal_dis_kol`) | FCStd "Dirsek catali" BREP köşeleri: x 219,9 ve 227,9 (8 mm); x en çok 227,9; y en çok −145 | `dirsek-montaj.FCStd` zip |
| Kupon kutusu | 73,9 × 72 × 33 | D1 / D2 STL: 73,9 × 72 × 33; x −31 … 42,9 | STL |
| D1 hacmi | 71.079,65 mm³ (B-rep) | STL 71.075 mm³; açık kenar 0 | STL |
| Tüp iç / dış r (E) | 25,65 / 28,0 | E STL, z = 12 kesiti: 25,65 / 28,0 | STL |
| Geçme boşlukları | 0,25 / 0,25 | 25,65 − 25,4 ve 28,25 − 28,0 | yukarıdaki iki satırdan |
| Kelepçe delikleri | Ø3,4; y −151 / −162 | `dirsek_parcalar.py` `KELEPCE_Y` = (TUC + 19, TUC + 8) = (−151, −162) | kaynak kod |
| STL md5 ↔ JSON kaydı | dört kupon | 4 / 4 aynı | dosya |
| E kuponu | taze mi | STL baytı HEAD ile aynı (15.10); geometri bugünkü tasarımla aynı. STEP gövdesi ve JSON kaydı yeniden yazıldı | git, STL |
| Etek kuponu STL | üst 8 × 42,5 × 29,5; alt 20 × 52,5 × 33 | STL kutusu aynı, açık kenar 0; hacim 3,625 / 10,798 / 10,911 cm³ | STL |
| Etek sağ ↔ sol | sol X aynası | BREP köşe sınırları: orta bant, z +105 braketi ve perçin somunu x'te ayna. Ön bandın merkez ucu farklı (sağ x 26, sol −38; dikiş dili), z +105 bölgesinden uzak. P108b B-rep ölçümü sol için de aynı eğriyi veriyor (somun 1–8 mm, 9,4 / 8,9 mm³) | FCStd zip, `brep-yol.json` |

- `m7_kuponlari.py` yalnız `test/` altına yazıyor (STL, STEP, JSON). `dirsek_parcalar.py` modül düzeyinde dosya yazmıyor. İki FCStd
  açılıyor, kaydedilmiyor. `git status`'ta hiçbir FCStd değişmedi.
- Etek kupon betiği rehberin iki parçalı yolunu deniyor. Kupon parçası z +10'da (dx, 0, 10) noktasından x 240'tan 0'a gelir, sonra
  dz 10'dan 0'a iner. JSON'da kupon ve tam model eğrisi aynı: dz 0,5–8,5 arası, en çok 9,98 mm³.
- Betiğin "tam modeli" yalnız orta bant, braket, perçin somunu ve ısıl gömmelerden oluşuyor; sonar gibi öbür engeller P108b ölçümünde.
- Dikiş kesiti (dudak 1,5, dil 1,25, boşluk 0,25) JSON'daki betik ölçümünden okundu. Ben ayrıca kesit almadım.
- Tazelik denetiminde bozma (depo dışı kopya; çıkış kodu doğrudan okundu):

| Bozma | Sonuç |
|---|---|
| `catal_dis_kol` 8 → 9 | ESKİ, çıkış 1 |
| `TUP_PIM_R` 25,5 | ESKİ (2 satır) |
| Dirsek FCStd'ye 1 bayt | ESKİ |
| D1 STL'ye 1 bayt | ESKİ |
| Kabuk FCStd'ye 1 bayt | bant ve etek ESKİ |
| Etek flanşlı STL silindi | ESKİ |
| Dosyalar geri yüklendi | TAZE, çıkış 0 |

16 denetim şunlar: yanak 3, bant 3, etek 4 (kaynak + 3 STL), M7 kaynak 1, M7 STL 4, M7 arayüz 1.

## 4. Kafa notundaki iki metin değişikliği (görev 4)

- **12 V satırı kayıtla uyumlu.** `elektrik.md` 337 ve 371: göğüs ekranının 12 V'u tabandaki F6 → LM2577 + LM2596 hattından. Boyun
  demetinde yalnız kafanın 12 V çifti var (37, 275). `KY.yollar()["12 V"]` en üst y 1.205, `A.S3` 1.270; ikisi de koşturularak
  doğrulandı. `lale158-kontrol.json`: "taban guc panelinden". Satır HEAD notundaki elle düzeltmenin içeriğini taşıyor.
- **L USB-A dirseğin çıkması uydurma değil.** `kablolama-on-kararlar.md` §5 (14.11): "USB ses kartı, ~30 cm USB-A uzatma ve L USB-A
  dirsek kablajdan çıkar; Pi port 2 boş kalır". Aynı kayıt 323, 425 ve `kablolar.json` #53'te, `maliyet.json` satırında da var ("ses
  kartı uzatmasıyla birlikte kablajdan çıktı"). Yedek koşulu kayıtta duruyor: KT2 geçmezse uzatma ve dirsek o zaman alınır. Notta bu
  koşul yok, ama "listede olmayan" kalemler zaten koşullu adaylar; geri alınması gerekmez.
- Günlük bunu "uygulama ajanı kararı" diye yazıyor; aslında 14.11 kararının uygulanması.
- **Not ve rapordaki diğer farklar** (kelime kelime bakıldı):
  - Tarih değişti; F10w kafa ve tork sayıları güncellendi.
  - Kütle ve devrilme sayıları değişti; kaynakları D6'da.
  - Ses kartı satırları kalktı; hoparlör yolu 824 mm oldu.
  - Hoparlör ön halkası için "> 4,243 (en yakın 5 parçada yok)" yazıyor; bu bir alt sınır.
  - Koşu kimliği değişti; omuz anlatısı O1'de.
  - Beklenmedik içerik yok. Yeni kişi adı, yerel yol ya da e-posta eklenmemiş.
  - Değişen satırlarda kullanıcının soyadı geçiyor, ama bu satırlar HEAD'de de aynı biçimdeydi; kanca kalıbında yok.

## 5. Kendi koşularım (depo kökünden, `py -3 -B -X utf8`)

| Komut | Çıkış | Sonuç |
|---|---|---|
| `carpisma_kos.py kontrol` (başta / sonda) | 0 / 0 | 17 dosya kayıtla aynı |
| `rehber_denetim.py --kaynak` | 0 | CAD kaynak 947; eskime HATA 0, bilgi 2 ((gösterim) etiketleri); standart HATA 0; artırma silinen 9, kardeşsiz 0; onay farkı 0 (kablo 220, liste 257, metin 1199) |
| `rehber_denetim.py --bozma-denemesi` | 0 | 346 / 346 |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 114 / 114 |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / toplam bozma 174 |
| `F10l-birlesim.py <kök> d8ade70` | 0 | GECER; B cümle 1177 / 1177, eklenen 0, silinen 0 |
| `kupon_tazelik.py` (ve `--kati`) | 0 / 0 | TAZE (16 denetim) |
| `F4c-dogrula.py` | 0 | GECTI (kupon kütlesine bakmıyor, O4) |
| `rehber_denetim.py` (veri kipi) | 1 | standart 18 (beklenen) |

`git diff --quiet HEAD` ile değişmediği görülenler: `dongu-158.md`, `karar-kuyrugu.md`, `sonuc-rapor.html`, demo HTML,
`baski-listesi.md`, `F4c-partiler.json`, `.md`, `.py`, `F4c-liste.py`, `F4c-dogrula.py`, `maliyet.json`, `rehber-veri.json`,
`dirsek_parcalar.py`, `arayuz.py`. İzlenen 17 dosya `carpisma_kos kontrol` ile aynı. FreeCAD kilidi "boş".

**Gizlilik (görev 7).** Kanca kalıpları şunlara uygulandı: on bir değişen metin dosyasının eklenen satırları (STEP dahil), iki STL ile
altı yeni dosyanın tamamı (STL, JSON, günlük); toplam 19 girdi. Kalıplar: anahtar, parola ataması, e-posta, IBAN / telefon, yerel
yol, takma ad, ekip adı. Bulgu 0. STEP'te telefon kalıbına uyan koordinat dizisi de 0.

## 6. Kapanış tarifi (§ 11) ve önerilen kayıtlar (§ 10)

- **Sıra:** soru (c) tam üretimden ÖNCE kararlaştırılmalı. § 11.7 "§ 10.4 seçilirse … tam üretim yeniden" diyor; bu ikinci bir
  ≈ 42 dakikalık koşu demek. Metin değişecekse onay yenilemesi ve F10l'den sonra tek bir üretim koşulsun.
- **Eksik adımlar:**
  - O1'in düzeltilmesi ve not ile raporun yeniden üretilmesi; `uygulama_rapor.py` sistem Python'uyla koşar, FreeCAD istemez.
  - O2'deki README ve baskı listesi cümleleri.
  - Tam üretimden sonra ad farkının yalnız 9 olduğu, betikle sınansın: CAD'den yeni kuralla ad kur, `rehber-veri.json` ile
    karşılaştır. Beklenen fark 9 düzeltme + 0; 12 kablo adı zaten eşit olmalı.
- **§ 10.1:** "Tam üretim ve zincir 2–10 geçti" cümlesi koşul olarak doğru kurulmuş. "kafa-yerleşim notu üreticisi düzeltilip yeniden
  üretildi" ifadesi O1 düzeltilmeden yazılmamalı.
- **§ 10.2:** kafa-yerleşim maddesi "kapandı" değil, "üretici düzeltildi, omuz metni …" olmalı (O1). M7 maddesine "E STL'si 15.10
  baytında kaldı, geometri güncel" eklensin. Kuyruk satırı 1893'teki "BİLİNEN ESKİ" atfı düzeltilsin.
- **§ 11.5:** etek alt parçası için "taşıyıcıdaki Ø10 boşluk" kontrolüne D2'deki çıkıntı eklensin.
- **§ 11.3** beklentileri doğru. Ad tekleşmesi parça listesi satırlarını ve onay sayısını değiştirmez (bkz. § 2).

## 7. Üç açık soru (karar Ahmet'in; görüşüm)

**(a) Etek kuponu Parti 0'a eklensin mi?** Evet, ama "toplama katılmaz" bloğuna (yanak ve bant gibi) ve iki koşulla. Önce D2'deki
çıkıntı giderilsin ve README'ye O3'teki yöntem yazılsın. Maliyet küçük: üst + flanşlı alt ≈ 12 g, ≈ 20 dk. İlk deneme flanşlı biçimle
yapılsın; perçin aleti gerekmez. Delikli biçim perçin somunu ve alet gelince. Bilgi değeri asimetrik: kuralına uygun "geçti" K55 a'yı
etek ön için güçlendirir, "kaldı" ise belirsizdir. Bunu bilerek basmak yine de değerli; rehberdeki en riskli geçmelerden biri hiç
denenmedi. Blok elle yazılmış ve `F4c-liste.py` onu koruyor (Kablo deneme parçası … STL durumu arası); orada etek önü için "kupon
yok" cümlesi de aynı anda düzeltilsin.

**(b) Baskı listesi ve F4c bu kapanışta yenilensin mi?** Evet. Değişiklik küçük ve belirlenimci; şu an okura yanlış bir uyarı
gösteriyor ("D / E koşmuyor").
- Sıra: `Y2b-baski.py` → `F4c-partiler.py` → `F4c-liste.py` → `F4c-dogrula.py` (0).
- `Y2b-baski.json`'un baytça değişmediğini `git diff` ile doğrulayın; girdisi değişmedi.
- Etkilenecekler: `F4c-partiler.json`, `F4c-partiler.md`, `baski-listesi.md` (Parti 0 satırları, toplamlar, uyarının kalkması).
- `F4c-rapor.html` elle alınmış eski bir anlık görüntü; hiçbir betik onu üretmiyor. Aynı kalır, ama içindeki Parti 0 sayıları eskir.
  Ya tarihli bırakılsın ya da başına bir satır eklensin.
- Demo, F9b ve regresyon baskı listesini okumuyor (grep ile bakıldı). Yine de zincir 8 ve 10 koşulacağı için gerekirse yakalanır.
- İsteğe bağlı: `F4c-dogrula`'ya Parti 0 kütlelerini `m7-kupon-sonuc.json` ile karşılaştıran bir denetim eklenmesi (O4'teki kör nokta).

**(c) Rehber F1'deki "bu bant için kupon henüz yok" cümlesi çevrilsin mi?** Evet. Commit'ten sonra cümle yanlış olur, çünkü kupon
dosyası var. Ama bu kapanışta ve tam üretimden önce yapılsın (bkz. § 6), dikkat edilecek üç şeyle:
- Yalnız ön sağ ve ön sol bant metinleri (`rehber_metin.py` 1236 ve 1253) değişir. Çerçeve, omuz ve diğer bantlardaki aynı cümle
  (1477, 1512, 1530) değişmez; onların kuponu yok.
- Sol bant için "sağ bant kuponuyla (ayna) çıkarım" ibaresi gerekir.
- Rehbere betik yolu yazmak yerine kupon adı yeterli. "Kupon zorlamadan oturursa" demek O3'teki yöntem yazılmadan erken; önerdiğiniz
  "kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir" kalıbı daha dürüst ve § 10.4 metninden iyi.

Etkisi: `rehber_kritik_onay.json` yenilenir. ZORUNLU / YASAK listelerinde "henüz yok" ifadesine bağlı bir kural varsa güncellenir;
F10l listeleri yeniden üretilir; ardından 0b–0f ve tam üretim.

## 8. Bakmadıklarım

- Tam rehber üretimi ve zincir 2–10 (F10a / d / e / f, F9b, regresyon) koşulmadı; yasak.
- FreeCAD hiç açılmadı. Etek dikiş kesitini ve kupon ↔ tam model yol eğrisini yeniden ölçmedim; JSON'daki betik ölçümüne güvendim.
- D1 ile FCStd dilimi arasındaki hacim farkının 0 olduğunu bağımsız ölçmedim. Kontrol ettiklerim: BREP köşe sınırları (dış kol,
  y sınırı), STL kesitleri ve STL hacmi.
- `m7-kuponlari.step` içindeki gövdeleri STL'yle karşılaştırmadım; yalnız gizlilik için taradım.
- Kuponların görüntüsüne ve dilimleyicide hâline bakmadım.
- Etek sol bandını yalnız köşe sınırlarıyla ve P108b kaydıyla karşılaştırdım; dilimini kesmedim.
- `--kaynak`'taki "955 → 947" sayısının önceki değeri (955) yeniden ölçülmedi.

## Tur 1 kontrolü (19.11, düzeltme turu 1 sonrası; FreeCAD koşulmadı)

**Karar: GEÇER.** Dört ORTA (O1–O4) kapandı; aşağıdaki iki not yalnız yorum / ileride dikkat, kapanışı bekletmez.

### T1. Bulgular

- **O1 kapandı.** `uygulama_metin.py` omuz anlatısını sabit metinden değil `carpisma-sonuc.json`'dan kuruyor (`OMUZ_TAMAM` = omuz
  "tamam" ve `tek_kosu` ve omuz koşusu = taban koşusu). Not ve `rapor.html`'de "omuz bölümü hariç", "eski kayıttan", "yeni kabuktan
  önce", "omuz regresyonu koşulsun" geçmiyor (0 / 0). Koşu numarası 20261119-075818 kayıtla aynı. Not ile rapor üreticiden birlikte
  çıkmış; yeni karar sorusu yalnız "`uygulama_ivme.py` yeniden koşulsun mu?" (günlük § 12.1 ile aynı).
- **Kütle kaynağı cümlesi doğru.** `uygulama-ivme.json` son commit 09.11.2026 (dosya çalışma ağacında değişmedi); ev kütlesi 26.120,6 g;
  `montaj-analiz.json` 25.835,06 + 400 = 26.235,1 g; fark 114,46 ≈ 114,5 g. Not: tarih `git log` ile okunuyor; dosya commit'siz
  değişirse cümle eski tarihi gösterir (bugün sorun değil).
- **O2 kapandı.** F1 ön sağ (1236) ve ön sol (1254) cümleleri günlük § 12.2 ile harfi harfine aynı; çerçeve ve omuz satırlarında (1479,
  1514, 1532) "kupon henüz yok" duruyor. Onay kaydı farkı yalnız F1 cümlesi, ZORUNLU kalıbı (1 değişti, 1 eklendi) ve iki metin
  kaydı. `F10l-birlesim.py` farkı yalnız taban `d8ade70` ve bu iki silinen / iki eklenen cümle.
- **O3 kapandı.** `etek-kuponu.json` içinde `sinir`, `deneme`, `malzeme_notu` var. Hareket sınırlı: alt parça mengene / kıskaçta, üst
  parça takoza tutturulur, "elle eğilmez, döndürülmez"; önce yalnız x, sonra yalnız −z 10 mm. "Geçti" kısıtlı hareketle kanıt,
  "geçmedi" belirsiz (K55 b ya da tam bant); kayıt yeri `test/README.md` "K55 etek ön bandı kuponu" tablosu. Baskı listesindeki
  elle yazılmış paragraf JSON ve README ile aynı (takoz, döndürülmez, ≤ 0,5 mm, üç tekrar, belirsiz, K55 b, brim).
- **Etek STL.** md5'ler JSON'la aynı (üst `aa4dd699`, alt `45c61ce3`, flanşlı `6cf9d06a`). Alt ve flanşlı STL'de z < 5 mm'de aşağı bakan
  yüz alanı 0: z 3 çıkıntısı gitti. Toplam aşağı bakan alanı kendi eşiğimle 54,3 / 103,7 mm² ölçtüm (JSON 52,5 / 100,3); fark eşik
  tanımından, yön ve büyüklük aynı.
- **O4 kapandı.** Baskı listesi ve F4c farkı yalnız beklenen yerlerde: Parti 0 CF toplamı (0,18–0,31 kg), parça + kupon 1,37–1,56 kg,
  pay 128 / −58 g, D2'siz 31–171 g, D1 41,8–90,3 g, D2 42,3–88,6 g, Parti 0 7,37–12,08 sa (D2'siz 6,17–9,56), "D / E eski" uyarısı
  silindi (`m7_uyari` boş), kupon bloğu başlığı ve iki etek satırı "toplama katılmaz" bloğunda (blok 101–161 g, 2,9 sa). Başka parça
  ya da parti satırı değişmedi; `Y2b-baski.json` ve `F4c-rapor.html` değişmedi. Sayılar ilk tur hesabımla aynı.
- **Yeni 7. denetim yakalıyor.** Depo dışı kopyada dört bozma: m7 JSON'da D1 üst kütle 90,3 → 91,0; etek JSON'da üst tahmini kütle
  3,6 → 5,0; baskı listesinde D1 hücresi 90,4; etek flanşlı hücresi 14,9. Dördünde de çıkış 1, "KALDI 7"; geri alınınca 0, GECTI.
- **Not (düşük, yorum).** `kupon_tazelik.py` 28. satır yorumu durum listesinde hâlâ "BILINEN ESKI" sayıyor; kod ve 6. / 59. satır
  istisnanın kalktığını söylüyor. Bir sonraki dokunuşta yorumdan çıkarılabilir.

### T2. Koşularım (FreeCAD'siz, depo kökünden)

| Komut | Çıkış | Sonuç |
|---|---|---|
| `carpisma_kos.py kontrol` (baş / son) | 0 / 0 | izlenen 17 dosya kayıtla aynı |
| `rehber_denetim.py --kaynak` | 0 | CAD 947, eskime HATA 0 / bilgi 2, standart HATA 0, artırma silinen 9 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 347 / 347 (17 standart / artırma bozması dahil) |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER; 114 / 114 |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER; toplam 174 |
| `F10l-birlesim.py` (varsayılan taban) | 0 | GECER; 1177 / 1177, eklenen 2 / 2, silinen 2 / 2 |
| `kupon_tazelik.py` / `--kati` / `--bozma-denemesi` | 0 / 0 / 0 | TAZE (16 denetim); 4 / 4 |
| `F4c-dogrula.py` / `--bozma-denemesi` | 0 / 0 | GECTI (1–7); 7 / 7 |
| `rehber_denetim.py` (veri) | 1 | bilinen: standart 18 (ISO 7381), tam üretimden sonra 0 beklenir |

Değişmeyenler (`git diff --quiet HEAD`): `dongu-158.md`, `karar-kuyrugu.md`, `sonuc-rapor.html`, demo, `maliyet.json`,
`Y2b-baski.json`, `F4c-rapor.html`, `rehber-veri.json`, `arayuz.py`. Koşudan önce ve sonra `git status` aynı (45 satır); kilit "boş".

### T3. Gizlilik

Kanca kalıpları (anahtar, parola, e-posta, IBAN / telefon, yerel yol, takma ad, ekip adı) çalışma ağacı farkının eklenen satırlarına ve
yeni dosyalara: 25 dosya, bulgu 0. Kanca dışı bilgi: kafa notu ve üreticisinde eklenen satırlarda kullanıcının resmî adı geçiyor; HEAD'de
aynı satırlar zaten vardı (tarih değiştiği için satır yeniden yazıldı), yeni bilgi değil.

### T4. Kapanış tarifi (§ 13)

- Sıra tam: ön sınama 0a–0h → tam üretim → betikle sınama → zincir 2–10 → gözle bakış → plan / kuyruk / demo → F9b. Veri kipi standart
  hatasının 18 → 0 inmesi hem § 13.3'te hem zincir 3'te yazılı. F1 için panel 33.3 / 33.5, PDF adım 33 (s. 54–55) ve F3 / F4'te
  "kupon henüz yok"un durması yazılı.
- Plan hücresi metninde dikey çizgi yok; "17 bozma" sayısı koşuyla aynı. Kuyruğun 1893. satırında "BİLİNEN ESKİ" bugün duruyor;
  tarif onu doğru satırla değiştiriyor.
- § 13.8 listesi (5 + 12 + 4 + 3 + 2 = 26 dosya) `git status`'taki 19 eski kir dışındaki 26 dosyayla birebir aynı; yasak liste
  kesişmiyor.

### T5. Bakmadıklarım

- Tam üretim, zincir 2–10, panel ve PDF (koşulmadı, tarife göre sonra).
- `uygulama_rapor.py`'yi yeniden koşup notun bit bit aynı çıktığını denemedim; yalnız farkı ve kaynak sayıları okudum.
- Etek kuponunun dilimleyicideki hâlini ve basılabilirliğini görmedim.
