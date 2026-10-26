# Pi 5 (lale) kurulum kaydı ve yeniden kurma rehberi

Son güncelleme: 26 Ekim 2026 (Efe + Claude). Bu dosya Pi'nin nasıl kurulduğunu ve sıfırdan nasıl
kurulacağını anlatır; şifre ve Wi-Fi anahtarı içermez.

## Mevcut durum (26 Ekim 2026 gecesi)

| Konu | Değer |
|---|---|
| Kart | Raspberry Pi 5, 64 GB microSD, Active Cooler |
| İşletim sistemi | Raspberry Pi OS (64-bit, masaüstü) 2026-10-06, Trixie, cloud-init ile ilk kurulum |
| Hostname | `lale` → ağda `lale.local` (avahi) |
| Kullanıcılar | `efe` (sudo, Efe'nin PC anahtarı + şifre) ve `duffy` (sudo, Ahmet'in anahtarı; ilk kurulumdan korundu) |
| SSH | açık; anahtar ve şifre ile giriş |
| Wi-Fi | Efe'nin ev/ikinci ev/iPhone ağları + Ahmet'in ağı kayıtlı (NetworkManager; `nmcli con show`) |
| Seri | `rpi.interfaces.serial: true`, `dtparam=uart0=on` (Nextion için GPIO14/15, `/dev/serial0` → ttyAMA10) |
| Ses | yalnız HDMI (`vc4hdmi0`, `vc4hdmi1`); 3,5 mm yok; mikrofon henüz yok |
| Depo | `~/tekerlekli-insansi-robot` (sığ klon, dal `yazilim-baslangic`, origin SSH; Pi'nin anahtarı Efe'nin GitHub hesabında) |
| Sanal ortam | `~/robot-venv` (`--system-site-packages`; pygame/gpiozero/lgpio apt'tan) |
| Modeller | `kod/modeller/vosk-model-small-tr-0.3/`, `kod/modeller/tr_TR-dfki-medium.onnx(.json)` (depoya girmez) |
| Ayar | `kod/ayarlar.yaml`: ad Lale, tts piper, ses `plughw:CARD=vc4hdmi0,DEV=0`, yüz tam ekran |
| Doğrulama | 104 pytest yeşil (SDL dummy), Piper wav üretti, Vosk modeli yüklendi, terminal konuşma turu geçti |
| Kurulum logu | `~/kur_lale.log` (betik `~/kur_lale.sh`) |

Kurulmayan: systemd kullanıcı servisi (`kod/robot.service`). Ekran ve mikrofon takılmadan açılırsa
5 saniyede bir yeniden başlar; donanım gelince kurulacak (`kod/OKU_BENI.md` 7. bölüm).

## Bağlanma ve çalıştırma

```bash
ssh efe@lale.local                      # Efe'nin PC'sinden anahtarla; Ahmet: ssh duffy@lale.local
cd ~/tekerlekli-insansi-robot/kod
source ~/robot-venv/bin/activate
python3 ana.py --gelistirici --yuzsuz --stt klavye --tts yazi --tetik klavye   # ekransız/mikrofonsuz deneme
python3 ana.py --gelistirici --tam-ekran                                       # ekran bağlıyken: dokun + yaz
python3 -m robot.mikrofon                                                      # mikrofon gelince eşik ölçümü
python3 ana.py --icerik universite                                             # tam sesli mod (mikrofon + Vosk)
```

Piper sesi denemesi (HDMI hoparlör bağlıyken):

```bash
echo "Merhaba, ben Lale." | ~/robot-venv/bin/piper --model modeller/tr_TR-dfki-medium.onnx --output_file /tmp/lale.wav
aplay -D plughw:CARD=vc4hdmi0,DEV=0 /tmp/lale.wav
```

Depoyu güncelleme: `cd ~/tekerlekli-insansi-robot && git pull`. Pi'de yapılan değişiklik commit + push edilir
(git kimliği Efe'nin hesabı olarak ayarlı).

## Sıfırdan kurma (Windows'tan, ~25 dk)

Pi OS Trixie ilk kurulumu **cloud-init** ile yapar: bootfs (FAT32, Windows'ta görünür) üstünde `user-data`,
`network-config`, `meta-data`. Eski `ssh` / `userconf.txt` / `wpa_supplicant.conf` dosyaları yok.

1. **İmaj:** `https://downloads.raspberrypi.com/os_list_imagingutility_v4.json` içinden "Raspberry Pi OS (64-bit)"
   adresini al (2026-10-06 sürümü 1,4 GB `.img.xz`), indir, `.sha256` ile doğrula.
2. **Yazma:** Raspberry Pi Imager 2.0.8 (`winget install RaspberryPiFoundation.RaspberryPiImager`). GUI'den
   ya da komut satırından (yönetici izni ister, UAC'de "Evet"):
   ```powershell
   Start-Process "C:\Program Files\Raspberry Pi Ltd\Imager\rpi-imager.exe" -ArgumentList '--cli','<img.xz>','\\.\PhysicalDriveN' -Verb RunAs -Wait
   ```
   `PhysicalDriveN` numarasını `Get-Disk` ile doğrula (BusType USB, ~60 GB). 64 GB karta yazma + doğrulama ≈ 7 dk.
   GUI ile yazıyorsan özelleştirme ekranında hostname `lale`, kullanıcı, Wi-Fi ve SSH'ı doğrudan girebilirsin;
   o zaman 3. adım gerekmez.
3. **bootfs dosyaları (CLI ile yazdıysan):**
   - `user-data` (cloud-config): `hostname: lale`, `manage_etc_hosts: true`, `packages: [avahi-daemon, git,
     python3-venv, python3-pip, portaudio19-dev, libportaudio2, espeak-ng, alsa-utils]`, `timezone: Europe/Istanbul`,
     `keyboard: {model: pc105, layout: "tr"}`, `users:` listesinde her kullanıcı için `name`, `shell: /bin/bash`,
     `lock_passwd: false`, `passwd: "<sha512 hash: openssl passwd -6>"`,
     `groups: adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,render,netdev,gpio,i2c,spi`,
     `sudo: "ALL=(ALL) NOPASSWD:ALL"`, `ssh_authorized_keys: ["ssh-ed25519 ..."]`; sonra `enable_ssh: true`,
     `ssh_pwauth: true`, `rpi: {interfaces: {serial: true}}`.
   - `network-config` (netplan v2): `wifis.wlan0.access-points` altında her SSID için `password:` (düz metin olur),
     `regulatory-domain: "TR"`, `dhcp4: true`, `optional: true`; `ethernets.eth0` dhcp.
   - `meta-data`: `instance-id: <benzersiz>`.
   - `cmdline.txt` sonuna **aynı satırda** ` ds=nocloud;i=<aynı instance-id> cfg80211.ieee80211_regdom=TR`
     (imajın cmdline'ı satır sonuyla biter; ikinci satıra düşerse çekirdek okumaz).
   - `config.txt` sonuna `dtparam=uart0=on` (Nextion UART).
4. **İlk açılış:** rootfs genişletme + yeniden başlatma + paket kurulumu ≈ 6-7 dk. Pi 5'in MAC'i `2c:cf:67`
   ile başlar (`arp -a`). `ssh efe@lale.local`, bitişi `sudo cloud-init status --wait` ile bekle.
5. **Robot yazılımı:**
   ```bash
   git clone --depth 1 --single-branch -b yazilim-baslangic git@github.com:DuffyDucky/tekerlekli-insansi-robot.git ~/tekerlekli-insansi-robot
   cd ~/tekerlekli-insansi-robot/kod && bash kur_pi.sh
   ~/robot-venv/bin/pip install webrtcvad-wheels piper-tts
   wget -P modeller https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip && (cd modeller && unzip -q vosk-model-small-tr-0.3.zip && rm vosk-model-small-tr-0.3.zip)
   wget -P modeller https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx
   wget -P modeller https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json
   SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ~/robot-venv/bin/python3 -m pytest -q
   ```
   Zayıf Wi-Fi'de tam klon (100+ MB geçmiş) çok yavaş; `--depth 1` şart. Uzun kurulumu `nohup ... &` ile
   başlatıp ayrı ssh'tan bekle.

## Öğrenilen tuzaklar

- **Daha önce açılmış bir karta** bootfs'ten Wi-Fi/kullanıcı eklemek (meta-data ve cmdline'da instance-id
  değiştirerek) Pi OS Trixie'de **işe yaramadı** (26 Ekim 2026'da denendi, Pi iki açılışta da ağa girmedi).
  Çözüm sıfırdan yazım ya da rootfs'e Linux'tan dokunmak.
- Pi OS'ta `iw` yok; sinyal için `cat /proc/net/wireless` ya da `nmcli -f IN-USE,SSID,CHAN,RATE,SIGNAL dev wifi`.
  -79 dBm'de klon dakikalarca sürdü; Pi modeme yaklaştırılınca -67 dBm.
- Uzaktan `pkill -f "git clone"` kendi ssh komut satırını da öldürür; `pkill -x git` kullan.
- cloud-init logunda `cc_netplan_nm_patch bulunamadı` uyarısı Pi OS'un kendi modülü, zararsız.
- Pygame'li testler ekransız `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` ile geçer.

## Açık işler

- Ekran + HDMI hoparlör bağlanınca tam ekran yüz ve Piper sesi denemesi; sonra `robot.service`.
- Mikrofon (XVF3800 dizi, bkz. `raporlar/mikrofon-secimi.md`) gelince eşik ölçümü ve varsayılan sesli mod.
- `kod/icerik/*.yaml` içindeki "..." yer tutucuları (21 adet, `python3 icerik_kontrol.py` listeler).
- ESP32 gelince `seri.port` (`/dev/ttyUSB0` ya da `/dev/ttyACM0`).
- Nextion ekranı: config.txt'deki UART satırı Ahmet'in; ekranın planı ekipte netleşecek.
