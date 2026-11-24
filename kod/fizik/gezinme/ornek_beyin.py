"""`--beyin` kancası ve canlı harita katmanı için örnek: keşif sürüşü + yalnız odometriyle kaba doluluk ızgarası.

    kod\\simulasyon3b.bat labirent_5x5_t1 --beyin gezinme.ornek_beyin:OrnekHaritaBeyni

SLAM DEĞİL (poz düzeltmesi yok, odometri kayar): yalnız arayüzün örneği. Çerçeve "baslangic": Beyin'in (0, 0, 0)'ı
bırakıldığı gövde pozu; pencere çizimi dünyaya kendisi taşır. Izgara 0,05 m, float 0..1 (0,5 bilinmiyor)."""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gezinme.beyinler import Kesif, bilesik, govdeden_noktaya, noktadan_govdeye  # noqa: E402


class OrnekHaritaBeyni:
    def __init__(self, boyut_m=40.0, cozunurluk_m=0.05):
        self.r = govdeden_noktaya((0.0, 0.0, 0.0))
        self.kesif = Kesif()
        self.coz = cozunurluk_m
        n = int(boyut_m / cozunurluk_m)
        self.orijin = (-boyut_m / 2, -boyut_m / 2)
        self.log = np.zeros((n, n), dtype=np.float32)     # log-odds
        self.montaj = (0.19, 0.0)

    @property
    def poz(self):
        return noktadan_govdeye(self.r)

    def _isle(self, tarama):
        x, y, th = self.poz
        a = np.asarray(tarama["acilar"], dtype=float)
        m = np.asarray([np.nan if d is None else d for d in tarama["mesafeler"]], dtype=float)
        ok = np.isfinite(m)
        c, s = math.cos(th), math.sin(th)
        ox, oy = x + c * self.montaj[0], y + s * self.montaj[0]
        px = ox + m[ok] * np.cos(th + a[ok])
        py = oy + m[ok] * np.sin(th + a[ok])
        n = self.log.shape[0]
        j = ((px - self.orijin[0]) / self.coz).astype(int)
        i = ((py - self.orijin[1]) / self.coz).astype(int)
        sec = (i >= 0) & (i < n) & (j >= 0) & (j < n)
        np.add.at(self.log, (i[sec], j[sec]), 0.9)
        np.clip(self.log, -4, 4, out=self.log)

    def adim(self, t, tarama, artim):
        self.r = bilesik(self.r, artim)
        if tarama is not None:
            self._isle(tarama)
        return self.kesif.adim(tarama, artim)

    def durum(self):
        p = 1.0 / (1.0 + np.exp(-self.log))
        return {"poz": self.poz, "mod": self.kesif.mod, "yol": [], "hedef": None,
                "harita": {"cozunurluk_m": self.coz, "orijin": self.orijin, "izgara": p},
                "ek": {"cerceve": "baslangic"}}
