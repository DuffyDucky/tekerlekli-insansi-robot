"""Kütle merkezi ve el hesabı devrilme ivmesi (modelden; görev 5'in statik denetimi).

    %V% kod\\fizik\\ucurum\\kutle_merkezi.py   -> sonuc/kutle_merkezi.json

Ani frende öne devrilme sınırı (rijit gövde, teker kaymıyor): öne devrilme için arka teker yükü sıfıra iner:
    düz:        a_dev = g * (x_on - x_km) / z_km
    iniş eğimi θ: a_dev = g * ((x_on - x_km) * cos θ - z_km * sin θ) / z_km   (eğim kütle merkezini öne iter)
x_on = ön teker temas noktası (dingil x), x_km, z_km = kütle merkezi (gövde çerçevesi, yerden).
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402

_yol.dusuk_oncelik()


def main():
    import mujoco as mj
    from ucurum import kosu, sensor
    w = kosu.dunya_kur("duz", sensor.yerlesim("2K", 0.06, 15), 1, (12.0, 15.0, 0.0))[1].dunya
    m, d = w.m, w.d
    for _ in range(300):
        mj.mj_step(m, d)
    # serbest gövdeli kök gövde: en büyük alt ağaç kütlesi
    kok = max(range(1, m.nbody), key=lambda b: (m.body_parentid[b] == 0, m.body_subtreemass[b]))
    km = d.subtree_com[kok].copy()
    poz = d.xpos[kok].copy()
    R = d.xmat[kok].reshape(3, 3)
    yerel = R.T @ (km - poz)
    kutle = float(m.body_subtreemass[kok])
    z_km = float(km[2])
    x_on = 0.185
    g = 9.81
    sonuc = dict(kutle_kg=kutle, km_govde_x_m=float(yerel[0]), km_govde_y_m=float(yerel[1]), km_yerden_z_m=z_km,
                 on_dingil_x_m=x_on, arka_dingil_x_m=-x_on)
    for th in (0.0, 10.0):
        t = math.radians(th)
        a = g * ((x_on - yerel[0]) * math.cos(t) - z_km * math.sin(t)) / z_km
        sonuc["devrilme_ivmesi_m_s2_egim_%d" % th] = round(float(a), 3)
    os.makedirs(_yol.SONUC, exist_ok=True)
    with open(os.path.join(_yol.SONUC, "kutle_merkezi.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, indent=1)
    print(json.dumps(sonuc, indent=1))


if __name__ == "__main__":
    main()
