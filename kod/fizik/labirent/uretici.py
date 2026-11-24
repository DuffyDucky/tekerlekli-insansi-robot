"""Lale labirent sahneleri: üret, çiz, doğrula, istatistik. Keşif deneyi için (START -> FINISH, ön bilgisiz, 15 dk).

    py -3 kod\\fizik\\labirent\\uretici.py uret                          # sahne ailesinin hepsi (SAHNE_AILESI)
    py -3 kod\\fizik\\labirent\\uretici.py uret --satir 9 --sutun 9 --tohum 7 [--hucre 1.3] [--start ust:0] [--finish alt:-1] [--ad X]
    py -3 kod\\fizik\\labirent\\uretici.py ciz [sahne ...]               # -> kod\\fizik\\labirent\\gorsel\\*.png (matplotlib)
    py -3 kod\\fizik\\labirent\\uretici.py fizibilite                    # süre tablosu (Markdown) -> stdout
    py -3 kod\\fizik\\labirent\\uretici.py istatistik [--boyut 17]       # algoritma karşılaştırması (seçim gerekçesi)
    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod\\fizik\\labirent\\uretici.py dogrula [sahne ...]   # mujoco gerekir

Çıktı iki katmanlı sahne biçimi (koridor sahneleriyle aynı kalıp): `kod/araclar/haritalar/<ad>.json` (2B harita: duvar
çizgi parçaları, `cevre_duvari` kapalı) + `kod/fizik/sahneler/<ad>.json` (3B sahne; labirente özel `labirent` alanı, yükleyiciler
bilinmeyen anahtara bakmaz). Duvarlar 3B'de `dunya.sahne_xml` iç duvar levhası: 2 mm, 1,0 m yükseklik (`fizik_parametreleri.json`
`ic_duvar_kalinligi_m` / `duvar_yuksekligi_m`); LiDAR düzlemi z 0,295 m duvarı keser. `dunya.py`'ye dokunulmadı.

Çerçeve: harita x sağa, y yukarı (m). Hücre (satır r, sütun c): r = 0 en üst satır, c = 0 en sol sütun. Labirentin dış sınırı
[x0, y0, x1, y1]; çevresinde DIS_PAY_M açık zemin (MuJoCo zemini sonsuz düzlem; 2B haritada duvar yok, LiDAR boşluk görür).
Hücre kodu (`labirent.hucreler`, satır başına bir dize, hücre başına bir onaltılık hane): açık kenar bitleri K 1, D 2, G 4, B 8
(kuzey = +y, doğu = +x). START / FINISH açıklıkları da bit olarak işlenir.

Tek kaynak bu dosya: JSON'lar buradan üretilir, elle düzeltilmez.
"""

import argparse
import json
import math
import os
import random
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(BURASI)
KOD = os.path.dirname(FIZIK)
HARITALAR = os.path.join(KOD, "araclar", "haritalar")
SAHNELER = os.path.join(FIZIK, "sahneler")
GORSEL = os.path.join(BURASI, "gorsel")

# ------------------------------------------------------------------ robot ve geometri sabitleri (gerekçe BENIOKU.md)
# Robot (model/lale.xml çarpışma geom'ları, ev pozu; ölçüm: BENIOKU.md "Robot ölçüleri"):
ROBOT_ON_M = 0.2642          # gövde merkezinden öne (c_govde yarı derinlik; etek 0,2625)
ROBOT_ARKA_M = 0.2642
ROBOT_YAN_M = 0.2617         # yarı genişlik (c_govde; etek 0,260)
ARKA_DINGIL_M = 0.185        # arka dingil gövde merkezinin gerisinde (ön omnili öneride dönme merkezi)
DONUS_YARICAP_M = 0.5199     # arka dingil etrafında yerinde dönüşte süpürme yarıçapı (ölçülen)
HUCRE_M = 1.30               # geçit (hücre) genişliği, duvar ekseninden duvar eksenine
START_IC_M = 0.45            # START pozunda gövde merkezi çizginin bu kadar içinde (gerekçe aşağıda)
DIS_PAY_M = 3.0              # labirentin çevresinde açık zemin
IC_DUVAR_M = 0.002           # fizik_parametreleri.json ic_duvar_kalinligi_m (yalnız geometrik kontrolde pay)
# START_IC_M: ayak izi (arka kenar 0,264) tamamen içeride (0,186 m pay); arka dingil çizginin 0,265 m içinde, böylece arka
# dingil etrafında yerinde dönüşte gövde merkezi (dingile 0,185 m) çizgiye en çok 0,080 m yaklaşır, dışarı geçmez.

K, D, G, B = 1, 2, 4, 8
YON = {K: (-1, 0), D: (0, 1), G: (1, 0), B: (0, -1)}          # (dr, dc)
TERS = {K: G, G: K, D: B, B: D}
KENAR_BIT = {"ust": K, "sag": D, "alt": G, "sol": B}

# Sahne ailesi: adlar sabit (gezinme / keşif ajanları kullanıyor). tohum = t numarası.
SAHNE_AILESI = {}
for _n, _ts in ((5, (1,)), (7, (1,)), (9, (1, 2, 3)), (13, (1, 2, 3)), (17, (1, 2, 3))):
    for _t in _ts:
        SAHNE_AILESI["labirent_%dx%d_t%d" % (_n, _n, _t)] = dict(satir=_n, sutun=_n, tohum=_t)
AMAC = {5: "gelistirme", 7: "gelistirme", 9: "sinama", 13: "sinama", 17: "final sinavi (ornek gorselle ayni boyut sinifi)"}


# ------------------------------------------------------------------ labirent (topoloji)

