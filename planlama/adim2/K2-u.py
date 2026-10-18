# K2 kontrolu: S1 kablo kasetinin U lopu icin BAGIMSIZ cozucu (tasarimcinin kablo_yolu.u_lop / s1_poz'unu kullanmaz).
# Model: butun kablo (tambur bagi -> ic kosu -> U -> dis kosu -> duvar bagi) tek ayrik elastika; N esit parca, uclar ve uc
# tegetleri bagda sabit, boy L sabit; engel: her dugum r_i <= |p - c_i| ve |p - c_o| <= r_o (demet merkez cizgisi). Bukulme
# enerjisi sum(dtheta^2) en az (scipy SLSQP, analitik turev). Temas bolgeleri ve U sekli cozumden kendiliginden cikar (temas
# topolojisi varsayilmaz). Yalniz numpy/scipy: FreeCAD python'u ya da scipy'li herhangi bir python ile calisir.
# Duzlem: u = y, v = -z (omuz yereli); psi = atan2(v, u) derece (+Y 0, arka 90, alt 180, on 270), arayuz.KOL_KABLO["s1"] ile ayni.
import math
import numpy as np
from scipy.optimize import minimize


def _e(t):
    return np.stack([np.cos(t), np.sin(t)], 1)


def coz(ri, ro, psi_d, psi_w, L, N=240, ci=(0.0, 0.0), co=(0.0, 0.0), sapma_i=0.0, sapma_o=0.0, th0=None, maxiter=3000):
    """psi_d: tambur bagi (sabit cerceve, derece), psi_w: duvar bagi. sapma_i: bagda kablonun tambur tegetinden disari acisi
    (derece, + = disari), sapma_o: duvar bagindan ice acisi. Doner dict."""
    ci, co = np.asarray(ci, float), np.asarray(co, float)
    ds = L / N
    pd, pw = math.radians(psi_d), math.radians(psi_w)
    p0 = ci + ri * np.array([math.cos(pd), math.sin(pd)])
    p1 = co + ro * np.array([math.cos(pw), math.sin(pw)])
    # tambur bagindan +psi yonunde cikar (merkez solda): disari sapma = saga donus = aci azalir.
    # duvar bagina -psi yonunde varir: icten gelme (disari dogru hareket) = sola donus = aci artar.
    # dal (U): toplam donus = (psi_w - 90) - (psi_d + 90) + sapmalar.
    a0 = pd + math.pi / 2 - math.radians(sapma_i)
    a1 = a0 + (pw - pd - math.pi) + math.radians(sapma_i) + math.radians(sapma_o)

    def tam(x):
        return np.concatenate([[a0], x, [a1]])

    def nodes(th):
        return np.vstack([p0, p0 + ds * np.cumsum(_e(th), 0)])

    def F(x, mu):
        """Ceza yontemi: enerji + mu * (engel ihlali^2 + uc hatasi^2). Turev: dugum gradyani -> ters kumulatif toplam."""
        th = tam(x)
        P = nodes(th)
        d = np.diff(th)
        E = float(d @ d)
        g_th = np.zeros(N)
        g_th[:-1] -= 2 * d
        g_th[1:] += 2 * d
        G = np.zeros_like(P)                                   # dF/dP_k
        Q = P[1:-1]
        for c, sgn, rr in ((ci, 1.0, ri), (co, -1.0, ro)):
            D = Q - c
            r = np.hypot(*D.T)
            v = sgn * (r - rr)                                 # >= 0 olmali
            m = v < 0
            E += mu * float((v[m] ** 2).sum())
            G[1:-1][m] += (mu * 2 * v[m] * sgn / r[m])[:, None] * D[m]
        eu = P[-1] - p1
        E += mu * float(eu @ eu)
        G[-1] += mu * 2 * eu
        # dP_k/dtheta_j = ds * e_perp(theta_j), k > j
        S = np.cumsum(G[::-1], 0)[::-1]                         # S[k] = sum_{m>=k} G[m]
        Sj = S[1:]                                             # parca j -> dugumler j+1..N
        g_th += ds * (-np.sin(th) * Sj[:, 0] + np.cos(th) * Sj[:, 1])
        return E, g_th[1:-1]

    def kis(x):
        P = nodes(tam(x))[1:-1]
        return np.concatenate([np.hypot(*(P - ci).T) - ri, ro - np.hypot(*(P - co).T)])

    if th0 is None:
        th0 = baslangic(ri, ro, psi_d, psi_w, L, N, a0, a1)
    x = np.asarray(th0, float)[1:-1].copy()
    nit = 0
    for mu in (1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9):
        r = minimize(F, x, args=(mu,), jac=True, method="L-BFGS-B", options=dict(maxiter=maxiter, maxcor=30, ftol=1e-16, gtol=1e-11))
        x = r.x
        nit += r.nit
    r.x = x
    r.nit = nit
    r.fun = F(x, 0.0)[0]
    th = tam(r.x)
    P = nodes(th)
    dth = np.diff(th)
    kap = np.abs(dth).max()
    hata = float(np.abs(P[-1] - p1).max())
    ihlal = float(min(0.0, kis(r.x).min()))
    rr = np.hypot(*P.T)
    psi = np.degrees(np.arctan2(P[:, 1], P[:, 0])) % 360.0
    # temas bolgeleri: ic (r - ri < tol) ve dis
    tol = 0.02
    di = np.hypot(*(P - ci).T) - ri
    do = ro - np.hypot(*(P - co).T)
    ic_tem = np.where(di < tol)[0]
    dis_tem = np.where(do < tol)[0]
    # U: ic temasin son dugumu ile dis temasin ilk dugumu arasi (s sirasiyla)
    serbest = np.where((di >= tol) & (do >= tol))[0]
    k_ = dth / ds                                                   # egrilik (parca arasi)
    return dict(th=th, P=P, R_min=ds / kap if kap > 0 else 1e9, k=k_, s=np.arange(N + 1) * ds, hata=hata, ihlal=ihlal,
                ok=bool(hata < 5e-3 and ihlal > -5e-3), mesaj=str(r.message), nit=int(r.nit), E=float(r.fun),
                r=rr, psi=psi, serbest=serbest, ic_tem=ic_tem, dis_tem=dis_tem, ds=ds, a0=a0, a1=a1, di=di, do=do)


