# F7b günlüğü: yazdırılabilir rehber + kafa (QLED, ses, hub) adımları (P7.2), 09.11.2026

Brief: `planlama/d158/F7b-brief.md`. A ajanı (tasarım / uygulama). Commit, push ve silme yapılmadı. Bu dosyadaki saatler yerel saattir.

## Özet (kabul)

| # | Kabul ölçütü (brief "Kabul") | Sonuç | Kaynak |
|---|---|---|---|
| 1 | Kafa, hoparlör, hub metinleri görünen parçalarla uyumlu, çelişki 0, doğrulanmamışlar işaretli | çelişki 0; 14 bileşen × adım anma denetimi hepsi metinde | `kontrol.json` `denetim.tutarlilik` (`anmayan` 0, `celiski` 0); `rehber_denetim.py` çıkış 0 |
| 2 | ASCII kalıntı 0 (betikle) | 0 (veride 4.626 metin + tarayıcının bastığı 58 metin: 50 adım paneli, 7 telefon paneli, yazdir) | `kontrol.json` `denetim.ascii_kalinti_sayi` |
| 3 | Yanlış ad gruplaması 0 (betikle) | 0 (eski kural aynı veride 17 satırı yanlış toplardı) | `denetim.gruplama_yanlis`, `gruplama.eski_kural_yanlis` |
| 4 | `kontrol.json` 50/50, konsol hatası 0, parça 1192 ↔ 1192 | 50/50, 0, 1192 ↔ 1192 (mesh), her parça tam bir adımda: evet, atanmamış 0 | `planlama/rehber/kontrol.json` `ozet` (17:26) |
| 5 | PDF ≥ 50 sayfa, adım sayısıyla tutarlı; ≥ 6 sayfaya gözle bakıldı | 50 sayfa = 50 adım (HTML 50 `.sayfa`), taşan sayfa 0, A4 (595 × 842 pt), 3.883 kB; 9 sayfaya bakıldı (aşağıda) | `kontrol.json` `yazdir`; pypdf |
| 6 | 360 px yatay kaydırma yok (ekran görüntüsü) | 7 adımda (0, 9, 24, 31, 32, 35, 49) görüntü alanı 360, taşma 0 px | `kontrol.json` `telefon`; `planlama/rehber/goruntu/telefon-360-adim-NN.png` |
| 7 | `carpisma_kos.py kontrol` 0, `regresyon.py --yazma` 0 | 0 / 0 (başta 17:07 ve sonda 17:27) | aşağıda komutlar |

