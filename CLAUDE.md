# Robot projesi — yapay zekâ oturumları için bağlam

Tekerlekli insansı robot (üniversite projesi, 4 kişilik ekip, MCBÜ Mekatronik MYO). Proje sahibi
Duffy; mekanik, montaj, kablaj ve SolidWorks'te güçlü, yazılımı yapay zekâ yardımıyla yazıyor.

- Türkçe konuş; doğrudan ol, ilk cümlede cevaba başla. Bitmiş işi tablo veya kısa listeyle özetle.
- Projenin güncel durumu: `README.md` (kararlar, CAD sonuçları, açık işler) ve `planlama/proje-plani.md`.
  Varsayımda bulunmadan önce bu dosyaları ve ilgili kaynak notunu oku.
- Yeni rapor → `raporlar/`, dayandığı araştırma → `raporlar/kaynaklar/` (kaynak URL'li; tahminleri
  "tahmini" diye işaretle). Plan değişikliği → `planlama/`. Tasarım → `tasarim/`. Yazılım kodu → `kod/`
  (aşağıdaki "Yazılım" bölümü).
- CAD: `tasarim/cad/robot_cad.py` tek kaynak; STEP, `parca-listesi.csv` ve `tasarim/Robot-Tasarim-Demosu.html`
  bu betikten üretilir, üretilmiş dosyaları elle düzenleme. Demo arayüzü `tasarim/cad/viewer-template.html`.
  Koordinat: Y yukarı, Z ileri (yüz +Z), X sağ-sol, mm. Python 3.12 + CadQuery 2.8; sanal ortam OneDrive
  dışında (`README.md`). Değişiklikten sonra betiği çalıştır, çakışma kontrolünü ve kütle/ağırlık
  merkezi çıktısını raporla.
- Maliyet: `planlama/maliyet.json` tek kaynak (TL fiyat, satıcı, bağlantı, durum, stok; USD kurdan hesaplanır).
  Değişince `tasarim/cad/demo_uret.py` çalıştır (CadQuery gerekmez). Yeni fiyatı satıcı sayfasından doğrula;
  kanıt `raporlar/kaynaklar/05-fiyat-arastirmasi.md`.
