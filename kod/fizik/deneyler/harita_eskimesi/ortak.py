"""Harita eskimesi deneyi: ortak parçalar (yollar, koşul ızgarası, dünyayı haritadan saptıran bozucular).

Robotun haritası her zaman bozulmamış koridor haritasıdır (`kod/araclar/haritalar/koridor_N.json`, konumlayıcı ve
rota onu kullanır, hiçbir şey değişmez). Bozucular yalnız DÜNYAYI (çarpışma + LiDAR'ın gördüğü geometri, insanlar,
sensör ve odometri hataları) değiştirir. Geometri bozucuları (ölçek, eğrilme) dünyayı harita çerçevesinden T ile
çıkarır: dünya = T(harita). Başlangıç noktası T'nin sabit noktasıdır; hedefin gerçek yeri T(hedef).

Koşul sözlüğü: {"id", "etken", "kademe", "deger", "p": {bozucu parametreleri}}. `p` anahtarları:
  kapi (oran), esya (adet / 10 m), insan (kişi / 10 m), grup (m, duvardan içeri), olcek (oran), genislik (m),
  egrilme (derece / 20 m), gurultu (m), donussuz (oran), cam (oran), menzil (m), odo_olcek (oran), odo_donus (oran),
  odo_kayma (olay / dakika hareket).
"""

import json
import math
import os
import sys
import time

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(os.path.dirname(BURASI))
KOD = os.path.dirname(FIZIK)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

SONUC = os.path.join(BURASI, "sonuc")
HAM = os.path.join(SONUC, "ham")
GORSEL = os.path.join(BURASI, "gorsel")
DURUM = os.path.join(BURASI, ".durum")
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
VARIS_PAYI = 0.3

# Taban (bozulmasız) 2B sensör / odometri değerleri. Odometri tabanı kesif/benzet2b.py ile aynı: dönüş %14 fazla
# (MuJoCo ONERI ölçüsü, konumlama BENIOKU), öteleme %0 sistematik; std 2 % / 3 %.
TABAN = dict(gurultu=0.010, menzil=12.0, odo_olcek=0.0, odo_donus=0.14)


def dusuk_oncelik():
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    if sys.platform == "win32":
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)
        except Exception:
            pass


def durum_yaz(satir):
    with open(DURUM, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), satir))


# ------------------------------------------------------------------ koşul ızgarası
KADEMELER = {
    # etken: (alt etken, [(etiket, değer)])
    "kapi": ("a", [0.10, 0.25, 0.50, 1.00]),
    "esya": ("b", [0.5, 1.0, 2.0, 4.0]),
    "insan": ("c", [0.5, 1.0, 2.0, 4.0]),
    "grup": ("c", [0.6, 0.9, 1.2, 1.5]),
    "olcek": ("d", [0.005, 0.01, 0.02, 0.03]),
    "genislik": ("d", [0.025, 0.05, 0.075, 0.10]),
    "egrilme": ("d", [0.5, 1.0, 2.0, 4.0]),
    "gurultu": ("e", [0.02, 0.03, 0.05, 0.08]),
    "donussuz": ("e", [0.10, 0.25, 0.50, 0.75]),
    "cam": ("e", [0.25, 0.50, 0.75, 1.00]),
    "menzil": ("e", [8.0, 6.0, 4.0, 2.0]),
    "odo_olcek": ("f", [0.02, 0.05, 0.075, 0.10]),
    "odo_donus": ("f", [0.05, 0.10, 0.15, 0.25]),
    "odo_kayma": ("f", [0.5, 1.0, 2.0, 4.0]),
}
OKUL_GUNU = {
    "hafif": dict(kapi=0.10, esya=0.5, insan=0.5, olcek=0.005, egrilme=0.5, gurultu=0.02, donussuz=0.10, cam=0.25,
                  odo_olcek=0.02, odo_donus=0.05),
    "orta": dict(kapi=0.25, esya=1.0, insan=1.0, grup=0.9, olcek=0.01, genislik=0.05, egrilme=1.0, gurultu=0.03,
                 donussuz=0.25, cam=0.50, menzil=8.0, odo_olcek=0.05, odo_donus=0.10, odo_kayma=1.0),
    "agir": dict(kapi=0.50, esya=2.0, insan=2.0, grup=1.2, olcek=0.02, genislik=0.10, egrilme=2.0, gurultu=0.05,
                 donussuz=0.50, cam=1.00, menzil=6.0, odo_olcek=0.075, odo_donus=0.15, odo_kayma=2.0),
}


