# F9c kontrolü (P9.3: sonuç raporu ve Ahmet'e özet): bağımsız kontrol ajanı B, 09.11.2026

Kontrol edilenler: `planlama/d158/sonuc-rapor.html`, `F9c-uret.py`, `F9c-dogrula.py`, `F9c-dusukler.json`, `F9c-gunluk.md`, 8 ekran görüntüsü,
`karar-kuyrugu.md` (K51, K52), `tasarim/Robot-Tasarim-Demosu.html`. Esas alınan: çalışma ağacı (dal `lale-duzeltme`, HEAD `0089d97`).
A'nın günlüğüne ve doğrulama betiğine dayanmadım; her sayıyı kaynağından kendim okudum. Yazdığım tek depo dosyası bu dosya. Geçici betikler,
tarayıcı profili ve ekran görüntüleri scratchpad'de. Commit, push, silme, checkout, reset, stash yapılmadı; FreeCAD koşulmadı.
`git status --porcelain` her ölçümden önce ve sonra aynıydı. Arka planda çalışan süreç bırakılmadı (headless Chrome 0).

## Karar: **KOŞULLU**

Kritik bulgu 0, orta 2, düşük 10.

Raporun gövdesi sağlam:
- 36 paket ve durumları plan ile satır satır aynı.
- 118 hash'in hepsi `git log`'da ve döngüde.
- Sayılar kaynakla aynı; 60'tan fazla sayıyı bağımsız okudum, yalnız 1 eski sayı çıktı.
- Açık karar sayısı 47/52 ve K51/K52 kaynaklarıyla tutarlı. Kuyrukta başka madde değişmemiş.
- Demo bayt bayt aynı. Konsol 0, kırık bağlantı 0, 360 px'te yatay kaydırma 0.
- `kontrol` 0, regresyon 0. Commit listesinde ad, soyad, yol ve artifact adresi 0.

Geçmeyen iki nokta:
- **O-1:** takvim tablosunun 9 satırından 3'ü düşmüş. Rapor yine de "birebir" diyor.
- **O-2:** F7c'nin TVS açığı (KT-F7c-1) elektrik güvenliği listesinde yok.

İkisi de küçük düzeltme: betikte iki satır, JSON'a bir satır, sonra yeniden üretim. B dar yeniden kontrol yapar.

## Bulgular

### O-1 (orta). Takvim tablosu eksik; "birebir" iddiası yanlış
- **Kaynak:** `planlama/proje-plani.md:107-117` "İki örnek" tablosu 9 satır.
- **Raporda olan:** 6 satır (Taban … Demo hazır).
- **Düşen satırlar:**
  - "Teslim (stoklu)": S+1, 22.11 (H8) / 6.12 (H10).
  - "H15–16'ya sığıyor mu": A/16.11 **Evet**, diğer üçü **Hayır**. Bu, Ahmet için takvimin ana sonucu.
  - "Kesinti 2 + 3 ile (≈ −1 hf)".
- **Kök neden:** `F9c-uret.py:672-679`.
  - `sat_` listesi yalnız "| " ile başlayan satırları alıyor. Ayraç satırı (`|---|`) bu listede yok. Bu yüzden `bas + 2` ilk veri satırını
    (Teslim) atlıyor.
  - Boş hücreli satırlarda (`| |`) " | " ile bölme bir hücre eksik veriyor. Döngü `break` ile duruyor.
- **Neden doğrulamadan geçti:** `F9c-dogrula.py` takvimde satır sayısına bakmıyor. Yalnız görünen sayıların kaynakta geçip geçmediğine bakıyor.
- **Düzeltme:**
  - Döngü `bas + 1`'den başlasın.
  - Hücreler boş hücreyi koruyacak biçimde bölünsün (ör. `l.strip().strip("|").split("|")`, sonra `strip`).
  - Kalın yazım (`**…**`) korunsun.
  - Doğrulamaya "takvim satır sayısı kaynak = rapor (9 = 9)" denetimi eklensin.
- Grep kanıtı (`sonuc-rapor.html`): "Teslim (stoklu)" 0, "sığıyor" 0, "22.11 (H8)" 0.

### O-2 (orta). KT-F7c-1 (TVS) açığı raporda ve kuyrukta yok; elektrik grubu eksik
- **F7c'nin bulgusu:** `F7c-gunluk.md:203-213`.
  - P6KE6V8A veri sayfası Diodes DS21502'de "OBSOLETE – PART DISCONTINUED" yazıyor.
  - Satıcı ürününün (`maliyet.json:103`, Direnc.net) üreticisi doğrulanmadı.
  - Önerilen E3a metni ("bant = katot (Diodes DS21502 Rev. 20-4, 2024); satıcı ürününün üreticisi doğrulanmadı") bir sonraki metin turuna bırakıldı.
- B bunu doğruladı (`F7c-kontrol.md:269-278`). F7c raporu açık diye yazıyor: `F7c-rapor.html:230` "açık kalanlar: KT-F7c-1…3'ün uygulanması".
- **Bugünkü durum:**
  - P7.4'ün kapsamında bu madde yoktu.
  - Rehber E3a bugün yalnız "TVS tek yönlü: katot (çizgili uç) +5 V'a, anot GND'ye" diyor (`rehber/veri/rehber-veri.json`). Üretici ve OBSOLETE notu yok.
  - Depoda F7c dışında "OBSOLETE" 0.
- KT-F7c-2 ve -3 K51/K52 oldu. KT-F7c-1 ise ne kuyrukta, ne "Karar değil, iş" bölümünde, ne raporun açık düşüklerinde.
- A, günlüğün §6'sında bunu "TVS kutbu (→ F7c)" diye kapalı saydı. Kutup F7c'de doğrulandı; ama üretici, OBSOLETE ve metin önerisi açık.
- K51 (varsayılan a) ikinci adedin de bu parçadan olmasına dayanıyor. Bu yüzden sipariş öncesi bir satıcı teyidi gerekiyor.
- **Düzeltme:** `F9c-dusukler.json` elektrik grubuna bir satır eklenecek. Satırın alanları:
  - paket: F7c, `KT-F7c-1`;
  - tür: doğrulanmadı;
  - cümle: "P6KE6V8A üretimden kalkmış (Diodes), satıcı ürününün üreticisi doğrulanmadı; E3a metin önerisi uygulanmadı";
  - adım: "sipariş öncesi satıcıdan üretici / veri sayfası teyidi (K51 ile); E3a metni sonraki rehber turunda".

  Elektrik 17 → 18, toplam 46 → 47 olur. Bu bir karar değil; kuyruğa girmesi orkestratörün seçimi.