## Komutlar (saat, çıkış kodu)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 17:07 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| 17:07 | `py -3 planlama/d158/regresyon.py --yazma` | 0 | GEÇER, kötüleşen yok |
| 17:07 | kilit "F7b 2026-11-09 17:07 …" → `rehber_uret.py --gorsel-yok` → kilit "boş" | 0 | veri 30 s; mesh 288 benzersiz / 1192 parça, 189.934 üçgen, GLB 2,56 MB; 50 adım |
| 17:08 | `rehber_denetim.py` (ilk tarama) | 1 | ASCII 104 (gözden geçirilmemiş Türkçe kelimeler + "tas direnç"), gruplama 1 (denetimin kendi normalleştirmesi: "Yüz kabuğu (ön) sağ"), çelişki 1 (göğüs ekranı ürün kodundaki "LCD"); üçü de aşağıda |
| 17:10 | `rehber_uret.py --veri-yok --adimlar 0,9,24,31,32,34,49 --cikti <scratchpad>` | 2 | 7/7 geçti; telefon genişliği 504 (Chrome pencereyi ~500 px'in altına indirmiyor), PDF K2 sayfası taşıyor, yazdir metninde betik sızıntısı → düzeltildi |
| 17:13 | aynı, `--adimlar 0,31,32` | 2 | telefon 360 / taşma 0 (DevTools), PDF taşma 0; ASCII 10 (telefon panelinde `code` içeriği, yazdir'de öznitelik metni) → düzeltildi |
| 17:15 | kilit → `rehber_uret.py --gorsel-yok` → kilit "boş" | 0 | veri 27 s |
| 17:15–17:20 | `rehber_uret.py --veri-yok` (tüm adımlar) | 2 | 50/50, konsol 0; ASCII 3 ("tas", "keskialet", "multimetrealet": yan yana öğe metni birleşiyordu) → düzeltildi |
| 17:20 | kilit "F7b 2026-11-09 17:20 …" → `rehber_uret.py --gorsel-yok` → kilit "boş" | 0 | veri 27 s (son veri: üretim 17:21) |
| 17:21–17:26 | `rehber_uret.py --veri-yok` (tüm adımlar) | **0** | 50 adım 50 geçti, konsol 0, her parça tek adımda; yazdir görüntüsü 50; telefon 7 × 360/0; PDF 50 sayfa, taşan yok; denetim ASCII 0, gruplama 0, çelişki 0 |
| 17:27 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | aynı |
| 17:27 | `py -3 planlama/d158/regresyon.py --yazma` | 0 | GEÇER |
| 17:27 | `python tasarim/freecad/rehber/rehber_denetim.py` | 0 | ASCII 0, gruplama 0, çelişki 0; parça 1192, şema 13 |

FreeCAD kuralı her koşudan önce: `freecadcmd` / `FreeCAD` süreci yok, boş bellek 2,25–3,01 GB, kilit "boş". Kilit dosyası silinmedi;
koşudan sonra "boş" yazıldı ve yeniden okundu ("boş"). Rehber verisi tek komutun iki yarısıyla üretildi (`--gorsel-yok` kilit altında,
sonra `--veri-yok`): FreeCAD yalnız ilk yarıda çalışır, kilit tarayıcı kontrolü boyunca tutulmadı. Her koşudan sonra `lale-rehber`
profilli Chrome süreci kalmadığı denetlendi (0).

## Yapılanlar

### 1. Kafa, hoparlör, hub metinleri (`tasarim/freecad/rehber/rehber_metin.py`)
- **E3a** "Tezgâh: kafa içi (Pi 5, 5 V çeviriciler)": Pi 5 4 burç (M2,5×8 + M2,5×5), D24V50F5 (Pi), SY8205 (kafa ekranı) ve P6KE6V8A
  1 mm köpük bant + kablo bağıyla, 625ZZ dış bilezik, tilt hornu. QLED, tırnaklar, kamera, ReSpeaker, ses kartı ve PAM8403 açıkça E4'e
  yönlendirildi. M6'daki "LCD 4 × M3×6" ve "kamera 4 × M2×8 PT" yalnız "bu adımda yok" bağlamında kaldı. Horn sırası "doğrulanmadı".
  Notlar: iki 5 V hattı köprülenmez; Touch VBUS uyarısı E4'te (`planlama/adim3/elektrik.md`).
- **E4** "Kafa kabukları + yüz ekranı, kamera, ses": 5 maddelik iş (kamera 4 × M2×8 PT; 10,1" QLED vida deliksiz, camı ön duvara
  yaslanır, 4 tırnak x ±85, 1 × M3×6 ISO 7380 + ısıl gömme, 1 mm köpük; QLED kabloları HDMI / Power / Touch; ReSpeaker 3 × M2×8 PT,
  ses kartı + PAM8403 köpük bant; kabuklar, tabla → raf 4 × M3×10). Bağlantı sayımı: M3×6 ×11 (4 tırnak + 7 dikiş), M3×5 ×2, ısıl
  gömme ×17, M3×10 ×4, M2×8 PT ×7. Notlar: Touch VBUS ölçümü (Power ↔ Touch VBUS, multimetre, takmadan önce), iki 5 V köprülenmez, sıra
  "doğrulanmadı", PAM 5 V noktası K10 (varsayılan D24V50F5), kütle ve akım varsayımları. Arka kabuk dikişleri K2'den sonra sıkılır
  (boyundan gelen uçlar). Bu sıra montaj mantığından çıkarıldı: doğrulanmadı.
- **K2** madde 4 (F7a'nın "madde 3"ü): ESP32 USB artık boyuna girmez: 05.11 B kararı, ESP32'den direk arka yüzü (z −26) boyunca üst arka
  kapak hizasındaki hub'a (`lale158/kablo_yolu_ekran.py` başı, `elektrik.md` hub satırı). Madde 5: boyun demeti 5 kablo (kafa 12 V,
  tilt, göğüs HDMI, hub uzatması, hoparlör). Notlar: K14 (boyundan inen HDMI ve hub uzatması ekip teyidi bekliyor, doğrulanmadı), K11
  (göğüs ekranı 12 V giriş noktası), eksik kablolar, hub düşerse ESP32 + dokunmatik birlikte düşer.
- **F2**: hoparlör kabı (ön halka, flanşlı arka), kelepçe 2 × M3×20 + köpük ped, PAM8403 → hoparlör uç bağlantısı; havya. Notlar: K6
  eksen / kama, kablo ucunun biçimi varsayım (ürün elde yok).
- **F5**: hub üst arka servis kapağının takozunda, iki yan dayama arasında 1 mm köpük bant; Pi USB 3 uzatması, Hub 1 göğüs dokunmatiği,
  Hub 2 ESP32, 3–4 boş (K1). Devreye alma testi hub bağlıyken, kapaklar sonra (22 × M3×6 + 22 ısıl gömme). Notlar: 150 mm söküm payı
  tahmin, hub giriş gerilimi ölçülmedi.
- **Taban kablo şeması 8**: CAD etiketi `taban_parcalar.py`'de (carpisma_kos `KAYNAK_SABIT` içinde, dokunulmadı). Görünen ad
  `rehber_metin.KABLO_AD` ile: "Kablo yolu 8: Kafa 12 V (K4 / E4): F3 5 A → 18 AWG çift → direk ön yüzü → R62 → boyun → kafa girişi →
  Pololu D24V50F5 (Pi 5; PAM8403 varsayım, K10) + SY8205 (10,1" QLED)". Şema 12'nin direkten kafaya çıkan kısmının eski olduğu adında
  ve K2 kablo kancasında yazıyor (geometri kaynakta değişmeli; açık 4). Beklenen CAD etiketi başı tutmazsa `rehber_veri.py` uyarı yazar
  (`kablo_ad_uyari`, bu koşuda boş).

### 2. Göğüs ekranı / kafa kablo yolları (`rehber_veri.py`, `app.js`, `yazdir.html`)
`lale158/kablo_yolu_ekran.py` yalnız okundu (import edilip noktaları rehber koordinatına çevrildi). **13 gösterim şeması** eklendi:
K2'de 5 (göğüs HDMI, hub uzatması, ESP32 USB, hoparlör, göğüs 12 V), F3'te 1 (göğüs dokunmatiği → Hub 1), E4'te 7 (ReSpeaker USB, ses
kartı uzatması, 3,5 mm → PAM, PAM 5 V, kafa içi QLED HDMI / Touch / Power). Şemalar `semalar` alanında, `parcalar`da değil:
**parça sayısı 1192 değişmedi, Referans parça sayısı 13 (12 taban kablo şeması + ana anahtar gösterimi) değişmedi**; görünen gösterim
öğesi sayısı 13 → 26 (13 Referans parça + 13 şema). Tarayıcı kontrolü her adımda beklenen şema kümesini de karşılaştırır (`sema_fark`, hepsi
boş).

### 3. Parça listesi gruplama (`rehber_veri.py`)
Anahtar: (kod, tür, renk, taban ad). Taban ad = FreeCAD `0NN` eki, sondaki açıklama parantezi ve sağ / sol atılmış ad. Satır `ids`
taşır; adı tek parçaysa tam ad, çoksa taban ad + "(sağ + sol)" ya da tek yan. Örnek (F7a'da yanlış olanlar): F2 "Gövde alt bandı (sağ +
sol) ×2" + hoparlör parçaları ayrı satırlarda; H0a dirsek / bilek servoları ayrı; F5 dört kapak ayrı; F1 etek arka / orta / ön ayrı.
`rehber_denetim.py` her satırın üyelerinin tek taban adı olduğunu, satır adıyla aynı olduğunu ve adımın her parçasının tam bir satırda
olduğunu denetler: 0 yanlış. Eski kural (kod + tür + renk) aynı veride 17 satırı farklı adlarla toplardı. Bağlantı satırları: ısıl gömme
somunlarda "Baskıdan sonra takılı (hazırlık); burada yalnız sayılır" notu (F7a-kontrol D-1).

### 4. TR sözlüğü ve tarama (`rehber_metin.py` `TR_EK`, `TR_IFADE`, `tr()`; `rehber_denetim.py`)
- `TR_EK` (küçük harf sözlüğü), `TR_IFADE` (10,1in → 10,1", O32 → Ø32, one-arka → ön-arka, 4 lu → 4'lü, VARSAYIM / TAHMIN /
  DOGRULANMADI, -> → →, psi → ψ, tas direnç → taş direnç), `TUR_AD`, `MODUL_AD`. "mantari", "cikis", "govdesi" artık veride yok.
- Tarama: veri (adım metinleri, parça satırları, tür, malzeme, bağlantı kodu, tıklama etiketi: ad / kod / modül, şema adları) + headless
  Chrome'un bastığı panel / seçim / lejant metni (50 adım), telefon paneli (7) ve `yazdir.html` metni. Kod (`…` ve `<code>`) ve kesme
  sonrası ek atlanır. Kalıntı = sözlükte karşılığı olup uygulanmamış kelime, kısaltma listesinde olmayan büyük harfli kelime ya da elle
  gözden geçirilmiş `ASCII_TAMAM` listesinde olmayan her ASCII kelime. Bu turda listeye eklenenler doğru Türkçe (delik, birlikte, gerilim
  …) ya da teknik ad (Power, Touch, lens, WROOM, IPS, JGB, LOW / HIGH, RESPEAKER-MIC dosya adı); gerçek kalıntı olarak yalnız "tas direnç"
  bulundu ve düzeltildi.
- Denetimin "LCD" eski ifade deseni göğüs ekranı ürün kodunu ("Waveshare 11.6inch HDMI LCD (H)") hariç tutar; kalan iki LCD geçişi o ürün
  kodu ve E3a'daki "M6'daki LCD … bu adımda yok" cümlesi.

### 5. Yazdırılabilir sürüm, telefon, kadraj
- `rehber/yazdir.html`: adım başına A4 sayfa (başlık, rozetler, 3B görüntü `rehber/goruntu/adim-NN.png`, süre / parça / alet / bağlantı
  sayısı, iş metni, Notlar ve uyarılar, parçalar + bağlantı elemanları, kontrol listesi (kutucuklu), kablo kancası + şemalar, erişim
  notu, alt bilgi "Sayfa i / N"). İki sütun dengeli akar; sığmazsa önce görüntü 84 → 46 mm, sonra yazı 9,6 → 6,6 pt küçülür. Sonuç:
  taşan sayfa 0; küçük yazılı iki sayfa: E4 (7,2 pt), K2 (7,8 pt).
- PDF: `rehber_uret.py` headless Chrome `--print-to-pdf` → `planlama/rehber/Lale-montaj-rehberi.pdf`; sayfa sayısı pypdf ile; eski PDF
  sayılmasın diye dosya saati denetlenir. PDF meta verisinde yerel yol yok (başlık ve üretici yalnız).
- Telefon: Chrome `--window-size=360,…` görüntü alanını 504 px'te bırakıyor (17:10 koşusu). Kontrol DevTools protokolüne geçti
  (`Emulation.setDeviceMetricsOverride` 360 × 1600, mobil). Taşma = max(belge, body scrollWidth) − clientWidth. `stil.css`: dar
  ekranda `body{overflow:auto}`, `.baslik{min-width:0}`, panel / etiket / lejant `overflow-wrap:anywhere`. Taşma `overflow-x:hidden`
  ile gizlenmedi.
- Kadraj (F7a-kontrol D-4): yarıçap = max(70, 1,1·r0, min(0,3·rg, 2,2·r0)); r0 yeni parçalar, rg görünen robot. E1 r 82 → 180, B3 236 →
  259 (bağlam görünür). `kontrol-veri`'ye `kadraj` yazılır.
- `--cikti <klasör>` (F7a-kontrol D-5): bağımsız kontrol depoyu değiştirmeden koşabilir (`rehber/goruntu` her zaman güncellenir).

## Bakılan görüntüler ve sayfalar
- PDF (son koşu 17:26): sayfa 1 (0 hazırlık), 10 (B3), 25 (E1), 30 (E3a), 32 (E4), 33 (K2), 35 (F2), 50 (F5): 8 sayfa. Hepsi tek sayfada,
  görüntü doğru adımda, metin okunur. K2 sayfası 17:13 koşusunda da bakıldı (iki sütun düzeltmesinden sonra sığdı). 17:10 koşusunda K2 sağ
  sütunu taşıyordu (iki sütun grid → CSS sütun akışı).
- Telefon 360 px: adım 31 (E4) ve 49 (F5) görüntüsü: yatay kaydırma yok, üst çubuk, sahne, lejant, panel ve alt gezinme 360 px içinde.
- Tarayıcı kadrajı: B3 ve E1 PDF görüntüsünde bağlamla birlikte (F7a'da çok yakındı).

## M6-montaj-sirasi.md önerisi (F7a günlüğü; dosya değiştirilmedi)
F7a önerisi yönü doğru ama eksik ve kısmen genel. Değerlendirme, satır satır (`planlama/adim4/M6-montaj-sirasi.md` 2. bölüm):
- **C1, F1, F3, E2c**: F7a önerisi rehber metniyle tutarlı; olduğu gibi alınabilir.
- **E3a** (satır 29): F7a "kafa (QLED yüz kabuğunda)" yazmış, yetmez. Önerilen: "Tezgâh: kafa iskeleti, Pi 5 (4 burç), D24V50F5 + SY8205
  + P6KE6V8A (köpük bant), 625ZZ dış bilezik, tilt hornu | 4 × M2,5×8 burç + 4 × M2,5×5; 1 × M3×5 horn". Mevcut satırdaki "LCD 4 × M3×6"
  ve "kamera 4 × M2×8 PT" E4'e taşınmalı.
- **E4** (satır 31): mevcut "4 × M3×8 ISO 7380 + vizör" eski. Önerilen: "Kafa kabukları + 10,1" QLED (4 tırnak), kamera, ReSpeaker, USB
  ses kartı, PAM8403 | 11 × M3×6 ISO 7380 (4 tırnak + 7 dikiş) + 2 × M3×5; 17 ısıl gömme; 4 × M3×10 (tabla → raf); 7 × M2×8 PT (4 kamera
  + 3 ReSpeaker)". Erişim: arka kabuk dikişleri K2'den sonra.
- **K2** (satır 32): F7a önerisinde yok, ama satır "Nextion kablosu" ve "kafa 12 V + sinyal (direk → boyun)" diyor. Önerilen: boyun demeti
  5 kablo (kafa 12 V, tilt, göğüs HDMI, hub uzatması, hoparlör); ESP32 USB direk arka yüzünden hub'a (boyundan değil); göğüs ekranı 12 V
  tabandan ayrı dal; Nextion kalkar. K14 teyidi gelmeden "doğrulanmadı" notuyla.
- **F2** (satır 34): F7a "+ uzatma 1 / 2, hoparlör; M5×18 dışarıdan" doğru; eklenmeli: hoparlör kelepçesi 2 × M3×20 + köpük ped.
  Mevcut "M5×10 + pul, içeriden" eski (K1 sonrası M5×18 dışarıdan, perçin somun).
- **F5** (son satır): "7 × M3×6" eski; önerilen: "arka + üst arka servis kapağı (hub kapak içinde, köpük bant), etek H1 / H2 | 22 × M3×6
  ISO 7380 + 22 ısıl gömme"; "devreye alma testinden sonra, hub bağlıyken".
- Tablo erişim sütunu hâlâ 125 cm `M6_erisim.py` analizinden; 1,58 m'de yeniden koşulmadan erişim sınıfları güncellenmemeli (F7a madde 9
  açık).

## Dokunulan dosyalar (commit listesi)
Değişen:
- `tasarim/freecad/rehber/rehber_metin.py`
- `tasarim/freecad/rehber/rehber_veri.py`
- `tasarim/freecad/rehber/rehber_uret.py`
- `rehber/app.js`
- `rehber/stil.css`
- `rehber/veri/rehber-veri.json`, `rehber/veri/rehber-veri.js` (üretilen; `robot.glb` / `robot-glb.js` içerik olarak aynı çıktı)
- `planlama/rehber/kontrol.json` (üretilen)
- `planlama/rehber/goruntu/adim-00.png` … `adim-49.png` (50, üretilen)
- `planlama/rehber/R-gunluk.md`

Yeni:
- `tasarim/freecad/rehber/rehber_denetim.py`
- `rehber/yazdir.html`
- `rehber/goruntu/adim-00.png` … `adim-49.png` (50, üretilen; yazdırılabilir sürümün görüntüleri)
- `planlama/rehber/goruntu/telefon-360-adim-00.png`, `-09`, `-24`, `-31`, `-32`, `-35`, `-49` (7, üretilen)
- `planlama/rehber/Lale-montaj-rehberi.pdf` (üretilen)
- `planlama/d158/F7b-gunluk.md` (bu dosya)
- `planlama/d158/F7b-brief.md` (orkestratörün brief'i; bu paket yazmadı, commit'e girer)
- `planlama/d158/F7b-kontrol.md` (B'nin kontrol raporu; bu paket yazmadı, commit'e girer)

Kilit: `planlama/d158/FREECAD-KILIT.txt` yalnız koşu süresince yazıldı, sonda "boş" (izlenmeyen dosya, commit'e girmez).
Dokunulmadı: `rehber/index.html`, `lale158/kablo_yolu_ekran.py`, `taban_parcalar.py` ve diğer tarama kaynakları, `*_lib.py`, model
dosyaları, `M6-montaj-sirasi.md`, `karar-kuyrugu.md`, `dongu-158.md`, F6b alanı. Çalışma ağacındaki `planlama/d158/F5*-pano-govde.txt`,
`F9b-*` ve diğer değişiklikler bu paketin değil.

## Açıklar
1. **Doğrulanmamış (metinde işaretli):** E4 / K2 iş sırası (arka kabuk dikişleri K2'den sonra), boyundan inen HDMI ve hub uzatması (K14,
   ekip teyidi), göğüs ekranı 12 V giriş noktası ve acil stop davranışı (K11), PAM8403 5 V noktası (K10), hoparlör ekseni / kama (K6),
   hoparlör kablo ucu biçimi, hub'ın 150 mm söküm payı ve giriş gerilimi, QLED kütle / akım, horn sırası.
2. **Modelde yok:** kafa girişindeki P6KE18A (metinde "modelde yok"); hub uzatması (~1 m USB-A) ve hoparlör kablosu robot listesinde yok.
3. **Touch VBUS:** ölçüm uyarısı E3a, E4 Notlar'da; ölçüm henüz yapılmadı (`elektrik.md`).
4. **Taban şeması 8 / 12 kaynakta eski:** CAD etiketi "kafada 5 V/5,5 A cevirici (Pi 5, LCD)" ve şema 12'nin direkten kafaya çıkan kısmı
   (05.11 öncesi ESP32 → kafa USB) `taban_parcalar.py`'de. Dosya tarama kaynağı (`KAYNAK_SABIT`), bu pakette değiştirilmedi; görünen ad
   rehberde düzeltildi. Kaynakta düzeltilmesi gerekiyor (model geometrisi değişir, tarama yeniden koşar).
5. **Küçük yazı:** E4 (7,2 pt) ve K2 (7,8 pt) sayfaları sığdı ama küçük; metin kısalırsa ya da adım bölünürse büyür. K2 görüntüsü
   şemalar tüm robotu kapsadığı için uzak (r 863).
6. **Telefon kontrolü** Python `websockets` paketine bağlı (yoksa `telefon.gecti` false ve sebep `kontrol.json`'a yazılır).
7. **Önceden var olan yerel yollar:** `rehber_uret.py` ve `rehber_veri.py`'deki yol düzeltme turu 1'de kaldırıldı (D-5, aşağıda).
   `carpisma_kos.py` (tarama kaynağı, dokunulmaz) ve depodaki öbür izlenen dosyalar hâlâ içeriyor; `F7a-kontrol.md` içinde scratchpad'e
   giden yerel bir yol var. Depo herkese açık: kayıt ajanı / orkestratör değerlendirmeli.
8. Kök `README.md` rehber satırı (≈ 139) eski: F7b ekleri (PDF, telefon, denetim, `--cikti`) yok. README bu paketin yazma alanında değil.
9. Parça adlarında `M2,5x8`, `M2x8` gibi "x" yazımları CAD adından geliyor (metinde ×); ASCII denetimi bunları kalıntı saymıyor.
10. `M6-montaj-sirasi.md` önerisi yukarıda; tablo güncellenmedi. `M6_erisim.py` 1,58 m'de koşulmadı (F7a madde 9).

## Düzeltme turu 1 (09.11, `planlama/d158/F7b-kontrol.md`: kritik 0, orta 3, düşük 9)

### Maddeler

| Madde | Durum | Değişen yer |
|---|---|---|
| O-1 göğüs regülatörü 12 V ayarı | yapıldı | `rehber_metin.py` K2 madde 7 + kontrol + not, F3 madde 3 + not |
| O-2 1N5819 yönü | yapıldı | K2 madde 4, "ESP32 USB" şema adı, F5 madde 1 (atıf) |
| O-3 iki P6KE6V8A + kutup | yapıldı (kutup kaynakta yok, işaretli) | E3a madde 2 + not |
| D-2 enerji durumu | yapıldı | E3a kontrol (SY8205 ölçümü), K2 başı, K1 iş + kontroller |
| D-4 `--cikti` tam yalıtım | yapıldı | `rehber_uret.py` |
| D-5 yerel yol | yapıldı | `rehber_uret.py` başlık + `LAUNCH`, `rehber_veri.py` başlık |
| D-7 (isteğe bağlı) | yapıldı | F2 not, E4 kontrol |
| D-1 (isteğe bağlı) | yapıldı | `rehber_denetim.py` (zorunlu uyarı, bağlantı satırı, bağlam penceresi, LCD muafiyeti, "çıkar") |
| D-3, D-6, D-9 | yapılmadı (düzeltme listesinde zorunlu değil; D-9 orkestratörde) | — |

### Metinler: önce → sonra (kaynak)
- **K2 madde 4 (O-2).** Önce: "ESP32 USB (VBUS'ta 1N5819) boyuna girmez …". Sonra: "… F5'te hub'a takılır. VBUS teline seri 1N5819: anot hub (Pi)
  tarafında, katot ESP32 tarafında; çevre 5 V hub'a / Pi'ye geri beslemez. ESP32 kartının kendi VBUS→VIN diyodu varsa gerekmez:
  multimetreyle bak (doğrulanmadı)." Kaynak `planlama/adim3/elektrik.md:283` ("seri 1N5819 (anot Pi tarafında) … Diyot sayesinde çevre 5 V
  Pi'ye geri beslemez") ve `:285` (kartın kendi diyodu doğrulanırsa gerekmez, montajda multimetreyle). 05.11 sonrası yol Pi → hub → ESP32
  olduğu için "Pi tarafı" = hub tarafı. Şema adı aynı cümleyle; F5 madde 1'e "1N5819 yönü K2 madde 4" atfı.
- **K2 madde 7 + kontrol + not (O-1).** Madde 7 sonuna "Regülatör ekrana bağlanmadan 12 V'a ayarlanır (kontrol)". Yeni kontrol: "Göğüs ekranı
  regülatörü (LM2577 + LM2596) ekrana bağlanmadan, çıkışı multimetreyle 12 V'a ayarlandı: tezgâhta akım sınırlı kaynakla (sınır 2 A) ve
  yük direnciyle". Yeni not: "LM2577 + LM2596 kartı ve mini 2 A sigorta modelde yok; takılacakları yer (şemada güç paneli) doğrulanmadı".
  Kaynak `elektrik.md:67` (ayar), `:16` (regülatör modelde / BOM'da yok); tezgâh kaynağı, 2,0 A sınır ve yük direnci
  `planlama/d158/testler/T7-gogus-ekrani-12v.md:37, 43, 45`. K2 enerjisiz yapıldığı için ayar tezgâhta yazıldı (çelişki çıkmasın).
- **F3 madde 3 (O-1).** Önce: "11,6" ekranı (kasalı) cebe koy. K2'de bırakılan HDMI ve 12 V uçlarını tak (90° fişler)." Sonra: "… 12 V fişini
  takmadan önce regülatör çıkışını yeniden ölç: 12 V (K2'de ayarlandı; ölçünce enerjiyi kes). Sonra K2'de bırakılan HDMI ve 12 V uçlarını
  enerjisizken tak (90° fişler)." Not: "Regülatör kartı ve mini 2 A sigorta modelde yok; yerleri doğrulanmadı".
- **E3a madde 2 + not (O-3).** Önce: "… SY8205 (kafa ekranının ayrı 5 V hattı) ve P6KE6V8A TVS (kafa ekranı 5 V)." Sonra: "… Her iki 5 V çıkışına
  bir P6KE6V8A TVS: SY8205 → QLED hattındaki modelde var, D24V50F5 → Pi hattındaki modelde ve BOM'da yok (ikinci TVS'i ayrıca al). TVS tek
  yönlü: katot (çizgili uç) +5 V'a, anot GND'ye." Kaynak `elektrik.md:47, 49, 282` ("her iki 5 V çıkışına P6KE6V8A"); BOM'da tek adet
  (F7b-kontrol O-3, `F4a-gunluk.md:188`). **Kutup yönü depo kaynaklarında yok** (elektrik.md, testler, kafa raporu tarandı): tek yönlü TVS'in
  genel bağlanışı olarak yazıldı; notta "depo kaynağında yazmıyor, veri sayfasıyla doğrulanmadı" diye işaretli.
- **E3a kontrol (D-2).** Önce: "SY8205 çıkışı yük bağlanmadan ölçüldü: 5 V (kafa ekranı hattı)". Sonra: "SY8205 çıkışı yük bağlanmadan, akım
  sınırlı tezgâh kaynağıyla (12 V, sınır 1 A) ölçüldü: 5 V (kafa ekranı hattı). SY8205'te ters kutup koruması yazmıyor: kaynağın kutbunu
  bağlamadan önce kontrol et". **Seçim: ölçüm E3a'da kaldı.** Gerekçe: E3a tezgâh adımı; SY8205 çıkışı burada açık ve QLED'e bağlanmamış
  (E4'te bağlanır). K2 artık enerjisiz yapılıyor (aşağıda): ölçüm K2'ye taşınsaydı orada enerji gerekecek ve "K2 enerjisiz" kuralıyla
  çelişecekti. Kaynak: `planlama/d158/testler/T3-kafa-5v-akim.md:45` (SY8205'te koruma yazmıyor; ilk enerji laboratuvar kaynağıyla, akım
  sınırı 1 A), `elektrik.md:25`.
- **K2 başı (D-2).** Önce: "Kabuktan önce dur. Taban uçları K1'de bağlandı; …". Sonra: "Kabuktan önce dur. Enerjisiz çalış: akü XT60 ayrık, F3
  (kafa) takılı değil; kafa uçları enerjisiz bağlanır. Taban uçları K1'de bağlandı; …".
- **K1 (D-2 çelişkisi).** Önce: iş "Akü ayrık kalır; sırayla:", ama kontrollerde enerji isteyen XL4016 ayarı, motor yön testi, PC817 ölçümü ve
  "ilk açılışta BMS". Sonra: iş "Bağlarken akü ayrık (XT60 açık); sırayla:" + yeni madde 6 "Enerjili ölçümler (bağlantılar bitince; aşağıda
  "enerjili" yazan kontroller): akım sınırlı tezgâh kaynağıyla ya da aküyle, ana sigorta takılı, F3 (kafa) takılı değil. Bitince akü XT60'tan
  yeniden ayrılır: K2 ve kafa işleri enerjisiz yapılır. Bu sıra kaynakta yok, doğrulanmadı." Kontroller "Enerjili (madde 6): …" ve "Akü
  ayrıkken: …" diye ayrıldı; bara kapasitesi "akü ayrıkken, multimetrenin kapasite kademesiyle" (`elektrik.md:462`), BMS gözlemi "enerjili,
  ilk açılışta" (`elektrik.md:461`).
- **F2 not (D-7).** Eklendi: "Hoparlör kabı, kulakları, ızgarası ve kelepçesi varsayım: ürün elde görülmeden kesinleşmez (`kabuk_parcalar.py`),
  doğrulanmadı" (`kabuk_parcalar.py:730`).
- **E4 kontrol (D-7).** Önce: "tırnak cıvatası cama bastırıyor ama camı zorlamıyor". Sonra: "tırnak cama bastırıyor (cıvata tırnağı boss'a tutar),
  camı zorlamıyor" (`kafa10_lib.py:341`).

### Kod
- **D-4.** `--cikti` verilince kontrol.json, `goruntu/` (kontrol + telefon), PDF ve `<çıktı>/rehber/` (yazdir.html + `veri/rehber-veri.js`
  kopyası + 3B görüntüler) o klasöre gider; depodaki `rehber/` yalnız okunur. `--cikti` `--veri-yok` olmadan verilirse betik durur (veri
  üretimi `rehber/veri/`'ye yazar). Deneme (17:55, `--veri-yok --cikti <scratchpad> --adimlar 29,32`): koşu sırasında depoya yeni yazılan
  dosya 0 (`find -newer`); çıktı klasöründe kontrol.json, goruntu/, PDF, rehber/{yazdir.html, veri/, goruntu/adim-29, -32}. Çıkış 2: kopyada
  48 görüntü yokken yazdir'in yer tutucu metnindeki "rehber_uret" ASCII kalıntı sayıldı → yer tutucudaki dosya adı `<code>` içine alındı
  (`yazdir.html`).
- **D-5.** `LAUNCH = os.environ.get("LALE_FC_LAUNCH") or os.path.join(os.path.expanduser("~"), ".robot-cad", "run_fc.py")`; başlık yorumları
  `~/.robot-cad/run_fc.py`. `tasarim/freecad/rehber/`, `rehber/` ve `planlama/rehber/` içinde yerel kullanıcı klasörü yolu 0 (grep).
  Yeniden üretim ortam değişkeni olmadan koştu (17:54): başlatıcı ev klasöründen bulundu, çalışıyor.
- **D-1.** `rehber_denetim.py`: (4) zorunlu uyarı listesi, 11 madde (E3a köprülenmez / iki TVS / TVS kutbu / akım sınırlı ölçüm; E4 Touch
  VBUS / köprülenmez; K1 akü ayrık; K2 enerjisiz / 1N5819 yönü / regülatör ayarı; F3 fişten önce ölçüm); (5) adımın her bağlantı elemanı
  parçası tam bir bağlantı satırında; eski ifadenin bağlamı desenin ±60 karakterinde aranır, affedilenler `affedilen` listesine yazılır;
  "çıkar" bağlam listesinden çıktı; LCD muafiyeti yalnız "11.6inch HDMI LCD" ürün koduna. Düzeltilmemiş veride (17:54 öncesi) zorunlu uyarı
  eksik 8 / 11 bulundu (beklenen). Enjeksiyon (scratchpad'de bellek içi kopya, depo değişmedi): F2'den bağlantı satırı düştü, "Kafa LCD
  vidası 11,6 mm", "ESP32 USB … boyuna çıkar.", E4'ten Touch VBUS notu silindi, K2'den 1N5819 yönü silindi: beşi de yakalandı. Bugünkü
  veride bağlamla affedilen 6 cümle. Yeni doğru Türkçe kelimeler (enerjili, katot, diyodu …) gözden geçirilip `ASCII_TAMAM`'a eklendi.

### Komutlar (saat, çıkış)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 17:54 | süreç 0, boş bellek 2,72 GB, kilit "boş" → kilit "F7b düzeltme turu 1 2026-11-09 17:54 …" → `rehber_uret.py --gorsel-yok` (LALE_FC_LAUNCH tanımsız) → kilit "boş" (yeniden okundu) | 0 | veri 28 s; mesh 288 / 1192, 189.934 üçgen, GLB 2,56 MB, 50 adım |
| 17:54 | `rehber_denetim.py` | 1 → 0 | yeni metinde ASCII 31 (doğru Türkçe kelimeler) → `ASCII_TAMAM`; sonra ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 11 |
| 17:55 | `rehber_uret.py --cikti <scratchpad> --adimlar 29` (`--veri-yok` olmadan) | 1 | beklenen ret: "--cikti ile --veri-yok kullan" |
| 17:55 | `rehber_uret.py --veri-yok --cikti <scratchpad> --adimlar 29,32` | 2 | yalıtım denemesi (yukarıda); yer tutucu düzeltildi |
| 17:56–18:01 | `rehber_uret.py --veri-yok` (tüm adımlar) | **0** | 50 / 50, konsol 0, 1192 ↔ 1192, her parça tek adımda; yazdir görüntüsü 50; telefon 7 × 360 / 0; PDF 50 sayfa, taşan yok, küçük yazı E4 7,2 pt, K2 7,2 pt (önce 7,8), 3.891 kB; denetim ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 11 |
| 18:01 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| 18:01 | `py -3 planlama/d158/regresyon.py --yazma` | 0 | GEÇER (kötüleşen yok) |
| 18:01 | `python tasarim/freecad/rehber/rehber_denetim.py` | 0 | aynı |

`lale-rehber` profilli Chrome süreci kalmadı (0); FreeCAD süreci yok; kilit "boş".

### Bakılan PDF sayfaları (18:01 PDF'i)
Sayfa 18 (K1: madde 6, "Enerjili / Akü ayrıkken" kontrolleri), 30 (E3a: iki TVS, kutup, akım sınırlı ölçüm, not), 33 (K2: başta enerjisiz,
madde 4 1N5819 yönü, madde 7, regülatör kontrolü, not, şema adı; 7,2 pt, tek sayfa), 35 (F2: hoparlör varsayım notu), 36 (F3: madde 3
yeniden ölçüm, not). Hepsi tek sayfada; metin doğru adımda.

### Dokunulan dosyalar (bu tur)
`tasarim/freecad/rehber/rehber_metin.py`, `rehber_uret.py`, `rehber_veri.py`, `rehber_denetim.py`; `rehber/yazdir.html`;
`rehber/veri/rehber-veri.json`, `.js`; `rehber/goruntu/adim-NN.png` (50); `planlama/rehber/kontrol.json`, `goruntu/adim-NN.png` (50),
`goruntu/telefon-360-adim-NN.png` (7), `Lale-montaj-rehberi.pdf`, `R-gunluk.md`; bu günlük. Commit listesi yukarıda (F7b-brief.md ve
F7b-kontrol.md eklendi). `.gitignore`'a dokunulmadı.

### Açıklar (bu turdan)
- TVS kutup yönü veri sayfasıyla doğrulanmalı; ikinci P6KE6V8A (Pi hattı) modelde ve BOM'da yok.
- Göğüs regülatörü kartı ve mini 2 A sigortanın yeri modelde yok (K11 ile birlikte).
- K1 madde 6'nın sırası (enerjili ölçümler K1 sonunda) kaynakta yok; rehberde "doğrulanmadı". Sigortaları ve aküyü ilk kez takma sırasını
  veren ayrı bir adım hâlâ yok (F7b-kontrol D-2 son madde).
- "F3" hem kafa hattının sigortası hem de kabuk adımının kodu; K1 / K2'de "F3 (kafa)" diye ayrıldı.
- Zorunlu uyarı denetimi adım düzeyinde: aynı uyarı adımın başka bir satırında da geçiyorsa (E4 Touch VBUS kontrolde de var) tek satırın
  silinmesi yakalanmaz.
- D-3 (küçük yazı: E4 ve K2 7,2 pt), D-6 (tıklama etiketinde FreeCAD `0NN` eki), D-9 (PNG / PDF depo boyutu) açık.

## Düzeltme turu 2 (09.11, son tur; `planlama/d158/F7b-kontrol.md` "Yeniden kontrol (düzeltme 1)", O-4)

Bu turda değişen kaynaklar: `tasarim/freecad/rehber/rehber_metin.py` (K1, F1) ve `rehber_denetim.py` (`ZORUNLU` + 4 satır, `ASCII_TAMAM`
kelimeleri). Başka kaynak dosyaya dokunulmadı; git komutu kullanılmadı.

### Maddeler

| Madde | Durum |
|---|---|
| 1 K1 madde 6: enerjili ölçüm yok, köprüleme talimatı yok; XL4016 ve PC817 tezgâhta; motor yön testi ve BMS F1 sonrası | yapıldı |
| 2 F1: başta "Bağlarken akü ayrık"; kontrolde "İlk enerji" satırı (`elektrik.md:440-461` sırası), kaynakta olmayan "doğrulanmadı" | yapıldı |
| 3 `ZORUNLU`: K1 ve F1 satırları (isteğe bağlı) | yapıldı (4 satır: K1 "K1'de enerji verilmez", K1 "köprülenmez", F1 "Bağlarken akü ayrık", F1 "İlk enerji … BTS EN = 0 … ön şarj") |
| 4 Yeniden üretim + PDF K1 / F1 + tarama | yapıldı (aşağıda) |
| 5 Günlük | bu bölüm |

### Metinler: önce → sonra (kaynak)
- **K1 madde 6.** Önce: "6. Enerjili ölçümler (bağlantılar bitince; aşağıda "enerjili" yazan kontroller): akım sınırlı tezgâh kaynağıyla ya da
  aküyle, ana sigorta takılı, F3 (kafa) takılı değil. Bitince akü XT60'tan yeniden ayrılır: K2 ve kafa işleri enerjisiz yapılır. Bu sıra
  kaynakta yok, doğrulanmadı." Sonra: "6. K1'de enerji verilmez: ana anahtar ve acil stop mantarı F1'de takılır. Mantar ve ana anahtar uçları
  hiçbir zaman köprülenmez; akü XT60 ayrık kalır, boştaki ana hat uçları gerilimsiz ve bantlı. XL4016 ayarı ve PC817 ölçümü kartlar takılmadan
  önce tezgâhta, akım sınırlı tezgâh kaynağıyla yapılır (kontrol); motor yön testi ve ilk açılış F1'in sonunda (İlk enerji). Bu sıra kaynakta
  yok, doğrulanmadı." Gerekçe: anahtarlı bara (BTS, XL4016 A / B / C) yalnız röle K1 kapanınca enerjilenir; röle bobini F5 → mantar (NC)
  üzerinden beslenir ve ön şarj dizisiyle kapanır (`elektrik.md:440-458`); mantar ve ana anahtar F1'de takılır (F1 madde 3–4).
- **K1 kontroller.** Önce: "Enerjili (madde 6): XL4016 A / B / C 6 V, çevre 5 V'a ayarlandı (yükten önce, çıkış ölçülerek)"; "Enerjili (madde 6):
  motor yön testi …"; "Enerjili (madde 6): PC817 modülü 3,3 V'ta ölçüldü …"; "Enerjili (madde 6): ilk açılışta BMS kesiyor mu gözlendi".
  Sonra: "Tezgâhta (kart takılmadan, B3 / B5a öncesi): XL4016 A / B / C 6 V, çevre 5 V'a ayarlandı; akım sınırlı tezgâh kaynağıyla 12 V giriş,
  yüksüz, çıkış ölçülerek"; yeni "Mantar ve ana anahtar uçları köprülenmedi; boştaki ana hat uçları bantlı, akü XT60 ayrık"; "Tezgâhta (akım
  sınırlı tezgâh kaynağıyla): PC817 modülü 3,3 V'ta ölçüldü …"; "Motor yön testi ve ilk açılışta BMS gözlemi burada değil: F1 "İlk enerji"".
  "Akü ayrıkken: bara kapasitesi …" değişmedi (`elektrik.md:462`).
- **F1 iş metni.** Başa eklendi: "Bağlarken akü ayrık (XT60 açık)."
- **F1 kontrol.** Önce: "Mantara basınca röle düşüyor". Sonra (bu satır içine katıldı): "İlk enerji (F1 sonu): ana anahtar ve mantar bağlı, ana
  sigorta takılı, F3 (kafa) takılı değil; tekerlekler yerden kesik (şasi takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0.
  Ana anahtarı aç: BMS kesiyor mu gözle (röle K1 açık, yalnız F3 / F4 / F5 girişleri). Devreye alma ön şarjla: röle K2 → 300 ms → röle K1
  (ESP32 yazılımı). Mantara basınca iki röle de düşüyor. Motor yön testi: her yan ileri komutta ileri döner. Bitince ana anahtarı kapat, aküyü
  XT60'tan ayır (`planlama/adim3/elektrik.md` E9). Bu sıra ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı". Kaynaklar:
  BTS EN = 0 ve motorların ön şarjda çekmemesi `elektrik.md:451`; ön şarj dizisi (K2, 300 ms, K1, sonra K2 bırakılır) `:448, 455-457`; acil stopta
  iki röle birlikte bırakır `:437, 457`; ana anahtar açılışında yalnız F3 / F4 / F5 girişleri, BMS gözlemi `:460-461`; tekerler havada düzeni
  `testler/T13-rampada-acil-stop.md:118` (rampa testinden; bu adım için kaynakta yok, işaretli).
- `rehber_denetim.py`: K1 / F1'in yeni doğru Türkçe kelimeleri (enerji, verilmez, gerilimsiz, sonunda, sonu, tekerlekler, yerden, takozda,
  zaman) gözden geçirilip `ASCII_TAMAM`'a eklendi.

### Komutlar (saat, çıkış)

| Saat | Komut | Çıkış | Sonuç |
|---|---|---|---|
| 18:19 | düzeltilmemiş veriyle denetim (bellek içi) | — | yeni 4 zorunlu satır eksik 4 (beklenen) |
| 18:20 | koşu öncesi sha1 (126 dosya: rehber betikleri, `rehber/` web + veri + görüntü, `planlama/rehber/` kontrol + görüntü + PDF + R-gunluk, F7b belgeleri; scratchpad'deki betikle, git'siz) + `find -newer` işareti | — | 126 dosya |
| 18:20 | süreç 0, boş bellek 2,88 GB, kilit "boş" → kilit "F7b düzeltme turu 2 2026-11-09 18:20 …" → `rehber_uret.py --gorsel-yok` → kilit "boş" (yeniden okundu) | 0 | veri 28 s; mesh 288 / 1192, 189.934 üçgen, GLB 2,56 MB, 50 adım |
| 18:21 | `rehber_denetim.py` | 1 → 0 | ASCII 9 (doğru Türkçe kelimeler) → `ASCII_TAMAM`; sonra ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 15 |
| 18:21–18:26 | `rehber_uret.py --veri-yok` (tüm adımlar) | **0** | 50 / 50, konsol 0, 1192 ↔ 1192, her parça tek adımda; yazdir görüntüsü 50; telefon 7 × 360 / 0; PDF 50 sayfa, taşan yok, küçük yazı E4 7,2 pt, K2 7,2 pt, 3.894 kB; denetim ASCII 0, gruplama 0, çelişki 0, zorunlu eksik 0 / 15, affedilen 6 |
| 18:26 | `py -3 tasarim/freecad/carpisma_kos.py kontrol` | 0 | izlenen 17 dosyanın özetleri kayıtla aynı |
| 18:26 | `py -3 planlama/d158/regresyon.py --yazma` | 0 | GEÇER (kötüleşen yok) |
| 18:26 | `python tasarim/freecad/rehber/rehber_denetim.py` | 0 | aynı |

`lale-rehber` profilli Chrome süreci 0, FreeCAD süreci 0, kilit "boş".

### Koşu öncesi / sonrası sha1 (126 dosya; ilk 12 hane)
Değişen 7, yeni 0, eksilen 0:

| Dosya | Önce | Sonra | Neden |
|---|---|---|---|
| `rehber/veri/rehber-veri.json` | 051ed980a85a | c5415def14e7 | K1 / F1 metni |
| `rehber/veri/rehber-veri.js` | db20f69f9f35 | 78af287a6abf | aynı |
| `planlama/rehber/kontrol.json` | b85a4ee01cff | dea748fbb1d7 | yeni koşu |
| `planlama/rehber/Lale-montaj-rehberi.pdf` | c9a7d8f94612 | 219b8ddc37b2 | K1 / F1 sayfaları |
| `planlama/rehber/goruntu/adim-17.png` | fc87ec718c7c | b953dccd95d4 | K1 paneli |
| `planlama/rehber/goruntu/adim-33.png` | a73c87cba355 | 63d8d0d5e09c | F1 paneli |
| `tasarim/freecad/rehber/rehber_denetim.py` | 9032a0e4d18d | 7d47ef92398e | `ASCII_TAMAM` eki (koşular arasında elle; koşu yazmadı) |

Aynı kalanlar: `rehber_metin.py` (öncesi düzeltilmiş hâliyle alındı), `rehber_uret.py`, `rehber_veri.py`, `rehber_secici.py`, `app.js`,
`stil.css`, `yazdir.html`, `index.html`, `robot.glb`, `robot-glb.js` (yeniden yazıldı, içerik aynı), öbür 48 kontrol PNG'si, 50 yazdır
görüntüsü (yeniden yazıldı, içerik aynı), 7 telefon görüntüsü, `R-gunluk.md`, F7b belgeleri. `find -newer` (.git hariç): koşu boyunca
yazılanlar yalnız yukarıdaki üretim yolları ve kilit dosyası; depoda başka dosya yok.

### Bakılan PDF sayfaları (18:26 PDF'i)
Sayfa 18 (K1: madde 6 "K1'de enerji verilmez … köprülenmez … tezgâhta"; kontroller "Tezgâhta …", "köprülenmedi", "burada değil: F1 İlk
enerji"; tek sayfa, 9,6 pt) ve 34 (F1: başta "Bağlarken akü ayrık (XT60 açık)."; kontrolde "İlk enerji (F1 sonu) …" satırı; tek sayfa).

### Dokunulan dosyalar (bu tur)
`tasarim/freecad/rehber/rehber_metin.py`, `tasarim/freecad/rehber/rehber_denetim.py`; üretilen: `rehber/veri/rehber-veri.json`, `.js`,
`planlama/rehber/kontrol.json`, `planlama/rehber/Lale-montaj-rehberi.pdf`, `planlama/rehber/goruntu/adim-17.png`, `adim-33.png`;
bu günlük. Commit dosya kümesi değişmedi (F7b-kontrol "C için kesin git add listesi", 122 dosya).

### Açıklar (bu turdan)
- XL4016 ayarı ve PC817 ölçümü B3 / B5a'da kartlar takılmadan yapılmalı; B3 / B5a metni bunu söylemiyor (yalnız K1 kontrolünde "B3 / B5a
  öncesi" yazıyor). Bu tur yalnız K1 / F1 ile sınırlıydı; P7.3'e öneri: B3 ve B5a'ya bir kontrol satırı.
- F1 "İlk enerji" sırası ve tekerlerin yerden kesik düzeni bu adım için kaynakta yok (rampa testinden alındı), "doğrulanmadı".
- Devreye alma ESP32 yazılımına bağlı (ön şarj dizisi); yazılım hazır değilse F1'de yalnız ana anahtar açılışı ve BMS gözlemi yapılabilir. Metin
  bunu ayrıca söylemiyor.
- D-1' (zorunlu uyarı denetimi yalnız varlığa bakıyor; "yasak ifade" listesi yok), D-3, D-6 açık; D-9 P9.3'te.
