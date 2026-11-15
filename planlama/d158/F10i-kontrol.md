**DÜZELTME GEREKLİ**: kaynak denetimleri çıkış 0 ile geçiyor. Ama üç kablonun talimatı karta zarar verebilecek biçimde eksik ya da belirsiz: G22, X01 ve P01–P03. Ayrıca tamlık ve kontak denetimi, rehberden eksik ya da yanlış talimat kaldığında bunu yakalamıyor; bunu kendi bozma denemelerimle gösterdim.

# F10i (P10.7b2a) bağımsız kaynak kontrolü

- Kontrol eden: bağımsız inceleme ajanı (Opus). Uygulama ajanının günlüğündeki (`F10i-gunluk.md`) iddialara güvenmeden, kaynaktan ölçtüm.
- Taban: dal `lale-duzeltme`, HEAD `1328b60`. Uygulama ajanının bıraktığı commit edilmemiş çalışma ağacını inceledim: 15 değişmiş dosya, 1 yeni dosya.
- Saat: rapor 2026-11-15 01:55'te yazıldı (sistem saati).
- Depoya yazılan tek dosya bu rapor. Commit, push ya da `git add` yapılmadı. FreeCAD, `rehber_uret.py`, F10* doğrulayıcıları ve başsız tarayıcı koşulmadı. Bozma denemeleri depo dışındaki geçici bir klasörde, bellekte ya da kopya üzerinde yapıldı.
- Boş bellek denetim boyunca 1,2 GB sınırının üstündeydi: en düşük 3,3 GB, sonda 5,3 GB.

## 1. Koşular (kendim koştum)

| Komut | Çıkış | Sonuç |
| --- | --- | --- |
| `kablolar_uret.py --kontrol` | 0 | güncel |
| `kablolar_denetim.py` | 0 | tüm bölümler GEÇER (`yon_yer` dahil) |
| `kablolar_denetim.py --bozma-denemesi` | 0 | 156 / 156 |
| `rehber_denetim.py --kaynak` | 0 | kritik fark 0; tamlık 172 madde, eksik 0, muaf 21; 74 / 74 kablo; 95 görünür dizge |
| `rehber_denetim.py --bozma-denemesi` | 0 | 104 / 104 |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 32 / 32 |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GEÇTİ |
| 7 değişen `.py` dosyasının derlenmesi (`py_compile`; çıktı geçici klasöre yazıldı) | 0 | — |
| `node --check rehber/app.js` | 0 | — |

Günlükteki sayılar (156, 104, 32, 74 / 74, 172) kendi koşumla aynı çıktı.

## 2. Üretimden önce düzelmeli

