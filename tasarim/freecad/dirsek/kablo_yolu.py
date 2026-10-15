# Kol kablo yolu (duzeltme plani M1) - model + kalici kontrol yardimcilari (FreeCAD 1.1, Part + numpy)
# Tanim: ../arayuz.py KOL_KABLO (sag kol, omuz yereli, ev pozu; sol kol = X aynasi). Bu dosya geometri uretmez; dirsek_montaj.py
# cagirir ve sonucu dirsek-analiz.json "kablo" alanina yazar.
#
# Serbest kablo bolumu (lop) modeli: duzlemsel ayrik elastika. Uclarin konumu ve cikis tegeti baglama noktasinda sabit, boy L
# sabit, bukulme enerjisi (sum theta^2) en az; N parca, kisitli en kucuk kareler (SQP / Lagrange). Yassi kablo lop duzleminde
# kalir (genislik yonunde rijit); duzlem disi koordinat boy boyunca dogrusal ya da son 'gecis' mm'de yumusak gecer.
# Eklem araliginda her pozda: en kucuk egrilik yaricapi (>= r_dinamik), kiris (< L: kablo hic gerilmez), demet zarfi
# (cevrel yaricap) ile parcalar arasi en kucuk bosluk (>= pay_bosluk). Sabit yollar: cokgen; her kosede r_sabit yaricapli yay
# sigmali (komsu kenar paylari), kablo yassi yatar (zarf = demet kalinligi / 2).
import math
import numpy as np
import FreeCAD as App
import Part

V = App.Vector


# ---------------------------------------------------------------------------------------------- elastika
def elastika(p0, a0, p1, a1, L, N=120, th0=None, d_ipucu=None, iter_=800, tol=1e-9):
    """p0, p1: (u, v); a0: cikis tegeti acisi, a1: varis tegeti acisi (rad). Doner (noktalar (N+1)x2, donus acilari, yakinsadi)."""
    ds = L / N
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = math.atan2(math.sin(a1 - a0), math.cos(a1 - a0))
    if d_ipucu is not None:                    # surekli dal: onceki toplam donuse en yakin 2*pi*k temsilcisi
        d = d + 2 * math.pi * round((d_ipucu - d) / (2 * math.pi))
    if th0 is None:
        k = np.arange(1, N)
        th = np.full(N - 1, d / (N - 1)) + 0.6 * (2 * math.pi / N) * np.cos(2 * math.pi * k / N)
    else:
        th = np.array(th0, float) + (d - float(np.sum(th0))) / (N - 1)
    ok = False
    for it in range(iter_):
        phi = a0 + np.concatenate([[0.0], np.cumsum(th)])
        c, s = np.cos(phi), np.sin(phi)
        end = p0 + ds * np.array([c.sum(), s.sum()])
        g = np.array([end[0] - p1[0], end[1] - p1[1], th.sum() - d])
        if np.abs(g[:2]).max() < tol and abs(g[2]) < 1e-12 and it > 3:
            ok = True
            break
        cs_s = np.cumsum((-s * ds)[::-1])[::-1]
        cs_c = np.cumsum((c * ds)[::-1])[::-1]
        J = np.vstack([cs_s[1:], cs_c[1:], np.ones(N - 1)])
        lam = np.linalg.solve(J @ J.T, J @ th - g)
        adim = J.T @ lam - th
        m = np.abs(adim).max()
        if m > 0.3:
            adim *= 0.3 / m
        th = th + adim
    phi = a0 + np.concatenate([[0.0], np.cumsum(th)])
    pts = p0 + ds * np.vstack([np.zeros(2), np.cumsum(np.stack([np.cos(phi), np.sin(phi)], 1), 0)])
    return pts, th, ok


def _eksen(duzlem):
    """Lop duzlemi: 'x' -> duzlem (z, y), dik eksen x; 'z' -> duzlem (x, y), dik eksen z."""
    return {"x": ((2, 1), 0), "z": ((0, 1), 2)}[duzlem]


