**KAYNAK GEÇER** (üretim adımına geçilebilir; "üretimden önce düzelmeli" sınıfında madde yok, aşağıdaki açık işler kayıtlı gidebilir)

# F10h ikinci bağımsız kontrol: P10.7b1 düzeltme turu 1, kaynak düzeyi

- Tarih: 2026-11-14, 10:43 (saat okundu). Dal `lale-duzeltme`, HEAD `8134519`; değişiklikler çalışma ağacında.
- Yöntem: kaynak okuma + depoda yalnız okuyan koşular + kendi geçici kopyamda bozma denemeleri (`py -3 -B`, önbellek kapalı).
  FreeCAD, `rehber_uret.py`, başsız tarayıcı koşmadı. Boş bellek koşular boyunca 1775–1841 MB.
- İlk kontrolün (`F10h-kontrol.md`) "doğru" hükümleri ve ajanın sayıları baz alınmadı; her sayı yeniden ölçüldü.
- Kontrol süresince depoda değişen dosya yok: 147 dosyanın başlangıç (10:23) SHA-256'sı ile bitişteki aynı; `git status` 32 satır,
  başta da 32. `kod/`, `main`, `pin-haritasi.md`, `rehber/veri`, `rehber/goruntu`, `planlama/rehber`, CAD kaynakları HEAD'e göre fark 0.

## 1. Kısa sonuç

