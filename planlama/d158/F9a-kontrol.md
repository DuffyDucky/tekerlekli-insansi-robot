# P9.1 (F9a) bağımsız kontrol — ajan B, 08.11.2026

Kontrol edilen: `planlama/proje-plani.md` (çalışma kopyası, `git diff` HEAD'e göre), `planlama/d158/F9a-gunluk.md`.
Kabul ölçütü: `planlama/d158/F9a-brief.md`. Yazılan tek dosya bu rapor. CAD koşturulmadı, commit yok.

## Karar: **KOŞULLU**

Tarih aritmetiği, 1,58 m başlık sayıları, tarihçe düzeni ve ad kuralı doğru. Ama planın ana cevabı ("S = 16.11 → Evet, H16
tampon") baskının kritik yolda olmadığı varsayımına bağlı ve bu koşul senaryo tablosunda yazmıyor. Nominal 8 hafta, lazer kesimin
taban adımlarının çoğunu beklettiğini hesaba katmıyor. Kesinti 4 ("gövde/göğüs kabuğu sonraya") M6 sırasıyla ve kabuk
bindirmesiyle çelişiyor. Aşağıdaki 1–4. düzeltmeler yapılınca GEÇER olur.

## 1. Tarih aritmetiği

| Kontrol | Sonuç |
|---|---|
| H1 = 28.09.2026 pazartesi; 08.11 = H6 pazar | Doğru (`date`) |
| Dönem haftaları H7 9–15 Kas … H16 11–17 Oca (`proje-plani.md:19–20`) | Hepsi doğru; 1.01.2027 cuma (H14) |
| S = 16.11: S+1 22.11 (H8), S+2 29.11 (H9), S+3 6.12 (H10), S+5 20.12 (H12), S+6 27.12 (H13), S+7 3.01 (H14), S+8 10.01 (H15) | Hepsi doğru |
| S = 30.11: 6.12 (H10), 13.12 (H11), 20.12 (H12), 3.01 (H14), 10.01 (H15), 17.01 (H16), 24.01 (dönem sonrası) | Hepsi doğru |
| Nominal 8 hf = 1 + 1 + 1 + 2 + 0,5 + 0,5 + 1 + 1 (aşama 2, 5, 6, 8, 9, 10, 11, 12) | Toplama doğru, ama aşama 2a ihmal edilmiş (bulgu B) |
| Kötümser ≈ 12 | Tablodaki üst sınırlarla 2 + 1 + 1,5 + 2,5 + **1** (kollar) + 1 + 2 + 2 = **13**; planın listelediği kalemlerle 12,5. "+4 hf" (`:94`) de 4,5–5 olmalı |
| İyimser ≈ 6,5 | Tablodaki alt sınırlarla 0,5 + 1 + 1 + 1,5 + 0,5 + 0,5 + 1 + 1 = **7,0**; lazer alt sınırı 1 hf olduğu için taban S+1'den önce başlayamaz → **7,5**. 6,5 tablodan çıkmıyor |
| Son güvenli gün 16.11 (1 hf tampon) / 23.11 (tamponsuz) | Nominal 8 hf ile doğru: 16.11 + 8 hf → 10.01; 23.11 + 8 hf → 17.01 (H16 pazarı). "Tamponsuz" demo hazırın H16'nın son günü olması demek; demo günü bilinmiyor (`:128`) |
| ≈ 4.12 (kesintiyle S + 6,5 hf ≤ 17.01) | 18.01 − 45,5 gün = 3.12 öğlen; 6 hf ile 7.12. Hesap tutarlı, **ama kesinti 4 düşerse geçersiz** (bulgu C) |
| S = 30.11 kesintiyle ≈ 10–14.01 | 30.11 + 6–6,5 hf = 10–14.01, tutarlı; kesinti 4 düşerse 17.01 (bulgu C) |
| Kalan kapasite 10 hf × 32 ≈ 320 kişi-saat | Doğru (H7–H16 = 10 hafta, 4 × 8) |

## 2. Kaynaklı denen süreler ve sayılar

| İddia | Kaynakta | Sonuç |
|---|---|---|
| Robotsepeti "tedarik süresi 7–12 iş günü" (`05-fiyat-arastirmasi.md:578–579`) | Satırlar doğru: ReSpeaker Lite ve MAX98357A **ürün sayfası** notu | Kaynak var ama satıcı geneline genellenmiş ("o satıcıdan alınan kalem"). 7–12 iş günü ≈ 1,5–2,5 hf; plan "2–2,5" diyor |
| Limacell "özel üretim, ort. 3 iş günü" (`06-aku-secimi.md:121`) | Satır 121, aday 3: aynen | Doğru |
| Victron sayfada stok 1 (15.10, `maliyet.json`) | `maliyet.json:82` "Fiyat 15 Ekim 2026 … sayfada stok 1"; notlar `:24` 17 Ekim | Doğru |
| Baskı 65 parça, 7,63–7,68 kg, 159–160 sa; 4–5 hf paylaşımlı; durmadan ≈ 6,7 gün | `baski-listesi.md:12`, `:34`, `:84` | Doğru. 65 parça Parti 1–4'tür (24 + 25 + 5 + 11); günlük "Parti 0–4" diyor |
| Parti 1: 24 parça, 68–69 sa; kupon ≈ 3 sa; filament firma + ekip; PETG-CF payı neredeyse yok | `baski-listesi.md:131`, `:112`, `:37` | Doğru |
| Haftada 32–40 sa | 160 / 5 ve 160 / 4; türetilmiş, "4–5 hf tahmininden" yazıyor | Dürüst |
| M6: 48 adım + F5; taban 1–16, K1 17, 18–36, kollar 37–48 (robotta 38–41, 48); kural 2, 3, 4 | `M6-montaj-sirasi.md` §1, §2, `:145–149` | Numaralar doğru. Ama M6 tablosu 125 cm'den (`planlama/rehber/R-gunluk.md:31`); 1,58 m'de göğüs ve kafa ekranı adımları henüz yok (`R-gunluk.md:33–34`), plan bunu söylemiyor |
| Stoksuz: ön şarj rölesi K2, optokuplör, IMU, kart burcu seti, servo uzatma, geniş köşe, kamera | `maliyet.json:102`, `:98`, `:62`, `:134`, `:52`, `:41`, `:65` hepsi `"stok": "yok"` | Doğru |
| Mesafe burcu M5 × 40 | `maliyet.json:44` `"stok": "belirsiz"`, satıcı "Türkiye'de bulunamadı"; `05-fiyat-arastirmasi.md:120`, `:150` (alternatifler) | Plan "stoksuz ya da bulunamayanlar" diyor: doğru. Günlük (bulgu 4) "`stok: yok`" diyor: yanlış alan değeri |
| XVF3800 ithal, ön sipariş; kamera kablosu ithal | `maliyet.json:73` (RobotShop EU, ön sipariş, stok belirsiz), `:66` | Doğru; 4 (3–6) hf "varsayım" diye işaretli |
| ≈ 1.340 TL (6808 × 4 + M3 × 168 + M5 × 6) | 4 × 106,80 + 168 × 5,22 + 6 × 6,27 = 427,20 + 876,96 + 37,62 = **1.341,78** (`maliyet.json:49`, `:146`, `:147`) | Aritmetik doğru. M5 fiyatı "tahmini". **Liste eksik:** kupon B 625ZZ ister (`tasarim/freecad/test/README.md:9`; 5 × 29,67 = 148,35, `maliyet.json:50`), kupon D 2 × M3×20 + pul + DIN 985 ister (`README.md:92–93`) |
| Lazer: alt plaka 346 × 500, 14 bükme braket, 2 kontrplak; süre/fiyat tahmini | `maliyet.json:129`, `:40` (8 + 6), `:130` | Doğru, "varsayım" işareti dürüst. "Sigma kesimi" lazer atölyesinde değil: satıcı ölçüye kesip gönderiyor (`maliyet.json:37`), aşama 2'ye ait |
| Yazılım: 8 jest listesi, 3 × 20, Y11 20–30 sa | `yazilim-plani.md:82`, `:86`, `:85` | Doğru |
| 2209-B rektör e-imzası 16–23.11 | Depoda yalnız brief'te (`F9a-brief.md:13`) | Kaynaksız; 23.11 H9 pazartesi, "(H8)" tam değil |

Varsayım işaretleri genel olarak dürüst: kaynaksız her süre "varsayım" ya da "süre varsayım" diye yazılmış.

## 3. Bulgular

**A. "S = 16.11 → Evet" baskıya bağlı, koşul tabloda yok (önemli).** Plan baskıyı nominal yola koymuyor; yan yolda "S'den önce
başlamazsa … aşama 8 ≈ 1,5–2 hf gecikir" diyor (`proje-plani.md:59–61`). Kupon değerlendirmesi 6808 ve ısıl gömme ister
(`baski-listesi.md:88`, `:116–117`), bunlar alınmadı; erken alım Ahmet'in kararında (`:116–118`). 1,58 m STL'leri de dışa aktarılmadı
(`baski-listesi.md:124–125`). S = 16.11'e bir hafta var: erken alım olmazsa yan yol devreye girer, demo hazır ≈ S + 9,5–10 hf =
24–31.01, H16'ya sığmaz. İki örnek tablosu (`:92`), son güvenli gün (`:99`) ve "Sipariş gecikmesi" riski (`:181`) bu koşulu yazmalı.

**B. Lazer kesim nominalde kritik yolda.** 2a nominal 1,5 hf, teslim 1 hf; plan "taban adım 4–5 buna bağlı" diyor (`:42`). M6'ya
göre lazer parçası bekleyen taban adımları çok daha fazla: alt plaka 4–10 (B1a–B4 plakaya), bükme etek braketi 11 (C0), kontrplak
güç paneli ve elektronik katı 12–15, bükme gövde braketi 18 (`M6-montaj-sirasi.md:97–111`). Lazersiz yalnız 1–3 (iskelet) yapılır,
o da birkaç saat. Ya 2a nominali 1 hf yapılıp "DXF ve teklif S'den önce" koşulu yazılır, ya nominal toplam 8,5 hf olur
(S = 16.11 → 13.01, tampon ≈ 0,5 hf; tamponsuz son gün ≈ 19.11). Ayrıca taban adım 9 aküyü takar (`M6:102`): aşama 5 2b'ye de bağlı.

**C. Kesinti 4 M6 ve kabuk yapısıyla çelişiyor (uygulayıcının "doğrulanmadı" maddesi: kontrol edildi, tutmuyor).**
- Omuz bandı göğüs bandına 1268 dikişinde bindirme cıvatalarıyla bağlı (`tasarim/freecad/kabuk/kabuk_parcalar.py:116`, `:594`,
  `:602`). Göğüs bandı yoksa omuz bandının alt bağlantısı yok.
- F3'te ekran ve M5 braket "üst açıklıktan (omuz bandı yok)" takılır (`M6:128`). Omuz bandı (F4) takılınca bu yol kapanır.
- F4 göbekten (G1, kollar) önce olmalı; sonra omuz bandı ancak kol başına ≈ 25 cıvata sökülünce çıkar (`M6:129`, `:149`, `:163`,
  `:171–181`). Bu yüzden "kollarla paralele" mümkün değil; "demo sonrasına" da omuz bandını askıda bırakır ya da sonradan kol
  sökümü ister.
- Süre kazancı da dayanaksız: F2 + F3 ≈ 21 M3 + 4 M5 cıvata (`M6:127–128`), saatlik iş; −0,5–1 hf kazanç montajdan çıkmaz.
  Kazanç olsa olsa baskıdadır (göğüs bantları 4,50–4,60 sa/adet, `baski-listesi.md:146–147`).
- 11,6" göğüs ekranı göğüs bandının cebinde (`baski-listesi.md:8`); bandı ertelemek göğüs ekranını da erteler, kesinti 5'teki
  "sabit tanıtım ekranı"yla çelişir.
- Sonuç: kesinti 2 + 3 ile kazanç ≈ 1 hf. S = 30.11 → demo hazır 17.01 (H16 pazarı), tampon yok. "≈ 4.12" son günü ≈ 30.11 olur.
  Mümkün tek kabuk kesintisi gövde kabuğunun (F2–F4) **tamamını** dışarıda bırakmak; bedeli sonradan kol başına ≈ 25 cıvata söküm.
  Bu bir karar maddesi olarak yazılabilir.

**D. Başlık sayıları ve tarihçe doğru.** 1.580,0 mm ve 1.177 parça (`lale158-kontrol.json:2`, `:5`), 25.910,6 g (400 g kablo payı
dahil; `uygulama-ivme.json:9`, `:17`; `uygulama-notu.md:7`), 10 servo DS3235 × 4 + MG996R × 6 (`servo-10-oneri.md:29–38`),
10,1" QLED 1280×720 (`baski-listesi.md:93`), 11,6" göğüs (`baski-listesi.md:12`), rampa payı 1,517 / eşik 1,5 (`uygulama-notu.md:7`,
`:36`). "1,65 m ana tasarım" ifadesi dosyada yok. Kalan 1,65 m geçişleri tarihçe ya da durum bilgisi: `:9` (maliyet.json henüz 1,65 m
sayılarıyla), `:10` (tarihçe), `:144` (Tarihçe başlığı), `:187` (kararın alındığı tasarım). Eski takvim tablosunun satırları
değişmemiş (diff yalnız başlığı ve üstündeki paragrafı değiştiriyor), "Tarihçe: 15 Ekim takvimi" başlığı altında.

**E. Adlar ve 2209-B.** `proje-plani.md`'de takma ad 0, "Echo" 0; kişi adı yalnız "Ahmet" (`:14`, `:118`, `:144`, `:146`, `:157`,
`:170`). Başka öğrenci ya da danışman adı yok ("hoca" rol olarak). **Günlükte "Efe" geçiyor** (`F9a-gunluk.md:61`): yeni dosyada yeni
geçiş. `tubitak-2209b/` izlenmiyor (git'te `??`), diff alınamıyor; içindeki en yeni dosya 16:13 (v14-final.docx), brief 21:20,
plan 21:28: uygulayıcı dokunmamış.

## 4. Düzeltme listesi

1. **İki örnek tablosu (`:92`), son güvenli gün (`:99`), "Sipariş gecikmesi" riski (`:181`):** S = 16.11 "Evet"i koşullu yaz:
   "erken alım (kupon parçaları) ve Parti 0–1 S'den önce ise; değilse baskı yan yolu +1,5–2 hf, sığmaz". Son güvenli günlere de
   aynı koşulu ekle.
2. **Aşama 2a ve 5 (`:42`, `:47`, `:57`, `:59`):** "Taban adım 4–5" → "taban adım 4–15 ve 18 (alt plaka, kontrplak, bükme
   braketler)". Ya 2a nominalini 1 hf yap ve "DXF + teklif S'den önce" koşulunu yaz, ya nominal toplamı 8,5'e çıkar ve iki örneği
   ona göre yeniden hesapla. Aşama 5'e 2b (akü, adım 9) bağımlılığını ekle. "Sigma kesimi"ni 2a'dan 2'ye al.
3. **Kesinti 4 (`:109–111`):** "Doğrulanmadı" yerine "M6 ile çelişiyor" yaz ve maddeyi kaldır ya da "gövde kabuğu F2–F4 tamamen
   dışarıda; sonradan takmak kol başına ≈ 25 cıvata söküm (M6 §3); göğüs ekranı da ertelenir" diye karar maddesine çevir. S = 30.11
   kesinti yolunu (`:96–98`) ≈ 1 hf kazançla yeniden yaz (demo hazır ≈ 17.01, tampon yok); "≈ 4.12" → "≈ 30.11".
4. **İyimser / kötümser (`:57–58`, `:94`):** tablodan türet: iyimser ≈ 7–7,5, kötümser ≈ 12,5–13 ("+4 hf" → "+4,5–5 hf"), ya da
   hangi aşamaların paralel kısaldığını yaz.
5. **Erken alım (`:116–117`):** listeye 625ZZ × 5 (kupon B, ≈ 148 TL) ve kupon D bağlantı elemanlarını (2 × M3×20, pul, DIN 985) ekle;
   toplamı ≈ 1.490 TL yap; M5 fiyatının tahmini olduğunu yaz.
6. **Robotsepeti satırı (`:41`):** "o satıcıdan alınan kalem" → "MAX98357A ve ReSpeaker Lite sayfalarında"; süreyi ≈ 1,5–2,5 hf yap.
7. **"Tamponsuz 23.11" (`:99`):** "demo H16'nın son günündeyse" ekle (demo günü bilinmiyor, `:128`).
8. **Dış tarih (`:127`):** e-imza tarihinin kaynağını yaz (Ahmet'in bildirimi, depoda belge yok); "(H8)" → "(H8 – H9 pazartesi)".
9. **M6 dayanağı (`:47`, `:52`):** M6 tablosunun 125 cm olduğu, 1,58 m'de göğüs ve kafa ekranı adımlarının henüz yazılmadığı notu
   (`R-gunluk.md:31–34`); adım numaraları kayabilir.
10. **Günlük:** `:61` "Efe'nin alanı" → "yazılım rolünün alanı"; `:11` "Parti 0–4: 65 parça" → "Parti 1–4: 65 parça (+ Parti 0 kuponları)";
    `:33` mesafe burcu için "`stok: yok`" → "`stok: belirsiz`, Türkiye'de bulunamadı".

---

## Yeniden kontrol 1 (08.11.2026, düzeltme turu 1'den sonra)

Kontrol edilen: `proje-plani.md` çalışma kopyası, `F9a-gunluk.md` "Düzeltme turu 1". Yazılan tek dosya bu rapor.

### Karar: **KOŞULLU** (iki madde kaldı: Y1, Y2; Y3–Y4 küçük)

### 10 maddenin durumu

| # | Durum | Not |
|---|---|---|
| 1 | Uygulandı | A/B ayrımı; dört sütunlu tablo, son güvenli gün tablosu, risk satırı (`:205`) koşullu. A'nın koşul metni gevşek: Y2 |
| 2 | Uygulandı | 2a → adım 4–15 ve 18 (`:42`), M6 `:97–111` ile tutarlı (alt plaka 4–10, bükme etek braketi 11, kontrplak 12–15, bükme gövde braketi 18). 2b aşama 5'te (`:47`). Sigma aşama 2'de (`:41`, `maliyet.json:37`) |
| 3 | Uygulandı | Kesinti 4 çıktı, karar maddesi oldu; kesinti 2 + 3 = −1 hf; A son günü 30.11 |
| 4 | Uygulandı | İyimser 7,5 / nominal 8 / kötümser 13 tablodan doğru türetiliyor (max(2,2a), 5, 6, 8, 9, 10, 11, 12: alt 1+1+1+1,5+0,5+0,5+1+1; üst 2+1+1,5+2,5+1+1+2+2); "+5 hf" doğru |
| 5 | Uygulandı | 427,20 + 148,35 + 876,96 + 37,62 = 1.490,13 TL, doğru. Küçük not: Y3 |
| 6 | Uygulandı | `:41` |
| 7 | Uygulandı | Son güvenli gün tablosunun başlığında |
| 8 | Uygulandı | `:150` |
| 9 | Uygulandı | M6 dayanağı notu, Kritik yol altında |
| 10 | Uygulandı | Günlükte "Efe" 0, `:11` "Parti 1–4 (+ Parti 0)", `:32` `stok: belirsiz`. (`:33`'teki `stok: yok` ötekiler için, doğru) |

Ad ve kapsam yeniden: `proje-plani.md`'de takma ad ve "Echo" 0, kişi adı yalnız "Ahmet"; günlükte de 0. "1,65 m ana" 0.
`tubitak-2209b/`'de 16:14'ten sonra değişen dosya 0.

### Tarih ve H numaraları (dört sütun)

Tablodaki göreli değerlere göre her tarih ve H numarası doğru: A sütunları ilk kontroldeki gibi; B'de 16.11 → taban 3.12 (H10),
ilk sürüş 9.12 (H11), gövde 3.01 (H14), kollar 10.01 (H15), jest 17.01 (H16), demo 24.01 / S+10,5 ≈ 27–28.01; 30.11 → 17.12 (H12),
23.12 (H13), 17.01 (H16), 24.01, 31.01, 7.02 / ≈ 10–11.02. Kesinti satırı (A: 3.01, 17.01; B: 17–21.01, 31.01–4.02) ve son güvenli
gün tablosu (A: 16.11 / 23.11 / 30.11; B 10 hf ile: 2.11 / 9.11 / 16.11) bu göreli değerlerle aritmetik olarak doğru.
Sorun tarihlerde değil, B'nin göreli değerinde (Y1).

### Kalan bulgular

**Y1. Durum B ≈ 10–10,5 hf iki gecikmeyi üst üste topluyor.** Plan B'yi "lazer +0,5" ve "aşama 8 +1,5–2" toplamı olarak kuruyor
(8 + 0,5 + 1,5–2). İkisi toplanmaz: lazer gecikmesi ilk sürüşü S+3,5'e iter, ama aşama 8 B'de baskıyı bekliyor (baskı S+1,5'te
başlar, S+5,5–6,5'te biter, `proje-plani.md` Durum B). Aşama 8 S+3,5'te başlayıp en erken baskı bitince kapanır. Bu yarım hafta
o beklemenin içinde kalır. Planın kendi "+1,5–2 hf" varsayımıyla gövde S+6,5–7, demo hazır **S+9,5–10**. Son parti çıkınca
≈ 0,5 hf montaj payıyla gövde S+6–7, demo S+9–10 olur. Tablodaki "Gövde + kabuk S+7" tek değeri aralığın üst ucu.

**16.11-B hangisi doğru?** İkisi de değil:
- Uygulayıcının 24–28.01'i (S+10–10,5) bu çift sayımdan geliyor.
- İlk turdaki benim 24–31.01'im aritmetik hatamdı: S+9,5–10 = 20–24.01'dir, 24–31.01 değil.
- Doğrusu, planın kendi varsayımlarıyla **≈ 20–24.01**; montaj payı 0,5 hf ile en erken 17.01.

Sonuç değişmiyor: tamponlu sığmaz. Ama kesinti 2 + 3 ile 16.11-B ≈ 13–17.01 olur ("17–21.01" değil). B'nin son güvenli günleri en
fazla yarım hafta öne kayar (9,5 hf ile ≈ 5.11 / 12.11 / 19.11). 30.11-B: ≈ 3–7.02, kesintiyle ≈ 27–31.01, yine sığmaz.

**Y2. Durum A'nın baskı koşulu "Parti 1 S+3'ten önce" yetmiyor (`:59–60`, takvim `:79–81`, risk `:205`).** Yazıcı tek ve paylaşımlı.
Parti 1'den sonra kalan Parti 2–4 91 sa ≈ 2,3–2,8 hf (68–69 sa Parti 1, toplam 159–160; `baski-listesi.md:34`, `:131`). Parti 2
(omuz yuvası, kafa servo yuvası) aşama 8'in ilk adımlarında lazım: M6 adım 19 (D1a), 23 (E1a) (`M6:112`, `:116`). Parti 1 S+3'te biterse
Parti 2–4 S+5,3–5,8'de biter. Aşama 8 (S+3 → S+5) 0,5–1 hf kayar, A'nın 8 haftası tutmaz. A için gereken: Parti 1 S'den önce
(≈ S−0,5) başlayıp ≈ S+1,5'e kadar bitmeli. Parti 2 servo gelince (S+1) sıraya girmeli. Yazıcı haftada 32–40 sa ayrılmalı ki
baskının tamamı ≈ S+4,5'te bitsin. Takvimdeki "S → S+1 Parti 1 sürer / S+1 → S+2 Parti 2 / S+2 → S+3 Parti 1 bitmiş olmalı"
satırları tek yazıcıda çakışıyor. S = 16.11 için bu, kupon parçalarının gelip değerlendirilmesi, CAD/STL dışa aktarma ve Parti 1'in
başlaması **≈ 12.11'e kadar** demek. Bunu açıkça yazın, A'nın ne kadar dar olduğu görünsün.

**Y3 (küçük).** "M3×20 seti listede ayrı fiyatlı değil" (`S'yi beklemeden`) tam doğru değil. M3×20, `maliyet.json:136` M3 imbus
satırında (1,30 TL kategori taban fiyatı). 2 adet ≈ 2,6 TL, pul ve DIN 985 ile toplam ≈ 1.495 TL; "≈ 1.490" kalabilir, ifade düzeltilmeli.

**Y4 (küçük).** `:116` "9.11 (fiilen geçti)": 9.11 yarın (H7 pazartesi). "Yarın; hoca onayı ve ödeme bir günde olmayacağı için fiilen
kaçırıldı" diye yazın.

### Düzeltme listesi (tur 2)

1. Durum B'yi ≈ 9,5–10 hf yap (lazer gecikmesi baskı beklemesinin içinde kalır; gerekçeyi bir cümleyle yaz). B sütunlarında
   gövde S+6,5–7, kollar S+7,5–8, jest S+8,5–9, demo S+9,5–10 olsun. Tarihler: 16.11-B 20–24.01, kesintiyle ≈ 13–17.01;
   30.11-B 3–7.02, kesintiyle ≈ 27–31.01. B son güvenli günlerini aralıkla yaz ya da "10 hf (ihtiyatlı) ile" diye kalsın.
   Risk satırında (`:205`) ve günlükte "10–10,5" → "9,5–10".
2. Durum A koşulu (a): "Parti 1 S'den önce başlar, ≈ S+1,5'e kadar biter; Parti 2 servo gelince başlar; yazıcı haftada 32–40 sa;
   baskı ≈ S+4,5'te biter" yaz. Takvim tablosundaki parti satırlarını tek yazıcıya göre sırala. S = 16.11 için son adım tarihini
   (≈ 12.11) yaz.
3. Y3 ve Y4 ifadeleri.

---

## Yeniden kontrol 2 (08.11.2026, düzeltme turu 2'den sonra)

Yalnız kalan maddeler kontrol edildi (Y1–Y4). Tarih hesabı: S 00:00 + k hafta; tam haftada önceki gün (pazar), yarım haftada
perşembe öğlen.

### Son karar: **GEÇER** (iki küçük not, tarihlerin sonucunu değiştirmez)

| Madde | Sonuç |
|---|---|
| Y1 B = 9,5–10 hf | Uygulandı. Gerekçe doğru: lazerin yarım haftası, aşama 8'in baskıyı beklediği sürede kalıyor. Gövde S+6,5–7, kollar S+7,5–8, jest S+8,5–9, demo S+9,5–10. "Sığar mı" açıkları (0,5–1 / 2,5–3 hf) ve son güvenli günler (B: 2–6.11 / 9–13.11 / 16–19.11) bu değerlerle tutarlı |
| B tarihleri | 16.11-B: taban 3.12 ✓, gövde 31.12 – 3.01 ✓, jest 14–17.01 ✓, demo üst 24.01 ✓. 30.11-B: taban 17.12 ✓, gövde 14–17.01 ✓, jest 28–31.01 ✓, demo üst 7.02 ✓. Yarım haftalı dört değer bir gün erken: ilk sürüş 10.12 / 24.12 (yazan 9.12 / 23.12), kollar alt ucu 7.01 / 21.01 (yazan 6.01 / 20.01), demo alt ucu 21.01 / 4.02 (yazan 20.01 / 3.02). H numaraları ve sonuçlar aynı kalıyor |
| Kesintili 16.11-B ≈ 14–17.01, 30.11-B ≈ 28–31.01 | **Uygulayıcı doğru.** S+8,5 = 16.11 + 59,5 gün = 14.01 öğlen; 30.11 için 28.01 öğlen. Benim "13–17.01"im, yarım haftaya da "pazar = −1 gün" kuralını uygulamamdan geldi; yarım haftada bu kural geçerli değil |
| Y2 A hazırlık takvimi | Tek yazıcıyla tutarlı. Parti 1 12.11'de başlarsa (68,5 sa): 40 sa/hf ile 23.11, 32 sa/hf ile 26.11 biter (yazan ≈ 25.11). Parti 2: 28.11 – 3.12 (≈ 1.12). Parti 3: 1–6.12 (≈ 5.12). Parti 4: 10–17.12 (yazan 17.12 = 32 sa/hf ucu = S+4,5) |
| M6 19 / 23 bağımlılığı | Tutarlı. 16.11-A'da aşama 8, 7.12'de (S+3) başlıyor. Parti 2 (omuz yuvası adım 19, boyun servo ve rulman yuvası adım 23, `M6:112`, `:116`) en geç 3.12'de bitiyor. Parti 3 (kafa, adım 29–31) en geç 6.12'de bitiyor. Parti 4 etek (adım 33) en geç 17.12'de bitiyor; aşama 8'in sonu 20.12, yani etek sona yetişiyor (32 sa/hf ucunda 3 gün pay). Parti 2 için servo S+1'de (22.11) geliyor; kargo 2 hf'ye uzarsa (30.11) Parti 2 ≈ 1 gün kayar, sınırda |
| Y3 ≈ 1.496 TL | Doğru. 2 × 1,30 (`maliyet.json:136`) + 4 × 0,40 (`:145`) + 2 × 1,02 (`:144`) = 6,24; 1.490,13 + 6,24 = 1.496,37 |
| Y4 9.11 | Uygulandı ("yarın … fiilen kaçırıldı, varsayım") |

### Küçük notlar (isteğe bağlı)

1. Yarım haftalı dört tarihi bir gün ileri alın (yukarıdaki tablo). Bu sonucu değiştirmez.
2. A hazırlık takviminde 11–12.11 içine kupon değerlendirmesi, CAD ve STL dışa aktarma sığdırılmış. Bu, aşama 3'ün 0,5 hf
   nominalini 1 güne indiriyor. Plan, Parti 1 16.11'de başlarsa ortaya çıkan +0,5 hf'yi yazıyor. Bu sıkıştırmanın da
   "varsayım" diye işaretlenmesi yeterli.