### D-1 (düşük). `F9c-dogrula.py` kısmen totoloji; altbilgideki iddia abartılı
Altbilgi: "çıkış 0 = her sayı kaynağıyla aynı".

Gerçek karşılaştırma yapan denetimler:
- [1] `data-j` 77 değeri kaynak JSON'dan, `git show` ile ya da hesapla yeniden okuyup aynı biçimle karşılaştırıyor.
- [6] açık karar listesini kuyruktan kendi ayrıştırmasıyla çıkarıyor.
- [5] paket kodlarını plandan alıyor.

Bağımsız olmayan ya da zayıf denetimler:
- **(a)** Düşük sayıları (46 / 17 / 29) rapor ile aynı ara veriden, A'nın kendi `F9c-dusukler.json`'undan geliyor. Kontrol dosyalarına karşı denetim yok.
- **(b)** A/B/C grup sayıları sayfanın kendi `data-grup` satırlarından sayılıyor. Sayfa kendisiyle karşılaştırılıyor.
- **(c)** Maliyet hesabı üretici ile aynı fonksiyondan geliyor (`F9d-tarama.py` `_maliyet`). Benim ayrı hesabım tuttu (aşağıda).
- **(d)** [3] `data-kaynak`, sayının kaynak dosyada **herhangi bir yerde alt dize** olarak geçmesine bakıyor (`s in m`). "0", "4", "94" gibi
  sayılar hemen her dosyada geçer.
- **(e)** [3b] satır numarasının yalnız dosya uzunluğundan küçük olduğuna bakıyor, satırın içeriğine bakmıyor.
- **(f)** Satır başına durum emojisi planla karşılaştırılmıyor; yalnız toplam sayılar karşılaştırılıyor. Ben satır satır karşılaştırdım: 36/36 aynı.
- **(g)** Hash'in doğru pakete ait olduğuna değil, yalnız `git log`'da bulunduğuna bakıyor.

Kanıt: O-1 ve D-2 doğrulamadan geçti.

Öneri: altbilgi "çıkış 0 = JSON değerleri kaynakla aynı; metin sayıları kaynak dosyada geçiyor" olsun. O-1 için takvim satır sayısı denetimi
eklensin.

### D-2 (düşük). P8.1 satırında eski sayı
- Raporun P8.1 satırı: "136 satırın 94'ü tam doğrulandı".
- 94, F8a A'nın ilk turundan (`dongu-158.md` §5).
- Son durum `F8a-siparis.json` `toplamlar.sayac`'ta: `dogrulandi_onayli` 86 + `dogrulandi_onaysiz` 7 = **93**. F8a raporu da bunu yazıyor
  (`F8a-rapor.html:90` "86 onaylı + 7 onaylı olmayan").
- 136 doğru (`sayac.siparis_satiri`).

### D-3 (düşük). "Ahmet'in yapacakları": iki ifade karar verilmiş gibi okunuyor, bir atıf yanlış
- **K49:** "(5 girdi .gitignore, 5 dosya commit)". Önünde "varsayılan" yok; karar verilmiş gibi okunuyor. K47'de "varsayılan b" yazıyor, K49'da da yazmalı.
- **"ikisi K18–K24 ile birlikte":** K47 için yanlış. K47'nin beklettiği "Rehber turlarının git add listesi, depo büyümesi". K18–K24 bağı yalnız K49'da.
- **K48:** "varsayılan sil" yanında "Ahmet'in onayıyla" yok. C tablosunda var; yapılacaklarda da olmalı.

Doğru olanlar:
- `main` birleştirmesinin Ahmet'in onayına bağlı olduğu açık yazıyor.
- Silme işleri ve `.gitignore` kararları "Ahmet'in yapacakları" başlığı altında.
- Efe'den beklenen #5, #6, #7 tam.
- Liste brief'in beş maddesini kapsıyor.

### D-4 (düşük). Aciliyet: K3 C'de, B'ye uygun
- K3 elde yük sınırı, bir güvenlik sınırı.
- Kuyruğa göre rampa 5°'de 100 g'da devrilme payı 1,479, 500 g'da 1,329; ikisi de < 1,5 (`karar-kuyrugu.md` K3).
- K38 ve K45 (yazılım hız sınırları) "kolların ilk hareketinden önce" gerekçesiyle B'de. K3 de aynı gerekçeyle B'ye uyar: kolların yüklü ilk
  hareketinden önce.
- Sipariş ya da güvenlik öncesi gerekip C'ye düşmüş başka madde bulmadım:
  - K18–K26 ve K47–K49 depo, belge ve dil maddeleri;
  - K25 ve K26 için "main birleştirmesinden önce" notu var.
- A 20 / B 13 / C 14 toplamı 47; gerekçeler savunulabilir.

### D-5 (düşük). "Kayıtta yok" yazan varsayılanlar
- K32, K35, K36 ve K45'te varsayılan sütunu "Kayıtta yok". Bu, kuyruk özet tablosundan birebir alınmış, yani doğru.
- Ama madde gövdelerinde öneri var:
  - K32: "alınacaksa S'nin ilk partisinde; stok 1'e düşerse öne alınsın";
  - K36: "ikinci satıcı ya da adet düşürme";
  - K45: A'nın taslağı a ile b arasında.
- Brief "önerilen varsayılanı yaz" diyor. "Kayıtta yok; F8a önerisi: …" biçimi daha bilgilendirici olur.

### D-6 (düşük). P0.1–P0.3 hash bağı kaba
- Üç paketin her biri aynı 6 F0 commit'ine bağlı.
- `8dcc4eb`, `0b8a245`, `fa49caa`, `680b965` yalnız P0.1'in sınıflandırma commit'leri: konu satırları rehber, elektrik, baskı listesi ve demo.
- P0.2 ve P0.3 için `93da9af` ("plan, F0 (sınıflandırma, karar kuyruğu, regresyon betiği)") ve `c1bb4ed` yeter.
- Hash'lerin hepsi var ve döngü içinde; sorun yalnız paketlere bağlamada.

### D-7 (düşük, görsel)
- P6.1 "İş" hücresi "Önce `kabuk_parcalar.py" diye kesilmiş: tek bir backtick düz metin olarak görünüyor.
- 1400 px'te karar tablolarının "KOD" başlığı "KO / D" diye ikiye kırılıyor (ekran görüntüsü 1400-kararlar).

### D-8 (düşük). Sipariş toplamının niteleyicisi düşmüş
- Rapor: "Sipariş paketi toplamı (baskı hizmetiyle, pay dahil) 107.569,14".
- Kaynaktaki ad: "Okul bütçesi (parça + hizmet), doğrulanmamış ve K4 dahil × 1,15" (`F8a-siparis.md:22-25`).
- Raporda "doğrulanmamış ve K4 dahil" kısmı eksik.
- Kararsız kalemler hariç tutar 107.119,16 (`toplamlar.kararsiz_haric_pay15`).

