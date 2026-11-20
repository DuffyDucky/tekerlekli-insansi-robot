# P10.8c günlüğü: yanlış standart numarası, M7 D / E onarımı, etek ön bandı kuponu, kafa-yerleşim notu

Uygulama ajanı, 19.11.2026. Dal `lale-duzeltme`, başlangıçta HEAD = uzak = `d8ade70`, `git status` 19 satır (eski kir). Commit,
push ve `git add` yok; tam rehber üretimi (`rehber_uret.py`) bu adımda koşulmadı (kapanış adımının işi, § 11). Bağımsız kontrol
ajanı bu günlüğü okuyacak; riskli yerler § 9'da.

## 1. Başlangıç

- `tasarim/freecad/carpisma_kos.py kontrol`: çıkış 0, "izlenen 17 dosyanin ozetleri kayitla ayni".
- FreeCAD kilidi (`planlama/d158/FREECAD-KILIT.txt`, git dışı) "boş". Her FreeCAD koşusunda dolduruldu, sonra yine "boş".
- Bellek: başlangıçta boş ≈ 4 GB. Kullanıcının tarayıcısı açıktı, dokunulmadı. FreeCAD koşuları kısa, tek tek (en uzunu M7, ≈ 3 dk).
- İzlenen 17 dosyaya yazılmadı, montaj betikleri koşmadı (son kontrol § 6).

## 2. Görev 1: rehberde yanlış standart numarası

**Kaynak tanım (iş tanımı, `P108b-gunluk.md` § 14.2 ve § 16.4 sonu):** rehberde "Çerçeve cıvatası M3x6 ISO 7381 … 7387" (yedi ad) ve iki
kez "Yaka cıvatası M3x6 ISO 7381" görünüyor; doğrusu ISO 7380.

**Kök neden (doğrulandı):** FreeCAD 1.1 aynı etiketi ikinci kez verince eski sürümlerin 0NN ekini koymuyor, etiketin sonundaki sayıyı
artırıyor. Etiket "… ISO 7380" ile bitince ikinci kopya "… ISO 7381", sonraki "… 7382" oluyor. `Kod` özelliği hiç artırılmıyor.
- `tasarim/freecad/kabuk/kabuk-montaj.FCStd`: K204–K218, 8 nesne "Cerceve civatasi M3x6 ISO 7380 … 7387", hepsinin kodu
  "M3x6 ISO 7380" (üretici `kabuk_parcalar.py:885`, `kod="M3x6 ISO 7380"`).
- `tasarim/freecad/dirsek/dirsek-montaj.FCStd`: D054 / D056 "Yaka civatasi M3x6 ISO 7380 / 7381" (`dirsek_parcalar.py:335`); dosya
  rehberde dirsek_sag ve dirsek_sol için iki kez kullanılıyor.
- Rehber verisinde yanlış adlı parça 9: kabukta 7 (7381…7387; 7380 doğru), dirsekte 2 (sağ ve sol D056).
- Rehberin adı `rehber_veri.py` (394, 788, 847) `RM.tr(RM.kopya_eki_sil(ad, kod))` ile kuruyor; `kopya_eki_sil` yalnız 0NN ekini
  siliyordu.

**Sızıntı taraması (`ISO 738[1-9]`, eşleşme sayısı):**

| Dosya | Sayı | Ne | Tam üretimle düzelir mi |
|---|---|---|---|
| `rehber/veri/rehber-veri.json`, `.js` | 9 / 9 | parça adları (7381 × 3, 7382…7387 × 1) | evet |
| `planlama/rehber/kontrol.json` | 17 | üretim kontrol çıktısı | evet |
| `planlama/d158/F10d-dogrula.json` / `F10e` / `F10f` | 18 / 14 / 2 | zincir çıktısı | evet (zincir 4–6) |
| `tasarim/freecad/montaj/robot-montaj.step` | 21 | FreeCAD etiketi (STEP ürün adı) | hayır, CAD etiketi |
| `tasarim/cad/lale158-model.js`, `rapor/lale158-model.js` | 9 / 7 | eski kopyalar, artık üretilmiyor (K48) | hayır |
| `planlama/adim4/M6_erisim_sonuc.json` | 10 | eski adım 4 çıktısı | hayır |
| `tasarim/freecad/lale158/ikinci-kontrol.json` | 28 | eski kayıt | hayır |
| `tasarim/freecad/lale158/kafa-yerlesim/uygulama-ikinci.json` | 14 | FreeCAD etiketi | hayır |

Temiz olanlar: PDF (metni 0), rehber adımlarının bağlantı listeleri (kodu kullanıyor), demo HTML (0; demo rehber adlarını çalışma
anında `rehber-veri.js`'ten yükler, tam üretimden sonra düzelir), GLB (0), `montaj-analiz.json` (8 çerçeve + 4 yaka, hepsi 7380),
`planlama/maliyet.json`, `planlama/baski-listesi.md`.

**Yapılan:**
- `tasarim/freecad/rehber/rehber_metin.py`: `kopya_eki_sil` 0NN eki yoksa yeni `artirma_eki_sil`'e düşer. **Ölçüt (kör sondaki sayıyı
  silme değil):** adın sonundaki sayı kodun sonundaki sayıdan büyükse ve adın o sayıdan önceki kısmı + kodun sayısı kodla bitiyorsa
  sayı koddakine döner. Kod yoksa, kod sayıyla bitmiyorsa ya da ad koddan farklı bir tabanla bitiyorsa ad değişmez ("Sonar 8",
  "Kablo yolu 12", "Civata M5x18 DIN 912" değişmez).
