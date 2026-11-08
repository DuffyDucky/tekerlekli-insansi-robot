# R — 3B montaj rehberi: çalışma günlüğü

Bir sonraki ajan buradan devam eder. Durum kutuları + hangi komut ne üretti.

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
- [ ] C. Yazdırılabilir sürüm (adım başına sayfa) — başlanmadı
- [x] D. Tek komut `python tasarim/freecad/rehber/rehber_uret.py` (aşağıda). Kök `README.md`'ye yazıldı (04.11)
- [x] E. Headless Chrome kontrolü: adım 0,1,4,5,9,11,16,17 hazır, konsol hatası 0 (`planlama/rehber/kontrol.json`); görüntüler
      `planlama/rehber/goruntu/adim-NN.png` (1, 9, 17 gözle bakıldı: doğru)

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
- Kablo: HDMI + USB dokunmatik Pi'den boyundan iner (CAD'de böyle, **Efe teyidi yok**); uç K2'de göğüs hizasında bırakılır, K2 metnine eklenecek.
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
| `python tasarim/freecad/rehber/rehber_uret.py` | 1) freecadcmd + `rehber_veri.py` (~20 s) → `rehber/veri/rehber-veri.json`, `rehber-veri.js`, `robot.glb`, `robot-glb.js`; 2) her adım için headless Chrome `--dump-dom` (hata/hazır) + `--screenshot` → `planlama/rehber/goruntu/adim-NN.png`, `planlama/rehber/kontrol.json` (tüm 50 adım ~5 dk) |
| `... rehber_uret.py --veri-yok --adimlar 1,4,9` | yalnız tarayıcı kontrolü + seçili görüntüler |
| `... --gorsel-yok` | yalnız veri + mesh |
| Doğrudan: `FC_SCRIPT=<rehber_veri.py> freecadcmd run_fc.py` | yalnız veri + mesh |
| Açmak | `rehber/index.html` çift tık (file:// çalışır; three.js 0.160.0 jsdelivr'den, internet gerekir). `?adim=N`, `?cekim=1` (animasyonsuz), `?tema=dark` |

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
- three.js CDN'den: çevrimdışı açılmaz (GitHub Pages'te sorun değil).


## Kayıt
- 2026-10-15: günlük açıldı.
- 2026-10-15: kaynaklar okundu. Koordinatör talimatı: **%50 checkpoint'te dur** (A çalışır + B iskeleti, iskelet+taban adımları uçtan uca,
  ekran görüntüleri, konsol temiz). Yazdırılabilir sürüm ve cila sonraya.
- 2026-11-04: C1 ve sonrası adım yazıları, K1 / K2 ayrımı, M6 bayrağı kapalı, kök README komutu. Veri üretilmedi, görsel bakılmadı. Yukarıda "Yapılacaklar".

## Kararlar (tasarım)
- Adım ataması tek kaynak: `planlama/adim4/M6_erisim.py` içindeki `ADIMLAR` seçicileri. `rehber_veri.py` bu dosyanın
  "yukle" işaretine kadarki kısmını `exec` eder (kopya yok). İç kod → rehber kodu: `E4a→E4`; kafa "Yanak-horn civatasi" → `E3`.
- Adım metinleri (iş, bağlantı, alet, erişim) `M6-montaj-sirasi.md` 2. bölüm tablosundan **ayrıştırılır** (48 satır + F5). Ek
  metin (kontrol listesi, kablo kancası, süre, uçuş yönü) `tasarim/freecad/rehber/rehber_metin.py` (adım koduna bağlı, CAD'den bağımsız).
- Mesh: tek GLB (`rehber/veri/robot.glb`), parça başına bir düğüm (ad `p####`), aynı parçalar tek mesh (eylemsizlik çerçevesiyle
  örnekleme; sol = sağın X aynası düğüm matrisinde). Normaller tarayıcıda hesaplanır. file:// için aynı GLB base64 olarak
  `rehber/veri/robot-glb.js` (fetch file:// altında çalışmıyor).
- Görünürlük: parça başına `a` (takıldığı adım), `b` (robota girdiği adım; tezgâh alt montajı bağlanınca), `t` (tezgâh anahtarı).
  Tezgâh adımında yalnız o alt montaj görünür.
- 19 + 10 bağlantı (M6 YOK, G4 kaset hariç; K1 gövde braketi M5 ×4, K2 etek braketi M3 ×6) `m6` bayrağıyla işaretli.