### D-9 (düşük, yalnız günlük)
- `F9c-gunluk.md` §7 madde 7, yanlışlıkla yayımlanan özel sayfayı "F9b B"ye bağlıyor.
- Plan §5'e göre bunu F6b B yaptı ("F6b B: KOŞULLU GEÇER … B yanlışlıkla özel bir artifact yayımladı").
- Raporda paket adı geçmiyor; etkisi yalnız günlükte.

### D-10 (düşük, atıf)
- "Mantar 0,26 m yükseklikte" bilgisi `F8d-kontrol.md:271`'de.
- Rapor satırı `F8d :376–377`'yi gösteriyor; orada yalnız "Ö1 açık iş" notu var.

### Bilgi (bulgu değil)
- **Korunan değerlerdeki "son koşu":** `regresyon-son-kosu.json`, 2026-11-09T14:30:50. Sonraki paketler regresyonu `--yazma` ile koştu.
  Benim bugünkü koşum aynı 10 değeri verdi ("aynı" 10/10).
- **Demo karar listesi:** demo K50–K52'yi göstermiyor; liste `demo_uret.py` içindeki sabit `KARARLAR` listesi. Orkestratör kararıyla kabul edildi;
  raporun "Kayıt notları" bölümü bunu doğru yazıyor.
- **Pakete ait olmayan değişiklikler:** çalışma ağacında 13 kabuk PNG'si ve `tasarim/freecad/montaj/yerlesim-kontrol.json` (K23).
  A'nın listesinde yok; doğru.
- **`dongu-158.md`:** kilit tablosundaki F9c B satırı ve P9.3 🔄 durumu C'de güncellenmeli.
- **Tarayıcı:** konsol 0. Koyu temada 360 px görüntü okunaklı.

## Özellikle bakılanlar: sonuçlar

### 1. Paket envanteri
- Planda 36 paket (F0 3, F1 7, F2 2, F3 2, F4 5, F5 3, F6 2, F7 4, F8 4, F9 4).
- Durumlar: 33 ✅, P1.4 🟡, P4.5 ⛔, P9.3 🔄.
- Raporun 36 satırıyla **satır satır aynı**: kod ve durum emojisi.
- Rapordaki hash'ler:
  - 118 hash, 66 benzersiz;
  - hepsi `git rev-parse --verify` ile var;
  - hepsi döngü aralığında (`8dcc4eb^..HEAD` = 66);
  - pakete bağlanmayan commit 0.
- 66 commit'in konu satırını tek tek pakete karşı okudum. 15'ten fazlası doğrudan doğru pakete bağlı:
  - `f567ac2` P1.1, `fc8d7b5` P1.4, `409d521` P1.5;
  - `9cca013` / `1a319f2` P3.1–3.2;
  - `79fb383` / `233ce00` P4.1/4.2/4.4;
  - `c7f9af4` / `34d0cc0` / `0979d70` P4.5;
  - `a35cab1` / `76fd4b2` / `fbaa7ab` / `2879c86` P8.1;
  - `ff1c2e9` / `b7c7cb8` / `33d2f76` P2;
  - `f7ed8c4` / `e796f15` P4.3 + P8.2;
  - `647cafc` … `22bcfd2` P6.1 + P4.5;
  - `887bcfe` / `3946ad5` P7.1;
  - `0f8e1ad` / `45af546` / `8bead02` P6.2;
  - `649885f` / `2d1f412` / `059a849` P7.2;
  - `a3fbcd6` / `8ce30ec` P9.2;
  - `e448eab` / `00a2f56` / `4c7e2ec` P7.3;
  - `1a67071` / `c96ed03` P7.4;
  - `afea121` / `5d1fbd1` P9.4;
  - `e7e6f0d` / `0089d97` P7.4 + P9.4;
  - `fc9c651` / `15b0a30` P8.3;
  - `f747bb0` / `7e78b45` P8.4;
  - `979b995` / `92efdb0` / `e700636` P9.1;
  - `4d242eb` / `3159125` / `5cc17c4` P5.
- Tek kaba bağ D-6.

### 2. Sayılar (bağımsız okuma)
Her değeri kendi betiğimle doğrudan kaynak anahtarından okudum (raporun `data-j` özniteliklerini kullanmadan).

