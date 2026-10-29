# M6: montaj sırası ve alet erişimi (4. adım analizi)

Düzeltme planı M6 · 15 Ekim 2026 · Opus-7. Bu bir analiz: CAD değiştirilmedi. 8. sıradaki 3B montaj rehberinin girdisi olacak.

- Ölçüm betikleri (FCStd'leri yalnız okur):
  - `planlama/adim4/m6_yukle.py`: modüller, ev pozunda global koordinatta.
  - `M6_erisim.py`: 464 bağlantı elemanı × (montaj adımı + servis), ~14 dk. Çıktı `M6_erisim_sonuc.json`.
  - `M6_ek.py`: etek kapağı, S1 kaseti, göbek. Çıktı `M6_ek_sonuc.json`.
  - `m6_tablo.py`: adım tablosunun ham hâli. Çıktı `m6_tablo.md`.
- Kullanılan CAD (dosya saatleri):

  | Modül | FCStd saati | Not |
  |---|---|---|
  | iskelet | 14 Ekim 22:41 | |
  | taban | 15 Ekim 08:58 | |
  | kafa | 15 Ekim 08:57 | |
  | kabuk | 15 Ekim 09:21 | S1 kaset gövdesi/kapağı ve 2 dikme cıvatası var |
  | omuz | 15 Ekim 09:27 | S1 tamburu var |
  | dirsek | 15 Ekim 09:32 | |

- **S1 varsayımı:** analiz bu dosyalarla yapıldı. S1 ~14:00'te bitti ve kontrolü sürüyor. Kaset geometrisi ya da bağlantısı
  değişirse G4 ve 3. bölümdeki Ø84 maddesi `M6_erisim.py` ve `M6_ek.py` ile yeniden koşulmalı. Ped yarığı ve kaset için
  `planlama/adim2/S1-kaset.md` esas alındı:
  - 2 dikme (ψ 200° / 226°) M3×8 → kabuk pedinde ısıl gömme somun,
  - üst uçta yalnız pim; kabuğa vidalı kulak yok,
  - kablo çıkışı ψ 214°'de pedde 12 × 6 yarık.
- **Y1b (25 Ekim 2026):** kaset değişti (flanş pahı, U cebi +2 mm, duvar bağı ip delikleri, duvar dışı ikinci pim kulağı ψ 300;
  tamburda kayış yarıkları yerine bağlama ipi yolu). Dikme cıvataları ve ped yarığı **aynı yerde**; G4 sırası önden radyal olarak
  düzeltildi. `M6_erisim.py` / `M6_ek.py` yeniden koşulmadı (Y3 M6 CAD adımında koşulacak).

## 1. Özet

| | Sonuç |
|---|---|
| Rehber adımı | **48** (tezgâh alt montajları ayrı adım; 2 kablolama kapısı kabuktan önce) |
| Bağlantı elemanı (alet gerektiren) | 464 (sağ + sol) |
| Doğru sırayla erişilebilen | 445 (kaset dikmeleri S1 −45°'de dahil) |
| Sırayla bile erişilemeyen | **19** (göbek–horn 4, S2 somunu 4, dirsek servosu 4 cıvata + 6 somun, tilt somunu 1), hepsi CAD değişikliği ister; ayrıca 10 tanesi geometride erişilir ama el kabuğun içinde kalır (K1 4, K2 6) |
| Tam kapalı robotta (servis) doğrudan erişilen | 289 (düz 165 + L 124); 117 erişilemez, gerisi sınırda |

**Sıra yanlışsa erişilemeyen, doğru sırayla çözülenler** (rehbere kural olarak girer):
- **Etek braketleri:** M6 × 6 uzun raya, güç paneli ile elektronik katından **önce** takılır. Sonra M6 başının üstünde yalnız
  30 mm kalır (5 mm alyan + kısa kol 33 mm).
- **Tahrik:** braket → plaka (M4), sonra motor → braket (M3×6), sonra teker. Teker takılıysa motor cıvatasına 11,5 mm kalır;
  motor takılıysa braket M4'üne 3,2 mm kalır.
- **Pan grubu (kafa):**
  - pan horn vidası → boyun mili (mil–horn 4 × M3×8) → eğme çatalı (çatal–mil 4 × M3×8) → tilt servosu.
  - Tilt servosu önce takılırsa mil–horn ve çatal–mil cıvatalarına 18–64 mm kalır, L kolu dönemez.
- **Kafa:**
  - Kafa iskeleti tilt hornuna (yanak–horn 4 × M3×8) kabuklardan **önce** bağlanır. Kabuklar takılınca cıvatalar kafanın
    içinde kalır.
  - Pi, LCD ve kamera tezgâhta takılır.
- **Göbek:**
  - Göbek–horn cıvataları S2 servosu göbeğe takılmadan önce sıkılır. Servo takılınca başa 13 mm kalır.
  - S1 tamburu göbeğe tezgâhta bağlanır (3 × M3×8, −x yüzden). Omuz bandı takılıysa bu cıvatalara yalnız 12,5 mm kalır.
- **Dirsek tezgâhı:** sıra şöyle (her biri bir sonrakini kapatır): servolar → dirsek hornu → çatal → bilek hornu → flanş → el.
  - Flanş takılıysa bilek horn vidasına 0,3 mm kalır.
  - El takılıysa flanş–horn cıvatalarına 1,0 mm kalır.
  - Pim M5 tezgâhta takılır: robotta göğüs bandı 8,9 mm'de.
- **S1 kaseti:** dikme cıvataları S1 **−45°** (kol arkada) ya da **+90°**'de takılır. Serbest boy 110 mm. S1 0°'da üst kol tüpü
  7,5 mm'de engelliyor, +45°'de kol çatalı 0,2 mm'de engelliyor.
  - **Düzeltme (Y1b, 25 Ekim 2026; `planlama/adim2/K2-s1-kontrol.md` B5/K5):** kaset +x yönünden takılamaz (gövde t 10,5'te, kapak
    t 4,0'te göbeğe / tüpe çarpar). Doğru sıra **önden radyal** (G4 satırı ve `planlama/adim2/S1-kaset.md` "Montaj sırası (K5)").
    Anahtar erişimi S1 −45° / S2 90°'de iki dikme cıvatasına ≥ 8 mm.

**Sırayla da çözülmeyenler → CAD değişiklik listesi (4. bölüm):**

| Sorun | CAD | Öncelik |
|---|---|---|
| Göbek–horn M3×12'nin 2'si (z +6) göbeğin kendi duvarında kapalı (x 169…199, serbest 7 mm). Hiç takılamaz | C1 | yüksek |
| Dirsek servosu kulak M4×16'nın 2'si ön kol duvarına 13,6 mm; 3 kontra somun tutulamıyor (kol başına) | C2 | yüksek |
| S2 servosu kontra somunlarının 2'si (kol başına) ve tilt servosunun 1'i anahtarla tutulamıyor | C3 | orta |
| Gövde braketi M5 × 4: başı kabuğun içinde. Alet yolu var (L, 80 / 106 mm), ama el kabuk içinde olmalı | K1 | yüksek |
| Etek braketi M3 × 6: başı eteğin içinde (L 74 mm). Yalnız alttan, robot yatırılınca | K2 | orta |
| Omuz bandı Ø84 halka: kol takılıyken çıkmaz (geometri doğruladı) | K3 + K4 | orta |
| Etekte sigorta ve servis kapağı yok | K5 (K6) | yüksek |
| Ana anahtar düğmesi için etek deliği yok | K7 | yüksek |

## 2. Montaj sırası (rehber tablosu)

Sütunlar:
- **Erişim:** `M6_erisim.py` sınıfı, o adımda takılı tüm parçalar engel sayılarak.
  - `düz`: tornavida tipi uzun alyan/bits, uzun kol + 20 mm serbest.
  - `L`: L alyan; kısa kol sığar, uzun kol ≥ 45° döner.
  - `açık ağız`: somun yandan anahtarla tutulur.
  - `lokma`: somun eksenden lokmayla tutulur.
  - `cep`: somun altıgen cepte durur, anahtar gerekmez.
  - Sayılar sağ + sol toplamıdır.
- **Tezgâh:** alt montaj masada yapılır; engel yalnız o alt montajın parçalarıdır.
- **Çekiç somun ve ısıl gömme:** alet istemez. Isıl gömme somunlar baskıdan hemen sonra havyayla takılır (M7 kuponuna göre).

| No | Kod | Parça / iş | Bağlantı elemanı | Alet | Erişim, not |
|---|---|---|---|---|---|
| 1 | A1 | Şase çerçevesi: 2 uzun + 3 ara ray, 8 iç köşe bağlantı | 16 × M6×10 DIN 913 set vida | alyan 3 | düz |
| 2 | A2 | Gövde direği + 2 direk–ray köşe bağlantısı | 4 × M6×16 DIN 912 + pul + çekiç somun | alyan 5 | düz |
| 3 | A3 | Omuz traversi + 2 direk–travers köşe bağlantısı | 4 × M6×16 + pul + çekiç somun | alyan 5 | düz |
| 4 | B1a | Tezgâh: alt plakaya 20 naylon burç (alttan), akü ön takozu | 20 × M3×6; 2 × M3×8 → ısıl gömme | alyan 2,5 | düz |
| 5 | B1 | Alt plaka → şase (robot yan yatık ya da sehpada) | 14 × M6×14 + çekiç somun, alttan | alyan 5 | düz |
| 6 | B2a | 4 motor braketi → alt plaka | 8 × M4×16 + pul + çekiç somun M4 | alyan 3 | düz; **motordan önce** |
| 7 | B2b | 4 motor → braket | 16 × M3×6 | alyan 2,5 | düz; **tekerden önce** |
| 8 | B2 | 4 kaplin + 4 teker | 4 × M4×16 eksenel vida | alyan 3 | düz |
| 9 | B3 | 2 × BTS7960, 3 × XL4016 → burçlar; akü + 2 kayış | 20 × M3×6 (üstten) | alyan 2,5 | düz |
| 10 | B4 | 8 kat burcu M5×40 | 8 × M5×16 DIN 913 saplama + çekiç somun M5 | alyan 2,5 | düz |
| 11 | C0 | 6 etek braketi → uzun ray üst kanalı | 6 × M6×14 + pul + çekiç somun | alyan 5 | düz; **güç paneli ve elektronik katından önce** (sonra 30 mm kalır) |
| 12 | B5a | Tezgâh: güç paneline sigorta kutusu, röle, ana sigorta yuvası, ana anahtar | 3 × M4×16 + naylon somun | alyan 3 + 7 mm anahtar | düz / lokma |
| 13 | B5 | Güç paneli → burçlar | 4 × M5×12 + pul | alyan 4 | düz |
| 14 | B6a | Tezgâh: elektronik katı: burçlar alttan, kartlar üstten (arayüz, 2 dağıtım, PCA9685, BNO055, ESP32) | 16 × M3×8 + 8 × M2,5×8 (alt), 16 × M3×6 + 8 × M2,5×5 (üst) | alyan 2,5 / 2 | düz |
| 15 | B6 | Elektronik katı → burçlar | 4 × M5×12 + pul | alyan 4 | düz |
| 16 | B7 | 3 sonar tutucu + sonar → ön ara ray | 4 × M6×14 ISO 7380 + çekiç somun | alyan 4 | düz |
| 17 | K1 | **Kablolama kapısı 1 (taban):** akü → XT60 → ana sigorta → röle → sigorta kutusu → sürücüler / XL4016 → kartlar; motor ve enkoder; sonar; acil stop hattı (kontak gövdesi etek adımında takılır, uç bırakılır) | kablo bağı | — | ölçüm, yön testi; kabuk takılmadan |
| 18 | C1 | 4 gövde braketi → direk ±X kanalı (y 400 / 780) | 8 × M6×14 + çekiç somun | alyan 5 | L (80 mm, kendi braketi) |
| 19 | D1a | Tezgâh: omuz yuvası + S1 servosu (×2) | 8 × M4×16 + 8 × M4 kontra somun | alyan 3 + 7 mm açık ağız | düz / açık ağız (3 yön) |
| 20 | D1b | Tezgâh: 6808-2RS + rulman kapağı (×2) | 8 × M3×12 → yuvada ısıl gömme | alyan 2,5 | düz |
| 21 | D1c | Tezgâh: S1 servosu ortaya; S1 hornu + merkez vidası (×2) | 2 × M3×5 horn vidası | PH1 | düz |
| 22 | D1 | Omuz gövdesi → travers ucu (kaydırarak) ×2 | 8 × M6×16 + çekiç somun | alyan 5 | düz 6, L 2 (alttaki 141 mm). Servis: üst cıvata kabuk üst kapağındaki Ø14 delikten, L 85 mm |
| 23 | E1a | Tezgâh: boyun (servo yuvası + pan servosu, rulman yuvası + 2 × 6808, boyun plakası) | 4 × M3×8 + pul → ısıl gömme; 4 × M3×10 | alyan 2,5 | düz |
| 24 | E1 | Boyun → travers üst kanalı | 2 × M6×20 + pul + çekiç somun | alyan 5 | düz |
| 25 | E2a | Pan servosu ortaya; pan hornu + merkez vidası | 1 × M3×5 horn vidası | PH1 | düz; **boyun milinden önce** |
| 26 | E2b | Boyun mili + 6808 iç bilezikleri | 4 × M3×8 mil–horn | alyan 2,5 | düz; **eğme çatalından önce** |
| 27 | E2c | Eğme çatalı | 4 × M3×8 çatal–mil → ısıl gömme | alyan 2,5 | düz; **tilt servosundan önce** |
| 28 | E2 | Tilt servosu + 625ZZ + M5 pim | 4 × M4×16 + 4 × kontra somun; 1 × M5×12 + pul | alyan 3 / 4 + 7 mm | düz; 1 kontra somun tutulamıyor → **C3** |
| 29 | E3a | Tezgâh: kafa içi: kafa iskeleti, Pi 5 (burç), LCD, kamera, 5 V çevirici, amfi (köpük bant), tilt hornu | 4 × M2,5×8 burç + 4 × M2,5×5; 4 × M3×6 ISO 7380 (LCD); 4 × M2×8 PT (kamera); 1 × M3×5 horn vidası | alyan 2, PH0, PH1 | düz |
| 30 | E3 | Kafa → tilt hornu (yanak) | 4 × M3×8 yanak–horn | alyan 2,5 | L; **kabuklardan önce** (sonra kafa içinde kalır) |
| 31 | E4 | Kafa kabukları (ön + arka) + vizör | 4 × M3×8 ISO 7380 | alyan 2 | düz |
| 32 | K2 | **Kablolama kapısı 2 (gövde içi, KABUKTAN ÖNCE):**<br>• servo uzatmaları (dağıtım A/B → direk boyunca → travers arkası → omuz),<br>• kafa 12 V + sinyal (direk → boyun),<br>• Nextion kablosu (göğüs hizasında uç bırakılır),<br>• sinyal hatları;<br>kablo bağları direğe | kablo bağı | — | S1 kablosu G4'te kasetten içeri girer: uç travers arkasında bırakılır |
| 33 | F1 | Taban eteği 6 bant (orta → ön → arka) + acil stop (panel somunu) + ana anahtar düğmesi | 17 × M3×6 ISO 7380 bindirme (dışarıdan); 6 × M3×8 etek braketi (içeriden) | alyan 2 / 2,5 | bindirme düz; braket L 74 mm, el alttan, robot yatık → **K2**; düğme deliği yok → **K7** |
| 34 | F2 | Gövde alt + orta bantları (sağ, sol) | 12 × M3×6 ISO 7380; 2 × M5×10 + pul (braket y 400, içeriden) | alyan 2 / 4 | bindirme düz; M5 L 80 mm ama el kabuk içinde (üstten ~400 mm derin) → **K1** |
| 35 | F3 | Göğüs bantları + Nextion | 9 × M3×6 ISO 7380; 4 × M3×6 DIN 912 ekran (içeriden); 2 × M5×10 (braket y 780) | alyan 2 / 2,5 / 4 | ekran ve braket üst açıklıktan (omuz bandı yok); M5 L 106 mm → **K1** |
| 36 | F4 | Omuz bantları: Ø84 rulman kapağının üstünden geçer, üst kapak boynu sarar | 6 × M3×6 ISO 7380 | alyan 2 | düz. **Bu adımdan sonra omuz bandı ancak göbek sökülünce çıkar** (3. bölüm) |
| 37 | G0 | Tezgâh: göbek + S1 kablo tamburu (×2); tamburun 2 bağlama ipi yoluna Ø0,4 mumlu ip önceden geçirilir (halka altı oluk → iki dudak cebi, uçlar ~80 mm yukarıda serbest) | 6 × M3×8 (−x yüzden) → göbekte ısıl gömme | alyan 2,5 | düz |
| 38 | G1 | Göbek → S1 hornu (6808 iç bileziğine) | 8 × M3×12 göbek–horn | alyan 2,5 | düz 4; **YOK 4** (göbek duvarı) → **C1**; S2 servosundan önce |
| 39 | G2 | S2 servosu → göbek; mafsal 625ZZ + M5 pim; **S2 servo kablosu G2'den ~20 mm önce, göbeğin arka iç şeridinde uzatmaya eklenir** (lehim + ısıyla daralan makaron ya da JR çifti, kablo bağı; Y1b B10) | 8 × M4×16 + 8 × kontra somun; 2 × M5×12 + pul | alyan 3 / 4 + 7 mm | cıvata düz; somun 4'ü açık ağız, **4'ü YOK** → **C3** |
| 40 | G3 | S2 hornu + merkez vidası, kol çatalı (çatal–horn), üst kol tüpü; kablo G2 → tambur bağı (ψ 145): 3 aynı PVC şerit kanala, teğet (bağ açısı 0 ± 2°), **2 bağlama ipi** demetin üstünde düğümlenir (cerrah + kare düğüm, uç 3 mm) | 2 × M3×5 horn; 8 × M3×8 çatal–horn; 4 × M3×8 tüp → ısıl gömme | PH1, alyan 2,5 | düz |
| 41 | G4 | **S1 kablo kaseti, önden radyal (Y1b K5):** (a) **gövde** önden radyal, x ofsetsiz (arka plaka omuz pedine yaslı kayar; S1 −45 / −20 / 0 × S2 90 ya da S1 −45 × S2 5) → (b) U elle kanala, dış koşu duvar boyunca, ψ 214'te yarıktan içeri; **lop boyu L 171,4 mm (−5…0)** tambur bağından duvar bağına (kabloda işaret) → (c) **duvar bağı:** 2 bağlama ipi (ψ 226,5 / 230) duvar deliklerinden, düğüm duvarın dışında → (d) **kapak** önden radyal, flanş gövdeden **x +3,3…5 mm havada** (S1 0…135°, S2 ≥ 30°; S1 −45°'de en çok +3,3) → (e) kapak **−x itilir**: 2 × Ø3 pim (uç ψ 331 + kulak ψ 300) yuvasına → (f) 2 dikme cıvatası | 4 × M3×8 dikme → pedde ısıl gömme; 4 × Ø0,4 ip (tambur 2 + duvar 2) / kol | alyan 2,5 | cıvatalar **S1 −45° / S2 90°**'de ≥ 8 mm açık; +x'ten kaydırma **olmaz** (gövde/kapak göbeğe ve tüpe çarpar) |
| 42 | H0a | Tezgâh: ön kol + dirsek ve bilek servoları | 16 × M4×16 + 16 × kontra somun | alyan 3 + 7 mm | bilek: cıvata düz, somun cepte. Dirsek: **2 cıvata/kol YOK** (13,6 mm), **3 somun/kol YOK** → **C2** |
| 43 | H0b | Tezgâh: dirsek hornu + merkez vidası | 2 × M3×5 horn | PH1 | düz; **çataldan önce** |
| 44 | H0c | Tezgâh: dirsek çatalı → horn; 625ZZ; M5 pim (yanaktaki ısıl gömmeye) | 8 × M3×8 çatal–horn; 2 × M5×12 + pul | alyan 2,5 / 4 | düz; pim robotta erişilemez (göğüs bandı 8,9 mm) |
| 45 | H0d | Tezgâh: bilek hornu + merkez vidası | 2 × M3×5 horn | PH1 | düz; **flanştan önce** |
| 46 | H0e | Tezgâh: bilek flanşı | 8 × M3×8 flanş–horn | alyan 2,5 | düz; **elden önce** |
| 47 | H0f | Tezgâh: el | 4 × M3×6 ISO 7380 yaka → ısıl gömme | alyan 2 | düz |
| 48 | H1 | Dirsek modülü → üst kol tüpü (pim + bilezik); kablolar tüp içinden G2'ye | 4 × M3×20 + 8 pul + 4 × M3 kontra somun | alyan 2,5 + 5,5 mm lokma | düz / lokma. Sıkma: kulaklar değmeden (M7 kupon D) |
| — | F5 | Son: arka servis kapağı (+ önerilen etek kapağı K5) | 7 × M3×6 ISO 7380 | alyan 2 | düz; devreye alma testinden sonra kapatılır |

Rehber için sıra kuralları:
1. Taban (4–17) iskelet bitince yapılır. Plaka cıvataları alttan takıldığı için robot sehpada ya da yan yatık olmalı.
2. Elektrik testi (K1) kabuktan önce yapılır.
3. Kafa (23–31) kabuktan önce takılır: omuz bandının üst kapağı boynu sarar ve boyun cıvataları ile omuz yuvasının üst cıvatası
   bu kapağın altında kalır.
4. Kollar (37–48) kabuk bittikten sonra takılır.

## 3. Ø84 omuz halkası, S1 kaseti ve servis

**Geometri (ölçüldü):**
- Omuz bandının düz yan duvarı x 147…152'de. Ø84 deliğin içinden şunlar geçer:
  - rulman kapağı (x 146…160, kulak cıvataları r ≈ 33,5),
  - 6808,
  - göbeğin mili.
- Deliğin dışında (x ≥ 152) şunlar var:
  - tambur (r 43,7 > 42),
  - göbek (y 998'e kadar),
  - kaset (r 77, kabuk pedine vidalı),
  - kol.
- Bant ancak +x yönünde çıkabilir (sağ yarım; sol için −x). Bu yöndeki her parça Ø84'ten büyük olduğu için kol takılıyken bant
  çıkmaz.
- Aşağı/yukarı kaydırma da olmaz:
  - üst kapak omuz yuvasının 2 mm üstünde,
  - yuvanın M6 başı Ø14 delikten kapağa giriyor,
  - kafa üstte.
- Ped yarığı (ψ 214°, r ≈ 46…58, 12 × 6) ile Ø84 delik arasında ~3 mm et kalıyor (`M6_ek_sonuc.json → ped_psi_r_dolu`).

**Bandı sökmek için gereken sıra (servis yolu, şu anki CAD ile):**
1. Dirsek: 2 bilezik cıvatası.
2. Kaset: 2 dikme cıvatası, S1 −45° / S2 90°'de; kapak +x 3,5 mm kaldırılıp (pimlerden çıkar) önden radyal çekilir; duvar bağı ipleri kesilir; gövde önden radyal çekilir.
3. Kol çatalı: S2 horn vidası + 4 çatal–horn cıvatası + M5 mafsal pimi.
4. S2 servosu: 4 × M4 + kontra somun.
5. Göbek–horn: 4 × M3×12 (C1 yapılmadan 2'si hiç sökülemez).
6. Göbek + tambur.
7. Kablolar: kaset yarığından dişi JR'lerle geri çekilir (yarık 12 × 6 → JR erkek 10,3 × 4 geçer).
8. Omuz bandının 6 + bindirme cıvatası.

Toplam kol başına ~25 cıvata.

**Seçenekler:**

| Seçenek | Ne | Bedel | Değerlendirme |
|---|---|---|---|
| A. Kesin sıra (CAD yok) | F4 göbekten önce; servis yukarıdaki yolla | bant sökümü kol başına ~25 cıvata | montaj için yeterli, servis için ağır |
| B. Bandı Ø84'ten kenara yarmak | delikten bant kenarına yarık | tambur r 43,7 ve kaset (pede vidalı) yüzünden bant yine +x'e çıkamaz; yarık göbek/kaset çapı kadar olmalı → yan duvar "C" olur, kaset tutunacak ped kaybolur | **önerilmez** |
| C. Ped yarığını Ø84 ile birleştirmek ("anahtar deliği", K3) | ψ 214°'deki 3 mm eti kaldır: yarık r 42…58 açık | yan duvar halkası ψ 214'te açılır; ped hâlâ dikmeleri (ψ 200 / 226) taşır, yarıktan uzaklık ~6 mm | S1 kablo demeti konnektörsüz yana alınır: kol/göbek sökümünde kabloyu çekmek gerekmez; montajda kablo yarığa yatırılır |
| D. Üst arka servis kapağı (K4) | göğüs bandının arka duvarında, `ARKA_KAPAK` gibi ikinci kapak | 1 parça + 6 bindirme | omuz bandını sökme ihtiyacını büyük ölçüde kaldırır: braket y 780, Nextion arkası, travers arkasındaki S1 kablo ucu, kafa kablo birleşimleri |

**Öneri:** A + C + D.
- Bant yalnız kabuk değişiminde sökülür.
- Gündelik servis (kablo, Nextion, kafa beslemesi, braket) üst arka kapaktan yapılır.
- S1 kablosu anahtar deliği sayesinde konnektör sökmeden kasetten çıkar.
- B önerilmez: yarık, kasetin bağlandığı pedi böler ve tamburun çapı yüzünden yine yetmez.

## 4. CAD değişiklik listesi

> **Y3 (29 Ekim 2026, 1,65 m):** C1–C3 ve K1–K7 CAD'e işlendi (seçilen çözümler, ölçüler ve doğrulama `planlama/y3/Y3-gunluk.md`,
> sabitler `tasarim/freecad/arayuz.py` `M6`). Aşağıdaki tablo 125 cm ölçümüdür; sıra tablosu ve `M6_erisim.py` 1,65 m'de Y4'te yeniden koşulur.

Sahip, dosya sahibidir. Bu ajan hiçbirini uygulamadı.

| No | Modül / dosya | Değişiklik | Sabit (öneri) | Öncelik | Doğrulama |
|---|---|---|---|---|---|
| C1 | omuz / `omuz_parcalar.py` (göbek) | Göbek–horn cıvatalarından ikisi (y 949 / 961, z +6, baş x 162, +x) göbek duvarında kapalı (x 169…199). İki çözüm: (a) eksenlerinde Ø6 erişim deliği (S2 servo cebinden geçer; S2 servosu G1'de takılı değil); (b) dört cıvatayı da erişilen iki konuma (z −6) göre yeniden diz. Kontrol: `omuz_montaj`'a "horn cıvatası alet yolu ≥ 20 mm (S2 servosuz)" | — | **yüksek** (2 cıvata takılamaz) | `M6_erisim.py` G1 → düz 8 |
| C2 | dirsek / `dirsek_parcalar.py` (ön kol) | Dirsek servosu kulak cıvatalarından 2'si (baş x 210, +x) ön kol duvarına 13,6 mm; 3 kontra somun tutulamıyor. İki çözüm: (a) ön kol dış duvarında cıvata eksenlerinde Ø8 erişim deliği + kontra somun yerine altıgen somun cebi (bilek servosundaki gibi, orada `cep`); (b) cıvatayı ters tak, başı servo tarafında, somun ön kolda altıgen cepte | — | **yüksek** | H0a → YOK 0 |
| C3 | omuz (göbek: S2), kafa (eğme çatalı: tilt) | Anahtarla tutulamayan DIN 985 somunlar: S2'de kol başına 2, tilt'te 1. Altıgen somun cebi ya da M4 ısıl gömme somun (kontra somun kalkar) | `INSERT[4]` gerekirse (şu an yok) | orta | G2 / E2 → somun cep |
| K1 | kabuk + `arayuz.KABUK_GOVDE_BRAKET` | Gövde braketi M5'i ters çevir: dışarıdan M5×16 ISO 7380 → kabuk boss'u (Ø5,5 geçiş + dış yüzde Ø10,5 oturma) → braket ayağında M5 perçin somun (3 mm Al'de Ø7 delik). Isıl gömme M5 × 4 kalkar. Böylece M5 hem montajda hem serviste dışarıdan, düz erişilir; bant sökümü braket dahil dışarıdan olur | `civata_m5=(5, 16)`, `m5_tip="ISO 7380"`, `m5_somun="perçin somun"`; `kabuk_montaj` kavrama kontrolü güncellenir | **yüksek** | F2/F3 → düz |
| K2 | kabuk + `arayuz.KABUK_ETEK_BRAKET` | Etek braketi M3'ü ters çevir: dışarıdan M3×8 ISO 7380 → 2 mm Al braket ayağında M3 diş (ya da M3 perçin somun); etekteki ısıl gömme M3 × 6 kalkar | `civata_m3`, `m3_tip` | orta | F1 → düz |
| K3 | kabuk / `kabuk_parcalar.py` (S1 ped yarığı) | Ped yarığını (ψ 214°, r ~46…58) Ø84'e kadar aç (r 42…58): ~3 mm et kalkar. Dikmelere (ψ 200 / 226, r 53–54, Ø8) uzaklık ~6 mm | `KOL_KABLO["s1"]["cikis"]["yarik"]` iç ucu r_delik | orta | S1 kontrolü (kablo yolu, baskı) |
| K4 | kabuk + `arayuz` | Üst arka servis kapağı, `ARKA_KAPAK` ile aynı yapı (bindirmeli, söküleblir). Öneri: x ±75, y 700…870 (göğüs bandı arka duvarı), r 15. **Yer kontrolü yapılmadı:** iç tarafta direk (z ±20) ve braket y 780 (z ±15) var, arka duvar z ≈ −80…−88 | `ARKA_KAPAK_UST = dict(x=75, y0=700, y1=870, z0=-200, z1=-40, r=15)` | orta | kabuk_montaj + carpisma |
| K5 | kabuk (etek arka sağ + sol) + `arayuz` | **Sigorta + servis kapağı H1:** ayrıntı aşağıda | `ETEK_SERVIS_KAPAGI = dict(x=(-44, 36), z=(-230, -175), pay=6, t=3, civata=(3, 6))` | **yüksek** | `M6_ek.py` H1 (ölçüldü) |
| K6 | kabuk ya da taban | Ana sigorta yuvası (30 A, x 97…127, z −160…−100) H1'in dışında. Öneri (taban, 5. adım E8/E9): yuvayı H1 altına taşı (sigorta kutusunun yanına). Olmazsa kabukta küçük kapak H2: delik x 94…130, z −160…−100; kapak +5 mm; en yakın etek orta bandı 7,5 mm, acil stop mantarı 14,4 mm, çakışma yok | `ETEK_SIGORTA_KAPAGI` (yalnız H2 seçilirse) | orta | `M6_ek.py` H2 |
| K7 | kabuk (etek arka sol) | Ana anahtar düğmesi (taban: ASW-A01, x −79,4, z −200, düğme zarfı Ø40, y 262…284) için etek üst plakasında delik **yok**. Taban parçasının notu "kabuk deliği gerekir" | `ANA_ANAHTAR = dict(x=-79.4, z=-200.0, delik_d=?)`: çap ASW-A01 çiziminden (bilinmiyor) | **yüksek** (montajda zorunlu) | kabuk_montaj |
| S | rehber (CAD yok) | 2. bölümdeki sıra kuralları; kaset için S1 −45° | — | — | — |

**K5 ayrıntısı (H1, etek arkası sigorta + servis kapağı):**
- Yer ve ölçü:
  - Etek üst plakasında (y 259…262), gövdenin arkasında.
  - Delik **80 × 55 mm**: x −44…36, z −230…−175, köşe r 8.
  - Kapak **92 × 67 × 3 mm** PETG.
  - Bağlantı: 4 × M3×6 ISO 7380 → plakanın altında 4 boss + M3 ısıl gömme (bindirme kuralıyla).
- Ölçülen boşluklar (`M6_ek.py`):
  - Kapak ana anahtar gövdesine 7,4 mm, acil stop mantarına 15 mm.
  - Delik plakanın tamamen içinde (kesilen 13.200 / 13.200 mm³).
  - Altında 6 yollu sigorta kutusu var (üstü y 214,5, plakaya 45 mm: parmak/sigorta pensesi için yeterli).
- Dikkat:
  - Delik etek arka sağ/sol dikişini (x = 0) keser. Kapak dikişi örter; dört boss iki yarıya ikişer dağılır.
  - Sigorta kutusu "tahmini zarf" (105 mm), delik 80 mm. Kutunun iki ucundaki sigortalar kısmen örtülebilir. Gerçek kutu
    seçilince kutu delik altına ortalanmalı (taban), ya da delik x −46…46'ya genişletilmeli (kapak acil stop mantarına 1,4 mm
    kalır: sınırda).
- Servis kapağı olarak bu delikten şunlara erişilir: sigortalar, röle soketinin üstü, acil stop kontak bağlantısı (kablo yolu 10).
  Akünün kendisine erişim yok: akü güç panelinin altında.

## 5. Alet tablosu

Kaynak: `M6_erisim.py` (ISO 2936 yaklaşık kol boyları, tahmini).

| Alet | Ölçü | Kullanıldığı | En zor yer (serbest boy) |
|---|---|---|---|
| L alyan, küresel uçlu, uzun seri | 2 mm (kısa kol 16, uzun 80) | ISO 7380 M3 (kabuk bindirme, el, kafa kabuğu, LCD); M2,5 DIN 912 | — (düz) |
| L alyan, küresel uçlu | 2,5 mm (18 / 90) | M3 DIN 912 (hepsi), M5 DIN 913 saplama | etek braketi M3 (içeriden, 74 mm); kaset dikmesi (S1 −45°) |
| L alyan | 3 mm (20 / 100) | M4 DIN 912 (servo kulakları, motor braketi, teker), M6 DIN 913 set vida | dirsek servosu kulak (13,6 mm → C2) |
| L alyan | 4 mm (25 / 110) | M5 DIN 912 (kat, mafsal, pim, gövde braketi), M6 ISO 7380 (sonar) | gövde braketi M5 (içeriden 80 / 106 mm → K1) |
| L alyan, **uzun küresel uçlu ≥ 150 mm** | 5 mm (28 / 125) | M6 DIN 912 (iskelet, plaka, braketler, omuz yuvası, boyun) | omuz yuvası üst M6, serviste kabuk Ø14 deliğinden (L 85 mm); gövde braketi M6 (L 80 mm) |
| Yıldız tornavida | PH1, ≥ 60 mm sap | servo horn merkez vidaları (5) | flanş takılıysa bilek hornu (sıra) |
| Yıldız tornavida | PH0 | kamera M2×8 PT | — |
| Açık ağız / yıldız anahtar | 5,5 mm | M3 kontra somun (bilezik) | lokma da olur (24 mm) |
| Açık ağız anahtar, ince | 7 mm | M4 kontra/naylon somun (servo kulakları, güç paneli) | S1: 3 yön; S2 ve dirsek: bazıları hiç (C2, C3) |
| Lokma | 5,5 / 7 mm | bilezik ve güç paneli somunları | — |
| Havya + ısıl gömme ucu | M3 / M5 | tüm ısıl gömme somunlar (baskıdan sonra, tezgâhta) | yatay delikler: M7 kupon C |
| Tork tornavida (öneri) | 0,5–1,5 N·m | plastiğe giden M3 / M5 (kupon C değerleri) | — |
| Kablo bağı, sıcak tutkal | — | K1, K2, G3, G4 | — |
| Ø0,4 mumlu polyester bağlama ipi + makas | ~0,5 m / kol | G0, G3, G4 (S1 tambur ve duvar bağı; Y1b K2/K4) | — |

## 6. Açık sorunlar ve sınırlar

1. **Ölçüm modeli:**
   - Alet düz silindir: r = 0,58 s + 0,6 mm.
   - L kolu salınımı: 15°'lik 24 yön, 70 mm kol.
   - Küresel uç: 25° eğik, 12 yön.
   - **El hacmi modellenmedi.** Kabuk içi cıvatalar (K1, K2, Nextion ekranı) geometride "L" çıkıyor ama el kapalı hacimde
     olmalı. Bu yargı elle yapıldı.
2. **Somun ölçütü:**
   - Derin lokma ve 2 mm kalınlığında, 18 mm genişliğinde açık ağız varsayıldı.
   - Bağlantı elemanları (pul, komşu cıvata başı) açık ağız için engel sayılmadı, yani iyimser.
   - `CEP` sınıfı: somun 30° dönünce çevredeki parçaya ≥ 0,3 mm³ giriyorsa altıgen cep sayıldı.
3. **Ev pozu dışı pozlar:** kollar yalnız ev pozunda tarandı. S1 kaseti ±45 / 90°'de ayrıca ölçüldü. Rehber dirsek/bilek
   açıları için "kolu kaldırarak" notu verirse yeniden ölçülmeli.
4. **Kablolar ve konnektörler CAD'de yok.** K1/K2'nin içeriği `taban` kablo yolu şemalarından ve S1-kaset.md'den alındı.
   Kablonun alet yolunu kapatması ölçülmedi.
5. **Servis ölçümünde 117 erişilemez bağlantı var.** Çoğu tasarım gereği iç kalıyor (taban kartları, servo kulakları, iskelet).
   Servis yolu: etek H1 → sigortalar; arka kapak(lar) → gövde içi; kol sökümü → omuz bandı.
6. Sigorta kutusu, ana sigorta yuvası ve ana anahtar "tahmini zarf". K5/K6/K7 ölçüleri gerçek parça seçilince güncellenmeli.
7. **CAD değişikliklerinden sonra:** C1–C3 ve K1–K7 uygulanınca, 6. adımda yeniden üretimden sonra `M6_erisim.py` ve
   `M6_ek.py` yeniden koşulmalı (~15 dk) ve bu tablo güncellenmeli.
