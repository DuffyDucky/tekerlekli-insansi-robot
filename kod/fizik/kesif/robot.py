"""Robot ölçüleri ve kinematik sınırlar (keşif beyni + 2B benzetici için tek yer).

Kaynak: kod/ortak/robot_parametreleri.json (taban 0,520 x 0,525 m, dingil yarı 0,185, iz 0,432 / firmware 0,426,
teker azami 0,39 m/s TAHMİN, ivme 0,5 / fren 1,8 m/s^2) ve `kod/fizik/lidar_ozellik.json` (montaj x 0,190 m).
Gövde çerçevesi: x ileri, y sol; gövde merkezi = taban dikdörtgeninin merkezi. Arka çeker dingil gövde merkezinin
0,185 m gerisinde; yerinde dönüş onun çevresinde. Gezinme ajanı kesin ölçüleri `kod/fizik/gezinme/BENIOKU.md`
başına yazınca `gezinmeden_oku()` onları alır (biçim bilinmediği için yalnız tanınan anahtarlar).
"""

import math
import os
import re
from dataclasses import dataclass, replace

from ._yol import FIZIK


@dataclass
class RobotOlcu:
    genislik_m: float = 0.52          # taban (y)
    derinlik_m: float = 0.525         # taban (x)
    dingil_x_m: float = -0.185        # arka çeker dingilin ortası, gövde çerçevesinde
    lidar_x_m: float = 0.190
    lidar_y_m: float = 0.0
    v_seyir: float = 0.25             # m/s (brief: ≈ 0,25 seyir)
    v_tavan: float = 0.39             # m/s teker azami (TAHMİN)
    w_tavan: float = 1.8              # rad/s ≈ 2 v_tavan / iz
    ivme: float = 0.5                 # m/s^2 düz sürüş
    fren: float = 1.8                 # m/s^2
    w_ivme: float = 3.0               # rad/s^2 (VARSAYIM)
    iz_m: float = 0.426

    @property
    def yari_genislik(self):
        return self.genislik_m / 2

    @property
    def on_x(self):
        return self.derinlik_m / 2

    @property
    def arka_x(self):
        return -self.derinlik_m / 2

    @property
    def cevrel_yaricap(self):
        return math.hypot(self.derinlik_m / 2, self.genislik_m / 2)

    @property
    def supurme_yaricapi(self):
        """Arka dingil çevresinde yerinde dönüşte gövdenin süpürdüğü daire yarıçapı (araştırma notu §3)."""
        a = self.on_x - self.dingil_x_m
        b = self.dingil_x_m - self.arka_x
        return max(math.hypot(a, self.yari_genislik), math.hypot(b, self.yari_genislik))

    def kose_noktalari(self):
        """Gövde çerçevesinde taban dikdörtgeninin 4 köşesi."""
        hx, hy = self.derinlik_m / 2, self.genislik_m / 2
        return [(hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)]


VARSAYILAN = RobotOlcu()


def gezinmeden_oku(temel=VARSAYILAN):
    """`kod/fizik/gezinme/BENIOKU.md` varsa içindeki `anahtar = değer` / `anahtar: değer` satırlarından tanınanları al."""
    yol = os.path.join(FIZIK, "gezinme", "BENIOKU.md")
    if not os.path.exists(yol):
        return temel
    try:
        with open(yol, encoding="utf-8") as f:
            metin = f.read()
    except OSError:
        return temel
    degis = {}
    for alan in ("genislik_m", "derinlik_m", "dingil_x_m", "lidar_x_m", "v_seyir", "v_tavan", "w_tavan", "ivme"):
        m = re.search(r"`?%s`?\s*[:=]\s*(-?[0-9]+(?:[.,][0-9]+)?)" % alan, metin)
        if m:
            degis[alan] = float(m.group(1).replace(",", "."))
    return replace(temel, **degis) if degis else temel
