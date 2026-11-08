# T12 · Perçin somun ve etek delikleri: ölçü ve kupon denemesi

Kâğıt T12 / 13 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

**A** Satın alınan M5 ve M3 perçin somunlarını ölçmek; modeldeki tahmini ölçülerle (delik, flanş, gövde) karşılaştırmak.
**B** Hurda alüminyum kuponda bir perçin somun takıp gerçek cıvatanın robottaki konumunda **kaç diş tuttuğunu** ve somunun delikte dönüp
dönmediğini görmek.
**C** Ana anahtar (ASW-A01) ve robota takılacak acil stop için etek plakasındaki delik çaplarını gerçek parçayla kontrol etmek.

## Neden önemli

Gövde braketleri (K1) kabuğa dışarıdan M5×18 cıvata ile, etek braketleri (K2) M3×14 cıvata ile bağlanıyor; cıvata braketteki perçin somuna
giriyor. Perçin somun ölçüleri **tahmini** (`arayuz.py:961`). Perçin somunun dişi gövdenin uç kısmında olduğu için cıvata az diş tutabilir
("kavrama ~2 diş olabilir", `Y3-kontrol.md:42-43`); bu yüzden M5 cıvata 16'dan 18 mm'ye uzatıldı ve "gerçek perçin somun ≥ 8,3 mm gövdeli
seçilmeli" denildi (`kararlar:119-122`). Ana anahtar deliği Ø30 tahmini (`arayuz.py:976-977`), acil stop deliği için "etek deliği kontrol"
notu var (`elektrik.md:62`). **Bu ölçüm braketler delinmeden ve etek basılmadan önce yapılır.**

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| M5 perçin somun: braket deliği Ø7,1 (3 mm Al), flanş Ø10 × 1,0, gövde Ø7 × 9, düz flanşlı çelik | `arayuz.py:961-962` | **Tahmini** |
| M3 perçin somun: braket deliği Ø5,1 (2 mm Al), flanş Ø7 × 0,8, gövde Ø5 × 7 | `arayuz.py:961`, `arayuz.py:964` | **Tahmini** |
| Braket kalınlığı: gövde braketi 3 mm, etek braketi 2 mm (Al) | `arayuz.py:442`, `arayuz.py:446` | Tasarım |
| Cıvatalar: M5×18 ISO 7380 (gövde), M3×14 ISO 7380 (etek) | `arayuz.py:962`, `arayuz.py:964`, `kararlar:119` | Karar 29.10 (M5) |
| Cıvata ucu braket iç yüzünden M5'te 5,3 mm, M3'te 4,3 mm içeride; gövdede 0,7 mm kalır | `kabuk-analiz.json` (satır 573, 1217) | Model kontrolü |
| Boss'taki flanş cebi: flanş çapı + 0,6 mm, flanş kalınlığı + 0,1 mm (M5: Ø10,6 × 1,1; M3: Ø7,6 × 0,9); flanş kabuğa 0,09 mm | `arayuz.py:963`, `arayuz.py:965`, `kabuk_parcalar.py:700`, `kabuk_parcalar.py:714`, `kabuk-analiz.json` (satır 593, 1237) | Model |
| Gerçek M5 perçin somun gövdesi ≥ 8,3 mm olmalı | `kararlar:121-122` | Karar notu |
| Adet: M5 8, M3 6; siparişte perçin somun 16 (2 yedek) | `Y3-kontrol.md:60`, `Y3-kontrol.md:63` | BOM + pay |
| Ana anahtar deliği Ø30 (ASW-A01 çizimi yok); delikten H1 kapağına 8,4 mm, düğme zarfı Ø40'tan 3,4 mm | `arayuz.py:976-977`, `Y3-kontrol.md:40-41` | **Tahmini**; boşluklar 1,65 m modelinde ölçüldü |
| Acil stop deliği Ø22,4 (CAD: Emas B200E60); alınan NP2 BE102, "etek deliği kontrol" | `arayuz.py:436`, `elektrik.md:62` | Kontrol edilmedi |
| Robota takılacak acil stop parçası: iki kaynak farklı parça söylüyor | `elektrik.md:62` "NP2 BE102"; `arayuz.py:660` "Elde B200E-E (40 mm mantar)" | **Çelişki**, tasarım ajanına; C'de takılacak parça işaretlenir |
| Acil stop mantarı basılınca kilitlenir (basılı kalır), çevirerek ya da çekerek bırakılır | Kaynak yok; CAD mantar zarfı Ø60 (`arayuz.py:660`) | **Varsayım, doğrulanmadı** (takılacak mantarın kilitlenmeyen, yaylı tip olup olmadığı bilinmiyor) |

