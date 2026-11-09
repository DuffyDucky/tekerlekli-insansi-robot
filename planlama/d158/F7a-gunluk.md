# F7a günlüğü: 3B montaj rehberi 1,58 m modelinden (P7.1), 09.11.2026

Brief: `planlama/d158/F7a-brief.md`. Rehber günlüğü: `planlama/rehber/R-gunluk.md` (durum kutuları güncellendi).
Paralel paket F6b'nin alanına (baski_*, y2, baski-listesi, F4c-*, F6b-*) dokunulmadı.

## Kabul

| Ölçüt | Sonuç | Kaynak |
|---|---|---|
| 48 + F5 adım (+ hazırlık) | **50 adım** = 0 hazırlık + M6 tablosunun 48 satırı + F5 | `rehber/veri/rehber-veri.json` `adimlar` |
| Her model parçası tam bir adımda | **geçti**: 1192 parçanın her biri tam bir adımda "yeni" görünüyor; birden çok adımda 0, hiç görünmeyen 0, atanmamış 0 | `planlama/rehber/kontrol.json` `ozet.her_parca_tek_adimda`, `ozet.atanmamis` |
| Konsol hatası 0 | **0** (50 adımın hepsinde `data-hata` yok, `data-hazir="1"`) | `kontrol.json` `ozet.konsol_hatasi` |
| `kontrol.json` tüm adımlarda geçer | **50 / 50** | `kontrol.json` `ozet.gecen`, `sonuc[*].gecti` |
| Veri 1,58 modelinden | `kaynak.cad`: iskelet 14:27, omuz 14:27, kabuk 14:28, dirsek 14:28, taban 14:29, kafa 08:54 (09.11) = F6a'nın yazdığı modül FCStd'leri; FCStd'ler HEAD (a051281) ile aynı (git status'ta değişmemiş) | `rehber-veri.json` `kaynak.cad`, `ls --full-time tasarim/freecad/*/*-montaj.FCStd` |
| `carpisma_kos.py kontrol` 0 | **0** ("izlenen 17 dosyanin ozetleri kayitla ayni"), başta ve sonda | 15:43 ve 16:02 koşuları |
| `regresyon.py --yazma` 0 | **0** ("Sonuç: GEÇER (hepsi okundu, kötüleşen yok)"), başta ve sonda | 15:43 ve 16:02 koşuları |

## Komutlar (saat, çıkış kodu, bellek)

| Saat | Komut | Çıkış | Not |
|---|---|---|---|
| 15:43 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | başlangıç |
| 15:43 | `py -3 planlama/d158/regresyon.py --yazma` | 0 | GEÇER (başlangıç) |
| 15:44 | FreeCAD salt okuma parça dökümü (geçici betik, depo dışında; `m6_yukle.yukle` ile aynı kural) | 0 | kilit F7a; boş bellek 2,40 GB; 1192 parça. Seçicileri FreeCAD'siz denemek için |
| 15:54:09–15:54:34 | `python tasarim/freecad/rehber/rehber_uret.py --gorsel-yok` | 0 | kilit F7a; boş bellek 2,37 GB; veri 25 s |
| 15:55 | `... rehber_uret.py --veri-yok --adimlar 35` | 0 | tek adım deneme |
| 15:56–15:58 | `... rehber_uret.py --veri-yok` (50 adım) | 0 | 50 / 50; ardından F5 kamerası eklendi (aşağıda) |
| 15:59:50–16:02:45 | `python tasarim/freecad/rehber/rehber_uret.py` (tek komut: veri + 50 adım) | **0** | kilit F7a; boş bellek 2,21 GB; veri 22 s; "50 adim, 50 gecti, 0 sorunlu, konsol hatasi 0; her parca tek adimda: True" |
| 16:02 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | son |
| 16:02 | `py -3 planlama/d158/regresyon.py --yazma` | **0** | son, GEÇER |

