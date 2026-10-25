# K3 (Y1b kontrol): taslak-170'te S1 kaseti cevresi. Yalniz okur. Cikti: K3-taslak-<adim>.json
#   kiyas : taslak FCStd S1 cevresi parcalari (sag omuz yereline) <-> modul FCStd parcalari: Y1b geometrisi (pah, kulak, ip yolu, ip)
#           taslaga gecmis mi (hacim, merkez, ortak hacim orani); iki yan
#   ev    : kol zinciri S2 0 / 3 / 3,5 / 3,75 / 4 / 5 -> gobek + govde + kaset (iki yan)
#   kolkaset: kol zinciri (taslak: tup +30, dirsek DY-30, on kol / el x1,25) <-> kaset, S1 -45...135 (2,5) x S2 5...30 (0,5) + 35...120 (5)
#           (K3: S1 -45...135 / 5 x S2 5...20 / 1 + 25...120) x dirsek 0 / 52,5 / 105; nokta bulutu on tarama + en kucuk pozlarda kesin
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
ADIM = os.environ.get("K3_ADIM", "kiyas")
JS = "K3-taslak-%s.json" % ADIM
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
sys.path.insert(0, os.path.join(O.R, "taslak-170"))
import taslak_ayar as TA
DY = TA.DY
OY = V(*O.OY)
TS = O.ac("taslak-170/taslak-170.FCStd", "K3T")
OUT["taslak_parca"] = len(TS)
YAKIN = App.BoundBox(110, -130, -110, 290, 110, 110)


def yerel(s, sag=True):
    q = s.copy()
    if not sag:
        q = q.mirror(V(0, 0, 0), V(1, 0, 0))
    q.translate(V(-OY.x, -OY.y - DY, -OY.z))
    return q


TY = {}
for sag in (True, False):
    for p in TS:
        s = yerel(p["shape"], sag)
        if s.BoundBox.intersect(YAKIN) and s.BoundBox.XMin > 100:
            TY.setdefault("sag" if sag else "sol", []).append(dict(ad=p["ad"], grup=p["grup"], shape=s))
KOLGRUP = {"sag": ("OmuzSag_Kol", "DirsekSag_UstKol", "DirsekSag_OnKol", "DirsekSag_El"),
           "sol": ("OmuzSol_Kol", "DirsekSol_UstKol", "DirsekSol_OnKol", "DirsekSol_El")}
TKOL = {t: [dict(ad=p["ad"], grup=p["grup"], shape=yerel(p["shape"], t == "sag")) for p in TS if p["grup"] in KOLGRUP[t]] for t in ("sag", "sol")}
log("S1 cevresi", {k: len(v) for k, v in TY.items()}, "kol", {k: len(v) for k, v in TKOL.items()})


def kaset_t(taraf):
    return [(t["ad"], t["shape"]) for t in TY[taraf] if t["ad"].startswith("S1 kaset") or t["ad"].startswith("Kaset civatasi")]


if ADIM == "kiyas":
    OMU = O.ac("omuz/omuz-montaj.FCStd", "K3T")
    KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd", "K3T"))
    MOD = [dict(ad=p["ad"], grup="omuz/" + p["grup"], shape=p["shape"]) for p in OMU if p["tur"] != "Referans"] + \
          [dict(ad=p["ad"], grup="kabuk", shape=p["shape"]) for p in KAB]
    MOD = [m for m in MOD if m["shape"].BoundBox.intersect(YAKIN) and m["shape"].BoundBox.XMin > 100]
    out = {}
    for taraf in ("sag", "sol"):
        T = TY[taraf]
        sat = []
        for m in MOD:
            sm = m["shape"]
            if sm.Volume < 1e-6:
                continue
            en = None
            for t in T:
                st = t["shape"]
                if abs(st.Volume - sm.Volume) > max(0.05, 0.002 * sm.Volume):
                    continue
                if (st.BoundBox.Center - sm.BoundBox.Center).Length > 0.05:
                    continue
                c = sm.common(st).Volume / sm.Volume
                if en is None or c > en[1]:
                    en = (t["ad"], round(c, 5))
            sat.append(dict(modul_parca=m["ad"], grup=m["grup"], hacim=round(sm.Volume, 3), taslak=en))
        ayni = [q for q in sat if q["taslak"] and q["taslak"][1] > 0.9999]
        farkli = [q for q in sat if not (q["taslak"] and q["taslak"][1] > 0.9999)]
        y1b = [q for q in sat if q["modul_parca"].startswith(("S1 kaset", "S1 kablo tamburu", "S1 tambur baglama ipi"))]
        out[taraf] = dict(modul_parca=len(sat), ayni=len(ayni), farkli=[(q["modul_parca"], q["grup"], q["taslak"]) for q in farkli], y1b=y1b)
        log(taraf, len(sat), len(ayni), out[taraf]["farkli"], [(q["modul_parca"], q["taslak"]) for q in y1b])
    OUT["kiyas"] = out
    O.kaydet(JS, OUT)

