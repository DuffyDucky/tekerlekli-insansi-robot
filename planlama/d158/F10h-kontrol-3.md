**DÜZELTME GEREKLİ** (tek madde: K1 madde 8'in "köprü yalnız şu yerlerde takılır" listesi anahtarlı baranın köprülerini dışarıda bırakıyor; geri kalan her şey kayıtlı açık iş olarak gidebilir)

# F10h üçüncü bağımsız kontrol: P10.7b1 açık işler turu (§ 12), kaynak düzeyi

- Tarih: 2026-11-14, 11:34 (saat okundu). Dal `lale-duzeltme`, HEAD `8134519`; değişiklikler çalışma ağacında.
- Yöntem: bugünkü kaynağın taze kopyası (geçici klasörümde, `kopya2`), `py -3 -B`, önbellek kapalı; depoda yalnız okuyan koşular.
  FreeCAD, `rehber_uret.py`, başsız tarayıcı koşmadı. Boş bellek 1517–3869 MB.
- Ajanın § 12 iddiaları baz alınmadı; her sayı yeniden ölçüldü. Bozmalar yalnız kopyada; her bozmadan sonra dosya ve onay kaydı özeti
  geri doğrulandı (SHA-256 aynı).

## 1. Kısa sonuç

Ajanın sayıları tutuyor: B takımı onay kaydıyla 47 / 47, onaysız 44 / 47 (B09, B24, B25 yalnız onayla); G takımı geometriyle 17 / 18,
onayla 18 / 18; K takımı 8 / 8. Renk ve karşıtlık değerleri kendi CIEDE2000 hesabımla aynı. Onay kaydı bozuk / yok / boş olunca sessiz
geçmiyor, olağan koşu kaydı yazmıyor. Ama iki şey var:

1. **K1 madde 8'deki yeni köprü listesi kayıtla çelişiyor** (montajcıya yanlış iş yaptırır; § 2).
2. **Onay kaydının kapsamı anahtar sözcüğe bağlı.** Kayıt, metindeki cümlelerin yalnız `KRITIK_SOZ` taşıyan ya da yer tutucu / zorunlu
   uyarı içerenlerini tutuyor. Kişi güvenliği ve sıra cümleleri dışarıda kalıyor. 17 yeni kapsam / atlatma bozmamın 5'i her
   mekanizmadan tamamen kaçtı, 4'ü yalnız ASCII sözlüğü sayesinde rastlantıyla yakalandı; onay kaydı 17'nin 7'sini tuttu (§ 3.1). Bu, brief'in "sessiz değişikliği imkânsız kılar"
   iddiasını bugün karşılamıyor; açık iş.

## 2. Üretimden önce düzelmeli

1. **K1 madde 8: anahtarlı baranın köprüleri "yalnız" listesinde yok.** `tasarim/freecad/rehber/rehber_metin.py:286-289`: "Bu adımda
   köprü yalnız şu yerlerde takılır: Ö4 yerindeki kısa tel köprü (madde 5), acil stop düğüm kartındaki (A02, A04) {kopru.A02} tel köprü
   (madde 5), yıldız barasının saplamaları arasındaki {kopru.yildiz} köprü (madde 2) ve KT3 … ara kablolar".
   - Kayıt: `planlama/adim3/kablolar.json` `klemens_turleri.bara-pabuc.kopruler` iki köprü takımı yazıyor: "Yıldız barası · GND" (4 ×
     12 AWG siyah) ve **"Anahtarlı bara · +" (3 × 12 AWG kırmızı, 50 mm)**; aynı kaydın `not` alanı: "Köprüler: yıldız 4 + anahtarlı
     bara 3 = 7 adet 12 AWG".
   - Rehberde anahtarlı bara köprüsü hiçbir yerde açıkça yazmıyor (madde 2'deki "saplamalar arası {kopru.yildiz} köprü" iki barayı da
     kapsıyor gibi okunuyordu; bu boşluğu ikinci kontrolde ben de görmedim). Yeni madde 8 ise listeyi "yalnız" sözüyle kapatıp
     köprüyü açıkça yıldız barasına bağlıyor. Harfiyen uygulayan montajcı anahtarlı baranın 4 saplamasını köprülemez; BTS7960B ve XL4016
     A / B / C'nin saplamaları besleme saplamasından ayrık kalır.
   - Ölçüm: `rehber_metin.py` içinde "köprü" ve "anahtarlı bara" geçen bütün satırları okudum (köprü: :261, :272, :278, :286-289, :304-305,
     :458; anahtarlı bara: :217, :259, :263-264, :291, :722, :726, :1363, :1615-1621); `rehber_deger.py`'de anahtarlı bara köprüsü için yer
     tutucu yok (yalnız `{kopru.yildiz}`, `:104-105`).
   - Öneri: madde 8 listesine "anahtarlı baranın saplamaları arasındaki 3 × {kopru.bara} kırmızı köprü (madde 2)"; madde 2'de iki baranın
     köprüsü ayrı ayrı. `rehber_deger.py`'ye `{kopru.bara}` (`kopruler["Anahtarlı bara · +"].awg`). Değişiklik onay kaydını yeniler; bu
     cümle bağımsız kontrole gider. Devre değeri değişmez.

## 3. Kayıtlı açık iş olarak gidebilir

### 3.1 Onay kaydının kapsamı (yeni bozmalar, kopyada)

Kapsam kuralı: `rehber_denetim.py:948-951` (`KRITIK_SOZ`), `:985-994` (girdi seçimi). Metin cümlelere `_CUMLE_GENIS` ile bölünüyor
(`:268`; `;` bölmez). Kayda girmeyen cümle serbestçe değişir; kayıt bir alandaki kritik cümlelerin **sırasını kendi aralarında** tutuyor,
kritik olmayanlara göre yerini değil (`rehber_kritik.py:64-67`).

| Kod | Bozma | Onay | Öbür kural | Sonuç |
| --- | --- | --- | --- | --- |
| N01b | F5: "dönen tekere el uzatılmaz" → "uzatılabilir" | kaçtı | yok | **tamamen kaçtı** |
| N01 | aynı cümle: "dönen tekeri elle durdurarak dene" | kaçtı | ASCII ("tekeri") | rastlantı |
| N03 | K1: "Kabuk takılmadan önce burada dur" → "takıldıktan sonra" | kaçtı | yok | **tamamen kaçtı** |
| N04 | K1 Ö4 ardına "Bu maddeyi şimdilik atla." | kaçtı | ASCII ("atla") | rastlantı |
| N04b | K1 Ö4 ardına "Bu maddeyi şimdilik yapma." | kaçtı | ASCII | rastlantı |
| N04c | K1 madde 7 ardına "Yukarıdaki listeye uyma." | kaçtı | ASCII | rastlantı |
| N05 | F5: "Bu adımdaki sıra kaynakta yok, doğrulanmadı." silindi | kaçtı | yok | **tamamen kaçtı** |
| N07 | K1 madde 7 ardına "Önce kabuğu kapat." | kaçtı | yok | **tamamen kaçtı** |
| N11 | F5: "Mantarı bırak …" ile "Motor yön testi …" yer değiştirdi | kaçtı | yok | **tamamen kaçtı** |
| N02 | F5: "Saat, yüzük, bileklik çıkar" → "takılı kalabilir" | yakaladı | — | |
| N06 | F5: erişim alanında "kimse yok" → "bir yardımcı kolları tutar" | yakaladı | — | |
| N08 | `AD_CEVIRI`: "(yedek, takılmaz)" → "(yedek, E4'te takılır)" | — | elektrik (terim) | yakalandı |
| N09 | `SEMA` ESP32 USB: 1N5819 anot / katot ters | yakaladı | — | |
| N10 | K1 Ö4 cümlesi iki cümleye bölündü | yakaladı | — | |
| N12 | K1 madde 8'e kontrol cümlesinin kopyası | yakaladı | — | |
| N13 | K1 madde 8: yıldız barası köprüsü listeden silindi | yakaladı | — | |
| N15 | F5: "Kollar aşağıda başlar" → "yukarıda" | yakaladı | zorunlu | |

Tamamen kaçan 5 (N01b, N03, N05, N07, N11); N01 ve N04 ailesi (4) ASCII sözlüğü genişletilince kaçar. ASCII sözlüğü bir bekçi değil: gerçek
düzenlemede yeni kelime sözlüğe eklenir (bu turda 8 kelime eklendi, § 12.4).

- Öneri: kayıt anahtar sözcükle değil, **her adımın görünen bütün alanlarının bütün cümleleriyle** (530 metin; bugün 319'u kayıtta) ya da
  alan başına tek özetle kurulsun. Kayıt zaten yalnız özet tutuyor, maliyeti küçük; bir yazım düzeltmesi de onay ister, ama brief'in
  amacı tam olarak bu. Kritik olmayan cümle değişiklikleri "uyarı", kritikler "hata" diye ayrılabilir.
- Kayıt CAD ad / kod çevirisini ve arayüz metinlerini (app.js, yazdir.html) içermiyor (`kritik_girdiler` yalnız `kaynak_metinler`);
  N08 elektrik kuralıyla yakalandı, kayıtla değil.

### 3.2 Onay kaydının kendisi (kopyada; `rehber_denetim.py --kaynak`)

| Durum | Sonuç |
| --- | --- |
| dosya yok | çıkış 1, "onaylı kritik girdi farkı 1" (kayıt yok satırı) |
| bozuk JSON | çıkış 1, **traceback** (`rehber_kritik.oku` → `json.load`); `rehber_kablo.py` de traceback |
| boş dosya | çıkış 1, traceback |
| `{}` / `{"bolumler": {}}` | çıkış 1, fark 528 |
| `metin` bölümü yok | çıkış 1, fark 319 |
| aynı yerde iki girdinin sırası ters (K1 is_) | çıkış 1, fark 2 |
| yerler arası blok sırası (özetler aynı) | çıkış 0 (doğru: anlamsız) |
| yalnız okunur `bas` alanı elle değişti | çıkış 0 (doğru: özet tutuyor; ama fark satırı bu alanı gösteriyor, aşağıda) |

- Sessiz geçiş yok. Bozuk JSON'da düzgün ileti yerine traceback (`rehber_kritik.py:34-37`): öneri `try / except ValueError` → "kayıt
  okunamadı" hatası.
- Fark satırı eski hâli dosyadaki `bas` alanından (ilk 60 karakter) yazıyor (`rehber_kritik.py:76`); `bas` elle değiştirilirse eski hâl
  yanlış gösterilir, karar yine özetten. Ajan da bildirmiş; öneri: kayda tam metni (ya da en az değişen bölgeyi) yazmak.
- **Olağan koşu yazmıyor:** depoda `rehber_denetim.py --kaynak`, `--bozma-denemesi`, `rehber_kablo.py`, `--bozma-denemesi` koşuları öncesi
  ve sonrası `rehber_kritik_onay.json` SHA-256 ve değişiklik zamanı aynı; `__pycache__` oluşmadı.
- **Üretim zincirinde yeri:** `F10h-gunluk.md` § 9 madde 3-4 ve `:178-182` ön sınamada, zincirden önce: doğru. Ama `rehber_uret.py` ve
  `rehber_veri.py` kaydı hiç okumuyor (grep: "kritik", "onay" yok); ön sınamadan sonra metin değişirse üretim fark etmez. Kural "zincir son
  kod yazımından sonra" bunu yazılı olarak kapatıyor. Öneri: `rehber_uret.py` başında `kritik_fark()` çağrısı (FreeCAD'siz, standart
  kitaplık).

### 3.3 Öbür bulgular

1. **B22 hâlâ traceback.** `kablolar.json`'da koruyucu adı değişince denetim çöküyor (çıkış 1, yakalanıyor ama ileti yok). Ajan bildirmiş;
   öneri: `rehber_deger.py:149` `KeyError` çözülemeyen yer tutucu olarak yazılsın.
2. **G takımında geometrinin kaçırdığı yeni dört bozma** (onay kaydı hepsini yakaladı): G19 yol 4 + G08, G20 yol 4 + G10 (dal "gövdesi" ana
   yolun ayrılma noktasına kadarki bölümünü aldığı için röle / bara uçlu kablolar dala da uyuyor), G24 yol 10'da A03 yerine G22 (ajanın
   yazdığı ayırt edilemeyen çift), G26 yol 1'den G02 çıkarıldı (geometri eksik eşlemeyi sınamıyor; sayım 51 → 50 olurdu). Ölçüm: 26 deneme,
   geometri 21, onay 26. Kalıcı bir yanlışa yol açmıyor (eşleme tablosu kayıtta); açık iş.