def baslangic(ri, ro, psi_d, psi_w, L, N, a0, a1):
    """Tasarimcidan bagimsiz kaba baslangic: ic yay + yarim daire (cap = h) + dis yay; boy L'ye gore U acisi."""
    h = ro - ri
    pd, pw = math.radians(psi_d), math.radians(psi_w)
    pU = (L - math.pi * h / 2 + ri * pd + ro * pw) / (ri + ro)
    pts = []
    for t in np.linspace(pd, pU, 200):
        pts.append((ri * math.cos(t), ri * math.sin(t)))
    rm = (ri + ro) / 2
    c = np.array([rm * math.cos(pU), rm * math.sin(pU)])
    er = np.array([math.cos(pU), math.sin(pU)])
    et = np.array([-math.sin(pU), math.cos(pU)])
    for t in np.linspace(math.pi, 0.0, 200)[1:]:
        q = c + (h / 2) * (math.cos(t) * er + math.sin(t) * et)
        pts.append(tuple(q))
    for t in np.linspace(pU, pw, 200)[1:]:
        pts.append((ro * math.cos(t), ro * math.sin(t)))
    pts = np.array(pts)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    sq = np.linspace(0, s[-1], N + 1)
    q = np.stack([np.interp(sq, s, pts[:, 0]), np.interp(sq, s, pts[:, 1])], 1)
    th = np.unwrap(np.arctan2(*np.diff(q, axis=0).T[::-1]))
    th = th - th[0] + a0
    th = th + np.linspace(0, 1, N) * ((a1 - th[-1]))
    return th


