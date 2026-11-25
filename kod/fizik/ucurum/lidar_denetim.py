"""Kısa denetim: 2B LiDAR (x 0,19, z 0,295, yatay) aşağı inen merdiveni görüyor mu?

Aynı robot pozu (en öndeki teker kenardan 0,30 m geride, kenara dik bakıyor), iki sahne: `merdiven_17x30` ve `duz`
(merdivensiz, aynı acik_alan haritası; x = 20'de duvar). Anlık tarama, gürültü ve yuvarlama kapalı. Ön +-60 derece
sektördeki ölçümler karşılaştırılır; ayrıca tarama düzlemi 1,5 derece öne eğik (dosyadaki üst sınır) durum.

    %V% kod\\fizik\\ucurum\\lidar_denetim.py    -> sonuc/lidar_denetim.json + ekrana özet
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402


def tarama(sahne_ad, egim=0.0):
    import numpy as np
    import lidar as L
    from ucurum import kosu, sensor, sahne as S
    bas = (S.E - 0.30 - 0.185, S.Y0, 0.0)
    sz, c, e, sd, rng = kosu.dunya_kur(sahne_ad, sensor.yerlesim("2K", 0.06, 15), 0, baslangic=bas)
    c.dunya.adim(0.3)
    lid = L.SanalLidar(c.dunya, gurultu_sigma_m=0.0, cozunurluk_m=0.0, kor_maske=True, duzlem_egimi_derece=egim)
    t = lid.anlik_tarama()
    a = np.degrees(np.array(t["acilar"]))
    m = np.array([np.nan if v is None else v for v in t["mesafeler"]], dtype=float)
    on = np.abs(a) <= 60.0
    return a[on], m[on]


def main():
    out = {}
    for egim in (0.0, 1.5):
        am, mm = tarama("merdiven_17x30", egim)
        ad, md = tarama("duz", egim)
        olc_m = int((~(mm != mm)).sum())
        olc_d = int((~(md != md)).sum())
        ikisi = (mm == mm) & (md == md)
        fark = float(abs(mm[ikisi] - md[ikisi]).max()) if ikisi.any() else None
        en_yakin_m = float(mm[mm == mm].min()) if olc_m else None
        out["egim_%.1f" % egim] = dict(isin=len(am), olcum_merdiven=olc_m, olcum_duz=olc_d, en_yakin_merdiven_m=en_yakin_m,
                                       en_yakin_duz_m=float(md[md == md].min()) if olc_d else None,
                                       en_buyuk_fark_mm=None if fark is None else round(fark * 1000, 3),
                                       kenar_uzakligi_lidar_m=round(16.0 - (16.0 - 0.30 - 0.185 + 0.19), 3))
        print("egim %.1f: on +-60 derece %d isin; merdivenli %d olcum (en yakin %s m), duz %d olcum; en buyuk fark %s mm"
              % (egim, len(am), olc_m, en_yakin_m, olc_d, out["egim_%.1f" % egim]["en_buyuk_fark_mm"]))
    os.makedirs(_yol.SONUC, exist_ok=True)
    with open(os.path.join(_yol.SONUC, "lidar_denetim.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    _yol.dusuk_oncelik()
    main()
