"""Tek durağan taramadan harita sınıflaması (hareketsiz): düzenli poz kafesinde tarama eşleştirme.

Her harita için serbest alanda `xy_adim` aralıklı noktalar x `aci_adim_derece` aralıklı yönler denenir; her pozun
log-olasılığı MCL ile aynı ölçüm modelinden (varsayılan "alan") gelir. Harita puanı, poz üzerinde düzgün önselle
marjinal olabilirlik: log mean_poz exp(l). Olasılıklar bu puanların softmax'ı (eşit harita önseli). En iyi poz
çevresinde küçük bir yerel arama (yarım adım) yapılır.

Kafes kaba olduğundan (0,2 m / 3°) uzak duvarlarda uç kayması büyür: sigma_isabet MCL'dekinden geniş (0,25 m)
alınır. Aynı kafes MCL'nin küresel başlangıcında da kullanılır (`CokHaritaliMCL`, `baslangic="kafes"`).
"""

import math

import numpy as np

from .harita2b import haritalari_yukle
from .olcum import OlcumParametreleri, log_olasilik
from .tarama import LidarOzellik, tarama_hazirla


def kafes_olcum_parametreleri():
    """Kaba kafes için varsayılan ölçüm parametreleri (geniş sigma, boş ışın yok: hız)."""
    return OlcumParametreleri(sigma_isabet=0.25, bos_isin_sayisi=0)


def kafes_adimi(harita, xy_adim, en_cok_nokta):
    """Büyük haritada kafes aralığını nokta tavanına göre büyüt."""
    if en_cok_nokta:
        xy_adim = max(xy_adim, math.sqrt(harita.serbest_alan_m2() / en_cok_nokta))
    return xy_adim


def kafes_puanla(harita, hazir, p, xy_adim=0.2, aci_adim_derece=3.0, en_cok_nokta=4000, parca=400_000):
    """Serbest alan kafesindeki her pozun log-olasılığı. -> X, Y, T, L (düz diziler), kullanılan xy adımı.

    en_cok_nokta: harita başına en çok (x, y) noktası; aşılırsa aralık büyütülür (30 x 30 m açık alan gibi)."""
    acilar = np.radians(np.arange(-180.0, 180.0, aci_adim_derece))
    xy_adim = kafes_adimi(harita, xy_adim, en_cok_nokta)
    gx, gy = harita.serbest_izgara_noktalari(xy_adim)
    if gx.size == 0:
        gx, gy, _ = harita.rastgele_serbest(200, np.random.default_rng(0))
    X = np.repeat(gx, acilar.size)
    Y = np.repeat(gy, acilar.size)
    T = np.tile(acilar, gx.size)
    L = np.empty(X.size)
    adim = max(1, parca // max(1, hazir.acilar.size))
    for b in range(0, X.size, adim):
        s = slice(b, b + adim)
        L[s] = log_olasilik(harita, X[s], Y[s], T[s], hazir, p)
    return X, Y, T, L, xy_adim


def _lse(a):
    m = float(np.max(a))
    return m + math.log(float(np.sum(np.exp(a - m))))


def tek_taramadan_sinifla(haritalar, tarama, ozellik=None, olcum=None, xy_adim=0.2, aci_adim_derece=3.0,
                          karar_esigi=0.5, serbest_pay=0.20, izgara_cozunurluk=0.05, en_cok_nokta=4000):
    """-> {olasiliklar, en_olasi, kararsiz, fark, pozlar: {ad: (x, y, theta, log_olasilik)}, puanlar, poz_sayilari}"""
    haritalar = haritalari_yukle(haritalar)
    ozellik = ozellik if ozellik is not None else LidarOzellik.varsa_dosyadan()
    p = olcum if olcum is not None else kafes_olcum_parametreleri()
    hazir = tarama_hazirla(tarama, ozellik, p.isin_sayisi)
    puanlar, pozlar, sayilar = {}, {}, {}
    for h in haritalar:
        h.hazirla(izgara_cozunurluk, serbest_pay)
        X, Y, T, L, adim = kafes_puanla(h, hazir, p, xy_adim, aci_adim_derece, en_cok_nokta)
        puanlar[h.ad] = _lse(L) - math.log(L.size)
        i = int(np.argmax(L))
        en = (X[i], Y[i], T[i], L[i])
        # yerel arama: yarım adım çevresinde 5 x 5 x 5
        dx = np.linspace(-adim / 2, adim / 2, 5)
        da = np.radians(np.linspace(-aci_adim_derece / 2, aci_adim_derece / 2, 5))
        ox, oy, oa = np.meshgrid(dx, dx, da, indexing="ij")
        x2, y2, t2 = en[0] + ox.ravel(), en[1] + oy.ravel(), en[2] + oa.ravel()
        l2 = log_olasilik(h, x2, y2, t2, hazir, p)
        j = int(np.argmax(l2))
        if l2[j] > en[3]:
            en = (x2[j], y2[j], t2[j], l2[j])
        pozlar[h.ad] = (float(en[0]), float(en[1]), float((en[2] + math.pi) % (2 * math.pi) - math.pi),
                        float(en[3]))
        sayilar[h.ad] = int(X.size)
    ad = list(puanlar)
    v = np.array([puanlar[a] for a in ad])
    P = np.exp(v - v.max())
    P /= P.sum()
    olas = {a: float(q) for a, q in zip(ad, P)}
    sirali = sorted(olas.items(), key=lambda kv: -kv[1])
    fark = sirali[0][1] - (sirali[1][1] if len(sirali) > 1 else 0.0)
    return dict(olasiliklar=olas, en_olasi=sirali[0][0], kararsiz=bool(fark < karar_esigi), fark=float(fark),
                pozlar=pozlar, puanlar=puanlar, poz_sayilari=sayilar)
