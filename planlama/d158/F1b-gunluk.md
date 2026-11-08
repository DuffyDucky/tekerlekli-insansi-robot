# F1b günlüğü (P1.1, P1.4, P1.5) — tasarım ajanı A, 08.11.2026

Brief: `planlama/d158/F1b-brief.md`. Plan: `planlama/dongu-158.md` §3 F1. Karar kuyruğu: `planlama/d158/karar-kuyrugu.md`.
Dal `lale-duzeltme`. Kısaltmalar: `TF/` = `tasarim/freecad/`, `KY/` = `TF/lale158/kafa-yerlesim/`, `SP/` = oturum scratchpad klasörü (depo dışı,
`C:\Users\Victus\AppData\Local\Temp\claude\6eb585d8171c6c4f\bc1094ac-141c-42e4-99c1-30e40153afa9\scratchpad`). Önceki durumun kopyaları `SP/f1b/once/`.
FreeCAD 1.1, başlatıcı `C:\Users\Victus\.robot-cad\run_fc.py` (`FC_SCRIPT=<betik> freecadcmd.exe run_fc.py`).

## Başlangıç (23:34)
- `py -3 planlama/d158/regresyon.py --yazma` (23:34:51, taban 23:29:59): çıkış 0, "GEÇER", 10 değer "aynı".
- Boş bellek 4,96 GB / 15,29 GB; çalışan FreeCAD süreci yok.
- `py -3 TF/carpisma_kos.py kontrol`: "kaynagi eskimis bolumler: omuz" (çıkış 1; F1a sonundaki durum).
- `git status --short` başlangıçta: `dongu-158.md`, `y2/Y2b-ivme.json`, 13 kabuk görseli, `montaj/yerlesim-kontrol.json` değişik (K23 / orkestratör);
  izlenmeyenler K18–K22 klasörleri, `F1a-kontrol.md`, `F1b-brief.md`, F5b dosyaları.

## P1.1 Akü 2,8 → 3,0 kg

**Kaynak:** modelde akü kütlesi tek yerde: `TF/arayuz.py:623` `TABAN["aku"]["kutle_g"]` (taban_parcalar.py:320-321 "Aku LiFePO4 12,8 V (yatik)"
parçası bunu okur). Malzeme listesi v4 (`tubitak-2209b/malzeme-listesi/Lale-malzeme-listesi-2026-11-03-v4.xlsx`, sayfa 1, satır 5, salt okundu):
"Akü 12,8 V LiFePO4 20 Ah: Victron Energy ... BAT512020705", sütunlar Ad / Adet / Satıcı / URL / Birim fiyat / Toplam / Durum; **kütle sütunu yok**.
3,0 kg'nin kaynağı: `planlama/maliyet.json:82` ("... 167 × 181 × 77 mm, 3,0 kg", Victron BAT512020705) ve `raporlar/kaynaklar/06-aku-secimi.md:119`
("3 kg (üretici datasheet; satıcı sayfasında yok)", datasheet bağlantısı aynı dosya :187). Başka sayı yok → 3.000 g.

Değişen: `TF/arayuz.py:623-624` `kutle_g` 2800.0 → **3000.0**; `not_` metni "güncellenmedi" yerine kaynak ve tarih. Akünün yeri/ölçüsü aynı.
`TF/taban/taban_rapor.py` (:344, :515, :537): "model 2,8 kg ... güncellenmedi" cümleleri 3,0 kg'ye (rapor yeniden üretilince çelişmesin diye; yalnız bu üç cümle).
Dokunulmayan eski metinler (tarihçe / başka paket): `TF/lale158/ikinci_ozet.py:143`, `TF/lale158/lale158-regresyon.json:266`,
`TF/lale158/2209b-cad-sonuclar.json:50`, `TF/lale158/qled-cerceve-tasarim-notu.md:129`, `TF/taslak-170/**`, `planlama/adim5/B-malzeme-plan.md:61`.

Zincir (`SP/f1b/zincir_p11.sh`, her adım öncesi boş bellek ≥ 2 GB denetimi, tek FreeCAD süreci; loglar `SP/f1b/<ad>.log`):
| Adım | Komut | Saat | Süre | Çıkış | Boş bellek (başta) |
|---|---|---|---|---|---|
| 1 | `cd TF/taban && FC_SCRIPT=taban_montaj.py freecadcmd run_fc.py` | 23:39:14–23:40:54 | 100 s | 0 | 5,02 GB |
| 2 | `cd TF/montaj && FC_SCRIPT=ana_montaj.py ...` | 23:40:55–23:42:39 | 104 s | 0 | 5,00 GB |
| 3 | `cd KY && FC_SCRIPT=uygulama_ivme.py ...` | 23:42:40–23:43:53 | 73 s | 0 | 4,86 GB |
| 4 | `cd planlama/y2 && FC_SCRIPT=Y2b-ivme.py ...` | 23:43:53–23:45:06 | 73 s | 0 | 4,81 GB |

Yazılan dosyalar: `TF/taban/taban-analiz.json`, `taban-montaj.FCStd`, `taban-montaj.step`, `taban-bom.csv`; `TF/montaj/montaj-analiz.json`,
`robot-montaj.FCStd`, `robot-montaj.step`, `robot-bom.csv`; `KY/uygulama-ivme.json`; `planlama/y2/Y2b-ivme.json`.
K23'ün öteki dosyaları (`TF/montaj/yerlesim-kontrol.json` 03.11 21:23, `TF/kabuk/gorsel/*.png` 03.11) bu zincirde yazılmadı (tarihler değişmedi).