def ozet(c):
    """Topolojiden bagimsiz U olculeri. U = egriligin en buyuk oldugu yerin cevresi: ic sinir = egriligin isaret degistirdigi
    (bukum) son nokta, dis sinir = duvara ilk temas. Kosu acisi: bag ile U siniri arasi yay (derece). Ic kosunun tamburdan
    kalkmasi (en buyuk di) ve U ucu (en buyuk psi) de raporlanir."""
    k, P = c["k"], c["P"]
    pu = np.degrees(np.unwrap(np.radians(c["psi"])))
    jm = int(np.argmax(np.abs(k)))
    pos = np.where(k[:jm] >= 0)[0]
    i_inf = int(pos.max()) + 1 if len(pos) else 0
    dis = np.where(c["do"][jm + 1:] < 0.02)[0]
    i_dis = jm + 1 + int(dis.min()) if len(dis) else len(P) - 1
    return dict(R_min=float(c["R_min"]), R_yer_r=float(c["r"][jm + 1]), R_yer_psi=float(c["psi"][jm + 1]),
                psi_bukum=float(pu[i_inf]) % 360, psi_dis_temas=float(pu[i_dis]) % 360,
                a_ic=float(pu[i_inf] - pu[0]), a_dis=float(pu[i_dis] - pu[-1]),
                u_uc_psi=float(pu[i_inf:i_dis + 1].max()) % 360, u_uc_ileri=float(pu[i_inf:i_dis + 1].max() - pu[i_inf]),
                ic_kalkma=float(c["di"][:i_inf + 1].max()) if i_inf > 0 else 0.0,
                r_min=float(c["r"].min()), r_max=float(c["r"].max()), hata=c["hata"], ihlal=c["ihlal"])


if __name__ == "__main__":
    import sys, time
    t = time.time()
    ri, ro = 41.1, 73.1
    for phi in (-45, 45, 135):
        c = coz(ri, ro, 145.0 + phi, 228.3, 171.4, N=int(sys.argv[1]) if len(sys.argv) > 1 else 240)
        o = ozet(c)
        print(phi, "R_min %.3f hata %.1e ihlal %.1e nit %d ok %s %s" % (c["R_min"], c["hata"], c["ihlal"], c["nit"], c["ok"], c["mesaj"]),
              {k: round(v, 2) for k, v in o.items()}, "%.1fs" % (time.time() - t))


# ---------------------------------------------------------------------------------------------- engelsiz serbest lop (dirsek / S2)
def serbest(p0, a0, p1, a1, L, N=150, th0=None, k=None, bombe=(-2.5, -1.2, 0.0, 1.2, 2.5), maxiter=4000):
    """Iki ucu ankastre (konum + teget) sabit boylu ayrik elastika, engelsiz. Ceza yontemi + L-BFGS (tasarimcinin Gauss-Newton
    cozucusunden ve onceki K'nin SLSQP'sinden farkli). th0 verilirse sureklilik (k = toplam donus dali). Doner (th, E, hata, k)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    ds = L / N

    def bir(kk, x0):
        b = a1 + 2 * math.pi * kk

        def F(x, mu):
            th = np.concatenate([[a0], x, [b]])
            d = np.diff(th)
            E = float(d @ d)
            g = np.zeros(N)
            g[:-1] -= 2 * d
            g[1:] += 2 * d
            eu = p0 + ds * np.array([np.cos(th).sum(), np.sin(th).sum()]) - p1
            E += mu * float(eu @ eu)
            g += mu * 2 * ds * (-np.sin(th) * eu[0] + np.cos(th) * eu[1])
            return E, g[1:-1]
        x = x0.copy()
        for mu in (1e0, 1e2, 1e4, 1e6, 1e8, 1e10):
            r = minimize(F, x, args=(mu,), jac=True, method="L-BFGS-B", options=dict(maxiter=maxiter, maxcor=30, ftol=1e-16, gtol=1e-12))
            x = r.x
        th = np.concatenate([[a0], x, [b]])
        d = np.diff(th)
        hata = float(np.hypot(*(p0 + ds * np.array([np.cos(th).sum(), np.sin(th).sum()]) - p1)))
        return th, float(d @ d), hata
    s = np.linspace(0, 1, N)
    if th0 is not None:
        b = a1 + 2 * math.pi * k
        x0 = (np.asarray(th0) + (a0 - th0[0]) * (1 - s) + (b - th0[-1]) * s)[1:-1]
        th, E, h = bir(k, x0)
        return th, E, h, k
    best = None
    for kk in (-1, 0, 1):
        b = a1 + 2 * math.pi * kk
        for bm in bombe:
            x0 = (a0 + (b - a0) * s + bm * np.sin(math.pi * s))[1:-1]
            th, E, h = bir(kk, x0)
            if h < 1e-3 and (best is None or E < best[1]):
                best = (th, E, h, kk)
    return best
