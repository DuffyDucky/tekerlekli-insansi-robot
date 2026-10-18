# K2 ek 2: S2 lopu <-> S1 kaseti (sabit) haritasi, S2 100...120 x S1 100...135. Iki olcu: demet cevrel zarfi (r 2,52; tasarimcinin
# yontemi) ve dikdortgen kesit (duzlem ici kalinlik 2,8, duzleme dik genislik 4,2) en yakin noktadaki yone gore. Yalniz okur.
import os, sys, math, time, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part
A, V, log, tasi = O.A, O.V, O.log, O.tasi
U = O.yukle("K2-u.py")
t0 = time.time()
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
KASET = [(p["ad"], p["shape"]) for p in KAB if p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi")]
KK = A.KOL_KABLO
SL = KK["s2_lop"]
T, W = KK["serit"][1], KK["serit"][0]
R_C = math.hypot(W, 2 * T) / 2
F, tF = V(*SL["F"]), V(*SL["F_teget"])
out = []
onceki, k = None, None
THS = [5.0, 6.0] + list(np.arange(9.0, 120.01, 3.0))
LOPS = {}
for th in THS:
    pl = O.Pr(float(th))
    M, tM = pl.multVec(V(*SL["M"])), pl.Rotation.multVec(V(*SL["M_teget"]))
    a0, a1 = math.atan2(tM.y, tM.x), math.atan2(tF.y, tF.x)
    if onceki is None:
        ph, E, h, k = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150)
    else:
        k = round(((onceki[-1] - onceki[0]) + a0 - a1) / (2 * math.pi))
        ph, E, h, k = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150, th0=onceki, k=k)
    onceki = ph
    LOPS[th] = (M, F, ph)
for th in [t for t in THS if t >= 99]:
    M, F_, ph = LOPS[th]
    N = len(ph)
    ds = SL["L"] / N
    uv = np.vstack([[M.x, M.y], np.array([M.x, M.y]) + ds * np.cumsum(np.stack([np.cos(ph), np.sin(ph)], 1), 0)])
    s = np.linspace(0, 1, len(uv))
    s0 = 1.0 - SL["gecis"] / SL["L"]
    tt = np.clip((s - s0) / (1 - s0), 0, 1)
    w = M.z + (F_.z - M.z) * tt * tt * (3 - 2 * tt)
    pts = [V(float(uv[i][0]), float(uv[i][1]), float(w[i])) for i in range(len(uv))]
    uz = np.cumsum([0] + [(b - a).Length for a, b in zip(pts[:-1], pts[1:])])
    keep = [i for i in range(len(pts)) if 4.0 <= uz[i] <= uz[-1] - 4.0]
    ken = Part.makePolygon([pts[i] for i in keep])
    for phi in range(100, 136, 5):
        kf = tasi(ken, O.Pp(float(phi)))
        best = (1e9, None, None)
        for a, sh in KASET:
            dd, pp, info = sh.distToShape(kf)
            if dd < best[0]:
                best = (dd, a, pp[0])
        d, a, (p_sh, p_k) = best
        # yerel cerceve (gobek cercevesinde): en yakin lop noktasi
        inv = O.Pp(float(phi)).inverse()
        pk = inv.multVec(p_k)
        ps = inv.multVec(p_sh)
        j = int(np.argmin([(pts[i] - pk).Length for i in keep]))
        i = keep[j]
        tg = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
        tg.normalize()
        ez = V(0, 0, 1)
        n = tg.cross(ez)
        n.normalize()
        u = ps - pk
        if u.Length > 1e-9:
            u.normalize()
        destek = abs(u.dot(n)) * T + abs(u.dot(ez)) * W / 2      # dikdortgen kesitin u yonundeki yari olcusu (2 serit: kalinlik 2,8)
        out.append(dict(yana=float(th), S1=phi, d=round(d, 3), cevrel=round(d - R_C, 3), dikdortgen=round(d - destek, 3), parca=a,
                        nokta_gobek=[round(pk.x, 2), round(pk.y, 2), round(pk.z, 2)]))
        log(out[-1])
import json
json.dump(dict(satir=out, r_cevrel=R_C), open(os.path.join(HERE, "K2-ek2.json"), "w", encoding="utf-8"), indent=1)
log("bitti %.0fs" % (time.time() - t0))
