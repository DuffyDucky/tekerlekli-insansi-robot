**DÜZELTME GEREKLİ** (küçük, tek cümle; engelleyici yok). Düzeltme turu 1'in metin değişiklikleri kayıtla birebir tutuyor. Bara sırası,
saplama numaraları, sigorta değerleri, kesitler ve kutuplar `kablolar.json` ile aynı. 14 göndermenin hepsi doğru karta gidiyor. Onay
kaydında kritik değer farkı 0. FreeCAD'siz sınamaların hepsi geçti. Üretimi durduracak ya da sessizce yanlış üretecek bir koşul bulamadım.
Tek kusur sıra değişikliğinden doğuyor. Toprak kartı (G05) artık XT60'tan önce geliyor ve metin XT60'ı anmıyor. Montajcı G05'i akünün
kutbuna bağlayabilir (D1). Düzeltmesi tek cümle. Üretimden sonra yapılırsa ikinci bir tam koşu gerekir, o yüzden şimdi yapılmalı.

# F10l kontrol 2 · P10.7b2d düzeltme turu 1 (K1 12, K2 8 kart; ikinci bağımsız kontrol)

16.11.2026, 02:13–02:30 (saat okundu). Dal `lale-duzeltme`, HEAD = `1c4e882`, iş çalışma ağacında. Depoda yalnız bu dosya yazıldı.
Betiklerim, kopyalarım ve bütün çıktılar oturum scratchpad'inde (`…\scratchpad\k2\`). Masaüstü'ne ya da depoya çıktı düşmedi.
`git status --porcelain` koşulardan önce ve sonra aynı. Depoda `__pycache__` yok. Eski `rehber_metin.py`'yi `git show 1c4e882:` ile
bellekte yükledim. Karşılaştırmayı ajanın `F10l-birlesim.py` betiğine dayanmadan kendi betiğimle yaptım.

## Bulgular (önem sırasıyla)

### D1 (düzeltilmeli, düşük-orta; üretimden önce) 17.1'de G05'in akü ucu belirsiz kaldı

`tasarim/freecad/rehber/rehber_metin.py:327`: "Toprak (G05, 12 AWG): akü − → yıldız barasının ortadaki (3.) saplaması."

- **Kayıt:** `kablolar.json` G05 damarı "XT60 (robot tarafı) · −" → "Yıldız barası · GND", uç türü lehim. Akünün kutbunu XT60'ın akü
  tarafına G01 bağlıyor (iki damar).
- **Eski sıra:** 17.1 ana hattı (XT60, G01 / G02) anlatıyordu, G05 ondan sonra geliyordu; "akü −" XT60 bağlamında okunuyordu.
- **Yeni sıra:** 17.1 montajcının ilk kartı ve kartta XT60 hiç geçmiyor. B3'ten akü robotta, "XT60 uçları ayrık, kutuplar bantlı"
  (B3 kontrolü) geliyor. Kartı harfiyen okuyan öğrenci kutbun bandını açıp 12 AWG G05'i doğrudan akünün − kutbuna bağlayabilir. Bunun iki
  sonucu var:
  - Çalışma sırasında boştaki 12 AWG pabuç akünün + kutbuna yakın durur.
  - XT60 eksi tarafta artık ayırmaz: kayıttan sapma, sonraki "akü ayrık = enerjisiz" ölçümlerinde kafa karışıklığı.
- Kısa devre yolu yalnız pabucun + kutba değmesiyle oluşur (+ bantlı), yani olasılık düşük. Ama kart 17.1 "şimdi bunu yap" kartı ve bu
  okuma bu turun sıra değişikliğinden doğdu.

**Önerilen düzeltme** (`rehber_metin.py:327`, "…({saplama.G05}.) saplaması." cümlesinin hemen arkasına, "İki bara da" cümlesinden önce):

```
"G05'in akü ucu XT60'ın robot tarafındaki − ucudur (lehim): akünün kutbuna doğrudan bağlama, akü kutupları bantlı kalır (akü ile "
"XT60'ın akü tarafı arası G01, madde 1). "
```

- "madde 1" çevirmeyle "alt adım 17.2" olur (çapa 1 = ana hat kartı). "G01," virgülle bitiyor, yani `_ADIM_ONEKI` onu adım öneki
  sanmaz. Gönderme sayısı 14 → 15 olur; D7 sayımı kendiliğinden tutar.
