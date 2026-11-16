# P10.9a bağımsız kontrol: F9c-uret / F9c-dogrula iki basamaklı faz

Kontrol ajanı, 16.11.2026 02:48–02:58 (sistem saati). Dal `lale-duzeltme`, HEAD `1c4e882`; iş çalışma ağacında (commit yok).
Okunan fark: `git diff 1c4e882 -- planlama/d158/F9c-uret.py planlama/d158/F9c-dogrula.py`. FreeCAD ve tarayıcı yok; bütün
çıktılar depo dışında (scratchpad `p109a-kontrol/`). Depoda yazılan tek dosya bu rapor. Koşular sırasında `dongu-158.md` ve
`karar-kuyrugu.md` değişmedi (md5 önce = sonra); `planlama/d158` altında `__pycache__` yok.

## Hüküm: **DÜZELTME GEREKLİ**

Çekirdek iddialar tutuyor: F0–F9 korunuyor, kalıp değişikliği F0–F9 girdilerinde hiçbir sonucu değiştirmiyor, sayaçlar doğru,
K58 tutarsızlığı gerçek. Ama yeni sayfada F10'un 4 commit'i yanlış pakete bağlı (B1), denetim faz özet satırını ve F10
özetlerinin durum sözcüklerini hiç sınamıyor (B2, B3), K61'in aciliyet grubu var olan ölçüte uymuyor (B4). Hepsi iki betikte, dar
düzeltmeyle kapanıyor (B1–B3 düzeltmeleri depo dışında koşturuldu, sonuçları aşağıda).

## Bulgular (önem sırasıyla)

### B1 (orta-yüksek): F10'da 4 commit yanlış pakete bağlanmış
- `F9c-uret.py:242`: §5 tek başlıklı ✅ satırındaki bütün hash'ler alınıyor; F10 satırlarında "push A..B" aralığı var, sol uç bir
  önceki paketin son commit'i. Sonuç: `9d0c58a` ("Lale P10.2: ölçüm ve kayıt raporu") P10.1'e (`dongu-158.md:465`
  "push 9d0c58a..ada0b87"), `ada0b87` ("Lale P10.1: planlama") P10.3'e (`:461`), `10b60d6` ("Lale P10.3: planlama") P10.4'e
  (`:455`) bağlı. "push X..Y" kalıbı planda yalnız bu üç satırda var, F0–F9'da yok.
- `F9c-uret.py:231`: P kodu konu satırının tamamından aranıyor. `759bb28` "Lale P10.4b: …" konusunun içindeki "(P10.7)" ileri
  göndermesi yüzünden P10.7'ye de bağlı (günlükteki örnek; yanlış bağ).
- Kanıt: `iz.py` izlemesi (hangi satırdan geldiği) ve aşağıdaki düzeltmeyle yeniden üretim.
- Düzeltme (iki satır):
  - `F9c-uret.py:242`:
    `            for h in re.findall(r"\b[0-9a-f]{7}\b", re.sub(r"\b[0-9a-f]{7}\.\.(?=[0-9a-f]{7}\b)", "", l)):`
  - `F9c-uret.py:231`:
    `        ks = set(kodlar(s.split(": ", 1)[0], set(harita)))   # yalnız konu öneki; gövdedeki "(P10.7)" gibi göndermeler değil`
- Sınandı: iki düzeltmeyle 36 F0–F9 satırının commit listesi aynı; değişen yalnız P10.1 (−`9d0c58a`), P10.3 (−`ada0b87`),
  P10.4 (−`10b60d6`), P10.7 (−`759bb28`); eşleşmeyen commit 2 olarak kalıyor; denetim yine yalnız K58 hatasını veriyor.

### B2 (orta): Denetim faz özet tablosunu denetlemiyor
- `F9c-dogrula.py` [2] yalnız sayfada bulunan `faz_karar_*` span'larını karşılaştırıyor; faz satırının varlığı ve Durum'u
  sınanmıyor. Bozma: F10 faz satırını silmek → **GEÇER**; F10 Durum 🔄 → ✅ → **GEÇER** (F0–F9'da da aynı açık, F9'dan kalma; F10
  açık bir faz olduğu için şimdi önemli).
