# F4a günlüğü: belgeler 1,58 m (P4.1, P4.2, P4.4)

09.11.2026 · ajan A (belgeler) · brief `planlama/d158/F4a-brief.md`. FreeCAD kullanılmadı; commit yok.

Kısaltmalar (kaynak dosyalar):

| Kısa | Dosya |
|---|---|
| LK | `tasarim/freecad/lale158/lale158-kontrol.json` (`kablo_ozet.kablo`, `toplam_boy_mm`, `parca`) |
| MA | `tasarim/freecad/montaj/montaj-analiz.json` |
| UI | `tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json` (`ev`, `izgara_yuk_0g.a_sinir_pay15`) |
| KY | `tasarim/freecad/lale158/kafa-yerlesim/` (`uygulama-notu.md`, `secenekler.md`) |
| KA | `tasarim/freecad/kafa/kafa-analiz.json` |
| TA | `tasarim/freecad/taban/taban-analiz.json` |
| BOM | `tasarim/freecad/montaj/robot-bom.csv` |
| RG | `tasarim/freecad/lale158/lale158-regresyon.json` |
| ES | `kod/ortak/eklem_sinirlari.json` (yalnız okundu) |
| KK | `planlama/d158/kablo-kurali-notu.md` |
| KQ | `planlama/d158/karar-kuyrugu.md` (yalnız okundu) |

Bütün dosyaların değişiklik öncesi kopyası ve sayfa öykünmesi bu oturumun geçici klasöründe; depoda yedek dosya yok.

## 1. Değişen dosyalar

### `planlama/adim3/elektrik.md` (P4.1)

- 158 bölüm başlığı: "04.11.2026; 09.11.2026 F4a: 05.11 B + R1 yerleşimine göre". 09.11 kaynak paragrafı (KY) ve "CAD durumu (09.11)" paragrafı eklendi. Paragraf BOM satırlarını veriyor ve iki şeyi not ediyor: LM2577 + LM2596 modelde yok; I2S amfi 0 parça (KY `uygulama-notu.md:57`).
- Değişiklik tablosu:
  - Amfi satırı: MAX98357A [tarihçe]; PAM8403 kafa sol duvarında. PAM 5 V noktası "karar bekliyor (K10)", tepe 0,71 A (KQ K10).
  - USB satırı: 5 bilinen cihaz ve gövdedeki hub; "6. cihaz bekliyor (K1, pano #5)".
  - Boyun demeti 5 kablo: kafa 12 V, tilt servo, göğüs HDMI, hub uzatması, hoparlör. Satırda "karar bekliyor (K14, pano #6)" yazıyor (KK:34-35, `kablo_yolu_ekran.py:31,116,197`).
  - ESP32 USB: Hub → ESP32, yol 971 mm, önerilen boy 1.360 mm (LK).
  - Yeni satır: akü 2.800 → 3,0 kg (BOM), ev pozu 26.115,6 g (UI `ev.kutle_g`), rampa payı 1,519 (UI `rampa5_geri`).
- Kafa güç şemasına PAM satırı ve K10 notu eklendi. Göğüs ekranı dal bloğu:
  - K11 karar bekliyor;
  - 3 adet 90° fiş gerektiği notu (F1b);
  - boylar LK'den: HDMI 757/950, USB dokunmatik 395/640, 12 V 1.376/1.720 mm (eski 1.060 mm USB tarihçe);
  - port ucu temas hacmi 897,1 / 391,5 / 617,3 mm³ (`dongu-158.md` P1.4).
- Yeni USB port tablosu:
  - Pi1 ReSpeaker, Pi2 ses kartı, Pi3 hub, Pi4 kafa ekranı dokunmatiği;
  - Hub1 göğüs dokunmatiği, Hub2 ESP32, Hub3 ve Hub4 boş (KY `uygulama-notu.md:58` "2 port boş").