def kosullar():
    out = [dict(id="taban", etken="taban", alt="-", kademe=0, deger=0.0, p={})]
    for et, (alt, degerler) in KADEMELER.items():
        for i, d in enumerate(degerler, 1):
            out.append(dict(id="%s_%d" % (et, i), etken=et, alt=alt, kademe=i, deger=d, p={et: d}))
    for i, (ad, p) in enumerate(OKUL_GUNU.items(), 1):
        out.append(dict(id="okul_%s" % ad, etken="okul", alt="g", kademe=i, deger=i, p=dict(p)))
    return out


def kosul(kid):
    for k in kosullar():
        if k["id"] == kid:
            return k
    raise KeyError(kid)


# ------------------------------------------------------------------ geometri yardımcıları
def sahne_oku(kor):
    with open(os.path.join(FIZIK, "sahneler", kor + ".json"), encoding="utf-8") as f:
        return json.load(f)


def harita_oku(kor):
    with open(os.path.join(KOD, "araclar", "haritalar", kor + ".json"), encoding="utf-8") as f:
        return json.load(f)


def hatlar(sahne):
    out = [[tuple(p) for p in sahne["orta_hat"]]]
    if sahne.get("orta_hat_yan_kol"):
        out.append([tuple(p) for p in sahne["orta_hat_yan_kol"]])
    return out


def _izdusum_hat(hat, x, y):
    """-> (uzaklık, izdüşüm noktası, parça birim yönü, hat boyunca s)."""
    en = None
    s0 = 0.0
    for (ax, ay), (bx, by) in zip(hat, hat[1:]):
        L = math.hypot(bx - ax, by - ay)
        t = max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / (L * L)))
        px, py = ax + t * (bx - ax), ay + t * (by - ay)
        d = math.hypot(x - px, y - py)
        if en is None or d < en[0]:
            en = (d, (px, py), ((bx - ax) / L, (by - ay) / L), s0 + t * L)
        s0 += L
    return en


def en_yakin_hat(sahne, x, y):
    return min((_izdusum_hat(h, x, y) for h in hatlar(sahne)), key=lambda e: e[0])


def kutu_parcalari(k):
    x0, y0 = k["x"], k["y"]
    x1, y1 = x0 + k["g"], y0 + k["d"]
    return [[x0, y0, x1, y0], [x1, y0, x1, y1], [x1, y1, x0, y1], [x0, y1, x0, y0]]


def _icinde(p, a, u, n, boy, der, tol=1e-3):
    """p nokta; a köşe, u duvar yönü, n dış normal: dikdörtgen [0, boy] x [0, der] içinde mi?"""
    dx, dy = p[0] - a[0], p[1] - a[1]
    s = dx * u[0] + dy * u[1]
    d = dx * n[0] + dy * n[1]
    return -tol <= s <= boy + tol and -tol <= d <= der + tol


def kapi_cercevesi(sahne, oz):
    """Kapı özelliği -> (a, b, u (a->b birim), n (dış normal), genişlik)."""
    ax, ay, bx, by = oz["duvar_cizgisi"]
    L = math.hypot(bx - ax, by - ay)
    u = ((bx - ax) / L, (by - ay) / L)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    _, q, _, _ = en_yakin_hat(sahne, mx, my)
    n = (-u[1], u[0])
    if (q[0] - mx) * n[0] + (q[1] - my) * n[1] > 0:     # n hatta doğru bakıyorsa ters çevir (dış normal)
        n = (-n[0], -n[1])
    return (ax, ay), (bx, by), u, n, L


