# Sağ / sol kararı (K65): CAD'in "sağ"ı robotun kendi solu

16.11.2026, P10.7b2e kısım 2. Karar: orkestratör (Echo). Okuyacak: Efe (yazılım), montaj ekibi. Kuyruk maddesi:
`planlama/d158/karar-kuyrugu.md` K65.

Kısa: kablolar, CAD ve montaj rehberi "sağ" derken **robota önden bakan kişinin sağını** kastediyor. ESP32 yazılımı "sağ" derken
**robotun kendi sağını** kastediyor. Bu ikisi ters taraflar. Kablolar değişmiyor; rehbere tanım cümlesi girdi; yazılımın eşlemesi
düzeltilmeli (aşağıda § 3).

## 1. Bulgu ve kanıt

**Eksenler (CAD, `tasarim/freecad/arayuz.py`):** +Y yukarı, +Z ileri (yüz), eksenler sağ elli (FreeCAD / CadQuery). Sağ elli bir
sistemde Y yukarı ve Z ileri iken +X robotun kendi **solu**dur.

Bu hüküm bu pakette ayrıca sınandı (yalnız araştırmaya dayanmadan):

- Ön +Z: sonarlar z > 0 (`tasarim/freecad/taban/taban-analiz.json`, sonar parçalarının merkezi önde); acil stop mantarı x +117, z −200
  (arka).
- Yan görünüş: `tasarim/freecad/montaj/gorsel/montaj-yan.png` kamerası tam +X'te (`montaj/montaj_gorsel.py`). Karede göğüs ekranı
  (ön) görüntünün solunda, acil stop mantarı sağında. Robotun kendi sağ yanından bakan biri robotun önünü kendi sağında görür; burada
  ön solda görünüyor, demek ki kamera robotun kendi **sol** yanında. +X = robotun kendi solu.

**"sağ" adı +X'e bağlı (CAD):** `taban_parcalar.py` `SX(sx)`: x > 0 ise "sag" (motorlar, braketler, tekerler); BTS7960 sol / sağ
x −67 / +68; sağ omuz / kol x +185, "SOL" yazılan aynalı kol −X'te; acil stop x +117 (arka sağ), ana anahtar x −117 (arka sol). Rehber
verisinde konumu belli parça adlarından 528'i bu kurala uyuyor; uymayan 14 ad ya "sağ/sol" ikisini birden taşıyor (kafa kabuğu
cıvataları) ya da işlev adı (XL4016 A "(sağ kol)": sağ kolu besler, kendisi x ≈ −7…−29).

**Belgeler bu adla tutarlı:** `planlama/adim3/kablolar.json` (G12 / G13, M01–M04, B01 / B02, N01 / N02, Q01 / Q03, S01–S08,
SV1 / SV2), `planlama/adim3/pin-haritasi.md` (§ 2 tablo, § 2 PCA9685 kanalları), montaj rehberi kareleri ve metni. Hiçbirinde "sağ"ın
kimin sağı olduğu yazılı değildi.

**Yazılım (`origin/main` 71cf76d) robotun kendi çerçevesini kullanıyor:**

- `kod/esp32/src/motorlar.cpp` `motorlar_hedef`: `v_sol = v − w·b/2`, `v_sag = v + w·b/2`; `kod/esp32/OKU_BENI.md`: `w` rad/s
  "sola +", IMU yaw "sola +". Standart diferansiyel sürüş: "sağ teker" robotun kendi sağı.
- `kod/jestler/kanallar.yaml`: `kafa_pan` "küçük = robotun sağına, büyük = soluna".
- `kod/esp32/OKU_BENI.md` kalibrasyon 3: `kafa_pan` 70 "robotun sağına bakmalı".

## 2. Karar

1. Donanım adları **korunur** (CAD, kablo tablosu, rehber, pin haritası). Bütün donanım belgelerini robotun kendi çerçevesine çevirmek
   kablolar.json, rehber metni, `taban_parcalar.py` SX(), pin haritası ve bütün karelerin yeniden üretimi demek; bu pakette yapılmaz.
2. Tanım cümlesi (rehber adım 0, kablo tablosu, pin haritası § 2 ve § 9 başı):
   "Bu rehberde ve kablo tablosunda sağ / sol, robota önden bakan kişinin sağı / soludur; robotun kendi sağı / solu değildir."
   Örnekler (kayıttan): acil stop mantarı robota önden bakınca sağ arka köşede; "SOL" yazılan aynalı kol önden bakınca solda
   (robotun kendi sağ kolu).