class Labirent:
    """satir x sutun hücre, acik[r][c] açık kenar bitleri; start / finish = (kenar, hücre)."""

    def __init__(self, satir, sutun, acik, start, finish, tohum=None, algoritma=None):
        self.satir, self.sutun, self.acik = satir, sutun, acik
        self.start, self.finish = start, finish                 # (kenar adı, (r, c))
        self.tohum, self.algoritma = tohum, algoritma

    def komsular(self, h):
        r, c = h
        for bit, (dr, dc) in YON.items():
            if self.acik[r][c] & bit:
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.satir and 0 <= cc < self.sutun:
                    yield (rr, cc)

    def mesafeler(self, kaynak):
        """BFS hücre mesafesi {hücre: adım}."""
        m = {kaynak: 0}
        kuyruk = [kaynak]
        for h in kuyruk:
            for n in self.komsular(h):
                if n not in m:
                    m[n] = m[h] + 1
                    kuyruk.append(n)
        return m

    def yol(self, a, b):
        """a'dan b'ye hücre yolu (ağaçta tek)."""
        geri = {a: None}
        kuyruk = [a]
        for h in kuyruk:
            if h == b:
                break
            for n in self.komsular(h):
                if n not in geri:
                    geri[n] = h
                    kuyruk.append(n)
        y = [b]
        while y[-1] != a:
            y.append(geri[y[-1]])
        return y[::-1]

    def cozum(self):
        return self.yol(self.start[1], self.finish[1])

    def derece(self, h):
        return bin(self.acik[h[0]][h[1]]).count("1")

    def cikmazlar(self):
        """Tek açık kenarlı hücreler (START / FINISH açıklığı açık kenar sayılır)."""
        return [(r, c) for r in range(self.satir) for c in range(self.sutun) if self.derece((r, c)) == 1]

    def kenar_sayisi(self):
        """İç geçit sayısı (hücreden hücreye açık kenar)."""
        n = 0
        for r in range(self.satir):
            for c in range(self.sutun):
                n += bool(c + 1 < self.sutun and self.acik[r][c] & D) + bool(r + 1 < self.satir and self.acik[r][c] & G)
        return n

    def mukemmel_mi(self):
        """(her hücre erişilebilir mi, döngü yok mu, iç geçit sayısı). Ağaç: bağlı ve kenar = hücre - 1."""
        N = self.satir * self.sutun
        E = self.kenar_sayisi()
        bagli = len(self.mesafeler(self.start[1])) == N
        # simetri: açık bitler iki tarafta aynı
        for r in range(self.satir):
            for c in range(self.sutun):
                for bit, (dr, dc) in YON.items():
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < self.satir and 0 <= cc < self.sutun:
                        if bool(self.acik[r][c] & bit) != bool(self.acik[rr][cc] & TERS[bit]):
                            return False, False, E
        return bagli, bagli and E == N - 1, E

    def kod(self):
        return ["".join("%x" % v for v in satir) for satir in self.acik]

    @classmethod
    def koddan(cls, satirlar, start, finish):
        acik = [[int(ch, 16) for ch in s] for s in satirlar]
        return cls(len(acik), len(acik[0]), acik, start, finish)


def _kenar_hucre(kenar, i, satir, sutun):
    if kenar not in KENAR_BIT:
        raise ValueError("kenar ust / alt / sol / sag olmalı: %r" % kenar)
    n = sutun if kenar in ("ust", "alt") else satir
    i = i % n
    if kenar == "ust":
        return (0, i)
    if kenar == "alt":
        return (satir - 1, i)
    if kenar == "sol":
        return (i, 0)
    return (i, sutun - 1)


def _sec(rng, liste):
    return liste[min(len(liste) - 1, int(rng.random() * len(liste)))]


def labirent_uret(satir, sutun, tohum, start=("ust", 0), finish=("alt", -1), algoritma="geri_izleme"):
    """Mükemmel (döngüsüz, tam bağlı) labirent. Rastgelelik yalnız random.Random(tohum).random() (sürümler arası kararlı).

    algoritma: "geri_izleme" (özyinelemeli geri izleme, yığınla; START hücresinden) | "wilson" | "agac:<p>" (büyüyen ağaç,
    p olasılıkla en yeni hücre = geri izleme, 1 - p ile rastgele = Prim benzeri). Seçim gerekçesi BENIOKU.md."""
    rng = random.Random(tohum)
    acik = [[0] * sutun for _ in range(satir)]
    s_hucre = _kenar_hucre(start[0], start[1], satir, sutun)
    f_hucre = _kenar_hucre(finish[0], finish[1], satir, sutun)
    if s_hucre == f_hucre and start[0] == finish[0]:
        raise ValueError("START ve FINISH aynı açıklık")

    def bos_komsular(h, ziyaret):
        r, c = h
        out = []
        for bit, (dr, dc) in YON.items():
            rr, cc = r + dr, c + dc
            if 0 <= rr < satir and 0 <= cc < sutun and (rr, cc) not in ziyaret:
                out.append((bit, (rr, cc)))
        return out

    def oy(h, bit):
        r, c = h
        dr, dc = YON[bit]
        acik[r][c] |= bit
        acik[r + dr][c + dc] |= TERS[bit]

    if algoritma == "geri_izleme" or algoritma.startswith("agac"):
        p = 1.0 if algoritma == "geri_izleme" else float(algoritma.split(":")[1])
        ziyaret = {s_hucre}
        aktif = [s_hucre]
        while aktif:
            i = len(aktif) - 1 if (p >= 1.0 or rng.random() < p) else min(len(aktif) - 1, int(rng.random() * len(aktif)))
            h = aktif[i]
            nb = bos_komsular(h, ziyaret)
            if not nb:
                aktif.pop(i)
                continue
            bit, n = _sec(rng, nb)
            oy(h, bit)
            ziyaret.add(n)
            aktif.append(n)
    elif algoritma == "wilson":
        tum = [(r, c) for r in range(satir) for c in range(sutun)]
        agacta = {s_hucre}
        for h0 in tum:
            if h0 in agacta:
                continue
            yon = {}
            h = h0
            while h not in agacta:                      # rastgele yürüyüş; son çıkış yönü = döngü silinmiş yol
                bit, n = _sec(rng, bos_komsular(h, set()))
                yon[h] = bit
                h = n
            h = h0
            while h not in agacta:
                bit = yon[h]
                oy(h, bit)
                agacta.add(h)
                dr, dc = YON[bit]
                h = (h[0] + dr, h[1] + dc)
    else:
        raise ValueError("bilinmeyen algoritma: %r" % algoritma)
    acik[s_hucre[0]][s_hucre[1]] |= KENAR_BIT[start[0]]
    acik[f_hucre[0]][f_hucre[1]] |= KENAR_BIT[finish[0]]
    return Labirent(satir, sutun, acik, (start[0], s_hucre), (finish[0], f_hucre), tohum, algoritma)


# ------------------------------------------------------------------ metrik geometri

def _r(v):
    return round(float(v) + 0.0, 4) + 0.0


class Yerlesim:
    """Hücre <-> harita koordinatı. x0, y0 labirentin sol alt köşesi."""

    def __init__(self, satir, sutun, h, x0, y0):
        self.satir, self.sutun, self.h, self.x0, self.y0 = satir, sutun, h, x0, y0
        self.x1, self.y1 = x0 + sutun * h, y0 + satir * h

    def merkez(self, hucre):
        r, c = hucre
        return (self.x0 + (c + 0.5) * self.h, self.y0 + (self.satir - r - 0.5) * self.h)

    def hucre(self, x, y):
        """(r, c) ya da None (labirent dışı)."""
        c = int(math.floor((x - self.x0) / self.h))
        r = int(math.floor((self.y1 - y) / self.h))
        if 0 <= r < self.satir and 0 <= c < self.sutun:
            return (r, c)
        return None

    def acik_cizgi(self, kenar, hucre):
        """Dış sınırdaki açıklık çizgisi [[x1, y1], [x2, y2]] ve içeri bakan birim normal."""
        r, c = hucre
        h = self.h
        xa, xb = self.x0 + c * h, self.x0 + (c + 1) * h
        ya, yb = self.y1 - (r + 1) * h, self.y1 - r * h
        if kenar == "ust":
            return [[xa, self.y1], [xb, self.y1]], (0.0, -1.0)
        if kenar == "alt":
            return [[xa, self.y0], [xb, self.y0]], (0.0, 1.0)
        if kenar == "sol":
            return [[self.x0, ya], [self.x0, yb]], (1.0, 0.0)
        return [[self.x1, ya], [self.x1, yb]], (-1.0, 0.0)