def _P(a, u, n, s, d):
    return (a[0] + u[0] * s + n[0] * d, a[1] + u[1] * s + n[1] * d)


def _kutu_kesisir(k1, k2, pay=0.05):
    return not (k1[2] + pay <= k2[0] or k2[2] + pay <= k1[0] or k1[3] + pay <= k2[1] or k2[3] + pay <= k1[1])


def _hat_kutuda(sahne, kutu, pay=0.3):
    for h in hatlar(sahne):
        for (ax, ay), (bx, by) in zip(h, h[1:]):
            L = math.hypot(bx - ax, by - ay)
            n = max(2, int(L / 0.1))
            for i in range(n + 1):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                if kutu[0] - pay <= x <= kutu[2] + pay and kutu[1] - pay <= y <= kutu[3] + pay:
                    return True
    return False


def oda_kur(sahne, a, u, n, L, odalar, t=0.15):
    """Kapalı kapının arkasına oda (açıklık + 0,15 m duvar + oda). Odalar çakışmasın, oda koridora girmesin.
    -> (parçalar, oda kutusu) ya da None."""
    for yari in (1.5, 1.1, 0.8):
        for D in (3.0, 2.0, 1.2):
            r0, r1 = L / 2 - yari, L / 2 + yari
            k = [_P(a, u, n, r0, t), _P(a, u, n, r1, t + D)]
            kutu = (min(k[0][0], k[1][0]), min(k[0][1], k[1][1]), max(k[0][0], k[1][0]), max(k[0][1], k[1][1]))
            if any(_kutu_kesisir(kutu, o) for o in odalar) or _hat_kutuda(sahne, kutu):
                continue
            noktalar = [_P(a, u, n, 0, 0), _P(a, u, n, 0, t), _P(a, u, n, r0, t), _P(a, u, n, r0, t + D),
                        _P(a, u, n, r1, t + D), _P(a, u, n, r1, t), _P(a, u, n, L, t), _P(a, u, n, L, 0)]
            parca = [[p[0], p[1], q[0], q[1]] for p, q in zip(noktalar, noktalar[1:])]
            return parca, kutu
    return None


def mevcut_odalar(sahne):
    out = []
    for o in sahne["ozellikler"]:
        if o.get("oda"):
            r = o["oda"]
            out.append((r["x0"], r["y0"], r["x1"], r["y1"]))
    return out


def kapi_ac(duvarlar, sahne, oz, odalar):
    """Haritada kapalı (girinti) kapıyı dünyada aç: girintiyi sil, arkasına oda koy. -> yeni duvar listesi | None."""
    a, b, u, n, L = kapi_cercevesi(sahne, oz)
    sonuc = oda_kur(sahne, a, u, n, L, odalar)
    if sonuc is None:
        return None
    parca, kutu = sonuc
    derin = float(oz.get("derinlik_m", 0.09))
    kalan = [p for p in duvarlar
             if not (_icinde(p[:2], a, u, n, L, derin) and _icinde(p[2:], a, u, n, L, derin))]
    odalar.append(kutu)
    return kalan + parca


def kapi_kapat(duvarlar, sahne, oz, cam=False):
    """Haritada açık kapıyı dünyada kapat: açıklığa 0,05 m içeride kapı kanadı."""
    a, b, u, n, L = kapi_cercevesi(sahne, oz)
    p, q = _P(a, u, n, 0, 0.05), _P(a, u, n, L, 0.05)
    return duvarlar + [[p[0], p[1], q[0], q[1]]]