3. Rehber web uygulaması: küçük görünüm balonu artık "Bu adımın parçaları (sağ / sol robota önden bakana göre)" diyor; eski
   "robotun sağ-ön tarafı" ifadesi kalktı. Kare başlığındaki "bakış: sağ-önden" aynı tanımı kullanır (kamera +X yanında).
   Veri dosyasının `koordinat` açıklaması: "+X robota önden bakanın sağı (robotun kendi solu)".
4. K1 kontrol listesine sağ / sol kurulum testi girdi (§ 5); test F5'te, devreye alındıktan ve motor / enkoder yön testinden sonra
   yapılır.
5. Yazılımın eşlemesi düzeltilir (Efe; § 3). Kablo değişmez.

## 3. Yazılımda değişmesi gerekenler

Tablo: donanım adı (kablo tablosu / pin haritası) → pin ya da kanal → CAD tarafı → robotun kendi tarafı. Bugün yazılım soldaki adı
robotun kendi tarafı sanıyor; doğrusu son sütun.

| Donanım adı | Pin / kanal (pin haritası) | CAD | Robotun kendi tarafı |
|---|---|---|---|
| Sol motor ileri / geri (sol BTS7960B IN1 / IN2, B01) | GPIO25 / GPIO26 | −X | **sağ** |
| Sağ motor ileri / geri (sağ BTS7960B IN1 / IN2, B02) | GPIO27 / GPIO14 | +X | **sol** |
| Sol BTS akım (IS) | GPIO32 | −X | sağ |
| Sağ BTS akım (IS) | GPIO33 | +X | sol |
| Sol enkoder A / B (sol arka motor, N01) | GPIO18 / GPIO17 | −X | sağ |
| Sağ enkoder A / B (sağ arka motor, N02) | GPIO16 / GPIO15 | +X | sol |
| Sonar sağ echo / trig (Q01) | GPIO39 / PCA9685 kanal 10 | +X | sol |
| Sonar orta echo / trig (Q02) | GPIO34 / PCA9685 kanal 11 | orta | orta |
| Sonar sol echo / trig (Q03) | GPIO35 / PCA9685 kanal 12 | −X | sağ |
| `sag_omuz`, `sag_omuz_yan`, `sag_dirsek`, `sag_bilek` (dağıtım kartı A, P01) | PCA9685 kanal 0–3 | +X kol | **sol kol** |
| `sol_omuz`, `sol_omuz_yan`, `sol_dirsek`, `sol_bilek` (dağıtım kartı B, P02) | PCA9685 kanal 5–8 | −X kol (aynalı, "SOL") | **sağ kol** |
| `kafa_pan` küçük açı | PCA9685 kanal 4 | yüz −X'e | sağa (yazılımın cümlesi doğru) |

