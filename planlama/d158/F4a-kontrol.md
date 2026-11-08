# F4a bağımsız kontrol (P4.1, P4.2, P4.4) — 09.11.2026

Ajan B (kontrol). Okunan: `dongu-158.md` §1–§3, `F4a-brief.md`, `F4a-gunluk.md` (kanıt sayılmadı), 7 belgenin `git diff`'i.
Her sayı kaynak JSON / CSV'den yeniden okundu; maliyet toplamı betikle ve sayfa mantığının öykünmesiyle (depoya yazmadan) hesaplandı.
FreeCAD kullanılmadı, depoda bu dosya dışında hiçbir şey değişmedi.

## Genel karar: **KOŞULLU GEÇER**

Sayıların hepsi kaynakla birebir. JSON geçerli, toplamlar doğru, uydurulmuş fiyat yok, gizlilik temiz, regresyon 10/10 aynı.
Hub yeri ve boyun demetinde A brief'e değil kaynaklara uydu, doğru olan da kaynaklar. Koşullar küçük ve metinsel (6 madde, hepsi ≤ 2 satır):
tilt ±20 çelişkisi iki belgede söylenmiyor, `Lale-Proje-Ozeti.txt` durum bölümünde F3 ve K2 eskimiş, iki küçük anlam kaybı var.
A'ya ayrı bir düzeltme turu gerekmiyor; C koşulları birebir uygulayabilir.

## Madde tablosu

