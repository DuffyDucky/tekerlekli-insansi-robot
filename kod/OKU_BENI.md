# Robot yazılımı: başlangıç paketi

Tek Python süreci. Durum makinesi BEKLE → DİNLE → DÜŞÜN → (JEST) → KONUŞ → BEKLE döner.
Robot **sesli** çalışır, karşınızda bir yapay zekâ varmış gibi konuşursunuz: düğme yok, mikrofon konuşma
başlayınca dinlemeye geçer (`SesTetik`), dinleme 0,8 sn sessizlikle biter, Vosk tanır, robot cevaplar.
Robot konuşurken mikrofon kapalıdır (yarım dupleks). Mikrofon ya da Vosk modeli yoksa robot açık bir
mesajla durur. Mikrofonsuz deneme için **`--gelistirici`**: ekrana dokun (ya da Enter), soruyu ekrandaki
kutuya (ya da terminale) yaz; bu yalnız geliştirici aracıdır, ziyaretçi robota bir şey yazmaz.
Her tur `gunlukler/YYYY-MM-DD.csv` dosyasına bir satır olarak yazılır (ölçüm için). Robot bulunduğu
bölgeyi birden çok kaynaktan bulur ve yer tarifini/işaret yönünü ona göre seçer (9. bölüm). `kod/bakim.txt`
varken robot bakımdadır (10. bölüm); ölçüm araçları 11., yüz ifadeleri 12. bölümde.

| Dosya | İş |
|---|---|
| `ana.py` | Ayarları okur, parçaları kurar, sesli mod denetimi, konuşma döngüsü (`tek_tur`) |
| `ayarlar.yaml` | Tüm seçimler (sağlayıcılar, algılama eşiği, içerik paketi, ekran, GPIO pini, seri port) |
| `robot/durum.py` | Durum makinesi; izinli geçişler `GECISLER` tablosunda (BEKLE ↔ BAKIM dahil) |
| `robot/bakim.py` | Bakım modu: `--bakim`, `bakim.etkin` ya da `bakim.txt` dosyası (10. bölüm) |
| `robot/mikrofon.py` | Ortak mikrofon: 30 ms parçalar, RMS eşiği (+ varsa webrtcvad), konuşma başı/sonu algılama |
| `robot/tetik.py` | Konuşma tetiği: `SesTetik` (varsayılan, düğmesiz), `DokunmaTetik` (ekran), `GpioTetik` (düğme), `KlavyeTetik` |
| `robot/stt.py` | Konuşma tanıma: `VoskSTT` (varsayılan), `GoogleSTT`; geliştirici: `KlavyeSTT`, `EkranSTT` (metin kutusu) |
| `robot/icerik.py` | İçerik paketi okuma ve kelime eşlemeli arama |
| `robot/dil.py` | Cevap üretici: `KuralTabanli` (varsayılan), `BulutDilModeli` (gemini / anthropic); `SohbetGecmisi` (son 6 tur) |
| `robot/tts.py` | Seslendirme: `YaziTTS` (varsayılan), `Pyttsx3TTS`, `PiperTTS` |
| `robot/yuz.py` | pygame yüzü (ilkel şekiller), altta son söylenen metin; dokunma tetiğinde "Konuşmak için dokun" alanı; ifadeler ve bakış `Ifade` (12. bölüm) |
| `robot/gunluk.py` | Etkileşim günlüğü: her tur bir CSV satırı (tanınan, konu, puan, cevap, jest, süreler) |
| `robot/seri.py` | ESP32'ye satır tabanlı JSON (`jest(ad, yon)`, `sur`, `dur`, `rampa(ac)`); portu DTR/RTS kapalı açar, açılışta `hazir` ya da ping cevabı bekler; port yoksa `SahteSeri` |
| `robot/konum/` | Konum: Wi-Fi, GPS, BLE, ArUco, görsel, odometri, elle kaynakları + `KonumYoneticisi`; `python3 -m robot.konum` aracı (9. bölüm) |
| `robot/uzaktan/` | Telefondan kumanda: web sunucusu (`sunucu.py`), robota güvenli erişim (`kopru.py`), telefon sayfası (`sayfa.html`, `manifest.json`); `python3 -m robot.uzaktan` robotsuz deneme (10. bölüm) |
| `konum/bolgeler.yaml`, `konum/parmak_izi.yaml` | Bölge haritası (GPS çemberi, ArUco, beacon) ve Wi-Fi parmak izi kaydı |
| `icerik/universite.yaml`, `icerik/tesis.yaml` | Örnek içerik paketleri ("..." yerleri doldurulacak) |
| `icerik_kontrol.py` | İçerik paketi denetleyicisi: zorunlu alanlar, boş/tekrarlı anahtar kelime, "..." listesi |
| `olcum/test_seti.py`, `olcum/test_seti_universite.txt` | STT test seti ölçümü (tanıma oranı, kelime hata oranı, süre) |
| `olcum/bilinmeyen_rapor.py`, `konum_turu.py`, `gurultu_prova.py` | Cevapsız soru raporu, konum doğruluk turu, SNR × tanıma provası (11. bölüm) |
| `robot.service` | Pi'de otomatik başlatma (systemd kullanıcı servisi) |
| `tests/` | pytest testleri |

## 1. Windows'ta çalıştırma (mikrofonsuz geliştirici denemesi)

Depo kökünde (PowerShell):