**Bu kâğıtta türetilen değerler (hesap):**
- Cıvata başının altından braketin flanş tarafındaki yüzüne kadar olan boy (kabuk + boss): M5'te 18 − (3 + 5,3) = **9,7 mm**, M3'te
  14 − (2 + 4,3) = **7,7 mm**. Kupon denemesinde bu boy, flanşın üstüne konan pullarla taklit edilir: pul yığını **H = 9,7 − flanş kalınlığı**
  (M5), **H = 7,7 − flanş kalınlığı** (M3).
- Gövde boyu alt sınırı = braket + cıvata ucunun geçişi: M5 3 + 5,3 = **8,3 mm** (`kararlar:121` ile aynı), M3 2 + 4,3 = **6,3 mm**.
- Ana anahtar: delik büyürse H1 kapağına kalan et 8,4 − (d − 30) ÷ 2; en az 3 mm et (varsayım) için **d ≤ 40,8 mm**. Plakanın üstünde kalan
  düğme kısmı H1 kapağına binmemeli: dış çap ≤ 40 + 2 × 3,4 = **46,8 mm**.

## Gereken alet

- Kumpas (0,02 mm; derinlik çubuklu)
- **Perçin somun pensesi** M3–M6 (siparişte var, `adim5/maliyet_duzelt.py:235`)
- Hurda alüminyum lama: **3 mm** (M5 kuponu) ve **2 mm** (M3 kuponu), her biri ~40 × 60 mm
- Sütunlu ya da el matkabı, **Ø7,1** ve **Ø5,1** matkap uçları (modeldeki delik), havşa ya da çapak alma aleti, **eğe**, mengene (matkap tablasına ya da tezgâha cıvata veya işkenceyle sabitlenir), punta
- Bir M5×18 ve bir M3×14 ISO 7380 cıvata (siparişten), uygun alyan (M5: 3 mm, M3: 2 mm), M5 ve M3 düz pullar (H yüksekliğine yetecek kadar)
- Bir M5 + bir M3 perçin somun (siparişteki 2 yedekten), satın alınan ASW-A01 ve acil stop mantarı (C için)
- Koruyucu gözlük

## Güvenlik

- **Kupon kenarları:** kesilmiş lamanın kenar ve köşeleri delmeden önce **eğeyle yuvarlatılır** (çapaklı köşe eli keser).
- **Matkap:** koruyucu gözlük takılır; kupon **mengeneye** sıkılır, elle tutulmaz (matkap ucu takılınca kupon döner, eli keser). Mengene
  de matkap tablasına ya da tezgâha cıvata veya işkenceyle **sabitlenir**; serbest mengene uçla birlikte döner.
  **Matkap kullanırken eldiven takılmaz** (dönen uca dolanır); uzun saç toplanır, bol kol sıvanır.
- Delik çapakları keskindir: çapak alma aletiyle temizle, çıplak parmakla sıyırma.
- Perçin somun pensesinin kolları arasına parmak girmez; pense kapanırken kupon masada sabit.
- Bölüm C'deki parçalar **yeni, kablosuz** olmalı. ASW-A01 ya da acil stop robotta takılı ve kabloluysa önce akünün XT60'ını ayır, ana 30 A
  sigortayı çıkar.
- Saat, yüzük, bileklik çıkar.

## Yöntem

**A. Ölçüler (perçin somun takılmadan)**

1. Paketteki üretici bilgisini yaz: önerilen delik çapı, **kavrama aralığı** (perçinlenebilecek sac kalınlığı aralığı), açık uçlu mu kapalı uçlu mu.
   Bilgi yoksa "yok" yaz.
