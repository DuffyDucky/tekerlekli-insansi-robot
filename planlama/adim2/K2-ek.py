# K2 ek olcumler: (1) S1 ust sinirinda U cebi (kaset ust ucu) ile kablo arasi duzlem ici bosluk ve giris hacmi: S1 asimi ve kablo boyu
# (L) toleransi; dikme / pim bosluklari tum aralikta. (2) kaset <-> kol S2 3...5 (alt sinir alti). Yalniz okur. Cikti: K2-ek.json
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
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
ADIM = os.environ.get("K2_ADIM", "hepsi")
JS = "K2-ek-%s.json" % ADIM
OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
KASET = [(p["ad"], p["shape"]) for p in KAB if p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi")]
KG = dict(KASET)
KOL = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Kol"] + [(p["ad"], p["shape"]) for p in DIR if p["grup"] == "UstKol"]
S1 = A.KOL_KABLO["s1"]
T = A.KOL_KABLO["serit"][1]
KAL = S1["serit"] * T
GEN = A.KOL_KABLO["serit"][0]
RI = S1["tambur"]["r"][1] + KAL / 2
RO = S1["duvar"]["r"][0] - KAL / 2
XC = 0.5 * sum(S1["kanal_x"])
L0 = S1["L"]

# kaset dilim telleri (x sabit): duvar halkasi (buyuk) + dikme / pim (kucuk)
TEL = {}
for xk in (154.0, XC, 157.9):
    tl = []
    for a in ("S1 kaset govdesi sag", "S1 kaset kapagi sag"):
        s = KG[a]
        if s.BoundBox.XMin <= xk <= s.BoundBox.XMax:
            for w in s.slice(V(1, 0, 0), xk):
                c = w.BoundBox.Center
                tl.append((a, w, w.BoundBox.DiagonalLength, O.yz_psi(c.y, c.z)))
    TEL[xk] = tl
log("teller", {k: [(a, round(d, 1), [round(q, 1) for q in pr]) for a, w, d, pr in v] for k, v in TEL.items()})


def demet_kati(P2):
    P2 = np.asarray(P2)
    t = np.gradient(P2, axis=0)
    t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.stack([-t[:, 1], t[:, 0]], 1)
    pts = [V(XC - GEN / 2, q[0], -q[1]) for q in P2 + KAL / 2 * n] + [V(XC - GEN / 2, q[0], -q[1]) for q in (P2 - KAL / 2 * n)[::-1]]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(GEN, 0, 0))


def olc(phi, L=L0, **kw):
    c = U.coz(RI, RO, S1["tambur"]["bag_psi"] + phi, S1["bag_duvar_psi"], L, N=240, **kw)
    oz = U.ozet(c)
    P2 = c["P"]
    k = np.abs(c["k"])
    jm = int(np.argmax(k))
    pos = np.where(c["k"][:jm] >= 0)[0]
    i_inf = int(pos.max()) + 1 if len(pos) else 0
    dis = np.where(c["do"][jm + 1:] < 0.02)[0]
    i_dis = jm + 1 + int(dis.min()) if len(dis) else len(P2) - 1
    # U bolgesi: bukumden dis temasin 5 mm (yay) oncesine kadar
    n5 = int(5.0 / c["ds"])
    Ub = P2[i_inf:max(i_inf + 2, i_dis - n5)]
    sonuc = dict(phi=phi, L=L, R_min=round(oz["R_min"], 3), u_uc_psi=round(oz["u_uc_psi"], 2), psi_dis_temas=round(oz["psi_dis_temas"], 2))
    for xk, tl in TEL.items():
        ub = Part.makePolygon([V(xk, q[0], -q[1]) for q in Ub])
        tum = Part.makePolygon([V(xk, q[0], -q[1]) for q in P2])
        for a, w, dg, pr in tl:
            if dg > 60:          # duvar halkasi: yalniz U bolgesi (dis kosu tasarim geregi duvara yaslanir)
                d = w.distToShape(ub)[0] - KAL / 2
                key = "U_duvar"
            else:
                d = w.distToShape(tum)[0] - KAL / 2
                key = "kucuk_%s_%.0f" % ("pim" if pr[0] > 300 else "dikme", pr[0])
            if key not in sonuc or d < sonuc[key]:
                sonuc[key] = round(d, 3)
    kat = demet_kati(P2)
    sonuc["kaset_giris_mm3"] = round(sum(kat.common(s).Volume for a, s in KASET[:2]), 3)
    return sonuc


if ADIM in ("hepsi", "cep"):
    sat = []
    for phi in [-45, -30, 0, 30, 60, 90, 110, 120, 125, 130, 132, 133, 134, 135, 135.5, 136, 137, 138]:
        sat.append(olc(float(phi)))
        log(sat[-1], "%.0fs" % (time.time() - t0))
    OUT["cep_phi"] = sat
    O.kaydet(JS, OUT)
    sat = []
    for dL in (-10, -5, -2, -1, 0.5, 1, 2, 5, 10):
        for phi in (135.0, -45.0):
            sat.append(olc(phi, L=L0 + dL))
            log(sat[-1])
    OUT["cep_L"] = sat
    sat = []
    for a in (5, 10, 15):
        sat.append(dict(sapma_i=a, **olc(135.0, sapma_i=a)))
        log(sat[-1])
    OUT["cep_sapma"] = sat
    O.kaydet(JS, OUT)

if ADIM in ("hepsi", "kol"):
    sat = []
    for th in (3.0, 3.5, 4.0, 4.5, 5.0):
        best = (1e9, None, None, None)
        for phi in range(-45, 136, 5):
            inv = O.Pp(float(phi)).multiply(O.Pr(th)).inverse()
            ks = [(a, tasi(s, inv)) for a, s in KASET]
            d, a, b = O.enaz(ks, KOL, pay=5)
            if d < best[0]:
                best = (d, a, b, phi)
        sat.append((th, round(best[0], 3), best[1], best[2], best[3]))
        log("kaset-kol S2", sat[-1])
    OUT["kaset_kol_alt"] = sat
    O.kaydet(JS, OUT)
O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
