# F10o · P10.7b2g bağımsız kontrolü: boyun tüneli deneme parçası

17.11.2026 06:05–06:20 (kontrol ajanı; saat okundu). Depo `lale-duzeltme`, HEAD = uzak = `3bc5aa9`; paket çalışma ağacında, commit yok.
FreeCAD açılmadı. STL kendi ikili okuyucumla, ışın–üçgen kesişimiyle ölçüldü (`olc()` kullanılmadı); kaynak, `kafa7_parcalar.py` sabitlerinden
elle kuruldu. Yama depoda uygulanmadı (yalnız `git apply --check` ve scratch kopyada). Depoda yazılan tek dosya bu.

## Karar: GEÇMEZ (bu hâliyle)

Ölçüler doğru, ağ temiz, kayıt araçları bozulmuyor. Ama parça iki yerde gerçek tünelden farklı ve ikisi de denemenin sonucunu değiştirebilir:
biri parçayı gerçekten geniş yapıyor (yanlış "geçer"), öbürü tam darboğazda gerçekten dar (yanlış "geçmez"). İkisi de betikte küçük değişiklik
ve bir FreeCAD koşusuyla düzelir.

## Engelleyici

**E1. Mil içine dönüş parçada yok (parça gerçekten geniş).** Kutu z ≤ −12'de kesiliyor; mil içi (r < 16) parçada yalnız z −16…−12 (4 mm),
sonrası ön yüzden ve üst yüzden açık. Kanıt (STL): x 0, y 56 hattında boşluk z −27,5'ten ön yüze (−12) kesintisiz; y 58, z −13'te x −10…10
açık; STL sınır kutusu kaynak z −30…−12. Gerçekte fiş pencereden Ø32 milin içine girip yukarı dönmek zorunda ve kayıttaki iki dik dönüşten
biri tam bu ("mil içinden pencereye", `kablolama-on-kararlar.md:137`). Parçada fiş pencereden düz çıkıp gidiyor: 30 mm'lik micro HDMI ucu
parçadan geçip robotta takılabilir. Düzeltme: `boyun_tunel_deneme.py:30` KUTU mil bölgesinde z'de tam mil çapına (≥ +20) ve y'de pencere
üstünde en az bir fiş boyu (≈ y 95, flanş `Y_FL` 92…96) uzasın. Yalnız mil tüpü (r 16…20) ve alt 6808 dolgusu yukarı uzatılırsa kütle az artar.
Kayıtlardaki "iki dik dönüş" ifadesi (günlük §1–3, json `donusler`, `dongu-158.md` § 5, yama metni "mil ucundan çıkar") bu düzeltmeden sonra doğru olur.

**E2. Dolgu, gerçek tünelin darboğazındaki boşluğu kapatıyor (parça gerçekten dar).** Ek (1) r < 20, y 45,9…48. Gerçekte o katmanda yalnız
alüminyum horn var: r 12,5 (`dirsek_lib.py:25` HORN_MG R), y 44,6…47,9 (`kafa7_parcalar.py:52-53`). r 12,5…20 arası 1,9 mm yüksekliğinde boş;
kanal üstünden (arka duvar z −23) kablo odasına (iç duvar = mil diski r 20) geçilen basamak tam burası. y 46 düzleminde iki tarafın örtüşmesi
parçada x −4'te 3,4 mm, x −1'de 3,0, x 6'da 3,9 mm; gerçekte horn boşluğu bunu 1,9 mm'lik bir katmanla genişletiyor. Kaba 2B konfigürasyon
araması (`scratchpad/b2g-kontrol/gecis_bfs*.py`, düz katı levha): 8 × 3, 8 × 3,6 ve 13 × 4,5 mm fişlerin ucu x0 ≥ −8'de gerçekte y 48–49'a,
parçada y 46'ya kadar ilerliyor. Yani fark tam S10 gibi ince fişlerin geçip geçmeyeceği yerde. Günlük §3 "eklerin kablo yoluna girmediği"
ve json `ekler_kablo_yoluna_girmiyor: true` yanlış: `ek_bolge_malzeme` bu basamağı hiç ölçmüyor (kanal, pencere, oda). Düzeltme
(`boyun_tunel_deneme.py:65`): dolgu kanal üstü izinin (x −14…6) içinde r < 12,5'e insin, yanlarda r < 20 kalsın. O zaman disk altında kalan
r 12,5…20 boşluğu x'te ≤ 20 mm köprü olur; çıkıntı analizini yeniden koşun.

## Düzeltilmeli

- **D1 Rehber yaması, deneme sırası** (`F10o-rehber-metin.patch` + kopyası `B2G_EKLENEN`): "önce U03 …, sonra H02 …, sonra S10" kabloların
  birikmesini söylemiyor. Gerçekte H02 fişi U03'ün kablosu tünelde dururken, S10 da ikisinin yanından geçecek; yalnız U03 "tünel boşken"
  geçiyor (`kablolama-on-kararlar.md:141`). Öneri: "geçen kabloyu parçada bırak, sonrakini yanından geçir".
- **D2 Tabla teması 514 değil, 540 mm²**: `boyun_tunel_deneme.py:207`, 0,2 mm'lik dilim hacmini 0,21'e bölüyor. STL'de Z = 0 yüz alanı 540,0
  (30 × 18, eksik yok). Düzeltilecek yerler: json `tabla_temas_mm2`, günlük §2.
- **D3 Baskı listesi eki "rulman / ısıl gömme deliği yok"**: parçada kulak tablasının M3 ısıl gömme deliği kesiti var (STL, x −4 / z −15'te
  boşluk y 25,4…31,6 = 5,7 + 0,5). Zararsız, ama cümle "kullanılmayan bir ısıl gömme deliği kesiti var" olmalı.
- **D4 Günlük başlığı "taban lale-duzeltme = uzak = 9b019d2"**: gerçekte HEAD ve uzak `3bc5aa9` (P10.9b, iki commit). Bu iki commit
  `rehber/`, `F10l-birlesim.py`, `baski-listesi.md` ve `dongu-158.md` dosyalarına dokunmuyor (`git diff --quiet` rc 0); yama ve F10l'in
  9b019d2 tabanı geçerli. Yalnız cümle düzelmeli.

## Not (kapsam dışı / sonraki paket)

- **N1 Gerçek tünelin kendisi:** E2'deki basamakta örtüşme 3–3,9 mm (x −1…6; x −14'te 8,7 mm). Kaba modelde 7 mm kalın katı fiş gerçek CAD'de de
  bu basamağı geçemiyor. Deneme büyük olasılıkla U03 / H02 için "geçmez" diyecek, yedek yol (fişsiz geçirip yeniden sonlandırma; şerit HDMI)
  şimdiden planlanmalı. Model kaba (2B, düz levha, 0,2 mm / 3° adım), sonuç doğrulanmadı.
- **N2 Pan servosunun kendi kablosu** yarıktan (`kafa7_parcalar.py:146`) kanala ve alt çıkışa iniyor, ama demet alanı 69,9 mm²'ye dahil değil
  (`kablolama-on-kararlar.md:125-126`). Denemede bir servo kablosu yarıktan geçirilmiş olsun mu, karar gerekiyor.
- **N3 Alt çıkışa yaklaşma:** boyun plakası z −25'te bitiyor (`arayuz.py:607`), servo yuvası arkada 5 mm taşıyor. z < −30 tarafındaki komşuyu
  (gövde, traversa, kabuk) sınayamadım: montaj FCStd'si açılmadı.
- **N4 0,6 mm duvar:** kanal ön duvarı z −19,2 ile kulak boşluğu z −18,6 arasında (y 31,6…40, x −10,5…6). Gerçek parçada da aynı. Baskıdan
  sonra bakılsın: kırılırsa deneme genişler.
- **N5 Parçada açık kalan yerler:** oda yanları kutu x −18 / 12'de, servo kablo yarığı ön yüzde açık (gerçekte servo gövdesi var). Etkisi yerel,
  parçayı biraz genişletir.
- **N6** Fiş listesi doğru: boyun demeti `kablolar.json`'da 5 kablo (G17, S10, U03, H02, AU3). Fişli olanlar U03 (13 × 7, `gecis_sirasi` 1),
  H02 (7 / 18 / 30, 2) ve S10 (ölçü depoda yok). AU3 / G17 fişsiz. Atlanan fişli kablo yok, sıra KOK §4 ile aynı. Yama metni düz Türkçe, yol
  doğru, eski KT4 cümlesi aynen duruyor.

## Bağımsız ölçüm (STL, kaynak koordinatı, mm)

| Ölçü | STL'den | Kaynak sabitinden | Günlük |
|---|---|---|---|
| Kanal kesiti (y 23) | x −14,0…6,0 / z −27,0…−19,2 → 20,0 × 7,8 | 20 × 7,8 (`:143`) | 19,96 × 7,76 (tarama) |
| Kanal sabit kesit / eksende boş | y 6,0…40,09 / 6,0…43,9 | 34 / 45° tavan 40…44 | 33,95 / 37,86 |
| Alt çıkış | x 20,0; y 6…18 (x −4), y 6…14 (x −12) | 20 × 12, üstü 45° | 19,96 × 11,96 |
| Mil penceresi | y 53…63 (x 0), 53…60 (x 8); x ±10 | 20 × 10, üstü 45° | 19,96 × 9,96 |
| Oda radyal (x 0, y 50) | z −27,5…−20,0 = 7,5 | 27,5 − 20 | 7,42 |
| Ağ | 2040 üçgen, 3060 kenarın hepsi 2 yüzlü, 1 bileşen | | kapalı, manifold |
| Hacim / kutu | 17 783,97 mm³; 30 × 18 × 63 | | 17 783,99 |
| Tabla teması | 540,0 mm² | 30 × 18 | 514 (D2) |
| 46° üstü aşağı bakan yüz | 543,3 mm²: Z 61 (197,7), 42,9 (160,6), 11 (72), 59 (48,3), 60 (40,5), 15 (24) | | 543,2, aynı dağılım |

Kütle 17,78 cm³ × 1,27 = 22,6 g (%100); 13,9 g / ≈ 24 dk tahmini kupon yöntemiyle tutarlı. Yön (servo yuvası tabanı tablada) ve köprüler
(≤ 20 mm, 6 mm radyal) desteksiz basıma uygun.

## Koşulan denetimler

- `git apply --check planlama/d158/F10o-rehber-metin.patch`: temiz.
- `rehber_denetim.py --kaynak` (yamasız depo): rc 0; ASCII 0, zorunlu eksik 0, yasak 0, çıplak 0, onaylı kritik girdi farkı 0, tamlık eksik 0.
- `kablolar_denetim.py`: GEÇER. `F4c-dogrula.py`: SONUÇ GEÇTİ (5a, 5b sabit nokta). `F10l-birlesim.py` (yamasız, b5fc255): GEÇER.
- Yama scratch kopyaya uygulandı (`rehber_metin.py` AST tamam). Kopyada `F10l-birlesim.py` (9b019d2, `GIT_DIR` depoya): GEÇER; cümle
  1099 → 1101, eklenen 2 / 2, silinen 0 / 0.
- Koşulardan sonra depo durumu değişmedi (16 değişmiş + 10 izlenmeyen, başlangıçtakiyle aynı).

**Sınayamadıklarım:** yamalı hâlde `rehber_denetim.py --kaynak` (kopyada bütün girdiler yok; günlük "yalnız onay farkı 2" diyor). Kaynak
`kafa-montaj.FCStd`'nin FreeCAD'le doğrudan ölçümü (kaynak modeli sabitlerden elle kurdum, ısıl gömme / horn vida delikleri dışında STL'le
uyumlu). Komşu montaj parçaları (N3). Fiziksel fiş ölçüleri (S10 ölçüsü depoda yok). N1 / E2'deki geçiş araması kaba bir modelle yapıldı,
kesin değil.

## Yeniden kontrol (tur 1 sonrası)

17.11.2026 06:39–06:47 (kontrol ajanı; saat okundu). Yeni STL (14 454 üçgen, md5 `fae01178…`) ilk turdaki kendi okuyucumla ölçüldü
(`scratchpad/b2g-kontrol/stl_olc2.py`, `yarik.py`, `kabuk.py`); FreeCAD açılmadı, yama depoda uygulanmadı.

### Karar: DÜZELTMEYLE GEÇER

İki engelleyici giderildi. Yeni bulgu tek: yamadaki servo kablosu cümlesi yeni parçada uygulanamıyor (düzeltilmeli, metin işi).

### Eski bulguların durumu

- **E1 giderildi.** Pencere y 55 / 58 / 61, x 0 hattında boşluk z −27,5'ten karşı duvara (z +16,0) kadar sürüyor, ötesi mil duvarı r 16…20.
  Mil içi y 66 / 70 / 80 / 90 / 95'te x ve z'de Ø 32,0 kapalı. Mil içinde gerçek komşular da var: mil-horn cıvata başları (x 8, y 55,
  z −7,9…−4,1) ve horn vidası (eksende y 42,9…49,1). Fiş pencereden girip Ø32 içinde y 53 → 96 arası 43 mm yükseklikte dönüyor: 30 mm'lik micro
  HDMI ucu artık gerçekteki duvarlarla sınırlanıyor. Yalnız mil ucu y 96'da açık (N7).
- **E2 giderildi.** İz içinde (x −10 / −4 / 0 / 4) y 46,5 ve 47,5'te ön sınır horn kenarı r 12,5'te (z −7,50 / −11,84 / −12,50 / −11,84).
  y 48,5'te sınır mil diski r 20'de (−17,32 / −19,59 / −20,00), y 45'te kanal üstünde arka duvar −23. Hepsi kaynak sabitleriyle aynı; basamak artık
  gerçekteki gibi ne dar ne geniş. İz yanlarındaki dolgu (x 8 ve x −15'te r 20'ye kadar kapalı, y 46…47,9) gerçekte boş bir yeri kapatıyor.
  Ama fiş y < 46'da kanal üstünün x −14…6 duvarları arasında. Basamağı geçerken 1,9 mm'lik katmana yalnız bir köşesi girebilir. Kanalda
  dönebileceği açı (20 mm genişlikte 13–18 mm fiş, ≲ 13°) ile bu köşe yana en çok 1,9 × tan 13° ≈ 0,4 mm taşar. Engelleyici değil (not N8).
- **D1 giderildi** (yama: "geçen kabloyu parçada bırak … U03 … U03'ün kablosu tünelde yerindeyken H02 … S10").
- **D2 giderildi:** STL'de tabla teması 2000,0 mm². json, günlük § 8 ve baskı listesiyle aynı.
- **D3 giderildi** (`baski-listesi.md:203-204`). **D4 giderildi** (günlük başlığı `3bc5aa9`).
- **N2 kısmen:** kayıt ve yama koşulu doğru. Ama yama cümlesi uygulanamıyor (Y1).
- **N1** açık risk olarak `dongu-158.md` § 5'te. **N5 değişti:** oda yanları z −24'te r 27,5 duvarıyla kapalı (x ±13,42), açık kalan yalnız
  annulusun x ±20 kesiti (|z| ≤ 18,9, fiş yolunun yanında). Yarık artık ön yüzde açık değil (aşağı bkz.).

### Yeni bulgular

- **Y1 (düzeltilmeli) Servo kablosu cümlesi:** "Önce bir servo kablosunu parçanın ön yüzündeki yarıktan kanala indir" (`F10o-rehber-metin.patch:24-25`
  `B2G_EKLENEN` ve `:51-52` rehber metni). Yeni parçada yarık ön yüze açılmıyor. Dolu pan servosu z −10,2'den başlıyor (x −1 / y 10 ve x 3,5 / y 13
  hatlarında boşluk z −31…−10,2, sonra malzeme). Yarık y 5…14 arasında taban ve servo ile kapalı (x −1, z −15 hattında boş y 5…14), yalnız kanala
  açık. Doğrusu: "bir servo kablosunu alt çıkıştan kanala sok, ucunu kanal dibindeki servo kablo yarığına it ve yerinde bırak". Aynı ifade
  `baski-listesi.md:208` "servo kablosu yarıkta" ile uyumlu, orası kalabilir. Metin değişince ASCII / onay denetimi yeniden koşmalı.
