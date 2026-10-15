# G: dirsek kelepçesi + eski sınır kodu (düzeltme planı 1. adım, tasarım ajanı)

Başlangıç: 14 Ekim 2026. Git commit yok, tam çakışma taraması ve ana montaj koşulmaz.

## Durum
- [x] 1 Dirsek bilezik kelepçesi: mekanizma doğrula, yarık, kapanma kontrolü
- [x] 2 Eski sınır kodu -> arayuz.OMUZ (dirsek_montaj tork, iskelet_montaj ızgara, eklem_dogrulama, montaj_gorsel)
- [x] 3 Kontrol tutarlılığı (omuz kanal tabanı >= 0,5; iskelet köşe M6 >= 0,5)
- [x] 4 Kabuk cam boşluğu geometriden ölçülsün

## Günlük
- Başladı. CLAUDE.md, README, V-dogrulama, A1, A2 okundu.
- Mekanizma (dirsek_parcalar.py:97-116): pim r 25,4 (çatalla tek parça), tüp duvarı r 25,65-28,0, bilezik iç r 28,25; halka oluğu (pim ile bilezik arası) y -140…-114'e kesilmiş -> tüp gerçekten pim ile bilezik arasında, V oluğa dayanıyor. Yarık x 184-186 (2 mm), kulaklar x 178-192, M3x20 cıvata y -121/-132, z TZ-36.
- Yarık 2 mm -> kapanınca ic yarıçap 2/(2π) = 0,318 mm iner; toplam radyal boşluk 0,5 -> tüp pime hiç bastırılamıyor (yalnız 0,07 mm bilezik-tüp sıkışması, V-dogrulama). Mekanizma sorunu DOĞRU.
- Karar: yarık 2 -> 4 mm (arayuz.DIRSEK['bilezik_yarik']). Kapanma 4/(2π)=0,637 mm; 0,5 + 0,1 ön yük = 0,6 -> kalan ön yük 0,137. Neden bu: bilezik/tüp/pim boşlukları (0,25) A1'de baskı toleransı için açılmıştı, geri almak M2'yi bozar; yarığı büyütmek yalnız ince bir malzeme kesimi (kulaklar 6 -> 5 mm, geometri yalnız eksilir, yeni çakışma imkansız). Kulaklar tam değince durur -> ön yük geometriyle sınırlı (aşırı sıkma yok).
- arayuz.py: DIRSEK'e bilezik_yarik=4.0, bilezik_on_yuk_min=0.1 eklendi. dirsek_parcalar.py: yarık genişliği arayüzden. dirsek_montaj.py: kalıcı kontroller (yarık geometriden ölçülür, kapanma >= boşluk + ön yük; vida boyu/somun/kayan kulak çakışması).
- (G burada Windows güncellemesiyle kesildi, 14 Ekim ~13:12. Devralan: tasarım ajanı, 14 Ekim akşamı.)

