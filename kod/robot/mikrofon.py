# Ne yapıyor: mikrofonu 30 ms'lik parçalar halinde okur ve her parçada konuşma var mı diye bakar.
# Konuşma = ses enerjisi (RMS) eşiğin üstünde VE (webrtcvad kuruluysa) "insan sesi" denen parça.
# SesTetik konuşma başlayınca tetikler; STT aynı mikrofondan konuşmayı sessizlik gelene kadar alır.
#
# Yarım dupleks: akış BEKLE'de açılır, DİNLE bitince kapanır; robot DÜŞÜN/KONUŞ'tayken mikrofon kapalı.
# Eşik ayarı için (Pi'de, kod/ klasöründen):  python3 -m robot.mikrofon   (10 sn ses düzeyini yazar)

from collections import deque

try:
    import numpy as np
except ImportError:          # Windows'ta testler numpy'siz de toplanabilsin
    np = None

ORNEKLEME = 16000            # Hz; Vosk ve webrtcvad 16 kHz ister
PARCA_MS = 30                # webrtcvad yalnız 10/20/30 ms parça kabul eder
PARCA = ORNEKLEME * PARCA_MS // 1000      # 480 örnek = 960 bayt (int16)
BASLAMA_PARCA = 3            # art arda 3 konuşma parçası (90 ms) = konuşma başladı; tek tıkırtı tetiklemez
ON_KAYIT_PARCA = 10          # konuşma algılanmadan önceki 300 ms de alınır; ilk hece kesilmesin
ATLA_PARCA = 10              # akış açılınca ilk 300 ms atlanır (açılma tıkırtısı, robotun son yankısı)


class MikrofonYok(Exception):
    """Mikrofon ya da gerekli paket yok; ana.py bunu açık bir mesajla kullanıcıya söyler."""


def rms(parca):
    """Parçanın ses enerjisi (karekök ortalama kare). Sessiz oda ~50-300, konuşma ~1000+ (int16)."""
    ornekler = np.frombuffer(parca, dtype=np.int16).astype(np.float32)
    return float(np.sqrt(np.mean(ornekler * ornekler))) if len(ornekler) else 0.0


def vad_kur(duzey):
    """webrtcvad kuruluysa insan sesi algılayıcı (0 gevşek - 3 sıkı); yoksa None ve yalnız RMS."""
    if duzey is None or duzey < 0:
        return None
    try:
        import webrtcvad
    except ImportError:
        return None
    return webrtcvad.Vad(int(duzey))


def gercek_akis_fabrikasi(cihaz=None):
    """sounddevice ile 16 kHz, tek kanal, int16 akış açan fonksiyonu döner. Olmazsa MikrofonYok."""
    try:
        import sounddevice as sd
    except Exception as hata:     # paket yok ya da PortAudio kütüphanesi yok (OSError)
        raise MikrofonYok(f"'sounddevice' kullanılamıyor ({hata}). Kurulum: pip install sounddevice "
                          "(Pi'de önce: sudo apt install portaudio19-dev python3-numpy)")
    if np is None:
        raise MikrofonYok("'numpy' gerekli: pip install numpy (Pi'de: sudo apt install python3-numpy)")
    try:
        sd.check_input_settings(device=cihaz, samplerate=ORNEKLEME, channels=1, dtype="int16")
    except Exception as hata:
        raise MikrofonYok(f"Mikrofon bulunamadı ya da 16 kHz açılamıyor ({hata}). "
                          "Cihazları görmek için: python3 -c \"import sounddevice; print(sounddevice.query_devices())\"")

    def ac():
        return sd.RawInputStream(samplerate=ORNEKLEME, blocksize=PARCA, dtype="int16",
                                 channels=1, device=cihaz)
    return ac