| # | Madde | Sonuç | Kanıt (kaynakta okunan) |
|---|---|---|---|
| 1 | Boy 1.580,0 | ✅ | LK `toplam_boy_mm` 1580.0; MA `boy_mm` 1580.0 |
| 2 | Parça 1.179 | ✅ | LK `parca` 1179; MA `parca_sayisi` 1179, `karsilastirma.parca` montaj = beklenen = 1179 |
| 3 | Kütle 26.115,6 g / montaj 25.715,6 g | ✅ | UI `ev.kutle_g` 26115.6; MA `kutle_g` 25715.59; TA `robot.pozlar[ev].kutle_g` 26115.6 |
| 4 | AM (−0,03; 522,71; −10,03), montaj (−0,03; 528,46; −9,26) | ✅ | UI `ev.am` [−0.03, 522.71, −10.03]; MA `agirlik_merkezi` [−0.026, 528.457, −9.256] |
| 5 | Modül kütleleri (6.410,8 / 2 × 567,6 / 7.170,4 / 2 × 400,5 / 2.088,5 / 8.109,8) ve parçaları (59 / 73 / 357 / 57 / 161 / 342) | ✅ | MA `moduller` birebir; omuz konumu (0, 1270, 0) |
| 6 | 22 eklem; s3 1.270, uzama 315, taban 520 | ✅ | MA `eklemler` 22 ad; `s3_mm`, `uzama_mm`, `taban_w_mm` |
| 7 | Baskı 72 adet (62 kalem) | ✅ | BOM `Baski` 62 satır, adet toplamı 72 |
| 8 | 10 servo (DS3235 × 4, MG996R × 6), 4 × XL4016, direk 1.115,5 | ✅ | BOM satırları; `Sigma 40x40 ... 1115.5 mm` (satır 152) |
| 9 | Rampa 1,519, düz 2,097; elde 100 / 500 g → 1,479 / 1,329 | ✅ | UI `izgara_yuk_0g.a_sinir_pay15.rampa5_geri` 1.519, `duz_geri` 2.097; `izgara_yuk_100g` / `500g` rampa en küçük 1.479 / 1.329 |
| 10 | Devrilme 3,66 / 3,28 / 4,05 m/s²; statik eğim 20,5 / 18,5 / 22,5°; rampa 2,79 / 2,42 / 3,18; dF 195, dR 175 | ✅ | TA `robot.pozlar[ev].duz` (ileri 3.66, geri 3.28, yan 4.05, `statik_egim_*`, `dF`, `dR`); UI `ev.duz` 3.66 / 3.284 / 4.053, `ev.rampa5` 2.791 / 2.416 / 3.183 |
| 11 | Tilt payı 3,64, pan 2,21, kafa grubu 1.570,8 g | ✅ | KA `tork.tilt.pay_tilt15` 3.64, `tork.pan.pay_iki_hane` 2.21, `tork.tilt.kutle_g` 1570.8 |
| 12 | Mikrofon–hoparlör 574,3 | ✅ | regresyon `mik_hoparlor_mm` 574,3 |
| 13 | Kablo boyları HDMI 757/950, dokunmatik 395/640, 12 V 1.376/1.720, ESP32 971/1.360, hub 617/920, ses kartı 217/270, dizi 85/110, hoparlör 824/1.030, 3,5 mm 36/40, PAM 5 V 64/80 | ✅ | LK `kablo_ozet.kablo` birebir. Hoparlör: LK 824, `uygulama-notu.md:111` ve `kablo-kurali-notu.md` 823; A LK'yi kullandı, tutarlı |
| 14 | Boyun doluluk %39,9 / %44,8 / %34,3, demet 69,9 mm² | ✅ | LK `gecis` 0.399 / 0.448 / 0.343, `boyun_demet_alan_mm2` 69.9 |
| 15 | Port ucu temas 897,1 / 391,5 / 617,3 mm³ | ✅ | LK `kablo_tup_uc_temas` |
| 16 | PAM tepe 0,71 A; Pi hattı 3,28–3,38 A (%66–68) | ✅ | `KY/uygulama-notu.md:98` (hesap, ölçüm değil; belgede "hesap" diye yazılmış) |
| 17 | Motor: rampa 6,86 kg·cm = 6,3'ün 1,09 katı; a 0,25 → 0,92; duruş 0,76; düz 3,31 (0,53) | ✅ | TA `motor.rampa5` T 6.86 oran 1.089; `rampa5_yavas.oran` 0.923; `rampa5_durus.oran` 0.758; `surekli_kgcm` 6.3; `duz` 3.31 / 0.525 |
| 18 | Akü süresi 16,8 / 36,6 / 85,2 W → 12,2 / 5,6 / 2,4 sa; 256 Wh × 0,8 | ✅ | TA `aku.senaryo`, `wh`, `kullanilabilir`; kalemlerde QLED ve 11,6" ekran var (1,58 m yükleri) |
| 19 | Akü 3,0 kg | ✅ | BOM Victron satırı 3000 g; `maliyet.json` akü modeli "3,0 kg"; `arayuz.py:623` (HEAD) `kutle_g=3000.0` |
| 20 | Teker izi 432 (x ±216, z ±185) | ✅ | `planlama/y2/Y2b-ivme.json` `teker_hatti` |
| 21 | Eklem / sürüş sınırları (S1 −45…135, S2 +5…120, S1 ≥ 120 → S2 ≤ 117, tilt ±13, ivme 0,5 / fren 1,8 / rampa 0,1) | ✅ sayı, ⚠️ ifade | `kod/ortak/eklem_sinirlari.json` `eklemler`, `bagimli`, `teker.ivme_sinir_m_s2`. İfade sorunu: madde 30 |
| 22 | Takvim Kapı 1 S+2→S+3, Kapı 2 S+6→S+7, Kapı 3 S+7→S+8 | ✅ | `proje-plani.md:95, 98, 99` |
| 23 | Satır atıfları (`robot-bom.csv` 133/145/147/150/151/156/157/158/159; `KY/uygulama-notu.md` 3, 45, 47, 56–59, 98, 100, 106–115, 123–132, 134; `KY/secenekler.md:26`; `kablo_yolu_ekran.py:6, 19, 31, 116, 197`; `kablo-kurali-notu.md:20-35, 54-55`) | ✅ | Hepsi tek tek açıldı, içerik iddiayla aynı |
| 24 | `arayuz.py` satır atıfları (343–346, 623, 997, 1001, 1003) | ✅ HEAD, ⚠️ sonra | HEAD'de doğru. F2'nin çalışma kopyası 178. satırdan sonra +6 satır ekliyor; F2 commit edilince bu atıflar 6 kayar. Anahtar adı da yazıldığı için okunabilir kalır (öneri, koşul değil) |
| 25 | Hub yeri / boyun demeti (brief'teki orkestratör hatası) | ✅ A doğru | K5 kapanış kaydı (`karar-kuyrugu.md:150`): hub gövdeye. `uygulama-notu.md:58` hub y 1.085–1.157 (omuz 1.270'in altı, gövde). `kablo_yolu_ekran.py:6, 31, 197`: boyunda 12 V çift + tilt (`MEVCUT`) + HDMI + hub uzatması + hoparlör (`yeni`). Göğüs 12 V yolu (`:116`) tabandan başlıyor, en üst noktası y 1.205 (< S3 1.270): boyundan geçmiyor. `uygulama-notu.md:115` "(boyundan)" yanlış, `kablo_yolu_ekran.py:2` başlık yorumu da eski düzeni anlatıyor (ikisi de F4a dışında) |
| 26 | `maliyet.json` geçerli | ✅ | `json.load` sorunsuz; 130 kalem, 11 not; satır başına bir kalem biçimi korunmuş; `git diff --check` temiz |
| 27 | Toplamlar | ✅ | `maliyet_toplam.py` önce: genel 103.767,58, koşullu dahil 109.056,64. Sonra: **102.919,71** ve **108.208,77**. Ara toplam farkı tam 737,28 (MAX98357A, adet 1); genel farkı 847,87 = 737,28 × 1,15 (847,872, kuruş yuvarlaması). Koşullu grup 4.599,18 değişmedi (omni 4.539,18 + fan 60) |
| 28 | `fiyat_bekliyor` seçenek mantığını bozuyor mu | ✅ bozmuyor | Sayfa `on()` öykünmesi (V1/V2/V3 × yazıcı/hizmet × elde açık/kapalı × yedek açık/kapalı, 24 durum): V1 ve V2'nin 16 durumu birebir aynı; V3'ün 8 durumunda fark yalnız −847,87 (elde+hizmet+yedek 847,88, yuvarlama). Null `tl`'li 11 kalemin hepsi `secenek "fiyat_bekliyor"`; betik ve sayfa bunları çarpmadan önce eliyor, NaN / çökme yok. `demo_uret.py` null'ı JSON'a olduğu gibi gömer, sayfa gizler |
| 29 | Uydurulmuş fiyat | ✅ yok | 11 yeni kalemin 11'i `tl: null`, `durum "dogrulanmadi"`, satıcı/URL boş. 01.11 PAM fiyatı (21,86) bilerek kullanılmamış |
| 30 | MAX98357A tarihçesi | ✅ | Kalem silinmedi; `"ver": "v1,v2"` ile V1/V2'de duruyor, V3'ten çıktı, not alanı nedenini yazıyor (K16, 04.11). 29.10 V3 listesi git'te (`HEAD:planlama/maliyet.json`) |
| 31 | Kapsam: K4'ün 6 kalemi + 90° fişler | ✅ | K4 sorusundaki 6 kalem (`karar-kuyrugu.md:137-138`, `uygulama-notu.md:134`) birebir; 3 adet 90° fiş (`kablo_yolu_ekran.py:19`, F1b B). PAM8403 ve USB ses kartı satırları brief'in "04.11 kararıyla uyumlu hâle getir" maddesi kapsamında |
| 32 | Açık kararlar işaretli mi | ✅ büyük ölçüde | `elektrik.md`: K1, K10, K11, K14 her geçişte "karar bekliyor (Kn)" ya da "bekliyor (K1, pano #5)"; K11 varsayılanı "önerilen varsayılan", K10 için "K10'un varsayılanıdır, karar değil". README / OZET / proje-plani aynı. Eksik: `Lale-Proje-Ozeti.txt:123` seri yolu (koşul 3) ve K2 (koşul 2) |
| 33 | 6. USB cihazı uydurulmamış | ✅ | Her yerde "adı belli 5 cihaz" + "6. cihaz bekliyor (K1, pano #5)"; eski "yönlü mikrofonun ses kartı olabilir" tahmini de metinden çıktı |
| 34 | 1,65 m kalıntısı | ✅ | `git grep -n -E "1,65 m\|1\.65 m\|165 cm"` 197 satır. Dokunulan 7 belgede hepsi "Önce" sütunu, [tarihçe] başlığı ya da "o günkü 1,65 m" bağlamı. Kalanlar: `planlama/y2/`, `dongu.md`, günlük/kontrol dosyaları, `siparis-farki-2026-10-29.md`, `yazilim-notu-stowent-170.md`, `yazilim-plani.md:126` (29.10 kararı), demo sayfası (P9.2), `arayuz.py` yorumları (F2'nin dosyası; `:18` "BOY TEK PARAMETRE: 1,65 m" yorumu eski ama değer 1580 → P4.5 / P6.1'e not), `eklem_sinirlari.json:193` (`kod/`, üretilen dosya) |
| 35 | Gizlilik: eklenen satırlarda takma ad | ✅ 0 | `git diff -U0 -- <7 belge> \| grep -i '^+.*<takma ad>'` → 0. Silinen satırlarda 1 (README eski tarihçe cümlesi). Kalan geçişler (değişmeyen satırlar): `elektrik.md` 6, `maliyet.json` 2, `README.md` 8, `Lale-Proje-Ozeti.txt` 1 satır → P4.5 |
| 36 | Gizlilik: soyad, yerel yol, kişisel bilgi | ✅ | Eklenen satırlarda kişi adı yalnız "Efe" (depoda zaten geçiyor), soyad yok, README ekip bölümüne dokunulmamış. Yerel disk yolu, e-posta, telefon numarası yok ("telefon" yalnız "telefon kumandası"). `F4a-gunluk.md` ve `F4a-brief.md`'de takma ad 0, yerel yol 0 |
| 37 | Regresyon | ✅ 10/10 aynı | `py -3 planlama/d158/regresyon.py --yazma` → boy 1580, çakışmalar 0/0/0/0, rampa 1,519, tilt 3,64, pan 2,21, mik–hop 574,3, SY8205 × USB 0; "GEÇER (hepsi okundu, kötüleşen yok)", çıkış 0. F2 kaynaklı değişen değer yok |

