# Y0f günlüğü: fizik simülasyonu (CAD'den kütle / AM / atalet modeli, MuJoCo dünyası sahte ESP32'nin altında, ölçümler, 3B pencere) (A ajanı)

Paket: **Y0f** (Y0s'un fizik katmanı; ad Y0s ile aynı mantıkta, `P<sayı>.<sayı>` değil: döngü paketi değil, yazılım planı Y0–Y3'ün
donanımsız ön çalışmasının devamı). Önerilen commit öneki `Lale Y0f:` (commit ve push C adımında). A başlangıcı 22.11.2026 20:52
(saat okundu). Dal `lale-duzeltme`, HEAD `bec3f03` (yerel = uzak). `git add` / commit / push yapılmadı. CAD kaynakları, rehber,
`planlama/d158/` denetim betikleri, 21 eski kirli dosya kapsam dışı (yalnız okundu).

Kesilirse devam: § 9 "Durum" en son yapılanı ve sıradakini yazar.

## 1. Başlangıç durumu (ölçülen)

| Ne | Değer |
| --- | --- |
| HEAD | `bec3f03` (yerel = uzak) |
| Eski kirli dosyalar | 21 (`Y0f-olcum/git-status-bas.txt`: 14 M + 7 ??); md5 `Y0f-olcum/kir-bas.md5` (paketten önce alındı) |
| 2B testler | `py -3 kod/testler/kos.py` 58 / 58, 9,1 s |
| Python | `py -0`: yalnız 3.14.0 (py başlatıcısı). Ayrıca uv'nin 3.12.14'ü (CAD sanal ortamı) var, kullanılmadı |

## 2. Araç ve ortam

