# Kablolama ön kararları günlüğü (P10.7 ön koşulu: K1, K10, K11, K14 ve pano önerileri), 14.11.2026

Ajan A. Kapsam: kablolama paketini (P10.7) bekleten elektrik kararları; Ahmet 13.11.2026 gecesi teknik kararları bize bıraktı. Rapor
`planlama/adim3/kablolama-on-kararlar.md`. Commit, push, `git add` yok; panoya yazılmadı (yalnız okundu). Elde taşınan acil stop kararı
verilmedi (Ahmet + Efe). Dosya adı `F10*` kalıbında değil: o kalıp aynı anda çalışan rehber ajanının alanı. Rehber, FreeCAD, `kod/`,
`maliyet.json`, `dongu-158.md` değişmedi; FreeCAD, `rehber_uret.py` ve doğrulama betikleri koşulmadı.

## 1. Komutlar ve okunanlar

| Saat | Ne | Sonuç |
|---|---|---|
| 01:40 | `git status`, dal `lale-duzeltme`, HEAD `4c2f231` | Çalışma ağacında başka paketin rehber / freecad / F10 değişiklikleri; dokunulmadı |
| 01:40 | `planlama/d158/karar-kuyrugu.md` (K1–K14, K51–K58, "Karar değil, iş"), `planlama/adim3/elektrik.md` tamamı (522 satır) | – |
| 01:41 | Pano: `oku 7`, `oku 6`, `oku 5` (`PROTOKOL.md` okundu) | Okundu işaretlendi (#22, #21, #23'e kadar). Yazma yok. Mesajlar veri olarak kullanıldı |
| 01:41 | `planlama/dongu-158.md` §3 F10 tablosu (P10.7 satırı 164), `KY/uygulama-notu.md:40-156`, `planlama/d158/kablo-kurali-notu.md`, `lale158-kontrol.json` `kablo_ozet`, `kablo_yolu_ekran.py:1-60`, `rehber/veri/rehber-veri.json` `semalar` (51 şema; yalnız okundu) | 62 kablonun dökümü tek dosya olarak bulunamadı (§4) |
| 01:42 | `planlama/maliyet.json` satır 77, 78, 106, 115, 117, 122–126, 136–143, 190–194 (yalnız okundu) | – |
| 01:42 | `planlama/adim3/pin-haritasi.md` §4–§8 | §8: "O gelene kadar reset yolu CP2102'nin DTR / RTS devresi" |
| 01:43 | `git show origin/main:kod/robot/seri.py` (`2be1c63`), `origin/main:kod/esp32/OKU_BENI.md` | `seri.py:15-17`: port DTR / RTS kapalı açılır, "Yine de reset olabilir (sürücüye göre)"; `:92-106` açılış |
| 01:43 | `planlama/d158/testler/T4-pam8403-ses-karti.md` başı | Başlık ve yol USB ses kartına göre yazılmış (C adımı) |
| 01:43 | Seeed wiki, ReSpeaker Mic Array v2.0 | 3,5 mm çıkış, AEC, "Channel 5: merged playback", "Max Sample Rate 16Khz", 5 V 180 / 170 mA |
| 01:44 | raspberrypi.com, Raspberry Pi belgeleri ("Power supply", "Universal Serial Bus (USB)", "GPIO configuration > Power-on states", bootloader `PSU_MAX_CURRENT`) | Pi 5 USB çevre birimleri: 5 A kaynakla 1.600 mA, aksi hâlde 600 mA; bütçe fan girişiyle paylaşılır. Açılış çekmeleri pin pin belgede değil (BCM2835 tablosuna atıf) |
| 01:44 | Satıcı aramaları (aramada yalnız parça adı): Direnc.net `AO3400`, `IRLML6344`, `sot23 adaptor`, "SMD - DIP Çevirici" kategorisi; Motorobit `sot23`; genel web araması | AO3400A: Direnc.net'te 0 ürün; IRLML6344TRPBF 8,56 TL stokta; SOT-23 adaptörü onaylı satıcılarda yok |
| 01:45 | Saat (`Get-Date`): 2026-11-14 01:45 | – |

## 2. Neye dayandım (ölçüm değil, belge ve hesap)

- **Hiçbir şey ölçülmedi.** Akımlar `elektrik.md` ve `KY/uygulama-notu.md` hesapları, üretici sayfası (ReSpeaker 180 mA) ve bir varsayım
  (göğüs regülatörü verimi %80). Kablo çapları CAD'in tahmini çapları.
- Acil stopta neyin enerjili kaldığı `elektrik.md` sigorta dalları (satır 91) ve blok şemadan (satır 323–339) çıkarıldı; rapor §12.
- Boyun kesit oranları LK `gecis` ve `boyun_demet_alan_mm2`'den; yeniden hesaplanmadı (yalnız toplam elle sınandı: 10,6 + 5,9 + 28,3 + 12,6 + 12,6 = 70,0 ≈ 69,9).

## 3. Karar özeti

| # | Karar | Sapma |
|---|---|---|
| K1 | a; 4 cihaz (ses kararıyla) | – |
| K10 | a, D24V50F5 | – |
| K11 | a, ana anahtar sonrası, röle öncesi; acil stopta ekran açık | – |
| K14 | a, CAD'deki 5 kablo, şartlı | – |
| Ö1 | ReSpeaker 3,5 mm → PAM8403 kabul; ses kartı yedek | – |
| Ö2 | Hub harici besleme yok | Efe'nin önerisinden |
| Ö3 | Yeni reset teli yok; DTR / RTS devresiyle bilinçli reset | Efe'nin önerisinden (Efe'ye soru) |
| Ö4 | Karar yok (Ahmet + Efe); seçenekler + köprülü klemens önerisi | – |

