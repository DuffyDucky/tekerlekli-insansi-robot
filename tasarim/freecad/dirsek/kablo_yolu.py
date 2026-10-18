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


# ---------------------------------------------------------------------------------------------- S1 doner U-lop kaseti
# (duzeltme plani M1 / S1, 15 Ekim 2026; arayuz.KOL_KABLO["s1"], planlama/adim2/S1-kaset.md)
# Yuvarlanan U: ic kosu tambura (r_i, demet merkez cizgisi) sarili ve tamburla doner, dis kosu sabit duvara (r_o) yaslanir. Serbest
# parca (U) temasli duzlemsel elastikadir: ayrilma noktalarinda egrilik surekli (puruzsuz temasta noktasal moment yok): icte +1/r_i,
# dista -1/r_o; parca boyunca ic kuvvet sabit. Atis yontemi (RK4 + fsolve). Sekil pozdan bagimsiz (yalniz doner); bag noktalari
# yalniz U'nun konumunu belirler: L = r_i a_i + l_U + r_o a_o (a_i = psi_U - psi_tambur_bagi, a_o = psi_U + delta - psi_duvar_bagi).
def psi_yz(psi, r):
    """S1 ekseni etrafinda aci psi (derece; psi = atan2(-z, y): +Y 0, arka 90, asagi 180, on 270) ve yaricap -> (y, z)."""
    a = math.radians(psi)
    return r * math.cos(a), -r * math.sin(a)


def yz_psi(y, z):
    return math.degrees(math.atan2(-z, y)) % 360.0, math.hypot(y, z)


def u_lop(ri, ro, M=400):
    """Temasli U: ic daire ri (CCW, egrilik +1/ri) -> dis daire ro (CW, -1/ro). Doner dict: R_min, l (serbest boy), delta (dis temasin
    ic ayrilmaya gore acisi, derece), pol (derece, s boyunca), r, k (egrilik), s."""
    from scipy.optimize import fsolve

    def ent(Fx, Fy, l, kayit=False):
        h = l / M
        x, y, t, k = ri, 0.0, math.pi / 2, 1.0 / ri
        out = [(x, y, t, k)]

        def f(x, y, t, k):
            return (math.cos(t), math.sin(t), k, Fx * math.sin(t) - Fy * math.cos(t))
        for _ in range(M):
            a = f(x, y, t, k)
            b = f(x + h / 2 * a[0], y + h / 2 * a[1], t + h / 2 * a[2], k + h / 2 * a[3])
            c = f(x + h / 2 * b[0], y + h / 2 * b[1], t + h / 2 * b[2], k + h / 2 * b[3])
            d = f(x + h * c[0], y + h * c[1], t + h * c[2], k + h * c[3])
            x += h / 6 * (a[0] + 2 * b[0] + 2 * c[0] + d[0])
            y += h / 6 * (a[1] + 2 * b[1] + 2 * c[1] + d[1])
            t += h / 6 * (a[2] + 2 * b[2] + 2 * c[2] + d[2])
            k += h / 6 * (a[3] + 2 * b[3] + 2 * c[3] + d[3])
            if kayit:
                out.append((x, y, t, k))
        return np.array(out) if kayit else (x, y, t, k)

    def artik(v):
        x, y, t, k = ent(v[0], v[1], v[2])
        b = math.atan2(y, x)
        return [math.hypot(x, y) - ro, math.cos(t - b), k + 1.0 / ro]
    h = ro - ri
    v = fsolve(artik, [-3.2 / h ** 2, -0.45 / h ** 2, 2.14 * h], xtol=1e-12)
    res = max(abs(q) for q in artik(v))
    Y = ent(v[0], v[1], v[2], True)
    r = np.hypot(Y[:, 0], Y[:, 1])
    pol = np.degrees(np.arctan2(Y[:, 1], Y[:, 0]))
    gecerli = bool(res < 1e-7 and r.min() > ri - 1e-6 and r.max() < ro + 1e-6 and math.sin(Y[-1, 2] - math.radians(pol[-1])) < -0.99)
    return dict(R_min=float(1.0 / np.abs(Y[:, 3]).max()), l=float(v[2]), delta=float(pol[-1]), pol=pol, r=r, k=Y[:, 3],
                s=np.linspace(0.0, v[2], M + 1), F=[float(v[0]), float(v[1])], artik=float(res), gecerli=gecerli,
                pol_max=float(pol.max()), r_ri=ri, r_ro=ro)


def s1_olcu(KK):
    """arayuz KOL_KABLO -> S1 kaseti turetilmis olculeri: demet, ri, ro, kanal merkezi x, U cozumu."""
    S = KK["s1"]
    n, t = S["serit"], KK["serit"][1]
    k = n * t
    ri = S["tambur"]["r"][1] + k / 2.0
    ro = S["duvar"]["r"][0] - k / 2.0
    xc = 0.5 * (S["kanal_x"][0] + S["kanal_x"][1])
    return dict(n=n, kalinlik=k, ri=ri, ro=ro, xc=xc, U=u_lop(ri, ro))


