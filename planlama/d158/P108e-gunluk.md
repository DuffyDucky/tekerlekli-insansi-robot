# P10.8e günlüğü: rehber açıkları (A ajanı)

Paket: P10.8e, A (uygulama). Başlangıç 21.11 ≈ 06:55. Dal `lale-duzeltme`, yerel = uzak = `269e51b`. Kilit tablosu satırı
`planlama/dongu-158.md` § Kilit tablosu (P10.8e). Commit / push B'nin işi; bu günlük adım adım yazıldı (her maddeden sonra).

Kaynaklar: `planlama/dongu-158.md` (P10.8 hücresi, § 5 satır 27), `planlama/d158/P108d-gunluk.md` (§ 3, § 4, § 6, § 7, § 11),
`planlama/d158/P108d-kontrol.md` (§ 5 devir listesi), `planlama/d158/karar-kuyrugu.md` (P10.8b rehber açıkları, P10.8c kapanışı).

## 1. Başlangıç durumu

| Ne | Değer |
| --- | --- |
| HEAD / origin | `269e51b` / `269e51b` |
| FreeCAD kilidi | boş; FreeCAD süreci yok |
| Boş bellek | ≈ 7,1 GB |
| `git status --short` | 21 satır (eski kirli / izlenmeyen dosyalar; görev listesindeki 21 dosya) |
| `rehber_kablo.py` | çıkış 1, SONUÇ KALDI (1 hata): "HATA şema SV3 son ucu [100.0, 192.0, -60.0]: uç noktasının yanındaki parça (Dagitim karti C …) eşlenen kabloların ucu değil"; uç etiketi 49 modelde / 8 modelsiz; ayırt edilemeyen çift 0 |
| `rehber_denetim.py --kaynak` | çıkış 1, ascii kalıntı 5: nominal, vidali, dort, kopru, giris; CAD kaynak etiket / kod 975, eskime HATA 0 / bilgi 2; onay farkı 0 (kablo 220, liste 258, metin 1199) |
| `rehber_denetim.py` (veri) | çıkış 0; parça 1238, şema 65, zorunlu 0/165 |
| `planlama/adim3/kablolar_denetim.py` | çıkış 0, GEÇER |
| `planlama/d158/F10l-birlesim.py` | çıkış 0, GEÇER (taban `d8ade70`, eklenen 2 / silinen 2) |

Önce logları: `planlama/d158/P108e-olcum/once/` (rehber_kablo.log, kaynak.log, veri.log, kablolar.log, birlesim.log).
Eski kirli dosyaların başlangıç özeti (md5): `planlama/d158/P108e-olcum/kir-bas.md5` (13 kabuk PNG'si, `yerlesim-kontrol.json`, 5 kök
dosya, `P108d-olcum/ara1.json`); sonda aynı listeyle karşılaştırılır.

### 1.1 Plan ile görev özeti arasındaki farklar

- Plan (P10.8 hücresi) altı maddeye ek olarak şunları sayıyor: rehberde `PARCA_CAD` / `UC_MODELSIZ` / `MODELSIZ_KONUM` kayıtlarının
  modele (P10.8d kartlarına) bağlanması, `rehber_metin.py` yol 11 / 12 cümleleri ve `rehber_denetim.py` ZORUNLU kuralı, rehber verisi
  1.238 → 1.264 parça. Plan kazanır: bunlar madde 1 ve madde 6'nın içinde yapıldı.
- Madde 5: `uygulama_ivme.py` P10.8d'de B tarafından zaten yeniden koşuldu (`uygulama-ivme.json` rampa5_geri 1,519 → 1,523;
  P108d-kontrol § 5). Kalan iş yalnız rapor / notun (`uygulama_rapor.py`) yeniden üretilmesi.
- Bu pakette değil (plan): K52, K31 insert boyu, `TABAN_DISI_BOLGE`.
- Görev özetinde "madde 1 = kart C / SV3 şema hatası" yalnız `sema_geometri_denetle` hatası; plan aynı maddede kartların rehberde modele
  bağlanmasını da istiyor. Çözüm ikisini birlikte kapattı (§ 3): SV3 hatasının nedeni rehberin kartı "modelsiz" saymasıydı.
- Kapsamı genişleten, planda yazılı olmayan iki bulgu (yapıldı, gerekçe § 3, § 6): (a) `rehber_secici` iki yeni kartı (26 parça) B5a'ya
  atıyor; B5a metni kartları anmıyordu, bir cümle eklendi. (b) `uygulama_metin.py` "o koşudan sonra montaj değişti … yeniden
  hesaplanmadı" cümlesini fark 0,0 g'da da yazıyordu; koşullu yapıldı.

## 2. Madde 2: `--kaynak` ASCII kalıntısı (5 → 0)

| Kelime | Yer (CAD kaynağı, P10.8d kartları) | Çözüm |
| --- | --- | --- |
| nominal | etiket "Acil stop dugum karti (pertinaks, nominal zarf TAHMIN)" | `rehber_denetim.ASCII_TAMAM` (doğru yazım) |
| vidali, dort, kopru | kod "Delikli pertinaks 30 x 30 (TAHMIN): 2x 2 pin 5,08 mm vidali klemens, dort ucu >= 18 AWG tel kopru" | `rehber_metin.TR_EK`: vidalı, dört, köprü |
| giris | kod "Delikli pertinaks 36 x 30 (TAHMIN): 16 AWG giris klemensi, …" | `TR_EK`: giriş |

Görünen ad sonrası (`RM.tr`): "… vidalı klemens, dört ucu >= 18 AWG tel köprü". Yasak kalıp ("köprü teli") tetiklenmedi (yasak 0).
Madde 1 / 3 metinleri iki yeni ASCII kelime getirdi ("kesikten" K1 17.10, "dibinden" K1 17.11): doğru yazım, `ASCII_TAMAM`'a eklendi.

| Ölçü | Önce | Sonra |
| --- | --- | --- |
| `rehber_denetim.py --kaynak` ascii kalıntı | 5 (çıkış 1) | 0 (çıkış 0) |

## 3. Madde 1: SV3 ↔ dağıtım kartı C ve kartların rehberde modele bağlanması