```powershell
py -3 -m pip install pyyaml pytest pygame numpy
py -3 -m pytest kod/tests -q                                  # testler
py -3 kod/ana.py --gelistirici --icerik universite            # yüz: dokun + ekrana yaz
py -3 kod/ana.py --gelistirici --yuzsuz --icerik universite   # yalnız terminal: Enter + yaz
py -3 kod/ana.py --yuz --deneme-saniye 3                      # yüz tüm ifadeleri gösterip 3 sn'de kapanır
py -3 kod/icerik_kontrol.py                                   # içerik paketlerini denetle
```

`--gelistirici` olmadan (`py -3 kod/ana.py`) mikrofon/Vosk yoksa robot "Kurulamadı: ... Mikrofonsuz
denemek için: --gelistirici" yazıp çıkış kodu 2 ile kapanır; bu beklenen davranış.

Geliştirici modunda (yüz açık): yüzün altındaki **Konuşmak için dokun** alanına tıkla/dokun; alan metin
kutusuna döner, soruyu yaz (ı, ğ, ş, İ çalışır; Backspace siler), Enter gönderir. Boş Enter "soru yok"
sayılır. Cevap ekranda ve terminalde `Robot: ...` diye görünür; jest varsa `[seri] {"k":"jest",...}`
satırı çıkar. Robot konuşurken yapılan dokunmalar sayılmaz. Çıkış: ESC ya da pencereyi kapat (`--yuzsuz`
ile Ctrl+C). Bilgisayarda mikrofon ve Vosk varsa `--gelistirici` olmadan da sesli çalışır.

Komut satırı seçenekleri ayar dosyasını ezer: `--icerik universite|tesis|dosya.yaml`, `--yuz/--yuzsuz`,
`--tam-ekran`, `--gelistirici`, `--tetik ses|dokunma|gpio|klavye`, `--saglayici kural|gemini|anthropic`,
`--stt vosk|google|klavye`, `--tts yazi|pyttsx3|piper`, `--ayar baska.yaml`, `--deneme-saniye N`
(deneme modu mikrofon istemez).

## 2. Pi'de bu akşam adım adım

Raspberry Pi OS Bookworm (64 bit, masaüstü), 10,1" dokunmatik ekran HDMI'da (dokunma için ekranın USB
kablosu da Pi'ye takılı). Bu akşam mikrofon ve hoparlör yok: robot **geliştirici modunda** denenir
(dokun + USB klavyeyle yaz). Komutları Pi'nin kendi ekranındaki terminalde çalıştırın (SSH'tan açılan
pygame penceresi ekrana gelmez).

1. Depoyu al: `git clone https://github.com/DuffyDucky/tekerlekli-insansi-robot.git`
   → `cd tekerlekli-insansi-robot && git checkout yazilim-baslangic && cd kod`
2. Kur: `bash kur_pi.sh` (apt paketleri, `~/robot-venv` sanal ortamı, pyttsx3, pyserial, sounddevice, vosk)
3. Ortamı aç: `source ~/robot-venv/bin/activate`, sonra testler: `python3 -m pytest tests -q`
4. Normal modu dene: `python3 ana.py` → mikrofon yok, "Kurulamadı ... --gelistirici" yazıp kapanmalı.
5. Yüzle dene: `python3 ana.py --gelistirici --icerik universite --tam-ekran` → "Konuşmak için dokun"a
   parmakla dokun, kutuya "Kantin nerede?" yaz, Enter. 3-4 soru sor, ESC ile çık. Sonra günlüğe bak:
   `cat gunlukler/$(date +%F).csv` (her soru bir satır, süreler ms).
6. İçerik: `python3 icerik_kontrol.py universite` (hata 0 olmalı; "..." satırları doldurulacaklar listesi)
7. Ölçüm denemesi (mikrofonsuz): `python3 olcum/test_seti.py --stt klavye --etiket pi-deneme --adet 5`
8. Ses (HDMI hoparlör varsa): `espeak-ng -v tr "Merhaba, ben robot"` (aşağıdaki HDMI notu); ses geliyorsa
   `ayarlar.yaml` → `tts.saglayici: pyttsx3`, tekrar çalıştır.

**Mikrofon gelince (sesli mod):** USB mikrofonu tak; Vosk Türkçe modelini indir (`kur_pi.sh` içindeki yorumlu
`wget` satırı, `modeller/` klasörüne). Eşik için `python3 -m robot.mikrofon` (10 sn: önce sessiz dur, sonra
konuş; sessizdeki ve konuşmadaki sayının arasını `algilama.esik` yap). Sonra `--gelistirici` olmadan:
`python3 ana.py --icerik universite --tam-ekran`, robota doğrudan konuş. Ayarlarda `tetik.saglayici: ses`
ve `stt.saglayici: vosk` (varsayılan zaten bu).

**HDMI ses:** Pi 5'te 3,5 mm ses çıkışı yok; ses HDMI'dan (ekranın hoparlörü ya da kulaklık çıkışı
varsa) veya USB ses kartından gelir. Masaüstünde sağ üstteki ses simgesine sağ tıklayıp çıkışı HDMI
seçin. Kartları görmek için `aplay -l`; deneme için
`speaker-test -c2 -t wav -D plughw:CARD=vc4hdmi0,DEV=0` (kart adı `aplay -l` çıktısına göre değişir).
Piper kullanılırsa aynı değeri `tts.ses_cihazi` alanına yazın.

## 3. `ayarlar.yaml` alanları

