#!/usr/bin/env bash
# Ne yapıyor: Raspberry Pi OS Bookworm (64 bit) üzerinde robot yazılımının bağımlılıklarını kurar.
# apt paketleri + sistem paketlerini de gören sanal ortam (~/robot-venv) + pip paketleri.
# Kullanım (kod/ klasöründe):  bash kur_pi.sh
set -e
cd "$(dirname "$0")"

echo "== apt paketleri =="
sudo apt update
sudo apt install -y python3-pygame python3-pip python3-venv python3-gpiozero python3-lgpio \
    python3-numpy portaudio19-dev espeak-ng libespeak-ng1 alsa-utils

echo "== sanal ortam: ~/robot-venv =="
# --system-site-packages: apt'tan gelen pygame ve gpiozero/lgpio (Pi 5 GPIO'su için şart) venv'de de görünür
python3 -m venv --system-site-packages ~/robot-venv
~/robot-venv/bin/pip install -r requirements.txt
# Seslendirme, seri port ve sesli mod (mikrofon akışı + çevrimdışı konuşma tanıma)
~/robot-venv/bin/pip install pyttsx3 pyserial || echo "UYARI: pyttsx3/pyserial kurulamadı"
~/robot-venv/bin/pip install sounddevice vosk || echo "UYARI: sounddevice/vosk kurulamadı (sesli mod çalışmaz)"

mkdir -p modeller

# --- İsteğe bağlı adımlar (komutu kopyalayıp çalıştırın) ---
# Piper (daha doğal Türkçe ses):
#   ~/robot-venv/bin/pip install piper-tts
#   wget -P modeller https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx
#   wget -P modeller https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json
#   echo "Merhaba, ben robot." | piper --model modeller/tr_TR-dfki-medium.onnx --output_file /tmp/deneme.wav && aplay /tmp/deneme.wav
#
# Vosk küçük Türkçe model (sesli mod için gerekli; model adını https://alphacephei.com/vosk/models sayfasından doğrulayın):
#   wget https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip && unzip vosk-model-small-tr-0.3.zip -d modeller
#
# Daha iyi konuşma algılama (gürültüde insan sesini ayırır; kurulmazsa yalnız ses düzeyi eşiği kullanılır):
#   ~/robot-venv/bin/pip install webrtcvad-wheels
# Eşik ayarı (mikrofon takılıyken, önce sessiz durun sonra konuşun):  python3 -m robot.mikrofon
#
# Bulut dil modeli (anahtar ~/.bashrc içine: export GEMINI_API_KEY=... ya da export ANTHROPIC_API_KEY=...):
#   ~/robot-venv/bin/pip install google-genai
#   ~/robot-venv/bin/pip install anthropic
#
# Konum (OKU_BENI.md 9. bölüm; gpsd GEREKMEZ). ArUco/görsel için OpenCV, BLE beacon için bleak:
#   sudo apt install python3-opencv            # ya da: ~/robot-venv/bin/pip install opencv-contrib-python-headless
#   ~/robot-venv/bin/pip install bleak
#   ~/robot-venv/bin/pip install onnxruntime   # isteğe bağlı daha iyi görsel özet, model:
#   wget -O modeller/mobilenet.onnx https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-12.onnx
#   python3 -m robot.konum tara                 # kaynaklar çalışıyor mu
#
# Otomatik başlatma (masaüstü açılınca robot kendiliğinden çalışsın; ayrıntı OKU_BENI.md 7. bölüm):
#   mkdir -p ~/.config/systemd/user
#   cp robot.service ~/.config/systemd/user/
#   systemctl --user daemon-reload
#   systemctl --user enable --now robot.service
#   journalctl --user -u robot -f              # canlı log (çıkmak: Ctrl+C)
#   systemctl --user stop robot                # durdur;  kalıcı kapatmak: systemctl --user disable robot

echo
echo "Kurulum bitti. Çalıştırmak için:"
echo "  source ~/robot-venv/bin/activate"
echo "  python3 ana.py --icerik universite              # mikrofon + Vosk modeli gerekir"
echo "  python3 ana.py --gelistirici --icerik universite # mikrofonsuz deneme (dokun + yaz)"
