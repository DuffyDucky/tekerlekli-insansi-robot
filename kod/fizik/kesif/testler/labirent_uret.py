"""Deneme labirenti üretici (yalnız keşif testleri / eğitim için; depo sahnelerine yazmaz).

Döngüsüz ("mükemmel") ızgara labirenti: DFS geri izleme ya da Prim. Duvarlar kalın kutu (`engeller` kutu), eş
doğrultulu bitişik duvarlar birleştirilir. START batı kenarında rastgele bir satırda, FINISH öbür üç kenardan
rastgele bir hücrede. Labirentin çevresinde `pay_m` boş dış alan (cevre_duvari yok: dış alandan ışın dönmez).
Çıktı biçimi: `kod/SIMULASYON.md` "Yeni harita" + `labirent` alanı (sahne.py'nin okuduğu adlar).

    py -3 kod\\fizik\\kesif\\testler\\labirent_uret.py 9 9 --hucre 1.35 --tohum 1 --ad dene_9x9_t1
"""

import argparse
import json
import math
import os
import random
from collections import deque

KLASOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "labirentler")


def _dfs(R, C, rng):
    acik = set()      # ((r, c), (r2, c2)) sıralı çift
    gor = {(0, 0)}
    yigin = [(0, 0)]
    while yigin:
        r, c = yigin[-1]
        kom = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if 0 <= r + dr < R and 0 <= c + dc < C and (r + dr, c + dc) not in gor]
        if not kom:
            yigin.pop()
            continue
        n = rng.choice(kom)
        acik.add(tuple(sorted([(r, c), n])))
        gor.add(n)
        yigin.append(n)
    return acik


def _prim(R, C, rng):
    acik = set()
    gor = {(rng.randrange(R), rng.randrange(C))}
    kenar = []

    def ekle(h):
        r, c = h
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (r + dr, c + dc)
            if 0 <= n[0] < R and 0 <= n[1] < C and n not in gor:
                kenar.append((h, n))
    for h in list(gor):
        ekle(h)
    while kenar:
        k = kenar.pop(rng.randrange(len(kenar)))
        if k[1] in gor:
            continue
        acik.add(tuple(sorted(k)))
        gor.add(k[1])
        ekle(k[1])
    return acik