Rehberin bugünkü metni ve tablo tarafı doğru: 181 yer tutucunun hepsi cümlenin anlattığı kayda bakıyor, çözülmüş metinde yanlış değer,
biçim bozukluğu ya da boş değer yok. Ü1, Ü2, Ü3 kapandı. Devre değerleri (`kablolar.json` uçları, GPIO, koruma, kesit, acil stop) HEAD
ile aynı. Bozma denemeleri ise yeni denetimin güvencesinin günlükteki "42 / 42"den dar olduğunu gösteriyor: benim 46 denememin 24'ü
kaçtı (22'si zararlı). Bu bugünkü çıktıyı bozmaz (üretim aynı kaynaktan, aynı metni yazar), ama bir sonraki metin düzenlemesinde
yanlış değeri durduracak bir bekçi yok. Bu yüzden açık iş olarak, P10.7b2'deki ilk metin değişikliğinden önce kapanması önerilir.

## 2. Üretimden önce düzelmeli

Yok.

## 3. Kayıtlı açık iş olarak gidebilir

Her madde: yer · nasıl ölçtüm · önerilen düzeltme.

### 3.1 Denetim delikleri (yer tutucu sistemi ve elektrik denetimi)

1. **Bozuk yer tutucu sessizce geçer.** `rehber_deger.py:33` deseni `\{([a-z_]+)\.([^{}\s]+)\}`; `coz` (`:141-152`) yalnız eşleşeni
   çözer. `{A.F6}` (B20) ve `{a. F6}` (B21) metinde olduğu gibi kalır, `kaynak_denetle` "çözülemeyen yer tutucu 0" der; kâğıda çıplak
   süslü parantez basılır. Ölçüm: kopyada iki biçim, ikisi de kaçtı. Öneri: çözülmüş metinde `{`, `}` ya da `⟦` kalıyorsa hata
   (`rehber_denetim.py` `kaynak_denetle`, tek satır).
2. **Aynı türden yanlış anahtar yakalanmaz.** Bir değerin yerine aynı türden başka bir anahtar yazılınca (kesit yerine kesit, GPIO
   yerine GPIO) denetim bunu fark etmez, çünkü kural yalnız cümlede bir kablo kimliği ya da sigorta etiketi varsa çalışır. Kaçan
   denemeler:
   - B06: acil stop hattı 22 AWG.
   - B07: saplama 4 yerine 3.
   - B08: ön şarj süresinin ikinci anılışı.
   - B09: bara durumunun ikinci teyidi GPIO23.
   - B10: taban direnci 270 Ω.
   - B36: KT3 köprüsü 16 AWG.

   Ölçüm: 6 / 6 kaçtı. Öneri: anahtar ↔ izinli adım / cümle çapası tablosu. Örnek: `ms.onsarj` yalnız "ön şarj" ya da "bekle"
   yanında, `gpio.BARA_DURUM` yalnız "PC817 #2" ya da "bara" yanında geçebilsin.
3. **Çıplak sayı kuralı büyük harfe duyarlı.** `rehber_denetim.py:812-813`: bağlam desenlerinde ("ön şarj", "bekle") `re.I` yok. Cümle
   başında "Ön şarj direnci 10 Ω" yazılırsa yakalanmaz (B11). Öneri: `ciplak_sayilar` (`:836`) aramasına `re.I`.
4. **Birim ve satır atlatmaları.**
   - B15: "500 mA" ve B16: "kA" geçer, çünkü `:810` deseni yalnız ` ?A\b`.
   - B18: etiket ile değer arasında satır sonu varsa (`:830` cümle bölmesi) kural çalışmaz.
   - B14b: değer sözle yazılınca geçer. Benzeri B14 yalnız ASCII sözlüğü sayesinde, rastlantıyla yakalandı.

   Öneri: desen `\d+(?:,\d+)? ?[mk]?A\b`; bölmeden önce satır sonlarını boşluğa çevir.
5. **Yük bağlamı muafiyeti fazla geniş.** `rehber_denetim.py:817` `CIPLAK_YUK` içinde "sürekli", "anma", "ölç\w*" ve "sınır\w*" var.
   "F3 sürekli 7,5 A" gibi yanlış bir sigorta değeri muaf geçer (B34). Öneri: yalnız `yük\w*|tüketim\w*|varsayı\w*` kalsın. Sigorta
   bağlamı kelimesi (F1–F6, mini, bıçak) aynı yan cümledeyse muafiyet uygulanmasın.
6. **MOSFET / WAGO pencereleri affettirir.** `rehber_denetim.py:702-707`: ±30 karakterde "değil", "eski" ya da "yerine" ("yok",
   "seçenek", "almaz") geçerse terim serbest kalır. Ajanın kendi M10 / M11 örnekleri yakalanıyor, ama benim cümlelerim kaçtı:
   - B29: "MOSFET sürücü kullan, BJT değil".
   - B30: "WAGO düğümü kullan; bu adımda boş yuva yok".

   Öneri: istisna yalnız terimin kendisini olumsuzlayan kalıpta geçerli olsun ("MOSFET değil", "MOSFET yerine", "WAGO yok"; terim ile
   istisna sözcüğü arasında en çok 2 sözcük).
7. **ZORUNLU öğeleri ön ek eşleşmesiyle olumsuzu da kabul eder.** `rehber_denetim.py:144-224`: B26 ve B27'de "tak" → "takma"
   yapıldı; desen kelimenin başını tuttuğu için zorunlu uyarı "var" sayıldı. Öneri: ZORUNLU desenlerinin fiil sonuna `\b`, ayrıca
   `(?!ma\b|me\b)` eklenmesi.
8. **Açık karar ve Ö4 kuralları sözcük affıyla geçer.**
   - B28: K52 kimliği, "karar bekliyor" sözüyle birlikte silinirse kural tetiklenmez (`:709-711` yalnız kimlik varsa bakar). Sonuç:
     açık kararın rehberden sessizce düşmesi yakalanmıyor. Yalnız `ZORUNLU` (`:216-217`) kendi cümlesini arar; B28'de o cümle silinmedi.
   - B38: "Ö4 köprüsüz bırakılır; röle çekmez" kuralı geçer. `:712` "çekmez" sözcüğü aynı cümlede olduğu için affeder; B38 yalnız
     ASCII sözlüğü sayesinde, rastlantıyla yakalandı.

   Öneri: K52, K60 ve K61 için kimlik varlığı `ZORUNLU` listesine eklensin; Ö4 kuralında "çekmez" affı "köprü yoksa röle çekmez"
   kalıbına daraltılsın.
9. **Çıplak sayı muafiyetini sınayan yok.** `CIPLAK_MUAF` (`rehber_denetim.py:818-820`) denetimin içinde. Listeye madde eklenmesi
   (B33) denetimin bir sınamasını tetiklemez. Öneri: `--bozma-denemesi` muaf listesinin uzunluğunu (1) sabitlesin.
10. **Kablo tablosunda yük daraltması yanlış sigortayı saklar.** `planlama/adim3/kablolar_denetim.py:2092`. Bellekte 8 deneme yaptım,
    5'i kaçtı:
    - K1: G22 notu "Hat sigortası 3 A (yük çok az)".
    - K2: "Kafa yükü için 10 A sigorta".
    - K3: "10 A (yük varsayımı)".
    - K6: "Sigorta 10 A, çeker".
    - K8: "Sigorta 7,5 A, tüketim 2 A".

    Bağlamsız kontrol (K4) ve başka yan cümle (K5) yakalandı. K7 yalnız "Yük" büyük harfle yazıldığı için desen tutmadı ve öyle
    yakalandı; bu tutarsız bir koruma. Bugünkü tabloda bu biçimde yanlış değer yok: `koruma` alanları HEAD ile aynı. Öneri: sigorta
    sözcüğü ya da F etiketi aynı yan cümledeyse daraltma uygulanmasın; yük sayısı ayrı bir sayı olarak (sigortanın ardında) kalabilir.

### 3.2 Geometrik eşleme sınaması

11. **Kaçan eşleme yanlışları.** `rehber_kablo.py:102-108` (`GEO_DAL`, `GEO_ISTISNA`) ve `:374-448` (`geometri_denetle`). 18 eşleme
    bozması denedim: 12 yakalandı, 6 kaçtı.
    - G1: yol 4 + M01. G3: yol 4 + G12. İkisi de `GEO_DAL` mirası yüzünden kaçtı; dal yolu ana yolun bütün noktalarını alıyor.
    - G4: yol 5 + S09. y ≥ 400'e ulaşan her yol, taban dışı her ucu kabul ediyor.
    - G6: yol 10 + G22. Ortak uç parçaları geçiriyor.
    - G7: yol 1 + G05 ve G8: yol 2 + G01. Modelsiz bara ve `PARCA_CAD` içinde XT60'ın akü kutusuna indirgenmesi geçiriyor.

    Bugünkü eşlemede bu türden yanlış yok. G13'ün yol 4'te durması geometriyle tutuyor: yol 4, yol 3'ten rölenin ve baranın aşağısında
    ayrılıp BTS sağ ile motorlara gidiyor. G19, B02, Q01 ve Q02'nin çizilmeyene, X01'in çizilene geçmesi doğru. Öneri:
    - Dal yolu yalnız ayrılma noktasından sonraki noktaları miras alsın.
    - "Taban dışı" kabulü için uç parça adı da eşleşsin.
    - Modelsiz düğümlerde (yıldız barası, acil stop düğümü) bilgi yerine "elle bakıldı" kaydı tutulsun.

### 3.3 Metin

12. **E4: çizim ile metin çelişiyor.** `rehber_metin.py:515-517` ve `:583-585`. Metin "USB ses kartı bu adımda takılmaz", ama alt adım
    deseni kartı içeriyor, yani animasyon kartı yerine uçuruyor. Köpük bant satırı ("yedek USB ses kartının yeri; kart takılmaz")
    bandın yapıştırılıp yapıştırılmayacağını söylemiyor. "Kutuda" sözcüğü aynı rehberdeki sigorta "kutusu" ile karışabilir. Çeliş
    kayıtlı (`karar-kuyrugu.md:1361-1362`, P10.7b2). Öneri: "kart takılmaz, yedek parça kutusunda durur; köpük bant da yapıştırılmaz"
    ve kartın E4 deseninden çıkması (CAD tarafı P10.7b2).
13. **K1 madde 8'deki "tek köprü" sözü.** `rehber_metin.py:285-286`: "(tek köprü madde 5'teki Ö4 yerinde)". Aynı adımda düğüm kartında
    `{kopru.A02}` tel köprüsü ve KT3 kutu giriş köprüleri de var; söz harfiyen yanlış okunabilir. Ölçüm: okuyarak, `:272` ve
    `:277-278` ile karşılaştırdım. Öneri: "(mantar zincirinde elle takılan tek köprü madde 5'teki Ö4 yeridir; düğüm kartındaki lehimli
    köprüler kartın parçası)".
