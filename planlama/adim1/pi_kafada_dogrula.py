# Secilen aday (R0, t=(-34,189,1)) icin kesin dogrulama: kafa parcalariyla cakisma + en yakin 3 parca, tilt taramasinda Pan/Govde ile cakisma.
import os, sys, json, math
import numpy as np
import FreeCAD as App
import Part
BU = os.path.dirname(os.path.abspath(__file__))
FC = os.path.join(os.path.dirname(os.path.dirname(BU)), "tasarim", "freecad")
for _p in (os.path.join(FC, "kafa"), FC):
    sys.path.insert(0, _p)
sys.dont_write_bytecode = True
import kafa_parcalar as KP
V = App.Vector
GOVDE = [("PCB", 0, 85, 0, 56, 0, 1.3), ("alt pay", 0, 85, 0, 56, -1.5, 0), ("USB-C+HDMI", 6.5, 46, -1.7, 6.2, 1.3, 4.6),
         ("CSI", 47, 57, 0, 17, 1.3, 5.3), ("USB/Eth", 66.4, 88.1, 2.3, 54.2, -0.7, 17.5), ("GPIO", 7, 58, 50, 55.5, 1.3, 11.0),
         ("Cooler", 6, 69.5, 6.5, 49, 1.3, 15.0)]
KOR = [("fan 10", 6, 69.5, 6.5, 49, 15.0, 25.0), ("kablo 30", 6.5, 57, -30, 0, -1, 12), ("USB 20", 88.1, 108, 2.3, 54.2, -1, 17.5),
       ("SD 15", -15, 0, 18, 38, -3, 6)]
R = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]
T = (-34.0, 189.0, 1.0)
m = App.Matrix(R[0][0], R[0][1], R[0][2], T[0], R[1][0], R[1][1], R[1][2], T[1], R[2][0], R[2][1], R[2][2], T[2], 0, 0, 0, 1)
def sk(parts):
    bx = []
    for (_, x0, x1, y0, y1, z0, z1) in parts:
        b = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0)); b.transformShape(m); bx.append(b)
    return bx[0].fuse(bx[1:])
body, kor = sk(GOVDE), sk(KOR)
out = dict(bb_govde=[round(v, 1) for v in (body.BoundBox.XMin, body.BoundBox.XMax, body.BoundBox.YMin, body.BoundBox.YMax, body.BoundBox.ZMin, body.BoundBox.ZMax)],
           bb_koruma=[round(v, 1) for v in (kor.BoundBox.XMin, kor.BoundBox.XMax, kor.BoundBox.YMin, kor.BoundBox.YMax, kor.BoundBox.ZMin, kor.BoundBox.ZMax)])
KAF = [p for p in KP.P if p["grup"] == "Kafa" and p["tur"] != "Referans"]
dist = []
ov = []
for p in KAF:
    sh = p["shape"]
    d = body.distToShape(sh)[0]; dk = kor.distToShape(sh)[0]
    dist.append((round(d, 2), round(dk, 2), p["ad"]))
    if body.BoundBox.intersect(sh.BoundBox) and body.common(sh).Volume > 0.01: ov.append(("govde", p["ad"]))
    if kor.BoundBox.intersect(sh.BoundBox) and kor.common(sh).Volume > 0.01: ov.append(("koruma", p["ad"]))
dist.sort()
out["en_yakin_govde"] = dist[:5]
out["en_yakin_koruma"] = sorted(dist, key=lambda r: r[1])[:5]
out["cakisma"] = ov
tc = []
mind = 1e9
for th in range(-25, 31, 5):
    for nm, sh0 in (("govde", body), ("koruma", kor)):
        bt = sh0.copy(); bt.transformShape(KP.Ptilt(th).toMatrix())
        for p in [q for q in KP.P if q["grup"] in ("Pan", "Govde")]:
            sh = p["shape"]
            d = bt.distToShape(sh)[0]
            mind = min(mind, d)
            if bt.BoundBox.intersect(sh.BoundBox) and bt.common(sh).Volume > 0.01: tc.append((th, nm, p["ad"]))
out["tilt_cakisma"] = tc
out["tilt_en_yakin_pan_govde_mm"] = round(mind, 2)
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join(BU, "pi_kafada_dogrula_sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