**K23 notu:** `planlama/y2/Y2b-ivme.json` 03.11 ara çıktısıydı (ev kütlesi 25.467,9 g, rampa5_geri 1,564). Hattın kendi betiği
`planlama/y2/Y2b-ivme.py` (uygulama_ivme.py'nin kopyası; yalnız çıktı adı farklı) P1.1 güncel modelle yeniden üretti: artık
`KY/uygulama-ivme.json` ile aynı sayılar (ev 26.115,6 g, rampa5_geri 1,519). Karar kuyruğu K23'e not düşüldü.

Öncesi / sonrası (öncesi `SP/f1b/once/`, sonrası depo; özet betiği `SP/f1b/p11_ozet.py`, çıktılar `SP/f1b/p11_once.txt`, `p11_sonra.txt`):
| Değer (JSON : anahtar) | Önce | Sonra |
|---|---|---|
| Akü parçası (`taban-analiz.json` `parcalar[Aku LiFePO4 12,8 V (yatik)].kutle_g`) | 2.800,0 g | **3.000,0 g** |
| Taban modülü (`taban-analiz.json` `kutle_g` / `kutle_payli_g`) | 7.909,8 / 8.309,8 g | 8.109,8 / 8.509,8 g |
| Ana montaj (`montaj-analiz.json` `kutle_g`) | 25.515,59 g | **25.715,59 g** |
| Ana montaj AM (`montaj-analiz.json` `agirlik_merkezi`, x; y; z) | (−0,026; 531,557; −8,377) | (−0,026; **528,457**; −9,256) |
| Robot, ev pozu, kablo payı dahil (`uygulama-ivme.json` `ev.kutle_g`) | 25.915,6 g | **26.115,6 g** |
| AM yüksekliği, ev (`uygulama-ivme.json` `ev.am[1]`; taban-analiz `robot.pozlar[ev].am[1]`) | 525,71 mm (525,6) | **522,71 mm** (522,7) |
| AM z, ev (`uygulama-ivme.json` `ev.am[2]`) | −9,17 | −10,03 (akü arkada: AM 0,86 mm arkaya) |
| Statik devrilme açısı ev, ileri / geri / yan (`taban-analiz.json` `robot.pozlar[ev].duz.statik_egim_*`) | 20,3 / 18,5 / 22,3° | **20,5 / 18,5 / 22,5°** |
| Statik devrilme açısı, "geri" pozu (kollar −45°) ileri / geri / yan | 20,8 / 17,8 / 22,2° | 20,9 / 17,8 / 22,4° |
| Statik devrilme açısı, "one_yuk" (kollar önde + 0,5 kg) ileri / geri / yan | 16,9 / 19,6 / 21,0° | 17,1 / 19,6 / 21,2° |
| Devrilme ivmesi ev, düz ileri / geri / yan (`uygulama-ivme.json` `ev.duz`) | 3,623 / 3,281 / 4,030 m/s² | 3,660 / 3,284 / 4,053 |
| Devrilme ivmesi ev, rampa 5° ileri / geri / yan (`ev.rampa5`) | 2,755 / 2,414 / 3,160 | 2,791 / 2,416 / 3,183 |
| **Rampa yüksüz payı** (`izgara_yuk_0g.a_sinir_pay15.rampa5_geri`, ızgara en kötü) | 1,517 | **1,519** (≥ 1,5 → kabul) |
| Rampa 100 g / 500 g (`izgara_yuk_{100,500}g.a_sinir_pay15.rampa5_geri`) | 1,477 / 1,327 | 1,479 / 1,329 |
| Düz zemin en kötü (`izgara_yuk_0g.a_sinir_pay15.duz_geri`) | 2,095 | 2,097 |
| Fren 1,8 m/s² düz payı 0 / 100 / 500 g (`izgara_yuk_*.fren_pay.duz_min`) | 1,746 / 1,712 / 1,587 | 1,748 / 1,714 / 1,589 |
| `planlama/y2/Y2b-ivme.json` rampa5_geri yüksüz (K23 ara çıktısı → güncel) | 1,564 (03.11 modeli) | 1,519 |

Yorum: akü taban arkasında ve alçakta (y ≈ 133, z ≈ −121): +200 g AM'yi 3,0 mm indirdi, 0,86 mm arkaya aldı; "geri" devrilmesi için
iki etki neredeyse dengelendi (rampa5_geri +0,002), ileri ve yan biraz iyileşti. Rampa ≥ 1,5 → karar kuyruğuna madde gerekmedi.
K3'teki 100 g / 500 g rampa sayıları (1,477 / 1,327) 1,479 / 1,329 oldu; K3'e yalnız yeni sayıları veren bir not eklendi (eski metin
ve seçenekler aynı; < 1,5 sonucu değişmedi, yeni karar maddesi açılmadı).

## P1.4 Göğüs kablo tüpleri

**Önce (HEAD = F1a sonu, `TF/lale158/lale158-kontrol.json` `kablo_tup_cakisma`):** HDMI × "Gogus ekrani 11,6 in HDMI 1920x1080 kasali" 897,1;
12 V × kasa 617,3; USB dokunmatik × kasa 167,6 mm³. SY8205 için plandaki 249,7 mm³ eski: `KY/uygulama-olcum.json` `kablo_sy8205.*` +
`kafa_ici_qled_kablo.*` `sy8205_kesisim_mm3` toplamı 0 (F0 B2.5).

**Yeniden ölçüm** `SP/f1b/p14_olc.py` (freecadcmd, `TF/montaj/robot-montaj.FCStd` P1.1 sonrası, 23:46–23:51, 254,6 s, çıkış 0; sonuç `SP/f1b/p14_olcum.json`).
Tüpler `lale158_kontrol.py` ile aynı kuruldu; kasa göğüs ekranı yerel çerçevesine (`kablo_yolu_ekran.gp`) çevrildi. Bulgular:
- Modeldeki kasa düz kutu: yerel sınır kutusu x ±142,325, y ±91,125, z −31,5…−2,0 (= `arayuz.GOGUS_EKRAN` kasa 284,65 × 182,25 × 29,5, cam_geri 2,0).
  **Port girintisi modelde yok** (`kabuk_parcalar.py:880-881` not: "port girintisi var; dogrulanmadi"). Port duvarı x = −110 (`arayuz.py:346`, "fotoğraftan tahmini").
- Üç kablonun son iki segmenti (`kablo_yolu_ekran.ekran_ucu`): x = −128'de arkadan dikey iniş (z −43,5 → −19,5, 24 mm; kasaya z −31,5'te girer) ve
  port duvarına yatay 18 mm (x −128 → −110). Kasa kesişiminin **tamamı** bu iki segmentte:
  | Kablo (Ø) | Kesit Y | Dikey segment ∩ kasa | Yatay segment ∩ kasa | Toplam | Uç bölgesi içi | Uç bölgesi dışı | Eksen ucu → port duvarı | Eksen ucu port satırında | Bölge dışı tüp → kasa |
  |---|---|---|---|---|---|---|---|---|---|
  | HDMI (6) | 5 | 395,84 | 565,49 | 897,05 | 897,05 | **0,0** | 0,0 mm | evet | 13,614 mm |
  | 12 V (5) | −27 | 268,34 | 386,15 | 617,3 | 617,3 | **0,0** | 0,0 mm | evet | 3,64 mm |
  | USB dokunmatik (4) | −15 | 167,55 | 242,95 | 167,55 (!) | 167,55 | **0,0** | 0,0 mm | evet | 14,806 mm |
  (Segment hacimleri küre uçlarıyla, birbiriyle örtüşür; "Bölge dışı tüp → kasa": tüpün uç bölgesi dışındaki kısmının kasanın bölge dışı kısmına en kısa uzaklığı.)