def duvar_parcalari(lab, yer):
    """Duvar çizgi parçaları; aynı doğrultudaki bitişik duvarlar tek parça (MuJoCo'da tek kutu)."""
    R, C, h = lab.satir, lab.sutun, yer.h
    parca = []
    for i in range(R + 1):                                  # yatay çizgiler, üstten
        y = yer.y1 - i * h
        var = []
        for c in range(C):
            if i < R:
                v = not (lab.acik[i][c] & K)
            else:
                v = not (lab.acik[R - 1][c] & G)
            var.append(v)
        c = 0
        while c < C:
            if var[c]:
                c2 = c
                while c2 + 1 < C and var[c2 + 1]:
                    c2 += 1
                parca.append([_r(yer.x0 + c * h), _r(y), _r(yer.x0 + (c2 + 1) * h), _r(y)])
                c = c2 + 1
            else:
                c += 1
    for j in range(C + 1):                                  # düşey çizgiler, soldan
        x = yer.x0 + j * h
        var = []
        for r in range(R):
            if j < C:
                v = not (lab.acik[r][j] & B)
            else:
                v = not (lab.acik[r][C - 1] & D)
            var.append(v)
        r = 0
        while r < R:
            if var[r]:
                r2 = r
                while r2 + 1 < R and var[r2 + 1]:
                    r2 += 1
                parca.append([_r(x), _r(yer.y1 - (r2 + 1) * h), _r(x), _r(yer.y1 - r * h)])
                r = r2 + 1
            else:
                r += 1
    return parca


def _donusler(hucreler):
    """Hücre dizisinde yön değişimleri: (90° sayısı, 180° sayısı)."""
    n90 = n180 = 0
    for a, b, c in zip(hucreler, hucreler[1:], hucreler[2:]):
        d1 = (b[0] - a[0], b[1] - a[1])
        d2 = (c[0] - b[0], c[1] - b[1])
        if d1 == d2:
            continue
        if d1 == (-d2[0], -d2[1]):
            n180 += 1
        else:
            n90 += 1
    return n90, n180


# ------------------------------------------------------------------ ön bilgisiz taban stratejileri (fizibilite tahmini)

_SAG = {K: D, D: G, G: B, B: K}
_SOL = {v: k for k, v in _SAG.items()}


def duvar_takip(lab, el="sol", budama=False, gorus_m=12.0, hucre_m=HUCRE_M):
    """Duvar takibi (mükemmel labirentte FINISH'i her zaman bulur): ziyaret edilen hücre dizisi START -> FINISH.

    budama True: kavşakta düz bakılan kolun tamamı görüşte (tek düz koridor, yan açıklıksız, çıkmazla biter, boyu <= gorus_m)
    ise o kola girilmez (LiDAR'ın uçtan uca görebildiği çıkmaz). İdealize TAHMİN: duvar yüzeyini gören ışın açısı, kör sektör ve
    harita belirsizliği yok sayılır."""
    s, f = lab.start[1], lab.finish[1]
    gelis = TERS[KENAR_BIT[lab.start[0]]]                    # içeri giriş yönü (START kenarından içeri)
    yon = gelis
    h = s
    dizi = [h]
    sira = (_SOL, None, _SAG) if el == "sol" else (_SAG, None, _SOL)
    adim = 0
    while h != f or not (lab.acik[f[0]][f[1]] & KENAR_BIT[lab.finish[0]] and False):
        if h == f:
            break
        adim += 1
        if adim > 100000:
            raise RuntimeError("duvar takibi bitmedi")
        aday = [sira[0][yon], yon, sira[2][yon], TERS[yon]]
        for d in aday:
            r, c = h
            if not (lab.acik[r][c] & d):
                continue
            dr, dc = YON[d]
            n = (r + dr, c + dc)
            if not (0 <= n[0] < lab.satir and 0 <= n[1] < lab.sutun):
                continue                                    # START açıklığından geri çıkma: kural dışı
            if budama and d != TERS[yon] and _gorunur_cikmaz(lab, h, d, gorus_m, hucre_m, f):
                continue
            yon = d
            h = n
            dizi.append(h)
            break
    return dizi


def _gorunur_cikmaz(lab, h, d, gorus_m, hucre_m, f):
    """h'den d yönündeki kol: düz, yan açıklıksız, çıkmazla bitiyor ve boyu görüş içinde mi (FINISH içermez)."""
    r, c = h
    n_adim = 0
    while True:
        dr, dc = YON[d]
        r, c = r + dr, c + dc
        n_adim += 1
        if (r, c) == f:
            return False
        v = lab.acik[r][c]
        if v & ~(d | TERS[d]) & 0xF:                       # yan açıklık
            return False
        if not (v & d):                                     # uç: çıkmaz
            return (n_adim + 0.5) * hucre_m <= gorus_m
        if n_adim * hucre_m > gorus_m:
            return False


# ------------------------------------------------------------------ sahne kurma

def ad_uret(satir, sutun, tohum, hucre_m=HUCRE_M):
    ad = "labirent_%dx%d_t%d" % (satir, sutun, tohum)
    if abs(hucre_m - HUCRE_M) > 1e-9:
        ad += "_h%d" % int(round(hucre_m * 100))
    return ad


