# Robot yazılımı: başlangıç paketi

Tek Python süreci. Durum makinesi BEKLE → DİNLE → DÜŞÜN → (JEST) → KONUŞ → BEKLE döner.
Donanım yokken klavye, yazı ve sahte seri ile çalışır; Pi'de yalnız `ayarlar.yaml` değiştirilerek
gerçek mikrofon, hoparlör, düğme ve ESP32'ye geçilir.

| Dosya | İş |
|---|---|
| `ana.py` | Ayarları okur, parçaları kurar, konuşma döngüsü (`tek_tur`) |
| `ayarlar.yaml` | Tüm seçimler (sağlayıcılar, içerik paketi, ekran, GPIO pini, seri port) |
| `robot/durum.py` | Durum makinesi; izinli geçişler `GECISLER` tablosunda |
| `robot/icerik.py` | İçerik paketi okuma ve kelime eşlemeli arama |
| `robot/dil.py` | Cevap üretici: `KuralTabanli` (varsayılan), `BulutDilModeli` (gemini / anthropic) |
| `robot/stt.py` | Konuşma tanıma: `KlavyeSTT` (varsayılan), `VoskSTT`, `GoogleSTT` |
| `robot/tts.py` | Seslendirme: `YaziTTS` (varsayılan), `Pyttsx3TTS`, `PiperTTS` |
| `robot/yuz.py` | pygame yüzü (ilkel şekiller), altta son söylenen metin |
| `robot/tetik.py` | Bas-konuş: `KlavyeTetik` (Enter), `GpioTetik` (düğme) |
| `robot/seri.py` | ESP32'ye satır tabanlı JSON; port yoksa `SahteSeri` |
| `icerik/universite.yaml`, `icerik/tesis.yaml` | Örnek içerik paketleri ("..." yerleri doldurulacak) |
| `tests/` | pytest testleri |

## 1. Windows'ta çalıştırma (klavye + yazı + yüz)

Depo kökünde (PowerShell):

```powershell
py -3 -m pip install pyyaml pytest pygame
py -3 -m pytest kod/tests -q                       # testler
py -3 kod/ana.py --yuzsuz --icerik universite      # yalnız terminal
py -3 kod/ana.py --icerik universite               # yüz penceresiyle
py -3 kod/ana.py --yuz --deneme-saniye 3           # yüz tüm ifadeleri gösterip 3 sn'de kapanır
```

Kullanım: Enter'a bas (düğme yerine), sonra soruyu yaz ve Enter (mikrofon yerine). Robotun cevabı
`Robot: ...` diye yazılır; jest varsa `[seri] {"k":"jest",...}` satırı görünür. Çıkış: Ctrl+C
(terminal) ya da ESC (yüz penceresi). Yüz açıkken soruları yine terminale yazın.

Komut satırı seçenekleri ayar dosyasını ezer: `--icerik universite|tesis|dosya.yaml`, `--yuz/--yuzsuz`,
`--saglayici kural|gemini|anthropic`, `--stt klavye|vosk|google`, `--tts yazi|pyttsx3|piper`,
`--ayar baska.yaml`, `--deneme-saniye N`.

## 2. Pi'de bu akşam adım adım

