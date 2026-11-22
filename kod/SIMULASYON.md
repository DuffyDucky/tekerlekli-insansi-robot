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
