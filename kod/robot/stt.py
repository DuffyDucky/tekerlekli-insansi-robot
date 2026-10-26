# Ne yapıyor: kullanıcının söylediğini yazıya çevirir. Hepsi aynı arayüz: dinle() -> str | None.
# VoskSTT internetsiz (Türkçe küçük model), GoogleSTT internetle; ikisi de ortak mikrofondan (robot/mikrofon.py)
# okur, dinleme sessizlikle biter. KlavyeSTT (terminal) ve EkranSTT (metin kutusu) yalnız geliştirici denemesi için.

import json
import os
import queue

from robot.mikrofon import ORNEKLEME
from robot.tetik import kuyrugu_bosalt


class KlavyeSTT:
    """Mikrofon yerine klavye. Girdi biterse (Ctrl+Z / dosya sonu) EOFError fırlar, program kapanır."""

    def dinle(self):
        metin = input("Siz: ").strip()
        return metin or None


class EkranSTT:
    """Yalnız GELİŞTİRİCİ modu (--gelistirici, mikrofon yokken deneme): soru ekrandaki metin kutusuna
    yazılır, Enter gönderir.
    Yüz (ANA iş parçacığı) Enter'da gonder(metin) çağırır; dinle() kuyruktan okur."""

    def __init__(self):
        self.kuyruk = queue.Queue()

    def gonder(self, metin):
        self.kuyruk.put(metin)               # yüz çağırır (ana iş parçacığı)

    def dinle(self):
        kuyrugu_bosalt(self.kuyruk)          # eski girişler sayılmaz
        print("[Sorunuzu ekrandaki kutuya yazıp Enter'a basın]")
        metin = self.kuyruk.get().strip()    # Enter'a basılana kadar burada bekler
        return metin or None


class VoskSTT:
    """Çevrimdışı tanıma (Türkçe küçük model). Ses ortak mikrofondan gelir; dinleme sessizlikle biter."""

    def __init__(self, model_yolu, mikrofon, azami_saniye=8):
        if mikrofon is None:
            raise RuntimeError("mikrofon yok")
        try:
            import vosk
        except ImportError:
            raise RuntimeError("'vosk' paketi gerekli: pip install vosk")
        if not os.path.isdir(model_yolu):
            raise RuntimeError(f"Vosk modeli bulunamadı: {model_yolu} (kur_pi.sh içindeki indirme komutuna bakın)")
        vosk.SetLogLevel(-1)                  # Vosk'un uzun açılış yazılarını gizle
        self.vosk = vosk
        self.model = vosk.Model(model_yolu)
        self.mikrofon = mikrofon
        self.azami_saniye = azami_saniye

    def dinle(self):
        tanima = self.vosk.KaldiRecognizer(self.model, ORNEKLEME)
        # Parçalar konuşulurken tanıyıcıya verilir; konuşma bitince (sessizlik) sonuç hemen hazır olur
        for parca in self.mikrofon.konusma_parcalari(self.azami_saniye):
            tanima.AcceptWaveform(parca)
        metin = json.loads(tanima.FinalResult()).get("text", "").strip()
        return metin or None


class GoogleSTT:
    """İnternetle tanıma (speech_recognition paketi, tr-TR). Ses ortak mikrofondan kaydedilip gönderilir."""

    def __init__(self, mikrofon, azami_saniye=8):
        if mikrofon is None:
            raise RuntimeError("mikrofon yok")
        try:
            import speech_recognition
        except ImportError:
            raise RuntimeError("'SpeechRecognition' paketi gerekli: pip install SpeechRecognition")
        self.sr = speech_recognition
        self.tanima = speech_recognition.Recognizer()
        self.mikrofon = mikrofon
        self.azami_saniye = azami_saniye

    def dinle(self):
        ses = self.mikrofon.konusmayi_kaydet(self.azami_saniye)
        if not ses:
            return None
        try:
            veri = self.sr.AudioData(ses, ORNEKLEME, 2)          # 2 bayt = 16 bit örnek
            return self.tanima.recognize_google(veri, language="tr-TR")
        except self.sr.UnknownValueError:
            return None                                   # anlaşılmadı
        except self.sr.RequestError as hata:
            print(f"[stt] Google'a ulaşılamadı: {hata}")
            return None


def stt_sec(saglayici, vosk_model="", azami_saniye=8, mikrofon=None):
    """Ayardaki ada göre STT kurar; kurulamazsa nedenini yazıp klavyeye düşer
    (ana.py bunu görür: normal modda robot durur, geliştirici modunda klavyeyle devam eder)."""
    try:
        if saglayici == "vosk":
            return VoskSTT(vosk_model, mikrofon, azami_saniye)
        if saglayici == "google":
            return GoogleSTT(mikrofon, azami_saniye)
    except Exception as hata:
        print(f"[stt] {saglayici} kurulamadı: {hata}")
        return KlavyeSTT()
    if saglayici != "klavye":
        print(f"[stt] Bilinmeyen sağlayıcı '{saglayici}'; klavye kullanıyorum.")
    return KlavyeSTT()