class Mikrofon:
    """Ses tetiği ve STT'nin ortak mikrofonu. akis_ac yalnız testte sahte akış vermek için."""

    def __init__(self, cihaz=None, esik=500, sessizlik_saniye=0.8, vad_duzeyi=2, akis_ac=None):
        self._akis_ac = akis_ac or gercek_akis_fabrikasi(cihaz)
        self.esik = esik
        self.sessizlik_saniye = sessizlik_saniye
        self.vad = vad_kur(vad_duzeyi)
        self.akis = None
        self.on_kayit = []        # tetik anında yakalanan konuşma başı; STT ilk bunu alır
        self._bekleme_sifirla()

    def _bekleme_sifirla(self):
        """konusma_bekle'nin çağrılar arası belleği: son 300 ms ve art arda konuşma parçası sayısı."""
        self._son_parcalar = deque(maxlen=ON_KAYIT_PARCA)
        self._ardisik = 0

    def konusma_mi(self, parca):
        if rms(parca) < self.esik:
            return False
        return self.vad is None or self.vad.is_speech(parca, ORNEKLEME)

    def ac(self):
        if self.akis is None:
            self.akis = self._akis_ac()
            self.akis.start()
            for _ in range(ATLA_PARCA):
                self._oku()

    def kapat(self):
        if self.akis is not None:
            self.akis.stop()
            self.akis.close()
            self.akis = None
        self._bekleme_sifirla()

    def _oku(self):
        veri, _ = self.akis.read(PARCA)
        return bytes(veri)

    def konusma_bekle(self, zaman_asimi=None):
        """BEKLE: konuşma başlayana kadar dinler; başlayınca True. Akış açık kalır; konuşmanın başı on_kayit'ta.
        zaman_asimi (saniye) verilirse o sürede konuşma başlamazsa False döner (ana.py arada bakım dosyasına
        bakar); akış ve son 300 ms korunur, sonraki çağrı kaldığı yerden sürer."""
        self.ac()
        azami = None if zaman_asimi is None else max(1, int(zaman_asimi * 1000 / PARCA_MS))
        okunan = 0
        while azami is None or okunan < azami:
            parca = self._oku()
            okunan += 1
            self._son_parcalar.append(parca)
            self._ardisik = self._ardisik + 1 if self.konusma_mi(parca) else 0
            if self._ardisik >= BASLAMA_PARCA:
                self.on_kayit = list(self._son_parcalar)
                self._bekleme_sifirla()
                return True
        return False

    def konusma_parcalari(self, azami_saniye=8, konusmasiz_bekleme=5):
        """DİNLE: konuşmayı parça parça verir. Konuşmadan sonra sessizlik_saniye kadar sessizlik olunca,
        hiç konuşulmazsa konusmasiz_bekleme saniye sonra, en geç azami_saniye'de biter; sonra akış kapanır."""
        self.ac()
        try:
            konustu = bool(self.on_kayit)
            yield from self.on_kayit
            self.on_kayit = []
            sessiz_ms = 0
            for sira in range(1, int(azami_saniye * 1000 / PARCA_MS) + 1):
                parca = self._oku()
                yield parca
                if self.konusma_mi(parca):
                    konustu, sessiz_ms = True, 0
                else:
                    sessiz_ms += PARCA_MS
                if konustu and sessiz_ms >= self.sessizlik_saniye * 1000:
                    return                                    # cümle bitti
                if not konustu and sira * PARCA_MS >= konusmasiz_bekleme * 1000:
                    return                                    # kimse konuşmadı
        finally:
            self.kapat()                                      # yarım dupleks: robot konuşurken kapalı

    def konusmayi_kaydet(self, azami_saniye=8):
        """Bütün konuşmayı tek parça ham ses (bayt) olarak döner; hiç ses yoksa b''."""
        return b"".join(self.konusma_parcalari(azami_saniye))


def esik_olc(saniye=10, cihaz=None):
    """Eşik seçmek için: önce sessiz durun, sonra konuşun; satırlardaki RMS değerlerine bakın."""
    import time
    akis = gercek_akis_fabrikasi(cihaz)()
    akis.start()
    print("RMS (sessizken ve konuşurken karşılaştırın; esik ikisinin arasına):")
    bitis = time.monotonic() + saniye
    while time.monotonic() < bitis:
        degerler = [rms(bytes(akis.read(PARCA)[0])) for _ in range(8)]   # ~0,25 s
        en_buyuk = max(degerler)
        print(f"{en_buyuk:7.0f} {'#' * int(min(en_buyuk, 4000) / 100)}")
    akis.stop()
    akis.close()


if __name__ == "__main__":
    esik_olc()
