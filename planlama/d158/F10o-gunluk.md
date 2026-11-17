# F10o · P10.7b2g günlüğü: boyun tüneli deneme parçası

Açılış 17.11.2026 05:49 (uygulama ajanı; saat okundu). Taban: paket `9b019d2` (P10.7b2f) üstünde açıldı; çalışırken `lale-duzeltme` =
uzak = `3bc5aa9`'a ilerledi (P10.9b, başka ajan; iki commit yalnız `karar-kuyrugu.md`, `F9c-uret.py`, `P109b-gunluk.md`'ye dokunuyor,
bu paketin dosyalarına değil; yamanın ve `F10l-birlesim.py`'nin `9b019d2` tabanı geçerli; düzeltme turu 1, D4). Kaynak düzeyinde kapanış
17.11.2026 ≈ 06:05. Commit yok, push yok, tam rehber üretimi ve doğrulama zinciri koşmadı. FreeCAD yalnız bu paketin betiğiyle (tek
süreç, yalnız `kafa-montaj.FCStd`) iki kez koştu. Sırada: bağımsız kontrol → (isteğe bağlı) rehber yaması + onay + üretim → commit / push.
Girdi: brief (P10.7b2g), hazırlık notu § 3, `kablolama-on-kararlar.md` §4 K14 / KT4, `rehber_metin.py:973-978`.

Dokunulmayanlar: CAD model ve tarama kaynakları (`kafa7_parcalar.py`, `kafa_parcalar.py`, `kafa_montaj.py`, `kafa-montaj.FCStd` (md5
`e7f7ba7e…` JSON'da; koşulardan sonra git'te değişmemiş), `arayuz.py`, `carpisma*`); `kablolama-on-kararlar.md` (satır sayısı korunsun
diye hiç); `karar-kuyrugu.md`, `F9c-uret.py`, `P109b-gunluk.md` (başka ajan); üretilmiş çıktı (`rehber/veri/`, `rehber/goruntu/`,
`planlama/rehber/`, PDF); eski kir (19 dosya) olduğu gibi.

## 1. Tünel nerede modellenmiş (CAD'den)

Tünel tek parçada değil, üç parçaya yayılıyor (hepsi kafa modülünün Govde / Pan grubunda, 1,58 m'de 125 cm'den aynen):

| Bölüm | Parça | Kaynak satırı | Geometri (kafa yereli, mm) |
|---|---|---|---|
| Alt çıkış (arka yüz) | Servo yuvası | `kafa7_parcalar.py:148` | x −14…6, y 6…18 (üstü 45°), arka duvardan z −31…−26,5 |
| Arka kanal | Servo yuvası | `:143` | x −14…6, y 6…40, z −27…−19,2 |
| Kanal üstü → kablo odası | Servo yuvası | `:144-145` | y 40…46, z −23…−10,4; tavan 45° |
| Kablo odası | Rulman yuvası (servo yuvası üstü ile alt 6808 arası) | `:170` | halka r 20 (mil dışı) … 27,5, y 46…62 |
| Mil penceresi | Boyun mili (ev pozu, pencere −z'de) | `:244` | x −10…10, y 53…63 (üstü 45° ile 10'a daralır), z −25…0 |

İki dik dönüş: alt çıkış (yatay) → kanal (dik); kanal üstü / oda → mil penceresi (yatay, eksene doğru).

## 2. Parça (`tasarim/freecad/kafa/boyun_tunel_deneme.py`), ilk sürüm: kutu, ekler, ölçü ve kütle § 8'de değişti

- Kaynak: `kafa-montaj.FCStd` (kafa_montaj.py çıktısı) içindeki "Servo yuvasi", "Rulman yuvasi", "Boyun mili" katıları; yerel koordinat
  betikte doğrulanır (servo yuvası y 3…46). Parça = (üç parçanın birleşimi + iki baskı eki) ∩ kutu x −18…12, y 3…66, z −31…−12.
  Kesit elle çizilmedi.
- Baskı ekleri (kablo yoluna girmez, sayısal kanıt § 3): (1) dolgu r < 20, y 45,9…48: mil diski ile servo yuvası üstü arasındaki 1,9 mm
  boşluk (horn yeri; kablo geçmez), mili parçaya bağlar ve disk altını köprüye çevirir; (2) alt 6808'in yeri r 20…26, y 64…66: gerçekte
  oda tavanı rulmandır, parçada da kapalı.