En dar düzeltme (öneri; seçim Efe'nin):

- **Sürüş:** `motorlar_hedef`'te `v_sol` robotun kendi solu (= donanımdaki "sağ" motor, GPIO27 / 14) sürülmeli, `v_sag` robotun kendi
  sağı (= donanımdaki "sol" motor, GPIO25 / 26). Pin adlarını (`kod/ortak/pinler.json` / `pinler.h`) takas etmek ya da
  `motorlar_hedef` içinde iki tarafı değiştirmek; enkoderler de aynı biçimde (odometride `sol` = GPIO16 / 15, `sag` = GPIO18 / 17).
  Motor ile kendi enkoderi zaten aynı kanalda (B02 ↔ N02, B01 ↔ N01); takas ikisini birlikte yapılmalı.
- **BTS akım (IS) girişleri:** `guc.*`'taki arıza bayrağı (`is_sol` / `is_sag`, GPIO32 / GPIO33; `kod/esp32/OKU_BENI.md`) da aynı
  biçimde takas edilir: robotun kendi solunun IS'i GPIO33 (donanımdaki "sağ" BTS), kendi sağınınki GPIO32. **Ek (16.11, pano #8
  mesaj #33):** Pi'ye giden arıza satırındaki `is_sol` / `is_sag` adları da girişleriyle birlikte taşınır; takastan sonra `is_sol`
  GPIO33'ün, `is_sag` GPIO32'nin arızasıdır (ad robotun kendi tarafını gösterir). Eşik önerisi (≥ 500 mV, hesap) `pin-haritasi.md` Y7'de.
- **Yön bayrakları takasla birlikte:** `motorlar.cpp`'deki `SOL_MOTOR_TERS` / `SAG_MOTOR_TERS` ve `SOL_ENKODER_TERS` /
  `SAG_ENKODER_TERS` (bugün false / true, false / true; hepsi TAHMİNİ) taraf adına bağlı. Pinler takas edilirse bu bayraklar da
  taraflarıyla birlikte taşınır ya da F5 yön testinde yeniden kalibre edilir; pinler takas edilip bayraklar yerinde bırakılırsa iki
  taraf da ters döner / ters sayar.
- **Sonar:** sonar sürücüsü yazıldığında "sağ" (Q01, GPIO39, kanal 10) robotun kendi solu sayılmalı.
- **Kollar:** `kanallar.yaml`'da `sag_*` kanalları (0–3) robotun kendi sol kolu. Ya adlar değişir (kanal 0–3 → `sol_*`), ya da
  yorumlara "sag_* = CAD +X kolu = robotun kendi sol kolu" yazılır ve jestler buna göre okunur.
- `*_TERS` bayrakları (OKU_BENI kalibrasyonu) dönüş **yönünü** düzeltir, **tarafı** düzeltmez: bu eşleme onlarla çözülmez.

## 4. Jest / pan çelişkisi

`kod/jestler/isaret.yaml`: "Sağ kol yana açılır … kafa aynı yöne bakar"; `sag` varyantında kafa 70 ("robotun sağına"). Sağ kol =
kanal 0 → dağıtım kartı A → CAD +X kolu = robotun kendi **sol** kolu; kafa 70 = robotun kendi **sağı**. Kol ve kafa ters taraflara
bakar; jest kendi niyetiyle çelişir. `selam` jesti de (sağ kol) robotun kendi sol eliyle yapılır.

Ek olarak CAD yorumları pan yönünü "robotun sağına (+X)" diye yazıyor (§ 6); bu da yanlış: +X'e dönen yüz robotun kendi soluna bakar.
Yazılımın `kafa_pan` cümlesi ("küçük = robotun sağına") fiziksel olarak doğru, ama kalibrasyonu yapan kişi "sağ"ı rehberdeki tanımla
(önden bakanın sağı) okursa `ters` bayrağını yanlış kurar. Kalibrasyon adımında "robotun kendi sağı (robota önden bakınca solunuz)"
yazılmalı.

## 5. Doğrulama testi (K1 kontrol listesinde; F5'te, devreye aldıktan ve yön testinden sonra)

Komutlar `kod/esp32/OKU_BENI.md`'den (origin/main 71cf76d, sürüm 0.5.0): `sur` (v m/s, w rad/s, w sola +; 500 ms komut gelmezse
motorlar durur), `odo_sifirla`, `odo` satırı (`sol`, `sag` toplam tik).

Sıra: bu test **taraf** testidir; F5 "İlk enerji, aşama 2"deki motor / enkoder **yön** testinden (`*_MOTOR_TERS`, `*_ENKODER_TERS`,
OKU_BENI) sonra yapılır. Yön kalibre edilmeden teker ters dönebilir ya da sayaç azalabilir; montajcı yön hatasını taraf hatası sanar.

1. Tekerler yerden kesik (şasi takozda). `sur` v = 0, w = 0,2: robot kendi soluna dönmek ister, yani **robota önden bakınca soldaki
   tekerler ileri, sağdakiler geri** döner. Bugünkü yazılımla ters çıkması beklenir (§ 3).
2. `odo_sifirla`, sonra arka tekerleri tek tek elle çevir: **önden bakınca soldaki arka teker yalnız `sag`, sağdaki yalnız `sol`**
   sayacını değiştirmeli (öbür sayaç sabit kalır). Ölçüt hangi sayacın değiştiğidir; artıp azalması yön sorusudur
   (`*_ENKODER_TERS`), bu testin konusu değil.
3. Ters çıkarsa kablo değiştirilmez; robot sürülmez, § 3 düzeltmesi beklenir.