- Tabloya üç madde eklendi: K1 bekliyor; hub düşerse ESP32 ve göğüs dokunmatiği birlikte düşer (KK:54-55); `maliyet.json`'daki aday kalemlere işaret.
- 1,65 m bölümü başlığı "[tarihçe]" ve 09.11 tarihçe notu; tablo başlığı "1,65 m (29.10; 1,58 m'de değişmeyenler geçerli)".
- E4 "boyundan" yeniden yazıldı. 125 cm amfi satırı "[ESKİ, 125 cm kafası]" oldu. Boyun kablo listesi güncellendi: doluluk %39,9 / %44,8 / %34,3 (LK).
- Blok şema satırlarında K10, K1, K14 ve K11 işaretleri var. Akım bütçesinin kafa satırına K10 tepe notu, sigorta tablosunun göğüs satırına K11 eklendi.
- Açık işler 2, 15, 16 ve 17 güncellendi.

### `planlama/maliyet.json` (P4.2)

- `notlar[0]`: "V3 satırları 29 Ekim 2026 listesidir (o günkü ana tasarım 1,65 m); ana tasarım artık 1,58 m."
- `notlar`'a yeni not: `secenek "fiyat_bekliyor"` olan kalemler hiçbir toplama girmez.
- `notlar` "Göğüs ekranı yok (1,65 m…)" notu "Tarihçe: …; 1,58 m'de 11,6" göğüs ekranı var; bu listeye P8.1'de girecek" oldu.
- MAX98357A kalemi: `"ver": "v1,v2"` ve tarihçe notu. V3 görünümünden çıktı.
- Fiyatsız 2 karar kalemi eklendi: PAM8403 ses amfisi ve USB ses kartı (04.11 kararı; KQ K16). Bunlar `tl: null`, `durum "dogrulanmadi"`, `secenek "fiyat_bekliyor"`, `adim "F4a"`.
- Fiyatsız 9 kablo / fiş adayı eklendi:
  - `kosullu "K4"` (6 kalem): USB-A uzatma ~30 cm (ses kartı uzatması, yol 217 / boy 270 mm), USB-A uzatma ~1 m (hub uzatması 617 / 920), L USB-A dirsek, kısa micro USB (dizi 85 / 110), hoparlör kablosu ~1,1 m (824 / 1.030), L 3,5 mm kısa kablo (36 / 40). Boylar LK'den.
  - `kosullu "F1b"` (3 kalem): 90° HDMI, 90° micro USB, 90° DC jak 12 V (F1b B önerisi). HDMI 90° adaptörün v4'te olup olmadığı kontrol edilmedi; `tubitak-2209b/` açılmadı.
- Fiyat yazılmadı: satıcı sayfası bu pakette doğrulanmadı. `raporlar/kaynaklar/06-onayli-satici-B.md`'deki 01.11 PAM8403 fiyatı (21,86 TL) izlenmeyen dosyada; P8.1'de doğrulanınca girer.

**Toplamlar** (`py -3 planlama/adim5/maliyet_toplam.py`, çıkış 0; JSON geçerli, 130 kalem, 11 not):

| | Önce | Sonra |
|---|---|---|
| V3 görünen kalem | 99 | 98 |
| Ara toplam | 90.232,68 | 89.495,40 |
| **Genel** (%15 pay) | **103.767,58** | **102.919,71** (−847,87 = MAX98357A 737,28 × 1,15) |
| Koşullular dahil ara | 94.831,86 | 94.094,58 |
| **Koşullular dahil genel** | **109.056,64** | **108.208,77** |
| Koşullu grup | 4.599,18 | 4.599,18 (yeni adaylar fiyatsız, toplama girmez) |

