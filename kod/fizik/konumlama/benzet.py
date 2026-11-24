"""Saf 2B benzetim yardımcıları: ara noktalardan yol, bozuk odometri, MCL'yi yol boyunca koşturma.

Testler ve deney ajanı için. Gerçek poz dizisi + (bozulmuş) odometri artımları üretir; tarama 2B ışın izlemeyle
(`sentetik_tarama`) ya da dışarıdan (MuJoCo LiDAR) gelebilir.
"""

import math

import numpy as np

from .hareket import artim_birlestir
from .tarama import sentetik_tarama


def yol_uret(noktalar, baslangic_aci=0.0, adim_m=0.10, donus_adim=0.20):
    """Ara noktalar [(x, y), ...] -> gerçek pozlar [(x, y, th)]: yerinde dön, sonra düz git (adım adım)."""
    x, y = noktalar[0]
    th = baslangic_aci
    pozlar = [(x, y, th)]
    for (hx, hy) in noktalar[1:]:
        hedef = math.atan2(hy - y, hx - x)
        fark = _sar(hedef - th)
        n = int(math.ceil(abs(fark) / donus_adim))
        for i in range(n):
            th = _sar(th + fark / n)
            pozlar.append((x, y, th))
        d = math.hypot(hx - x, hy - y)
        n = int(math.ceil(d / adim_m))
        for i in range(1, n + 1):
            pozlar.append((x + (hx - x) * i / n, y + (hy - y) * i / n, th))
        x, y = hx, hy
    return pozlar


def goreli(a, b):
    """a pozundan b pozuna gövde çerçevesinde artım (dx, dy, dth)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    c, s = math.cos(a[2]), math.sin(a[2])
    return c * dx + s * dy, -s * dx + c * dy, _sar(b[2] - a[2])


def odometri_noktasi(poz, px):
    """Gövde merkezi pozundan odometrinin izlediği noktanın pozu (gövde ekseninde px kadar ileride / geride)."""
    return poz[0] + px * math.cos(poz[2]), poz[1] + px * math.sin(poz[2]), poz[2]


def odometri_boz(artim, rng, olcek_hata=0.0, donus_hata=0.0, std_ileri=0.0, std_donus=0.0):
    """Enkoder kayması benzetimi: sistematik ölçek / dönüş hatası + Gauss gürültü."""
    dx, dy, dth = artim
    d = math.hypot(dx, dy)
    k = 1.0 + olcek_hata + (rng.normal(0, std_ileri) if std_ileri else 0.0)
    return dx * k, dy * k, dth * (1.0 + donus_hata) + (rng.normal(0, std_donus * abs(dth) + 0.002 * d)
                                                       if std_donus else 0.0)


def yol_boyunca(mcl, harita, pozlar, ozellik, rng, tarama_her=1, olcek_hata=0.03, donus_hata=-0.014,
                std_ileri=0.02, std_donus=0.05, kayip_orani=0.0, ek_engeller=None, dt=0.1):
    """MCL'yi gerçek poz dizisi boyunca koştur. -> [(gercek_poz, Tahmin)] (yalnız tarama alınan adımlar).
    Odometri, gerçek robottaki gibi `mcl.ayar.odometri_noktasi_x` noktasının artımıdır (pozlar gövde merkezi)."""
    sonuc = []
    t = 0.0
    birikmis = (0.0, 0.0, 0.0)
    px = mcl.ayar.odometri_noktasi_x
    for i, poz in enumerate(pozlar):
        if i > 0:
            a = odometri_boz(goreli(odometri_noktasi(pozlar[i - 1], px), odometri_noktasi(poz, px)), rng,
                             olcek_hata, donus_hata, std_ileri, std_donus)
            birikmis = artim_birlestir(birikmis, a)
            t += dt
        if i % tarama_her:
            continue
        tar = sentetik_tarama(harita, poz, ozellik, rng, t=t, kayip_orani=kayip_orani, ek_engeller=ek_engeller)
        tah = mcl.guncelle(tar, artim=birikmis)
        birikmis = (0.0, 0.0, 0.0)
        sonuc.append((poz, tah))
    return sonuc


def konum_hatasi(tah, poz):
    """(xy hatası m, yön hatası rad) tahminin ana modu ile gerçek poz arasında."""
    return math.hypot(tah.x - poz[0], tah.y - poz[1]), abs(_sar(tah.theta - poz[2]))


def _sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi
