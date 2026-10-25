# K3: kaset gorunum (S1-gorunum.py yontemi, yalniz okur; S1-gorunum.json'a YAZMAZ): Y1b oncesi (HEAD 102f246 FCStd) ve simdi.
import os, sys, shutil, tempfile, json
import FreeCAD as App
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
sys.path.insert(0, R)
import arayuz as A
oy = A.MODULLER["omuz_sag"]["konum"][1]
HEADF = os.environ.get("K3_HEAD_FCSTD")


def olc(src, et):
    tmp = os.path.join(tempfile.gettempdir(), "K3_gorunum_%s.FCStd" % et)
    shutil.copy2(src, tmp)
    d = App.openDocument(tmp)
    out, bant = {}, None
    for o in d.Objects:
        if o.TypeId != "Part::Feature":
            continue
        if o.Label.startswith("S1 kaset") and o.Label.endswith("sag"):
            b = o.Shape.BoundBox
            out[o.Label] = [round(v, 2) for v in (b.XMin, b.XMax, b.YMin - oy, b.YMax - oy, b.ZMin, b.ZMax)]
        if o.Label == "Omuz bandi sag":
            b = o.Shape.BoundBox
            bant = [round(v, 2) for v in (b.XMin, b.XMax, b.YMin - oy, b.YMax - oy, b.ZMin, b.ZMax)]
    App.closeDocument(d.Name)
    k = list(out.values())
    return dict(kaset_bb=out, ust_tasma_mm=round(max(v[3] for v in k) - bant[3], 2), on_tasma_mm=round(max(v[5] for v in k) - bant[5], 2),
                yan_tasma_mm=round(max(v[1] for v in k) - bant[1], 2))
S = dict(once=olc(HEADF, "once"), simdi=olc(os.path.join(R, "kabuk", "kabuk-montaj.FCStd"), "simdi"))
print(json.dumps(S, ensure_ascii=False))
json.dump(S, open(os.path.join(HERE, "K3-gorunum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