**Sayfa öykünmesi** (`viewer-template.html` `on()`/`calc()` mantığı, DOM'suz; demo sayfası açılmadı, `demo_uret.py` koşmadı):
- V1 ve V2 sekiz durumda aynı.
- NaN yok; fiyatsız kalem görünmüyor.
- V3, yazıcı ile, elde kalemler düşülmüş: 78.871,83 → 78.023,96. V3, hizmet ile: 109.180,53 → 108.332,66.

Neden `secenek "fiyat_bekliyor"`: `maliyet_toplam.py` saydığı bir kalemde `tl` null görürse çöküyor. Sayfa da `secenek`'i baskı modundan farklı olan kalemi gizliyor. Bu değer ikisinde de kalemi dışarıda bırakıyor; `kosullu` alanı K4 / F1b bağını taşıyor.

### `README.md` (P4.4)

- Belge tablosu:
  - "Güncel tasarım (1,58 m)";
  - yeni satır `dongu-158.md` / `d158`;
  - `dongu.md` satırı tarihçe oldu;
  - baskı listesi satırı: 65 parça;
  - demo satırı: "29.10 listesi; 1,58 m listesi P8.1'de".
- "Güncel tasarım" bölümü 1,58 m tablosuyla değişti:
  - boy 1.580,0 mm, 1.179 parça (LK);
  - modül parça ve kütleleri (MA);
  - ev pozu 26.115,6 g, rampa 1,519, düz arka 2,097 (UI);
  - devrilme 3,66 / 3,28 / 4,05 m/s² (TA);
  - tilt 3,64, pan 2,21, kafa grubu 1.570,8 g (KA);
  - mikrofon–hoparlör 574,3 mm (KY);
  - eklem sınırları (ES);
  - maliyet ≈ 102.900 / ≈ 108.200 / elde ≈ 78.000 (bu paketin toplamları).
- Tarihçe paragrafı eklendi. Eski Eylül–Ekim tablolarının ve "Açık işler"in o tarihe ait olduğu notu yazıldı. Yeniden yazılan eski satırdaki takma ad geçişi gitti (−1).

### `tasarim/freecad/README.md` (P4.4)

- Satır 7: "Aşağıdaki modül bölümlerindeki 125 cm / 1,65 m sayıları eski". Yeni "Güncel sayılar (09.11.2026)" bloğu eklendi (LK, MA).
- 1,65 m paragrafı "Tarihçe — 1,65 m … o tarihte ana tasarım 1,65 m idi" oldu.
- Kabuk satırına 11,6" göğüs ekranı eklendi. Omuz orijini (0, 1270, 0) MA'dan.

### `tasarim/freecad/OZET.md` (P4.4)

- Başa 1,58 m özeti eklendi:
  - modül tablosu (MA, BOM);
  - devrilme, motor ve akü (TA);
  - çakışma (LK, RG);
  - eklem sınırları (ES);
  - açık kararlar (KQ).
- Eski 9 Ekim 125 cm metni "# Tarihçe: 9 Ekim 2026 özeti (125 cm, FreeCAD V3)" altında kaldı; başlıklarına "(125 cm)" / "(9 Ekim 2026)" eklendi.

### `planlama/proje-plani.md` (P4.4; yalnız başlık satırları 5–11)

- Parça 1.177 → 1.179 (LK).
- Kütle 25.910,6 → 26.115,6 g (UI).
- Akü 3,0 kg (BOM), rampa 1,519 (UI) eklendi.
- Maliyet "1,65 m sayılarıyla … ≈ 103.800" → "29.10 listesi … ≈ 102.900" (bu paket).

### `Lale-Proje-Ozeti.txt` (P4.4)

- Başlık: 09.11 notu, kaynaklar, Kn anlamı.
- Bölüm 2 1,58 m'ye göre yeniden yazıldı (LK, MA, UI, TA, KA).
- Bölüm 3 (parça, güç, maliyet): MAX98357A çıktı, K16 notu girdi.
- 4.1 mimari:
  - yüz 7" LCD → 10,1" QLED (HDMI 0);
  - göğüs Nextion (UART2) satırı → 11,6" HDMI 1 + USB dokunmatik (arayüz kararı yok, KK);
  - ses çıkışı USB ses kartı → PAM8403;
  - seri: Pi port 3 → hub (gövde) → ESP32.
- 4.4 eklem sınırları:
  - tilt −25…30 → −13…13 (ES, karar 29.10);
  - "S1 ≥ 120° iken S2 ≤ 117°" eklendi;
  - kafa-kol yasak kutusu "şu an yok, tam taramada yeniden" (125 cm kutusu ±13 tilt aralığının dışında).
- 4.5 sürüş: "ivme ≤ 0,5, rampada ≤ 0,25" → düz 0,5, fren 1,8, rampada 0,1 ve kollar ev pozunda (ES `teker`, karar 29.10).
- 4.6 güç zinciri (`elektrik.md`):
  - F1'e XL4016 C (pan + tilt, 5 A) eklendi; A ve B yalnız kollar;
  - F3: Pololu D24V50F5 (PAM K10) + SY8205 → QLED;
  - F4'ten Nextion çıktı;
  - mini 2 A → göğüs ekranı (K11);
  - devreye alma "Nextion düğmesi" → "Pi 'arm'; telefon kumandası".
- 5 takvim:
  - P9.1 sipariş gününe göre özeti: Kapı 1 S+2→S+3, Kapı 2 S+6→S+7, Kapı 3 S+7→S+8 (`proje-plani.md:85-99`);
  - 15 Ekim takvimi [Tarihçe] işaretli kaldı.
- 6 durum (17 Ekim → 09.11, `dongu-158.md` durum sütunları):
  - F0, F1 (P1.4 yalnız girinti varsayımıyla 0), F5, P8.3, P8.4 ve P9.1 tamam;
  - F2, F3a ve F4a sürüyor;
  - P6, P7 ve P8.1 bekliyor;
  - sipariş yok;
  - açık kararlar K1, K4, K10, K11, K14, K3/K9.
- Riskler:
  - Rampa motoru "%90" → a 0,5 ile 6,86 kg·cm = sürekli 6,3'ün 1,09 katı; a 0,25 ile 0,92, duruşta 0,76 (TA `motor.rampa5*`).
  - Kafa ısısı "34–46 °C" → ~49 °C; en kötü durum hesaplanmadı (`elektrik.md:35`).

## 2. 1,65 m kalıntı kontrolü

Komut: `git grep -n -e "1,65 m" -e "1.65 m" -e "165 cm"` (09.11, düzenlemeler sonrası). Dokunulan dosyalarda kalan geçişler:

| Dosya | Geçiş | Tür |
|---|---|---|
| `elektrik.md` | :23, 24, 26, 27, 29, 33, 34, 38, 39 | "Önce" sütunu (125 cm / 1,65 m eski değer); 1,58 m değeri yanındaki sütunda |
| `elektrik.md` | :95, 97, 99, 103, 113 | [tarihçe] işaretli 1,65 m bölümü |
| `elektrik.md` | :214, 458, 515 | 125 cm gövde metni içinde "1,65 m'de …" tarih bilgisi; :515 "1,83 sa kabulü 1,65 m yükleri içindi" |
| `maliyet.json` | :20, 21 | Tarihçe notları ("o günkü ana tasarım 1,65 m") |
| `maliyet.json` | :38, 41, 48, 53, 69, 117, 135, 140, 167 | 29.10 listesi kalem notlarının kaynak bilgisi (Y2b) |
| `README.md` | :14, 50, 53, 54 | Tarihçe / "29.10 listesi (o günkü 1,65 m tasarımı)" |
| `proje-plani.md` | :10, 11, 183, 226 | Aynı tür; :183 tarihçe bölümü; :226 "karar 29.10 (1,65 m'de alındı, 1,58 m'de sürüyor)" |
| `freecad/README.md` | :7, 15 | "modül bölümlerindeki … 1,65 m sayıları eski"; tarihçe |
| `Lale-Proje-Ozeti.txt` | :35, 104, 217 | Tarihçe; maliyet listesinin tarihi; rehberin 1,65 m'den kalma olduğu |

Sonuç: dokunulan dosyalarda "1,65 m" ana tasarım anlamında yalnız tarihçe ve "o günkü" bağlamında kalıyor. Depo genelinde "1,65 m ana tasarım" ifadesi şu yerlerde geçiyor: Y2a/Y2b günlük ve betikleri, `S1-kaset.md:194` (Y2a başlığı) ve `yazilim-notu-stowent-170.md:3` (29 Ekim güncellemesi). Hepsi tarihçe ya da günlük. Kapsam dışında kalan geçişler aşağıda, §4'te.

## 3. Brief ile kaynak arasındaki farklar (kaynağa göre yazıldı)

1. **Hub yeri.** Brief'in 8. satırı "kafa arka kabuk yan duvarı, K5 kapandı" diyor. K5'in kendi kapanış kaydı (KQ K5) ve KY `uygulama-notu.md:58` başka bir şey söylüyor: hub **gövdede**, üst arka göğüs servis kapağının içinde (y 1.085–1.157, `arayuz.py` SES_USB.hub). Ses kartı ve PAM kafanın sol duvarında. Belgelere gövde yazıldı.
2. **Boyun demeti.** Brief "göğüs HDMI + USB dokunmatik + 12 V" diyor. KK:34-35 ve `kablo_yolu_ekran.py:31,116,197` boyundan 5 kablo geçtiğini gösteriyor: kafa 12 V, tilt servo, göğüs HDMI, hub uzatması, hoparlör. Göğüs USB dokunmatiği ve ESP32 USB'si gövdedeki hub'dan çıkıyor, boyundan geçmiyor. Göğüs 12 V'u tabandan geliyor, boyundan geçmiyor. `dongu-158.md:100`'deki P4.1 tanımı da eski ifadeyi taşıyor.
3. **KY `uygulama-notu.md:115`** göğüs 12 V'u için "Taban → göğüs ekranı (boyundan)" diyor. Bu, `kablo_yolu_ekran.py` ile çelişiyor. Dosya F1 / KY'nin; dokunulmadı.

## 4. Kapsam dışında kalan eski içerik (dokunulmadı, sahibi belirtildi)

- **`planlama/y2/Y2b-*.json`** elle düzenlenmedi; P6.1 yeniden üretir.
  - `Y2b-aku.json`: 1,65 m yükleri. `kalemler` 10,1" (B) ekranı Pi USB'den besliyor; göğüs ekranı, QLED ve SY8205 yok. `senaryo`, `sure_sa`, `victron_fan_ile_sa` ve `gereksinim_2sa` eski. `gereksinim_2sa.kaynak` alanında takma ad var (P4.5).
  - `Y2b-baski.json`: 1,65 m baskı listesi (65 parça, 7.627–7.684 g, 158,7–159,9 sa).
  - `Y2b-ivme.json`: güncel (F1b yeniden üretti).
- `tasarim/freecad/README.md` modül bölümleri (~:150, ~:156) hâlâ Nextion ve 125 cm anlatıyor. Satır 7'deki not bunların eski olduğunu söylüyor; içerik P6 / P7'de yenilenmeli.
- `proje-plani.md:44`: kritik yolda XVF3800 geçiyor. Başlık dışı; bu pakette dokunulmadı (güncel mikrofon ReSpeaker Mic Array v2.0).
- `elektrik.md` 125 cm gövde bölümleri [ESKİ] işaretli yerler dışında 125 cm anlatıyor; 04.11 kuralıyla aynı.
- `elektrik.md` akü süresi ~3,8–4,4 sa (normal) ile TA'nın 16,8 / 36,6 / 85,2 W → 12,2 / 5,6 / 2,4 sa tahmini uyuşmuyor. README akü süresi vermiyor; OZET ve özet ikisini de, 'ölçülmedi' notuyla veriyor.
- `maliyet.json`'da 1,58 m'nin eksik kalemleri: QLED, 11,6" göğüs ekranı, SY8205, hub, HDMI 1,5 m, USB 2 m. BOM'da P6KE6V8A tek; P6KE18A yok. Hepsi P8.1'e.
- `baski-listesi.md:12`: 65 parça, 7,63–7,68 kg, 159–160 sa. BOM'daki baskı parçası 72 adet (62 satır; kabuk 34, kafa 14, omuz 12, dirsek 8, taban 4). Fark P4.3'te.
- Demo sayfası `tasarim/Robot-Tasarim-Demosu.html:967` gömülü maliyet JSON'u 29.10 tarihli (1,65 m notlarıyla). Dokunulmaz; P9.2 / P8.1.
- Brief `OZET.md` (kök) diyor; depo kökünde böyle bir dosya yok, yalnız `tasarim/freecad/OZET.md` güncellendi.
- `git status`'ta `planlama/dongu-158.md` değişmiş görünüyor (+4 −3). Bu paket o dosyaya yazmadı.

## 5. Takma ad geçişleri (P4.5'e)

Eklenen satırlarda 0 geçiş var (`git diff -U0 | grep '^+'`). Yeniden yazılan bir README satırında 1 geçiş kalktı. Dokunulan dosyalarda kalanlar (değiştirilmeyen satırlar):

| Dosya | Sayı | Satırlar |
|---|---|---|
| `planlama/adim3/elektrik.md` | 6 | 34, 105, 107, 113, 116, 378 |
| `planlama/maliyet.json` | 2 | 58, 135 |
| `README.md` | 8 | 59, 61, 77, 78, 100, 103, 107, 123 |
| `Lale-Proje-Ozeti.txt` | 1 | 21 |
| `tasarim/freecad/README.md`, `OZET.md`, `planlama/proje-plani.md` | 0 | — |

## 6. Karar taslağı (karar kuyruğuna yazılmadı; F3a / Ahmet'e öneri)

- **K4 (6 kablo kalemi):** Öneri: a, aday olarak listede, fiyatsız, `secenek "fiyat_bekliyor"`. P8.1'de satıcı sayfası doğrulanınca `tl` girilir ve `secenek` kaldırılıp `g "kosullu"` yapılır. Bu pakette böyle uygulandı.
- **Brief / P4.1 metni:** `F4a-brief.md:8` ve `dongu-158.md:100`'deki "hub kafa arka kabuk yan duvarı" ve "boyun: göğüs HDMI + USB dokunmatik + 12 V" ifadeleri §3'e göre düzeltilmeli (sahibi döngü yöneticisi).
- **KY `uygulama-notu.md:115`:** göğüs 12 V "boyundan" → "tabandan, boyundan geçmez" (sahibi F1; `kablo_yolu_ekran.py` ile hizalanır).
- **`maliyet_toplam.py`:** `tl` null kalemde çökmemesi için null-güvenli toplam (null'ı atla ve say, "fiyatsız N kalem" yazdır). Öneri; betiğe dokunulmadı.
- **K10:** varsayılan D24V50F5 (Pi bara). Tepe 3,28–3,38 A (%66–68) sınırda değil; P8.3 PAM akım ölçümüne bağla.
- **K11:** varsayılan (a) ana anahtardan sonra, röleden önce; değişirse `elektrik.md` sigorta tablosu ve `Lale-Proje-Ozeti.txt` 4.6 birlikte güncellenir.

## 7. Açık kalanlar

- K1 (6. USB cihazı, pano #5) ve K14 (boyun demeti Efe teyidi, pano #6) cevap bekliyor; belgelerde "bekliyor" yazıyor.
- Yeni 11 kalemin fiyatı P8.1'de satıcı sayfasıyla girilecek.
- Akü süresi iki kaynakta farklı (bkz. §4); ölçülmedi.
- Kafa en kötü durum ısısı yeni düzende hesaplanmadı (`elektrik.md:35`).
- Y2b JSON'ları ve demo sayfası eski; P6.1 / P8.1 / P9.2.
- Takma ad geçişleri §5'te; P4.5.