- Düzeltme: `F9c-dogrula.py:329`'dan sonra (paket durum döngüsünün ardından):
```python
    # Faz özet satırı: plandaki her faz bir kez, Durum = fazdaki paketlerin en kötüsü (P10.9a kontrolü)
    fz = {}
    for kd, em in paket:
        fz.setdefault("F" + re.match(r"P(\d+)\.", kd).group(1), []).append(em)
    en_kotu = lambda ems: next((e for e in "🔄⛔🟡⏳" if e in ems), "✅")
    fsat = re.findall(r'<tr><td data-b="Faz"><b>(F\d+)</b>(.*?)</tr>', sayfa, re.S)
    for f in fazlar():
        hs = [s for k, s in fsat if k == f]
        if len(hs) != 1:
            hata("faz %s özet tablosunda %d kez" % (f, len(hs)))
        elif en_kotu(fz.get(f, [])) not in re.findall(r'<td data-b="Durum">(.*?)</td>', hs[0], re.S)[0]:
            hata("faz %s durum hücresi plandaki %s'yi içermiyor" % (f, en_kotu(fz.get(f, []))))
```
- Sınandı: yeni sayfada ek hata 0; iki bozma da yakalandı ("faz F10 özet tablosunda 0 kez", "faz F10 durum hücresi plandaki
  🔄'yi içermiyor").

### B3 (orta): F10 özetleri elle yazılmış durum taşıyor, denetim bunu görmüyor; P10.7 "Kalan" eksik
- `F9c-uret.py:406–421` F10 `PAKET_SONUC` metinleri 16.11 02:39 anlık görüntüsü ("Açık (K53)", "Sürüyor: P10.7b2d"). [3] yalnız
  sayıların kaynakta geçtiğine bakıyor. Bozma: P10.2 sonucunu "Kapandı (K53)" yapmak → **GEÇER**; P10.5 "alt adım 71" → "72" →
  **GEÇER** (72 planda başka yerde geçiyor; F9c-gunluk §12'deki alt dize sınırı). P10.2 kapanınca ya da P10.7 bitince sayfa
  yanlış durumu yazar ve denetim geçer.
- Düzeltme (denetim), B2 bloğunun ardına:
```python
    # F10 özet kalıbı (P10.9a): plandaki durum ✅ değilse Sonuç "Açık" ile başlar, ✅ ise başlamaz
    for kd, satir in re.findall(r'<tr data-paket="(P10\.\d+[a-z]?)">(.*?)</tr>', sayfa, re.S):
        sn = re.sub(r"<[^>]+>", "", (re.findall(r'<td data-b="Sonuç">(.*?)</td>', satir, re.S) or [""])[0]).strip()
        if (pd.get(kd) != "✅") != sn.startswith("Açık"):
            hata("paket %s sonuç metni plandaki %s durumuyla çelişiyor: %s" % (kd, pd.get(kd), sn[:40]))
```
  Sınandı: yeni sayfada ek hata 0; "Kapandı (K53)" bozması yakalandı.
- Düzeltme (içerik), `F9c-uret.py:416-418` P10.7 metni planın kalanlarıyla (`dongu-158.md:165` "Sıradaki: P10.7b2 …" listesi;
  b2a–b2c'nin kapattıkları çıkarıldı):
  `"Açık. Kapalı alt paketler: P10.7a (74 kablo tek kaynakta, `kablolar.json`; 16.11 sipariş listesi genel 120.852,43 TL), P10.7b1, P10.7b2a (74 / 74 kablo talimatta, PDF 80 sayfa), P10.7b2b, P10.7b2c. Sürüyor: P10.7b2d (K1 / K2 demet alt adımları). Kalan: taban yollarının yeniden tasarımı, boyların ölçümü, düğüm tutucusu, boyun tüneli deneme parçası, G19 / G20 / G24 / G26 (yalnız onayla); K52, K60, K61; Efe'nin iki cevabı."`
  (Sınanmadı: metnin `data-kaynak` denetimi; içindeki sayılar 74, 16.11, 120.852,43, 80 eski metinde de vardı.)

### B4 (orta): K61 aciliyet grubu B değil A olmalı
- `F9c-uret.py:364` K61 "B". Kuyruk `karar-kuyrugu.md` K61 gövdesi: seçenek "a) kullanılmaz, kalem siparişten çıkar", kalem
  `maliyet.json` "Bas-konuş düğmesi" 76,24 TL. Grup A'nın ölçütü "Sipariş ya da elektrik güvenliği öncesi"; aynı biçimdeki K12
  ("30 mm fan seçilirse sipariş satırı eklenir") ve K32 ("satın alınırsa sipariş toplamı … değişir") A. Bugün S = 16.11.
- Düzeltme: `    "K61": ("A", "Seçenek a kalemi siparişten çıkarır (Bas-konuş düğmesi 76,24 TL); karar S = 16.11 siparişinden önce, b seçilirse kablo ve yer P10.7b kablajında."),`
  Sonuç: grup A/B/C 21/14/14 → 22/13/14.
- Öbürleri savunulabilir: K53 A (`proje-plani.md:92` "S'den önce … DXF ve lazer teklifi"; kontrplak elektronik katı lazer kesimde;
  gerekçe kuyrukta değil plan dosyasında, `Neden` hücresinin `data-kaynak`'ında PLAN var). K60 A (elektrik güvenliği; seçenek B
  alıcı ve beslemesi ekler). K54 B, K55 B (kupon / kabuk baskısından önce; K2 "Parti 3 basılmadan önce" B ile aynı ölçüt).
  K62 C (kayıt).

### B5 (düşük-orta): Paket kartı ⏳'yı saymıyor, "(bu paket)" artık yanlış
- `F9c-uret.py:581`: kart "41 ✅ · 1 🟡 · 2 ⛔ · 1 🔄 (bu paket)"; toplam 45 ≠ 47 (P10.8, P10.9 ⏳ görünmüyor), 🔄 P10.7'dir, bu sayfa değil.
- Düzeltme: format dizisinde `%s 🔄 (bu paket)` → `%s 🔄 · %s ⏳`, argümanlara `H("paket_⏳", say["⏳"])` eklenir
  (`F9c-dogrula.py` `paket_⏳`'yı zaten hesaplıyor).

### B6 (düşük): Sayfadaki kural notu bayat
- `F9c-uret.py:611-613`: (a) faz durum sırası ⏳'yı anmıyor, `faz_durum()` anıyor; (b) karar → faz kuralı yeni üçüncü adımı
  anmıyor (K62 bu adımla F10'a gidiyor); (c) "F9'un 🔄'ı bu paketin kendisidir" bugün yanlış (F9 ✅).
- Düzeltme metni:
  `'<p class="note">Faz durumu, fazdaki paketlerin en kötüsüdür (🔄 &gt; ⛔ &gt; 🟡 &gt; ⏳ &gt; ✅). Açık kararlar faza şu kuralla '`
  `'bağlandı: kuyruğun Durum hücresindeki paket etiketi (ör. F8a → F8); yoksa Bloke hücresindeki ilk P kodu; yoksa Durum hücresindeki ilk P kodu (ör. K62 → F10); yoksa F0. '`
  `'F10 açık; bu sayfanın faz sonu yenilemesi P10.9.</p>'`

### B7 (düşük): Kapalı P9.3 satırı canlı sayıyı gösteriyor
- `F9c-uret.py:761-763`: P9.3 "Bu rapor: 47 paket, 49 açık karar" `data-h`'ye bağlı; P9.3'ün sonucu F9 sonu sayfasıdır (36 paket,
  47 / 52). Günlükteki "P9.3'te yalnız paket sayısı 36 → 47" farkı bu yüzden çıkıyor; anlamca yanlış.
- Düzeltme: `son = K("F9 sonu sayfası (09.11): 36 paket, 47 / 52 açık karar, 10 korunan değer; F10 yenilemesi P10.9.", DONGU)`
  (36 paket `dongu-158.md:147`, 47 / 52 planda 3 yerde, 10 korunan değer planda). P10.9 satırı "bu rapor" bağlantısını taşır.
  Sınanmadı.

### B8 (düşük, etkisi bugün 0): §5 başlık yolunda harfsiz koda inme yok
- `F9c-uret.py:240-241`: "**P10.7a ✅" başlığı (`dongu-158.md:165`, `:351`) `hedef("P10.7a")` → harita'da yok → satırdaki hash'ler
  sessizce düşüyor. Bugün bu hash'ler konu satırından zaten P10.7'de. Düzeltme: `hk = hedef(b[0])` öncesinde
  `b0 = paket_kodu(*re.match(r"P(\d+)\.(\d+)([a-z]?)", b[0]).groups(), set(harita)) if b[0].startswith("P") else b[0]` ve
  `hedef(b0)`. Sınanmadı.

### B9 (kaynak, P10.9a alanı dışında): K58 başlığı
- Gerçek. Doğru olan özet tablosu: `karar-kuyrugu.md:73` "kapandı (14.11; …)", `:80` kapananlar listesinde K58, gövdedeki
  "**Durum:** kapandı (14.11.2026)", plan P10.6 "✅ 14.11 karar verildi (K58 …)". Yanlış olan `karar-kuyrugu.md:1147` başlığı.
- Düzeltme: `## K58 · ESP32 pin haritası (pano #8) — KAPANDI` (kuyruğa yazma yetkisi olan pakette).

### B10 (düşük, günlük ifadesi)
- `P109a-gunluk.md:28` "sayfa 14.11'den beri yeniden üretilemiyordu": özgün üretici K53'ün açıldığı 11.11'den (F10b) beri
  `KeyError` ile düşer; 14.11'de K1 / K10 / K11 / K14 kapanınca ayrıca "fazla grup" ile `return 1`. Sayfanın son değişikliği 14.11
  `8134519` (12 satır elle yama). Öneri: "üretici 11.11'den (K53) beri düşüyordu; sayfa son kez 14.11'de elle yamandı".

## Sınadıklarım (kendi ölçümüm)

1. **F0–F9 korunuyor: evet.** Özgün betikler `git show 1c4e882:…` ile çıkarıldı. Özgün üretici bugün `KeyError: 'K53'`
   (`uret`, grup_A sayımı) ile düşüyor. Doğrulandı. En dar yama: `GRUP`'a yeni betikteki altı satır, `return 1` kaldırıldı, çıktı
   yolu. Özgün ↔ yeni farkı 13 satır: 36 F0–F9 paket satırından 35'i bayt bayt aynı, P9.3'te yalnız paket sayısı (B7). F0 faz
   açık kararı 13 → 7 (K53–K62 özgünde F0'a düşüyordu), F10 satırı eklendi, paket toplamı ve kartı, eşleşmeyen commit 25 → 2,
   11 F10 satırı. Karar satırları aynı. Ajanın ("C", "?") yamasıyla da denetim 21 hata ve grup 19/11/19 çıktı (iddiayla aynı).
   Depodaki `sonuc-rapor.html` ↔ özgün üreticinin bugünkü çıktısı: farkların hepsi 09.11'den sonra kaynak değişikliği (karar
   47/52 → 49/63, K1 / K10 / K11 / K14 kapandı, K53–K62 açıldı, P9.3 🔄 → ✅, commit 66 → 95, HEAD, PDF 54 → 80, K28 Beklettiği
   metni, F10a–F10e rapor bağlantıları). Açıklanamayan fark yok. Depodaki sayfa değişmemiş (md5 sabit, git status temiz).
2. **F10 durumları doğru:** 11 satırın Durum'u planla aynı (✅ 7, ⛔ P10.2, 🔄 P10.7, ⏳ P10.8 / P10.9). Açık paket kapalı ya da
   kapalı paket açık gösterilmemiş. Özetlerdeki her sayı ve iddia `dongu-158.md:157-168` Durum hücrelerinde ve §5'te var. Eksik
   kalan P10.7 "Kalan" listesi (B3). P10.7b2c'nin kapalı olduğu yalnız çalışma ağacındaki plan düzenlemesinde ve `1c4e882`'de;
   HEAD'deki plan hücresi 🔄 diyor (öbür ajanın commit'i bunu kalıcı yapacak).
3. **Kalıplar:** eski ↔ yeni `kodlar` / `etiket` / §5 başlık / brief etiketi bütün 95 commit ve bütün plan satırlarında karşılaştırıldı.
   Fark yalnız F10 girdilerinde. Planda paket olmayan P kodları: P10.7a, b, b1, b2, b2a–b2d ve P4.5a. Hepsi doğru biçimde P10.7 /
   P4.5'e iniyor. Gerçek harfli paketler (P10.4b, P10.5b) korunuyor. Tarih, ölçü ve karar numarası paket sanılmıyor: P/F öneki ve
   "✅" ya da parantez şartı var. Kuyruktaki 49 açık kararın faz ataması tek tek listelendi, hepsi doğru. Yanlış eşleşmeler B1'de.
4. **Sayaçlar:** kuyruk Özet tablosu 63 satır, K1–K63 eksiksiz ve tekrarsız, açık 49, kapalı 14. `karar-kuyrugu.md:80`
   "**Açık: 49.** **Kapandı: 14** … Toplam 63" ile aynı. Yeni kalıp bu satırı okuyor. K58: B9.
5. **Denetim bozmaları** (22 deneme, `--tarayicisiz --sayfa`): yakalananlar F10 / F0–F9 paket satırı silme, paket durumu (⛔ → ✅,
   ⏳ → ✅, ✅ → 🟡), `karar_acik`, `faz_karar_F10`, sahte P10.10 satırı, karar satırı silme, karar grubu, commit hücresini boşaltma,
   `komit_eslesmeyen`. Kaçanlar şunlar. F10 faz satırını silme ve faz Durum'u (B2). F10 özetinde durum sözcüğü (B3). Yaygın bir sayıyı
   değiştirme (B3). Faz notundan karar kimliği silme (sayı aynı). Bir commit'i başka pakete taşıma: bilinen sınır, F9c-gunluk §12.
   Bunun dar düzeltmesi sınandı ve yakalıyor: plan Durum hücresindeki her hash o paketin commit hücresinde olmalı. Rapor
   bağlantısını silme de kaçıyor. B2 ve B3 önerileri eklenmiş denetim yeni sayfada yine yalnız K58 hatasını veriyor.
6. **Aciliyet grubu:** B4.

## Doğrulayamadıklarım / varsaydıklarım

- [9] tarayıcı ölçümleri (1400 / 360 px yatay kaydırma, konsol), `--goruntu`: koşulmadı (bellek, kural).
- F10 özetlerini yalnız plan (`dongu-158.md` §3 ve §5) ile karşılaştırdım; `F10*-gunluk.md` / `-kontrol.md` dosyalarıyla değil.
- "Pano #8 mesajını Ahmet gönderecek" ve `maliyet.json` 120.852,43 TL'nin bugün de geçerli olup olmadığı: plandaki "sipariş farkı
  yok" kayıtlarına dayanıyor, kendim yeniden hesaplamadım.
- Üretim çalışma ağacındaki plana (öbür ajanın commit'lenmemiş düzenlemeleri dahil) karşı koştu. O ajan plana yazmayı sürdürürse
  son üretim P10.9'da yinelenmeli.
- B6–B8 düzeltme metinleri koşturulmadı. B3 içerik metni koşturulmadı.
