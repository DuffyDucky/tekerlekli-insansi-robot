# F10r · P10.7b2i günlüğü (uygulama ajanı): yol 9 kırpması, U06 şeması, kablo boyları

DURUM: KAPANDI (19.11.2026 05:55; § 8). Madde 1, 2 ve 3 (dar kapsam) bitti; kontrol DÜZELTMEYLE GEÇER: D1–D3 düzeltildi, D4–D7
ve B1 kuyrukta. Tam üretim (FreeCAD veri adımlı) + 17.7 kadraj düzeltmesiyle `--veri-yok` yeniden üretim, zincir 2–10 çıkış 0.

Açılış 19.11.2026 01:33 (saat okundu). Dal `lale-duzeltme`, HEAD = uzak = `8bca2f5`. Boş bellek 6,76 GB (FreeCAD koşularından önce
6,76 / 6,40 GB). Girdi: `F10q-gunluk.md` § 3–4, `karar-kuyrugu.md:1613-1615` (yol 9 GEO_ISTISNA), `:1728-1732` ve `:1759-1760` (U06),
`F10n-gunluk.md` § 1, § 9 (yol 12 `CAD_KIRP` ve FreeCAD denemesi). Model kaynaklarına (`tasarim/freecad/**/…_parcalar.py`, `*_lib.py`,
`arayuz.py`, FCStd) dokunulmadı; paralel CAD ajanının ayrı worktree'sine dokunulmadı.

## 0. Başlangıç kiri (`git status --short`, 19 dosya; dokunulmadı)

`F10q-gunluk.md` § 0 ile aynı: `tasarim/freecad/kabuk/gorsel/` altında 13 PNG, `tasarim/freecad/montaj/yerlesim-kontrol.json`, kökte
`geometri2_cikar.py`, `geometri2_dogrula.py`, `geometri_cikar.py`, `gez.js`, `uc.js`.

## 1. Madde 1: Kablo yolu 9 kırpması: BİTTİ (kaynak + FreeCAD denemesi)

Sorun (F10q § 3): `taban-analiz.json` `kablo_yolu[8].noktalar`: [0] (0; 215,5; −203) sigorta kutusu F4, [1] (62; 182; −30), [2] (55; 150;
20), [3] (49,2; 125; 75) XL4016 çevre (kutusunun içinde) = G18'in yolu; [4] (40; 150; 150), [5] (40; 185; 160), [6] (80; 200; 75) ESP32 =
eski tasarımın çevre 5 V → ESP32 hattı. y aralıkları çakışıyor, y düzlemi ayıramaz; z ≤ 77,5 ESP32 ucunda kalıntı bırakır.

**Echo kararı (geri alınabilir): kesim düzlemi genelleştirildi, yol 9 normali (0, 1, 1) / √2.** Gerekçe: izdüşüm y + z korunan
noktalarda en çok 200 (/√2 = 141,42; noktalar[3]), atılanlarda en az 275 (/√2 = 194,45; ESP32 ucu): kesim 141,42 + 2,5 = **143,92**,
atılan bölümün tüpüyle arada ≈ 48 mm, kalıntı yok. Tüp her noktada küre + aralarda silindir (`taban_parcalar.tup`), bu yüzden "korunan
noktaların en büyük izdüşümü + r" korunan bölümü tamamen içeride bırakır. Kesim kayıttaki noktalardan ve tüp yarıçapından; uydurma
geometri yok. Yol 12 değişmedi (yön +y, kesim 192,5; onay kaydındaki yazımı da aynı).

