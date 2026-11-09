# Tani: (1) ust arka kapak z 2,5 destek sorunu gercek mi; (2) AI HAT+ zarfi x kabuk nerede, onceki kafada var miydi. Dosya yazmaz (tani.json haric).
import os, sys, json
sys.dont_write_bytecode = True
import FreeCAD as App
import Part
V = App.Vector
UST = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p_ in (UST, os.path.join(UST, "kabuk"), os.path.join(UST, "kafa")):
    sys.path.insert(0, p_)
import arayuz as A
S = {}
import kabuk_parcalar as K
d = K.PARCA["Ust arka servis kapagi"]
sh = K.P[d["indeks"]]["shape"]
rot = App.Rotation(V(*d["yukari"]), V(0, 0, 1))
s = sh.copy()
s.transformShape(App.Placement(V(0, 0, 0), rot).toMatrix(), True)
bb = s.BoundBox
S["kapak_bb"] = [round(x, 3) for x in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]
S["kapak_valid"] = s.isValid()
S["kapak_hacim"] = round(sh.Volume, 1)
zmin = bb.ZMin
kat = []
onceki = None
for k in range(0, 13):
    z = zmin + 0.5 + k
    if z >= bb.ZMax:
        break
    ws = s.slice(V(0, 0, 1), z)
    # F6a (P6.1; F1b P1.5 kabuk_montaj.baski_analiz kalibi): teller kapali degilse makeFace cagrilmaz (eskiden hata katmani atlatiyor /
    # betigi durduruyordu); duzlem 0,05 / 0,1 / 0,25 mm kaydirilip yeniden kesilir, yuz katman duzlemine geri tasinir (kaydirma alaninda).
    yuz, kdz = None, None
    for _dz in (0.0, 0.05, -0.05, 0.1, -0.1, 0.25, -0.25):
        try:
            ws2 = s.slice(V(0, 0, 1), z + _dz)
        except Exception:
            ws2 = None
        if not ws2:
            break
        if all(w.isClosed() for w in ws2):
            try:
                yuz = Part.makeFace(ws2, "Part::FaceMakerBullseye")
            except Exception:
                yuz = None
            if yuz is not None and _dz != 0.0:
                yuz.translate(V(0, 0, -_dz))
            kdz = _dz
            break
    r = dict(z=round(z - zmin, 2), tel=len(ws), kapali=[w.isClosed() for w in ws][:12], alan=round(yuz.Area, 1) if yuz else None, yuz=len(yuz.Faces) if yuz else 0,
             kaydirma=kdz)
    if yuz is not None and onceki is not None:
        dest = []
        hata = []
        for f in onceki.Faces:
            try:
                dest.append(f.makeOffset2D(1.0, 0))
            except Exception as e:
                hata.append(repr(e)[:60])
                dest.append(f)
        dd = dest[0].fuse(dest[1:]) if len(dest) > 1 else dest[0]
        dd.translate(V(0, 0, 1.0))
        ac = yuz.cut(dd)
        r["acik"] = [(round(f.Area, 2), round(max(f.BoundBox.XLength, f.BoundBox.YLength), 1)) for f in ac.Faces][:10]
        r["ofset_hata"] = hata
        r["dest_alan"] = round(dd.Area, 1)
        # bagimsiz denetim: bu katman yuzu, bir onceki katman yuzune dogrudan (ofsetsiz) izdusumde ne kadar tasiyor
        o2 = onceki.copy()
        o2.translate(V(0, 0, 1.0))
        r["ofsetsiz_tasma_mm2"] = round(yuz.cut(o2).Area, 2)
    kat.append(r)
    onceki = yuz
S["kapak_katman"] = kat
# dogrudan kati denetimi: z 1,5 ve 2,5 arasinda kati kesiti
print(json.dumps(S, ensure_ascii=False)[:3000], flush=True)
# ------------------------------------------------------------ AI HAT+ zarfi
doc = App.openDocument(os.path.join(UST, "kafa", "kafa-montaj.FCStd"))
K_ = A.KAFA
YT, ZT = K_["tilt_nokta"][1], K_["tilt_nokta"][2]
x0, z1 = -42.5, -27.893
ah = Part.makeBox(65.0, 4.6, 56.5, V(x0, YT + 41.6 + 16.0, ZT + z1 - 56.5))
S["ai_kafa"] = []
for o in doc.Objects:
    if o.TypeId == "Part::Feature" and getattr(o, "Tur", "") != "Referans":
        t = o.Shape.copy()
        t.Placement = o.getGlobalPlacement()
        t = t.copy()
        if t.BoundBox.intersect(ah.BoundBox):
            c = t.common(ah)
            if c.Volume > 1e-3:
                b = c.BoundBox
                S["ai_kafa"].append(dict(ad=o.Label, v=round(c.Volume, 2), bb_bas=[round(q, 2) for q in (b.XMin, b.XMax, b.YMin - YT, b.YMax - YT, b.ZMin - ZT, b.ZMax - ZT)]))
App.closeDocument(doc.Name)
print(json.dumps(S["ai_kafa"], ensure_ascii=False), flush=True)
json.dump(S, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "uygulama-tani.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("BITTI", flush=True)