14. **F5 parantezi iki türlü okunuyor.** `rehber_metin.py:1356-1357`: "(K2 devreye almadan {ms.k1_sonra} sonra zaten bırakıldı)".
    "devreye almadan" sözü "devreye almadan önce" diye de okunabiliyor. Öneri: "(K2, devreye alma sırasında K1 çektikten {ms.k1_sonra}
    sonra zaten bırakılmıştı)".
15. **Ö4 köprü telinin kesiti yazmıyor** (`rehber_metin.py:277-278`). Kayıtta da yok: A02 18 AWG, F5 2 A. Risk düşük. Öneri: "{awg.A02}
    tel" ya da kayda bir satır.
16. **Tek anahtar birden çok kabloyu temsil ediyor.** Bugün değerler eşit, ama tabloda biri değişirse metin sessizce kayar.
    - `{a.hat-A}` K1'deki "A ve B" için duruyor.
    - `{awg.G16}` G14–G16 için duruyor.
    - Yerleşim listesinde saplama başına yalnız ilk kablo yer tutucu; öbür kimlikler elle yazılmış.
    - KT3 köprü teli için `{awg.G01}` kullanılmış; G04 daha uygun.

    Öneri: her kimliğe kendi anahtarı ya da `rehber_deger`'de "eşit olmalı" sınaması.

