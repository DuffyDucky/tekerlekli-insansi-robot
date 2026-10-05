# Tekerlekli insansı robot — üniversite projesi

Manisa Celal Bayar Üniversitesi Mekatronik MYO'da 4 kişilik ekiple yapılacak, bacaksız, tekerlekle
hareket eden, gövde + kafa + 2 kollu insansı robot. Bu klasör projenin tek çalışma alanı: raporlar,
planlama, tasarım (CAD) ve ileride yazılım kodu burada tutulur.

## Klasör yapısı

| Klasör / dosya | İçerik |
|---|---|
| `raporlar/Humanoid-Robot-Fizibilite-Raporu.html` | Fizibilite raporu: maliyet, ses mi görüntü mü, yetkinlik, teknik gereklilikler, profesyonel destek, takvim, finansman, riskler |
| `raporlar/kaynaklar/` | Raporun dayandığı araştırma notları (donanım/maliyet, yazılım/yapay zekâ, referans projeler/finansman, parça ölçüleri, fiyat araştırması ve doğrulaması) |
| `planlama/proje-plani.md` | Kapsam, takvim, roller, ilk iki hafta, riskler, açık sorular |
| `planlama/maliyet.json` | Doğrulanmış malzeme maliyeti (satıcı, TL, bağlantı, stok); demodaki maliyet bölümünün tek kaynağı |
| `tasarim/Robot-Tasarim-Demosu.html` | Gerçek parçalarla 3B CAD montajı; V1 / V2 düğmesi; devrilme, motor ve servo hesabı canlı; TL + USD proje maliyeti |
| `tasarim/cad/Humanoid-Robot-Montaj.step` · `-V2` · `-V3` | SolidWorks'te açılan montaj dosyaları (V1, V2, V3) |
| `tasarim/cad/parca-listesi.csv` · `-V2` · `-V3` | Gerçek parça listesi (model, ölçü, adet, kütle) |
| `tasarim/cad/robot_cad.py` | Modeli üreten kod (STEP + CSV + demo) |
| `tasarim/cad/demo_uret.py` | Demoyu şablon + model + maliyetten yeniden üretir; CadQuery gerekmez |
| `CLAUDE.md` | Bu klasörde açılan yapay zekâ oturumları için bağlam |

HTML dosyaları çift tıklayınca tarayıcıda açılır. Demodaki 3B görünüm için internet gerekir.

## Proje çerçevesi (Duffy, 26 Eylül 2026)

- Ekip: **4 kişi**
- Süre: **normalde 1 dönem**, proje başarılı giderse muhtemelen 2 dönem
- Bütçe: **okul / hoca destekli**
- Karar verilmemiş: robot yalnız sesle mi etkileşsin, ses + görüntüyle mi

## Şu ana kadarki kararlar ve öneriler

| Konu | Öneri / sonuç |
|---|---|
| Ses mi görüntü mü | Önce ses + tekerlek + kayıtlı jestler. İkinci adım "hafif görüntü": yüzü algılayıp kafayı kişiye çevirme ve düğmeyle "ne görüyorsun?". Yüz **tanıma**, otonom gezinme (ROS 2 / Nav2), eşya tutan kol kapsam dışı. |
| Konuşma zinciri | Bulut konuşma tanıma (Türkçe) + bulut dil modeli + seslendirme; uyandırma kelimesi yerine bas-konuş düğmesi; internet kesilirse çevrimdışı yedek mod |
| Bütçe | CAD tasarımının doğrulanmış malzeme listesi (27 Eylül 2026): **≈ 64.500 TL ≈ 1.320 USD** (%15 pay, yedek parça ve kargo dahil); 54 kalemin 48'i satıcı sayfasından doğrulandı. Baskı hizmetiyle ≈ 68.800 TL. Aylık bulut ≈ 10–20 $. (Fizibilite tahmini ≈ 61.700 TL'ydi.) |
| Ekip | Yazılım / yapay zekâ sorumlusu şart; güç elektroniği ve KVKK için danışman |
| Güvenlik | LiPo yerine LiFePO4 akü, donanımsal acil stop, servo ve işlemci için ayrı güç hatları |
| Mekanik | Ağırlığı alta topla, tabanı geniş tut, robotu kat kat kur ve her katta test et |
| V2 (hoca, 2 Ekim 2026) | 10,1" dokunmatik ekran göğüste, kafada iki yuvarlak göz ekranı (Pepper benzeri; Duffy A seçeneğini seçti). Tekerlekler yerinde, taban kabuğu genişleyip onları sarıyor. Malzeme ≈ 77.900 TL (%15 pay dahil; V1 64.500). |
| V3 deneme (Duffy, 2 Ekim 2026) | V2 yorumu: "taban çok geniş", "ekran çok alçakta", "yüz ifadesi çok ruhsuz". V3: boy 125 cm, şase 27 cm (akünün sığdığı en dar), taban 44 cm ve yukarı 30 cm'ye daralan etek, 10,1" ekran üst göğüste 15° yukarı eğik (merkez 82 cm), kafada 7" yüz ekranı + siyah akrilik yüz paneli (Pi 5 iki HDMI). Malzeme ≈ 79.400 TL. |

