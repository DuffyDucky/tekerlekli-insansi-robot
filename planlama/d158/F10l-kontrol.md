**DÜZELTME GEREKLİ** (küçük; üretimden önce). Paketin kendi iddiaları tuttu: metin gerçekten yalnız bölündü, onay kaydında kritik değer
değişmedi, yeni denetimler kendi kurallarıyla yakalıyor, bugünkü modelde üretimi durduracak koşul bulamadım. Ama montajcı gözüyle iki metin
kusuru (D1 bara sırası ve çifte bağlatma, D2 madde ↔ alt adım numarası) ve kısmi koşuda bir kod hatası (D3) var. Üçü de ucuz; 45–50
dakikalık üretimden önce düzeltilirse ikinci bir koşuya gerek kalmaz.

# F10l kontrolü · P10.7b2d-A (K1 / K2 demet alt adımları; kaynak düzeyi)

16.11.2026, bitiş 01:31 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `1c4e882`; paket commit edilmemiş. Salt okuma: depoda yalnız bu
dosya yazıldı. Farkı `git diff 1c4e882` ile kendim okudum. Eski sürümleri `git show 1c4e882:…` ile depo dışına çıkardım; betiklerim ve
kopyalar depo dışında (oturum scratchpad'i). A'nın `F10l-birlesim.py` betiğine güvenmedim, karşılaştırmayı kendim yazdım. FreeCAD,
`rehber_veri.py` ve `rehber_uret.py` tam koşusu yok. Bitişte depoda `__pycache__` yok.

## Bulgular (önem sırasıyla)

Engelleyici yok.

### D1 (düzeltilmeli, orta) Bara pabuç sırası ve aynı ucun iki alt adımda bağlatılması

Metin eskisiyle aynı. Ama tek parça metin bölünüp kartlara ayrılınca her kart "şimdi bunu yap" diye okunur:

- **17.1 G06 − ucu, bara kurulmadan baraya** (`rehber_metin.py:331`): "− ucu yıldız barasına (mavi pabuç)". Baranın köprüleri ve
  G05 ise 17.3'te geliyor (`:353-354`). 17.3'teki kural "büyük akımlı pabuçlar yığının altında" ve yerleşim "saplama 3: G05 (akü) /
  G06" diyor. Montajcı 17.1'i harfiyen yaparsa 16 AWG'lik G06'yı saplama 3'ün en altına takar; 12 AWG köprü ucu ve G05 üstüne gelir.
- **G12–G15'in bara ucu iki yerde** (`:372` 17.4 "Baradan: iki BTS7960B (G12, G13; 12 AWG); mini hat sigortalarıyla XL4016 A ve B …",
  G14 / G15 sigorta yuvasının "bir kuyruğu … bara saplamasına"; `:401-403` 17.7 "G12 ve G13'ün + uçlarını anahtarlı baraya … G14 ve
  G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baraya (madde 3)"). Saplama 1'de G12 (12 AWG) ile G14 / G15 (mavi pabuç) birlikte
  duruyor. G12 17.7'de takılırsa ince pabuçların üstüne gelir. 17.4'te takılırsa 17.7 aynı işi yineletir.
- Aynı yineleme 17.5 ↔ 17.7'de (G18 + ucu F4'e, `:386` ve `:403`) ve 17.5 ↔ 17.9'da (G17, G20 taban ucu, `:386` ve `:419`) var.

**Günlük § 8'deki soruya hüküm:** 17.3'teki yerleşim listesi için ayrı bir "hazırlık" alt adımı gerekmez. Liste baranın kurulduğu
yerde, yani 17.3'te doğru duruyor. Asıl sorun sırada: bara (köprüler, G05) ilk bağlantıdan önce kurulmalı. Önerim, ikisinden biri:
(a) "Toprak ve iki bara" paragrafı ilk alt adım olur (yalnız sıra değişir, cümle değişmez); ya da (b) 17.1'de G06'nın − ucu "bantlı
bırak, 17.3'te G05'in üstüne" diye ertelenir. Ek olarak G12–G15, G18, G17 ve G20'nin bara / kutu ucu tek alt adımda bağlatılmalı,
öbür kart yalnız anmalı. Uç takılan kartta saplama numarası da yazmalı; bugün montajcı numara için 17.3'e geri dönmek zorunda. Bu metin
değişikliği; onay kaydı, `ZORUNLU` ve yeni bozmalar gerekir. Karar orkestratörde.

