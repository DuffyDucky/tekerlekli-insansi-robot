# -*- coding: utf-8 -*-
# Lale 1,58 m - USB koridoru (tabla ustu, SY8205 onu) icin en yakin parcalar + ust arka kapak vida sayisi. Yalniz sonuc.json'a "koridor" ve "ust_kapak_vida" ekler.
# FC_SCRIPT=<bu dosya> FC_MONTAJ=<kopya> freecadcmd run_fc.py   (yerlesim_olc.py'den sonra)
import os, sys, json
sys.dont_write_bytecode = True
import FreeCAD as App
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yerlesim_lib as Y
doc = App.openDocument(os.environ["FC_MONTAJ"])
P = []
for o in doc.Objects:
    if o.TypeId == "Part::Feature" and getattr(o, "Tur", "") != "Referans":
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        P.append((o.Label, s.copy()))
App.closeDocument(doc.Name)
t = Y.tup([Y.bas_g(62.0, 47.0, -37.0)] + Y.KORIDOR[1:], 2.0)
bb = t.BoundBox
bb.enlarge(30.0)
r = []
for ad, s in P:
    if s.BoundBox.intersect(bb) and not ad.startswith(("MAX98357A", "Kopuk bant (MAX")):
        r.append((ad, round(t.distToShape(s)[0], 2)))
r.sort(key=lambda q: q[1])
vida = sorted({ad for ad, _ in P if "ust arka kapak" in ad})
n_v = sum(1 for ad, _ in P if ad.startswith(("Kapak civatasi", "Civata")) and "ust arka kapak" in ad)
J = os.path.join(HERE, "sonuc.json")
d = json.load(open(J, encoding="utf-8"))
d["koridor"] = dict(not_="Pi USB -> tabla ustu -> trunk: tup O4; en yakin 8 parca", en_yakin=r[:8])
d["ust_kapak_etiket"] = dict(adlar=vida[:12], sayi=sum(1 for ad, _ in P if "ust arka kapak" in ad))
json.dump(d, open(J, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("KORIDOR", r[:8], flush=True)
print("KAPAK", vida[:12], d["ust_kapak_etiket"]["sayi"], flush=True)