Neden: P10.8d iki kartı (acil stop düğüm kartı, dağıtım kartı C) modele ekledi, rehber ikisini hâlâ "modelsiz" sayıyordu. SV3 şemasının son
ucu (100; 192; −60) artık modelli kartın kutusuna 3,0 mm (P108d § 4) ve "uç noktasının yanındaki parça eşlenen kabloların ucu değil" hatası
veriyordu. CAD geometrisi değişmedi; yalnız rehber kaynağı.

`tasarim/freecad/rehber/rehber_kablo.py`:
- `PARCA_CAD`: "Acil stop düğümü" MODELSIZ → `^Acil stop dugum karti`; "Dağıtım kartı C" MODELSIZ → `^Dagitim karti C`.
- `MODELSIZ_KONUM`: iki "elle bakıldı" kaydı kalktı. `UC_MODELSIZ` → `UC_ETIKET`: "Acil stop düğümü (mantar NC çıkışı)",
  "Dağıtım kartı C (kafa)" (desen modelde tam 1 parça; uç etiketi 49 / 8 → 51 / 6).
- `SEMA_KONUM` "Dağıtım kartı C" nominal noktası kalktı. Yerine `sema_geometri_denetle`: `kablo_yolu_taban.DAGITIM_C` kartın kutusuna
  ≤ `DAGITIM_C_ESIK` (5 mm) olmalı ve desen modelde tam 1 parça (bugün 3,0 mm).
- Yeni `GEO_YAN_ELLE` {(6, S09, a), (6, S10, a)}: CAD yolu 6 yalnız boyun → kafa bölümünü çiziyor (taban ucu (0; 1215; −26)); kart
  modelli olunca bu iki kablonun kart yanı "yola ulaşmıyor" hatası veriyordu (P108d § 6 bellek deneyi: 2 hata). Yan "elle bakıldı"
  bilgisi yazılır (P10.8d öncesi davranış), yan yola ulaşırsa ya da kayıt kullanılmazsa HATA. Onay kaydına girer.
- Bozma: b44 (kart C = XL4016 C kutusu) artık `DAGITIM_C` eşiğiyle yakalanıyor; b77 `SEMA_KONUM` yerine `kablo_yolu_taban.DAGITIM_C`'yi
  30 mm kaydırır; b79 SV3 yerine modelsiz uçlu K01'in adından "yeri yaklaşık"ı siler; yeni b107–b110 (elle kaydı silindi, kullanılmayan
  kayıt, ulaşan yan elle sayıldı, düğüm kartı yerine ön şarj kartı). 114 → 118, hepsi yakalandı.

**CAD paketine devir (yapılmadı, geometri):** CAD yolu 6 (`taban_parcalar.py` YOL[5], 3 nokta: (0; 1215; −26) → (0; 1290; −30) →
(0; 1325; −10)) kart C'ye inmiyor. Kartın kutusu x 94…130, y 187,5…199,1, z −92…−62 (taban-analiz.json); yolun taban ucu karttan
≈ 1.020 mm yukarıda. Yolun kart C'den direk arka yüzüne çıkan bölümü çizilirse `GEO_YAN_ELLE` iki kaydı "yan yola ulaşıyor" HATA'sıyla
kendini gösterir ve silinir.

`rehber_metin.py` metinleri (eski → yeni):
- B5a kablo notu: "Dağıtım kartı C modelde yok: şemanın o ucunun yeri yaklaşık" → "Dağıtım kartı C modelde (zarfı ve ölçüsü TAHMİN, kart
  yapılınca ölçülecek): şema kartın ön (+z) kenarının yanında biter".
- B5a iş: kart listesine "acil stop düğüm kartı (röle K1 ile ön şarj kartının arasında)" ve dört M3×8 naylon burç / M3×6 / M3×8 eklendi;
  "İki kartın ölçüsü ve zarfı TAHMİN". Gerekçe: `rehber_secici` 26 yeni parçanın 26'sını B5a'ya atıyor (simülasyon, `grup`
  "Guc_aku_surucu_panel"; analiz JSON'undaki "Guc" grubuyla düğüm kartı F1'e, kart C hiçbir adıma düşüyordu: gerçek grup adı belirleyici).
  B5a kontrolü: "… acil stop düğüm kartı ve dağıtım kartı C de (P10.8d yerleşimi)".
- K1 17.8: "acil stop düğüm kartı karede görünmez (modelde yok)" → "acil stop düğüm kartı güç panelinde aynı yanda, röle K1 ile ön şarj
  kartının arasında (zarfı TAHMİN)". Yer taban-analiz.json'dan: düğüm kartı x −133…−103, z −105…−75; röle z −155…−115; ön şarj z −26…24.
- K1 17.10: "karedeki Kablo yolu 11 ve 12 kesiğin dışında görünür (çizim kusuru)" → "karedeki Kablo yolu 11 ve 12 de kesikten geçer"
  (P108d § 2: yol 11 kesikten x −28, yol 12 (−25,0; 160,7)). `rehber_denetim.py` ZORUNLU kuralı yeni cümleye çevrildi.
- `KABLO_AD` 11 / 12: "çizimdeki yol kesiğin dışında görünür" → "(çizimdeki yol da, P10.8d)".
- K1 kablo notu (P03 tablosu): "Dağıtım kartı C modelde yok, yeri çizilmez" → "modelde, XL4016 C'nin arka yanında (zarfı TAHMİN)".
- SEMA SV3 adı: "(yeri yaklaşık: modelde yok, XL4016 C'nin yanında)" → "(XL4016 C'nin arka yanında, zarfı TAHMİN)".
- `kablo_yolu_taban.py` yorumları (DAGITIM_C, SV3, başlık) aynı gerçeğe çevrildi.

| Ölçü | Önce | Sonra |
| --- | --- | --- |
| `rehber_kablo.py` | çıkış 1, 1 hata (SV3 son ucu ↔ kart C) | çıkış 0, GEÇER; SV3 uçları tamam |
| `geometri_denetle` (CAD yolları) | 0 hata (kartlar modelsiz, elle) | 0 hata; 2 bilgi (yol 6 S09 / S10 a GEO_YAN_ELLE) |
| uç etiketi modelde / modelsiz | 49 / 8 | 51 / 6, hata 0 |
| `rehber_kablo.py --bozma-denemesi` | 114 / 114 (P10.8c) | 118 / 118 |
| onay kaydı (kablo / liste / metin) | 220 / 258 / 1199 | 219 / 258 / 1201 (`--kritik-onay-yenile`, 25 fark; § 7) |

