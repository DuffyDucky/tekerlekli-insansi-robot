# P10.8d B: (1) E4 arka kafa kabugu dikisi bagimsiz supurme (adim 1 mm), (2) panel alti vida basi oturmasi (yuz kesisimi).
import os, json, time
import FreeCAD as App
import Part
V = App.Vector
t0 = time.time()
R = os.environ["B_ROBOT"]; OUT = os.environ["B_CIKTI"]; TABANLAR = os.environ["B_TABANLAR"].split(";")
FC = os.path.join(R, "tasarim", "freecad")
out = {}


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


# ---- (1) E4
d = App.openDocument(os.path.join(FC, "montaj", "robot-montaj.FCStd"))
K = {}
for o in d.Objects:
    if o.TypeId == "Part::Feature" and o.Label in ("Arka kafa kabugu sag", "Arka kafa kabugu sol"):
        s = o.Shape.copy(); s.Placement = o.getGlobalPlacement(); K[o.Label] = s.copy()
SAG, SOL = K["Arka kafa kabugu sag"], K["Arka kafa kabugu sol"]
e4 = dict(sag_bb=[round(x, 2) for x in (SAG.BoundBox.XMin, SAG.BoundBox.XMax, SAG.BoundBox.ZMin, SAG.BoundBox.ZMax)],
          sol_bb=[round(x, 2) for x in (SOL.BoundBox.XMin, SOL.BoundBox.XMax, SOL.BoundBox.ZMin, SOL.BoundBox.ZMax)],
          yerinde_ortak=round(SAG.common(SOL).Volume, 4), yerinde_mesafe=round(SAG.distToShape(SOL)[0], 4))


def ilk(mov, fix, v, adim=1.0, mx=160.0):
    u = V(*v); u.normalize(); t = 0.0
    while t < mx:
        t += adim
        m = mov.copy(); m.translate(u * t)
        if not m.BoundBox.intersect(fix.BoundBox):
            return ("serbest", round(t, 1))
        c = m.common(fix).Volume
        if c > 0.5:
            return ("kapali", round(t, 2), round(c, 2))
    return ("serbest_max", t)


YON = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1), "-z": (0, 0, -1), "+x+z": (1, 0, 1), "-x-z": (-1, 0, -1), "+y-z": (0, 1, -1)}
e4["sag_hareketli"] = {k: ilk(SAG, SOL, v, 0.25 if k == "-z" else 1.0) for k, v in YON.items()}
log("sag", e4["sag_hareketli"])
e4["sol_hareketli"] = {k: ilk(SOL, SAG, v, 0.25 if k in ("+z", "-z") else 1.0) for k, v in YON.items()}
log("sol", e4["sol_hareketli"])
# kesit: y orta, x -18..2, z -66..-60 (0,25 mm) hangi kabuk
yh = 0.5 * (SAG.BoundBox.YMin + SAG.BoundBox.YMax)
sat = []
for i in range(25):
    z = -66.0 + 0.25 * i
    sat.append("z %+7.2f " % z + "".join({(1, 0): "R", (0, 1): "L", (1, 1): "X", (0, 0): "."}[(int(SAG.isInside(V(-18 + 0.5 * j, yh, z), 1e-4, False)), int(SOL.isInside(V(-18 + 0.5 * j, yh, z), 1e-4, False)))] for j in range(41)))
e4["kesit_y"] = round(yh, 1); e4["kesit"] = sat
log("\n".join(sat))
out["e4"] = e4

# ---- (2) vida basi oturma (panel alti)
for tb in TABANLAR:
    dt = App.openDocument(tb)
    P = {o.Label: o for o in dt.Objects if o.TypeId == "Part::Feature"}
    pan = P["Guc paneli (arka kat)"].Shape
    pmin = pan.BoundBox.YMin
    pa = [f for f in pan.Faces if abs(f.BoundBox.YMin - pmin) < 1e-4 and abs(f.BoundBox.YMax - pmin) < 1e-4]
    res = []
    for ad, o in P.items():
        if not (ad.startswith("Vida") and ad.endswith("alt)") and ("On sarj" in ad or "dugum" in ad or "Dagitim karti C" in ad)):
            continue
        s = o.Shape
        fs = [f for f in s.Faces if abs(f.BoundBox.YMin - pmin) < 1e-3 and abs(f.BoundBox.YMax - pmin) < 1e-3]
        tam = sum(f.Area for f in fs)
        des = sum(f.common(g).Area for f in fs for g in pa)
        res.append([ad[-50:], round(s.BoundBox.Center.x, 2), round(s.BoundBox.Center.z, 2), round(tam, 3), round(des, 3), round(des / tam, 3) if tam else None])
    out["vida_" + os.path.basename(os.path.dirname(tb))] = res
    log(tb, res)
    App.closeDocument(dt.Name)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("BITTI")