def sahne_kur(ad, satir, sutun, tohum, hucre_m=HUCRE_M, start=("ust", 0), finish=("alt", -1), algoritma="geri_izleme"):
    """(harita sözlüğü, sahne sözlüğü, Labirent)."""
    lab = labirent_uret(satir, sutun, tohum, start, finish, algoritma)
    yer = Yerlesim(satir, sutun, hucre_m, DIS_PAY_M, DIS_PAY_M)
    parca = duvar_parcalari(lab, yer)
    boyut = [_r(yer.x1 + DIS_PAY_M), _r(yer.y1 + DIS_PAY_M)]
    s_cizgi, s_n = yer.acik_cizgi(*lab.start)
    f_cizgi, f_n = yer.acik_cizgi(*lab.finish)
    mx, my = (s_cizgi[0][0] + s_cizgi[1][0]) / 2, (s_cizgi[0][1] + s_cizgi[1][1]) / 2
    bx, by = mx + s_n[0] * START_IC_M, my + s_n[1] * START_IC_M
    th = math.degrees(math.atan2(s_n[1], s_n[0]))
    baslangic = {"x": _r(bx), "y": _r(by), "aci_derece": _r(th)}
    coz = lab.cozum()
    yol = [[_r(v) for v in yer.merkez(hc)] for hc in coz]
    n90, n180 = _donusler(coz)
    cikmaz = lab.cikmazlar()
    _, mukemmel, E = lab.mukemmel_mi()
    if not mukemmel:
        raise RuntimeError("%s mükemmel değil" % ad)
    fm = lab.mesafeler(lab.finish[1])
    cap = max(lab.mesafeler(max(fm, key=fm.get)).values())
    sol = duvar_takip(lab, "sol", hucre_m=hucre_m)
    sag = duvar_takip(lab, "sag", hucre_m=hucre_m)
    aciklama = ("Mukemmel labirent %d x %d hucre, hucre %.2f m (dis olcu %.2f x %.2f m), tohum %d, %s. START %s kenari "
                "(%d, %d), FINISH %s kenari (%d, %d). Uretici: kod/fizik/labirent/uretici.py."
                % (satir, sutun, hucre_m, sutun * hucre_m, satir * hucre_m, tohum, algoritma, lab.start[0], lab.start[1][0],
                   lab.start[1][1], lab.finish[0], lab.finish[1][0], lab.finish[1][1]))
    harita = {"ad": ad, "aciklama": aciklama, "boyut_m": boyut, "cevre_duvari": False, "duvarlar": parca, "engeller": [],
              "baslangic": baslangic}
    lb = {
        "satir": satir, "sutun": sutun, "hucre_m": hucre_m, "tohum": tohum, "algoritma": algoritma,
        "start": {"kenar": lab.start[0], "hucre": list(lab.start[1]), "cizgi": [[_r(v) for v in p] for p in s_cizgi],
                  "ic_normal": list(s_n), "poz": [_r(bx), _r(by), _r(math.radians(th))]},
        "finish": {"kenar": lab.finish[0], "hucre": list(lab.finish[1]), "cizgi": [[_r(v) for v in p] for p in f_cizgi],
                   "ic_normal": list(f_n)},
        "cozum_yolu": yol,
        "cozum_hucre_sayisi": len(coz),
        "cozum_uzunlugu_m": _r(len(coz) * hucre_m),
        "cozum_donus": {"d90": n90, "d180": n180},
        "toplam_gecit_m": _r(E * hucre_m),
        "gecit_sayisi": E,
        "cikmaz_sayisi": len(cikmaz),
        "cap_hucre": cap,
        "duvar_takip": {"sol_el_hucre": len(sol), "sag_el_hucre": len(sag)},
        "sinir": [_r(yer.x0), _r(yer.y0), _r(yer.x1), _r(yer.y1)],
        "hucreler": lab.kod(),
        "hucre_kodu": "satir r = 0 en ustte; hane = acik kenar bitleri K 1 (+y), D 2 (+x), G 4 (-y), B 8 (-x)",
        "tanimlar": ("cozum_uzunlugu_m = cozum_hucre_sayisi x hucre_m (START cizgisinden FINISH cizgisine hucre "
                     "merkezlerinden gecen kirik cizgi); toplam_gecit_m = ic gecit sayisi (hucre - 1) x hucre_m; cikmaz = "
                     "tek acik kenarli hucre (START / FINISH acikligi acik kenar sayilir); poz = [x, y, th rad] govde "
                     "merkezi, START cizgisinin %.2f m icinde, iceri bakiyor." % START_IC_M),
    }
    sahne = {"ad": ad, "aciklama": "Labirent sahnesi (kesif deneyi): %s haritasi. Rampa / esik yok. Kurallar ve puan: "
                                   "kod/fizik/labirent/BENIOKU.md (hakem.py, puan.py)." % ad,
             "harita": ad, "baslangic": baslangic, "rampalar": [], "esikler": [], "labirent": lb}
    return harita, sahne, lab


def _json_yaz(yol, veri):
    if FIZIK not in sys.path:
        sys.path.insert(0, FIZIK)
    from koridor_sahneleri import _json_yaz as yaz                   # aynı okunur JSON biçimi
    yaz(yol, veri)


def uret_tek(ad, **kw):
    h, s, lab = sahne_kur(ad, **kw)
    _json_yaz(os.path.join(HARITALAR, ad + ".json"), h)
    _json_yaz(os.path.join(SAHNELER, ad + ".json"), s)
    L = s["labirent"]
    print("%-20s %2dx%-2d duvar parcasi %3d | cozum %3d hucre %6.1f m | gecit %6.1f m | cikmaz %3d | boyut %s m"
          % (ad, L["satir"], L["sutun"], len(h["duvarlar"]), L["cozum_hucre_sayisi"], L["cozum_uzunlugu_m"],
             L["toplam_gecit_m"], L["cikmaz_sayisi"], h["boyut_m"]))
    return h, s


def uret(adlar=None):
    for ad in (adlar or SAHNE_AILESI):
        uret_tek(ad, **SAHNE_AILESI[ad])


def sahne_listesi():
    return sorted(f[:-5] for f in os.listdir(SAHNELER) if f.startswith("labirent_") and f.endswith(".json"))


def oku(ad):
    with open(os.path.join(SAHNELER, ad + ".json"), encoding="utf-8") as f:
        s = json.load(f)
    with open(os.path.join(HARITALAR, s["harita"] + ".json"), encoding="utf-8") as f:
        h = json.load(f)
    return h, s


def labirent_sahneden(s):
    """3B sahne sözlüğünden (Labirent, Yerlesim)."""
    L = s["labirent"]
    lab = Labirent.koddan(L["hucreler"], (L["start"]["kenar"], tuple(L["start"]["hucre"])),
                          (L["finish"]["kenar"], tuple(L["finish"]["hucre"])))
    x0, y0, _, _ = L["sinir"]
    return lab, Yerlesim(L["satir"], L["sutun"], L["hucre_m"], x0, y0)


# ------------------------------------------------------------------ fizibilite (süre tahmini)

# Seyir modeli (BENIOKU.md "Fizibilite"): düz kısım v ile, her 90° dönüş T90, her 180° (çıkmazda U) T180 saniye.
# T90: öneri firmware + ön omni ölçümü 90° 2,0-2,6 s (SIMULASYON.md ONERI tablosu); T180 iki katı. Hızlanma / yavaşlama
# (0,5 m/s² -> 0,39 m/s'ye 0,78 s) dönüş sürelerine gömülü sayılır (iyimser).
HIZLAR = (0.39, 0.30, 0.25)
T90_S, T180_S = 2.3, 4.6
SINIR_S = 900.0


def sure_s(uzunluk_m, d90, d180, v):
    return uzunluk_m / v + d90 * T90_S + d180 * T180_S


def fizibilite_satirlari(adlar=None):
    sat = []
    for ad in adlar or [a for a in SAHNE_AILESI]:
        _, s = oku(ad)
        lab, yer = labirent_sahneden(s)
        L = s["labirent"]
        h = L["hucre_m"]
        coz = lab.cozum()
        a90, a180 = _donusler(coz)
        E = L["gecit_sayisi"]
        # tam DFS keşfi: her iç geçit gidiş-dönüş, FINISH'e giden yol bir kez: 2E - (çözüm - 1) geçit + iki yarım hücre
        dfs_m = (2 * E - (len(coz) - 1)) * h + h
        dfs_180 = L["cikmaz_sayisi"]
        dfs_90 = 2 * _tum_donus90(lab)
        r = {"ad": ad, "boyut": "%dx%d" % (L["satir"], L["sutun"]), "kenar_m": L["sutun"] * h,
             "cozum_m": L["cozum_uzunlugu_m"], "gecit_m": L["toplam_gecit_m"], "cikmaz": L["cikmaz_sayisi"],
             "a": (L["cozum_uzunlugu_m"], a90, a180), "b": (L["toplam_gecit_m"], _tum_donus90(lab), 0),
             "dfs": (dfs_m, dfs_90, dfs_180)}
        for el in ("sol", "sag"):
            for bud in (False, True):
                d = duvar_takip(lab, el, budama=bud, hucre_m=h)
                n90, n180 = _donusler(d)
                r["%s%s" % (el, "_bud" if bud else "")] = (len(d) * h, n90, n180)
        sat.append(r)
    return sat