| Alan | Değerler | Not |
|---|---|---|
| `robot.ad` | metin | Robotun adı (henüz konmadı) |
| `icerik.paket` | `universite`, `tesis`, `.yaml` yolu | `icerik/` klasöründen okunur |
| `icerik.esik` | sayı (3) | Eşleşme puanı bunun altındaysa "bilmiyorum"; anahtar kelime 3, ortak kelime 1 puan |
| `dil.saglayici` | `kural`, `gemini`, `anthropic` | Bulut çalışmazsa kendiliğinden `kural` |
| `dil.gemini_model`, `dil.anthropic_model` | model adı | Varsayılan `gemini-flash-latest`, `claude-haiku-5-5` |
| `dil.gecmis_tur` | sayı (6) | Sohbet hafızası: bulut modeline giden son soru-cevap sayısı |
| `stt.saglayici` | `vosk`, `google`, `klavye` | Varsayılan `vosk`; `klavye` yalnız geliştirici denemesi |
| `stt.vosk_model`, `stt.azami_saniye`, `stt.mikrofon` | yol, saniye, cihaz | `mikrofon` boş = varsayılan giriş |
| `algilama.esik` | RMS (500) | Konuşma sayılan en düşük ses düzeyi; gürültüde büyüt (`python3 -m robot.mikrofon`) |
| `algilama.sessizlik_saniye` | saniye (0.8) | Konuşmadan sonra bu kadar sessizlik olunca dinleme biter |
| `algilama.vad_duzeyi` | 0-3 (2), -1 | `webrtcvad` kuruluysa insan sesi denetimi; -1 = yalnız RMS |
| `tts.saglayici` | `yazi`, `pyttsx3`, `piper` | |
| `tts.hiz`, `tts.piper_komut`, `tts.piper_model`, `tts.ses_cihazi` | | `ses_cihazi` aplay `-D` değeri |
| `yuz.etkin`, `yuz.genislik`, `yuz.yukseklik`, `yuz.tam_ekran` | | 10,1": 1280×800; Pi'de `tam_ekran: true` ya da `--tam-ekran` |
| `tetik.saglayici`, `tetik.gpio_pin` | `ses`/`dokunma`/`gpio`/`klavye`, BCM no (17) | Varsayılan `ses` (düğmesiz). `dokunma` yüz kapalıysa Enter'a düşer. Düğme GPIO17 (fiziksel pin 11) ile GND arası |
| `seri.port`, `seri.hiz` | boş / `/dev/ttyUSB0`, 115200 | Boşsa sahte seri |
| `jest.sure` | saniye | Jestten sonra konuşmaya geçmeden bekleme |
| `gunluk.etkin`, `gunluk.klasor` | `true`/`false`, klasör (`gunlukler`) | Etkileşim günlüğü; klasör depoya girmez |
| `konum.*` | 9. bölüm | Konum kaynakları, ağırlıklar, tazelik, son bilinen bölge; `--konum <bolge>` elle verir |
| `bakim.etkin`, `bakim.dosya`, `bakim.aralik_saniye` | `false`, `bakim.txt`, 1.0 | Bakım modu (10. bölüm); `--bakim` = `etkin: true` |

Sesli mod (ses tetiği, Vosk/Google) kurulamazsa robot durur (çıkış kodu 2); `--gelistirici` ile dokunma/Enter
ve klavyeye düşer. Diğer eksikler (TTS, bulut, seri, GPIO) programı durdurmaz: neden yazılır ve varsayılana
(yazı, kural, sahte seri) düşülür. Açılıştaki `[ana] ...` satırı hangi parçanın gerçekten kurulduğunu gösterir.

## 4. Sağlayıcı değiştirme (bulut dil modeli, sohbet)

```bash
pip install google-genai            # ya da: pip install anthropic
export GEMINI_API_KEY=...           # ya da: export ANTHROPIC_API_KEY=...
python3 ana.py --saglayici gemini   # ya da ayarlar.yaml → dil.saglayici: gemini
```

Windows PowerShell'de: `$env:GEMINI_API_KEY="..."`. Anahtarı koda ve depoya yazmayın. Bulut modeli
sohbet eden bir karşılama robotu gibi davranır: sistem istemi "Türkçe, sıcak, en fazla 1-2 kısa cümle,
sesli okunacak; kurumla ilgili sorularda içerik paketine dayan, olmayan olguyu uydurma, görevliye yönlendir;
gündelik sohbete devam et". İsteme içerik paketinden bu soruya en uygun 3 bilgi ve konu başlıkları eklenir;
son 6 soru-cevap (`dil.gecmis_tur`) mesaj geçmişi olarak gider, böylece "peki orası kaçta açılıyor?" gibi
devam soruları anlaşılır. İçerik eşleşmesi olmasa da sohbete devam eder (kural tabanlı "bilmiyorum" derdi).
Anahtar ya da paket yoksa, ya da internet giderse robot kural tabanlı cevaba düşer. Bulut çağrısı yalnız sahte
istemciyle test edildi; gerçek anahtarla ilk denemede model adını kontrol edin.

## 5. Bu gece doğrulanacaklar (Pi'de)