**Ü1. G22 (PC817 #2 algı teli): kartın hangi ucuna ve hangi yönde bağlanacağı hiçbir yerde yazmıyor.**
- Yer: `tasarim/freecad/rehber/rehber_metin.py:325-326` (K1, madde 3).
- Nasıl ölçtüm: 74 kablonun tamamı için "nerede, hangi uç, hangi adımda" tablosu çıkardım. G22'nin rehberde geçtiği yerler şunlar: K1'de yalnız bara ucu yazıyor; F5'te yalnız sigorta takılıyor (`rehber_metin.py:1472`). Kart tarafındaki IN2 + / IN2 − ucu ve kutup yönü hiçbir yerde yok.
- Neden önemli: PC817 LED'i ters bağlanırsa algı çalışmaz, ters gerilim LED'e zarar verebilir.
- Neden yakalanmadı: tamlık denetimi bu maddeyi sayıyor, çünkü cümlede "→" var.
- Öneri: K1 madde 3'e bir emir cümlesi ekle: "G22'nin öbür ucunu PC817 #2 kartında IN2 + klemensine, GND dönüşünü IN2 − klemensine bağla". K1 kontrolüne de kutup bakışı ekle.

**Ü2. X01 (PC817 çıkış beslemesi): 3V3'e gideceği yazmıyor.**
- Yer: `rehber_metin.py:258-259` (B6a).
- Nasıl ölçtüm: tablo satırını kablo kaydıyla karşılaştırdım. Kayıtta bu hat ESP32 3V3; metinde besleme pini adı geçmiyor.
- Neden önemli: 5 V'a bağlanırsa GPIO23 ve GPIO5 5 V görür. ESP32 girişleri 3,3 V'a dayanıklıdır, 5 V'a değil.
- Öneri: metne `{…X01}` yer tutucusuyla "ESP32 3V3 (5 V değil)" yaz. B6a kontrolüne de ölçüm ekle: besleme açıkken PC817 çıkışı en çok 3,3 V olmalı.

**Ü3. P01 / P02 / P03 (PCA9685 V+): "bağlı değil" cümlesi emir değil, bilgi cümlesi gibi okunuyor.**
- Yer: `rehber_metin.py:262-264` (B6a) ve `355-357` (K1, madde 7).
- Kaynak: `planlama/adim3/elektrik.md:226`: "Bu köprünün V+ ucu kartta bağlı değil. PCA9685 V+ klemensi boş kalır."
- Neden önemli: hazır 3 telli atlama kablosu kullanılırsa PCA V+ rayı XL4016 A / B / C çıkışlarını birbirine paralel bağlar. Bu, regülatörlere zarar verebilir.
- Öneri: metni emir kipine çevir: "PCA9685 V+ klemensine tel bağlama; 3 telli hazır kablo kullanma." Bir süreklilik kontrolü ekle: PCA V+ ile dağıtım kartı V+ arasında ölçü aleti ötmemeli. YASAK kalıplarına "PCA9685 V+ … bağla" ekle.

**Ü4. Tamlık denetimi ileri tarihli ve olumsuz cümleleri talimat sayıyor.**
- Yer: `rehber_denetim.py` yaklaşık 1182 (`TALIMAT_FIIL`) ve 1206 (`tamlik_denetle`).
- Fiil kalıbı çok geniş. Şu biçimlerin hepsine uyuyor:
  - "takılır", "takma", "takılmaz" (`tak\w*`);
  - "gider", "gelir", "iner", "çıkar";
  - "→" işareti.
- Bozma denemesi: N01 ve N02'nin talimatını sildim, kablo adlarını "…K2'de takılır" biçimli bir cümleye taşıdım. Tamlık 0 eksik verdi, yani denetim bunu yakalamadı.
- Öneri:
  - kabloyu, kablo kaydının `rehber` alanında "bugün" bağlandığı yazan adımda arat;
  - "-de takılır / bağlanır" gibi edilgen ileri cümleleri ve "takma / bağlama" olumsuzlarını talimat sayma.

**Ü5. K1 kontağı 87 yerine 87a'ya (NC) yazılırsa hiçbir denetim yakalamıyor.**
- Yer: `planlama/adim3/kablolar_denetim.py`, K1 `uclar` kontrolü. K1'de yalnız alanların boş olmaması kontrol ediliyor; K2'de ise COM, NO ve NC zorlanıyor.
- Bozma denemesi: kablo kaydında K1'i `30→87a` yaptım. Yalnız görünüm farkı çıktı ("md'yi yeniden üret"). Bunu güvenlik hatası olarak yakalayan bir denetim yok.
- Neden önemli: 87a, rölenin dinlenmede kapalı ucudur. Bu durumda acil stop basılıyken bara enerjili kalır.
- Öneri: K1 `uclar` değerini `elektrik.md:441` ile birebir karşılaştır (30 → 87); 87a görülürse hata ver. Bu denetime bir bozma denemesi de ekle.

**Ü6. Kutup ters çevrildiğinde denetimler bunu yakalamıyor; yalnız onay kaydı yakalıyor.**
- Yer:
  - K1, SV1/SV2 polarite cümlesi: `rehber_metin.py:315-326` çevresi;
  - B6a kondansatör cümlesi: `rehber_metin.py:253-257`.
- Bozma denemesi: iki cümlede de + ile −'yi yer değiştirdim. Anlamsal denetimler (zorunlu, tamlık, yasak) bunu geçirdi. Yalnız onay kaydı, metin değiştiği için farkı gösterdi.
- Karşılaştırma: B5a'da (SV3) ve E3a'da (TVS) aynı ters çevirme `ZORUNLU` kalıbıyla yakalanıyor. Kablo kaydında kondansatörün yönünü bozduğumda da `zorunlu` yakalıyor.
- Öneri: B6a kondansatörü ve K1 SV1/SV2 için de `LISTE ZORUNLU` kalıbı ekle. Kalıp, kutup yönünü yer tutucu üzerinden istemeli.

**Ü7. `F10e-dogrula.py` vurgu rengi ölçümünü sessizce düşürüyor (üretim zinciri).**
- Yer: `planlama/d158/F10e-dogrula.py:96-99` ve `309`. Ayrıca `rehber/app.js`, `VURGU_TON`.
- Nedeni: doğrulayıcı vurgu rengini şu düzenli ifadeyle arıyor: `\bVURGU_ANA\s*=\s*"(#...)"`. `app.js`'te artık `const VURGU_ANA = VURGU_TON.light.ana` yazıyor, yani değer bir dizge değil. Bu yüzden `appjs_sabit("VURGU_ANA")` `None` dönüyor ve `ton["secim"]` `None` oluyor.
- Sonuç: vurgu karşıtlık ölçümü hata vermeden düşüyor ve ölçüm `gecti` sonucunun içinde değil. Doğrulayıcıyı koşmadım; bu çıkarım kaynak okumasından.
- Öneri: doğrulayıcı `VURGU_TON` nesnesini okusun. Değer bulunamazsa sessizce atlamasın, hata versin.

## 3. Kayıtlı açık iş olarak gidebilir

- **A1. G07 (100 kΩ ölçüm direnci).** Yer: `rehber_metin.py:302-307`. Bölümün K1 kontrolü doğru: pabuç saplamaya girmeden önce 100k ölçülüyor. Üç eksik var:
  - lehimden önce makaronun geçirilmesi yazmıyor;
  - gerginlik giderme yazmıyor (şu haliyle yükü direncin gövdesi taşıyor);
  - F1 ölçümü (`846-851`) yalnız uç değerleri veriyor (2,23 V ve 1,53 V).

  Öneri: bölücü oranını (0,1525) ve 12,8–14,4 V akü aralığı için beklenen 1,95–2,20 V değerini ekle. Hesap: `elektrik.md:234` (100k / 18k).
- **A2. K2 pin kontrolünün sırası.** Yer: `rehber_metin.py:740-747`. Pinler 12 AWG lehimlendikten sonra kontrol ediliyor. Öneri: kontrolü lehimden önceye al.
- **A3. Koruyucu yeri denetimi yalnız metinde adın geçip geçmediğine bakıyor.** Yer: `kablolar_denetim.py`, koşul `p_.casefold() in yer.casefold()`.
  - Bozma denemesi 1: hat-B sigortasını yük ucuna taşıdım, "Anahtarlı bara" adı metinde kaldı. Denetim yalnız tesadüfen, grup yer tutucusu hatasıyla yakaladı.
  - Bozma denemesi 2: R-aku-olcum'un yerini "arayüz kartında" yaptım. Denetim yakalamadı.

  Öneri: "… ucunda" ifadesi önce gelmeli ve yük ucunun adı geçmemeli.
- **A4. Çıplak değer kuralı direnç ve gerilim değerlerini kapsamıyor.**
  - Bozma denemesi: çıplak "100 kΩ" yakalanmadı, çıplak "20 A" yakalandı. G07 için yanlış bir gerilim (4,23 V) yazdım; yakalanmadı. F1'de yanlış ölçüm koşulu yazdım; yakalanmadı.
  - Öneri: çıplak değer kuralını ölçüm bağlamındaki V ve Ω değerlerine de genişlet. F1'deki gerilimleri kayıttan türeyen yer tutuculardan üret.
- **A5. Mantar ve ana anahtar uçları için YASAK kalıbı yok.** "Mantarın NC uçlarını aynı vidaya bağla" cümlesi yakalanmadı. Öneri: "aynı vida / klemens" ifadesinin mantar ya da ana anahtarla birlikte geçtiği durumlar için YASAK kalıbı ekle.
- **A6. "(kablajda teyit)" ibaresi silinse de yakalanmıyor.** E3a ve B5a'da ibareyi sildim; yakalanmadı. Kablo kaydı tarafında ise teyit sözcüğü silinince `yon_yer` yakalıyor. Öneri: ibareyi rehber metninde de zorunlu kıl.
- **A7. A06'nın − ucu silinse de yakalanmıyor.** Yer: `rehber_metin.py:336-338`. Öneri: iki uçlu kablolarda her iki ucun adı zorunlu olsun.
- **A8. Tek sözcüklü ASCII dizgeler denetlenmiyor.** Yer: `rehber_denetim.py`, `_gorunen_mu`; içinde boşluk olmayan dizgeyi "görünmez" sayıyor.
  - Bozma denemesi: "Onceki" ve title özniteliğindeki "Parca secili" denetlenmedi. "bagla" ve "Kablo secili" yakalandı.
  - `index.html` bu denetimin kapsamında değil.
- **A9. Açık temadaki vurgu rengi (#a35ef2) parça sınıfı rengi "lazer" (#8e44ad) ile 13,4 ΔE00 uzaklıkta.**
  - Bu, renk ayrımı eşiği olan 15'in altında. Bu çift hiçbir eşik denetiminde yok. Öneri: vurgu rengini parça sınıfı renklerine karşı da eşiğe sok.
  - Açık temanın kopya tonu (#d9bffb) sahne zemininde 1,36 karşıtlıkta. Bu yalnız ikincil ton için kayda değer.
- **A10. 27.000 yerleşim sayısı yeniden üretilemedi.**
  - Günlükteki sayıyı çıkaran betik depoda yok.
  - Kendi sayımımda, saplama sırası gözetilmeden 14.840 geçerli yerleşim çıktı. G09 ve G11 ayrı saplamalara izin verildiğinde ve G11 5,6 Ω ile 2,6 A'ye sınırlandığında da sonuç aynı.
  - Vardığım sonuç değişmiyor: en kötü köprü akımı her yerleşimde 20 A (bkz. §5).
- **A11. Kondansatör kaydının kaynağı kayboldu.** `kablolar.json` içinde `kondansatorler.kaynak` yeniden yazılmış ve eski `planlama/adim3/elektrik.md:130` göndermesi düşmüş. Öneri: göndermeyi geri ekle.
- **A12. Dağıtım kartı C'nin güç panelinde montaj yeri ve donanımı yok.** Kart modelde de yok. Öneri: açık iş olarak yaz.
- **A13. TVS "iki uçta da işaret varsa (çift yönlü)" cümlesi üretici yazımıyla çelişiyor.** Yer: `rehber_metin.py:547-552`.
  - Vishay yazımına göre çift yönlü parçada bant hiç yoktur; "iki uçta işaret" diye bir şey yok.
  - Öneri: gövde baskısına bakılsın: …A tek yönlü, …CA çift yönlü.
  - Çift yönlü parça takılırsa zarar vermez, ama ters kutup koruması kaybolur.
- **A14. Ana anahtarın saplama ölçüsü bilinmiyor.** M5 varsayımla yazılmış, ölçü teslimde netleşecek.
- **A15. Günlükteki "eski ölçüt 2 eksik" sayısı yeniden üretilemedi.**
  - Eski `rehber_denetim --kaynak` sürümünü kendi kopyamda koştum: eksik 0 (6 kablonun adı geçmiyor, yalnız bilgi olarak).
  - Yeni ölçütün eski metne uygulanması doğru üretildi:
    - eski metin + eski kayıt: 46 eksik (34 kablo, 10 koruyucu, 1 koruyucu yeri, 1 kutuplu parça);
    - eski metin + yeni kayıt: 66 eksik.
  - Bu yalnız günlükte düzeltilecek bir sayı.

## 4. Üretim adımında bakılacaklar

- Ü7 düzelmeden `F10e-dogrula` koşulursa, vurgu karşıtlığı "geçti" görünür ama aslında ölçülmemiştir. Doğrulayıcı çıktısında vurgu satırı açıkça bulunmalı.
- Üretilen `rehber/veri` dosyasında yer tutucular çözülmüş olmalı. Şunlar elle bakılmalı:
  - G07: bölücü değerleri;
  - K1: `{kontak.K1}` = 30 → 87;
  - E3a / B5a / B6a: kutup cümleleri.
- Yazdırma sayfası (`yazdir.html`): `lejantMetin`, `altKablo` gösterimi ve açık tema tonu (`rt.light`) baskıda kontrol edilsin.
- HDMI kablosunun açık tema rengi #1d3854 → #193cff olarak değişti. Hesabım:
  - karşıtlık sahne zemininde 5,57, lejantta 6,71;
  - L* 39,0; siyah kablo tonu 13,2;
  - en yakın kablo tonları mor 17,8 ve mavi 18,2 ΔE00.

  Ekranda siyah ve mavi kabloyla yan yana göz kontrolü yapılsın.
- Tarayıcıda karanlık temada vurgu (#00ffee) ve kopya ton (#9ffff6) birlikte görülsün. Hesabım:
  - vurgu karşıtlığı sahnede 13,41, lejantta 12,55;
  - en yakın kablo tonu beyaz, 24,7 ΔE00.

## 5. Kendi ölçümlerim (özet)

**74 kablo.** Her kablo için talimatın olduğu adımı, iki ucu ve kutbu tabloya çıkardım.
- Talimatı eksik ya da belirsiz olanlar: G22, X01, P01–P03 (Ü1–Ü3) ve G07 / K2 sırası (A1–A2).
- Öbürleri doğru adımda ve doğru uçta.
- Kablo kaydında devre değerleri değişmemiş. Durum sayıları da değişmemiş: kesin 20, teyit 53, karara bağlı 1.

**Güvenlik sırası.** Hepsi doğru:
- akü en son bağlanıyor;
- ölçümler akü ayrıkken yapılıyor;
- F1'de G07 ölçüm sırası doğru: önce problar, sonra akü, sonra anahtar;
- TVS katodu + uca, kondansatör şeridi − uca bağlanıyor;
- K2'nin COM / NO mantığı `elektrik.md:426-464` (E9 ön şarj) ile uyumlu;
- sigortalar bara (kaynak) ucunda.

**Köprü akımı.**
- Yöntem: her köprüye, beslediği yüklerin toplamı ile besleme akımından küçük olanı atanıyor; kök sigorta bu değeri ayrıca sınırlıyor.
- Yıldız bara: eski ve yeni sürümde aynı, 20 / 20 / 15 / 5 A.
- Anahtarlı bara (yeni): 20 / 20 / 2 A. Eski kod burada "akü dönüşü yok" diye yanlış bir hata veriyordu.
- 12 AWG etek sınırı: CFR 35 A ile NFPA 79 25 A'nin küçüğü olan 25 A × 0,82 (45 °C) = 20,5 A. Pay 0,5 A.
- Her yerleşimde en kötü köprü 20 A çıkıyor, çünkü F1 ile sınırlı 20 A'lik bir BTS her zaman besleme saplamasının dışında kalıyor.
- Köprüler G09 ve G12 ile aynı kesitte (F1 arkasında 12 AWG). Bu yüzden 0,5 A'lik pay tüm sistemde ortak. Kalın köprüye gerek yok.
- Yerleşim hükmü: serbest yerleşim güvenli.

**Renk.** CIEDE2000 ve WCAG hesabını kendim yaptım; günlükteki değerlerle aynı çıktı. Tek ek bulgum A9 (vurgu ve "lazer").

**Bozma denemeleri.** 24 deneme yaptım: 14 metin, 10 kablo kaydı.
- Anlamsal denetimin (onay kaydı hariç) yakaladıkları, 12 tane:
  - X01 silme;
  - G22;
  - B5a kutup;
  - E3a kutup;
  - köprüleme / kısa devre ifadesi;
  - sigorta yerine tel;
  - eski kontrol-4 kalıbı;
  - ASCII "bagla";
  - G07 giriş saplamasına;
  - TVS bant = anot;
  - kondansatör şeritli bacak V+'ya;
  - yıldız bara F3 / F4 saplama 1'e.

  Bunlara ek olarak K2 teyit sözcüğü ile TVS sipariş maddesini `yon_yer` yakaladı.
- Yakalanmayanlar, 12 tane:
  - N01 / N02 ileri cümle;
  - K1 SV ters;
  - B6a kondansatör ters;
  - K2 G10'u NC'ye (yalnız tesadüfi ASCII hatası çıktı);
  - sigorta yük ucunda;
  - çıplak 100 kΩ;
  - G07 4,23 V;
  - mantar aynı vida;
  - "kablajda teyit" silme;
  - F1 ölçüm koşulu;
  - A06 − ucu;
  - K1 87a.

  Bunlara ek olarak kayıttaki "kutup belli" teyit metni ve R-aku-olcum yeri de yakalanmadı.
- Onay kaydı metindeki her bozmayı fark olarak gösterdi. Bu bir insan gözden geçirme kapısıdır, anlamsal bir denetim değildir.

**Onay kaydı.**
- 88 fark: 62 eklendi, 25 değişti, 1 silindi. Sayı günlükteki listeyle aynı.
- Silinen ve değişen 26 farkın hepsini eski metinle okudum. Örneklemim ≥ 25.
- Silinen tek cümle "K1'de bırakılan iki ana hat ucunu bağla". Bunun yerini, alt adım 10'daki ve F1'deki daha ayrıntılı cümleler aldı.
- E3a'daki "veri sayfasıyla doğrulanmadı" notu "teslimde gövde bandı okunur" biçimine dönmüş. Bu, doğrulanmamışlığı gizlemiyor.
- K52, K60 ve K61 hâlâ "karar bekliyor".
- Önemli: onay kaydı ham cümleleri yer tutucular çözülmeden saklıyor. Bu yüzden kayıttaki bir değer değişikliği onay farkında görünmez.

**Pabuç ve parça sayısı.**
- Kırmızı pabuç 4 → 5; bir adet 10'luk paket yetiyor (`maliyet.json` madde 162).
- Mavi pabuç 9 / 20, sarı pabuç 23.
- Kondansatör: 2200 µF, 5 adet (2 + 2 + 1), yedek yok; madde 61'de değişiklik yok.
- TVS: P6KE6V8A 2 adet, P6KE18A 1 adet; değişiklik yok.
- Makaron ve direnç setleri kapsıyor.
- `maliyet.json` değişmedi.

**Döngü kaydı.** `dongu-158` düzeltmesindeki commit saati (15:50:47 +0300) git kaydıyla doğrulandı.

## 6. Sınırlar ve gizlilik

- Paket dışındaki dosyalara dokunulmamış. Yalnız dosya tarihine baktım; içeriklerini açmadım:
  - `tasarim/freecad/kabuk/gorsel/*.png`: 13 dosya, son yazım 9 Kasım;
  - `tasarim/freecad/montaj/yerlesim-kontrol.json`: son yazım 3 Kasım.
- Şu yerlerde fark yok: `kod/`, `planlama/maliyet.json`, `planlama/adim3/pin-haritasi.md`, `rehber/veri`, `rehber/goruntu`, `planlama/rehber`.
- Gizlilik taraması: `1328b60`'a göre eklenen satırlarda ve yeni dosyada yerel yol, makine adı, e-posta ya da kişisel ad deseni 0 eşleşme verdi.

## 7. Bakılmadı

- Üretilmiş çıktılar (`rehber/veri`, ekran görüntüleri) ve tarayıcıdaki gerçek görünüm: üretim bu paketin kapsamı dışında.
- `F10*` doğrulayıcılarının çalışması: koşulmadı. Ü7 yalnız kaynak okumasıyla bulundu.
- Röle, mantar ve ana anahtarın gerçek parça veri sayfası: teslimde bakılacak.
- `index.html` ASCII denetimi.
- Kablo uzunlukları ve güzergâh geometrisi: `rehber_kablo.py`'de geometri kodu değişmediği için yeniden sınanmadı.