def s1_poz(KK, phi, O=None, L=None, psi_w=None, bag_psi=None):
    """S1 acisi phi'de (derece) kablonun sabit cercevedeki yeri. Doner: psi_bag, psi_U (ic ayrilma), a_i, a_o (derece), nokta (omuz
    yereli V listesi: tambur bagi -> ic kosu -> U -> dis kosu -> duvar bagi), u_nokta (yalniz U)."""
    S = KK["s1"]
    O = O or s1_olcu(KK)
    U = O["U"]
    L = S["L"] if L is None else L
    psi_w = S["bag_duvar_psi"] if psi_w is None else psi_w
    psi_d = (S["tambur"]["bag_psi"] if bag_psi is None else bag_psi) + phi
    ri, ro, xc = O["ri"], O["ro"], O["xc"]
    d = math.radians(U["delta"])
    psU = (L - U["l"] + ri * math.radians(psi_d) + ro * (math.radians(psi_w) - d)) / (ri + ro)
    psi_U = math.degrees(psU)
    a_i, a_o = psi_U - psi_d, psi_U + U["delta"] - psi_w
    pts = []
    for ps in np.linspace(psi_d, psi_U, max(2, int(abs(a_i) / 2) + 2))[:-1]:
        y, z = psi_yz(ps, ri)
        pts.append(V(xc, y, z))
    upts = []
    for pl_, rr in zip(U["pol"][::4], U["r"][::4]):
        y, z = psi_yz(psi_U + pl_, rr)
        upts.append(V(xc, y, z))
    if (len(U["pol"]) - 1) % 4:
        y, z = psi_yz(psi_U + U["pol"][-1], U["r"][-1])
        upts.append(V(xc, y, z))
    pts += upts
    for ps in np.linspace(psi_U + U["delta"], psi_w, max(2, int(abs(a_o) / 2) + 2))[1:]:
        y, z = psi_yz(ps, ro)
        pts.append(V(xc, y, z))
    return dict(phi=phi, psi_bag=psi_d, psi_U=psi_U, a_i=a_i, a_o=a_o, nokta=pts, u_nokta=upts,
                u_uc_psi=psi_U + U["pol_max"])


def s1_gecis(KK, O=None):
    """G2 (S2 lopu sonu, gobek cercevesi) -> tambur bagi: psi boyunca r ve x icin kubik Hermite (G2 tegeti S2 lopundan, bagda tegeti
    +psi, x sabit). Gobek cercevesinde V listesi (omuz yereli, S1 = 0)."""
    S = KK["s1"]
    O = O or s1_olcu(KK)
    G = KK["s2_lop"]
    gx, gy, gz = G["F"]
    tg = V(*G["F_teget"])
    ps0, r0 = yz_psi(gy, gz)
    ps1, r1 = S["tambur"]["bag_psi"], O["ri"]
    x0, x1 = gx, O["xc"]
    a = math.radians(ps0)
    e_r = V(0, math.cos(a), -math.sin(a))
    e_p = V(0, -math.sin(a), -math.cos(a))
    drdp0 = r0 * tg.dot(e_r) / max(tg.dot(e_p), 1e-9)            # dr/dpsi (mm/rad) G2'de
    D = math.radians(ps1 - ps0)

    def herm(p0, p1, m0, m1, t):
        h00, h10, h01, h11 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t, -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1
    out = []
    for t in np.linspace(0.0, 1.0, S["gecis"]["n"] + 1):
        ps = ps0 + (ps1 - ps0) * t
        r = herm(r0, r1, drdp0 * D, 0.0, t)
        x = herm(x0, x1, 0.0, 0.0, t)
        y, z = psi_yz(ps, r)
        out.append(V(x, y, z))
    return out


def s1_cikis(KK, O=None):
    """Duvar bagi -> duvar boyunca -> psi_c'de radyal ice -> ped yarigi (-x) -> govde ici (omuz yereli) noktalari (sabit cerceve)."""
    S = KK["s1"]
    O = O or s1_olcu(KK)
    C = S["cikis"]
    xc, ro = O["xc"], O["ro"]
    pts = []
    for ps, rr in ((S["bag_duvar_psi"], ro), (C["psi"], ro - 0.5)):   # duvar boyunca tek kiris (kose yaricapi icin); kose duvardan 0,5 ice
        y, z = psi_yz(ps, rr)
        pts.append(V(xc, y, z))
    y, z = psi_yz(C["psi"], C["r_don"])
    pts.append(V(xc, y, z))
    pts.append(V(C["x_ic"], y, z))
    pts += [V(*p) for p in S["govde_ici"]]
    return pts
