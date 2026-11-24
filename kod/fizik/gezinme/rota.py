"""Koridor rotaları: duraklar (kapı hizasında orta hat noktaları) ve orta hat çizgesinde en kısa yol (saf Python).

Duraklar sahne JSON'undan türetilir (`kod/fizik/sahneler/koridor_N.json`, `ozellikler` içindeki `kapi_kapali` /
`kapi_acik`): her kapının `hat` (orta_hat / orta_hat_yan_kol) üzerinde `s_m` uzaklığındaki noktası. Adlar
`k<N>_kapi_<i>`: i = 1.. kapının başlangıçtan rota uzaklığına göre sırası. Ayrıca `k<N>_bas`, `k<N>_son` (orta hat uçları)
ve T'de `k<N>_kol_son` (yan kol ucu). Göreli ad (`kapi_3`, `son`) koridor bilinince `k<N>_` ile tamamlanır.
"""

import heapq
import json
import math
import os

_SAHNELER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sahneler")


def sahne(ad):
    with open(os.path.join(_SAHNELER, ad + ".json"), encoding="utf-8") as f:
        return json.load(f)


def _nokta(P, s):
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= L:
            t = s / L if L else 0.0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        s -= L
    return tuple(P[-1])


class Cizge:
    """Orta hat çizgesi: orta_hat ve (varsa) orta_hat_yan_kol çoklu çizgileri; yan kolun başı ana hatta ise birleşir."""

    def __init__(self, s):
        self.hatlar = {"orta_hat": [tuple(p) for p in s["orta_hat"]]}
        if s.get("orta_hat_yan_kol"):
            self.hatlar["orta_hat_yan_kol"] = [tuple(p) for p in s["orta_hat_yan_kol"]]
        self.dugum = []          # (x, y)
        self.kenar = {}          # i -> [(j, L)]
        self.parcalar = []       # (i, j) çizge kenarları (izdüşüm için)
        ana = self.hatlar["orta_hat"]
        if "orta_hat_yan_kol" in self.hatlar:
            J = self.hatlar["orta_hat_yan_kol"][0]
            ana = self._bol(ana, J)
            self.hatlar["orta_hat"] = ana
        for ad, P in self.hatlar.items():
            onceki = None
            for p in P:
                i = self._dugum_ekle(p)
                if onceki is not None and onceki != i:
                    self._kenar_ekle(onceki, i)
                onceki = i

    @staticmethod
    def _bol(P, J):
        """J noktası P'nin bir parçasının üstündeyse orada köşe ekle."""
        out = [P[0]]
        for a, b in zip(P, P[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy
            t = ((J[0] - a[0]) * dx + (J[1] - a[1]) * dy) / L2 if L2 else 0
            if 1e-6 < t < 1 - 1e-6 and math.hypot(a[0] + t * dx - J[0], a[1] + t * dy - J[1]) < 1e-6:
                out.append(tuple(J))
            out.append(b)
        return out

    def _dugum_ekle(self, p):
        for i, q in enumerate(self.dugum):
            if math.hypot(p[0] - q[0], p[1] - q[1]) < 1e-6:
                return i
        self.dugum.append((float(p[0]), float(p[1])))
        self.kenar[len(self.dugum) - 1] = []
        return len(self.dugum) - 1

    def _kenar_ekle(self, i, j):
        L = math.hypot(self.dugum[i][0] - self.dugum[j][0], self.dugum[i][1] - self.dugum[j][1])
        self.kenar[i].append((j, L))
        self.kenar[j].append((i, L))
        self.parcalar.append((i, j))

    def izdusum(self, x, y):
        """(x, y)'nin çizgeye en yakın noktası: (nokta, parça (i, j), uzaklık)."""
        en = None
        for i, j in self.parcalar:
            a, b = self.dugum[i], self.dugum[j]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy
            t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2)) if L2 else 0.0
            q = (a[0] + t * dx, a[1] + t * dy)
            d = math.hypot(q[0] - x, q[1] - y)
            if en is None or d < en[2]:
                en = (q, (i, j), d)
        return en

    def en_kisa_yol(self, p, q):
        """Çizge üstünde p'nin izdüşümünden q'nun izdüşümüne en kısa yol: [p', ..., q'] (köşeler dahil)."""
        pp, (pi, pj), _ = self.izdusum(*p)
        qq, (qi, qj), _ = self.izdusum(*q)
        if {pi, pj} == {qi, qj}:
            return [pp, qq]
        n = len(self.dugum)
        P_, Q_ = n, n + 1
        kom = {k: list(v) for k, v in self.kenar.items()}
        kom[P_] = [(pi, _uz(pp, self.dugum[pi])), (pj, _uz(pp, self.dugum[pj]))]
        kom[Q_] = []
        for k in (qi, qj):
            kom[k] = kom[k] + [(Q_, _uz(qq, self.dugum[k]))]
        konum = dict(enumerate(self.dugum))
        konum[P_], konum[Q_] = pp, qq
        uz = {P_: 0.0}
        once = {}
        h = [(0.0, P_)]
        while h:
            d, u = heapq.heappop(h)
            if u == Q_:
                break
            if d > uz.get(u, 1e18):
                continue
            for v, L in kom.get(u, []):
                if d + L < uz.get(v, 1e18):
                    uz[v] = d + L
                    once[v] = u
                    heapq.heappush(h, (d + L, v))
        yol = [Q_]
        while yol[-1] != P_:
            yol.append(once[yol[-1]])
        return [konum[k] for k in reversed(yol)]