- **Sınıflandırma: üçü de (i) uç teması**, gerçek çakışma yok. Tüp kasaya yalnız port girintisinin olması gereken yerde (−X kısa kenar ile port
  duvarı arası, port satırı yüksekliğinde) girer ve eksen ucu port duvarında (fiş konnektörde) biter. Tüp kasanın gövdesinden (girinti dışından)
  geçmiyor: bölge dışı kesişim 0, bölge dışındaki tüp kasaya en az 3,64 mm uzak. Kanıt görseli: `planlama/d158/F1b-kablo-kesit.png`
  (her kablonun kendi Y düzleminde ekran yerel kesiti: kasa zarfı, uç bölgesi, tüp; başlıkta son ölçüm). Görsel `SP/f1b/p14_ciz.py` (sistem Python'u, matplotlib).
- **Yan bulgu (ölçüm yöntemi):** USB dokunmatik tüpü ardışık `fuse` ile kurulunca son (yatay) segment kayboluyordu: tüp hacmi 4.742,9 mm³,
  π r² L = 4.958,8 (`SP/f1b/tup_dene.py`); kasa ortak hacmi 167,6 (yalnız dikey segment). Silindir ve uç kürelerini ayrı argüman olarak tek
  `multiFuse` ile kurunca tek katı, 4.966,8 mm³, kasa ortak **391,5** mm³ (`SP/f1b/tup_dene2.py`); öteki kablolarda hacim ve kesişim aynı (HDMI 897,1, 12 V 617,3).
  Yani HEAD'deki 167,6 eksik ölçülmüştü; doğru değer 391,5 ve tamamı uç bölgesinde.

**Düzeltme (ölçüm yöntemi; yol yeniden çizilmedi, geometri değişmedi):**
- `TF/lale158/kablo_yolu_ekran.py`: yeni `EKRAN_PORT_KABLO = ("HDMI", "USB dokunmatik", "12 V")` ve `uc_bolgesi(r)` (FreeCAD'siz, göğüs ekranı yerel kutusu):
  x −kasa/2 − 1 … x_duvar + r (port girintisi + fiş ucu küresi), y port satırı (−33…33), z kasa arkası − 1 … port satırı üstü (cam_geri farkı ekli).
  HDMI x −143,325…−107,0; USB −143,325…−108,0; 12 V −143,325…−107,5; z −32,5…−10,5. Yollar değişmedi (`yollar()` aynı).
- `TF/lale158/lale158_kontrol.py` (CRLF korundu): (1) tüp kurulumu tek `multiFuse` (yukarıdaki yan bulgu); (2) bu üç kablo × ekran kasası kesişimi
  ikiye ayrılır: uç bölgesi içi → yeni `kablo_tup_uc_temas`, dışı → `kablo_tup_cakisma` (eşik yine 0,5 mm³); (3) yeni `kablo_tup_uc_bolgesi`
  (kablolar, yerel kutular, çerçeve, gerekçe) ve `kablo_tup_hacim` (her tüpün hacmi, π r² L, katı sayısı, geçerlilik); `kablo_tup_notu` güncellendi.
  Gerekçe (JSON'a da yazıldı): kasa düz zarf, gerçek kasada portlar −X kısa kenardaki girintide kenara bakıyor; bu bölgedeki hacim fişin
  girintiye girip konnektöre takılmasıdır. Port yeri doğrulanmadığı için bölge de tahmin; port ölçülünce ikisi birlikte güncellenmeli.

**Sonra** `cd TF/lale158 && FC_SCRIPT=lale158_kontrol.py freecadcmd run_fc.py` (00:05:49–00:06:01, 12 s, çıkış 0; log `SP/f1b/lale158_kontrol.log`;
çıktının kopyası `SP/f1b/lale158-kontrol-p14.json`):
| `lale158-kontrol.json` | Önce | Sonra |
|---|---|---|
| `kablo_tup_cakisma.HDMI` × göğüs ekranı kasası | 897,1 | **yok (0)** |
| `kablo_tup_cakisma.12 V` × kasa | 617,3 | **yok (0)** |
| `kablo_tup_cakisma.USB dokunmatik` × kasa | 167,6 | **yok (0)** |
| `kablo_tup_uc_temas` HDMI / USB dokunmatik / 12 V (yeni alan) | — | 897,1 / 391,5 / 617,3 |
| `kablo_tup_hacim` USB dokunmatik (yeni) | (4.742,9, ölçülmüyordu) | 4.966,8 (π r² L 4.958,8), tek katı, geçerli |
| `toplam_boy_mm`, `boy_tamam`, `ekran_cakisma` | 1.580,0, true, [] | 1.580,0, true, [] |
| Öteki girdiler (kafa / boyun; P1.4 dışı, değişmedi) | HDMI × Boyun mili 15,1, × Servo yuvası 1,7; Hub uzatması × Pi 2,9, × Boyun mili 1,2; Hoparlör × Boyun mili 1,2; Ses kartı uzatması × Pi 2,5; Dizi USB × Pi 11,8; 3,5 mm → PAM × PAM8403 2,8 | aynı |
Öteki girdiler kafa/boyun tarafında (Pi portlarına ve PAM'a uç temasları, boyun mili / servo yuvası geçişi); `kablo_tup_notu` "elle bakılmalı" diyor.
Kafa F1a'nın alanı, brief'te yok: dokunulmadı, ayrıştırılmadı (açık).
**SY8205 × kafa kabloları:** `kablo_yolu_ekran.yollar()` değişmedi; `KY/uygulama_olc.py` kabuk koşusundan sonra yeniden koşuldu (aşağıda, regresyon değeri).

## P1.5 Kabuk günlüğü ve rapor

### "Wire is not closed" (16 satır)
`kabuk1.log` (04.11, başka oturumun scratchpad'inde) ve F1a'nın `kabuk_montaj` logunda (`SP/kabuk_montaj.log` satır 1–16) 16 × `<Exception> Wire is not closed.`;
satırlar logun başında görünüyor çünkü stderr tamponsuz, stdout tamponlu (yerini göstermez).
**Tanı** `SP/f1b/tel_ara.py` (freecadcmd, 23:54:32–00:01:21, 409 s, çıkış 0; sonuç `SP/f1b/tel_ara.json`, log `SP/f1b/tel_ara.log`):
`kabuk_montaj.baski_analiz`'in katman döngüsü (parça baskı yönüne çevrilir, 1 mm katman, `s.slice` + `Part.makeFace(ws, "Part::FaceMakerBullseye")`)
34 baskı parçasında aynen koşuldu. Logda yine **16** satır; hepsi `makeFace` çağrısından ("FreeCAD exception thrown (Wire is not closed.)"),
`slice` hiç hata vermedi. Kaynak: **`TF/kabuk/kabuk_montaj.py` `baski_analiz()`**, kesitten gelen telin kapalı olmaması:
| Parça | Katman (baskı z, mm) | Açık tel |
|---|---|---|
| Gövde alt bandı sağ / sol | 217,5; 221,5 | 42 kenarlı tel, uçlar üst üste (aralık 0,0) ama topolojik olarak kapalı değil |
| Gövde uzatma bandı 1 sağ / sol | 73,5 | 26 kenar, 47,0 mm eksik (x ±125, y 0 … ∓47: yan duvar parçası kesitte yok) |
| Gövde uzatma bandı 1 sağ / sol | 161,5; 165,5 | 42 kenar, uçlar üst üste (0,0) |
| Gövde uzatma bandı 2 sağ / sol | 73,5 | 26 kenar, 47,0 mm eksik |
| Gövde orta bandı sağ / sol | 217,5; 221,5 | 38–39 kenar, 6,2 mm eksik (x ±98, y 80,3…86,5) |
Toplam 2+2+3+3+1+1+2+2 = 16. Neden: OCC kesiti bu düzlemlerde teli kapatamıyor (bir kenar eksik ya da başlangıç/bitiş tepe noktaları
ayrı). Hangi yüzün buna yol açtığı (bindirme dili, boss ya da dikiş yüzüne denk gelme olasılığı) **doğrulanmadı**; uzatma bantlarında 161,5 / 165,5
ile alt bantta 217,5 / 221,5 aynı mutlak yükseklikte değil, ortak olan parçanın baskı üst kenarına uzaklık (alt ve uzatma bantlarında 8 ve 4 mm, orta bantta 9,4 ve 5,4 mm). Sonuç: o katman ve bir sonrakinin destek kontrolü atlanıyordu (`yuz = None` → `onceki = None`); destek sorunu yazılmıyordu.
**Deneme** `SP/f1b/tel_dene.py` (freecadcmd, çıkış 0, `SP/f1b/tel_dene.json`): 16 katmanın hepsi düzlem +0,05 mm kaydırılınca kapanıyor; yüz alanları
komşu katmanlarla uyumlu (ör. alt bant sağ 217,5: 613,05 mm², komşular 599,75 / 578,73), logda yeni satır yok.
**Düzeltme** `TF/kabuk/kabuk_montaj.py` `baski_analiz()` (yalnız analiz; kabuk geometrisi değişmedi, `kabuk_parcalar.py` dokunulmadı):
teller kapalı değilse `makeFace` çağrılmaz; düzlem 0,05 / −0,05 / 0,1 / −0,1 / 0,25 / −0,25 mm kaydırılıp yeniden kesilir, kurulan yüz katman
düzlemine geri taşınır (önceki katmanla eş düzlem kesimi bozulmasın); kapanmazsa katman "kesit teli kapanmadi" diye destek sorunu sayılır.
Kaydırılan katmanlar her baskı sonucuna `kesit_kaydirma` [(z, dz)] olarak yazılır. `kabuk_parcalar.py:733` yorumu (72 → 70) **düzeltilmedi**:
kabuk_parcalar.py başka sebeple değişmedi (brief: P6.1'e kalır).

### `kabuk_rapor.py`
Önce: `KeyError: 'ekran_kontrol'` (satır 130); ayrıca `A.NEXTION` (arayuz'da yok, AttributeError olurdu), 125 cm / V3 metinleri (Nextion yuvası,
4 U braket y 400/780, M5×10 + ısıl gömme somun, dikiş 476,5/690/883, "hoparlör ızgarası yok"), `onceki/*.json` ile kabuk öncesi karşılaştırma,
Ekim 2026 omuz/iskelet regresyonu (omuz `fark.json` "FARK"). `kabuk/rapor.html` 14.10'dan ve içinde eski MAX98357A satırı.
Değişiklik (yedek `SP/f1b/kabuk_rapor.ONCE.py`; yama betikleri `SP/f1b/yama_kabuk_rapor1.py`, `yama_kabuk_rapor2.py`, her blok tam bir kez eşleşti):
- Ekran kontrolü `kabuk-analiz.json` `gogus_ekrani`'ndan 7 satırlık tabloya (kasa ↔ direk ≥ 20, kasa ↔ göğüs bandı, kasa ↔ çerçeve, VESA taşıyıcı dayalı,
  çerçeve flanşı dayalı, M6 uç sınırı, aktif alana giren parça 0).
- Bağlantı tablosu veriden: gövde braketleri (`baglanti` tip govde: 8 adet, y400/530/688/1095) ve etek braketleri (6 adet, z −105/0/+105), eleman
  sayımı `baglanti[].eleman`'dan; Nextion satırı yerine göğüs ekranı, hoparlör (kap + kelepçe + 2× M3×20) ve USB hub satırları.
- Kararlar / açık işler 1,58 m'ye: sayılar `arayuz.py`'den (KABUK_T, GOVDE_DIKIS, UZAMA, GOGUS_EGIM, ARKA_KAPAK, M6 arka_kapak_ust, OMUZ_DUVAR,
  UST_KAPAK_ERISIM, BOYUN_ACIKLIK_R, SES_USB) ve `kabuk-analiz.json`'dan; ses düzeni: hoparlör gövde orta bandı sağ, hub üst arka servis kapağı içi,
  PAM8403 + USB ses kartı kafada (K16, K17). Kabuk öncesi karşılaştırma ve eski omuz/iskelet regresyonu çıktı (korunan değerler için `planlama/d158/regresyon.py`'ye atıf).
- Görseller: `kabuk/gorsel/*.png` 03.11 (K23, dokunulmadı); 125 cm'den kalan `kabuk-nextion-on.png` (göğüs değil karın önü) ve `kabuk-nextion-ic.png`
  (%0,2 dolu, boş) rapora alınmadı; öteki 11 görselin altına "03.11 kabuk koşusundan, P6.1'de yenilenecek" notu.
- Deneme koşusu (SP'ye, `py -3 SP/rapor_dene.py kabuk_rapor.py SP/f1b/kabuk-rapor-dene.html`): çıkış 0, 955 kB; metinde (görseller hariç) "V3",
  "HATA", takma ad 0.

### P1.5 koşuları
Önce boş bellek 4,2 GB, FreeCAD süreci yok. `bash SP/f1b/zincir_2.sh kabuk_montaj lale158_kontrol` (çıktı `SP/f1b/zincir_3.out`):
- `cd TF/kabuk && FC_SCRIPT=kabuk_montaj.py freecadcmd run_fc.py`: 00:06:07–01:18:54 (4.367 s), çıkış 0, log `SP/f1b/kabuk_montaj.log`.
  Koşu boyunca boş bellek 2,99–3,48 GB (3 dk'da bir `Win32_OperatingSystem` ile bakıldı).
- Ardından `lale158_kontrol.py` (01:18:55–01:19:08, 13 s, çıkış 0; boş bellek 3,82 GB). `lale158-kontrol.json` P1.4 koşusuyla aynı (`sure_s` dışında fark yok;
  `kablo_tup_uc_temas` 897,1 / 391,5 / 617,3, boy 1.580,0).

Önce/sonra (`SP/f1b/once/kabuk-analiz.json` ↔ `TF/kabuk/kabuk-analiz.json`, karşılaştırma `SP/f1b/p15_karsi.py`):
| Değer | Önce | Sonra |
|---|---|---|
| Logda `Wire is not closed` (`grep -c`) | 16 | **0** (logda exception/error/traceback 0) |
| `baski[].kesit_kaydirma` (yeni) | — | 8 parçada 16 katman, hepsi dz +0,05 (alt bant sağ/sol 217,5 / 221,5; uzatma 1 sağ/sol 73,5 / 161,5 / 165,5; uzatma 2 sağ/sol 73,5; orta bant sağ/sol 217,5 / 221,5) |
| Bu 8 parçada `destek_sorun_sayi`, `desteksiz`, `cikinti_orani` | 0, true, değerler | aynı (artık atlanan katman yok, yeni destek sorunu çıkmadı) |
| Toplam `destek_sorun_sayi` (34 baskı) | 31 (göğüs bandı 1+1, üst arka servis kapağı 1, VESA taşıyıcı 28) | 31 |
| `kutle_g`, `agirlik_merkezi` | 7.170,4; (0,63, 651,67, 12,76) | aynı |
| `cakisma`, `iskelet_cakisma`, `gecersiz`, `coklu_kati`, `temizlik`, `bolge.ihlal` | 0, 0, 0, 0, 0, 0 | aynı |
| `baglanti_kontrol` / `vida_kontrol` tamam | 14/14, 84/84 | aynı |
| `gogus_ekrani` (tüm anahtarlar) | — | değişmedi |
| `sure_s` | 4.736,7 | 4.315,4 |
Yazılan dosyalar: `TF/kabuk/kabuk-analiz.json`, `kabuk-montaj.FCStd`, `kabuk-montaj.step` (STEP katı 357). `kabuk-bom.csv` içerik olarak aynı (git fark göstermiyor).
`kabuk/gorsel/*.png` ve `montaj/yerlesim-kontrol.json` 03.11 tarihli kaldı (K23, dokunulmadı; git'te "M" görünmeleri bu oturumdan önce).

**`kabuk_rapor.py`** gerçek koşu: `cd TF/kabuk && py -3 kabuk_rapor.py` (01:19, çıkış 0) → `kabuk/rapor.html` 978.501 bayt (önce 1.109.774, 14.10).
Metinde (gömülü görseller hariç): `MAX98357` 0, takma ad 0, "V3" 0, "HATA" 0, "2,8 kg" 0; "nextion" yalnız iki dosya adı geçişi (rapora alınmayan görsellerin notu).
Rapor çakışma bölümleri eskimiş uyarısı verdi (aşağıdaki tarama öncesi); tarama sonrası yeniden üretildi (aşağıda).

**Taban raporu** `cd TF/taban && py -3 taban_rapor.py` (00:09, çıkış 0) → `taban/rapor.html` 2.590.708 bayt; "3,0 kg" üç yerde, "2,8 kg" yalnız "önceki 2,8 kg Landport" ifadesinde.
Tarama sonrası yeniden üretildi (aşağıda).

**SY8205 / mikrofon–hoparlör** `bash SP/f1b/zincir_2.sh uygulama_olc` → `cd TF/lale158/kafa-yerlesim && FC_SCRIPT=uygulama_olc.py freecadcmd run_fc.py`
(01:19:20–01:26:27, 427 s, çıkış 0, boş bellek 3,75 GB; log `SP/f1b/uygulama_olc.log`). `uygulama-olcum.json` önceki kopyayla (`SP/f1b/once/uygulama-olcum.json`, 08.11 23:03)
karşılaştırıldı: yalnız `sure_s` (461,7 → 427,0) farklı. `kablo_sy8205.*.sy8205_kesisim_mm3` hepsi 0,0; `mic_hoparlor.poz_min_mm` 574,3.

## Çakışma taraması (omuz hariç 8 bölüm, tek tek)
`arayuz.py` değiştiği için (P1.1) `carpisma_kos.py` kaynak özeti dokuz bölümü de eskimiş saydı. Omuz brief gereği koşulmadı (~4,8 sa, plan P6).
Bölümler `bash SP/f1b/zincir_carp.sh statik kol_sag kol_sol kolkol kafa_sabit kafa_sag kafa_sol taban` ile **tek tek** koşuldu: her bölümden önce
boş bellek ≥ 2 GB ve `tasklist` ile FreeCAD süreci 0 denetlendi; bölüm "sonuc YOK" ya da çıkış ≠ 0 verirse zincir durur. Her biri `cd TF && py -3 carpisma_kos.py <bölüm>`
(çıktılar `SP/f1b/carp_<bölüm>.out`, zincir çıktısı `SP/f1b/zincir_carp.out`). Önceki birleşik sonucun kopyası `SP/f1b/carpisma-sonuc-p15.json`.
| Bölüm | Saat | Süre | Tepe bellek | Boş bellek (başta) | Sonuç |
|---|---|---|---|---|---|
| statik | 01:26:56–01:28:28 | 91 s | 738 MB | 6,36 GB | rc 0, `TF/carpisma-bolum/statik.json` yazıldı |
| kol_sag | 01:28:28–01:32:26 | 237 s | 733 MB | 6,17 GB | rc 0, `kol_sag.json` |
| kol_sol | 01:32:27–01:36:25 | 237 s | 733 MB | 6,25 GB | rc 0, `kol_sol.json` |
| kolkol | 01:36:26–01:37:22 | 56 s | 195 MB | 6,29 GB | rc 0, `kolkol.json` |
| kafa_sabit | 01:37:23–01:40:00 | 157 s | 745 MB | 6,29 GB | rc 0, `kafa_sabit.json` |
| kafa_sag | 01:40:01–01:47:56 | 475 s | 624 MB | 6,29 GB | rc 0, `kafa_sag.json` |
| kafa_sol | 01:47:57–01:55:49 | 471 s | 619 MB | 6,31 GB | rc 0, `kafa_sol.json` |
| taban | 01:55:50–01:57:16 | 86 s | 741 MB | 6,21 GB | rc 0, `taban.json` |
| omuz | — | — | — | — | koşulmadı (`omuz.json` 04.11; eskimiş kalan tek bölüm) |

`py -3 carpisma_kos.py birlestir` (çıkış 0): "eksik: [] | TOPLAM cakisma 364 eklem araliginda 0". `py -3 carpisma_kos.py kontrol`: çıkış 1,
"kaynagi eskimis bolumler: **omuz**" (yalnız omuz; beklenen).
`TF/carpisma-sonuc.json` önce (`SP/f1b/carpisma-sonuc-p15.json`) ↔ sonra:
| Değer | Önce | Sonra |
|---|---|---|
| `ev_pozu_cakisma` | [] (0) | **[] (0)** |
| `ev_pozu_kesisen_cift` | 819 | 819 |
| `toplam.cakisma` / `eklem_araliginda` | 364 / 0 | 364 / 0 |
| `toplam.kafa` / `toplam.taban` (toplam / eklem aralığında) | 6 / 0; 0 / 0 | aynı |
| `kol_tarama`, `kol_kol`, `kafa_tarama`, `taban_tarama` | — | yalnız süre / koşu kimliği alanları farklı; çakışma ve boşluk sayıları aynı |
| `kutle_g.taban` / `kutle_toplam_g` | 7.909,8 / 25.515,6 | 8.109,8 / 25.715,6 (P1.1) |
| `agirlik_merkezi` y; z | 531,56; −8,38 | 528,46; −9,26 (P1.1) |
| `bolumler` | dokuzu "tamam" | dokuzu "tamam" |
`birlestirme_notu` yine "EKSIK / KARISIK birlestirme: eksik bolum yok; kosu kimlikleri [omuz 20261103-215611 + bu koşunun 8 kimliği]; kaynak ayni: False"
(omuz eski koşudan; F1a sonundaki durumla aynı nitelikte).

**Raporlar tarama sonrası yeniden üretildi** (sistem Python'u): `cd TF/taban && py -3 taban_rapor.py` (çıkış 0, `taban/rapor.html` 2.590.737 bayt),
`cd TF/kabuk && py -3 kabuk_rapor.py` (çıkış 0, `kabuk/rapor.html` 978.385 bayt). İkisinin uyarısı artık yalnız "kaynagi eskimis bolumler: omuz".
`kafa`, `iskelet` ve `lale158` raporları brief'te yok, koşulmadı.

## Regresyon
`py -3 planlama/d158/regresyon.py` (normal mod, 01:57:45; taban 23:29:59): **çıkış 0**, "Sonuç: GEÇER (hepsi okundu, kötüleşen yok)".
| Değer | Taban | Şimdi | Eşik | Durum |
|---|---|---|---|---|
| boy_mm | 1580 | 1580 | 1580 ± 0,05 | aynı |
| cakisma_kafa_ici | 0 | 0 | 0 | aynı |
| cakisma_kabuk_ici | 0 | 0 | 0 | aynı |
| cakisma_kabuk_x_iskelet | 0 | 0 | 0 | aynı |
| cakisma_ev_pozu | 0 | 0 | 0 | aynı |
| **rampa_yuksuz** | 1,517 | **1,519** | 1,5 | **iyileşti** (P1.1) |
| tilt_payi | 3,64 | 3,64 | 3 | aynı |
| pan_payi | 2,21 | 2,21 | 2 | aynı |
| mik_hoparlor_mm | 574,3 | 574,3 | 400 | aynı |
| sy8205_x_usb_mm3 | 0 | 0 | 0 | aynı |
"Değişti" durumunda değer yok; tek fark rampa, betik onu "iyileşti" sınıfladı. Betik normal modda `planlama/d158/regresyon-son-kosu.json` ve
`planlama/d158/regresyon.json`'ı (taban) yazdı: tarih 01:57:45, rampa 1,517 → 1,519, kaynak sha256'ları güncellendi. Taban elle zorlanmadı.

## Karar kuyruğu
Yeni K maddesi **yok** (P1.1'de rampa ≥ 1,5; P1.4 uç teması ve ölçüm yöntemi düzeltmesi; P1.5 yalnız analiz ve rapor). Mevcut maddelere iki not:
- K3: P1.1 sonrası düz / fren / rampa payları (0 / 100 / 500 g); K9'daki 500 g rampa 1,327 → 1,329. Seçenekler ve sonuç aynı.
- K23: `planlama/y2/Y2b-ivme.json` P1.1 ile yeniden üretildi; `montaj/yerlesim-kontrol.json` ve `kabuk/gorsel/*.png` bilerek yazılmadı.

## Değişen dosyalar (bu paket)
Kaynak / betik: `TF/arayuz.py` (P1.1), `TF/taban/taban_rapor.py` (P1.1 metni), `TF/lale158/kablo_yolu_ekran.py`, `TF/lale158/lale158_kontrol.py` (P1.4),
`TF/kabuk/kabuk_montaj.py`, `TF/kabuk/kabuk_rapor.py` (P1.5).
Koşu çıktıları: `TF/taban/taban-analiz.json`, `taban-montaj.FCStd`, `taban-montaj.step`, `taban-bom.csv`, `taban/rapor.html`, `taban/dxf/*.dxf` (yeniden yazıldı, git farkı yok);
`TF/montaj/montaj-analiz.json`, `robot-montaj.FCStd`, `robot-montaj.step`, `robot-bom.csv`; `KY/uygulama-ivme.json`, `KY/uygulama-olcum.json` (yalnız `sure_s`);
`planlama/y2/Y2b-ivme.json`; `TF/lale158/lale158-kontrol.json`; `TF/kabuk/kabuk-analiz.json`, `kabuk-montaj.FCStd`, `kabuk-montaj.step`, `kabuk-bom.csv` (git farkı yok), `kabuk/rapor.html`;
`TF/carpisma-bolum/{statik,kol_sag,kol_sol,kolkol,kafa_sabit,kafa_sag,kafa_sol,taban}.json`, `TF/carpisma-sonuc.json`;
`planlama/d158/regresyon.json`, `regresyon-son-kosu.json`.
Planlama: `planlama/d158/karar-kuyrugu.md` (K3, K23 notları), `planlama/d158/F1b-gunluk.md` (bu dosya), `planlama/d158/F1b-kablo-kesit.png` (yeni).
Yan ürün: Python `__pycache__/*.pyc` (`TF/`, `TF/lale158/`, `TF/kabuk/`; git yok sayıyor, önceden de vardı; silme yasak, bırakıldı).
Depoda geçici dosya yok; deneme betikleri ve kopyalar `SP/f1b/` içinde. Commit / push / silme yapılmadı.

## F1b-rapor.html için (kayıt ajanı)
- Önce/sonra tabloları: P1.1 ("Öncesi / sonrası"), P1.4 (`lale158-kontrol.json` tablosu ve kablo ölçüm tablosu), P1.5 ("P1.5 koşuları"),
  çakışma taraması ve regresyon tabloları.
- Görsel: `planlama/d158/F1b-kablo-kesit.png` (P1.4 kanıtı). Kabuk görselleri yenilenmedi (K23 / P6.1); yeni kabuk görseli yok.
- Yeniden üretilen raporlar: `tasarim/freecad/kabuk/rapor.html`, `tasarim/freecad/taban/rapor.html`.

## Açık kalanlar
1. Port yeri (x_duvar −110) ve ona bağlı uç bölgesi tahmin; gerçek kasa / port ölçülünce `arayuz.GOGUS_EKRAN["port"]` ile `uc_bolgesi` birlikte güncellenmeli.
2. `lale158-kontrol.json` `kablo_tup_cakisma` kafa / boyun girdileri (HDMI × Boyun mili 15,1, × Servo yuvası 1,7; Pi uç temasları 2,9 / 2,5 / 11,8; PAM 2,8;
   Boyun mili 1,2 × 2) ayrıştırılmadı (brief dışı, kafa F1a'nın alanı).
3. `TF/kabuk/kabuk_parcalar.py:733` yorumu (72 → 70) düzeltilmedi → P6.1.
4. `kabuk/gorsel/*.png` 03.11 tarihli; `kabuk_gorsel.py` P6.1'de yeniden koşulmalı. K23 dosyaları (`montaj/yerlesim-kontrol.json`, görseller) yerinde.
5. Eski "2,8 kg" metinleri tarihçe / başka pakette: `TF/lale158/ikinci_ozet.py:143`, `lale158-regresyon.json:266`, `2209b-cad-sonuclar.json:50`,
   `qled-cerceve-tasarim-notu.md:129`, `TF/taslak-170/**`, `planlama/adim5/B-malzeme-plan.md:61`.
6. `kafa`, `iskelet` ve `lale158` raporları yeniden üretilmedi (brief'te yok).
7. Omuz bölümü 04.11'den; birleşik sonuç "KARISIK" kalıyor (plan gereği P6).
8. `TF/lale158/kablo_yolu_ekran.py` (satır 2, 6) ve `planlama/y2/Y2b-ivme.py` yorumlarında bu paketten önce kalma takma ad geçişleri var; dokunulmadı.
9. `kabuk_montaj.baski_analiz` kesit kaydırması (+0,05 mm) **kapandı (B buldu):** kök neden kesit düzleminin yatay eksenli delik silindirinin tepesine / dibine tam teğet gelmesi (R 2,0 delikler eksen ±2 mm, R 5,25 havşa dibi; F1b-kontrol madde 14). 0,05 mm kaydırma bu teğetliği kaldırır; geçici çare değil, doğru düzeltme.

