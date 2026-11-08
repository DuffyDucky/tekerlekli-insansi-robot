# F8d kontrolü (P8.4 ek test kâğıtları T10–T13, T1/T4 ekleri) — bağımsız kontrol ajanı B, 08.11.2026

Brief: `planlama/d158/F8d-brief.md`. İncelenen: `testler/T10`–`T13`, T1 ve T4 ekleri (git diff), `00-genel.md`, `testler_html.py`,
`testler.html`, `F8d-gunluk.md`. Örnek alınan: `F8c-kontrol.md`. Yazılan tek dosya bu. CAD betiği koşulmadı; commit/push/silme yok.

## Genel karar

**GEÇMEZ (düzeltmeyle geçer, tek tur yeter).** Sayılar, atıflar ve HTML sağlam; T1 ve T4 ekleri doğru. Güvenlikte bir kâğıt geçmiyor:
**T13 C** (hareket hâlinde rampada acil stop), hareketli robotu durdurmak için tek bir yol kullanıyor: yazılımdaki "devreden çıkar" komutu.
Bu komutun var olduğu henüz teyit edilmedi. Komut çalışmazsa ya da telefon bağlantısı koparsa ne yapılacağı yazmıyor. Donanım
mantarına basmak için de düşme hattına girmek gerekiyor. T10 ve T12'de küçük ama zorunlu güvenlik/yöntem eksikleri var. Düzeltme 1–8
zorunlu, 9–16 önerilir.

| Kâğıt | Karar | Gerekçe (kısa) |
|---|---|---|
| 00-genel | KOŞULLU | Ortak kural 1'deki "acil stop elde" T9/T13'te karşılanamıyor (mantar robotta); kural T13 düzeltmesiyle birlikte yeniden yazılmalı (5) |
| T1 eki | **GEÇER** | 12,8 V'ta 12,0 V'a ulaşılmazsa seri ölçer zorunlu çıkarılıyor, kırmızı uç V soketine geri takılıyor, "düşük V" deneme değerlendirmeye girmiyor |
| T4 eki | **GEÇER** | Röle davranışı `elektrik.md:216/222/227` ile birebir tutuyor; K2 bobini de mantar arkasında (`elektrik.md:410-411`). Öneri 9 |
| T10 kafa ısısı | KOŞULLU | Termokupllar enerji yokken takılıyor, okuyucu alan dışında ✔; ama "kafa 12 V gerilimi" nereden, nasıl ölçülecek yazmıyor, pensin okunduğu yer de belli değil: enerji varken baş/boyun bölgesine prob uzatılmasına açık kapı (6) |
| T11 H1 açıklığı | **GEÇER** | Tezgâhta kablosuz kutu; sayılar doğru. Öneri: delik aralığına tolerans, şablonu 45 mm yükseltmek (10, 11) |
| T12 perçin + delikler | KOŞULLU | Gözlük, mengene, eldiven yasağı, delik çapağı ✔; kupon kenar çapağı ve mengenenin sabitlenmesi yok (7). Bölüm C'de alt sınır ve dönme kilidi ölçütü yok (8) |
| T13 rampada acil stop | **GEÇMEZ** | Sıra kuralı (A → B → C), iki ip düzeni ve ip boşlukları iyi; ama C'de hareketli robotun tek durdurma yolu doğrulanmamış bir yazılım komutu ve bunun yedek yolu yok (1–4) |
| HTML / betik | **GEÇER** | `--kontrol` geçti, HTML güncel; T2–T9'da yalnız sayaç değişmiş |

## 1. Güvenlik (kâğıtlar uygulama sırasıyla okundu)

**G1 (T13, GEÇMEZ): C'de durdurma yolu tek, doğrulanmamış ve yedeği yok.**
- T13 acil stopu "devreden çıkar" yazılım komutuyla, telefon kumandasından tetikliyor (`T13:57-59`). Elektrik tarafında sonuç doğru:
  GPIO12 = 0 olunca K1 bırakır (`elektrik.md:216-222`). Ama komutun var olup olmadığı Efe'ye soruluyor (`dongu-158.md:162` (2)).
  Kâğıt bunu yalnız "düz zeminde bir kez denenir" diye karşılıyor (`T13:58-59`); gecikme sınırı, kaç deneme yapılacağı ve
  komut çalışmazsa C'nin yapılıp yapılmayacağı yazmıyor.
- Telefon bağlantısı koparsa: depodaki hakem notuna göre Pi, ESP32'ye USB kalp atışını göndermeyi sürdürür. 500 ms bekçisi bunu
  görmez ve son hız komutu sürebilir (`tubitak-2209b/taslak/hakem-v9/hakem-3.md:105`). Bekçinin tanımı `yazilim-plani.md:45`, `:75`'te.
  C'de robot v hızıyla giderken hem sürüş hem acil stop aynı telsiz bağlantısından geçiyor. Bağlantı koparsa elde kalan önlem yalnız iplerdir.
- İnişte taban ipi robotu tutar (ip elde, dayanaktan geçiyor). **Çıkışta ise hiçbir şey robotu durdurmaz:** taban ipi yalnız aşağı yönde
  tutar, devrilme ipi "çekmek için kullanılmaz" (`T9:58-59`). Robot rampanın üstüne, yani dayanağa ve ipi tutan kişiye doğru gider.
- Donanım mantarı etek üst plakasında (`arayuz.py:436`). Kâğıt doğru olarak "kimse düşme hattına girmez" diyor (`T13:58`). Ama sonuç
  şu: C sırasında **düşme hattının dışından basılabilecek bir donanım kesme yolu yok.** Ortak kural 1'deki "acil stop elde" (`00-genel.md:32`)
  bu kâğıtta karşılanmıyor ve kâğıt bunu açıkça söylemiyor. Aynı açık T9'da da var: T9 "acil stopu tutan kişi alan dışında" diyor
  (`T9:61`), adım 13'te ise "aynısını acil stop düğmesiyle yap" deniyor (`T9:110`). Bu, robot rampadayken düğmeye uzanmayı gerektirir.
  T13 adım 13'ün yerine geçiyor (`T13:163`), ama T13 yapılmazsa T9:110 olduğu gibi kalıyor.