### 3.4 Görünüm

17. **Renk ayrımı yalnız karşıtlıkla ölçülüyor, sınıflar arası uzaklık ölçülmüyor.** Kendi CIELAB ΔE76 hesabımda en yakın çiftler:
    - Açık tema: beyaz ↔ USB grisi 16,2; siyah ↔ HDMI 17,4.
    - Koyu tema: siyah ↔ HDMI 19,1; USB ↔ HDMI 19,9; siyah ↔ beyaz 20,1.

    Koyu temada "siyah" (toprak) sınıfı açık gri, "beyaz" sınıfı neredeyse beyaz çiziliyor. Ayırt edilebilir, ama 3B ışık altında
    karışma riski var. Öneri: `karsitlik_denetle`'ye sınıf çiftleri arasında en az ΔE eşiği (ör. 20) ve üretimde iki temada kare bakışı.
18. **Kesit kademeleri arasında en dar adım %16.** 3,1 → 3,6 mm, kuralın %15 eşiğinin hemen üstünde; 18 ve 16 AWG gözle zor
    ayrılabilir. Ölçüm: `KESIT_YARICAP` (`rehber_kablo.py:33`). Öneri: üretim karelerinde bakılsın, gerekirse 16 AWG 3,8.

### 3.5 Kayıt tutarlılığı

19. **`dongu-158.md:190`** "Bozma: kablo tablosu 138" yazıyor. Ek karardan (K01 teyite) sonra 139 (`F10h-gunluk.md:37`, `:166`, `:408`
    hepsi 139). Öneri: "138 (ek kararla 139)".
20. **`kablolama-on-kararlar.md:92`** "Kutu 6 yollu, F1–F5 beşini kullanıyor" o günün anlatımı; aynı paragraf (`:90`) F6'yı 6. yuvaya
    alıyor. Çelişki değil, ama satırın sonuna "(şimdi F6 da dolu)" eklenebilir.

## 4. Üretim adımında bakılacaklar

`F10h-gunluk.md` § 9 listesi sıra ve kapsam olarak yerinde. Ön sınamalar (1–6) zincirden önce, zincir son kod yazımından sonra başlıyor;
beklenen sayıların hepsini ben de ölçtüm (§ 5). Listeye ek:

1. **Veri modu denetimi** (zincir 3) çözülmüş metinde `{`, `}`, `⟦` kalmadığını gözle de doğrulasın; madde 3.1-1 düzelmediyse denetim
   bunu söylemez.
