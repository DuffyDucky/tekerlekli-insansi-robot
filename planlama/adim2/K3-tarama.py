# K3 (Y1b kontrol): 125 cm modullerde S1 kaseti cevresi tam poz taramasi (nokta bulutu + cKDTree on tarama, en kucuk pozlarda kesin
# distToShape + common). K2-tarama yontemi; yeni geometri (pah, U cebi 6,5, ip delikleri, pim2 kulagi, tambur ip yolu + ip). Yalniz okur.
#   kaset : kaset (govde, kapak, civatalar) <-> kol zinciri (omuz Kol + dirsek UstKol + OnKol + El, dirsek 0 / 52,5 / 105)
#           S1 -45...135 (2,5) x S2 5...30 (0,5) + 35...120 (5)
#   tambur: tambur + ip <-> sabit (omuz govde, kabuk sag tumu), S1 -60...180 (1); tambur + ip <-> kol, S2 0...120
#   gobek : gobek (tambur haric, ip dahil) <-> kaset + kabuk sag, S1 -60...180 (1)
# Cikti: K3-tarama-<adim>.json
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part
from scipy.spatial import cKDTree

A, V, log, tasi = O.A, O.V, O.log, O.tasi
t0 = time.time()
ADIM = os.environ.get("K3_ADIM", "kaset")
JS = "K3-tarama-%s.json" % ADIM
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"), yontem="nokta bulutu (<= 0,6 mm) + cKDTree; en kucuk pozlarda kesin distToShape + common")
OMU = O.ac("omuz/omuz-montaj.FCStd", "K3T")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd", "K3T"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd", "K3T")


def sec(P, f):
    return [(p["ad"], p["shape"]) for p in P if f(p)]


