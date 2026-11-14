# Lale: elektrik kararları (düzeltme planı 3. adım: E0–E4, E7, K4)

Tarih: 15 Ekim 2026. Tek yer: bu dosya. CAD karşılığı `tasarim/freecad/taban/` ve `kafa/`, sayılar `taban-analiz.json`
(`donus`, `aku`) ve `kafa-analiz.json` (`tork`, `isi`, `pi`). "Tahmini" yazan değer ölçülmedi ya da kaynaktan türetildi.
Pin planı 14.11.2026'da kesinleşti (karar: Ahmet'in 13.11.2026 yetkilendirmesiyle); tek yazılı kaynağı `planlama/adim3/pin-haritasi.md`. Akü süreleri E8'in (5. adım) işi, burada yalnız anlık akımlar var.
T2 takip düzeltmesi (15 Ekim 2026, bağımsız kontrol `K3-kontrol.md`): JGB37 tork uyarısı, ESP32 beslemesi ifadesi, DTR/RTS, ön şarj, PC817 3,3 V, Pololu akımı, kafa ısısı (`T2-takip.md`).

## 158 cm güncellemesi (04.11.2026; 09.11.2026 F4a: 05.11 B + R1 yerleşimine göre)

Geçerli olan bu bölüm. Kaynak: `tubitak-2209b/BAGLAM.md` §8 (03–04.11 kararları), `tubitak-2209b/malzeme-listesi/Lale-malzeme-listesi-2026-11-03-v4.xlsx`,
`tasarim/freecad/lale158/kablo_yolu_ekran.py`, `tasarim/freecad/kafa/kafa-analiz.json`. Aşağıdaki bölümlerde bununla çelişen eski kısımlar 04.11'de silindi ya da [ESKİ] işaretlendi; eski değerler bu tabloda duruyor, tam metin git geçmişinde (`f95f96b`).
09.11 güncellemesinin kaynakları (kısaltma **KY/** = `tasarim/freecad/lale158/kafa-yerlesim/`): `KY/uygulama-notu.md` (05.11 B + R1 seçimi, satır 3),
`tasarim/freecad/lale158/lale158-kontrol.json` (`kablo_ozet`), `tasarim/freecad/montaj/robot-bom.csv`, `tasarim/freecad/arayuz.py` (`SES_USB`, satır 988–1003),
`planlama/d158/kablo-kurali-notu.md`, `planlama/d158/karar-kuyrugu.md` (K1, K10, K11, K14). Açık kararlar satırında "karar bekliyor (Kn)" yazar.
**CAD durumu (09.11):** 10,1" QLED, SY8205, Pololu D24V50F5, PAM8403, USB ses kartı, ReSpeaker Mic Array v2.0, 4'lü hub ve hoparlör modelde
(`montaj/robot-bom.csv` satır 158, 151, 147, 145, 157, 150, 156, 133); 11,6" göğüs ekranı da modelde (satır 159). Göğüs 12 V regülatörü (LM2577 + LM2596)
modelde yok (BOM'da satırı yok). Yerleşim: ses kartı ve PAM8403 kafa sol duvarında, hub gövdede göğüs üst arka servis kapağının içinde, hoparlör gövde orta bandı
sağ duvarında (`KY/uygulama-notu.md:45, 47, 56, 58, 59`). I2S amfi modelde 0 parça (`KY/uygulama-notu.md:57`; K16 kapandı, 04.11).
04.11 gecesinin "bu parçalar henüz modelde yok" notu tarihçedir.

| Konu | Eski değer | Geçerli (1,58 m) | Durum |
|---|---|---|---|
| Kafa 5 V düşürücü | 125 cm ve 1,65 m: Pololu D36V50F5 (ithal, giriş 5,5–50 V) | **Pololu D24V50F5**: 5 V ±%4, 5 A sürekli, giriş en çok 38 V (alt sınır satıcı sayfasında yok), ters gerilim, aşırı akım, kısa devre, ısı koruması, yumuşak başlatma, 17,8 × 20,3 × 8,8 mm (Robotistan; `raporlar/kaynaklar/07-gogus-ekrani-ve-5v.md`) | Karar 01.11. 12 V girişteki sürekli akım üretici eğrisinden **doğrulanmadı** |
| Kafa ekranı | 125 cm: 7" LCD 2,5 W. 1,65 m: 10,1" (B) hocadan, ≈ 0,75 A tahmini. 01.11: 7" | **10,1" QLED 1280×720 HDMI** (WaveShare, kod 20789): görünen alan 225,64 × 127,36 mm, Power ve Touch ayrı micro USB, HDMI tam boy, vida deliği yok, tırnakla tutulur | Karar 03.11 gece. Kütle üreticide **doğrulanmadı** (600 g varsayım). Modelde henüz yok |
| Kafa ekranı beslemesi | Pi USB-A'dan | **Ayrı SY8205 5 V düşürücü + P6KE6V8A**, Pi'den bağımsız. SY8205 sayfası: giriş 7–30 V, sürekli 3,7 A, koruma yazmıyor | Karar 03–04.11. QLED akımı 0,9 A **varsayım**, ölçülmedi |
| Göğüs ekranı | 125 cm: Nextion 10,1" (UART2, çevre 5 V'tan 0,8 A). 1,65 m: yok | **11,6" 1080p HDMI, kasalı (Waveshare)**: 12 V ~0,5 A, dokunmatik USB 5 V ~80 mA. Besleme **LM2577 + LM2596 kartı 12 V'a ayarlı**, sigorta kutusunun 6. yuvasında **F6 3 A** standart bıçak: ana anahtar sonrası, röle öncesi (K11 a, 14.11; düzeltme turu 1). Çerçeve gövde renginde, ekran 2 mm içeride | Karar 01.11, regülatör 03.11, çerçeve 04.11. Ekran jakı ölçüsü **doğrulanmadı** |
| Mikrofon | 125 cm: ReSpeaker Lite 0,5 W. 1,65 m: XVF3800, ~1 W varsayım | **ReSpeaker Mic Array v2.0** (XVF-3000, 16 kHz, 4 mikrofon, USB; Robotistan) | XVF3800 Türk satıcıda yok, muadil. Akımı **doğrulanmadı** |
| Amfi | [tarihçe] I2S amfi MAX98357A, 3 W tepe (04.11'de kalktı, K16) | **PAM8403 2 × 3 W**, analog girişi **ReSpeaker'ın 3,5 mm çıkışından** (14.11, **masa denemesine bağlı kabul**, KT2; pano #7 öneri 1: yankı giderme referansı; USB ses kartı kablajdan çıktı, yedek olarak siparişte; `planlama/adim3/kablolama-on-kararlar.md` §5). PAM kafa sol duvarında (`KY/uygulama-notu.md:56`). Hoparlör 40 × 20, 4 Ω, 3 W gövde orta bandı sağ duvarında, kablosu PAM'dan boyundan iner (`KY/uygulama-notu.md:59`; `robot-bom.csv:133`) | v4 muadili. PAM 5 V: **D24V50F5 (Pi hattı), K10 a (14.11), masa denemesine bağlı (KT1)**; geçmezse SY8205 (b). Akım ölçülmedi: PAM tepesi 0,71 A hesap (3 W, verim %85 varsayımı; `KY/uygulama-notu.md:98`); T4 ile ölçülecek |
| Kafa 5 V toplam | 125 cm: 18,7 W → 3,7 A tepe. 1,65 m: ≈ 20,5 W → 4,1 A tepe | **Normal karşılama 3,57 A** (QLED 0,9 A varsayımıyla; ≈ 17,85 W) | Hesap, ölçülmedi. Tepe değer yeni düzende hesaplanmadı |
| "16,2 W" | Önceki kafa 5 V hesabında geçen değer | Kullanılmıyor | **Türetilmiş değerdi**, ölçüm ya da üretici verisi değil. Hangi kalemlerden türediği bu klasörde bulunamadı |
| Pi hattı (D24V50F5) | Ekran dahil tek hat | **2,67 A** (ekran ayrı düşürücüde); 5 A'in %53'ü | Hesap, ölçülmedi |
| Ekran hattı (SY8205) | Yok | **0,9 A varsayım**; 3,7 A sürekli sınırının %24'ü | Ölçülecek |
| Kafa 12 V (F3 5 A) | 125 cm: tepe 1,62 A. 1,65 m: tepe ≈ 1,8 A | Normal ≈ 1,55 A (3,57 A × 5 V ÷ 0,90 ÷ 12,8 V) | Hesap. SY8205 verimi bilinmiyor, Pololu'nunki alındı (0,90). F3 aynı |
| Akü, normal kullanım | 125 cm: 5,7 sa. 1,65 m: 5,9 sa (7", göğüs ekranı yok) | **~3,8–4,4 sa** (kaba tahmin; 207 Wh kullanılabilir ile ≈ 47–55 W demek) | **Ölçülmedi.** Yoğun senaryo (1,65 m: 1,83 sa, Ahmet kabul etti 29.10) yeni yüklerle yeniden hesaplanmadı |
| Kapalı kafa, 30 °C ortam | 125 cm: en kötü 49 °C (14,5 W). 7" (`kafa-analiz.json`): en kötü 44,4 °C (14,5 W) | **~49 °C**, normal karşılama (R 0,992 K/W ile 3,57 A ÷ 0,90 ≈ 19,8 W'tan 49,7 °C: tutarlı). Servo sınırı 55 °C | **Ölçülecek.** En kötü durum yeni düzende hesaplanmadı |
| USB | LCD, mikrofon, ESP32 doğrudan Pi'de. 04.11: "6 cihaz, Pi'de 4 port, 4'lü hub", hub'ın yeri açık | **4 cihaz** (14.11: altıncı cihaz yok, K1; USB ses kartı çıktı, ses yolu masa denemesine bağlı, geçmezse kart Pi port 2'ye) + 4'lü hub (USB 2.0, **USB'den beslenir**, harici besleme yok (14.11, pano #6 öneri e reddedildi), tek anahtar açık kalmalı, 72 × 25 × 19 mm). Hub gövdede, göğüs üst arka servis kapağının içinde (`arayuz.py:1001` `SES_USB.hub`, y 1.085–1.157; `KY/uygulama-notu.md:58`; K5 kapandı). Port dağılımı aşağıda "USB" paragrafında | K1 a (14.11, pano #5 mesaj #23); Pi port 2 ve hub'da 2 port boş |
| Boyun demeti | 12 V çift + ESP32 USB + tilt; "HDMI ve CSI boyundan çıktı". 04.11: + göğüs HDMI + göğüs USB dokunmatik | **5 kablo:** kafa 12 V çift (18 AWG) + tilt servo + göğüs ekranı HDMI + hub uzatması (USB) + hoparlör. Göğüs USB dokunmatiği ve ESP32 USB hub'dan çıkar, boyundan geçmez; göğüs ekranı 12 V'u tabandan gelir, boyundan geçmez. CSI kafada kalır (`kablo_yolu_ekran.py:6, 31`; `planlama/d158/kablo-kurali-notu.md:20-35`) | **K14 a (14.11)**: Efe'nin tarafı yazılım açısından kabul (pano #6 #21); şart: **alınacak HDMI kablosu Ø ≤ 6 mm**, ince / esnek (MJ:191 kablonun çapı bilinmiyor); **hub uzatması USB 2.0, erkek fiş gövdesi ≤ 13 × 7 mm**, HDMI'den önce geçirilir; servo kanalı 20 × 7,8 kapalı tünel, iki dik dönüş: kablolar bu şartla 16.11'de sipariş edilir; **demet kurulmadan önce, teslimde, tünelin basılmış kısa deneme parçasında elle fiş geçirme denemesi zorunlu**, geçmezse fişsiz geçirip yeniden sonlandırma / HDMI için şerit (FPC) + uç adaptörleri (`kablolama-on-kararlar.md` §4); demet bağlanmadan önce Efe'nin reset cevabı (§7); masa denemesi ve büküm kablajda teyit |
| Servo uzatması | 1,65 m: dirsek, bilek 1,93 m; S2 ≈ 1,77 m | Dirsek, bilek 1,86 m; S2 1,70 m (v4, model) | Hesap |
| ESP32 USB | 1,65 m: Pi → ESP32 ≈ 1,64 m. 04.11: ≈ 1,57 m, 2 m kablo | **Hub → ESP32 (taban):** yol 971 mm, önerilen 1.360 mm (yol × 1,25 + 150 kapak sökme payı); v4'teki 2 m kablo yeter. Pi → hub: hub'ın 130 mm kablosu + uzatma, yol 617, önerilen 920 mm (`lale158-kontrol.json` `kablo_ozet.kablo`; `arayuz.py:1003`) | Hesap (yol şema, pay tahmini) |
| Akü kütlesi | Model 2.800 g (09.11 öncesi) | **3,0 kg** (Victron datasheet; `planlama/maliyet.json` Victron satırı, `raporlar/kaynaklar/06-aku-secimi.md:119`); modelde `arayuz.py:623` 3.000 g. Robot ev pozu 26.115,6 g (400 g kablo payı dahil), yüksüz rampa devrilme payı 1,519 (`KY/uygulama-ivme.json` `ev.kutle_g`, `izgara_yuk_0g.a_sinir_pay15.rampa5_geri`) | F1b (`planlama/d158/F1b-gunluk.md` P1.1) |
| Hat sigortası yuvası | ×2, sonra ×4, v4'te ×5 (beşincisi göğüs) | **×4** (A, B, C, şarj); göğüs ekranı kutunun F6 yuvasında (K11) | 14.11 düzeltme turu 1 |

**Kafa güç mimarisi (geçerli):**

```
F3 5 A ── 18 AWG çift ── boyun ── kafa girişi: P6KE18A
   ├─ Pololu D24V50F5 5 V ── P6KE6V8A ── USB-C ── Raspberry Pi 5 + diğer kafa yükleri   (2,67 A, hesap)
   │     └─ PAM8403 5 V (kablo yol 64 / önerilen 80 mm)                                    (K10 a, masa denemesine bağlı; tepe 0,71 A hesap)
   └─ SY8205 5 V ──────────── P6KE6V8A ── micro USB Power ── 10,1" QLED                  (0,9 A, varsayım)
```

PAM D24V50F5'ten beslenir: **K10 a, masa denemesine bağlı** (14.11, orkestratör, Ahmet'in 13.11 yetkilendirmesiyle; düzeltme turu 1). Pi hattı 5 V bütçesi (hesap, ölçülmedi): Pi + soğutucu tam yük 2,40 A (12 W, E8) + ReSpeaker 0,18 + hub 0,13 (tahmin) + QLED Touch ~0,05 (tahmin) + kamera 0,14 + PAM tepesi 0,71 ≈ **3,61 A (5 A'in %72'si)**; **AI HAT+ (güç değeri resmî değil, ~2,5 W tahmin) +0,5 A → 4,11 A (%82), yükte ≈ 4,51 A (%90)**. `KY/uygulama-notu.md:98`'in 3,28–3,38 A'i Pi tam yükünü içermiyor. Gerekçe: D24V50F5 korumalı, ReSpeaker (ses kaynağı) ile aynı çıkış toprağı.
**Şart (KT1):** Pi stres + en yüksek ses (+ takılıysa AI HAT+) altında Pi düşük gerilim uyarısı vermez (`vcgencmd get_throttled` = 0x0) ve hat ≲ 4 A (DC pens ya da GND dönüşünde şönt; seri multimetre değil); Pi girişi `vcgencmd pmic_read_adc` EXT5V_V ile okunur. Geçmezse PAM **SY8205'e (b)**: SY8205 0,9 (varsayım) + 0,71 ≈ 1,61 A (3,7 A'in %44'ü); kablo yine tek, uç SY8205 çıkışı, PAM 5 V hattına küçük sigorta (SY8205'te koruma yazmıyor), KT2 yeniden.
**AI HAT+ siparişi / takılması bu denemeye bağlıdır.** PAM 5 V kablo boyu `lale158-kontrol.json` `kablo_ozet.kablo."PAM 5 V"`.

- **İki 5 V kaynağı köprülenmez.** QLED'in Touch micro USB'si Pi'ye veri için gider. Touch VBUS'u ekran içinde Power girişine bağlıysa Pi'nin 5 V'u ile SY8205 çıkışı Touch kablosu üzerinden birleşir. Ekranın iç bağlantısı **doğrulanmadı**: kart gelince Pi'ye takmadan multimetreyle Power ile Touch VBUS arasına bak. Bağlıysa çözüm o ölçümle seçilir (tahmini çözüm yazılmadı).
- **Ekran kablosu:** kafa içi kısa HDMI 30 cm şerit + iki lehimsiz fiş (Pi ucu micro HDMI düz, ekran ucu HDMI düz; v4'te üç satır, tek kablo). Power: 30 cm USB-A → micro B kablonun USB-A ucu kesilir, SY8205 çıkışına bağlanır. Touch: kutudaki USB kablosu.

**Göğüs ekranı dalı (geçerli):**

```
Sigorta kutusu F6 3 A (standart bıçak, 6. yuva) ── LM2577 + LM2596 kartı (giriş 4–35 V, 12 V'a ayarlı) ── 18 AWG ── 11,6" ekran 12 V jakı (90° fiş)   ana anahtar sonrası, röle öncesi (K11 a, düzeltme turu 1); boyundan geçmez
Pi 5 micro HDMI 1 ── HDMI (v4 1,5 m) ── boyun ── ekran HDMI (ekran ucunda 90° fiş / adaptör)                                    K14 a (14.11); alınacak kablo Ø ≤ 6, masa denemesi
Hub (göğüs üst arka kapağı içi) ── USB-A → micro B (v4 2 m) ── ekran TOUCH (90° fiş)                                              boyundan geçmez; hub'a Pi port 3'ten boyundan gelen uzatmayla bağlı
```

- Regülatörü ekrana bağlamadan multimetreyle 12 V'a ayarla (akü 12,8–14,4 V, v4). Ekran fişi: kutudaki adaptör kablosu kesilebilir (v4).
- **K11 a (14.11; düzeltme turu 2, üçüncü bakış bekliyor):** dal sigorta kutusunun **6. yuvasından (F6, 3 A standart bıçak; bulunamazsa 5 A standart)** çıkar; ayrı hat yuvası kalktı; kutu yuvaları ortak baralıysa korumasız ara kablo yok, ayrı girişliyse 12 AWG kısa giriş köprüleri (KT3, teslimde bakılır). GND WAGO yıldızına. Ana anahtar kapalıyken kesilir, **acil stopta ekran açık** (hareket üretmez; durumu gösterir). Giriş (regülatör verimi %80 varsayım): ekran tipik ~0,5 A ile ≈ 0,59 A @ 12,8 V, ≈ 0,75 A @ 10 V; ekran en çok 1 A (12 V / 1 A adaptör) ile ≈ 1,17 A @ 12,8 V, **≈ 1,5 A @ 10 V = 3 A'in %50'si** (2 A'de %75: sıcak etekte pay dar). 18 AWG 3 A ile korunur. Gerekçe `kablolama-on-kararlar.md` §3. Port yeri fotoğraftan tahmini (`arayuz.GOGUS_EKRAN` port; `arayuz.py:343-346`).
- **90° fiş üç kabloda:** HDMI, USB dokunmatik (micro B) ve 12 V jakı. Kablo ekranın −X kısa kenarındaki port girintisine 18 mm yatay girer; düz fiş bu dönüşü yapamaz (`planlama/d158/F1b-kontrol.md` madde 12 ve "90° fiş" maddesi). Fiş gövdeleri modelde yok; port girintisi modelde yok, ekran gelince ölçülecek (P1.4 🟡).
- Yol / önerilen boy (yol × 1,25, hub'a bağlı kablolarda + 150 mm kapak sökme payı; ikisi de tahmin; `lale158-kontrol.json` `kablo_ozet.kablo`, `arayuz.py:1003`):
  HDMI 757 / 950 mm, USB dokunmatik 395 / 640 mm, 12 V 1.376 / 1.720 mm. 04.11'deki USB dokunmatik 1.060 mm Pi'den boyundan inen eski yola aitti (tarihçe).
  Göğüs ekranı kasası × kablo tüpü gerçek çakışma 0; port ucu temas hacmi HDMI 897,1 / USB 391,5 / 12 V 617,3 mm³, port girintisi varsayımıyla (`lale158-kontrol.json` `kablo_tup_uc_temas`; F1b).

**USB (4 cihaz, 14.11; 4 Pi portu + 4'lü hub):** port dağılımı modelde (`KY/uygulama-notu.md:123-132`; `arayuz.py:997` `SES_USB.pi_usb`; Pi 2 modelde hâlâ ses kartı, P10.7):

| Port | Cihaz | Kablo (yol / önerilen mm; `lale158-kontrol.json` `kablo_ozet.kablo`) |
|---|---|---|
| Pi 1 | ReSpeaker Mic Array v2.0 | Dizi USB, kısa micro USB 85 / 110 |
| Pi 2 | **Boş** (14.11: USB ses kartı çıktı; ses ReSpeaker 3,5 mm → PAM8403, masa denemesine bağlı (KT2); geçmezse yedek kart buraya) | — (eski: ~30 cm uzatma + L dirsek, 217 / 270) |
| Pi 3 | 4'lü hub (gövde, göğüs üst arka kapağı içi) | Hub'ın 130 mm kablosu + ~1 m USB-A uzatma, boyundan, 617 / 920 |
| Pi 4 | Kafa ekranı (10,1" QLED) Touch | Kutu kablosu 350 mm, kafa içi yol 217 (`kablo_ozet.kafa_ici_qled`) |
| Hub 1 | Göğüs ekranı (11,6") Touch | USB-A → micro B, 395 / 640 (v4 2 m) |
| Hub 2 | ESP32 (CP2102), VBUS'ta 1N5819 | 971 / 1.360 (v4 2 m) |
| Hub 3, 4 | Boş | — |

- **6. cihaz yok (K1 a, 14.11; pano #5 mesaj #23).** Ses ReSpeaker'dan çıktığı için cihaz sayısı 4. ReSpeaker 5 V 180 mA (Seeed wiki). Pi 5 USB çevre
  birimlerine 5 A kaynakla 1.600 mA, aksi hâlde 600 mA verir, bütçe fan girişiyle paylaşılır (raspberrypi.com "Power supply"); Ayar adları (raspberrypi.com): EEPROM'da `PSU_MAX_CURRENT=5000` (USB-PD görüşmesini atlayıp bu akımı varsayar) ya da `/boot/firmware/config.txt` içinde `usb_max_current_enable=1`; kurulumda yapılır.
- Hub kapanırsa ESP32 bağlantısı ve göğüs dokunmatiği birlikte düşer (`kablo-kurali-notu.md:54-55`). Hub yükü ≈ 0,1 A (göğüs dokunmatiği; ESP32 VIN'den beslenir, VBUS diyotlu ikinci kaynak): harici besleme yok (14.11). **F4 atarsa** ESP32 tamamen hub'dan beslenir (0,24 A, E4): hub ≈ 0,37 A, Pi USB toplamı ≈ 0,6 A (ReSpeaker 0,18 + hub 0,37 + QLED Touch ~0,05): ayar yoksa 600 mA sınırında, ayarla 1,6 A içinde (hesap). Hub girişindeki gerilim ölçülmedi (`KY/uygulama-notu.md:100`); kablajda teyit.
- Listede olmayan 6 kablo kalemi (K4) ve göğüs ekranının 3 adet 90° fişi `planlama/maliyet.json`'a fiyatsız, koşullu aday olarak girdi (P4.2, 09.11).

**Sigorta dalları (geçerli):** ana 30 A → F1 20 A (röle K1 → anahtarlı bara: BTS7960 × 2, hat 7,5 A → XL4016 A, hat 7,5 A → XL4016 B, hat 5 A → XL4016 C), F2 15 A yedek, F3 5 A kafa, F4 5 A XL4016 çevre, F5 2 A acil stop, F6 3 A göğüs ekranı (K11, 14.11); ayrıca şarj girişi mini 10 A. Ayrıntı "Sigorta listesi".

**v4 muadilleri (elektriği etkiler, bölümler yeniden yazılmadı):** röle K1 MAH-112-C-4 30/40 A (dahili diyot yazmıyor, 1N4007 kullan); ön şarj rölesi K2 JQC-3FF 10 A (E9'daki JQC-3F(T73) 7 A yerine; ayak düzeni pertinakta kontrol edilir); motor sürücü BTS7960B (pin adları EN1/EN2, IN1/IN2; pin planında EN = INH, IN = PWM varsayımıyla eşlendi, `pin-haritasi.md` §6.1; 3,3 V lojik sayfada yok, kart gelince kontrol); acil stop NP2 BE102 (CAD 60 mm B200E60; etek deliği kontrol); hızlı klemens 2273-203 en çok 2,5 mm², 12 AWG ana kabloda kullanılmaz; şarj cihazı IMAX B6 (4S'te ≈ 3,4 A; 14,6 V kesme cihazda ölçülecek).

## 1,65 m güncellemesi (Y2b, 29 Ekim 2026) [tarihçe]

**Tarihçe (09.11 notu):** ana tasarım 01.11'den beri 1,58 m; bu bölüm o günkü 1,65 m tasarımını anlatır. 1,58 m'de değişenler üstteki bölümde, burada yalnız
"[1,58 m: …]" işaretli satırlar ve 1,58'de değişmeyen kararlar (akü yeri, acil stop, servo hatları, Pi 4 GB) geçerli.
Bu dosyanın gövdesi 125 cm tasarım (15 Ekim) içindir. Yüz ekranı, göğüs ekranı, mikrofon ve kafa 5 V satırları 04.11'de üstteki tabloya taşındı. O günkü 1,65 m tasarımında değişen ve
geçerli kalanlar aşağıda. Kaynak: `tasarim/freecad/taban/taban-analiz.json` (Y2a, robot 24,80 kg), `planlama/y2/Y2b-aku.py` →
`Y2b-aku.json` (E8 yeniden), `planlama/y2/Y2b-ivme.json`, `planlama/kararlar-2026-10-29.md`. Yeni yük değerleri tahmini.

| Konu | 125 cm (bu dosyanın gövdesi) | 1,65 m (29.10; 1,58 m'de değişmeyenler geçerli) |
|---|---|---|
| Akü | Victron SuperPack 12,8/20, taban arka bölmesi | **Aynı yerde** (75 mm öne geometrik olarak olmadı). Karar 29.10: rampada / eğimde kollar ev pozunda ve taban ivmesi ≤ 0,1 m/s²; düzde ≤ 0,5 m/s² (devrilme sınırı ≈ 2,0 m/s², `Y2b-ivme.json`). Karar 29.10 (Y2b): yazılım / acil stop freni düz zeminde **≤ 1,8 m/s²** (düzde 0,5 kg el yüküyle bile devrilme payı 1,54). Karar 29.10 (Ahmet): **rampada / eğimde yavaşlama ve fren de ≤ 0,1 m/s²** (rampada 1,8 frende ev pozu payı 1,31 < 1,5) |
| Acil stop, devreye alma (E3, E9) | K1 40 A (GPIO12, IRLZ44N #1), K2 7 A + 5,6 Ω ön şarj (GPIO2, IRLZ44N #2), PC817 #1 mantar sonrası (GPIO23), #2 anahtarlı bara (GPIO5), F5 2 A | **Değişmedi** (yalnız pinler, 14.11: K1 GPIO4, K2 GPIO19; röle sürücüsü 14.11'de BC337-40, `pin-haritasi.md` sürüm 4). Devreye alma komutu Pi'den (telefon kumandası; Nextion yok). CAD'de güç panelinde K1 + soket ve ana sigorta var; **Y3 (29.10): K2 (JQC-3F 7 A) + 5,6 Ω 11 W + 1N4007 güç panelinde "Ön şarj kartı" (70 × 50 pertinaks, merkez x −97,5 / z −1, akünün önünde) olarak CAD'e girdi** (zarf tahmini). Pin tablosundaki "GPIO2 boş" çelişkisi Y2b'de düzeltildi |
| Ana bilgisayar | Raspberry Pi 5 8 GB (liste) | **Raspberry Pi 5, 4 GB RAM** (eldeki kart; Ahmet 29.10: "pi 4 gb"). Güç bütçesi aynı bırakıldı (4 / 7 / 12 W; 8 GB ölçümlerine dayanıyordu, 4 GB'ta en çok biraz daha az) |
| Omuz servoları (E1) | DS3218MG; hat yoğun 4,4 / 4,7 A | **DS3235** (durma 2,1 A @6 V datasheet; tasarımda 3,0 A ihtiyatlı). Kol ×1,25 ile kol + kafa servosu bir hatta yoğun ≈ **5,45 A** (A, pan ile 5,47; B, tilt 0,9 ile ≈ 5,8), tepe 7,8 A (taslak kol analizi) → XL4016'nın sürekli 5 A önerisinin üstünde. **Karar 29.10: kafa servoları kol hatlarından ayrıldı, üç servo hattı** (aşağıdaki "Servo hatları" tablosu): kol hatları yoğun ≈ 4,87 A. Hat akımı yine ölçülmeli |
| Servo uzatmaları | ~1,3 m | [1,58 m: üstteki tablo] dirsek / bilek 1,93 m, S2 ≈ 1,77 m (1.769,8 mm: Y2b hesabı, göbek eki yolu = G2 öncesi 20 + geçiş 23,9 + S1 lopu 171,4 + gövde içi 238 + dikey 1.286,5 + konnektör 30; `planlama/y2/Y2b-kontrol.md` bulgu 4. `dirsek-analiz.json` `kablo.s1_boy` S2 satırı Y3'te (29.10) `dirsek_montaj.py` ile yeniden üretildi: DS3235 **1.770 mm**, eski yarık yolu 1.490 kalktı); durma akımında 2 × 1,93 × 0,052 × 2,5 A ≈ 0,50 V düşüm (servo ≈ 5,5 V görür; tahmini) |
| ESP32 – Pi USB | 1,25 m | ≈ 1,64 m (1,58 m: ≈ 1,57 m) → **2 m** kablo |
| Kafa 12 V (18 AWG çift) | boyundan | +0,385 m; 1,8 A'de ek düşüm < 0,03 V (ihmal) |
| Taban, dönüş (E0) | 21,73 kg, iz 356 (x ±178) | 24,80 kg, AM (−0,2; 521,3; −13,2), iz 432 (x ±216). Yerinde dönüş μ 0,5: en yüklü motor 15,7 kg·cm = sürekli ×2,49, 2,12 A; ön omniyle ×0,47. Karar aynı: önce ölç, μ ≥ 0,4 → ön omni |
| Akü süreleri (E8) | Victron boşta / normal / yoğun 10,9 / 5,7 / 2,0 sa | **12,1 / 5,9 / 1,83 sa** [1,65 m yükleriyle: 7", göğüs ekranı yok; 158 cm kaba tahmini üstteki tabloda] (akü tarafı 17,1 / 35,1 / 113,5 W, XL4016 × 4 boşta dahil; yoğun omniyle 2,07; ders 5,8, fuar 5,1 sa → 8 saatlik fuar için öğle şarjı ya da ikinci akü, değişmedi). **Gereksinim 2 saat kullanım; yoğun kullanımda hesaplanan 1,83 sa Ahmet tarafından kabul edildi (29.10).** Normal / tipik 5,9 sa ✔ (gereksinimin ≈ 3 katı); yoğun 1,83 < 2 (kabul). Tasarım değişikliği yok (`Y2b-aku.json` `gereksinim_2sa`) |
| Yedek GPIO | GPIO2 (E9 ile K2'ye gitti) | GPIO16 / 17 (14.11: enkodere gitti, röleler GPIO4 / 19'a; boş kalan GPIO12, `pin-haritasi.md`) |

**Servo hatları (karar 29 Ekim 2026, Ahmet: "iki ayrı regülatör, sol kol / sağ kol"):** her kol kendi XL4016'sında, kafa servoları
(pan + tilt) üçüncü bir XL4016'da (yeni; XL4016 3 → 4, `maliyet.json`). Akımlar `taslak-170/kol-analiz/kol-analiz.json` (oran 1,25, DS3235)
servo başına değerlerinden; tepe = 2 servo kalkışta (DS3235 3,0 A, MG996R 2,5 A) + diğerleri yoğunda. Giriş = 6 V × I / 0,88 / 12,8 V. Tahmini.

| Hat | Servolar | Yoğun (6 V) | Tepe (6 V) | Giriş yoğun / tepe (12,8 V) | Hat sigortası |
|---|---|---|---|---|---|
| A | sağ kol: S1, S2 (DS3235), dirsek, bilek | **4,87 A** (1,80 + 1,83 + 0,84 + 0,40) | **7,24 A** | 2,6 / 3,9 A | 7,5 A (aynı) |
| B | sol kol: aynı | **4,87 A** | **7,24 A** | 2,6 / 3,9 A | 7,5 A (aynı) |
| C (yeni) | kafa pan + tilt (MG996R) | **1,5 A** (0,6 + 0,9) | **5,0 A** | 0,8 / 2,7 A | 5 A mini (yeni yuva) |

- Neden kafa ayrı hatta: kafa servosu hangi kol hattına girse o hat > 5 A (pan ile 5,47, tilt ile ≈ 5,8; ikisi bir kolda ≈ 6,4). Kafayı çevre 5 V
  XL4016'sına (ESP32 / sensör beslemesi; servo gürültüsü, 5 V'ta düşük tork) ya da kafadaki Pololu'ya (kafa 5 V tepe 4,1 A + 5 A > 5,5 A) bağlamak reddedildi.
- Kol hatları yoğunda 5 A önerisinin %97'si: sınırda kalıyor, hat akımı ölçümü (E7 yük testi) yine gerekli; aşarsa o hat için 20 A düşürücü.
- XL4016 C güç panelinde, diğer üçünün arkasında (Y3 yerleşimi; yük A / B'den taşındı; E7 ısısına ek yalnız boşta kaybı ≈ 0,13 W); çıkış 2 servo uzatmasına küçük klemensle, dağıtım kartı gerekmez
  (2200 µF kondansatör önerilir; maliyette yok). **Y3 (29.10): dördüncü XL4016 (C) CAD'de güç panelinin üstünde (merkez x 97,5 / z 0, 8 mm naylon burç), akünün önünde** (alt vidalar akünün üstüne gelmez); CAD'deki XL4016 adları A sağ kol / B sol kol / C kafa. Hat sigortaları kablo üstünde (CAD'de çizilmez). PCA9685 kanalları (sinyal) değişmez; yalnız
  pan / tilt kanallarının beslemesi C hattından gelir.

## Özet: ne değişti

| Konu | Önce | Sonra |
|---|---|---|
| Pi 5 | Tabanda, XL4016 "Pi 5,1 V" ile | **Kafada** (K4). Boyundan 12 V + ESP32 USB çıkar; kafada 5 V düşürücü (04.11: Pololu D24V50F5 5 V / 5 A) |
| Servo beslemesi (E1) | 10 servo tek XL4016 (8 A), güç PCA9685 V+ üstünden | **İki hat:** A = sağ kol + pan, B = sol kol + tilt. İki XL4016 (biri Pi'den boşaldı), 16 AWG, iki dağıtım kartı; PCA9685 V+ boş |
| Sonar (E2) | 5 V echo doğrudan ESP32'ye | 4,7 kΩ / 10 kΩ bölücü (3,40 V) |
| Akü ölçümü (E2) | Yok | 100 kΩ / 18 kΩ bölücü + 100 nF, GPIO36 |
| Acil stop durumu (E2) | Okunmuyor | PC817 #1 mantar sonrası 12 V'u okur; PC817 #2 anahtarlı 12 V barayı okur |
| PCA9685 / BNO055 mantık (E2) | 5 V | 3V3 (ESP32 regülatörü) |
| Acil stop yeniden başlatma (E3) | Mantar bırakılınca röle kendiliğinden çeker | Bobin: F5 → mantar NC → bobin → BC337-40 (ESP32 "devreye al", GPIO4; 14.11'e dek GPIO12). Bırakmak gücü vermez |
| ESP32 beslemesi (E4) | Pi USB'si + çevre 5 V birlikte | Diyotlu VEYA (iki kaynak): asıl çevre 5 V (VIN); USB kablosunun VBUS teline seri 1N5819 (anot Pi tarafında). Pi'ye geri besleme yok, CP2102 VBUS algısı sürer |
| Amfi | Tabanda (I2S 1 m boyundan) | Kafada (04.11: PAM8403 + USB ses kartı, I2S kalktı; 05.11 B + R1: kafa sol duvarı, `KY/uygulama-notu.md:56`). **14.11: ses yolu değişti, bkz. `kablolama-on-kararlar.md` §5:** PAM girişi ReSpeaker 3,5 mm çıkışından, USB ses kartı yedek. Bu, Ahmet'in 04.11 seçimini (K16: PAM8403 + USB ses kartı) değiştirir; masa denemesine bağlı (KT2) |
| Etek ısısı (E7) | Pi + 3 XL4016 + 2 BTS kapalı etekte | Pi ve onun XL'i çıktı (≈ −8…11 W). Fan yeri ayrıldı (ölçüme bağlı), ölçüm planı aşağıda |

## E0: dönüş yükü ve K1

**Hesap:** `tasarim/freecad/taban/donus_hesap.py` (FreeCAD gerekmez; `taban_montaj.py` çağırır → `taban-analiz.json` `donus`).
**Ölçüm gelince yalnız** `arayuz.TABAN['donus']` içindeki `mu_olculen`, `stall_kgcm_olculen`, `stall_A_olculen` doldurulur;
hesap "ölçülen" senaryoyu ekler, karar ona göre verilir.

Varsayımlar (hepsi açık):
- Robot ev pozu 21,73 kg, AM (−0,2; 372,9; −13,8) mm (taban + güncel kafa + montajın geri kalanı + 400 g kablo payı; T2 kafa perdesiyle 21,71 → 21,73, tablo değerleri yuvarlamada aynı). Arka aks daha yüklü: ön 98,6 N, arka 114,5 N.
- Kare yerleşim: iz 356 (teker düzlemi x ±178), aks arası 370 (z ±185), teker r 62,5 mm. Her yandaki iki motor aynı BTS7960'tan paralel sürülür, yani aynı hızda döner.
- JGB37-520 60 dev/dk: durma 21 kg·cm (Direnc.net sayfası), sürekli = durmanın %30'u = 6,3 kg·cm (projedeki ölçüt). Durma akımı 2,8 A (tahmini, `06-aku-secimi.md`), boşta 0,12 A; akım torkla doğrusal.

> **Uyarı (JGB37 torku doğrulanmadı, K3):** 21 kg·cm yalnız satıcı etiketi: Direnc.net sayfasında "Tork 21KG" yazıyor, birim yok, durma mı nominal mi belli değil.
> Aynı motorun Aslong tablosu 1:90 (66 dev/dk) için **durma 9 kg·cm / 1,2 A** veriyor (`raporlar/kaynaklar/06-aku-secimi.md` satır 15); 60 dev/dk (≈ 1:100) için bu ≈ 10 kg·cm.
> Hesap değeri değişmedi (21), yalnız senaryo koşuldu: `T2_donus_9kg.py` (`donus_hesap.py`'yi import eder, arayüz değişmez). Durma 9 kg·cm, sürekli 2,7 kg·cm, durma akımı 1,2 A ile:
>
> | μ | Yerinde dönüş (arka) | Durmanın | Üst sınır | Ön omni | Omni / sürekli 2,7 | Omni düz gidiş çekişmesi |
> |---|---|---|---|---|---|---|
> | 0,4 | 12,1 kg·cm | **%134** | %194 | 2,7 kg·cm | ×1,00 | ×0,68 |
> | 0,5 | 14,9 kg·cm | **%165** | %240 | 2,6 kg·cm | ×0,95 | ×0,86 |
> | 0,6 | 17,7 kg·cm | **%197** | %285 | 2,9 kg·cm | ×1,08 | ×1,08 |
>
> Sonuç: tork gerçekten ~9 kg·cm ise standart tekerle robot **yerinde dönemez** (μ 0,4'te bile motorlar durur); ön omniyle dönüş durmanın %29–33'ü, yani sürekli sınır (%30) civarında (×0,95–1,08; sınırda, ısıl yük izlenmeli).
> Omni + Ø127/Ø125 çap farkı düz gidişte de sürekli değere yaklaşır: Ø125'e yakın omni ya da hız düzeltmesi gerekir. Yazılımdaki "> 2,0 A'de kes" eşiği bu senaryoda geçersiz (durma akımı 1,2 A): eşik ölçümden sonra yazılır. (14.11: durma algılama enkoderle, satır 203.)
> Düz sürüşte de pay daralır: `taban-analiz.json` `motor` düz 0,5 m/s² ivmede 2,75 kg·cm (2,7'nin ×1,02), 5° rampa + 0,5 m/s² 5,7 kg·cm (×2,1; durmanın %63'ü).
> **Motor (durma torku + akımı) ve zemin μ ölçümü omni siparişinden ÖNCE yapılmalı** (ölçüm aşağıda). Tork ≤ 10 kg·cm çıkarsa omni tek başına yetmeyebilir: daha düşük devirli (daha yüksek oranlı) JGB37 ya da daha güçlü motor da değerlendirilmeli.
- Sürtünme: Coulomb, her tekerde kuvvet ≤ μN, yönü kayma hızının tersi. Lastik esnemesi için kayma ölçeği 0,05 (kaymanın hıza oranı 0,05'te kuvvet ≈ 0,7 μN; tahmini). Yuvarlanma direnci Crr 0,03. Omni makarası yanal direnci 0,05 (tahmini).
- **Üst sınır** modeli ayrıca: yanal sürtünme tam μN, dönüş direnci katsayısı μ_t = μ / (0,925 + 0,15 R/B) (Wong, *Theory of Ground Vehicles*, kayarak yönlenme yarı ampirik bağıntısı).

| μ | Yerinde dönüş, en yüklü motor (arka) | Sürekli 6,3'ün | Durma 21'in | Akım | Üst sınır (R 0) | Ön omni ile |
|---|---|---|---|---|---|---|
| 0,4 | 12,1 kg·cm | ×1,91 | %57 | 1,7 A | 17,5 (×2,78; durmanın %83'ü) | 2,7 kg·cm (×0,43) |
| 0,5 | 14,9 kg·cm | ×2,36 | %71 | 2,0 A | 21,6 (×3,43; **durmanın %103'ü**) | 2,6 kg·cm (×0,41) |
| 0,6 | 17,7 kg·cm | ×2,81 | %84 | 2,4 A | 25,7 (×4,08; **%122**) | 2,9 kg·cm (×0,46) |

- Ön motorlar 9,2 / 11,3 / 13,4 kg·cm. Dönme merkezi ağır arka aksa ~26 mm kayar.
- Dönüş ivmesi payı (1 rad/s², I_z ≈ 0,85 kg·m²) motor başına +0,8 kg·cm.
- **Yay çizerek dönüş** (aynı model, u_sol = k·u_sağ): R ≈ 0,12 / 0,37 / 1,10 m için μ 0,5'te 14,8 / 14,4 / 13,0 kg·cm (×2,34 / ×2,29 / ×2,06).
  Üst sınırda R 0,5 / 1 / 2 m: 17,8 / 15,2 / 11,8 kg·cm. Kare yerleşimde yanal kayma yarıçaptan bağımsız olduğu için yay **çok az** yardım eder.
  R ≥ 2 m bile μ 0,5'te sürekli değerin ×1,9'u.
- **Ön omni** (Nexus 14075, Ø127 × 29, 22 makara Ø19, 480 g, 30 kg; [ozrobotics](https://ozrobotics.com/shop/double-aluminum-omni-wheel-5-inches-basic-14075/)): robot arka aks ortası (z −184) etrafında döner, arka tekerler neredeyse saf yuvarlanır.
  Motor yükü 2,6–2,9 kg·cm (×0,41–0,46). Omni Ø127, teker Ø125: aynı motor hızında önler %1,6 hızlı, düz giderken ön motorlara 1,8–2,9 kg·cm çekişme biner (arka 0,2–0,8 fren).
  Kabul edilebilir, ama Ø125'e yakın omni bulunursa o seçilmeli. **Omni teker düzlemi standartla aynı olmalı (x 178):** farklı x'te (163,5) hesap, ayni yandaki ön/arka motorun birbirine karşı çalıştığını gösterdi (arka motor 17 kg·cm fren).

**Sonuç (μ 0,5, ölçüm yok): KÖTÜ.** Yerinde dönüş sürekli değerin %236'sı; üst sınır modelinde durma torkunu aşıyor (μ ≥ 0,5'te robot dönemeyebilir).
**K1 önerisi:** Kararınız aynı kalıyor: önce ölç (aşağıda). Ölçümde μ ≥ 0,4 çıkarsa (beklenen) **(a) ön iki teker omni**. CAD hazır, bayrakla açılır:
`arayuz.TABAN['omni']['aktif'] = True` ya da `TABAN_OMNI=1`. Varsayılan geometri değişmedi.

**Omni CAD (bayrak açıkken, `taban_montaj.py` ile denendi):** 316 parça, taban 8.209,4 g (+680 g: 2 × (480 − 140)), robot 22,39 kg, AM z −7,8 (öne kayar).
Çakışma: taban içi 0, iskelet 0, kabuk 0, bağlantı 119/119. **Teker–etek boşluğu 10,55 mm (hedef 12):** omni 1 mm büyük ve göbek adaptörü ön yüzde. Kabuk ajanı için açık iş (etek ön bant 1,5 mm).
Omni aks yeri aynı olduğu için zeminde 1 mm aşağı çiziliyor; gerçekte ön 1 mm kalkar (0,15°, önemsiz). Göbek: 12 mm altıgen → omni flanşı adaptörü (tahmini; Nexus göbek delik düzeni satıcıdan teyit).
Ana montaj yükleyicisi (`montaj/moduller.py`) teker gruplarını "Teker 125 x 58 (…)" adıyla kuruyor; omni açılırsa "Omni teker 127 x 29 (…)" adı da eklenmeli (montaj klasörü bende değil).

**Yazılım kısıtı (her durumda, K1 (c)):**
- Standart tekerle: yerinde dönüş komutu en çok 90° ve ω ≤ 0,6 rad/s (≈ 2,6 s), ardından en az 3 kat dinlenme (ısıl yük). Yaw ivmesi ≤ 1 rad/s².
  Sürüş sırasında yön değişimi yay ile (R ≥ 1 m, k ≥ 0,5). Bu, yükü yalnız %10–15 azaltır; asıl çözüm omni.
- Akım izleme: ~~BTS7960 IS çıkışları (GPIO32/33) motor başına > 2,0 A ölçülürse 2 s sonra dönüşü kes~~ (μ 0,5'te yerinde dönüş akımı 2,0 A). **14.11: kural enkodere taşındı** (PWM > 0 iken sayım yoksa dönüşü kes; eşik ve süre ölçümden sonra): IS bölücüsüyle kart başına ≈ 4 A altı okunmaz, IS yalnız arıza bayrağı (`pin-haritasi.md` Y7, D7).
- Omni ile: dönme merkezi arka aks ortası. Odometri modeli arka aksta diferansiyel sürüş; ön enkoderler kayma tespiti içindir.

**Ölçüm (ekip, ~1 saat):** (1) Bir JGB37'yi laboratuvar kaynağında 12 V'ta mil kilitli tut, durma akımını oku; tork için 100 mm kol + el kantarı
(F × 0,1 m). (2) Robotu (ya da eşit yüklü tabanı) zeminde yanlamasına el kantarıyla çek: μ = F / (m g). Kullanılacak zeminlerin hepsinde (sınıf, koridor).
(3) Sonuçları `arayuz.TABAN['donus']`'a yaz, `taban_montaj.py` koş.

## E1: servo beslemesi

| Hat | Servolar | Bekleme | Jest anı | Yoğun (kol uzanmış tutuyor + hareket) | Gerçekçi tepe (≤ 100 ms) | Teorik (hepsi durma) |
|---|---|---|---|---|---|---|
| **A**: sağ kol + pan | S1, S2 (DS3218MG; 1,65 m'de DS3235, Y2b bölümü), dirsek, bilek, pan (MG996R) | 0,3 A | 2,8 A | **4,4 A** | 7,7 A | 12,7 A |
| **B**: sol kol + tilt | S1, S2, dirsek, bilek, tilt | 0,4 A | 2,9 A | **4,7 A** | 7,7 A | 12,7 A |

Servo başına varsayım (tahmini): jestte S1 0,8, S2 0,6, dirsek 0,6, bilek 0,4, pan 0,4, tilt 0,5 A; yoğunda 1,5 / 0,9 / 0,9 / 0,5 / 0,6 / 0,9 A;
kalkış anı 2,5 A (MG996R durma 2,5 A @6 V, DS3218MG 2,6 A @6,8 V; `06-aku-secimi.md`). Gerçekçi tepe = 2 servo kalkışta + diğerleri hareket.

- **Seçim: iki XL4016 (8 A modül, sürekli ≤ 5 A önerilir).** Biri yeni değil: K4 ile boşalan Pi XL4016'sı servo B oldu, XL sayısı 3 kalır. Hat başına yoğun yük 4,4 / 4,7 A, sınırın altında.
  Kafa servolarını iki hatta bölmek (pan A, tilt B) yükü dengeliyor. "Sağ kol + kafa / sol kol" bölüşümünde A 5,3 A olurdu.
- Teorik durma (12,7 A) XL4016'nın kendi akım sınırına çarpar: gerilim düşer, servo resetlenebilir, tehlikeli değil. Ölçümde hat sürekli > 5 A ise yedek: o hat için 20 A / 300 W düşürücü modül (fiyat doğrulanmadı).
- XL4016 girişleri: anahtarlı 12 V baradan (röle sonrası), her biri **7,5 A hat sigortası** ile (giriş tepe 7,7 A × 6 V / 0,88 / 12,8 V ≈ 4,1 A).
- XL → dağıtım kartı: **16 AWG** silikon çift (≈ 0,3 m; 0,6 m gidiş-dönüş 8 mΩ → 7,7 A'de 0,06 V).
- **Dağıtım kartı A / B** (ön kat ön bandı, (±72; 205); 70 × 50 pertinaks): 16 AWG klemens → V+ ve GND barası (kalın tel) → 2200 µF (mevcut 4 kondansatörden 2'şer) → 6 adet 3 pinli çıkış (servo uzatmaları).
  Sinyal: PCA9685 kanalından kısa 3 pinli köprüyle kartın sinyal girişine. Bu köprünün V+ ucu kartta bağlı değil. **PCA9685 V+ klemensi boş kalır.**
- Uzatma: servo başına 22 AWG, ~1,3 m. Durma akımında 2,6 m × 0,052 Ω/m × 2,5 A ≈ 0,34 V düşüm (servo 5,66 V görür); kabul. Daha az düşüm istenirse dağıtım traverse seviyesine taşınabilir (iskelet/kabuk işi, açık).

## E2: gerilim seviyeleri

| Sinyal | Çözüm | Değer |
|---|---|---|
| HC-SR04 echo ×3 (5 V) | Bölücü (arayüz kartında): seri 4,7 kΩ, toprağa 10 kΩ | 5 × 10/14,7 = 3,40 V (ESP32 ≤ 3,6 V). Trig 3,3 V yeterli (PCA9685 kanalından, aşağıda). HC-SR04P yalnız yeni alımda: 3,3 V beslenirse echo 3,3 V |
| Akü gerilimi | 100 kΩ / 18 kΩ + 100 nF, ana anahtar sonrası (kapalıyken akım çekmez) | 14,6 V → 2,23 V, 10,0 V → 1,53 V (ESP32 ADC 11 dB doğrusal bölge ≤ 2,45 V). Akım 0,12 mA. Bir kez multimetreyle kalibre et |
| Acil stop durumu | PC817 2 kanal modülü ([Direnc.net, 43,59 TL](https://www.direnc.net/pc817-2-kanal-optokuplor-izolasyon-icin-modul); giriş 3,6–24 V). Kanal 1 mantar NC sonrasındaki düğüm | LOW = mantar serbest, HIGH = basılı ya da F5 attı. **Modülün çıkış tarafı 3,6–30 V için verilmiş, ESP32 3,3 V bunun altında:** montajda 3,3 V'ta çıkışın tam LOW/HIGH verdiği multimetreyle ölçülecek (aşağıdaki not) |
| Anahtarlı 12 V durumu | PC817 kanal 2, röle sonrası bara | LOW = motor/servo gücü var |
| PCA9685 mantık | VCC ← ESP32 3V3 (I2C pull-up'lar 3,3 V'a); OE → GND | Servo gücü V+'tan değil, dağıtım kartından |
| BNO055 | VIN ← 3V3 | Adafruit kartı 3–5 V kabul eder |
| JGB37 enkoder | VCC ← 3V3 (Hall çıkışı 3,3 V) | 5 V gerekirse çıkışa 4,7k/10k bölücü (ölç) |

**PC817 modülü 3,3 V'ta (K3 notu):** modülün giriş tarafı 3,6–24 V (12 V için uygun), ama çıkış tarafı da satıcı sayfasında "3,6–30 V" ve jumper'la yüksek/düşük seçiliyor; ESP32 tarafı 3,3 V nominalin altında.
Montajda: çıkışı açık kolektör gibi kullan (modülün çıkış besleme ucu 3V3'e ya da boş, sinyal ESP32 GPIO'suna dahili pull-up ile), girişe 12 V verip kesip multimetreyle 3,3 V tarafında LOW < 0,4 V ve HIGH > 2,5 V gör.
Olmazsa **alternatif (önerilen yedek, ~10 TL):** arayüz kartına doğrudan iki PC817 (DIP-4): giriş LED'ine seri 2,2 kΩ (12,8 V'ta (12,8 − 1,2) / 2,2 k ≈ 5,3 mA, 14,6 V'ta 6,1 mA, 0,08 W; 1/4 W yeter),
LED'e ters paralel 1N4148 (ters gerilim koruması), çıkış kolektörü → GPIO23 / GPIO5 + 10 kΩ pull-up 3V3'e, emetör GND. PC817 CTR ≥ %50 (5 mA'de ≥ 2,5 mA) → 3,3 V / 10 kΩ = 0,33 mA'i rahat doyurur. Mantık aynı: LED yanık = çıkış LOW.

## E3: acil stop ve yeniden başlatma

```
F5 2 A ─── mantar NC ───┬─── röle K1 bobini (+) ── bobin (−) ── BC337-40 kollektör   (bobine ters paralel 1N4007)
                        │                                       BC337-40 emitör ── GND
                        └── PC817 #1 giriş (12 V algı)          BC337-40 taban ── 270 Ω ── GPIO4 ;  taban ── 2,2 kΩ ── GND
K1 kontağı (40 A): F1 20 A ──> anahtarlı 12 V bara ──> BTS7960 sol/sağ, XL4016 A, XL4016 B  (PC817 #2 bu barayı okur)
```

- Röle yalnız **mantar serbest ve ESP32 "devreye al" (GPIO4 = 1)** iken çeker. Mantar bırakılınca hiçbir şey olmaz; güç ancak operatör komutuyla gelir (Pi komutu: telefon kumandası; Nextion "Devreye al" düğmesi Y2b ile kalktı).
- Yazılım kuralı (ESP32): PC817 #1 HIGH görünce GPIO4'ü hemen 0 yap ve kilitle. Yeniden devreye almadan önce:
  (1) mantar serbest, (2) PCA9685 çıkışları servoların **son bilinen konumuna** yazılmış, (3) BTS EN = 0 ve PWM = 0, (4) açık komut. Sonra GPIO4 = 1.
  PC817 #2 500 ms içinde LOW olmazsa hata ver.
- Açılışta güvenli: GPIO4 strapping değil; reset sırasında ve sonrasında çıkışı kapalı, dahili zayıf pull-down'ı açık (Espressif IO_MUX); Arduino-ESP32 2.0.17'de hiçbir açılış işi ya da varsayılan çevre birimi onu sürmez; 3.x'te `Serial2` RX varsayılanıdır (sürmez, pull-up açar: Serial1 / Serial2 varsayılan pinlerle açılmaz, `pin-haritasi.md` §2, §3.1, Y1). Röleyi kapalı tutan asıl şey tabandaki 2,2 kΩ pull-down'dır (14.11'e dek 10 kΩ, sonra 4,7 kΩ, 14.11 düzeltmesiyle 2,2 kΩ; sürücü 14.11 `pin-haritasi.md` sürüm 4'ten beri BC337-40, D1, D9). ESP32 kilitlenirse görev izleyicisi (watchdog) resetler; reset anında çıkış kapanır, pull-down LOW'a çeker → röle bırakır. (14.11'e dek K1 GPIO12'deydi; GPIO16 ara kararı Arduino'nun PSRAM yoklaması yüzünden geri alındı: `pin-haritasi.md` §3.1.)
- Kalan risk: yazılım hatası pini 1'de bırakıp mantar bırakılırsa röle yeniden çeker. Donanımla kapatılacaksa: röle kontağına paralel ikinci (kendini tutma) kontak + ayrı başlat butonu (iki kontaklı röle gerekir). Şimdilik yazılım kuralı + watchdog.
- **Pi seri portu DTR/RTS (K3 E-2, yazılım planına satır):** DevKit'teki otomatik reset devresi (CP2102 DTR/RTS → EN/GPIO0) ESP32'yi Pi seri portu açıp kapatırken resetleyebilir.
  Reset → GPIO4 LOW (pull-down) → röle bırakır → servo ve motor gücü kesilir, **kollar düşer**. Pi tarafı portu DTR/RTS değiştirmeden açmalı: pyserial'de port açılmadan önce
  `ser.dtr = False; ser.rts = False` ayarlanıp sonra `ser.open()`, Linux'ta ayrıca `stty -F /dev/ttyUSB0 -hupcl` (kapanışta DTR düşmesin). İlk bağlantı testinde
  ESP32'nin boot mesajı basmadığı (resetlenmediği) görülmeli. Yazılım yine de "ESP32 resetlendi" durumunu ele almalı: reset sonrası röle kapalı açılır, yeniden devreye alma E3 kuralıyla. **Bilinçli reset (14.11, pano #7 öneri 5):** yeni Pi GPIO → EN teli yok; Pi aynı DTR / RTS devresiyle bilerek bir reset dizisi uygular (devre kartta zaten var; boyun demeti büyümez). Efe'ye soruldu (taslak); `kablolama-on-kararlar.md` §7. **Boyun demeti bağlanmadan önce** Efe'nin iki cevabı beklenir: bilinçli reset DTR / RTS ile yapılabiliyor mu, otomatik reset donanımda kapatılacak mı; "tel gerekir" derse bükümlü çift eklenir (≈ +2 mm², servo kanalı %44,8 → ≈ %46). Port açılırken Linux DTR ve RTS'yi etkin yapar; pyserial önce DTR'yi sonra RTS'yi bırakır, arada DTR bırakık / RTS etkin bir an EN'i LOW çeker: kapalı açma ayarına rağmen reset olabilir (KT6).
- **Ön şarj (E9) önemi arttı (K3):** E3 ile röle her "devreye al"da yeniden çeker. Her seferinde anahtarlı bara üstündeki kondansatörler (XL4016 / BTS giriş kondansatörleri; XL çıkışındaki
  4 × 2200 µF servo kondansatörü de XL üzerinden) boş halden dolar. Victron BMS yüksek kapasitif yükte kesebilir, ~10 s sonra yeniden dener (`06-aku-secimi.md` satır 61, 164).
  Önceden yalnız açılışta olan darbe artık her acil stop sonrasında olur. E9 (5. adım): röle kontağına paralel 10 Ω / 5 W ön şarj direnci + gecikmeli çekme ya da ≥ 30 A NTC; değer için bara kapasitesi ölçülecek.
- Röle sürücüsü (14.11, `pin-haritasi.md` sürüm 4 + 14.11 düzeltme, §6 D1 / D9): **BC337-40** (TO-92, delikli; -40 sınıfı zorunlu, ayak sırası teslimde diyot testiyle, T2a), taban 270 Ω seri + **2,2 kΩ** taban → GND, bobine ters 1N4007; GPIO 4 / 19 sürüş gücü varsayılanda (2) kalır. Bobin (üretici tabloları MAH3 / JQC-3FF): K1 85 Ω ±%10 → en kötü 0,19–0,21 A; K2 400 Ω ±%10 → ≈ 0,04 A. En kötü taban akımı 4,79 mA → zorunlu β K1 40–44, K2 ≈ 9. hFE en az 250 @ 100 mA; 300 mA'de üreticiye göre 60 (onsemi; satın alınacak BC337-40TA adı) – 170 (Diotec): belgeyle garanti pay ≈ 1,37× (VCE 1 V'ta). VCE ≤ 0,3 V'u hiçbir üretici garanti etmez, belgeyle sınır 1,0 V: K1 bobini besleme 11 V'ta ≥ 10,0 V, 10 V'ta ≥ 9,0 V görür (çekme garantisi ≤ 8,4 V, 23 °C); doyum T2 (g)'de VCE ölçülerek kabul edilir. Kayıp en kötü ≈ 0,22 W, 60 °C ortamda Tj ≈ 103 °C (izin 0,45 W). Sıcak bobinde çekme gerilimi artar (≈ 9,6 V @ 60 °C, ≈ 10,3 V @ 80 °C, hesap): uzun çalışmadan hemen sonra düşük aküyle devreye almada K1 çekmeyebilir; arıza güvenli yönde, Y4 hata yolu yakalar (`pin-haritasi.md` T2). Kapalı hâl: boşta taban ≤ 0,25 V, 70 °C'de bobin ≤ 0,3 mV, bırakma sınırı 1,2 V. Listedeki VBsemi IRLZ44NPBF-VB çıkar (sürüm 3'ün mantık seviyeli MOSFET şartı kalktı).
- F5 2 A: bobin 0,15 A + PC817 ~5 mA. Önceki 5 A bu devre için büyüktü, 5 A artık F3/F4'te.

## E4: Pi 5 beslemesi (K4: Pi kafada)

Tarih notu 04.11.2026: düşürücü, bütçe, ekran beslemesi ve boyun demeti 1,58 m'e göre yeniden yazıldı (eski değerler üstteki tabloda).

- **Boyundan (09.11, 05.11 B + R1):** 12 V çift (18 AWG, F3 5 A) + tilt servo (3 tel) + göğüs ekranı HDMI (757 / 950 mm) + hub uzatması (USB, Pi port 3 → gövdedeki hub; 617 / 920 mm) + hoparlör kablosu (PAM8403 → gövde orta bandı; 824 / 1.030 mm). ESP32 USB ve göğüs USB dokunmatik hub'dan çıkar, boyundan geçmez. CSI kafada kalır. Boylar yol / önerilen (`lale158-kontrol.json` `kablo_ozet.kablo`); düzen **K14 a (14.11)**: Efe'nin tarafı yazılım açısından kabul (pano #6 #21); HDMI ince / esnek, Ø ≤ 6; masa denemesi ve büküm kablajda teyit. 14.11 kararlarıyla demete tel eklenmedi.
- **Kafada Pi düşürücüsü:** Pololu **D24V50F5** (Robotistan): giriş en çok 38 V, çıkış 5 V ±%4, 5 A sürekli, 17,8 × 20,3 × 8,8 mm; ters gerilim, aşırı akım, kısa devre, aşırı sıcaklık koruması, yumuşak başlatma, düşük gerilim kilitleme (`raporlar/kaynaklar/07-gogus-ekrani-ve-5v.md`). 12 V girişteki sürekli akım üretici eğrisinden teyit edilecek (açık iş 8).
- **Kafada ekran düşürücüsü:** SY8205 (Motorobit): giriş 7–30 V, sürekli 3,7 A, sayfada koruma yazmıyor; çıkışında P6KE6V8A var. Pi hattından ayrı (üstteki mimari).
- **Kafa 5 V bütçesi:** normal karşılama toplam **3,57 A**, ekran ayrı düşürücüde **Pi hattı 2,67 A**, QLED **0,9 A varsayım**. Hesap, ölçülmedi; tepe değer yeni düzende hesaplanmadı.
- **Bağlantı:** D24V50F5 VOUT → kısa USB-C erkek ucu (20 AWG, ~10 cm; v4: USB Type-C 24 pin test kartı, kablo lehimlenir) → Pi USB-C. PD yok, bu yüzden:
  - EEPROM'a `PSU_MAX_CURRENT=5000` (`sudo rpi-eeprom-config --edit`): firmware PD pazarlığını atlar, 5 A kaynak varsayar ([raspberrypi.com](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html), bootloader yapılandırması).
  - `config.txt`: `usb_max_current_enable=1` (aynı belge; USB-A çıkış sınırını kaldırır). Önceden LCD beslemesi içindi; kafa ekranı artık Pi'den beslenmiyor, hub ve USB cihazları için tutuldu. Gereği montajda ölçümle görülür.
- **TVS:** her iki 5 V çıkışına P6KE6V8A (6,45–7,14 V kırılma), kafa girişinde 12 V'a P6KE18A (15,3 V tutma; LiFePO4 şarjda 14,6 V). Delikli gövde, klemense lehimlenir.
- **ESP32 çift besleme (diyotlu VEYA, iki kaynak):** asıl kaynak çevre 5 V → VIN. Pi'ye giden USB kablosunun VBUS teline seri **1N5819** (anot Pi tarafında). VBUS kesilmez:
  CP2102'nin VBUS pini bağlantı algısıdır, kesilirse kart USB'de görünmeyebilir. Diyot sayesinde çevre 5 V Pi'ye geri beslemez; çevre 5 V düşerse ESP32 Pi'den ~4,4–4,7 V alır (zararsız, ESP32 çalışır).
  Kartın kendi VBUS→VIN diyodu doğrulanırsa (DOIT DevKit V1 şemasında var) bu diyot gerekmez. Montajda multimetreyle bakılacak.

## K4: kafa CAD özeti (125 cm kafası, 15 Ekim; güncel sayılar `kafa-analiz.json`, 10,1" QLED modeli bekleniyor)

| | Önce | Sonra |
|---|---|---|
| Parça / kütle | 98 / 1.363,1 g | 115 / 1.431,3 g (+68,2: Pi + soğutucu 58, 4 burç + 8 vida ~3, çevirici 7, amfi 2, köpük); T2 yarık + perde sonrası **1.443,5 g** |
| Tilt grubu (kablo payı 25 g dahil) | 833,4 g, 4,46 kg·cm, **pay 2,11** | 926,6 g, 4,64 kg·cm (yerçekimi 2,62 @30° + ivme 2,02), **pay 2,03** (P tahmini 1,96); T2 sonrası 938,8 g, 4,67 kg·cm, **pay 2,01** |
| Pan | 2,6 kg·cm, pay 3,6 | 2,64 kg·cm, pay 3,6; üst rulman eksenel 10,1 → 11,0 N |
| Tilt mili yük paylaşımı | horn 4,07 N / pim 4,11 N | 4,55 / 4,54 N (açık iş: tilt servosuna ikinci rulman) |
| Hareket aralığı | tilt −25…40 serbest, pan ±180 | aynı (çarpan poz kümesi birebir aynı) |

- Yer: Pi kartı köşesi (x −34, z +1), kart altı y 191 (4 × M2,5×8 pirinç burç; alttan M2,5×8 tabladan, üstten M2,5×5; tabla delikleri Ø2,9).
  Pi ↔ kafa iskeleti 6,6 mm, ↔ arka kabuk 7,5 mm; tilt taramasında (−25…30°) Pan/Gövde grubuna en az 31,6 mm. Soğutucu üstü y 208,5, tavana 64 mm.
- [ESKİ, 125 cm kafası] Çevirici (−75; 44) ve amfi (65; 44; o günkü I2S amfi MAX98357A) tablada 1 mm köpük bant + kablo bağıyla. Çevirici ↔ kablo geçişi ~25 mm, amfi ↔ LCD HDMI bloğu 11,6 mm. 1,58 m'de I2S amfi modelde yok; PAM8403 ve USB ses kartı kafa sol duvarında (`KY/uygulama-notu.md:45, 56-57`).
- Kamera FPC **300 mm** (Pi 5 22 pin 0,5 mm → 15 pin 1 mm); kafa ekranına 30 cm şerit HDMI; kısa USB-C güç ucu. Kafa içi kablolar referans (kütleye 25 g nokta yük olarak tork hesabında).
- **Havalandırma (güncel kabuk, `kafa-analiz.json`):** arka kabuk yarıkları giriş 630 mm², çıkış 840 mm², yükseklik farkı 50 mm. Yerleşim 10,1" QLED modelinde yeniden bakılacak.
- **Isı (el hesabı, 30 °C ortam, R 0,992 K/W; `kafa-analiz.json` `isi`):** 7" kafada boşta / tipik / en kötü 7,2 / 11,4 / 14,5 W → kapalı 37,1 / 41,3 / 44,4 °C. 10,1" QLED ile normal karşılamada **~49 °C** (servo sınırı 55 °C), ölçülecek. Önceki 125 cm değerleri (39 / 45 / 49 °C, "yarıklı 34–42 °C") 04.11'de kaldırıldı.
  Test şartı (değişmedi): kafa kapalı, stres (stress-ng + animasyon), SoC ≤ 75 °C, tilt servosu gövdesi ≤ 50 °C. Yazılım SoC > 75 °C'de animasyon FPS düşürür. Aşılırsa üst bant arkasına 25–30 mm egzoz fanı.
- **Servis (125 cm kafası; yeni kabukta doğrulanmadı):** microSD −X'e bakar (x −49…−34, z −17…−37). Arka kabuk 2 vidayla (x ±105, z −30) sökülünce SD, USB-A ve Ethernet erişilir. Ön kabuk ve LCD yerinde kalır.
- **Kablo listesi (boyun; `lale158/kablo_yolu_ekran.py`, 05.11 B + R1):** 12 V çift 18 AWG + tilt servo + göğüs HDMI (Ø6) + hub uzatması (Ø4) + hoparlör (Ø4) ≈ 69,9 mm² (kablo çapları tahmini; `kablo_yolu_ekran.py:31, 197`). Dar kesitler: mil arka penceresi 20 × 10 (175 mm², %39,9), servo yuvası arka kanalı 20 × 7,8 (156 mm², %44,8), alt çıkış 20 × 12 (204 mm², %34,3) (`lale158-kontrol.json` `kablo_ozet.boyun_demet_alan_mm2`, `gecis`). Düzen **K14 a (14.11)**. Hoparlör yeri kapandı: gövde orta bandı sağ duvarı (`KY/uygulama-notu.md:59`).
- **Tabanda boşalan Pi yeri** (−90,5; 80): E2/E3 arayüz kartı (70 × 50 pertinaks: bölücüler, PC817, röle sürücüsü BC337-40 × 2 (D9) + 1N4007, klemens).

## E7: etek içi ısı

- **Isı kaynakları (Pi gittikten sonra; tahmini):** XL4016 A/B (hat başına yoğun 4,5 A × 6 V = 27 W çıkış → kayıp 3,7 W), XL4016 çevre (6 W → 0,8 W), BTS7960 ×2 (dönüşte ~0,3 W),
  röle bobini 1,8 W, ESP32 + kartlar ~1 W. Tipik ~8 W, yoğun ~11,5 W. Önceki düzende bunlara Pi (7–10 W) ve onun XL'i (~1 W) ekleniyordu: etek ısısı yaklaşık yarıya indi.
- **Isı yolu:** XL4016 modülünde ısı, IC'nin ve diyodun vidalı olduğu **üstteki** alüminyum soğutucuda. Kart altı ile alt plaka arasına ped koymak ısı kaynağına değmez. 8 mm naylon burç kalıyor (kısa devre koruması), ped/plaka önerilmiyor.
  Isıyı soğutucu üstündeki hava taşır.
- **Fan (ölçüme bağlı):** 40 × 40 × 10 12 V fan, üç XL4016'nın ortasında kat altına asılı, aşağı üfler. Yer `arayuz.BOLGELER` "E7 fan yeri" (x ±25, y 162,5–174,5, z 85–135) olarak ayrıldı; iskelet/kabukla ihlal 0.
  Sıcak hava etek üst açıklığından gövdeye ve etek altından çıkar. Etek arka bandında havalandırma yarıkları: **kabuk için açık iş** (kabuk benim dosyam değil).
- **Ölçüm planı:** 3 XL4016 soğutucusuna, bir BTS7960'a, etek içi havaya (orta) ve akü yüzeyine NTC/termokupl (multimetre ya da ESP32).
  Kabuk kapalı, 25–30 °C ortam, 30 dk "yoğun" profil: servo hatlarına 1,33 Ω / 30 W yük direnci (6 V'ta 4,5 A) ya da kollar uzanmış tutarken. Ardından 5 dk yerinde dönüş/sürüş döngüsü.
  **Ölçüt:** XL4016 soğutucusu ≤ 80 °C, etek havası ≤ 45 °C, akü yüzeyi ≤ 45 °C. Aşılırsa fan + etek yarıkları; yine aşılırsa servo hattı 20 A modüle.

## Blok şema (metin)

```
Akü Victron SuperPack 12,8 V 20 Ah (BMS 30 A sürekli) ── XT60 ── Ana sigorta 30 A ── ASW-A01 ana anahtar ── sigorta kutusu (6 yol)
  │                                                                                   │
  └─ (anahtar sonrası) akü ADC bölücü 100k/18k ── ESP32 GPIO36                         ├─ F1 20 A ── röle K1 kontağı ── anahtarlı 12 V bara (WAGO)
                                                                                      │        ├─ BTS7960 sol ── ön sol + arka sol JGB37 (paralel)
                                                                                      │        ├─ BTS7960 sağ ── ön sağ + arka sağ JGB37 (paralel)
                                                                                      │        ├─ 7,5 A ── XL4016 A 6 V ── 16 AWG ── dağıtım A ── sağ kol (4)   [29.10: pan C'ye]
                                                                                      │        ├─ 7,5 A ── XL4016 B 6 V ── 16 AWG ── dağıtım B ── sol kol (4)   [29.10: tilt C'ye]
                                                                                      │        ├─ 5 A ──── XL4016 C 6 V ── 16 AWG ── klemens ── kafa pan + tilt   [29.10, yeni]
                                                                                      │        └─ PC817 #2 (bara durumu) ── ESP32 GPIO5
                                                                                      ├─ F2 15 A ── yedek
                                                                                      ├─ F3 5 A ── 18 AWG çift, direk ön yüzü, boyun ── KAFA: P6KE18A ─┬─ D24V50F5 5 V ── P6KE6V8A
                                                                                      │                                                                │  ├─ USB-C ── Raspberry Pi 5 ── USB: 1 ReSpeaker v2.0 (3,5 mm ── PAM8403 (5 V: D24V50F5, K10 a, masa denemesine bağlı) ── hoparlör (gövde)), 2 boş, 3 hub (gövde: göğüs Touch, ESP32, 2 boş), 4 kafa ekranı Touch
                                                                                      │                                                                │  └─ micro HDMI 0: kafa ekranı ; micro HDMI 1: göğüs ekranı (K14 a) ; CSI: Camera Module 3 (FPC 300 mm)
                                                                                      │                                                                └─ SY8205 5 V ── P6KE6V8A ── micro USB Power: 10,1" QLED (Touch'tan 5 V köprülenmez)
                                                                                      ├─ F6 3 A ── LM2577 + LM2596 12 V ── 11,6" göğüs ekranı 12 V [K11 a: kutunun 6. yuvası, röle öncesi, acil stopta açık]
                                                                                      ├─ F4 5 A ── XL4016 çevre 5 V ── ESP32 VIN, sonar ×3, enkoder (3V3 ESP32'den), PCA9685/BNO055 mantık (3V3)
                                                                                      └─ F5 2 A ── mantar NC ── röle K1 bobini ── BC337-40 ── GND   (PC817 #1 mantar sonrası)
Veri: Pi (kafa) ── USB ≈ 1,57 m (VBUS'ta 1N5819) ── ESP32 (taban) ── I2C: PCA9685 (10 servo + 3 sonar trig), BNO055 ; PWM/EN/IS: BTS ×2 ; enkoder ×2 (A/B)
Toprak: akü − ── WAGO yıldız noktası (güç paneli) ── tüm dönüştürücüler; kafa GND 12 V dönüşüyle
```

## Akım bütçesi (anlık, akü tarafı 12,8 V; dönüştürücü verimi XL 0,88, Pololu 0,90, BTS 0,95)

| Yük | Hat | Tipik | Yoğun | Tepe |
|---|---|---|---|---|
| Kafa (Pi + 10,1" QLED + kamera + amfi + mikrofon; 04.11) | F3 | ≈ 1,55 A (normal karşılama, 3,57 A @5 V; hesap) | hesaplanmadı | hesaplanmadı (yalnız Pi hattı: Pi tam yük + PAM ≈ 3,61 A @5 V, AI HAT+ ile ≈ 4,1–4,5 A; K10 a masa denemesine bağlı, "Kafa güç mimarisi") |
| Göğüs ekranı (04.11) | F6 3 A | ~0,5 A @12 V (ekran; regülatör kaybı dahil değil) | hesaplanmadı | hesaplanmadı |
| Servo A | F1 → 7,5 A | 1,5 A (jest 2,8 A × 6 V) | 2,3 A (4,4 A) | 4,1 A (7,7 A) |
| Servo B | F1 → 7,5 A | 1,5 A | 2,5 A (4,7 A) | 4,1 A |
| Motorlar ×4 (BTS) | F1 | 0,9 A (düz, sabit hız) | **8,0 A (yerinde dönüş μ 0,5: 4 × 2,0)** | 11,2 A (4 × durma) |
| Çevre 5 V (ESP32 0,24 + sensör/enkoder/opto ~0,15; Nextion 0,8 A Y2b ile çıktı) | F4 | 0,4 A [ESKİ, Nextion dahil] | 0,5 A | 0,6 A |
| Röle bobini + PC817 | F5 | 0,15 A | 0,15 A | 0,15 A |
| **Toplam** [ESKİ, 15 Ekim: kafa 0,89 / 1,13 / 1,62 A ile, göğüs ekranı yok; 04.11 satırlarıyla yeniden toplanmadı] | | **5,3 A** | **14,6 A** | **21,8 A** (teorik) |

- F1 yükü: yoğun 12,8 A, teorik 19,4 A (≤ 20 A). Ana 30 A ve Victron BMS 30 A sürekli içinde. Omni ile yerinde dönüşte motorlar 4 × 0,45 A, yoğun toplam ≈ 8,4 A.
- Zaman ortalaması ve akü süresi: `taban-analiz.json` `aku` (hat verimleri güncellendi; röle bobini hesapta 0,3 W, gerçekte ~1,8 W: E8, 5. adım).

## Sigorta listesi

| Yer | Değer | Besler | Not |
|---|---|---|---|
| Ana | 30 A | akü + → her şey | XT60 sonrası kablolu yuva (mevcut) |
| F1 | 20 A | röle K1 (ve paralel ön şarj kolu K2 + 5,6 Ω, E9) → anahtarlı 12 V bara | motorlar + iki servo hattı. Ön şarj kolu da F1'den sonra, ayrı sigorta yok |
| F2 | 15 A | yedek | |
| F3 | **5 A** (önce 10 A Pi) | kafa 12 V (18 AWG): D24V50F5 + SY8205 | normal ≈ 1,55 A (04.11, hesap); tepe hesaplanmadı |
| F4 | 5 A | XL4016 çevre 5 V | **ikinci 5 A** (E9): sette tek 5 A var, F3 onu alır |
| F5 | **2 A** (önce 5 A) | acil stop / röle K1 + K2 bobinleri | sette yok: yeni. K1 0,15 A + K2 ~0,03 A + PC817 |
| Hat | 7,5 A × 2 + 5 A | XL4016 A ve B girişi; C (kafa servoları, 29.10) | kapaklı mini bıçak sigorta yuvası × 3 (yeni) |
| F6 | **3 A** standart bıçak (14.11; önce hat yuvasında mini 2 A) | LM2577 + LM2596 → 11,6" göğüs ekranı | kutunun 6. yuvası, ana anahtar sonrası, röle öncesi (K11 a). Ekran en çok 1 A @12 V → girişte 10 V'ta ≈ 1,5 A (%50) |
| Şarj | 10 A (mini) | XT60 şarj girişi → akü + (ana anahtar öncesi) | E9 / akü raporu önerisi; dördüncü kapaklı yuva (yeni). Şarj cihazı 6 A |

**Sigorta seti (E9, 5. adım):** kutudaki set 5, 10, 2 × 15, 2 × 20 (standart/ATO bıçak). F3 ve F4 iki 5 A ister, bir tane var:
**ikinci 5 A** ve F5 için **2 A** standart bıçak eklenir. Hat yuvaları mini bıçak: 7,5 A × 2 (XL4016 A / B) + 5 A (XL4016 C, kafa
servoları; karar 29.10) + şarj girişi 10 A. Maliyette tek satır "Bıçak sigorta (ek)" (6 adet; standart/mini ayrımı modelde), yuvalar
"Hat sigortası yuvası" × 4 (v4'te × 5; 14.11'de göğüs ekranı kutunun F6 yuvasına geçti), ayrıca standart 3 A (F6). Setteki 10 A ve bir 15 A yedek kalır.
**H1 erişimi (karar 29.10, Ahmet):** etek servis kapağı H1 açıklığı değişmez (x ±32, 64 × 50; `arayuz.M6 etek_kapak_h1`). 6 yollu sigorta
kutusu alınınca ölçülür; kutu 1 × 6 dizilişliyse uçtaki iki yuva kapak altında kalır, bu iki yuva **yedek sigorta** için ayrılır
(F2 15 A yedek ve boş / yedek yuva; 14.11: boş yuva F6 3 A göğüs ekranı oldu, nadiren değişir; `kablolama-on-kararlar.md` §3). **Kutu girişi (14.11, KT3):** yuvalar ortak baralı mı teslimde bakılır; ayrı girişliyse giriş köprüleri **12 AWG**, kutunun üstünde olabildiğince kısa, tek giriş klemensinden yıldız (F1–F6 hepsi). Sık değişebilecek F1, F3, F4, F5 ortadaki dört yuvaya; 2 × 3 dizilişte altısı da açıkta.

## E8: akü süreleri (5. adım, akü raporuyla hizalı)

**Tarih notu 04.11.2026:** bu bölüm 125 cm yükleriyle (7" LCD, Nextion) hesaplandı; yöntem geçerli, sayılar güncel değil. 1,58 m kaba tahmini üstteki tabloda (normal ~3,8–4,4 sa, ölçülmedi); `Y2b-aku.py` yeni yüklerle yeniden koşulmadı.

Yöntem akü raporununki (`raporlar/aku-secimi/rapor.html`, `06-aku-secimi.md`): kullanılabilir = nominal × 0,90 (DoD) × 0,90 (yaşlanma,
soğuk, BMS) = **× 0,81**; süre = Wh × 0,81 ÷ akü tarafı W. Akü **Victron SuperPack 12,8/20 = 256 Wh** (K3). Hesap betiği
`planlama/adim5/e8_aku.py` → `e8-aku.json`. Yük değerleri tahmini (yalnız Nextion akımı datasheet'ten).

3. adımın yeni tüketicileri dahil: Pi kafada **Pololu düşürücü üzerinden (verim 0,90)**, röle bobini **0,15 A × 12,8 V = 1,9 W** (önce 0,3 / 1,5 W),
XL4016 boşta 0,4 W, PC817 girişleri ~0,13 W, servo bekleme akımı E1 tablosundan (0,7 A × 6 V = 4,2 W). Fan (E7, koşullu) ayrı satırda.

| Yük (yük tarafı, W) | Hat (verim) | Boşta | Normal | Yoğun |
|---|---|---|---|---|
| Pi 5 + Active Cooler | kafa (0,90) | 4,0 | 6,5 | 12,0 (tam yük) |
| 7" yüz LCD [ESKİ] | kafa (0,90) | 1,7 | 2,45 | 2,5 |
| Kamera 0,7 + mikrofon 0,5 + amfi | kafa (0,90) | 1,2 | 1,7 | 2,7 |
| Nextion 10,1" [ESKİ, kalktı] | 5 V (0,88) | 2,5 | 3,5 | 4,0 |
| ESP32 + sensör + mantık | 5 V (0,88) | 0,8 | 1,0 | 1,3 |
| Servolar A + B | 6 V (0,88) | 4,2 (bekleme) | 10,2 (%20 jest) | **34,2** (sürekli jest, E1 5,7 A × 6 V) |
| Tahrik 4 × JGB37 | 12 V (0,95) | 0,3 | 5,0 | **36,1** (%40 düz, %20 ivme, %25 rampa, %15 yerinde dönüş 2,0 A/motor) |
| Sabit: röle 1,9 + XL boşta 0,4 + PC817 0,1 | akü | 2,5 | 2,5 | 2,5 |
| **Akü tarafı** | | **19,0 W (1,5 A)** | **36,3 W (2,8 A)** | **104,4 W (8,2 A)** |

| Senaryo | Akü W | Victron 256 Wh | 24 Ah (307 Wh) | 30 Ah (384 Wh) |
|---|---|---|---|---|
| Boşta (sunum bekleme) | 19,0 | 10,9 sa | 13,1 sa | 16,4 sa |
| Normal etkileşim | 36,3 | 5,7 sa | 6,9 sa | 8,6 sa |
| **Yoğun** | **104,4** | **2,0 sa** | 2,4 sa | 3,0 sa |
| Yoğun, ön tekerler omni | 91,9 | 2,3 sa | 2,7 sa | 3,4 sa |
| Ders karışımı (%40 / %50 / %10) | 36,2 | 5,7 sa | 6,9 sa | 8,6 sa |
| Fuar karışımı (%35 / %50 / %15) | 40,5 | 5,1 sa | 6,1 sa | 7,7 sa |
| + E7 fanı (1,2 W, koşullu) | | yoğun 1,96 sa, normal 5,5 sa | | |

- **Yoğun senaryo düzeltme planındaki şartı karşılıyor (≥ 100 W).** Planın "≈ 2,5 sa" değeri 307 Wh (24 Ah) içindi; bu hesapta 24 Ah ile 2,4 sa.
  Seçilen Victron ile **≈ 2,0 sa**.
- **3 saatlik ders:** 134 Wh nominal gerekir (10,5 Ah). Victron 5,7 sa ile rahat.
- **8 saatlik fuar:** 400 Wh nominal gerekir (31 Ah). Victron 5,1 sa ile yetmez: öğle şarjı (6 A ile ≈ 3,5 sa) ya da ikinci akü. Akü raporunun
  sonucuyla aynı.
- Akü raporuyla fark: boşta 14,6 → 19,0 W (servo bekleme 1,5 → 4,2 W, röle 1,5 → 1,9 W, Pololu kaybı), normal 31 → 36 W, yoğun 73 → 104 W
  (yoğun tanımı sürekli jest + yerinde dönüş payı ile ağırlaştırıldı). OZET / `taban-analiz.json` `aku` hâlâ 307 Wh × 0,80 ve röle 0,3 W ile
  hesaplı (10,9 / 32,6 / 80,7 W): **CAD tarafında açık iş** (`tasarim/freecad` bu adımda değişmedi; 6. adımda taban yeniden üretilirken 256 Wh,
  × 0,81 ve bu tablo alınmalı).
- En büyük belirsizlik: servo bekleme ve jest akımı (E1 tahmini) ve yerinde dönüş akımı (K1 ölçümü). Ölçümden sonra `e8_aku.py` yeniden koşulur.

## E9: ön şarj (5. adım kararı)

**Sorun:** E3 ile röle K1 her "devreye al"da çeker. Anahtarlı bara üstündeki boş kondansatörler aküye doğrudan bağlanır: XL4016 A/B ve
BTS7960 ×2 modül giriş elektrolitleri (tahmini 4 × ~470 µF ≈ **2 mF**, ölçülecek) ve XL çıkışındaki 4 × 2200 µF servo kondansatörü (XL üzerinden).
Kablo + kontak ≈ 30 mΩ ile tepe ≈ 13,3 V / 0,03 Ω ≈ 440 A, ~60 µs (tahmini). Victron datasheet dipnotu: yüksek giriş kapasitesinde akü
kesebilir, ~10 sn sonra yeniden dener (`06-aku-secimi.md`). Önceden yalnız açılışta olan bu darbe artık her acil stop sonrasında olur.

| Seçenek | Sonuç |
|---|---|
| Röle kontağına **kalıcı** paralel direnç | **Red.** K1 açıkken (acil stopta) bara direnç üzerinden beslenir: XL4016'lar servolara zayıf güç verir, acil stop delinir. Bara yüklüyse direnç yanar |
| Seri NTC (≥ 30 A) | **Red.** Sürekli akım yolunda: yoğun 12,8 A'de birkaç W ve 100 °C üstü (PETG etek, Tg ≈ 80 °C). Acil stoptan hemen sonra NTC sıcak kalır, darbeyi sınırlamaz. Yük adımlarında gerilim düşürür |
| **Ön şarj rölesi K2 + direnç, K1'e paralel kol** | **Seçildi.** Kol yalnız devreye alma anında ~300 ms kapalı; acil stop iki röleyi birlikte bırakır |

**Devre:**
```
F1 20 A ──┬── K1 kontağı (40 A) ─────────────────────┬── anahtarlı 12 V bara (BTS ×2, 7,5 A ── XL4016 A/B)
          └── K2 kontağı (7 A) ── R_ön 5,6 Ω 11 W ───┘
F5 2 A ── mantar NC ──┬── K1 bobini ── BC337-40 #1 (GPIO4)      (her bobine ters paralel 1N4007)
                      └── K2 bobini ── BC337-40 #2 (GPIO19; 270 Ω seri, 2,2 kΩ taban → GND)
```
- **R_ön = 5,6 Ω, 11 W taş (çimento) direnç** (Direnc.net 13,95 TL); **K2 = 12 V 10 A sinyal rölesi** JQC-3FF-12VDC (Qianji, Direnc.net 19,36 TL, MJ:109; 15 Ekim'de JQC-3F(T73) 7 A yazıyordu), ikinci röle sürücüsü BC337-40 (E3 şartı) + 1N4007.
- **Tepe ön şarj akımı:** 14,6 V / 5,6 Ω = **2,6 A** (BMS 30 A sürekli sınırının onda biri). τ = 5,6 Ω × 2 mF = 11 ms; %99 dolum 56 ms.
  Ön şarj penceresi **300 ms**: XL çıkışındaki 8,8 mF servo kondansatörü de buck üzerinden dolsun.
- **Enerji:** bara ½ · 2 mF · 14,6² ≈ 0,21 J + servo kondansatörleri ½ · 8,8 mF · 6² ≈ 0,16 J; dirençte < 0,5 J, 11 W için ihmal.
- **Ön şarjda yük:** XL4016 A/B servoları bekleme akımıyla besler (≈ 5 W, ≈ 0,4 A): R'de ≈ 2,2 V düşüm, bara ≈ 11 V'a çıkar. K1 kapanınca
  kalan adım ≈ 2 V (darbe enerjisi doğrudan bağlamanın ≈ %2'si). BTS EN = 0 olmalı (E3 kuralı); motorlar ön şarjda çekmez.
- **Hata durumu:** K1 kapanmazsa ya da bara kısa devreyse R'de 13,3² / 5,6 ≈ 32 W (14,6 V'ta 38 W). F1 bu akımı görmez; yazılım K2'yi
  **≤ 1 s** içinde bırakır. Taş direncin kısa süreli aşırı yük dayanımı (tipik 5–10 × P_n, 5 s) seçilen ürün sayfasında yok: doğrulanmadı.
- **Yer:** güç paneli, K1 yanında; direnç panel yüzeyinden ≥ 5 mm yukarıda (ısı), PETG'ye ve kablo demetine değmez. Montaj rehberi B5a adımı.
- **Yazılım (ESP32, E3 dizisine ek):** (1) E3 ön koşulları: mantar serbest, servo hedefleri son konumda, BTS EN = 0, açık komut;
  (2) GPIO19 = 1 (K2); (3) 300 ms bekle, PC817 #2 LOW olmalı (bara var), değilse GPIO19 = 0 ve hata; (4) GPIO4 = 1 (K1);
  (5) 100 ms sonra GPIO19 = 0; (6) PC817 #2 LOW teyidi. Reset ya da acil stopta iki pin de LOW (pull-down), iki röle de bırakır.
- **K2 pini (14.11: GPIO19):** E9'da K2 son yedek pin olan GPIO2'ye (DevKit LED'i, strapping) konmuştu; LED yakıp söndüren herhangi bir program K2'yi açıp kapatıyordu.
  14.11 kararıyla K1 GPIO4'e, K2 GPIO19'a taşındı (Nextion kalkınca boşalan 16 / 17 enkodere gitti; 16 / 17'yi Arduino çekirdeği açılışta sürer); GPIO2 yalnız kart LED'i, GPIO12 boş (`pin-haritasi.md` §3.1).
  PCA9685 kanal 13 alternatifi önerilmez: ESP32 resetlenince PCA çıkışını korur, K2 kapalı kalabilir.
- **Ana anahtar açılışı:** K1 açık olduğundan yalnız F3/F4/F5/F6 girişleri bağlanır (Pololu + XL çevre girişi, tahmini ≤ 0,6 mF; 14.11'den beri F6 dalında LM2577 + LM2596 kartının giriş kondansatörleri de, değeri bilinmiyor). BMS'in bunu kesip
  kesmediği ilk açılışta gözlenir; keserse aynı yöntem ana anahtara uygulanır (malzeme eklenmedi, ölçüme bağlı).
- **Ölçüm (montajda):** bara kapasitesi multimetrenin kapasite kademesiyle (K1 açık, akü ayrık). 2 mF'tan çok büyükse ön şarj penceresi
  5τ + XL dolum payına göre uzatılır; R değişmez.

## Pin planı (ESP32 DevKit 30 pin; kesin, 14.11.2026)

Karar: Ahmet'in 13.11.2026 yetkilendirmesiyle. Tek yazılı kaynak ve gerekçeler, reset davranışı, firmware ve donanım şartları,
"kablajda teyit edilecek" listesi: `planlama/adim3/pin-haritasi.md`. Bu tablo onunla aynıdır; fark çıkarsa o esastır.
**Röle kuralı:** röleler yalnız hiçbir açılış kodunun ve varsayılan çevre biriminin sürmediği, reset boyunca LOW kalan pinlerde (4, 19). Çekirdek sabit: espressif32@6.9.0 (Arduino-ESP32 2.0.17); 3.x'e geçiş `pin-haritasi.md` gözden geçirilmeden yapılmaz. **Şart:** modül PSRAM'siz WROOM (aksi hâlde 16 / 17'deki iki enkoder kanalı çalışmaz; `pin-haritasi.md` §1, T1).

| GPIO | İşlev | Not |
|---|---|---|
| 36 (VP) | Akü gerilimi | ADC1; 100k/18k |
| 39 (VN) | Sonar sağ echo | yalnız giriş; bölücü. ADC1 açılırken ~80 ns LOW darbesi (Espressif errata GPIO-3.11) |
| 34 | Sonar orta echo | yalnız giriş; bölücü |
| 35 | Sonar sol echo | yalnız giriş; bölücü |
| 32 | BTS sol IS (IS1 + IS2) | ADC1. **Koruma zorunlu (diyotsuz bölücü):** IS → 6,8 kΩ → pin, pin → 5,1 kΩ → GND (kart IS direnci birleşik 500 Ω ise; 14 mA hata akımında pin ≈ 2,9 V). Kart direnci önce ölçülür (`pin-haritasi.md` D7, T6) |
| 33 | BTS sağ IS (IS1 + IS2) | ADC1; bölücü 32 ile aynı (zorunlu) |
| 25 / 26 | BTS sol IN1 / IN2 (ileri / geri PWM; IBT-2 adıyla RPWM / LPWM) | 3.x'te 25 = `Serial2` TX, 26 = `Serial1` RX varsayılanı (Y1) |
| 27 / 14 | BTS sağ IN1 / IN2 (ileri / geri PWM) | 3.x'te 27 = `Serial1` TX varsayılanı (Y1). 14 reset sonrası zayıf pull-up ile HIGH (Espressif IO_MUX): EN LOW olduğu için zararsız |
| 13 | BTS EN (iki kartın EN1 + EN2'si ortak) | 10 kΩ pull-down (zorunlu: reset sırasında pin yüzer) |
| 4 | Röle K1 "devreye al" (BC337-40 #1 tabanı; E3) | 270 Ω seri + 2,2 kΩ taban → GND (zorunlu). Reset boyunca dahili pull-down; 2.0.17'de açılış kodu sürmez (3.x: `Serial2` RX varsayılanı, yalnız pull-up). 14.11'e dek GPIO12 |
| 19 | Ön şarj rölesi K2 (BC337-40 #2 tabanı; E9) | 270 Ω seri + 2,2 kΩ taban → GND (zorunlu: reset sonrası dahili çekme yok). VSPI MISO yalnız giriş. 14.11'e dek GPIO2 |
| 23 | Acil stop durumu (PC817 #1; LOW = mantar serbest) | pull-up yalnız 3V3'e (dahili; dış 10 kΩ önerilir) |
| 5 | Anahtarlı 12 V durumu (PC817 #2; LOW = bara var) | pull-up yalnız 3V3'e. Strapping: yalnız SDIO slave zamanlaması, normal açılışı etkilemez |
| 21 / 22 | I2C SDA / SCL (PCA9685 0x40, BNO055) | 3V3 |
| 18 / 17 | Enkoder sol arka A / B | PCNT. 17'de 1 kΩ seri zorunlu (açılışta PSRAM saati; UART2 TX varsayılanı) |
| 16 / 15 | Enkoder sağ arka A / B | PCNT. 16'da 1 kΩ seri zorunlu (açılışta PSRAM CS HIGH). 15 strapping: LOW ise yalnız ROM açılış yazısı susar |
| 1 / 3 | UART0 (CP2102 → USB → hub → Pi) | |
| 2 | Kart üstü durum LED'i (yalnız) | strapping; dışarıya hiçbir şey bağlanmaz |
| 12 | **Boş** | strapping (açılışta HIGH = flash beslemesi 1,8 V); hiçbir şeye bağlanmaz |

- **PCA9685 kanalları:** 0–4 hat A servoları (sağ kol S1, S2, dirsek, bilek, kafa pan), 5–9 hat B servoları (sol kol S1, S2, dirsek, bilek, kafa tilt; pan ve tilt beslemesi 29.10'dan beri hat C), 10 / 11 / 12 **sonar trig** sağ / orta / sol (3,3 V, I2C ile ≥ 10 µs darbe), 13–15 yedek. Böylece üç GPIO kazanıldı. Kanal ↔ eklem `main` `kod/jestler/kanallar.yaml` ile aynı.
- Ön motorların enkoderleri bağlanmadı (pin yok). Yandaki iki motor aynı sürücüde olduğu için yan başına bir dörtlü enkoder yeter. Ön enkoder istenirse I2C GPIO genişletici (PCF8574 yavaş; PCNT gerekir) ya da ESP32-S3: bu pin kararının dışında.
- Yedek: GPIO2 E9 ile K2'ye gitmişti; Nextion kalkınca (Y2b) boşalan **GPIO16 / 17** 14.11'de enkodere gitti, enkoderden boşalan 4 / 19 K1 / K2'ye, K2'den boşalan GPIO2 yalnız LED, K1'den boşalan **GPIO12 boş** (strapping; yalnız açılışta LOW kalan bir iş için). XL4016 NTC (E7 ölçümü) için ADC1 pini kalmadı: ölçüm geçici olarak multimetreyle ya da BNO055 sıcaklığıyla.

## Malzeme

**Tarih notu 04.11.2026:** 15 Ekim'in adım 3 maliyet tablosu (D36V50F5, XL4016 × 3, tek toplam) kaldırıldı; git geçmişinde duruyor. Güncel malzeme ve fiyat: `tubitak-2209b/malzeme-listesi/Lale-malzeme-listesi-2026-11-03-v4.xlsx`.

## Açık işler

1. **Ölçüm (K1):** JGB37 durma torku ve akımı, zemin μ → `arayuz.TABAN['donus']`.
2. **Kabuk:** omni seçilirse etek ön bantta teker boşluğu 10,55 → 12 mm (1,5 mm). Etek arka bandına havalandırma yarıkları (E7). Hoparlör yeri kapandı (09.11 notu: gövde orta bandı sağ duvarı, `KY/uygulama-notu.md:59`).
3. **Montaj:** `montaj/moduller.py` omni teker adı; ana montaj ve tam tarama (6. adım). `carpisma-sonuc.json` taban ve kafa bölümleri eskidi.
4. **E5:** pin planı kesinleşti (14.11.2026, `pin-haritasi.md`). Açık kalan: kart gelince teyitler (`pin-haritasi.md` §7: modül türü, röle sürücüleri: bobin akımı ve kontak, T2, EN kilidi, BTS kartı, PC817, IS direnci ve bölücü, enkoder). Ön enkoderler bağlanmadı.
5. **E8/E9 (5. adım):** akü süreleri (Victron 256 Wh, röle 1,8 W), sigorta seti.
6. ESP32 kartında VBUS→VIN diyodu kontrolü; JGB37 enkoderinin 3,3 V'ta çalıştığı; BTS7960 modülünde IS direnci.
7. Tilt servosu radyal yük (4,55 N): ikinci rulman açık işi sürüyor.
8. Pololu D24V50F5: 12 V girişte sürekli akım üretici grafiğinden teyit edilecek (Pi hattı normal 2,67 A; tepe hesaplanmadı).
9. **JGB37 tork riski (T2):** 21 kg·cm satıcı etiketi; 9 kg·cm (Aslong 1:90) senaryosunda standart tekerle yerinde dönüş imkânsız, omni sınırda. Motor ve zemin ölçümü omni siparişinden önce.
10. PC817 modülünün 3,3 V çıkış tarafı montajda ölçülecek; olmazsa arayüz kartına doğrudan PC817 + 2,2 kΩ (E2 notu).
11. Yazılım planına: Pi seri portu DTR/RTS değiştirmeden açılır (E3); ESP32 reset = röle bırakır = kollar düşer.
12. E9 ön şarj: röle her "devreye al"da yeniden çektiği için öncelik arttı (E3). Bilinen, bu paketten eski: acil stopta XL4016 çıkışlarındaki 8,8 mF ≈ 0,16 J tutar (E9 enerji), kısa bir son servo hareketi olabilir.
13. Kafa ısı testi: normal karşılamada kapalı kafa ~49 °C hesap, ölçülecek; aşılırsa 25–30 mm egzoz fanı.
14. **10,1" QLED (04.11):** kütle (600 g varsayım), akım (0,9 A varsayım), Touch VBUS ile Power arasındaki bağ ölçülecek.
15. **Boyun demeti K14 a (14.11):** 12 V + tilt + göğüs HDMI + hub uzatması + hoparlör; yazılım kabul (pano #6 #21). Açık: alınacak HDMI kablosu Ø ≤ 6 mm (MJ:191'in çapı bilinmiyor), hub uzatması USB 2.0 ve fiş ≤ 13 × 7 mm (MJ:137 USB 3.0, büyük ihtimalle geçmez); demet kurulmadan önce tünel deneme parçasında elle fiş denemesi (parça P10.7 baskı listesinde); ince HDMI ile masa denemesi (pano #6 soru f), boyun içi dört geçiş elle, pan ±90 / tilt ±13'te büküm; demet bağlanmadan Efe'nin reset cevabı.
16. **Göğüs ekranı dalı K11 a (14.11):** ana anahtar sonrası, röle öncesi, acil stopta açık. Açık: jak ölçüsü; port yeri ve girintisi (fotoğraftan tahmini; P1.4 🟡); üç 90° fiş; F6 3 A (kutu yuvalarının ortak girişli olduğu kutu gelince teyit); regülatörün panel yeri (K52).
17. **USB (14.11):** 4 cihaz (K1 a; ses kartı çıktı, ReSpeaker 3,5 mm → PAM8403; PAM 5 V D24V50F5, K10 a). Açık: K10 a ve ses yolu masa denemesine bağlı (KT1, KT2); hub girişi gerilimi (harici besleme yok; F4 atarsa hub ≈ 0,37 A); Pi USB akım ayarı (`PSU_MAX_CURRENT` / `usb_max_current_enable`); modelde Pi 2'deki ses kartı ve uzatması (P10.7).
18. **Akü süresi:** normal ~3,8–4,4 sa kaba tahmin; yoğun senaryo yeniden hesaplanacak, ölçüm yapılacak (gereksinim 2 saat; 1,83 sa kabulü 1,65 m yükleri içindi).
19. **v4 muadilleri:** BTS7960B pin adları pin planında eşlendi (EN1/EN2 = INH, IN1/IN2 = PWM varsayımı; `pin-haritasi.md` §6.1); bu eşleme ve 3,3 V lojik kart gelince ölçülecek (T4). K2 JQC-3FF ayak düzeni.
