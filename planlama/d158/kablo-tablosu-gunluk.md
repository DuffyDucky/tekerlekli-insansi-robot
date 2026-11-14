# Kablo tablosu günlüğü (P10.7a: kabloların tek kaynağı + 16.11 sipariş listesi), 14.11.2026

Ajan A. Kapsam: plan E1 kalemi (kablo tablosu, görünüm, denetim) ve `planlama/maliyet.json`'un kablolama ön kararlarına göre güncellenmesi;
belge tutarlılığı; plan D2. Commit, push, `git add` yok; panoya yazılmadı. Rehber (`rehber/`, `planlama/rehber/`, `tasarim/freecad/`),
`kod/` ve `main` değişmedi; FreeCAD ve `rehber_uret.py` koşulmadı. Devre değeri (pin, direnç, sigorta, kesit) seçilmedi: belgede yazılı
olmayan her şey tabloda `durum: karara bağlı` ve aşağıda "Orkestratöre" (O-1 … O-14). Çalışma ağacındaki eski değişik dosyalara
(`tasarim/freecad/kabuk/gorsel/*.png`, `tasarim/freecad/montaj/yerlesim-kontrol.json`) dokunulmadı.

## 1. Yapılan (dosyalar)

| Dosya | Ne |
|---|---|
| `planlama/adim3/kablolar.json` (yeni) | Tek kaynak: 74 kablo kaydı, 175 damar; renk kuralı, kesit kuralı, acil stop dalları, ortak noktalar, demet sırası, orkestratöre listesi, 62 dökümünün dışarıda kalanları |
| `planlama/adim3/kablolar_uret.py` (yeni) | JSON → `kablolar.md`; FreeCAD'siz, standart kütüphane; `--kontrol` (güncel değilse çıkış 1), kaynak okunamazsa çıkış 2 |
| `planlama/adim3/kablolar.md` (yeni, üretilmiş) | Okunur görünüm: özet, renk / kesit kuralı, acil stop dalları, demet demet (montaj sırasıyla) uç uç damar tabloları, 62 eşlemesi, orkestratöre |
| `planlama/adim3/kablolar_denetim.py` (yeni) | Kalıcı denetim (§5) |
| `planlama/maliyet.json` | Kablolama ön kararları §17 (§6); `tarih` 2026-11-09 → 2026-11-14 |
| `README.md:50`, `planlama/proje-plani.md:10-11` | Maliyet tarihi ve yuvarlak toplamlar |
| `planlama/d158/sonuc-rapor.html` | Yalnız 5 maliyet `data-j` değeri (satır 88, 199–202) |
| `tasarim/Robot-Tasarim-Demosu.html` | `tasarim/cad/demo_uret.py` ile yeniden üretildi (gömülü `maliyet.json`, kuyruk özeti) |
| `planlama/adim3/elektrik.md:5, :305` | Tek kaynağa işaret (satır eklenmedi, mevcut satırların sonuna) |
| `planlama/yazilim-plani.md:33, 34, 53, 58, 59` | GPIO12 → GPIO4, GPIO2 → GPIO19, Nextion → HDMI göğüs ekranı |
| `planlama/d158/testler/T13-rampada-acil-stop.md:64, 81`, `T4-pam8403-ses-karti.md:3, 11, 72`, `testler.html` | GPIO12 → GPIO4; T4'e ses yolu notu; `testler_html.py` ile üretim |
| `planlama/adim5/B-malzeme-plan.md:44` | Tarihçe notu (BC337-40 #2, GPIO19) |
| `planlama/dongu-158.md:164`, `planlama/d158/karar-kuyrugu.md:1235, 1260, 1264` | Başlangıç notları (yerinde, satır eklenmedi) |

Belgelerde satır eklenmedi ve silinmedi; tablodaki `belge:satır` atıfları geçerli kaldı (denetimin `kaynak` sınaması).

## 2. Kaynaklar

- Devre: `planlama/adim3/elektrik.md` (E1–E9, blok şema 323–341, sigorta listesi 360–380, pin planı 472–496, hat C 122–132),
  `planlama/adim3/pin-haritasi.md` sürüm 4 (§9 JSON önerisi 405–451, Y4 / Y5, D1–D9), `planlama/adim3/kablolama-on-kararlar.md`
  (§2–§9, §12 acil stop listesi 355–360, §17), `planlama/adim3/06-aku-secimi.md` (12 AWG ≤ 30 A, şarj cihazı).
- PCA9685 kanalları: `main` dalındaki `kod/jestler/kanallar.yaml` (`git show origin/main:...`, yalnız okundu).
- Boylar: `tasarim/freecad/` altındaki kablo yolu kaynakları ve analiz JSON'ları (yalnız okundu); boyu olan her kayıtta `boy.kaynak`.
- Rehber adımları: rehber kaynağındaki bugünkü kablo / demet tanımları (yalnız okundu); yoksa "öneri".
- 62 sayısı: 10.11 incelemesinin kablo dökümü (depo dışı, salt okuma; yolu ve içeriği depoya taşınmadı).
- Fiyatlar: onaylı satıcı sayfaları 14.11'de okundu (Direnc.net, Motorobit, Robotistan, Robocombo).

## 3. Tablo sayıları

- **74 kablo** (çok damarlı demetler ve çiftler tek kayıt), 175 damar.
- Durum: **karara bağlı 62**, **kablajda teyit edilecek 10**, **kesin 2**. Durum kuralı: `eksik` doluysa karara bağlı; değilse `teyit`
  doluysa kablajda teyit; ikisi de boşsa kesin (denetim sınar).
- Boy CAD'den belli **17**, belli değil **57** (`boy: null`, "P10.7b'de ölçülecek").
- Acil stopta enerjili 44, enerjisiz 30.
- Demet: taban alt kat 12, taban (K1) 17, elektronik katı 10, sonar 3, etek (F1) 4, gövde (K2) 3, boyun 5, kafa içi 11, göğüs 1, kol sağ 4, kol sol 4.
- **Renk kuralı:** iletken rengi kutup gösterir (+ kırmızı, − / GND siyah; listedeki 12 / 16 / 18 AWG silikon kablolar yalnız kırmızı ve
  siyah). Devre türü iki uçta ~2 cm renkli makaronla: kırmızı 12 V bara öncesi, turuncu anahtarlı bara / motor, sarı servo, mavi 5 V,
  yeşil acil stop, mor sinyal / I2C, siyah toprak, beyaz ses; hazır kablolar gri. Rehber çiziminde aynı renkler (hex değerleri tabloda).
  Belgede yazılı kablo rengi yoktu; setteki makaron renkleri doğrulanmadı.
- Çoğu kaydın "karara bağlı" olmasının nedeni: kesiti yazılmamış güç dalları (O-1), 16 / 20 / 22 AWG için kesit-sigorta kuralının
  olmaması (O-2) ve listede sinyal teli olmaması (O-4).

## 4. 62 ile mutabakat

Tam eşleme `kablolar.md` "10.11 dökümündeki 62 kabloyla eşleme" tablosunda; denetim her döküm satırının eşlendiğini sınar.

- **Çıkan (1):** #53 USB ses kartı uzatması (ses ReSpeaker 3,5 mm çıkışından; KOK §5).
- **Birleşen:** #5 (− dönüş damarları ilgili çiftlere), #48 + #49 + #40 → Q01–Q03 (sonar demetleri), #12–#15 tek tek motor kayıtları kaldı.
- **Bölünen:** #8 → G08 + G09, #9 → G10 + G11, #39 → G18 + G19, #41 → A01, A02, A03, A06, #42 → A04, A05, #43 → G20 + G21, #50 → I01 + I02,
  #51 → P01–P03.
- **Uç değişen:** #42 (sürücü IRLZ44N / GPIO2 → BC337-40 #2 / GPIO19), #43 (mini 2 A hat yuvası → kutu F6 3 A), #61 (ses kaynağı ReSpeaker).
- **Eklenen (3):** G01 akü kutup kabloları (döküm XT60'tan başlıyordu), X01 arayüz kartı → ESP32 demeti, AU2 ses bölücüsü → PAM8403.
- Son sayı 74 kayıt; 61'e uydurulmadı (kayıt birimi döküm satırından incedir).

## 5. Denetim betiği

`planlama/adim3/kablolar_denetim.py` (FreeCAD'siz; çıkış 0 geçer, 1 hata, 2 kaynak okunamadı). Sınadıkları: `alanlar` (zorunlu alanlar,
durum kuralı), `iki_uc`, `ayni_nokta` (bir klemens / pin iki ayrı işe verilmemiş; bilinçli ortak noktalar `ortak_noktalar`'da),
`esp32_pin` (`pin-haritasi.md` §9 JSON'u ile birebir: 24 pin + boş GPIO12, DURUM_LED GPIO2 dışarı bağlanmaz), `pca_kanal` (pin haritası ve
`main` `kanallar.yaml`), `kesit` (yazılı kurala göre koruyan sigortaya yetiyor mu; kuralı olmayan kesit karara bağlı olmalı), `acil_stop`
(KOK §12 listesi ve ifadeleri), `kaynak` (her kaydın kaynağı var, `belge:satır` aralığı dosyada var, JSON yolu var), `denetim_62`, `gorunum`.

14.11 koşusu: 10 sınama GEÇER, çıkış 0. `--bozma-denemesi`: 15 bellek içi bozma, **15 / 15 yakalandı** (her sınama için en az bir).
Ayrıca dosyayla bozma (X01 GPIO4 → GPIO2, geçici kopya) çıkış 1; olmayan `--kanallar` dosyası çıkış 2.

## 6. `maliyet.json` değişiklikleri (14.11)

| Satır | Eski → yeni | Fiyat / satıcı (14.11 okundu) |
|---|---|---|
| 77 PAM8403 | model: giriş ReSpeaker 3,5 mm çıkışından, 10 kΩ / 2,2 kΩ bölücüyle; not | değişmedi (21,96, Robotistan) |
| 78 USB ses kartı | not: kablajdan çıktı, yedek olarak siparişte | değişmedi (91,80, Motorobit) |
| 106 Röle sürücüsü | VBsemi IRLZ44NPBF-VB × 2 (Robotistan 24,40) → **BC337-40TA × 3** | 3,02 TL, Direnc.net (2,52 + KDV; marka ONS (Fairchild); stok adedi yazmıyor) |
| 109 K2 | not: sürücü BC337-40 #2, GPIO19 | değişmedi |
| 115 Direnç seti | not: kullanılacak değerler setten; "Nextion RX, MOSFET gate" eski | değişmedi (90,50, Robocombo) |
| 122 Hat sigortası yuvası | adet 5 → **4**; fiyat 36,72 → 37,08 | Motorobit |
| 123 2 A mini | V3'ten çıkarıldı (`ver: v1,v2`; satır silinmedi) | eski 7,34 |
| 127 2 A standart (F5) | fiyat 4,28 → 4,33; not | Motorobit, "Standart Bıçak Sigorta", 19,1 × 18,7 mm, stok 100+ |
| 128 5 A standart (F4) | fiyat 4,28 → 4,33; not | Motorobit, standart, stok 1000+ |
| 136 USB-A uzatma 30 cm (ses kartı) | V3'ten çıkarıldı (koşullu −77,46) | – |
| 137 Hub uzatması | USB 3.0 1 m (Motorobit 214,20) → USB 2.0 A erkek-dişi ~1 m, erkek fiş ≤ 13 × 7 mm; **fiyat bekliyor** (koşullu K4 kaldı) | onaylı satıcılarda bulunamadı |
| 138 L USB-A dirsek | V3'ten çıkarıldı (fiyatsızdı) | – |
| 141 3,5 mm kısa kablo | model: ReSpeaker → bölücü → PAM8403; hâlâ **fiyat bekliyor** | Robotistan 1,5 m tükendi |
| 191 Göğüs HDMI | model: Ø ≤ 6 mm şartı; fiyat 117,10 → 117,59; stok "yok" (sayfada "Tükendi"); çap sayfada yazmıyor | Robotistan |
| 197 (yeni, sona eklendi) | 3 A standart bıçak sigorta (F6) × 1 | 4,33 TL, Motorobit (3,61 + KDV), stok 100+ |

Mini 5 A / 7,5 A × 2 / 10 A satırları (124–126) kaldı: hat yuvaları mini / mikro bıçak alır; §17 yalnız kutudaki mini 2 A'yı çıkarır.

**Toplam:** genel 118.666,22 → **118.577,17 TL** (−89,05; ara −77,44: röle sürücüsü −39,74, hat yuvası −35,28, mini 2 A −7,34, 3 A +4,33,
HDMI +0,49, iki standart sigorta +0,10). Koşullularla 124.573,11 → **124.148,64** (−424,47; ses kartı uzatması −77,46, eski hub uzatması
−214,20 artık fiyatsız). Elde düşülmüş 93.770,47 → 93.681,41; QLED alınırsa 102.071,11 → 101.982,06. V3 kalem sayısı 121 (değişmedi).
Fiyatsız V3 satırı 2: hub uzatması (137), 3,5 mm kablo (141).

**Bağımlılar:** README:50 (≈ 118.600; ≈ 124.100; ≈ 93.700; ≈ 102.000; sipariş paketinin kendi toplamı ≈ 107.600 `F8a-siparis.json`'dan,
değişmedi), `proje-plani.md:10-11`, `sonuc-rapor.html` 5 `data-j` değeri, demo yeniden üretimi. `demo_uret.py` `KALEM_ISARET` korumaları
(indeks 33, 36, 78) tutuyor: satır sona eklendi, "Nextion" metni direnç setinin notunda kaldı. Not: direnç setinin notu demoda hâlâ "eski
tasarım notu" işaretli (işaret bütün nota); 14.11 eki güncel bilgidir.

**Koşan doğrulamalar (hepsi FreeCAD'siz):**

| Betik | Önce | Sonra |
|---|---|---|
| `planlama/adim5/maliyet_toplam.py` | 118.666,22 / 124.573,11 | 118.577,17 / 124.148,64 |
| `tasarim/cad/demo_uret.py` | – | çıkış 0; "UYARI: K11 artık 'kapandı' - sayfa metnini güncelle" |
| `planlama/d158/F9b-dogrula.py --tarayicisiz` | çıkış 1, 2 hata (K11 "karar bekliyor" ↔ kuyrukta kapandı) | çıkış 1, 4 hata: aynı K11 kökü (yeniden üretimle etiket "kuyrukta: kapandı" oldu, F9b bu etiketi kabul etmiyor); maliyet sınaması [3] geçer |
| `planlama/d158/F9c-dogrula.py --tarayicisiz` | çıkış 1, 28 hata | çıkış 1, 28 hata (aynı; maliyet `data-j` hataları `sonuc-rapor.html` güncellenince kalktı) |
| `planlama/d158/F9d-tarama.py --ozet` | çıkış 0 | çıkış 0 (README yuvarlak toplamları yeni değerlerle eşleşiyor) |
| `planlama/d158/testler/testler_html.py --kontrol` | geçer | yeniden üretim sonrası geçer |
| `kablolar_uret.py --kontrol`, `kablolar_denetim.py` | – | güncel; GEÇER |

K11 sorunu bu paketten değil: K11 kablolama ön kararlarında kapandı, `demo_uret.py` `KARARLAR` listesinde ve şablonun göğüs ekranı
kutusunda (`{{K:K11}}`) hâlâ duruyor. Düzeltmek şablonu da değiştirir; demo / sonuç raporu sahibine (P10.9) bırakıldı. (İkinci turda orkestratörün isteğiyle düzeltildi, §13.)

## 7. Tablo ihtiyacı × listedeki miktar (ilk tur; miktar değiştirilmedi, ikinci turda işlendi: §13)

| Kalem | Liste | Tablodan ihtiyaç | Değerlendirme |
|---|---|---|---|
| Sinyal teli / dupont | yok | 16 kayıt (X01, B01–B02, N01–N02, I01–I02, P01–P03, Q01–Q03, G07, G22, A06) | **eksik** (O-4) |
| 12 AWG uç halka pabucu (anahtar, sigorta kutusu, bara) | yalnız akü M5 pabucu | G02–G05 uçları | büyük ihtimalle eksik; uç türü O-3'e bağlı |
| WAGO 2273-203 | 10 | bara ≈ 8 iletken + yıldız ≈ 10+ toprak; 12 AWG girmez | büyük ihtimalle eksik (sayım tahmini; O-3) |
| 2 pin klemens | 4 | ≥ ~9 bağlantı noktası (tahmin) | büyük ihtimalle eksik (O-6, O-7) |
| Servo uzatma 100 cm | 19 | ≥ 16 (kol 8 + S2 4 + S1 2 + pan / tilt); PCA köprüleri uzatmadan kesilirse ≈ 24 | sınırda; boylar P10.7b'de |
| 16 AWG kırmızı / siyah, 1 m | 1 + 1 | SV1 + SV2 ≈ 0,6 m çift + SV3 + hat yuvası ekleri | sınırda |
| 18 AWG kırmızı / siyah, 7 m | 7 + 7 | G21 1,72 m çift + G17 (boy yok) + öbürleri | yeter görünüyor |
| 2200 µF kondansatör (XL C çıkışı, EL:129 "önerilir") | yok (yanlış: listede 4 vardı, dağıtım A / B; §13) | 1 | eksik (öneri düzeyinde) |
| BC337-40, 1N4007, sigortalar, hat yuvası | 3, 2, standart 2 / 3 / 5 A, 4 | 2 + 1, 2, F4 / F5 / F6, 4 | yeter |

## 8. Plan D2 (devreye alma kuralı, klemens serisi, şarj gerilimi)

- **Klemens serisi** → O-3: WAGO 2273 en çok 2,5 mm² (EL:93); 12 AWG ana dönüş ve 20 A bara için seri seçilmemiş. Karar gerekir.
- **Şarj gerilimi** → O-13: akü raporu 14,4 V cihaz ve "14,6 V'luk cihaz verilmemeli" (06-aku-secimi.md:165), EL:93 IMAX B6 "14,6 V kesme
  cihazda ölçülecek", EL:282 "LiFePO4 şarjda 14,6 V" (TVS gerekçesi), EL:67 / T7 12,8–14,4 V. Metinler tek değere ancak karar ya da ölçümle
  iner. Karar gerekir.
- **Devreye alma kuralı** → O-14: EL:260 "şimdilik yazılım kuralı + watchdog"; kendini tutma kontağı ve elde acil stop (Ö4) kararsız.
  Karar gerektirmeyen kısım işlendi: tablo bugünkü devreyi (GPIO4 / GPIO19, E9 dizisi, Y4 / Y5) taşır; `yazilim-plani.md` dizisi düzeltildi.

## 9. Orkestratöre (karar gerekenler; seçenekler `kablolar.md` "Orkestratöre" bölümünde)

O-1 kesiti yazılmamış güç dalları (21 kayıt) · O-2 16 / 20 / 22 AWG kesit-sigorta kuralı (18 kayıt) · O-3 klemens serisi · O-4 sinyal teli
listede yok · O-5 sigortasız algı telleri G07 / G22 · O-6 acil stop düğümünün yeri + Ö4 · O-7 taban dağıtım noktaları (BTS VCC, çevre 5 V,
EN pull-down) · O-8 pan / tilt sinyalinin hat C ile birleşimi · O-9 ses bölücüsünün yeri · O-10 K4 açık · O-11 şartlı hazır kablolar onaylı
satıcıda yok (USB 2.0 küçük fiş, Ø ≤ 6 HDMI) · O-12 bas-konuş düğmesi listede var, pin / kablo yok · O-13 şarj gerilimi · O-14 devreye alma kuralı.

## 10. Belge tutarlılığı ve kalanlar

- `elektrik.md`: seçim **kablo listesi tek kaynak `kablolar.json`**; `elektrik.md` devre kararlarının ve gerekçelerin yeri, ayrı kablo listesi
  tutmaz (satır 5'e işaret, 305'e kısa atıf).
- Düzeltildi: `yazilim-plani.md:33, 34, 53, 58-59`; `T13:64, 81`; `T4:72` + başa ses yolu notu; `maliyet.json:106, 109, 115` notları;
  `B-malzeme-plan.md:44` tarihçe notu.
- **Bu pakette değişmedi (listede kalır):** `tasarim/freecad/rehber/rehber_metin.py:637` "K2 = GPIO2 LED" uyarısı ve `:817` "K11 b"
  (P10.7b); `KY/uygulama-notu.md:98, :102-134`, `arayuz.py` `SES_USB`, `kablo_yolu_ekran.py` `KABLO`, rehber şemaları 7 ve 8
  (`tasarim/freecad/`, dokunulmaz); `elektrik.md:29, :278, :511` "tepe hesaplanmadı" ifadeleri (kablo / pin işi değil); `yazilim-plani.md:84`
  Y10 satırındaki Nextion (iş planı satırı, listede yoktu); T4 kâğıdının ReSpeaker yoluna göre yeniden yazılması (yalnız not eklendi).
- Belgeler arası: KOK §3 / §17 2 A ve ikinci 5 A standardı "bekliyor" der, oysa MJ:127 / 128 09.11'den beri vardı; EL:370 "yuva × 3" ile EL:41
  "× 4" farklı. (İkinci turda eşitlendi, §13.)

## 11. Doğrulanamayanlar

- Boylar: 57 kablonun boyu yok; 17'si CAD yolundan, hiçbiri ölçülmedi.
- Direnc.net BC337-40TA stok adedi; Motorobit sayfalarında fiyatın KDV dahil olduğu açıkça yazmıyor (3,61 + KDV = 4,33 hesap).
- MJ:191 HDMI'nin çapı (sayfada yok) ve stoku (14.11 tükendi); Ø ≤ 6 şartını karşılayıp karşılamadığı bilinmiyor.
- Makaron setinin renkleri; direnç setinin içeriği elde sayılmadı.
- §7'deki ihtiyaç sayıları kayıt sayımından ve tahminden; boylar gelince yeniden sayılır.

## 12. Orkestratör kararları (14.11)

Orkestratör 14.11'de O-1 … O-14'ü kararlaştırdı. Karar metni, tabloda uygulanışı ve veren her karar için `planlama/adim3/kablolar.json`
`kararlar` alanında (görünüm `kablolar.md` "Orkestratör kararları (14.11)"); `kablolama-on-kararlar.md` §18 kısa özet.

| Kod | Karar | Uygulama |
|---|---|---|
| O-1 | c: listedeki kesitler, koruyana yeten en ince | Uygulandı; G11'de "direnç sonrası kol" kuralı uygulanmadı (aşağıda), M01–M04'te uygulanamadı (O-16) |
| O-2 | a + b: kaynaklı akım tablosu, dönüştürücü kuralı, servo uzatması istisnası | Uygulandı; temkinli tablo 12 AWG'yi 25 A'e indirdi → yeni çelişki O-15 |
| O-3 | a, yoksa b | a onaylı satıcılarda yok → b (bara + halka pabuç); bara ürünü de bulunamadı (fiyat bekliyor) |
| O-4 | a + b | Uygulandı; 22 AWG rulo stokta yok (fiyat bekliyor); pense yok → lehim + makaron |
| O-5 | a | G07 uygulandı; G22 uygulanamadı (O-18) |
| O-6 | a / c | Uygulandı (A02, A04, A06); Ö4 açık |
| O-7 | a | Uygulandı (B01, B02, G19, X01); BTS VCC kablajda teyit |
| O-8 | kol yöntemi | Kollarda yöntem yazılı (dağıtım kartı, EL:225) → kafa için dağıtım kartı C (SV3, P03, S09, S10) |
| O-9 | a | Uygulandı (AU2) |
| O-10 | b | Uygulandı (U01, U03, AU1, AU3) |
| O-11 | b | Uygulandı; H02, U03 kablajda teyit |
| O-12 | açık | Tablo ve liste değişmedi; soru için bilgi §13 |
| O-13 | metin | `elektrik.md:67, :93, :282`, T7:17, :25, KOK KT8 |
| O-14 | a | Kablaj değişmedi |

## 13. İkinci tur (14.11, bitiş ≈ 04:25)

**Sonuç:** kesin 32, kablajda teyit edilecek 30, karara bağlı 12 (ilk tur: 2 / 10 / 62). Karara bağlı kalanların hepsi insan kararı
bekliyor: G01–G05 (O-15), M01–M04 (O-16), G06 (O-17), G22 (O-18), G20 (K52).

**O-2 kaynakları (14.11 okundu):** 33 CFR 183.425 Table 5, 80 °C sütunu (<https://www.law.cornell.edu/cfr/text/33/183.425>) ve NFPA 79
(2018) Table 12.5.1, 75 °C sütunu, 30 °C ortam (Lutze'nin yeniden basımı, PDF metni okundu; bağlantı `kablolar.json`). Temkinli (küçük)
değerler: 12 AWG 25 A (CFR 35), 16 AWG 10 A (CFR 20), 18 AWG 7 A (CFR 15), 20 AWG 5 A, 22 AWG 3 A, 24 AWG 2 A (CFR 18 AWG'den başlar).
Orkestratörün beklediği mertebelerden ikisi farklı çıktı: 16 AWG 15 değil 10 A; 12 AWG kayıtlı 30 A değil 25 A. Yalıtım sınıfı satıcı
sayfalarından (12 / 16 AWG "PVC, 80 °C"; 18 / 20 AWG silikon 200 °C); demet düzeltmesi uygulanmadı.

**Uygulanmayan / itiraz:**
- **G11 (O-1):** ön şarj direnci sonrası kol. K1 kapalıyken anahtarlı bara bu kolu öbür yandan F1 20 A ile besler; kısa devrede akımı direnç
  sınırlamaz. "Direncin akımına göre kesit" güvensiz → F1'e göre 12 AWG. Kart ucundaki 5,08 mm klemens 12 AWG almaz: lehim ya da pabuç (teyit).
- **G22 (O-5):** PC817 #2 hazır modül; seri direnç modülün üstünde, değeri sayfada yok (EL:235). Kaynak ucuna direnç koymak yeni devre değeri
  → uygulanmadı, O-18.
- **M01–M04 (O-1):** motorun kendi kablosu, kesiti belgede yok → O-16.
- **G01–G05 (O-2):** temkinli tabloda 12 AWG ≤ 25 A, ana hat 30 A ile korunuyor → O-15 (devre değeri değiştirilmedi).
- **G06:** kesit 16 AWG oldu (10 A ≤ 10), ama uçlar yazılı değil → O-17.

**Satıcı araması (14.11):** WAGO 221-61x Motorobit, Robotistan, Robocombo, Direnc.net'te bulunamadı (spesifikasyon üretici sayfasından
doğrulanamadı: 403). Yedek b'nin M5 barası da bulunamadı; adaylar `maliyet.json` notunda. Sarı halka pabuç RV 5.5-5 (4–6 mm², 10'lu)
Motorobit 49,44 TL; delik çapı sayfada açık yazmıyor (5 varsayımı), 12 AWG (3,31 mm²) pabucun 4 mm² alt sınırının altında: sıkmada teyit.
22 AWG renkli rulo: Robocombo "Stok:0", Robotistan "Satışa Kapalı". Dupont kiti, jumper setleri, 20 AWG Motorobit. Robocombo sayfalarında
fiyat okunamadı (JavaScript); 09.11 fiyatları korundu.

**Boy tahmini:** 57 kablo için `boy_tahmin` (etiket "tahmin, P10.7b'de ölçülecek"): `tasarim/freecad/montaj/montaj-analiz.json` ev pozu parça
merkezleri arası Manhattan uzaklığı × 1,25 + 150 mm, 50 mm'ye yukarı (× 1,25 ve 150 mm EL:70'ten; orada 150 mm yalnız hub kablolarında, burada her kabloya üst sınır payı); CAD'de olmayan uçlar için vekil parça kayıtta yazılı.
Sabitler: G01 100, G02 150 (akü raporu "≤ 15 cm"; CAD'deki ana sigorta zarfı akü merkezinden 177 mm: yerleşimde teyit), SV3 300, AU2 100,
C01 300. FreeCAD koşulmadı; JSON yalnız okundu.

**Malzeme:** ihtiyaç × 1,3 (`kablolar.md` "Malzeme özeti"); denetim `malzeme` sınaması liste adedini sınar.

| Kalem | Önce → sonra | Fiyat / satıcı |
|---|---|---|
| Servo uzatma | 19 → 24 | 44,71 Robotistan (sayfada "Tükendi") |
| 12 AWG kırmızı / siyah | 2 → 7 / 2 → 3 m | 118,00 Robocombo (09.11) |
| 16 AWG kırmızı / siyah | 1 → 6 / 1 → 6 m | 60,50 Robocombo (09.11) |
| 18 AWG kırmızı / siyah | 7 → 13 / 7 → 11 m | 43,26 Motorobit |
| 20 AWG kırmızı / siyah | yeni 1 + 1 m | 24,72 Motorobit |
| 2200 µF | 4 → 5 | 4,33 Motorobit |
| Pertinaks / 5,08 klemens | 5 → 6 / 4 → 12 | 24,20 Direnc.net / 5,50 Robocombo |
| Halka pabuç sarı 10'lu | yeni 2 | 49,44 Motorobit |
| Halka pabuç kırmızı / mavi, güç barası, 22 AWG sinyal teli | yeni 2 / 2 / 4 rulo | fiyat bekliyor |
| Dupont kiti / jumper D-D / jumper E-D | yeni 1 / 1 / 1 | 444,96 / 43,26 / 49,44 Motorobit |

Toplam (`planlama/adim5/maliyet_toplam.py`): genel 118.577,17 → **121.725,12** (+3.147,95); koşullularla 124.148,64 → **127.296,59**
(+3.147,95). Fiyatsız kalem 2 → 5 (V3'te). Bağımlılar güncellendi: README:50, `proje-plani.md:10-11`, `sonuc-rapor.html` (dört `data-j`),
demo yeniden üretildi.

**Düzeltme (ilk tur):** §7'de 2200 µF için "listede yok" yazılmıştı; yanlış. Listede 4 vardı (dağıtım kartı A / B, 2'şer, EL:225); eksik
olan XL C'ninki (EL:130) → 5.

**Belge tutarlılığı:** KOK §3 / §10 / §14 / §17 "bekliyor" notları `maliyet.json` ile eşitlendi (standart 2 / 3 / 5 A 4,33 TL; hub
uzatması ve 3,5 mm kablo hâlâ fiyat bekliyor; HDMI 117,59 TL "Tükendi"). EL:370 "yuva × 3" A / B / C içindir, şarjın dördüncü yuvası
EL:372'de: toplam 4 (tablodan G06, G14, G15, G16); EL:370'e açıklama eklendi, EL:41 ve `maliyet.json` zaten 4. `elektrik.md` sonuna
üretilmiş "dal başına kesit" bloğu (tek kaynak tablo; `kablolar_uret.py --kontrol` ve denetim sınar). EL:266 / :429 / :449 ani akım
hesabı 4 × 2200 µF ile; 5. kondansatör not edildi, hesap yeniden yapılmadı.

**F9b:** `demo_uret.py` `KARARLAR`'dan K11 çıkarıldı, şablonun göğüs ekranı kutusundaki `{{K:K11}}` düz metin oldu ("kutunun F6 yuvası (K11 a)").
Kuyrukta kapalı olanlardan listede yalnız K11 vardı (K1, K10, K14, K56, K57, K58 listede değildi). F9b 0 hata (ilk tur öncesi 2, ikisi de K11).

**Denetim:** yeni sınamalar `tahmin`, `klemens`, `malzeme`; `kesit` genişledi (kaynakların küçüğü, kayıtlı istisna, "kesit-koruma:" kararı)
ve `gorunum` `elektrik.md` bloğunu da sınar. 27 bozma denemesinin 27'si yakalandı. Çıktıda istisna (10) ve kesit-koruma kararı bekleyen
(10) sayıları yazılır.

**O-12 için bilgi (tablo ve liste değişmedi):** düğme `maliyet.json`'da "Bas-konuş düğmesi" (43 mm arcade, Robotistan 76,24). CAD'de
(`montaj-analiz.json` parça listesi) düğme yok, belgelerde yeri yazılı değil. Kullanım: `yazilim-plani.md:23` (eski satır, bas-konuş →
ReSpeaker), `proje-plani.md:141, :225`, README:72; `main` kodunda `kod/robot/tetik.py` `GpioTetik`, `ayarlar.yaml` `tetik.saglayici: ses`
(varsayılan düğmesiz), `gpio_pin: 17` (BCM, fiziksel pin 11, GND'ye); `OKU_BENI.md:231` "GPIO17 ile GND arasına"; `Y2b-gunluk.md:84` Efe
düğmesiz `SesTetik`'i seçti. Yani düğme Pi'ye bağlanır (Pi kafada); ESP32 pini gerekmez.

**Ahmet'e:** (güç barası üçüncü turda kalktı, §14); 22 AWG sinyal teli,
ince uç pabucu, USB 2.0 uzatma ve 3,5 mm kablo onaylı satıcılarda yok (başka satıcı Ahmet'in kararı, O-11 a); servo uzatma sayfada
"Tükendi"; Ö4.

**Doğrulanamayanlar:** WAGO 221-61x ve 2273 üretici verisi (üretici sayfası okunamadı; 2273 değerleri satıcıdan); 5,08 mm klemensin kesit
sınırı; sarı pabucun delik çapı ve 12 AWG'de sıkma; Robocombo 14.11 fiyatları; BTS7960 VCC'nin dış 5 V istediği; boy tahminleri
(üst sınır, ölçüm değil); NFPA 79 değerleri standardın kendisinden değil, üretici yeniden basımından.

## 14. Üçüncü tur: orkestratör kararları O-15 … O-18 ve revizeler (14.11, bitiş ≈ 04:40)

Orkestratör G11 ve G22 itirazlarını kabul etti ve şunları kararlaştırdı (depoda "orkestratör kararı, 14.11"; `kablolar.json` `kararlar`,
`kablolama-on-kararlar.md` §18):

| Kod | Karar | Uygulama |
|---|---|---|
| O-15 | 12 AWG / 30 A değişmez; kayıtlı istisna `ana-hat-12awg` | G01–G05 kablajda teyit |
| O-16 | motorun fabrika kablosu değişmez; kayıtlı istisna `motor-fabrika-kablosu` | M01–M04 kablajda teyit |
| O-17 | şarj kolu: + ana sigortanın yük tarafı / ana anahtarın akü tarafı, − yıldız; 10 A sigorta akü tarafındaki ucun dibinde | G06 kablajda teyit; EL:372 "akü +, ana anahtar öncesi" ile uyumlu, kayıtlı kararla çelişki yok |
| O-18 | b: G22'nin bara ucunda hat sigortası + 2 A | G22 kesin; hat yuvası 4 → 5 |
| O-3 r | hazır güç barası yok; M5 saplama + yaylı pul + somun üstünde pabuç yığını, basılmış tutucu (CAD P10.7b); saplamada ≤ 5 pabuç | yıldız 11 iletken → 3 saplama (2 köprü), anahtarlı bara 8 → 2 (1 köprü); denetim düğüm kapasitesini sınar |
| O-4 r | Dupont kiti çıkar; uç olarak jumper kablolarının fabrika sıkılı dişi uçları | jumper dişi-dişi 1 → 3 |

**Sonuç:** kesin 33, kablajda teyit edilecek 40, karara bağlı 1 (G20, K52).

**Ana hattın beklenen sürekli akımı (`ana-hat-12awg`):** akım bütçesinin toplam satırı (EL:355, "ESKİ" işaretli) yoğun 14,6 A, teorik tepe
21,8 A (4 motor durmada). Göğüs ekranı (~0,5 A, EL:349) ve kafada yalnız Pi hattının tepesi (4,5 A @5 V → ≈ 1,95 A akü tarafında; eskisi
1,62 A) eklenince tepe ≈ 22,6 A (bu günlükteki hesap; kafanın tam tepesi hesaplanmadı). Zaman ortalaması yoğunda 104 W / 12,8 V ≈ 8,1 A
(EL:420). Hepsi **25 A'in altında**.

**Yalıtım sınıfı:** Robocombo 12 AWG sayfası (ikinci turda, 14.11 okundu) ürün adında "silikon", tablosunda "PVC, 80 °C" diyor; ad ile
tablo çelişiyor. İstisna kaydına yazıldı, teslimde kablo üstündeki yazıdan teyit.

**Motor (`motor-fabrika-kablosu`):** durma akımı 2,8 A (tahmini, EL:157; 9 kg·cm senaryosunda 1,2 A, EL:161); aynı yandaki iki motor tek
BTS çıkışına paralel, yan başına ≈ 5,6 A. BTS7960 için belgelerde akım sınırı olarak yalnız çipin 43 A değeri (01-donanim-maliyet.md:122)
ve satıcı adındaki "40 Amper" var; kablo koruması değil, kısa devrede koruma F1 20 A.

**Uygulamada düzeltme (O-18):** orkestratör "2 A standart bıçak" yazdı; listedeki hat sigortası yuvası (Motorobit, "Mini / Micro") mini
bıçak alır, bu yüzden 2 A **mini** (listede V3'ten çıkarılmış "2A Mini" satırı geri döndü). Kararın amacı (bara ucunda 2 A) değişmedi.

**Pabuçlar (M5, Motorobit, 14.11 okundu):** sarı RV 5.5-5 49,44 TL (2 → 3 paket; 12 AWG uç ≈ 19); mavi RV 2-5 (1,5–2,5 mm²) 24,10 TL
× 2 (16 AWG uç 9); kırmızı RV 1.25-5 (0,5–1,5 mm²) 19,78 TL × 1 (18 AWG 3 + G22 − 22 AWG 1; 0,33 mm² aralığın altında, uç katlanır,
teslimde denenir). Sarı pabucun 12 AWG'yi tutmaması için doğrulanmış bir çözüm bulunamadı: teslimde denenir. Bara saplaması (M5 × 25
cıvata + somun + yaylı pul, 6 takım): listedeki M5 × 12 yığın için kısa, M5 somun ve yaylı pul yok → yeni satır, fiyat bekliyor.

**Dişi uç sayımı (O-4 r):** sinyal kayıtlarında erkek başlıklı kartlara giden uçlar: ESP32 30, PCA9685 21, HC-SR04 12, BTS7960 12, dağıtım
kartları 10, BNO055 4 = 89 (arayüz kartı lehim, PC817 vidalı klemens, enkoder fişi sayılmadı) × 1,3 = 116 → dişi-dişi 40'lı (ortadan
kesilince 80 dişi uç) × 2 + 1 set masa testi; erkek-dişi 1 kalır. Sıkma pensesi onaylı satıcılarda bulunamadı (Robotistan'daki iki pense
"Tükendi", fiyat yok; SN-28B görülmedi).

**Miktar düzeltmesi (150 mm pay):** ikinci turda her tahmine eklenen 150 mm kapak sökme payı EL:70'te yalnız hub kablolarında; tahmin
edilen kablolarda hub kablosu yok ve kısa kart içi tellerde (ör. X01'in 14 damarında damar başına) metreyi şişiriyordu. Kaldırıldı
(`boy_tahmin_kurali`: × 1,25, 50 mm'ye yukarı); 52 tahmin yeniden hesaplandı. Sonuç: servo uzatma 24 → 23, 12 AWG kırmızı 7 → 5, 16 AWG
6 → 5 (×2), 18 AWG kırmızı 13 → 11, siyah 11 → 9, sinyal teli 4 → 3 rulo.

**Kalem kalem döküm (pay hariç / %15 pay dahil, TL):**

| Kalem | İkinci tur | Üçüncü tur | Toplam fark |
|---|---|---|---|
| 12 AWG kırmızı (118,00/m) | +590,00 | −236,00 | +354,00 |
| 12 AWG siyah | +118,00 | 0 | +118,00 |
| 16 AWG kırmızı / siyah (60,50/m) | +302,50 / +302,50 | −60,50 / −60,50 | +242,00 / +242,00 |
| 18 AWG kırmızı / siyah (43,26/m) | +262,50 / +175,98 | −86,52 / −86,52 | +175,98 / +89,46 |
| 20 AWG kırmızı / siyah | +24,72 / +24,72 | 0 | +24,72 / +24,72 |
| Servo uzatma | +227,16 | −44,71 | +182,45 |
| 2200 µF | +4,53 | 0 | +4,53 |
| Pertinaks | +24,20 | 0 | +24,20 |
| 5,08 mm klemens | +44,00 | 0 | +44,00 |
| Sarı pabuç | +98,88 | +49,44 | +148,32 |
| Mavi / kırmızı pabuç | – | +48,20 / +19,78 | +48,20 / +19,78 |
| Dupont kiti | +444,96 | −444,96 | 0 |
| Jumper dişi-dişi / erkek-dişi | +43,26 / +49,44 | +86,52 / 0 | +129,78 / +49,44 |
| Hat sigortası yuvası | – | +37,08 | +37,08 |
| 2 A mini | – | +7,34 | +7,34 |
| **Ara toplam** | **+2.737,35** | **−771,35** | **+1.966,00** |
| **%15 pay dahil (genel)** | **+3.147,95** | **−887,05** | **+2.260,90** |

Genel 118.577,17 (P10.7a ilk tur) → 121.725,12 (ikinci) → **120.838,07 TL**; koşullularla 124.148,64 → 127.296,59 → **126.409,54**.
Fiyatsız (V3) 5 → 4: USB 2.0 uzatma, 3,5 mm kablo, 22 AWG sinyal teli, bara saplaması. Bağımlılar güncellendi: README:50,
`proje-plani.md:10-11`, `sonuc-rapor.html` (dört `data-j`), demo yeniden üretildi.

**Tam ad araması (orkestratörün 8. maddesi):** `planlama/d158/testler/T7-gogus-ekrani-12v.md:127` "Ahmet" oldu. `git grep` ile tam ad izlenen 39
dosyada, 84 satırda geçiyor (değiştirilmedi; liste orkestratöre raporda). Çoğu F4b kararıyla resmî ad olarak yazılmış satırlar (README:59,
`Lale-Proje-Ozeti.txt:21`, `kararlar-2026-10-29.md:1`, `dongu-158.md:3`, test kâğıtlarının karar satırları, brief'ler).

**Denetim:** istisna kaydında gerekçe / şart / kontrol / karar alanları zorunlu; çıktıda istisna adı başına kablo sayısı; saplamalı
düğüm kapasitesi (saplama × 5 − 2 × köprü) sınanıyor; tahmin kuralı JSON'dan okunuyor. 31 bozma denemesinin 31'i yakalandı.

**Ahmet'e (ek):** sıkma pensesi + Dupont uç kiti isterse daha temiz iş: onaylı satıcılarda pense bulunamadı (fiyatsız; yurt dışında SN-28B
sınıfı 17–36 USD görülüyor, onaylı satıcı değil); kit 444,96 TL (Motorobit) listeden çıktı.

## 15. Düzeltme turu 1 (14.11, bitiş ≈ 05:41; devamı §15.9)

Bağımsız kontrol `planlama/d158/P107a-kontrol.md` (DÜZELTME GEREKLİ): tablonun değerleri doğru; durduran iki bulgu (D1 denetim betiği
elektrik güvenliğinde dişsiz, D2 16.11 sipariş paketi bayat) ve 17 açık iş maddesi. Orkestratörün kararları (madde 1 – 11) uygulandı;
uygulanamayan tek karar madde 1'in saplama sayısı (aşağıda, O-22).

### 15.1 D1: denetim betiği

Tablo şeması 3. sürüm (`planlama/adim3/kablolar.json`): `dugumler` (294 uç: parça, ağ, `gpio` / `pca_kanal` sayı alanı), `aglar` (kutup,
gerilim, sınıf; GND tek ağ, 5V-pi ve 5V-cevre ayrı sınıf), `koruyucular` (akımı sınırlayan her eleman: giriş, çıkışlar, sınır, kaynak),
`anahtarlar` (kontak / mantar / geçiş), `ic_baglar`, `ayri_topraklar`, `yildiz_noktasi`, `parca_beslemesi`, `dallar` (dal → eleman + §12
ifadesi), `devre_turleri`, `zinciri_kesen_turler`, `malzeme_ust_esik`. Kablo başına `koruma` artık koruyucu kimliği, `besleme_zinciri`
makine okunur liste (paralel eleman iç liste). `acil_stop_dallari` listesi kaldırıldı.

Yeni / yeniden yazılan sınamalar (`planlama/adim3/kablolar_denetim.py`):

| Sınama | Ne yapar |
|---|---|
| `ag` | her uç `dugumler`'de; telin iki ucu aynı ağda (arada `ara_koruyucu` varsa giriş / çıkış ağları); güç ucu adlı düğümün ağı yazılı; 5V-pi ↔ 5V-cevre hiçbir telde, köprüde ya da elemanda birleşmez |
| `yer_tutucu` | kesin kayıtta `?`, `…`, "öneri", "TBD", boş sonlandırma yasak |
| `esp32_pin`, `pca_kanal` | GPIO / kanal numarası düğümün sayı alanından (yazım biçiminden değil); pin haritası §9 ve `main` `kanallar.yaml` ile |
| `kesit` | devre türünden bağımsız, akım taşıyan her + / − damar; koruyan eleman devrenin yapısından (`koruyucular` + `anahtarlar` grafında kaynağa yürüyerek), kayıttaki `koruma` ile karşılaştırılır; sınır = tablo × ortam katsayısı; sınırı belgelenmemiş korumada (D24V50F5, SY8205) kayıtlı istisna ya da karara bağlı şart |
| `donus` | her güç kablosunda − damar ya da `ortak_donus`; dönüş + damarından ince değil; bütün dönüş düğümleri yıldız noktasına varır (`ayri_topraklar` hariç); motor çıkışı çift damar |
| `acil_stop` | kablonun bayrağı besleme zincirinden hesaplanır (zinciri kesen tür: kontak, mantar); kayıttaki `besleme_zinciri` devreden türetilenle aynı; her dal §12'nin (KOK:351-363) Enerjili / Enerjisiz listesindeki ifadesiyle karşılaştırılır |
| `kaynak` | gösterilen satır aralığında kablonun ayırt edici terimlerinden biri (kimlik, uç parçaları, "<awg> awg") geçer; eleman kaynakları da |
| `malzeme` | iki yönlü: eksik (ihtiyaç × 1,3 > liste) ve fazla (liste > `malzeme_ust_esik`: paket yuvarlaması + 1 birim) |
| `alanlar` | `devre`, `dal`, `koruma` kapalı listelerden (`devre_turleri`, `dallar`, `koruyucular`) |
| `klemens` | saplama başına en çok 4 pabuç (köprü uçları dahil: n saplama n × 4 − 2(n − 1)); "klemens:" teyitli tür kesin olamaz |

Bozma denemeleri: kendi 49 + kontrolün kaçan 10'u = **59, hepsi yakalandı** (`--bozma-denemesi`, çıkış 0).

| Kontrolün bozması | Eski betik | Şimdi yakalayan |
|---|---|---|
| B3 `ESP32 · GPIO 12` (boşluklu) | kaçtı | `ag`, `esp32_pin`: uç düğüm listesinde yok |
| B4 G18'in − damarı silindi | kaçtı | `donus`: + var, − / `ortak_donus` yok |
| B5 S03 ucu `?` | kaçtı | `yer_tutucu`, `ag` |
| B6 G16 "sinyal", 22 AWG + 5 A | kaçtı | `kesit`: 22 AWG düzeltmeli 2,46 A < hat-C 5 A (devre türü artık muafiyet değil) |
| B8 G12 F4 dalına, enerjili | kaçtı | `acil_stop`: dal F4, zincirden anahtarlı bara |
| B9 G17 koruması F4 | kaçtı | `kesit`: devreden F3 |
| B10 X01 ESP32 VIN Pi hattından | kaçtı | `ag`: 5V-pi ↔ 5V-cevre birleşiyor |
| B11 G08 kaynağı `elektrik.md:1` | kaçtı | `kaynak`: satırda kablonun terimi yok |
| B14 SV1 koruması 2 A, 22 AWG | kaçtı | `kesit`: koruma devreden XL4016-A |
| B15 servo uzatma 23 → 230 | biçimden | `malzeme`: üst eşik 24 m |

### 15.2 D2: sipariş paketi

Üretici betik yok (paket ajan eliyle yazılmış), yeniden üretilmedi. `planlama/d158/F8a-siparis.md` başına 14.11 notu (orkestratörün metni)
ve 34 satırlık "paketten bu yana değişen kalemler" tablosu (satıcı, adet, birim fiyat, bağlantı; karşılaştırma `maliyet.json` commit
`76fd4b2` (P8.1) → bugün); S87 IRLZ44N **ALMA**, §5.1'deki S87 satırına da işaret. Not 47 satır ekledi; `F8a-kontrol.md` ve
`F4c-kontrol.md`'deki `F8a-siparis.md:NN` atıfları 09.11 hâline göre (notta yazılı). `F8a-siparis.json`'a yalnız üst düzey
`guncelleme_14_11` anahtarı eklendi (var olan yapı aynı; F9c / F9d okuyor). Bağlantılar `maliyet.json`'a çevrildi: `proje-plani.md:92`,
`karar-kuyrugu.md:43, :499, :512`, `README.md:50` (paket toplamı ≈ 107.600 metni F9d için duruyor, "bayat" notuyla).

### 15.3 Kontrolün 17 açık iş maddesi

| # | Konu | Ne yapıldı |
|---|---|---|
| 1 | saplama başına 5 pabuç | sınır 4 (ABYC E-11; `bara-pabuc`, denetim). "Yıldız 4 / anahtarlı bara 3 saplama" sığmadı → geçici 5 + 4 saplama, 10 takım, **O-22** |
| 2 | XL4016 "8 A" | `koruyucular.XL4016-*` 10 A (çip sınırı, tipik); "8 A" `anma` alanında. `servo-uzatmasi` şartına tezgâh kısa devre denemesi, ölçüt T8 E bölümü (≤ 10 A'de kesiyor / düşürüyor, uzatma < 80 °C). SV1–SV3 ve G19 kurala uymadı → **O-20**, **O-19** |
| 3 | motor istisnası gerekçesi | "F1 kabloyu korumaz"; koruma motor sargısı + BTS7960 akım sınırlama / ısıl kapatma + yazılım (IS → EN). Yazılım şartı aşağıdaki "Efe'ye bildirilecek" listesinde, kural numarası verilmedi |
| 4 | ortam sıcaklığı | katsayı etek 45 °C 0,82, kafa 49 °C 0,75 (NEC 310.15(B)(1), ikincil kaynak). (a) G06 sigortası 10 → 7,5 A (IMAX B6 en çok 5 A, 16 AWG düzeltmeli 8,2 A); (b) K03 20 → 18 AWG; (c) bir kalın kesit yetmeyen 15 kablo karara bağlı: O-19 (11), O-20 (3), O-21 (K04) |
| 5 | D24V50F5 sınırı | `akim_a` boş (eşik belgelenmemiş, sıcaklıkla düşüyor), "5 A" anma; K03 / K05 istisna `kafa-5v-donusturucu-arkasi` |
| 6 | 1N4007 | A03 ve A05: bobin uçlarının dibinde, katot bobinin + ucuna; EL:443 |
| 7 | G10 / G11 "(öneri)" | G10 K2 pimine lehim, G11 direnç bacağına lehim; G12 / G13 `bts-guc` + "klemens:" teyidi; denetim "öneri"yi ve klemens sınırı bilinmeyen 12 AWG'yi kesin kayıtta yakalıyor |
| 8 | EL çelişkileri | EL:129 / :330 dağıtım kartı C; EL:68, :341 yıldız noktası; EL:325 anahtarlı bara M5; EL:372 şarj 7,5 A + IMAX B6 |
| 9 | T7 "mini 2 A" | T7:11, :28, :119 → F6 3 A standart; `testler.html` yeniden üretildi |
| 10 | KOK:361 8,8 mF | 11 mF / 0,20 J; ani akım beş kondansatörle yeniden (§15.5); EL:448-449 |
| 11 | KOK:455 "Dupont" | jumper dişi uçları |
| 12 | eski MOSFET / mini sigorta | `Lale-Proje-Ozeti.txt:97-98, :176, :178`, `B-malzeme-plan.md:64` → BC337-40, F6 3 A. `planlama/adim5/maliyet_duzelt.py` bilerek değişmedi (tarihî betik, bir kez koşmuş) |
| 13 | "ana anahtar açık" | §12 ve alan tanımı "ana anahtar devrede (ON)" |
| 14 | XT60E-M pinleri | G06 notu: pinler her zaman gerilimli, kapak / koruyucu |
| 15 | alçak profil mini ↔ yuva | `maliyet.json` kalem 86 notu: teslimde denenir, oturmazsa normal profil mini |
| 16 | AU2 bölücü | AU2 `not`: bölücü PAM pedlerinin dibinde, lehim işi |
| 17 | `rehber_metin.py:637` | yapılmadı (rehber yasak), P10.7b listesinde duruyor |

**Orkestratör onayı 14.11 (madde 9):** dağıtım kartı C ve renk kuralı (+ kırmızı, − / GND siyah). Kendi seçtiğim, onay bekleyenler: ortam
bölgesinin demetten atanması (göğüs ve kollar etek sınırıyla; kafaya giden ya da ucu kafada olan kablo kafa), O-22'ye kadar geçici 5 + 4
saplama, O-18'de "2 A standart" yerine 2 A **mini** (üçüncü turda raporlandı), K03 için 18 AWG siyah 9 → 10 m ve iki 20 AWG satırının
V3'ten çıkması, D2 karşılaştırma tabanı olarak `76fd4b2`.

### 15.4 Kesit kuralı, koruyucular, değişen kablolar

- **Kural:** tablo akımı (33 CFR 183.425 + NFPA 79, küçüğü) × ortam katsayısı ≥ koruyanın sınırı. Katsayı NEC 2020 Tablo 310.15(B)(1),
  75 °C sütunu: 41–45 °C 0,82, 46–50 °C 0,75 (sınav hazırlık sayfasından; NEC metni okunmadı).
- **Koruyucular:** XL4016 A / B / C / çevre 10 A (önce 8 A); D24V50F5 sınır yok (önce 5 A); SY8205 sınır yok; BTS7960 sınır yok (akım
  sınırlama var, eşik belgelenmemiş); şarj hattı 7,5 A (önce 10).
- **İstisnalar (4 ad, 21 kablo):** `servo-uzatmasi` S01–S10 (şarta tezgâh kısa devre denemesi), `ana-hat-12awg` G01–G05,
  `motor-fabrika-kablosu` M01–M04 (gerekçe düzeltildi), yeni `kafa-5v-donusturucu-arkasi` K03, K05.
- **Kesiti ya da sigortası değişen:** K03 20 → 18 AWG; G06 sigortası 10 → 7,5 A. Başka devre değeri değişmedi.

### 15.5 Ani akım (beş kondansatör)

5 × 2200 µF = 11 mF, 12,8 V'ta ≈ 0,20 J (eskisi 8,8 mF). Ön şarj direnci üstünden tepe akım aynı (≈ 2,6 A); güç en çok V² / 4R ≈ 9,5 W,
≈ 25 ms'de; dolma ≲ 80 ms, 300 ms penceresinin içinde. Direnç enerjisi ≲ 0,45 J, 0,5 J sınırının altında. Kayıtlı sınırların içinde
(hesap; ölçülmedi).

### 15.6 Sayılar

- **Durum:** kesin 24, teyit 34, karara bağlı 16 (15 kesit-koruma + G20 / K52); önce 33 / 40 / 1. Kesinden düşüş yeni sınamaların
  sonucu (O-19 … O-21) ve teyit maddeleri (klemens, kesit okuma).
- **`maliyet.json`:** 18 AWG siyah 9 → 10 (+43,26), 7,5 A mini 2 → 3 ve 7,42 (+7,58), 2 A mini 7,42 (+0,08), 10 A mini V3 dışı (−7,34),
  20 AWG kırmızı / siyah V3 dışı (−49,44), bara saplaması 6 → 10 (fiyatsız). Ara −5,86, pay dahil **−6,74**: genel 120.838,07 →
  **120.831,33 TL**, koşullularla 126.409,54 → **126.402,80**; elde düşülmüş 95.935,58, QLED 104.236,22. V3 kalem 126, fiyatsız 4.
  Bağımlılar: `sonuc-rapor.html` (dört `data-j`), demo yeniden üretildi; README / proje-plani yuvarlamaları (≈ 120.800 / 126.400) aynı.
- **F9c:** `git archive 9a0c6fe` geçici klasöre açıldı (`.git` yalnız okundu, `GIT_OPTIONAL_LOCKS=0`), F9c orada koştu: 28 hata; çalışma
  ağacında 28 hata; iki küme satır satır aynı (karar kuyruğu ↔ sonuç sayfası sayımları, P10.7a öncesinden).

### 15.7 Efe'ye bildirilecek (kural numarası yok)

1. BTS7960 IS (akım algılama / arıza) ucu izlenir; arızada EN düşürülür. `motor-fabrika-kablosu` istisnasının dayanaklarından biri.

### 15.8 Ahmet'e (teslimde)

1. Alçak profil 2 A / 7,5 A mini sigortanın "Mini/Micro" hat yuvasına oturması.
2. XT60E-M şarj girişinin pinleri her zaman gerilimli: kapak takılı kalır.
3. T8 E: bir servo uzatmasının ucunda XL4016 kısa devre denemesi (en çok 2 s, yanmaz zemin).
4. K04 hazır micro USB kablosunun kesiti (O-21 b seçilirse).

### 15.9 Düzeltme turu 1 devamı: O-19 … O-22 (orkestratör kararı, 14.11; bitiş ≈ 05:55)

Orkestratör O-22 itirazını kabul etti (sayım). Kararlar `kablolar.json` `kararlar` (O-19 … O-22, D1-10); `orkestratore` listesinden çıktılar.

| Kod | Karar | Uygulama |
|---|---|---|
| O-19 | a: XL4016 çevre çıkışında, G19'un XL ucunun dibinde 2 A mini hat sigortası | yeni koruyucu `hat-cevre` (2 A, sigorta, tip ve yer kayıtta); yeni ağ `xl-cevre-cikis` (XL4016 çevre OUT+ → sigorta); G19 + damarı `ara_koruyucu`; G19, X01, B01, B02, N01, N02, I01, I02, Q01–Q03 koruması `hat-cevre`, zincirleri `… → F4 → XL4016-cevre → hat-cevre`; hat yuvası 5 → 6, 2 A mini 1 → 2 |
| O-20 | c: kayıtlı istisna `servo-ana-hat-16awg` (SV1–SV3), çıkışa sigorta yok | gerekçe, şart (T8 E2 + P10.7b gerilim düşümü), kontrol, beklenen akım bütçesi kayıtta; T8'e E2 satırları |
| O-21 | a: `kafa-5v-donusturucu-arkasi` K04'e genişler | K04 teyit maddesi (kesit yazısı; < 24 AWG ya da yazı yoksa 18 AWG + micro B); durum kablajda teyit; kafa ekranı akımı K04 notunda |
| O-22 | a: yıldız 5, anahtarlı bara 4 saplama, takım 10 | `bara-pabuc.kopruler` (4 + 3 köprü, 12 AWG, 50 mm, 14 sarı pabuç) malzeme sayımına girdi; sarı pabuç 3 → 4 paket; P10.7b açık işi: şerit / pano tipi nötr barası |

**Orkestratör onayı 14.11 (madde 5):** ortam bölgesinin demetten atanması, O-18'de 2 A mini, D2 karşılaştırma tabanı `76fd4b2` (D1-10).

**5 V çevre yük bütçesi** (`koruyucular.hat-cevre.yuk_butcesi`; 5 V tarafı, 3V3 yükleri doğrusal regülatörden aynı akımla):

| Yük | Tipik | Tepe | Kaynak |
|---|---|---|---|
| ESP32 kartı | 0,24 A | 0,5 A | tipik EL:353 (E4); tepe Espressif ESP32-WROOM-32E veri sayfası v2.1: Wi-Fi TX ortalama 239 / tepe 379 mA (Tablo 16), beslemenin vermesi gereken en az 0,5 A (Tablo 14), birincil, okundu |
| HC-SR04 × 3 | 0,045 A | 0,045 A | 15 mA / adet (yaygın veri sayfası değeri; açılmadı) |
| BNO055 | 0,012 A | 0,012 A | 12,3 mA (Bosch veri sayfası değeri; açılmadı) |
| PCA9685 mantık | 0,006 A | 0,01 A | NXP veri sayfası değeri (açılmadı) |
| Enkoder × 2 | 0,02 A | 0,02 A | tahmin |
| BTS7960 mantık × 2 | 0,02 A | 0,02 A | tahmin |
| PC817 modülü çıkışı | 0,001 A | 0,005 A | EL:244 + tahmin |
| **Toplam** | **0,34 A** | **0,61 A** | |

2 A'in açılış ve tepe akımında atmaması: tepe 0,61 A anmanın %31'i (mini bıçak sigorta %110'da açmaz, %200'de en erken 0,15 s).
Sigorta XL4016'dan sonra; açılışta yalnız aşağı akıştaki küçük kondansatörler dolar (≤ 200 µF tahmini, çevre hattında 2200 µF yok):
en kötü durumda XL4016'nın 10 A sınırıyla ≈ 0,1 ms, I²t ≈ 0,01 A²s. Bakılan üretici değerlerinde 2 A mininin erime I²t'si 2,8–9 A²s
(Littelfuse MINI 297; listedeki Motorobit sigortasının kendi değeri yok). **3 A'e gerek yok**; 22 AWG damarların 45 °C sınırı 2,46 A ≥ 2 A.

**Servo ana hatlarının akım bütçesi** (`servo-ana-hat-16awg.beklenen_akim_a`, EL:121-123, 6 V tarafı, tahmini):

| Kablo | Hat | Sürekli (yoğun) | Tepe | Bölge | Düzeltilmiş sınır |
|---|---|---|---|---|---|
| SV1 | A, sağ kol | 4,87 A | 7,24 A | etek | 8,2 A |
| SV2 | B, sol kol | 4,87 A | 7,24 A | etek | 8,2 A |
| SV3 | C, kafa | 1,5 A | 5,0 A | kafa | 7,5 A |

Üçü de sürekli ve tepede düzeltilmiş sınırın altında; en yakın A / B tepede %88. İstisna yapıldı.

**Kafa ekranı akımı (K04):** üretici sayfasında değer yok (Waveshare 10.1HP-CAPQLED-B: yalnız "Micro USB, 5 V"; kutudan 5 V 3 A
adaptör çıkıyor, tüketim değil); tasarımda 0,9 A varsayım (EL:25), ölçülmedi.

**"Kesin 33 → 24" neden düştü (madde 6):** düşen 9 kayıt (SV1–SV3, G19, I01, I02, Q01–Q03) ve teyitten karara geçen 6 kayıt (X01,
B01, B02, N01, N02, K04) **yalnız** O-19 / O-20 / O-21 `kesit-koruma` eksik maddesi yüzünden düşmüştü; yer tutucu, eksik uç tipi ya da
yeni teyit maddesi yüzünden kesinden düşen kayıt yok (tur 3 ile karşılaştırma: durumu değişen kayıtların hiçbirine yeni teyit maddesi eklenmemiş). Kararlarla
hepsi geri döndü: **kesin 33, teyit 40, karara bağlı 1 (G20, K52)**. 40 teyit maddesinin hepsi teslimde bakılacak şeyler (ölçü, klemens
kesiti, kablo yazısı, eşleşme ölçümü); ürün sayfasından bu turda kapatılabilecek bir uç tipi bulunmadı (BTS7960 güç klemensinin aldığı
kesit ve 5,08 mm klemensin kesiti satıcı sayfalarında yok, D1'de bakıldı).

**Birincil kaynak denemeleri (madde 7):**
- XL4016: **okundu.** XLSEMI veri sayfası Rev 1.2, s. 5: Switch Current Limit IL, VFB = 0, **10 A tipik** (en az / en çok yok).
  `koruyucular.XL4016-*.sinir_kaynagi` buna çevrildi. Rev 1.3 ("12A" başlıklı) açılamadı.
- Ortam katsayısı: **açılamadı.** NEC metni NFPA'da ücretli; Schneider Electric başvuru sayfası 403, Elliott Electric tablo sayfası
  bağlantı reddi. Değerler (0,82 / 0,75) birden çok ikincil kaynakta aynı; kayıtta "ikincil kaynaktan" notu duruyor.

**Denetim:** yeni sınamalar: istisnanın `beklenen_akim_a` bütçesi (her hat sürekli + tepe ≤ kablonun düzeltilmiş sınırı, kayıttaki
sınır kesit / bölgeden hesaplananla aynı), koruyucunun `yuk_butcesi` (toplam = kalemler, tepe < sigorta), köprü sayısı = saplama − 1,
köprüler malzeme sayımında. Yeni bozmalar: `b_kesit_10` (hat-cevre 3 A), `b_kesit_11` (G19 sigortası kaldırıldı), `b_kesit_12` (SV1
tepe 9 A), `b_kesit_13` (SV3 kafada etek sınırı), `b_kesit_14` (SV2 istisnasız), `b_kesit_15` / `16` (yük bütçesi tutarsız / tepe
2,1 A), `b_klemens_6` (köprü 3), `b_malzeme_3` (köprü metresi). **67 bozmanın 67'si yakalandı**, çıkış 0.

**`maliyet.json`:** hat yuvası 5 → 6 (+37,08), 2 A mini 1 → 2 (+7,42), sarı pabuç 3 → 4 paket (+49,44): ara +93,94, pay dahil
**+108,03**. Genel 120.831,33 → **120.939,36 TL**, koşullularla 126.402,80 → **126.510,83**; elde düşülmüş 96.043,61, QLED 104.344,25.
Bağımlılar: README:50 ve `proje-plani.md:11` (≈ 120.900 / 126.500; ≈ 96.000 / 104.300), `sonuc-rapor.html` dört `data-j`, demo
yeniden üretildi, F8a 14.11 notu ve tablosu yeniden yazıldı (hat yuvası, 2 A mini, sarı pabuç satırları), T8 E2, EL:91 / :338 / :368 /
:370, KOK:433 / :434 / :435.

**Efe'ye bildirilecek (son hâl):** 1. BTS7960 IS izlenir, arızada EN düşürülür (`motor-fabrika-kablosu` dayanağı).

**Ahmet'e (son hâl, teslimde):** 1. alçak profil 2 A / 7,5 A mininin "Mini/Micro" yuvaya oturması; 2. XT60E-M pinleri her zaman
gerilimli, kapak takılı; 3. T8 E + E2 tezgâh kısa devre denemeleri (bir uzatma ve SV1–SV3, en çok 2 s); 4. K04 kablosunun kesit yazısı
(< 24 AWG ya da yazısızsa 18 AWG + micro B ile yeniden); 5. kafa ekranının akımı ilk açılışta ölçülür (0,9 A varsayımı).

## 16. Düzeltme turu 2 (14.11, bitiş ≈ 06:56)

İkinci bağımsız kontrol `planlama/d158/P107a-kontrol-2.md` (DÜZELTME GEREKLİ): tablonun değerleri ve sipariş paketi doğru; durduran iki
bulgu: **D1′** denetim sigorta değerlerini ve istisnaları tablonun kendisiyle sınıyor, **D3** tabloda ve `elektrik.md`'de eski sigorta /
kesit metni. Bu turda devre değeri değişmedi (sigorta, kesit, pin aynı); değişen yalnız denetim, metin ve bir malzeme adedi (1N4007).

### 16.1 D1′: sınamalar bağımsız kaynağa bağlandı

Betik (`planlama/adim3/kablolar_denetim.py`) artık tablodaki sayıyı tablonun başka bir alanıyla değil, ayrıştırdığı belgeyle karşılaştırır:

| # | Sınama | Bağımsız kaynak (betiğin ayrıştırdığı yer) |
|---|---|---|
| 1 | `koruyucu`: her sigortanın akımı ve biçimi (standart / mini); BMS ve XL4016'nın sınırı; belgesiz sınırlar (D24V50F5, SY8205, BTS7960) `None` kalmalı; adındaki "N A" = akım; `set` sigortalarının çokluk kümesi; listede koruyucusuz satır kalmamalı | `elektrik.md` "Sigorta listesi" tablosu (Değer hücresi "N A standart / mini"; Hat satırı "mini: A 7,5 A · B 7,5 A · C 5 A · G22 2 A · çevre 2 A"; Şarj satırı); karar satırları: `kablolama-on-kararlar.md` K11 satırı (F6), KT3 satırı (F5), KÖK "Hat sigortası yuvası / 2 A mini" satırı (hat-G22, hat-cevre), "şarj kolu:" satırı (hat-sarj); `maliyet.json` sipariş satırının modelindeki amper (koruyucunun `siparis` alanı); BMS "BMS N A sürekli" (EL blok şeması), XL4016 "çipin anahtar akımı sınırı **N A tipik**" (EL:222). Sayı bulunamazsa hata |
| 2 | `kesit` istisnaları: her istisnada `koruyucular` {kimlik: üst sınır, kaynak satırı, en ince AWG}; istisnalı kablonun besleme zincirinden hesaplanan koruyucusu bu kümede olmalı; belgeli akım ≤ üst sınır, belgesiz koruyucuda üst sınır ≤ en ince kesitin düzeltilmiş sınırı; kesit ≥ en ince; üst sınır sayısı kaynak satırında geçmeli; üye listesi, koruyucu kümesi ve en ince kesit betikteki sabitlerle aynı | `ISTISNA_KARARI` (karar kodu + üyeler: O-2, O-15, O-16, O-21, O-20) ve `ISTISNA_KESITI` (kararların metnindeki en ince kesit) betikte sabit; tablo değişince sabit değişmez. Kesit tablosu (33 CFR 183.425 Table 5, NFPA 79 Table 12.5.1), ortam katsayısı (NEC 310.15(B)(1)) ve bölge sıcaklığı (EL satırından kalıpla) da sabit |
| 3 | `acil_stop`: her dalın sigortası ve enerjili / enerjisiz oluşu | `elektrik.md` blok şeması (`├─ Fn N A ──` blokları: bloktaki her eleman o sigortanın çıkışından beslenir) ve `kablolama-on-kararlar.md` §12 Enerjili / Enerjisiz listeleri, **tam öğe eşleşmesi** (parantez atılır, `;` ve cümle sonundan bölünür, `:` öncesi baş alınır, `a → b → c` zincirinde yalnız son öğe; F sigortalı dalın öğesi "Fn …" ile başlamalı); bir ifade iki listede birden olamaz |
| 4 | köprüler `kesit` sınamasında (yıldız: kök aku-bms 30 A, akü dönüşü ortadaki saplamada → köprüde yarısı, 15 ≤ 20,5 A; anahtarlı bara: F1 20 ≤ 20,5 A); kart içi bağlar (`ic_baglar`) `ag` sınamasında (5 V Pi ↔ 5 V çevre birleşmesi kart içinde de hata) | `klemens_turleri.bara-pabuc.kopruler` (`besleme_saplamasi`, ortadaki saplama 3 / 5); kesit tablosu sabit |
| 5 | yer tutucu kalıbı ("…", "...", "bilinmiyor", "belirlenecek", "sonra bakılacak", tek başına "?", "-", TBD; her durumda, uç alanında da); uç türü yapılandırılmış alan (`uc_turu` {a, b} her damarda; tür sözlüğü ve sınırı betikte sabit `UC_TURU_SINIRI`; parçanın güç ucu türü sabit `PARCA_UC_TURU`; 12 AWG sınırı bilinmeyen uca yalnız "klemens:" teyidiyle; sonlandırma metni "5,08" / "wago" diyorsa uç türünde olmalı); kaynak sınamasında genel sözcükler ayırt edici değil; 1N4007 `anahtarlar.K1-bobin / K2-bobin.geri_tepme_diyodu` (parça, yer, yön, kablo); donanım adetleri tablodan sayılıp `maliyet.json` ile (sigorta satırı n ≤ adet ≤ n + 1, hat yuvası = mini sigorta 6, saplama 9 ≤ adet ≤ 10, pabuç renk sınıfına göre × 1,3 + paket yuvarlaması, 1N4007 bobin + 1 ≤ adet ≤ bobin + 2); alan adı beyaz listesi (eski `klemensler` alanı hata) | `maliyet.json` kalemleri; tür sınırları sabit tablo |

**Yeni `sayi_metin` sınaması (D3'ün kalıcı çaresi):** kablo adı, `kesit_not`, `not` ve koruyucu adındaki "N A", "Fn N A" ve "N AWG" kalıpları
kaydın kendi alanlarıyla (koruyucu akımları / sınırları, kesiti) karşılaştırılır; tutmayan sayı hata. Adlar sayı taşımaya devam ediyor
(okunurluk için), ama alanla çelişen sayı artık geçmez. Kontrolün saydığı üç eski metin bu sınamanın bozması olarak da duruyor.

**Kaynak sınaması:** sözcük eşleşmesi (5+ harfli kök), genel sözcükler (`sigorta`, `gnd`, `kablo`, `hat` …) ayırt edici sayılmaz, parça adı
öbekleri ve "yıldız noktası" eşanlamı eklendi. Zayıf atıflar temizlendi: G05 → EL:323, EL:341; G16'dan EL:124, G17'den KOK:125, G21'den
EL:71 çıktı. C01 `uc_b.parca` "Kamera (Camera Module 3)".

### 16.2 Bozma denemeleri

Kontrolün betiği (`boz.py`) salt okunarak kendi geçici kopyamda koştu (dosyalara yazılmadı); ardından kendi bozmalarım. Toplam 96,
yakalanan 96; kontrolün 55 bozmasının hepsi yakalanıyor. Temiz tabloda çıkış 0, yanlış alarm 0.

Kontrolün kaçan 22 bozması:

| Bozma | Ne | Sonuç | Yakalayan sınama: ilk hata |
|---|---|---|---|
| B5c | G17 (kablajda teyit) kayıt düzeyi uc_b.nokta '?' | yakalandı | `yer_tutucu`: G17 (kablajda teyit edilecek): uc_b yer tutucu içeriyor '?': ? (eksik bilgi eksik / teyit alanına) |
| N1b | Çevre dalı tutarlı biçimde F4'ten F3'e taşındı (G18 ucu, XL4016 çevre girişi, aşağı akış dalları) | yakalandı | `acil_stop`: eleman XL4016-cevre: girişi 'f3-cikis', blok şemasında F4 bloğunda ('f4-cikis') |
| N2c | N2b + dallar.F6.p12 'anahtarlı bara' (§12 Enerjisiz listesinde geçen ifade) | yakalandı | `acil_stop`: dal F6: devrenin yapısına göre enerjisiz; §12'nin Enerjisiz listesinde 'anahtarlı bara' öğesi yok (tam eşleşme) |
| N4b | ic_baglar'a D24V50F5 çıkışı ↔ arayüz kartı çevre 5 V kart içi bağı (kablo değil) | yakalandı | `ag`: kart içi bağ D24V50F5 · VOUT (P6KE6V8A) ↔ Arayüz kartı · çevre 5 V: 5 V Pi ve 5 V çevre ağlarını birleştiriyor (5v-pi ↔ 5v-cevre) |
| N5b | Kesin kayıt G18 sonlandırma '…' (üç nokta) | yakalandı | `yer_tutucu`: G18 (kesin): sonlandirma yer tutucu içeriyor '…': … (eksik bilgi eksik / teyit alanına) |
| N5c | Kesin kayıt G18 sonlandırma 'sonra bakılacak' / uc_b.nokta 'bilinmiyor' | yakalandı | `yer_tutucu`: G18 (kesin): uc_b yer tutucu içeriyor 'bilinmiyor': bilinmiyor (eksik bilgi eksik / teyit alanına) |
| N7b | klemens-508 sınırı 4 mm² yazıldı + G11 (12 AWG) bu klemense | yakalandı | `alanlar`, `klemens`: G11: tanımsız alan ['klemensler'] (denetim okumaz; eski alan adı mı?) |
| N7c | G10 sonlandırması 'ön şarj kartı 5,08 klemensi' (klemensler alanına yazılmadan) | yakalandı | `klemens`: G10: sonlandırma metni '5,08' diyor, uç türlerinde klemens-508 yok (12 AWG kablo) |
| N8a | Koruyucular: F6 3 → 5 A (ad 'F6 3 A' kaldı) | yakalandı | `koruyucu`, `sayi_metin`: koruyucu F6: adı 'F6 3 A standart (sigorta kutusu)' 3 A diyor, akim_a 5 |
| N8c | Koruyucular: ana sigorta 30 → 40 A | yakalandı | `kesit`, `koruyucu`, `sayi_metin`: koruyucu ana-sigorta: adı 'Ana sigorta 30 A (standart bıçak, kablolu yuva)' 30 A diyor, akim_a 40 |
| N8d | Koruyucular: aku-bms 30 → 100 A ve ana sigorta 60 A | yakalandı | `kesit`, `koruyucu`, `sayi_metin`: koruyucu aku-bms: adı 'Akü BMS (Victron SuperPack, 30 A sürekli)' 30 A diyor, akim_a 100 |
| N8e | Koruyucular: hat-A 7,5 → 8 A | yakalandı | `koruyucu`: koruyucu hat-A: adı 'Hat sigortası A 7,5 A mini (XL4016 A girişi)' 7,5 A diyor, akim_a 8 |
| N8f | Koruyucular: hat-sarj 7,5 → 8 A | yakalandı | `koruyucu`, `sayi_metin`: koruyucu hat-sarj: adı 'Şarj hat sigortası 7,5 A mini (akü tarafındaki ucun dibinde)' 7,5 A diyor, akim_a 8 |
| N9b | İstisna servo-ana-hat-16awg gerekçesi '?' / şartı '-' | yakalandı | `kesit`: istisna 'servo-ana-hat-16awg': gerekce boş / yer tutucu / çok kısa ('?') |
| N9c | İstisna ana-hat-12awg kapsamına G08 eklendi, G08 de istisnayı taşıyor (12 AWG F1 arkası, sessiz muafiyet) | yakalandı | `kesit`: istisna 'ana-hat-12awg': kapsam ['G01', 'G02', 'G03', 'G04', 'G05', 'G08'] (6), kayıtlı karar O-15: ['G01', 'G02', 'G03', 'G04', 'G05'] (5) |
| N9d | G18 (18 AWG, F4) kesiti 22 AWG + kafa-5v-donusturucu-arkasi istisnası (kapsama da eklendi) | yakalandı | `kesit`: istisna 'kafa-5v-donusturucu-arkasi': kapsam ['G18', 'K03', 'K04', 'K05'] (4), kayıtlı karar O-21: ['K03', 'K04', 'K05'] (3) |
| N10a | G18 kaynağı elektrik.md:5 (genel giriş paragrafı) | yakalandı | `kaynak`: G18: ilgisiz satır: planlama/adim3/elektrik.md:5 (kablonun ayırt edici terimlerinden hiçbiri yok: f4, g18, xl4016, xl4016 çevre, yıldız barası, yıldız |
| N10b | SV1 kaynağı elektrik.md:341 (toprak satırı) | yakalandı | `kaynak`: SV1: ilgisiz satır: planlama/adim3/elektrik.md:341 (kablonun ayırt edici terimlerinden hiçbiri yok: akım, dağıtım, dağıtım kartı a, gücü, out, servo,  |
| N11c | maliyet: hat sigortası yuvası 6 → 3 | yakalandı | `donanim`: maliyet.json kalem 85 (Hat sigortası yuvası): 3 adet, tabloda 6 mini sigorta (hat-A, hat-B, hat-C, hat-G22, hat-cevre, hat-sarj) |
| N11d | maliyet: bara saplaması 10 → 2 takım | yakalandı | `donanim`: maliyet.json kalem 156 (Bara saplaması): 2 takım, tabloda 9 saplama (n ≤ adet ≤ n + 1) |
| N14 | 1N4007 (A03) sonlandırmasından diyot silindi | yakalandı | `donanim`: K1-bobin: diyotun kablosu A03 yok ya da sonlandırmasında 1N4007 yazmıyor |
| N16 | dallar.F4.p12 'akü' (Enerjili listesinin her yerinde geçen kısa ifade) | yakalandı | `acil_stop`: dal F4: devrenin yapısına göre enerjili; §12'nin Enerjili listesinde 'akü' öğesi yok (tam eşleşme) |

Benim bozmalarım (her yeni sınama için en az bir; "+" olanlar kontrolün bozmasının adı / notu da tutarlı değiştirilmiş hâli, yani yalnız
bağımsız kaynak yakalayabilir):

| Bozma | Ne | Yakalayan |
|---|---|---|
| N7a′ | G05 − damarının yıldız ucu uc_turu klemens-508 (12 AWG, sınırı bilinmeyen 5,08 klemense) | `klemens` |
| N7b′ | klemens-508 sınırı 4 mm² + G11'in ön şarj ucu klemens-508 (uc_turu) | `klemens` |
| N14′ | K1 bobininin geri_tepme_diyodu alanı silindi | `donanim` |
| Y1 | elektrik.md sigorta listesinde F4 5 → 10 A (belge değişti, tablo eski) | `koruyucu` |
| Y2 | hat-C 5 → 7,5 A, siparişi de 7,5 A satırına (kalem 88) taşındı | `donanim`, `koruyucu`, `sayi_metin` |
| Y3 | F5 biçimi mini yazıldı (kutu standart bıçak alır) | `donanim`, `koruyucu` |
| Y4 | D24V50F5'e belgesiz 5 A akım sınırı yazıldı (K03'ün istisnası gereksiz görünür) | `koruyucu` |
| Y5 | maliyet.json ana sigorta satırı modeli '40 Amper' (sipariş ↔ tablo farkı) | `kaynak`, `koruyucu` |
| Y6 | 16 AWG NFPA 79 dayanağı 10 → 15, en çok 15 (tutarlı, kaynaktan farklı) | `kesit`, `sayi_metin` |
| Y7 | ortam katsayısı 45 °C 0,82 → 0,95 | `kesit`, `sayi_metin` |
| Y8 | kafa bölgesi 49 → 40 °C | `kesit`, `sayi_metin` |
| Y9 | istisna ana-hat-12awg ana-sigorta üst sınırı 30 → 40 ve ana sigorta 40 (ikisi birlikte) | `kesit`, `koruyucu`, `sayi_metin` |
| Y10 | yeni istisna adı 'g08-kisa' (G08 F1 arkası 12 AWG, yeni ad, kapsam + koruyucu dolu) | `kesit` |
| Y11 | K04 kesiti 26 AWG yazıldı (istisna SY8205 için en ince 24 AWG) | `kesit` |
| Y12 | yıldız köprülerinin besleme saplaması 3 → 1 (akü dönüşü uçta: köprü 30 A taşır) | `kesit` |
| Y13 | anahtarlı bara köprüleri 16 AWG | `kesit` |
| Y14 | §12'de 'F6 göğüs ekranı dalı' Enerjisiz listesine de eklendi | `acil_stop` |
| Y15 | blok şemasında göğüs regülatörü F4 bloğuna taşındı (belge değişti, tablo eski) | `acil_stop` |
| Y16 | ic_baglar: SY8205 çıkışı ↔ D24V50F5 çıkışı yerine çevre: ESP32 VIN ↔ D24V50F5 VOUT (kart içi) | `ag` |
| Y17 | teyit kaydı G21 damar ucu 'belirlenecek klemens' | `ag`, `yer_tutucu` |
| Y18 | G04 sigorta kutusu ucu 'klemens:' teyidi silindi (12 AWG, sınırı bilinmeyen uç) | `klemens` |
| Y19 | G09 bara ucu uc_turu 'lehim' (saplamalı düğümde pabuçsuz uç; pabuç sayımından da kaçar) | `klemens` |
| Y20 | G13 sonlandırma 'WAGO 221 ile' (12 AWG, WAGO türü uçta yok) | `klemens` |
| Y21 | maliyet: sarı halka pabuç 4 → 1 paket | `donanim`, `kaynak` |
| Y22 | maliyet: 1N4007 3 → 2 (yedek yok) | `donanim`, `kaynak` |
| Y23 | hat-G22 mini sigortası G22'nin damarından çıkarıldı (yuvasız mini sigorta) | `acil_stop`, `ag`, `donanim`, `kesit` |
| Y24 | maliyet: 7,5 A mini 3 → 1 | `donanim`, `kaynak` |
| Y25 | G19 kaynağı elektrik.md:363 (sigorta listesi başlık satırı: 'Yer / Değer / Besler') | `kaynak` |
| Y26 | G18 adı 'F4 10 A → XL4016 çevre girişi' | `sayi_metin` |
| Y27 | G16 kesit notu '18 AWG yeter' | `sayi_metin` |
| Y28 | eski alan adı: G05'e klemensler = [{uc b, wago-2273}] (denetim okumaz) | `alanlar` |
| Y29 | teyit kaydı G17'nin uc_b.parca başka parça ('PAM8403') | `alanlar` |
| N8a+ | N8a ve koruyucunun adı da tutarlı biçimde 'F6 5 A' (yalnız belge yakalayabilir) | `koruyucu`, `sayi_metin` |
| N8c+ | N8c ve ana sigortanın adı / G02 adı / düğüm adları da tutarlı biçimde 40 A | `kesit`, `koruyucu` |
| N8e+ | N8e ve hat-A adı da '8 A' | `koruyucu` |
| N8f+ | N8f ve şarj sigortasının adı / G06 adı / kesit notu da '8 A' | `koruyucu` |
| N9d+ | G18 22 AWG + kafa-5v istisnası, kapsama eklenmeden (yalnız kablo alanı) | `kesit` |
| N16+ | dallar.aku-ana.p12 'akü' (sigortasız dal, Enerjili zincirin ilk öğesi) | `acil_stop` |
| Y30 | servo-uzatmasi en ince kesiti 24 AWG + S01 24 AWG (tutarlı; karar 22 AWG) | `kesit` |
| Y31 | hat-cevre koruyucusu kaldırıldı (G19 doğrudan XL4016 çevre arkasında; liste satırı yetim) | `acil_stop`, `ag`, `kesit`, `koruyucu`, `sayi_metin` |
| Y32 | G08 F1 ucu 'lehim' yazılıp 'klemens:' teyidi silindi (kesin görünür) | `klemens` |

Betiğin kendi `--bozma-denemesi` listesi 67 → **97** (kontrolün istediği N1b, N2c, N8c, N9d ve her yeni sınama için en az bir bozma);
97'nin 97'si yakalandı, çıkış 0.

### 16.3 D3: eski metin

- Tablo (`d2_yama`, `kablolar.json` yeniden üretildi): G06 adı "Şarj kolu: akü + → 7,5 A hat sigortası → XT60E-M şarj girişi (+ / −)",
  G06 `kesit_not` 7,5 A / 16 AWG düzeltmeli 8,2 A; K03 `kesit_not` 18 AWG, kafa 5 V istisnası, 5,25 A; G19 notu 2 A çevre sigortası,
  8,2 A (eski "8 A sınırı" çıktı); hat-A / B / C adına "(XL4016 X girişi)".
- `elektrik.md`: :41 hat yuvası × 6; :222 XL4016 10 A tipik (Rev 1.2); :279 18 AWG; sigorta listesi :364–370 ve :372 tek biçimde
  ayrıştırılabilir ("N A standart / mini"; Hat satırı tek hücrede beş mini; "toplam 6 kapaklı mini yuva"; şarj "7,5 A mini (düzeltme turu 1,
  14.11; önce 10 A)"); :376–377 sigorta seti ve yuva × 6; :418 IMAX B6 ≈ 3,4 A ≈ 6 sa (hesap); :429 5 × 2200 µF; :448–449 ani akım
  (§16.5); :515 11 mF ≈ 0,20 J. Satır eklenmedi / silinmedi.
- `kablolama-on-kararlar.md:458` "karar 10 A; düzeltme turu 1'de **7,5 A mini**"; `:110` "şarj P10.7a düzeltme turu 1'de 7,5 A".
- `planlama/adim5/B-malzeme-plan.md:43`, `planlama/adim3/pin-haritasi.md:43` (röle sürücüsü BC337-40; önce IRLZ44N),
  `Lale-Proje-Ozeti.txt:175`, `planlama/d158/karar-kuyrugu.md:1260` (hat yuvası 5 → 4 → 5 → 6).
- Depo taraması (şarj "10 A", K03 "20 AWG", "8 A sınırı", hat yuvası adedi, "6 takım", "5 pabuç"; tarihli günlük / kontrol raporları,
  `main`, `kod/`, rehber çıktıları hariç): ek olarak `planlama/d158/testler/T3-kafa-5v-akim.md:117` (K03 20 → 18 AWG, atıf EL:246 → EL:279;
  `testler.html` yeniden üretildi). Kalan eski değerler yasak alanda ya da tarihli: `tasarim/freecad/rehber/rehber_metin.py:251, :634` ve
  `rehber_denetim.py:151, :157` ("şarj 10 A"; rehber yasak, P10.7b), `tasarim/freecad/taslak-170/kol-analiz/` ("XL 8 A", eski taslak),
  `planlama/adim5/maliyet_duzelt.py` (tarihî betik), F7c / F7d raporları ve `raporlar/aku-secimi` (tarihli).

### 16.4 Sayılar

- **Durum:** kesin **32**, teyit **41**, karara bağlı **1** (G20, K52). Önce 33 / 40 / 1: G08 kesinden teyite geçti (12 AWG iletkeni
  sigorta kutusunun F1 çıkışına gidiyor; kutunun ucunun aldığı kesit belgesiz → "klemens:" teyidi; G04, G10'a da aynı madde).
- **İstisnalar (5 ad, 25 kablo):**

| İstisna | Kablolar | Koruyucu | Üst sınır (kaynak) | En ince |
|---|---|---|---|---|
| `servo-uzatmasi` (O-2) | S01–S10 | XL4016 A / B / C | 10 A (EL:222) | 22 AWG |
| `ana-hat-12awg` (O-15) | G01–G05 | akü BMS, ana sigorta | 30 A (KOK:456) | 12 AWG |
| `motor-fabrika-kablosu` (O-16) | M01–M04 | BTS7960 sol / sağ (sınır belgesiz) | 2,8 A (EL:157) | 18 AWG; kesit okunamazsa teyit |
| `kafa-5v-donusturucu-arkasi` (O-21) | K03, K04, K05 | D24V50F5 (belgesiz) / SY8205 (belgesiz) | 5 A (maliyet kalem 64 modeli) / 0,9 A (EL:25) | 18 / 24 AWG; kesit okunamazsa teyit |
| `servo-ana-hat-16awg` (O-20) | SV1–SV3 | XL4016 A / B / C | 10 A (EL:222) | 16 AWG |

- **`maliyet.json`:** 1N4007 2 → 3 (röle başına bir + bir yedek; +0,61). Ara 105.164,66 → 105.165,27; genel 120.939,36 →
  **120.940,06 TL**, koşullularla 126.510,83 → **126.511,53**; elde düşülmüş 96.044,31, QLED 104.344,95. V3 kalem 126. Bağımlılar:
  `sonuc-rapor.html` dört `data-j`, demo yeniden üretildi, F8a 14.11 notu ve tablosu yeniden yazıldı (35 satır, 1N4007 satırı eklendi);
  README:50 ve `proje-plani.md:11` yuvarlamaları (≈ 120.900 / 126.500 / 96.000 / 104.300) aynı.

### 16.5 Ani akım (temkinli)

Kontrolün rakamları alındı: dolma **≈ 100 ms** (bara τ 11 ms + servo kondansatörleri, bekleme akımı ≈ 0,4 A aynı direnci paylaşınca
≈ 50 ms; önceki "≲ 80 ms" bekleme akımını saymıyordu), direnç enerjisi **≈ 0,7 J** / 300 ms (bara 0,21 + servo kondansatörlerine aktarılan
pay ≤ 0,23 + bekleme akımı kaybı 0,27). Ortalama ≈ 2,4 W, ilk anda en çok ≈ 38 W (τ 11 ms ile söner); 11 W taş direnç için küçük. Önceki
"0,5 J sınırı"nın kaynağı yoktu, kaldırıldı. 300 ms penceresinin içinde; tepe akım 2,6 A (değişmedi). Hesap; ölçülmedi. EL:448–449; §15.5
eski hesaptır.

### 16.6 Efe'ye bildirilecek (son hâl, kural numarası yok)

1. BTS7960 IS izlenir, arızada EN düşürülür (`motor-fabrika-kablosu` dayanağı).
2. Çevre 5 V'un düşmesi (2 A `hat-cevre` sigortasının atması) yazılımda arıza sayılır.
3. Soru: ESP32 USB'den (hub VBUS, 1N5819) beslenirken çevre hattının yükleri (sonar, BTS mantığı, PC817 çıkışı) bu diyot ve Pi USB'si
   üstünden geri beslenir (kontrol §2-9, EL:284-286). Bu nasıl ele alınacak (yazılımda algılama mı, devrede ayırma mı)?

### 16.7 Ahmet'e (son hâl, teslimde)

1. Alçak profil 2 A / 7,5 A mininin "Mini/Micro" yuvaya oturması.
2. XT60E-M pinleri her zaman gerilimli, kapak takılı.
3. T8 E + E2 tezgâh kısa devre denemeleri (bir uzatma ve SV1–SV3, en çok 2 s).
4. K04 kablosunun kesit yazısı (< 24 AWG ya da yazısızsa 18 AWG + micro B ile yeniden).
5. Kafa ekranının akımı ilk açılışta ölçülür (0,9 A varsayımı).
6. 1N5819'un 1 A sınırı (çevre yükleri USB'den geri beslenirse aşılabilir; Efe 3 ile birlikte).
7. Akü dönüşü (G05) yıldız barasının **ortadaki (3.) saplamasına**; G12 − ve G13 − ortanın iki yanına (köprüden geçen akım yarıya iner;
   tabloda G05 sonlandırması ve `kopruler.Yıldız barası · GND.besleme_saplamasi` 3).
8. K1 soketinin (ISO mini, kablolu) kuyruk kesiti; 12 AWG'ye eklenecek (kontrol §2-15).

### 16.8 Doğrulama

| Komut | Sonuç |
|---|---|
| `planlama/adim3/kablolar_denetim.py` | çıkış 0, 19 sınama geçer |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 97 / 97 yakalandı, çıkış 0 |
| kontrolün `boz.py` + kendi bozmalarım (geçici kopya) | 96 / 96 yakalandı |
| `planlama/adim3/kablolar_uret.py --kontrol` | güncel, çıkış 0 |
| `planlama/adim5/maliyet_toplam.py` | genel 120.940,06; koşullular dahil 126.511,53; V3 kalem 126 |
| `planlama/d158/F9b-dogrula.py --tarayicisiz` | GEÇER, 0 hata |
| `planlama/d158/F9c-dogrula.py --tarayicisiz` | çıkış 1, 28 hata (P10.7a öncesi küme; maliyet `data-j` hatası yok) |
| `planlama/d158/F9d-tarama.py --ozet` | çıkış 0, README uyuşmazlığı 0 |
| `planlama/d158/testler/testler_html.py --kontrol` | geçer |

### 16.9 Doğrulanamayanlar ve uyarılar

- **Köprü yarılama kuralı bir sadeleştirme:** akü dönüşü ortadaysa yıldızın iki yanı toplam akımı paylaşır, ama koruyucu akımlarıyla en kötü
  durumda bir yan 20,5 A'i aşabilir (bir yandaki dönüşler 30 A'e yaklaşırsa). Kayıtta şartıyla duruyor: G12 − ve G13 − ortanın iki yanında.
- SY8205'in satıcı modelindeki "5A" ile anma 3,7 A karşılaştırılmadı (sınır belgesiz kalıyor).
- D24V50F5'in üst sınırı (5 A) satıcı modelinden; üretici "tipik en çok sürekli akım" diyor, sınır değil.
- Sigorta kutusunun ucunun aldığı kesit, BTS7960 güç klemensi, 5,08 mm klemens, MAH-112-C-4 soket kuyruğu: belgesiz, teslimde.
- NEC ortam katsayısı ikincil kaynaktan; XL4016 Rev 1.3 açılmadı (değişmedi).
- `F8a-siparis.json` `guncelleme_14_11` içinde V3 dışı satırların adedi 0 yapılmadı (kontrol §2-13, isteğe bağlı; md tablosunda "→ **0**").

## 17. Ek tur (üçüncü bakıştan sonra; 14.11, bitiş ≈ 07:50)

Üçüncü bağımsız bakış `planlama/d158/P107a-kontrol-3.md` (DÜZELTME GEREKLİ) tablonun değerlerini doğru buldu; durduran üç bulgu: **D-A**
ince telli kablo yalnız tek telli alan WAGO 2273'e giriyor (kafa 12 V girişi, acil stop düğümü; A06'nın 22 AWG'si alt sınırın da altında),
**D-B** `sayi_metin` komşu sigortanın değerini izinli sayıyor ve `not` / damar `ara` metinlerini sınamıyor, **D-C** röle K1 arkasındaki
elemanlar blok şemayla karşılaştırılmıyor. Orkestratör tek ek tur + dar kapsamlı dördüncü bakış kararı verdi. Devre değeri değişmedi;
değişen yalnız iki düğümün sonlandırması ve yıldız köprüsünün yerleşimi. Tablo `d3_yama` ile yeniden üretildi.

### 17.1 D-A: iki düğüm vidalı klemensli karta, uç türü sözlüğüne iletken ve alt sınır

- **5,08 mm klemensin kesit aralığı okunamadı:** satıcı sayfası (Robocombo, kod 2511201001, 14.11 okundu) yalnız ad, kod ve stok
  gösteriyor. Bu yüzden 22 AWG uçlar klemense girmez: **A06 +** (düğüm kartında bir klemensin kuyruğuna, kart altı), **A06 −** ve
  **G07 b** (arayüz kartında pede) lehim + makaron; üçü "kablajda teyit" (`klemens:` maddesi: teslimde aralık okunursa yeniden bakılır).
- **Kafa giriş kartı:** küçük pertinaks parçası (P6KE18A üstünde), üç adet 2 pin 5,08 mm vidalı klemens (G17 b, K01 a, K02 a); + uçları ve
  − uçları kart üstünde lehimle köprülü. **Acil stop düğüm kartı:** güç panelinde küçük pertinaks parçası, iki adet 2 pin klemens (A02'nin
  iki ucu, A04 a), dört ucu lehimle köprülü. İnce telli uç kalaylanmaz, bükülür (yüksük varsa yüksük). `kablolama-on-kararlar.md` O-6
  satırına not düşüldü.
- **WAGO 2273:** hiçbir uçta yok; `maliyet.json` kalem 62 V3 dışı (`ver` "v1,v2"), satır silinmedi. Bütün WAGO uçları aynı ölçüyle
  gözden geçirildi: başka WAGO ucu yok.
- **Uç türü sözlüğü** (`klemens_turleri`): her türde `iletken` ("tek telli" / "tek telli / ince telli" / belgesizse `null`), `en_az_mm2`
  ve `iletken_not`. Malzeme türlerinde `iletken` (silikon, sinyal, servo uzatması: ince telli). Denetim (`klemens` sınaması, sabitler
  betikte: `UC_TURU_ILETKEN`, `UC_TURU_SINIRI`, `MALZEME_ILETKEN`, `ALT_SINIRI_BELGESIZ`): ince telli kablo tek telli uca giremez; kesit
  türün alt sınırının altında olamaz; alt sınırı belgesiz türe (5,08 klemens) 0,5 mm² altı uç giremez; sözlükteki değer sabitten farklıysa
  hata.
- **G22'nin yıldız dönüşü (bulgu 8):** 22 AWG (0,33 mm²) kırmızı pabucun 0,5 mm² alt sınırının altında. Uç: 22 AWG tel ≈ 5 cm **18 AWG
  siyah ara parçaya** lehim + makaron, ara parça kırmızı M5 pabuçla saplamaya (damar alanı `uc_kuyrugu`: 18 AWG, 0,82 mm², silikon-18,
  50 mm). Denetim uç kesitini kuyruktan okur. "İkiye katlanır" yazılmadı.
- **`maliyet.json`:** WAGO 2273 V3 dışı (10 × 12,24 = −122,40); 5,08 mm klemens 12 → **16** (12 klemens × 1,3 = 15,6; `klemens_yerleri`:
  kafa girişi 3, acil stop düğümü 2, arayüz kartı 2, dağıtım A / B / C birer, ön şarj 1, Ö4 1; +22,00); delikli pertinaks 6 → **7** (iki küçük
  kart bir plaketten; `pertinaks_parcalari`; +24,20). Ara **−76,20**.

### 17.2 D-B: `sayi_metin` yalnız kablonun kendi koruyucusunu kabul eder

- Taranan alanlar: ad, `kesit_not`, `not`, `sonlandirma`, damar `ara` ve damar `not`.
- Bağımsız kaynak: kablonun besleme zinciri (denetimin kendi `kablo_zinciri` hesabı) üstündeki koruyucuların akımları. Komşu koruyucu
  ancak sayının hemen önünde adıyla anılırsa (F1–F6, ana sigorta, BMS, XL4016 A / B / C / çevre, hat-…) ve o koruyucunun değeriyle
  tutarsa geçer; adı bilinmeyen koruyucu hata. Kesit notunda / notta ayrıca düzeltilmiş sınır, tablo değeri ve istisna üst sınırı.
- AWG sayısı kablonun kesitleri ve uç kuyrukları dışında olamaz.
- Tarihçe ayrı alana taşındı (`tarihce`, denetim okumaz): G06 notu ve + ara, K03 notu, G20 notu, N01 / N02 kesit notu, hat-sarj notu;
  K04'teki "3 A adaptör" metni sayısız yazıldı.
- Kontrolün örnekleri (T26, T27, T28, T30, T31, T44, T45) yakalanıyor (§17.4).

### 17.3 D-C: tablo blok şemayla tam eşleşmeyle

- `blok_agaci`: `elektrik.md` "Blok şema (metin)" ağacı ayrıştırılır (her `├─` / `└─` bir kol, `──` ve `─┬─` ile öğeler; kolun ebeveyni
  üstteki kardeşin ebeveyni ya da daha sol sütundaki en yakın kolun son öğesi / `┬` noktası; "(X sonrası)" önekli kol kökteki X'e bağlanır).
- `blok_karsilastir`: her koruyucu / anahtar `DIYAGRAM` sabitiyle tam bir şema öğesine eşlenir; tablodaki girişi, şemada en yakın eşlenmiş
  atanın çıkışıyla aynı olmalı; hat sigortalarının değeri şemayla aynı olmalı; şemada eşlenmemiş sigorta, ayrıştırılamayan şema ya da
  türetilemeyen giriş / çıkış hata (`esp32-3v3` gerekçesiyle şema dışı).
- Mesaj: "tablo ↔ elektrik.md blok şeması uyuşmuyor; şema doğruysa tabloyu, tablo doğruysa önce şemayı ve karar kaydını düzelt"
  (devreden diyen bütün mesajlara eklendi).
- Ayrıştırmanın tutması için şemada dört satır düzeltildi, satır sayısı aynı: şarj kolu "(ana sigorta sonrası) 7,5 A mini ── XT60E-M şarj"
  kendi satırında; "röle K1 kontağı ∥ K2 ön şarj kolu"; "2 A mini (O-18 b) ── PC817 #2"; "röle K1 bobini ∥ K2 bobini". Ağaç 62 öğe.
- T40b, T41b, T42c yakalanıyor.

### 17.4 Bozma denemeleri

Kontrolün betiği (`boz3.py`) salt okunarak geçici kopyada koştu: 56 bozmanın 54'ü yakalandı, temiz tabloda çıkış 0. Kontrolün kaçan 18
bozması:

| Bozma | Ne | Sonuç | Yakalayan: ilk hata |
|---|---|---|---|
| P06 | Sigorta listesi F4 Değer hücresinde iki sayı | yakalandı | `koruyucu`: hücrede 2 akım değeri (bir olmalı; tarihçe parantez içinde) |
| T22 | K1 diyot yönü ters yazıldı | yakalandı | `donanim`: yon metni katot bobin + ucunda olmalı |
| T24 | K01 kesiti 12 AWG / 2,0 mm² | yakalandı | `alanlar`: 12 AWG ↔ 2,0 mm², tabloda 3,31 |
| T26 | G16 adı 7,5 A hat sigortası | yakalandı | `sayi_metin`: kendi koruyucuları [5, 20, 30] |
| T27 | G14 adı 5 A hat sigortası | yakalandı | `sayi_metin`: kendi koruyucuları [7,5, 20, 30] |
| T28 | G19 notu "XL4016 çevre 8 A" | yakalandı | `sayi_metin`: XL4016 çevre 10 A |
| T29 | K03 notu "20 AWG" | **kaçtı (işlemsiz)** | metin artık `tarihce`'de, bozma bir şey değiştirmiyor; eşdeğeri (K03 `not` "20 AWG") yakalanıyor |
| T30 | G06 + ara "10 A mini" | yakalandı | `sayi_metin`: kendi koruyucuları [7,5, 30] |
| T31 | G18 notu "F4 10 A" | yakalandı | `sayi_metin`: F4 5 A |
| T34 | BC337-40 3 → 1 | yakalandı | `donanim`: bobin 2 + 1 yedek |
| T35 | 2200 µF 5 → 4 | yakalandı | `donanim`: kartlarda 5 |
| T36 | WAGO 2273 10 → 1 | **kaçtı (geçersiz)** | WAGO artık V3 dışı; V3 dışı satırın adedi hata değil |
| T39 | 5,08 klemens 12 → 2 | yakalandı | `donanim`: 12 klemens × 1,3 |
| T40b | XL4016 A röle öncesine, tutarlı | yakalandı | `acil_stop`: blok şemasında röle K1 kontağı ∥ K2 arkasında |
| T41b | G22 algı teli röle öncesine, tutarlı | yakalandı | `acil_stop`: aynı |
| T42c | BTS sol röle öncesine, tam tutarlı | yakalandı | `acil_stop`: aynı |
| T44 | G22 adı 7,5 A hat sigortası | yakalandı | `sayi_metin`: kendi koruyucuları [2, 20, 30] |
| T45 | G22 + ara "7,5 A mini" | yakalandı | `sayi_metin`: aynı |

Önceki kontrolün 96 bozması (`boz2`) yeniden: 96 / 96. Betiğin kendi `--bozma-denemesi` listesi 97 → **121** (her yeni sınama için en az
bir: blok şeması 5, `sayi_metin` 4, ince telli / alt sınır / sözlük 4, köprü yerleşimi 2, mm² 1, iki sayılı hücre 1, diyot yönü 2, BC337,
2200 µF, 5,08 klemens, WAGO, pertinaks); 121 / 121, temiz tabloda çıkış 0.

### 17.5 Küçük maddeler

1. **Yıldız yerleşimi** (`kopruler.Yıldız barası · GND.yerlesim`): saplama 1 G12 / G14 / G15, 2 G13 / G16, 3 G05 (akü) / G06, 4 G17 / G18,
   5 G20 / G22. En kötü köprü akımı = uzak yandaki dönüşlerin koruyucu akımları toplamı (aynı kök sigortadakiler o sigortayla, hepsi BMS
   30 A ile sınırlı): 1–2 **20 A**, 2–3 **20 A**, 3–4 **15 A**, 4–5 **5 A**; sınır 12 AWG 20,5 A. Denetim yerleşimin düğümdeki iletkenleri
   tam kapsadığını, saplama başına pabuç sınırını ve akü dönüşünün besleme saplamasında olduğunu da sınar.
2. **1N4007 yönü** yapısal alan (`katot_dugumu` / `anot_dugumu`): K1 86 / 85, K2 bobin + / −; ters yazım hata.
3. **AWG ↔ mm²** kayıt, damar, kuyruk ve kesit tablosunda; 22 AWG 0,34 → 0,33 (tablodan).
4. **Sigorta listesi hücresinde iki sayı** hata (tarihçe parantez içinde tek sayıyla).
5. **Donanım sayımı:** BC337-40 (bobin + 1 … + 2), 2200 µF (`kondansatorler`: dağıtım A 2, B 2, C 1; EL'deki sayı da), 5,08 klemens
   (`klemens_yerleri`, × 1,3 … 1,5), pertinaks (n … n + 1), WAGO (uç yoksa V3 satırı yok).
6. **Ani akım, boş akü (12,8 V):** bekleme yükü dirençte büyük pay alır, yalnız onunla bara ≈ 9,4 V'ta dengelenir; XL4016 girişi 8 V'un
   üstünde kalmalı, bu aralıkta kondansatörlere ≈ 0,4–1,0 W kalır: 0,20 J ≈ **0,2–0,5 s**. 300 ms'ye pay yok → Efe listesine not (§17.7).
   EL:448'e eklendi. Hesap; ölçülmedi.
7. **P10.7b listesi:** `rehber_metin.py` :626, :711, :1291 ("şarj 10 A"), :634 ("göğüs ekranı mini 2 A") (§18.6).

### 17.6 Sayılar

- **Durum:** kesin **31**, teyit **42**, karara bağlı **1** (G20, K52). Önce 32 / 41 / 1: A06 kesinden teyite geçti (22 AWG düğüm
  ucu lehimli, 'klemens:' maddesi); G07 ve G17 zaten teyitteydi, G22 kuyrukla kesin kaldı (önceki kopyayla karşılaştırıldı).
- **`maliyet.json`:** ara 105.165,27 → **105.089,07**; genel 120.940,06 → **120.852,43 TL**, koşullularla 126.511,53 → **126.423,90**; elde
  düşülmüş 95.956,68, QLED 104.257,32. V3 kalem 126 → 125. Bağımlılar: `sonuc-rapor.html` dört `data-j`, demo yeniden üretildi, F8a 14.11
  notu ve tablosu yeniden yazıldı (36 satır, kayma 49), README:50 ve `proje-plani.md:11` koşullu yuvarlaması ≈ 126.500 → **≈ 126.400**
  (öbürleri ≈ 120.900 / 96.000 / 104.300 aynı).

### 17.7 Listelere ekler

- **Efe:** 4. Ön şarj beklemesi en az 300 ms; boş aküde (12,8 V) dolma hesapla 0,2–0,5 s olduğu için **500 ms önerilir**; bekleme bitince
  GPIO5 LOW teyidi (LOW değilse ön şarj kolu çalışmıyor: hata); K2 toplam en çok 1 s. GPIO5'in LOW olması dolduğunu göstermez. Pin
  raporundaki 300 ms için değişiklik önerisi: 500 ms; karar yazılım tarafıyla. (C adımında düzeltildi; önceki "LOW olana kadar" metni
  yanlıştı, `P107a-kontrol-4.md` §2-1.)
- **Ahmet (teslimde):** 9. 5,08 mm klemensin kesit aralığı (okunursa A06 / G07'nin lehimli uçlarına yeniden bakılır). 10. İnce telli uç
  vidalı klemense kalaylanmadan, bükülerek (yüksük varsa yüksük). 11. G22'nin yıldız ucu: 5 cm 18 AWG ara parça + kırmızı pabuç.
  12. Seçenek: onaylı satıcılar dışından kollu WAGO 221-413 alınabilir (ince telli alır); karar Ahmet'in, tablo vidalı klemensle gider.
  §16.7 madde 7'nin yerine: yıldız yerleşimi §17.5-1'deki gibi.
- **P10.7b:** `rehber_metin.py` :626, :711, :1291, :634 (§18.6).

### 17.8 Doğrulama

| Komut | Sonuç |
|---|---|
| `planlama/adim3/kablolar_denetim.py` | çıkış 0, 19 sınama geçer |
| `planlama/adim3/kablolar_denetim.py --bozma-denemesi` | 121 / 121 yakalandı, çıkış 0 |
| kontrolün `boz3.py` (geçici kopya) | 56'nın 54'ü; kaçan T29 (işlemsiz), T36 (geçersiz) |
| önceki `boz2` (geçici kopya) | 96 / 96 |
| `planlama/adim3/kablolar_uret.py --kontrol` | güncel, çıkış 0 |
| `planlama/adim5/maliyet_toplam.py` | ara 105.089,07; genel 120.852,43; koşullular dahil 126.423,90; V3 kalem 125 |
| `planlama/d158/F9b-dogrula.py` | GEÇER, 0 hata |
| `planlama/d158/F9c-dogrula.py` | çıkış 1, 28 hata (P10.7a öncesi küme; maliyet `data-j` hatası yok) |
| `planlama/d158/F9d-tarama.py` | çıkış 0, README uyuşmazlığı 0 |
| `planlama/d158/testler/testler_html.py --kontrol` | geçer |

### 17.9 Doğrulanamayanlar ve uyarılar

- 5,08 mm klemensin kesit aralığı belgesiz (A06 / G07 lehimli; alt sınırı da denetimde sabit "belgesiz").
- Modül vidalı klemensleri (PC817 kartı vb.) iletken türü / aralığı yazmıyor; 22 AWG uçlar sınanmıyor (`modul-vidali` `null`).
- WAGO 2273'ün yalnız tek telli aldığı kontrolün okuduğu dağıtıcı sayfalarından; üretici sayfası açılmadı.
- G22 kuyruğunun 5 cm 18 AWG'si malzeme sayımında ayrı satır değil (18 AWG siyah silikonun payı içinde).
- Anahtarlı baranın yerleşimi kayıtlı değil; köprü tam F1 20 A ile sınanıyor (12 AWG, 20,5 A).
- XL4016 girişinin 8 V alt sınırı bu turda veri sayfasından yeniden okunmadı.
- §16.9'daki köprü yarılama uyarısı kapandı (yerleşim ve toplam hesabı §17.5-1).

### C adımında düzeltilenler (14.11; dördüncü bakış `P107a-kontrol-4.md` GEÇER, açık işlerinden yalnız dördü)

1. **Ön şarj notu (§2-1):** EL:448'in son cümlesi ve §17.7 Efe maddesi 4 "GPIO5 LOW olana kadar" diyordu; yanlıştı (PC817 #2 baranın
   dolduğunu değil gerilim olduğunu okur, ≈ 4 ms'de LOW olur). Yeni metin: en az 300 ms, boş akü için 500 ms önerilir, bekleme bitince
   GPIO5 LOW teyidi, K2 toplam en çok 1 s; pin raporundaki 300 ms için değişiklik önerisi 500 ms, karar yazılım tarafıyla. Aynı bölümün
   yazılım dizisi (EL:456, adım 3) aynı yönergeye getirildi. `pin-haritasi.md` değişmedi.
2. **`maliyet.json` kırmızı pabuç notu (§2-4):** "tel ucu katlanır" kalktı (G22 dönüşü 18 AWG ara parçayla); adet ve fiyat aynı. Demo
   yeniden üretildi (gömülü kopya).
3. **P10.7b listesi (§2-6):** `rehber_metin.py` :587, :611, :808, :842, :843, :1524 ("göğüs mini 2 A") §18.6'ya ve kuyruğa eklendi.
4. **K59:** kuyruğa kapalı kayıt olarak girdi (dördüncü bakış GEÇER); §18.3'teki öneri metni bu sonuçla birleştirildi.

Öbür açık işler (§2-2, §2-3, §2-5, §2-7) düzeltilmedi; `karar-kuyrugu.md` "Karar değil, iş" bölümünde P10.7b'nin başında yapılacak işler.

## 18. C adımında yapılacaklar

1. `planlama/dongu-158.md` P10.7 satırı (A adımındaki notun yerine, öneri):
   > 🔄 P10.7a ✅ 14.11 (commit "Lale P10.7a"; bağımsız kontroller `P107a-kontrol.md`, `-2.md`, `-3.md` + düzeltme turu 1, 2 ve ek tur +
   > dördüncü bakış …): kablo tablosu `planlama/adim3/kablolar.json` (şema 3; 74 kayıt, 62 ile eşlendi; kesin 31, teyit 42, karara bağlı 1;
   > boy belli 17, 57'si etiketli tahmin; kayıtlı kesit istisnası 5 ad / 25 kablo, koruyucu ve üst sınırıyla; ortam düzeltmeli kesit kuralı;
   > 5 V çevre hattına 2 A mini; kafa girişi ve acil stop düğümü vidalı klemensli kart), görünüm `kablolar.md`, denetim `kablolar_denetim.py`
   > (sigorta değerleri `elektrik.md` sigorta listesinden, tablo blok şemayla tam eşleşmeyle, dallar §12'den, uç türü iletken ve alt
   > sınırıyla; 121 / 121 bozma yakalandı); orkestratör kararları O-1 … O-22, D1-1 … D1-10 ve ek tur işlendi; `maliyet.json` (genel ≈ 120.900,
   > koşullu ≈ 126.400; fiyatsız 4); F8a paketine 14.11 bayatlık notu. Kalan: K52, P10.7b.
2. `planlama/dongu-158.md` §5 girdisi (saat C adımında saatten okunur):
   > - 2026-11-14 HH:MM **P10.7a kablo tablosu + sipariş listesi (üç tur + iki düzeltme turu + ek tur).** Tek kaynak
   >   `planlama/adim3/kablolar.json` (74 kablo); kesit = tablo (33 CFR 183.425 + NFPA 79) × ortam katsayısı (etek 0,82, kafa 0,75); koruma
   >   devrenin yapısından; sigorta değerleri `elektrik.md` sigorta listesinden, tablo blok şemadan denetlenir; acil stop besleme
   >   zincirinden ve §12 ile; kayıtlı istisnalar `servo-uzatmasi`, `ana-hat-12awg`, `motor-fabrika-kablosu`,
   >   `kafa-5v-donusturucu-arkasi`, `servo-ana-hat-16awg`; 5 V çevre 2 A mini (O-19); bara 5 + 4 saplama, akü dönüşü ortada, yıldız
   >   yerleşimi kayıtlı (O-22, ek tur); WAGO 2273 yerine vidalı klemensli iki küçük kart (ek tur); K03 18 AWG, şarj sigortası 7,5 A;
   >   `maliyet.json` genel 120.852,43 TL; F8a paketi bayat notlu, sipariş `maliyet.json`'dan. Açık: K52. Günlük
   >   `planlama/d158/kablo-tablosu-gunluk.md`.
3. `planlama/d158/karar-kuyrugu.md`: 1235, 1260, 1264'teki A adımı notları "yapıldı" diye kapatılır. **K59** açılır (özet tablosuna satır,
   sayımlar güncellenir; metin önerisi):
   > ## K59 · P10.7a kablo tablosunun bağımsız bakışları
   > - **Durum (14.11.2026):** üçüncü bağımsız bakış (`planlama/d158/P107a-kontrol-3.md`) geçmedi (D-A ince telli kablo tek telli WAGO
   >   2273'e, D-B komşu sigortanın değeri ve sınanmayan metin alanları, D-C blok şemayla karşılaştırılmayan röle arkası).
   > - **Karar (14.11.2026, orkestratör):** tek ek tur + dar kapsamlı dördüncü bakış. Ek tur `kablo-tablosu-gunluk.md` §17. Dördüncü bakış
   >   geçerse K59 kapanır; geçmezse orkestratöre döner.
4. Commit'e girecekler (bu paket): `planlama/adim3/kablolar.json`, `kablolar.md`, `kablolar_denetim.py`, `kablolar_uret.py` (yeni);
   `planlama/adim3/elektrik.md`, `kablolama-on-kararlar.md`, `pin-haritasi.md`; `planlama/maliyet.json`; `planlama/adim5/B-malzeme-plan.md`;
   `Lale-Proje-Ozeti.txt`; `README.md`; `planlama/proje-plani.md`; `planlama/yazilim-plani.md`; `planlama/dongu-158.md`;
   `planlama/d158/karar-kuyrugu.md`, `sonuc-rapor.html`, `F8a-siparis.md`, `F8a-siparis.json`, `kablo-tablosu-gunluk.md`;
   **`planlama/d158/P107a-kontrol.md`, `P107a-kontrol-2.md`, `P107a-kontrol-3.md`** (üç kontrol raporu; dördüncüsü gelince o da);
   `planlama/d158/testler/T3-kafa-5v-akim.md`, `T4-pam8403-ses-karti.md`, `T7-gogus-ekrani-12v.md`, `T8-servo-hatlari.md`,
   `T13-rampada-acil-stop.md`, `testler.html`; `tasarim/Robot-Tasarim-Demosu.html`, `tasarim/cad/demo_uret.py`,
   `tasarim/cad/viewer-template.html`. Girmeyecekler (bu paketten değil): `tasarim/freecad/kabuk/gorsel/*.png`,
   `tasarim/freecad/montaj/yerlesim-kontrol.json`, `tubitak-2209b/`.
5. Kontrol: `planlama/adim3/kablolar_denetim.py --bozma-denemesi` (121), `kablolar_uret.py --kontrol`, `planlama/adim5/maliyet_toplam.py`,
   F9b, F9c (28 hata, 9a0c6fe ile aynı küme), F9d, `testler_html.py --kontrol`.
6. P10.7b: boylar ölçülünce `boy` doldurulur ve `boy_tahmin` silinir; gerilim düşümü `gerilim_dusumu_kontrol` taşıyan kablolarda, ana
   hatta (`ana-hat-12awg` şartı) ve SV1–SV3'te (`servo-ana-hat-16awg` şartı); motor kablosunun kesiti okunur (`motor-fabrika-kablosu`);
   bara tutucusu çizilir (5 + 4 saplama, yıldız yerleşimi §17.5-1); kafa giriş ve acil stop düğüm kartları yerleştirilir; T8 E + E2 tezgâh
   denemeleri; ortam katsayılarının kaynağı NEC metninden okunur; XL4016 Rev 1.3 sınırı ve 8 V giriş alt sınırı bakılır; 5 V çevre yük
   bütçesindeki açılmamış veri sayfası değerleri (HC-SR04, BNO055, PCA9685) okunur; rehberdeki eski metin: `rehber_metin.py` :626, :711,
   :1291 ("şarj 10 A"), :634 ("göğüs ekranı mini 2 A"), :251, `rehber_denetim.py:151, :157`; ayrıca (dördüncü bakış §2-6)
   `rehber_metin.py` :587, :611, :808, :842, :843, :1524 ("göğüs mini 2 A").