- **MuJoCo 4.0.1** Python 3.14 tekerleğiyle kuruldu (ilk deneme; PyBullet'e gerek kalmadı). Bağımlılıklar: numpy 2.5.5, glfw 2.11.0,
  PyOpenGL 3.1.10, mujoco-core / mujoco-studio / mujoco-studio-wasm 4.0.1, websockets 17.4 (tam liste `kod/fizik/gereksinimler.txt`).
- Sanal ortam **depo dışında**: `%LOCALAPPDATA%\lale-sim-venv` (`py -3.14 -m venv`; küresel Python'a paket kurulmadı). Belgede yol ortam
  değişkeniyle yazılır; `LALE_SIM_VENV` ile başka yer verilebilir.
- Ham CAD ağı (≈ 20 MB) OneDrive dışında önbellekte: `%LOCALAPPDATA%\lale-fizik-onbellek\cad_ham` (`LALE_FIZIK_ONBELLEK`). Depoya
  yalnız seyreltilmiş görsel ağ (≈ 2,9 MB) ve JSON girer (CLAUDE.md: "büyük geçici dosyaları buraya koyma").

## 3. Kaynaklar ve çelişkiler (düzeltilmedi, yalnız kayıt)

| # | Ne | Kaynaklar | Modelde kullanılan |
| --- | --- | --- | --- |
| Ç-f1 | Sağ / sol | CAD grup adları önden bakanın sağı (K65: CAD "Sag" = +X = robotun kendi solu); `eklem_sinirlari.json` `r_*` CAD adını izler (`r_s1` ayna false = CAD +X); `protokol.json` servo adları robotun kendi sağı ve `sag_omuz` → `r_s1` | Gövde ve servo adları robotun kendi çerçevesinde: `sag_*` gövdeleri CAD "Sol" gruplarından. Sınırlar iki yanda aynı olduğu için sonuç değişmez; ama `sag_omuz` → `r_s1` eşlemesi adca CAD'in sağını (robotun solu) gösteriyor, Efe / Ahmet bakmalı |
| Ç-f2 | Sarhoş teker | Brief "tahrik tekerleri ve sarhoş tekerler"; eski CadQuery modeli (`tasarim/cad/robot_cad.py` bölüm 6) 2 tahrik + 2 sarhoş; **güncel FreeCAD montajı 4 × JGB37 tahrikli, sarhoş teker yok** (montaj-analiz.json 4 teker eklemi, BOM'da sarhoş teker yok) | Güncel montaj: 4 tahrikli teker (kızak yönlendirme). Kütle / AM `montaj-analiz.json`'dan; `robot_cad.py` (125 cm dönemi) kullanılmadı |
| Ç-f3 | Motor durma torku | Direnc.net 21 kg·cm (taban-analiz.json `stall_kgcm`) ↔ Aslong tablosu oran 90: 9 kg·cm (`06-aku-secimi.md`) | 21 (ana), 9 (duyarlılık) |
| Ç-f4 | 60 dev/dk yüksüz mü anma mı | BOM / satıcı "60 dev/dk"; Aslong oran 90 → 66 | 60 yüksüz kabul, gerilimle ölçeklenir (TAHMİN) |
| Ç-f5 | Kütle | OZET.md 25.715,6 g (09.11) ↔ montaj-analiz.json 25.876,13 g (20.11 üretim) | montaj-analiz.json (+ 400 g kablo payı TAHMİN) |

## 4. Yapılanlar (adım adım)

1. 20:52–21:00 kaynak okuma (Y0s günlüğü / kontrolü / SIMULASYON.md, CLAUDE.md, README, freecad README / OZET, montaj-analiz.json,
   taban-analiz.json, BOM, `origin/main` `kod/esp32/src/motorlar.cpp` ve `guc.cpp` yalnız `git show` ile). Önemli: firmware'de
   `PWM 0 + EN HIGH = BTS7960 fren`, `EN LOW = boşta` (motorlar.cpp yorumu); bekçi `motorlar_ani_dur` EN'e dokunmaz (fren), acil stop /
   arıza / bırak EN LOW (boşta); PID katsayıları 0 (açık çevrim, `u = rampa_hiz / 0,39`).
2. MuJoCo kurulumu (§ 2). Duman testi geçti.
3. `kod/fizik/cad_cikar.py` (FreeCAD 1.1, `run_fc.py` başlatıcısı): `robot-montaj.FCStd` **geçici klasöre kopyalanıp** açılır (CAD
   klasörüne yazılmaz; sonra `git status` aynı), 1.251 parça: `Kutle_g`, katı hacmi, AM, `MatrixOfInertia` (kutu ve L şekliyle doğrulandı:
   AM'de, köşegen dışı −∫xy), parça başına üçgen aralığı; 22 grup paralel eksenle toplanır → `kod/fizik/model/cad_govdeler.json`.
   FCStd toplamı 25.876,14 g, AM (0,0345; 526,18; −9,71) mm = montaj-analiz.json (25.876,13 g; aynı AM).
4. `kod/fizik/fizik_parametreleri.json`: CAD'de olmayan her sayı (sürtünme, motor, servo, temas, kablo payı) kaynak / TAHMİN ile.
5. `kod/fizik/model_uret.py` (standart kitaplık): gövde ağacı (taban serbest; gövde = iskelet + kabuk + omuz gövdeleri + kafa gövdesi,
   tabana sabit; kafa boyun / baş; kol başına omuz göbeği, üst kol, ön kol, el; 4 teker), eklemler montaj-analiz.json eksen / noktası,
   sınırlar eklem_sinirlari.json; görsel ağ köşe kümelemeyle 5 mm'ye seyreltildi; çarpışma ilkel şekiller → `model/lale.xml`,
   `model/kutle_karsilastirma.md`. Model 26.276,1 g = montaj + kablo payı (fark +0,01 g, AM farkı < 0,01 mm); taban-analiz ev pozu ile
   fark +0,04 g, AM ≤ 0,04 mm. MuJoCo'da derlenince `body_mass` toplamı 26,2761 kg, `subtree_com` aynı.
6. İlk hata (düzeltildi): CAD "Sag" gruplarını robotun sağına koymuştum; K65 okununca ters çevrildi (Ç-f1).
7. `kod/fizik/dunya.py` (MuJoCo dünyası: sahne, motor modeli, ışın, temas okumaları), `kod/fizik/fizik_esp32.py` (`SahteEsp32` alt
   sınıfı: yalnız `_hareket`, `_dilim`, `_sonar_olc`, `konum_ayarla`, `hakem` kancaları; firmware modeli aynen), `kod/testler/duzenek.py`
   `LALE_HEDEF=fizik` (mujoco yoksa SkipTest). 2B 58 / 58 değişmedi.
8. Hız okuması hatası (düzeltildi): `mj_objectVelocity` yerel kipte gövdenin ana atalet eksenlerini kullanıyor; serbest eklem `qvel`'inden
   hesaplandı.
9. İlk fizik koşusu (Y0s testleri `LALE_HEDEF=fizik`): 33 senaryo testinin 22'si geçti, 11'i kaldı; ayrıntı § 6.
10. Sonar: 2B'de kalınlıksız iç duvar 3B'de 4 cm ortalı kutu olunca uzaklık 2 cm kısa çıktı; iç duvar 2 mm levha yapıldı
    (`ic_duvar_kalinligi_m`), SonarMenzil geçti.
11. Yuvarlanma direnci (crr 0,03, taban-analiz ile aynı) teker eklemine sabit sürtünme olarak eklendi; ölçüm kaydı her fizik
    adımında (`adim_kaydi`).
12. **Hata (düzeltildi, sonuçları değiştirdi):** MuJoCo temas sürtünmesini iki geom'un büyüğünden alır; zemin geom'u varsayılan
    µ 1 taşıdığı için robotun µ'sü (0,8 / 0,5) hiç etkimiyordu. Sahne geom'larına `friction="0 0 0"` verildi; temas µ'sü artık
    robot tarafının değeri. Bundan önceki dönüş / fren sayıları atıldı, ölçümler yeniden koşuldu.
13. `kod/fizik/olcumler.py`: model, statik devrilme (yerçekimi eğdirilerek, tekerler kilitli; ilk ölçüt teker yükü <1 N idi,
    silindir temasında yük ±3 N oynadığı için 2 derece erken veriyordu, ölçüt "taban 0,5° döndü" yapıldı), fren (dur / bekçi /
    acil × ileri / geri × ev / kollar öne × 5 parametre takımı + firmware fren eğrisi), kol (520 poz + dinamik salınım), çarpışma,
    rampa (3–20°, sonar kapalı / açık), eşik (5–40 mm, 0,2 / 1,0), dönüş (µ 0,2–0,8 × 21 / 9 kg·cm), kalkış torku.
14. Eşik ve rampa ilk koşusunda robot 40 mm eşikte ve 15° rampada hiç ilerlemedi: firmware modelinin TASLAK sonar kuralı (30 cm
    dur) eşiği / rampayı engel saydı. Ölçüm ikiye ayrıldı: sonar kapalı (mekanik sığa) ve sonar açık (bugünkü kural).
15. 20° rampada robot geri devrildi (statik geri devrilme 18,6°): fizik doğru; devrilme ölçütü "eğimden 8° sapma" yapıldı.
16. `kod/fizik/carpisma_denetim.py`: 1.225 CAD parçasının dışbükey zarfı, MuJoCo temas denetimi. İlk koşuda hiç temas yoktu:
    `mjDSBL_CONSTRAINT` temas denetimini de kapatıyormuş; kaldırıldı. Sonuç § 5.
17. `kod/fizik/testler/test_fizik.py` (6 test) ve `kod/fizik/kos_fizik.py` (3 bölüm; Y0s'ta beklenen farklar gerekçeli liste).
18. 3B pencere `kod/fizik/gorunum3b.py`, `kod/simulasyon3b.bat`, sahneler `oda_rampa`, `rampa_parkuru`. İlk sürüm donuyordu
    (§ 7), düzeltildi.
19. `kod/SIMULASYON.md` "Fizik simülasyonu (Y0f)" bölümü, `kod/fizik/gereksinimler.txt`.

## 5. Ölçüm sonuçları ve el hesabı farkı

Ham sayılar `Y0f-olcum/olcum.json`, okunur döküm `olcum.md`; özet ve yorum `kod/SIMULASYON.md` "Fiziğin söyledikleri".
El hesabı ile fark: statik ileri / geri devrilme +0,1° (20,7 / 18,6 ↔ 20,6 / 18,5); yana +2,8° (el hesabı teker merkezi,
fizik teker dış kenarı); aks yükleri < 0,1 N; bekçi duruşunda frende yükü azalan aks 0 N'ye iner (düzeltme turunda: bu
bölümdeki eski "tepe 3,1–3,2 m/s², 0 N 60–100 ms" ölçüm penceresi ve temas ayarı ürünü, hüküm değil; doğru üçlü ayrım ve
aralıklar § 10 ve `SIMULASYON.md`); rampada kayma hızı el hesabıyla aynı (0,034 / 0,10 m/s); yerinde dönüş eşiği µ 0,4 civarı
(firmware u 0,55 ile; tam PWM'de farklı: § 10);
kalkış torku fizik tepe değeri el hesabından 0,02–0,08 N·m yüksek (geçici rejim).

## 6. Testler

- 2B: `py -3 kod/testler/kos.py` 58 / 58 (paketten önce ve sonra).
- Fizikte (`kos_fizik.py`): fizik testleri 6 / 6; Y0s 58 testin 48'i geçer, 10'u beklenen fark (`BEKLENEN_FARK`, gerekçeli):
  AcilStop × 2, BaglantiKopmasi, Bekci × 3, BozukMesaj (durma anlık değil), SinirDisiHiz × 3 (açık çevrim hız, kızak dönüş).
  Bir koşuda `test_gorunum.test_yalniz_ayni_koken` (gerçek zamanlı HTTP) kaldı, tek başına 4 kez geçti: kararsız, fizikten
  bağımsız görünüyor; koşucu yeniden dener ve "KARARSIZ" yazar. B bakmalı.
- Üç ardışık tam koşu: `Y0f-olcum/kosu-1..3.log` (§ 9).

## 7. 3B pencere

- Ana oturumun gönderdiği ilk görüntü: başlık "Yanıt Vermiyor", sahne beyaz, Türkçe harfler kutu, katman panelleri örtüyor.
  Bulgular ve değişiklikler:
  1. Donma: `set_texts` görüntüleyici kilidinin (`v.lock()`) içinde çağrılıyordu; kendi kilidini aldığı için kilitleniyordu.
     Kilit dışına alındı. 60 s sürüşte pencere 11 kez taşındı / yeniden boyutlandı, her seferinde `Responding = True`; döngü
     sanal = duvar saati (18,0 / 18,0 s; 45,0 / 45,0 s), en uzun döngü 62–283 ms (283 ms ekran görüntüsü alınan kare).
  2. Beyaz sahne: kamera robotu 135° azimutla izliyordu, oda köşesinde duvarın dışına düşüyordu. Kamera robotun arka-sağından,
     3,5 m, −30°; duvarlar yarı saydam.
  3. Türkçe harfler: MuJoCo yazı tipi yalnız ASCII; katman metni ASCII'ye çevrildi (`ascii_tr`).
  4. Katman üst üste / panelleri örtüyor: MuJoCo'nun sol / sağ panelleri kapalı açılıyor, katman sol altta tek kutu, 4–6 satır.
  5. Katmandaki konum / teker yükü okuması: model ve fizik çalışıyordu (doğrulandı: aynı kod başsız 25 adımda sorunsuz).
- Bakılan ekran görüntüleri (paket dışında, geçici klasörde): odada robot ve kolon, acil stop, kollar öne-yukarı, kollar yana,
  10° rampada tırmanış ve `dur` sonrası rampada geri kayma (katmanda ölçülen v −0,10 m/s: § 5 bulgusu pencerede de görünüyor).
- Klavye: gerçek tarama kodlu tuş olaylarıyla (keybd_event) Home, Yukarı × 3, Sol, Sağ, Delete × 2, Page Up × 2 işlendi
  (günlükte "komut v 0,30", "ACIL STOP mantari BASILDI", "kol pozu: one"). SendKeys'in tarama kodsuz olayları GLFW'de −1
  geliyor (yalnız yapay olay sorunu). F12 ile sahne değişimi SendKeys ile çalıştı. Pencere X ile kapatılınca python süreci
  kalmıyor (bellek taşıması: port açılmaz).

## 8. B için bakılacaklar

- `kod/fizik/fizik_parametreleri.json`: her TAHMİN'in kaynağı ve makullüğü (özellikle durma torku 21 / 9, dişli sürtünmesi).
- Sağ / sol eşlemesi (Ç-f1, `model_uret.py` `AGAC`, `EKLEM_ESLE`) ve `kutle_karsilastirma.md`.
- `kos_fizik.py` `BEKLENEN_FARK`: gerekçeler fizik olarak doğru mu, gerçek hata gizleniyor mu.
- `kod/testler/duzenek.py` değişikliği (tek dosya Y0s'tan); 2B 58 / 58.
- Ölçüm yöntemleri: statik devrilme ölçütü, fren tepe ivmesinin 5 ms penceresi, sonar_kisti tanımı, eşik "geçti" ölçütü.
- 3B pencereyi kendisi açıp sürmeli (`kod\simulasyon3b.bat`).

## 9. Durum

- 21:20 civarı: § 4 madde 1–9 bitti.
- 22:00 civarı: madde 10–19 bitti. Üç ardışık tam koşu (`kosu-1..3.log`): her biri çıkış 0, fizik 6 / 6, Y0s 48 + 10 beklenen
  fark, ölçüm sayı özeti üçünde aynı `70a9a5a6e4b0dd5c`, süre 137,3 / 135,5 / 135,2 s. 2B 58 / 58 (9,5 s). 21 eski dosya md5
  21 / 21 aynı. Yeni dosyalarda pre-push kalıpları (yerel yol, takma ad, e-posta, ekip soyadları) 0 bulgu. Pencere kapanınca
  python süreci 0. A işi bitti; sıra B.

## 10. Düzeltme turu (B: KOŞULLU GEÇER, `Y0f-kontrol.md`)

B'nin raporu okundu; K1–K10 ve küçük maddeler. Sınırlar aynı (git add / commit / push yok, 21 eski dosya ve CAD dokunulmadı).

- **K4 + K5 (muafiyet).** Test düzeyindeki `BEKLENEN_FARK` (10 test) boşaltıldı; farklar doğrulama düzeyine indi:
  `kod/testler/duzenek.py` `FIZIK_FARKLARI` (6 kalem: `durus`, `reset_odo`, `dur_fren_yolu`, `kablo_yolu`, `hiz_esitligi`,
  `w_kirpma`) ve yardımcılar `surucu_kesik_dogrula`, `durus_dogrula`, `hakem_durdu`, `hiz_esit`, `enkoder_duruyor(durus=)`.
  `test_guvenlik.py`'de 10 testte ilgili satırlar bu yardımcılardan geçer; 2B yolu satır satır eskisi (2B 58 / 58). Fizik
  arka ucu hakeme sürücü girişini (`surucu`: EN, PWM, teker hedefi) ekledi. "Anında durma" yerine: sürücü komutu kesik +
  pay içinde durma. Paylar protokol üstünden 0,3 m/s'den ölçüldü (`kod/fizik/fizik_esp32.py` + istemci, ana parametreler):
  bekçi freni 270 ms / 15,6 mm -> pay 400 ms / 25 mm; acil stop boşta 870 ms / 0,128 m -> 1,3 s / 0,20 m. Fizikte 58 / 58
  geçer; eski 10 muaf testin 70 doğrulama çağrısının hepsi fizikte koşuyor (6'sı fiziksel karşılığıyla). `KARARSIZ` yeniden
  denemesi yalnız `test_yalniz_ayni_koken`. K5'in iki yanlış gerekçe metni muafiyetle birlikte kalktı; yeni metinler
  `FIZIK_FARKLARI`'nda gerçek doğrulamayı anlatıyor.
- **K4 bozma deneyi.** `cekirdek.py` `_bekci_kontrol` içinde `_motor_ani_dur()` -> `pass`: 2B çıkış 1 (5 kalan: bekçi × 2,
  bozuk satır, kablo, TCP soket); fizik koşusu çıkış 1, aynı 5 test "YENİ KALAN" (bekçi testleri "firmware teker hedefi
  sıfırlanmadı: [0,3, 0,3]"). Geri alındı; `cekirdek.py` md5 önce / sonra `bf8b866155e18149dcc9ea987fd50329` (bozukken
  `b12fecef...`). Çıktı `Y0f-olcum/k4-bozma.log`.
- **K1 (dönüş).** `olcumler.py` `donus` `yerinde_firmware_ve_tam_pwm` (tam PWM: `FizikEsp32.pwm_zorla`, yalnız ölçüm).
  21 kg·cm: firmware (u 0,55) µ 0,4 / 0,5 / 0,8 -> 0,051 / 0,001 / 0,001 rad/s; tam PWM 0,30 / 0,16 / 0,12. 9 kg·cm: firmware
  0 / 0 / 0, tam PWM 0,001 / 0,001 / 0,001. B ile fark: 21 kg·cm tam PWM µ 0,4'te B 0,17, burada 0,30 (1 / 2 / 5 s sonra 0,28 /
  0,30 / 0,31, kararlı). Fark B'nin betiğinden geliyordu: firmware'i atlayıp tekerlere doğrudan tam PWM, kollar ev pozunda değil;
  kollar ev pozundayken 0,26–0,32 (`Y0f-kontrol.md` § 10.4). Gerçek firmware'e karşılık gelen değer 0,30–0,32; µ 0,4 eşiğe yakın
  olduğu için yük dağılımına duyarlı. µ 0,5 / 0,8 yakın; hüküm aynı.
  `SIMULASYON.md` dönüş maddesi yeniden yazıldı, seçenekler "Karar isteyenler"de tarafsız.
- **K2 (rampada tutma).** Ölçüt yukarı süzülmenin bittiği andan (dur sonrası en yüksek x): 5 s'de geri kayma ve son 2 s
  ortalama hız; dur sonrası 15 s izleniyor (ping'le sessizlik beslenir). Ana (dişli 0,05): 3° 7,7 mm/s / 3,8 cm, 5° 34,4 / 16,8,
  10° 101 / 48,8. Dişli 0,2: 3° 2,5 / 1,2 (el hesabı 0; MuJoCo yumuşak sürtünme kısıtı sızması), 5° 5,8 / 2,9, 10° 72 / 34,9.
  Hiçbirinde tutmuyor; "0,2 N·m'de 5°'de durur" cümlesi kaldırıldı. B'nin sayılarıyla aynı.
- **K3 (bekçi).** `fren.bekci_duyarlilik` (ana, 15 / 9 kg·cm, solref 0,002 / 0,008, dt 0,5 ms) + 2 ms pencere
  (`tepe_yavaslama_2ms_m_s2`). 10 ms tepe 2,9–3,9, 2 ms 4,2–10,7 m/s², 0 N 25–71 ms; 9 kg·cm'de aks 65 N. B'nin tablosuyla
  aynı. Eski yazıda "5 ms ortalamalı" yanlıştı: ±5 adım = 10 ms. Metin (a) / (b) / (c) ayrımıyla yeniden yazıldı.
- **Küçükler.** Yana devrilme 25,2° (245 mm) ve iki geometri cümlesi; yansıyan atalet 0 / 0,005 / 0,01 / 0,015 × dişli 0,05 /
  0,2 ile acil stop kayması 0,08–0,29 m (`fren.acil_stop_araligi`); "Karar isteyenler" tablosu; B'nin bakmadıkları
  (sonar 15° / 40 mm, zarf taraması, dinamik kol, FreeCAD ataleti) "bağımsız kontrol edilmedi"; sahne değişiminin komut satırı
  yolu; K8 hakem 0,1 mm/s kırpması belgede. K9 (`olcum.md` dökümü) değiştirilmedi.
- **Bitiş denetimi.** 2B 58 / 58 (9,1 s). Fizik iki tam koşu (`kosu-4.log`, `kosu-5.log`): ikisi de çıkış 0, fizik 6 / 6,
  Y0s 58 / 58, sayı özeti ikisinde `f3507f3911bd53da` (eski `70a9a5a6e4b0dd5c`: ölçüm alanları değişti), 168 / 171 s.
  21 eski dosya md5 21 / 21. Pencere bir kez açıldı (20 s `Responding = True`), kapatılınca yeni python süreci 0.
  `Y0f-olcum/kosu-1..3.log` düzeltme öncesi koşulardır (eski muafiyet listesi ve eski sayı özeti `70a9a5a6e4b0dd5c`); güncel
  koşular `kosu-4.log`, `kosu-5.log`.
- **Kapanış (C) notları.** `Y0f-olcum/olcum.json` ve `olcum.md` kapanış ön kontrolündeki fizik koşusuyla (C, 22.11) yeniden
  yazıldı: sayı özeti aynı (`f3507f3911bd53da`), süre alanları o koşunun. `kod/fizik/testler/test_fizik.py`'de atlama dekoratörü
  bir ada bağlandı (`fizik_gerekli`), çünkü `pre-push` kancasının e-posta kalıbı sütun 0'daki `@unittest.skipUnless` satırını
  yanlış alarm olarak yakalıyordu; davranış değişmedi (mujoco yokken 6 test atlandı, sanal ortamda fizik 6 / 6).

## 11. Kapanış (C)

C ajanı, 22.11 (saat okundu: 23:04).

**Adım 1, paket commit'i `0ed416f`** ("Lale Y0f: fizik simülasyonu (MuJoCo): …"; 50 dosya, ≈ 4,3 MB).
- Ön kontrol: yerel = uzak = `bec3f03`; F9c 2 (yapısal, K68); 2B 58 / 58; fizik koşusu çıkış 0, fizik 6 / 6, Y0s fizikte 58 / 58,
  sayı özeti `f3507f3911bd53da`; 21 eski dosya md5 21 / 21.
- Commit'ten önce B'nin Y1 önerisiyle iki belge düzeltmesi (`kod/SIMULASYON.md` "Karar isteyenler" dönüş satırı; 0,17 / 0,30 farkının
  açıklaması `SIMULASYON.md` ve bu günlük § 10 K1'de) ve `test_fizik.py` dekoratörü (yukarıda). Atlama iki yönde sınandı: sistem
  Python'u (mujoco yok) 6 / 6 "atlandı"; sanal ortam fizik 6 / 6, özet aynı.
- `pre-push` kalıpları sahnelenen farkın tamamında 0 (dekoratörden önce e-posta kalıbı 2 satırda yanlış alarm veriyordu); commit'ten
  sonra kanca bu aralıkta çalıştırıldı: çıkış 0. Konu öneki `Lale Y0f:` (Y0s emsali; döngü paketine bağlanmaz).

**Adım 2, kayıt eşitlemesi** (bu bölümle aynı commit): `dongu-158.md` § 5 satırı ve § 3 F5 altına Y0f notu; `karar-kuyrugu.md`
K75–K80 (açık 34 → 40, toplam 80) ve "Y0f … kapanışından açık iş" bölümü; `F9c-uret.py` `Y0F` / `Y0FK`, `GRUP` K75–K80 (taslak), iki
sayfa notu; sayfa yeniden üretildi. `F9c-dogrula.py` değişmedi. Push ve commit sonrası ölçüm orkestratöre raporda.

## 12. Kumanda ve hareket hâlinde dönüş (A, commit yok)

Ahmet 3B pencereyi denedi: "basılı tutunca dönsün ve ileri geri gitsin bide o kadar az dönüş yapıyor ki 10 kere ileri geri
yaptım hala daha engeli aşamadım"; Home tuşunu dizüstünde bulamadı.

**1. Kumanda** (`kod/fizik/gorunum3b.py`, `kod/SIMULASYON.md` tuş bölümü):
- Oklar basılı tuttukça sürer: Yukarı / Aşağı 0,25 m/s (Shift 0,39), Sol / Sağ 1 rad/s, birlikte yay; bırakınca `dur`. Kademeli
  artırma kalktı. `sur` 200 ms'de bir protokolden (bekçi 500 ms). Eski görünüm `sur.v`'yi 0,39'a bölüp gönderiyordu (m/s yerine
  oran; 0,3 m/s komut 0,77'ye gidip kırpılıyordu): düzeltildi, artık m/s.
- Bırakma: Windows'ta her döngüde `GetAsyncKeyState`, yalnız ön plandaki pencere bu süreçteyse; odak yoksa basılı tuş yok
  sayılır (robot durur). Görüntüleyicinin tuş geri çağrısı yalnız basma / tekrar veriyor.
- Tuşlar: 6 devreye al, 7 dur, 8 acil stop, 9 gücü bırak, Enter kol pozu, Shift+6..9 rampa kipi / kafa / başa koy / sonraki
  sahne; eski tuşlar duruyor. Çakışma: görüntüleyici modülünün kısayol tablosu (harfler `mjVISSTRING` / `mjRNDSTRING`
  bayrakları, " 0".." 5" geom grubu, "S0".."S5" site grubu) ve canlı sınama (pencerede 0 geom grubu 0'ı kapattı; 6–9,
  Shift+6–9, Enter görüntüleyici seçeneklerini değiştirmedi).
- Katman: sol üstte kalıcı ipucu (devrede değilken en üstte "ONCE 6'YA BAS", acil stopta "önce 8, sonra 6", odak yokken uyarı);
  sol altta komut / gerçek v ve w yan yana.
- Sınama (`kod\simulasyon3b.bat` temiz açılış, gerçek tarama kodlu basılı tutma / bırakma olayları): 6 -> arm ok; Yukarı
  basılı 2,5 s -> komut 0,25 / gerçek 0,24, bırakınca dur; Sol basılı -> komut w 1,00 / gerçek 0,00 (yerinde dönmüyor, K75);
  Yukarı+Sol (yay) -> v 0,25 / 0,02, w 1,00 / 0,00; Aşağı, Shift+Yukarı (0,39) çalıştı; Yukarı basılıyken başka pencere öne
  geldi -> "odak kayboldu", dur, gerçek 0 / 0 (tuş hâlâ basılı); 8 -> arıza ACIL STOP, 8 + 6 -> yeniden sürüş. Pencere
  yanıt veriyor, en uzun döngü 97 ms; kapanınca python süreci 0. Ekran görüntülerine bakıldı (depo dışında).
- 2B 58 / 58; fizik koşusu çıkış 0, sayı özeti `f3507f3911bd53da` (değişmedi; görünüm ölçümlere girmiyor).

**2. Hareket hâlinde dönüş** (`kod/fizik/olcum_donus_hareket.py` yeni; çıktı `Y0f-olcum/donus-hareket.json` / `.md`; iki koşu
md5 aynı `c8caa97b…`; `olcumler.py` ve `olcum.json` değişmedi, sayı özeti aynı):
- Firmware karışımı `origin/main:kod/esp32/src/motorlar.cpp` `motorlar_hedef` (satır 268–280) ve `teker_adim` (220–244) ile
  model (`cekirdek.py` `_motor_hedef`, `_teker_hedefleri`; `fizik_esp32.py` `_surucu`) aynı: v, w ±1 kırpma, iz 0,426, büyük
  teker 0,39'u aşarsa iki teker birlikte ölçek, u = rampa_hiz / 0,39, KP = 0, hedef 0 ise PWM 0 (fren).
- µ 0,5 / 0,8 × 21 / 9 kg·cm × v 0,1 / 0,2 / 0,3 / −0,2 × w 0,1 / 0,25 / 0,5 / 1: gerçekleşen w hepsinde ≤ 0,001 rad/s; yarıçap
  ve 90° süresi tanımsız (dönmüyor). Dönme µ 0,4'te başlıyor (w 1 ile 0,04–0,05), µ 0,3'te 0,13, µ 0,2'de 0,24–0,27 rad/s; en
  iyi komut her µ'de w 1 (pencerenin w'si değiştirilmedi).
- Manevra (kolonun 0,9 m önü, 1,5 s ileri-sol + 1,5 s geri, sonar açık): geri-sağ ile 20 tekrarda 0,0 / 0,1°, geri-sol ile
  3,3 / 3,4°; 45° ve 90°'ye ulaşılmadı. Pencerede Aşağı+Sağ w −1 gönderir (yön oku gibi değil, dönme yönü), ileri-sol ile
  birbirini götürür; ama tutarlı yönle de dönmüyor.
- Pencere gözlemi (Yukarı+Sol'da v 0,02): aynı tuş dizisi başsız, sonar açık 0,022 (kolona 32 cm, firmware ileri sınırı
  0,05), kapalı 0,199 m/s: neden TASLAK sonar kuralı, karışım değil; pencerenin komutu başsızla aynı.
- Eski pencerenin `sur.v`'yi 0,39'a bölmesi ölçümleri etkilemedi: `olcumler.py`, testler ve bu ölçüm istemciyi doğrudan m/s
  ile sürer, pencereyi kullanmaz; yalnız § 7'deki pencere gözlemlerinde gönderilen hız yazılandan büyüktü (0,3 -> 0,77, 0,39'a
  kırpılır).

## 13. Dönüş varyantları (A, commit yok)

A ajanı, 22–23.11 (saat okundu: 00:04). İstek: "ya şöyle olsaydı" karşılaştırması; hepsi VARSAYIM, varsayılan V0 (bugünkü
firmware 0.5.0 + mekanik), testler ve sayı özeti değişmez.

- **Kod.** Yeni `kod/fizik/varyantlar.py` (V0, V1, V2, V3, V4, V1+V3, V2+V3; ön teker XML dönüşümü), `kod/fizik/olcum_varyantlar.py`.
  `dunya.py` (`model_kur` / `FizikDunya` `varyant` seçeneği; V3 / V4 makara açısı her adımda 0; V4 ön tekerler tahriksiz),
  `fizik_esp32.py` (`varyant`: `w_giris`, PI, V4'te enkoder arkada), `olcumler.py` (`Deney` `varyant` geçirir; kendi ölçümleri
  hep None). Varyant None iken hiçbir yeni dal çalışmaz.
- **Modelleme.** V1 `w_giris` 3. V2 PI kp 2, ki 10 (TAHMİN), doyumda integral durur, hedef 0'da PWM 0. V3 ön temas küre +
  robotun x ekseninde pasif makara menteşesi; ilk denemede makara dönerken teker ekseni yatıyor ve çekiş kayboluyordu
  (yerinde w 0); çözüm makara açısını her adım sonunda 0'a döndürmek (küre simetrik: temas değişmez, hız korunur). V4 aynı
  model, ön motor ve dişli yok (bilyalı sarhoş). Yapılmayan: arkada sarhoş teker, dönen çatallı sarhoş teker dinamiği, iz /
  dingil oranı. Doğru / kaba verdikleri `SIMULASYON.md` "Dönüş varyantları".
- **Ölçüm** (`Y0f-olcum/donus-varyantlar.json` / `.md`, ≈ 85 s, iki koşu md5 aynı `03d05734…`). 21 kg·cm yerinde w µ 0,5 / 0,8:
  V0 0,001 / 0,001; V1 0,118 / 0,126; V2 0,088 / 0,086; V3 0,79 / 0,71; V4 0,52 / 0,38; V1+V3 1,66 / 1,58; V2+V3 0,98 / 0,98.
  9 kg·cm: yalnız V3 (0,43 / 0,25), V1+V3, V2+V3 döner. Kolon dolaşma (`oda_engelli`, 3 ara nokta, 60 s): V0 başarısız; V1 35 /
  44 s, V2 44 / 53 s (21 kg·cm); V3 11–18 s, V4 14–15 s (9 kg·cm'de başarısız), birleşimler 10–14 s. Tork / sürekli (yerinde):
  V0 2,0, V1 / V2 2,1–2,3 (9 kg·cm 3,6 = durma), V3 0,6–0,8. Yan etkiler (µ 0,8, 21 kg·cm): düz gidiş ve fren simetrik
  modelde yönsüz (bu yüzden 10 N / 0,3 s yanal itme eklendi: V3 / V4 6 mm, 0,3 / 0,4°); 5° yan eğimde 5 s düz gidiş V0 0,3
  mm, V3 0,24 m / 16,5°, V4 0,43 m / 29°, V2+V3 0,06 m / 2,9°; V4 `dur` 0,083 m (V0 0,070), V2 0,055.
- **Bulgu (B bakmalı).** Dönerken anlık teker yükü çırpıntılı: std ≈ 100 N, ortalama doğru (61 / 68 N); V0'da da µ 0,2
  kaymasında var (std 116–149 N), yani kayan silindir - düzlem temasının; dönüş hızı iterasyon 200, noslip 5, piramit koniyle
  ±%5 değişti. Pencerede tek karede "88 0 89 0" görüldü, bu çırpıntı.
- **Pencere.** `--varyant`, `kod\simulasyon3b.bat <sahne> <varyant>` (ikinci argüman V ile başlarsa), Shift+Enter sonraki
  varyant (pencere yeni modelle yeniden açılır). V0 dışında üstte kalıcı `VARSAYIM: <ad> (bugunku robot DEGIL)`; durum
  satırında `[sahne, varyant]`. V1'de pencere w'si 3. Geri giderken araba direksiyonu: Aşağı+Sağ w +1 (arka sağa); yalnız
  komut işareti. Bırakma günlüğüne konum (x, y, yön) eklendi. Shift+Enter çakışma sınaması: görüntüleyici seçenekleri
  değişmedi (denetim tuşu 0 geom grubunu değiştirdi).
- **Pencere sınaması** (gerçek tarama kodlu tuşlar, oda_rampa). V0: 6, Yukarı, Sağ 1,6 s, Yukarı, Sol… -> yön hep 0°, kolona
  x 2,36'da yaklaştı (sonar yavaşlattı), dolaşamadı; Aşağı+Sağ -> komut v −0,25 / w +1,00, gerçek −0,20 / 0,00; Shift+Enter ->
  V1 penceresi açıldı, üstte "VARSAYIM: V1 firmware w tavani 3 rad/s (bugunku robot DEGIL)". V3 (bat ikinci argümanı): Sağ 2,2
  s -> −76°, güneyden kolonun yanına (x 2,97, y 0,68), Sol 2 s -> +55° (kolona dönünce sonar durdurdu); Aşağı+Sağ -> yön 59 ->
  99° (arka sağa). Dolaşmayı penceredeki tuş dizim tamamlamadı (dizim kolona döndü), başsız ölçümde V3 12 s'de dolaşıyor.
  Sınama sırasında pencere iki kez odak kaybetti (başka pencere öne geldi); robot o anlarda durdu, kayıtta "odak kayboldu".
  Yanıt veriyor, en uzun döngü 61–81 ms, kapanınca python süreci 0. Ekran görüntülerine bakıldı (depo dışında).
- **Denetim.** 2B 58 / 58; fizik koşusu çıkış 0, sayı özeti `f3507f3911bd53da` (değişmedi; koşunun yazdığı `olcum.json`'da
  yalnız süre alanları değişmişti, commit'teki hâline döndürüldü); `donus-hareket.json` md5 aynı (`c8caa97b…`); 21 eski dosya
  md5 21 / 21; kalıp taraması 14 dosya 0 bulgu, satır başı `@` yok.

## 14. Ek kapanışı (C)

- 23.11 00:28 (saat okundu). Paket commit'i `89583a5` (15 dosya, B'nin listesiyle birebir; `__pycache__` yok). Commit'ten önce
  `SIMULASYON.md`'de yalnız B'nin § 11 düzeltmeleri E1–E4 uygulandı; dosyada kanca kalıpları 0.
- Ön denetim: yerel = uzak = `5d5d3e4`; 2B 58 / 58; fizik koşusu çıkış 0, fizik 6 / 6, Y0s fizikte 58 / 58, sayı özeti
  `f3507f3911bd53da`; koşunun yeniden yazdığı `Y0f-olcum/olcum.json` `git checkout --` ile döndürüldü, `git diff` boş.
- Kanca, sahnelenen ağaçtan üretilmiş dalda olmayan bir commit nesnesi üzerinde değiştirilmeden çalıştırıldı: çıkış 0.
- Kayıt eşitlemesi: `dongu-158.md` § 5, K75 güncellemesi (yeni numara yok; açık 40, toplam 80), açık işlere "Y0f eki" maddesi,
  `sonuc-rapor.html` yeniden üretildi. `F9c-uret.py` Windows konsolunda (cp1254) yazdırırken `UnicodeEncodeError` verdi ve
  sayfayı yazmadı; `PYTHONIOENCODING=utf-8` ile yeniden koşuldu (betik değişmedi).

## 15. Öneri firmware + ön omni (A, commit yok)

A ajanı, 23.11 (saat okundu: 01:07 – 01:32). İstek: K75 yönü (Ahmet: ön iki teker omni, sarhoş teker yok) için firmware önerisi
ve simülasyonda sınanması. Teker seçilmedi; CAD, sipariş listesi, `arayuz.py`, `maliyet.json` değişmedi.

- **Firmware önerisi** (ayrı çalışma ağacı, depo dışında; dal `oneri/donus-omni`, `origin/main` `71cf76d` üstüne; push yok,
  birleştirme yok). Commit'ler: `a41815f` (PI KP 4 / KI 20 TAHMİN, `INTEGRAL_SINIRI` 1,0, iki teker birlikte doyum ölçeklemesi,
  doyumda integral geri alma, hızlanma rampasında integral durur, `W_GIRIS_SINIRI` 1,0), `120a9a7` (integral yalnız hızlanmada
  dursun, frende çalışsın), `e308120` (Efe notu `ONERI-donus.md`). Yalnız `motorlar.cpp` / `motorlar.h`; protokol, watchdog,
  acil stop, güç durumları aynı. `pio run` (esp32dev, depo dışı venv) başarılı: RAM %6,9, Flash %24,4; karta yüklenmedi.
- **Model.** `varyantlar.py`: `ONERI_FW` (C++ sabitleriyle aynı), varyantlar `ONERI`, `ONERI-T`, `ONERI-ADAY` (Nexus 14075
  ölçüleri: temas küresi r 63,5 mm, 480 g, merkez 14,5 mm içeri; ön uç 1 mm yükselir), `oneri_varyanti()`; `SIRA_V` eski
  karşılaştırmayı sabit tutar. `dunya.py`: makara eklemine `frictionloss` (yanal sürtünme × statik teker yükü × r), ön teker
  ölçü seçenekleri. `fizik_esp32.py`: `_oneri_adim` (20 ms; tik farkından hız, PI, doyum, geri alma). Yeni
  `kod/fizik/olcum_oneri.py` -> `Y0f-olcum/donus-oneri.md` / `.json` (≈ 4,5 dk; iki koşu md5 aynı `802bc870…`).
- **Bulunan gerileme ve düzeltme.** İlk öneriyle Y0s fizikte 55 / 58: Y1 ivme testleri (düz 0,575 > 0,56, rampa kipi 0,159 >
  0,15 m/s²) ve PWM oranı testi kaldı. İvme gerçek gerilemeydi (rampa sırasında biriken integral rampa sonunda %6 hız aşması);
  integral hızlanma rampasında durdurularak düzeltildi (ilk düzeltme frende de durduruyordu, 90° aşmasını 7'den 13°'ye
  çıkardı; ikinci commit yalnız hızlanmaya indirdi). Kalan tek test `test_cok_buyuk_w_kirpilir_donus_orani_korunur`: PWM
  oranının hedef oranına eşitliği açık çevrime özgü; hedef kırpma ve oran denetimleri geçiyor; test gevşetilmedi.
- **Sonuç** (ayrıntı `SIMULASYON.md` "Öneri firmware + ön omni"). Yerinde w komut 1: ONERI 0,97–0,98 (21 kg·cm), 0,72–0,86 (9);
  ONERI-T 0,08 / 0,001 (lastikle kapalı çevrim de dönmüyor); ONERI-ADAY 1,05 / 0,69–0,84. 90° 1,9–3,0 s, aşma 8–15° (`dur`
  sonrası fren), salınım yok. Kolon 11–14 s. `dur` 0,046 m (V0 0,070). 5° yan eğim 5 s'de 0,05 m (V3 açık çevrim 0,24).
  Rampada tutma değişmedi. Makara yanal sürtünmesi eşiği: 21 kg·cm ≈ 13 N / teker, 9 kg·cm ≈ 5 N.
- **Pencere.** `kod\simulasyon3b-omni.bat` yeni (tek tık ONERI); bat ikinci argümanı `-` ile başlamıyorsa varyant; Shift+Enter
  döngüsü ONERI / ONERI-T / ONERI-ADAY'ı da içerir. B § 11: reddedilen `sur` durum kutusunda "acil stop: komut reddedildi"
  (1,5 s); senaryo `oda_rampa`'da acil stop sırasında Yukarı basılı tutulur. Gerçek tuşlarla sınandı: bat penceresi ONERI
  açtı, Sağ / Sol ile −107° / +92° döndü, kolonun güneyinden geçti; 6, 8, Yukarı -> "sur  acil stop: komut reddedildi" görüldü;
  Shift+Enter -> ONERI-T. Bir denemede pencereye dışarıdan Backspace (GLFW 259, MuJoCo'nun sıfırlama tuşu) geldi, robot model
  başlangıç pozuna döndü; tekrar denemede yok, kaynağı bu sınama betiği değil.
- **Denetim.** 2B 58 / 58; fizik koşusu V0 sayı özeti `f3507f3911bd53da` (değişmedi; `olcum.json` döndürüldü);
  `donus-varyantlar.json` `03d05734…`, `donus-hareket.json` `c8caa97b…` aynı; Y0s fizikte ONERI / ONERI-T / ONERI-ADAY 57 / 58.

## 16. Düzeltme turu: B § 12 (A, commit yok)

A ajanı, 23.11 (saat okundu: bölüm yazılırken 02:12). B'nin hükmü: `lale-duzeltme` KOŞULLU GEÇER
(B1–B3), firmware önerisi HENÜZ HAZIR DEĞİL (F1–F3), pencere R1.

- **F1, enkoder arızası koruması** (öneri dalı `f22a149`). İki katman: (1) PI düzeltmesi en çok `DUZELTME_ORANI` 1,0 ×
  |ileri besleme| + `DUZELTME_TABANI` 0,3 (çıkış ≤ 2 × ileri besleme + 0,3); (2) makullük: düzeltme payın sonundayken hız <
  `KUSKU_HIZ_M_S` 0,02 m/s ya da ters işaretli, `KUSKU_SURE_MS` 500 ms sürerse o teker açık çevrime (0.5.0 davranışı), kilit
  yeniden başlatmaya dek; sıkışmış teker de aynı davranışı alır. Hepsi TAHMİN. `motorlar_enkoder_arizali()`; protokolde alan
  yok, değiştirilmedi (notta `durum` / `ping` için `enk_ariza` önerisi). İlk dar pay (0,5 × + 0,15) 9 kg·cm motorla yavaş
  yerinde dönüşü durdurup yanlış alarm verdi (w 0,5 komutunda 0,008–0,14 rad/s): genişletildi.
- **Model ve test.** `fizik_esp32.py` `_oneri_adim` aynı koşullar; `enkoder_bozuk` (yalnız deneme: "takili" / "ters").
  Yeni `kod/fizik/testler/test_enkoder_ariza.py` (4 test; sağlam 1 s v 0,10, sonra arıza, 3 s): iki yan takılı ya da ters
  korumasız 1,22 m / son 1 s 0,42 m/s -> korumalı 0,36–0,37 m / 0,08 m/s, tespit 510–550 ms; tek yan takılı −84° -> −6,3°,
  tespit 550 ms; sağlam enkoderde alarm yok. Bulunan model hatası: önceki turda eklediğim `_k_odo_sifirla` aynı sınıftaki
  eski tanımın gölgesinde kalıyordu (öneri modelinde odo sıfırlamada `onceki_tik` sıfırlanmıyordu); tek tanımda birleştirildi.
- **Yanlış alarm.** `olcum_oneri.py` korumayı bütün ölçümlerde izler (`donus-oneri.md` "Enkoder arızası koruması"):
  tetiklenme yalnız gerçek durmada: eşiği geçemeyen 9 kg·cm koşuları (her varyantta 4) ve lastikle yerinde dönemeyen ONERI-T.
  Kalkış, omni dönüş (9 kg·cm doyum dahil), rampa, yan eğim, geçilen eşik, duyarlılık ve makara taramasında 0. Eşik tablosu
  korumadan önceki koşuyla aynı.
- **F2.** Dalda `ONERI_PI_ACIK 0` varsayılan: ilk yüklemede KP = KI = 0 (kaçma riski olmayan varsayılan); masada 1 yapılır
  ya da `-DONERI_PI_ACIK=1`. İki hâl de derlendi. Not: masada güvenli sıra (havada yön / enkoder -> elde acil stopla arıza
  denemesi -> KP, sonra KI -> yerde düşük hız), PWM oranı (yarıçap değil; enkoder oranı 0,214 / beklenen 0,170 / açık çevrim
  omni 0,295), ivme eşiği 0,56, makara çekme tarifi ve "mertebe, sınır değil" (öneri dalı `11b2931`).
- **F3.** `INTEGRAL_SINIRI` 0,6, gerekçe ölçümle: 9 kg·cm, yerinde w 0,5: 0,3 ile 0,30–0,36, 0,6 ile 0,46–0,49 rad/s (1,0 ile
  aynı); 21 kg·cm'de fark yok. Kod yorumu ve not aynı sayıyı yazıyor.
- **B1.** `doksan` yönü 10 ms'de bir denetler: aşma 4,4–6,3° (önce 8–15°, 200 ms denetim). **B2.** Eşik bölümüne "kazanç PI'dan,
  omniyle eşik modellenmedi". **B3.** `SIMULASYON.md` ve notta "güvenlik aynı" cümlesine enkoder arızası riski ve koruma.
- **R1.** `gorunum3b.py`: her döngüde `d.time` geri giderse (MuJoCo Backspace = `mj_resetData`) "başa koy": robot başlangıç
  pozuna, servolar firmware açılarına, `dur`; durum kutusunda 3 s "MuJoCo sifirlandi (Backspace): robot basa kondu". Gerçek
  tuşla sınandı (6, Yukarı 1,5 s, Backspace): robot başlangıçta dik, teker yükleri 61 / 68 N, satır göründü.
- **Ölçüm** yeniden üretildi (iki koşu md5 aynı `6699257d…`). Dönüş sayıları değişmedi (21 kg·cm 0,97–0,98; 9 kg·cm 0,72–0,86;
  9 kg·cm w 0,5 0,46–0,49); ONERI-T kolon µ 0,8'de 60 s'de başarılı (önce başarısız; dönemeyen tekerler açık çevrime düştü).

## 17. İkinci ek kapanışı (C)

- 23.11 02:31 (saat okundu). Paket commit'i `8b9d49e` (14 dosya, B § 13 listesiyle birebir; `__pycache__` yok). Öneri dalında
  B'nin N1–N4'ü yerel commit `fc940a0` (`ONERI-donus.md` ve `motorlar.cpp` yorumu; C++ davranışı değişmedi, derlenmedi; push yok).
  `SIMULASYON.md`'de yalnız yakalanmayan enkoder arızaları cümlesi ve K75 satırı değişti.
- Ön denetim: yerel = uzak = `749d6ee`; `index.lock` yok; fizik koşusu çıkış 0, fizik 10 / 10, Y0s fizikte 58 / 58, sayı özeti
  `f3507f3911bd53da`; `olcum.json` `git checkout --` ile döndürüldü, `git diff` boş. 2B beş tam koşuda iki kez 57 / 58: kalan
  `test_gorunum.test_yalniz_ayni_koken` (403 cevabında `WinError 10053`), tek başına 6 / 6 geçti; § 6'daki kayıtlı kararsızlık, paket
  2B koduna dokunmuyor.
- Kanca iki dalın gönderilecek farkında (öneri dalı için yalnız sınama, gönderilmedi) değiştirilmeden çalıştırıldı: çıkış 0; ek tarama
  (takma ad, ekip soyadları, e-posta, yerel yol) 0.
- K75: dosyanın kuralına göre Ahmet'in kararı yazıldı; firmware yarısı Efe'de ve teker seçilmediği için K2 gibi açık kalır, sayaç
  değişmez (açık 40, toplam 80). İlk sürümde durum hücresinden "F5 yazılım hizası" düşmüş, F9c faz hatası verdi; geri eklendi.

## 18. Makaralı omni teker modeli: ONERI-MAKARA (A, commit yok)

A ajanı, 23.11 (saat okundu: bölüm yazılırken 03:42). Ahmet'in isteği: omni teker simülasyonda gerçek teker olarak
modellensin (CAD sonra; bu işte CAD, rehber, web demosu dokunulmadı).

- **Model.** `kod/fizik/omni_makara.py` + tek parametre dosyası `kod/fizik/omni_teker.json` (alan başına `deger` / `durum` /
  `kaynak`). Ürün sayfası (ozrobotics 14075): Ø127, 29 mm, 22 makara Ø19, 480 g, kauçuk, pirinç boru yatak. TAHMİN: makara boyu
  22 mm, sıra aralığı 10 mm, makara 6 g, yatak sürtünmesi 2 N eşdeğer yanal, göbek deliği 6 mm (`arayuz.py` 12 mm altıgen
  adaptör diyor: teyit). Göbek motor eklemi ve enkoderle; 22 makara ayrı gövde + pasif menteşe; temas elipsoid (sapma 0,005 mm),
  seçenek 5 küre / kapsül. `varyantlar.py` `ONERI-MAKARA` + `makara_varyanti()`; `dunya.py` teker geom kümeleri (V0 yolu aynı);
  `duzenek.py` ve `test_enkoder_ariza.py` `LALE_VARYANT` ortam değişkeni (varsayılan yol aynı); `gorunum3b.py` 1 tuşu ipucu ve
  makaralıda ikinci ekran görüntüsü (gövdesiz). `simulasyon3b-omni.bat` -> ONERI-MAKARA (gerekçe: 12–16 × gerçek zaman, uyarı 0,
  gerçek tekere en yakın; küre modeli ONERI-ADAY ile açılır).
- **Bulunan iki sayısal tuzak.** (1) Elipsoid-kutu teması nativeccd, varsayılan ccd toleransı 1e-6'da rampa temaslarının ≈ %3'ünde
  normal 28° sapıyor: 15° rampada sahte çekiş 0,17 m/s (doğrusu 0,09). 1e-9 yalnız bu varyantta. (2) Makara ekleminin Coulomb
  sürtünmesi varsayılan `solimpfriction` 0,9 ile etkisiz: 2 N ile 200 N aynı sonuç, makaralar 36 rad/s dönmeye devam; 0,9999
  ile sınır tutuyor (dof_solimp okunarak doğrulandı). İkincisi bulunmadan önceki ilk ölçüm koşusu atıldı, ölçüm yeniden üretildi.
- **Ölçüm** `planlama/d158/Y0f-olcum/omni-makara.md` / `.json` (`kod/fizik/olcum_makara.py`, ≈ 6,5 dk, çıkış 0; iki koşu RTF süreleri dışında aynı, md5 RTF yüzünden farklı). Değişen:
  9 kg·cm yerinde w 0,78–0,93 (küre 0,69–0,84), yay daha iyi, 5° yan eğim kayması 0,03 m (küre 0,05), 15° rampa 0,09 m/s (küre
  0,10), titreşim 1,58 m'de 0,09–0,15 mm (kapsülle 1,6–2,5 mm; makara geçiş frekansı ölçülen baskın frekansla aynı). Aynı: 21 kg·cm
  dönüş, kolon, `dur` / acil stop, rampa tutma (tutmuyor), eşik 5–15 mm (düzeltme § 19: eşik duyarlılığında makara 25 mm'yi
  geçiyordu, ön enkoderli küre modeli geçemiyordu; "aynı" yanlıştı). Yatak sürtünmesi 9 kg·cm'de
  belirleyici (5 N'da w 0,40–0,53, 7 N'da duruyor). Koruma tetiklenmeleri: geçilemeyen eşikler, 7 N üstü sürtünmeyle duran yerinde
  dönüş ve 9 kg·cm 15° rampa (arka enkoder): hepsi gerçek durma.
- **Enkoder yeri.** Pin planı (`planlama/adim3/pin-haritasi.md`) ve `elektrik.md` enkoderleri arka motorlara koyuyor; simülasyon
  varsayılanı ön (TAHMİN). Arka enkoderle 21 kg·cm yerinde w 0,90 (ön 1,06), 15° rampa 0,12 m/s (ön 0,09); 10° aynı.
- **Doğrulama.** 2B 58 / 58; fizik koşusu çıkış 0, 10 / 10, Y0s fizikte 58 / 58, özet `f3507f3911bd53da` (`olcum.json`
  yalnız süreler, geri alındı); `donus-varyantlar`, `donus-hareket`, `donus-oneri` yeniden üretildi, md5 aynı. ONERI-MAKARA ile:
  enkoder arızası 4 / 4, Y0s fizikte 57 / 58 (ONERI ile aynı kalan `test_cok_buyuk_w_kirpilir_donus_orani_korunur`). Pencere
  gerçek tuşla (6, Yukarı, Sol, 1, Yukarı+Sağ): robot dik, gövde gizlenince makaralı ön tekerler ve arka lastikler görünüyor.

## 19. Düzeltme turu: B § 14 (A, commit yok; öneri dalında yerel commit)

A ajanı, 23.11 (saat okundu: bölüm yazılırken 04:23). B'nin hükmü: makaralı omni KOŞULLU GEÇER (S1–S6), enkoder bulgusu doğru.

- **Enkoder arka.** Öneri varyantları (ONERI, ONERI-T, ONERI-ADAY, ONERI-MAKARA) `varyantlar.py` `ENKODER_ONERI = "arka"`;
  `dunya.py` varyantın `enkoder_teker`'ini uygular, açık `degis` önce gelir (ön enkoder = `degis={"enkoder_teker": "on"}`
  duyarlılığı). `fizik_parametreleri.json` `enkoder_teker` notu "depoya göre ARKA" (pin-haritasi 100–103 / 398, elektrik
  488–495, kablolar N01 / N02, pinler.h 35–38); değer ön kaldı: yalnız V0 ve V1–V2+V3'ün yeniden üretilebilirliği için. V0
  etkilenmedi: fizik koşusu çıkış 0, özet `f3507f3911bd53da`; `donus-varyantlar` / `donus-hareket` md5 aynı (`03D05734` /
  `62C21162`, `C8CAA97B` / `105E9DF4`). Y0s fizikte V0'da bir kez `test_yalniz_ayni_koken` kaldı, yeniden koşuda geçti (§ 6).
- **Yeniden üretim** (arka enkoder). `donus-oneri`: yerinde w komut 1, 21 / 9 kg·cm: ONERI 0,892–0,923 / 0,742–0,880, ONERI-T
  0,085–0,095 / 0,001, ONERI-ADAY 0,893–0,926 / 0,706–0,861; `omni-makara`: ONERI-MAKARA 0,904–0,933 / 0,805–0,916. B'nin
  değerleri (ONERI 0,892, ONERI-MAKARA 0,904, 9 kg·cm µ 0,8 0,742 / 0,805) birebir. Ön enkoderli sayılar iki dosyada
  "enkoder önde olsaydı" tablosunda. Arka enkoderle değişen öbürleri: 15° rampa 0,12 m/s (ön 0,09–0,10; kapsül de çıkıyor),
  eşik duyarlılığında küre modeli de 25 mm geçiyor, kapsül titreşimi 0,75–1,65 mm ileri (ön enkoderle 1,6–2,5), yatak
  sürtünmesi 21 kg·cm'de artık etkisiz değil (7 N'da 0,83–0,87). `omni-makara` iki koşu RTF dışında aynı.
- **Koruma.** Arıza testleri arka enkoderle ONERI ve ONERI-MAKARA'da 4 / 4: tespit 510–550 ms ve iki yan 0,36–0,37 m aynı; tek yan
  takılı korumasız −78° / −80° (ön −84° / −89°), korumalı −5,8° / −6,5° (ön −6,3° / −7,1°). Y0s fizikte iki varyantta 57 / 58
  (bilinen kalan). Ölçümdeki 10 tetiklenme ön ölçümün etiketiyle görünüyordu: kasıtlı arıza denemeleriymiş, etiket düzeltildi
  ("KASITLI ..."); öbürleri gerçek durma (geçilemeyen eşik, ≥ 7 N sürtünme, 9 kg·cm 15° rampa).
- **Belgeler.** `SIMULASYON.md`: ONERI tablosu arka enkoderle + ön duyarlılık satırı, duyarlılık paragrafı, `TEKER_CAPI_M` 0,125
  doğru (%1,6 riski kalktı), K75 satırı (0,97–0,98 yerine 0,89–0,92 / 0,74–0,88; `karar-kuyrugu.md`'ye dokunulmadı, C'nin);
  makaralı bölüm S1 (pencere gerçek zamanda, 9–16 × başsız), S2 eşik cümlesi, S3 titreşim cümlesi, S4 / yatak ölçütü (makara
  başına, iki temasta ≈ 2,1 kat), % ölçütü. `omni_teker.json`: S5, S6 ("enkoder önde 0,17 yerine 0,09; arkada 0,18 yerine
  0,12"), birleştirme notu (tek kaynak adayı `tasarim/cad/omni-teker.json`, merkez kabulü farklı, karar açık).
- **Efe notu** öneri dalında yerel commit `95b7066` (push yok; yalnız `ONERI-donus.md`, C++ değişmedi): enkoder arkada,
  `TEKER_CAPI_M`, tablo arka enkoderle + ön duyarlılık, makaralı sütun, masa sırası "arka enkoderin yönünü doğrula", yana çekme
  ölçütü. Tek teker kilidi sayısı (0,97 -> 0,73) ön enkoderle ölçülmüştü, notta öyle yazıldı.
- **Pencere.** MuJoCo katman metni 500 karakterde kesiliyor (ölçüldü: 555 karakterlik ipucunun 500. karakteri "Shi"). İpucu
  kısaltıldı, `ust_metin` sınırı aşınca önce açıklama satırlarını düşürür (her varyantta en kötü durum ≤ 495). Pencere açılınca
  çalışma alanına sığdırılır (`pencereyi_sigdir`, Windows). Önceki "durum kutusu kesik" görüntüleri DPI'sız ekran yakalamanın
  kırpmasıydı (125 % ölçekte sol üst 1536 × 864 fiziksel piksel); DPI'lı yakalamayla gerçek tuş (6, Yukarı, 1, 8 + Yukarı):
  üst ipucu "Shift+ ... Enter varyant  fare: kamera" dahil tam, ACIL STOP satırıyla tam, sol alt kutu "son" satırına dek
  görev çubuğunun üstünde.
- **Doğrulama.** 2B 58 / 58.

## 20. Üçüncü ek kapanışı (C)

- 23.11 04:29 (saat okundu). Commit 1 `413b8ba` (19 dosya: B § 14.8'in 15'i + düzeltme turunun `olcum_oneri.py`,
  `fizik_parametreleri.json`, `donus-oneri.json|md`). Commit 2 `3ec5b12` (web demosu, 4 dosya; önek `Lale Y0f:`, çünkü F9c'de
  eşleşen tek önek türü döngü paketi etiketi ve demo bir paketin işi değil).
- Ön denetim: fizik çıkış 0, 10 / 10, Y0s fizikte 58 / 58, V0 özeti `f3507f3911bd53da`; `olcum.json` döndürüldü, `olcum.*`,
  `donus-varyantlar.*`, `donus-hareket.*` diff boş; `donus-oneri.md` ONERI 0,892, `omni-makara.md` ONERI-MAKARA ana satırı 0,904 (B: 0,892 / 0,904);
  `SIMULASYON.md`'de ONERI için "0,97" yalnız "enkoder önde olsaydı" (383, 393, 483); 329'daki 0,97 eski V2+V3 tablosunun
  9 kg·cm değeri, bu farkta değişmedi. 2B 58 / 58.
- D1: şablon notu "Demo kabulü" oldu; F9b ilk denemede iki bağsız sayı (14,5 / 29) yüzünden 6 hata verdi; sayılar
  `omni-teker.json` `merkez_fizik` alanına bağlandı (`demo_uret.py`'ye iki anahtar), sayfa yeniden üretildi, F9b GEÇER.
- Kanca her commit'ten önce sahnelenen ağaçta değiştirilmeden: çıkış 0; ek tarama 0. Pages kaynağı `main` /.