## Sorulan özel noktalar

**Tilt −13…13.** Belgeler ±13'ü 29.10 kararı ve `eklem_sinirlari.json` sınırı olarak veriyor. Sayı doğru, karar kaydıyla da uyumlu:
`tilt.neden` "yazilim siniri (karar 29 Ekim 2026, Y2a KZ3: +-15 -> +-13)" diyor. Ama iki belge bunu "yazılım sınırı" diye düz yazıyor ve main'deki kodun
bugün ±20 (70…110) kullandığını söylemiyor (F5 Ç4, `servo-10-oneri.md:34, 83`). Güncel kafada ±20 çakışıyor: KA `tarama.kafa_govde` her pan açısında tilt +20'de 327,4,
−20'de 654,9 mm³ (`ilk_carpan`). Konu pano #6'da Efe'ye soruldu. `OZET.md` tablosu "robot yazılımında uygulanmalı" başlığıyla doğru çerçeveliyor;
`Lale-Proje-Ozeti.txt:152` (başka bir modele bağlam veriyor) ve `README.md:44`'te çelişki görünmüyor → koşul 1.

**"Rampa riski 1,09 kat".** Kaynak TA `motor.rampa5.oran` 1.089 (a 0,5, 5°, T 6,86 / sürekli 6,3). Eski "%90" yaklaşık a 0,25 değerine karşılık geliyordu
(`rampa5_yavas.oran` 0,923); A bunu da yazmış. Düzeltme doğru ve kaynaklı. Not: güncel rampa sınırı 0,1 m/s² için TA'da oran yok; metin bunu
"0,25 ile 0,92, duruşta 0,76" diye iki uçla veriyor, uydurma ara değer yok.