3. **`TABAN_DISI_BOLGE` gövde bölgesi geniş** (x −260…260, y 400…1280): ajan da yazmış. G4 / G5 / G22 / G23 bugün kol bölgesiyle
   yakalanıyor; gövde içi uçlar (USB hub) bugün eşli değil.
4. **Ö4 köprü teli** `{awg.A01|A02}` = 18 AWG; A01 ve A02 kayıtta 18 AWG (`kablolar.md:100-101`); Ö4 yeri A02'nin üstünde (A02
   `sonlandirma`: "mantar vidası → Ö4 için iki uçlu yer … köprülü"). Doğru.
5. **F5 cümlesi** (`rehber_metin.py:1362-1363`): "K2, devreye alma sırasında K1 çektikten {ms.k1_sonra} sonra zaten bırakılmıştı; E9 adım
   5" — `elektrik.md:457` "(5) 100 ms sonra GPIO19 = 0" ile aynı; `{ms.k1_sonra}` = 100 ms. Tek anlamlı. "E9 adım 5" aynı belgede "5. adım"
   (proje adımı) diliyle karışabilir; "E9 dizisinin (5) maddesi" daha açık olur (düşük).
6. **E4** (`:518-520`, `:587-589`): kart takılmaz, animasyondaki yerin eski tasarımdan kaldığı, köpük bandın yapıştırılmadığı, "kutuda"
   yerine "yedek parçalarla saklanır": `kablolama-on-kararlar.md` § 5 Ö1 ile tutuyor. Animasyonda kartın köpük bandı da uçuyor
   (`gizli_ok` "Köpük bant (USB ses"); cümle yalnız kartı anıyor (düşük). Kartın desenden çıkması P10.7b2'de kayıtlı.
7. **§ 12.4'teki öbür çiftler** (K1 madde 1, 3, 5, yerleşim, kontrol ana hat, Teslimde, KT3, E3a, K2 kontrol, F1 / F5 G22, F5 not_): hepsini
   bugünkü dosyada okudum; anlam değişmemiş. Grup değerleri kayıtla aynı: yerleşim grupları `kopruler["Yıldız barası · GND"].yerlesim`
   (1: G12 / G14 / G15, 2: G13 / G16, 3: G05 / G06, 4: G17 / G18, 5: G20 / G22); `{awg.G04}` (KT3) = 12 AWG, G04 `sonlandirma` "kutu ayrı
   girişliyse 12 AWG kısa köprüler" ile aynı.
8. **K1 madde 8'in öbür üç köprüsü kayıtta var:** Ö4 (`kablolar.json` A02, `kablolama-on-kararlar.md` O-6), düğüm kartı (A02 / A04
   `sonlandirma` "≥ 18 AWG tel köprüyle"), yıldız barası (`kopruler`); KT3 ara kabloları G04 `sonlandirma`'da "köprüler" diye geçiyor.
   Uydurma yok; eksik yalnız § 2'deki.
9. **18 ↔ 16 AWG kademesi** (%16) değişmedi; § 9'da gözle bakış notu var.