2. **Ön sınama 6** ("kontrolün kaçan 20'si") yalnız ilk kontrolün bozmalarını kapsıyor. Bu kontrolün 22 zararlı kaçağı (§ 5.4) sayılmadı.
   Açık iş olarak kayda geçmeli: 3.1 maddeleri.
3. **E4 karesi:** USB ses kartı animasyonda yerine uçuyor mu (madde 12). Uçuyorsa kart P10.7b2'ye dek ya desenden çıkmalı ya da metin
   "çizimde görünür, takılmaz" demeli.
4. **İki temada kare bakışı:** koyu temada toprak (açık gri) ↔ beyaz ses teli, açık temada beyaz sınıf ↔ USB grisi (madde 17); 18 / 16
   AWG kademesi (madde 18). Karşıtlık değerleri düz renkten hesaplandı, 3B ışıklandırma altında bakılmadı.
5. **FreeCAD Python'u:** `rehber_deger.py` yalnız standart kitaplık kullanıyor (`os`, `re`, `json`), f-string, `:=` ve `match` yok;
   dosyaları `encoding="utf-8"` ile açıyor. Kökü `__file__`'dan üç üst dizin olarak buluyor; bu, `rehber_kablo.py` ve `rehber_uret.py`
   ile aynı kalıp. FreeCAD içinde içe aktarım koşmadı (bakılmadı); üretimin ilk satırlarında "kablo esleme: GECTI" ve yer tutucu
   hatasının 0 olduğu görülmeli.
6. **`kontrol.json`**: `cizilen` 51, `cizilmeyen` 23, şema 49, parça 1192 (§ 9 tablosu). PDF sayfa sayısı lejant satırı yüzünden değişirse
   nedeni yazılsın.

## 5. Kendi ölçümlerim

### 5.1 Koşular (depoda, yalnız okuyan; hepsi çıkış 0)

| Koşu | Sonuç |
| --- | --- |
| `kablolar_uret.py --kontrol` | güncel |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / toplam 139, GEÇER |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER; çizilen 51, çizilmeyen 23 (liste ajanınkiyle aynı); geometri hata 0, bilgi 5; karışık sınıflı yollar 3, 5, 7; bozma 17 / 17 |
| `rehber_denetim.py --kaynak` / `--bozma-denemesi` | metin 530 (+ CAD 893, arayüz 552); ASCII, elektrik, zorunlu, yasak (istisna 5), çıplak, çözülemeyen hepsi 0; bozma 42 / 42 |
| `rehber_kol_kablo.py --yazma` | GEÇTİ, 38 bölüm, 36 s |
| `node --check rehber/app.js` ve `yazdir.html` satır içi betiği (kopyaya çıkarıldı) | ikisi de 0 |
| Rehber modülleri + `kablolar_denetim.py` + `kablolar_uret.py` sözdizimi (bellekte derleme) | 13 / 13 |

Kol kaynaklarının olmadığı geçici kopyada `rehber_kablo.py` "kol kesitleri türetilemedi" hatası verip 1 ile çıkıyor (sessizce
geçmiyor); ilk kontrolün 4. açık işi düzelmiş.

### 5.2 Ü1, Ü2, Ü3

- **Ü1:** `AD_CEVIRI` (5 kalıp) 1179 CAD parça kaydının ad ve kodlarında yalnız dört metne dokunuyor:
  - köpük bant,
  - USB ses kartı adı,
  - USB ses kartı kodu,
  - arayüz kartı kodu ("MOSFET" → "BC337-40 ×2 …").

  Çevirisiz elektrik bulgusu 4, çeviriyle 0. `rehber_veri.py:736-742` çevrilmemiş eski terimde üretimi durduruyor. Kapandı.