**`Lale-Proje-Ozeti.txt` geniş değişiklik, kapsam.** Brief P4.4 bu dosyayı "1,58 m'ye, eski sayılar" diye adıyla veriyor. Bu yüzden şu değişiklikleri kapsam içi sayıyorum:
mimari (7" → QLED, Nextion → 11,6" HDMI, MAX → PAM), tilt, rampa ivmesi 0,25 → 0,1 (`eklem_sinirlari.json` `teker.ivme_sinir_m_s2.rampa_surus` 0.1),
güç zinciri (XL4016 C 5 A pan + tilt: `elektrik.md` sigorta tablosu; D36 → D24V50F5: `elektrik.md:23`), takvim S+n ve rampa riski.
Hepsi 17 Ekim ya da 125 cm sayısıydı ve hepsi kaynaklı. Kontrol ettiğim her sayı tuttu. "Devreye al: Pi 'arm'; telefon kumandası" için kaynak `elektrik.md:255`
ve `yazilim-plani.md:48`. Sorunlar yalnız durum bölümünün tarihi (F3 bitti, K2 eksik) ve seri yolunda K14 işaretinin olmaması.

## Koşullar (C birebir uygular; her biri ≤ 2 satır)

1. **Tilt ±20 çelişkisi.**
   - `Lale-Proje-Ozeti.txt:152`
     eski: `  Kafa tilt        : −13…13°   (yazılım sınırı, karar 29.10; tilt payı ±15'te 3,64, KA)`
     yeni: `  Kafa tilt        : −13…13°   (tasarım sınırı, karar 29.10; tilt payı ±15'te 3,64, KA). main'deki kod bugün ±20`
           `                   (70…110) kullanıyor; ±20'de kafa gövdeye çarpıyor (KA tarama 327,4 / 654,9 mm³), Efe'ye soruldu (pano #6).`
   - `README.md:44`
     eski: `tilt yazılım sınırı ±13° (`kod/ortak/eklem_sinirlari.json`)`
     yeni: `tilt sınırı ±13° (karar 29.10, `kod/ortak/eklem_sinirlari.json`; main'deki kod ±20 kullanıyor, ±20'de çakışma var, pano #6)`