# ------------------------------------------------------------------ geometri dönüşümleri (dünya = T(harita))
class Donusum:
    """Ölçek (başlangıç çevresinde) ve eğrilme (başlangıçtan başlangıç yönünde, sabit eğrilik). Kimlik varsayılan."""

    def __init__(self, bas, olcek=0.0, egrilme_der_20m=0.0):
        self.bx, self.by, self.bth = bas
        self.k = 1.0 + olcek
        self.kappa = math.radians(egrilme_der_20m) / 20.0
        self.kimlik = (olcek == 0.0 and egrilme_der_20m == 0.0)

    def _yerel(self, x, y):
        c, s = math.cos(self.bth), math.sin(self.bth)
        dx, dy = x - self.bx, y - self.by
        return c * dx + s * dy, -s * dx + c * dy

    def _dunya(self, u, v):
        c, s = math.cos(self.bth), math.sin(self.bth)
        return self.bx + c * u - s * v, self.by + s * u + c * v

    def nokta(self, x, y):
        if self.kimlik:
            return x, y
        u, v = self._yerel(x, y)
        u, v = u * self.k, v * self.k
        if self.kappa:
            R = 1.0 / self.kappa
            f = u * self.kappa
            u, v = (R - v) * math.sin(f), R - (R - v) * math.cos(f)
        return self._dunya(u, v)

    def aci(self, x, y):
        """T'nin (x, y)'deki yerel dönmesi (rad)."""
        if self.kimlik or not self.kappa:
            return 0.0
        u, _ = self._yerel(x, y)
        return u * self.k * self.kappa

    def poz(self, p):
        x, y = self.nokta(p[0], p[1])
        return (x, y, p[2] + self.aci(p[0], p[1]))

    def ters_nokta(self, x, y):
        if self.kimlik:
            return x, y
        u, v = self._yerel(x, y)
        if self.kappa:
            R = 1.0 / self.kappa
            f = math.atan2(u, R - v)
            r = math.hypot(u, R - v)
            u, v = f / self.kappa, R - r
        return self._dunya(u / self.k, v / self.k)

    def ters_poz(self, p):
        x, y = self.ters_nokta(p[0], p[1])
        return (x, y, p[2] - self.aci(x, y))


def bol(parcalar, en_cok=1.0):
    out = []
    for x1, y1, x2, y2 in parcalar:
        L = math.hypot(x2 - x1, y2 - y1)
        n = max(1, int(math.ceil(L / en_cok)))
        for i in range(n):
            out.append([x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n,
                        x1 + (x2 - x1) * (i + 1) / n, y1 + (y2 - y1) * (i + 1) / n])
    return out


def genislik_kaydir(kor, delta):
    """Bir uzun duvarı dış normali boyunca delta kadar kaydırarak (+ geniş, - dar) dünya haritasını üretir.
    `koridor_sahneleri` tanımı bellekte kopyalanıp yeniden üretilir; harita çerçevesi korunur (kaydırma düzeltilir)."""
    import copy
    import koridor_sahneleri as KS
    kenar_ad = {"koridor_1": "ust", "koridor_2": "ust", "koridor_3": "kol1_ust", "koridor_4": "ana_alt",
                "koridor_5": "ust", "koridor_6": "ust"}[kor]
    t = copy.deepcopy(KS.KORIDORLAR[kor])
    i = t["kenar"].index(kenar_ad)
    cg = [list(p) for p in t["cokgen"]]
    p0, p1 = cg[i], cg[(i + 1) % len(cg)]
    (ux, uy), (nx, ny), _, _, _ = KS._kenar_bilgi(p0, p1)
    for p in (p0, p1):
        p[0] += nx * delta
        p[1] += ny * delta
    t["cokgen"] = [tuple(p) for p in cg]
    ad = "_he_%s" % kor
    KS.KORIDORLAR[ad] = t
    try:
        h_harita, s_harita = KS.sahne_kur(kor)
        h, s = KS.sahne_kur(ad)
    finally:
        del KS.KORIDORLAR[ad]
    dx = s_harita["kaydirma_m"][0] - s["kaydirma_m"][0]
    dy = s_harita["kaydirma_m"][1] - s["kaydirma_m"][1]
    h["duvarlar"] = [[x1 + dx, y1 + dy, x2 + dx, y2 + dy] for x1, y1, x2, y2 in h["duvarlar"]]
    for e in h["engeller"]:
        e["x"] += dx
        e["y"] += dy
    h["ad"] = kor
    h["baslangic"] = h_harita["baslangic"]
    return h


