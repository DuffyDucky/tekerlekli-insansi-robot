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
- [~] B3. Kablolama kapısı: K1/K2 adımında taban kablo yolu şemaları renkli; metin yer tutucu. **Eksik:** K2 için ayrı güzergâh (şu an
      12 yolun hepsi K1'de; direk boyunca olanlar K2'ye ayrılmalı), KOL_KABLO geçitleri (ψ214 yarık, tüp penceresi, çatal oluğu, tırnak)
- [~] Metin (`rehber_metin.py`): 0, A1–A3, B1a–B7, C0, K1, K2 kontrol + kablo kancası yazıldı; C1'den sonrası yalnız M6 tablosu + kısa başlık
- [ ] C. Yazdırılabilir sürüm (adım başına sayfa) — başlanmadı
- [x] D. Tek komut `python tasarim/freecad/rehber/rehber_uret.py` (aşağıda). **README'ye henüz yazılmadı**
- [x] E. Headless Chrome kontrolü: adım 0,1,4,5,9,11,16,17 hazır, konsol hatası 0 (`planlama/rehber/kontrol.json`); görüntüler
      `planlama/rehber/goruntu/adim-NN.png` (1, 9, 17 gözle bakıldı: doğru)

## Komutlar ve ürettikleri
| Komut | Üretir |
|---|---|
| `python tasarim/freecad/rehber/rehber_uret.py` | 1) freecadcmd + `rehber_veri.py` (~20 s) → `rehber/veri/rehber-veri.json`, `rehber-veri.js`, `robot.glb`, `robot-glb.js`; 2) her adım için headless Chrome `--dump-dom` (hata/hazır) + `--screenshot` → `planlama/rehber/goruntu/adim-NN.png`, `planlama/rehber/kontrol.json` (tüm 50 adım ~5 dk) |
| `... rehber_uret.py --veri-yok --adimlar 1,4,9` | yalnız tarayıcı kontrolü + seçili görüntüler |
| `... --gorsel-yok` | yalnız veri + mesh |
| Doğrudan: `FC_SCRIPT=<rehber_veri.py> freecadcmd run_fc.py` | yalnız veri + mesh |
| Açmak | `rehber/index.html` çift tık (file:// çalışır; three.js 0.160.0 jsdelivr'den, internet gerekir). `?adim=N`, `?cekim=1` (animasyonsuz), `?tema=dark` |

## Sıradaki işler (madde madde)
1. README (`tasarim/freecad/README.md`) "Rehber" bölümü: tek komut, ne zaman koşulur (6. adımda modüller yeniden üretildikten ve
   `M6_erisim.py` yeniden koşulduktan SONRA; adım ataması ve YOK bayrakları oradan gelir). README başka ajanın da dosyası: dikkat.
2. Kamera: bazı adımlarda (ör. 9 B3) kadraj çok yakın; `kameraYerlestir` hedef kutuya görünen robotun bir kısmını da katmalı.
3. Parça listesi gruplama: aynı kodlu parçalar gruplanırken ad ilk parçanınki (ör. "BTS7960 motor sürücü sol ×2"): kod tabanlı ortak ad.
4. K1/K2 kablo ayrımı + KOL_KABLO geçitleri (G3, G4, H1 kablo kancaları) + "kablo listesi C işi, 5. hafta" yer tutucusu her iki kapıda.
5. `rehber_metin.py`: C1, D*, E*, F*, G*, H* için kontrol listesi ve kablo kancası (M6 2. bölüm kuralları + 3. bölüm Ø84 sırası:
   "F4'ten sonra omuz bandı ancak göbek sökülünce çıkar", G4 "S1 −45°'de", H0 sırası, H1 bilezik sıkma kupon D).
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