## 4. Madde 4: G07 ve G16 şemaları (katı içinden geçme)

Ölçüm (B-rep, FreeCAD 1.1, salt okuma): `planlama/d158/P108e-sema-olcum.py` + girdi `planlama/d158/P108e-sema-girdi.py <etiket>`.
Montaj `tasarim/freecad/montaj/robot-montaj.FCStd` açıldı, kaydedilmedi; 1.251 gerçek parça (Tur ≠ Referans), şemanın eksen çizgisi ×
parça `distToShape`. "ara" = en yakın nokta şemanın iki ucundan da 10 mm'den uzak. Çıktılar `P108e-olcum/sema-once.json`,
`sema-sonra.json` (+ `.log`, `sema-girdi-*.json`). FreeCAD kilidi her koşu için alındı, sonra "boş" yazıldı (her koşu ≈ 4 s).

Yalnız şema kaynağı değişti: `tasarim/freecad/lale158/kablo_yolu_taban.py` (`yollar()` G07, G16). Parça / montaj kaynağı, FCStd, STEP
değişmedi.

| Şema | Önce (noktalar) | Sonra (noktalar) |
| --- | --- | --- |
| G07 (r çizim 2,5) | (−95,4; 214; −178) → (−56; 184; −165) → (−56; 184; 45) → (−70; 196; 51) | (−95,4; 214; −178) → (−58; 195; −165) → (−58; 195; 45) → (−70; 196; 51) |
| G16 (r çizim 3,6) | saplama (−12,5; 191,9; −110) → (−12,5; 195; −95) → (−12,5; 195; −30) → (55; 195; −5) → (61; 196; 0) | saplama → (−12,5; 195; −95) → (−12,5; 195; −30) → **(28; 195; −30)** → (55; 195; −5) → (61; 196; 0) |

| Ölçü (B-rep) | Önce | Sonra |
| --- | --- | --- |
| G07 eksen içinde parça | 1 (Bara tutucusu yıldız, 0,0) | 0 |
| G07 çizim (r 2,5) içinde, ara | 4 (yıldız tutucusu 0,0; anahtarlı tutucu 0,5; M3 ısıl gömme 2,0; yıldız 1 M5 cıvata 2,119) | 0 |
| G07 en dar ara | 0,0 mm (Bara tutucusu yıldız) | 4,0 mm (Somun M5 yıldız 1); sonra 4,74 yaylı pul, 5,15 ön şarj kartı vidaları |
| G07 en dar uç | 2,0 (ana anahtar gövdesi, tahmini zarf) | 2,0 (aynı; uç değişmedi) |
| G16 eksen içinde, ara | 1 (Gövde direği, 0,0 mm; nokta (20; 195; −18), uca 44,8 mm) | 0 |
| G16 çizim (r 3,6) içinde, ara | 1 | 0 |
| G16 en dar ara | 0,0 (Gövde direği) | 5,5 (Bara tutucusu yıldız, dikeyde: hat y 195, tutucu üstü 189,5) |
| G16 uç | bara saplaması (pabuç saplamada; uç, beklenen) | aynı |
| Şema boyu (`kablo_yolu_taban.py` ozet) | G07 281 mm, G16 160 mm | G07 267 mm, G16 165 mm |
| `kablolar.json` `sema_boy.mm` | 281 / 160 | 267 / 165 (`rehber_kablo.py --sema-boy-yaz`; fark yalnız bu iki satır) |

`kablolar.json` değişince `planlama/adim3/kablolar.md` eskidi (`kablolar_denetim` "gorunum" GEÇMEZ): `py -3 -B -X utf8
planlama/adim3/kablolar_uret.py` ile yeniden yazıldı (fark yalnız G07 / G16 gösterim şeması boyu, 2 satır).

Gerekçe: G07 bara kabloları gibi tutucu üstü yükseklikte (`Y_BARA_UST` 195) gider; x −58, yıldız 1 saplamasının cıvata / somun yığını
(x ≥ −54) ile ön şarj kartı (x ≤ −62,5) arası. G16 direğin (x, z −20…20) arkasından z −30'da x 28'e kadar düz, sonra eski dönüşle
XL4016 C'ye. Kat / plaka geçişi iki şemada da yok (`gecis_denetle` boş, önce de boştu). Bu bir gösterim şemasıdır, boy ölçümü değildir.

## 5. Madde 3: rehber kareleri 32.1 ve 17.11

Yöntem: `planlama/d158/P108e-onizleme.py` (P108b § 5 yöntemi): `rehber/` klasörünün geçici kopyasına (sistemin geçici klasöründe) aday
görünüm alanları yazılır, headless Chrome 1400 × 900 kare çeker. Kareler `planlama/d158/P108e-olcum/onizleme/`. Veri eski (1.238 parça,
kartlar yok); 32.1 kartlara bağlı değil, 17.11'de kart C kareye tam üretimde girer.

**17.11 (U06 çizgisi yoktu).** Yeni "adım ötesi şema" (`sema_on`): `DEMET_ALT` K1 alt adım 11 `sema_on={"(U06)": (300.0, not)}`.
- `rehber_veri.py`: desen tam bir şemaya uymalı, şema sonraki adımın olmalı, y ≤ sınır noktaları şemanın bir ucunda bitişik ve ≥ 2;
  uymazsa üretim durur. Veride `sira_grup[].sema_on = [{i, pts, not_, y_ust}]`. U06: 10 noktanın son 8'i (direk dibinden (14; 300; −26)
  ESP32 portuna).
- `app.js`: `tupGeo` (tüp geometrisi tek yerde), `ON_OBJ`; `uygula` alt adımın `sema_on` bölümünü vurgulu çizer, lejantta sınıfını
  sayar; `userData.d = "on"` (F10d `sema_karede` yalnız "simdi"yi sayar, SEMA_OBJ kendi adımına dek gizli). Lejantta not satırı.
- `rehber_gorunum.uc_isle`: `sema_on` kabloları uç etiketi kümesine; `etiket_kablo=("U06",)` kalktı (U06 artık çizilen kablo).
- Odak: "Dağıtım kartı C" eklendi. Metin: "Bu alt adımın kabloları karede vurgulu değil: … U06'nın şeması … karesinde" → "Karede
  vurgulu çizgi U06'nın taban bölümüdür (direk dibinden ESP32'ye; tamamı K2 madde 4'ün karesinde)"; kart C "güç panelinde, XL4016 C'nin
  arka yanında (B5a)".
