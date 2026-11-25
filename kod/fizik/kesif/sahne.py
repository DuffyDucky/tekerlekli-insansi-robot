"""Labirent sahnesi yükleme (2B harita JSON + `labirent` alanı) ve beynin görmesine izin verilen bilgi.

Biçim (labirent ajanının 3B JSON'undaki `labirent` alanıyla aynı adlar hedeflendi; farklı gelirse `_labirent_oku`
uyarlanır). Tanınan anahtarlar:
    labirent.start.cizgi | start_cizgisi : [x1, y1, x2, y2]   (dünya, m)
    labirent.finish.cizgi | finish_cizgisi : [x1, y1, x2, y2]
    labirent.start_poz | start.poz | baslangic : [x, y, aci_derece] ya da {"x", "y", "aci_derece"}
    labirent.cozum_yolu | cozum : [[x, y], ...]
Dış yön: START için başlangıç pozunun gerisi; FINISH için çizginin labirent merkezinden uzak yanı.

Beyne verilen tek şey START çizgisinin başlangıç gövde çerçevesindeki yeri (`beyin_start_cizgisi`).
"""

import json
import math
import os
from dataclasses import dataclass, field

import numpy as np

from ._yol import HARITALAR, SAHNELER, KESIF


@dataclass
class Sahne:
    ad: str
    veri: dict                      # 2B harita JSON
    start_poz: tuple                # dünya (x, y, th) gövde merkezi
    start_cizgi: tuple              # ((x1, y1), (x2, y2))
    finish_cizgi: tuple
    start_dis: tuple                # birim normal, dışarı
    finish_dis: tuple
    cozum: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    sahne3b: dict = None            # labirent ajanının 3B sahne sözlüğü (hakem için), yoksa None


def _cizgi(v):
    if v is None:
        return None
    if isinstance(v, dict):
        for k in ("cizgi", "line", "uclar"):
            if k in v:
                return _cizgi(v[k])
        if "p1" in v and "p2" in v:
            return (tuple(map(float, v["p1"])), tuple(map(float, v["p2"])))
        return None
    v = list(v)
    if len(v) == 4 and not isinstance(v[0], (list, tuple)):
        return ((float(v[0]), float(v[1])), (float(v[2]), float(v[3])))
    if len(v) == 2:
        return (tuple(map(float, v[0])), tuple(map(float, v[1])))
    return None


def _poz(v):
    if v is None:
        return None
    if isinstance(v, dict):
        if "x" in v:
            th = v.get("aci_derece", None)
            th = math.radians(float(th)) if th is not None else float(v.get("aci_rad", v.get("th", 0.0)))
            return (float(v["x"]), float(v["y"]), th)
        for k in ("poz", "pose"):
            if k in v:
                return _poz(v[k])
        return None
    v = list(v)
    th = float(v[2]) if len(v) > 2 else 0.0
    if abs(th) > 2 * math.pi + 0.01:
        th = math.radians(th)
    return (float(v[0]), float(v[1]), th)


def _dis_normal(cizgi, ic_nokta):
    (x1, y1), (x2, y2) = cizgi
    tx, ty = x2 - x1, y2 - y1
    L = math.hypot(tx, ty) or 1.0
    nx, ny = ty / L, -tx / L
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    if (ic_nokta[0] - mx) * nx + (ic_nokta[1] - my) * ny > 0:
        nx, ny = -nx, -ny
    return (nx, ny)


def _bul(ad):
    if isinstance(ad, dict):
        return ad, ad.get("ad", "adsiz")
    if os.path.exists(str(ad)):
        yol = str(ad)
    else:
        aday = [os.path.join(HARITALAR, ad + ".json"), os.path.join(KESIF, "testler", "labirentler", ad + ".json"),
                os.path.join(SAHNELER, ad + ".json")]
        yol = next((a for a in aday if os.path.exists(a)), None)
        if yol is None:
            raise FileNotFoundError("sahne bulunamadı: %s" % ad)
    with open(yol, encoding="utf-8") as f:
        v = json.load(f)
    return v, v.get("ad") or os.path.splitext(os.path.basename(yol))[0]


