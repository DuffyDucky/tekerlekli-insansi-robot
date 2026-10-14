# P: Raspberry Pi 5'i kafaya taşımak (K4 analizi)

Tarih: 14 Ekim 2026. Durum: **TAMAMLANDI (analiz)**. Hiçbir CAD/kaynak dosyası değiştirilmedi; yalnız bu klasöre betik ve sonuç dosyası eklendi.
Ölçüm betikleri bu klasörde: `pi_kafada_olcum.py` (boş hacim + 24 yönelim taraması), `pi_kafada_tabla.py` (tablaya doğrudan vida),
`pi_kafada_dogrula.py` (seçilen konum, kesin çakışma + tilt taraması); sonuçlar `pi_kafada_sonuc.json`, `pi_kafada_tabla_sonuc.json`,
`pi_kafada_dogrula_sonuc.json`. Betikler yalnız `kafa_parcalar.py`'yi import eder (yazmaz); voxel önbelleği `%TEMP%\pi_kafada_voxel.npz`.
Satır numaraları okuma anındaki durumdur (başka oturumlar dosyaları değiştiriyor olabilir); kaynak olarak dosya + değişken adı da verildi.

## Karar önerisi (özet)

**Kafaya koy, şu şartlarla:** (1) Pi kafa tablasının üstüne, arka-sol bölgeye vidalanır (ölçüldü, çakışma 0); (2) kafaya **12 V** çıkar,
kafada küçük 5 V/5 A düşürücü olur (5 V'u 1,25 m çekmek yerine); (3) kapalı kafaya giriş + çıkış havalandırması eklenir (şimdi yok, ısı 4,5 kat artıyor);
(4) ESP32'ye USB (1,25 m) ve Nextion hattı yeniden planlanır; (5) kafa iskeleti ve arka kabuk **henüz basılmadığı** için (baski-listesi ☐) değişiklik şimdi ucuz.
Kazanç: boyundan HDMI, CSI şeridi ve iki USB çıkar; kesit ~%40 azalır, dönen boyundan şerit/HDMI geçme riski biter.
Bedel: kafa +145 g (tilt payı 2,11 → 1,96), +10 W ısı kafada, servis kafa içinde.

## 1. Yer

| Ölçü | Değer | Kaynak |
|---|---|---|
| Kafa iç boşluğu | x ±102,5, y 97,5…272,5, z -62,5…82,5 (dış 210×180×150, duvar 2,5, köşe R28/R12) | `kafa_parcalar.py` KB, KT, kafa_kutu; `arayuz.KAFA["kafa_kutu"]` |
| Kafa tablası (Kafa iskeleti) | y 178…183, x ±100,5, z ±58, 4 hafifletme cebi + kablo geçişi (x -50…-37, z 0…24); kafayı alt (tilt mekanizması) ve **üst bölmeye** ayırıyor | `kafa_parcalar.py` Y_TABLA, ki; `kafa-analiz.json` parça "Kafa iskeleti" bb y 114…183 |
| Üst bölme (tabla üstü) | y 183…272,5 = **89,5 mm yükseklik**, içinde hiçbir parça yok (yalnız LCD/kamera ön tarafta) | voxel ölçümü (`pi_kafada_olcum.py`) |
| **LCD arkası ↔ arka iç duvar net derinlik** | **136,9 mm** (z -62,5 → 74,4; x=0, y=200 ve 230 doğrusu, kesin ray ölçümü). LCD konnektör blokları z 64,5/70,5'e iniyor (x +52…72 ve x -40…30, y 149…199): oraya göre 127/133 mm. CAD'deki 15 mm modül kalınlığı tahmini; Waveshare sayfası toplam 8 mm diyor, gerçek pay daha fazla | ray: `pi_kafada_sonuc.json` "ray"; LCD `kafa_lib.py` LCD/lcd_local; Waveshare wiki: waveshare.com/wiki/7inch_HDMI_LCD_(C) |
| Boş iç hacim | üst bölme 2.563 cm³, alt bölme 2.159 cm³ (2,5 mm voxel; toplam iç 5.093 cm³, analitik iç kesin iç ile 600 noktada %0,17 uyumsuz) | `pi_kafada_sonuc.json` |
| Pi 5 + Active Cooler | kart 85×56 (delik Ø2,7, 58×49, kenardan 3,5); cooler 63,5×42,5×13,7; USB/Eth bloğu 17,5 yüksek, +X kenarında 3 mm taşar; **USB-C, 2× micro-HDMI ve 2× CSI aynı kenarda (y=0)**; STEP'ten bileşen kutuları alındı. Gövde 55 cm³, koruma hacimleriyle 116 cm³ | `donanim/datasheet/raspberry-pi-5-mechanical-drawing.pdf`, `pi5-step/rpi-5b_no_graphics.step`, `04-parca-olculeri.md` satır Pi 5 |
| Koruma hacimleri (varsayım) | fan üstü 10 mm, kablo kenarı 30 mm (micro-HDMI/USB-C/FPC fişleri), USB tarafı 20 mm, microSD 15 mm; kompakt varyant 8/22/8/8 | benim varsayımım (ölçülecek) |

**Yerleşim taraması:** 24 yönelim × 2,5 mm ızgara, Pi gövdesi + koruma hacimleri, kafa parçaları (kabuk dahil) ve tilt taramasında (-25…30°) Pan/Gövde grubu ile
≥ 2,5 mm payla çakışmayan konumlar (FFT korelasyon). Tam koruma ile: üst bölmede bileşen-yukarı/kablo kenarı-ön yönelimde **14.608 geçerli konum** (Pi merkezi x -42…35, z -33…22),
alt bölmede yalnız 495 konum ve hiçbirinde tutma yüzeyi yok (tabla altı / duvar bulunamadı). Kompakt korumada üst 21.022, alt 14.203 konum (alt bölmede yine havada).

**Tablaya doğrudan vida** (`pi_kafada_tabla.py`): 4 delik merkezinin tabla katısına ≥ 3,5 mm (M2,5 ısıl gömme somun Ø4 + et, varsayım) içinde kaldığı konumlar, 1 mm adım:
kablo kenarı ön için 1.318, sağ/sol için 506'şar. **Seçilen (R0, kablo kenarı +Z):** kart köşesi (x -34, z +1), alt yüzey y = 189 (tabla 183 + 6 mm M2,5 burç);
kart x -34…51, z -55…+1 (USB bloğuyla x 54,1, konnektörlerle z 2,7), yükseklik y 187,5…206,5 (cooler üstü 204), fan koruması 214'e kadar. Delik merkezleri (x, z): (-30,5; -2,5), (27,5; -2,5), (-30,5; -51,5), (27,5; -51,5).
**Kesin sonuç (`pi_kafada_dogrula.py`):** Pi gövdesi ve tüm koruma hacimleri × kafa grubunun tüm parçaları (iskelet, kabuklar, LCD, kamera, vizör, bağlantı elemanları) çakışma **0**; en yakın parça: tabla 4,5 mm (burç boşluğu), arka kabuk 7,5 mm (GPIO kenarı z -55 ↔ iç duvar -62,5);
tilt -25…30° taramasında Pan/Gövde grubuna en yakın **28,1 mm**, çakışma 0. LCD konnektör bloğuna (z 64,5) Pi konnektörlerinden ~62 mm, kablo koruma hacminden sonra ~33 mm kalır.
Bağlantı mesafeleri (düz çizgi): Pi USB-C (x -23) kablo geçişine (x -50…-37, z 0…24) ~15-25 mm; Pi CSI (x 13…23) → kamera (0, 258, 76) ~100 mm (şeritle ~170-190 mm: **200 mm FPC sınırda, 300 mm önerilir**);
Pi micro-HDMI (x -8, +5) → LCD HDMI bloğu (x 52…72) ~115 mm (kısa micro-HDMI→HDMI kablo 25-30 cm gerekir; TR stoğu doğrulanmadı).
Tablanın hafifletme cepleri Pi'yi kısıtlıyor ama delikler cebe değmiyor; ek parça gerekmez, yalnız iskelette 4 yerde ısıl gömme somun (tabla 5 mm, somun yuvası ≤ 4-5 mm: yeterliliği kupon testinde bakılmalı).
Alt bölmede (sol-arka, Pi dikey) tork açısından daha iyi (aşağıda) ama tutma yüzeyi yok, kabuğa braket ve Pi'nin ısı yolu karmaşık; **önermiyorum**.

## 2. Tork

Projedeki servo: **MG996R** (pan ve tilt), `arayuz.KAFA["servo"]`, `kafa_montaj.py` STALL = 9,4 kg·cm @4,8 V. Datasheet doğrulandı (electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf): 9,4 @4,8 V, 11 @6 V, 55 g, 0,17 s/60° @4,8 V, **çalışma sıcaklığı 0…55 °C**.
Mevcut kafa (kafa-analiz.json tork): tilt grubu 833,4 g, AM (0,81; 183,76; 29,73), eksen (y 130, z 25), AM-eksen 54 mm; yer çekimi 2,58 (30°'de) + ivme 1,88 = **4,46 kg·cm → pay 2,11**. Pan: 1.029,4 g, 2,6 kg·cm, pay 3,6.
Hesabı `kafa_montaj.py` formülleriyle yeniden kurdum (4,459 / pay 2,11 aynı çıktı) ve nokta kütle + kutu atalet ekledim (alfa 26,2 rad/s², 60° / 0,4 s profil, projedeki gibi).

| Ek kütle (Pi 46 g + cooler 12 g [taban_lib.py PI kutle_g] + tutucu/burç ~15 g + düşürücü ~6-40 g + kısa kablolar ~20 g) | Tilt toplam | Tilt payı (4,8 V / 6 V) | Pan payı | Üst rulman eksenel / radyal |
|---|---|---|---|---|
| 0 (mevcut) | 4,46 | 2,11 / 2,47 | 3,6 | 10,1 / 23,8 N |
| 120 g, seçilen konum (8,5; 196; -27) | 4,57 | 2,06 / 2,41 | 3,6 | 11,3 / 21,0 N |
| **145 g** | **4,81** | **1,96 / 2,29** | 3,6 | 11,5 / 20,4 N |
| 170 g | 5,05 | 1,86 / 2,18 | 3,5 | 11,8 / 19,8 N |
| 145 g, serbest en iyi (-25; 193; -18) | 4,63 | 2,03 / 2,37 | 3,5 | 11,5 / 21,6 N |
| 145 g, alt-arka bölme (-74; 130; -2,5) | 4,18 | 2,25 / 2,63 | 3,3 | 11,5 / 25,1 N |

Notlar: (a) 145 g'da en kötü yer çekimi momenti -25° tarafına (burun yukarı) kayıyor (2,62 kg·cm), çünkü Pi AM'yi geriye çekiyor; (b) tilt statik tutma yükü hâlâ stall'ın ~%28'i;
(c) tilt mili yük paylaşımı: kütle merkezi x = +1,9 mm, horn payı 0,498 → 0,518 (horn tarafı 4,1 N → ~5,0 N, 625ZZ tarafı 4,1 → ~4,6 N); (d) **tilt servosunda radyal yük açık işi** (ikinci rulman) bu kütleyle bir miktar ağırlaşır, çözülmeli;
(e) "pay" stall'a göre; sürekli tutuş için %50'ye göre bakılırsa 145 g'da 0,98 (mevcutta 1,05): sınır, ama projedeki ölçüt stall.
Robot AM: kafa +145 g (y 1.168), tabandan Pi 58 g + Pi'nin XL4016'sı 60 g çıkarsa AM y 370,5 → 376,9 mm, devrilme eşiği ileri/geri/yana 5,28/4,52/4,71 → 5,19/4,44/4,63 m/s² (pay 3,5/3,0/3,1× → 3,46/2,96/3,09×): fark %2'den az.

## 3. Isı

- Pi 5 yük gücü: 8 GB, boşta **3,2 W**, stress-ng **9,8 W** (jeffgeerling.com/blog/2024/new-2gb-pi-5-has-33-smaller-die-30-idle-power-savings); projedeki tahmin 4/7/12 W (`taban_montaj.py` TUKETIM). Ürün özeti: 5 V/5 A USB-C, 0…70 °C, "kapalı kutuda kapatılmamalı, iyi havalandırılmış ortam" (`raspberry-pi-5-product-brief.pdf`, güvenlik uyarıları).
  Resmi doküman: fan 50 °C altında kapalı, 75 °C'de tam hız, 80-85 °C arası çekirdek kısılır (raspberrypi.com/documentation/computers/raspberry-pi.html).
- Kafada harcanan güç = LCD 2,5 W (Waveshare: 490 mA @5 V) + kamera ~0,5 + Pi (3,2…9,8) + düşürücü kaybı (%90 verim): boşta ~7 W, tipik (Pi 7 W) ~11 W, en kötü ~14,5 W. Şimdi kafada yalnız LCD+kamera ~3 W.
- Kapalı kabuk (tahmini, el hesabı): yüzey 0,19 m² (210×180×150), toplam ısı geçirgenliği ~9 W/m²K (iç+dış, taşınım + ışınım), PETG 2,5 mm (k≈0,2 varsayım) → R ≈ 1,3 K/W → iç hava **~19 K** (en kötü), 14 K (tipik) ortamın üstünde.
  30 °C ortamda iç hava ~49 °C; MG996R sınırı 55 °C, Pi fanı 50 °C'de açılır. Yani kapalı kafada tipik yük sınırda, en kötü yük için havalandırma şart.
- Hava yolu (öneri): Active Cooler fanı üstten emer, kanatçıklardan yana atar. Kart üstünde 68 mm boş yükseklik var. Giriş: arka duvar (z -65), y 190…235, x -40…40 aralığında 10 yarık 3×40 mm = **1.200 mm²**;
  çıkış: iki yan duvar (x ±105), üst bölme y 200…265, z -50…-10, her yanda 6 yarık 3×40 = toplam **1.440 mm²**. Gerekçe: ΔT_hava ≤ 8 K için hava debisi Q/(ρ·cp·ΔT) = 14,5/(1,16·1007·8) = 1,55 L/s ≈ 3,3 CFM; yarık hızı ≤ 1,5 m/s → ≥ 1.030 mm² serbest alan hem giriş hem çıkışta.
  Mevcut 8 yarık (arka kabuk, y 140…176, 8×140 = 1.120 mm²) alt bölmede kalıyor, Pi'ye yardım etmez. Active Cooler'ın debisi doğrulanmadı (üretici vermiyor); kabuğun içindeki sirkülasyon fanla sağlanır.
- Test şartı: kafa kapalı, stres (stress-ng + 30 fps animasyon), SoC ≤ 75 °C ve tilt servosu gövdesi ≤ 50 °C. Yazılımda SoC > 75 °C'de animasyon FPS düşürülür.
- Ses: fan açıkken kafa içi gürültü mikrofona yakın; mikrofonu fandan uzak (ön-alt) koy.

## 4. Boyundan geçecekler ve kesit

Dar boğazlar (kafa_parcalar.py): boyun mili Ø32 (804 mm²), **mil kablo penceresi 13,7×10 = 137 mm²**, servo yuvası arka kanalı 20×7,8 = 156 mm², alt çıkış penceresi 12×12 ≈ 144 mm², çatal deliği Ø28 (616), tabla geçişi 13×24 (312).
Dar boğaz ≈ **137 mm²** (mil penceresi). Kesitler tipik kablo çaplarıyla (tahmini, ölçülecek):

| | Mevcut (Pi tabanda) | Pi kafada |
|---|---|---|
| Boyundan geçen | micro-HDMI→HDMI 1,5 m (Ø4-5 ≈ 12,6 mm²), kamera FPC 1,1-1,3 m (K4; 15 pin ucu ~16 mm, 13,7 mm pencereye yatık sığmaz, tahmini; ≈ 7 mm²), USB LCD dokunmatik+güç (9,6), USB mikrofon (9,6), tilt servo 3 tel (8,5), (hoparlör 2 tel 2,5) | 12 V çift 18 AWG (7,6), ESP32 USB (9,6), Nextion TX/RX 2 tel (2,3; ya da ESP32'ye taşınırsa 0), tilt servo (8,5), (hoparlör 2,5) |
| Toplam kesit | ~50 mm² (pencere doluluğu %37) | ~30 mm² (%22) |
| Kablo yolu (taban_parcalar.py YOL 12) | Pi → (0, 1010, 20): 0,87 m; kafa içi +0,22 m = ~1,1 m (K4: "1,3 m") | taban XL4016 → kafa Pi: 0,91 + 0,22 = ~1,13 m; bağlantı/boşluk payıyla **1,25 m** |

- **Güç:** 12 V + kafada 5 V/5 A düşürücü önerilir. 5 V'u doğrudan çekmek (Pi 3 A tipik, 5 A tepe; 18 AWG 20,95 mΩ/m, gidiş-dönüş 2,5 m): 3 A'de 0,16 V, 5 A'de **0,26 V** düşüm (5,1 V kaynakta Pi 4,84 V görür; konnektör/USB-C kablo ayrıca; Pi 4 için 4,63 V eşiği bilinir, Pi 5 için doğrulanmadı) → ince hat marjinal.
  12 V hatta (Pi 3 A@5,1 V → 1,4 A; tepe 5 A → 2,4 A, %90 verim): 18 AWG'de 0,07 V (%0,6) / 0,12 V (%1,0), 20 AWG'de 0,12 / 0,20 V (%1,6): önemsiz. Akü LiFePO4 12,8 V nominal, düşürücü giriş penceresi bol.
  Örnek modül: Pololu D24V50F5 (6-38 V giriş, 5 V ±%4, 5 A, %85-95 verim, 17,8×20,3×8,8 mm, pololu.com/product/2851; kütle sayfada yok, ~6 g tahmin; 32,95 USD ≈ 1.610 TL, kur 48,878). Ayarlı 5,1 V isteniyorsa daha ucuz 5 A modül olur (fiyat/stok doğrulanmadı). Eldeki XL4016 (65×47×23,5, 60 g) kafada gereksiz ağır.
  Pi'ye USB-C kablo kırığı ile verilirse PD yok → USB 600 mA sınırı; `usb_max_current_enable=1` (E4'te zaten açık iş).
- **ESP32:** USB (CP210x/CH340) 1,25 m, ±90° burulur; yalnız veri (VBUS kesik) kablo, çünkü ESP32 çevre 5 V'tan besleniyor (E4: iki kaynak). UART (3,3 V) seçeneği gürültüye daha açık.
- **Nextion:** UART'ı Pi'den değil **ESP32'den** sür (Pi → ESP32 JSON komutu); böylece boyundan sinyal geçmez, 5 V çevre hattı zaten tabandan göğüse gidiyor (YOL 11). Nextion TX 3,0-5,0 V → okuyan taraf için 1k/2k bölücü (`donanim/datasheet/README.md`). Pi'den sürmek istenirse TX/RX 2 tel ~0,7 m (kesite +2,3 mm²).
- **Hoparlör:** MAX98357A I2S (BCLK ~1,4 MHz) boyundan **geçirilmemeli** (korumasız ~0,7 m, risk; doğrulanmadı). Amfi Pi yanında (kafada, 2 g); hoparlör ya kafada (Ø40×20, 27 g, üst bölmede yer var; tilt'e +27 g) ya göğüste (2 tel). Hoparlör yeri CAD'de hâlâ yok (`kabuk_rapor.py` "hoparlör yeri seçilince"); karar Duffy'nin.
- **Mikrofon:** kafada (USB, Pi'nin USB'sine kısa). CAD'de yeri yok; ReSpeaker Lite ölçüsü doğrulanmadı.
- Boyundan geçen yalnız 12 V, ESP32 USB, tilt servo (6 V + sinyal) ve opsiyonel Nextion/hoparlör kalır; CSI, HDMI ve LCD/mikrofon USB'si kafa içinde kısa kalır. Şerit/HDMI dönen mil içinde bükülmez.

## 5. Etkilenen dosyalar ve iş miktarı (S küçük, M orta, L büyük)

| Alan | Dosya | Değişiklik | İş |
|---|---|---|---|
| Kafa CAD | `kafa/kafa_lib.py` (Pi 5 modeli taban_lib'den), `kafa_parcalar.py` (iskelette 4 ısıl gömme somun yuvası; Pi + cooler + burç + düşürücü parçaları; arka kabukta giriş yarıkları, yan duvarlarda çıkış yarıkları; kablo gösterimi), `kafa_montaj.py` (çakışma, tork, baskı, ısı kontrolü), `kafa_rapor.py` (metinler: FPC/HDMI notları, kablo bölümü), `kafa_gorsel.py` | yeni parçalar + kontroller + yeniden üretim (~2 dk koşu) | **M** |
| Kafa baskısı | `planlama/baski-listesi.md`: kafa iskeleti (116 g) ve arka kabuk yeniden boyut/yarık; yeni küçük parça (düşürücü tutucu) | henüz basılmadı (☐) | **S** |
| Arayüz | `arayuz.py`: `KAFA` (ek kütle, Pi bölgesi), `BOLGELER` (taban Pi 5 ve "Pi 5 fan hava payı" bölgeleri kalkar), `TABAN` (pi, xl[0] "Pi 5,1 V") | yalnız çıkarma/ekleme | **S** |
| Taban | `taban/taban_parcalar.py` (PI_I, pi_del, YOL 7/11/12), `taban_montaj.py` (TUKETIM Pi satırı 12 V hattına; E7 etek ısısı azalır), `taban_lib.py` (PI), rapor metinleri (`taban_rapor.py`) | Pi ve bir XL4016 çıkar, kablo yolu şemaları değişir, elektronik katta yer açılır (Pi 85×56 + fan payı) | **M** |
| Güç planı | `duzeltme-plani.md` (K4 kapanır, E4 12 V + kafa düşürücüsüne göre güncellenir, E7), F3 sigortası 3 A'e inebilir | metin | **S** |
| Çakışma | `carpisma.py`: kabuk zarfı değişmiyor, dış sonuçlar geçerli; kafa×sabit (53 s) ve taban (104 s) bölümleri kontrol için, tam koşu C7 ile bir kerede | makine | **S** |
| Ana montaj | `montaj/ana_montaj.py`, `eklem_dogrulama.py`, `montaj_gorsel.py`, `montaj_rapor.py` | parça/kütle yeniden (~30-40 dk makine) | **M** (makine) |
| Maliyet | `planlama/maliyet.json`: +5 V/5 A düşürücü (Pololu ≈ 1.610 TL ya da ucuz modül), -1 XL4016 (3→2), "Ekran kablosu 1,5 m" → 25-30 cm, "Kamera kablosu 200 mm" → 300 mm, +ESP32 için USB kablo 1,5 m; açık iş "~1 m FPC" ve "kafaya HDMI kablosu" silinir | net etki ± birkaç yüz TL (Pololu seçilmezse nötr) | **S** |
| Yazılım planı | `yazilim-plani.md`: mimari şeması (Pi kafada), Pi↔ESP32 USB 1,25 m, Nextion'u ESP32 sürer (yeni iş: ESP32 Nextion sürücüsü ~1 gün), SoC sıcaklık izleme + FPS düşürme, masa düzeneği aynı kalır (Pi zaten masada) | metin + 1 küçük görev | **S-M** |
| Belgeler | `tasarim/freecad/OZET.md` (kafa ~1,51 kg, taban ~7,39 kg, açık işler), `tasarim/freecad/README.md`, kök `README.md`, `proje-plani.md` (risk satırı), `kafa/rapor.html` | sayılar | **S** |

Toplam: ~1,5 oturum tasarım + kontrol + doküman, ~1 saat makine süresi (kafa 2 dk, taban 2 dk, ana montaj ~40 dk).

## Belirsiz / ölçülecek

1. Pi 5 + Active Cooler gerçek kütlesi (46+12 g `taban_lib.py` değeri; tartı), düşürücü ve kablo kütlesi (120-170 g aralığı varsayım).
2. Active Cooler hava debisi ve kafa kapalı/açık yarıklı **gerçek SoC ve iç hava sıcaklığı** (stres testi; el hesabı ±%30).
3. FPC genişliği (15 pin uç ~16 mm tahmini) ve 300 mm şerit; micro-HDMI→HDMI 25-30 cm kablonun TR stoğu.
4. M2,5 ısıl gömme somun için 5 mm tablada yeterli et (kupon), delik merkezinden et payı 3,5 mm varsayımı.
5. Kablo çapları (kesit tablosu tipik değerlerle), 13,7×10 pencereden tüm demetin fiilen geçmesi (prototip).
6. Hoparlör ve mikrofon yeri (karar), ReSpeaker Lite ölçüsü.
7. MG996R yan yük sınırı (tilt servo mili radyal 4,1 → ~5,0 N); üretici verisi yok.
8. Pi 5'in düşük gerilim eşiği (4,63 V Pi 4 değeri; Pi 5 için resmi doküman bulunamadı).