- Sonra şunlar gerekir:
  1. `rehber_denetim.py --kritik-onay-yenile`. Beklenen fark: 1 eklenen talimat cümlesi; cümle bölücü ":"de bölerse 2.
  2. `F10l-birlesim.py` `BEKLENEN_EKLENEN`'e bu cümle, norm biçiminde ("madde 1" yerine "§G"). Bölücü nasıl ayırırsa o kadar satır.
  3. § 9.4 sınamalarının yeniden koşusu.
- Eşdeğer, daha az metinli bir seçenek: cümlenin başını "Toprak (G05, {awg.G05}): akü − (XT60'ın robot tarafı, lehim) → yıldız barasının…"
  yapmak. Ama "akü − → yıldız barasının ortadaki" dizisini arayan bir desen olabilir (`rehber_denetim.py:1748` bozma metni). Ekleme
  cümlesi daha güvenli.

### D2 (not; aynı turda yapılırsa ucuz) Kablo yolu 3'ün G12 kısmı 17.4 karesinde "şimdi", ucu 17.5'te (görev 9)

Hükmüm: **kabul edilebilir**, üretimden önce düzeltme şartı değil.

- `CAD_ESLEME[3]` = G12, G09, G11, G08, G10, M01 (`rehber_kablo.py:110`). Yol tek parça CAD çizgisi, bölünemez.
- Öğrenci çizgiyi görüp G12'yi 17.4'te takarsa bile yığın sırası doğru kalır:
  - Anahtarlı bara saplama 1: köprü ucu (17.1) → G12 → G14 / G15 (17.5). Yıldız barası saplama 1 de aynı sıra.
  - 12 AWG yine altta, saplama başına pabuç sayısı aynı (4). Kısa devre ya da yanlış saplama oluşmaz.
- 17.5'te G12 karede "önceki" renkte görünür, G13 "şimdi". Küçük kafa karışıklığı.
- İstenirse N3'ün eşi tek cümle, `rehber_metin.py:376` "…röle gövdesindeki şema)." ile "\n" arasına:
  `" Karede Kablo yolu 3'ün baradan sol BTS7960B'ye giden kısmı (G12) da görünür; o uç madde 3b'de bağlanır."`
  ("madde 3b" → "alt adım 17.5"). Bu cümleyle D6 U4 tutar: 17.4 G12'yi anıyor ve 17.5'i numarasıyla anıyor. D3 de tutar (G12 17.5'te
  kendi demetiyle). Onay farkı +1, birlesim listesi +1 satır.

### N1 (not) D6 / D7 gerçek hatanın bir kısmını yakalıyor; asıl dayanak onay kaydı

Gerçek kaynak bozmalarım (kaynak bellekte değiştirildi, `kaynak_denetle` koşuldu; `…\scratchpad\k2\kaynak_boz.py`):

| Kaynak bozması | D6 / D7 | Onay farkı | Başka | Sonuç |
|---|---|---|---|---|
| 17.11'e "G17'nin − ucunu yıldız barasının {saplama.G17\|G18} numaralı saplamasına bağla." (gösterge "alt adım 17.7'de bağlandı" duruyor) | 0 | 1 | bağlam 1 | D6 kaçırdı |
| 17.9'a "G13'ün − ucunu … bağla." (17.5 göstergesi duruyor) | 0 | 1 | — | D6 kaçırdı |
| 17.12 köprüler "madde 2" → "madde 3" (var olan ama yanlış karta, 17.4) | 0 | 1 | zorunlu 1 | D7 kaçırdı, ZORUNLU yakaladı |
| F5'te "K2 madde 4" → "K2'nin 4. maddesi" (başka biçim) | 0 | 1 | — | D7 kaçırdı |

- **D6 U1 "bir uç iki kartta"** (`rehber_denetim.py:2449-2453`) metni değil, elle yazılan `DEMET_ALT[..]["uc"]` beyanını sayıyor. Bozması
  (`:2323-2324`) da yalnız bu beyanı bozuyor.
- **D6 U4** (`:2484-2493`) yalnız "o kartın numarası metinde geçiyor mu" diye bakıyor. Göstergeli bir karta eklenen ikinci "bağla"yı
  görmüyor.
