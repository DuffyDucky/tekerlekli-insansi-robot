# F8a günlüğü: 158 sipariş paketi (P8.1)

Tarih: 09.11.2026. Ajan: F8a (A). Çıktılar: `F8a-siparis.md`, `F8a-siparis.json`, bu dosya. Mevcut dosyalara dokunulmadı; commit yok; FreeCAD açılmadı.
**Sipariş verilmedi, sepete ürün eklenmedi, satıcıya yazılmadı, hesap açılmadı / giriş yapılmadı.** Yalnız herkese açık ürün ve arama sayfaları okundu.

## 1. Yöntem

1. **Kaynaklar** (salt okundu): `planlama/d158/F8a-brief.md`, `planlama/dongu-158.md` (§2 kurallar, F8a satırı, K1–K9), `planlama/siparis-farki-2026-10-29.md`, `planlama/maliyet.json` (29.10; V3 görünür 98 satır, ara 89.495,40, genel 102.919,71, koşullu 108.208,77; 11 `fiyat_bekliyor`), `git show b27fd80:planlama/maliyet.json` (17.10 Excel'in içeriği), `planlama/adim5/maliyet_toplam.py` (toplam yöntemi: V3 + yazıcı + ×1,15), `planlama/proje-plani.md` 1–168 (kritik yol, S = 16.11, erken alım ≈ 1.496 TL), `planlama/d158/karar-kuyrugu.md` (K1, K2, K4, K9–K12, K16, K17), `planlama/d158/F1b-kontrol.md`, `planlama/d158/F4a-gunluk.md`, `tasarim/freecad/lale158/kafa-yerlesim/uygulama-notu.md` 85–160 (kablo boyları, portlar; yalnız okundu, FreeCAD açılmadı), `raporlar/kaynaklar/06-onayli-satici-A.md`, `raporlar/kaynaklar/06-aku-secimi.md`.
2. **`tubitak-2209b/`** yalnız okundu (F1b emsali): `malzeme-listesi/Lale-malzeme-listesi-2026-11-03-v4.xlsx` (Python stdlib zip/xml ile, openpyxl yok), `malzeme-listesi/rapor.md`, `malzeme-listesi/whatsapp-mesaji.txt`, `BAGLAM.md` 130, 208, 221–222. Hiçbiri değiştirilmedi.
3. **158 güncel liste** = v4 (03.11; 81 site satırı + 46 bulunamayan + kamera + 4 hizmet + 2 koşullu + 2 elde + PAKET A 13) + `maliyet.json`'daki K4 (6) ve F1b (3) adayları. `maliyet.json` gövdesi 29.10 (1,65 m) listesi + F4a'nın 09.11 kısmi eklemeleri olduğundan kalem listesi v4'ten alındı; `maliyet.json` köprüyle karşılaştırıldı.
4. **Fiyat ve stok okuma:** sayfalar `curl` ile indirildi (paralel, tarayıcı kimliğiyle), metin veri olarak ayrıştırıldı; sayfadaki yönergeler uygulanmadı.
   - Fiyat: JSON-LD `Product.offers`; witcdn altyapısında (Motorobit, Direnc, Robotistan) gizli `product-price-vat-include` alanı (**KDV dahil**; JSON-LD fiyatı Motorobit/Direnc'te KDV hariç); Robocombo (ikas) JSON-LD indirimli fiyat + SKU'ya uyan varyant kaydı; Ideasoft sitelerinde (Rulmanal, paslanmazcivata.ist, Robotzade) `salePrice` + KDV.
   - Stok: Motorobit `STOCK`; Robocombo varyant `stockCount`; Robotistan ve Direnc'te ürün sayfası adet göstermediği için **site arama sayfasındaki** ürün kaydının `quantity` alanı (Direnc 99999 = 'adet gösterilmiyor'); Ideasoft `product-stock-amount`.
   - Robotistan sayfalarında gizli bir 'Tükendi' bloğu (`d-none`) var; WebFetch bunu 'tükendi' diye okuyabiliyor. Bu yüzden JSON-LD `availability` ve arama `quantity` esas alındı.
   - Robocombo araması yalnız JavaScript ile çalışıyor, okunamadı: Robocombo'da ikinci satıcı yalnız bilinen ürün sayfalarıyla arandı.
   - Çapraz kontrol: 6 sayfa WebFetch ile ayrıca okundu (PAM8403, USB ses kartı, DS3235, JGB37, Victron, 90° micro USB kablo ve diğerleri); curl sonucuyla aynı.
   - WebSearch (standard kip) 3 sorgu: `USB 2.0 erkek dişi 90 derece L adaptör robotistan OR motorobit OR robocombo OR direnc.net`, `micro USB 90 derece erkek dişi adaptör dirsek robocombo`, `3.5mm stereo L tipi 90 derece erkek kısa kablo robocombo OR robotistan OR motorobit`. Onaylı sitede uygun sonuç çıkmadı; extended kipe geçilmedi (aynı sorgular site aramasında da boş).
5. **Varyant fiyatı:** paslanmazcivata.ist ve Rhino3DPrinter'da boy/varyant seçimi sayfada JavaScript ile; seçim sepete ekleme gerektirmese de fiyat yalnız taban olarak okunabildi. Bu satırlar 'kısmen' sayıldı.
6. **Toplam yöntemi:** tutar = adet × bugün sayfada görülen fiyat; birincil stokta değilse ikinci satıcı fiyatı (işaretli). Bugün fiyat görülmeyen satırda v4 (03.11) fiyatı 'doğrulanmadı' etiketiyle. Pay eklenmedi; `maliyet.json` kıyası için ×1,15 ayrıca verildi. Kargo eklenmedi.
7. Sayfa okuma saatleri: 2026-11-09 03:35 – 2026-11-09 04:27 (yerel). Ara dosyalar ve betikler oturumun geçici klasöründe (depoya girmedi).

## 2. Bakılan sayfalar

### 2.1 Ürün sayfaları (200 sayfa, tarih 09.11.2026)

| URL | Saat | HTTP |
|---|---|---|
| https://atakale.com/index.php?product_id=438&route=product%2Fproduct | 03:35 | 200 |
| https://robiz.net/longubracket | 03:47 | 200 |
| https://robiz.net/servoarm25t | 03:47 | 200 |
| https://robiz.net/servobracket | 03:47 | 200 |
| https://robocombo.com/12awg-kirmizi-silikon-kablo-1m | 03:35 | 200 |
| https://robocombo.com/12awg-siyah-silikon-kablo-1m | 03:35 | 200 |
| https://robocombo.com/12v-fan-40x40x10mm | 03:35 | 200 |
| https://robocombo.com/13-3-1080p-kapasitif-dokunmatik-ips-ekran-raspbe-4329 | 03:48 | 200 |
| https://robocombo.com/16awg-kirmizi-silikon-kablo-1m | 03:35 | 200 |
| https://robocombo.com/16awg-siyah-silikon-kablo-1m | 03:35 | 200 |
| https://robocombo.com/2-metre-micro-usb-2-0-kablo-sarj-kablosu-4143 | 03:35 | 200 |
| https://robocombo.com/2-pin-1-no-508mm-klemens-2511201001 | 03:35 | 200 |
| https://robocombo.com/300-parca-30-cesit-direnc-seti-14w-3923 | 03:35 | 200 |
| https://robocombo.com/40-pin-disi-header-180-derece | 03:35 | 200 |
| https://robocombo.com/amass-xt60h-f-disi-lipo-batarya-guc-konnektor-4912 | 03:35 | 200 |
| https://robocombo.com/amass-xt60h-m-erkek-lipo-batarya-guc-konnektor-4913 | 03:35 | 200 |
| https://robocombo.com/bts7960b-dc-43a-cift-motor-surucu-2867 | 03:48 | 200 |
| https://robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4534 | 03:35 | 200 |
| https://robocombo.com/esp32-wi-fi-bluetooth-gelistirme-karti | 03:35 | 200 |
| https://robocombo.com/imax-b6-sarj-cihazi-80w-adaptorlu-3245 | 03:35 | 200 |
| https://robocombo.com/pca9685-16-kanal-12-bit-pwm-surucu-lehimli-4603 | 03:35 | 200 |
| https://robocombo.com/sandisk-ultra-64gb-micro-sd-2910 | 03:35 | 200 |
| https://robocombo.com/tower-pro-mg996r-metal-disli-dijital-servo-motor-180-derece | 03:35 | 200 |
| https://robocombo.com/xl4016-8a-dc-dc-step-down-voltaj-regulatoru-2991 | 03:35 | 200 |
| https://userpilbatarya.com/urun/14-4-volt-6-amper-lifepo4-sarj-cihazi-4s/ | 03:47 | 200 |
| https://www.cnc-marketi.com/arama?q=M6+imbus | 04:24 | 200 |
| https://www.cnc-marketi.com/arama?q=m6x16 | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu-m6 | 03:47 | 200 |
| https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu-m6 | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu10-kanal-profil-tirtilli-somunu | 03:47 | 200 |
| https://www.cnc-marketi.com/urun/10-kanal-profil-tirtilli-somunu10-kanal-profil-tirtilli-somunu | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip | 03:47 | 200 |
| https://www.cnc-marketi.com/urun/40x40-sigma-profil-10-kanal-agir-tip | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/45x45-gizli-kose-baglanti-90-k10 | 03:47 | 200 |
| https://www.cnc-marketi.com/urun/45x45-gizli-kose-baglanti-90-k10 | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/genis-kose-baglanti-40x40-k10 | 03:47 | 200 |
| https://www.cnc-marketi.com/urun/genis-kose-baglanti-40x40-k10 | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/m6x12-fosfat-allen-alyan-basli-imbus-civata | 04:25 | 200 |
| https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata | 03:47 | 200 |
| https://www.cnc-marketi.com/urun/m6x16-fosfat-allen-alyan-basli-imbus-civata | 04:24 | 200 |
| https://www.cnc-marketi.com/urun/m6x16-fosfat-bombe-basli-imbus-civata | 04:25 | 200 |
| https://www.cnc-marketi.com/urun/m6x20-fosfat-allen-alyan-basli-imbus-civata | 04:25 | 200 |
| https://www.direnc.net/022r-11w-tas-direnc-11664 | 03:35 | 200 |
| https://www.direnc.net/116inch-hdmi-lcd-ekran-raspberry-pi-uyumlu-1920x1080-ips-teknik-ozellikleri | 03:48 | 200 |
| https://www.direnc.net/12v-minyonpot-qianji-role--jqc-3ff-12vdc-10a | 03:35 | 200 |
| https://www.direnc.net/13-3-inc-hdmi-lcd-h-1920x1080-ips-dokunmatik-ekran | 03:48 | 200 |
| https://www.direnc.net/133-inc-kapasitif-dokunmatik-ekran-lcd-19201080-hdmi-ips | 03:48 | 200 |
| https://www.direnc.net/133inch-hdmi-lcd-h-kilifla-v2-1920x1080-ips | 03:48 | 200 |
| https://www.direnc.net/25mm-x-100mm-kablo-bagi-100-adet-siyah | 03:35 | 200 |
| https://www.direnc.net/2x050-kordon-kablo | 03:43 | 200 |
| https://www.direnc.net/30-mm-x-30-m-mavi-bant-ressamlar-baski-maskeleme-araci-reprap-3d-yazici | 03:35 | 200 |
| https://www.direnc.net/6x13-delikli-plaket | 03:35 | 200 |
| https://www.direnc.net/arduino-ultrasonic-sensor-hc-sr04 | 03:35 | 200 |
| https://www.direnc.net/beyaz-petg-filament-175mm-1kg | 03:48 | 200 |
| https://www.direnc.net/hdmi-disi-erkek-cevirici-90-derece-dirsek | 03:43 | 200 |
| https://www.direnc.net/inmp441-mems-i2s-cok-yonlu-mikrofon-modulu | 03:35 | 200 |
| https://www.direnc.net/insert-somun-m3 | 04:27 | 200 |
| https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor | 03:35 | 200 |
| https://www.direnc.net/p6ke6v8a | 03:35 | 200 |
| https://www.direnc.net/raspberry-pi-5-kamera-fpc-kablosu-300mm | 03:35 | 200 |
| https://www.direnc.net/siyah-petg-filament-175mm-1kg-tri-d | 03:48 | 200 |
| https://www.direnc.net/usb-erkek-disi-kablo--1 | 03:43 | 200 |
| https://www.direnc.net/ut-353-mini-ses-ve-seviye-olcer | 03:35 | 200 |
| https://www.direnc.net/yp-600-6mm-plastik-distans-m25-vidaya-uygun-20-adet | 03:35 | 200 |
| https://www.elektrix.com/acil-stop-mantar-40mm-emergency-etiketli | 03:47 | 200 |
| https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya | 03:50 | 200 |
| https://www.gecersunenerji.com/12-volt-24-ah-lifepo4-batarya | 04:24 | 200 |
| https://www.hepsiburada.com/victron-lithium-superpack-12-8v-20ah-256wh-m5-dahili-bms-li-lifepo4-lityum-aku-pm-HBC0000M2DPYC | 03:47 | 403 |
| https://www.kartalotomasyon.com.tr/B200E60-60mm-Mantar-Acil-Stop-Butonu-NO,PR-55175.html | 03:47 | 200 |
| https://www.kartalotomasyon.com.tr/urun/12v-40a-mikro-role-5-fisli | 03:47 | 200 |
| https://www.makermarketim.net/bts7960b-40-amper-motor-surucu-modulu | 03:47 | 200 |
| https://www.merterelektronik.com/orbus-12.8-volt-20-amper-lityum-lifepo4-aku-lit-12-20 | 03:50 | 200 |
| https://www.motorobit.com/10a-mikro-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/18-awg-silicone-cable-black-1-meter | 03:35 | 200 |
| https://www.motorobit.com/18-awg-silicone-cable-red-1-meter | 03:35 | 200 |
| https://www.motorobit.com/1n4007-1000v-1a-diyot | 03:35 | 200 |
| https://www.motorobit.com/1n5819-1a-40v-diyot | 03:35 | 200 |
| https://www.motorobit.com/1x40-erkek-header-40-pin-254mm-180-derece-beyaz | 03:35 | 200 |
| https://www.motorobit.com/2200uf-16v-electrolytic-capacitor-10x20mm | 03:35 | 200 |
| https://www.motorobit.com/2273-203-3-pin-buat-klemensi | 03:35 | 200 |
| https://www.motorobit.com/25t-servo-motor-kolu-gri | 03:35 | 200 |
| https://www.motorobit.com/2a-maksi-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/2a-mikro-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/2x035-kordon-kablo-1-metre | 03:43 | 200 |
| https://www.motorobit.com/2x050-kordon-kablo-1-metre | 03:43 | 200 |
| https://www.motorobit.com/2x075-tseli-kordon-kablo-1-metre | 03:35 | 200 |
| https://www.motorobit.com/30a-maksi-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/30x30x10mm-12v-010a-fan-2-kablolu | 03:43 | 200 |
| https://www.motorobit.com/328-parca-renkli-makaron-seti | 03:35 | 200 |
| https://www.motorobit.com/35mm-stereo-jak-erkek | 03:43 | 200 |
| https://www.motorobit.com/3m-serit-metre-16mm | 03:35 | 200 |
| https://www.motorobit.com/5-amper-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/55x21mm-90-derece-erkek-dc-barrel-jak | 03:43 | 200 |
| https://www.motorobit.com/5a-mikro-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/6-channel-auto-blade-fuse-box | 03:35 | 200 |
| https://www.motorobit.com/6mm-motor-safti-ile-uyumlu-hex-tekerlek-kaplini | 03:35 | 200 |
| https://www.motorobit.com/75a-mikro-oto-sigorta-bicak-sigorta | 03:35 | 200 |
| https://www.motorobit.com/anahtarli-usb-uzatma-kablosu-disi-erkek-30cm | 03:43 | 200 |
| https://www.motorobit.com/asw-a01-100a-on-off-battery-disconnect-switch | 03:35 | 200 |
| https://www.motorobit.com/ds3218mg-20kg-su-gecirmez-dijital-servo-motor | 03:49 | 200 |
| https://www.motorobit.com/gepro-um-0224-24v-2a-adaptor | 03:35 | 200 |
| https://www.motorobit.com/harici-ses-karti-cm108-hoparlor-mikrofon-girisi | 03:35 | 200 |
| https://www.motorobit.com/hcw-p715-9-36vtan-5va-5a-voltaj-dusurucu-regulator-karti | 03:48 | 200 |
| https://www.motorobit.com/hdmi-disi-erkek-cevirici-konnektor-90-derece | 03:35 | 200 |
| https://www.motorobit.com/hw468-5v-5a-voltaj-dusurucu-regulator-karti | 03:48 | 200 |
| https://www.motorobit.com/iypk-30x30-10-adet-yapiskanli-kroseler | 03:35 | 200 |
| https://www.motorobit.com/lipo-pil-tutucu-cirt-bant-20x400mm-siyah | 03:35 | 200 |
| https://www.motorobit.com/mah-112-c-4-12v-30/40a-otomotiv-rolesi-5-pin | 03:35 | 200 |
| https://www.motorobit.com/np2-be102-nc-metal-acil-stop-butonu | 03:35 | 200 |
| https://www.motorobit.com/p6ke18a-transil-diyot | 03:35 | 200 |
| https://www.motorobit.com/pam8403-ses-kontrollu-ses-amplifikatoru | 03:43 | 200 |
| https://www.motorobit.com/speaker-4-ohm-3w-40mm | 03:35 | 200 |
| https://www.motorobit.com/su-gecirmez-minimicro-bicak-sigorta-yuvasi-16awg | 03:35 | 200 |
| https://www.motorobit.com/sy8205-7-30vtan-5va-5a-voltaj-dusurucu-servo-surucu-guc-karti | 03:35 | 200 |
| https://www.motorobit.com/tpa3116-d-class-50-hifi-2x50w-2-kanal-stereo-amfi-modulu | 03:35 | 200 |
| https://www.motorobit.com/usb-30-disi-erkek-siyah-uzatma-kablosu-1-metre | 03:43 | 200 |
| https://www.motorobit.com/usb-71-kanal-kulaklik-mikrofon-ses-karti | 03:35 | 200 |
| https://www.motorobit.com/usb-type-c-erkek-24-pin-test-karti | 03:35 | 200 |
| https://www.motorobit.com/waveshare-156-19201080-kapasitif-dokunmatik-hdmi-ekran | 03:48 | 200 |
| https://www.motorobit.com/wg-1224s0510p-dc-dc-12-24vden-5v-10a-voltaj-dusurucu-modul | 03:48 | 200 |
| https://www.motorobit.com/xt60e-m-panel-tipi-erkek-konnektor-xt60 | 03:35 | 200 |
| https://www.otomasyoncu.net/urun/40x40-kose-baglanti-genis | 03:47 | 200 |
| https://www.otomasyoncu.net/urun/40x40-kose-baglanti-genis | 04:24 | 200 |
| https://www.otomasyoncu.net/urun/sigma-profil-40x40-agir-kanal-10 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/5mm-paslanmaz-setskur-cesitleri-kafasiz-alyan-din916 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/6mm-paslanmaz-setskur-cesitleri-kafasiz-alyan-din916 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/m3-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/m3-paslanmaz-imbus-civata-cesitleri-din912 | 04:24 | 200 |
| https://www.paslanmazcivata.ist/urun/m4-paslanmaz-imbus-civata-cesitleri-din912 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/m5-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380 | 03:50 | 200 |
| https://www.paslanmazcivata.ist/urun/m5-paslanmaz-imbus-civata-cesitleri-din912 | 03:50 | 200 |
| https://www.paslanmazcivata.ist/urun/m6-paslanmaz-bombe-bas-alyan-imbus-civata-cesitleri-din7380 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/m6-paslanmaz-imbus-civata-cesitleri-din912 | 04:24 | 200 |
| https://www.paslanmazcivata.ist/urun/paslanmaz-fiberli-somun-cesitleri-din985 | 03:47 | 200 |
| https://www.paslanmazcivata.ist/urun/paslanmaz-pul-dar-pul-cesitleri-din125 | 03:47 | 200 |
| https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3 | 03:47 | 200 |
| https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3 | 04:24 | 200 |
| https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5 | 03:47 | 200 |
| https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m5 | 04:24 | 200 |
| https://www.robocombo.com/dsservo-ds3218-20kg-servo-motor-180-derece-su--4151 | 03:49 | 200 |
| https://www.robocombo.com/max9814-mikrofon-amplifikator-cma-4544pf-w-yuksek-3865 | 03:48 | 200 |
| https://www.robolinkmarket.com/328-parca-renkli-makaron-seti-kutulu | 03:47 | 200 |
| https://www.robolinkmarket.com/hc-sr04-arduino-ultrasonic-mesafe-sensoru | 03:47 | 200 |
| https://www.robolinkmarket.com/m3-ysb-vida-somun-ve-pul-seti-220-parca | 03:47 | 200 |
| https://www.robolinkmarket.com/m4-ysb-vida-somun-ve-pul-seti-395-parca | 03:47 | 200 |
| https://www.robolinkmarket.com/m5-ysb-vida-somun-ve-pul-seti-188-parca | 03:47 | 200 |
| https://www.robotistan.com/101-inc-lcd-ekran-modulu | 03:48 | 200 |
| https://www.robotistan.com/101-inc-qled-ekran-modulu | 03:35 | 200 |
| https://www.robotistan.com/116-inc-lcd-ekran-modulu | 03:35 | 200 |
| https://www.robotistan.com/133-inc-kapasitif-dokunmatik-ekran | 03:48 | 200 |
| https://www.robotistan.com/23w-mini-amfi-devresi-pam8403 | 03:35 | 200 |
| https://www.robotistan.com/30cm-40-pin-ayrilabilen-disi-disi-f-f-jumper-kablo-300-mm | 03:35 | 200 |
| https://www.robotistan.com/35-mm-erkek-erkek-15-mt-stereo-aux-kablo | 03:35 | 200 |
| https://www.robotistan.com/40-serisi-m5-t-somun | 03:35 | 200 |
| https://www.robotistan.com/43mm-led-arcade-basmali-buton-kirmizi | 03:35 | 200 |
| https://www.robotistan.com/60-cekirdek-22awg-servo-kablosu | 03:35 | 200 |
| https://www.robotistan.com/7-hdmi-kapasitif-dokunmatik-lcd-ekran-1024x600 | 03:48 | 200 |
| https://www.robotistan.com/8-ohm-5w-hoparlor | 03:35 | 200 |
| https://www.robotistan.com/8mm-m3-disidisi-plastik-aralayici | 03:35 | 200 |
| https://www.robotistan.com/aluminyum-l-tipi-37d-motor-tutucu | 03:35 | 200 |
| https://www.robotistan.com/bno055-9dof-sensor-modul | 03:35 | 200 |
| https://www.robotistan.com/bts7960b-20-amper-motor-surucu-karti | 03:35 | 200 |
| https://www.robotistan.com/buyuk-arazi-tekerlegi-125mm-x-58mm-mavi | 03:35 | 200 |
| https://www.robotistan.com/cok-fonksiyonlu-servo-motor-tutucu | 03:48 | 200 |
| https://www.robotistan.com/dc-dc-ayarli-voltaj-yukseltici-dusurucu-karti-lm2577lm2596 | 03:35 | 200 |
| https://www.robotistan.com/diy-hdmi-kablo-30-cm-hdmi-serit-kablo | 03:35 | 200 |
| https://www.robotistan.com/fibromast-3d-175-mm-petg-filament-beyaz | 03:48 | 200 |
| https://www.robotistan.com/hdmi-erkek-mikro-hdmi-erkek-altin-uclu-kablo-1 | 03:35 | 200 |
| https://www.robotistan.com/hdmi-plug-diy-hdmi-kablo-ile-birlikte-kullanilabilir | 03:35 | 200 |
| https://www.robotistan.com/kablolu-bicak-sigorta-yuvasi-standart-boy | 03:35 | 200 |
| https://www.robotistan.com/micro-hdmi-plug-diy-hdmi-kablo-ile-birlikte-kullanilabilir | 03:35 | 200 |
| https://www.robotistan.com/micro-sd-kart-32gb | 03:35 | 200 |
| https://www.robotistan.com/micro-usb-15cm-data-kablosu-siyah | 03:43 | 200 |
| https://www.robotistan.com/mikro-usb-kablo-30 | 03:43 | 200 |
| https://www.robotistan.com/pc817-2-kanal-optokuplor-izolasyon-modulu | 03:35 | 200 |
| https://www.robotistan.com/pololu-5v-15a-step-down-voltaj-regulator-d24v150f5-pl-2881 | 03:48 | 200 |
| https://www.robotistan.com/pololu-5v-5a-step-down-voltaj-regulator-d24v50f5-pl-2851 | 03:35 | 200 |
| https://www.robotistan.com/raspberry-pi-5-4-gb | 03:35 | 200 |
| https://www.robotistan.com/raspberry-pi-active-cooler-en | 03:35 | 200 |
| https://www.robotistan.com/raspberry-pi-ai-hat | 03:35 | 200 |
| https://www.robotistan.com/raspberry-pi-kamera-modulu-3 | 03:43 | 200 |
| https://www.robotistan.com/raspberry-pi-usb-kablo-a-micro-b-dik-usb-kablo-donusturucu | 03:43 | 200 |
| https://www.robotistan.com/raspberry-pi5-icin-aktif-sogutucu | 03:43 | 200 |
| https://www.robotistan.com/raspberrypi-camera-module | 03:35 | 200 |
| https://www.robotistan.com/respeaker-2-mikrofonlu-pi-hat | 03:48 | 200 |
| https://www.robotistan.com/respeaker-mic-array-v20 | 03:35 | 200 |
| https://www.robotistan.com/sogutma-fan-12v-kablo-28cm | 03:43 | 200 |
| https://www.robotistan.com/u-tipi-uzun-servo-motor-cercevesi | 03:48 | 200 |
| https://www.robotistan.com/usb-erkek-disi-donusturucu-30cm | 03:43 | 200 |
| https://www.robotistan.com/usb-hub-3lu-mini-usb-a-dahili-guc-anahtari | 03:35 | 200 |
| https://www.robotistan.com/usb-uzatma-kablo-40-cm-seffaf | 03:43 | 200 |
| https://www.robotistan.com/usb-uzatma-kablosu-15-m-seffaf | 03:43 | 200 |
| https://www.robotistan.com/vbsemi-elec-irlz44npbf-vb | 03:35 | 200 |
| https://www.robotzade.com/urun/37-mm-motor-tutucu-aparat-metal | 03:47 | 200 |
| https://www.rulmanal.com.tr/urun/625-zz-kwc-5-16-5-rulman | 03:47 | 200 |
| https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman | 03:47 | 200 |
| https://www.rulmanal.com.tr/urun/6808-2rs-kwc-40x52x7-rulman | 04:24 | 200 |
| https://www.rulmanal.com.tr/urun/6808-2rs-nsk-40x52x7-rulman | 03:47 | 200 |

Hepsiburada Victron sayfası 403 döndü (bot engeli); fiyatı doğrulanmadı. paslanmazcivata.ist ilk denemede 429 verdi, sonra okundu.

### 2.2 Arama sayfaları (332 sorgu, 09.11.2026)

Sonuç sayısı parantezde; 'stok sorgusu' = ürün adının ilk kelimeleriyle yapılan, yalnız stok adedi için kullanılan arama.

- https://www.direnc.net/arama?q=10.1+qled (1)
- https://www.direnc.net/arama?q=100a+ak%C3%BC+ay%C4%B1r%C4%B1c%C4%B1 (0)
- https://www.direnc.net/arama?q=11.6+in%C3%A7 (0)
- https://www.direnc.net/arama?q=12+awg+silikon+kablo (0)
- https://www.direnc.net/arama?q=12V+Minyonpot+Qianji+R%C3%B6le+JQC-3FF-12VDC+10A (stok sorgusu)
- https://www.direnc.net/arama?q=16+awg+silikon+kablo (0)
- https://www.direnc.net/arama?q=18+awg+silikon+kablo (0)
- https://www.direnc.net/arama?q=1n4007 (4)
- https://www.direnc.net/arama?q=1n5819 (1)
- https://www.direnc.net/arama?q=2+metre+micro+usb (0)
- https://www.direnc.net/arama?q=2.5mm+x+100mm+Kablo+Ba%C4%9F%C4%B1+100+Adet (stok sorgusu)
- https://www.direnc.net/arama?q=2200uf+16v (1)
- https://www.direnc.net/arama?q=25t+servo+kolu (0)
- https://www.direnc.net/arama?q=2x0.5+kablo (1)
- https://www.direnc.net/arama?q=3.5+mm+90+derece (0)
- https://www.direnc.net/arama?q=3.5+mm+jak+kablo (1)
- https://www.direnc.net/arama?q=3.5mm+erkek+erkek (6)
- https://www.direnc.net/arama?q=3.5mm+l+jak (0)
- https://www.direnc.net/arama?q=300+Par%C3%A7a+30 (stok sorgusu)
- https://www.direnc.net/arama?q=300+Par%C3%A7a+30+%C3%87e%C5%9Fit (stok sorgusu)
- https://www.direnc.net/arama?q=300+Par%C3%A7a+30+%C3%87e%C5%9Fit+Diren%C3%A7+Seti+- (stok sorgusu)
- https://www.direnc.net/arama?q=3010+fan (0)
- https://www.direnc.net/arama?q=30a+b%C4%B1%C3%A7ak+sigorta (0)
- https://www.direnc.net/arama?q=30mmX30M+3D+Yaz%C4%B1c%C4%B1+%C4%B0%C3%A7in+Mavi+Bask%C4%B1+Maskeleme (stok sorgusu)
- https://www.direnc.net/arama?q=30x30+fan (2)
- https://www.direnc.net/arama?q=37d+motor+tutucu (0)
- https://www.direnc.net/arama?q=37mm+motor+tutucu (0)
- https://www.direnc.net/arama?q=4+ohm+3w+hoparl%C3%B6r (1)
- https://www.direnc.net/arama?q=43mm+arcade+buton (0)
- https://www.direnc.net/arama?q=5.08+klemens+2 (7)
- https://www.direnc.net/arama?q=5.6R+11W+Ta%C5%9F+Diren%C3%A7 (stok sorgusu)
- https://www.direnc.net/arama?q=5v+5a+voltaj+d%C3%BC%C5%9F%C3%BCr%C3%BCc%C3%BC (0)
- https://www.direnc.net/arama?q=6x13+Delikli+Plaket (stok sorgusu)
- https://www.direnc.net/arama?q=90+derece+adapt%C3%B6r (0)
- https://www.direnc.net/arama?q=HC-SR04+Arduino+Ultrasonik+Mesafe+Sens%C3%B6r%C3%BC (stok sorgusu)
- https://www.direnc.net/arama?q=INMP441+Mems+I2S+%C3%87ok+Y%C3%B6nl%C3%BC+Mikrofon+Mod%C3%BCl%C3%BC (stok sorgusu)
- https://www.direnc.net/arama?q=JGB37-520+-+12V+60RPM+Enkoderli+Motor (stok sorgusu)
- https://www.direnc.net/arama?q=P6KE6V8A+Transil+Diyot (stok sorgusu)
- https://www.direnc.net/arama?q=Raspberry+Pi+5+Kamera+FPC+Kablosu+- (stok sorgusu)
- https://www.direnc.net/arama?q=Uni-T+UT-353+Mini+Ses+ve+Seviye+%C3%96l%C3%A7er (stok sorgusu)
- https://www.direnc.net/arama?q=YP-600+6mm+Plastik+Distans+-+M2.5+Vidaya (stok sorgusu)
- https://www.direnc.net/arama?q=a%C3%A7%C4%B1l%C4%B1+usb (0)
- https://www.direnc.net/arama?q=acil+stop (2)
- https://www.direnc.net/arama?q=active+cooler (1)
- https://www.direnc.net/arama?q=ai+hat (0)
- https://www.direnc.net/arama?q=aktif+so%C4%9Futucu+raspberry+pi+5 (0)
- https://www.direnc.net/arama?q=arazi+tekerle%C4%9Fi+125 (0)
- https://www.direnc.net/arama?q=asw-a01 (0)
- https://www.direnc.net/arama?q=aux+kablo (0)
- https://www.direnc.net/arama?q=b%C4%B1%C3%A7ak+sigorta (0)
- https://www.direnc.net/arama?q=bno055 (1)
- https://www.direnc.net/arama?q=bts7960 (1)
- https://www.direnc.net/arama?q=c%C4%B1rt+bant (0)
- https://www.direnc.net/arama?q=camera+module+3 (1)
- https://www.direnc.net/arama?q=d24v50f5 (0)
- https://www.direnc.net/arama?q=dc+jak+90+derece (0)
- https://www.direnc.net/arama?q=dc+jak+erkek (0)
- https://www.direnc.net/arama?q=di%C5%9Fi+header+40 (0)
- https://www.direnc.net/arama?q=diren%C3%A7+seti (32)
- https://www.direnc.net/arama?q=dirsekli (0)
- https://www.direnc.net/arama?q=ds3235 (0)
- https://www.direnc.net/arama?q=erkek+header+40 (0)
- https://www.direnc.net/arama?q=esp32+30+pin (0)
- https://www.direnc.net/arama?q=hc-sr04 (3)
- https://www.direnc.net/arama?q=hdmi+%C5%9Ferit+kablo (0)
- https://www.direnc.net/arama?q=hdmi+90+derece (1)
- https://www.direnc.net/arama?q=hex+kaplin (0)
- https://www.direnc.net/arama?q=hoparl%C3%B6r+kablo (0)
- https://www.direnc.net/arama?q=hoparl%C3%B6r+kablosu (0)
- https://www.direnc.net/arama?q=imax+b6 (0)
- https://www.direnc.net/arama?q=irlz44n (2)
- https://www.direnc.net/arama?q=k%C4%B1sa+micro+usb (0)
- https://www.direnc.net/arama?q=kordon+kablo (2)
- https://www.direnc.net/arama?q=lm2577+lm2596 (0)
- https://www.direnc.net/arama?q=m3+plastik+aralay%C4%B1c%C4%B1 (0)
- https://www.direnc.net/arama?q=m5+t+somun (0)
- https://www.direnc.net/arama?q=makaron+seti (0)
- https://www.direnc.net/arama?q=mg996r (0)
- https://www.direnc.net/arama?q=micro+hdmi+plug (0)
- https://www.direnc.net/arama?q=micro+usb+10+cm (0)
- https://www.direnc.net/arama?q=micro+usb+20+cm (0)
- https://www.direnc.net/arama?q=micro+usb+90+derece (0)
- https://www.direnc.net/arama?q=micro+usb+a%C3%A7%C4%B1l%C4%B1 (0)
- https://www.direnc.net/arama?q=micro+usb+d%C3%B6n%C3%BC%C5%9Ft%C3%BCr%C3%BCc%C3%BC (1)
- https://www.direnc.net/arama?q=micro+usb+data+kablosu (0)
- https://www.direnc.net/arama?q=micro+usb+kablo (3)
- https://www.direnc.net/arama?q=mikro+hdmi+kablo (2)
- https://www.direnc.net/arama?q=mini+b%C4%B1%C3%A7ak+sigorta (0)
- https://www.direnc.net/arama?q=mini+b%C4%B1%C3%A7ak+sigorta+yuvas%C4%B1 (0)
- https://www.direnc.net/arama?q=oto+r%C3%B6le+12v (0)
- https://www.direnc.net/arama?q=otomotiv+r%C3%B6lesi (0)
- https://www.direnc.net/arama?q=p6ke18 (0)
- https://www.direnc.net/arama?q=pam8403 (1)
- https://www.direnc.net/arama?q=pc817+2+kanal (1)
- https://www.direnc.net/arama?q=pca9685 (2)
- https://www.direnc.net/arama?q=pololu+5v (0)
- https://www.direnc.net/arama?q=raspberry+pi+kamera+mod%C3%BCl+3 (2)
- https://www.direnc.net/arama?q=respeaker (0)
- https://www.direnc.net/arama?q=servo+horn (0)
- https://www.direnc.net/arama?q=servo+uzatma+kablosu (0)
- https://www.direnc.net/arama?q=sigorta+kutusu (0)
- https://www.direnc.net/arama?q=sigorta+yuvas%C4%B1 (7)
- https://www.direnc.net/arama?q=stereo+kablo (4)
- https://www.direnc.net/arama?q=sy8205 (0)
- https://www.direnc.net/arama?q=type-c+erkek+test+kart%C4%B1 (0)
- https://www.direnc.net/arama?q=usb+90+derece (0)
- https://www.direnc.net/arama?q=usb+a+erkek+di%C5%9Fi (0)
- https://www.direnc.net/arama?q=usb+adapt%C3%B6r (8)
- https://www.direnc.net/arama?q=usb+dirsek (0)
- https://www.direnc.net/arama?q=usb+erkek+di%C5%9Fi (1)
- https://www.direnc.net/arama?q=usb+hub+4 (1)
- https://www.direnc.net/arama?q=usb+kablo (26)
- https://www.direnc.net/arama?q=usb+l+tipi (0)
- https://www.direnc.net/arama?q=usb+ses+kart%C4%B1 (0)
- https://www.direnc.net/arama?q=usb+uzatma (2)
- https://www.direnc.net/arama?q=wago+3 (0)
- https://www.direnc.net/arama?q=xl4016 (2)
- https://www.direnc.net/arama?q=xt60 (12)
- https://www.direnc.net/arama?q=xt60+panel (1)
- https://www.direnc.net/arama?q=yap%C4%B1%C5%9Fkanl%C4%B1+kro%C5%9Fe (0)
- https://www.motorobit.com/arama?q=10.1+qled (1)
- https://www.motorobit.com/arama?q=11.6+in%C3%A7 (0)
- https://www.motorobit.com/arama?q=12+awg+silikon+kablo (2)
- https://www.motorobit.com/arama?q=16+awg+silikon+kablo (2)
- https://www.motorobit.com/arama?q=2+metre+micro+usb (0)
- https://www.motorobit.com/arama?q=2x0.5+kablo (2)
- https://www.motorobit.com/arama?q=3.5+mm+90+derece (0)
- https://www.motorobit.com/arama?q=3.5+mm+jak+kablo (0)
- https://www.motorobit.com/arama?q=3.5mm+erkek+erkek (9)
- https://www.motorobit.com/arama?q=3.5mm+l+jak (0)
- https://www.motorobit.com/arama?q=3010+fan (0)
- https://www.motorobit.com/arama?q=30x30+fan (8)
- https://www.motorobit.com/arama?q=37d+motor+tutucu (0)
- https://www.motorobit.com/arama?q=37mm+motor+tutucu (1)
- https://www.motorobit.com/arama?q=43mm+arcade+buton (0)
- https://www.motorobit.com/arama?q=5.08+klemens+2 (1)
- https://www.motorobit.com/arama?q=5v+5a+voltaj+d%C3%BC%C5%9F%C3%BCr%C3%BCc%C3%BC (3)
- https://www.motorobit.com/arama?q=90+derece+adapt%C3%B6r (0)
- https://www.motorobit.com/arama?q=a%C3%A7%C4%B1l%C4%B1+usb (5)
- https://www.motorobit.com/arama?q=active+cooler (3)
- https://www.motorobit.com/arama?q=ai+hat (0)
- https://www.motorobit.com/arama?q=aktif+so%C4%9Futucu+raspberry+pi+5 (3)
- https://www.motorobit.com/arama?q=arazi+tekerle%C4%9Fi+125 (3)
- https://www.motorobit.com/arama?q=aux+kablo (3)
- https://www.motorobit.com/arama?q=bno055 (1)
- https://www.motorobit.com/arama?q=bts7960 (1)
- https://www.motorobit.com/arama?q=camera+module+3 (1)
- https://www.motorobit.com/arama?q=d24v50f5 (0)
- https://www.motorobit.com/arama?q=dc+jak+90+derece (4)
- https://www.motorobit.com/arama?q=dc+jak+erkek (12)
- https://www.motorobit.com/arama?q=delikli+pertinaks (0)
- https://www.motorobit.com/arama?q=delikli+plaket (14)
- https://www.motorobit.com/arama?q=di%C5%9Fi+header+40 (3)
- https://www.motorobit.com/arama?q=diren%C3%A7+seti (7)
- https://www.motorobit.com/arama?q=dirsekli (0)
- https://www.motorobit.com/arama?q=ds3235 (1)
- https://www.motorobit.com/arama?q=esp32+30+pin (0)
- https://www.motorobit.com/arama?q=hc-sr04 (4)
- https://www.motorobit.com/arama?q=hdmi+%C5%9Ferit+kablo (0)
- https://www.motorobit.com/arama?q=hdmi+90+derece (1)
- https://www.motorobit.com/arama?q=hoparl%C3%B6r+kablo (6)
- https://www.motorobit.com/arama?q=hoparl%C3%B6r+kablosu (0)
- https://www.motorobit.com/arama?q=imax+b6 (1)
- https://www.motorobit.com/arama?q=irlz44n (0)
- https://www.motorobit.com/arama?q=jgb37 (0)
- https://www.motorobit.com/arama?q=jqc-3ff+12v (1)
- https://www.motorobit.com/arama?q=k%C4%B1sa+micro+usb (0)
- https://www.motorobit.com/arama?q=kablo+ba%C4%9F%C4%B1+100 (32)
- https://www.motorobit.com/arama?q=kamera+fpc+kablo (0)
- https://www.motorobit.com/arama?q=kordon+kablo (5)
- https://www.motorobit.com/arama?q=lm2577+lm2596 (0)
- https://www.motorobit.com/arama?q=m2.5+distans (0)
- https://www.motorobit.com/arama?q=m3+plastik+aralay%C4%B1c%C4%B1 (32)
- https://www.motorobit.com/arama?q=m5+t+somun (0)
- https://www.motorobit.com/arama?q=mg996r (4)
- https://www.motorobit.com/arama?q=micro+hdmi+plug (0)
- https://www.motorobit.com/arama?q=micro+usb+10+cm (0)
- https://www.motorobit.com/arama?q=micro+usb+20+cm (0)
- https://www.motorobit.com/arama?q=micro+usb+90+derece (0)
- https://www.motorobit.com/arama?q=micro+usb+a%C3%A7%C4%B1l%C4%B1 (0)
- https://www.motorobit.com/arama?q=micro+usb+d%C3%B6n%C3%BC%C5%9Ft%C3%BCr%C3%BCc%C3%BC (5)
- https://www.motorobit.com/arama?q=micro+usb+data+kablosu (1)
- https://www.motorobit.com/arama?q=micro+usb+kablo (13)
- https://www.motorobit.com/arama?q=mikro+hdmi+kablo (2)
- https://www.motorobit.com/arama?q=p6ke6 (2)
- https://www.motorobit.com/arama?q=pam8403 (5)
- https://www.motorobit.com/arama?q=pc817+2+kanal (1)
- https://www.motorobit.com/arama?q=pca9685 (1)
- https://www.motorobit.com/arama?q=pololu+5v (0)
- https://www.motorobit.com/arama?q=raspberry+pi+kamera+mod%C3%BCl+3 (0)
- https://www.motorobit.com/arama?q=respeaker (0)
- https://www.motorobit.com/arama?q=servo+uzatma+kablosu (6)
- https://www.motorobit.com/arama?q=stereo+kablo (4)
- https://www.motorobit.com/arama?q=ta%C5%9F+diren%C3%A7+5.6 (0)
- https://www.motorobit.com/arama?q=usb+90+derece (0)
- https://www.motorobit.com/arama?q=usb+a+erkek+di%C5%9Fi (1)
- https://www.motorobit.com/arama?q=usb+adapt%C3%B6r (14)
- https://www.motorobit.com/arama?q=usb+dirsek (0)
- https://www.motorobit.com/arama?q=usb+erkek+di%C5%9Fi (15)
- https://www.motorobit.com/arama?q=usb+hub+4 (3)
- https://www.motorobit.com/arama?q=usb+kablo (32)
- https://www.motorobit.com/arama?q=usb+l+tipi (0)
- https://www.motorobit.com/arama?q=usb+uzatma (18)
- https://www.motorobit.com/arama?q=xl4016 (2)
- https://www.motorobit.com/arama?q=xt60 (30)
- https://www.robotistan.com/arama?q=10.1in%C3%A7+Kapasitif+Dokunmatik+QLED+Quantum+Dot+Ekran (stok sorgusu)
- https://www.robotistan.com/arama?q=100a+ak%C3%BC+ay%C4%B1r%C4%B1c%C4%B1 (0)
- https://www.robotistan.com/arama?q=11.6in%C3%A7+Kapasitif+Dokunmatik+LCD+Ekran+Mod%C3%BCl%C3%BC+- (stok sorgusu)
- https://www.robotistan.com/arama?q=12+awg+silikon+kablo (1)
- https://www.robotistan.com/arama?q=16+awg+silikon+kablo (1)
- https://www.robotistan.com/arama?q=18+awg+silikon+kablo (1)
- https://www.robotistan.com/arama?q=1n4007 (2)
- https://www.robotistan.com/arama?q=1n5819 (1)
- https://www.robotistan.com/arama?q=2+3+W (stok sorgusu)
- https://www.robotistan.com/arama?q=2+3+W+Mini (stok sorgusu)
- https://www.robotistan.com/arama?q=2+3+W+Mini+Amfi+Devresi+- (stok sorgusu)
- https://www.robotistan.com/arama?q=2+metre+micro+usb (0)
- https://www.robotistan.com/arama?q=2200uf+16v (1)
- https://www.robotistan.com/arama?q=22AWG+Servo+Uzatma+Kablosu (stok sorgusu)
- https://www.robotistan.com/arama?q=25t+servo+kolu (0)
- https://www.robotistan.com/arama?q=2x0.5+kablo (0)
- https://www.robotistan.com/arama?q=3.5+MM+Erkek+Erkek+1.5+Mt+Stereo (stok sorgusu)
- https://www.robotistan.com/arama?q=3.5+mm+90+derece (5)
- https://www.robotistan.com/arama?q=3.5+mm+jak+kablo (0)
- https://www.robotistan.com/arama?q=3.5mm+erkek+erkek (36)
- https://www.robotistan.com/arama?q=3.5mm+l+jak (0)
- https://www.robotistan.com/arama?q=30+cm+40+Pin+Ayr%C4%B1labilen+Di%C5%9Fi-Di%C5%9Fi+F-F (stok sorgusu)
- https://www.robotistan.com/arama?q=3010+fan (2)
- https://www.robotistan.com/arama?q=30a+b%C4%B1%C3%A7ak+sigorta (0)
- https://www.robotistan.com/arama?q=30x30+fan (0)
- https://www.robotistan.com/arama?q=4+ohm+3w+hoparl%C3%B6r (0)
- https://www.robotistan.com/arama?q=40+Serisi+M5+T+Somun (stok sorgusu)
- https://www.robotistan.com/arama?q=43mm+LED+Arcade+Basmal%C4%B1+Buton+K%C4%B1rm%C4%B1z%C4%B1 (stok sorgusu)
- https://www.robotistan.com/arama?q=5.08+klemens+2 (1)
- https://www.robotistan.com/arama?q=8+ohm+5w+hoparl%C3%B6r (1)
- https://www.robotistan.com/arama?q=8mm+M3+Di%C5%9Fi-Di%C5%9Fi+Plastik+Aralay%C4%B1c%C4%B1 (stok sorgusu)
- https://www.robotistan.com/arama?q=90+derece+adapt%C3%B6r (0)
- https://www.robotistan.com/arama?q=Aluminyum+L+tipi+37D+Motor+Tutucu+%C4%B0kili (stok sorgusu)
- https://www.robotistan.com/arama?q=B%C3%BCy%C3%BCk+Arazi+Tekerle%C4%9Fi+125+mm+x+58 (stok sorgusu)
- https://www.robotistan.com/arama?q=BNO055+9DOF+Sens%C3%B6r+Mod%C3%BCl (stok sorgusu)
- https://www.robotistan.com/arama?q=BTS7960B+40+Amper+Motor+S%C3%BCr%C3%BCc%C3%BC+Kart%C4%B1 (stok sorgusu)
- https://www.robotistan.com/arama?q=DC-DC+Ayarl%C4%B1+Voltaj+Y%C3%BCkseltici-D%C3%BC%C5%9F%C3%BCr%C3%BCc%C3%BC+Kart%C4%B1+LM2577+LM2596 (stok sorgusu)
- https://www.robotistan.com/arama?q=DIY+HDMI+Kablo+-+30+cm+HDMI (stok sorgusu)
- https://www.robotistan.com/arama?q=HDMI+Erkek+Mikro+HDMI+Erkek+Alt%C4%B1n+U%C3%A7lu (stok sorgusu)
- https://www.robotistan.com/arama?q=HDMI+Plug+DIY+HDMI+Kablo+ile+Birlikte (stok sorgusu)
- https://www.robotistan.com/arama?q=Kablolu+B%C4%B1%C3%A7ak+Sigorta+Yuvas%C4%B1+Standart+Boy (stok sorgusu)
- https://www.robotistan.com/arama?q=Micro+HDMI+Plug+DIY+HDMI+Kablo+ile (stok sorgusu)
- https://www.robotistan.com/arama?q=Micro+SD+Kart+32GB (stok sorgusu)
- https://www.robotistan.com/arama?q=Mikro+USB+Kablo (stok sorgusu)
- https://www.robotistan.com/arama?q=PC817+2+Kanal+Optokupl%C3%B6r+%C4%B0zolasyon+Mod%C3%BCl%C3%BC (stok sorgusu)
- https://www.robotistan.com/arama?q=Pololu+5+V%2C+5+A+Step-Down+Voltaj (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+5+-+4GB (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+AI (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+AI+HAT (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+AI+HAT+26T (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+Active (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+Active+Cooler (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+Camera (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+Camera+Module (stok sorgusu)
- https://www.robotistan.com/arama?q=Raspberry+Pi+Camera+Module+3 (stok sorgusu)
- https://www.robotistan.com/arama?q=ReSpeaker+Mic+Array+v2.0 (stok sorgusu)
- https://www.robotistan.com/arama?q=USB+Hub+-+4l%C3%BC+-+USB+Dahili (stok sorgusu)
- https://www.robotistan.com/arama?q=VBsemi+Elec+IRLZ44NPBF-VB (stok sorgusu)
- https://www.robotistan.com/arama?q=a%C3%A7%C4%B1l%C4%B1+usb (0)
- https://www.robotistan.com/arama?q=acil+stop (0)
- https://www.robotistan.com/arama?q=active+cooler (1)
- https://www.robotistan.com/arama?q=asw-a01 (0)
- https://www.robotistan.com/arama?q=aux+kablo (1)
- https://www.robotistan.com/arama?q=b%C4%B1%C3%A7ak+sigorta (2)
- https://www.robotistan.com/arama?q=c%C4%B1rt+bant (12)
- https://www.robotistan.com/arama?q=camera+module+3 (6)
- https://www.robotistan.com/arama?q=dc+jak+90+derece (0)
- https://www.robotistan.com/arama?q=dc+jak+erkek (0)
- https://www.robotistan.com/arama?q=delikli+pertinaks (16)
- https://www.robotistan.com/arama?q=delikli+plaket (0)
- https://www.robotistan.com/arama?q=di%C5%9Fi+header+40 (0)
- https://www.robotistan.com/arama?q=diren%C3%A7+seti (2)
- https://www.robotistan.com/arama?q=dirsekli (0)
- https://www.robotistan.com/arama?q=ds3235 (0)
- https://www.robotistan.com/arama?q=erkek+header+40 (0)
- https://www.robotistan.com/arama?q=esp32+30+pin (1)
- https://www.robotistan.com/arama?q=hc-sr04 (3)
- https://www.robotistan.com/arama?q=hdmi+90+derece (0)
- https://www.robotistan.com/arama?q=hex+kaplin (6)
- https://www.robotistan.com/arama?q=hoparl%C3%B6r+kablo (1)
- https://www.robotistan.com/arama?q=hoparl%C3%B6r+kablosu (0)
- https://www.robotistan.com/arama?q=imax+b6 (1)
- https://www.robotistan.com/arama?q=jgb37 (1)
- https://www.robotistan.com/arama?q=jqc-3ff+12v (0)
- https://www.robotistan.com/arama?q=k%C4%B1sa+micro+usb (0)
- https://www.robotistan.com/arama?q=kablo+ba%C4%9F%C4%B1+100 (10)
- https://www.robotistan.com/arama?q=kamera+fpc+kablo (0)
- https://www.robotistan.com/arama?q=kordon+kablo (0)
- https://www.robotistan.com/arama?q=m2.5+distans (0)
- https://www.robotistan.com/arama?q=makaron+seti (3)
- https://www.robotistan.com/arama?q=mg996r (2)
- https://www.robotistan.com/arama?q=micro+usb+10+cm (0)
- https://www.robotistan.com/arama?q=micro+usb+20+cm (0)
- https://www.robotistan.com/arama?q=micro+usb+90+derece (1)
- https://www.robotistan.com/arama?q=micro+usb+a%C3%A7%C4%B1l%C4%B1 (0)
- https://www.robotistan.com/arama?q=micro+usb+d%C3%B6n%C3%BC%C5%9Ft%C3%BCr%C3%BCc%C3%BC (6)
- https://www.robotistan.com/arama?q=micro+usb+data+kablosu (2)
- https://www.robotistan.com/arama?q=micro+usb+kablo (6)
- https://www.robotistan.com/arama?q=mini+b%C4%B1%C3%A7ak+sigorta (1)
- https://www.robotistan.com/arama?q=mini+b%C4%B1%C3%A7ak+sigorta+yuvas%C4%B1 (1)
- https://www.robotistan.com/arama?q=oto+r%C3%B6le+12v (0)
- https://www.robotistan.com/arama?q=otomotiv+r%C3%B6lesi (0)
- https://www.robotistan.com/arama?q=p6ke18 (0)
- https://www.robotistan.com/arama?q=p6ke6 (0)
- https://www.robotistan.com/arama?q=pam8403 (1)
- https://www.robotistan.com/arama?q=pca9685 (3)
- https://www.robotistan.com/arama?q=servo+horn (0)
- https://www.robotistan.com/arama?q=sigorta+kutusu (0)
- https://www.robotistan.com/arama?q=sigorta+yuvas%C4%B1 (11)
- https://www.robotistan.com/arama?q=stereo+kablo (3)
- https://www.robotistan.com/arama?q=sy8205 (0)
- https://www.robotistan.com/arama?q=ta%C5%9F+diren%C3%A7+5.6 (14)
- https://www.robotistan.com/arama?q=type-c+erkek+test+kart%C4%B1 (0)
- https://www.robotistan.com/arama?q=usb+90+derece (2)
- https://www.robotistan.com/arama?q=usb+a+erkek+di%C5%9Fi (3)
- https://www.robotistan.com/arama?q=usb+adapt%C3%B6r (5)
- https://www.robotistan.com/arama?q=usb+dirsek (0)
- https://www.robotistan.com/arama?q=usb+erkek+di%C5%9Fi (8)
- https://www.robotistan.com/arama?q=usb+kablo (21)
- https://www.robotistan.com/arama?q=usb+l+tipi (0)
- https://www.robotistan.com/arama?q=usb+ses+kart%C4%B1 (0)
- https://www.robotistan.com/arama?q=usb+uzatma (4)
- https://www.robotistan.com/arama?q=wago+3 (0)
- https://www.robotistan.com/arama?q=xl4016 (3)
- https://www.robotistan.com/arama?q=xt60 (17)
- https://www.robotistan.com/arama?q=xt60+panel (0)
- https://www.robotistan.com/arama?q=yap%C4%B1%C5%9Fkanl%C4%B1+kro%C5%9Fe (0)
- https://robocombo.com/search?q=usb+uzatma (JavaScript; sonuç okunamadı)

### 2.3 WebFetch ile ayrıca okunanlar (09.11.2026)

- https://www.robotistan.com/23w-mini-amfi-devresi-pam8403
- https://www.motorobit.com/usb-71-kanal-kulaklik-mikrofon-ses-karti
- https://robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4534
- https://www.direnc.net/jgb37-520-12v-60rpm-enkoderli-motor
- https://atakale.com/index.php?product_id=438&route=product%2Fproduct
- https://www.robotistan.com/raspberry-pi-usb-kablo-a-micro-b-dik-usb-kablo-donusturucu

### 2.4 Düzeltme turu 1 (09.11.2026, 04:24–04:27 sayfa; 04:26 arama)

19 sayfa yeniden okundu (CNC Marketi 9, Rhino3DPrinter 2, paslanmazcivata.ist 2, Rulmanal 1, Otomasyoncu 1, Geçersun Enerji 1, Direnc 1, CNC arama 2); §2.1 tablosunda saatleriyle. WebSearch (standard kip), ruthex M3×5,7 Türk satıcısı için:

- `ruthex M3 5.7 ısıl gömme somun insert satın al`
- `M3 insert somun 5.7 mm boy 3D baskı pirinç`
- `"M3x5.7" insert somun site:.com.tr OR site:trendyol.com OR site:hepsiburada.com`

Sonuç: ruthex RX-M3x5.7 yalnız yurt dışı satıcılarda (3DJAKE, galaxus, 3dprima); Türk satıcı bulunamadı. Extended kipe geçilmedi: sonuç takvim için yeterince net (yurt dışı teslim erken alıma yetişmez).

## 3. Bulunamayanlar ve doğrulanamayanlar

| Kalem | Durum | Aranan yer |
|---|---|---|
| L USB-A dirsek 90° (K4c) | Bulunamadı | Robotistan, Motorobit, Direnc aramaları (usb 90 derece, dirsek, l tipi, açılı usb, usb adaptör, usb erkek dişi); WebSearch. Motorobit'te yalnız 50 cm açılı erkek-erkek USB 3.0 kablo |
| L 3,5 mm fişli kısa kablo (K4f) | Bulunamadı | Aynı üç site (3.5 mm, aux, stereo jak); WebSearch. Düz lehimli fiş var (Motorobit 9,18) |
| 90° micro USB adaptör (F1b) | Adaptör yok; muadil 90° kablo | Robotistan 'USB Kablo A - Micro B (Dik)' 87,82 (boy yazmıyor); 30 cm 90° kablo tükendi |
| Mesafe burcu M5×40 dişi-dişi | Bulunamadı (v4'te de) | Onaylı siteler; plan önerisi: baskılı burç + uzun cıvata |
| Akü kutup pabucu, köpük bant 1 mm, dişli çubuk M3, ISO mini röle soketi, JR konnektör seti, perçin somun M3/M5, yönlü mikrofon | Bugün fiyat görülmedi | v4 yaklaşık fiyatı tutara girdi, 'doğrulanmadı' |
| M2,5×5, M2,5×8 imbus, M2×8 PT, mumlu ip | Fiyat yok (v4'te de) | Tutara girmedi |
| Kamera Module 3 | Tükendi | Robotistan iki sayfa (0); Direnc/Motorobit'te yok; Robocombo v4'te tükendi |
| 8 Ω 5 W hoparlör (PAKET A) | Fiyat sayfada 0,00 görünüyor, stok 1 (gereken 3) | Robotistan; ikinci satıcı aranmadı (PAKET A brief kapsamında değil) |
| Victron akü ikinci satıcı | Onaylı 4 sitede yok; Hepsiburada 403 | Plan yedeği Limacell 12 V 24 Ah (gecersunenerji, onaylı değil) 09.11: 4.814,86, InStock, özel üretim ort. 3 iş günü; ölçü/kütle CAD yuvasıyla kontrol edilmedi |
| Isıl gömme insert Ø4,0 × 5,7 varyantı | Taban fiyat 5,29 (M3), 6,35 (M5) | Sayfada L 5,7 varyantı yok (ID3 OD4 L4; ID3 OD5 L4–8); CAD deliği Ø4,0 / L 5,7 ile uyum doğrulanmadı. ruthex RX-M3x5.7 (dış çap 4,6, delik 4,0–4,2) Türkiye'de bulunamadı. Seçenekler sipariş §4.1 |
| M6×16 fosfat (A151) | CNC Marketi 'Son 2 Adet', gereken 18 | İkinci satıcı paslanmaz DIN 912 A2 (paslanmazcivata.ist, taban 3,89, ürün stoğu 322.514); muadil CNC M6×16 fosfat bombe başlı 4,80, stok 235. CNC'de M6×12 ve M6×20 fosfat allen de tükendi. Fosfat şartının kaynağı bulunamadı |
| Paslanmaz vidalar (24 satır) | Taban fiyat | Boy seçilmeden; adet kademesi var, sayfada |
| İkinci satıcısı olmayanlar (onaylı sitelerde) | JGB37 60 dev/dk, D24V50F5, ReSpeaker v2.0, DIY HDMI seti, mini alçak profil sigortalar, Wago 2273, ASW-A01, 30 A bıçak, USB-C test kartı, 6 yollu sigorta kutusu, 43 mm arcade buton, 5,6 Ω 11 W, M2,5 distans, P6KE18A, Pi 5 kamera FPC 300 mm (yalnız 500 mm), yapışkanlı kroşe (Robotistan tükendi). Bakılmadı: 1×40 erkek header, standart bıçak 2/5 A | §5.1 tablosu |

## 4. Doğrulama kapsamı (öncelik sırası)

- (a) 11 fiyatsız aday: 9'u fiyatlandı (PAM8403 21,96; USB ses kartı 91,80; 90° HDMI 45,90; USB-A 30 cm 77,46; USB-A 1 m 214,20; micro USB 15 cm 38,42; hoparlör kablosu 2 × 30,60; 90° micro USB muadil kablo 87,82; 90° DC jak 12,24). 2'si bulunamadı.
- (b) Kritik yol ve erken alım: hepsi bakıldı (§3 sipariş dosyası). Mesafe burcu bulunamadı; lazer/bükme teklifi yok.
- (c) En pahalı 15: hepsi bugün sayfada; yönlü mikrofon (doğrulanmadı) ve kamera (stok yok) hariç.
- (d) Kalanlar: sipariş satırlarının 93/136'i tam, 27'i kısmen doğrulandı; 10 doğrulanmadı/stok yok; 6 fiyatsız. İkinci satıcı fiyatı olan satır: 73.

## 5. `maliyet.json` için önerilen güncellemeler (kayıt ajanı uygular; F8a dokunmadı)

1. 11 `fiyat_bekliyor` satırı: 9'una `tl`, satıcı, URL ve tarih 2026-11-09 (fiyatlar `F8a-siparis.json` K4a/b/d/e, F1a/b/c, S89, S47). Satır satır: PAM8403 (S89) ve USB ses kartı (S47) → `secenek` kaldırılır (`maliyet.json` notu: K16 kararlı, genel toplama girer); K4a, K4b, K4d, K4e → `secenek: kosullu`; F1b 3 fiş (90° HDMI F1a, 90° micro USB F1b, 90° DC jak F1c) → `secenek: kosullu` (Ahmet kesin derse kaldırılır; 90° HDMI v4'te kesin); F1b micro USB satırının `not`'una 'adaptör değil, 90° kablo; boy sayfada yok'. K4c ve K4f `fiyat_bekliyor` kalsın (bulunamadı).
2. 90° HDMI ve 90° micro USB satırları `g: ses` grubunda; F1b göğüs ekranı kablosu olduğu için `elektronik` (USB-A uzatma satırlarıyla aynı grup; 90° DC jak `guc`ta kalır) olmalı.
3. Omuz servosu DS3235: 1.171,50 → 1.809,00 (Robocombo, liste 1.930; stok 85); `not`'a 'indirimli fiyat'. Yedek satırı da. Hedef: `maliyet.json` idx 14 ve 124 (ver v3).
4. MG996R: 199,00 → 202,50 (Robocombo, stok 393).
5. Mikrofon dizisi: XVF3800 5.500 (tahmini, RobotShop) → ReSpeaker Mic Array v2.0 6.680,04 (Robotistan, stok 9), v4 kararı.
6. Kafa 5 V düşürücü: Pololu D36V50F5 (ithal) 1.975,38 → D24V50F5 2.266,93 (Robotistan, stok 14).
7. Göğüs ekranı 11,6" 9.367,79 + 12 V regülatör 275,67 + HDMI 1,5 m 117,10 satırları eklensin (yok).
8. **Koşullu (yalnız Ahmet kafa ekranının satın alınacağını teyit ederse; sipariş §9 madde 5):** Yüz/kafa ekranı satırına QLED 10,1" Robotistan 7.217,95 (stok 2, `elde` yok) eklenir ve V3'teki Waveshare 10,1" (B) `elde` 12.424,50 satırı V3'ten çıkarılır. Etki: ara −5.206,55 (genel × 1,15 ile −5.987,53); 'elimizdekiler düşülmüş' toplamı +7.217,95 × 1,15 artar. Teyit yoksa hiçbir şey değişmez (README ve `maliyet.json` notu 'hocadan gelirse'). Hedef: `maliyet.json` idx 33.
9. Kafa: SY8205 146,88, micro USB 30 cm 34,76, USB hub 187,23; 'Ekran kablosu 114,30' yerine DIY HDMI şerit seti (105,51 + 247,61 + 247,61). PAM8403 ve USB ses kartı öneri 1'de; burada ikinci kez yazılmaz.
10. **Geri çekildi.** Filament → baskı hizmeti (7,7 kg × 1.500) tahmini fiyatı fiyatlı satır yapar; teklif yok. Ahmet'e soru olarak sipariş §9 madde 10'da. `maliyet.json`'da değişiklik yok.
11. Bluetooth gamepad (750) ve perçin somun aleti (400) V3'ten çıkarılsın: ver "v1,v2" + not (F4a'nın MAX98357A deseni; satır silinmez, idx kaymaz; Ahmet'in 03.11 kararı, v4 raporu).
12. Kargo satırı (`kalemler` içinde `g: kargo`, adet 12 × 120): `adet` 12 → 4, `tl` 120 kalır (tahmini), `not`: 'Atakale, paslanmazcivata.ist, Rulmanal, Otomasyoncu: eşik altı ya da eşik bilinmiyor, ücret sayfada yok (F8a §8, 09.11)'. Yeni satır: 'Rhino3DPrinter kargosu', `g: kargo`, adet 1, `tl` 139, `durum: dogrulandi`, URL https://www.rhino3dprinter.com/urun/kaliteli-insert-somun-m3 ('Yurtiçi Kargo 139TL', 2.500 TL üzeri ücretsiz; sipariş 969,14). Onaylı dört site ve CNC Marketi eşiği geçiyor: 0.
13. **Fiyat kısmı geri çekildi** (taban fiyat; CAD varyantı sayfada yok). Yalnız ısıl gömme M3 ve M5 satırlarının `not`'una: '09.11 taban 5,29 / 6,35; CAD L 5,7 varyantı sayfada yok (F8a D3)'. `tl` ve `durum` değişmez; M3 adedi (168 ↔ 176) P4.3'te.
14. Rulman: 6808-2RS 106,80 → 108,16 (stok 51); 625ZZ 29,67 → 30,04, sayfa adı 'BGR (Karbon)': model alanındaki 'KWC' düzeltilsin.
15. Tırtıllı somun M5: CNC Marketi 3,85 → 3,96 (v4'teki Robotistan satırı tükendi); M6 3,79 → 3,90; adet 60 → 62 (v4).
16. Geniş köşe bağlantı: birincil CNC Marketi kalır, `stok: "yok"` (09.11 'Stokta yok'); `alt`: Otomasyoncu 31,36 (stok ve kargo sayfada yok; fiyat '0,52 USD + KDV'). F8a tutarı Otomasyoncu'yla (4 × 31,36 = 125,44).
17. Akü satırına not: Atakale 'özel sipariş, 7 gün içinde tedarik'; stok 1. Fiyat aynı (12.680,70). `alt`: Limacell 12 V 24 Ah, gecersunenerji, 4.814,86 (09.11; onaylı değil, özel üretim ort. 3 iş günü, ölçü kontrolü gerekli). Hedef: `maliyet.json` idx 48.
18. Satıcı/model aktarımı: aşağıdaki eşleme tablosundaki satırlar (yalnız F8a'da bugün sayfada doğrulanan satırlar). Her satırda `satici`, `url`, `tl` (= birim), `durum: dogrulandi`, `stok` F8a'dan; URL `F8a-siparis.json` `kalemler[id]` → kullanılan satıcı. Bir `maliyet.json` satırına birden çok F8a satırı düşüyorsa satır bölünür. Kısmen / v4 yaklaşık / bulunamadı satırları (JR seti, röle soketi, pabuç, vidalar, insert, saplama, perçin somun, mesafe burcu) aktarılmaz. idx'ler kayıt öncesi maliyet.json (c7f9af4) içindir; 18 ilk uygulanır, sondan başa (126 → 0); model alanı da F8a urun'üyle değişir.
19. Adet değişenler (v4): servo uzatma 19, 18 AWG 14 m, hat sigortası yuvası 5, bıçak sigorta 7, TVS 3, pertinaks 5, ESP32/dokunmatik USB kablosu 2, vida satırları (§2.1 'Vida adetleri').
20. **Koşullu, en son uygulanır:** `tarih` → `"2026-11-09"` (ISO, mevcut alan gibi). Yalnız F8a'da 'doğrulandı' olan satırlar `durum: dogrulandi` olur; 'kısmen' ve 'doğrulanmadı' satırları değişmez. 1,58 m geçişi tamamlanmadıysa `notlar[0]`'da 'kısmen' kalır.

Toplam **20 öneri**: 10 geri çekildi, 13'ün fiyat kısmı geri çekildi, 8 ve 20 koşullu, kalanı kontrol onaylı (`F8a-kontrol.md` §4). Uygulama sırası 1–19, en son 20. Tahmini fiyat fiyatlı satıra, taban fiyat 'doğrulandı'ya dönüşmez.

### 5.1 Öneri 18 eşleme tablosu (`maliyet.json` `kalemler[idx]` ↔ F8a id)

Birim ve satıcı: F8a'da kullanılan satıcı (09.11). `maliyet.json` adedi F8a'dan farklıysa F8a adedi yazılır (adet değişimi öneri 19).

| idx | `maliyet.json` ad | F8a id | Satıcı | Birim (TL) | F8a adet | Not |
|---|---|---|---|---|---|---|
| 0 | Enkoderli DC motor | S9 | Direnc.net | 665,41 | 4 |  |
| 1 | Motor montaj braketi | S84 | Robotistan | 764,79 | 2 | adet 2 paket (4 adet) |
| 2 | Altıgen kaplin | S20 | Motorobit | 122,40 | 4 |  |
| 3 | Arazi tekerleği | S72 | Robotistan | 362,27 | 4 |  |
| 5 | Sigma profil | A162 | CNC Marketi | 934,08 | 3 | onaylı olmayan satıcı |
| 6 | İç köşe bağlantı (gizli) | A134 | CNC Marketi | 39,60 | 8 | onaylı olmayan satıcı; 45×45 K10 sayfası |
| 18 | Servo horn 25T alüminyum | S40 | Motorobit | 76,50 | 10 |  |
| 19 | Servo uzatma kablosu | S88 | Robotistan | 44,52 | 19 |  |
| 24 | Soğutucu | S90 | Robotistan | 322,02 | 1 |  |
| 26 | Alt kontrolcü | S53 | Robocombo | 289,50 | 1 |  |
| 27 | Servo sürücü | S61 | Robocombo | 181,00 | 1 |  |
| 28 | Yönelim sensörü (IMU) | S93 | Robotistan | 771,50 | 1 |  |
| 29 | Ultrasonik mesafe sensörü | S16 | Direnc.net | 60,49 | 3 |  |
| 31 | Kamera kablosu | S11 | Direnc.net | 175,43 | 1 |  |
| 43 | Hoparlör | S30 | Motorobit | 107,10 | 1 |  |
| 44 | Bas-konuş düğmesi | S73 | Robotistan | 76,24 | 1 |  |
| 45 | Motor sürücü | S85 | Robotistan | 265,30 | 2 | S85 (3 adet) bölünür: 45'te 2 |
| 46 | DC-DC düşürücü | S54 | Robocombo | 121,00 | 4 |  |
| 49 | Akü şarj cihazı | S52 | Robocombo | 1.809,00 | 1 |  |
| 50 | Acil stop butonu | S19 | Motorobit | 306,00 | 1 |  |
| 51 | Sigorta kutusu | S41 | Motorobit | 315,18 | 1 |  |
| 52 | Ana sigorta yuvası | S71 | Robotistan | 48,18 | 1 |  |
| 53 | Ana sigorta | S22 | Motorobit | 4,28 | 2 |  |
| 54 | Ana güç anahtarı | S21 | Motorobit | 281,52 | 1 |  |
| 55 | Güç konnektörü | S66 | Robocombo | 30,50 | 5 | 2 satıra bölünür |
|  |  | S67 | Robocombo | 30,50 | 5 |  |
| 56 | Silikon kablo 12 AWG | S62 | Robocombo | 118,00 | 2 | 2 satıra bölünür |
|  |  | S63 | Robocombo | 118,00 | 2 |  |
| 57 | Silikon kablo 18 AWG | S42 | Motorobit | 42,84 | 7 | 2 satıra bölünür |
|  |  | S43 | Motorobit | 42,84 | 7 |  |
| 58 | Kondansatör | S33 | Motorobit | 4,28 | 4 |  |
| 59 | Hızlı klemens | S29 | Motorobit | 12,24 | 10 | 10 adet tekli |
| 60 | Makaron seti | S34 | Motorobit | 116,28 | 1 |  |
| 62 | USB-C güç ucu | S48 | Motorobit | 153,00 | 1 |  |
| 63 | TVS diyot | S15 | Direnc.net | 6,05 | 2 | 2 satıra bölünür |
|  |  | S46 | Motorobit | 16,52 | 1 |  |
| 64 | Optokuplör modülü | S86 | Robotistan | 74,10 | 1 |  |
| 65 | Röle sürücü MOSFET | S87 | Robotistan | 24,40 | 2 |  |
| 66 | Röle K1 | S39 | Motorobit | 183,60 | 1 |  |
| 68 | Ön şarj rölesi K2 (E9) | S14 | Direnc.net | 19,36 | 1 |  |
| 69 | Ön şarj direnci (E9) | S13 | Direnc.net | 9,98 | 1 |  |
| 70 | XT60 şarj girişi tutucusu | S49 | Motorobit | 61,20 | 1 |  |
| 72 | Diyot | S24 | Motorobit | 0,61 | 2 | 2 satıra bölünür |
|  |  | S25 | Motorobit | 1,22 | 1 |  |
| 73 | Direnç seti | S55 | Robocombo | 90,50 | 1 |  |
| 74 | Delikli pertinaks | S8 | Direnc.net | 24,20 | 5 |  |
| 75 | Klemens ve pin header | S59 | Robocombo | 5,50 | 4 | 3 satıra bölünür |
|  |  | S26 | Motorobit | 4,28 | 2 |  |
|  |  | S57 | Robocombo | 6,50 | 1 |  |
| 76 | Silikon kablo 16 AWG | S64 | Robocombo | 60,50 | 1 | 2 satıra bölünür |
|  |  | S65 | Robocombo | 60,50 | 1 |  |
| 77 | Hat sigortası yuvası | S27 | Motorobit | 36,72 | 5 |  |
| 78 | Bıçak sigorta (ek) | S35 | Motorobit | 7,34 | 1 | 6 satıra bölünür |
|  |  | S36 | Motorobit | 7,34 | 1 |  |
|  |  | S37 | Motorobit | 7,34 | 2 |  |
|  |  | S38 | Motorobit | 7,34 | 1 |  |
|  |  | S44 | Motorobit | 4,28 | 1 |  |
|  |  | S45 | Motorobit | 4,28 | 1 |  |
| 79 | ESP32 – Pi USB kablosu | S58 | Robocombo | 75,50 | 2 |  |
| 105 | Kart burcu seti | S82 | Robotistan | 1,83 | 48 | set değil, 48 adet tekli |
| 106 | M2,5 pirinç distans seti | S12 | Direnc.net | 65,33 | 1 |  |
| 120 | Cırt kayış | S23 | Motorobit | 52,02 | 4 |  |
| 121 | Kablo bağı ve yapışkanlı taban | S10 | Direnc.net | 27,95 | 1 | 2 satıra bölünür |
|  |  | S32 | Motorobit | 31,82 | 10 |  |
| 126 | Yedek motor sürücü | S85 | Robotistan | 265,30 | 1 | S85'in yedeği: 1 |

## 6. Karar taslakları (karar Ahmet'in; panoya yazılmadı)

Düzeltme turu 1'de KT1–KT9, kontrolün 12 maddelik listesiyle (`F8a-kontrol.md` §5) birleştirildi; tek liste `F8a-siparis.md` §9'da (14 madde, öneri dilinde). Eşleme: KT1 → 1, KT2 → 3, KT3 → 4, KT4 → 5, KT5 → 12, KT6 → 6, KT7 → 13, KT8 → 14, KT9 → 7. Kontrolün 2, 8, 9, 10, 11. maddeleri yeni. Eski metinler aşağıda kayıt için; KT2 ve KT9 düzeltildi.

- **KT1 Hocadaki liste hangisi?:** Brief 17.10 Excel diyor; `tubitak-2209b/BAGLAM.md:221-222` v4'ün (03.11) hocanın öğrencisine gittiğini ve beğenildiğini yazıyor, `rapor.md:4` 'gönderilmedi' diyor. Öneri: v4 hocada sayılsın; fark tablosu 2.2 (8 ekleme, 1 satıcı, 1 model değişikliği) iletilsin.
- **KT2 Erken alım:** Bugün 1.515,90 TL (plan 1.496,37; +19,53). Insert 176 ise 1.558,22. Satıcılar onaylı listede değil (Rulmanal, Rhino3DPrinter, paslanmazcivata.ist): okul siparişi mi kişisel alım mı, Ahmet karar verir. Öneri (düzeltildi): 168 bu hafta (plan, `proje-plani.md:71, 119`), fark 8 P4.3'te; insert varyantı sipariş §4.1.
- **KT3 Akü:** Atakale 'özel sipariş, 7 gün'. Öneri: akü siparişi S'de (16.11) ya da erken alımla birlikte; 2b dalı 1–2 hf + 7 gün tedarik + kargo. Tek stok, ikinci onaylı satıcı yok.
- **KT4 QLED stok 2:** Robotistan stok 2 (v4'te 4). Bitmesi hâlinde Motorobit 15.300 (+8.082). Öneri: S'de ilk sipariş partisine al.
- **KT5 Tırtıllı somun M5:** Robotistan tükendi. Öneri: CNC Marketi (M6 somun, sigma ve köşe bağlantılarla aynı sipariş; zaten onaylı listede değil).
- **KT6 K4c, K4f bulunamadı:** Onaylı sitelerde L USB-A dirsek ve L 3,5 mm kısa kablo yok. Seçenek: düz kablo + baskı yönlendirme (yarıçap kontrolü P4.1/P6.1), ya da onaylı dışı satıcı. Öneri: P4.2'de kablo yarıçapıyla yeniden bak.
- **KT7 8 Ω hoparlör (PAKET A):** Robotistan stok 1 < 3 ve fiyat 0,00 görünüyor. PAKET A için ikinci satıcı ya da adet düşürme gerekebilir (bu paketin kapsamı dışında, not).
- **KT8 Kamera:** Module 3 her yerde tükendi; v4 notu 'gelmezse NoIR'. NoIR Module 3 de Robotistan'da tükendi (arama). Kritik yolda değil.
- **KT9 K9 b maliyeti:** Pay ≥ 1 dirsek DS3218MG +2.332,50; pay ≥ 2 omuz için 6–8,4 V'ta stoklu yeterli servo yok (80/150 kg tükendi; 220 kg yalnız 24 V) (60 kg·cm < 62,4). Varsayılan a (≤ 100 g) ile 0 TL.

## 7. Fark edilen sorunlar (dokunulmadı)

- `maliyet.json` gövdesi 29.10 (1,65 m) listesi + F4a'nın 09.11 kısmi eklemeleri; 158 kalemleri (11,6", QLED, ReSpeaker v2.0, D24V50F5, kafa kabloları) yalnız v4'te. `maliyet.json` toplamı 158 için doğru değil (köprü: sipariş §7).
- 90° HDMI ve 90° micro USB `fiyat_bekliyor` satırları `g: ses` grubunda (öneri 2).
- 90° HDMI adaptör hem v4 satır 28'de hem `maliyet.json` F1b adayında: siparişte bir kez (F8a'da çift sayılmadı).
- Isıl gömme M3 168 (plan, `maliyet.json`) ↔ 176 (v4).
- v4 satır 76 notu 'Kasım indirimli fiyat, liste 8.112,99': QLED fiyatı indirim bitince yükselebilir.
- v4 satır 71 'Ana sigorta yuvası standart boy' Robotistan stok 41; ikinci satıcı olarak yalnız mini boy bulundu (12 AWG ana hatta uygun olmayabilir).
- Robotistan 'USB Kablo A - Micro B (Dik)' sayfasında kablo boyu yazmıyor; göğüs dokunmatiği için 640 mm gerekiyor.
- 90° DC jak ölçüsü (5,5×2,1 / 5,5×2,5) göğüs ekranı için doğrulanmadı (v4 raporu da aynı notu düşmüş).
- `tubitak-2209b/malzeme-listesi/rapor.md:4` 'Liste gönderilmedi' ↔ `BAGLAM.md:222` 'beğendi' çelişkisi.
- Kanal 10 M5 T-somun: Robotistan sayfasında kanal ölçüsü yazmıyordu (v4 notu); CNC Marketi sayfası kanal 10 diyor.
- CAD'in M3 insert boyu (5,7) Türk satıcılarda yok; kupon delikleri buna göre (sipariş §4.1). M5 kupon delikleri (Ø6,2–6,6) Rhino OD7 kuralının (Ø6,7–6,8) altında.
- `maliyet.json` M6×16 satırının 'fosfat' şartının kaynağı yok; CNC'de M6×12/16/20 fosfat allen stoğu bitiyor.
- Limacell 30 A sürekli deşarj sınırı ile motor tepe akımı ve 30 A ana sigorta uyumu doğrulanmadı (yalnız akü yedeği seçilirse önemli).

## 8. Sınırlar

- Kargo taşıma süreleri sayfalarda yok; yalnız 'kargoya veriliş' metinleri yazıldı. Takvimde 1–3 iş günü **varsayım** (akü takvimi sipariş §3.1 dahil).
- Varyant fiyatları (insert OD/L, vida boyu) sepete eklemeden görünmüyor; sepete eklenmedi.
- Stok adedi Direnc'te çoğu üründe gösterilmiyor ('stokta, adet yok'). Robotistan adedi arama sayfasından; ürün sayfasıyla aynı an değil (aynı saat).
- Fiyatlar sipariş günü değişebilir (özellikle Robocombo indirimli fiyatları: DS3235 1.809 / liste 1.930, IMAX 1.809 / 2.110,50, Sandisk 995 / 1.146).
- Hizmet tutarları (14.390) v4 tahmini; teklif alınmadı.
- F2 bekliyor: omuz durdurucu (baskı parçası) ve olası vida/somun bu pakete girmedi; P4.3/P8.2'de eklenir.

## 9. Düzeltme turu 1 (09.11.2026; kontrol `F8a-kontrol.md`, KOŞULLU)

| Madde | Ne yapıldı | Yer |
|---|---|---|
| 3.1/1 md:24 kıyas | 'fark 4.643,42' kaldırıldı; aynı esasla kıyas: okul × 1,15 107.569,14, kararsız hariç × 1,15 107.119,16, 78.023,96'ya göre +29.545,18 | sipariş §1 |
| 3.1/2–3 köprü 471/472 | '− filament −6.843,09' ve '− lazer + bükme −2.840,00' satırları; hizmetler aşağıda geri ekleniyor | sipariş §7 |
| 3.1/4 köprü 475 | 'yukarıda elde kalemlerle düşüldü' | sipariş §7 |
| 3.1/5 'Diğer' | 'Kalıntı: köprü toplamından geri hesaplandı, kalem kalem ayrıştırılmadı.' | sipariş §7 |
| 3.1/6 köprü sonuç cümlesi | Aynı esasla: +29.545,18; elde dahil 116.845,70 ↔ 102.919,71 → +13.925,99 | sipariş §7 |
| 3.1/7 A151 | birincil 'stok 2 (gereken 18)', durum 'Stok yetmez: ikinci satıcı gerekli', JSON `stok_adet` 2; ikinci satıcı eklendi (D2) | sipariş §3, §5.4 |
| 3.1/8 K9 b pay ≥ 2 | not sütununa RDS5180/RDS51150 tükendi, DES220 24 V; ifade '6–8,4 V'ta stoklu servo yok (80/150 kg tükendi, 220 kg 24 V)' | sipariş §6, §9; günlük KT9 |
| 3.1/9 öneri 2 | parantez düzeltildi | günlük §5 |
| 3.1/10 Victron ikinci satıcı | Limacell satırı kontrolün metniyle | günlük §3 |
| 3.1/11 insert notu | 'Sayfada L 5,7 varyantı yok …' | sipariş §4, §5.4 |
| 3.1/12 başlık | 'doğrulanmamış ve K4 dahil' | sipariş §1, §7 |
| D1 kargo/stok | CNC (132 TL, 2.400 eşik, stok adetleri), Rhino (139 TL, 2.500), paslanmazcivata.ist (aynı gün kargo, 2.000; ürün stoğu), Rulmanal (16:00, 2.500), Otomasyoncu (sayfada yok); §8'e kargo ücreti sütunu, JSON `kargo_ucreti` | sipariş §3, §4, §8 |
| D2 M6×16 | ikinci satıcı paslanmaz DIN 912 A2 3,89 (kısmen); muadil CNC bombe başlı 4,80 stok 235; tutar +5,22 | sipariş §1, §3, §5.4, §9/11 |
| D3 insert | Rhino'da L 5,7 yok; seçenekler A (OD4 L4), B (OD5 L6), C (ruthex, yurt dışı); karar Ahmet'in; KT2 → '168 bu hafta, fark 8 P4.3'te' | sipariş §4.1, §9/3 |
| D4 akü | Limacell sayfadan doğrulandı (4.814,86, InStock, 3 iş günü, 12 Kasım kargoda); S5 ikinci satıcı; takvim tablosu | sipariş §3.1, §9/4 |
| D5 / öneriler 1, 8, 10, 12, 13, 16, 17, 18, 20 | satır satır hedef (1), koşullu (8, 20), geri çekildi (10, 13 fiyat), kargo satıcı başına (12), alt açık (16, 17), eşleme tablosu (18) | günlük §5, §5.1 |
| Kontrol §1/6 JSON | `toplamlar`a `kosullu_dahil_pay15`, `kararsiz_haric_pay15`, `fark_alinacaklar`, `fark_elde_dahil` | sipariş JSON |
| Kontrol §1/7 | '29.10 listesi + F4a'nın 09.11 kısmi eklemeleri' | sipariş giriş, §7; günlük §1, §7 |
| Kontrol §1/13 K4 | K4 a: 'koşullu = genel toplam dışı (0); satın alınırsa +391,28' | sipariş §6; JSON `karar_bagli_etki.K4` |
| Karar listesi | KT1–KT9 + kontrol §5 → 14 madde, öneri dilinde | sipariş §9 |

Toplam etkisi: okul bütçesi 93.533,16 → 93.538,38 (+5,22, yalnız M6×16 ikinci satıcı). Erken alım tutarı değişmedi (1.515,90); Rhino kargosuyla 1.654,90.

Kontrol (sipariş verilmedi): sepete ekleme, giriş, satıcıya yazma yok; FreeCAD açılmadı (`tolerans_kuponu.py` yalnız metin olarak okundu); `maliyet.json`, `karar-kuyrugu.md`, `proje-plani.md` değişmedi.