def _tum_donus90(lab):
    """Ağaçtaki her hücrede, geçit çiftlerinden dik açılı olanların sayısı (geçitleri bir kez gezen yürüyüşün kaba dönüş sayısı)."""
    n = 0
    for r in range(lab.satir):
        for c in range(lab.sutun):
            v = lab.acik[r][c]
            dik = (bool(v & K) or bool(v & G)) and (bool(v & D) or bool(v & B))
            n += 1 if dik else 0
    return n


def fizibilite_md(adlar=None):
    sat = fizibilite_satirlari(adlar)
    out = []
    out.append("| Sahne | Kenar m | Cozum m | Gecit m | Cikmaz | t_min = L*/0,39 dk | (a) cozum yolu dk @0,39 / 0,30 / 0,25 | "
               "(b) gecitler bir kez dk @0,30 | (c) tam DFS kesfi dk @0,39 / 0,30 | sol el / sag el dk @0,30 | "
               "sol / sag el + gorus budamasi dk @0,30 |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    f = lambda t: ("%.1f" % (t / 60)).replace(".", ",")
    for r in sat:
        a = r["a"]
        b = r["b"]
        out.append("| `%s` | %s | %s | %s | %d | %s | %s / %s / %s | %s | %s / %s | %s / %s | %s / %s |" % (
            r["ad"], ("%.1f" % r["kenar_m"]).replace(".", ","), ("%.1f" % r["cozum_m"]).replace(".", ","),
            ("%.1f" % r["gecit_m"]).replace(".", ","), r["cikmaz"], f(r["cozum_m"] / 0.39),
            f(sure_s(*a, 0.39)), f(sure_s(*a, 0.30)), f(sure_s(*a, 0.25)), f(sure_s(*b, 0.30)),
            f(sure_s(*r["dfs"], 0.39)), f(sure_s(*r["dfs"], 0.30)),
            f(sure_s(*r["sol"], 0.30)), f(sure_s(*r["sag"], 0.30)),
            f(sure_s(*r["sol_bud"], 0.30)), f(sure_s(*r["sag_bud"], 0.30))))
    return "\n".join(out), sat


def dagilim(boyutlar=(5, 7, 9, 13, 17), n_tohum=100, v=0.30, hucre_m=HUCRE_M, algoritma="geri_izleme"):
    """Boyut başına n_tohum labirentte 15 dk içinde kalma oranları (seyir modeliyle). Markdown tablo."""
    out = ["| Boyut (hucre %s m, v %s m/s) | L* ort. [min-max] m | t_min = L*/0,39 > 15 dk | (a) cozum yolu > 15 dk | "
           "sol/sag el en iyisi <= 15 dk | sol/sag el + budama en iyisi <= 15 dk | ikisi de (rastgele el) <= 15 dk | "
           "tam DFS kesfi <= 15 dk |" % (("%.2f" % hucre_m).replace(".", ","), ("%.2f" % v).replace(".", ",")),
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for n in boyutlar:
        Ls, a_asar, tmin_asar, el, el_bud, el_iki, dfs_ok = [], 0, 0, 0, 0, 0, 0
        for t in range(1001, 1001 + n_tohum):                # aile tohumlarından (1-3) ayrı
            lab = labirent_uret(n, n, t, algoritma=algoritma)
            coz = lab.cozum()
            a90, a180 = _donusler(coz)
            Lm = len(coz) * hucre_m
            Ls.append(Lm)
            tmin_asar += Lm / 0.39 > SINIR_S
            a_asar += sure_s(Lm, a90, a180, v) > SINIR_S
            st = []
            for bud in (False, True):
                ss = []
                for e in ("sol", "sag"):
                    d = duvar_takip(lab, e, budama=bud, hucre_m=hucre_m)
                    ss.append(sure_s(len(d) * hucre_m, *_donusler(d), v))
                st.append(ss)
            el += min(st[0]) <= SINIR_S
            el_bud += min(st[1]) <= SINIR_S
            el_iki += max(st[1]) <= SINIR_S
            E = lab.kenar_sayisi()
            dfs_m = (2 * E - (len(coz) - 1)) * hucre_m + hucre_m
            dfs_ok += sure_s(dfs_m, 2 * _tum_donus90(lab), len(lab.cikmazlar()), v) <= SINIR_S
        p = lambda k: "%%%d" % round(100.0 * k / n_tohum)
        out.append("| %dx%d (kenar %s m) | %.0f [%.0f-%.0f] | %s | %s | %s | %s | %s | %s |" % (
            n, n, ("%.1f" % (n * hucre_m)).replace(".", ","), sum(Ls) / len(Ls), min(Ls), max(Ls), p(tmin_asar), p(a_asar),
            p(el), p(el_bud), p(el_iki), p(dfs_ok)))
    return "\n".join(out)


# ------------------------------------------------------------------ algoritma istatistiği

def istatistik(boyut=17, n_tohum=50):
    print("boyut %dx%d, %d tohum, hucre %.2f m (ortalama [en az - en cok])" % (boyut, boyut, n_tohum, HUCRE_M))
    print("%-14s %-22s %-18s %-18s %-22s" % ("algoritma", "cozum hucre", "cikmaz", "cap hucre", "sol el hucre"))
    for alg in ("geri_izleme", "agac:0.75", "agac:0.5", "wilson"):
        cz, ck, cp, se = [], [], [], []
        for t in range(1, n_tohum + 1):
            lab = labirent_uret(boyut, boyut, t, algoritma=alg)
            cz.append(len(lab.cozum()))
            ck.append(len(lab.cikmazlar()))
            fm = lab.mesafeler(lab.finish[1])
            cp.append(max(lab.mesafeler(max(fm, key=fm.get)).values()))
            se.append(len(duvar_takip(lab, "sol")))
        g = lambda v: "%.0f [%d-%d]" % (sum(v) / len(v), min(v), max(v))
        print("%-14s %-22s %-18s %-18s %-22s" % (alg, g(cz), g(ck), g(cp), g(se)))


# ------------------------------------------------------------------ çizim (matplotlib)

def ciz(adlar=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrow, Polygon, Rectangle
    os.makedirs(GORSEL, exist_ok=True)
    adlar = adlar or sahne_listesi()
    for ad in adlar:
        h, s = oku(ad)
        L = s["labirent"]
        x0, y0, x1, y1 = L["sinir"]
        W, H = h["boyut_m"]
        olc = 0.55 if L["sutun"] <= 9 else (0.42 if L["sutun"] <= 13 else 0.36)
        fig = plt.figure(figsize=(2.0 + W * olc, 1.2 + H * olc), dpi=120)
        ax = fig.add_axes([0.07, 0.07, 0.86, 0.84])
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="#f7f7f4", edgecolor="none", zorder=0))
        for (xa, ya), (xb, yb) in [L["start"]["cizgi"]]:
            pass
        yol = L["cozum_yolu"]
        sc, fc = L["start"]["cizgi"], L["finish"]["cizgi"]
        sm = [(sc[0][0] + sc[1][0]) / 2, (sc[0][1] + sc[1][1]) / 2]
        fm = [(fc[0][0] + fc[1][0]) / 2, (fc[0][1] + fc[1][1]) / 2]
        tam = [sm] + yol + [fm]
        ax.plot([p[0] for p in tam], [p[1] for p in tam], color="#2b7bba", lw=2.2, alpha=0.85, zorder=2,
                solid_joinstyle="round", label="cozum yolu (%.1f m)" % L["cozum_uzunlugu_m"])
        lab, yer = labirent_sahneden(s)
        for hc in lab.cikmazlar():
            cx, cy = yer.merkez(hc)
            ax.plot(cx, cy, marker="x", ms=4, color="#b5b5b5", zorder=1)
        for xa, ya, xb, yb in h["duvarlar"]:
            ax.plot([xa, xb], [ya, yb], color="#1d1d1d", lw=2.0, solid_capstyle="projecting", zorder=3)
        ax.plot([sc[0][0], sc[1][0]], [sc[0][1], sc[1][1]], color="#2e9e4f", lw=5, zorder=4, solid_capstyle="butt")
        ax.plot([fc[0][0], fc[1][0]], [fc[0][1], fc[1][1]], color="#d62728", lw=5, zorder=4, solid_capstyle="butt")
        n = L["start"]["ic_normal"]
        fn = L["finish"]["ic_normal"]
        ax.text(sm[0] - n[0] * 0.55, sm[1] - n[1] * 0.55, "START", color="#2e9e4f", ha="center", va="center", fontsize=10,
                weight="bold", zorder=6)
        ax.text(fm[0] - fn[0] * 0.55, fm[1] - fn[1] * 0.55, "FINISH", color="#d62728", ha="center", va="center", fontsize=10,
                weight="bold", zorder=6)
        bx, by, th = L["start"]["poz"]
        c, sn = math.cos(th), math.sin(th)
        kose = [(-ROBOT_ARKA_M, -ROBOT_YAN_M), (ROBOT_ON_M, -ROBOT_YAN_M), (ROBOT_ON_M, ROBOT_YAN_M), (-ROBOT_ARKA_M, ROBOT_YAN_M)]
        ax.add_patch(Polygon([(bx + c * u - sn * v, by + sn * u + c * v) for u, v in kose], closed=True, facecolor="#ffd84d",
                             edgecolor="#8a6d00", lw=1, zorder=5))
        ax.add_patch(FancyArrow(bx, by, 0.45 * c, 0.45 * sn, width=0.04, head_width=0.16, head_length=0.14, color="#8a6d00",
                                zorder=6))
        ax.plot([x0 + 0.1, x0 + 0.1 + 2 * L["hucre_m"]], [y0 - 0.45, y0 - 0.45], color="black", lw=3, solid_capstyle="butt")
        ax.text(x0 + 0.1 + L["hucre_m"], y0 - 0.35, "2 hucre = %.1f m" % (2 * L["hucre_m"]), ha="center", va="bottom",
                fontsize=8)
        ax.set_aspect("equal")
        ax.set_xlim(x0 - 1.4, x1 + 1.4)
        ax.set_ylim(y0 - 1.4, y1 + 1.4)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_title("%s  -  %dx%d, hucre %.2f m, kenar %.1f m | cozum %.1f m (%d hucre), gecit %.1f m, cikmaz %d"
                     % (ad, L["satir"], L["sutun"], L["hucre_m"], L["sutun"] * L["hucre_m"], L["cozum_uzunlugu_m"],
                        L["cozum_hucre_sayisi"], L["toplam_gecit_m"], L["cikmaz_sayisi"]), fontsize=9, loc="left")
        ax.legend(loc="upper right", fontsize=8, frameon=True, bbox_to_anchor=(1.0, 1.0))
        yol_png = os.path.join(GORSEL, ad + ".png")
        fig.savefig(yol_png, bbox_inches="tight")
        plt.close(fig)
        print(yol_png)


# ------------------------------------------------------------------ geometrik kontroller (bağımlılıksız)

_HG = None


def _hg():
    """sahte_esp32.harita geometri yardımcıları (bir kez yüklenir)."""
    global _HG
    if _HG is None:
        yol = os.path.join(KOD, "araclar")
        if yol not in sys.path:
            sys.path.insert(0, yol)
        from sahte_esp32 import harita as _HG_mod
        _HG = _HG_mod
    return _HG


def _parca_uzaklik(a, b):
    """İki parça arası en kısa uzaklık (kesişiyorsa 0)."""
    hg = _hg()
    _nokta_parca_uzaklik, _parca_kesisir = hg._nokta_parca_uzaklik, hg._parca_kesisir
    if _parca_kesisir(a, b):
        return 0.0
    return min(_nokta_parca_uzaklik(a[0], a[1], b), _nokta_parca_uzaklik(a[2], a[3], b),
               _nokta_parca_uzaklik(b[0], b[1], a), _nokta_parca_uzaklik(b[2], b[3], a))


def ayak_izi(x, y, th, pay=0.0):
    c, s = math.cos(th), math.sin(th)
    k = [(-ROBOT_ARKA_M - pay, -ROBOT_YAN_M - pay), (ROBOT_ON_M + pay, -ROBOT_YAN_M - pay),
         (ROBOT_ON_M + pay, ROBOT_YAN_M + pay), (-ROBOT_ARKA_M - pay, ROBOT_YAN_M + pay)]
    return [(x + c * u - s * v, y + s * u + c * v) for u, v in k]


def aciklik(duvarlar, kose):
    """Ayak izi çokgeni ile duvarlar arası en küçük açıklık (m; levha yarı kalınlığı düşülmüş). İçeri girme -> negatif."""
    _icinde = _hg()._icinde
    kenar = [kose[i] + kose[(i + 1) % len(kose)] for i in range(len(kose))]
    en = 1e9
    xs = [p[0] for p in kose]
    ys = [p[1] for p in kose]
    for p in duvarlar:
        if max(p[0], p[2]) < min(xs) - 1.0 or min(p[0], p[2]) > max(xs) + 1.0 or \
           max(p[1], p[3]) < min(ys) - 1.0 or min(p[1], p[3]) > max(ys) + 1.0:
            continue
        if _icinde(kose, p[0], p[1]) or _icinde(kose, p[2], p[3]):
            return -1.0
        for k in kenar:
            en = min(en, _parca_uzaklik(tuple(p), tuple(k)))
    return en - IC_DUVAR_M / 2


def geometrik_kontrol(ad):
    """Çözüm yolu boyunca ayak izi ve her hücrede arka dingil etrafında tam tur; açıklıklar; mükemmellik. Döner sözlük."""
    h, s = oku(ad)
    L = s["labirent"]
    lab, yer = labirent_sahneden(s)
    du = h["duvarlar"]
    bag, muk, E = lab.mukemmel_mi()
    # 1) çözüm yolu: START pozundan, hücre merkezlerinden, FINISH çizgisinin 0,6 m dışına; 0,05 m adım, yol yönüne bakan iz
    sc, fc = L["start"]["cizgi"], L["finish"]["cizgi"]
    fn = L["finish"]["ic_normal"]
    fm = [(fc[0][0] + fc[1][0]) / 2, (fc[0][1] + fc[1][1]) / 2]
    bx, by, th0 = L["start"]["poz"]
    hat = [[bx, by]] + L["cozum_yolu"] + [fm, [fm[0] - fn[0] * 0.6, fm[1] - fn[1] * 0.6]]
    en_yol = 1e9
    for (ax_, ay_), (bx_, by_) in zip(hat, hat[1:]):
        Lp = math.hypot(bx_ - ax_, by_ - ay_)
        if Lp < 1e-9:
            continue
        th = math.atan2(by_ - ay_, bx_ - ax_)
        for k in range(int(Lp / 0.05) + 1):
            t = min(1.0, k * 0.05 / Lp)
            en_yol = min(en_yol, aciklik(du, ayak_izi(ax_ + (bx_ - ax_) * t, ay_ + (by_ - ay_) * t, th)))
    # 2) her hücrede arka dingil hücre merkezinde, 0-360° (5°) yerinde dönüş; ayrıca gövde merkezi etrafında
    en_don = en_don_merkez = 1e9
    for r in range(lab.satir):
        for c in range(lab.sutun):
            cx, cy = yer.merkez((r, c))
            for i in range(72):
                th = math.radians(5 * i)
                gx, gy = cx + ARKA_DINGIL_M * math.cos(th), cy + ARKA_DINGIL_M * math.sin(th)
                en_don = min(en_don, aciklik(du, ayak_izi(gx, gy, th)))
                en_don_merkez = min(en_don_merkez, aciklik(du, ayak_izi(cx, cy, th)))
    # 3) START pozunda temassız; START'ta arka dingil etrafında dönüşte gövde merkezi çizgiyi geçmiyor
    en_bas = aciklik(du, ayak_izi(bx, by, th0))
    sn = L["start"]["ic_normal"]
    gx, gy = bx - sn[0] * ARKA_DINGIL_M, by - sn[1] * ARKA_DINGIL_M       # arka dingil
    smx, smy = (sc[0][0] + sc[1][0]) / 2, (sc[0][1] + sc[1][1]) / 2
    en_ic = min(((gx + ARKA_DINGIL_M * math.cos(math.radians(a)) - smx) * sn[0] +
                 (gy + ARKA_DINGIL_M * math.sin(math.radians(a)) - smy) * sn[1]) for a in range(360))
    # 4) açıklıklar gerçekten açık: çizgi ortasından dışarı / içeri, açıklık genişliğinde hiçbir duvar parçası yok
    acik_ok = True
    for cz in (sc, fc):
        for p in du:
            if _parca_uzaklik(tuple(p), (cz[0][0], cz[0][1], cz[1][0], cz[1][1])) < 1e-6:
                ortak_uc = any(math.hypot(p[i] - cz[j][0], p[i + 1] - cz[j][1]) < 1e-6 for i in (0, 2) for j in (0, 1))
                ic = _parca_uzaklik(tuple(p), ((cz[0][0] * 0.9 + cz[1][0] * 0.1), (cz[0][1] * 0.9 + cz[1][1] * 0.1),
                                               (cz[0][0] * 0.1 + cz[1][0] * 0.9), (cz[0][1] * 0.1 + cz[1][1] * 0.9)))
                if not ortak_uc or ic < 1e-6:
                    acik_ok = False
    # dış sınırda yalnız iki açıklık
    x0, y0, x1, y1 = L["sinir"]
    sinir_bosluk = 0
    for r in range(lab.satir):
        for c in range(lab.sutun):
            v = lab.acik[r][c]
            sinir_bosluk += (r == 0 and v & K > 0) + (r == lab.satir - 1 and v & G > 0) + \
                            (c == 0 and v & B > 0) + (c == lab.sutun - 1 and v & D > 0)
    ok = bag and muk and en_yol > 0.05 and en_don > 0.0 and en_bas > 0.05 and en_ic > 0.0 and acik_ok and sinir_bosluk == 2
    return {"ok": ok, "bagli": bag, "dongusuz": muk, "gecit": E, "en_aciklik_yol_m": en_yol, "en_aciklik_donus_m": en_don,
            "en_aciklik_donus_merkez_m": en_don_merkez, "en_aciklik_start_m": en_bas, "start_donus_ic_m": en_ic,
            "acikliklar_acik": acik_ok, "sinir_acikligi": sinir_bosluk}


# ------------------------------------------------------------------ doğrulama (mujoco)

def _yollar():
    for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
        if _y not in sys.path:
            sys.path.insert(0, _y)


def _isinlar_cikis(L, px, py, a, t, kacan_noktasi):
    """Kaçan ışın labirentten yalnız START / FINISH açıklığından çıkmış olmalı: sınıra geldiği nokta açıklık çizgisinde mi."""
    x0, y0, x1, y1 = L["sinir"]
    dx, dy = math.cos(a), math.sin(a)
    tt = []
    if abs(dx) > 1e-12:
        tt += [(x0 - px) / dx, (x1 - px) / dx]
    if abs(dy) > 1e-12:
        tt += [(y0 - py) / dy, (y1 - py) / dy]
    tt = [v for v in tt if v > 1e-9]
    tc = min(v for v in tt if (x0 - 1e-6 <= px + dx * v <= x1 + 1e-6 and y0 - 1e-6 <= py + dy * v <= y1 + 1e-6))
    qx, qy = px + dx * tc, py + dy * tc
    for k in ("start", "finish"):
        (ax_, ay_), (bx_, by_) = L[k]["cizgi"]
        if min(ax_, bx_) - 1e-6 <= qx <= max(ax_, bx_) + 1e-6 and min(ay_, by_) - 1e-6 <= qy <= max(ay_, by_) + 1e-6:
            return k
    return None


def dogrula(adlar, sure_olc=True):
    _yollar()
    import ctypes
    try:                                                    # düşük öncelik (BELOW_NORMAL); tanıtıcı 64 bit: restype şart
        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = ctypes.c_void_p
        k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass
    import time
    import dunya as D
    if not D.FIZIK_VAR:
        print("mujoco yok: %s" % D.FIZIK_HATA)
        return 2
    import gorunum3b as G3
    tamam = True
    sonuc = {}
    for ad in adlar:
        h, s = oku(ad)
        L = s["labirent"]
        g = geometrik_kontrol(ad)
        t0 = time.perf_counter()
        p = G3.Pencere(ad)                                  # 3B pencerenin kendi kurulumu (görüntüleyici açılmadan)
        t_kur = time.perf_counter() - t0
        w = p.w
        bas_temas = w.temas_engel()
        x0, y0, _, yaw0, _, _ = w.poz()
        p.adim(5000)                                        # 5 s sanal: devreye alınmadı, sürüş yok
        x1, y1, z1, yaw1, _, _ = w.poz()
        temas = w.temas_engel()
        kayma = math.hypot(x1 - x0, y1 - y0)
        dyaw = abs(math.degrees(yaw1 - yaw0))
        # LiDAR: çözüm yolundaki her hücre merkezinde 360 ışın (1°) x z 0,10 / 0,20 / 0,295 m (3B) + 2B. Kaçan ışın yalnız
        # START / FINISH açıklığından çıkabilir (duvar arası sızıntı yok).
        n_isin = kacan = sizan = kacan2 = sizan2 = 0
        en_uzak = 0.0
        hh = p.harita
        for px, py in L["cozum_yolu"]:
            for z in (0.10, 0.20, 0.295):
                for i in range(360):
                    a = math.radians(i + 0.5)
                    r = w.isin([px, py, z], [math.cos(a), math.sin(a), 0.0], 60.0)
                    n_isin += 1
                    if r is None:
                        kacan += 1
                        if _isinlar_cikis(L, px, py, a, None, None) is None:
                            sizan += 1
                    else:
                        en_uzak = max(en_uzak, r[0])
            for i in range(360):
                a = math.radians(i + 0.5)
                if hh.isin(px, py, a, 60.0) is None:
                    kacan2 += 1
                    if _isinlar_cikis(L, px, py, a, None, None) is None:
                        sizan2 += 1
        # FINISH dışında boşluk: FINISH çizgisinin 1 m dışından dışarı bakan yarı düzlemde ışınların hepsi kaçar
        fc, fn = L["finish"]["cizgi"], L["finish"]["ic_normal"]
        fx, fy = (fc[0][0] + fc[1][0]) / 2 - fn[0] * 1.0, (fc[0][1] + fc[1][1]) / 2 - fn[1] * 1.0
        dis_aci = math.atan2(-fn[1], -fn[0])
        dis_kacan = sum(1 for i in range(-80, 81, 2)
                        if w.isin([fx, fy, 0.295], [math.cos(dis_aci + math.radians(i)), math.sin(dis_aci + math.radians(i)), 0.0], 60.0) is None)
        dis_ok = dis_kacan == 81
        rtf = None
        if sure_olc:
            # başsız adım süresi: yalnız fizik (FizikDunya.adim, motorlar boşta) ve firmware çekirdeğiyle (Pencere.adim)
            t0 = time.perf_counter()
            w.adim(5.0)
            t_fiz = time.perf_counter() - t0
            t0 = time.perf_counter()
            p.adim(5000)
            t_pen = time.perf_counter() - t0
            rtf = (5.0 / t_fiz, 5.0 / t_pen)
        ok = g["ok"] and (not bas_temas) and (not temas) and kayma < 0.005 and dyaw < 0.5 and sizan == 0 and sizan2 == 0 and dis_ok
        tamam = tamam and ok
        sonuc[ad] = dict(g, geom=w.m.ngeom, kurulum_s=t_kur, bas_temas=bas_temas, temas_5s=temas, kayma_mm=kayma * 1000,
                         dyaw=dyaw, isin=n_isin, kacan=kacan, sizan=sizan, kacan2=kacan2, sizan2=sizan2, en_uzak=en_uzak,
                         finish_disi_bosluk=dis_ok, rtf=rtf, ok=ok)
        print("%-18s %s | geom %4d, kurulum %.2f s | START temas %s, 5 s sonra %s, kayma %.2f mm, yaw %.3f der | "
              "LiDAR 3B %d isin, kacan %d (sizan %d), 2B kacan %d (sizan %d), en uzak %.1f m, FINISH disi bosluk %s | "
              "aciklik yol %.3f / donus(arka dingil) %.3f / donus(merkez) %.3f / START %.3f m, START donus ic %.3f m | "
              "mukemmel %s, acikliklar %s (%d) | RTF fizik %s, cekirdekle %s"
              % (ad, "TAMAM" if ok else "KALDI", w.m.ngeom, t_kur, bas_temas, temas, kayma * 1000, dyaw, n_isin, kacan,
                 sizan, kacan2, sizan2, en_uzak, dis_ok, g["en_aciklik_yol_m"], g["en_aciklik_donus_m"],
                 g["en_aciklik_donus_merkez_m"], g["en_aciklik_start_m"], g["start_donus_ic_m"],
                 g["bagli"] and g["dongusuz"], g["acikliklar_acik"], g["sinir_acikligi"],
                 "%.1f" % rtf[0] if rtf else "-", "%.1f" % rtf[1] if rtf else "-"), flush=True)
        del p, w
    with open(os.path.join(BURASI, "testler", "dogrulama_son.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    return 0 if tamam else 1


# ------------------------------------------------------------------ komut satırı

def _kenar_arg(v):
    k, _, i = v.partition(":")
    return (k, int(i or 0))


def main(argv):
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Lale labirent sahneleri")
    alt = ap.add_subparsers(dest="is_")
    u = alt.add_parser("uret")
    u.add_argument("--satir", type=int)
    u.add_argument("--sutun", type=int)
    u.add_argument("--tohum", type=int, default=1)
    u.add_argument("--hucre", type=float, default=HUCRE_M)
    u.add_argument("--start", type=_kenar_arg, default=("ust", 0), help="kenar:hucre, ör. ust:0 (varsayılan)")
    u.add_argument("--finish", type=_kenar_arg, default=("alt", -1), help="kenar:hucre, ör. alt:-1 (varsayılan)")
    u.add_argument("--algoritma", default="geri_izleme")
    u.add_argument("--ad")
    u.add_argument("adlar", nargs="*")
    c = alt.add_parser("ciz")
    c.add_argument("adlar", nargs="*")
    d = alt.add_parser("dogrula")
    d.add_argument("adlar", nargs="*")
    d.add_argument("--sure-yok", action="store_true")
    fz = alt.add_parser("fizibilite")
    fz.add_argument("--dagilim", action="store_true", help="boyut başına 100 tohum, 15 dk oranları")
    fz.add_argument("--hucre", type=float, default=HUCRE_M)
    fz.add_argument("--v", type=float, default=0.30)
    fz.add_argument("--algoritma", default="geri_izleme")
    st = alt.add_parser("istatistik")
    st.add_argument("--boyut", type=int, default=17)
    st.add_argument("--tohum-sayisi", type=int, default=50)
    a = ap.parse_args(argv)
    if a.is_ == "uret":
        if a.satir:
            sutun = a.sutun or a.satir
            ad = a.ad or ad_uret(a.satir, sutun, a.tohum, a.hucre)
            uret_tek(ad, satir=a.satir, sutun=sutun, tohum=a.tohum, hucre_m=a.hucre, start=a.start, finish=a.finish,
                     algoritma=a.algoritma)
        else:
            uret(a.adlar or None)
        return 0
    if a.is_ == "ciz":
        ciz(a.adlar or None)
        return 0
    if a.is_ == "dogrula":
        return dogrula(a.adlar or list(SAHNE_AILESI), sure_olc=not a.sure_yok)
    if a.is_ == "fizibilite":
        if a.dagilim:
            print(dagilim(v=a.v, hucre_m=a.hucre, algoritma=a.algoritma))
        else:
            print(fizibilite_md()[0])
        return 0
    if a.is_ == "istatistik":
        istatistik(a.boyut, a.tohum_sayisi)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
