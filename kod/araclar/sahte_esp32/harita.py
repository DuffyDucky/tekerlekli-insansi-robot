"""Üstten bakışlı 2B oda haritası: duvar parçaları, kutu ve daire engeller; ışın izleme ve çarpışma.

Harita düz bir JSON dosyasıdır (`kod/araclar/haritalar/*.json`, biçim `SIMULASYON.md`). Birim metre, x sağa,
y yukarı (haritanın kendi çerçevesi), açı derece, sola (saat yönü tersine) +.
Yalnız standart kitaplık; deterministik.
"""

import json
import math
import os

HARITA_KLASORU = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "haritalar")


class HaritaHatasi(ValueError):
    pass


class Harita:
    def __init__(self, veri, ad=None):
        self.veri = veri
        self.ad = ad or veri.get("ad", "adsiz")
        try:
            self.genislik, self.yukseklik = (float(v) for v in veri["boyut_m"])
        except (KeyError, TypeError, ValueError):
            raise HaritaHatasi("boyut_m: [genislik, yukseklik] gerekli")
        self.parcalar = []          # (x1, y1, x2, y2)
        self.daireler = []          # (x, y, r)
        for d in veri.get("duvarlar", []):
            if len(d) != 4:
                raise HaritaHatasi("duvar [x1, y1, x2, y2] olmalı: %r" % (d,))
            self.parcalar.append(tuple(float(v) for v in d))
        for e in veri.get("engeller", []):
            tur = e.get("tur")
            if tur == "kutu":
                x, y, g, h = float(e["x"]), float(e["y"]), float(e["g"]), float(e["d"])
                k = [(x, y), (x + g, y), (x + g, y + h), (x, y + h)]
                for i in range(4):
                    self.parcalar.append(k[i] + k[(i + 1) % 4])
            elif tur == "daire":
                self.daireler.append((float(e["x"]), float(e["y"]), float(e["r"])))
            else:
                raise HaritaHatasi("bilinmeyen engel türü: %r" % (tur,))
        w, h = self.genislik, self.yukseklik
        if veri.get("cevre_duvari", True):
            self.parcalar += [(0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)]
        b = veri.get("baslangic", {})
        self.baslangic = (float(b.get("x", w / 2)), float(b.get("y", h / 2)), math.radians(float(b.get("aci_derece", 0))))

    @classmethod
    def dosyadan(cls, yol):
        if not os.path.isabs(yol) and not os.path.exists(yol):
            aday = os.path.join(HARITA_KLASORU, yol if yol.endswith(".json") else yol + ".json")
            if os.path.exists(aday):
                yol = aday
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
        return cls(veri, ad=veri.get("ad") or os.path.splitext(os.path.basename(yol))[0])

    def sozluk(self):
        """Görünüm için: bütün parçalar ve daireler (çevre duvarı dahil)."""
        return {"ad": self.ad, "boyut_m": [self.genislik, self.yukseklik],
                "parcalar": [list(p) for p in self.parcalar], "daireler": [list(d) for d in self.daireler],
                "aciklama": self.veri.get("aciklama", "")}

    # ------------------------------------------------------------ ışın izleme

    def isin(self, x, y, aci, en_cok):
        """(x, y)'den `aci` yönünde en yakın yüzey: (uzaklık, geliş açısı rad) ya da None.

        Geliş açısı ışın ile yüzey normali arasındaki açı (0 = dik).
        """
        dx, dy = math.cos(aci), math.sin(aci)
        en_iyi = None
        for (x1, y1, x2, y2) in self.parcalar:
            ex, ey = x2 - x1, y2 - y1
            pay = dx * ey - dy * ex
            if abs(pay) < 1e-12:
                continue
            t = ((x1 - x) * ey - (y1 - y) * ex) / pay
            u = ((x1 - x) * dy - (y1 - y) * dx) / pay
            if t <= 1e-9 or t > en_cok or u < 0.0 or u > 1.0:
                continue
            if en_iyi is None or t < en_iyi[0]:
                boy = math.hypot(ex, ey)
                nx, ny = -ey / boy, ex / boy
                gelis = math.acos(min(1.0, abs(dx * nx + dy * ny)))
                en_iyi = (t, gelis)
        for (cx, cy, r) in self.daireler:
            fx, fy = x - cx, y - cy
            b = fx * dx + fy * dy
            c = fx * fx + fy * fy - r * r
            ayirt = b * b - c
            if ayirt < 0:
                continue
            t = -b - math.sqrt(ayirt)
            if t <= 1e-9 or t > en_cok:
                continue
            if en_iyi is None or t < en_iyi[0]:
                hx, hy = x + dx * t, y + dy * t
                nx, ny = (hx - cx) / r, (hy - cy) / r
                gelis = math.acos(min(1.0, abs(dx * nx + dy * ny)))
                en_iyi = (t, gelis)
        return en_iyi

    # ------------------------------------------------------------ çarpışma

    def cokgen_carpar(self, kose):
        """Dışbükey çokgen (köşe listesi) herhangi bir duvara / engele değiyor ya da içine giriyor mu?"""
        n = len(kose)
        kenarlar = [kose[i] + kose[(i + 1) % n] for i in range(n)]
        for p in self.parcalar:
            for k in kenarlar:
                if _parca_kesisir(p, k):
                    return True
            if _icinde(kose, p[0], p[1]) or _icinde(kose, p[2], p[3]):
                return True
        for (cx, cy, r) in self.daireler:
            if _icinde(kose, cx, cy):
                return True
            for k in kenarlar:
                if _nokta_parca_uzaklik(cx, cy, k) < r:
                    return True
        return False