- Önizleme `k1_11-17-11.png` (bakıldı): gri U06 çizgisi direk dibinden ESP32 taşıyıcısına iniyor, etiket 1 PCA9685, 2 ESP32; lejant
  "Kablo: Hazır kablo: USB" ve not satırı. Önce (`simdiki-17-11.png`): çizgi yok.

**32.1 (yolun anahtarlı baradan çıkışı seçilmiyordu; P108b § 5'te üç bakış denenmiş, açık bırakılmıştı).** Beş bakış denendi:

| Aday | Kamera / odak | Gözle (bakıldı) |
| --- | --- | --- |
| simdiki | "arka" (sağ-arkadan), bütün robot | bara çıkışı seçilmiyor (eski kare) |
| k2_1_arka_taban | "arka" + taban odağı | çok yakın; bara saplamaları büyük, dağıtım kartları kenarda, okunmuyor |
| k2_1_arkaust_taban | (0,35; 1; −0,8) + taban odağı | iyi ama etiket 3 (dağıtım B) direğin üstüne düşüyor, kart direğin arkasında |
| k2_1_arka_dik | (0; 1; −0,7) + taban odağı | **seçildi**: anahtarlı baranın 4 saplaması önde, sarı çizgi 1 numaralı saplamaya (arkadan bakınca en sağ) iniyor, iki dağıtım kartı direğin iki yanında (etiket 1, 3), direğe çıkış görünüyor |
| k2_1_arka_yuksek | (0,08; 1,4; −0,6) + taban odağı | kartlar direk kollarının arkasına giriyor |

Taban odağı: "Servo dağıtım kartı A / B", "XL4016 servo 6 V A / B", "Bara tutucusu anahtarlı". Omuz uçları (etiket 2, 4) kadraj dışı:
`UC_ORTULU[("K2", 1)]` "sağ S1 …" / "sol S1 …" = "bu kadrajın dışında" (17.4 emsali). Metin: "Kare tabana arkadan ve üstten bakar: yolun
anahtarlı baradan çıkışı, iki dağıtım kartı ve direğe çıkış karede; omuz uçları kadrajın dışında." Son kare tam üretimde (§ 8);
orada omuz uçları etiketlenmediği için numaralar 1 (dağıtım kartı A), 2 (dağıtım kartı B) oldu (önizlemede 1 / 3).

## 6. Madde 5: `uygulama_ivme` ve kafa-yerleşim raporu

`uygulama_ivme.py` P10.8d'de yeniden koşulmuştu (`uygulama-ivme.json`, yüksüz ızgara 1,523); bu pakette yeniden koşulmadı. Rapor ve not
`py -3 -B -X utf8 tasarim/freecad/lale158/kafa-yerlesim/uygulama_rapor.py` ile yeniden üretildi (çıkış 0; log `P108e-olcum/uygulama-rapor.log`,
"yazildi boy 1580.0 kafa 1542.7 izgara 1.523 esik alti False").

İlk koşuda not "o koşudan sonra montaj değişti: … (fark 0,0 g). Devrilme payları yeni montajla yeniden hesaplanmadı" ve karar listesinde
"`uygulama_ivme.py` yeniden koşulsun mu?" yazıyordu: ikisi de artık yanlış. Üretici `uygulama_metin.py` koşullu yapıldı (fark < 1 g ise
"koşu güncel montajla aynı kütleyi veriyor … Devrilme payları bu montajla hesaplandı", soru yazılmaz) ve rapor yeniden üretildi.

| `uygulama-notu.md` / `rapor.html` | Önce (19.11) | Sonra (21.11) |
| --- | --- | --- |
| yüksüz ızgara devrilme payı | 1,519 (3 yerde) | 1,523 (4 yerde; tablonun "önce" sütunu 1,523 zaten) |
| elde 100 g / 500 g | 1,479 / 1,329 | 1,483 / 1,333 |
| fren payı yüksüz | 1,747 | 1,751 |
| ev pozu kütle / AM y | 26.120,6 g / 522,84 | 26.276,1 g / 520,50 |
| parça sayısı | 1.225 | 1.251 |
| çarpışma koşusu | 20261119-075818 | 20261121-023529 |
| "yeniden hesaplanmadı" / "yeniden koşulsun mu" | var | yok |

## 7. Onay kaydı, birleşim beklentisi ve ön sınamalar (üretimden önce)

- `py -3 -B -X utf8 tasarim/freecad/rehber/rehber_denetim.py --kritik-onay-yenile`: çıkış 0, 25 fark yazıldı (log
  `P108e-olcum/ara/onay-yenile.log`): kablo 11 (GEO_YAN_ELLE +2, MODELSIZ_KONUM −2, PARCA_CAD ~2, SEMA_KONUM −1, UC_ETIKET +2,
  UC_MODELSIZ −2), liste 1 (ZORUNLU), metin 13 (B5a is_ / kablo / kontrol, K1 17.8 / 17.10 / 17.11, K1 kablo, K2 32.1, KABLO_AD 11 / 12,
  SEMA SV3). Kayıt 220 / 258 / 1199 → 219 / 258 / 1201. **Bu 25 fark bağımsız kontrolden geçmeli** (B).
- `planlama/d158/F10l-birlesim.py`: varsayılan taban `d8ade70` → `269e51b`; `BEKLENEN["269e51b"] = (P108E_SILINEN, P108E_EKLENEN)`,
  11 silinen + 13 eklenen cümle, dört etiket ("kartlar modelde (P10.8d)", "yol 11 / 12 kesikten (P10.8d)", "17.11 U06 taban bölümü",
  "32.1 taban bakışı"). Liste olmadan 269e51b'ye karşı KALIR (24), listeyle GEÇER (eski taban d8ade70'e karşı KALIR, beklenen).
- Ön sınamalar (loglar `P108e-olcum/on/`):

| Komut | Sonuç |
| --- | --- |
| `rehber_kablo.py` | 0, GEÇER |
| `rehber_kablo.py --bozma-denemesi` | 0, 118 / 118 |
| `rehber_denetim.py --kaynak` | 0; ascii 0, onay farkı 0, CAD etiket / kod 975, eskime HATA 0 / bilgi 2 |
| `rehber_denetim.py --bozma-denemesi` | 0, 347 / 347 |
| `planlama/adim3/kablolar_denetim.py` | önce 1 ("gorunum": `kablolar.md` eski) → `kablolar_uret.py` → 0, GEÇER |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 0, 174 bozma, GEÇER |
| `planlama/d158/F10l-birlesim.py` | 0, GEÇER |
| `tasarim/freecad/test/kupon_tazelik.py` | 0, TAZE (16 denetim) |
| `planlama/d158/F4c-dogrula.py` | 0, GEÇTİ |

Not: görevde yazan `test/kupon_tazelik.py` yolu yok; betik `tasarim/freecad/test/kupon_tazelik.py`.

## 8. Madde 6: tam rehber üretimi

`py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py`, Bash arka planı, ilerleme `P108e-olcum/uretim.durum`, log `P108e-olcum/uretim.log`.
FreeCAD kilidi 07:21'de alındı; veri adımı 07:25'te bitti (`freecadcmd` süreci kalmadı), kilit 07:33'te "boş" yazıldı.

| Ölçü | P10.8c (19.11) | P10.8e (21.11) |
| --- | --- | --- |
| Süre / çıkış | 3.119 s / 0 | **2.693 s (07:21:40–08:06:33) / 0**; Traceback / Exception 0; "ek kontrol sorunlu: -" |
| Veri | 1.238 parça, 50 adım, 65 şema | **1.264 parça** (+26: iki kart, 8 burç, 16 vida; 26'sı B5a'da), 50 adım, 65 şema |
| Uç etiketi (karede) | 58 | 60 (B5a: 1 XL4016 C, 2 Dağıtım kartı C) |
| Alt adım | 91 / 91 | 91 / 91, her şema tek alt adımda (60) |
| PDF | 89 sayfa | 90 sayfa, taşan yok, en küçük yazı 8,1 pt |
| Metin denetimi | temiz | ASCII 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0, standart 0, elektrik iddiası 0 |
| Sıra / giriş / uçuş | 0 / 0 / 0 | ulaşılamaz 0, girilemez 0, uçuş çarpışan 0, `istisna_bos` 0, ısıl gömme hata 0 |
| Tarayıcı | 50 / 50, konsol 0 | 50 / 50, konsol 0, her parça tek adımda |

Veride: `sema_on` yalnız K1 alt adım 11'de (U06, 10 noktanın 8'i); K2 alt adım 1 kamera (0; 1; −0,7), odak 53 parça. Log satırı
"rehber_metin alanlari, degisen 2: G4.4 sema_yalniz, G4.5 sema_yalniz" bu paketin değişikliği değil (bilgi; incelenmedi).

**Bakılan kareler** (`rehber/goruntu/`, gözle):
- `adim-17-11.png`: gri U06 çizgisi direk dibinden ESP32'ye iniyor; etiket 1 PCA9685, 2 dağıtım kartı C (artık modelde, kart ve burçları
  görünüyor), 3 ESP32; lejantta "ESP32 USB (U06): yalnız taban bölümü (…); tamamı K2 madde 4'ün karesinde".
- `adim-32-01.png`: önizlemeyle (k2_1_arka_dik) aynı bakış; anahtarlı baranın saplamaları, sarı yolun baradan çıkışı ve direğe
  çıkışı, dağıtım kartı A (1) ve B (2) direğin iki yanında. Konum kutusu "orta · y 100–1290".
- `adim-12.png` (B5a tezgâh): etiket 1 XL4016 C, 2 dağıtım kartı C (dört burçla), sarı SV3 aralarında. Acil stop düğüm kartı
  karede etiketsiz; hangi kart olduğunu kareden ayırt etmedim.