if ADIM == "ev":
    ev = {}
    for taraf in ("sag", "sol"):
        T = TY[taraf]
        GOBt = [(t["ad"], t["shape"]) for t in T if t["grup"].endswith("_Gobek")]
        KOLt = [(t["ad"], t["shape"]) for t in TKOL[taraf]]
        SAB = kaset_t(taraf) + [(t["ad"], t["shape"]) for t in T if t["grup"].endswith("_Govde")]
        sat = []
        for th in (0.0, 3.0, 3.5, 3.75, 4.0, 5.0):
            kol = [(a, tasi(s, O.Pr(th))) for a, s in KOLt]
            cak, en = [], (1e9, None, None)
            for a, s in kol:
                bb = App.BoundBox(s.BoundBox)
                bb.enlarge(3)
                for b, q in GOBt + SAB:
                    if not bb.intersect(q.BoundBox):
                        continue
                    d = s.distToShape(q)[0]
                    if d < en[0] and not b.startswith("S2 servo"):
                        en = (round(d, 3), a, b)
                    if d < 1e-6:
                        v = s.common(q).Volume
                        if v > 1e-3:
                            cak.append((a, b, round(v, 2)))
            sat.append(dict(S2=th, cakisma=cak, en_kucuk_servo_haric=en))
            log(taraf, th, cak, en, "%.0fs" % (time.time() - t0))
        ev[taraf] = sat
    OUT["ev"] = ev
    O.kaydet(JS, OUT)

if ADIM == "kolkaset":
    D = A.DIRSEK
    ey, ez = D["eksen_y"] - TA.UST_KOL_UZAMA, D["eksen_z"]
    UST = [(t["ad"], t["shape"]) for t in TKOL["sag"] if t["grup"].endswith(("_Kol", "_UstKol"))]
    ALT = [(t["ad"], t["shape"]) for t in TKOL["sag"] if t["grup"].endswith(("_OnKol", "_El"))]
    KASt = kaset_t("sag")

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
            P.append(Q[ui])
            ad += [i] * len(Q[ui])
        return np.vstack(P), np.array(ad)

    def mat(pl):
        m = pl.toMatrix()
        return np.array([[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]]), np.array([m.A14, m.A24, m.A34])
    PH = [float(x) for x in np.arange(-45, 135.01, 5.0)]
    TH = [float(x) for x in np.arange(5.0, 20.01, 1.0)] + [25.0, 30.0, 45.0, 60.0, 75.0, 90.0, 105.0, 120.0]
    Pk, Ik = bulut(KASt, 0.6)
    res = {}
    for al in (0.0, 52.5, 105.0):
        Pe = App.Placement(V(0, 0, 0), App.Rotation(V(*D["eksen_yon"]), al), V(0, ey, ez))
        zincir = UST + [(a, tasi(s, Pe)) for a, s in ALT]
        Pz, Iz = bulut(zincir, 0.6, kutu=App.BoundBox(90, -110, -100, 290, 110, 100))
        tree = cKDTree(Pz)
        sat = []
        for p in PH:
            for t in TH:
                R, tt = mat(O.Pp(p).multiply(O.Pr(t)).inverse())
                d, j = tree.query(Pk @ R.T + tt, distance_upper_bound=25.0)
                i = int(np.argmin(d))
                sat.append(((p, t), float(d[i]), KASt[Ik[i]][0], zincir[Iz[j[i]]][0] if np.isfinite(d[i]) else None))
        sat.sort(key=lambda q: q[1])
        kes = []
        for (p, t), d, a, b in sat[:5]:
            inv = O.Pp(p).multiply(O.Pr(t)).inverse()
            dd, aa, bb = O.enaz([(x, tasi(s, inv)) for x, s in KASt], zincir, pay=3)
            kes.append(((p, t), round(d, 3), round(dd, 3), aa, bb))
        altmin = min([q for q in sat if q[3] in [a for a, _ in ALT]] or [((None, None), 1e9, None, None)], key=lambda q: q[1])
        res["dirsek %.1f" % al] = dict(kesin=kes, on_kol_el_en_az=(altmin[0], round(altmin[1], 3), altmin[2], altmin[3]), poz=len(sat))
        log("al", al, kes[:2], "on kol/el", res["dirsek %.1f" % al]["on_kol_el_en_az"], "%.0fs" % (time.time() - t0))
        OUT["kol_kaset"] = res
        O.kaydet(JS, OUT)

O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