- **D7** çevrilmeyen "madde N"yi ve olmayan kartı yakalıyor. Var olan ama yanlış karta giden çapayı ve başka biçimdeki göndermeyi
  yakalamıyor.
- Bellekteki bozmalarım D6 U3 ile D7e'nin çalıştığını da gösterdi: 17.1 ↔ 17.2 takası (G06 bara kurulmadan) D6 3 + D7 4 hata verdi;
  "alt adım 17.5" yerine "17.7" yazmak D6 4 hata verdi; G22 − yer tutucusunu silmek D6 1 hata verdi.
- Dördünü de onay kaydı yakaladı, üretim on sınamada durur (`rehber_uret.py:769-778`). Yani sessiz geçiş yok. Ama "D6 çifte bağlatmayı
  yakalar" iddiası yalnız beyan düzeyinde doğru. Düzeltme şartı değil.

### N2 (not) "N numaralı saplamasına" biçimi her yerde değil

Bu turun eklediği bütün saplama numaraları "N numaralı" biçiminde. Eski biçim (dokunulmamış) dört yerde duruyor:

- 17.1 "ortadaki (3.) saplaması" (`rehber_metin.py:327`)
- 17.6 "yıldız barasının {saplama.G22}. saplamasına" (`:396`)
- K1 kontrolü "yıldızın {saplama.G05}." (`:495`)
- F1 kontrolü "saplamasına (3.)" (`:974`)

Anlam aynı, montajcı için zararsız. `baglam` ve tamlık denetimi bu dördünde de geçiyor. Günlük § 9.1'deki genel ifade ("N numaralı …
biçiminde") yalnız yeni cümleler için doğru.

### N3 (not) "Baralar B5a'da panele takılı" iddiasının dayanağı zayıf (eski boşluk, regresyon değil)

- Kayıttaki tek dayanak B5a kablo notu: "Panelde yıldız barası (…) ve anahtarlı bara (…) erişilebilir kalsın" (`rehber_metin.py:244`).
- B5a iş metni ve kontrol listesi (sigorta kutusu, röle, ana sigorta yuvası) baraları saymıyor. Hiçbir adım bara tutucusunu panele
  taktırmıyor (`kablolar.json` bara-pabuc: "Tutucunun CAD'i P10.7b iş maddesi").
- Eski sırada da 17.1 G06'yı baraya bağlatıyordu; boşluk bu turdan önce de vardı.
- Öneri (bu paket dışı): B5a iş metnine "Yıldız barası ve anahtarlı bara (M5 saplamalı tutucu) panele" maddesi, kontrol listesine aynı
  satır.

### N4 (not) 32.6'da karede yeni öğe yok

AU3 şeması 32.5'te "şimdi" çiziliyor, lehim ve kutup kontrolü 32.6'da yapılıyor. 32.6'da AU3 "önceki" renkte görünür. Kabul edilebilir;
karede bakılacak.

## Doğruladıklarım (yöntem)

