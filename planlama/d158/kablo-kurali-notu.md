# P5.2 — Boyun kablo kuralı notu (Efe için, 08.11.2026)

Öneri ve bilgi notu; karar yok, `kod/` değişmedi. CAD betikleri koşturulmadı: boylar betiklerin son çıktısından okundu
(`tasarim/freecad/lale158/lale158-kontrol.json` → `kablo_ozet`, aynı sayılar `lale158/kafa-yerlesim/uygulama-olcum.json` → `kablo_listesi`).
Kısaltmalar: **KYE** = `tasarim/freecad/lale158/kablo_yolu_ekran.py`, **LK** = `lale158-kontrol.json` `kablo_ozet`, **EL** = `planlama/adim3/elektrik.md`,
**YP** = `planlama/yazilim-plani.md`, **AY** = `tasarim/freecad/arayuz.py`.

## Eski kural

"ESP32 kafadaki Pi'ye tek USB kablosuyla bağlı; **HDMI ve CSI boyundan geçmez**." (`git show 0b8a245^:planlama/yazilim-plani.md`, satır 64).
Aynı sürümde göğüs ekranı Nextion'du ve "K4 sonrası boyundan ayrı sinyal geçmez" yazıyordu (aynı dosya, satır 124).

## Yeni durum (CAD, 05.11.2026 yerleşim B + R1)

- Pi 5 kafada (YP:63). Göğüste 11,6" 1080p HDMI ekran + USB dokunmatik (EL:19); Nextion yok (YP:124).
- 4'lü USB hub göğüs üst arka kapağının içinde. Boyundan **HDMI, hub uzatması, hoparlör, 12 V, tilt** iner; göğüs dokunmatiği ve ESP32 USB hub'dan çıkar, kafaya girmez (KYE:6).
- Pi portları: 1 ReSpeaker, 2 ses kartı, 3 hub, 4 kafa dokunmatiği. Hub'da göğüs dokunmatiği, ESP32, 2 boş port (KYE:7; AY:997).
- CSI kafada kalır (EL:30, EL:242); kamera FPC 300 mm (EL:267).

## Boyundan geçen kablolar (5)

Önerilen boy = yol × 1,25, hub'a bağlı kablolarda + 150 mm kapak sökme payı (AY:1003, ikisi de tahmin). Çaplar tahmini (KYE:5, KYE:18).