def uret(R, C, hucre=1.35, kalinlik=0.10, tohum=1, yontem="dfs", pay_m=4.0, ad=None):
    rng = random.Random(tohum)
    acik = (_dfs if yontem == "dfs" else _prim)(R, C, rng)
    m = pay_m
    # START: batı kenarı (c = -1 yönü), FINISH: K / D / G kenarlarından biri
    rs = rng.randrange(R)
    adaylar = [("dogu", r, C - 1) for r in range(R)] + [("kuzey", R - 1, c) for c in range(C)] + \
              [("guney", 0, c) for c in range(C)]
    adaylar = [a for a in adaylar if not (a[1] == rs and a[2] == 0)]
    fk, fr, fc = rng.choice(adaylar)

    def x(c):
        return m + c * hucre

    def y(r):
        return m + r * hucre
    # yatay duvar çizgileri: k = 0..R (y = y(k)); hücre (k-1, c) ile (k, c) arası
    kutular = []
    t = kalinlik

    def yatay(k, c0, c1):
        kutular.append({"tur": "kutu", "x": round(x(c0) - t / 2, 4), "y": round(y(k) - t / 2, 4),
                        "g": round((c1 - c0) * hucre + t, 4), "d": t})

    def dikey(k, r0, r1):
        kutular.append({"tur": "kutu", "x": round(x(k) - t / 2, 4), "y": round(y(r0) - t / 2, 4),
                        "g": t, "d": round((r1 - r0) * hucre + t, 4)})
    for k in range(R + 1):
        bas = None
        for c in range(C + 1):
            if c < C:
                if k == 0:
                    duvar = not (fk == "guney" and fc == c)
                elif k == R:
                    duvar = not (fk == "kuzey" and fc == c)
                else:
                    duvar = tuple(sorted([(k - 1, c), (k, c)])) not in acik
            else:
                duvar = False
            if duvar and bas is None:
                bas = c
            if not duvar and bas is not None:
                yatay(k, bas, c)
                bas = None
    for k in range(C + 1):
        bas = None
        for r in range(R + 1):
            if r < R:
                if k == 0:
                    duvar = r != rs
                elif k == C:
                    duvar = not (fk == "dogu" and fr == r)
                else:
                    duvar = tuple(sorted([(r, k - 1), (r, k)])) not in acik
            else:
                duvar = False
            if duvar and bas is None:
                bas = r
            if not duvar and bas is not None:
                dikey(k, bas, r)
                bas = None
    # START / FINISH çizgileri (dış duvar ekseninde) ve pozlar
    sc = [x(0), y(rs), x(0), y(rs + 1)]
    if fk == "dogu":
        fcz = [x(C), y(fr), x(C), y(fr + 1)]
        fdis = (x(C) + 1.0, y(fr) + hucre / 2)
    elif fk == "kuzey":
        fcz = [x(fc), y(R), x(fc + 1), y(R)]
        fdis = (x(fc) + hucre / 2, y(R) + 1.0)
    else:
        fcz = [x(fc), y(0), x(fc + 1), y(0)]
        fdis = (x(fc) + hucre / 2, y(0) - 1.0)
    sp = [x(0) + hucre / 2, y(rs) + hucre / 2, 0.0]
    # çözüm: hücre BFS
    on = {(rs, 0): None}
    q = deque([(rs, 0)])
    while q:
        h = q.popleft()
        if h == (fr, fc):
            break
        r, c = h
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (r + dr, c + dc)
            if 0 <= n[0] < R and 0 <= n[1] < C and n not in on and tuple(sorted([h, n])) in acik:
                on[n] = h
                q.append(n)
    yol = []
    h = (fr, fc)
    while h is not None:
        yol.append([round(x(h[1]) + hucre / 2, 4), round(y(h[0]) + hucre / 2, 4)])
        h = on[h]
    yol.reverse()
    cozum = [[round(x(0) - 1.0, 4), round(y(rs) + hucre / 2, 4)]] + yol + [[round(fdis[0], 4), round(fdis[1], 4)]]
    L = sum(math.hypot(cozum[i + 1][0] - cozum[i][0], cozum[i + 1][1] - cozum[i][1]) for i in range(1, len(cozum) - 1))
    ad = ad or "dene_%dx%d_t%d" % (R, C, tohum)
    return {
        "ad": ad,
        "aciklama": "Keşif deneme labirenti (%s, %dx%d, hücre %.2f m, duvar %.2f m, tohum %d). Üretici: "
                    "kod/fizik/kesif/testler/labirent_uret.py" % (yontem, R, C, hucre, kalinlik, tohum),
        "boyut_m": [round(C * hucre + 2 * m, 4), round(R * hucre + 2 * m, 4)],
        "cevre_duvari": False,
        "duvarlar": [],
        "engeller": kutular,
        "baslangic": {"x": sp[0], "y": sp[1], "aci_derece": 0.0},
        "labirent": {
            "hucre_m": hucre, "satir": R, "sutun": C, "duvar_kalinligi_m": kalinlik, "uretici": yontem,
            "tohum": tohum, "merkez": [x(0) + C * hucre / 2, y(0) + R * hucre / 2],
            "start": {"cizgi": sc}, "finish": {"cizgi": fcz, "kenar": fk},
            "start_poz": [sp[0], sp[1], 0.0], "cozum_yolu": cozum, "cozum_uzunlugu_m": round(L, 3),
        },
    }


def kaydet(v, klasor=KLASOR):
    os.makedirs(klasor, exist_ok=True)
    yol = os.path.join(klasor, v["ad"] + ".json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=1)
    return yol


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("satir", type=int)
    p.add_argument("sutun", type=int)
    p.add_argument("--hucre", type=float, default=1.35)
    p.add_argument("--kalinlik", type=float, default=0.10)
    p.add_argument("--tohum", type=int, default=1)
    p.add_argument("--yontem", default="dfs")
    p.add_argument("--ad", default=None)
    a = p.parse_args()
    print(kaydet(uret(a.satir, a.sutun, a.hucre, a.kalinlik, a.tohum, a.yontem, ad=a.ad)))