1. **Montajcı yürüyüşü 17.1 → 17.12 ve 32.1 → 32.8** (çözülmüş metin; `kablolar.json` `klemens_turleri.bara-pabuc.kopruler.*.yerlesim`
   ve kablo kayıtları):
   - Her bara ucu tam bir kartta bağlatılıyor; öbür kartlar ucu numarasıyla anıyor ("alt adım 17.5'te / 17.7'de bağlandı").
     - G05 17.1; G06 17.2 (s3, G05'in üstüne); G09 / G11 17.4 (anahtarlı s3).
     - G12 / G13 17.5 (+ anahtarlı s1 / s2, − yıldız s1 / s2), sonra G14 / G15 (anahtarlı s1 yuvayla, yıldız s1), sonra G16 (s2 / s2).
     - G22 17.6 (+ yuvanın kuyruğu anahtarlı s4, − ara parçayla yıldız s5).
     - G17 / G18 / G20 / A01 kutu ucu ve G17 / G18 / G20 − ucu 17.7 (yıldız s4, s4, s5).
   - **Pabuç sırası:** her saplamada 12 AWG (köprü, G05, G09, G11, G12, G13) incelerden önce. Saplama başına pabuç: yıldız 4/4/4/4/3,
     anahtarlı 4/4/4/2 (köprü uçları dahil), sınır 4. Köprüler 17.1'de, her bağlantıdan önce.
   - **Değerler:** sigortalar (F3 5 A, F4 5 A, F5 2 A, F6 3 A, hat A / B 7,5 A, C 5 A, G22 2 A), kesitler ve kutuplar yer tutucudan
     geliyor ve kayıtla aynı. Yeni cümlelerdeki yuva adları (G17 F3, G18 F4, A01 F5, G20 F6) kayıttaki `uc_a` ile aynı.
   - **Uyarılar:** K1 ana metni "Bağlarken akü ayrık (XT60 açık)" bütün kartlardan önce. "Ters bağlıyken enerji verme" 17.6'da G22'den
     önce. G07 makaronu 17.3'te lehimden önce. K2 ana metni "enerjisiz, F3 takılı değil". AU3 "dikişleri sıkmadan önce, enerjisizken"
     32.6'da "Sonra dikişleri sık"tan önce.
   - **Enerji:** K1 / K2'de hiçbir kartta akü bağlanmıyor. Açık uçlu hatlar (G17, G20, A01) sigortasız ve akü ayrıkken bağlanıyor; F1
     aşama 1'de F3 / F6 takılmıyor.
   - Tek sorun D1.
2. **Metin farkı** (eski ve yeni bütün adımlar, cümle cümle, çözülmüş ve ham; `…\scratchpad\k2\fark.py`, çıktı `fark.txt`):
   - Değişen yalnız K1, K2, F1 (yalnız ham, yer tutucu), F5 (iki gönderme), B6a (yalnız sıra) ve SEMA G07.
   - § 9.2'nin 8 değişen + 3 yeni cümlesi ve "yalnız biçim" listesi gerçek farkla birebir: eksik ya da fazla yok.
   - Kaybolan cümle ya da uyarı yok. Eski 17.9'daki G12–G15 / G18 bağlama bilgisi 17.5 ve 17.7'ye tam taşınmış.
   - E4'te metin değişmedi (`sema_ortulu` yalnız veri alanı). KABLO_AD aynı.
3. **Göndermeler (14), elle:**
   - 17.2 → 17.1 (G05, bara)
   - 17.9 → 17.5 (G12–G15) ve 17.7 (G18)
   - 17.11 → 17.7 (G17 / G20)
   - 17.12 → 17.8 ×2 (Ö4, düğüm kartı köprüsü) ve 17.1 ×2 (bara köprüleri)
   - K1 kontrol → 17.4 (K2 pim yeri) ve 17.1 (yerleşim)
   - K1 kablo P03 → 17.11
   - F5 iş metni ve F5.1 → 32.4 (1N5819)
   - 32.6 "bu alt adımda aşağıda" (AU3'ün gövde ucu aynı kartın ikinci paragrafında)

   Hepsi doğru. Çevrilmemiş kalan "madde" yok: kalanlar adımın kendi maddesi (B6a, E3a, F2, F3, F4, F5, H0a, H0c, H1). `app.js`,
   `yazdir.html`, `rehber_veri.py`, `rehber_kablo.py` ve şema adlarında K1 / K2 maddesine gönderme yok (yalnız yorumlarda "madde").
   Türkçe ekler doğru (17.1'de, 17.4'te, 17.5'te, 17.7'de, 17.8'de).
4. **Yer tutucular:**
   - `{v.aku_en_cok}` = "14,6 V": `elektrik.md:234` E2 "Akü gerilimi" satırı "14,6 V → 2,23 V, 10,0 V → 1,53 V"nin büyüğü.
   - `{v.aku_aralik}` = "12,8–14,4 V": `elektrik.md:67`, dosyadaki ilk "akü a–b V".
   - Çözülmüş F1 metni eskisiyle birebir aynı. Not: `elektrik.md:93` 14,6 V'u "en kötü durum hesap değeri" sayıyor; multimetre aralığı
     seçiminde (20 V) bu temkinli ve doğru.
5. **Onay kaydı** (`1c4e882` ↔ bugün, kendi karşılaştırmam; `…\scratchpad\k2\onay.py`):
   - Kablo bölümü 165 = 165, fark 0. Liste 204 → 206: köprü ZORUNLU deseni ve iki "is_ana".
   - Metin 1040 → 1064. Silinen metinlerde olup eklenenlerde olmayan değer belirteçleri yalnız "14,6 V", "14,4 V" (yer tutucuya geçti)
     ve "madde N" göndermeleri. Eklenenler saplama yer tutucuları, "alt adım S.M", kablo kimlikleri ve yuva adları.
   - Sigorta, kesit, AWG ya da kutup değeri silinmedi, değişmedi: **kritik değer farkı 0** tutuyor.
6. **`F10l-birlesim.py` beklenen listesi** farka uydurulmuş bir "her şey beklenen" değil: 9 silinen + 13 eklenen cümle tek tek yazılmış ve
   benim bağımsız farkımla aynı. Ama B parçası her göndermeyi "§G"ye eşitliyor (`F10l-birlesim.py:85-90`), C yalnız sayıyor. Hedef kartın
   doğruluğunu bu betik değil, benim elle bakışım ve D7e doğruladı.
7. **Üretim riski** (kod okuması + eski veriden benzetim, `…\scratchpad\k2\benzet.py`, `alan.py`):
   - **Kart numaraları:** `rehber_veri.py:74` `ALT_ADIM_NO` koşulu tetiklenmez. `rehber_metin.m6_kodlar()` ile `rehber_veri.m6_tablo()`
     aynı dosya ve aynı düzenli ifade; benzetimde 50 kod eşit, K1 = 17, K2 = 32.
   - **Kablo yolu → kart:** CAD etiketleri "Kablo yolu N: …" biçiminde, "Kablo yolu 1:" deseni 10 / 11 / 12'ye uymuyor. Eşleme
     tam bir kartta: 1 → 17.2, 2 → 17.1, 3 → 17.4, 4 → 17.5, 9 → 17.7, 10 → 17.8, 11 → 17.10, 5 / 7 → 32.1, 6 → 32.2, 8 → 32.3,
     12 → 32.4.
   - **Şema → kart:** G07 → 17.3, G16 → 17.5, G22 → 17.6, G19 → 17.9, B02 / N01 / N02 / Q01 / Q02 → 17.10, U06 → 32.4,
     H02 / U03 / AU3 → 32.5, G20 / G21 → 32.7. `demet_sema_coklu` uyumsuz 0; `sira_grup_bul` aynı kartı veriyor.
   - **Veri alanları:** `kablo_sec` P03 → [3] (17.11). `sema_ortulu` deseni E4.4'ün şema 26'sına uyuyor.
   - **`alan_isle`:** eski veride K1'de bilerek duruyor. Yeni biçimli benzetilmiş veride durmuyor; demet / genel / kablo /
     sema_ortulu alanlarını yazıyor.
   - **D3:** `tek = tek_s = None` (`rehber_uret.py:727`); sonraki bütün kullanımlar `if tek_s`, `(tek_s or {})` ya da
     `tek_s is None or` ile korunuyor. `%` işleci koşuldan önce bağlandığı için biçim dizgesi yalnız `tek_s` varken hesaplanıyor. Yeni hata
     yok. `say_sema` girdisi tarayıcının `g["sema"]` tamsayı listesi (eski `sema_fark` de bunu kullanıyor).
   - **`yazdir.html` / `app.js`:** yeni dallar yalnız `st.demet_alt`, `g.kablo`, `g.ref`, `g.sema_ortulu` ya da satırsız sıralı adımda
     çalışıyor. `lejantMetin`'in öbür çağrısında (`:220`) `ortulu` yok: davranış eskisi gibi. `altGrup`, `SEMA_OBJ`, `userData.d`
     tanımlı. `pdf_tamlik_bozma` üretimde çağrılmıyor (yalnız elle).
   - **Durdurma koşulları:** `rehber_veri`'nin yeni `SystemExit`'leri `veri()`'de "bitti:" yokluğuyla yakalanıyor (`rehber_uret.py:63`),
     sessiz değil.
   - **`rehber_sira`:** K1 / K2 eskiden de Referans dışı parçasız tek grup olduğu için boş grup davranışı yeni değil; çökerse
     `try` içinde, sessiz değil.

## Koşular (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`, cwd scratchpad)

| Sınama | Çıkış | Benim sonucum | Günlük § 9.4 |
|---|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel | aynı |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 172 | aynı |
| `rehber_denetim.py --kaynak` | 0 | metin 615; zorunlu 0; onay farkı 0 (kablo 165, liste 206, metin 1064); D1–D7 hata 0; K1 12 / 38 / 16, K2 8 / 18 / 10 | aynı |
| `rehber_denetim.py --bozma-denemesi` | 0 | 289 / 289, temel hata 0 | aynı |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, onay tutuyor / 86 / 86 | aynı |
| `rehber_kablo.py --veri …` / `+ --bozma-denemesi` | 0 / 0 | GEÇER, eşlemesiz 0 / 95 / 95 | aynı |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GECTI | aynı |
| `node --check rehber/app.js` | 0 | — | aynı |
| `F10l-birlesim.py` | 0 | GECER (14 gönderme, çözülemeyen 0) | aynı |
| `pdf_tamlik_bozma` (eski PDF + eski veri) | — | doğal (K1 s19 → s20) 10 / 10; sentetik (K2 s42 → s43) 11 / 11 | aynı |
| derleme (`compile`): `rehber_veri`, `rehber_uret`, `rehber_gorunum`, `F10d-dogrula`, `rehber_metin`, `rehber_denetim`, `rehber_deger` | — | hatasız | aynı |
| `rehber_gorunum.alan_isle` (bellekte) | — | eski veride K1'de durdu; benzetilmiş yeni biçimde geçti | aynı |
| kendi betiklerim: metin farkı, onay, benzetim, 8 bellek + 4 kaynak bozması | — | yukarıda | — |

## Sınadığım / varsaydığım

- **Sınadım:** yukarıdaki koşuların hepsi; cümle düzeyinde metin farkı; onay kaydı belirteç farkı; 14 göndermenin hedefi; kart eşlemesinin
  eski veriden benzetimi; D6 / D7'ye kendi bozmalarım; F1 yer tutucularının kaynağı.
- **Kod okumasıyla (koşmadan):** D3 kısmi koşu yolu; `app.js` ve `yazdir.html` yeni dallarının tarayıcıdaki davranışı; `rehber_sira`'nın
  boş gruplu kartlarla davranışı; `F10d-dogrula.py` `sema_tek`.
- **Varsaydım:** G05'in doğrudan aküye bağlanma olasılığı okur yargısı, ölçülmedi. Pabuç yığını kuralının elektriksel önemi kayıttaki
  kurala (`bara-pabuc.not`, ABYC E-11) dayanıyor. CAD kablo yollarının adı ve konumu bugünkü `taban-analiz.json` ile eski veriden; yeni
  FreeCAD çıktısı aynı varsayıldı.

## Doğrulayamadıklarım

- Kareler, PDF yerleşimi (91 alt adım kartı, sayfa sayısı, taşma, en küçük yazı), tarayıcıda E4 notu ve "Karede görünmez:" satırı,
  `alt_kontrol` / `F10d` `sema_tek`'in gerçek ölçümü, perdelenme / uçuş denetimi: hepsi üretim ister.

## Üretimden sonra bakılacak kareler

- **17.1:** bara + yerleşim listesi + Kablo yolu 2; D1 düzeltmesi yapıldıysa cümle kartta. Kartın boyu ≈ 910 karakter (+ düzeltme).
- **17.2:** G06 "3 numaralı saplamasına, alt adım 17.1'de takılan G05'in üstüne"; Kablo yolu 1.
- **17.4:** Kablo yolu 3 (G12 kısmı karede, D2); **17.5:** Kablo yolu 4 + G16 şeması, G12 "önceki" renkte; G12 → G14 / G15 → G16 sırası
  okunuyor mu.
- **17.6:** G22 şeması; **17.7:** Kablo yolu 9 (G18), yuva adları; **17.9 / 17.11 / 17.12:** göndermeler, kart başlığında "17.k".
- **32.1:** N3 cümlesi + Kablo yolu 5 / 7; **32.4:** U06 + eski yollu Kablo yolu 12; **32.5 / 32.6:** bölünme (1085 / 899 karakter),
  32.6'da AU3 "önceki" (N4).
- **E4.4:** ekranda "Ses kablosu (AU1, AU2): sol arka kabuğun arkasında kalır (görünümü döndür)"; basılıda "Karede görünmez:" satırı.
- **F1 kontrolü:** "akü en çok 14,6 V" ve "(12,8–14,4 V)".
- **K1 / K2 ilk basılı sayfası:** ana metin + "Bu adımda yeni parça yok."; P03 yalnız 17.11 kartında, "Kablo kancası"nda değil.
- **B6a Kablo kancası:** açıklama satırlardan önce.
