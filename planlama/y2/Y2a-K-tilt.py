import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "..", "tasarim", "freecad")   # planlama/y2 -> proje koku
sys.path.insert(0, os.path.join(R, "kafa")); sys.path.insert(0, R)
import FreeCAD as App
import kafa_parcalar as KP
P = KP.P
kaf = [p for p in P if p["grup"] == "Kafa" and p["tur"] != "Referans"]
sab = [p for p in P if p["grup"] in ("Pan", "Govde") and p["tur"] != "Referans"]
out = {}
for th in [15, 15.5, 16, 16.5, 17, 18, 19, 20, -15, -15.5, -16, -16.5, -17, -18, -19, -20]:
    pl = KP.grup_yer("Kafa", 0.0, th)
    hits, en = [], (1e9, None)
    for a in kaf:
        s = a["shape"].copy(); s.transformShape(pl.toMatrix(), True)
        bb = App.BoundBox(s.BoundBox); bb.enlarge(5)
        for b in sab:
            if not bb.intersect(b["shape"].BoundBox): continue
            d = s.distToShape(b["shape"])[0]
            if d < 1e-6:
                v = s.common(b["shape"]).Volume
                if v > 0.01: hits.append((a["ad"], b["ad"], round(v, 2)))
            if d < en[0]: en = (round(d, 3), a["ad"], b["ad"])
    out[str(th)] = dict(cakisma=hits[:5], en_kucuk=en)
    print(th, len(hits), en, flush=True)
json.dump(out, open(os.path.join(HERE, "Y2a-K-tilt.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