### D2 (düzeltilmeli, orta-düşük) Kart numarası ile metindeki madde numarası uyuşmuyor

- Kart başlığı "17.4 · Röle K1 …", metin "3. F1 20 A …" diye başlıyor. 17.2 ile 17.7 numarasız. 32.5 "5." ile başlıyor, içinde "6."
  var. Eşleme şöyle: madde 1 → 17.1 + 17.2, 2 → 17.3, 3 → 17.4, 4 → 17.5, 5 → 17.6, (numarasız) → 17.7, 6 → 17.8, 7 → 17.9, 8 → 17.10.
- Kartlardaki göndermeler eski madde numarasıyla kaldı. Ölçüm (`re.findall("madde \d+")`, çözülmüş metin): 17.7 "madde 3", "madde 4";
  17.9 "madde 4" ("B6a madde 4"); 17.10 "madde 5" ×2, "madde 2" ×2; K1 kontrol listesi "madde 3", "madde 2"; K1 kablo listesi P03
  "madde 7"; 32.5 "madde 6". Telefondaki montajcı 17.10'daki "madde 2"yi 17.2 sanar (G07), oysa kastedilen 17.3 (bara köprüleri).
- En dar düzeltme, cümleye dokunmadan: alt adım adına madde numarasını ekle, ör. "Röle K1, ön şarj kartı ve bara çıkışları (madde 3)".
  Bu 17 adı değiştirir, onay kaydı yenilenir. Daha temiz düzeltme `_demet_bol`'da baştaki "N. " önekini atmak ve "madde N"yi "17.x"e
  çevirmek, ama bu cümle değişikliğidir.

### D3 (düzeltilmeli, düşük; yalnız kısmi koşu) `alt_kontrol` kısmi koşuda NameError verir

`rehber_uret.py:727-746`: `tek = None` ilk değeri var, `tek_s` için yok. `tek_s` yalnız `if tum:` içinde tanımlanıyor (`:739`), oysa
`:744-754` her durumda okuyor. `--adimlar 17,32` gibi kısmi bir koşuda (`:4`'te belgelenmiş yol) bu NameError verir. Hata `:818-822`'deki
`try` ile yakalanır: "alt adim kontrolu: HATA", `gecti` False, yani sessiz değil. Bu sonuç kod okumasından; koşturmadım (tarayıcı ister).
Tam koşuda `tum` True olduğu için planlanan üretimi etkilemez. Düzeltme: `:727`'ye `tek_s = None` eklemek.

### Notlar (düzeltme şartı değil)

- **N1 · D3 kuralı kaba.** Kural yalnız demet üyeliğine bakıyor ve K1'in 10 alt adımının 6'sında "taban (K1)" var. Kendi bozmamda G22
  talimatını 17.4'ten 17.1'e taşıdım: D3 yakalamadı. Yakalayanlar D4 (G22 şeması kablosuz kaldı) ve onay kaydı (8 fark). Şeması olmayan
  bir kablo böyle taşınırsa yalnız onay kaydı yakalar.
- **N2 · D1 bozmaları gerçekte oluşamayacak bir durumu sınıyor.** `_demet_bol` alt adım metnini tam metinle aynı dizgeden türettiği için
  kaynakta ikisi ayrışamaz; D1 yalnız elle verilen `ham`'da düşer. Gerçek koruma `ZORUNLU`, `ZORUNLU_SIRA` ve onay kaydıdır. Örneğin
  "ters bağlıyken enerji verme" `rehber_denetim.py:220`'de de kilitli. Bozmalar kendi kuralıyla yakalanıyor (`dene` kural sayısının
  artışını ölçüyor, `:2222-2225`), yani iddia doğru; ama D1'in gerçek değeri sınırlı.