def _uz(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def yol_boyu(P):
    return sum(_uz(a, b) for a, b in zip(P, P[1:]))


_DURAK_ONBELLEK = {}


def duraklar(kor):
    """{ad: {"xy": (x, y), "kapi": özellik id | None, "tur", "rota_m": başlangıçtan rota uzaklığı}} (sıralı)."""
    if kor in _DURAK_ONBELLEK:
        return _DURAK_ONBELLEK[kor]
    s = sahne(kor)
    cz = Cizge(s)
    n = kor.split("_")[-1]
    bas = tuple(s["orta_hat"][0])
    adaylar = []
    for o in s.get("ozellikler", []):
        if not o.get("tur", "").startswith("kapi"):
            continue
        hat = s.get(o.get("hat", "orta_hat"))
        if not hat:
            continue
        p = _nokta([tuple(q) for q in hat], float(o["s_m"]))
        adaylar.append((yol_boyu(cz.en_kisa_yol(bas, p)), p, o))
    adaylar.sort(key=lambda a: a[0])
    d = {}
    d["k%s_bas" % n] = dict(xy=bas, kapi=None, tur="uc", rota_m=0.0)
    for i, (r, p, o) in enumerate(adaylar, 1):
        d["k%s_kapi_%d" % (n, i)] = dict(xy=(round(p[0], 4), round(p[1], 4)), kapi=o["id"], tur=o["tur"], rota_m=round(r, 3))
    son = tuple(s["orta_hat"][-1])
    d["k%s_son" % n] = dict(xy=son, kapi=None, tur="uc", rota_m=round(yol_boyu(cz.en_kisa_yol(bas, son)), 3))
    if s.get("orta_hat_yan_kol"):
        y = tuple(s["orta_hat_yan_kol"][-1])
        d["k%s_kol_son" % n] = dict(xy=y, kapi=None, tur="uc", rota_m=round(yol_boyu(cz.en_kisa_yol(bas, y)), 3))
    _DURAK_ONBELLEK[kor] = d
    return d


def durak_coz(kor, ad):
    """Tam ad (k5_kapi_3) ya da göreli ad (kapi_3, son, bas) -> (tam ad, (x, y)). Yoksa KeyError."""
    d = duraklar(kor)
    n = kor.split("_")[-1]
    tam = ad if ad.startswith("k%s_" % n) else "k%s_%s" % (n, ad)
    return tam, tuple(d[tam]["xy"])


def rota(kor, bas_xy, hedef_xy, bas_poz=None, giris_m=0.5):
    """Robotun yerinden (bas_xy, gövde merkezi) orta hatta inip orta hat boyunca hedefe giden yol.

    Robot orta hattan uzaksa önce izdüşümünün `giris_m` ilerisine (rota yönünde) çapraz iner; yakınsa doğrudan yoldan
    başlar. Döner: [(x, y), ...] (ilk nokta robotun yeri)."""
    cz = _CIZGE.get(kor)
    if cz is None:
        cz = _CIZGE[kor] = Cizge(sahne(kor))
    P = cz.en_kisa_yol(bas_xy, hedef_xy)
    # izdüşümden giris_m ilerideki noktaya kadar olan baş kısmı kes (çapraz iniş)
    kalan = giris_m
    out = [tuple(bas_xy)]
    i = 0
    while i < len(P) - 1:
        L = _uz(P[i], P[i + 1])
        if L >= kalan:
            t = kalan / L if L else 0
            out.append((P[i][0] + (P[i + 1][0] - P[i][0]) * t, P[i][1] + (P[i + 1][1] - P[i][1]) * t))
            out.extend(P[i + 1:])
            break
        kalan -= L
        i += 1
    else:
        out.append(P[-1])
    # tekrar eden / çok kısa ilk parça
    temiz = [out[0]]
    for p in out[1:]:
        if _uz(p, temiz[-1]) > 0.02:
            temiz.append(p)
    if len(temiz) == 1:
        temiz.append(tuple(hedef_xy))
    return temiz


_CIZGE = {}
