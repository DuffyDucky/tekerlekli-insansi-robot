# FreeCAD'de omuz montajini acar ve kolu bir tur oynatir (ASCII baslaticiyla freecad.exe uzerinden)
import os, sys, math
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
XR = 185.0
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))
import arayuz as A
Y0 = int(A.OMUZ["yana_aralik"][0])   # yana acma yazilim alt siniri (15 Ekim 2026: 5); kareler 0'a (sinir disi) inmez
doc = App.openDocument(os.path.join(HERE, "omuz-montaj.FCStd"))


def poz(phi, th):
    gp = App.Placement(V(0, 0, 0), App.Rotation(V(-1, 0, 0), phi), V(0, 0, 0))
    doc.getObject("Gobek").Placement = gp
    doc.getObject("Kol").Placement = gp.multiply(App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(XR, 0, 0)))


seq = []
for _ in range(2):
    seq += [(p, Y0) for p in range(0, 121, 3)] + [(120, t) for t in range(Y0, 91, 3)] + \
           [(120 - p, max(Y0, 90 - int(p * 0.75))) for p in range(0, 121, 3)] + [(0, Y0)] * 10
state = {"i": 0}


def adim():
    if state["i"] >= len(seq):
        timer.stop()
        poz(0, Y0)
        return
    poz(*seq[state["i"]])
    state["i"] += 1


def basla():
    Gui.getMainWindow().showMaximized()
    v = Gui.getDocument(doc.Name).activeView()
    z = V(0.6, 0.35, 1.0).normalize()
    x = V(0, 1, 0).cross(z).normalize()
    v.setCameraOrientation(App.Rotation(x, x.cross(z) * -1, z, "ZYX"))
    v.fitAll()
    cam = v.getCameraNode()
    p = V(165, -50, 30) + z * cam.focalDistance.getValue()
    cam.position.setValue(p.x, p.y, p.z)
    cam.height.setValue(420)
    timer.start(40)


timer = QtCore.QTimer()
timer.timeout.connect(adim)
QtCore.QTimer.singleShot(2500, basla)