- **N3 · 32.1'de Kablo yolu 5 / 7 "şimdi" çiziliyor.** Bu yollar G14 → SV1 ve G15 → SV2'yi içeriyor (`CAD_ESLEME` 5 / 7 = SV1 / SV2,
  G14 / G15, S01–S08), oysa G14 / SV1 17.4 / 17.7'de bağlandı. Montajcı bara–XL4016 kısmını yeni iş sanabilir. Kablo yolu 12 (B01)
  32.4'te; bunun gerekçesi `sema_ok`'ta yazılı.
- **N4 · Kart boyu.** 32.5 1977, 17.4 1781 karakter (A'nın ölçümüyle aynı). Bugünkü veride en uzun alt adım kartı 871 karakter (G3.2).
  Kestirimim: kart tek sayfaya sığar (≈ 109 mm metin sütunu, 8,5–9,6 pt), taşma beklemem; ölçülmedi. 32.5 iki ayrı iş taşıyor:
  tünelden geçirme ve kafa ucunda bağlama + AU3 kutbu. "Hoparlör kablosu (AU3) dışındaki …" cümlesinden önce yalnız "\n" eklenerek
  bölünebilir. 17.4 de "Baradan:" ve "PC817 #2" cümlelerinden önce bölünebilir. İkisinde de cümle değişmez.
- **N5 · Demet adları montajcıya hiç görünmüyor.** `app.js` / `yazdir.html` `g.demet`'i okumuyor. "Alt adım = demet" pratikte "alt adım =
  paragraf, demet = denetim bilgisi" demek. Adlar da metinde geçen kablodan geliyor: 17.5'teki "boyun", G17 yalnız anıldığı için orada.
- **N6 · Ekranda ana metin her alt adımda yineleniyor** ve "… sırayla:" ile bitiyor (K1). Basılıda bir kez çıkıyor. Düşük.

## Doğruladıklarım (yöntem)

1. **Metin yalnız bölündü** (kendi betiğim; eski `rehber_metin.py` bellekte, yeni modül import):
   - K1 tam metni 11, K2 tam metni 9 paragraf. Alt adımlar paragraf 1 … n'i ardışık ve eksiksiz kullanıyor. Ana metin + alt adımlar,
     hem ham (yer tutucular çözülmeden) hem çözülmüş hâlde, eski `is_` ile **birebir eşit**.
   - K1 / K2 dışında `ADIM_HAM`'da yalnız B6a `kablo` farklı (açıklama maddesinin sırası). `KABLO_AD_HAM` aynı. `SEMA_HAM`'da yalnız G07
     farklı; şema sırası aynı.
   - Onay kaydındaki cümle dizisi K1'de 63 = 63, K2'de 29 = 29: sırasıyla eşit.
   - **Uyarılar:** "akü ayrık (XT60 açık)" ve K2'deki "enerjisiz çalış …" ana metinde; basılıda kartlardan önce, ekranda her alt adımın
     üstünde. G07 makaronu 17.2'de lehimden önce. "Ters bağlıyken enerji verme" 17.4'ün sonunda, ama K1'de enerji zaten verilmiyor
     (17.10). AU3 kutbu ve dikiş sırası 32.5'te, dikişten önce. Hepsi ilgili işten önce.
2. **Bölme** (`kablolar.json` `demet` alanı): metinde geçen her kablonun demeti, geçtiği bir alt adımın demetlerinde. Bugünkü veride
   CAD "Kablo yolu" parçaları `sira_grup_bul` ile şu alt adımlara düşüyor: 1 → 17.1, 2 → 17.3, 3 / 4 → 17.4, 9 → 17.5, 10 → 17.6,
   11 → 17.8, 5 / 7 → 32.1, 6 → 32.2, 8 → 32.3, 12 → 32.4. Şemalar `demet_sema_coklu` ile tam bir alt adımda (K1 9, K2 5). P03 maddesi
   yalnız 17.9'da (`kablo` = [3]). Not: alt adım sırası `demet_sirasi` sırasını izlemiyor ("taban alt kat" listede ilk, 17.7'de); izlemesi
   gerekmez, sıra paragraf sırası.