| Konu | Rapor | Benim okumam | Kaynak |
|---|---|---|---|
| Boy | 1.580,0 mm | 1580.0 | `lale158-kontrol.json` `toplam_boy_mm` |
| Parça (ana montaj) | 1.179 | 1179 | `montaj-analiz.json` `parca_sayisi` |
| Kütle ana montaj | 25.720,55 g | 25720.55 | `montaj-analiz.json` `kutle_g` |
| Kütle ev pozu / kablo payı | 26.120,6 / 400 g | 26120.6 / 400.0 | `uygulama-ivme.json` `ev.kutle_g`, `kablo_payi.kutle_g` |
| Servo / DS3235 / MG996R | 10 / 4 / 6 | 10 / 4 / 6 | demo `script#kaynak` `servo`, `s_ds`, `s_mg` |
| Baskı adet / tür / destekli | 72 / 62 / 13 | 72 (parça adetleri toplamı da 72) / 62 / 13 | `baski-analiz.json` `toplam.adet`, `len(parcalar)`, `toplam.destekli_adet` |
| Filament | 7,67–7,73 kg | 7668.9–7726.7 g | `toplam.toplam_g` |
| Destek | 124,5 g | 124.5 | `toplam.destek_g` |
| Süre | 159,90–161,08 sa | 159.9–161.08 | `toplam.sure_sa` |
| PETG / PETG-CF | 6,47 / 1,19–1,25 kg | 6474.9 / 1194.0–1251.8 g | `Y2b-baski.json` `toplam.petg_g`, `cf_g` |
| Parti 0–4 | 8/27/25/9/11 | 8/27/25/9/11 | `F4c-partiler.json` `partiler.N.toplam.adet` |
| Maliyet genel | 118.666,22 | 118.666,22 (Decimal) ve `maliyet_toplam.py` "genel 118666.22" | `maliyet.json` |
| Koşullularla | 124.573,11 | 124.573,11; `maliyet_toplam.py` "genel 124573.11" | aynı |
| Elde düşülmüş | 93.770,47 | 93.770,47 | aynı |
| QLED satın alınırsa | 102.071,11 | (ara − elde + 7.217,95) × 1,15 = 102.071,11 | `maliyet.json` + `F8a-siparis.json` QLED `birincil.fiyat` |
| Sipariş paketi | 107.569,14 | 107569.14 | `F8a-siparis.json` `toplamlar.okul_butcesi_dahil_pay15` (ad, D-8) |
| Bütçe farkı | 29.545,18 | 29545.18 | `toplamlar.fark_alinacaklar` |
| Sipariş satırı / doğrulanan | 136 / 94 | 136 / **93** | `toplamlar.sayac` (D-2) |
| Rehber adım / veri | 50 / 50 | 50 / 50 | `planlama/rehber/kontrol.json` `ozet.adim`, `rehber-veri.json` `adimlar` |
| Rehber parça / mesh | 1.192 / 1.192 | 1192 / 1192 | `ozet.parca_rehber`, `ozet.parca_mesh` |
| PDF sayfa / en küçük yazı | 54 / 8,1 pt | 54 / 8.1 | `yazdir.pdf_sayfa`, `yazdir.en_kucuk_yazi_pt_pdf` |
| Demo anahtar | 127 | 127 | demo `script#kaynak` `anahtarlar` |
| Korunan 10, döngü başı | 1580,0; 0; 0; 0; 0; 1,517; 3,64; 2,21; 574,3; 0 | aynı | `git show 93da9af:planlama/d158/regresyon.json` (2026-11-08T20:20:13) |
| Korunan 10, son koşu + eşik | 1580,0; 0; 0; 0; 0; 1,519; 3,64; 2,21; 574,3; 0 · eşik 1,5 / 3 / 2 / 400 | aynı; karşılaştırma 10/10 "aynı" | `regresyon-son-kosu.json` |
| Takvim (6 satır) | hücreler | `proje-plani.md:110-115` ile hücre hücre aynı | eksik 3 satır: O-1 |
| Commit / paket / açık karar | 66 / 36 / 47 | 66 / 36 / 47 | `git rev-list --count 8dcc4eb^..HEAD`, plan, kuyruk |
| Düşük satırları | 3,647°, 0,38 + 0,47 = 0,85 > 0,65 | aynı | `F2-kontrol.md:85-90` |
| | 1,12 / 1,46 / 0,86 / 0,98; stall 30,4 | aynı | `F3a-kontrol.md:28, :53-54` |
| | 12,2 / 5,6 / 2,4 sa | aynı | `F4a-kontrol.md:35` |
| | 0,71 A, %66–68 | aynı | `F4a-kontrol.md:33` |
| | 4,87 A, ≥ 5,85 V | aynı | `F8c-kontrol.md:43, :145` |
| | 15,5° / 8,1° | aynı | `F6a-kontrol.md:130-131` |
| | 0,26 m | aynı | `F8d-kontrol.md:271` (D-10) |
| | 6.063,11 TL (K35) | aynı | `F8a-kontrol.md:213` |

Uyuşmazlık: yalnız 94 ↔ 93 (D-2).

`F9c-uret.py`'yi scratchpad'e yazacak biçimde koştum (`CIKTI` değiştirildi). Çıktı depodaki `sonuc-rapor.html` ile **bayt bayt aynı** (129.077 bayt).
Yani rapor elle düzenlenmemiş. Totoloji incelemesi: D-1.

### 3. Karar kuyruğu
- **Sayım:**
  - özet tablosu 52 satır, 52 benzersiz;
  - **açık 47**, kapalı 5 (K5, K8, K15, K16, K17);
  - gövde başlığı 52; KAPANDI başlığı 5;
  - "**Açık: 47** … **Kapandı: 5** … Toplam 52" satırı aynı.
  - Not: K7'nin gövdesindeki "Durum: yer kapandı" özet tablosundaki "açık" ile ayrışıyor. Bu fark F9c'den önce de vardı; rapor K7'yi "yalnız ifade
    (yer kapandı)" diye doğru anlatıyor.
- **`git diff`:** +55 / −1 satır. Değişenler:
  - özet tablosunda K51 ve K52 satırları;
  - "Açık: 45 → 47, Toplam 50 → 52" satırı;
  - P9.3 kaynak notu (2 satır);
  - gövdede `## K51` ve `## K52`.

  Başka madde değişmemiş. Satır sonları korunmuş (diff yalnız bu satırlar).