## Devralma (14 Ekim 2026, akşam)
- Kontrol: `git diff` + G'nin adım kaydı karşılaştırıldı. Yarım kalan dosya YOK: arayuz (bilezik_yarik, bilezik_on_yuk_min), dirsek_parcalar (yarık arayüzden), dirsek_montaj (kelepçe kontrolleri, `_izgara`), iskelet_montaj (`_izgara` + köşe M6 ≥ 0,5; ilk denemesi AssertionError ile düştü, ikinci `rep` denemesi CRLF'i koruyarak uygulanmış), omuz_montaj (`M6_TABAN_PAY_MIN`) tam ve sözdizimi doğru. `eklem_dogrulama.py`, `montaj_gorsel.py`, `kabuk_montaj.py` yalnız okunmuştu, hiç değişmemişti. Satır sonları korunuyor (arayuz/iskelet/omuz/montaj CRLF; dirsek_montaj, dirsek_parcalar, kabuk_montaj LF, bunlar G'den önce de LF idi).
- Madde 2 tamamlandı: `montaj/eklem_dogrulama.py`: `Y0 = arayuz.OMUZ["yana_aralik"][0]`; sınır içi vakalardaki tüm "yana 0" pozları (POZ 4, DPOZ 5, iki kol 1, kafa+kollar 1, taban+kollar 1) → Y0 (3°). Sınır dışı listesine (0, 0) eklendi (mekanik ev pozu artık sınır dışı). `montaj/montaj_gorsel.py`: Kollari_oynat yana formülü `Y0 + (1,2 − Y0)/2·(1 − cos)` (3,0…68,75°, eski 0…68,75°); poz-önü görseli yana 0 → Y0; pozda verilmeyen kol yana Y0; yeni `animasyon_kontrol()` her karede (161 kare) eklem sınırlarını ve kafa-kol yasak kutusunu (`arayuz.KAFA_KOL_YASAK`) denetler, ihlalde betik durur. GUI gerektirdiği için koşulmadı; kontrol işlevi sistem Python'unda ayrı denendi: 0 ihlal (öne −34,4…103,2, yana 3,0…68,8, dirsek 0…103,1, bilek ±68,8, pan ±45,8, tilt ±14,3; kutu koşulu öne ≥ 120 ve tilt ≥ 20 hiç oluşmuyor).
- Madde 4 tamamlandı: `kabuk_montaj.py` cam boşluğu artık geometriden: cam kutusu (`K.EO["cam"]`, w = PCB önü…0, `K.EKM`) ↔ göğüs çevresindeki gövde parçaları `distToShape`; `bosluk.cam_duvar_mm` + en yakın 3 parça + şart (≥ 0,05, temas yok). Sonuç kabuk koşusunda (aşağıda).
- Koşular: `dirsek_montaj.py` (31 s): geçersiz 0, ev pozu çakışma 0, omuz arayüzü 0, bağlantı 22/22, kelepçe kontrolleri geçti (aşağıdaki tablo); çatal 88,78 → 88,21 g, modül 368,7 → 368,1 g; tork taraması artık S2 3…120 (yüksüz S1 8,02 → 7,99 kg·cm). `iskelet_montaj.py` (12 s): 59 parça, çakışma 0, bağlantı 12/12, bölge ihlali 0, köşe M6 8/8 (somun payı 0,6, tabana 1,9, şart 0,5); en kötü durum ızgarası artık öne −45…135 × yana 3…120: direk σ 0,931 → 0,911 MPa, travers aynı, tepe sehim 0,166 mm aynı.

## Kelepçe: G'nin kararı ve benim değerlendirmem
| | önce | sonra |
|---|---|---|
| Yarık (geometriden ölçülen) | 2,0 mm | **4,0 mm** (`arayuz.DIRSEK["bilezik_yarik"]`) |
| Kapanınca iç yarıçap düşüşü | 0,318 mm | **0,637 mm** (yay boyu ile: 28,250 → 27,613) |
| Toplam radyal boşluk (pim–tüp 0,25 + bilezik–tüp 0,25) | 0,50 | 0,50 |
| Kalan ön yük (şart ≥ 0,1) | −0,18 (tüp pime hiç bastırılamıyor) | **+0,137 mm** ✓ |
| Kulaklar (x 178…192) | 6 mm + 6 mm | 5 mm + 5 mm; kapanınca kayan kulak çakışması 0 mm³ |
| M3×20 cıvata | — | kapalı hâlde uç somundan taşar (≥ 0,5), somun dişli boy içinde, somun/pul çatalın kalanına ≥ 1 mm: 22/22 bağlantı geçti |
| Çatal kütlesi | 88,78 g | 88,21 g (M1 oluğuyla 87,49 g) |
- Katılıyorum (4 mm yarık, M2'nin 0,25 boşluklarını geri almadan, yalnız malzeme çıkararak, kulaklar değince ön yük geometriyle sınırlı). İki çekincem kontrolün idealize olduğunu gösteriyor, ikisi de baskı kuponunda (M7: tüp-bilezik geçme halkası) ölçülmeli:
  1. Bilezik kökü alın kapağına bağlı (yarık y −140'ta bitiyor): kapanma kökte sıfır, uçta en büyük. Alt cıvata (y −132) köke 8 mm yakın; ortalama kapanma 0,637'nin altında kalır. Hesap tüm halkanın düzgün kapandığını varsayıyor.
  2. Tüpün pime değmesi için PETG tüpün çevresel olarak ~%0,9 sıkışması gerekir; gerçekte tüp ovalleşip pime yer yer değer. Kelepçenin asıl tutuşu bilezik–tüp sürtünmesi, pim yalnız merkezleme ve eğilme desteği.
- Kontrolün yeri: `dirsek_montaj.py` "omuz_arayuzu.kontroller" (yarık geometriden, kapanma ≥ boşluk + ön yük) + "sikma_bilezigi" + kelepçe cıvatası kontrolleri; `dirsek-analiz.json`.

## Sonuç (14 Ekim, gece)
| Madde | Sonuç |
|---|---|
| 1 Kelepçe | yukarıdaki tablo; kalıcı kontrol geçti |
| 2 Sınırlar | dirsek tork ızgarası S1 −45…135 / S2 3…120 (`_izgara`, `A.OMUZ`); iskelet en kötü durum ızgarası aynı kaynaktan (15°); `eklem_dogrulama.py` sınır içi pozlarda yana alt sınır 3° (`Y0`), (0, 0) sınır dışı listesinde; `montaj_gorsel.py` Kollari_oynat yana 3,0…68,8°, poz görselleri Y0, `animasyon_kontrol()` 161 karede sınır + kafa-kol yasak kutusu: 0 ihlal (sistem Python'unda denendi; GUI betiği koşulmadı) |
| 3 Kontrol tutarlılığı | omuz kanal tabanı ≥ 0,5 (4/4: 1,7 / 0,8); iskelet köşe M6 ≥ 0,5 (8/8: somun payı 0,6, tabana 1,9) |
| 4 Cam boşluğu | `kabuk_montaj.py` cam kutusu ↔ gövde parçaları `distToShape` (aşağıdaki koşu) |
- Koşulan: dirsek_montaj (M1 ile birlikte, son koşu 56 s), iskelet_montaj (12 s), omuz_montaj (39 s, M1 tüp penceresiyle), kabuk_montaj (aşağıda). `dirsek_rapor.py` yeniden üretildi. Koşulmayan: montaj_gorsel (GUI), eklem_dogrulama ve ana montaj (6. adım), carpisma.
- Açık: `montaj/montaj_gui_kontrol.py` sınır beklentisi (dokunma yetkim yoktu) yana 0 içeriyorsa 6. adımda bakılmalı; rapor metinlerindeki "yana 0…120" (A2'nin listesi) belge adımında.
- Kabuk koşusu (`kabuk_montaj.py`, 8 dk, 15 Ekim gecesi): cam–duvar **0,102 mm geometriden ölçüldü** (en yakın: omuz bandı sağ/sol ve göğüs bandı, üçü de 0,1022; şart ≥ 0,05 geçti; eski elle yazılı formülle aynı değer, artık ölçüm). Diğer kontroller değişmedi: geçersiz 0, kabuk içi çakışma 0, iskelet 0, bindirme 0,1881 (21 çift), baskı 15/15. Kabuk geometrisi bu adımda değişmedi (194 parça, 4.886 g).