2. **Durum bölümü eskimiş (F3 bitti; AI HAT+ ana modelde yok, K2 açık).** `Lale-Proje-Ozeti.txt`
   - `:212` eski: `AI HAT+,` → yeni: `AI HAT+ için iki çözüm (ana modelde yok, K2),`
   - `:215` eski: `- Sürüyor: omuz mekanik durdurucu ve omuz çakışma taraması (F2), karar kaydı (F3a), belgeler (F4a).`
     yeni: `- Sürüyor: omuz mekanik durdurucu ve omuz çakışma taraması (F2), belgeler (F4a). F3 (elde yük, servo payları) tamam; karar K3/K9'da.`
   - `:220` eski: `elde yük sınırı (K3/K9).` → yeni: `elde yük sınırı (K3/K9), AI HAT+ × cıvata boss'u (K2).`
3. **Seri yolunda K14 işareti yok.** `Lale-Proje-Ozeti.txt:123`
   eski: `USB, Pi port 3 → boyundan gövdedeki hub → ESP32 (taban), 115200 baud`
   yeni: `USB, Pi port 3 → boyundan gövdedeki hub → ESP32 (taban; CAD'de böyle, Efe teyidi K14), 115200 baud`
4. **`tasarim/freecad/OZET.md:34-35` eskimiş (F3 bitti).**
   eski: `Kol servo payları 3,0 kg akü ve AI HAT+ sonrası P3.2'de` / `  yeniden hesaplanıyor (F3a); burada yazılmadı.`
   yeni: `Kol servo payları 3,0 kg akü sonrası P3.2'de` / `  hesaplandı (`planlama/d158/F3a-yuk.json`; AI HAT+ ana modelde yok, K2); el yükü önerisi düzde ≤ 100 g / el (K3, K9).`
5. **Elde düşülmüş toplamın koşulu kaybolmuş.** `README.md:50`
   eski: `Elimizdekiler düşülürse ≈ 78.000 TL.`
   yeni: `Yüz ekranı hocadan gelirse ve elimizdekiler (Pi 5, hafıza kartı) düşülürse ≈ 78.000 TL.`
   Dayanak: `maliyet.json`'da V3'te `elde` işaretli üç kalem: Ana bilgisayar, Hafıza kartı, Yüz ekranı. Yüz ekranı 29.10 listesindeki Waveshare 10,1" (B).
   QLED'in hocadan gelip gelmeyeceği P8.1'de netleşmeli.
6. Koşul yok, kayıt notu: `F4a-gunluk.md` §4'teki "README ve özet yalnız elektrik.md tahminini … verdi" cümlesi yanlış. `OZET.md` ve `Lale-Proje-Ozeti.txt`
   önce TA tahminini (12,2 / 5,6 / 2,4 sa), sonra `elektrik.md` tahminini veriyor; README akü süresi vermiyor. Belgeler doğru, yalnız günlük cümlesi hatalı. C isterse
   günlükte "README akü süresi vermiyor; OZET ve özet ikisini de, 'ölçülmedi' notuyla veriyor" diye düzeltir.

Büyük düzeltme yok. A'ya ayrı tur gerekmiyor.

## Öneriler (koşul değil; sahibi yanında)

- **`arayuz.py` satır numaraları** (`elektrik.md` 09.11 paragrafı ve tablolarında 343–346, 623, 997, 1001, 1003): F2 commit edilince +6 kayar. Anahtar adları
  (`SES_USB.hub`, `pi_usb`, `kablo_pay`, `TABAN["aku"]`, `GOGUS_EKRAN` port) yanlarında yazılı, okunabilirlik kalıyor. P4.5 ya da P6.1 sırasında anahtar adına indirgenebilir.