- **K51 kaynakları:**
  - `F7c-gunluk.md:215` (KT-F7c-2 başlığı) ve `:216-222`;
  - `maliyet.json:103`: adet 2, 6,05 TL, Direnc.net, "dogrulandi", F8a S15, stok 1.210;
  - `robot-bom.csv:144`: "P6KE6V8A TVS (kafa ekrani 5 V);1";
  - `elektrik.md:47` (Pi hattı, 2,67 A hesap), `:49` (QLED hattı), `:282` ("her iki 5 V çıkışına").

  Hepsi birebir. Seçenekler a / b / c, varsayılan a, etki (0 TL; c'de −6,05 TL), bloke ve durum tam. Uydurma fiyat yok.
- **K52 kaynakları:**
  - `F7c-gunluk.md:224` (KT-F7c-3 başlığı) ve `:225-231`;
  - `elektrik.md:62`: göğüs dalı satırı (atıf `:60-62`, 60 boş, 61 kod çiti; kabul edilebilir);
  - `elektrik.md:41` ve `:377` (×5, beşincisi göğüs);
  - `maliyet.json:190`: LM2577 + LM2596, 275,67 TL;
  - `maliyet.json:122`: yuva adet 5, 36,72 TL; notta 4 kullanım: A, B, C, XT60 şarj;
  - `maliyet.json:123`: 2 A mini, 7,34 TL; notta "F5 2 A standart", göğüs anılmıyor → kuyrukta "doğrulanmadı";
  - `robot-bom.csv:113` (6 yollu kutu) ve `:137` (30 A yuva). Regülatör, mini 2 A ve hat yuvası BOM'da yok.

  Hepsi doğru. Kart ölçüsü "doğrulanmadı" diye işaretli. Fiyatlar yalnız var olan satırlardan; uydurma yok.
- **Rapor ↔ kuyruk:** 47 satırın "Önerilen varsayılan" ve "Beklettiği" sütunları kuyruk özet tablosuyla **47/47 birebir**.
- **Aciliyet:** A 20 + B 13 + C 14 = 47. Savunulabilir; tek öneri D-4 (K3 → B).

### 4. Açık düşükler (örneklem 9 kontrol dosyası)
Okunan dosyalar: F5b, F9a, F6b, F8a, F3a, F2, F7b, F7c, F7d (son iki elektrik için tam tarandı). Ayrıca F4a, F4c, F6a, F8c, F8d, F1b'de satır
atıfları örneklendi.

| Dosya | Açık kalan | Raporda | Sonuç |
|---|---|---|---|
| F5b | D7/D8 isteğe bağlı (kabul) | dışarıda (eylemsiz); ölü adam "F5b :23" elektrik satırında | doğru |
| F9a | küçük not 2 (sıkıştırma "varsayım" işaretsiz); not 1 kapalı (`proje-plani.md` 10.12 / 24.12 / 7.01 / 21.01 düzeltilmiş) | not 2 var (F9a :212–214) | doğru |
| F6b | D-6 (`F4c-liste.py:164-167` sabit sayılar: hâlâ var), D-7 (bilgi) | D-6 var, D-7 dışarıda | doğru |
| F8a | T1-5, D3, akü stok, QLED stok | var (F8a :34, :215, :261); K30 Limacell elektrik grubunda | doğru |
| F3a | Madde 8, 15, :109–112; koşul 1–5 C'de | var | doğru |
| F2 | B-1, B-2, B-4, B-5, B-7; B-3, B-6 P6.1'de kapandı | var | doğru |
| F7b | son karar: D-1', D-3, D-6, D-10, D-11, D-12 → F7c; D-9 → K47 | dışarıda (kapandı), K47 kuyrukta | doğru |
| F7c | O-1/O-2 kapandı; 6 düşük → F7d; KT-F7c-2/-3 → K51/K52; **KT-F7c-1 açık** | **yok** | **O-2** |
| F7d | D-2', D-3, D-8, D-9; K50 doğrulanmadılar | var | doğru |

Kapanmış olup açık görünen satır bulmadım. Örnekler (hâlâ açık oldukları doğrulandı):
- README "Kafa grubu 1.570,8 g" (`README.md:44`);
- `tasarim/freecad/README.md:47-48` `$USERPROFILE` tırnaksız;
- README "Bu sürüm `lale-duzeltme` dalında" (`:21`);
- `arayuz.py:18` 1,65 m yorumu;
- `rehber-veri.json`'da "önceden" 0 kez.

Elektrik güvenliği grubu, KT-F7c-1 dışında tam.

### 5. Ahmet'in yapacakları
Liste tam:
- karar maddeleri (20 öncelikli);
- `main` / Pages (Ahmet onayı, KT-F9b-1);
- silme işleri (K48, özel sayfa);
- `.gitignore` (K47, K49);
- Efe'den #5, #6, #7 (+ K14, K44).

`main`, silme ve `.gitignore` onaylarının Ahmet'te kaldığı açık. İfade düzeltmeleri D-3'te.

### 6. Demo
- `demo_uret.py`'yi scratchpad'e yazacak biçimde koştum (`DEMO` değiştirildi, göreli model dosyalarının yalnız varlığı için scratchpad'de boş taslak).
- Çıktı: 127 anahtar, 14 karar, 153 kalem. Depodaki demoyla **bayt bayt aynı** (`cmp` 0; sha256 `e0cc5ff4e5a7…`).
- HEAD ↔ çalışma ağacı: dosya boyu aynı (168.056 bayt). Tek fark bölgesi (12 bayt): gömülü `karar-kuyrugu.md` izi `ba78d2666dfe` → `27e97f88e0ac`.
  Bugünkü kuyruğun sha256'sı `27e97f88e0ac`. Fark yalnız kuyruk izi.
- `F9b-dogrula.py` 0 (GECER; 1400 ve 360 px konsol 0).

### 7. Sayfa
- **Kendi CDP betiğim** (Node, headless Chrome, `file://`, ayrı scratchpad profili):
  - 1400 px: innerWidth = scrollWidth = clientWidth 1400;
  - 360 px: 360 = 360 = 360;
  - konsol, istisna, yükleme hatası **0**;
  - sayfa dışına taşan öğe 0; iç kaydırması olan tablo 0.
- **Kendi bağlantı sayımım:**
  - 81 `href`/`src`: göreli dosya 71 (33 benzersiz), çapa 10, dış 0;
  - **kırık 0** (çapalar dahil);
  - git'te izlenmeyen hedef 3 (`F9c-brief.md`, `F9c-gunluk.md`, `sonuc-rapor.html`), üçü de commit listesinde.
  - A'nın "dış bağlantı 10" dediği, aslında bu 10 çapa.
- **Ekran görüntüleri:** scratchpad'de 13 görüntü aldım. Bakılanlar:
  - 360 üst (kartlar sığıyor);
  - 360 koyu tema (okunaklı);
  - 360 takvim (ilk satır "Taban", O-1'i doğruluyor);
  - 1400 kararlar ("KOD" kırılıyor, D-7);
  - 1400 paketler (hash'ler ve rozetler doğru).

### 8. Bütünlük
- `carpisma_kos.py kontrol`: 0. Regresyon `--yazma`: 0.
- Commit listesi (17 dosya + bu dosya) taraması:
  - takma ad 0 (takma ad `git remote get-url origin` sahibinden ve kullanıcının lakap biçiminden çalışma anında türetildi; adlar hiçbir yere yazılmadı);
  - başka öğrenci / danışman soyadı 0 (liste `tubitak-2209b/BAGLAM.md` §6'dan çalışma anında; ≥ 3 harf);
  - yerel kullanıcı yolu 0;
  - artifact adresi 0.
  - Pozitif kontroller: soyad listesi BAGLAM'da 11 eşleşme buldu; takma ad biçimleri `tasarim/freecad/index.html` ve `CLAUDE.md`'de bulundu (K25 / K26
    dosyaları).
- A'nın listesi 16 dosya, çalışma ağacıyla tam:
  - `F9c-*` 14 (brief, gunluk, uret, dogrula, dusukler, 8 PNG) + `sonuc-rapor.html`;
  - izinle değişen 2: `karar-kuyrugu.md`, demo.
- Eklenecekler: `dongu-158.md` ve bu dosya (`F9c-kontrol.md`).
- Dışarıda kalacaklar:
  - 13 kabuk PNG, `yerlesim-kontrol.json`;
  - `F5-pano-govde.txt`, `F5b-pano-govde.txt`, `FREECAD-KILIT.txt`;
  - `kvkk/`, `rapor/`, `raporlar/…`, `tubitak-2209b/`, `tasarim/solidworks/`;
  - `lale158-model.js`, `lale_dongu*`, `kafa-yerlesim/kaynak/`.

## Ölçümler: komut ve çıkış kodu

Hepsi depo kökünden, `PYTHONIOENCODING=utf-8`, `py -3 -B`. "scratchpad" = oturumun geçici klasörü.

| # | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 1 | `git status --porcelain` (başta; her ölçümden sonra `diff`) | 0 | her seferinde aynı |
| 2 | `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | **0** | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 3 | `py -3 -B planlama/d158/regresyon.py --yazma` | **0** | GEÇER, 10/10 aynı (taban 2026-11-09T14:30:50) |
| 4 | `demo_uret.build()`, `DEMO` → scratchpad | 0 | 127 anahtar, 14 karar, 153 kalem |
| 5 | `cmp scratchpad/demo.html tasarim/Robot-Tasarim-Demosu.html` | **0** | bayt bayt aynı |
| 6 | `git show HEAD:tasarim/Robot-Tasarim-Demosu.html` + bayt farkı (Python) | 0 | 1 bölge, kuyruk izi; `sha256sum karar-kuyrugu.md` → `27e97f88e0ac` |
| 7 | `py -3 -X utf8 -B planlama/d158/F9b-dogrula.py` | **0** | GECER (hata 0), konsol 0, 360 px |
| 8 | `F9c-uret.main()`, `CIKTI` → scratchpad; `cmp` | 0 / **0** | rapor bayt bayt aynı |
| 9 | `py -3 -B planlama/d158/F9c-dogrula.py` | **0** | GEÇER (takma ad / soyad ortam değişkeni verilmedi; onları ayrı taradım, #14) |
| 10 | `node scratchpad/cdp.mjs <chrome> file:///…/sonuc-rapor.html scratchpad` | 0 | konsol 0, 1400 / 360 kaydırma 0, taşan 0, 13 PNG |
| 11 | bağlantı sayımı (Python, `os.path.exists` + `git ls-files --error-unmatch`) | 0 | 71 göreli, kırık 0, çapa 10/10 |
| 12 | `git log --format=%h 8dcc4eb^..HEAD`, `git rev-parse --verify` (118 hash) | 0 | 66/66, bulunamayan 0, döngü dışı 0 |
| 13 | plan ↔ rapor durum karşılaştırması; kuyruk sayımı; rapor ↔ kuyruk sütunları (Python) | 0 | 36/36; 47/52; 47/47 |
| 14 | `py -3 scratchpad/tara.py <17 dosya>` (+ pozitif kontrol) | 0 | takma ad 0, soyad 0, yol 0, artifact 0 |
| 15 | `py -3 -B planlama/adim5/maliyet_toplam.py`; Decimal ile ayrı hesap | 0 | 118.666,22 / 124.573,11 / 93.770,47 / 102.071,11 |
| 16 | `git diff --stat`, `git diff planlama/d158/karar-kuyrugu.md planlama/dongu-158.md` | 0 | kuyruk +55/−1 yalnız K51/K52 |
| 17 | headless Chrome süreç denetimi (`Win32_Process`, "headless") | 0 | kalan süreç 0 |

## A için düzeltme (dar)
1. **O-1:** `F9c-uret.py` takvim döngüsü. Önce `bas + 1`'den başla; sonra boş hücreyi koruyan bölme. Bu ikisiyle 9/9 satır gelir.
   `F9c-dogrula.py`'ye takvim satır sayısı denetimi ekle.
2. **O-2:** `F9c-dusukler.json` elektrik grubuna KT-F7c-1 satırı (yukarıdaki metin). Elektrik 18, toplam 47 olur. Günlük §6'daki "TVS kutbu (→ F7c)"
   dışlamasını düzelt.
3. İsteğe bağlı, aynı turda:
   - D-2: 94 → 93, kaynak `F8a-rapor.html:90` ya da `sayac`;
   - D-3: K49 ve K48 ifadeleri, K47 atfı;
   - D-7;
   - D-8 niteleyicisi;
   - D-1 altbilgi metni.
4. Yeniden üret ve koş: `F9c-uret.py`, `F9c-dogrula.py --goruntu` 0. 8 PNG yenilenir (düşükler bölümü değişir). Ardından `kontrol` 0, regresyon 0.

B dar yeniden kontrol yapar:
- takvim 9/9;
- elektrik 18;
- düşük toplamı;
- bayt bayt yeniden üretim;
- konsol, bağlantı, 360 px.

## C için kesin `git add` listesi (18 dosya; A'nın düzeltmesi ve B'nin yeniden kontrolünden sonra geçerli)

```
git add planlama/d158/F9c-brief.md planlama/d158/F9c-gunluk.md planlama/d158/F9c-uret.py planlama/d158/F9c-dogrula.py planlama/d158/F9c-dusukler.json planlama/d158/F9c-kontrol.md planlama/d158/sonuc-rapor.html planlama/d158/F9c-goruntu-1400-ust.png planlama/d158/F9c-goruntu-1400-kararlar.png planlama/d158/F9c-goruntu-1400-paketler.png planlama/d158/F9c-goruntu-1400-dusukler.png planlama/d158/F9c-goruntu-360-ust.png planlama/d158/F9c-goruntu-360-kararlar.png planlama/d158/F9c-goruntu-360-paketler.png planlama/d158/F9c-goruntu-360-dusukler.png planlama/d158/karar-kuyrugu.md tasarim/Robot-Tasarim-Demosu.html planlama/dongu-158.md
```

C'ye notlar:
- **`dongu-158.md`:** kilit satırı ve P9.3 durumu C'nin kaydında güncellenir. O zaman `F9c-uret.py` yeniden koşmaz: rapor çalışma ağacındaki P9.3 🔄 ile üretildi
  ve bunu "bu paket" diye açıklıyor.
- **Öncesinde koşulacaklar:** `F9c-dogrula.py` 0, `F9b-dogrula.py` 0, `cmp` (demo üretimi = depo).
- **Commit yapmaya ilişkin:**
  - `LF → CRLF` uyarıları bilgi amaçlı;
  - `git add -A` kullanılmaz;
  - commit öncesi checkout, reset ya da stash yapılmaz (F6a D-7).
- **Commit dışı:** 13 kabuk PNG'si ve `yerlesim-kontrol.json`.

## Commit mesajı önerisi

Üç commit (önceki paketlerin düzeni):

1. `Lale P9.3: sonuç raporu ve Ahmet'e özet (sonuc-rapor.html: 36 paket, açık karar 47/52, aciliyet 20/13/14, açık düşük 47 (elektrik 18), korunan değer 10/10); F9c-uret.py, F9c-dogrula.py (F9c)`
   - Dosyalar: `F9c-*` (kontrol dahil), `sonuc-rapor.html`, 8 PNG.
   - Not: düşük sayısı A'nın düzeltmesinden sonraki değerle yazılır.
2. `Lale P9.3: karar kuyruğu K51–K52 (Pi hattında ikinci P6KE6V8A; göğüs regülatörü + mini 2 A + hat sigortası yuvası), demo kuyruk izi`
   - Dosyalar: `karar-kuyrugu.md`, `tasarim/Robot-Tasarim-Demosu.html`.
3. `Lale P9.3: planlama`
   - Dosya: `dongu-158.md`.

Mesajlarda kişi adı yalnız gerekirse "Ahmet"; takma ad, yerel yol ya da artifact adresi yok.

---

# Yeniden kontrol (düzeltme 1): B, 09.11.2026

Kapsam: A'nın `F9c-gunluk.md` §12 notları ve orkestratörün altı maddesi. Her şeyi yeniden kendim ölçtüm. Bozma testleri sayfanın ve düşük JSON'unun
scratchpad'deki kopyalarında yapıldı. Depoya yazılan tek dosya bu. `git status --porcelain` bu turun başında ve sonunda aynı.
Turun başında yalnız şu dosyalar yeniydi: A'nın 2 takvim PNG'si ve bu dosya.

## Karar: **GEÇER**

O-1 ve O-2 kapandı. İlk turun D-1…D-10 bulguları kapandı ya da günlükte sınırıyla yazıldı. Bu turda kritik ve orta bulgu yok; yeni düşük 1 (D-11).
Bu düşük commit'i engellemez.

## Madde sonuçları

| # | Denetim | Bağımsız ölçüm | Sonuç |
|---|---|---|---|
| 1 | Takvim | `proje-plani.md:107-117` kendi ayrıştırmamla okundu (kalın yazım temizlendi), sayfa tablosu `tablo.py` ile çıkarıldı. Başlık + 9 satır ↔ başlık + 9 satır, **hücre farkı 0**. İlk satır "Teslim (stoklu)", son satır "Kesinti 2 + 3 ile (≈ −1 hf)"; "H15–16'ya sığıyor mu" var. 1400 ve 360 px görüntülerde 9 satır görünüyor | **GEÇER** (O-1 kapandı) |
| 1b | F9 özeti | Özet satırı: "Takvim: S = 16.11 yalnız durum A'da sığar (bir hafta tampon)". Kaynak `proje-plani.md:119`: "**S = 16.11:** **yalnız durum A'da** sığar (bir hafta tampon)". Tablonun altında kaynak cümle tam alıntı | GEÇER |
| 2 | KT-F7c-1 | Satır: F7c :269–278, "doğrulanmadı", OBSOLETE (Diodes DS21502), üretici doğrulanmadı, E3a önerisi uygulanmadı, sipariş öncesi satıcı teyidi (K51 bağı). `F7c-kontrol.md:269-278` ve `F7c-gunluk.md:203-213` ile tutarlı. JSON 47 satır (elektrik 18, diğer 29); sayfa başlıkları 47 / 18 / 29 | **GEÇER** (O-2 kapandı) |
| 3a | P8.1 | "136 satırın 93'ü tam doğrulandı (86 onaylı + 7 onaylı olmayan)". `F8a-siparis.json` sayaç 86 + 7 ve `F8a-rapor.html:90` ile aynı | GEÇER (D-2) |
| 3b | K3 ve gruplar | K3 B'de, gerekçesi "Güvenlik sınırı: elde yükle rampa payı 1,5'in altına iniyor". Gruplar A 20 / B 14 / C 13 = 47 | GEÇER (D-4) |
| 3c | "Ahmet'in yapacakları" | Kararlar karar diye değil, öneri diye yazılmış: K47 / K48 / K49 "önerilen varsayılan"; K48 "yalnız Ahmet'in onayıyla"; ".gitignore değişikliği Ahmet'in kararından sonra"; K18–K24 bağı yalnız K49'da; `main` "Ahmet'in onayına bağlı". Karar verilmiş gibi okunan ifade kalmadı | GEÇER (D-3) |
| 3d | Diğer düşükler | Sipariş toplamının niteleyicisi + kararsız hariç tutar (D-8). P0.2 ve P0.3 yalnız `93da9af`, `c1bb4ed` (D-6). P6.1 hücresindeki tek backtick gitti, "KOD" başlığı kırılmıyor (D-7). K32 / K36 / K45 gövde önerisi madde gövdesiyle birebir (D-5). F8d `:271` (D-10). Altbilgi sınırlarını söylüyor (D-1). Özel sayfa F6b B'ye bağlı (D-9) | GEÇER |
| 3e | KT-F9b-3 / KT-F9b-4 (orkestratör kararı) | Gerekçe `F9c-gunluk.md:170-173` (§6) ve `:224-226` (§7 madde 9) var: "iş, karar değil", `F9b-gunluk.md` §8'de açık, sahipleri belli. `F9b-gunluk.md:162`, `:173` ile tutarlı | yazılı; bulgu sayılmadı |
| 4 | Doğrulamanın bağımsızlığı | Bozma testleri aşağıda; istenen üç bozma da yakalandı | GEÇER (not D-11) |
| 5 | Üretim ve bütünlük | Sonuçlar aşağıda | GEÇER |
| 6 | Kuyruk ve demo | sha256: `karar-kuyrugu.md` `27e97f88e0ac`, demo `e0cc5ff4e5a7`. İkisi de ilk kontroldeki değerle aynı, bu turda değişmemiş. `git diff` kuyruk için yine +55/−1 | GEÇER |

## Bozma testleri (`F9c-dogrula.py --tarayicisiz`, kopyalarda)

Betik `scratchpad/enjeksiyon.py`. Sayfa ve gerektiğinde `F9c-dusukler.json` kopyalandı; modülün `SAYFA` / `DUSUK` değişkenleri kopyaya
yönlendirildi.

| # | Bozma | Çıkış | Yakalayan denetim |
|---|---|---|---|
| 0 | bozma yok (temel) | 0 | — |
| 1 | takvim hücresi 29.11 (H9) → 28.11 (H9) | **1** | [5b] takvim satır 2 + [3] data-kaynak |
| 1b | takvim hücresi → 13.12 (H11) (kaynakta başka yerde geçen değer) | **1** | yalnız [5b] takvim; eski [3] bunu kaçırırdı |
| 1c | takvim satırı "Teslim (stoklu)" silindi | **1** | [5b] "kaynak 10 satır, sayfa 9" |
| 2 | P8.1 93 → 94 | **1** | [2] data-h `p81_dogrulanan` + [5b] P8.1 sayaç |
| 3 | KT-F7c-1 satırı silindi (yalnız sayfa) | **1** | [5b] "düşük elektrik: sayfa 17, JSON 18" |
| 3b | KT-F7c-1 satırı silindi (sayfa + JSON) | **1** | [2] data-h düşük sayıları (47 ↔ 46, 18 ↔ 17) |
| 3c | KT-F7c-3 / K52 satırı silindi (sayfa + JSON) | **1** | [2] data-h düşük sayıları |
| 4 | P1.4 🟡 → ✅ (satır durumu) | **1** | [5] "durum hücresi plandaki 🟡'yi içermiyor" |
| 3d | KT-F7c-1 tutarlı biçimde silindi (sayfa + JSON + başlık sayıları; ilk turdaki gibi satır hiç üretilmemiş) | **0** | **yakalanmadı** → D-11 |

### D-11 (düşük, yeni). KT kapsam denetimi günlük §6'daki herhangi bir geçişle yetiniyor
- [5b] bir KT kodunu "karşılandı" saymak için kodun düşük JSON'unda, kuyrukta ya da günlük §6'da geçmesini yeterli buluyor.
- KT-F7c-1 §6'da iki kez geçiyor; ikisi de "satır olarak eklendi" açıklaması (`F9c-gunluk.md:164`, `:180`). Bu yüzden satır hem sayfadan
  hem JSON'dan tutarlı biçimde silinince denetim 0 dönüyor (test 3d).
- Yani O-2'deki türden bir eksik bugün de yakalanmazdı. Yakalanması için şunlardan biri gerekir:
  - günlük §6'da kodun yer aldığı ayrı bir "dışarıda bırakılanlar" listesi aranmalı;
  - ya da açık düşük için JSON'un `kod` alanına bakılmalı.
- Bugünkü rapor doğru (KT-F7c-1 satırı var, 23 KT kodunun dağılımı düşükte 4, kuyrukta 16, §6'da 3). Engelleyici değil; sonraki pakette düzeltilebilir.
- A da bu sınırı günlük §12'de "kapanmış düşükleri ayırt etmez" diye kısmen yazmış.

## Ölçümler: komut ve çıkış kodu (bu tur)

| # | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 1 | `git status --porcelain` (başta ve sonda `diff`) | 0 | aynı |
| 2 | `F9c-uret.main()`, `CIKTI` → scratchpad; `cmp` depodaki `sonuc-rapor.html` | 0 / **0** | **bayt bayt aynı**. Paket 36, commit 66, bulunamayan hash 0, eşleşmeyen commit 0, karar 52 / 47 |
| 3 | `py -3 -B planlama/d158/F9c-dogrula.py` (tarayıcı dahil) | **0** | takvim 9/9 hücre farkı 0; P8.1 93; düşük 47; KT 23; bağlantı 71 / kırık 0, çapa 10 / hedefsiz 0; konsol 0; 360 px 0 |
| 4 | `py -3 scratchpad/enjeksiyon.py` | 0 | 8/8 bozma yakalandı, 3d yakalanmadı (D-11) |
| 5 | `node scratchpad/cdp2.mjs` (kendi headless Chrome'um, `file://`) | 0 | 1400 ve 360 px: innerWidth = scrollWidth = clientWidth; taşan 0; konsol 0; 13 görüntü (scratchpad); 1400-takvim, 360-takvim, 1400-kararlar gözle incelendi |
| 6 | Kendi bağlantı sayımım (Python) | 0 | 81 href / src: 71 göreli (33 benzersiz), 10 çapa, dış 0; kırık 0 |
| 7 | `py -3 -B tasarim/freecad/carpisma_kos.py kontrol` | **0** | 17 özet kayıtla aynı |
| 8 | `py -3 -B planlama/d158/regresyon.py --yazma` | **0** | GEÇER, kötüleşen yok |
| 9 | `py -3 -X utf8 -B planlama/d158/F9b-dogrula.py` | **0** | GECER (hata 0) |
| 10 | `py -3 scratchpad/tara.py` (20 dosya; takma ad, lakap, soyad, yol, artifact) | 0 | hepsi 0 |
| 11 | `sha256sum karar-kuyrugu.md Robot-Tasarim-Demosu.html`; `git diff --stat` | 0 | değişmemiş (madde 6) |
| 12 | headless Chrome süreç denetimi | 0 | kalan süreç 0 |

## C için kesin `git add` listesi (20 dosya)

```
git add planlama/d158/F9c-brief.md planlama/d158/F9c-gunluk.md planlama/d158/F9c-uret.py planlama/d158/F9c-dogrula.py planlama/d158/F9c-dusukler.json planlama/d158/F9c-kontrol.md planlama/d158/sonuc-rapor.html planlama/d158/F9c-goruntu-1400-ust.png planlama/d158/F9c-goruntu-1400-kararlar.png planlama/d158/F9c-goruntu-1400-takvim.png planlama/d158/F9c-goruntu-1400-paketler.png planlama/d158/F9c-goruntu-1400-dusukler.png planlama/d158/F9c-goruntu-360-ust.png planlama/d158/F9c-goruntu-360-kararlar.png planlama/d158/F9c-goruntu-360-takvim.png planlama/d158/F9c-goruntu-360-paketler.png planlama/d158/F9c-goruntu-360-dusukler.png planlama/d158/karar-kuyrugu.md tasarim/Robot-Tasarim-Demosu.html planlama/dongu-158.md
```

Commit dışında kalacaklar:
- 13 kabuk PNG'si ve `tasarim/freecad/montaj/yerlesim-kontrol.json` (K23);
- `F5-pano-govde.txt`, `F5b-pano-govde.txt`, `FREECAD-KILIT.txt`;
- izlenmeyen klasörler (`kvkk/`, `rapor/`, `raporlar/…`, `tubitak-2209b/`, `tasarim/solidworks/` …);
- `tasarim/cad/lale158-model.js` (K48).

C'ye notlar:
- **`dongu-158.md`:** P9.3 durumu ve kilit satırı C'nin kaydında güncellenir. Rapor yeniden üretilmez; raporun 🔄'ı "bu paket" diye açıklanıyor.
- **Commit öncesi:** `F9c-dogrula.py` 0, `F9b-dogrula.py` 0, `kontrol` 0, regresyon 0.
- **Commit yapmaya ilişkin:** `git add -A` kullanılmaz; checkout, reset ya da stash yapılmaz.

## Commit mesajları

1. `Lale P9.3: sonuç raporu ve Ahmet'e özet (sonuc-rapor.html: 36 paket, açık karar 47/52, aciliyet 20/14/13, açık düşük 47 (elektrik 18), takvim 9 satır, korunan değer 10/10); F9c-uret.py, F9c-dogrula.py (F9c)`
   - Dosyalar: `F9c-*` (kontrol dahil, 10 PNG), `sonuc-rapor.html`.
2. `Lale P9.3: karar kuyruğu K51–K52 (Pi hattında ikinci P6KE6V8A; göğüs regülatörü + mini 2 A + hat sigortası yuvası), demo kuyruk izi`
   - Dosyalar: `planlama/d158/karar-kuyrugu.md`, `tasarim/Robot-Tasarim-Demosu.html`.
3. `Lale P9.3: planlama (döngü sonu)`
   - Dosya: `planlama/dongu-158.md`.

Mesajlarda takma ad, yerel yol ve artifact adresi yok.
