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
