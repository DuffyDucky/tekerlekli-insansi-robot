# K2: kaset ust ucu yuk degerlendirmesi + duvar bagi (kablo bagi) yeri. Yalniz okur. Cikti: K2-yuk.json
#  - arka plakanin kabuk bandina dayanan alani, desteksiz (bandin ustunde kalan) kismin uzunlugu
#  - psi = sabit radyal kesitlerde kaset (govde, govde + kapak) kesit alani ve x yonu egilme atalet momenti
#  - duvar bagi psi 228,3 cevresinde duvarda kablo bagi icin yarik / delik var mi (isin taramasi)
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part
A, V, log, tasi = O.A, O.V, O.log, O.tasi
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
KG = {p["ad"]: p["shape"] for p in KAB}
gv, kp = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
bant = KG["Omuz bandi sag"]
OUT = {}
# 1) arka yuz (x 152) <-> bant temas alani ve psi kapsami
arka = [f for f in gv.Faces if "Plane" in f.Surface.TypeId and abs(f.CenterOfMass.x - 152.0) < 0.01]
fa = Part.makeCompound(arka)
ort = Part.makeCompound([f.extrude(V(-0.2, 0, 0)) for f in arka]).common(bant)
OUT["arka_yuz_alan"] = round(sum(f.Area for f in arka), 1)
OUT["banta_dayanan_alan"] = round(ort.Volume / 0.2, 1)
# dayanan bolgenin psi kapsami (r 60'ta)
dayan = []
for ps in np.arange(185, 340, 1.0):
    y, z = O.psi_yz(ps, 60.0)
    p = V(151.9, y, z)
    dayan.append((float(ps), bool(bant.isInside(p, 1e-3, True)), bool(gv.isInside(V(152.5, y, z), 1e-3, True))))
ds = [q[0] for q in dayan if q[1] and q[2]]
OUT["r60_dayanan_psi"] = [min(ds), max(ds)] if ds else None
OUT["r60_kaset_psi"] = [min(q[0] for q in dayan if q[2]), max(q[0] for q in dayan if q[2])]
# r 75'te de
d75 = []
for ps in np.arange(185, 340, 1.0):
    y, z = O.psi_yz(ps, 76.0)
    d75.append((float(ps), bool(bant.isInside(V(151.9, y, z), 1e-3, True)), bool(gv.isInside(V(152.5, y, z), 1e-3, True))))
OUT["r76_dayanan_psi"] = [q[0] for q in d75 if q[1] and q[2]][:1] + [q[0] for q in d75 if q[1] and q[2]][-1:]
OUT["r76_kaset_psi"] = [min(q[0] for q in d75 if q[2]), max(q[0] for q in d75 if q[2])]


# 2) radyal kesitler: duzlem x ekseni + e_r(psi) icerir, normali e_psi
def kesit(sh, ps):
    a = math.radians(ps)
    n = V(0, -math.sin(a), -math.cos(a))           # e_psi (psi artan yon) omuz yerelinde
    ws = sh.slice(n, 0.0)
    fs = []
    er = V(0, math.cos(a), -math.sin(a))
    for w in ws:
        try:
            f = Part.Face(w)
            if f.Area > 1e-3 and f.CenterOfMass.dot(er) > 0:
                fs.append(f)
        except Exception:
            pass
    if not fs:
        return None
    A_ = sum(f.Area for f in fs)
    xc = sum(f.CenterOfMass.x * f.Area for f in fs) / A_
    # I_x (x yonu egilme): integral (x - xc)^2 dA, ucgenlemeyle
    I = 0.0
    for f in fs:
        pts, tri = f.tessellate(0.01)
        for (i, j, k) in tri:
            p0, p1, p2 = pts[i], pts[j], pts[k]
            ar = (p1 - p0).cross(p2 - p0).Length / 2
            xs = [p0.x - xc, p1.x - xc, p2.x - xc]
            I += ar / 6.0 * (xs[0] ** 2 + xs[1] ** 2 + xs[2] ** 2 + xs[0] * xs[1] + xs[1] * xs[2] + xs[0] * xs[2])
    c = max(max(v.Point.x for f in fs for v in f.Vertexes) - xc, xc - min(v.Point.x for f in fs for v in f.Vertexes))
    return dict(alan=round(A_, 2), xc=round(xc, 3), I_x=round(I, 2), c=round(c, 3), W=round(I / c, 2), parca_sayisi=len(fs))


kes = []
for ps in (240, 260, 280, 300, 310, 320):
    kes.append(dict(psi=ps, govde=kesit(gv, ps), govde_kapak=kesit(gv.fuse(kp), ps)))
    log(kes[-1])
OUT["kesit"] = kes
# 3) duvar bagi: psi 220...236 araliginda duvarda (r 74...78) delik / yarik var mi (x 154...158 isinlari)
bos = []
for ps in np.arange(220, 236.01, 0.5):
    for xk in (154.0, 155.9, 157.9):
        y0, z0 = O.psi_yz(ps, 74.5)
        y1, z1 = O.psi_yz(ps, 78.5)
        ray = Part.makeLine(V(xk, y0, z0), V(xk, y1, z1))
        L = gv.common(ray).Length
        if L < 1.9:
            bos.append((float(ps), xk, round(L, 2)))
OUT["duvar_bagi_bosluk"] = bos
OUT["duvar_bagi_not"] = "bos liste = psi 220...236'da duvar (2 mm) kesintisiz: kablo bagi icin yarik / delik yok"
# kaset govdesinde kucuk delikler (dikme, pim disinda) - yuz tiplerine gore silindirler
cyl = sorted(set((round(f.Surface.Radius, 2), round(O.yz_psi(f.Surface.Center.y, f.Surface.Center.z)[0], 1),
                  round(O.yz_psi(f.Surface.Center.y, f.Surface.Center.z)[1], 1)) for f in gv.Faces if "Cylinder" in f.Surface.TypeId
                 and f.Surface.Radius < 5))
OUT["govde_kucuk_silindirler"] = cyl
cylk = sorted(set((round(f.Surface.Radius, 2), round(O.yz_psi(f.Surface.Center.y, f.Surface.Center.z)[0], 1),
                   round(O.yz_psi(f.Surface.Center.y, f.Surface.Center.z)[1], 1)) for f in kp.Faces if "Cylinder" in f.Surface.TypeId
                  and f.Surface.Radius < 5))
OUT["kapak_kucuk_silindirler"] = cylk
json.dump(OUT, open(os.path.join(HERE, "K2-yuk.json"), "w", encoding="utf-8"), indent=1, default=str)
log(json.dumps(OUT, default=str)[:3000])
