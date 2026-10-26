# Robot yazılımı: başlangıç paketi

Tek Python süreci. Durum makinesi BEKLE → DİNLE → DÜŞÜN → (JEST) → KONUŞ → BEKLE döner.
Robot **sesli** çalışır, karşınızda bir yapay zekâ varmış gibi konuşursunuz: düğme yok, mikrofon konuşma
başlayınca dinlemeye geçer (`SesTetik`), dinleme 0,8 sn sessizlikle biter, Vosk tanır, robot cevaplar.
Robot konuşurken mikrofon kapalıdır (yarım dupleks). Mikrofon ya da Vosk modeli yoksa robot açık bir
mesajla durur. Mikrofonsuz deneme için **`--gelistirici`**: ekrana dokun (ya da Enter), soruyu ekrandaki
kutuya (ya da terminale) yaz; bu yalnız geliştirici aracıdır, ziyaretçi robota bir şey yazmaz.
Her tur `gunlukler/YYYY-MM-DD.csv` dosyasına bir satır olarak yazılır (ölçüm için).

| Dosya | İş |
|---|---|
| `ana.py` | Ayarları okur, parçaları kurar, sesli mod denetimi, konuşma döngüsü (`tek_tur`) |
| `ayarlar.yaml` | Tüm seçimler (sağlayıcılar, algılama eşiği, içerik paketi, ekran, GPIO pini, seri port) |
| `robot/durum.py` | Durum makinesi; izinli geçişler `GECISLER` tablosunda |
| `robot/mikrofon.py` | Ortak mikrofon: 30 ms parçalar, RMS eşiği (+ varsa webrtcvad), konuşma başı/sonu algılama |
| `robot/tetik.py` | Konuşma tetiği: `SesTetik` (varsayılan, düğmesiz), `DokunmaTetik` (ekran), `GpioTetik` (düğme), `KlavyeTetik` |
| `robot/stt.py` | Konuşma tanıma: `VoskSTT` (varsayılan), `GoogleSTT`; geliştirici: `KlavyeSTT`, `EkranSTT` (metin kutusu) |
| `robot/icerik.py` | İçerik paketi okuma ve kelime eşlemeli arama |
| `robot/dil.py` | Cevap üretici: `KuralTabanli` (varsayılan), `BulutDilModeli` (gemini / anthropic); `SohbetGecmisi` (son 6 tur) |
| `robot/tts.py` | Seslendirme: `YaziTTS` (varsayılan), `Pyttsx3TTS`, `PiperTTS` |
| `robot/yuz.py` | pygame yüzü (ilkel şekiller), altta son söylenen metin; dokunma tetiğinde "Konuşmak için dokun" alanı |
| `robot/gunluk.py` | Etkileşim günlüğü: her tur bir CSV satırı (tanınan, konu, puan, cevap, jest, süreler) |
| `robot/seri.py` | ESP32'ye satır tabanlı JSON; port yoksa `SahteSeri` |
| `icerik/universite.yaml`, `icerik/tesis.yaml` | Örnek içerik paketleri ("..." yerleri doldurulacak) |
| `icerik_kontrol.py` | İçerik paketi denetleyicisi: zorunlu alanlar, boş/tekrarlı anahtar kelime, "..." listesi |
| `olcum/test_seti.py`, `olcum/test_seti_universite.txt` | STT test seti ölçümü (tanıma oranı, kelime hata oranı, süre) |
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
seslendirme_ms; uctan_uca_ms`. Ayraç `;`, kodlama UTF-8 (BOM'lu): Türkçe Excel'de çift tıklayınca sütunlara
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
  `sudo usermod -aG dialout $USER` ve yeniden oturum aç.
- **Bulut:** anahtar alınca `dil.saglayici: gemini` ya da `anthropic` (sohbet hafızası bulutta işe yarar).
- **Durum doğrulaması:** hiçbir şey donanımda denenmedi; yukarıdaki listeyi bu akşam işaretleyin.