def sahne_yukle(ad):
    """ad: harita adı / yolu / 2B sözlük ya da (2B harita sözlüğü, 3B sahne sözlüğü) çifti (labirent.uretici.sahne_kur)."""
    s3 = None
    if isinstance(ad, (tuple, list)) and len(ad) >= 2 and isinstance(ad[0], dict):
        veri, isim = ad[0], ad[0].get("ad", "adsiz")
        s3 = ad[1]
    else:
        veri, isim = _bul(ad)
    lab = dict(veri.get("labirent") or {})
    # 2B haritada labirent alanı yoksa aynı adlı 3B sahnede ara
    if not lab and s3 is None and not isinstance(ad, dict):
        yol3 = os.path.join(SAHNELER, isim + ".json")
        if os.path.exists(yol3):
            with open(yol3, encoding="utf-8") as f:
                s3 = json.load(f)
    if not lab and s3 is not None:
        lab = dict(s3.get("labirent") or {})
    st = lab.get("start") if isinstance(lab.get("start"), dict) else {}
    fn = lab.get("finish") if isinstance(lab.get("finish"), dict) else {}
    sc = _cizgi(lab.get("start_cizgisi") or st or lab.get("start"))
    fc = _cizgi(lab.get("finish_cizgisi") or fn or lab.get("finish"))
    sp = _poz(lab.get("start_poz") or st.get("poz") or veri.get("baslangic"))
    if sp is None:
        b = veri.get("baslangic", {})
        sp = (float(b.get("x", 0)), float(b.get("y", 0)), math.radians(float(b.get("aci_derece", 0))))
    w, h = (float(v) for v in veri.get("boyut_m", [0, 0]))
    merkez = lab.get("merkez") or [w / 2, h / 2]
    if lab.get("sinir"):
        x0, y0, x1, y1 = lab["sinir"]
        merkez = [(x0 + x1) / 2, (y0 + y1) / 2]
    if sc is None:
        # START çizgisi verilmemiş: robotun 0,4 m gerisinde 1,6 m'lik dik çizgi (VARSAYIM)
        c, s = math.cos(sp[2]), math.sin(sp[2])
        bx, by = sp[0] - 0.4 * c, sp[1] - 0.4 * s
        sc = ((bx - 0.8 * s, by + 0.8 * c), (bx + 0.8 * s, by - 0.8 * c))
    sd = _dis_normal(sc, (sp[0], sp[1]))
    fd = _dis_normal(fc, merkez) if fc is not None else (0.0, 0.0)
    if st.get("ic_normal"):
        sd = (-float(st["ic_normal"][0]), -float(st["ic_normal"][1]))
    if fn.get("ic_normal"):
        fd = (-float(fn["ic_normal"][0]), -float(fn["ic_normal"][1]))
    coz = lab.get("cozum_yolu") or lab.get("cozum") or []
    return Sahne(ad=isim, veri=veri, start_poz=sp, start_cizgi=sc, finish_cizgi=fc, start_dis=sd, finish_dis=fd,
                 cozum=[tuple(map(float, p[:2])) for p in coz], meta={k: v for k, v in lab.items()
                                                                         if k not in ("cozum_yolu", "cozum")},
                 sahne3b=s3)


def dunyadan_beyne(sahne, x, y):
    """Dünya noktasını başlangıç gövde çerçevesine (beyin harita çerçevesi) çevir."""
    sx, sy, sth = sahne.start_poz
    c, s = math.cos(sth), math.sin(sth)
    dx, dy = np.asarray(x) - sx, np.asarray(y) - sy
    return c * dx + s * dy, -s * dx + c * dy


def beyinden_dunyaya(sahne, x, y):
    sx, sy, sth = sahne.start_poz
    c, s = math.cos(sth), math.sin(sth)
    x, y = np.asarray(x), np.asarray(y)
    return sx + c * x - s * y, sy + s * x + c * y


def beyin_start_cizgisi(sahne):
    (x1, y1), (x2, y2) = sahne.start_cizgi
    a = dunyadan_beyne(sahne, x1, y1)
    b = dunyadan_beyne(sahne, x2, y2)
    return ((float(a[0]), float(a[1])), (float(b[0]), float(b[1])))
