# F10j günlüğü · P10.7b2b: kayıt kapanışı, üç metin kusuru, denetim dişleri (kaynak düzeyinde)

15.11.2026, 07:25–07:56 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `4a097fb` ("Lale P10.7b2a"). Kapsam: R1, R2, R3, R4, R6,
R8, R10, R29 (keşif kalem tablosu). Kapsam dışı: R5, R7, R9, R11 ve öbürleri. FreeCAD, `rehber_uret.py` üretimi, F10* doğrulayıcıları
ve başsız tarayıcı **koşmadı**; rehber çıktılarına (`rehber/veri`, `rehber/goruntu`, `planlama/rehber/*.pdf`, `kontrol.json`)
dokunulmadı. Commit, push, `git add` yok. Devre değeri, sipariş listesi, CAD kaynakları, eski kontrol raporları değişmedi.
Paket dışı 14 dosya (13 `tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json`) dokunulmadan duruyor.

## Başlangıç ölçümü (değişiklikten önce, 07:25)

| Koşu | Çıkış | Not |
|---|---|---|
| `planlama/adim3/kablolar_uret.py --kontrol` | 0 | güncel |
| `planlama/adim3/kablolar_denetim.py` | 0 | bozma 167 |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0 | onay kaydı kablo 94 / liste 180 / metin 991; tamlık 172 öğe, eksik 0, muaf 21; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 185 / 185 |
| `tasarim/freecad/rehber/rehber_kablo.py` | 0 | çizilen 51 / çizilmeyen 23; geometri hata 0, bilgi 4; ayırt edilemeyen 1 (yol 10 A03 ↔ G22) |
| `rehber_kablo.py --bozma-denemesi` | 0 | 36 / 36 |
| `tasarim/freecad/rehber/rehber_kol_kablo.py --yazma` | 0 | |
| `git status --short` | | 14 satır (paket dışı 14) |

## R1 · P10.7b2a ve K63 kapanış kaydı

- `planlama/dongu-158.md:42` kilit satırı. Eski: "P10.7b2a | A (uygulama, kaynak düzeyinde; bitti, bağımsız kontrol bekliyor) | …".
  Yeni: P10.7b2b satırı (bu paketin yazdığı alan); P10.7b2a satırı silindi (paket bitti).
- `planlama/dongu-158.md:164` P10.7 satırı. Eski: "**P10.7b2a … 🔄 A ✅ kaynak düzeyinde 15.11** (…; bağımsız kontrol ve üretim
  bekliyor)". Yeni: "**P10.7b2a … ✅ 15.11, kapandı** (commit `4a097fb` "Lale P10.7b2a", uzak dal aynı commit'te; dört bağımsız kontrol
  `F10i-kontrol.md` DÜZELTME GEREKLİ, `-2.md` KAYNAK GEÇER, `-3.md` SON TUR GEÇER, `-4.md` COMMIT EDİLEBİLİR; üç düzeltme turu: ikisi
  kaynak düzeyinde, biri basılı sayfa yerleşimi; üretim ve zincir geçti, PDF 80 sayfa; K63 kapandı; tur sayısı K62'ye not)"; satırın
  sonuna P10.7b2b girdisi eklendi.
- `planlama/d158/karar-kuyrugu.md:78` K63 satırı: "**açık** (…; bağımsız kontrol ve üretim bekliyor)" → "kapandı (15.11; P10.7b2a,
  commit `4a097fb` …)"; varsayılan ve bloke sütunu "—".
- `karar-kuyrugu.md:77` K62 satırı: durum sütununa "15.11 notu: P10.7b2a'da üç düzeltme turu, ikisi kaynak, biri basılı sayfa"; madde
  **açık** kaldı. K62 bölümüne (`:1219-1225`) "P10.7b2a notu (kayıt; Ahmet'in bilgisine, karar verilmiş değil)" maddesi.
- `karar-kuyrugu.md:80` sayılar: "Açık: 50. Kapandı: 13 … Toplam 63" → "Açık: 49. Kapandı: 14 (… K59, K63 …). Toplam 63". Özet tablosu
  satır satır sayıldı (betikle, durum sütununun başı "**açık**" / "kapandı"): açık 49, kapandı 14, toplam 63; tanımsız durum 0.
- `karar-kuyrugu.md:117-123` P10.7b2a paragrafı: "K63 kaynak düzeyinde uygulandı (bağımsız kontrol bekliyor)" → kapanış (commit, dört
  kontrol ve hükümleri, üç tur, PDF 80); P10.7b2b satırı eklendi.
- `karar-kuyrugu.md` K63 bölümü: başlığa "— KAPANDI"; "Durum: açık … (bağımsız kontrol ve üretim bekliyor; kapanış onlardan sonra)" →
  "kapandı (15.11.2026, P10.7b2a; commit `4a097fb` …, uzak dal aynı commit'te)".
- `karar-kuyrugu.md` "P10.7b2a'da ele alınanlar": "(15.11, kaynak düzeyinde; bağımsız kontrol bekliyor; …)" → "(15.11; dört bağımsız
  kontrolden ve üretimden geçti, commit `4a097fb`; …)"; "Üretimde gözle bakılacak" → "Üretimde kare bakışı yapıldı (`F10i-gunluk.md`
  "Üretim ve zincir")".
- Doğrulama: `git rev-parse` HEAD ve `origin/lale-duzeltme` ikisi `4a097fb`. Commit'in yazar zamanı 07:03:17, commit zamanı 07:04:28
  (keşifteki 07:03:17 yazar zamanı). İki dosyada P10.7b2a / K63 ile aynı satırda "bekliyor" 0 (betikle ve aramayla).

## R2 · Kontrol-3 ve kontrol-4'ün açık işleri kuyrukta

`karar-kuyrugu.md` "Karar değil, iş" bölümünün sonuna dört madde: kontrol-3 A1–A7 (her biri "yapıldı", A6'da tolerans kalanı), kontrol-4
A1–A6 (A1, A2, A6 yapıldı; A3, A4, A5 açık, R5), "P10.7b2b'de ele alınan önceki açık işler" (G19 / G20 / G24 / G26, `PARCA_CAD`;
`TABAN_DISI_BOLGE` açık) ve "P10.7b2b'nin bulduğu açık işler". Kontrol-1 A8 maddesine "P10.7b2b'de yapıldı" notu.

## R3 · Üç talimat metni kusuru (`tasarim/freecad/rehber/rehber_metin.py`)

Sayılar yalnız yer tutuculardan (`{oran.aku_olcum}`, `{v.aku_aralik}`, `{v.aku_olcum}`, `{uc.AU3:+:a}`, `{uc.AU3:−:a}`); devre değeri
değişmedi, `rehber_deger.py`'ye dokunulmadı.

1. **K1 G07 makaronu** (kontrol-3 A5), `rehber_metin.py:328-330`. "(lehimden sonra geçmez)." ile "Direnci telin ucuna lehimle." arasına
   yeni cümle. Çözülmüş: "Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada tut (lehimin
   ısısı yakındaki makaronu erken büzer, sonra kaymaz)."
2. **K2 madde 5 AU3 sırası** (kontrol-3 A4), `rehber_metin.py:826-832`. Eski: "Kafa ucunda bağla (E4'te arka kabuk dikişleri
   sıkılmadı), sonra dikişleri sık." ardından AU3 lehimi. Yeni (çözülmüş): "Kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı);
   dikişleri sıkmadan önce, enerjisizken (akü XT60 ayrık): lehimden önce hoparlör kablosunun (AU3) + damarını iki ucunda multimetrenin
   süreklilik kademesiyle bul ve işaretle (iki ucu da boşta). Hoparlör kablosunun (AU3) kafa ucunu PAM8403'ün sol kanal çıkışına
   lehimle: + damarını L+ ucuna, − damarını L− ucuna; gövde ucunu fişsiz bırak (madde 6), F2'de hoparlöre lehimlenir. Kutup kontrolü,
   dikişleri sıkmadan önce (AU3): işaretli + damarı L+ ucunda, öbür damar L− ucunda (ters ise lehimi şimdi düzelt). Sonra dikişleri sık."