- A ve B'de bu açık sorun değil: robot durarak bekliyor. Komut çalışmazsa robot motorla yerinde kalır, taban ipi de bağlı ve boşluksuz.

**G2 (T13): C'de kişi sayısı ve görevler yazmıyor.** C'de taban ipi elde, devrilme ipi elde, kumanda (sürüş + acil stop) ve video var.
Ortak kural "en az iki kişi" (`00-genel.md:33`) bu kâğıtta yetmez: iki kişiyle biri hem ip tutup hem kumanda kullanmak zorunda kalır.

**G3 (T10): gerilim ve pens okuması.** Termokupllar enerji yokken takılıyor, teller hareketli parçalardan uzak tutturuluyor, okuyucu kafa erişim
alanı + 0,5 m'nin dışında duruyor (`T10:54-56`, `T10:67-73`). Kafa enerjiliyken kafaya el uzatılmıyor: brief'in T10 sorusu bu bakımdan **temiz**.
Açık kalan tek yer: adım 6 ve Tablo 2'de "kafa 12 V gerilimi" isteniyor (`T10:82`, `T10:121`). Ama ölçü uçlarının enerji yokken nereye
takılacağı yazmıyor. Akım pensi de gövdede, kafaya yakın bir yerde duruyor (`T10:74-75`) ve ekranının nereden okunacağı belirsiz. Gösterilen
nokta, T3'ün N1'i, kafanın içinde, P6KE18A'dan sonra (`T3:58`, `elektrik.md:300`). Öğrenci bu değeri enerji varken boyuna ya da gövdenin
üstüne prob uzatarak okuyabilir. Bu, kâğıdın kendi `T10:54` kuralıyla çelişir.

**G4 (T12): kesik kenarlar ve mengene.** Delik çapağı, gözlük, kuponun mengeneye sıkılması, eldiven yasağı ve pense uyarısı var (`T12:59-62`).
Brief'in sorduğu **kupon kenar çapağı** yok: hurda lamanın kesik kenarı ve köşeleri keskin. Mengenenin matkap tablasına ya da tezgâha
sabitlenmesi de yazmıyor; mengene sabit değilse matkap ucu takılınca mengeneyle birlikte kupon döner. Kâğıt bu tehlikeyi zaten adlandırıyor (`T12:59`).