- **`fiyat_bekliyor` gizli dışlama riski:** P8.1'de `tl` yazılıp `secenek` değiştirilmezse kalem sessizce toplam dışında kalır. A'nın önerisi doğru:
  `maliyet_toplam.py`'a "fiyatsız / fiyat_bekliyor N kalem" satırı (betiğe bu pakette dokunulmadı, doğru). Sahibi P8.1.
- **README "Kafa grubu 1.570,8 g"** tilt'in taşıdığı grubun kütlesi (KA `tork.tilt.kutle_g`). Modül kütlesi 2.088,5 g (OZET ve özet). "tilt grubu" demek karışıklığı önler.
- **Kaynaktaki eski ifadeler** (F4a dışı, dokunulmadı): `KY/uygulama-notu.md:115` göğüs 12 V "(boyundan)" → "(tabandan, boyundan geçmez)";
  `kablo_yolu_ekran.py:2` başlık yorumu "gogus ekrani HDMI + USB dokunmatik boyundan iner" → 05.11 B düzeni. İkincisi takma ad içeren satırda (P4.5 ile birlikte).
- **90° HDMI adaptör** v4'te zaten olabilir; A işaretlemiş. P8.1 mükerrerlik kontrolü.
- `tasarim/freecad/README.md` modül bölümleri (~:150, :156) hâlâ Nextion ve 125 cm anlatıyor; satır 7 uyarıyor. P6 / P7'de yenilenir.

## A'nın karar taslaklarına görüşüm (`F4a-gunluk.md` §6)

| Taslak | Görüş |
|---|---|
| K4: a, fiyatsız `fiyat_bekliyor`, P8.1'de `tl` + `secenek "kosullu"` | Katılıyorum. Toplamı bozmuyor, iz bırakıyor (`kosullu` alanı K4 / F1b). Tek şart: yukarıdaki gizli dışlama riski için betik uyarısı |
| Brief / P4.1 metni düzeltilsin | Orkestratör P4.1 satırını zaten düzeltti (`dongu-158.md` diff). `F4a-brief.md:8` olduğu gibi kalabilir (tarihçe); günlük §3 nedeni açıklıyor |
| `uygulama-notu.md:115` düzeltilsin | Katılıyorum (madde 25 kanıtı). Sahibi F1 / KY; F4a'da değil |
| `maliyet_toplam.py` null-güvenli | Katılıyorum; "atla ve say" doğru davranış, sessiz atlama değil |
| K10 varsayılan D24V50F5 (%66–68) | Hesap olarak tutarlı (`uygulama-notu.md:98`). "Sınırda değil" ifadesi ölçümsüz; P8.3 PAM akımı ve Pi tam yük tepesi (hesaplanmadı, `elektrik.md:22`) ölçülmeden kesin denmemeli. Varsayılan olarak kalabilir |
| K11 varsayılan a | Kuyruktaki varsayılanla aynı. Güvenlik açısından "doğrulanmadı" notu kuyrukta var; belgede de "önerilen varsayılan" diye geçiyor, uygun |

## Commit'e girmemeli

- F2'nin alanı: `tasarim/freecad/arayuz.py`, `tasarim/freecad/omuz/`, `tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json`,
  `planlama/d158/F2-*`.
- Orkestratörün dosyası: `planlama/dongu-158.md` (F4a yazmadı; C'nin ya da orkestratörün kaydına).
- İzlenmeyen ve dışlanan: `kvkk/`, `rapor/`, `tubitak-2209b/`, `tasarim/solidworks/`, `raporlar/kaynaklar/06-onayli-satici-*.md`, `07-gogus-ekrani-ve-5v.md`,
  `KY/kaynak/`, `lale_dongu*`, diğer paketlerin `d158` dosyaları.
- F4a için açık `git add` listesi: `planlama/adim3/elektrik.md`, `planlama/maliyet.json`, `README.md`, `tasarim/freecad/README.md`, `tasarim/freecad/OZET.md`,
  `planlama/proje-plani.md`, `Lale-Proje-Ozeti.txt`, `planlama/d158/F4a-brief.md`, `planlama/d158/F4a-gunluk.md`, `planlama/d158/F4a-kontrol.md`.
  Üç F4a dosyasında takma ad 0, yerel yol 0 (bu dosya dahil).