- [ ] `kur_pi.sh` hatasız bitiyor mu (sounddevice/vosk dahil); `python3 -m pytest tests -q` yeşil mi
- [ ] `python3 ana.py` mikrofonsuz açık mesajla kapanıyor mu (çıkış kodu 2: `echo $?`)
- [ ] Yüz tam ekran mı, 1280×800 ekrana oturuyor mu, ESC ile çıkılıyor mu (Wayland masaüstünde)
- [ ] `--gelistirici`: "Konuşmak için dokun" alanı parmakla dokununca tepki veriyor mu (bir dokunma = bir tur)
- [ ] `--gelistirici`: metin kutusuna USB klavyeyle ı, ğ, ş, ç, ö, ü, İ yazılıyor mu; Backspace ve Enter çalışıyor mu
- [ ] `gunlukler/` altında günün CSV'si oluşuyor mu, satır sayısı soru sayısına eşit mi
- [ ] `robot.service` açılışta yüzü tam ekran getiriyor mu (7. bölüm; mikrofon yoksa servis 5 sn'de bir yeniden dener)
- [ ] Türkçe karakterler (ı, ğ, ş, İ) alt satırda doğru görünüyor mu
- [ ] HDMI ses geliyor mu (`speaker-test`, `espeak-ng -v tr "deneme"`)
- [ ] pyttsx3 Türkçe ses buluyor mu (açılışta "Türkçe ses bulunamadı" uyarısı çıkıyor mu); çıkıyorsa
      ya da ses kötüyse Piper'ı kur (`kur_pi.sh` içindeki yorumlu komutlar), `tts.saglayici: piper`
- [ ] Piper komutunun seçenekleri (`--model`, `--output_file`) kurulan sürümle uyuşuyor mu
- [ ] Cevaplarda "..." geçen yerler: içerik paketini gerçek bilgiyle doldur (TTS "..."yı garip okur)

Mikrofon gelince ayrıca: konuşma başlayınca DİNLE'ye geçiyor mu, ilk kelime kesiliyor mu, 0,8 sn
sessizlikte dinleme bitiyor mu, robot konuşurken kendi sesiyle tetiklenmiyor mu, gürültüde eşik yeterli mi.

## 6. Ölçüm: etkileşim günlüğü ve STT test seti (TÜBİTAK 2209-B)

**Etkileşim günlüğü** (`robot/gunluk.py`): her tur `gunlukler/YYYY-MM-DD.csv` dosyasına bir satır.
Sütunlar: `zaman; tetik; stt; taninan; dil; konu; puan; cevap; jest; dinleme_ms; dusunme_ms;
seslendirme_ms; uctan_uca_ms; bolge; konum_kaynak` (son ikisi 27 Ekim 2026'da eklendi; günün dosyası eski
başlıkla açılmışsa yeni satırlar `YYYY-MM-DD_2.csv`'ye gider). Ayraç `;`, kodlama UTF-8 (BOM'lu): Türkçe Excel'de çift tıklayınca sütunlara
ayrılır; Python'da `pandas.read_csv(yol, sep=";")`. Süreler: dinleme = `stt.dinle()` (ses tetiğinde konuşmanın
başından sessizlik bitene kadar, tanıma dahil), düşünme = `dil.cevapla()`, seslendirme = `tts.soyle()` (Piper'da
ses üretme + çalma), uçtan uca = tetikten (konuşma başı) seslendirmenin bitişine kadar tüm tur. Duyulamayan soru
da (boş `taninan`) satır olarak yazılır; komut tanıma oranı için gerekir. `konu` boşsa robot "bilmiyorum"
demiştir (ya da bulut eşleşmesiz sohbet etmiştir); `kalıp:...` selam/teşekkür gibi kalıplardır.

**STT test seti** (`olcum/test_seti.py`): setteki her cümleyi ekrana yazar, kullanıcı söyler, seçilen STT dinler
(robotla aynı mikrofon ve `algilama` ayarları; dinleme sessizlikle biter).

```bash
python3 olcum/test_seti.py --stt vosk --etiket lab-45dB          # Pi, mikrofonla (her cümleden önce Enter)
py -3 kod/olcum/test_seti.py --stt klavye --etiket deneme --adet 5 # Windows, mikrofonsuz (yazarak)
```

Ölçülenler: tam eşleşme (harfi harfine), normalize eşleşme (küçük harf, noktalamasız), kelime hata oranı
(KHO/WER, Levenshtein: değiştirilen + silinen + eklenen kelime / doğru cümledeki kelime), konu (niyet)
eşleşmesi (tanınan cümle robotu doğru konuya götürüyor mu) ve dinleme süresi (ort/medyan/en fazla). Özet
ekrana ve `olcum/sonuclar/YYYY-MM-DD_HHMM_<stt>_<etiket>.csv` dosyasına yazılır (cümle satırları, boş satır,
özet). Ctrl+C ölçümü erken bitirir, o ana kadarki sonuçlar kaydedilir. Seçenekler: `--set dosya.txt`,
`--icerik`, `--adet N`, `--sonuc-klasoru`. Ortamı etikete yazın (ör. ses ölçerle okunan gürültü:
`lab-45dB`, `koridor-65dB`); aynı seti her ortamda aynı kişiyle tekrarlayın. Dinleme süresi konuşma süresini
de içerir; saf tanıma gecikmesi değildir. Mikrofon/Vosk kurulamazsa betik klavyeye düşer ve dosya adında
`klavye` yazar.

Test seti `olcum/test_seti_universite.txt` örnek 36 cümle; Efe 100'e tamamlayacak (her satır bir cümle,
`#` açıklama). Yeni cümle robotun bildiği bir konuya gitmeli: `tests/test_olcum.py` bunu denetler.

## 7. Pi'de otomatik başlatma (systemd kullanıcı servisi)

`robot.service` masaüstü oturumu açılınca robotu tam ekran, sesli modda başlatır. Pi masaüstüne otomatik
giriş açık olmalı (`sudo raspi-config` → System Options → Boot / Auto Login → Desktop Autologin). Servis
dosyasındaki yollar depo `~/tekerlekli-insansi-robot`, sanal ortam `~/robot-venv` varsayar; farklıysa düzeltin.

```bash
mkdir -p ~/.config/systemd/user
cp ~/tekerlekli-insansi-robot/kod/robot.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now robot.service   # şimdi başlat + her açılışta başlat
systemctl --user status robot                 # çalışıyor mu
journalctl --user -u robot -f                 # canlı log (Ctrl+C ile log'dan çıkılır, robot durmaz)
systemctl --user restart robot                # kod/ayar değişince
systemctl --user stop robot                   # durdur (ESC ile çıkmak da durdurur; yeniden açılmaz)
systemctl --user disable robot                # açılışta başlamasın
```