- Kutunun ön yüzü z −12: mil içi (r < 16) ve pan servo kablo yarığı (x −6…4, y 5…14) ön yüze açık çıkar; fiş mil ucundan çıkarılır.
- Baskı: kaynak +Y yukarı (gerçek parçaların yönü), servo yuvası tabanı (y 3) tablada. STL koordinatı (x, −z, y − 3).
- Çıktı: `tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl` (2.040 üçgen, md5 `5133b18f…`), `tasarim/freecad/kafa/boyun-tunel-deneme.json`.
- (İlk sürüm, § 8'de 40 × 50 × 93 / ≈ 68 g oldu.) Parça: 30 × 18 × 63 mm, tek katı, geçerli; hacim 17,78 cm³; %100 dolulukla 22,6 g, tahmini 13,9 g; ≈ 24 dk (test/m7_kuponlari.py
  yöntemi: 4 çevre + %25 dolgu, `PETG_HACIM_HIZI` × 1,3); tabla teması 514 mm². Malzeme beyaz PETG (ölçü denemesi; asıl servo yuvası
  PETG-CF, kıt filament harcanmasın).
- 46° üstü aşağı bakan yüz 543 mm², hepsi köprü: z 61 (198 mm², rulman dolgusu altı, 6 mm radyal), z 42,9 (161 mm², dolgu altı, kanal
  üstü açıklığı üzerinde ≤ 20 mm), z 11 (72 mm², servo kablo yarığı tavanı, 10 mm), z 59–60 (pencere üstü 10 mm ve rulman yuvası
  basamağı), z 15 (24 mm², alt çıkış üstünün düz kısmı, 8 mm). Bu köprülerin üçü gerçek parçada da var (aynı yönde basılıyor).

## 3. Ölçüm ve doğrulama

Ölçüm: nokta içeride mi taraması (0,02 mm adım) kaynak kesişiminde (`S`, eksiz) ve parçada (`P`) aynı noktalarda.

| Ölçü | Beklenen (kayıt) | CAD'den (kaynak) | Parça | Fark kaynak ↔ parça |
|---|---|---|---|---|
| Kanal kesiti | 20 × 7,8 | 19,96 × 7,76 (aralık −13,98…5,98 / −26,98…−19,22) | aynı | 0,000 |
| Kanal boyu (sabit kesit) | ≈ 34 | 33,95 (y 6,05…40,0) | aynı | 0,000 |
| Kanal ekseninde boş boy (kanal üstü dahil) | — | 37,86 (y 6,02…43,88) | aynı | 0,000 |
| Alt çıkış | 20 × 12 | 19,96 × 11,96 | aynı | 0,000 |
| Mil penceresi | 20 × 10 | 19,96 × 9,96 (mil tek başına, kutusuz da aynı) | aynı | 0,000 |
| Kablo odası radyal | — | 7,42 (z −27,48…−20,06) | aynı | 0,000 |

- Görünen −0,04 farklar tarama adımından (iki uçta 0,02): CAD değeri beklenene eşit (20 × 7,8, 34, 20 × 12, 20 × 10). Hazırlık notundaki
  değerlerle **fark yok**.
- Tolerans 0,05 mm: **GEÇER** (9 / 9 ölçüm, fark 0,000).
- Eklerin kablo yoluna girmediği: kanal, pencere ve oda bölgelerinde malzeme hacmi kaynakta ve parçada aynı (160,399 / 113,637 / 0,000 mm³).
- STL: hacim farkı %0,003, sınır kutusu farkı 0,0000 mm, ağ kapalı, manifold dışı yok: **GEÇER**.
- Fiş payı (bilgi): USB-A erkek fiş ≤ 13 × 7 ↔ kanal 20 × 7,8 (kalınlıkta 0,8 mm); micro HDMI ≤ 18 × 7, boy ≲ 30 ↔ 20 × 7,8 ve iki dik
  dönüş. Baskı toleransı (±0,2) gerçek parçadakiyle aynı profille basılırsa aynı olur; deneme bu yüzden gerçek profille.