Her FreeCAD koşusundan önce: çalışan `freecadcmd` / `FreeCAD` süreci 0, boş bellek ≥ 2 GB, `FREECAD-KILIT.txt` boş; koşu boyunca
"F7a <saat> <komut>", bitince "boş". Dosya başta yoktu (oluşturuldu, silinmedi).

**Kilit olayı:** 15:54:34'te "boş" yazdım; dosya 15:55:39'da kendiliğinden eski içeriğe ("F7a 2026-11-09 15:54 ...") döndü. Çalışan
FreeCAD yoktu; içerik bu paketin kendi satırıydı. Büyük olasılıkla OneDrive eşitlemesi eski sürümü geri yazdı. 15:59'da bayat kilit
olarak üzerine yazdım; 16:02:45'te "boş", 16:02:55'te yeniden okundu: "boş". F6b de aynı dosyayı kullandığı için bu geri dönme onu
bekletebilir: kilit dosyası OneDrive dışında olmalı ya da yazdıktan sonra birkaç saniye beklenip yeniden okunmalı (öneri).

Tek komut koşusunda kilit tarayıcı bölümü boyunca da (≈ 3 dk) tutuldu; FreeCAD yalnız ilk 22 s'te çalıştı.

## Seçiciler (iş 1)

Yer: **`tasarim/freecad/rehber/rehber_secici.py`** (yeni, saf Python). `rehber_veri.py` artık `M6_erisim.py`'yi exec etmiyor; bunu import ediyor.

Gerekçe (daha az iz): `M6_erisim.py` 125 cm erişim analizidir; `M6_erisim_sonuc.json` ve `M6-montaj-sirasi.md` tablosu o seçicilerle
üretildi. Seçicileri orada değiştirmek, analizi 1,58 m'de yeniden koşmadan (FreeCAD, uzun, paylaşılan makine) betik, JSON ve tablo
üçlüsünü birbirinden koparırdı. Rehberin kendi katmanında değiştirmek yalnız rehberi etkiliyor. `M6_ek.py` adım ataması yapmıyor
(yalnız ölçüm), dokunulmadı. `M6_erisim.py`, `M6_ek.py`, `M6_erisim_sonuc.json` değişmedi.

125 cm seçicilerine göre değişen atamalar (parça adedi):