- **Ü2:** K1 `:277-278` Ö4 köprüsünü, "köprü yoksa röle çekmez" uyarısını ve "Ö4 karar bekliyor (K60)" sözünü taşıyor. Bunlar
  `kablolama-on-kararlar.md` § 8 ve O-6 ile, `karar-kuyrugu.md` K60 (açık) ile tutuyor. PC817 #1'in mantar serbestken LOW okuması pin
  haritasındaki "HIGH = mantar basılı / F5 attı" ile uyumlu. Kapandı (kesit eksik: madde 15).
- **Ü3:** eşleme geometriyle tutuyor (madde 11'deki yorum). Kapandı.

### 5.3 Yer tutucular

181 yer tutucu, türe göre ajanın sayısıyla aynı:

| Tür | Adet |
| --- | --- |
| a | 59 |
| awg | 46 |
| bicak | 21 |
| gpio | 20 |
| saplama | 11 |
| ohm | 7 |
| ms | 7 |
| kopru | 3 |
| ara | 2 |
| yuva | 2 |
| s | 2 |
| yeniden | 1 |

Hepsini bağlamıyla çözülmüş metinde tek tek okudum:

- Yanlış kayda bakan yok.
- "A A", "GPIO GPIO", boş değer ya da `None` yok.
- Bugünkü metinde bozuk biçimli yer tutucu yok.
- `rehber_deger.py` içinde gömülü değer tablosu yok; değerler `kablolar.json`, pin haritası § 9 JSON bloğu ve `elektrik.md`'den okunuyor.

Yeni cümleleri kayda karşı okudum; F5'teki sigorta kutusu dizilişi (uç yuvalarda F2 yedek ve F6) `elektrik.md:377-380` ve
`kablolama-on-kararlar.md:90-92` ile tutuyor. "Alçak profil mini (2 A, 7,5 A)" `kablo-tablosu-gunluk.md:549` ile aynı. KT3 atıfı
(`F5`, "ilk açılışta F6 atmamalı") kayıtla tutuyor. Ham metinde kalan 80 gerilim değeri ve ses / sonar bölücü dirençleri kayıtla çelişmiyor.

### 5.4 Bozma denemeleri: `rehber_denetim --kaynak` (kopyada)

46 deneme koştu (B02'nin kaynak cümlesi bulunamadı, koşmadı).

**Yakalanan (22):** B01, B03, B04, B05, B12, B12b, B17, B19, B23, B31, B32, B33k (kontrol), B37, B39, B40, B41, B42, B43, B38b ve
rastlantıyla yakalanan üç deneme:
- B14 ve B38: ASCII sözlüğü sayesinde.
- B22: denetimin çökmesi sayesinde.

**Kaçan (24):** B06, B07, B08, B09, B10, B11, B13, B14b, B15, B16, B18, B20, B21, B24, B25, B26, B27, B28, B29, B30, B33, B34, B35,
B36. Bunlardan B35 zararsız (aynı değer). B11 doğru değerin çıplak yazılması: zararlı değil, ama kural onu yakalamalıydı.

| Sınıf | Deneme | Madde |
| --- | --- | --- |
| aynı türden yanlış anahtar | B06, B07, B08, B09, B10, B36 | 3.1-2 |
| bozuk yer tutucu | B20, B21 | 3.1-1 |
| büyük harf, birim, satır sonu, sözle değer | B11, B15, B16, B18, B14b | 3.1-3, 3.1-4 |
| saplama çıplak (kural yok) | B13 | 3.1-2 |
| anlam ters (sıra; adımın başka alanı) | B24, B25 | 3.1-2 |
| ZORUNLU ön ek | B26, B27 | 3.1-7 |
| açık karar silme | B28 | 3.1-8 |
| MOSFET / WAGO penceresi | B29, B30 | 3.1-6 |
| muaf listesi | B33 | 3.1-9 |
| yük / "sürekli" muafiyeti | B34 | 3.1-5 |

### 5.5 Kablo tablosu

- Durum: kesin 20 / teyit 53 / karara bağlı 1 (`kablolar.md:10` ile aynı).
- `klemens-508` uçlu 11 kablo var; hiçbiri kesin değil. G07 ve A06 sonlandırmada 5,08 geçiyor ama uçları lehimli; ikisi de teyit.
- `kablolar.json`, HEAD'e göre:
  - 74 kimlik aynı.
  - Değişenler:
    - `teyit` 23 kayıtta.
    - `durum` 11 kayıtta: SV1–SV3, G18, G19, G22, A01, A02, A04, K01, K02.
    - `sonlandirma` 5 kayıtta: G17, A02, A04, K01, K02 ("lehimle köprülü" → "≥ 18 AWG tel köprüyle").
    - `klemens_yerleri` notu.
    - `renk_kurali.ilke`.
  - K04 notu aynı.
  - Uç, GPIO, koruma, kesit ve acil stop alanları değişmemiş.
- Yük daraltması: madde 3.1-10.

### 5.6 Görünüm

- **Karşıtlık:** kendi WCAG uygulamamla, `stil.css` zeminlerine karşı hesapladım. Zeminler: açık tema sahne #eceae4, kart #fff; koyu
  tema sahne #1b1c20, kart #202226. 11 ton × 2 tema × 2 zemin:
  - En düşük değer USB grisi, açık tema, sahne zemini: 3,47. Ajanın değeriyle ve `karsitlik_tablosu` ile aynı.
  - Hepsi ≥ 3,0.
  - Koyu temada toprak #b9bec5: 9,11 / 8,52. Açık temada sarı #8a6d00: 4,09 / 4,92; beyaz #4e6d7d: 4,58 / 5,52.
- **Ayırt edilebilirlik:** madde 17. Kırmızı ↔ turuncu ΔE76 27,9 (açık) yeterli.
- **Kalınlık:** 2,5 / 3,1 / 3,6 / 4,6 mm. Kol tüpleri `TBL.cizim` (`rehber_kol_kablo.py:410`) üzerinden tablodan, 22 AWG 2,5; inceltme yok.
- **Alan adları:** `rehber_kablo.Tablo.cizim` şu alanları yazıyor: `kablo`, `ks`, `kb`, `renk`, `r`, `rt`, `kt`, `karisik`.
  `lejant()` ise [renk, ad, ton] yazıyor. Okuyan taraflar:
  - `app.js` `kabloTon` (`:293`, `rt[tema]`), `lejant` (`:1247-1281`, `kablo_sinif`, "k:"+(kt||ks)) ve `kabloBilgi` (`kb`, `karisik`)
    aynı adları okuyor.
  - `yazdir.html:87` `rt.light` okuyor, `:97` `kablo_sinif` okuyor.

  Uyumlu.

### 5.7 Sayılar ve gizlilik

- Belgeler arası sayı tutarlı:
  - 51 / 23 çizilen / çizilmeyen.
  - 20 / 53 / 1 durum.
  - 74 kablo.
  - 139 kablo tablosu bozması (`dongu-158.md:190` hariç, madde 19).
  - 42 / 42 ve 17 / 17 bozma.
  - Eski sayılar (55 / 19, 22 / 51 / 1, 136, 49 / 54) tarihli girdilerde ve işaretli.
- Bu paketin eklediği 1411 satırda ve izlenmeyen üç yeni dosyada yerel kullanıcı yolu, makine adı, e-posta, anahtar ya da soyadı yok.
  Metinde geçen iki ad (proje sahibi ve yazılımcı) HEAD'de de vardı; rol adı olarak kullanılıyor.

## 6. Bakılmadı

- FreeCAD altında `rehber_deger` içe aktarımı ve tam üretim (yalnız statik inceleme: madde 4-5).
- Üretilmiş veri (`rehber/veri`) ve karelerde renk, ton, yarıçap; 3B ışıklandırma altında karşıtlık.
- Başsız tarayıcıda lejant ve bilgi kartının çizimi (yalnız alan adları ve sözdizimi).
- `F10f`, `F10e`, `F10d`, `F10a`, `F9b` doğrulayıcıları, `carpisma_kos.py`, `regresyon.py`.
- `kafa-yerlesim/uygulama_rapor.py` içindeki eski kablo adları (günlükte bilgi olarak yazılı; bu pakette dokunulmamış).