def _yon(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


_EPS = 1e-12


def _isaret(d):
    return 0 if abs(d) <= _EPS else (1 if d > 0 else -1)


def _parca_uzerinde(ax, ay, bx, by, px, py):
    """p, a-b doğrusu üzerindeyken (eşdoğrusal) parçanın sınır kutusunda mı?"""
    return (min(ax, bx) - _EPS <= px <= max(ax, bx) + _EPS) and (min(ay, by) - _EPS <= py <= max(ay, by) + _EPS)


def _parca_kesisir(p, q):
    """İki parça kesişiyor ya da değiyor mu (eşdoğrusal üst üste binme ve uç değmesi dahil)."""
    ax, ay, bx, by = p
    cx, cy, dx, dy = q
    d1 = _isaret(_yon(cx, cy, dx, dy, ax, ay))
    d2 = _isaret(_yon(cx, cy, dx, dy, bx, by))
    d3 = _isaret(_yon(ax, ay, bx, by, cx, cy))
    d4 = _isaret(_yon(ax, ay, bx, by, dx, dy))
    if d1 * d2 < 0 and d3 * d4 < 0:
        return True
    return ((d1 == 0 and _parca_uzerinde(cx, cy, dx, dy, ax, ay)) or
            (d2 == 0 and _parca_uzerinde(cx, cy, dx, dy, bx, by)) or
            (d3 == 0 and _parca_uzerinde(ax, ay, bx, by, cx, cy)) or
            (d4 == 0 and _parca_uzerinde(ax, ay, bx, by, dx, dy)))


def _icinde(kose, x, y):
    n = len(kose)
    isaret = 0
    for i in range(n):
        ax, ay = kose[i]
        bx, by = kose[(i + 1) % n]
        d = _yon(ax, ay, bx, by, x, y)
        if d == 0:
            continue
        s = 1 if d > 0 else -1
        if isaret == 0:
            isaret = s
        elif s != isaret:
            return False
    return True


def _nokta_parca_uzaklik(x, y, p):
    ax, ay, bx, by = p
    ex, ey = bx - ax, by - ay
    boy2 = ex * ex + ey * ey
    t = 0.0 if boy2 == 0 else max(0.0, min(1.0, ((x - ax) * ex + (y - ay) * ey) / boy2))
    return math.hypot(x - (ax + t * ex), y - (ay + t * ey))


def harita_listesi():
    return sorted(f[:-5] for f in os.listdir(HARITA_KLASORU) if f.endswith(".json"))
