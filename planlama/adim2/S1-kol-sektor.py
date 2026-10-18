# S1 kaseti: kol + ust kol (dirsek) parcalarinin gobek cercevesinde x<165 bolgesindeki aci (psi: +Y=0, -Z (arka)=90, -Y=180, +Z=270) ve yaricap kapsami; yalniz okur
import os, sys, math, shutil, tempfile, json
import FreeCAD as App, Part
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
V = App.Vector
def ac(rel):
    dst = os.path.join(tempfile.gettempdir(), "S1k_" + os.path.basename(rel)); shutil.copy2(os.path.join(R, rel), dst)
    d = App.openDocument(dst); out = []
    for o in d.Objects:
        if o.TypeId == "Part::Feature":
            par = o.getParentGeoFeatureGroup(); s = o.Shape.copy(); s.Placement = o.getGlobalPlacement()
            out.append((o.Label, par.Name if par else "-", s))
    App.closeDocument(d.Name); return out
OMU = ac("omuz/omuz-montaj.FCStd"); DIR = ac("dirsek/dirsek-montaj.FCStd")
def pts(s, d=0.3):
    P = []
    for f in s.Faces:
        try:
            p, _ = f.tessellate(d); P += [(q.x, q.y, q.z) for q in p]
        except Exception: pass
    return np.array(P)
kol = [s for (a, g, s) in OMU if g == "Kol"] + [s for (a, g, s) in DIR if g == "UstKol"]
gob = [(a, s) for (a, g, s) in OMU if g == "Gobek"]
K = np.vstack([pts(s) for s in kol])
out = []
for th in (5, 10, 20, 40, 80, 120):
    a = math.radians(th); c, s_ = math.cos(a), math.sin(a)
    x = 185 + (K[:, 0] - 185) * c - K[:, 1] * s_; y = (K[:, 0] - 185) * s_ + K[:, 1] * c; z = K[:, 2]
    r = np.hypot(y, z); psi = np.degrees(np.arctan2(-z, y)) % 360
    m = (x < 165) & (r > 30) & (r < 85)
    if m.any():
        print("S2 %3d: x<165 noktalari psi %.1f..%.1f  r %.1f..%.1f  xmin %.2f" % (th, psi[m].min(), psi[m].max(), r[m].min(), r[m].max(), x[m].min()))
    else:
        print("S2 %3d: x<165 yok" % th)
    for xl in (161, 163):
        m = (x < xl) & (r > 30) & (r < 85)
        if m.any(): print("   x<%d: psi %.1f..%.1f r %.1f..%.1f" % (xl, psi[m].min(), psi[m].max(), r[m].min(), r[m].max()))
G = np.vstack([pts(s) for a, s in gob])
r = np.hypot(G[:, 1], G[:, 2]); psi = np.degrees(np.arctan2(-G[:, 2], G[:, 1])) % 360
m = (G[:, 0] < 163.01) & (r > 24)
print("gobek x<163 r>24:", m.sum(), (G[m, 0].min() if m.any() else None))
for a, s in gob: print(a, [round(v, 1) for v in (s.BoundBox.XMin, s.BoundBox.XMax, s.BoundBox.YMin, s.BoundBox.YMax, s.BoundBox.ZMin, s.BoundBox.ZMax)])
