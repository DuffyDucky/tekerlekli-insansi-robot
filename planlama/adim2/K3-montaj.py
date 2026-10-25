# K3 (Y1b kontrol) K5: kaset govdesi / kapagi ONDEN RADYAL montaj yolu (yeni geometri: kulak, pah, ip delikleri). Yalniz okur.
# Nokta bulutu (<= 0,4 mm) + cKDTree: hareketli parca (govde / kapak) yol boyunca kaydirilir, hedef: kabuk sag (kaset haric; kapak icin
# govde dahil) + gobek (Pp) + kol (Pp Pr). En kucuk mesafe < 0,05 olan adimlarda kesin common hacmi. Yon: parcanin psi ortalamasi
# (sektor ortaortayi) +-15 derece. Cikti: K3-montaj.json
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
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
OMU = O.ac("omuz/omuz-montaj.FCStd", "K3M")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd", "K3M"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd", "K3M")
GOB = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Gobek"]
KOL = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Kol"] + [(p["ad"], p["shape"]) for p in DIR if p["grup"] == "UstKol"]
KG = {p["ad"]: p["shape"] for p in KAB}
GOVDE, KAPAK = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
KAB_D = [(p["ad"], p["shape"]) for p in KAB if not p["ad"].startswith("S1 kaset") and not p["ad"].startswith("Kaset civatasi")]
BOLGE = App.BoundBox(130, -190, -190, 175, 190, 190)
KAB_D = [(a, s) for a, s in KAB_D if s.BoundBox.intersect(BOLGE)]
log("kabuk aday", len(KAB_D), [a for a, _ in KAB_D])


def bulut(lst, ml=0.4, kutu=None):
    P, ad = [], []
    for i, (a, s) in enumerate(lst):
        if kutu is not None and not s.BoundBox.intersect(kutu):
            continue
        pts, tri = s.tessellate(0.03)
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
        P.append(Q[ui])
        ad += [i] * len(ui)
    return np.vstack(P), np.array(ad)


def mat(pl):
    m = pl.toMatrix()
    return np.array([[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]]), np.array([m.A14, m.A24, m.A34])


def psi_ort(sh):
    ps = np.radians([O.yz_psi(v.Y, v.Z)[0] for v in sh.Vertexes])
    return math.degrees(math.atan2(np.sin(ps).mean(), np.cos(ps).mean())) % 360


# sabit hedef bulutu (kabuk) bir kez; hareketli hedefler (gobek, kol) poz basina
PK, IK = bulut(KAB_D, 0.4, kutu=BOLGE)
log("kabuk bulutu", len(PK), "%.0fs" % (time.time() - t0))
PG, IG = bulut(GOB, 0.4)
PL, IL = bulut(KOL, 0.4, kutu=App.BoundBox(120, -200, -150, 300, 150, 150))
PGV, IGV = bulut([("govde", GOVDE)], 0.4)
log("gobek / kol bulutu", len(PG), len(PL), "%.0fs" % (time.time() - t0))
S = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 70.0, 90.0]
rad = []
for ad_, sh, x_of, govde_hedef in (("govde", GOVDE, 0.0, False), ("kapak", KAPAK, 3.3, True), ("kapak", KAPAK, 3.5, True)):
    PH, IH = bulut([(ad_, sh)], 0.4)
    pm = psi_ort(sh)
    for phi, th in ((-45.0, 90.0), (-20.0, 90.0), (0.0, 90.0), (-45.0, 5.0), (0.0, 30.0), (45.0, 90.0)):
        Rg, tg = mat(O.Pp(phi))
        Rl, tl = mat(O.Pp(phi).multiply(O.Pr(th)))
        hed = [PK, PG @ Rg.T + tg, PL @ Rl.T + tl] + ([PGV] if govde_hedef else [])
        etk = [("kabuk", IK, KAB_D), ("gobek", IG, GOB), ("kol", IL, KOL)] + ([("govde", IGV, [("govde", GOVDE)])] if govde_hedef else [])
        lab = np.concatenate([np.full(len(h), i) for i, h in enumerate(hed)])
        idx = np.concatenate([e[1] for e in etk])
        tree = cKDTree(np.vstack(hed))
        for dps in (0.0, -15.0, 15.0):
            dy, dz = O.psi_yz(pm + dps, 1.0)
            yol = []
            for s in S:
                off = np.array([x_of, dy * s, dz * s])
                d, j = tree.query(PH + off, distance_upper_bound=10.0)
                i = int(np.argmin(d))
                if np.isfinite(d[i]):
                    g = etk[lab[j[i]]]
                    kim = "%s:%s" % (g[0], g[2][idx[j[i]]][0])
                else:
                    kim = None
                vol = []
                if d[i] < 0.05:                     # kesin: tasinan parca x hedef parca common
                    q = sh.copy()
                    q.translate(V(*off))
                    tg_list = KAB_D + [(a, tasi(s_, O.Pp(phi))) for a, s_ in GOB] + [(a, tasi(s_, O.Pp(phi).multiply(O.Pr(th)))) for a, s_ in KOL] + \
                        ([("govde", GOVDE)] if govde_hedef else [])
                    for a, s_ in tg_list:
                        if q.BoundBox.intersect(s_.BoundBox):
                            v = q.common(s_).Volume
                            if v > 1e-3:
                                vol.append((a, round(v, 3)))
                yol.append((s, round(float(d[i]), 3), kim, vol))
            rad.append(dict(parca=ad_, x_ofset=x_of, yon_psi=round(pm + dps, 1), S1=phi, S2=th, cakisan=[q for q in yol if q[3]],
                            en_kucuk=min((q[1], q[0], q[2]) for q in yol)))
            log(ad_, x_of, round(pm + dps, 1), phi, th, "en kucuk", rad[-1]["en_kucuk"], "cakisan", [(q[0], q[3]) for q in yol if q[3]][:3],
                "%.0fs" % (time.time() - t0))
        OUT["radyal"] = rad
        O.kaydet("K3-montaj.json", OUT)
# kapak son eksenel adim (3,5 -> 0) radyal konumda, kesin
son = []
for phi, th in ((-45.0, 90.0), (-20.0, 90.0), (0.0, 90.0), (0.0, 30.0)):
    hed = [("govde", GOVDE)] + [(a, tasi(s, O.Pp(phi))) for a, s in GOB] + [(a, tasi(s, O.Pp(phi).multiply(O.Pr(th)))) for a, s in KOL] + KAB_D
    for t in (3.5, 3.0, 2.0, 1.0, 0.5, 0.0):
        q = KAPAK.copy()
        q.translate(V(t, 0, 0))
        vol = []
        for a, s in hed:
            if q.BoundBox.intersect(s.BoundBox):
                v = q.common(s).Volume
                if v > 1e-3:
                    vol.append((a, round(v, 3)))
        son.append((phi, th, t, vol))
OUT["kapak_eksenel_son"] = son
log("eksenel son", [q for q in son if q[3]])
OUT["ozet"] = {"%s x%.1f" % (k[0], k[1]): dict(cakisan_poz=[(q["S1"], q["S2"], q["yon_psi"]) for q in rad if (q["parca"], q["x_ofset"]) == k and q["cakisan"]],
                                              temiz_poz=[(q["S1"], q["S2"], q["yon_psi"]) for q in rad if (q["parca"], q["x_ofset"]) == k and not q["cakisan"]])
               for k in (("govde", 0.0), ("kapak", 3.3), ("kapak", 3.5))}
O.kaydet("K3-montaj.json", OUT)
log(json.dumps(OUT["ozet"]))
log("bitti %.0fs" % (time.time() - t0))