| Eski → yeni | Adet | Parçalar | Kaynak |
|---|---|---|---|
| F2 / F3 → C1 | 8 | M5 perçin somun (8 braket) | braketle birlikte çakılır (R-gunluk C1 metni) |
| F5 → F2 | 4 | gövde uzatma bandı 1 ve 2, sağ + sol | dikişler y 476,5 / 634 / 791,5 |
| F3 / F4 → F2 | 22 | y 792 dikişi (6 cıvata + 6 ısıl gömme), x = 0 dikişi y 771 / 862 / 952 (4 + 4), y 688 braketi M5×18 (2) | etiket ve y |
| F4 → F3 | 10 + 8 | y 1005 dikişi, x = 0 cep altı / üstü (y 1022,7, 1222), y 1095 M5×18 | `lale158_rapor.py` bağlantı tablosu |
| F4 → F5 | 14 | üst arka kapak bindirme 7 + ısıl gömme 7 | kapak F5'te |
| F1 → F5 | 18 | etek servis kapağı H1, H2 + 8 cıvata + 8 ısıl gömme | R-gunluk F5 metni ("etek H1 ve H2") |
| F5 → F2 | 9 | hoparlör, kap (ön halka, arka), kelepçe, köpük ped, 2 × M3×20, 2 ısıl gömme | `kabuk_parcalar.py:730` orta bant sağ ön duvarı |
| (F5'te kaldı) | 2 | 4'lü USB hub + köpük bant | üst arka kapak içi (`kabuk_parcalar.py:912`) |
| B1a / B3 / X → B5a | 26 | XL4016 C, ön şarj kartı (X idi: atanmamış), 8 naylon burç, 8 M3×8, 8 M3×6 | güç paneli katında (y > 170; R-gunluk B5a) |
| B2a → B2 | 4 | teker eksenel M4 pulu | teker adımı |
| E2 → E2c | 13 | boyun yükseltme adaptörü, 4 M3 saplama DIN 976, 4 pul, 4 DIN 985 | `kafa10_lib.py` başlık notu |
| E2b → E2 | 1 | kafadaki 625ZZ iç bilezik (tilt pimi, çatal yanağı); E2b yalnız 6808 iç bilezikleri (tur 1, O-1) | M6 E2 "Tilt servosu + 625ZZ + M5 pim" |
| B5a → F1 | 1 | ana anahtar ASW-A01 gövdesi (tur 1, O-2) | `taban_parcalar.py:10`, `:392`, `:444` (etek plakası altı) |
| E3a → E4 | 47 | QLED + 4 tırnak + 4 tırnak cıvatası + 4 tırnak ısıl gömme + 4 köpük; kamera + 4 vida; ReSpeaker + 3 vida; USB ses kartı, PAM8403 + 2 köpük; tabla cıvatası 4 + raf ısıl gömme 4; kabuk dikişi ısıl gömme 9 | `kafa10_lib.py` BAG: yüz / arka kabuğa bağlananlar |

Brief'teki listeye göre: braket eşiği 8 braket (C1: 8 braket + 16 M6 + 16 çekiç somun + 8 perçin somun), etek M3×14 (F1, 6),
gövde uzatma bandı (F2), H1 / H2 (F5), üst arka kapak hub takozlu (F5, hub dahil), dolgu şeritleri (F1, 2), göğüs ekranı çerçevesi
sağ / sol + VESA taşıyıcı + M6 / M4 / pul / çekiç somun (F3), omuz göbeği dişi (G0: F2 durdurucusu `omuz_parcalar.py:213` göbeğe
fuse edilmiş, ayrı parça değil; "Omuz gobegi" G0'da), QLED kafa parçaları (E4).

### Parça sayımı (model ↔ rehber)

| Modül | Model (FCStd, `m6_yukle` kuralı) | Rehber (`rehber-veri.json`) | Fark |
|---|---|---|---|
| iskelet | 59 | 59 | 0 |
| omuz_sag / omuz_sol | 73 / 73 | 73 / 73 | 0 |
| kabuk | 357 | 357 | 0 |
| dirsek_sag / dirsek_sol | 57 / 57 | 57 / 57 | 0 |
| kafa | 161 | 161 | 0 |
| taban | 355 | 355 | 0 |
| **Toplam** | **1192** | **1192** | **0** |

Tür: Bağlantı 893, Satın 210, Baskı 72 (baskı listesiyle aynı), Lazer 3, İmalat 1, Referans 13 (12 kablo şeması: K1'de 7, K2'de 5; ana
anahtar düğmesi gösterimi F1). Gerekçeli hariç tutma (`m6_yukle.HARIC`, eskisi gibi): omuz dosyasındaki "Omuz traversi" kopyası ve
"Govde kabugu yan yuzu (referans)", sağ + sol 4 nesne (asılları iskelet A3'te ve kabukta).

Adım başına yeni görünen parça (kontrol.json, düzeltme turu 1'den sonra; "alt" = o adımda robota bağlanan tezgâh alt montajı):
A1 29, A2 15, A3 15, B1a 46, B1 28 + alt 46, B2a 28, B2b 20, B2 16, B3 28, B4 24, C0 30, B5a 39, B5 8 + alt 39, B6a 80, B6 8 + alt 80,
B7 14, K1 7, C1 48, D1a 22, D1b 20, D1c 4, D1 16 + alt 46, E1a 27, E1 6 + alt 27, E2a 2, E2b 7, E2c 18, E2 14, E3a 23, E3 4 + alt 23,
E4 60, K2 5, F1 62, F2 87, F3 54, F4 18, G0 16, G1 14 + alt 16, G2 28, G3 26, G4 12, H0a 42, H0b 4, H0c 28, H0d 4, H0e 10, H0f 10,
H1 16 + alt 98, F5 50. Toplam 1192. (16:02 koşusunda B5a 40, B5 alt 40, E2b 8, E2 13, F1 61 idi; aşağıda "Düzeltme turu 1".)

## Üretim (iş 2)

`rehber/veri/`: `rehber-veri.json` (420 kB), `rehber-veri.js`, `robot.glb` 2,56 MB (288 benzersiz mesh, 189.934 üçgen), `robot-glb.js`
3,4 MB. Veride yeni alanlar: `kaynak.secici`, `atanmamis` (boş), adım başına `kamera`.

## Göğüs ekranı (iş 3)

Ayrı adım açılmadı: kabul "48 + F5 adım" ve M6 F3 satırı zaten "göğüs bantları + Nextion". F3 = "Göğüs bantları + göğüs ekranı":
bant → VESA taşıyıcı (2 × M6×18 + pul + çekiç somun, direk ön kanalı, cepten) → ekran (4 × M4×12 + pul, arkadan, üst arka kapak
açıkken) → çerçeve sağ + sol (8 × M3×6 ISO 7380 → ısıl gömme). F3 "Notlar"da doğrulanmadı işaretli 6 madde: sıra kaynakta yok; VESA
delik yeri ve vida derinliği; taşıyıcı ↔ K2 kafa 12 V hattı çakışması; port yeri; HDMI boyundan / dokunmatik hub'dan (teyit yok);
12 V dalı giriş noktası ve acil stop (elektrik.md K11). K2 metnine madde 6 (göğüs ekranı HDMI + 12 V uçları) ve not eklendi.
Kaynaklar: `tasarim/freecad/lale158/lale158_rapor.py` bağlantı tablosu ve açıklar, `lale158/kablo_yolu_ekran.py`, `planlama/adim3/elektrik.md`.

## Uygulama (iş 4)

`rehber/app.js`, `index.html`, `stil.css`: "M6 tablosu:" → "Bağlantı:"; M6 kırmızı kutusu (`m6-uyari`), `SINIF.m6`, satır / etiket
M6 işaretleri ve `tr.m6` stili kaldırıldı; lejant boşsa gizlenir; `not_` sarı çizgili "Notlar" kutusunda (md biçimli); "Erişim notu (M6)"
→ "Erişim notu"; adım `kamera: "arka"` ise görünüm arkadan (F5'te arka kapaklar önden görünmüyordu). Kontrol için `?cekim=1`'de
`<script type="application/json" id="kontrol-veri">` içine adımın yeni görünen parça kimlikleri (simdi / alt), hedef sayısı ve mesh'i
olmayanlar yazılır. Satır sonları CRLF korundu.

`rehber_uret.py`: kontrol artık bu veriyi `rehber-veri.json`'dan beklenen listeyle karşılaştırır, tüm adımlar koşulunca her parçanın tam
bir adımda göründüğünü denetler; headless Chrome ayrı profil (`%TEMP%/lale-rehber-chrome`) ile açılır (açık Chrome'a bağlanmasın).
`rehber_metin.py`: F3, K2, F5 (`kamera`), hazırlık "65 parça" → "72 parça" (baskı listesi 72), F7a başlık notu, TR sözlüğüne 1,58 m kelimeleri.

## Kontrol ve görüntüler (iş 5)

`planlama/rehber/kontrol.json` (16:02; tur 1'den sonra 16:30, sonuç aynı): 50 adım, 50 geçti, konsol hatası 0, her parça tek adımda: true. Görüntüler
`planlama/rehber/goruntu/adim-00.png` … `adim-49.png` (50 dosya; 8'i 15.10'dan güncellendi, 42'si yeni).

Gözle bakılanlar (16 adım): 00 (hazırlık, bitmiş robot), 01 (A1 şase), 12 (B5a güç paneli: XL4016 C + ön şarj kartı panelde), 18 (C1,
8 braket + perçin somun), 22 (D1 omuz), 27 (E2c adaptör + saplamalar), 29 (E3a tabla), 31 (E4: QLED, kamera, ses kartı, PAM, ReSpeaker),
32 (K2 kablo şemaları + göğüs ekranı uçları metni), 33 (F1 ilk kabuk: etek + dolgu şeritleri, H1 / H2 delikleri açık), 34 (F2: uzatma
bantları, hoparlör ızgarası), 35 (F3 göğüs ekranı + Notlar), 36 (F4 omuz bantları), 42 (H0a dirsek tezgâhı), 48 (H1 dirsek → tüp),
49 (son, F5: arka + üst arka kapak + etek kapakları, arkadan). Hepsi doğru adımda; 49 kamera düzeltmesinden sonra yeniden bakıldı.
Düzeltme (tur 1, F7a-kontrol D-2): 49 dışındaki 15 görüntüye 15:56 koşusunun çıktısında bakıldı. Depodaki PNG'lerin hepsi son tam
koşudan: 16:02 koşusunda 16:00:16–16:02:45; düzeltme turu 1'den sonra 16:28:06–16:30:57 (aşağıda). Veri de her tam koşuda yeniden üretildi.

## M6-montaj-sirasi.md için öneri (dosya değiştirilmedi)

Tablo hâlâ 125 cm. Rehber `rehber_metin.py` ile üstünü örtüyor; tablo güncellenirse: C1 "8 gövde braketi (y 400 / 530,25 / 687,75 / 1095),
16 × M6×14 + 16 çekiç somun, 8 M5 perçin somun"; F1 "6 bant + 2 dolgu şeridi; 6 × M3×14 ISO 7380 dışarıdan"; F2 "+ uzatma 1 / 2,
hoparlör; M5×18 dışarıdan (y 400 / 530 / 688)"; F3 "göğüs bantları + göğüs ekranı (taşıyıcı 2 × M6×18, kasa 4 × M4×12, çerçeve 8 ×
M3×6)"; E2c "adaptör + 4 M3 saplama + pul + DIN 985"; E3a / E4 kafa (QLED yüz kabuğunda); F5 "+ üst arka kapak (hub), etek H1 / H2".

## P7.2'ye kalanlar

1. **Kafa metinleri** (E3a, E4; R-gunluk 4): E3a metni hâlâ "kamera" ve "model 7", LCD satırı" diyor; kamera, QLED, tırnaklar, ReSpeaker,
   USB ses kartı, PAM8403, tabla → raf cıvataları artık E4'te görünüyor. E3a'da kalan: kafa iskeleti, Pi 5 + burç + vidalar, D24V50F5,
   SY8205, TVS (+ köpük), tilt horn + vida, 625ZZ. E4 `baglanti_md`'si QLED tırnakları, kamera ve ReSpeaker vidalarını saymıyor. Ayrı
   kafa ekranı adımı (E3a–E4 arası) istenirse adım sayısı 51 olur.
2. **Ses:** hoparlör grubu F2'de görünür, F2 metninde yok; PAM8403 → hoparlör kablosu.
3. **Hub:** 4'lü hub + köpük bant F5'te görünür, F5 metninde yok; hub uzatması, göğüs dokunmatiği ve ESP32 USB bağlantıları.
4. **K2 metni madde 3** ("ESP32 USB … direk ön yüzü → boyun") 05.11 B kararıyla çelişiyor (ESP32 USB hub'dan çıkar,
   `kablo_yolu_ekran.py:6`, `elektrik.md:37`). Taban kablo şeması 8'in adı ("kafada 5 V/5,5 A çevirici (Pi 5, LCD)") eski; yollar
   `taban_parcalar.py`'de (tarama kaynağı değilse orada düzeltilmeli).
5. `lale158/kablo_yolu_ekran.py` göğüs ekranı yolları rehber şemasına girmedi.
6. **Parça listesi gruplama** (R-gunluk sıradaki 3): aynı kod bir satırda, ilk parçanın adıyla: F2 "Gövde alt bandı sağ ×11" (bantlar +
   hoparlör kabı), H0a "Dirsek servosu MG996R ×4" (dirsek + bilek), F5 "Arka servis kapağı ×4", F1 "Etek arka sağ ×8". Yanıltıcı.
7. TR sözlüğü eksikleri ("mantari", "cikis", "govdesi" ASCII kalıyor).
8. Yazdırılabilir sürüm (madde C), telefon görünümü (390 × 844), bazı adımlarda yakın kadraj (R-gunluk sıradaki 2).
9. `M6_erisim.py` 1,58 m'de koşulmadı: erişim sınıfları 125 cm'den. Yeniden koşulursa ADIMLAR `rehber_secici.py`'den alınmalı.

## Açıklar

- Göğüs ekranı montaj sırası kaynakta yok; F3'teki sıra erişim notlarından çıkarıldı, doğrulanmadı (metinde işaretli).
- Yargıya dayanan atamalar (kaynakla gerekçeli ama montajda denenmedi): ısıl gömme somunlar bağlı oldukları cıvatanın adımında (etek
  H1 / H2 kapak ısıl gömmeleri fiziksel olarak etek plakasında ama F5'te listeleniyor; kafa dikiş ısıl gömmeleri E4'te); kamera E4'te
  (yüz kabuğuna vidalı); hoparlör F2'de; hub F5'te.
- `FREECAD-KILIT.txt` OneDrive'da geri döndü (yukarıda); F6b'ye haber verilmeli.
- Kafa adımlarının metni görünen parçalarla şu an uyumsuz (P7.2 madde 1).

## Dokunulan dosyalar (commit listesi)

- `tasarim/freecad/rehber/rehber_secici.py` (yeni)
- `tasarim/freecad/rehber/rehber_veri.py`
- `tasarim/freecad/rehber/rehber_metin.py`
- `tasarim/freecad/rehber/rehber_uret.py`
- `rehber/app.js`, `rehber/index.html`, `rehber/stil.css`
- `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js`, `rehber/veri/robot.glb`, `rehber/veri/robot-glb.js` (üretilen)
- `planlama/rehber/kontrol.json`, `planlama/rehber/goruntu/adim-00.png` … `adim-49.png` (50; üretilen)
- `planlama/rehber/R-gunluk.md`
- `planlama/d158/F7a-gunluk.md` (yeni)
- `planlama/d158/F7a-brief.md` (paketin brief'i; önceki paketlerin brief'leri gibi commit'e girer)

Commit dışı: `planlama/d158/FREECAD-KILIT.txt` (koordinasyon dosyası, paylaşılan; içerik "boş"). `planlama/d158/F7a-kontrol.md` B'nin
dosyası; commit'e girip girmeyeceği orkestratörün kararı.

Değişmedi: `planlama/adim4/M6_erisim.py`, `M6_ek.py`, `M6_erisim_sonuc.json`, `M6-montaj-sirasi.md`, tarama kaynakları, model dosyaları.
Depo dışı: geçici döküm betiği (oturum karalama klasörü), Chrome profili `%TEMP%/lale-rehber-chrome`.

## Düzeltme turu 1 (09.11.2026 16:20–16:40; kaynak `planlama/d158/F7a-kontrol.md`)

| Madde | Değişiklik | Dosya |
|---|---|---|
| O-1 | E2b'deki "ic bilezik" eşleşmesi yalnız 6808'ler (`_ve(_ad("6808"), _ad("ic bilezik"))`); kafadaki 625ZZ iç bilezik Pan grubunun genel satırıyla E2'ye düştü (E2 metni "Karşı yanağa 625ZZ ve M5 pimi tak") | `rehber_secici.py` E2b satırı |
| O-2 | "Ana anahtar ASW" ikinci B5a satırından çıkarıldı, F1 satırına eklendi. Ayrıca ilk B5a satırına (Guc_aku, y > 170) `_degil(_ad("Ana anahtar"))` eklendi: gövde y 216…256 olduğu için o satır da yakalıyordu (FreeCAD'siz benzetimle görüldü) | `rehber_secici.py` B5a, F1 satırları |
| O-2 metin | B5a: M6 `is_`'i ezen yeni `is_` (ana anahtar yok, F1'e yönlendirme); kontrol maddesinden ana anahtar çıktı. F1 madde 4: gövde etek üst plakasının altına, acil stobun karşısına (yer öneri, bağlantı elemanı modelde yok, doğrulanmadı) + K1 uçlarını bağla. K1 madde 1: ana anahtar uçları bırakılır, F1'de bağlanır | `rehber_metin.py` |
| D-6 | "(M6 erişim notuna bak)" → "(erişim notuna bak)" (bayt düzeyinde, CRLF korundu) | `rehber/app.js:294` |
| D-2 | Görüntü saatleri düzeltildi (yukarıda "Kontrol ve görüntüler"); `R-gunluk.md` "12 görüntü" → "16 görüntü" | bu dosya, `R-gunluk.md` |
| §7 | Commit listesine `F7a-brief.md` eklendi; `FREECAD-KILIT.txt` commit dışı | bu dosya |

Komutlar:

| Saat | Komut | Çıkış | Not |
|---|---|---|---|
| 16:25 | FreeCAD'siz seçici benzetimi (karalama betiği, 15:44 parça dökümü üzerinde) | 0 | 625ZZ → E2, ana anahtar → F1 (ilk B5a satırı düzeltmesinden sonra) |
| 16:27:34–16:30:57 | `python tasarim/freecad/rehber/rehber_uret.py` | **0** | kilit "F7a düzeltme turu 1 16:27"; öncesinde kilit "boş", FreeCAD süreci 0, boş bellek 2,55 GB; veri 28 s; "50 adim, 50 gecti, 0 sorunlu, konsol hatasi 0; her parca tek adimda: True"; sonra kilit "boş" |
| 16:32 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | **0** | "izlenen 17 dosyanin ozetleri kayitla ayni" |
| 16:32 | `py -3 planlama/d158/regresyon.py --yazma` | **0** | "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)" |

Adım sayıları (yeni görünen parça):

| Adım | Önce (16:02) | Sonra (16:30) |
|---|---|---|
| 12 B5a | 40 | 39 |
| 13 B5 (alt montaj) | 8 + alt 40 | 8 + alt 39 |
| 26 E2b | 8 | 7 |
| 28 E2 | 13 | 14 |
| 33 F1 | 61 | 62 |

Toplam 1192 ↔ 1192 (model ↔ rehber), atanmamış 0, birden çok adımda 0, hiç görünmeyen 0. `kontrol.json` 50/50, konsol hatası 0.
`kaynak.cad` değişmedi (iskelet / omuz 14:27, kabuk / dirsek 14:28, taban 14:29, kafa 08:54).

Gözle bakılan görüntüler (16:28–16:30 koşusu):
- **12 B5a:** güç paneli; sigorta kutusu, röle, ana sigorta yuvası, XL4016 C, ön şarj kartı; ana anahtar yok, metin F1'e yönlendiriyor.
- **26 E2b:** boyun mili + 6808 iç bilezikleri + 4 M3×8; havada halka yok, kadraj mile oturdu.
- **28 E2:** tilt servosu + 625ZZ iç bilezik + M5 pim, pul ve ısıl gömme; listede 625ZZ var.
- **33 F1:** etek; listede "Ana anahtar ASW-A01 govdesi" ve madde 4'ün yeni metni.

Kalan küçük not: parça adı "govdesi" ASCII kalıyor (TR sözlüğü eksiği, P7.2 madde 7).
