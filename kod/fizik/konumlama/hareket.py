"""Odometri hareket modeli (gürültülü örnekleme).

Girdi gövde çerçevesinde artımlı hareket (dx, dy, dtheta): önceki pozun çerçevesinde yer değiştirme ve dönüş.
(v, w, dt) verilirse sabit eğrilikli yayla artıma çevrilir (`hizdan_artim`).

Gürültü (her parçacığa ayrı, Gauss; std'ler mutlak artıma orantılı + taban):
    sigma_x  = a_ileri  * |d| + a_ileri_donus * |dtheta| + taban_xy
    sigma_y  = a_yanal  * |d| + a_ileri_donus * |dtheta| + taban_xy
    sigma_th = a_donus  * |dtheta| + a_donus_ileri * |d| + taban_th
  d = hypot(dx, dy). Dört tekerli kızak yönlendirmede dönüşte teker kayar, enkoder yalnız tekerin dönüşünü görür:
  dönüş gürültüsü (a_donus) ve yanal kayma (a_yanal) bilerek geniş. Sistematik hata (iz genişliği farkı: 360°'de
  -5°, `SIMULASYON.md` (e)) ortalaması sıfır gürültü değildir; std'ler onu da örtecek kadar geniş seçildi.
"""

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class HareketGurultusu:
    a_ileri: float = 0.05         # m/m
    a_yanal: float = 0.03         # m/m
    a_ileri_donus: float = 0.01   # m/rad
    a_donus: float = 0.10         # rad/rad
    a_donus_ileri: float = 0.05   # rad/m
    taban_xy: float = 0.005       # m (her güncellemede)
    taban_th: float = 0.005       # rad


def hizdan_artim(v, w, dt):
    """(v m/s, w rad/s, dt s) -> gövde çerçevesinde (dx, dy, dtheta)."""
    dth = w * dt
    if abs(dth) < 1e-9:
        return v * dt, 0.0, dth
    r = v / w
    return r * math.sin(dth), r * (1 - math.cos(dth)), dth


def artim_birlestir(a, b):
    """İki gövde artımını ardışık birleştir (a sonra b)."""
    dx1, dy1, t1 = a
    dx2, dy2, t2 = b
    c, s = math.cos(t1), math.sin(t1)
    return dx1 + c * dx2 - s * dy2, dy1 + s * dx2 + c * dy2, t1 + t2


def uygula(x, y, th, artim, gurultu, rng):
    """Parçacıklara artımı gürültüyle uygula (yerinde değil, yeni diziler döner)."""
    dx, dy, dth = artim
    n = np.shape(x)[0]
    d = math.hypot(dx, dy)
    g = gurultu
    if g is None:
        ex = ey = et = np.zeros(n)
    else:
        sx = g.a_ileri * d + g.a_ileri_donus * abs(dth) + g.taban_xy
        sy = g.a_yanal * d + g.a_ileri_donus * abs(dth) + g.taban_xy
        st = g.a_donus * abs(dth) + g.a_donus_ileri * d + g.taban_th
        # ileri / yanal gürültü hareket yönü boyunca ve ona dik (gövde x/y değil)
        if d > 1e-9:
            ux, uy = dx / d, dy / d
        else:
            ux, uy = 1.0, 0.0
        e_il = rng.normal(0.0, sx, n)
        e_ya = rng.normal(0.0, sy, n)
        ex = ux * e_il - uy * e_ya
        ey = uy * e_il + ux * e_ya
        et = rng.normal(0.0, st, n)
    ddx, ddy = dx + ex, dy + ey
    c, s = np.cos(th), np.sin(th)
    yx = x + c * ddx - s * ddy
    yy = y + s * ddx + c * ddy
    yth = _sar(th + dth + et)
    return yx, yy, yth


def _sar(a):
    return (a + np.pi) % (2 * np.pi) - np.pi