Koşular (boş bellek önce 2,99 GB / 2,91 GB; tek `freecadcmd`, kilit alındı ve "boş"a döndü, UTF-8 BOM'suz):

| Koşu | Saat | Süre | Çıkış |
|---|---|---|---|
| `freecadcmd run_fc.py` (FC_SCRIPT=`kafa/boyun_tunel_deneme.py`) 1 | 05:54 | 26 s | 0 (pencere x ölçüsü kutu sınırına taşıyordu → kesintisiz aralık, mil tek başına da ölçüldü) |
| aynı, 2 (son) | 05:55 | 32 s | 0 |

## 4. Rehber metni: ayrı yama (`planlama/d158/F10o-rehber-metin.patch`), UYGULANMADI

Bu gece tam üretim koşamayabileceği için rehber metni çalışma ağacına bağlanmadı; değişiklik tek yamada, `git apply` ile uygulanır:

- `tasarim/freecad/rehber/rehber_metin.py` K2 alt adım 5 (boyun demeti), KT4 cümlesinden sonra iki cümle (eski cümle aynen kalır,
  `rehber_denetim.py` zorunlu kalıbı "Demeti kurmadan önce basılmış tünel deneme parçasında" bozulmaz):
  "Parça: Boyun tüneli deneme parçası (`tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl`; baskı listesinde tolerans kuponlarının
  yanında, beyaz PETG, ≈ 14 g, destek gerekmez)." ve "Fişleri parçanın arka yüzündeki alt çıkıştan sok, kanaldan yukarı ve mil
  penceresinden geçirip mil ucundan çıkar: önce hub uzatmasının (U03) USB-A erkek fişi, sonra HDMI'nin (H02) micro HDMI ucu, sonra tilt
  servo kablosunun (S10) 3 pinli fişi; hoparlör (AU3) ve 12 V (G17) fişsiz geçer, deneme gerekmez."
  Fiş listesi `planlama/adim3/kablolar.json` (U03 `hazir_kablo.sart` 13 × 7, `gecis_sirasi` 1; H02 7 / 18 / 30, `gecis_sirasi` 2; S10
  servo kablosu; AU3 / G17 fişsiz, `kablolama-on-kararlar.md` §4 sıra maddesi). "Final değil" durumu değişmedi (metin yalnız eklendi).
- `planlama/d158/F10l-birlesim.py`: varsayılan taban `9b019d2`, `B2G_EKLENEN` 2 cümle (silinen yok).

Yama uygulanmış hâlde denendi, sonra geri alındı (`git checkout`; çalışma ağacında iki dosya değişmemiş):

| Sınama (yama uygulanmış) | Sonuç |
|---|---|
| `rehber_denetim.py --kaynak` | 1: yalnız **onaylı kritik girdi farkı 2** (K2 alt adım 5 is_, iki eklenen cümle); ASCII 0, zorunlu 0, yasak 0, çıplak sayı 0, tamlık eksik 0. İlk taslakta ASCII 7 (yol ve "desteksiz", "denenmez" gibi izin listesinde olmayan kelimeler) → yol ters tırnağa alındı, kelimeler değiştirildi; `ASCII_TAMAM`'a ekleme yapılmadı |
| `F10l-birlesim.py` (taban 9b019d2) | GEÇER: cümle 1099 → 1101, eklenen 2 / 2, silinen 0 / 0; eski taban b5fc255 ile beklendiği gibi KALIR (2) |
| `kablolar_denetim.py` | GEÇER |
| `rehber_kablo.py` | GEÇER (onay kaydı kablo bölümü tutuyor) |

Yamayı bağlama sırası (bağımsız kontrolden sonra): `git apply planlama/d158/F10o-rehber-metin.patch` →
`py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile` (2 eklenen metin girdisi; yeni kritik birimli değer
yok, "≈ 14 g" birimli; kontrol bakmalı) → `rehber_denetim.py --kaynak` 0 → üretim (§ 6) → zincir.

## 5. Kayıtlar

