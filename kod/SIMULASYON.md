# Sahte ESP32 simülasyonu (Y0s)

Robot gelmeden Pi tarafının ve güvenlik kurallarının sınanması için. Pi kodu karşısında gerçek ESP32 mi sahtesi mi olduğunu
bilmez; aynı testler ileride gerçek karta karşı da koşacak şekilde yazıldı. Günlük: `planlama/d158/Y0s-gunluk.md`.

**Dürüst sınır:** sahte ESP32, firmware 0.5.0 sözleşmesinin ve planın güvenlik kurallarının *çalıştırılabilir modeli /
şartnamesidir*. Gerçek ESP32'nin C++ kodunu (`main` dalı `kod/esp32/`) **sınamaz**. Testler geçiyor diye firmware'in doğru
olduğu söylenemez; söylenebilen, "sözleşme ve kurallar şöyle davranırsa Pi tarafı ve senaryolar tutarlı" olduğudur.

## Tek komut

- **Simülasyon + tarayıcıda görünüm:** `kod\simulasyon.bat` çift tık (ya da `py -3 kod\araclar\sahte_esp32`). Tarayıcı
  `http://127.0.0.1:8765` açılır. Tuşlar: oklar sür (Shift tam hız), **R** devreye al, **B** bırak, **X** dur, **Boşluk** acil stop
  mantarı (bas / bırak). Kapatmak: pencerede Ctrl+C. Seçenekler: `--harita oda_bos`, `--port 5760`, `--http 8765`,
  `--gorunum-yok`, `--tarayici-yok`.
- **Testler:** `py -3 kod\testler\kos.py` (58 test, ≈ 10 s; çıkış kodu 0 = hepsi geçti; 5'i güvenlik testi değil, aşağıdaki
  "tasarım bulguları"). `--liste` her testi dayandığı plan maddesiyle yazar, `-k Bekci` yalnız adında geçenleri koşar, `-v` ayrıntılı.
- **Protokol belgesi:** `kod\ortak\PROTOKOL.md` (üretilir). JSON'u değiştirince `py -3 kod\ortak\protokol_belge_uret.py`.

Bağımlılık yok: yalnız Python standart kitaplığı (3.14 ile denendi) ve `unittest`. Sanal ortam gerekmez.

## Düzen

| Yer | Ne |
| --- | --- |
| `ortak/protokol.json` | **Tek kaynak**: çerçeve, zamanlar, sınırlar, komutlar, mesajlar, hata adları, servolar. Her öğede kaynak ve `taslak` işareti |
| `ortak/robot_parametreleri.json` | Teker, iz, taban ölçüsü, enkoder, sonar yerleri…; her biri `kaynakli` ya da `TAHMIN` + kaynak |
| `ortak/lale_protokol.py` | JSON okuyucu (Python); kodla / çöz / denetle |
| `araclar/sahte_esp32/cekirdek.py` | Saf, deterministik model; zaman `adim(ms)` ile dışarıdan |
| `araclar/sahte_esp32/harita.py`, `araclar/haritalar/*.json` | 2B oda, ışın izleme, çarpışma |
| `araclar/sahte_esp32/tasima.py`, `tcp_sunucu.py` | Bellek içi taşıma (sanal saat); TCP "sanal seri hat" (gerçek zaman) |
| `araclar/sahte_esp32/gorunum.py`, `gorunum.html` | Tarayıcı görünümü (isteğe bağlı; yalnız 127.0.0.1, aynı köken) |
| `pi/lale_pi/` | İnce Pi istemcisi + taşıma arayüzü (`TcpTasima`; `SeriTasima` yer tutucu) |
| `testler/` | `duzenek.py` (hedef, ortam, hakem, odo ölçüsü), `test_guvenlik.py`, `test_sozlesme.py` (firmware ayrıntıları), `test_protokol_kaynak.py`, `test_harita.py`, `test_tcp_duman.py`, `test_gorunum.py`, `test_tasarim_bulgulari.py`, `kos.py` |

## Testler nasıl çalışır