Kablo: 62 → 61. Boyun: değişmedi. Maliyet: genel 0 (+7,34 koşulu), koşullu −77,46; MOSFET satırı satıcıyla.

## 4. Açık kalanlar

- **62 kablonun dökümü:** sayı `dongu-158.md:259` (10.11 rehber dökümü) ve `:164`'ten; listesi depoda bulunamadı. Raporun §11'i farkı
  dökümden bağımsız verir (−1: ses kartı uzatması). Tablo yazılırken döküm yeniden kurulmalı.
- **Yeni 3,5 mm kablonun yolu ve boyu** (ReSpeaker jakı → PAM): CAD'de ölçülmedi; jakın kart üstündeki yönü bilinmiyor.
- **AO3400A ve SOT-23 adaptörü:** onaylı satıcılarda bulunamadı. IRLML6344 PH D9'a göre yalnız T2 sonucuna bağlı.
- **Göğüs regülatörü verimi** kaynakta yok (%80 varsayım); mini 2 A'nın açılış akımına dayanımı ölçülmedi.
- **ReSpeaker çıkış seviyesi ↔ PAM8403 girişi** ve modülde ses ayarı olup olmadığı doğrulanmadı.
- **ESP32'nin hub VBUS'undan çektiği akım** ölçülmedi (diyotlu VEYA'dan çıkarım).
- **Efe'nin cevabı** (reset dizisi, 16 kHz) bekleniyor; taslak depo dışında, gönderilmedi.
- Kablajda teyit listesi: rapor §13 (KT1–KT7).

## 5. C adımında yapılacak

1. `karar-kuyrugu.md` özet tablosu: K1, K10, K11, K14 "kapandı" (kontrol geçince); sayım satırı (`Açık: 52 … Kapandı: 6`) buna göre;
   bu pakette yalnız dört "Durum" satırı ve "yeni sorular" kaydı yazıldı. K56, K57, K58 ve P10.5b satırlarına dokunulmadı.
2. `planlama/dongu-158.md` P10.7 satırının durum sütunu (öneri metni):
   > ⛔ → 🔄 ön kararlar verildi (14.11; K1 a, K10 a, K11 a, K14 a; ses ReSpeaker çıkışından, hub USB beslemeli, reset teli yok; elde acil stop
   > Ahmet + Efe'de; `planlama/adim3/kablolama-on-kararlar.md`). Kalan: kablo tablosu (62 → 61), MOSFET satıcısı (AO3400A bulunamadı),
   > rehber `rehber_metin.py:637` uyarısı; T1–T8 ve KT1–KT7 kablajda.
3. `planlama/dongu-158.md` §5 girdisi (öneri metni; saat C adımında saatten okunur):
   > - 2026-11-14 HH:MM **P10.7 ön kararları (A bitti, kontrol bekliyor).** Ahmet'in 13.11 yetkilendirmesiyle: K1 a (4 USB cihazı), K10 a
   >   (PAM D24V50F5), K11 a (göğüs ekranı röle öncesi, acil stopta açık), K14 a (boyun 5 kablo, şartlı). Pano önerileri: ses ReSpeaker
   >   3,5 mm → PAM kabul (ses kartı yedek), hub harici besleme hayır, Pi → ESP32 reset teli yok (DTR / RTS; Efe'ye soru), elde acil stop
   >   kararı Ahmet + Efe. Kablo 62 → 61, boyun değişmedi; maliyet genel 0, koşullu −77,46 TL. Rapor `planlama/adim3/kablolama-on-kararlar.md`,
   >   günlük `planlama/d158/kablolama-onkarar-gunluk.md`.
4. `planlama/maliyet.json` (sahibi): MJ:106 (AO3400A / IRLML6344, adet 3), SOT-23 adaptör satırı, MJ:136 ve MJ:138 (ses kartı uzatması ve L
   dirsek çıkar), MJ:141 (3,5 mm kablo: ReSpeaker → PAM, boy CAD'den), MJ:77–78 notları (ses kartı yedek), MJ:106 / 109 "GPIO2" → GPIO19,
   MJ:123 notu (göğüs dalı).
5. `planlama/d158/testler/T4-pam8403-ses-karti.md`: başlık ve "Amaç" yolu (ReSpeaker 3,5 mm → PAM), K10 karar satırı; `testler.html` üretimi.
6. `elektrik.md:<satır>` atıfları: satır sayısı değişmedi (522 → 522), atıf listesi gerekmiyor. İçeriği değişen satırlar: 26, 28, 36, 37, 48,
   52–54, 62, 63, 68, 74, 79, 86–88, 264, 275, 305, 334, 335, 337, 348, 371, 518–520. Bu satır numaralarına içerik için atıf yapan belge
   (ör. `KK` K10 "`elektrik.md:24`", K11 "`elektrik.md:55`") eski numaralandırmaya ait; C adımı yalnız anlam değiştiyse düzeltir.
7. Pano: Efe'ye taslak (depo dışında) Ahmet onayıyla gönderilir.

(Madde 2–4 ve 6'nın güncel hâli §6.5'te; düzeltme turu 1 onları değiştirdi.)

## 6. Düzeltme turu 1 (14.11.2026, 02:13–02:26)

Girdi: bağımsız kontrol `planlama/d158/kablolama-onkarar-kontrol.md` (DÜZELTME GEREKLİ: D1 K10 payı, D2 K11 sigorta yeri, D3 BC337 yedeği;
bulgu 1–10) ve orkestratörün düzeltme kararları (D1, D2, röle sürücüsü kabul, bulgu 1–10). Sınırlar aynı; K56 / K57 / P10.5b'ye dokunulmadı,
K58'e yalnız bir satır not.

**Kayıt dışı olay:** bu paketin ilk turunda `karar-kuyrugu.md`'ye yazılan Durum satırları ve "Kayıt" bloğu, aynı çalışma ağacında başka bir
işin commit'ine (`b1c2a8d`, 14.11 02:11, P10.5b) girmiş; bu paket commit yapmadı. Düzeltme turunun kuyruk değişiklikleri commit'lenmedi.

### 6.1 Yapılan

| Kontrol / karar | Yapılan | Dosya |
|---|---|---|
| D1 (K10) | "%32 pay" kalktı; 5 V bütçesi kalem kalem (Pi tam yük 2,40, ReSpeaker 0,18, hub 0,13, QLED Touch ~0,05, kamera 0,14, PAM 0,71 ≈ 3,61 A, %72; AI HAT+ resmî olmayan değerle 4,11–4,51 A, %82–90); karar "a, masa denemesine bağlı" (KT1: uyarı yok, ≲ 4 A); geçmezse b (SY8205 1,61 A, %44; kablo yine tek, uç SY8205, küçük sigorta); AI HAT+ siparişi denemeye bağlı | rapor §2, EL:28, :48, :52-54, :334, :348, KK K10 |
| D2 (K11) | Seçenek (i): kutunun 6. yuvası F6, standart bıçak; korumasız ara kablo ve hat yuvası kalktı; sigorta 3 A (ekran en çok 1 A → 10 V'ta 1,50 A = %50; 2 A'de %75); ana anahtar kapalıyken kesilir; K8 notu | rapor §3, EL:26, :41, :62, :68, :91, :337, :349, :371, :377, :380, :519, KK K11 |
| Röle sürücüsü (D3) | BC337-40 + 270 Ω + 4,7 kΩ + 1N4007; PH sürüm 4 (D1, D9, §3.1, T2, §9 donanım notu, BJT kaynak satırı, bağlı "gate" → "taban" sözcükleri); EL E3 / E9 / blok şema / pin satırları 4 ve 19 (yalnız ifade) / :106 / :143 / :306 / :507; KK K58 tek satır not | PH, EL, KK |
| Bulgu 1–3 (ses) | "masa denemesine bağlı kabul"; KT2'ye kılıf ↔ USB GND sürekliliği ve ses tavanı (giriş bölücüsü 10 kΩ / 2,7 kΩ); AEC cümlesi çıkarım olarak işaretli; yedek açık (USB ses kartı, Pi port 2) | rapor §5, §13, EL:28, :36, :79, KK kayıt |
| Bulgu 4 (K16) | "14.11: ses yolu değişti" notu, Ahmet'in 04.11 seçimini değiştirdiği açık | KK K16, EL:145 |
| Bulgu 5 (K14) | alınacak kablo şartı (Ø ≤ 6; MJ:191'in çapı bilinmiyor); fiş geçişi: kanal 20 × 7,8, fiş ≲ 7 mm, micro HDMI ucu aşağıdan yukarı, HDMI A ucu gövdede, sıra HDMI → hub uzatması → tilt → fişsiz hoparlör ve 12 V | rapor §4, EL:37, :63, :518, KK K14 |
| Bulgu 6 (reset) | karar aynı; demet bağlanmadan Efe'nin iki cevabı; bükümlü çift etkisi (%44,8 → ≈ %46); port açılış riski (DTR bırakık / RTS etkin anı EN'i LOW çeker); KT6'ya servis yeniden başlatma / yeniden açılış | rapor §7, §13, EL:264, KK K14 ve kayıt |
| Bulgu 7 (hub) | F4 atarsa hub ≈ 0,37 A, Pi USB ≈ 0,6 A; ayar adları `PSU_MAX_CURRENT=5000` / `usb_max_current_enable=1` | rapor §6, EL:87-88, :520 |
| Bulgu 8 (pano taslağı) | "kapattık" → "karar verdik (bağımsız kontrol bekliyor)"; BC337 / K1 / hub / reset bilgisi. Gönderilmedi | depo dışı taslak |
| Bulgu 9–10 | servo kondansatörü notu (8,8 mF ≈ 0,16 J, kısa son servo hareketi; bu paketten eski); 62 kablonun listesi depoda yok, P10.7'de yeniden kurulur | rapor §11, §12, EL:515 |

### 6.2 Hesaplar (sayılar; hepsi hesap, ölçüm değil)

- **BC337-40 (Vishay Doc. 85112 Rev. 1.2):** I_B en kötü (VOH 2,64 V, VBE 1,2 V) 5,08 mA, VBE 1,0 V ile 5,86 mA, tipik 9,09 mA. Zorunlu β K1
  (0,17 A) 33,5 / 29,0 / 18,7; K2 (0,03 A) 5,9 / 5,1 / 3,3. hFE en az 250 (100 mA), ≈ 170 (300 mA, BC338-40 vekil). GPIO en çok 9,8 mA
  (3,3 V) / 10,9 mA (3,6 V). VCE(sat) belgede yalnız 0,7 V @ 500 / 50 mA; K1 kaybı 34 / 51 / 119 mW (VCE 0,2 / 0,3 / 0,7 V), ≈ 25 K ısınma,
  60 °C'de izin 0,45 W. Bobin 11 V barada en kötü 10,3 V.
- **Boşta:** taban 0,31 / 0,35 / 0,49 V. Kollektör akımı iki modelle (1 mA'de VBE 0,60 / 0,55 V, −2 mV / K): 0,31 V'ta 70 °C ≤ 6,3 µA;
  0,49 V'ta 25 °C 14–97 µA, 60 °C 0,25–1,4 mA, 70 °C 0,5–2,8 mA. Çekme akımı (yaygın %75 oranı) K1 ≈ 110, K2 ≈ 22 mA → en kötü köşede ≈ 40 / 8 kat
  pay. T2 ölçütü: bobin akımı ≤ 1 mA, kontak hiç kapanmıyor; aşılırsa 4,7 kΩ → 2,2 kΩ (I_B yine ≈ 4,8 mA).
- **K10:** 3,61 A (%72); AI HAT+ ile 4,11 / 4,51 A; b'de SY8205 1,61 A (%44); PAM sinüs tepesi anlık ≈ 1,4 A.
- **K11:** ekran 12 W, verim %80 → 15 W: 10 V 1,50 A, 12,8 V 1,17 A, 14,6 V 1,03 A; tipik 0,59 / 0,75 A. 3 A'de en kötü %50.
- **Ses tavanı:** 3 W / 4 Ω → 3,46 V rms; PAM 24 dB (× 15,85) → giriş 0,22 V rms. Bölücü 10 kΩ / 2,7 kΩ: 0,213 (sonsuz yük) – 0,190
  (18 kΩ yük); 1 V rms varsayımıyla çıkış 2,3–2,9 W.
- **Hub:** normal 0,13 A; F4 atarsa 0,37 A; Pi USB toplamı ≈ 0,6 A.
- **Boyun:** bükümlü çift eklenirse 69,9 → ≈ 72 mm², servo kanalı ≈ %46, mil penceresi ≈ %41, alt çıkış ≈ %35.
- **Maliyet:** BC337-40 ×3 (9,06) − IRLZ44N ×2 (48,80) = −39,74; hat yuvası −36,72; genel −76,46 + 3 A sigorta (fiyat bekliyor); koşullu −77,46.

### 6.3 Kaynaklar ve komutlar

- Vishay BC337 / BC338 veri sayfası (Doc. 85112 Rev. 1.2): üretici sitesinden indirildi, depo dışında ayrı klasörde, PyMuPDF ile yalıtılmış
  Python'da okundu. Direnç seti ve sigorta kutusu satıcı sayfaları (Robocombo, Motorobit, 14.11). PAM8403: Diodes veri sayfası / uygulama notu
  (arama sonucu: en çok 24 dB, Ri en az 18 kΩ; giriş empedansı sayıyla bulunamadı).
- Pin tablosu sınaması (depo dışı betik, `git show HEAD:` ile karşılaştırır): PH §2 HEAD ↔ çalışma **aynı (25 pin)**, PH §9 JSON HEAD ↔ çalışma
  **aynı**, EL pin planı HEAD ↔ çalışma **aynı**, çalışmada PH §2 ↔ JSON ↔ EL **aynı**; JSON `surum` 3 → 4. Sonuç GEÇER.
- `elektrik.md` satır sayısı 522 → 522. İçeriği bu turda değişen satırlar (HEAD'e göre, iki turun toplamı): 26, 28, 36–37, 41, 48, 52–54,
  62–63, 68, 74, 79, 86–88, 91, 106, 143, 145, 249–251, 259, 264, 268, 275, 305–306, 334–335, 337, 339, 348–349, 371, 377, 380, 443–444,
  446, 483–484, 507, 515, 518–520.

### 6.4 Hâlâ doğrulanamayanlar

- BC337'nin 1 mA'deki VBE'si ve VCE(sat)'ın 170 mA'deki değeri (belgede sayı yok); rölelerin çekme / bırakma akımları (MAH-112-C, JQC-3FF
  belgesiz); T2 ölçer.
- AI HAT+ gücü (resmî değer yok); D24V50F5'in 12 V girişte sürekli akımı (EL açık iş 8).
- Kutunun yuvalarının ortak girişli olduğu; standart 3 A bıçak sigortanın satıcısı ve fiyatı.
- ReSpeaker kulaklık çıkışının seviyesi ve kılıfın toprak olup olmadığı; PAM8403 giriş empedansı; kartta ses ayarı; 10 kΩ / 2,7 kΩ'un sette olduğu.
- HDMI (MJ:191) ve USB-A uzatma fişlerinin ölçüleri; servo kanalının yandan açılıp açılmadığı (CAD); fiş geçiş sırası buna bağlı.
- Efe'nin cevapları (reset, 16 kHz). 62 kablonun listesi (P10.7'de yeniden).

### 6.5 C / P10.7'de girecek (güncel liste; §5'in 2–4 ve 6. maddelerinin yerine)

1. `karar-kuyrugu.md` özet tablosu ve sayım (kontrol geçince); K10 "denemeye bağlı" olarak.
2. `planlama/dongu-158.md` P10.7 satırı ve §5 girdisi: §5'teki öneri metni şu farklarla: K10 a masa denemesine bağlı (b yedek), K11 a = kutunun
   F6 3 A yuvası, ses "masa denemesine bağlı kabul", röle sürücüsü BC337-40 (PH sürüm 4), maliyet genel −76,46 + 3 A sigorta, koşullu −77,46,
   "MOSFET satıcısı" kalanı kalkar.
3. `planlama/maliyet.json` (sahibi):
   - MJ:106 IRLZ44N ×2 → **BC337-40 ×3** (2 + 1 yedek), Direnc.net BC337-40TA 3,02 TL (−39,74 TL); SOT-23 adaptör / AO3400A satırı açılmaz.
   - MJ:115 direnç seti notu: "MOSFET gate" → "BC337 tabanı 270 Ω (setin sayfasında var) + 4,7 kΩ"; ses bölücüsü 10 kΩ / 2,7 kΩ.
   - MJ:122 hat sigortası yuvası **adet 5 → 4** (−36,72 TL), not: göğüs ekranı kutunun F6 yuvasına geçti.
   - **Standart 3 A bıçak sigorta +1** (F6; fiyat bekliyor). MJ:123 / 124'ün "mini" modeli F4 / F5 için standart olmalı mı: sahibine soru.
   - MJ:136 ve MJ:138 (ses kartı uzatması ve L dirsek) koşullu satırdan çıkar; MJ:141 3,5 mm kablo (ReSpeaker → PAM, boy CAD'den); MJ:77–78
     notları (ses kartı yedek, ses ReSpeaker'dan, denemeye bağlı).
   - MJ:191 göğüs HDMI notu: "alınacak kablo şartı Ø ≤ 6 mm, micro HDMI fişi ≤ 7 mm kalın"; şartı karşılamazsa satır değişir.
   - MJ:106 / 109 notlarındaki "GPIO2" → GPIO19.
4. `planlama/d158/testler/T4-pam8403-ses-karti.md`: yol (ReSpeaker 3,5 mm → bölücü → PAM), KT1 (stres + en yüksek ses + AI HAT+, ≲ 4 A) ve KT2
   (süreklilik, seviye, bölücü) maddeleri.
5. `elektrik.md:<satır>` atıfları: satır sayısı değişmedi, atıf listesi gerekmez (içeriği değişen satırlar §6.3).
6. Pano: Efe'ye taslak (depo dışında, düzeltme turu 1'e göre güncellendi) Ahmet onayıyla gönderilir.

## 7. Düzeltme turu 2 (14.11.2026, 02:43–02:55)

Girdi: ikinci kontrol `planlama/d158/kablolama-onkarar-kontrol-2.md` (tek durduran bulgu D1: röle kapalı hâli ölçütü; on iki küçük bulgu) ve
orkestratörün kararları (D1, bulgu 1, 3–12, Madde 8 C listesi). Her hesap yeniden yapıldı; hepsi tuttu, **uygulanmayan karar yok**. Sınırlar
aynı; K56 / K57 / P10.5b'ye dokunulmadı, K58'de yalnız MOSFET'e bağlı satırlar (donanım, açık kalan, not, iş maddesi).

### 7.1 Yapılan

| Karar | Yapılan | Dosya |
|---|---|---|
| D1 (kapalı hâl) | Ölçüt: bobin gerilimi < bırakma garantisi 1,2 V (çekme akımının katı karşılaştırması kalktı). Taban → GND 4,7 kΩ → **2,2 kΩ** (iki röle; seri 270 Ω aynı). PH sürüm 4 kaldı, başlığa "14.11 düzeltme: taban-GND 2,2 kΩ" notu; D1, D9, §3.1, §4, satır 4 / 19, T2, §9 JSON `donanim`; yeni RÖ kaynak satırı (röle verisi, ikinci elden) | PH, EL:251, :259, :268, :483–484, rapor §9, PG §12 |
| Bulgu 3 | BC337-40: -40 sınıfı zorunlu, sınıfsız BC337 kabul edilmez; T2a: teslimde diyot testiyle ayak sırası (taban → E ve taban → C iletir); ters takılırsa ters β küçük, röle çekmez ya da VCE büyür, T2 yakalar | PH D9 / T2a, EL:268, rapor §9 |
| Bulgu 4 | T2 yedeği: çekişte VCE > 0,3 V ise seri 220 Ω, T2 yinelenir; T2 kapalı hâl ölçütü bobin gerilimi ≤ 0,12 V; T2 oda sıcaklığında, sıcak köşe payı yalnız hesap | PH T2, rapor §9, KT7 |
| Bulgu 1 (K14) | Karar aynı (5 kablo, CAD değişmez); hub uzatması USB 2.0, erkek fiş ≤ 13 × 7 mm, HDMI'den önce; kanal kapalı tünel, iki dik dönüş; siparişten önce baskı parçalarında elle fiş denemesi zorunlu; yedekler: fişsiz geçirip yeniden sonlandırma, şerit (FPC) HDMI + uç adaptörleri; MJ:137 / 191 değişecek kalem; "Ahmet'in bilmesi gereken risk" bölümü | rapor §4, §13 KT4, §14; EL:37, :518; KK K14 |
| Bulgu 5 | KT3: teslimde kutunun ortak giriş barası var mı; ayrı girişliyse 12 AWG köprüler, kısa, tek giriş klemensinden; "korumasız ara kablo yok" buna koşullu | rapor §3, KT3; EL:68, :380; KK K11 |
| Bulgu 6 | Kutu standart (ATO) bıçak alır; listedeki mini sigortalar kutu için yanlış tür; C: F5 2 A standart, ek 5 A standart, F6 3 A standart (yoksa 5 A standart; 18 AWG ile uyumlu) | rapor §3, §10, §14; EL:444; KK K11 |
| Bulgu 7 | KT1 yöntemi: akım DC pens ya da şönt (seri multimetre değil); Pi girişi `vcgencmd pmic_read_adc` EXT5V_V; düşük gerilim `vcgencmd get_throttled` (bit 0 ve 16; Raspberry Pi belgesiyle) | rapor §2, KT1; EL:53; KK K10 |
| Bulgu 8 | Ses bölücüsü başlangıç 10 kΩ / 2,2 kΩ (sette var; 2,7 kΩ yok); son değer KT2; güç hesabı bu değerle | rapor §5, §9, §11; KK kayıt |
| Bulgu 9 | Pano taslağı: T2 yöntemi (bobin gerilimi), GPIO 4 / 19 sürüş gücü düşürülmez (varsayılan 2, ESP-IDF kaynağından), 2,2 kΩ. Gönderilmedi | depo dışı taslak |
| Bulgu 10–12 | §6.1 tablosunda `pin-karari-gunluk.md` eksikti (aşağıda); rapor §16'ya eklendi. İlk açılış dolum notuna F6 regülatör kondansatörleri (EL:461). E9'da K2 = JQC-3FF-12VDC 10 A (MJ:109, Direnc.net 19,36 TL; `maliyet.json` okunarak) | EL:446, :461; rapor §16 |
| Madde 8 | KK: K1 / K10 / K11 / K14 Durum ve özet tablo metni "karar verildi, üçüncü bakış bekliyor"; sayım ("Açık: 50 … Kapandı: 8") ve "kapandı" işaretleri aynı; K58 MOSFET satırları BC337-40 ve 2,2 kΩ; K52 notu (F6, mini 2 A yok); C listesi §7.5 | KK |

**§6.1'e ek (bulgu 10):** düzeltme turu 1'de `planlama/d158/pin-karari-gunluk.md` §11 (sürüm 4) de yazılmıştı; tabloda yoktu. Bu turda §12 eklendi.

### 7.2 Hesaplar (sayılar; hepsi hesap, ölçüm değil)

- **Boşta (270 Ω + 2,2 kΩ):** taban 0,154 / 0,165 / 0,246 V (pin sızıntısı yok / tipik / en kötü varsayım). 70 °C'de kollektör sızıntısı
  0,13–0,72 µA → bobin K1 (85 Ω) ≤ 0,07 mV, K2 (400 Ω) ≤ 0,32 mV; belgedeki ICES sınırıyla (≤ 10 µA, 125 °C) K2 ≤ 4,4 mV. Bırakma sınırı
  1,2 V'un ≤ %0,4'ü. (4,7 kΩ ile en kötü köşede K2 ≈ 1,0–1,2 V idi: sınırda.)
- **Sürülürken:** I_B en kötü (VOH 2,64 V, VBE 1,2 V) 4,79 mA; VBE 1,0 V ile 5,62, 0,85 V ile 6,24, tipik 8,90 mA. Bobin K1 85 Ω ±%10:
  14,6 V / 76,5 Ω = 0,191 A, soğuk en kötü 0,21 A; K2 0,041–0,045 A. Zorunlu β K1 39,9 / 43,9, K2 8,6 / 9,4; hFE en az ≈ 170 @ 300 mA
  (BC338-40 vekil) → ≈ 3,9 kat aşırı sürüş [**C adımında düzeltildi, §8: belgeyle garanti pay ≈ 1,37×, VCE sınırı 1,0 V**]. GPIO akımı 9,8 (3,3 V) / 10,9 mA (3,6 V). K1 kaybı 42 / 63 / 147 mW (VCE 0,2 / 0,3 / 0,7 V),
  ≈ 31 K ısınma; 60 °C'de izin 0,45 W. Bobin 11 V barada en kötü 10,3 V (çekme garantisi ≤ 8,4 / 9,0 V).
- **220 Ω yedeği:** I_B en kötü 6,00 mA, β 32–35, GPIO 12,0 / 13,4 mA; ESP32 VOH ölçütü 40 mA'de tanımlı, içinde.
- **T2 ölçütü:** bobin ≤ 0,12 V (1,2 V'un %10'u); oda sıcaklığında, sıcak köşe payı hesaptan.
- **Ses bölücüsü 10 kΩ / 2,2 kΩ:** oran 0,180 (yüksüz) – 0,164 (18 kΩ yük); 1 V rms varsayımıyla PAM çıkışı 2,60–2,86 V rms → 4 Ω'da 1,7–2,0 W
  (3 W tavanın altında).
- **F6:** en kötü 1,5 A → 3 A'de %50, 5 A'de %30.
- **Maliyet:** genel −83,80 TL (tur 1'in −76,46'sı + MJ:123 2 A mini −7,34) + üç standart sigortanın fiyatı (+ MJ:191 değişirse); koşullu
  −77,46 TL + USB 2.0 uzatma farkı (MJ:137 214,20 TL yerine).

### 7.3 Kaynaklar ve komutlar

- ESP-IDF v4.4.7 `components/hal/include/hal/gpio_types.h`: `GPIO_DRIVE_CAP_DEFAULT = 2` ("medium"). Seviye başına mA değerleri kaynaktan
  okunmadı.
- Raspberry Pi belgesi (`vcgencmd`): `get_throttled` bit 0 (0x1) "Undervoltage detected", bit 16 (0x10000) "Undervoltage has occurred";
  `pmic_read_adc` yalnız Pi 5, EXT5V_V besleme gerilimi.
- Röle verisi (K1 MAH3 ailesi 85 Ω, çekme ≤ 8,4 V, bırakma ≥ 1,2 V; K2 JQC-3FF 400 Ω, ≤ 9,0 V, ≥ 1,2 V): kontrol-2'den, ikinci elden.
- BC337 / BC338 Vishay Doc. 85112 Rev. 1.2 (tur 1'de indirilmişti). PAM8403: 24 dB, Ri en az 18 kΩ (tur 1). CAD kanal ölçüsü
  `kafa7_parcalar.py:143-148` (kontrol-2 okuması).
- Pin tablosu sınaması yeniden koştu: PH §2, PH §9 JSON, EL pin planı HEAD ↔ çalışma ve birbiriyle **aynı (25 pin)**, JSON `surum` 4. **GEÇER.**
- `elektrik.md` satır sayısı 522 (değişmedi). Bu turda içeriği değişen satırlar: 37, 53, 68, 251, 259, 268, 380, 444, 446, 461, 483–484, 518.
- `git diff` ile K56 / K57 / P10.5b'de değişiklik yok; `tasarim/freecad` altındaki değişik görseller ve `yerlesim-kontrol.json` bu paketten
  önce de değişikti, bu pakete ait değil.

### 7.4 Hâlâ doğrulanamayanlar

- BC337'nin 1 mA'deki VBE'si ve 0,2 A'deki VCE(sat)'ı (belgede yok); röle verisinin üretici belgesi (ikinci elden); T2 / T2a ölçer.
- ESP32 sürüş gücü seviyelerinin mA karşılığı (kaynakta okunmadı).
- Kutunun ortak giriş barası; standart 3 A / 2 A / 5 A bıçak sigortanın satıcısı ve fiyatı.
- Fiş ölçüleri ve elle geçirme denemesi (MJ:137, MJ:191, alınacak USB 2.0 uzatma); şerit HDMI'de 1080p.
- ReSpeaker çıkış seviyesi, kılıfın toprak olup olmadığı, PAM8403 giriş devresi; bölücünün son değeri (KT2).
- AI HAT+ gücü; D24V50F5'in sürekli akımı. Efe'nin cevapları. 62 kablonun listesi (P10.7'de).

### 7.5 C / P10.7'de girecek (güncel liste; §6.5'in yerine)

1. `karar-kuyrugu.md` özet tablosu ve sayım (üçüncü bakış geçince); K10 "denemeye bağlı"; K16 :31 özet satırı (ses yolu değişti).
2. `planlama/dongu-158.md` P10.7 satırı ve §5 girdisi: K10 a masa denemesine bağlı (b yedek), K11 a = kutunun F6 3 A standart yuvası (ortak
   giriş teslimde), K14 a + kablo şartı + elle deneme, ses "masa denemesine bağlı kabul" (bölücü 10 kΩ / 2,2 kΩ), röle sürücüsü BC337-40 +
   270 Ω + 2,2 kΩ (PH sürüm 4 + düzeltme), maliyet genel −83,80 + üç standart sigorta, koşullu −77,46 + USB 2.0 farkı.
3. `planlama/maliyet.json` (sahibi):

| Satır | Kalem | Adet | Satıcı | Fiyat |
|---|---|---|---|---|
| MJ:106 | IRLZ44N → **BC337-40** (yalnız -40 sınıfı) | 2 → 3 (1 yedek) | Direnc.net (BC337-40TA) | 3,02 TL / adet (−39,74 toplam) |
| MJ:115 | Direnç seti notu: taban 270 Ω + 2,2 kΩ ×2, yedek 220 Ω; ses bölücüsü 10 kΩ + 2,2 kΩ | 1 (değişmez) | Robocombo | 90,50 (değişmez) |
| MJ:122 | Hat sigortası yuvası (göğüs çıktı) | 5 → 4 | Motorobit | −36,72 |
| MJ:123 | 2 A mini → **2 A standart** (F5) | 1 | bulunamadı | −7,34 + fiyat bekliyor |
| yeni | **5 A standart** (F4'ün ikinci 5 A'i) | 1 | bulunamadı | fiyat bekliyor |
| yeni | **3 A standart** (F6; yoksa 5 A standart) | 1 | bulunamadı | fiyat bekliyor |
| MJ:137 | USB 3.0 uzatma → **USB 2.0** A erkek-dişi ~1 m, erkek fiş ≤ 13 × 7 mm | 1 | aranmadı | 214,20 yerine fiyat bekliyor (koşullu) |
| MJ:191 | Göğüs HDMI notu: Ø ≤ 6 mm, micro fiş ≤ 7 mm kalın / ≤ 18 mm geniş; elle denemeyi geçmezse şerit (FPC) + adaptör | 1 | Robotistan | 117,10 (şart karşılanmazsa değişir) |
| MJ:136, 138 | Ses kartı uzatması ve L dirsek koşullu satırdan çıkar | – | – | −77,46 (koşullu) / 0 |
| MJ:141 | 3,5 mm kablo ReSpeaker → PAM (boy CAD'den) | 1 | – | fiyat bekliyor |
| MJ:77–78 | Notlar: ses kartı yedek, ses ReSpeaker'dan, denemeye bağlı | – | – | 0 |
| MJ:106, 109 | Notlardaki "GPIO2" → GPIO19; "IRLZ44N" → BC337-40 | – | – | 0 |

4. `planlama/d158/testler/T4-pam8403-ses-karti.md`: yol (ReSpeaker 3,5 mm → bölücü 10 k / 2,2 k → PAM), KT1 (stres + en yüksek ses + AI HAT+,
   `get_throttled` 0x0, DC pens / şönt ≲ 4 A, `pmic_read_adc`) ve KT2 maddeleri.
5. `elektrik.md`: satır sayısı değişmedi, atıf listesi gerekmez; :29 / :278 / :511'deki "tepe hesaplanmadı" ifadeleri C'de güncellenir.
6. Pano: Efe'ye taslak (depo dışında, düzeltme turu 2'ye göre güncellendi) Ahmet onayıyla gönderilir.

## 8. C adımı (14.11.2026, 03:08–03:30)

Girdi: üçüncü bağımsız bakış `planlama/d158/kablolama-onkarar-kontrol-3.md`: **GEÇER** (kayıtlı açık işlerle); A1–A7 metin düzeltmeleri ve
"C listesi" (Madde 8). Tasarım değeri değişmedi (270 Ω / 2,2 kΩ / BC337-40; pinler aynı).

### 8.1 Yapılan

| Madde | Yapılan | Yer |
|---|---|---|
| A1 | "hFE ≈ 170 → ≈ 3,9 kat" kalktı: 300 mA'deki en az hFE üreticiye göre (onsemi / Lumimax 60, DC Components 40, Diotec -40 170); belgeyle garanti pay 60 × 4,79 mA ≈ 287 mA > 0,21 A, **≈ 1,37×**. VCE ≤ 0,3 V'u hiçbir üretici garanti etmez; belgeyle sınır **1,0 V**: K1 bobini 11 V'ta ≥ 10,0 V, 10 V'ta ≥ 9,0 V (çekme ≤ 8,4 V). Kayıp ≤ 0,22 W, 60 °C'de Tj ≈ 103 °C (izin 0,45 W). Doyumu T2 (g)'nin VCE ölçümü kabul eder | PH BJT kaynak satırı, D9 satırı, D9 hesabı (zorunlu β, VCE, kayıp); R §9 tablo ve parça şartı; EL:268; G §7.2 notu |
| A2 | Sipariş 16.11'de yeni şartlarla (USB 2.0, fiş ≤ 13 × 7; HDMI Ø ≤ 6); fiş denemesi "sipariş öncesi" değil **demet kurulmadan önce**, teslimde, boyun tünelinin basılmış kısa deneme parçasında (kesit 20 × 7,8, ≈ 34 mm, iki dik dönüş, mil penceresi); parça P10.7 baskı listesine iş; CAD'e dokunulmadı; risk bölümü buna göre | R §4, risk paragrafı, KT4, §14; EL:37, :518; KK K14 Durum ve iş maddesi |
| A3 | T2a: "hFE soketinde ≥ 250" kalktı (soket µA–mA'de ölçer); ölçüt gövde yazısı + diyot testi; ayak sırası düz yüz önde C-B-E; ters takmada pine ≈ 2–3 mA, asıl risk bobin akımı (K1 ≈ 70 mA, varsayımla) | PH T2a; R §9 |
| A4 | T2'de "bara" ayrıldı: osiloskop kanalı **bobin (+) ucu** (F5 → mantar NC sonrası), (g) "bobin beslemesi 11 / 14,6 V", kontak çıkışı "anahtarlı bara"; "F5 normal kullanımda takılmaz" → "sorun giderilene dek robot devreye alınmaz" | PH T2 |
| A6 | Sıcak bobinde çekme gerilimi ≈ 9,6 V (60 °C) / ≈ 10,3 V (80 °C) (hesap, %0,39 / K): uzun çalışmadan sonra düşük aküyle K1 çekmeyebilir; arıza güvenli yönde, Y4 hata yolu yakalar | PH T2 Not; EL:268 |
| A7 | IOH 40 mA DS Tablo 5-3'te **tipik** sütunda (en yüksek kademe; ≈ 29 mA'e inebilir); kademeler ≈ 5 / 10 / 20 / 40, varsayılan 2 (IO_MUX not 8); röle verisi üretici tablolarından doğrulandı ("ikinci elden" kalktı) | PH RÖ satırı, D1 hesabı (2 yer), D9 bobin akımı satırı; R §9 tablo ve sürüş gücü maddesi; EL:268 |
| Sipariş bölümü | Rapora **§17 "16.11 siparişinden önce değişen kalemler"** (11 satır: kalem, eski → yeni, adet, satıcı / fiyat, neden); `maliyet.json`'a dokunulmadı | R §17, §0 işaretçi |
| Kayıt | KK: K1, K10, K11, K14 **kapandı** (özet tablo kalıbı K58 gibi; başlıklarda "— KAPANDI"; Durum satırları; K10 "masa testine bağlı kabul"); sayım dosyadan yeniden: **açık 46, kapandı 12**, toplam 58; dört önerinin kaydı (ses kabul, hub hayır, reset teli hayır + şart, elde acil stop Ahmet + Efe) üçüncü bakışa göre güncellendi; K16 notu duruyor; "Karar değil, iş"e yeni madde (KT1–KT7, tünel deneme parçası, sipariş değişiklikleri, tutarsız belgeler, 62 kablonun dökümü, Efe'nin iki cevabı, kontrol-3'ün bakamadıkları) | KK |
| Döngü | `planlama/dongu-158.md` P10.7 satırı (engel kalktı; kalan kablo tablosu işi + Efe'nin iki cevabı) ve §5 günlük girdisi | dongu-158 |
| Pano | Taslak son hâl: konu #7, gönderim komutu `--kaynak` satırlarıyla, gövde ayrı .txt (depo dışında); A5 düzeltmeleri. **Gönderilmedi** | depo dışı |

- `elektrik.md` satır sayısı 522 (değişmedi): satır atfı düzeltmesi gerekmedi. `pin-haritasi.md` satır sayısı arttı (D9 hesabı); PH'ye satır
  numarasıyla atıf yapan canlı belge aranmadı (istenen yalnız EL idi).
- Pin tablosu betiği yeniden koştu: 25 pin, üç yerde ve HEAD ile aynı, **GEÇER**.
- K58'in Durum satırındaki "P10.7 K10 / K11 / K14 ve parça işlerini bekliyor" yan cümlesine dokunulmadı (K58 bu paketin değil).
