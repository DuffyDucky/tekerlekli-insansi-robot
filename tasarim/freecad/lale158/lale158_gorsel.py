# Lale 1,58 m - gorseller (FreeCAD GUI icinde): on, yan, izometrik (tam robot), gogus on / kesit / arka (kabuk gizli), kafa on, kablo yolu.
# FC_SCRIPT=<bu dosya> freecad.exe run_fc.py   montaj/ana_montaj.py'den sonra. Dosya kaydedilmez; montajin kendisi degismez.
import os, sys, tempfile, traceback
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore
from pivy import coin  # noqa

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for p_ in (HERE, UST):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A
import kablo_yolu_ekran as KY

OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(tempfile.gettempdir(), "lale158_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22), "siyah": (0.13, 0.13, 0.14),
        "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22), "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6), "pcb": (0.15, 0.45, 0.25)}
KABLO_RENK = {"HDMI": (0.85, 0.15, 0.15), "USB dokunmatik": (0.15, 0.35, 0.9), "12 V": (0.95, 0.75, 0.05)}


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


def kamera(v, eye, h, merkez):
    z = V(*eye).normalize()
    up = V(0, 1, 0) if abs(z.y) < 0.99 else V(0, 0, -1)
    x = up.cross(z).normalize()
    y = z.cross(x)
    q = App.Rotation(x, y, z, "ZYX").Q
    cam = v.getCameraNode()
    cam.orientation.setValue(coin.SbRotation(q[0], q[1], q[2], q[3]))
    v.fitAll()
    pos = V(*merkez) + z * cam.focalDistance.getValue()
    cam.position.setValue(pos.x, pos.y, pos.z)
    cam.height.setValue(h)


def kaydet(v, ad, w=1200, h=1200):
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, ad), w, h, "White")
    log("gorsel", ad)


def go():
    doc = App.openDocument(os.path.join(UST, "montaj", "robot-montaj.FCStd"))
    gd = Gui.getDocument(doc.Name)
    Gui.updateGui()
    for o in doc.Objects:
        vo = gd.getObject(o.Name)
        if vo is None:
            continue
        if o.TypeId in ("App::Part", "Assembly::AssemblyObject"):
            vo.Visibility = True
        elif o.TypeId == "Part::Feature":
            vo.Visibility = getattr(o, "Tur", "") != "Referans"
            rk = RENK.get(getattr(o, "Renk", "gri"), RENK["gri"])
            try:
                vo.ShapeColor = rk
            except Exception:
                pass
        elif "Joint" in o.TypeId or o.TypeId == "App::FeaturePython":
            try:
                vo.Visibility = False
            except Exception:
                pass
    # eklem gruplari gizli (goruntu kirliligi)
    for o in doc.Objects:
        if o.TypeId == "Assembly::JointGroup":
            gd.getObject(o.Name).Visibility = False
    v = Gui.activeDocument().activeView()
    v.setAnimationEnabled(False)
    v.setCameraType("Orthographic")
    Gui.updateGui()
    kamera(v, (0, 0, 1), 1700, (0, 790, 0)); kaydet(v, "lale158-on.png", 1100, 1500)
    kamera(v, (1, 0, 0), 1700, (0, 790, 0)); kaydet(v, "lale158-yan.png", 1100, 1500)
    kamera(v, (0.7, 0.4, 1.0), 1800, (0, 790, 0)); kaydet(v, "lale158-izometrik.png", 1200, 1500)

    yc = A.GOGUS_EKRAN_Y
    kamera(v, (0, 0.26, 0.97), 420, (0, yc, 80)); kaydet(v, "gogus-on.png")
    kamera(v, (0.75, 0.25, 0.9), 520, (0, yc + 20, 60)); kaydet(v, "gogus-izometrik.png")
    kamera(v, (0, 0, 1), 460, (0, A.S3 + 150, 0)); kaydet(v, "kafa-on.png")
    kamera(v, (0.8, 0.2, 0.9), 480, (0, A.S3 + 170, 0)); kaydet(v, "kafa-izometrik.png")

    # kablolar (gecici nesneler, kaydedilmez)
    for ad, yol in KY.yollar().items():
        r = max(KY.KABLO[ad][0] / 2, 3.0)
        t = None
        for a_, b_ in zip(yol[:-1], yol[1:]):
            a_, b_ = V(*a_), V(*b_)
            if (b_ - a_).Length < 1e-6:
                continue
            c = Part.makeCylinder(r, (b_ - a_).Length, a_, b_ - a_).fuse(Part.makeSphere(r, b_))
            t = c if t is None else t.fuse(c)
        o = doc.addObject("Part::Feature", "Kablo_" + ad.split()[0])
        o.Shape = t
        gd.getObject(o.Name).ShapeColor = KABLO_RENK[ad]
    Gui.updateGui()
    # kabuk ve omuz disi gizli: ic gorunus (iskelet, tasiyici, kasa, kablo, kafa ici)
    gizle = []
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" and hasattr(o, "Tur"):
            lb = o.Label
            if lb.startswith(("Gogus bandi", "Omuz bandi", "Govde orta", "Govde uzatma", "Govde alt", "Ust arka servis", "Arka servis", "Yuz kabugu", "Arka kafa kabugu")):
                vo = gd.getObject(o.Name)
                if vo.Visibility:
                    vo.Visibility = False
                    gizle.append(vo)
    Gui.updateGui()
    kamera(v, (-0.75, 0.2, -0.9), 620, (0, yc + 40, 20)); kaydet(v, "gogus-arka-kablo.png")
    kamera(v, (1, 0.05, 0.02), 760, (0, A.S3 - 30, 20)); kaydet(v, "kablo-yan.png", 1100, 1500)
    kamera(v, (-1, 0.2, 0.6), 760, (0, A.S3 - 30, 20)); kaydet(v, "kablo-izometrik.png", 1100, 1500)
    for vo in gizle:
        vo.Visibility = True
    # kesit x = 0: gecici kirpma (Part::Feature kopyalari yerine gorunum kirpmasi)
    try:
        doc.recompute()
        from pivy import coin as _c
        sg = v.getSceneGraph()
        cp = _c.SoClipPlane()
        cp.plane.setValue(_c.SbPlane(_c.SbVec3f(-1, 0, 0), 0.5))
        sg.insertChild(cp, 0)
        Gui.updateGui()
        kamera(v, (1, 0, 0), 480, (0, yc + 30, 30)); kaydet(v, "gogus-kesit.png")
        kamera(v, (1, 0, 0), 460, (0, A.S3 + 150, 0)); kaydet(v, "kafa-kesit.png")
        sg.removeChild(cp)
    except Exception:
        log(traceback.format_exc())
    App.closeDocument(doc.Name)
    log("bitti")
    Gui.getMainWindow().close()


def guvenli():
    try:
        go()
    except Exception:
        log(traceback.format_exc())
        Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