- **Y2 (not) İki kapalı iç boşluk:** STL'de 3 kabuk var; ikisi ters yönlü iç boşluk. Biri eksende y 41,6…42,9 r 1,5 (−9,2 mm³, servo çıkış mili
  / horn vidası arası), öbürü mil-horn cıvata deliği artığı (x 4,3…7,7, z −7,7…−4,3, y 47,9…52,9; −10,1 mm³). Fiş yolunda değiller, baskıya
  zararsızlar; "tek katı" iddiası katı düzeyinde doğru.
- **N7 (not):** mil ucu y 96'da açık. Gerçekte üstünde çatal tabanı ve tabla kablo geçişi var (`kablolama-on-kararlar.md:126`). Tünelin dışında,
  fiş dikleştikten sonraki yol. Ayrıca sınanmalı.
- **N8 (not):** İz yanlarındaki 126,7 mm³'lük dolgu (E2 maddesi) fiş yolunu en çok ≈ 0,4 mm etkiler; dolgu mil diskini taşıdığı için
  bırakılabilir.
- **Basılabilirlik makul:** 46° üstü aşağı bakan yüz 1611,3 mm² (günlük 1613). Seviyeler aynı: Z 61 / 41,6 / 44,9 / 43 / 11 / 59. Horn altı
  konsol halka r 6,5…12,5 (6 mm) Z 41,6'da. Sarkarsa y 41,6…44,6'daki servo üstü boşluğa iner, basamağın darboğazı (y 46…48, z −23 ↔ r 20)
  değişmez. Boyalı destek önerisi yerinde.

### Bağımsız ölçüm (yeni STL)

Kutu 40 × 50 × 93 (kaynak x ±20, y 3…96, z −30…20); hacim 119 594,35 mm³ (json 119,59 cm³). Kenarların hepsi 2 yüzlü. Tabla 2000,0 mm².
Kanal 20 × 7,8, y 6…40,09; alt çıkış 20 × 12; oda radyal 7,5; pencere 20 × 10. Hepsi ilk turla aynı. Kütle 67,5 g / %100 151,9 g ve 115 dk:
json = günlük § 8 = baskı listesi (`:208`) = `dongu-158.md` § 5 (≈ 68 g, 152 g) = yama (≈ 68 g). Eski 30 × 18 × 63 / 14 g "eskidi" diye işaretli.

### Koşulan denetimler

- `git apply --check`: temiz.
- Yama scratch kopyada: `F10l-birlesim.py` GEÇER (1099 → 1102, eklenen 3 / 3, silinen 0 / 0).
- Yamasız depoda: `rehber_denetim.py --kaynak` rc 0, `kablolar_denetim.py` GEÇER, `F4c-dogrula.py` GEÇTİ.
- Depo durumu değişmedi.
- **Sınanamadı:** yamalı `--kaynak` (kopyada bütün girdiler yok); geçiş araması yeni STL'de yeniden koşulmadı (basamak kesitleri doğrudan
  kaynak modeliyle karşılaştırıldı, kesitler aynı olduğundan ilk turdaki "gerçek" sonuçları geçerli).

### Kapanış ajanının yamayı uygulamadan önce düzelteceği tam liste

1. `planlama/d158/F10o-rehber-metin.patch:24-25` (`B2G_EKLENEN` N2 cümlesi) ve `:51-52` (rehber metni): "parçanın ön yüzündeki yarıktan kanala
   indir" yerine "alt çıkıştan kanala sok, ucunu kanal dibindeki servo kablo yarığına it" (ikisi birebir aynı olmalı). Ardından yamalı
   `rehber_denetim.py --kaynak` (ASCII 0, onay farkı 3) ve `F10l-birlesim.py`.
2. İsteğe bağlı: `planlama/d158/F10o-gunluk.md` § 8'de N2 satırındaki aynı ifade.