## CAD modelinden çıkanlar (varsayılan tasarım)

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
2. **Fiziksel yapı endişesi:** Duffy: "beni korkutan fiziksel yapısı". Yaklaşım: robot aslında
   "insan gibi görünen bir servis arabası"; ağırlık alta, katman katman yapım ve test.
3. **Tasarım demosu v1:** basit kutularla 3B model, kaydırıcılarla devrilme/motor/servo hesabı.
4. **Gerçek parçalarla CAD (v2):** Duffy: "buna reel bir görünüm kazandır kullanacağın parçalar
   gerçek olsun hatta solid gibi bir yerde çiz". Bilgisayarda CAD programı olmadığı için CadQuery
   ile gerçek ölçülü montaj kuruldu; 19 parçanın ölçüsü araştırıldı (12'si üretici çiziminden) →
   `raporlar/kaynaklar/04-parca-olculeri.md`. STEP dosyası geri okuma testinden geçti (218 geçerli katı).
5. **Taşıma:** proje DuffyOS vault'undan bu klasöre taşındı; bundan sonraki çalışmalar burada.

## Açık işler

- [ ] Robotun amacını hocayla netleştir (karşılama / tanıtım / rehber) → kapsam ve malzeme listesi kesinleşir
- [ ] İşletmede Mesleki Eğitim (4. yarıyıl, 2027 bahar) projenin 2. dönemini daraltır mı? Bölüme sor
- [ ] Rolleri yaz; yazılım sorumlusu yoksa bilgisayar mühendisliğinden ortak ara
- [ ] Bölümde hazır malzemeyi listele (3D yazıcı, dizüstü, profil, güç kaynağı)
- [ ] Siparişi erken ver: 27 Eylül'de enkoderli JGB37 yalnız Direnc.net'te stokta; Camera Module 3 Türkiye'de hiçbir satıcıda yok (stok alarmı ya da Adafruit)
- [ ] Limacell 24 Ah akünün ölçüsünü satıcıya sor (CAD yuvası 181 × 77 × 167 mm)
- [ ] Lazer kesim (Al plaka, kontrplak) için DXF ile online teklif al; tahmini 2.000 TL
- [ ] JGB37 braketini alırken delik düzenini kontrol et (mil 7 mm kaçık; çoğu satıcı ortalı mil braketi satıyor)
- [ ] STEP dosyasını SolidWorks'te aç (henüz denenmedi)
- [ ] Parçalar gelince tahmini ölçüleri kumpasla doğrula (enkoder boyu, braket delikleri, BTS7960 delikleri)
- [ ] Ağırlık için hafif profil (40×40 hafif veya 30×30) seçeneğini değerlendir (≈ 2 kg, tahmini)
- [x] Hoca geri bildirimi (2 Ekim 2026): (1) ekran daha büyük olsun (şu an 7"); (2) tekerlekler dışarıda
  değil, kabuğun içine gömülü olsun. Hoca: ekran gövdede de olabilir. Karar (Duffy): tekerlekler yerinde kalır,
  kabuk dışa genişleyip tekerlekleri sarar; yüz A seçeneği (göğüste ekran + kafada göz ekranları). → Demoda V2.
  SolidWorks tasarımında da uygulanacak.
- [ ] V2 kabuklarının 23 cm'lik baskı bölme çizgileri ve birleşme yerleri (SolidWorks'te)
- [ ] 10,1" ekranın 5 V ≈ 0,75 A beslemesini güç planına ekle; ekran ve göz ekranı kütlelerini tartıp CAD'e gir
- [ ] Okulun 3D yazıcı tablası 25 × 25 × 25 cm (hocanın söylediği; model doğrulanmadı). Her baskı parçası
  buna sığacak şekilde bölünmeli (pay için ≤ 23 cm hedef)

## CAD'i yeniden üretme

`tasarim/cad/robot_cad.py` başındaki ölçü ve yerleşim değerleri değiştirilip çalıştırılınca STEP,
parça listesi ve demo birlikte yenilenir. Python 3.12 + CadQuery 2.8 gerekir (`requirements.txt`).
Sanal ortamı OneDrive dışında kur (yüzlerce MB):

```powershell
uv venv --python 3.12 $env:LOCALAPPDATA\robot-cad-venv
uv pip install --python $env:LOCALAPPDATA\robot-cad-venv\Scripts\python.exe -r tasarim\cad\requirements.txt
cd tasarim\cad
& $env:LOCALAPPDATA\robot-cad-venv\Scripts\python.exe robot_cad.py . model.json
```

Koordinatlar SolidWorks ile aynı: Y yukarı, Z ileri (robotun yüzü +Z), X sağ-sol, birim mm.

Yalnız fiyat ya da demo arayüzü değiştiyse CadQuery gerekmez: `planlama/maliyet.json` veya
`tasarim/cad/viewer-template.html` düzenlendikten sonra `python tasarim\cad\demo_uret.py` demoyu yeniler
(3B modeli mevcut demodan alır).