- `planlama/baski-listesi.md`: "Tolerans kuponları (Parti 0)" bölümünün sonuna "Kablo deneme parçası" alt bölümü ve tek satırlık tablo
  (`| ☐ |` biçimi kullanılmadı: o satırlar Y2b'ye bağlı parça satırlarıdır, deneme parçası toplama girmez). Liste kısmen üretici
  çıktısı (`baski_listesi_guncelle.py` yalnız kabuk / kafa `| ☐ |` satırlarını yazar); kupon bölümü elle yazılmış metin, ekleme oraya.
  `F4c-dogrula.py`: **SONUÇ GEÇTİ** (1–6, 5b sabit nokta dahil).
- `planlama/dongu-158.md` § 5 satırı.
- Sonuç raporu özeti (`F9c-uret.py` P10.7 "Kalan" listesinden "boyun tüneli deneme parçası"nın çıkması): **yapılmadı**, dosya bu gece
  başka ajanda. Kayıt ajanı / sonraki pakete.

## 6. Tam üretim gerekiyor mu

- **Yama uygulanmazsa: hayır.** Bu paketin çalışma ağacındaki değişiklikleri (yeni betik + STL + JSON, baskı listesi, plan, günlük, yama
  dosyası) rehber verisine, karelere ve PDF'e girmez; rehber üretimi ve zincir gerekmez, commit üretimsiz atılabilir.
- **Yama uygulanırsa:** yalnız metin değişir (K2 alt adım 5 is_); CAD / mesh / kadraj değişmez, yazdırma 3B kareleri (`rehber/goruntu`,
  `?sahne=1`) metinden bağımsız. FreeCAD veri adımı gerekmez: `rehber_gorunum.isle()` metin alanlarını FreeCAD'siz yazar (F7d'de
  bağımsız doğrulanmış yol). Depodaki en hafif tam yol:
  `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (FreeCAD açmaz; bütün kontrol / yazdırma kareleri, telefon, PDF,
  denetim, sıra yine çekilir; önceki koşular 1862–2639 s, ≈ 31–44 dk). Kareleri yeniden çizmeden yalnız metin + PDF yenileyen yol
  depoda **yok**: `--veri-yok --gorsel-yok` yalnız `rehber-veri.json/.js` metin alanlarını yazar (saniyeler), PDF / `kontrol.json` /
  kontrol kareleri eski kalır, zincirde PDF ↔ veri karşılaştırması olan denetimler için yetmez; `--adimlar N` kısmi koşu
  `kontrol.json`'u kısmi yazar (tek-adım sınamaları "yok" olur). Bu ikisi commit için önerilmez.

## 7. Açık kalanlar

- `F9c-uret.py` "Kalan" listesi ve sonuç raporu özeti (başka ajanın dosyası).
- `kablolama-on-kararlar.md:148-149` ve KT4 satırı parçanın dosya adını anmıyor (satır sayısı riski yüzünden dokunulmadı; aynı satır
  içinde düzenleme satır sayısını korur, `kablolar_denetim` kaynak sınamasıyla birlikte yapılmalı).
- Parçanın basılması ve fiş denemesi (fiziksel, kablolar gelince). Sonuç KT4'e ve rehber K2 kontrol maddesine (`rehber_metin.py:1011`).
- `test/README.md` deneme parçasını anmıyor (parça kafa modülünün klasöründe; kuponlar `test/`'te): istenirse bir satır.

## 8. Düzeltme turu 1 (kontrol `planlama/d158/F10o-kontrol.md` GEÇMEZ; 06:23–06:40)

Orkestratör kararları uygulandı. Betik `tasarim/freecad/kafa/boyun_tunel_deneme.py` (satırlar bu turdaki dosyaya göre):

| Bulgu | Ne yapıldı | Yer |
|---|---|---|
| E1 mil içine dönüş yoktu | Kutu x −20…20, y 3…96, z −31…20 (mil dış çapı r 20 ve flanş üstü y 96): fiş pencereden Ø32 milin içine girip karşı duvara (z +16…20) çarpar ve yukarı döner; mil ucu y 96'da açık | `:32-33` `KUTU` |
| E2 dolgu basamağı kapatıyordu | Tünelin gerçek komşuları aynı FCStd'den kaynağa eklendi: pan horn (r 12,5, y 44,6…47,9; FCStd'den ölçüldü), horn vidası, mil-horn cıvataları, pan servosu ve çıkış mili. Dolgu yalnız y 46…47,9, r < 20 ve kanal üstü izinin (x −14…6) **dışında**; izde yalnız gerçek horn kalır | `:30-31` `KOMSU`, `:79-86` `EKLER` |
| Genel ilke | Fiş yolu bölgesi `YOL` (alt çıkış, kanal, kanal üstü, basamak y 44…49 iz içinde, kablo odası, pencere, mil içi); gerçekte boş kısmı `YOL_BOS = YOL − kaynak`. Her ekin `YOL_BOS` ile kesişimi, kaynaktan kesilen hacim ve basamaktaki boş hacim ölçülür; `ekler_kablo_yoluna_girmiyor` bunlardan | `:88-96`, `:181-195` |
| D1 birikme | Yama: "geçen kabloyu parçada bırak, sonraki fişi onun yanından geçir: önce tünel boşken U03, sonra U03'ün kablosu tünelde yerindeyken H02, sonra iki kablonun yanından S10" | `F10o-rehber-metin.patch` |
| D2 tabla teması | 0,2 mm dilim / 0,2 (0,21 değil); ayrıca eğri yüzlerde `BoundBox` gevşek olduğu için ölçü ve tabla hizası `optimalBoundingBox()` | `:219-220`, `:253` |
| D3 ısıl gömme deliği | Cümle düzeltildi: kaynak parçaların vida / ısıl gömme deliklerinin kesitleri parçada kalır, kullanılmaz (delik gerçek parçanın geometrisi, çıkarılmadı) | `baski-listesi.md:203-204` |
| D4 taban SHA | Başlık düzeltildi (`3bc5aa9`) | bu günlük, başlık |
| N2 pan servo kablosu | CAD doğruluyor: `kafa7_parcalar.py:146` "pan servosu kablosu → kanal" yarığı (x −6…4, y 5…14) kanala açılıyor, kablo kanaldan ve alt çıkıştan iner. `kablolar.json` S09 (uzatma) güzergâh yazmıyor, çelişmiyor. Yamaya eklendi; düzeltme turu 2'de (yeniden kontrol Y1: yarık yeni parçada ön yüze açılmıyor) şu hâle geldi: "Önce bir servo kablosunu alt çıkıştan kanala sok, ucunu kanal dibindeki servo kablo yarığına it ve yerinde bırak" | yama |
| N1 basamak riski | Tasarım değişmedi; açık risk olarak buraya ve `dongu-158.md` § 5'e yazıldı: deneme U03 / H02 için "geçmez" diyebilir; yedek yol (fişsiz geçirme, şerit HDMI) ayrı pakette | § 7, plan |

**Yeni parça:** 40 × 50 × 93 mm (X × Y × Z baskı), tek katı, geçerli; hacim 119,59 cm³; %100 dolulukla 151,9 g, tahmini 67,5 g;
≈ 115 dk; tabla teması 2.000 mm² (40 × 50, tam taban). STL 14.454 üçgen, md5 `fae01178…`; STL ↔ BRep hacim farkı %0,002, kapalı, manifold.
Kaynak katıları: servo yuvası, rulman yuvası, boyun mili + komşular (pan servosu MG996R, çıkış mili, horn, horn vidası, mil-horn cıvatası).
Ekler (hepsi fiş yolu dışında, kesişim 0,0000 mm³): dolgu 969 mm³, rulman (iki 6808 ve arası, r 20…26, y 64…82) 8.247 mm³, servo altı
(servo cebi y 3…5) 1.228 mm³. Bilgi: izin yanlarında (x < −14, x > 6) 1,9 mm katmandaki dolgu 126,7 mm³ (orkestratör: yanlarda kalabilir).

**Baskı:** 46° üstü aşağı bakan yüz 1.613 mm²: z 61 (459 mm², rulman dolgusu altı, oda üstünde r 20…26 halka köprü), z 41,6 (434 mm²,
**horn altı**: horn r 12,5, çıkış mili r 6,5 üstünde; r 6,5…12,5 arası 6 mm konsol halka, altında servo üstüne 3 mm boşluk; fiş yolunda
değil), z 44,9 (357 mm², mil diski altı, izde x'te 20 mm köprü), z 43 (110 mm², dolgu altı horn boşluğu kenarı), z 11 (88 mm², servo kablo
yarığı tavanı, 10 mm), z 59 (77 mm², rulman yuvası basamağı). Destek gerekmez; tek gerçek konsol horn altı halkadır (6 mm, sarkarsa servo
üstündeki boşluğa sarkar, fiş yolunu daraltmaz). İstenirse o halkaya dilimleyicide boyalı destek.

**Ölçü doğrulaması (kaynak ↔ parça, 0,02 mm adım; 25 ölçüm, en büyük fark 0,02, tolerans 0,05: GEÇER):**

| Ölçü | Kaynak | Parça |
|---|---|---|
| Kanal / boy / alt çıkış / pencere / oda | aynı § 3 (20 × 7,8; 34; 20 × 12; 20 × 10; 7,42) | aynı |
| Basamak y 45 (servo yuvası üstü içi), x −10 / −4 / 0 / 4 | z −22,98…−7,52 / −11,86 / −12,50 / −11,86 | aynı (x 0: −12,52) |
| Basamak y 46,95 (horn katmanı) | z −25,60…−7,52 / −27,20…−11,86 / −27,48…−12,52 / −27,20…−11,86 | aynı |
| Basamak y 48,5 (mil diski) | z −25,60…−17,34 / −27,20…−19,60 / −27,48…−20,00 / −27,20…−19,60 | aynı (x 0: −20,02) |
| Mil dönüşü y 58, x 0 (oda → pencere → mil içi → karşı duvar) | z −27,48…15,98 | aynı |
| Mil içi y 70 / 90 (x 0, z 0) | Ø 31,96 | aynı |
| Basamakta (y 44…49, iz) boş hacim | 1.311,035 mm³ | 1.311,035 mm³ |
| Bütün fiş yolunda boş hacim | 53.904,187 mm³ | 53.904,187 mm³ |

y 46,95'teki z aralığı horn kenarında (r 12,5) bitiyor: kontrolün gördüğü 1,9 mm'lik katman artık parçada da açık (önce r 20'de kapanıyordu).

**Koşular:** `freecadcmd` (tek süreç, yalnız `kafa-montaj.FCStd`; kilit alındı, "boş"a döndü) 06:24 (336 s, çıkış 0; ek ölçümünde iz
bölgesi kanal üstü izinden geniş tanımlıydı ve `BoundBox` gevşekti → düzeltildi) ve 06:30 (333 s, çıkış 0, son). Boş bellek 2,82–2,91 GB.

**Yama (UYGULANMADI), yeniden kuruldu:** 3 cümle (parça / ≈ 68 g; N2 servo kablosu; D1 sıra ve birikme). Yamalı hâlde
`rehber_denetim.py --kaynak` yalnız onay farkı 3 (ASCII 0; ilk taslakta "sonrakini", "dururken", "ikisinin" izin listesinde değildi,
kelimeler değiştirildi), `F10l-birlesim.py` GEÇER (1099 → 1102, eklenen 3 / 3), `kablolar_denetim.py` GEÇER, `rehber_kablo.py` GEÇER.
Yamasız ağaçta `--kaynak` 0, `F10l-birlesim.py` GEÇER, `git apply --check` temiz. Onay yenilemesinde girecek yeni birimli değer: ≈ 68 g.

**Kontrolün yeniden bakması gerekenler:** komşu katıların seçimi (pan servosu ve vidalar parçada dolu; servo yarığı ön yüzde açık kalıyor
mu: servo gövdesi z −10,4'ten başlar, yarık z −19,5…−10,3, açık); kutunun x ±20'de kesmesi (oda yanları x ±20'de hâlâ açık, N5);
horn altı konsolu; `YOL` bölgesinin tanımı (basamak izi x −14…6, orkestratör kararıyla).

## 9. Kapanış: düzeltme turu 2, yama, demo, üretim, zincir, commit (17.11.2026 06:43–; saatler sistemden)

Kapanış ajanı (b2f'nin üretimini koşan ajan); HEAD = uzak = `3bc5aa9`. Yeniden kontrol (`F10o-kontrol.md` sonu) **DÜZELTMEYLE GEÇER**.

### 9.1 Düzeltme turu 2 (yeniden kontrol Y1; yalnız metin)

- Yama `git apply` ile uygulandı (temiz). Servo kablosu cümlesi iki yerde birebir aynı biçimde değişti (`rehber_metin.py` K2 alt adım 5,
  `F10l-birlesim.py` `B2G_EKLENEN`): "Önce bir servo kablosunu alt çıkıştan kanala sok, ucunu kanal dibindeki servo kablo yarığına it
  ve yerinde bırak (pan servosunun kendi kablosu robotta bu kanaldan iner)." Eski "ön yüzündeki yarıktan kanala indir" yeni parçada
  uygulanamıyordu (yarık ön yüze açılmıyor). § 8 N2 satırı aynı ifadeyle güncellendi.
- ASCII denetimi yeni "dibindeki" kelimesini yakaladı; doğru Türkçe yazım, `rehber_denetim.ASCII_TAMAM`'a gerekçeli satırla eklendi.
- Yamalı hâlde: `rehber_denetim.py --kaynak` ASCII 0, **onay farkı 3**; `F10l-birlesim.py` **GEÇER** (cümle 1099 → 1102, eklenen 3 / 3,
  silinen 0 / 0). `--kritik-onay-yenile`: yalnız b2g'nin 3 cümlesi eklendi (parça / ≈ 68 g; servo kablosu; fiş sırası), başka fark yok;
  kayıt kablo 222 / liste 213 / metin 1124.
- `F10o-rehber-metin.patch` uygulanan son hâlden (`git diff HEAD`) yeniden üretildi (kayıt olarak commit'te; `git apply -R --check` temiz).

### 9.2 Demo, F9b, F9c (brief madde 3)

- `demo_uret.py` yalnız yeniden koşunca F9b 15 → 30 hataya çıktı: şablon K3, K9, K38, K41, K44, K45, K46'yı hâlâ yer tutucuyla
  ("karar bekliyor") gösteriyordu. Düzeltme: `demo_uret.KARARLAR`'dan 7 kapanan karar çıktı (13 → 6); `viewer-template.html`'de
  yer tutucuların yerine kuyruktaki kararın sayısız özeti yazıldı (ör. "yazılım aralığı, mekanik durdurucu yok (K41, kapandı)"; sayı
  yazılmadı, F9b her sayıyı kaynağa bağlıyor).
- Kalan 2 hata F9b'nin kendi sabit örneğindendi: brief örnekleri K42 / K44 / K45 sayfada "karar bekliyor" olmalı; K44 / K45 kapandığı
  için kural kuyrukla çelişiyordu. `F9b-dogrula.py` örnekleri hâlâ açık K42 / K32 / K34 yapıldı (gerekçe satırı kodda; sınamanın amacı
  korunur). **F9b GEÇER (hata 0)**; sayı bağsız 0, karar 6 / etiket 16.
- `F9c-uret.py`: P10.2 "K53 kapandı (17.11, çentik); … çentik bir sonraki tam taramalı CAD paketinde"; P10.7 b2f ve b2g kapalı
  alt paketlere geçti, "Kalan"dan boyun tüneli deneme parçası çıktı; F10 özeti b2f, b2g. Plan P10.2 satırı ⛔ → ⏳ (K53 kapandı, uygulama
  sonraki CAD paketinde). `F9c-uret --cikti <depo dışı>` + `F9c-dogrula --tarayicisiz --sayfa`: **GEÇER (hata 0)**; kuyruk açık 26,
  kapanan 40, toplam 66 (plandaki güncel sayaçlarla çelişen satır yok; § 5'teki eski sayılar tarihsel kayıt). `sonuc-rapor.html` yeniden
  üretilmedi (faz sonu, P10.9).

### 9.3 Üretim (`rehber_uret.py --veri-yok`, 06:44:56–07:27:57)

FreeCAD'siz yol yeter: b2g rehber modeline / GLB'ye dokunmuyor (parça baskı denemesi, montajda yok); `rehber_uret` `--veri-yok`'ta da
`rehber_gorunum.isle()`'yi koşuyor, o da adım / alt adım `is_` alanlarını `rehber_metin`'den yazıyor ("rehber_metin alanlari, degisen 1:
K2.5 is_"). **Çıkış 0, 2581 s**; bellek önce 2,84 GB, en düşük 1,36 GB. Kilit gerekmedi (FreeCAD koşmadı), "boş" kaldı.
Alt adım 91, şema 65 (60 tek alt adımda), parça 1192; uç etiketi 24 / 48 / 46; PDF **86 sayfa**, taşan yok, en küçük 8,1 pt; denetim ASCII 0,
zorunlu eksik 0 / 118, elektrik 0; sıra ulaşılamaz 0 / 565, uçuş çarpışan 0 (istisna 16), ısıl 0, perdelenme gerekçesiz 0; kol kablo GEÇTİ;
tarayıcı 50 / 50, 360 px taşma 0. Değişen çıktı: `rehber-veri.json` / `.js`, PDF, `kontrol.json`, 5 kontrol görüntüsü (32.5 metin sütunu
13,5 k px; 29, 33.10, 35.1, 35.4 eşik üstü 0 px, kenar yumuşatma). GLB değişmedi.

**K2 alt adım 5 (PDF s. 48 ve site):** metin sığıyor, taşma yok; parça adı "Boyun tüneli deneme parçası", yol
`tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl` (kod kutusunda dosya adının kendi tiresinden satır kırılıyor), fiş sırası U03 → H02 → S10,
AU3 / G17 fişsiz; servo kablosu cümlesi yeni hâliyle. PDF alt bilgisindeki "üretim 02:41" veri damgası (`--veri-yok` veriyi
FreeCAD'le yeniden üretmediği için b2f'nin saati; bilgi).

### 9.4 Zincir 2–10

F10m § 13.2 komutları; F10d tek başına; `zin1` 2–5 (07:28–07:55, en düşük boş bellek 1,03 GB tek ölçüm), `zin2` F10d (07:55–08:12,
1,74 GB), `zin3` 7–10 (08:12–08:20, 1,71 GB). Bekçi hiç tetiklenmedi.

| Sıra | Komut | Çıkış | Süre (s) | Ölçülen |
| --- | --- | --- | --- | --- |
| 2 | `rehber_kablo.py --veri …` / `--bozma-denemesi --veri …` | 0 / 0 | 1 / 29 | GEÇER / **108 / 108** |
| 3 | `rehber_denetim.py` (veri) | 0 | 1 | ASCII 0, zorunlu eksik 0 / 118, yasak 0 |
| 4 | `F10f-dogrula.py` | 0 | 599 | GEÇTİ |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | 1016 | GEÇTİ; `renk_demo` KALDI (bilinen karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` | 0 | 1008 | GEÇTİ; 141 / 141 konum; uç etiketi 20 konum / 48, hata 0; 360 px taşma 0 |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | 460 | GEÇTİ; seçim 6 / 6, mini 50 / 50, dış istek 0, konsol 0 |
| 8 | `F9b-dogrula.py` | 0 | 5 | **GEÇER (hata 0)** |
| 9 | `carpisma_kos.py kontrol` | 0 | 0 | izlenen 17 dosya kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | 0 | GEÇER, kötüleşen yok (`regresyon.json` değişmedi) |
| + | `F9c-uret --cikti <depo dışı>` + `F9c-dogrula --tarayicisiz --sayfa` | 0 / 0 | — | GEÇER (hata 0) |