## 4. Üretim adımında bakılacaklar

1. § 2 düzeltmesinden sonra onay kaydı yenilenir; yenilenen fark (yalnız K1 madde 2 / 8 cümleleri ve yeni `kopru.bara` anahtarı
   beklenir) bağımsız kontrole gider, sonra ön sınama baştan.
2. Ön sınama 6 (§ 9 `:175-176`): bu kontrolün N takımı (§ 3.1) eklenirse "onaysız" sayım değil, "kayıt dışı" sayım da yazılsın.
3. İki temada renk bakışı: koyu temada siyah (#b3b3b3) ↔ USB (#818181) ↔ beyaz (#f2f6f7) grileri; açık temada siyah ↔ HDMI (#222222 ↔
   #1d3854). Değerler düz renkten; 3B ışık altında bakılmadı.
4. E4 karesi: animasyonda kart ve köpük bandı uçuyor mu; metin bunu söylüyor mu.

## 5. Kendi ölçümlerim

### 5.1 Bozma tablosu (taze kopya, `rehber_denetim.py --kaynak`)

"Onaysız" = onay farkı dışındaki kurallar (kayıt bozmayla birlikte yenilenmiş gibi); ASCII sözlüğü ayrı sayıldı (rastlantı).

| Takım | Deneme | Onaylı yakalanan | Onaysız yakalanan | Onaysız kaçan |
| --- | --- | --- | --- | --- |
| B (ilk tur, bugünkü metne uyarlanmış çapalar) | 47 | **47** | **44** (43 kural + B22 çökme) | B09 (iki varlık aynı cümlede), B24, B25 (sıra) |
| N (yeni: kapsam / atlatma) | 17 | çıkış ≠ 0: 12 (onay kaydı 7, elektrik 1, yalnız ASCII 4) | kural 2 (N08 elektrik, N15 zorunlu) + yalnız ASCII 4 | 5 tamamen: N01b, N03, N05, N07, N11 (§ 3.1) |
| G (eşleme; `geometri_denetle` + `onay_denetle`) | 26 (ilk 18 + 8 yeni) | **26** | geometri 21 (ilk 18'de 17) | G6, G19, G20, G24, G26 |
| K (kablo tablosu yükü, bellekte) | 8 + 7 yeni | — | ilk 8: **8 / 8**; yeni 7: beklenen 7 / 7 | yok |

- İlk turda yakaladığım 22 bozmanın hepsi hâlâ onay kaydı olmadan da yakalanıyor (B22 yine çökmeyle): yan cümle bölmesi (ondalık virgül)
  ve Türkçe küçük harf değişikliği eskiden yakalananı kaçırmıyor.
- K'nin yeni yedisi: meşru yük notları sessiz ("yük 1,5 A" G22, "tüketim 4 A" G17, "QLED yükü 0,9 A varsayım", "şarj akımı 7 A çeker"
  G06); zincir sigortasını aşan yük ("tüketim 6 A" G17, F3 5 A), "koruma 7,5 A, yük 2 A" ve eski muaf sözcük "Sürekli 10 A" alarm.
- Grup yer tutucusu (kopya `kablolar.json`): G15 18 AWG, S07 20 AWG, A02 16 AWG, G15'in saplaması 1 → 2, G04 10 AWG: beşi de
  "BOZUK YER TUTUCU … ⟦?…⟧" ve çıkış 1.
- Temiz kaynakta yanlış alarm 0 (kopyada ve depoda).

### 5.2 Koşular (depoda, yalnız okuyan)

| Koşu | Sonuç |
| --- | --- |
| `kablolar_uret.py --kontrol` | güncel, çıkış 0 |
| `kablolar_denetim.py` / `--bozma-denemesi` | GEÇER / toplam 145, GEÇER |
| `rehber_denetim.py --kaynak` | her kalem 0, onay farkı 0 (kayıt metin 319, liste 119, kablo 90), çıkış 0 |
| `rehber_denetim.py --bozma-denemesi` | 65 / 65, bozulmamış kaynakta 0 |
| `rehber_kablo.py` / `--bozma-denemesi` | GEÇER, çizilen 51 / çizilmeyen 23, geometri hata 0 / bilgi 4, ayırt edilemeyen 1, onay tutuyor / 27 / 27 |
| `node --check rehber/app.js` | 0 |

### 5.3 Renk (kendi CIEDE2000 uygulamam; Sharma 2005 1. sınama çifti 2,0425 tuttu)

| Tema | En yakın çiftler (ΔE00) |
| --- | --- |
| açık | siyah ↔ HDMI 15,3; beyaz ↔ USB 15,9; kırmızı ↔ turuncu 17,1; mavi ↔ beyaz 17,4; kırmızı ↔ CSI 18,0 |
| koyu | turuncu ↔ CSI 15,1; mavi ↔ HDMI 15,3; siyah ↔ beyaz 15,7; siyah ↔ USB 15,9; USB ↔ CSI 18,4 |

En düşük WCAG karşıtlığı 3,19 (açık tema USB #828282, sahne zemini). Ajanın tablosuyla aynı; hepsi ≥ 3,0 ve ΔE00 ≥ 15.

### 5.4 Değişmemesi gerekenler ve gizlilik

- `kod/`, `main`, `pin-haritasi.md`, `rehber/veri`, `rehber/goruntu`, `planlama/rehber`, kabuk / montaj Python kaynakları, `*.FCStd`,
  `tasarim/freecad/taban`, `montaj-analiz.json`: HEAD'e göre fark 0. `pin-haritasi.md` ve `F10h-kontrol.md` özeti 10:23'teki ile aynı;
  `F10h-kontrol-2.md` son değişiklik 10:45 (benim yazımım).
- `kablolar.json` HEAD'e göre fark ikinci kontroldeki ile aynı (teyit 23, durum 11, sonlandırma 5); uç, GPIO, koruma, kesit, acil stop
  alanları değişmemiş.
- Eklenen 1730 satırda ve `rehber_kritik.py`, `rehber_kritik_onay.json`, `rehber_kablo.py`, `rehber_deger.py`, `F10h-gunluk.md`'de yerel
  yol, makine adı, e-posta, anahtar yok.

## 6. Bakılmadı

- FreeCAD altında `rehber_kritik` içe aktarımı ve tam üretim (statik: yalnız standart kitaplık — `os`, `re`, `json`, `hashlib`, `difflib`).
- Kopyada `rehber_kablo.py` ana koşusunun onay satırı (kol kaynakları kopyada olmadığından ana koşu kol hatasıyla 1 çıkıyor); onay
  davranışı `onay_denetle()` doğrudan ve depoda ana koşuyla sınandı.
- Üretilmiş veri, kareler, 3B ışıkta renkler; tarayıcıda lejant.
- `taban-analiz.json` yeniden üretilince bölge ve nominal nokta tablolarının tutması.
