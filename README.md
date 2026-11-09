# Tekerlekli insansı robot — üniversite projesi

Manisa Celal Bayar Üniversitesi Mekatronik MYO'da 4 kişilik ekiple yapılacak, bacaksız, tekerlekle
hareket eden, gövde + kafa + 2 kollu insansı robot. Bu klasör projenin tek çalışma alanı: raporlar,
planlama, tasarım (CAD) ve ileride yazılım kodu burada tutulur.

## Klasör yapısı

| Klasör / dosya | İçerik |
|---|---|
| `tasarim/freecad/` | **Güncel tasarım (1,58 m):** FreeCAD modülleri (iskelet, kabuk, omuz, dirsek, kafa, taban), `arayuz.py` (tek ölçü kaynağı), ana montaj `montaj/` (FCStd, STEP, `robot-bom.csv`) |
| `kod/ortak/eklem_sinirlari.json` | Eklem sınırları (CAD'den `eklem_sinirlari_uret.py` ile üretilir, elle düzenlenmez) |
| `planlama/dongu-158.md` · `planlama/d158/` | Güncel iş döngüsü (1,58 m, F0–F9), paket brief / günlük / kontrol dosyaları, karar kuyruğu (`d158/karar-kuyrugu.md`) |
| `planlama/dongu.md` | Tarihçe: 1,65 m iş döngüsü (Y1–Y6); `planlama/y2/` Y2a/Y2b günlük ve kontrolleri; `planlama/kararlar-*.md` karar günlüğü |
| `rehber/` · `tasarim/freecad/rehber/` · `planlama/rehber/R-gunluk.md` | 3B montaj rehberi (`rehber/index.html`; 1,58 m modelinden, 50 adım, 1.192 parça), yazdırılabilir rehber `planlama/rehber/Lale-montaj-rehberi.pdf` (54 sayfa), onu üreten betikler ve çalışma günlüğü. Sayıların kaynağı `planlama/rehber/kontrol.json` (`ozet.adim`, `ozet.parca_rehber`, `yazdir.pdf_sayfa` / `yazdir.sayfa_esleme`) |
| `planlama/baski-listesi.md` · `planlama/adim3/elektrik.md` · `planlama/yazilim-plani.md` | Baskı listesi (1,58 m, 72 parça; 09.11, tek analiz `tasarim/freecad/lale158/baski-analiz.json`), elektrik kararları (E0–E9; 1,58 m bölümü başta), yazılım planı |
| `raporlar/Humanoid-Robot-Fizibilite-Raporu.html` | Fizibilite raporu: maliyet, ses mi görüntü mü, yetkinlik, teknik gereklilikler, profesyonel destek, takvim, finansman, riskler |
| `raporlar/kaynaklar/` | Raporun dayandığı araştırma notları (donanım/maliyet, yazılım/yapay zekâ, referans projeler/finansman, parça ölçüleri, fiyat araştırması ve doğrulaması) |
| `planlama/proje-plani.md` | Kapsam, takvim, roller, ilk iki hafta, riskler, açık sorular |
| `planlama/maliyet.json` | Doğrulanmış malzeme maliyeti (satıcı, TL, bağlantı, stok); demodaki maliyet bölümünün tek kaynağı |
| `tasarim/Robot-Tasarim-Demosu.html` | Lale tasarım demosu, 1,58 m (P9.2, `planlama/d158/F9b-*`): sayfadaki sayılar 127 JSON anahtarından üretilir (boy 1.580 mm: `tasarim/freecad/lale158/lale158-kontrol.json` `toplam_boy_mm`); 3B model rehberin GLB'si (`rehber/veri/robot-glb.js`, `rehber-veri.js`) göreli bağlantıyla, 1.192 parça; açık kararlar "karar bekliyor"; maliyet `planlama/maliyet.json`. Bu sürüm `lale-duzeltme` dalında |
| `tasarim/cad/Humanoid-Robot-Montaj.step` · `-V2` · `-V3` | Eski CadQuery montajları (V1, V2, V3; arşiv) |
| `tasarim/cad/parca-listesi.csv` · `-V2` · `-V3` | Gerçek parça listesi (model, ölçü, adet, kütle) |
| `tasarim/cad/robot_cad.py` | Eski CadQuery modelini üreten kod (STEP + CSV; arşiv); bu model artık demoda kullanılmaz |
| `tasarim/cad/demo_uret.py` | Demoyu şablon + kaynak JSON'lar + maliyetten yeniden üretir; FreeCAD / CadQuery gerekmez; denetimi `planlama/d158/F9b-dogrula.py` |
| `CLAUDE.md` | Bu klasörde açılan yapay zekâ oturumları için bağlam |

HTML dosyaları çift tıklayınca tarayıcıda açılır. Demodaki 3B görünüm için internet gerekir.

## Güncel tasarım: 1,58 m (01.11.2026 kararı, 03.11.2026 CAD; sayılar 09.11.2026)

Ana tasarım `tasarim/freecad/`; iş döngüsü `planlama/dongu-158.md`, açık kararlar `planlama/d158/karar-kuyrugu.md`.
Sayıların kaynağı: `tasarim/freecad/montaj/montaj-analiz.json` (MA), `tasarim/freecad/lale158/lale158-kontrol.json` (LK),
`tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json` (UI), `tasarim/freecad/kafa/kafa-analiz.json` (KA), `tasarim/freecad/montaj/robot-bom.csv` (BOM),
`planlama/d158/regresyon.json` (korunan değerler).

| Konu | Değer |
|---|---|
| Boy | **1.580,0 mm** (yerden kafa tepesine; LK `toplam_boy_mm`, MA `boy_mm`); gövde direği 1.115,5 mm tek parça sigma 40 × 40 (BOM), omuz traversi merkezi y 1.270 mm, gövde uzatması 315 mm (MA `s3_mm`, `uzama_mm`) |
| Parça / kütle | 1.179 parça (MA `parca_sayisi`), ana montaj 25.720,55 g (MA `kutle_g`); ev pozu, 400 g kablo payıyla (UI `kablo_payi.kutle_g`) **26.120,6 g** (UI `ev.kutle_g`), AM (−0,03; 522,84; −10,03) mm (UI `ev.am`) |
| Taban | 520 mm (MA `taban_w_mm`), teker izi 432 mm (x ±216; `planlama/y2/Y2b-ivme.json` `teker_hatti`), 4 × JGB37; akü Victron 12,8 V 20 Ah, **3,0 kg**, yerinde (BOM; karar 29.10) |
| Devrilme | Yüksüz, 5° rampa, en kötü kol pozu: pay **1,519** (eşik 1,5; UI `izgara_yuk_0g.a_sinir_pay15.rampa5_geri`); düz zeminde 2,097 (`duz_geri`) |
| Kollar | Kol başına 4 servo: omuz S1 + S2 **DS3235**, dirsek + bilek MG996R; kafa pan / tilt MG996R (**toplam 10 servo**; BOM: DS3235 × 4, MG996R × 6). El yükü sınırı **karar bekliyor (K3, K9)**; öneri düzde ≤ 100 g / el |
| Kafa | 10,1" QLED 1280 × 720 HDMI yüz ekranı (BOM), Raspberry Pi 5 4 GB kafada, 5 V: Pololu D24V50F5 (Pi) + SY8205 (ekran). Kafa grubu 1.570,8 g; tilt payı (±15) 3,64, pan payı 2,21 (KA `tork`); tilt sınırı ±13° (karar 29.10, `kod/ortak/eklem_sinirlari.json`; main'deki kod ±20 kullanıyor, ±20'de çakışma var, pano #6) |
| Göğüs | 11,6" 1080p HDMI kasalı ekran, gövdeye gömülü (BOM); kumanda telefondan |
| Ses | ReSpeaker Mic Array v2.0 (kafa) + USB ses kartı + PAM8403 (kafa sol duvarı) + 40 mm 3 W hoparlör (gövde) (BOM); mikrofon-hoparlör en az 574,3 mm. PAM 5 V besleme noktası **karar bekliyor (K10)**; 6. USB cihazı bekliyor (K1) |
| Elektrik | `planlama/adim3/elektrik.md` "158 cm güncellemesi": USB port dağılımı, boyun demeti (12 V + tilt + göğüs HDMI + hub uzatması + hoparlör; Efe teyidi K14), göğüs ekranı 12 V dalı (K11) |
| Yazılım sınırları | Rampada / eğimde kollar ev pozunda, ivme ve fren ≤ 0,1 m/s²; düz zeminde ivme ≤ 0,5, fren ≤ 1,8 m/s² (`kod/ortak/eklem_sinirlari.json` `teker.ivme_sinir_m_s2`; karar 29.10); S2 ≥ +5° |
| Baskı | 72 parça (13'ü destekli), destek dahil 7.668,9–7.726,7 g filament, 159,9–161,08 sa (`tasarim/freecad/lale158/baski-analiz.json` `toplam`; F6b tek analiz, liste `planlama/baski-listesi.md`) |
| Maliyet | `planlama/maliyet.json` (tarih 2026-11-09): 29.10 listesi P8.1 sipariş paketiyle (`planlama/d158/F8a-siparis.md`) 1,58 m'ye kısmen güncellendi: satıcı ve fiyatlar 09.11 sayfalarından, göğüs ekranı 11,6", ReSpeaker v2.0, D24V50F5, kafa kabloları. V3 satırları, yazıcıyla, yedek ve %15 pay dahil **≈ 118.700 TL** (koşullularla ≈ 124.600); bulunamayan 2 kablo fiyatsız, toplama girmiyor. Yüz ekranı hocadan gelirse ve elimizdekiler (Pi 5, hafıza kartı) düşülürse ≈ 93.800 TL; yüz ekranı satın alınırsa (QLED, K32) ≈ 102.100. Sipariş paketinin kendi toplamı (baskı hizmetiyle, pay dahil) ≈ 107.600 TL; sipariş verilmedi |
| Kapsam | Otonom gezinme, lidar, ROS 2 / Nav2 **yok** (hoca, 21 Ekim); kumandayla sürüş + konuşma + jest |

**Tarihçe:** hoca 1,70 m ve 10" kafa istedi (21 Ekim); boy 29 Ekim'de 1,65 m'ye (Y2a; o tasarımda 1.650 mm, 1.120 parça, 24,56 kg,
maliyet ≈ 103.800 TL; `planlama/y2/`), 01.11'de 1,58 m'ye indi. 1,65 m ve öncesinin sayıları git geçmişinde ve `planlama/y2/`, `planlama/dongu.md` içinde.

Aşağıdaki bölümler projenin geçmişidir (Eylül–Ekim, CadQuery V1–V3, 115–125 cm); güncel sayılar yukarıda ve `planlama/` belgelerinde.
Bu bölümlerdeki tablolar ve "Açık işler" listesi Eylül–Ekim tarihlidir (7" ekran, 2,8 kg akü gibi değerler o günün); güncel açık işler `planlama/dongu-158.md` ve karar kuyruğunda.

## Proje çerçevesi (Ahmet Yorulmaz, 26 Eylül 2026)

- Robotun adı: **Lale** (Ahmet, 11 Ekim 2026)
- Ekip: **4 kişi**
- Süre: **normalde 1 dönem**, proje başarılı giderse muhtemelen 2 dönem
- Bütçe: **okul / hoca destekli**
- Karar verilmemiş: robot yalnız sesle mi etkileşsin, ses + görüntüyle mi

## Şu ana kadarki kararlar ve öneriler

| Konu | Öneri / sonuç |
|---|---|
| Ses mi görüntü mü | Önce ses + tekerlek + kayıtlı jestler. İkinci adım "hafif görüntü": yüzü algılayıp kafayı kişiye çevirme ve düğmeyle "ne görüyorsun?". Yüz **tanıma**, otonom gezinme (ROS 2 / Nav2, lidar; hoca 21 Ekim 2026: iptal), eşya tutan kol kapsam dışı. |
| Konuşma zinciri | Bulut konuşma tanıma (Türkçe) + bulut dil modeli + seslendirme; uyandırma kelimesi yerine bas-konuş düğmesi; internet kesilirse çevrimdışı yedek mod |
| Bütçe | CAD tasarımının doğrulanmış malzeme listesi (27 Eylül 2026): **≈ 64.500 TL ≈ 1.320 USD** (%15 pay, yedek parça ve kargo dahil); 54 kalemin 48'i satıcı sayfasından doğrulandı. Baskı hizmetiyle ≈ 68.800 TL. Aylık bulut ≈ 10–20 $. (Fizibilite tahmini ≈ 61.700 TL'ydi.) |
| Ekip | Yazılım / yapay zekâ sorumlusu şart; güç elektroniği ve KVKK için danışman |
| Güvenlik | LiPo yerine LiFePO4 akü, donanımsal acil stop, servo ve işlemci için ayrı güç hatları |
| Mekanik | Ağırlığı alta topla, tabanı geniş tut, robotu kat kat kur ve her katta test et |
| V2 (hoca, 2 Ekim 2026) | 10,1" dokunmatik ekran göğüste, kafada iki yuvarlak göz ekranı (Pepper benzeri; Ahmet A seçeneğini seçti). Tekerlekler yerinde, taban kabuğu genişleyip onları sarıyor. Malzeme ≈ 77.900 TL (%15 pay dahil; V1 64.500). |
| V3 deneme (Ahmet, 2 Ekim 2026) | V2 yorumu: "taban çok geniş", "ekran çok alçakta", "yüz ifadesi çok ruhsuz". V3: boy 125 cm, şase 27 cm (akünün sığdığı en dar), taban 44 cm ve yukarı 30 cm'ye daralan etek, 10,1" ekran üst göğüste 15° yukarı eğik (merkez 82 cm), kafada 7" yüz ekranı + siyah akrilik yüz paneli (Pi 5 iki HDMI). Malzeme ≈ 79.400 TL. |

## CAD modelinden çıkanlar (eski CadQuery V1 varsayılan tasarım, 115 cm)

| Konu | Sonuç |
|---|---|
| Ölçü | 48 × 52 × 115 cm (teker dahil genişlik × derinlik × boy) |
| Toplam kütle | 17,75 kg (0,6 kg vida/kablo payı dahil) |
| En ağır kalemler | 40×40 ağır sigma ≈ 5,3 kg · LiFePO4 akü 2,8 kg · PETG kabuklar ≈ 3,3 kg · alt plaka 1,3 kg |
| Ağırlık merkezi | yerden 291 mm, merkezin 17 mm gerisinde |
| Devrilme | ileri frende 6,8, geri frende 5,7 m/s² (acil stop payı 3,8×); yana 7,2 m/s² |
| Taban motoru | 4× JGB37, 5° rampada motor başına 4,7 kg·cm (sürekli sınırın %74'ü) |
| Kol | 386 g; omuz 5,4 kg·cm (DS3218 güvenli sınır 10), dirsek 1,0 kg·cm (MG996R sınır 5) |
| **V2 farkı** | Ölçü 51 × 52 × 115 cm · 18,9 kg · ağırlık merkezi 282 mm · devrilme ileri 6,9, geri 5,9 m/s² (pay 4,0×), yana 7,4 · motor 5,0 kg·cm (%79) · PETG ≈ 4,4 kg · taban kabuğu 513 × 227 × 520 (9 baskı parçası), gövde 6, kafa 2 · çakışma yok (kol × gövde 2.822 mm³ V1'den kalma) |
| **V3 farkı** | Ölçü 44 × 52 × 125 cm · 18,6 kg · ağırlık merkezi 337 mm · devrilme ileri 5,8, geri 5,0 m/s² (pay 3,3×), yana 5,2 (3,4×) · motor 4,9 kg·cm (%77) · PETG ≈ 4,4 kg · etek 6, gövde 8, kafa 2 baskı parçası · çakışma yok (kol × gövde 2.299 mm³, V1'den kalma sorun) |
| Yapı | 340×500 sigma çerçeve; altta 3 mm Al plaka + yatık akü (arka) + motor sürücüleri (ön); 40 mm burç üstünde 5 mm kontrplak elektronik katı; motorlar L braketle plaka altında; tek sigma direk + 200 mm omuz traversi; PETG kabuklar |

## Konuşma geçmişi (26 Eylül 2026)

1. **Fizibilite araştırması:** üç paralel araştırma (donanım-maliyet, yazılım-yapay zekâ, referans
   projeler-finansman-destek) → `raporlar/`. Ajan çıktılarında iki düzeltme yapıldı: 2 JGB37 motor
   15–20 kg'a yetmez (≤15 kg ya da 4 motor); LiPo yerine LiFePO4.
2. **Fiziksel yapı endişesi:** Ahmet: "beni korkutan fiziksel yapısı". Yaklaşım: robot aslında
   "insan gibi görünen bir servis arabası"; ağırlık alta, katman katman yapım ve test.
3. **Tasarım demosu v1:** basit kutularla 3B model, kaydırıcılarla devrilme/motor/servo hesabı.
4. **Gerçek parçalarla CAD (v2):** Ahmet: "buna reel bir görünüm kazandır kullanacağın parçalar
   gerçek olsun hatta solid gibi bir yerde çiz". Bilgisayarda CAD programı olmadığı için CadQuery
   ile gerçek ölçülü montaj kuruldu; 19 parçanın ölçüsü araştırıldı (12'si üretici çiziminden) →
   `raporlar/kaynaklar/04-parca-olculeri.md`. STEP dosyası geri okuma testinden geçti (218 geçerli katı).
5. **Taşıma:** proje kişisel not deposundan (vault) bu klasöre taşındı; bundan sonraki çalışmalar burada.

## Açık işler

- [ ] Robotun amacını hocayla netleştir (karşılama / tanıtım / rehber) → kapsam ve malzeme listesi kesinleşir
- [ ] İşletmede Mesleki Eğitim (4. yarıyıl, 2027 bahar) projenin 2. dönemini daraltır mı? Bölüme sor
- [ ] Rolleri yaz; yazılım sorumlusu yoksa bilgisayar mühendisliğinden ortak ara
- [ ] Bölümde hazır malzemeyi listele (3D yazıcı, dizüstü, profil, güç kaynağı)
- [ ] Siparişi erken ver: 27 Eylül'de enkoderli JGB37 yalnız Direnc.net'te stokta; Camera Module 3 Türkiye'de hiçbir satıcıda yok (stok alarmı ya da Adafruit)
- [x] ~~Limacell 24 Ah akünün ölçüsünü satıcıya sor~~ → akü Victron SuperPack 12,8 V 20 Ah (K3, 14 Ekim 2026), ölçüsü CAD yuvasıyla aynı
- [ ] Lazer kesim (Al plaka, kontrplak) için DXF ile online teklif al; tahmini 2.000 TL
- [ ] JGB37 braketini alırken delik düzenini kontrol et (mil 7 mm kaçık; çoğu satıcı ortalı mil braketi satıyor)
- [ ] STEP dosyasını SolidWorks'te aç (henüz denenmedi)
- [ ] Parçalar gelince tahmini ölçüleri kumpasla doğrula (enkoder boyu, braket delikleri, BTS7960 delikleri)
- [ ] Ağırlık için hafif profil (40×40 hafif veya 30×30) seçeneğini değerlendir (≈ 2 kg, tahmini)
- [x] Hoca geri bildirimi (2 Ekim 2026): (1) ekran daha büyük olsun (şu an 7"); (2) tekerlekler dışarıda
  değil, kabuğun içine gömülü olsun. Hoca: ekran gövdede de olabilir. Karar (Ahmet): tekerlekler yerinde kalır,
  kabuk dışa genişleyip tekerlekleri sarar; yüz A seçeneği (göğüste ekran + kafada göz ekranları). → Demoda V2.
  SolidWorks tasarımında da uygulanacak.
- [ ] V2 kabuklarının 23 cm'lik baskı bölme çizgileri ve birleşme yerleri (SolidWorks'te)
- [ ] 10,1" ekranın 5 V ≈ 0,75 A beslemesini güç planına ekle; ekran ve göz ekranı kütlelerini tartıp CAD'e gir
- [ ] Okulun 3D yazıcı tablası 25 × 25 × 25 cm (hocanın söylediği; model doğrulanmadı). Her baskı parçası
  buna sığacak şekilde bölünmeli (pay için ≤ 23 cm hedef)

## Montaj rehberini üretme

```powershell
python tasarim/freecad/rehber/rehber_uret.py
```

Bu komut CAD modüllerinden adım verisini ve mesh'i üretir (FreeCAD, `rehber/veri/`), her adımı başsız Chrome/Edge ile kontrol eder ve görüntüleri `planlama/rehber/goruntu/` altına yazar (özet `planlama/rehber/kontrol.json`). Tüm adımlar yaklaşık 5 dakika sürer.
Yalnız tarayıcı kontrolü için `--veri-yok`, yalnız veri için `--gorsel-yok`, seçili adımlar için `--adimlar 1,4,9`. Rehberi açmak için `rehber/index.html` (3B için internet gerekir).
Adım yazıları `tasarim/freecad/rehber/rehber_metin.py`, adım seçicileri (1,58 m) `tasarim/freecad/rehber/rehber_secici.py` içinde. Üretmeden önce `planlama/rehber/R-gunluk.md` "Yapılacaklar"daki açık maddelere bak.

## CAD'i yeniden üretme

Bu bölüm eski CadQuery modeli (V1–V3, 125 cm) içindir. `tasarim/cad/robot_cad.py` başındaki ölçü ve yerleşim
değerleri değiştirilip çalıştırılınca STEP ve parça listesi yenilenir; sonunda demo da yeniden üretilir ama CadQuery
modeli demoya girmez. Python 3.12 + CadQuery 2.8 gerekir (`requirements.txt`).
Sanal ortamı OneDrive dışında kur (yüzlerce MB):

```powershell
uv venv --python 3.12 $env:LOCALAPPDATA\robot-cad-venv
uv pip install --python $env:LOCALAPPDATA\robot-cad-venv\Scripts\python.exe -r tasarim\cad\requirements.txt
cd tasarim\cad
& $env:LOCALAPPDATA\robot-cad-venv\Scripts\python.exe robot_cad.py . model.json
```

Koordinatlar SolidWorks ile aynı: Y yukarı, Z ileri (robotun yüzü +Z), X sağ-sol, birim mm.

Demo için CadQuery gerekmez: `planlama/maliyet.json`, kaynak JSON'lar ya da `tasarim/cad/viewer-template.html`
değiştikten sonra `py -3 tasarim/cad/demo_uret.py` demoyu yeniler (3B model `rehber/veri/robot-glb.js` ve
`rehber-veri.js` dosyalarından göreli bağlantıyla okunur; sayfa `rehber/` klasörüyle birlikte açılmalı).