3. **F1 G07 ölçümünde akünün kendi gerilimi** (kontrol-3 A6), `rehber_metin.py:918-936`. Akü ayrıkken önce akünün XT60 pimlerinden
   akü gerilimi okunur; bölücü okuması bu gerilimle karşılaştırılır; aralık dışı okumada üç dal (akü aralıkta ya da oran tutmuyorsa
   bölücü bozuk; akü aralık dışında ve oran tutuyorsa akü aralığa gelene kadar devam yok). Eski parantez "(akü {v.aku_aralik} dışındaysa
   okuma da bölücü oranı kadar kayar)" bu dallarla değişti; ana anahtar / ESP32 / aşama 2 yasağı aynen duruyor. Çözülmüş tam metin
   aşağıda "Onay farkı" bölümünde (F1 kontrol girdileri) ve rapor özetinde.
   - **Kısmi:** brief "toleransıyla karşılaştır" diyor; dirençlerin toleransı kaynakta yok (`planlama/adim3/elektrik.md` E2 yalnız
     değer ve oran; `planlama/maliyet.json` direnç seti yalnız güç sınıfı). Sayı uydurulmadı: metin "beklenen bölücü okuması = akü
     gerilimi × bölücü oranı (0,1525); dirençlerin toleransı kaynakta yok (kablajda teyit)" diyor, sert eşik kaynaklı `{v.aku_olcum}`
     aralığında kaldı. "Belirgin farklı" sayısız. Açık iş kuyrukta (R2).
- İki bağlam düzeltmesi: K2 kutup cümlesine "(AU3)", F1 "Okuma …" cümlesine "bölücü okumasını … değerlendir" (anahtar ↔ bağlam
  denetimi cümlede varlık adını istiyor). ASCII izinli listeye 16 yeni doğru yazım (`rehber_denetim.py:137-142`, gerekçe yorumda).

**Denetim kuralları** (`tasarim/freecad/rehber/rehber_denetim.py`):
- `ZORUNLU` K1 G07 deseni (`:181-187`): "makaronu geçir" → "Makaronu lehim yerinden uzağa … orada tut" → "Direnci telin ucuna lehimle."
  → bacak kovana sık + lehim → soğuyunca makaron (eski desen bu cümleyi istemiyordu). Yeni `ZORUNLU` K2 deseni (`:188-192`): enerjisiz
  koşul, + damarı bul, AU3 lehimi, kutup kontrolü, "Sonra dikişleri sık" sırayla.
- `ZORUNLU_ALAN` F1 kontrol için 5 yeni madde (`:339-350`).
- Yeni `ZORUNLU_SIRA` (`:352-386`, `zorunlu_sira_listesi`, `sira_denetle`): "önce" öğesi alanda geçmeli ve "sonra"nın her geçişi onun ilk
  geçişinden sonra gelmeli. 5 madde: K2 dikişler AU3 lehiminden ve kutup kontrolünden sonra; K1 makaron tele geçirilir ve uzakta tutulur,
  lehimler sonra; F1 akünün kendi gerilimi akü takılmadan önce. `kaynak_denetle` (`:2125`) ve bozma sayacı `_zorunlu_eksik_say`
  (`:1879`) bunu da sayar; liste onay kaydına girer (`:1595`).
- `ZORUNLU_BOZMA` 9 yeni bozma (`:1815-1845`): makaron cümlesi silindi / lehimden sonraya taşındı; K2 kutup kontrolü silindi, dikişler
  AU3'ten önce sıkıldı, enerjisiz koşulu silindi; F1 akü gerilimi silindi, akü takıldıktan sonraya taşındı, "beklenen = akü × oran"
  silindi, "devam etme" silindi. 9 / 9 yakalandı. Sıra bozmalarından F1'inki ilk denemede kaçtı (yeni metin eski cümleyi silmeden
  ekliyordu, yani sıra bozulmuyordu); bozma, cümleyi taşıyacak biçimde düzeltildi, sonra yakalandı.

## R4 · PDF tamlık denetimi (`tasarim/freecad/rehber/rehber_uret.py`)

- `:374-396` yeni `_tam_say`, `_tam_kaynak` (adımın bütün kaynak alanlarının normalleştirilmiş metni: başlık, iş, erişim, bağlantı, alet,
  not, kontrol, kablo, alt adım ad / iş, parça ve bağlantı adları).
- `pdf_tamlik(pdf, V, esleme, ham=None)` (`:419-485`): **B4b**: devam sayfasında (eşleşen parça sayfanın ilk parçası değilse) bir önceki
  sayfanın son `TAM_EN_AZ` karakteri, eşleşmenin sayfa metnindeki konumundan önce yeniden geçiyorsa yineleme. **B5**: her maddenin
  PDF'teki sayısı adımın bütün kaynak alanlarındaki sayısından fazlaysa yineleme (yalnız `kontrol` alanına göre sayılsaydı K-4'ün 11
  bilinen kasıtlı tekrarı yanlış alarm olurdu: başlık = iş, kısa cümle iki alanda, alt adım işi ana işte). Madde listesine `kablo`,
  `erisim`, `baglanti_md` eklendi. Dönüş `yineleme`, `yineleme_sayi`, `madde_fazla`; `gecti` = eksik yok ve yineleme yok (sıkı yönde;
  hiçbir eşik gevşemedi). `yazdir()` çıktısı (`:586-590`) yinelemeyi de yazar.
- `:487-541` yeni `_tam_sil`, `pdf_tamlik_bozma(pdf, V, esleme)`: sayfa metinleri bellekte bozulur, dosya yazılmaz.
- Doğrudan çağrı, üretim yok (depo dışı geçici betik, bugünkü `planlama/rehber/Lale-montaj-rehberi.pdf` + `rehber/veri/rehber-veri.json`
  + `kontrol.json` `yazdir.sayfa_esleme`): `gecti` True, adım 50, madde 402, eksik 0, **yineleme 0, fazla 0** (yanlış alarm 0).
- Bozma (aynı yolla): temiz PDF geçer; B4b akış içinde (K1 s20) ve s20 başında; B5 kontrol / kablo / not maddesi iki kez; kontrol maddesi
  K1'in başka sayfasında (s19) yeniden; A2 `kablo` / `erisim` / `baglanti_md` metni PDF'ten silindi: **10 / 10 beklendiği gibi** (çıkış 0).

## R6 · Denetim kalıpları (`rehber_denetim.py`)

- **K-3 A1** (`:546-550`): "mantar / ana anahtar uçları aynı vidada" kalıbının iki kolunda isim listesine `kontak`. Bozma (`:1748-1751`):
  "Mantarın iki ucunu tek kontak vidasına sık" ve "Tek kontak vidasına ana anahtarın iki ucunu bağla" yakalanır; "Mantarın iki ucunu
  kendi kontak vidalarına ayrı ayrı sık" yakalanmaz. 3 / 3.
- **K-3 A2** (`:1226-1229`): gerilim (akü ölçümü) bağlamına `\bokuma\b`. Keşifteki "aralığ" önerisi denendi, bugünkü kaynakta 3 yanlış alarm
  verdi ("20 V aralığı" F1 kontrol ve F3 iş metni, F1'de "akü en çok 14,6 V"); "akü gerilimi" de denendi, 1 yanlış alarm ("bırakınca akü
  gerilimi (12,8–14,4 V)"). İkisi de alınmadı; bu çıplak değerler R9'un işi (kuyrukta açık iş). Bozma (`:1701-1705`): "Okuma 1,95–2,20 V
  aralığının altında …", "Okuma 1,9 V ile 2,2 V arasında değilse …", "Okuma 2,1 V ise …" yakalanır; "3. Kafa 12 V (G17, …)" yakalanmaz. 4 / 4.
- **K-3 A3** (`:1380-1382`): `TALIMAT_LISTE` yalnız liste başlığı: sayım + isteğe bağlı parantez + iki nokta. Ölçüm: bugünkü iş
  metinlerinde ok taşıyan ve sayım geçen tek cümle K2 madde 5'in "5 kablo (K14 a):" başlığı; eski ve yeni kalıp ikisi de tutuyor (AU3 / H02
  bozması yine yakalanıyor). Bozma (`:1999-2006`): "'2 tel' geçen ok talimatı" K03'ü sayar; "2 kablo (K14 a):" başlıklı okta K03 sayılmaz. 2 / 2.
