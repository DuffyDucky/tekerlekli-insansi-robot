# F10f üçüncü bağımsız bakış (düzeltme turu 2'nin kontrolü), 13.11.2026

Kontrolcü: ayrı ajan (B3). Ajanın günlüğündeki "§ Düzeltme turu 2" bölümünü iddia olarak okudum; aşağıdaki sayılar kendi ölçümüm.
Geçici dosyalar ve betikler scratchpad `f10f-b3/` içinde. Depoda yazdığım tek dosya bu rapor. Üretici, depodaki doğrulama betikleri
ve FreeCAD koşulmadı. Rehber `rehber/index.html` üzerinden başsız tarayıcıyla, salt okuma açıldı. Kaynak modülleri kendi betiğimden
içe aktarıldı (`-B`, `__pycache__` yazılmadı). Önceki kontrolün (B2) betikleri yalnız kopyalanarak kullanıldı.

## 1. Hüküm

**GEÇER.** Kabul ölçütlerinin hepsi kendi ölçümümle tutuyor. Bir ölçüt sınırda: kablo karelerinde zor 4 / 14 çıktı, hedef ≤ 4.
Paketi durduran bulgu yok. Açık kalanlar commit'e kayıtlı açık iş olarak girebilir (bölüm 3).

En önemli bulgular:
1. **625ZZ (44.1) kapandı.** Rulman çatalla birlikte +y uçuyor. Nokta–üçgen ölçümüyle de rehberin ışın ölçümüyle de tek engel horn
   merkez vidası (K1-b). Kör nokta kapandı:
   - rehberin kendi `ucus_yolu` fonksiyonu eski yönü yakalıyor (8,67 mm), eski kural yakalamıyor;
   - iki ayrı bilerek bozma da yakalandı (kol adımı 41.6, kol dışı 49.3).
2. **Bağımsız tam tarama.** 329 uçuş satırında (birim satırları hariç) her satırın temiz / değil sonucu `kontrol.json` ile birebir
   aynı. Duruşta örtüşen çifti olan satır yalnız 8. Yeni kuralın eklediği tek satır 31.6 kamera. "Kol dışında 1 ölçüm kaydı"
   inandırıcı.
3. **Patlatmada ön kollar artık çiziliyor.** Değişen 9 konumun hepsine iki temada tam boy baktım; bozulma görmedim. Takılı
   görünümde ve bütün satırlar takıldıktan sonra ekran farkı 0.
4. **Kablo kareleri: zor 4 / 14, ajanın iddiası 2.** Fark 48.2 / 48.3'ten geliyor. İki ek ayrı işaretli ama tek çizgi üstünde hâlâ
   seri okunuyor. Anlaşılmayan kare 0.
5. **Kural dışı bir değişiklik var, kim yaptığı bilinmiyor.** Depo kökündeki boş, izlenmeyen `rehber_metin.py` artık yok (B2
   12.11 22:43'te görmüştü). Günlükte ya da döngü kaydında silindiğine dair satır yok. Paketin içeriğini etkilemiyor; Ahmet'e
   bildirilmeli.

## 2. İkinci kontrolün bulguları

| # | Bulgu | Durum | Ölçümüm, kanıt |
| --- | --- | --- | --- |
| 3.1 | 625ZZ uçuşu yuvadan geçiyor (44.1), duruş kör noktası | **kapandı** | Ayrıntı aşağıda (3.1a–d). |
| 3.2 | 42 / 42.1 patlatmada iki ön kol gizli | **kapandı** | Ayrıntı aşağıda (3.2). |
| 3.3 | Okunurluk zor 5 / 14 | **kapandı (sınırda)** | Zor 4 / 14, anlaşılmıyor 0 (bölüm 5). 41.3 açık temada kenar artık siyah, okunuyor. 41.4 / 41.5'te tambur ve kaset kenarı çizili, iki kare kıyaslanıyor. 48.2 / 48.3 hâlâ zor. Şema görünürlüğü korunuyor (bölüm 5). |
| 3.4 | 40.2 / 41.2 S2 uzatma ucunun yeri | **kapandı** | 40.2: "S2 uzatması G2'de göbekte eklendi". 41.2: "S2 uzatması G2'de göbekte S2 servo kablosuna ekli". Kaynak adım 39 madde 1 (göbek arka iç şeridinde ek) ile tutuyor. 40.2'de "burada … G2'de" tekrarı var; anlamı bozmuyor. |
| 3.5 | F4'te iç terim | **kapandı** | 36. adım madde 2: "Elle ulaşılabilirlik ölçüldü (bantlar takılıyken) … elin 0,5–23 mm yakınına kadar engelsiz düz yol var". Okur dilinde. Okur verisinde "el zarfı" geçmiyor. "sıra denetimi" 30 ve 31. adımda geçiyor; bunlar F10d'den kalma, bu turun değil. |
| 3.6 | M8 (eski tür dize anahtar) | **kapandı (istenen kapsamda)** | Ayrıntı aşağıda (3.6). |
| 3.6 | T4 / T9 metin denetimi | **kapandı** | Ayrıntı aşağıda (3.6). |
| 3.6 | "L 171,4 mm (−5…0)" birimi | **kapandı** | Metin artık "L 171,4 mm (−5…0 mm)" (41.2 / 41.3 verisi). |
| 3.7 | Adım 0, 47 / 58 px fark | **kapandı, açıklama tarayıcıda doğrulandı** | Ayrıntı aşağıda (3.7). |
| §4 | PDF kare içi lejant ≈ 2,5 pt | **kapandı** | Ayrıntı aşağıda (§4). |
| devir a | gizli parçalar | kapsam dışı (ayrı iş) | Yeniden ölçülmedi. `F10f-dogrula.json` `parca_kare.gecti` = null (bilgi amaçlı, önceki turla aynı tasarım). |

### 3.1 625ZZ uçuşu (44.1)

**(a) Yeni veride uçuş.**
- p0571 / p0583 ev sahibi p0562 (sağ dirsek çatalı), p0628 / p0640 ev sahibi p0619. Hepsi +y, d 63,5; çatalla birlikte uçuyor.
- **Nokta–üçgen ölçümü** (B2'nin `geo_ucus` betiği kopyalandı, 1 mm adım, 48 engel):
  - p0562 + p0571 + p0583: eşik üstü tek engel p0573 horn merkez vidası, 3,0 mm. Duruşta p0572 0,0.
  - Sol ayna aynı: p0630, 3,0 mm.
  - Grup yuva omzundan geçmiyor, başka bir şeye girmiyor. Horn vidası K1-b karar kalemi.
- **Rehberin ışın ölçümü** (`b3_tara`): duruş çifti yok; p0562 > p0573 5,46 mm. Bu, K1-b dar izni (5,96) içinde.

**(b) Denetim kodu ve bilerek bozma.**
- Kod: `rehber_giris._dinlenme_suz`. Çift artık dışarıda bırakılmıyor; eşik = duruş derinliği + `DINLENME_PAY` (0,5 mm, h ile aynı).
  `rehber_sira._yol` iki geçişte de (ilk çarpma ve `tum`) payı veriyor.
- **İki ölçünün farkı** (`b3_profil`, eski yön, sağ):
  - Duruşta x ekseni ışınları (rulman ekseni) 0,06 mm'lik sıkı geçme halkasından 2 ışınla geçiyor. Ortak boy 5,0 mm, yani bilezik
    genişliği. Bu bir "derinlik" değil, eksen boyunca örtüşme boyu.
  - Uçuşta y / z ışınları omuzdaki mercek kesitinin kirişini ölçüyor: 8,49 / 8,67 mm (t 0,5–10 mm, t 12'de 0).
  - B2'nin 1,55 mm'si yüzeye dik batma (nokta–üçgen).
  - Denetim 8,67 > 5,0 + 0,5 ile yakalıyor. Kiriş ≈ 2√(2Rδ), R ≈ 8 mm. Buna göre bu çiftte yaklaşık δ > 0,47 mm'lik radyal batma
    yakalanır; 0,06 mm geçme geçer. Pay makul.
- **Kalıntı zayıflık:** eşik çiftin duruştaki en uzun ışın örtüşmesine bağlı. Duruşta uzun örtüşen çiftlerde kör alan büyüyor.
  Örnek: 40.1'de kol çatalı ↔ omuz göbeği duruşta 29,0 mm. Bu çiftte kirişi 29,5 mm'den kısa batma görünmez. Nokta–üçgen ölçümü
  bu çiftte uçuşta artış göstermedi (duruş 2,5, eşik üstü yok). Sahte alarm riski düşük: duruşta ışın halkayı kaçırırsa çift yeni
  sayılır ve her > 0,2 mm örtüşme raporlanır, yani hata güvenli yönde.
- **Bilerek bozma** (`b3_mut`; rehberin kendi `Denetim.ucus_yolu`'su, veri kopyası):

  | Deneme | Ne bozuldu | Yeni kural (pay 0,5) | Eski kural |
  | --- | --- | --- | --- |
  | m1 | 44.1 tur 1 yönü (dış bilezik sağ −x / sol +x, d 40) | çarpışan 2: p0571 → p0562 8,67, p0628 → p0619 8,67; `gecti` False | çarpışan 0 |
  | Kol adımı | 41.6 p0233 kaset kapağı −z (duruş ortağı p0127 9,55) | p0127 34,15 çarpan listesinde | p0127 listede yok |
  | Kol dışı | 49.3 p0217 arka servis kapağı +z (duruş ortağı p0211 1,5) | p0211 91,59 listede | p0211 yok |
  | m2 | 40.1 dış bilezik tur 1'deki gibi ayrı uçar | çarpışan 2 (p0121 9,27, p0118 8,44, p0117 7,97, p0116 6,42) | çarpışan 2, çatal yok |

  `F10f-dogrula.json` `sinama.dinlenme.gecti` true ve aynı sayıları veriyor.

**(c) Bütün rehber.**
- Uçuş denetimi yalnız alt adımı olan adımlarda koşuyor: 21, 31, 33–36, 40–46, 48, 49. Bu, F10d'den beri böyle; "bütün rehber"
  bu kapsam demek.
- Bağımsız tarama (`b3_tara`): her satır tek süpürme, filtre uygulanmadan çift başına en büyük ışın derinliği ve duruş derinliği;
  iki kural dışarıda uygulandı. 329 satır (7 masa birimi satırı hariç).
  - Temiz / değil sonucu `kontrol.json` ile **329 / 329 aynı**.
  - Duruş çifti olan satır 8: 31.6 p0798, 41.6 p0233 / p0235, 49.3 p0217, 40.1 p0121 / p0194 / p0127 / p0200.
  - Eski → yeni kuralda ek çarpışan satır **1**: 31.6 p0798 → p0750, duruş 3,91, uçuş 7,95.
- `kontrol.json`: satır 336, çarpışan 0, istisna 20, `istisna_bos` 0, ölçüm kaydı 1, `gecti` true.
  - Sınıflar: dize 9 (hepsi kol dışı: 33.3–5, 35.1–3 × 2, 35.5 × 2), karar 4, duruş 4, yol 2, ölçüm kaydı 1.
  - Kol adımlarında 10 istisna: 36.1–2 yol, 40.1 karar × 2, 41.6 duruş × 4, 44.1 karar × 2. Kol adımında dize anahtar 0.
  - Ajanın dağılımıyla aynı. Yeni istisnaların (36.1 / 36.2 "yol", 31.6 "ölçüm kaydı") hepsi dar (parça id + engel + derinlik),
    sınıfı yazılı.
- Ölçüm kaydı listesi günlükte ve `kontrol.json`'da aynı: 1 satır (bölüm 4).

**(d) Kaynak ve atama.**
- `dirsek_rapor.py` SIRA 2: "625ZZ'yi çatal iç kolunun Ø16 yuvasına, dudağa dayanana kadar bastır". Ön kol çatala SIRA 6'da
  giriyor. 44.1 metni ("önce … bastır, tezgâhta; rulman çatalla birlikte gelir") kaynakla tutuyor.
- Parça ↔ adım ataması HEAD ile aynı: 1192 parça, `a` / `b` farkı 0, satır üyeliği farkı 0, birden fazla adımda parça 0. Alt adım 71.
- Tur 1 verisine göre (`f10f-d2/t1r` kopyası) uçuşu değişen parça yalnız 6: p0122, p0195, p0571, p0583, p0628, p0640. Hepsinde
  değişen yalnız u / d / h.

**40.1 (brief dışı değişiklik).**
- Kaynak `omuz_rapor.py` SIRA 2: "625ZZ'yi çatalın arka koluna bastır". Metindeki "tezgâhta önceden bastırılır, çatalla birlikte
  gelir" dış bilezik için kaynakla tutuyor.
- Nokta–üçgen ölçümü (p0121 + p0122 + pim / ısıl gömme, +x, d 56,9): eşik üstü yalnız p0116 1,67 ve p0118 2,48 mm. Bunlar B2'nin
  K1-a ölçümüyle aynı; rulman eklenince yeni engel çıkmadı.
- Işın ölçümünde dış bilezik p0122'nin p0116 / p0118 çarpması (6,42 / 5,0) çatalın K1-a dar izni (6,92 / 5,5) içinde kalıyor.
  İzin engel id'sine bağlı; hangi hareketli parçanın çarptığını ayırmıyor.
- Karede okur (40.1 patlatma, iki tema) çatalı ve yuvasındaki bileziği görüyor. İç bilezik + pul + cıvata 39'dan göbekte duruyor.
- **Tutarsızlık** (bölüm 3, Y1): 39. adım metni hâlâ "Karşı tarafa 625ZZ ve M5 pim" diyor. 40.1 ise rulmanın dış bileziğinin
  çatala önceden bastırıldığını söylüyor. Rehber şimdi K1-a seçenek C'nin yarısında. K1-a notu (günlük) bunu "C'nin rulman kısmı"
  diye yazıyor ama 39 metniyle çelişkiyi yazmıyor.

### 3.2 Patlatmada d ≤ 0 parçalar

- **Ölçüm yöntemi:** depo ↔ yalnız `x.yerinde = false` yapılmış kopya (scratchpad). `?patlat=1&isaret=0`, 1400 × 900, Σ|ΔRGB| > 24,
  tuval.

| Konum | 4 | 12 | 14 | 19 | 23 | 29 | 37 | 42 | 42.1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Açık px | 210 828 | 95 252 | 138 699 | 46 033 | 68 925 | 105 625 | 11 028 | 50 971 | 50 971 |
| Koyu px | 210 727 | 95 110 | 138 708 | 45 950 | 68 997 | 105 499 | 11 028 | 50 971 | 50 971 |

- Ajanın pf2 sayılarıyla uyuşuyor. Kalan 111 konumu yeniden saymadım (bkz. ölçemediklerim).
- **Kendi gözüm (9 konum, iki tema, tam boy):**
  - 42 ve 42.1'de iki ön kol yerinde, saydam mavi. Servolar ve somunlar artık bir parçaya göre konumlanıyor. B2 3.2 kapandı.
  - 4: plaka saydam; 20 burç ve akü takozu plakanın içinden görünüyor.
  - 29: kart saydam; alttan gelen cıvatalar görünüyor.
  - 12, 14, 19, 23, 37: taban / gövde saydam, parçalar referanslı.
  - Üst üste binme, vurgu kaybı ya da yanlış yerde çizim görmedim.
- **Saydamlığın yan etkisi:**
  - Yerinde çizilen parça gri "önceki" ile karışmıyor: kendi CAD renginde, 0,35 saydamlıkta.
  - 4, 29, 42.1'de bu parçanın kenarı pembe, yani "Bağlandığı yer" (öbür parçalar ona bağlanıyor). Anlam doğru; "şimdi takılan" ile
    "bağlandığı yer" aynı parçada birleşiyor, okur lejantla ayırıyor.
- **Patlatma dışı görünüm değişmedi:** 9 konum × 2 tema takılı görünüm depo ↔ kopya **0 px**. `?patlat=1&tak=40` (bütün satırlar
  takılı) 4, 29, 42.1 × 2 tema **0 px**; plaka ve ön kol takılınca opak.
- **Kod:** `taban()` her `siraKonum`'da `mat1`'den geri yükleniyor; saydamlık yalnız `!takili && x.yerinde`.
- **Ayna düzeltmesi korunuyor:** 4 / 12 / 42 vb. dışındaki kol adımlarında veri değişmedi. Bilek / dirsek kulak cıvatası u / d / h
  tur 1 ile aynı (değişen 6 parça yalnız 625ZZ).

### 3.6 M8 ve metin denetimi

**M8 (eski tür dize anahtar).**
- Kod: kullanılmayan dize anahtar ve kol adımındaki dize anahtar `istisna_bos`'a giriyor.
- Deneme m8a: 44.1'e "625ZZ" dize anahtarı ve eski yön. Sonuç: `istisna_bos` 1, "kol adımında dize anahtar"; `gecti` False.
  Eski kuralla "kullanılmayan dize anahtar"; yine False.
- **Kalıntı:** kol dışındaki 9 dize anahtar kullanıldığı sürece satırı hangi engel ve derinlik olursa olsun susturuyor. Bu turda
  bunun gizlediği yeni satır yok: tarama eski ↔ yeni farkını yalnız 31.6'da buldu, o da dar anahtara çevrildi.

**T4 / T9 (`b3_metin`, rehberin `metin_denetle`'si, veri kopyası).**

| Deneme | Sonuç |
| --- | --- |
| 41.4 iç ↔ dış takası | etiket_hata 2 |
| 41.5 takası | etiket_hata 2 |
| "125,3 m" | birim_hata 1 |
| "74,9 rad" | birim_hata 1 |
| "74,9° (74,9 mm)" | birim_hata 1 |
| "(−5…0 cm)" | birim_hata 1 |
| "171,4 cm" | birim_hata 1 |

Yakalanmayanlar (düşük):
- Toleransın birimsiz yazımı "(−5…0)": eksik 0, birim 0. Günlükteki "eski metinde 1 eksik" iddiasıyla uyuşmuyor.
- 41.4 ↔ 41.5 arası ψ ≈ 225 / 290 takası.

### 3.7 Adım 0

`b3_adim0`, iki tema, ilk F10f kontrolünün (tur 0) karesi ↔ şimdi:

| Çekim | Tur 0 ile fark (açık / koyu) | Not |
| --- | --- | --- |
| Olduğu gibi | 47 / 58 px | kutu x 324–468, y 237–282 |
| Uzatma şemaları (16) tur 0 rengine (#0d8f6f) çevrilince | 4 / 12 px | kalan küçük fark başka bir şema renginden |
| Kol kablo şemaları gizlenince | fark kaybolmuyor, büyüyor (64 / 78) | şemalar tur 0'da da vardı |

- Ajanın açıklaması (uzatma rengi değişikliği, gövde boşluğundan görünen şema) tarayıcıda doğrulandı. Neden `tak()` değil.
- Şimdi ↔ B2'nin tur 1 karesi: 0 / 0 px. Bu turda adım 0 değişmedi.

### §4 PDF

`b3_pdf`, PyMuPDF:
- 75 sayfa, 16 193 kB. En küçük yazı 8,1 pt. Görüntü 121, boş 0.
- 20 "Karede:" satırı, hepsi 8,1 pt, sayfa 53–72.
- Sayfa 72'ye gözle baktım: lejant karenin altında metin olarak, renk kutucuklu, okunuyor, taşma yok.
- Ajanın sayılarıyla aynı.

## 3. Yeni bulgular (bu turun getirdiği ya da açığa çıkardığı)

Önem sırasıyla:

- **Y1 (düşük-orta): 39 ↔ 40.1 rulman metni çelişiyor.**
  - 39 "Karşı tarafa 625ZZ ve M5 pim" diyor (iç bilezik 39'da göbekte). 40.1 "625ZZ'nin dış bileziği … tezgâhta önceden bastırılır,
    çatalla birlikte gelir" diyor. Gerçekte tek bir rulman var; okur onu iki yerde takıyor gibi okur.
  - Bu turdan önce de tutarsızdı: dış bilezik iç bileziğin içinden 6,4–8,9 mm geçerek ayrı uçuyordu. Yeni metin kaynağa (omuz SIRA 2)
    daha yakın.
  - **Kayıtlı açık iş:** K1-a karar kalemine bağlı (seçenek C, 39 metnini ve atamayı da değiştirir). K1-a notuna bu çelişki tek
    satırla eklenmeli. Paketi durdurmaz.
- **Y2 (düşük): 48.2 / 48.3 hâlâ zor.**
  - Ajan "anlaşılır" dedi, benim gözümle iki temada da zor. Tek tüp çizgisi üstünde uzatma → JR → uzatma parçası → lehim → servo
    sırası okur.
  - İki ek beyaz bantla iki ayrı nokta olarak seçiliyor ama tek kabloda seri duruyor. Dirsek servo kablosunun JR'den sonra nereye
    gittiği karede yok; metin anlatıyor.
  - **Kayıtlı açık iş:** sayım hedefi (≤ 4) tutuyor. Paketi durdurmaz.
- **Y3 (düşük): ışın derinliğiyle duruş eşiği iki ayrı ölçüyü karıştırıyor** (3.1b).
  - Duruşta uzun örtüşen çiftlerde kör alan kalıyor: 40.1 çatal ↔ göbek 29 mm.
  - **Kayıtlı açık iş:** bu turda bu yüzden kaçan bir çift bulmadım (nokta–üçgen ölçümü 40.1 ve 44.1'de temiz).
- **Y4 (düşük): denetimin hâlâ yakalamadıkları.** Kol dışı dize anahtarlar kullanıldığı sürece her engeli susturuyor; tolerans
  birimsiz yazım ve ψ takası yakalanmıyor (3.6). Kayıtlı açık iş.
- **Y5 (süreç, düşük): kökteki boş `rehber_metin.py` silinmiş.**
  - İzlenmeyen dosya olduğu için git izi yok. B2 raporu (22:43) "duruyor" diyor; turun brief'i "dokunma, silme yok" diyor; günlükte
    ve `dongu-158.md`'de silme kaydı yok. Kim sildiği ölçülemedi.
  - İçerik boştu ve commit'e girmeyecekti; paket içeriğini etkilemiyor. **Paketi durdurmaz;** Ahmet'e bildirilmeli.
- **Not (bulgu değil):** 41.4'te −45 tambur ucu hâlâ 31 / 41 px (açık / koyu; B2 31 / 39). p0118'in saydam çizilmesi ucun pikselini
  artırmadı. Kare, kenar çizgisi ve iz sayesinde "zor"a çıktı, anlaşılmıyor değil.

## 4. Kol dışı "ölçüm kaydı" satırları

**Sayı 1**, günlükte ve `kontrol.json` → `sira.ucus.olcum_kaydi`'nda aynı: 31.6 p0798 kamera; engel p0750 yüz kabuğu (ön) sağ
7,95 ve p0763 ısıl gömme 2,91 (ışın derinliği).

- **Doğrulama:**
  - Işın ölçümüm aynı: duruş 3,91, uçuş 7,95.
  - Nokta–üçgen ölçümü (`geo_ucus`, 1 mm adım): duruşta yüz kabuğuna 0,28 mm, uçuşta en çok 0,56 mm. Isıl gömmeye 0,56 mm.
  - Yani gerçek ama sığ: kamera −z yolunda kabuğun iç yüzünü yarım milimetre sıyırıyor. 7,95 mm kesitin kiriş boyu, batma değil.
- **Önem: düşük.** Parça katının içinden geçerek takılıyor gibi gösterilen satır değil. Mesh / baskı toleransı düzeyinde bir sürtme.
  Okuru yanıltacak ağırlıkta satır yok.
- `kontrol.json`'daki 7,95 mm sayısı okunurken "8 mm batma" sanılabilir. Ölçünün kiriş olduğu kayda bir cümleyle yazılmalı
  (açık iş).
- **Neden yalnız 1:** tarama 329 satırın yalnız 8'inde duruş çifti buldu. Yeni kural yalnız bu satırların sonucunu değiştirebilir.
  8'in 1'i eşiği aşıyor. Bir filtre satır elemiyor: kol dışında 6 adım (21, 31, 33, 34, 35, 49) tarandı ve sonuçlar `kontrol.json`
  ile birebir aynı. Brief "en az 5'ini doğrula" diyordu; liste tek satır, onu iki yöntemle doğruladım.

## 5. Kare sınıflaması

- **Yöntem:** 1400 × 900, `?adim=N.J&cekim=1`, iki tema, tam boy, kendi gözüm. Sonuç iki temanın kötüsü (B2 ölçeği).
- **Konsol:** 28 yüklemenin hepsinde hata 0, uyarı 0.

| Kare | Açık | Koyu | Sonuç | Not |
| --- | --- | --- | --- | --- |
| 36.4 | açık | açık | açık | |
| 36.5 | açık | açık | açık | |
| 40.2 | açık | açık | açık | S2 lopu menekşe, sıkı kıvrım çekincesi sürüyor (bilerek) |
| 40.3 | açık | açık | açık | aynı |
| 41.2 | açık | açık | açık | |
| 41.3 | açık | açık | açık | açık temada kenar siyah, kaset duvarı seçiliyor (B2: zor) |
| 41.4 | zor | açık | **zor** | tambur / kaset kenarı çizili, iz seçiliyor; açık temada gri üstü gri yoğun, −45 ucu 31 px |
| 41.5 | zor | açık | **zor** | aynı; U'nun kayması 41.4 ile kıyaslanıyor |
| 42.2 | açık | açık | açık | |
| 42.3 | açık | açık | açık | |
| 44.2 | açık | açık | açık | |
| 44.3 | açık | açık | açık | |
| 48.2 | zor | zor | **zor** | iki ek ayrı işaretli ama tek çizgide seri; koyuda siyah JR koyu zeminde seçiliyor |
| 48.3 | zor | zor | **zor** | aynı |

**Toplam:** zor 4 / 14, anlaşılmıyor 0. Hedef ≤ 4 tutuyor, sınırda. Günlükteki "zor 2" ile fark 48.2 / 48.3.

**Şema görünürlüğü** (B2'nin `b2_kare` yöntemi, gizle / göster, Σ|ΔRGB| > 24):
- 14 şema × 2 tema: 13, 15, 16, 20, 21, 22, 23, 28, 30, 31, 32, 40, 41, 48. Yeni ek işaretleri (`nokta_lehim`, `nokta_jr`) dahil.
- Hepsi görünür; en az 1575 px (s20 açık). Ekran = sayfanın kendi fonksiyonu, 28 / 28. Geri dönüş farkı 0.

**Kol dışı regresyon:**
- 14 adres × 2 tema, B2'nin tur 1 kareleriyle: 0, 5, 12, 17, 21.1, 25, 31.3, 31.9, 33.4, 34.7, 35.3, 46.2, 49.3, 49.4. Hepsi **0 px**.

**Konsol:**
- 121 konum × 2 tema, normal görünüm: 242 yükleme, hata 0, uyarı 0, hazır olmayan 0.
- 121 konum, patlatma, açık tema: hata 0, uyarı 0.

**Zincir ve kurallar (madde 5, 6):**
- **`.durum` dosyaları** günlükle aynı: uret1 2, kalan her koşu 0. zin2 05:28:49 başladı, 4983 s.
- **Sıra:**
  - Son kod yazımları: app.js 05:19:46, denetim 03:10, metin / sıra 02:49, giriş 22:46.
  - uret1 FreeCAD verisi 02:56'da yazıldı (PDF altbilgisi "üretim 2026-11-13 02:56"). Uçuşu belirleyen kod bundan önce yazıldı;
    denetim 03:10'da yalnız `ASCII_TAMAM`'a dokundu.
  - zin2 çıktıları: veri 05:29, kareler 05:29–05:41, PDF 05:42, `kontrol.json` 06:08, F10f 06:17, F10e 06:32, F10d 06:44,
    F10a 06:51.
  - Son veri `--veri-yok` ile üretildi. Uçuş verisi son kodla tutarlı: tam taramam `kontrol.json` ile 329 / 329 aynı.
- **`gecti` alanları:** F10a / F10d / F10e / F10f-dogrula `gecti` true. `F10e` `renk_demo` false, HEAD'deki `F10e-dogrula.json`'da
  da false; bu turdan değil.
- **8 ASCII sözcük:** hepsine, elin, ekli, kolunun, dayanana, pulla, lehimden, lehimi. Hepsi Türkçe harfsiz doğru yazım; denetim
  susturulmadı.
- **Doğrulama betikleri:** `F10f-dogrula.py` eşikleri F10d / F10e ile aynı (24 / 30 / 0,20); `gecti` altı alt sınamanın hepsini
  istiyor; gevşetme görmedim. `rehber_denetim.py` farkı yalnız `ASCII_TAMAM` satırı.
- **HEAD ile aynı (git karması):** F10a / F10d / F10e / F9b-dogrula, regresyon, carpisma_kos, `robot.glb`, `robot-glb.js`,
  `index.html`, README.
- **Korunan dosyalar:** `kabuk/gorsel/*.png` 09.11 14:28, `yerlesim-kontrol.json` 03.11 21:23. İkisi de paketten eski, commit'e
  girmemeli.
- **Turda değişen dosyalar:** 12.11 22:40 sonrası değişen dosyalar yalnız rehber betikleri, `rehber/` app.js / yazdir / veri,
  `planlama/rehber` çıktıları, F10*-dogrula, F10f-* planlama dosyaları, `FREECAD-KILIT.txt` (içerik "boş", git farkı yok) ve
  `dongu-158.md` (orkestratörün).
  - `kod/`, `karar-kuyrugu.md`, `README.md`, `rehber/vendor/`, `F10a-goruntu-*` dokunulmamış.
  - Kökteki boş dosya silinmiş (Y5).
- **Kural taraması:** bu turda yazılan dosyalarda yerel kullanıcı klasörü yolu ve takma ad bulmadım. Kol kablo metin denetimi pin 0.

## 6. Ölçemediklerim ve nedenleri

- **Patlatma kuralının kalan 111 konumdaki sıfır farkı.** Ajanın pf1'ine dayanıyor; ben yalnız 9 değişen konumu saydım. 121
  konumda patlatma konsolu temiz.
- **Masa birimi uçuş satırları (7).** Benim taramam birim satırlarını atladı; 329 / 336.
- **Koyu temada patlatma konsolu.** Yalnız açık tema tarandı.
- **K1-a / K1-b'de alet erişimi ve kablonun elle döşenmesi.** Model ve kapsam dışı.
- **Kökteki boş dosyayı kimin, ne zaman sildiği.** İzlenmeyen dosya, iz yok.
- **Okunurluk sınıflaması tek göze dayanıyor** (benim). Bağımsız ikinci göz yok.
- **İlk kontrol bulgu 6 (demet kalınlığı) ve 36.5 iç ucu.** Bu turun kapsamı dışında, yeniden ölçülmedi.
- **FreeCAD tarafı ve üretici yeniden koşusu.** Kural gereği koşulmadı.