- Senaryo testleri kartla **yalnız protokol** üzerinden konuşur (`self.esp`). Protokolün taşıyamadığı fiziksel işler
  `self.ortam`'dadır (mantara bas, kabloyu çek, I2C'yi kopar, ana anahtarı kapat, robotu bir yere koy). Asıl iddia önce
  protokolden doğrulanır: cevap / hata, güç olayı, `ping`, hız ve durma enkoder tiklerinden (`odo`). Haritadaki gerçek konum /
  hız **hakem**dir (`self.hakem_varsa()`), yalnız EK doğrulamadır ve gerçek kartta atlanır. `set LALE_HAKEM=yok` bunu sahte
  kartta prova eder (güvenlik + sözleşme testlerinin hepsi hakemsiz de geçer). (`test_harita.py`, `test_tasarim_bulgulari.py`
  modelin kendi testleridir, çekirdeğe bakar.)
- Hedef `LALE_HEDEF` ile seçilir: `bellek` (varsayılan, sanal saat), `tcp` (aynı senaryolar gerçek zamanda TCP'den, ≈ 2 dk),
  `seri:COM3` (gerçek kart; taşıma henüz yazılmadı, testler atlanır). Gerçek kartta `Ortam` adımları (mantar, kablo, konum)
  operatör uygulaması yazılana kadar "atlandı" olur.
- Plan değerleri (30 cm, 500 ms, 5 s, 600 ms) testlerde bilerek sabit yazılı: test tek kaynağı değil planı doğrular.

## Yeni harita

`kod/araclar/haritalar/<ad>.json`:

```json
{
  "ad": "koridor",
  "aciklama": "kısa açıklama",
  "boyut_m": [10.0, 3.0],
  "cevre_duvari": true,
  "duvarlar": [[4.0, 0.0, 4.0, 1.0]],
  "engeller": [{"tur": "kutu", "x": 6, "y": 1, "g": 0.5, "d": 0.5}, {"tur": "daire", "x": 8, "y": 2, "r": 0.3}],
  "baslangic": {"x": 1.0, "y": 1.5, "aci_derece": 0}
}
```

Metre; x sağa, y yukarı; `duvarlar` [x1, y1, x2, y2] parçaları; kutu sol alt köşe + genişlik `g` + derinlik `d`. Başlangıçta
robot (520 × 525 mm) hiçbir şeye değmemeli (`test_harita` denetler). Açmak: `kod\simulasyon.bat --harita koridor`.

## Yeni senaryo

`kod/testler/test_<konu>.py` içinde `LaleTesti`'nden türet; `HARITA` / `KONUM` ver. Docstring'in **ilk satırı** dayanak:
`"""Dayanak: <dosya> § <bölüm> ..."""`. Kullan: `self.devreye_al()`, `self.esp.sur_tut(v, w, ms)`, `self.esp.istek({...})`,
`self.esp.bekle(ms)`, `self.guc_olayi_bekle("ariza")`, `self.hata_bekle(cevap, "hata_adi")`, `self.ortam.mantar_bas()`,
`self.sur_olc(v, w, ms)` (odo'dan ölçülen hız), `self.enkoder_duruyor(bas, sonra_ms)`, ek doğrulama için `self.hakem_varsa()`.
Asıl iddiayı protokolden kur; yalnız hakemle doğrulanan test gerçek kartta atlanır. TASLAK bir yeteneğe dayanıyorsa başta `self.yetenek_gerek("sonar")`. Kartın gönderdiği her mesaj protokole
uymazsa test kendiliğinden kalır.

## Gerçek ESP32 gelince ne değişir

1. `kod/pi/lale_pi/tasima.py` `SeriTasima` yazılır (pyserial, DTR/RTS sırası `main` `kod/robot/seri.py`'deki gibi). Testler
   `set LALE_HEDEF=seri:COM3` ile gerçek karta koşar; mantar / kablo adımları operatör eliyle (bir `Ortam` uygulaması) yapılır,
   hakem gerektiren kontroller atlanır, zaman toleransı genişler.
2. Firmware 0.5.0'da olmayan TASLAK öğeler (sonar mesajı, 30 cm durma, bağımlı servo sınırı) ya firmware'e eklenir ya
   protokolden çıkarılır; eklenmezse ilgili testler "yetenek yok" diye atlanır. Önce Efe / Ahmet kararı.
3. `robot_parametreleri.json` içindeki TAHMİN'ler (enkoder tik / tur, teker azami hızı, sonar açısı) ölçülüp yazılır.
4. Gerçek kartla sahte kart farklı davranırsa önce `protokol.json` düzeltilir, sonra iki taraf.

## Simülasyonun gösterdiği tasarım bulguları

Bunlar modelin hatası değil, planlanan davranışın (üç ön sonar, engel varken geri ve yerinde dönüş serbest, histerezissiz hız
sınırı) sonucudur; model bunları gizleyecek biçimde değiştirilmedi. Her biri `kod/testler/test_tasarim_bulgulari.py`'de
yeniden üretilir; o testlerin **geçmesi sorunun var olduğunu** gösterir (güvenlik testi değildir, `kos.py` ayrı sayar).

- **(a) Arkada sonar yok.** Geri giderken robot duvara çarpar, `engel` gelmez, kart çarpmayı fark etmez
  (`test_a_arkada_sonar_yok_geri_giderken_duvara_carpar`).
- **(b) Engel varken yerinde dönüş.** Durma mesafesi 30 cm, taban köşesinin dönüş yarıçapı ≈ 0,37 m: duvara eğik yaklaşıp sonarla
  durduktan sonra yerinde dönünce köşe duvara çarpar (`test_b_...`).
- **(c) 30–35 cm arası sürünme.** `engel` 30 cm altında var olur, 35 cm'de kalkar (histerezis); hız sınırı ise histerezissiz
  (≥ 30 cm'de en az 0,05 m/s). Bu yüzden `engel` varken robot 30–35 cm arasında ileri sürünür, 30 cm'de yine durur (`test_c_...`).
- **(d) Ek: dar açıyla yaklaşma.** Duvara ~20°'den dar açıyla (neredeyse paralel) gidince ön sonarların ışınları yüzeye 60°'den
  eğik gelir (yankı yok, TAHMİN) ve taban köşesi ileri sürüşte duvara değer (`test_d_...`).
- **(e) İz farkı (Ç3).** Firmware komutu 0,426 m izle tekerlere çevirir, Pi odometrisi de 0,426 kullanır; CAD izi 0,432 m. Model
  ikisini ayrı tutar (`robot_parametreleri.json` `firmware_iz_genisligi_m` / `iz_genisligi_m`). Pi odometrisi 360° dönüş
  dediğinde gerçek dönüş ≈ 355° (360° başına −5,0°, %1,4; `test_e_...`). Hangisinin doğru olduğu ölçümle belirlenecek.

## Modellenmeyenler

Motor dinamiği ve gecikmesi (hız rampası ideal izlenir; bekçi ve güç bırakma *anında* sıfır hız), teker kayması (dört
tekerli kızak yönlendirme ideal diferansiyel sayılır), yük / eğim / rampa fiziği (rampa kipi yalnız elle; IMU yok), pil
deşarjı ve gerilim düşümü (akü sabit 13,1 V), sensör gürültüsü ve HC-SR04 karışması / çoklu yansıma, PID, enkoder titreşimi,
BTS IS akım arızası (`is_sol` / `is_sag`), PCA9685 / servo dinamiği ve kol mekaniği (servo yalnız hız sınırlı izler; güç
kesilince kolların düşmesi çizilmez), jest kareleri (jest yalnız 2 s "aktif" sayılır), yay çizerek dönüş kuralı (K1; 0.5.0'da
da yok), döngü bekçisi (2 s görev bekçisi), seri hat hızı / bayt kaybı, gerçek reset süresi.

## Fizik simülasyonu (Y0f)

Aynı sahte ESP32'nin (firmware modeli değişmedi) altına ikinci bir dünya: **MuJoCo 4.0.1** fiziği. Pi istemcisi ve protokol
aynı; istemci karşısında hangi dünyanın olduğunu bilmez. Teker hızı komutu firmware'deki gibi açık çevrim PWM'e
(`u = rampa_hiz / 0,39`) çevrilir, PWM DC motor modeline (durma torku, boş hız, kısa devre freni / boşta) gider; enkoder ön
tekerin fizikteki açısından, sonar MuJoCo ışın demetinden (7 x 3 ışın, yankı kuralı 2B ile aynı) gelir. Günlük:
`planlama/d158/Y0f-gunluk.md`; ölçümler: `planlama/d158/Y0f-olcum/`.

**Kurulum (bir kez).** Sanal ortam depo dışında durur (OneDrive klasörüne girmez); başka yer için `LALE_SIM_VENV`.

    py -3.14 -m venv "%LOCALAPPDATA%\lale-sim-venv"
    "%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe" -m pip install -r kod\fizik\gereksinimler.txt

Kurulum yoksa hiçbir şey bozulmaz: `py -3 kod\testler\kos.py` 58 / 58 kalır, fizik koşucusu "atlandı" der.

| Ne | Komut (`%V%` = `%LOCALAPPDATA%\lale-sim-venv\Scripts\python.exe`) | Süre |
| --- | --- | --- |
| 3B pencere | `kod\simulasyon3b.bat` (oda + rampa) ya da `kod\simulasyon3b.bat rampa_parkuru` | - |
| Fizik testleri + Y0s testleri fizikte + ölçümler | `%V% kod\fizik\kos_fizik.py` (`--olcum-yok` ile ≈ 20 s) | ≈ 3 dk |
| Yalnız ölçümler | `%V% kod\fizik\olcumler.py [--yalniz fren,rampa]` | ≈ 2,5 dk |
| Modeli CAD'den yeniden üret | `py -3 kod\fizik\model_uret.py --cad` (FreeCAD 1.1, `~/.robot-cad/run_fc.py`; CAD klasörüne yazmaz, FCStd geçici kopyadan okunur) ya da önbellekten `py -3 kod\fizik\model_uret.py` | ≈ 1 dk |
| Kol çarpışması (zarf) | `%V% kod\fizik\carpisma_denetim.py` | ≈ 10 s |

**3B pencere tuşları** (MuJoCo'nun kendi tuşlarıyla çakışmaz): Home devreye al, End dur, Yukarı / Aşağı hız ±0,1 m/s,
Sol / Sağ dönüş ±0,25 rad/s, Delete ACİL STOP mantarı bas / bırak (fiziksel düğme; sonra yeniden Home), Insert gücü bırak,
Page Up / Down kol pozu (ev, öne, öne-yukarı, yana, dirsek bükük, geri), F9 rampa kipi, F10 kafa, F11 başa koy, F12 sonraki
sahne. Kamera fareyle (sol tuş döndür, sağ tuş kaydır, tekerlek yakınlaş); F1 MuJoCo yardımı. Sol altta durum satırları
(güç, komut / ölçülen hız, eğim, teker yükleri, son olay). Sahneler `kod/fizik/sahneler/*.json` (harita + rampa / eşik).
Tuşlar yalnız pencere odaktayken gelir; B'nin ilk denemesinde F10 / F12 ulaşmadı (odak ya da sentetik tuş olayı). Sahne
değiştirmenin tuşsuz yolu komut satırı: pencereyi kapat, `kod\simulasyon3b.bat rampa_parkuru` ya da `kod\simulasyon3b.bat
oda_rampa` ile yeniden aç (ilk argüman sahne adı; `kod\fizik\sahneler\` altındaki dosya adı uzantısız).

**Düzen.** `kod/fizik/`: `cad_cikar.py` (FreeCAD: parça kütle / AM / atalet tensörü / ağ), `model_uret.py` (gövde ağacı,
eklemler, sınırlar, ağ seyreltme -> `model/lale.xml`, `model/kutle_karsilastirma.md`), `fizik_parametreleri.json` (CAD'de
olmayan her sayı, kaynağı ya da TAHMİN), `dunya.py` (MuJoCo dünyası, sahne, motor modeli, ışın), `fizik_esp32.py`
(`SahteEsp32` alt sınıfı; yalnız dünya kancaları), `olcumler.py`, `carpisma_denetim.py`, `kos_fizik.py`, `gorunum3b.py`,
`testler/test_fizik.py`. Y0s'tan değişen iki dosya: `kod/testler/duzenek.py` (`LALE_HEDEF=fizik` hedefi, `FIZIK_FARKLARI`
yardımcıları) ve `kod/testler/test_guvenlik.py` (10 testte fiziğe özgü doğrulamalar yardımcılardan geçer; 2B yolu aynı).

**Y0s testleri fizikte (58 / 58 geçer).** Test düzeyinde muafiyet yok. Fiziğin 2B ideal dünyadan bilerek farklı olduğu
yerde yalnız ilgili **doğrulama** fiziksel karşılığıyla değişir (`kod/testler/duzenek.py` `FIZIK_FARKLARI`, 6 kalem); testin
öbür doğrulamaları (bekçi tetiklenmesi, kilit, `birak` kilidi çözmez, mantar basılıyken `arm` reddi, reset, olay
iletileri, hata cevapları) fizikte de koşar ve kalırsa koşucu 1 döner. "Anında durma" yerine: sürücü girişi kesik (firmware
teker hedefi 0; bekçi / kablo = EN HIGH + PWM 0 kısa devre freni, acil stop / reset = EN LOW boşta) ve robot pay içinde
durur (fren 400 ms / 25 mm, boşta 1,3 s / 0,20 m; 0,3 m/s'den ölçülen 270 ms / 15,6 mm ve 870 ms / 0,128 m). Öbürleri: hakem
hız eşitliği 6 basamak yerine ±0,01 m/s (açık çevrim), `dur` fren yolu sınırına +5 mm, kopukken yol sınırına fren payı,
reset sonrası odo (0, 0) yerine "sıfırlandı ve kayma payından az", yay dönüşünde enkoder oranı yerine firmware'in sürücüye
verdiği hedef / PWM oranı. Hakem için fizik arka ucu sürücü girişini (`surucu`: EN, PWM, teker hedefi) verir; gerçek kartta
osiloskopla ölçülebilecek sinyaller. Bekçinin motor durdurması bozulunca (deney: `_bekci_kontrol` içinde `_motor_ani_dur`
yok) fizik koşusu da 2B ile aynı 5 testi kalır ve 1 döner (`planlama/d158/Y0f-olcum/k4-bozma.log`). Yeniden deneme yalnız
gerçek zamanlı HTTP görünüm testi `test_yalniz_ayni_koken` için (yük altında bir kez kaldı; B 56 koşuda üretemedi); öbür
her kalan koşuyu bozar. Fizik hakemi |v| < 0,1 mm/s'yi 0 yazar (duran gövdenin 1e-13 m/s titreşimi; enkoder etkilenmez,
0,1 mm/s altı sürünme hakemde görünmez).

### Fiziğin söyledikleri (ana değerler; TAHMİN parametre duyarlılıkları `planlama/d158/Y0f-olcum/olcum.md`)

- **Model = CAD.** 26.276,1 g, AM (−10,5; 0,0; 520,5) mm (ev pozu, 400 g kablo payı dahil); montaj + kablo payıyla fark
  +0,01 g, taban-analiz ev pozuyla +0,04 g / ≤ 0,04 mm; beş kol pozunun AM'si taban-analiz ile ≤ 0,05 mm. Statik aks
  yükleri ön 121,6 / arka 136,2 N (el hesabı aynı). Atalet tensörü CAD katılarından (karşılaştırılacak CAD değeri yok;
  FreeCAD'den atalet çıkarımı **bağımsız kontrol edilmedi**, B yalnız mertebeye baktı).
- **Statik devrilme eğimi** (tekerler kilitli): ileri 20,7°, geri 18,6° (el hesabı 20,6 / 18,5°, fark ≤ 0,15°); yana 25,3°.
  Yana el hesabı ile fizik ayrı geometri kullanır: taban-analiz el hesabı teker merkezinden (216 mm: atan(216 / 520,5) =
  22,5°), fizik teker silindirinin dış kenarından (216 + 29 = 245 mm: atan(245 / 520,5) = 25,2°) devriliyor; gerçek
  lastiğin yuvarlak omzu ikisinin arasında bir değer verir. Kollar öne / yukarı / geri en kötü geri 18,0° (kollar geride).
- **Durma.** `dur` (firmware fren sınırı 1,8 m/s²): tepe yavaşlama 1,77 m/s², arka aks yükü 136 -> 69 N, kalkma yok
  (fizik olarak sağlam: firmware belirler). **Bekçi ani duruşu** (PWM 0 + EN HIGH = kısa devre freni, tam hızdan) üç ayrı
  hüküm:
  (a) **Arka aks yükünü kısa süre kaybeder; gerçek ama durma torkuna bağlı (TAHMİN).** İlk an istenen yavaşlama el hesabıyla
  ≈ 4,5 m/s² > devrilme eşiği 3,68 m/s². 21 ve 15 kg·cm'de aks 0 N'a iner, 9 kg·cm'de inmez (en az 65 N; tepe 1,9 m/s²).
  (b) **Devrilme ilerleyemez (kendini sınırlar).** Arka tekerler yükünü kaybedince yalnız ön tekerler frenler: ≈ 2,5 m/s²
  < 3,68 (kollar en kötü pozda eşik 3,15, yine altında); gövde dönmez (en büyük eğim ≤ 0,011°).
  (c) **Tepe yavaşlama ve 0 N süresi ölçüm / temas ayarı ürünü; hüküm değil.** Tepe, ivmenin türetildiği pencereye bağlı:
  10 ms pencerede 2,9–3,9 m/s², 2 ms pencerede 4,2–10,7 m/s²; 0 N süresi 25–71 ms, teker kalkması 0,01–0,06 mm (temas
  batmasının altında). Aralık: ana, durma 15 kg·cm, temas solref 0,002 / 0,008 s, zaman adımı 0,5 ms (`olcum.json`
  `fren.bekci_duyarlilik`). Tasarım için cümle: 21 kg·cm motorla tam hızda bekçi duruşunda arka tekerler kısa süre yükünü
  kaybeder (sıçrar); devrilme olmaz.
  **Acil stop** (EN LOW, boşta, tam hızdan): ana parametrelerle 0,35 m/s², 0,218 m / 1,1 s. Kayma yolu TAHMİN iki parametreye
  bağlı; aralık yansıyan atalet 0 / 0,005 / 0,01 / 0,015 kg·m² x dişli sürtünmesi 0,05 / 0,2 N·m: **0,08–0,29 m**
  (0,5–1,5 s). Dişli 0,05'te 0,18 / 0,22 / 0,25 / 0,29 m; dişli 0,2'de 0,08 / 0,10 / 0,12 / 0,13 m (`fren.acil_stop_araligi`;
  0,01–0,015 benzer küçük fırçalı motorların rotor ataletinden ~1,7 kat, B'nin önerisi).
- **Rampa** (rampa kipi, sonar kuralı kapalı): 15°'ye dek çıkar (15°'de 0,19 m/s); **20°'de geri devrilir** (statik geri
  devrilme 18,6°). **`dur` sonrası rampada tutmaz, geri kayar** (mekanizma fizik olarak sağlam: kısa devre freni sıfır hızda
  tork vermez, tutma yalnız sürtünmeden; hız TAHMİN dişli geri sürülme sürtünmesine bağlı). Ölçüt `dur` anından değil, robotun
  yukarı süzülmesi (0,06–0,12 m, 0,3–0,5 s) bittiği andan: sonraki 5 s'de geri kayma ve son 2 s'nin ortalama hızı.

  | Eğim | dişli 0,05 N·m (ana) | dişli 0,2 N·m | el hesabı (0,05 / 0,2) |
  | --- | --- | --- | --- |
  | 3° | 7,7 mm/s, 5 s'de 3,8 cm | 2,5 mm/s, 1,2 cm | 7,6 / 0 mm/s |
  | 5° | 34,4 mm/s, 16,8 cm | 5,8 mm/s, 2,9 cm | 34,4 / 5,8 mm/s |
  | 10° | 101 mm/s, 48,8 cm | 72 mm/s, 34,9 cm | 101 / 72 mm/s |

  İkisinde de hiçbir eğimde tutmuyor. 3° / dişli 0,2'de el hesabı tutması gerektiğini söylüyor; fizikteki 2,5 mm/s MuJoCo eklem
  sürtünmesinin yumuşak kısıtının sınırda sızması (B: 5° / 0,25 N·m'de 4,1 mm/s): model ürünü. 5°'de tutmak için teker başı
  toplam eklem sürtünmesi ≥ 0,351 N·m gerekir (dişli ≥ 0,23 N·m). 9 kg·cm motorla 10°'yi çıkamaz. **Sonar kuralı açıkken**
  (firmware TASLAK, 30 cm'de dur) 15° ve 20° rampayı engel görüp rampanın 30 cm önünde durur; 10°'ye dek geçer (sonar ışın
  modeli ve bu bulgu **bağımsız kontrol edilmedi**).
- **Eşik** (sonar kapalı): azami hızla 30 mm'ye dek geçer, 40 mm'de ön teker çıkar ama etek (35 mm) takılır; 0,2 m/s
  komutla yalnız 5 mm (açık çevrimde düşük PWM düşük tork verir; kapalı çevrimli firmware'de değişir). 9 kg·cm motorla 5 mm.
  Sonar açıkken 40 mm eşiği engel sayıp durur (**bağımsız kontrol edilmedi**).
- **Dönüş.** Geometri fizik olarak sağlam (temas modeline duyarsız: B'nin condim, küre teker, dar silindir, impratio,
  zaman adımı varyasyonları), eşik TAHMİN µ ve durma torkuna bağlı. **Yerinde dönmemenin doğrudan nedeni motor değil
  firmware'in açık çevrim eşlemesi:** `w` girişi 1 rad/s'ye kırpılır, teker hedefi 0,213 m/s, PWM hıza orantılı
  (`u = 0,213 / 0,39 = 0,55`); durmada eldeki tork durmanın %60'ı (0,55 x 13,1 / 12). Aynı motor tam PWM'de döner:

  | Gövdenin ölçülen yerinde dönüş hızı (rad/s; 2 s sonra 1 s ortalaması) | µ 0,4 | µ 0,5 | µ 0,8 |
  | --- | --- | --- | --- |
  | 21 kg·cm, firmware (u 0,55) | 0,051 | 0,001 | 0,001 |
  | 21 kg·cm, tam PWM (u 1) | 0,30 | 0,16 | 0,12 |
  | 9 kg·cm, firmware (u 0,55) | 0,000 | 0,000 | 0,000 |
  | 9 kg·cm, tam PWM (u 1) | 0,001 | 0,001 | 0,001 |

  El hesabı (B, izotrop Coulomb, saf dönme): dönme eşiği µ 21 kg·cm firmware'de 0,40, tam PWM'de 0,79; 9 kg·cm'de 0,14 /
  0,30. Fizik ikisiyle de uyuşuyor (21 kg·cm tam PWM µ 0,8'de hâlâ döner; 9 kg·cm tam PWM µ 0,4'te dönmez). B'nin fizik
  koşusuyla fark: tam PWM µ 0,4'te B 0,17, burada 0,30 rad/s (µ 0,5 / 0,8'de 0,13 / 0,13 ile 0,16 / 0,12 yakın). Fark B'nin
  betiğinden geliyordu: firmware'i atlayıp tekerlere doğrudan tam PWM verdi, kollar ev pozunda değildi; kollar ev pozundayken
  aynı betik 0,26–0,32 veriyor (B, `planlama/d158/Y0f-kontrol.md` § 10.4). Gerçek firmware'e karşılık gelen değer 0,30–0,32;
  µ 0,4 eşiğe yakın olduğu için yük dağılımına duyarlı. Hüküm
  ("tam PWM'de µ 0,8'e dek döner") ikisinde aynı. Tam PWM'de dönüş yavaş (0,1–0,3 rad/s) ve motorlar durmaya yakın çalışır.
  Yay dönüşleri (v 1 / w 1, v 0,3 / w 0,5) µ 0,5 ve 0,8'de düz gider (el: eşdeğer yerinde tork µ eşiği ≈ 0,36). Yanal
  devrilme yok (dönemediği için). Karar seçenekleri aşağıda ("Karar isteyenler").
- **Kalkış torku** (teker başı): düz 0,46 N·m (durmanın %22'si, sürekli değerin %74'ü), 5° rampa kipinde 0,58 (%94 sürekli),
  5° kipsiz 0,81 (%131), 10° 0,93 (%150); el hesabı 0,38 / 0,56 / 0,73 / 0,91.
- **Kol.** 520 poz (iki / tek kol): devrilme ivmesi en kötü ileri 3,46 (S1 105°), geri 3,15 m/s² (S1 75°, S2 120°): firmware
  freninin 1,75–1,9 katı, bekçinin ilk an talebinden az (aritmetik B'ce doğrulandı). Kollar hızla (85°/s) sallanınca teker
  yükü 60 -> 50 N, kayma yok (dinamik kol salınımı **bağımsız kontrol edilmedi**). Kol - gövde çarpışması (parça zarfları):
  dirsek / ön kol / el / kafa temaslı poz 0 / 2.760 (her kol), kol - kol 0; zarf temasları yalnız omuz mekanizmasında (iç içe
  eş eksenli parçalar, zarf yanılgısı). Kesin tarama P10.8d'de (0 çakışma). Zarf taraması **bağımsız kontrol edilmedi**.

**Doğruluk sınırı.** Sayılar TAHMİN parametrelere bağlı (`fizik_parametreleri.json`: sürtünme, motor durma torku 21 / 9 kg·cm
iki kaynak, dişli sürtünmesi, yansıyan atalet, temas sertliği). Hiçbir sonuç "devrilmez" kesinliğinde değildir; ölçülmüş
motor ve zemin değerleriyle yeniden koşulmalı.

### Karar isteyenler (Efe / Ahmet)

Etiket: **sağlam** = fizik olarak sağlam (geometri / CAD / firmware sabiti), **TAHMİN** = TAHMİN parametreye bağlı (hangisi
yazılı). Sınıflama B'nin bağımsız kontrolüyle (`planlama/d158/Y0f-kontrol.md` § 3) aynı.

| Konu | Etiket | Ne gerekiyor |
| --- | --- | --- |
| Yerinde dönüş (firmware mi mekanik mi) | Geometri sağlam; eşik TAHMİN (µ, durma torku) | Bugünkü firmware'le µ ≥ 0,45'te dönmez. Seçenekler, öncelik sırası olmadan: firmware tarafı (dönüşte `w` tavanını yükseltmek, PWM eşlemesine ileri besleme / durma torku telafisi, enkoderle kapalı çevrim hız denetimi) ya da mekanik taraf (ön tekerleri omni / sarhoş teker yapmak, iz / dingil oranını değiştirmek). Tam güçte bile µ 0,8'de dönüş 0,12 rad/s (≈ 7 °/s; 90° için ≈ 13 s, tam tur ≈ 52 s) ve motorlar durma noktasına yakın çalışıyor: firmware düzeltmesi tek başına işe yarar bir yerinde dönüş vermez. 9 kg·cm motorla hiçbir koşulda dönmüyor. Hüküm motor durma torku ve zemin µ ölçümüne bağlı (ikisi TAHMİN) |
| Rampada `dur` sonrası tutma | Mekanizma sağlam; hız TAHMİN (dişli geri sürülme sürtünmesi) | Kısa devre freni tutmaz; 3° / 5° / 10°'de geri kayar (tablo yukarıda). Tutma ya ölçülmüş yüksek dişli sürtünmesinden (5°'de ≥ 0,23 N·m) ya da firmware'den (enkoderle konum tutma, fren / kilit) gelir |
| Bekçi duruşunun sertliği | Devrilmeme sağlam (kendini sınırlar); aks boşalması TAHMİN (durma torku) | Tam hızda ani durma arka tekerleri kısa süre kaldırır; istenmiyorsa bekçiye de fren rampası (firmware 0.5.0'da rampasız) |
| Sonar kuralı rampa ve eşiği engel sayıyor | TASLAK firmware kuralı; fizik bulgusu bağımsız kontrol edilmedi | 15° / 20° rampa ve 40 mm eşik önünde 30 cm'de durur; rampa kipinde sonar kuralı ne olacak |
| Açık çevrimde düşük hızda tork | TAHMİN (durma torku, k_V) | 0,2 m/s komutta yalnız 5 mm eşik; kapalı çevrim (PID) ya da ileri besleme kararıyla birlikte |
| Ölçülecek üç parametre | TAHMİN | Motor durma torku (21 mi 9 kg·cm mi; Ç-f3, `planlama/adim3/elektrik.md` uyarısı), zemin µ (dönüş eşiği), dişli kutusu geri sürülme sürtünmesi (rampada tutma, acil stop kayması 0,08–0,29 m) |
| Ç-f1 ad eşlemesi | Sayılara etkisi yok | Model robotun kendi çerçevesinde (`sag_*` = CAD "Sol"); `eklem_sinirlari.json` CAD adını kullanıyor. K65 § 3 eşlemesiyle kapatılmalı |

### Fizikte de modellenmeyenler

Teker lastiği esnekliği ve temas yaması (silindir - düzlem, iki temas noktası), yuvarlanma direnci yükle değişmez (sabit
Coulomb), motor endüktansı / akım sınırı / sürücü ısınması, akü gerilim düşümü (13,1 V sabit), dişli boşluğu, servo iç
dinamiği (konum eyleyicisi kp / kv TAHMİN; güçsüzken sabit sürtünme), kablo ve esnek parçalar (gövdeler katı), sarhoş teker
yok (güncel montajda yok), sensör gürültüsü, IMU (firmware'de yok). Çarpışma ilkel şekillerle (etek, gövde, kafa kutuları,
kol kapsülleri, teker silindirleri); görsel ağ CAD'den 5 mm seyreltilmiş.