- **K-3 A7** (`:419-421`): `_CUMLE_GENIS` "ör.", "vb.", "bkz." sonrasında bölmez. Onay kaydında E3a TVS cümlesi üç parça yerine tek girdi
  (aşağıda onay farkı, 3 girdi). Bozma (`:1993-1998`): iki kısaltma örneği 2 parça, cümle sonu örneği 3 parça. 3 / 3. `_CUMLE_GENIS` ve
  `_GERILIM_BAGLAM` onay kaydının kural listesine girdi (`:1606-1608`).
- **K-1 A8** (`:1057-1058`, `:1161-1184`): `rehber/index.html` `ARAYUZ_GORUNEN`'de; JS dizgelerinde ve HTML etiketlerinde görünen öznitelik
  değerleri (title / aria-label / placeholder / alt) tek sözcük de olsa; görünen özelliğe (textContent / innerText / innerHTML / title /
  placeholder / ariaLabel / alt, `setAttribute` ile title / aria-label / placeholder / alt) aynı deyimde atanan dizge. Karşılaştırma işleci
  içeren deyimdeki dizge kod sayılır. Yeni yakalanan ve elle bakılan 7 sözcük (`rehber/index.html` görünen metni ve title öznitelikleri: "neresi",
  "Tema", "tekrar", "oynat", "patlat", "beklet", "yerlerini"; düzeltme turu 1'de 6 → 7 düzeltildi) doğru Türkçe, izinli listeye gerekçeyle girdi (`:137-142`); son durum ASCII kalıntı 0,
  görünen dizge 102 → 137. Bozma: "Onceki" textContent, üç terimli atama, title özniteliği, title ataması, `setAttribute`
  aria-label, `yazdir.html` title, `index.html` metni ve alt özniteliği yakalanır (bozma listesi `:2022-2032`); `x.title = k === "baglanti" ? …` ve
  `el.className = "secili"` yakalanmaz. 10 / 10.
- `kablolar_denetim.py` bu pakette değişmedi (R6'nın maddeleri hep `rehber_denetim.py`'de).

## R8 · Eşleme sınamasının dişleri (`tasarim/freecad/rehber/rehber_kablo.py`)

- `PARCA_CAD` (`:151-152`, `:160-161`): "XL4016 C" = `^XL4016 servo 6 V C` (CAD parçası "XL4016 servo 6 V C (kafa pan + tilt)" güç
  panelinde); "XT60E-M" = modelsiz; "Dağıtım kartı C" taban dışı → modelsiz (karar P7b2a-6: güç panelinde, XL4016 C'nin yanında; kart
  modelde yok, R23). `MODELSIZ_KONUM`'a ikisi gerekçesiyle (`:181-186`), nokta ve vekil yok: sınanmaz, "elle bakıldı" bilgisi.
  Vekil olarak XL4016 C kutusu denendi: yol 6 yalnız boyun → kafa bölümünü çizdiği için S09 / S10'un kart yanı yola ulaşmıyor (gerçek
  durum; bozma b44 bunu gösteriyor).
