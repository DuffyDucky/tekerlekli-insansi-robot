# Ne yapıyor: robotun cevabını seslendirir. Hepsi aynı arayüz: soyle(metin).
# YaziTTS yalnız ekrana yazar (hoparlör yokken, varsayılan). Pyttsx3TTS işletim sisteminin sesini
# kullanır (Windows SAPI, Pi'de espeak-ng). PiperTTS daha doğal Türkçe ses: piper komutu + aplay.

import os
import subprocess
import tempfile


def yaz(metin):
    print(f"Robot: {metin}")


class YaziTTS:
    def soyle(self, metin):
        yaz(metin)


class Pyttsx3TTS:
    """pyttsx3 motoru konuşmanın yapıldığı iş parçacığında, ilk konuşmada kurulur (Windows COM kuralı)."""

    def __init__(self, hiz=170):
        try:
            import pyttsx3
        except ImportError:
            raise RuntimeError("Pyttsx3TTS için 'pyttsx3' paketi gerekli: pip install pyttsx3 "
                               "(Pi'de ayrıca: sudo apt install espeak-ng libespeak-ng1)")
        self.pyttsx3 = pyttsx3
        self.hiz = hiz
        self.motor = None

    def _motoru_kur(self):
        self.motor = self.pyttsx3.init()
        self.motor.setProperty("rate", self.hiz)
        ses = turkce_ses_bul(self.motor.getProperty("voices"))
        if ses:
            self.motor.setProperty("voice", ses.id)
        else:
            print("[tts] Türkçe ses bulunamadı; varsayılan sesle okunacak (Türkçe bozuk çıkabilir).")

    def soyle(self, metin):
        yaz(metin)
        if self.motor is None:
            self._motoru_kur()
        self.motor.say(metin)
        self.motor.runAndWait()


def turkce_ses_bul(sesler):
    """Ad, kimlik ya da dil bilgisinde 'tr'/'turk' geçen ilk sesi döner."""
    for ses in sesler:
        diller = " ".join(str(d) for d in (getattr(ses, "languages", None) or []))
        bilgi = f"{ses.id} {ses.name} {diller}".lower()
        if "turk" in bilgi or "tr-tr" in bilgi or "tr_tr" in bilgi or ses.id.lower().endswith("tr"):
            return ses
    return None


class PiperTTS:
    """piper komutu metni wav dosyasına çevirir, aplay çalar. ses_cihazi boşsa varsayılan çıkış."""

    def __init__(self, model_yolu, komut="piper", ses_cihazi=""):
        if not os.path.exists(model_yolu):
            raise RuntimeError(f"Piper ses modeli bulunamadı: {model_yolu} (kur_pi.sh içindeki indirme komutuna bakın)")
        self.model_yolu = model_yolu
        self.komut = komut
        self.ses_cihazi = ses_cihazi

    def soyle(self, metin):
        yaz(metin)
        wav = os.path.join(tempfile.gettempdir(), "robot_konusma.wav")
        # Metin piper'a standart girişten verilir (piper sürümüne göre seçenek adları değişebilir)
        subprocess.run([self.komut, "--model", self.model_yolu, "--output_file", wav],
                       input=metin.encode("utf-8"), check=True, capture_output=True)
        calma = ["aplay", "-q", wav]
        if self.ses_cihazi:
            calma[1:1] = ["-D", self.ses_cihazi]
        subprocess.run(calma, check=True)


def tts_sec(saglayici, hiz=170, piper_model="", piper_komut="piper", ses_cihazi=""):
    """Ayardaki ada göre TTS kurar; kurulamazsa nedenini yazıp yazıya düşer."""
    try:
        if saglayici == "pyttsx3":
            return Pyttsx3TTS(hiz)
        if saglayici == "piper":
            return PiperTTS(piper_model, piper_komut, ses_cihazi)
    except Exception as hata:
        print(f"[tts] {saglayici} kurulamadı: {hata}\n[tts] Yalnız yazıyla devam ediyorum.")
        return YaziTTS()
    if saglayici != "yazi":
        print(f"[tts] Bilinmeyen sağlayıcı '{saglayici}'; yazı kullanıyorum.")
    return YaziTTS()
