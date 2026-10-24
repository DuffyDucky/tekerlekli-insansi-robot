# Lale 1,70 m taslak: GUI kurulumu + gorseller (FreeCAD GUI icinde calisir; taslak_montaj.py'den SONRA)
#   FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecad.exe" C:/Users/Victus/.robot-cad/run_fc.py
# 1) taslak-170.FCStd: gizli gelen montaj/gruplar/parcalar gorunur, renkler, eklem gorunum nesneleri; dosya GUI'den kaydedilir.
# 2) %TEMP%/taslak170-gorsel.FCStd (renk bazinda bilesik, yeni + eski 125 cm): onden, yandan, izometrik, kafa yakin, sag kol yakin,
#    karsilastirma -> gorsel/
import os, sys, math, tempfile, traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin  # noqa

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
GORSEL_DOC = os.path.join(tempfile.gettempdir(), "taslak170-gorsel.FCStd")
LOG = os.path.join(tempfile.gettempdir(), "taslak170-gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22),
        "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22),
        "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6), "pcb": (0.10, 0.45, 0.25), "pcb_k": (0.10, 0.45, 0.25),
        "pcb_m": (0.15, 0.30, 0.60), "ahsap": (0.80, 0.65, 0.45), "aku": (0.25, 0.30, 0.35), "kirmizi": (0.85, 0.15, 0.12),
        "koyu": (0.25, 0.25, 0.28), "lastik": (0.10, 0.10, 0.10), "motor": (0.62, 0.64, 0.68), "naylon": (0.92, 0.92, 0.88),
        "vizor": (0.05, 0.05, 0.07), "kablo": (0.9, 0.3, 0.2)}


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


def kaydet(v, ad, w=1400, h=1000):
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, ad), w, h, "White")
    log("gorsel", ad)


def montaj_dosyasi():
    import JointObject
    doc = App.openDocument(os.path.join(HERE, "taslak-170.FCStd"))
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if o.TypeId in ("Assembly::AssemblyObject", "App::Part", "Part::Feature"):
            gd.getObject(o.Name).Visibility = True
        if o.TypeId == "Part::Feature":
            gd.getObject(o.Name).ShapeColor = RENK.get(getattr(o, "Renk", "gri"), RENK["gri"])
    n = 0
    for o in doc.Objects:
        if o.TypeId == "App::FeaturePython" and hasattr(o, "Proxy"):
            if isinstance(o.Proxy, JointObject.GroundedJoint):
                JointObject.ViewProviderGroundedJoint(o.ViewObject).attach(o.ViewObject)
            elif isinstance(o.Proxy, JointObject.Joint):
                JointObject.ViewProviderJoint(o.ViewObject).attach(o.ViewObject)
                o.ViewObject.Proxy.redrawJointPlacements(o)
                n += 1
            o.ViewObject.Visibility = True
    Gui.updateGui()
    doc.save()
    log("montaj dosyasi kaydedildi, eklem gorunumu", n)
    App.closeDocument(doc.Name)


def gorseller():
    doc = App.openDocument(GORSEL_DOC)
    gd = Gui.getDocument(doc.Name)
    Gui.activateView("Gui::View3DInventor", True)
    v = Gui.activeDocument().activeView()
    v.setCameraType("Orthographic")
    for o in doc.Objects:
        vo = gd.getObject(o.Name)
        vo.ShapeColor = RENK.get(o.Renk, RENK["gri"])
        vo.Visibility = True
        if o.Renk in ("celik", "pirinc"):
            vo.LineWidth = 1.0
    yeni = [o for o in doc.Objects if o.Takim == "Yeni"]
    eski = [o for o in doc.Objects if o.Takim == "Eski"]
    kesit = [o for o in doc.Objects if o.Takim == "Kesit"]

    def goster(liste):
        for o in doc.Objects:
            gd.getObject(o.Name).Visibility = o in liste

    goster(yeni)
    kamera(v, (0, 0, 1), 1850, (0, 850, 0))
    kaydet(v, "taslak-on.png", 1100, 1400)
    kamera(v, (1, 0, 0), 1850, (0, 850, 0))
    kaydet(v, "taslak-yan.png", 1100, 1400)
    kamera(v, (0.8, 0.45, 1.0), 1900, (0, 860, 0))
    kaydet(v, "taslak-izometrik.png", 1100, 1400)
    kamera(v, (0.75, 0.35, 1.0), 520, (0, 1560, 20))
    kaydet(v, "taslak-kafa.png", 1200, 1000)
    kamera(v, (-0.9, 0.25, -0.6), 520, (0, 1560, -20))
    kaydet(v, "taslak-kafa-arka.png", 1200, 1000)
    kamera(v, (1.0, 0.15, 0.35), 620, (190, 1195, 0))
    kaydet(v, "taslak-kol.png", 1000, 1200)
    kamera(v, (0.9, 0.2, 0.5), 700, (0, 720, 0))
    kaydet(v, "taslak-govde-uzatma.png", 1200, 1000)
    goster(kesit)
    kamera(v, (0.55, 0.15, 1.0), 1250, (0, 860, 0))
    kaydet(v, "taslak-govde-kesit.png", 1100, 1400)
    goster(yeni + eski)
    kamera(v, (0, 0, 1), 1900, (-450, 850, 0))
    kaydet(v, "karsilastirma-125-170-on.png", 1600, 1250)
    kamera(v, (0.35, 0.2, 1.0), 1950, (-450, 860, 0))
    kaydet(v, "karsilastirma-125-170-izo.png", 1600, 1250)
    App.closeDocument(doc.Name)


def guvenli():
    try:
        montaj_dosyasi()
    except Exception:
        log(traceback.format_exc())
    try:
        gorseller()
    except Exception:
        log(traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
