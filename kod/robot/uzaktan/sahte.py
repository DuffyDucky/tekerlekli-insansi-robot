# Ne yapıyor: donanımsız robot taklidi (sahte seri, yazı TTS, pencere açmayan yüz, sohbet geçmişi).
# `python -m robot.uzaktan` denemesi ve testler kullanır; gerçek robotta kullanılmaz.
# Sahte seri rampa kipini de tutar (SahteSeri.rampa / rampa_acik): telefondaki "Rampa" anahtarı
# donanımsız denenebilir; jest reddi köprüde, ivme sınırı yalnız gerçek ESP32'de.

from collections import deque
from types import SimpleNamespace

from robot.durum import DurumMakinesi
from robot.seri import SahteSeri
from robot.tts import YaziTTS


class SahteYuz:
    def __init__(self):
        self.metin = ""

    def metin_goster(self, metin):
        self.metin = metin


def sahte_robot(seri=None, tts=None, konum=None):
    return SimpleNamespace(
        durum=DurumMakinesi(),
        tetik=None,
        stt=None,
        dil=SimpleNamespace(gecmis=SimpleNamespace(turlar=deque(maxlen=6))),
        tts=tts or YaziTTS(),
        seri=seri or SahteSeri(),
        yuz=SahteYuz(),
        konum=konum,
    )
