# R — 3B montaj rehberi: çalışma günlüğü

Bir sonraki ajan buradan devam eder. Durum kutuları + hangi komut ne üretti.

## Durum (09.11.2026 16:05, F7a / P7.1: 1,58 m modelinden yeniden üretildi; ayrıntı `planlama/d158/F7a-gunluk.md`)
- [x] F7a-1. Seçiciler 1,58 m: `tasarim/freecad/rehber/rehber_secici.py` (rehberin kendi katmanı; M6_erisim.py / M6_ek.py değişmedi, gerekçe
      dosya başında). 1192 parça (1179 + 13 referans), atanmamış 0; model ↔ rehber modül modül fark 0
- [x] F7a-2. Üretildi: `rehber_uret.py` tek komut (veri 22 s + 50 adım tarayıcı ≈ 3 dk). `kaynak.cad` = F6a modül FCStd saatleri
      (iskelet / omuz 14:27, kabuk / dirsek 14:28, taban 14:29, kafa 08:54). Mesh 288 benzersiz, 189.934 üçgen, GLB 2,56 MB
- [x] F7a-3. Göğüs ekranı F3 içinde (bant → VESA taşıyıcı → ekran → çerçeve); doğrulanmamışlar F3 "Notlar"da. K2'ye göğüs ekranı uçları
- [x] F7a-4. Uygulama: "M6 tablosu:" → "Bağlantı:", M6 kırmızı kutusu / lejantı kaldırıldı (boş lejant gizlenir), `not_` "Notlar" kutusunda,
      adım başına `kamera: "arka"` (F5)