- Parça ölçüsü ekliyorsan kaynağını `raporlar/kaynaklar/04-parca-olculeri.md` ile tutarlı tut.
- Bu klasör OneDrive'da; büyük geçici dosyaları ve sanal ortamları buraya koyma.
- Proje genelde DuffyOS oturumundan yönetiliyor (Duffy'nin tercihi, 26 Eylül 2026); dosyalar buraya
  yazılıyor. Bu klasörde doğrudan açılan bir oturumda proje hafızası bu klasördeki dosyalardır.

## Yazılım (`kod/`, dal `yazilim-baslangic`, 26 Ekim 2026)

Tek Python süreci (Pi 5'te 3.11/3.12, Windows'ta 3.13). ROS yok, IK yok; jest = ESP32'de kayıtlı servo
açıları. Durum makinesi BEKLE → DİNLE → DÜŞÜN → (JEST) → KONUŞ → BEKLE. Ayrıntı: `kod/OKU_BENI.md`.
Robot SESLİ çalışır (Efe kararı, 26 Ekim 2026: ziyaretçi yazmaz, yapay zekâyla konuşur gibi konuşur): düğmesiz
`SesTetik`, Vosk, dinleme sessizlikle biter; mikrofon yoksa durur. Klavye/metin kutusu yalnız `--gelistirici`.

| Dosya | İş |
|---|---|
| `kod/ana.py` | Ayarları okur, bileşenleri kurar (`bilesenleri_kur` → `mikrofon_kur`, `sesli_modu_denetle`, `ekran_girdisini_bagla`), konuşma turu (`tek_tur`, `Kronometre` + günlük); yüz ana iş parçacığında, döngü ayrı iş parçacığında. Sesli mod kurulamazsa `SesliModKurulamadi` → çıkış kodu 2; `--gelistirici`/`--deneme-saniye` dokunma + klavyeye düşer |
| `kod/ayarlar.yaml` | Tek ayar dosyası: sağlayıcılar (varsayılan `tetik: ses`, `stt: vosk`), `algilama` (esik, sessizlik_saniye, vad_duzeyi), `dil.gecmis_tur`, içerik paketi, ekran, GPIO, seri, `gunluk` |
| `kod/robot/mikrofon.py` | `Mikrofon`: 16 kHz 30 ms parçalar, RMS eşiği + varsa webrtcvad; `konusma_bekle()` (3 parça = başladı, 300 ms ön kayıt), `konusma_parcalari()` (sessizlikte biter, sonra akış kapanır = yarım dupleks); `akis_ac` ile sahte akış; `python3 -m robot.mikrofon` eşik ölçer |
| `kod/robot/gunluk.py` | `Gunluk` (`gunlukler/YYYY-MM-DD.csv`, `;` + utf-8-sig, yazamazsa yalnız uyarı), `Kronometre`, `tur_satiri`; süre tanımları dosya başında |
| `kod/robot/durum.py` | `Durum`, `DurumMakinesi`; izinli geçişler `GECISLER` tablosu, geçersiz geçiş `GecersizGecis`, dinleyiciler `(eski, yeni)` |
| `kod/robot/icerik.py` | İçerik paketi (YAML) ve arama: `turkce_kucuk`, kök = ilk 5 harf, anahtar 3 / ortak kelime 1 puan, eşik altı None |
| `kod/robot/dil.py` | `Cevap(metin, jest, konu, puan)`; `SohbetGecmisi` (son N tur); `KuralTabanli` (içerik → kalıp → "bilmiyorum", geçmişi yalnız kaydeder; `cevap_bul` kaydetmeden); `BulutDilModeli` gemini/anthropic sohbet istemi + mesaj geçmişi, eşleşmesiz de sohbet eder, sorunla `KuralTabanli`'ye düşer |
| `kod/robot/stt.py` · `tts.py` · `tetik.py` | `dinle()`, `soyle()`, `bekle()` arayüzleri; `*_sec()` ayardan kurar, olmazsa klavye/yazıya düşer. `SesTetik`/`VoskSTT`/`GoogleSTT` ortak `Mikrofon`'u kullanır; `DokunmaTetik` ve `EkranSTT` yüzle `queue.Queue` üzerinden konuşur |
| `kod/robot/yuz.py` | pygame yüzü, `yuz_ciz()` pencere olmadan da çizer; `Yuz.dokunma_tetik`/`yazi_alici` bağlıysa alt şerit (`alt_alan`, `alanda_mi`): BEKLE'de dokunma alanı, DİNLE'de metin kutusu (yalnız geliştirici); olaylar `_olaylari_isle` (MOUSEBUTTONDOWN, FINGERDOWN, TEXTINPUT); pygame yoksa `etkin=False` |
| `kod/robot/seri.py` | ESP32'ye satır JSON (`jest`, `sur`, `dur`), hız sınırı; port boşsa `SahteSeri` |
| `kod/icerik/*.yaml` | İçerik paketleri (`universite`, `tesis`); "..." = doldurulacak bilgi |
| `kod/icerik_kontrol.py` | İçerik paketi denetleyicisi: zorunlu alan, boş/tekrarlı anahtar kelime = hata (çıkış 1), "..." satır listesi, bilinmeyen jest uyarısı (jest adları `kod/jestler/*.yaml`'dan); `--siki` |
| `kod/olcum/test_seti.py` · `test_seti_universite.txt` | STT ölçümü: tam/normalize eşleşme, KHO (Levenshtein), konu eşleşmesi, dinleme ms; `--stt --etiket --adet`; sonuç `kod/olcum/sonuclar/` (depoya girer) |
| `kod/robot.service` | systemd kullanıcı servisi: `graphical-session.target`, `DISPLAY=:0`, `ana.py --icerik universite --tam-ekran`, `Restart=on-failure` |
| `kod/tests/` | pytest; `conftest.py` `kod/`'u yola ekler ve örnek paketi verir; pygame testleri SDL `dummy` sürücüsüyle olay sentezler |
| `kod/kur_pi.sh` · `requirements.txt` | Pi kurulumu (apt + `~/robot-venv --system-site-packages`), paket listesi |

- Test: `py -3 -m pytest kod/tests -q` (depo kökünden; numpy gerekir, pygame/vosk/sounddevice/bulut olmadan da geçer).
- Çalıştırma (mikrofonsuz): `py -3 kod/ana.py --gelistirici --icerik universite` (dokun + yaz), `--yuzsuz` ile
  terminal; yüz denemesi `--yuz --deneme-saniye 3`. Pi'de `kod/` içinde `source ~/robot-venv/bin/activate &&
  python3 ana.py --icerik universite` (mikrofon + Vosk modeli gerekir). Denetim `py -3 kod/icerik_kontrol.py`,
  ölçüm `py -3 kod/olcum/test_seti.py --stt klavye --etiket deneme --adet 5`, eşik `python3 -m robot.mikrofon`.
- Tuzaklar: pygame yalnız ana iş parçacığında çalışır (`Yuz.calistir`), konuşma döngüsü arka planda;
  Pi 5'te 3,5 mm ses yok, HDMI çıkışı masaüstünden ya da `aplay -D plughw:CARD=vc4hdmi0,DEV=0` ile seçilir;
  Türkçe küçük harf için `str.lower()` değil `icerik.turkce_kucuk` (İ→i, I→ı); Pi 5 GPIO için apt'tan
  gelen gpiozero + lgpio gerekir (venv `--system-site-packages`); `kod/modeller/` ve `kod/gunlukler/` depoya
  girmez; systemd kullanıcı servisi masaüstü ortamını almaz (`DISPLAY=:0` dosyada), stdin'siz çalışır (klavye
  tetik olmaz); dokunma ekranında SDL hem FINGERDOWN hem `touch=True` fare olayı üretir, fare olayı atlanır.
- Donanımda hiçbir şey doğrulanmadı (26 Ekim 2026); doğrulama listesi `kod/OKU_BENI.md` 5. bölümde.

### ESP32 (`kod/esp32/`) ve jestler (`kod/jestler/`)

PlatformIO + Arduino (espressif32@6.9.0 = Arduino-ESP32 2.0.17, ArduinoJson 7.2.1, Adafruit PWM Servo
Driver 3.0.2; sürümler sabit). Ayrıntı ve ilk çalıştırma listesi: `kod/esp32/OKU_BENI.md`.

| Dosya | İş |
|---|---|
| `kod/esp32/include/pinler.h` | Bütün pinler tek yerde (önerilen, kablajda doğrulanacak) |
| `kod/esp32/src/main.cpp` | Güç notu; `loop()` beklemesiz, motor ve servo/jest 50 Hz, LED; `DURUM_YAYINI` 1 s durum mesajı |
| `kod/esp32/src/seri_protokol.*` | 115200 satır JSON: `jest`(ad) `sur`(v,w) `dur` `servo`(kanal,aci) `ping`; cevap `{"ok":..,"k":..}`, açılışta `{"k":"hazir"}` |
| `kod/esp32/src/servolar.*` | PCA9685 50 Hz, robot açısı → µs, sınıra kırpma, `ters`, her 20 ms `hiz*0,02` derece adım |
| `kod/esp32/src/jestler.*` | Kare oynatıcı, doğrusal ara değer, bitince `BOSTA_DURUS`; `dur`/elle `servo` jesti keser |
| `kod/esp32/src/motorlar.*` | BTS7960 LEDC 20 kHz; v (m/s), w (rad/s) → sol/sağ, rampa 0,5 m/s², enkoder kesmesi, PID katsayıları 0 (ileri besleme = açık çevrim); TAHMİNİ sabitler dosya başında |
| `kod/esp32/src/watchdog.*` | 500 ms `sur` gelmezse `motorlar_dur()`; 2 s döngü bekçisi (ESP32 reset) |
| `kod/esp32/src/jest_verisi.h` | ÜRETİLİR, elle düzenleme: `py -3 kod/jestler/jest_uret.py` |
| `kod/jestler/kanallar.yaml` | Servo tablosu TEK KAYNAK: ad → PCA9685 kanalı, min/max µs, açı sınırı, hız, ters; açı kuralı yorumda |
| `kod/jestler/{bosta,selam,isaret,evet}.yaml` | Jestler (taslak); kullanılan kanal ilk karede olmalı; `bosta` son karesi = boşta duruş |
| `kod/jestler/jest_uret.py` · `test_jest_uret.py` | YAML → başlık (sınır/sıra/hız denetimi, `--kontrol`); testler başlığın güncelliğini de denetler |

- Derleme: `py -3 -m platformio run -d kod/esp32` (yükleme `-t upload`, monitör `device monitor -d kod/esp32`).
  Jest test: `py -3 -m pytest kod/jestler -q`. YAML değişince önce `jest_uret.py`, sonra derle.
- Tuzaklar: servolar ayrı DC-DC'den (PCA9685 V+), Pi USB'sinden asla (brownout), topraklar ortak; Emas acil stop
  güç hattını keser, yazılım bekçileri onun yerine geçmez; Pi sürerken `sur`'u ~200 ms'de bir yinelemeli
  (500 ms bekçi); Pi portu açınca DevKit resetlenir, `hazir` beklenmeli; pinler/yönler/`TIK_PER_TUR`/
  `TEKER_AZAMI_HIZ`/servo sınırları tahmini, WROVER kartta GPIO 16/17 kullanılamaz.
- ESP32 tarafı derlendi (26 Ekim 2026, RAM %7, flash %23) ama donanımda denenmedi.