**G5 (T4 eki, öneri):** Mantar basılıyken bara donanımla kapalı: doğru (`elektrik.md:216`; K2 bobini de aynı NC'nin arkasında, `elektrik.md:410-411`).
Mantar bırakılınca yazılım hatasında röle yeniden çekebilir: doğru (`elektrik.md:227`). Yalnız "mantarı ancak herkes alan dışındayken serbest
bırak" (`T4:70-71`) uygulanamıyor: bırakan kişinin eli robotun etek plakasındadır. Bırakmadan önce yazılım durumunda GPIO12 = 0
(devre dışı) görülmeli, bırakan kişi düğmeye arkadan uzanmalı ve hemen geri çekilmeli.

**Sorunsuz bulunanlar:** T13 sıra kuralı (A GEÇER olmadan B yok, A ve B olmadan C yok) ve robot ipe asılıyken boşluk verilmemesi
(`T13:60`). A'da taban ipi boşluksuz ve dayanağa bağlı, B'de tam 2 cm (0,15 m/s yakalama hızı). Kantar ve ipin doğrultusunda durulmuyor
(`T13:63`). Dayanak düşme hattının dışında. İndirme kuralı E3'e bağlı (`elektrik.md:223-224`). Devrilme ipi her bölümde ≤ 10 cm. T10'da
kol hatları enerji kesikken sigortasız; motor EN = 0, PWM = 0 ve takoz var; durdurma kuralı 55 °C ve 80 °C; kafa 10 dk soğumadan açılmıyor.
T11 tezgâhta ve kablosuz; robottaysa önce XT60 ayrılıp 30 A sigorta çıkarılıyor.

## 2. Sayılar (yeniden türetildi)

| Değer | Hesap | Sonuç |
|---|---|---|
| T13 alt sınır | a ≤ 2,41 ÷ 1,5 = 1,607 m/s²; d = v² ÷ (2a) = v² ÷ 3,213 m = **31,1 · v² cm** | 31 ✔ (aşağı yuvarlama %0,3 gevşek, önemsiz) |
| T13 üst sınır | a = 0,1 m/s²; d = v² ÷ 0,2 m = **500 · v² cm** | ✔ |
| Örnek v = 0,20 | 31,1 × 0,04 = 1,24 cm; 500 × 0,04 = 20 cm | ✔ (v = 0,393'te 4,8 / 77 cm) |
| 2,26 kg | 25,911 × sin 5° = 25,911 × 0,08716 = 2,258 | ✔ |
| 0,56 m/s² | 9,81 × (0,08716 − 0,03 × 0,99619) = 0,562 | ✔ (dişli kutusunun dönme ataleti yok sayılmış, üst sınır: tutucu) |
| 0,15 m/s | √(2 × 0,562 × 0,02) = 0,150 | ✔ |
| T10 50 / 55 °C | `qled-not:119`, `P-pi-kafada.md:45`, `duzeltme-plani.md:33` | ✔ |
| T10 48,2 / 50,9 °C | `qled-not:116-117` (yarıklı), 49,7 / 52,8 kapalı, fan 36,9–40,5 | ✔; artış 18,2 / 20,9 K ✔; %30 payı `P-pi-kafada.md:117` ✔ |
| T10 örnek | 44 + (30 − 22) = 52 | ✔ |
| T11 | 64 × 50 (`arayuz.py:973` x ±32, z −228…−178), 105 × 60 × 35 ve delik x ±47 → **94 mm** (`arayuz.py:655`); kutu merkezi z −203 = açıklık merkezi | ✔ |
| T12 flanş cebi | 10,0 + 0,6 = 10,6; 1,0 + 0,1 = 1,1; 7,0 + 0,6 = 7,6; 0,8 + 0,1 = 0,9 (`arayuz.py:961-965`, `kabuk_parcalar.py:700`, `:714`) | ✔ |
| T12 gövde alt sınırı | M5 3 + 5,3 = 8,3 (`kararlar:121-122` ile aynı); M3 2 + 4,3 = 6,3; 6,3 + 0,7 = 7,0 = model gövdesi | ✔ |
| T12 pul yığını | M5 18 − (3 + 5,3) = 9,7; M3 14 − (2 + 4,3) = 7,7; H = boy − flanş kalınlığı (flanş cepte) | ✔ |
| T12 ana anahtar | 8,4 − (d − 30) ÷ 2 ≥ 3 → d ≤ 40,8; 40 + 2 × 3,4 = 46,8 | ✔ |
| T12 kavrama | M5: 5 tur × 0,8 = 4,0 mm = 0,8 × 5; M3: 5 × 0,5 = 2,5 mm ≥ 0,8 × 3 = 2,4 | ✔ (dış kaynak diye işaretli) |

İki küçük not:
- `T13:31` ve `:143` 1,61'i `pay_geri` alanından "m/s²" diye alıyor. Ama `pay_geri` boyutsuz bir sayı: f(dR) ÷ 1,5
  (`taban_montaj.py:363`). Değer, 2,41 ÷ 1,5 güvenlik katsayısıyla sayıca aynı çıkıyor, çünkü proje ölçütü pay = a_dev ÷ a ≥ 1,5
  (`kararlar:79` yöntemi). Atıf "`rampa5.geri` 2,41 ÷ 1,5" diye yazılmalı. `kararlar:79` aynı büyüklük için eski modelden 2,366 veriyor;
  kâğıt doğru olarak daha yeni JSON'u kullanıyor.
- `T13:142` B eşiği için "okuma payı ±0,5 cm (T9 adım 10)" diyor. T9 adım 10'daki pay ise 4–6 cm bandı, yani ±1 cm (`T9:101`). Ya atıf
  düzeltilmeli ya da B'nin doğrudan şerit okuması olduğu (video karesi değil, mm bölmeli) gerekçe olarak yazılmalı.

## 3. Atıf denetimi (36 atıf açıldı; hepsi doğru satırda, değer tutuyor)

| Atıf | Kâğıt | Satırda olan | Sonuç |
|---|---|---|---|
| `qled-not:114-117`, `:119` | T10 | Senaryo tablosu; "tilt servo gövdesi 50 °C'yi geçerse 30 mm fan"; servo ısısı yok | ✔ |
| `P-pi-kafada.md:45`, `:66`, `:73`, `:117` | T10 | MG996R 0…55 °C; 80–85 °C kısma; test şartı; el hesabı ±%30 | ✔ |
| `elektrik.md:28`, `:270`, `:477` | T10 | 19,8 W / ~49 °C "Ölçülecek"; test şartı + fan; açık iş 13 | ✔ |
| `elektrik.md:60`, `:91`, `:297` | T10 | Hat 7,5 + 7,5 + 5 A; C = pan + tilt; XL4016 C anahtarlı barada | ✔ |
| `karar-kuyrugu.md:94`, `:189` | T10 | Fan yeri HAT zarfıyla kesişiyor; K12 varsayılanı a | ✔ |
| `oneri-taslak-v8.md:68` | T10 | 4 saatlik yükte düşük gerilim ve ısıl yavaşlama 0 | ✔ |
| `arayuz.py:655`, `:973` | T11 | `sigorta_kutusu` zarfı; `etek_kapak_h1` | ✔ |
| `Y3-kontrol.md:40-43`, `:107-108`, `:113-115` | T11, T12 | 8,4 / 3,4 mm; 1 × 6 uç ikisi kapalı; "kavrama ~2 diş"; ±44 seçeneği; K7 ve perçin açık | ✔ |
| `kararlar:114-115`, `:119-122` | T11, T12 | H1 aynı, uç yuvalar yedek; M5×18, "≥ 8,3 mm gövde" | ✔ |
| `elektrik.md:290`, `:341-347`, `:327-347` | T11 | 6 yollu kutu; sigorta seti; H1 kararı; sigorta listesi | ✔ |
| `M6-montaj-sirasi.md:228` | T11 | Kutu üstü plakaya 45 mm (15 Ekim, eski model) | ✔ |
| `karar-kuyrugu.md:149`, `:298` | T11, T12 | K8 KAPANDI; "K7 perçin delik çapı" (birleştirme bulgusu doğru) | ✔ |
| `arayuz.py:961-965`, `:442`, `:446`, `:436`, `:976-977` | T12 | Perçin ölçüleri ve cep payı; braket 3 / 2 mm; acil stop Ø22,4; anahtar Ø30 tahmini | ✔ |
| `kabuk_parcalar.py:700`, `:714` | T12 | Cep silindiri = flanş + `cep_pay` | ✔ |
| `kabuk-analiz.json` satır 573, 593, 1217, 1237 | T12 | 5,3 / 4,3 mm uç, 0,7 mm kalır; flanş kabuğa 0,09 mm | ✔ |
| `Y3-kontrol.md:60`, `:63` | T12 | M5 8, M3 6; perçin 16 (`maliyet.json:160` de 16) | ✔ (not: `maliyet_duzelt.py:233` eski "M5 × 6 + M3 × 8, 14": güncel değil, kâğıt doğru kaynağı kullanıyor) |
| `adim5/maliyet_duzelt.py:235`, `elektrik.md:62` | T12 | Perçin somun pensesi M3–M6; NP2 BE102 "etek deliği kontrol" | ✔ |
| `kararlar:7-8`, `:77`, `:83`; `duzeltme-plani.md:63` | T13 | 5°, ≤ 0,1; rampa freni 0,1; acil stopta kayma; E6 dinamik fren | ✔ |
| `elektrik.md:216-222`, `:223-224`, `:227` | T13, T4 | Mantar NC + GPIO12; yeniden devreye alma; yazılım hatasında yeniden çekme | ✔ |
| `taban-analiz.json` `robot.pozlar[0].rampa5` | T13 | geri 2,41, pay_geri 1,61; `donus.kutle_kg` 25,911; `motor.hiz_m_s` 0,393 | ✔ (birim notu §2) |
| `arayuz.py:667`; `uygulama-notu.md:35`; `uygulama-ivme.json` `yontem` | T13 | crr 0,03; pay 1,61 ≥ 1,5; a_sinir = a_dev_min ÷ 1,5 | ✔ |
| `elektrik.md:54` | T1 eki | Akü 12,8–14,4 V | ✔ |

## 4. Varsayım işaretleri, sayısal sınırlar, "aşılırsa"

- **Dürüst:** T10 ortam düzeltmesi, süreler, kararlılık ölçütü ve tel boyu varsayım diye işaretli. T11'de 3 mm pense payı ve kutunun merkezden
  bağlanması varsayım. T12'de 5 tur ve ISO diş adımı dış kaynak, ±0,2 mm, geçiş payları ve 3 mm et varsayım. T13'te 0,10 kg, 1,0 cm,
  30 s ve ölçüm noktası varsayım; 2,26 / 0,56 / 0,15 türetilen diye ayrılmış. Değeri 1,65 m ya da 125 cm modelinden gelenler (8,4 / 3,4 mm,
  45 mm, 1 × 6 hesabı) "yeniden ölçülmedi" diye yazılmış. Çıkarım olgu gibi sunulmuyor.
- **Sayısal sınırlar:** dört kâğıtta da var. Eksikler: T11'de delik aralığı "94 mm" için tolerans yok (öneri 10). T12 C'de yalnız
  üst sınır var. Delik parçaya göre fazla büyükse (somun ya da flanş deliği örtmüyorsa) KALIR çıkacak bir alt sınır yok, dönme kilidi
  tırnağı ölçülüyor ama ölçütü yok (düzeltme 8). T13'te alt sınır ortalama yavaşlamaya göre konmuş, gerçek devrilme anlık
  yavaşlamaya bağlı. Bu yüzden tutucu ve dişli kutusu sert tutuyorsa sık sık "KALIR: ani duruş" verebilir. Kâğıt 1 cm'nin altını
  teker kalkmasına bağlıyor (`T13:147`); öneri 13.
- **Aşılırsa:** dördünde de belge, kişi ve sonraki adım yazıyor: K12 / tasarım ajanı / Ahmet Yorulmaz (T10), K8'in yeniden açılması (T11),
  `arayuz.py:961-965` ve "braket delinmez, etek basılmaz" (T12), karar kuyruğunda yeni madde, dinamik fren notu ve "karar verilene kadar
  rampa yalnız bu düzenekle" (T13). İyi.

## 5. HTML ve betik

- `py -3 planlama\d158\testler\testler_html.py --kontrol` → "md dosyası: 14 (kâğıt T: 13), HTML bölümü: 14, iç bağlantı: 68, id: 166 /
  KONTROL GEÇTİ", çıkış 0. Betiğin 5. kontrolü (`testler_html.py:307`) HTML'yi md'lerden yeniden üretip karşılaştırıyor: HTML güncel.
- `git diff`: T2, T3, T5, T6, T7, T8, T9'da tek değişen satır "Kâğıt Tn / 9" → "/ 13". T1 ve T4'te sayaca ek olarak yalnız brief'teki ekler
  (T1 adım 5, T4 adım 5). `testler_html.py`'de yalnız açıklama satırı ve başlık. T10–T13 yeni (izlenmeyen) dosyalar.

## 6. Takma ad ve kişisel veri

`testler/` ve `F8d-gunluk.md` içinde takma ad **0**. Kişi adı olarak proje sahibinin adı (P8.3'te de vardı, `git show HEAD` ile görüldü)
ve yazılımcının yalnız ilk adı (Efe: T1 1, T10 2, T13 4 kez) geçiyor. Telefon, e-posta, kimlik bilgisi yok.

## 7. Düzeltme listesi

Zorunlu:
1. **T13 C ön şartı:** C ancak şunlar sağlanırsa yapılır (A ve B bunlar olmadan da yapılabilir): (a) Efe "devreden çıkar" komutunun var
   olduğunu teyit etti. (b) Robot düz zemindeyken komuttan sonra PC817 #2 en geç 0,5 s içinde düşüyor; 3 deneme yapılır, gecikme yazılır
   (varsayım işaretli). (c) Robot düz zeminde en düşük hızla giderken telefon bağlantısı kesilince en geç 0,5 s içinde duruyor
   (`hakem-v9/hakem-3.md:105` riski). Bunlardan biri tutmazsa C yapılmaz ve sonuç "C yapılmadı: durdurma yolu yok" diye kuyruğa gider.
2. **T13 yedek yol:** "Komut 1 s içinde barayı düşürmezse" maddesi eklenmeli: ipler gergin tutulur, kimse düşme hattına girmez,
   robot ipe dayanıp durunca ne yapılacağı tanımlanır (ör. Pi'den uzaktan kapatma / ESP32 reset → GPIO12 LOW, `elektrik.md:226`, `:229`;
   işe yarayıp yaramadığı düz zeminde denenmiş olmalı). Mantara ancak robot ipte hareketsizken ve yan taraftan uzanılır.
3. **T13 çıkış yönü:** Çıkışta durmayan robotu ip durdurmaz. Bunu kâğıt açıkça yazmalı. Dayanak ve ipi tutan kişi rampanın üst ucunun
   **yanında** durmalı, robotun gidiş doğrultusunun dışında. Rampanın üstünde robotun durmadan gidebileceği yol boş bırakılmalı.
4. **T13 kişi ve görev:** C için en az 3 kişi: (taban ipi), (devrilme ipi), (kumanda: sürüş + acil stop; ip tutmaz). Video tripodda.
5. **00-genel kural 1:** "acil stop düğmesi elde" yerine şu yazılmalı: mantar robotun etek plakasındadır. Robot hareket ederken
   ona alan dışından ulaşılamaz. Rampa kâğıtlarında (T9, T13) durdurma yolu T13'teki doğrulanmış yazılım komutudur, iple birlikte.
   Ayrıca **T9 adım 13**'teki "aynısını acil stop düğmesiyle yap" (`T9:110`) ya kaldırılmalı ya da T13'e yönlendirilmeli; bu hâliyle robot
   rampadayken düğmeye uzanmayı gerektiriyor.
6. **T10 adım 3 ve 6:** Kafa 12 V gerilim uçları da pens gibi **enerji yokken** takılmalı (gövdede, pens ile aynı yerde). Teller alan
   dışına çıkarılmalı, multimetre orada okunmalı. Pens ekranı alan dışından görülmüyorsa telefonla çekilmeli ya da pens okunmamalı.
   "N1" yerine ölçüm noktası "gövdedeki F3 sonrası kafa 12 V teli" diye yazılmalı (N1 kafanın içinde).
7. **T12 güvenlik:** "Kupon kenarları ve köşeleri eğe ya da çapak alma aletiyle körletilir" ve "mengene matkap tablasına ya da tezgâha
   sıkılır (sütunlu matkapta tabla dayamasına yaslanır)" maddeleri eklenmeli.
8. **T12 Bölüm C ölçütleri:** (a) Alt sınır: üretici panel deliği yazıyorsa delik o değer ±0,3 mm. Yazmıyorsa sıkma somunu ya da
   flanşın dış çapı ≥ delik + 4 mm (varsayım). Sağlanmazsa KOŞULLU. (b) Dönme kilidi tırnağı varsa deliğe kama yuvası gerekir: KOŞULLU,
   tasarım ajanına gider. (c) Acil stop satırına "kilitlenir mi (basılı kalır mı), nasıl bırakılır (döndürerek / çekerek)" eklenmeli.
   T4 eki bu bilgiye dayanıyor. Dış bilgi, doğrulanmadı: XB2 tipi adlandırmada BE1xx genelde yaylı, çıkıntılı düğmeyi gösterir;
   CAD'deki 60 mm mantarla (`arayuz.py:660`) aynı tip olmayabilir.

Önerilir:
9. T4 adım 5: mantarı bırakmadan önce yazılım durumunda GPIO12 = 0 görülsün. Bırakan kişi düğmeye arkadan uzansın ve hemen çekilsin.
10. T11: delik aralığı GEÇER sınırı "94 ± 0,5 mm" olsun (varsayım).
11. T11 adım 4–5: şablon, kutu üstünden ölçülen yüksekliğe (modelde 45 mm, `M6:228`) iki takozla kaldırılsın. Pense erişimi plaka
    yüksekliğinde denensin; şablon sigortaların üstüne yatırılınca sonuç iyimser çıkar.
12. T13 atıfları: `:31` ve `:143` "`rampa5.geri` 2,41 ÷ 1,5" diye düzeltilsin (§2). `:142`'deki ±0,5 cm ya gerekçelendirilsin ya da T9'un ±1 cm'si yazılsın.
13. T13: d < 31·v² ama teker kalkması 0 ve devrilme ipi gerilmediyse sonuç **KOŞULLU: ani duruş** yazılsın (KALIR değil). Veri yine
    tasarım ajanına gider; enerji hesabı (`F8d-gunluk.md` bulgu 3) orada doğrulanır.
14. T13 C: kantar elde taşınan ipte dayanağa yaklaşınca karabinaya takılabilir; C'de kantar robot ucuna yakın takılsın ya da çıkarılsın.
    Rampa boyu ölçüm noktası şartına yetmiyorsa v'nin düşürüleceği yazılsın.
15. T10: Tablo 2 30 dakikada bir, adım 6 ise SoC'yi 10 dakikada bir istiyor; Tablo 2 10 dakikalık olsun ya da "Pi kaydından (`T10-pi.log`)"
    diye yazılsın. Güvenlik satırındaki sigorta listesi "F1, F3, F4 (ESP32), F5 (röle bobini)" olsun.
16. T12: kupon denemesi siparişteki 2 yedeği (1 M5 + 1 M3) tüketiyor. Somun dönerse yeni kupon için ek perçin somun gerekecek
    (`T12:159`); siparişe birkaç adet pay eklenmesi önerilir.

## 8. Uygulayıcı günlüğü hakkında

`F8d-gunluk.md` iddiaları bağımsız olarak doğrulandı: `--kontrol` çıktısı, iki atıf düzeltmesi (`M6:228`, `elektrik.md:341-344`), JSON anahtarları
ve T13 birim hatasının düzeltilmesi doğru. Bulgu 1 (`karar-kuyrugu.md:298` iki açığı birleştiriyor) ve bulgu 2 (donanımda uzaktan acil stop yok)
doğru. Ancak bulgu 2'nin sonucu kâğıda bir ön şart olarak girmemiş; düzeltme 1–5 bunu kapatıyor.

---

# Yeniden kontrol 1 (08.11.2026, düzeltme turu 1'den sonra)

Girdi: `F8d-gunluk.md` "Düzeltme turu 1". Kâğıtlar yeniden, öğrencinin uygulayacağı sırayla okundu. Okunanlar: 00-genel, T13 (tamamı),
T9 (diff ve güvenlik), T6, T8, T10, T12, T11, T4. Yazılan tek dosya bu.

## Karar

**KOŞULLU (GEÇER'e çok yakın).** 16 maddenin 16'sı uygulanmış. Asıl GEÇMEZ sebebi kapandı: T13 C artık D1–D3 doğrulanmadan
yapılmıyor ve komut çalışmazsa izlenecek yol yazılı. Kalan üç küçük zorunlu düzeltme var: biri ön şart denemesinde yeni bir
kaçırma yolu (R1), biri yaklaşma yönü (R2), biri parça adı (R3). Bunlar uygulanınca paket GEÇER; yeni bir kontrol turu gerekmez,
diff'e bakılması ve `--kontrol` yeter.

| Kâğıt | Karar | Not |
|---|---|---|
| 00-genel | **GEÇER** | Kural 1 tutarlı (aşağıda); öneri Ö1 |
| T1 eki | **GEÇER** | Değişmedi |
| T4 eki | **GEÇER** | GPIO12 = 0 kontrolü, arkadan uzanma ve kilitlenmenin "doğrulanmadı" diye işaretlenmesi eklendi (`T4:69-73`) |
| T6, T8 | **GEÇER** | Yalnız acil stop satırı kural 1'e bağlandı (`T6:54`, `T8:49`) |
| T9 | **GEÇER** | B, D1–D3'e bağlandı; 3 kişi kuralı, çıkış yönü uyarısı; adım 13'teki düğmeye basma kaldırıldı (`T9:55-60`, `:115-116`) |
| T10 | **GEÇER** | Pens ve gerilim uçları enerji yokken gövdede takılıyor, okuma dışarıdan ya da fotoğrafla, yoksa "okunmadı" (`T10:45`, `:75-78`); F1, F3, F4, F5; Tablo 2 notu |
| T11 | **GEÇER** | 94 ± 0,5 mm, varsayım diye işaretli (`T11:94`); şablon takozlarla 45 mm yüksekte (`T11:37`, `:56-57`) |
| T12 | KOŞULLU | Kenar, mengene, alt sınır, dönme kilidi ve kilitlenme ölçütleri iyi; ama acil stop parça adı çelişkisi kâğıtta yok (R3) |
| T13 | KOŞULLU | Ana açık kapandı; R1 (D3 denemesinde robot kaçabilir) ve R2 (komut çalışmazsa mantara yaklaşma yönü) kaldı |
| HTML | **GEÇER** | `--kontrol`: md 14 (T 13), HTML bölümü 14, iç bağlantı 86, id 166, KONTROL GEÇTİ, çıkış 0 |

## T13, T9-B ve T13 A/B: uygulama sırasıyla okuma

1. **Ön şartlar, düz zemin (`T13:98-110`).**
   - D1 (Efe'nin yazılı teyidi) ve D2 (robot dururken komut, 3 deneme, ≤ 0,5 s, kayıt yoksa sağlanmamış) güvenli: robot hareket etmiyor.
   - **R1: D3 yeni bir kaçırma yolu açıyor.** D3'te robot düz zeminde giderken kumanda bağlantısı kesiliyor. Bu denemenin amacı,
     robotun durmayabileceğini görmek. Durmazsa robot en düşük hızla sürmeye devam eder ve onu durduracak bir yol yazılmamış:
     ip yok; D2 komutu aynı bağlantıdan geçtiği için o da çalışmaz; mantara uzanmak ise hareket hâlindeki robota el uzatmak demek
     (ortak kural 7). Yazılım planının kendi kabul denemesi bunu **tekerler havadayken** yapıyor (`yazilim-plani.md:75`: "Tekerlek havadayken …
     kablo çekilince 500 ms içinde duruyor"). D3 de böyle yapılmalı. Robot şaside takozlarla kaldırılır, tekerler havada döner,
     duruş teker videosundan okunur. Bu yapılamıyorsa D3 yerde, taban ipi arkadaki sabit dayanağa ≤ 0,5 m boşlukla bağlıyken yapılır.
2. **Görevler ve yerleşim (`T13:67-77`, `T9:55-62`).** 3 kişi şartı ve "kumandayı tutan ip tutmaz" kuralı var; üç kişi yoksa test yok.
   Çıkış yönü boş (≥ 3 m), dayanak ve ipi tutan kişi doğrultudan ≥ 1 m yanda (ikisi de varsayım diye işaretli). Çıkışta acil stop
   rampanın alt yarısında veriliyor. Çıkış yönündeki kaçırma yolu kapandı.
3. **A ve B (`T13:117-133`).** Robot rampaya iplerle sürülüyor, D1–D3 sağlanmış, durdurma "yazılım dur" ile, acil stop komutla veriliyor.
   A'da ip boşluksuz ve bağlı, B'de 2 cm. Komut çalışmazsa robot zaten motorla duruyor. Kalan yol yok.
4. **C (`T13:135-145`).** Ön şart Tablo 0'dan kontrol ediliyor; ilk deneme alt yarıda, en düşük hızla. Kantar ipin robot ucunda ya da
   çıkarılmış. Kalan yol yok.
5. **Komut çalışmazsa (`T13:78-86`).** Sıra doğru: ölü adam tuşu bırakılır (`yazilim-plani.md:78`), ipler gergin tutulur, yalnız D4'te
   denenmiş yedek yol kullanılır, kimse doğrultuya girmez, sonra mantara basılır.
   - **R2:** 4. adımda mantara "yandan" uzanılıyor. Ama bu anda bara açık (komut çalışmadı), yani **kollar da güçlü** ve yazılım hatalı
     olabilir. Mantar etek plakasının arka-sağ köşesinde (`arayuz.py:436`: x +, z −; sigorta kutusu da z −'de, "akünün arkasında",
     `arayuz.py:655`). Kollar ise gövdenin iki yanında. "Yandan" sözü kişiyi tam kolun yanına getirebilir. Düzeltme şöyle yazılmalı:
     rampanın **üst tarafından**, mantarın bulunduğu **arka köşeden**, kol hizasının arkasından, tek kolla uzanılır; gövde rampanın alt
     tarafına geçmez; devrilme ipi gergin kalır. Ayrıca D4'ün (Pi üzerinden ESP32'yi resetlemek) Pi'nin telsiz bağlantısına bağlı olduğu
     yazılmalı. Bağlantı koptuysa D4 de çalışmayabilir, yedek yine ölü adam tuşu ve iplerdir.
6. **Sonuç ve kuyruk (`T13:205-222`).** "C yapılmadı" ve "KALIR: durdurma yolu çalışmadı" kuyruğa gidiyor; ön şart kapanmadan robot rampada
   sürülmüyor. İyi.

**D1–D3'ün T13 A/B ve T9-B'ye genişletilmesi: onaylıyorum.** A/B'de ve T9-B'de robot rampada motorla sürülüyor (`T13:120`, `T9:98`).
Sürüş bağlantısı kopunca ortaya çıkan kaçırma riski (`hakem-3.md:105`) C'dekiyle aynı. Acil stopun tek yolu da yine komut. C ile
sınırlamak tutarsız olurdu. Bedeli bütün rampa denemelerinin Efe'nin teyidine kadar beklemesi; ama rampa hiçbir parça siparişini
engellemiyor (T1 ve T9-A düz zeminde), bu yüzden kabul edilebilir. Not: T9 adım 13 (`T9:115`), isteğe bağlı "motor gücünü kes (PWM 0, sürücü kapalı)"
ölçümü de dişli kutusunun boşta durumunu ölçer; T13 A ile aynı bilgiyi verir, çelişki yok.

## Kural 1'in yeni hâli

`00-genel.md:32-41` tutarlı:
- Mantarın yeri (`arayuz.py:436`, `:466` "Acil stop mantari (etek plakasi ustu)") ve uzaktan acil stopun olmaması doğru yazılmış.
- Görevi yalnız mantar olan ayrı kişi tanımlanmış, erişilemiyorsa test yapılmıyor.
- Komut ek yol olarak geçiyor; rampa istisnası T13 D1–D3'e bağlı; rampada en az 3 kişi.
- T6:54, T8:49 ve T10:57 aynı cümleyle kurala bağlanıyor, T9:55-60 istisnayı kullanıyor. Çelişen kalmadı.
- Eski "acil stop elde" ifadesi `testler/` içinde artık yok (grep).

**Ö1 (öneri):** Mantarın, T8'in kendi tanımladığı "tam uzanmış kolun ulaşabileceği yer + 0,5 m" bölgesinin (`T8:52`) dışında kalıp
kalmadığı geometriyle kontrol edilmedi. Mantar 0,26 m yükseklikte, sağ omzun aşağı yukarı altında (`arayuz.py:44` Y_COV1 = 262).
Kol uzunluğuna göre bölgenin sınırına düşebilir. Kural güvenli yönde işliyor ("erişilemiyorsa test yapılmaz"), ama T6-B ve T8'i
durdurabilir. Tasarım ajanı mantar kişisinin duracağı yeri (robotun arkası, arka-sağ köşe) kol tarama hacmine göre bir kez işaretlemeli.

## Acil stop parçası: iki kaynak

- Kaynaklar farklı söylüyor: `arayuz.py:660` "Emas B200E60 … **Elde B200E-E (40 mm mantar)**". `elektrik.md:62` ise "acil stop
  **NP2 BE102** (CAD 60 mm B200E60; etek deliği kontrol)".
- Kâğıtlar yalnız NP2 BE102'yi adlandırıyor (`T12:14`, `:37`, `:96`, `:139`, `T4:69`). B200E-E hiç geçmiyor.
- Kilitlenme ölçütü (`T12:38`, `:159`, varsayım işaretli) ve "kilitlenmiyorsa ayrı kişi basılı tutar" (`T12:176-177`) doğru yaklaşım.
  Ama öğrenci elindeki parça B200E-E ise Tablo 4'ün satır adı yanlış parçayı gösterir. Günlükteki "T12 C ikisini ölçüyle ayırır"
  iddiası kâğıtta karşılanmıyor.
- **R3:** T12 C'nin başına "Robota takılacak acil stop: ☐ NP2 BE102 (`elektrik.md:62`) ☐ Emas B200E-E, 40 mm, elde (`arayuz.py:660`)
  ☐ başka: ____" satırı eklenmeli. Varsayım tablosuna da "iki kaynak farklı parça söylüyor" diye yazılmalı. Ölçütler takılacak
  parçaya uygulanır; çelişki tasarım ajanına gider (`elektrik.md:62` ya da `arayuz.py:660` düzeltilir). T4:69'daki "NP2 BE102'nin" ifadesi
  "takılan mantarın" diye değiştirilmeli.

## Yeni varsayımlar ve atıflar

- Yeni sayıların hepsi varsayım diye işaretli: D2 ve D3'teki 0,5 s, 15 kare, ≥ 3 m ve ≥ 1 m, 94 ± 0,5 mm, delik ±0,3 mm ve delik + 4 mm,
  ek perçin 2'şer, kilitlenme. B'deki ±0,5 cm için gerekçe yazılmış (duran robot, şeritten doğrudan okuma); kabul ediyorum.
- Yeni atıflar açıldı, hepsi doğru satırda:
  - `elektrik.md:225`: PC817 #2, 500 ms
  - `elektrik.md:226`, `:229`: reset anında GPIO12 LOW
  - `yazilim-plani.md:35`: 500 ms Pi mesajı yoksa teker DUR
  - `yazilim-plani.md:75`: watchdog, tekerlek havada kabul denemesi
  - `yazilim-plani.md:78`: ölü adam tuşu
  - `arayuz.py:466`: mantar etek plakası üstünde
  - `hakem-v9/hakem-3.md:105`: kumanda koparsa son komut kalabilir
- Bir not: `yazilim-plani.md:36`'ya göre kumanda Bluetooth gamepad ve ESP32'ye doğrudan bağlı (Bluepad32). Bu durumda 500 ms Pi
  bekçisi gamepad kopmasını görmez; D3'ün bunu ölçmesi doğru.
- `git diff`: T2, T3, T5, T7'de yalnız sayaç değişmiş. T6 ve T8'de sayaç ve acil stop satırı, T9'da sayaç ve düzeltme 5'in satırları
  değişmiş (Tablo 2'deki "Acil stop" ip yükü satırı da kaldırılmış, adım 13 ile tutarlı). Takma ad 0; kişi adları önceki gibi.

## Zorunlu düzeltmeler (yeniden kontrol 1)

- **R1 (T13 D3; T9-B D3'e bağlandığı için T9'u da kapsar):** D3 tekerler havadayken yapılmalı (`yazilim-plani.md:75` ile aynı düzen).
  Bu olmuyorsa robot yerde, taban ipi arkadaki dayanağa ≤ 0,5 m boşlukla bağlıyken yapılmalı. D3'ün durmama sonucu ip ya da teker
  havası ile sınırlanmalı.
- **R2 (T13 "komut çalışmazsa" 4. adım):** Yaklaşma yönü yazılmalı: üst taraftan, arka köşeden, kol hizasının arkasından, tek kolla;
  devrilme ipi gergin. D4'ün telsiz bağlantıya bağlı olduğu da not edilmeli.
- **R3 (T12 C, T4:69):** Takılacak acil stop parçası işaretlenmeli (NP2 BE102 ↔ elde B200E-E). Kaynak çelişkisi varsayım tablosuna
  yazılmalı ve tasarım ajanına gitmeli.

---

# Yeniden kontrol 2 (08.11.2026, düzeltme turu 2'den sonra; son karar)

Bakılanlar: R1–R3'ün değiştirdiği yerler. T13'te D3 ve D4 (`T13:105-123`), "komut çalışmazsa" (`T13:78-90`) ve Tablo 0;
T9 güvenlik (`T9:55-61`); T12 C (`T12:14`, `:38-39`, `:94`, `:144`, `:178-179`); `T4:69`. T13 ve T12 git'te izlenmeyen yeni dosyalar,
bu yüzden ilgili bölümleri doğrudan okudum. T4 ve T9'a `git diff` ile baktım. `--kontrol`: md 14 (T 13), HTML bölümü 14, iç bağlantı 86,
id 166, KONTROL GEÇTİ, çıkış 0.

## Son karar

**GEÇER, iki satırlık koşulla (K1, K2).** R1, R2 ve R3 uygulanmış. Asıl güvenlik açıkları (T13 C'nin doğrulanmamış tek durdurma yolu
ve D3'te robot kaçırma) kapandı. Yeni metin iki yerde küçük bir açık bırakıyor. Uygulayıcı bu iki satırı ekleyince paket GEÇER;
ayrı bir kontrol turu gerekmez, diff'e bakmak yeter.

| Kâğıt | Karar |
|---|---|
| 00-genel, T1 eki, T4 eki, T6, T8, T10, T11, HTML | **GEÇER** |
| T9 | **GEÇER** (D3 tanımı T13'e bağlı; K1 oradan gelir) |
| T12 | **GEÇER**: R3 tam. Takılacak parça kutusu (`T12:94`), çelişki satırı varsayım tablosunda (`:38`), Tablo 4'te "takılacak parça" (`:144`), çelişki tasarım ajanına (`:178-179`). `T4:69` de "takılan mantarın" diye düzeltilmiş |
| T13 | **GEÇER (K1, K2 ile)** |

## R1: "tekerler havada" ve "robot yerde, ip ≤ 0,5 m"

- **Tekerler havada (esas düzen):** Yeni bir açık yok. Enerji yokken kaldırılıyor, takozlar şasiye oturuyor, dönen tekere el uzatılmıyor,
  mantara arka köşeden basılıyor (`T13:111-113`, `:118-119`).
  - Öneri: takozlar tekerleri ancak 1–2 cm yerden kesecek kadar alçak ve geniş olsun. 1,58 m'lik robotun ağırlık merkezi yükselir,
    destek tabanı da daralmamalı.
  - Öneri: kaldırma iki kişiyle yapılsın. Robot takozdayken 1,6 m'lik düşme hattında kimse durmasın.
- **Robot yerde, ip ≤ 0,5 m (yedek düzen):** Robotun kaçması 0,5 m ile sınırlı, önünde kimse yok. Ama **ip birden gerildiğinde robot
  öne devrilebilir.** Bunu ipin esnekliğine ve hıza göre kaba hesapladım (ip esnekliği bilinmiyor, varsayım).
  - Hesap: 6 mm, ~200 kg taşıyan bir ipin 1 m'si için yay katsayısı k ≈ 10–20 kN/m. Robot ipe ½·m·v² enerjiyle çarpar. Tepe yavaşlama
    a = v·√(k/m).
  - v = 0,1 m/s'de a ≈ 2,0–2,8 m/s². v = 0,2 m/s'de a ≈ 3,9–5,5 m/s².
  - Düz zeminde ev pozunda öne devrilme ivmesi 3,62 m/s² (`taban-analiz.json` `robot.pozlar[0].duz.ileri`).
  - Yani "en düşük hız" 0,2 m/s civarındaysa robot öne, yüz üstü devrilebilir. Önünde kimse durmadığı için yaralanma olasılığı düşük,
    ama robot ağır hasar görür. Metin hız sınırı koymuyor, devrilme ipinden de söz etmiyor.
  - **K1:** Yedek düzene şu eklenmeli: hız **≤ 0,1 m/s** (varsayım); devrilme ipi T9'daki gibi omuz altından bağlı ve elde, ≤ 10 cm boşlukla;
    1,6 m'lik düşme hattında kimse yok. 0,1 m/s'ye inilemiyorsa yalnız "tekerler havada" düzeni kullanılır.

## R2: "arka köşe rampanın altına bakıyorsa uzanılmaz"

- Kural doğru: kimseyi robotun aşağısına göndermiyor. Ama yeni bir durum yaratıyor (`T13:88-90`). Robot rampada, **bara açık ve
  kollar güçlü** hâlde iplerde asılı kalıyor. Bağlantı ne zaman geri gelecek belli değil. Bu sürede devrilme ipi "gergin kalır"
  deniyor, yani **elle tutuluyor.**
- Bu dal sık yaşanacak bir dal: çıkış denemelerinde robot yukarı bakar, dolayısıyla arka köşe rampanın altına bakar.
- Elle uzun süre tutulan ip yorulup bırakılabilir. Tutan kişi düşme hattının dışında olsa da robot devrilir.
- Bitiş koşulu da yok: bağlantı hiç gelmezse ne yapılacağı yazmıyor.
- **K2:** Bu dala şu eklenmeli:
  1. Devrilme ipi de üst taraftaki ikinci sabit bir noktaya bağlanır ve elde tutulmaz.
  2. Tekerlerin dönmediği ve koku ya da ısınma olmadığı alan dışından izlenir.
  3. Bağlantı en çok 5 dk içinde (varsayım) geri gelmezse, iki ip sabitken mantara rampa doğrultusuna dik, **yandan** uzanılır:
     ayaklar robotun arka kenarının yukarısında, tek kolla, gövde robotun aşağısına geçmeden. Rampada devrilme, ipler sabitken
     rampa boyunca olur, yana olmaz (`rampa5.yan` 3,16 m/s² en büyük pay).

## R3

Tam. Yeni bir açık yok. Takılacak parça kâğıtta işaretleniyor, kilitlenme ölçütü varsayım diye işaretli, çelişki tasarım ajanına gidiyor.

## Kalan açık iş (karar değil)

Ö1 (mantar kişisinin yeri ile kol tarama hacmi) günlükte tasarım ajanına açık iş olarak yazılmış. Kâğıtlarda güvenli yönde işliyor;
GEÇER kararını değiştirmez.