3. **Onay kaydı** (eski `1c4e882` ile yeni JSON, yerden bağımsız çokluk + yer bazında):
   - Kablo bölümü 165 → 165, fark 0.
   - Liste 204 → 206; eklenen yalnız iki `ZORUNLU_ALAN` "is_ana".
   - Metin 1040 → 1058: eklenen 19 (17 alt adım adı, G07 şemasının iki cümlesi), silinen 1 (G07'nin noktasız eski hâli).
   - Yeri değişen 88 cümle (K1 60, K2 26, SEMA G07, B6a sırası). Bunun dışında yalnız iki girdinin `neden` alanı "metin" → "zorunlu"
     oldu.
   - Sigorta, kesit, uç, yer tutucu ya da sıra değişikliği **yok**.
4. **Yan etki:**
   - `app.js` ve `yazdir.html`'deki yeni dallar yalnız `st.demet_alt`, `g.kablo`, `g.ref` ya da satırsız sıralı adımda çalışıyor. Bugünkü
     veride `g.ref` yalnız F1.9'da dolu ve renksiz, satırsız sıralı adım da yok; yani K1 / K2 dışında çıktı değişmez.
   - `pdf_tamlik` kablo maddesini adımın bütün sayfalarında arıyor (`rehber_uret.py:464`). P03'ün kartta basılması tamlığı bozmaz.
   - `rehber_veri.py`'nin iki yeni "dur" koşulu bugünkü CAD adları ve yeni desenlerle tetiklenmiyor (benzetim: uyumsuz 0).
   - `alt_kontrol` / `F10d` şema ölçütü: bugünkü veride alt adımlı adımların 46 şemasında birden çok 0, hiç 0. `F10d` `g["sema"][].d`
     alanını zaten `yabanci` hesabında kullanıyor, biçim aynı.
   - `rehber_gorunum.alan_isle` eski veride durur. Tam üretim önce `veri()` koştuğu için sorun değil (`rehber_uret.py:808-812`).

## Kendi bozmalarım (bellekte; `rehber_metin` kaynağı `_demet_bol`'dan önce değiştirilip `kaynak_denetle` koşuldu)

| Bozma | D1–D4 | Zorunlu | Onay farkı | Sonuç |
|---|---|---|---|---|
| bozulmamış | 0 | 0 | 0 | geçti |
| G22 talimatı 17.4 → 17.1 (kaynak dizgesinde) | D4 1 (D3 0) | 0 | 8 | yakalandı (D3 değil, N1) |
| Sonar cümlesi 17.8 → 17.1 | D2 1, D3 3, D4 2 | 0 | 2 | yakalandı |
| Madde 2 ↔ 3 yer değiştirdi (bara kurulmadan çıkış) | D4 1 | 0 | 20 | yakalandı (sıra anlamı değil, Kablo yolu 2'nin kablosu) |
| G07 paragrafı 17.2 → 17.9 konumuna | D2 6+ | 0 | 65 | yakalandı |
| AU3 şeması 32.5 → 32.1 | D4 1 | 0 | 0 | yakalandı (yalnız D4) |

## Koşular (FreeCAD'siz; `py -3 -B -X utf8`, `PYTHONDONTWRITEBYTECODE=1`)

| Sınama | Çıkış | Benim sonucum | A (§ 5) |
|---|---|---|---|
| `kablolar_uret.py --kontrol` | 0 | güncel | aynı |
| `kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0 | GEÇER / 172 GEÇER | aynı |
| `rehber_denetim.py --kaynak` | 0 | demet D1–D4 hata 0; K1 10 / 38 kablo / 16 öğe, K2 7 / 18 / 10 | aynı |
| `rehber_denetim.py --bozma-denemesi` | 0 | 274 / 274; temel hata 0 | aynı |
| `rehber_kablo.py` / `--bozma-denemesi` | 0 / 0 | GEÇER, onay tutuyor / 86 / 86 | aynı |
| `rehber_kablo.py --veri …` / `+ --bozma-denemesi` | 0 / 0 | GEÇER, eşlemesiz 0 / 95 / 95 | aynı |
| `rehber_kol_kablo.py --yazma` | 0 | 38 bölüm, GECTI | aynı |
| `node --check rehber/app.js` | 0 | — | aynı |
| `F10l-birlesim.py` | 0 | GECER (455 = 455) | aynı |
| kendi birleşim + onay + benzetim betiklerim | — | yukarıda | — |

Koşulardan sonra `git status`: paket dosyaları ve eski kir dışında değişiklik yok, `rehber/veri` yazılmadı. Bir koşunun çıktısı yanlışlıkla
depo dışına (Masaüstü) yazıldı; scratchpad'e taşındı.

## Doğrulayamadıklarım

- Kareler, PDF yerleşimi (17 kartın sayfa düzeni, 32.5 / 17.4'ün sığması), tarayıcıda `app.js` görünümü, `alt_kontrol` ve `F10d`'nin
  gerçek ölçümü. Hepsi üretim ister.
- D3 NameError'ı yalnız kod okumasıyla saptandı, koşturulmadı.
- Pabuç yığını kuralının elektriksel önemi (D1) kaynakta yazılı kurala dayanıyor; ayrıca ölçmedim.

## Ek: ajan B kalemleri

| Kalem | Ne | Kaynak | Bugün | FreeCAD'siz? |
|---|---|---|---|---|
| Gerilim yer tutucuları | F1 kontrol ve F3'te çıplak gerilimler: "20 V aralığı", "akü en çok 14,6 V", "(12,8–14,4 V)"; R9 | `karar-kuyrugu.md:1504-1505` (listedeki dosyalarda yok) | açık: `rehber_metin.py:947`, `:952`, `:1162`'de duruyor | evet (kaynak + onay) |
| E4 lejantı | E4 alt 4'te AU1 / AU2 opak kabuğun arkasında, ama lejant "Karede: Kablo: Analog ses" diyor; kuyrukta "E4 genel bakış lejantı (örtülme ölçümü ister)" | `F10k-gunluk.md:592`, `:614-615`; `karar-kuyrugu.md:1450` | açık | kısmen: metin / saydam desen evet, doğrulama üretim ister |
| A4 | Listedeki dosyalarda açık bir "A4" yok (F10j-kontrol-2 A4 `F10k-gunluk.md:111`'de yapıldı). Kuyrukta açık aday: kontrol-4 A4 "basılı sayfalarda boş alan" (R5) | `karar-kuyrugu.md:1496` | açık (aday) | evet (`yazdir.html`), ölçüm PDF ister |
| K1 mor hatlar | K1'de altı sinyal hattı (G07, B02, N01, N02, Q01, Q02) aynı mor; basılıda ayırt edilmiyor | `F10k-gunluk.md:177-178`, `:607-609` | kısmen azaldı: G07 17.2'ye ayrıldı, beşi 17.8'de birlikte | renk kuralı evet; görmek üretim ister |
| SV3 ucu | Dağıtım kartı C modelde yok; B5a'da SV3'ün kart ucu boşlukta ("yeri yaklaşık") | `F10k-gunluk.md:398-401`, `:616` | açık (düşük) | hayır (model ister) |
| E3a K01 | 14 mm'lik K01 şeması seçilince etiket kartının altında kalıyor; kafa giriş kartı modelde yok | `F10k-gunluk.md:591`, `:612-613` | açık | etiket yeri evet (`app.js`); kart için model gerekir |
| E4 alt 4 | yukarıdaki E4 lejantıyla aynı bulgu (kare 4) | `F10k-gunluk.md:592`, `:614` | açık | yukarıdaki gibi |
| B6a not sırası | "3B çizim değil" açıklaması satırlardan sonra geliyordu | `F10k-gunluk.md:617` | bu pakette yapıldı | — |