def lop_coz(lt, rel_yer, pozlar, N=120):
    """lt: arayuz lop tanimi; rel_yer(poz) -> hareketli grubun (M) sabit grup (F) cercevesindeki yerlesimi (App.Placement).
    Doner: [dict(poz, nokta=[V], r_min, kiris, yakinsadi)] (noktalar sabit grup cercevesinde, omuz yereli ev pozu)."""
    (iu, iv), iw = _eksen(lt["duzlem"])
    F, tF = V(*lt["F"]), V(*lt["F_teget"])
    L = lt["L"]
    sonuc, th0 = [], None
    for poz in pozlar:
        pl = rel_yer(poz)
        M, tM = pl.multVec(V(*lt["M"])), pl.Rotation.multVec(V(*lt["M_teget"]))
        pts, th, ok = elastika((M[iu], M[iv]), math.atan2(tM[iv], tM[iu]), (F[iu], F[iv]), math.atan2(tF[iv], tF[iu]), L, N=N,
                               th0=th0, d_ipucu=None if th0 is None else float(np.sum(th0)))
        th0 = th
        n = len(pts)
        s = np.linspace(0.0, 1.0, n)
        gecis = lt.get("gecis")
        if gecis:                                   # duzlem disi: son 'gecis' mm'de yumusak (smoothstep)
            s0 = max(0.0, 1.0 - gecis / L)
            t = np.clip((s - s0) / max(1e-9, 1.0 - s0), 0.0, 1.0)
            w = M[iw] + (F[iw] - M[iw]) * (t * t * (3 - 2 * t))
        else:
            w = M[iw] + (F[iw] - M[iw]) * s
        nokta = []
        for i in range(n):
            q = [0.0, 0.0, 0.0]
            q[iu], q[iv], q[iw] = float(pts[i][0]), float(pts[i][1]), float(w[i])
            nokta.append(V(*q))
        ds = L / N
        r_min = ds / float(np.abs(th).max()) if np.abs(th).max() > 1e-12 else 1e9
        sonuc.append(dict(poz=poz, nokta=nokta, r_min=r_min, kiris=(M - F).Length, yakinsadi=bool(ok)))
    return sonuc


# ---------------------------------------------------------------------------------------------- olcum
def cokgen(nokta, bas=0.0, son=0.0):
    """Nokta dizisinin bastan 'bas', sondan 'son' mm kirpilmis cokgen kenari."""
    p = [V(*q) if not isinstance(q, App.Vector) else q for q in nokta]
    uz = [(b - a).Length for a, b in zip(p[:-1], p[1:])]
    top = sum(uz)

    def nokta_at(d):
        acc = 0.0
        for a, b, l in zip(p[:-1], p[1:], uz):
            if acc + l >= d:
                return a + (b - a) * ((d - acc) / max(l, 1e-12))
            acc += l
        return p[-1]
    d0, d1 = bas, top - son
    q = [nokta_at(d0)]
    acc = 0.0
    for b, l in zip(p[1:], uz):
        acc += l
        if d0 < acc < d1:
            q.append(b)
    q.append(nokta_at(d1))
    return Part.makePolygon(q), top


def en_yakin(kenar, sekiller, pay_kutu=30.0):
    """kenar ile (ad, shape) listesindeki en yakin sekil: (mesafe, ad). Sinir kutusu on elemesi."""
    bb = App.BoundBox(kenar.BoundBox)
    bb.enlarge(pay_kutu)
    best = (1e9, None)
    for ad, sh in sekiller:
        if not sh.BoundBox.intersect(bb):
            continue
        d = sh.distToShape(kenar)[0]
        if d < best[0]:
            best = (d, ad)
    return best


def kose_yaricap(nokta):
    """Cokgen kosesine sigan en buyuk yay yaricapi (ic kenarlar iki koseyle yari yariya paylasilir). Doner (en kucuk, kose sirasi)."""
    p = [V(*q) for q in nokta]
    n = len(p)
    uz = [(b - a).Length for a, b in zip(p[:-1], p[1:])]
    sonuc = []
    for i in range(1, n - 1):
        a, b = (p[i] - p[i - 1]), (p[i + 1] - p[i])
        if a.Length < 1e-9 or b.Length < 1e-9:
            continue
        cosx = max(-1.0, min(1.0, a.dot(b) / (a.Length * b.Length)))
        aci = math.acos(cosx)                       # yon degisimi
        if aci < 1e-6:
            continue
        l1 = uz[i - 1] * (1.0 if i - 1 == 0 else 0.5)
        l2 = uz[i] * (1.0 if i == n - 2 else 0.5)
        sonuc.append((min(l1, l2) / math.tan(aci / 2.0), i, math.degrees(aci)))
    if not sonuc:
        return 1e9, None, []
    m = min(sonuc)
    return m[0], m[1], sonuc


def demet(serit_sayisi, serit):
    """Demet: genislik, kalinlik, cevrel yaricap (lop), yassi yari kalinlik (sabit yol)."""
    w, t = serit
    k = serit_sayisi * t
    return dict(genislik=w, kalinlik=k, r_lop=math.hypot(w, k) / 2.0, r_sabit=k / 2.0)


def r_sinir(KK, serit_sayisi):
    """Merkez cizgisi icin bukulme siniri: en icteki serit kat x kalinlik; demet merkezi ondan (n-1) t / 2 disarida."""
    t = KK["serit"][1]
    ek = (serit_sayisi - 1) * t / 2.0
    return KK["r_dinamik_kat"] * t + ek, KK["r_sabit_kat"] * t + ek