- `adim-17-08.png`: yeşil acil stop kablosu, etiket 1–4; `adim-17-10.png`: mor sinyal yolları, etiket 1–8, kesiğin dışında ayrı bir
  çizgi görmedim (yer ölçümü P108d § 2'de, kareden ölçülmedi); `adim-17-05.png`: turuncu bara çıkışları, etiket 1–4; `adim-32-04.png`:
  U06 direk boyunca, etiket 1.

PDF metni (pypdf): s. 13 B5a "acil stop düğüm kartı (röle K1 …)", s. 22 yol 11 / 12 "(çizimdeki yol da, P10.8d)", s. 26 17.10
"… 11 ve 12 de kesikten geçer" ve 17.11 "taban bölümüdür", s. 48 32.1 "Kare tabana arkadan ve üstten bakar …". Kalan "modelde yok"
geçişleri bu paketin kartları değil (K52 a regülatörü, kafa giriş kartı vb.).

Eski kirli dosyalar: `md5sum -c planlama/d158/P108e-olcum/kir-bas.md5` → 20 / 20 aynı (üretim hiçbirini yeniden yazmadı).

## 9. Zincir 2–10 ve iki düzeltme

**Tur 1** (`bash planlama/d158/P108e-zincir.sh`, 08:06:52–09:03:43, loglar ve `zincir.durum` `P108e-olcum/zincir-tur1/`; uç etiketi yeniden ölçümü `zincir-tur1/uc-1.json`;
sonuçları aşağıdaki tabloda):

| # | Komut | Çıkış | Sonuç |
| --- | --- | --- | --- |
| 0a | `carpisma_kos.py kontrol` | 0 | izlenen 17 dosya kayıtla aynı |
| t1 / t2 | `kupon_tazelik.py` / `--bozma-denemesi` | 0 / 0 | TAZE (16) / 4 / 4 |
| 2a | `rehber_kablo.py --veri …` | 0 | GEÇER |
| 2b | `rehber_kablo.py --bozma-denemesi --veri …` | 0 | 136 / 136 (P10.8c 132 + 4 yeni) |
| 2c | `rehber_denetim.py --kaynak` | 0 | ascii 0, onay farkı 0 (219 / 258 / 1201) |
| 3 | `rehber_denetim.py` | 0 | ASCII 0, zorunlu eksik 0 / 165, yasak 0, standart 0, elektrik 0; parça 1264, şema 65 |
| 4 | `F10f-dogrula.py` | 0 | GECTI (586 s) |
| 5 | `F10e-dogrula.py --goruntu-yok` | 0 | GECTI (1.018 s); `renk_demo` KALDI (bilinen karar) |
| 6 | `F10d-dogrula.py --goruntu-yok` | **2** | **KALDI** (1.026 s): uç etiketi hata 4 (aşağıda) |
| 6g | `F10d-dogrula.py --gizli …` | 0 | bilgi: 103 / 116 parçanın alt adım karesinde pikseli var |
| 7 | `F10a-dogrula.py --kanit-yok` | 0 | GECTI (596 s) |
| 8 | `F9b-dogrula.py` | **1** | **GECMEZ (109 hata)** (aşağıda) |
| 9 | `carpisma_kos.py kontrol` | 0 | kayıtla aynı |
| 10 | `regresyon.py --yazma` | 0 | GEÇER, kötüleşen yok |

**F10d uç etiketi (4 hata), nedeni kartın artık modelde olması:**
- 32.2 (kafa servo uzatmaları): "Dağıtım kartı C (kafa)" uç etiketi oldu, ama kart güç panelinde, kadraj kafada: sahne ve etkileşimli
  kipte "güvenli alanın dışında" (U1 × 2), görünür piksel 0 (U4). Çözüm: `rehber_metin.UC_ORTULU[("K2", 2)]` "Dağıtım kartı C (kafa)" =
  "bu kadrajın dışında" (aynı alt adımda "kafa tilt servosu" emsali). Basılı sayfa "Uç karede görünmez: … (bu kadrajın dışında)" der.
- B5a (adım 12) etkileşimli kip (1.000 × 796 tuval): etiket 2 "yer bulunamadı (çakışma)". Kart güvenli alanın sağ kenarına 31 px
  (nokta x 770, alan x1 801), çevresi bağlantı elemanı işaretleriyle dolu; ad kutusu en çok 8,5 R uzakta aranıyordu. Çözüm: `app.js`
  `ucCiz` arama uzaklıklarına 11 R ve 14 R eklendi; yalnız yakında yer bulamayan etiket için denenir. Sınama (`F10d-dogrula.py
  --yalniz-uc … --rehber <geçici kopya>`, önce / sonra JSON karşılaştırması): 23 konum × 2 kipte değişen tek etiket B5a etkileşimli
  etiket 2 (nokta (770; 307) → kutu (770; 167), 140 px, çizgiyle); yazdırma karesi kipinde hiçbir etiket yer değiştirmedi.
  Yazdırma karesinde (sahne, 1.200 × 720) bu etiket zaten çiziliyordu.

**F9b (109 hata):** 99'u P10.8d'nin montaj değişikliği (parça 1.225 → 1.251, kütle 25.835,06 → 25.876,13 g, AM y, satın alma /
bağlantı sayıları, taban modülü, tarama kütlesi): `tasarim/Robot-Tasarim-Demosu.html` P10.8d'den sonra yeniden üretilmemiş (P10.8d
kapanışında F9b koşulmamış). 10'u bu paketin: GLB düğümü 1.238 → 1.264. Çözüm, P10.8c'deki gibi: `py -3 -B -X utf8
tasarim/cad/demo_uret.py` (yalnız demo sayfasını yazar; sayılar kaynak JSON'lardan).

**Kaynak değişikliklerinden sonra** (09:05): `rehber_denetim.py --kaynak` 0 (ascii 0, onay farkı 0), `rehber_kablo.py` 0,
`F10l-birlesim.py` GEÇER, `node --check rehber/app.js` tamam. UC_ORTULU ve app.js onay kaydında değil (fark 0).

**İkinci üretim** `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (FreeCAD'siz; GLB ve parça verisi ilk üretimden):
09:04:40–09:46:49, 2.529 s, çıkış 0, Traceback 0, "ek kontrol sorunlu: -" (log `P108e-olcum/uretim2.log`, `uretim2.durum`). Uç etiketi
60 → 59 (32.2'de kart C "uc_yok": "bu kadrajın dışında"); alt adım 91 / 91; PDF 90 sayfa; ASCII 0, zorunlu eksik 0 / 165, yasak 0,
standart 0, elektrik 0; sıra / giriş / uçuş 0 / 0 / 0; tarayıcı 50 / 50, konsol 0. `adim-32-02.png` bakıldı: etiket 1 kafa pan servosu,
kart C etiketi yok. Eski kirli dosyalar yine 20 / 20 aynı (`b2-tarama.nabiz` değişme zamanı 06:29, paketten önce).
Sonra `py -3 -B -X utf8 tasarim/cad/demo_uret.py`: çıkış 0, "1264 dugum, sayi anahtari 127"; demo farkı yalnız 13 gömülü sayı
(yukarıdaki F9b anahtarları) ve gömülü kaynak blokunda aynı değerler (7 satır).

**Tur 2** (`bash planlama/d158/P108e-zincir.sh`, 09:47:01–10:41:33, loglar `P108e-olcum/zincir/`, `zincir.durum`): **15 adımın 15'i
çıkış 0.**

| # | Sonuç |
| --- | --- |
| 0a / 9 | kayıtla aynı |
| t1 / t2 | TAZE (16) / 4 / 4 |
| 2a / 2b | GEÇER / 136 / 136 |
| 2c / 3 | ascii 0, onay farkı 0 / ASCII 0, zorunlu eksik 0 / 165, yasak 0, kopya eki 0 |
| 4 F10f | GECTI (586 s) |
| 5 F10e | GECTI (1.014 s); `renk_demo` KALDI (bilinen karar) |
| 6 F10d | **GECTI** (1.021 s); uç etiketi 23 konum, 59 etiket, hata 0 |
| 6g | 103 / 116 (bilgi; tur 1 ile aynı) |
| 7 F10a | GECTI (467 s) |
| 8 F9b | **GECER (hata 0)** |
| 10 | regresyon GEÇER, kötüleşen yok |

## 10. Kontrol ve kapanış tarifi (B için)

Depo kökünden, `export PYTHONIOENCODING=utf-8`; Python komutları `py -3 -B -X utf8 …`. Uzun adımlar (üretim, F10e / F10d / F10f / F10a)
Bash arka planında `.durum` kalıbıyla. A'nın sonuçları § 7, § 8, § 9; aşağıdaki "beklenen" sütunu onlardan.

**Bağımsız kontrolde özellikle bakılacaklar**
1. `rehber_kritik_onay.json` 25 farkı (§ 7; `git diff tasarim/freecad/rehber/rehber_kritik_onay.json`): her eski → yeni metnin doğru olduğu.
2. `GEO_YAN_ELLE` iki kaydının gerekçesi (`rehber_kablo.py` `_YOL6_KART_C`) ve CAD paketine devir notu (§ 3).
3. G07 / G16 yeni noktaları (§ 4): B-rep ölçüsü `P108e-olcum/sema-sonra.json`; şema boyu 281 → 267, 160 → 165 mm (`kablolar.json`).
4. `sema_on` (§ 5): `rehber_veri.py` kuralları ve `app.js` çizimi; kare `rehber/goruntu/adim-17-11.png`.
5. 32.1 karesi `rehber/goruntu/adim-32-01.png` ve `UC_ORTULU[("K2", 1)]`.
6. `uygulama_metin.py` koşulu (§ 6) ve `uygulama-notu.md` sayıları (`uygulama-ivme.json`, `montaj-analiz.json` ile).
7. B5a yeni cümleleri (§ 3): burç / vida ölçüleri TAHMİN diye yazılı mı; kart yerleri `taban-analiz.json` ile.
8. § 9'daki iki düzeltme: `UC_ORTULU[("K2", 2)]` ve `app.js` `ucCiz` 11 R / 14 R (B5a etkileşimli kipte etiket 2 çizgiyle 140 px
   yukarıda; yeri gözle değerlendirilmedi, yalnız F10d U1–U4 kuralları geçti).
9. `tasarim/Robot-Tasarim-Demosu.html` farkı yalnız sayılar mı (`git diff --word-diff`).

**Komut zinciri ve beklenen değerler**

| # | Komut | Beklenen (A'nın sonucu) |
| --- | --- | --- |
| 0a | `(cd tasarim/freecad && py -3 -B -X utf8 carpisma_kos.py kontrol)` | 0; izlenen 17 dosya kayıtla aynı |
| 0b | `tasarim/freecad/rehber/rehber_denetim.py --bozma-denemesi` | 0; 347 / 347 |
| 0c | `tasarim/freecad/rehber/rehber_kablo.py` / `--bozma-denemesi` | 0 / 0; GEÇER; 118 / 118 |
| 0d | `planlama/adim3/kablolar_denetim.py` / `--bozma-denemesi` | 0 / 0; GEÇER; 174 |
| 0e | `planlama/d158/F10l-birlesim.py` | 0; GEÇER; eklenen 13 / silinen 11 (taban `269e51b`) |
| 0f | `tasarim/freecad/test/kupon_tazelik.py` / `--bozma-denemesi` | 0 / 0; TAZE (16) / 4 / 4 |
| 0g | `planlama/d158/F4c-dogrula.py` | 0; GEÇTİ |
| 0h | `tasarim/freecad/lale158/kafa-yerlesim/uygulama_rapor.py` (isteğe bağlı) | 0; "izgara 1.523"; `git diff` notta yeni fark yok |
| 1 | `py -3 -X utf8 tasarim/freecad/rehber/rehber_uret.py --veri-yok` (isteğe bağlı; A koştu, § 9; tam üretim FreeCAD kilidiyle § 8) | 0; ≈ 42 dk; uç etiketi 59; "ek kontrol sorunlu: -"; PDF 90 sayfa |
| 1b | `tasarim/cad/demo_uret.py` (1'den sonra; 1 koşulmadıysa da çıktı aynı kalmalı) | 0; "1264 dugum"; `git diff` demoda yeni fark yok |
| 2a | `rehber_kablo.py --veri rehber/veri/rehber-veri.json` | 0; GEÇER |
| 2b | `rehber_kablo.py --bozma-denemesi --veri rehber/veri/rehber-veri.json` | 0; 136 / 136 |
| 2c | `rehber_denetim.py --kaynak` | 0; ascii 0; onay farkı 0 (219 / 258 / 1201) |
| 3 | `rehber_denetim.py` | 0; ASCII 0, zorunlu eksik 0 / 165, yasak 0, standart 0, elektrik 0; parça 1264 |
| 4 | `planlama/d158/F10f-dogrula.py` | 0; GECTI (≈ 590 s) |
| 5 | `planlama/d158/F10e-dogrula.py --goruntu-yok` | 0; GECTI (≈ 1.020 s); `renk_demo` KALDI (bilinen karar) |
| 6 | `planlama/d158/F10d-dogrula.py --goruntu-yok` | 0; GECTI (≈ 1.020 s); uç etiketi 59, hata 0 |
| 6g | `planlama/d158/F10d-dogrula.py --gizli planlama/rehber/kontrol.json` | 0; bilgi, 103 / 116 |
| 7 | `planlama/d158/F10a-dogrula.py --kanit-yok` | 0; GECTI (≈ 470 s) |
| 8 | `planlama/d158/F9b-dogrula.py` | 0; GECER (hata 0) |
| 9 | `carpisma_kos.py kontrol` (0a gibi) | 0; kayıtla aynı |
| 10 | `planlama/d158/regresyon.py --yazma` | 0; GEÇER, kötüleşen yok |

A'nın zinciri tek betikte: `bash planlama/d158/P108e-zincir.sh [adım …]` (adımlar 0a t1 t2 2a 2b 2c 3 4 5 6 6g 7 8 9 10; loglar
`P108e-olcum/zincir/`, ilerleme `P108e-olcum/zincir.durum`; ≈ 55 dk). 0b–0h, 1 ve 1b betikte yok (A ayrı koştu, § 7, § 8, § 9).
**Denenmemiş:** 0h'nin üçüncü koşusu (A iki kez koştu, ikincisi metin düzeltmesinden sonra; "yeni fark yok" denenmedi); 1b'nin
ikinci koşusu (demoda yeni fark yok beklentisi denenmedi); `P108e-zincir.sh`'nin argümanlı çağrısı (yalnız argümansız koşuldu).

**`git add` listesi**
```
git add planlama/adim3/kablolar.json planlama/adim3/kablolar.md \
  planlama/d158/F10l-birlesim.py planlama/dongu-158.md \
  planlama/d158/P108e-gunluk.md planlama/d158/P108e-onizleme.py planlama/d158/P108e-sema-girdi.py \
  planlama/d158/P108e-sema-olcum.py planlama/d158/P108e-zincir.sh planlama/d158/P108e-olcum \
  planlama/d158/F10a-dogrula.json planlama/d158/F10d-dogrula.json planlama/d158/F10e-dogrula.json planlama/d158/F10f-dogrula.json \
  planlama/rehber rehber/app.js rehber/veri rehber/goruntu \
  tasarim/Robot-Tasarim-Demosu.html tasarim/freecad/lale158/kablo_yolu_taban.py \
  tasarim/freecad/lale158/kafa-yerlesim/rapor.html tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md \
  tasarim/freecad/lale158/kafa-yerlesim/uygulama_metin.py \
  tasarim/freecad/rehber/rehber_denetim.py tasarim/freecad/rehber/rehber_gorunum.py tasarim/freecad/rehber/rehber_kablo.py \
  tasarim/freecad/rehber/rehber_kritik_onay.json tasarim/freecad/rehber/rehber_metin.py tasarim/freecad/rehber/rehber_veri.py
```
F10 JSON'larından zincir değiştirmeyen olursa `git add` onu sessizce atlar. Eklemeden önce `git status --short` ile listede
olmayan bir değişiklik kalmadığına bak (aşağıdaki dışarıda kalanlar hariç).

**Dışarıda kalanlar (eklenmez, dokunulmaz):** `tasarim/freecad/kabuk/gorsel/` 13 PNG, `tasarim/freecad/montaj/yerlesim-kontrol.json`,
kökteki `geometri_cikar.py`, `geometri2_cikar.py`, `geometri2_dogrula.py`, `gez.js`, `uc.js`, `planlama/d158/P108d-olcum/ara1.json`,
`planlama/d158/P108d-kontrol-olcum/b2-tarama.nabiz`, `planlama/d158/FREECAD-KILIT.txt` (izlenmiyor; şu an "boş").

**Commit mesajı önerisi**
```
Lale P10.8e: rehber açıkları: acil stop düğüm kartı ve dağıtım kartı C rehberde modelde (SV3 şema hatası, GEO_YAN_ELLE), G07 / G16 şeması katı dışında, 17.11 U06 taban bölümü (sema_on), 32.1 taban bakışı, kafa-yerleşim notu 1,523; rehber yeniden üretildi (1.264 parça)
```

**Commit mesajına ek** (yukarıdaki öneriye): "; demo sayfası P10.8d montajı ve 1.264 düğümle yeniden üretildi (F9b 0)".

## 11. Durum ve devredilenler

| Madde | Durum | Önce → sonra |
| --- | --- | --- |
| 1 SV3 / kart C | yapıldı (rehberde) | `rehber_kablo.py` 1 hata → 0; uç etiketi 49 / 8 → 51 / 6 modelde / modelsiz |
| 2 ASCII kalıntı | yapıldı | 5 → 0 |
| 3 kareler 32.1, 17.11 | yapıldı | 17.11 U06 çizgisi yok → taban bölümü çiziliyor; 32.1 bütün robot → taban bakışı |
| 4 G07 / G16 | yapıldı (yalnız şema kaynağı) | katı içinden geçen ara 4 + 1 → 0; en dar ara 4,0 / 5,5 mm; boy 281 / 160 → 267 / 165 mm |
| 5 uygulama raporu | yapıldı | 1,519 → 1,523; parça 1.225 → 1.251; eskimiş iki cümle kalktı |
| 6 rehber üretimi | yapıldı | 1.238 → 1.264 parça; iki üretim çıkış 0; zincir tur 2 15 / 15 çıkış 0 |

**CAD paketine devir (geometri, yapılmadı):** CAD kablo yolu 6 (`taban_parcalar.py` YOL[5]) kart C'ye inmiyor (taban ucu (0; 1215; −26),
kart z −92…−62); `GEO_YAN_ELLE` iki kaydı bunu "elle bakıldı" diye taşıyor (§ 3).

**Doğrulanmayanlar:** kart zarfları ve burç / vida ölçüleri TAHMİN (P10.8d'den); B5a etkileşimli kipteki uzak etiketin (dağıtım
kartı C, 140 px çizgi) görünüşü gözle değerlendirilmedi; 17.10 karesinde yol 11 / 12'nin kesikten geçtiği kareden ölçülmedi (yer ölçümü
P108d § 2); acil stop düğüm kartı B5a karesinde etiketsiz, kareden ayırt edilmedi.

## 12. B: bağımsız kontrol ve kapanış (21.11 ≈ 10:44–11:00)

Kontrol raporu `planlama/d158/P108e-kontrol.md`: **GEÇER**. Özet:
- Muafiyetler (iki `UC_ORTULU`, iki `GEO_YAN_ELLE`, `app.js` 11 R / 14 R) karelere / `taban-analiz.json`'a bakılarak doğrulandı, kapsamları
  dar; B'nin F10d `--yalniz-uc` koşusu (hata 0) A'nın değişiklik öncesi `zincir-tur1/uc-1.json`'u ile 23 konum × 2 kipte karşılaştırıldı:
  fark yalnız B5a etkileşimli etiket 2 (140 px) ve 32.2'nin numarası.
- CAD: FCStd / STEP ve parça / montaj kaynağı değişmedi, `carpisma_kos.py kontrol` 0; şema ölçüm girdisi kaynakla aynı (16 / 16).
- Zincir tur 2 geçerli (09:47'den sonra kaynak / çıktı değişmedi); B'nin 17 hızlı denetimi A'nın değerlerini verdi; md5 önce / sonra aynı.
- § 11'deki üç "doğrulanmayan" kareye B baktı: B5a etkileşimli etiket okunur (CDP çerçevesinde 140 px çizgiyle, statik ekranda kartın
  yanında); düğüm kartı karede görünüyor ama etiketsiz (röle ile ön şarj kartı arasındaki küçük yeşil kart); 17.10'da kesik kareden
  seçilmiyor, dayanak P10.8d ölçümü.
- Gizlilik taraması (eklenen satırlar + yeni dosyalar, PNG parçaları, PDF üstverisi): makine yolu, anahtar, e-posta, telefon bulunmadı;
  yol düzeltmesi gerekmedi. Eklenen satırlardaki tek kişi adı kafa-yerleşim notunun HEAD'de de olan "Seçim:" satırında.
- Commit "Lale P10.8e" (açık liste, `--pathspec-from-file`), `lale-duzeltme`'ye push; eski 21 kir dışarıda. Commit kimliği ve push sonucu
  `planlama/dongu-158.md` § 5'te değil, B'nin raporunda (commit kendi kimliğini taşıyamaz).