GOV = sec(OMU, lambda p: p["grup"] == "Govde" and p["tur"] != "Referans")
GOB = sec(OMU, lambda p: p["grup"] == "Gobek")
TAMBUR = [(a, s) for a, s in GOB if a == "S1 kablo tamburu" or a.startswith("S1 tambur baglama ipi")]
GOB_D = [(a, s) for a, s in GOB if a != "S1 kablo tamburu"]
KOL = sec(OMU, lambda p: p["grup"] == "Kol") + sec(DIR, lambda p: p["grup"] == "UstKol")
ALT = sec(DIR, lambda p: p["grup"] in ("OnKol", "El"))
KASET = sec(KAB, lambda p: p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi"))
KAB_D = sec(KAB, lambda p: not (p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi")))
log("parca", len(GOV), len(GOB), len(KOL), len(ALT), len(KASET), len(KAB_D))
D = A.DIRSEK


def bulut(lst, ml=0.6, kutu=None):
    P, ad = [], []
    for i, (a, s) in enumerate(lst):
        if kutu is not None and not s.BoundBox.intersect(kutu):
            continue
        pts, tri = s.tessellate(0.05)
        X = np.array([[p.x, p.y, p.z] for p in pts])
        Tr = np.array(tri, dtype=int)
        if len(Tr) == 0:
            continue
        A0, B0, C0 = X[Tr[:, 0]], X[Tr[:, 1]], X[Tr[:, 2]]
        Lm = np.max(np.stack([np.linalg.norm(B0 - A0, axis=1), np.linalg.norm(C0 - B0, axis=1), np.linalg.norm(A0 - C0, axis=1)]), 0)
        nn = np.maximum(1, np.ceil(Lm / ml)).astype(int)
        q = [X]
        for n in np.unique(nn):
            m = nn == n
            ij = np.array([(u, v) for u in range(n + 1) for v in range(n + 1 - u)], float) / n
            q.append((A0[m][:, None, :] + (B0[m] - A0[m])[:, None, :] * ij[None, :, 0:1] + (C0[m] - A0[m])[:, None, :] * ij[None, :, 1:2]).reshape(-1, 3))
        Q = np.vstack(q)
        if kutu is not None:
            k = ((Q[:, 0] >= kutu.XMin) & (Q[:, 0] <= kutu.XMax) & (Q[:, 1] >= kutu.YMin) & (Q[:, 1] <= kutu.YMax) &
                 (Q[:, 2] >= kutu.ZMin) & (Q[:, 2] <= kutu.ZMax))
            Q = Q[k]
        if len(Q) == 0:
            continue
        _, ui = np.unique(np.floor(Q / (0.5 * ml)).astype(np.int64), axis=0, return_index=True)
        Q = Q[ui]
        P.append(Q)
        ad += [i] * len(Q)
    log("bulut", len(ad), "nokta", "%.0fs" % (time.time() - t0))
    return np.vstack(P), np.array(ad)


def mat(pl):
    m = pl.toMatrix()
    R = np.array([[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]])
    t = np.array([m.A14, m.A24, m.A34])
    return R, t


def kesin(hs, sabit):
    dd, aa, bb = O.enaz(hs, sabit, pay=3)
    h = []
    if dd < 1e-6:
        for x, s in hs:
            for y, q in sabit:
                if s.BoundBox.intersect(q.BoundBox):
                    v = s.common(q).Volume
                    if v > 1e-4:
                        h.append((x, y, round(v, 4)))
    return round(dd, 3), aa, bb, h


def ad(lst):
    return [a for a, _ in lst]


if ADIM == "kaset":
    PH = [float(x) for x in np.arange(-45, 135.01, 2.5)]
    TH = [float(x) for x in np.arange(5.0, 30.01, 0.5)] + [float(x) for x in np.arange(35, 120.01, 5)]
    Pk, Ik = bulut(KASET, 0.6)
    res = {}
    for al in (D["aralik"][0] if "aralik" in D else 0.0, 52.5, 105.0):
        Pe = App.Placement(V(0, 0, 0), App.Rotation(V(*D["eksen_yon"]), al), V(0, D["eksen_y"], D["eksen_z"]))
        zincir = KOL + [(a, tasi(s, Pe)) for a, s in ALT]
        Pz, Iz = bulut(zincir, 0.6, kutu=App.BoundBox(90, -110, -100, 290, 110, 100))
        tree = cKDTree(Pz)
        sat = []
        for p in PH:
            for t in TH:
                R, tt = mat(O.Pp(p).multiply(O.Pr(t)).inverse())
                d, j = tree.query(Pk @ R.T + tt, distance_upper_bound=25.0)
                i = int(np.argmin(d))
                sat.append(((p, t), float(d[i]), ad(KASET)[Ik[i]], ad(zincir)[Iz[j[i]]] if np.isfinite(d[i]) else None))
        sat.sort(key=lambda q: q[1])
        kes = []
        for (p, t), d, a, b in sat[:6]:
            inv = O.Pp(p).multiply(O.Pr(t)).inverse()
            kes.append(((p, t), round(d, 3)) + kesin([(x, tasi(s, inv)) for x, s in KASET], zincir))
        by_t = {}
        for (p, t), d, a, b in sat:
            if t not in by_t or d < by_t[t][0]:
                by_t[t] = (round(d, 3), p, a, b)
        alt = [q for q in sat if q[0][1] >= 5.0]
        res["dirsek %.1f" % al] = dict(kesin=kes, en_kucuk_10=[(q[0], round(q[1], 3), q[2], q[3]) for q in sat[:10]],
                                       S2_basina=sorted([(t,) + v for t, v in by_t.items()]), poz=len(sat),
                                       alt_kol_el_en_az=min([q for q in sat if q[3] and any(q[3] == x for x, _ in ALT)] or [(None, 1e9, None, None)],
                                                            key=lambda q: q[1])[:4])
        log("dirsek", al, kes[:3], "%.0fs" % (time.time() - t0))
        OUT["kaset_kol"] = res
        O.kaydet(JS, OUT)
    # S2 alt sinir alti bilgi (3...4,75)
    tree = cKDTree(bulut(KOL, 0.6, kutu=App.BoundBox(90, -110, -100, 290, 110, 100))[0])
    alt = []
    for t in (3.0, 3.5, 4.0, 4.5, 4.75):
        best = (1e9, None)
        for p in PH:
            R, tt = mat(O.Pp(p).multiply(O.Pr(t)).inverse())
            d, j = tree.query(Pk @ R.T + tt, distance_upper_bound=25.0)
            if d.min() < best[0]:
                best = (float(d.min()), p)
        alt.append((t, round(best[0], 3), best[1]))
    OUT["kaset_kol_alt_bilgi"] = alt
    log("alt", alt)
    O.kaydet(JS, OUT)

if ADIM == "tambur":
    SAB = GOV + KAB_D + KASET
    pz = [float(p) for p in np.arange(-60, 180.01, 1.0)]
    KT = App.BoundBox(140, -60, -60, 175, 60, 60)
    Ps, Is = bulut(SAB, 0.4, kutu=KT)
    tree = cKDTree(Ps)
    Ph, Ih = bulut(TAMBUR, 0.3)
    sat = []
    for p in pz:
        R, t = mat(O.Pp(p))
        d, j = tree.query(Ph @ R.T + t, distance_upper_bound=20.0)
        i = int(np.argmin(d))
        sat.append((p, float(d[i]), ad(TAMBUR)[Ih[i]], ad(SAB)[Is[j[i]]] if np.isfinite(d[i]) else None))
    ic = sorted([q for q in sat if -45 <= q[0] <= 135], key=lambda q: q[1])
    kes = []
    for p, d, a, b in sorted(sat, key=lambda q: q[1])[:6] + ic[:3]:
        kes.append((p, round(d, 3)) + kesin([(x, tasi(s, O.Pp(p))) for x, s in TAMBUR], SAB))
    # parca basina en kucuk (on tarama)
    by = {}
    for p, d, a, b in sat:
        k_ = (a, b)
        if k_ not in by or d < by[k_][0]:
            by[k_] = (round(d, 3), p)
    OUT["tambur_ip_sabit"] = dict(kesin=kes, cift_basina=sorted(((k[0], k[1]) + v for k, v in by.items()), key=lambda q: q[2])[:15])
    log("tambur-sabit", kes[:4])
    O.kaydet(JS, OUT)
    pz2 = [0.0, 3.0, 3.5, 3.75, 4.0, 4.5, 5.0, 6.0, 8.0, 10.0] + [float(x) for x in np.arange(12.5, 120.01, 2.5)]
    Pt, It = bulut(TAMBUR, 0.3)
    tree = cKDTree(Pt)
    Pk, Ik = bulut(KOL, 0.4, kutu=App.BoundBox(125, -60, -50, 245, 60, 50))
    tk = []
    for th in pz2:
        R, t = mat(O.Pr(th))
        d, j = tree.query(Pk @ R.T + t, distance_upper_bound=40.0)
        i = int(np.argmin(d))
        tk.append((th, round(float(d[i]), 3), ad(KOL)[Ik[i]], ad(TAMBUR)[It[j[i]]] if np.isfinite(d[i]) else None))
    for th in (3.5, 3.75, 4.0, 5.0):
        tk.append(("kesin", th) + kesin([(x, tasi(s, O.Pr(th))) for x, s in KOL], TAMBUR))
    OUT["tambur_ip_kol"] = tk
    log("tambur-kol", tk[-4:])
    O.kaydet(JS, OUT)

if ADIM == "gobek":
    SAB = KASET + KAB_D
    pz = [float(p) for p in np.arange(-60, 180.01, 1.0)]
    Ps, Is = bulut(SAB, 0.6, kutu=App.BoundBox(140, -110, -110, 200, 110, 110))
    tree = cKDTree(Ps)
    Ph, Ih = bulut(GOB_D, 0.6)
    sat = []
    for p in pz:
        R, t = mat(O.Pp(p))
        d, j = tree.query(Ph @ R.T + t, distance_upper_bound=20.0)
        i = int(np.argmin(d))
        sat.append((p, float(d[i]), ad(GOB_D)[Ih[i]], ad(SAB)[Is[j[i]]] if np.isfinite(d[i]) else None))
    ic = sorted([q for q in sat if -45 <= q[0] <= 135], key=lambda q: q[1])
    kes = [(p, round(d, 3)) + kesin([(x, tasi(s, O.Pp(p))) for x, s in GOB_D], SAB) for p, d, a, b in ic[:5]]
    OUT["gobek_kaset_kabuk"] = dict(kesin=kes, en_kucuk_10=[(q[0], round(q[1], 3), q[2], q[3]) for q in ic[:10]])
    log("gobek", kes)
    O.kaydet(JS, OUT)

O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
