# Ne yapıyor: kullanıcının söylediğini yazıya çevirir. Hepsi aynı arayüz: dinle() -> str | None.
# KlavyeSTT klavyeden okur (mikrofon yokken, varsayılan). VoskSTT internetsiz (Türkçe küçük model),
# GoogleSTT internetle çalışır. Paket eksikse açık bir hata mesajı verir; ana.py klavyeye düşer.

import json


class KlavyeSTT:
    """Mikrofon yerine klavye. Girdi biterse (Ctrl+Z / dosya sonu) EOFError fırlar, program kapanır."""

    def dinle(self):
        metin = input("Siz: ").strip()
        return metin or None


class VoskSTT:
    """Çevrimdışı tanıma: vosk + sounddevice. Model klasörü ayardan (vosk-model-small-tr-...)."""

    ORNEKLEME = 16000   # Hz, Vosk küçük modelleri 16 kHz ister

    def __init__(self, model_yolu, azami_saniye=8, cihaz=None):
        try:
            import sounddevice
            import vosk
        except ImportError:
            raise RuntimeError("VoskSTT için 'vosk' ve 'sounddevice' paketleri gerekli: "
                               "pip install vosk sounddevice (Pi'de önce: sudo apt install portaudio19-dev)")
        self.sd = sounddevice
        self.model = vosk.Model(model_yolu)   # klasör yoksa vosk kendi hatasını verir
        self.vosk = vosk
        self.azami_saniye = azami_saniye
        self.cihaz = cihaz or None

    def dinle(self):
        tanima = self.vosk.KaldiRecognizer(self.model, self.ORNEKLEME)
        parca = 4000                                   # 0,25 s'lik ses parçası
        en_fazla_parca = int(self.azami_saniye * self.ORNEKLEME / parca)
        # Mikrofon yalnız bu blokta açık (DİNLE durumu); robot konuşurken açılmaz
        with self.sd.RawInputStream(samplerate=self.ORNEKLEME, blocksize=parca, dtype="int16",
                                    channels=1, device=self.cihaz) as akis:
            for _ in range(en_fazla_parca):
                veri, _ = akis.read(parca)
                if tanima.AcceptWaveform(bytes(veri)):   # konuşma bitti (sessizlik algılandı)
                    break
        metin = json.loads(tanima.FinalResult()).get("text", "").strip()
        return metin or None


class GoogleSTT:
    """İnternetle tanıma: speech_recognition paketi, tr-TR. Mikrofon için PyAudio da gerekir."""

    def __init__(self, azami_saniye=8):
        try:
            import speech_recognition
        except ImportError:
            raise RuntimeError("GoogleSTT için 'SpeechRecognition' ve 'PyAudio' paketleri gerekli: "
                               "pip install SpeechRecognition PyAudio")
        self.sr = speech_recognition
        self.tanima = speech_recognition.Recognizer()
        self.azami_saniye = azami_saniye

    def dinle(self):
        try:
            with self.sr.Microphone() as kaynak:
                self.tanima.adjust_for_ambient_noise(kaynak, duration=0.5)
                ses = self.tanima.listen(kaynak, timeout=5, phrase_time_limit=self.azami_saniye)
            return self.tanima.recognize_google(ses, language="tr-TR")
        except (self.sr.WaitTimeoutError, self.sr.UnknownValueError):
            return None                                   # kimse konuşmadı ya da anlaşılmadı
        except self.sr.RequestError as hata:
            print(f"[stt] Google'a ulaşılamadı: {hata}")
            return None


def stt_sec(saglayici, vosk_model="", azami_saniye=8, mikrofon=None):
    """Ayardaki ada göre STT kurar; kurulamazsa nedenini yazıp klavyeye düşer."""
    try:
        if saglayici == "vosk":
            return VoskSTT(vosk_model, azami_saniye, mikrofon)
        if saglayici == "google":
            return GoogleSTT(azami_saniye)
    except Exception as hata:
        print(f"[stt] {saglayici} kurulamadı: {hata}\n[stt] Klavyeye düşüyorum.")
        return KlavyeSTT()
    if saglayici != "klavye":
        print(f"[stt] Bilinmeyen sağlayıcı '{saglayici}'; klavye kullanıyorum.")
    return KlavyeSTT()
