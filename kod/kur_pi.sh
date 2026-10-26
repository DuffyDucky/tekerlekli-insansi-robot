#!/usr/bin/env bash
# Ne yapıyor: Raspberry Pi OS Bookworm (64 bit) üzerinde robot yazılımının bağımlılıklarını kurar.
# apt paketleri + sistem paketlerini de gören sanal ortam (~/robot-venv) + pip paketleri.
# Kullanım (kod/ klasöründe):  bash kur_pi.sh
set -e
cd "$(dirname "$0")"

echo "== apt paketleri =="
sudo apt update
sudo apt install -y python3-pygame python3-pip python3-venv python3-gpiozero python3-lgpio \
    portaudio19-dev espeak-ng libespeak-ng1 alsa-utils

echo "== sanal ortam: ~/robot-venv =="
# --system-site-packages: apt'tan gelen pygame ve gpiozero/lgpio (Pi 5 GPIO'su için şart) venv'de de görünür
python3 -m venv --system-site-packages ~/robot-venv
~/robot-venv/bin/pip install -r requirements.txt
# Bu akşam: seslendirme ve seri port
~/robot-venv/bin/pip install pyttsx3 pyserial || echo "UYARI: pyttsx3/pyserial kurulamadı"

mkdir -p modeller

# --- İsteğe bağlı adımlar (komutu kopyalayıp çalıştırın) ---
# Piper (daha doğal Türkçe ses):
#   ~/robot-venv/bin/pip install piper-tts
#   wget -P modeller https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx
#   wget -P modeller https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json
#   echo "Merhaba, ben robot." | piper --model modeller/tr_TR-dfki-medium.onnx --output_file /tmp/deneme.wav && aplay /tmp/deneme.wav
#
# Vosk küçük Türkçe model (mikrofon gelince; model adını https://alphacephei.com/vosk/models sayfasından doğrulayın):
#   ~/robot-venv/bin/pip install vosk sounddevice
#   wget https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip && unzip vosk-model-small-tr-0.3.zip -d modeller
#
# Bulut dil modeli (anahtar ~/.bashrc içine: export GEMINI_API_KEY=... ya da export ANTHROPIC_API_KEY=...):
#   ~/robot-venv/bin/pip install google-genai
#   ~/robot-venv/bin/pip install anthropic

echo
echo "Kurulum bitti. Çalıştırmak için:"
echo "  source ~/robot-venv/bin/activate"
echo "  python3 ana.py --icerik universite"