Kartta denenmedi: devreye alma adımlarının tam sırası ve `sur`'un yalnız w ile (v = 0) davranışı OKU_BENI'de örneklenmemiş (örnekler
v ile). Doğrulanmadı.

## 6. Bekleyen düzeltmeler (bu pakette yapılmadı)

CAD model dosyalarına bu pakette dokunulmadı (paket kuralı). Sonraki, model dosyalarını değiştiren pakette:

- `tasarim/freecad/arayuz.py:7` "+X robotun sagi" → "+X robota önden bakanın sağı (robotun kendi solu)". Kopyaları:
  `taban/taban_parcalar.py:8` ("+X sag"), `taslak-170/taslak_ayar.py:166`, `taslak-170/kutle.json:3`. (Rehber verisinin `koordinat`
  açıklaması `tasarim/freecad/rehber/rehber_veri.py`'de bu pakette düzeltildi; üretimden sonra veriye geçer.)
- Kafa pan yorumları "+açı yüz robotun sağına (+X)": `arayuz.py:593`, `kafa/kafa_parcalar.py:195`, `kafa/kafa7_parcalar.py:570`,
  `kafa/kafa_montaj.py:861` (ve üretilmiş `kafa-analiz.json`), `montaj/eklem_dogrulama.py:299` → "yüz +X'e, robotun kendi soluna".
- **Açık madde:** `arayuz.py:359` göğüs ekranı portları: "arkadan bakınca sol = robotun solu, −X". Üç ifade birbirini tutmuyor: −X
  arkadan bakınca sağda görünür ve robotun kendi sağıdır. Not üretici fotoğrafından geliyorsa portlar aslında +X'te olabilir; CAD onları
  x ≈ −110'a koymuş. Ekranın arkası gerçek üründe ya da fotoğrafta bir kez bakılmalı (Ahmet'e soru açık: "göğüs ekranı portları gerçek
  üründe hangi tarafta"). Ekran kablolarının yönünü etkiler (`elektrik.md` "−X kısa kenardaki port girintisi", rehber K2 "HDMI direğin
  solundan").
- Yazılım tarafı (§ 3, § 4): Efe.

## 7. Emin olunmayanlar

- Göğüs ekranı portlarının gerçek tarafı (§ 6).
- Efe'nin `origin/main` dışında daha yeni bir yazılım dalı olup olmadığı (bakılmadı).
- Basılı PDF girişinde daha önce bir tanım olup olmadığı (kaynakta yok; büyük olasılıkla yok).
- `kafa_pan` servosunun yönü (`ters`) kalibrasyonla belirlenir; § 4'teki kol / kafa çelişkisi açıların tahmini olmasından bağımsız.

## 8. İleride: donanım adlarını robotun kendi çerçevesine çevirme (açık not)

Bütün donanım adlarını robotun kendi çerçevesine çevirmek (CAD "sağ" → "sol") yazılımla tek sözlük sağlar, ama kablolar.json, rehber
metni, kareler, `taban_parcalar.py` SX(), baskı listesindeki "SOL" etiketi ve pin haritasının birlikte değişmesi demek. Bu pakette
seçilmedi; tam taramalı CAD paketi ya da yazılım düzeltmesi sırasında yeniden değerlendirilebilir. Seçilirse bu belgedeki tanım
cümlesi de ters döner.

## 9. Kaynaklar

- Bu pakette yapılan sınama: `planlama/d158/F10m-gunluk.md` § 11.
- Salt okunur araştırma (16.11.2026, ajan raporu; depoda değil): bu belgenin § 1, § 3, § 4 ve § 6'sındaki dosya / satır göndermelerinin
  çoğu oradan; § 1'deki iki sınama, OKU_BENI komutları, `motorlar.cpp`, `kanallar.yaml`, `isaret.yaml` satırları ve CAD yorum satırları
  bu pakette yeniden okundu.
- TÜBİTAK önerisi aynı ayrımı biliyor: `tubitak-2209b/taslak/gorseller/sekiller-notlar.md:52` ("iki sağ farklıdır"),
  `oneri-taslak-v10.md:162`, `:164` (araştırmadan; bu pakette yeniden okunmadı). `tubitak-2209b/` depoda izlenmiyor
  (`.git/info/exclude`): bu dosyalar depodan görünmez, yalnız yerel kopyada.
