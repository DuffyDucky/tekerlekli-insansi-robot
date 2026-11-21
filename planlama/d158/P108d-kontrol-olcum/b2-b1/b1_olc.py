# B2: bulgu B1 (yol 11 x Sonar tutucu sol) en yakin noktalar ve yola gore konumu. Salt okur; JSON'u scratchpad'e yazar.
import FreeCAD, json, os
R = r"."
OUT = r"<gecici>\b1.json"
doc = FreeCAD.openDocument(os.path.join(R, "tasarim", "freecad", "taban", "taban-montaj.FCStd"))
def bul(on):
    return [o for o in doc.Objects if o.Label.startswith(on) and hasattr(o, "Shape") and not o.Shape.isNull() and o.Shape.Volume > 0]
yol = bul("Kablo yolu 11")
son = bul("Sonar tutucu sol")
out = dict(yol=[o.Label for o in yol], sonar=[o.Label for o in son], olcum=[])
for y in yol:
    for s in son:
        d, pts, info = y.Shape.distToShape(s.Shape)
        com = y.Shape.common(s.Shape).Volume
        out["olcum"].append(dict(yol=y.Label[:40], parca=s.Label, mesafe=round(d, 4), ortak_mm3=round(com, 4),
                                 noktalar=[[[round(c, 2) for c in (p[0].x, p[0].y, p[0].z)], [round(c, 2) for c in (p[1].x, p[1].y, p[1].z)]] for p in pts[:4]],
                                 yol_bb=[round(v, 2) for v in (y.Shape.BoundBox.XMin, y.Shape.BoundBox.XMax, y.Shape.BoundBox.YMin, y.Shape.BoundBox.YMax, y.Shape.BoundBox.ZMin, y.Shape.BoundBox.ZMax)],
                                 parca_bb=[round(v, 2) for v in (s.Shape.BoundBox.XMin, s.Shape.BoundBox.XMax, s.Shape.BoundBox.YMin, s.Shape.BoundBox.YMax, s.Shape.BoundBox.ZMin, s.Shape.BoundBox.ZMax)]))
# sonar sol govdesi / pin blogu: yolun basladigi parca(lar)
out["sonar_diger"] = []
for o in bul("Sonar"):
    if o.Label.startswith("Sonar tutucu"):
        continue
    for y in yol:
        d = y.Shape.distToShape(o.Shape)[0]
        if d < 15:
            out["sonar_diger"].append([o.Label, round(d, 3)])
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("B1 YAZILDI", OUT)