2. Kumpasla her türden (M5, M3) ölç: flanş çapı, flanş kalınlığı, gövde dış çapı, gövde boyu (flanşın altından gövde ucuna).

**B. Kupon denemesi**

3. Kuponu mengeneye sık, punta vur, **modeldeki çapla** del: 3 mm kupona Ø7,1, 2 mm kupona Ø5,1. Deliği kumpasla ölç, yaz. Çapağı al.
4. Perçin somunu deliğe flanş yukarıda olacak biçimde tak. Gövde deliğe elle girmeli; zorla girmiyorsa ya da delikte belirgin boşluklu
   oynuyorsa yaz. Pense ile perçinle (pensenin talimatına göre). Flanş kupona düz oturdu mu bak.
5. Kuponun arkasından perçin somun gövdesinin çıkıntısını ölç (takılmış gövde boyu).
6. **Kavrama denemesi:** flanşın üstüne düz pulları üst üste koy; pul yığınının yüksekliği **H** (türetilen değerler) kadar olsun, kumpasla
   ölç (± 0,2 mm yeterli; varsayım). Cıvatayı pulların içinden geçirip alyanla elle, başı pullara oturana kadar tak; aşırı sıkma.
   Cıvata başı pullara oturmadan durursa (kapalı uçlu somunda dibe vurma) yaz.
7. Başı oturduktan sonra alyanla bir kez daha sık (elle, sıkı): **perçin somun delikte döndü mü?**
8. Cıvatayı **tur sayarak** gevşet: cıvata somundan kurtulana (serbest dönene) kadar kaç tam tur döndü? Kavrama boyu = tur × diş adımı
   (M5: 0,8 mm, M3: 0,5 mm; ISO kaba diş, dış kaynak).

**C. Etek delikleri**