| Kablo | Tür ve uçlar | Yol / önerilen boy (mm) | Kesit | Boyunda kesişme (mm³, LK `kablo_tup_cakisma`) | Kaynak |
|---|---|---|---|---|---|
| Kafa 12 V | 18 AWG çift, taban F3 5 A → kafa girişi | toplam boy kaynakta yok | 10,6 mm² | tüp olarak modellenmedi (yalnız kesit, KYE:32) | EL:38; LK `mevcut` |
| Tilt servosu | 3 tel, kafa → tabandaki PCA9685 | toplam boy kaynakta yok | 5,9 mm² | tüp olarak modellenmedi (yalnız kesit, KYE:32) | EL:242; YP:29–31; LK `mevcut` |
| Göğüs HDMI | ince micro HDMI → HDMI A; Pi **HDMI1** → göğüs ekranı; ekran ucunda 90° fiş / adaptör | 757 / **950** | Ø6 | boyun mili 15,1; servo yuvası 1,7 | KYE:19; LK `kablo.HDMI` |
| Hub uzatması | USB-A; Pi port 3 → hub (hub'ın sabit 130 mm kablosu + ~1 m uzatma) | 617 / 920 | Ø4 | boyun mili 1,2 | KYE:21; LK `kablo."Hub uzatmasi"` |
| Hoparlör | PAM8403 (kafa) → hoparlör (gövde) | 823 / 1.030 | Ø4 | boyun mili 1,2 | KYE:23; LK `kablo.Hoparlor` |

Demet kesiti 69,9 mm²; en dolu dar kesit servo yuvası arka kanalı %44,8 (20 × 7,8 mm), mil arka penceresi %39,9, alt çıkış %34,3 (LK `boyun_demet_alan_mm2`, `gecis`).

**Boyundan geçmeyenler:** göğüs USB dokunmatiği (hub → ekran, 395 / 640), ESP32 USB (hub → taban, 971 / 1.360), göğüs ekranı 12 V
(taban → ekran, 1.376 / 1.720), kafa ekranı HDMI 30 cm şerit (kafa içi), CSI (LK `kablo`; EL:44; EL:267).

**Yollar kesin değil:** göğüsteki şema yollarının kablo tüpleri göğüs ekranı kasasıyla kesişiyor (HDMI 897,1 / 12 V 617,3 / USB dokunmatik 167,6 mm³;
`lale158-kontrol.json:392` `kablo_tup_cakisma`, parça "Gogus ekrani 11,6 in HDMI 1920x1080 kasali"). Göğüs kablo kesişmesi ayrıca ölçülecek; yol değişirse boylar yeniden okunmalı.

**Boyun içi kesişmeler** (tablodaki sütun): LK `kablo_tup_notu` (`lale158-kontrol.json:456`) "Listede rulman yuvasi, servo yuvasi, mil varsa o kablo gecisi elle bakilmali."
diyor; bu dört geçiş (HDMI × mil, HDMI × servo yuvası, hub uzatması × mil, hoparlör × mil) elle bakılacak.

**Eski yazımlar (P4.1'in işi):** YP:63–64 ("HDMI ve USB dokunmatik kabloları boyundan iner", "ESP32 kafadaki Pi'ye tek USB kablosuyla bağlı"),
EL:30, EL:50–51 ("1,5 m HDMI", "2 m USB … boyun … TOUCH"), EL:56 (USB dokunmatik 1.060 mm), EL:242, EL:272. Hepsi 05.11 B'den önceki düzeni anlatıyor;
commit `0b8a245` mesajı da "05.11 B + R1 yerleşimi (hub gövdede) bu metinde henüz yok: P4.1" diyor.

## Yazılıma etkisi

1. **İki HDMI ekran:** yüz (10,1" QLED, 1280×720, EL:17) Pi HDMI0'da (KYE:127), göğüs (11,6" 1080p) HDMI1'de (KYE:19). Koddaki yüz tek pygame penceresi
   ve 1280×800 (`main:kod/ayarlar.yaml:40–41`). Göğüs arayüzünün nasıl çizileceği ve dokunmanın nasıl işleneceği karara bağlanmadı (YP:124).
2. **HDMI uzunluğu:** göğüs hattı önerilen boyuyla ~950 mm pasif kablo ve ekran ucunda 90° adaptör (KYE:19). Bu kablo boyuyla Pi 5 → 11,6" ekran denemesi
   depoda kayıtlı değil: açılışta ekranın algılanması ve 1080p görüntü masada aynı kabloyla denenmeli.
3. **Ses:** kod sesi HDMI'ye veriyor (`main:kod/ayarlar.yaml:36` `vc4hdmi0`). Yeni düzende HDMI0 yüz ekranı; ses USB ses kartı → PAM8403 → hoparlör (EL:21; KYE:7, KYE:23).
4. **USB ve seri:** ESP32 artık hub'ın arkasında (KYE:7). DTR/RTS kuralı aynen geçerli (YP:52). İki dokunmatik var (kafa Pi port 4'te, göğüs hub'da);
   doğru ekrana eşlenmeleri gerekir. Hub USB'den beslenir ve "tek anahtar açık kalmalı" (EL:29): hub kapanırsa ESP32 bağlantısı ve göğüs dokunmatiği birlikte düşer.
5. **Pan:** HDMI ve hub uzatması pan ekseninin içinden (adaptör + mil Ø32) geçer (KYE:3); kablo halkası ±90 için (AY:579). Kodun pan sınırı ±45 (`main:kod/jestler/kanallar.yaml:48`), içinde.

## Efe'ye sorular (4)

1. Boyun düzenini kabul ediyor musun: 12 V + tilt + göğüs HDMI + hub uzatması + hoparlör; ESP32 ve göğüs dokunmatiği gövdedeki hub'dan? (karar kuyruğu K14)
2. Yüz HDMI0, göğüs HDMI1 ataması yazılım için uygun mu; yüz ve göğüs arayüzü aynı süreçte mi çalışacak? (Yüz ayarı bugün 1280×800, QLED 1280×720.)
3. ESP32'nin ve göğüs dokunmatiğinin hub arkasında olması seri bağlantı ve dokunma eşlemesi için sorun çıkarır mı?
4. ~1 m'lik bir HDMI kablosuyla Pi 5 → 11,6" ekran denemesini masada yapabilir misin (algılama ve 1080p)?