Dokunulan kaynak:
- `tasarim/freecad/rehber/rehber_kablo.py`: `GEO_ISTISNA[9]` kalktı (sözlük boş, iki yorum satırı); `CAD_KIRP[9] = dict(son=3,
  yon=(0, 1, 1), gerekce=…)`; yeni `cad_kirp_yon`, `izdusum`, `cad_kirp_kesim` (eski `cad_kirp_y`'nin yerine; (yon, d) döner),
  `cad_kirp_metin`, `cad_kirp_denetle` (FreeCAD'siz: atılan her noktanın küresi düzlemin öbür yanında, `son` sınırlı); `glb_kutulari` artık
  `(bmin, bmax, izd)` (izd: her kesim yönünde mesh izdüşüm aralığı); `kirp_veri_denetle` y yerine kesim yönündeki izdüşüme bakar (yol 12'de
  +y: b2f sınaması aynen); onay girdisi y yönünde eski biçim, başka yönde "son 3 kesim yön (0.0, 1.0, 1.0) ≤ 143.921 · …"; ana çıktıya
  "kırpma kesimi: … hata N" satırı; bozma: b94 (yol 9 CAD_KIRP'ten silindi), b95 (son=2, XL4016 ucu kesildi), b96 (yön silindi → y
  düzlemi), b97 (z düzlemi, ESP32 kalıntısı); veri bozmaları v10 / v11 izdüşüme çevrildi, yeni v16 (yol 9 kırpılmamış GLB), v17 (baştan
  kesilmiş), v18 (GLB'de o yönde izdüşüm yok); `CAD_ESLEME[9]` yorumu.
- `tasarim/freecad/rehber/rehber_veri.py` `kirp(p, yon, ky, n)`: kesim kutusu yerel y'si yön'e dönen yerleşimle kurulur; sınırlar
  şekil R⁻¹ ile döndürülüp sıkı kutudan (`_izd`); +y'de R birim (b2f aynen). Ek: **bütün** atılan noktalar kesilmiş katının dışında
  olmalı (eskisi yalnız ilk atılan noktaya bakıyordu; z kesimi ESP32 ucunu bırakırdı). Log satırı ASCII'siz "≤ / ·" içermez: **ilk
  FreeCAD denemesinde `cad_kirp_metin`'in "≤" karakteri freecadcmd stdout'unda (cp1254) UnicodeEncodeError verdi**; üretimi durdururdu,
  düzeltildi.
- `tasarim/freecad/rehber/rehber_metin.py`: 17.7 "XL4016 çevreden sonraki kısmı eski çizimdir … uygulanmaz" → "Karede vurgulu çizgi
  Kablo yolu 9'dur (G18, F4 → XL4016 çevre); …"; `KABLO_AD[9]` "Şemanın XL4016 sonrası kısmı eski" → "CAD yolunun XL4016 sonrası eski kısmı
  (doğrudan ESP32'ye) rehberde çizilmez; …" (yol 12'nin b2f cümlesiyle aynı kalıp).

FreeCAD denemesi (depo dışı `…\scratchpad\b2i\kirp_deneme.py`; kilit alınıp bırakıldı, 01:38–01:40; yalnız taban modülü, 2 s):
betik `rehber_veri.py`'deki gerçek `KIRP_PAY … KIRPILAN` kaynağını çalıştırır.

| Yol | Önce | Sonra | Kesim yüzü | Noktalar | Bozmalar (gerçek kodla) |
|---|---|---|---|---|---|
| 9 | izdüşüm 6,34…246,45, hacim 10.237,08 mm³, 1 katı | `kirp()` geçti; izdüşüm 6,3388…143,9214, hacim 6.120,59, 1 katı; global kutu x −2,5…64,5, y 122,5…218,0, z −205,5…79,6 | 1 düz yüz, 22,10 mm² | korunan 4 / 4 içeride, atılan 3 / 3 dışarıda | bayat (5000), boş (−5000), son korunanın önünde (119,2), y yönü (218), z yönü (77,5): **5 / 5 SystemExit** |
| 12 | 137,5…1327,5, 27.255,63 | geçti; 137,5…192,5, 3.944,49, 1 katı (b2f ile aynı) | 1 yüz, 81,22 mm² (b2f ile aynı) | 3 / 3, 6 / 6 | bayat, boş, önünde (159): 3 / 3 |

Kırpılmış yol 9 `geometri_denetle`'de istisnasız geçiyor (uçlar sigorta kutusu ve XL4016 çevre kutusu, hata 0).

## 2. Madde 2: U06 "ESP32 USB" şeması: BİTTİ (kaynak + `lale158_kontrol` koşusu)

**Echo kararı (geri alınabilir): şemanın taban kısmı yeniden çizildi; `lale158/kablo_yolu_ekran.py` şema kaynağıdır, model kaynağı
değildir** (FCStd üretmez; `carpisma_kos.py` izlediği 17 dosyada yok; kafa kütlesinde ESP32 USB zaten sayılmıyor, `kafa_ici_kablo_kutle`).
Karar kuyruğu da düzeltmeyi bu dosyada istiyor (`:1729`).

Yeni taban ucu (`ESP_USB_TABAN`, `ESP_PORT`, `FIS_ESP`): ESP32 DevKit'in micro USB portu, `taban_lib.esp_local()` bileşeninden: +x ucu,
global x 100…107, y 199,2…202,2, z 71…79 → port ağzı (107; 200,7; 75). Fiş +x'ten takılır, fişin arka ucu port ağzından 18 mm (TAHMİN,
ürün elde yok), son nokta port ağzının 2,5 mm önü. Yol (etek üst plakası geçişi 05.11 çizimiyle aynı): (14; 262; −40) → (14; 225; −40)
→ (40; 215; −30) direğin sağı → (40; 205; 37) → (125; 205; 37) XL4016 C (z ≤ 23,5) ile ESP32 taşıyıcısı (z ≥ 50) arasındaki şerit, kat
üstünde → (127,5; 200,7; 75) fişin arka ucu → (109,5; 200,7; 75). Hub tarafı değişmedi.

FreeCAD (kilit alınıp bırakıldı, 01:42–01:45):
- `lale158_kontrol.py` (depodaki betik, `robot-montaj.FCStd`, 14 s, çıkış 0): `lale158-kontrol.json` farkı **yalnız** U06 + süre:
  `kablo_ozet.kablo.ESP32 USB` yol 971 → **1.129** mm, önerilen 1.360 → **1.560** mm; `kablo_tup_hacim` 12.218,1 → 14.199,8 mm³ (π r² L
  14.192,0; geçerli, 1 katı); **`kablo_tup_cakisma["ESP32 USB"]` = [] (önce de [])**; `sure_s` 9,5 → 12,8. Başka alan değişmedi (CAD kaynakları
  09.11'den beri aynı; toplam boy 1580, sığmayan baskı 0).
- Depo dışı `u06_yakin.py` (yeni taban bölümü × montaj parçaları, en yakın uzaklık): ESP32 DevKit 0,50 mm (port ağzı, temas yok),
  Gövde direği 4,12 (direk arka yüzü boyunca, eski çizimle aynı), ESP32 taşıyıcısı 9,60, taşıyıcı vidası 13,49, XL4016 C 15,00,
  kat sağ M5 cıvatası 17,50, elektronik katı 19,20, güç paneli 25,18.

Kaynakta kaldırılan / eklenen:
- `rehber_kablo.py`: `SEMA_GEO_ISTISNA` U06 b / son ve `_ESP` gerekçesi kalktı (denetleyici şema düzelince "kullanılmıyor" diye kendisi
  yakaladı); b51 artık HDMI baş istisnasını siliyor (U06'nınki yok); yeni b98 (U06 eski istisnası geri eklendi → "kullanılmıyor").
- `rehber_metin.py`: K2 kablo listesindeki "yanlış yerde … şema yeniden çizilecek" maddesi kalktı; DEMET_ALT ESP32 USB `kablo_sec` kalktı;
  K2 "Önerilen boylar" ESP32 USB 1.360 → **1.560**; K1 alt adım 17.11 (madde 7): "ESP32 USB'nin (U06) taban ucunu bağla: micro USB fişini
  ESP32'nin önden bakınca sağ ucundaki portuna tak; kabloyu elektronik katının üstünden, ESP32 taşıyıcısı ile güç panelindeki XL4016
  C'nin arasından direğin sağına götür (yukarısı K2'de, direk arka yüzü)". "Önden bakınca sağ" = +x (adım 0 tanımı; 17.10 da ESP32'yi
  "önden bakınca sağda" diyor).
- `rehber_denetim.py`: `ZORUNLU_ALAN` K2 "yanlış yerde" kilidi ve dört D2 bozması kalktı; yerine `ZORUNLU` K1 U06 taban ucu talimatı ve
  üç bozma (talimat silindi / fiş güç paneline / kablo ESP32 kartının üstünden); `ASCII_TAMAM`'a "portuna" (gerekçe satırıyla).
- İlk denemede yakalanan ve düzeltilen: K1 cümlesinde "bağlandı; ESP32 USB" → "bağlandı. ESP32 USB" yapınca D6 bozması ("dalı (G20) …
  bağlandı; " desenini arıyor) boşa düştü, KAÇTI; noktalı virgül geri kondu → 305 / 305.

**Bağımlılık (CAD ajanı, K64):** yeni yol güç panelinde x 14…40, z −40…−30, y 205…262 şeridinden ve elektronik katında z 37 ± 2 /
x 40…127 şeridinden geçer. K64 bara tutucusunun (yıldız barası nominali (−20; 186; −90), anahtarlı bara röle yanında) yeri henüz yok:
**tutucu bu şeritlere konursa U06 şeması yeniden çizilmeli.** K51 (TVS) kafada, bu yoldan geçmez. USB ses kartı, K2 boss, K53 ilgisiz.

## 3. Madde 3: Kablo boyları: DAR KAPSAMDA BİTTİ

**Echo kararı (geri alınabilir): bu pakette yalnız 1 ve 2'nin değiştirdiği boylar.** 57 "tahmin" kablonun ölçümü (P10.7b "boyların
ölçümü") bu paketin işi değil: kablo başına tasarlanmış yol yok; taban CAD yolları `kod="(gosterim)"` referans tüpleri, şema yolu da
kuralla "ölçüm değil" (`kablolar_denetim` b_sema_boy_4).

- U06: `kablolar.json` `boy` yol 971 → 1.129, önerilen 1.360 → 1.560 (kaynak aynı anahtar); `sema_boy` 971 → 1.129 (`rehber_kablo.py
  --sema-boy-yaz`); `kablolar.md` yeniden üretildi (yalnız U06 satırı); `elektrik.md:39` ve `:83` satır içi (satır sayısı aynı). Hazır kablo
  2 m: yetiyor, sipariş / `maliyet.json` değişmedi.
- **Yeni diş (kayıt tazeliği):** `kablolar_denetim.py` `boy_tazelik` (`s_kaynak` içinde): boy JSON anahtarından yazıldıysa aynı adlı `_mm`
  alanları kaynakla eşit olmalı (dirsek-analiz gibi tek sayıda tek alan). Önceden U06'nın eski değerini hiçbir sınama yakalamıyordu (HEAD
  kaydına uygulanınca "U06: … onerilen_mm 1360 ≠ kaynak 1560.0; yol_mm 971 ≠ kaynak 1129.0"). Bozma: `b_boy_tazelik` (U06 971),
  `b_boy_tazelik_2` (S03 gereken 1800 ≠ 1856): ikisi de YAKALADI.
- Bilgi (kayda yazılmadı, ölçüm paketine): kırpılmış CAD yolu uzunlukları G18 **307 mm** (kayıtta `boy_tahmin` 550), B01 **189 mm**
  (`boy_tahmin` 400). Gösterim tüpü merkezden merkeze; ölçüm değil.

## 4. Onay kaydı ve birleşim

- `rehber_kritik_onay.json` yenilendi (önceki kopya depo dışında `…\scratchpad\b2i\onay-once.json`; fark listesi `kaynak-once.txt`):
  **11 fark, hepsi bu paketin:** kablo: +CAD_KIRP 9, −GEO_ISTISNA 9, −SEMA_GEO_ISTISNA ×2 (U06); liste: +ZORUNLU (K1 U06), −ZORUNLU_ALAN
  (K2 U06); metin: K1 alt adım 11 is_ (değişti + eklendi), K1 alt adım 7 is_ (17.7), K2 kablo (silindi + değişti), KABLO_AD 9. Yeni sayılar
  kablo 220, liste 226, metin 1142. Kritik (birimli) değer farkı: yalnız önerilen boy 1.360 → 1.560 (K2 kablo).
- `F10l-birlesim.py`: varsayılan taban `8bca2f5`, `B2I_SILINEN` 5 / `B2I_EKLENEN` 4 (uygulanan metinden, etiketler elle): GECER, cümle
  1121 → 1120.

## 5. Sınamalar (PYTHONIOENCODING=utf-8; hepsi koşuldu, 01:36–01:53)

| Sınama | Sonuç |
|---|---|
| `rehber_kablo.py` | SONUÇ GEÇER; kırpma kesimi hata 0, geometri hata 0, şema geometrisi hata 0 (istisnalı 4, önce 5), onay tutuyor |
| `rehber_kablo.py --bozma-denemesi` | **98 / 98** (b2h 93; +b94–b98) |
| `rehber_kablo.py --veri rehber/veri/rehber-veri.json` (depodaki ESKİ veri) | **beklenen KALDI (1):** "CAD_KIRP yol 9 (p1188): mesh izdüşümü en büyük 246.4, kesim 143.9: eski kısım rehberde çiziliyor" (üretimle kalkar) |
| `rehber_kablo.py --bozma-denemesi --veri` (eski veri) | 116 / 116 (taban hatası yüzünden bilgi değeri sınırlı; üretimden sonra yinelenmeli) |
| `rehber_denetim.py --kaynak` | çıkış 0; ASCII 0, zorunlu eksik 0, yasak 0, çıplak 0, onay farkı 0 (yenilemeden önce 11) |
| `rehber_denetim.py --bozma-denemesi` | çıkış 0, **305 / 305** (b2h 306: −4 U06 D2, +3 K1 U06) |
| `F10l-birlesim.py` | GECER (eklenen 4 / 4, silinen 5 / 5) |
| `kablolar_uret.py` + `kablolar_denetim.py` | 74 kablo yazıldı; GEÇER (boy 17 ölçüm / CAD, 57 tahmin) |
| `kablolar_denetim.py --bozma-denemesi` | **174**, GEÇER (önce 172) |
| `carpisma_kos.py kontrol` | izlenen 17 dosya kayıtla aynı |
| `regresyon.py` | GEÇER, kötüleşen yok. **Dikkat:** argümansız koşu `regresyon.json` / `-son-kosu.json`'u yazdı (yalnız tarih ve `lale158-kontrol.json` özeti `55edf339ec74` → `ff14b5a41487`); ikisi `git checkout` ile geri alındı (fark depo dışında `regresyon-deneme.diff`). Zincirde `--yazma` (= yazma) kullanılır |
| `git diff --check` | temiz (yalnız LF / CRLF uyarıları) |
| FreeCAD | § 1 kırpma denemesi, § 2 `lale158_kontrol` + yakınlık; kilit sonunda "boş" |

Koşulmayan: tam üretim (FreeCAD veri adımı dahil `rehber_veri.py`), zincir 2–10, F10d / F10e / F10f / F10a (veri ister), F9b / F9c
(demo ve sonuç raporu değişmedi), `rehber_kol_kablo` (kol tarafı değişmedi). `__pycache__`: bu oturumun açtığı üç klasör silindi.

Gözle / FreeCAD'le doğrulanan: yol 9 ve 12 kesimi gerçek şekilde (hacim, kesim yüzü, nokta içerde / dışarıda, bozmalar); U06 tüpü ×
bütün montaj (çakışma 0, en yakın uzaklıklar). **Yalnız kaynak düzeyinde kalan:** GLB'de yol 9'un gerçekten kesilmiş çizimi ve kareler
(17.7, K1 ana karesi, 17.11, 32.4), U06'nın rehber verisindeki şema noktaları ve karede görünümü, uç etiketi sayıları (K1 alt adım 11
metnine "ESP32", "XL4016 C" girdi: konum / etiket sayısı b2f'deki 24 / 48 / 46'dan değişebilir), PDF sayfa sayısı.

## 6. Dokunulan dosyalar

Değişen: `tasarim/freecad/rehber/rehber_kablo.py`, `rehber_veri.py`, `rehber_metin.py`, `rehber_denetim.py`, `rehber_kritik_onay.json`;
`tasarim/freecad/lale158/kablo_yolu_ekran.py`, `tasarim/freecad/lale158/lale158-kontrol.json` (FreeCAD çıktısı); `planlama/adim3/
kablolar.json`, `kablolar.md` (üretilen), `kablolar_denetim.py`, `elektrik.md`; `planlama/d158/F10l-birlesim.py`. Yeni: bu günlük.
`planlama/dongu-158.md`, `F9c-uret.py`, `karar-kuyrugu.md`, `planlama/maliyet.json`, `tubitak-2209b/` değişmedi. Eski kir (19) aynı.

## 7. Kapanış tarifi (üretim, yeterlilik, zincir, commit; işi bilmeyen biri tek başına uygular)

Temel `F10q-gunluk.md` § 9; farklar: **bu kez FreeCAD veri adımlı tam üretim** (`--veri-yok` YETMEZ: yol 9'un GLB kırpması ve U06 şeması
`rehber_veri.py`'de üretilir) ve § 10'daki çalışan arka plan kalıbı.

### 7.0 Hazırlık

- Çalışma dizini depo kökü. Bağımsız kontrolün düzeltme istediği bir şey varsa önce o; kaynak değişirse 7.0'ın sınamaları yeniden.
- Ön sınama (saniyeler): `rehber_denetim.py --kaynak` çıkış 0 / onay farkı 0; `rehber_kablo.py` SONUÇ GEÇER; `F10l-birlesim.py` GECER;
  `kablolar_denetim.py` GEÇER. Biri tutmazsa üretime başlama.
- Chrome kapalı, boş bellek ≥ 2,9 GB (PowerShell `(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB`); 2 GB altında başlama.
- Kilit: `planlama/d158/FREECAD-KILIT.txt` içeriği "boş" olmalı; üretimden önce tek satır "P10.7b2i kapanış ajanı (üretim) <saat>" yaz,
  üretim bitince "boş" (dosya git'te izlenmiyor). Paralel CAD ajanı ayrı ağaçta; aynı anda FreeCAD koşturuyorsa bellek ikisine yetmeyebilir,
  ölçmeden başlama.

Arka plan kalıbı (Git Bash; `Start-Process` kalıbı tutmamıştı, F10q § 10). Log ve `.durum` depo dışında:

```
cd "<depo kökü>"; U="<oturum karalama klasörü>/b2i-kapanis"; mkdir -p "$U"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
AD=uret; s=$(date +%s); py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py > "$U/$AD.log" 2>&1; c=$?; echo "BITTI cikis $c sure $(( $(date +%s)-s ))" > "$U/$AD.durum"
```

Bu satırı Bash aracında `run_in_background` ile başlat; bitiş bildirimiyle ya da kısa aralıklı `cat "$U/$AD.durum"` / `tail -5 "$U/$AD.log"`
ile oku (tek uzun bekleyiş yok). Bellek: 2–3 dakikada bir ölç; 1,2 GB altına art arda iki kez inerse süreci durdur, belleği bekle, adımı
baştan koş (kod hatası değil).

### 7.a Üretim (FreeCAD veri adımlı, `--veri-yok` YOK, `--cikti` YOK)

- Komut: `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py` (arka plan, `AD=uret`). Süre: önceki tam koşular 2606–2895 s (≈ 45–50 dk).
- Geçme: `.durum` "BITTI cikis 0". Logda: "CAD_KIRP: Kablo yolu 9: … izdüşüm 246.45 -> 143.92 (yon (0, 0.7071, 0.7071), kesim 143.92; …
  katı 1)" ve "CAD_KIRP: Kablo yolu 12: … 1327.50 -> 192.50 (yon (0, 1, 0), kesim 192.50; … katı 1)"; `SystemExit` yok; ön sınama "onay
  kaydi tutuyor (kablo 220, liste 226, metin 1142)"; parça 1192, alt adım 91, şema 65, çizim sınıfı 68 / 5 / 1 (beklenen, değişmemeli);
  PDF ≈ 86 sayfa, taşan 0, en küçük ≥ 8,0 pt; denetim ASCII 0, zorunlu eksik 0. Uç etiketi sayısı (b2f 24 / 48 / 46) değişebilir: değişirse
  günlüğe yaz, F10d U1–U6 geçiyorsa sorun değil.
- FreeCAD Python'u `__pycache__` yazabilir: zincirden önce bu koşunun açtıklarını sil (`planlama/d158/__pycache__` önceden vardı).
- Kilidi "boş"a döndür.

### 7.b Yeterlilik kanıtı (üretimden hemen sonra, ön planda, saniyeler)

```
py -3 -B -X utf8 tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json
```
Beklenen: "kırpma kesimi: yol 9 (0, 0.7071, 0.7071) · p ≤ 143.92, yol 12 y ≤ 192.5; hata 0", "kırpılan CAD yolları (…): robot.glb okundu;
hata 0", şema geometrisi hata 0 / istisnalı 4, SONUÇ GEÇER. (Üretimden önce eski veriyle bu sınama "yol 9 … 246.4 … eski kısım rehberde
çiziliyor" ile KALDI veriyordu: kalkmış olmalı.) Ek:

```
py -3 -B -X utf8 -c "import json;V=json.load(open('rehber/veri/rehber-veri.json',encoding='utf-8'));s=[x for x in V['semalar'] if 'ESP32 USB' in str(x.get('kaynak',''))+str(x.get('ad',''))];print(len(s), s[0].get('noktalar', s[0].get('p'))[-3:] if s else None)"
```
Beklenen: 1 şema, son noktalar ≈ (125; 205; 37), (127,5; 200,7; 75), (109,5; 200,7; 75) (alan adı farklıysa `semalar[...]` anahtarlarına
bakıp aynı üç noktayı ara). `rehber-veri.json` içinde "yanlış yerde" geçmemeli; "eski çizimdir (doğrudan ESP32'ye)" geçmemeli.
Tutmazsa: üretim veri adımını atlamış demektir (log başında "--veri-yok" ya da veri aşaması yok) → 7.a'yı doğru komutla yinele.

### 7.c Zincir 2–10 (F10q § 9.c ile aynı tablo ve sıra; `py -3 -B -X utf8 …`, depo kökünden)

| Sıra | Komut | Süre | Geçme |
|---|---|---|---|
| 2a | `tasarim/freecad/rehber/rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 1–2 s | SONUÇ GEÇER (7.b) |
| 2b | `tasarim/freecad/rehber/rehber_kablo.py --bozma-denemesi --veri rehber/veri/rehber-veri.json` | ≈ 30 s | hepsi yakalandı (beklenen ≈ 116 / 116: kaynak 98 + veri) |
| 3 | `tasarim/freecad/rehber/rehber_denetim.py` (veri) | 1 s | ASCII 0, zorunlu eksik 0 / N, yasak 0, çıkış 0 |
| 4 | `planlama/d158/F10f-dogrula.py` | ≈ 10 dk | GEÇTİ |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | ≈ 15–17 dk | GEÇTİ (`renk_demo` KALDI bilinen) |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` (tek başına) | ≈ 15–17 dk | GEÇTİ, 360 px taşma 0 |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | ≈ 7–8 dk | GEÇTİ, dış istek 0, konsol 0 |
| 8 | `planlama/d158/F9b-dogrula.py` | 5 s | GEÇER (hata 0) |
| 9 | `tasarim/freecad/carpisma_kos.py kontrol` | < 1 s | izlenen 17 dosya kayıtla aynı |
| 10 | `planlama/d158/regresyon.py --yazma` (**`--yazma` = dosyaya yazma**) | < 1 s | GEÇER, kötüleşen yok |

4–7 arka plan kalıbıyla (her biri ayrı `AD`). Zincir `planlama/d158/F10{a,d,e,f}-dogrula.json` yazar (commit'e girer). Toplam ≈ 50–55 dk.
Not: `regresyon.json` bu pakette değişmez (`--yazma`); argümansız koşarsa `lale158-kontrol.json` özeti değiştiği için yazar: geri al.

### 7.d Zincir yeşilse kapanış düzenlemeleri

1. `planlama/d158/F9c-uret.py` P10.7 özeti: "P10.7b2h (…). " satırının arkasına `"P10.7b2i (yol 9 eski kısmı rehberde kırpıldı, U06 şeması
   ESP32 portuna yeniden çizildi, U06 boyu 1.560). "`; F10 özetinde "b2f, b2g, b2h" → "b2f, b2g, b2h, b2i".
2. `planlama/dongu-158.md` § 5 en üste kapanış satırı (saat `date`): "**P10.7b2i kapanışı** (commit "Lale P10.7b2i"): üretim tam (FreeCAD
   veri adımlı) çıkış 0 (süre, PDF sayfa), yol 9 / 12 kırpma hata 0, zincir 2–10 çıkış 0"; § 3 P10.7 satırının sonuna kısa b2i özeti ve
   kalın ibare tam olarak "**P10.7b2i kapandı**" (F9c-dogrula `**P10.7b2i … kapandı**` arar; F10q § 10'daki hata).
3. `planlama/d158/karar-kuyrugu.md`: `:1613-1614` (yol 9 GEO_ISTISNA) ve `:1728-1732`, `:1759-1760` (U06) maddelerinin sonuna "→ 19.11
   P10.7b2i: yapıldı (F10r-gunluk § 1 / § 2)" ekle; maddeleri silme.
4. Bu günlüğe "§ 8 Kapanış" (üretim ve zincir tablosu, 7.b çıktıları), DURUM satırı.
5. Yeniden koş: `F9c-uret.py --cikti "$U/sonuc.html"` + `F9c-dogrula.py --tarayicisiz --sayfa "$U/sonuc.html"` → GEÇER (hata 0); F9b,
   `regresyon.py --yazma`, `rehber_denetim.py --kaynak` 0, `F10l-birlesim.py` GECER. `__pycache__` kalmadığını denetle.

### 7.e Commit

Eski kir, girmez (19): 13 kabuk PNG'si (`tasarim/freecad/kabuk/gorsel/`), `tasarim/freecad/montaj/yerlesim-kontrol.json`, kökte
`geometri2_cikar.py`, `geometri2_dogrula.py`, `geometri_cikar.py`, `gez.js`, `uc.js`. **`git add -A` yok; dosyalar adıyla.**

Girecek (kaynak, 14 + 7.d'dekiler): `planlama/adim3/elektrik.md`, `planlama/adim3/kablolar.json`, `planlama/adim3/kablolar.md`,
`planlama/adim3/kablolar_denetim.py`, `planlama/d158/F10l-birlesim.py`, `planlama/d158/F10r-gunluk.md`, (kontrol dosyası
`planlama/d158/F10r-kontrol*.md` varsa), `tasarim/freecad/lale158/kablo_yolu_ekran.py`, `tasarim/freecad/lale158/lale158-kontrol.json`,
`tasarim/freecad/rehber/rehber_denetim.py`, `rehber_kablo.py`, `rehber_kritik_onay.json`, `rehber_metin.py`, `rehber_veri.py`; 7.d:
`planlama/d158/F9c-uret.py`, `planlama/dongu-158.md`, `planlama/d158/karar-kuyrugu.md`.
Girecek (üretim / zincir): `rehber/veri/rehber-veri.json`, `rehber-veri.js`, `robot.glb`, `robot-glb.js` (tam üretim GLB'yi de yazar),
`planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/kontrol.json`, `planlama/d158/F10a-dogrula.json`, `F10d-dogrula.json`,
`F10e-dogrula.json`, `F10f-dogrula.json`, üretimin değiştirdiği kareler (`git status --short -- rehber/goruntu planlama/rehber/goruntu`
listesindeki her `M` / `??` PNG, adıyla). Başka yeni yol görünürse alma, günlüğe yaz. `regresyon.json` değişirse dur, günlüğe yaz.

Push öncesi `git diff --cached` kişisel bilgi / yerel kullanıcı yolu / anahtar taraması (bu günlükteki yerel kullanıcı yolu kapanışta
yolsuz ifadeye çevrildi, § 8). Sonra:

```
git commit -m "Lale P10.7b2i: Kablo yolu 9'un eski XL4016 → ESP32 kısmı rehberde kırpıldı (y + z kesimi), U06 şeması ESP32 portuna yeniden çizildi (boy 1.560), boy kaynağı tazelik denetimi, rehber yeniden üretildi"
git push origin lale-duzeltme
```

(İleti sonuna depodaki kurala göre yardımcı satırı.) Push sonrası `git fetch` + `git rev-list --left-right --count HEAD...origin/lale-duzeltme` → 0 0.

### 7.f Bir adım kırmızıysa

F10q § 9.f ile aynı: commit / push yok; log'un son 60 satırı ve `.durum` "§ 8 Kapanış: KALDI" başlığıyla bu günlüğe; çıktıları geri alma
ya da commit'leme. `rehber_veri.py` `CAD_KIRP: …` `SystemExit` verirse mesajı olduğu gibi yaz: kesim / nokta / izdüşüm değerleri § 1
tablosuyla karşılaştırılır (deneme aynı kodla geçti; fark çıkarsa model dosyası ya da `taban-analiz.json` değişmiş olabilir: paralel CAD
ajanının işi buraya birleştiyse önce o).

Tahmini kapanış süresi: kontrol sonrası ön sınama 2 dk + üretim 45–50 dk + 7.b 2 dk + zincir 50–55 dk + 7.d / commit 10 dk ≈ **1 sa 50 dk–2 sa**.

## Kontrol ajanının özellikle bakması gerekenler

1. `rehber_veri.kirp()` dönüş yönü: `App.Rotation(V(0,1,0), yon)` + `transformShape(R⁻¹)` ile izdüşüm, +y'de birim mi (yol 12 sonuçları
   b2f ile birebir: 3.944,49 mm³, 81,22 mm²). Deneme betiği depo dışında, gerçek kaynağı okuyor.
2. `glb_kutulari` artık üçlü döndürüyor: başka bir çağıran (F10d / F10e / app) iki elemanlı bekliyor mu (aramada yalnız `rehber_kablo`
   buldum).
3. K1 17.11'deki "önden bakınca sağ ucundaki portuna" (+x) yön ifadesi ve "ESP32 taşıyıcısı ile güç panelindeki XL4016 C'nin arasından"
   tarifinin karede okunurluğu (üretimden sonra, K1 alt adım 11 karesi; U06 şeması bu karede değil 32.4'te çiziliyor olabilir).
4. Fiş boyu 18 mm ve port yeri TAHMİN (ürün elde yok); şema sınaması son noktayı DevKit kutusuna 0,5 mm buluyor, istisnasız geçiyor.
5. K64 bağımlılığı (§ 2 sonu): CAD ajanının bara tutucusu bu şeritlere düşerse U06 yeniden çizilir.
6. `boy_tazelik` kuralının kapsamı: yalnız JSON anahtarlı `boy`; metin satırı kaynaklı boylara (yok) bakmaz.

## 8. Kapanış (02:10–05:55, kapanış ajanı)

**Kontrol düzeltmeleri (F10r-kontrol):**
- D2: § 0 üstündeki paralel CAD worktree yolu yolsuz ifadeye çevrildi; § 7.e notu güncellendi.
- D1: `F8a-siparis.json` S58 `not2` ve `F8a-siparis.md` S58 satırı: "1,5 m: ESP32 USB'ye yetmez (önerilen 1.560 mm, P10.7b2i); yalnız
  göğüs dokunmatiğine (640 mm) yeter". Ürün, adet, fiyat, `maliyet.json` değişmedi. Bu iki dosyayı bağlayan üretici / onay kaydı yok
  (`not2`'yi okuyan betik yok; F9c-dogrula yalnız doğrulanan satır sayacını okur, GEÇER).
- D3: `kafa-yerlesim/uygulama-notu.md:110` ve `kablo-kurali-notu.md:34` satırlarına "→ 19.11 P10.7b2i: 1.129 / 1.560";
  `uygulama-olcum.json` yenilemesi kuyrukta (`uygulama-notu.md` `uygulama_rapor.py` üretimidir, yenilenince ek kaynaktan gelir).
- D4, D5, D6, B1 ve D7 (düzeltmesi onay kaydını yeniden yenilettiği için yapılmadı) `karar-kuyrugu.md` sonunda "P10.7b2i bağımsız
  kontrolünden açık iş" altında. Düzeltmelerden sonra `rehber_kablo`, `rehber_denetim --kaynak`, `kablolar_denetim`, `F10l-birlesim`: hepsi 0.

**Üretim ve zincir:**

| Adım | Sonuç | Çıkış | Süre |
|---|---|---|---|
| 7.a tam üretim (FreeCAD veri adımlı) | ön sınama onay tutuyor (220 / 226 / 1142); parça 1192, 50 adım, alt adım 91, şema 65; uç etiketi 24 / 48 / 46 (b2f ile aynı); PDF 86 sayfa, taşan 0, en küçük 8,1 pt; denetim ASCII 0, zorunlu eksik 0 / 131; tarayıcı 50 / 50 | 0 | 2515 s |
| 7.b yeterlilik | `rehber_kablo --veri`: "kırpma kesimi: yol 9 (0, 0.7071, 0.7071) · p ≤ 143.92, yol 12 y ≤ 192.5; hata 0", "kırpılan CAD yolları … robot.glb okundu; hata 0", şema geometrisi hata 0 / istisnalı 4, SONUÇ GEÇER (eski veriyle KALDI veren "yol 9 … eski kısım çiziliyor" kalktı); ESP32 USB şeması 1, son noktalar (125; 205; 37), (127,5; 200,7; 75), (109,5; 200,7; 75), `boy_mm` 1129; "yanlış yerde" ve "eski çizimdir (doğrudan ESP32" 0 | 0 | - |
| 2a / 2b / 3 | SONUÇ GEÇER; bozma 116 / 116; denetim ASCII 0, zorunlu eksik 0 / 131, yasak 0, elektrik iddiası 0 | 0 | - |
| 4 F10f / 5 F10e | GEÇTİ / GEÇTİ (`renk_demo` KALDI bilinen) | 0 / 0 | 718 / 1168 s |
| 6 F10d (ilk koşu) | **KALDI**: uç etiketi hata 3: U1 17.7 "2 XL4016 çevre çizilmedi (güvenli alanın dışında)" (sahne + etkileşimli), U4 17.7 p1019 karede 0 px | 2 | 1099 s |
| 7 F10a | GEÇTİ (bu koşu, düzeltmeden önceki veriyle) | 0 | 524 s |

Neden (paket içi): 17.7'nin `kamera` / `odak`'ı yoktu, kadraj vurgulu yola (p1188) sığıyordu. Yol XL4016 çevrede kırpılınca kutusu küçüldü
(y ≥ 122,5); XL4016 çevre etiket noktası y 114,2'de kadrajın kenarına düştü. Düzeltme: `rehber_metin.DEMET_ALT` K1 17.7'ye
`odak=("Kablo yolu 9:", "Sigorta kutusu", "XL4016 çevre")` (gerekçe satırıyla; denetleyici ve onay kaydı değişmedi, `rehber_denetim
--kaynak` 0). Tek adım önizlemesi (`--veri-yok --adimlar 17 --ek-yok`, 114 s) ve paralel F10d ön koşusu: uç etiketi hata 0, GEÇTİ.

| Adım (düzeltmeden sonra) | Sonuç | Çıkış | Süre |
|---|---|---|---|
| üretim `--veri-yok` | görünüm `K1.7 odak`; PDF 86 sayfa, taşan 0, en küçük 8,1 pt; tamlık eksik 0; denetim ASCII 0, zorunlu eksik 0 / 131; kablo eşleme GEÇTİ; tarayıcı 50 / 50 (F10d ön koşusuyla paralel, bu yüzden uzun) | 0 | 3195 s |
| 2a / 2b / 3 | 7.b ile aynı çıktılar; 116 / 116; denetim 0 | 0 | - |
| 4 F10f | GEÇTİ | 0 | 679 s |
| 5 F10e `--goruntu-yok` | GEÇTİ (`renk_demo` KALDI bilinen) | 0 | 1162 s |
| 6 F10d `--goruntu-yok` (tek başına) | GEÇTİ; uç etiketi 20 konum / 48 / 35, hata 0; 360 px taşma 0 | 0 | 1096 s |
| 7 F10a `--kanit-yok` | GEÇTİ, dış istek 0, konsol 0 | 0 | 526 s |
| 8 F9b / 9 çarpışma / 10 regresyon `--yazma` | GEÇER hata 0 / izlenen 17 dosya kayıtla aynı / GEÇER, kötüleşen yok, `regresyon.json` değişmedi | 0 | < 10 s |

Not: üretim logunda tarifin beklediği "CAD_KIRP: …" satırları yok; `rehber_uret.veri()` FreeCAD çıktısını süzüp yalnız mesh / GLB / bitti
satırlarını basıyor. Kesimin kanıtı veri adımının "bitti: 50 adim" ile bitmesi (`kirp()` SystemExit verseydi "bitti" olmazdı) ve 7.b'nin
GLB izdüşüm sınaması. 7.d: F9c-uret P10.7 / F10 özetleri, `dongu-158.md` § 3 ve § 5, kuyruk notları; F9c-uret + F9c-dogrula GEÇER (hata
0), F9b, regresyon, `rehber_denetim --kaynak`, `F10l-birlesim`, `rehber_kablo`, `kablolar_denetim` yeniden 0. FreeCAD'in yazdığı
`__pycache__` (cpython-311; `planlama/adim4`, `tasarim/freecad`, `lale158`, `rehber`) silindi; önceden var olanlar duruyor.

**Gözle görüldü (kareler):**
- 17.7: eski karede (HEAD) kırmızı G18 tüpü XL4016 çevreden sola, ESP32'ye doğru uzanıyordu; yeni karede o kısım yok, yol sigorta
  kutusundan ("1") XL4016 çevreye iniyor, kesik uçta artık yok. Düzeltmeden sonra "2 XL4016 çevre" etiketi de karede.
- 32.4: eski karede U06 direğin dibinden tabana dik iniyordu; yeni karede direğin dibinden elektronik katı üstünden yana kıvrılıp bir
  kartta ("1" işaretinin yanında) bitiyor. Kare geniş (direğin boyu); micro USB portu bu ölçekte seçilemiyor: "portta bitiyor" yalnız
  veriyle (son nokta port ağzının 2,5 mm önü) doğrulandı.
- 17.11: karede U06 çizilmiyor; tek uç etiketi "1 PCA9685" (P03). Metin fişi ESP32 portuna taktırıyor ama karede ESP32 / U06 vurgusu
  yok: metin ile kare kısmen uyuşuyor (kuyruğa yazıldı). K2 (32.4) metni "ESP32 USB 1.560" ile veri `boy_mm` 1129 / önerilen 1.560 tutarlı.
