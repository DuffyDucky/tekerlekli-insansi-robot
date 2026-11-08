# -*- coding: utf-8 -*-
# Lale 1,58 m - F1a P1.7 hoparlor arka tutucu gorselleri (FreeCAD GUI). kabuk_parcalar'i import eder, hoparlor cevresindeki parcalari
# gecici belgeye koyar; hicbir sey kaydetmez. Cikti: gorsel/P17-hoparlor-ic.png (govde icinden, bant yari saydam),
# gorsel/P17-hoparlor-kesit-eksen.png (hoparlor ekseninden, x = HOP_C.x), gorsel/P17-hoparlor-kesit-civata.png (civata ekseninden).
#   FC_SCRIPT=<bu dosya> freecad.exe run_fc.py
import os, sys, tempfile, traceback
sys.dont_write_bytecode = True
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore
from pivy import coin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
OUT = os.path.join(HERE, "gorsel")
LOG = os.path.join(tempfile.gettempdir(), "hoparlor_gorsel.log")
open(LOG, "w").close()
R = dict(bant=(0.86, 0.87, 0.90), kap=(0.96, 0.55, 0.13), kel=(0.18, 0.52, 0.86), hop=(0.15, 0.15, 0.17), ped=(0.95, 0.85, 0.25),
         celik=(0.50, 0.52, 0.56), pirinc=(0.86, 0.66, 0.22), gri=(0.62, 0.62, 0.64))


def log(*a):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


def kamera(v, eye, h, merkez, up_=None):
    z = V(*eye).normalize()
    up = up_ or (V(0, 1, 0) if abs(z.y) < 0.99 else V(0, 0, -1))
    x = up.cross(z).normalize()
    y = z.cross(x)
    q = App.Rotation(x, y, z, "ZYX").Q
    cam = v.getCameraNode()
    cam.orientation.setValue(coin.SbRotation(q[0], q[1], q[2], q[3]))
    v.fitAll()
    pos = V(*merkez) + z * cam.focalDistance.getValue()
    cam.position.setValue(pos.x, pos.y, pos.z)
    cam.height.setValue(h)


def go():
    for p_ in (LALE, UST, os.path.join(UST, "kabuk"), os.path.join(UST, "kafa")):
        if p_ not in sys.path:
            sys.path.insert(0, p_)
    import kabuk_parcalar as K
    C, N = K.HOP_C, K.HOP_N
    log("HOP_C", C, "HOP_N", N)
    doc = App.newDocument("p17")
    gd = Gui.getDocument(doc.Name)
    v = gd.activeView()
    v.setAnimationEnabled(False)
    v.setCameraType("Orthographic")
    kutu = Part.makeBox(180, 140, 140, C - V(90, 70, 70))
    ob = []
    for p in K.P:
        sh = p["shape"]
        if p.get("tur") == "Referans" or not sh.BoundBox.intersect(kutu.BoundBox):
            continue
        ad = p["ad"]
        s_ = sh.common(kutu) if ad.startswith(("Govde", "Gogus")) else sh
        if s_.Volume < 1e-3:
            continue
        o = doc.addObject("Part::Feature", "P%d" % len(ob))
        o.Label = ad
        o.Shape = s_
        vo = gd.getObject(o.Name)
        if ad.startswith("Hoparlor kelepcesi"):
            c, t = R["kel"], 0
        elif ad.startswith("Hoparlor kabi"):
            c, t = R["kap"], 0
        elif ad.startswith("Hoparlor 40"):
            c, t = R["hop"], 0
        elif ad.startswith("Kopuk ped"):
            c, t = R["ped"], 0
        elif "civata" in ad.lower():
            c, t = R["celik"], 0
        elif ad.startswith("Isil gomme"):
            c, t = R["pirinc"], 0
        elif ad.startswith(("Govde", "Gogus")):
            c, t = R["bant"], 60
        else:
            c, t = R["gri"], 50
        vo.ShapeColor = c
        vo.Transparency = t
        ob.append(o)
    log("parca", [o.Label for o in ob])
    Gui.updateGui()
    ic = C + N * -60.0                                  # govde ici (hoparlorun arkasi)
    m = C + N * -12.0
    kamera(v, (ic - C).normalize() + V(0.45, 0.35, 0), 120, (m.x, m.y, m.z))
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "P17-hoparlor-ic.png"), 1200, 1000, "White")
    log("ic")
    for ad, xk in (("P17-hoparlor-kesit-eksen.png", C.x), ("P17-hoparlor-kesit-civata.png", C.x + K._HP["kulak_e"])):
        yarim = Part.makeBox(200, 300, 300, V(xk - 200, C.y - 150, C.z - 150))
        yeni = []
        for o in ob:
            vo = gd.getObject(o.Name)
            vo.Visibility = False
            c_ = o.Shape.common(yarim)
            if c_.Volume > 1e-3:
                n = doc.addObject("Part::Feature", "K_" + o.Name)
                n.Shape = c_
                gn = gd.getObject(n.Name)
                gn.ShapeColor = vo.ShapeColor
                gn.Transparency = 0
                yeni.append(n)
        kamera(v, (1, 0, 0), 90, (xk, m.y, m.z))
        Gui.updateGui()
        v.saveImage(os.path.join(OUT, ad), 1200, 1000, "White")
        log(ad)
        for n in yeni:
            doc.removeObject(n.Name)
        for o in ob:
            gd.getObject(o.Name).Visibility = True
    App.closeDocument(doc.Name)
    log("BITTI")


def guvenli():
    try:
        go()
    except Exception:
        log(traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
