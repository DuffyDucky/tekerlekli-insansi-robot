# Robot projesi — yapay zekâ oturumları için bağlam

Tekerlekli insansı robot (üniversite projesi, 4 kişilik ekip, MCBÜ Mekatronik MYO). Proje sahibi
Duffy; mekanik, montaj, kablaj ve SolidWorks'te güçlü, yazılımı yapay zekâ yardımıyla yazıyor.

- Türkçe konuş; doğrudan ol, ilk cümlede cevaba başla. Bitmiş işi tablo veya kısa listeyle özetle.
- Projenin güncel durumu: `README.md` (kararlar, CAD sonuçları, açık işler) ve `planlama/proje-plani.md`.
  Varsayımda bulunmadan önce bu dosyaları ve ilgili kaynak notunu oku.
- Mekanik/elektrik tasarımı (Ahmet/Duffy) `lale-duzeltme` dalında. Tasarım ile `kod/` arasındaki farklar ve kimin karar vereceği: `planlama/kopru-mekanik-yazilim.md`. Donanım (servo sayısı, eklem sınırı, pin, güç, acil stop) hakkında varsayımda bulunmadan önce oku; tasarım dosyalarını `git show origin/lale-duzeltme:<yol>` ile okuyabilirsin.
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
| `kod/ana.py` | Ayarları okur, bileşenleri kurar (`bilesenleri_kur` → `mikrofon_kur`, `sesli_modu_denetle`, `ekran_girdisini_bagla`, `konum_kur`), konuşma turu (`tek_tur`: bölge `konum_durumu` ile alınır, `dil.cevapla(soru, bolge=...)`, `isaret` jesti `yon` ile; `Kronometre` + günlük); `--konum <bolge>` elle bölge; yüz ana iş parçacığında, döngü ayrı iş parçacığında. Sesli mod kurulamazsa `SesliModKurulamadi` → çıkış kodu 2; `--gelistirici`/`--deneme-saniye` dokunma + klavyeye düşer |
| `kod/ayarlar.yaml` | Tek ayar dosyası: sağlayıcılar (varsayılan `tetik: ses`, `stt: vosk`), `algilama` (esik, sessizlik_saniye, vad_duzeyi), `dil.gecmis_tur`, içerik paketi, ekran, GPIO, seri, `gunluk` |
| `kod/robot/mikrofon.py` | `Mikrofon`: 16 kHz 30 ms parçalar, RMS eşiği + varsa webrtcvad; `konusma_bekle()` (3 parça = başladı, 300 ms ön kayıt), `konusma_parcalari()` (sessizlikte biter, sonra akış kapanır = yarım dupleks); `akis_ac` ile sahte akış; `python3 -m robot.mikrofon` eşik ölçer |
| `kod/robot/gunluk.py` | `Gunluk` (`gunlukler/YYYY-MM-DD.csv`, `;` + utf-8-sig, yazamazsa yalnız uyarı), `Kronometre`, `tur_satiri` (+ `bolge`, `konum_kaynak` sütunları; günün dosyası eski başlıklıysa uyarıp `_2.csv`'ye yazar); süre tanımları dosya başında |
| `kod/robot/durum.py` | `Durum`, `DurumMakinesi`; izinli geçişler `GECISLER` tablosu, geçersiz geçiş `GecersizGecis`, dinleyiciler `(eski, yeni)` |
| `kod/robot/icerik.py` | İçerik paketi (YAML) ve arama: `turkce_kucuk`, kök = ilk 5 harf, anahtar 3 / ortak kelime 1 puan, eşik altı None; yerlerde `tarifler: {bolge: metin}` ve `yon`/`yonler` (`Kayit.tarif_sec(bolge)`, `yon_sec`, `GECERLI_YONLER` = sol/sag/ileri/arka) |
| `kod/robot/dil.py` | `Cevap(metin, jest, konu, puan, yon)`; `cevapla(soru, bolge=None)` (bölge bulut istemine "Robot şu an: <bölge>" olarak gider); `VaryantSecici` (selamlama/kalıplar liste olabilir, art arda aynı yok, `{ad}/{rol}/{kurum}`), `KALIP_ADLARI`; `SohbetGecmisi` (son N tur); `KuralTabanli` (içerik → kalıp → "bilmiyorum", geçmişi yalnız kaydeder; `cevap_bul` kaydetmeden); `BulutDilModeli` gemini/anthropic sohbet istemi + mesaj geçmişi, eşleşmesiz de sohbet eder, sorunla `KuralTabanli`'ye düşer |
| `kod/robot/stt.py` · `tts.py` · `tetik.py` | `dinle()`, `soyle()`, `bekle(zaman_asimi=None)` (bool; `zaman_asimli`) arayüzleri; `Mikrofon.konusma_bekle(zaman_asimi)`; `*_sec()` ayardan kurar, olmazsa klavye/yazıya düşer. `SesTetik`/`VoskSTT`/`GoogleSTT` ortak `Mikrofon`'u kullanır; `DokunmaTetik` ve `EkranSTT` yüzle `queue.Queue` üzerinden konuşur |
| `kod/robot/yuz.py` | pygame yüzü, `yuz_ciz()` pencere olmadan da çizer; `Ifade` (bakış gezinme, 3-6 s kırpma, DÜŞÜN göz kayması, KONUŞ ağız 14 harf/s TAHMİNİ, BAKIM dişli), `bakis_hedefi(x, y)`, yazı yüzeyleri `ONBELLEK`; `Yuz.dokunma_tetik`/`yazi_alici` bağlıysa alt şerit (`alt_alan`, `alanda_mi`): BEKLE'de dokunma alanı, DİNLE'de metin kutusu (yalnız geliştirici); olaylar `_olaylari_isle` (MOUSEBUTTONDOWN, FINGERDOWN, TEXTINPUT); pygame yoksa `etkin=False` |
| `kod/robot/seri.py` | ESP32'ye satır JSON (`jest(ad, yon=None)`, `sur`, `dur`, `rampa(ac)` + `rampa_acik`), hız sınırı; `port_ac` portu DTR/RTS kapalı açar (Linux'ta ayrıca `stty -hupcl`), `SeriBaglanti.hazir_bekle` açılışta en çok 3 s `hazir` ya da ping cevabı bekler (reset olsa da olmasa da); port boşsa `SahteSeri`; gelen satırları `KonumYoneticisi` kendi iş parçacığında okur (`odo` odometriye, diğerleri yoksayılır) |
| `kod/robot/bakim.py` | `Bakim(etkin, dosya, aralik)`, `BAKIM_DOSYASI` (`kod/bakim.txt`, varlığı yeter), `BAKIM_SOZU`; ana.py `bakim_kur`/`bakim_denetle`/`bakima_gir`/`tetik_bekle`; `--bakim`, `ayarlar.yaml bakim:`; durum tablosunda BEKLE ↔ BAKIM; bakımda tek söz, mikrofon kapalı, `dur` |
| `kod/robot/uzaktan/` | Telefondan kumanda (27 Ekim 2026): `sunucu.py` `UzaktanSunucu` (stdlib ThreadingHTTPServer, 8080, PIN hmac → HttpOnly çerez, yalnız JSON POST ≤ 4 KB, Origin denetimi, yanlış PIN 1 s), `kopru.py` `RobotKoprusu` (durum/sur/dur/jest/soyle/bolge_sec/bakim/rampa; `durum()`'da `rampa`, rampa açıkken jest 409; ölü adam 400 ms, sürerken `sur` 150 ms'de bir, `SusturulanTetik` robot kendi sesini duymasın), `sahte.py`, `sayfa.html` (Rampa anahtarı: açıkken "kollar ev pozunda, yavaş" uyarısı, jest düğmeleri kapalı; `POST /rampa {ac}`) + `manifest.json`; `python3 -m robot.uzaktan` sahte robotla; ana.py `uzaktan_kur` (kurar) + `main` (portu açar/kapatır) |
| `kod/robot/konum/` | Konum paketi (27 Ekim 2026): `kaynak.py` (`KonumKaynagi`, `KonumTahmini(bolge, x, y, yon_derece, guven, zaman, kaynak)`), kaynaklar `wifi` (nmcli / Windows'ta wlanapi WlanScan + netsh, parmak izi en yakın bölge, ikinciye yakınsa güven düşer), `gps` (NMEA GGA/RMC elle ayrıştırma, haversine geofence), `ble` (bleak), `aruco` (cv2.aruco DICT_4X4_50, eski/yeni arayüz), `gorsel` (ORB + histogram özet, en yakın komşu kosinüs ≥ 0,75; `onnxruntime` + `kod/modeller/mobilenet.onnx` varsa onu kullanır; örnekler `kod/konum/gorsel_ornekler/*.npz`), `kamera` (tek kamera kilitle paylaşılır: Picamera2 ya da cv2), `odometri` (ESP32 `odo` satırları, diferansiyel ölü hesap, `duzelt`, `yaw_isareti`), `elle` (`--konum`, `kod/konum/bolge.txt` 5 s'de bir); `birlestirici.KonumYoneticisi`: arka plan iş parçacığı, puan = ağırlık × güven × tazelik, taze tahmin yoksa son bilinen bölge korunur, `durum()`; araç `python3 -m robot.konum tara|kaydet|ogret|nerede|izle|bolgeler|sifirla-odometri|isaret` |
| `kod/konum/bolgeler.yaml` · `parmak_izi.yaml` | Bölgeler (ad, açıklama, `gps` merkez/yarıçap, `isaretler` ArUco id→bölge, `beaconlar` MAC→bölge; 5 örnek, değerler "..."/null) ve Wi-Fi parmak izi veritabanı; ikisi de depoya girer, `gorsel_ornekler/`, `isaretler/`, `bolge.txt` girmez |
| `kod/icerik/*.yaml` | İçerik paketleri (`universite`, `tesis`); "..." = doldurulacak bilgi |
| `kod/icerik_kontrol.py` | İçerik paketi denetleyicisi: zorunlu alan, boş/tekrarlı anahtar kelime = hata (çıkış 1), "..." satır listesi, bilinmeyen jest uyarısı (jest adları `kod/jestler/*.yaml`'dan), geçersiz `yon` ve `tarifler` bölgesi `bolgeler.yaml`'da yoksa uyarı; `--siki` |
| `kod/olcum/test_seti.py` · `test_seti_universite.txt` | STT ölçümü: tam/normalize eşleşme, KHO (Levenshtein), konu eşleşmesi, dinleme ms; `--stt --etiket --adet`; sonuç `kod/olcum/sonuclar/` (depoya girer) |
| `kod/olcum/bilinmeyen_rapor.py` · `konum_turu.py` · `gurultu_prova.py` | Günlüklerden cevapsız/zayıf (puan < `--esik` 4) soruların kök gruplu Markdown raporu (`--gun 7`); bölge bölge gezip her kaynağın ve birleşiğin doğruluğunu CSV + Markdown'a yazan konum turu (`--etiket --adet --kaynaklar`); konuşma wav + gürültü wav'ı `--snr` dB'lerde karıştırıp Vosk ile tanıyan gürültü provası (numpy + wave; `olcum/ses/` depoya girmez) |
| `kod/robot.service` | systemd kullanıcı servisi: `graphical-session.target`, `DISPLAY=:0`, `ana.py --icerik universite --tam-ekran`, `Restart=on-failure` |
| `kod/tests/` | pytest (212); `conftest.py` `kod/`'u yola ekler ve örnek paketi verir; pygame testleri SDL `dummy` sürücüsüyle olay sentezler; `test_konum*.py` sentetik parmak izi/geofence/odometri/birleştirme, cv2 yoksa kamera testleri atlanır |
| `kod/kur_pi.sh` · `requirements.txt` | Pi kurulumu (apt + `~/robot-venv --system-site-packages`), paket listesi |
| `kod/PI5-KURULUM.md` | Gerçek Pi 5 (`lale`, **4 GB RAM**: bellek bütçesi buna göre) kurulum kaydı ve sıfırdan kurma rehberi (cloud-init dosyaları, Imager CLI, modeller, tuzaklar; "Robota takılınca güç ayarı": Pololu D36V50F5 PD konuşmaz → EEPROM `PSU_MAX_CURRENT=5000` + `config.txt` `usb_max_current_enable=1`, masada PD adaptörle gerekmez, Pi'de denenmedi); Pi'deki yol `~/tekerlekli-insansi-robot`, venv `~/robot-venv` |

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
  tetik olmaz); dokunma ekranında SDL hem FINGERDOWN hem `touch=True` fare olayı üretir, fare olayı atlanır;
  Wi-Fi taraması bağlantıyı 1-2 s kesebilir (aralık 15 s), Windows'ta `netsh` önbellek verir (wlanapi ile tarama tetiklenir), telefon hotspot'ları (yerel MAC) parmak izini bozabilir;
  görsel eşik 0,75 gerçek ortamda ayarlanmalı; robot servisi çalışırken seri port meşguldür (`nerede`/`tara` sahte seriye düşer); kamera kaynakları (`aruco.etkin`, `gorsel.etkin`) varsayılan kapalı;
  `kod/bakim.txt` varken robot bakımda (telefon da yazar); uzaktan sunucu portu `bilesenleri_kur`'da değil `main`'de açılır (testler port açmasın); köprünün seri yazımı kilitli ama `tek_tur` `seri.jest` kilitsiz (satırlar kısa); kalıp cevap varyantları paketin `kaliplar:` bölümünde, koddaki varsayılanlar tek metin.
- Pi 5'te doğrulanan (26 Ekim 2026 gecesi): kurulum, 104 test, Piper/Vosk yükleme, terminal konuşma turu; ekran, ses çıkışı, mikrofon, GPIO ve seri henüz doğrulanmadı (`kod/PI5-KURULUM.md`, `kod/OKU_BENI.md` 5. bölüm).
- Konum paketi (27 Ekim 2026) Windows'ta eduroam'da doğrulandı (tarama 7-11 BSSID, `kaydet`/`nerede`, `--konum` ile bölgeye özel tarif); Pi'de nmcli, kamera, GPS, BLE ve ESP32 odo satırları doğrulanmadı; Pi'nin apt OpenCV'sinde aruco var mı bilinmiyor.
- Diğer proje çıktıları: `planlama/kararlar-2026-10-27.md` (27 Ekim karar günlüğü: AI beyni API/RAG, hotspot, telefon kumandası), `raporlar/yz-beyni-ve-goruntu-arastirmasi-2026-10-27.md`, `raporlar/4g-modem-secenekleri-2026-10-27.md`, `raporlar/mikrofon-secimi.md` (mikrofon kararı), `tasarim/pi5-kutu/` (Pi kutusu STL + parametrik betik; vault'tan kopya, tek kaynak burası), `belgeler/tubitak-2209-b/` (başvuru taslağı docx + OKU_BENI; docx'i XML düzeyinde değil Word'de düzenle, sonra commit).

### ESP32 (`kod/esp32/`) ve jestler (`kod/jestler/`)

PlatformIO + Arduino (espressif32@6.9.0 = Arduino-ESP32 2.0.17, ArduinoJson 7.2.1, Adafruit PWM Servo
Driver 3.0.2; sürümler sabit). Ayrıntı ve ilk çalıştırma listesi: `kod/esp32/OKU_BENI.md`.

| Dosya | İş |
|---|---|
| `kod/esp32/include/pinler.h` | Bütün pinler tek yerde (önerilen, kablajda doğrulanacak) |
| `kod/esp32/src/main.cpp` | Güç notu (10 servo, hat A/B/C); `loop()` beklemesiz, motor ve servo/jest 50 Hz, LED; `DURUM_YAYINI` 1 s durum mesajı; `ODO_YAYINI` (varsayılan 1) `ODO_ARALIK_MS` (100) odometri satırı; `imu_baslat()`; `egim_denetle()` 100 ms: IMU eğimi geçerliyse `RAMPA_EGIM_AC` 3,0° / `RAMPA_EGIM_KAPAT` 1,5° histerezisle (TAHMİNİ) `rampa_imu_bildir` |
| `kod/esp32/src/seri_protokol.*` | 115200 satır JSON: `jest`(ad, isteğe bağlı `yon` sol/sag/ileri/arka; varyant varsa oynar, cevapta `yon` + `yon_uygulandi`, geçersizse `yon_gecersiz`) `sur`(v,w, isteğe bağlı `rampa` bool) `dur` `rampa`(`ac`; cevap `rampa`/`elle`/`imu`) `servo`(kanal,aci) `ping` (cevapta `odo`, `rampa`) `odo_sifirla`; cevap `{"ok":..,"k":..}`, açılışta `{"k":"hazir"}`; yayın `{"k":"odo","sol","sag","yaw","ms"}` 10 Hz sabit tamponla, `ok` alanı yok, watchdog'u etkilemez; durum yayınında `rampa`. Rampa kipi = elle ‖ IMU (`rampa_uygula`): açılınca jest kesilir + `servolar_bostaya()`, açıkken `bosta` dışı jest ve `servo` → `rampa_modunda` (sürüm 0.4.0) |
| `kod/esp32/src/imu.*` | IMU iskeleti: `imu_baslat`, `imu_var`, `imu_yaw_derece`, `imu_egim_derece` (yataydan eğim, IMU yoksa NAN); `IMU_VAR` 0 iken yaw `null`; MPU6050 0x68 / BNO055 0x28, PCA9685 ile aynı I2C (21/22) |
| `kod/esp32/src/servolar.*` | PCA9685 50 Hz, robot açısı → µs, sınıra kırpma, `ters`, her 20 ms `hiz*0,02` derece adım |
| `kod/esp32/src/jestler.*` | Kare oynatıcı, doğrusal ara değer, bitince `BOSTA_DURUS`; `dur`/elle `servo` jesti keser; `jest_baslat(ad, yon, ms, &yon_uygulandi)` + `jest_yon_indeksi`: yön varyantı yoksa varsayılan oynar |
| `kod/esp32/src/motorlar.*` | BTS7960 LEDC 20 kHz; v (m/s), w (rad/s) → sol/sağ; `rampa_adimi`: hızlanma (\|hız\| büyür) `IVME_DUZ_SURUS` 0,5, yavaşlama/fren (\|hız\| küçülür, `dur`, bekçi) `IVME_DUZ_FREN` 1,8, rampa kipinde ikisi de 0,1 m/s² (`sinirlar_verisi.h`); `motorlar_dur()` artık yalnız hedefi sıfırlar (fren sınırıyla durur, anında değil); `motorlar_rampa_modu(bool)` / `motorlar_rampa_modu_mu()`; enkoder kesmesi, PID katsayıları 0 (ileri besleme = açık çevrim); `motor_tik_sifirla()` portMUX kilitli (PID önceki tikini de sıfırlar); TAHMİNİ sabitler dosya başında, `TIK_PER_TUR`/teker çapı/iz genişliği `ayarlar.yaml konum.odometri` ile aynı olmalı |
| `kod/esp32/src/watchdog.*` | 500 ms `sur` gelmezse `motorlar_dur()`; 2 s döngü bekçisi (ESP32 reset) |
| `kod/esp32/src/jest_verisi.h` · `sinirlar_verisi.h` | ÜRETİLİR, elle düzenleme: `py -3 kod/jestler/jest_uret.py`; ikincisi `IVME_DUZ_SURUS`, `IVME_DUZ_FREN`, `IVME_RAMPA_SURUS`, `IVME_RAMPA_FREN` (float, m/s²; yalnız `motorlar.cpp` include eder) |
| `kod/ortak/eklem_sinirlari.json` | Eklem sınırları + `bagimli` kısıtı + `teker.ivme_sinir_m_s2`: TEK KAYNAK, Ahmet'in CAD betiği (`lale-duzeltme`) üretir, elle düzenleme. Eklem açısı 0 = ev pozu (S1 −45…135, S2 5…120, dirsek 0…105, bilek/pan ±90, tilt ±13). Tazele (depo kökünde): `git show origin/lale-duzeltme:kod/ortak/eklem_sinirlari.json > kod/ortak/eklem_sinirlari.json`, sonra `jest_uret.py` |
| `kod/jestler/kanallar.yaml` | Servo tablosu TEK KAYNAK (29 Ekim 2026, 10 servo): `sag_omuz` 0 (S1), `sag_omuz_yan` 1 (S2), `sag_dirsek` 2, `sag_bilek` 3, `kafa_pan` 4, `sol_*` 5-8, `kafa_tilt` 9 (0-4 hat A, 5-9 hat B, 10-12 sonar trig ayrılmış, 13-15 yedek; kol içi sıra kablajda doğrula); omuz S1/S2 DS3235 (180° sürüm; 270° tuzağı notu) hız 85 °/s, diğerleri MG996R; `eklem` + `eklem_ofset` (robot açısı = eklem + ofset: S1 45, S2 0, dirsek 0, bilek/pan/tilt 90), `min_aci`/`max_aci` YAZILMAZ (yazılırsa hata); açı kuralı yorumda; `ayna` / `ayna_aci` (kol kanalı → karşı kol, açı aynı; `kafa_pan` 180-açı); sol `ters: true` tahmini |
| `kod/jestler/{bosta,selam,isaret,evet}.yaml` | Jestler (taslak, açılar TAHMİNİ); kullanılan kanal ilk karede olmalı; `bosta` son karesi = boşta duruş = ev pozu (S1 45, S2 5, dirsek 0, bilek 90, pan/tilt 90) |
| `kod/jestler/jest_uret.py` · `test_jest_uret.py` | YAML + JSON → iki başlık (`eklem_oku`, `kanallari_oku(yol, sinirlar)` sınırı ofsetle türetir, `bagimli_kurallari` robot açısına çevirir, `_bagimli_denetle` kareleri ve aradaki doğrusal yolu 10 parçada denetler → `JestHatasi`, kanal jestte yoksa uyarı; `ivme_sinirlari` + `sinir_uret`; sıra/hız denetimi; `--kontrol` iki başlığı da denetler); `yonler:` bölümü (varsayilan / ayna / kare listesi) ile yön varyantları derleme sırasında üretilir, ayna karşılıklılık ve sınır denetimi; testler (42) |

- Derleme: `py -3 -m platformio run -d kod/esp32` (yükleme `-t upload`, monitör `device monitor -d kod/esp32`).
  Jest test: `py -3 -m pytest kod/jestler -q`. YAML ya da `kod/ortak/eklem_sinirlari.json` değişince önce
  `jest_uret.py`, sonra derle. Bu makinede pytest/platformio `py -3 -m pip install --user pytest platformio` ile kurulur.
- Tuzaklar: servolar ayrı DC-DC'lerden (PCA9685 V+; hat A sağ kol, B sol kol, C kafa), Pi USB'sinden asla (brownout),
  topraklar ortak; Emas acil stop güç hattını keser, yazılım bekçileri onun yerine geçmez (acil stopta motorlar boşa
  düşer, ivme sınırı işlemez); Pi sürerken `sur`'u ~200 ms'de bir yinelemeli (500 ms bekçi); `dur` artık anında değil
  (düzde ~0,2 s, rampa kipinde ~4 s); Pi portu DTR/RTS kapalı açar ama reset yine olabilir, `seri.py` `hazir` ya da
  ping bekler; pinler/yönler/`TIK_PER_TUR`/`TEKER_AZAMI_HIZ`/ofsetler/sol `ters` tahmini, WROVER kartta GPIO 16/17
  kullanılamaz; elle `servo` komutu `bagimli` kısıtını denetlemez (yalnız jestler üretimde denetlenir).
- Bu turun DIŞINDA kalan köprü farkları (karar bekliyor, kodda yok): F4/F6 acil stop rölesi ve pinleri, F7 sonar ve akü
  izleme, F9 akım ölçer, F11 gamepad; F8'deki "yerinde dönüş yok, yay çizerek dönüş" uygulanmadı (açık soru).
- ESP32 0.3.0 derlendi (27 Ekim 2026, RAM %7, flash %23,1, `-Wall` uyarısız; `-DODO_YAYINI=0 -DIMU_VAR=1` ile de). 0.4.0 (29 Ekim 2026, dal `donanim-uyum-2026-10-29`) derlendi: RAM %7,0 (22904 B), flash %23,2 (304601 B), `-Wall` uyarısız; `-DODO_YAYINI=0 -DIMU_VAR=1` ile de (yalnız bilinçli IMU `#warning`). Hiçbiri donanımda denenmedi. Odo açıkken seri monitör kalabalıktır (elle denerken `-DODO_YAYINI=0`); Pi tarafı komut cevabı beklerken `odo` satırlarını ayıklamalı. Yönlü `isaret` (açılar TAHMİNİ): sag = sağ kol yana-öne (S1 70, S2 80) + pan 70, sol = aynası (kanallar 5-8, kablajda doğrula), ileri = iki kol öne yatay (S1 135) S2 10 + kafa düz, arka = S1 10 (geriye) + S2 40 + pan 45; eski "omuz üstünden 150" kalktı. Gerçek servoda açılar, ofsetler ve elin gövdeye çarpması doğrulanmadı.