- `tasarim/freecad/rehber/rehber_denetim.py`:
  - `STANDART_BILINEN` (projede bilinen küme: DIN 125, 127, 912, 913, 916, 933, 934, 976, 985, ISO 7380; kaynak `planlama/maliyet.json`
    ve `montaj-analiz.json` kodları, 19.11.2026), `standartlar`, `standart_denetle` (kural "bilinmeyen standart" ve "ad ↔ kod
    standardı"), `artirma_denetle` (silinen etiketler; tabanı aynı FCStd'de olmayan artırılmış etiket = HATA "kardeşsiz").
  - Veri kipi (`denetle`): parça adları ve metinler standart denetiminden geçer, `gecti` buna bağlı.
  - `--kaynak` (`kaynak_denetle`): rehber metni + arayüz görünen dizgeleri + CAD etiket / kodu (üretimin adıyla) standart denetimine,
    CAD parçaları `artirma_denetle`'ye girer. Çıktıya "standart numarasi … HATA", "ARTIRMA …" ve "KAYNAKTA YENI (bilgi)" satırları
    eklendi.
  - Bozma: `standart_bozma_denemesi` (16 sınama), `elektrik_bozma_denemesi` toplamına eklendi.
- Üretim aynı işlevi kullanıyor: `rehber_uret.py` önce `kaynak_denetle`'yi, yeni veriyle `denetle(V, …)`'yi koşar; adları
  `rehber_veri.py` aynı `RM.kopya_eki_sil` ile kurar. Ayrı bir kopya yok.

**Ölçümler:**
- Ölçüt 1238 CAD parçasında tam bu 9 etikette tetikleniyor; dokuzunun da kardeş zinciri tam (kod … etiket sayıları aynı belgede).
  Başka ad ↔ kod standart çelişkisi yok (adlardaki DIN 913 kodla tutarlı).
- `--kaynak`: CAD kaynak etiket / kod 955 → **947** (dokuz ad tekilleşti), eskime HATA 0, bilgi **10 → 2**. Kalan iki bilgi satırı
  beklenen "(gösterim)" etiketleri: "(gösterim)" ve "Ana anahtar düğmesi (gösterim, kabuk deliği gerekir)".
- Veri kipi şimdiki (commit'li) `rehber-veri.json` üstünde çıkış **1**, standart hatası 18 (9 bilinmeyen + 9 ad ↔ kod): beklenen, veri
  tam üretimden önce eski adları taşıyor. Yeni işlevle adları yeniden kurulmuş benzetim verisi (depo dışı) çıkış 0, standart 0.
- Üretim adları benzetimi: yeni kural tam 9 adı "… ISO 7380" yapıyor; mevcut 12 kablo adı farkı (taban) etkilenmiyor.

**Bozma (16, hepsi yakalandı):** eski kural güncel CAD'de yakalanır (ad ↔ kod 9 ve bilinmeyen numara 9); metinde "ISO 7381"; DIN 913 /
912 kayması; veride "ISO 7387"; tabanı belgede olmayan artırılmış etiket (kardeşsiz); 0NN kuralı bozulmadı; 9 doğru ad bozulmaz
("Cerceve civatasi M3x6 ISO 7380", "Saplama M3x73 DIN 976 (0)", "Civata M3x6", "Civata M5x18 DIN 912", "Sonar 8", "Kablo yolu 12",
"Burc M5x40", "Motor NEMA 17", "Setskur M4x6 DIN 913"). Toplam `--bozma-denemesi` **346 / 346** (önce 330).

## 3. Görev 2: `tasarim/freecad/test/m7_kuponlari.py` D / E onarımı

**Kaynak tanım (`karar-kuyrugu.md` "P10.8a kupon dosyalarından açık iş", `P108a-gunluk.md`):** D / E bölümü Y2a'dan beri koşmuyor
(`arayuz.DIRSEK["tup_uc_y"]` −140 → −170; betikte `Y_KAPAK` −148 sabit, "width of box too small"). D1 / D2 / E STL'leri 15.10
koşusundan. `kupon_tazelik.py` "BILINEN ESKI" istisnasıyla geçiyordu.

**Kök neden:** D bölümünün ölçüleri betikte sabit sayıydı (y −148, dış kol 224,9 …); dirsek çatalı Y2a'da 30 mm aşağı indi ve dış kol
5 → 8 mm oldu, betik izlemedi. Eski tazelik denetimi `catal_dis_kol`'u izlemiyordu.

**Yapılan:**
- D bölümü ölçüleri `dirsek_parcalar.py`'den okunuyor (import; yalnız okunur): TX / TZ / TUC (arayüzle eşitliği assert), pim ve tüp
  yarıçapları, bilezik, yarık, `Y_KAPAK = KOPRU_Y[0]` (−178), `Y_TABLA = TUC + 25` (−145), iç / dış kol (156 / 227,9), çatal eki 3,
  kelepçe y / z. Bütün y konumları TUC'ye göre. Okunanlar `SONUC["dirsek_okunan"]`'da.
- `M7_YALNIZ_C` kipi kalktı; çıktıdan önce D1 doğrulaması (FCStd dilimi ve bellekteki çatal, dört fark < 1 mm³) geçmezse betik durur.
- `SONUC["kaynak"]` (dirsek-montaj.FCStd md5), her kuponda `stl_md5`, `SONUC["arayuz_olcum"]` (aynı radyal geçiş taraması kupona ve
  gerçek parçaya).
- `kupon_tazelik.py`: M7 bölümü yeniden yazıldı (yalnız-C kaydı, kaynak md5, STL md5, arayüz karşılaştırması; her fark ESKI), "BILINEN
  ESKI" istisnası kalktı, `--kati` artık etkisiz. `tasarim/freecad/test/README.md` uyarısı "D / E onarıldı" paragrafıyla değişti.
- Çıktılar yeniden üretildi: `m7-kupon-sonuc.json`, `m7-kuponlari.step`, `stl/kupon-d1-kelepce-kesiksiz.stl`, `stl/kupon-d2-kelepce-
  bosaltmali.stl`. C ve E STL'leri bayt bayt aynı (md5 9e5c6bda, 8f5eddb7). İkinci koşu aynı STL'leri verdi (belirlenimci).

**Ölçüm: kupon arayüzü = güncel tasarım** (aynı tarama işlevi, mm):

| Arayüz | Tasarım (arayüz / CAD) | D1 | D2 | Gerçek çatal (FCStd) |
|---|---|---|---|---|
| Pim yarıçapı | 25,4 (`TUP_PIM_R`) | 25,4 | 25,4 | 25,4 |
| Bilezik iç / dış yarıçap | 28,25 / 31,0 | 28,25 / 31,0 | 28,25 / 31,0 | 28,25 / 31,0 |
| Bilezik yarığı uç / kök | 4,0 | 4,0 / 4,0 | 4,0 / 4,0 | 4,0 / 4,0 |
| Kelepçe deliği çapı × 2, merkez y | Ø3,4; y −162 / −151 | aynı | aynı | aynı |
| Dış kol | 8 (`catal_dis_kol`) | 227,9 (156 + …) | aynı | 227,9 |
| Tüp iç / dış yarıçap (E ↔ omuz FCStd "Ust kol tupu") | 25,65 / 28,0 | – | – | E 25,65 / 28,0 = gerçek tüp 25,65 / 28,0 |
| Geçme tüp ↔ pim / tüp ↔ bilezik | 0,25 / 0,25 (kabul en çok 0,3) | 0,25 / 0,25 | 0,25 / 0,25 | 0,25 / 0,25 |

- D1 ↔ FCStd dilimi (y −178 … −145): 71.079,65 mm³, iki yönlü fark 0,000; D1 ↔ bellekteki çatal aynı. Tüp çakışma 0. D2 bağlı sektör
  θ 45–120°, tüp oturma y −170,25.
- Kupon boyları: D1 / D2 70,9 → **73,9** × 72 × 33 (dış kol 5 → 8). D1 90,3 g (100 %) / 41,8 g (tahmini), 71 dk; D2 88,6 / 42,3 g,
  72 dk; dört kupon toplam 210 / 106 g (README tablosu).
- `git status`'ta hiçbir FCStd değişmedi.
- Tazelik bozması (depo dışı kopya ağaçta): HEAD JSON'u → ESKI (yalnız-C, kaynak yok, STL md5 yok, `tup_uc_y` −140 / −170); `tup_uc_y`
  oynatılınca → ESKI; STL'nin baytı değişince → ESKI.

**Yapılmayan (iş tanımı gereği):** `planlama/baski-listesi.md`, `F4c-*` değişmedi. Önerilen kayıt § 10.3.

## 4. Görev 3: etek ön bandı kuponu (K55)

**Kaynak tanım:** rehber F1 (adım 33) "Ön sağ / sol bant": "Bandı yerinin 10 mm önünde yandan (+x / −x) getir …, sonra önden içeri (−z)
it: bu son 10 mm'de engel … z +105 braketinin perçin somunu (1–8 mm, ölçüm) … Bu geçme denenmedi; bu bant için kupon henüz yok."
B-rep ölçümü `planlama/d158/P108b-olcum/brep-yol.json` (etek ön sağ: yan bacak serbest, son 10 mm'de perçin somunu 1–8 mm, ≈ 9,4 mm³).
P10.8a'nın ilk bant kuponu bu yolu denemiyordu (`P108a-kontrol.md` O2); bu kez yol modelde kuponla ve tam bantla ölçüldü.

**Keşif (salt okunur FreeCAD, `kabuk-montaj.FCStd`):** dikiş z 87,5; dil orta bantta (y 121'de z 90 / 95: orta 257,0–258,25 dil, ön
258,5–260,0 dudak, boşluk 0,25); z +105 boss'u ön bantta (x 252–257); braket "Etek braketi sag z+105" dik ayağı x 250–252, y 106,5–136,5,
z 90–120; perçin somunu flanşı x 252,0–252,8 (boss yüzündeki cebe girer). z +88 ısıl gömmeleri y 60 / 85 / 198 (dilimin dışında).

**Yapılan:** yeni `tasarim/freecad/kabuk/etek_kuponu.py` (`bant_kuponu.py` kalıbı; FreeCAD 1.1; yalnız `kabuk-montaj.FCStd`'yi okur).
- **Üst parça** = "Etek on sag" ∩ kutu (x 240–270, y 106,5–136, z 77,5–130): dudak, z +105 boss'u, flanş cebi, Ø3,4 geçiş.
- **Alt parça** = "Etek orta sag" dilimi (dil) + "Etek braketi sag z+105" dilimi (2 mm dik ayak, Ø5,1 perçin somunu deliği) + taşıyıcı
  (ayağın arkasında x 244–250 sertlik bloğu, Ø10 perçin boşluklu; üstte y 136,5–139,5 iki dilimi birleştiren plaka). Taşıyıcı kuponun
  kendi eki; gerçek parçalar kesilmedi, değiştirilmedi.
- Alt parça iki biçimde: **delikli** (gerçek M3 perçin somunu ayağa perçinlenir) ve **flanşlı** (perçin somununun CAD şekli tek parça;
  perçin aleti yoksa).
- **Yol modelde:** üst parça (dx, 0, +10)'dan yana bacakla dx → 0 (240, 160, …, 1, 0), sonra dz 10 → 0 (0,5 mm adım). Aynı yol tam
  "Etek on sag" ile gerçek engellere (tam orta bant, tam braket, perçin somunu, z +88 ısıl gömmeleri) karşı da koşulur.
- Çıktı: `kabuk/etek-kuponu.json`, `kabuk/stl/etek-kuponu-ust.stl`, `etek-kuponu-alt.stl`, `etek-kuponu-alt-flansli.stl`. Baskı yönü
  bantlar gibi ters (dünya −y yukarı). Betik, yol denetimlerinden biri tutmazsa çıktı yazmadan durur.
- `kupon_tazelik.py`'ye "etek on bandi (K55)" eklendi (kaynak FCStd md5 + üç STL md5).

**Ölçümler (`etek-kuponu.json`):**
- Kaynak ↔ kupon kesit karşılaştırması (3 y × 6 z hattı, dudak / dil / boss / cep): hepsi ≤ 0,01 mm, sonuç doğru. Dikiş: dudak 1,5,
  dil 1,25, boşluk 0,25 (arayüz `KABUK_BINDIRME_BOSLUK` 0,25).
- Yolun z bacağında perçin somunuyla ortak hacim: **kupon ve tam model aynı eğri**, dz 8,5 → 0,5 mm arası, en çok 9,98 mm³ (dz 2,5);
  dz 10 / 9,5 / 9 ve 0 (yerinde) serbest. B-rep ölçümüyle (1–8 mm, 9,4 mm³; P108b adımı farklı) uyumlu.
- Yan bacak (z +10'da) kuponda ve tam modelde serbest; ne kuponda ne tam modelde perçin somunundan başka engel (dil, taşıyıcı, ısıl
  gömme) yok; yerinde (0, 0, 0) ortak hacim 0.
- Delikli alt parça somunsuz: yol tamamen serbest (engel yalnız somun). Flanşlı alt parça: somunlu eğriyle aynı.
- Parçalar (STL ↔ B-rep hacim farkı ≤ %0,003, kapalı, manifold dışı yok):

| Parça | Ölçü mm (baskı yönünde) | Kütle tahmini | Süre tahmini | Tablaya temas | 46° üstü çıkıntı |
|---|---|---|---|---|---|
| Üst | 8,0 × 42,5 × 29,5 | 3,6 g | 6 dk | 110 mm² | 23,9 mm² |
| Alt delikli | 20,0 × 52,5 × 33,0 | 8,2 g | 14 dk | 840 mm² | 172,5 mm² |
| Alt flanşlı | 20,0 × 52,5 × 33,0 | 8,4 g | 14 dk | 840 mm² | 220,3 mm² |

- İki koşu aynı STL'leri ve (süre dışında) aynı JSON'u verdi. FCStd değişmedi.

**Sınır (ilk turda yalnız betik başlığında yazılıydı; "JSON'da da yazılı" ifadesi yanlıştı, P108c-kontrol O3):** dilim kısa (y 106,5–136)
ve gerçek banttan serttir; taşıyıcı gerçek braketten serttir. ~~Kupon zorlamadan geçiyorsa gerçek bant da geçer~~ (düzeltme turu 1:
yalnız hareket kısıtlıyken; § 12.4). Kupon sağ bandı keser; sol bant X aynası. Rehber metni bu turda değişmedi (düzeltme turu 1'de
değişti, § 12.2).

## 5. Görev 4: `kafa-yerlesim` raporu ve notu

**Kaynak tanım:** `karar-kuyrugu.md` (D3 kapanış notu altı "Açık (düzeltme turu 3'te bulundu, düzeltilmedi)" ve P10.7b2j / b2k
bloğunda `kafa-yerlesim/rapor.html` maddesi), `F10u-gunluk.md` § 11 madde 6: `uygulama_metin.py:58` IndexError `_yak_tr` ile giderildi,
ama yeniden üretilen not (1) F10w montajından gelen sayıları değiştirdi, (2) 12 V satırının elle düzeltmesini kaybetti, (3) "Listede
olmayan 6 kalem" dört kalem sayıyordu ve L USB-A dirseğini anıyordu. "Üretici düzeltilip ikisi birlikte yeniden üretilmeli."

**Önce inceleme:** üretici `tasarim/freecad/lale158/kafa-yerlesim/uygulama_rapor.py` (sistem Python'u, FreeCAD yok; `uygulama_metin.py`
içinde exec). Yalnız `uygulama-notu.md` ve `rapor.html` yazar (satır 205, 275). `kafa-analiz.json`, `kabuk-analiz.json`,
`montaj-analiz.json`, `lale158-kontrol.json`, `uygulama-*.json`, `carpisma-sonuc.json`, `taban-analiz.json`'u yalnız okur;
`arayuz` ve `kablo_yolu_ekran` (içe aktarınca yazmaz) okunur. `kafa_montaj` gerekmez. İzlenen 17 dosyadan hiçbirine yazmaz. Koşu
önce / sonra `git status` farkı yalnız bu iki dosya.

**Yapılan (üreticide, yalnız rapor metni):**
- `uygulama_rapor.py` 12 V satırı: "Taban → göğüs ekranı (tabandan, boyundan geçmez; `kablo_yolu_ekran.py` yolunun en üst noktası
  y 1.205 < omuz S3 1.270; `lale158-kontrol.json` …)". Sayılar `KY.yollar()["12 V"]` ve `A.S3`'ten (HEAD notundaki elle düzeltmenin
  içeriği, F4a § 2–3).
- `uygulama_metin.py`: `LISTE_DISI` listeden kuruluyor, kalem sayısı `LISTE_DISI_N` ile sayılıyor (not başlığı, HTML ve karar
  maddesinde). L USB-A dirsek çıktı (yalnız Pi 2 → ses kartı yolundaydı; ses kartı P10.7b2j'de yedek, takılmaz). Kalan 3 kalem: USB-A
  uzatma ~1 m, kısa micro USB, hoparlör kablosu ~1,1 m. **Uygulama ajanı kararı.**
- `py -3 -B -X utf8 tasarim/freecad/lale158/kafa-yerlesim/uygulama_rapor.py`: çıkış 0, "yazildi boy 1580.0 kafa 1542.7 izgara 1.519
  esik alti False".

**Fark (`uygulama-notu.md`, HEAD'e göre; `rapor.html` aynı değerler):**
- Tarih 05.11 → 19.11.2026.
- F10w montajından (beklenen yön): parça 1.177 → 1.225, toplam kütle 25.910,6 → 26.120,6 g, kafa grubu 1.570,8 → 1.542,7 g, tilt payı
  3,64 → 3,78, tilt statik 0,152 → 0,093 kg·cm, pan 2,21 → 2,26, ızgara yüksüz 1,517 → 1,519 (100 g 1,479, 500 g 1,329, fren 1,747),
  AM y 525,62 → 522,84.
- Ses kartı satırları kalktı: ölçüm satırı "modelde yok (P10.7b2j …)", kablo tablosundan "Ses kartı uzatması" ve "3,5 mm → PAM",
  port Pi 2 "Boş (USB ses kartı yedek, takılmaz)", varsayım satırı. ESP32 USB satırı 1.129 / 1.560 (elle notu kalktı, değer aynı).
  Hoparlör yolu 823 → 824 mm.
- Hoparlör ön halkası "göğüs bandına > 4,243 (en yakın 5 parçada yok) mm" (`_yak_tr` düzeltmesinin yazdığı biçim).
- 12 V satırı düzeltme içeriğini koruyor; "Listede olmayan 3 kalem" ve "3 kablo kalemi".
- Çarpışma koşu kimliği 20261105-185759 / 20261103-215611 → 20261119-075818, `tek_kosu` false → true.

**Fark ettim, dokunmadım (iş dışı):** notun özeti ve "Atlananlar" maddesi hâlâ "zincir omuz bölümü hariç koştu", "omuz bölümü eski
kayıttan", "… yeni kabuktan önce" diyor; `carpisma-sonuc.json` artık `tek_kosu` true ve omuz koşusu 19.11 tarihli. Metin üreticide
sabit; düzeltilmesi ayrı iş (§ 10.5).

## 6. Komutlar ve çıkış kodları (depo kökünden, `PYTHONIOENCODING=utf-8 py -3 -B -X utf8`)

FreeCAD koşuları `FC_SCRIPT=<betik> freecadcmd <kullanıcının run_fc.py'si>` ile, tek süreç, kilit dolu / sonra boş; loglarda
Traceback ve hata yok (freecadcmd hata olsa da 0 dönebildiği için loglar okundu).

| Komut | Çıkış | Sonuç |
|---|---|---|
| `tasarim/freecad/carpisma_kos.py kontrol` (başta) | 0 | izlenen 17 dosya kayıtla aynı |
| FreeCAD: `tasarim/freecad/test/m7_kuponlari.py` (iki kez) | 0 / 0 | "bitti"; D1 doğrulama ok; ikinci koşu aynı STL'ler |
| FreeCAD: keşif betiği (depo dışı, salt okunur) | 0 | § 4 keşif değerleri |
| FreeCAD: `tasarim/freecad/kabuk/etek_kuponu.py` (iki kez) | 0 / 0 | "bitti 8,0 s"; yol denetimleri doğru; ikinci koşu aynı STL / JSON |
| `tasarim/freecad/lale158/kafa-yerlesim/uygulama_rapor.py` (üretici düzeltmesinden önce ve sonra) | 0 / 0 | § 5 |
| `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0 | ASCII 0, zorunlu eksik 0, yasak 0 (istisna 10), onay farkı 0 (kablo 220, liste 257, metin 1199); CAD kaynak 947; eskime HATA 0 / bilgi 2; standart HATA 0; artırma silinen 9, kardeşsiz 0 |
| `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0 | **346 / 346** (önce 330) |
| `tasarim/freecad/rehber/rehber_kablo.py` | 0 | SONUÇ GEÇER; onay kaydı tutuyor |
| `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi` | 0 | **114 / 114** |
| `planlama/adim3/kablolar_denetim.py` | 0 | SONUÇ GEÇER |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0 | SONUÇ GEÇER; toplam bozma **174** |
| `planlama/d158/F10l-birlesim.py <depo> d8ade70` | 0 | birleşim sınaması GECER; B cümle eski 1177 / yeni 1177, eklenen 0 / silinen 0 (beklenen 0 / 0) |
| `tasarim/freecad/test/kupon_tazelik.py` | 0 | SONUC: TAZE (16 denetim): yanak, bant, etek ön (kaynak + 3 STL), M7 kaynak + 4 STL + arayüz |
| `tasarim/freecad/carpisma_kos.py kontrol` (sonda) | 0 | izlenen 17 dosya kayıtla aynı |
| `planlama/d158/F4c-dogrula.py` (salt okunur; bilgi) | 0 | SONUC: GECTI (baskı listesi kupon kütlelerine bakmıyor; § 10.3 yine de önerilir) |
| `rehber_denetim.py` (veri kipi, commit'li eski veri; bilgi) | 1 | standart 18 (beklenen, § 2) |

Pre-push kancasının desenleri (yerel kullanıcı yolu, takma ad, e-posta, anahtar, IBAN / telefon, ekip adı) değişen ve yeni satırlarda
arandı (kancanın içerik kalıpları değişen satırlara ve yeni dosyaların tamamına, kanca dışında koşuldu): bulgu 0. Aynı
sınama bilerek bozulmuş bir satırı yakaladı.

## 7. Kararlar (uygulama ajanı kararı; geri alınabilir)

1. **Düzeltme yeri rehber tarafı** (`kopya_eki_sil`), CAD etiketi değil: CAD parça geometrisi / etiketleri bu işte değişmez, izlenen
   dosyalara yazılmaz. STEP'teki etiketler (21) böyle kalıyor.
2. **Ölçüt kod kanıtı + kardeş zinciri:** sondaki sayı yalnız kod aynı tabanla daha küçük bir sayıda bitiyorsa düşer; zinciri tam
   olmayan artırılmış etiket `--kaynak`'ta HATA (yanlış "düzeltme" yerine dur).
3. **Bilinen standart kümesi elle:** 10 numara, kaynağı yorum satırında. Yeni bir standart (ör. DIN 7991) gelirse `--kaynak` HATA verir;
   bilerek böyle (eklemek tek satır).
4. **Bozma negatif listesinde "Dagitim karti 2" yerine "Motor NEMA 17":** etiket "Dagitim karti 2", kod "… 1" gibi bir çelişki kod
   ölçütüyle yanlış düzelirdi; bu durumu `artirma_denetle` kardeşsiz kuralı yakalar (bozma sınaması 5).
5. **M7 ölçüleri `dirsek_parcalar.py` içe aktarılarak okunuyor** (izlenen dosya; yalnız okunur). ~~Sabit sayı kalmadı.~~ Düzeltme
   turu 1: `dirsek_parcalar.py`'de satır içi yazılan sayılar okunamıyor, betikte kaldı ve listelendi (§ 12.5).
6. **Etek kuponu taşıyıcısı kuponun kendi eki** (gerçek braketin basılı eşi değil, ama dik ayak ve delik gerçek dilim); alt parçanın
   perçin somunlu ve flanşlı iki biçimi.
7. **Kafa-yerleşim üreticisinde iki metin düzeltmesi** (12 V satırı, liste dışı kalem sayısı + L dirsek): kuyruk "üretici düzeltilip
   yeniden üretilmeli" diyordu; ikisi de yalnız rapor metni.

## 8. Yapılmayanlar ve neden

- Tam rehber üretimi, zincir 2–10, plan / kuyruk / demo / `sonuc-rapor.html`, `planlama/baski-listesi.md`, `F4c-*`: iş tanımı gereği
  bu adımda yok (§ 10, § 11).
- `robot-montaj.STEP` ve eski kopyalardaki (lale158-model.js, M6, ikinci-kontrol, uygulama-ikinci) "ISO 738x" etiketleri: CAD etiketi
  ya da artık üretilmeyen eski çıktı; montaj betikleri koşulmaz.
- Kuponların görüntüsüne bakılmadı (tarayıcı / görsel üretim yok, bellek kısıtı). Doğrulama geometrik: kesit karşılaştırması, yol
  eğrisi, STL ↔ B-rep.
- Kupon basılmadı (fiziksel deneme Ahmet'te).
- `uygulama-notu.md`'nin omuz anlatısı (§ 5 sonu).

## 9. Kontrol ajanı için riskli yerler

1. **`artirma_eki_sil` ölçütü:** "taban + kod sayısı kodla bitiyor" koşulu. Kodu sayıyla biten, adı da aynı sayı tabanıyla biten ama
   gerçekten farklı numaralı parça (ör. kod "Kablo 1", ad "Kablo 12") yanlış düzelir mi? Bugünkü 1238 parçada tetiklenen 9; hepsi
   kardeş zincirli. Tam üretimden sonra veride `ISO 738[1-9]` 0 ve ad sayısının yalnız bu 9'da değiştiğini doğrula.
2. **Veri kipi şu an kırmızı** (commit'li veri, standart 18). Tam üretim yapılmadan commit edilirse `rehber_denetim.py` (zincir 3) düşer.
3. **`kaynak_denetle` FCStd okuyamazsa** (`cad_parcalar()` istisnası) `ar` None olur ve `--kaynak` geçmez (bilerek).
4. **M7 D1 / D2 kütle ve ölçü değişti** (70,9 → 73,9 mm): `baski-listesi.md` / `F4c-partiler.*` eski değerleri taşıyor; F4c-dogrula
   sonucu § 6'da (GECTI).
5. **Etek kuponu yol eğrisinin kapsamı:** yalnız z bacağı (0,5 mm) ve yan bacak (11 nokta, z +10). Ara diyagonal yol yok; rehber de
   iki parçalı yolu anlatıyor. Engel ortak hacmi > 0,001 mm³ sayılıyor (B-rep, temas sayılmaz).
6. **Etek kuponu sol bant:** sağ dilim; sol için aynalık varsayımı.
7. **Kafa notunda L USB-A dirseğin listeden çıkması** içerik kararı (§ 7.7); HTML'de de 3 kalem.
8. **`kupon_tazelik.py` `--kati`** artık etkisiz (her fark zaten ESKI); bayrağı kullanan betik var mı bak (bulamadım).

## 10. Önerilen kayıtlar (uygulama ajanı yazmadı; kapanış adımı için hazır metin)

### 10.1 `planlama/dongu-158.md` P10.8 Durum hücresi (dikey çizgi yok)

"P10.8c (19.11, `planlama/d158/P108c-gunluk.md`): rehberde yanlış standart numarası düzeldi (FreeCAD 1.1 kopya etiketinde sondaki
sayıyı artırıyordu; kopya_eki_sil sayıyı koddan geri alıyor, 9 ad ISO 7380), standart numarası denetimi ve 16 bozma eklendi. M7 D / E
kuponu güncel dirsekten okunuyor ve yeniden üretildi (D1 / D2 73,9 mm, arayüz ölçümü tasarımla aynı), tazelik istisnası kalktı. Etek ön
bandı kuponu (K55): rehberin iki parçalı yolu kuponda ve tam modelde aynı eğri (perçin somunu dz 0,5–8,5 mm). kafa-yerleşim notu
üreticisi düzeltilip yeniden üretildi. Tam üretim ve zincir 2–10 geçti."
(Son cümleyi zincir gerçekten geçtiyse yaz.)

### 10.2 `planlama/d158/karar-kuyrugu.md`

- "P10.8b rehber açıklarından" bloğundaki yanlış ISO numarası maddesine: "→ 19.11 P10.8c: **kapandı** (`P108c-gunluk.md` § 2;
  `kopya_eki_sil` → `artirma_eki_sil`, `--kaynak` standart / artırma denetimi; CAD etiketi ve `robot-montaj.step` etiketi değişmedi)."
- P10.8a "M7 D / E onarımı" maddesine: "→ 19.11 P10.8c: **kapandı** (`P108c-gunluk.md` § 3). `baski-listesi.md` / F4c Parti 0 D1 /
  D2 kütlesi ve m7 uyarısı F4c yeniden üretimini bekliyor (§ 10.3)."
- K55 bölümüne not: "Not (P10.8c, 19.11.2026; `P108c-gunluk.md` § 4): etek ön bandı kuponu `tasarim/freecad/kabuk/etek_kuponu.py`
  (üst = ön bant dilimi, alt = orta bant dili + braket dik ayağı + taşıyıcı; perçin somunlu ya da flanşlı). Rehberin iki parçalı yolu
  kuponda ve tam modelde aynı ortak hacim eğrisini veriyor (perçin somunu dz 0,5–8,5 mm, en çok ≈ 10 mm³; yan bacak serbest).
  Basılmadı; kupon zorlamadan geçerse K55 a etek ön için yeterli, kalırsa K55 b."
- kafa-yerleşim açık işine: "→ 19.11 P10.8c: **kapandı** (`P108c-gunluk.md` § 5): üretici 12 V satırı ve liste dışı kalem sayısı
  (3; L USB-A dirsek çıktı) düzeltildi, `uygulama-notu.md` ve `rapor.html` birlikte yeniden üretildi."
- Yeni iş maddesi: "`kafa-yerlesim/uygulama-notu.md` omuz anlatısı ('omuz bölümü hariç', 'yeni kabuktan önce') `tek_kosu` true olan
  `carpisma-sonuc.json` ile çelişiyor; metin `uygulama_metin.py`'de sabit (`P108c-gunluk.md` § 5)."

### 10.3 `planlama/baski-listesi.md` / `F4c-*` (önerilen; bu adımda değişmedi)

Parti 0'da D1 / D2 / E satırlarının kütle, süre ve ölçüsü yeni `m7-kupon-sonuc.json`'dan gelir (D1 41,8 g / 71 dk, D2 42,3 g / 72 dk,
73,9 × 72 × 33 mm); `F4c-partiler.py`'nin m7 eski uyarısı (`yalniz_c`) kalkar. Sıra: `py -3 -B -X utf8 planlama/d158/F4c-partiler.py`
→ `py -3 -B -X utf8 planlama/d158/F4c-liste.py` → `py -3 -B -X utf8 planlama/d158/F4c-dogrula.py` (F4c-liste `Y2b-baski.py`'yi
koşmayı da yazar; Y2b girdisi değişmedi). Etek kuponu Parti 0'a eklenecekse bu ayrı karar (Ahmet).

### 10.4 Rehber F1 (adım 33) metni (önerilen; değişmedi)

"… Bu geçme denenmedi; bu bant için kupon henüz yok." → "… Bu geçme henüz denenmedi; önce etek ön bandı kuponunu (K55,
`tasarim/freecad/kabuk/etek_kuponu.py`) bas ve aynı yolla dene: kupon zorlamadan oturursa bandı da aynı yoldan tak, oturmazsa tasarım
kararını (K55 b) bekle." Metin değişirse `rehber_kritik_onay.json` yenilenir ve F10l listeleri yeniden üretilir.

### 10.5 Yeni iş (karar değil)

kafa-yerleşim omuz anlatısı (§ 5 sonu); `robot-montaj.step` ve eski çıktılardaki "ISO 738x" etiketleri (CAD tarafında etikete 0NN
benzeri ayırıcı ya da tekil ad; montaj koşusu gerektirir).

## 11. Kapanış tarifi (ESKİDİ: güncel tarif § 13)

### 11.1 Kurallar

- Bütün komutlar depo kökünden. Python `py -3 -B -X utf8` (tam üretimde `py -3 -X utf8`), Bash'te `PYTHONIOENCODING=utf-8`.
- Uzun koşu: arka planda, çıktı ve çıkış kodu depo dışına: `<komut> > "$DIS/<ad>.log" 2>&1 < /dev/null; echo $? > "$DIS/<ad>.durum"`.
  Ön planda en çok 170 s yokla. `Start-Process` yok. Çıkış kodunu `.durum`'dan, sonucu logdan oku (`freecadcmd` hata olsa da 0 dönebilir).
- FreeCAD aynı anda tek süreç; tam üretim kilidi kendisi doldurur, başlamadan "boş" olmalı.
- **Bellek:** eşik koşulu yok. P10.8b kapanışında ölçülen: tam üretim 2.510 s, boş fiziksel bellek en düşük 0,71 GB, üretim yine bitti.
  Bu kez de **ölçüm kaydı tut:** 30 s'de bir boş fiziksel bellek ve `freecadcmd` / `rehber_uret` çalışma kümesi; en düşük değeri, süreyi
  günlüğe yaz. Durma ölçütü: süreç üretim bitmeden kaybolursa, logda bellek hatası çıkarsa ya da CPU süresi 15 dk ilerlemezse.
- Yasaklar: `regresyon.py` argümansız yok (zincir 10'da `--yazma`); montaj betikleri yok; izlenen 17 dosyaya yazma yok. Commit'e
  girmeyecekler: 19 eski kir (`tasarim/freecad/kabuk/gorsel/*.png` 13, `tasarim/freecad/montaj/yerlesim-kontrol.json`, kökteki
  `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`), `planlama/maliyet.json`, `tubitak-2209b/`,
  kilit dosyası.

### 11.2 Ön sınama

| # | Komut | Beklenen (alt sınır) |
|---|---|---|
| 0a | `tasarim/freecad/carpisma_kos.py kontrol` | 0; "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 0b | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0; ASCII 0, zorunlu eksik 0, yasak 0, onay farkı 0 (kablo 220, liste 257, metin 1199); CAD kaynak 947; eskime HATA 0 / bilgi 2; standart HATA 0; artırma silinen 9, kardeşsiz 0 |
| 0c | `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0; ≥ 346 / 346 |
| 0d | `tasarim/freecad/rehber/rehber_kablo.py` ve `--bozma-denemesi` | 0 / 0; GEÇER; ≥ 114 / 114 |
| 0e | `planlama/adim3/kablolar_denetim.py` ve `--bozma-denemesi` | 0 / 0; GEÇER; toplam ≥ 174 |
| 0f | `planlama/d158/F10l-birlesim.py <depo kökü> d8ade70` | 0; GECER; cümle değişmediği için listeler boş |
| 0g | `tasarim/freecad/test/kupon_tazelik.py` | 0; "SONUC: TAZE (16 denetim)" |

### 11.3 Tam üretim (FreeCAD veri adımlı; `--veri-yok` DEĞİL: adlar yeniden kurulmalı)

`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py`, arka planda, `.durum` kalıbıyla; ≈ 42 dk (P10.8b 2.510 s). Beklenen son satır
"BITTI cikis 0" ve "ek kontrol sorunlu: -". P108b § 16.3'e göre:
- veri 1238 parça, 50 adım; `robot.glb` / `robot-glb.js` HEAD ile aynı.
- görünüm alt adım 91 / 91, uç etiketi 58 (± değişmemeli: metin değişmedi), hata 0.
- yazdır taşan 0, PDF 89 sayfa civarı.
- denetim ASCII 0, zorunlu eksik 0, yasak 0, kopya eki 0, elektrik iddiası 0, **standart numarası 0** (yeni satır).
- sıra: ulaşılamaz 0, giriş yolu girilemez 0, uçuş çarpışan 0, `istisna_bos` 0.
- onay farkı 0; tarayıcı 50 / 50, konsol 0.

Üretimden sonra:
- `rehber/veri/rehber-veri.json` ve `.js`'te `ISO 738[1-9]` **0** olmalı; HEAD'e göre parça adı farkı **tam 9** (7 "Cerceve
  civatasi M3x6 ISO 7380", 2 "Yaka civatasi M3x6 ISO 7380"; Türkçe gösterimde "Çerçeve cıvatası …", "Yaka cıvatası …"), başka metin
  farkı yok (üretim tarihi / süre alanları hariç).
- `planlama/rehber/kontrol.json` değişir; kareler değişmemeli (ad kare çizimine girmiyor; değişirse piksel farkına bak).

### 11.4 Zincir 2–10 (P108b § 15.4 sırası)

| # | Komut | Beklenen |
|---|---|---|
| 2a | `tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0, SONUÇ GEÇER |
| 2b | `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi --veri rehber/veri/rehber-veri.json` | 0; ≥ 132 / 132 |
| 2c | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0; 0b ile aynı |
| 3 | `tasarim/freecad/rehber/rehber_denetim.py` (veri) | 0; ASCII 0, zorunlu eksik 0, yasak 0, elektrik iddiası 0, standart 0 |
| 4 | `planlama/d158/F10f-dogrula.py` | 0, GECTI (≈ 560 s); JSON'da `ISO 738[1-9]` 0 |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | 0, GECTI (≈ 960 s); `renk_demo` KALDI bilinen |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` | 0, GECTI (≈ 980 s) |
| 6g | `planlama/d158/F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | bilgi |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | 0, GECTI |
| 8 | `planlama/d158/F9b-dogrula.py` | 0, GECER (kuyruk / plan değiştiyse önce demo, § 11.7) |
| 9 | `tasarim/freecad/carpisma_kos.py kontrol` | 0, kayıtla aynı |
| 10 | `planlama/d158/regresyon.py --yazma` | 0, GEÇER, kötüleşen yok |

### 11.5 Gözle bakılacaklar

- Rehber sayfasında (`rehber/`) çerçeve cıvatalarının geçtiği F3 adımının ve dirsek yaka cıvatalarının geçtiği adımın parça listesi:
  adlar "… ISO 7380"; liste satır sayısı HEAD ile aynı (ad tekilleşti, parça sayısı değişmedi; adet gösterimi varsa adet arttı mı bak).
- PDF'te aynı sayfalar: "ISO 7381" araması 0.
- Etek kuponu ve M7 kuponları: isteğe bağlı, STL'leri bir dilimleyicide aç (D1 / D2 dış kol 8 mm, etek alt parçada Ø5,1 delik ve
  taşıyıcıdaki Ø10 boşluk; flanşlı biçimde flanş ayağın dış yüzünde).
- `tasarim/freecad/lale158/kafa-yerlesim/rapor.html`: 12 V satırı ve "Listede olmayan 3 kalem".

### 11.6 Kırmızıya düşebilecek yerler

| Yer | Belirti | Ne yap |
|---|---|---|
| Tam üretim denetimi, standart numarası | > 0 | Logdaki adı oku. Yeni bir artırılmış etiketse `--kaynak` da yakalamalıydı: koordinatöre bildir; bilinen kümeye kayıtsız ekleme yapma |
| Veri farkı | 9'dan fazla ad değişti | `artirma_eki_sil` beklenmeyen bir adı değiştirdi (§ 9.1): durdur, koordinatöre |
| F10d / F10e / F10f | Parça adı karşılaştırması (GLB / demo adı) düşer | GLB'de ISO 738x yok (adlar zaten farklı yoldan); çıkarsa hangi denetim, logdan oku, koordinatöre |
| `rehber_denetim --kaynak` | `ARTIRMA KARDESSIZ` | FCStd'de taban etiketi olmayan artırılmış ad: CAD bulgusu, koordinatöre |
| F9b | Hata > 0 | Kuyruk / plan değiştiyse demo eski: § 11.7 |
| F4c-dogrula | m7 kütle / ölçü farkı | § 10.3 sırası (ayrı karar: bu kapanışa alınacak mı) |

### 11.7 Plan, kuyruk, demo

Sıra: (1) § 10.1 plan hücresi (dikey çizgisiz; satırın sütun ayırıcı sayısı HEAD ile aynı), (2) § 10.2 kuyruk, (3) kuyruk değiştiği için
`py -3 -B -X utf8 tasarim/cad/demo_uret.py` (yalnız `tasarim/Robot-Tasarim-Demosu.html`'i yazar; fark yalnız gömülü sha'lar olmalı),
(4) `planlama/d158/F9b-dogrula.py` (0, hata 0). § 10.3 (F4c) ve § 10.4 (rehber F1 metni) ayrı karar; § 10.4 seçilirse onay yenilemesi +
F10l + § 11.2 + tam üretim yeniden.

### 11.8 Commit'e girecek dosyalar

`git add <yol>` ile tek tek; sonra `git diff --cached --name-only` § 11.1 yasak listesiyle kesişmemeli.
- **Kaynak (8):** `tasarim/freecad/rehber/rehber_metin.py`, `tasarim/freecad/rehber/rehber_denetim.py`,
  `tasarim/freecad/test/m7_kuponlari.py`, `tasarim/freecad/test/kupon_tazelik.py`, `tasarim/freecad/test/README.md`,
  `tasarim/freecad/kabuk/etek_kuponu.py` (yeni), `tasarim/freecad/lale158/kafa-yerlesim/uygulama_rapor.py`,
  `tasarim/freecad/lale158/kafa-yerlesim/uygulama_metin.py`.
- **Kupon çıktıları (8):** `tasarim/freecad/test/m7-kupon-sonuc.json`, `m7-kuponlari.step`, `stl/kupon-d1-kelepce-kesiksiz.stl`,
  `stl/kupon-d2-kelepce-bosaltmali.stl`; `tasarim/freecad/kabuk/etek-kuponu.json`, `kabuk/stl/etek-kuponu-ust.stl`,
  `etek-kuponu-alt.stl`, `etek-kuponu-alt-flansli.stl` (yeni).
- **Günlük:** bu günlük `planlama/d158/P108c-gunluk.md`; kontrol ajanının dosyası varsa o da.
- **Rapor (2):** `tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md`, `rapor.html`.
- **Üretim çıktıları:** `rehber_uret.py`'nin yazdığı ve `git status`'ta görünen `rehber/` dosyaları ve `planlama/rehber/kontrol.json`;
  zincir JSON'ları (F10a / F10d / F10e / F10f; regresyon `--yazma` ile değişirse `regresyon.json` / `regresyon-son-kosu.json`).
- **Kayıtlar:** `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md`, demo yeniden üretildiyse `tasarim/Robot-Tasarim-Demosu.html`;
  § 10.3 seçilirse `planlama/baski-listesi.md`, `planlama/d158/F4c-partiler.json`, `F4c-partiler.md`.
- **Push öncesi:** `.git/hooks/pre-push` kancası koşar (yerel yol, takma ad, e-posta, anahtar, IBAN / telefon, ekip adı). Bulgu çıkarsa
  push etme, satırı düzelt.

## 12. Düzeltme turu 1 (kontrol: `P108c-kontrol.md`, DÜZELTMEYLE GEÇER)

Koordinatör kararları kontrol raporundan sonra. Kurallar aynı: commit, push ve `git add` yok; tam üretim yok; izlenen 17 dosyaya
yazılmadı; montaj betiği koşulmadı. İlk brief'teki "baskı listesi ve F4c'ye dokunma" sınırı bu tur için koordinatörce kaldırıldı.
Aşağıdaki kararların hepsi **Echo kararı (geri alınabilir)**.

### 12.1 O1 ve D6: kafa notunun omuz anlatısı ve kütle kaynağı

Echo kararı (geri alınabilir): omuz metinleri kayda bağlanır. Kütle ve devrilme sayılarının tarihi ve kaynağı notta yazılır;
`uygulama-ivme.json` yeniden üretilmez.

**Kayıt (`tasarim/freecad/carpisma-sonuc.json`):**
- `tek_kosu` true.
- 9 bölümün hepsi "tamam", hepsi aynı koşuda (20261119-075818): statik, omuz, kol_sag, kol_sol, kolkol, kafa_sabit, kafa_sag,
  kafa_sol, taban.
- Omuz bölümü 19.11.2026 08:00:30–11:11:59 arasında koştu (11.489 s).

**Kod:**
- `uygulama_metin.py`'de `OMUZ_TAMAM` üç koşulun hepsini ister: omuz durumu "tamam", `tek_kosu` true, omuz koşusu taban koşusuyla
  aynı. Özet, tarama satırı, koşu tablosu, "Atlananlar" ve "Karar" metinleri bu değişkenden kurulur. Değişken yanlışsa eski metin
  kendiliğinden geri gelir.
- `uygulama_rapor.py` tablo satırı aynı koşulu kendisi hesaplar, çünkü bu satır exec'ten önce kuruluyor.
- `IVME_KAYNAK` cümlesi iki şey yazar: `uygulama-ivme.json`'un son commit tarihi (`git log`, 09.11.2026) ve güncel
  `montaj-analiz.json` kütlesi, kablo payıyla birlikte.

**Değişen cümleler** (`uygulama-notu.md`; `rapor.html`'de aynı değerler):

| Yer | Eski | Yeni |
|---|---|---|
| Özet, ilk cümle | "B + R1 modele işlendi, zincir omuz bölümü hariç koştu." | "B + R1 modele işlendi; çarpışma taraması bütün bölümlerle (omuz dahil) tek koşuda yenilendi (koşu 20261119-075818)." |
| Özet, tarama | "eklem aralığındaki tarama 0 (omuz bölümü eski kayıttan)" | "eklem aralığındaki tarama 0 (omuz bölümü dahil, koşu 20261119-075818)" |
| Özet, kütle | "26.120,6 g (400 g kablo payı dahil)" | "26.120,6 g (400 g kablo payı dahil; `uygulama-ivme.json`, 09.11.2026)" |
| Tablo | "Tarama, eklem aralığında çakışma (omuz bölümü eski)" | "… (omuz dahil, tek koşu)" |
| Koşu tablosu | "statik kol_sag kol_sol kolkol kafa_sabit kafa_sag kafa_sol taban … (omuz hariç)" | "statik omuz kol_sag … taban (koşu 20261119-075818)" |
| Atlananlar | "**`carpisma_kos` omuz bölümü ve omuz regresyonu koşmadı** … yeni kabuktan önce" | Kalktı. Yerine: "Kütle ve devrilme sayıları `uygulama-ivme.json`'dan (dosyanın son commit'i 09.11.2026, `uygulama_ivme.py`); o koşudan sonra montaj değişti: güncel `montaj-analiz.json` 25.835,1 g + 400 g kablo payı = 26.235,1 g (fark 114,5 g). Devrilme payları yeni montajla yeniden hesaplanmadı." |
| Devrilme maddesi | "… Ev pozu kütle 26.120,6 g, AM y 522,84 (önceki …)." | Aynı; sonuna yukarıdaki kaynak cümlesi eklendi. |
| Karar | "**Omuz bölümü ve omuz regresyonu** (~4,8 saat) koşulsun mu? …" | Kalktı. Yerine: "**`uygulama_ivme.py` yeniden koşulsun mu?** … 09.11.2026 … güncel montajla toplam 26.235,1 g." |

**Kanıt:**
- Üretici çıkış kodu 0.
- Not ve raporda şu ifadeler 0 kez geçiyor: "omuz bölümü hariç", "eski kayıttan", "yeni kabuktan önce", "omuz koşulsun".
- Not artık kayıtla aynı şeyi söylüyor: omuz dahil, tek koşu, 20261119-075818.

**`uygulama-ivme.json` neden yeniden üretilmedi:**
- `uygulama_ivme.py` montaj betiği değil ve izlenen dosyaya yazmıyor.
- Ama FreeCAD'de `montaj/moduller`'i yükleyip bütün robotun kütle merkezini kuruyor. Bu ağır bir FreeCAD koşusu, ayrı bir iş.
- Notta kaynak ve tarih var. Fark önerilen kayda alındı (§ 13.7).

**Düzeltme (kontrol § 4):** L USB-A dirseğin çıkması uygulama ajanının kararı değildi; 14.11 kararının uygulamasıydı
(`kablolama-on-kararlar.md` § 5). Kontrol D6 gereği şu da düzeltildi: kütle cümlesi "F10w montajından" değil,
`uygulama-ivme.json`'dan (09.11).

### 12.2 (c) Rehber F1 kupon notu

Echo kararı (geri alınabilir): F1 kupon notu şimdi değişir. Yalnız etek ön sağ ve ön sol değişti; çerçeve ve omuz notları kaldı.

| Yer (`rehber_metin.py`) | Eski | Yeni |
|---|---|---|
| F1 alt adım 3 (ön sağ) | "Bu geçme denenmedi; bu bant için kupon henüz yok." | "Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir." |
| F1 alt adım 5 (ön sol) | aynı | "Bu geçme kuponla denenmedi (etek ön kuponu sağ banttan kesildi; sol bant için sonucu ayna çıkarımıdır); kupon sonucu gelince bu adım yeniden yazılabilir." |

**`rehber_denetim.py`:**
- ZORUNLU'daki F1 maddesi değişti: "… (K55 b) bekle. Bu geçme kuponla denenmedi …; kupon sonucu gelince bu adım yeniden yazılabilir."
  ifadesi iki kez aranıyor.
- Yeni ZORUNLU: ayna çıkarımı ibaresi.
- ASCII listesine "kuponu" ve "ayna" eklendi.

**YASAK değişmedi:** YASAK adım ayırmıyor ve F3 / F4'te "kupon henüz yok" cümlesi kalmalı. F1'de eski cümlenin kalktığını F10l
listesi sınıyor.

**Onay ve F10l:**
- `--kritik-onay-yenile` 4 fark yazdı: ZORUNLU 1 değişti + 1 eklendi, metin 2 değişti. Liste 257'den 258'e çıktı.
- `F10l-birlesim.py` taban `d8ade70` için güncellendi; varsayılan taban da `d8ade70`. Beklenen: silinen 2, eklenen 2.

### 12.3 (a) + (b) Baskı listesi, F4c, etek kuponu Parti 0'da

Echo kararı (geri alınabilir): baskı listesi ve F4c şimdi yenilenir. Etek kuponu "toplama katılmaz" bloğuna girer.

**Sıra:**
- `planlama/y2/Y2b-baski.py` çıkış 0. **`Y2b-baski.json` değişmedi** (`git diff --quiet`).
- `F4c-partiler.py` 0 → `F4c-liste.py` 0 ("yazildi 357 satir") → `F4c-dogrula.py` 0, GECTI.

**Elle yazılmış blok** (`F4c-liste.py` korur):
- Başlık artık "Yanak, bant ve etek ön kuponları".
- Etek önü "kupon yok" cümlesi kalktı; yerine yöntem ve kabul ölçütü geldi (§ 12.4).
- İki yeni satır:
  - üst: 8 × 42,5 × 29,5 mm, 3,6–4,6 g, ≈ 6 dk, brim;
  - alt flanşlı: 20 × 52,5 × 33 mm, 8,8–14,7 g, ≈ 15 dk; ilk deneme bununla.
- Blok toplamı: 88–142 g / 2,5 sa → 101–161 g / 2,9 sa.

**Diğer metinler:**
- `test/README.md:253`'teki "etek ön … kuponu yok … kuyrukta" cümlesi kalktı; yerine etek kuponu bölümüne gönderme.
- "D / E bölümü koşmuyor" uyarısı listeden ve `F4c-partiler`'den kendiliğinden kalktı (`yalniz_c` alanı yok).

**Değişen satırlar (baskı listesi ve F4c):**

| Satır | Eski | Yeni |
|---|---|---|
| D1 g / sa | 40,9–87,9 / 1,16–2,50 | 41,8–90,3 / 1,19–2,57 |
| D2 g / sa | 41,4–86,2 / 1,18–2,45 | 42,3–88,6 / 1,20–2,52 |
| E | 14,3–17,9 g | aynı |
| Parti 0 toplam g / sa | 257,4–420,0 / 7,32–11,94 | 259,2–424,8 / 7,37–12,08 |
| Parti 0 PETG-CF | 175,7–301,1 g (0,18–0,30 kg) | 177,5–305,9 g (0,18–0,31 kg) |
| D2'siz süre | 6,1–9,5 sa | 6,2–9,6 sa |
| Parça + kupon PETG-CF | 1,37–1,55 kg; pay 130 / −53 g; D2'siz 33–172 g | 1,37–1,56 kg; pay 128 / −58 g; D2'siz 31–171 g |
| m7 uyarısı (liste, `F4c-partiler.md` / `.json`) | "Uyarı (D1 / D2 / E eski) …" | kalktı |

Değerler kontrolün F4c formülüyle önceden hesapladığı değerlerle aynı.

**`F4c-dogrula.py` 7. denetim (`kupon_kutle_denetle`):**
- Şunları kupon JSON kayıtlarıyla karşılaştırır (`m7-kupon-sonuc.json`, yanak, bant, etek; 11 kayıt):
  - F4c-partiler'in Parti 0 m7 kuponları;
  - baskı listesinin Parti 0 tablosu;
  - "toplama katılmaz" bloğundaki STL yollu satırlar.
- m7 tam koşudansa eski uyarı listede ya da `m7_uyari`'de durmamalı.
- `--bozma-denemesi` **7 / 7**:
  - temiz kopya 0;
  - F4c D1 eski kütle;
  - liste D1 eski kütle;
  - m7 D2 kütlesi değişti;
  - etek JSON kütlesi değişti;
  - liste uyarısı;
  - `m7_uyari` dolu.

`F4c-rapor.html`'e dokunulmadı. Hiçbir betik onu üretmiyor ve Parti 0 sayıları eskidi (önerilen kayıt § 13.7).

### 12.4 O3, D2, D3: etek kuponunun deneme yöntemi, çıkıntı, malzeme notu

Echo kararı (geri alınabilir): yöntem hareketi kısıtlar. Desteksiz çıkıntı giderilir, malzeme notu yazılır.

**`etek_kuponu.py`:**
- Taşıyıcı plaka x 240'tan başlıyor (önce 244).
- JSON'a üç yeni alan:
  - `sinir`: sertlik; serbest dilim döndürülebilir ama gerçek bant döndürülemez; "geçti" yalnız kısıtlı hareketle kanıt, "geçmedi"
    belirsiz; sol bant ayna çıkarımı.
  - `deneme`: hazırlık, hareket 1 / 2, geçti, geçmedi, kayıt yeri, karar, baskı (brim).
  - `malzeme_notu`: perçin somunu PETG ayağa takılıyor, gerçekte ayak 2 mm Al; ilk deneme flanşlı biçimle.
- Betik başlığındaki "zorlamadan geçiyorsa gerçek bant da geçer" cümlesi düzeltildi.

**Yöntem** (JSON, README ve baskı listesinde aynı):
1. Alt parça mengene ya da kıskaçla sabitlenir.
2. Üst parça düz bir takoza tutturulur ve döndürülmez.
3. Önce yalnız x ekseninde (+x yanından) duvar hizasına getirilir.
4. Sonra yalnız −z yönünde 10 mm itilir.

**Kabul:**
- **Geçti:** elle itişle oturur; dikiş ≤ 0,5 mm; M3×14 elle girer; iz ya da çatlak yok; üç tekrarda aynı sonuç.
- **Geçmedi:** ancak döndürerek geçer, ya da iz / çatlak var. Sonuç belirsizdir: K55 b ya da tam bantla deneme; karar Ahmet'te.
- Sonuç `test/README.md` "K55 etek ön bandı kuponu" tablosuna yazılır.
- Geçerse K55 a seçilir ve F1 notu "kuponla denendi (tarih)" olur.

**Yeniden üretim:** FreeCAD, tek süreç, kilitli. Çıkış 0, "bitti 9,3 s".

| Ölçüm | Önce (tur 0) | Sonra |
|---|---|---|
| Alt delikli: kütle (tahmini / %100), süre | 8,2 / 13,7 g, 14 dk | 8,6 / 14,5 g, 15 dk |
| Alt flanşlı: kütle, süre | 8,4 / 13,9 g, 14 dk | 8,8 / 14,7 g, 15 dk |
| Alt: tabla teması | 840 mm² | 1.050 mm² |
| Alt: 46° üstü aşağı bakan yüz (delikli / flanşlı) | 172,5 / 220,3 mm², içinde z 3,0'da 120 mm² düz çıkıntı | 52,5 / 100,3 mm²; z 3,0 çıkıntısı yok |
| Üst | 8 × 42,5 × 29,5, 3,6 / 4,6 g, 6 dk, md5 `aa4dd699…` | aynı (STL değişmedi) |
| Kesit karşılaştırması (kaynak ↔ kupon) | ≤ 0,01 mm | ≤ 0,01 mm; dikiş 1,5 / 1,25 / 0,25 |
| Yol: kupon ↔ tam model | aynı eğri | **aynı eğri:** perçin somunu dz 0,5–8,5 mm, en çok 9,98 mm³; yan bacak serbest, başka engel yok, yerinde 0; delikli somunsuz serbest; flanşlı aynı eğri |

**STL ve tazelik:**
- Yeni STL md5: alt delikli `45c61ce3…`, flanşlı `6cf9d06a…`.
- Tazelik kaydı JSON'da. `kupon_tazelik` sonucu TAZE (16).

**README:**
- "K55 etek ön bandı kuponu" bölümü eklendi: parçalar, sınır, malzeme, baskı, test, geçti / geçmedi, sonuca göre, sonuç tablosu,
  gerekenler. Sayılar JSON'dan.
- Bant kuponundaki "etek ön … çıkarım" maddesi düzeltildi.

### 12.5 Düşükler

- **D1 (`rehber_denetim.py`):** bozma listesine yeni negatif eklendi.
  - Girdi: etiket "Civata M3x16", kod "M3x6".
  - `artirma_eki_sil` adı "Civata M3x6"ya çevirirdi. Ama zincir (M3x6 … M3x15) belgede yok, bu yüzden `artirma_denetle` bunu
    **kardeşsiz HATA** sayar.
  - Sonuç: `--kaynak` geçmez, üretim başlamaz, ad sessizce değişmez. Yakalandı.
  - `--bozma-denemesi`: 346 → **347 / 347**.
- **D4 (`kupon_tazelik.py`):** yeni `arayuz_fark` işlevi.
  - Bugünkü `arayuz.py`'de bulunmayan anahtar (üst düzey ya da sözlük içi) fark sayılır; değer "(arayuz.py'de yok)" yazılır.
  - Sonuç ESKİ olur.
  - `--bozma-denemesi` **4 / 4**: temiz kopya 0; `DIRSEK["catal_dis_kol"]` silindi; `TUP_PIM_R` silindi; `GECME["tup_pim"]` değişti.
    Hepsi bellek kopyasında, depoya yazılmadı.
- **D5 (`m7_kuponlari.py`):** okunabilecek başka sabit yok.
  - `dirsek_parcalar.py` bu sayıları modül sabiti olarak tutmuyor, çatal kurulumunda (satır 104–125) satır içi yazıyor.
  - Betikte kalan sayılar (betik yorumunda da listeli):
    - bilezik / alın kapağı r 31 (`R_BIL_DIS`), pim / bilezik boyu 25 (`PIM_BOY`);
    - sıkma kulakları x 178…192, z TZ − 41…TZ − 30, y TUC + 2;
    - köprü bandı z TZ ± 16;
    - 45° destek ucu x 213, y TUC + 12 (+ `CATAL_EK`);
    - tüp yuvası TUC + 26 / + 27;
    - pim içi r 21,9, TUC + 18…26;
    - tavan konisi r 21,9 → 5 (TUC + 1,1);
    - kablo deliği r 5;
    - pah r 31 → 23, z TZ + 16…40;
    - yarık z TZ − 45…TZ − 27,5;
    - kelepçe deliği x 177…193.
  - Koruma: D1 ↔ FCStd dilimi ve bellekteki çatal karşılaştırılır; fark > 1 mm³ ise betik durur.
  - Yalnız yorum değişti, betik yeniden koşulmadı. Kupon çıktıları ve md5'leri aynı. § 3'teki "sabit sayı kalmadı" iddiası
    düzeltildi.
- **Günlük:** § 4'teki "Sınır (JSON'da da yazılı)" düzeltildi (ilk turda yalnız betik başlığındaydı; artık JSON'da `sinir`).

### 12.6 Sınamalar

Hepsi depo kökünden: `PYTHONIOENCODING=utf-8 py -3 -B -X utf8`.

| Komut | Çıkış | Sonuç |
|---|---|---|
| `tasarim/freecad/carpisma_kos.py kontrol` (turun sonunda) | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| `rehber/rehber_denetim.py --kaynak` | 0 | ASCII 0, zorunlu eksik 0, yasak 0, onay farkı 0 (kablo 220, liste 258, metin 1199); CAD 947; eskime HATA 0 / bilgi 2; standart HATA 0; artırma silinen 9, kardeşsiz 0 |
| `rehber/rehber_denetim.py --bozma-denemesi` | 0 | 347 / 347 |
| `rehber/rehber_kablo.py` ve `--bozma-denemesi` | 0 / 0 | GEÇER; 114 / 114 |
| `planlama/adim3/kablolar_denetim.py` ve `--bozma-denemesi` | 0 / 0 | GEÇER; toplam bozma 174 |
| `planlama/d158/F10l-birlesim.py` | 0 | GECER; B cümle 1177 / 1177, eklenen 2 (beklenen 2), silinen 2 (beklenen 2) |
| `test/kupon_tazelik.py` ve `--bozma-denemesi` | 0 / 0 | TAZE (16 denetim); 4 / 4 |
| `planlama/d158/F4c-dogrula.py` ve `--bozma-denemesi` | 0 / 0 | GECTI (1–7, 11 kupon kaydı); 7 / 7 |
| `kafa-yerlesim/uygulama_rapor.py` | 0 | not ve rapor yazıldı |
| `kabuk/etek_kuponu.py` (FreeCAD) | 0 | bitti 9,3 s; log hatasız |
| `planlama/y2/Y2b-baski.py`, `F4c-partiler.py`, `F4c-liste.py` | 0 / 0 / 0 | `Y2b-baski.json` değişmedi |

**Kanca kalıpları** (anahtar, parola ataması, e-posta, IBAN / telefon, yerel yol, takma ad, ekip adı):
- Taranan: değişen izlenen dosyaların eklenen satırları + yeni dosyaların tamamı.
- Kanca dışında koşuldu (5.301 satır). Sonuç: **bulundu = 0**; pozitif kontrol (takma ad + e-posta içeren örnek satır) bulundu = 1.

## 13. Kapanış tarifi (GÜNCEL, tek başına okunur; § 11'in yerine)

### 13.1 Kurallar

**Ortam:**
- Bütün komutlar depo kökünden.
- Python `py -3 -B -X utf8`; tam üretimde `py -3 -X utf8`. Bash'te `PYTHONIOENCODING=utf-8`.

**Uzun koşu:**
- Arka planda koş; çıktı ve çıkış kodu depo dışına gitsin:
  `<komut> > "$DIS/<ad>.log" 2>&1 < /dev/null; echo $? > "$DIS/<ad>.durum"`.
- Ön planda en çok 170 s yokla. `Start-Process` kullanma.
- Çıkış kodunu `.durum`'dan, sonucu logdan oku: `freecadcmd` hata olsa da 0 dönebilir.

**FreeCAD:**
- Aynı anda tek süreç.
- Tam üretim kilidi (`planlama/d158/FREECAD-KILIT.txt`, git dışı) kendisi doldurur. Başlamadan önce "boş" olmalı.

**Bellek:**
- Eşik koşulu yok. P10.8b kapanışında tam üretim 2.510 s sürdü; boş fiziksel bellek en düşük 0,71 GB'a indi, üretim yine bitti.
- Bu kez de ölçüm kaydı tut: 30 s'de bir boş fiziksel bellek ve `freecadcmd` / `rehber_uret` çalışma kümesi. En düşük değeri ve süreyi
  günlüğe yaz.
- Şu durumlarda dur: süreç bitmeden kaybolur, logda bellek hatası çıkar ya da CPU süresi 15 dk ilerlemez.

**Yasaklar:**
- `regresyon.py`'yi argümansız koşma (zincir 10'da `--yazma`).
- Montaj betiği koşma.
- İzlenen 17 dosyaya yazma.

**Commit'e girmeyecekler:**
- 19 eski kir:
  - `tasarim/freecad/kabuk/gorsel/*.png` (13);
  - `tasarim/freecad/montaj/yerlesim-kontrol.json`;
  - kökteki `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`.
- `planlama/maliyet.json`, `tubitak-2209b/`, kilit dosyası.
- `planlama/d158/F4c-rapor.html` (değişmedi).

### 13.2 Ön sınama (tam üretimden önce)

| # | Komut | Beklenen |
|---|---|---|
| 0a | `tasarim/freecad/carpisma_kos.py kontrol` | 0; "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 0b | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0; ASCII 0, zorunlu eksik 0, yasak 0, onay farkı 0 (**kablo 220, liste 258, metin 1199**); CAD kaynak 947; eskime HATA 0 / bilgi 2; standart HATA 0; artırma silinen 9, kardeşsiz 0 |
| 0c | `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0; ≥ **347 / 347** |
| 0d | `tasarim/freecad/rehber/rehber_kablo.py` ve `--bozma-denemesi` | 0 / 0; GEÇER; ≥ 114 / 114 |
| 0e | `planlama/adim3/kablolar_denetim.py` ve `--bozma-denemesi` | 0 / 0; GEÇER; toplam ≥ 174 |
| 0f | `planlama/d158/F10l-birlesim.py` (varsayılan taban `d8ade70`) | 0; GECER; B cümle 1177 / 1177, **eklenen 2 / 2, silinen 2 / 2** (F1 kupon notu) |
| 0g | `tasarim/freecad/test/kupon_tazelik.py` ve `--bozma-denemesi` | 0 / 0; "TAZE (16 denetim)"; 4 / 4 |
| 0h | `planlama/d158/F4c-dogrula.py` ve `--bozma-denemesi` | 0 / 0; GECTI (1–7); 7 / 7 |

### 13.3 Tam üretim

FreeCAD veri adımlı koşu; `--veri-yok` DEĞİL, çünkü adlar ve F1 metni yeniden kurulmalı.

`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` arka planda, `.durum` kalıbıyla koşulur.
- Süre ≈ 42 dk (P10.8b'de 2.510 s).
- Logun sonunda "BITTI cikis 0" ve "ek kontrol sorunlu: -" olmalı.

**Beklenen (P108b § 16.3 ile karşılaştır):**
- Veri: 1238 parça, 50 adım; `robot.glb` ve `robot-glb.js` HEAD ile aynı.
- Görünüm: alt adım 91 / 91, uç etiketi 58, hata 0.
- Yazdırma: taşan sayfa 0. PDF ≈ 89 sayfa; sol bant cümlesi uzadığı için ± 1 olabilir.
- Denetim: ASCII 0, zorunlu eksik 0, yasak 0, kopya eki 0, elektrik iddiası 0, **standart numarası 0**. Veri kipi standart hatası
  bugün 18; bu üretimden sonra **0'a inmeli**.
- Sıra: ulaşılamaz 0, giriş girilemez 0, uçuş çarpışan 0, `istisna_bos` 0.
- Onay farkı 0; tarayıcı 50 / 50, konsol 0.

**Üretimden sonra betikle sına:**
- `rehber/veri/rehber-veri.json` ve `.js`'te `ISO 738[1-9]` **0** olmalı.
- CAD'den yeni kuralla ad kurulup veriyle karşılaştırılsın (P108c-kontrol § 6 önerisi):
  - HEAD'e göre parça adı farkı **tam 9**: 7 "Çerçeve cıvatası M3x6 ISO 7380", 2 "Yaka cıvatası M3x6 ISO 7380";
  - 12 taban kablo adı eşit kalmalı.
- Metin farkı yalnız F1 alt adım 3 ve 5 olmalı; üretim tarihi ve süre alanları bunun dışında.
- `planlama/rehber/kontrol.json` değişir.
- Kare farkı yalnız 33.3 ve 33.5 panelli karelerinde, sağdaki panel bölgesinde olmalı.

### 13.4 Zincir 2–10 (P108b § 15.4 sırası)

| # | Komut | Beklenen |
|---|---|---|
| 2a | `tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0, SONUÇ GEÇER |
| 2b | `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi --veri rehber/veri/rehber-veri.json` | 0; ≥ 132 / 132 |
| 2c | `tasarim/freecad/rehber/rehber_denetim.py --kaynak` | 0; 0b ile aynı |
| 3 | `tasarim/freecad/rehber/rehber_denetim.py` (veri) | **0**; ASCII 0, zorunlu eksik 0, yasak 0, elektrik iddiası 0, standart **0** (bugün 18) |
| 4 | `planlama/d158/F10f-dogrula.py` | 0, GECTI (≈ 560 s); JSON'da `ISO 738[1-9]` 0 |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | 0, GECTI (≈ 960 s); `renk_demo` KALDI bilinen |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` | 0, GECTI (≈ 980 s) |
| 6g | `planlama/d158/F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | bilgi |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | 0, GECTI |
| 8 | `planlama/d158/F9b-dogrula.py` | 0, GECER (kuyruk / plan değiştiyse önce demo, § 13.7) |
| 9 | `tasarim/freecad/carpisma_kos.py kontrol` | 0, kayıtla aynı |
| 10 | `planlama/d158/regresyon.py --yazma` | 0, GEÇER, kötüleşen yok |

### 13.5 Gözle bakılacaklar

**F1 cümlesi:**
- Panel (`rehber/` sayfası, adım 33):
  - 33.3 (ön sağ): "… (K55 b) bekle. Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir."
  - 33.5 (ön sol): aynı cümle, artı "(etek ön kuponu sağ banttan kesildi; sol bant için sonucu ayna çıkarımıdır)".
  - Panelde taşma olmamalı; sol bant cümlesi uzadı.
- PDF: adım 33 sayfası (P10.8b'de s. 54–55). Metin tam olmalı, kesik yok.
- F3 / F4: çerçeve (35.5) ve omuz (36.x) notlarında "kupon henüz yok" **duruyor** olmalı.

**Parça listesi:**
- Çerçeve cıvatalarının (F3) ve dirsek yaka cıvatalarının geçtiği adımlarda adlar "… ISO 7380".
- Satır sayısı HEAD ile aynı (`(grup, kod)` ile toplanıyor).
- PDF'te "ISO 7381" araması 0.

**Baskı listesi:**
- Parti 0 D1 / D2 satırları ve toplamlar (§ 12.3).
- "Toplama katılmaz" bloğunda iki etek satırı ve yöntem paragrafı.
- "D / E eski" uyarısı yok.

**Kafa notu** (`tasarim/freecad/lale158/kafa-yerlesim/rapor.html` ve `uygulama-notu.md`):
- Özet "omuz dahil, tek koşu" diyor.
- Atlananlar'da kütle kaynağı cümlesi var.
- 12 V satırı "tabandan, boyundan geçmez"; liste dışı 3 kalem.

**Kuponlar** (isteğe bağlı, dilimleyicide):
- D1 / D2 dış kol 8 mm.
- Etek alt flanşlı: z 3'te çıkıntı yok.
- Etek üst: dar taban, brim.

### 13.6 Kırmızıya düşebilecek yerler

| Yer | Belirti | Ne yap |
|---|---|---|
| Tam üretim denetimi, standart numarası | > 0 | Logdaki adı oku. Yeni bir artırılmış etiketse `--kaynak` da yakalamalıydı: koordinatöre bildir. Bilinen kümeye kayıtsız ekleme yapma. |
| Veri farkı | 9'dan fazla ad ya da F1 dışında metin farkı | `artirma_eki_sil` ya da metin beklenmeyen yeri değiştirdi: dur, bildir. |
| PDF / panel | 33.5'te taşma | Sol bant cümlesi uzun. Kısaltmadan önce bildir. Kısaltılırsa ZORUNLU, onay ve F10l listesi birlikte değişir. |
| F10d / e / f | Parça adı karşılaştırması düşer | GLB'de ISO 738x yok. Hangi denetim düştü, logdan oku, bildir. |
| `--kaynak` | `ARTIRMA KARDESSIZ` | CAD bulgusu: bildir. |
| F9b | hata > 0 | Kuyruk ya da plan değiştiyse demo eski: § 13.7. |
| `F4c-dogrula` 7 | kupon kütlesi sorunu | Bir kupon betiği yeniden koşmuş. `Y2b-baski.py` → `F4c-partiler` → `F4c-liste` → `F4c-dogrula` (`Y2b-baski.json` değişmemeli). |

### 13.7 Plan, kuyruk, demo (hazır metinler)

**Sıra:**
1. Plan hücresi.
2. Kuyruk.
3. Kuyruk değiştiği için `py -3 -B -X utf8 tasarim/cad/demo_uret.py`. Yalnız `tasarim/Robot-Tasarim-Demosu.html`'i yazar; fark yalnız
   gömülü sha'lar olmalı.
4. `planlama/d158/F9b-dogrula.py`: 0, hata 0.

**`planlama/dongu-158.md` P10.8 Durum hücresine eklenecek metin.** Metinde dikey çizgi yok; satırın sütun ayırıcı sayısı HEAD ile aynı
kalmalı. Son cümleyi yalnız zincir gerçekten geçtiyse yaz.

"P10.8c (19.11, `planlama/d158/P108c-gunluk.md`, bir düzeltme turuyla): rehberde yanlış standart numarası düzeldi (FreeCAD 1.1 kopya
etiketinde sondaki sayıyı artırıyordu; ad koddan geri alınıyor, 9 ad ISO 7380; standart numarası ve artırma zinciri denetimi, 17 bozma).
M7 D / E kuponu güncel dirsekten okunuyor ve yeniden üretildi, tazelik istisnası kalktı. Etek ön bandı kuponu (K55): rehberin iki
parçalı yolu kuponda ve tam modelde aynı eğri; deneme hareket kısıtlı, ilk deneme flanşlı biçim; Parti 0 toplama katılmaz bloğunda.
Rehber F1 ön bantlarda 'kuponla denenmedi' notu. Baskı listesi ve F4c yeni M7 kütleleriyle yenilendi; F4c-dogrula'ya kupon kütlesi
denetimi eklendi. Kafa-yerleşim notu üreticisi düzeltildi (12 V, liste dışı kalem, omuz anlatısı kayda bağlı) ve yeniden üretildi.
Tam üretim ve zincir 2–10 geçti."

**`planlama/d158/karar-kuyrugu.md`:**

- **"P10.8b rehber açıklarından" bloğu, ISO numarası maddesine eklenecek:**
  "→ 19.11 P10.8c: **kapandı** (`P108c-gunluk.md` § 2, § 12.5; `kopya_eki_sil` → `artirma_eki_sil`, `--kaynak` standart / artırma
  denetimi; CAD etiketi ve `robot-montaj.step` etiketi değişmedi)."
- **P10.8a "M7 D / E onarımı" maddesine eklenecek:**
  "→ 19.11 P10.8c: **kapandı** (`P108c-gunluk.md` § 3, § 12.3). D1 / D2 güncel dirsekten yeniden üretildi; E'nin STL'si 15.10 baytında,
  geometri güncel. Baskı listesi ve F4c yeni kütlelerle yenilendi, eski uyarı kalktı."
- **Aynı maddede düzeltilecek satır (≈ 1893):**
  - Eski: `Denetim: py -3 tasarim/freecad/test/kupon_tazelik.py ("BİLİNEN ESKİ").`
  - Yeni: `Denetim: py -3 tasarim/freecad/test/kupon_tazelik.py (P10.8c'den beri istisna yok; her fark ESKİ).`
  - Neden: "BİLİNEN ESKİ" çıktısı artık yok.
- **K55 bölümüne not:**
  "Not (P10.8c, 19.11.2026; `P108c-gunluk.md` § 4, § 12.4): etek ön bandı kuponu `tasarim/freecad/kabuk/etek_kuponu.py`. Üst parça ön
  bant dilimi; alt parça orta bant dili + braket dik ayağı + taşıyıcı (perçin somunlu ya da flanşlı). Rehberin iki parçalı yolu kuponda
  ve tam modelde aynı ortak hacim eğrisi (perçin somunu dz 0,5–8,5 mm, en çok ≈ 10 mm³; yan bacak serbest). Deneme hareket kısıtlı:
  önce yalnız x, sonra yalnız −z, üst parça döndürülmeden. 'Geçti' kanıt; 'geçmedi' belirsiz (K55 b ya da tam bant). Rehber F1
  'kuponla denenmedi' diyor. Basılmadı."
- **Kafa-yerleşim açık işine eklenecek:**
  "→ 19.11 P10.8c: **kapandı** (`P108c-gunluk.md` § 5, § 12.1). Üretici düzeltildi: 12 V satırı; liste dışı kalem (3; L USB-A dirsek
  14.11 kararıyla çıktı); omuz anlatısı `carpisma-sonuc.json`'a bağlı (`tek_kosu`). `uygulama-notu.md` ve `rapor.html` birlikte yeniden
  üretildi."
- **Yeni iş maddeleri** (karar değil, iş):
  - "`kafa-yerlesim/uygulama-ivme.json` 09.11 koşusundan. Not kütleyi 26.120,6 g diyor; güncel montajla 26.235,1 g (fark 114,5 g).
    Devrilme payları yeni montajla hesaplanmadı. `uygulama_ivme.py` (FreeCAD, `montaj/moduller`) yeniden koşulmalı, sonra
    `uygulama_rapor.py` (`P108c-gunluk.md` § 12.1)."
  - "`planlama/d158/F4c-rapor.html` hiçbir betikle üretilmiyor ve Parti 0 sayıları P10.8c'den önceki (D1 40,9–87,9 g, D2 41,4–86,2 g,
    toplam 257,4–420,0 g). Tarihli eski görüntü diye bırakılsın ya da başına 'eski görüntü; güncel: baski-listesi.md /
    F4c-partiler.md' satırı eklensin."
  - "`m7_kuponlari.py`'de satır içi sabitler kaldı. `dirsek_parcalar.py`'de de satır içi oldukları için okunamıyorlar; liste
    `P108c-gunluk.md` § 12.5'te. Koruma: D1 ↔ FCStd hacim karşılaştırması."

### 13.8 Commit'e girecek dosyalar

Dosyalar `git add <yol>` ile tek tek eklenir. Sonra `git diff --cached --name-only` çıktısı § 13.1'deki yasak listeyle kesişmemeli.

**Rehber ve denetim (5):**
- `tasarim/freecad/rehber/rehber_metin.py`
- `tasarim/freecad/rehber/rehber_denetim.py`
- `tasarim/freecad/rehber/rehber_kritik_onay.json`
- `planlama/d158/F10l-birlesim.py`
- `planlama/d158/F4c-dogrula.py`

**Kuponlar (12):**
- `tasarim/freecad/test/m7_kuponlari.py`
- `tasarim/freecad/test/kupon_tazelik.py`
- `tasarim/freecad/test/README.md`
- `tasarim/freecad/test/m7-kupon-sonuc.json`
- `tasarim/freecad/test/m7-kuponlari.step`
- `tasarim/freecad/test/stl/kupon-d1-kelepce-kesiksiz.stl`
- `tasarim/freecad/test/stl/kupon-d2-kelepce-bosaltmali.stl`
- `tasarim/freecad/kabuk/etek_kuponu.py` (yeni)
- `tasarim/freecad/kabuk/etek-kuponu.json` (yeni)
- `tasarim/freecad/kabuk/stl/etek-kuponu-ust.stl` (yeni)
- `tasarim/freecad/kabuk/stl/etek-kuponu-alt.stl` (yeni)
- `tasarim/freecad/kabuk/stl/etek-kuponu-alt-flansli.stl` (yeni)

**Kafa-yerleşim (4):** `tasarim/freecad/lale158/kafa-yerlesim/` altında
- `uygulama_rapor.py`
- `uygulama_metin.py`
- `uygulama-notu.md`
- `rapor.html`

**Baskı listesi ve F4c (3):**
- `planlama/baski-listesi.md`
- `planlama/d158/F4c-partiler.json`
- `planlama/d158/F4c-partiler.md`

`Y2b-baski.json` değişmedi.

**Günlük ve kontrol:**
- `planlama/d158/P108c-gunluk.md`
- `planlama/d158/P108c-kontrol.md`
- kontrol ajanının ikinci turu varsa onun dosyası

**Üretim çıktıları:**
- `rehber_uret.py`'nin yazdığı, `git status`'ta görünen `rehber/` dosyaları
- `planlama/rehber/kontrol.json`
- zincir JSON'ları: F10a / F10d / F10e / F10f
- regresyon `--yazma` ile değişirse `regresyon.json` / `regresyon-son-kosu.json`

**Kayıtlar:**
- `planlama/dongu-158.md`
- `planlama/d158/karar-kuyrugu.md`
- `tasarim/Robot-Tasarim-Demosu.html` (demo yeniden üretildiyse)

**Push öncesi:** `.git/hooks/pre-push` kancası koşar (yerel yol, takma ad, e-posta, anahtar, IBAN / telefon, ekip adı). Bulgu çıkarsa
push etme, satırı düzelt.

## 14. Kapanış (§ 13 tarifiyle; 19.11 akşamı başladı, 20.11 gecesi bitti)

Kontrol tur 1 GEÇER (`P108c-kontrol.md`). Kaynak dosyaların son değişikliği 21:29 (`m7_kuponlari.py`, yalnız yorum); sonra yalnız
`kupon_tazelik.py` 22:40'ta yorum satırı (T1 notu: durum listesinden "BILINEN ESKI" çıktı). Bu dosya rehber üretiminin girdisi değil
(`rehber_uret.py` ve zincir betikleri onu çağırmaz); t1 / t2 bu değişiklikten sonra yeniden koştu.

**Ön sınama** (19.11 21:42–21:44, son kaynak değişikliğinden sonra): 0a–0h hepsi çıkış 0 (`--bozma-denemesi` 347 / 347, kablo 114 / 114,
kablolar 174, F10l eklenen 2 / silinen 2, tazelik TAZE 16 + 4 / 4, F4c GECTI 1–7 + 7 / 7). Veri kipi üretimden önce çıkış 1, standart 18
(beklenen).

**Tam üretim** (`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py`, FreeCAD veri adımlı): 21:44:32–22:36:31, 3.119 s, çıkış 0,
"ek kontrol sorunlu: -". Veri 1238 parça, 50 adım; `robot.glb` / `robot-glb.js` HEAD ile baytça aynı. Alt adım 91 / 91, uç etiketi 58,
taşan yok, PDF 89 sayfa. Denetim: ASCII 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0, standart numarası 0, elektrik iddiası 0; sıra
ulaşılamaz 0, giriş girilemez 0, uçuş çarpışan 0, `istisna_bos` 0; tarayıcı 50 / 50, konsol 0. Bellek: boş fiziksel en düşük 0,52 GB,
süreç çalışma kümesi en çok ≈ 1,7 GB; süreç kaybolmadı, bellek hatası yok.

**Üretimden sonra:**
- `ISO 738[1-9]`: `rehber-veri.json` 0, `.js` 0, `planlama/rehber/kontrol.json` 0, PDF metni 0 (ISO 7380 104 kez).
- Veri farkı (HEAD'e göre, 14 alan): 9 parça adı (7 "Çerçeve cıvatası M3x6 ISO 7380", 2 "Yaka cıvatası M3x6 ISO 7380"), F1 alt adım 3
  ve 5 metni, üretim tarihi ve iki süre alanı. Başka fark yok.
- Kareler: 33.3 ve 33.5'te fark yalnız sağ panel bölgesinde (x 1019–1382). 17.5'te 73 piksel, en çok 7 / 255: görüntüleme gürültüsü,
  içerik değişmedi. Başka kare değişmedi.
- PDF s. 54–55 (adım 33.3 / 33.5): F1 cümlesi tam, kesik yok; 33.5'te ayna çıkarımı ibaresi var.

**Zincir 2–10.** İlk deneme 19.11 22:40'ta başladı; t1, t2, 2a geçti, 2b koşarken iş durduruldu (çıktısı yok). Zincir 20.11'de baştan
koşuldu (depo kökünden, `PYTHONIOENCODING=utf-8 py -3 -B -X utf8`):

| # | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 0a | `carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |
| t1 / t2 | `kupon_tazelik.py` / `--bozma-denemesi` | 0 / 0 | TAZE (16) / 4 / 4 |
| 2a | `rehber_kablo.py --veri …` | 0 | SONUÇ GEÇER |
| 2b | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 132 / 132 |
| 2c | `rehber_denetim.py --kaynak` | 0 | CAD 947; standart HATA 0; artırma silinen 9, kardeşsiz 0; onay farkı 0 (220 / 258 / 1199) |
| 3 | `rehber_denetim.py` (veri) | 0 | ASCII 0, zorunlu eksik 0, yasak 0, kopya eki 0, standart **0**, elektrik 0 |
| 4 | `F10f-dogrula.py` | 0 | GECTI (587 s); JSON'da `ISO 738[1-9]` 0 |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | GECTI (1009 s); `renk_demo` KALDI (bilinen karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 0 | GECTI (971 s) |
| 6g | `F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | 0 | bilgi |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | GECTI (437 s) |
| – | plan hücresi + kuyruk (§ 13.7), sonra `tasarim/cad/demo_uret.py` | 0 | demo farkı yalnız gömülü sha'lar |
| 8 | `F9b-dogrula.py` | 0 | GECER (hata 0) |
| 9 | `carpisma_kos.py kontrol` | 0 | kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | GEÇER, kötüleşen yok (tilt 3,78, pan 2,26 iyileşti); `regresyon.json` değişmedi |

**Kayıtlar:** `dongu-158.md` P10.8 Durum hücresine § 13.7 metni (son cümle dahil; sütun ayırıcı 6, HEAD ile aynı). `karar-kuyrugu.md`:
ISO maddesi, M7 D / E maddesi (+ "BİLİNEN ESKİ" satırı düzeltildi), K55 notu, kafa-yerleşim açık işi, yeni blok "P10.8c kapanışından
açık iş" (üç madde). § 5 günlük satırı yazılmadı (tarifte yok; orkestratörün işi).