- [x] F7a-5. `kontrol.json`: 50/50 adım geçti, konsol hatası 0, her adımda yeni görünen parçalar beklenenle aynı, her parça tam bir adımda
- [x] P7.2 (F7b, 09.11 17:26; ayrıntı `planlama/d158/F7b-gunluk.md`): E3a / E4 / K2 / F2 / F5 metinleri (QLED, kamera, ReSpeaker, ses
      kartı, PAM8403, hoparlör, hub; ESP32 USB hub'dan), `kablo_yolu_ekran.py` 13 gösterim şeması (parça değil; 1192 ↔ 1192), gruplama
      anahtarı kod + ad, TR sözlüğü + `rehber_denetim.py` (ASCII 0, gruplama 0, çelişki 0), `rehber/yazdir.html` → PDF 50 sayfa,
      360 px taşma 0 (7 adım), kadraj E1 / B3. `kontrol.json` 50/50, konsol 0
- [x] P7.3 (F7c, 09.11 19:10, düzeltme 1 19:49; ayrıntı `planlama/d158/F7c-gunluk.md`): ilk enerji iki aşamalı (F1 kafasız: ana
      30 A, F4, F5 takılı; F1 20 A, F3, hat A / B / C, göğüs 2 A takılı değil, bara enerjisiz; F5 devreye
      alma + ön şarj + motor yön testi), mantar metni K1 düşer, B3 / B5a / B6a tezgâh ayarı satırı, denetimde yasak talimat taraması
      (köprüleme, akü bağlıyken iş, enerji varken bağlantı) + "yerden kesik" zorunlu satırı + görünen adda FreeCAD eki, PDF en küçük
      yazı 8,1 pt (devam sayfasıyla 53 sayfa; eşleme `kontrol.json` `yazdir.sayfa_esleme`). `kontrol.json` 50/50, konsol 0, 1192 ↔ 1192
- [x] P7.4 (F7d, 09.11 20:26 veri, 20:31 kontrol; ayrıntı `planlama/d158/F7d-gunluk.md`): F3 göğüs regülatörü ölçüm sırası açık (ana
      anahtar kapalıyken akü tak → aç → ölç → kapat → akü ayır → uçları sök), K11 b'de fiş F5 aşama 2'de ölçümden sonra; mantar ve
      regülatör ölçümünde DC V kademesi, V soketi, klemensin + ucu; F1 mantar NC süreklilik denemesi; şarj girişi 10 A (K1 kablo, F1 etek,
      aşama 1 / 2 "takılı değil"); denetimde köprüleme eş anlamlıları, "röleyi elle kapat", "açtıktan sonra … tak", pencere sıra
      bağlacında kesilir, `ZORUNLU` 35. PDF 54 sayfa (adım 31, 32, 35, 49 iki sayfa), en küçük yazı 8,1 pt. `kontrol.json` 50/50, konsol 0
      Düzeltme turu 1 (F7d-kontrol KOŞULLU; 21:13 kontrol): pencere yalnız enerjiyi bitiren ifadede kesilir (olumsuz ekli biçim kesmez),
      "artı" / "eksi" kelime sınırıyla; K1 şarj kolu akü XT60'ının robot tarafından (doğrulanmadı), − ucu / kutup doğrulanmadı; F5 notunda
      sigortadan sonra gerilimli şarj pimi uyarısı (KT-F7d-1'e kadar); F3 ölçümünden önce takı ve fiş ucu yalıtımı; `ZORUNLU` 40. Veri
      FreeCAD'siz yazıldı (yalnız metin alanları, `rehber_veri.py` kuralı; `uretim` 20:26 kaldı). PDF yine 54 sayfa, en küçük 8,1 pt

## Durum (15 Ekim 19:20, Opus-10 checkpoint'te durdu: koordinatör talimatı "en yakın checkpoint")
- [x] 0. Kaynaklar okundu (CLAUDE.md, README, OZET, dongu, M6 md + JSON + M6_erisim.py, baski-listesi, elektrik.md, KOL_KABLO, taban YOL)
- [x] A1. `tasarim/freecad/rehber/rehber_veri.py` çalışıyor: 50 adım (0 hazırlık + M6'nın 48'i + F5), 962 parça (13+5 kablo/gösterim referansı dahil)
- [x] A2. Mesh: tek GLB 2,01 MB (252 benzersiz mesh, 148 k üçgen; MeshPart, açısal 0,5 rad, mesh başına ≤ 5000 üçgen hedefi); base64 kopyası 2,7 MB
- [x] A3. M6 bayrakları: C1 4 + C2 10 + C3 5 = 19, K1 4 + K2 6 = 10 → 29 (adım paneli kırmızı kutu + parça kırmızı)
- [x] B1. `rehber/index.html` + `app.js` + `stil.css`: 3B görünüm, ileri/geri, açılır adım listesi, klavye (←/→, R uçuş, V görünüm, T tema),
      panelde yatay kaydırma, açık/koyu tema, localStorage (adım, kontrol kutuları, tema; try/catch), tıkla → parça adı, lejant
- [x] B2. Uçuş animasyonu (parça kendi yönünden, cıvatalar 0,45 gecikmeli; tezgâh alt montajı bağlandığı adımda grup halinde)
- [x] B3. Kablolama kapısı (04.11, kodu yazıldı, veri üretilmedi): `RM.kablo_kapisi` y > 300 olan şemaları K2'ye ayırır (K1'de 7, K2'de 5 yol beklenir; koşuda bak).
      KOL_KABLO geçitleri metinde: ψ214 yarık (F4, G4), tüp penceresi (G3), çatal oluğu (H0c), tırnak (H0a). Şemalar bölünmedi: K2 şemasının taban kısmı K1'de bağlanır
- [x] Metin (`rehber_metin.py`, 04.11): C1 ve sonrası 32 adım + K1 yazıldı; 125 cm / Y3 öncesi M6 satırları `is_`, `baglanti_md`, `alet`, `erisim` ile eziliyor
- [x] C. Yazdırılabilir sürüm (adım başına sayfa): F7b'de yapıldı (`rehber/yazdir.html`, `planlama/rehber/Lale-montaj-rehberi.pdf`)
- [x] D. Tek komut `python tasarim/freecad/rehber/rehber_uret.py` (aşağıda). Kök `README.md`'ye yazıldı (04.11)
- [x] E. Headless Chrome kontrolü: adım 0,1,4,5,9,11,16,17 hazır, konsol hatası 0 (`planlama/rehber/kontrol.json`); görüntüler
      `planlama/rehber/goruntu/adim-NN.png` (1, 9, 17 gözle bakıldı: doğru)

## Yapılacaklar 04.11 → durum 09.11 (F7a)
1 yapıldı (üret ve bak: 50 adım, 16 görüntüye gözle bakıldı). 2 yapıldı (seçiciler `rehber_secici.py`'de; M6 tablosu hâlâ 125 cm,
öneri F7a günlüğünde). 3 yapıldı (F3 + K2; doğrulanmamışlar işaretli). 4 P7.2'ye (parçalar E4'te görünür, metin eski). 5 yapıldı.
6: kablo_yolu_ekran.py yolları, kablo listesi, yazdırılabilir sürüm, baski_listesi_guncelle.py hâlâ açık.
Aşağıdaki metin 04.11 kaydıdır (tarihçe).

## Yapılacaklar (04.11.2026, sonraki ajan buradan başlar)
Gece yalnız metin yazıldı: FreeCAD ve `rehber_uret.py` çalışmadı, `rehber/veri/` eski. `rehber_metin.py` ve `rehber_veri.py` için `py_compile` geçti, başka test yok.

**1. Üret ve bak.** `python tasarim/freecad/rehber/rehber_uret.py`, sonra tüm adımların görüntüsüne bak. Önce adım 2'deki seçicileri düzelt, yoksa parçalar yanlış adımda çıkar.

**2. Seçiciler 125 cm'den kaldı (`planlama/adim4/M6_erisim.py`, `M6_ek.py`; yalnız metin ezildi, parça ataması değil):**
- `_y<690` eşiği ve 4 braket varsayımı; 8 braket var (y 400 / 530,25 / 687,75 / 1095).
- Etek `"M3x8"` seçicisi: kod artık M3×14, C0'a düşer. F1'e alınmalı.
- "Govde uzatma bandi" F2'de yok, F5'e düşer.
- H1, H2, üst arka kapak, dolgu şeritleri, göğüs çerçevesi, VESA taşıyıcı, adaptör ve saplamaların adımı doğrulanmadı.
- `M6-montaj-sirasi.md` tablosu hâlâ 125 cm (F3 / K2'de Nextion). Tablo düzeltilmedi; `rehber_metin.py` üstünü örtüyor.

**3. Göğüs ekranı adımı yazılacak (F3'ten sonra):** VESA taşıyıcı: kasaya 4 × M4×12 DIN 912 + pul, direk ön kanalına 2 × M6×18 DIN 912 + pul + çekiç somun (`lale158/lale158_rapor.py` satır 77–78; delik yeri ve vida derinliği orada da doğrulanmadı). Çerçeve sağ + sol, ekran 2 mm içeride, çerçeve gövde renginde. Direk ön yüzünden K2'nin kafa 12 V ve USB hattı da geçiyor: çakışma doğrulanmadı.
- Kablo: HDMI boyundan iner, dokunmatik USB hub'dan (05.11 B kararı; CAD'de böyle, teyit yok); uç K2'de göğüs hizasında bırakılır (09.11'de K2'ye eklendi).
- Besleme: 12 V, LM2577 + LM2596 kartı, 2 A sigortalı ayrı dal. Giriş noktası ve acil stop davranışı doğrulanmadı (`elektrik.md`).

**4. Kafa ekranı adımı yazılacak (E3a ile E4 arasına):** 10,1" QLED, vida deliği yok, tırnak; görünen alan 225,64 × 127,36; kütle doğrulanmadı.
- Önce model: `kafa10_lib.py`, `kafa7_parcalar.py` 10,1" için güncellenmeli. E3a parça listesindeki 7" LCD o zaman kalkar.
- Kablo: HDMI tam boy (Pi micro HDMI 0), Power micro USB ← kesik USB-A ← SY8205 + P6KE6V8A, Touch micro USB ← Pi.
- **Uyarı:** iki 5 V köprülenmez; Touch kablosu VBUS'u Pi'ye bağlar (`elektrik.md`).
- SY8205, 4'lü hub, PAM8403, USB ses kartı, TVS'lerin kafadaki yeri modelde yok, doğrulanmadı.

**5. Uygulama (`rehber/app.js`):** kırmızı kutu ve lejant "M6 CAD sonrası değişecek" artık boş kalır (`M6_BAYRAK_ACIK = False`); "M6 tablosu:" etiketi güncel `baglanti_md` önünde de çıkıyor, "Bağlantı:" olmalı. `not_` alanı gösterilmiyor.

**6. Bilinen eksikler:**
- `lale158/kablo_yolu_ekran.py` yolları rehbere girmedi; kablo şemaları K1 / K2 diye bölünmedi; taban_parcalar'da "kafada 5 V/5,5 A cevirici (Pi 5, LCD)" adı eski.
- `lale158/baski_listesi_guncelle.py` tekrar koşarsa `planlama/baski-listesi.md`'de 158 cm bloğunu yeniden üretir: "1,65 m tarihli" cümlesi döner, Özet satır 3 yeniden 7" olur. Betik düzeltilmeli.
- Kablo listesi (boy + kesit) yazılmadı; uzatma ek yeri kaynakta yok.
- Yazdırılabilir sürüm başlanmadı (madde C).

**Bağlı dosyalar:** `tasarim/freecad/arayuz.py`, `kafa10_lib.py`, `kafa7_parcalar.py`, `kabuk_parcalar.py`, `lale158/kablo_yolu_ekran.py`, `planlama/adim3/elektrik.md`, `planlama/y3/Y3-gunluk.md`, `tubitak-2209b/malzeme-listesi/` v4 xlsx.

## Komutlar ve ürettikleri
| Komut | Üretir |
|---|---|
| `python tasarim/freecad/rehber/rehber_uret.py` | 1) freecadcmd + `rehber_veri.py` (~22 s) → `rehber/veri/rehber-veri.json`, `rehber-veri.js`, `robot.glb`, `robot-glb.js`; 2) her adım için headless Chrome `--dump-dom` (hata/hazır + `kontrol-veri`: yeni görünen parçalar) + `--screenshot` → `planlama/rehber/goruntu/adim-NN.png`, `planlama/rehber/kontrol.json` (tüm 50 adım ≈ 3 dk; çıkış 0 = hepsi geçti) |
| (F7b ekleri, aynı komut) | `rehber/goruntu/adim-NN.png` (yalnız 3B, `?sahne=1`), `planlama/rehber/goruntu/telefon-360-adim-NN.png` (DevTools ile 360 px; Python `websockets` gerekir), `planlama/rehber/Lale-montaj-rehberi.pdf` (`rehber/yazdir.html`), `kontrol.json` `telefon` / `yazdir` / `denetim` alanları. Tüm adımlar ≈ 5 dk |
| `... --veri-yok --cikti <klasör>` / `--ek-yok` | tüm çıktılar o klasöre (kontrol.json, goruntu/, PDF, `<klasör>/rehber/` yazdir.html + veri kopyası + 3B görüntüler; depodaki `rehber/` yalnız okunur, F7b-kontrol D-4) / telefon, PDF ve denetimi atla |
| FreeCAD başlatıcısı | `LALE_FC_LAUNCH` ortam değişkeni, yoksa `~/.robot-cad/run_fc.py` (ASCII yol; F7b-kontrol D-5) |
| `python tasarim/freecad/rehber/rehber_denetim.py` | yalnız veri üzerinde ASCII kalıntı, gruplama (parça + bağlantı satırları), kafa / hoparlör / hub tutarlılığı, zorunlu güvenlik uyarıları (çıkış 0 = temiz) |
| `... rehber_uret.py --veri-yok --adimlar 1,4,9` | yalnız tarayıcı kontrolü + seçili görüntüler |
| `... --gorsel-yok` | yalnız veri + mesh |
| Doğrudan: `FC_SCRIPT=<rehber_veri.py> freecadcmd run_fc.py` | yalnız veri + mesh |
| Açmak | `rehber/index.html` çift tık (file:// çalışır, internet gerekmez; three.js 0.160.0 `rehber/vendor/` içinde, F10a). Tuşlar: P patlat / topla, Boşluk sıradaki satırı tak, Shift+Boşluk geri al, O öncekiler opak / saydam / gizli, M küçük görünüm, Esc seçimi temizle. `?adim=N`, `?cekim=1` (animasyonsuz), `?tema=dark` |

## Sıradaki işler (madde madde)
1. Kök `README.md` yazıldı (04.11). `tasarim/freecad/README.md` "Rehber" bölümü hâlâ yok: tek komut, ne zaman koşulur (modüller yeniden üretildikten ve
   `M6_erisim.py` yeniden koşulduktan SONRA; adım ataması ve YOK bayrakları oradan gelir). README başka ajanın da dosyası: dikkat.
2. Kamera: bazı adımlarda (ör. 9 B3) kadraj çok yakın; `kameraYerlestir` hedef kutuya görünen robotun bir kısmını da katmalı.
3. Parça listesi gruplama: aynı kodlu parçalar gruplanırken ad ilk parçanınki (ör. "BTS7960 motor sürücü sol ×2"): kod tabanlı ortak ad.
4. Yapıldı (04.11, metin + kod): K1/K2 kablo ayrımı, KOL_KABLO geçitleri. Yer tutucu yerine "kablo listesi henüz yazılmadı" notu.
5. Yapıldı (04.11): `rehber_metin.py` C1, D*, E*, F*, G*, H* yazıları, kontrol listesi, kablo kancası.
6. Uçuş yönleri gözle kontrol (özellikle D1 kaydırma ±x, F bantları radyal, G/H); şu an yalnız iskelet + taban bakıldı.
7. Yazdırılabilir sürüm: `rehber/yazdir.html` (adım başına bir sayfa: `?cekim=1` görüntüsü + listeler) + `--print-to-pdf`.
8. Tüm 50 adımı `rehber_uret.py` ile koş, görüntülere bak, telefonda (dar pencere 390×844 görüntüsü) dene.

## Bilinen sorunlar
- CAD etiketleri ASCII; `rehber_metin.TR` sözlüğü sık kelimeleri Türkçeleştiriyor (eksik kelimeler ASCII kalır). Bir malzeme kodunda
  bozuk karakter var ("hu� kontrplak", kaynak CAD'de).
- Süre değerleri tahmini (5 + 1 dk/cıvata + 0,3/somun-pul + 0,8/parça), hazırlık 60 dk elle.
- Mesh kaba (148 k üçgen); gerekirse `ucgenle()` içindeki `diag * 0.004` ve 5000 bütçesi artırılır (GLB 2 MB, pay çok).
- Eylemsizlik örneklemesi simetrik parçalarda eksen etrafındaki dönüşü keyfi seçer (somun altıgeni, cıvata soketi); görsel olarak önemsiz.
- three.js artık yerel (`rehber/vendor/`, F10a): rehber çevrimdışı da açılır. Demo görüntüleyici (`tasarim/cad/viewer-template.html`) hâlâ CDN'den (r128): internetsiz 3B açılmaz.


## Kayıt
- 2026-10-15: günlük açıldı.
- 2026-10-15: kaynaklar okundu. Koordinatör talimatı: **%50 checkpoint'te dur** (A çalışır + B iskeleti, iskelet+taban adımları uçtan uca,
  ekran görüntüleri, konsol temiz). Yazdırılabilir sürüm ve cila sonraya.
- 2026-11-04: C1 ve sonrası adım yazıları, K1 / K2 ayrımı, M6 bayrağı kapalı, kök README komutu. Veri üretilmedi, görsel bakılmadı. Yukarıda "Yapılacaklar".
- 2026-11-09 (F7a, P7.1): 1,58 m modelinden yeniden üretildi; seçiciler `rehber_secici.py`; göğüs ekranı F3; uygulama düzeltmeleri; kontrol 50/50.
- 2026-11-09 (F7a düzeltme turu 1, `planlama/d158/F7a-kontrol.md` O-1 / O-2): kafadaki 625ZZ iç bilezik E2b → E2, ana anahtar ASW-A01 gövdesi B5a → F1 (etek plakası altı); B5a / K1 / F1 metni buna göre. Yeniden üretildi: 50/50, konsol 0, 1192 ↔ 1192.
- 2026-11-09 (F7b, P7.2): kafa / hoparlör / hub metinleri, göğüs ekranı kablo şemaları, gruplama, TR denetimi, yazdırılabilir PDF (50 sayfa),
  360 px. Yeniden üretildi 17:21 (veri) / 17:26 (kontrol): 50/50, konsol 0, 1192 ↔ 1192, denetim temiz. `planlama/d158/F7b-gunluk.md`.
- 2026-11-09 (F7b düzeltme turu 1, `planlama/d158/F7b-kontrol.md`): elektrik güvenliği talimatları (göğüs regülatörü 12 V ayarı, 1N5819 yönü,
  iki P6KE6V8A + kutup, K1 / K2 enerji durumu), `--cikti` tam yalıtım, başlatıcı yolu ortam değişkeni / ev klasörü, denetime zorunlu uyarı
  ve bağlantı satırı denetimi. Veri 17:54'te yeniden üretildi.
- 2026-11-09 (F7c, P7.3; `planlama/d158/F7c-gunluk.md`): F7b-kontrol D-10, D-11, D-12, D-1', D-3, D-6. Veri 19:05 (FreeCAD, kilit altında),
  kontrol 19:10: 50/50, konsol 0, 1192 ↔ 1192, PDF 52 sayfa (adım 31 ve 32 iki sayfa), en küçük yazı 8,1 pt, denetim 0.
  Düzeltme 1 (F7c-kontrol O-1, O-2, D-1, D-2, D-3): veri 19:44, kontrol 19:49: 50/50, konsol 0, 1192 ↔ 1192, PDF 53 sayfa (adım 31,
  32, 49 iki sayfa), en küçük yazı 8,1 pt, denetim 0 (zorunlu 0 / 23, yasak 0).
- 2026-11-09 (F7d, P7.4; `planlama/d158/F7d-gunluk.md`): F7c-kontrol D-5, D-6', D-7, D-8, D-9, D-10. Veri 20:26 (FreeCAD, kilit altında),
  kontrol 20:31: 50/50, konsol 0, 1192 ↔ 1192, PDF 54 sayfa (adım 31, 32, 35, 49 iki sayfa), en küçük yazı 8,1 pt, denetim 0
  (zorunlu 0 / 35, yasak 0, istisna 5). Demo "Bu sayfa hakkında" metni `F9b-dogrula.py`'nin gerçek denetimlerine göre yazıldı.
- 2026-11-09 (F7d düzeltme turu 1; `planlama/d158/F7d-kontrol.md` O-1, O-2, D-1, D-2, D-4, D-5): FreeCAD koşulmadı; adım metni
  `rehber-veri.json` / `.js`'e `rehber_veri.py`'nin alan kuralı ve yazma biçimiyle yazıldı (değişiksiz yeniden yazım FreeCAD çıktısıyla bayt
  bayt aynı; fark yalnız K1 `is_`, F3 `is_`, F5 `not_`). Kontrol 21:13: 50/50, konsol 0, 1192 ↔ 1192, PDF 54 sayfa, en küçük 8,1 pt,
  denetim 0 (zorunlu 0 / 40, yasak 0, istisna 5); F9b, `kontrol`, regresyon 0.

## Kararlar (tasarım)
- 09.11 (F7b): Göğüs ekranı / kafa kablo yolları (`lale158/kablo_yolu_ekran.py`) `semalar` olarak girer, `parcalar`a değil: gösterim
  tüpü, parça sayısına ve "her parça tek adımda" denetimine katılmaz. Taban kablo şemalarının görünen adı `rehber_metin.KABLO_AD`'dan
  (CAD etiketi `taban_parcalar.py`'de, tarama kaynağı).
- 09.11 (F7b): Parça listesi satırı = (kod, tür, renk, sağ / sol atılmış taban ad); satır `ids` taşır, denetim betikle doğrular.
- 09.11 (F7a): Adım ataması tek kaynak `tasarim/freecad/rehber/rehber_secici.py` (1,58 m; saf Python, FreeCAD'siz test edilir). Kodlar
  doğrudan M6 tablosu kodları (E4a / E3a ara kodu yok). M6_erisim.py'nin ADIMLAR'ı 125 cm kaydı olarak kaldı; M6 analizi 1,58 m'de
  yeniden koşulursa seçicileri buradan almalı.
- 09.11 (F7a): Göğüs ekranı ayrı adım değil, F3'ün içinde (M6 F3 satırı zaten "göğüs bantları + Nextion"); adım sayısı 48 + F5 + hazırlık kaldı.
- 09.11 (F7a): Isıl gömme somunlar bağlandıkları cıvatanın adımında listelenir (bindirme, kapak). Bir parçaya vidalanan alt parça o parçayla
  aynı adımda: kamera / QLED / tırnaklar yüz kabuğuyla, ReSpeaker / ses kartı / PAM8403 arka kabukla (E4); hub üst arka kapakla (F5);
  hoparlör orta bantla (F2); XL4016 C ve ön şarj kartı güç paneliyle (B5a); etek H1 / H2 kapakları F5.
- (15.10) Adım ataması tek kaynak: `planlama/adim4/M6_erisim.py` içindeki `ADIMLAR` seçicileri. `rehber_veri.py` bu dosyanın
  "yukle" işaretine kadarki kısmını `exec` eder (kopya yok). İç kod → rehber kodu: `E4a→E4`; kafa "Yanak-horn civatasi" → `E3`. [09.11'de değişti]
- Adım metinleri (iş, bağlantı, alet, erişim) `M6-montaj-sirasi.md` 2. bölüm tablosundan **ayrıştırılır** (48 satır + F5). Ek
  metin (kontrol listesi, kablo kancası, süre, uçuş yönü) `tasarim/freecad/rehber/rehber_metin.py` (adım koduna bağlı, CAD'den bağımsız).
- Mesh: tek GLB (`rehber/veri/robot.glb`), parça başına bir düğüm (ad `p####`), aynı parçalar tek mesh (eylemsizlik çerçevesiyle
  örnekleme; sol = sağın X aynası düğüm matrisinde). Normaller tarayıcıda hesaplanır. file:// için aynı GLB base64 olarak
  `rehber/veri/robot-glb.js` (fetch file:// altında çalışmıyor).
- Görünürlük: parça başına `a` (takıldığı adım), `b` (robota girdiği adım; tezgâh alt montajı bağlanınca), `t` (tezgâh anahtarı).
  Tezgâh adımında yalnız o alt montaj görünür.
- 19 + 10 bağlantı (M6 YOK, G4 kaset hariç; K1 gövde braketi M5 ×4, K2 etek braketi M3 ×6) `m6` bayrağıyla işaretli.
