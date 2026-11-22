"""Bellek içi taşıma: istemciyi sahte ESP32 çekirdeğine doğrudan bağlar, zamanı sanal saatle ilerletir.

`bekle(ms)` çekirdeği ilerletir (`adim`), duvar saatine bakmaz. `kopar()` / `bagla()` kablo çekilmesini taklit eder:
koparken giden baytlar kaybolur, kartın yazdıkları da kaybolur (karşıda dinleyen yok).
"""

import os
import sys

_KOD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _y in (os.path.join(_KOD, "pi"), os.path.join(_KOD, "ortak")):
    if _y not in sys.path:
        sys.path.insert(0, _y)

from lale_pi.tasima import Tasima  # noqa: E402


class BellekTasima(Tasima):
    def __init__(self, cekirdek):
        self.cekirdek = cekirdek
        self._acik = False
        self.bagli = True              # kablo takılı mı
        self._satirlar = []

    def ac(self):
        self._acik = True
        self.cekirdek.cikis_al()       # port açılmadan önce yazılanlar (açılış "hazir"ı dahil) alınmadı sayılmaz:
        # gerçek hatta da port açılmadan önce gelen baytlar kaybolur. Testler açılışı ayrıca sınar (reset ile).

    def kapat(self):
        self._acik = False

    def acik_mi(self):
        return self._acik

    def kopar(self):
        self.bagli = False

    def bagla(self):
        self.bagli = True

    def yaz(self, bayt):
        if not self._acik:
            raise ConnectionError("taşıma kapalı")
        if self.bagli:
            self.cekirdek.bayt_al(bayt)

    def oku(self):
        s, self._satirlar = self._satirlar, []
        return s

    def bekle(self, ms):
        self.cekirdek.adim(ms)
        cikan = self.cekirdek.cikis_al()
        if self._acik and self.bagli:
            self._satirlar += cikan
