# Lale 1,58 m - oneri belgesi Sekil 4 icin ham gorseller (FreeCAD GUI): tam robot on, yan, ust govde yakin (kafa ekrani + kamera + gogus ekrani).
# FC_SCRIPT=<bu dosya> freecad.exe run_fc.py   ana_montaj'dan sonra. Dosya kaydedilmez. Log %TEMP%\sekil4_gorsel.log. Cikti lale158/gorsel/sekil4-*.png.
import os, sys, tempfile, traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for p_ in (HERE, UST):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A

OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(tempfile.gettempdir(), "sekil4_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22), "siyah": (0.13, 0.13, 0.14),
        "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22), "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6), "pcb": (0.15, 0.45, 0.25)}


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


def kamera(v, eye, h, merkez):
    z = V(*eye).normalize()
    up = V(0, 1, 0)
    x = up.cross(z).normalize()
    y = z.cross(x)
    q = App.Rotation(x, y, z, "ZYX").Q
    cam = v.getCameraNode()
    cam.orientation.setValue(coin.SbRotation(q[0], q[1], q[2], q[3]))
    v.fitAll()
    pos = V(*merkez) + z * cam.focalDistance.getValue()
    cam.position.setValue(pos.x, pos.y, pos.z)
    cam.height.setValue(h)


def kaydet(v, ad, w, h):
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
            try:
                vo.ShapeColor = RENK.get(getattr(o, "Renk", "gri"), RENK["gri"])
            except Exception:
                pass
        elif "Joint" in o.TypeId or o.TypeId == "App::FeaturePython":
            try:
                vo.Visibility = False
            except Exception:
                pass
    for o in doc.Objects:
        if o.TypeId == "Assembly::JointGroup":
            gd.getObject(o.Name).Visibility = False
    v = Gui.activeDocument().activeView()
    v.setAnimationEnabled(False)
    v.setCameraType("Orthographic")
    Gui.updateGui()
    ORTA = A.BOY / 2.0
    # dikey karede kamera yuksekligi kisa kenara (genislik) uyar: 820 mm genislik = 1640 mm yukseklik, 2,44 piksel/mm
    kamera(v, (0, 0, 1), 820, (0, ORTA, 0)); kaydet(v, "sekil4-on.png", 2000, 4000)
    kamera(v, (1, 0, 0), 820, (0, ORTA, 0)); kaydet(v, "sekil4-yan.png", 2000, 4000)
    kamera(v, (0, 0.08, 1), 560, (0, 1290, 40)); kaydet(v, "sekil4-ust-govde-on.png", 1800, 2000)
    kamera(v, (0.55, 0.15, 1), 600, (0, 1290, 40)); kaydet(v, "sekil4-ust-govde-uc-ceyrek.png", 1800, 2000)
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
