"""MuJoCo kaydını (gezinme.duzenek.Kayit .npz) SLAM'e açık döngüde yeniden oynat: odometri + taramalar -> HafifSLAM,
tahmin ile yer gerçeğini karşılaştır. Kapalı döngü koşusu gerekmeden SLAM ayarlarını gerçek fizik verisinde sınar.

    py -3 -m kesif.tekrar sonuc/ham/mujoco/labirent_17x17_t1_t0.npz [anahtar=deger ...]
      anahtar: SlamAyari alanı (ör. yaz_w_maks=0.5) ya da e.<EslestirmeAyari alanı> (ör. e.d_maks=0.2)
"""

import math
import sys

import numpy as np


def _goreli(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    c, s = math.cos(a[2]), math.sin(a[2])
    return (c * dx + s * dy, -s * dx + c * dy, (b[2] - a[2] + math.pi) % (2 * math.pi) - math.pi)


def tekrar(yol, degis=None, sahne=None, t0=None):
    from gezinme.duzenek import kayit_oku
    from .sahne import dunyadan_beyne, sahne_yukle
    from .slam import HafifSLAM, SlamAyari
    m, d = kayit_oku(yol)
    s = sahne_yukle(sahne or m["sahne"])
    A = SlamAyari()
    for k, v in (degis or {}).items():
        h = A.eslestirme if k.startswith("e.") else A
        k = k[2:] if k.startswith("e.") else k
        setattr(h, k, type(getattr(h, k))(v))
    sl = HafifSLAM(A)
    T, O, G = d["t"], d["odo"], d["gercek"]
    TT, MM, ac = d["tarama_t"], d["tarama_mm"], d["acilar"]
    if t0 is None:
        # kayıt satır saati koşu başına göre (t - t0), tarama saati dünya saati: t0 = devreye alma süresi
        t0 = float((m.get("sonuc") or {}).get("t0", 0.5))
    T = T + t0
    k = 0
    hata = []
    for i in range(1, len(T)):
        sl.odometri(_goreli(O[i - 1], O[i]), T[i])
        # bu adıma kadar tamamlanmış taramalar (tur sonu = t + 0,1)
        while k < len(TT) and TT[k] + 0.1 <= T[i] + 1e-9:
            mm = MM[k].astype(float) / 1000.0
            mm[MM[k] == 0] = np.nan
            sl.tarama_isle({"t": float(TT[k]), "acilar": ac, "mesafeler": mm}, T[i])
            k += 1
            gx, gy = dunyadan_beyne(s, G[i, 0], G[i, 1])
            gth = G[i, 2] - s.start_poz[2]
            p = sl.poz
            hata.append((T[i], math.hypot(gx - p[0], gy - p[1]),
                         math.degrees((gth - p[2] + math.pi) % (2 * math.pi) - math.pi)))
    H = np.array(hata)
    return {"poz_hata_maks": round(float(H[:, 1].max()), 3), "poz_hata_son": round(float(H[-1, 1]), 3),
            "poz_hata_ort": round(float(H[:, 1].mean()), 3), "yon_son": round(float(H[-1, 2]), 2),
            "k_don": round(sl.k_don, 3), "k_il": round(sl.k_il, 3), "ist": sl.istatistik}, H


if __name__ == "__main__":
    from ._yol import dusuk_oncelik
    dusuk_oncelik()
    deg = dict(a.split("=") for a in sys.argv[2:])
    print(tekrar(sys.argv[1], {k: float(v) for k, v in deg.items()})[0])