Robota takılacak acil stop: ☐ NP2 BE102 (`elektrik.md:62`) ☐ Emas B200E-E, 40 mm mantar, elde (`arayuz.py:660`) ☐ başka: ______
(Kaynaklar farklı parça söylüyor. Adım 10 ve C ölçütleri **işaretlenen parçaya** uygulanır; iki parça da eldeyse ikisi ölçülür,
Tablo 4'e ayrı satır yazılır.)

9. **ASW-A01 ana anahtar:** bağlantı biçimini yaz (ortada somunlu gövde mi, vidalı flanş mı). Etek plakasından **geçecek** kısmın en büyük çapını
   ve plakanın **üstünde kalan** kısmın (düğme/kapak) en büyük çapını ölç. Üretici panel deliği yazıyorsa onu da yaz. Bağlanabileceği plaka
   kalınlığı aralığını (somunun ne kadar kalın plakayı sıkabildiğini) not et.
10. **Acil stop (yukarıda işaretlenen parça):** dişli gövdenin dış çapını, varsa dönme kilidi tırnağının ölçüsünü ve mantar çapını ölç; üretici panel deliğini yaz.
    Mantara bir kez bas: **basılı kalıyor mu** (kilitlenir), yoksa bırakınca geri mi geliyor (yaylı)? Kilitleniyorsa nasıl bırakılıyor
    (çevirerek / çekerek) yaz. Parça kablosuz ve masada; bu yalnız mekanik kontroldür.

## Kayıt tablosu

Üretici bilgisi: M5 önerilen delik ______ mm, kavrama aralığı ______ mm, ☐ açık uçlu ☐ kapalı uçlu;
M3 önerilen delik ______ mm, kavrama aralığı ______ mm, ☐ açık uçlu ☐ kapalı uçlu

Tablo 1: M5 perçin somun (gövde braketi K1)

| Ölçü | Model (tahmini) | GEÇER sınırı | Ölçülen |
|---|---|---|---|
| Flanş çapı (mm) | 10,0 | ≤ 10,6 (cep çapı) | |
| Flanş kalınlığı (mm) | 1,0 | ≤ 1,1 (cep derinliği) | |
| Gövde dış çapı (mm) | 7,0 | deliğe elle girer, Ø7,1 | |
| Gövde boyu, takılmadan (mm) | 9,0 | ≥ 8,3 | |
| Kavrama aralığı 3,0 mm'yi içeriyor mu | — | evet | ☐ evet ☐ hayır ☐ bilgi yok |

Tablo 2: M3 perçin somun (etek braketi K2)

| Ölçü | Model (tahmini) | GEÇER sınırı | Ölçülen |
|---|---|---|---|
| Flanş çapı (mm) | 7,0 | ≤ 7,6 (cep çapı) | |
| Flanş kalınlığı (mm) | 0,8 | ≤ 0,9 (cep derinliği) | |
| Gövde dış çapı (mm) | 5,0 | deliğe elle girer, Ø5,1 | |
| Gövde boyu, takılmadan (mm) | 7,0 | ≥ 6,3 | |
| Kavrama aralığı 2,0 mm'yi içeriyor mu | — | evet | ☐ evet ☐ hayır ☐ bilgi yok |

Tablo 3: kupon denemesi

| Kupon | Delik, ölçülen (mm) | Pul yığını H (mm) | Kavrama: tur / mm | Somun döndü mü |
|---|---|---|---|---|
| M5 (3 mm Al) | | | ______ tur / ______ mm | ☐ hayır ☐ evet |
| M3 (2 mm Al) | | | ______ tur / ______ mm | ☐ hayır ☐ evet |

Takılmış gövde çıkıntısı (kupon arkası): M5 ______ mm, M3 ______ mm   Flanş düz oturdu: M5 ☐ M3 ☐   Cıvata dibe vurdu: M5 ☐ M3 ☐

Tablo 4: etek delikleri

| Parça | Plakadan geçen kısım, en büyük Ø (mm) | Üstte kalan kısım, en büyük Ø (mm) | Üretici panel deliği (mm) | Bağlantı biçimi / plaka kalınlığı aralığı |
|---|---|---|---|---|
| ASW-A01 ana anahtar (model delik Ø30) | | | | |
| Acil stop, takılacak parça: ______ (model delik Ø22,4) | | | | |

Acil stop: dönme kilidi tırnağı ☐ yok ☐ var (______ mm)   Basınca ☐ kilitlenir ☐ kilitlenmez (yaylı)   Bırakma ☐ çevirerek ☐ çekerek
Mantar Ø ______ mm (CAD zarfı Ø60, `arayuz.py:660`)

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| Flanş çapı / kalınlığı | M5 **≤ 10,6 / ≤ 1,1 mm**, M3 **≤ 7,6 / ≤ 0,9 mm** | `arayuz.py:963`, `arayuz.py:965`, `kabuk_parcalar.py:700`, `kabuk_parcalar.py:714` |
| Gövde boyu (takılmadan) | M5 **≥ 8,3 mm**, M3 **≥ 6,3 mm** | `kararlar:121-122`; M3 aynı hesapla (`kabuk-analiz.json` satır 1217) |
| Kavrama aralığı | M5 **3,0 mm**'yi, M3 **2,0 mm**'yi içerir | `arayuz.py:442`, `arayuz.py:446` |
| Delik: gövde Ø7,1 / Ø5,1 deliğe elle girer, somun perçinlendikten ve cıvata sıkıldıktan sonra **dönmez** | dönme **0** | Model deliği `arayuz.py:962`, `arayuz.py:964` |
| Kavrama (adım 8) | **≥ 5 tam tur** (M5 ≥ 4,0 mm, M3 ≥ 2,5 mm) | **Varsayım:** standart somun yüksekliği ≈ 0,8 × çap (dış kaynak, depoda yok) |
| Cıvata başı pullara oturdu (dibe vurmadı) | **evet** | Bu kâğıdın yöntemi |
| Ana anahtar: geçen kısım + 1 mm (varsayım: geçiş payı) | **≤ 30,0 mm** GEÇER; 30–40,8 mm KOŞULLU; > 40,8 KALIR | `arayuz.py:977`; 40,8 türetilen (3 mm et varsayımıyla) |
| Ana anahtar: üstte kalan kısım | **≤ 46,8 mm** | Türetilen, `Y3-kontrol.md:40-41` |
| Acil stop: dişli gövde + 0,1 mm (varsayım: geçiş payı) | **≤ 22,4 mm** | `arayuz.py:436` |
| Delik alt sınırı (ana anahtar ve acil stop): model deliği aşırı büyük olmasın | Üretici panel deliği varsa model deliği onun **±0,3 mm** içinde; yoksa somunun / flanşın dış çapı **≥ delik + 4 mm**; değilse **KOŞULLU** | **Varsayım** (sıkma somunu deliği örtmeli) |
| Acil stop: dönme kilidi tırnağı | **yok** (varsa delikte kama yuvası gerekir → **KOŞULLU**) | Bu kâğıdın yöntemi |
| Acil stop: basınca kilitlenir | **evet** (kilitlenmezse **KOŞULLU**) | **Varsayım, doğrulanmadı**; [T4](T4-pam8403-ses-karti.md) adım 5 ve [00-genel.md](00-genel.md) kural 1 bunu kullanır |

Gövde boyu sınırı tutmasa da kavrama ≥ 5 tur ise kabul edilebilir (kavrama asıl ölçüttür); bu durumda sonuç **KOŞULLU** yazılır.

## Sınır aşılırsa

- **Flanş cebe sığmıyor, delik uymuyor ya da gövde/kavrama yetmiyor:** ölçüler tasarım ajanına; `arayuz.py:961-965` (`govde_braket_m5`,
  `etek_braket_m3`) gerçek değerlerle güncellenir, kabuk ve ana montaj yeniden koşulur. **Braketler bu sonuçtan önce delinmez.**
- **Kavrama < 5 tur:** kaynaktaki çözüm cıvatayı uzatmak (M5×16 → M5×18 kararı böyle verildi, `kararlar:119-122`); bir boy daha uzun cıvata
  (M5×20, M3×16) ya da daha uzun gövdeli perçin somun seçilir; uzayan ucun başka parçaya değmediği tasarım ajanında kontrol edilir; karar
  **Ahmet Yorulmaz**'da.
- **Somun delikte döndü:** üreticinin önerdiği delik çapıyla yeni kupon (ek perçin somun gerekir); sonuç tasarım ajanına. Siparişte yalnız
  2 yedek var (`Y3-kontrol.md:63`) ve kupon denemesi ikisini de harcar: siparişe ek perçin somun (M5 ve M3'ten en az 2'şer; varsayım)
  eklenmesi tasarım ajanına önerilir.
- **Acil stop parçası çelişkisi (her sonuçta):** işaretlenen parça adı ve ölçüleri tasarım ajanına; `elektrik.md:62` ya da `arayuz.py:660`
  takılacak parçaya göre düzeltilir.
- **Ana anahtar / acil stop deliği uymuyor:** ölçüler tasarım ajanına (`arayuz.py:976-977` `ana_anahtar_delik_d`, `arayuz.py:436` `ACIL_STOP`);
  KALIR çıkarsa H1 kapağı yakınlığı yeniden çizilir, karar Ahmet Yorulmaz'da. **Etek bu sonuçtan önce basılmaz.**
- **Delik alt sınırı tutmuyor ya da dönme kilidi tırnağı var:** KOŞULLU; delik çapı ve kama yuvası ölçüleriyle tasarım ajanına (`arayuz.py:436`).
- **Acil stop kilitlenmiyor (yaylı):** KOŞULLU; tasarım ajanına ve Ahmet Yorulmaz'a (kilitlenen mantar gerekir mi). O zamana kadar
  mantarı basılı tutması gereken testlerde ([T4](T4-pam8403-ses-karti.md) adım 5) ayrı bir kişi basılı tutar.
- Her sonuçta: `Y3-kontrol.md:113-115`'teki açık ("K7 delik çapı ve perçin somun ölçüleri tahmini") bu ölçümle kapanır;
  `karar-kuyrugu.md` "karar değil, iş" listesine (satır 298) sonuç yazılır.

## Sonuç

A ☐ GEÇER ☐ KOŞULLU ☐ KALIR   B ☐ GEÇER ☐ KOŞULLU ☐ KALIR (M5 ______ tur, M3 ______ tur)   C ☐ GEÇER ☐ KOŞULLU ☐ KALIR

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