Veri, GLB, PDF ve `kontrol.json`'un SHA-256'sı zincirden önce / sonra aynı. Zincirin yazdığı: `planlama/d158/F10{a,d,e,f}-dogrula.json`.
Depoda `__pycache__` yok; eski kirin (19 dosya) SHA-1'i başlangıçla aynı.

Push öncesi tarama: `boyun_tunel_deneme.py` satır 14'teki çalıştırma yorumunda yerel kullanıcı yolu vardı; `~/.robot-cad/run_fc.py`
yapıldı (yalnız yorum, betik yeniden koşulmadı). Başka bulgu yok (anahtar, parola, e-posta, telefon, adres, resmî belge, takma ad 0).

Commit: tek commit "Lale P10.7b2g: …", açık `git add` listesiyle (eski kir girmedi). Bu dosya commit'in içinde olduğu için push
sonucu burada yazmaz; ajanın raporunda ve commit geçmişindedir.

### 9.5 Açık (bu paketten; kontrolün notları)

- **N1 (açık risk):** 7 mm kalın fiş kablo odası basamağını geçemeyebilir; deneme U03 / H02 için "geçmez" diyebilir; yedek yol (fişsiz
  geçirme, şerit HDMI) ayrı pakette.
- **Y2 (not):** STL'de fiş yolu dışında iki küçük kapalı iç boşluk (≈ 9 ve 10 mm³; servo çıkış mili / horn vidası arası, mil-horn cıvata
  deliği artığı); baskıya zararsız.
- **N7 (not):** mil ucu y 96'da açık; gerçekte üstünde çatal tabanı ve tabla kablo geçişi var, tünelin dışında, ayrı sınanmalı.