Raspberry Pi OS Bookworm (64 bit, masaüstü), 10,1" ekran HDMI'da, klavye takılı. Komutları Pi'nin
kendi ekranındaki terminalde çalıştırın (SSH'tan açılan pygame penceresi ekrana gelmez).

1. Depoyu al: `git clone https://github.com/DuffyDucky/tekerlekli-insansi-robot.git`
   → `cd tekerlekli-insansi-robot && git checkout yazilim-baslangic && cd kod`
2. Kur: `bash kur_pi.sh` (apt paketleri, `~/robot-venv` sanal ortamı, pyttsx3, pyserial)
3. Ortamı aç: `source ~/robot-venv/bin/activate`, sonra testler: `python3 -m pytest tests -q`
4. Yüzsüz dene: `python3 ana.py --yuzsuz --icerik universite` (3-4 soru sor)
5. Yüzle dene: `ayarlar.yaml` içinde `yuz.tam_ekran: true` yap, `python3 ana.py --icerik universite`
6. Ses: önce `espeak-ng -v tr "Merhaba, ben robot"` ile hoparlörü dene (aşağıdaki HDMI notu),
   ses geliyorsa `ayarlar.yaml` → `tts.saglayici: pyttsx3`, tekrar çalıştır.

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
| `stt.saglayici` | `klavye`, `vosk`, `google` | Mikrofon gelince `vosk` |
| `stt.vosk_model`, `stt.azami_saniye`, `stt.mikrofon` | yol, saniye, cihaz | |
| `tts.saglayici` | `yazi`, `pyttsx3`, `piper` | |
| `tts.hiz`, `tts.piper_komut`, `tts.piper_model`, `tts.ses_cihazi` | | `ses_cihazi` aplay `-D` değeri |
| `yuz.etkin`, `yuz.genislik`, `yuz.yukseklik`, `yuz.tam_ekran` | | 10,1": 1280×800; Pi'de `tam_ekran: true` |
| `tetik.saglayici`, `tetik.gpio_pin` | `klavye`/`gpio`, BCM no (17) | Düğme GPIO17 (fiziksel pin 11) ile GND arası |
| `seri.port`, `seri.hiz` | boş / `/dev/ttyUSB0`, 115200 | Boşsa sahte seri |
| `jest.sure` | saniye | Jestten sonra konuşmaya geçmeden bekleme |

Eksik paket ya da donanım programı durdurmaz: neden yazılır ve varsayılana (klavye, yazı, kural,
sahte seri) düşülür. Açılıştaki `[ana] ...` satırı hangi parçanın gerçekten kurulduğunu gösterir.

## 4. Sağlayıcı değiştirme (bulut dil modeli)

```bash
pip install google-genai            # ya da: pip install anthropic
export GEMINI_API_KEY=...           # ya da: export ANTHROPIC_API_KEY=...
python3 ana.py --saglayici gemini   # ya da ayarlar.yaml → dil.saglayici: gemini
```

Windows PowerShell'de: `$env:GEMINI_API_KEY="..."`. Anahtarı koda ve depoya yazmayın. Bulut modeline
kısa bir sistem istemi (robotun adı ve rolü, "1-2 cümle, Türkçe, kibar") ve içerik paketinden en iyi
3 eşleşme gider. Anahtar ya da paket yoksa, ya da internet giderse robot kural tabanlı cevaba düşer.
Bulut çağrısı yalnız sahte istemciyle test edildi; gerçek anahtarla ilk denemede model adını kontrol edin.

## 5. Bu gece doğrulanacaklar (Pi'de)

- [ ] `kur_pi.sh` hatasız bitiyor mu; `python3 -m pytest tests -q` yeşil mi
- [ ] Yüz tam ekran mı, 1280×800 ekrana oturuyor mu, ESC ile çıkılıyor mu (Wayland masaüstünde)
- [ ] Türkçe karakterler (ı, ğ, ş, İ) alt satırda doğru görünüyor mu
- [ ] HDMI ses geliyor mu (`speaker-test`, `espeak-ng -v tr "deneme"`)
- [ ] pyttsx3 Türkçe ses buluyor mu (açılışta "Türkçe ses bulunamadı" uyarısı çıkıyor mu); çıkıyorsa
      ya da ses kötüyse Piper'ı kur (`kur_pi.sh` içindeki yorumlu komutlar), `tts.saglayici: piper`
- [ ] Piper komutunun seçenekleri (`--model`, `--output_file`) kurulan sürümle uyuşuyor mu
- [ ] Cevaplarda "..." geçen yerler: içerik paketini gerçek bilgiyle doldur (TTS "..."yı garip okur)

## 6. Sonraki adımlar

- **Mikrofon gelince:** `vosk sounddevice` kur, Vosk modelini `modeller/` içine indir,
  `stt.saglayici: vosk`. `python3 -c "import sounddevice; print(sounddevice.query_devices())"` ile
  mikrofonun adını/numarasını bul, gerekirse `stt.mikrofon` alanına yaz.
- **Düğme gelince:** GPIO17 ile GND arasına bağla, `tetik.saglayici: gpio`.
- **ESP32 gelince:** ESP32 tarafı aynı JSON satırlarını okuyacak (`robot/seri.py` başındaki komut
  listesi) ve 500 ms komut gelmezse motorları durduracak (watchdog). `seri.port: /dev/ttyUSB0`
  (ya da `/dev/ttyACM0`; `ls /dev/tty*` ile bak). Kullanıcı `dialout` grubunda olmalı:
  `sudo usermod -aG dialout $USER` ve yeniden oturum aç.
- **Bulut:** anahtar alınca `dil.saglayici: gemini` ya da `anthropic`.
- **Durum doğrulaması:** hiçbir şey donanımda denenmedi; yukarıdaki listeyi bu akşam işaretleyin.