- Kurallar (`:188-200` açıklama ve tablolar; `:662-713` `_yan_sina`, `:716-…` `geometri_denetle`, yeni bölümler `:749-781`):
  - (a) dal: dalda eşlenen her kablonun en az bir yanı dalın kendi noktalarıyla sağlanmalı (G19, G20).
  - (b) sınıf: bir yolda birden çok devre sınıfı ancak `KARISIK_BILINEN`'deki gibi (3 kırmızı / turuncu, 5 ve 7 sarı / turuncu; R18)
    (G24). `uc_imzasi` sınıfı da taşır (`:634`): ayırt edilemeyen çift 1 → 0.
  - (c) eksik eşleme: yolun sınıfında, iki yanı da bu yolla geometrik olarak sağlanan (elle bakılan ya da yalnız vekil parçayla sağlanan
    yan sayılmaz) eşlenmemiş kablo hata (G26). İlk denemede 9 yanlış alarm: G09 / G11 / G12 (anahtarlı bara vekili Röle K1; her taban yolu
    röleden çıkıyor) ve G10 (yol 1 ve 8, ön şarj kartı sigorta kutusunun yanında). Vekil yan kanıt sayılmadı (7 gitti); G10 için
    `GEO_EKSIK_MUAF` yol 1 ve 8 gerekçesiyle (G10 yol 3'te çizili). Son durum yanlış alarm 0. G18 / yol 9 kısmi eşleme yanlış alarm vermiyor.
  - `KARISIK_BILINEN` ve `GEO_EKSIK_MUAF` onay kaydında (`:814-816`).
- Bozma (`:1003-1011`, `:1028-1032`; `dene` yeni tabloları geri yükler, `:956-958`): b37 G19 (yol 4 + G08), b38 G20 (yol 4 + G10), b39 G24
  (yol 10 A03 → G22), b40 G26 (yol 1'den G02 çıktı), b41 yol 3'ün bilinen karışımı silindi, b42 yol 5 + G19, b43 G10 / yol 1 muafı silindi,
  b44 dağıtım kartı C XL4016 C kutusu sayıldı. Dördü (G19, G20, G24, G26) onay kaydı yenilendikten sonra da "denetim" mekanizmasıyla
  (geometri / eşleme kuralı) yakalanıyor; ilk iletileri: "yol 4: G08 iki yanı da yalnız ana yolun (yol 3) bölümüyle sağlanıyor …",
  "yol 10: devre sınıfları karışık (turuncu/yesil); bilinen karışım yok", "yol 1: G02 kablosunun iki yanı da bu yola ulaşıyor, sınıfı yolda
  (kirmizi) ama eşlenmemiş …". b23 (G6) da artık geometriyle yakalanıyor.
- Sonuç: çizilen **51** / çizilmeyen **23** (değişmedi); geometri hata 0, **bilgi 4 → 6** (yeni iki: yol 6 S09 a ve S10 a, dağıtım kartı C
  "elle bakıldı"; keşif "bilgi 4 korunur" diyordu, `PARCA_CAD`'i kararla tutarlı yapmanın doğal sonucu); ayırt edilemeyen 1 → 0.
- **Yapılmadı:** `TABAN_DISI_BOLGE` gövde bölgesi daraltılmadı: bugün gövde bölgesinde biten eşli uç yok, kaynaklı bir sınır (montaj
  analizinden ölçülmüş iç hacim) bu pakette çıkarılmadı. Açık iş.

## R10 · `planlama/rehber/R-gunluk.md`

- `:5` başlık. Eski: "## Durum (09.11.2026 16:05, F7a / P7.1: 1,58 m modelinden yeniden üretildi; ayrıntı …)". Yeni: "## Durum
  (15.11.2026, P10.7b2b sonunda): son üretim P10.7b2a (commit `4a097fb`): 50 adım, 1192 parça, 49 şema, PDF 80 sayfa; … Aşağıdaki
  kutular 09.11.2026 16:05 F7a / P7.1 kaydı …". 80 sayfa ve 50 / 1192 / 49 bugünkü PDF ve veriden okundu.
- "Kayıt" bölümüne F10g (P10.5b), F10h (P10.7b1), F10i (P10.7b2a, PDF 79 → 80) ve F10j (bu paket) girdileri. F10g / F10h sayıları
  `planlama/dongu-158.md` kayıtlarından alındı, bu pakette yeniden ölçülmedi. `:174` "PDF 75 sayfa" F10f girdisinin kendi tarihi için
  doğru, değiştirilmedi. README zaten "(80 sayfa)".

## R29 · Kablo yolu parçalarının rengi (`p1180`–`p1191`)

`karar-kuyrugu.md` F10e açık işine kapanış notu. Ölçüm (salt okuma): bugünkü `rehber/veri/rehber-veri.json`'da 12 / 12 parçanın `renk`i,
`rehber_kablo.Tablo.cizim(CAD_ESLEME[n])` sınıf rengiyle aynı (ör. `p1187` G17 `#d63031`, `p1189` acil stop `#2e9e4f`). P10.7b1'den beri
renk tablodan; tasarım kararı bu. Tarayıcıda "gerçek renk" kipinde bu parçaların ne gösterdiği ölçülmedi.

## Onay kaydı (`tasarim/freecad/rehber/rehber_kritik_onay.json`)

`rehber_denetim.py --kritik-onay-yenile` bütün metin ve kural değişikliklerinden sonra bir kez koşuldu (çıkış 0): **38 fark** yazıldı;
kayıt kablo 94 → 100, liste 180 → 193, metin 991 → 997. Hepsi bu paketin:

- **kablo (7):** `GEO_EKSIK_MUAF` eklendi; `KARISIK_BILINEN` eklendi; `MODELSIZ_KONUM` "Dağıtım kartı C *" ve "XT60E-M *" eklendi;
  `PARCA_CAD` "Dağıtım kartı C = taban-disi" → "modelsiz"; "XL4016 C = ^XL4016 servo 6 V C" ve "XT60E-M = modelsiz" eklendi.
- **liste (17):** `CIPLAK_KURAL` gerilim bağlamı (+ `\bokuma\b`); `CUMLE_GENIS` ve `GERILIM_BAGLAM` eklendi; `TALIMAT_LISTE` değişti;
  `YASAK` mantar / ana anahtar kalıbı (+ `kontak`); `ZORUNLU` K1 G07 değişti, K2 AU3 eklendi; `ZORUNLU_ALAN` 5 F1 maddesi; `ZORUNLU_SIRA` 5.
- **metin (14):**
  - E3a iş: TVS cümlesi üç parçadan bire (1 değişti, 2 silindi; metin aynı, yalnız bölme; A7).
  - F1 kontrol: "… multimetreyi DC V kademesinde bırak; kırmızı ucu … bağla." → "… DC V kademesinde bırak."; eklendi "Önce akünün kendi
    gerilimini oku: …"; eklendi "Sonra kırmızı ucu … saplamasına bağla."; eklendi "Bölücü okumasını not aldığın akü gerilimiyle karşılaştır:
    beklenen bölücü okuması = akü gerilimi × bölücü oranı ({oran.aku_olcum}); dirençlerin toleransı kaynakta yok (kablajda teyit), küçük fark
    ESP32'nin bir kez yapılan kalibrasyonuyla düzelir (E2)."; "Okuma {v.aku_olcum} aralığının … sonra ölçü uçlarını sök; akü ayrıkken
    bölücüyü kontrol et: … (akü {v.aku_aralik} dışındaysa okuma da bölücü oranı kadar kayar)." → "… sonra ölçü uçlarını sök; bölücü okumasını
    not aldığın akü gerilimine göre değerlendir."; eklendi "Akü gerilimi {v.aku_aralik} içindeyse ya da … bölücü bozuk: …"; eklendi "Akü
    gerilimi {v.aku_aralik} dışındaysa ve … akü {v.aku_aralik} aralığına gelene kadar devam etme (…)".
  - K1 iş: eklendi "Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada tut (…)".
  - K2 iş: "Kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı), sonra dikişleri sık." → "Kafa ucunda bağla (…); dikişleri sıkmadan
    önce, enerjisizken (akü XT60 ayrık): lehimden önce hoparlör kablosunun (AU3) + damarını … işaretle (iki ucu da boşta)."; eklendi
    "Kutup kontrolü, dikişleri sıkmadan önce (AU3): …"; eklendi "Sonra dikişleri sık."

Beklenmeyen fark yok. Kayıt SHA-256 öncesi D44657A1…, sonrası E33E52F6…. Kayıt metnin doğruluğunu kanıtlamaz; fark bağımsız kontrole.

## Son koşular (07:50–07:55)

| Koşu | Çıkış | Sonuç (önce → sonra) |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel |
| `kablolar_denetim.py` | 0 | GEÇER |
| `rehber_denetim.py --kaynak` | 0 | ascii 0, elektrik 0, zorunlu eksik 0, yasak 0, çıplak 0, bağlam 0, onay farkı 0; tamlık 172, eksik 0, muaf 21; kablo 74 / 74 |
| `rehber_kablo.py` | 0 | 51 / 23; geometri hata 0, bilgi 4 → 6; ayırt edilemeyen 1 → 0; onay tutuyor |
| `rehber_kol_kablo.py --yazma` | 0 | GECTI |
| `rehber_denetim.py --bozma-denemesi` | 0 | 185 / 185 → **216 / 216**; bozulmamış kaynakta hata 0 |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 167 → 167 |
| `rehber_kablo.py --bozma-denemesi` | 0 | 36 / 36 → **44 / 44** |
| `pdf_tamlik` doğrudan (bugünkü PDF) | 0 | yineleme 0, fazla 0, eksik 0 |
| `pdf_tamlik_bozma` doğrudan | 0 | yeni: 10 / 10 |
| `py_compile` (çıktı depo dışında): `rehber_denetim.py`, `rehber_kablo.py`, `rehber_metin.py`, `rehber_uret.py` | 0 | |
| `node --check rehber/app.js` | 0 | (dosya değişmedi) |
| `git diff 4a097fb -- planlama/adim3/kablolar.json` | | boş: devre değeri değişmedi |

Depoda `__pycache__` yok. `git status --short`: 23 satır (paket dışı 14 + `planlama/d158/karar-kuyrugu.md`, `planlama/dongu-158.md`,
`planlama/rehber/R-gunluk.md`, `tasarim/freecad/rehber/` altında 5 dosya değişti, bu günlük yeni). Eklenen 965 satırın (bu günlük dahil) gizlilik taraması
(yerel kullanıcı yolu, bulut eşitleme ve kullanıcı klasörlerinin adları, kullanıcı ve makine adı, varsayılan bilgisayar adı önekleri,
takma adlar, e-posta, telefon, gizli anahtar biçimleri): eşleşme 0.

## Keşfin tutmayan yerleri

- R8 kabul ölçütü "bilgi 4 korunur" ile "`PARCA_CAD` kararla tutarlı" birlikte tutmuyor: kart güç panelinde ve modelsiz olunca yol 6'nın
  S09 / S10 kart yanı sınanamaz, bilgi 6. Ayırt edilemeyen çift 1 → 0 (sınıf kuralı).
- R6 A2 önerisi ("aralığ" bağlama) bugünkü kaynakta 3 yanlış alarm veriyor; "okuma" seçildi.
- R8 "gövde bölgesi daralır": kaynaklı sınır olmadan yapılmadı.
- Commit saati: keşifteki 07:03:17 yazar zamanı; commit zamanı 07:04:28.
- R3 "toleransıyla": toleransın kaynağı yok (kısmi).
- Satır numaraları küçük kaymalarla doğru (ör. YASAK kalıbı `:482-486`, keşif `:481-490`).

## Doğrulanamayanlar

- Üretim koşmadı: yeni metnin basılı sayfaya yerleşimi, sayfa sayısı, devam sayfalarındaki bölme yeri ölçülmedi. PDF tamlık denetimi
  yalnız bugünkü (eski metinli) PDF'te ve onun bellekteki bozmalarında sınandı.
- Tarayıcı koşmadı: A8 kapsamındaki görünen dizgelerin ekranda gerçekten görünüp görünmediği ve "gerçek renk" kipi gözle bakılmadı.
- Dirençlerin toleransı ve akünün şarjı kaynakta yok; F1'deki "belirgin farklı" ölçütü sayısız.
- `ZORUNLU_SIRA` yalnız bir alan içindeki sırayı görür; alanlar arası (iş ↔ kontrol) sıra sınanmaz.
- F10g / F10h sayıları (`R-gunluk.md`) kayıtlardan alındı, bu pakette yeniden ölçülmedi.

## Üretimde beklenen sayılar ve bakılacak kareler

- Parça **1192**, şema **49**, alt adım **71**, 50 adım; kablo eşleme 51 / 23; elektrik 0; tamlık eksik 0, **yineleme 0**; PDF **80 ± 1**
  sayfa (K1'e ≈ 170, K2'ye ≈ 250, F1 kontrolüne ≈ 700 karakter eklendi; F1'in kontrol sayfası bir sayfa büyüyebilir). `rehber_kablo.py
  --veri` GEÇER, bilgi 6. F10* doğrulayıcıları bu paketin değiştirdiği işlevleri okumuyor (arama: `pdf_tamlik`, `geometri_denetle`,
  `ayirt_edilemeyen`, `TALIMAT_LISTE`, `_CUMLE_GENIS`, `ARAYUZ_GORUNEN` yalnız `tasarim/freecad/rehber/` içinde).
- Bakılacak: K1'in G07 paragrafı (makaron cümlesi lehimlerden önce, bölme yeri); K2 madde 5'in son üç cümlesi (AU3 lehimi → kutup →
  "Sonra dikişleri sık" aynı sırada, devam sayfasında yineleme yok); F1 kontrol listesinin G07 maddesi (akü gerilimi önce, üç dal, yasak
  cümlesi); bu üç adımın devam sayfalarının başı (B4b).

## Düzeltme turu 1 (`planlama/d158/F10j-kontrol.md` DÜZELTME GEREKLİ; 15.11.2026, 08:24–08:34, saat okundu)

Kaynak düzeyinde. FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları, başsız tarayıcı koşmadı; rehber çıktılarına dokunulmadı. Commit,
push, `git add` yok. Devre değeri değişmedi (`git diff 4a097fb -- planlama/adim3/kablolar.json` boş). Kontrolün üç bulgusu (D1, D2, D3)
düzeltildi; "Öbür bulgular"daki açık işler yalnız kuyruğa yazıldı.

### D1 · F1 G07 ölçümü (`tasarim/freecad/rehber/rehber_metin.py` F1 `kontrol`)

Tek uzun madde (çözülmüş 2.102 karakter) üç maddeye bölündü (631 / 831 / 888 karakter). Kontrolün önerdiği metin temel alındı; farklar:
ikinci madde "Karar yalnız banttan: okuma {v.aku_olcum} içindeyse bölücü geçer; ana anahtarı kapat, …" ve oranın "açıklamadır, karar
ölçütü değildir" olduğu açıkça yazıldı; üçüncü madde "Bölücü okuması {v.aku_olcum} …" ile başlıyor (anahtar ↔ bağlam denetimi cümlede
"bölücü" adını istiyor; kontrolün "Okuma …" cümlesi tek başına kalınca bağlam bulgusu 1 verdi) ve "Kusuru düzeltince ölçümü akü gerilimi
maddesinden baştan yinele." eklendi (yeniden ölçüm için ana anahtarın ne zaman açılacağı belli olsun). "pimine" → "kontağına"; kısa
devre uyarısı "(bir uç iki kontağa birden değmesin, iki uç birbirine değmesin)". Kalkanlar: "belirgin farklıysa", "katına yakınsa", koşulsuz
"… bölücü bozuk" cümlesi, koşulsuz "aralığın üstündeyse alt direnç eksik" teşhisi (artık yalnız akü aralıktayken okunan maddede),
"küçük fark kalibrasyonla düzelir".

Eski (çözülmüş, tek madde; özet): "… DC V kademesinde bırak. Önce akünün kendi gerilimini oku: … + pimine, siyah ucu − pimine değdir …
Sonra kırmızı ucu … bağla. … Bölücü okumasını not aldığın akü gerilimiyle karşılaştır: … küçük fark ESP32'nin bir kez yapılan
kalibrasyonuyla düzelir (E2). Hiç gerilim okunmuyorsa …; aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış. Okuma 1,95–2,20 V
aralığının altında ya da üstündeyse: …; bölücü okumasını not aldığın akü gerilimine göre değerlendir. Akü gerilimi 12,8–14,4 V içindeyse ya
da … belirgin farklıysa bölücü bozuk: … Akü gerilimi 12,8–14,4 V dışındaysa ve … katına yakınsa bölücü sağlam, …: akü 12,8–14,4 V
aralığına gelene kadar devam etme (…). Bölücünün orta noktası … aşama 2'ye (F5) geçme. Bitince ana anahtarı kapat, aküyü XT60'tan ayır,
sonra ölçü uçlarını sök".

Yeni (çözülmüş, üç madde):

1. "Akü ölçüm teli (G07), aşama 1'de mantar ölçümünden sonra: ana anahtar kapalı, akü XT60'tan ayrıkken multimetreyi DC V kademesinde
   bırak (kırmızı uç V soketinde). Önce akünün kendi gerilimini oku: akü XT60'tan ayrıkken kırmızı ucu akünün XT60'ındaki (akü tarafı) +
   kontağına, siyah ucu − kontağına değdir (bir uç iki kontağa birden değmesin, iki uç birbirine değmesin), okunanı not al: bu akü
   gerilimidir. Akü gerilimi 12,8–14,4 V dışındaysa burada dur: bölücü ölçümüne geçme, ana anahtarı açma, aşama 2'ye (F5) geçme; akü
   12,8–14,4 V aralığına gelince bu maddeyi baştan yinele (akünün şarjı bu adım için kaynakta yok, doğrulanmadı)"
2. "Akü gerilimi 12,8–14,4 V içindeyse: kırmızı ucu arayüz kartındaki akü ölçüm bölücüsünün orta noktasına (G07'nin kart ucu), siyah ucu
   yıldız barasının akü dönüşü (G05) saplamasına bağla. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim
   akü geriliminin bölücü oranı (0,1525) katıdır: akü 12,8–14,4 V iken bölücünün orta noktasında 1,95–2,20 V okunur
   (`planlama/adim3/elektrik.md` E2). Bölücü okumasını not al: not aldığın akü gerilimiyle birlikte ESP32'nin bir kez yapılan multimetre
   kalibrasyonunda kullanılır (E2); beklenen bölücü okuması = akü gerilimi × bölücü oranı (0,1525); bu açıklamadır, karar ölçütü değildir
   (dirençlerin toleransı kaynakta yok, kablajda teyit). Karar yalnız banttan: okuma 1,95–2,20 V içindeyse bölücü geçer; ana anahtarı
   kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök"
3. "Bölücü okuması 1,95–2,20 V aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök.
   Akü gerilimi 12,8–14,4 V içinde olduğu için bölücü bozuk: hiç gerilim okunmadıysa G07'nin pabucu, direnci ya da kart ucu kopmuş;
   aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış. Akü ayrıkken bölücüyü kontrol et: G07'nin direnci (pabuç ile bölücünün
   orta noktası arası, K1 kontrolündeki direnç ölçümü), direncin ve G07'nin iki ucundaki lehim, bölücünün alt direnci. Bölücünün orta
   noktası ESP32'nin akü ölçüm pinine bağlı (B6a, X01): bölücü düzelip okuma aralığa girene kadar ana anahtarı yeniden açma, ESP32'ye bu
   bölücüyle enerji verme, aşama 2'ye (F5) geçme. Kusuru düzeltince ölçümü akü gerilimi maddesinden baştan yinele. Listedeki yerlerde
   kusur bulunmazsa da devam etme: akü gerilimini ve bölücü okumasını kayda yaz (tolerans kaynakta yok)"

Sayıların hepsi yer tutucudan (`{v.aku_aralik}`, `{v.aku_olcum}`, `{oran.aku_olcum}`); çözülmemiş yer tutucu 0.

**Dört durum** (metin harfiyen izlenerek):

| Akü gerilimi | Bölücü okuması | Metnin verdiği sonuç | Güvenli / tek anlamlı |
|---|---|---|---|
| 12,8–14,4 V içinde | 1,95–2,20 V içinde | madde 2: bölücü geçer; ana anahtar kapatılır, akü ayrılır, uçlar sökülür | evet / evet |
| 12,8–14,4 V içinde | 1,95–2,20 V dışında | madde 3: bölücü bozuk; kapat → ayır → sök; listedeki yerler kontrol; düzelene kadar ana anahtar açılmaz, ESP32'ye bu bölücüyle enerji yok, aşama 2 yok; kusur bulunmazsa da devam yok, kayda yazılır | evet / evet |
| dışında | (içinde) | madde 1: burada dur; bölücü ölçümüne geçilmez, okuma hiç alınmaz; ana anahtar açılmaz, aşama 2 yok | evet / evet |
| dışında | (dışında) | madde 1: aynı (bölücüye geçilmediği için okuma yok) | evet / evet |

Kontrolün bulduğu yanlış durum (akü biraz aralık dışı, okuma bant içine düşüyor → aşama 2'ye geçiliyordu) artık oluşmuyor: akü aralık
dışındayken okuma alınmıyor. Akü aralıktayken oranın birkaç yüzde kaydığı, okumanın bant içinde kaldığı durum "geçer" (kararla aynı; fark
E2'nin bir kez yapılan kalibrasyonuna girer).

### D2 · K2 madde 5 (`rehber_metin.py` K2 `is_`)

Eski: "Kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı); dikişleri sıkmadan önce, enerjisizken (akü XT60 ayrık): lehimden önce …".
Yeni (çözülmüş, madde 5'in son kısmı): "Hoparlör kablosu (AU3) dışındaki dört kabloyu (U03, H02, S10, G17) kafa ucunda bağla (E4'te arka
kabuk dikişleri sıkılmadı). Hoparlör kablosu (AU3) için, dikişleri sıkmadan önce, enerjisizken (akü XT60 ayrık): lehimden önce hoparlör
kablosunun (AU3) + damarını iki ucunda multimetrenin süreklilik kademesiyle bul ve işaretle (iki ucu da boşta). Hoparlör kablosunun
(AU3) kafa ucunu PAM8403'ün sol kanal çıkışına lehimle: + damarını L+ ucuna, − damarını L− ucuna; gövde ucunu fişsiz bırak (madde 6),
F2'de hoparlöre lehimlenir. Kutup kontrolü, dikişleri sıkmadan önce (AU3): işaretli + damarı L+ ucunda, öbür damar L− ucunda (ters ise
lehimi şimdi düzelt). Sonra dikişleri sık." Baştan sona izlendi: dört kablo bağlanır → AU3 enerjisiz: + damarı bulunur → lehim → kutup
kontrolü → dikişler sıkılır; hiçbir cümle önceki bir işi geri almıyor. Metinde "dikiş… sık…" geçişi 4: "sıkılmadı", "sıkmadan" (2),
"Sonra dikişleri sık" (sonda).

### D3 · Sayı

`karar-kuyrugu.md:1461` ve bu günlüğün R6 maddesi: izinli listeye giren sözcük 6 → **7** ("neresi" dahil; `rehber_denetim.py:138`).

### Kurallar (`tasarim/freecad/rehber/rehber_denetim.py`)

- `ZORUNLU_ALAN` F1: "pimine" deseni → "kontağına" + iki kısa devre uyarısı; "beklenen = akü × oran" deseni "; bu açıklamadır, karar ölçütü
  değildir" ile; "içindeyse ya da … belirgin" → "Akü gerilimi {v.aku_aralik} dışındaysa burada dur: bölücü ölçümüne geçme, ana anahtarı
  açma, aşama 2'ye (F5) geçme"; "dışındaysa ve … yakınsa" → "Akü gerilimi {v.aku_aralik} içindeyse: kırmızı ucu … bölücüsünün orta
  noktasına"; "Okuma {v.aku_olcum} …" → "Bölücü okuması {v.aku_olcum} …". Yeni üç: "Karar yalnız banttan: okuma {v.aku_olcum} içindeyse
  bölücü geçer" (bant kuralı), "Akü gerilimi {v.aku_aralik} içinde olduğu için bölücü bozuk", "Listedeki yerlerde kusur bulunmazsa da devam
  etme: …".
- `ZORUNLU_SIRA`: K2'nin iki "sonra" deseni `dikişleri\s+sık(?!\w)` → `_DIKIS_SIK` = `[dD]ikiş\w*\s+sık(?!madan|ılmad)\w*` ("dikişlerini
  sık", "dikişleri sıkıp", büyük harfli başlangıç da; "sıkmadan", "sıkılmadı", "sıkılmadan" sayılmaz; 9 örnekle bellekte sınandı, 9 / 9).
  Yeni F1 sırası: "Akü gerilimi {v.aku_aralik} dışındaysa burada dur" bölücü ölçümünden ("aküyü XT60'tan tak, sonra ana anahtarı aç:
  okunan gerilim …") önce.
- `ZORUNLU` K2: yeni "Hoparlör kablosu (AU3) dışındaki dört kabloyu (U03, H02, S10, G17) kafa ucunda bağla" (AU3 yeniden "kafa ucunda bağla"
  kapsamına girerse).
- ASCII izinli liste: F1 metninin 9 yeni sözcüğü (yinele, kalibrasyonunda, banttan, kusuru, maddesinden, kusur, bulunmazsa, kayda,
  tolerans; gözden geçirildi, Türkçe harfi olmayan doğru yazım). Artık kullanılmayan "pimine", "belirgin", "kalibrasyonuyla" listede
  bırakıldı (kalıntı alarmı vermez; temizlik bu turun işi değil).
- `ZORUNLU_BOZMA`: metni değişen dört bozma yeni metne uyarlandı (K2 dikişler lehimden önce; F1 akü gerilimi silindi; F1 akü gerilimi
  akü takıldıktan sonra; F1 aralık dışı talimatı silindi); "F1 akü aralık dışında devam etme silindi" yerine yeni karar ağacı bozmaları.
  Yeni 16: K2 "dikişlerini sık", "dikişleri sıkıp" (kontrolün kural sayımında kaçan iki bozması), AU3 yeniden "kafa ucunda bağla"
  kapsamında; F1 "pimine" geri geldi, kısa devre uyarıları silindi, "iki uç birbirine değmesin" silindi (kontrolde yalnız onay kaydıyla
  yakalanıyordu), akü aralık dışı kapısı silindi, kapı "not al, bölücü ölçümüne geç" oldu, kapıdaki aşama 2 yasağı silindi, kapı bölücü
  ölçümünden sonraya (sıra), bölücü ölçümü koşulsuz ("Sonra kırmızı ucu"), bant kuralı silindi, bant yerine sayısız oran ölçütü ("yakınsa
  geçer"), oran karar ölçütü oldu, "bölücü bozuk" koşulsuz, "kusur bulunmazsa devam et". Hepsi kural sayımıyla yakalandı.
- Bozma: **216 / 216 → 231 / 231**; bozulmamış kaynakta hata 0 (yanlış alarm 0).

### Onay kaydı

`rehber_denetim.py --kritik-onay-yenile` bir kez (çıkış 0): **25 fark**; kayıt kablo 100 → 100, liste 193 → 198, metin 997 → 1000.
Hepsi bu turun cümleleri ve kuralları:
- liste (12): `ZORUNLU` K2 "dört kabloyu" eklendi (1); `ZORUNLU_ALAN` F1 5 değişti, 3 eklendi (yukarıdaki desenler); `ZORUNLU_SIRA` K2 iki
  "sonra" deseni değişti, F1 kapı sırası eklendi (3).
- metin (13): F1 kontrol 11 (eski cümleler → üç maddenin cümleleri; eklenen 2: "Akü gerilimi {v.aku_aralik} içindeyse: kırmızı ucu …
  bağla." ve "Listedeki yerlerde kusur bulunmazsa da devam etme: …"); K2 iş 2 (eski "Kafa ucunda bağla (…); dikişleri sıkmadan önce,
  enerjisizken (…): lehimden önce … (iki ucu da boşta)." → "Hoparlör kablosu (AU3) dışındaki dört kabloyu … sıkılmadı)."; eklendi
  "Hoparlör kablosu (AU3) için, dikişleri sıkmadan önce, enerjisizken (akü XT60 ayrık): lehimden önce … (iki ucu da boşta).").
- Kayıt girdi sırayla karşılaştırıldığı için eski ve yeni cümleler konumca eşleşiyor (ör. eski "Bitince ana anahtarı kapat …" → yeni
  "Kusuru düzeltince …"); anlamca silinen bir uyarı yok: eski cümlelerin bütün yasakları ve sırası yeni üç maddede. Beklenmeyen fark yok.
  Kayıt SHA-256 öncesi E33E52F6…, sonrası 0AD235A0….

### Koşular (08:31–08:32)

| Koşu | Çıkış | Sonuç (önce → sonra) |
|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel |
| `kablolar_denetim.py` | 0 | GEÇER |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 167 → 167 |
| `rehber_denetim.py --kaynak` | 0 | ascii 0, elektrik 0, zorunlu eksik 0, yasak 0 (istisna 10), çıplak 0, bağlam 0, onay farkı 0 (100 / 198 / 1000); tamlık 172, eksik 0, muaf 21; kablo 74 / 74 |
| `rehber_denetim.py --bozma-denemesi` | 0 | 216 / 216 → **231 / 231**; bozulmamış kaynakta hata 0 |
| `rehber_kablo.py` | 0 | 51 / 23; geometri hata 0, bilgi 6; onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | 0 | 44 / 44 → 44 / 44 |
| `rehber_kol_kablo.py --yazma` | 0 | GEÇTİ |
| `py_compile` (çıktı depo dışında): `rehber_denetim.py`, `rehber_metin.py` | 0 | |
| `git diff 4a097fb -- planlama/adim3/kablolar.json` | | boş |

Ara koşu: onay yenilenmeden önce `--kaynak` çıkış 1 (beklenen onay farkı; ilk denemede ayrıca ASCII 9 ve bağlam 1, yukarıda giderildi).
Depoda `__pycache__` yok.

### Kuyruğa yazılan açık işler

`karar-kuyrugu.md` "Karar değil, iş" sonuna "P10.7b2b bağımsız kontrolünden açık iş" maddesi: `pdf_tamlik`'in kaçırdığı yineleme türleri,
başlık yanlış alarmı, `pdf_tamlik_bozma`'nın komuta bağlanmaması, A1 / A2 / A7 biçim kaçakları, XT60E-M eşlemesi, `kablolar.json`'daki
"Dağıtım kartı C (kafa)" adı. Kontrol-3 A6 maddesine düzeltme turu 1 notu. Hiçbiri düzeltilmedi.

### Doğrulanamayanlar

- Üretim ve tarayıcı koşmadı: üç maddeye bölünen F1 kontrolünün basılı sayfa yerleşimi ölçülmedi (kontrolün ölçümünde F1 44–49,
  en küçük yazı 8,1 pt; bölünmüş metin 2.350 karakter, eskisinden 248 fazla; madde başına en çok 888, kontrolün sınırı ≈ 2.300'ün altında).
- AU3 kutbunun ters yazılması ("+ → L−") ve "okunanı not al" silinmesi hâlâ yalnız onay kaydıyla yakalanıyor (kontrolün öbür bulgusu;
  brief'in açık iş listesinde yok, bu turda kural eklenmedi).
- Akü XT60'ının gerçek kontak cinsi ve PAM8403 uç etiketleri parça gelince bakılır.

## Üretim ve zincir (15.11.2026; üretim ajanı U, zincir ve kare bakışı ajan U2)

Dal `lale-duzeltme`, HEAD = uzak = `4a097fb`, kaynak çalışma ağacında (düzeltme turu 1 sonrası). Üretim 08:38:52–09:21:34 (ajan U);
ajanın oturumu üretimden sonra kesildi, zincir, kare bakışı ve bu kayıt ikinci ajanla (U2) 11:03–11:50'de yapıldı (saat okundu).
Yöntem F10g § 5 / F10i "Üretim ve zincir": depo dışı geçici klasörde sarmalayıcı (15 s bellek bekçisi, eşik 1,2 GB art arda iki ölçüm),
her koşunun `.durum` kaydı; her koşu `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`. **Kaynağa dokunulmadı, kod düzeltmesi yapılmadı;
üretim yeniden koşmadı.** Aynı saatlerde ikinci dar bakış (`F10j-kontrol-2.md`, KAYNAK GEÇER, 08:45) depoyu yalnız okudu; metin
düzeltmesi istemedi.

**Başlangıç denetimi (U2, 11:01):** HEAD = uzak = `4a097fb`; kilit "boş"; boş bellek 4,29 GB; çalışan FreeCAD / Python süreci yok.
Paketin kaynaklarının son yazımı üretim başlangıcından (08:38:52) önce: `rehber_uret.py` 07:33:37, `rehber_kablo.py` 07:52:31,
`rehber_metin.py` 08:29:35, `rehber_denetim.py` 08:30:23, `rehber_kritik_onay.json` 08:30:40, `planlama/adim3/` en son 03:14:00
(`kablolar.md`). Yani çıktılar bugünkü kaynaktan üretildi. Paket dışı 14 dosyanın SHA-1'i üretimden önceki kayıtla aynı (yeniden
yazılmadı); zincirden sonra da aynı.

**FreeCAD kilidi:** üretimin FreeCAD aşaması (veri 178 s) için ajan U aldı, aşama bitince "boş"a döndürdü (kilit dosyasının son yazımı
08:42:05). Zincirin hiçbir adımı FreeCAD açmıyor (`carpisma_kos.py kontrol` yalnız özet karşılaştırır); kilide dokunulmadı. Son hâli
"boş". FreeCAD'in Python'u `-B`'ye karşın dört `__pycache__` yazdı (`planlama/adim4`, `tasarim/freecad`, `tasarim/freecad/lale158`,
`tasarim/freecad/rehber`; 08:38–08:41, gitignore'da, içlerinde yalnız `.pyc`); iş sonunda silindi.

### Ön sınama (FreeCAD'siz, ajan U, 08:37:49–08:38:31)

`kablolar_uret.py --kontrol`, `kablolar_denetim.py`, `rehber_denetim.py --kaynak`, `rehber_kablo.py`, `rehber_kol_kablo.py --yazma`,
`node --check rehber/app.js`: hepsi çıkış 0 (loglar geçici klasörde). Üretimin ön sınama satırı: "kaynak denetimi gecti, onay kaydi
tutuyor (kablo 100, liste 198, metin 1000)".

### Zincir

| Sıra | Komut | Başlangıç | Çıkış | Süre (s) | Beklenen | Ölçülen |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rehber_uret.py` (tam) | 08:38:52 | 0 | 2562 | çıkış 0 | çıkış 0; "ek kontrol sorunlu: -"; tarayıcı 50 / 50, konsol hatası 0 |
| 1 | parça / şema / alt adım | | | | 1192 / 49 / 71 | 1192 / 49 / 71 (71 geçti) |
| 1 | kablo eşleme | | | | GEÇTİ, 51 / 23 | "kablo esleme: GECTI" |
| 1 | denetim | | | | elektrik 0 | ASCII 0, elektrik 0, zorunlu uyarı eksik 0 / 108, yasak 0 (istisna 10) |
| 1 | uçuş / sıra / giriş / perdelenme | | | | hata 0 | 340 satır, çarpışan 0, istisna 16; 565 bağlantı ulaşılamaz 0; girilemez 0; gerekçesiz 0, istisna 117 |
| 1 | PDF | | | | 80 ± 1 sayfa, taşan yok, ≥ 8,0 pt | **80 sayfa** (adım 50 + devam 30), taşan yok, en küçük yazı DOM / PDF 8,1 pt, 16165 kB, eşleme tutarlı |
| 1 | PDF tamlık | | | | eksik 0, yineleme 0 | 50 adım, `is_` 32017 karakter, eksik 0; madde 404, eksik 0; **yineleme 0** |
| 2 | `rehber_kablo.py --veri …` | 11:03:11 | 0 | 1 | GEÇER, bilgi 6 | SONUÇ GEÇER; 51 / 23; geometri hata 0, **bilgi 6**; ayırt edilemeyen 0; onay tutuyor; eşlemesiz çizim 0 |
| 2 | `rehber_kablo.py --bozma-denemesi --veri …` | 11:03:12 | 0 | 8 | yakalanır | 52 / 52 (44 kaynak + 8 veri) |
| 3 | `rehber_denetim.py` (veri) | 11:03:20 | 0 | 1 | elektrik / yasak 0 | ASCII 0, elektrik 0, zorunlu eksik 0 / 108, yasak 0, parça 1192, şema 49 |
| 4 | `F10f-dogrula.py` | 11:03:20 | 0 | 577 | GEÇTİ | GEÇTİ (veri, sınama, kablo kare, sağ / sol, mini etiket) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 11:12:57 | 0 | 881 | çıkış 0, `renk_demo` önceki gibi | GEÇTİ; `renk_demo` KALDI (karar; önceki paketle aynı, bilinen kayıt) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 11:27:38 | 0 | 726 | GEÇTİ | GEÇTİ; konum 121, masa yabancı şema 0, 360 px taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 11:39:44 | 0 | 436 | GEÇTİ | GEÇTİ; seçim 6 / 6, yazdırma kareleri 50 / 50, PDF görüntü 121, boş sayfa yok, dış istek 0, konsol 0 |
| 8 | `F9b-dogrula.py` | 11:47:00 | 0 | 5 | GEÇER | GEÇER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 11:47:05 | 0 | 0 | 17 dosya aynı | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 10 | `regresyon.py --yazma` | 11:47:05 | 0 | 0 | aynı | GEÇER, 10 değer aynı |

Zincir 2–10 `.durum`: "BITTI cikis 0 sure 2634 enaz 2.48". **Bellek:** en düşük boş fiziksel bellek üretimde 2,86 GB (170 ölçüm),
zincirde 2,48 GB (174 ölçüm); bekçi tetiklenmedi.

### Sapmalar ve nedenleri

- Sapma yok: beklenen bütün sayılar tuttu, PDF 80 sayfa (P10.7b2a ile aynı) ve sayfa eşlemesi `4a097fb` PDF'iyle adım adım aynı
  (kayan adım yok).
- **Bilgi:** `--bozma-denemesi --veri` 44 → 52 (kaynak bozmaları 36 → 44, R8; veri bozmaları 8).
- **Bilgi, basılı yazı boyu:** K2 (adım 32) ilk sayfasında gövde yazısı 8,89 → **8,5 pt** (madde 5 uzadı, `sigdir()` küçülttü; alt
  sınırın üstünde, sayfa sayısı aynı). K1 (adım 17) ilk sayfası önceki gibi 8,5 pt. F1 (adım 33) kontrol listesi sayfası 9,1 → 9,49 pt
  (kontrol listesi yine tek sayfada).

### Kare bakışı (ajan U2, 11:48–11:50; kendi başsız Chrome'um, 1400 × 900, profil geçici klasörde)

Ekran: K1 (17), K2 (32), F1 (33), iki temada genel kare + panel sayfaları (DOM ölçümüyle) ve hedef cümleye kaydırılmış panel karesi.
Basılı: PDF sayfaları PyMuPDF ile 110 / 160 dpi. **Baktığım: 8 ekran karesi** (K1 makaron, K2 dört kablo / AU3, F1 G07 madde 1 ve
madde 3; her biri açık ve koyu) **ve 15 PDF sayfası** (K1 19–22, K2 42–43, F1 44–49, rastgele üç değişmemiş adım:
`random.Random(1582)` → adım 13 B5 s. 14, adım 15 B6 s. 17, adım 27 E2c s. 32). Panel sayfa kareleri (17 + 10 + 10, iki tema) çekildi,
tek tek bakılmadı; onların yerine panel metni DOM'dan okundu.

| Kare | Tema | Gördüğüm |
| --- | --- | --- |
| Panel metni (3 adım, DOM) | açık, koyu | Çözülmemiş yer tutucu **0** (`{…}`, `⟦`, `⟧` yok); panel dışına taşan / kesilen öğe 0 |
| K1 G07 paragrafı (ekran) | açık, koyu | "… (lehimden sonra geçmez). Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada tut (…). Direnci telin ucuna lehimle." sırası doğru, tam, kesik yok |
| K2 madde 5 (ekran) | açık, koyu | Dört kablo (U03, H02, S10, G17) → AU3 enerjisiz + damarı bul → lehim (+ → L+, − → L−) → kutup kontrolü → "Sonra dikişleri sık." tam ve sırada |
| F1 kontrol (ekran) | açık, koyu | G07'nin üç maddesi üç ayrı onay kutusunda (liste sırası 3, 4, 5; DOM metni 631 / 829 / 888 karakter, kaynakta 631 / 831 / 888: fark kod biçimli dosya adının işaretleri), ayrı ayrı okunuyor; kapı ("dışındaysa burada dur"), bant kuralı, "Kusuru düzeltince … baştan yinele" ve "kusur bulunmazsa da devam etme" yerinde |
| Basılı K1 s. 19 | — | Başlık, kare, "Karede:" satırı 5 sınıf (12 V, toprak, anahtarlı bara / motor, acil stop, sinyal); makaron cümlesi "Direnci telin ucuna lehimle"den önce; sayfa sonunda "İş metni yarım kaldı: devamı sonraki sayfa (K1, adım 17) →" |
| Basılı K1 s. 20–22 | — | s. 20 "← K1 iş metni: önceki sayfa sonunda yarım kalan yer burada sürüyor", madde 5 sonu–8 tam, yineleme yok; s. 21 kontrol listesi iki sütun, sığıyor; s. 22 kablo kancası, erişim |
| Basılı K2 s. 42–43 | — | s. 42 "Karede:" satırı 6 sınıf (HDMI, USB, analog ses, 12 V, servo 6 V, sinyal); madde 5'in son üç cümlesi sırada, sayfada tam (devam sayfasına bölünmedi); s. 43 kontrol listesi, kablo kancası, erişim; yineleme yok |
| Basılı F1 s. 44–49 | — | s. 44 iş metni (F1'de "Karede:" satırı yok, `4a097fb` PDF'inde de yok); s. 45 parça tablosu; s. 46 kontrol listesi tek sayfada, G07'nin üç maddesi ayrı kutularda, sığıyor; s. 47–49 alt adım kartları |
| Basılı rastgele s. 14, 17, 32 | — | Sığıyor, okunuyor, değişiklik izi yok |

**Zor okunan / yanıltıcı kareler: 3** (üçü de önceden bilinen, bu paketin işi değil) — K1 iş metninin madde 1–3'ü uzun tek paragraf
(ekran ve basılı); F1 "İlk enerji, aşama 1" kontrol maddesi 2322 karakterlik tek paragraf; F1 kablo kancasının ikinci maddesi
"… ana anahtarın saplama ölçüsü ve pabucu teslimde" diye yarım cümleyle bitiyor (veride de böyle; basılı ya da ekran kesiği değil,
kaynak metni).

### Üretimin ve zincirin yazdığı dosyalar

Üretim: `rehber/veri/rehber-veri.json` / `.js`, `planlama/rehber/goruntu/adim-06.png`, `adim-31-01.png`, `adim-36-02.png`,
`adim-41-06.png`, `planlama/rehber/kontrol.json`, `Lale-montaj-rehberi.pdf`. Zincir: `planlama/d158/F10{a,d,e,f}-dogrula.json`
(PDF, `kontrol.json`, veri zincirde değişmedi, SHA-256 önce / sonra aynı). Paket dışı 14 dosya yeniden yazılmadı. `git status`
zincirden önce 33, sonra 37 satır (+4 doğrulama JSON'u).

### Doğrulanamayanlar

- PDF'in görünüşü PyMuPDF görüntüsünden; kâğıda basılmadı.
- Panel sayfa karelerinin çoğuna gözle bakılmadı (metin DOM'dan okundu); hedef cümle kareleri dışında ekran görüntüsü tek tek incelenmedi.
- Üretimi (08:38–09:21) ben koşmadım; sayıları `uret1.log` / `uret1.durum` / `kontrol.json`'dan okudum.