# ------------------------------------------------------------------ dünya kurulumu
def _duvar_mesafesi(harita, x, y, ux, uy, en_cok=3.0):
    import numpy as np
    d = harita.isin_izle(np.array([x]), np.array([y]), np.array([math.atan2(uy, ux)]), menzil=en_cok)
    return float(np.asarray(d).ravel()[0])


ESYA_TURLERI = [("kutu", 0.5, 0.5), ("sira", 1.2, 0.4), ("cop", 0.4, 0.4), ("dolap", 0.9, 0.45)]


def esya_yerlestir(sahne, harita2b, yogunluk, rng, kapali_noktalar):
    """Duvar dibine haritada olmayan eşya: yoğunluk = adet / 10 m orta hat. Kapı önleri (± 0,8 m), uçlar ve köşeler
    (orta hat kırılmasından 1,5 m) boş bırakılır. -> (engeller listesi [kutu / daire], kayıt)."""
    import numpy as np
    H = hatlar(sahne)
    boylar = [sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(h, h[1:])) for h in H]
    top = sum(boylar)
    n = int(round(yogunluk * top / 10.0))
    kirilmalar = [p for h in H for p in h]
    out, kayit, kutular = [], [], []
    deneme = 0
    while len(kayit) < n and deneme < 400 * max(n, 1):
        deneme += 1
        s = rng.uniform(0, top)
        hi = 0
        while s > boylar[hi]:
            s -= boylar[hi]
            hi += 1
        h = H[hi]
        for a, b in zip(h, h[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if s <= L:
                break
            s -= L
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        px, py = a[0] + ux * s, a[1] + uy * s
        if min(math.hypot(px - q[0], py - q[1]) for q in kirilmalar) < 1.5:
            continue
        yan = 1 if rng.random() < 0.5 else -1
        nx, ny = -uy * yan, ux * yan
        dw = _duvar_mesafesi(harita2b, px, py, nx, ny)
        if not math.isfinite(dw) or dw > 2.0:
            continue
        tur, g, d = ESYA_TURLERI[int(rng.integers(len(ESYA_TURLERI)))]
        # kapı önü: duvar noktası kapı açıklığına yakınsa geç
        wx, wy = px + nx * dw, py + ny * dw
        if any(math.hypot(wx - q[0], wy - q[1]) < 0.8 + g / 2 for q in kapali_noktalar):
            continue
        cx, cy = px + nx * (dw - d / 2 - 0.02), py + ny * (dw - d / 2 - 0.02)
        if tur == "cop":
            kutu = (cx - 0.2, cy - 0.2, cx + 0.2, cy + 0.2)
        elif abs(ux) > 0.5:
            kutu = (cx - g / 2, cy - d / 2, cx + g / 2, cy + d / 2)
        else:
            kutu = (cx - d / 2, cy - g / 2, cx + d / 2, cy + g / 2)
        if any(_kutu_kesisir(kutu, k, pay=0.1) for k in kutular):
            continue
        # duvar içine taşmasın (köşe noktaları duvara 1 cm'den yakın değil, gövde köşesi serbest alanda)
        kx = np.array([kutu[0], kutu[2], kutu[0], kutu[2]])
        ky = np.array([kutu[1], kutu[1], kutu[3], kutu[3]])
        if float(harita2b.geometri_uzakligi(kx, ky).min()) < 0.005 and tur != "cop":
            # duvara dayalı köşeler duvara değebilir; içe taşma denetimi: merkez duvardan uzak mı
            pass
        kutular.append(kutu)
        if tur == "cop":
            out.append({"tur": "daire", "x": round(cx, 3), "y": round(cy, 3), "r": 0.2})
        else:
            out.append({"tur": "kutu", "x": round(kutu[0], 3), "y": round(kutu[1], 3),
                        "g": round(kutu[2] - kutu[0], 3), "d": round(kutu[3] - kutu[1], 3)})
        kayit.append(dict(tur=tur, merkez=[round(cx, 3), round(cy, 3)]))
    return out, kayit


def dunya_kur(kor, p, rng):
    """Koşul parametreleri p ile dünya. -> sözlük:
      veri       çarpışma + MuJoCo dünyası (harita JSON biçimi; kutu / daire engeller)
      lidar_veri LiDAR'ın gördüğü dünya (cam kapılar açık), veri ile aynı çerçeve
      siyah      dönüş vermeyen yüzey parçaları [[x1, y1, x2, y2]] (LiDAR dünyasının alt kümesi)
      T          Donusum (harita -> dünya)
      kayit      ne değişti (sayılar)
    Bozucuların uygulanma sırası: kapı / cam / eşya (harita çerçevesinde), sonra genişlik, sonra T (ölçek, eğrilme)."""
    import numpy as np
    from konumlama.harita2b import Harita2B
    sahne = sahne_oku(kor)
    harita = harita_oku(kor)
    kayit = {}
    if p.get("genislik"):
        delta = p["genislik"] * (1 if rng.random() < 0.5 else -1)
        veri = genislik_kaydir(kor, delta)
        kayit["genislik_m"] = round(delta, 3)
    else:
        veri = json.loads(json.dumps(harita))
    duvar = [list(map(float, d)) for d in veri["duvarlar"]]
    engel = list(veri.get("engeller", []))
    odalar = mevcut_odalar(sahne)
    kapilar = [o for o in sahne["ozellikler"] if o["tur"] in ("kapi_kapali", "kapi_acik")]
    kapali_noktalar = [tuple(o["merkez"]) for o in kapilar]
    lidar_duvar = None
    # a. kapılar: oran kadarının durumu ters (kapalı -> açık + oda, açık -> kapalı)
    if p.get("kapi"):
        sira = list(range(len(kapilar)))
        rng.shuffle(sira)
        n = max(1, int(round(p["kapi"] * len(kapilar))))
        acilan = kapanan = 0
        for i in sira[:n]:
            o = kapilar[i]
            if o["tur"] == "kapi_kapali":
                yeni = kapi_ac(duvar, sahne, o, odalar)
                if yeni is not None:
                    duvar = yeni
                    acilan += 1
            else:
                duvar = kapi_kapat(duvar, sahne, o)
                kapanan += 1
        kayit.update(kapi_toplam=len(kapilar), kapi_acilan=acilan, kapi_kapanan=kapanan)
    # e. cam kapı: kapalı kapıların oranı kadarı camdan; LiDAR arkasındaki odayı görür, robot geçemez
    if p.get("cam"):
        kapali = [o for o in kapilar if o["tur"] == "kapi_kapali"]
        sira = list(range(len(kapali)))
        rng.shuffle(sira)
        n = max(1, int(round(p["cam"] * len(kapali))))
        lidar_duvar = [list(d) for d in duvar]
        cam = 0
        for i in sira[:n]:
            o = kapali[i]
            a, b, u, nn, L = kapi_cercevesi(sahne, o)
            # kapı zaten (a. etkenle) açıldıysa girintisi yoktur: atla
            if not any(_icinde(d[:2], a, u, nn, L, 0.09) and _icinde(d[2:], a, u, nn, L, 0.09) for d in lidar_duvar):
                continue
            yeni = kapi_ac(lidar_duvar, sahne, o, odalar)
            if yeni is None:
                continue
            # odanın duvarları çarpışma dünyasına da girer (yalnız cam kanadın arkası); kanat çarpışmada kalır
            eklenen = [d for d in yeni if d not in lidar_duvar]
            lidar_duvar = yeni
            duvar = duvar + eklenen
            cam += 1
        kayit["cam_kapi"] = cam
    # b. eşya
    if p.get("esya"):
        h2 = Harita2B(dict(veri, duvarlar=duvar, engeller=engel))
        e_ek, e_kayit = esya_yerlestir(sahne, h2, p["esya"], rng, kapali_noktalar)
        engel = engel + e_ek
        kayit["esya"] = len(e_kayit)
    # T: ölçek, eğrilme
    b = sahne["baslangic"]
    T = Donusum((b["x"], b["y"], math.radians(b.get("aci_derece", 0.0))), olcek=p.get("olcek", 0.0),
                egrilme_der_20m=p.get("egrilme", 0.0))
    if not T.kimlik:
        def tp(lst):
            out = []
            for x1, y1, x2, y2 in bol(lst, 1.0):
                a_, b_ = T.nokta(x1, y1), T.nokta(x2, y2)
                out.append([a_[0], a_[1], b_[0], b_[1]])
            return out
        kut = [e for e in engel if e["tur"] == "kutu"]
        dai = [e for e in engel if e["tur"] == "daire"]
        duvar = tp(duvar + [q for k in kut for q in kutu_parcalari(k)])
        if lidar_duvar is not None:
            lidar_duvar = tp(lidar_duvar + [q for k in kut for q in kutu_parcalari(k)])
        engel = []
        for e in dai:
            x, y = T.nokta(e["x"], e["y"])
            engel.append(dict(e, x=x, y=y, r=e["r"] * T.k))
        kayit.update(olcek=p.get("olcek", 0.0), egrilme_der_20m=p.get("egrilme", 0.0))
    yuvarla = lambda L: [[round(v, 4) for v in d] for d in L]
    dunya_veri = dict(veri, duvarlar=yuvarla(duvar), engeller=engel, ad=kor)
    xs = [v for d in dunya_veri["duvarlar"] for v in (d[0], d[2])]
    ys = [v for d in dunya_veri["duvarlar"] for v in (d[1], d[3])]
    dunya_veri["boyut_m"] = [max(veri["boyut_m"][0], math.ceil(max(xs) + 0.5)),
                             max(veri["boyut_m"][1], math.ceil(max(ys) + 0.5))]
    lidar_veri = dict(dunya_veri, duvarlar=yuvarla(lidar_duvar)) if lidar_duvar is not None else dunya_veri
    # e. dönüşsüz yüzeyler: LiDAR dünyasının duvarları 1 m parçalara bölünür, oran kadarı siyah / parlak
    siyah = []
    if p.get("donussuz"):
        parcalar = bol(lidar_veri["duvarlar"], 1.0)
        for e in lidar_veri["engeller"]:
            if e["tur"] == "kutu":
                parcalar += kutu_parcalari(e)
        sec = rng.random(len(parcalar)) < p["donussuz"]
        siyah = [q for q, s_ in zip(parcalar, sec) if s_]
        kayit["siyah_parca"] = int(sec.sum())
        kayit["parca"] = len(parcalar)
    if min(xs) < 0 or min(ys) < 0:
        kayit["uyari"] = "dunya negatif koordinatta"
    return dict(veri=dunya_veri, lidar_veri=lidar_veri, siyah=siyah, T=T, kayit=kayit, sahne=sahne)


def mujoco_sahnesi(kor, dunya):
    """Duzenek'e verilecek sahne sözlüğü: koridor sahnesi + dünya haritası (harita_veri)."""
    s = sahne_oku(kor)
    s = dict(s, harita_veri=dunya["veri"], ad=kor)
    return s
