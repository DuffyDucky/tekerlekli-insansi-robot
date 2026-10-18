# S1 kaseti gorunum olcusu (yalniz okur): kaset govdesi + kapagi sinir kutusu omuz yerelinde, kabuk ust yuzu (y 30) ve on yuzune gore
import os, sys, shutil, tempfile, json
import FreeCAD as App
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
sys.path.insert(0, R)
import arayuz as A
tmp = os.path.join(tempfile.gettempdir(), "S1_gorunum_kabuk.FCStd")
shutil.copy2(os.path.join(R, "kabuk", "kabuk-montaj.FCStd"), tmp)
d = App.openDocument(tmp)
oy = A.MODULLER["omuz_sag"]["konum"][1]
out = {}
bant = None
for o in d.Objects:
    if o.TypeId != "Part::Feature":
        continue
    if o.Label.startswith("S1 kaset") and o.Label.endswith("sag"):
        b = o.Shape.BoundBox
        out[o.Label] = [round(v, 1) for v in (b.XMin, b.XMax, b.YMin - oy, b.YMax - oy, b.ZMin, b.ZMax)]
    if o.Label == "Omuz bandi sag":
        b = o.Shape.BoundBox
        bant = [round(v, 1) for v in (b.XMin, b.XMax, b.YMin - oy, b.YMax - oy, b.ZMin, b.ZMax)]
App.closeDocument(d.Name)
k = list(out.values())
ymax = max(v[3] for v in k); zmax = max(v[5] for v in k); xmax = max(v[1] for v in k)
sonuc = dict(kaset_bb=out, omuz_bandi_bb=bant, ust_tasma_mm=round(ymax - bant[3], 1), on_tasma_mm=round(zmax - bant[5], 1),
             yan_tasma_mm=round(xmax - bant[1], 1), not_="omuz yereli (y 0 = S1 ekseni); tasma = kaset en uc - omuz bandi en uc")
print(json.dumps(sonuc, ensure_ascii=False))
json.dump(sonuc, open(os.path.join(HERE, "S1-gorunum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