Mikrofon takılı değilse robot "Kurulamadı" yazıp kod 2 ile kapanır, servis 5 sn'de bir yeniden dener;
mikrofon takılınca kendiliğinden açılır (log'da tekrar eden satırlar bu yüzdendir). Bu akşam mikrofonsuz
servis denemek isterseniz `ExecStart` satırının sonuna geçici olarak `--gelistirici` ekleyin.

**Ekran (DISPLAY/WAYLAND) notu:** systemd kullanıcı servisleri masaüstünün ortam değişkenlerini kendiliğinden
almaz; servis `DISPLAY=:0` ile açar (Bookworm'un Wayland masaüstünde pygame Xwayland üzerinden çizer). Pi'nin
kendi terminalinde `echo $DISPLAY $WAYLAND_DISPLAY` çıktısı farklıysa servis dosyasındaki değeri değiştirin;
pencere hiç açılmazsa dosyadaki yorumlu `WAYLAND_DISPLAY` ve `SDL_VIDEODRIVER=wayland` satırlarını açın.
Servis açılışta başlamıyorsa `systemctl --user is-active graphical-session.target` bakın; `inactive` ise
oturum bu hedefi kurmuyor demektir: `~/.config/labwc/autostart` dosyasına (Wayfire'da `~/.config/wayfire.ini`
→ `[autostart]`) `systemctl --user start robot.service` satırını ekleyin. Servis stdin'siz çalışır; bu yüzden
tetik `ses`, `dokunma` ya da `gpio` olmalı, `klavye` tetikle hemen kapanır.

## 8. Sonraki adımlar

- **Mikrofon gelince:** 2. bölümdeki "Mikrofon gelince" adımları. Mikrofonun adı/numarası için
  `python3 -c "import sounddevice; print(sounddevice.query_devices())"`, gerekirse `stt.mikrofon` alanına yaz.
  Gürültülü ortamda `pip install webrtcvad-wheels` (insan sesi denetimi) ve `algilama.esik` ayarı.
- **Düğme gelince (isteğe bağlı):** GPIO17 ile GND arasına bağla, `tetik.saglayici: gpio`.
- **ESP32 gelince:** ESP32 tarafı aynı JSON satırlarını okuyacak (`robot/seri.py` başındaki komut
  listesi) ve 500 ms komut gelmezse motorları durduracak (watchdog). `seri.port: /dev/ttyUSB0`
  (ya da `/dev/ttyACM0`; `ls /dev/tty*` ile bak). Kullanıcı `dialout` grubunda olmalı:
  `sudo usermod -aG dialout $USER` ve yeniden oturum aç. Port açılınca ESP32 resetlenmesin diye `seri.py`
  DTR/RTS kapalı açar; Pi'de bir kez `stty -F /dev/ttyUSB0 -hupcl` (29 Ekim 2026, denenmedi).
  Robota takılınca Pi güç ayarı: `kod/PI5-KURULUM.md` "Robota takılınca güç ayarı".
- **Bulut:** anahtar alınca `dil.saglayici: gemini` ya da `anthropic` (sohbet hafızası bulutta işe yarar).
- **Durum doğrulaması:** hiçbir şey donanımda denenmedi; yukarıdaki listeyi bu akşam işaretleyin.

## 9. Konum ve yön tarifi (`robot/konum/`)

Robot bulunduğu **bölgeyi** (giriş holü, kantin önü...) birden çok kaynaktan birleştirerek bulur; yer
sorulunca o bölgeye özel tarifi söyler ve işaret jestini doğru yöne yapar (`{"k":"jest","ad":"isaret","yon":"sol"}`).
Bölge bilinmiyorsa genel tarif ve yönsüz işaret (eski davranış). Hedef doğruluk **bölge düzeyi (3-10 m)**;
metre altı konum değil. Her tur günlüğe `bolge` ve `konum_kaynak` sütunlarıyla yazılır.

| Kaynak | Dosya | Ne verir | Gereken | Yoksa |
|---|---|---|---|---|
| Elle | `elle.py` | `--konum <bolge>` ya da `konum/bolge.txt` (5 s'de bir okunur); güven 1, eskimez | - | - |
| Wi-Fi parmak izi | `wifi.py` | Bölge (kayıtlı ölçümlere en yakın) | `nmcli` (Pi OS'te hazır), Windows'ta `netsh` | kayıt yoksa sessiz |
| GPS | `gps.py` | Bölge (GPS çemberi), HDOP'a göre güven | NMEA seri modül + `pyserial` | `port` boşsa pasif |
| BLE beacon | `ble.py` | En güçlü RSSI'li beacon'un bölgesi | `bleak` + beaconlar | pasif |
| ArUco işareti | `aruco.py` | Bölge + isteğe bağlı x, y, yön | OpenCV (aruco), kamera | pasif |
| Görsel tanıma | `gorsel.py` | Öğretilmiş karelere en benzer bölge | OpenCV, kamera; isteğe bağlı `onnxruntime` | pasif |
| Odometri | `odometri.py` | x, y, yön (bölge değil) | ESP32 `{"k":"odo",...}` satırları (`seri.port`) | sessiz |

Birleştirme (`birlestirici.py`, `KonumYoneticisi`): puan = ağırlık × güven × tazelik (yaş/`tazelik_saniye` ile
doğrusal azalır); aynı bölgeyi söyleyenlerin puanı toplanır, en yüksek bölge seçilir. Hiç taze tahmin yoksa
**son bilinen bölge korunur** (robot hiçbir koşulda durmaz). ArUco işaretinde x/y varsa odometri oraya
düzeltilir, yoksa GPS (bölge merkezi `yerel` doluysa). Kalman/parçacık filtresi sonraki aşama.
Her kaynak kendi iş parçacığında okunur; biri hata verirse yalnız o tur atlanır, kütüphanesi yoksa açık
mesajla pasif olur (açılışta `[konum] etkin: ... | pasif: ...`).

**Kurulum (Pi):** `gpsd` GEREKMEZ (NMEA satırları kodda ayrıştırılır).

```bash
sudo apt install python3-opencv            # ArUco + görsel; aruco var mı: python3 -c 'import cv2; cv2.aruco'; yoksa:
~/robot-venv/bin/pip install opencv-contrib-python-headless
~/robot-venv/bin/pip install bleak pyserial # BLE beacon, GPS/ESP32 seri
sudo apt install python3-picamera2          # CSI kamera (çoğu Pi OS'te hazır); USB kamerada gerekmez
# İsteğe bağlı daha iyi görsel özet (~14 MB, depoya girmez):
~/robot-venv/bin/pip install onnxruntime
wget -O modeller/mobilenet.onnx https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-12.onnx
```

**Komut satırı aracı** (`kod/` klasöründen; Windows'ta `py -3 -m robot.konum ...`):

```bash
python3 -m robot.konum bolgeler                 # bölgeler + her bölgede kaç Wi-Fi ölçümü / görsel örnek var
python3 -m robot.konum tara                     # her kaynağın ham okuması (Wi-Fi BSSID listesi, GPS fix...)
python3 -m robot.konum tara --hepsi             # ayarda kapalı kaynaklar (kamera) dahil
python3 -m robot.konum kaydet giris-holu --adet 5   # Wi-Fi parmak izi topla (konum/parmak_izi.yaml)
python3 -m robot.konum ogret giris-holu --adet 5    # kameradan görsel örnek (konum/gorsel_ornekler/)
python3 -m robot.konum nerede                   # birleştirici sonucu bir kez
python3 -m robot.konum izle                     # sürekli (Ctrl+C)
python3 -m robot.konum isaret 7                 # ArUco işareti PNG'si (konum/isaretler/), basıp asın
python3 -m robot.konum sifirla-odometri         # ESP32'ye {"k":"odo_sifirla"}
python3 ana.py --konum giris-holu               # bölgeyi elle ver (diğer kaynakları ezer)
```

Robot servisi çalışırken seri port meşguldür; `nerede`/`tara`/`sifirla-odometri` o zaman sahte seriye düşer
(odometri görünmez). Önce `systemctl --user stop robot`.

**Kampüste Wi-Fi parmak izi toplama:**
1. `konum/bolgeler.yaml`'da bölgeleri yazın (kimlik + ad; GPS ve yerel x/y bilinmiyorsa `null` kalsın).
2. Robotu (ya da Pi'yi) bölgenin ortasına götürün, `python3 -m robot.konum kaydet <bolge> --adet 5`.
   Bölgenin 2-3 farklı noktasında ve günün farklı saatlerinde tekrarlayın (insan kalabalığı sinyali değiştirir).
3. Bitince `python3 -m robot.konum izle` ile bölgeler arasında yürüyün; yanlış bölge çıkan yere daha çok ölçüm.
4. `konum/parmak_izi.yaml` depoya girer: `git add kod/konum/parmak_izi.yaml` (ekip aynı haritayı kullanır).
İnternet ya da ağa bağlanmak gerekmez, yalnız tarama yapılır. Telefon hotspot'ları (BSSID'nin ikinci hanesi
2, 6, A, E olanlar çoğu zaman taşınabilir cihazdır) haritayı bozabilir; kayıt sırasında kapalı olsunlar.

**Görsel öğretme:** `aruco.etkin`/`gorsel.etkin` ayarlarını kamera takılınca `true` yapın. Her bölgede robotun
duracağı yerde `ogret <bolge> --adet 5`; robotu 20-30° döndürüp tekrarlayın, akşam ışığında bir tur daha.
`tara --hepsi` görsel satırındaki benzerlik değeri `gorsel.esik` (0.75) ayarı için kullanılır. ArUco işareti
(15 cm, A4) kamera yüksekliğine asılır; `bolgeler.yaml` → `isaretler: {7: giris-holu}`.

**İçerik:** yerlerde `tarifler: {bolge: tarif}` ve `yon: sol|sag|ileri|arka` ya da `yonler: {bolge: yön}`
(`icerik/universite.yaml` örnekleri "..." ile; gerçek yön ve tarifle doldurun). `icerik_kontrol.py` geçersiz
yönü ve `bolgeler.yaml`'da olmayan bölge adını hata sayar. Bulut modeline "Robot şu an: <bölge>" eklenir.

**Ayarlar** (`ayarlar.yaml` → `konum:`): `etkin`, `aralik_saniye` (GPS/BLE), `tazelik_saniye` (30),
`son_bilinen_bolge` (açılış bölgesi), `gps_duzeltme_m`, `bolgeler`; her kaynakta `etkin`, `agirlik` ve kendi
alanları (`wifi.aralik` 15 s, `gps.port`, `aruco.iyi_kenar_px`, `gorsel.esik`, `odometri.tik_tur`/`teker_cap_m`/
`iz_genislik_m`/`yaw_isareti`, `elle.bolge`/`dosya`).

**Sınırlar ve tuzaklar:**
- Bölge düzeyi (3-10 m); yan yana iki bölge Wi-Fi'da benzer görünebilir (güven düşer, son bilinen korunur).
- Wi-Fi taraması bağlantıyı 1-2 s kesebilir/yavaşlatabilir (bulut dil modeli o an gecikebilir): aralık 15 s.
- Windows `netsh` önbellek listesini verir; kod taramayı `wlanapi` ile tetikleyip 4 s bekler (dizüstü denemesi
  için; Windows 11'de konum izni kapalıysa liste boş gelir).
- Görsel tanıma ışık, kalabalık ve dekor değişiminden etkilenir; ArUco en güvenilir kamera kaynağıdır.
- GPS bina içinde çoğu zaman fix vermez; yalnız bahçe/giriş önü gibi açık alanlar.
- Odometri sabitleri TAHMİNİ (`esp32/src/motorlar.cpp` ile aynı); tekerleği 10 tur çevirip `tik_tur`'u ölçün.
  IMU yaw işareti doğrulanmadı: robotu sola çevirip `izle`'de yön artmıyorsa `yaw_isareti: -1`.
- Donanımda (Pi'de nmcli, kamera, GPS, BLE, ESP32 odo) hiçbiri henüz denenmedi; testler sahte veriyle geçer.

## 10. Bakım modu (`robot/bakim.py`)

Robot bakımdayken bir kez "Şu an bakımdayım, birazdan dönerim." der, sonra susar; yüzde bakım ifadesi
(yarı kapalı gözler, dönen dişli), mikrofon kapalı, ESP32'ye `{"k":"dur"}` gider. Süren konuşma turu yarıda
kesilmez: bakıma yalnız BEKLE'den girilir (durum tablosunda BEKLE ↔ BAKIM).

```bash
touch ~/tekerlekli-insansi-robot/kod/bakim.txt   # çalışırken bakıma al (1 s içinde); telefon uygulaması da yazacak
rm ~/tekerlekli-insansi-robot/kod/bakim.txt      # bakımdan çıkar, robot yeniden dinler
python3 ana.py --bakim     # bakımda başlat (yeniden başlatana kadar); ayarda: bakim.etkin: true
```

Ayarlar: `bakim.etkin`, `bakim.dosya` (`bakim.txt`, kod/'a göre), `bakim.aralik_saniye` (1 s). Tetik beklerken de
her saniye dosyaya bakılır (ses/dokunma/GPIO tetiği zaman aşımlı bekler; klavye tetiği Enter'a kadar bakamaz).
`--bakim` ile mikrofon takılı olmasa da robot durmaz (bakımda dinlemediği için). Dosya depoya girmez.

## 11. Ölçüm araçları (TÜBİTAK tabloları)

Üçü de sonucu `olcum/sonuclar/`'a yazar (depoya girer), dış kütüphane olarak yalnız numpy kullanır.

**Bilinmeyen sorular** (`olcum/bilinmeyen_rapor.py`): günlüklerden (`gunlukler/*.csv`) robotun cevaplayamadığı
(konu boş / "bilmiyorum") ve zayıf eşleşmeyle (puan < `--esik`, varsayılan 4) cevapladığı soruları toplar,
benzerlerini kök kelimelerle gruplar, sıklığa göre `bilinmeyen-YYYY-MM-DD.md` yazar: soru, kaç kez, örnek cümle,
en yakın mevcut kayıt, boş "İçeriğe ekle" sütunu. Haftada bir çalıştırıp içerik paketini büyütün.

```bash
python3 olcum/bilinmeyen_rapor.py --gun 7            # son 7 gün; --esik 5, --icerik tesis, --bugun 2026-11-03
```

**Konum test turu** (`olcum/konum_turu.py`): `bolgeler.yaml`'daki bölgeleri sırayla sorar ("Robotu şu bölgeye
götürün", Enter; 'a' atlar, Ctrl+C bitirir), her noktada `--adet` (5) tarama yapar; her kaynağın tek başına ve
birleştiricinin tahminini `konum-turu-<etiket>.csv`'ye (bölge, kaynak, tahmin, güven, doğru mu) yazar; kaynak
başına ve bölge başına doğruluk tablosunu (`.md`) basar. Hedef: 10 bölgede birleşik doğru bölge oranı ≥ %90.
Her yeni bölgede önceki tahminler silinir. `elle` ve odometri ölçülmez (elle doğruyu bilir, odometri bölge vermez).

```bash
python3 olcum/konum_turu.py --etiket kampus-1 --adet 5 --kaynaklar wifi,aruco   # varsayılan: ayarda etkinler
```

**Gürültü provası** (`olcum/gurultu_prova.py`): `olcum/ses/konusma/<ad>.wav` + `<ad>.txt` (doğru metin) kayıtlarını
`olcum/ses/gurultu/*.wav` ile `--snr` değerlerinde (20,10,5,0 dB) karıştırır, Vosk ile tanır, `test_seti.py`'nin
ölçütleriyle (normalize eşleşme, KHO) SNR × tanıma tablosu yazar (`gurultu-<etiket>.md`; temiz kayıt taban
satırı, gürültü türüne göre tablo, ayrıntı). Kayıtlar 16 bit wav (her hız olur, 16 kHz'e çevrilir); depoya
girmez (kişisel ses). SNR bütün kayıt üzerinden hesaplanır: kayıtların başını/sonunu kısa kesin. Taşma olursa
karışım bütünüyle kısılır (kırpma yok, SNR değişmez). Vosk yoksa `--stt klavye` (karışımı wav olarak yazar,
dinleyip yazarsınız: insan tabanı) ya da `--stt referans` (betiği denemek için; hep %100).

```bash
python3 olcum/gurultu_prova.py --etiket kantin --snr 20,10,5,0       # Pi, Vosk modeliyle
```

## 12. Yüz ifadeleri ve cevap çeşitliliği

| Durum | Yüz |
|---|---|
| BEKLE | Bakış yavaşça gezinir (2-5 s'de bir yeni nokta), gözler 3-6 s'de bir (rastgele) kırpar |
| DİNLE | "Dinliyorum": gözler büyük, kaşlar hafif kalkık, mikrofon simgesi |
| DÜŞÜN | Gözler yukarıda bir yana bir yana kayar, ağız yerinde üç nokta |
| KONUŞ | Ağız metnin harflerine göre açılıp kapanır (sesli harf geniş, ünsüz dar, boşluk kapalı; 14 harf/s TAHMİNİ) |
| JEST | Gülen gözler ve ağız |
| BAKIM | Yarı kapalı gözler, sağ üstte dönen dişli |

`Yuz.bakis_hedefi(x, y)` gözleri bir yöne çevirir (x -1 sol..+1 sağ, y -1 yukarı..+1 aşağı, 2,5 s); şimdilik
ekrana dokunulan yere bakmakta kullanılır, ileride kamera kişinin yönünü verecek. Animasyon durumu `Ifade`
sınıfında (pygame'siz de çalışır); yazı yüzeyleri önbellekte, her karede yeni yüzey yaratılmaz (PC'de kare başı
0,2-0,5 ms; Pi 5'te 30 fps ölçülmedi). Ağız konuşma süresini metinden tahmin eder; Piper sesi üretirken
(KONUŞ'un başında) ağız sesten önce kıpırdayabilir. Hepsi `--yuz --deneme-saniye 6` ile sırayla görülür.

**Cevap çeşitliliği:** içerik paketinde `selamlama` ve `kaliplar` (kimsin, nasilsin, tesekkur, hosca_kal,
merhaba, yardim) tek metin ya da liste olabilir; liste ise robot rastgele birini söyler, art arda aynısını
söylemez. Metinlerde `{ad}` (robotun adı), `{rol}`, `{kurum}` yazılabilir. Örnekler `icerik/universite.yaml`'da.

## 13. Telefondan kumanda (`robot/uzaktan/`)

Robot çalışırken Pi'de küçük bir web sunucusu da açılır (Nextion ekranı yerine; Efe kararı, 27 Ekim 2026).
Telefon robotla **aynı Wi-Fi'da** olmalı; tarayıcıda açın:

- `http://lale.local:8080` (Pi'nin adı `lale`), olmazsa açılışta terminale yazılan IP: `http://192.168.x.x:8080`.
  Bazı Android sürümleri `.local` adını çözmez; o zaman IP'yi kullanın.
- İlk açılışta PIN sorulur (varsayılan `1234`). Doğru PIN'den sonra telefon 30 gün hatırlanır; robot yeniden
  başlarsa PIN bir kez daha sorulur. Yanlış PIN'e cevap 1 sn gecikir.
- **PIN değiştirme:** `ayarlar.yaml` → `uzaktan: pin: "4821"` (tırnak içinde), robotu yeniden başlatın.
  Port: `uzaktan.port` (8080). Kapatmak: `uzaktan.etkin: false`.
- **Ana ekrana ekleme:** Android Chrome'da ⋮ → "Ana ekrana ekle"; iPhone Safari'de Paylaş → "Ana Ekrana Ekle".
  Adres HTTPS olmadığı için tam "uygulama yükleme" değil kısayol olur; iş görür.

Sayfada: üstte durum şeridi (bağlantı, durum, bölge), yön düğmeleri (basılı tut = sür, bırak = dur; yavaş
0,15 m/s, normal 0,3 m/s), jestler (selam, evet, işaret ← ↑ → ↓), "Söyle" kutusu ve hazır cümleler, bölge seçimi
(`konum/bolge.txt`'ye yazar), bakım modu anahtarı (`kod/bakim.txt`), **Rampa** anahtarı, altta her zaman
görünen kırmızı **DUR**. "Söyle" yalnız robot BEKLE'deyken çalışır; konuşma sırasında reddedilir ve sebebi yazılır.
**Rampa** (29 Ekim 2026): rampaya/eğime girmeden aç. ESP32 (0.4.0) teker ivmesini ve frenini 0,1 m/s²'ye indirir,
kolları ev pozuna alır; açıkken uyarı görünür ("kollar ev pozunda, yavaş"), jest düğmeleri kapanır (`POST /rampa {ac}`).

**Güvenlik:** telefon düşer, uygulama kapanır ya da Wi-Fi koparsa Pi son `sur`dan 0,4 sn sonra kendisi
`dur` gönderir; Pi çökerse ESP32 watchdog'u 0,5 sn'de durdurur. Donanım acil stop yine şart. Hız seri.py
sınırlarına (0,5 m/s, 1 rad/s) kırpılır. Sunucu **yalnız yerel ağ** içindir: modemde port yönlendirme yapmayın,
internete açmayın. PIN'i ilk iş değiştirin. Pi'de güvenlik duvarı (ufw) varsayılan kapalıdır; açtıysanız:
`sudo ufw allow from 192.168.0.0/16 to any port 8080 proto tcp`. Kampüs ağlarında (eduroam) cihazlar çoğu zaman
birbirini göremez; o zaman telefonun hotspot'una Pi'yi bağlayın.

**Robotsuz deneme (Windows'ta da):** `kod/` içinden `py -3 -m robot.uzaktan` (ya da `--port 8080 --pin 4821`);
sahte robotla açılır, adresleri yazar, gelen komutları `[seri] {...}` olarak gösterir. Windows güvenlik duvarı
izin sorarsa "Özel ağlar"a izin verin.
